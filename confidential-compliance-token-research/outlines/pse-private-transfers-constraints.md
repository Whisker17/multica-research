---
topic: "PSE Private Transfers 用户研究与产品约束分析"
project_slug: "confidential-compliance-token-research"
topic_slug: "pse-private-transfers-constraints"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate
artifact_paths:
  outline: "confidential-compliance-token-research/outlines/pse-private-transfers-constraints.md"
  draft: "confidential-compliance-token-research/research-sections/pse-private-transfers-constraints/drafts/round-1.md"
  final: "confidential-compliance-token-research/research-sections/pse-private-transfers-constraints/final.md"
  index: "confidential-compliance-token-research/research-sections/_index.md"
scope: |
  1. 从 PSE 用户研究提炼 private transfers blocker 分类（技术、产品、合规、生态）。
  2. 将 private transfer 痛点映射到 confidential RWA，区分哪些仍成立、哪些因机构 confidentiality 而变化。
  3. 比较 account-based confidential token 与 note-based shielded pool 的产品权衡，覆盖 composability、匿名性、余额模型、钱包 UX、证明/解密体验。
  4. 提炼 Mantle confidential compliance token 设计约束，覆盖钱包集成、远程 prover/加密 SDK、viewing key/auditor key、gas sponsor、institutional onboarding、DeFi 可组合性边界。
  5. 输出反模式清单，至少覆盖无披露通道、只追求匿名而忽略发行方控制、移动端证明不可用、匿名集依赖无法启动等。
  6. 按 requirements-framework rubric 给出产品/UX 维度补充评分建议。
audience: "Mantle 协议、产品、RWA、合规、钱包与 DeFi 集成团队；后续 adversarial review 与 technical writing agents"
expected_output: |
  后续 draft/final 需要把 PSE private transfers 用户研究与 dashboard 约束转化为 Mantle confidential compliance token 的产品要求、反模式清单、设计边界和 requirements-framework 产品/UX 评分补充建议。
revision_metadata:
  created_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-24T00:27:32Z"
  last_modified_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-24T00:27:32Z"
multica_issue_id: "687a44f7-c9b1-42a3-b435-99ea6fd09a29"
branch_name: "research/confidential-compliance-token-research/pse-private-transfers-constraints"
base_commit: "eefb63d9297c823d545a82ce36a2c31f7eceaba8"
language: "中文"
mode: "single-issue-lightweight"
reference_inputs:
  primary_web:
    - title: "User Research: Uncovering Problems in the Private Transfers Space"
      url: "https://pse.dev/blog/private-transfers-engineering-user-research"
      author: "John Guilding"
      published: "2026-05-08"
      access_date: "2026-06-24"
      note: "Rendered page metadata says the article summarizes 38 interviews. Its GitHub edit link returned 404 during outline preparation; the draft must recover and cite exact body claims from the rendered page, RSS, or another primary route before using detailed blocker counts or quotes."
    - title: "Private Transfers Analysis dashboard"
      url: "https://private-transfers.pse.dev/"
      repo: "https://github.com/privacy-ethereum/private-transfers-benchmarks"
      access_date: "2026-06-24"
      note: "Dashboard identifies itself as work in progress; use cited evaluation JSON and schema fields, and mark needsResearchReview entries where present."
  local_hard_inputs:
    - path: "confidential-compliance-token-research/research-sections/requirements-framework/final.md"
      issue: "WHI-266"
      commit: "9eb29a150f380f21add9b431b66fea2ee5d12881"
    - path: "evm-privacy-research/research-sections/erc7984-confidential-token/final.md"
      commit: "fdbda370e9e9137890c5bd2deb7752e03d76d0bc"
    - path: "evm-privacy-research/research-sections/zk-shielded-pool/final.md"
      issue: "WHI-260"
      commit: "788453b4097f37003337b943bcf6d7f8f68b02ba"
    - path: "evm-privacy-research/research-sections/privacy-eips-survey/final.md"
      issue: "WHI-257"
      commit: "957773b13b2f5a66354ccda4b7d0c79a7236b222"
---

# Research Outline

本节研究的核心问题是：PSE private transfers 的用户研究与 dashboard 不是直接给 Mantle 选择某个隐私协议，而是暴露 private transfer 产品进入真实用户、钱包、合规、生态和 PMF 场景时会失败的地方。后续 draft 必须把这些失败点转换成 Mantle confidential compliance token 的可执行产品约束，而不是停留在协议功能对照。

