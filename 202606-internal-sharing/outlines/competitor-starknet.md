---
topic: "StarkNet 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-starknet"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/competitor-starknet.md"
  draft: "202606-internal-sharing/research-sections/competitor-starknet/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/competitor-starknet/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  按更新后的 issue 描述重启研究：不预设重点 repo。第一步先扫描 StarkNet / Starknet
  相关 GitHub Organization，包括但不限于 `starkware-libs`、`starknet-io`、
  `keep-starknet-strange`，并通过官方链接、repo topics、README、package namespace、
  fork/network 关系和生态项目引用发现其他相关 org。对所有候选 repo 计算近 3 个月活跃度
  （PR 数量、commit 频率、contributor 活跃度等），数据驱动筛选 Top 活跃 repo。
  第二步才针对筛选出的活跃 repo 做 PR 活动分析：主要开发方向与 PR 分类、重大功能变更
  与架构调整、开发活跃度趋势变化。第三步结合 GitHub 活动和公开信息分析 Starknet
  叙事变化、生态战略调整、与 zkSync 等竞争对手的差异化定位，以及对 Mantle 的竞争启示。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、协议/客户端/证明系统工程师、
  开发者生态与战略研究同事，以及 Multica Research Squad 的 Review Agent 和后续写作者。
  读者熟悉 L2、ZK rollup、EVM、Cairo / STARK / appchain 基本概念，但需要一份
  可复核、数据驱动、能避免 cherry-pick 的 Starknet 近期开发和叙事判断。

expected_output: |
  一份中文结构化 research section，涵盖：
  - Starknet 相关 GitHub org 与 repo 全量发现方法、数据口径、活跃 repo 排名和 Top repo 筛选理由
  - 被筛选活跃 repo 的近 3 个月 PR / commit / contributor 趋势、PR 分类、代表 PR 和开发重点变化
  - 重大功能变更与架构调整：仅基于筛选后的 repo 和代表 PR 归纳，不预先假设 sequencer、Cairo 或其他 repo 必然是重点
  - 叙事方向演变：新功能/新方向发力点、生态战略调整、Appchains、proof/finality、developer tooling、games/AI、privacy/BTCFi/DeFi 等证据强弱
  - 与其他竞争对手（含 zkSync）的差异化定位
  - 对 Mantle 的竞争启示：must-monitor、borrow/prototype、avoid/not-transferable、short/mid/long-term action
  - 至少 6 张图/表：org/repo discovery funnel、活跃 repo 排名、repo x week 活跃热力图、PR 分类矩阵、叙事证据矩阵、Starknet vs zkSync 对比、Mantle 响应矩阵

source_requirements_summary: |
  Phase B 必须以 primary source 为主：GitHub org/repo metadata、PR/commit/contributor data、
  representative PR diffs、release notes、Starknet / StarkWare / Starknet Foundation 官方资料、
  Cairo / STARK / appchain / ecosystem 官方资料，以及 zkSync 官方 docs/blog/code 用于路线对比。
  时间窗口默认以当前重启日为锚点：2026-02-23 至 2026-05-23；如果 draft 抓取日发生变化，
  必须用 rolling 90 days 并写明精确起止时间。不得沿用已作废的旧 outline/draft 中
  `sequencer`、`cairo` 预设重点或其旧统计值。GitHub Search 口径必须严格区分
  `created:... is:merged` 与 `merged:...`；所有统计需记录查询语句、抓取时间、分页完整性、
  bot/archived/fork/generated 过滤规则和人工核验样本。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-23T22:39:55+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-23T22:39:55+08:00"
  restart_note: "Restarted after issue description changed from preselected repo analysis to data-driven repo discovery."

multica_issue_id: "c02c081b-e00f-4e37-9098-80cbe4b3ecbe"
branch_name: "research/202606-internal-sharing/competitor-starknet"
base_commit: "4d52e841496cccc7a4c2640ef0f96cbd6e55a637"
language: "中文"
research_depth: "standard"

