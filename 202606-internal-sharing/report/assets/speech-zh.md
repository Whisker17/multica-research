# 中文演讲稿 — Mantle 竞争格局与叙事方向分析

> 时长目标：~20 分钟 | 格式：逐 Slide 对应 | 【】内为演讲者备注

---

## Slide 1 — 封面

大家好，今天的内部分享主题是 Mantle 的竞争格局与叙事方向分析。我们花了几周时间，对整个 L2 赛道和相关竞品做了一次系统性的调研，目的是回答一个核心问题：Mantle 下一步该往哪走。

---

## Slide 2 — 议程

今天分三个部分来讲。

第一部分看市场现状——市场发生了什么变化，Mantle 面临什么挑战。第二部分看竞争对手——其他人在做什么，竞争压力从哪来。第三部分给出方向建议——我们评估了三条路线的技术可行性。

先说结论：我们的分析显示，**机构金融**是 Mantle 契合度最高的方向——以 zkSync Prividium 为对标，利用国库和收益生态优势构建合规技术栈。具体为什么，以及怎么做，接下来展开。

---

## Slide 3 — L2 赛道格局演变

先看大盘。这三组数据图表分别展示 TVL、DAU 和手续费的情况。

TVL 方面——我们选了六条主要 L2 做对比。Base 以 44.7 亿美金排第一，占六链合计的 67%。Arbitrum 15.1 亿，占 22.7%。两家加起来就是 89.7%，接近九成。Mantle 在 2.32 亿，占 3.5%。更关键的是年度变化：Base 涨了 40.8%，Arbitrum 跌了 34.3%，zkSync 跌了 61.4%，Mantle 仅涨 2.1%。TVL 是赢家通吃格局。

DAU 更极端。Base 日活 43.5 万，独占 72.6%。Mantle 只有 1,600，占 0.3%。而且六链 DAU 全部在大幅下降——Base 跌 74.7%，Mantle 跌 81%。这不只是长尾问题，是全行业用户萎缩。

手续费方面，EIP-4844 之后所有链的中位数费用都在亚美分级别——从 OP 的 0.00002 美金到 zkSync 的 0.015 美金。费用竞争作为差异化手段已经结束了。现在的竞争维度变了——变成了生态控制、用户分发、ZK 隐私、收益资产这些方向。

---

## Slide 4 — 叙事转向：DeFi → RWA / 机构金融

接下来看叙事变化。

左边是 DeFi 的天花板。全球 DeFi TVL 从去年 5 月的 960 亿涨到去年 10 月峰值 1710 亿，现在回落到 810 亿，年同比跌了 15.3%。Aave V3 独占借贷 TVL 34%，但整体萎缩了 30%。最极端的例子是 Blast——峰值 22.6 亿，现在只剩 3100 万，跌了 99%。纯靠 DeFi 激励的增长不可持续。

右边是 RWA 的加速。链上 RWA 从去年的 107 亿涨到现在的 338 亿，年增长 216%。美国国债代币化到了 150.5 亿。12 个子类别年增长全部为正，最高的企业信贷涨了 1552%。BlackRock BUIDL 约 30 亿 AUM，而且今年 5 月他们向 SEC 申请了 70 亿美金货币市场基金上链。

但有一个深层矛盾需要注意。Vitalik 的 cypherpunk 立场倡导隐私优先和抗审查。而机构金融需要 KYC、需要许可制。这两个方向在以太坊生态内是有结构性张力的。

---

## Slide 5 — Mantle 当前定位与挑战

Mantle 目前是什么情况。

技术栈方面，OP Stack、Ethereum aligned、OP Succinct 用 SP1 Hypercube、Ethereum blob DA——已移除 EigenDA，L2Beat 重新分类为 rollup。

看这张 TVL 和 DAU 的双轴图。TVL 绿线，从去年 6 月 2.19 亿，到今年 4 月因 Aave V3 激励冲到 7.05 亿峰值，现在回落到 2.32 亿，年同比涨 6%。但 DAU 红线一路单调下降——从 8,143 降到 1,608，年同比跌 80%。注意这条 Aave V3 上线的竖线——TVL 因激励短暂飙升，但 DAU 在整个周期内没有任何反弹。

再看协议分布。Mantle 原生 DeFi 在 Aave V3 上线前就在持续萎缩——Merchant Moe 从 8400 万跌到 3700 万，跌 56%。Agni 从 3900 万跌到 2300 万，跌 41%。Aave V3 上线 12 天吸引了 2.9 亿存款，峰值 5.92 亿占总 DeFi TVL 的 56%，但到 5 月回落到 1.32 亿。这说明激励驱动的 TVL 增量粘性很低。

