---
topic: "竞争对手与新兴方向非代码叙事分析（Blog/News/Twitter）"
project_slug: "202606-internal-sharing"
topic_slug: "narrative-analysis"
github_repo: "Whisker17/multica-research"
round: 1
status: draft

artifact_paths:
  outline: "202606-internal-sharing/outlines/narrative-analysis.md"
  draft: "202606-internal-sharing/research-sections/narrative-analysis/drafts/round-1.md"
  final: "202606-internal-sharing/research-sections/narrative-analysis/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

draft_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-24T00:55:00+08:00"
  outline_path: "202606-internal-sharing/outlines/narrative-analysis.md"
  outline_commit: "f6842858a676e19d459c0f7c2800b61758e21e49"
  outline_approval_source: "Multica comment a98dde4c-f503-4ced-87b0-5fed8b83fb04 (Review Verdict: outline-approved), original Orchestrator deep-draft dispatch a4c1555e-16db-4bd0-9dc4-de9852d270ae, and resume dispatch 348365ee-a01f-42f3-b060-0e6ef821b558"
  outline_file_status_note: "Persisted outline frontmatter remains status:candidate; Orchestrator state approved it for Phase B. This draft does not edit the outline."
  branch_name: "research/202606-internal-sharing/narrative-analysis"
  language: "zh-CN"
  research_depth: "standard"
  evidence_window: "2026-02-24 to 2026-05-24"
  accessed_at: "2026-05-24"
  twitter_x_coverage: "partial; direct full-fidelity X scraping was not available in this pass. Official blogs/newsrooms, docs, embedded social announcements, and reputable media references were used as substitutes. Direct-social cells are marked caveated or absent where evidence was weak."
  guardrails_applied:
    - "Existing internal final sections were used only as background and technical baselines; narrative claims are supported with fresh public evidence from 2026-02-24 to 2026-05-24 or labeled stale/background."
    - "Weak source-matrix cells are marked absent, inferred, or caveated instead of being padded with low-signal social posts."
    - "Volatile metrics and status claims include source date and accessed date where used."
  items_covered: [item-1, item-2, item-3, item-4, item-5, item-6, item-7, item-8]
  fields_investigated:
    - project
    - project_group
    - source_channel
    - source_url
    - published_at
    - accessed_at
    - evidence_level
    - narrative_theme
    - narrative_claim
    - audience_target
    - evidence_strength
    - narrative_change
    - mantle_implication
  diagrams_produced: [table-1, matrix-1, matrix-2, map-1, playbook-1]
---

# 竞争对手与新兴方向非代码叙事分析 - Round 1 Draft

## 1. Executive Summary

本研究窗口固定为 **2026-02-24 至 2026-05-24**，关注 10 个项目的非代码叙事：Solana、Tempo、Circle Arc、Hyperliquid、Base、Optimism、Arbitrum、ZKsync、Starknet、Canton。结论不是"所有链都在讲同一个故事"，而是市场叙事正在从过去的低费、TPS、泛开发者生态，转向四类更具体的控制权竞争：**稳定币/支付入口、机构/RWA 信任、专用执行环境、链上流动性与分发渠道**。

独立 L1 / 专用链阵营的叙事更进攻。Solana 用高性能、PayFi/RWA/consumer 生态把自己从 meme/零售流量重新包装成可承载真实经济活动的高吞吐网络；Tempo 和 Circle Arc 把稳定币支付推进到"链本身为支付设计"的垂直路线，前者依托 Stripe/Paradigm 与 Payment Lane，后者依托 Circle/USDC、StableFX、Partner Stablecoins 和 Arc Economic OS；Hyperliquid 则把链上永续、HyperEVM、HIP-3 permissionless markets 和 HYPE 资产表现合成"加密金融流动性中心"叙事。它们共同挤压 Mantle 的支付、流动性和高性能叙事空间。

Ethereum L2 阵营更像在争夺生态编排权。Base 的优势不是单纯技术，而是 Coinbase 分发、Base-owned client/performance roadmap、Flashblocks、资产发行/合规原语和 onchain economy 品牌；Optimism 强化 Superchain interoperability、标准化治理和 OP Stack / op-reth 迁移；Arbitrum 通过 Stylus、Timeboost、BoLD、Orbit 讲"金融原生 + 可定制 Nitro stack"；ZKsync 则把 Elastic Chain/Gateway、Airbender、ZKsync OS、native AA 和 Prividium 打包为 correctness + privacy + enterprise 路线；Starknet 近期更明显地把 STARK 技术叙事连接到 Bitcoin/BTCFi、性能路线和隐私/证明能力。

企业级方向中，Canton 与 Arc/Tempo/ZKsync Prividium 形成鲜明对照。Canton 不是通用 DeFi 公链，而是面向机构多方工作流的 need-to-know privacy 网络；它的叙事重心是 capital markets workflow、tokenized collateral、互操作和合规隐私。对 Mantle 来说，Canton 的启示不是迁移 Daml/Canton 栈，而是如果要讲 RWA/企业/机构，必须补足隐私边界、审计角色、身份/准入、真实合作深度和数据口径。

对 Mantle 的核心建议：短期不要泛泛复制"稳定币/RWA/AI/机构"热词，而应把叙事压成一句可验证定位：**Ethereum-aligned modular high-performance L2 for yield, liquidity, and institution-ready settlement**。证明点应优先围绕 MNT / mETH / cmETH / yield-bearing 生态、EigenDA / modular DA、EVM/OP 兼容、DeFi 流动性、稳定币支付 UX 原型、企业 L3/private DA PoC，而不是空泛 TPS 或没有合作证据的机构 logo。中期要补叙事证据：可公开 dashboard、稳定币 paymaster/merchant demo、RWA/treasury 案例、developer distribution、privacy/compliance PoC、以及与 Base/Arbitrum/Optimism/ZKsync 不同的 L2 整合路径。

## 2. Methodology: 研究窗口、来源边界与编码方法

**研究窗口**：2026-02-24 至 2026-05-24。所有叙事 claim 默认要求在此窗口内有公开证据；更早信息仅作为 `[stale/background]`，不单独支撑"近期变化"。访问日期统一记录为 2026-05-24，除仓库内既有 final section 已记录的访问日期外，本 draft 不再重写其历史访问时间。

**来源层级**：

| 等级 | 来源类型 | 用法 |
|---|---|---|
| official-primary | 官方 blog、newsroom、docs、whitepaper、status page | 支撑项目自我叙事、产品状态、路线图 |
| official-social | 官方 X/Twitter、官方社媒 cross-post、嵌入社媒公告 | 支撑传播重点；本轮 direct X 覆盖 partial |
| media-reported | CoinDesk、The Block、Blockworks、Fortune Crypto 等 | 支撑媒体放大和市场解读；不替代官方状态 |
| data-supported | DeFiLlama、官方 dashboard、链上/财务报告 | 支撑 TVL、费用、交易量等 volatile facts |
| ecosystem-signal | 生态 newsletter、合作伙伴公告、开发者文档 | 补充 adoption/生态方向 |
| internal-research | 仓库内已完成 final sections | 只作背景/技术 baseline；叙事 claim 需新证据或标注 stale/background |
| inferred / caveated | 多源间接推断或证据不足 | 必须显式标注，不作为强结论 |

**Twitter/X 限制**：本轮没有完整抓取每个官方账号 3 个月推文、互动数和转推网络。因此，"社交媒体"只在有官方 cross-post、博客嵌入、媒体引用或可核验公开贴时作为证据；否则在 source coverage 中标注 `[caveated]` 或 `[absent]`。这避免把搜索结果片段或低信号社媒转述填成强证据。

