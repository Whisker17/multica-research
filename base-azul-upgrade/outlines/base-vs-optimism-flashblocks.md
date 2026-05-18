---
topic: "Base vs Optimism Flashblocks 机制与设计差异对比"
project_slug: base-azul-upgrade
topic_slug: base-vs-optimism-flashblocks
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: base-azul-upgrade/outlines/base-vs-optimism-flashblocks.md
  draft: base-azul-upgrade/research-sections/base-vs-optimism-flashblocks/drafts/round-{n}.md
  final: base-azul-upgrade/research-sections/base-vs-optimism-flashblocks/final.md
  index: base-azul-upgrade/research-sections/_index.md

scope: |
  系统对比 Base 与 Optimism（以 Unichain 为代表的 OP Stack flashblocks 采用方）在 Flashblocks 机制
  上的设计理念、共享组件、差异化实现与运营策略，以 `flashbots/rollup-boost` 为锚点，沿
  Producer 层 → Protocol 层 → Builder 层 → Consumer 层 → Propagation 层 → HA 层 → 协议演进 七条
  轴线展开。重点对比内容：

  - **Producer 层共享与差异**：rollup-boost 作为 OP Stack sequencer sidecar 的 Engine API multiplexing
    架构（`engine_forkchoiceUpdated` builder + fallback EL 双路、`engine_getPayload` builder-first
    with local fallback、`BlockSelectionPolicy` 基于 gas-used 的选块策略）、各链是否存在 fork 或
    chain-specific patches。
  - **Flashblocks 协议核心**：`FlashblocksPayloadV1` / `ExecutionPayloadFlashblockResultV1` /
    `ExecutionPayloadStaticV1` 数据结构、`FLASHBLOCKS_TIME = 200ms`、`FLASHBLOCKS_PER_L2_BLOCK`、
    `flashblock_gas_limit(i) = (i/F) * block_gas_limit` 线性 gas-limit、SSZ + 4-byte version
    prefix 编码、state root 内嵌策略、validity rules（monotonic index、immutable base、every prefix
    valid）。
  - **Builder 端 (`flashbots/op-rbuilder`)**：gas-limit heuristic `F` 值对 tx 包含的影响（F=10 下
    max tx fits in flashblock 4）、tx 排序与 MEV 处理在不同链上的差异。
  - **Consumer 层三方实现**（重点更新维度）：
    - `base/base`（原 `base/node-reth`）下 `crates/execution/flashblocks` + `flashblocks-node`
      的完整实现（含 `CanonicalBlockReconciler`、`ReorgDetector`、`PendingBlocksBuilder`、
      multi-block flashblocks sync）。
    - `paradigmxyz/reth` 历史上在 `crates/optimism/flashblocks` 提供的 `reth-optimism-flashblocks`
      crate（自 v1.7.0 引入、v1.9.4 仍在）；commit `372802d06`（2026-02-06）的 `chore: remove
      op-reth from repository (#21532)` 将 op-reth（含 flashblocks 子模块）整体迁移至
      `ethereum-optimism/optimism` 的 `rust/op-reth/crates/flashblocks/`（当前 v1.11.3）。Phase B
      必须澄清「Flashbots 官方推荐 paradigmxyz/reth」与「代码现位于 ethereum-optimism/optimism」
      之间的实际关系，并定位 `pending` tag overlay 的具体实现。
    - `danyalprout/reth-flashblocks`：根据公开 GitHub 列表，目前在该账户下未见同名 repo；相关工作
      已上游化进入 paradigmxyz/reth → ethereum-optimism/optimism 路径，且 `danyalprout` 名下尚存
      `flashblocks-demo`、`flashblocks-websocket-client` 等辅助工具。Phase B 需明确这一 fork 的现
      状（是否已 archived、是否有遗留分叉、与上游差异是否仍存在）。
    - JSON-RPC overlay：`pending` tag overloading、`op_supportedCapabilities` 返回值、Flashblocks
      RPC 数据流（WebSocket → `FlashblocksPayloadV1` → in-memory cache → pending 请求响应 → 状态
      一致性）。
  - **WebSocket Proxy 架构与运营**：`base/flashblocks-websocket-proxy`（Base 维护的 canonical proxy）
    与 `flashbots/rollup-boost` 内置 `crates/websocket-proxy`（Redis 分布式限流约 48KB
    `rate_limit.rs`、Brotli 压缩、auth/registry/subscriber 设计）的关系；fan-out 拓扑与单向广播
    设计；以及 `flashbots/rollup-boost` 在 commit `f6d1246`（2025-12-16）`Remove flashblocks-rpc
    crate (#456)` 后该 crate 的去向（仍以 vendored 形式存在于 `ethereum-optimism/optimism` 的
    `rust/rollup-boost/crates/flashblocks-rpc/`）。
  - **HA 故障转移**：现有 WebSocket 广播方案的 HA 缺陷、Base TDD（Notion: "TDD: Rollup Boost
    Integration with HA Sequencer"）与 `op-conductor` 的集成、`specs/flashblocks_p2p.md` 中
    devp2p `flblk/1` 子协议、双签名 `Authorization` 机制（sequencer + builder）、`StartPublish` /
    `StopPublish` 实现 HA 切换、取消 rollup-boost 同步验证并以 Authorization 取代信任的设计，以
    及各链的 P2P 方案采用进度。
  - **协议演进方向**：Flashblocks v2（rollup-boost issue #321）、Flashtestations TDX/TEE 可信块构建
    规范（`specs/flashtestations.md`）、压缩方案演进（json → zstd+dict → brotli → raw，issue
    #455）。

  本研究**不**重复 `flashblocks-network-changes`（WHI-30）已覆盖的 Azul payload 简化（移除
  `new_account_balances` / `receipts`、保留 `access_list` 但不填充）与 Engine API V5 / eth/69 协议
  变更；**不**进入 Multiproof 与 Osaka EVM 范畴；**不**包含实际部署运维（仅设计与实现差异）。

