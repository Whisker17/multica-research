# 中文演讲稿 — Mantle 竞争格局与叙事方向分析

> 时长目标：~20 分钟 | 格式：逐 Slide 对应 | 【】内为演讲者备注

---

## Slide 1 — 封面

大家好，今天的内部分享主题是 Mantle 的竞争格局与叙事方向分析。我们花了几周时间，对整个 L2 赛道和相关竞品做了一次系统性的调研，目的是回答一个核心问题：Mantle 下一步该往哪走。

---

## Slide 2 — 议程

今天分三个部分来讲。

第一部分看市场现状——市场发生了什么变化，Mantle 面临什么挑战。第二部分看竞争对手——其他人在做什么，竞争压力从哪来。第三部分给出方向建议——我们评估了三条路线的技术可行性。

先说结论：我们的分析显示，**机构金融**是 Mantle 契合度最高的方向。具体为什么，以及怎么做，接下来展开。

---

## Slide 3 — L2 赛道格局演变

先看大盘。这张图是截至 5 月 25 号主要 L2 的 TVL 分布。

两个数字最直观：Arbitrum 大约 150 到 170 亿美金，占 40-44%；Base 大约 110 到 130 亿，占 28-33%。两家加起来吃掉了 L2 DeFi 流动性的 77%。

Mantle 的位置在 11 到 12 亿之间，排在第二梯队。日活地址大约 2,276——这个数字后面我会详细说。

再看右边的 DAU 对比。Base 日活 38 万，是 Mantle 的大约 168 倍。这不是一个数量级的差距，是两个数量级。

大背景是，2024 年 3 月 EIP-4844 上线后，Gas 费降了 80-90%。费用竞争作为差异化手段已经结束了。现在的竞争维度变了——变成了生态控制、用户分发、ZK 隐私、收益资产这些方向。

---

## Slide 4 — 叙事转向：DeFi → RWA / 机构金融

接下来看叙事变化。这里有两个对比。

左边是 DeFi 的天花板。全球 DeFi TVL 在 920 到 1400 亿之间，远低于市场曾经预期的 2500 亿。更关键的是，83-95% 的存入流动性在任意时刻是闲置的。Aave 一家拿了借贷市场 59% 的份额。纯靠 DeFi 激励的增长不可持续——Blast 从 27 亿 TVL 崩到 5500 万就是最极端的例子。

右边是 RWA 的加速。链上 RWA 总市值从 2025 年初的约 60 亿涨到现在的 310 到 340 亿，涨幅超过 200%。美国国债代币化到了 130 到 150 亿。BlackRock 的 BUIDL 有 25 亿 AUM，而且今年 5 月他们向 SEC 申请了一个 70 亿的货币市场基金上链。

但有一个深层矛盾需要注意。Vitalik 今年 2 月的文章明确倡导隐私优先和抗审查——FOCIL 已经确认纳入今年底的 Hegota 硬分叉。而机构金融需要 KYC、需要许可制。这两个方向在以太坊生态内是有结构性张力的。我们的建议是：公共 L2 保持中性结算层，合规能力放在 L3 或 Validium 层实现。

---

## Slide 5 — Mantle 当前定位与挑战

Mantle 目前是什么情况。

技术栈方面，OP Stack、Ethereum aligned、EigenDA，这些都是行业标准方案，没有独特的技术壁垒。

资产方面，mETH 大约 9.25 亿 TVL，是第四大 ETH LST；cmETH 大约 5.15 亿。稳定币供给峰值 8.25 亿，目前保留了 81%，大约 6.7 亿。这个资产基本盘是我们后面讨论方向时的重要支撑。

但用户活跃度是硬伤。看这条趋势线——Q1 2025 日活 3.8 万，到 Q2 降到 1.2 万，Q3 又跳到 5.3 万，然后 Q4 崩到 5-6 千，Q1 2026 继续降到 2,276。这种过山车说明我们的用户不是有机增长，波动太大。

