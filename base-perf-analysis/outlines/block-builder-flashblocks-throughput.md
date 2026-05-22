---
topic: "Block Builder 与 Flashblocks 对吞吐量的影响分析"
project_slug: base-perf-analysis
topic_slug: block-builder-flashblocks-throughput
github_repo: Whisker17/multica-research
multica_issue_id: 49cd3543-e373-48d9-918b-55a167873968
report_issue_id: d38ec675-b760-484d-b071-d235fec00784
order: 2
round: 1
status: candidate
rerun: true
rerun_authority: "Issue description updated 2026-05-22; previous May 20 outline/drafts/final are superseded and must not be reused without revalidation."

artifact_paths:
  outline: base-perf-analysis/outlines/block-builder-flashblocks-throughput.md
  draft: base-perf-analysis/research-sections/block-builder-flashblocks-throughput/drafts/round-{n}.md
  final: base-perf-analysis/research-sections/block-builder-flashblocks-throughput/final.md
  index: base-perf-analysis/research-sections/_index.md

scope: |
  分析 Base 的 Block Builder 分离架构（rollup-boost）和 Flashblocks 机制对有效吞吐量的提升贡献，
  并评估 Mantle 引入类似机制的可行性和预期收益。本次 rerun 以 2026-05-22 的 issue 描述为
  权威 scope，覆盖：
  (1) rollup-boost / builder sidecar 在 OP Stack Engine API 路径上的 multiplexing 行为，
      尤其是 `engine_forkchoiceUpdated` 与 `engine_getPayload` 的 builder + local 双路分发；
  (2) builder 优先 + local fallback 的 payload 选择策略，重点验证 `BlockSelectionPolicy::GasUsed`
      及延迟、超时、健康状态、payload-id 映射对选块结果的影响；
  (3) Base builder 中 Flashblocks 的 200ms sub-block 生成、payload 精简、WebSocket 发布与
      rollup-boost P2P `flblk/1` 方案之间的吞吐/传播路径差异；
  (4) 空块从约 200/天降至约 2/天的公开 claim 与实际链上样本之间的一致性，并拆解其机制来源；
  (5) Mantle 当前 block building 流程、空块率 baseline，以及 `mantle-xyz/reth` 的
      `flashblocks/poc` 和 `feat/flashblocks-mantle-aware` 分支进展；
  (6) builder 分离、空块消除、Flashblocks pre-confirmation 三类收益的非重复量化，区分
      effective gas throughput、finalized TPS、user-perceived TPS。

out_of_scope: |
  - Flashblocks 安全性、授权模型、HA 故障转移的完整安全分析；仅在传播路径与吞吐开销相关处记录。
  - Batcher 对 Flashblocks 数据的处理方式、DA 提交策略与 batcher pipeline 内部瓶颈。
  - MEV / 排序策略 / builder 激励或收益分配；只分析 gas-used 选择策略对吞吐的工程影响。

audience: |
  Mantle / Base 协议工程师、sequencer 与 execution client 团队、Multica base-perf-analysis
  下游研究作者与 Technical Writer。读者熟悉 OP Stack Engine API、reth payload builder、
  sequencer 2s block cadence、unsafe/safe/finalized head 语义，但不要求预先了解 Base
  builder 或 rollup-boost 的具体实现。

