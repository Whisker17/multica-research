---
topic: "Mantle vs Base 性能差距综合分析与改进建议"
project_slug: base-perf-analysis
topic_slug: perf-gap-analysis-recommendations
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: base-perf-analysis/outlines/perf-gap-analysis-recommendations.md
  draft: base-perf-analysis/research-sections/perf-gap-analysis-recommendations/drafts/round-{n}.md
  final: base-perf-analysis/research-sections/perf-gap-analysis-recommendations/final.md
  index: base-perf-analysis/research-sections/_index.md

scope: |
  综合课题 1–7 的研究成果，量化各组件对 Mantle 与 Base 端到端 TPS 差距的贡献权重，
  构建瓶颈分层模型（Level 1 binding / Level 2 latent / Level 3 headroom），
  输出分阶段改进路线图（Quick Wins / 中期 / 长期），并附带风险评估矩阵和 ROI 排序。
  覆盖：执行层（WHI-55）、区块构建与 Flashblocks（WHI-56）、Gas 协议（WHI-57）、
  Sequencer 管线（WHI-58）、Batcher 管线（WHI-59）、DA 带宽（WHI-60）、
  背压机制（WHI-61）七个维度。

audience: |
  Mantle 协议工程团队决策者与执行层/共识层开发者；Multica 研究 squad 内部的
  Orchestrator 与 Adversarial Agent（审阅用）；OP Stack 生态中关注 L2 性能优化的
  技术负责人。读者熟悉 rollup 架构基础，已阅读或可访问课题 1–7 的 final 报告。

expected_output: |
  - 各组件 TPS 贡献权重饼图（Mermaid pie chart），附场景条件与不确定性说明
  - 瓶颈分层模型与 binding constraint 判定（Mermaid flowchart），每个候选标注 evidence_confidence
  - 改进路线图含时间轴与 TPS 里程碑（Mermaid gantt chart）
  - Quick Wins 清单（分三类：参数-TPS / 参数-硬化 / 代码-协议）
  - 中期 / 长期改进项 ROI 排序表，含场景范围与 caveats
  - 风险评估矩阵（影响 × 概率 × 工程复杂度）
  - Executive Summary（1 页以内）

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-20T10:00:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-20T15:30:00Z"

prerequisite_sections:
  - slug: execution-layer-reth-fork-comparison
    issue: WHI-55
    status: done
  - slug: block-builder-flashblocks-throughput
    issue: WHI-56
    status: done
  - slug: gas-protocol-perf-config
    issue: WHI-57
    status: done
  - slug: sequencer-consensus-pipeline-perf
    issue: WHI-58
    status: done
  - slug: batcher-pipeline-architecture
    issue: WHI-59
    status: done
  - slug: da-bandwidth-throughput-ceiling
    issue: WHI-60
    status: done
  - slug: batcher-sequencer-backpressure
    issue: WHI-61
    status: done
---

# Research Outline: Mantle vs Base 性能差距综合分析与改进建议

## Items

### item-1: Executive Summary 与现状快照

综合课题 1–7 的定量发现，建立 Mantle 与 Base 当前性能现状的对比快照：实测 TPS、empty block 率、gas 利用率、blob 利用率、L1 confirmation 延迟等关键指标。提供一页以内的 Executive Summary，给出"Mantle 距离 Base 当前水平还差多少、差在哪里"的简明结论，作为后续所有分析的锚点。现状快照中的每个指标须标注 `evidence_confidence`。

- **Priority**: high
- **Dependencies**: none

### item-2: 各组件 TPS 贡献权重分析

将端到端 TPS 差距分解到七个组件维度（执行层、区块构建/Flashblocks、Gas 协议、Sequencer 管线、Batcher 管线、DA 带宽、背压机制），量化每个组件对"Mantle 相对 Base TPS 差距"的贡献权重。方法论包括：(a) 根据各课题的量化发现（gas/s、block time overhead、empty block 率、blob 利用率等）建立归因模型；(b) 区分 demand-side（交易需求不足导致的空块）与 supply-side（系统瓶颈导致的吞吐上限）因素；(c) 标注当前 Mantle 处于"demand-bound"还是"supply-bound"状态。

**权重报告方式**：由于课题 WHI-59 中 `MaxPendingTransactions=1` 和 `TargetNumFrames=1` 为推断值（`inferred`），其对应的 TPS 增益仅在饱和-积压（saturated-backlog）场景下成立（`scenario-only`），权重百分比必须以**范围或场景条件区间**呈现（如 "Batcher 管线：15–30% under saturated-backlog; ≤5% under current demand-bound conditions"），而非单一精确百分比。Mermaid pie chart 必须附带 caveats 字段说明不确定性来源和场景假设。

