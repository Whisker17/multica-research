---
topic: "Sequencer Pipeline 与共识层优化分析：Base base-consensus vs Mantle op-node / kona"
project_slug: base-perf-analysis
topic_slug: sequencer-consensus-pipeline-perf
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: base-perf-analysis/outlines/sequencer-consensus-pipeline-perf.md
  draft: base-perf-analysis/research-sections/sequencer-consensus-pipeline-perf/drafts/round-{n}.md
  final: base-perf-analysis/research-sections/sequencer-consensus-pipeline-perf/final.md
  index: base-perf-analysis/research-sections/_index.md

scope: |
  对比 Base 共识节点（`base/base` → `crates/consensus`，Rust，基于 op-rs/kona 的 actor 模型实现）
  与 Mantle 共识节点（`mantlenetworkio/mantle-v2` → `op-node`，Go，从 ethereum-optimism/optimism
  分叉而来；`mantle-xyz/kona` 仅作为 cannon 故障证明的 kona-client 使用）在 **sequencer pipeline**
  设计上的性能差异，覆盖：
  (1) 节点服务的进程/任务拓扑：Base actor-mpsc 流水线 vs op-node 单进程事件循环；
  (2) Sequencer 主循环的 build / seal / gossip / insert 流水线阶段拆解，及阶段之间是否解耦/并行；
  (3) Derivation pipeline 的并行度：是否与 sequencer 主循环、与执行层 commit 同时运行；
  (4) Engine API 调用模式：FCU、newPayload、getPayload 的版本（V2/V3/V4）、调用频率、批量化、
      同步/异步、超时与回退；
  (5) 共识层在单 block time budget（~2s for Base/Mantle）中的耗时占比，识别是否构成 TPS 瓶颈；
  (6) `mantle-xyz/kona` fork 的实际作用域（FP-only vs online consensus），明确是否可被替换为
      在线 sequencer 实现，及其与 `op-rs/kona` 主线、Base 的 base-consensus 的演进差距；
  (7) Pipeline 并行化 / Engine API 调用模式 / sequencer 主循环重构对 Mantle TPS 的可量化提升空间
      与对应改造路径。

audience: |
  Mantle / Base 协议工程师与 sequencer / consensus team；
  Multica 研究 squad 内部下游 Research Agent（perf-gap-analysis-recommendations、
  batcher-sequencer-backpressure、execution-layer-reth-fork-comparison 的消费侧）；
  OP Stack 生态中评估"是否把 op-node 替换为 kona-node / base-consensus 风格的 Rust actor
  实现"的运营者；项目内部决策者评估"共识层重构"作为 TPS 提升的可行路径。
  读者熟悉 OP Stack Engine API（forkchoiceUpdated / newPayload / getPayload）、derivation
  pipeline 概念、actor / event-loop 编程模型；不必预先了解 base-consensus 或 mantle-v2
  op-node 的具体细节。

expected_output: |
  - Base base-consensus（Rust actor 模型）与 Mantle op-node（Go 单进程 driver/事件循环）的
    架构对比矩阵（按 actor / 模块 / 关键 channel 列出）
  - Sequencer 主循环阶段拆解：build_start → build_seal → gossip → insert → consolidate 的
    时序图，每阶段标注调用者、是否阻塞主循环、典型耗时数量级（measured / reported / inferred）
  - Engine API 调用模式对比表：每个端点（FCU/newPayload/getPayload）的版本、调用方、目标
    actor、是否在主循环内同步等待、超时策略
  - Derivation pipeline 并行度对比：与 sequencer build、与 engine commit 是否共享线程 /
    channel / lock；max in-flight 步骤数
  - 共识层在 ~2s block time budget 中的耗时占比量化估算（含 sealing duration 常数：
    Base 早期预算 vs Mantle 50 ms hardcoded）
  - `mantle-xyz/kona` fork 作用域分析：明确其等同 `op-rs/kona` 的 kona-client（fault proof
    binary）而非 kona-node（online consensus），以及 mantle-v2 中 `kona/` 目录与 op-challenger
    cannon-kona 配置的关系
  - Pipeline 并行化 / 异步 Engine API 改造对 Mantle TPS 的量化提升估算（按 non-additive /
    upper-bound 护栏标注）
  - 至少 3 张 Mermaid 图：架构对比、sequencer build/seal pipeline 时序图、Engine API 调用
    序列图（可叠加 derivation pipeline 并行度对比为第 4 张）
  - 针对 Mantle 的至少 3 条改进建议（pipeline 重构、异步 FCU、空块抑制策略、kona-node
    迁移可行性等），标注预期 TPS 提升、改造成本与风险等级

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-20T06:35:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-20T06:35:00Z"

