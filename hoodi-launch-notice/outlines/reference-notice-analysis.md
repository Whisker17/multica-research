---
topic: "分析 Mantle Arsia 升级通告的格式与内容结构"
project_slug: hoodi-launch-notice
topic_slug: reference-notice-analysis
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: hoodi-launch-notice/outlines/reference-notice-analysis.md
  draft: hoodi-launch-notice/research-sections/reference-notice-analysis/drafts/round-{n}.md
  final: hoodi-launch-notice/research-sections/reference-notice-analysis/final.md
  index: hoodi-launch-notice/research-sections/_index.md

scope: |
  阅读并拆解 Mantle Arsia 升级通告的完整结构，包括标题、概述、Purpose、What's New、Impact
  Assessment、Summary、站内链接和行动指引。提取可复用的上线/升级通告模板、技术深度基准、
  目标读者定位和语言风格，并对比 Arsia 网络升级通告场景与 Hoodi 测试网上线场景在格式、风险提示、
  行动指引和技术说明深度上的差异。Arsia 升级的目标网络环境（主网/测试网）须经源文档验证后方可用于
  场景对比。研究必须覆盖 Arsia 原文、Mantle 官方文档站其他通告，以及
  至少 1-2 个 Optimism/Base 等 L2 官方升级或测试网上线通告作为外部对照。
audience: |
  Hoodi 上线通告的 Technical Writer、Mantle 协议/生态/开发者关系团队，以及需要审核上线公告结构、
  语气和技术准确性的项目负责人。读者熟悉 L2、OP Stack、rollup 升级和测试网上线的基本概念，
  但需要一份可直接转化为通告写作框架的结构化分析。
expected_output: |
  - 完整的 Arsia 通告结构分析文档，覆盖章节层级、信息顺序、技术内容密度、行动指引和语气
  - 通告模板：必备章节、可选章节、每章建议回答的问题、建议篇幅和证据类型
  - 针对 Hoodi 测试网上线场景的格式调整建议，明确哪些 Arsia 元素应保留、弱化、替换、删除或新增
  - 至少引用 Mantle Arsia 通告原文和 1-2 个 Optimism/Base 等 L2 项目的类似通告或官方升级文档
  - 至少比较 1 篇 Mantle 官方文档站其他通告，判断 Arsia 是否代表 Mantle 稳定公告模板
  - 至少 1 张 Mermaid 通告结构总览图，展示章节层次关系和内容要素

source_requirements_summary: |
  Deep phase 必须优先使用官方来源。Arsia 原文必须逐节拆解并保留短引；Mantle 站内对照建议优先使用
  "Migration of Data Availability to Ethereum Blobs" 和 "Limb Upgrade: Ensuring Mantle's Compatibility
  with Fusaka"；外部对照建议优先使用 Base 官方 Azul / hardfork / node-operator 升级文档与
  Optimism 官方 OP Stack hardfork / network upgrade 文档。Hoodi 背景建议使用 Ethereum Foundation
  "Holesky and Hoodi Testnet Updates"。若某外部页面无法直接抓取 Markdown，必须记录访问限制，并以可访问的
  官方 docs、spec、release note 或公告 URL 替代，不得用非官方二手文章替代。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-27T04:19:49Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-27T05:15:00Z"

multica_issue_id: de2f6b68-b0e4-424a-a50b-28db4c320a09
branch_name: research/hoodi-launch-notice/reference-notice-analysis
base_commit: 9c26c3322c79286538ae9b827640876fe489423c
language: "中文"
research_depth: "standard"

methodology_gate:
  primary_source_first: true
  arsia_must_be_section_by_section: true
  minimum_external_l2_comparisons: 2
  external_l2_policy: "优先 Optimism + Base；若其中一个官方页面抓取受限，必须说明限制并用同项目其他官方 docs/spec/release note 替代。"
  hoodi_scenario_policy: "不要把 Arsia 升级通告模板原样套用到 Hoodi；Arsia 的网络环境（主网/测试网）须经源文档验证后才能用于场景对比。必须单独建立测试网上线场景的读者、行动、风险和资源链接清单。"
  arsia_environment_gate: "场景对比前必须先完成 Arsia 升级环境验证（item-8）。官方通告页面标题声明 'Arsia Upgrade on Sepolia'（测试网），如正文暗示主网级别变更，draft 必须记录冲突并采用环境中性表述。"