audience: |
  Mantle 团队评估是否引入或借鉴 Flashblocks 的技术决策者与工程实施者；Base / OP Stack 生态研究者；
  Multica 研究 squad 下游 Research Agent（特别是若后续派生 `mantle-impact-assessment` 的影响评估
  者）；Flashblocks consumer / RPC provider 集成方（Alchemy / QuickNode / 自建 op-reth 节点的团
  队）；MEV searcher、indexer、wallet/SDK 开发者评估 200ms preconfirmation UX 接入门槛。读者熟悉
  Ethereum Engine API、L2 sequencer 架构与 OP Stack 模块化协议，但不一定熟悉 Flashblocks 的具体规
  范与各家实现内部结构。

expected_output: |
  - rollup-boost 共享 Producer 层架构图与链间差异化配置分析（含 Engine API multiplexing 序列、
    BlockSelectionPolicy 选块流程、Base vs Optimism/Unichain 在 fork/配置/CLI flags 层面的具体偏离
    点；如不存在偏离，需明确说明并给出 commit 证据）。
  - Flashblocks 协议核心数据结构与参数 spec 解读（含 `FlashblocksPayloadV1` 字段映射、SSZ 编码示
    例、`F` 值取值与 tx 包含矩阵、state root 内嵌的 rationale）。
  - **Consumer 层三方实现深度对比**：分别从「代码位置 + 行数级别 + crate 命名」「实现能力矩阵」
    「`pending` tag overlay 路径」「multi-block flashblocks sync 支持」「JSON-RPC 方法覆盖」
    「演进 / 上游化 / 废弃状态」「Mantle 接入成本估算」七个维度逐项比较 `base/base` 的
    `flashblocks-node` extension、`ethereum-optimism/optimism` 中 `rust/op-reth/crates/flashblocks`
    及 `rust/rollup-boost/crates/flashblocks-rpc`、以及 `danyalprout/reth-flashblocks`（实际存在
    性 / archived 状态 / fork lineage）。
  - reth 原生 flashblocks 支持的代码架构与上游化时间线（v1.7.0 引入 → v1.9.4 仍在 → commit
    `372802d06` 迁移至 ethereum-optimism/optimism；commit `f6d1246` 在 rollup-boost 上游移除
    flashblocks-rpc crate）。
  - WebSocket（rate-limited fan-out + brotli + auth）vs P2P（devp2p `flblk/1` + Authorization 双
    签名 + StartPublish/StopPublish）两种传播方案的架构对比与 HA 行为对比。
  - HA 故障转移策略对比表：WebSocket 方案缺陷 → op-conductor 集成 → P2P Authorization 切换路径，
    各链当前采用进度。
  - Builder (`flashbots/op-rbuilder`) gas-limit heuristic `F` 与 tx ordering 策略链间差异，对 MEV
    与用户体验的影响。
  - 协议演进路线图对比（v2、Flashtestations、压缩方案）对 Base 与 Optimism/Unichain 的不同意义，
    及对第三方 OP Stack 链的影响。
  - Mantle 接入门槛评估章节（基于上述全部 finding，给出「沿用 Flashbots 上游 + 选择何种 consumer
    实现」与「自建分叉」两条路径的 trade-off 评分）。
  - Evidence: 至少引用 rollup-boost specs（flashblocks.md、flashblocks_p2p.md、flashtestations.md）
    + crates 源码、`base/base` `crates/execution/flashblocks*` 源码、`ethereum-optimism/optimism`
    `rust/op-reth/crates/flashblocks` + `rust/rollup-boost/crates/flashblocks-rpc` 源码、
    `flashbots/op-rbuilder` 源码、`base/flashblocks-websocket-proxy` README、Flashbots 官方 RPC
    文档（rollup-boost.flashbots.net/developers/flashblocks-rpc.html）、关键 GitHub commit / issue
    / PR（如 reth #21532、reth #17858、rollup-boost #321 / #455 / #456）。
  - 至少 7 张 Mermaid 图：rollup-boost 共享架构 + 链差异全景图、Consumer 三方架构对比图、WebSocket
    vs P2P 传播架构对比图、Flashblock 构建生命周期序列图、HA 故障转移流程对比图（WebSocket vs
    P2P Authorization）、Consumer 能力对比矩阵、Flashblocks RPC 数据流图。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-18T03:00:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-18T03:00:00Z"
