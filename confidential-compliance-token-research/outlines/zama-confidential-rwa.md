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

# 研究大纲（Research Outline）：Zama Confidential RWA Tokenization 深度分析

## 研究条目（Items）

### item-1: 产品叙事拆解与 claim 分级

调查 Zama 在 Confidential RWA Tokenization 页面、Zama Protocol 首页、T-REX Ledger partnership post 中声称解决的机构 RWA 痛点：公开链金额/余额暴露、合规转账验证、发行方/监管方披露、机构资产互操作。必须把叙事拆成四类证据等级（four-way evidence class）：已上线能力、官方文档能力、partnership claim、roadmap/vendor self-report，避免把官网营销材料直接当生产事实。输出应说明 Zama 对 RWA 的真实价值主张究竟是机密记账（confidential accounting）、合规披露、T-REX Ledger 集成，还是更泛化的链上机密金融（confidential onchain finance）。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: none

### item-2: 技术架构拆解：fhEVM / Gateway / KMS / ACL / decrypt model

调查 Zama Confidential Blockchain Protocol / fhEVM 的执行路径：host contract 如何只处理密文句柄（ciphertext handle）/ 符号化执行（symbolic execution），coprocessor 如何执行 FHE，Gateway 如何同步 ACL 并协调解密（decrypt），KMS / 门限解密（threshold decryption）的信任和活性假设是什么。必须分别解释 ACL 授权、公开解密（public decrypt）、用户/私有解密（user/private decrypt）、观察者访问（observer access）的权限边界，并标注哪些是 Zama 协议层能力、哪些是 OpenZeppelin 合约库封装出来的 token/RWA 能力。该条目是后续 Mantle 集成和风险评估的技术基础。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1

### item-3: 标准关系拆解：ERC-7984、OpenZeppelin Confidential Contracts、ERC-3643 / T-REX

调查 ERC-7984 的接口边界、OpenZeppelin Confidential Contracts 的 fhEVM 专用（fhEVM-specific）实现与扩展、ERC-3643/T-REX 的身份和合规职责，并画清三者之间的依赖和非依赖关系。必须避免三类混淆：把 ERC-7984 的接口标准（interface standard）当成 Zama 后端实现；把 OpenZeppelin `ERC7984Rwa`/ObserverAccess/Restricted/Hooked 等扩展当成 ERC-7984 本体；把 ERC-3643 的 KYC/转账合规（transfer compliance）当成机密记账（confidential accounting）。输出应形成一张职责矩阵（responsibility matrix），说明谁负责 token interface、加密金额/加密余额（encrypted amount/balance）、KYC claim、转账策略（transfer policy）、冻结/恢复（freeze/recovery）、观察者披露（observer disclosure）、赎回/解密提取（redeem/unshield）。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-2

### item-4: RWA transfer lifecycle：发行到赎回的端到端流程

构造 Zama + ERC-3643/T-REX 或 Zama + ERC-7984/OZ RWA 路线下的 RWA token lifecycle：发行/KYC/claim、铸造或封装（mint or wrap）、机密转账（confidential transfer）、策略检查（policy check）、冻结/恢复（freeze/recovery）、审计披露（audit disclosure）、赎回/解密提取（redeem/unshield）。每一步都要回答参与方（actor）、合约/模块（contract/module）、加密/明文状态（encrypted/plaintext state）、策略门控（policy gate）、解密/披露事件（decryption/disclosure event）、失败语义（failure semantics）、审计证据（audit evidence）。输出应是一张生命周期表（lifecycle table），并明确哪些步骤在公开材料中已有官方支持，哪些是合理架构推导或待验证的集成缺口（integration gap）。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-2, item-3

### item-5: Mantle 轻量集成评估

评估在现有 Mantle EVM L2 上接入 Zama 所需的最小组件：Solidity contracts、OpenZeppelin Confidential Contracts、Zama SDK/relayer/gateway、支持 FHE 的网络访问（FHE-enabled network access）、链下服务（offchain service）、operator/KMS/coprocessor 依赖、钱包/索引器/浏览器改动（wallet/indexer/explorer changes）。必须单独回答是否需要 Mantle 硬分叉、执行客户端改动、precompile、专用 L3/新链、新资产桥或全节点隐私网络。输出应形成 Mantle 集成评估表（Mantle integration assessment table），并按 requirements-framework 的轻量否决规则（lightweight veto）标注 `no chain change`、`sidecar/operator dependency`、`protocol change required`、`unknown`。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-2, item-4

### item-6: 风险评估与证据缺口