**叙事编码字段**：每条项目结论按主题、目标受众、claim、事实支撑、发布日期、渠道强度、媒体放大、风险/caveat、对 Mantle 相关性编码。摘要必须包含：当前主叙事、近三个月变化、证据强度、Mantle 启示。

**Grok 参考处理**：issue 描述中的 Grok 参考分析只作为 hypothesis backlog。本稿对 Tempo、Arc、Base、Optimism、Arbitrum、ZKsync、Canton 复用了仓库内已审 final section 的技术和事实 baseline，但近期叙事表述仍要求使用 2026-02-24 至 2026-05-24 公开信息核验或标注 caveat。

## 3. Project Findings

### 3.1 Solana: 从高性能零售链扩展到 PayFi / RWA / consumer rails

**当前主叙事**：Solana 仍保留高性能、低成本、consumer/retail 的心智，但近三个月官方和生态传播明显在把高吞吐性能重新绑定到真实经济活动：PayFi、稳定币支付、RWA、mobile / consumer app、AI agent / machine economy 和机构采用。Solana Foundation 2026-05-11 的 April ecosystem roundup 把 institutional commitments、tokenized assets、stablecoins/payments、agentic commerce、consumer apps 和 protocol infrastructure 放在同一叙事框架中，显示 Solana 不想只被定义为 meme/零售链，而是在用"高性能公链 + 大众分发 + 支付/RWA/AI 应用"争夺更宽的应用层心智（source: Solana Foundation news, 2026-05-11, accessed 2026-05-24）。

**近三个月变化**：Solana 的变化不是放弃 meme/consumer，而是把 consumer traffic 与机构支付/RWA 连接起来。Solana Foundation 2026-05-05 宣布与 Google Cloud 合作推出 Pay.sh，面向稳定币支付和 AI commerce / agent commerce 的更简化付款入口；该公告强调 Google Cloud 支持、stablecoin checkout 和开发者集成，表明 Solana 正在把"支付可用性"作为外部叙事抓手（official-primary, 2026-05-05, accessed 2026-05-24）。同时，媒体在 2026 年春季持续讨论 Solana 在稳定币转账、RWA tokenization、DePIN/AI 等主题中的增长，但这些媒体表述常混合链上数据、生态营销和市场价格，不能全部视为官方战略。

**证据强度**：medium-high。官方新闻能够支撑 PayFi / stablecoin checkout / AI commerce 的叙事变化；RWA 与机构采用需要更多一手项目级证据和链上口径，本文不复述未核验的"稳定币占比 35.5%"等数字。Solana 的 direct X 覆盖在本轮为 `[caveated]`，只把官方新闻与媒体覆盖作为主证据。

**对 Mantle 启示**：Solana 的威胁在于它能把性能、consumer distribution 和支付/RWA 讲成一条线。Mantle 若只说低费 EVM，会被 Solana 的 consumer + PayFi 叙事覆盖。更好的应对是强调 Ethereum-aligned settlement、yield-bearing ecosystem、机构可组合性和 EVM 开发者迁移成本低，同时用稳定币支付 demo 和真实 DeFi/RWA 流动性证明 Mantle 也能承载真实金融活动。

### 3.2 Tempo: 支付优先 L1，把稳定币支付做成协议叙事

**当前主叙事**：Tempo 的公开定位是 payments-first blockchain / stablecoin payment rail。相较普通 EVM 链把支付作为应用场景，Tempo 把支付交易分类、稳定币 gas、fee sponsorship、memo/reconciliation、合规策略和企业隐私 Zone 作为协议与客户端能力来讲。Tempo 官网在访问日显示 "Mainnet is live"，docs 把 Stablecoin Payments 拆成 memos、任意稳定币付费、fee sponsorship 和并行交易；Payment Lane spec 明确用 `general_gas_limit` 为非支付交易设约束，使支付交易在拥堵期仍有 blockspace（source: tempo.xyz and docs.tempo.xyz, accessed 2026-05-24）。仓库内 payment-tempo final 进一步核验，Tempo public repo 支持 mainnet/Presto 服务存在，mainnet/Presto T4 激活时间在代码中为 2026-05-18 14:00 UTC；Zones 仍需按 early/testnet 性质处理，因为公开代码中 proof validation 仍为空 stub（internal-research baseline, accessed 2026-05-24）。

**近三个月变化**：Tempo 的叙事从"Stripe/Paradigm 背景的支付链"向"支付专用 blockspace + machine/agent payments + institutional validation"深化。核心传播点包括 Payment Lane、稳定币支付 gas、Machine Payments Protocol / agent commerce、merchant / platform / payroll 等高频支付场景。Visa 2026-04-14 宣布在 Tempo 上运行 validator node，官方口径是把 Visa 的可靠性、安全和信任标准延伸到稳定币支付网络（source: Visa investor news, 2026-04-14, accessed 2026-05-24）。但 partner logo 与 validator 参与仍不等同于 production payment volume；本文不采纳未核验的具体商户/银行生产深度说法。

**证据强度**：medium-high for product positioning and docs; medium for adoption。Tempo 官网/docs、Payment Lane spec 和 Visa validator announcement 能支撑支付优先叙事；partner、mainnet adoption、SLA 和生产性能仍保持 caveat。

**对 Mantle 启示**：Tempo 对 Mantle 的压力不是规模，而是表达精确度。它把"支付链"拆成了可感知产品能力：stablecoin gas、payment lane、fee sponsorship、memo、policy registry、enterprise zone。Mantle 要讲支付，短期应优先做 paymaster / 稳定币 gas UX、merchant checkout demo、memo/reconciliation 标准和 access-key-like spending policy，而不是泛称"低费适合支付"。

### 3.3 Circle Arc: USDC 发行方转向 stablecoin finance L1 / Economic OS

**当前主叙事**：Arc 是 Circle 从 USDC 发行方转向全栈金融基础设施提供者的战略载体。官方把 Arc 定义为 stablecoin finance / Economic OS for the internet：USDC gas、EVM compatibility、CCTP、StableFX、Partner Stablecoins、可选隐私、机构验证者和未来 PoS。Arc 的叙事优势来自 Circle 的发行方地位，而不是纯链性能；它能把 stablecoin liquidity、issuer relationship、FX、支付网络和合规监管包装为一个平台。

**近三个月变化**：2026 年 5 月 Arc 叙事出现明显金融化和代币化升级。仓库内 payment-ark final 直接解析 ARC whitepaper PDF：截至 2026-05-05，Arc testnet 处理 244.1M transactions；`[stale/background]` Circle 2026-01-29 product vision 的较早口径曾提到 first 90 days 150M+ transactions；mainnet beta / launch 仍是 2026 年夏季预期，无具体日期（source date: 2026-05 whitepaper / Arc and Circle official materials; accessed: 2026-05-23/24）。Circle 2026-05-11 Q1 2026 results 官方披露 ARC Token $222M presale、$3B fully diluted network valuation，以及 a16z crypto、BlackRock、ICE、Standard Chartered Ventures 等投资方；更细的条款和投资者保护机制若来自媒体，仍按 secondary-only 处理。

**证据强度**：high for official product positioning, whitepaper testnet metrics, and official presale amount/valuation disclosure; medium for detailed presale terms if only media-reported。Arc 的强证据来自 Circle 官方白皮书、Circle blog/pressroom、Q1 2026 results 和产品文档。主网状态仍为未来/预计，不得写成已上线。