新的增长支柱——MI4、UR、MantleX、Aave V3——都还在早期阶段。Aave V3 上线后 12 天吸引了 2.9 亿存款，但被评估为激励驱动的，粘性存疑。

核心问题很明确：TVL 部分恢复了，但用户在流失，我们需要找到下一个叙事锚点。

---

## Slide 6 — Chapter 1 小结

总结第一章的三个要点。

一，DeFi 要守，但不能指望它带动增长。二，RWA 和机构金融是链上最快增长的叙事，年增长超过 200%。三，合规基础设施正在成为新的竞争维度——在我们调研的五条链里，只有 zkSync 有。

接下来看竞争对手具体在做什么。

---

## Slide 7 — 竞品分析框架

我们把竞争对手分成三类。

第一类是 L2 竞品——Base、Arbitrum、Optimism、zkSync、StarkNet、X Layer——这是同赛道的直接竞争。第二类是 L1 通用链——Solana、Sui、BNB Chain——跨赛道的替代竞争。第三类是 L1 垂直链——Tempo、Circle Arc、Canton——新赛道的抢位竞争。

分析维度主要是两个：最近 90 天的 GitHub 代码活动，以及叙事方向的变化。我们要看的是他们实际在做什么，不只是在说什么。

---

## Slide 8 — L2 竞品：技术路线对比（上）

先看三个走「平台化」路线的 L2。

Base 在做客户端独立——Azul 升级是他们第一次脱离 OP 官方发版节奏，切到自己的 base-reth-node。Flashblocks 提供 200 毫秒的预确认。Beryl 在做安全代币的 PolicyRegistry。90 天内 1810 个 PR，开发强度最高。核心竞争力是 Coinbase 1.1 亿用户的分发能力，这是不可复制的。

Arbitrum 走的是多 VM + 应用链路线。Stylus 让你用 Rust/C 写合约，Orbit 做定制应用链，Timeboost 做 MEV 排序拍卖，BoLD 做无许可验证。DeFi 深度最强。

Optimism 在做 Superchain 协调层。1202 个 PR 基本都在 monorepo 里。一个需要注意的风险：op-geth 的支持在 5 月 31 号就到期了，之后必须迁移到 op-reth。这对 Mantle 有直接影响。

**关键判断**：这三家都在走生态扩张的路线。Mantle 的体量——2300 日活对比 Base 的 38 万——不够走这条路。

---

## Slide 9 — L2 竞品：技术路线对比（下）

再看另外三个。

**zkSync**——这是今天最重要的对标。他们在 DeFi TVL 崩了 96% 之后，完全转向了 ZK 隐私加企业。ZKsync OS 是 RISC-V 级别的虚拟机重写，Airbender 是下一代证明器。但最核心的是 **Prividium**——一个企业级的合规 Validium 方案。他们声称已经吸引了 35 家以上的金融机构。代码层面有完整的本地开发环境，包括 Keycloak 身份、受保护 RPC、区块浏览器。当然，35 家银行这个数字是供应商声称，我们没有独立验证。但 Prividium 作为模式的可行性是有代码证据的。

**StarkNet**——Cairo/STARK 体系，STWO 下一代证明器在积极开发。DeFi TVL 只有约 2 亿，但 ZK 工程深度领先。非 EVM 架构使得它不构成直接迁移竞争。

**X Layer**——这个要特别注意，因为和 Mantle 最像：都是交易所背景、都是 OP Stack L2。他们从 Polygon CDK 迁移到了 OP Stack，正在做 Exchange OS 和 Agent Payment Protocol。OKX 的 1.2 亿用户是他们的分发优势。

---

## Slide 10 — L1 通用链叙事动态

L1 通用链方面。

Solana 的 Alpenglow 是全新的共识机制，目标 Q3 上主网。Jito BAM 在做区块构建基础设施。他们声称有 100 亿稳定币供给和每月 2000 亿的稳定币转账。

