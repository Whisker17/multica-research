---
topic: "Sui 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-sui"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/competitor-sui.md"
  draft: "202606-internal-sharing/research-sections/competitor-sui/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/competitor-sui/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  分析 Sui 在最近 3 个月的开发活动与市场/生态叙事变化。时间窗口固定为 2026-02-23 至
  2026-05-23，重点仓库为 `MystenLabs/sui`，需要覆盖 PR 活动趋势、主要开发方向与 PR 分类、
  重大功能变更与架构调整、开发节奏变化，以及 Sui 官方叙事在 gasless stablecoin payments /
  Fireblocks 支持、Move 生态扩展、支付/DeFi 发力、与其他 L1 差异化定位方面的变化。
  研究必须最终落到对 Mantle 的竞争启示：哪些变化会影响 Mantle 的支付、DeFi、企业/机构、
  开发者生态和 L1/L2 差异化叙事。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享的准备者、Mantle 协议和生态负责人、
  支付/DeFi/BD 团队，以及 Research Review Agent 和 Technical Writer。读者熟悉 L1/L2、
  Move/EVM、公链开发活动和稳定币支付概念，但不一定了解 Sui 近期 GitHub 具体 PR、对象模型
  演进、Sui Payments / gasless stablecoin transfers 的实现边界，或 Sui 对外叙事变化。

expected_output: |
  - 一份中文结构化 research section，能够直接支持内部分享材料
  - Sui 近 3 个月 GitHub 活动概况：PR 数量、合并/关闭趋势、主要贡献者/模块、热点标签或目录
  - PR 分类与开发重点变化：协议核心、共识/执行、对象/交易模型、Move/Framework、SDK/CLI/API、
    indexer/RPC、钱包/支付、DeFi/生态、安全/性能/测试/运维
  - 重大功能变更与架构调整清单：每项包含 PR/commit 链接、影响模块、用户/开发者影响和置信度
  - 叙事方向演变：gasless stablecoin payments / Fireblocks、Move 生态扩展、支付/DeFi、机构/托管、
    性能和与其他 L1 差异化
  - 与 Mantle 的竞争分析：威胁面、可借鉴设计、不可直接迁移约束、短中长期响应建议
  - 至少 3 张图表/表格：PR 活动时间线、开发方向分类矩阵、Sui vs Mantle 竞争启示矩阵

source_requirements_summary: |
  深度研究必须以 primary source 为主。GitHub 活动需直接查询 `MystenLabs/sui` PR / commit / release /
  milestone / label 数据，并记录查询时间、时间窗口、过滤条件和样本口径。叙事分析需优先引用
  Sui 官方 blog、Sui 官方文档、Mysten Labs / Sui Foundation 官方公告、Fireblocks 官方公告或文档。
  如使用 PR Tracker 每日跟踪报告，必须注明覆盖日期、采集口径和与 GitHub 直接查询的差异。
  既有 `sui-gasless-stablecoin-payments` 研究可作为前置材料，但任何易过期事实必须重新核验。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-23T10:33:58+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-23T10:33:58+08:00"

prerequisite_sections:
  - slug: sui-gasless-mechanism
    path: sui-gasless-stablecoin-payments/research-sections/sui-gasless-mechanism/final.md
    status: existing-research
  - slug: sui-payments-code-analysis
    path: sui-gasless-stablecoin-payments/research-sections/sui-payments-code-analysis/final.md
    status: existing-research
---

# Research Outline: Sui 近期开发与叙事分析

## Research Questions

1. 2026-02-23 至 2026-05-23 期间，`MystenLabs/sui` 的 PR 活动总量、合并节奏、活跃模块和开发者分布发生了什么变化？
2. 最近 3 个月的 PR 能否归纳出明确开发主线：协议核心、性能/可靠性、Move 生态、交易支付体验、SDK/API、DeFi/机构支付、基础设施运维分别占比如何？
3. 哪些 PR 或 release 代表重大功能变更或架构调整？这些变化对 validator、full node、indexer、钱包、支付应用、DeFi 协议和开发者工具各有什么影响？
4. Sui 对外叙事是否从高性能通用 L1 进一步转向支付、稳定币、托管机构接入、DeFi 流动性或 Move 开发者生态？证据来自哪些官方 blog、文档、合作公告和产品页？
5. Gasless stablecoin payments / Fireblocks 支持在 Sui 叙事中扮演什么角色？它是独立支付产品、机构托管入口、还是更广义 sponsored transaction / payments stack 的展示窗口？
6. Sui 与 Solana、Aptos、Base、Tempo、Canton 等替代方案的差异化定位是什么？这种定位对 Mantle 的 L2/支付/DeFi/企业业务叙事造成哪些压力？
7. Mantle 应如何响应：哪些 Sui 做法值得借鉴，哪些受 Move 对象模型或 L1 架构限制不能直接迁移，哪些方向应通过 Mantle 自身生态和 OP/EVM 兼容性形成反差？

