---
topic: "执行层性能架构对比：Base Reth Fork vs Mantle Reth Fork"
project_slug: base-perf-analysis
topic_slug: execution-layer-reth-fork-comparison
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: base-perf-analysis/outlines/execution-layer-reth-fork-comparison.md
  draft: base-perf-analysis/research-sections/execution-layer-reth-fork-comparison/drafts/round-{n}.md
  final: base-perf-analysis/research-sections/execution-layer-reth-fork-comparison/final.md
  index: base-perf-analysis/research-sections/_index.md

scope: |
  深度对比 Base 与 Mantle 两个 reth fork 的执行层架构、定制改动与性能关键路径，
  覆盖：(1) 相对上游 reth 的修改清单与版本基线差异；(2) 并行 EVM / 并行状态访问 /
  pipeline 设计；(3) MDBX 存储层与状态/区块/收据缓存配置；(4) Mantle 特有 MetaTx 与
  L1 cost 计算的 EVM overhead；(5) 模块级 IOPS / 单 block 执行时间 / gas throughput
  / 内存占用对比，量化两 fork 在执行层对端到端 TPS 差距的贡献，并产出按优先级排序的
  Mantle 改进建议清单。
audience: |
  Mantle / Base 性能优化方向的协议工程师与执行层（EL）开发者；
  Multica 研究 squad 内部下游 Research Agent（sequencer-consensus-pipeline-perf,
  perf-gap-analysis-recommendations 等）；OP Stack 生态中关注从 op-geth 迁移到
  reth-based EL 的运营者；项目内部决策者评估"reth fork 改造"作为提升 TPS 的可行路径。
  读者熟悉 EVM/MDBX/reth pipeline 基础，但不必了解两个 fork 的具体定制细节。
expected_output: |
  - 两个 reth fork 的模块级架构差异矩阵（按 crate / 子系统列出 diff vs upstream reth）
  - 性能关键改动清单（每项附预估 gas/s 或 TPS 影响量级）
  - 上游 reth 基线版本对比表（commit / 标签 / 关键 feature 同步状态）
  - MDBX 配置对比表（map_size、page_size、sync_mode、env flags、compactor 策略）
  - 并行执行/状态访问能力对比（是否启用、并行度、退化路径、edge case 处理）
  - EVM 执行 pipeline 对比图（fetch → recover → execute → state-root → commit 各阶段）
  - 量化的执行层 TPS 贡献估算：(a) 上游版本差距、(b) 并行 EVM 缺失、(c) MetaTx/L1 cost overhead
  - 针对 Mantle 的至少 3 条改进建议，标注预期 TPS 提升、改造成本与风险等级
  - 至少 2 个 Mermaid 图表（模块依赖 / EVM pipeline / 状态存储任选）

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-20T04:30:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-20T05:05:00Z"

attribution_tiers:
  description: |
    所有性能相关的代码、改动、配置与 TPS 影响声明，必须显式标注其归属层级（Tier A–E）。
    无法明确归属的声明必须标记为 `[UNATTRIBUTED]` 并在 Patch Log 中记录待补证据。
  tiers:
    - id: A
      name: 上游 reth
      source_repo: paradigmxyz/reth
      note: 中立 baseline；同时供 Base 与 Mantle 比较
    - id: B
      name: OP 继承层
      source_repo: ethereum-optimism/optimism (op-reth/v2.2.1 或 Mantle Cargo.toml 引用的精确 source commit)
      note: 由 OP Stack 引入、对 Base 与 Mantle 共有的 op-reth 行为
    - id: C
      name: Base overlay
      source_repo: base/base
      note: Base 在 OP 继承层之上的增量改动
    - id: D
      name: Mantle overlay
      source_repo: mantle-xyz/mantle-elysium (workspace)
      note: Mantle 在 OP 继承层之上的增量改动（仅 mantle-elysium 仓库内改动）
    - id: E
      name: Mantle 外部依赖补丁
      source_repo: mantle-xyz/revm, mantle-xyz/evm, 及 Mantle Cargo.toml `[patch.crates-io]` 注入的其他 fork
      note: 通过 Cargo `[patch]` 重定向到 Mantle 自有 fork 的 crate 改动；逻辑虽位于外部仓库但作用域同 mantle-elysium 一致