prerequisite_sections:
  - slug: competitor-zksync-or-enterprise-privacy-if-present
    path: "202606-internal-sharing/research-sections/enterprise-privacy/final.md"
    status: existing-research-if-present
  - slug: competitor-base-if-present
    path: "202606-internal-sharing/research-sections/competitor-base/final.md"
    status: existing-research-if-present
  - slug: competitor-optimism-if-present
    path: "202606-internal-sharing/research-sections/competitor-optimism/final.md"
    status: existing-research-if-present
---

# Research Outline: StarkNet 近期开发与叙事分析

## Method Guardrails

1. **不预设 repo**：`starkware-libs`、`starknet-io`、`keep-starknet-strange` 是 seed org，不是结论。旧 outline/draft 中的 `starkware-libs/sequencer`、`starkware-libs/cairo` 只可作为候选 repo 被重新排名，不得直接设为重点。
2. **先发现、再排序、后分析**：Phase B 必须先完成 org/repo inventory 和活跃度 leaderboard，再决定 Top repo 深挖对象；最终正文需保留未入选 repo 的筛除理由。
3. **可复现统计口径**：所有 repo 活跃度指标必须写明 query/API、时间窗口、分页、去重、bot 过滤、archived/fork/template 规则。PR created、PR merged、PR open backlog、default-branch commit、PR branch commit 和 unique contributor 不能混用。
4. **排名需做敏感性检查**：默认使用综合活跃度分数，但需要报告权重变化后 Top list 是否稳定。若 PR 数量和 contributor 活跃度给出不同 Top list，应同时解释差异。
5. **叙事不得先行**：Appchains、proof/finality、games/AI、privacy/BTCFi、DeFi、developer tooling 等叙事只能在 GitHub 活动、官方资料或生态证据支持后进入结论；证据弱的方向必须标为 narrative signal。
6. **竞争结论必须映射 Mantle**：每个 Starknet 变化都要回答：对 Mantle 是工程威胁、开发者心智威胁、生态 GTM 威胁、叙事参考，还是不具备可迁移性。

## Research Questions

1. 2026-02-23 至 2026-05-23 期间，Starknet 相关 GitHub org 的完整候选集合是什么？除了 seed org 外，哪些 org/repo 通过官方链接、topics、README、package namespace 或生态依赖被纳入？
2. 在所有候选 repo 中，按 PR created/merged/open backlog、default-branch commit 频率、unique PR authors / commit authors、reviewer 活跃度和 release activity 排序，Top 活跃 repo 是哪些？排序对权重变化是否稳健？
3. Top 活跃 repo 是否集中在 core protocol、sequencer/node、Cairo/compiler、proof/OS、developer tooling、docs/education、appchain stack、game/Dojo、wallet/account、indexer/data、DeFi/BTCFi/privacy 等某些 cluster？
4. 被选中 repo 的近 3 个月 PR 活动中，主要开发方向和 PR 分类是什么？哪些只是 CI/docs/generated cleanup，哪些代表实质功能或架构变化？
5. 代表 PR 显示的重大功能变更是什么：性能、proof/finality、preconfirmation、appchain configurability、language/compiler capability、developer experience、ecosystem tooling 或 production hardening？
6. 活跃度趋势是否变化：哪些 repo 在近 3 个月升温、降温或出现 backlog 积累？这些变化是否与 roadmap、release、mainnet upgrade、生态 campaign 或外部叙事节点相关？
7. Starknet 近期叙事是否从单一 ZK Rollup 扩容转向更宽的 provable infra / Cairo app ecosystem / appchains / games-AI / privacy-BTCFi-DeFi？每条叙事背后的工程证据和官方证据分别多强？
8. 与 zkSync 及其他竞品相比，Starknet 的差异化定位是什么：STARK/Cairo/provable programming、app-specific stack、proof/finality、developer migration、enterprise/privacy、ecosystem GTM 各有什么取舍？
9. 对 Mantle 而言，Starknet 的近 3 个月变化在哪些维度形成竞争压力：proof/finality 叙事、开发者语言生态、appchain/L3、全链上游戏/AI、BTCFi/privacy/DeFi、企业或 payment 叙事？
10. Mantle 应该如何响应：哪些指标必须持续监控，哪些工程能力可以原型验证，哪些叙事可借鉴，哪些因 EVM/OP Stack/DA/生态差异不应照搬？

