---
topic: "Circle Arc 支付链深度分析"
project_slug: 202606-internal-sharing
topic_slug: payment-ark
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: 202606-internal-sharing/outlines/payment-ark.md
  draft: 202606-internal-sharing/research-sections/payment-ark/drafts/round-{n}.md
  final: 202606-internal-sharing/research-sections/payment-ark/final.md
  index: 202606-internal-sharing/research-sections/_index.md

scope: |
  分析 Circle Arc 的项目定位与愿景（从稳定币发行方到 "Economic OS" 的战略转型）、技术架构设计
  （Malachite 共识引擎、USDC 作为 Gas、完整 EVM 兼容、可选隐私控制、CCTP 跨链协议、抗量子设计）、
  支付场景适配能力（Circle StableFX 机构级稳定币外汇引擎、Circle Partner Stablecoins 非美元稳定币生态、
  跨境支付与外汇结算、Agentic Commerce AI Agent 微交易）、代币经济学（ARC 代币 100 亿总量，
  60% 生态/25% Circle/15% 储备，费用转换与销毁机制）、机构生态与合作方（BlackRock、Visa、
  Goldman Sachs、a16z 等 100+ 测试网参与机构）、与 Tempo 的方案差异与互补性、
  与 Mantle 生态的潜在关联和竞争分析。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享的准备者、Mantle 支付/企业业务方向负责人、
  协议工程师、BD/生态合作团队，以及 Multica Research Squad 的 Adversarial Agent 和 Technical Writer。
  读者熟悉 L1/L2、稳定币和支付基础设施概念，但不一定熟悉 Arc、Malachite BFT、StableFX、
  CCTP V2 或 ARC 代币经济学的内部机制。

expected_output: |
  - 一份中文结构化 research section，能够直接支持内部分享材料
  - Arc 的一句话定位、战略意图、发展阶段和机构生态版图
  - 技术架构概述：Malachite BFT 共识、USDC Gas、EVM 兼容、可选隐私、CCTP、抗量子路线
  - Circle 平台服务栈：StableFX、Partner Stablecoins、CPN 的支付场景覆盖
  - ARC 代币经济学：分配、五大功能、费用转换与销毁、通胀模型、治理框架
  - 与 Tempo 的对比分析：定位差异、技术路线差异、生态策略差异
  - 对 Mantle 的启示：可借鉴模块、潜在竞争/合作路径、支付赛道趋势判断
  - 至少 3 张 Mermaid 图：架构分层图、费用转换与代币经济学流程图、Arc vs Tempo 对比矩阵

source_requirements_summary: |
  Primary source 包括 Arc 官网/官方文档(arc.io, docs.arc.io)、ARC 代币白皮书(2026年5月)、
  Circle 官方博客和公告、Arc 博客技术文章。对网络状态、测试网数据、合作伙伴、融资、
  代币经济学参数等易过期事实，必须重新验证并注明验证日期或证据置信度。
  Tempo 对比数据需引用本仓库已有 payment-tempo 研究和公开资料。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-23T15:45:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-23T15:45:00+08:00"

prerequisite_sections:
  - slug: payment-tempo
    path: 202606-internal-sharing/research-sections/payment-tempo/final.md
    status: existing-research
---

# Research Outline: Circle Arc 支付链深度分析

## Research Questions

1. Circle 从稳定币发行方向 L1 区块链基础设施层（"Economic OS"）转型的战略逻辑是什么？这一转型对 USDC 生态和稳定币竞争格局意味着什么？
2. Arc 的技术架构如何服务机构级支付场景：Malachite BFT 共识引擎、USDC Gas 模型、可选隐私、CCTP 跨链和抗量子设计各自解决什么问题？这些技术选择与通用 L1/L2 有何本质差异？
3. Circle 在 Arc 上构建的平台服务栈（StableFX、Partner Stablecoins、CPN）如何形成从稳定币发行→FX 交易→跨境结算→支付网络的闭环？
4. ARC 代币经济学如何平衡网络安全（staking/验证者激励）、协议治理（去中心化）和价值捕获（费用转换/销毁）？作为上市公司发行原生代币有何特殊风险和先例意义？
5. Arc 与 Tempo（Stripe/Paradigm）在支付链赛道的定位差异、技术路线差异和生态策略差异是什么？二者是否存在互补或直接竞争关系？
6. Arc 对 Mantle 生态的潜在影响：是否会分流机构稳定币结算量？Mantle 可以从 Arc 的哪些设计中获取启示？是否存在合作路径？

