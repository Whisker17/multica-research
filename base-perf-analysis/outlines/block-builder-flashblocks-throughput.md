---
topic: "Block Builder 与 Flashblocks 对吞吐量的影响分析"
project_slug: base-perf-analysis
topic_slug: block-builder-flashblocks-throughput
github_repo: Whisker17/multica-research
round: 1
status: approved
approved_at: "2026-05-20T04:26:08Z"
approved_by: "agent:orchestrator (Orchestrator, id=273629f0-3fe7-47c4-aae7-846a11dbbe13)"
approval_evidence: "Phase B dispatch comment e6ceb60a-5a54-4b4f-83af-33dee3f07217 — Outline APPROVED, no revisions needed"

artifact_paths:
  outline: base-perf-analysis/outlines/block-builder-flashblocks-throughput.md
  draft: base-perf-analysis/research-sections/block-builder-flashblocks-throughput/drafts/round-{n}.md
  final: base-perf-analysis/research-sections/block-builder-flashblocks-throughput/final.md
  index: base-perf-analysis/research-sections/_index.md

scope: |
  分析 Base 的 Block Builder 分离架构（rollup-boost）与 Flashblocks 机制对"有效吞吐量"的提升贡献，
  覆盖：(1) rollup-boost 的 Engine API 多路复用与 builder-vs-local payload 选择策略；
  (2) 空块率从 ~200/天降至 ~2/天的实现机制与对有效 gas-throughput 的影响；
  (3) Flashblocks 200ms sub-block 粒度对节点同步、状态一致性与用户感知 TPS 的影响；
  (4) Mantle 当前 block building 现状与 `mantle-xyz/reth` flashblocks-aware/POC 分支的进展评估；
  (5) Builder 分离对 sequencer 主循环 CPU/内存释放的量化估算。
  本研究专注吞吐量维度；安全性、HA 故障转移、MEV 策略不在范围内。
audience: |
  Mantle/Base 协议工程师与 sequencer 团队；
  Multica 研究 squad 内部下游 Research Agent（sequencer-consensus-pipeline-perf,
  batcher-sequencer-backpressure, perf-gap-analysis-recommendations）；
  OP Stack 生态中评估 rollup-boost / Flashblocks 集成可行性的运营者；
  关注 L2 user-perceived TPS（pre-confirmation）与最终 TPS 区别的研究者。
  读者熟悉 Engine API（newPayload / forkchoiceUpdated / getPayload）与 OP Stack sequencer 流程。
expected_output: |
  - rollup-boost 数据流架构图，含 Engine API multiplexing 与 BlockSelectionPolicy 决策树
  - Builder vs Local payload 选择逻辑的代码级解析（带 file:line 引用）
  - 空块消除机制的工程拆解：从 ~200/天 → ~2/天 是 builder 持续构建、pending tx 检测、还是其它机制
  - Flashblocks sub-block（200ms 粒度）的生命周期与广播路径（WebSocket vs P2P `flblk/1`）
  - Flashblocks 对节点同步与状态一致性的额外开销量化（CPU、网络、磁盘）
  - Mantle `flashblocks/poc` 与 `feat/flashblocks-mantle-aware` 分支的进展评估与阻塞点
  - Builder 分离前后 sequencer 主循环 CPU/内存占用的量化对比估算
  - 至少 2 张 Mermaid 图（rollup-boost 数据流 / Flashblocks 生命周期 / Sequencer 对比任选）
  - Mantle 引入 rollup-boost + Flashblocks 的可行性结论与改造路径

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-20T04:35:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-20T05:30:00Z"
---

# Research Outline: Block Builder 与 Flashblocks 对吞吐量的影响分析

## Items

### item-1: rollup-boost 架构与 Engine API 多路复用

调查 rollup-boost 作为外部 builder/proxy 在 Base sequencer 与 EL 之间的位置：它如何同时接收
sequencer 的 `engine_forkchoiceUpdated` / `engine_getPayload` 调用并向 base-reth-node（local）与
外部 builder 双路分发；payload 收集的并行/竞速模式；超时与回退（builder 慢/挂时如何 fallback
到 local）的工程实现。代码切入点：`base/base` → `crates/builder`，以及 `flashbots/rollup-boost`
仓库的 proxy server 实现。需要识别每一跳的延迟开销（解析、序列化、HTTP/gRPC 调用），评估
"接入 builder 是否引入了 sequencer 主循环延迟"。