## Items

### item-1: GitHub org universe discovery and inclusion rules

建立 Starknet 相关 org/repo 的发现边界，防止只分析熟悉 repo。seed org 为 `starkware-libs`、`starknet-io`、`keep-starknet-strange`；Phase B 还必须通过官方 Starknet/StarkWare 页面、GitHub org profile、repo topics、README link graph、package namespace、fork/network 关系、生态 docs 和代表项目引用发现其他候选 org/repo。

必须覆盖：

- Seed org 全量 repo inventory：repo name、owner、description、topics、language、archived/fork/template、default branch、stars/forks、pushed_at、created_at、updated_at；
- Related org 发现规则：官方资料直接链接、repo topic 包含 `starknet`/`cairo`/`starkware`/`dojo` 等、README 明确声明 Starknet core/ecosystem role、被 seed org docs 引用、package namespace 归属；
- 排除规则：个人实验仓库、无官方/生态连接的 fork、镜像仓库、长期 archived repo、无近 3 个月活动且无战略意义 repo；
- 保留规则：即使 PR 低活跃，但若是官方 roadmap 指名或关键生态基础设施，可进入 narrative appendix，但不得挤占 Top active repo 结论；
- 输出：org/repo inventory table、发现路径、纳入/排除理由、未覆盖风险。

- **Priority**: high
- **Dependencies**: none

### item-2: Activity data pipeline, ranking formula, and Top repo selection

对所有候选 repo 计算近 3 个月活跃度，形成数据驱动 Top list。默认窗口为 2026-02-23 至 2026-05-23；若实际抓取日不同，使用抓取日前 rolling 90 days 并写明绝对日期。

默认指标：

1. **PR activity**：PR created、PR merged、PR closed-unmerged、open backlog、draft PR、merge rate、median merge latency；
2. **Commit frequency**：default branch commits、merged PR commits、weekly active days，避免把 generated/vendor update 视为实质开发；
3. **Contributor activity**：unique human PR authors、unique commit authors、reviewers/approvers、core vs drive-by contributor；
4. **Release and issue signals**：tags/releases、milestones、linked issues、major labels；
5. **Noise controls**：bot PR、renovate/dependabot、format-only、generated bindings、translation-only、CI-only、bulk docs cleanup 单独标注。

默认综合分数建议：

- `activity_score = 0.40 * normalized_pr_created + 0.20 * normalized_pr_merged + 0.20 * normalized_commit_days + 0.15 * normalized_unique_human_contributors + 0.05 * normalized_release_signal`
- 另做 sensitivity check：PR-heavy、commit-heavy、contributor-heavy 三种权重；若 Top 10 变化超过 30%，正文必须解释。
- Top repo selection 默认取 Top 8-12，并允许按 cluster 保留 1-2 个战略 repo；任何战略补入都必须与纯活跃度排名分开展示。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Active repo overview and cluster map

基于 item-2 结果输出 Starknet 近期开发重心的客观画像：Top repo 是 core infra 居多，还是 developer tooling / docs / ecosystem appchain / games / wallet / data infra 居多。该项是后续 PR 深挖的入口。

必须覆盖：

- Top repo leaderboard：rank、owner/repo、cluster、activity score、PR created/merged/open、commit days、unique contributors、main language、latest release；
- Cluster map：core protocol/node、Cairo/compiler/language、proof/OS/prover、developer tooling、docs/education、appchain stack、game/Dojo、wallet/account, indexer/data, DeFi/BTCFi/privacy, infra/ops；
- Trend signals：每周 PR created/merged、commit active days、contributor count、open backlog；
- Outlier analysis：高 PR 但低 contributor、高 commit 但低 PR、docs-heavy、bot-heavy、archived-but-important、single-maintainer burst；
- Repo selection decision：进入 Phase B 深挖的 repo、只进入 appendix 的 repo、排除的 repo及理由。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Cross-repo PR taxonomy and development direction analysis

