---
topic: "Batcher 内部 Pipeline 架构与吞吐量瓶颈对比 (Base vs Mantle)"
project_slug: base-perf-analysis
topic_slug: batcher-pipeline-architecture
github_repo: Whisker17/multica-research
round: 1
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
  last_modified_at: "2026-05-20T06:45:00Z"
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

- **Priority**: high
- **Dependencies**: item-1, item-3

### item-6: 串行瓶颈定位与各阶段耗时估算

将 item-1 至 item-5 的观察整合成"按阶段排序的瓶颈清单"：对每个 pipeline 阶段
给出 (i) Mantle 当前实测/估算耗时上界（基于源代码与公开 metrics、文档默认值），
(ii) CPU-bound / IO-bound / network-bound 分类，(iii) 该阶段达到饱和时的链级
TPS 上限。重点核对内部调研结论（"batcher 是 Mantle TPS 最大限制"）是否真的指向
batcher 内部某具体环节，还是指向"batcher commit 节奏 vs sequencer block 节奏"
的耦合（后者归属 5c）。明确 top-3 瓶颈：预期是 (a) `MaxPendingTransactions=1`
导致的 L1 inclusion 串行、(b) `TargetNumFrames=1` 导致的 blob 利用率低、
(c) 单 channel 串行限制 burst 平滑能力，但要用代码证据收敛。

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
| tps_impact | 对链级 TPS 的边际影响（公式 / 数量级估算 / 敏感度区间） | item-2, item-3, item-4, item-5, item-6, item-7 |
| resource_profile | CPU-bound / IO-bound / network-bound 分类与瓶颈机制 | item-1, item-2, item-3, item-4, item-6 |
| safety_implication | reorg / nonce gap / DA cost / fee bumping / state growth 等安全或经济风险 | item-3, item-5, item-7, item-8 |
| implementation_cost | 落地工作量估算：仅配置变更 / cherry-pick PR / 需要重写组件，含人天数量级 | item-7, item-8 |
| confidence | 高 / 中 / 低：基于源代码直接读取 / 上游 PR + issue 锚点 / 类比推算 | all |

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
| src-6 | on_chain_data | Base mainnet / Mantle mainnet batcher 提交 tx 样本（blob 数 / calldata size / inclusion lag / fee 分布）作为 default 配置的实际行为锚点 | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
