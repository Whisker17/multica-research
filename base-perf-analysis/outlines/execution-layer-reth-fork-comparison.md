---
topic: "执行层性能架构对比：Base Reth Fork vs Mantle Reth Fork（三方对比）"
project_slug: base-perf-analysis
topic_slug: execution-layer-reth-fork-comparison
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: base-perf-analysis/outlines/execution-layer-reth-fork-comparison.md
  draft: base-perf-analysis/research-sections/execution-layer-reth-fork-comparison/drafts/round-{n}.md
  final: base-perf-analysis/research-sections/execution-layer-reth-fork-comparison/final.md
  index: base-perf-analysis/research-sections/_index.md

scope: |
  三方对比 Base Rust 执行层（base-reth-node）、Mantle Go 执行层（op-geth 生产基线）与
  Mantle Rust 执行层（mantle-elysium，未来方向）在性能优化上的设计差异。以 Mantle op-geth
  作为可量化的生产性能基线，定位 Mantle 执行层在两栈上的具体性能瓶颈。覆盖：
  (1) 三方相对上游的修改清单与版本基线差（paradigmxyz/reth Tier A；ethereum-optimism/op-geth Tier G）；
  (2) Base Rust 栈的关键性能特性（flashblocks、engine-tree cached execution、custom EVM factory）；
  (3) Mantle op-geth Go 栈的定制改动（MetaTx、TokenRatio L1 cost、MNT 代币模型、Arsia 升级）；
  (4) Mantle Rust 栈（mantle-elysium）的 overlay 层、外部依赖补丁与当前实现成熟度；
  (5) 存储层（MDBX vs LevelDB/pathdb）、EVM 执行（REVM vs go-ethereum EVM）、缓存策略的
  跨栈对比；(6) Go runtime（GC/goroutine 调度）对执行性能的系统性影响；
  (7) Go 栈 → Rust 栈迁移的预期性能提升量化（分执行层子系统估算）；
  (8) Mantle 改进建议（分别标注 Go 栈适用和 Rust 栈适用，按优先级排序）。

audience: |
  Mantle / Base 性能优化方向的协议工程师与执行层（EL）开发者；
  Multica 研究 squad 内部下游 Research Agent；OP Stack 生态中关注从 op-geth 迁移到
  reth-based EL 的运营者；项目内部决策者评估"reth fork 改造"作为提升 TPS 的可行路径。
  读者熟悉 EVM/MDBX/reth pipeline 基础，但不必了解三个实现的具体定制细节。

expected_output: |
  - 三方执行层架构差异矩阵（Base reth / Mantle op-geth / Mantle reth，模块级别）
  - 性能关键改动清单（每项标注预估 TPS 影响，区分三方，标注归属 Tier）
  - 上游版本基线对比表（reth commit/tag、op-geth commit、op-reth 版本）
  - 存储层配置对比表（MDBX vs LevelDB/pathdb，含 map_size、page_size、sync_mode、缓存参数）
  - EVM 执行流程对比图（三方，Mermaid）
  - Go 栈 → Rust 栈迁移的预期性能提升估算（分子系统量化）
  - MetaTx 与 TokenRatio L1 cost 对 op-geth 执行性能的 overhead 量化
  - 针对 Mantle 的至少 5 条改进建议（按优先级排序，明确标注 Go 栈适用 / Rust 栈适用）
  - 至少 2 个 Mermaid 图表（架构对比 / EVM pipeline / 迁移增益估算任选）

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-22T12:00:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-22T19:50:00+08:00"
  rerun_reason: "用户于 2026-05-22 更新 issue 要求三方对比，新增 Mantle op-geth（Go 生产栈）作为性能基线"

attribution_tiers:
  description: |
    所有性能相关的代码、改动、配置与 TPS 影响声明，必须显式标注其归属层级（Tier A–F）。
    无法明确归属的声明必须标记为 [UNATTRIBUTED] 并在 Patch Log 中记录待补证据。
  tiers:
    - id: A
      name: 上游 reth（Rust baseline）
      source_repo: paradigmxyz/reth
      note: Rust EL 中立 baseline；同时供 Base reth 与 Mantle reth 比较
    - id: B
      name: OP 继承层
      source_repo: ethereum-optimism/optimism (op-reth/v2.2.1 或 Mantle Cargo.toml 引用的精确 source commit)
      note: 由 OP Stack 引入、对 Base 与 Mantle Rust fork 共有的 op-reth 行为
    - id: C
      name: Base overlay（Rust 栈）
      source_repo: base/base (crates/execution)
      note: Base 在 OP 继承层之上的增量改动（flashblocks、engine-tree、custom EVM factory 等）
    - id: D
      name: Mantle Rust overlay
      source_repo: mantle-xyz/reth (mantle-elysium branch, op-reth/ + mantle-reth/ workspaces)
      note: Mantle 在 OP 继承层之上的增量 Rust 改动
    - id: E
      name: Mantle 外部依赖补丁
      source_repo: mantle-xyz/revm, mantle-xyz/evm, mantlenetworkio/mantle-v2 (op-alloy/alloy-op-evm)
      note: 通过 Cargo [patch.crates-io] 注入的 Mantle fork；token_ratio trait、fee model 等
    - id: F
      name: Mantle Go 生产栈（op-geth 基线）
      source_repo: mantlenetworkio/op-geth
      note: Mantle 当前生产 Go 执行层；相对上游 op-geth 的定制改动（MetaTx、TokenRatio、Arsia 升级等）；作为 Go→Rust 迁移的性能基线
