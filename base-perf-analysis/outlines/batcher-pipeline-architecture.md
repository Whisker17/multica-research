---
topic: "Batcher 内部 Pipeline 架构与吞吐量瓶颈对比 (Base vs Mantle)"
project_slug: base-perf-analysis
topic_slug: batcher-pipeline-architecture
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: base-perf-analysis/outlines/batcher-pipeline-architecture.md
  draft: base-perf-analysis/research-sections/batcher-pipeline-architecture/drafts/round-{n}.md
  final: base-perf-analysis/research-sections/batcher-pipeline-architecture/final.md
  index: base-perf-analysis/research-sections/_index.md

scope: |
  深度对比 Base 自研 Rust batcher (base/base 仓库 crates/batcher) 与 Mantle 当前
  Go batcher (mantlenetworkio/mantle-v2 op-batcher，OP Stack 上游 fork) 的内部
  pipeline 架构，定位 Mantle batcher 的具体串行瓶颈环节并量化各环节对链 TPS 的
  限制。覆盖：pipeline 阶段拆解（block ingest → channel build → frame encode →
  compression → blob/calldata pack → L1 submit）、各阶段的并行度与背压模型、
  压缩策略（算法、配置、ratio vs shadow vs none、zlib vs brotli）、提交策略
  （MaxPendingTransactions、TargetNumFrames、blob 数量动态选择、DA throttling）、
  以及"参数调优 vs 架构重写"两条改进路径的预期收益。
  不进入：L1 DA 带宽理论上限分析（由 5b 课题覆盖）；batcher 与 sequencer 的背压
  耦合（由 5c 课题覆盖）；batcher 正确性 / reorg 处理 / 数据完整性细节验证。
audience: |
  Mantle 协议核心工程师、Performance / Sequencer / DA 团队、关心 batcher 路线图
  的产品决策者，以及需要在"短期参数调优"和"中期架构升级"之间做投资优先级判断的
  技术负责人。读者熟悉 OP Stack rollup 基本架构（channel / frame / blob），但
  不一定熟悉 Base Rust batcher 的具体代码组织或最新 OP Stack 多 blob/多 channel
  upstream 进展。
expected_output: |
  - Base 与 Mantle batcher pipeline 阶段对比图（含每阶段输入/输出、是否并行、
    背压点、关键代码引用）
  - 各 pipeline 阶段的预估耗时与 CPU/IO/network 资源画像
  - 压缩策略对比表（algorithm、kind、target_output_size、approx_compr_ratio、
    实测/估算压缩比、压缩延迟、流式 vs 批量）
  - 串行瓶颈点清单（top 3+，每项标注预估 TPS 上限、定位证据、修复成本）
  - 并行化改进方案：分"参数调优 quick wins"（MaxPendingTransactions、
    TargetNumFrames、compressor kind/algo、MaxChannelDuration）与"架构演进"
    （多 channel 并行、submission queue 重写、DA-type 动态切换）两层
  - 至少 3 个 Mermaid 图表：Base pipeline、Mantle pipeline、瓶颈瀑布/Gantt

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-20T06:45:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-20T07:10:00Z"
  rounds:
    - round: 1
      commit: "https://github.com/Whisker17/multica-research/commit/68c37e08802e3a11e98c790775647cc58f905a30"
      verdict: revise
      adversarial_comment_id: "84e4f9a1-b779-47fa-81e5-87754c9a970b"
    - round: 2
      adversarial_comment_id: null
      patches_applied:
        - "Mandatory Patch 1: Unit normalization subsection added to item-5 with Base/Mantle rows backed by code evidence"
        - "Mandatory Patch 2: runtime_configuration_evidence field added; top-3 bottleneck claims now require a live/config anchor or 'default-code-path risk' label"
        - "item-6 TPS formulas constrained to consume normalized units from item-5 table only"
        - "Non-blocking: upstream PR / Mantle commit cross-reference note added to item-5 / item-7"
        - "Non-blocking: Pectra/EIP-7691 analysis gated on actual L1 fork constants in checked-out code"
---

# Research Outline: Batcher 内部 Pipeline 架构与吞吐量瓶颈对比 (Base vs Mantle)

## Items

### item-1: Pipeline 阶段拆解与数据流对比