expected_output: |
  - rollup-boost 数据流架构图和 Engine API multiplexing 分析，包含 builder/local 分发、
    payload-id 映射、超时与 fallback 边。
  - `BlockSelectionPolicy::GasUsed` 选块逻辑的代码级解释，说明为什么 builder payload 默认优先、
    何时 local payload 胜出、如何限制 builder 慢/差导致的吞吐或延迟损失。
  - Base builder Flashblocks 生命周期分析：200ms sub-block 生成、gas/DA budget 分片、
    state-root 计算策略、WebSocket 发布和 consumer pending-state 组合。
  - Flashblocks P2P `flblk/1` 规范与 WebSocket 中继模式的吞吐/传播/消息放大差异。
  - 空块率 99% 降低 claim 的机制拆解与链上验证计划；若样本与公开 claim 不一致，必须标注
    evidence level 与置信区间，不得沿用旧结论。
  - Mantle 当前 block building 与 flashblocks POC 分支进展评估，含 commit-level diff、
    关键阻塞点、生产化缺口。
  - Builder 分离后 sequencer 主循环 CPU/内存释放量的 first-order 估算，明确哪些工作真的
    从 sequencer 热路径移出，哪些只是进程边界变化。
  - 至少 3 张 Mermaid 图：rollup-boost 架构图、Flashblocks 生命周期、builder 分离前后
    sequencer 主循环对比。
  - Mantle 引入 rollup-boost + Flashblocks 的可行性结论、收益上限、风险与优先级建议。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-22T11:35:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-22T11:35:00Z"

evidence_policy:
  levels:
    - id: verified-code
      meaning: "代码路径在指定 commit 中直接验证，附 path:line。"
    - id: verified-data
      meaning: "链上或 telemetry 数据可复现，附查询窗口、采样方法、置信区间。"
    - id: reported
      meaning: "来自官方博客/规范/README，但未独立复算。"
    - id: inferred
      meaning: "由代码结构或公开数据推导，必须列出假设。"
    - id: unresolved
      meaning: "证据冲突或缺失，不能作为结论使用。"
  mandatory_rules:
    - "旧 final.md / round-1/2/3.md 的数值与结论只能作为 historical context，不得复制为新结论。"
    - "所有吞吐收益必须归类为 effective gas throughput、finalized TPS、user-perceived TPS 之一。"
    - "Builder 分离、空块减少、pre-confirmation 三类收益不得简单相加；必须说明重叠与上限。"
    - "任何 Base vs Mantle 对比都必须分清 OP upstream、Base overlay、Mantle overlay、reth upstream。"
---

# Research Outline: Block Builder 与 Flashblocks 对吞吐量的影响分析

## Rerun Notes

本 outline 覆盖 2026-05-22 更新后的 issue scope。前次 May 20 的 outline、drafts 与 final 已被
Orchestrator 标记为可覆盖的旧产物；Phase B 可参考其问题历史，但必须重新验证核心代码、分支、
空块数据与量化模型。

## Key Questions Coverage

| Question | Primary Items | Required Output |
|---|---|---|
| Q1: rollup-boost 的 builder 选择策略如何避免延迟增加同时提升 gas 利用率？ | item-1, item-2, item-3 | Engine API 双路分发时序、GasUsed policy 决策树、超时/fallback 约束 |
| Q2: 空块率 99% 降低通过什么机制实现？ | item-4, item-5 | 公开 claim 拆解、代码机制、链上复核、与 pending-tx / no-tx-pool 行为关系 |
| Q3: 200ms sub-block 粒度对同步与状态一致性的额外开销？ | item-6, item-7 | producer/consumer 生命周期、状态 root / pending-state 开销、WebSocket vs P2P 对比 |
| Q4: Mantle `flashblocks/poc` 分支实现程度和阻塞点？ | item-8, item-9 | 两分支 commit-level diff、功能覆盖矩阵、生产化缺口 |
| Q5: Builder 分离后 sequencer 主循环 CPU/内存释放量估算？ | item-10, item-11 | 热路径工作量拆解、资源释放估算、Mantle ROI 与路线图 |

## Items

### item-1: rollup-boost 架构定位与 Engine API multiplexing

重建 rollup-boost 在 sequencer / local L2 execution engine / external builder 之间的 sidecar
位置。重点验证 `engine_forkchoiceUpdated`、`engine_getPayload`、必要时 `engine_newPayload`
是否分别发往 local 与 builder；在什么条件下 builder 只接收 FCU、何时 builder payload-id 与
local payload-id 需要映射；`no_tx_pool`、execution mode、builder health 对流量分发的影响。