## Items

### item-1: GitHub 活动基线与数据口径

建立近 3 个月 Sui 开发活动的事实底座。研究需直接查询 `MystenLabs/sui` 在 2026-02-23 至 2026-05-23 的 PR 数据，明确 open / merged / closed 口径、默认分支、bot PR 是否纳入、draft PR 是否纳入、backport/revert/dependabot 是否单独标注。输出应包含每周 PR 数、merged PR 数、平均 merge latency、主要作者/reviewer、主要 touched directory、release tag 或 milestone 对应关系，并与 PR Tracker 每日跟踪报告交叉核验（如果 PR Tracker 覆盖该窗口）。

必须覆盖：

- GitHub 查询方法：REST / GraphQL / gh CLI / BigQuery / PR Tracker 的具体过滤条件；
- 时间窗口固定为 2026-02-23 至 2026-05-23，避免使用模糊的"最近"；
- PR 分类原始表：PR number、title、state、created/merged/closed date、author、labels、files changed、directory bucket、summary、source URL；
- 数据清洗规则：排除或单列依赖更新、CI、release/backport、文档、自动格式化、大规模重命名；
- 置信度说明：GitHub API 限制、squash merge、跨 repo 依赖、private work 不可见、PR Tracker 覆盖缺口。

- **Priority**: high
- **Dependencies**: none

### item-2: PR 分类体系与开发方向分布

把原始 PR 数据转化为可用于内部分享的开发方向图谱。研究需建立互斥或可多选的分类体系，并解释每类对 Sui 产品/协议演进的意义，而不是只列 PR 标题。

建议分类：

- **协议核心 / 对象与交易模型**：transaction data、object runtime、protocol config、epoch / system state、storage rebate、gasless / sponsored tx；
- **共识 / 执行 / 性能可靠性**：validator、consensus adapter、checkpoint、authority、execution engine、parallelism、latency、crash recovery；
- **Move 与 Framework**：Move VM、Sui framework、Move package/tooling、standard library、address balance / coin / funds accumulator；
- **API / SDK / CLI / 开发者体验**：TypeScript/Rust SDK、GraphQL/gRPC/JSON-RPC、CLI、wallet adapter、examples、docs；
- **Indexer / RPC / Data / Observability**：indexer schema、event ingestion、metrics、tracing、archival/analytics、full node ops；
- **支付 / 稳定币 / DeFi 相关**：gasless stablecoin transfers、address balances、payments docs、coin/balance APIs、partner integration hooks；
- **安全 / 测试 / 审计 / 运维**：fuzzing、formal checks、load test、CI、dependency security、incident hardening；
- **生态和产品支持**：wallet, explorer, bridge, zkLogin/passkey, app-facing features。

每类需要给出 PR 数量/占比、代表 PR、变化趋势、工程意图推断和对开发者/用户的可见影响。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 重大功能变更与架构调整

从 PR 分类中筛出真正影响架构、协议行为、开发者接口或生态叙事的变化。每个重大变更必须提供 PR/commit/release evidence，说明该变更是已合并、已发布、feature-gated、测试中还是仅为重构准备。

重点检查：

- gasless stablecoin transfers、sponsored transaction、address balance、payments 相关 protocol config / validation / SDK / docs 变化；
- Move / Framework 新能力或 breaking changes，包括 coin/balance/funds accumulator、package upgrade、object / type system 相关改动；
- execution / consensus / checkpoint / authority / storage 方向的性能和可靠性优化；
- GraphQL/gRPC/JSON-RPC、indexer、wallet/developer tooling 的接口变更；
- validator/full node 运维和 observability 的可见变化；
- 安全边界调整：签名验证、transaction checks、deny list、rate limiter、abuse control、feature flag；
- release notes 与 PR 之间的对应关系：哪些 PR 最终形成官方对外发布叙事，哪些只是内部工程债治理。

