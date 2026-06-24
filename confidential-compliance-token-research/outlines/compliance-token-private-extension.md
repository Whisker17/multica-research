---
topic: "合规 Token 底座与 B20 私密扩展需求分析"
project_slug: "confidential-compliance-token-research"
topic_slug: "compliance-token-private-extension"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "confidential-compliance-token-research/outlines/compliance-token-private-extension.md"
  draft: "confidential-compliance-token-research/research-sections/compliance-token-private-extension/drafts/round-{n}.md"
  final: "confidential-compliance-token-research/research-sections/compliance-token-private-extension/final.md"
  index: "confidential-compliance-token-research/research-sections/_index.md"

scope: |
  M1 分析任务。复用 compliance-token-standards 与 requirements-framework 已完成结论，抽取 Mantle
  confidential compliance token 的合规 token 能力模型；分析 B20 协议骨架与 ERC-3643 应用层骨架；
  定义 encrypted balance / amount / allowance、密文事实上的 policy check、auditor disclosure、
  freeze/recovery under ciphertext 等 private feature 对合规骨架的新增要求；输出
  B20 + private feature 的 phase 1 must-have / optional / phase 2 boundary table；并标注哪些结论可
  直接复用旧项目文件，哪些必须对 Base/Mantle local code 重新核验。
audience: "Mantle 协议/战略团队、RWA/机构业务负责人、合规架构师、隐私后端评估作者、研究评审 agent"
expected_output: |
  outline 阶段输出本文件；final 阶段输出
  confidential-compliance-token-research/research-sections/compliance-token-private-extension/final.md。
  final 需给出合规 token 能力到 confidential extension 需求矩阵、B20 / ERC-3643 / TIP-20 复用边界、
  B20 + private feature phase 1 / optional / phase 2 能力表，以及 Base/Mantle 代码核验清单。

revision_metadata:
  created_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-24T00:40:00Z"
  last_modified_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-24T00:40:00Z"

multica_issue_id: "18fbd577-47e2-47f6-bfbf-a7519114df13"
report_issue_id: "7b29e4a8-01eb-4cbf-9b59-8e363f9a40e4"
branch_name: "research/confidential-compliance-token-research/compliance-token-private-extension"
base_commit: "eefb63d9297c823d545a82ce36a2c31f7eceaba8"
dependencies:
  - "requirements-framework"
order: 4
language: "中文"
mode: "composable-single-issue"

reference_inputs:
  direct_reuse:
    - path: "confidential-compliance-token-research/research-sections/requirements-framework/final.md"
      commit: "9eb29a150f380f21add9b431b66fea2ee5d12881"
      role: "CCT 术语口径、能力模型、rubric、证据复用规则、Inco/Optalysys 分类边界"
    - path: "compliance-token-standards/report/final-report.md"
      commit: "79d472632bd30a5354fbec396f807e0bb63bdea1"
      role: "合规 token 8 类 taxonomy、应用层 vs 协议层合规、Mantle 分阶段策略"
    - path: "compliance-token-standards/research-sections/base-b20-analysis/final.md"
      commit: "f42915ecd33c7f099d4ac0de89997390fc52d0b9"
      role: "B20 Factory / PolicyRegistry / ActivationRegistry / RBAC / policy scopes / Asset-Stablecoin variants / issuer controls"
    - path: "compliance-token-standards/research-sections/erc3643-trex-analysis/final.md"
      commit: "a260e40f58b0d8d2e15ba7bd263ab67a3288b6bd"
      role: "ERC-3643 ONCHAINID、Identity Registry、Claim Topics、Trusted Issuers、Modular Compliance、Agent roles"
    - path: "compliance-token-standards/research-sections/tempo-tip20-analysis/final.md"
      commit: "67c509b757699152095a8872b810817f6104aaba"
      role: "TIP-20 / TIP-403 支付型 precompile、memo、Payment Reconciliation、policy registry 生产经验"
    - path: "compliance-token-standards/research-sections/compliance-token-comparison/final.md"
      commit: "f42915ecd33c7f099d4ac0de89997390fc52d0b9"
      role: "ERC-3643 / B20 / TIP-20 横向能力差异与成熟度 trade-off"
    - path: "compliance-token-standards/research-sections/mantle-compliance-token-strategy/final.md"
      commit: "f42915ecd33c7f099d4ac0de89997390fc52d0b9"
      role: "Mantle 当前无自定义 precompile、双客户端/硬分叉约束、ERC-3643 短期先行策略"
  local_code_verification_targets:
    - path: "/Users/whisker/Work/src/networks/base"
      purpose: "仅当 final 需要确认 B20 当前代码是否仍符合旧项目 pinned 结论、是否出现 B20Security/redeem/private extension 新信号时使用"
    - path: "/Users/whisker/Work/src/networks/mantle"
      purpose: "核验 Mantle 当前是否仍无自定义 precompile、下一次 hardfork 是否仍未定义、op-geth/reth precompile 接入面是否有变化"