attribution_tiers:
  description: |
    所有共识层 / sequencer pipeline / Engine API 相关的代码、改动、配置与 TPS 影响声明，必须
    显式标注其归属层级（Tier A–E）。无法明确归属的声明必须标记为 `[UNATTRIBUTED]` 并在 Patch
    Log 中记录待补证据。归属层级与 execution-layer-reth-fork-comparison 保持一致语义，但
    source_repo 适配于共识层。
  tiers:
    - id: A
      name: 上游 op-rs/kona（Rust 共识节点基线）
      source_repo: op-rs/kona
      note: 中立 baseline；同时供 Base base-consensus 与 Mantle kona-client 比较。kona-node
        作为 online consensus 实现，kona-client 作为 FP binary。
    - id: B
      name: 上游 ethereum-optimism/optimism op-node（Go 共识节点基线）
      source_repo: ethereum-optimism/optimism (monorepo) `op-node/`
      note: Mantle op-node 直接基于此 fork；Base base-consensus 在 actor 拓扑、事件模型上
        刻意偏离此基线。声明任何 "Mantle 选择" 必须先验证是否为 OP 继承行为，否则误归。
    - id: C
      name: Base overlay
      source_repo: base/base → crates/consensus
      note: Base 在 op-rs/kona 之上的 actor 拓扑 / channel capacity / engine task queue
        增量改动。Base 的"重写"语义需逐 actor 验证。
    - id: D
      name: Mantle overlay (op-node)
      source_repo: mantlenetworkio/mantle-v2 → op-node/
      note: Mantle 在 OP op-node 之上的增量改动（MetaTx、L1 cost、arsia 升级、blob、operator-fee 等）
    - id: E
      name: Mantle overlay (kona fork)
      source_repo: mantle-xyz/kona (branches: arsia*, audit-fix, eigen_verify, blob_test, ...)
      note: Mantle 在 op-rs/kona 之上的 fork，**作用域仅限 kona-client（cannon 故障证明
        prestate）**，不参与在线 sequencer。任何把 Tier E 的代码当作"Mantle 在线共识层"
        的声明都必须 `[MISATTRIBUTED]` 并在 Patch Log 中记录。
---

# Research Outline: Sequencer Pipeline 与共识层优化分析

## Items

### item-1: 共识节点服务拓扑与进程/任务模型对比

逐 actor / 逐模块对比两边的共识节点服务架构：Base `base-consensus-node`（`base/base` →
`crates/consensus/service`）采用严格 actor 模型，由 `RollupNodeBuilder` 构造五大 actor
（Engine、Derivation、Network、L1Watcher、Sequencer，以及可选的 RPC），actor 间仅通过
`tokio::sync::mpsc`（多为 capacity=1024）与 `tokio::sync::watch` 通信，单一 `CancellationToken`
统一管理生命周期；Mantle `op-node`（`mantle-v2/op-node`）继承自 OP optimism monorepo 的 Go
实现，使用 `event` bus 与 `rollup/driver`、`rollup/engine`、`rollup/sequencing`、`rollup/derive`
等子包，通过事件订阅而非显式 channel 解耦。需要给出 actor / module 一一对应表，标注哪些
是 Base 自有创新（Tier C）、哪些直接继承自 op-rs/kona（Tier A）、哪些来自 OP op-node（Tier B）、
哪些是 Mantle 在 op-node 之上的增量（Tier D）。

**强制要求**：每条架构差异声明必须显式标注 Tier，并区分"语言/runtime 差异"（Rust+tokio vs Go
+goroutine）与"实际并行度差异"。仅 runtime 不同不一定意味着 TPS 差异；需有热路径数据支撑。