---

# Research Outline: 分析 Mantle Arsia 升级通告的格式与内容结构

## Methodology Gate

Deep draft 开始前必须先完成四个事实底座：

1. **Arsia 原文逐节拆解**：列出原文所有一级/二级/三级标题、每段功能、技术点、行动对象和外链，不能只写摘要。
2. **对照样本登记表**：登记 Mantle 站内对照和 Optimism/Base 外部对照的 URL、页面类型、适用场景、可访问性和采用理由。
3. **Hoodi 场景边界**：明确 Hoodi 是测试网上线而非主网升级，因此行动指引、风险提示、成功指标和 CTA 必须围绕测试参与、开发者迁移、反馈渠道和已知限制设计。
4. **Arsia 升级环境验证**：在场景对比前，必须逐源记录 Arsia 升级的目标网络环境。官方通告标题声明"Arsia Upgrade on Sepolia"（测试网），如有来源声明主网环境，必须显式标记冲突并在对比中采用环境中性表述。

若官方页面只提供动态 HTML 或抓取失败，draft 必须记录访问方式与限制；可使用官方 `llms.txt`、`.md`、spec、release note、changelog、GitHub release 或官方 blog 作为替代证据，但不能用社区媒体替代官方对照。

## Pre-Verified Official Source Handles

以下是 outline 阶段已确认或推荐优先验证的官方来源入口。Deep draft 仍需重新抓取、逐条短引和记录访问时间。

| Source | URL | Access note | Required Use |
|--------|-----|-------------|--------------|
| Mantle Arsia Upgrade | https://docs.mantle.xyz/network/introduction/updated-notices/arsia-upgrade-mantles-new-fee-model-and-op-stack-alignment | GitBook HTML 与 `.md` alternate 均可用；`.md` 已显示完整章节 | 主样本，逐节拆解 |
| Mantle DA-to-Blobs notice | https://docs.mantle.xyz/network/introduction/updated-notices/migration-of-data-availability-to-ethereum-blobs | GitBook HTML 与 `.md` alternate 均可用 | Mantle 站内模板对照 |
| Mantle Limb/Fusaka notice | https://docs.mantle.xyz/network/introduction/updated-notices/limb-upgrade-ensuring-mantles-compatibility-with-fusaka | 从 Mantle Updated Notices 导航发现；deep phase 需验证正文可访问性 | Mantle 站内升级对照候选 |
| Optimism network upgrades | https://docs.optimism.io/op-stack/protocol/network-upgrades | 官方 docs，列出 OP Stack activations 与 upgrade process | 外部升级结构对照 |
| Optimism Holocene notice | https://docs.optimism.io/notices/archive/holocene-changes | 官方 notice，包含 breaking changes、activation、operator action | 外部 hardfork/action guide 对照 |
| Optimism Upgrade 14 notice | https://docs.optimism.io/notices/upgrade-14 | 官方 notice，包含 timeline、affected chains、chain/node/user operator sections | 外部 upgrade notice 对照候选 |
| Base Azul operator guide | https://docs.base.org/base-chain/node-operators/base-v1-upgrade | 官方 docs，搜索索引显示 activation timeline、required software、migration steps | Base operator/action guide 对照 |
| Base Azul announcement | https://blog.base.dev/introducing-base-azul | 官方 Base blog，公告口径与产品叙事对照 | Base announcement style 对照 |
| Hoodi testnet context | https://blog.ethereum.org/2025/03/18/hoodi-holesky | Ethereum Foundation official blog，说明 Hoodi launch、Pectra activation、client releases、testnet purpose | Hoodi 测试网场景边界 |

## Research Questions

1. Arsia 通告的完整章节结构是什么？标题、概述、Purpose、What's New、Impact Assessment、Summary 和链接导航分别承担什么传播功能？
2. Arsia 如何把 fee model、operator fee、dynamic EIP-1559、DA footprint block sizing、OP Stack fork alignment、RPC/API 和合约升级等技术变化压缩成可读公告？技术深度的上限和下限在哪里？
3. Arsia 如何区分用户、开发者、节点运营者、Mantle 网络本身等受众？哪些人需要行动，哪些人无需行动，行动链条是否闭环？
4. Arsia 的语言风格偏公告、技术说明、开发者文档入口还是风险沟通？它如何平衡主网升级的重要性与用户友好性？
5. Mantle 官方文档站其他 Updated Notices 是否使用相似结构？哪些模块是 Mantle 文档系统的稳定模板，哪些是 Arsia 场景特有？
6. Optimism/Base 同类通告如何处理 hardfork/testnet/network upgrade 的激活时间、版本要求、操作步骤、兼容性风险、链接资源和 CTA？
7. Hoodi 测试网上线与 Arsia 网络升级通告相比，公告目标、读者行动、风险级别、业务影响、技术说明和成功标准有哪些结构性差异？Arsia 升级的目标网络环境是否已被源文档明确验证？
8. 最终 Hoodi 上线通告应采用什么模板？哪些章节为必备、可选或不建议使用？

