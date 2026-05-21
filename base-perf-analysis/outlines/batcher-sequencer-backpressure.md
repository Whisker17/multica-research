---
topic: "Batcher-Sequencer 背压机制与解耦策略 (Base vs Mantle)"
project_slug: base-perf-analysis
topic_slug: batcher-sequencer-backpressure
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: base-perf-analysis/outlines/batcher-sequencer-backpressure.md
  draft: base-perf-analysis/research-sections/batcher-sequencer-backpressure/drafts/round-{n}.md
  final: base-perf-analysis/research-sections/batcher-sequencer-backpressure/final.md
  index: base-perf-analysis/research-sections/_index.md

scope: |
  分析 Batcher 吞吐量瓶颈如何向 Sequencer 传递背压从而限制链的有效 TPS，对比
  Base 和 Mantle 在 batcher-sequencer 解耦策略上的差异，评估解耦方案对 Mantle
  TPS 提升的潜力。覆盖：背压机制分类（显式 vs 隐式）、Sequencer→Batcher 数据流
  与 unsafe blocks 消费机制、SequencerMaxSafeLag 与 DA Throttling 两套显式背压
  控制器、Unsafe span 增长控制与 reorg 风险、Base Flashblocks pre-confirmation
  解耦、"5k TPS" 语义精确分析（pre-confirmation vs finalized）、4 种改进策略
  可行性评估（异步 batcher、多 batcher 实例、Flashblocks 式解耦、自适应 gas
  limit）。不进入：batcher 内部 pipeline 优化细节（由课题 5a 覆盖）、DA 带宽
  理论上限（由课题 5b 覆盖）、fault proof 对 safe head 的要求。

audience: |
  Mantle 协议核心工程师、Sequencer / DA 团队、性能优化决策者。读者熟悉 OP Stack
  基本架构（unsafe/safe/finalized head 语义、batcher 与 derivation pipeline 关系），
  但不一定熟悉 OP Stack 上游新增的 DA throttling 控制器细节或 Base Flashblocks
  pre-confirmation 机制的具体实现。

expected_output: |
  - Batcher-sequencer 背压机制对比图（Mermaid）
  - Unsafe span 行为分析（正常 vs 压力场景）
  - "5k TPS" 定义精确分析（pre-confirmation vs finalized）
  - 4 种解耦改进策略可行性评估矩阵
  - 针对 Mantle 的优先推荐方案

dependencies:
  - topic_slug: batcher-pipeline-architecture
    relationship: |
      5a 提供 batcher 内部串行瓶颈定位（R1: MaxPendingTransactions=1, R2b: TargetNumFrames=1,
      R3: single pending channel），on-chain 观测数据（Mantle ~448s/tx, Base ~49s/tx），
      以及 §6.6 "sequencer 出块速度 ~10× batcher 提交速度" 的耦合度量。本课题在
      5a 的 batcher-side 瓶颈之上，分析这些瓶颈如何通过背压信号传导回 sequencer。
  - topic_slug: da-bandwidth-throughput-ceiling
    relationship: |
      5b 证实 DA 带宽不是 Mantle 当前约束（1.18 TPS 需求 vs ~1,749 TPS DA ceiling，
      ~1,480× 余量），因此 batcher-sequencer 背压不能归因于 L1 DA 稀缺，而是
      batcher 内部队列/控制环路问题。本课题在此基础上分析背压的实际传导路径。
  - topic_slug: block-builder-flashblocks-throughput
    relationship: |
      Section 2 分析了 Flashblocks pre-confirmation 机制如何将用户感知 TPS 与 DA
      finalized TPS 解耦，以及 Mantle reth 分支的 Flashblocks 移植进度。本课题
      将 Flashblocks 作为一种解耦策略进行可行性评估。
  - topic_slug: sequencer-consensus-pipeline-perf
    relationship: |
      Section 4 分析了 Base actor model vs Mantle event-bus 的 sequencer 架构差异，
      包括 sealingDuration=50ms 硬编码、FCU 调用模式等。本课题关注 sequencer 侧
      接收背压后的行为（stall vs throttle）以及架构对背压响应效率的影响。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-20T11:10:00Z"