---

# Research Outline: 执行层性能架构对比：Base Reth Fork vs Mantle Reth Fork（三方对比）

## 三方对比框架

本课题以 **Mantle op-geth（Tier F，Go 生产基线）** 作为锚点，同时对比：

| 实现 | 仓库 | 语言 | 角色 |
|------|------|------|------|
| Base Rust 栈 | `base/base` → `crates/execution` | Rust | 高性能参考对象 |
| Mantle Go 栈 | `mantlenetworkio/op-geth` | Go | **当前生产基线（Tier F）** |
| Mantle Rust 栈 | `mantle-xyz/reth` → `mantle-elysium` 分支 | Rust | 未来迁移目标 |

所有 TPS / gas-throughput 估算必须以 Mantle op-geth 的生产实测或代码路径分析作为锚定参照，
而非单纯做两个 Rust fork 的理论对比。

## Items

### item-1: 三方版本基线与 fork 演化轨迹

确认三个实现当前各自的上游版本 pin：

- **Base reth**（Tier C）：从 `base/base` `Cargo.toml` 读取 `paradigmxyz/reth tag = "v1.11.4"`，
  确认 op-reth 继承层版本（Tier B），梳理 Base overlay 的 fork 演化策略（rebase/merge/backport）。
- **Mantle reth**（Tier D/E）：从 `mantle-xyz/reth` `Cargo.toml` 读取 `paradigmxyz/reth rev = 88505c7f`
  (= v2.2.0，aligned with op-reth/v2.2.1) 与 `ethereum-optimism/optimism op-reth/v2.2.1` 对应关系，
  梳理 Mantle Rust 栈的 op-reth 源码引入方式（作为 workspace 成员 `op-reth/`）。
- **Mantle op-geth**（Tier F）：确认 `mantlenetworkio/op-geth` 相对上游 `ethereum-optimism/op-geth`
  的 base commit 与滞后量（latest: fix inner audit #162，含 Arsia 升级）。

量化各实现相对 EL 关键性能 PR 的同步状态。特别标注：Base reth 使用 reth tag `v1.11.4` 而
Mantle reth 使用 rev `88505c7f`（op-reth v2.2.0 equivalent）——判断两者 reth upstream 版本的
实际差距（reth v1.x 与 v2.x 版本线关系）以及对性能的影响方向。

**强制要求**：Mantle Rust 栈需同时对比 Tier A（reth）和 Tier B（op-reth）；
Mantle Go 栈（Tier F）需与上游 op-geth 单独对比，不得与 Rust baseline 混用。

- **Priority**: high
- **Dependencies**: none
- **Required investigation_fields**:
  - `tier_a_pin_base` / `tier_a_pin_mantle_reth`: reth tag/rev for each Rust fork
  - `tier_b_pin`: op-reth source for each Rust fork
  - `base_reth_pin`: must checkout `base/base` at tag `v1.11.4` (or the HEAD tag at project start if v1.11.4 is unavailable, but the pin must be recorded)
  - `mantle_reth_pin`: must checkout `mantle-xyz/reth` at commit `88505c7f` (mantle-elysium branch, ≈ v2.2.0)
  - `tier_f_upstream_delta`: Mantle op-geth commit delta vs ethereum-optimism/op-geth HEAD
  - `version_gap_perf_implication`: 版本差距对性能的预期影响方向

### item-2: Mantle op-geth 定制改动清单与性能特征（Go 生产基线分析）

作为全课题的性能锚点，深度分析 `mantlenetworkio/op-geth`（Tier F）相对上游 op-geth 的
全部定制改动。重点模块：