调查 Zama 路线的主要风险：FHE 性能和延迟、KMS/key/decryption 治理、operator 去中心化、ACL 撤销性和历史披露、合规披露权限设计、Hook/Observer 权限持久化、厂商锁定（vendor lock-in）、标准成熟度、数据可用性 / 密文可用性（data availability / ciphertext availability）、审计和事故响应。对 TVL/TVS、partnership、roadmap、性能数据、生产部署声称必须标注独立验证状态；厂商自报指标默认降权。输出应形成风险登记表（risk register），包含严重度（severity）、证据等级（evidence class）、缓解措施（mitigation）、对 Mantle 决策的影响（Mantle decision impact）。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-2, item-5

### item-7: 评分卡打分与初步判定（Rubric scoring and initial verdict）

按 `confidential-compliance-token-research/research-sections/requirements-framework/final.md` 的 CCT rubric 给 Zama 打分：privacy_coverage、compliance_capability、selective_disclosure、deployment_lightweight、engineering_delta、maturity、mantle_fit。评分必须引用 item-1 到 item-6 的证据，不允许用 partnership 或 vendor roadmap 单独拉高 maturity / Mantle fit。输出初判为 `候选 / 参考 / 出局`，并说明是短期 PoC、主候选路线、还是仅作为长期协议能力参考。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1, item-2, item-3, item-4, item-5, item-6

## 字段（Fields）

| 字段 | 描述 | 适用条目 |
|-------|-------------|------------|
| evidence_class | 把每条主张归类为：已部署能力、官方文档化能力、partnership claim、roadmap claim、厂商自报、第三方佐证或研究者推断。 | all |
| source_url_or_path | 记录确切的 URL/路径以及访问日期、版本、tag 或 commit SHA。 | all |
| actor_and_authority | 识别发行方、投资者、转账代理、观察者、审计方、监管方、KMS/operator、gateway、合约或桥接/赎回参与方，以及他们各自持有的权限。 | item-2, item-3, item-4, item-6 |
| encrypted_vs_plaintext_state | 指明哪些字段是密文句柄、加密的链下状态、明文的链上状态、事件或链下记录。 | item-2, item-4, item-5 |
| disclosure_vector | 针对每条解密/观察者路径，记录权限方、触发条件、负载、范围、可撤销性、泄露面与审计日志。 | item-2, item-4, item-6 |
| standard_boundary | 区分接口标准、实现库、协议后端、合规 token 标准与 partnership 产品层。 | item-3 |
| lifecycle_step | 把发现映射到发行/KYC/铸造/封装/转账/策略/冻结/恢复/审计/赎回各步骤。 | item-4 |
| mantle_integration_delta | 跟踪所需的合约、SDK、链下服务、operator、gateway/KMS 访问、客户端改动、桥接改动，以及是否需要硬分叉/客户端改动。 | item-5 |
| risk_and_mitigation | 记录风险、严重度、证据置信度、缓解措施以及对 Mantle 决策的影响。 | item-6, item-7 |
| rubric_score | 存储 0-5 分、打分依据、证据锚点，以及驱动候选/参考/出局判定的因素。 | item-7 |

## 图示预期（Diagram Expectations）

| ID | 类型 | 描述 | 格式 | 适用条目 |
|----|------|-------------|--------|------------|
| diag-1 | architecture | Zama Confidential RWA 架构输入：用户/钱包加密、host contract、ERC-7984/OZ RWA 模块、ACL、Gateway、coprocessor、KMS、观察者/审计方/监管方解密路径，以及 T-REX/ERC-3643 合规层。必须标注链上 vs 链下、明文 vs 密文状态。 | mermaid | item-2, item-3, item-5 |
| diag-2 | flow | RWA transfer lifecycle 表：发行/KYC/claim、铸造/封装、机密转账、策略检查、冻结/恢复、审计披露、赎回/解密提取。列：参与方、组件、状态变更、解密/披露、证据等级、未决缺口。 | ascii | item-4 |
| diag-3 | comparison | 职责矩阵，对比 Zama Protocol、ERC-7984、OpenZeppelin Confidential Contracts、ERC-3643/T-REX 以及 Mantle 集成适配器。行应包括 token interface、加密记账、身份、转账策略、观察者披露、冻结/恢复、桥接/赎回、运营信任。 | ascii | item-3, item-5 |
| diag-4 | comparison | Mantle 轻量集成评估表：所需组件、由谁运营、是否需要链/客户端改动、部署阻碍、PoC 路径、生产阻碍、来源证据。 | ascii | item-5 |
| diag-5 | decision | 评分卡与判定树，展示 Zama 何时为 `候选`、`参考` 或 `出局`，包含轻量否决条件与风险门控。 | mermaid | item-7 |

## 来源要求（Source Requirements）

