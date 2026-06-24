---
topic: "Confidential RWA 候选方案补充调研"
project_slug: "confidential-compliance-token-research"
topic_slug: "confidential-rwa-candidates"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "confidential-compliance-token-research/outlines/confidential-rwa-candidates.md"
  draft: "confidential-compliance-token-research/research-sections/confidential-rwa-candidates/drafts/round-{n}.md"
  final: "confidential-compliance-token-research/research-sections/confidential-rwa-candidates/final.md"
  index: "confidential-compliance-token-research/research-sections/_index.md"

scope: |
  在 Zama 之外，筛选并调研最符合 Mantle private RWA / confidential compliance token 需求的产品、协议或设计，
  形成候选方案集合与初筛结论。候选按 A/B/C 层分级：A 层（Inco confidential token/RWA 方案、
  Inco confidential ERC20 framework 代码级 PoC、VOSA-RWA/VOSA-20、Nightfall/EY enterprise）；
  B 层（Railgun/Privacy Pools、Paladin/Privacy Groups、Fhenix/CoFHE、Optalysys 性能/生产化参考）；
  C 层架构 benchmark（Aztec/Starknet STRK20/EIP-8182）。复用 evm-privacy-research WHI-255 到 WHI-261
  已完成 final artifacts 为输入，不重复通用 EVM privacy 内容。
audience: "Mantle 协议/战略团队、RWA/机构业务负责人、合规架构师、研究评审 agent、后续路线裁决作者"
expected_output: |
  final 阶段输出候选方案分层 profile 表、Inco confidential ERC20 framework 代码级 PoC profile（pin commit）、
  Optalysys FHE 性能/生产化约束 profile、候选初筛矩阵（主候选/强备选/局部补强/参考/出局）、
  与 Zama 差异标注，并明确不预先替 WHI-271 做最终路线裁决。

revision_metadata:
  created_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-24T00:21:06Z"
  last_modified_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-24T00:21:06Z"

multica_issue_id: "84e8d44a-f970-4531-a351-f9d801da4947"
report_issue_id: "7b29e4a8-01eb-4cbf-9b59-8e363f9a40e4"
branch_name: "research/confidential-compliance-token-research/confidential-rwa-candidates"
base_commit: "eefb63d9297c823d545a82ce36a2c31f7eceaba8"
requirements_framework_path: "confidential-compliance-token-research/research-sections/requirements-framework/final.md"
requirements_framework_commit: "eefb63d9297c823d545a82ce36a2c31f7eceaba8"
language: "中文"
mode: "single-issue-composable"
---

# Research Outline: Confidential RWA 候选方案补充调研

## Items

### item-1: 研究边界、复用输入与候选纳入规则

本项先固定研究边界：本 section 不重跑完整 EVM privacy landscape，只抽取与 Mantle private RWA / confidential compliance token 直接相关的候选与差异结论。Deep draft 必须把 WHI-266 的 rubric 作为评分基线，并把 `evm-privacy-research` WHI-255 到 WHI-261 的 accepted final artifacts 作为复用输入；凡复用旧结论，必须标注路径、commit SHA 与复用边界。候选纳入规则应围绕 RWA/合规相关性、轻量集成可能、选择性披露、成熟度、Mantle 适配五个维度，避免把通用隐私项目误升格为 confidential RWA 候选。

- **Priority**: high
- **Dependencies**: none

### item-2: A 层候选一 - Inco confidential token/RWA 方案与代码级 PoC

本项深入调查 Inco 在 confidential token / RWA / compliant privacy 方向的产品、文档、合作叙事与实际工程证据，并与 Zama 形成差异标注。必须分开处理两类证据：Inco Network / Lightning / Atlas 作为机密计算或 confidential token 方案，和 `Inco-fhevm/confidential-erc20-framework` 作为 unaudited engineering PoC。代码级 profile 必须 pin GitHub commit，梳理 wrapper、confidential ERC20、compliant transfer rules、Identity/credential 示例、delegated viewing、transfer-rule failure semantics、测试/部署流程与未审计风险。

- **Priority**: high
- **Dependencies**: item-1

### item-3: A 层候选二 - VOSA-RWA/VOSA-20 与 Nightfall/EY enterprise confidential token

本项覆盖两组 A 层候选。VOSA 方向应复用 `vosa-standards/final.md` 的 exposed-graph、轻量、合规门控、未审计论坛草案结论，并补充本项目需要的 RWA/compliance token fit/gap。Nightfall/EY 方向应重点调研 enterprise confidential token 经验、X.509/企业身份、rollup/operator 模型、RWA/合规披露适配性与生产成熟度；不能把 token-only confidential transfer 直接写成完整 confidential compliance token。