- **Priority**: high
- **Dependencies**: none
- **Required investigation_fields**:
  - `attribution_tier`：每条声明标注 A/B/C/D/E
  - `actor_or_module_map`：Base actor ↔ op-node module 的一一对应（含未对应项）
  - `channel_or_eventbus_capacity`：Base 各 mpsc/watch 的 capacity（service README 已给出
    精确数字：mpsc=1024、gossip_payload=256、signer=16、p2p_rpc=1024、admin_rpc=1024、
    L1WatcherQueries=1024、EngineRpc=concurrent=16 semaphore、L1WatcherQueryProcessor
    concurrent=32）vs op-node 各 event 订阅者数量
  - `cancellation_model`：单 token cancel 链 vs context.Context tree

### item-2: Sequencer 主循环 build / seal / gossip / insert 流水线阶段

精确还原两边 sequencer 主循环：

Base sequencer（`base/base` → `crates/consensus/service/src/actors/sequencer/`）：`tokio::select!`
五个分支（按优先级）—— cancellation、admin queries、`PayloadSealer::step()`、build ticker
（`block_time` 默认 2 s，wall-clock 对齐，`UNIX_EPOCH + (sealed_block_timestamp + block_time)
* 1s - last_seal_duration` 调度）、initial reset retries。`PayloadSealer` 三阶段（Sealed →
Committed → Gossiped）：分别调用 `conductor.commit_unsafe_payload()`、
`gossip_client.schedule_execution_payload_gossip()`（fire-and-forget）、
`engine_client.insert_unsafe_payload()`（fire-and-forget `ProcessUnsafeL2BlockRequest`）。
`PayloadBuilder::build_on(parent)` 调用 `L1OriginSelector` → `StatefulAttributesBuilder::
prepare_payload_attributes()` → `PoolActivation` 检查 → `start_build_block` 发送 `BuildRequest`
返回 `PayloadId`。

Mantle op-node sequencer（`mantle-v2/op-node/rollup/sequencing/sequencer.go`）：`sealingDuration
= 50 ms` 常量；`nextAction` / `nextActionOK` 时间触发；`onBuildStarted` 在 `BuildStartedEvent`
后计算 `payloadTime.Add(-sealingDuration)`；事件驱动而非 select-loop；行为通过 `engine`
package 的 build_start / build_seal / build_sealed / payload_process / payload_success 事件
串接。

需要：(a) 给出两边主循环 ASCII / Mermaid 时序图；(b) 量化每阶段是否阻塞主循环、是否 fire-and-
forget；(c) 比较 `sealingDuration` 常数与 Base 早期 schedule 的 wall-clock 留量；(d) 标注哪
些阶段在 Base 与 engine actor 解耦、在 Mantle 仍同进程内同步阻塞。

- **Priority**: high
- **Dependencies**: item-1
- **Required investigation_fields**:
  - `pipeline_stages`：每个阶段名、调用者、被调者、是否同步阻塞、典型耗时
  - `attribution_tier`：每个阶段对应 Tier（A/B/C/D/E）
  - `wall_clock_alignment`：tick 调度算法（next_tick 公式）
  - `decoupling_class`：`fire_and_forget` | `awaited` | `oneshot_channel` | `event_bus`

### item-3: Engine API 调用模式与版本兼容性

逐端点对比 `engine_forkchoiceUpdatedV{2,3}`、`engine_newPayloadV{2,3,4}`、`engine_getPayloadV{2,3,4}`
的调用模式：

- 端点版本与硬分叉激活（Base README 列出 V2/V3/V4 自动选择，按 Bedrock/Canyon/Delta/Ecotone/
  Isthmus 激活时间；Mantle op-node 通过 `chain_spec`/`mantle_chain_spec` 在 Arsia 升级前后选择）
- 调用方与目标 actor / module：Base 的 `EngineActorRequest` 五类（BuildRequest、GetPayload、
  Seal、ProcessUnsafeL2Block、ProcessSafeL2Signal、Reset），由 sequencer / network / derivation
  / RPC actor 通过 mpsc(1024) 入队；Mantle 的 EngineController 直接持有 `engine.Engine` 接口
  （`ForkchoiceUpdate`/`NewPayload`/`GetPayload`），通过 event bus 触发
