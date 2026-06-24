---
topic: "Mantle 轻量级集成路线与 PoC 计划"
project_slug: "confidential-compliance-token-research"
topic_slug: "integration-roadmap"
github_repo: "Whisker17/multica-research"
round: 1
status: approved

artifact_paths:
  outline: "confidential-compliance-token-research/outlines/integration-roadmap.md"
  draft: "confidential-compliance-token-research/research-sections/integration-roadmap/drafts/round-{n}.md"
  final: "confidential-compliance-token-research/research-sections/integration-roadmap/final.md"
  index: "confidential-compliance-token-research/research-sections/_index.md"

scope: |
  把 WHI-272 协议设计转化为 Mantle 可执行的轻量集成路线与 PoC 计划。覆盖：(1) 最小
  PoC 成功标准，包括 KYC/policy、mint、confidential transfer、audit disclosure、
  freeze/recovery 的最小闭环；(2) Phase 0/1 contract + external backend/SDK 集成路线，
  默认不改 Mantle 执行客户端；(3) Phase 2 native B20-like precompile / PolicyRegistry
  precompile 评估；(4) 合约、SDK、wallet、indexer、auditor tooling、KMS/operator、
  bridge、docs、security review 工程改动面；(5) p50/p95/p99 latency、encrypted op
  cost、burst、audit evidence、monitoring、failure recovery 等生产化观测项；(6) 风险
  门槛与停止条件；(7) 验证计划；(8) 一页路线图与 PoC checklist。
audience: "Mantle 小型协议/工程团队、RWA/机构产品负责人、合规与安全评审、Research Review Agent、后续 Technical Writer"
expected_output: |
  0-3 / 3-6 / 6-12 月阶段路线图，PoC 成功标准，工程改动面分析，性能与生产化观测项，
  风险门槛与停止条件，验证计划，以及面向工程团队的一页路线图和可执行 PoC checklist。

revision_metadata:
  created_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-24T13:15:19Z"
  last_modified_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-24T13:15:19Z"

multica_issue_id: "cf06b8fa-ed51-4b1e-8f3f-bfcd2f76197a"
report_issue_id: "7b29e4a8-01eb-4cbf-9b59-8e363f9a40e4"
branch_name: "research/confidential-compliance-token-research/integration-roadmap"
base_commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
dependencies:
  - "mantle-protocol-design"
  - "zama-confidential-rwa"
  - "compliance-token-private-extension"
language: "zh-CN"
mode: "single-issue"

reference_inputs:
  direct_reuse:
    - path: "confidential-compliance-token-research/research-sections/mantle-protocol-design/final.md"
      commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
      role: "WHI-272 protocol design；六模块 CCT 架构、接口、状态、流程、backend adapter、risk gates"
    - path: "confidential-compliance-token-research/research-sections/zama-confidential-rwa/final.md"
      commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
      role: "Zama / ERC-7984 / OZ RWA 集成细节；Mantle lightweight integration 表；Gateway/KMS/ACL 风险"
    - path: "confidential-compliance-token-research/research-sections/compliance-token-private-extension/final.md"
      commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
      role: "B20 + private feature phase boundary；backend maturity gate；Mantle local code verification boundary"
    - path: "confidential-compliance-token-research/research-sections/route-comparison/final.md"
      commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
      role: "主推 ERC-3643 + ERC-7984/OZ overlay；Inco/VOSA/Fhenix backup/reference buckets；native B20 phase 2 boundary"
    - path: "confidential-compliance-token-research/research-sections/requirements-framework/final.md"
      commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
      role: "CCT rubric、Mantle lightweight constraints、Inco framework 与 Optalysys 证据分类、engineering delta checklist"
  local_code_verification_target:
    path: "/Users/whisker/Work/src/networks/mantle"
    purpose: "仅当 deep draft 对 Mantle precompile/hardfork/current-client surface 作当前事实声明时使用；引用必须标注 repo path、commit SHA 和文件路径"