---

# Research Outline: 执行层性能架构对比：Base Reth Fork vs Mantle Reth Fork

## Items

### item-1: 上游 reth 基线对齐度与 fork 演化轨迹

确认 Base（`base/base` → `crates/execution`，即 base-reth-node）和 Mantle（`mantle-xyz/reth` →
`mantle-elysium` 分支）当前各自 pin 在 `paradigmxyz/reth`（Tier A）与 `ethereum-optimism/optimism`
op-reth/v2.2.1（Tier B，OP 继承层；以 Mantle `Cargo.toml` 引用的精确 source commit 为准）的
哪个 commit/tag，量化两者相对上游 reth **与** OP op-reth 双 baseline 的滞后量与 cherry-pick 模式
（rebase vs merge vs selective backport）。需要枚举每个 fork 对上游 EL 关键性能 PR（pipeline
重构、parallel execution、prune、stateless 等）的同步状态，判断"版本基线差"在两链 TPS 差距
中占多少比例，并识别 Mantle 可通过低成本同步上游或 OP 上游获得的性能红利。

**强制要求**：每条版本基线声明必须显式标注 Tier（A=upstream reth、B=OP op-reth），不得只与
upstream reth 单边对比，否则会把 OP 继承的行为错误归因为 Mantle 自有选择。

- **Priority**: high
- **Dependencies**: none
- **Required investigation_fields**:
  - `attribution_tier`：每个版本基线/PR 同步状态条目必须标注 `A`（upstream reth）或 `B`（OP op-reth）
  - `tier_a_baseline_commit` / `tier_b_baseline_commit`：两个 baseline 的精确 commit SHA
  - `tier_a_lag` / `tier_b_lag`：两 fork 相对各自 baseline 的 commit 数 / 关键 PR 缺口

### item-2: 两个 fork 相对上游的定制改动清单与目的分类

逐 crate 梳理 Base/Mantle 相对上游的全部定制改动，按目的分类为：(a) 性能优化、
(b) 协议适配（OP Stack/L2 derivation/L1 origin 处理）、(c) 安全/审计加固、(d) DX/可运维性、
(e) 未文档化的实验性改动。每项标注变更文件、行数量级、是否触及热路径（execute_block /
state_root / db txn）。给出"哪些 Base 改动对性能直接贡献"与"哪些 Mantle 改动反而引入 overhead"的对照。

**强制归属要求**：每条改动必须 bucket 到下列归属层级之一（避免把 OP 继承行为误归为 Mantle/Base 选择）：

- **Tier A — upstream reth**：来自 `paradigmxyz/reth` 主线，Base 与 Mantle 共享
- **Tier B — OP 继承**：来自 `ethereum-optimism/optimism` op-reth/v2.2.1（或 Mantle `Cargo.toml` 引用
  的精确 op-reth source commit），Base 与 Mantle 共享的 OP Stack 行为
- **Tier C — Base overlay**：`base/base` 在 OP 继承层之上的增量改动
- **Tier D — Mantle overlay**：`mantle-elysium` workspace 内部、在 OP 继承层之上的增量改动
- **Tier E — Mantle 外部依赖补丁**：Mantle `Cargo.toml` 中 `[patch.crates-io]` 注入的 fork
  （`mantle-xyz/revm`、`mantle-xyz/evm` 等），即使逻辑位于外部仓库，作用域等同 Tier D

不能明确归属的条目必须标 `[UNATTRIBUTED]` 并记录到 Patch Log 与 follow-up 列表，不得纳入 TPS 影响声明。