## Items

### item-1: 项目定位与战略愿景

建立 Arc 的叙事锚点：Circle 从 USDC 发行方到 L1 基础设施构建者的战略转型逻辑。需要覆盖 Circle 的公司背景（USDC 发行方、纽交所上市 CRCL）、Arc 的 "Economic OS" 定位、从 litepaper（2025年8月）到公测（2025年10月）到代币预售（2026年5月）到主网（2026年夏季预计）的发展时间线、以及这一转型对稳定币竞争格局（GENIUS Act、银行/金融科技竞品代币威胁）的战略防御意义。

必须覆盖：

- Circle 公司概况：USDC 发行方、2026年纽交所上市（CRCL）、Q1 2026 营收 $694M、USDC 流通量 $77B、链上 USDC 季度交易量 $21.5T；
- Arc 定位：从稳定币发行到拥有基础设施层的战略跃迁，"Economic OS for the internet"；
- 发展时间线：litepaper 2025.08、公测 2025.10（100+ 机构参与）、测试网交易量 244.1M（截至 2026.05.05）、ARC 白皮书 2026.05、$222M 代币预售 2026.05、主网预计 2026 夏季；
- 战略背景：GENIUS Act 通过后银行/金融科技可发行稳定币，Circle 需要通过拥有基础设施层来降低对第三方链的依赖；
- 与 Circle 2026 产品愿景的关系：三大支柱架构（Foundation Layer / Asset Layer / Application Layer）。

- **Priority**: high
- **Dependencies**: none

### item-2: 技术架构设计

拆解 Arc 的核心技术选择，解释每个设计决策如何服务机构级支付/结算场景，以及与通用 EVM 链的本质差异。

必须覆盖：

- Malachite 共识引擎：Rust 实现、Tendermint 内核（Informal Systems 开发，现由 Circle 管理）、确定性亚秒级终局（100 验证者 ~780ms、小网络 ~330-490ms）、吞吐量 ~50k TPS / 13.5 MB/s、区块引用传播（非完整 payload）、2/3 验证者提交即终局、双进程架构（共识与执行分离）；
- 验证者模型：初期 PoA（许可制机构验证者）→ 未来 PoS 过渡，身份层（KYC/合规）+ 经济层（ARC 质押）双层安全模型；
- USDC Gas 模型：稳定币计价交易费用、无波动性原生代币依赖、可预测的美元成本、对机构财务/审计的简化意义；
- EVM 兼容性：完整 EVM 支持，开发者可使用现有框架和工具；
- 可选隐私控制：合规导向的 selectively shielded balances、opt-in configurable privacy、机构审计可见性保留；
- CCTP V2 跨链协议：原生 1:1 USDC 跨链、覆盖 18+ 网络、Q3 2025 季度交易量 $31B（740% YoY）；
- 抗量子设计：4 阶段路线图（主网 PQ 签名 opt-in → 隐私状态保护 → 基础设施加固 → 验证者认证升级）；
- MEV 保护：私有/加密 mempool、TEE 驱动的区块构建、密封竞价拍卖。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Circle 平台服务栈与支付场景适配

分析 Circle 在 Arc 上构建的平台服务如何形成完整的支付/结算/FX 闭环，以及各服务对不同支付场景的适配能力。

必须覆盖：