Sui 的 gasless 稳定币转账已经上主网了——这是协议层的特性，不是补贴。USDC、USDY 等七个稳定币可以零 Gas 费 P2P 转账。DeepBook 做链上订单簿。

BNB Chain 的工程主要在 BSC 客户端稳定化和 reth 双客户端。250 毫秒块时间目标目前只是 BEP spec，没有实现 PR。AI Agent 叙事声量高但代码弱。

**要点**：L1 通用链在速度、生态和机构采用上全面加速，L2 不能只靠以太坊安全性这一个叙事。

---

## Slide 11 — L1 垂直链的冲击

这是竞争最直接的一类。

**Tempo**——Stripe 和 Paradigm 投的支付链。Payment Lane 把 Gas 分成系统、支付、通用三个池子，支付交易享有优先权。协议级稳定币 Gas，大约每笔支付 0.001 美元。BFT 共识目标 600 毫秒终局。主网已经运营，但实际交易量和商户深度我们没有独立验证。Zones 的有效性证明目前是空的——架构接口有了，证明还没。

**Circle Arc**——USDC 的发行方自己做了一条 L1。他们的 CCTP V2 已经支持 26 条链，累计 1260 亿美金转账量。StableFX 做机构级跨币种原子结算。8 种非美元合作稳定币。测试网有 100 多家机构参与，处理了 2.44 亿笔交易。主网 beta 预期今年夏天。ARC 代币预售 2.22 亿美元，FDV 30 亿。**有一个关键事实**：Circle 的主要文档——CCTP 支持列表、USDC 合约地址、Circle Mint 支持链——都没有列出 Mantle。

**Canton**——这是企业金融工作流的标杆。Broadridge DLR 每天结算 3680 亿美金，每月约 8 万亿。Goldman Sachs、HSBC、DTCC 都在用。他们用的是 Daml 合约语言和 need-to-know 隐私模型——非 EVM，开发者生态小，但在机构金融领域的生产落地无人可及。

**核心警示**：垂直赛道不是空白——已经有原生竞争者从架构层就针对特定场景做了优化。

---

## Slide 12 — Chapter 2 关键发现

三个结论，引出下一章。

一，生态扩张路线——Base、Arbitrum、Optimism 在做的平台化——Mantle 体量不够。二，垂直赛道已有原生竞争者——Tempo、Arc、Canton 各自占位，纯做垂直链不现实。三，但有一个差异化切入点：L2 加上合规基础设施，在通用链和垂直链之间找到自己的位置。zkSync Prividium 已经证明了这个位置是存在的。

那 Mantle 可以走哪条路？我们评估了三个方向。

---

## Slide 13 — 评估框架

我们对每个方向从四个维度做分析：市场规模、竞品格局、关键技术壁垒、Mantle 适配性。

三个方向和结论我提前告诉大家：AgentFi，弱；Payment Chain，中；机构金融，强。接下来逐个展开。

---

## Slide 14 — AgentFi（弱）

AgentFi 目前是最热的叙事之一。CoinGecko 上 AI Agents 分类市值约 36.8 亿美金，加密 AI Agent 赛道整体在 23 到 26 亿之间。但要注意，这个赛道仍处于早期概念验证阶段，真实使用信号有限。

竞争格局方面，Base 在这个方向的布局最完整——CDP AgentKit 加 x402 支付协议加 Base MCP 加 Coinbase 1.1 亿用户分发。Solana 有低费加 pay-kit，Sui 有协议级 gasless P2P，X Layer 有 APP 加 Agentic Wallet。

我在这里展开讲一下 Base 的 AgentFi 生态，因为它代表了这个赛道目前的最高水准。

做 AgentFi，链的基础设施需要六层能力：标准化 AI 接口、Agent 钱包加权限管理、低延迟执行、机器间支付协议、DeFi 流动性支撑、以及 Agent 发行平台。Base 在这六层上都有对应方案。

