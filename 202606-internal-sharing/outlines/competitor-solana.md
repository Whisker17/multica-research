---
topic: "Solana 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-solana"
github_repo: "Whisker17/multica-research"
round: 2
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/competitor-solana.md"
  draft: "202606-internal-sharing/research-sections/competitor-solana/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/competitor-solana/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  分析 Solana 近期开发与叙事变化。研究必须先扫描 Solana 相关 GitHub Organization
  `solana-labs`、`anza-xyz`、`jito-foundation` 下的所有公开 repo，并按 2026-02-23 至
  2026-05-23 近 3 个月活跃度进行数据驱动排序，再从排序结果中确定 Top 活跃 repo 作为
  PR 活动分析对象。不得预设分析 `anza-xyz/agave`、`solana-labs/solana` 或任何其他仓库；
  如发现官方资料、repo 依赖、release note 或生态组织指向其他 Solana 核心相关 org，需记录
  发现依据后纳入扩展扫描或说明排除理由。后续分析需覆盖活跃 repo 概况、PR 分类、重大功能
  变更与架构调整、开发活跃度趋势、公开叙事变化、竞争对比，以及对 Mantle 的启示。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、协议/客户端/生态战略同事、
  以及 Multica Research Squad 的 Review Agent 和 Technical Writer。读者熟悉 L1/L2、
  执行客户端、共识、MEV、SVM、稳定币/支付和 DePIN 基本概念，但需要一份以可复现数据
  为入口、能直接支持内部竞争分析的中文研究 section。

expected_output: |
  一份中文结构化 research section，至少包含：
  - Solana 相关 org 全量 repo 扫描方法、活跃度评分公式、Top repo 排名和入选/排除理由
  - `repo_universe.{csv,json}`、`repo_activity_metrics.{csv,json}`、`repo_ranking.{csv,json}`、`top_repo_prs.{csv,json}` 四组可复算 datasets 及其 query/scoring metadata
  - Top 活跃 repo 的近 3 个月 PR 活动概况、周粒度趋势、贡献者活跃度和代表 PR
  - 主要开发方向与 PR 分类，包括但不限于从数据中出现的客户端/共识/性能、SVM/runtime、MEV/validator infra、program/token tooling、支付/DePIN/RWA 等方向
  - 重大功能变更与架构调整，逐项区分 merged code、open PR、proposal/SIMD、roadmap、devnet/testnet/mainnet 状态
  - Solana 近期叙事变化：新功能和新方向发力点、生态战略调整、与 Ethereum L2、Base、Sui、Starknet、Tempo、Monad 等竞争路径的差异化定位
  - 对 Mantle 的竞争启示：需要监控的工程指标、可借鉴设计、不能照搬的约束、短中长期行动建议
  - 至少 5 张图/表：repo 活跃度排名、PR 分类矩阵、开发趋势时间线、叙事证据矩阵、Mantle 竞争响应矩阵

source_requirements_summary: |
  Phase B 必须优先使用 primary sources：GitHub org/repo/PR/commit/release API、PR diff、官方 docs/blog、
  Solana/Anza/Jito/Solana Foundation 公开资料、SIMD/SPL/roadmap/governance materials、官方或可复核
  on-chain/ecosystem dashboards。所有近况事实必须以 2026-05-23 或之后抓取的数据重新验证。
  不得复用 restart 前旧 outline/drafts/datasets，也不得在未完成 org 全量扫描前指定重点仓库。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-23T14:41:21Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-23T14:56:22Z"

multica_issue_id: "39fa56ed-8511-4fb2-b433-2a61ff998680"
branch_name: "research/202606-internal-sharing/competitor-solana"
base_commit: "6254ca5"
language: "中文"
research_depth: "standard"
restart_note: |
  本 outline 为 2026-05-23 restart 后的新数据驱动 outline，当前为 round-2 revision。旧 outline/drafts/datasets
  已由 Orchestrator 在 commit 6254ca5 清除；本轮必须从数据驱动 repo discovery 重新开始。