---

# Research Outline: Batcher-Sequencer 背压机制与解耦策略 (Base vs Mantle)

## Items

### item-1: 背压机制全景分类与数据流映射

对 Base 和 Mantle 的 batcher-sequencer 背压机制进行系统分类，绘制完整的数据流与
背压信号传递路径。分为四类机制：

**显式背压-sequencer 侧**：`SequencerMaxSafeLag`（`mantle-v2/op-node/rollup/
sequencing/sequencer.go:449-454`）——当 `safe_head + maxSafeLag <= unsafe_head` 时，
sequencer 设置 `nextActionOK = false` 完全停产。这是二值（on/off）控制：要么全速
出块，要么完全停止，无中间状态。通过 CLI flag `--sequencer.max-safe-lag`
（`flags.go:253`）配置，通过 `driver.go:199` 在启动时注入。

**显式背压-batcher 侧**：DA Throttling via `miner_setMaxDASize`（`mantle-v2/
op-batcher/batcher/driver.go` throttlingLoop）——batcher 持续监控 `UnsafeDABytes()`
（`channel_manager.go:579-581`：pendingBlocks + openChannels + closedChannels），
通过 4 种控制器策略（Step/Linear/Quadratic/PID，`throttler/controller.go`）
计算 throttling intensity (0.0-1.0)，映射为 `maxTxSize` 和 `maxBlockSize`，
通过 RPC 调用 sequencer/builder 的 `miner_setMaxDASize` 限制每个 block 的 DA 数据量。
**⚠ 关键发现：Mantle 的 op-geth fork 已移除 `miner_setMaxDASize` RPC 方法**
（证据：`op-e2e/system/mantleda/throttling_enabled_test.go` 注释 "The
miner_setMaxDASize RPC method has been removed from op-geth"）。因此 DA throttling
在 Mantle 上**不可用**——启用 throttling（threshold > 0）会导致 batcher 检测到
缺失方法后关闭。`throttling_disabled_test.go` 确认默认运行模式为
`LowerThreshold = 0`（禁用 throttling loop）。这意味着 Mantle 的 batcher-sequencer
背压**仅依赖 SequencerMaxSafeLag 一种机制**——binary stall，无渐进控制。
Base 侧 `miner_setMaxDASize` 完整可用（`base/crates/execution/rpc/src/miner.rs`
`MinerApiExt`），且 `BaseDAConfig` atomic 由 payload builder 每 block 读取。
`op-conductor` 中的 `execution_miner_proxy.go` 也暴露了 `SetMaxDASize` 转发，
但同样因 op-geth 移除而失效。

**隐式背压-engine 侧**：`maxUnsafePayloadsMemory = 500MB`（`mantle-v2/op-node/
rollup/engine/engine_controller.go:42, 184`）—— P2P unsafe payload 队列有内存上限，
超限时丢弃最旧 payload。不是信号，是资源保护。

**隐式背压-queue backlog**：batcher channel_manager 按自身速率消费 blocks，
无显式信号回传 sequencer。5a 的单 pending channel 架构（R3）使得 batcher
处理速度受限时 block 在内存中累积，但 sequencer 不感知。

需要为两链分别绘制完整的 sequencer → engine → batcher → L1 → derivation →
safe head 的数据流图，标注每个背压信号的方向、触发条件和控制效果。

- **Priority**: high
- **Dependencies**: none

### item-2: Unsafe Span 控制与增长行为分析

分析 unsafe head 与 safe head 之间的差距（unsafe span）在正常和压力场景下的表现，
对比 Base 和 Mantle 的控制策略。

