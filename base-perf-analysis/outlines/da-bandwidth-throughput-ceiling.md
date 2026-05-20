---
topic: "DA 带宽利用率与理论吞吐量上限分析 (Base vs Mantle)"
project_slug: base-perf-analysis
topic_slug: da-bandwidth-throughput-ceiling
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: base-perf-analysis/outlines/da-bandwidth-throughput-ceiling.md
  draft: base-perf-analysis/research-sections/da-bandwidth-throughput-ceiling/drafts/round-{n}.md
  final: base-perf-analysis/research-sections/da-bandwidth-throughput-ceiling/final.md
  index: base-perf-analysis/research-sections/_index.md

scope: |
  量化 L1 数据可用性 (DA) 层在 EIP-4844 + Pectra (以及任何在观测窗口内激活的 BPO
  EIP-7892) 升级后的理论带宽上限，对比 Base 与 Mantle (mantle-v2) 主网在 blob 提交
  频率、blob 填充率、压缩比以及 calldata/blob 混合策略上的实际差异，建立"DA 带宽 →
  有效 TPS 上限"映射模型，并判定 DA 层是否是 Mantle 当前 TPS 与 Base 之间差距的
  binding constraint。映射模型严格区分 (a) 协议层 blob 容量 (128 KiB protocol-defined
  raw size)、(b) batcher/derivation 可写入的 usable payload bytes per blob、(c) 在
  blob base-fee 飙升与 inclusion-delay 约束下的"经济可用 DA 容量"。包括 EIP-7691 在
  Pectra 主网激活后 blob target/max 的变化，以及 EIP-7840 / EIP-7892 BPO 机制在观测
  日期是否已通过 BPO 调度过 target/max；同时记录 Fusaka/PeerDAS 路线图对 Mantle DA
  上限的前瞻性影响（仅作展望，不展开细节）。不进入：batcher 内部 channel 构造细节
  （由课题 5a 覆盖）、alt-DA 方案（Celestia / EigenDA）的整体评估、blob fee market
  的经济学闭式推导（仅引用其对"经济可用容量"的影响）。
audience: |
  Mantle 协议核心工程师、Sequencer 与 Batcher 团队、关注 L2 路线图的产品负责人，以及
  需要判断"是否值得增加 batcher 投入以提升 DA 利用率"的运营/治理决策者。读者熟悉
  EIP-4844 与 OP Stack 的 batcher/derivation 基本概念，但不一定掌握 Pectra blob 参数
  变化（EIP-7691, EIP-7840, EIP-7892 BPO）的最新数值，也不一定亲手做过 blob 填充率统计。
expected_output: |
  - L1 DA 带宽理论上限计算（含公式推导：active_target_blobs × usable_payload_bytes_per_blob
    / slot_time；并显式标注 protocol-defined raw blob size = 128 KiB 与
    usable_payload_bytes_per_blob 的差额来源：field element 31/32 byte 编码、frame
    header、channel padding、压缩后 trailing zero-pad）
  - Pectra 前 / Pectra 后 / 当前观测日激活的 BPO 调度 / Fusaka 展望四阶段的 DA 上限
    对比表（每阶段都标注 activation_fork 与 source EIP / BPO meta EIP）
  - Base vs Mantle blob 利用率对比表（每 L1 epoch 平均 blob 数、平均 decoded payload
    fill-rate、calldata 回退占比、压缩比、有效 DA 字节/L2 tx）；测量方法显式区分
    archival-indexer 数据 vs raw RPC 数据，并标注观测窗口是否落在 EIP-4844 sidecar
    retention 内
  - 不同交易类型 mix (transfer / swap / mint / deploy) 下的 DA 约束 TPS 计算表
  - Blob 填充率分析与 Mantle 可获得的 TPS 提升空间估算（含敏感度区间）
  - DA 是否为 binding constraint 的判定结论，**分别给出 physical capacity 下与
    economically-usable capacity 下的两套判定**，并对比与执行层（gas/blocktime/state）
    约束的优先级
  - 至少 2 个 Mermaid 图表（DA 带宽利用率对比 + TPS 上限映射）

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-20T06:35:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-20T06:55:00Z"
---