输出应包含"重大变更表"：变更名、PR/commit、目录、类型、状态、影响对象、叙事含义、风险/限制、证据链接、置信度。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 开发活跃度趋势与工程组织信号

分析 Sui 近期开发节奏是否加快、收敛、转向或进入稳定维护。研究不只统计 PR 数，还要看工作流质量和工程组织信号。

必须覆盖：

- 每周 PR created / merged / closed 趋势，以及是否存在 release 前后峰值；
- merge latency、review 密度、large PR 占比、revert/backport/hotfix 占比；
- 活跃贡献者/团队集中度：是否由核心 Mysten/Sui 工程师主导，外部贡献者是否有实质比例；
- 模块集中度：热点目录是否集中在 protocol / core / framework / payments / SDK / indexer；
- 开发节奏与官方叙事事件的关系：例如 gasless stablecoin announcement 前后是否有对应代码/文档 PR；
- 与 Mantle 工程节奏可比较的指标：核心协议变更频率、developer tooling 投入、支付/DeFi 产品化投入。

结论要区分"高 PR 数"与"高协议创新强度"。文档、CI 和小修 PR 不能简单等同于战略性开发投入。

- **Priority**: medium
- **Dependencies**: item-1, item-2

### item-5: Gasless Stablecoin Payments / Fireblocks 叙事与实现边界

单独分析 Sui 近期最明确的支付叙事：gasless stablecoin payments 以及 Fireblocks 支持。该 item 应复用既有 `sui-gasless-stablecoin-payments` final sections，但必须重新核验 2026-05-23 时点的官方 docs、blog、源码和合作方公告。

必须覆盖：

- Sui 官方如何表述 gasless stablecoin transfers：free tier、eligible stablecoin allowlist、PTB shape、rate limit、congestion priority、SDK 自动检测；
- Fireblocks 支持的公开证据：Sui 官方 blog、Fireblocks 官方文档/公告、custody/signing/policy/API 支持边界；
- 支付产品定位：这是对普通用户免 SUI 转账、机构托管接入、merchant payments、还是更大 Sui Payments stack 的入口；
- 实现边界：gasless stablecoin transfer 不等于任意 Sui transaction 免费，也不等于 Fireblocks 自动处理所有 sponsorship；
- 与 Sui PR 活动的对应：近期 PR 是否在 protocol config、gasless validation、rate limiter、SDK、docs、payments page 或 tests 上支撑该叙事；
- 对 Mantle 的启示：paymaster / gas sponsorship、稳定币支付 UX、商户 SDK、托管平台集成、无 gas onboarding。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-6: Move 生态扩展与开发者叙事变化

评估 Sui 是否在近期强化 Move 生态和开发者体验，而不只是推广支付。研究需把 Move 语言/Framework、SDK/API、wallet/zkLogin/passkey、docs/examples、生态 grants 或 hackathon 等材料与 GitHub PR 活动相互印证。

必须覆盖：

- Move / Sui Framework 近期新增或强化的能力；
- 开发者工具链：CLI、package management、testing、localnet、SDK、GraphQL/gRPC、docs examples；
- 钱包和用户身份体验：zkLogin、passkey、sponsored/gasless flows、wallet adapter；
- Sui 与 Aptos Move 的差异化叙事：对象模型、parallel execution、owned/shared objects、PTB、address balances；
- 官方生态叙事：Sui blog、developer relations、events、grant / ecosystem announcement；
- 对 Mantle 的竞争含义：Move 开发者心智、非 EVM 应用范式、对象模型对支付/游戏/DeFi 的表达优势与迁移成本。

- **Priority**: medium
- **Dependencies**: item-2, item-3

### item-7: 支付 / DeFi 方向发力与生态证据

把官方叙事和 GitHub PR 映射到具体支付/DeFi 业务方向，避免只停留在技术机制。研究要区分链本身能力、生态应用增长和合作方营销。