prerequisite_sections:
  - slug: payment-tempo
    path: 202606-internal-sharing/research-sections/payment-tempo/final.md
    status: existing-research-if-present
  - slug: enterprise-canton
    path: 202606-internal-sharing/research-sections/enterprise-canton/final.md
    status: existing-research-if-present
  - slug: enterprise-privacy
    path: 202606-internal-sharing/research-sections/enterprise-privacy/final.md
    status: existing-research-if-present
---

# Research Outline: Solana 近期开发与叙事分析

## Research Questions

1. 在 2026-02-23 至 2026-05-23 窗口内，`solana-labs`、`anza-xyz`、`jito-foundation` 三个 org 的所有 repo 中，哪些 repo 按 PR 数量、commit 频率、unique contributors、活跃天数、release/issue 活动和近期趋势综合排序最活跃？
2. 全量 repo 排名是否会推翻对 Solana 近期开发重点的直觉判断？Top 活跃 repo 分别代表 core protocol、client/runtime、validator infra、MEV/Jito、program/tooling、docs/ecosystem 还是其他方向？
3. Top 活跃 repo 的 PR 活动可以归纳出哪些主要开发方向：共识/客户端性能、SVM/runtime、networking、accounts/storage、transaction scheduling、validator operations、MEV、token/program tooling、DePIN/payments/RWA 或其他数据中出现的类别？
4. 哪些近期 PR 或 proposal 构成重大功能变更或架构调整？这些变化是已合并代码、open PR、feature gate、SIMD/proposal、devnet/testnet 实验、roadmap 声明还是 mainnet 已激活？
5. Solana 近期公开叙事是否正在围绕低延迟/高吞吐、多客户端/validator diversity、SVM 扩展、MEV/validator infra、支付/DePIN、Token Extensions/RWA、mobile/consumer 或其他方向发生变化？这些叙事是否有 GitHub 活动支撑？
6. 如果 Alpenglow/SIMD、Firedancer、Jito、SVM rollups、Token Extensions、Solana Pay、DePIN 或 mobile 等主题在数据或 primary sources 中出现，它们分别处于什么成熟度，如何影响 Solana 的竞争定位？
7. 与 Ethereum L2、Base、Sui、Starknet、Tempo、Monad 等竞品相比，Solana 的近期开发重点和叙事差异化在哪里：单体高性能 L1、应用专用 SVM、支付/DePIN 生态、MEV supply chain、validator/client 多样性，还是开发者/消费应用分发？
8. 对 Mantle 而言，Solana 的近期变化构成哪些直接或间接压力？Mantle 应监控哪些指标、借鉴哪些设计、避免哪些误判，并如何把自身 OP Stack/EigenDA/MNT/企业与支付方向转化为差异化回应？

## Items

### item-1: 全量 org/repo 发现、扩展范围和活跃度评分

建立本研究的事实入口。必须扫描 `solana-labs`、`anza-xyz`、`jito-foundation` 三个 GitHub Organization 的所有公开 repo，并在开始 PR 主题分析前生成可复现的 repo universe 与活跃度 ranking。不得预设重点 repo；任何进入 Top 分析集的 repo 都必须来自排序结果或有明确的扩展扫描证据。

必须覆盖：