- **Priority**: high
- **Dependencies**: item-1
- **Required expected_output**：定制改动矩阵必须按 5 列 bucket 输出（每行一条改动）：
  | crate / 文件 | 归属 Tier (A/B/C/D/E) | 改动摘要 | 是否热路径 | TPS 影响（measured / reported / inferred；带 Tier 标签） |
- **Per-tier 子表**：报告 item-2 输出必须包含 5 个独立子表（A、B、C、D、E），每个 Tier 单独列出改动条目；
  禁止把 Tier B（OP 继承）与 Tier C/D（Base/Mantle overlay）混在同一行

### item-3: 并行 EVM 与并行状态访问能力对比

调查 Base 是否实现并行 EVM 执行（block-internal tx-level parallelism）或并行状态访问（state warm-up /
prefetch），以及具体策略：基于读写集预测、optimistic concurrency、还是简单的预取。对照 Mantle
现状（默认上游 reth 是顺序执行；mantle-elysium 是否启用任何并行特性）。明确退化路径与
正确性保证机制（冲突检测、回滚、最终顺序提交），并估算在 Base 主网典型 tx mix 下并行带来的
有效 gas/s 提升。

- **Priority**: high
- **Dependencies**: item-2

### item-4: MDBX 存储层与缓存策略配置对比

提取两个 fork 在 MDBX 配置上的所有差异：`map_size`、`page_size`、`sync_mode`（SAFE_NOSYNC /
NOMETASYNC）、`env_flags`、`Geometry`、`commit_latency` 等；同时对比 state cache / block cache /
receipt cache / trie cache 的容量、淘汰算法、预热策略。讨论 flat state layout、state trie
optimization（如 path-based scheme、archive vs full）等关键决策。量化在写放大、IOPS、p99
state-read 延迟维度上的差异。

- **Priority**: high
- **Dependencies**: item-2

### item-5: EVM 执行扩展与自定义 precompiles

对比两个 fork 在 REVM 版本、自定义 precompiles、gas metering 修改、opcode 行为微调上的差异。
Base 侧重点：是否有 L2-friendly 的执行短路（跳过部分主网验证如某些状态根 sanity 检查）、
是否有 jit/aot 实验、precompile 加速（如 secp256r1、bn254）。Mantle 侧重点：MetaTx 处理路径
（gas payer 分离）、L1 cost 计算注入点（per-tx 还是 per-block）、是否引入额外的 token 抽象
（MNT vs ETH gas token）对热路径的影响。量化 Mantle 特有逻辑在单 tx / 单 block 上的 CPU overhead。

- **Priority**: high
- **Dependencies**: item-2

### item-6: Pipeline 设计与执行/验证阶段并行度

对比两个 fork 的 reth pipeline 阶段拓扑（Headers → Bodies → Senders → Execution → MerkleTrie →
History → Finish 等）、阶段并行度与流水线深度、checkpoint 粒度、reorg 处理路径。讨论是否
有针对 sequencer 在线场景（pending block 持续生成）的 pipeline 调整，以及对 historical sync
与 live execution 路径的拆分。识别哪些 pipeline 改动对 sustained TPS（持续吞吐）有 first-order
影响，哪些只是 sync-time 优化。

- **Priority**: medium
- **Dependencies**: item-1, item-2

### item-7: 性能基准与量化对比矩阵

汇总以下指标，构建可量化的执行层性能对比矩阵：(a) 单 block 执行时间（同一 gas 量、同一 tx mix
下两 fork 各自耗时）、(b) gas throughput（gas/s 上限）、(c) state read/write IOPS、(d) 内存占用
（RSS、cache hit rate）、(e) p50/p99 tx execution latency。承认主网在线 benchmark 在该研究阶段
可能拿不到，回退到代码静态分析 + 已有公开 benchmark + 推断式估算，明确每项数据的证据等级
（直接测量 / 公开报告 / 推断）。

**测量方法学护栏（强制）**：