对 Top active repo 的所有 PR 做统一分类，并针对每个 repo 输出主要开发方向。分类先用 rules/keywords 初筛，再对高信号 PR 人工核验 PR body、diff、目录、linked issue 和 release note。

建议分类：

1. **core-protocol-node**：sequencer/node、consensus、preconfirmation、mempool、batcher、RPC/gateway、state sync；
2. **execution-proof-os**：blockifier/execution、Starknet OS、prover input、resource accounting、committer、proof facts；
3. **cairo-language-compiler**：Cairo compiler、Sierra、corelib、syscall、semantic/lowering/diagnostics、Starknet classes；
4. **developer-tooling-docs**：SDK、CLI、testing framework、docs/book/tutorials、release tooling；
5. **appchain-stack**：Madara/Starknet Stack/appchain config、settlement/proving path、DA/config/fees/consensus customization；
6. **game-dojo-ecosystem**：Dojo、Katana、Torii、Cartridge、game-specific infra、indexer/session/account UX；
7. **wallet-account-aa**：account abstraction、wallet/controller/session keys、signing、transaction UX；
8. **defi-btcfi-privacy**：DeFi SDK, BTCFi, privacy, STRK20-like standards, bridge/liquidity infra；
9. **observability-infra-ci**：dashboards、alerts、deployment、CI, tests, flaky fixes, security scans；
10. **cleanup-generated-deps**：dependency bump、format/generated code、refactor without behavioral change。

每类需要输出 PR count、代表 PR、状态、代码目录、是否 production-facing、叙事含义和对 Mantle 的可迁移性。

- **Priority**: high
- **Dependencies**: item-3

### item-5: Major feature changes and architecture shifts in selected repos

从 Top active repo 中筛选真正影响架构、性能、安全、proof/finality、开发者体验或生态策略的变化。该项不能按预设模块写，而要以 item-3/4 发现的 repo cluster 为主线组织。

必须覆盖：

- 每个 selected repo 的 top 3-5 个重大变化：对应 PR、merge/open 状态、diff 目录、关联 issue/release、功能意图；
- 架构层级：interface change、protocol behavior、execution/proof pipeline、developer API、deployment/ops、docs/tutorial-only；
- 变更阶段：merged-code、open-pr、closed-unmerged、feature-flagged、test-only、release-note-only、roadmap-only；
- 跨 repo 依赖：某个功能是否同时涉及 core repo、tooling repo、docs repo、appchain repo 或 ecosystem repo；
- 风险和不确定性：PR 量大但业务影响小、open PR 未合并、roadmap 未落地、测试重构被误读为功能完成；
- Mantle 映射：通用 L2 engineering lesson、EVM-compatible 可迁移、Cairo/STARK-specific 不可迁移、需要另行验证。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: Development activity trend and organization signal

分析 Starknet 开发活跃度是否在近 3 个月发生变化，以及变化背后的组织和产品含义。该项不是简单画趋势图，而要解释周粒度峰值、低谷和 backlog 的原因。

必须覆盖：

- Weekly trend：PR created/merged、default branch commit days、unique contributors、open backlog；
- Repo-level momentum：升温 repo、降温 repo、长期高活跃 repo、短期 burst repo；
- Contributor structure：核心团队集中度、外部 contributor、reviewer bottleneck、bot/generated 噪音；
- Release/roadmap correlation：release tag、major blog、roadmap milestone、mainnet/testnet upgrade、hackathon/grant/event 与活跃度峰值的关系；
- Risk signals：open PR 积压、低 merge rate、single-maintainer risk、docs-only 活跃、high churn without release；
- Mantle relevance：哪些趋势代表真实战略投入，哪些只是维护/清理。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4

### item-7: Narrative evidence map from GitHub activity to public messaging

