---
topic: "7702 之后的 native AA 方案全景与 Base 选型动因"
project_slug: "base-eip8130-native-aa"
topic_slug: "post7702-native-aa-landscape"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "base-eip8130-native-aa/outlines/post7702-native-aa-landscape.md"
  draft: "base-eip8130-native-aa/research-sections/post7702-native-aa-landscape/drafts/round-{n}.md"
  final: "base-eip8130-native-aa/research-sections/post7702-native-aa-landscape/final.md"
  index: "base-eip8130-native-aa/research-sections/_index.md"

scope: "梳理 EIP-7702 之后的 native/in-protocol AA 候选方案（至少 RIP-7560、EIP-8141/EIP-7701、EIP-3074 历史对照；按方法论补充 EIP-2938、EIP-5806、EIP-5003、EIP-7377、EIP-7851 等历史/相邻方案），逐一拆解其原理与定位，并与 EIP-8130 的 account configuration / authenticator 路线对比；以 Base/OP 公开 PR、forum、design-docs、ACD/硬分叉 meta 与既有本地研究为信号源，还原 Base 选择 EIP-8130 而非其它方案的动因，严格区分明确陈述与合理推断；为每个被纳入候选的 native AA 方案按 WHI-275 rubric 预填 D1~D13 行。"
audience: "Mantle dev teams、协议工程师、钱包/AA infra 工程师、Research Review Agent、后续 WHI-281/WHI-282 决策章节。读者熟悉 ERC-4337/EIP-7702/EIP-8130 基础，但需要一份可审查的 post-7702 native AA 版图与 Base 选型信号分析。"
expected_output: "候选/排除清单 + 检索方法论 + 各候选方案原理与定位表 + 各候选方案 D1~D13 预填行（不可判定维度有标注+原因） + Base 选型动因（事实/推断标注，每条附 URL/commit SHA） + 8130 vs 替代方案初步差异点清单。"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-27"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-27"

multica_issue_id: "c1205b12-9d26-4200-a547-9e034a901dc9"
report_issue_id: "fc840c0d-ac87-41c8-b1ae-6d1318b8eaba"
branch_name: "research/base-eip8130-native-aa/post7702-native-aa-landscape"
base_commit: "6bf3e8a39d9a6c069ed23746306108c42714cac2"
language: "zh-CN"
research_depth: "standard"
search_cutoff_date: "2026-06-27"
primary_local_dependencies:
  - "base-eip8130-native-aa/research-sections/native-aa-framework/final.md"
  - "base-eip8130-native-aa/research-sections/eip8130-deep-dive/final.md"
  - "base-eip8130-native-aa/research-sections/erc4337-mechanism-limits/final.md"
  - "base-eip8130-native-aa/research-sections/eip7702-mechanism-limits/final.md"
---

# Research Outline: 7702 之后的 native AA 方案全景与 Base 选型动因

## Search Cutoff And Evidence Contract

本 outline 的检索截止日期为 **2026-06-27**。后续 deep draft 必须在文首保留该日期，并为每个外部规范、PR、forum、ACD 记录写明实际访问日期；如果 draft 执行日晚于 2026-06-27，状态敏感项必须重新核验。

本 issue 的结论边界比一般技术综述更严格：如果没有找到 Base/OP 对“为什么选择 EIP-8130 而非 RIP-7560/EIP-8141/EIP-7701 等”的明确公开表述，结论必须写成：

> 未发现明确选择理由；以下为基于代码/PR节奏/方案差异的推断。

任何 Base/OP 选型动因都要标注为 `explicit-public-statement`、`code-pr-signal`、`design-doc-signal`、`roadmap-signal`、`inference` 或 `unknown`。不得把推断包装成 Base 官方理由。

## Research Questions

