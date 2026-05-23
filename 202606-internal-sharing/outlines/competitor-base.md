---
topic: "Base 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-base"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/competitor-base.md"
  draft: "202606-internal-sharing/research-sections/competitor-base/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/competitor-base/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  根据更新后的 issue 描述重新研究 Base 近期开发与叙事变化。研究必须先扫描 `base`、`base-org`
  以及通过官方链接、repo metadata、docs、GitHub topics、package namespace 发现的其他相关 GitHub
  Organization 下全部可见 repo，对近 3 个月 PR 数量、commit 频率、活跃 contributor、release/tag、
  default-branch push、issue/discussion 等指标做数据驱动排序，再选择 Top 活跃 repo 进入深度分析。
  不得预设只分析 `base/base`；PR Tracker 每日跟踪报告已覆盖 `base/base`，只能作为辅助交叉验证和
  历史线索，不能替代 org-wide GitHub 原始数据。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、Mantle 协议/客户端/基础设施/生态与战略团队、
  Research Review Agent 和 Orchestrator。读者熟悉 L2、OP Stack、Superchain、Base Stack、Coinbase
  生态和 Mantle 现有性能/架构研究，但需要一份以最新公开开发活动和官方叙事为基础、可复核且不预设
  repo 结论的竞争对手近况梳理。

expected_output: |
  一份中文结构化 research section，涵盖：
  - Base 相关 GitHub org/repo 的近 3 个月活跃度数据集、排序方法、Top 活跃 repo 概况和排除项；
  - Top 活跃 repo 的 PR 活动分类、主要开发方向、重大功能变更、架构调整和活跃度趋势变化；
  - Base 近期叙事演变：Base Stack 独立路线、新功能和新方向发力点、性能/预确认/证明/资产发行/开发者体验、
    Coinbase 生态绑定和生态战略调整；
  - 对 Mantle 的竞争启示：直接威胁、可借鉴设计、不可照搬约束、短中长期行动建议；
  - 至少 5 张图/表：org/repo universe 表、repo 活跃度排行榜、Top repo PR 趋势图、PR 分类矩阵、
    叙事演变时间线、Mantle 竞争响应矩阵。

source_requirements_summary: |
  Deep phase 必须优先使用 primary source。第一步必须直接查询 GitHub org/repo/PR/commit/contributor/release
  数据，固定近 3 个月窗口并记录查询时间、查询语句、分页完整性、rate-limit caveat、去重规则和排序公式。
  PR Tracker 每日报告、仓库内既有 Base Azul、Base 性能、Mantle 切换 Base codebase 研究只能作为辅助输入，
  必须用 GitHub 原始数据、Base 官方 docs/blog/spec、Coinbase 官方资料和可核验链上/benchmark 数据重新验证。
  时间敏感事实不得沿用旧 artifact 或本 outline 的示例。

methodology_gate:
  repo_discovery_first: true
  prohibition: "不得预设只分析 base/base；不得在完成 org-wide repo 活跃度排序前决定最终分析 repo 列表。"
  required_orgs: ["base", "base-org"]
  related_org_policy: "通过 Base 官网/docs/blog、GitHub repo metadata、package namespace、官方链接和 GitHub search 发现其他相关 org，并记录纳入/排除理由。"
  time_window: "默认以 deep draft 抓取日向前 3 个月；若 2026-05-24 抓取，建议记录为 2026-02-24 至 2026-05-24 UTC，并在 draft 中写明实际抓取时间。"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-24T00:15:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-24T00:15:00+08:00"

multica_issue_id: "30956d61-edce-4606-bf76-169d60c817ca"
branch_name: "research/202606-internal-sharing/competitor-base"
base_commit: "3b25b071c64e95836c8a21913e6159c703c57e48"
language: "中文"
research_depth: "standard"