- 主循环内是否同步等待 RPC 返回：Base 处理任务在 engine processing task 上排队后由 oneshot
  返回（fire-and-forget 路径不等待），sequencer 主循环可继续；Mantle EngineController 调用是
  阻塞的（go func RPC over HTTP/JWT），由事件触发但完成是同步等待
- 错误分级与重试：Base engine 的 Critical / Reset / Flush / Temporary 四级错误；op-node
  `checkNewPayloadStatus` / `checkForkchoiceUpdatedStatus` 的 VALID / INVALID / SYNCING 处理
- 调用频率：每次 sequencer tick 触发 FCU+getPayload；新 unsafe block 触发 newPayload+FCU；
  derivation 完成一轮触发 ProcessSafeL2Signal（Base）/ ConsolidateInput（op-node 旧叫法）

**强制要求**：所有"调用延迟"声明必须标 measurement_scenario（block gas limit / tx mix /
hardware / sync mode），并按 non-additive 原则；调用次数声明必须区分 `per_block` / `per_l1_epoch` /
`per_safe_head_update`。

- **Priority**: high
- **Dependencies**: item-1, item-2
- **Required investigation_fields**:
  - `endpoint_versions`：每端点支持的 V2/V3/V4 列表
  - `caller_pattern`：mpsc-queue / direct-call / event-bus
  - `sync_or_async`：`sync_await` | `fire_and_forget` | `oneshot_then_resume`
  - `frequency_class`：per_block | per_l1_epoch | per_safe_head | per_finalized | per_reset
  - `attribution_tier`：A/B/C/D/E
  - `denominator`：ms_per_call | calls_per_block | retries_per_failure

### item-4: Derivation Pipeline 并行度与与 Sequencer / Engine 的耦合

Base derivation actor（`base/base` → `crates/consensus/service/src/actors/derivation/`）：六状态
机（AwaitingELSyncCompletion → Deriving → AwaitingSafeHeadConfirmation → AwaitingL1Data →
AwaitingSignal …），`pipeline.step()` 循环，`PreparedAttributes` 触发 ProcessSafeL2Signal；
delegation 变体 `DelegateDerivationActor`（4 s 轮询 sync-status）与 `DelegateL2DerivationActor`
（FollowNode 用，2 s 轮询）。Engine 通过 QueuedEngineDerivationClient 回调 `notify_sync_completed`
/ `send_new_engine_safe_head`，触发状态机推进。**关键：derivation actor 与 sequencer actor 完
全解耦，跑在不同 tokio task，仅通过 engine actor mpsc 交互。**

Mantle op-node derivation（`mantle-v2/op-node/rollup/derive/`）：StatefulAttributesBuilder、
ChannelBank、BatchQueue、SpanBatch 等 stage，由 `rollup/driver` 的 `step_scheduling_deriver.go`
统一调度；`sync_deriver.go` 处理同步阶段。**与 sequencing / engine 同进程，跑在同一 op-node
event loop**。BatchMux（`batch_mux.go`）做多态分发；Mantle 在 attributes_queue 注入 MetaTx
（gas payer 分离）与 Arsia 升级特殊事务。

需要量化：(a) 两边 derivation step 的最大 in-flight 数；(b) 与 sequencer build 是否共享线程
/ scheduler；(c) 与 engine FCU 是否串行；(d) 当 L1 epoch 推进时，derivation 是否会延迟
sequencer 出块。

- **Priority**: high
- **Dependencies**: item-1, item-2
- **Required investigation_fields**:
  - `derivation_state_count`：状态机/阶段数
  - `coupling_to_sequencer`：`independent_task` | `same_event_loop` | `shared_lock`
  - `coupling_to_engine`：`mpsc_request` | `direct_call` | `event_emit`
  - `attribution_tier`：A/B/C/D/E

### item-5: `mantle-xyz/kona` fork 实际作用域与可替换性分析