- Org 扫描方法：GitHub REST/GraphQL/`gh api` 查询、抓取时间、分页完整性、archived/fork/template/private 不可见 repo 的处理；
- 近 3 个月窗口：固定为 2026-02-23 至 2026-05-23，并记录时区、created/updated/merged/committed 的统计口径；
- 活跃度评分：至少包括 PR created、PR merged、commit count、unique contributors、active days、release count、issue/comment activity、近期加速度；需要给出公式、权重和敏感性检查；
- 预注册评分设计：Phase B 开始 PR 主题分析前，必须在 outline 本文或 companion file 中固定 metric weights、normalization approach 和 de-noising rules；如使用 companion file，draft 必须列出路径；权重不得在看到 Top repo 结果后为迎合直觉而调整；
- 标准化方法：必须使用 log-scaling、winsorized scaling、percentile/rank scaling 或等价方案，避免 raw PR/commit/issue/comment 量直接支配总分；如果保留 raw activity view，必须与去噪/标准化 view 分开呈现；
- 去重和 repo 身份规则：必须明确 duplicate/fork/rename/migration 处理，说明 canonical repo 选择、历史 repo 与 active fork 是否合并计数、fork/template 是否排除或单列、rename 后旧 URL 如何追踪；
- 排名阶段噪音控制：bot-generated、docs-only、CI-only、release-automation、changelog-only repo/activity 必须在 repo-ranking 阶段显式识别、标记和处理，不得推迟到 item-2 的 PR-level filtering 才处理；
- Top repo 选择：建议 Top 8-12，但最终数量由长尾分布决定；需要同时报告全量 ranking、阈值、入选理由和未入选但高战略相关 repo；
- 敏感性视图：repo ranking dataset 至少包含三套排序/视图：(a) raw activity ranking，保留原始活跃量；(b) human-code-activity ranking，排除 bots/docs/CI/release/changelog noise 后的代码活动；(c) strategic-low-activity watchlist，识别近期低活跃但因协议、roadmap、生态或运营相关性高而需要持续关注的 repo；
- 扩展 org 发现：如官方 docs、repo dependency、release note、SIMD/SPL、Solana Foundation 或生态核心项目指向其他 Solana 相关 org，记录来源后决定是否纳入扩展扫描；
- 强制数据产物：必须在 `202606-internal-sharing/research-sections/competitor-solana/datasets/` 持久化以下 JSON/CSV 文件，供 Review Agent 独立复算，不能只在正文放表：
  - `repo_universe.csv` 和 `repo_universe.json`：`solana-labs`、`anza-xyz`、`jito-foundation` 的全量公开 repo list，包含 zero-/low-activity repos；
  - `repo_activity_metrics.csv` 和 `repo_activity_metrics.json`：全量 repo 的 per-repo metric rows，不限 Top repos；
  - `repo_ranking.csv` 和 `repo_ranking.json`：含综合 score、分项 score、权重、normalization/de-noising 标记和三套 sensitivity views 的 ranked output；
  - `top_repo_prs.csv` 和 `top_repo_prs.json`：Top-repo PR dataset，记录入选 repo 的 PR rows、分类字段、噪音标记、代表 PR 标记和可回溯 URL。
- 数据元数据要求：上述每个 dataset 文件必须包含或伴随同名 metadata 字段/文件，记录 fetch timestamp、timezone、exact REST/GraphQL/`gh` CLI queries、pagination notes、rate-limit notes、archived/fork/template flags、exclusions applied、duplicate/fork/rename handling、zero-/low-activity repo coverage，以及任何扫描失败或不可见资源的说明。

- **Priority**: high
- **Dependencies**: none

### item-2: Top 活跃 repo 的 PR 数据集、分类体系和代表 PR 选择

在 item-1 之后，针对数据选出的 Top 活跃 repo 生成 PR 数据集和分类规则。该项要把 repo-level 活跃度转化为 PR-level 证据，避免把 star、repo 名称或历史重要性误当成近期开发重点。

必须覆盖：

- 每个入选 repo 的 PR created/merged/open/closed-unmerged/draft/revert/backport/bot/generated/docs-only/CI-only 分布；
- 周粒度趋势：PR created、merged、open backlog、merge latency、review latency、核心作者与 reviewer；
- 分类体系：先用 title/body/files/labels/目录/linked issue 自动预分类，再对每个高信号类别人工复核代表 PR；
- 代表 PR 选择：每个入选 repo 至少选 5-10 个代表 PR；PR 量较小但战略相关的 repo 可降低数量但必须说明；
- PR 证据等级：`merged-code`、`open-pr`、`closed-unmerged`、`draft-pr`、`proposal-linked`、`release-note-linked`、`test-only`、`docs-only`、`inferred`；
- 噪音控制：bot/dependabot、formatting、generated bindings、snapshot updates、CI flake fixes、bulk refactors 不得与功能推进混为一谈。
- 数据产物：Top-repo PR dataset 必须以 `top_repo_prs.csv` 和 `top_repo_prs.json` 持久化到 `202606-internal-sharing/research-sections/competitor-solana/datasets/`，并可与 item-1 的 `repo_ranking.{csv,json}` 通过 repo full name、repo id、PR number/URL 和抓取窗口 join；不得只在 prose table 中呈现代表 PR。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 数据驱动的近期开发重点与架构变更