**对 Mantle 启示**：Arc 是 Mantle 在稳定币/RWA/机构叙事上的强威胁，因为它拥有 USDC 原生入口和机构合规品牌。Mantle 不应正面复制"USDC-native L1"叙事，而应讲 Ethereum L2 上的多资产、多收益、多生态 settlement：与 CCTP、USDC、mETH/cmETH、RWA tokenization、DeFi treasury 结合，证明 Mantle 是稳定币/RWA 的组合层和收益层，而不是发行方自有结算链的替代品。

### 3.4 Hyperliquid: 永续流动性中心，把 DeFi 收入和 HYPE 资产表现变成链叙事

**当前主叙事**：Hyperliquid 的外部叙事是 crypto-native financial infrastructure：先通过 perp DEX 和 HyperCore 获得交易流动性与收入，再通过 HyperEVM、HIP-3 builder-deployed perpetuals、permissionless markets、HYPE 资产表现扩展为链上金融中心。它不是先讲通用开发者生态，而是用交易量、费用、代币和流动性建立金融注意力。官方 HIP-3 docs 明确 builder-deployed perps 是把 perp listing process 向 permissionless 方向推进的里程碑，并规定 market deployer、oracle、staking、fee share、slashing 等机制（source: Hyperliquid Docs HIP-3, accessed 2026-05-24）。

**近三个月变化**：2026 年春季，Hyperliquid 叙事从"高性能 perp DEX"扩展到"可部署新金融市场的链上交易基础设施"。HIP-3 / builder-deployed perps 和更广义的 permissionless market 叙事使外部开发者/做市商可以围绕永续、商品、预测市场或新资产类别构建市场；HyperEVM docs 则把 HyperCore 与 HyperEVM 定义为同一 Hyperliquid blockchain 的两个关键部分，试图把交易流动性外溢给 EVM 应用（source: Hyperliquid Docs HyperEVM, accessed 2026-05-24）。媒体和社区在 2026 年持续讨论 HYPE 市值/FDV、fees、TVL 和交易占比，但这些都是高度 volatile 指标，本文不采纳未逐条核验的"$55B TVL / 30 天 fees $50M / FDV 超 Solana"等具体数字。

**证据强度**：medium。官方 docs 与生态材料能支撑 HIP-3 / HyperEVM / permissionless markets 的方向；费用、TVL、FDV 等数字需要 DeFiLlama、TokenTerminal、Coingecko 或官方 dashboard 的逐日口径核验，本稿将其标为 `[volatile-not-reused]`。媒体覆盖可证明叙事热度，但也受 HYPE 价格表现强烈影响。

**对 Mantle 启示**：Hyperliquid 对 Mantle 的威胁是 DeFi 心智，不是支付或企业。它把一条链的价值叙事压缩成"流动性、收入、交易者、代币表现"。Mantle 若要竞争 DeFi narrative，需要更明确的 liquidity flywheel：mETH/cmETH、MNT incentives、perp/options/RWA yield、cross-chain liquidity routing，而不是只把 DeFi 当生态列表。

### 3.5 Base: Coinbase 分发 + Base Stack + onchain economy

**当前主叙事**：Base 的叙事核心是 global onchain economy，但真正护城河是 Coinbase 分发与 Base-owned technical roadmap 的结合。Base 2026-03-31 strategy 将 2026 聚焦为 building global markets、scaling payments and stablecoins、being the home for builders，并把稳定币支付、tokenized markets、AI agents 与 Base App/Builder ecosystem 连接起来（source: Base blog, 2026-03-31, accessed 2026-05-24）。官方和既有 final section 显示，Base 正在通过 `base-node-reth`、`base-consensus`、Flashblocks、Multiproof、Beryl / Token Factory / Policy Registry 等方向，把自己从 OP Stack L2 推进成 Coinbase 主导的 Base Stack。注意：Base 仍是 Ethereum rollup，不应写成完全脱离 Superchain 或 OP 生态。

**近三个月变化**：Base 的近期非代码传播重点包括 onchain commerce、稳定币支付、开发者增长、Token Factory / compliance primitive、Flashblocks low-latency UX、以及 Coinbase 产品入口。Base 2026-04-21 Azul blog 称 Azul 是 Base first independent network upgrade，目标主网激活 2026-05-13，并将 client stack 收敛到 `base-reth-node` 和 `base-consensus`；同文提到 empty blocks 下降和多次 5,000 TPS bursts，但这仍是官方 benchmark / burst 口径，不是 sustained mainnet TPS（source: Base blog, 2026-04-21, accessed 2026-05-24）。仓库内 competitor-base final 核验：截至 2026-05-23，`base/base@92abf0a` 中 Beryl 的 B20Factory、PolicyRegistry、ActivationRegistry 等已密集合并，但 mainnet/sepolia/devnet/zeronet 的 `beryl_timestamp` 仍为 `None`；因此 Beryl 是 merged-code behind activation gates，不是已上线能力。

**证据强度**：high for engineering direction and official Base/Coinbase positioning; medium for performance claims。Base 叙事有强公开技术和产品证据，但所有 TPS、稳定币量、活跃地址、TVL 这类 live metrics 都需要演示前刷新。

**对 Mantle 启示**：Base 是 Mantle 最直接的 L2 心智竞争者，因为它能把低费 EVM、用户入口、开发者工具、稳定币支付和资产发行全部绑定到 Coinbase。Mantle 的应对不是说"我们也是 L2"，而是强调与 Coinbase 分发不同的优势：MNT/mETH yield、modular DA/EigenDA、亚洲/全球生态、DeFi liquidity、institution-ready settlement、以及更中立的 Ethereum-aligned settlement layer。

### 3.6 Optimism: Superchain 标准化、互操作与治理网络

**当前主叙事**：Optimism 近期叙事是 Superchain as infrastructure：OP Stack、Superchain interoperability、op-supernode / op-supervisor、op-reth/kona、standardization/governance、Retro Funding / Collective。它不再只讲单条 OP Mainnet，而是讲一组共享标准、治理和互操作的 L2 网络。Optimism 2026-03-11 blog 还明确反对单一 TPS 标题数，强调 end-to-end devnet benchmarking、sustained real work、tail latency 和 reproducibility（source: Optimism blog, 2026-03-11, accessed 2026-05-24）。官方与仓库 final section 均显示，Optimism 的近期核心不是零散应用，而是把多链互操作和标准化运维推进成基础设施平台。

**近三个月变化**：competitor-optimism final 对 2026-02-23 至 2026-05-23 的 `ethereum-optimism` org 扫描发现：`optimism` monorepo 在窗口内有 1,202 个新 PR、751 merged；活动集中在 interop / op-supernode / op-supervisor、op-reth/kona、op-deployer、op-contracts v7 release candidates、registry 和 devnet。官方 docs notice 写明 `op-geth` / `op-program` 支持到 2026-05-31，并要求迁移到 `op-reth` / `cannon-kona`，这使 Optimism 叙事从"OP Stack 可复制"推进到"Superchain client stack modernization"（source: Optimism docs notice, accessed 2026-05-24）。

**证据强度**：high for GitHub/org activity and docs notices; medium for market positioning。Base 独立化不等于退出 Superchain；interoperability 也不能写成所有链 mainnet-ready。媒体关于 OP token 或 Base 关系的解读应视为市场反应，不是协议事实。

**对 Mantle 启示**：Optimism 的压力来自标准化与生态网络，而不是单链性能。Mantle 若继续保持 OP/EVM 兼容路线，需要清楚回答：跟随 OP Stack、选择性移植 Base/OP 组件、还是保持 Mantle 自有 DA/economics 差异化。叙事上应避免被归类为"又一条 OP Stack follower"，必须强调 EigenDA / MNT / yield / liquidity / enterprise 的组合差异。