- **Priority**: high
- **Dependencies**: item-1

### item-4: B 层候选 - Railgun/Privacy Pools、Paladin/Privacy Groups、Fhenix/CoFHE、Optalysys

本项对 B 层做 fit/gap profile，不要求写成主路线。Railgun/Privacy Pools 应定位为合规选择性披露或 association-set 补强，而非 RWA token 标准；Paladin/Privacy Groups 应定位为企业业务流程隐私和 privacy domains 参考，而非直接 token ledger 标准；Fhenix/CoFHE 应作为 backend-replaceable confidential compute 候选，与 Zama/Inco 差异化比较；Optalysys 只作为 FHE 性能、成本、SLA、硬件加速与运维生产化参考，不得写成 token framework 或 Mantle 集成协议。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: C 层架构 benchmark - Aztec、Starknet STRK20、EIP-8182

本项仅做 benchmark 摘要和反例/上限参照，避免扩大为完整 privacy landscape。Aztec 应作为隐私原生链/私密状态上限与非轻量反例；Starknet STRK20 应复用 shielded-pool final 中关于 STRK20 成熟度、Cairo/STARK 基底和未交付/未审计 caveat；EIP-8182 应作为协议层 unified shielded pool benchmark，重点记录需硬分叉/协议层改动、全局匿名集和 Mantle 不适合作 phase 1 轻量候选的原因。

- **Priority**: medium
- **Dependencies**: item-1

### item-6: 候选分层 profile 表与逐候选 source pack

本项产出 deep draft 的核心结构化 profile 表。每个候选至少应包含：候选层级、角色定位、隐私原语、合规/披露模型、issuer controls、桥接/赎回适配、部署形态、成熟度、Mantle 集成 delta、与 Zama 差异、证据等级、关键 gap。每个候选还必须有 source pack：官方文档/规格、代码仓库或审计、既有 final artifact、外部 vendor 或二手来源，均标注访问日期或 commit。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4, item-5

### item-7: 候选初筛矩阵与 Zama 差异标注

本项将候选按 `主候选 / 强备选 / 局部补强 / 参考 / 出局` 形成初筛矩阵，但不得替 WHI-271 做最终路线裁决。矩阵应解释每个候选相对 Zama 的差异：信任模型、成熟度、Mantle 部署轻量度、RWA 合规能力、披露机制、性能/SLA 风险和工程 PoC 价值。结论必须保留 uncertainty：例如 Inco PoC 可作为代码级参考但不可作为生产成熟度证据，Optalysys 可作为生产化约束但不可作为协议候选。

- **Priority**: high
- **Dependencies**: item-6

### item-8: Gap Register、降权/出局理由与后续 WHI-271 输入

本项记录未解决问题、降权原因和需要 WHI-271 或后续工程 PoC 判断的内容。至少覆盖：厂商 roadmap/benchmark/partnership 是否独立验证；未审计代码或论坛草案的安全边界；FHE ACL 撤销性与合规最小披露冲突；TEE/硬件信任的监管叙事；privacy pool 与 RWA issuer controls 的错位；独立链/硬分叉方案为何不适合 phase 1。输出应是路线裁决输入，而不是路线裁决本身。