- **Priority**: high
- **Dependencies**: none

### item-2: BlockSelectionPolicy 与 Builder/Local payload 选择策略

深入 `BlockSelectionPolicy`（基于 `gas-used` 的选块策略）：它如何在 builder 与 local payload
之间打分、tie-breaker、是否对 builder payload 做合法性校验（state-root 一致性、tx 顺序）。
讨论"选 builder block 提升 gas 利用率" vs "等待 builder 可能引入延迟" 的 trade-off，以及
如何防止 builder 提供更优块但代价是慢 X ms 的情况下打破 block-time SLO。给出 Base 实际配置
（超时阈值、最少等待时间、policy 参数）。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 空块消除机制与有效 gas-throughput 提升

定量分析"空块率从 ~200/天降至 ~2/天"的具体实现路径：(a) 是 builder 持续在后台构建 payload
直到截止时间，还是 (b) sequencer 在 mempool 为空时跳过新 block，还是 (c) 两者结合；
对照 stock OP Stack 的 empty-block 触发条件（block time 到点但 mempool 空时仍产生 0-tx block）。
量化"非空块占比提升"对有效 gas-throughput（gas_used/s 而非 gas_limit/s）的实际贡献，承认
"理论 TPS" 与 "有效 TPS" 的区别。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Flashblocks sub-block 生命周期与广播路径

绘制 Flashblocks 的端到端数据流：sequencer 内部以 200ms 粒度切出 sub-block → builder 或
sequencer 发布到 Flashblocks producer → WebSocket 广播给订阅节点 vs P2P `flblk/1` 子协议在
节点之间传播 → consumer 节点合并 sub-block 形成最终 block。明确每个角色（producer / proxy /
consumer / verifier）的职责，以及 Flashblocks payload 相对完整 block payload 的精简内容
（移除哪些字段、为什么不影响共识）。引用 `specs/flashblocks_p2p.md` 永久链接。

- **Priority**: high
- **Dependencies**: none

### item-5: Flashblocks 对节点同步、状态一致性与吞吐量的额外开销

讨论 200ms sub-block 粒度对：(a) 节点本地状态机的 reorg/rewind 频率与代价、(b) RPC 层 `eth_getBlockByNumber`
与 `pending` 语义的扩展、(c) WebSocket 长连接的 CPU 与内存占用、(d) P2P `flblk/1` 在节点间的带宽
放大。区分"用户感知 TPS（pre-confirmation 体验，200ms 内可见交易）"与"链最终 TPS（每 2s block
确认的 gas）"，避免把 pre-confirmation 误算入吞吐量本身。

- **Priority**: high
- **Dependencies**: item-4

### item-6: Mantle 当前 Block Building 现状

梳理 Mantle 主网目前的 block building 流程：是否有 builder 分离？sequencer 直接调用 EL
`engine_getPayload`？空块率与有效 gas 利用率现状（链上抽样）？这是 Mantle 与 Base 在
"有效 TPS" 上差距的多少比例？为后续 item-7 的可行性评估提供 baseline。

- **Priority**: high
- **Dependencies**: none

### item-7: Mantle flashblocks/poc 与 feat/flashblocks-mantle-aware 分支评估

阅读 `mantle-xyz/reth` 仓库 `flashblocks/poc` 与 `feat/flashblocks-mantle-aware` 两个分支的
所有 commit，给出：(a) 实现到什么阶段（producer / consumer / 全链路）、(b) 与 Base/Flashbots
上游的兼容性、(c) 当前阻塞点（如 sequencer 改动、共识层适配、MetaTx/L1 cost 与 sub-block 的交互）、
(d) 估算从 POC 到生产可用的剩余工程量。代码切入点：相关分支的最新 commit hash + 文件:行号。

- **Priority**: high
- **Dependencies**: item-1, item-4, item-6

### item-8: Builder 分离对 Sequencer 主循环的资源释放

量化估算：若 Mantle 引入 rollup-boost 类似架构，sequencer 主循环中以下负载会被卸载到 builder
进程：(a) tx ordering / inclusion logic、(b) gas 估算与 mempool 查询、(c) payload assembly
（state warm-up、execute、state-root）。结合 item-3/4，估算释放出来的 CPU/内存能否被用于
提升 block-time 或并行执行的资源，给出"sequencer 主循环延迟降低 X%"的 first-order 估算
（标注证据等级）。

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-3