从 item-2 的 PR 分类中识别 Solana 近期真正的工程主线。研究必须先呈现数据中出现的类别，再解释其协议、客户端、validator、program/tooling 或生态含义；不得在未验证前把旧叙事套入新数据。

潜在但需由数据验证的分析维度包括：

- Client/protocol core：共识、replay、banking stage、runtime/SVM、accounts DB、storage、snapshot、networking、gossip、QUIC/TPU、feature gate；
- Performance and scheduling：transaction scheduling、fee markets、compute budget、priority fees、local fee markets、block packing、latency、throughput；
- Validator/operator infra：validator CLI、monitoring、deployment、ledger tooling、RPC, test validator、release automation、security fixes；
- MEV/Jito supply chain：block engine、relayer、shredstream、bundle auction、tip distribution、validator incentives、restaking 或 stake pool 相关变化；
- Programs/tooling：SPL/token tooling、Token Extensions、program libraries、Anchor/SDK、developer CLI、testing frameworks；
- Ecosystem/application infra：wallet/mobile、payments, DePIN support, indexing, docs, examples, grants/hackathon tooling；
- 架构变更判断：每个重大变更需标注涉及 repo/PR、代码路径、状态、上线假设、风险、是否改变 mainnet 行为。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 活跃度趋势、贡献者结构和组织重心变化

解释 Solana 开发活动的时间趋势和组织结构，而不仅是静态 Top repo 排名。该项要判断近期活跃度是集中于少数 core repo，还是分散到 Anza/Jito/Solana Labs 多个团队与工具链；也要区分真实开发加速与一次性迁移/重构/CI 噪音。

必须覆盖：

- 周粒度活跃度：Top repo 的 PR created/merged、commit count、active contributors、merge latency 和 open backlog；
- 组织比较：`solana-labs`、`anza-xyz`、`jito-foundation` 三个 org 的活动占比、类别差异和趋势变化；
- 贡献者结构：核心维护者、外部 contributors、bots、reviewers、单点依赖和团队边界；
- Repo 迁移/归档风险：如 historical repo 与 active fork/renamed repo 并存，必须说明如何避免重复计数或错把旧 repo 当活跃中心；
- Release 和 mainnet 相关性：高 PR 活跃是否对应 release、feature activation、validator upgrade、testnet/devnet/mainnet rollout；
- 对叙事的含义：活动重心从 Labs 到 Anza/Jito、从 core 到 tooling、从 performance 到 ecosystem 的变化若存在，需要用数据证明。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: 重大功能、proposal/SIMD 和 roadmap 状态校准

把 PR 活动与 Solana 官方 proposal、SIMD、roadmap、release note 和公开工程博客连接起来。该项必须区分代码实现、治理/社区投票、proposal metadata、feature gate、benchmark、testnet/devnet 和 mainnet activation，避免把 roadmap 或 benchmark 写成生产事实。

必须覆盖：

- Proposal/SIMD 关联：从 Top repo PR、commit message、issue、release note 中提取相关 SIMD/SPL/proposal，并核验官方状态；
- Consensus/performance 方向：如 Alpenglow/SIMD-0326、Votor/Rotor、PoH/TowerBFT 替代、latency/finality claims 等若在当前 primary sources 中出现，需明确 governance vote、metadata state、implementation PR、devnet/testnet/mainnet 状态和剩余风险；
- Multi-client/validator diversity：如 Firedancer、Agave、Solana Labs legacy client 或其他 validator/client effort 被数据或官方资料指向，需说明 repo 所属组织、代码活跃度、compatibility/testnet/mainnet 状态；
- SVM/runtime 扩展：runtime、program execution、SVM rollup/appchain、SDK/tooling 相关变化必须以 PR/官方资料验证；
- Token/program/payment/DePIN 方向：Token Extensions、Solana Pay、DePIN/RWA/payments 等若作为叙事出现，需追溯到 repo activity、official docs 或 on-chain/ecosystem evidence；
- 风险与反证：对于没有 PR 支撑或仅有营销材料的叙事，必须降级为 narrative signal，并标注缺少的证据。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-6: Solana 近期叙事变化与生态战略调整

