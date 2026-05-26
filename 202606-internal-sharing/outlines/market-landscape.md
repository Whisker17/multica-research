---
topic: "L2 赛道格局与市场现状分析"
project_slug: "202606-internal-sharing"
topic_slug: "market-landscape"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/market-landscape.md"
  draft: "202606-internal-sharing/research-sections/market-landscape/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/market-landscape/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  本 section 为 Mantle 工程团队 20260605 bi-weekly 全公司分享的第一章，目标是用数据和市场证据解释
  Ethereum L2 赛道从通用 Rollup 竞争进入差异化定位阶段的过程，并把这一背景连接到 RWA / 机构金融
  叙事转向以及 Mantle 当前定位。研究必须覆盖 Base、Arbitrum、Optimism、zkSync、Mantle 五条主要
  L2 的 TVL、日活地址、交易量、gas/费用、合约部署/开发者 proxy 等趋势，并解释基础设施型
  Superchain/Orbit 与应用导向型 Base/Mantle 的分化。第二部分需要分析 DeFi 叙事天花板、监管收紧、
  RWA 机构入场和合规基础设施竞争。第三部分聚焦 Mantle 从 mETH/DeFi 生态到 RWA 方向探索的背景、
  技术栈现状、生态活跃度变化，以及寻找下一个叙事点的必要性。

audience: |
  Mantle 工程团队、生态/BD/战略研究同事、协议和产品负责人，以及 Research Review Agent 和后续
  deep draft 写作者。读者熟悉 L2、Rollup、DeFi、RWA、OP Stack、Superchain/Orbit 等基本概念，
  但需要一份可复核、数据驱动、适合内部分享第一页建立共识的市场格局分析。

expected_output: |
  一份中文结构化 research section，包含：
  1. L2 赛道格局演变的数据驱动分析，含 Base / Arbitrum / Optimism / zkSync / Mantle 的对比图表数据；
  2. DeFi -> RWA / 机构金融叙事转向的市场证据，覆盖监管、机构入场和合规基础设施；
  3. Mantle 当前生态定位、技术栈状态和活跃度变化数据，并论证寻找下一个叙事点的必要性。

source_requirements_summary: |
  Deep phase 必须以 Dune Analytics / DuneSQL 自建查询作为主要链上数据来源，DefiLlama、L2Beat、
  官方 dashboard、Token Terminal、GitHub / contract deployment 数据作为交叉验证或补充。所有时间序列
  必须记录查询日期、窗口、链 ID / schema / table、过滤条件、去重规则和缺失数据 caveat。已完成竞品研究
  WHI-79 至 WHI-85、WHI-87 非代码叙事分析可以作为内部参考和线索，但不得替代本 section 的最新数据抓取
  与事实核验。涉及 2026 年市场状态、机构产品规模、监管和 Vitalik 观点的事实必须用发布日期明确的来源重新验证。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-26T08:02:20+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-26T08:02:20+08:00"

multica_issue_id: "ae371472-f733-4dcc-a34b-a9194d099148"
branch_name: "research/202606-internal-sharing/market-landscape"
base_commit: "196f34db73d8d03ce070aa0218825b1cea67e1f6"
language: "中文"
research_depth: "standard"

prerequisite_sections:
  - slug: competitor-base
    path: "202606-internal-sharing/research-sections/competitor-base/final.md"
    status: existing-research
  - slug: competitor-arbitrum
    path: "202606-internal-sharing/research-sections/competitor-arbitrum/final.md"
    status: existing-research
  - slug: competitor-optimism
    path: "202606-internal-sharing/research-sections/competitor-optimism/final.md"
    status: existing-research
  - slug: competitor-zksync
    path: "202606-internal-sharing/research-sections/competitor-zksync/final.md"
    status: existing-research
  - slug: narrative-analysis
    path: "202606-internal-sharing/research-sections/narrative-analysis/final.md"
    status: existing-research
  - slug: enterprise-canton
    path: "202606-internal-sharing/research-sections/enterprise-canton/final.md"
    status: existing-research
  - slug: enterprise-privacy
    path: "202606-internal-sharing/research-sections/enterprise-privacy/final.md"
    status: existing-research