**Base MCP** 是他们 5 月 26 号刚发布的，基于 Anthropic 的 MCP 标准，让 AI 应用能直接执行链上操作。首发就集成了 Morpho、Moonwell、Aerodrome、Uniswap 等七大 DeFi 协议插件，采用 OAuth 2.1 安全模型。**CDP AgentKit** 是模型无关的开发框架，50 多个 TypeScript Actions、30 多个 Python Actions。Agentic Wallets 用 TEE 保护密钥，内置 Session Caps 和 Transaction Limits 策略引擎。**x402 协议** 激活 HTTP 402 状态码做机器间微支付，最低 0.001 美元，亚秒结算，峰值每周 15.6 万笔，已集成 Google AP2。

Agent 生态方面——Social 类的 Clanker 在 Farcaster 上自动发币，累计协议费用超过 5000 万美金，交易者 55.8 万。Virtuals Protocol 部署了超过 1.8 万个 Agent，年协议收入 Base 第二——超过 5900 万美金。Trading/DeFi 类 Agent 做 7 乘 24 收益监控和再平衡。生态支撑层有 Flashblocks 200 毫秒预确认，Smart Wallet 的 ERC-4337 加 ERC-7715 权限体系，以及 Aerodrome DEX 峰值 TVL 超 10 亿。

**Mantle 的适配性**：优势在于 EVM 兼容、mETH/DeFi 收益生态可支撑 Agent 财库、已有 AA 基础。但六维 Gap 全部需要补建——无 MCP server、无 Agent 专用权限体系、标准 2 秒区块时间无预确认、无 x402 等效协议、DEX 流动性深度不足、无 Agent 发行平台。

**判断：弱。**Base 已经构建了 AgentKit → Wallet → x402 → MCP 四层垂直整合加 Coinbase 分发，这是不可复制的结构性优势。Mantle 六维均需从零补建，差异化壁垒有限。

---

## Slide 15 — Payment Chain（中）

支付赛道在快速增长。稳定币供给 3207 亿，USDC 单季链上交易量 21.5 万亿，同比增长 263%。但渗透率只有全球支付的 0.02%。更重要的是，支付级链已有原生竞争者——Tempo 已有主网，Arc 预售 2.22 亿、100 多家机构参与测试网，Sui 的 gasless P2P 已经上线。

这里要强调一个关键认知：**Payment Chain 不等于通用链上部署支付合约**。它需要链在六个维度提供协议级能力——确定性终局（BFT 亚秒不可重组，不是 L2 的软确认）、费用确定性（稳定币计价、用户不可见）、支付专用 blockspace（保留容量，不被 DeFi 挤出）、稳定币原生支持（协议级 memo、合规、fee eligibility）、跨链互操作（安全低延迟 burn-and-mint）、以及合规基础设施（链级 transfer policy 执行）。

看看具体竞品怎么做的。

**Tempo** 的核心创新是 Payment Lane——协议级 blockspace 三分区。System Lane、Payment Lane、General Lane，支付交易享有保留 gas 容量，DeFi 拥堵不影响支付。共识是 Commonware Simplex BFT，目标 500 到 600 毫秒确定性终局，双进程隔离设计降低执行负载对共识路径的影响。稳定币 Gas 以 attodollars 计价，一笔 TIP-20 transfer 约 0.001 美元。TIP-20 是预编译级 token 标准，原生支持 memo、pause、fee eligibility。TIP-403 做合规策略注册表预编译。Enterprise Zones 提供 Reth validium 隐私执行环境，但 proof 还是空的，不推荐生产使用。性能数据是设计目标，生产 SLA 待验证。

**Circle Arc** 走的是完全不同的路线——USDC 发行方自建全栈金融 OS。Malachite BFT 约 780 毫秒终局，小规模可到 330 到 490 毫秒，约 5 万 TPS。USDC 是原生 Gas 代币，EWMA 费用平滑加 Paymaster 多币种（内置 FX 引擎）。最大的结构性优势是 CCTP V2——原生跨链 USDC，26 个域，累计 1260 亿美金，同比增长 740%。第三方链不可复制。StableFX 做机构 FX 引擎，8 种合作稳定币，RFQ 执行加原子结算。测试网 100 多家机构含 BlackRock、Goldman、Mastercard。主网预计今年夏天。