- Circle StableFX：机构级稳定币外汇引擎，RFQ 执行模式、24/7 链上结算（支付与交付原子化）、资本效率设计（可编程结算窗口/轧差）、准入门槛（KYB/AML 审查）；
- Circle Partner Stablecoins 计划：8 个首批合作稳定币（BRLA-巴西、KRW1-韩国、PHPC-菲律宾、AUDF-澳大利亚、MXNB-墨西哥、JPYC-日本、QCAD-加拿大、ZARU-南非）、准入标准（技术/运营/储备/风控）、与 USDC 的互操作性、对多币种结算的意义；
- Circle Payments Network (CPN)：自 2025.05 上线以来年化数十亿美元交易量、连接金融机构/PSP/VASP/企业、全球支付结算网络定位；
- 其他平台服务：Mint（稳定币铸造/赎回）、Wallets（可编程钱包）、Contracts（智能合约部署）、Gateway（法币出入金）、Paymaster（费用赞助）；
- 支付场景映射：跨境支付/汇款（亚秒终局+稳定币费用+CCTP 跨链）、机构 FX 结算（StableFX+多币种稳定币）、资本市场结算（代币化抵押品+亚秒终局）、Agentic Commerce（AI Agent 微交易/自主支付）、点对点支付、商户收单/电商结算；
- 各场景的未解决问题：法币出入金依赖、退款/争议机制、商户 reconciliation、合规管辖权。

- **Priority**: high
- **Dependencies**: item-2

### item-4: ARC 代币经济学与治理框架

深入分析 ARC 代币的设计逻辑、价值捕获机制和治理结构，以及作为上市公司发行原生代币的先例意义和风险。

必须覆盖：

- 代币基本参数：初始总量 100 亿、分配比例（60% 生态/25% Circle/15% 长期储备）、预售详情（740M 代币 @ $0.30、$222M 总额、$3B FDV）；
- ARC 五大结构功能：经济对齐（质押/委托/安全）、平台效用（费用折扣/全栈服务准入）、费用捕获（转换/销毁/分配）、治理（经济参数投票）、扩展效用面（多链/专用通道/准入控制）；
- 费用转换与销毁机制：所有费用（USDC/稳定币/ARC）在协议层转换为 ARC → 分配给验证者/质押者 + 永久销毁，MEV 拍卖收入同样路由；
- 通胀模型：衰减通胀，初始 ~2-3% 年化 → 目标通胀中性（销毁完全抵消新增发行），不保证固定时间线；
- 质押机制：PoA → PoS 过渡、许可制验证者出块、代币持有者委托质押、奖励来源（通胀发行+费用衍生收入）；
- 治理框架：共享责任制、渐进去中心化、四类参与者（代币持有者/验证者/Circle/建设者）、五个决策域的初始治理分工；
- 投资者保护条款：代币未交付或网络未完成过渡则 2028.05.08 前回购权；
- 先例意义与风险：首家上市公司进行代币预售、证券分类风险、Circle 25% 持仓的治理集中度。

- **Priority**: high
- **Dependencies**: item-2

### item-5: 机构生态与合作方版图

梳理 Arc 测试网阶段已公开的 100+ 机构参与者，按类别分析其参与深度和对 Arc 生态的意义，避免将 logo 列表过度解读为深度集成。

必须覆盖：

- 资本市场机构：Apollo、BNY、ICE（纽交所母公司）、State Street、Invesco — 代币化资产/抵押品结算方向；
- 银行/资管：BlackRock、Goldman Sachs、HSBC、Deutsche Bank、Société Générale、Standard Chartered、Commerzbank、Emirates NBD、SBI Holdings — 跨境结算/FX/财资管理方向；
- 支付/金融科技：Mastercard、Visa、AWS、Coinbase、Kraken、Brex、Mercoin、dLocal、Corpay、Nuvei — 支付网络/商户服务/法币出入金方向；
- DeFi/基础设施：MetaMask、Ledger、Chainlink、Uniswap Labs、Aave、Curve、Cloudflare、Alchemy — 开发者工具/流动性/预言机方向；
- 区域稳定币发行方：BRLA、KRW1、PHPC、AUDF、MXNB、JPYC、QCAD、ZARU — Partner Stablecoins 计划的落地载体；
- 参与深度评估：测试网参与 ≠ 主网承诺 ≠ 深度产品集成，需要区分信号强度（测试网注册/验证者候选/产品集成/公开 use case）；
- $222M 预售投资人与 $500M Tempo 投资人的重叠/差异分析。