Phase B 必须从 `flashbots/rollup-boost` 的 `crates/rollup-boost/src/proxy.rs`、
`engine_api.rs`、`server.rs`、`client/*`、`probe.rs` 与 integration tests 中提取 path:line
证据，并把 Base `crates/builder` 中外部 builder 进程与 local base-reth-node 的边界分开。

- **Priority**: high
- **Dependencies**: none
- **Required investigation_fields**:
  - `engine_api_route_matrix`: method -> local / builder / both / conditional
  - `payload_id_mapping`: local payload id 与 builder payload id 的转换点
  - `health_and_execution_mode`: 不健康 builder 是否继续接收 FCU/getPayload
  - `latency_budget`: proxy 额外序列化、RPC、timeout 与 block-time budget 的关系
  - `code_locations`: commit SHA + path:line

### item-2: Builder 优先 + local fallback 的 payload 选择策略

分析 `BlockSelectionPolicy`，特别是 `GasUsed` 策略：builder 与 local payload 均可用时如何比较；
builder gas used 低于 local 的阈值时如何回退 local；tie-breaker 是否默认 builder；异常/超时/invalid
payload 时的 local fallback 是否发生在同一个 block-time 内。必须区分“builder 提供更满的块”
与“builder 比 local 慢但仍被等待”的不同风险。

需要将 selection policy 与 tests 串起来：`builder_full_delay`、`remote_builder_down`、
`builder_returns_incorrect_block`、`unhealthy_builder_traffic`、`no_tx_pool` 等测试能否说明延迟
和 liveness 边界。

- **Priority**: high
- **Dependencies**: item-1
- **Required investigation_fields**:
  - `selection_decision_tree`: builder/local/invalid/timeout/unhealthy/no_tx_pool 分支
  - `gas_used_threshold`: 阈值、单位、边界条件、test coverage
  - `fallback_timing`: fallback 是否等待到 getPayload、是否影响 2s cadence
  - `throughput_vs_latency_tradeoff`: gas utilization 提升与额外等待时间的证据等级
  - `open_config_questions`: Base production 参数是否公开、无法获取时的替代证据

### item-3: Base `crates/builder` 与 rollup-boost 的职责边界

Base `base/base` 当前树包含 `crates/builder/core`、`crates/builder/publish`、
`crates/execution/flashblocks`、`crates/common/flashblocks` 等模块；rollup-boost 则包含 proxy、
selection、Flashblocks inbound/outbound 与 P2P spec。Phase B 需要明确哪些吞吐贡献来自
external builder sidecar，哪些来自 Base 自有 builder payload builder，避免把 rollup-boost
proxy 行为误归到 `base/base` 或反向误归。

输出应包括模块边界表：`rollup-boost` proxy / selection / flashblocks relay、Base builder
payload construction、Base publish WebSocket、Base execution consumer pending-state、Mantle
reth consumer POC。

- **Priority**: high
- **Dependencies**: item-1, item-2
- **Required investigation_fields**:
  - `ownership_boundary`: flashbots/rollup-boost vs base/base vs mantle-xyz/reth
  - `process_boundary`: sequencer, rollup-boost, local EL, builder EL, RPC consumer
  - `misattribution_risks`: 旧报告或外部资料中可能混淆的声明
  - `artifact_reuse_guard`: 旧 final 中哪些声明需要重算

### item-4: 空块减少 claim 的来源、定义与链上复核设计

对“空块减少 99%（约 200/天到约 2/天）”建立可复核方法。首先确认官方来源（Base Azul blog、
Base docs、rollup-boost docs 或 dashboard）中“empty block”的定义：0 tx、仅 deposit/system tx、
gas_used=0、或用户交易为空。然后用 Base 主网与 Mantle 主网同窗口抽样复算：