逐阶段拆解两链 batcher 的完整数据流：L2 block ingest → channel build → frame
encode → compression → blob/calldata pack → L1 tx submit → receipt confirm。
Base 侧从 `base/base` 仓库 `crates/batcher/{source,encoder,comp,blobs,core,service}`
读取（重点：`encoder/src/pipeline.rs` 的 `BatchPipeline` trait、`core/src/driver.rs`
的 `BatchDriver` tokio::select 主循环、`core/src/submissions.rs` 的
`SubmissionQueue` + `Semaphore` 并发提交）。Mantle 侧从 `mantle-v2/op-batcher/batcher/`
读取（重点：`driver.go` 的 publishing/throttling/receipts loops、`channel_manager.go`
的"single pending channel"设计、`channel_builder.go`、`tx_data.go`）。需要明确：
每个阶段的输入/输出契约、阻塞 vs 异步、错误处理 / requeue 路径、reorg 处理点。

- **Priority**: high
- **Dependencies**: none

### item-2: Channel / Frame 构建并行度对比

聚焦 Base 与 Mantle 在 channel 与 frame 层的并行度差异。Mantle `channelManager`
文档明确写"only creates a single pending channel at a time & waits for the channel
to either successfully be submitted or timeout before creating a new channel"
（`op-batcher/batcher/channel_manager.go`），即 channel 构建严格串行。Base 侧
`BatchPipeline` 是同步状态机但 `BatchDriver` 通过 tokio::select 把 encoding step
与 submission/receipt/admin/L1-head 多路解耦，且 `STEP_BUDGET=128` 一次性消化多
block，再让步给 receipt 处理。需对照评估：单 channel 串行对 burst 流量的延迟放大、
多 channel pre-build 的可行性、frame cursor 与 requeue 路径对再提交吞吐的影响、
span batch 与 singular batch 在并发上的差异（`MaxBlocksPerSpanBatch`）。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 提交并发与背压：MaxPendingTransactions / Semaphore