prerequisite_sections:
  - slug: base-strategy-azul-overview
    path: base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md
    status: existing-research
  - slug: flashblocks-network-changes
    path: base-azul-upgrade/research-sections/flashblocks-network-changes/final.md
    status: existing-research
  - slug: base-vs-optimism-flashblocks
    path: base-azul-upgrade/research-sections/base-vs-optimism-flashblocks/final.md
    status: existing-research
  - slug: multiproof-architecture
    path: base-azul-upgrade/research-sections/multiproof-architecture/final.md
    status: existing-research
  - slug: multiproof-provers-challengers
    path: base-azul-upgrade/research-sections/multiproof-provers-challengers/final.md
    status: existing-research
  - slug: osaka-evm-changes
    path: base-azul-upgrade/research-sections/osaka-evm-changes/final.md
    status: existing-research
  - slug: mantle-impact-assessment
    path: base-azul-upgrade/research-sections/mantle-impact-assessment/final.md
    status: existing-research
  - slug: block-builder-flashblocks-throughput
    path: base-perf-analysis/research-sections/block-builder-flashblocks-throughput/final.md
    status: existing-research
  - slug: perf-gap-analysis-recommendations
    path: base-perf-analysis/research-sections/perf-gap-analysis-recommendations/final.md
    status: existing-research
  - slug: architecture-advantage-summary
    path: mantle-base-codebase-evaluation/research-sections/architecture-advantage-summary/final.md
    status: existing-research
  - slug: comprehensive-evaluation-recommendation
    path: mantle-base-codebase-evaluation/research-sections/comprehensive-evaluation-recommendation/final.md
    status: existing-research
---

# Research Outline: Base 近期开发与叙事分析

## Methodology Gate

Deep draft 开始前必须先完成 `item-1` 和 `item-2` 的 org/repo universe 发现与活跃度排名，并把完整排序表写入草稿第一部分。只有在 repo 活跃度排名表完成后，才能确定后续 PR 深挖对象。若 `base/base` 排名第一，也必须证明这一结论来自 org-wide 数据；若 SDK、docs、contracts、infra、apps、examples、spec 或 Coinbase 相关 repo 在特定维度更活跃，必须纳入 Top repo 分析或明确排除理由。

最低执行要求：

- 扫描 `base`、`base-org` 全部可见 repo，并通过 Base 官网/docs/blog、repo README、GitHub topics、package namespace、Coinbase developer docs 和 GitHub search 发现其他相关 org/repo。
- 对 archived、fork、template、mirror、sample、website/docs、SDK、app、infra、contracts、spec、research、ecosystem tooling repo 分别标注类型。
- 统计近 3 个月 PR created、PR merged、PR closed、commit count、active contributors、release/tag、default branch push、issue/discussion activity。
- 形成可复核排序公式。建议基础权重：merged PR 30%、PR created 20%、commit count 20%、active contributors 15%、release/tag/default-branch recency 10%、issue/discussion signal 5%；如调整权重必须解释。
- 选择 Top 5-8 活跃 repo 作为候选，最终深挖数量可按数据分布收敛到 Top 3-5，但必须保留完整排名附录。
- PR Tracker 每日报告只能用于核验 `base/base` 的细节覆盖、补充 PR 摘要和发现遗漏，不得替代 GitHub API/GraphQL/gh CLI 的原始数据。

## Research Questions

