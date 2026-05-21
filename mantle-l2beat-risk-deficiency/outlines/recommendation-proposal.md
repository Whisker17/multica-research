---
topic: "Proposer Failure 与 Exit Window 综合推荐改进方案"
project_slug: mantle-l2beat-risk-deficiency
topic_slug: recommendation-proposal
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: mantle-l2beat-risk-deficiency/outlines/recommendation-proposal.md
  draft: mantle-l2beat-risk-deficiency/research-sections/recommendation-proposal/drafts/round-{n}.md
  final: mantle-l2beat-risk-deficiency/research-sections/recommendation-proposal/final.md
  index: mantle-l2beat-risk-deficiency/research-sections/_index.md

scope: |
  综合评估 Mantle 在 L2Beat Risk Chart 的 Proposer Failure 与 Exit Window 两个红色/缺陷维度的改进选项，
  输出面向通过 L2Beat risk analysis 复核的推荐方案、优先级、工程难度、风险矩阵与 action items。
  Proposer Failure 需比较扩大白名单、permissionless proposer/self-propose、fallback/escape hatch、治理替换
  或 L2Beat 配置覆盖等路径；Exit Window 需比较 core-rollup timelock、Security Council emergency path、
  纯 timelock、分阶段迁移和即时升级权收敛方案。研究必须基于前序三个 final sections，并重新核验会影响
  推荐有效性的最新 L2Beat source/page 与 Mantle 关键合约状态。
audience: |
  Mantle 协议工程师、治理/安全团队、L2Beat 沟通/BD 负责人、Multica Technical Writer，以及需要将
  Proposer Failure 与 Exit Window 两条修复线落成工程路线图的决策者。读者预期理解 OP Stack、OP Succinct、
  output oracle、withdrawal proof、ProxyAdmin/timelock/multisig 基础概念，但需要明确的优先级、取舍、
  风险与可执行步骤。
expected_output: |
  - Proposer Failure 推荐改进方案，含扩大白名单、permissionless proposer/self-propose、fallback/escape hatch、
    governance/SC replacement、L2Beat override/documentation 等方案对比矩阵。
  - Exit Window 推荐改进方案，含 core ProxyAdmin timelock、critical owner role timelock、emergency path、
    Security Council 模式、纯 timelock 模式、7.5d/30.5d 阈值路径等方案对比矩阵。
  - 综合优先级排序表、工程难度和时间估算、风险评估矩阵、可执行 Action Items、实施建议时间线。
  - Evidence：明确引用 l2beat-risk-assessment-framework、mantle-proposer-failure-analysis、
    mantle-exit-window-analysis 三个 final sections 的关键发现，并补充一手源核验。
  - 4 张 Mermaid 图：Proposer Failure 方案决策树、Exit Window 实施时间线、优先级四象限、
    推荐实施路径流程图。

dependencies:
  blocked_by:
    - l2beat-risk-assessment-framework
    - mantle-proposer-failure-analysis
    - mantle-exit-window-analysis
  order: 4

guardrails:
  - 不把 L2Beat Stage 1/2 阈值混入 Risk Chart Proposer Failure 或 Exit Window sentiment 判定。
  - 不把 "uses SP1" 当作通过 Proposer Failure 的充分条件；必须区分 proof validity、caller permission、fallback liveness 与 L2Beat template semantics。
  - 不把治理/多签可恢复能力等同于用户自助退出；需按 L2Beat good/warning/bad 语义拆分。
  - 不把普通 timelock 改造视为充分条件；若任何 instant upgrade / owner / guardian / challenger bypass 仍存在，必须单独列为 blocking risk。
  - 不直接修改 `_index.md`，最终只提供 Index Entry Proposal。
  - 所有动态合约状态、L2Beat 页面、L2Beat source 观察必须记录 fetched_at / commit / block / chain metadata。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-21T13:55:09Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-21T13:55:09Z"
---

# Research Outline: Proposer Failure 与 Exit Window 综合推荐改进方案

## Items

### item-1: Evidence Baseline and Decision Criteria

建立推荐方案的证据基线与评价标准，避免在综合建议阶段重新发明 L2Beat 口径或引用过期事实。该 item 需要提取三个上游 final sections 的关键 findings：Risk Chart 判定规则、Mantle Proposer Failure 当前根因、Mantle Exit Window 当前根因，并对所有会影响建议有效性的动态事实做 fresh verification 计划。输出应形成一套可复用的评分框架，用于后续每个方案的 L2Beat pass likelihood、工程复杂度、安全风险、运营影响和审计需求打分。

- **Priority**: high
- **Dependencies**: none

### item-2: Proposer Failure Remediation Options and Recommendation

系统比较 Mantle 修复 Proposer Failure 的候选方案：扩大 approved proposer 白名单、多方运营者/委员会 fallback、permissionless self-propose、delay-based whitelist drop、Morph-style delayed `commit/propose with proof` fallback、OP Succinct fallbackTimeout/optimistic fallback、escape hatch、治理/SC 替换 proposer、以及仅补充文档或 L2Beat override 的非合约路径。每个方案必须回答：是否真正提供用户自助提款/自助出块路径，是否会把 L2Beat outcome 从 `PROPOSER_CANNOT_WITHDRAW` 移到 good/warning，是否兼容 Mantle 当前 OP Succinct + SP1 oracle，是否需要合约升级/审计/运营流程变更。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Exit Window Remediation Options and Recommendation