两者核心差异：**Tempo 优化支付交易管道**（Payment Lane 加固定基础费加 TIP-20 预编译），**Arc 构建全栈金融 OS**（USDC 原生发行加 CCTP 跨链加 StableFX 加机构验证者）。Tempo 缺跨链，Arc 缺 Payment Lane。

**Mantle 的 Gap 分析**：结构性差距三项——L2 软确认不等于 BFT 终局（需等 L1 约 13 分钟）、Circle CCTP 未列 Mantle、无协议级稳定币支持。可补齐的有 Paymaster 加 AA 做稳定币 Gas UX、应用层合规合约、Payment Intent SDK。需要改造的有 sequencer payment tag 加 soft reservation、predeploy 合规策略注册表。需要架构决策的有推动 Circle CCTP 合作、BFT fast-finality、协议级稳定币 Gas。

**判断：中。**纯支付链叙事六维中三维为结构性差距，Mantle 不占位。但 **B2B 结算加财库层**定位可行——Paymaster 加 Payment Intent SDK 加 merchant treasury 加 DeFi yield 的组合作为切入。支付作为机构金融的子场景仍然重要，不是完全放弃。支付需要 Web2 分发，纯 crypto 方案很难 mass adoption。

---

## Slide 16 — 机构金融：市场机会

现在看契合度最高的方向。

链上 RWA 从 2025 年初 60 亿到现在 310 到 340 亿，年增长超过 200%。这个趋势不是预测——有实实在在的催化因素。BlackRock BUIDL 25 亿 AUM。SEC 发布了代币化证券声明。GENIUS Act 已签署。BlackRock 今年 5 月还向 SEC 申请了 70 亿美金货币市场基金上链。MiCA 和 FATF 在全球层面推动合规框架。

机构要什么？四个词：合规、隐私、数据主权、审计。没有这些，真正的机构资金不会上链。

**核心论点**：这不是"要不要做"的问题，而是"谁先做好"的问题。

已经有人在做了。zkSync Prividium 声称吸引了 35 家以上金融机构——Cari Network 联合五家美国区域银行，合计存款超过 6000 亿美金，目标 2026 年 Q3 试点。Deutsche Bank 确认了合作关系。BitGo 提供机构级托管。

Canton 有更强的生产验证：Broadridge DLR 日均结算 3680 亿美金，月近 8 万亿回购结算。DTCC 计划 2026 上半年进入 controlled production MVP。

这些数字说明需求是真实的，而且已经有人在吃这块市场。

---

## Slide 17 — 机构金融：对标 zkSync Prividium

Prividium 的架构值得细看。我同时把 Canton 的设计理念拿来做对比。

Prividium 的核心是一条**许可制 Validium 链**，运行在机构自有基础设施上。结算路径是三层的：用户通过 Okta 或 SIWE 认证，进入 Proxy RPC（做三步验证：JWT 加钱包加函数权限），然后到 Sequencer 私有执行，再到 Prover 用 Airbender GPU 生成 STARK 证明，通过 ZKsync Gateway 聚合后提交到以太坊 L1。L1 只能看到状态根和证明——零交易数据。数据存在 PostgreSQL 加 Blob Store 的私有子网里，不暴露到互联网。本地开发环境已开源，Docker Compose 一键起全套：Prividium API、Keycloak 身份、Admin/User Panel、zkSync OS、Sequencer、Prover、Block Explorer、Prometheus/Grafana。

准入控制有四层。第一层身份认证——Okta OIDC 或 SIWE 或混合模式。第二层 Proxy RPC 网关——三步验证加审计日志，是整个网络的唯一入口。第三层 RBAC 权限——合约函数级粒度，可限参数，Admin Dashboard 配置不用写代码。第四层 L1 TransactionFilterer——白名单过滤强制交易路径。

