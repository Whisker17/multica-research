---
topic: "Arbitrum 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-arbitrum"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/competitor-arbitrum.md"
  draft: "202606-internal-sharing/research-sections/competitor-arbitrum/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/competitor-arbitrum/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  按更新后的 issue 描述重启研究：不预设重点 repo。第一步先扫描 Arbitrum 相关 GitHub
  Organization，包括但不限于 `OffchainLabs`、`ArbitrumFoundation`，并通过官方 docs/blog、
  GitHub org profile、repo topics、README link graph、package namespace、fork/network 关系、
  release notes、DAO / ecosystem materials 发现其他相关 org/repo。对所有候选 repo 计算
  近 3 个月活跃度（固定窗口：2026-02-24 至实际抓取时点；若 draft 抓取日晚于本 outline，
  使用 2026-02-24..crawl_time 并记录绝对时间），按 PR 数量、commit 频率、contributor 活跃度、
  release/tag、issue/milestone 等指标数据驱动排序，筛选 Top 活跃 repo 作为分析对象。
  第二步针对筛选出的活跃 repo 进行 PR 活动分析：主要开发方向与 PR 分类、重大功能变更与架构调整、
  开发活跃度趋势变化。第三步结合 GitHub 活动和公开信息分析 Arbitrum 近期叙事变化：新功能和
  新方向发力点、生态战略调整、与 Optimism/Base、zkSync、Starknet、Mantle 等竞争对手的差异化定位，
  以及对 Mantle 的竞争启示。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、协议/客户端/基础设施工程师、
  生态与战略研究同事，以及 Multica Research Squad 的 Review Agent 和后续写作者。
  读者熟悉 L2、Optimistic Rollup、Arbitrum Nitro、Orbit、Stylus、fraud proof、MEV / sequencing
  和 appchain/L3 基本概念，但需要一份可复核、数据驱动、避免 cherry-pick 的 Arbitrum 近期开发和
  叙事判断。

expected_output: |
  一份中文结构化 research section，涵盖：
  - Arbitrum 相关 GitHub org/repo 的全量发现方法、近 3 个月活跃度数据集、排序公式、Top 活跃 repo
    概况和筛选理由；
  - Top 活跃 repo 的 PR / commit / contributor 趋势、PR 分类、代表 PR、主要开发重点变化和重大
    功能/架构调整；
  - 叙事方向演变：Stylus/WASM、Orbit/appchain/L3、Timeboost/MEV、BoLD/permissionless validation、
    Nitro reliability、developer tooling、DAO/ecosystem strategy 等方向的证据强弱；
  - 与 Optimism/Base、zkSync、Starknet、Mantle 的竞争格局对比；
  - 对 Mantle 的竞争启示：must-monitor、borrow/prototype、avoid/not-transferable、short/mid/long-term action；
  - 至少 6 张图/表：org/repo discovery funnel、活跃 repo 排名、repo x week 活跃热力图、PR 分类矩阵、
    叙事证据矩阵、竞品定位矩阵、Mantle 响应矩阵。

source_requirements_summary: |
  Phase B 必须以 primary source 为主：GitHub org/repo metadata、PR/commit/contributor data、
  representative PR body/diff/release links、Offchain Labs / Arbitrum Foundation 官方 docs/blog/release notes、
  Arbitrum DAO governance/forum/proposals、Orbit/Stylus/Timeboost/BoLD 官方资料和链上/生态指标。
  不得复用已作废旧 artifact 中预设 `OffchainLabs/nitro`、`OffchainLabs/stylus-sdk-rs` 的重点 repo 结论
  或旧统计值；这两个 repo 只能作为全量候选 repo 参与重新排序。GitHub Search 口径必须严格区分
  `created:...`、`merged:...`、默认分支 commit、PR branch commit 和 open backlog；所有统计需记录查询语句、
  抓取时间、分页完整性、rate-limit caveat、bot/archived/fork/generated 过滤规则和人工核验样本。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-24T00:10:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-24T00:10:00+08:00"
  restart_note: "Restarted after user updated issue: research must discover active Arbitrum repos data-first across orgs instead of preselecting Nitro/Stylus repos."

multica_issue_id: "764c2f01-8fd0-4620-bf51-3c6a8397bf46"
branch_name: "research/202606-internal-sharing/competitor-arbitrum"
base_commit: "194f6bd37f5729000de2e87181dff7926ea14729"
language: "中文"
research_depth: "standard"