| ID | 类型 | 描述 | 最少数量 |
|----|------|-------------|-----------|
| src-1 | official_product_pages | Zama 官方产品页面，包括 `https://www.zama.org/solutions/confidential-rwa-tokenization` 与 `https://www.zama.org/`；草稿中访问日期须为 2026-06-24 或之后。 | 2 |
| src-2 | official_partnership_posts | Zama 和/或 T-REX 官方合作来源，尤其是 `https://www.zama.org/post/zama-becomes-the-confidentiality-layer-for-the-t-rex-ledger`；须把 partnership 指标和 roadmap 主张与已部署的技术保证分开归类。 | 1 |
| src-3 | official_zama_docs | Zama Protocol / fhEVM 文档，涵盖架构、ACL、Gateway、KMS/解密、Solidity 库与 OpenZeppelin 示例。所需 URL 包括文档页面如 `https://docs.zama.org/protocol/solidity-guides/smart-contract/acl` 与 `https://docs.zama.org/protocol/protocol/overview/gateway`；须注明文档版本或访问日期。 | 4 |
| src-4 | standards_specs | ERC-7984 与 ERC-3643 的一手 ERC/EIP 文本，外加仅在为避免接口混淆时所需的任何 ERC-7945 上下文。 | 2 |
| src-5 | official_openzeppelin_docs_code | OpenZeppelin Confidential Contracts 文档与 GitHub 源码，包括 ERC7984Rwa/ObserverAccess/Restricted/Hooked 的 token API 文档以及仓库 commit 或 release/version。 | 2 |
| src-6 | local_reuse_inputs | 锁定 commit 的本地研究输入：requirements framework 位于 `confidential-compliance-token-research/research-sections/requirements-framework/final.md` commit `9eb29a150f380f21add9b431b66fea2ee5d12881`；ERC-7984 位于 `evm-privacy-research/research-sections/erc7984-confidential-token/final.md` commit `fdbda370e9e9137890c5bd2deb7752e03d76d0bc`；Zama/Inco/Fhenix 位于 `evm-privacy-research/research-sections/confidential-coprocessor/final.md` commit `0041e3a1598751a7d121fecc600ba3d6ad42ad05`。 | 3 |
| src-7 | compliance_token_context | 锁定 commit 的合规 token 输入：ERC-3643/T-REX 位于 `compliance-token-standards/research-sections/erc3643-trex-analysis/final.md` commit `a260e40f58b0d8d2e15ba7bd263ab67a3288b6bd`；Base B20 位于 `compliance-token-standards/research-sections/base-b20-analysis/final.md` commit `f42915ecd33c7f099d4ac0de89997390fc52d0b9`；这些仅用于合规/生命周期/Mantle 基线，不作为 Zama 证据。 | 2 |
| src-8 | audit_or_security_material | 在可获取时，提供 OpenZeppelin Confidential Contracts 与 Zama/fhEVM 的安全/审计材料。若没有现成审计覆盖所用的确切版本，须明确指出该缺口。 | 1 |
| src-9 | independent_corroboration | 针对部署、生态、partnership、性能或浏览器声称的独立或第三方佐证。缺乏独立佐证的厂商指标须标注 `未独立验证`。 | 2 |

## 修订日志（Patch Log）

| 轮次 | 操作 | 目标 | 原因 | 来源 |
|-------|--------|--------|--------|--------|

## 验收标准（Verification Acceptance Criteria）

| ID | 标准 | 适用条目 |
|----|-----------|------------|
| vc-1 | 清晰区分已部署的 Zama 能力、官方文档化能力、partnership claims、roadmap claims 与研究者推断。 | item-1, item-7 |
| vc-2 | 解释 fhEVM / Gateway / KMS / ACL / decrypt model，且不把 FHE 当作黑盒。 | item-2 |
| vc-3 | 区分 ERC-7984 接口标准、OpenZeppelin Confidential Contracts 实现/扩展、Zama 后端与 ERC-3643/T-REX 合规层。 | item-3 |
| vc-4 | 覆盖 RWA 生命周期：合规检查、加密余额、加密转账、选择性披露、冻结/恢复以及赎回/解密提取。 | item-4 |
| vc-5 | 说明 Mantle 集成是否需要硬分叉、执行客户端改动、KMS/operator 运营、SDK/服务依赖，还是仅需合约/适配器。 | item-5 |
| vc-6 | 把厂商自报的性能、TVL/TVS、partnership、roadmap 与部署指标标注为已独立验证或 `未独立验证`。 | item-1, item-6 |
| vc-7 | 每条实质性结论都附带 URL/路径以及访问日期、版本或 commit SHA。 | all |
| vc-8 | 最终评分使用 requirements-framework 的 rubric，并产出 `候选 / 参考 / 出局`，附明确注意事项与决策门控。 | item-7 |