资产基本盘：mETH 约 9.25 亿 TVL，第四大 ETH LST；cmETH 约 5.15 亿。稳定币约 6.69 亿。

核心问题很明确：TVL 部分恢复了，但用户持续流失，DeFi 激励驱动已经证伪，我们需要找到新的叙事锚点。

---

## Slide 6 — Chapter 1 小结

总结第一章的三个要点。

一，DeFi 要守，但不能指望它带动增长。二，RWA 和机构金融年增长超过 200%——是链上最快增长的叙事。三，合规基础设施正在成为新的竞争维度——在我们调研的五条链里，只有 zkSync 有。

接下来看竞争对手具体在做什么。

---

## Slide 7 — 竞品分析框架

我们把竞争对手分成三类。

第一类是 L2 竞品——Base、Arbitrum、Optimism、zkSync、StarkNet、X Layer——这是同赛道的直接竞争。第二类是 L1 通用链——Solana、Sui、BNB Chain——跨赛道的替代竞争。第三类是 L1 垂直链——Tempo、Circle Arc、Canton——新赛道的抢位竞争。

分析维度主要是两个：近 90 天的 GitHub 代码活动，以及叙事方向的变化。我们要看的是他们实际在做什么，不只是在说什么。

---

## Slide 8 — L2 竞品：技术路线对比（上）

先看三个走「平台化」路线的 L2。

**Base** 在做客户端独立——Azul 升级 5 月 28 号主网激活，收敛到 base-reth-node 加 base-consensus 自有技术栈。Flashblocks 200 毫秒预确认已经在主网运行。Multiproof TEE 加 ZK 在推进中但未完成。Beryl 的合规资产原语 B20Factory 和 PolicyRegistry 代码已合并但主网尚未激活。90 天内 1810 个 PR，开发强度最高。核心竞争力是 Coinbase 1.2 亿用户的分发能力，这是不可复制的。

**Arbitrum** 走的是金融原生加可定制 Nitro stack 路线。BoLD 无许可验证还在 Draft 阶段——多个 PR 标记了 DO NOT MERGE。Timeboost 做 MEV 排序拍卖。Stylus SDK 从 v0.10.2 迭代到 v0.10.7，支持 WASM 多语言合约。90 天 256 个 PR，34 个贡献者。工程重心在底层硬化——安全与排序，不是 Orbit 应用链代码爆发。

**Optimism** 在做 Superchain 协调层。1202 个 PR 主要在 monorepo 里，98 个 PR 作者，周 PR 从第 9 周的 50 个加速到第 21 周的 129 个。op-reth/kona Rust 迁移和 op-supernode/supervisor 互操作 devnet 在同步推进。一个需要注意的风险：**op-geth 的支持在 5 月 31 号就到期了**，之后必须迁移到 op-reth。这对 Mantle 有直接影响。

**关键判断**：这三家都在走生态扩张的路线。Mantle 的体量——1,600 日活对比 Base 的 43.5 万——不够走这条路。

---

## Slide 9 — L2 竞品：技术路线对比（下）

再看另外三个。

**zkSync**——这是今天最重要的对标。他们的工程已经从单一 zksync-era 仓库扩展为多仓库栈：ZKsync OS Server 最活跃 404 个 PR，OS RISC-V 多 VM 支持 EVM、EraVM、Wasm 共 146 个 PR，Airbender GPU 证明器 94 个 PR，Gateway 加 era-contracts 154 个 PR。跨 5 个组织总共 1,427 个 PR——远超 era 单仓库 130 个 PR 数据所暗示的活跃度。最核心的是 **Prividium**——一个企业级的合规 Validium 方案，本地开发环境已开源，Docker Compose 全栈包含 Keycloak 身份、Protected RPC、Admin Panel、zkSync OS、Sequencer、Prover、Block Explorer、Prometheus/Grafana。他们声称已吸引 35 家以上金融机构——但这个数字来自合作方 Cari Network 声称，不是 zkSync 直接披露，我们没有独立验证。Prividium 目前是本地开发环境，非生产部署证明。

**StarkNet**——Cairo/STARK 体系 ZK 深度领先。Sequencer/OS 有 1,324 个 PR，是所有链中最高。Cairo 发了四个版本，STWO Circle STARK 223 个 PR。v0.14.2 主网已激活。但 BTCFi 叙事声量大代码极弱——strkBTC 只有 2 个 PR 和 8 个 commit。非 EVM 架构不构成直接迁移竞争。

**X Layer**——和 Mantle 最像：都是交易所背景、都是 OP Stack L2。Exchange OS 白皮书 V1.0 描述了双环境设计——X Layer EVM 治理加 TradeZone 30 万 TPS 撮合——但只是白皮书，无生产部署。APP Agent 支付协议有四类 intent 设计。Agentic Wallet 用 TEE 安全。OKX 1.2 亿用户是分发优势，但 L2BEAT TVS 只有 1023 万美金。