prerequisite_sections:
  - slug: competitor-optimism
    path: "202606-internal-sharing/research-sections/competitor-optimism/final.md"
    status: existing-research-if-present-on-main
  - slug: competitor-base
    path: "202606-internal-sharing/research-sections/competitor-base/final.md"
    status: existing-research-if-present-on-main
  - slug: competitor-starknet
    path: "202606-internal-sharing/research-sections/competitor-starknet/final.md"
    status: existing-research-if-present-on-main
  - slug: stage1-case-studies
    path: "mantle-stage1-rollup/research-sections/stage1-case-studies/final.md"
    status: existing-research
  - slug: upgrade-exitwindow-securitycouncil
    path: "mantle-stage1-rollup/research-sections/upgrade-exitwindow-securitycouncil/final.md"
    status: existing-research
  - slug: mantle-impact-assessment
    path: "base-azul-upgrade/research-sections/mantle-impact-assessment/final.md"
    status: existing-research
  - slug: architecture-advantage-summary
    path: "mantle-base-codebase-evaluation/research-sections/architecture-advantage-summary/final.md"
    status: existing-research
---

# Research Outline: Arbitrum 近期开发与叙事分析

## Method Guardrails

1. **不预设 repo**：`OffchainLabs` 和 `ArbitrumFoundation` 是 seed org，不是结论。旧 artifact 中的 `OffchainLabs/nitro`、`OffchainLabs/stylus-sdk-rs` 只可作为候选 repo 被重新排名，不得直接设为重点。
2. **先发现、再排序、后分析**：Phase B 必须先完成 org/repo inventory 和活跃度 leaderboard，再决定 Top repo 深挖对象；最终正文需保留未入选 repo 的筛除理由。
3. **固定窗口与可复现口径**：窗口使用 2026-02-24 至实际抓取时点；若 deep draft 抓取日变化，必须写明精确起止时间、时区、API 查询、分页、去重、bot/archived/fork/generated 规则。
4. **排名需做敏感性检查**：默认使用综合活跃度分数，同时报告 PR-heavy、commit-heavy、contributor-heavy 三种权重下 Top list 是否稳定。若 Top 10 变化超过 30%，正文必须解释。
5. **类别不得反向决定 repo**：Stylus、Orbit、Timeboost、BoLD、Nitro reliability 等只能作为 PR/叙事分类候选；只有当数据发现相关 repo/PR 活跃，才进入重点结论。
6. **叙事必须有证据分层**：每条叙事至少标注 GitHub/code evidence、official/governance evidence、ecosystem/onchain evidence 和 confidence；证据弱的方向只能写为 signal 或 inference。
7. **Mantle 结论必须可执行**：每个 Arbitrum 变化都要回答：对 Mantle 是工程威胁、开发者心智威胁、生态/GTM 威胁、叙事参考，还是不可迁移。

## Research Questions

1. 2026-02-24 至抓取时点，Arbitrum 相关 GitHub org 的完整候选集合是什么？除了 `OffchainLabs`、`ArbitrumFoundation` 外，哪些 org/repo 通过官方链接、topics、README、package namespace、release 或生态依赖被纳入？
2. 在所有候选 repo 中，按 PR created/merged/open backlog、default-branch commit 频率、unique PR authors / commit authors、reviewer 活跃度和 release/tag 排序，Top 活跃 repo 是哪些？排序对权重变化是否稳健？
3. Top 活跃 repo 是否集中在 core protocol/node、Stylus/WASM SDK、Orbit/appchain tooling、governance/foundation、docs/devrel、contracts/bridge、data/indexer、ops/release 等 cluster？
4. 被选中 repo 的近 3 个月 PR 活动中，主要开发方向和 PR 分类是什么？哪些只是 CI/docs/generated/dependency cleanup，哪些代表实质功能或架构变化？
5. 代表 PR 显示的重大功能变更是什么：fraud proof/BoLD、Timeboost/sequencing、Stylus/WASM、Orbit/appchain、Nitro node reliability、developer tooling、governance/contracts 或 ecosystem infra？
6. 活跃度趋势是否变化：哪些 repo 在近 3 个月升温、降温或出现 backlog 积累？这些变化是否与 release、governance vote、mainnet/testnet deployment、grant/campaign 或官方叙事节点相关？
7. Arbitrum 近期叙事是否从"领先 optimistic rollup / Nitro"扩展为"multi-VM Stylus + Orbit appchain/L3 + MEV/time auction + permissionless fraud proof + DAO/ecosystem growth"组合？每条叙事背后的工程证据和官方证据分别多强？
8. 与 Optimism/Base、zkSync、Starknet、Mantle 相比，Arbitrum 的差异化定位是什么：customizable Orbit、Stylus WASM、BoLD safety、Timeboost MEV、DAO/governance、ecosystem distribution 各有什么取舍？
9. 对 Mantle 而言，Arbitrum 的近 3 个月变化在哪些维度形成竞争压力：security/stage、MEV/sequencing、appchain/L3、multi-VM developer mindshare、ecosystem growth、enterprise/payment/app-specific chain？
10. Mantle 应该如何响应：哪些指标必须持续监控，哪些工程能力可以原型验证，哪些叙事可借鉴，哪些因架构/治理/生态差异不应照搬？