### 3.7 Arbitrum: 金融原生 L2，以 Stylus / Timeboost / BoLD / Orbit 组合差异化

**当前主叙事**：Arbitrum 的近期叙事可概括为 financial layer + customizable Nitro stack。Stylus 扩展多语言/WASM 开发者心智；Timeboost 把 MEV/排序权市场产品化；BoLD 提供 permissionless validation / fraud proof 安全叙事；Orbit / Arbitrum chains 提供 appchain/custom gas/AnyTrust 配置面。Arbitrum Orbit 页面用 "Your Chain, Your Rules" 包装 custom gas token、DA/security choice 和 appchain control；docs 2026-05-19 更新仍把 execution、gas tokens、DA、governance、validation 配置作为开发者入口（source: Arbitrum orbit/docs, accessed 2026-05-24）。与 OP 的 Superchain 标准化、Base 的分发不同，Arbitrum 的叙事是：金融应用可以在 Nitro 生态内获得更多自定义权和排序/执行能力。

**近三个月变化**：competitor-arbitrum final 核验，2026-02-23 至 2026-05-23 窗口内 `OffchainLabs/nitro` 有 257 PR（169 merged），`stylus-sdk-rs` 有 44 PR（31 merged）。强证据在 BoLD/MEL/validator、Timeboost、Stylus SDK hardening、release/CI；Orbit 的近期 Nitro PR title 证据较弱，主要由官方 Arbitrum chains docs、AnyTrust/custom gas token/BoLD/Timeboost adoption docs 支撑。因此近期 Arbitrum 的真实变化更像底层安全、排序、验证和 DX 硬化，而不是 Orbit 代码爆发。

**证据强度**：high for BoLD/Timeboost/Stylus engineering + official docs; medium-low for Orbit as recent-code narrative。Stylus 仍带 public preview / release-candidate 语义，不可写成完全成熟生态；Timeboost 对多数链仍可能是 alpha/not formally supported，需要按链标注。

**对 Mantle 启示**：Arbitrum 对 Mantle 的压力是"差异化技术组合"。Mantle 短期应建立 Arbitrum watchlist：BoLD/Stage 1、Timeboost auction、Stylus SDK、Orbit/AnyTrust adoption。中期可评估 preconfirmation/MEV sharing、企业 L3/custom gas、WASM/alt-VM developer funnel，但需要避免直接复制引入公平性、监管和工具链风险的能力。

### 3.8 ZKsync: Elastic Chain + ZK correctness + enterprise privacy

**当前主叙事**：ZKsync 的叙事从 zkEVM 技术领先，转向 ZK Stack + Elastic Chain / Gateway + ZKsync OS / Airbender + native AA + Prividium。Gateway docs 把 Gateway 定义为 optional shared proof aggregation layer；Prividium docs 则明确它是 licensed product，用 Validium/private DA、permissioning、Proxy RPC、Okta/SIWE 和 selective disclosure 服务机构隐私（source: ZKsync docs Gateway/Prividium, accessed 2026-05-24）。它把正确性证明、互操作、账户体验和企业隐私组合成一条路线，试图与 Optimism 的 Superchain、Base 的分发性能、Arbitrum 的 Nitro customization 区分。

**近三个月变化**：competitor-zksync final 核验，2026-02-23 至 2026-05-23 窗口内 `matter-labs/zksync-era` 有 129 PR（88 merged），主线为 release/protocol upgrade、v31 interop、Gateway、Airbender commitment、DA commitment、API/verifier/prover 正确性。supporting repos 中 `zksync-os`、`zksync-airbender`、`zksync-os-server`、`era-contracts`、`zksync-sso`、`local-prividium` 均有活跃信号。官方 docs 中 ZKsync OS Developer Preview 描述 Airbender proving ERC-20 transfer 约 $0.0001、可水平扩展到约 1 second block proofs；这些只能作为官方 developer-preview claims，不是独立主网指标（source: ZKsync OS docs, accessed 2026-05-24）。

**证据强度**：high for PR/release direction; medium for performance and enterprise adoption。Prividium 是 licensed enterprise module + Validium/private DA product，公开 docs 给出架构和功能，但生产客户、性能和银行合作深度需要逐项验证。

**对 Mantle 启示**：ZKsync 把"ZK + enterprise privacy + AA + interop"打包得很完整，压缩 Mantle 在企业/隐私/正确性叙事上的表达空间。Mantle 不应声称自己已有同等隐私或 ZK 能力；可讲的是 Ethereum-aligned OP/EVM compatibility + modular DA + SP1/OP Succinct validity path watchlist + enterprise L3/private DA PoC。

### 3.9 Starknet: STARK 技术心智转向 Bitcoin/BTCFi、性能和隐私应用

**当前主叙事**：Starknet 的基础叙事仍是 STARK / ZK validity、Cairo、scalability。但近期对外传播更倾向把 STARK 技术与 Bitcoin/BTCFi、性能路线、隐私/证明能力和 STRK governance/staking 连接起来。Starknet 2026-03-05 technical infrastructure roadmap 明确引用 Vitalik "identify a value add other than scaling" 的问题，并把 2026 路线拆成 S-two、Rust Committer、preconfirmations、Starkzap、Bitcoin/stablecoin payments、strkBTC optional privacy 等叙事（source: Starknet blog, 2026-03-05, accessed 2026-05-24）。相比 ZKsync 的 enterprise/Elastic Chain，Starknet 更强调 STARK 技术正统、Bitcoin liquidity 的新应用面，以及 Cairo/STARK 对复杂可验证计算的支撑。

**近三个月变化**：Starknet 2026-03-22 roadmap 把 Phase 4 明确列为 Bitcoin bridge、2-second block time、STRK20 privacy、quantum-resistant cryptography、1k+ sustained TPS / 5k+ max TPS、strkBTC、S-two proof verification within Starknet；这些是 roadmap，不是全部已完成事实（source: Starknet roadmap, last updated 2026-03-22, accessed 2026-05-24）。社区 forum 2026-03-16 的 v0.14.2 pre-release notes 称 v0.14.2 通过 SNIP-36 启用 in-protocol S-Two proof verification，并列出 testnet 2026-03-23、mainnet 2026-04-13；Starknet 官方 2026-04-20 blog 进一步称 v0.14.2 已在 mainnet live，并将其定位为 STRK20 encrypted balances 与 private strkBTC DeFi 的基础设施。strkBTC 方面，2026-05-07 相关报道称 governance approved SNIP-38/SNIP-39，引入 stakable Bitcoin wrapper；本稿将其作为 media-reported / governance signal，而不是官方 production adoption 数据。

**证据强度**：medium。官方 roadmap / technical roadmap 能支撑 BTCFi、performance、proof/privacy direction；v0.14.2 mainnet live 有官方 blog 与 community pre-release notes 支撑，但 STRK20、strkBTC、SNIP 执行、隐私资产和下游应用采用仍需在 final 前逐项复核。

**对 Mantle 启示**：Starknet 的威胁不是当前 TVL 或 EVM 兼容，而是长期 ZK/STARK 技术心智和 BTCFi 叙事。如果 Mantle 要涉及 Bitcoin/BTCFi 或隐私证明，必须有明确产品或合作证据；否则更适合把 Starknet 作为 monitor，而不是直接对标。

### 3.10 Canton: 机构多方工作流、need-to-know privacy 与资本市场网络

**当前主叙事**：Canton 的外部叙事是 institutional public network with privacy：面向金融机构的 tokenized collateral、capital markets workflow、multi-party settlement、need-to-know privacy 和 interoperability。它不是 EVM L2，也不是通用 DeFi 公链，而是 Daml / Canton Protocol / Global Synchronizer 支撑的多机构协作网络。