1. 截至 2026-06-27，EIP-7702 之后仍值得纳入 Mantle native AA 讨论的 in-protocol / protocol-adjacent AA 方案有哪些？哪些应进入候选清单，哪些只应进入排除/历史/相邻清单？
2. RIP-7560、EIP-8141、EIP-7701、EIP-2938、EIP-3074、EIP-5003、EIP-7377、EIP-7851 等方案分别试图解决什么问题？它们在交易类型、验证模型、mempool admission、payer/paymaster、nonce/replay、EOA migration、签名灵活性和安全面上如何定位？
3. EIP-8130 的 account configuration / actor / authenticator / payer / phased calls 路线，与 RIP-7560 的 rollup-native 4337 enshrinement、EIP-8141 的 frame transaction、EIP-7701 的 EOF-native AA、EIP-3074/7702 类 EOA delegation 路线的根本差异是什么？
4. Base/OP 公开材料中，是否存在直接解释“选择 8130 而不是其它 native AA 方案”的文本？如果没有，哪些 PR 时间线、design-doc、spec 讨论、Base Stack/OP Stack 工程节奏可以作为合理推断的依据？
5. 按 WHI-275 D1~D13 rubric，哪些候选方案能直接预填，哪些维度必须标注不可判定？不可判定是因为规范缺口、实现缺口、Base/OP 未表态、Mantle codebase 未审计，还是生态数据不足？
6. 面向 Mantle 决策，8130 相比替代方案的初步差异点有哪些：工程可落地性、mempool DoS 边界、验证灵活性、钱包/SDK 生态、OP Stack 适配、短期产品价值、长期协议路线风险？

## Guardrails

> **G1 - 候选与排除必须分开**：
> `candidate` 只给完整或接近完整的 protocol-native AA 路线，例如 RIP-7560、EIP-8141、EIP-7701、EIP-2938；`historical` 给已退出但影响路线选择的方案，例如 EIP-3074、EIP-5003；`adjacent` 给 EOA migration / delegation lifecycle 方案，例如 EIP-7377、EIP-7851。排除项仍要说明为什么不做完整 D1~D13。

> **G2 - 状态要逐项核验**：
> Draft / Final / Withdrawn / Stagnant / RIP Draft / CFI 都是时间敏感状态。EIP-8141 只能写 Draft + EIP-8081 Hegota/Hegotá Considered for Inclusion，不能写成 scheduled 或 accepted。EIP-7701、EIP-3074、EIP-5003 的 withdrawn/superseded 状态必须用官方 EIP 页面核验。

> **G3 - Base 选型理由必须证据分级**：
> Base 已实现大量 8130 PR 是事实；“Base 因为 X 放弃 Y”不是事实，除非有 Base/OP 公开文本直接这么写。设计动机表必须拆成 `明确陈述` 和 `合理推断` 两栏。

> **G4 - 不重复 WHI-276/277/278 的全文**：
> EIP-8130、ERC-4337、EIP-7702 已有 final section。本文只复用其结论并引用 source anchors，重点补上 post-7702 alternatives 和 Base 选型动因。

> **G5 - D1~D13 每格都要有证据或 unknown reason**：
> 每个候选方案每个维度必须填 `value / evidence / confidence / caveat`。没有证据时写 `不可判定`，并说明原因；不要留空，也不要用泛泛判断补齐。

## Candidate Scan Methodology

### Source Hierarchy

1. **Primary specs**：官方 EIP/ERC/RIP 页面与 GitHub raw markdown。用于方案状态、规范字段、交易类型、验证/执行模型、security considerations。
2. **Primary implementation / PR evidence**：`base/base`、`ethereum-optimism/design-docs`、`ethereum-optimism/specs`、`ethereum-optimism/optimism`、`ethereum-optimism/op-geth` 相关 PR、commit、design docs。用于 Base/OP 公开信号。
3. **Governance / roadmap records**：Ethereum Magicians、AllCoreDevs/硬分叉 meta、EIP-8081 Hegota meta。用于 EIP-8141/EIP-7701 等路线状态。
4. **Local accepted research**：WHI-275 framework、WHI-276 EIP-8130 deep dive、WHI-277 EIP-7702、WHI-278 ERC-4337。用于统一 rubric、已验证的 Base PR timeline、7702/4337 边界。
5. **Secondary commentary**：钱包/AA infra 博客、论坛综述、X threads。只用于发现候选或解释生态语境；不能作为关键规范或 Base 选型理由的唯一证据。

### Query Plan

Deep draft 至少执行以下检索，记录查询字符串、日期和结果摘要：