把 Top repo 活动与 Starknet 官方/生态叙事连接起来，判断近期叙事变化。每条叙事必须同时标注工程证据、官方叙事证据、生态证据和置信度；证据不足的方向只写为 signal。

候选叙事包括但不限于：

- **Provable high-performance infra**：proof/finality、preconfirmation、throughput、prover/OS/resource accounting；
- **Cairo / provable programming ecosystem**：语言、compiler、corelib、developer tooling、education；
- **Appchains / app-specific stack**：Starknet Stack、Madara、settlement/proof path、custom config；
- **Games / full-chain worlds / AI**：Dojo、Cartridge、games、verifiable compute、agent/ML proof；
- **Privacy / BTCFi / DeFi**：privacy roadmap、BTCFi/strkBTC/STRK20-like standards、DeFi SDK/liquidity；
- **Developer onboarding and ecosystem infra**：docs, SDK, wallet/account, indexer/data, tutorials。

输出一张 narrative evidence matrix：叙事、GitHub repo/PR evidence、官方资料、生态项目证据、状态、置信度、商业含义。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-6

### item-8: Deep dives for discovered strategic clusters

根据 item-3 的 cluster map 选择 3-5 个战略 cluster 做深入分析。默认不固定 cluster；如果数据发现 core infra、Cairo/compiler、appchain/games 或 developer tooling 最活跃，则按实际排序展开。

每个 cluster 必须回答：

- 该 cluster 包含哪些 selected repo，活跃度和趋势如何；
- 关键 PR / release / docs 说明了什么开发重点；
- 是否有跨 repo 架构变化；
- 对 Starknet 叙事的支撑强度；
- 与 zkSync / OP Stack / Arbitrum Orbit / Base / Sui / Tempo 等竞品相比的差异；
- 对 Mantle 的威胁等级和可迁移性。

若某个外界常见叙事（例如 games/AI 或 BTCFi/privacy）没有进入 Top active repo，仍需在 narrative section 中解释：这是低活跃/高叙事，还是证据不足。

- **Priority**: medium
- **Dependencies**: item-3, item-4, item-5, item-7

### item-9: Starknet vs zkSync and other competitor positioning

专门处理 Starknet 与 zkSync 的 ZK 路线差异，并在必要时补充 OP Stack、Arbitrum Orbit、Base、Sui、Tempo 等竞品作为定位参照。比较必须连接到 item-3/7 的数据发现，而不是泛泛比较。

必须覆盖：

- Execution model：Cairo/STARK/provable programs vs EVM/Solidity compatibility；
- Proof system and finality：STARK transparency、prover stack、proof reproducibility、latency/finality claims vs zkSync Boojum/Airbender/Gateway 等官方路线；
- Appchain route：Starknet Appchains / Madara / app-specific compute vs ZK Stack / Hyperchains / Prividium / OP Stack L3 / Orbit；
- Developer and ecosystem GTM：学习成本、tooling、docs、wallet/account UX、游戏/AI/appchain developer mindshare；
- Enterprise/privacy/payment positioning：Starknet privacy/BTCFi/DeFi signals vs zkSync enterprise/privacy and Mantle payment/enterprise directions；
- Security/governance caveats：L2Beat stage, upgradeability, escape hatch, security council, prover reproducibility；
- 对 Mantle 的映射：Mantle 若强调 EVM-compatible high-throughput settlement、EigenDA、MNT liquidity、payment/enterprise 或 ZK overlay，应如何差异化表达。

- **Priority**: high
- **Dependencies**: item-7, item-8

### item-10: Mantle competitive implications and action plan

将数据驱动发现和叙事分析转化为 Mantle 可执行判断。结论必须按证据强度、工程可行性、产品价值、叙事价值和组织成本分层。

必须输出四类建议：

1. **Must monitor now**：
   - Top active Starknet repo 的 weekly PR/commit/contributor leaderboard；
   - proof/finality/preconfirmation 公开指标与 roadmap 兑现情况；
   - appchain/games/AI/BTCFi/privacy 叙事是否出现从 marketing 到 code/release/on-chain 的跃迁；
   - zkSync 与 Starknet 两条 ZK 路线对 Mantle ZK overlay / enterprise / payment 叙事的挤压。