**近三个月变化**：Canton Network 2026-05-10 官方/基金会 editorial 解释 Global Synchronizer 是 network-of-networks backbone，并强调跨应用 atomic settlement 与 privacy without shared global state；Canton global-synchronizer 页面把 GSF/Linux Foundation governance、Canton Coin incentives、cross-application connections 与 tokenized asset liquidity 作为核心叙事（source: cantonnews.org 2026-05-10 and canton.network page, accessed 2026-05-24）。2026-02-25 Chainlink/Canton announcement 称 Chainlink Data Streams、SmartData NAV/AUM feeds、Proof of Reserve 已在 Canton ecosystem 可用，强化 institutional tokenization data layer。enterprise-canton final 记录的多组 adoption 口径（$2T+ / $1.5T+ / $6T / 400 / 450 / 600）来源日期和定义不一，本稿仍作为 `[stale/background, source-attributed]`，不合并成单一实时指标。JPMD、DTCC、HQLAX 等机构信号须逐项区分 planned、pilot、controlled production 和 production deployment。

**证据强度**：high for architecture / positioning; medium for adoption metrics because dates and definitions differ。Canton 的叙事强在企业隐私和资本市场工作流，但不能把所有 Daml/Canton-family 项目都写成 public Canton Network production deployment。

**对 Mantle 启示**：Canton 说明 ToB/RWA 叙事必须具体到工作流：托管、抵押品、DvP、监管 observer、隐私边界、审计导出、机构准入。Mantle 若只说"RWA ready"会显得空；应先做企业 L3/private DA、permissioned settlement、proof/audit dashboard、身份/准入和合作伙伴深度分级。

## 4. Table 1: 项目叙事摘要表

| 项目 | 当前主叙事 | 近 3 个月变化 | 证据强度 | 对 Mantle 的直接压力 |
|---|---|---|---|---|
| Solana | 高性能 consumer + PayFi/RWA/AI commerce | 官方新闻把 pay.sh、AI、consumer、DeFi、mobile 与高吞吐网络绑定 | medium-high | consumer + payments + high-performance 心智 |
| Tempo | payments-first stablecoin L1 | 从支付链定位深化到 Payment Lane、stablecoin gas、agent/merchant payments、Visa validator | medium-high, adoption caveated | 支付产品表达精确度 |
| Circle Arc | USDC-native stablecoin finance L1 / Economic OS | ARC whitepaper、testnet metrics、mainnet beta summer 2026、presale media 放大 | high official / medium media | 稳定币发行方 + 机构合规品牌 |
| Hyperliquid | 链上金融流动性中心 | HIP-3/HyperEVM 将 perp liquidity 扩成 permissionless financial markets | medium | DeFi liquidity / trader mindshare |
| Base | Coinbase-distributed global onchain economy | Base-owned client、Flashblocks、Beryl asset/compliance primitives 持续推进 | high | L2 用户分发、开发者入口、支付/资产发行 |
| Optimism | Superchain interoperability + standardization | op-supernode/supervisor、op-reth/kona、registry/devnet 活跃 | high | OP Stack 标准化网络效应 |
| Arbitrum | financial layer + customizable Nitro stack | BoLD、Timeboost、Stylus hardening；Orbit 近期代码证据较弱 | high for core / medium-low Orbit | 多 VM、MEV、appchain 定制叙事 |
| ZKsync | Elastic Chain + ZK OS/Airbender + Prividium | Era v31/Gateway/Airbender + supporting repos 活跃 | high code / medium adoption | ZK correctness + enterprise privacy |
| Starknet | STARK + BTCFi/performance/privacy applications | Roadmap/technical roadmap 强化 Bitcoin、S-two、preconfirmation、STRK20/privacy；具体部署状态需复核 | medium | STARK/BTCFi 技术心智 |
| Canton | institutional workflow network with privacy | 企业/RWA/GSF 指标口径不一；机构协作叙事持续 | high architecture / medium metrics | ToB/RWA 可信度标准 |

## 5. Matrix 1: 跨项目叙事趋势矩阵

说明：`H/M/L/A` = high / medium / low / absent。括号内为主要证据等级：`O` official-primary, `S` social/cross-post, `M` media-reported, `D` data-supported, `I` inferred/caveated。`↑/→/?` = strengthening / stable / unclear。弱项保留 `[absent]` 或 `[caveated]`。

| 主题 | Solana | Tempo | Arc | Hyperliquid | Base | Optimism | Arbitrum | ZKsync | Starknet | Canton |
|---|---|---|---|---|---|---|---|---|---|---|
| 稳定币/支付 | H(O,↑) pay.sh / PayFi | H(O,↑) payments-first / stablecoin gas | H(O,↑) USDC gas / StableFX | L(I,?) [not core] | M(O/I,↑) commerce/payments | L(I,?) [Superchain infra] | L(I,?) [not core] | M(O/I,→) AA/Gateway support | L(I,?) [roadmap] | L(I,?) [settlement, not retail payments] |
| RWA/代币化 | M(M/I,↑) [needs data] | L(I,?) | H(O,↑) partner stablecoins / capital markets | A | M(I,↑) token factory / assets | L(I,?) | M(I,→) financial layer | M(I,↑) Prividium / enterprise | L(I,?) | H(O/I,→) tokenized collateral |
| 机构/合规 | M(I,↑) | M(O/I,↑) Visa validator / policy / zones caveated | H(O,↑) Circle compliance | L(I,?) | M(I,↑) Coinbase/compliance primitives | M(O,→) governance/standardization | M(I,→) Orbit/custom chains | H(O/I,↑) Prividium | L(I,?) | H(O,→) financial institutions |
| AI agent / machine payments | M(O,↑) AI commerce/pay.sh | M(I,↑) agent payments caveated | L(I,?) | A | L(I,?) | A | A | A | L(I,?) | A |
| 隐私/permissioned | L(I,?) | M(I,↑) Zones early | M(O,↑) optional privacy | A | M(I,↑) policy/compliance | L(I,?) | L(I,?) | H(O/I,↑) Prividium | M(I,?) caveated | H(O,→) need-to-know privacy |
| 高性能/低延迟 | H(O,→) core brand | H(I,↑) payment lane/finality caveated | H(O,↑) deterministic finality benchmark | H(I,→) HyperCore | H(I,↑) Flashblocks / reported TPS caveated | M(O,↑) op-reth/supernode | M(O,→) Nitro/Timeboost | H(O/I,↑) OS/Airbender claims caveated | M(I,?) | M(O,→) synchronizer, not public TPS |
| 应用链/模块化 | M(I,→) | M(I,?) Zones | L(I,?) | M(I,↑) HyperEVM ecosystem | M(I,↑) Base Stack | H(O,↑) Superchain | H(O,→) Orbit | H(O,↑) Elastic Chain | M(I,?) appchain/BTCFi caveated | M(O,→) network-of-networks |
| DeFi/流动性 | H(M/I,→) | L | M(I,?) | H(M/D,↑) fees/liquidity volatile | M(I,↑) Coinbase/Base DeFi | L/M(I,?) | H(O/I,→) financial layer | M(I,→) | L/M(I,?) | A |
| 开发者生态 | H(O,→) | M(I,?) | M(O,↑) EVM + Circle tools | M(I,↑) HyperEVM | H(O/I,↑) Coinbase/Base tools | H(O,↑) OP Stack | H(O,→) Stylus/Nitro | H(O,↑) ZK Stack/OS | M(I,?) Cairo | L(I,?) Daml niche |
| 代币/治理 | M(M,→) SOL market narrative | A/unknown | M(O,↑) ARC presale official amount/valuation | H(M/D,↑) HYPE volatile | A | M(M,?) OP token/governance | M(I,→) ARB DAO | M(I,→) ZK token | M(I,?) STRK | M(I,?) Canton Coin |
| consumer/social/gaming | H(O/M,→) | A | A | L(I,?) trader community | H(O/I,↑) Coinbase distribution | L | M(I,?) gaming/Stylus | L | M(I,?) gaming/BTCFi | A |