- **Priority**: medium
- **Dependencies**: item-1

### item-6: 与 Tempo 的方案对比

建立 Arc 与 Tempo 的系统性对比，从项目背景、技术路线、支付机制、生态策略和发展阶段多维度分析差异与互补性。

必须覆盖：

- 项目背景对比：Circle（稳定币发行方/上市公司）vs Stripe/Paradigm（支付平台/VC），$222M@$3B FDV vs $500M@$5B、发展阶段（Arc 测试网/主网待上线 vs Tempo 2026.03 主网已上线）；
- 技术路线差异：Malachite BFT（Tendermint 衍生/Rust）vs Commonware Simplex BFT（自研/Rust）、亚秒终局 vs ~600ms 终局、验证者模型差异；
- 支付机制差异：Arc 全链 USDC Gas vs Tempo 稳定币 Gas（attodollars 计价）、Arc 无支付专用 blockspace vs Tempo Payment Lane（区块空间分区保障支付 SLA）、Arc StableFX（机构 FX）vs Tempo StablecoinDEX/Fee AMM、Arc 可选隐私（selectively shielded）vs Tempo 可选隐私 + Zones（企业隐私 L2 validium）；
- 稳定币标准差异：Arc 沿用 ERC-20 + Circle 原生发行 vs Tempo TIP-20 协议级预编译标准（固定 6 位小数/memo/pause/role-based access）；
- 生态策略差异：Arc 侧重金融机构/资本市场（BlackRock/Goldman Sachs/ICE）vs Tempo 侧重商户/支付/平台（Stripe 商户网络/DoorDash/Shopify/Klarna）；
- AI/Agent 支付：Arc Agentic Commerce（目标场景但具体 SDK 待上线）vs Tempo Machine Payments Protocol（MPP，已有 Visa AI Agent 支付集成）；
- 共同点：稳定币 Gas（无波动性代币）、EVM 兼容、可选隐私、机构验证者模型、GENIUS Act 合规基础；
- 互补性分析：Arc 可作为机构 FX/结算层，Tempo 可作为商户/支付路由层，二者在跨链稳定币流动性上可能互联。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-5

### item-7: 与 Mantle 生态的潜在关联与竞争分析

将 Arc 分析落地到 Mantle 可执行的判断，涵盖竞争威胁评估、可借鉴设计和合作可能性。

必须覆盖：

- 竞争维度分析：Arc 作为新 L1 vs Mantle 作为 Ethereum L2，定位不同但机构稳定币结算量存在分流风险；USDC 在 Mantle 为桥接版本（非 Circle 原生发行）；Arc 可能虹吸 DeFi 协议（Uniswap/Aave/Curve 均参与 Arc 测试网）；
- 可借鉴的设计：
  1. 稳定币 Gas 模型：USDC 计价费用消除波动代币依赖，Mantle 可通过 Paymaster 实现类似 UX 但无需协议层改造；
  2. 可选隐私控制：合规导向的 selectively shielded balances，对 Mantle 企业客户有参考价值；
  3. StableFX 链上 FX 引擎：RFQ + 原子化结算模式，Mantle DeFi 生态可考虑类似机构 FX 协议；
  4. CCTP/跨链稳定币流动性：Arc 作为 USDC 原生结算层的跨链流动性优势，Mantle 需评估 CCTP 集成的优先级；
  5. 机构验证者模型：许可制验证者 + 经济层（质押），对 Mantle 企业级部署有参考；