---

## Slide 10 — L1 通用链叙事动态

L1 通用链方面。

**Solana** 的 Alpenglow/Votor 是全新共识机制，用 BLS 聚合实现亚秒终局，Q3 主网目标但还在压力测试。开发主体已从 Solana Labs 迁移到 Anza 和 Jito 双客户端分工——Labs 的 116 个仓库几乎全部不活跃了。Pay.sh 做稳定币 Checkout 和 Google Cloud 合作。核心威胁是他们正在把零售流量和 PayFi、机构叙事连成一条线。

**Sui** 的 gasless 稳定币转账已经上主网了——7 个白名单币种包括 USDC、USDY 等，gasless TPS 上限 300。这是协议层的特性，不是补贴。DeepBook 做现货加保证金。Hashi 做 BTC 机构托管接了 BitGo、FalconX、Ledger 等 6 家。Walrus 存储加 Seal 加密密钥。MystenLabs 跨组织 2,966 个 PR。

**BNB Chain** 的工程主要在 BSC 客户端稳定化和 reth 双客户端。Mendel 硬分叉 4 月 28 号主网激活。250 毫秒出块目标只有 BEP spec 没有实现 PR，当前是 450 毫秒。opBNB 实质废弃了——一名开发者，90 天零合并 PR。AI Agent 叙事声量高但代码弱——bnbchain-mcp 89% PR 关闭率。

**要点**：L1 通用链的威胁不是单一维度——Solana 把 consumer 加 PayFi 加机构连成一条线，Sui 把协议级支付 UX 加 BTC 托管加数据栈打包成产品，BNB Chain 靠交易所流量但技术栈实际在收缩。L2 不能只靠以太坊安全性这一个叙事。

---

## Slide 11 — L1 垂直链：赛道已有原生占位者

这是竞争最直接的一类。大家看这三张卡片——每张代表一条专门为某个赛道设计的 L1。

【左卡片】**Tempo**——Stripe 和 Paradigm 孵化的支付专用链，主网已经在跑了。标志性进展是 **Visa 4 月 14 号宣布运行 Tempo 验证节点**——这是传统支付巨头对 crypto 支付链的直接背书。技术层面，T4 硬分叉 5 月 18 号主网激活，Payment Lane V2 收紧了安全分类，MPP 机器支付协议已上线。但 Zones 企业隐私层还在测试网，proof 是 stub，不是生产就绪。

【中卡片】**Circle Arc**——USDC 发行方自建全栈金融 OS。标志性进展是 **ARC Token 预售 2.22 亿美元、FDV 30 亿**——a16z 领投 7500 万，BlackRock、Apollo、ICE、Standard Chartered 参投。核心结构性优势是 CCTP V2——26 个域、累计 1260 亿美金、年增 740%，这是第三方链不可复制的。测试网 2.44 亿笔交易、100 多家机构参与。但注意状态标签是橙色——**主网尚未上线**，预期今年夏天。

【右卡片】**Canton**——Daml 加 need-to-know 隐私的企业结算网络。标志性进展是 **DTCC 2026 上半年受控生产 MVP**——这是全球最大的证券结算机构。Broadridge DLR 每天结算 3680 亿美金、月近 8 万亿。Chainlink 2 月上线了 Canton 数据层。但多个合作仍处于「意向」阶段——JPMD 尚未部署，HQLAX 待监管批准。

底部关键信息：**赛道不是空白。原生竞争者已经从架构层做了场景优化，通用 L2 后发难以追赶。**

---

## Slide 12 — Chapter 2 关键发现

四个结论，引出下一章。

一，**通用平台路线已无 Mantle 的位置**。Optimism 用 Superchain 定义 OP Stack 生态，1202 个 PR。Arbitrum 用 Orbit 可定制 Nitro stack 覆盖应用链。Base 在 Coinbase 1.2 亿用户基础上选择独立技术栈——1810 个 PR。Mantle 同为 OP Stack L2，既不是 Stack 提供者，也没有百万级 DAU 支撑独立技术栈投入——当前 DAU 约 1,600。

二，**交易所分发未能有效转化为链上生态**。三个交易所背景 L2 都证实了这一点。OKX 1.2 亿用户支持 X Layer，TVL 只有 9100 万。Bitget 1.2 亿用户将 4.4 亿 BGB 迁到 Morph，TVL 只有 890 万。Bybit Alpha 集成 Mantle 后，Fluxion TVL 从 44.8 万缓慢增长到 255 万。对比 Base——同样 Coinbase 1.2 亿用户，TVL 43 亿。说明关键不是交易所导流，而是产品和技术栈的差异化。