系统比较 Mantle 修复 Exit Window 的候选方案：将 core rollup ProxyAdmin owner 迁移到 timelock、将 `OPSuccinctL2OutputOracle.owner` / critical owner roles 同步迁移到 timelock、设置 regular path 至少 7.5d 或 30.5d delay、引入可审计 Security Council emergency path、拆分普通升级与紧急升级、限定/延迟 guardian/challenger/pause/output deletion 权限、以及分阶段从 instant multisig 迁移到 delayed governance。每个方案必须按 L2Beat `EXIT_WINDOW(upgradeDelay, exitDelay)` 公式复算 expected outcome，并明确哪些 bypass 会让 primary sentiment 仍为 `None` / bad。

- **Priority**: high
- **Dependencies**: item-1

### item-4: Cross-Dimension Dependencies and Minimum Passing Package

分析 Proposer Failure 与 Exit Window 两条修复线之间的依赖、并行性和最小可通过组合。该 item 需要回答：只修 Proposer Failure 是否足以让用户 exit window 有实际意义；只修 timelock 是否会因 Proposer Failure 仍红而被 L2Beat 认为不足；两个改进是否可以并行开发和审计；是否存在一个 shared governance/timelock/proposer fallback package 同时改善两个风险切片。输出应定义 "minimum viable L2Beat pass package" 与 "best-practice target package" 两套范围，并列出各自的 residual risks。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: Engineering Effort, Audit Scope, and Operational Impact

评估每个候选方案的工程工作量、审计范围、上线复杂度和运营影响。Proposer Failure 侧需要估算 oracle/fallback 合约改造、prover availability、permissionless proof verification gas/DoS 风险、白名单/role 管理、monitoring/runbook；Exit Window 侧需要估算 timelock 迁移、Safe/role handover、emergency runbook、upgrade scheduling、用户公告、incident response 延迟、监控告警。输出应包含时间估算区间、关键依赖、需要 Mantle 团队确认的 open questions，以及 L2Beat re-review 前应准备的 evidence package。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4

### item-6: Prioritized Roadmap, Action Items, and L2Beat Re-Review Plan

把前述技术结论转成可执行路线图：按 quick win、minimum pass、best-practice hardening、post-review cleanup 分阶段排列 action items，并给出 owner 类型、前置条件、验收标准和交付物。该 item 还要设计与 L2Beat 沟通/复核的材料清单：合约 diff、deployment addresses、timelock settings、permissionless fallback proof、source permalinks、page/config PR、风险说明和 migration timeline。输出应能直接支持 Technical Writer 写最终报告与 Mantle 团队立项。

