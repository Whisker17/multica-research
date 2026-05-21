# Research Outline: Base Codebase 性能提升优势综述

**Project slug**: `mantle-base-codebase-evaluation`
**Topic slug**: `performance-advantage-summary`
**Round**: 2
**Branch**: `research/mantle-base-codebase-evaluation/performance-advantage-summary`
**GitHub repo**: `Whisker17/multica-research`

---

## 1. Topic Analysis

### 1.1 Research Question

Mantle 切换至 Base codebase 后，在各组件层面能获得哪些具体的、可量化的性能提升？这些提升如何按实施难度和预期收益分级，形成可执行的路线图？

### 1.2 Scope

1. Mantle 当前性能指标与 Base 性能指标对比（TPS / 延迟 / 吞吐量差距量化）
2. 执行层（op-reth fork）差异对性能的影响
3. Block Builder 与 Flashblocks 对吞吐量的贡献
4. Gas 协议与性能配置参数对比
5. Sequencer 共识管道性能差异
6. Batcher 管道架构对吞吐量的影响
7. DA 带宽与吞吐量天花板
8. Quick Wins vs 中长期优化分析（含预期收益量化）
9. 组件级瓶颈到 Base 改进项的映射

### 1.3 Audience

Mantle 技术决策者、核心基础设施工程团队、项目管理层。需要同时满足技术深度（工程师可据此实施）和战略高度（管理层可据此决策资源分配）。

### 1.4 Expected Output

1. **性能对比表格**: Mantle 当前 vs Base 当前 vs Mantle 切换后预期（含三列对比）
2. **改进项分级表**: Quick Wins / Mid-term / Long-term，含预期 TPS 增益、实施工时、ROI 评级
3. **组件瓶颈映射**: 组件级瓶颈到 Base 改进项的因果映射关系
4. **证据引用**: 来自 `base-perf-analysis` 各子研究的定量证据

---

## 2. Outline Items

### Item 1: Executive Summary — 性能差距全景与关键结论

**Research question**: Mantle 与 Base 之间的整体性能差距是什么？切换 codebase 后最核心的收益是什么？

**Investigation fields**:
- F1.1: 当前 Mantle 性能基线（TPS、区块利用率、gas 利用率、延迟指标）
- F1.2: 当前 Base 性能基线（TPS、区块利用率、gas 利用率、延迟指标）
- F1.3: 差距量化（倍数关系、绝对差值）
- F1.4: Mantle demand-bound vs supply-bound 状态诊断
- F1.5: 切换后预期性能天花板（保守/乐观区间）
- F1.6: 三句话核心结论

**Key metrics from primary sources**:
- Mantle: ~0.7-1.0 TPS, 60.8% empty blocks, 0.29% gas utilization
- Base: ~93.7 user-tx/s, ~0.20% empty blocks
- Gap: ~90-130× TPS gap
- Mantle primary binding constraint: demand-side, NOT supply-side
- Post-switch saturated ceiling: ~1,083 TPS (Quick Wins only), ~2,000-3,000+ TPS (full roadmap)

**Sources**: `perf-gap-analysis-recommendations/final.md` §Executive Summary, §Bottleneck Level Model

---

### Item 2: 性能对比基准表

**Research question**: 三方（Mantle 当前 / Base 当前 / Mantle 切换后预期）在各核心指标上的量化对比如何？

**Investigation fields**:
- F2.1: TPS 对比（user-tx/s, system-tx/s）
- F2.2: 区块时间与区块大小对比
- F2.3: Gas 配置对比（gasLimit, baseFee, EIP-1559 参数）
- F2.4: DA 带宽利用率对比
- F2.5: Batcher 吞吐量对比（blob/tx, 发送频率）
- F2.6: 延迟对比（block seal time, pre-confirmation latency）
- F2.7: 空块率对比

**Output format**: 三列对比表（Mantle Current | Base Current | Mantle Post-Switch Expected）

