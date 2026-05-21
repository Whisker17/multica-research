---
topic: "Mantle Exit Window 根因分析与对标研究"
project_slug: mantle-l2beat-risk-deficiency
topic_slug: mantle-exit-window-analysis
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: mantle-l2beat-risk-deficiency/outlines/mantle-exit-window-analysis.md
  draft: mantle-l2beat-risk-deficiency/research-sections/mantle-exit-window-analysis/drafts/round-{n}.md
  final: mantle-l2beat-risk-deficiency/research-sections/mantle-exit-window-analysis/final.md
  index: mantle-l2beat-risk-deficiency/research-sections/_index.md

scope: |
  深入分析 Mantle 在 L2Beat Risk Analysis 的 Exit Window 维度被标红的具体原因，并与通过该指标的
  L2 项目做法对标。研究必须覆盖 Mantle 合约升级机制（ProxyAdmin、TimelockController、权限链）、
  当前 timelock delay 的链上精确值、proposer/executor/admin 权限、是否存在绕过 timelock 的即时升级路径、
  force inclusion / withdrawal finalization 相关延迟、effective exit window 的计算推导、L2Beat 标红判定条件、
  Sequencer Failure / Proposer Failure 是否为 non-zero Exit Window 的前置条件、Arbitrum One 与 OP Mainnet
  的对标配置，以及延长 timelock 后对紧急修复和运营流程的影响。
audience: |
  Mantle 协议工程与治理团队、Multica 研究 squad 下游 Technical Writer、以及关注 L2Beat Risk Chart
  升级安全维度的 L2 协议研究者。读者默认理解 OP Stack / rollup bridge / proxy upgrade 基础概念，
  但需要本研究给出可复核的一手证据链、精确数值、对比表和根因总结。
expected_output: |
  - Mantle 当前合约升级权限链完整图解（含 ProxyAdmin、timelock、multisig、可执行升级的直接/间接权限）。
  - Mantle 当前 effective exit window 的精确计算推导：upgrade delay、force inclusion 或 withdrawal exit delay、
    L2Beat 采用的公式、7 天红线差距。
  - Mantle vs Arbitrum One vs OP Mainnet 的 Exit Window 配置对比表，明确 primary/emergency 与 regular
    exit-window 路径、页面文案、源码表达式、以及每个 comparator 是正向通过样本还是 negative/control case。
  - L2Beat 标红 Mantle Exit Window 的具体原因定位，引用 L2Beat 源码配置和页面展示。
  - 对 `l2beat-risk-assessment-framework` 结论的显式导入：验证 L2Beat Risk Rosette / riskView 口径下
    Sequencer Failure 与 Proposer Failure 是否必须为 green 才能支撑 non-zero Exit Window，并说明它们
    对 Mantle Exit Window 改善是否构成阻塞依赖；不得越界重做 Proposer Failure 根因分析。
  - 1-3 个导致 Mantle 不合格的核心根因，以及把 timelock 延长到满足要求时的运营影响。
  - Evidence 必须引用 Mantle Etherscan verified contracts / on-chain reads、l2beat/l2beat 源码、
    L2Beat Mantle 项目页、Arbitrum 与 OP Mainnet 的一手或准一手配置来源，并记录 `fetched_at`
    时间戳与 L2Beat source commit / permalink metadata。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-21T10:06:43Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-21T10:37:00Z"
---

# Research Outline: Mantle Exit Window 根因分析与对标研究

## Items

### item-1: 证据基线与 Mantle 合约地址清单

建立 Mantle Exit Window 研究的可复核证据基线。先从 L2Beat Mantle 配置、ProjectDiscovery 输出、Mantle 官方网络配置、Etherscan verified contracts 和链上读数交叉确认本研究要分析的 L1 合约集合，避免引用过期地址或非生产实例。该 item 输出所有后续计算使用的 canonical contract inventory，并标注每个地址的来源、链、代理/实现关系、验证状态和是否纳入 L2Beat 当前风险页面。

- **Priority**: high
- **Dependencies**: none

### item-2: Mantle 合约升级权限链与 timelock 精确参数

解析 Mantle 当前合约升级链路：ProxyAdmin / proxy owners / TimelockController / multisig / proposer / executor / admin roles 之间的控制关系。必须通过 Etherscan source、ABI read、event history 或 RPC 调用确认当前 `minDelay` / `getMinDelay()` 精确值、角色成员、角色 admin、executor 是否开放、以及谁能 schedule / execute / cancel 升级。该 item 还要区分普通升级路径与任何 emergency / owner / admin / multisig 直接调用路径。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 即时升级或 timelock 绕过路径排查