---

# Research Outline: 合规 Token 底座与 B20 私密扩展需求分析

本 section 的核心任务不是重做 `compliance-token-standards`，而是把旧项目的合规 token 能力语言迁移到 Confidential Compliance Token（CCT）语境：以 B20 作为协议骨架和能力类比，以 ERC-3643 作为短期应用层合规基线，以 TIP-20 作为支付/对账型 precompile 参考，再定义 private feature 对这些骨架新增的最小要求。

关键边界：`Base B20 token + private feature` 是产品和架构类比，不等于 Mantle phase 1 要复制 Base B20 precompile。Mantle 当前策略仍应默认轻量集成优先；precompile / hardfork / native encrypted accounting 属于 phase 2 或中长期协议路线，除非 local code verification 改变这一约束。

## Items

### item-1: 合规 Token 能力模型抽取与 CCT 映射

从既有合规 token taxonomy 中抽取 CCT 必须继承的能力模型：identity/KYC、transfer policy、issuer controls、sanctions/blacklist、recovery、legal metadata、payment reconciliation、audit/privacy。研究应把普通 compliance token 能力与 private feature 的新增要求并列表达，避免把“合规能力”与“加密账本能力”混为一谈。本项还要明确哪些能力属于 phase 1 token/product 必须回答的问题，哪些可由外部 identity registry、policy registry、auditor service 或 disclosure workflow 提供。

- **Priority**: high
- **Dependencies**: none

### item-2: B20 协议骨架与可复用能力语言

分析 B20 的协议骨架：B20Factory、PolicyRegistry、ActivationRegistry、RBAC、四类 policy scopes、Asset/Stablecoin variants、issuer controls、pause / mint / burn / burnBlocked / metadata / permit 等能力。重点不是复制 precompile，而是抽象出 Mantle CCT 可以复用的能力语言：deterministic factory、policy slot、policy registry、role-separated issuer control、feature activation、asset/stablecoin variant split。研究需标注 B20 结论来自既有文件还是需要重新核验 Base local code，尤其是 B20Security、redeem、batchBurn、securityIdentifier 或任何 private extension 相关新信号。

- **Priority**: high
- **Dependencies**: item-1

### item-3: ERC-3643 应用层合规骨架与短期路线价值

分析 ERC-3643 / T-REX 的应用层骨架：ONCHAINID、Identity Registry、Identity Registry Storage、Claim Topics Registry、Trusted Issuers Registry、Modular Compliance、Agent roles、freeze/partial freeze/forced transfer/recovery/pause/mint/burn。研究应解释 ERC-3643 为什么适合作为 Mantle phase 1 的合规基线或集成参照，并说明它缺少 encrypted amount/balance/allowance、密文 policy check 和 confidential disclosure 的哪些部分。

- **Priority**: high
- **Dependencies**: item-1

### item-4: TIP-20 / 支付对账能力的边界复用