## Items

### item-1: Arsia 通告的章节骨架与信息排序

拆解 Mantle Arsia 升级通告从标题到正文结尾的完整结构，记录每一层标题、段落功能和读者任务。重点识别通告如何先建立升级价值，再解释技术变化，最后转向影响范围与行动指引。Deep draft 需要输出"章节 - 原文位置 - 目的 - 关键信息 - 受众 - 可复用性"表格，避免只做摘要。

必须覆盖：

- 标题和副标题如何同时传达主题、技术方向和生态定位；
- Overview 如何定义升级性质、核心变化和收益；
- Purpose 如何把技术变化拆成 numbered drivers；
- What's New 如何从 fee model、operator fee、EIP-1559、RPC、contract upgrades、node-level improvements 逐层展开；
- Impact Assessment 如何按用户/开发者/节点运营者分组；
- Summary 如何把技术细节重新压缩成 3-5 个记忆点；
- 文内链接如何把复杂公式、changelog、operator 指南等内容外移。

- **Priority**: critical
- **Dependencies**: none

### item-2: Arsia 核心内容模块与技术深度基准

分析 Arsia 通告如何说明 Mantle 新 fee model、OP Stack alignment、升级前后行为差异和相关技术背景。需要判断每个技术点的解释深度：哪些内容面向普通用户，哪些面向节点运营者、开发者或生态项目方，哪些依赖外部文档链接承接。输出应形成 Hoodi 通告可复用的技术深度标尺，而不是复述 Arsia 技术方案本身。

必须覆盖：

- fee model 相关模块：compression-based L1 data fee、FastLZ、dual scalars、operator fee、three-component fee；
- fee market 相关模块：dynamic EIP-1559、block extraData、minimum base fee、DA footprint gas scalar；
- compatibility 相关模块：Canyon through Jovian fork alignment、op-node baseline、standard OP Stack blob format；
- API/contract 相关模块：`eth_estimateTotalFee`、`eth_getBlockRange` deprecation、L1Block/GasPriceOracle/OperatorFeeVault/SystemConfig；
- 技术深度分层：正文解释、公式级细节、合约级细节、operator 版本/命令、外链承接；
- 对 Hoodi 的启示：测试网上线时技术说明应解释"为什么值得参与/测试"而不是主网 fee impact。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 影响范围、风险提示与行动指引模式

调查 Arsia 通告如何处理受影响对象、升级窗口、节点/应用/用户需要采取的行动、无需行动的对象，以及潜在风险或兼容性提示。需要提取"谁需要做什么、何时做、如果不做会怎样、去哪里获取更多帮助"这一行动指引链条。该项将直接决定 Hoodi 测试网上线通告是否需要区分 validators、node operators、developers、wallets、bridges、生态 dApps 和普通测试用户。

必须覆盖：

- Arsia 原文中的用户、开发者、节点运营者三类影响描述；
- "required upgrade" 的表述位置、强度和缺失信息；
- 是否提供激活时间、版本号、changelog、回滚/失败后果、支持渠道；
- 对普通用户"无需行动"与费用变化"会感知到"之间的张力；
- 对开发者"estimateGas 仍可用，但应采用新 API"的迁移强度；
- 对 Hoodi 的调整：测试网应新增 faucet、RPC、explorer、bridge/testing constraints、known issues、feedback/support channels、测试任务和非生产风险。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 目标读者定位与语言风格

分析 Arsia 通告的读者假设、措辞风格、技术术语解释方式和可信度建设方式。需要区分公告/营销叙事、技术迁移说明、开发者文档入口和风险沟通四类语气，并判断 Arsia 如何在同一篇通告内平衡这些需求。输出应给出 Hoodi 通告的推荐语气：测试网语境下应更强调参与、实验性、反馈渠道和非生产风险，弱化主网升级式的强业务影响表述。