| Target | Query / Action | Required Output |
|---|---|---|
| EIP corpus | 搜索 `account abstraction`, `native account abstraction`, `EOA delegation`, `migration transaction`, `SETSELFDELEGATE`, `AUTHCALL`, `PAYGAS`, `frame transaction` | 候选/排除清单，含 EIP number、status、created date、superseded-by |
| RIP corpus | 搜索 `RIP-7560`, `native account abstraction`, `paymaster`, `validation frame`, `nonceKey` | RIP-7560 及 companion RIP 列表，区分主方案与组件 |
| Base PRs | `repo:base/base eip8130 OR 8130 OR "account configuration" OR authenticator OR "phased calls"` | PR number、title、state、mergedAt、merge commit/head SHA、URL、设计信号分类 |
| OP design docs/specs | `repo:ethereum-optimism/design-docs 8130 OR "account abstraction"`；`repo:ethereum-optimism/specs 8130 OR "account abstraction"` | 是否存在 OP 对 8130 的 design doc；尤其复核 design-docs #380 及相邻 PR |
| Governance/forum | Ethereum Magicians threads for EIP-8130/8141/7701/3074/7851, ACD/Hegota references | 是否有 explicit rationale；EIP-8141 是否仍 CFI |
| Prior local research | `base-eip8130-native-aa/research-sections/*/final.md` | 可复用结论、source anchors、已知 caveats |

### Inclusion Criteria

纳入 `candidate` 的方案必须至少满足一项：

- 引入 EIP-2718 新交易类型或等价 protocol transaction path，使智能账户/合约账户可作为 top-level sender 或验证主体。
- 修改 transaction validity、mempool admission、gas payment、validation/execution frame 或 nonce/replay 规则。
- 明确试图替代/enshrine ERC-4337 或实现 native account abstraction。

纳入 `adjacent` 的方案满足：

- 只解决 EOA migration、delegation lifecycle、residual ECDSA authority、或者 7702 的安全/迁移缺口；
- 需要协议改动，但不构成完整 native AA。

排除项包括：

- 纯应用层 smart wallet / SDK / paymaster 服务；
- ERC-4337 本体（已由 WHI-278 覆盖，本 issue 只作为对照）；
- EIP-7702 本体（已由 WHI-277 覆盖，本 issue 只讨论 post-7702 相邻延伸）；
- 非 Ethereum/EVM 账户模型，除非用于 Mantle 决策的背景对照。

## Initial Candidate And Exclusion Inventory

Deep draft 必须重新核验本表；本表只是 outline 阶段的初始工作集。

| Proposal | Initial class | Current status to verify | Why included / excluded | Expected D1~D13 treatment |
|---|---|---|---|---|
| EIP-8130 | comparison anchor | Draft; Base implementing | 本 issue 的比较基准；已有 WHI-276 final。 | 引用 WHI-276 row，不重复 full scoring。 |
| RIP-7560 | candidate | RIP Draft | Rollup-targeted native AA；接近把 ERC-4337 validation/paymaster/execution enshrine 到 rollup protocol。 | Full D1~D13 prefill required. |
| EIP-8141 | candidate | Draft; EIP-8081 Hegota CFI, not scheduled | Frame Transaction；当前最直接的 generalized native AA competitor。 | Full D1~D13 prefill required. |
| EIP-7701 | historical candidate | Withdrawn; superseded by EIP-8141 | EOF-native AA 前身，理解 8141 路线变化所必需。 | Full or condensed D1~D13 row; mark withdrawn caveats. |
| EIP-2938 | historical candidate | Status must be reverified | 早期 protocol AA proposal，新 tx type / PAYGAS / validation restrictions，是 4337 与后续 native AA 的历史前身。 | Condensed D1~D13 row; mark historical/stalled. |
| EIP-3074 | historical / EOA delegation | Withdrawn; superseded by EIP-7702 | 用户明确要求历史对照；解释 3074 -> 7702 -> 7851/8130 的路线分叉。 | Condensed D1~D13 row focused on D1-D11; D12/D13 mostly historical. |
| EIP-5003 | historical / EOA migration | Withdrawn; superseded by EIP-7702 | AUTHUSURP 迁移 EOA 代码，说明“永久迁移 EOA”路线为何退出。 | Exclusion/historical row; not full native AA unless draft upgrades. |
| EIP-7377 | adjacent / migration | Reverify status | One-time EOA-to-contract migration transaction；解决迁移而非完整 AA。 | Exclusion/adjacent row with D1/D2/D8/D11 only, unless upgraded. |
| EIP-7851 | adjacent / post-7702 lifecycle | Reverify status; requires EIP-7702 | Code-controlled EOA delegation + ECDSA-disabled delegation prefix；重要 post-7702 安全补丁路线，但不是完整 native AA。 | Adjacent row; full D1~D13 optional, at least D4/D8/D9/D11. |
| EIP-5806 | adjacent / historical EOA delegation | Reverify status | Delegate transaction：允许 EOA 用 delegate-call-like 机制执行任意代码；规范自称不是 AA primitive，但属于 3074/7702 历史路线。 | Adjacent/historical row; at least D1/D2/D4/D6/D8/D11. |
| ERC-4337 | baseline comparison | Final ERC | 已由 WHI-278 覆盖，作为 application-layer baseline。 | Reuse WHI-278 row only. |
| EIP-7702 | baseline comparison | Final, Pectra deployed | 已由 WHI-277 覆盖，作为 post-7702 starting point。 | Reuse WHI-277 row only. |