---

# Research Outline: L2 赛道格局与市场现状分析

## Methodology Gate

Deep draft 必须先完成数据底座，再写市场判断。任何关于"Base 领先"、"Mantle 活跃度下降"、
"RWA 加速"或"DeFi 叙事天花板"的结论都需要标注数据来源、时间窗口、口径和置信度。

最低执行要求：

- 固定链上数据窗口：建议至少覆盖最近 12 个月，并用最近 90 天作为高频变化窗口；如果 Dune 表可用，应按日聚合并在图表数据中保留 `date`、`chain`、`metric`、`value`。
- 自建 DuneSQL 查询覆盖 Base、Arbitrum One、OP Mainnet、zkSync Era、Mantle 的 DAU、交易笔数、gas used / fees、活跃合约、合约部署数；TVL 可用 DefiLlama / L2Beat 交叉验证，并尽量保留历史序列。
- 统一口径：DAU 使用 active addresses 或 sender addresses 时必须说明是否包括系统地址、桥、sequencer、合约内部调用；交易量必须区分 tx count、DEX volume、stablecoin transfer volume 和 bridge volume。
- 开发者增速 proxy 优先使用 contract deployments、new verified contracts、GitHub org activity 或 Electric Capital / Developer Report 等可得数据；不得把合约部署数直接等同于真实开发者数量。
- 对已完成竞品研究只作引用线索：Base / Arbitrum / Optimism / zkSync 的前序 final 可复用结构和历史结论，但本 section 的关键数字必须重新抓取或明确标注为历史材料。
- 每个图表都要提供可复制数据表或 CSV-ready markdown 表，并说明图表推荐形态、排序、单位、缺失值处理和异常点解释。
- 对监管、机构入场、RWA 规模和 Vitalik 观点等时间敏感事实，必须使用 2025-2026 年官方或主流来源重新核验，写明发布日期和访问日期。

## Research Questions

1. Ethereum L2 赛道是否已经从"通用低费 Rollup"竞争转向"分发渠道、应用场景、基础设施网络和合规能力"竞争？哪些数据支持这一判断？
2. Base、Arbitrum、Optimism、zkSync、Mantle 在 TVL、DAU、交易笔数、gas/fees、合约部署和开发者 proxy 上的 12 个月趋势分别如何？近期 90 天是否出现结构性分化？
3. 基础设施型路线（Optimism Superchain、Arbitrum Orbit、zkSync Elastic Chain / ZK Stack）和应用导向型路线（Base 的 Coinbase 分发 / onchain economy、Mantle 的 mETH/DeFi/RWA 探索）各自如何形成差异化？
4. DeFi 叙事是否遇到增长天花板或监管压力？TVL、DEX/perp 活动、收益率、稳定币/RWA 增长和监管事件分别给出什么证据？
5. RWA / 机构金融叙事加速的关键证据是什么？BlackRock BUIDL、Franklin Templeton、Ondo 等案例代表真实资产规模增长、合规产品化，还是营销叙事放大？
6. 合规基础设施正在如何成为 L2 差异化维度？KYC/AML、permissioned appchain、隐私、token policy、identity、institutional custody 等能力如何影响 L2 竞争？
7. Vitalik / Ethereum cyberpunk 方向（credible neutrality、censorship resistance、privacy）与行业 ToB / permissioned / KYC-AML 转向之间的张力是什么？它对 L2 叙事和产品路线意味着什么？
8. Mantle 当前技术栈和生态定位是什么？OP Stack based、Ethereum aligned、标准化组件选择是否帮助或限制其进入 RWA / 机构金融叙事？
9. Mantle 的 TVL、DAU、交易量、gas、合约部署、mETH 相关生态活动是否显示活跃度下降或结构迁移？下降来自市场周期、激励变化、生态结构还是竞品挤压？
10. 对内部分享而言，应该如何用 3-5 个高置信度结论解释"Mantle 为什么需要下一个叙事点"，同时避免夸大 RWA 或低估 DeFi 基本盘？