从 TIP-20 / TIP-403 中抽取与 CCT 相关的支付型能力：memo、ISO currency、Payment Reconciliation、policy registry、StablecoinDEX / payment lane / fee infrastructure 的启发。研究应把 TIP-20 明确定位为支付/对账参考，而不是 Mantle RWA CCT 的主架构来源；同时识别 B20 Stablecoin variant 与 TIP-20 payment metadata 之间哪些能力可以作为 phase 1 optional 或 phase 2 product extension。

- **Priority**: medium
- **Dependencies**: item-1, item-2

### item-5: Private Feature 新增需求定义

定义 private feature 对合规骨架的新增要求：encrypted balance、encrypted transfer amount、confidential allowance、encrypted frozen balance / frozen amount、policy check over encrypted and plain facts、auditor/regulator/issuer disclosure、freeze/recovery/force-transfer under ciphertext、wrap/unwrap 或 redeem 时的披露边界。研究必须明确每项能力的实现责任可能在 token core、hook、policy engine、observer、KMS/coprocessor、identity service 或 offchain audit workflow 中，而不是默认都进入链协议。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

### item-6: B20 + Private Feature Phase Boundary Table

输出 `B20 + private feature` 的 phase 1 must-have / phase 1 optional / phase 2 native-precompile boundary table。phase 1 must-have 应聚焦可用、可审计、能 PoC 的最小 CCT；phase 1 optional 应列出对产品完整性有帮助但不阻塞 MVP 的能力；phase 2 应包含 hardfork/precompile、native encrypted accounting、protocol-level policy over ciphertext、ZK/FHE proof optimizations、native bridge/redeem 等高成本能力。每个划分都必须带理由、依赖和证据来源。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-5

### item-7: Base/Mantle Code Verification Boundary

列出哪些结论直接复用旧项目 final，哪些必须在 deep draft 前或 final 前对 local code 重新核验。Base 侧重点：B20 目录、policy/activation/factory 是否仍符合 pinned 结论，是否已有 B20Security 或 confidential/private 扩展进入主线。Mantle 侧重点：当前是否仍无自定义 precompile，硬分叉注册、op-geth/reth precompile 接入面、fraud-proof / op-program precompile 列表是否支持短期协议改动。

- **Priority**: high
- **Dependencies**: item-2, item-6

### item-8: Design Risks, Open Questions, and Non-Goals

整理 CCT 需求边界中的风险和非目标：过度承诺 Mantle 短期复制 B20 precompile、把 ERC-3643 当作 privacy solution、忽略 FHE ACL 撤销和审计日志、忽略 DeFi/bridge/redeem 的明文需求、把 TIP-20 支付链能力照搬到 Mantle RWA、把 vendor PoC 或本地分支信号当作生产事实。输出 deep draft 必须处理的 open question backlog。

- **Priority**: medium
- **Dependencies**: item-5, item-6, item-7

### Required Output Tables

Deep draft should include these tables even if final section headings change:

1. **Compliance Token Capability -> Confidential Extension Requirement Matrix**