三，**垂直赛道已有原生竞争者从架构层占位**。支付方向有 Tempo——T4 硬分叉主网激活加 Visa 验证节点加 Payment Lane 协议级设计——和 Arc——2.22 亿预售加 CCTP 1260 亿不可复制跨链优势加 BlackRock 投资。企业/RWA 方向有 Canton——DTCC 2026 上半年生产 MVP 加 need-to-know 隐私加 Chainlink 数据层加 Broadridge 日均 3680 亿结算。这些链从共识层到 blockspace 设计都针对特定场景做了优化，通用 L2 后发难以追赶。

四，**竞争窗口正在快速收窄**。2026 Q1-Q2 各赛道密集推进：Tempo 主网迭代加 Visa 落地，Arc 2.22 亿预售冲刺夏季主网，Canton 连续签约 DTCC/JPMD/HQLAX，zkSync Prividium 已开源但仍为本地开发环境。Mantle 需要选择方向并做同等深度的基础设施投入。

过渡句：平台化走不了，交易所导流不够，垂直赛道有人占，窗口还在收窄——Mantle 应该往哪个方向走？接下来我们逐一评估三个候选方向。

---

## Slide 13 — 评估框架

每个方向按三步展开：市场格局、技术前提、行业案例。

三个方向用颜色区分：蓝色 AgentFi——AI Agent 经济基础设施；橙色 Payment Chain——稳定币支付专用链；绿色机构金融——合规隐私与企业结算。

目标是全面理解每个方向的机会与挑战，为 Mantle 的叙事决策提供依据。

---

## Slide 14 — AgentFi：市场格局与技术前提

AgentFi 目前是最热的叙事之一。CoinGecko 上 AI Agents 分类市值 36.8 亿美金，24 小时成交额 5.38 亿。加密 AI Agent 赛道整体在 23 到 26 亿之间。但阶段判断是：代币投机大于真实使用，仍处早期概念验证阶段。真实使用信号方面，x402 Discovery 有 50,566 个资源、72,141 独立付费方、过去 30 天 326,224 次调用——这是目前最接近生产级的 Agent 支付数据。

竞争格局方面，Base 的布局最完整——AgentKit 加 x402 加 Base MCP 加 Agentic Wallets，配合 Coinbase 1.2 亿用户分发，构成四层垂直整合。Solana 有 pay-kit/MPP 加 Token Extensions 加 SVM 低延迟。X Layer 有 APP Agent 支付协议加 Agentic Wallet。

做 AgentFi，链的基础设施需要六层能力：标准化 AI 接口、Agent 钱包加权限管理、低延迟执行、机器间支付协议、DeFi 流动性支撑、以及 Agent 发行平台。

---

## Slide 15 — 案例：Base AgentFi 生态

【看左边的四层架构图 `charts/slide15-base-agentfi-arch.png`】

Base 的 AgentFi 生态建立在四层垂直整合之上。从底向上看这张架构图。

最底层是 **CDP AgentKit**——模型无关的开发框架，50 多个 TypeScript Actions、30 多个 Python Actions，覆盖转账、兑换、NFT 铸造、智能合约部署。第二层是 **Agentic Wallets**——TEE 保护密钥，内置 Session Caps 和 Transaction Limits 策略引擎，通过 Paymaster 在 Base 上实现无 Gas 交易。第三层是 **x402 协议**——激活 HTTP 402 状态码做机器间微支付，最低 0.001 美元，亚秒结算，已集成 Google AP2。最上层是 **Base MCP**——5 月 26 号刚发布的，基于 Anthropic 的 MCP 标准，首发集成 Morpho、Moonwell、Aerodrome、Uniswap 等七大 DeFi 协议插件，采用 OAuth 2.1 安全模型。

底部的基础设施支撑层包括 Flashblocks 200 毫秒预确认、Smart Wallet 的 ERC-4337 加 ERC-7715 权限体系、以及 Aerodrome DEX 峰值 TVL 超 10 亿。

Agent 生态方面——看右边的表格。Social 类的 Clanker 在 Farcaster 上自动发币，累计协议费用超过 5000 万美金，交易者 55.8 万。Virtuals Protocol 部署了超过 1.8 万个 Agent，年协议收入在 Base 排第二——超过 5900 万美金。Trading/DeFi 类 Agent 做 7 乘 24 收益监控和再平衡。

**关键洞察**：Base AgentFi 生态的核心竞争力不是单个协议，而是 Coinbase 分发加四层垂直整合的组合效应——开发者用 `npm create onchain-agent@latest` 就能获得钱包、DeFi、支付、AI 接口全套能力。Mantle 在六维上全部需要从零补建，差异化壁垒有限。