## 6. Matrix 2: 来源覆盖与证据缺口

| 项目 | 官方 Blog / Docs | 社交媒体 | 主流媒体 | 主要缺口 |
|---|---|---|---|---|
| Solana | full: Solana Foundation news 2026-05-05, 2026-05-11 | partial: direct X not scraped | partial: media signals not exhaustively archived | RWA/stablecoin numeric claims need fresh data source |
| Tempo | medium-full: homepage, docs, Payment Lane spec, internal final baseline | caveated | partial via Visa partner announcement | Partner production depth and social/media amplification |
| Circle Arc | full: Circle/Arc materials, whitepaper baseline, Circle Q1 2026 official results | partial | medium: media secondary for finer presale terms | ARC presale amount / valuation / investor consortium are official; finer allocation terms remain secondary-only; mainnet date still future |
| Hyperliquid | partial: docs/HIP direction | partial/caveated | medium but volatile | TVL/fees/FDV need dated dashboard snapshots |
| Base | full via existing final + public release/blog/docs context | partial | partial | Live metrics and official 5K TPS primary evidence |
| Optimism | full via existing final + docs/blog context | partial | partial | Interop mainnet readiness by chain; Base relationship nuance |
| Arbitrum | full via existing final + docs | partial | partial | Orbit recent-code evidence weak; adoption metrics |
| ZKsync | full via existing final + docs/release context | partial | partial | Prividium production adoption; independent benchmarks |
| Starknet | medium: roadmap + technical roadmap + forum notes | weak/partial | partial | Needs direct confirmation for v0.14.2 mainnet status, strkBTC/SNIP execution, encrypted balance production status |
| Canton | full architecture baseline; recent adoption partial | weak | partial | Metrics date/definition conflicts; production vs planned institution signals |

## 7. Competitive Landscape: L1 vs L2 vs 企业网络

### 7.1 独立 L1 / 专用链：争夺端到端控制权

Solana、Tempo、Arc、Hyperliquid 的共同点是，它们都在讲"垂直控制"。Solana 控制高性能执行与 consumer ecosystem；Tempo 控制支付交易路径和稳定币 gas；Arc 控制 USDC 原生发行、结算和机构 FX；Hyperliquid 控制交易流动性、perp 市场和 HYPE 资产循环。这类叙事比"我也是低费链"更有力，因为它们都绑定一个高价值场景。

对 Mantle 的压力按强度排序：

1. Arc / Tempo 压力最大的是稳定币支付与机构结算，因为它们把支付能力下沉到链级产品。
2. Hyperliquid 压力最大的是 DeFi 流动性心智，因为它能用收入、交易量和代币表现吸引注意力。
3. Solana 压力最大的是 consumer + performance + PayFi 组合，它能连接 retail traffic 与机构/支付叙事。

### 7.2 Ethereum L2：从低费扩容转向生态编排

Base、Optimism、Arbitrum、ZKsync、Starknet 的竞争已经不只是"谁更便宜"。Base 讲分发渠道和 Base-owned stack；Optimism 讲 Superchain 标准化和互操作；Arbitrum 讲 financial layer、Stylus、Timeboost、Orbit；ZKsync 讲 ZK correctness、Elastic Chain、enterprise privacy；Starknet 讲 STARK/BTCFi/性能路线。L2 的优势仍是 Ethereum security、EVM/生态继承、可组合性和开发者工具，但头部 L2 正在把这些优势产品化为不同网络策略。

对 Mantle 来说，L2 竞争的核心问题是：Mantle 的差异化到底是 DA、经济模型、收益资产、亚洲/全球生态、企业/机构、还是性能？如果叙事不聚焦，Base/OP/Arbitrum/ZKsync 会分别从分发、标准、金融工具、ZK/企业四个方向吸走心智。

### 7.3 企业网络：Canton 代表另一种"非公链式机构采用"

Canton 与 Arc/Tempo/ZKsync Prividium 的不同在于，它不是把通用公链拿去服务企业，而是从机构工作流、隐私和 Daml 合约模型出发构建网络。Canton 的叙事说明，机构采用需要的不只是低费和 TPS，还包括：谁能看到什么、监管如何观察、合约授权如何表达、多机构如何同步、审计如何导出、数据如何驻留。

这对 Mantle 是提醒：如果要讲企业/RWA，必须证明数据边界和流程，而不是只列生态 logo。Mantle 更适合以 enterprise L3/private DA/permissioned settlement PoC 的方式进入，而不是把公共主链包装成企业隐私网络。

### 7.4 头部整合趋势

当前叙事竞争呈现头部集中：Base、Arbitrum、Optimism、Solana、Hyperliquid 更容易获得开发者、流动性和媒体注意力；Arc/Tempo/Canton 则依靠发行方、支付平台或机构网络形成专用场景护城河。中小 L2 / ZK 项目如果继续讲泛化 TPS 或低费，心智会被压缩；更可行的路径是转向隐私、企业、特定 appchain、Bitcoin/BTCFi、特定金融产品或开发者工具差异。

## 8. Map 1: 竞争定位图

| 象限 | 项目 | 叙事特征 | Mantle 应对 |
|---|---|---|---|
| Consumer / distribution-led | Solana, Base | 用户入口、consumer app、pay/shopping/social、开发者分发 | 不硬拼 consumer 流量；强调 yield/liquidity + Ethereum settlement + 生态伙伴 |
| Stablecoin / payment-led | Tempo, Arc | 稳定币 gas、payment lane、issuer/FX、merchant/agent payments | 做稳定币 paymaster、checkout demo、CCTP/USDC integration、merchant reconciliation |
| Financial liquidity-led | Hyperliquid, Arbitrum | perp/DeFi liquidity、MEV/order flow、financial layer | 建立 Mantle DeFi flywheel：mETH/cmETH/MNT incentives/perp/RWA yield |
| Network/infra-led | Optimism, ZKsync, Starknet | Superchain / Elastic Chain / STARK / proof / interop | 清晰说明 Mantle 的 OP/EVM compatibility + EigenDA + validity roadmap |
| Enterprise workflow-led | Canton | privacy, Daml, tokenized collateral, institution workflows | 企业 L3/private DA/permissioned settlement/audit role PoC |

## 9. Playbook 1: 对 Mantle 的叙事定位建议

### 9.1 一句话定位

建议内部分享使用：

> Mantle should position as an Ethereum-aligned modular high-performance L2 for yield, liquidity, and institution-ready settlement, not as another generic low-fee EVM chain.

中文表达：

> Mantle 的差异化不是"又一条低费 EVM L2"，而是以 Ethereum 对齐和模块化 DA 为底座，承载收益资产、DeFi 流动性与机构级结算场景的高性能 L2。

### 9.2 可抢占或强化的叙事