1. **MetaTx 系统**（`core/types/meta_transaction.go`，已确认存在）：
   - MetaTxParams 结构（ExpireHeight、SponsorPercent、GasFeeSponsor、V/R/S 签名）
   - `MetaTxCheck`：32 字节前缀 `0x00...4D616E746C654D6574615478507265666978` 检查，在每笔 EIP-1559
     tx 的 `state_transition.go` 热路径中调用
   - `DecodeMetaTxParams` / `CalculateSponsorPercentAmount`：MetaTx 启用时的额外路径
   - 量化每笔交易的额外 CPU overhead（热路径仅字节比较 ~ns；MetaTx 激活时 RLP 解码 + sig 验证 ~μs）

2. **TokenRatio L1 cost 模型**（`core/types/rollup_cost.go`，已确认存在）：
   - `TokenRatioSlot`（slot 0）用于 MNT/ETH 换算
   - `ArsiaL1AttributesSelector = {0x49, 0xe7, 0x23, 0x83}`（Mantle 特有，区别于 Ecotone/Isthmus）
   - `OperatorCostFunc` 与 `OperatorFeeParamsSlot`（slot 8）
   - `TokenRatio` 对每笔非 Deposit tx 的 L1 cost 计算路径：额外 SLOAD + big.Int 乘除

3. **MNT/ETH 双代币 state_transition**（`core/state_transition.go`，1272 行）：
   - `BVM_ETH_ADDR`、`LEGACY_ERC20_MNT` 对 balance 读写热路径的影响
   - L2ProxyAdmin owner 转移逻辑
   - 预确认机制（`core/miner_preconf.go`、`core/preconf_checker.go`）

4. **Go runtime 影响**：
   - GC 停顿（concurrent mark-sweep STW <1ms）在 block execution 中的插入点
   - goroutine 调度开销 vs Rust tokio 在 IO-bound 存储访问上的差异
   - heap allocation 模式（tx processing 中频繁分配 state 对象、receipt）

- **Priority**: high
- **Dependencies**: item-1
- **Required investigation_fields**:
  - `metatx_hot_path_coverage`: MetaTx 检查是否覆盖所有非 Deposit tx
  - `token_ratio_per_tx_extra_sloads`: TokenRatio 计算的额外 SLOAD 次数
  - `go_gc_throughput_overhead_pct`: GC 对 CPU throughput 损耗估算（%）
  - `mantle_op_geth_current_tps`: 已知或可推断的当前生产 TPS

### item-3: Base reth 定制改动清单与核心性能特性

梳理 Base Rust 栈（Tier C）相对 OP 继承层（Tier B）的全部定制改动，重点覆盖：

1. **Flashblocks 系统**（`crates/execution/flashblocks/`，已确认模块结构）：
   - StateProcessor、PendingStateBuilder（sub-block 流式构造）
   - 并行 sender recovery（`sender_recovery_duration` histogram metric，
     `flashblocks-node/benches/sender_recovery.rs` 基准测试）
   - FlashblocksCache、PendingBlocks 内存结构
   - 对有效 TPS（用户感知 latency）vs 执行吞吐（gas/s）的分离影响

2. **Engine-tree cached execution**（`crates/execution/engine-tree/src/cached_execution.rs`）：
   - 缓存执行结果的粒度与命中场景（payload construction re-execution 优化）

3. **Custom EVM Factory**（`BaseEvmFactory` + `base_common_evm::BaseBlockExecutorFactory`）：
   - `BaseBlockExecutionCtx`、`BaseSpecId`（超出标准 OP spec，覆盖到 Jovian 升级）
   - L1 info 解析路径：parse_l1_info_tx_jovian（Base 独有 selector `3db6be2b`）
   - `BaseStorage = EmptyBodyStorage`（body 不落盘，减少 write amplification）

4. **Metering 子系统**（`crates/execution/metering/`）：
   - block 级 gas metering 并行路径（`block.rs`、`types.rs`）

5. **TX pool 优化**（`crates/execution/txpool/`）：
   - `BaseOrdering`、`TimestampedTransaction` 设计

- **Priority**: high
- **Dependencies**: item-1
- **Required investigation_fields**:
  - `flashblocks_parallel_sender_recovery_speedup`: sender recovery 并行化的估算加速比
  - `cached_execution_use_cases`: cached execution 的触发条件与命中率估算
  - `base_jovian_l1_selector_impact`: Jovian L1 info 解析对 L1 cost 热路径的影响

### item-4: Mantle reth（mantle-elysium）改动清单与实现成熟度

梳理 Mantle Rust 栈（Tier D/E）定制改动，并评估 `mantle-elysium` 分支的实现成熟度：

1. **Workspace 架构**（`op-reth/` + `mantle-reth/`）：
   - `op-reth/`：从 `ethereum-optimism/optimism op-reth/v2.2.1` 作为 workspace 成员引入
   - `mantle-reth/`：trait override 层，当前大部分 crates 已注释（"Uncomment as crates are created"）
   - 已实装 vs 规划中的 crates 比例（影响当前 Mantle reth 是否实际能运行）