## Items

### item-1: 数据口径、DuneSQL 查询设计与交叉验证框架

建立全 section 的数据方法论，先定义链、指标、时间窗口和异常值处理，再进入结论。该项必须产出 DuneSQL 查询清单和数据字典，确保后续图表可复核。重点是让 Base / Arbitrum / Optimism / zkSync / Mantle 的指标在同一口径下可比，同时标注 Dune 表覆盖差异和 DefiLlama / L2Beat 的交叉验证方式。

必须覆盖：

- 链映射：Base、Arbitrum One、OP Mainnet、zkSync Era、Mantle 的 chain name、chain id、Dune schema/table、DefiLlama slug、L2Beat slug；
- 时间窗口：最近 12 个月日频趋势、最近 90 天变化、必要时增加 2024-2026 长周期参考；
- DuneSQL 查询清单：DAU、tx count、gas used、fees paid、active contracts、new contract deployments、bridge inflow/outflow、stablecoin transfer proxy；
- TVL 数据方案：DefiLlama historical TVL、L2Beat total value secured / canonical / external / native 等口径差异；
- 去重与过滤：EOA / contract sender、system address、sequencer/batcher、bridge contracts、airdrop/激励 spike、机器人/垃圾交易、链重组或索引缺失；
- 输出数据字典：`date`、`chain`、`metric`、`value`、`unit`、`source`、`query_url_or_file`、`last_refreshed_at`、`confidence`、`notes`。

- **Priority**: high
- **Dependencies**: none

### item-2: L2 关键数据对比与赛道格局演变

用统一数据口径比较五条 L2 的核心市场指标，判断赛道是否从通用 Rollup 扩容竞争进入分层与差异化竞争。该项应优先产出图表数据，而不是先写观点。需要把绝对规模、增长率、份额变化和近期趋势同时呈现，避免只看单日排名。

必须覆盖：

- TVL：各链 12 个月历史、峰值、当前值、90 天变化、市场份额变化，并解释 DefiLlama 与 L2Beat 口径差异；
- DAU / active addresses：日频趋势、7d/30d rolling average、峰值事件、激励或空投影响；
- 交易笔数与 gas/fees：tx count、gas used、user fees、费用下降/上涨对活跃度的影响；
- 开发者 proxy：new contract deployments、active contracts、verified contracts / GitHub activity 若可得；说明 proxy 局限；
- 数据分化判断：Base 是否在用户/交易上领先，Arbitrum 是否在 TVL/DeFi 上仍强，Optimism 是否更多体现 Superchain 网络效应，zkSync 是否处于 ZK/Elastic Chain 转型，Mantle 是否依赖 mETH / DeFi 激励；
- 输出：L2 指标总览表、12 个月 TVL/DAU/tx 趋势图数据、90 天变化排名、链间份额堆叠图数据。

- **Priority**: high
- **Dependencies**: item-1

### item-3: L2 差异化路线：基础设施网络 vs 应用导向链

分析 L2 竞争从"谁更便宜/更快"转向"谁控制生态入口、应用场景、开发者网络和发行渠道"的结构性变化。该项需要把 Optimism Superchain、Arbitrum Orbit、zkSync Elastic Chain 等基础设施型路线，与 Base / Mantle 等应用或分发导向路线放在同一框架内比较。

必须覆盖：