1. 近 3 个月内，`base`、`base-org` 和其他经验证相关 org 下哪些 repo 实际最活跃？排序依据是什么，Top repo 是否只有 `base/base`，还是 contracts、docs/spec、SDK、infra、apps、examples 或 Coinbase 相关 repo 也显示出显著投入？
2. Top 活跃 repo 的开发活动分别指向哪些主线：Base Stack 独立路线、Azul 后续、Beryl/预编译合约、性能/5K 叙事、Flashblocks、Multiproof、开发者体验、资产发行、Coinbase 生态集成、运维可靠性，还是其他数据发现的新方向？
3. Top repo 的 PR 活动在近 3 个月是否出现方向变化、release 前后峰值、贡献者集中、跨 repo 协同或从协议研发向产品化/生态工具扩散的迹象？
4. 哪些 PR、commit、release、spec 或 docs 变化代表重大功能变更、架构调整或产品化推进？它们处于 merged-code、released、testnet、mainnet-active、feature-gated、roadmap、experimental 还是 docs-only 阶段？
5. Base 的对外叙事是否从 OP Stack/Superchain 成员与低费 L2，进一步转向独立 Base Stack、高性能/低延迟、链上资产发行、Coinbase 分发和 onchain economy 平台底座？
6. "脱离 OP Stack"应如何精确表述：哪些层独立，哪些层仍继承/共享/兼容 Superchain 或 OP Stack 组件？这个变化对 Mantle 的上游依赖和代码路线意味着什么？
7. Base 的近期发力对 Mantle 构成哪些竞争压力：性能口径、开发者心智、资产发行/合规原语、支付/商户生态、Coinbase 渠道、Stage 2/最终性叙事、运维与 release 速度？
8. Mantle 应该立即跟踪什么、借鉴什么、避免照搬什么，并如何转化为工程 watchlist、POC、产品叙事和中长期路线建议？

## Items

### item-1: GitHub org/repo universe 发现与纳入边界

建立研究对象边界。该项不是分析预设 repo，而是先发现 Base 相关代码资产和文档/生态资产分布。必须从 GitHub API/GraphQL/gh CLI 拉取 `base`、`base-org` 全部可见 repo，并补充官方链接和搜索验证是否存在相关 org/repo。

必须覆盖：

- `base`、`base-org` 全 repo 清单：repo name、URL、description、archived/fork/template 状态、default branch、primary language、stars/forks、created/updated/pushed_at；
- 相关 org/repo 发现：从 Base 官网、docs、blog、GitHub topics、repo README、package metadata、Coinbase developer docs、official links 搜索是否存在官方/半官方 repo；
- repo 类型标注：core protocol/client、contracts/precompile/spec、Flashblocks/builder、Multiproof/proof、SDK/API/CLI、docs/website、wallet/app、infra/devops、examples/demo、benchmark/load-test、deprecated/archive；
- 纳入/排除规则：archived repo 默认排除活跃排序但保留清单；fork/mirror 单列；纯 website/docs 可进入叙事/开发者投入分析但不能直接等同协议开发；
- 输出完整 repo universe 表，作为后续 ranking 的输入。

- **Priority**: critical
- **Dependencies**: none

### item-2: 近 3 个月 repo 活跃度排名与 Top repo 选择

对 `item-1` 的 repo universe 做数据驱动排序，决定后续 PR 深挖对象。该项是本研究硬门槛，deep draft 不得跳过。

必须覆盖：

- 时间窗口固定为 deep draft 抓取日向前 3 个月，所有查询使用 UTC 日期并说明边界是否含首尾日；
- 每个 repo 的 PR created、PR merged、PR closed、commit count、active contributors、active weeks、default branch pushes、release/tag 数、recent issue/discussion activity；
- 排序公式和权重；至少给出总分、各指标原始值、归一化值、rank；
- 噪声处理：dependabot/renovate、release/backport、bot-generated docs、large generated files、archived/fork repo、monorepo squash merge；
- Top repo 选择规则：建议 Top 5-8 候选，若数据长尾明显可选 Top 3-5 深挖；所有排除的高分 repo 需解释；
- 敏感性检查：PR-only、commit-only、contributors-only、recent-release-only 四种视角是否改变 Top repo；
- 与 PR Tracker 的关系：Tracker 已覆盖的 `base/base` 排名、遗漏与差异如何处理。

- **Priority**: critical
- **Dependencies**: item-1

### item-3: Top repo PR 活动基线与原始数据表

针对 `item-2` 选出的 Top repo，建立 PR 级事实底座。输出需要支持可复核分析，而不是只汇总结论。

必须覆盖：