隐私保证是整链级的——Validium 固有特性，不是额外功能。ZK 证明保证状态转换正确性。

**Canton 的设计对比**：Canton 代表了完全不同的范式。Prividium 是 "Prove-Not-Reveal"——整链对外不可见，但运营商可见全部。Canton 是 "Need-to-Know"——没有任何节点持有全局状态，每方只看到子交易级投影，连 Sequencer 和 Mediator 都看不到交易明文。Canton 的优势是金融合约语义最强——Daml 的 signatory/observer/controller 天然映射金融合同。生产验证最扎实——月结算 8 万亿。Canton 的劣势是非 EVM、开发者池小、与 OP Stack 适配性低。

**Mantle 路径**：在 OP Stack 框架下实现 Prividium 模式的合规隔离层——EVM 兼容，开发者迁移成本低，Solidity/Foundry 直接可用。同时借鉴 Canton 的 Observer 角色和职责分离设计思想。我们不需要复制 ZK 证明系统——合规和准入才是 Prividium 的价值核心。

---

## Slide 18 — 机构金融：Mantle 合规技术栈路线图

这是今天最重要的一页 Slide——技术差距矩阵。基于 Prividium 加 Canton 双对标更新。

【逐行指读】

合规 RPC 网关：Prividium 有 Proxy RPC 加三步认证，我们没有。需要构建认证加 RBAC 加审计的网关层，复杂度中。

RBAC 权限系统：Prividium 做到合约函数级，Canton 用 Daml 的 signatory/observer 模型。我们目前没有。目标是合约函数级加参数级，通过 Admin Dashboard 加策略引擎实现，复杂度中。

身份注册：Prividium 用 Okta/SIWE 加 Keycloak，Canton 用 Party/Participant 拓扑。我们无原生方案。目标是 KYC Registry 合约，集成 Okta/SIWE 加链上注册，复杂度中。

审计与 Selective Disclosure：Prividium 有 Private Explorer 加选择性披露，Canton 有 Observer 加审计日志。我们没有。目标是可导出审计加选择性披露，通过 Audit Log API 加 SD 合约实现，复杂度中。

Validium 隐私 DA：Prividium 的运营商 DB 全量私有，Canton 各方本地 ACS。我们用 EigenDA 是公共的。需要 EigenDA 改造或独立 DA 层，复杂度高。

企业 Zone/L3：Prividium 是 ZK Stack Validium 变体，Canton 是 Multi-Synchronizer。我们有 MIX4 基础可以演进，复杂度高。

ZK 合规证明：Prividium 有 STARK Airbender，Canton 用 2PC。我们有 SP1 规划中。可以集成现有方案做 KYC-in-ZK，复杂度中。

合规执行层：Prividium 有 TransactionFilterer，Canton 有 2PC verdict。我们据说有 ERC-3643 demo 但无公开确认。目标是身份加策略加审计加披露四位一体，通过 ERC-3643 扩展加 predeploy 实现，复杂度中到高。

L1 Bridge Filter：Prividium 有 TransactionFilterer 限制未授权强制交易。我们没有。需要 L1/L2 bridge 白名单合约，复杂度低。

**Canton 设计思想的借鉴**——这里是概念层面，不是技术栈迁移。三个点：第一，Regulatory Observer 角色——合约级 observer role，监管方获可审计视图而非全量明文。第二，Sequencer/Mediator 职责分离——可引入独立 compliance/verdict service。第三，ACS Commitment——企业 Zone 可验证状态摘要，供多方 reconciliation。

**核心信息**：技术栈几乎从零构建——但路径明确，有双对标可参考，每一项都有清晰的实现路径和复杂度评估。

---

## Slide 19 — 机构金融：Mantle 适配性评估

优势方面。