综合 GitHub 活动和公开信息，判断 Solana 近期叙事是否发生变化。叙事分析必须从数据和 primary sources 出发，不得预设 Solana 的重点一定是某个仓库或某条旧叙事。

必须覆盖：

- 叙事时间线：2026-02-23 至 2026-05-23 的官方 blog、docs、roadmap、release、governance/proposal、ecosystem announcement；
- 技术叙事：低延迟/高吞吐、consensus overhaul、multi-client、SVM scaling、MEV/validator infra、fee markets、network stability；
- 应用/生态叙事：payments、DePIN、mobile/consumer、Token Extensions/RWA、stablecoin、institutional/enterprise、developer tooling；
- 证据矩阵：每个叙事需映射到 GitHub activity、official source、on-chain/ecosystem data、industry commentary 和置信度；
- 竞争定位：Solana 如何相对 Ethereum L2/Base、Sui、Starknet、Tempo、Monad 等竞品定位自己；哪些差异是工程事实，哪些是市场叙事；
- 负面或约束：validator decentralization、client diversity、network stability、MEV centralization、state growth、hardware requirements、governance coordination 等潜在风险必须列入。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5

### item-7: 横向竞品对比与 Mantle 竞争压力分解

将 Solana 的近期开发重点放入 Mantle 关心的竞争格局中。比较要围绕工程能力、产品叙事和生态 go-to-market，而不是泛泛比较 TPS 或 TVL。

比较对象至少包括：

- Ethereum L2 / Base：OP Stack/Reth/Flashblocks、L2 settlement/security、distribution、application ecosystem；
- Sui：Move/object model、gasless stablecoin payments、consumer/payment UX、parallel execution；
- Starknet：Cairo/STARK/provable appchain、proof/finality、游戏/AI/Bitcoin liquidity narratives；
- Tempo：payments-first L1、stablecoin gas、Payment Lane、enterprise/privacy Zones；
- Monad/其他高性能 EVM L1：EVM compatibility、高 throughput/low latency、parallel execution、developer migration；
- Jito/MEV 供应链内部竞争维度：validator incentives、MEV capture、restaking/liquid staking 如数据支持。

对比维度：

- latency/finality、throughput、fee predictability、developer compatibility、app specialization、sequencing/MEV、validator/client diversity、payment/DePIN readiness、enterprise suitability、governance/security assumptions；
- 对 Mantle 的压力来源：用户/开发者心智、支付/DePIN应用、性能叙事、settlement/finality、sequencer/MEV、生态 BD；
- 对 Mantle 的机会：OP Stack/EVM compatibility、EigenDA/DA strategy、MNT economics、enterprise/payment integration、L2/L3/appchain strategy。

- **Priority**: high
- **Dependencies**: item-5, item-6

### item-8: Mantle 行动建议、监控指标和不确定性

把研究结论转化为 Mantle 可执行判断。建议必须按证据强度和行动成本分层，不能因为 Solana 某方向活跃就直接建议 Mantle 复制。

必须输出：

1. **必须监控**：
   - Top repo 活动趋势、major PR/release、proposal/SIMD 状态、mainnet activation、validator/client rollout；
   - Solana latency/finality/performance claims 是否有生产指标支撑；
   - SVM/payment/DePIN/Token Extensions/RWA 叙事是否出现真实 adoption evidence。
2. **可借鉴/可原型**：
   - PR 数据驱动的 roadmap watchlist；
   - performance/finality dashboard、client diversity reporting、feature activation transparency；
   - payment/DePIN 专用 UX、fee predictability、developer tooling、MEV observability。
3. **谨慎或不适合照搬**：
   - 单体 L1 硬件/validator 假设直接迁移到 Mantle；
   - SVM/runtime 设计直接套到 EVM/OP Stack；
   - 以 benchmark 替代 production reliability；
   - 把生态营销当作 adoption。