- 每个 Top repo 的 PR 原始表：repo、PR number、title、state、created_at、merged_at/closed_at、author、is_bot、labels、milestone、changed files、additions/deletions、touched directories、review count、source URL；
- 每周 PR created / merged / closed / still-open 趋势；
- merge latency、large PR 占比、revert/backport/hotfix/release PR 占比；
- contributor 分布：Base core、Coinbase、外部贡献者、bot、生态合作方；
- 跨 repo 协同：同一功能是否同时触达 core/client、contracts/spec、docs、SDK、infra、examples 或 Coinbase docs；
- GitHub API 限制、private work 不可见、squash merge、force push、monorepo 子目录归类和 PR Tracker coverage caveats。

- **Priority**: high
- **Dependencies**: item-2

### item-4: PR 分类体系与开发方向分布

把 Top repo 的 PR 数据转化为开发方向图谱。分类应先由 repo/path/labels/title/PR body/changed files 证据生成，再人工合并成研究可读类别；若数据发现新方向，必须新增分类而不是硬塞进旧框架。

建议分类：

1. **Base Stack / 客户端独立路线**：base-reth-node、base-consensus、Engine API、hardfork config、migration、release tooling；
2. **Azul 后续与 EVM/DX 对齐**：Osaka EIP、P256、eth/69、eth_config、developer RPC、compatibility tests；
3. **Beryl / 预编译合约与资产发行**：Token Factory、Policy Registry、系统地址、ABI、gas pricing、activation gate；
4. **性能与 5K Peak TPS 叙事**：execution optimization、builder separation、state root、gas/tx cap、load tests、benchmark；
5. **Flashblocks / 预确认 UX**：producer/consumer、WebSocket/P2P、rollup-boost、pending RPC、sub-block pipeline；
6. **Multiproof / 安全与最终性**：TEE、ZK、AggregateVerifier、Proposer、Challenger、Registrar、withdrawal/finality；
7. **Coinbase 生态绑定**：wallet、smart wallet、onramp/offramp、Commerce、Developer Platform、stablecoin、identity/compliance；
8. **SDK / Docs / DevRel / Examples**：API、CLI、SDK、docs、tutorial、sample app、migration guide；
9. **运维/可靠性/测试/安全**：CI、fuzz、integration tests、observability、release infra、incident hardening、dependency security；
10. **Other data-discovered category**：由 Top repo 数据直接发现的新方向。

每类需要输出 PR 数量/占比、代表 PR、repo 分布、趋势变化、工程意图、用户/开发者可见影响、implementation status 和 confidence。

- **Priority**: high
- **Dependencies**: item-3

### item-5: Top 活跃 repo 的开发重点与重大变更深挖

从分类结果中筛出真正影响协议行为、架构、开发者接口、资产发行、性能或生态叙事的变化。每个重大变更必须有 PR/commit/release/spec/docs evidence。

必须覆盖：

- 每个 Top repo 的功能定位、近期主线、重大 PR/commit/release、关键目录和状态；
- Base Stack 相关 repo 是否显示客户端、共识、hardfork、release 或 migration 路线持续独立；
- contracts/spec/precompile 类 repo 是否显示 Beryl、Token Factory、Policy Registry 或资产发行能力推进；
- Flashblocks/builder/performance 类 repo 是否显示低延迟、吞吐、builder separation 或 load-test 进展；
- Multiproof/proof/security 类 repo 是否显示 TEE/ZK/withdrawal/finality 路线推进；
- docs/SDK/examples/infra 类 repo 是否显示产品化、开发者教育、Coinbase 生态接入或 operator readiness；
- 输出"重大变更表"：变更名、repo、PR/commit/release/spec、状态、影响层、叙事含义、风险/限制、证据链接、置信度。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: 开发活跃度趋势与工程组织信号

判断 Base 近期是协议创新加速、产品化推进、维护稳定、release 收敛、跨 repo 协同增强，还是单一 repo 活跃导致的统计错觉。不能只把 PR 数量等同于战略投入。

必须覆盖：