## Items

### item-1: GitHub org universe discovery and inclusion rules

建立 Arbitrum 相关 org/repo 的发现边界，防止只分析熟悉 repo。seed org 为 `OffchainLabs` 和 `ArbitrumFoundation`；Phase B 还必须通过 Arbitrum / Offchain Labs 官方页面、GitHub org profile、repo topics、README link graph、package namespace、fork/network 关系、ecosystem docs、DAO proposal、release notes 和代表项目引用发现其他候选 org/repo。

必须覆盖：

- Seed org 全量 repo inventory：owner/repo、description、topics、language、archived/fork/template、default branch、stars/forks、pushed_at、created_at、updated_at、latest release/tag；
- Related org 发现规则：官方资料直接链接、repo topic 包含 `arbitrum`/`nitro`/`stylus`/`orbit`/`timeboost` 等、README 明确声明 Arbitrum core/ecosystem role、被官方 docs 或 selected repo 引用、package namespace 归属；
- 排除规则：个人实验仓库、无官方/生态连接的 fork、镜像仓库、长期 archived repo、无近 3 个月活动且无战略意义 repo；
- 保留规则：即使 PR 低活跃，但若是官方 roadmap 指名或关键生态基础设施，可进入 narrative appendix，但不得挤占 Top active repo 结论；
- 输出：org/repo inventory table、发现路径、纳入/排除理由、未覆盖风险。

- **Priority**: high
- **Dependencies**: none

### item-2: Activity data pipeline, ranking formula, and Top repo selection

对所有候选 repo 计算近 3 个月活跃度，形成数据驱动 Top list。窗口固定为 2026-02-24 至实际抓取时点；如果 draft 抓取日不是 2026-05-24，仍以 dispatch 指定的 2026-02-24 起点为准并写明结束时间。

默认指标：

1. **PR activity**：PR created、PR merged、PR closed-unmerged、open backlog、draft PR、merge rate、median merge latency；
2. **Commit frequency**：default branch commits、merged PR commits、weekly active days，避免把 generated/vendor update 视为实质开发；
3. **Contributor activity**：unique human PR authors、unique commit authors、reviewers/approvers、core vs drive-by contributor；
4. **Release and issue signals**：tags/releases、milestones、linked issues、major labels；
5. **Noise controls**：bot PR、renovate/dependabot、format-only、generated bindings、translation-only、CI-only、bulk docs cleanup 单独标注。

默认综合分数建议：

- `activity_score = 0.40 * normalized_pr_created + 0.20 * normalized_pr_merged + 0.20 * normalized_commit_active_days + 0.15 * normalized_unique_human_contributors + 0.05 * normalized_release_signal`
- 另做 sensitivity check：PR-heavy、commit-heavy、contributor-heavy 三种权重；若 Top 10 变化超过 30%，正文必须解释。
- Top repo selection 默认取 Top 8-12，并允许按 cluster 保留 1-2 个战略 repo；任何战略补入都必须与纯活跃度排名分开展示。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Active repo overview and cluster map

基于 item-2 结果输出 Arbitrum 近期开发重心的客观画像：Top repo 是 core protocol 居多，还是 Stylus SDK、Orbit tooling、foundation/governance、docs/devrel、contracts/bridge、ops/release、ecosystem infra 居多。该项是后续 PR 深挖的入口。