# Research Outline: DA 带宽利用率与理论吞吐量上限分析 (Base vs Mantle)

## Items

### item-1: L1 DA 带宽理论上限（EIP-4844、Pectra、BPO 调度）

确立 L1 DA 带宽的理论上限基线，并把"协议层 blob 大小"与"rollup 实际可用 payload"
这两个量分开。需要：

1. 拉取 EIP-4844 原始规范：blob 大小 = 4096 field elements × 32 bytes = 131,072
   bytes = 128 KiB（protocol-defined raw blob size），blob target / max blobs per
   block，blob base fee 自适应公式。
2. 核对 Pectra (Prague) 升级中 EIP-7691 对 blob target / max 的提升数值（社区共识为
   target 3→6、max 6→9），同时确认 EIP-7840 / EIP-7892 (Blob Parameter Only / BPO)
   meta EIP 在 Pectra 之后通过 BPO fork 调节 target/max 的机制与调度表。
3. **明确观测日的"当前激活 blob schedule"**：在写出 `TPS_DA` 前，先用 ethereum/EIPs
   仓库、ethereum/execution-specs、ethereum/consensus-specs、ACD 与 ethereum-magicians
   讨论记录、以及主流客户端 release notes（geth / reth / prysm / lighthouse）来验证
   截至 2026-05-20 是否有 BPO fork 已激活并将 target/max 从 6/9 调到其他数值。
   如果有，outline 与后续草稿必须使用 BPO 后的 target/max，而不是默认回到
   post-Pectra 6/9 —— 这是直接影响 DA ceiling 的关键参数。
4. **拆解 `usable_payload_bytes_per_blob`**：明确 protocol raw 128 KiB → rollup 可写
   payload 之间的差额来源：
   - field element 编码：每 32-byte field element 中只有 ≤31 bytes 是 rollup payload
     可写区（OP Stack 用 31-byte encoding 而非 32-byte，最大上限 4096 × 31 = 126,976
     bytes）；具体编码常量需要从 op-batcher 的 `BlobsType` 编码路径与 op-node
     derivation 的 blob decoder 反查。
   - frame / channel header overhead（OP Stack frame format：channel ID + frame
     number + frame data length + is_last 标志位）。
   - 编码后的 zero-padding：channel 不足以填满 blob 时的 trailing padding。
   - 因此 `usable_payload_bytes_per_blob` 必须来自 base/base 与 mantlenetworkio/mantle-v2
     的 batcher 源码常量（不要硬编码 128 KiB），并在表中分别给出 Base 与 Mantle 的数值
     （如果两者编码版本不同则分别列出）。
5. 结合 L1 slot 时间（12s）计算 pre-Pectra / post-Pectra / 当前激活 BPO 下的最大
   physical DA 带宽 (bytes/s) 与年化容量。
6. 给出 Fusaka / PeerDAS 路线图对 blob 数量与采样模型的预期变化（仅作展望，不展开
   PeerDAS 内部细节）。

- **Priority**: high
- **Dependencies**: none

### item-2: 有效 DA 字节与压缩比基线

建立"L2 交易 → 落到 L1 blob 上的字节数"的映射模型。需要确定四类典型 L2 交易（ERC-20
transfer、Uniswap v3 exactInputSingle swap、ERC-721 mint、合约部署）的 RLP 原始字节
大小区间，以及 OP Stack span batch (Holocene/Isthmus 后) 的字段布局与压缩算法（zlib /
brotli）。从 op-batcher 与 op-node derivation 代码 (mantle-v2 / op-geth fork) 验证
Mantle 是否启用 span batch；从 base/base 的 batcher 配置确认 Base 当前的压缩策略与
channel timeout。压缩比定义统一为 `compressed_channel_bytes / sum(raw_RLP_bytes)`，
分母用每种交易类型的 RLP 大小基准值，分子来自批量采样的 channel size。基于公开 Dune
query 或自行 RPC 采样估算实测压缩比，并给出每种交易类型的"压缩后 DA 字节 / 交易"基准
值。该值是 item-6 公式中 `avg_compressed_bytes_per_tx` 的来源。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Base 主网 Blob 提交模式与填充率