- Base Azul / Flashblocks 上线前后窗口；
- Mantle 当前窗口；
- 相同采样长度下的 empty blocks/day、empty ratio、gas_used/block、effective gas/s；
- Wilson / bootstrap CI 或至少给出样本误差说明。

旧报告中出现过公开 claim 与样本差异，rerun 必须重新处理为 evidence-labeled 结论。

- **Priority**: high
- **Dependencies**: item-1, item-2
- **Required investigation_fields**:
  - `empty_block_definition`: 0 tx / gas_used=0 / user-tx-empty 的口径
  - `sampling_method`: RPC / explorer / Dune / BigQuery 查询窗口与脚本
  - `base_before_after`: Base 上线前后数据
  - `mantle_baseline`: Mantle 当前 empty rate 与 gas utilization
  - `confidence_label`: verified-data / reported / unresolved-discrepant

### item-5: 空块消除机制与有效 gas-throughput 贡献

在 item-4 数据基础上拆解机制：空块减少是否主要来自 external builder 持续构建更完整 payload、
Base builder 的 txpool/best-txs 选择、`no_tx_pool` 行为、pending tx 检测、或 sequencer cadence
策略改变。需要用 `base/base` `crates/builder/core/src/flashblocks/payload.rs`、
`best_txs.rs`、`config.rs`、tests，以及 rollup-boost `no_tx_pool`/execution mode tests 验证。

量化时只计算 effective gas throughput，即相同 block gas limit 和 block time 下，empty ratio
下降与 gas_used/block 上升对 `gas_used / second` 的贡献。不得把 pre-confirmation latency 改善
算作 final TPS 增加。

- **Priority**: high
- **Dependencies**: item-2, item-4
- **Required investigation_fields**:
  - `mechanism_classification`: builder-continuous / pending-detection / no_tx_pool / txpool-best / other
  - `gas_utilization_delta`: gas_used/block、non-empty ratio、effective gas/s
  - `counterfactual`: Mantle 如果只减少空块、不改变 gas limit，收益是多少
  - `non_additivity_guard`: 与 item-10 CPU/offload 收益的重叠关系

### item-6: Flashblocks producer 生命周期与 payload 大小优化

分析 Base builder 如何按 200ms 级别生成 Flashblocks：`flashblocks_interval`、每 block 的
flashblocks 数量、leeway/time drift、gas/DA budget 分片、state-root 是否在每个 flashblock 计算、
payload base + diff 的序列化字段、WebSocket publish 的 ring buffer / subscriber 行为。

重点代码面：`base/base` `crates/builder/core/src/flashblocks/payload.rs`、
`context.rs`、`generator.rs`、`best_txs.rs`、`crates/common/flashblocks/src/payload.rs`、
`crates/builder/publish/src/publisher.rs`。输出需要解释 payload size optimization 来自哪些字段复用
或推迟计算，而不是泛称“更小 payload”。

- **Priority**: high
- **Dependencies**: none
- **Required investigation_fields**:
  - `subblock_cadence`: 200ms / derived interval / leeway / missing flashblocks metrics
  - `payload_schema`: base fields vs diff fields vs metadata
  - `state_root_strategy`: intermediate zero/omitted vs final compute
  - `gas_da_budget_split`: gas_per_batch、DA limit per flashblock
  - `publish_path`: WebSocket publish, buffer, subscriber backpressure behavior

### item-7: Flashblocks consumer、pending-state 与 200ms 开销

分析 Flashblocks 对节点同步和状态一致性的额外开销。Base consumer 侧应覆盖
`crates/execution/flashblocks` 与 `flashblocks-node`：接收 Flashblocks、组合 pending blocks、
pending tag RPC、receipt/transaction fallback、canonical block 到达后的清理、gap/sequence 检查。
Mantle reth POC 侧应覆盖 `crates/optimism/flashblocks/src/service.rs`、`sequence.rs`、
`worker.rs`、`consensus.rs`、`ws/stream.rs` 等。