| 叙事 | 为什么可抢 | 需要的 proof points |
|---|---|---|
| Yield-bearing settlement layer | Mantle 有 mETH/cmETH/MNT 与收益生态基础 | TVL、收益产品、集成协议、资金流向、风险披露 |
| Modular high-performance L2 | EigenDA / modular DA 可与 OP/EVM 兼容形成差异 | DA 成本/吞吐 dashboard、延迟指标、可靠性报告 |
| Institution-ready EVM settlement | 比 Canton 更开放，比 Arc/Tempo 更 Ethereum-composable | permissioned L3/private DA PoC、审计导出、合规 partner、RWA case |
| DeFi liquidity hub | 对抗 Hyperliquid/Arbitrum，需要流动性 flywheel | perp/DEX/lending/yield integrations、incentive ROI、用户 retention |
| Stablecoin UX layer | 不复制 Arc/Tempo，但可补支付体验 | stablecoin paymaster、USDC/CCTP、merchant checkout demo、memo standard |

### 9.3 必须防守的叙事

| 竞争者 | 抢占心智 | Mantle 防守方式 |
|---|---|---|
| Base | Coinbase 分发、onchain economy、developer funnel | 强调中立 settlement、yield/liquidity、非单一 CEX 控制、亚洲/全球生态 |
| Arc / Tempo | 稳定币支付专用链 | 避免正面对标 issuer/payment rail；做 EVM 支付 UX 和稳定币 liquidity layer |
| Hyperliquid | DeFi liquidity / trader mindshare | 用 mETH/cmETH/MNT 和核心 DeFi 协议做收益/流动性闭环 |
| Arbitrum / Optimism | L2 mindshare、OP/Nitro stack、互操作 | 明确 Mantle 与 OP Stack、EigenDA、validity roadmap 的关系 |
| ZKsync / Starknet | ZK/privacy/validity 技术心智 | 不过度承诺；讲 SP1/OP Succinct watchlist 与企业 privacy PoC |
| Canton | 机构/RWA 可信工作流 | 用具体 workflow 证明，不讲空泛机构 adoption |

### 9.4 应避免的同质化表达

- 不要只说 "high TPS / low fees"，除非有公开 dashboard 和可复现实测。
- 不要泛称 "RWA ready"，必须给出资产类型、发行方、托管/审计/合规流程和用户。
- 不要在没有 partner production 证据时用 logo wall 证明机构采用。
- 不要说 "privacy/compliance" 而没有说明 privacy from whom、数据在哪里、谁能审计。
- 不要把 OP Stack/EVM 兼容讲成唯一卖点；Base/OP/Arbitrum 都能讲得更强。
- 不要把 stablecoin payment 等同于稳定币在链上可转账；支付需要 fee UX、memo、merchant API、reconciliation、refund/settlement。

### 9.5 短中长期路线

| 时间 | 对外叙事 | 需要补的产品/工程证据 |
|---|---|---|
| 短期 0-3 个月 | Mantle as yield + liquidity + Ethereum-aligned settlement L2 | 公共 dashboard、mETH/cmETH proof points、稳定币 paymaster demo、DeFi liquidity map、竞品对比页 |
| 中期 3-9 个月 | Mantle as modular settlement layer for payments/RWA/DeFi | USDC/CCTP route、merchant checkout pilot、RWA/treasury case、enterprise L3/private DA PoC、developer grant stories |
| 长期 9-18 个月 | Mantle as institution-ready modular financial network | validity proof roadmap、permissioned settlement toolkit、privacy/compliance proofs、cross-chain liquidity routing、institutional partner production evidence |

## 10. Risks, Open Questions, and Fact-Check List

1. **Starknet status gap**：v0.14.2 mainnet live 与 native proof verification 有官方来源；reviewer 仍需重点补核 STRK20 encrypted balances、strkBTC、SNIP execution、redeemability 和下游应用采用，避免把 roadmap/forum/media signal 写成生产采用事实。
2. **Tempo adoption gap**：Tempo 官网/docs 和 Visa validator announcement 能支撑近期叙事，但社媒覆盖和具体 partner production depth 仍不完整。Final 前应明确所有 adoption claims 的 caveat。
3. **Hyperliquid volatile metrics**：TVL、fees、FDV、HYPE rank、market share 必须在演示前用同一数据源刷新，并记录 source date/accessed date。
4. **Arc financing / presale**：$222M presale、$3B FDV 与 investor consortium 已由 Circle 2026-05-11 Q1 results 官方披露；a16z 单独出资额、具体分配/锁定/治理条款若只来自媒体，应保留 secondary-only。
5. **Base performance**：5K TPS 只能保留 reported/benchmark/roadmap 口径；Beryl/Token Factory/Policy Registry 是 merged-code behind activation gates。
6. **Optimism/Base relationship**：不能说 Base 已离开 Superchain；Base client/cadence 独立化与生态/settlement 关系要分开。
7. **Arbitrum Orbit**：官方产品文档强，但近 3 个月 Nitro title-level code evidence 弱；不要把 Orbit 写成最高强度近期开发主线。
8. **ZKsync performance**：ZKsync OS / Airbender performance 是 official Developer Preview claim，不是 independent benchmark。
9. **Canton adoption metrics**：$2T+ / $1.5T+ / $6T / 400 / 450 / 600 等口径来源和日期不同，必须按 source-attributed 背景处理。
10. **Partner logos**：设计伙伴、投资方、validator、MOU、testnet participant、mainnet production deployment 必须分开。
11. **Twitter/X bias**：本 draft 未完整抓取 X；不能把社媒覆盖视为完整互动分析。Final 若需要社媒强结论，应单独抓取官方账号窗口内高互动帖。

## 11. Source Coverage

### 11.1 Fresh public anchors used in this draft