测量 Base mainnet 上 Base batcher 的 blob 提交模式：每 L1 block 的平均 blob 数、最大
blob 数、blob 间隔 (channel cadence)、每个 blob 的 **decoded payload fill-rate**
（定义为 `decoded_channel_bytes / usable_payload_bytes_per_blob`，**不再以 128 KiB 为
分母**）、calldata 回退占比、blob base fee 与 batcher 经济触发条件。重点回答"Base 在
当前激活的 blob schedule 下是否用满 target blobs/block"以及"Flashblocks 200ms 子块
时间是否改变 blob 提交节奏"。

**测量可行性约束（必须遵守）**：

- EIP-4844 sidecar 在执行层客户端默认 retention 约 18 天 (`MIN_EPOCHS_FOR_BLOB_SIDECARS_REQUESTS`
  ≈ 4096 epochs)，**raw L1 RPC 不能保证拿到 >18 天前的 decoded blob payload**。仅靠
  blob 计数（来自 L1 block header 的 `blob_versioned_hashes`）无法计算 fill-rate ——
  必须拿到 decoded payload bytes。
- 因此 item-3 必须从下面两条路径中**选择一条并在 outline 草稿里显式声明**：
  - **路径 A（archival-indexer 优先，推荐）**：使用 blobscan.com、Dune 的
    `ethereum.beacon_blob_sidecars` / `ethereum.blob_data` indexed tables、
    Etherscan blob explorer、或自行长期归档的 blob storage 服务作为 decoded payload
    数据源，采用 **>=200k L1 blocks (~30 天)** 完整窗口。
  - **路径 B（raw-RPC 缩短窗口 + indexer 回退）**：把 raw L1 archive RPC 直接采样
    窗口缩短至 **≤14 天**（落在 sidecar retention 内），并对窗口前段缺失的样本
    使用 Dune / Etherscan / blobscan 作为 fallback；fallback 比例 >20% 时必须在表中
    标注 confidence=medium。
- batcher 地址：`0x5050F69a9786F081509234F1a7F4684b5E5b76C9` (Base mainnet batcher)。
  通过 `eth_getBlockByNumber` 拉取 L1 block 中的 type-3 transaction，再用上面选定的
  数据源回填 decoded blob bytes。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Mantle 主网 Blob 提交模式与填充率

同样的方法应用到 Mantle mainnet：测量 mantle-v2 batcher 的 blob 提交节奏、blob
**decoded payload fill-rate**（同 item-3 的分母定义）、是否仍存在 calldata 提交（哪些
条件下回退）、blob 时间间隔与 channel timeout 配置。

数据来源遵循与 item-3 相同的可行性约束（archival-indexer 优先；raw-RPC 必须在
sidecar retention 内并配置 fallback）。在写草稿之前必须先回答两个先决条件：

1. **当前 DA 模式确认**：从 mantle-v2 配置（rollup.json / SystemConfig）确认 batcher
   地址、确认 mantle-v2 截至 2026 Q2 主网当前使用的 DA 通道是 EIP-4844 blob、calldata
   还是 alt-DA (EigenDA / Celestia)。如果 Mantle 没有启用 blob 通道，item-4 改为
   "记录当前 DA 模式 + 提供等效 DA 带宽换算"，并把对比表的 fill-rate 字段标记 N/A。
2. 给出与 Base 同维度的对比数据，并标注观测窗口、样本量、置信区间。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: Calldata vs Blob 混合策略与回退条件