**Mantle 的 `SequencerMaxSafeLag` 分析**：
- 代码路径：`sequencer.go:449-454`，在 `onForkchoiceUpdate` 中检查
- 配置方式：`maxSafeLag atomic.Uint64`（`sequencer.go:89`），通过
  `SetMaxSafeLag()`（`sequencer.go:761-763`）设置
- 行为模式：binary stall——一旦触发，`nextActionOK = false` 直到 safe head
  追上后下次 FCU 重新允许（`sequencer.go:462-474`）
- 需要确认：Mantle mainnet 当前的 `maxSafeLag` 实际配置值（cli default vs deployed）

**Base 的 unsafe span 控制**：
- 初步代码搜索未在 `base/base` 仓库 `crates/consensus/service/src/actors/sequencer/`
  中发现 SequencerMaxSafeLag 等效的 binary stall 机制
- Base 使用 actor model（5 独立 tokio task），sequencer 与 derivation 天然解耦
- Base 的 unsafe span 控制 **完全依赖 DA throttling**（`DaThrottle` in
  `crates/batcher/core/src/throttle.rs`），通过渐进式降低 block DA size 来间接
  控制 span 增长，而非 stall sequencer——这是一个关键架构差异
- 需要验证：Base 是否在 spec 或其他配置中有未被代码搜索覆盖的 span 控制机制

**Unsafe span 行为建模**：
- 正常场景：sequencer 2s/block，batcher commit cadence（Base ~49s, Mantle ~448s），
  span 稳态值
- 压力场景：L1 拥堵 / blob fee 飙升 / batcher 重启 / DA 切换时 span 增长速率
- 极端场景：span 过大的风险——reorg 影响范围（unsafe chain 全部回滚）、derivation
  pipeline 内存压力、用户交易确认延迟
- DA Throttling 与 MaxSafeLag 的交互：当两种机制同时激活时的行为

- **Priority**: high
- **Dependencies**: item-1

### item-3: Batcher→Sequencer DA Throttling 控制器架构对比

深度对比 Base 和 Mantle 的 DA throttling 控制器实现。

**Mantle (Go) 控制器架构**：
- `ThrottleController`（`throttler/controller.go`）：pluggable strategy pattern，
  持有 `ThrottleStrategy` 接口 + `ThrottleConfig`
- 4 种策略：
  - `StepStrategy`（`step_strategy.go`）：binary on/off，低于 threshold 不限，
    高于立即全限
  - `LinearStrategy`（`linear_strategy.go`）：线性插值 `intensity = (load - lower) / (upper - lower)`
  - `QuadraticStrategy`（`quadratic_strategy.go`）：二次曲线，低负载温和、高负载激进
  - `PIDStrategy`（`pid_strategy.go`）：PID 控制器，experimental，P/I/D 三项独立调参
- 输入信号：`UnsafeDABytes()`（`channel_manager.go:579-581`）= 三层积压总和
- 输出控制：`maxTxSize` + `maxBlockSize` → `miner_setMaxDASize` RPC
- 运行时管理：支持通过 admin RPC 动态切换控制器类型、查询状态、重置
- 多端点并行：`throttlingLoop`（`driver.go:676`）为每个 endpoint 启动独立 goroutine

**Base (Rust) 控制器架构**：
- `DaThrottle`（`batcher/core/src/throttle.rs`）：支持 3 种模式——`Off`、`Step`（binary）、
  `Linear`（在 threshold 到 2× threshold 之间线性插值）。**无 Quadratic 或 PID**——
  比 Mantle 的 4 策略更简洁
- 默认配置（`bin/batcher/src/cli.rs`）：`threshold_bytes=1_000_000`（1MB），
  `block_size_lower_limit=2_000`，`block_size_upper_limit=130_000`，
  `tx_size_lower_limit=150`，`tx_size_upper_limit=20_000`
- `RpcThrottleClient`（`batcher/service/src/throttle.rs`）：实现 `ThrottleClient` trait，
  多端点 failover