2. **Borrow or prototype**：
   - 可迁移的 observability、proof/finality dashboard、sequencer/preconfirmation UX、appchain template、developer tooling、ecosystem demo；
   - 针对 Mantle 的 EVM/OP Stack/EigenDA 约束设计原型，不直接复制 Cairo/STARK 特定实现。
3. **Avoid or do not overfit**：
   - Cairo 专用语言生态、Starknet OS、SHARP/Stwo 路线若与 Mantle 架构不兼容，不应写成短期路线；
   - games/AI/privacy/BTCFi 若仅有叙事没有活跃 repo 和用户指标，不应成为 Mantle 主叙事；
   - 单个高活跃 repo 不能外推为整个生态增长。
4. **Short/mid/long-term plan**：
   - 短期：建立 Starknet repo watchlist、ZK competitor dashboard、PR taxonomy 更新机制；
   - 中期：验证 Mantle preconfirmation/proof acceleration/appchain/payment or game demo；
   - 长期：形成 Mantle 自身差异化：EVM-compatible performance, Ethereum-aligned settlement, EigenDA/data availability, MNT liquidity, enterprise/payment distribution。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7, item-8, item-9

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| evidence_window | 起止日期、抓取时间、时区、rolling 90 days 规则、是否与 2026-02-23..2026-05-23 一致 | all |
| discovery_source | org/repo 被发现的来源：seed org、official link、topic、README link、package namespace、dependency/reference、manual review | item-1 |
| repo_inventory_metadata | owner/repo、description、topics、language、archived/fork/template、default branch、stars/forks、pushed_at、created_at、latest release | item-1, item-3 |
| inclusion_decision | include-top、include-strategic-appendix、exclude-fork、exclude-archived、exclude-inactive、exclude-unrelated，并说明理由 | item-1, item-3 |
| activity_metrics | PR created/merged/closed/open、merge rate、median merge latency、commit active days、unique PR authors、unique commit authors、reviewers、release signal | item-2, item-3, item-6 |
| activity_score | 综合分数、各指标标准化值、权重、排名、sensitivity check 结果 | item-2, item-3 |
| noise_filter | bot、generated、format-only、dependency bump、CI-only、docs-only、translation-only、bulk cleanup 的识别和保留/降权规则 | item-2, item-4 |
| repo_cluster | core-protocol-node、execution-proof-os、cairo-language-compiler、developer-tooling-docs、appchain-stack、game-dojo-ecosystem、wallet-account-aa、defi-btcfi-privacy、observability-infra-ci、other | item-3, item-8 |
| pr_metadata | PR 号、标题、状态、创建/合并/关闭时间、作者、review 周期、标签、改动行数、主要目录、关联 issue/release | item-4, item-5 |
| pr_category | 统一 PR 分类及二级分类，含自动分类规则和人工核验结果 | item-4 |
| representative_pr_evidence | 代表 PR 的 body/diff/目录/linked issue/release note 摘要，标注是否实质功能变更 | item-4, item-5 |
| implementation_status | merged-code、open-pr、closed-unmerged、feature-flagged、test-only、docs-only、release-note-only、roadmap-only、mainnet/testnet/devnet/unknown | item-5, item-7, item-8 |
| architectural_change | interface/protocol/execution/proof/developer API/deployment/docs 层级的影响，是否跨 repo | item-5, item-8 |
| activity_trend | weekly trend、momentum direction、backlog、contributor concentration、release/roadmap correlation | item-6 |
| narrative_signal | 叙事类型、GitHub 证据、官方证据、生态证据、证据置信度、商业含义 | item-7 |
| competitor_comparison | 与 zkSync/OP Stack/Arbitrum Orbit/Base/Sui/Tempo 的差异维度、source、证据强度 | item-9 |
| mantle_competitive_impact | 对 Mantle 的威胁等级、可迁移性、工程成本、产品价值、叙事价值、建议行动 | item-10 |
| evidence_type | merged-code、open-pr、github-metadata、official-doc、official-blog、release-note、onchain-data、industry-commentary、internal-research、inferred | all |
| evidence_confidence | high/medium/low，并说明不确定性来源；roadmap/open PR/二手报道默认不得标 high | all |
| caveats_open_questions | 事实缺口、口径争议、未覆盖 repo、API rate-limit、query limitation、不可外推边界、需 Mantle 工程团队复核点 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | funnel | GitHub discovery funnel：seed org -> related org discovery -> repo inventory -> filters -> ranked candidate repos -> selected Top repos / strategic appendix | mermaid or markdown table | item-1, item-2, item-3 |
| diag-2 | leaderboard | 活跃 repo 排名表：rank、owner/repo、cluster、activity score、PR/commit/contributor/release metrics、selection decision | markdown table | item-2, item-3 |
| diag-3 | heatmap | Repo x week 活跃热力图：PR created/merged、commit active days、unique contributors，可拆为两张表 | markdown table | item-3, item-6 |
| diag-4 | matrix | PR 分类矩阵：repo x category x PR count x representative PR x implementation status x narrative meaning x Mantle impact | markdown table | item-4, item-5 |
| diag-5 | architecture | 如果 Top repo 显示 core/proof/appchain cluster 活跃，则绘制 discovered architecture map，展示跨 repo 组件与变更位置；若未发现，则说明不适用 | mermaid | item-5, item-8 |
| diag-6 | timeline | Starknet 叙事演变时间线：GitHub activity peaks + official posts/releases/events + ecosystem signals，标注证据强弱 | mermaid or markdown table | item-6, item-7 |
| diag-7 | comparison | Starknet vs zkSync / other competitors 路线对比矩阵：language/VM、proof/finality、appchain、developer tooling、enterprise/privacy/payment、GTM | markdown table | item-9 |
| diag-8 | matrix | Mantle 竞争响应矩阵：Starknet signal x evidence strength x threat level x transferability x recommended action x time horizon | markdown table | item-10 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | github_org_inventory | Seed org 和 related org 的 repo inventory。必须覆盖 `starkware-libs`、`starknet-io`、`keep-starknet-strange` 全量 repo，并记录发现的其他相关 org/repo | all seed repos |
| src-2 | github_activity_metrics | 所有候选 repo 的 PR/commit/contributor/release metrics，含查询语句、抓取时间、分页、rate limit、bot/noise 过滤 | all candidate repos |
| src-3 | github_pr_data | Selected Top repo 的近 3 个月 PR 原始数据，含 PR 号、标题、状态、时间、作者、标签、目录、关联 issue/release | all selected repos |
| src-4 | github_code_analysis | 对 selected repo 代表 PR 的 diff 或合并后代码进行文件级验证，覆盖每个 selected repo 的高信号类别 | >= 25 representative PRs total |
| src-5 | official_starknet_sources | Starknet / StarkWare / Starknet Foundation 官方 blog、docs、technical roadmap、release notes、ecosystem pages | >= 10 |
| src-6 | official_repo_release_sources | Selected repo 的 release notes、tags、milestones、CHANGELOG、README/docs，用于连接 PR 活动和产品状态 | >= selected repo count |
| src-7 | cairo_and_proof_sources | Cairo、Sierra、Starknet OS、Stwo/Stone/SHARP/prover/finality 相关官方资料；仅在数据发现相关 cluster 时深挖，否则作为叙事核验 | >= 5 |
| src-8 | appchain_ecosystem_sources | Starknet Stack、Madara、Dojo、Cartridge、Paradex 或数据发现出的 appchain/game/tooling 项目的官方资料或 repo | >= 5 if relevant |
| src-9 | zksync_comparison_sources | zkSync 官方 docs、ZK Stack、Gateway、Boojum、Airbender、Prividium、release/blog/code，用于路线对比 | >= 6 |
| src-10 | onchain_or_metrics_data | Starknet 主网和生态指标：TPS、fees、finality/proof latency、TVL、active addresses、app/game usage、BTCFi/DeFi 数据；可用官方 dashboards、L2Beat、DeFiLlama、explorers | >= 4 |
| src-11 | internal_research | 仓库内已有竞品、enterprise/privacy、L2 stage、安全或 Mantle 相关研究，用于对比和复用已核验证据 | >= 3 |
| src-12 | industry_commentary | 高可信行业文章、团队访谈、工程博客或社区讨论；只能辅助叙事判断，关键事实必须用 primary source 交叉验证 | >= 3 |
| src-13 | mantle_sources | Mantle docs、代码、公开路线、内部研究或链上数据，用于竞争启示和可迁移性判断 | >= 3 |