必须覆盖：

- 标题和 Overview 的定位：面向生态的 announcement 还是面向 operator 的 upgrade notice；
- "major network upgrade"、"significant improvements"、"generally lower/fair pricing" 等价值表达如何与技术事实配合；
- 技术术语是否解释充分，是否对非工程读者友好；
- 风险和不确定性是否显性表达，哪些内容被省略；
- Hoodi 推荐语气：清晰、测试导向、邀请参与、透明列出限制，不使用主网确定性收益口径夸大测试网意义。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: Mantle 官方文档站其他通告的版式一致性

选择 Mantle 官方文档站 Updated Notices 或相邻公告中的其他 1-2 篇通告，与 Arsia 通告比较标题格式、开头概述、技术变更说明、行动指引、链接导航和收尾方式。目标是确认 Arsia 是 Mantle 文档站的稳定公告模板，还是针对主网升级的一次性结构。该项需要特别关注 Mantle 站内链接习惯和信息架构，便于 Hoodi 通告保持品牌和文档系统一致性。

优先对照样本：

- `Migration of Data Availability to Ethereum Blobs`：DA 迁移、security/economics/OP Stack alignment、用户/开发者/网络分组；
- `Limb Upgrade: Ensuring Mantle's Compatibility with Fusaka`：测试网 Sepolia 升级、Purpose、What's New、Impact Assessment、Summary；
- 如 deep phase 发现 Mantle 文档站还有更贴近 Hoodi 的测试网上线/网络更新页，可替换或补充。

- **Priority**: medium
- **Dependencies**: item-1

### item-6: Optimism / Base 同类通告对比样本

选取至少 1-2 个 L2 官方升级或测试网上线通告作为外部对照，优先覆盖 Optimism 和 Base。研究它们如何组织激活时间、技术变化、操作者行动、风险沟通和开发者链接。对比重点不是评判项目优劣，而是找出 Hoodi 通告可借鉴的行业常见结构与可避免的缺口。

优先候选：

- Base 官方 `base-chain/node-operators/base-v1-upgrade`：用于对比 operator migration、client version、hardfork 行动指引；
- Base 官方 `Introducing Base Azul` blog 与 Azul specs/docs：用于对比 hardfork feature taxonomy、technical depth、announcement narrative 和 reader routing；
- Optimism 官方 `op-stack/protocol/network-upgrades`、`notices/archive/holocene-changes`、`notices/upgrade-14` 或同等级官方 notice/release note：用于对比 OP Stack upstream 的 activation / protocol-change notice；
- 若抓取 Optimism docs 页面受限，必须记录限制，并用 Optimism 官方 specs、release notes、GitHub release 或 governance/forum announcement 替代。

必须输出：

- 样本选择表：项目、URL、页面类型、场景、采用理由、可访问性；
- 横向对比表：章节结构、激活时间、行动对象、技术深度、风险/兼容性、CTA/link routing；
- Hoodi 可借鉴项与不可照搬项。

- **Priority**: high
- **Dependencies**: item-1, item-3

### item-7: Hoodi 官方测试网语境与公告边界

建立 Hoodi 测试网事实底座，避免把 Hoodi 当作泛泛的内部测试环境或主网升级。Deep draft 需要优先使用 Ethereum Foundation 官方 Hoodi/Holesky testnet update、Ethereum testnet docs、client release notes，以及项目内部提供的 Hoodi 网络参数资料，确认 Hoodi 的上线目的、测试周期、参与者、网络参数和已知限制。

必须覆盖：

- Hoodi 是否作为 Holesky 后继/补充测试网，以及它与 Sepolia、Holesky 的定位差异；
- 官方公布的 Hoodi launch、Pectra activation、client release、validator/operator participation、staking/testing purpose；
- Hoodi 上线通告需要的 factual checklist：chain ID、RPC、explorer、faucet、bridge、docs、status page、client versions、known issues、support channel；
- 哪些参数来自 Ethereum Foundation 或公共生态，哪些必须由 Mantle/Hoodi 项目内部提供，不能在 draft 中臆造；
- Hoodi 作为测试网时必须明确的非生产风险、可能重置、rate limit、资金无价值、support/SLA 边界。