- `BatchDriver`（`core/src/driver.rs`）通过 `tokio::select!` 主循环每轮调用
  `self.throttle.apply(self.pipeline.da_backlog_bytes())` 并条件性强制 blob DA
- 接收端：`miner_setMaxDASize` 写入 `BaseDAConfig` atomic（`execution/payload/src/config.rs`），
  payload builder 每 block 读取。另有 `miner_setGasLimit` RPC（`execution/rpc/src/miner.rs`）
  支持运行时 gas limit 调整——这为策略 D（自适应 gas limit）提供了现成 RPC 基础设施

**⚠ Mantle 关键状态**：DA throttling 在 Mantle 上因 `miner_setMaxDASize` RPC
被移除而**完全不可用**。op-batcher 中的 throttler 代码存在但处于休眠状态
（`LowerThreshold = 0`）。默认阈值配置为 `DefaultThrottleLowerThreshold = 3_200_000`
bytes，`DefaultThrottleUpperThreshold = 12_800_000` bytes，controller = "quadratic"
（`throttle_flags.go`），但这些从未生效。恢复 DA throttling 需要先在 Mantle
op-geth 中重新实现 `miner_setMaxDASize` RPC。

**关键对比维度**：控制粒度（binary vs continuous）、响应速度、overshoot 风险、
可观测性（metrics）、运行时可调性、Mantle 上的可用性（DA throttling 不可用 vs
Base 完整可用）、恢复 Mantle DA throttling 的工程路径。

- **Priority**: high
- **Dependencies**: item-1

### item-4: Batcher 吞吐量瓶颈的上游影响链

分析 batcher 慢导致的完整连锁反应，构建因果链模型。

**因果链 A — safe head 滞后**：
Batcher 慢 → DA 数据提交延迟 → verifier derivation pipeline 无法推进 →
safe head 滞后 → SequencerMaxSafeLag 触发 → sequencer stall → 用户感知 TPS = 0

**因果链 B — blob 积压与费用螺旋**：
Batcher 慢 → 未提交 block 在 channel_manager 中积压 → UnsafeDABytes 增长 →
DA throttling 触发 → 限制 block DA size → 但积压继续增长 → L1 拥堵时 blob fee
上升 → batcher tx 被延迟/替换 → 进一步降低提交频率 → 恶性循环
（op-batcher readme.md "Data Availability Backlog" section 明确描述此场景）

**因果链 C — 背压传导至用户**：
Batcher 慢 → DA throttling 限制 maxBlockSize → sequencer 每 block 可纳入的 DA
数据量下降 → 有效 gas limit 降低 → 用户感知 TPS 下降（但 sequencer 仍在出块，
只是每块更小）

**因果链 D — derivation 滞后**：
Batcher 慢 → DA 数据不完整 → derivation pipeline 等待（derive.NotEnoughData 状态）→
safe head 停滞 → 依赖 safe head 的服务（bridge finalization、fault proof）延迟

需要量化每条因果链的时间常数（从 batcher 慢到用户感知 TPS 下降的传导延迟）和
Mantle 当前各环节的容量余量。结合 5a 的结论（Mantle batcher ~448s commit cadence）
和 5b 的结论（DA 非约束，~1,480× 余量）评估：当 Mantle demand 增长到何种水平时，
各因果链会被激活。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

### item-5: "5k TPS" 语义精确分析与 Flashblocks 解耦

精确拆解 Base 的 "5k TPS" 声明，区分不同 TPS 度量，评估 Flashblocks
pre-confirmation 作为一种解耦策略的效果。

**TPS 度量层次**：
- **Pre-confirmation TPS（user-perceived）**：用户提交 tx 到看到 tx 出现在
  Flashblock sub-block 中的速率。Flashblocks 将 2s L2 block 拆为 8 × 250ms
  sub-block（Section 2），用户延迟从 ≤2s 压至 ≤250ms。