必须覆盖：

- Sui Payments、stablecoin transfers、address balances、sponsored tx、wallet/custodian integration 对支付场景的组合价值；
- DeFi 相关生态证据：DEX、lending、liquid staking、stablecoin liquidity、RWA/treasury、bridge/interop、TVL/volume 等可核验指标；
- 支付/DeFi 相关 PR 是否集中在 core protocol、framework、SDK、indexer、docs 或 ecosystem examples；
- 与 Tempo、Solana、Base、Canton 等支付/机构方向方案的差异：Sui 是通用高性能 L1 上的支付 UX 优化，而非支付专用链或企业许可网络；
- 风险：gasless path 很窄、Fireblocks 能力边界需确认、稳定币流动性和法币出入金仍依赖外部伙伴、DeFi 指标可能受激励影响。

- **Priority**: high
- **Dependencies**: item-3, item-5, item-6

### item-8: 竞品定位：Sui 与其他 L1/L2/支付链的差异化

建立横向竞争框架，解释 Sui 的差异化不是单点功能，而是对象模型、高性能 L1、Move、gasless/sponsored UX、机构托管合作和生态叙事的组合。

比较对象至少包括：

- **Mantle / Ethereum L2**：EVM 兼容、以太坊安全与流动性、L2 成本结构、paymaster/AA 可实现路径；
- **Solana**：高吞吐通用 L1、支付/DePIN/consumer 心智、低费用但 gas 抽象不同；
- **Aptos**：Move 生态近邻、并行执行、机构/支付叙事相似点；
- **Base**：Coinbase 分发、USDC/商户/consumer apps、EVM 生态和账户抽象；
- **Tempo**：支付优先 L1、稳定币 gas、Payment Lane、机构支付叙事；
- **Canton / Fireblocks 类机构基础设施**：合规、托管、机构工作流，而非开放 DeFi L1。

对比维度：

- 开发活动强度与协议变更速度；
- 支付 UX：gasless / sponsored / stablecoin gas / paymaster；
- 开发者生态：Move vs EVM、SDK/API、工具链、迁移成本；
- DeFi 流动性和分发；
- 机构/托管/合规合作；
- 性能、最终性、费用可预测性；
- 对 Mantle 可复制性、不可复制性和可反向定位点。

- **Priority**: high
- **Dependencies**: item-5, item-6, item-7

### item-9: 对 Mantle 的竞争启示与响应建议

把 Sui 近期开发和叙事变化转化为 Mantle 可执行判断。输出不应只是"关注 Sui"，而要按产品、工程、生态和叙事给出优先级。

必须覆盖四类结论：

1. **威胁面**：
   - Sui 用 gasless stablecoin transfer 降低支付 onboarding 摩擦；
   - Fireblocks/托管合作增强机构可用性叙事；
   - Move 对象模型和 PTB 对支付/游戏/DeFi 组合体验有独特表达；
   - 高频 GitHub 活动可能强化"快速演进 L1"印象。
2. **Mantle 可借鉴**：
   - stablecoin payment UX、paymaster/gas sponsorship、merchant SDK、memo/reconciliation；
   - SDK/API 层自动识别支付路径并隐藏 gas；
   - 以官方 blog + docs + code PR 串联叙事，而不是只发布合作公告；
   - PR 活动分类和 release note 机制可用于对外展示工程势能。
3. **不可直接迁移**：
   - Move 对象模型、Sui gasless validation、address balance 机制与 EVM/OP Stack 并不一一对应；
   - L2 的 gas economics、sequencer、paymaster、ERC-20/4337 约束不同；
   - Fireblocks 支持 Sui 不等于可复用为 Mantle 支付产品优势。
4. **路线建议**：
   - 短期：Mantle stablecoin payment demo / paymaster UX / merchant SDK / Fireblocks 或托管平台接口盘点；
   - 中期：payment-specific transaction path、AA/paymaster 标准化、stablecoin fee abstraction、DeFi liquidity routing；
   - 长期：企业/机构支付叙事与 EVM 兼容优势结合，形成与 Sui/Tempo/Canton 不同的"Ethereum-aligned payments and DeFi settlement layer"定位。

- **Priority**: high
- **Dependencies**: item-5, item-7, item-8

