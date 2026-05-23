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
  以 2026-02-23 至 2026-05-23 为固定窗口，研究 Sui 近期开发活动与对外叙事变化。研究必须严格
  按三步执行：第一步先扫描 MystenLabs GitHub Organization 下全部公开 repo，并在发现 Sui
  Foundation、SuiNS、MoveBit/Sui 相关官方或半官方组织等相关 org 时记录纳入/排除理由，按近 3 个月
  PR 数量、commit 频率、活跃 contributor、recent release/tag、issue/discussion 信号等指标排序，数据驱动
  选出 Top 活跃 repo；第二步只针对第一步筛出的活跃 repo 做 PR 活动和开发方向分析；第三步再结合
  GitHub 活动、Sui 官方 blog/docs、PR Tracker 每日跟踪报告和合作方公告分析叙事变化与对 Mantle 的竞争启示。
  不得预设只分析 `MystenLabs/sui`，也不得在完成 repo 活跃度扫描前直接下结论。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享的准备者、Mantle 协议/生态/支付/BD 团队、
  Research Review Agent 和 Orchestrator。读者熟悉 L1/L2、Move/EVM、公链开发活动和稳定币支付概念，
  但需要一份可复核、数据驱动的 Sui 近期开发重点与竞争叙事判断。

expected_output: |
  - 一份中文结构化 research section，可直接支持内部分享材料
  - MystenLabs 及必要相关 org 的活跃 repo 排名表，明确数据口径、排序公式、Top repo 选择阈值和排除项
  - Top 活跃 repo 的 PR 活动分析：开发方向分类、重大功能/架构变化、周度趋势、贡献者/模块集中度
  - Sui 近期叙事演变：新功能发力点、生态战略调整、支付/DeFi/Move/机构方向证据链
  - 横向竞争分析：Sui 相对 Mantle、Solana、Aptos、Base、Tempo、Canton 等方案的差异化定位
  - 对 Mantle 的竞争启示：威胁面、可借鉴设计、不可迁移约束、短中长期响应建议
  - 至少 4 个表/图：repo 活跃度排名、PR 活动时间线、开发方向分类矩阵、Sui vs Mantle 竞争启示矩阵

source_requirements_summary: |
  Deep phase 必须优先使用 primary source。GitHub 活动需通过 GitHub REST/GraphQL/gh CLI 或可复核导出直接查询
  MystenLabs 全 org repo 列表、PR、commit、contributor、release/tag 和 touched files，并记录查询时间、时间窗口、
  排序公式、rate limit/分页处理和样本排除规则。叙事分析需优先引用 Sui 官方 blog、Sui 官方 docs、
  Mysten Labs / Sui Foundation 公告、相关合作方官方公告或文档；PR Tracker 每日跟踪报告只能作为辅助交叉验证，
  必须标注覆盖日期、口径与 GitHub 原始数据差异。任何二手媒体或社区帖必须降级为补充信号。

methodology_gate:
  repo_discovery_first: true
  prohibition: "不得预设只分析 MystenLabs/sui；不得在完成 org-wide repo 活跃度排序前决定最终分析 repo 列表。"
  time_window: "2026-02-23 至 2026-05-23"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-23T22:50:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-23T22:50:00+08:00"
---

# Research Outline: Sui 近期开发与叙事分析

## Methodology Gate

Deep draft 开始前必须先完成 `item-1` 与 `item-2` 的 repo discovery / ranking，并把结果写入草稿的第一部分。只有在 repo 活跃度排名表完成后，才能确定后续 PR 深挖对象。若 `MystenLabs/sui` 排名第一，也必须证明这一结论来自 org-wide 数据，而不是先验假设；若其他 repo 活跃度接近或在特定维度更高，必须纳入 Top repo 分析或明确排除理由。

最低执行要求：