4. **短中长期建议**：
   - 短期：建立 Solana repo/PR watchlist 和竞品叙事 dashboard；
   - 中期：针对支付/DePIN/low-latency UX 做 Mantle 原型或市场测试；
   - 长期：评估 Mantle L2/L3/appchain、finality、sequencer/MEV、enterprise/payment 差异化路线。

- **Priority**: high
- **Dependencies**: item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| evidence_window | 研究窗口、抓取时间、时区、数据源、查询语句和是否覆盖全量 org/repo | all |
| dataset_path | 持久化 dataset 文件路径、格式、schema/version、fetch timestamp、timezone、exact queries、pagination/rate-limit notes 和可复算说明 | item-1, item-2, all gates |
| repo_universe | org、repo、archived/fork/template 状态、primary language、description、stars/forks、last pushed、release/issue activity、zero-/low-activity 标记、是否纳入 ranking | item-1 |
| activity_score | PR created/merged、commit count、unique contributors、active days、release count、issue/comment activity、加速度、explicit weights、normalization/de-noising 方法和敏感性检查 | item-1, item-4 |
| ranking_view | raw activity ranking、human-code-activity ranking、strategic-low-activity watchlist 三套视图的 score、rank、入选/排除依据和差异解释 | item-1, item-4 |
| noise_treatment | bot-generated、docs-only、CI-only、release-automation、changelog-only、generated files、formatting 和 bulk refactor 在 repo-ranking 与 PR-level 两阶段的处理规则 | item-1, item-2, item-4 |
| repo_identity_rule | duplicate/fork/rename/migration/canonical repo 处理规则、合并/排除理由和可能导致 ranking 偏差的风险 | item-1, item-4 |
| selection_rationale | Top repo 入选/排除理由、阈值、长尾分布、战略相关但低活跃 repo 的处理 | item-1, item-2 |
| pr_count_and_state | 每个入选 repo 的 PR 总量、merged/open/closed/draft、bot/human、docs/CI/generated/revert/backport 处理 | item-2, item-3, item-4 |
| pr_category | PR 分类标签、分类依据、代表 PR、涉及目录/组件和人工复核结论 | item-2, item-3 |
| implementation_status | 功能处于 merged-code、open-pr、proposal/SIMD、feature-gated、devnet/testnet、mainnet-active、roadmap 或 narrative-only 哪一阶段 | item-3, item-5, item-6 |
| code_surface | 涉及的 repo、package、目录、module、protocol/component boundary 和变更范围 | item-3, item-5 |
| contributor_signal | active contributors、maintainers、reviewers、外部贡献者、bot 噪音、组织边界和单点依赖 | item-4 |
| narrative_signal | 叙事主张、对应 GitHub/official/on-chain/industry evidence、置信度和反证 | item-5, item-6 |
| competitor_mapping | Solana 与 Base/Sui/Starknet/Tempo/Monad/Ethereum L2 等竞品的差异化维度和证据等级 | item-7 |
| mantle_impact | 对 Mantle 的竞争压力、可借鉴设计、不可照搬约束、监控指标和行动建议 | item-7, item-8 |
| confidence_and_gaps | 数据缺口、API 限制、冲突来源、未验证假设、需要工程团队进一步确认的问题 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | 全量 repo 活跃度排名矩阵：org/repo、activity score、PR/commit/contributor/release 指标、入选状态和主要类别 | mermaid | item-1 |
| diag-2 | timeline | 2026-02-23 至 2026-05-23 Top repo PR/release/proposal/roadmap 事件时间线，按 repo 或类别分泳道展示 | mermaid | item-2, item-3, item-5 |
| diag-3 | comparison | PR 分类矩阵：repo × 类别 × PR 数量 × 代表 PR × implementation status × narrative relevance | mermaid | item-2, item-3 |
| diag-4 | flow | 从 GitHub activity 到 narrative claim 的证据链：repo/PR -> code/proposal/release -> public narrative -> ecosystem evidence -> confidence | mermaid | item-5, item-6 |
| diag-5 | comparison | Solana vs Base/Sui/Starknet/Tempo/Monad/Mantle 竞争定位对比：性能/finality、developer compatibility、payment/DePIN、MEV、enterprise、security assumptions | mermaid | item-7 |
| diag-6 | flow | Mantle 响应决策流：monitor、prototype、partner、differentiate、ignore 的触发条件和风险 | mermaid | item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | github_org_api | `solana-labs`、`anza-xyz`、`jito-foundation` 全量 repo listing；包括分页、archived/fork/template 处理和抓取时间 | 3 |
| src-2 | github_activity_api | 每个候选 repo 的 PR、commit、contributor、release、issue/comment 数据；需覆盖 Top ranking 所需指标、exact queries、分页/rate-limit notes 和全量 per-repo persisted rows | 20 |
| src-3 | github_pr_diff | Top 活跃 repo 的代表 PR 页面、diff、linked issue/release；每个高信号类别需人工复核代表 PR | 40 |
| src-4 | official_docs_blog | Solana、Anza、Jito、Solana Foundation、SPL/SVM/Solana Pay 等官方 docs/blog/roadmap/release notes，用于校准叙事和状态 | 12 |
| src-5 | governance_proposals | SIMD/SPL/proposal/governance/community vote/feature gate 资料；必须区分 proposal metadata、vote、implementation 和 mainnet activation | 6 |
| src-6 | release_and_changelog | 入选 repo 的 release notes、tags、validator/client upgrade notes、mainnet/testnet/devnet activation notes | 8 |
| src-7 | on_chain_ecosystem_data | 可复核 on-chain 或 ecosystem dashboards/API，用于验证支付、DePIN、Token Extensions/RWA、MEV/Jito、validator/client adoption 等叙事 | 8 |
| src-8 | competitor_primary_sources | Base/Optimism、Sui、Starknet、Tempo、Monad/Ethereum L2 等竞品的官方 docs/blog/research，用于横向对比 | 8 |
| src-9 | internal_research | 本仓库已有 Tempo、Canton、enterprise privacy 或其他内部研究，用于 Mantle 支付/企业/隐私/竞争启示交叉引用 | 3 |
| src-10 | expert_commentary | 高可信工程博客、研究报告、podcast/transcript 或行业评论；只能辅助解释叙事，关键事实必须用 primary source 交叉验证 | 4 |