- 基础设施型路线：Optimism Superchain / OP Stack、Arbitrum Orbit / L3、zkSync Elastic Chain / ZK Stack 的定位、网络效应、收入/治理/互操作逻辑；
- 应用导向路线：Base 的 Coinbase 分发、onchain economy、支付/资产发行/开发者 funnel；Mantle 的 MNT、mETH、DeFi/yield、RWA 探索和 Ethereum-aligned 定位；
- 指标映射：基础设施型路线应看生态链数量、stack adoption、interop、developer tooling、shared security / governance；应用导向型路线应看终端用户、资金流、应用交易、稳定币/RWA/DeFi 活动；
- 竞品研究复用：从 competitor-base、competitor-optimism、competitor-arbitrum、competitor-zksync final 中提取已验证结论，并重新核验关键时间敏感事实；
- 输出：L2 positioning matrix、基础设施型 vs 应用导向型路线对照表、"通用 Rollup -> 差异化定位"演变时间线。

- **Priority**: high
- **Dependencies**: item-2

### item-4: DeFi 叙事天花板与监管收紧证据

评估 DeFi 作为 L2 主叙事的增长约束。该项不应简单宣称 DeFi 过时，而要区分 DeFi 仍是 TVL 和交易基本盘、但作为新增叙事和机构入口可能受限。需要同时看链上数据、收益率/流动性、监管事件和竞品叙事变化。

必须覆盖：

- DeFi 数据：各链 DeFi TVL、DEX/perp 活动、借贷/yield 协议活跃、mETH / LST / yield 产品关联指标；
- 增长约束：激励驱动 TVL、空投/points 结束后的活跃度回落、收益率压缩、流动性集中在少数头部协议；
- 监管压力：美国、欧盟、亚洲主要监管事件或政策信号中与 DeFi、稳定币、交易平台、KYC/AML、前端责任相关的部分；
- L2 叙事变化：竞品是否减少单纯 DeFi 表达，转向 payments、RWA、institutional adoption、consumer apps、appchain / stack；
- 输出：DeFi 增长约束证据表、监管时间线、DeFi basic layer vs narrative ceiling 的判断框架。

- **Priority**: medium
- **Dependencies**: item-1, item-2

### item-5: RWA / 机构金融加速的市场证据

梳理 RWA 与机构金融从边缘主题进入主流 crypto 叙事的证据，重点区分真实资产规模、机构产品落地、链上发行/赎回机制、二级市场活跃度和媒体叙事。该项必须覆盖 BlackRock BUIDL、Franklin Templeton、Ondo 等案例，并对数据口径和链部署做核验。

必须覆盖：

- 机构案例：BlackRock BUIDL、Franklin Templeton tokenized money market funds、Ondo Finance、Securitize、Centrifuge / Maker / Sky、以及其他 2025-2026 年高影响 RWA 案例；
- 指标：AUM / TVL、持有人数、发行链、转账活跃度、赎回机制、合作机构、合规结构、二级流动性；
- RWA 市场数据来源：RWA.xyz、DefiLlama RWA、官方产品页、SEC / prospectus / regulatory filings、issuer announcements；
- 与 L2 的关系：哪些 RWA 产品选择 Ethereum mainnet、public L2、permissioned chain、appchain 或 enterprise network；L2 需要提供什么才能承接机构资产；
- 输出：RWA 机构入场案例表、RWA 增长时间线、RWA 对 L2 基础设施需求矩阵。

- **Priority**: high
- **Dependencies**: item-4

### item-6: 合规基础设施竞争与 cyberpunk / ToB 分歧

分析合规基础设施为什么成为 L2 差异化竞争维度，以及它与 Ethereum 原生价值观之间的张力。该项需要平衡 Vitalik / Ethereum 社区关于 privacy、censorship resistance、credible neutrality 的观点，与行业 ToB / permissioned / KYC-AML / institutional adoption 的现实转向。

必须覆盖：