- **Priority**: high
- **Dependencies**: item-3, item-6

### item-8: Arsia 升级环境与源文档冲突检查门控

在进入场景对比（item-9）之前，必须先对 Arsia 升级的网络环境进行源文档级别的验证。当前 Mantle 官方 Arsia 通告页面（https://docs.mantle.xyz/network/introduction/updated-notices/arsia-upgrade-mantles-new-fee-model-and-op-stack-alignment）标题区域包含"Arsia Upgrade on Sepolia"字样，Sepolia 是以太坊测试网。然而通告正文描述的变更（fee model 重构、OP Stack 对齐、合约升级等）可能暗示主网级别的影响范围。Draft 必须在此项中解决环境分类的歧义，确保下游所有场景对比（item-9）和模板设计（item-10）建立在经过验证的事实基础之上。

必须覆盖：

- (a) **逐源环境记录**：分别记录 Arsia 升级的目标网络环境——官方通告页面、Mantle docs 其他页面引用、站内对照通告中的交叉引用各自声明了什么环境（Sepolia 测试网、主网、未明确声明）；
- (b) **激活参数记录**：记录每个来源所述的 Arsia 激活时间/窗口（timestamp 或 block number）和受影响的运营者集合（validators、node operators、sequencer、dApp developers 等）；
- (c) **环境置信度判断**：对"Arsia 升级目标环境"给出置信度（high / medium / low），并说明判断所依据的证据链——标题声明、正文上下文、跨页交叉引用、Limb/Fusaka 通告中 Sepolia 环境的类比等；
- (d) **冲突标记与保守处理**：如果不同官方来源之间（或同一通告标题与正文之间）对环境描述存在矛盾，必须显式标记该冲突，记录各方表述，并在后续场景对比中采用环境中性表述（"Arsia 网络升级"而非"Arsia 主网升级"），直到获得明确的官方主网确认。

- **Priority**: critical
- **Dependencies**: item-1

### item-9: Arsia 网络升级通告 vs Hoodi 测试网上线通告的场景差异

系统比较 Arsia 网络升级通告与 Hoodi 测试网上线通告在公告目标、读者行动、风险级别、业务影响、技术说明和成功标准上的差异。本项必须以 item-8 的环境验证结论为前提——如果 Arsia 的目标环境被确认为测试网（Sepolia），则对比轴从"主网升级 vs 测试网上线"调整为"测试网升级通告 vs 测试网上线通告"；如果环境未确认，则采用环境中性的"网络升级通告 vs 测试网上线通告"框架。需要明确哪些章节应直接保留，哪些应改写为"测试网参与/迁移/反馈"导向，哪些升级元素应降级为可选，哪些测试网场景必须新增。

必须覆盖：

- 目标差异：网络升级强调连续性、兼容性、安全和强行动；测试网上线强调可用性、参与方式、测试目标和反馈；
- 读者差异：Arsia 以 users/developers/node operators 为主；Hoodi 可能需要 developers、node operators、validators/test participants、wallet/infra providers、ecosystem partners；
- 行动差异：Arsia 是 upgrade-before-fork；Hoodi 是 connect/deploy/test/report/migrate-from-old-testnet；
- 风险差异：网络升级风险更强调 service continuity；测试网风险应明确非生产、可能重置、faucet 限制、已知问题、支持窗口；
- 技术差异：Arsia 可深入 fee/protocol upgrade；Hoodi 应解释 network parameters、RPC、explorer、bridge/faucet、chain ID、compatibility、test objectives；
- 成功指标差异：网络升级为升级完成和稳定运行；测试网为参与量、反馈质量、生态集成、问题发现；
- 环境敏感性：上述所有对比维度的表述必须与 item-8 验证结论一致，不得超出已验证的环境分类做出假设。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-6, item-7, item-8

### item-10: 可交付通告模板与写作检查清单

将前述分析综合为可执行的 Hoodi 上线通告模板，包括必备章节、可选章节、每章目的、建议篇幅、技术深度、证据/链接要求和禁忌事项。模板应能被 Technical Writer 直接拿来组织正文，并包含一份发布前检查清单，覆盖事实准确性、目标读者、行动指引、链接完整性、风险提示和风格一致性。模板中涉及 Arsia 对比的章节必须使用经 item-8 验证的环境表述。

建议模板必须至少包含：