Source integrity note: PSE 文章的页面元数据可确认标题、作者、发布时间和“38 interviews”摘要，但 outline 阶段未能通过页面的 GitHub edit link 获取 Markdown 源文。后续 draft 在引用 PSE 用户研究的具体 blocker、样本表达、数量或访谈结论前，必须先通过 rendered page、RSS、PSE repo 或其他 primary route 复核正文。

## Items

### 1. PSE private transfers source extraction and blocker taxonomy

Research the PSE user-research article and Private Transfers Analysis dashboard as the product-discovery anchor. Extract blocker categories in four buckets: technical, product/UX, compliance, and ecosystem/PMF. Keep the article and dashboard distinct: the article is user-research evidence; the dashboard is a structured protocol-evaluation model with dimensions such as privacy, cost/performance, UX, decentralization/security, compliance, verifiability, state, and composability.

Required output:

- A concise blocker taxonomy with one-sentence definition per category.
- Evidence notes for each blocker: source, claim, affected user segment, and whether the evidence comes from article interviews, dashboard schema, evaluation JSON, or local prior research.
- A "do not overclaim" note for any PSE article detail that could not be verified from body text.

### 2. Private-transfer blocker to Mantle confidential RWA constraint mapping

Map private transfer pain points into confidential RWA and institutional token design. The analysis must explicitly split blockers into three outcomes: still applies unchanged, applies but changes because confidentiality is institutional/accounting-centric, or becomes less central because RWA issuers already control onboarding and disclosure.

Required output:

- A mapping table from PSE/dashboard blocker to Mantle RWA design constraint.
- A short narrative explaining which private-transfer pains are amplified by institutional usage: auditability, issuer control, onboarding, wallet operations, and explainable disclosure.
- A short narrative explaining which retail private-transfer assumptions are weaker for confidential RWA: pure anonymity as the north star, anonymous-set cold-start as the only privacy metric, and permissionless self-custody as the default integration path.

### 3. Account-based confidential token versus note-based shielded pool product tradeoff

Compare account-based confidential tokens, especially ERC-7984-style encrypted-balance interfaces and FHE-backed implementations, with note-based shielded pools such as Railgun, Privacy Pools, and EIP-8182-style designs. The comparison must be product-first: it should evaluate the model a wallet, issuer, auditor, and DeFi integrator would experience, not only cryptographic guarantees.

Required output:

- A product comparison table covering composability, anonymity, balance model, wallet UX, proof/decryption flow, disclosure model, issuer controls, and Mantle fit.
- A conclusion that distinguishes "best privacy primitive" from "best Mantle confidential compliance token substrate."
- A list of assumptions that would change the conclusion, such as native account abstraction adoption, protocol-level private transfer support, mature mobile provers, or standardized selective disclosure.

### 4. Wallet, prover, encryption SDK, and gas sponsor constraints

Turn the product blockers into concrete wallet and infrastructure requirements. Cover wallet integration, remote prover/proof delegation, encryption SDK ergonomics, local/mobile proving feasibility, decryption and handle display, private-state scanning, gas sponsorship, relayer/paymaster routing, recovery, and key management.

Required output:

- A user journey for "first institutional holder receives, views, transfers, and discloses a confidential token."
- A wallet/prover constraint list split into MVP, should-have, and risky-later categories.
- A gas sponsor/paymaster requirement that avoids requiring users to already hold public gas assets in a way that links identity, transfer intent, or portfolio activity.

### 5. Selective disclosure, auditor key, issuer control, and institutional compliance operations

Analyze disclosure and compliance as a first-class product surface rather than a legal appendix. The draft must cover viewing key, auditor key, issuer key, regulator or fund-admin access, holder-initiated disclosure, issuer-initiated controls, access revocation, audit logs, disclosure scope, and operational workflows for onboarding and investigations.

Required output:

- A disclosure matrix with actors, what they can see, who grants access, duration, revocation semantics, and audit trail.
- A warning section on permanent, overbroad, or invisible viewing access.
- A product requirement for explainable disclosure UX: users and institutions must understand which encrypted balances, transfers, or positions are visible to which parties.

### 6. DeFi composability and institutional onboarding boundaries

Define where confidential RWA can compose with Mantle DeFi and where it should not claim seamless composability. Address encrypted balances in AMMs/lending, adapter-based DeFi, oracle/indexer limitations, custody and fund-administrator workflows, bridge/redeem boundaries, KYC/KYB admission, transfer restrictions, and secondary-market controls.

Required output:

- A boundary map for DeFi use cases: safe MVP, possible with adapters, research-only, and anti-pattern.
- An onboarding flow for institution, issuer, wallet/custodian, auditor, and DeFi venue.
- A cold-start analysis for liquidity, counterparties, compliance participants, and privacy set, not only anonymous users.