## Items

### item-1: 候选发现、排除清单与检索方法论

建立可复查的 search log 和 candidate inventory。输出必须包含：查询字符串、检索日期、source hierarchy、纳入/排除标准、候选清单、排除清单、每个方案的 status/accessed date、是否需要完整 D1~D13。重点避免两类错误：漏掉 EIP-8141/EIP-7851 这类较新的方案；把 EOA delegation/migration 方案误写成完整 native AA。

- **Priority**: high
- **Dependencies**: none

### item-2: RIP-7560 原理、定位与 8130 对照

拆解 RIP-7560 的 rollup-native AA 路线：AA transaction type、sender/paymaster validation、execution/postOp frame、nonce/paymaster model、mempool/DoS 限制、与 ERC-4337 的兼容/差异。对照 8130 时必须聚焦验证模型：7560 更接近 fully programmable account validation / 4337 enshrinement；8130 则显式声明 authenticator，使节点可按 canonical set 做 admission。还要判断 7560 是否被 Base/OP 公开讨论或拒绝。

- **Priority**: high
- **Dependencies**: item-1

### item-3: EIP-8141 与 EIP-7701 路线：Frame Transaction vs EOF-native AA

拆解 EIP-8141 的 Frame Transaction：`FRAME_TX_TYPE=0x06`、VERIFY/DEFAULT/SENDER frames、signature list、payment approval、atomic batch、public mempool rules、PQ/off-ramp 叙事；并回溯 EIP-7701 为何 Withdrawn / superseded by EIP-8141。不得把 8141 写成已 scheduled；所有 Hegota 说法必须通过 EIP-8081 或 ACD 记录核验为 CFI。对照 8130 时重点比较：完全可编程验证 vs bounded/canonical authenticator、PQ 灵活性 vs mempool 可预测性、通用 frame abstraction vs OP Stack 短期落地成本。

- **Priority**: high
- **Dependencies**: item-1

### item-4: 历史与相邻路线：EIP-3074、2938、5806、5003、7377、7851

做历史/相邻方案表，不把它们与完整 native AA 混为一谈。必须覆盖：

- EIP-3074 AUTH/AUTHCALL/invoker model，以及为何被 7702 取代；
- EIP-2938 作为早期 protocol AA proposal 的新 tx type / PAYGAS / validation restriction 思路；
- EIP-5806 delegate transaction 与 3074/7702 的 delegated execution 路线差异，尤其其不是完整 AA primitive 的边界；
- EIP-5003 / EIP-7377 的 EOA migration 价值与退出/边界；
- EIP-7851 如何试图解决 7702 residual ECDSA authority / delegation lifecycle 问题；

该 item 的目标是给 WHI-281 一张“为何没有选择这些路线”的历史版图，而不是对每个历史 EIP 做全文 deep dive。

- **Priority**: medium
- **Dependencies**: item-1