分析两条链的 DA 提交决策树：什么条件下提交 blob、什么条件下回退到 calldata、是否存在
混合提交（同一 batch 部分走 blob 部分走 calldata）。聚焦三个触发条件：(a) blob base
fee 飙升时的成本回退、(b) 数据量小于一个 blob 时的填充策略（pad / 等待 / 走 calldata）、
(c) 链上拥堵或 inclusion delay 触发的紧急提交。需要从 op-batcher 源码（mantle-v2 与
base 的 batcher 配置）核对算法，并用 item-3 / item-4 的实测数据验证回退的实际发生
频率与成本影响。明确"protocol 层 DA 容量"、"batcher 实际利用"与"economically-usable
DA 容量"（item-7 使用）三者之间的差距来源与传递方向。

- **Priority**: medium
- **Dependencies**: item-3, item-4

### item-6: DA 带宽 → TPS 映射模型

构建从 DA 带宽到 L2 TPS 上限的封闭公式，**显式使用 `usable_payload_bytes_per_blob`
而不是硬编码 128 KiB**：

```
usable_payload_bytes_per_blob  := (from batcher/derivation code, item-1.4)
fill_rate                      := decoded_channel_bytes / usable_payload_bytes_per_blob
active_target_blobs_per_block  := (from item-1.3, observation-date-dependent)
slot_time                      := 12 s

TPS_DA = (active_target_blobs_per_block × usable_payload_bytes_per_blob × fill_rate)
         / (slot_time × avg_compressed_bytes_per_tx)
```

对每个参数做敏感度分析。给出至少六种场景的 TPS 上限：

1. pre-Pectra: target=3, fill=70%, usable=126,976 B
2. post-Pectra (EIP-7691 baseline): target=6, fill=70%
3. post-Pectra: target=6, fill=95%
4. **观测日激活的 BPO 调度** (用 item-1.3 的实测值；如无 BPO 激活则在表中显式
   标注 "no BPO active as of YYYY-MM-DD")
5. Mantle 当前观测值（item-4）
6. Base 当前观测值（item-3）

同时基于四种交易 mix（重 transfer / 重 swap / 均衡 / 重合约部署）展开，输出"DA 约束的
TPS 上限"矩阵。结果与课题 3 (Gas 协议层) 和声明的 Base 5k TPS 数字做对照。所有
TPS_DA 数字都属于 **physical capacity** 下的上限；economic capacity 在 item-7 处理。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4

### item-7: Binding Constraint 判定（physical vs economically-usable 双判定）

判定 DA 层在当前 (post-Pectra / 观测日激活的 BPO 调度) 是否是 Mantle TPS 的 binding
constraint。**必须给出两套判定**：

1. **Physical capacity 判定**：用 item-6 的 `TPS_DA` (physical) 与执行层约束
   （block gas limit / block time / per-tx gas cap / state growth）、Sequencer 约束
   （mempool 与 ordering）做对照。
2. **Economically-usable capacity 判定**：把 physical TPS_DA 折算到拥堵窗口下的
   "经济可用 DA 容量"，至少考虑：
   - **Blob base-fee 飙升场景**：参考近 30 天内 blob base fee 出现的 P95 / P99 峰值
     窗口（含 Pectra 后 max=9 blobs 引发的 fee 振荡），计算 batcher 在该价格下
     不亏本可提交的最大 blob 数（与 batcher 经济阈值对照）。
   - **Inclusion-delay 约束**：拥堵 L1 区块下 type-3 tx 排队 / 重提交导致的有效
     blob 提交速率下降。
   - **calldata 回退成本上限**：blob 涨价后回退 calldata 的等效 DA 带宽降级幅度
     （由 item-5 的回退算法 + Pectra 后 calldata cost 决定）。

把这两套判定合并成三种可能结论：

- (a) Physical 与 economic 都是 binding：DA 在任何场景下都限制 Mantle TPS → 优先攻关
  DA 利用率 + 填充率优化（item-8）。
- (b) Physical 不是 binding，但 economic 是：拥堵 / fee 高时 DA 才成为瓶颈 → 重点是
  batcher 的 fee strategy / 跨用户聚合 / inclusion robustness。
- (c) Physical 与 economic 都不是 binding：瓶颈在执行/sequencer → DA 优化收益小。