### 7. Mantle confidential compliance token anti-pattern checklist

Produce a checklist that can be used during product/design review. The checklist should include at least the provided anti-patterns and add any discovered from sources.

Minimum anti-patterns:

- No disclosure channel: privacy is shipped without holder, issuer, or auditor visibility paths.
- Anonymity-only framing: design optimizes unlinkability while ignoring issuer controls, eligibility, freeze/recover, redemption, and regulated audit.
- Mobile proving unusable: normal wallets cannot generate or delegate proofs within acceptable latency, battery, and reliability budgets.
- Anonymous-set dependency cannot start: the product depends on a large active shielded pool before it offers institutional value.
- Gas sponsor missing: users need public gas funding that links identity or intent before they can use confidential transfers.
- Viewing keys are permanent and overbroad: disclosure cannot be scoped, revoked, logged, or explained.
- Remote prover/KMS is operationally opaque: sensitive material moves into infrastructure without trust, custody, or failure boundaries.
- DeFi composability is asserted without adapter constraints: encrypted balances are assumed to work in ordinary AMMs/lending without explaining price, liquidation, oracle, and indexer flows.

Required output:

- Checklist table with anti-pattern, symptom, why dangerous, detection question, mitigation, and severity.
- A short section mapping each anti-pattern back to at least one blocker or local research input.

### 8. Product and UX scoring addendum for requirements-framework rubric

Extend the WHI-266 requirements framework with product/UX scoring guidance. This should not replace the existing 0-5 axes; it should add a supplement reviewers can apply when judging confidential compliance token candidates.

Required output:

- Product/UX scoring table with 0-1, 2-3, and 4-5 anchors.
- Explicit mapping to existing axes: `privacy_coverage`, `compliance_capability`, `selective_disclosure`, `deployment_lightweight`, `engineering_delta`, `maturity`, and `mantle_fit`.
- Recommendation for how much product/UX evidence should affect borderline scores, especially when cryptography is strong but onboarding, wallet, disclosure, or gas flows are weak.

### Required core tables

The final section must include these tables:

| Table | Required columns |
| --- | --- |
| Private transfers blocker -> Mantle RWA design constraints | PSE/dashboard evidence; blocker_category; retail private-transfer pain; RWA carryover; institutional change; Mantle requirement; anti-pattern risk; rubric impact |
| Account-based confidential token vs note-based shielded pool | model; privacy coverage; balance model; composability; anonymity/cold start; wallet UX; proof/decryption; disclosure/compliance; issuer controls; Mantle fit |
| Mantle confidential compliance token anti-pattern checklist | anti-pattern; symptom; why dangerous; detection question; mitigation; severity |
| Product/UX scoring addendum | dimension; score 0-1; score 2-3; score 4-5; evidence required; linked WHI-266 axes |

## Fields

| Field | Meaning | Expected use |
| --- | --- | --- |
| `source_anchor` | Primary evidence source for a claim | Prevents mixing PSE interviews, dashboard schema, dashboard JSON, and prior research as if they were the same evidence type |
| `evidence_weight` | high / medium / low | High for primary source with explicit claim; medium for dashboard WIP fields or local synthesis; low for inference |
| `blocker_category` | technical / product_ux / compliance / ecosystem_pmf | Normalizes private-transfer blockers before mapping to Mantle |
| `user_segment` | retail holder / institution / issuer / auditor / wallet / DeFi venue / regulator / developer | Shows whose blocker is being solved |
| `private_transfer_blocker` | The original private-transfer pain | Keeps the mapping grounded in the PSE/dashboard problem space |
| `rwa_carryover` | unchanged / changed / weaker / not_applicable | Captures whether the blocker survives translation into confidential RWA |
| `institutional_delta` | How RWA confidentiality changes the blocker | Forces the draft to explain issuer, auditor, custody, and onboarding differences |
| `product_constraint` | Concrete Mantle requirement implied by the blocker | Converts research into design requirements |
| `ux_failure_mode` | What a real user/operator would experience if ignored | Supports product/UX scoring and anti-pattern detection |
| `compliance_disclosure_vector` | holder-initiated / issuer-initiated / auditor-access / regulator-access / none | Normalizes selective disclosure and auditability claims |
| `state_model` | account_balance / note_utxo / pool / hybrid / other | Supports the account-vs-note comparison |
| `proof_decryption_experience` | local_proof / remote_proof / FHE_handle / wallet_decrypt / scanning / none | Captures the wallet and prover surface |
| `wallet_integration_surface` | extension / mobile / custodian / smart account / SDK / dapp adapter | Shows where integration risk appears |
| `gas_sponsor_requirement` | none / optional / required / unresolved | Tracks whether public gas funding leaks usage or blocks adoption |
| `defi_composability_boundary` | native / adapter / constrained / research_only / unsafe_claim | Prevents vague DeFi compatibility claims |
| `rubric_score_impact` | Affected WHI-266 axes and expected direction | Links findings to requirements-framework scoring |
| `anti_pattern_flag` | Named checklist item, if any | Supports final anti-pattern checklist and review traceability |