2. **外部依赖补丁**（Tier E）：
   - `mantle-xyz/revm@mantle-elysium`：Mantle fee model patches（token_ratio trait）
   - `mantle-xyz/evm@mantle-v0.34.0`：`token_ratio` trait method on `alloy-evm`
   - `mantlenetworkio/mantle-v2@rust/upgrade-develop-20260511`：
     `alloy-op-evm`、`alloy-op-hardforks`、`op-alloy` Mantle 定制版本
   - 这些 patch 对 L1 cost 计算热路径的影响

3. **L1 cost 实现**（`op-reth/crates/evm/src/l1.rs`）：
   - 当前实现是否已集成 `TokenRatioSlot`（Tier E revm 补丁）
   - 与 op-geth `rollup_cost.go` TokenRatio 逻辑的对等性

4. **上游 reth 功能差距**：
   - 相对 Base reth（reth v1.11.4）的功能差距
   - 是否缺失特定性能优化（MDBX tuning、trie 优化）

- **Priority**: high
- **Dependencies**: item-1, item-2
- **Required investigation_fields**:
  - `mantle_reth_crate_completion_ratio`: mantle-reth/ workspace 已实装 crates 比例
  - `tier_e_token_ratio_integration_status`: Tier E revm/evm patch 中 token_ratio 的集成状态
  - `l1_cost_parity_with_opgeth`: Mantle reth L1 cost 与 op-geth TokenRatio 的功能对等度

### item-5: 存储层架构三方对比

1. **数据库引擎**：
   - Base reth / Mantle reth：MDBX（通过 `reth-db`）
   - Mantle op-geth：Go `ethdb` 接口（确认实际后端：pebble/leveldb/mdbx）
   - MDBX vs Go DB 的 IOPS、写放大、p99 读延迟已知差距

2. **Rust forks MDBX 配置对比**：
   - 从各自代码提取：`map_size`、`page_size`、`sync_mode`、`Geometry`、`env_flags`
   - Base：`BaseStorage = EmptyBodyStorage`（body 不落盘）的存储影响
   - Mantle reth：是否继承上游 reth/op-reth 的默认 MDBX 配置

3. **State trie 架构**：
   - Base reth：`crates/execution/trie/`（是否启用 path-based trie）
   - Mantle reth：`op-reth/crates/trie/`（含 store_v2 cursor）
   - Mantle op-geth：pathdb vs hashdb，snapshot layer

4. **缓存配置**：
   - state / block / receipt / trie cache 容量（各实现默认值）
   - Go GC 对大 heap cache 的 pressure 影响

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4
- **Required investigation_fields**:
  - `mdbx_config_base` / `mdbx_config_mantle_reth`: 从代码提取的 MDBX 配置
  - `opgeth_db_backend`: Mantle op-geth 实际数据库后端
  - `storage_iops_gap_estimate`: Mantle op-geth vs Mantle reth 存储 IOPS 差距估算

### item-6: EVM 执行引擎三方对比

1. **执行引擎**：
   - Base reth / Mantle reth：REVM（Rust）
   - Mantle op-geth：go-ethereum EVM（Go）
   - 公开 benchmark 支持的 REVM vs go-EVM 执行速度比

2. **并行 EVM 能力**：
   - Base reth：flashblocks 并行 sender recovery（已确认）；tx-level 并行执行状态（待调查）
   - Mantle reth：op-reth v2.2.0 的并行执行状态
   - Mantle op-geth：顺序执行，无并行 EVM

3. **REVM 版本与自定义扩展**：
   - Base：上游 reth v1.11.4 内含的 REVM 版本
   - Mantle：`mantle-xyz/revm@mantle-elysium`（Tier E patch）
   - 两个 Rust fork 的 REVM 版本差异；Mantle patch 是否引入性能回退

4. **Precompiles**：
   - Base：`BaseEvmFactory` + `activation_admin_address` 逻辑（是否注册额外 precompiles）
   - Mantle：Tier E revm patch 的 precompile 配置
   - op-geth：Go EVM precompile 配置

- **Priority**: high
- **Dependencies**: item-3, item-4
- **Required investigation_fields**:
  - `revm_vs_goevm_speedup_ratio`: 公开 benchmark 支持的执行速度倍数
  - `parallel_evm_status_all_three`: 三方并行 EVM 状态
  - `mantle_revm_patch_regression_risk`: Mantle revm fork 是否引入性能回退风险

### item-7: Go runtime vs Rust 执行模型系统性影响与迁移增益量化