Mantle/op-batcher 默认 `MaxPendingTransactions=1`（`flags.go`），上游 OP Stack
issue [#14109](https://github.com/ethereum-optimism/optimism/issues/14109) 明确
指出"pending transactions is never higher than 1"为已知瓶颈，OP 官方文档对高吞
量链推荐 `MAX_PENDING_TX=10`。Base 侧通过 `SubmissionQueue::new(tx_manager, inbox,
max_pending)` 的 `Semaphore::new(max_pending)` 控制并发，`FuturesUnordered`
跟踪 in-flight receipts，并通过 `txpool_blocked` 状态管理 mempool 拥塞。需要量化：
单一 in-flight tx 对 throughput 的乘性影响（throughput ≤ blob_size / RTT_L1）、
nonce 分配与 receipt 串行确认对 reorg 风险的影响、Base 的 DA-throttle
（`DaThrottle`、`force_blobs_when_throttling`）与 Mantle 的 throttling loop 在
高负载下的行为差异。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 压缩策略对比：算法 / kind / target_output_size

详细对比两链的压缩管线：Mantle `op-batcher/compressor/{compressors,
ratio_compressor,shadow_compressor,non_compressor}.go` 支持 `RatioKind`、
`ShadowKind`、`NoneKind`，默认 `ShadowKind`，算法默认 `Zlib`（可选 brotli via
`derive.CompressionAlgo`），`approx-compr-ratio` 默认 0.6。Base 侧
`crates/batcher/comp/src/{brotli,zlib,shadow,ratio,composer,variant}.rs` 提供 brotli
和 zlib 两种算法、shadow + ratio 两种"满载估计"策略以及 `composer.rs` 的组合器。
需要量化：相同 L2 交易混合下 brotli vs zlib 的压缩比与 CPU 延迟、shadow（精确）
vs ratio（近似）的 over/under-fill 误差、`TargetOutputSize` = `MaxDataSize(
TargetNumFrames, MaxFrameSize)` 关系、压缩是否真的是 pipeline 瓶颈（vs L1
inclusion）。

- **Priority**: high
- **Dependencies**: item-1

### item-5: Blob 提交策略与 DA-Type 动态切换

对比两链的 blob 提交策略：Mantle 默认 `target-num-frames=1`（即 1 blob/tx），
`MaxL1TxSize=120000` calldata（blob 时以 BlobMaxData 覆盖），可选 `UseBlobs` /
calldata；OP Stack 上游 v1.7.2 [PR #9779](https://github.com/ethereum-optimism/optimism/pull/9779)
引入多 blob 支持（推荐 6 blob/tx）与 [#11219](https://github.com/ethereum-optimism/optimism/issues/11609)
动态 DA-type 切换。Base 侧 `submissions.rs::submit_pending` 一次性把 ready frames
打包成 ≤ `BlobEncoder::BLOB_MAX_DATA_SIZE` 的 blob payload，提交一笔 L1 tx；
`force_blobs_when_throttling` 在 DA backlog 上升时强制走 blob。需要确认：Mantle
当前 fork 是否落后于 v1.7.2 多 blob 能力、是否实施动态 DA-type、
EIP-7691 (Pectra Blob Throughput 增加：3/6 → 6/9 target/max) 对两链 batcher
的影响、blob fee market 抖动下的 fee bumping 路径。

> **Cross-version verification (non-blocking)**: 任何"Mantle 落后于 OP 上游 vX.Y.Z /
> PR #N"的论断（包括 v1.7.2 / #9779 / #11219）都必须在 draft 中给出 (i) 对应 OP
> 上游 commit hash 与文件:行号、(ii) Mantle fork 中对应文件的当前 commit hash 与
> 文件:行号（或确认该路径在 Mantle fork 中不存在 / 未 cherry-pick）。"上游已合并
> PR" 不等同于 "Mantle 已具备该能力"，必须代码层确认。
>
> **Pectra fork-constants verification (non-blocking)**: 对于 EIP-7691 / Pectra
> blob 增容（target 3→6、max 6→9）的论断，draft 必须在 checked-out 代码中查找
> 实际的 L1 fork 常量（如 `MAX_BLOB_GAS_PER_BLOCK`、`TARGET_BLOB_GAS_PER_BLOCK`、
> `BLOB_GAS_PER_BLOB`、Prague/Pectra activation timestamp 等）并引用 file:line；
> 仅引用 EIP 提案标题或路线图博客不足以作为"两链 batcher 已受益于 Pectra"的证据。

#### Unit normalization: channel / frame / submission / blob / L1 tx

> **规范要求 (mandatory)**：draft 必须以本表的语义作为 item-2/3/5/6 所有"frame
> 数"、"blob 数"、"per-tx"度量的统一基线。**不得在未先消解单位差异的情况下，
> 把 Base 的"一个 blob 内打包多帧"与 Mantle 的"一帧一 blob"或"MantleBlobs RLP
> 跨 blob 切片"当作 1:1 blob-count 语义直接比较。** 凡涉及 TPS 公式（item-6），
> 必须把所有项归一为 `bytes_per_L1_tx` 或 `bytes_per_blob` 后再做比较，不允许
> 直接用 `frames_per_tx` 跨链相加。

| Field | Base (`crates/batcher` Rust) | Mantle (`op-batcher` Go, 双路径) |
|-------|------------------------------|--------------------------------|
| **What one frame maps to** | 帧是 blob payload 内的**子单元**：blob 内顺序拼接多帧 `[DERIVATION_VERSION_0] ++ frame_0.encode() ++ frame_1.encode() ++ ...`；每帧 ~23 字节开销 + frame data。证据：`base/crates/batcher/blobs/src/encoder.rs:43-62` (`FRAME_OVERHEAD = 23`, `encode_packed`)；`base/crates/batcher/core/src/submissions.rs:69-92`（`while …` 累积 frames 至 `BLOB_MAX_DATA_SIZE`）。 | **Calldata 路径**：1 帧 = 1 L1 tx（`tx_data.go:14-18` "exactly one frame per transaction"；`channel_config.go:95-100` `MaxFramesPerTx()` 在 `!UseBlobs` 时返回 1）。**Blob 路径 (Arsia 之后)**：1 帧 = 1 blob，`Blobs()` 对 `td.frames` 循环 `blob.FromData(frame)`（`tx_data.go:48-58`；`channel_config.go:49-51` "multi-blob transaction with one blob per frame"）。**Blob 路径 (Arsia 之前, `MantleBlobs`)**：所有 frames 先 RLP 编码为单一字节流（每帧前缀 version byte），再按 `MaxBlobDataSize` 字节切片到多个 blob——单帧可能**跨 blob**（`tx_data.go:60-107`；`driver.go:1013-1023` Arsia gate）。 |
| **Max frames per submission/tx** | 取决于压缩后 frame 大小与 `BLOB_MAX_DATA_SIZE` 的比例；理论上一个 blob payload 可承载多帧直至 ~130043 字节（含每帧 23 字节开销）。提交侧通过 `Semaphore` permit 决定并发 L1 tx 数，每 permit = 1 L1 tx（`base/crates/batcher/core/src/submissions.rs:45-51` doc）。 | **Calldata**：硬编码 1（`channel_config.go:95-100`）。**Blob (post-Arsia)**：`MaxFramesPerTx() = TargetNumFrames`（默认 1，可配置；上游推荐 6 = EIP-4844 `MAX_BLOB_COMMITMENTS_PER_BLOCK` 中单 tx 的常用上限）。**Blob (pre-Arsia, MantleBlobs)**：单 tx 内 blob 数 = `ceil(rlp(frames).len / MaxBlobDataSize)`，frame 数无独立上限，由 `TargetNumFrames` 和压缩输出共同决定（`tx_data.go:88-104`）。 |
| **Can one L1 tx carry multiple blobs?** | **否**：`submissions.rs:110-117` 中 `TxCandidate { …, blobs: Arc::from(vec![blob]) }` 始终为单元素 `vec`；当前提交路径**不存在**多 blob/tx 的代码分支。注意 `encoder/src/config.rs:45-51` 配置文档说"N blobs per transaction"，但 submission 实际不遵守此意图——文档与实现不一致需在 draft 中显式标注。 | **是**：`tx_data.go:48` `Blobs() ([]*eth.Blob, error)` 返回 slice；`driver.go:1010-1033` `blobTxCandidate` 构造 `txmgr.TxCandidate{Blobs: blobs}` 并 log `"num_blobs", len(blobs)`。MantleBlobs 路径同样在单 tx 内携带多 blob（按字节切片）。 |
| **How `TargetNumFrames` is interpreted** | 用作**压缩器目标输出大小**与 channel 关闭阈值，而非直接的 per-tx blob 数：`encoder/src/encoder.rs:332` `target_output_size = config.target_frame_size`；`encoder.rs:533-534` channel-close = `target_frame_size * target_num_frames`。默认 `target_num_frames=1`（`encoder/src/config.rs:105`）。**注意**：尽管文档暗示"N blobs per tx"，实际 submission 不读此值——它只控制 channel 何时关闭。 | 双路径解释不同。**Calldata**：未直接使用，单 tx 单 frame（`MaxFramesPerTx()=1`）。**Blob (post-Arsia)**：直接 = per-tx blob 数（`channel_config.go:36-39` "controls the number of blobs to target adding to each blob tx"；`channel.go:114-141` `NextTxData` / `HasTxData` 在 `PendingFrames() >= MaxFramesPerTx()` 时返回）。**MantleBlobs (pre-Arsia)**：作为压缩器 `TargetOutputSize = MaxDataSize(TargetNumFrames, MaxFrameSize)` 的输入（`channel_config.go:65-72`），间接影响一个 channel 被切成多少 frame，从而影响 RLP 后跨 blob 切片数。 |
| **Byte-size limit binding each path** | `BLOB_MAX_DATA_SIZE = (4*31+3)*1024 - 4 = 130044` 字节（`base/crates/consensus/protocol/src/frame.rs:45`）；`MAX_BLOB_FRAME_SIZE = 130043`（=`BLOB_MAX_DATA_SIZE` - prefix；同文件:52）。默认 `target_frame_size = max_frame_size = MAX_BLOB_FRAME_SIZE` (`encoder/src/config.rs:101-102`)。 | **Calldata**：`MaxL1TxSize` 默认 `120000` 字节（`config.go:100-102`、`flags/flags.go:75-80`）；`service.go:266` `MaxFrameSize = MaxL1TxSize - 1`。**Blob 两条路径共享**：`eth.MaxBlobDataSize = (4*31+3)*1024 - 4 = 130044` 字节（`op-service/eth/blob.go:18-24`）；`service.go:277` blob 路径覆盖 `cc.MaxFrameSize = MaxBlobDataSize - 1`；`blob.go:92-95` `FromData` 拒绝超过 `MaxBlobDataSize` 的输入。 |

**关键不对称提示（draft 必须显式呈现）**：

1. Base 的"1 frame = blob 内子单元，1 tx = 1 blob"与 Mantle Arsia 后的"1 frame = 1 blob，1 tx ≤ TargetNumFrames blobs"在**底层数据布局上恰好相反**：Base 把多 frame 塞进单 blob 单 tx；Mantle 把多 frame 拆成多 blob 单 tx。因此"Mantle TargetNumFrames=1"与"Base 单 blob/tx"在表面同为单 blob，但 Base 单 blob 可承载多帧、Mantle 单 blob 仅承载 1 帧（post-Arsia）或部分 RLP 切片（pre-Arsia）。
2. Mantle 的 pre/post-Arsia 切换会让 `TargetNumFrames=N` 的语义从"channel 切多少帧→RLP 后切多少 blob"变为"channel 切多少帧→直接多少 blob"。draft 比较 Mantle 与 Base 时必须先确认当前 mainnet/testnet 处于哪个 fork 阶段，并在 `runtime_configuration_evidence` 中记录。
3. Base 的 `encoder/src/config.rs` 配置文档与 `submissions.rs` 实际行为不一致（文档说"N blobs per tx"，代码只产 `vec![blob]` 单 blob）——draft 应将其作为"未利用的多 blob 容量"列为潜在改进项，而非作为 Base 的现有能力。

- **Priority**: high
- **Dependencies**: item-1, item-3

### item-6: 串行瓶颈定位与各阶段耗时估算

将 item-1 至 item-5 的观察整合成"按阶段排序的瓶颈清单"：对每个 pipeline 阶段
给出 (i) Mantle 当前实测/估算耗时上界（基于源代码与公开 metrics、文档默认值），
(ii) CPU-bound / IO-bound / network-bound 分类，(iii) 该阶段达到饱和时的链级
TPS 上限。重点核对内部调研结论（"batcher 是 Mantle TPS 最大限制"）是否真的指向
batcher 内部某具体环节，还是指向"batcher commit 节奏 vs sequencer block 节奏"
的耦合（后者归属 5c）。明确 top-3 瓶颈：候选是 (a) `MaxPendingTransactions=1`
导致的 L1 inclusion 串行、(b) `TargetNumFrames=1` 导致的 blob 利用率低、
(c) 单 channel 串行限制 burst 平滑能力，但要用代码证据收敛。

> **TPS 公式规范化要求 (mandatory)**：item-6 中所有 TPS 上限估算必须显式引用
> item-5 "Unit normalization" 表中已统一的单位定义，禁止跨链直接相加 `frames`
> 或 `blobs`。推荐归一形式：
>
> ```
> TPS_max ≈ (bytes_per_L1_tx × MaxPendingTransactions) / (RTT_L1 × bytes_per_tx_of_avg)
> 其中：
>   bytes_per_L1_tx (Base, 当前) = min(BLOB_MAX_DATA_SIZE, sum_of_packed_frames)   # 单 blob
>   bytes_per_L1_tx (Mantle calldata) = min(MaxL1TxSize - 1, 1 frame)             # 单 frame
>   bytes_per_L1_tx (Mantle blob post-Arsia) = TargetNumFrames × MaxBlobDataSize  # N blob × ~130KB
>   bytes_per_L1_tx (Mantle blob pre-Arsia / MantleBlobs) = ceil(rlp(channel_frames).len) ≤ N × MaxBlobDataSize
> ```
>
> 任何不能用上述统一形式表达的 TPS 上限论断必须在 draft 中以"⚠ 非规范化估算"
> 标注并独立说明假设。

> **`runtime_configuration_evidence` 字段使用要求 (mandatory)**：item-6 中
> 每一个被列入 top-3 的 Mantle 瓶颈，必须填写 `runtime_configuration_evidence`
> 四类（见下方 Fields 定义）。若四类中缺少 **2.deployed_config** 与
> **3.observed_on_chain** 中的**任一项**作为 live 锚点，该条目必须改用
> **"default-code-path risk (未观测)"** 措辞，不得使用"current Mantle bottleneck"。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

### item-7: 并行化改进方案：参数 Quick Wins vs 架构演进

把改进方案分成两层。Quick Wins（仅 op-batcher 配置变更，无代码修改）：
`MaxPendingTransactions` 提升至 5–10、`TargetNumFrames` 提升至 6（启用多 blob）、
压缩算法切到 brotli、`MaxChannelDuration` 调优、启用 DA-type 动态切换（若 Mantle
fork 已 cherry-pick #11219）。架构演进（需要代码修改或借鉴 Base 设计）：
多 channel pre-build 并行（取消"single pending channel"）、submission queue +
semaphore 重写、流式压缩 + 增量 frame flush、DA-throttle 控制器重构。
每条建议给出：当前值/状态、推荐值/做法、变更途径、预期 TPS 增益（含敏感度区间）、
工程复杂度估算（人天 / PR 数量级）、回滚策略、与其他课题（5b / 5c / item-8 风险）
的耦合点。

- **Priority**: high
- **Dependencies**: item-6

### item-8: 风险与权衡：fee 经济、reorg、DA 占用

对 item-7 中每条建议展开权衡分析：(a) 提升 MaxPendingTransactions 引入更高的
nonce-gap 风险与 reorg 期间的 requeue 雪崩；(b) 多 blob/tx 在 blob 拥堵时会被
fee bumping 双倍化（OP 官方文档警告）、需要更高 min tip cap / base fee buffer；
(c) brotli 压缩比更高但 CPU 占用上升，对 sequencer 同机部署有副作用；(d) 缩短
MaxChannelDuration 增加 L1 提交频度 → DA 成本上升、blob fee market 影响放大；
(e) 多 channel 并行引入更复杂的 reorg 处理（多 channel 同时回滚的状态机）。
为每项给出可观察指标（metrics / alerting target）与降级路径（fall-back 到
旧配置/单 channel 的开关）。明确"快速可逆"与"需要灰度"的分类。

- **Priority**: medium
- **Dependencies**: item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| code_evidence | 主要代码引用（仓库路径:行号、commit 锚点），覆盖 Base Rust 与 Mantle Go 两侧 | all |
| concurrency_model | 该阶段在 Base / Mantle 的并发模型（同步状态机 / 单 goroutine loop / tokio::select / semaphore / FuturesUnordered） | item-1, item-2, item-3, item-5 |
| default_value | 默认配置值（含 flag name、单位、版本/fork 锚点） | item-3, item-4, item-5, item-7 |
| recommended_value | 针对 Mantle 的推荐值或推荐做法（含 OP 官方建议与 Base 实测参照） | item-3, item-4, item-5, item-7 |
| tps_impact | 对链级 TPS 的边际影响（公式 / 数量级估算 / 敏感度区间），必须按 item-6 "TPS 公式规范化要求" 使用 item-5 unit normalization 表的归一单位 | item-2, item-3, item-4, item-5, item-6, item-7 |
| resource_profile | CPU-bound / IO-bound / network-bound 分类与瓶颈机制 | item-1, item-2, item-3, item-4, item-6 |
| safety_implication | reorg / nonce gap / DA cost / fee bumping / state growth 等安全或经济风险 | item-3, item-5, item-7, item-8 |
| implementation_cost | 落地工作量估算：仅配置变更 / cherry-pick PR / 需要重写组件，含人天数量级 | item-7, item-8 |
| confidence | 高 / 中 / 低：基于源代码直接读取 / 上游 PR + issue 锚点 / 类比推算 | all |
| runtime_configuration_evidence | **(mandatory for bottleneck claims)** 区分四类证据并分别填写：(1) **cli_default** — flag 在源码中的默认值与文件:行号；(2) **deployed_config** — Mantle 实际部署的 env / helm / systemd / docker-compose / startup-log 引用（若可获取）；(3) **observed_on_chain** — Mantle mainnet/testnet batcher tx 样本（DA type、blobs per tx、tx cadence、inclusion lag），含 tx hash 或 explorer 链接；(4) **inferred_recommendation** — 分析师结论与置信度。任何 item-6 "top-3 bottleneck" 论断必须至少有一条 (2) 或 (3) 类 live 锚点；否则该论断必须标注为 **"default-code-path risk (未观测)"** 而非 "current Mantle bottleneck"。 | item-3, item-4, item-5, item-6, item-7 |
| upstream_mantle_commit_diff | **(mandatory for upstream-comparison claims, non-blocking)** 任何"Mantle 落后于 OP 上游 vX.Y.Z / PR #N"（含 v1.7.2 / #9779 / #11219 / #14109 / Pectra）的论断都必须填写：(a) 上游 commit hash + 文件:行号，(b) Mantle fork 对应文件的 commit hash + 文件:行号，或显式声明"该 commit 在 Mantle fork 中缺失（未 cherry-pick）"。仅引用 PR 编号不足。 | item-3, item-4, item-5, item-7 |
| fork_constants_verified | **(mandatory for Pectra/EIP-7691 / hardfork claims, non-blocking)** 凡涉及 L1 hardfork 容量（如 EIP-7691 Pectra blob target 3→6 / max 6→9、`MAX_BLOB_GAS_PER_BLOCK`、`TARGET_BLOB_GAS_PER_BLOCK`、`BLOB_GAS_PER_BLOB`、Prague activation timestamp）的论断必须在 checked-out 代码（base / mantle-v2 / 上游依赖）中查得**具体常量值 + 文件:行号**；不允许仅引用 EIP 标题或路线图博客。 | item-5, item-7 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | Base batcher pipeline 架构图（阶段、并行度、tokio::select 主循环、SubmissionQueue/Semaphore、DaThrottle、关键类型与 crate 边界） | mermaid | item-1, item-2, item-3, item-5 |
| diag-2 | architecture | Mantle op-batcher pipeline 架构图（publishing/throttling/receipts loops、single pending channel、MaxPendingTransactions=1 串行点、compressor 分支） | mermaid | item-1, item-2, item-3, item-5 |
| diag-3 | timeline | Pipeline 各阶段耗时 / 占用瀑布图（block ingest / channel build / compress / pack / submit / wait L1 inclusion），标注每阶段在 Mantle 默认配置下的串行段长度与 Base 对应阶段的并行段 | mermaid (gantt) | item-1, item-6 |
| diag-4 | comparison | 压缩策略对比矩阵（algorithm × kind × target_output_size × approx_compr_ratio × CPU/ratio tradeoff），并标注 Base 与 Mantle 各自的默认/可选组合 | mermaid | item-4 |
| diag-5 | hierarchy | 并行化改进方案优先级象限（TPS 收益高/低 × 工程复杂度低/高 × 风险高/低），区分 quick wins 与架构演进 | mermaid | item-7, item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | `base/base` 仓库 `crates/batcher/{core,encoder,comp,blobs,service,source,admin}` 关键文件：`driver.rs`、`pipeline.rs`、`submissions.rs`、`channel_out.rs`、`composer.rs`、`shadow.rs`、`brotli.rs`、`zlib.rs`、blob `encoder.rs` | 6 |
| src-2 | code_analysis | `mantlenetworkio/mantle-v2` 仓库 `op-batcher/batcher/{driver,channel_manager,channel_builder,channel_config,tx_data,service}.go` 与 `op-batcher/compressor/{ratio,shadow,non}_compressor.go`、`op-batcher/flags/flags.go` | 6 |
| src-3 | code_analysis | OP Stack 上游 `ethereum-optimism/optimism` `op-batcher/` 对照实现（确认 Mantle fork 与 upstream 的 commit 差） | 2 |
| src-4 | official_docs | Optimism batcher 配置文档（max-pending-tx、target-num-frames、compressor、blob 推荐配置）与 OP Stack channel/frame 规范 | 2 |
| src-5 | governance_proposals | OP Stack 关键 PR/Issue 锚点：multi-blob 支持 PR #9779 (v1.7.2)、动态 DA-type #11219、`MaxPendingTransactions=1` issue #14109、Pectra blob 增容 EIP-7691 | 3 |
| src-6 | on_chain_data | Base mainnet / Mantle mainnet 各自 batcher EOA 提交 tx 样本（DA type、blob 数 / calldata size、tx cadence、L1 inclusion lag、fee 分布），样本量 ≥ 50 笔（连续区间或随机抽样均可），作为 item-6 `runtime_configuration_evidence.observed_on_chain` 锚点。Mantle 样本缺失时必须显式声明并触发 "default-code-path risk" 标注。 | 2 |
| src-7 | deployed_config | Mantle 当前 batcher 部署的实际配置（env vars / helm chart / systemd unit / docker-compose / startup logs 中任意一种均可），用于核对 `data-availability-type`、`target-num-frames`、`max-pending-tx`、`max-l1-tx-size`、`max-channel-duration` 的运行时值是否与 CLI 默认值一致；若部署配置无法获取，draft 必须以 "default-code-path risk" 措辞限定所有相关 bottleneck 结论。 | 1 (best-effort) |
| src-8 | upstream_diff | OP Stack 上游与 Mantle fork 的 commit 对照证据：针对 v1.7.2 / PR #9779（multi-blob）/ #11219（动态 DA-type）/ #14109（MaxPendingTransactions=1）等每条"Mantle 落后"论断，提供上游 commit hash + 文件:行号与 Mantle fork 对应文件 commit hash + 文件:行号（或"未 cherry-pick"声明）。 | 3 |
| src-9 | fork_constants | Pectra/EIP-7691 与其他 L1 hardfork 容量论断的常量锚点：在 checked-out 代码（base / mantle-v2 / 其依赖的 op-geth / go-ethereum）中查得 `MAX_BLOB_GAS_PER_BLOCK`、`TARGET_BLOB_GAS_PER_BLOCK`、`BLOB_GAS_PER_BLOB`、Prague / Pectra activation timestamp 等常量的实际值与 file:line；不允许仅引用 EIP 文本。 | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | add subsection | item-5 → "Unit normalization: channel / frame / submission / blob / L1 tx" | 解决 Round-1 adversarial finding 1：Base "frames packed into one blob payload" 与 Mantle "frames as blobs per tx" / MantleBlobs RLP-跨-blob 切片在单位语义上不可直接比较。新增表格用代码证据为两链分别定义 frame / blob / tx 映射、最大值、字节限制，并明确"关键不对称"以约束 draft 比较口径。 | adversarial comment `84e4f9a1-b779-47fa-81e5-87754c9a970b` (finding 1) |
| 2 | add field | Fields → `runtime_configuration_evidence` (mandatory) | 解决 Round-1 adversarial finding 2：CLI default ≠ live behavior。新字段强制 draft 区分 cli_default / deployed_config / observed_on_chain / inferred_recommendation 四类，并对 top-3 bottleneck 要求至少一条 live 锚点，否则降级为 "default-code-path risk"。 | adversarial comment `84e4f9a1-b779-47fa-81e5-87754c9a970b` (finding 2) |
| 2 | tighten | item-6 → TPS formula normalization | 强制所有 TPS 公式消费 item-5 unit normalization 表的归一单位（bytes_per_L1_tx），防止跨链直接相加 frames/blobs 的 apples-to-oranges 比较。 | adversarial comment `84e4f9a1-b779-47fa-81e5-87754c9a970b` (finding 1 follow-on) |
| 2 | add field | Fields → `upstream_mantle_commit_diff` (non-blocking) | 任何"Mantle 落后于上游 PR/version"论断需提供双侧 commit hash + file:line，仅引用 PR 编号不足。 | adversarial comment `84e4f9a1-b779-47fa-81e5-87754c9a970b` (non-blocking 1) |
| 2 | add field | Fields → `fork_constants_verified` (non-blocking) | Pectra/EIP-7691 等 L1 hardfork 容量论断必须在 checked-out 代码中查得实际常量值，不允许仅引用 EIP 标题。 | adversarial comment `84e4f9a1-b779-47fa-81e5-87754c9a970b` (non-blocking 2) |
| 2 | add sources | Source Requirements → src-7 (deployed_config), src-8 (upstream_diff), src-9 (fork_constants) | 为新增的三个 mandatory/non-blocking 字段提供独立的源类别与最小取证数量，避免 draft 把代码默认值直接当作 live 证据。 | adversarial comment `84e4f9a1-b779-47fa-81e5-87754c9a970b` (both findings + non-blocking) |
| 2 | extend | item-5 → cross-version verification & Pectra fork-constants notes | 在 item-5 正文中显式写入两条 non-blocking 验证规则，配合新 Fields 落地。 | adversarial comment `84e4f9a1-b779-47fa-81e5-87754c9a970b` (non-blocking 1 & 2) |