输出需把开销拆成 CPU（重复执行/状态 root）、内存（pending sequence/cache）、网络（每 200ms
广播）、RPC 语义（pending block/receipt/logs）和一致性（canonical block 到来时 reconcile）五类。

- **Priority**: high
- **Dependencies**: item-6
- **Required investigation_fields**:
  - `consumer_state_machine`: sequence insert / gap handling / canonical reconcile
  - `state_consistency_cost`: rewind/re-execution/cache layering
  - `rpc_semantics`: pending block、eth_subscribe、receipt fallback、sync tx path
  - `overhead_model`: per-subblock CPU/network/memory estimates with evidence labels
  - `final_vs_perceived_tps`: pre-confirmation latency improvement vs final block throughput

### item-8: WebSocket 广播 vs P2P `flblk/1` 子协议吞吐差异

比较当前 WebSocket 模式与 P2P `flblk/1` 规范。WebSocket 路径中 builder/rollup-boost/proxy/RPC
provider 是否形成中心化 fanout；P2P 方案如何通过 AuthorizedMessage、StartPublish/StopPublish、
builder signature、authorizer signature、duplicate suppression 与 gossip fanout 改变吞吐和故障边界。

注意：安全性与 HA 不是本课题主轴，但 P2P 协议的授权与 single-publisher 规则会影响吞吐路径、
消息大小、验证成本和 failover 时是否丢失 preconfirmations，因此需要在吞吐开销维度简述。

- **Priority**: medium
- **Dependencies**: item-6, item-7
- **Required investigation_fields**:
  - `transport_topology`: one-to-many WebSocket vs peer gossip
  - `message_overhead`: authorization/signature/start-stop messages vs raw payload
  - `fanout_model`: producer outbound bandwidth、RPC provider inbound bandwidth、dup suppression
  - `implementation_status`: rollup-boost P2P spec vs code readiness
  - `scope_boundary`: security/HA details deferred, throughput implications retained

### item-9: Mantle 当前 block building baseline

梳理 Mantle 当前生产路径：sequencer 如何调用 execution engine，是否有 builder sidecar 或外部 builder
分离；op-node / reth / op-geth 之间的 payload building 边界；是否存在 `miner_*` runtime controls；
当前 empty block rate、gas_used/block、effective gas/s、block time variance。需要与
`sequencer-consensus-pipeline-perf`、`execution-layer-reth-fork-comparison`、`batcher-sequencer-backpressure`
等同项目章节对齐，避免重复但要给出本课题可用 baseline。

- **Priority**: high
- **Dependencies**: item-4
- **Required investigation_fields**:
  - `mantle_execution_path`: sequencer -> EL Engine API -> payload builder
  - `builder_separation_status`: none / partial / branch-only / production
  - `empty_block_baseline`: same method as item-4
  - `gas_utilization_baseline`: gas_used/block、gas/s、final TPS proxy
  - `cross_section_inputs`: other base-perf-analysis sections consumed and caveats

### item-10: Mantle `flashblocks/poc` 与 `feat/flashblocks-mantle-aware` 分支进展

对 `mantle-xyz/reth` 两个分支做 commit-level diff，而不是按功能名推断。初步 source scan 显示：
`flashblocks/poc` 包含 `crates/optimism/flashblocks`、WebSocket stream、sequence、service、worker、
consensus client 等模块；`feat/flashblocks-mantle-aware` 在此基础上包含 Mantle-aware `extra_data`
解析/兼容 helper。Phase B 必须验证：

- 分支基线与最新 commit：`flashblocks/poc`、`feat/flashblocks-mantle-aware`、Mantle reth main/upstream；
- producer 是否存在，还是主要 consumer / pending-state POC；
- 是否接入 execution engine / consensus client / RPC pubsub；
- Mantle `extra_data`、receipt、L1 cost、token ratio、Arsia/chain spec 兼容改动；
- 测试覆盖、运行入口、缺失生产 wiring。

