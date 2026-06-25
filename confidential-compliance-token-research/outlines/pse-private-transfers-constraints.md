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

# 研究大纲（Research Outline）

本节研究的核心问题是：PSE private transfers 的用户研究与 dashboard 不是直接给 Mantle 选择某个隐私协议，而是暴露 private transfer 产品进入真实用户、钱包、合规、生态和 PMF 场景时会失败的地方。后续 draft 必须把这些失败点转换成 Mantle confidential compliance token 的可执行产品约束，而不是停留在协议功能对照。

来源完整性说明（Source integrity note）：PSE 文章的页面元数据可确认标题、作者、发布时间和“38 interviews”摘要，但 outline 阶段未能通过页面的 GitHub edit link 获取 Markdown 源文。后续 draft 在引用 PSE 用户研究的具体 blocker、样本表达、数量或访谈结论前，必须先通过 rendered page、RSS、PSE repo 或其他 primary route 复核正文。

## 研究项（Items）

### 1. PSE private transfers 来源提取与 blocker 分类法（PSE private transfers source extraction and blocker taxonomy）

将 PSE 用户研究文章与 Private Transfers Analysis dashboard 作为产品发现（product-discovery）的锚点进行研究。把 blocker 分类提取为四个桶：技术、产品/UX、合规、生态/PMF。保持文章与 dashboard 各自独立：文章是用户研究证据；dashboard 是一个结构化的协议评估模型，覆盖隐私、成本/性能、UX、去中心化/安全、合规、可验证性、状态、可组合性等维度。

所需产出：

- 一份精炼的 blocker 分类法，每个类别配一句话定义。
- 每个 blocker 的证据说明：来源、论断、受影响的用户群体，以及证据是来自文章访谈、dashboard schema、evaluation JSON 还是本地既有研究。
- 对任何无法从正文核实的 PSE 文章细节，给出「不要过度声称（do not overclaim）」的提示。

### 2. private-transfer blocker 到 Mantle confidential RWA 约束的映射（Private-transfer blocker to Mantle confidential RWA constraint mapping）

将 private transfer 的痛点映射到 confidential RWA 与机构 token 设计。分析必须明确把 blocker 拆分为三种结果：仍然原样成立；成立但因 confidentiality 偏机构/会计中心而发生变化；或因 RWA 发行方已经控制 onboarding 与披露而变得不那么核心。

所需产出：

- 一张从 PSE/dashboard blocker 到 Mantle RWA 设计约束的映射表。
- 一段简短叙述，说明哪些 private-transfer 痛点会被机构使用放大：可审计性、issuer control、onboarding、钱包操作以及可解释的披露。
- 一段简短叙述，说明哪些散户 private-transfer 假设对 confidential RWA 更弱：把纯匿名作为终极目标、把 anonymous-set 冷启动作为唯一隐私指标，以及把无需许可的自托管作为默认集成路径。

### 3. account-based confidential token 与 note-based shielded pool 的产品权衡（Account-based confidential token versus note-based shielded pool product tradeoff）

比较 account-based confidential token（尤其是 ERC-7984 风格的加密余额接口和 FHE 支撑的实现）与 note-based shielded pool（如 Railgun、Privacy Pools、EIP-8182 风格设计）。该比较必须以产品为先：应评估钱包、issuer、auditor 和 DeFi 集成方会体验到的模型，而不仅是密码学保证。

所需产出：

- 一张产品对比表，覆盖可组合性、匿名性、余额模型、钱包 UX、证明/解密流程、披露模型、issuer controls 以及 Mantle 契合度。
- 一个区分「最佳隐私原语（best privacy primitive）」与「最佳 Mantle confidential compliance token 基底（best Mantle confidential compliance token substrate）」的结论。
- 一份会改变上述结论的假设清单，例如原生 account abstraction 的采用、协议级 private transfer 支持、成熟的移动端 prover，或标准化的 selective disclosure。

### 4. 钱包、prover、加密 SDK 与 gas sponsor 约束（Wallet, prover, encryption SDK, and gas sponsor constraints）

把产品 blocker 转化为具体的钱包与基础设施需求。覆盖钱包集成、远程 prover/证明委托、加密 SDK 的人体工学、本地/移动端证明可行性、解密与 handle 展示、private-state 扫描、gas sponsorship、relayer/paymaster 路由、恢复和 key management。