## Diagram Expectations

| Diagram | Purpose | Required content |
| --- | --- | --- |
| Blocker-to-requirement flow | Show how source observations become Mantle requirements | PSE article/dashboard evidence -> blocker category -> RWA translation -> product constraint -> anti-pattern/rubric impact |
| Model tradeoff matrix | Compare account-based confidential token and note-based shielded pool models | Rows for account balance, note UTXO, shielded pool, hybrid; columns for composability, anonymity, disclosure, issuer control, wallet/prover burden |
| Actor/data visibility map | Make disclosure and audit relationships inspectable | Holder, issuer, auditor, regulator, wallet/custodian, prover, DeFi venue; encrypted data, decrypted data, viewing grants, logs |
| Institutional onboarding journey | Identify UX and operational blockers | KYB/KYC, wallet setup, key setup, receive token, view balance, transfer, disclose, redeem, incident/freeze |
| Requirement heatmap | Tie blockers to Mantle design priorities | Blocker categories versus wallet, prover, disclosure, issuer controls, gas sponsor, DeFi, onboarding, scoring axes |

## Source Requirements

Minimum source set for the draft:

| Source group | Minimum requirement | Notes |
| --- | --- | --- |
| PSE user research article | Use the article page and recover body claims before citing exact interview findings | Must include title, author, date, access date, and source caveat if body retrieval remains incomplete |
| PSE Private Transfers Analysis dashboard | Use the public dashboard and `privacy-ethereum/private-transfers-benchmarks` repository | Treat dashboard as WIP; preserve `needsResearchReview` caveats |
| Dashboard schema | Cite `project-evaluations/src/data/schema.ts` and `project-evaluations/src/data/evaluation-schema.ts` | Use to justify blocker dimensions and product fields |
| Dashboard project evaluations | Use at least Railgun and Privacy Pools JSON; add ERC-7984/Zama or other encrypted-token entries if needed | Compare real evaluation fields, not only general protocol descriptions |
| WHI-266 requirements framework | Cite `confidential-compliance-token-research/research-sections/requirements-framework/final.md` at commit `9eb29a150f380f21add9b431b66fea2ee5d12881` | Product/UX addendum must map back to existing axes |
| ERC-7984 confidential token research | Cite `evm-privacy-research/research-sections/erc7984-confidential-token/final.md` at commit `fdbda370e9e9137890c5bd2deb7752e03d76d0bc` | Needed for account-based confidential token analysis |
| Shielded-pool research | Cite `evm-privacy-research/research-sections/zk-shielded-pool/final.md` at commit `788453b4097f37003337b943bcf6d7f8f68b02ba` | Needed for Railgun, Privacy Pools, viewing keys, POI/ASP, and pool UX |
| Privacy EIPs background | Cite `evm-privacy-research/research-sections/privacy-eips-survey/final.md` at commit `957773b13b2f5a66354ccda4b7d0c79a7236b222` | Needed for EIP-8182 and account-abstraction/gas-adjacent context |
| Primary standards/docs | Include current ERC/EIP/spec docs where claims depend on standards behavior | Prefer standards, official docs, source repos, audits, or paper/spec text over secondary summaries |
| Compliance/institutional context | Use primary or near-primary sources for regulated token controls if referenced | Keep legal claims modest; focus on product requirements and operational constraints |

Integrity requirements:

- Distinguish primary evidence, local prior research, and inferred product implications.
- Do not copy claims from generated summaries without checking the underlying source.
- Mark any dashboard data that is pending or explicitly flagged for research review.
- Avoid treating private-transfer retail PMF as identical to institutional confidential RWA PMF.
- Quote sparingly and only where exact wording matters.

## Patch Log

| Date | Round | Change | Author |
| --- | --- | --- | --- |
| 2026-06-24 | 1 | Created initial candidate outline from Orchestrator dispatch, PSE/dashboard source reconnaissance, and local WHI-266/WHI-260/WHI-257/ ERC-7984 context. | Deep Research Agent |