### item-10: 风险、开放问题与事实核验清单

集中列出 deep draft 必须显式标注的 caveats，避免内部分享把初步信号写成确定事实。

必须核验：

- 2026-02-23 至 2026-05-23 PR 总量和分类是否受 bot/backport/release PR 扭曲；
- PR Tracker 是否覆盖 Sui、覆盖日期是否完整、与 GitHub 原始数据差异多大；
- Sui 官方 blog 中 gasless stablecoin / Fireblocks 公告的发布日期、措辞和支持边界；
- Fireblocks 是否有独立官方资料确认 Sui 支持范围、gasless support、PTB policy inspection 或 sponsor signing；
- Sui docs/source 中 allowlisted stablecoin、minimum amount、rate limit、gasless_max_tps、SDK transport 的最新状态；
- 是否存在近期安全事故、性能退化、validator incident、major revert 或 controversial PR；
- DeFi/TVL/volume 指标来源和激励口径；
- 与 Mantle 对比时避免把 L1 和 L2 的最终性、费用、信任边界和流动性条件混为一谈。

- **Priority**: medium
- **Dependencies**: item-1, item-3, item-5, item-7, item-8

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| source_anchor | 每个关键论断对应的 primary source：GitHub PR/commit/release、Sui docs/blog、Fireblocks docs/blog、PR Tracker 条目或链上/生态数据来源 | all |
| data_window | 数据时间窗口、查询时间、过滤条件、是否纳入 bot/backport/release/docs PR | item-1, item-2, item-4 |
| pr_metadata | PR number、title、state、created/merged/closed date、author、labels、files changed、touched directories、linked issue/release | item-1, item-2, item-3 |
| category | PR 或叙事材料所属开发方向：protocol、consensus/execution、Move/framework、SDK/API、indexer/RPC、payments/DeFi、security/testing、docs/ecosystem | item-2, item-3 |
| impact_scope | 影响对象：validator、full node、indexer、wallet、SDK、app developer、DeFi protocol、custodian、end user、Mantle strategy | item-3, item-5, item-6, item-7, item-9 |
| narrative_claim | 官方或合作方对外叙事主张、发布日期、目标受众、与代码/文档 evidence 的对应关系 | item-5, item-6, item-7, item-8 |
| implementation_status | merged、released、feature-gated、testnet-only、docs-only、experimental、inferred、not-found-after-search | item-3, item-5, item-6, item-7 |
| competitive_signal | 对 Mantle 构成的威胁、可借鉴点、不可迁移约束或差异化机会 | item-8, item-9 |
| confidence | 高 / 中 / 低；高=GitHub/source/docs 交叉验证，中=官方公告但实现细节有限，低=第三方报道或合理推断 | all |
| caveat | 数据缺口、口径限制、过期风险、冲突来源、需要后续验证的问题 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | timeline | 2026-02-23 至 2026-05-23 Sui PR 活动时间线：每周 created/merged PR、release/event/blog 标记、重大 PR 标注 | mermaid or ascii | item-1, item-4 |
| diag-2 | comparison | Sui PR 开发方向分类矩阵：类别、PR 数/占比、代表 PR、影响对象、叙事含义 | mermaid or markdown table | item-2, item-3 |
| diag-3 | flow | Gasless stablecoin payments 从 wallet/custodian 到 validator admission 的端到端流程，并标注 Fireblocks/Gas Station 可能位置和实现边界 | mermaid sequenceDiagram | item-5 |
| diag-4 | comparison | Sui vs Mantle/Base/Solana/Aptos/Tempo/Canton 竞争定位矩阵：支付 UX、开发者生态、机构合作、费用/最终性、可迁移性 | markdown table | item-8 |
| diag-5 | decision | Mantle 响应路线图：短期 UX/SDK，中期 paymaster/payment path，长期机构支付与 EVM-aligned DeFi settlement 定位 | mermaid flowchart | item-9 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | github_pr_data | `MystenLabs/sui` 2026-02-23 至 2026-05-23 PR 原始数据，必须包含查询方法、过滤条件和可复现导出；必要时附 GitHub search/API query。 | 1 dataset |
| src-2 | github_pr_samples | 每个主要开发类别至少引用代表性 PR / commit / release note，重大结论必须给出 PR number 和 URL。 | 20 |
| src-3 | official_blog | Sui / Mysten Labs / Sui Foundation 官方 blog 或公告，覆盖 gasless stablecoin payments、Fireblocks、Move/ecosystem、DeFi/payments narrative。 | 4 |
| src-4 | official_docs | Sui 官方文档，至少覆盖 sponsored transactions、gasless stablecoin transfers、payments/address balances、Move/Framework、SDK/API。 | 5 |
| src-5 | source_code | `MystenLabs/sui` 源码或 release tag，对重大协议/validation/API claims 做代码级验证；记录 commit hash。 | 5 |
| src-6 | partner_docs | Fireblocks 官方文档/公告/API 资料，确认 Sui custody/signing/policy/gasless/payment support 的实际边界。 | 1 |
| src-7 | pr_tracker | PR Tracker 每日跟踪报告；若未覆盖 Sui 或覆盖不足，需在 draft 中写明 not found / insufficient coverage。 | 0 |
| src-8 | ecosystem_data | DeFi/payment 生态数据来源，如 DefiLlama、SuiVision、SuiScan、Artemis、官方 ecosystem pages；必须注明访问日期和指标口径。 | 3 |
| src-9 | comparative_sources | Mantle/Base/Solana/Aptos/Tempo/Canton 的官方或既有研究资料，用于横向竞争定位；避免只用二级媒体。 | 5 |
| src-10 | internal_research | 复用 `sui-gasless-stablecoin-payments` 既有 final sections 和 202606 内部分享相关 enterprise/payment 研究，作为前置材料但不得替代最新核验。 | 2 |