## Data Collection Plan for Phase B

1. Use GitHub REST or GraphQL to list org repos:
   - `GET /orgs/{org}/repos?per_page=100&type=all`
   - record `archived`, `fork`, `is_template`, `default_branch`, `topics`, `pushed_at`, `updated_at`.
2. Discover related orgs/repo:
   - Search official Starknet/StarkWare pages and selected repo README/docs for GitHub links.
   - Search GitHub topics and code/repo search for `starknet`, `cairo`, `dojo`, `madara`, then include only if official/ecosystem linkage is documented.
3. For each candidate repo, collect:
   - PR created in window: `repo:{owner}/{repo} is:pr created:{start}..{end}`
   - PR merged in window: `repo:{owner}/{repo} is:pr merged:{start}..{end}`
   - PR open backlog at end: `repo:{owner}/{repo} is:pr is:open created:<={end}`
   - default branch commits via GraphQL history `since`/`until`; record if API limitations require approximation.
   - unique human contributors from PR authors + commit authors after bot filtering.
4. Normalize and rank:
   - Compute default score and three sensitivity scores.
   - Produce leaderboard and Top repo shortlist before any qualitative deep dive.
5. Classify PRs:
   - Rule-based first pass from title/body/labels/directories.
   - Manual verification for all high-impact or high-score PRs.
   - Separate docs/CI/generated/dependency noise from functionality.