- 扫描 `MystenLabs` 全部公开 repo，不只查询 `sui`。
- 对 archived、fork、template、sample、website/docs、SDK、app、infra、research、ecosystem 工具类 repo 分别标注类型。
- 统计 2026-02-23 至 2026-05-23 的 PR created、PR merged、commit count、active contributors、release/tag、default branch push、issues/discussions 活跃度。
- 形成可复核排序公式，建议基础权重：merged PR 35%、PR created 20%、commit count 20%、active contributors 15%、release/tag/default-branch push recency 10%；如调整权重必须解释。
- 选择 Top 5-8 活跃 repo 作为候选，最终深挖数量可按数据分布收敛到 Top 3-5，但必须保留完整排名附录。
- 如果发现 `sui-foundation`、`SuiNS`、`suinetwork`、官方 docs/SDK/生态工具迁移到其他 org，需记录发现路径、验证依据和纳入/排除理由。

## Research Questions

1. 近 3 个月内，MystenLabs org 下哪些 repo 最活跃？排名依据是什么，Top repo 是否只有 `MystenLabs/sui`，还是 SDK、docs、wallet、apps、infra、research 工具等 repo 也显示出显著投入？
2. Top 活跃 repo 的开发活动分别指向哪些主线：协议核心、共识/执行、Move/Framework、SDK/API、indexer/RPC、钱包/支付、DeFi/生态、基础设施/运维、文档/开发者教育？
3. 这些 repo 的 PR 活动在 2026-02-23 至 2026-05-23 是否出现方向变化、release 前后峰值、贡献者集中或跨 repo 协同？
4. 哪些 PR、release、commit 或 docs 变化代表重大功能变更、架构调整或产品化推进？它们处于已合并、已发布、feature-gated、实验中还是文档/叙事先行状态？
5. Sui 近期对外叙事是否从高性能通用 L1 转向更明确的支付、稳定币、DeFi、机构托管、Move 开发者体验、consumer apps 或 infra reliability？证据来自哪些官方资料与代码活动？
6. Gasless stablecoin payments、Fireblocks 支持、Move 对象模型、PTB、address balance、zkLogin/passkey、SDK/API 等近期信号分别如何支撑或限制 Sui 的叙事？
7. Sui 与 Mantle、Solana、Aptos、Base、Tempo、Canton 等竞争方案相比，差异化定位是什么？Mantle 应如何响应，哪些做法值得借鉴，哪些因 L1/Move 架构差异不可直接迁移？

## Items

### item-1: Org 与 repo universe 发现

建立研究对象边界。该项不是分析 `MystenLabs/sui`，而是先发现 Sui 相关代码资产分布。必须从 GitHub API/gh CLI 拉取 `MystenLabs` org 全部公开 repo，并补充搜索与官方链接验证是否存在相关 org 或 repo 迁移。

必须覆盖：

- `MystenLabs` 全 repo 清单：repo name、URL、description、archived/fork/private visible 状态、default branch、primary language、stars/forks、created/updated/pushed_at；
- repo 类型标注：core protocol、Move/framework、SDK、wallet/app、indexer/data、docs/website、infra/devops、research/benchmark、example/demo、deprecated/archive；
- 相关 org 发现：从 Sui 官网、docs、GitHub topics、package metadata、official blog links、repo README links、Sui Foundation assets 搜索是否还有官方/半官方 repo；
- 纳入/排除规则：archived repo 默认排除活跃排序但保留清单；fork repo 单列；纯 website/docs 不能直接等同协议开发但可用于叙事/开发者投入分析；
- 输出完整 repo universe 表，作为后续 ranking 的输入。

- **Priority**: high
- **Dependencies**: none

### item-2: 近 3 个月 repo 活跃度排名与 Top repo 选择

对 `item-1` 的 repo universe 做数据驱动排序，决定后续 PR 深挖对象。该项是整个研究的硬门槛，deep draft 不得跳过。

必须覆盖：

