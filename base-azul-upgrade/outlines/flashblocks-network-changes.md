---
topic: "Flashblocks 优化与网络协议变更解析"
project_slug: base-azul-upgrade
topic_slug: flashblocks-network-changes
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: base-azul-upgrade/outlines/flashblocks-network-changes.md
  draft: base-azul-upgrade/research-sections/flashblocks-network-changes/drafts/round-{n}.md
  final: base-azul-upgrade/research-sections/flashblocks-network-changes/final.md
  index: base-azul-upgrade/research-sections/_index.md

scope: |
  系统解析 Base Azul 在「Flashblocks WebSocket payload 简化 + 节点间/Engine 间网络协议升级」这一工作线
  上的所有变更：(a) FlashblocksMetadata 移除 `new_account_balances` 与 `receipts`、保留但不再填充
  `access_list`；(b) EIP-7642 (eth/69) 修改 Status 消息字段、删除 Receipts 中的 Bloom、新增
  BlockRangeUpdate (0x11)；(c) Engine API 升级至 V5 envelope + V4 payload 形态
  （`engine_forkchoiceUpdatedV3`、`engine_getPayloadV5`、`engine_newPayloadV4`，blob 输入与
  `executionRequests` 必须为空）；(d) EIP-7910 引入 `eth_config` JSON-RPC 暴露当前/下一个/最后一个 fork
  的链配置参数。每一项变更都需结合 Base Spec、相关 EIP 与 `base/base` 实际代码（commit
  `84155fef0c50f7799e804c757e078306848f032e`，与 `base-strategy-azul-overview` final 保持一致）做交叉
  校验，并明确 Base 在通用 Ethereum 之上的 specific 行为（如 blobSchedule 取零、executionRequests 必须
  为空、access_list 保留但不填充）。

  本研究**不**重复 `osaka-evm-changes` 已覆盖的执行层 EIP（如 EIP-7823/7825/7883/7939/7951）的语义层
  解读、**不**进入 `multiproof-architecture` 的证明系统范畴、也**不**回顾 Flashblocks 本身的历史与
  非-Azul 时期设计——仅聚焦 Azul 在 payload/网络/Engine/RPC 表面引入的变更。

audience: |
  Base / OP Stack 生态研究者、Multica 研究 squad 下游 Research Agent（特别是 `mantle-impact-assessment`
  的影响评估者）、Flashblocks 数据消费者（Flashbots rollup-boost、`base/flashblocks-websocket-proxy`、
  RPC 服务商、MEV searcher、indexer）、Engine API 客户端集成方、节点运维与 dev tooling 团队。
  读者熟悉 Ethereum Engine API 与 wire protocol 基本概念，但不一定了解 Azul 的具体 payload 变更。

expected_output: |
  - Flashblocks payload 变更前后字段级对比（含示例 JSON、Receipts/AccountBalances 字段的下游用途）
  - EIP-7642 (eth/69) 升级技术解读：Status 字段差异、Receipts 编码差异、BlockRangeUpdate 新消息、
    与 eth/68 的双版本共存策略
  - Engine API V5 envelope + V4 payload 调用流程文档：从 sequencer 出块到 verifier 导入的完整生命周期，
    blob 与 executionRequests 必须为空的约束在 Base 上的具体含义
  - EIP-7910 `eth_config` RPC 返回值结构分析：每个字段的语义、Base 上 blobSchedule 取零的原因、
    precompiles/systemContracts 在 Azul 阶段的具体集合
  - `base/base` 关键代码段（结构体定义、消息编解码、Engine API handler、RPC handler）的位置引用与注释
    解析，commit SHA 与行号精确到位
  - 至少 3 张 Mermaid 图：Flashblocks payload 字段前后对比、Engine API V5 调用序列、
    eth/68 vs eth/69 握手对比；可选第 4 张 eth_config 响应结构树
  - Evidence: 引用 ≥3 条 Base/EIP 官方文档、≥4 个 base/base 代码位置（commit `84155fef…`）、
    ≥2 处 ethereum-optimism/optimism 上游对比、≥2 篇行业/官方博客或论坛讨论

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-17T03:30:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-17T03:30:00Z"
---

# Research Outline: Flashblocks 优化与网络协议变更解析

## Items

### item-1: Flashblocks WebSocket Payload Simplification

调查 Azul 对 Flashblocks WebSocket 传输的 `FlashblocksMetadata` payload 所做的结构性简化：明确移除
`new_account_balances`（地址→余额映射）与 `receipts`（交易哈希→Receipt 映射），保留 `access_list`
字段但在 Azul 阶段不填充。需要梳理 Azul 前后 payload 的完整字段集（结构体定义、JSON 示例）、
官方与社区对「为未来性能增强预留空间」「为 Block Access List 铺路」的叙事，以及对 Flashbots
rollup-boost、`base/flashblocks-websocket-proxy`、应用层 `pending` 标签 RPC 调用、indexer/MEV searcher
等不同消费者的差异化影响。明确「应用应通过 `eth_getTransactionReceipt(pending)` 而非 WebSocket
raw payload 获取 receipts」这一推荐路径。