- 合规能力清单：KYC/AML、身份与 attestations、permissioned pools、transfer restrictions、token policy registry、institutional custody、audit / reporting、privacy-preserving compliance；
- 项目案例：Base 合规资产发行/Token Factory 相关信号、zkSync Prividium / enterprise privacy、Canton enterprise workflow、Arc / Tempo 稳定币支付与合规、Ondo / Securitize RWA 合规路径；
- Vitalik / Ethereum 观点：credible neutrality、privacy、cypherpunk/cyberpunk、anti-censorship、account abstraction / privacy roadmap；必须使用原文或官方上下文，避免断章取义；
- 分歧分析：public permissionless L2 与 permissioned institutional environments 的边界、可组合性损失、监管接受度、用户隐私、中心化风险；
- 对 Mantle 的含义：Mantle 若进入 RWA / 机构金融，需要哪些合规、隐私、identity、audit、custody、policy 组件；哪些能力适合作为 L2 公共层，哪些应放在应用层或 appchain；
- 输出：compliance stack diagram、cyberpunk vs ToB tension matrix、Mantle capability gap list。

- **Priority**: high
- **Dependencies**: item-5

### item-7: Mantle 技术栈、生态定位与转型背景

建立 Mantle 当前定位的事实底座：技术栈、Ethereum alignment、mETH / DeFi 生态、MNT、模块化组件和 RWA 转型背景。该项需要避免把 Mantle 简化为"OP Stack fork"或"DeFi 链"，而是说明现有资产、约束和可转向空间。

必须覆盖：

- 技术栈现状：OP Stack based、Ethereum aligned、结算/桥、数据可用性、sequencer / batcher、标准化组件选择、与 upstream OP Stack / EigenDA / Mantle-specific 组件的关系；
- 生态资产：MNT、mETH / cmETH / FBTC / yield-bearing assets、核心 DeFi 协议、桥、钱包、开发者工具、生态激励；
- 转型背景：mETH / DeFi 生态增长后的边际叙事空间、RWA / institutional-ready settlement / payment experimentation 的可能入口；
- 与竞品差异：Base 有 Coinbase 分发、Arbitrum 有 DeFi/Orbit/Stylus、Optimism 有 Superchain、zkSync 有 ZK/Elastic/Prividium；Mantle 的可差异化证据在哪里；
- 输出：Mantle asset-and-capability map、技术栈事实表、现有生态与 RWA/机构叙事匹配度矩阵。

- **Priority**: high
- **Dependencies**: item-3, item-6

### item-8: Mantle 活跃度下降与生态健康度诊断

用链上数据判断 Mantle 生态活跃度是否下降、下降在哪些维度、与竞品相比是否显著，以及可能原因。该项必须用同一口径数据与 Base / Arbitrum / Optimism / zkSync 对比，不能只引用单一 TVL 或单一 dashboard。

必须覆盖：

- Mantle TVL、DAU、tx count、gas/fees、active contracts、new contract deployments、bridge flows、stablecoin/RWA/yield assets 的 12 个月与 90 天趋势；
- mETH / DeFi 相关活跃：mETH TVL/holders/flows、核心 DEX / lending / yield 协议指标、incentive / campaign 时间点；
- 生态健康度：用户留存、交易集中度、协议集中度、真实用户 vs bot / farming、合约部署质量 proxy；
- 下降原因假设：激励退坡、市场整体降温、竞品吸流、叙事疲劳、应用不足、开发者减少、数据口径变化；
- 对比判断：Mantle 是绝对下降、相对落后、结构转移，还是指标选择导致的误读；
- 输出：Mantle health dashboard data、下降原因假设表、与五条 L2 90 天变化对照图。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-7

### item-9: 下一叙事点必要性与内部分享结论框架

把前述数据和市场证据转化为内部分享可用的论证链。该项应给出清晰但不过度营销的结论：为什么 Mantle 需要寻找下一个叙事点，RWA / 机构金融是否是合理方向，以及需要哪些工程、生态和合规支撑。

必须覆盖：