- 不适合直接照搬的设计：Arc 是全新 L1 而非 OP Stack L2，共识引擎/费用模型/隐私层无法直接移植到 Mantle 架构；
- 潜在合作路径：CCTP 跨链桥（Arc ↔ Mantle USDC 流动性互通）、DeFi 协议在两个链上的双重部署、机构客户共享、稳定币 FX 流动性互联；
- 对 Mantle 路线的建议：短期（Paymaster 稳定币 Gas UX、CCTP 集成评估）、中期（机构 FX 协议、企业隐私模块）、长期（支付赛道战略定位）。

- **Priority**: high
- **Dependencies**: item-3, item-5, item-6

### item-8: 风险、开放问题与支付赛道趋势

集中列出 Arc 的关键风险和不确定性，以及支付链赛道的宏观趋势判断。

必须覆盖：

- 执行风险：主网尚未上线（预计 2026 夏季）、测试网数据不代表主网表现、PoA → PoS 过渡时间表未定；
- 中心化风险：初期 Circle 主导验证者准入/协议规则/财政/网络管理，去中心化路线依赖渐进治理移交；
- 代币经济学风险：$222M 预售投资者保护条款（2028.05 回购权）、通胀中性目标不保证实现、Circle 25% 持仓的治理集中度、首家上市公司代币预售的监管不确定性；
- 竞争风险：Tempo 已上线主网且生态策略更激进、通用 EVM 链（Ethereum/Base/Solana）流动性和开发者社区更成熟、Tether Plasma 等竞品同期布局；
- 技术不确定性：Malachite BFT 在大规模验证者集下的实际表现、可选隐私的具体实现细节待主网验证、抗量子设计的性能影响；
- 支付场景适配限制：链上最终性 ≠ 法币清结算/合规最终性、退款/争议机制缺失、商户 reconciliation/PSP API 层缺口、法币出入金依赖外部服务；
- 支付赛道趋势判断：稳定币发行方垂直整合（Circle Arc、Tether Plasma）vs 支付平台水平扩展（Stripe Tempo）、GENIUS Act 后银行/金融科技入场的竞争加剧、机构采用从"测试网参与"到"生产级部署"的鸿沟。