| Compliance capability | Existing standard source | Confidential extension requirement | Phase target | Verification class |
|---|---|---|---|---|
| identity_kyc | ERC-3643 ONCHAINID / B20 policy list | KYC facts may remain offchain/plain while transfer amount is encrypted; define which claims are visible to policy engine | phase_1_must | direct_reuse + new synthesis |
| transfer_policy | B20 policy scopes / ERC-3643 Modular Compliance / TIP-403 | Policy must handle encrypted amount, encrypted allowance, receiver status, sanctions, and optional encrypted thresholds | phase_1_must | direct_reuse + private feature analysis |
| issuer_controls | B20 RBAC / ERC-3643 Agent roles | freeze, burn, recover, forced transfer, and disclosure must define ciphertext behavior and audit log | phase_1_must | direct_reuse + new synthesis |
| sanctions_blacklist | B20 BLOCKLIST / TIP-403 blacklist / ERC-3643 modules | Blocklist checks can stay plaintext-address based; encrypted amount does not remove sanctions duties | phase_1_must | direct_reuse |
| recovery | ERC-3643 recovery / B20 burnBlocked-like controls | Recover encrypted balance and allowances without leaking unrelated holder state | phase_1_optional | direct_reuse + new synthesis |
| legal_metadata | ERC-1643 legacy / B20 contractURI / TIP-1026 | Token/legal docs likely remain public or permissioned offchain; not a ciphertext core requirement | phase_1_optional | direct_reuse |
| payment_reconciliation | TIP-20 memo / payment infra / B20 memo | Encrypted transfers need payment reference strategy without revealing amount; memo privacy boundary explicit | phase_1_optional | direct_reuse + new synthesis |
| audit_privacy | compliance taxonomy + CCT rubric | Public audit vs issuer audit vs regulator disclosure must be separated | phase_1_must | requirements-framework reuse |

2. **B20 Skeleton -> CCT Product Analogy**

| B20 component | Reused idea | CCT adaptation | Do not assume |
|---|---|---|---|
| B20Factory | Deterministic token creation and variant configuration | Factory or deployer can create compliant confidential asset/stablecoin variants | Mantle phase 1 requires precompile factory |
| PolicyRegistry | Shared policy registry and policy IDs | Policy engine can bind address/KYC/sanctions/threshold rules to token | Policy can inspect encrypted facts without privacy backend |
| ActivationRegistry | Feature activation gate | Product feature flags / upgrade gates can stage confidential functionality | Mantle hardfork activation is available short term |
| RBAC | Separate admin/mint/burn/pause/metadata roles | Issuer, compliance officer, auditor, recovery agent, observer roles need explicit separation | One omnipotent owner is acceptable |
| Policy scopes | Sender/receiver/executor/mint receiver slots | Extend to spender/allowance/auditor/disclosure/freeze scopes where needed | B20 scopes already cover encrypted allowance or auditor disclosure |
| Asset/Stablecoin variants | Product split by asset type | RWA/security-like asset and stablecoin/payment variants may have different privacy/reconciliation needs | Both variants need identical private feature set |

3. **ERC-3643 Skeleton -> Private Feature Gaps**

| ERC-3643 component | What it solves | Gap for CCT | Candidate adaptation |
|---|---|---|---|
| ONCHAINID | Claim-based identity/KYC | Does not hide token amount/balance; claim privacy is limited | Reuse identity registry while encrypted token handles value |
| Identity Registry | Receiver verification | Sender/spender/auditor policies may need more scopes | Add policy hooks or registry adapters |
| Claim Topics / Trusted Issuers | KYC claim trust model | Policy over encrypted values needs backend-specific proofs/checks | Keep claims mostly plaintext/offchain, encrypt amounts |
| Modular Compliance | Business transfer rules | Rules using amount/balance thresholds need encrypted comparison or disclosure | Hook to FHE/ZK/coprocessor or fallback to plaintext thresholds |
| Agent roles | Freeze, forced transfer, recovery | Actions under ciphertext need key/disclosure/re-encryption semantics | Define privileged encrypted operations and logs |

4. **B20 + Private Feature Phase Boundary**