- **Sequencer-unsafe TPS**：sequencer 实际出块中纳入的 tx 数/秒，受 EL 执行速度
  和 gas limit 约束
- **DA-finalized TPS**：batcher 成功提交到 L1 且 derivation pipeline 确认的
  tx 数/秒，受 DA 带宽和 batcher 吞吐约束
- **L1-finalized TPS**：L1 block 本身 finalize 后的 TPS（~12min additional delay）

**Base "5k TPS" 归属分析**：
- 5b 证实 Base @ observed 153.03 B/UOP → DA ceiling ~942 TPS sustained
- 若声称 5k TPS，需 bytes/UOP 降至 ~29B（~5.3× 压缩改进）
- 可能指 pre-confirmation TPS（Flashblocks 层面用户可感知的速率）而非 DA-finalized
- 需要查找 Base 官方关于 "5k TPS" 的原始声明，确认其度量定义

**Flashblocks 解耦效果分析**：
- Flashblocks 不改变链最终 TPS（finalized gas/s），只改变用户延迟感知（Section 2 结论）
- 对 batcher-sequencer 背压的影响：Flashblocks 可能允许 sequencer 在 batcher 慢时
  继续提供 pre-confirmation，但 unsafe span 会持续增长
- DA throttling 与 Flashblocks 的交互：如果 throttling 限制了 block DA size，
  Flashblocks sub-block 是否也受限？

**Mantle 的对应情况**：
- Mantle reth 分支进度：`flashblocks/poc` 无实质代码，`feat/flashblocks-mantle-aware`
  仅覆盖 extra_data 解析（Section 2）
- Mantle 当前无 pre-confirmation 层，用户看到的 TPS 即 sequencer-unsafe TPS

- **Priority**: high
- **Dependencies**: item-2, item-4

### item-6: 4 种解耦改进策略可行性评估

系统评估 4 种解耦 batcher 和 sequencer 的策略，构建可行性矩阵。

**策略 A — 恢复 DA Throttling + 异步 Batcher（渐进解耦）**：
- 前提：**Mantle 当前完全缺失 DA throttling**——仅有 binary stall（MaxSafeLag）
  作为背压。这是最关键的架构缺口。
- 第一步：在 Mantle op-geth 中重新实现 `miner_setMaxDASize` RPC，使 op-batcher
  的 throttler 代码（4 种控制器策略）恢复功能
- 第二步：有了渐进 DA throttling 后，放宽 SequencerMaxSafeLag（设为较大值或禁用），
  用 DA throttling 的 continuous 控制替代 binary stall
- 预期效果：sequencer 持续出块（throttled 但不 stall），用户体验连续
- 风险：DA throttling 恢复后仍需测试控制器参数稳定性
- 实现复杂度：中——需要 op-geth 代码变更（实现 `miner_setMaxDASize`），
  但 op-batcher 侧的 throttler 代码已完整可用

**策略 B — 多 Batcher 实例（水平扩展）**：
- 思路：运行多个 batcher 实例并行消费 sequencer 的 unsafe blocks 并提交 DA
- 技术挑战：block 分配（哪个 batcher 负责哪些 blocks）、channel 去重
  （同一 block 不能被多个 batcher 提交）、nonce 管理（多 batcher 共享或独立 EOA）
- 先例分析：OP Stack 上游是否有多 batcher 设计？op-batcher readme 提到
  `(potentially multiple) sequencers`——是否暗示多 batcher 也在架构考虑中？
- 预期效果：线性扩展 batcher 吞吐，但需要额外的协调层
- 实现复杂度：高——需要新的 block 分配协议和 nonce 管理机制

**策略 C — Flashblocks 式解耦（pre-confirmation 层）**：
- 思路：引入 pre-confirmation 层吸收用户交互，batcher 异步最终确认
- 对 Mantle 的适用性：需要 rollup-boost + Flashblocks 完整移植
- 预期效果：用户感知 TPS 提升（延迟从 ~2s 降至 ~250ms），但 DA-finalized TPS
  不变；不解决 batcher 吞吐瓶颈本身