**澄清前提**：通过 `mantle-v2/kona/version.json`（version 1.2.4、prestateHash、interopPrestateHash）
与 `mantle-v2/op-challenger/flags/flags.go`（`cannon-kona-server` / `cannon-kona-prestate` /
`cannon-kona-l2-custom`）可证实：Mantle 仓库下的 `kona/` 目录与 `mantle-xyz/kona` fork **仅作
为 cannon 故障证明的 kona-client prestate** 使用，不在在线 sequencer 链路上。Mantle 在线共识
仍是 `mantle-v2/op-node`（Go）。

本 item 需要：
1. 列出 `mantle-xyz/kona` 现有分支（archive、arsia、arsia-oracle、arsia_v122、audit、audit-fix、
   blob_test、bugfix_eigen、bvm_eth、dev、dev_sync_upstream、eigen_verify、feature/operator-fee、
   fix_timeout 等），分类为：(a) 与上游 `op-rs/kona` 的版本同步 / 审计修复；(b) Mantle 特有
   feature（operator-fee、eigen DA、MNT blob、arsia 升级）；(c) bug fix 与 db 修复
2. 量化 mantle-xyz/kona 相对 op-rs/kona 主线的滞后量（HEAD commit / 关键 PR 缺口 / 是否对齐
   v1.x / v2.x）
3. 判断"把 Mantle 在线 sequencer 从 op-node 迁移到 kona-node"的可行性：需要同步哪些上游
   feature？Tier E 已有的改动有多少可复用？需要额外移植 Tier D 的哪些行为（MetaTx、L1 cost、
   token abstraction）？
4. 估算迁移成本（人月、风险等级、是否需要 hardfork）与预期收益（与 Base 类似的 actor 并行
   红利、Engine API decoupling、空块抑制等）

**强制要求**：任何"Mantle 在用 kona"的声明都必须标注 sub-scope（kona-client FP-only / kona-node
online / 完整迁移）。混淆者标 `[MISATTRIBUTED]`。

- **Priority**: high
- **Dependencies**: item-1
- **Required investigation_fields**:
  - `kona_fork_scope`：`fp_client_only` | `partial_node` | `full_node`（mantle-xyz/kona 当前 = fp_client_only）
  - `branch_purpose`：archive / audit / feature / bugfix / version_sync
  - `upstream_lag`：相对 op-rs/kona main / 最新 release tag 的 commit 数 / 关键 PR 缺口
  - `migration_cost_estimate`：人月、风险等级、依赖项

### item-6: 共识层在 block time budget 中的耗时占比与瓶颈识别

承接 item-2、item-3、item-4 的数据，在 Base ~2 s block time / Mantle ~2 s block time 预算下，
估算共识层（不含 EL 执行本身）的总耗时占比：

- Sequencer build 路径：origin selection + attributes building + start_build_block + FCU 排队
- Sequencer seal 路径：getPayload + conductor commit + gossip + insert（newPayload+FCU）
- Derivation 一轮 step（如果在该 tick 触发）
- L1 watcher 在该窗口内的影响（4 s head poll、log fetch 重试）

承认主网在线测量难度，回退到代码静态分析 + 公开 benchmark + 推断，并显式标注证据等级
（measured / reported / inferred）。

**测量方法学护栏（强制，与 execution-layer outline 同步）**：

1. **非加性原则**：所有共识层耗时百分比默认不可相加。只有同一 block time budget + 同一 tx mix
   + 同一硬件下测得、且作用于正交路径时才允许合成；否则报告为独立场景上界。
2. **同一基准前提**：跨 Base/Mantle 对比必须声明 block time、L1 epoch boundary 距离、tx mix、
   硬件 spec。
3. **分母标签**：每条声明用单一分母 — `ms/block`、`% of block time budget`、`calls/block`、
   `p99_latency`，不混用。
4. **Tier 归属**：A/B/C/D/E 同步。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4
- **Required investigation_fields**:
  - `denominator`：`ms/block` | `% of block time` | `calls/block` | `p50/p99 latency`
  - `measurement_scenario`：block_time / tx_mix / hardware / l1_epoch_position
  - `evidence_grade`：`measured` | `reported` | `inferred`
  - `additivity_class`：`additive_within_scenario` | `non_additive` | `upper_bound_only`
  - `attribution_tier`：A/B/C/D/E

### item-7: Pipeline 并行化与异步 Engine API 改造对 TPS 的影响估算