1. **GC 影响**（Go 栈）：
   - GC（concurrent tri-color mark-sweep）典型 STW pause（<1ms）对 block execution p99 latency 影响
   - 高 TPS 下 heap 快速增长时 GC 频率与 throughput 损耗（typical: 5-15% CPU）
   - Rust RAII / 无 GC 内存模型对比

2. **goroutine vs tokio async**：
   - goroutine context switch（~1μs）在 IO-bound 存储访问场景下的影响
   - Rust tokio work-stealing scheduler 在异步 MDBX 读写上的优势

3. **内存分配**：
   - op-geth tx 处理热路径的 heap allocation 频率（state 对象、receipt 构建）
   - Rust 栈分配与 arena 优化对相同路径的内存效率

4. **迁移增益分解估算**：
   - EVM 执行层增益（Go EVM → REVM）：基于公开 benchmark
   - 存储层增益（LevelDB/pebble → MDBX）：基于存储 IOPS 差距
   - 系统开销减少（GC → 无 GC）：基于 Go GC overhead 文档
   - 合成估算：明确非加性假设，给出 range 而非点估算

- **Priority**: high
- **Dependencies**: item-2, item-5, item-6
- **Required investigation_fields**:
  - `go_gc_throughput_overhead_pct`: GC CPU overhead 百分比（inferred）
  - `go_runtime_observables`: instrumentation entry points for GC evidence - identify GODEBUG/pprof/runtime.ReadMemStats call sites in mantlenetworkio/op-geth; locate trie batch commit sizes in core/state/statedb.go and trie/database.go; locate sync.Mutex / sync.RWMutex hot paths in state object caching and txpool; derive heap allocation rates from state object lifecycle (New/Copy/Finalise)
  - `gc_pause_proxy`: if live profiling is unavailable, estimate GC pressure via (a) total heap allocated per block × Go GC trigger fraction, (b) trie node object count × avg node size, (c) any existing issue/PR in mantlenetworkio/op-geth referencing GC tuning (GOGC, ballast, etc.); all proxies must be labeled `inferred`
  - `revm_vs_goevm_speedup_multiplier`: EVM 层迁移增益倍数
  - `storage_migration_gain_estimate`: 存储层迁移独立增益
  - `migration_gain_decomposition`: EVM 层 / 存储层 / GC 消除 的分解量化

### item-8: MetaTx 与 TokenRatio overhead 精确量化

1. **MetaTx overhead**（主要在 Tier F）：
   - `MetaTxCheck`（`core/types/meta_transaction.go`）每笔 EIP-1559 tx 热路径调用
   - MetaTx 未激活路径：32 字节前缀 `bytes.Equal` 比较（~ns，可忽略）
   - MetaTx 激活路径：`DecodeMetaTxParams`（RLP decode）+ `CalculateSponsorPercentAmount`
     （big.Int mul/div）+ 额外 ECDSA sig 验证（~μs 量级）
   - MetaTx 功能在 Mantle reth（Tier D/E）的当前移植状态

2. **TokenRatio / MNT L1 cost overhead**（Tier F 和 Tier E）：
   - op-geth（Tier F）：每笔非 Deposit tx 执行 `TokenRatioSlot` SLOAD + `Decimals` 除法
   - Arsia 升级后：`ArsiaL1AttributesSelector` 新解析路径（178 字节，vs Ecotone 标准）
   - Mantle reth（Tier E）：`mantle-xyz/evm` 的 `token_ratio` trait method 调用链等价分析
   - 与 Base L1 cost（无 MNT token，单纯 ETH）的开销差

3. **OperatorFee 机制**（`OperatorFeeParamsSlot` slot 8）：
   - 是否在所有 tx 触发额外 SLOAD；与上游 OP Stack IsthmusOperatorFee 的关系

- **Priority**: high
- **Dependencies**: item-2, item-4
- **Required investigation_fields**:
  - `metatx_per_tx_overhead_ns`: per-tx CPU cost of MetaTxCheck when MetaTx is NOT active (baseline path through meta_transaction.go); label `inferred` unless live profiling is cited
  - `metatx_active_us_path`: per-tx CPU cost when MetaTx IS active (full MetaTxParams decode + fee recalculation); label `inferred` unless live profiling is cited
  - `token_ratio_per_tx_extra_sloads`: count of extra SLOAD operations per tx for TokenRatioSlot / OperatorFeeParamsSlot / ArsiaL1AttributesSelector reads in rollup_cost.go
  - `token_ratio_bigint_cost`: estimate of big.Int or decimal cost for TokenRatio division/multiplication per tx vs Base ETH-only L1 cost path; label `inferred`
  - `injection_points_go`: exact file:line references in mantlenetworkio/op-geth where MetaTx check and token_ratio computation are injected into the tx execution hot path
  - `injection_points_rust`: if applicable, equivalent injection points in mantle-xyz/reth (Tier D/E); mark `[NOT_YET_IMPLEMENTED]` if the Mantle reth fork has not yet ported MetaTx
  - `evidence_tier`: A-F attribution tier for each field; any field without a determinable tier must be marked `[UNATTRIBUTED]`
  - `mantle_vs_base_l1cost_overhead_gap`: Mantle vs Base L1 cost 路径 overhead 差