所需产出：

- 一条「首位机构持有者接收、查看、转账并披露一枚 confidential token」的用户旅程（user journey）。
- 一份钱包/prover 约束清单，分为 MVP、应有项（should-have）和后续高风险项（risky-later）三类。
- 一项 gas sponsor/paymaster 需求，避免要求用户必须先持有公开 gas 资产，以免以某种方式关联身份、转账意图或投资组合活动。

### 5. selective disclosure、auditor key、issuer control 与机构合规运营（Selective disclosure, auditor key, issuer control, and institutional compliance operations）

把披露与合规作为一等产品界面来分析，而不是法律附录。该 draft 必须覆盖 viewing key、auditor key、issuer key、监管方或 fund-admin 访问、持有者发起的披露、发行方发起的控制、访问吊销、审计日志、披露范围，以及 onboarding 和调查的运营工作流。

所需产出：

- 一张披露矩阵（disclosure matrix），列出参与方、各自能看到什么、由谁授予访问、时长、吊销语义以及审计轨迹。
- 一节关于永久、过宽或不可见 viewing access 的警示。
- 一项关于可解释披露 UX 的产品需求：用户和机构必须理解哪些加密余额、转账或持仓对哪些方可见。

### 6. DeFi 可组合性与机构 onboarding 边界（DeFi composability and institutional onboarding boundaries）

界定 confidential RWA 在哪里可以与 Mantle DeFi 组合、在哪里不应宣称无缝可组合。处理 AMM/借贷中的加密余额、基于 adapter 的 DeFi、oracle/indexer 限制、托管与 fund-administrator 工作流、桥接/赎回边界、KYC/KYB 准入、转账限制以及二级市场控制。

所需产出：

- 一张 DeFi 用例边界图（boundary map）：安全 MVP、借助 adapter 可行、仅供研究（research-only）以及反模式。
- 一条覆盖机构、issuer、钱包/托管方、auditor 与 DeFi 场所的 onboarding 流程。
- 一份冷启动分析，针对流动性、对手方、合规参与者以及隐私集，而不仅是匿名用户。

### 7. Mantle confidential compliance token 反模式清单（Mantle confidential compliance token anti-pattern checklist）

产出一份可在产品/设计评审时使用的清单。该清单至少应包含所提供的反模式，并补充任何从来源中发现的反模式。

最少反模式：

- 无披露通道（No disclosure channel）：交付了隐私却没有为持有者、issuer 或 auditor 提供可见性路径。
- 仅以匿名为框架（Anonymity-only framing）：设计只优化 unlinkability，却忽略了 issuer controls、资格、freeze/recover、赎回以及受监管审计。
- 移动端证明不可用（Mobile proving unusable）：普通钱包无法在可接受的延迟、电量和可靠性预算内生成或委托证明。
- 匿名集依赖无法启动（Anonymous-set dependency cannot start）：产品在能提供机构价值之前，先依赖一个庞大且活跃的 shielded pool。
- 缺失 gas sponsor（Gas sponsor missing）：用户在能使用 confidential transfer 之前，必须先获得会关联身份或意图的公开 gas 资金。
- viewing key 永久且过宽（Viewing keys are permanent and overbroad）：披露无法被限定范围、吊销、记录或解释。
- 远程 prover/KMS 在运营上不透明（Remote prover/KMS is operationally opaque）：敏感材料在缺乏信任、托管或失败边界的情况下进入基础设施。
- 在没有 adapter 约束的情况下断言 DeFi 可组合性（DeFi composability is asserted without adapter constraints）：假定加密余额能在普通 AMM/借贷中正常工作，却不解释价格、清算、oracle 和 indexer 流程。

所需产出：

- 反模式清单表，含反模式、症状、为何危险、检测问题、缓解措施和严重程度。
- 一节简短内容，把每个反模式映射回至少一个 blocker 或本地研究输入。

### 8. requirements-framework rubric 的产品与 UX 评分附录（Product and UX scoring addendum for requirements-framework rubric）

为 WHI-266 requirements framework 扩展产品/UX 评分指引。这不应替换现有的 0-5 轴；它应作为评审者在评判 confidential compliance token 候选时可应用的补充。