必须覆盖：

- Top repo leaderboard：rank、owner/repo、cluster、activity score、PR created/merged/open、commit active days、unique contributors、main language、latest release；
- Cluster map：core-protocol-node、stylus-wasm-sdk、orbit-appchain-tooling、timeboost-sequencing-mev、bold-fraud-proof-validation、contracts-bridge-governance、foundation-ecosystem-devrel、docs-education、infra-ops-release、data-indexer-analytics、other；
- Trend signals：每周 PR created/merged、commit active days、contributor count、open backlog；
- Outlier analysis：高 PR 但低 contributor、高 commit 但低 PR、docs-heavy、bot-heavy、archived-but-important、single-maintainer burst；
- Repo selection decision：进入 Phase B 深挖的 repo、只进入 appendix 的 repo、排除的 repo 及理由。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Cross-repo PR taxonomy and development direction analysis

对 Top active repo 的所有 PR 做统一分类，并针对每个 repo 输出主要开发方向。分类先用 rules/keywords/path 初筛，再对高信号 PR 人工核验 PR body、diff、目录、linked issue、release note 和 review discussion。

建议分类：

1. **core-protocol-node**：Nitro node、sequencer、batch poster、validator、delayed inbox、feed、database/snapshot/pruning/sync；
2. **bold-fraud-proof-validation**：BoLD、challenge manager、assertion/edge/bisection、validator tooling、permissionless validation、watchtower/monitoring；
3. **timeboost-sequencing-mev**：express lane、auction/bidding、ordering rights、sequencer integration、fallback path、contracts/config；
4. **stylus-wasm-dx**：Stylus SDK、Rust/WASM ABI、storage/calls/events、host I/O、gas/metering、testing/examples/docs；
5. **orbit-appchain-anytrust**：Orbit chain config、AnyTrust / DAC、custom gas token、deployment tooling、bridge/inbox/outbox、validator/node ops；
6. **contracts-bridge-governance**：rollup contracts、bridge, governance parameters, DAO/security council hooks, deployments/upgrades；
7. **developer-tooling-docs**：CLI、SDK、examples、docs/tutorials、release notes、devrel assets；
8. **foundation-ecosystem**：grant/ecosystem repo、foundation website/content, ecosystem listing, campaigns, partner integration;
9. **observability-infra-ci-release**：dashboards、alerts、deployment、CI, tests, flaky fixes, security scans, release automation；
10. **cleanup-generated-deps**：dependency bump、format/generated code、refactor without behavioral change。

每类需要输出 PR count、代表 PR、状态、代码目录、是否 production-facing、叙事含义和对 Mantle 的可迁移性。

- **Priority**: high
- **Dependencies**: item-3

### item-5: Major feature changes and architecture shifts in selected repos

从 Top active repo 中筛选真正影响架构、性能、安全、sequencing、developer experience 或生态策略的变化。该项不能按预设 Nitro/Stylus/Orbit 写，而要以 item-3/4 发现的 repo cluster 和代表 PR 为主线组织。

必须覆盖：

- 每个 selected repo 的 top 3-5 个重大变化：对应 PR、merge/open 状态、diff 目录、关联 issue/release、功能意图；
- 架构层级：interface change、protocol behavior、sequencing/MEV、fraud proof/validation、WASM/developer API、appchain deployment、governance/ops、docs/tutorial-only；
- 变更阶段：merged-code、open-pr、closed-unmerged、feature-flagged、test-only、docs-only、release-note-only、roadmap-only、testnet/mainnet/unknown；
- 跨 repo 依赖：某个功能是否同时涉及 core repo、contracts repo、tooling repo、docs repo、foundation/ecosystem repo；
- 风险和不确定性：PR 量大但业务影响小、open PR 未合并、roadmap 未落地、测试重构被误读为功能完成；
- Mantle 映射：通用 L2 engineering lesson、OP Stack/EVM 可迁移、Arbitrum Nitro/AVM/Stylus-specific 不可迁移、需要另行验证。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: Development activity trend and engineering organization signal

分析 Arbitrum 开发活跃度是否在近 3 个月发生变化，以及变化背后的组织和产品含义。该项不是简单画趋势图，而要解释周粒度峰值、低谷、open backlog、review bottleneck 和 release/治理事件之间的关系。

