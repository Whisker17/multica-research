---
topic: "Sequencer Pipeline 与共识层优化分析：Base base-consensus vs Mantle op-node / kona"
project_slug: base-perf-analysis
topic_slug: sequencer-consensus-pipeline-perf
github_repo: Whisker17/multica-research
round: 2
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
  last_modified_at: "2026-05-20T06:55:00Z"

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
* 1s - last_seal_duration` 调度）、initial reset retries。`PayloadSealer` 在 sequencer
主循环上推进至多四态（Sealed → Committed → Gossiped → Inserted，每态由
`PayloadSealer::step()` 推进一格，见 `actors/sequencer/seal.rs:75-126`）：

- `Sealed → Committed`：`conductor.commit_unsafe_payload(&envelope).await`，await conductor
  确认（`seal.rs:93-102`）。
- `Committed → Gossiped`：`gossip_client.schedule_execution_payload_gossip(payload).await`，
  await gossip 入队（`seal.rs:103-110`）。**注意作用域**：调用方仅 await「调度入队」这一步成功；
  gossip 在网络上向 peer 广播 payload 的过程本身是 fire-and-forget，与 PayloadSealer 主循环
  解耦。这里不是「插入完成 fire-and-forget」。
- `Gossiped → Inserted`：`engine_client.insert_unsafe_payload(payload).await`，**sequencer
  阻塞等待 engine actor 真正插入完成并回送 `L2BlockInfo` 后，主循环才视为本格 seal step 完成**
  （`seal.rs:111-116`）。`insert_unsafe_payload` 的精确语义（`actors/sequencer/engine_client.rs:195-230`）：
  构造 `mpsc::channel(1)` 拿到 `result_tx`，发送
  `EngineActorRequest::ProcessLocalUnsafeL2BlockRequest(Box<InsertUnsafePayloadRequest>)`
  到 engine actor 队列，其中
  `InsertUnsafePayloadRequest { envelope, result_tx: Some(result_tx) }`
  （字段定义见 `actors/engine/request.rs:60-99`），随后 `result_rx.recv().await` 阻塞直到拿到
  `Ok(inserted_head)`。**这条本地 sequencer 插入路径不是 fire-and-forget。**

`PayloadBuilder::build_on(parent)` 调用 `L1OriginSelector` → `StatefulAttributesBuilder::
prepare_payload_attributes()` → `PoolActivation` 检查 → `start_build_block` 发送 `BuildRequest`
返回 `PayloadId`。

⚠️ **路径分类（强制，应对 Round-1 Adversarial Finding）**：

`base/base` 的 `EngineActorRequest`（见 `actors/engine/request.rs:46-64`）至少包含两条
**语义截然不同**的 unsafe-payload 插入路径，outline / draft 与所有 diagrams 必须按下面的
分类描述与作图，不得混用同一标签：

| 路径名称 | 触发方 | EngineActorRequest 变体 | result_tx | 调用方语义 | 文件:行号 |
|---|---|---|---|---|---|
| 本地 sequencer 插入（acked / awaited） | sequencer actor 的 `PayloadSealer` | `ProcessLocalUnsafeL2BlockRequest(Box<InsertUnsafePayloadRequest>)` | `Some(mpsc::Sender<Result<L2BlockInfo, _>>)` | `mpsc.send().await` 入队 + `result_rx.recv().await` 等待确认 | `actors/sequencer/engine_client.rs:195-230`、`actors/sequencer/seal.rs:111-116`、`actors/engine/request.rs:60-99` |
| 外部 unsafe payload 插入（fire-and-forget） | derivation / network actor 收到 P2P unsafe payload | `ProcessUnsafeL2BlockRequest(Box<BaseExecutionPayloadEnvelope>)` | 无（变体里没有 result 通道） | `mpsc.send().await` 入队后即返回，不等待 RPC 结果 | `actors/engine/request.rs:58-59` |

任何把这两条路径混同的描述（例如"Base 把本地 sequencer 插入做成了 fire-and-forget"）都必须
被 `[MISATTRIBUTED]` 标记，并在 Patch Log 记录。Mantle 端不需要这种区分（仅有单一同步路径），
对比时必须先固定 Base 路径再比较。

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
  - `decoupling_class`：`fire_and_forget`（外部 unsafe payload，`ProcessUnsafeL2BlockRequest`，无 result_tx） | `awaited_via_mpsc_result_tx`（本地 sequencer 插入，`ProcessLocalUnsafeL2BlockRequest` + `Some(result_tx)`） | `awaited_via_oneshot`（build/get_payload result_tx） | `event_bus`（Mantle op-node） | `direct_sync_call`（Mantle EngineController）。**禁止用单一标签描述 Base 全部 Engine 路径**。

### item-3: Engine API 调用模式与版本兼容性

逐端点对比 `engine_forkchoiceUpdatedV{2,3}`、`engine_newPayloadV{2,3,4}`、`engine_getPayloadV{2,3,4}`
的调用模式：

- 端点版本与硬分叉激活（Base README 列出 V2/V3/V4 自动选择，按 Bedrock/Canyon/Delta/Ecotone/
  Isthmus 激活时间；Mantle op-node 通过 `chain_spec`/`mantle_chain_spec` 在 Arsia 升级前后选择）
- 调用方与目标 actor / module：Base 的 `EngineActorRequest` 共 **7 个变体**（`actors/engine/request.rs:46-64`）：
  `BuildRequest`、`GetPayloadRequest`、`ProcessSafeL2SignalRequest`、
  `ProcessFinalizedL2BlockNumberRequest`、
  **`ProcessUnsafeL2BlockRequest`（外部 unsafe payload 插入，无 result_tx，fire-and-forget）**、
  **`ProcessLocalUnsafeL2BlockRequest`（本地 sequencer 插入，`InsertUnsafePayloadRequest`
  携带 `Option<mpsc::Sender<Result<L2BlockInfo, InsertTaskError>>>`，sequencer 端 always
  以 `Some(_)` 调用，await 后取回 `L2BlockInfo`）**、`ResetRequest`；由 sequencer / network
  / derivation / RPC actor 通过 mpsc(1024) 入队（service README + `actors/engine/`）；
  Mantle 的 EngineController 直接持有 `engine.Engine` 接口
  （`ForkchoiceUpdate`/`NewPayload`/`GetPayload`），由 op-node `event` bus 触发
- 主循环内是否同步等待 RPC 返回 — **必须按 EngineActorRequest 变体分类，不可统一回答**：
  - **本地 sequencer 插入 — awaited path**：
    `ProcessLocalUnsafeL2BlockRequest` + `result_tx: Some(_)`，sequencer 等待 mpsc result
    channel 拿到 `L2BlockInfo` 后才推进 `PayloadSealer::step()`；这条路径**不释放** sequencer
    主循环进入下一个 build tick，直到 unsafe head 实际推进（`engine_client.rs:195-230`、
    `seal.rs:111-116`）。
  - **外部 unsafe payload 插入 — fire-and-forget path**：
    `ProcessUnsafeL2BlockRequest`，无 result_tx，调用方只 `mpsc.send().await` 入队成功即返回，
    不等待 engine actor 实际处理结果（`request.rs:58-59`）。这是由 derivation / network
    actor 在收到 P2P unsafe block 时使用，**不在 sequencer 主循环上**。
  - **Build / GetPayload — oneshot awaited**：
    通过 mpsc(1) result_tx 返回 `PayloadId` / `BaseExecutionPayloadEnvelope`，调用方 await。
    从 sequencer 视角等价于 sync_await，但 RPC 与 JWT/HTTP 开销已被搬到 engine actor 处理
    任务。
  - **SafeL2Signal / Finalized / Reset — 视具体调用是否 await result**：safe-signal /
    finalized 不携带 result（fire-and-forget 入队）；`ResetRequest` 可选携带 result_tx。
  - **Mantle EngineController**：所有 Engine RPC 调用统一为 `go func` over HTTP/JWT，由
    op-node event bus 触发但 RPC 完成是同步等待，**没有把 RPC 排队到独立 actor / task** 的
    隔离层。
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
  - `sync_or_async`（必须显式标注 EngineActorRequest 变体）：`awaited_via_mpsc_result_tx`（本地 sequencer insert，`ProcessLocalUnsafeL2BlockRequest`，sequencer await L2BlockInfo） | `fire_and_forget`（外部 unsafe payload，`ProcessUnsafeL2BlockRequest`，无 result_tx） | `oneshot_then_resume`（build / get_payload，sequencer await PayloadId / envelope） | `direct_sync_call_with_event_trigger`（Mantle EngineController over HTTP/JWT）。**禁止把 Base 全部 Engine API 路径标为单一类别。**
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

### item-7: Pipeline 并行化与 Engine API 架构解耦对 TPS 的影响估算

基于 item-2 / item-3 / item-4 / item-6 的差距，对"如果 Mantle 引入 Base 风格的共识层
解耦改造"的潜在 TPS 提升做量化推断。

**框架原则（强制，应对 Round-1 Adversarial Finding）**：

1. 改进的本质是 **架构解耦（actor 分离 + 任务队列）**，而**不是**在本地 sequencer 路径上
   采用 fire-and-forget。Base 的关键设计是把 sequencer actor 与直接持有 EL HTTP/JWT 客户端
   的 EngineController 剥离开：所有 Engine API 工作经 `EngineActorRequest` 通过 mpsc(1024)
   路由到独立的 engine actor / engine processing task；RPC、序列化、JWT 校验、connection 管
   理都由 engine actor 承担，sequencer 主循环只持有 mpsc handle。**但 sequencer 仍 await
   本地 insert 的 `result_tx` 确认**（见 item-2 / item-3），从而保证下一轮 build 建立在已被
   engine 真正写入的 unsafe head 之上，正确性不被损害。
2. **明确禁止**的不正确建议措辞：
   - ❌ "把 Mantle 的 newPayload+FCU 改成 Base 那样的 fire-and-forget"
   - ❌ "采用 Base 风格的 `ProcessUnsafeL2BlockRequest` 路径让 sequencer 不等待 insert"
   - 任何把 Base 本地 sequencer 路径与外部 unsafe payload fire-and-forget 路径混同的描述，
     必须被 `[MISATTRIBUTED]` 标记。
3. 唯一可以保留 fire-and-forget 语义的场景：外部 P2P unsafe payload 插入路径
   （`ProcessUnsafeL2BlockRequest`）。该路径**不直接影响 sequencer 主循环 TPS**，但可降低
   follower / verifier 在 catch-up 时的延迟。

**待量化的改造杠杆（lever）**：

- **lever-1：actor + 任务队列解耦**——把 op-node 的 EngineController 直接持有 EL RPC
  客户端的模式改造为 Base `engine_client.rs` 模式：sequencer 通过 mpsc 把
  `InsertUnsafePayloadRequest` 入队到独立 engine actor / engine processing task，
  RPC + JWT/HTTP + 序列化开销搬出主循环，但仍 await `result_tx` 拿到 `L2BlockInfo` 才推进
  下一格 seal step。量化能释放多少 ms/block 的 main-loop 阻塞时间（不是消除 insert 延迟
  本身）。
- **lever-2：build / seal / derivation 跨 task 并行**——actor 拓扑天然允许
  `PayloadBuilder::build_on(parent+1)` 与 `PayloadSealer::step(parent)` 在 sequencer
  actor 自身 select! 循环内有序推进，同时 derivation actor 在另一 tokio task 上独立 step；
  量化跨 task 并行能与 sequencer 主循环重叠多少 derivation 工作量。
- **lever-3：derivation 独立 task**——把 derivation 从 op-node 同进程事件循环拆出独立
  task / process（Base derivation actor 模式）能让 derivation step 不再延迟 sequencer
  build；量化在 L1 epoch 边界处的 dead time。
- **lever-4：动态 schedule 替代 `sealingDuration=50ms` 常量**——把 sequencer build /
  seal 两阶段从 50 ms 常量改为 wall-clock-aligned 动态 schedule（参考 Base 的
  `last_seal_duration` 反馈，见 item-2 build ticker 公式），量化能避免多少 dead time。
- **lever-5：外部 unsafe payload 路径的 fire-and-forget**——这一项仅适用于外部网络层 unsafe
  block 插入（`ProcessUnsafeL2BlockRequest`，无 result_tx）。对 sequencer 主循环 TPS 影响
  小，主要降低 follower / verifier 节点的 catch-up 延迟，不要与 lever-1 混用同一 TPS 收益。
- **lever-6：空块抑制**（参考 Base 的 PoolActivation + builder-side 持续构建）能把
  effective gas/s 提多少。

每条估算严格遵循 item-6 的护栏。明确"理论 TPS"与"有效 TPS"区别，与 sibling 主题
block-builder-flashblocks-throughput 的 effective TPS 分析对齐（不重复计算同一收益）。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-6
- **Required investigation_fields**:
  - `improvement_lever`：`actor_task_queue_decoupling`（lever-1，本地 insert 仍 awaited） | `cross_task_parallel_build_seal_derivation`（lever-2） | `derivation_independent_task`（lever-3） | `dynamic_seal_schedule`（lever-4，替代 `sealingDuration=50ms` 常量） | `external_unsafe_fire_and_forget`（lever-5，**仅限**外部 unsafe payload 路径） | `empty_block_suppression`（lever-6） | `kona_node_migration`（item-5 关联）
  - `expected_gain`：ms/block 或 % of block time budget（带护栏标签）
  - `cross_topic_overlap`：与 block-builder-flashblocks-throughput / execution-layer-reth-fork-comparison
    的重合度（避免重复计算）
  - `framing_check`：每条建议必须显式声明 "**not** fire-and-forget on local sequencer insert"，
    或者解释为何采用外部 unsafe path 框架；混淆描述标 `[MISATTRIBUTED]`

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
| diag-2 | flow | Sequencer build / seal / gossip / insert pipeline 时序图：横向时间轴，Base 与 Mantle 双轨，每阶段标注调用 (FCU / getPayload / newPayload / insert) 与 `decoupling_class` 标签（`fire_and_forget` / `awaited_via_mpsc_result_tx` / `awaited_via_oneshot` / `direct_sync_call`）。**强制要求**：`PayloadSealer` 的 `Gossiped → Inserted` 阶段必须画成 **sequencer ↔ engine actor 的双向往返**（mpsc 入队 + result_tx 回传 `L2BlockInfo`），不得画为单向 fire-and-forget 箭头；同时标注 Base wall-clock-aligned schedule 与 Mantle `sealingDuration=50ms` 常量的差异 | mermaid | item-2 |
| diag-3 | sequence | Engine API 调用序列图（mermaid sequenceDiagram）：参与方 = Sequencer actor / Network actor / Derivation actor / Engine actor / EL；端点 = engine_forkchoiceUpdatedV3 / engine_getPayloadV3 / engine_newPayloadV4 + insert 路径。**强制要求至少画三条独立 lane**：(1) **本地 sequencer 插入（awaited）**：Sequencer → mpsc → Engine actor → 处理 → result_tx 回 `L2BlockInfo` → Sequencer 继续，使用双向箭头明确表达 await；(2) **外部 unsafe payload 插入（fire-and-forget）**：Network/Derivation → mpsc → Engine actor，**单向箭头**、无返回；(3) **Mantle EngineController → EL** 的直接同步 HTTP/JWT RPC，单 lane 内 sync_await。标注 sync_await（awaited via mpsc result_tx）vs fire_and_forget（无 result_tx）vs direct_sync_call | mermaid | item-3 |
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
| 2 | modify_item | item-2 | Round-1 review blocking finding: split insert path into local sequencer (`ProcessLocalUnsafeL2BlockRequest` with `Some(result_tx)`, awaited via mpsc result channel) vs external unsafe payload (`ProcessUnsafeL2BlockRequest`, no result_tx, fire-and-forget). Add explicit path-classification table with file:line evidence. Round-1 mischaracterized the seal pipeline insertion as fire-and-forget. Evidence verified: `base/base` `crates/consensus/service/src/actors/sequencer/engine_client.rs:195-230`, `actors/sequencer/seal.rs:75-126` (Gossiped→Inserted awaits `L2BlockInfo`), `actors/engine/request.rs:46-99` (variant definitions + `InsertUnsafePayloadRequest { result_tx: Option<...> }`). Also update `PayloadSealer` to four states (Sealed→Committed→Gossiped→Inserted) matching the seal step machine, and reclassify `gossip_client.schedule_execution_payload_gossip` as "调度入队 awaited; on-network broadcast fire-and-forget" to avoid mixing two scopes. | agent:research-agent (id=13a888db-49bb-4a19-9906-827729e156d9) via Adversarial Agent verdict at comment e6566893-a822-4656-9b4b-69d950f1b599 |
| 2 | modify_field | item-2.decoupling_class | Expand enum from `fire_and_forget / awaited / oneshot_channel / event_bus` to per-variant labels (`fire_and_forget` for external unsafe only, `awaited_via_mpsc_result_tx` for local sequencer insert, `awaited_via_oneshot` for build/get_payload, `event_bus` and `direct_sync_call` for Mantle). Explicit ban on single-label Base summary. | same |
| 2 | modify_item | item-3 | Round-1 review blocking finding: enumerate all 7 `EngineActorRequest` variants (was incorrectly summarized as 5 with wrong names), split sync/async classification per variant so local sequencer insert is `awaited_via_mpsc_result_tx` rather than the broader `fire-and-forget` claim. Same evidence as item-2 (request.rs:46-64). | same |
| 2 | modify_field | item-3.sync_or_async | Replace generic enum (`sync_await / fire_and_forget / oneshot_then_resume`) with variant-specific labels and explicit ban on collapsing to a single Base category. | same |
| 2 | modify_item | item-7 | Round-1 review blocking finding: reframe Mantle improvement target. The architectural improvement is **actor + task queue decoupling** (Base routes Engine work through `EngineActorRequest` mpsc to a separate engine actor so RPC/JWT/HTTP overhead leaves the sequencer main loop) — **not** adopting fire-and-forget semantics on the local sequencer insert path. Restructure into lever-1..6 with explicit ban on `fire-and-forget newPayload+FCU` framing. Preserve fire-and-forget framing only for external unsafe payload path (lever-5) where it is correct. | same |
| 2 | modify_field | item-7.improvement_lever | Replace flat list (`异步 FCU / derivation 解耦 / 动态 schedule / 空块抑制 / kona-node 迁移`) with explicit lever-1..6 enum that pins fire-and-forget to the external path only. Add `framing_check` field requiring each draft recommendation to declare "not fire-and-forget on local sequencer insert" or explain external-path scope. | same |
| 2 | modify_diagram | diag-2 | Require seal pipeline diagram to show `PayloadSealer Gossiped → Inserted` as bidirectional (mpsc enqueue + result_tx return for `L2BlockInfo`), not as a one-way fire-and-forget arrow. | same |
| 2 | modify_diagram | diag-3 | Require Engine API sequence diagram to draw at least three independent lanes: (1) local sequencer insert with two-way arrow representing mpsc + result_tx await; (2) external unsafe payload insert with one-way arrow (no result); (3) Mantle EngineController direct HTTP/JWT RPC. Single-lane sync_await/fire_and_forget summary is no longer sufficient. | same |