基于 item-2 / item-3 / item-4 / item-6 的差距，对"如果 Mantle 引入 Base 风格的 actor 解耦 +
fire-and-forget engine 调用"的潜在 TPS 提升做量化推断：

- 把 newPayload+FCU 从 sequencer 主循环同步等待改为 oneshot 异步（参考 Base
  `ProcessUnsafeL2BlockRequest` 路径）能释放多少 ms/block
- 把 derivation 从 op-node 同进程事件循环拆出独立 task / process 能释放多少
- 把 sequencer build / seal 两阶段从 50 ms `sealingDuration` 常量改为 wall-clock-aligned
  动态 schedule（参考 Base 的 `next_seal_duration` 反馈）能避免多少 dead time
- 空块抑制（参考 Base 的 PoolActivation + builder-side 持续构建）能把 effective gas/s 提多少

每条估算严格遵循 item-6 的护栏。明确"理论 TPS"与"有效 TPS"区别，与 sibling 主题
block-builder-flashblocks-throughput 的 effective TPS 分析对齐（不重复计算同一收益）。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-6
- **Required investigation_fields**:
  - `improvement_lever`：异步 FCU / derivation 解耦 / 动态 schedule / 空块抑制 / kona-node 迁移
  - `expected_gain`：ms/block 或 % of block time budget（带护栏标签）
  - `cross_topic_overlap`：与 block-builder-flashblocks-throughput / execution-layer-reth-fork-comparison
    的重合度（避免重复计算）

### item-8: 针对 Mantle 的改进建议与优先级排序

基于 item-1 ~ item-7，输出针对 mantle-v2 op-node 的共识层改进建议清单。每条建议标注：

- 来源差距编号（item-X）
- 预期收益（ms/block、% block time、effective gas/s 中**之一**，带 evidence_grade）
- 改造成本（人月、风险等级、是否需要 hardfork）
- 是否依赖上游同步（op-node / op-rs/kona 的版本对齐）
- 与其他 Wave 主题（block-builder-flashblocks-throughput、execution-layer-reth-fork-comparison、
  perf-gap-analysis-recommendations）的协同/互斥关系