---

## Slide 16 — Payment Chain：市场格局与技术前提

支付赛道在快速增长。全球稳定币供给 3207 亿，USDC 单季链上交易量 21.5 万亿，同比增长 263%。但一个关键区分——链上交易量不等于真实支付。真实稳定币支付年化只有约 3900 亿，渗透率 0.02%。跨境支付 TAM 是 179 万亿，全球汇款平均成本 6.36%。差距巨大，但机会也巨大。

更重要的是，支付级链已有原生竞争者。Tempo 已有主网运营加 Visa 验证节点加 Payment Lane 协议级设计。Circle Arc 有 USDC 原生发行加 CCTP 跨链加 2.22 亿预售。Sui 的 gasless P2P 已经上线，7 个白名单币种。

这里要强调一个关键认知：**Payment Chain 不等于在通用链上部署支付合约**。它需要链在六个维度提供协议级能力——确定性终局、费用确定性、支付专用 blockspace、稳定币原生支持、跨链互操作、以及合规基础设施。

核心洞察：支付需要 Web2 分发——Stripe、Visa、Circle 的网络效应。纯 crypto 方案很难 mass adoption。

---

## Slide 17 — 案例：Tempo 支付链架构

【看左边的架构图 `charts/slide17-tempo-arch.png`】

大家看这张 Tempo 的交易流程图。从上往下走。

用户和商户发起交易后形成 TempoTxEnvelope，先经过 **TIP-403 合规策略层**——这是预编译级别的合规策略注册表。然后进入最核心的创新——**Payment Lane**。

Payment Lane 是 Tempo 的核心差异化——架构图上用绿色高亮标注的部分。它把 blockspace 分成三个区：System Lane、Payment Lane 和 General Lane。通过 `general_gas_limit` 硬约束非支付交易的 gas 容量，即使 DeFi 拥堵，支付交易仍有保留的 blockspace。

往下是 **TIP-20 预编译 Token**——不是普通的 ERC-20 合约，而是协议级 token 标准。固定 6 位精度、原生 memo 字段用于支付对账、pause/role-based 权限、fee eligibility、直接集成 Payment Lane。稳定币 Gas 以 attodollars 计价，一笔 TIP-20 转账约 0.001 美元——无需持有原生代币。

底层是 **Reth EVM 执行层**加 **Commonware Simplex BFT** 共识——目标 500 到 600 毫秒确定性终局，双进程隔离设计降低执行负载对共识路径的影响。最下面是可选的 **Enterprise Zones**——但 proof 还是空的，不是生产就绪。

六维覆盖情况：终局性、费用确定、支付 blockspace、稳定币原生、合规都有。但**跨链互操作是缺失的**。注意，性能数据是设计目标，生产 SLA 待验证。Visa 4 月 14 号宣布运行 Tempo 验证节点。

---

## Slide 18 — 案例：Circle Arc 金融 OS 架构

【看左边的架构图 `charts/slide18-arc-arch.png`】

Arc 走的是完全不同的路线——USDC 发行方自建全栈金融 OS。

看这张五层平台栈架构图。最底层是 **Arc Core**——Malachite BFT 共识约 780 毫秒终局、小规模可到 330 到 490 毫秒、约 5 万 TPS。USDC 是原生 Gas 代币，EWMA 费用平滑抑制需求尖峰。EVM 兼容加可选隐私加许可制验证者。

第二层是 **Assets**——USDC 原生发行加 8 种合作稳定币覆盖巴西、韩国、菲律宾等 8 个国家，加 ARC Token。

第三层是 **Protocol Services**——这是核心差异化层，架构图上用绿色高亮标注。包括 CCTP V2 原生跨链 USDC——26 个域、累计 1260 亿美金、年增 740%——这是 Circle 发行方地位带来的**结构性优势，第三方链不可复制**。还有 Wallets、StableFX 机构 FX 引擎、CPN、Paymaster、Nanopayments。StableFX 做 RFQ 多报价执行加原子链上结算加可编程结算窗口，对接 8 国 Partner Stablecoins。

第四层是 **Developer Kits**——应用开发工具包、AI 构建工具、智能合约、Nanopayments SDK。

最上层是 **Applications**——DeFi、Payments、Capital Markets、Agentic Commerce。

融资规模：ARC Token 预售 2.22 亿美元、FDV 30 亿。测试网 2.44 亿笔交易。100 多家机构参与测试网——含 BlackRock、Goldman Sachs、Mastercard、State Street、Visa。主网今年夏天预期。

六维覆盖：终局性、费用确定、稳定币原生、跨链互操作、合规都有。但**缺少支付专用 blockspace**。