- **Priority**: high
- **Dependencies**: none

### item-3: 瓶颈分层模型（Level 1 / 2 / 3）

构建三层瓶颈模型：Level 1 = Binding Constraints（当前实际限制 Mantle TPS 天花板的瓶颈）；Level 2 = Latent Bottlenecks（当 Level 1 解除后将成为新天花板的瓶颈）；Level 3 = Headroom（当前有充足余量、暂不限制 TPS 的组件）。每个 binding-constraint 候选须标注 `evidence_confidence`。

关键判定：

- **Level 1 候选（须逐一标注 evidence_confidence）**：
  - Batcher `MaxPendingTransactions=1`（`evidence_confidence: inferred` — CLI default=1 confirmed via flags.go:63; on-chain cadence ~448s consistent with N=1 but non-unique proof; WHI-59 R3-P1 framing："code-default risk + plausible runtime inference"）
  - Batcher `TargetNumFrames=1` / per-tx blob utilization（`evidence_confidence: inferred` — CLI default=1 confirmed; on-chain 1 blob/tx directly observed, 但 config attribution 为推断; WHI-59）
  - Gas 协议 decorative gasLimit 200B + 固定 base fee（`evidence_confidence: deployed-config-verified` — 200B on-chain confirmed via Mantlescan; 0.02 gwei fixed base fee confirmed via docs; WHI-57 item-1）
  - Demand-side 空块率 60.8%（`evidence_confidence: observed` — WHI-56 直接采样; 但 timing-recoverable vs demand-empty 归因未完成，需 WHI-56 Phase 0a 采样）
- **Level 2**：执行层缺少 ParallelStateRoot（WHI-55 `evidence_confidence: code-default` — 代码路径已验证，TPS 增益为 upstream reported ≥20–50% state-root reduction `[PENDING VERIFICATION]`）；Sequencer 单线程 event-loop（WHI-58 `evidence_confidence: observed`）
- **Level 3**：DA 带宽 ~1,480× headroom（WHI-60 `evidence_confidence: observed`）

该模型以 Mermaid flowchart 呈现层级关系和解锁路径。

- **Priority**: high
- **Dependencies**: item-2

### item-4: Quick Wins 清单（≤4 周落地）

从七个课题的改进建议中提取所有短期可落地改进，按**实施性质**分为三类 bucket：

**(a) 参数-TPS 杠杆（parameter-only TPS levers）** — 仅需修改运行时配置/参数，可直接提升饱和-积压场景下的吞吐上限：

- Batcher `MaxPendingTransactions` 从 1 提升到 5–10（WHI-59 R1; `evidence_confidence: scenario-only` — TPS 增益 5–10× 仅在 saturated-backlog 条件下成立; 当前 demand-bound 状态下增益有限）
- Batcher `TargetNumFrames` 从 1 提升到 6（WHI-59 R2b; `evidence_confidence: scenario-only` — per-L1-tx bytes ~6× increase, 但需 saturated-backlog + channel_fill_time ≪ RTT/N）
- `MaxChannelDuration` 调优（WHI-59; `evidence_confidence: code-default` — 定性"平滑作用", 非直接 TPS 提升）

**(b) 参数-硬化/定价杠杆（parameter-only hardening/pricing levers）** — 仅需 SystemConfig 链上调用或 sequencer 配置变更，改善协议健康度/价格信号/worst-case 稳定性，但**不直接提升 sustained TPS**：

- EIP-1559 参数调优：`SystemConfig.setEIP1559Params(denominator=250, elasticity=6)`（WHI-57 Q2; `evidence_confidence: deployed-config-verified` — Arsia 后 Holocene-style dynamic 1559 已解锁; 当前 denominator=8, elasticity=2 确认于 deploy config）
- 动态 base fee 启用：`minBaseFee=1 wei`, 移除固定 0.02 gwei（WHI-57 Q3; `evidence_confidence: deployed-config-verified`）
- gasLimit 从 decorative 200B 校准到 1G–2G：`SystemConfig.setGasLimit(...)`（WHI-57 Q4; `evidence_confidence: deployed-config-verified` — 200B confirmed on-chain; 目标 1G–2G 为保守 buffer, 精确值需执行层基准; **直接 TPS 不变**, 但恢复 1559 价格信号的前提条件）
- 恢复 `miner_setMaxDASize` RPC 以启用 DA Throttling（WHI-61 Phase 1; `evidence_confidence: code-default` — RPC 在 Mantle op-geth 中已被移除, 需重新添加; 注意：此项虽归为"参数"类, 但需 op-geth 微量代码变更来恢复 RPC endpoint, 复杂度 2–4 人周）