**Key data points**:
| Metric | Mantle Current | Base Current | Source |
|--------|---------------|-------------|--------|
| User TPS | ~0.7-1.0 | ~93.7 | perf-gap §Executive |
| Empty block rate | 60.8% | 0.20% | block-builder §5.1 |
| Gas utilization | 0.29% (median 0.08%) | 8.19% avg / 7.31% median | perf-gap §Comparison Table (500-block sample) |
| gasLimit | 200B (decorative) | ~375M (binding) | gas-protocol §3.1 |
| baseFee | 0.02 gwei (fixed) | dynamic EIP-1559 | gas-protocol §3.2 |
| MaxPendingTx | 1 (serialized) | 10 | batcher §4.1 |
| Observed blobs/batch tx | 1 (on-chain confirmed §6.5) | 5 (Base mainnet observed §6.5) | batcher §6.5 on-chain sample |
| TargetNumFrames (config) | 1 (code-default) | — (Base mainnet not directly explained by Rust TargetNumFrames path) | batcher §2, §6.5 [R3-P1] |
| TargetNumFrames (Mantle post-switch target) | — | 6 (recommended quick-win config) | batcher §7 Quick Wins |
| Batcher cadence | ~448s | ~49s | batcher §3.3 |
| DA demand | ~97.1 B/s | ~14.4 KB/s | da-bandwidth §4.1 |
| Pre-confirmation | N/A | 250ms (Flashblocks) | block-builder §3.2 |

**Sources**: All 8 primary source finals

---

### Item 3: 执行层（op-reth Fork）性能差异分析

**Research question**: Base 与 Mantle 的 op-reth fork 在执行层架构上有哪些差异？这些差异如何影响性能？

**Investigation fields**:
- F3.1: 5-Tier (A-E) 归因模型概述
- F3.2: Tier C（Base 自研 OP-Stack 执行层，24 subcrates）vs Tier B（Mantle vendor op-reth/v2.2.1）
- F3.3: 缓存架构差异——Base CachedExecutor/CachedPrecompile vs Mantle TransactionCache/CachedReads（两种不同缓存架构，非"有无"之分）
- F3.4: 并行状态根计算——Base ParallelStateRoot/StateRootTask/LazyOverlay（已上线）vs Mantle（有库代码但未接线）
- F3.5: 异步 receipt root 计算（Base ReceiptRootTask）
- F3.6: Mantle Tier E token_ratio 开销（≥6 U256 ops + storage per tx）
- F3.7: 性能影响量化（TPS 权重：10-20%）

**Key findings from primary sources**:
- Base pins reth v1.11.4, Mantle pins v2.2.0
- Base Tier C: 24 subcrates for self-implemented OP-Stack execution
- Mantle has ParallelStateRoot/StateRootTask/LazyOverlay libs but NOT wired into execution path
- Mantle Tier E: token_ratio per-tx overhead (≥6 U256 ops + storage read/write)
- Two different cache architectures at different scopes (block-level vs flashblocks-scoped)

**Sources**: `execution-layer-reth-fork-comparison/final.md` §Tier A-E analysis, §Recommendations

---

### Item 4: Block Builder 与 Flashblocks 吞吐量贡献

**Research question**: Base 的 rollup-boost + Flashblocks 架构如何提升吞吐量和用户体验？Mantle 采用后的预期收益是什么？

**Investigation fields**:
- F4.1: rollup-boost 架构（BlockSelectionPolicy: GasUsed）
- F4.2: Flashblocks 250ms sub-block 机制与 pre-confirmation
- F4.3: 空块消除机制（builder 250ms×8 连续填充 vs Mantle 系统空块）
- F4.4: Mantle `flashblocks/poc` 与 `feat/flashblocks-mantle-aware` 分支现状
- F4.5: 性能影响量化——ROI 取决于 60.8% 空块中 timing-recoverable 比例
- F4.6: Phase 0a 必要性（需先量化需求侧填充率才能估算真实收益）

**Key findings from primary sources**:
- Mantle 60.8% system-only blocks vs Base 0.20%
- Flashblocks provides 250ms pre-confirmation latency
- Mantle `flashblocks/poc` has NO actual flashblocks code
- ROI depends on what fraction of empty blocks are timing-recoverable vs demand-absent
- Mid-term priority (Tier 3 Medium ROI in current demand state)

**Sources**: `block-builder-flashblocks-throughput/final.md` §Architecture, §Empty Block Analysis, §ROI

---

### Item 5: Gas 协议与性能配置参数对比