1. **非加性原则（non-additive）**：所有执行层 TPS / gas-throughput 估算默认**不可相加**。
   只有当两个改动在**同一 block 构造与 tx mix** 下测得、且改动作用于**正交的热路径**时，
   才允许做加法合成；否则必须报告为独立场景下的 upper-bound，不得直接累加。
2. **同一基准前提**：跨 fork（Base vs Mantle）或跨改动的对比，必须显式声明：(a) block gas
   limit、(b) tx mix（calldata-heavy / storage-heavy / compute-heavy 占比）、(c) 硬件 spec、
   (d) 同步阶段（live execution vs historical sync）。任何一项不一致的对比必须标
   `[INCOMPARABLE_BASELINE]`。
3. **分母标签（denominator labeling）**：每条量化声明必须用单一分母之一并显式标注：
   - `gas/s` — 执行层 gas throughput
   - `tx/s` — 交易吞吐（仅当 tx 体积接近时与 gas/s 不冲突；否则不可互换）
   - `per-block CPU (ms/block)` — 单 block 计算时间
   - `IOPS` — 存储层读写次数
   严禁在同一行/同一 claim 中混用 throughput（gas/s、tx/s）与 latency（ms、p99）作为同一指标。
4. **Tier 归属同步**：每条声明同时携带分母标签 + 归属 Tier（A/B/C/D/E）；缺一即 `[UNATTRIBUTED]`。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-6
- **Required investigation_fields**:
  - `denominator`：`gas/s` | `tx/s` | `per-block CPU` | `IOPS` | `latency_p50` | `latency_p99`
  - `measurement_scenario`：block gas limit / tx mix / hardware / sync mode 四元组
  - `additivity_class`：`additive_within_scenario` | `non_additive` | `upper_bound_only`
  - `attribution_tier`：A/B/C/D/E（与 item-2 一致）

### item-8: 针对 Mantle 的改进建议与优先级排序