- 工程量评估：基于 Section 2 分析，Mantle reth 分支距离可用有较大差距
- 关键限制：Flashblocks 解耦的是用户感知延迟而非 DA 吞吐，不能替代 batcher
  吞吐优化

**策略 D — 自适应 Gas Limit**：
- 思路：sequencer 根据 batcher 积压情况动态调整 L2 gas limit，在 batcher 积压时
  降低 gas limit（减少每 block 的数据量），在 batcher 空闲时提高 gas limit
- 与 DA throttling 的关系：DA throttling 已实现类似功能（限制 maxBlockSize），
  但控制的是 DA 数据量而非 gas limit；gas limit 调整更直接地影响执行层吞吐
- 实现路径：可能通过扩展 `miner_setMaxDASize` 或新增 `miner_setGasLimit` RPC
- 预期效果：更精细的背压控制，避免 binary stall
- 与 gas-protocol-perf-config（Section 3）的关系：gas limit 调整需与 EIP-1559
  gas pricing 机制协调

每种策略需填写：TPS 改善预估、实现复杂度（人周）、风险等级、可逆性、
与其他课题的耦合、推荐优先级。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

### item-7: Mantle 优先推荐方案与路线图

综合 item-1 至 item-6 的分析，结合 5a 和 5b 的结论，给出针对 Mantle 的分阶段
推荐方案。

**阶段 0 — 参数调优（立即可执行，配合 5a Quick Wins）**：
- 配合 5a R1/R2b 调整 MaxPendingTransactions 和 TargetNumFrames
- 确认 SequencerMaxSafeLag 当前值（CLI default = 0 即禁用；若生产中已启用，确认阈值）
- 注意：DA throttling 参数调优**不可行**——`miner_setMaxDASize` RPC 在 op-geth 中
  不存在，任何非零 threshold 会导致 batcher 关闭

**阶段 1 — 恢复 DA Throttling（最高优先级的背压修复）**：
- **这是 Mantle 最关键的背压架构缺口**：当前仅有 binary stall 一种背压，
  无渐进控制能力
- 在 Mantle op-geth 中实现 `miner_setMaxDASize` RPC（参照 Base 的
  `execution/rpc/src/miner.rs` 中 `BaseDAConfig` atomic 模式，或 OP Stack 上游
  的 Go 实现）
- 恢复后使用 op-batcher 已有的 Quadratic controller（默认配置：
  lower=3.2MB, upper=12.8MB）
- 预期收益：从 binary stall → continuous throttle，用户体验显著改善

**阶段 2 — 架构解耦（中期，需要较大工程投入）**：
- 评估异步 batcher（策略 A）+ DA throttling 渐进控制的组合方案
- 评估 Flashblocks 移植（策略 C）的优先级和路径
- 明确各阶段的 TPS 预期改善与工程投入

**与其他课题的关系**：
- 5a Quick Wins 是阶段 0 的前置条件
- 5b 确认 DA 非约束 → 阶段 0/1 的 batcher 参数优化可独立于 DA 层改进
- Section 4 的 actor model 重构是阶段 2 的架构基础

需要为每个阶段给出：预计 TPS 改善范围、工程投入估算、风险和回滚策略、
成功度量指标。

- **Priority**: high
- **Dependencies**: item-4, item-5, item-6

### item-8: 风险分析与边界条件

对 item-6 和 item-7 中每种策略和推荐方案进行风险分析。

**Unsafe span 增长风险**：
- 放松 MaxSafeLag 后 unsafe span 的理论增长模型
- Reorg 场景下的影响范围：span = N blocks 时 reorg 影响 N 个 block 的用户 tx
- 内存压力：unsafe chain 累积对 op-node 内存的影响
  （`maxUnsafePayloadsMemory = 500MB` 保护是否足够？）