### item-5: Base/OP 选型动因取证：明确陈述 vs 合理推断

建立 Base/OP evidence table。必须至少覆盖：

- `base/base` EIP-8130 PR 时间线：引用 WHI-276 已验证列表，并重新核验当前 PR state/merge commit；
- `ethereum-optimism/design-docs` 中与 EIP-8130 / AA / FMA / compliance module 相关的 PR（尤其前序研究提到的 design-docs #380），以及是否包含 rationale；
- `ethereum-optimism/specs`、`optimism`、`op-geth` 对 AA 或 8130 的任何公开接口/讨论；
- Base/OP forum、EIP PR、Magicians、ACD/Hardfork meta 中对 8130、7560、8141 的比较或评论；
- Base product context：Base Account、x402/agent wallets、payment rails 只能作为产品动机背景，不能替代技术选型证据。

输出分两张表：

1. **明确陈述表**：source、quote/summary、URL、commit/PR SHA、statement owner、what it explicitly says、confidence。
2. **合理推断表**：signal、source anchors、inference、alternative explanations、confidence、what would falsify it。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4

### item-6: 候选方案 D1~D13 预填矩阵

按 WHI-275 final 的 rubric，给每个 `candidate` 方案产出一行 D1~D13，至少包含 RIP-7560、EIP-8141、EIP-7701、EIP-2938；对 EIP-3074/EIP-7851 等相邻/历史方案给 condensed row 或 explain why not full row。每格格式为：

```text
value | evidence_type | source_anchor | confidence | caveat_or_unknown_reason
```

特别注意：

- D4/D9 要区分 fully programmable validation、canonical authenticator set、EOA residual ECDSA authority、code-controlled delegation；
- D5 要区分 paymaster、payer field、frame payment approval、application-level sponsor；
- D7 要区分 protocol nonce、keyed nonce、contract nonce、authorization tuple nonce、nonce-free expiry；
- D10 要强制写 status/deployment/ecosystem；
- D12/D13 必须标注是否依赖后续 Mantle codebase / product strategy。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4

### item-7: 8130 vs 替代方案初步差异点清单

形成一张 decision-facing diff matrix，不做最终裁决。维度至少包括：

| Dimension | 8130 hypothesis | Alternative contrast to verify |
|---|---|---|
| Verification model | canonical/declared authenticator, bounded admission | 7560/8141 fully programmable validation requires stronger simulation/mempool constraints |
| Mempool DoS | nodes can filter by authenticator identity | alternatives may need validation tracing, storage/opcode constraints, reputation |
| Account model | account configuration + actor/scope + account changes | 7560 closer to 4337 accounts; 8141 frames are more general; 7702/7851 keep EOA lineage |
| Payer/sponsorship | native payer + payer_auth | 4337/7560 paymaster, 8141 payment approval, 7702 app sponsor |
| EOA migration | implicit EOA path + 7702-style delegation + account changes | 7702/7851 directly address EOA lifecycle; 7560/8141 need compatibility path |
| OP Stack implementation | Base PRs show concrete path | RIP/8141 may be less implemented in Base/OP public code |
| Flexibility/PQ | less flexible than fully programmable validation, but canonical set can evolve | 8141 strongest PQ framing; 7560/4337 contract validation flexible |
| Product fit | Base Account/payment/agent wallet hypothesis | Must verify against explicit Base docs, not assume |

- **Priority**: high
- **Dependencies**: item-5, item-6

### item-8: Gap Analysis 与 final section handoff notes

列出 deep draft 无法在公开资料中判定的事项，并明确给 WHI-281/WHI-282 的 downstream handoff：

- Base/OP 是否有 explicit no-to-7560/no-to-8141 statement；
- OP design-docs 是否只是记录 8130 相关设计，还是包含 adoption decision；
- 8141/Hegota 状态是否变化；
- Mantle OP Stack 实现成本是否需要另起 codebase issue；
- 是否有 Base 8130 devnet/testnet usage data；
- 哪些 D12/D13 判断必须留给最终决策章节。