- **Priority**: high
- **Dependencies**: item-7, item-9
- **Required investigation_fields**:
  - `branch_commit_map`: branch, base commit, head commit, touched files
  - `feature_matrix`: producer / consumer / RPC / consensus injection / state root / tests
  - `mantle_specific_adaptations`: extra_data, fee fields, chain spec, receipt/accounting
  - `blockers`: missing components, unresolved TODOs, test gaps, upstream divergence
  - `production_gap_estimate`: low/medium/high effort with evidence

### item-11: Builder 分离对 sequencer 主循环 CPU/内存释放量估算

构建 builder separation 资源模型。先列出 stock / Mantle 当前 sequencer 热路径中哪些步骤在主循环内
等待：forkchoice update、start payload build、tx selection、execute/simulate、state-root、
getPayload/finalize、unsafe insert、gossip。再对比 rollup-boost + external builder 后哪些工作迁到
builder process，哪些仍由 local EL 作为 fallback 执行，哪些只是并行竞速但没有减少总机器资源。

必须给出 CPU、内存、latency 三类估算，并标明 evidence level。资源释放不能直接等同 TPS 增长；
若 block gas limit、state execution、batcher/DA、RPC 等仍是瓶颈，应给出上限约束。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-9
- **Required investigation_fields**:
  - `main_loop_work_breakdown`: before/after stage table
  - `offloaded_work`: tx ordering, payload assembly, state-root, validation, publish
  - `retained_work`: local fallback, final validation, unsafe insertion, consensus bookkeeping
  - `resource_estimate`: CPU core-ms/block、memory working set、latency saved
  - `bottleneck_guard`: why freed CPU may or may not translate to final TPS

### item-12: Mantle 可行性、收益上限与推荐路线

综合前 11 个 item，输出 Mantle 是否应引入 rollup-boost / Flashblocks、应先做哪个子集、预期收益上限
和工程风险。建议至少分三阶段：

1. Measurement gate：空块率、gas utilization、sequencer CPU profile、flashblocks POC benchmark；
2. Consumer-first / RPC pre-confirmation：若 producer 尚不成熟，先验证 consumer pending-state 与
   RPC 语义；
3. Builder separation + Flashblocks producer：接入 rollup-boost sidecar、local fallback、
   payload selection、P2P/WS 传播；
4. Production hardening：metrics、alerts、fallback drills、compatibility tests。

输出需包含“收益类型矩阵”：最终有效吞吐、用户感知确认延迟、sequencer 资源余量、空块浪费减少、
实现成本、上线风险。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7, item-8, item-9, item-10, item-11
- **Required investigation_fields**:
  - `benefit_matrix`: benefit type, estimate, evidence, caveat
  - `implementation_roadmap`: POC/testnet/mainnet steps
  - `dependency_map`: reth, op-node, op-geth, RPC, metrics, batcher-adjacent constraints
  - `recommendation`: proceed / defer / measurement-first with rationale
  - `index_summary_candidate`: one-line summary for final promotion

## Fields