必须覆盖：

- Weekly trend：PR created/merged、default branch commit days、unique contributors、open backlog；
- Repo-level momentum：升温 repo、降温 repo、长期高活跃 repo、短期 burst repo；
- Contributor structure：Offchain Labs core、Arbitrum Foundation、外部 contributor、bot/dependabot、ecosystem contributors 的比例；
- Release/roadmap correlation：release tag、major blog、governance proposal、mainnet/testnet activation、grant/campaign/event 与活跃度峰值的关系；
- Risk signals：open PR 积压、低 merge rate、single-maintainer risk、docs-only 活跃、high churn without release；
- Mantle relevance：哪些趋势代表真实战略投入，哪些只是维护/清理。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4

### item-7: Narrative evidence map from GitHub activity to public messaging

把 Top repo 活动与 Arbitrum 官方/生态叙事连接起来，判断近期叙事变化。每条叙事必须同时标注工程证据、官方/治理叙事证据、生态/链上证据和置信度；证据不足的方向只写为 signal。

候选叙事包括但不限于：

- **Stylus / multi-VM developer reach**：Rust/C/C++/WASM smart contracts、EVM interoperability、high-performance contracts、SDK/tooling maturity；
- **Orbit / appchain / L3 expansion**：custom gas token、AnyTrust、app-specific chains、enterprise/game/social/custom settlement、ecosystem growth；
- **Timeboost / MEV and ordering market**：auctioned ordering rights、express lane、sequencer revenue、fairness/latency caveats、appchain configurable ordering；
- **BoLD / permissionless validation / Stage security**：fraud proof maturity、validator permissionlessness、L2Beat stage implications、security council/exit window caveats；
- **Nitro reliability and rollup operations**：node performance/reliability、batcher/sequencer/validator ops、release hardening；
- **DAO/foundation/ecosystem strategy**：grants、partnerships、foundation programs、governance proposals、developer growth。

输出一张 narrative evidence matrix：叙事、GitHub repo/PR evidence、官方/治理资料、生态/链上证据、状态、置信度、商业含义。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-6

### item-8: Deep dives for discovered strategic clusters

根据 item-3 的 cluster map 选择 3-5 个战略 cluster 做深入分析。默认不固定 cluster；如果数据发现 core protocol、Stylus、Orbit、Timeboost、BoLD、foundation/ecosystem 或 docs/devrel 最活跃，则按实际排序展开。

每个 cluster 必须回答：

- 该 cluster 包含哪些 selected repo，活跃度和趋势如何；
- 关键 PR / release / docs / governance 说明了什么开发重点；
- 是否有跨 repo 架构变化；
- 对 Arbitrum 叙事的支撑强度；
- 与 Optimism/Base、zkSync、Starknet、Mantle 等竞品相比的差异；
- 对 Mantle 的威胁等级和可迁移性。

若某个外界常见叙事（例如 Orbit、Stylus、Timeboost 或 BoLD）没有进入 Top active repo，仍需在 narrative section 中解释：这是低活跃/高叙事、已进入维护期、证据不足，还是相关代码在别处发生。

- **Priority**: medium
- **Dependencies**: item-3, item-4, item-5, item-7

### item-9: Competitor positioning: Arbitrum vs Optimism/Base, zkSync, Starknet, and Mantle

建立横向竞争框架，解释 Arbitrum 在技术路线、治理、生态、MEV、developer mindshare 和 appchain strategy 上的差异。比较必须连接到 item-3/7 的数据发现，而不是泛泛比较。

必须覆盖：

- **Technology stack**：Nitro/AVM/Stylus vs OP Stack/Superchain/Base Stack vs zkSync ZK Stack vs Starknet Cairo/STARK vs Mantle OP-derived/EigenDA stack；
- **Ecosystem expansion**：Orbit L2/L3/AnyTrust/custom gas token vs Superchain standardization/interop vs Base Coinbase distribution vs zkSync Hyperchains/Prividium vs Starknet appchain/Cairo ecosystem；
- **MEV/latency/ordering**：Timeboost vs Flashblocks/preconfirmation/Base performance claims vs zkSync/Starknet finality/proof routes vs Mantle sequencer roadmap；
- **Security and decentralization**：BoLD/Arbitrum DAO/Security Council/L2Beat stage vs OP Cannon/Superchain governance vs Base nested governance vs zk rollup prover trust vs Mantle Stage 1 roadmap；
- **Developer mindshare**：Stylus WASM vs Solidity/EVM/OP Stack compatibility vs Cairo vs ZK Stack tooling；
- **Transferability to Mantle**：directly borrowable、prototype-needed、narrative-only、not transferable、avoid。