**(c) 代码/协议变更杠杆（code/protocol-change levers）** — 需要客户端代码修改和/或 hardfork 协调，实施复杂度显著高于 (a)(b)：

- **EIP-7825 per-tx gas cap 启用**（WHI-57 Q1; `evidence_confidence: observed` — Base 已在 Azul 激活; Mantle op-geth 显式 gate 在 `!IsOptimism()` 后面, 代码点: `txpool/validation.go:128`, `state_transition.go:536`, `miner/worker.go:765`, `gasestimator.go:73,84`; **需 op-geth fork 移除 gate + hardfork 协调**; 安全硬化措施, 非直接 TPS 提升）
- **gasLimit 大幅提升（如从 1G–2G 进一步到 10G+）** — 需要配合 state growth risk analysis、DoS surface 评估、执行层基准测试结果; 当前不宜盲目提升（WHI-57 item-1, item-6: Mantle 200B gasLimit 远超 sequencer 实际能力, "方向反了"）

每个 Quick Win 须标注：具体变更内容、`evidence_confidence`、预期 TPS 影响（范围值, 含场景条件）、实施复杂度、风险等级、所属课题来源。

- **Priority**: high
- **Dependencies**: item-3

### item-5: 中期改进路径（1–3 个季度）

整合需要工程开发但不需要架构重构的中期改进项，包括：(a) 接入 ParallelStateRoot（WHI-55 Reco-1, P0; `evidence_confidence: code-default` — upstream reported ≥20–50% state-root reduction `[PENDING VERIFICATION]`）；(b) Tier B cache 架构升级到 Tier C 模式（WHI-55 Reco-2, P1）；(c) Precompile cache + async receipt root（WHI-55 Reco-3/4, P1）；(d) Sequencer actor+task queue 重构（WHI-58; `evidence_confidence: inferred` — 5–30ms/block typical, ~95ms at boundary）；(e) rollup-boost 引入与 builder 分离（WHI-56 Phase 1; `evidence_confidence: inferred` — gated by Phase 0a ≥40% timing-recoverable 结论）；(f) Flashblocks 250ms sub-block 实现（WHI-56 Phase 2; `evidence_confidence: scenario-only` — ROI Scenario C 1.56× improvement, 依赖 empty-block attribution 结果）。每项需标注：工程量（人月）、预期 TPS 里程碑（范围值）、前置依赖、技术风险、`evidence_confidence`。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: 长期架构演进路径（3+ 个季度）

覆盖需要架构级变更或外部协调的长期改进：(a) kona-node 迁移——从 Go single event-loop 到 Rust actor model（WHI-58; 18–30 人月, 30–260ms compound improvement `evidence_confidence: inferred`）；(b) reth upstream rebase 到最新版本（WHI-55 Reco-6）；(c) token_ratio 机制重构，消除 BVM_ETH ERC20 EVM overhead（WHI-55 Reco-5）；(d) DA 策略升级（BPO2 target blob 利用率优化; WHI-60 当前 Level 3 但 TPS 上升后可能进入 Level 2; `evidence_confidence: observed` for current headroom）；(e) 完整背压机制体系建设（WHI-61 四类策略全面部署）。评估每项的技术不确定性、生态依赖（如 OP Stack upstream 变更节奏）、和组织资源需求。

- **Priority**: medium
- **Dependencies**: item-5

### item-7: 风险评估矩阵

对 item-4/5/6 中所有改进项建立风险评估矩阵，维度包括：(a) 技术风险（实现失败或性能不达预期的概率）；(b) 运营风险（部署后对现有网络稳定性的影响）；(c) 工程复杂度（人月 / 跨团队协调需求）；(d) 依赖风险（对上游 OP Stack / reth 版本的依赖程度）。特别关注：ParallelStateRoot 接入的 state trie 一致性风险、Flashblocks 250ms 出块的网络传播风险、kona-node 迁移的功能回归风险、gasLimit 大幅调整的 DoS 攻击面扩大风险。每项风险判断须标注 `evidence_confidence`。

- **Priority**: high
- **Dependencies**: item-4, item-5, item-6

### item-8: ROI 排序与改进路线图