---

# Research Outline: Mantle 轻量级集成路线与 PoC 计划

本 outline 的目标不是重新设计协议，而是把已接受的 WHI-272 CCT 协议设计压成一个可执行、可验收、可停止的 Mantle PoC / pilot roadmap。核心路线必须保持轻量：Phase 0/1 默认是 **application contracts + external confidential backend / SDK / disclosure tooling**，不要求 Mantle 执行客户端、precompile、hardfork 或新 chain。Native B20-like precompile、PolicyRegistry precompile、native encrypted accounting 和 protocol disclosure registry 只进入 Phase 2 评估项。

Deep draft 的审查重点是：PoC 是否能演示最小闭环；路线是否足够小到 Mantle 小工程团队能执行；工程改动面是否完整；性能/生产化观察项是否能支撑 go/no-go；风险门槛是否能阻止研究结论变成不可控工程承诺。

## Items

### item-1: 最小 PoC 成功标准与演示闭环

定义 Mantle CCT PoC 的最小成功标准，避免一开始把 production CCT、native precompile、full private DeFi、private identity 或 cross-chain private settlement 混入 MVP。PoC 必须能演示 KYC/policy onboarding、confidential mint、confidential transfer、scoped audit disclosure、freeze/recovery 或明确写入不覆盖项。研究应把成功标准拆成 must-pass、should-pass、explicit non-goal，并为每个标准写出可观察证据、验收方式和失败处理。

Required PoC success criteria table:

| Capability | Minimum PoC standard | Evidence required | Out of scope unless explicitly added |
|---|---|---|---|
| KYC / policy | Receiver and sender eligibility checked through ERC-3643-style identity/policy substrate or equivalent adapter | Passing and failing transfer cases; policy config snapshot; source anchor | Private identity, fully encrypted KYC facts |
| Mint | Issuer can mint encrypted amount to eligible holder | Transaction/log evidence, encrypted balance handle, role proof | Native mint precompile |
| Confidential transfer | Eligible holder can transfer encrypted amount without revealing amount/balance plaintext | Transfer trace, before/after encrypted handles, no plaintext amount event | Hiding address graph, timing, event existence |
| Audit disclosure | Authorized auditor/issuer/regulator flow can disclose scoped payload and log request/grant/result reference | Disclosure request, approval, decrypt/re-encrypt evidence, expiry/revocation log | Full-history viewing key |
| Freeze/recovery | Minimum freeze or recovery ceremony defined and demonstrable, or explicitly deferred with legal rationale | Freeze/recovery test, admin role, audit trail, failure semantics | Unlogged issuer superpowers |
| Failure/degraded mode | Backend outage, disclosure denial, policy failure, and malformed proof have documented outcomes | Manual runbook, failing test or mock outage scenario | Production incident automation |

- **Priority**: high
- **Dependencies**: none

### item-2: Phase 0/1 lightweight integration route: contracts, backend, SDK, demo

Design the concrete 0-3 month and 3-6 month route around contracts plus external confidential backend and SDK, without Mantle client changes. Phase 0 should be architecture spike and backend readiness validation; Phase 1 should be a narrow PoC / testnet pilot with a named backend path, disclosure registry, minimal wallet/indexer UX, and a demo script. The route must preserve backend replaceability from WHI-272: public interfaces use encrypted handles/proofs/capability flags rather than Zama `euint`, Inco handle shapes, VOSA proof encoding, or native precompile selectors.

Required Phase 0/1 route table:

| Phase | Time window | Goal | Deliverables | Go/no-go gate |
|---|---|---|---|---|
| Phase 0 | 0-3 months | Feasibility spike and design freeze | PoC spec, backend selection memo, adapter interface, threat model, source trace map, mock disclosure service | Named backend support path or bounded non-Mantle PoC target |
| Phase 1a | 3-6 months | Testnet PoC with minimal closed loop | Contracts, SDK demo, KYC/policy fixture, mint/transfer/disclosure/freeze tests, dashboard metrics | Demo passes checklist, no hardfork dependency discovered |
| Phase 1b | 3-6 months | Pilot readiness assessment | Security review scope, operator runbook, latency/cost measurements, wallet/indexer pilot UX, incident drill | Production gates met or route remains PoC-only |