**Tempo 和 Arc 的核心差异**：Tempo 优化支付交易管道——Payment Lane 加固定费加预编译 token。Arc 构建全栈金融 OS——USDC 原生发行加 CCTP 跨链加 StableFX 加机构验证者。Tempo 缺跨链，Arc 缺 Payment Lane。

---

## Slide 19 — 机构金融：市场机会与监管催化

现在看契合度最高的方向。

链上 RWA 非稳定币部分 310 到 340 亿，年增长超 200%。含稳定币的广义数字资产结算规模超过 4000 亿。集中在低风险资产：美国国债 150 亿加、大宗商品 70 亿加、资产支持信贷 23 亿加。阶段判断是机构试点到规模化早期——还不是主流采用。

机构要什么？不是低费加高 TPS。而是五个词：**合规**——KYC/KYB/AML/Travel Rule，谁能进来、谁能交易。**隐私**——交易数据谁能看、看多少、怎么证明不多看。**数据主权**——数据存在哪、谁控制、能否删除。**审计**——监管方怎么观察、怎么导出、怎么验证。**工作流**——托管、抵押品、DvP、结算、对账，不是单笔转账。

监管催化剂密集出现。GENIUS Act 签署，稳定币监管框架落地。SEC 今年 1 月声明代币化证券等于证券，所有合规角色——transfer agent、broker-dealer、custody——仍然适用。MiCA 统一欧盟框架。FATF Travel Rule 要求 VASP 传输双方身份。

已经有三种验证或探索中的模式。zkSync Prividium 是 "**Prove-Not-Reveal**"——整链对外不可见，ZK 证明保证正确性。Canton 是 "**Need-to-Know**"——子交易级投影，每方只看到与自己相关的部分。还有一种新思路是 Paladin 的 "**Pluggable Sidecar**"——不改链、在标准 EVM 旁挂一个隐私运行时，按场景选择不同的信任模型。后面我们会逐一展开。

---

## Slide 20 — 案例：zkSync Prividium — "Prove-Not-Reveal" 企业隐私

【看中央架构图 `charts/slide20-prividium-arch.png`】

Prividium 的核心是一条**许可制 Validium 链**。大家看这张端到端结算路径图。

从上往下。机构用户通过 **IdP** 认证——Keycloak、Okta OIDC 或 SIWE。然后进入 **Proxy RPC Gateway**——做三步验证：JWT 身份、钱包签名、函数权限检查。这是整个网络的唯一入口。

通过网关后到 **Sequencer 私有执行**——数据存在 PostgreSQL 加 Blob Store 的私有子网里，不暴露到互联网。再到 **Prover**——用 Airbender GPU 生成 STARK 证明。通过 **ZKsync Gateway** 聚合后提交到以太坊 L1。

注意架构图上那条绿色信任边界虚线——L1 只能看到状态根和 STARK 证明，**零交易数据泄露**。这不是额外功能，是 Validium 架构的固有特性。运营方可见全部数据，可作为审计资产。

看左边的四层准入控制侧栏。第一层身份认证——Okta SSO 或 SIWE 或多钱包支持。第二层 Proxy RPC 网关——三步验证加审计日志，标准 RPC 端点保持私有。第三层 RBAC 权限——Admin Dashboard 管理用户、角色、权限，合约函数级粒度，不用改代码。第四层 L1 TransactionFilterer——链上白名单过滤强制交易路径。

开发环境已经开源——`local-prividium` 用 Docker Compose 一键起全套：Prividium API、Keycloak、Admin Panel、zkSync OS、Sequencer、Prover、Block Explorer、Prometheus/Grafana。

机构采用信号：Cari Network 联合 5 家美国区域银行，合计存款超 6000 亿美金，目标今年 Q3 试点。Deutsche Bank 确认合作。BitGo 提供机构托管。但需注意，"35 家以上银行" 来自 Cari Network 声称，非 zkSync 直接披露。

**核心信息**：Prividium 的价值核心是合规和准入控制，不是 ZK 证明本身。合规 RPC 加 RBAC 加审计就已经解决了机构最关心的问题。

---

## Slide 21 — 案例：Canton — "Need-to-Know" 机构工作流网络

【看上部架构图 `charts/slide21-canton-arch.png`】

Canton 代表了完全不同的范式。大家看这张参与者模型图。

四层结构。最上层是 **Application Layer**——DvP、回购、抵押品、债券这些金融工作流。

第二层是 **Participant Layer**——每个参与方维护自己的 Local ACS。图上用不同颜色标注了三个参与方：蓝色的 Alice Bank、橙色的 Bob Fund、紫色的 Regulator。关键标注——"Only sees own contracts"，**每个参与方只看到与自身相关的合约**。