综合 TPS 贡献权重（item-2）、工程成本（item-5/6）、风险评估（item-7）计算每个改进项的 ROI 得分（TPS 增益 / 工程成本 / 风险系数），输出按 ROI 降序排列的优先级清单。

**ROI 报告方式**：与 item-2 一致，当底层前置报告仅支持 `inferred` 或 `scenario-only` 级别的 TPS 增益估算时（特别是依赖 WHI-59 的 Batcher 参数调优项），ROI 排名和 TPS 增益必须以**范围或场景条件区间**呈现（如 "5–15% TPS gain under saturated-backlog conditions; ≤2% under current demand-bound conditions"），而非单一精确数值。Mermaid gantt chart 的 TPS 里程碑必须标注场景条件（demand-bound baseline vs saturated-backlog ceiling），并在 caveats 字段中说明：(i) 哪些估算依赖于推断值或特定负载场景，(ii) 核心不确定性来源（如部署配置未确认、demand-side 归因未完成等）。

在此基础上绘制时间轴式路线图（Mermaid gantt chart），标注每个阶段的 TPS 里程碑：当前 → Quick Wins 后（需区分 demand-bound vs saturated 两个场景）→ 中期目标 → 长期目标。路线图需考虑依赖关系（某些改进需要先完成前置项）和资源并行度约束。