- **Priority**: high
- **Dependencies**: all

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| component | Arc 生态中的具体组件：Malachite BFT、USDC Gas、EVM Runtime、Privacy Layer、CCTP、StableFX、Partner Stablecoins、CPN、ARC Token、Paymaster 等 | all |
| source_evidence | 官方文档、白皮书、博客、公告、测试网数据或二级资料；关键事实必须给出可追溯来源 | all |
| evidence_confidence | 证据置信度：`verified-primary`（官方文档/白皮书）、`verified-testnet`（测试网数据）、`official-announcement`（公告/博客）、`inferred`（推理）、`stale-needs-refresh`（可能过期）、`speculative`（推测） | all |
| date_verified | 对易过期事实的验证日期，至少包括测试网状态、合作伙伴、融资、代币参数和性能数据 | item-1, item-2, item-5, item-8 |
| payment_scenario | 跨境支付、机构 FX 结算、资本市场结算、商户支付、Agentic Commerce、点对点支付、代币化资产 | item-3, item-6, item-7 |
| payment_value | 该组件对支付产品带来的价值：亚秒终局、费用可预测、合规隐私、跨链流动性、原子化结算、多币种支持 | item-2, item-3, item-6 |
| limitation | 未解决问题、适用条件、信任假设、合规边界或实现成熟度 | all |
| mantle_relevance | 对 Mantle 的关联：直接可借鉴、需改造后借鉴、长期 blueprint、仅作竞品观察、不建议采纳 | item-6, item-7, item-8 |
| token_function | ARC 代币的功能维度：经济对齐、平台效用、费用捕获、治理、扩展效用面 | item-4 |
| comparison_dimension | 与 Tempo 的对比维度：项目背景、共识机制、支付机制、稳定币标准、隐私方案、生态策略、AI/Agent 支付、发展阶段 | item-6 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | Arc 五层架构分层图：Arc Core（共识/终局/Gas/隐私/验证者）→ Assets & Protocols（USDC/稳定币/ARC/代币化资产）→ Protocol Services（CCTP/Wallets/StableFX/CPN）→ Developer Kits（Earn/Trade/Bridge/Agent SDK）→ Applications（DeFi/支付/钱包/Agents），旁边标注 ARC coordination layer 贯穿全栈 | mermaid flowchart | item-2, item-3 |
| diag-2 | flow | ARC 费用转换与代币经济学流程图：用户以 USDC/稳定币/ARC 支付交易费用 → 协议层统一转换为 ARC → 分流为验证者/质押者补偿（分配端）和协议销毁（供给缩减端）→ 通胀发行（引导阶段）→ 目标通胀中性 | mermaid flowchart | item-4 |
| diag-3 | comparison | Arc vs Tempo 多维对比矩阵：维度包括项目背景、共识机制、终局时间、Gas 模型、支付 blockspace、稳定币标准、隐私方案、FX 能力、AI/Agent 支付、机构生态、发展阶段、估值/融资、Mantle 可借鉴性 | markdown table | item-6 |
| diag-4 | timeline | Arc 发展时间线：litepaper 2025.08 → 公测 2025.10 → 244M 交易 → 白皮书 2026.05 → $222M 预售 → 主网预计 2026 夏季 → PoA→PoS 过渡（未定），对照 Tempo 和 GENIUS Act 时间节点 | mermaid gantt | item-1, item-6 |
| diag-5 | flowchart | Circle 平台服务与支付场景映射图：左侧列出支付场景（跨境/FX/资本市场/商户/Agent），右侧列出 Arc 服务组件（StableFX/Partner Stablecoins/CPN/CCTP/Paymaster），连线标注适配关系和未解决缺口 | mermaid flowchart | item-3 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | Arc 官网、官方文档（arc.io, docs.arc.io），覆盖架构、共识、Gas、隐私、开发者工具 | 3 |
| src-2 | whitepaper | ARC 代币白皮书（2026年5月），覆盖代币分配、五大功能、费用机制、通胀模型、治理框架 | 1 |
| src-3 | official_announcement | Circle 官方博客/公告，覆盖 Arc 发布、公测上线、StableFX、Partner Stablecoins、2026 产品愿景 | 4 |
| src-4 | official_blog | Arc 博客技术文章，覆盖 Malachite 共识、确定性终局、Gas 机制、抗量子设计 | 3 |
| src-5 | industry_reports | 主流财经/加密媒体对 $222M 预售的报道，覆盖投资人列表、估值、条款 | 2 |
| src-6 | existing_research | 本仓库已有 Tempo 研究：202606-internal-sharing/outlines/payment-tempo.md 和 202606-internal-sharing/research-sections/payment-tempo/ | 1 |
| src-7 | official_docs | Tempo 官方资料（用于对比），覆盖技术架构、Payment Lane、TIP-20、Zones | 2 |
| src-8 | official_announcement | Circle 基础设施报告（Internet Financial System Report），覆盖 CCTP 数据和生态概览 | 1 |

## Evidence Starting Points