至少给出 3 条具体建议，覆盖：(a) 异步 / fire-and-forget engine 调用改造；(b) sequencer
build/seal 阶段解耦或动态 schedule；(c) `mantle-xyz/kona` fork 的定位选择（保持 FP-only vs
扩展到 kona-node online）。优先级遵循"低风险、低成本、高收益"。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| code_locations | 关键文件路径与行号引用（path:line），可点击复核（base/base、kona、mantle-v2、mantle-xyz/kona 四仓库） | all |
| upstream_baseline | 该 item 对应的上游基线 commit/tag（Tier A op-rs/kona、Tier B op-node）与滞后量 | item-1, item-5 |
| actor_or_module_map | Base actor ↔ op-node module 的一一对应（含未对应项） | item-1, item-2, item-4 |
| pipeline_stages | 每个流水线阶段名、调用者、被调者、是否阻塞、典型耗时 | item-2, item-4 |
| engine_api_call | 每个 Engine API 端点的版本、调用方、目标、同步/异步、频率、错误处理 | item-3 |
| perf_impact_estimate | 该改动/差距对共识层耗时 / TPS 的量化影响（带护栏标签：denominator、scenario、additivity_class、evidence_grade） | item-2, item-3, item-4, item-6, item-7 |
| risk_and_correctness | 改造的正确性保证、reorg / reset / recovery 路径、potential consensus break 风险 | item-7, item-8 |
| config_parameters | 涉及的配置常量（block_time、sealingDuration、verifier_l1_confs、L1 head poll interval、channel capacity 等），Base 取值、Mantle 取值、上游默认 | item-1, item-2, item-3 |
| attribution_tier | 该声明的归属层级 A/B/C/D/E（与 frontmatter `attribution_tiers` 一致） | all |
| cross_topic_dependencies | 与 block-builder-flashblocks-throughput、execution-layer-reth-fork-comparison、perf-gap-analysis-recommendations 等的接口/重叠 | item-2, item-6, item-7, item-8 |
| recommendation_metadata | 改进建议的成本/风险/收益评分，依赖关系，是否需要 hardfork | item-8 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Base base-consensus actor 拓扑 vs Mantle op-node event-bus 拓扑：两侧并列展示 actor / module 节点与连接，标注 channel capacity（Base 端：mpsc=1024、gossip_payload=256、signer=16、p2p_rpc=1024、admin_rpc=1024、EngineRpc semaphore=16、L1WatcherQueryProcessor concurrent=32）与 op-node event bus 订阅关系；高亮 Tier C（Base overlay）与 Tier D（Mantle overlay）边界 | mermaid | item-1 |
| diag-2 | flow | Sequencer build / seal / gossip / insert pipeline 时序图：横向时间轴，Base 与 Mantle 双轨，每阶段标注调用 (FCU / getPayload / newPayload) 与是否 fire-and-forget；标注 Base wall-clock-aligned schedule 与 Mantle `sealingDuration=50ms` 常量的差异 | mermaid | item-2 |
| diag-3 | sequence | Engine API 调用序列图（mermaid sequenceDiagram）：参与方 = Sequencer / Network / Derivation / Engine actor / EL；端点 = engine_forkchoiceUpdatedV3 / engine_getPayloadV3 / engine_newPayloadV4；展示 Base 的 mpsc + oneshot 模式 vs Mantle op-node 的 EngineController 直接调用模式；标注 sync_await vs fire_and_forget | mermaid | item-3 |
| diag-4 | comparison | Derivation pipeline 并行度对比：左 Base（独立 tokio task 上的 derivation actor，通过 engine actor mpsc 与 sequencer 解耦），右 Mantle op-node（与 sequencer / engine 同进程事件循环，BatchMux 多态调度）；标注 in-flight step 数与 lock / channel 共享情况 | mermaid | item-4 |
| diag-5 | hierarchy | 改进建议优先级矩阵：X 轴 = 改造成本（人月），Y 轴 = 预期 ms/block 节省或 effective gas/s 提升；把 item-8 的建议落点到 quick-win / strategic / risky / 不推荐四象限 | mermaid | item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | `base/base` 仓库 `crates/consensus/` 全目录代码扫描（重点：service/、engine/、derive/、service README），附 commit SHA 与文件:行号引用 | 1 |
| src-2 | code_analysis | `mantlenetworkio/mantle-v2` 仓库 `op-node/rollup/` 全目录代码扫描（重点：driver/、engine/、sequencing/、derive/），附 commit SHA 与文件:行号引用 | 1 |
| src-3 | code_analysis | `op-rs/kona` 上游作为 **Tier A baseline**：`crates/node/service`、`crates/node/engine`、`crates/node/actors/*`、`bin/node`，用于 Base 偏离度计算 | 1 |
| src-3b | code_analysis | **Tier B baseline（Primary，必需）**：`ethereum-optimism/optimism` 仓库 `op-node/` 作为 OP 继承基线；用于把 Mantle 自有改动从 OP 继承行为中区分出来 | 1 |
| src-4 | code_analysis | `mantle-xyz/kona` 仓库当前 HEAD 与各 feature 分支（arsia*, audit-fix, eigen_verify, feature/operator-fee, blob_test）+ `mantle-v2/kona/version.json` 与 `mantle-v2/op-challenger/flags/flags.go` 的 cannon-kona 引用，用于 item-5 的作用域澄清 | 1 |
| src-5 | official_docs | OP Stack Engine API 规范（specs.optimism.io 或 specs.base.org 的 engine_api 章节）；包含 V2/V3/V4 端点定义、hardfork 激活时机 | 2 |
| src-6 | official_docs | Base specs（specs.base.org / base-specs / blog.base.dev/introducing-base-azul 与相关共识层升级公告），用于 Tier C overlay 行为佐证 | 2 |
| src-7 | expert_commentary | op-rs/kona 与 op-node 关于 actor / pipeline / engine API 设计的讨论（kona issues、design docs、blog post），用于 Tier A baseline 行为佐证 | 2 |
| src-8 | on_chain_data | Base / Mantle 主网典型 block 的 timestamp gap、tx 数量、L1 epoch boundary（链上 RPC 或 dune），用于 item-6 共识层耗时占比估算的校准 | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