1. 标题：Hoodi 测试网上线/开放测试的直接陈述；
2. TL;DR / Overview：上线状态、目标、谁应关注、核心入口；
3. Why Hoodi / 测试目标：上线目的、希望验证的协议或生态能力；
4. Network Information：chain ID、RPC、explorer、faucet、bridge、docs、status page；
5. What's Available / What's New：功能范围、兼容性、限制；
6. Who Should Do What：开发者、节点/infra、生态项目、测试用户；
7. Known Limitations and Risk：非生产、可能重置、rate limit、合约/桥限制；
8. Feedback and Support：issue、Discord/Telegram/forum、bug bounty 或反馈表单；
9. Next Steps：后续里程碑、更新节奏、迁移计划。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7, item-8, item-9

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| source_url | 被分析通告或参考资料的官方 URL，优先使用可稳定访问的原文链接 | all |
| source_access_method | `markdown` / `html` / `llms.txt` / `spec` / `release_note` / `github_release` / `manual_browser`；记录访问限制 | all |
| section_inventory | 原文标题层级、段落功能和信息顺序的结构化清单 | item-1, item-5, item-6 |
| content_function | 每个章节承担的传播功能：宣布、解释、证明、指引、风险提示、链接导航、CTA | item-1, item-5, item-6, item-10 |
| technical_depth | 技术说明的深度等级、术语解释方式、是否需要外链承接细节 | item-2, item-4, item-6, item-9, item-10 |
| audience_segments | 面向的读者群体及各自需要的信息：用户、开发者、节点运营者、生态伙伴、测试参与者、内部审核者 | item-3, item-4, item-7, item-9, item-10 |
| action_requirements | 读者需要采取的具体行动、时间窗口、前置条件、失败后果和支持渠道 | item-3, item-6, item-7, item-9, item-10 |
| risk_and_impact_language | 通告如何描述影响范围、风险、不确定性、兼容性和无需行动的对象 | item-3, item-4, item-6, item-7, item-9 |
| reusable_template_element | 可迁移到 Hoodi 通告的结构元素、推荐写法和需要调整的原因 | item-1, item-2, item-3, item-4, item-5, item-6, item-9, item-10 |
| hoodi_adjustment | 针对 Hoodi 测试网上线场景的保留、弱化、替换、新增或删除建议 | item-7, item-8, item-9, item-10 |
| factual_gap | Hoodi 通告所需但外部资料不足、必须向项目方确认的事实，如 network parameters、RPC、faucet、bridge、support channel | item-7, item-10 |
| evidence_quote | 关键原文短引或可验证事实，需遵守引用长度限制并配合解释 | all |
| confidence | `high` / `medium` / `low`，说明证据是否来自官方原文、间接索引或不可完整访问页面 | all |
| environment_classification | Arsia 升级的目标网络环境分类（Sepolia 测试网 / 主网 / 未确认），逐源记录并标注置信度和冲突 | item-8, item-9 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy | 通告结构总览图：以"上线/升级通告"为根节点，展示标题、概述、背景/Purpose、技术变化/What's New、影响范围、行动指引、资源链接、风险/限制、反馈渠道、收尾 CTA 等层级，并标注 Arsia 原文已有章节与 Hoodi 建议新增/调整章节 | mermaid | item-1, item-9, item-10 |
| diag-2 | comparison | Arsia 网络升级通告 vs Hoodi 测试网上线通告的内容映射图：左侧列出 Arsia 模块，右侧列出 Hoodi 对应模块，边上标注保留/弱化/替换/新增/删除；对比框架须与 item-8 环境验证结论一致 | mermaid | item-9, item-10 |
| diag-3 | flow | 读者行动路径图：按用户类型展示"读到通告 -> 判断是否受影响 -> 查找参数/链接 -> 执行动作 -> 验证/反馈"流程，用于检查行动指引是否闭环 | mermaid | item-3, item-7, item-10 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | Mantle Arsia 升级通告原文：https://docs.mantle.xyz/network/introduction/updated-notices/arsia-upgrade-mantles-new-fee-model-and-op-stack-alignment；必须作为主样本逐节拆解 | 1 |
| src-2 | official_docs | Mantle 官方文档站其他 Updated Notices / announcements，用于判断 Mantle 内部公告格式一致性和站内链接习惯；优先 DA-to-blobs 与 Limb/Fusaka 通告 | 1 |
| src-3 | official_docs | Optimism 官方升级或测试网相关通告，包括 OP Mainnet/Sepolia、OP Stack hardfork、网络升级说明、spec 或 official release note | 1 |
| src-4 | official_docs | Base 官方升级、测试网、网络上线或 hardfork 通告，例如 Base Azul upgrade、Base v1 node operator upgrade、Base Sepolia/network information、Base hardfork specs | 1 |
| src-5 | official_docs | Hoodi 或 Hoodi 所依赖生态的官方上下文资料，用于理解"测试网上线"与"主网升级"的语境差异；优先 Ethereum Foundation Hoodi/Holesky testnet update、Ethereum testnet docs、client release notes 或项目内部提供的 Hoodi 背景材料 | 1 |
| src-6 | internal_research | 仓库内既有 Mantle/Base/OP Stack 研究可作为背景线索，例如 `base-azul-upgrade`、`base-vs-mantle-reth-analysis`、`mantle-stage1-rollup`；所有时间敏感事实必须回到官方来源复核 | 0 |
| src-7 | expert_commentary | 可选：L2 通告写作、developer relations 或 network upgrade communication 的行业评论，仅用于辅助风格判断，不得替代官方来源 | 0 |