- Top repo 每周活动趋势、release/tag 前后峰值、issue/discussion 变化；
- merge latency、review 密度、large PR、revert/backport/hotfix、test-only/docs-only PR 占比；
- contributor 集中度：Base/Coinbase core vs 外部贡献者；是否出现新团队或合作方参与；
- 模块集中度：热点目录是否集中在 client/consensus/contracts/precompile/performance/docs/SDK/infra；
- 跨 repo 节奏：重大功能是否从 code/spec 到 SDK/docs/examples/operator tooling 形成产品化链条；
- 与官方叙事事件的时间关系：blog/announcement 前后是否有代码和文档支撑；
- 对 Mantle 可比指标：核心协议变更频率、release velocity、developer tooling 投入、性能/证明/支付产品化投入。

- **Priority**: medium
- **Dependencies**: item-3, item-4, item-5

### item-7: Base Stack 独立路线与 OP Stack/Superchain 关系

专门处理"脱离 OP Stack 后的独立发展路线"。必须复用既有 Base Azul 和 Mantle Base codebase evaluation 研究，但所有时间敏感事实必须重新验证。避免把"代码/客户端独立化"简化为"离开 Superchain"。

必须覆盖：

- Base Stack / Azul 的核心变化：base-reth-node、base-consensus、hardfork activation、Engine API、release cadence、migration path；
- 与 OP Stack/Superchain 仍共享或仍相关的部分：bridge/settlement assumptions、governance/registry、interop、legacy compatibility、upstream reth/Kona/OP components；
- Top repo PR 是否显示 Base 正在加速独立 release、减少 OP Stack dependency、或者只是在特定层面 fork/overlay；
- 与 Optimism/OP Stack 的关系：技术分层、治理分层、生态分层和叙事分层；
- 对 Mantle 的含义：继续跟随 OP Stack、选择性移植 Base 能力、或自建 Mantle-specific stack 的决策边界；
- 强制 caveat：不得写成 Base 已完全脱离/退出 Superchain，除非有官方 primary source 明确支持。

- **Priority**: high
- **Dependencies**: item-4, item-5, item-6

### item-8: Beryl、预编译合约与资产发行/合规原语

如果 repo ranking 或 PR 分类显示 Beryl/预编译合约/资产发行相关 repo 或路径活跃，必须单独深挖；若活跃度不高，也应在叙事分析中说明其证据状态。该项需要严格区分 merged code、activation gate、testnet、mainnet-active 和 roadmap。

必须覆盖：

- Beryl 范围与状态：hardfork/spec 名称、目标网络、activation plan、已合并 PR、open PR、测试网/主网配置；
- Token Factory：功能边界、token 类型、权限模型、费用/registry、与 ERC-20/ERC-6909/ERC-721 等标准关系；
- Policy Registry：policy 注册、组合、校验路径、sender/recipient 或 issuer/operator 约束、失败语义、事件；
- 预编译合约设计：系统地址、ABI、gas pricing、状态存储、upgrade/hardfork gating、索引器/钱包兼容差异；
- Coinbase 生态意义：是否支撑合规资产发行、商户/钱包集成、稳定币/支付路线，还是仅为底层能力预留；
- 风险与开放问题：中心化策略、合规责任、wallet/indexer support、开发者采用门槛、流动性碎片化；
- 强制 caveat：未由 primary source 确认已激活的能力不得写成 launched/mainnet capability。

- **Priority**: high
- **Dependencies**: item-4, item-5, item-7

### item-9: 性能、Flashblocks、Multiproof 与 5K Peak TPS 叙事拆解

综合 Top repo 活动、Base 性能既有研究和公开资料，拆解 Base 的高性能、低延迟和安全/最终性叙事。必须区分公开性能声明、代码层优化、benchmark/load test、主网真实吞吐、用户感知延迟和最终性。

必须覆盖：