- **Priority**: high
- **Dependencies**: item-7, item-8

### item-10: Mantle competitive implications and action plan

将数据驱动发现和叙事分析转化为 Mantle 可执行判断。结论必须按证据强度、工程可行性、产品价值、叙事价值、治理风险和组织成本分层。

必须输出四类建议：

1. **Must monitor now**：
   - Top active Arbitrum repo 的 weekly PR/commit/contributor leaderboard；
   - BoLD / Stage 1 / permissionless validation 的真实运行和 L2Beat 风险口径；
   - Timeboost / ordering auction 对 sequencer revenue、MEV-sharing、appchain business model 的影响；
   - Orbit/appchain 与 Stylus/WASM 是否出现从 docs/marketing 到 code/release/onchain adoption 的跃迁。
2. **Borrow or prototype**：
   - 可迁移的 observability、validator/proof monitoring、sequencer/MEV dashboard、appchain template、developer tooling、ecosystem demo；
   - 针对 Mantle 的 EVM/OP Stack/EigenDA/MNT 约束设计原型，不直接复制 Nitro/Stylus 特定实现。
3. **Avoid or do not overfit**：
   - Stylus/WASM、Orbit/AnyTrust、Timeboost 若依赖 Arbitrum-specific architecture 或 DAO economics，不应写成 Mantle 短期路线；
   - 单个高活跃 repo 不能外推为整个生态增长；
   - 证据弱的 ecosystem/foundation campaign 不应成为 Mantle 主叙事。