| Capability | Phase 1 must-have | Phase 1 optional | Phase 2 / native only | Reason |
|---|---|---|---|---|
| encrypted balance/amount | yes | - | native optimization later | CCT minimum requires confidential accounting, but not necessarily native precompile |
| confidential allowance | yes for ERC-20-like UX | - | native allowance registry optional | DeFi/custody approval flow breaks if allowance is public while balances are private |
| plaintext KYC/sanctions policy | yes | - | - | Can reuse ERC-3643/B20/TIP-403 style address/identity policy |
| policy over encrypted amount | minimum threshold/limit support | richer custom modules | native encrypted policy engine | Phase 1 can rely on privacy backend hooks/coprocessor |
| auditor disclosure | yes | richer regulator workflows | protocol disclosure registry | Institutional use requires authorized visibility |
| freeze/recovery under ciphertext | minimum freeze and recovery semantics | partial freeze and force-transfer | native encrypted recovery/precompile | Must define who can move or decrypt encrypted balances |
| legal metadata | - | yes | - | Important for RWA but not confidential core |
| payment reconciliation | - | yes | payment lane/native memo infra | Useful for stablecoin/payment variant; not CCT minimum |
| native precompile | - | - | yes | Mantle hardfork/client cost makes this phase 2 |

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| source_anchor | Exact file path, commit SHA, local repo path, or URL/access date supporting a claim | all |
| reuse_class | direct_reuse / bounded_reuse / new_synthesis / code_verification_required / local_branch_signal / out_of_scope | all |
| compliance_capability | identity_kyc, transfer_policy, issuer_controls, sanctions_blacklist, recovery, legal_metadata, payment_reconciliation, audit_privacy | item-1, item-5, item-6 |
| architecture_layer | application_contract, precompile_protocol, policy_registry, identity_registry, privacy_backend, observer_disclosure, bridge_redeem_adapter | item-2, item-3, item-4, item-5 |
| private_feature | encrypted_balance, encrypted_amount, confidential_allowance, encrypted_policy_check, auditor_disclosure, encrypted_freeze, encrypted_recovery, confidential_redeem | item-5, item-6 |
| phase_boundary | phase_1_must_have, phase_1_optional, phase_2_native, non_goal | item-5, item-6, item-8 |
| actor_scope | holder, issuer, agent, auditor, regulator, spender/operator, policy_admin, bridge_or_redeem_agent, defi_integrator | item-1, item-5, item-6 |
| disclosure_vector | authority, trigger, payload, scope, revocability, residual_leakage, audit_log | item-5, item-6, item-8 |
| code_verification_status | not_needed_reuse_only, base_code_required, mantle_code_required, both_code_required, blocked_by_missing_spec | item-2, item-7 |
| risk_label | overcommit_precompile, privacy_not_compliance, compliance_not_privacy, acl_revocation, defi_breakage, bridge_redeem_gap, vendor_or_branch_overclaim | item-8 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy | CCT capability stack showing compliance substrate, confidential accounting, policy engine, issuer controls, disclosure/audit, bridge/redeem, and DeFi adapters | mermaid | item-1, item-5 |
| diag-2 | architecture | B20 skeleton mapped to CCT adaptation: Factory, PolicyRegistry, ActivationRegistry, RBAC, scopes, variants, and private feature additions | mermaid | item-2, item-6 |
| diag-3 | flow | ERC-3643 transfer path plus private feature inserts: identity check, modular compliance, encrypted amount policy, disclosure/audit hooks | mermaid | item-3, item-5 |
| diag-4 | comparison | Phase boundary matrix from phase 1 must-have to optional to phase 2/native, with hardfork/precompile boundary highlighted | ascii | item-6 |
| diag-5 | flow | Code verification decision tree: old final reuse vs Base local code check vs Mantle local code check vs blocked/missing spec | mermaid | item-7 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | prior_research_final | Commit-pinned prior finals from `confidential-compliance-token-research` and `compliance-token-standards` listed in `reference_inputs.direct_reuse` | 7 |
| src-2 | code_analysis | Base local code only for claims that go beyond `base-b20-analysis/final.md` or need current-state verification | 1 |
| src-3 | code_analysis | Mantle local code for current precompile/hardfork/client constraints if final makes fresh Mantle implementation claims | 1 |
| src-4 | official_spec_or_primary_docs | ERC-3643 / B20 / TIP-20 / related official specs only when final claims exceed prior research or need updated confirmation | 2 |
| src-5 | issue_record | Multica issue/dispatch context for WHI-269 and dependency `requirements-framework` if process state or dependency acceptance is cited | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