- 论证链：L2 赛道分化 -> DeFi 叙事边际递减 -> RWA / 机构金融加速 -> 合规基础设施成为差异化 -> Mantle 需要新证据支撑的新叙事；
- 反论点：DeFi 仍是基本盘、RWA 可能增长慢且合规复杂、机构采用不等于公链活跃、Base/Arc/Tempo/Canton 等已占据部分心智；
- Mantle 可行叙事：Ethereum-aligned institutional-ready L2、yield-bearing asset base、modular settlement / DA、compliance-friendly app layer、RWA/payments pilot platform；
- 必要前置条件：数据改善、合作伙伴、identity/compliance/privacy primitives、institutional custody、RWA issuer / payment pilot、开发者工具和真实应用；
- 内部分享输出：3-5 个 slide-ready 结论、关键图表顺序、每页主 claim 与证据、不得夸大的 caveat。

- **Priority**: high
- **Dependencies**: item-5, item-6, item-8

### item-10: 风险、开放问题与事实核验清单

集中列出后续 deep draft 必须显式处理的 caveats，防止内部分享误用过时数据、混淆口径或把市场叙事当作已发生事实。该项应作为 review agent 检查清单。

必须覆盖：

- Dune 数据可得性：不同链表结构、索引延迟、系统地址过滤、internal tx 覆盖、contract creation 识别、zkSync / Mantle schema 差异；
- TVL 口径：DefiLlama 与 L2Beat 的 TVL / TVS / canonical / native / external 差异，不同资产价格波动影响；
- 地址与交易：active address 不等于真实用户，低费链可能产生 spam / bot；交易笔数不等于经济价值；
- 开发者 proxy：合约部署数、verified contract、GitHub activity 均有偏差；
- RWA 事实边界：AUM、TVL、token supply、onchain liquidity、permissioned transfer、fund shares、合作公告和真实使用需要分开；
- 监管与观点：政策解读和 Vitalik 观点必须保留上下文，不得用二手摘要替代原文；
- Mantle 结论：若数据不支持"活跃度下降"，必须改写为"结构变化"或"相对竞争压力"，不得为叙事需求强行下结论。