- Arc official website: `https://www.arc.io/`
- Arc documentation: `https://docs.arc.io/`
- ARC Token Whitepaper (PDF, May 2026): `https://6778953.fs1.hubspotusercontent-na1.net/hubfs/6778953/PDFs/arc_whitepaper.pdf`
- Arc blog - Malachite consensus: `https://www.arc.io/blog/arcs-deterministic-finality-the-bespoke-consensus-layer-built-using-malachite`
- Arc blog - Quantum-resistant design: `https://www.arc.io/blog/arcs-quantum-resistant-design-and-roadmap-why-it-matters`
- Circle blog - Arc introduction: `https://www.circle.com/blog/introducing-arc-an-open-layer-1-blockchain-purpose-built-for-stablecoin-finance`
- Circle pressroom - Arc testnet launch: `https://www.circle.com/pressroom/circle-launches-arc-public-testnet`
- Circle blog - StableFX & Partner Stablecoins: `https://www.circle.com/blog/introducing-circle-stablefx-and-circle-partner-stablecoins`
- Circle blog - 2026 product vision: `https://www.circle.com/blog/building-the-internet-financial-system-circles-product-vision-for-2026`
- Circle report - Arc and Circle infrastructure: `https://www.circle.com/reports/internet-financial-system/arc-and-circle-infrastructure`
- $222M presale coverage: `https://www.theblock.co/post/400709/circle-raises-222m-in-arc-token-presale-at-3b-fdv-from-a16z-crypto-blackrock-and-others-q1-revenue-up-20`
- Existing Tempo outline: `202606-internal-sharing/outlines/payment-tempo.md`
- Existing Tempo research sections: `202606-internal-sharing/research-sections/payment-tempo/`
- Tempo official site: `https://tempo.xyz/`

## Draft Structure Recommendation

1. Executive summary：Arc 的支付链定位、最重要结论和对 Mantle 的一句话启示。
2. 项目定位与战略愿景：Circle 战略转型、"Economic OS" 定位、发展时间线、GENIUS Act 背景。
3. 技术架构深度分析：Malachite BFT 共识、USDC Gas 模型、EVM 兼容、可选隐私、CCTP 跨链、抗量子设计、MEV 保护。
4. Circle 平台服务栈与支付场景：StableFX、Partner Stablecoins、CPN、各支付场景映射与未解决缺口。
5. ARC 代币经济学与治理：分配、五大功能、费用转换/销毁、通胀模型、治理框架、上市公司代币预售先例。
6. 机构生态与合作方：按类别梳理 100+ 机构参与者、参与深度评估。
7. 与 Tempo 的方案对比：项目背景、技术路线、支付机制、稳定币标准、生态策略、AI/Agent 支付、互补性分析。
8. 与 Mantle 生态的关联：竞争威胁评估、可借鉴设计、潜在合作路径、路线建议。
9. 风险与开放问题：执行/中心化/代币/竞争/技术/场景适配风险、支付赛道趋势判断。
10. Source appendix：列出所有 primary source 和置信度标注。

## Quality Checklist

- [ ] 明确区分 Arc（L1 区块链）与 ARC（原生代币），前者用全小写或首字母大写 Arc，后者全大写 ARC。
- [ ] 所有测试网数据（244.1M 交易、终局时间、TPS）标注"测试网"和验证日期，不暗示为主网性能。
- [ ] 合作伙伴参与深度区分为测试网注册/验证者候选/产品集成/公开用例四个层级。
- [ ] 代币经济学数据全部引用白皮书原文，注明 "indicative"/"preliminary" 等官方限定语。
- [ ] 与 Tempo 对比基于已有 payment-tempo 研究和公开资料，不臆造 Tempo 未公开的细节。
- [ ] 链上最终性与法币清结算/合规最终性明确区分，不过度宣传。
- [ ] 至少包含 3 张 Mermaid 图，且图与正文结论一致。
- [ ] 对 Mantle 的建议分为短期（应用层/SDK）、中期（协议/合约）、长期（战略定位），标注工程复杂度。
- [ ] 所有关键结论标注 evidence_confidence，低置信度或推断项不得写成事实。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create | full outline | Initial outline for Circle Arc rerun (previous run analyzed wrong topic - Bitcoin Ark Protocol) | Multica issue e63c9a11-8b78-448a-b9a9-741c2f8e5410 comment ef2791fc-05ec-49df-8932-949878e34694 |