- 时间窗口固定为 2026-02-23 至 2026-05-23，所有查询使用 UTC 日期并说明边界是否含首尾日；
- 每个 repo 的 PR created、PR merged、PR closed、commit count、active contributors、default branch pushes、release/tag 数、recent issue/discussion activity；
- 排序公式和权重；至少给出总分、各指标原始值、归一化值、rank；
- 噪声处理：dependabot/renovate、release/backport、bot-generated docs、large generated files、archived/fork repo；
- Top repo 选择规则：建议 Top 5-8 候选，若数据长尾明显可选 Top 3-5 深挖；所有排除的高分 repo 需解释；
- 排名结果的敏感性检查：用 PR-only、commit-only、contributors-only 三种视角复核，防止单一指标误导；
- 如果 `MystenLabs/sui` 是第一名，仍需展示其他 repo 的相对活跃度；如果其他 repo 在 SDK/docs/wallet 等维度突出，必须纳入对应分析。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Top repo PR 活动基线与数据表

针对 `item-2` 选出的 Top repo，建立 PR 级事实底座。输出需要支持可复核分析，而不是只汇总结论。

必须覆盖：

- 每个 Top repo 的 PR 原始表：repo、PR number、title、state、created_at、merged_at/closed_at、author、is_bot、labels、milestone、changed files、additions/deletions、touched directories、review count、source URL；
- 每周 PR created / merged / closed 趋势；
- merge latency、large PR 占比、revert/backport/hotfix/release PR 占比；
- contributor 分布：核心 Mysten/Sui 工程师、外部贡献者、bot、生态合作方；
- 跨 repo 协同：同一功能是否同时触达 core repo、SDK、docs、wallet、indexer 或 examples；
- GitHub API 限制、squash merge、force push、monorepo 子目录归类和 private work 不可见等 caveats。

- **Priority**: high
- **Dependencies**: item-2

### item-4: PR 分类体系与开发方向分布

把 Top repo 的 PR 数据转化为开发方向图谱。分类应允许按 repo 类型适配，但必须能跨 repo 对比。

建议分类：

- **协议核心 / 对象与交易模型**：transaction data、object runtime、protocol config、epoch/system state、storage rebate、gasless/sponsored tx；
- **共识 / 执行 / 性能可靠性**：validator、consensus adapter、checkpoint、authority、parallel execution、latency、crash recovery；
- **Move / Framework / Package**：Move VM、Sui framework、standard library、package upgrade、coin/balance/funds accumulator；
- **API / SDK / CLI / 开发者体验**：TypeScript/Rust SDK、GraphQL/gRPC/JSON-RPC、CLI、wallet adapter、examples、docs；
- **Indexer / RPC / Data / Observability**：indexer schema、event ingestion、metrics、tracing、archive/analytics、full node ops；
- **钱包 / 支付 / 稳定币 / DeFi**：gasless stablecoin transfers、address balances、sponsored tx、payments docs、coin/balance APIs、partner integration hooks；
- **安全 / 测试 / 审计 / 运维**：fuzzing、formal checks、load test、CI、dependency security、incident hardening；
- **生态产品与叙事支持**：explorer、bridge、zkLogin/passkey、consumer app support、developer education。

每类需要给出 PR 数量/占比、代表 PR、repo 分布、趋势变化、工程意图推断、用户/开发者可见影响和置信度。

- **Priority**: high
- **Dependencies**: item-3

### item-5: 重大功能变更与架构调整

从分类结果中筛出真正影响协议行为、架构、开发者接口、支付/DeFi 能力或生态叙事的变化。每个重大变更必须有 PR/commit/release/docs evidence。

重点检查：

- gasless stablecoin transfer、sponsored transaction、address balance、payments 相关 protocol config、validation、SDK、docs、rate limit 或 monitoring 变化；
- Move / Framework 新能力或 breaking changes：coin/balance/funds accumulator、package upgrade、object/type system、PTB；
- consensus / checkpoint / authority / storage / execution 性能可靠性变化；
- GraphQL/gRPC/JSON-RPC、indexer、wallet/developer tooling 的接口变更；
- validator/full node 运维、observability、release process 和安全边界调整；
- 跨 repo 功能链：core PR 是否配套 SDK/docs/wallet/indexer PR；
- 状态判断：已合并、已发布、feature-gated、测试中、文档先行或仅为重构准备。

输出"重大变更表"：变更名、repo、PR/commit/release、目录、类型、状态、影响对象、叙事含义、风险/限制、证据链接、置信度。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: 开发活跃度趋势与工程组织信号