所需产出：

- 产品/UX 评分表，含 0-1、2-3 和 4-5 锚点。
- 与现有轴的明确映射：`privacy_coverage`、`compliance_capability`、`selective_disclosure`、`deployment_lightweight`、`engineering_delta`、`maturity` 和 `mantle_fit`。
- 关于产品/UX 证据应在多大程度上影响临界分数的建议，尤其是当密码学很强但 onboarding、钱包、披露或 gas 流程偏弱时。

### 必备核心表格（Required core tables）

final 章节必须包含以下表格：

| 表格 | 必备列 |
| --- | --- |
| private transfers blocker -> Mantle RWA 设计约束 | PSE/dashboard 证据；blocker_category；散户 private-transfer 痛点；RWA 沿用；机构变化；Mantle 需求；反模式风险；rubric 影响 |
| account-based confidential token 对比 note-based shielded pool | 模型；隐私覆盖；余额模型；可组合性；匿名性/冷启动；钱包 UX；证明/解密；披露/合规；issuer controls；Mantle 契合度 |
| Mantle confidential compliance token 反模式清单 | 反模式；症状；为何危险；检测问题；缓解措施；严重程度 |
| 产品/UX 评分附录 | 维度；评分 0-1；评分 2-3；评分 4-5；所需证据；关联的 WHI-266 轴 |

## 字段（Fields）

| 字段 | 含义 | 预期用途 |
| --- | --- | --- |
| `source_anchor` | 某论断的主要证据来源 | 防止把 PSE 访谈、dashboard schema、dashboard JSON 和既有研究当作同一种证据类型混用 |
| `evidence_weight` | high / medium / low | high 用于带明确论断的一手来源；medium 用于 dashboard WIP 字段或本地综合；low 用于推断 |
| `blocker_category` | technical / product_ux / compliance / ecosystem_pmf | 在映射到 Mantle 之前对 private-transfer blocker 做归一化 |
| `user_segment` | retail holder / institution / issuer / auditor / wallet / DeFi venue / regulator / developer | 表明在解决谁的 blocker |
| `private_transfer_blocker` | 原始的 private-transfer 痛点 | 让映射始终扎根于 PSE/dashboard 的问题空间 |
| `rwa_carryover` | unchanged / changed / weaker / not_applicable | 捕捉该 blocker 在转译为 confidential RWA 后是否仍然成立 |
| `institutional_delta` | RWA confidentiality 如何改变该 blocker | 强制 draft 解释 issuer、auditor、托管和 onboarding 的差异 |
| `product_constraint` | 该 blocker 所隐含的具体 Mantle 需求 | 把研究转化为设计需求 |
| `ux_failure_mode` | 若被忽略，真实用户/运营者会体验到什么 | 支撑产品/UX 评分与反模式检测 |
| `compliance_disclosure_vector` | holder-initiated / issuer-initiated / auditor-access / regulator-access / none | 对 selective disclosure 与可审计性论断做归一化 |
| `state_model` | account_balance / note_utxo / pool / hybrid / other | 支撑 account-vs-note 比较 |
| `proof_decryption_experience` | local_proof / remote_proof / FHE_handle / wallet_decrypt / scanning / none | 捕捉钱包与 prover 界面 |
| `wallet_integration_surface` | extension / mobile / custodian / smart account / SDK / dapp adapter | 表明集成风险出现在何处 |
| `gas_sponsor_requirement` | none / optional / required / unresolved | 追踪公开 gas 资金是否泄露使用情况或阻碍采用 |
| `defi_composability_boundary` | native / adapter / constrained / research_only / unsafe_claim | 防止含糊的 DeFi 兼容性论断 |
| `rubric_score_impact` | 受影响的 WHI-266 轴及预期方向 | 把发现关联到 requirements-framework 评分 |
| `anti_pattern_flag` | 命中的清单项（若有） | 支撑最终反模式清单与评审可追溯性 |

## 图示预期（Diagram Expectations）