## Evidence Starting Points

- GitHub: `MystenLabs/sui` pull requests, commits, releases, tags, labels, milestones, changed files.
- Sui docs: Sponsored Transactions, Gasless Stablecoin Transfers, Sui Payments / Address Balances, PTB builder, Move / Sui Framework docs.
- Sui official blog: gasless stablecoin transfers with Fireblocks support; payments, DeFi, Move ecosystem, performance or developer announcements in the 2026-02-23 to 2026-05-23 window.
- Fireblocks official docs/blog/API pages: Sui asset/custody/signing/policy support and any gasless/payment-specific material.
- Existing internal research:
  - `sui-gasless-stablecoin-payments/research-sections/sui-gasless-mechanism/final.md`
  - `sui-gasless-stablecoin-payments/research-sections/sui-payments-code-analysis/final.md`
  - `202606-internal-sharing/outlines/payment-tempo.md`
  - `202606-internal-sharing/outlines/enterprise-canton.md`

## Draft Structure Recommendation

1. Executive summary: Sui 最近 3 个月开发活动和叙事变化的一句话判断。
2. GitHub activity snapshot: 数据口径、趋势、模块分布、代表 PR。
3. Development focus map: PR 分类和重大功能/架构变化。
4. Narrative evolution: gasless stablecoin / Fireblocks、Move、payments/DeFi、institutional positioning。
5. Competitive comparison: Sui vs Mantle / Base / Solana / Aptos / Tempo / Canton。
6. Mantle implications: threat, borrow, avoid, response roadmap。
7. Evidence appendix: PR dataset summary、source list、confidence/caveats。

## Quality Checklist

- [ ] 明确使用 2026-02-23 至 2026-05-23 作为 GitHub 活动窗口。
- [ ] 直接查询 `MystenLabs/sui` PR 数据，并说明过滤条件与数据口径。
- [ ] PR 分类有数量/占比/代表 PR，不只靠主观描述。
- [ ] 重大功能变更均有 PR/commit/release 或 source-code evidence。
- [ ] Gasless stablecoin / Fireblocks 叙事与实现边界清楚区分，未证实能力标为待验证。
- [ ] 至少引用 Sui 官方 blog、Sui docs、MystenLabs/sui source、Fireblocks official source。
- [ ] 若 PR Tracker 未覆盖或覆盖不足，明确写 not found / insufficient coverage。
- [ ] 对 Mantle 的启示包含可借鉴、不可迁移、短中长期建议。
- [ ] 包含至少 3 张图表/表格，并可被 Technical Writer 直接转化为汇报材料。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