判断 Sui 近期是协议创新加速、产品化推进、维护稳定、release 收敛，还是多 repo 协同转向。不能只把 PR 数量等同于战略投入。

必须覆盖：

- Top repo 每周活动趋势、release/tag 前后峰值、issue/discussion 变化；
- merge latency、review 密度、large PR、revert/backport/hotfix、test-only/docs-only PR 占比；
- contributor 集中度：核心团队 vs 外部贡献者；是否出现新团队或合作方参与；
- 模块集中度：热点目录是否集中在 protocol/core/framework/payments/SDK/indexer/docs；
- 跨 repo 节奏：重大功能是否从 core 到 SDK/docs/wallet 形成产品化链条；
- 与官方叙事事件的时间关系：blog/announcement 前后是否有代码和文档支撑；
- 对 Mantle 可比指标：核心协议变更频率、developer tooling 投入、支付/DeFi 产品化投入、生态工具维护。

- **Priority**: medium
- **Dependencies**: item-3, item-4, item-5

### item-7: Sui 官方叙事与公开信息时间线

建立 2026-02-23 至 2026-05-23 的对外叙事时间线，并与 GitHub 证据交叉映射。

必须覆盖：

- Sui 官方 blog、Sui docs、Mysten Labs / Sui Foundation 公告、developer updates、release notes；
- 合作方官方资料：Fireblocks、wallet/custody、stablecoin、DeFi、infra、developer tooling 合作；
- PR Tracker 每日跟踪报告（如覆盖）：使用覆盖日期、摘要标签和 GitHub 原始数据交叉验证，不把 tracker 当 primary source；
- 叙事标签：payments/stablecoin、DeFi/liquidity、Move developer ecosystem、consumer apps/gaming、institutional custody、performance/reliability、security、AI/agent commerce（若有）；
- 每个叙事事件对应的代码活动：repo/PR/docs/release 是否支撑，还是纯营销/合作公告；
- 易过期事实的验证日期，特别是 gasless stablecoin support、Fireblocks support、mainnet feature status 和 docs 参数。

- **Priority**: high
- **Dependencies**: item-2

### item-8: 支付、稳定币与机构托管叙事的代码支撑

单独分析 Sui 近期最明确的支付/机构化叙事，并严格区分功能范围和营销说法。

必须覆盖：

- gasless stablecoin transfers 的官方表述：eligible stablecoin、free tier、PTB shape、rate limits、congestion priority、SDK 自动检测、sponsorship 边界；
- Fireblocks 支持的公开证据：Sui 官方 blog、Fireblocks 官方 docs/announcement、custody/signing/policy/API 支持边界；
- 代码支撑：Top repo 中是否有 protocol config、gasless validation、rate limiter、SDK、wallet、docs、payments page、tests 或 monitoring PR；
- 产品定位：普通用户免 SUI 转账、机构托管入口、merchant payments、developer onboarding，还是 Sui Payments stack 的一部分；
- 边界说明：gasless stablecoin transfer 不等于任意 Sui transaction 免费；Fireblocks 支持 Sui 不等于自动 sponsor 所有交易；
- 对 Mantle 的启示：paymaster/gas sponsorship、稳定币支付 UX、商户 SDK、memo/reconciliation、托管平台集成、无 gas onboarding。

- **Priority**: high
- **Dependencies**: item-5, item-7

### item-9: Move 生态、开发者体验与应用范式叙事

评估 Sui 是否通过 Move、对象模型、PTB、SDK/API、wallet/identity 和 docs/examples 强化开发者生态，而不只是推广支付。

必须覆盖：

- Move / Sui Framework 近期新增或强化能力；
- CLI、package management、testing、localnet、SDK、GraphQL/gRPC、docs examples、starter kits；
- zkLogin、passkey、wallet adapter、sponsored/gasless flows 等用户/开发者体验；
- 与 Aptos Move 的差异化：对象模型、owned/shared objects、parallel execution、PTB、address balances、package/upgrade 语义；
- GitHub 活动与官方 developer relations、events、grants、ecosystem announcement 的对应关系；
- 对 Mantle 的竞争含义：Move 开发者心智、非 EVM 应用范式、对象模型对支付/游戏/DeFi 的表达优势与迁移成本。