专门排查 Mantle 是否存在可以绕过 timelock 的即时升级路径，以及 L2Beat 如何处理这类路径。调查范围包括 ProxyAdmin owner 是否可直接 `upgrade` / `upgradeAndCall`、TimelockController 是否只是部分合约 owner、multisig 是否同时持有其他关键权限、pause/guardian/transaction-filterer 是否能变相影响退出、以及是否存在被 L2Beat 视为 "instantly upgradable" 或 "no exit window" 的权限结构。该 item 的结论要明确：如果存在绕过路径，effective exit window 是否应按 0 处理；如果不存在，哪些链上证据支持该判断。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Mantle force inclusion / withdrawal exit delay 与 effective exit window 计算

确认 L2Beat 计算 Mantle Exit Window 时使用的 `exitDelay` 含义和精确值，区分 force inclusion delay、withdrawal finalization period、challenge/finality delay、proof maturity delay 等可能被混用的延迟。根据 L2Beat Risk Chart 公式 `window = upgradeDelay - exitDelay` 复算 Mantle effective exit window，给出秒、小时、天三个单位，并量化与 7 天最低要求的差距。该 item 必须导入 `l2beat-risk-assessment-framework` final 中 Risk Rosette / riskView 的 Exit Window 口径，并把 "Sequencer Failure 与 Proposer Failure 均为 green 是 non-zero Exit Window 的前置条件" 作为待验证的 gating claim 写入分析：若 Mantle 当前 `Proposer failure = Cannot withdraw` 或 Sequencer Failure 不满足 green，需要明确标为 blocking dependency，并说明"仅延长 timelock"是否足以改变 Exit Window 风险展示。该 item 要输出一条可审计的计算链：链上配置值 -> L2Beat discovery/config 值 -> riskView 函数入参 -> 页面显示结果。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: L2Beat Mantle 标红判定定位

从 l2beat/l2beat 源码和 L2Beat Mantle 项目页定位 Mantle Exit Window 被标红的直接配置和判定路径。需要确认 Mantle 是否走 OP Stack 模板默认、项目特定 `nonTemplateRiskView.exitWindow` 覆盖、ProjectDiscovery 自动值，或人工配置值；同时引用 `riskView.ts` 中 Exit Window sentiment 阈值和展示文案。该 item 还要把 prior framework 的 Sequencer Failure / Proposer Failure prerequisite 检查纳入判定路径，输出一个明确结论：Proposer Failure root-cause analysis out-of-scope，但 Proposer Failure 当前状态是否阻塞 Exit Window improvement 必须 in-scope 回答。该 item 必须把 "页面为什么红" 拆成源码文件、配置字段、函数调用、最终文案四层，而不是只给口头解释。

- **Priority**: high
- **Dependencies**: item-1, item-4

### item-6: Arbitrum One 对标：current Exit Window 分类

分析 Arbitrum One 在 L2Beat Exit Window 上的 current status，不得预设其为通过样本。必须把 L2Beat 页面主文案（例如 `Exit window: None`）、regular 子字段（例如 `Regular: 10d` 或当前页面实际值）、emergency / instant-upgrade primary path、以及源码表达式（如 `EXIT_WINDOW_PERMISSIONLESS_BOLD` / `withRegularExitWindow`）分列说明，并标注该 comparator 是正向 non-zero/passing 样本还是 negative/control case。重点解释即时 Security Council / emergency 权限是否主导 primary sentiment，以及普通升级与紧急升级在风险口径中的区别。该 item 输出可与 Mantle 同列比较的字段，而不是泛泛描述 Arbitrum 治理。

- **Priority**: medium
- **Dependencies**: item-5

### item-7: OP Mainnet 对标：OP Stack 项目的通过路径与限制

分析 OP Mainnet 当前在 L2Beat Exit Window 维度的配置和判定路径，明确它与 Mantle 同属或接近 OP Stack 体系时的关键差异。调查 Superchain governance / ProxyAdmin owner / ProtocolVersions / OptimismPortal / delayed upgrade path / Guardian 或 Security Council 权限，并确认 L2Beat 对 OP Mainnet 的源码配置和页面显示。该 item 必须把 OP Mainnet 当前页面是否仅显示 `None`、是否存在 regular 子字段、源码表达式、以及 primary/emergency 与 regular 路径分类写入对比表；如果 OP Mainnet 不是 current non-zero/passing comparator，则必须明确标为 negative/control case。该 item 要特别说明 Mantle 如果采用类似 OP Mainnet 的 timelock 或 governance 结构，需要满足哪些前置条件才可能改变 L2Beat 风险视图。