**Research question**: Gas 配置参数差异如何影响吞吐量上限和经济机制？Quick Wins 配置调整能带来什么收益？

**Investigation fields**:
- F5.1: gasLimit 对比——Base ~375M effective binding vs Mantle 200B decorative
- F5.2: EIP-7825 per-tx cap（Base active, Mantle gated by `!IsOptimism()`）
- F5.3: EIP-1559 参数对比——Base elasticity=6/denominator=250 vs Mantle elasticity=2/denominator=8
- F5.4: baseFee 机制——Base dynamic vs Mantle 0.02 gwei fixed
- F5.5: Quick Wins 参数调整路径（Q1-Q5 priority matrix）
- F5.6: gasLimit 校准至 1-2G 的安全评估

**Key findings from primary sources**:
- Mantle gasLimit 200B is decorative (never approached), Base 375M is actually binding
- EIP-7825 per-tx cap not enforced on Mantle due to `!IsOptimism()` gate
- Mantle fixed baseFee eliminates congestion signaling
- Quick wins: gasLimit calibration to 1-2G, EIP-1559 denominator=250/elasticity=6, dynamic baseFee

**Sources**: `gas-protocol-perf-config/final.md` §Parameter Comparison, §Q1-Q5 Priority Matrix

---

### Item 6: Sequencer 共识管道性能差异

**Research question**: Base 的 5-actor tokio 模型相比 Mantle 的单线程 event-loop 有什么性能优势？

**Investigation fields**:
- F6.1: Base 5-actor 架构（Engine/Derivation/Network/L1Watcher/Sequencer + mpsc(1024)）
- F6.2: Mantle 单 driver eventLoop 架构
- F6.3: PayloadSealer 3-state machine（Sealed→Committed→Gossiped）
- F6.4: sealingDuration=50ms hardcoded 限制
- F6.5: per-block FCU 开销（Mantle FCU=2，已从 round-1 "4 serial FCU" 纠正）
- F6.6: 7 improvement levers（actor+task queue, derivation split, dynamic schedule 等）
- F6.7: kona-node 迁移评估（18-30 person-months, Tier 4 Low ROI）

**Key findings from primary sources**:
- Base uses 5 concurrent tokio actor tasks vs Mantle single event-loop (op-node)
- sealingDuration=50ms is hardcoded in Mantle
- kona fork is fp_client_only, not full node replacement
- TPS weight: 5-12% for sequencer pipeline
- Dynamic sealing is a Quick Win; actor refactor is mid-term

**Sources**: `sequencer-consensus-pipeline-perf/final.md` §Architecture Comparison, §Improvement Levers

---

### Item 7: Batcher 管道架构与吞吐量影响

**Research question**: Batcher 配置差异如何构成 Mantle 当前最大的供给侧瓶颈？参数调优能带来多大的吞吐量提升？

**Investigation fields**:
- F7.1: 7-stage pipeline 对比
- F7.2: MaxPendingTransactions=1 序列化约束（code default）→ ~36 TPS saturated ceiling
- F7.3: TargetNumFrames=1 (code-default) → 1 blob/tx observed on-chain (§6.5); Base mainnet observed 5 blobs/tx (not directly explained by Rust TargetNumFrames path)
- F7.4: Zlib vs Brotli10 压缩效率对比
- F7.5: On-chain 行为对比——Mantle ~448s cadence vs Base ~49s
- F7.6: Quick Wins 量化——M=5-10, F=6 → ~1,083 TPS saturated ceiling
- F7.7: Single pending channel 架构约束

**Key findings from primary sources**:
- MaxPendingTx=1 is the single largest supply-side bottleneck
- Quick Win: MaxPendingTx 1→5-10 + TargetNumFrames 1→6 (recommended config target) → ~1,083 TPS
- Batcher TPS weight: 25-40% (highest component weight)
- Brotli10 provides ~15-25% better compression than Zlib
- This is the #1 ROI improvement (Tier 1 Exceptional)

**Sources**: `batcher-pipeline-architecture/final.md` §Pipeline Comparison, §Quick Wins Analysis

---

### Item 8: DA 带宽与吞吐量天花板

**Research question**: DA 层是否构成 Mantle 的性能瓶颈？BPO2 升级后的带宽天花板在哪里？