| Field | Description | Applies To |
|---|---|---|
| code_locations | 每条代码声明的 repo、commit SHA、path:line；不接受仅文件名 | all |
| ownership_boundary | flashbots/rollup-boost、base/base、mantle-xyz/reth、mantlenetworkio/mantle-v2/op-geth 的责任归属 | item-1, item-3, item-8, item-10 |
| engine_api_route_matrix | FCU/getPayload/newPayload 的 caller、callee、是否双路、是否 conditional、超时/fallback | item-1, item-2 |
| selection_policy | BlockSelectionPolicy 分支、gas-used 阈值、tie-breaker、invalid/timeout/unhealthy 行为 | item-2 |
| latency_budget | 每跳延迟、等待点、timeout、block-time budget 占比 | item-1, item-2, item-6, item-11 |
| empty_block_method | 空块定义、采样窗口、查询方法、CI/误差、Base/Mantle 对比 | item-4, item-5, item-9 |
| throughput_accounting | effective gas throughput / finalized TPS / user-perceived TPS 分类与非重复计算 | item-4, item-5, item-7, item-11, item-12 |
| flashblocks_payload_schema | base/diff/metadata 字段、压缩/精简点、state-root 策略、大小估算 | item-6, item-8 |
| consumer_state_consistency | sequence/gap/canonical reconcile/pending RPC 的状态一致性成本 | item-7, item-10 |
| transport_comparison | WebSocket vs P2P flblk/1 的 fanout、message overhead、implementation status | item-8 |
| mantle_branch_diff | `flashblocks/poc` 与 `feat/flashblocks-mantle-aware` commit-level diff 和功能矩阵 | item-10 |
| resource_release_model | builder 分离前后 CPU/memory/latency 工作量转移与上限约束 | item-11 |
| evidence_level | verified-code / verified-data / reported / inferred / unresolved 标签 | all |
| cross_topic_dependencies | 与 base-perf-analysis 其它章节的输入/输出关系和不能重复计算的收益 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|---|---|---|---|---|
| diag-1 | architecture | rollup-boost 数据流：Sequencer -> rollup-boost proxy -> local EL + builder EL 双路；FCU/getPayload/newPayload 路径、payload-id 映射、timeout/fallback、BlockSelectionPolicy 回传 | mermaid | item-1, item-2, item-3 |
| diag-2 | flow | Flashblocks 生命周期：builder payload context -> 200ms flashblock generation -> WebSocket publish / P2P flblk/1 gossip -> consumer pending state -> final canonical block reconcile；区分 pre-confirmation 与 finalization 时间轴 | mermaid | item-6, item-7, item-8 |
| diag-3 | comparison | Builder 分离前后 sequencer 主循环对比：当前 Mantle/stock 内嵌 build vs rollup-boost external builder + local fallback；高亮 offloaded、retained、duplicated work | mermaid | item-9, item-11 |
| diag-4 | matrix | Mantle adoption roadmap / dependency map：measurement gate -> consumer POC -> builder/proxy integration -> production hardening；标注 reth/op-node/op-geth/RPC/metrics 依赖 | mermaid | item-10, item-12 |

## Source Requirements

| ID | Type | Description | Min Count |
|---|---|---|---|
| src-1 | code_analysis | `base/base` main (`fc58ee84456ea0339ae900a16fdb5c06f957e948` observed in Phase A) `crates/builder/core`, `crates/builder/publish`, `crates/common/flashblocks`, `crates/execution/flashblocks`, `crates/execution/flashblocks-node` | 8 file refs |
| src-2 | code_analysis | `flashbots/rollup-boost` main (`ea7fe88f52f875f022672746b87b2bfb36c4e3be` observed in Phase A) `crates/rollup-boost/src/proxy.rs`, `engine_api.rs`, `selection.rs`, `flashblocks/*`, tests | 8 file refs |
| src-3 | code_analysis | `mantle-xyz/reth` `flashblocks/poc` (`1f8b656685886da9c325fb65214ec4146be739b6` observed) commit-level diff and `crates/optimism/flashblocks` feature matrix | 1 branch diff |
| src-4 | code_analysis | `mantle-xyz/reth` `feat/flashblocks-mantle-aware` (`58741b285f7f26ae0e7e2c65ec5d757d56117f5a` observed) commit-level diff against `flashblocks/poc` and Mantle baseline | 1 branch diff |
| src-5 | code_analysis | Mantle production baseline repos as needed: `mantlenetworkio/mantle-v2` op-node/sequencer and `mantlenetworkio/op-geth` payload builder / miner controls | 4 file refs |
| src-6 | official_spec | Flashblocks P2P spec. Dispatch names `specs/flashblocks_p2p.md` in `base/base`; Phase A observed this file in `flashbots/rollup-boost/specs/flashblocks_p2p.md` and no top-level `specs/` in checked `base/base` main, so Phase B must resolve canonical location and cite permanent URL/commit. | 1 spec |
| src-7 | official_docs | Base Azul / Flashblocks public docs or blog for empty-block reduction, 200ms pre-confirmation, payload-size claims, and deployment timeline | 2 docs |
| src-8 | expert_commentary | Flashbots / Base engineering material explaining rollup-boost design, external block production, builder fallback, or load testing acceptance criteria | 1 source |
| src-9 | on_chain_data | Base and Mantle empty-block / gas utilization sampling with reproducible method and uncertainty; must include exact block ranges and query code or dashboard permalink | 2 chain samples |
| src-10 | performance_data | Any available benchmark/profile/load-test data for builder CPU, Flashblocks publish/consume overhead, WebSocket/P2P throughput, or Mantle POC runtime | 1 dataset or explicit gap |