- **Priority**: high
- **Dependencies**: none

### item-2: EIP-7642 (eth/69) Wire Protocol Upgrade

解析 Azul 同步采用的 EIP-7642 (eth/69)：(a) Status 消息从 `[version, networkid, td, blockhash, genesis,
forkid]` 演化为 `[version, networkid, genesis, forkid, earliestBlock, latestBlock, latestBlockHash]`，
特别是移除 `td` (TotalDifficulty) 这一 post-merge 已废弃字段的原因；(b) Receipt 编码从含 `Bloom` 改为
`[tx-type, post-state-or-status, cumulative-gas, logs]` 的扁平结构，量化 bloom 移除带来的 ~530GB
带宽节约；(c) 新增 `BlockRangeUpdate (0x11)` 消息，每 32 块 epoch 至多广播一次的设计；(d) eth/68 与
eth/69 的双版本共存与节点兼容策略。同时区分「以太坊主网 eth/69 通用语义」与「Base/OP Stack
在自有 chain ID 与 forkid 下的应用细节」。

- **Priority**: high
- **Dependencies**: none

### item-3: Engine API V5 Envelope + V4 Payload Lifecycle

解析 Azul 引入的 Engine API 三方法组合：(a) `engine_forkchoiceUpdatedV3` 用于 sequencer 出块启动与
forkchoice 同步；(b) `engine_getPayloadV5` 返回 V5 envelope，但内部 execution payload 仍为 V4-shaped；
(c) `engine_newPayloadV4` 用于 payload 导入；(d) Base 特定的硬性约束——`expectedBlobVersionedHashes`、
`blobsBundle` 必须为空数组，`engine_newPayloadV4` 的 `executionRequests` 必须为空数组。需要厘清
「V5 envelope」与「V4 payload」的具体差异（envelope 含哪些 wrapper 字段、payload 内部字段是否一致），
并解释「envelope bump 但 payload 保留 V4」的设计折中。给出从 sequencer 出块到 verifier/follow-only
节点导入的完整调用时序。

- **Priority**: high
- **Dependencies**: none

### item-4: EIP-7910 `eth_config` JSON-RPC and Base-Specific Behavior

解析 Azul 暴露的 `eth_config` RPC 方法：(a) 响应包含 `current` / `next` / `last` 三个 fork
配置对象，每个对象必含 `activationTime`、`chainId`、`forkId` (EIP-6122 hash)、`blobSchedule`
（`baseFeeUpdateFraction`/`max`/`target`）、`precompiles`（名称→20-byte 地址映射）、`systemContracts`
（名称→地址映射）；(b) Base 特定行为——`blobSchedule` 三字段均为零（Base 不支持原生 blob 交易，
因此不能宣称合成的以太坊 blob schedule 默认值）；(c) `precompiles` 反映 Azul 阶段活跃的 EVM
集合（标准以太坊 Cancun/Prague/Osaka 集合 + Base-active additions，包括 EIP-7951 secp256r1 重新计价
后的 P256VERIFY）；(d) `systemContracts` 仅含 EIP-7910 schema 规定的合约（如 `BEACON_ROOTS_ADDRESS`、
`HISTORY_STORAGE_ADDRESS`），不暴露 Base 私有的 predeploy。同时讨论该 RPC 对预激活 fork 校验、
节点配置漂移检测、跨客户端 CI 校验等开发者工具链场景的意义。

- **Priority**: high
- **Dependencies**: none

### item-5: `base/base` Code Implementation Mapping

定位 `base/base` 仓库（commit `84155fef0c50f7799e804c757e078306848f032e`，与
`base-strategy-azul-overview` final 一致）中前四个 item 的具体代码实现位置：FlashblocksMetadata
结构体定义与序列化路径、`StatusMessage` 与 `Receipt` 在 eth/69 下的编解码、`engine_*` RPC handler
的方法分派与空数组校验、`eth_config` handler 的 fork 配置组装。每处代码位置需要给出文件路径
与行号区间，并对照 `ethereum-optimism/optimism`（commit `d905be1e03df0e30112dc382d3b9b74d0d65aaa3`，
同样与 overview final 一致）的上游等价位置，标注 Base 的偏离点。当代码位置与 spec 文本不一致时
明确记录差异并触发 BLOCKED/Major finding。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4

### item-6: Compatibility, Downstream Consumer Impact, and Migration Sequence