### item-9: Pipeline 设计与执行/验证阶段并行度（三方对比）

1. **Rust forks pipeline 拓扑**：
   - 标准 reth pipeline 阶段（Headers → Bodies → Senders → Execution → MerkleTrie → History → Finish）
   - Base：`engine-tree` 对 live execution 路径的定制（cached_execution、validator）
   - Mantle reth：op-reth v2.2.1 pipeline 设计，是否继承 reth v2.x pipeline 重构

2. **op-geth block 处理路径**：
   - `core/blockchain.go` insertChain 路径顺序执行阶段
   - `preconf_checker.go` 对 block 验证性能的影响
   - `pending.go` 与 payload building 并行度

3. **对 sustained TPS 的影响分类**：
   - first-order 影响（在线 sequencer）vs sync-time 优化

- **Priority**: medium
- **Dependencies**: item-3, item-4, item-5
- **Required investigation_fields**:
  - `base_engine_tree_live_sync_split`: Base engine-tree 是否实现在线/历史路径拆分
  - `mantle_reth_pipeline_stage_count`: Mantle reth pipeline 阶段数

### item-10: 量化性能对比矩阵（三方，以 Mantle op-geth 为 baseline）

以 Mantle op-geth（Tier F）= 1x 为基准，构建三方可量化的执行层性能对比矩阵：

| 指标 | Mantle op-geth (F) | Mantle reth (D/E) | Base reth (C) | 证据等级 |
|------|--------------------|-------------------|---------------|---------|
| EVM 执行速度 | 1x | estimated ~2-5x | estimated ~3-8x | inferred |
| 存储 IOPS 效率 | 1x（Go DB） | estimated ~3-5x（MDBX） | estimated ~3-5x（MDBX） | inferred |
| GC/内存 overhead | ~5-15% CPU | ~0% | ~0% | reported |
| MetaTx per-tx overhead | ~Xns/μs（hot path） | N/A（待移植） | N/A | inferred |
| TokenRatio per-tx overhead | 1 extra SLOAD | TBD | 0 | inferred |
| Go→Rust 迁移预期总增益 | baseline | TBD（分解量化） | ref | inferred |

**测量方法学护栏（强制）**：

1. **非加性原则**：所有估算默认不可相加，仅当改动作用于正交热路径时允许合成。
2. **同一基准前提**：跨实现对比必须声明 block gas limit、tx mix、硬件 spec、同步阶段。
3. **分母标签**：每条声明使用单一分母（`gas/s`、`tx/s`、`per-block CPU (ms/block)`、`IOPS`）
   并显式标注；禁止混用 throughput 与 latency。
4. **Tier 归属同步**：每条声明携带分母标签 + 归属 Tier（A/B/C/D/E/F）；缺一即 [UNATTRIBUTED]。
5. **Go→Rust 迁移增益分解**：必须将 EVM 执行引擎替换（Go→REVM）与存储引擎替换（Go DB→MDBX）
   分离量化，禁止合并声明总增益而不标注各子系统贡献。

- **Priority**: high
- **Dependencies**: item-5, item-6, item-7, item-8, item-9
- **Required investigation_fields**:
  - `denominator`: gas/s | tx/s | per-block CPU | IOPS | latency_p50 | latency_p99
  - `measurement_scenario`: block gas limit / tx mix / hardware / sync mode 四元组
  - `additivity_class`: additive_within_scenario | non_additive | upper_bound_only
  - `attribution_tier`: A/B/C/D/E/F（与 item-2~4 一致）
  - `migration_gain_decomposition`: EVM 层 / 存储层 / GC 消除 的增益分解

### item-11: 针对 Mantle 的改进建议（分 Go 栈与 Rust 栈，按优先级排序）

基于 item-1 ~ item-10 的差距清单，产出至少 5 条针对 Mantle 的改进建议。每条标注：

- 来源差距编号（item-x）
- 预期 TPS / gas-throughput 提升（upper-bound，带分母标签）
- 改造成本（人月估算 / 风险等级：低/中/高）
- 前置依赖（上游版本同步、OP Stack 升级等）
- 适用栈：`[Go 栈]` / `[Rust 栈]` / `[Go+Rust 栈]`
- 与其他 Wave 的互斥/协同关系