- 用户体验：长 unsafe span 下 tx 的确认状态语义（pre-confirmation ≠ safe ≠ finalized）

**DA 费用风险**：
- DA throttling 降低 block size 的同时，batcher 可能积压更多数据 → 后续 burst
  提交时面临更高 blob fee
- 5b 的 EIP-7918 blob fee 指数增长模型：+50% 持续 demand → ~7× in 5min

**控制器稳定性风险**：
- PID controller 的 overshoot / oscillation（throttling.md 多次警告 experimental）
- Step controller 的过度 throttling（throttling.md 明确警告 "too much throttling
  applied too quickly"）
- 多端点并行 throttling 的一致性（不同 endpoint 的 RPC 延迟差异）

**与 sequencer 架构的耦合**：
- Mantle 的单 event-loop 架构（Section 4）下，MaxSafeLag stall 会阻塞整个
  driver eventLoop → derivation 也被暂停 → safe head 更难追上 → 正反馈死锁风险
- Base 的 actor model 天然隔离此风险（derivation 在独立 task）

每种风险给出：发生概率、影响严重度、缓解措施、可观测指标。

- **Priority**: medium
- **Dependencies**: item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| code_evidence | 主要代码引用（仓库路径:行号、commit 锚点），覆盖 Base Rust 与 Mantle Go 两侧 | all |
| backpressure_type | 背压类型分类：explicit-sequencer / explicit-batcher / implicit-engine / implicit-queue | item-1 |
| trigger_condition | 背压触发条件（threshold 值、比较表达式、代码中的 if 条件） | item-1, item-2, item-3 |
| control_granularity | 控制粒度：binary（on/off stall）/ continuous（intensity 0.0-1.0）/ stepped | item-1, item-2, item-3 |
| signal_direction | 信号传递方向与参与组件（batcher→sequencer / sequencer→self / engine→queue） | item-1, item-4 |
| unsafe_span_metric | Unsafe span 数值（block count 或 time duration），区分正常/压力/极端场景 | item-2, item-8 |
| tps_definition | TPS 度量定义：pre-confirmation / sequencer-unsafe / DA-finalized / L1-finalized | item-5 |
| strategy_feasibility | 策略可行性评估：TPS 改善预估、实现复杂度（人周）、风险等级、可逆性 | item-6, item-7 |
| causal_chain | 因果链编号（A/B/C/D）与各环节时间常数 | item-4 |
| demand_activation_threshold | Mantle demand 增长到何种水平时该因果链/机制被激活（TPS 或 UnsafeDABytes） | item-4, item-8 |
| cross_topic_reference | 引用其他课题的结论（5a/5b/Section 2/Section 4），含具体 item 和数据点 | all |
| runtime_configuration_evidence | 区分四类证据：(1) cli_default — flag 源码默认值; (2) deployed_config — 实际部署配置; (3) observed_on_chain — 链上观测; (4) inferred — 分析师推断。MaxSafeLag 和 DA throttling 参数的 top 论断必须有 live 锚点，否则标注 "default-code-path risk" | item-1, item-2, item-3, item-7 |
| risk_severity | 风险严重度：critical / high / medium / low，含发生概率和影响评估 | item-8 |
| mitigation | 缓解措施与可观测指标 | item-8 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | Batcher-Sequencer 背压传递路径全景图：显示 sequencer → engine → batcher → L1 → derivation → safe head 的数据流，标注 4 种背压机制的位置、方向和触发条件，对比 Base 和 Mantle 两侧 | mermaid | item-1, item-4 |
| diag-2 | comparison | Unsafe span 控制策略对比图：左右对比 Base 和 Mantle 的 unsafe span 控制机制，包括 SequencerMaxSafeLag 的 binary stall 行为、DA throttling 的 continuous 控制、两者交互时序 | mermaid | item-2, item-3 |
| diag-3 | timeline | Unsafe span 增长时序图：正常场景 vs 压力场景（L1 拥堵/batcher 重启）下 unsafe span 的增长曲线，标注各背压机制的触发点和效果 | mermaid (sequence/gantt) | item-2, item-4 |
| diag-4 | matrix | 4 种解耦策略评估矩阵：行=策略（异步 batcher / 多 batcher / Flashblocks / 自适应 gas limit），列=维度（TPS 改善 / 复杂度 / 风险 / 可逆性 / 时间线） | mermaid | item-6, item-7 |
| diag-5 | flowchart | 解耦策略选择决策树（optional）：根据 Mantle 当前 demand 水平、工程资源、风险偏好等条件推荐策略路径 | mermaid | item-7 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | `mantle-v2/op-node/rollup/sequencing/sequencer.go` — SequencerMaxSafeLag 实现（`onForkchoiceUpdate` 中的 stall 逻辑、`SetMaxSafeLag` API、`maxSafeLag` atomic 字段），`flags.go` 中的 CLI flag 定义，`driver/config.go` 中的配置结构 | 3 |
| src-2 | code_analysis | `mantle-v2/op-batcher/batcher/` — DA throttling 完整实现链：`driver.go`（`throttlingLoop`、`blockLoadingLoop`、`sendToThrottlingLoop`、`singleEndpointThrottler`）、`throttler/controller.go`（`ThrottleController`、4 种策略）、`channel_manager.go`（`UnsafeDABytes()`） | 5 |
| src-3 | code_analysis | `base/base` 仓库 batcher throttling 实现：`crates/batcher/service/src/throttle.rs`（`RpcThrottleClient`）、`crates/batcher/core/` 中的 throttle 策略与 DA backlog 管理逻辑 | 3 |
| src-4 | code_analysis | `base/base` 仓库 sequencer unsafe span 控制：`crates/consensus/service/src/actors/sequencer/` 中是否有 MaxSafeLag 等效机制、engine actor 对 unsafe chain 的管理逻辑 | 2 |
| src-5 | code_analysis | `mantle-v2/op-node/rollup/engine/engine_controller.go` — `maxUnsafePayloadsMemory`、`PayloadsQueue` 实现、unsafe head 管理逻辑 | 2 |
| src-6 | cross_topic | 课题 5a（batcher-pipeline-architecture）final.md — R1/R2b/R3 瓶颈定位、on-chain 观测数据、§6.6 batcher-sequencer 耦合度量 | 1 |
| src-7 | cross_topic | 课题 5b（da-bandwidth-throughput-ceiling）final.md — DA 非约束结论（~1,480× 余量）、bytes/UOP 数据、EIP-7918 费用模型 | 1 |
| src-8 | cross_topic | Section 2（block-builder-flashblocks-throughput）final.md — Flashblocks pre-confirmation 机制、Mantle reth 分支进度、Base/Mantle 空块率和 gas 利用率对比 | 1 |
| src-9 | cross_topic | Section 4（sequencer-consensus-pipeline-perf）final.md — Base actor model vs Mantle event-bus 架构差异、sealingDuration、FCU 调用模式 | 1 |
| src-10 | official_docs | OP Stack 官方文档关于 unsafe/safe/finalized 语义、batcher 配置推荐（max-safe-lag、DA throttling）、Flashblocks 规范 | 2 |
| src-11 | on_chain_data | Base mainnet 和 Mantle mainnet 的 unsafe span 观测数据（如可获取）：safe head 与 unsafe head 的滞后量、batcher commit cadence（复用 5a on-chain 样本），用于校准 item-2 的行为模型 | 1 (best-effort) |
| src-12 | deployed_config | Mantle 当前 sequencer 和 batcher 的实际部署配置：`--sequencer.max-safe-lag` 值、DA throttling threshold 和 controller type、是否启用 throttling（即 threshold > 0）。若不可获取，所有 MaxSafeLag 和 throttling 论断必须标注 "default-code-path risk" | 1 (best-effort) |