- 5K Peak TPS 或类似高吞吐口径的来源、日期、测试条件、交易类型、峰值/持续、final block TPS vs Flashblocks 预确认吞吐；
- 性能相关 PR 分类：builder separation、Flashblocks、state root/cached execution、DA/压缩、gas limit/tx cap、transaction pool、sequencer/consensus；
- 主网指标：近 30 天 TPS、gas/s、empty block、block gas utilization、blob/DA 使用；必须标注查询时间且 presentation 前需刷新；
- Flashblocks 当前状态：producer/consumer、WebSocket/P2P、pending RPC、rollup-boost、sub-block latency 口径；
- Multiproof 当前状态：TEE+ZK、AggregateVerifier、Proposer/Challenger/Registrar、withdrawal/finality window；
- 与 Mantle 对比：不能把 Base reported peak 直接等同于 Mantle 当前必须达到的 sustained TPS；区分 demand-bound 和 supply-bound；
- 强制 caveat：缺少官方 primary source 的 5K TPS 必须标为 reported/benchmark/roadmap，不得写成 confirmed sustained mainnet throughput；预确认不是最终性。

- **Priority**: high
- **Dependencies**: item-4, item-5, item-6

### item-10: Coinbase 生态绑定、产品化与叙事时间线

把 GitHub 活动与 Base/Coinbase 公开信息连接起来，分析 Base 是否正在从"L2 网络"转向"Coinbase 链上金融/应用平台底座"。该项需要分别处理事实集成和战略推断，避免把品牌背书等同于已上线产品深度集成。

必须覆盖：

- Base 官方 blog/docs、Coinbase developer/product 公告、Coinbase Wallet / Smart Wallet、Developer Platform、onramp/offramp、Commerce、Exchange/Custody、USDC/稳定币、identity/KYC 相关资料；
- Base 技术能力与生态入口的连接点：Beryl、paymaster/sponsorship、P256/passkey、Flashblocks UX、低成本/高吞吐、SDK/docs/examples；
- 叙事时间线：官方措辞是否从 OP Stack/低费 L2 转向 onchain economy、global onchain economy、Base Stack、Coinbase distribution、consumer/payments/commerce；
- 真实落地证据：product docs、SDK/API、partner docs、mainnet usage、合约/地址/交易增长；
- 代码活动如何支撑或削弱叙事：narrative-heavy、engineering-heavy、productized、roadmap-only 标签；
- 对 Mantle 的威胁：分发渠道、合规信任、稳定币入口、商户/消费者品牌认知、开发者增长；
- 不确定性：Coinbase 内部路线不可见，公开集成深度可能不足，监管/合规口径不可外推。

- **Priority**: high
- **Dependencies**: item-5, item-7, item-8, item-9

### item-11: 横向竞争定位与对 Mantle 的行动建议

将 Base 近期开发和叙事变化转化为 Mantle 可执行判断。结论必须分层：工程依赖、产品/生态、治理/安全、竞争叙事，而不是泛化建议。

必须覆盖：

- **必须跟踪 / 防守**：Top 活跃 repo watchlist、Base Stack release、Beryl activation、Flashblocks/Multiproof 状态、5K TPS 证据、Coinbase product integration；
- **值得借鉴 / POC**：repo activity dashboard、client/release packaging、precompile/asset issuance design review、Flashblocks UX POC、proof/finality communication、developer docs/SDK productization；
- **谨慎 / 不适合直接照搬**：完整复制 Base Stack、把 Coinbase 分发能力当作 Mantle 可复制资产、把 activation-gated code 当已上线能力、把 peak TPS 当 sustained target；
- **竞争叙事回应**：Mantle 如何解释自己与 Base 的差异：EigenDA/DA strategy、MNT gas/economics、EVM liquidity、OP Stack compatibility、ZK/OP Succinct 路线、企业/支付/隐私场景；
- **行动建议**：短期 PR watchlist 和 monthly dashboard，中期 architecture/feature POC，长期客户端/证明/资产发行/支付路线选择，以及需要 Mantle 工程团队验证的 blockers。

- **Priority**: high
- **Dependencies**: item-6, item-7, item-8, item-9, item-10

### item-12: 证据完整性、反例和风险控制