第三层是 **Synchronizer**——Sequencer 负责排序加密消息，Mediator 做 2PC 确认聚合。但注意标注——"Cannot see plaintext/contract content"。**排序者和调解者都看不到交易明文**。这和 Prividium 不同——Prividium 的运营方可见全部数据，而 Canton 是**没有任何一个节点持有完整全局状态**。

最底层是 **Global Synchronizer**——Super Validators、治理和 Canton Coin。

看右边的 DvP 可视性矩阵。一笔 DvP 交易中：Alice 看到自己的资产转移加必要对手方输出，看不到其他客户合约。Bob 同理。Bank 1 只看到自行发行资产的转移投影，看不到交易原因和对手方细节。监管方只看到被显式设为 Observer 的合约。

Daml 合约模型是为金融工作流设计的——signatory 代表义务和责任，observer 用于监管审计，controller 执行合约操作，consume-create 模式天然生成审计轨迹。

机构生产验证——这是 Canton 最强的地方。**Broadridge DLR 日均 3680 亿美金、月近 8 万亿回购结算**。HSBC Orion 做债券生命周期，4 支数字债券，结算从 T+5 改善到 T+1。Goldman Sachs DAP 做多资产代币化，报告小于 60 秒结算。DTCC 计划 2026 上半年受控生产 MVP，做 DTC 托管的美国国债代币化。

**Canton 告诉我们一件事**：机构采用需要的是工作流级别的设计——谁能看什么、怎么授权、怎么审计，不是给通用链加几个 enterprise feature。

---

## Slide 22 — 案例：Paladin — "Pluggable Privacy Sidecar" 可插拔隐私运行时

【看左边的架构图 `charts/slide22-paladin-arch.png`】

Prividium 和 Canton 之后，我们来看第三种完全不同的思路——Paladin。

Paladin 不是一条链，也不是对 EVM 的分叉。大家看这张三层架构图。最下面 **Layer A** 是标准的 Base EVM Chain——可以是 Mantle，可以是以太坊，**完全不需要修改**。中间 **Layer B** 是 Paladin Privacy Runtime——作为 Sidecar 独立进程运行在 EVM 旁边，通过标准 JSON-RPC 和 WebSocket 交互。最上面 **Layer C** 是 Pente 专用的临时 EVM——只有在需要运行私有智能合约时才会启动。

关键在那条红色的分隔线——链上只存 hash、commitment、nullifier 和证明结果，**零业务数据**。所有明文、身份、UTXO 原像都留在 Layer B 的 Paladin 节点之间私有分发。

Paladin 最独特的是它提供三种隐私域，每种对应不同的信任模型。**Noto** 基于 Notary 信任——适合受控发行、银行存款 token 这类本来就需要权威方背书的资产。**Zeto** 基于 ZKP——用 Groth16 证明在链上验证合法性，但不公开金额和身份，适合 KYC-gated 的私密转账。**Pente** 基于 Privacy Group——2 到 10 方组建私有合约组，组内全员重放执行、组外完全不可见，适合债券生命周期、合规审批这类复杂业务逻辑。三种域共享同一个运行时，可以通过 **Atom** 做跨域原子 DvP 结算——比如 Noto 债券加 Zeto 现金在一笔 EVM 交易里同时交割。

现在关键问题——Paladin 和前面讲的 Prividium、Canton 有什么本质区别？看这张对比表。

**最核心的差异在于与底层链的关系**。Prividium 是链本身——你要用它就得部署一条 zkSync OS 的 Validium 链。Canton 也是链本身——需要跑 Daml 和 Global Synchronizer 全栈。而 Paladin 是 Sidecar——**不换链、不换栈，在已有 EVM 旁边挂一个进程就行**。对 Mantle 来说，这意味着不用迁移资产、不用放弃 DeFi composability，可以渐进式引入隐私能力。

但必须讲清楚风险。**第一个问题是 Besu 绑定**。Paladin 和 Besu 同属 Linux Foundation Decentralized Trust，Layer C 的 Pente 直接嵌入了 Besu 的 Java EVM 库。而 Mantle 的执行层是 geth 和 reth 体系——我们不可能再维护第三个 EVM 客户端。如果要在 Mantle L2 上原生运行 Pente，就需要把 ephemeral EVM 从 Besu 替换成 geth 或 revm，这涉及 PenteDomain、evm_runner、statedb 适配层的重实现，工作量不小。**第二是协议成熟度**——Pente 的组成员创建后不可变、Groth16 需要 trusted setup、Go 加 Java 混合运行时带来运维复杂性。**第三是没有生产验证**——Prividium 有 Cari Network 和 Deutsche Bank 的信号，Canton 有 Broadridge 每天 3680 亿的回购结算，而 Paladin 目前还没有公开的机构生产案例。