- **Priority**: high
- **Dependencies**: item-2, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| quantitative_finding | 来自课题 1–7 的定量数据点（TPS、gas/s、延迟、利用率等），必须标注来源课题编号 | all |
| evidence_confidence | 每个定量声明和 TPS 影响估算的证据置信度，取值范围：`observed`（直接测量）、`code-default`（编译默认值, 未确认部署配置）、`deployed-config-verified`（链上或运营商配置已确认）、`inferred`（基于行为观察推断, 无配置访问）、`scenario-only`（仅在特定负载场景下成立, 如 saturated-backlog）。WHI-59 的 MaxPendingTransactions=1 和 TargetNumFrames=1 标 `inferred`; 这些参数的 TPS 增益标 `scenario-only` | all |
| tps_impact_estimate | 预估该改进对 Mantle TPS 的提升量级；当 evidence_confidence 为 `inferred` 或 `scenario-only` 时，必须以范围或场景条件区间呈现（如 "5–15% under saturated-backlog"），不得使用单一精确百分比 | item-2, item-4, item-5, item-6, item-8 |
| caveats | 显式说明估算/排名的不确定性来源：依赖推断值、特定负载场景假设、部署配置未确认、demand-side 归因未完成等 | item-2, item-8 |
| engineering_cost | 实施所需的工程资源（人月、周数）、跨团队协调需求 | item-4, item-5, item-6, item-7, item-8 |
| risk_dimensions | 技术风险、运营风险、依赖风险的定性/定量评估 | item-5, item-6, item-7 |
| bottleneck_level | 瓶颈层级归属：L1-binding / L2-latent / L3-headroom | item-2, item-3 |
| prerequisite_source | 数据或结论的来源课题（WHI-55 到 WHI-61 的具体 section 和 recommendation ID） | all |
| demand_vs_supply | 区分该瓶颈/改进属于 demand-side（交易需求）还是 supply-side（系统吞吐上限） | item-2, item-3, item-4 |
| dependency_chain | 该改进项的前置依赖（其他改进项必须先完成才能开始或生效） | item-4, item-5, item-6, item-8 |
| attribution_tier | 改动归属层级（Tier A–E：upstream reth / OP op-reth / Base overlay / Mantle overlay / Mantle external patches） | item-2, item-5, item-6 |
| quick_win_bucket | item-4 专用：标注改进项属于 (a) parameter-TPS, (b) parameter-hardening, 还是 (c) code-protocol | item-4 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | pie-chart | 各组件 TPS 贡献权重饼图：展示执行层、区块构建、Gas 协议、Sequencer 管线、Batcher 管线、DA 带宽、背压机制七个组件各自对 Mantle-Base TPS 差距的贡献百分比。**必须附带 caveats 注释**：(i) 标注哪些权重分量基于 `inferred` 或 `scenario-only` 级别估算, (ii) 标注 demand-bound vs supply-bound 两种场景下权重分布的差异, (iii) 对 WHI-59 相关分量使用范围而非精确数值 | mermaid | item-2 |
| diag-2 | flowchart | 瓶颈分层模型：顶层为 Level 1 (Binding)，中层为 Level 2 (Latent)，底层为 Level 3 (Headroom)；每层列出对应组件，箭头表示"当 L1 解锁后 → L2 成为新瓶颈"的解锁路径。每个节点旁标注 `evidence_confidence` 级别 | mermaid | item-3 |
| diag-3 | gantt | 改进路线图时间轴：横轴为时间（月），纵轴为改进项；分四个泳道（Quick Wins-TPS / Quick Wins-Hardening / 中期 / 长期），标注每个阶段完成后的 TPS 里程碑（以范围呈现, 区分 demand-bound baseline 和 saturated-backlog ceiling）；用 milestone 标记关键目标 | mermaid | item-8 |
| diag-4 | quadrant | 风险-收益象限图：X 轴为工程成本（人月），Y 轴为预期 TPS 提升（范围中值）；气泡大小表示风险等级；帮助识别"高收益低成本"的优先项。注意标注 `scenario-only` 项的 TPS 提升使用场景 ceiling 而非 expected 值 | mermaid | item-7, item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | 来自课题 1–7 final 报告的定量数据和改进建议（每个课题至少引用 1 处关键发现） | 7 |
| src-2 | on_chain_data | Base 与 Mantle 的链上性能指标（TPS、gas utilization、empty block rate、blob usage）用于现状快照 | 2 |
| src-3 | official_docs | OP Stack / reth / EIP 官方文档，用于验证参数默认值、协议约束和接口规范 | 3 |
| src-4 | code_analysis | Mantle op-geth / mantle-xyz/reth 关键配置文件和参数的代码级验证，确保 Quick Wins 的可行性 | 2 |
| src-5 | industry_reports | L2 性能基准报告或同类 rollup 的公开性能数据，用于对标和验证估算合理性 | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-2 | 添加权重报告方式约束：基于 inferred/scenario-only 级别的估算须以范围/场景区间呈现，pie chart 须附 caveats 字段 | Adversarial Review round 1 — finding: items 2/8 overstate precision |
| 2 | modify_item | item-3 | 为每个 Level 1 候选添加显式 evidence_confidence 标注；MaxPendingTransactions=1 和 TargetNumFrames=1 标 inferred（非 deployed-config-verified）；demand-side 空块率标 observed 但归因未完成 | Adversarial Review round 1 — finding: binding-constraint evidence not tagged |
| 2 | modify_item | item-4 | 拆分为三个 bucket：(a) parameter-TPS, (b) parameter-hardening, (c) code-protocol；EIP-7825 从无代码 quick win 移至 (c) 需 op-geth + hardfork；每项添加 evidence_confidence；TPS 影响改为范围值 | Adversarial Review round 1 — finding: quick-win taxonomy conflates parameter vs code changes |
| 2 | modify_item | item-5 | 为各中期改进项添加 evidence_confidence 标注 | Adversarial Review round 1 — evidence-confidence requirement |
| 2 | modify_item | item-8 | 添加 ROI 报告方式约束：场景依赖的 TPS 增益须以范围呈现；gantt chart milestone 须区分 demand-bound vs saturated 场景；caveats 字段必须说明不确定性来源 | Adversarial Review round 1 — finding: items 2/8 overstate precision |
| 2 | add_field | evidence_confidence | 新增 evidence_confidence 字段（applies_to: all），定义五级置信度标准 | Adversarial Review round 1 — required change |
| 2 | add_field | caveats | 新增 caveats 字段（applies_to: item-2, item-8），显式说明不确定性来源 | Adversarial Review round 1 — required change |
| 2 | add_field | quick_win_bucket | 新增 quick_win_bucket 字段（applies_to: item-4），标注三类 bucket 归属 | Adversarial Review round 1 — quick-win taxonomy split |
| 2 | modify_diagram | diag-1 | pie chart 须附 caveats 注释，标注 inferred/scenario-only 分量和场景差异 | Adversarial Review round 1 — uncertainty acknowledgment |
| 2 | modify_diagram | diag-2 | flowchart 每个节点须标注 evidence_confidence 级别 | Adversarial Review round 1 — evidence-confidence requirement |
| 2 | modify_diagram | diag-3 | gantt chart 泳道从三个拆为四个（Quick Wins-TPS / Quick Wins-Hardening / 中期 / 长期），TPS milestone 须区分 demand-bound 与 saturated 场景 | Adversarial Review round 1 — quick-win taxonomy + ranges |
| 2 | modify_diagram | diag-4 | quadrant 图须标注 scenario-only 项使用场景 ceiling 而非 expected 值 | Adversarial Review round 1 — ranges requirement |