为 adversarial review 预留独立可检查的质量门。该项确保 final section 不会重复旧问题：预设 repo、只看 `base/base`、把 open PR 当完成、把叙事当事实、把 Base 独立化过度简化、把性能峰值当主网持续能力。

必须覆盖：

- 数据完整性：GitHub API/Search 是否漏页、rate limit、private repo 不可见、archived/fork 处理、PR Tracker 缺口；
- 结论反例：高活跃 repo 可能只是 docs/CI/deps；低活跃 repo 可能因成熟稳定但战略重要；monorepo PR 数可能掩盖子模块变化；
- 状态误读防线：open PR、merged PR、released code、testnet、mainnet-active、governance-approved、production-ready 必须分开；
- 叙事误读防线：官方叙事、Coinbase 产品资料、生态媒体、第三方评论、内部推断必须分层；
- Base/Mantle 比较防线：不可把 Base 技术独立等同于 Superchain 退出，不可把 Mantle fork 关系等同于自动继承 Base/OP roadmap；
- 输出：confidence/gaps 表和 "claims not supported" 列表，明确哪些说法最终稿不能写或只能低置信度写。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-7, item-8, item-9, item-10, item-11

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| repo_universe_record | repo/org 基础信息、纳入/排除理由、repo 类型、官方/半官方验证路径 | item-1 |
| activity_metrics | PR created/merged/closed、commit count、contributors、active weeks、release/tag、push recency、issue/discussion signal | item-2 |
| activity_score | 排序公式、权重、归一化值、rank、敏感性检查结果 | item-2 |
| pr_evidence | 代表 PR 的 number、title、state、date、author、changed paths、source URL、status | item-3, item-4, item-5 |
| classification_label | PR/变更所属开发方向分类，可多标签但必须说明主标签 | item-4, item-5 |
| implementation_status | spec / open-pr / merged-code / released / testnet / mainnet-active / feature-gated / roadmap / experimental / docs-only / inferred | item-4, item-5, item-7, item-8, item-9, item-10 |
| evidence_confidence | 证据置信度：primary-verified / cross-verified / code-observed / official-claim / tracker-assisted / inferred / unsupported | all |
| narrative_signal | 叙事标签、官方措辞、发布日期、对应 GitHub 证据、narrative-heavy 或 engineering-heavy 判断 | item-7, item-8, item-9, item-10 |
| op_stack_superchain_caveat | Base 与 OP Stack/Superchain 关系的分层表述及禁止过度外推事项 | item-7, item-12 |
| performance_caveat | peak vs sustained、benchmark vs mainnet、Flashblocks latency vs finality、metrics refresh requirement | item-9, item-12 |
| coinbase_linkage | 技术能力与 Coinbase product/channel/compliance/distribution 的连接点、证据和不确定性 | item-8, item-10 |
| mantle_implication | 对 Mantle 的威胁、借鉴价值、不可迁移约束、行动建议、owner/urgency | item-7, item-8, item-9, item-10, item-11 |
| gaps_and_risks | 数据缺口、反例、unsupported claims、需 presentation 前刷新或人工确认的事实 | item-12 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | table | Base 相关 org/repo universe 表：org、repo、类型、archived/fork、last pushed、primary language、纳入/排除理由 | markdown table | item-1 |
| diag-2 | ranked-table | Top repo 活跃度排行榜：repo、PR created/merged、commits、contributors、release signal、activity score、rank、deep-dive decision | markdown table | item-2 |
| diag-3 | timeline | Top repo 周度 PR created/merged 趋势，标注 release/announcement/major PR 峰值 | mermaid xychart or markdown table | item-3, item-6 |
| diag-4 | matrix | PR 分类矩阵：分类 x Top repo，填入 PR 数量、代表 PR、status、confidence | markdown table | item-4, item-5 |
| diag-5 | architecture | Base Stack / OP Stack / Superchain 分层关系图：客户端、协议、结算/桥、治理、生态叙事分别标注独立/共享/兼容/待验证 | mermaid flowchart | item-7 |
| diag-6 | timeline | Base 叙事演变时间线：Azul、Beryl、Flashblocks、Multiproof、Coinbase product/docs、performance claims，与 GitHub 活动互证 | mermaid timeline | item-8, item-9, item-10 |
| diag-7 | matrix | Mantle 竞争响应矩阵：威胁面、Base 证据、Mantle 当前状态、可行动作、优先级、风险 | markdown table | item-11 |
| diag-8 | evidence-map | 关键 claims 证据地图：claim、primary source、supporting source、status、confidence、不能写/需降级表述 | markdown table | item-12 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | github_org_data | `base`、`base-org` 及发现的相关 org 的 repo list、metadata、PR、commit、contributors、release/tag 原始查询结果，需记录查询时间和命令/API | 2 orgs plus discovered related orgs |
| src-2 | github_pr_analysis | Top 活跃 repo 的 PR/commit/release/spec 永久链接；每个 Top repo 至少 5 个代表 PR，若不足需说明 | 5 per Top repo |
| src-3 | official_base_docs | Base 官方 blog、docs、specs、release notes、dev notices，用于 Base Stack/Azul/Beryl/Flashblocks/Multiproof/开发者叙事验证 | 6 |
| src-4 | official_coinbase_sources | Coinbase 官方 product/developer docs、Wallet/Smart Wallet、Commerce、onramp/offramp、stablecoin、custody/identity 相关资料 | 4 |
| src-5 | internal_existing_research | 仓库内 Base Azul、Base 性能、Mantle Base codebase evaluation 相关 final sections；只能作为辅助背景并需重新验证时间敏感事实 | 6 |
| src-6 | pr_tracker | PR Tracker 每日跟踪报告，重点用于 `base/base` PR 摘要交叉验证；必须标注覆盖日期和与 GitHub 原始数据差异 | 1 series if accessible |
| src-7 | on_chain_and_benchmark_data | Base 主网/测试网指标、benchmark/load-test、TPS/gas/latency/blob utilization 数据；需区分 official claim、third-party dashboard 和 direct query | 3 |
| src-8 | comparison_sources | Optimism/OP Stack/Superchain 官方资料、Mantle 现有代码/研究、L2Beat 或其他 primary/near-primary 安全与架构资料，用于竞品与 Mantle 影响判断 | 4 |

