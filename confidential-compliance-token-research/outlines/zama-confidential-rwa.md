---
topic: "Zama Confidential RWA Tokenization 深度分析"
project_slug: "confidential-compliance-token-research"
topic_slug: "zama-confidential-rwa"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate
artifact_paths:
  outline: "confidential-compliance-token-research/outlines/zama-confidential-rwa.md"
  draft: "confidential-compliance-token-research/research-sections/zama-confidential-rwa/drafts/round-1.md"
  final: "confidential-compliance-token-research/research-sections/zama-confidential-rwa/final.md"
  index: "confidential-compliance-token-research/research-sections/_index.md"
scope: "Steps 1-7 per WHI-267: product narrative; technical architecture; standards boundaries among Zama, ERC-7984, OpenZeppelin Confidential Contracts, and ERC-3643/T-REX; RWA transfer lifecycle; Mantle lightweight integration; risk assessment; requirements-framework rubric score and candidate/reference/out initial verdict."
audience: "Mantle strategy, protocol, and RWA product readers evaluating whether Zama can serve as a confidential compliance token route under lightweight integration constraints."
expected_output: "A persisted deep-draft plan and eventual research section that covers all 7 steps, source URLs, architecture diagram input, RWA transfer lifecycle table, Mantle integration assessment table, and WHI-267 verification acceptance criteria."
revision_metadata:
  created_by: "Deep Research Agent"
  created_at: "2026-06-24T00:22:21Z"
  last_modified_by: "Deep Research Agent"
  last_modified_at: "2026-06-24T00:22:21Z"
---

# Research Outline: Zama Confidential RWA Tokenization 深度分析

## Items

### item-1: 产品叙事拆解与 claim 分级

调查 Zama 在 Confidential RWA Tokenization 页面、Zama Protocol 首页、T-REX Ledger partnership post 中声称解决的 institutional RWA 痛点：公开链金额/余额暴露、合规转账验证、发行方/监管方披露、机构资产互操作。必须把叙事拆成 four-way evidence class：已上线能力、官方文档能力、partnership claim、roadmap/vendor self-report，避免把官网营销材料直接当生产事实。输出应说明 Zama 对 RWA 的真实价值主张究竟是 confidential accounting、合规披露、T-REX Ledger 集成，还是更泛化的 confidential onchain finance。

- **Priority**: high
- **Dependencies**: none

### item-2: 技术架构拆解：fhEVM / Gateway / KMS / ACL / decrypt model

调查 Zama Confidential Blockchain Protocol / fhEVM 的执行路径：host contract 如何只处理 ciphertext handle / symbolic execution，coprocessor 如何执行 FHE，Gateway 如何同步 ACL 并协调 decrypt，KMS / threshold decryption 的信任和活性假设是什么。必须分别解释 ACL 授权、public decrypt、user/private decrypt、observer access 的权限边界，并标注哪些是 Zama 协议层能力、哪些是 OpenZeppelin 合约库封装出来的 token/RWA 能力。该 item 是后续 Mantle 集成和风险评估的技术基础。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 标准关系拆解：ERC-7984、OpenZeppelin Confidential Contracts、ERC-3643 / T-REX

调查 ERC-7984 的接口边界、OpenZeppelin Confidential Contracts 的 fhEVM-specific 实现与扩展、ERC-3643/T-REX 的身份和合规职责，并画清三者之间的依赖和非依赖关系。必须避免三类混淆：把 ERC-7984 的 interface standard 当成 Zama 后端实现；把 OpenZeppelin `ERC7984Rwa`/ObserverAccess/Restricted/Hooked 等扩展当成 ERC-7984 本体；把 ERC-3643 的 KYC/transfer compliance 当成 confidential accounting。输出应形成一张 responsibility matrix，说明谁负责 token interface、encrypted amount/balance、KYC claim、transfer policy、freeze/recovery、observer disclosure、redeem/unshield。

- **Priority**: high
- **Dependencies**: item-2

### item-4: RWA transfer lifecycle：发行到赎回的端到端流程

构造 Zama + ERC-3643/T-REX 或 Zama + ERC-7984/OZ RWA 路线下的 RWA token lifecycle：发行/KYC/claim、mint or wrap、confidential transfer、policy check、freeze/recovery、audit disclosure、redeem/unshield。每一步都要回答 actor、contract/module、encrypted/plaintext state、policy gate、decryption/disclosure event、failure semantics、audit evidence。输出应是一张 lifecycle table，并明确哪些步骤在公开材料中已有官方支持，哪些是合理架构推导或待验证 integration gap。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: Mantle 轻量集成评估