示例方向（需代码证据验证后列入，标注为 [TENTATIVE]）：
1. [TENTATIVE] **MetaTx 热路径优化**（`[Go 栈]`）：MetaTxCheck 惰性执行，仅在 tx data > 32B 时触发
2. [TENTATIVE] **TokenRatio block 级缓存**（`[Go+Rust 栈]`）：在 block 内缓存 TokenRatio，避免每 tx 重复 SLOAD
3. [TENTATIVE] **Mantle reth 上游 patch 对齐**（`[Rust 栈]`）：评估对齐 Base reth reth v1.11.4 关键 patch
4. [TENTATIVE] **mantle-reth/ overlay 实装**（`[Rust 栈]`）：推进 mantle-reth/crates/ 规划 crates 的实装
5. [TENTATIVE] **并行 sender recovery**（`[Rust 栈]`）：参考 Base flashblocks 并行 sender recovery 实现

- **Priority**: high
- **Dependencies**: item-1 ~ item-10

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| upstream_baseline | 上游版本 pin（reth tag/commit、op-geth commit），各实现滞后量 | item-1, item-3, item-4, item-9 |
| code_locations | 关键文件路径与行号引用（path:line），必须可点击复核 | all |
| modification_summary | 相对上游的改动摘要（模块、行数量级、是否触及热路径） | item-2, item-3, item-4, item-8 |
| perf_impact_estimate | 改动/差距对执行层 gas-throughput 或 TPS 的量化影响（证据等级：measured/reported/inferred） | item-2 ~ item-10 |
| stack_applicability | 建议或改动适用栈（Go 栈 / Rust 栈 / Go+Rust 栈） | item-11 |
| risk_and_correctness | 改动的正确性保证、冲突/回滚路径、潜在 consensus break 风险 | item-6, item-9 |
| config_parameters | 配置项（key、Base 取值、Mantle reth 取值、Mantle op-geth 取值、上游默认值） | item-5, item-9 |
| benchmark_evidence | 公开 benchmark 或链上数据（Base Azul 博客、reth issues、Go vs Rust EVM benchmark） | item-10 |
| recommendation_metadata | 建议的成本/风险/收益评分，依赖关系，适用栈，是否需要 hardfork | item-11 |
| cross_topic_dependencies | 与其他研究主题的接口/重叠（block-builder-flashblocks-throughput、gas-protocol-perf-config） | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | **三方执行层架构对比图**：三列并列展示 Base reth（crates/execution）、Mantle op-geth（core/）、Mantle reth（op-reth/ + mantle-reth/）的模块拓扑；颜色/形状区分 Tier 归属（A/B/C/D/E/F）；高亮性能关键模块（flashblocks、MetaTx、TokenRatio、engine-tree） | mermaid | item-2, item-3, item-4 |
| diag-2 | flow | **EVM 执行 pipeline 三方对比图**：三轨并列（Base reth / Mantle op-geth / Mantle reth），从 tx fetch → sender recovery → state warm-up → execute → state-root → DB commit；标注并行/串行状态、每阶段估算耗时、GC 停顿点（op-geth）、flashblocks 插入点（Base）、MetaTx/TokenRatio 注入点（Mantle） | mermaid | item-6, item-7, item-9 |
| diag-3 | architecture | **存储层架构三方对比图**：EVM hot path → state cache → trie cache → DB engine（MDBX vs Go DB）层次结构；标注三方 cache 大小与 DB flags；高亮 MDBX vs Go DB 的写路径差异 | mermaid | item-5 |
| diag-4 | quadrant | **改进建议优先级矩阵**：X 轴"改造成本"（低→高），Y 轴"预期 TPS 提升"（低→高）；item-11 建议落点到四象限；用图例区分 Go 栈建议 vs Rust 栈建议 | mermaid | item-11 |

## Source Requirements

Primary implementation checkout commands (required; use `multica repo checkout`, not generic git clones):

- `multica repo checkout https://github.com/base/base` (Tier C — Base reth; pin to v1.11.4 per P1)
- `multica repo checkout https://github.com/mantle-xyz/reth --ref mantle-elysium` (Tier D — Mantle reth; pin to 88505c7f per P1)
- `multica repo checkout https://github.com/mantlenetworkio/op-geth` (Tier F — Mantle op-geth Go production baseline)

Attribution baseline notes (not Multica checkout commands unless later added to workspace resources):