## Cross-Topic Dependencies

| Topic | Direction | Use |
|---|---|---|
| execution-layer-reth-fork-comparison | consume | Mantle reth fork attribution, upstream vs Mantle overlay boundaries, execution-client bottleneck caveats |
| sequencer-consensus-pipeline-perf | consume | Sequencer main-loop stages and FCU/getPayload path baseline; do not duplicate full consensus analysis |
| batcher-sequencer-backpressure | consume | Distinguish user-perceived pre-confirmation from DA/finalized throughput; avoid claiming Flashblocks solves batcher backpressure |
| da-bandwidth-throughput-ceiling | consume | Cap final throughput conclusions when DA is/ is not bottleneck |
| perf-gap-analysis-recommendations | produce | Provide recommended Mantle adoption options and evidence labels for final recommendation synthesis |

## Up-Front Gaps / Risks

1. **Spec location ambiguity**: Dispatch says `base/base/specs/flashblocks_p2p.md`; Phase A checkout did not find top-level `specs/` in `base/base` main but did find `flashbots/rollup-boost/specs/flashblocks_p2p.md`. Phase B must cite the canonical committed path and explain if dispatch path was stale.
2. **Empty-block claim may not match samples**: The `~200/day -> ~2/day` figure must be treated as reported until independently sampled. If sample windows diverge, final must present both and label confidence.
3. **Mantle POC may be consumer-heavy**: Initial scan shows `crates/optimism/flashblocks` consumer/sequence/ws/service code on `flashblocks/poc`; producer and production wiring require proof rather than inference.
4. **Throughput double-counting risk**: Builder separation, empty-block reduction, and pre-confirmation latency may overlap. The draft must provide a non-additive model and upper/lower bounds.
5. **Resource-release uncertainty**: CPU/memory release estimates may need profiles unavailable from public repos. If no production metrics exist, use bounded synthetic estimates and mark as inferred.
6. **Branch drift**: `mantle-xyz/reth` flashblocks branches may move. Phase B must record exact commit SHAs at analysis time and avoid relying on Phase A observed SHAs if they change.

## Acceptance Checklist For Phase B Dispatch

- [ ] Covers all five Key Questions and all current issue scope bullets.
- [ ] Includes at least diag-1, diag-2, diag-3 as Mermaid diagrams; diag-4 recommended.
- [ ] Provides code path and line references for every code claim.
- [ ] Separates effective gas throughput, finalized TPS, and user-perceived TPS.
- [ ] Validates or downgrades the empty-block 99% claim using chain data.
- [ ] Evaluates both Mantle reth branches with commit-level diffs.
- [ ] Quantifies builder-separation CPU/memory release with explicit evidence labels.
- [ ] Does not analyze Flashblocks security/HA, batcher data handling, or MEV beyond throughput-relevant notes.

## Patch Log

| Round | Action | Target | Reason | Source |
|---|---|---|---|---|
| 1 | Re-run outline generated from updated issue scope | Entire outline | User requested reimplementation on 2026-05-22; previous May 20 artifacts superseded | Orchestrator dispatch comment `4bdc7feb-3444-46bb-b91c-fa2dfc14a6a7` |