第一，EVM 全生态加以太坊 L2 合法性——机构用 Solidity/Foundry 直接开发，集成成本低。Prividium 模式无需切换开发工具链。第二，mETH 和 cmETH 的收益生态——这是 Tempo、Arc、Canton 都没有的独特价值。机构不只是要结算，结算完的资金需要收益管理。第三，MI4/Securitize 基础加超过 40 亿美金国库。第四，已有 Solidity/Foundry 工具链。

挑战方面。技术栈几乎从零构建——但路径明确，从 Proxy RPC 到 RBAC 到 Private DA 到 Zone，分阶段推进。CCTP 缺失是结构性硬伤。还没有生产级的机构客户案例。

对标定位：**Prividium 模式适配度高**——EVM 兼容加企业级打包加 OP Stack 可映射。Canton 模式不可直接迁移——Daml/JVM/2PC 与 Rollup 冲突——但设计语言值得借鉴。

**判断：强。**可走 Prividium 模式，且有独特国库和收益生态优势。

**分阶段路线**：

Phase 1，0 到 3 个月，准入与审计 MVP——Compliance RPC Gateway 加 Identity/KYC Registry 加 Sequencer Policy Engine 加 Audit Log Exporter 加 L1 Bridge Filter。不需要碰主链隐私。

Phase 2，3 到 9 个月，私有数据层——Private DA/Encrypted Archive 加 Selective Disclosure API 加 zkKYC PoC 加 Regulatory Observer API。

Phase 3，9 到 18 个月，企业 L3/Validium Zone——Per-tenant L3 Zone 加 Zone Sequencer 加 Private DA 加 ZonePortal Settlement 到 L2 加 Admin Dashboard 无代码配置。

一个战略原则：**先产品化合规可见性，再产品化密码学隐私**。许可、审计、披露 API——这些比 FHE 更接近企业收入。

---

## Slide 20 — 三方向对比总结

最后把三个方向放在一起看。

AgentFi——弱，赛道早期，红海竞争，我们没有结构性优势。Payment Chain——中，可以作为子场景但不该作为主叙事。机构金融——强，市场加速，先发者少，路径明确，Mantle 有独特优势。

---

## Slide 21 — 结论与下一步

总结三个核心结论。

一，L2 赛道已经从通用竞争进入差异化定位阶段。不选方向就是选择被边缘化。

二，竞争压力来自三个维度：L2 平台化、L1 替代、垂直链抢位。三面夹击。

三，**机构金融是 Mantle 契合度最高的叙事方向**。以 zkSync Prividium 为对标，利用国库和收益生态优势构建合规技术栈。

建议的下一步：立即评估 CCTP 和 Circle 的合作可行性——这是一个结构性缺口。Q3 做合规 RPC 加身份注册 MVP。Q4 开始企业 Zone PoC。

还有几个开放问题需要后续跟进：op-geth 的 EOL 迁移、Mantle 开发者活动的量化、ERC-3643 demo 的现状确认。

以上就是今天的分享。接下来进入 Q&A。

---

## Slide 22 — Q&A

【准备回答方向】

- **技术栈时间线和资源**：Phase 1 的合规 RPC 和身份注册是最轻量的，可以 3 个月内做出 MVP。重的部分是 Validium DA，至少 9-18 个月。
- **与 Prividium 的差异化**：我们有国库（40 亿+）、DeFi 收益生态（mETH/cmETH）和 MI4/Securitize 基础。Prividium 没有开放 DeFi 组合性。
- **合规方案选型**：KYC 层面可以集成 Polygon ID、Sismo 等现有 zkKYC 方案。合规策略引擎参考 ERC-3643/T-REX 体系。
- **支付子场景如何嵌入**：机构金融的 B2B 结算本质上就是支付。Paymaster 加 Payment Intent SDK 加商户财库是第一个落地点。
- **为什么不赌 AgentFi**：短期热度不等于长期壁垒。Base 有 Coinbase 分发，Solana 有性能优势——我们在这个赛道没有结构性护城河。