## Quality Checklist

- [ ] `item-1` 和 `item-2` 在 draft 首部完成，且 final repo list 来自数据排序而非先验。
- [ ] 完整 repo universe、activity ranking、Top repo selection/exclusion 表均可复核。
- [ ] `base/base` 如被深挖，必须说明它在排名中的位置；如未被深挖，必须解释为何 PR Tracker 覆盖 repo 不在 Top。
- [ ] 每个重大 claim 都有 implementation_status 与 evidence_confidence。
- [ ] Beryl / Token Factory / Policy Registry 未经 primary source 确认激活时，只能写为 merged-code / feature-gated / roadmap / inferred。
- [ ] 5K Peak TPS 或类似性能 claim 必须区分 reported peak、benchmark、mainnet sustained、Flashblocks latency，并标注 metrics refresh requirement。
- [ ] OP Stack/Superchain 关系必须分层表述，不得写成 Base 已完全退出 Superchain，除非 primary source 明确支持。
- [ ] Coinbase 生态绑定必须区分 product docs、actual integration、strategic inference 和 marketing narrative。
- [ ] 对 Mantle 建议必须可执行，至少包含 watchlist、POC、不可照搬项和需要工程验证的 blockers。
- [ ] `claims not supported` / gaps 表必须列出 final 中不能写或需降级的说法。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create_outline | all | 根据用户更新后的研究方法重建 outline：先扫描 `base`、`base-org` 及发现的相关 org，按近 3 个月活跃度数据驱动选择 Top repo；取消旧 outline 对 `base/base` 的预设深挖前提 | Orchestrator dispatch comment 6e6c6efd-1124-4195-a15e-7548598e740d |