| Source | Published / source date | Accessed | Evidence level | Used for |
|---|---|---|---|---|
| Solana Foundation, "Solana Foundation Launches Pay.sh in Collaboration with Google Cloud", https://solana.com/uk/news/solana-foundation-launches-pay-sh-in-collaboration-with-google-cloud | 2026-05-05 | 2026-05-24 | official-primary | Solana PayFi / stablecoin checkout / AI commerce |
| Solana Foundation, "Solana Ecosystem Roundup: April 2026", https://solana.com/news/solana-ecosystem-roundup-april-2026 | 2026-05-11 | 2026-05-24 | official-primary | Solana AI/consumer/DeFi/mobile/RWA/stablecoin ecosystem framing |
| Tempo homepage, docs, and Payment Lane spec: https://tempo.xyz/, https://docs.tempo.xyz/guide/payments, https://docs.tempo.xyz/protocol/blockspace/payment-lane-specification | accessed live pages | 2026-05-24 | official-primary | Tempo payments-first design, stablecoin payment UX, payment lane |
| Visa, "Visa Launches Validator Node on Tempo Blockchain", https://investor.visa.com/news/news-details/2026/Visa-Launches-Validator-Node-on-Tempo-Blockchain/default.aspx | 2026-04-14 | 2026-05-24 | partner official | Tempo institutional validation / stablecoin payments |
| Circle, "Building the Internet Financial System: Circle's Product Vision for 2026", https://www.circle.com/blog/building-the-internet-financial-system-circles-product-vision-for-2026 | 2026-01-29 | 2026-05-24 | official-primary, stale/background | Arc Economic OS framing and earlier 150M+ testnet metric; not used as fresh 3-month evidence |
| Arc, "Introducing the ARC Whitepaper", https://www.arc.io/blog/introducing-the-arc-token-whitepaper | 2026-05-11 | 2026-05-24 | official-primary | ARC coordination asset, Economic OS framing, Arc product caveats |
| ARC whitepaper, https://6778953.fs1.hubspotusercontent-na1.net/hubfs/6778953/PDFs/arc_whitepaper.pdf | 2026-05 | 2026-05-24 | official-primary | Arc testnet 244.1M transactions as of 2026-05-05, ARC token design |
| Arc / Circle official materials and ARC whitepaper baseline from `payment-ark/final.md` | 2026-05 | 2026-05-23/24 | official-primary + internal baseline | Arc Economic OS, testnet metrics, mainnet beta summer 2026 |
| Circle Q1 2026 Results, https://www.circle.com/pressroom/circle-reports-first-quarter-2026-results | 2026-05-11 | 2026-05-24 | official-primary | ARC $222M presale, $3B FDV, investor consortium, USDC Q1 metrics |
| Hyperliquid HIP-3 docs and HyperEVM docs, https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals and https://hyperliquid.gitbook.io/hyperliquid-docs/hyperevm | accessed live docs | 2026-05-24 | official-primary | HIP-3 builder-deployed perps and HyperCore/HyperEVM framing |
| Base 2026 Mission/Vision/Strategy, https://blog.base.org/2026-mission-vision-and-strategy | 2026-03-31 | 2026-05-24 | official-primary | Base global markets, payments/stablecoins, builder ecosystem |
| Base Azul blog, https://blog.base.dev/introducing-base-azul | 2026-04-21 | 2026-05-24 | official-primary | Base independent upgrade, base-reth-node/base-consensus, burst TPS caveat |
| Optimism "Benchmarking the OP Stack", https://www.optimism.io/blog/benchmarking-the-op-stack | 2026-03-11 | 2026-05-24 | official-primary | OP Stack benchmark narrative and anti-headline-TPS framing |
| Optimism op-geth/op-program deprecation notice, https://docs.optimism.io/notices/op-geth-deprecation | live docs | 2026-05-24 | official-primary | op-reth / cannon-kona migration and support deadline |
| Arbitrum Orbit and docs, https://arbitrum.io/orbit and https://docs.arbitrum.io/ | live pages / docs updated 2026-05-19 | 2026-05-24 | official-primary | Orbit / Arbitrum chains customization and appchain framing |
| ZKsync Gateway, ZKsync OS, Prividium docs: https://docs.zksync.io/zksync-protocol/gateway, https://docs.zksync.io/zksync-network/zksync-os, https://docs.zksync.io/zk-stack/prividium | live docs | 2026-05-24 | official-primary | Gateway, Airbender/OS developer preview, enterprise privacy |
| Starknet technical roadmap and roadmap: https://www.starknet.io/blog/technical-roadmap/ and https://www.starknet.io/roadmap/ | 2026-03-05 / last updated 2026-03-22 | 2026-05-24 | official-primary | Starknet BTCFi, S-two, preconfirmations, STRK20/privacy roadmap |
| Starknet v0.14.2 pre-release notes, https://community.starknet.io/t/0-14-2-pre-release-notes/116146 | 2026-03-16 | 2026-05-24 | ecosystem/governance-primary | SNIP-36 / S-Two proof verification caveat |
| Starknet, "Starknet v0.14.2: The Privacy Engine Arrives", https://www.starknet.io/blog/starknet-v0-14-2-the-privacy-engine-arrives/ | 2026-04-20 | 2026-05-24 | official-primary | v0.14.2 mainnet status, native proof verification, STRK20 / strkBTC privacy framing |
| Canton Global Synchronizer pages, https://cantonnews.org/insights/the-global-synchronizer-cantons-decentralized-backbone and https://www.canton.network/global-synchronizer | 2026-05-10 / live page | 2026-05-24 | official/ecosystem-primary | Canton network-of-networks, Global Synchronizer, privacy, governance |
| Chainlink/Canton announcement, https://www.prnewswire.com/news-releases/chainlink-now-live-on-canton-accelerating-institutional-grade-tokenization-at-scale-302696344.html | 2026-02-25 | 2026-05-24 | partner official | Canton institutional tokenization data/oracle layer |
| Base technical and narrative baseline from `competitor-base/final.md` | 2026-05-23 | 2026-05-24 | internal-research + code/release baseline | Base Stack, Beryl, Flashblocks, 5K TPS caveat |
| Optimism technical and narrative baseline from `competitor-optimism/final.md` | 2026-05-23 | 2026-05-24 | internal-research + GitHub/docs baseline | Superchain, op-reth/kona, interop |
| Arbitrum technical and narrative baseline from `competitor-arbitrum/final.md` | 2026-05-23 | 2026-05-24 | internal-research + docs/code baseline | BoLD, Timeboost, Stylus, Orbit caveat |
| ZKsync technical and narrative baseline from `competitor-zksync/final.md` | 2026-05-23 | 2026-05-24 | internal-research + code/release/docs baseline | Elastic Chain, Gateway, ZKsync OS, Airbender, Prividium |
| Tempo technical baseline from `payment-tempo/final.md` | 2026-05-22 | 2026-05-24 | internal-research + code/status baseline | Payment Lane, stablecoin gas, Zones caveat |
| Canton technical/adoption baseline from `enterprise-canton/final.md` | 2026-05-22 | 2026-05-24 | internal-research + official-doc baseline | Canton positioning, privacy, adoption metric caveats |
| Enterprise privacy baseline from `enterprise-privacy/final.md` | 2026-05-22 | 2026-05-24 | internal-research | Need-to-know / Validium / private DA framing |

### 11.2 Source requirement coverage

| Requirement | Coverage | Notes |
|---|---|---|
| Official blog/announcement for each project | partial-to-full | Strong for Solana, Tempo, Arc, Base, OP, Arbitrum, ZKsync, Starknet, Canton; Hyperliquid relies more on docs than blog/newsroom |
| Official Twitter/X high-interaction content | partial/caveated | Full X scrape not performed; no hard social-ranking claims |
| Mainstream crypto media | partial | Used mainly as media-amplification/caveat for Hyperliquid/Solana/Starknet; not exhaustively archived |
| 300-500 字 per-project summaries | full | Each project summary includes main narrative, change, evidence, Mantle implication |
| Cross-project trend matrix | full | Matrix includes weak/absent/caveated cells |
| Competitive landscape analysis | full | L1 / L2 / enterprise grouping and positioning map included |
| Mantle positioning recommendations | full | Playbook with avoid/defend/borrow/opportunity |
| Volatile metric date/access | partial | Avoided most unverified volatile metrics; included source/access dates where retained |

## 12. Gap Analysis

This draft is fit for round-1 adversarial review, but not all cells have equal confidence. The strongest sections are Base, Optimism, Arbitrum, ZKsync, Arc, Canton because they reuse recently reviewed internal finals plus public-source checks. Solana is medium-high because fresh official news anchors are available, though quantitative RWA/stablecoin claims were not reused. Tempo is medium-high for official product/docs and Visa validator evidence, but adoption depth remains caveated. Hyperliquid is medium because HIP-3/HyperEVM docs are strong while fees/TVL/FDV are volatile. Starknet is medium: v0.14.2 mainnet status is officially supported, but STRK20/strkBTC/encrypted balance production adoption still needs careful review.

Recommended review focus:

1. Verify Starknet STRK20 / strkBTC / encrypted balance production adoption before promoting any roadmap or privacy-asset item to shipped usage fact.
2. Decide whether Tempo homepage/docs plus Visa validator announcement are enough for narrative summary; otherwise request a Tempo-specific media/social addendum.
3. Require dated dashboard snapshots if any Hyperliquid metric is promoted from caveat to fact.
4. Check that no `[stale/background]` internal final claim is being used as fresh narrative evidence without label.
5. Confirm source matrix does not overclaim social media coverage.

## 13. Revision Log

| Round | Date | Change |
|---|---|---|
| 1 | 2026-05-24 | Initial deep draft produced from approved outline. Added project summaries, trend matrix, competitive analysis, Mantle playbook, source coverage, and gap analysis. Carried forward outline-review guardrails on fresh evidence, weak cells, and volatile facts. |