汇总上述变更对外部生态的影响：(a) Flashblocks 原始 WebSocket 消费者（rollup-boost、proxy、自建
listener、MEV searcher、indexer）需要的具体迁移动作；(b) eth/68-only peer 在 Azul 之后能否继续与
Base 节点握手与同步；(c) Engine API V4-only CL 客户端的兼容情况；(d) dev tooling（钱包、SDK、
explorer、CI 校验脚本）读取 `eth_config` 的最佳实践与 fallback；(e) Sepolia（自 2026-04-20 18:00 UTC
激活，截至研究撰写日已运行 27 天，至 commit `84155fef…` 当日）与 mainnet 计划（code 端
`1_779_991_200` / 2026-05-28 18:00 UTC，但公开 spec 仍标 TBD——遵循 `base-strategy-azul-overview`
final.md 的双口径表述）的 rollout 时序，以及部分迁移期的风险与缓解。该 item 是面向下游 Mantle 影响
评估等课题的接口层。

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| design_motivation | 该变更的公开/可推断动机（节省带宽、为 BAL 让路、Osaka 对齐、移除 post-merge legacy 等），区分官方叙事与研究者推断 | all |
| spec_reference | 精确指向 Base Spec 页面段落与/或 EIP 编号 + 章节锚（含 URL）；要求可独立点击复核 | all |
| before_after_comparison | Azul 前 / Azul 后的结构/消息/RPC 形态对比，给出最小可复现的 JSON 或字节序列片段 | all |
| base_code_location | 在 `base/base` @ `84155fef0c50f7799e804c757e078306848f032e` 中的文件路径 + 行号区间 + 函数/结构体名 | all |
| upstream_reference | 在 `ethereum-optimism/optimism` @ `d905be1e03df0e30112dc382d3b9b74d0d65aaa3` 或 reth 主线中的对应位置（若适用），并标注 Base 是 fork、port 还是 deviate | item-1, item-2, item-3, item-4, item-5 |
| base_specific_behavior | Base 相对通用 Ethereum 的偏离点（如 blobSchedule 全零、executionRequests 必须为空、access_list 保留但不填充、单客户端栈） | all |
| compatibility_impact | 对 eth/68 peer、V4-only Engine 客户端、非-Azul Flashblocks 消费者的握手/同步/导入兼容性 | all |
| consumer_impact | 具体被影响的下游产品/集成方（rollup-boost、flashblocks-websocket-proxy、Alchemy/QuickNode/GetBlock、钱包、indexer、MEV searcher、CI 校验脚本） | all |
| key_open_questions | 该 item 在 outline 阶段仍未解答、Phase B 必须解答的事实型问题清单（如「access_list 何时开始填充」「BlockRangeUpdate 在 Base 的实际广播节奏」） | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Flashblocks payload 在 Azul 前后字段级对比（保留 / 移除 / 保留但不填充 三类色块），含 `block_number` / `new_account_balances` / `receipts` / `access_list` 的状态 | mermaid | item-1 |
| diag-2 | flow | Engine API V5 envelope + V4 payload 调用序列：从 sequencer `engine_forkchoiceUpdatedV3` 触发出块 → `engine_getPayloadV5` 取回 envelope → verifier `engine_newPayloadV4` 导入；标注 blob 与 executionRequests 必须为空的约束位置 | mermaid | item-3 |
| diag-3 | comparison | eth/68 vs eth/69 握手序列对比（Status 字段、Receipt 编码、新增 BlockRangeUpdate）；建议为 sequenceDiagram 双泳道 | mermaid | item-2 |
| diag-4 | hierarchy | `eth_config` 响应结构树：current/next/last → activationTime/chainId/forkId/blobSchedule/precompiles/systemContracts，并标注 Base 上的 blobSchedule=0、precompiles 包含 P256VERIFY 等关键节点 | mermaid | item-4 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | Base Spec `upgrades/azul/exec-engine` 页面、`upgrades/azul/overview` 页面、EIP-7642、EIP-7910，含具体小节锚点 | 4 |
| src-2 | code_analysis | `base/base` @ `84155fef0c50f7799e804c757e078306848f032e` 中 Flashblocks 结构体、eth/69 编解码、Engine API handler、`eth_config` handler 的精确位置 | 4 |
| src-3 | code_analysis | `ethereum-optimism/optimism` @ `d905be1e03df0e30112dc382d3b9b74d0d65aaa3` 或 paradigm reth 主线中对应位置，用于标注 Base 的偏离 | 2 |
| src-4 | expert_commentary | base.dev 官方博客（如 "Introducing Base Azul"、"Flashblocks Deep Dive"）、`base/flashblocks-websocket-proxy` README、Flashbots rollup-boost 仓库相关说明 | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