- **Priority**: high
- **Dependencies**: item-1

### item-3: Phase 2 native route assessment: B20-like and PolicyRegistry precompile

Define how to evaluate native Mantle integration only after PoC evidence exists. This item should not propose a native route as Phase 1 work; it should specify when to revisit B20-like precompile, PolicyRegistry precompile, native encrypted accounting, native disclosure registry, native bridge/redeem adapter, or deeper chain integration. If deep draft cites Mantle local code for precompile or hardfork feasibility, it must verify current repo path + commit SHA + file path under `/Users/whisker/Work/src/networks/mantle` and separate code plumbing from product/governance schedule.

Required Phase 2 assessment table:

| Native option | Evaluation trigger | Evidence needed | Expected cost surface | Default disposition |
|---|---|---|---|---|
| B20-like token precompile | PoC proves demand and app-layer gas/UX is bottleneck | Mantle op-geth/reth/revm precompile surface, B20 analogy, security spec | dual-client execution changes, fork activation, audits, fraud-proof / op-program review | Phase 2 only |
| PolicyRegistry precompile | Policy evaluation is stable, generic, and repeatedly used | Policy semantics, upgrade rules, scope model, local code feasibility | protocol governance, compatibility, storage/API stability | Phase 2 only |
| Native encrypted accounting | External backend latency/cost is unacceptable but CCT demand is validated | Cryptographic backend spec, precompile/API design, key governance, client integration | high cryptography + protocol + ops cost | long-term research |
| Protocol disclosure registry | App-layer disclosure logs prove useful but insufficient | Legal/audit requirements, privacy impact, revocation model | governance and data-retention commitments | phase 2 candidate |
| Native bridge/redeem adapter | Pilot needs chain-level settlement integration | bridge/redeem legal flow, plaintext boundary, failure recovery | bridge/security review and operational liability | separate proposal |

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 工程改动面与 ownership map

Map every engineering surface a small Mantle team would actually need to own, integrate, or outsource. The final output must cover contracts, SDK, wallet, indexer/explorer, auditor tooling, KMS/operator, bridge/redeem, docs/runbooks, security review, and governance/roles. Inco confidential ERC20 framework may be used only as PoC/test/interface inspiration, never as production security evidence or unreviewed code reuse.

Required engineering surface table:

| Surface | Phase 0/1 work | Owner / operator | Test artifact | Production blocker |
|---|---|---|---|---|
| Contracts | token, policy, disclosure, issuer control, backend adapter, wrapper/redeem stubs | Mantle app team / issuer integrator | unit/integration tests; ABI and upgrade review | audit, governance, upgrade risk |
| SDK / backend adapter | encrypted input generation, decrypt request, grant/revoke, capability flags | backend partner or Mantle integration team | SDK demo, mock and real backend conformance tests | backend support path and SLA |
| Wallet / custody UX | encrypt amount, view/decrypt balance, approve disclosure, show policy failure | wallet/custody partner | manual demo and UX acceptance script | unusable approval/decryption flow |
| Indexer / explorer | show encrypted activity, policy/disclosure logs, no plaintext amount leakage | indexer/explorer team | indexed event sample and dashboard | missing audit evidence or misleading UI |
| Auditor tooling | request/grant/result tracking, evidence export | issuer/auditor operator | disclosure report sample | no scoped evidence or revocation story |
| KMS / operator | key ceremony, threshold/decrypt governance, outage response | backend provider, issuer, or operator set | runbook and incident drill | key governance unacceptable |
| Bridge / redeem | explicit plaintext settlement boundary and fallback | issuer/custodian/bridge provider | redeem/unshield demo or deferred rationale | no legal settlement path |
| Docs / security review | deployment guide, threat model, failure modes, audit scope | project lead + security | review package | security review too large for Phase 1 |