---

# Research Outline: Base vs Optimism Flashblocks 机制与设计差异对比

## Items

### item-1: rollup-boost 共享 Producer 层架构

调查 `flashbots/rollup-boost` 作为 OP Stack sequencer sidecar 的核心架构：Engine API multiplexing
（`engine_forkchoiceUpdated` 同时分发到 builder 与 fallback EL、`engine_getPayload` 在 builder 主
路返回 + local fallback 兜底）、`BlockSelectionPolicy` 基于 gas-used 的两路选块策略、
`crates/rollup-boost/src/server.rs`（约 62KB）与 `src/proxy.rs`（约 36KB）的职责切分，以及
client/auth、debug_api、health/probe、flashblocks launcher/service 等支撑模块。需要验证 Base 与
Optimism/Unichain 是否使用同一 rollup-boost 上游 commit、是否存在 Base-specific 配置 patches 或
CLI flag 差异；若无差异，应以 commit-pinned 证据明确「共享代码、差异在配置」。

- **Priority**: high
- **Dependencies**: none

### item-2: Flashblocks 协议核心设计与构建规则

精读 `flashbots/rollup-boost/specs/flashblocks.md`（1071 行）：数据结构（`FlashblocksPayloadV1`、
`ExecutionPayloadFlashblockResultV1`、`ExecutionPayloadStaticV1`、`Metadata` / `AccountMetadata` /
`StorageSlot` / `TransactionMetadata`）、参数（`FLASHBLOCKS_TIME = 200ms`、
`FLASHBLOCKS_PER_L2_BLOCK = L2_BLOCK_TIME / FLASHBLOCKS_TIME`）、构建规则（sequencer txs / deposits
必须在 flashblock 0；线性 gas-limit `flashblock_gas_limit(i) = (i/F) * block_gas_limit`）、SSZ +
4-byte version prefix 编码、state root 内嵌的非阻塞 rationale、`validity rules`（monotonic index、
immutable base、every prefix is a valid L2 block）、`Flashblock System Invariants`。结合
`crates/rollup-boost-types/src/flashblocks.rs` 与 `crates/rollup-boost-types/src/payload.rs` 的
Rust 实现，验证 spec ↔ 代码一致性。同时把 WHI-30（`flashblocks-network-changes`）final 中关于
Azul payload 简化（移除 `new_account_balances` / `receipts`、保留 `access_list`）的结论作为外部
依赖输入引用，但不重复推导。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Builder 层 (`flashbots/op-rbuilder`) 配置与链间差异化