4. **Short/mid/long-term plan**：
   - 短期：建立 Arbitrum repo watchlist、PR taxonomy 更新机制、BoLD/Timeboost/Orbit/Stylus evidence dashboard；
   - 中期：验证 Mantle preconfirmation/MEV-sharing/proof monitoring/appchain/payment or enterprise demo；
   - 长期：形成 Mantle 自身差异化：EVM-compatible performance, Ethereum-aligned settlement, EigenDA/data availability, MNT liquidity, enterprise/payment distribution。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7, item-8, item-9

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| evidence_window | 起止日期、抓取时间、时区、2026-02-24 起点、结束时间、是否包含当天部分数据 | all |
| discovery_source | org/repo 被发现的来源：seed org、official link、topic、README link、package namespace、dependency/reference、manual review | item-1 |
| repo_inventory_metadata | owner/repo、description、topics、language、archived/fork/template、default branch、stars/forks、pushed_at、created_at、latest release | item-1, item-3 |
| inclusion_decision | include-top、include-strategic-appendix、exclude-fork、exclude-archived、exclude-inactive、exclude-unrelated，并说明理由 | item-1, item-3 |
| activity_metrics | PR created/merged/closed/open、merge rate、median merge latency、commit active days、unique PR authors、unique commit authors、reviewers、release signal | item-2, item-3, item-6 |
| activity_score | 综合分数、各指标标准化值、权重、排名、sensitivity check 结果 | item-2, item-3 |
| noise_filter | bot、generated、format-only、dependency bump、CI-only、docs-only、translation-only、bulk cleanup 的识别和保留/降权规则 | item-2, item-4 |
| repo_cluster | core-protocol-node、stylus-wasm-sdk、orbit-appchain-tooling、timeboost-sequencing-mev、bold-fraud-proof-validation、contracts-bridge-governance、foundation-ecosystem-devrel、docs-education、infra-ops-release、data-indexer-analytics、other | item-3, item-8 |
| pr_metadata | PR 号、标题、状态、创建/合并/关闭时间、作者、review 周期、标签、改动行数、主要目录、关联 issue/release | item-4, item-5 |
| pr_category | 统一 PR 分类及二级分类，含自动分类规则和人工核验结果 | item-4 |
| representative_pr_evidence | 代表 PR 的 body/diff/目录/linked issue/release note 摘要，标注是否实质功能变更 | item-4, item-5 |
| implementation_status | merged-code、open-pr、closed-unmerged、feature-flagged、test-only、docs-only、release-note-only、roadmap-only、mainnet/testnet/devnet/unknown | item-5, item-7, item-8 |
| architectural_change | interface/protocol/sequencing/fraud-proof/WASM/appchain/deployment/docs 层级的影响，是否跨 repo | item-5, item-8 |
| activity_trend | weekly trend、momentum direction、backlog、contributor concentration、release/roadmap/governance correlation | item-6 |
| narrative_signal | 叙事类型、GitHub 证据、官方/治理证据、生态/链上证据、证据置信度、商业含义 | item-7 |
| competitor_comparison | 与 Optimism/Base、zkSync、Starknet、Mantle 的差异维度、source、证据强度 | item-9 |
| mantle_competitive_impact | 对 Mantle 的威胁等级、可迁移性、工程成本、产品价值、叙事价值、建议行动 | item-10 |
| evidence_type | merged-code、open-pr、github-metadata、official-doc、official-blog、governance-proposal、release-note、onchain-data、industry-commentary、internal-research、inferred | all |
| evidence_confidence | high/medium/low，并说明不确定性来源；roadmap/open PR/二手报道默认不得标 high | all |
| caveats_open_questions | 事实缺口、口径争议、未覆盖 repo、API rate-limit、query limitation、不可外推边界、需 Mantle 工程团队复核点 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | funnel | GitHub discovery funnel：seed org -> related org discovery -> repo inventory -> filters -> ranked candidate repos -> selected Top repos / strategic appendix | mermaid or markdown table | item-1, item-2, item-3 |
| diag-2 | leaderboard | 活跃 repo 排名表：rank、owner/repo、cluster、activity score、PR/commit/contributor/release metrics、selection decision | markdown table | item-2, item-3 |
| diag-3 | heatmap | Repo x week 活跃热力图：PR created/merged、commit active days、unique contributors，可拆为两张表 | markdown table | item-3, item-6 |
| diag-4 | matrix | PR 分类矩阵：repo x category x PR count x representative PR x implementation status x narrative meaning x Mantle impact | markdown table | item-4, item-5 |
| diag-5 | architecture | 如果 Top repo 显示 core/proof/sequencing/stylus/orbit cluster 活跃，则绘制 discovered architecture map，展示跨 repo 组件与变更位置；若未发现，则说明不适用 | mermaid | item-5, item-8 |
| diag-6 | timeline | Arbitrum 叙事演变时间线：GitHub activity peaks + official posts/releases/governance/events + ecosystem/onchain signals，标注证据强弱 | mermaid or markdown table | item-6, item-7 |
| diag-7 | comparison | Arbitrum vs Optimism/Base / zkSync / Starknet / Mantle 路线对比矩阵：VM/language、appchain、MEV/sequencing、安全/去中心化、developer tooling、GTM | markdown table | item-9 |
| diag-8 | matrix | Mantle 竞争响应矩阵：Arbitrum signal x evidence strength x threat level x transferability x recommended action x time horizon | markdown table | item-10 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | github_org_inventory | Seed org 和 related org 的 repo inventory。必须覆盖 `OffchainLabs`、`ArbitrumFoundation` 全量 repo，并记录发现的其他相关 org/repo | all seed repos |
| src-2 | github_activity_metrics | 所有候选 repo 的 PR/commit/contributor/release metrics，含查询语句、抓取时间、分页、rate limit、bot/noise 过滤 | all candidate repos |
| src-3 | github_pr_data | Selected Top repo 的近 3 个月 PR 原始数据，含 PR 号、标题、状态、时间、作者、标签、目录、关联 issue/release | all selected repos |
| src-4 | github_code_analysis | 对 selected repo 代表 PR 的 diff 或合并后代码进行文件级验证，覆盖每个 selected repo 的高信号类别 | >= 25 representative PRs total |
| src-5 | official_arbitrum_sources | Arbitrum / Offchain Labs / Arbitrum Foundation 官方 docs、blog、technical roadmap、release notes、ecosystem pages | >= 10 |
| src-6 | official_repo_release_sources | Selected repo 的 release notes、tags、milestones、CHANGELOG、README/docs，用于连接 PR 活动和产品状态 | >= selected repo count |
| src-7 | governance_sources | Arbitrum DAO governance forum、Snapshot/Tally/proposal pages、Security Council / upgrade references，用于 BoLD/Timeboost/Orbit/foundation claims | >= 5 |
| src-8 | orbit_stylus_timeboost_bold_sources | Orbit、Stylus、Timeboost、BoLD 官方 docs/spec/blog/release/governance；若某方向未进 Top active repo，仍需作为叙事核验和低证据说明 | >= 8 |
| src-9 | competitor_sources | Optimism/Base、zkSync、Starknet 官方 docs/blog/code/governance，用于路线对比 | >= 12 total |
| src-10 | onchain_or_metrics_data | Arbitrum One/Nova/Orbit/Stylus adoption/TVL/transactions/active addresses/fees/MEV or sequencer data；可用官方 dashboards、L2Beat、DeFiLlama、explorers | >= 4 |
| src-11 | internal_research | 仓库内已有竞品、Base、Optimism、Starknet、L2 stage、安全或 Mantle 相关研究，用于对比和复用已核验证据 | >= 4 |
| src-12 | industry_commentary | 高可信行业文章、团队访谈、工程博客或社区讨论；只能辅助叙事判断，关键事实必须用 primary source 交叉验证 | >= 3 |
| src-13 | mantle_sources | Mantle docs、代码、公开路线、内部研究或链上数据，用于竞争启示和可迁移性判断 | >= 3 |