- **Priority**: medium
- **Dependencies**: item-4, item-5, item-7

### item-10: DeFi、生态战略与链上指标证据

把官方叙事和代码活动映射到 DeFi/生态发展，避免只停留在技术机制或合作公告。

必须覆盖：

- Sui Payments、stablecoin transfers、address balances、sponsored tx、wallet/custodian integration 对支付/DeFi 场景的组合价值；
- DeFi 生态证据：DEX、lending、liquid staking、stablecoin liquidity、bridge/interop、RWA/treasury、TVL/volume 等可核验指标；
- 相关 PR 是否集中在 core protocol、framework、SDK、indexer、docs、examples 或 ecosystem apps；
- 与 Tempo、Solana、Base、Canton 等支付/机构方向方案的差异：Sui 是通用高性能 L1 上的支付 UX/Move 应用范式组合，而非支付专用链或企业许可网络；
- 风险：gasless path 范围有限、Fireblocks 能力边界需确认、稳定币流动性和法币出入金依赖外部伙伴、DeFi 指标可能受激励影响。

- **Priority**: medium
- **Dependencies**: item-5, item-7, item-8, item-9

### item-11: 横向竞争定位：Sui vs Mantle / Solana / Aptos / Base / Tempo / Canton

建立横向竞争框架，解释 Sui 的差异化不是单点功能，而是对象模型、高性能 L1、Move、gasless/sponsored UX、机构托管合作、DeFi/consumer 应用和开发者体验的组合。

比较对象至少包括：

- **Mantle / Ethereum L2**：EVM 兼容、以太坊安全与流动性、L2 成本结构、AA/paymaster 可实现路径；
- **Solana**：高吞吐通用 L1、低费用、consumer/DePIN/payments 心智，但 gas 抽象路径不同；
- **Aptos**：Move 生态近邻、并行执行、机构/支付叙事相似点；
- **Base**：Coinbase 分发、USDC/merchant/consumer apps、EVM 生态和账户抽象；
- **Tempo**：支付优先 L1、稳定币 gas、Payment Lane、机构支付叙事；
- **Canton / Fireblocks 类机构基础设施**：合规、托管、机构工作流，而非开放 DeFi L1。

对比维度：

- 开发活动强度与协议/SDK/应用变更速度；
- 支付 UX：gasless/sponsored/stablecoin gas/paymaster；
- 开发者生态：Move vs EVM、SDK/API、工具链、迁移成本；
- DeFi 流动性、稳定币深度和分发渠道；
- 机构/托管/合规合作；
- 性能、最终性、费用可预测性；
- 对 Mantle 可复制性、不可复制性和可反向定位点。

- **Priority**: high
- **Dependencies**: item-8, item-9, item-10

### item-12: 对 Mantle 的竞争启示与响应建议

把 Sui 近期开发和叙事变化转化为 Mantle 可执行判断。输出应按威胁面、可借鉴、不可迁移和路线建议组织。

必须覆盖：

1. **威胁面**
   - Sui 通过 gasless/sponsored stablecoin flow 降低支付 onboarding 摩擦；
   - Fireblocks/托管合作增强机构可用性叙事；
   - Move 对象模型、PTB、address balance 可能强化支付/游戏/DeFi 组合体验；
   - 多 repo 高频活动可能形成"快速演进、全栈产品化"印象。
2. **Mantle 可借鉴**
   - stablecoin payment UX、AA/paymaster/gas sponsorship、merchant SDK、memo/reconciliation；
   - SDK/API 层自动识别支付路径并隐藏 gas；
   - 官方 blog + docs + code PR + release notes 串联叙事；
   - 用 PR 活动分类和 release note 展示工程势能。
3. **不可直接迁移**
   - Move 对象模型、Sui gasless validation、address balance 与 EVM/OP Stack 不一一对应；
   - L2 gas economics、sequencer、paymaster、ERC-20/4337 约束不同；
   - Fireblocks 支持 Sui 不等于 Mantle 可直接获得同等支付产品优势。