**Investigation fields**:
- F8.1: BPO2 target=14, max=21 blobs/block 配置
- F8.2: 物理 DA 带宽——151.72 KB/s sustained
- F8.3: DA TPS ceiling 计算——Base ~942 TPS, Mantle ~1,749 TPS（由于更小的 tx encoding）
- F8.4: Mantle DA 需求现状——~97.1 B/s, ~1.18 TPS DA demand
- F8.5: DA headroom——~1,480× 余量
- F8.6: 结论：DA NOT binding for Mantle（当前和可预见未来均非瓶颈）

**Key findings from primary sources**:
- DA has ~1,480× headroom for Mantle — definitively NOT the bottleneck
- Mantle observed 82.38 B/UOP → ~1,749 TPS DA ceiling
- Base observed 153.03 B/UOP → ~942 TPS DA ceiling
- DA only becomes relevant at M4+ milestone (~1,400+ TPS)

**Sources**: `da-bandwidth-throughput-ceiling/final.md` §BPO2 Analysis, §DA Ceiling Calculation

---

### Item 9: 背压机制与安全约束

**Research question**: Mantle 当前的背压机制状况如何？切换至 Base 背压架构后有什么改进？

**Investigation fields**:
- F9.1: 4 种背压类型（A: SequencerMaxSafeLag, B: DA Throttling, C: Engine memory, D: Queue backlog）
- F9.2: Mantle 背压缺失诊断——MaxSafeLag=0 disabled, DA Throttling RPC removed
- F9.3: 4 条因果链分析
- F9.4: Base 的背压机制完整性
- F9.5: 4 项改进策略（P0-P2 优先级）
- F9.6: 背压修复与 Quick Wins 的前置依赖关系

**Key findings from primary sources**:
- Mantle has NO effective backpressure (MaxSafeLag=0 disabled)
- DA Throttling: code-default enabled but miner_setMaxDASize RPC removed from op-geth → batcher fails
- P0: Restore DA Throttling before any throughput increase
- P1: Adaptive Gas Limit, P2: Multi-Batcher, P2: Flashblocks integration

**Sources**: `batcher-sequencer-backpressure/final.md` §Backpressure Types, §Improvement Strategies

---

### Item 10: Quick Wins / Mid-term / Long-term 改进分级

**Research question**: 所有改进项如何按 ROI、实施难度和时间分级？形成怎样的可执行路线图？

**Investigation fields**:
- F10.1: ROI Tier 分类（Tier 1 Exceptional → Tier 4 Low）
- F10.2: Quick Wins 详表（QW-a1/a2/a3 batcher, QW-b1-b5 execution, QW-c1/c2 gas）
- F10.3: Mid-term 详表（MT-1 through MT-8）
- F10.4: Long-term 详表（LT-1 through LT-6）
- F10.5: TPS Milestone 路线图（M0→M1→M3→M4→M5）
- F10.6: 时间线——M1 +2wk, M3 +3-4mo, M4 +6-9mo, M5 +12-18mo
- F10.7: Risk matrix 与 accept-risk 项

**Key milestones from primary sources**:
| Milestone | Timeline | TPS Target | Key Actions |
|-----------|----------|-----------|-------------|
| M0 (Now) | - | 0.7-1.0 | Baseline |
| M1 | +2 weeks | ~1,083 | Batcher params + Brotli10 + Dynamic seal |
| M3 | +3-4 months | ~1,200-1,400 | ParallelStateRoot + Sequencer actor refactor |
| M4 | +6-9 months | ~1,400-2,000 | Flashblocks + Multi-batcher |
| M5 | +12-18 months | ~2,000-3,000+ | kona-node migration |

**ROI Tiers**:
- Tier 1 (Exceptional): Batcher params (MaxPendingTx, TargetNumFrames), Brotli10, Dynamic seal
- Tier 2 (High): ParallelStateRoot
- Tier 3 (Medium): Flashblocks, Sequencer refactor
- Tier 4 (Low): kona-node migration (18-30 person-months)

**Sources**: `perf-gap-analysis-recommendations/final.md` §Quick Wins, §Mid-term, §Long-term, §ROI Tiers, §TPS Milestones

---