- **Priority**: high
- **Dependencies**: item-2

### item-5: 性能、成本与生产化观测计划

Turn performance and operations into measurable PoC outputs. The research should define p50/p95/p99 latency targets or observed measurements for transfer, policy check, disclosure, freeze/recovery, redeem/unshield, encrypted input generation, backend decrypt, and indexer finality. Optalysys may frame FHE throughput/data-movement/hardware acceleration questions, but it must remain a performance/productionization reference and vendor narrative, not proof that any Mantle CCT route meets SLA.

Required observability table:

| Metric group | Metrics | Measurement method | Use in decision |
|---|---|---|---|
| User-facing latency | p50/p95/p99 for mint, transfer, policy check, disclosure request, balance view | testnet script and dashboard | UX go/no-go and wallet requirements |
| Backend latency | encrypted op latency, decrypt/re-encrypt time, KMS quorum time, Gateway/coprocessor retry time | backend logs and synthetic probes | backend maturity gate |
| Cost | gas, backend fee, operator cost, monitoring cost, audit/review cost | transaction traces and vendor/operator estimate | budget and production feasibility |
| Burst / reliability | concurrent transfers, decrypt burst, policy update burst, outage recovery time | load test and failure drill | pilot readiness |
| Audit evidence | disclosure logs, policy logs, admin action logs, result hashes, retention/export | auditor report sample | compliance acceptance |
| Monitoring | health checks, alerts, event indexing lag, stuck decrypt detection | dashboard spec | incident response |

- **Priority**: high
- **Dependencies**: item-2, item-4

### item-6: 风险门槛、停止条件与降级路线

Define explicit risk thresholds that stop the project, keep it in PoC-only mode, or downgrade it to reference/Phase 2 research. The deep draft must distinguish blocking production gates from PoC-acceptable caveats. It should include backend Mantle support, KMS/disclosure governance, vendor lock-in, performance, wallet UX, compliance disclosure sufficiency, bridge/redeem gaps, security review scope, and accidental hardfork/precompile dependency.

Required stop-condition matrix:

| Risk gate | Stop condition | Downgrade path | Evidence required |
|---|---|---|---|
| Backend availability | no Mantle support, self-host path, or bounded non-Mantle PoC target | reference only or Base-aligned PoC | backend statement, deployment test, or explicit non-Mantle scope |
| Disclosure governance | unclear grant/revoke/log authority or unacceptable historical access | redesign disclosure registry before pilot | authority matrix and audit log sample |
| Performance/SLA | p95/p99 or failure rate makes wallet/custody flow unusable | PoC-only; defer production | measured benchmark, not vendor claim |
| Vendor lock-in | public interface leaks backend-specific type/API | refactor adapter boundary | ABI/API review |
| Compliance sufficiency | audit disclosure or policy proof cannot satisfy issuer/regulator minimum | stop production path | compliance review memo |
| Wallet/UX burden | users/operators cannot complete encrypt/decrypt/disclosure flow reliably | custody-only pilot or stop | manual acceptance and error logs |
| Hardfork dependency | Phase 1 path requires Mantle client change/precompile | move to Phase 2 native track | local code verification and architecture decision |
| Security scope | audit scope exceeds small-team ability or unaudited PoC code is required | narrow PoC or stop | security review estimate |

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5

### item-7: 验证计划、source traceability 与成本估算

Specify how the deep draft and later PoC should be verified. The plan must include unit tests, integration tests, manual demo acceptance, adversarial review, source traceability, Mantle local code verification only when needed, cost estimate, and evidence classification. Each material conclusion in the final section must attach a path/URL and commit SHA, version, or access date; source gaps should be treated as blockers or caveats, not filled with inference.

Required validation plan table:

| Validation layer | What to verify | Artifact |
|---|---|---|
| Source traceability | every conclusion maps to local final path + commit SHA, official URL + access date, or local repo path + commit SHA + file path | evidence map |
| Contract unit tests | policy pass/fail, encrypted transfer path, disclosure registry, issuer roles, freeze/recovery semantics | test list and pass criteria |
| Integration tests | SDK encrypted input, backend decrypt/re-encrypt, indexer events, wallet/custody flow | testnet script |
| Manual acceptance | mint -> confidential transfer -> audit disclosure -> freeze/recovery demo | checklist and screenshots/log refs |
| Adversarial review | route is truly lightweight, native route staged correctly, stop conditions are enforceable | review response package |
| Cost estimate | contract/audit/backend/operator/wallet/indexer/security/doc effort | rough order-of-magnitude table |
| Local code verification | only if making current Mantle hardfork/precompile claims | repo path, commit SHA, file paths, searched terms |

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6

### item-8: 一页路线图与 PoC checklist packaging

Produce the final reader-facing package: a one-page roadmap and detailed PoC checklist that Mantle engineering/product can use to decide whether to start. The roadmap should summarize 0-3 / 3-6 / 6-12 month phases, owners, deliverables, gates, and downgrade paths. The checklist should be concrete enough to run as a project kickoff artifact, not just a narrative conclusion.

Required output package:

| Output | Content | Acceptance condition |
|---|---|---|
| One-page roadmap | phase timeline, deliverables, owners, go/no-go gates, Phase 2 trigger | readable without prior sections |
| PoC checklist | tasks across contracts, SDK/backend, wallet/indexer, auditor tooling, KMS/operator, bridge/redeem, docs/security | each row has owner, evidence, status, blocker |
| Decision memo | start / narrow / stop / defer-native recommendation | tied to measured gates |
| Caveat box | what this PoC does not prove | prevents production overclaim |

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| source_anchor | Exact local file path plus commit SHA, external URL plus access date/version, or local repo path plus commit SHA plus file path supporting each claim | all |
| reuse_class | direct_reuse, bounded_reuse, new_synthesis, code_verification_required, vendor_reference, engineering_poc_only, blocker_gap | all |
| phase_window | 0_3_months, 3_6_months, 6_12_months, phase_2_native, out_of_scope | all |
| chain_change_class | no_chain_change, app_integration, sidecar_operator_dependency, bridge_or_redeem_service, client_or_hardfork_required, unknown | item-2, item-3, item-4 |
| poc_success_signal | The observable pass/fail evidence for each PoC criterion | item-1, item-2, item-7, item-8 |
| engineering_surface | contract, sdk_backend, wallet_custody, indexer_explorer, auditor_tooling, kms_operator, bridge_redeem, docs_security, governance_roles | item-4, item-8 |
| performance_metric | p50, p95, p99, encrypted_op_cost, gas_cost, burst_capacity, recovery_time, indexing_lag, audit_export_time | item-5 |
| risk_gate | backend_support, disclosure_governance, performance_sla, vendor_lock_in, compliance_sufficiency, wallet_ux, hardfork_dependency, security_scope | item-6 |
| validation_method | unit_test, integration_test, manual_demo, adversarial_review, source_trace, local_code_check, cost_estimate, incident_drill | item-7 |
| checklist_status | not_started, planned, in_progress, passed, failed, deferred, blocked, non_goal | item-8 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | timeline | 0-3 / 3-6 / 6-12 month roadmap showing Phase 0 feasibility, Phase 1 PoC/pilot, and Phase 2 native evaluation trigger. Must show stop/downgrade gates between phases. | mermaid | item-2, item-3, item-6, item-8 |
| diag-2 | flow | Minimum PoC flow from KYC/policy onboarding through mint, confidential transfer, audit disclosure, freeze/recovery, and evidence capture. Label plaintext versus ciphertext versus disclosure boundaries. | mermaid | item-1, item-7 |
| diag-3 | architecture | Lightweight Phase 0/1 deployment architecture: contracts, backend adapter, confidential backend/Gateway/KMS or TEE/operator, SDK, wallet, indexer, auditor tooling, bridge/redeem service. Label no Mantle client change by default. | mermaid | item-2, item-4, item-5 |
| diag-4 | comparison | Engineering surface matrix with owner, work item, test artifact, blocker, and phase. | ascii | item-4, item-8 |
| diag-5 | decision | Risk gate and stop-condition decision tree: continue, narrow PoC, defer production, move to Phase 2 native, or stop. | mermaid | item-6 |
| diag-6 | checklist | One-page PoC checklist table suitable for Technical Writer conversion into `confidential-compliance-token-research/report/poc-checklist.md`. | ascii | item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | prior_research_final | Commit-pinned direct inputs from current `origin/main`: `mantle-protocol-design/final.md`, `zama-confidential-rwa/final.md`, and `compliance-token-private-extension/final.md` at commit `0a058bd286ab95d3a1ff7b76421a9e8627b675b4`. | 3 |
| src-2 | supporting_prior_research | Use `requirements-framework/final.md` and `route-comparison/final.md` for rubric, Inco/Optalysys classification, engineering delta, and route bucket rules. Cite paths and commit SHA. | 2 |
| src-3 | code_analysis | Mantle local repo analysis only if the draft makes current precompile/hardfork/client-surface claims. Required citation shape: `/Users/whisker/Work/src/networks/mantle` + subrepo commit SHA + file path + search/inspection method. | 1 |
| src-4 | official_backend_docs | Official docs/specs for the chosen backend and standards boundary: ERC-7984, ERC-3643, OpenZeppelin Confidential Contracts, Zama docs, Inco docs or other selected backend docs. Include access date or version. | 4 |
| src-5 | performance_reference | Optalysys and backend performance/SLA material may be used to frame latency/throughput/production questions only. Vendor claims must be labeled vendor_reference or self_report, not benchmark proof. | 2 |
| src-6 | engineering_poc_reference | Inco confidential ERC20 framework or comparable code may be used only as engineering PoC/test/interface inspiration. If used, cite repo commit and explicitly state unaudited/non-production status. | 1 |
| src-7 | issue_record | Multica issue description and Orchestrator dispatch for scope, expected output, Agent Directory, and acceptance criteria. | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|