评估在现有 Mantle EVM L2 上接入 Zama 所需的最小组件：Solidity contracts、OpenZeppelin Confidential Contracts、Zama SDK/relayer/gateway、FHE-enabled network access、offchain service、operator/KMS/coprocessor 依赖、wallet/indexer/explorer changes。必须单独回答是否需要 Mantle 硬分叉、执行客户端改动、precompile、专用 L3/new chain、新资产桥或全节点隐私网络。输出应形成 Mantle integration assessment table，并按 requirements-framework 的 lightweight veto 规则标注 `no chain change`、`sidecar/operator dependency`、`protocol change required`、`unknown`.

- **Priority**: high
- **Dependencies**: item-2, item-4

### item-6: 风险评估与证据缺口

调查 Zama 路线的主要风险：FHE 性能和延迟、KMS/key/decryption governance、operator 去中心化、ACL 撤销性和历史披露、合规披露权限设计、Hook/Observer 权限持久化、vendor lock-in、标准成熟度、data availability / ciphertext availability、审计和事故响应。对 TVL/TVS、partnership、roadmap、性能数据、生产部署声称必须标注独立验证状态；厂商自报指标默认降权。输出应形成 risk register，包含 severity、evidence class、mitigation、Mantle decision impact。

- **Priority**: high
- **Dependencies**: item-2, item-5

### item-7: Rubric scoring and initial verdict