4. **路线建议**
   - 短期：Mantle stablecoin payment demo / paymaster UX / merchant SDK / custody integration inventory；
   - 中期：payment-specific transaction path、AA/paymaster 标准化、stablecoin fee abstraction、DeFi liquidity routing；
   - 长期：企业/机构支付叙事与 EVM 兼容优势结合，形成 Ethereum-aligned payments and DeFi settlement layer 定位。

- **Priority**: high
- **Dependencies**: item-8, item-10, item-11

### item-13: 风险、开放问题与事实核验清单

集中列出 deep draft 必须显式标注的 caveats，避免把初步信号写成确定事实。

必须核验：

- repo universe 是否遗漏从 MystenLabs 迁出的官方资产或 Sui Foundation 维护资产；
- repo 活跃度是否被 bot、backport、release、generated docs、monorepo commits 扭曲；
- PR Tracker 是否覆盖 Sui、覆盖日期是否完整、与 GitHub 原始数据差异多大；
- Sui 官方 blog 中 gasless stablecoin / Fireblocks 公告的发布日期、措辞和支持边界；
- Fireblocks 是否有独立官方资料确认 Sui 支持范围、PTB policy inspection、gasless support 或 sponsor signing；
- Sui docs/source 中 allowlisted stablecoin、minimum amount、rate limit、gasless max TPS、SDK transport 的最新状态；
- 是否存在近期安全事故、性能退化、validator incident、major revert 或 controversial PR；
- DeFi/TVL/volume 数据是否来自可复核第三方数据源，是否存在激励或 wash trading 影响；
- 与 Mantle 的对比是否混淆 L1 与 L2、Move 与 EVM、protocol feature 与 app-layer capability。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-7, item-12

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| repo_identity | repo 名称、URL、org、type、archived/fork 状态、default branch、primary language、是否官方/半官方 | item-1, item-2 |
| activity_metrics | PR created/merged/closed、commit count、active contributors、release/tag、default branch push、issues/discussions、归一化分数 | item-2, item-3 |
| ranking_method | 排序公式、权重、过滤规则、敏感性检查、Top repo 选择阈值和排除理由 | item-2 |
| pr_metadata | PR number、title、state、dates、author、labels、milestone、reviews、changed files、directories、additions/deletions、URL | item-3, item-4, item-5 |
| development_category | PR 所属开发方向、分类依据、repo 分布、用户/开发者影响、工程意图推断 | item-4 |
| major_change | 重大变更名、状态、影响模块、影响对象、release/feature gate、叙事含义、风险/限制 | item-5 |
| trend_signal | 周度趋势、release 峰值、contributor 集中度、merge latency、revert/backport/hotfix、cross-repo coordination | item-6 |
| narrative_event | 官方公告/blog/docs/合作方资料的日期、主题、source URL、对应代码证据、叙事标签和置信度 | item-7, item-8, item-9, item-10 |
| payment_scope | gasless/sponsored/payment/custody 功能的支持对象、限制、rate limit、eligible assets、SDK/API 支持与非支持项 | item-8 |
| ecosystem_metric | TVL、volume、stablecoin liquidity、bridge flow、developer/event/grant 等指标来源、时间点、口径和 caveat | item-10 |
| competitor_comparison | 与 Mantle/Solana/Aptos/Base/Tempo/Canton 的维度对比、可复制性、不可复制性、反向定位点 | item-11 |
| mantle_implication | 威胁面、借鉴点、不可迁移约束、短中长期建议、优先级和依赖条件 | item-12 |
| source_confidence | 证据等级：GitHub primary、official docs/blog、partner official、PR Tracker、data aggregator、secondary media；标注推论与不确定性 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | table | MystenLabs / related org repo 活跃度排名表：repo、type、PR created/merged、commits、contributors、release/tag、score、rank、是否纳入 Top 分析、排除理由 | markdown table | item-2 |
| diag-2 | timeline | Top repo 每周 PR created/merged 趋势图，按 repo 或开发方向分组，标注官方公告/release 日期 | mermaid 或 markdown table | item-3, item-6, item-7 |
| diag-3 | matrix | PR 开发方向分类矩阵：repo x category，显示 PR 数量、代表 PR、趋势和产品/协议影响 | markdown table | item-4 |
| diag-4 | flow | 重大功能跨 repo 支撑链：core protocol -> SDK/API -> docs/wallet/indexer -> official narrative，展示哪些叙事有代码支撑 | mermaid | item-5, item-7, item-8 |
| diag-5 | comparison | Sui vs Mantle/Solana/Aptos/Base/Tempo/Canton 竞争定位矩阵，覆盖支付 UX、开发者生态、DeFi/流动性、机构/托管、性能、可复制性 | markdown table | item-11 |
| diag-6 | roadmap | Mantle 响应路线图：短期支付 UX demo、中期 paymaster/SDK/DeFi routing、长期 Ethereum-aligned payment and DeFi settlement narrative | mermaid | item-12 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | github_org_data | GitHub API/GraphQL/gh CLI 对 `MystenLabs` 全 org repo 的直接导出；包含 repo list、PR、commit、contributors、release/tag 和默认分支 push 数据 | 1 complete export |
| src-2 | github_pr_primary | Top repo 在 2026-02-23 至 2026-05-23 的 PR/commit/release primary links；每个 Top repo 需足够样本支撑分类和趋势 | 50+ PR links or complete export |
| src-3 | github_related_orgs | 从官方链接或 GitHub 搜索发现的 Sui 相关 org/repo 验证材料；如未纳入需说明排除理由 | 3 |
| src-4 | official_sui_sources | Sui 官方 blog、docs、release notes、developer updates、Mysten Labs / Sui Foundation 公告，优先覆盖支付、Move、SDK、DeFi、机构合作 | 8 |
| src-5 | partner_official_sources | Fireblocks、custody/wallet/stablecoin/DeFi/infra 合作方官方资料，用于验证合作范围和支持边界 | 3 |
| src-6 | pr_tracker | PR Tracker 每日跟踪报告（如覆盖 Sui），用于交叉验证 PR 摘要和趋势；必须标注覆盖日期和与 GitHub 原始数据差异 | 1 coverage set if available |
| src-7 | ecosystem_data | DeFiLlama、SuiVision、official explorer、stablecoin/bridge/volume 数据源，用于生态/DeFi 指标，必须记录查询日期和口径 | 3 |
| src-8 | competitor_primary_sources | Mantle、Solana、Aptos、Base、Tempo、Canton 等官方 docs/blog 或既有仓库研究，用于横向竞争对比，二手报道只能补充 | 6 |