| 图示 | 目的 | 必备内容 |
| --- | --- | --- |
| blocker 到需求的流程图 | 展示来源观察如何变成 Mantle 需求 | PSE 文章/dashboard 证据 -> blocker 类别 -> RWA 转译 -> 产品约束 -> 反模式/rubric 影响 |
| 模型权衡矩阵 | 比较 account-based confidential token 与 note-based shielded pool 模型 | 行为 account balance、note UTXO、shielded pool、hybrid；列为可组合性、匿名性、披露、issuer control、钱包/prover 负担 |
| 参与方/数据可见性图 | 让披露与审计关系可被检视 | 持有者、issuer、auditor、监管方、钱包/托管方、prover、DeFi 场所；加密数据、解密数据、viewing 授权、日志 |
| 机构 onboarding 旅程 | 识别 UX 与运营 blocker | KYB/KYC、钱包设置、key 设置、接收 token、查看余额、转账、披露、赎回、事件/冻结 |
| 需求热力图 | 把 blocker 与 Mantle 设计优先级关联 | blocker 类别对比钱包、prover、披露、issuer controls、gas sponsor、DeFi、onboarding、评分轴 |

## 来源要求（Source Requirements）

draft 的最少来源集：

| 来源组 | 最低要求 | 备注 |
| --- | --- | --- |
| PSE 用户研究文章 | 使用文章页面，并在引用具体访谈发现之前先恢复正文论断 | 必须包含标题、作者、日期、访问日期，若正文获取仍不完整则附来源注意事项 |
| PSE Private Transfers Analysis dashboard | 使用公开 dashboard 与 `privacy-ethereum/private-transfers-benchmarks` 仓库 | 将 dashboard 视为 WIP；保留 `needsResearchReview` 注意事项 |
| Dashboard schema | 引用 `project-evaluations/src/data/schema.ts` 与 `project-evaluations/src/data/evaluation-schema.ts` | 用于论证 blocker 维度与产品字段 |
| Dashboard 项目评估 | 至少使用 Railgun 和 Privacy Pools 的 JSON；如需可加入 ERC-7984/Zama 或其他加密 token 条目 | 比较真实的 evaluation 字段，而不仅是泛泛的协议描述 |
| WHI-266 requirements framework | 在 commit `9eb29a150f380f21add9b431b66fea2ee5d12881` 引用 `confidential-compliance-token-research/research-sections/requirements-framework/final.md` | 产品/UX 附录必须映射回现有轴 |
| ERC-7984 confidential token 研究 | 在 commit `fdbda370e9e9137890c5bd2deb7752e03d76d0bc` 引用 `evm-privacy-research/research-sections/erc7984-confidential-token/final.md` | account-based confidential token 分析所需 |
| Shielded-pool 研究 | 在 commit `788453b4097f37003337b943bcf6d7f8f68b02ba` 引用 `evm-privacy-research/research-sections/zk-shielded-pool/final.md` | Railgun、Privacy Pools、viewing key、POI/ASP 以及 pool UX 所需 |
| Privacy EIP 背景 | 在 commit `957773b13b2f5a66354ccda4b7d0c79a7236b222` 引用 `evm-privacy-research/research-sections/privacy-eips-survey/final.md` | EIP-8182 以及 account-abstraction/gas 相关背景所需 |
| 一手标准/文档 | 在论断依赖标准行为时纳入现行 ERC/EIP/spec 文档 | 优先采用标准、官方文档、源码仓库、审计或论文/规范正文，而非二手摘要 |
| 合规/机构背景 | 若引用受监管 token 控制，使用一手或近一手来源 | 法律论断保持克制；聚焦产品需求与运营约束 |

完整性要求：

- 区分一手证据、本地既有研究与推断出的产品含义。
- 不要在未核对底层来源的情况下照搬生成式摘要中的论断。
- 标记任何处于待定状态或被明确标注需研究复核的 dashboard 数据。
- 避免把 private-transfer 散户 PMF 等同于机构 confidential RWA PMF。
- 谨慎引用，仅在精确措辞重要时才引用。

## 修订日志（Patch Log）

| 日期 | 轮次 | 变更 | 作者 |
| --- | --- | --- | --- |
| 2026-06-24 | 1 | 基于 Orchestrator 派发、PSE/dashboard 来源侦察以及本地 WHI-266/WHI-260/WHI-257/ERC-7984 背景，创建初始候选 outline。 | Deep Research Agent |