按 `confidential-compliance-token-research/research-sections/requirements-framework/final.md` 的 CCT rubric 给 Zama 打分：privacy_coverage、compliance_capability、selective_disclosure、deployment_lightweight、engineering_delta、maturity、mantle_fit。评分必须引用 item-1 到 item-6 的证据，不允许用 partnership 或 vendor roadmap 单独拉高 maturity / Mantle fit。输出初判为 `候选 / 参考 / 出局`，并说明是短期 PoC、主候选路线、还是仅作为长期协议能力参考。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| evidence_class | Classify each claim as deployed capability, official documented capability, partnership claim, roadmap claim, vendor self-report, third-party corroboration, or researcher inference. | all |
| source_url_or_path | Record exact URL/path plus access date, version, tag, or commit SHA. | all |
| actor_and_authority | Identify issuer, investor, transfer agent, observer, auditor, regulator, KMS/operator, gateway, contract, or bridge/redeem actor and what authority they hold. | item-2, item-3, item-4, item-6 |
| encrypted_vs_plaintext_state | Specify which fields are ciphertext handles, encrypted offchain state, plaintext onchain state, events, or offchain records. | item-2, item-4, item-5 |
| disclosure_vector | Capture authority, trigger, payload, scope, revocability, leakage, and audit log for every decrypt/observer path. | item-2, item-4, item-6 |
| standard_boundary | Separate interface standard, implementation library, protocol backend, compliance token standard, and partnership product layer. | item-3 |
| lifecycle_step | Map findings to issuance/KYC/mint/wrap/transfer/policy/freeze/recovery/audit/redeem steps. | item-4 |
| mantle_integration_delta | Track required contracts, SDKs, offchain services, operators, gateway/KMS access, client changes, bridge changes, and whether a hard fork/client change is needed. | item-5 |
| risk_and_mitigation | Capture risk, severity, evidence confidence, mitigation, and impact on Mantle decision. | item-6, item-7 |
| rubric_score | Store 0-5 score, rationale, evidence anchors, and candidate/reference/out verdict driver. | item-7 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | Zama Confidential RWA architecture input: user/wallet encryption, host contract, ERC-7984/OZ RWA modules, ACL, Gateway, coprocessor, KMS, observer/auditor/regulator decrypt paths, and T-REX/ERC-3643 compliance layer. Must label onchain vs offchain and plaintext vs ciphertext state. | mermaid | item-2, item-3, item-5 |
| diag-2 | flow | RWA transfer lifecycle table: issuance/KYC/claim, mint/wrap, confidential transfer, policy check, freeze/recovery, audit disclosure, redeem/unshield. Columns: actor, component, state mutation, decrypt/disclosure, evidence class, open gap. | ascii | item-4 |
| diag-3 | comparison | Responsibility matrix comparing Zama Protocol, ERC-7984, OpenZeppelin Confidential Contracts, ERC-3643/T-REX, and Mantle integration adapter. Rows should include token interface, encrypted accounting, identity, transfer policy, observer disclosure, freeze/recovery, bridge/redeem, operational trust. | ascii | item-3, item-5 |
| diag-4 | comparison | Mantle lightweight integration assessment table: component required, who operates it, chain/client change needed, deployment blocker, PoC path, production blocker, source evidence. | ascii | item-5 |
| diag-5 | decision | Rubric scorecard and verdict tree showing when Zama is `候选`, `参考`, or `出局`, including lightweight veto conditions and risk gates. | mermaid | item-7 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_product_pages | Zama official product pages, including `https://www.zama.org/solutions/confidential-rwa-tokenization` and `https://www.zama.org/`; access date must be 2026-06-24 or later in the draft. | 2 |
| src-2 | official_partnership_posts | Zama and/or T-REX official partnership sources, especially `https://www.zama.org/post/zama-becomes-the-confidentiality-layer-for-the-t-rex-ledger`; classify partnership metrics and roadmap claims separately from deployed technical guarantees. | 1 |
| src-3 | official_zama_docs | Zama Protocol / fhEVM docs covering architecture, ACL, Gateway, KMS/decryption, Solidity library, and OpenZeppelin examples. Required URLs include docs pages such as `https://docs.zama.org/protocol/solidity-guides/smart-contract/acl` and `https://docs.zama.org/protocol/protocol/overview/gateway`; note docs version or access date. | 4 |
| src-4 | standards_specs | Primary ERC/EIP texts for ERC-7984 and ERC-3643, plus any ERC-7945 context only if needed to avoid interface confusion. | 2 |
| src-5 | official_openzeppelin_docs_code | OpenZeppelin Confidential Contracts docs and GitHub source, including token API docs for ERC7984Rwa/ObserverAccess/Restricted/Hooked and repository commit or release/version. | 2 |
| src-6 | local_reuse_inputs | Commit-pinned local research inputs: requirements framework at `confidential-compliance-token-research/research-sections/requirements-framework/final.md` commit `9eb29a150f380f21add9b431b66fea2ee5d12881`; ERC-7984 at `evm-privacy-research/research-sections/erc7984-confidential-token/final.md` commit `fdbda370e9e9137890c5bd2deb7752e03d76d0bc`; Zama/Inco/Fhenix at `evm-privacy-research/research-sections/confidential-coprocessor/final.md` commit `0041e3a1598751a7d121fecc600ba3d6ad42ad05`. | 3 |
| src-7 | compliance_token_context | Commit-pinned compliance token inputs: ERC-3643/T-REX at `compliance-token-standards/research-sections/erc3643-trex-analysis/final.md` commit `a260e40f58b0d8d2e15ba7bd263ab67a3288b6bd`; Base B20 at `compliance-token-standards/research-sections/base-b20-analysis/final.md` commit `f42915ecd33c7f099d4ac0de89997390fc52d0b9`; use these only for compliance/lifecycle/Mantle baseline, not as Zama evidence. | 2 |
| src-8 | audit_or_security_material | Security/audit material for OpenZeppelin Confidential Contracts and Zama/fhEVM where available. If no current audit covers the exact version used, state the gap explicitly. | 1 |
| src-9 | independent_corroboration | Independent or third-party corroboration for deployment, ecosystem, partnership, performance, or explorer claims. Vendor metrics without independent corroboration must be labeled `未独立验证`. | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|

## Verification Acceptance Criteria

| ID | Criterion | Applies To |
|----|-----------|------------|
| vc-1 | Clearly separates deployed Zama capabilities, official documented capabilities, partnership claims, roadmap claims, and researcher inference. | item-1, item-7 |
| vc-2 | Explains fhEVM / Gateway / KMS / ACL / decrypt model without treating FHE as a black box. | item-2 |
| vc-3 | Separates ERC-7984 interface standard, OpenZeppelin Confidential Contracts implementation/extensions, Zama backend, and ERC-3643/T-REX compliance layer. | item-3 |
| vc-4 | Covers RWA lifecycle: compliance checks, encrypted balances, encrypted transfers, selective disclosure, freeze/recovery, and redeem/unshield. | item-4 |
| vc-5 | States whether Mantle integration requires hard fork, execution-client changes, KMS/operator operations, SDK/service dependencies, or only contracts/adapters. | item-5 |
| vc-6 | Labels vendor-reported performance, TVL/TVS, partnership, roadmap, and deployment metrics as independently verified or `未独立验证`. | item-1, item-6 |
| vc-7 | Every material conclusion has a URL/path and access date, version, or commit SHA. | all |
| vc-8 | Final scoring uses the requirements-framework rubric and produces `候选 / 参考 / 出局` with explicit caveats and decision gates. | item-7 |