每种结论下都要给出 Mantle 的优化路径与触发条件（"在何种 fill_rate / blob fee 区间下
切换策略"）。

- **Priority**: high
- **Dependencies**: item-6, item-5

### item-8: Mantle 可获得的 TPS 提升空间与优化杠杆

将 item-6 / item-7 的结论转换为可落地的优化建议。优化杠杆至少覆盖：(a) 提升 blob
填充率（增加 channel timeout 上限 / 批量聚合 / 跨用户 batch）；(b) 增加每 L1 block
的 blob 数（如当前未用满 target 或 BPO 已上调 target）；(c) 提升 OP Stack 压缩比
（升级到 Isthmus span batch v2 / brotli quality 调整 / 31-byte encoding 优化）；
(d) 减小每笔 L2 tx 的 RLP 字节（calldata 优化指南推广至生态）；(e) batcher fee
strategy 与 inclusion robustness（item-7 economic 判定下的杠杆）。每条杠杆给出预期
TPS 增益、工程复杂度、风险（成本上升、inclusion delay、回滚策略）与可观测的成功指标。

- **Priority**: medium
- **Dependencies**: item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| current_value | 主网/规范当前生效数值（含数据来源时间戳） | item-1, item-3, item-4 |
| activation_fork | 该数值在哪个 hardfork 或 BPO fork 生效（Cancun, Prague/Pectra, BPO-YYYY-MM 等） | item-1, item-5, item-6 |
| current_active_blob_schedule | 观测日 `(target_blobs_per_block, max_blobs_per_block)`，并标注来源 EIP / BPO meta EIP（EIP-4844 / EIP-7691 / EIP-7840 / EIP-7892 / 具体 BPO fork）与激活 L1 epoch；在 outline 写出 TPS_DA 之前必须填写 | item-1, item-6, item-7 |
| usable_payload_bytes_per_blob | rollup 可写 payload 字节数（128 KiB 减去 field element 编码、frame header、channel padding），来源必须是 batcher/derivation 源码常量 | item-1, item-2, item-3, item-4, item-6 |
| measurement_method | 观测方法（archival-indexer 优先；如用 raw RPC 必须在 sidecar retention 内并标注回退方案） | item-3, item-4, item-5 |
| observation_window | 观测时间窗口、样本量与 retention 内/外标注（如 "近 14 天 raw RPC + Dune fallback for older samples"） | item-3, item-4 |
| data_source_class | archival_indexer / raw_rpc / dashboard / cross_check；用于判断 fill-rate 数字的可信度 | item-3, item-4 |
| formula | 推导用的封闭公式与参数定义；TPS_DA 公式必须用 `usable_payload_bytes_per_blob` 与 `active_target_blobs_per_block` 表达 | item-1, item-2, item-6 |
| sensitivity_range | 关键参数的敏感度区间（lower / median / upper） | item-2, item-6, item-7 |
| confidence | 高 / 中 / 低（基于实测 / 规范推算 / 类比 / fallback 比例） | all |
| source_evidence | 主要证据链接（commit / 区块范围 / Dune query URL / EIP 编号 / blobscan URL） | all |
| economic_capacity_scenario | 拥堵/fee 飙升场景下的可用 DA 容量（与 physical capacity 区分） | item-5, item-7 |
| recommendation | 针对 Mantle 的可落地建议（保持 / 调整 / 升级） | item-5, item-7, item-8 |
| binding_assessment | 该项是否构成 Mantle 当前 binding constraint 的证据，并区分 physical / economic | item-3, item-4, item-6, item-7 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Base vs Mantle 近 30 天 blob 提交频率与 decoded payload fill-rate 对比（柱状或表格化的 Mermaid；标注数据源类（archival vs raw）与窗口） | mermaid | item-3, item-4 |
| diag-2 | flow | DA 带宽 → 有效 TPS 上限的映射流程（128 KiB protocol blob → usable_payload_bytes_per_blob → fill_rate → TPS_DA → economic-adjusted TPS_DA） | mermaid | item-1, item-2, item-6, item-7 |
| diag-3 | hierarchy | Binding constraint 决策树（physical-DA vs economic-DA vs 执行层 vs Sequencer），含两套判定路径 | mermaid | item-7 |
| diag-4 | timeline | EIP-4844 → Pectra (EIP-7691) → EIP-7840 / EIP-7892 BPO 调度 → Fusaka/PeerDAS 路线图时序，并标注观测日的"当前激活 schedule" | mermaid | item-1 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | EIP 规范：EIP-4844, EIP-7691, EIP-7840, EIP-7892, 任何在观测日已激活的 BPO meta EIP，以及 PeerDAS/Fusaka 路线图文档；必须能定位到 BPO 激活的 L1 epoch | 4 |
| src-2 | code_analysis | base/base 与 mantlenetworkio/mantle-v2 (含 op-geth fork) 的 batcher / SystemConfig / rollup 配置 + op-node derivation；用于 `usable_payload_bytes_per_blob` 常量与编码版本 | 2 |
| src-3 | on_chain_data | Base mainnet 近 30 天 blob 提交数据；必须使用 archival blob indexer（blobscan / Dune blob_data / Etherscan blob explorer）作为 decoded payload 源，raw RPC 仅用于 sidecar retention 内的子窗口 | 1 |
| src-4 | on_chain_data | Mantle mainnet 近 30 天 blob 提交数据；同 src-3 的可行性约束。若 Mantle 当前不用 blob 通道，记录其 DA 模式与等效带宽换算源 | 1 |
| src-5 | industry_reports | L2Beat、Dune dashboards (含 blob fee market 与 fill-rate)、growthepie、blobscan 自带分析等公共 DA 利用率统计 | 2 |
| src-6 | expert_commentary | Base / Mantle / Optimism 团队关于 DA 策略、batcher 优化、blob fee 经济性、BPO 激活影响的公开博客或会议 talk | 2 |
| src-7 | client_release_notes | 主流 EL/CL 客户端 (geth, reth, prysm, lighthouse) 关于 Pectra / BPO 激活时点的 release notes，用于交叉验证 `current_active_blob_schedule` | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | revise | item-1, item-2, item-6, Fields, expected_output, scope | 把硬编码 128 KiB 替换为来自 batcher/derivation 源码的 `usable_payload_bytes_per_blob`；显式拆解 field-element 编码 / frame header / channel padding 的差额来源；fill_rate 重新定义为 `decoded_channel_bytes / usable_payload_bytes_per_blob` | Review Verdict round-1 #1 (Make blob payload capacity explicit) |
| 2 | revise | item-3, item-4, Fields (measurement_method, observation_window, data_source_class), Source Requirements (src-3, src-4) | EIP-4844 sidecar retention (~18 天) 内 raw RPC 才有 decoded blob payload；30 天窗口必须用 archival blob indexer (blobscan / Dune blob_data / Etherscan)，或缩短 raw-RPC 窗口至 ≤14 天 + 显式 fallback；blob 计数本身不足以计算 fill-rate | Review Verdict round-1 #2 (Fix measurement feasibility plan) |
| 2 | add | Fields (current_active_blob_schedule), item-1.3, item-6 scenarios, Source Requirements (src-7) | 新增 `current_active_blob_schedule` 字段，要求在写 TPS_DA 之前用规范 + 客户端 release notes 验证观测日的有效 target/max；若 BPO 已激活则使用 BPO 数值，不再默认 post-Pectra 6/9 为"当前" | Review Verdict round-1 #3 (Parameterize active blob schedule by observation date) |
| 2 | revise | item-5, item-7 (双判定), Fields (economic_capacity_scenario), Diagram diag-2 / diag-3 | item-7 拆成 physical capacity 判定 + economically-usable capacity 判定；后者要求考虑 blob base-fee 飙升、inclusion delay、calldata 回退降级；diag-2 / diag-3 加入 economic-adjusted 路径 | Review Verdict round-1 #4 (Add fee-market dynamics to binding test) |