基于 item-1 ~ item-7 的差距清单，产出针对 mantle-elysium 的执行层改进建议清单：每条建议标注
(a) 来源差距编号、(b) 预期 TPS / gas-throughput 提升、(c) 改造成本（人月 / 风险）、
(d) 是否依赖上游 reth 同步、(e) 与其他 Wave（block-builder、gas params、batcher、DA）建议的
互斥/协同关系。优先级排序考虑"低风险、低成本、高收益"原则，至少给出 3 条具体建议（如：
对齐上游 reth 版本、启用并行 EVM、重构 MetaTx 热路径）。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| upstream_baseline | 该 item 对应的上游 reth commit/tag 基线，以及两 fork 的滞后量与同步策略 | item-1, item-2, item-6 |
| code_locations | 关键文件路径与行号引用（path:line），必须可点击复核 | all |
| modification_summary | 相对上游的改动摘要（增/删/改的模块、行数量级、是否触及热路径） | item-2, item-3, item-4, item-5, item-6 |
| perf_impact_estimate | 该改动/差距对执行层 gas-throughput 或 TPS 的量化影响（带证据等级：measured / reported / inferred） | item-1, item-2, item-3, item-4, item-5, item-6, item-7 |
| risk_and_correctness | 改动的正确性保证、冲突/回滚路径、潜在 consensus break 风险 | item-3, item-5, item-6 |
| config_parameters | 涉及的配置项（key、Base 取值、Mantle 取值、默认上游取值） | item-4, item-6 |
| benchmark_evidence | 已有公开 benchmark 或链上数据证据链接（含 Base Azul 博客、Reth issues、Mantle dashboards） | item-7 |
| recommendation_metadata | 改进建议的成本/风险/收益评分，依赖关系，是否需要 hardfork | item-8 |
| cross_topic_dependencies | 与其他研究主题（block-builder-flashblocks-throughput、gas-protocol-perf-config、sequencer-consensus-pipeline-perf）的接口/重叠 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Base vs Mantle reth fork 模块依赖对比图：两侧并列展示 `crates/execution`（Base）与 `mantle-elysium` workspace（Mantle）的 crate 依赖拓扑，高亮自定义/新增/移除的 crate；标注上游 reth 与 fork 边界 | mermaid | item-2 |
| diag-2 | flow | EVM 执行 pipeline 对比图：横向展示同一 block 从 fetch → senders recovery → state warm-up → execute（并行/串行）→ state-root → DB commit 的各阶段，Base 与 Mantle 双轨绘制，标注每阶段的耗时数量级与是否并行 | mermaid | item-3, item-6 |
| diag-3 | architecture | 状态存储与缓存架构对比图：从 EVM hot path → state cache → trie cache → MDBX env 的层次结构，附两 fork 的 cache 大小与 MDBX flags；高亮 flat state layout / path-based trie 等关键差异 | mermaid | item-4 |
| diag-4 | hierarchy | 改进建议优先级矩阵：以"改造成本"为 X 轴、"预期 TPS 提升"为 Y 轴，把 item-8 的建议落点到四象限（quick win / strategic / risky / 不推荐） | mermaid | item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | `base/base` 仓库 `crates/execution` 全目录代码扫描，附 commit SHA 与文件:行号引用 | 1 |
| src-2 | code_analysis | `mantle-xyz/reth` 仓库 `mantle-elysium` 分支代码扫描，附 commit SHA 与文件:行号引用 | 1 |
| src-3 | code_analysis | 上游 `paradigmxyz/reth` 作为 **Tier A baseline**（用于 diff 计算与上游版本基线确认） | 1 |
| src-3b | code_analysis | **Tier B baseline（Primary，必需）**：`ethereum-optimism/optimism` op-reth/v2.2.1（或 Mantle `Cargo.toml` 中引用的精确 op-reth source commit）作为 OP 继承层 baseline；必须与 src-3 并行扫描，杜绝把 OP 继承行为误归为 Mantle/Base 自有选择。同时要校验 `base/base` 是否亦从 op-reth 派生，确认 Tier B 对 Base 同样适用 | 1 |
| src-4 | official_docs | Base Azul 升级官方资料：blog.base.dev/introducing-base-azul、specs.base.org/upgrades/azul/* | 2 |
| src-5 | official_docs | Reth 官方文档与 release notes（paradigmxyz.github.io/reth、CHANGELOG.md），用于上游对照 | 2 |
| src-6 | expert_commentary | Reth 性能基准/issue/PR 讨论（Paradigm 博客、reth issues 中关于 parallel execution / MDBX tuning 的讨论） | 2 |
| src-7 | on_chain_data | Base/Mantle 主网典型 block 的 gas usage、tx mix、execution time（链上 RPC 或 dune 估算）作为 perf_impact_estimate 的校准数据 | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 (patch) | add | `attribution_tiers` frontmatter block (A–E) | 引入显式归属层级，避免把 OP 继承行为误归为 Mantle/Base 自有性能选择 | Review Round 1 finding（Orchestrator Dispatch 2026-05-20） |
| 1 (patch) | add | `source_requirements.src-3b` | 添加 `ethereum-optimism/optimism` op-reth/v2.2.1 作为强制 Tier B Primary baseline，与 `paradigmxyz/reth` 并行扫描 | Review Round 1 finding |
| 1 (patch) | revise | `item-1` 描述 + required investigation_fields | 要求双 baseline（Tier A 上游 reth + Tier B OP op-reth）滞后量化，禁止单边对比 | Review Round 1 finding |
| 1 (patch) | revise | `item-2` 描述 + required expected_output / per-tier 子表 | 强制 5 列 Tier bucket（A/B/C/D/E）输出，未归属条目须 `[UNATTRIBUTED]` | Review Round 1 finding |
| 1 (patch) | revise | `item-7` 描述 + required investigation_fields | 增加非加性 / 同一基准 / 分母标签 / Tier 归属同步四项 TPS 测量护栏 | Review Round 1 finding |