### item-9: Mantle 引入 rollup-boost + Flashblocks 的可行性与改造路径

综合 item-1 ~ item-8，输出 Mantle 引入 builder 分离 + Flashblocks 的可行性结论，包括：
(a) 所需的客户端改造范围（reth fork、共识层、RPC 层）、(b) 与 Mantle 特有逻辑（MetaTx、
L1 cost）的兼容性风险、(c) 与项目其他 Wave 建议（执行层并行 EVM、gas 参数调整、batcher 重构）
的依赖与协同、(d) 阶段性目标（POC → 测试网 → 主网）的预估时间线与人月成本。
至少给出 2 条具体改造建议，按优先级排序。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7, item-8

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| code_locations | 关键文件路径与行号引用（path:line），含 commit SHA | all |
| protocol_role | 该 item 涉及的角色（sequencer / builder / proxy / producer / consumer / EL / 共识） | item-1, item-2, item-4, item-5, item-7 |
| data_flow_summary | 数据流摘要（input/output、调用方向、序列化格式） | item-1, item-2, item-4 |
| latency_breakdown | 各跳/各阶段延迟拆解（建立连接 / 序列化 / 执行 / 网络往返），含数量级估算 | item-1, item-2, item-4, item-5 |
| throughput_impact | 对有效 gas-throughput / 用户感知 TPS / 最终 TPS 的量化影响（带证据等级） | item-2, item-3, item-5, item-8 |
| empty_block_evidence | 空块率相关的链上数据 / 公开报告（Base 主网 vs Mantle 主网抽样） | item-3, item-6 |
| mantle_compatibility | 与 Mantle 特有逻辑（MetaTx、L1 cost、MNT gas token）的兼容性风险 | item-6, item-7, item-9 |
| feasibility_metadata | 可行性评估的成本/风险/收益评分，依赖关系，前置工程 | item-7, item-9 |
| cross_topic_dependencies | 与其他研究主题（execution-layer-reth-fork-comparison、sequencer-consensus-pipeline-perf、batcher-sequencer-backpressure、gas-protocol-perf-config）的接口/重叠 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | rollup-boost 数据流架构图：sequencer → rollup-boost proxy → (builder + base-reth-node 双路) → BlockSelectionPolicy 选块 → 提交回 sequencer；标注 Engine API 调用方向与超时回退路径 | mermaid | item-1, item-2 |
| diag-2 | flow | Flashblocks 生命周期：producer 生成 sub-block → WebSocket 广播 / P2P `flblk/1` 传播 → consumer 节点累积 sub-block → 形成最终 block；区分 mempool/pre-confirmation 与 finalized block 时间轴 | mermaid | item-4, item-5 |
| diag-3 | comparison | Sequencer 主循环对比：左侧 stock OP Stack（sequencer 内嵌 builder），右侧 Base（sequencer + rollup-boost 分离），高亮卸载到 builder 的负载块 | mermaid | item-8 |
| diag-4 | timeline | Mantle 改造路径时间线：从现状（POC 分支）→ 各阶段里程碑（producer 上线、consumer 上线、生产可用），与其他 Wave 建议的并行/依赖关系 | mermaid | item-9 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | `base/base` 仓库 `crates/builder` 目录代码扫描，含 commit SHA 与文件:行号引用 | 1 |
| src-2 | code_analysis | `flashbots/rollup-boost` 仓库源码（proxy server、BlockSelectionPolicy 实现） | 1 |
| src-3 | code_analysis | `mantle-xyz/reth` 仓库 `feat/flashblocks-mantle-aware` 与 `flashblocks/poc` 两个分支的全部 commit | 2 |
| src-4 | official_docs | Flashblocks P2P 规范 `specs/flashblocks_p2p.md`（base 仓库内或 specs.base.org） | 1 |
| src-5 | official_docs | Base Azul 升级博客（blog.base.dev/introducing-base-azul）与 specs.base.org/upgrades/azul/* 中 builder/Flashblocks 章节 | 2 |
| src-6 | expert_commentary | Flashbots 团队关于 rollup-boost 的公开博客或演讲（介绍设计目标与 throughput 数据） | 1 |
| src-7 | on_chain_data | Base 主网空块率（抽样统计或 Dune dashboard）、Mantle 主网空块率与有效 gas 利用率（抽样） | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