## Review Gates

Deep draft 进入 adversarial review 前必须通过以下 pass/fail gate：

1. `202606-internal-sharing/research-sections/competitor-solana/datasets/` 下必须存在 `repo_universe.{csv,json}`、`repo_activity_metrics.{csv,json}`、`repo_ranking.{csv,json}`、`top_repo_prs.{csv,json}`，且正文必须列出这些 dataset paths。
2. Dataset 或 companion metadata 必须提供 fetch timestamp、timezone、exact REST/GraphQL/`gh` CLI queries、pagination notes、rate-limit notes、archived/fork/template flags、exclusions applied、duplicate/fork/rename handling、zero-/low-activity repo coverage 和扫描失败说明。
3. `repo_ranking.{csv,json}` 必须包含 explicit metric weights、normalization approach、ranking-stage de-noising rules、raw activity ranking、human-code-activity ranking 和 strategic-low-activity watchlist。
4. Review Agent 必须能只依赖 persisted datasets 和 query metadata 独立复算 Top repo selection；prose tables、截图或正文摘要不能替代可复算数据。
5. 如果上述持久化文件、query metadata 或 scoring metadata 缺失，或不足以独立复算 Top repo selection，则 deep draft 必须判定为 gate fail，不能进入 final promotion。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | revised | item-1, item-2, Fields, Source Requirements, Review Gates | 将 repo universe/activity/ranking 和 Top-repo PR datasets 改为强制持久化产物；补齐预注册评分、normalization/de-noising、三套 sensitivity views 和 deep draft pass/fail reproducibility hook | Orchestrator Revision Request `9c2e9a86-65a2-4bc5-b2f7-682cd0a5d917` |