- **Priority**: medium
- **Dependencies**: item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|---|---|---|
| source_anchor | URL、PR URL、commit SHA、local path、line/section、accessed date；每个 claim 至少一个 anchor。 | all |
| proposal_status | `Final` / `Draft` / `RIP Draft` / `Withdrawn` / `Stagnant` / `CFI` / `unknown`，并写 official source。 | item-1 to item-4 |
| inclusion_class | `candidate` / `comparison-anchor` / `historical` / `adjacent` / `excluded`，说明理由。 | item-1, item-4 |
| mechanism_summary | 交易结构、验证主体、payer/paymaster、execution model、nonce/replay 的 3-5 句摘要。 | item-2 to item-4 |
| validation_model | `bounded-authenticator` / `fully-programmable-validation` / `frame-verify` / `EOA-delegation` / `migration-only` / `application-layer`。 | item-2 to item-7 |
| mempool_admission_model | 节点/排序器如何判断可接受：authenticator allowlist、simulation/trace、opcode/storage limits、bundler alt-mempool、ordinary txpool。 | item-2, item-3, item-6, item-7 |
| relation_to_7702 | `replaces` / `complements` / `superseded-by-7702` / `extends-7702` / `independent`。 | item-3, item-4, item-7 |
| relation_to_4337 | `enshrines-4337` / `complements-4337` / `application-layer-baseline` / `unrelated`。 | item-2, item-4, item-7 |
| base_op_signal_type | `explicit-public-statement` / `code-pr-signal` / `design-doc-signal` / `roadmap-signal` / `inference` / `unknown`。 | item-5, item-7 |
| explicit_vs_inferred | 每条 Base/OP 动因结论必须标注 `explicit` 或 `inferred`，并附 falsification note。 | item-5 |
| rubric_dimension | WHI-275 D1~D13 的维度 ID，方便最终矩阵溯源。 | item-6 |
| unknown_reason | `spec-gap` / `implementation-gap` / `status-unstable` / `no-public-statement` / `mantle-not-inspected` / `ecosystem-data-missing`。 | item-6, item-8 |
| confidence | `high` / `medium` / `low`，并说明置信度来自 primary spec、code/PR、forum、secondary 或推断。 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|---|---|---|---|---|
| diag-1 | taxonomy | Post-7702 AA landscape：baseline anchors（4337/7702/8130）、active native candidates（7560/8141）、historical candidates（7701/2938/3074/5003）、adjacent migration/delegation（7377/7851）。 | mermaid | item-1, item-4 |
| diag-2 | comparison | Validation model continuum：application-layer EntryPoint -> EOA delegation -> bounded authenticator/account configuration -> programmable validation frames。 | mermaid | item-2, item-3, item-7 |
| diag-3 | timeline | Base/OP evidence timeline：Base 8130 PR waves、OP design-doc/spec signals、EIP/ACD/Hegota milestones；每个点标 explicit/inferred。 | mermaid | item-5 |
| diag-4 | matrix | Candidate D1~D13 prefill matrix with evidence/confidence/caveat cells. | ascii/table | item-6 |
| diag-5 | decision matrix | 8130 vs RIP-7560 vs EIP-8141 vs EIP-7701 vs adjacent routes：engineering cost, DoS, flexibility, ecosystem, Mantle fit。 | ascii/table | item-7 |
| diag-6 | evidence classifier | Decision tree for writing Base/OP motive as fact vs inference. | mermaid | item-5, quality checklist |

## Source Requirements