### Item 11: 组件瓶颈到 Base 改进项映射

**Research question**: 每个组件级瓶颈如何映射到具体的 Base 改进项？因果关系和依赖链是什么？

**Investigation fields**:
- F11.1: Bottleneck Level Model（L1 demand-side, L2 latent supply, L3 headroom）
- F11.2: Component TPS Weight 分布（Batcher 25-40%, Execution 10-20%, Sequencer 5-12%）
- F11.3: 瓶颈→改进项因果映射表
- F11.4: 依赖链分析（哪些改进项必须先于其他项实施）
- F11.5: 关键前置条件（背压修复 → 吞吐量提升）

**Mapping structure**:
| Bottleneck Component | Current Constraint | Base Improvement | Priority | Dependency |
|---------------------|-------------------|-----------------|----------|------------|
| Batcher serialization | MaxPendingTx=1 | M=5-10, TargetNumFrames=6 (recommended target) parallel | P0 | Backpressure restore |
| Batcher compression | Zlib | Brotli10 | P0 | None |
| Sequencer seal timing | 50ms hardcoded | Dynamic seal schedule | P0 | None |
| Execution state root | Sequential | ParallelStateRoot | P1 | Wiring existing libs |
| Backpressure | Disabled/broken | Full 4-type restoration | P0 (prerequisite) | None |
| Gas config | Decorative 200B | Calibrated 1-2G + EIP-1559 | P1 | Demand growth |
| Block builder | System empty blocks | rollup-boost + Flashblocks | P2 | Demand sufficient |
| Sequencer architecture | Single event-loop | 5-actor tokio | P2 | Engineering effort |
| DA bandwidth | ~1,480× headroom | Not binding | - | Only at M4+ |

**Sources**: `perf-gap-analysis-recommendations/final.md` §Bottleneck Level Model, §Component TPS Weights

---

## 3. Diagram Plan

### Diagram 1: Performance Improvement Waterfall Chart

**Type**: Mermaid waterfall / stacked bar chart
**Purpose**: 展示从 Mantle 当前状态 (M0) 到各 milestone (M1→M5) 的 TPS 增量叠加，每一层标注对应的改进项和预期增益
**Data flow**:
- M0 baseline: 0.7-1.0 TPS
- M1 increment: Batcher Quick Wins → +~1,082 TPS
- M3 increment: ParallelStateRoot + Sequencer → +~117-317 TPS
- M4 increment: Flashblocks + Multi-batcher → +~200-600 TPS
- M5 increment: kona-node → +~600-1,000 TPS
**Placement**: Item 10 (改进分级) 或 Executive Summary

### Diagram 2: Component Bottleneck Heatmap

**Type**: Mermaid quadrant chart or styled table
**Purpose**: 组件级瓶颈热力图——X 轴为实施难度 (effort), Y 轴为性能影响 (TPS weight), 气泡大小为 ROI tier
**Components plotted**:
- Batcher params: Low effort, High impact → Tier 1
- Brotli10 compression: Low effort, Medium impact → Tier 1
- Dynamic seal: Low effort, Medium impact → Tier 1
- ParallelStateRoot: Medium effort, High impact → Tier 2
- Flashblocks: Medium effort, Medium impact → Tier 3
- Sequencer refactor: High effort, Medium impact → Tier 3
- kona-node: Very high effort, Medium impact → Tier 4
**Placement**: Item 11 (组件映射)

### Diagram 3: Dependency Chain Flow

**Type**: Mermaid flowchart (LR)
**Purpose**: 展示改进项之间的依赖关系和实施顺序约束
**Key dependencies**:
- Backpressure restore → Batcher throughput increase
- Demand growth → Gas config tuning ROI
- Demand growth → Flashblocks ROI
- ParallelStateRoot wiring → Execution layer gains
**Placement**: Item 11 (组件映射)

---

## 4. Source Requirements

### Primary Sources (Internal Research)

All sources are from the `base-perf-analysis/research-sections/` directory in the same repository:

| Source | Path | Status | Key Content |
|--------|------|--------|-------------|
| Performance Gap Analysis | `perf-gap-analysis-recommendations/final.md` | Final | Master synthesis: Quick Wins, ROI Tiers, TPS Milestones |
| Execution Layer Comparison | `execution-layer-reth-fork-comparison/final.md` | Final | 5-Tier attribution, cache architectures, ParallelStateRoot |
| Block Builder & Flashblocks | `block-builder-flashblocks-throughput/final.md` | Final | rollup-boost, empty block elimination, 250ms pre-confirmation |
| Gas Protocol Config | `gas-protocol-perf-config/final.md` | Final | gasLimit, EIP-7825, EIP-1559 params, baseFee mechanism |
| Sequencer Pipeline | `sequencer-consensus-pipeline-perf/final.md` | Final | 5-actor vs event-loop, PayloadSealer, improvement levers |
| Batcher Pipeline | `batcher-pipeline-architecture/final.md` | Final | 7-stage pipeline, MaxPendingTx, TargetNumFrames, Quick Wins |
| DA Bandwidth | `da-bandwidth-throughput-ceiling/final.md` | Final | BPO2, DA ceiling, ~1,480× headroom |
| Backpressure Mechanisms | `batcher-sequencer-backpressure/final.md` | Final | 4 backpressure types, Mantle broken state, restoration priorities |

### Citation Convention

All claims must cite the specific source section using the format:
`[source-slug §Section.Subsection]` — e.g., `[batcher-pipeline §4.1]`, `[perf-gap §Executive Summary]`

### External Sources

No external sources required for this synthesis. All data is sourced from the 8 internal primary research sections listed above. If additional context on Base or OP-Stack upstream is needed, reference the codebase directly via commit SHA.

---

## 5. Quality Checklist

- [ ] Every quantitative claim has a citation to a specific primary source section
- [ ] Performance comparison table has all three columns populated (Mantle Current / Base Current / Post-Switch)
- [ ] ROI tiers are consistent with `perf-gap-analysis-recommendations/final.md` classification
- [ ] TPS milestones are consistent with primary source roadmap
- [ ] Dependency chains are accurately represented (especially backpressure → throughput prerequisite)
- [ ] Demand-bound vs supply-bound distinction is clearly articulated
- [ ] No conflated "cache vs no cache" framing for execution layer (must be "two different cache architectures")
- [ ] Corrected FCU count (2, not 4) for Mantle sequencer
- [ ] Diagrams use Mermaid syntax and are renderable
- [ ] Outline is independently reviewable by adversarial agent without needing additional context
- [ ] All 9 scope areas are covered by at least one outline item
- [ ] Component weights sum to reasonable total and are sourced

---

## 6. Structural Notes

### Coverage Mapping (Scope → Items)

| Scope Area | Covered By |
|------------|-----------|
| 1. Mantle vs Base 性能对比 | Items 1, 2 |
| 2. 执行层差异 | Item 3 |
| 3. Block Builder & Flashblocks | Item 4 |
| 4. Gas 协议配置 | Item 5 |
| 5. Sequencer 管道 | Item 6 |
| 6. Batcher 管道 | Item 7 |
| 7. DA 带宽天花板 | Item 8 |
| 8. Quick Wins vs 中长期 | Item 10 |
| 9. 组件瓶颈映射 | Items 9, 11 |

### Key Analytical Constraints

1. **Demand-bound caveat**: Mantle 当前处于需求约束状态 (~0.7-1.0 TPS)，供给侧改进的实际效果只有在需求增长后才能观察到。所有 TPS 估算均为"saturated ceiling"（假设需求充足）。
2. **Cross-source consistency**: 当不同子研究间数据有差异时，以 `perf-gap-analysis-recommendations/final.md` 作为最终综合仲裁源。
3. **Round-1 corrections**: Sequencer FCU count 已从 "4 serial FCU" 修正为 "2 per block"，需确保本综述使用修正后的数据。
4. **Round-2 corrections**: (a) Base gas utilization 从 ~50%+ 修正为 8.19% avg / 7.31% median（perf-gap comparison table, 500-block sample）；(b) TargetNumFrames 与 observed blobs/tx 区分——Base mainnet 观测为 5 blobs/tx，非由 Rust TargetNumFrames 路径直接解释，TargetNumFrames=6 仅作为 Mantle 切换后 Quick Win 配置推荐；(c) Source requirements table 中所有 `final.md` 文件统一标注为 Final。