- upstream `paradigmxyz/reth` (Tier A baseline) — note the specific tag/rev used by Base and Mantle respectively
- `ethereum-optimism/optimism` op-reth/v2.2.1 (Tier B baseline) — note the exact source commit pinned by Mantle Cargo.toml
- upstream `op-geth`/`go-ethereum` (Tier F baseline) — for attributing Mantle op-geth customizations vs inherited behavior

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | `base/base` 仓库 `crates/execution` 全目录代码扫描，附 commit SHA 与文件:行号引用；checkout command: `multica repo checkout https://github.com/base/base`; pinned version: v1.11.4 (record actual checkout SHA) | 1 |
| src-2 | code_analysis | `mantle-xyz/reth` 仓库 `mantle-elysium` 分支代码扫描；checkout command: `multica repo checkout https://github.com/mantle-xyz/reth --ref mantle-elysium`; pinned commit: 88505c7f on mantle-elysium; record actual checkout SHA | 1 |
| src-3 | code_analysis | `mantlenetworkio/op-geth` 仓库代码扫描，重点 `core/types/meta_transaction.go`、`core/types/rollup_cost.go`、`core/state_transition.go`; checkout command: `multica repo checkout https://github.com/mantlenetworkio/op-geth` | 1 |
| src-4 | code_analysis | 上游 `paradigmxyz/reth` 作为 Tier A baseline；记录 Base 与 Mantle 分别使用的具体 tag/rev（通过本地依赖 pin 对比，不作为 Multica checkout command） | 1 |
| src-4b | code_analysis | **Tier B baseline（Primary，必需）**：`ethereum-optimism/optimism` op-reth/v2.2.1 作为 OP 继承层 baseline；记录 Mantle Cargo.toml pin 的 exact source commit（不作为 Multica checkout command） | 1 |
| src-4c | code_analysis | upstream `op-geth`/`go-ethereum` 作为 Tier F baseline；用于归因 Mantle op-geth customizations vs inherited behavior（不作为 Multica checkout command） | 1 |
| src-5 | official_docs | Base Azul 升级官方资料：https://blog.base.dev/introducing-base-azul | 1 |
| src-6 | official_docs | Reth 官方文档与 CHANGELOG.md（paradigmxyz/reth），用于版本基线对照 | 2 |
| src-7 | benchmark | Go vs Rust EVM 性能基准测试（Paradigm reth benchmark、op-reth 发布博客）；作为 Go→Rust 迁移增益估算的证据 | 2 |
| src-8 | on_chain_data | Base/Mantle 主网典型 block 的 gas usage、tx mix（用于校准 perf_impact_estimate 的 tx mix 假设） | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 (init) | create | 全文重写 | 用户于 2026-05-22 更新 issue 要求三方对比（新增 Mantle op-geth Go 生产栈作为 Tier F 基线）；原两方对比 outline 完全替换 | Orchestrator Dispatch 2026-05-22 re-run authorization |
| 1 (init) | add | attribution_tiers.F | 新增 Tier F（Mantle op-geth，Go 生产栈），作为 Go→Rust 迁移的性能基线 | 三方对比框架要求 |
| 1 (init) | add | item-2 | 新增 Mantle op-geth 定制改动清单专项（MetaTx、TokenRatio、Go runtime 分析） | 三方对比框架要求 |
| 1 (init) | add | item-7 | 新增 Go runtime vs Rust 执行模型系统性影响与迁移增益估算专项 | 三方对比框架要求 |
| 1 (init) | add | item-8 | 新增 MetaTx 与 TokenRatio overhead 精确量化专项 | 三方对比框架要求 |
| 1 (init) | revise | item-10 (formerly item-7) | 性能矩阵扩展为三方，以 Mantle op-geth 为 baseline（= 1x）；增加 Go→Rust 迁移增益分解护栏 | 三方对比框架要求 |
| 1 (init) | revise | item-11 (formerly item-8) | 改进建议扩展为 5+ 条，明确区分 Go 栈适用 / Rust 栈适用 | 三方对比框架要求 |
| 1 (carry-forward) | retain | attribution_tiers A–E，测量方法学护栏（非加性、分母标签、Tier 归属同步） | 从 Review Round 1 已批准 outline 继承；规则维持不变 | 原 outline Review Round 1 approved |
| 2 | patch P1 | item-1/src-1/src-2 | Add explicit version pins for Base reth v1.11.4 and Mantle reth 88505c7f | adversarial-review-round-1 |
| 2 | patch P2 | item-7 (dispatch item-4 equivalent / Go runtime item) | Add go_runtime_observables and gc_pause_proxy to required investigation_fields | adversarial-review-round-1 |
| 2 | patch P3 | item-8 | Add quantitative fields for MetaTx/TokenRatio overhead: metatx_per_tx_overhead_ns, metatx_active_us_path, token_ratio_per_tx_extra_sloads, token_ratio_bigint_cost, injection_points_go, injection_points_rust, evidence_tier | adversarial-review-round-1 |
| 2 | patch P4 | source-requirements | Add explicit multica repo checkout commands for three primary sources and retain upstream baseline notes without checkout commands | adversarial-review-round-1 |