| ID | Type | Description | Min Count |
|---|---|---|---|
| src-1 | local_research | WHI-275 framework final, WHI-276 EIP-8130 final, WHI-277 EIP-7702 final, WHI-278 ERC-4337 final；必须复用 D1~D13 和既有 caveats。 | 4 |
| src-2 | official_specs | EIP-8130、RIP-7560、EIP-8141、EIP-8081、EIP-7701、EIP-2938、EIP-3074、EIP-5806、EIP-5003、EIP-7377、EIP-7851、EIP-7702、ERC-4337/EIP-4337；每个记录 status 和 accessed date。 | 11 |
| src-3 | base_prs | `base/base` EIP-8130 PRs：至少复核 WHI-276 已列的 #2863/#2866/#2868/#2926/#3008/#3119/#3121/#3170/#3440/#3467/#3534/#3535/#3540/#3557/#3585/#3586/#3589/#3651/#3653/#3680/#3696/#3720/#3749/#3753/#3754/#3755/#3763/#3766；每条给 URL/state/commit。 | 25 |
| src-4 | op_public_signals | `ethereum-optimism/design-docs`、`specs`、`optimism`、`op-geth` 中 8130/AA 相关 PR；至少核验前序研究提及的 design-docs #380 与 search-discovered 结果。 | 3 |
| src-5 | governance_forum | Ethereum Magicians / ACD / hardfork meta / EIP PR discussions：覆盖 8141/Hegota CFI、7701 withdrawal, 7851 discussion, 7560 discussion if available。 | 5 |
| src-6 | implementation_or_tests | 如果 Base/OP PR 涉及实现，至少抽样代码路径或 test/fixture 来验证不是纯设计讨论；否则标注 no-public-code。 | 5 |
| src-7 | secondary_discovery | 钱包/AA infra 或研究博客可用于发现候选和生态语境，但每个核心 claim 必须回到 src-1~src-6。 | optional |

## Expected Deep Draft Structure

1. **文首基线声明**：search cutoff、source hierarchy、status-sensitive claims、fact-vs-inference rule。
2. **Executive thesis**：post-7702 native AA 版图的核心分叉：bounded authenticator（8130） vs programmable validation（7560/8141） vs EOA delegation/migration（3074/7851/7377）。
3. **候选/排除清单**：candidate、historical、adjacent、excluded 四类表，含 status、URL、accessed date、是否 full D1~D13。
4. **方案机制表**：RIP-7560、EIP-8141、EIP-7701、EIP-2938、EIP-3074、EIP-7851 等逐项拆解。
5. **Base/OP 公开信号**：明确陈述表 + 合理推断表；如无明确选择理由，使用规定句式。
6. **D1~D13 prefill matrix**：每个候选方案每维度 `value/evidence/confidence/caveat`。
7. **8130 vs alternatives 差异点**：验证模型、mempool、payer、EOA migration、OP Stack 落地、生态、PQ/签名灵活性、Mantle fit。
8. **Downstream handoff**：哪些结论可直接给 WHI-281；哪些必须留给 WHI-282 或 Mantle codebase analysis；哪些仍是 unknown。
9. **Appendix**：search log、source table、PR table、unknown/rejected claims。

## Quality Checklist

- [ ] 文首写明检索截止日期 2026-06-27，并为所有外部来源写 accessed date。
- [ ] 候选清单至少覆盖 RIP-7560、EIP-8141、EIP-7701、EIP-3074；方法论补充 EIP-2938、EIP-5806、EIP-5003、EIP-7377、EIP-7851 或说明排除原因。
- [ ] 每个 proposal 的 status 用官方 EIP/RIP 或 hardfork meta 核验；尤其 EIP-8141 只能写 Draft/CFI，EIP-7701/3074/5003 的 withdrawn/superseded 必须可点开。
- [ ] Base/OP 选型动因分为明确陈述和合理推断；没有明确公开理由时使用规定句式，不代言 Base。
- [ ] 每条 Base/OP 公开信号附 PR URL、commit SHA、forum URL、design-doc URL 或 local final section anchor。
- [ ] D1~D13 每格有 value/evidence/confidence/caveat；不可判定维度写明 unknown_reason。
- [ ] 8130 vs alternatives 差异表明确区分工程落地、协议安全、产品场景和生态成熟度，不把“更 native”当作自动优势。
- [ ] 对 ERC-4337/EIP-7702/EIP-8130 已有章节只复用，不重复长篇机制说明。
- [ ] 输出能直接供 Research Review Agent 检查候选遗漏、Base 动因过度推断、D1~D13 证据空洞三类风险。

## Patch Log

| Round | Action | Target | Reason | Source |
|---|---|---|---|---|
| 1 | create outline | `base-eip8130-native-aa/outlines/post7702-native-aa-landscape.md` | Initial outline from Orchestrator dispatch for WHI-279. | Dispatch comment `9c31541f-bbab-40a8-9b59-7df9f0347143`; prior sections on main at commit `6bf3e8a39d9a6c069ed23746306108c42714cac2`. |