## Data Collection Plan for Phase B

1. Use GitHub REST or GraphQL to list org repos:
   - `GET /orgs/{org}/repos?per_page=100&type=all`
   - record `archived`, `fork`, `is_template`, `default_branch`, `topics`, `pushed_at`, `updated_at`, `license`, `homepage`, `latest release`.
2. Discover related orgs/repo:
   - Search official Arbitrum / Offchain Labs / Arbitrum Foundation docs, blogs, ecosystem pages, GitHub org profiles and selected repo README/docs for GitHub links.
   - Search GitHub topics and repo search for `arbitrum`, `nitro`, `stylus`, `orbit`, `timeboost`; include only if official/ecosystem linkage is documented.
3. For each candidate repo, collect:
   - PR created in window: `repo:{owner}/{repo} is:pr created:2026-02-24..{crawl_date}`
   - PR merged in window: `repo:{owner}/{repo} is:pr merged:2026-02-24..{crawl_date}`
   - PR open backlog at crawl time: `repo:{owner}/{repo} is:pr is:open created:<= {crawl_date}`
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

- [ ] The draft starts with org/repo discovery and active repo ranking, not preselected Nitro/Stylus analysis.
- [ ] `OffchainLabs` and `ArbitrumFoundation` are fully scanned, and any additional orgs are included or explicitly rejected with reasons.
- [ ] Top active repo selection is reproducible: exact queries/API, date window, pagination, filters, ranking formula, and sensitivity check are documented.
- [ ] Old Nitro/Stylus assumptions and old counts are not reused without fresh data collection.
- [ ] PR created, PR merged, PR open backlog, commit frequency, contributor count, and release signal are kept as separate metrics before scoring.
- [ ] Bot/generated/docs/CI/dependency noise is identified and either excluded, down-weighted, or reported separately.
- [ ] Selected repo PR categories include representative PRs with manual diff/body verification.
- [ ] Major architecture/feature claims are tied to merged code, open PR, release note, official roadmap, governance source, or official docs with confidence labels.
- [ ] Narratives such as Stylus, Orbit, Timeboost and BoLD are downgraded if GitHub or official/governance evidence is weak in the window.
- [ ] Competitor comparison uses current official sources and avoids generic "Arbitrum vs OP Stack" simplification.
- [ ] Mantle recommendations are split into must-monitor, borrow/prototype, avoid/not-transferable, and short/mid/long-term actions.
- [ ] All time-sensitive facts include access date or crawl date, and all unresolved facts are preserved as caveats.

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | restart-rewrite | `202606-internal-sharing/outlines/competitor-arbitrum.md` | User updated issue: research must discover active Arbitrum repos data-first across orgs instead of preselecting `nitro` and `stylus-sdk-rs` | Multica comment `35b4b90d-34ca-4360-9bd8-fe14d67c5071` |