## Output Structure for Deep Draft

Deep draft 建议采用以下章节：

1. Executive Summary：3-5 条对 Hoodi 通告最有用的结论；
2. Arsia 原文结构拆解：逐节 inventory + 信息顺序分析；
3. Arsia 技术深度与读者定位：技术模块、术语处理、外链承接；
4. 影响范围与行动指引：users/developers/operators 的行动链条；
5. Mantle 站内通告模板对照：Arsia vs DA-to-blobs / Limb；
6. Optimism/Base 外部样本对照：行业结构模式；
7. Hoodi 测试网官方语境与事实缺口；
8. Arsia 升级环境验证与源文档冲突记录；
9. Arsia 网络升级通告 vs Hoodi 测试网上线通告场景差异矩阵；
10. Hoodi 上线通告模板与写作检查清单；
11. Mermaid diagrams；
12. Evidence appendix：官方 URL、短引、访问限制、置信度。

## Quality Checklist

- [ ] Arsia 原文逐节拆解，不只做摘要；
- [ ] Arsia 升级环境经源文档验证，冲突（如有）已显式标记，场景对比采用经验证的环境表述；
- [ ] 至少 1 篇 Mantle 站内通告对照；
- [ ] 至少 1 篇 Optimism 官方对照和 1 篇 Base 官方对照，或记录无法访问并用同项目官方替代；
- [ ] 至少 1 个 Hoodi/Ethereum Foundation 官方上下文来源，并列出 Hoodi 通告事实缺口；
- [ ] Hoodi 测试网上线差异单独成章；
- [ ] 输出可直接交给 Technical Writer 的模板和检查清单；
- [ ] 至少包含 `diag-1` Mermaid 通告结构总览图；
- [ ] 所有引用均来自官方来源或清楚标注为内部背景；
- [ ] 不写 `_index.md`，不生成 final 或 draft 文件。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create_outline | full | Orchestrator dispatch outline round 1 | Multica comment b0c256f1-5ab6-449a-93d4-46283c853217 |
| 2 | add_item | item-8 (source-conflict/environment gate) | Research Review Agent major finding: Arsia 通告标题声明 "Arsia Upgrade on Sepolia"（测试网），不能假设主网环境；须在场景对比前增加环境验证门控 | Review Verdict f1fb7998 via Orchestrator Revision Request 9e106a77 |
| 2 | reframe_item | item-9 (was item-8) | 标题和内容从"Arsia 主网升级 vs Hoodi 测试网上线"改为"Arsia 网络升级通告 vs Hoodi 测试网上线通告"，移除未经验证的主网假设 | Review Verdict f1fb7998 via Orchestrator Revision Request 9e106a77 |
| 2 | renumber_item | item-10 (was item-9) | 因 item-8 插入，原 item-9 顺延为 item-10，依赖链同步更新 | Cascading from item-8 insertion |
| 2 | update_methodology | methodology_gate, scope, fields, diagrams, output structure, quality checklist | 全局移除未经验证的"主网"假设，新增 arsia_environment_gate 和 environment_classification 字段，所有场景对比表述改为环境中性 | Review Verdict f1fb7998 |