## Deep Phase Execution Plan

1. **Repo universe scan**: 使用 GitHub API/gh CLI 导出 `MystenLabs` 全公开 repo，并记录查询命令、时间、分页和 rate limit；同步查找 Sui 官方链接指向的相关 org。
2. **Activity ranking**: 对所有 repo 计算 2026-02-23 至 2026-05-23 活跃度分数，输出完整排名、Top 候选和敏感性检查；在此之前不选择分析对象。
3. **Top repo PR export**: 对 Top repo 导出 PR 级数据与 commit/release/tag 数据，保留原始表或附录摘要。
4. **Classification and trend analysis**: 建立 PR 分类体系，计算 repo/category/week 分布，识别跨 repo 协同和工程组织信号。
5. **Major change extraction**: 从分类中筛出重大功能、架构、SDK/API、支付/DeFi/Move/infra 变化，并逐项链接 primary evidence。
6. **Narrative mapping**: 建立官方 blog/docs/partner announcement/PR Tracker 时间线，将叙事事件映射到 repo/PR evidence。
7. **Competition and Mantle implications**: 与 Mantle 及横向竞品比较，输出威胁、可借鉴、不可迁移和路线建议。
8. **Caveat audit**: 在 final draft 前逐项检查 `item-13`，确保所有易过期事实有验证日期和 source confidence。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | created | full outline | User requested rerun with data-driven repo discovery before Sui analysis; old outline incorrectly pre-assumed `MystenLabs/sui` only | Orchestrator dispatch `58617dc2-f750-4154-9fa9-f2f37f4c1e59` |