- **Priority**: medium
- **Dependencies**: item-5

### item-8: 根因归纳与改进路径的运营影响

综合 Mantle 现状计算、L2Beat 判定规则、Sequencer/Proposer prerequisite 检查和 Arbitrum/OP 对标结果，归纳 1-3 个导致 Mantle Exit Window 不合格的核心问题。改进路径只做研究级别的可行性和影响分析：例如 timelock 需延长到多少才满足 7 天窗口、是否还要消除即时绕过路径、是否必须先解决 Proposer Failure / Sequencer Failure 才能让 Exit Window 从 None 变为 non-zero、延长后对紧急 bug 修复、bridge incident response、governance 执行节奏和监控告警的影响。该 item 不写具体实施步骤或治理提案细节，避免越界到综合建议 issue。

- **Priority**: high
- **Dependencies**: item-4, item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| source_type | 证据类别：verified_contract、on_chain_read、l2beat_source、l2beat_page、official_docs、governance_docs、secondary_analysis。 | all |
| source_url_or_ref | 永久链接、Etherscan URL、GitHub commit permalink、RPC call 说明或文档 URL；最终 draft 不得只写仓库首页。 | all |
| fetched_at | 页面抓取、链上读取或源码观察的 UTC 时间戳；L2Beat 页面 snapshot 和链上读数必须精确到 ISO-8601。 | all |
| source_commit_metadata | L2Beat source / ProjectDiscovery / local framework artifacts 的 commit SHA、branch、permalink 行号；网页来源填 N/A 但要有 fetched_at。 | item-1, item-4, item-5, item-6, item-7 |
| chain_and_address | 合约所在链、地址、合约名、proxy/implementation 关系；非合约来源填 N/A。 | item-1, item-2, item-3, item-4 |
| observed_value | 读取到的关键值，如 `getMinDelay()`、role member、owner、finalization period、force inclusion delay、L2Beat config literal。 | item-2, item-3, item-4, item-5, item-6, item-7 |
| unit_and_normalized_days | 原始单位与标准化为 days 的值；秒/区块/小时必须写出转换公式。 | item-4, item-6, item-7, item-8 |
| verification_method | 如何验证该值：ABI read、event trace、source code constant、L2Beat discovery JSON、manual page observation、official docs。 | all |
| l2beat_interpretation | L2Beat 如何把该事实映射为 Exit Window 入参、文案、sentiment 或特殊规则。 | item-3, item-4, item-5, item-6, item-7 |
| prerequisite_status | Sequencer Failure 与 Proposer Failure 当前状态、是否为 green、是否满足 non-zero Exit Window gating claim、是否阻塞 Mantle Exit Window 从 None 改善为 non-zero；必须区分"引用 framework 结论"与"本研究新验证"。 | item-4, item-5, item-8 |
| trust_boundary | 谁能触发或绕过升级、谁能审查、用户需要信任哪个 multisig/SC/governance/timelock。 | item-2, item-3, item-6, item-7, item-8 |
| comparison_dimension | 对比字段：upgrade delay、exit delay、effective window、instant upgrade path、primary/emergency path、regular path、page text、L2Beat source expression、L2Beat sentiment、operational tradeoff。 | item-6, item-7, item-8 |
| comparator_classification | 每个 comparator 的 current classification：positive non-zero/passing comparator、regular-only comparator、negative/control case；必须解释分类依据。 | item-6, item-7, item-8 |
| confidence_and_open_questions | 结论置信度、冲突来源、仍需验证的 ABI/event/page snapshot 问题。 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy | Mantle 当前合约升级权限链：multisig/governance -> TimelockController roles -> ProxyAdmin -> upgradable bridge/portal/oracle proxies，并标注可绕过 timelock 的边。 | mermaid | item-1, item-2, item-3 |
| diag-2 | timeline | Exit Window 计算示意：upgrade scheduled、timelock delay、force inclusion/withdrawal exit delay、user detection/exit deadline、upgrade execution；展示 `effective = upgradeDelay - exitDelay`。 | mermaid | item-4, item-5 |
| diag-3 | comparison | Mantle vs Arbitrum One vs OP Mainnet 的配置对比图，至少包含 upgrade delay、exit delay、effective window、primary/emergency path、regular path、L2Beat page text、source expression、comparator classification、L2Beat sentiment。 | mermaid | item-6, item-7, item-8 |
| diag-4 | flow | L2Beat 数据路径：Etherscan/RPC/ProjectDiscovery -> discovered.json/project config -> riskView helper/template override -> Mantle risk-analysis 页面。 | mermaid | item-1, item-5 |
| diag-5 | dependency | Exit Window 改善前置条件图：导入 `l2beat-risk-assessment-framework`，展示 Sequencer Failure、Proposer Failure、upgrade delay、exit delay、emergency bypass path 如何共同决定 Mantle 是否能从 None 改为 non-zero。 | mermaid | item-4, item-5, item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | verified_contracts | Mantle L1 production contracts on Etherscan, including ProxyAdmin, TimelockController, OptimismPortal / bridge / output-oracle related contracts and any owner multisig contracts needed to prove the upgrade chain. | 5 |
| src-2 | on_chain_data | Direct reads or event-derived evidence for owners, role members, `getMinDelay()`, finalization / force-inclusion parameters, executor/proposer/canceller roles, and multisig threshold where available. | 8 |
| src-3 | l2beat_source | l2beat/l2beat source permalinks for Mantle project config, ProjectDiscovery output, common `riskView.ts` Exit Window function/thresholds, relevant OP/Nitro/template logic, and comparator source expressions. Every source observation must include commit SHA and line-level permalink. | 5 |
| src-4 | l2beat_project_pages | Current L2Beat project pages or page snapshots for Mantle, Arbitrum One, OP Mainnet, and any additional comparator used to identify a current non-zero/passing example. Every page observation must include `fetched_at`, page text for Exit Window and Proposer/Sequencer prerequisite status where relevant. | 3 |
| src-5 | benchmark_primary_sources | Arbitrum One and OP Mainnet official docs, governance contracts, Etherscan contracts, L2Beat configs, or canonical governance/security council references sufficient to explain their Exit Window treatment and classify each as positive / regular-only / negative-control. If neither Arbitrum nor OP Mainnet is a current non-zero/passing comparator, identify at least one additional actual passing comparator or explicitly state all available named comparators are controls. | 6 |
| src-6 | operational_context | Sources supporting the operational impact analysis: protocol governance docs, timelock/emergency upgrade docs, incident-response documentation, or comparable L2 governance practice. | 3 |
| src-7 | methodology_context | Prior framework section `l2beat-risk-assessment-framework` final/outline as local context for L2Beat Risk Chart thresholds and Sequencer/Proposer prerequisite interpretation; include source commit/path metadata and explicitly test the gating claim that both Sequencer Failure and Proposer Failure must be green for non-zero Exit Window. Do not import Stage 1/2 thresholds as Risk Chart criteria. | 1 |
| src-8 | source_metadata_audit | A source ledger table covering every L2Beat page snapshot and L2Beat source-code observation used in calculations, with `source_url_or_ref`, `fetched_at`, commit SHA/permalink, observed value, and whether the source is page text or code/discovery data. | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-4 | Add explicit `l2beat-risk-assessment-framework` import and Sequencer/Proposer prerequisite check for non-zero Exit Window; prevent draft from implying timelock extension alone is sufficient. | Review Agent finding MAJOR, 2026-05-21 |
| 2 | modify_item | item-5 | Require Mantle red-status mapping to include prerequisite/blocking-dependency judgment while keeping Proposer Failure root-cause analysis out of scope. | Review Agent finding MAJOR, 2026-05-21 |
| 2 | modify_item | item-6, item-7 | Require comparator classification by primary/emergency vs regular paths, page text, source expression, and positive vs negative/control status. | Review Agent finding MINOR, 2026-05-21 |
| 2 | add_field | fetched_at, source_commit_metadata, prerequisite_status, comparator_classification | Require timestamp and commit metadata for page/source observations and encode prerequisite/comparator checks as structured fields. | Review Agent findings MAJOR/MINOR, 2026-05-21 |
| 2 | modify_source_req | src-3, src-4, src-5, src-7; add src-8 | Require L2Beat source commit metadata, page `fetched_at`, benchmark current-status classification, and a source metadata audit ledger. | Review Agent finding MINOR, 2026-05-21 |
| 2 | clarify_item | item-4, item-5, src-7 | Tighten the Sequencer/Proposer prerequisite wording into an explicit gating claim to verify, and require an in-scope blocking-dependency answer for Mantle. | Review Agent finding MAJOR, 2026-05-21 |