定位 `flashbots/op-rbuilder` 的 flashblocks 构建器实现：gas-limit heuristic `F` 值（spec 示例
F=10 下 max tx fits in flashblock 4，约 40% block gas limit）的取值在 Base 与 Unichain 实际部
署中的差异、交易排序（priority-fee-only vs MEV-aware）、bundle/PBS-style 接入差异、与 op-rbuilder
对应 Engine API client 的对接。需要验证两条链的 op-rbuilder 是否同 commit、CLI flag 与 env 配置
是否有差异，并量化「F 值变化对单 flashblock 内 tx 包含上界」的关系。该 item 是 producer 层向
builder 端的延伸。

- **Priority**: medium
- **Dependencies**: item-1, item-2

### item-4: Consumer 层三方实现深度对比

并列分析三类 flashblocks consumer 实现，逐一确认代码位置、能力矩阵与现状：

  - **(a) `base/base`**（原 `base/node-reth`）下 `crates/execution/flashblocks/`（`block_assembler.rs`、
    `cache.rs`、`config.rs`、`pending_blocks.rs`、`processor.rs`、`receipt_builder.rs`、`rpc/*`、
    `state_builder.rs`、`state.rs`、`subscription.rs`、`traits.rs`、`validation.rs`）+
    `crates/execution/flashblocks-node/` extension（`extension.rs`、`lib.rs`、`test_harness.rs`、
    `tests/flashblocks_rpc.rs`、`benches/pending_state.rs`）。覆盖 RPC：`eth_getBlockByNumber("pending")`、
    `eth_getTransactionReceipt`、`eth_getTransactionByHash`、`eth_getBalance/getTransactionCount/call/estimateGas/simulateV1`、
    `eth_getLogs`、`eth_getBlockTransactionCountByNumber("pending")`、`eth_sendRawTransactionSync`、
    `eth_subscribe("newFlashblocks" / "pendingLogs" / "newFlashblockTransactions")`；并验证
    `CanonicalBlockReconciler` 与 `ReorgDetector` 如何提供 multi-block flashblocks sync（即
    canonical head 滞后场景下保留多个 flashblock pending state）。
  - **(b) `paradigmxyz/reth` → `ethereum-optimism/optimism` 路径**：核实 reth 主仓在 v1.7.0
    (PR #17982 `feat(optimism): Add new reth-optimism-flashblocks crate`)、v1.9.4 仍保留
    `crates/optimism/flashblocks/`；commit `372802d06`（2026-02-06）`chore: remove op-reth from
    repository (#21532)` 将 op-reth（含 flashblocks 子模块）整体迁移至
    `ethereum-optimism/optimism` 的 `rust/op-reth/crates/flashblocks/`（`reth-optimism-flashblocks`
    v1.11.3，文件含 `cache.rs`、`consensus.rs`、`payload.rs`、`pending_state.rs`、`sequence.rs`、
    `service.rs`、`tx_cache.rs`、`validation.rs`、`worker.rs`、`ws/*`）。需独立验证 Flashbots
    官方文档（rollup-boost.flashbots.net/developers/flashblocks-rpc.html）仍指向 paradigmxyz/reth
    的现状是否合时、`--flashblocks-url` CLI 是否仍可用、`pending` tag overlay 的具体实现路径。
  - **(c) `danyalprout/reth-flashblocks`**：直接访问 GitHub 验证该 repo 当前存在性、是否已
    archived、最后提交时间、与上游 paradigmxyz/reth flashblocks crate 的差异；同步核实 danyalprout
    名下其他相关仓库（`flashblocks-demo`、`flashblocks-websocket-client`）的角色。若 repo 不存
    在，需在 final 中以 BLOCKED-style 注释明确「Orchestrator dispatch 引用的 repo 与实际公开仓库
    不一致」并给出当前推荐替代。
  - **(d) 独立 RPC provider 实现**：`ethereum-optimism/optimism` 的
    `rust/rollup-boost/crates/flashblocks-rpc/`（继承自 `flashbots/rollup-boost` 历史 crate；
    upstream 已于 commit `f6d1246`，2025-12-16，`Remove flashblocks-rpc crate (#456)` 删除）；
    分析其 binary `src/bin/main.rs`、cache、rpc、metrics、flashblocks 模块作为「轻量 thin overlay」
    与「base/base 重量级 extension」「reth 原生 crate」三种部署形态的取舍。

最终产出能力矩阵（行=实现，列=能力：multi-block sync / `eth_subscribe("newFlashblocks")` / cached
execution / pending RPC 全集覆盖度 / reorg detection / 上游化状态 / 第三方接入成本）。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: Flashblocks 传播协议演进 — WebSocket vs P2P

对比两条传播路径：

  - **WebSocket 广播路径**：`base/flashblocks-websocket-proxy`（Base 维护 canonical proxy）与
    `flashbots/rollup-boost/crates/websocket-proxy/`（`auth.rs`、`client.rs`、`rate_limit.rs`（约
    48KB，Redis 分布式限流）、`registry.rs`、`server.rs`、`subscriber.rs`、`metrics.rs`）的分工；
    fan-out 拓扑、单向广播设计、Brotli 压缩、认证策略；以及 `flashbots/rollup-boost/crates/rollup-boost/src/flashblocks/`
    （`launcher.rs`、`service.rs`、`inbound.rs`、`outbound.rs`、`args.rs`）的发布侧实现。
  - **P2P 路径**：精读 `flashbots/rollup-boost/specs/flashblocks_p2p.md`（193 行）：devp2p `flblk/1`
    子协议、`Authorization` 双签名结构（sequencer 签名 + builder 签名）、`Authorized Message`、
    `StartPublish` / `StopPublish` 消息、`Builder Public Key` 与 `Publisher` 概念、取消 rollup-boost
    同步验证并改由 Authorization 信任的设计 rationale、多 builder 协调。需要核实 P2P 代码在
    rollup-boost / reth / op-stack 各 repo 的实现进度（是否仅 spec 阶段、是否已有 PoC）。

产出两套架构对比图与决策树（在什么 HA 与延迟规模下，应选择哪一种传播路径）。

- **Priority**: high
- **Dependencies**: item-1, item-4

### item-6: HA 故障转移策略对比

汇总两种 HA 模型：

  - **WebSocket + op-conductor 模型**：参考 Base TDD（Notion: "TDD: Rollup Boost Integration with
    HA Sequencer"）描述的 active sequencer failover 流程；分析在该模型下 WebSocket 连接迁移、
    subscriber 重连、已发布 flashblocks 在新 sequencer 的丢失风险。
  - **P2P Authorization 模型**：基于 `specs/flashblocks_p2p.md` 的 `StartPublish` / `StopPublish`
    认证消息实现 publisher 角色平滑切换；新 sequencer 的 builder 通过 RLPx 已知上一 builder 发布
    内容，从而在 failover 后继续 build 已承诺的 flashblocks；逐项映射到 Base 与 Unichain 当前的
    HA 部署状态。

最终给出 failover 行为对比表（含 RTO、对消费者的可观察影响、对 `pending` tag 一致性的保证级别），
并标注各链当前 HA 方案的采用进度（已部署 / spec only / PoC / planned）。

- **Priority**: high
- **Dependencies**: item-1, item-5

### item-7: 协议演进方向 — Flashblocks v2 / Flashtestations / 压缩演进

跟踪 Flashblocks 协议的下一代议程：

  - **Flashblocks v2**：rollup-boost issue #321 的设计动议、对 `FlashblocksPayloadV1` 与
    `ExecutionPayloadFlashblockDeltaV1` 的结构变更建议（若有 spec draft 则纳入）、对 base/base
    与 op-reth flashblocks crate 的迁移影响。
  - **Flashtestations**：精读 `flashbots/rollup-boost/specs/flashtestations.md`（839 行）：TDX / TEE
    可信块构建规范，attestation 结构、与 Authorization 模型的耦合、是否要求 builder 运行在 TEE。
  - **压缩方案演进**：rollup-boost issue #455 描述的 json → zstd+dict → brotli → raw 演进，
    `crates/websocket-proxy/src/...` 中现行 Brotli 实现与各候选方案的吞吐 / CPU / 兼容性折中。
  - **flashblocks-rpc crate 弃用**：commit `f6d1246`（2025-12-16）`Remove flashblocks-rpc crate
    (#456)` 在 rollup-boost 主线移除该 crate；同时仍以 vendored 形式存在于 `ethereum-optimism/optimism`
    的 `rust/rollup-boost/crates/flashblocks-rpc/`；这一去重对外部 RPC provider 的迁移路径。

- **Priority**: medium
- **Dependencies**: item-2, item-4, item-5

### item-8: 跨链综合对比与 Mantle 引入门槛评估

综合 item-1 ~ item-7 的 finding，产出面向 Mantle 决策的对比与评估：

  - **Base vs Optimism/Unichain 差异化总览表**：按 producer 配置、builder 配置、consumer 实现、
    传播路径、HA 方案、演进路线六个维度的实际偏离点（commit-pinned，不允许「相同」断言不附证据）。
  - **Mantle 接入路径分析**：基于 consumer 三方对比的能力矩阵，给出 (a) 直接复用 `base/base`
    flashblocks-node extension 的成本与依赖、(b) 直接复用
    `ethereum-optimism/optimism/rust/op-reth/crates/flashblocks` 的成本与依赖、(c) 走轻量
    `flashblocks-rpc` thin overlay 的成本与依赖、(d) 自建 fork 的代价。每条路径量化代码改动量、
    上游跟随成本、HA / 演进风险敞口。
  - **决策框架**：给出 Mantle 团队在 Producer 路径（是否引入 rollup-boost）、Builder 路径（是否
    需要 op-rbuilder fork）、Consumer 路径（三选一）、Propagation 路径（WS 起步 vs 直接 P2P）等
    维度的推荐与备选。

该 item 是面向「audience = Mantle 团队」的综合结论层，所有断言必须能回溯到前述 item 的 evidence。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| code_location | 该层的核心代码位置：repo + commit + 文件路径 + 行号区间 + crate/binary 名称 + 大致 LoC；要求所有断言可点击复核 | all |
| data_structures_and_protocols | 该层涉及的关键数据结构、wire 格式、Engine API / JSON-RPC / devp2p 协议消息（含字段定义与示例） | all |
| chain_specific_diffs | Base 与 Optimism/Unichain（以及必要时第三方 OP Stack 链）在该层的实际差异：commit、CLI flag、env、配置值、patch；若无差异需明确以证据陈述「相同」 | all |
| interface_surface | 该层对外暴露的 API 表面：Engine API 方法、JSON-RPC 方法、devp2p 消息、CLI / config flag、metrics；以方法签名与请求/响应示例呈现 | all |
| evolution_and_status | 上游化 / fork / 废弃 / vendored / archived 状态；关键 commit 时间线（如 reth #21532、rollup-boost #456）；最后活跃度信号 | item-3, item-4, item-5, item-6, item-7 |
| evidence_sources | 主要证据源（spec 段落 + 锚点 URL、代码 permalink 含行号、issue/PR 链接、blog/Notion 链接、官方推荐文档片段）；要求最小化二手解读 | all |
| mantle_integration_implications | 对第三方 OP Stack 链（特别是 Mantle）引入该层的成本、依赖、风险与替代方案 | all |
| open_questions_and_risks | 该 item 在 outline 阶段未解答、Phase B 必须解答的事实型问题；以及发现的潜在风险（如「flashblocks-rpc 在 rollup-boost 移除后是否仍有维护」「P2P spec 是否仅止于设计」） | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | rollup-boost 共享 Producer 架构 + Base / Optimism 差异化组件全景图：sequencer → rollup-boost (Engine API multiplexer) → builder (op-rbuilder) / fallback EL → consumer (base-flashblocks-node / op-reth flashblocks / flashblocks-rpc) → WS proxy / P2P；标注 Base / Optimism 的配置差异点 | mermaid | item-1, item-3, item-8 |
| diag-2 | comparison | Consumer 层三方实现架构对比图：`base/base` flashblocks-node extension vs `ethereum-optimism/optimism/rust/op-reth/crates/flashblocks` vs `danyalprout/reth-flashblocks`（若仍存在）/ vendored flashblocks-rpc；标注 crate 边界、入口模块、是否支持 multi-block sync、是否提供完整 pending RPC | mermaid | item-4 |
| diag-3 | comparison | WebSocket vs P2P 传播方案架构对比图：WS 路径（rollup-boost websocket-proxy + base/flashblocks-websocket-proxy + Redis rate limit + Brotli + auth）vs P2P 路径（devp2p flblk/1 子协议 + Authorization 双签名 + StartPublish/StopPublish）；标注 single point of failure / fan-out 拓扑 / 信任模型 | mermaid | item-5 |
| diag-4 | flow | Flashblock 构建生命周期序列图：`engine_forkchoiceUpdatedV3` → op-rbuilder 启动构建 → 每 200ms 产生 FlashblocksPayloadV1（含 state root）→ rollup-boost outbound 发布 → consumer inbound 解码 → cache 更新 → `engine_getPayloadV5` 返回最终 payload；标注 F、FLASHBLOCKS_TIME、validity rules 检查点 | mermaid | item-2, item-3, item-5 |
| diag-5 | flow | HA 故障转移流程对比图：WebSocket 方案（active sequencer 失效 → op-conductor 切换 → 新 sequencer/rollup-boost/builder 启动 → WS 重连 / subscriber 迁移）vs P2P Authorization 方案（StopPublish → 切换 publisher → StartPublish → builder 通过 RLPx 已知历史 flashblock → 继续构建）；标注 RTO、对 pending 一致性的影响 | mermaid | item-6 |
| diag-6 | comparison | Consumer 层实现能力对比矩阵（mermaid 表格 / classDiagram 风格）：行=base/base、reth-optimism-flashblocks (op-reth/optimism repo)、flashblocks-rpc (vendored)、danyalprout/reth-flashblocks (待核实)；列=multi-block sync、reorg detection、`eth_subscribe("newFlashblocks")`、`eth_sendRawTransactionSync`、cached execution、上游化状态、最后活跃 commit | mermaid | item-4, item-8 |
| diag-7 | flow | Flashblocks RPC 数据流图：WebSocket 连接 → FlashblocksPayloadV1 入站 → SSZ + version-prefix 解码 → in-memory cache 更新（PendingBlocks / pending state）→ `pending` 请求路由（`eth_call` / `eth_getBalance` / `eth_getTransactionReceipt` 等）→ canonical block 到达后 reconciler 合并；以 base/base 与 op-reth flashblocks crate 双泳道展示差异 | mermaid | item-4 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | `flashbots/rollup-boost` specs：`flashblocks.md` / `flashblocks_p2p.md` / `flashtestations.md`（含具体小节锚点）；Flashbots 官方 RPC 文档 https://rollup-boost.flashbots.net/developers/flashblocks-rpc.html | 4 |
| src-2 | code_analysis | `flashbots/rollup-boost` `crates/rollup-boost/src/`（`server.rs` / `proxy.rs` / `selection.rs` / `flashblocks/*`）+ `crates/rollup-boost-types/src/` + `crates/websocket-proxy/src/` 的精确文件 + 行号引用 | 6 |
| src-3 | code_analysis | `base/base` `crates/execution/flashblocks/` + `crates/execution/flashblocks-node/` 的精确文件 + 行号引用，commit 与 `base-strategy-azul-overview` final 保持一致或更新 | 5 |
| src-4 | code_analysis | `ethereum-optimism/optimism` `rust/op-reth/crates/flashblocks/`（含 `service.rs` / `worker.rs` / `pending_state.rs` / `ws/*`）+ `rust/rollup-boost/crates/flashblocks-rpc/` 的精确文件 + 行号引用 | 4 |
| src-5 | code_analysis | `flashbots/op-rbuilder` 中 builder 主路径与 gas-limit heuristic 实现的精确文件 + 行号引用 | 2 |
| src-6 | governance_proposals | 关键 GitHub PR / issue：reth #17982（新增 flashblocks crate）、reth #21532（迁移 op-reth）、reth #17858（native op flashblocks support）、rollup-boost #321（v2 议程）、rollup-boost #455（压缩演进）、rollup-boost #456（移除 flashblocks-rpc crate） | 4 |
| src-7 | expert_commentary | Flashbots 博客 "Introducing Rollup-Boost - Launching on Unichain"、RFD-1 Notion、Base TDD "Rollup Boost Integration with HA Sequencer"、`base/flashblocks-websocket-proxy` README | 3 |
| src-8 | cross_reference | 前序 `flashblocks-network-changes` (WHI-30) final.md（用作 Azul payload 简化输入，不重复推导） | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