- **Priority**: medium
- **Dependencies**: item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| candidate_tier | A/B/C 分层及其纳入理由；A=深度候选，B=fit/gap 补强，C=benchmark/反例 | all |
| candidate_role | 主候选、强备选、局部补强、参考、出局的初筛角色；最终裁决留给 WHI-271 | item-6, item-7, item-8 |
| source_anchor | 每条关键结论的文件路径、URL、commit SHA、访问日期或 issue/comment id | all |
| evidence_weight | direct_reuse、official_primary、code_analysis、audit_report、vendor_self_report、secondary_corroboration、engineering_poc、performance_reference、unverified | all |
| protected_data | amount、balance、counterparty、transaction_graph、business_state、contract_logic、order_flow、metadata 中实际保护和残余泄露 | item-2, item-3, item-4, item-5, item-6 |
| compliance_capabilities | identity/KYC、AML/sanctions、transfer_policy、issuer_controls、freeze/recovery/force_transfer、audit_log、redeem/bridge_controls | item-2, item-3, item-4, item-6 |
| disclosure_vector | authority、trigger、payload、scope、revocability、residual_leakage；必须沿用 WHI-266/WHI-254 的 6D 披露口径 | item-2, item-3, item-4, item-6, item-7 |
| deployment_shape | contract_only、wrapper、sidecar、coprocessor、TEE_network、FHE_backend、rollup、native_chain、protocol_hardfork、hardware_reference | item-2, item-3, item-4, item-5, item-6 |
| lightweight_score_inputs | no_new_chain、no_new_bridge、no_hardfork、no_full_node、new_operator_stack、new_sdk_wallet_work、commercial_dependency | item-2, item-3, item-4, item-5, item-7 |
| maturity_status | final_standard、draft_standard、forum_draft、audited、unaudited_poc、testnet、mainnet、production_customer、roadmap、marketing_only | item-2, item-3, item-4, item-5, item-6 |
| code_profile | repo URL, pinned commit, modules, tests, deploy flow, security disclaimers, license, production caveats | item-2 |
| performance_constraints | latency, throughput, cost, hardware dependency, SLA, audit posture, operational model, independent verification status | item-4, item-7, item-8 |
| zama_difference | Concrete difference from Zama/OZ path: trust model, privacy backend, compliance modules, integration cost, maturity, roadmap dependency | item-2, item-3, item-4, item-5, item-7 |
| gap_status | answered_by_reuse、needs_primary_research、needs_code_read、needs_independent_verification、out_of_scope、for_WHI_271 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy | Candidate landscape map: Zama baseline at center, A/B/C tiers around it, with each candidate's role as product route / code PoC / compliance supplement / performance reference / benchmark | mermaid | item-1, item-6, item-7 |
| diag-2 | comparison | Confidential RWA capability stack comparison across Inco, VOSA, Nightfall/EY, Railgun/PP, Paladin, Fhenix, Optalysys, Aztec/STRK20/EIP-8182 | mermaid | item-2, item-3, item-4, item-5 |
| diag-3 | flow | Inco confidential ERC20 PoC flow: wrap/mint, encrypted balance/amount, transfer rules, delegated viewing, identity check, unwrap/redeem, and where audit/ACL caveats enter | mermaid | item-2 |
| diag-4 | matrix | Initial screening matrix flow from candidate evidence to `主候选 / 强备选 / 局部补强 / 参考 / 出局`, including explicit "not WHI-271 final decision" gate | ascii | item-7, item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | prior_research_final | WHI-266 requirements framework final at `confidential-compliance-token-research/research-sections/requirements-framework/final.md`, pinned to `eefb63d9297c823d545a82ce36a2c31f7eceaba8` or per-file commit if newer | 1 |
| src-2 | prior_privacy_final | Reuse `evm-privacy-research` accepted finals for ERC-7984, confidential coprocessor, VOSA, shielded pools, Aztec, EEA benchmark, privacy EIPs; each reused claim needs path and commit SHA | 5 |
| src-3 | inco_primary | Inco official docs/blogs and Circle/Inco confidential ERC20 materials for product/RWA/compliance claims; mark roadmap and partnership claims separately | 3 |
| src-4 | inco_code_analysis | `Inco-fhevm/confidential-erc20-framework` or successor repo; pin exact commit, inspect contracts/tests/deploy docs, and record README/security/audit caveats | 1 |
| src-5 | vosa_primary | VOSA, VOSA-20, VOSA-RWA primary forum/spec threads plus any linked repos; preserve forum maturity, author, reply count/status, access date | 3 |
| src-6 | nightfall_ey_primary | EY/Nightfall official docs, GitHub repos, audit/security notes, enterprise token/confidential payment materials, and current deployment status | 3 |
| src-7 | shielded_pool_primary | Railgun and Privacy Pools official docs, audit reports, protocol docs, association-set/PPOI docs, and on-chain/TVL sources if used for maturity | 4 |
| src-8 | paladin_primary_or_prior | Paladin/Privacy Groups official LFDT/Kaleido docs or accepted prior internal research; clearly distinguish privacy-domain business workflow evidence from token-ledger evidence | 2 |
| src-9 | fhenix_primary | Fhenix/CoFHE official docs, GitHub or developer docs, EigenLayer/restaking materials, deployment status, audit/security posture | 3 |
| src-10 | optalysys_performance | Optalysys RWA/FHE/photonic acceleration pages plus at least one independent or methodological source for FHE performance limits if available; vendor claims must be labeled self-reported | 3 |
| src-11 | c_benchmark_sources | Aztec, Starknet STRK20, and EIP-8182 official docs/specs or prior accepted finals; use only for benchmark and anti-scope-expansion evidence | 3 |
| src-12 | zama_comparator | Zama/OZ baseline sources or accepted final artifacts sufficient to state differences; do not re-litigate Zama except for direct delta fields | 2 |
| src-13 | audit_or_security | For any candidate scored above "reference", look for audit/security documentation or explicitly state no public audit found | 1 |
| src-14 | issue_record | Multica issue/comment records for WHI-270 dispatch, WHI-266 dependency, and any reused WHI-255 to WHI-261 artifact if needed to verify accepted status | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