总结一下：Paladin 提供了一条**最轻量的隐私集成路径**——不换链就能获得企业隐私能力，但 Besu 绑定和协议成熟度是需要评估的技术代价。

---

## Slide 23 — 三方向全面评估

把三个方向放在一起做全面对比。这张十维度矩阵表很密，我挑关键维度讲。

**市场规模**：AgentFi 36.8 亿美金代币市值但非真实 TAM，Payment Chain 3207 亿稳定币供给加 179 万亿跨境 TAM 但只有 0.02% 渗透率，机构金融 310 到 340 亿 RWA 年增超 200%。

**竞争强度**：AgentFi 面对 Base 四层整合加 Coinbase 分发的不可复制优势。Payment Chain 面对 Tempo 加 Arc 从架构层优化加 CCTP 结构性垄断。机构金融目前只有 zkSync Prividium——还是本地开发环境阶段，窗口期存在。

**Mantle 已有基础**：AgentFi 方面有 EVM 加第三方 AA。Payment 方面有 5.578 亿稳定币。机构金融方面有 MI4/Securitize 加 USDY 加 mETH/cmETH 收益生态加约 40 亿国库——这些收益资产是 Tempo、Arc、Canton 都没有的独特价值。

**关键风险**：AgentFi 赛道可能停留在投机阶段，Base 先发优势难以逾越。Payment Chain 六维中三维为结构性差距。机构金融采用周期长，需要合作伙伴验证。

三个方向不是互斥的——AgentFi 的 Agent 财库管理和 Payment 的 B2B 结算都可以作为机构金融的子场景。关键问题是 Mantle 的主叙事锚点应该放在哪里。

---

## Slide 24 — 结论与下一步

总结三个核心发现。

一，**L2 赛道已进入差异化定位阶段**。头部 L2 各有不可复制的结构性护城河——Base 分发、Arbitrum 金融工具链、Optimism Superchain、zkSync ZK 加企业隐私。L1 通用链和垂直链同时压缩空间。Mantle 必须选择方向。

二，**三个候选方向各有机会与风险**。AgentFi 早期但 Base 先发优势极强。Payment Chain 增长快但原生竞争者已从架构层占位。机构金融增长最快且竞争窗口仍在，但需要从零构建合规技术栈。

三，**方向之间不是互斥的**。Agent 财库管理和 B2B 支付结算都可以作为更大叙事的子场景。关键是确定主叙事锚点，然后让其他方向围绕它展开。

需要团队讨论的问题：Mantle 的主叙事锚点应该放在哪个方向？op-geth EOL 迁移路径如何选择？是否有资源和意愿探索合规隐私基础设施？

以上就是今天的分享。接下来进入 Q&A。

---

## Slide 25 — Q&A

【准备回答方向】

- **技术栈时间线和资源**：合规 RPC 和身份注册是最轻量的，可以 3 个月内做出 MVP。重的部分是 Validium DA，至少 9-18 个月。
- **与 Prividium 的差异化**：我们有国库（40 亿+）、DeFi 收益生态（mETH/cmETH）和 MI4/Securitize 基础。Prividium 没有开放 DeFi 组合性。
- **合规方案选型**：KYC 层面可以集成现有 zkKYC 方案。合规策略引擎参考 ERC-3643/T-REX 体系。
- **支付子场景如何嵌入**：机构金融的 B2B 结算本质上就是支付。Paymaster 加 Payment Intent SDK 加商户财库是第一个落地点。
- **为什么不赌 AgentFi**：短期热度不等于长期壁垒。Base 有 Coinbase 分发，Solana 有性能优势——我们在这个赛道没有结构性护城河。
- **Canton 设计思想如何借鉴**：三个方向——Regulatory Observer 角色（合约级 observer role，监管方获可审计视图）；Sequencer/Mediator 职责分离（可引入独立 compliance service）；ACS Commitment（企业 Zone 可验证状态摘要，供多方 reconciliation）。是概念借鉴，不是技术栈迁移。
- **Paladin 的 Besu 替换可行性**：Layer A 的 Besu 可以直接换成 geth/op-geth，因为 Paladin 只用标准 JSON-RPC 17 个方法，无 Besu 专有 API 依赖。Layer C 的 Pente ephemeral EVM 替换成本更高——需要重实现 PenteDomain、evm_runner 和 statedb 适配层。如果选 geth 做 ephemeral EVM，需解决 vm.StateDB 接口和 trie/snapshot 的隐含耦合；如果选 revm，需要通过 CGO 做 Rust-Go 桥接。估计 3-6 个月工程量。Noto 和 Zeto 不依赖 Layer C，可以先行。