- **Priority**: high
- **Dependencies**: all

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| chain | Base、Arbitrum One、OP Mainnet、zkSync Era、Mantle，必要时包含 Ethereum mainnet / selected appchains 作为参照 | item-1, item-2, item-3, item-8 |
| metric_name | TVL、TVS、DAU、tx_count、gas_used、fees_usd、active_contracts、new_contract_deployments、bridge_flow、stablecoin_transfer_volume、RWA_AUM 等指标名 | item-1, item-2, item-4, item-5, item-8 |
| metric_definition | 指标计算公式、纳入/排除规则、单位、聚合粒度和可比性限制 | item-1, item-2, item-8 |
| time_window | 12m、90d、YTD、事件前后窗口，必须记录起止日期和时区 | all |
| data_source | Dune query、DefiLlama API、L2Beat、RWA.xyz、official dashboard、official docs/blog、regulatory filing、internal research artifact | all |
| query_or_source_url | Dune query URL、API endpoint、官方 URL 或仓库内 artifact path，必须可复核 | all |
| last_refreshed_at | 数据抓取或事实核验时间，ISO-8601 | all |
| evidence_level | official-primary、on-chain-data、dashboard-data、regulatory-filing、industry-data、media-reported、internal-research、inferred、unverified | all |
| confidence | high / medium / low，综合来源质量、口径清晰度和交叉验证情况 | all |
| l2_positioning | infrastructure-network、app-oriented、distribution-led、DeFi-led、RWA-institutional、privacy-compliance、unclear | item-3, item-7, item-9 |
| differentiation_axis | Superchain/Orbit/Elastic Stack、Coinbase distribution、DeFi liquidity、RWA/compliance、stablecoin/payments、privacy、developer ecosystem、yield-bearing assets | item-3, item-6, item-7, item-9 |
| narrative_claim | 项目或市场公开表达的核心叙事 claim，需用中文概括并保留关键英文术语 | item-3, item-4, item-5, item-6, item-9 |
| market_evidence | 支撑叙事的链上数据、AUM/TVL、合作、产品发布、监管文件或媒体报道 | item-4, item-5, item-6, item-9 |
| mantle_relevance | 对 Mantle 的含义：defend、borrow、avoid、opportunity、gap、monitor、not-applicable | item-3, item-6, item-7, item-8, item-9 |
| caveat | 数据限制、事实边界、口径差异、反论点或待验证事项 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Base / Arbitrum / Optimism / zkSync / Mantle 的核心指标总览：当前值、90d 变化、12m 趋势、数据源和置信度 | ascii | item-2 |
| diag-2 | timeline | L2 赛道从通用 Rollup 竞争到差异化定位的演变时间线，标注 Superchain/Orbit/Elastic/Base/Mantle 关键节点 | mermaid | item-3 |
| diag-3 | comparison | 基础设施型 L2 网络 vs 应用导向型 L2 的定位矩阵，横轴为生态/stack 控制，纵轴为用户/应用分发 | ascii | item-3 |
| diag-4 | timeline | DeFi 叙事增长约束、监管事件和 RWA 机构入场关键事件的并行时间线 | mermaid | item-4, item-5 |
| diag-5 | flow | RWA / 机构金融对 L2 的能力需求栈：identity、KYC/AML、custody、privacy、policy、settlement、reporting | mermaid | item-5, item-6 |
| diag-6 | comparison | cyberpunk / CR / privacy 与 ToB / KYC-AML / permissioned 路线的张力矩阵，列出收益、风险和适配场景 | ascii | item-6 |
| diag-7 | hierarchy | Mantle 现有资产与能力地图：technical stack、mETH/DeFi、MNT、ecosystem、RWA/compliance gaps | mermaid | item-7 |
| diag-8 | comparison | Mantle 生态健康度 dashboard：TVL、DAU、tx、gas、合约部署、mETH 活跃、bridge flow 的趋势与异常点 | ascii | item-8 |
| diag-9 | flow | 内部分享结论链：market fragmentation -> DeFi ceiling -> RWA/institutional acceleration -> compliance differentiation -> Mantle next narrative | mermaid | item-9 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | on_chain_data | Dune Analytics 自建查询，覆盖 Base、Arbitrum、Optimism、zkSync、Mantle 的 DAU、tx、gas/fees、active/new contracts 等日频数据 | 5 |
| src-2 | industry_data | DefiLlama、L2Beat、RWA.xyz、Token Terminal 或同等级 dashboard，用于 TVL/TVS/RWA/fees 数据交叉验证 | 4 |
| src-3 | official_docs | Base、Arbitrum、Optimism、zkSync、Mantle、Canton、Arc/Tempo 等官方 docs/blog/announcements，用于定位和技术栈事实 | 8 |
| src-4 | regulatory_filing | BlackRock BUIDL、Franklin Templeton、Ondo/Securitize 等 RWA 或 tokenized fund 的官方文件、产品页、SEC / prospectus / issuer disclosure | 3 |
| src-5 | media_reports | CoinDesk、The Block、Blockworks、Fortune Crypto、Bloomberg、Reuters 等主流报道，用于机构入场、监管和市场叙事交叉验证 | 6 |
| src-6 | expert_commentary | Vitalik / Ethereum Foundation / 核心研究者关于 privacy、credible neutrality、cypherpunk/cyberpunk、compliance tension 的原文或官方上下文 | 3 |
| src-7 | internal_research | 202606 internal sharing 已完成竞品研究 final 和 WHI-87 非代码叙事分析，仅作为背景线索和交叉引用 | 5 |
| src-8 | code_or_developer_data | GitHub org activity、contract deployment、verified contract、developer report 或其他开发者 proxy 数据，用于开发者增速分析 | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