6. Build narrative and competitor analysis only after repo discovery and PR classification are complete.

## Quality Checklist for Deep Draft

- [ ] The draft starts with org/repo discovery and active repo ranking, not preselected repo analysis.
- [ ] `starkware-libs`, `starknet-io`, and `keep-starknet-strange` are fully scanned, and any additional orgs are included or explicitly rejected with reasons.
- [ ] Top active repo selection is reproducible: exact queries/API, date window, pagination, filters, ranking formula, and sensitivity check are documented.
- [ ] Old `sequencer`/`cairo` assumptions and old counts are not reused without fresh data collection.
- [ ] PR created, PR merged, PR open backlog, commit frequency, contributor count, and release signal are kept as separate metrics before scoring.
- [ ] Bot/generated/docs/CI/dependency noise is identified and either excluded, down-weighted, or reported separately.
- [ ] Selected repo PR categories include representative PRs with manual diff/body verification.
- [ ] Major architecture/feature claims are tied to merged code, open PR, release note, official roadmap, or official docs with confidence labels.
- [ ] Narratives such as Appchains, proof/finality, games/AI, privacy/BTCFi/DeFi are downgraded if GitHub or official evidence is weak.
- [ ] Starknet vs zkSync comparison uses current official sources and avoids generic "STARK vs SNARK" simplification.
- [ ] Mantle recommendations are split into must-monitor, borrow/prototype, avoid/not-transferable, and short/mid/long-term actions.
- [ ] All time-sensitive facts include access date or crawl date, and all unresolved facts are preserved as caveats.

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | restart-rewrite | `202606-internal-sharing/outlines/competitor-starknet.md` | User updated issue: research must discover active Starknet repos data-first across orgs instead of preselecting `sequencer` and `cairo` | Multica comment `4c4961ea-74dd-4813-bd54-5987f09b0704` |