## Verification Acceptance Criteria

| ID | Criterion | Applies To |
|----|-----------|------------|
| vc-1 | Defines a minimum demonstrable PoC closed loop covering KYC/policy, mint, confidential transfer, audit disclosure, and freeze/recovery or explicit deferral. | item-1 |
| vc-2 | Phase 0/1 route defaults to contracts + external backend/SDK/services and does not require Mantle hardfork, execution-client changes, or precompile. | item-2 |
| vc-3 | Native B20-like precompile, PolicyRegistry precompile, native encrypted accounting, and deeper chain integration are treated as Phase 2 evaluation only, with evidence requirements and triggers. | item-3 |
| vc-4 | Engineering surface covers contracts, SDK, wallet/custody, indexer/explorer, auditor tooling, KMS/operator, bridge/redeem, docs, governance, and security review. | item-4 |
| vc-5 | Performance/production plan includes p50/p95/p99 latency, encrypted operation cost, gas/backend/operator cost, burst behavior, audit evidence, monitoring, and failure recovery. | item-5 |
| vc-6 | Stop conditions and downgrade paths are explicit enough to prevent PoC results from being marketed as production readiness. | item-6 |
| vc-7 | Verification plan includes tests, manual demo, adversarial review, source traceability, cost estimate, and local code verification rules for Mantle hardfork/precompile claims. | item-7 |
| vc-8 | Produces a one-page roadmap and actionable PoC checklist with owner/evidence/status/blocker fields. | item-8 |
| vc-9 | Inco framework is classified as engineering PoC/reference only, and Optalysys is classified as performance/productionization reference only. | item-4, item-5, item-7 |
| vc-10 | Every material conclusion in the final section has a path/URL and commit SHA, version, or access date. | all |