- **Priority**: high
- **Dependencies**: item-4, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| upstream_finding_ref | 引用上游 final section 的具体结论、路径、commit/frontmatter metadata；用于区分 imported fact 与本轮新增判断。 | all |
| source_type | 证据类别：prior_final、l2beat_source、l2beat_page、verified_contract、on_chain_read、official_docs、repo_code、governance_docs、benchmark_project、expert_or_best_practice。 | all |
| source_url_or_ref | 永久链接、GitHub commit permalink、文件路径、合约地址/RPC read 描述、L2Beat 页面 URL 或本地 final path。 | all |
| fetched_at_or_observed_at | 页面抓取、链上读取、源码 checkout 或本地 artifact 观察的 ISO-8601 时间；不适用时写 N/A 并说明原因。 | all |
| source_commit_or_block | L2Beat/source repo commit、Mantle/op-succinct/morph repo commit、链 ID + block number、或 local artifact commit。 | all |
| option_name | 候选方案名称，如 expanded whitelist、permissionless self-propose、delay-based fallback、core timelock、SC emergency path、pure timelock。 | item-2, item-3, item-4, item-5, item-6 |
| l2beat_expected_effect | 该方案预期映射到的 L2Beat Risk View outcome、sentiment、threshold calculation、是否需要 `nonTemplateRiskView` 或 L2Beat config PR。 | item-2, item-3, item-4 |
| user_self_help_property | 用户在 proposer outage 或 unwanted upgrade 场景下是否能独立退出/自助提交 proof/root，以及依赖哪些 actor、delay、prover 或 contract path。 | item-2, item-4 |
| upgrade_delay_and_exit_delay | Exit Window 相关的 upgradeDelay、exitDelay、effective window、阈值差距与单位换算；需列出公式。 | item-3, item-4, item-5 |
| bypass_and_emergency_path | 任何能绕过 regular timelock/fallback 的 owner、guardian、challenger、Security Council、pause、delete output、ProxyAdmin 或 emergency route。 | item-3, item-4, item-5 |
| compatibility_with_mantle_architecture | 与 Mantle 当前 OP Succinct + SP1 oracle、bridge/portal、ProxyAdmin、Safe/role 权限、prover operations 的兼容性。 | item-2, item-3, item-5 |
| engineering_effort | 粗粒度工程难度和时间区间，含 smart contract、deployment/migration、prover infra、monitoring、docs/config PR。 | item-2, item-3, item-5, item-6 |
| audit_requirement | 是否需要审计、审计重点、可复用审计范围、上线前安全门槛与测试/verification requirements。 | item-2, item-3, item-5, item-6 |
| security_risk | 方案引入的安全风险：invalid proof acceptance、DoS/gas griefing、malicious proposer、delayed incident response、timelock governance capture、emergency abuse。 | item-2, item-3, item-5 |
| operational_impact | 对紧急修复、bridge incident response、on-call、monitoring、proposer/prover operations、governance scheduling、用户公告的影响。 | item-3, item-5, item-6 |
| priority_score | 推荐优先级评分，至少包含 L2Beat pass likelihood、risk reduction、implementation complexity、time-to-ship、audit burden、operational risk。 | item-4, item-5, item-6 |
| action_item | 可执行任务描述、owner 类型、dependencies、acceptance criteria、evidence deliverable。 | item-6 |
| confidence_and_open_questions | 结论置信度、仍需 Mantle/L2Beat 确认的问题、冲突来源、下一轮 deep research 必须验证的缺口。 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | decision_tree | Proposer Failure 改进方案对比决策树：从 "用户能否 permissionlessly publish/prove after proposer failure" 出发，区分 expanded whitelist、governance/SC replacement、delay-based self-propose、escape hatch、OP Succinct fallback、L2Beat override，并标注 expected L2Beat sentiment。 | mermaid | item-2, item-4 |
| diag-2 | timeline | Exit Window 改进实施时间线：current instant upgrade -> role inventory -> timelock deployment -> ProxyAdmin/owner migration -> emergency path constraint -> L2Beat evidence package；同时展示 7.5d minimum 与 30.5d green target 的 calculation checkpoints。 | mermaid | item-3, item-5, item-6 |
| diag-3 | comparison | 综合改进优先级四象限图：紧急度/impact × 工程难度/complexity，放置 proposer fallback、permissionless self-propose、core timelock、owner-role timelock、emergency-path redesign、L2Beat re-review 等 action clusters。 | mermaid | item-4, item-5, item-6 |
| diag-4 | flow | 推荐实施路径流程图：evidence refresh -> choose minimum pass package -> design/spec -> audit -> deploy/migrate -> monitor -> L2Beat config/page PR -> re-review -> best-practice hardening。 | mermaid | item-6 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | prior_final_sections | 必须引用三个已完成 final sections：`l2beat-risk-assessment-framework/final.md`、`mantle-proposer-failure-analysis/final.md`、`mantle-exit-window-analysis/final.md`，并摘录与推荐决策直接相关的 facts、thresholds、root causes、open questions。 | 3 |
| src-2 | l2beat_source | 最新或锁定 commit 的 l2beat/l2beat source：`riskView.ts`、`opStack.ts`、Mantle project config/discovery、Morph config、positive/control comparator configs、任何 `nonTemplateRiskView` 或 OP Succinct handling 变更；每条 source observation 需 commit SHA + line permalink。 | 8 |
| src-3 | l2beat_project_pages | 当前 L2Beat 项目页面或页面 snapshot：Mantle、Morph、至少一个 permissionless/self-propose 正向样本、至少一个 Exit Window positive 或 regular-only/control 样本；记录 fetched_at、页面文案和值。 | 4 |
| src-4 | mantle_contract_state | Mantle L1 production contracts 的 verified source 与 on-chain reads：OPSuccinctL2OutputOracle、OptimismPortal、ProxyAdmin、critical owners/roles、Safe owners/thresholds、guardian/challenger/timelock roles、finalization period、approved proposers/zero-address permissionless flag。 | 10 |
| src-5 | option_implementation_sources | 与候选方案相关的一手代码/文档：op-succinct fallback/permissionless features、Morph delayed permissionless proof path、OP Stack permissionless fault proof root proposal、escape hatch examples、timelock controller patterns、Security Council emergency designs。 | 6 |
| src-6 | governance_and_operations | 合约升级治理与运营实践来源：Mantle governance/Safe docs、OpenZeppelin TimelockController docs、relevant L2 governance/security council docs、incident response/timelock emergency practice；用于支撑运营影响和 emergency-path 设计。 | 4 |
| src-7 | audit_and_security | 审计/安全风险来源：OP Succinct/Mantle/Morph audit materials if available、known prover/fallback/timelock risks、formal docs on permissionless proof submission DoS or invalid-proof protection。若找不到公开 audit，需记录 negative search evidence。 | 3 |
| src-8 | l2beat_review_process | L2Beat 更新/复核路径的依据：project config PR pattern、L2Beat methodology/forum/source contribution evidence、历史项目 riskView 更新 PR 或 issue；用于估算 re-review action items 和材料清单。 | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
