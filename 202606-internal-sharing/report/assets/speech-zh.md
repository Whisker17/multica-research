# 中文演讲稿 — Mantle 竞争格局与叙事方向分析

> 时长目标：~20 分钟 | 格式：逐 Slide 对应 | 【】内为演讲者备注

---

## Slide 1 — 封面

Hi everyone, thank you for joining today's session. I'll be presenting in Chinese to ensure accuracy and depth of the analysis — but feel free to ask questions in either language during the Q&A.

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

但有一个深层矛盾需要注意。Vitalik 最近在密集推动一个叫 **CROPS** 的框架——Censorship Resistance、Capture Resistance、Openness、Privacy、Security。今年 3 月以太坊基金会正式发布了新 mandate，把 CROPS 定义为以太坊的核心身份。Vitalik 原话是：以太坊要做"sanctuary technology"，要成为数字自由的最后一道防线，而不是去卷速度和 TPS。5 月他进一步表态——基金会会"选择 longevity over breadth"，收缩规模、减少卖 ETH，全面聚焦 CROPS。他甚至说，一味追求快和可扩展但只比竞争对手稍微去中心化一点——"is a route to mediocrity"。

这个方向和机构金融的需求是有结构性张力的。CROPS 强调抗审查、隐私优先、开源透明。但机构要的是 KYC、KYB、许可制准入、数据可审计。一个追求"没有任何政府或组织能控制"，另一个需要"监管方能随时查看"。这两个诉求在以太坊生态内目前没有被调和。

而且这不只是理念问题，已经影响到以太坊社区的实际走向——今年已经有至少 8 位资深 EF 成员离职，5 月就走了 5 个。前 EF 研究员 Dankrad Feist 甚至提议成立一个独立组织，拿至少 10 亿美金的 ETH 专门做性能和用户增长——也就是 CROPS 不直接解决的那些问题。

对 Mantle 来说，这个张力反而可能是机会。以太坊主网在 CROPS 方向越走越远，机构合规场景就越需要一个既继承以太坊安全性、又能满足合规要求的执行层——这正是 L2 可以填补的空间。

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

**Base** 在做客户端独立——Azul 升级 5 月 28 号主网激活，收敛到 base-reth-node 加 base-consensus 自有技术栈。不过 Azul 的上线过程并不顺利。原定 5 月 13 号激活，因为 proof node 性能没达标推迟了两周。上线前后也出了一些状况——5 月 12 号有一次 38 分钟的 Tx 数据提交中断，正常情况下每 47 秒就该提交一次。更值得关注的是，Azul 激活后第二天——5 月 29 号——就出现了 Base Mainnet Withdrawal Delay，提款出现延迟。这对一个主打"把提款从 7 天缩短到 1 天"的升级来说，上线次日就出提款延迟，多少有点尴尬。大家可以去 status.base.org 看完整的 incident 记录。另外一个风险点是审计覆盖偏薄——bug bounty 只开了 13 天、25 万美金，没有正式的第三方审计报告，对于一个系统级的 proof 架构变更来说，这个保障记录偏弱。当然 Azul 本身的目标是很有价值的——TEE 加 ZK 双证明体系把提款终局从 7 天压缩到 1 天，Flashblocks 200 毫秒预确认也已经在主网运行。

合规资产方面，Base 在做一个叫 **B20** 的原生合规资产框架，这是 Beryl 升级引入的。简单介绍一下——B20 不是普通的 ERC-20 合约，而是**预编译级别**的 token 标准，直接内嵌在 EVM 执行层。它有三个 token 变体：DEFAULT 是标准合规 token、18 位精度；STABLECOIN 是法币锚定、6 位精度、带 ISO 4217 货币代码；SECURITY 是金融证券、带 ISIN 编码和赎回机制。配套的 **PolicyRegistry** 也是预编译合约，提供全局的转账策略注册——支持 BLOCKLIST 和 ALLOWLIST 两种模式，可以在合约函数级别做准入控制。还有完整的 RBAC 角色体系——铸造、销毁、暂停、元数据管理都有独立角色。代码已合并但主网尚未激活——通过 ActivationRegistry 做功能开关控制。这个设计思路值得注意——Base 在协议层预埋了合规资产能力，说明他们也在为机构场景做准备。

90 天内 1810 个 PR，开发强度最高。核心竞争力是 Coinbase 1.2 亿用户的分发能力，这是不可复制的。

**Arbitrum** 走的是金融原生加可定制 Nitro stack 路线。先说 **BoLD**——全称 Bounded Liquidity Delay，这是 Arbitrum 的新一代争议解决协议。简单说，之前 Arbitrum 的欺诈证明是 1 对 1 的——一个挑战者对一个被挑战者。BoLD 改成了**全员对抗**模式，所有诚实方和恶意方同时参与，通过确定性的 Merkle 证明在固定时间窗口内（约 12 天）解决争议。核心价值是**无许可验证**——任何人都可以质押 bond 来验证和挑战状态断言，不再需要被列入白名单。这对 Arbitrum 走向 Stage 2 rollup 至关重要。BoLD 已经在 2025 年初上线了 Arbitrum One 和 Nova 主网，我们在代码仓库里看到的 Draft 和 DO NOT MERGE 标记是后续迭代的 PR，不是协议本身还没部署。值得关注的是，他们正在开发 **MEL——Message Extraction Layer**，这是 BoLD 的下一步演进。简单说，MEL 定义了验证者如何从 Sequencer Inbox 和 Delayed Inbox 中提取和处理消息，为欺诈证明提供更规范的消息来源层。我们在 nitro-contracts 仓库看到了 MEL OSP 合约和 MEL Rollup 合约的 PR，在 nitro 仓库看到了 Post-MEL assertions 和 BoLD with MEL 的 PR——全部处于 open 或 draft 状态，部分标记了 DO NOT MERGE。这说明 Arbitrum 在把 BoLD 的验证架构往更深的方向推——不只是争议解决，而是从消息提取到断言生成到欺诈证明的完整链路重构。Timeboost 做 MEV 排序拍卖。Stylus SDK 从 v0.10.2 迭代到 v0.10.7，支持 WASM 多语言合约。90 天 256 个 PR，34 个贡献者。工程重心在底层硬化——安全与排序，不是 Orbit 应用链代码爆发。

**Optimism** 在做 Superchain 协调层。1202 个 PR 主要在 monorepo 里，98 个 PR 作者，周 PR 从第 9 周的 50 个加速到第 21 周的 129 个。op-reth/kona Rust 迁移和 op-supernode/supervisor 互操作 devnet 在同步推进。一个需要注意的风险：**op-geth 的支持在 5 月 31 号就到期了**，之后必须迁移到 op-reth。这对 Mantle 有直接影响。

**关键判断**：这三家都在走生态扩张的路线。Mantle 的体量——1,600 日活对比 Base 的 43.5 万——不够走这条路。

---

## Slide 9 — L2 竞品：技术路线对比（下）

再看另外三个。

**zkSync**——这是今天最重要的对标。他们的工程已经从单一 zksync-era 仓库扩展为多仓库栈：ZKsync OS Server 最活跃 404 个 PR，OS RISC-V 多 VM 支持 EVM、EraVM、Wasm 共 146 个 PR，Airbender GPU 证明器 94 个 PR，Gateway 加 era-contracts 154 个 PR。跨 5 个组织总共 1,427 个 PR——远超 era 单仓库 130 个 PR 数据所暗示的活跃度。最核心的是 **Prividium**——一个企业级的合规 Validium 方案，本地开发环境已开源，Docker Compose 全栈包含 Keycloak 身份、Protected RPC、Admin Panel、zkSync OS、Sequencer、Prover、Block Explorer、Prometheus/Grafana。他们声称已吸引 35 家以上金融机构——但这个数字来自合作方 Cari Network 声称，不是 zkSync 直接披露，我们没有独立验证。Prividium 目前是本地开发环境，非生产部署证明。

**StarkNet**——Cairo/STARK 体系 ZK 深度领先。Sequencer/OS 有 1,324 个 PR，是所有链中最高。Cairo 发了四个版本，STWO Circle STARK 223 个 PR。v0.14.2 主网已激活。但 BTCFi 叙事声量大代码极弱——strkBTC 只有 2 个 PR 和 8 个 commit。非 EVM 架构不构成直接迁移竞争。

**X Layer**——和 Mantle 最像：都是交易所背景、都是 OP Stack L2。Exchange OS 白皮书 V1.0 描述了双环境设计——X Layer EVM 治理加 TradeZone 30 万 TPS 撮合——但只是白皮书，无生产部署。

	值得展开说的是 **APP（Agent Payments Protocol）**——4 月 29 号发布 V1.0 白皮书，定位是把 Agent 支付从"单笔交易"升级到"完整商业关系"。架构分三层。**传输层**做通信无关的消息投递——不只是 HTTP，还支持 XMTP、Telegram、Discord、Slack 甚至二维码和离线方式，这意味着 Agent 之间的支付不一定走 API 调用，可以走即时通讯。**Broker 编排层**负责持久化 challenge/paymentId、生成投递信封（URL/卡片/二维码/原始数据）、签名验证和链上广播（可选 gas 代付）。**结算层**定义了四种支付 intent：charge 是一次性固定价格支付；batch 是高频微支付批量结算，适合 IoT 场景；session 是按使用付费——比如 LLM token 流式计费，关闭通道时结算；upto 是预授权上限——"最多花 5000 token"，用完再结算。白皮书还定义了第五种 escrow——任务交付加争议解决，但标注为 coming soon，合约尚未部署。

	APP 有两种部署模式。**A2MCP（Agent-to-MCP）**：买方 Agent 消费带定价的 HTTP 服务，通过 HTTP 402 返回 challenge——这和 Base 的 x402 路径一致。**A2A（Agent-to-Agent）**：卖方本身也是 Agent，通过即时通讯投递 challenge——这是 x402 覆盖不到的场景，APP 在这里做了词汇扩展。APP 和 x402 的关系不是替代而是组合——在 HTTP 场景下 APP 对齐 x402，在多轮交互和非 HTTP 场景下 APP 扩展了协议边界。同时 APP 直接消费 MPP（Machine Payments Protocol）的 EVM 线格式。

	配套的 **Agentic Wallet** 3 月 18 号发布，用 TEE 安全飞地做 Agent 密钥管理，支持 20 多条链。底层是 OKX 的 **Onchain OS** 平台——日处理 12 亿次 API 调用、支撑全球 3 亿美金日交易量。

	但看代码就冷静了。base-contracts 仓库 3 个月只有 44 个 commit 和 2 个 PR，payments 仓库 35 个 commit 和 10 个 PR，mpp-specs 仓库 12 个 commit 和 1 个 PR。和 APP 白皮书描述的完整度相比，工程实现还在早期。OKX 1.2 亿用户是分发优势，但 L2BEAT TVS 只有 1023 万美金——交易所用户没有有效转化为链上生态。

---

## Slide 10 — L1 通用链叙事动态

L1 通用链方面。

**Solana** 的 Alpenglow/Votor 是全新共识机制，用 BLS 聚合实现亚秒终局，Q3 主网目标但还在压力测试。开发主体已从 Solana Labs 迁移到 Anza 和 Jito 双客户端分工——Labs 的 116 个仓库几乎全部不活跃了。Pay.sh 值得多说两句。这是 Solana 基金会和 Google Cloud 今年 5 月联合推出的——一个 pay-as-you-go 的 API 市场，让 AI Agent 用稳定币在 Solana 上结算。底层用的是 **x402 协议**——就是 Coinbase 在 Base 上推的那个 HTTP 402 支付标准，现在已经进了 Linux Foundation，背后有 Google、Stripe、AWS、Visa、Mastercard。Pay.sh 的做法是在 Google Cloud 前面加一层 API 代理，Agent 用 Solana 钱包当身份层——不用注册 Google 账号、不用管订阅，按调用付费，接入 Gemini、BigQuery、Vertex AI 等 Google Cloud 服务加 50 多个社区 API。Google Cloud Web3 策略负责人 Rich Widmann 原话说"Solana was the right choice for settlement"。这个定位很清晰——他们要做自主 Agent 经济的结算层。

再看更大的图景。Solana 基金会主席 Lily Liu 去年提出的 **PayFi** 概念正在快速落地——核心是围绕资金的时间价值构建链上金融原语，用去中心化技术缩短结算周期。机构端的信号也在加速：J.P. Morgan 和 Anchorage Digital 在 Solana 上做代币化稳定币储备，Western Union 计划今年 5 月在 Solana 上发 USDPT 稳定币，Goldman Sachs 披露持有 1.08 亿美金 SOL，BlackRock BUIDL 在 Solana 上清算了 5.5 亿，Solana 加入了 Mastercard Crypto Partner Program，Huma Finance 的 PayFi 网络累计交易量突破 100 亿。

核心威胁是他们正在把零售流量、AI Agent 支付、PayFi 和机构叙事连成一条完整的线——从消费者到机器到机构，一条链全覆盖。

**Sui** 的 gasless 稳定币转账已经上主网了——7 个白名单币种包括 USDC、USDY 等，gasless TPS 上限 300。这是协议层的特性，不是补贴。但这个功能刚上线就出了严重事故。5 月 28 到 29 号，Sui 主网 **48 小时内宕机三次**。根因是 v1.72 升级引入的 address balances 和 gasless stablecoin transfers 功能里的一个 gas smashing 逻辑 bug——当交易因余额不足被取消时，gas smashing 步骤仍然尝试花费那些资金，产生了负余额差值，直接导致验证者结算进程崩溃。第一次宕机将近 7 个小时。更离谱的是，Sui 基金会在 post-mortem 里承认，修复第一次宕机的补丁本身就有已知的再次宕机风险——他们接受了这个风险为了尽快恢复网络，结果第二天早上就再次命中了那个已知问题。第三次宕机发生在 epoch 切换时，还是同一个修复引发的级联故障。SUI 代币跌到 0.90 美金，188 万美金仓位被清算。虽然没有用户资金损失，但 DeFi 用户在宕机期间完全无法管理杠杆仓位。算上今年 1 月的共识分歧宕机，Sui 2026 年已经有三次重大可靠性事故了——让人想起 Solana 早期的可靠性问题。这对机构采用是一个信任打击。

DeepBook 做现货加保证金。Hashi 做 BTC 机构托管接了 BitGo、FalconX、Ledger 等 6 家。Walrus 存储加 Seal 加密密钥。MystenLabs 跨组织 2,966 个 PR。

**BNB Chain** 的工程主要集中在两条线：BSC Go 客户端（90 天 92 个 PR）和 **reth Rust 双客户端**（151 个 PR）。值得注意的是，reth 团队的 PR 产出已经超过了 BSC Go 团队——5 到 6 个全职开发者，目前是 v0.0.9-beta，还没到生产就绪，但投入力度说明这是他们的战略重心，在为多客户端生态做准备。

硬分叉方面，BNB Chain 过去一年的出块速度进化路径很清晰：3 秒到 1 秒到 500 毫秒到 450 毫秒，执行力不差。Mendel 硬分叉 4 月 28 号主网激活，对齐以太坊 Osaka，包含 MEV 竞价 gas 上限、bid block size 限制等 9 个子 BEP。下一步 Pasteur 硬分叉在准备中，核心是 **BEP-675 Builder-Proposed Blocks**——验证者对 builder 提交的区块做盲签名，类似 PBS 的 MEV 基础设施设计，技术上有参考价值。但 250 毫秒出块目标只有 BEP-670 spec 合并了，**没有任何客户端实现 PR**，当前仍然是 450 毫秒。

AI Agent 叙事是 BNB Chain 今年推得最猛的方向。数据很好看——15 万个链上 AI Agent 注册、Agent Survival Pack 联合 6 家生态伙伴、ERC-8004 agents 单日峰值 52.3 万笔交易、agent 驱动的 DEX 交易量单日 1800 万美金。但看代码就不一样了。bnbchain-mcp 的 PR 关闭率 89%——46 个 PR 创建，只有 4 个合并，大部分是 AI 生成的 PR noise。bnbagent-sdk 频繁 breaking changes 和合约重部署，核心开发者只有 2 个。15 万 agent 注册数要打个折扣——注册成本极低，不代表真实使用。这里有一个很有意思的**叙事-工程错配**：官方推得最猛的方向（AI Agent）代码成熟度最低，工程投入最大的方向（reth 双客户端）几乎没有市场声量。

另外两个信号。**opBNB 实质废弃了**——一名开发者，90 天只有 11 个 PR，Laplace 硬分叉的 PR 开了两个多月没合并。BSC L1 性能越来越强，L2 的差异化空间被自己压缩了。**Greenfield 存储也在萎缩**——只剩 2 个核心开发者，每季度 1 个前端 PR，说好的 AI 加存储协同，代码层面零证据。

**要点**：L1 通用链的威胁不是单一维度——Solana 把 consumer 加 PayFi 加机构连成一条线，Sui 把协议级支付 UX 加 BTC 托管加数据栈打包成产品，BNB Chain 靠交易所流量但技术栈实际在收缩。L2 不能只靠以太坊安全性这一个叙事。

---

## Slide 11 — L1 垂直链：赛道已有原生占位者

这是竞争最直接的一类。大家看这三张卡片——每张代表一条专门为某个赛道设计的 L1。

【左卡片】**Tempo**——Stripe 和 Paradigm 孵化的支付专用链，去年 10 月完成 5 亿美金 Series A、估值 50 亿，Sequoia、Ribbit Capital、SV Angel 参投。今年 3 月主网上线。设计阶段的参与方阵容值得注意——**Mastercard、UBS、Deutsche Bank、OpenAI、Shopify** 都参与了链的规格制定，这不是一般的 crypto 项目能拉到的资源。

标志性进展是 **Visa 4 月 14 号宣布运行 Tempo "锚定验证者"节点**。这不是简单挂个名——Visa 原话说节点是"configured and managed in-house"，经过了 6 个月和 Tempo 工程团队的联合开发。这是 Visa 在区块链基础设施层面**最深度的运营承诺**。同时 Stripe 自身和 Zodia Custody（渣打银行控股）也是第一批外部验证者。Visa 还在 Tempo 的 MPP（Machine Payments Protocol）基础上推出了 **Visa CLI**——让 AI Agent 可以直接用 Visa 卡消费，把传统支付网络和链上 Agent 经济接通了。

技术层面，**T4 硬分叉 5 月 18 号主网激活**。核心变更是 TIP-1031——把共识上下文（epoch、view、parent_view、Ed25519 proposer 公钥）直接嵌入区块头，这是实现 deferred verification（乐观公证加异步验证）的前置条件，也就是说他们在为共识层进一步优化终局性做铺垫。同时 T4 捆绑了一批审计驱动的正确性修复。Payment Lane V2（TIP-1045）收紧了支付交易的分类规则——从 V1 基于 TIP-20 地址前缀的检查升级到更严格的选择器白名单、空访问列表和有界密钥授权，进一步强化了支付 blockspace 的隔离性。T5 也已经在准备中了。

但 Zones 企业隐私层还在测试网——我们看了代码，`batch.rs` 里的 validity proof 验证是 **空 stub**，proof bytes 直接是空的。也就是说隐私层的证明系统还没有实际集成，不是生产就绪。另外目前验证者集合是许可制的，虽然目标是逐步走向无许可，但早期阶段本质上是一条许可链。

【中卡片】**Circle Arc**——USDC 发行方自建全栈金融 OS。先说背景——Circle 收购了 Informal Systems 的 Malachite 团队，把 Tendermint 衍生的 BFT 共识引擎和整个团队直接并入公司。这不是"基于某个开源项目搭建"，而是把共识层的核心人才和 IP 整合进来了。

标志性进展是 **ARC Token 预售 2.22 亿美元、FDV 30 亿**——a16z 领投 7500 万，BlackRock、Apollo、ICE、ARK Invest、Standard Chartered Ventures、Haun Ventures、General Catalyst、Marshall Wace 等 13 家参投。这是第一个主要上市公司（Circle 已在纽交所上市，代码 CRCL）做的 token 预售，本身就是一个监管信号——他们认为这条路在合规框架内走得通。投资者保护条款也很有意思：多年锁定期，如果 2028 年 5 月前没完成 PoS 转换，投资者有回购权。

**USDC 作为原生 Gas** 是 Arc 最核心的设计选择，值得多说一点。我们都知道以太坊的 EIP-1559——每个区块根据上一个区块的利用率来调整 base fee。问题是它只看前一个区块，所以一次 NFT mint 热潮就能让 gas 费瞬间飙升 10 倍甚至 100 倍。Arc 的做法不同——用 **EWMA 指数加权移动平均**来计算 base fee，同时参考多个历史区块的利用率，越近的权重越高、越远的指数衰减。效果是费用变化被平滑到多个区块上，短期需求尖峰不会立刻传导到价格。在此之上还加了 **bounded base fee**——设了严格的上下限，即使网络极端拥堵，费用也不会突破天花板。目标是每笔交易大约 **1 美分**。

这和 Tempo 的费用模型形成有意思的对比。Tempo 的 base fee 是**写死在协议常量里的**——`TEMPO_T1_BASE_FEE = 20,000,000,000` attodollars/gas，只能通过硬分叉修改，没有任何动态调整机制。一笔 TIP-20 转账固定约 $0.001，不管网络多拥堵费用都不变。Tempo 不靠价格信号抑制需求，而是靠 Payment Lane 的 blockspace 预留来应对拥堵——总区块 gas 上限 500M，其中 General Lane 被限制在 30M，至少 420M gas 保证给支付交易。但如果支付交易本身超过了预留容量，没有"加价插队"的机制，只能排队或被丢弃。Arc 的 EWMA 则保留了市场信号但做了阻尼——允许费用温和上升来抑制需求，但通过上下限防止指数级飙升。三种模型各有取舍：EIP-1559 完全市场化，波动最大但资源配置效率最高；Tempo 完全固定，最可预测但放弃了价格调节能力；Arc 的 EWMA 加 bounded base fee 是中间路线——用平滑和限幅换取"稳定但保留弹性"。

还有一个容易忽略的点——**税务和会计处理**。每次企业用 ETH 或 MNT 这样的波动代币付 gas，可能都构成一次应税处置，需要计算市价调整。Arc 的 USDC 费用本质上是美元运营支出——没有外汇换算层、没有资本利得敞口。对机构财务部门来说，这把区块链基础设施成本变成了和 AWS 账单一样可预测的东西。Paymaster 未来还会支持 EURC 等其他合规稳定币自动兑换为 USDC。

**StableFX** 需要展开说一下，因为这是 Arc 商业模式的核心组件之一。FX 就是 Foreign Exchange、外汇——不同货币之间的兑换交易。传统 FX 市场日交易量 7.5 万亿美金，是全球最大的金融市场，但基础设施很老——场所碎片化、需要预先注资、T+1 甚至 T+2 结算、只在市场营业时间运行。企业想用稳定币做跨币种结算，但 USDC 和 EURC 之间的兑换仍然要走传统 FX 通道。StableFX 要解决的就是这个问题——**把机构 FX 交易搬到链上**。

机制是这样的。第一步，机构发出 **RFQ（Request for Quote）**，多个流动性供应商同时返回报价，机构选最优价格——这不是 AMM 的恒定乘积模型，而是传统金融熟悉的询价模式，滑点更可控。第二步，选定报价后通过智能合约做 **PvP（Payment vs Payment）原子结算**——双方资金由合约托管，要么同时交割、要么都不发生，消除了结算对手方风险。传统 FX 里这个风险有个专门的名字叫 Herstatt risk，1974 年就因为这个倒过一家银行。第三步，**24/7 运营**加可编程结算窗口和轧差，不受传统市场营业时间限制。而且是 **all-to-all 模型**——不需要和每个对手方签双边协议，所有通过 KYB/AML 审核的机构进同一个流动性池。

配套的 8 国 **Partner Stablecoins** 构成了实际的多法币网络：巴西 BRLA、韩国 KRW1、菲律宾 PHPC、澳大利亚 AUDF、墨西哥 MXNB、日本 JPYC、加拿大 QCAD、南非 ZARU。举个具体场景——一家巴西公司要付款给日本供应商，BRLA 通过 StableFX 原子兑换为 JPYC，几秒内链上结算完成，不用走代理银行、不用等 T+2。这就是 Circle 要构建的东西——**以 USDC 为中间结算层、以 Arc 为清算基础设施的链上多法币 FX 网络**。这也解释了为什么 Arc 对 Circle 是战略必须——这种深度整合在别人的链上做不到。

核心结构性优势仍然是 **CCTP V2**——26 个域、累计 1260 亿美金、年增 740%。USDC 在 Arc 上是**原生发行**，不是桥接资产，所以可以做 1:1 的 CCTP burn-and-mint。这个能力第三方链不可复制——你可以集成 CCTP，但你不可能是 USDC 的发行方。

测试网 2.44 亿笔交易、**100 多家机构参与**——BlackRock、Goldman Sachs、Mastercard、Visa、AWS、Anthropic、Coinbase、Aave、Uniswap 等。但注意状态标签是橙色——**主网尚未上线**，预期今年夏天。还有一个战略背景值得点出：GENIUS Act 签署后银行和金融科技公司可以合法发行稳定币了，这会侵蚀 Circle 的 USDC 护城河。Arc 的战略意义是让 Circle 从"依赖第三方链的发行方"升级为"**发行方加结算层的垂直整合**"——通过 StableFX、CPN 和 Partner Stablecoins 构建网络效应。

【右卡片】**Canton**——Daml 加 need-to-know 隐私的企业结算网络。Canton 和前面两个项目有本质区别——它不追求通用公链的叙事，而是专门为**多机构金融工作流**设计的。核心理念是：没有任何节点持有完整全局账本。每个参与方只持有与自身相关的合约投影，Synchronizer 负责加密消息排序和 2PC 协调但**看不到交易明文**。这不是 ZK 隐私，而是 sub-transaction projection 加 Merkle DAG blinding——每笔交易根据 Daml 合约角色自动裁剪为不同方有权看到的子交易视图。

先说一下 DTCC 是什么——Depository Trust & Clearing Corporation，美国证券存管信托与清算公司。不夸张地说，这是**全球金融市场的基础设施核心**。美国几乎所有的股票、债券、ETF 交易的清算和结算都经过 DTCC。规模有多大？2022 年 DTCC 子公司处理的证券交易总值是 **2.5 千万亿美金**（quadrillion），托管资产来自 150 多个国家、价值 72 万亿。SEC 监管、全球 20 个办公地点。当 DTCC 选择在某条链上做代币化，这不是一般的"机构合作"，这是传统金融结算体系的核心玩家在做技术路线选择。

标志性进展要更新一下——**DTCC 已经确认 7 月进入有限生产交易、10 月全面上线**，比之前说的"H1 受控 MVP"更具体了。去年 12 月 SEC 给了 DTCC 一封 no-action letter，允许其在区块链网络上持有和记录代币化股权和 RWA，有效期三年——这是监管层面的绿灯。他们用 ComposerX 平台把 DTC 托管的美国国债代币化，**50 多家机构**正在参与服务的定义——涵盖银行、资管、托管、交易所和数字资产基础设施提供商。IntellectEU 已经推出了 Canton 入驻工具包来简化 DTCC 试点参与流程——这说明生态已经开始围绕这个生产部署做配套了。

Broadridge DLR 的数据也在更新——Messari 报告显示月回购结算量超过 **8 万亿美金**，日均 3680 亿。Broadridge 同时还是 Global Synchronizer 的 Super Validator，兼具应用开发方和网络运营方双重角色。

**Global Synchronizer** 目前有 **13 个 Super Validators** 在运行——包括 Blockdaemon、Figment、Kiln、Everstake 等机构级基础设施提供商。Canton Coin 作为治理和激励代币。

其他机构信号也在加速。**J.P. Morgan 今年 1 月宣布在 Canton 上部署 JPM Coin**，做机构跨境结算。今年 2 月，一个由 DTCC、LSEG（伦敦证交所集团）、Euroclear、Citadel Securities、Tradeweb、Société Générale、Archax 组成的**行业工作组**完成了第四轮跨境日内回购交易测试——标的是代币化英国国债。HQLAX 获得了 Broadridge 和 Digital Asset 的战略少数股权投资，计划迁移到 Canton Network，但需要 CSSF（卢森堡监管机构）批准。

但要讲清楚局限性。第一，Daml 和 Scala/JVM 技术栈对非 Scala 团队的运维负担很重——这不是你用 Solidity 和 Hardhat 能上手的东西。第二，vendor 提供的数据口径不一致——Global Synchronizer 页面说每月代币化 2 万亿以上 RWA，Digital Asset 的页面说 1.5 万亿以上证券，这些都不是独立审计的链上统计。第三，大额名义金额不等于链上 TPS 和延迟性能——Canton 至今没有公开的性能基准。

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

最底层是 **CDP AgentKit**——模型无关的开发框架，50 多个 TypeScript Actions、30 多个 Python Actions，覆盖转账、兑换、NFT 铸造、智能合约部署。AgentKit 是开源的技能框架，和 CDP Server Wallets v2 以及 cb-mpc 密码学库一起构成了底层基座。

第二层是 **Agentic Wallets**——今年 2 月 11 号发布，专门为自主 AI Agent 设计的钱包基础设施。密钥用 MPC 安全飞地保护——Agent 永远不直接接触私钥。内置 Session Caps、per-transaction limits、白名单对手方，都在基础设施层强制执行。通过 Paymaster 在 Base 上实现无 Gas 交易。安装方式很简单——`npx awal` 或者 MCP server，直接兼容 Claude、Codex、Gemini。这个设计的关键是**机构和企业级的安全护栏**——花费限额、权限边界、审计轨迹都在钱包层面解决。

第三层是 **x402 协议**——这是整个 agentic economy 的支付管道。激活 HTTP 402 状态码做机器间微支付，把任何 API 端点变成机器可导航的付费墙——Agent 不需要注册账号、不需要信用卡、不需要订阅，直接在 HTTP 请求里用 USDC 结算，200 毫秒完成。最新数据很有说服力——**过去 30 天 x402 在 Base 上的交易量达到 310 万笔、价值转移 120 万美金**，卖方增长 23%、买方增长 37%。

x402 的联盟阵容值得关注。Coinbase 和 Cloudflare 在去年 9 月联合成立了 **x402 Foundation**，核心成员现在包括 **Google、Visa、AWS、Circle、Anthropic、Vercel**。传统金融也在接入——**Visa** 通过 TAP（Trusted Agent Protocol）支持 x402，用 PKI 身份层区分合法 AI Agent 和恶意 bot。**Stripe** 通过 ACP（Agent Commerce Protocol）集成 x402，连接传统支付轨道。**Cloudflare** 在 Workers 平台集成了 x402，还在试点按爬取付费产品。**Amazon Bedrock AgentCore Payments** 5 月 7 号上线预览——AWS、Coinbase、Stripe 三方合作，让 AI Agent 在 Bedrock 里直接用 USDC 通过 x402 付费。这意味着 x402 不只是 crypto 标准——它正在被定位为 agentic economy 的基础管道。

最上层是 **Base MCP**——5 月 26 号发布，基于 Anthropic 的 MCP 标准，让 AI Agent 直接连接用户的 Base 账户执行链上操作。首发集成 Morpho、Moonwell、Aerodrome、Uniswap、Avantis、Bankr、Virtuals 七个 DeFi 协议插件。用户在 Claude、ChatGPT、Cursor 等 AI 界面里用自然语言就能发起链上交易。MCP 定义了 AI 模型如何与外部工具交互，x402 提供支付层——开发者在搭建带 x402 付费墙的 MCP 服务器，让 AI 模型自主为工具调用、数据获取和计算资源付费。

底部的基础设施支撑层包括 Flashblocks 200 毫秒预确认、Smart Wallet 的 ERC-4337 加 ERC-7715 权限体系、以及 Aerodrome DEX 峰值 TVL 超 10 亿。

Agent 生态方面——看右边的表格。生态已经覆盖多个品类。**Venice** 做推理付费，**BlockRunAI（Base Batches）** 让 Agent 跨 50 多个 AI 模型按调用付费、USDC 结算。**Browserbase** 让 Agent 用 USDC 付费获取云浏览器会话——Agent 可以用浏览器导航网站、收集上下文、运行工作流。**Exa** 做 web 搜索和内容数据。**Wolfram Alpha** 做计算。甚至旅行领域也有——**Tripadvisor、FlightAware、Amadeus** 提供旅行相关工作流。Social 类的 Clanker 在 Farcaster 上自动发币，累计协议费用超过 5000 万美金，交易者 55.8 万。Virtuals Protocol 部署了超过 1.8 万个 Agent，年协议收入在 Base 排第二——超过 5900 万美金。

**一个值得关注的新方向——Agent 从消费者变成赚钱者**。Base 认为下一阶段不只是 Agent 花钱，而是 Agent 赚钱——卖研究、运营付费服务、雇佣其他 Agent、自己支付运营成本。早期案例已经出现：**Felix** 是一个基于 OpenClaw 框架的 AI Agent，部署在 Base 上，几周内创造了超过 **26 万美金营收**——来源包括 PDF 销售、技能市场、定制服务。运营成本只有每月约 1500 美金（Claude Pro Max + Codex Max + 托管费）。这意味着 AI Agent 可能成为一种新的链上经济主体——不只是执行工具，而是自主运营的"一人公司"。

**关键洞察**：Base AgentFi 生态的核心竞争力不是单个协议，而是 **Coinbase 分发加四层垂直整合加顶级联盟（Google/Visa/AWS/Stripe/Anthropic）** 的组合效应。开发者用 `npm create onchain-agent@latest` 就能获得钱包、DeFi、支付、AI 接口全套能力。x402 310 万笔/月的真实交易量、Visa/Stripe/AWS 的接入，说明这不只是 crypto 叙事——传统互联网基础设施正在把 Base 当作 Agent 经济的结算层。Mantle 在六维上全部需要从零补建，差异化壁垒有限。

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

Payment Lane 是 Tempo 的核心差异化——架构图上用绿色高亮标注的部分。这个设计值得展开讲，因为它和我们熟悉的所有区块链处理交易的方式都不一样。

以太坊和所有 L2 的 blockspace 是**无差别的**——一个区块就是一个 gas 池子，NFT mint、DeFi 清算、稳定币转账全部在同一个池子里竞争。一次热门 NFT 发售就能让支付交易的 gas 费飙升 100 倍。Tempo 的做法是**在协议层把 blockspace 物理隔离**成三个区：System Lane、Payment Lane 和 General Lane。

具体数字是这样的。总区块 gas 上限 500M。其中 `shared_gas_limit` 是总量的 10%（50M），预留给系统交易和支付交易的共享池。General Lane 被 `general_gas_limit` 硬限制在 **30M gas**——不到总容量的 6%。剩下的 **420M+ gas 全部保证给支付交易**。这意味着即使 General Lane 被 DeFi 交易完全塞满，支付交易仍然有超过 84% 的 blockspace 可用。反过来，General Lane 满了不会影响支付交易的吞吐——这就是所谓的 **anti-noisy-neighbor guarantee**。

那怎么判断一笔交易是"支付"还是"通用"？这里有一个**双层分类机制**的设计。

**V1（共识层强制执行）**：看交易的 `to` 地址是否以 `0x20C0` 前缀开头——这是 TIP-20 支付 token 的固定地址前缀。检查是**无状态的**——不需要读取任何链上存储，纯粹基于地址格式判断。这避免了状态访问带来的侧信道攻击。对于 AA（Account Abstraction）交易，要求 `calls` 向量里的**所有**调用都指向 TIP-20 前缀地址才算支付交易。

**V2（TIP-1045，构建器层强制执行）**：在 V1 的基础上收紧了三个维度。第一，calldata 必须匹配**函数选择器白名单**——只有 transfer、transferWithMemo 等真正的支付操作才能进 Payment Lane，防止恶意构造的 calldata 占用支付 blockspace。第二，access list 和 authorization list **必须为空**——进一步隔离支付交易的执行环境。第三，AA 交易的密钥授权必须是有界的。V2 目前在交易池和 payload builder 层面执行，未来计划通过硬分叉提升到共识层。

区块的构建顺序也是确定性的：先执行 System Lane 的系统交易（奖励注册表更新、验证者配置），然后处理 Payment Lane 的支付交易，再处理 General Lane 的通用交易，最后运行区块末尾的系统交易（结算 DEX 和 Fee AMM）。支付交易在区块内有**确定性的位置**，不会被任意用户活动重排序。

这个设计的本质是：**Tempo 不是在应用层做支付优化，而是在共识层和区块构建层把支付当作一等公民。** blockspace 隔离、无状态分类、确定性排序——这三个加在一起，让支付交易获得了接近传统支付网络的可预测性保证。这是通用链加个支付合约做不到的。

往下是 **TIP-20 预编译 Token**——不是普通的 ERC-20 合约，而是协议级 token 标准。固定 6 位精度、原生 memo 字段用于支付对账、pause/role-based 权限、fee eligibility、直接集成 Payment Lane。稳定币 Gas 以 attodollars 计价，一笔 TIP-20 转账约 0.001 美元——无需持有原生代币。

底层是 **Reth EVM 执行层**加 **Commonware Simplex BFT** 共识——目标 500 到 600 毫秒确定性终局，双进程隔离设计降低执行负载对共识路径的影响。

最下面是 **Enterprise Zones**——这个设计也值得展开，因为它代表了一种"公链+私有执行环境"的混合架构思路。

Zones 在架构上是 **Validium**——连接到 Tempo L1 的平行私有链。L1 只存状态承诺（state commitment），不存交易数据。每个 Zone 由一个 operator（可以是企业自身或基础设施提供商）运行，operator 控制准入和交易处理。关键的信任模型是：**operator 能看到 Zone 内所有交易明文，但不能控制用户资产**——资金锁定在 L1 的 Zone 合约里，只有资产所有者能提取。Zone 内的用户只能看到自己的交易和余额，其他人只能看到加密的状态证明。

隐私是多层设计的。**存款用 ECIES 加密**——secp256k1 ECDH 加 AES-256-GCM，明文格式固定 64 字节（地址 20 + memo 32 + padding 12），固定长度防止通过密文大小推断交易类型。**RPC 是认证制的**——每个账户用签名 token 做访问控制，只能查询自己的数据。**区块对外脱敏**——transactions 数组清空、logsBloom 置零。甚至 **gas 也是固定的**——每笔用户 TIP-20 操作固定消耗 100,000 gas，防止通过 gas 差异做侧信道分析。**RPC 响应有 100ms 最低延迟**——防止通过响应时间推断状态。这些加在一起构成了一个相当完整的隐私防护体系。

共识模型很简单——**没有独立共识**。Zone 和 Tempo L1 是 1:1 的区块映射，每个 L1 区块产生一个对应的 Zone 区块，head = safe = finalized，直接继承 L1 的终局性。没有 P2P 网络、没有对等节点、没有共识协商——sequencer 是唯一的区块生产者，完全由 L1 事件驱动。L1 合规策略（TIP-403 白名单/黑名单）实时镜像到 Zone 内。

目标场景是**企业内部的机密支付工作流**——工资发放、财库管理、代币化存款结算。Tempo 目前在和一小批设计伙伴合作构建这些场景。但有几个重要限制。第一，**CREATE 和 CREATE2 被禁用了**——Zone 内不能部署自定义智能合约，只能用预编译的 TIP-20 操作。这让供应链金融、复杂 DeFi 这些需要自定义逻辑的场景无法实现。第二，**单 sequencer 意味着跨企业协作行不通**——多方信任场景下，由一方控制 sequencer 破坏了信任对称性。

最关键的风险我们在 Slide 11 提过——**validity proof 还没实现**。我们看了代码，`batch.rs` 里 `verifierConfig` 和 `proof` 字段都是空字节，有一行 TODO 注释说"等 proof generation 实现后再传入真实的 proof bytes"。precompile 代码已经做了 `no_std` 适配，兼容 SP1 RISC-V，说明他们在为 ZK 证明做准备，但实际的证明生成逻辑、L1 验证合约都还不存在。**当前的安全模型完全依赖对 sequencer 的信任**——等同于早期没有欺诈证明的 Optimistic Rollup。

行业内对 Zones 也有争议。Tempo 把它定位为"**privacy, not secrecy**"——合规审计方可以获得特殊访问密钥。但批评者指出，operator 能看到全部数据、能冻结和暂停用户操作——这更像是一个交易所，而不是一个 trust-minimized 的区块链。Zama 的高管直接评论说这"本质上是 operator 管理的私有链，缺乏密码学保证，携带类中心化风险"。这个争论的走向——公链加私有执行环境的混合模式 vs 密码学优先的纯隐私方案——会影响整个企业区块链的架构方向。

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

Prividium 的核心是一条**许可制 Validium 链**。先解释一下 Validium 和标准 ZK Rollup 的区别——zkSync Era 是 ZK Rollup，交易数据发布到以太坊 L1（calldata 或 blob），任何人都可以重建状态。Prividium 是 Validium，**交易数据留在运营方的私有数据库里**，L1 只存状态根和 STARK 证明。ZK 证明保证状态转换的正确性是一样的，但数据可用性从以太坊保证降级为运营方保证。在 DeFi 场景下这不可接受——用户需要无许可逃生。但在机构场景下这恰好是设计特性——银行运营自己的 Prividium 链，数据可用性由自身 IT 基础设施保证，不存在信任第三方的问题。而且监管法规（GDPR、银行保密法）**反而要求**交易数据不得无限制公开。

大家看这张端到端结算路径图，从上往下走。

机构用户通过 **IdP** 认证——Keycloak、Okta OIDC 或 SIWE，一个用户可以绑定多个钱包并继承同一角色权限。然后进入 **Proxy RPC Gateway**——这是整个网络的**唯一入口**，做三步验证：JWT token 验证、钱包地址匹配、**合约函数级权限检查**。注意是函数级——不是"能不能访问这个合约"，而是"能不能调用这个合约的这个函数、带什么参数"。未授权请求返回 401/403 并记入审计日志。标准 RPC 端点必须保持私有，只有 Proxy RPC 对外暴露。

通过网关后到 **Sequencer 私有执行**——数据存在 PostgreSQL 加 Blob Store 的私有子网里，不暴露到互联网。Sequencer 能看到所有交易明文，但不能伪造状态转换——因为最终要过 ZK 证明。再到 **Prover**——用 **Airbender GPU** 生成 STARK 证明。Airbender 是 zkSync 新一代开源 RISC-V 证明系统，替代了之前的 Boojum，声称支持商用 GPU 运行、亚秒级出块证明、每笔交易证明成本约 $0.0001。通过 **ZKsync Gateway** 聚合多链证明后提交到以太坊 L1。

注意架构图上那条绿色信任边界虚线——L1 只能看到状态根和 STARK 证明，**零交易数据泄露**。这不是额外功能，是 Validium 架构的固有特性。

看左边的四层准入控制侧栏。第一层身份认证——Okta SSO 或 SIWE 或多钱包支持。第二层 Proxy RPC 网关——三步验证加审计日志。第三层 **RBAC 权限**——通过 Admin Dashboard 管理用户、角色、权限，**合约函数级粒度加可选参数限制**，不用改代码。这和应用层白名单有本质区别——它在 RPC/网关层面运作，无法通过桥接、强制包含、sequencer 排序、multicall 或跨链消息绕过。第四层 **L1 TransactionFilterer**——这个很关键，它是部署在以太坊 L1 上的合约，过滤通过强制交易路径（绕过 Proxy RPC）提交的交易。白名单地址可以不受限制，非白名单地址只能做 ETH/ERC-20 转账——合约部署和任意函数调用被禁止。这堵住了用户绕过准入控制直接走 L1 强制包含的漏洞。

开发环境已经开源——`local-prividium` 用 Docker Compose 一键起全套：Prividium API、Keycloak、Admin Panel、zkSync OS、Sequencer、Prover、Block Explorer、Prometheus/Grafana，还有一个可选的机构回购借贷 demo 应用。配套的 `zksync-sso` 仓库提供 ERC-7579 模块化智能账户、Passkeys、Sessions、Paymaster 集成和账户恢复。

机构采用信号需要重点说一下。**Cari Network** 是最具体的案例——由美国第 27 任货币监理署署长 Gene Ludwig 创建，今年 3 月 16 号宣布选择 Prividium 作为技术基座。联合的 5 家美国区域银行现在有名字了——**Huntington Bancshares、First Horizon、M&T Bank、KeyCorp、Old National Bancorp**，合计存款超 6000 亿美金，目标今年 Q3 试点。他们要做的是**代币化存款**——在功能上像稳定币一样快速可转移，但保留银行直接负债的法律地位和 FDIC 保险资格，资金留在受监管的美国银行体系内。这个定位很明确——用银行存款代币对抗稳定币的冲击，特别是在 GENIUS Act 签署后银行面临的存款流失压力。美国银行家协会（ABA）已经支持在 Cari Network 上测试发行、转账和赎回流程。中型银行联盟（Mid-Size Bank Coalition of America）也表态支持。

**Deutsche Bank** 通过 **Project DAMA** 参与——用 Prividium 技术栈做了一个多托管人基金发行，原本需要几个月的流程在几天内完成。**BitGo** 提供机构级托管整合。Citi 和 Mastercard 也有接触。此外还有主权级项目——**阿联酋 ADI Chain** 在用 Prividium 架构。UBS 在 zkSync validium 上测试了代币化黄金。

zkSync 官方声称"35 家以上金融机构验证了 Prividium 架构"。需要说明的是——这个数字来自 zkSync 官网，**不是每家机构单独公告确认的**，我们研究中将其标记为 vendor-claimed。但 Cari Network 的 5 家银行、Deutsche Bank、BitGo、Citi、Mastercard 这些都有独立的公开信息源。

**核心信息**：Prividium 的价值核心是合规和准入控制，不是 ZK 证明本身。合规 RPC 加 RBAC 加审计加 L1 TransactionFilterer 已经解决了机构最关心的问题。ZK 证明提供的是锦上添花的密码学保证——即使运营方作恶也不能伪造状态转换。而 Validium 架构把隐私从"可选功能"变成了"默认特性"——不用额外做任何事，L1 观察者天然看不到任何交易数据。

---

## Slide 21 — 案例：Canton — "Need-to-Know" 机构工作流网络

【看上部架构图 `charts/slide21-canton-arch.png`】

Canton 代表了完全不同的范式。我先说一个核心概念帮助大家理解——Canton 的目标是构建一个"**虚拟全局账本（Virtual Global Ledger）**"。听起来矛盾——既是全局的，又是虚拟的？意思是：从使用体验上，它表现得像一个统一的全局账本，跨机构的资产可以原子化交易；但实际上**没有任何地方存在这个完整的账本**——每个参与方只持有与自己相关的那一片。

大家看这张参与者模型图。

四层结构。最上层是 **Application Layer**——DvP、回购、抵押品、债券这些金融工作流。

第二层是 **Participant Layer**——每个参与方运营自己的 **Participant Node**，维护自己的 **Local ACS（Active Contract Set）**。图上用不同颜色标注了三个参与方：蓝色的 Alice Bank、橙色的 Bob Fund、紫色的 Regulator。关键标注——"Only sees own contracts"。**没有任何节点持有完整的 ACS——这是分布式的、按 Party 投影的模型，不是复制的全局账本**。

这和我们熟悉的所有区块链有本质区别。以太坊、zkSync、Mantle——每个全节点都持有完整状态，所有数据对所有节点可见。Canton 反过来——**数据永远不离开有权看到它的节点**。如果你不是一笔交易的参与方，数据物理上不会到达你的节点。这消除了公链上即使用假名也会泄露的竞争情报问题——竞争对手无法从交易模式推断你的业务流。

第三层是 **Synchronizer**——这个名字就说明了它的角色，不是"执行者"而是"协调者"。Canton 把合约执行和交易排序**彻底解耦**了。

用一个直觉化的比喻来解释。想象一个密封信拍卖——**Sequencer** 是邮局，只负责给密封的信封盖时间戳和编号，保证大家收到信的顺序一致，但邮局**拆不开信封**——它看到的只是加密后的 payload、接收者地址、消息大小和时间戳。**Mediator** 是公证人——收集所有参与方的投票（同意或拒绝），在截止时间前出具裁决。公证人也**看不到信的内容**——它只知道谁需要签字、谁签了、谁没签。**Participant Node** 是参与方自己——只有收信人能拆开自己那份信，运行 Daml 代码验证交易是否合法，然后投票。

这和 Prividium 的信任模型有本质区别。Prividium 的运营方（Sequencer）可见全部数据，隐私保证是"对 L1 外部观察者"的。而 Canton 是**对 Synchronizer 运营方也隐私**。如果 Sequencer 被攻破，攻击者能延迟或审查消息、观察流量模式，但**不能解密合约内容、不能伪造参与方签名、不能单方面批准无效交易**。

但这也带来了一个 Prividium 没有的风险——**数据泄露是高风险的**。在以太坊上数据泄露不存在（因为本来就是公开的），但 Canton 上每个 Participant Node 持有未加密的私有合约数据和私钥。如果一家银行的 Participant Node 被攻破，攻击者获得的不只是密钥，还有这家银行签过的所有私有合约的完整历史记录。所以机构级的 HSM、密钥管理和多签是必须的。

**域（Domain）** 的概念也需要解释。Canton 不是一条链——它是一个**链的网络**。不同的实体可以运营不同的域：Goldman Sachs 可以运营自己的私有域用于内部跨分支交易；一组银行可以共同运营一个回购市场域；证券交易所可以把域作为市场基础设施；央行可以运营 CBDC 域。每个域定义自己的规则（谁能加入）、排序（解决冲突）和连通性（路由加密消息）。

最底层是 **Global Synchronizer**——13 个 Super Validators 运行，包括 Goldman Sachs、HSBC、BNP Paribas、Visa、Circle、Chainlink 等——**一半华尔街、一半 crypto 基础设施**。Global Synchronizer 提供三个共享服务：身份目录（相当于一个共享的通讯录，用于地址发现和证书验证）、BFT 共识排序（超过 2/3 诚实就安全）、和跨域协调（确保跨域交易的最终时间戳和正确性证明）。

**跨域原子交易**是 Canton 最有意思的能力——用一个具体场景来说。Bank A 想用央行域上的现金买黄金域上的黄金。Bank A 的 Participant Node 同时连接两个域。它先向现金域发起 transfer-out 锁定现金，现金域返回一个签名的排序证明。然后 Bank A 拿着这个证明去黄金域发起 transfer-in，黄金域验证证明后让黄金出现在 Bank A 的 ACS 里。**关键隐私保证**：央行看到 Bank A 花了现金，但看不到是用来买黄金的；黄金域看到黄金转移了，但看不到付款账户和金额。这和公链上的跨链桥有本质区别——Canton 做的是"**拓扑迁移**"，资产的账本登记从一个域物理迁移到另一个域，而不是锁定原资产铸造一个包装版本。

但这里有一个 Flashbots 社区讨论中提出的尖锐问题值得说一下——**如果 Participant Node 在 transfer-out 之后、transfer-in 之前崩溃了怎么办？** 现金域已经归档了资产，黄金域什么都没收到，证明卡在死掉的节点内存里。Canton 的回答是：证明持久化在现金域 Sequencer 的日志里，节点重启后可以恢复证明并完成 transfer-in。但在节点恢复之前，资产确实处于一个**悬空状态**——现金域花掉了，黄金域没到。这本质上是经典的 2PC 协调者崩溃问题。Canton 不会丢失资产（证明在日志里），但**在节点恢复前资产不可用**——所以跨域原子性严格来说是"最终原子"而不是"即时原子"。

**终局性模型**也值得说一下。Canton 的终局性是**确定性的**——一旦 Mediator 出具 Commit 裁决，交易就是最终的，永远不会被重组。不像以太坊需要等区块确认深度。流程分三步：Sequencer 分配序列号（排序完成但未最终确认）→ Participant Nodes 验证并投票 → Mediator 出具裁决（全票同意就 Commit，否则 Rollback）。延迟通常 1 到 2 秒。

看右边的 DvP 可视性矩阵——一笔 DvP 交易中：Alice 看到自己的资产转移加必要对手方输出，看不到其他客户合约。Bob 同理。Bank 只看到自行发行资产的转移投影，看不到交易原因和对手方细节。监管方只看到被**显式建模为 observer** 的合约——这是在 Daml 合约定义时就确定的，不是事后附加的权限。

**Daml 合约模型**和 Solidity 是两种完全不同的范式——如果说 Solidity 像面向对象编程，Daml 更像函数式编程（它实际上基于 Haskell）。Solidity 是账户模型——一个巨大的全局状态被函数更新；Daml 是合约模型——更接近比特币的 UTXO，合约被创建和消费，不可变。Solidity 默认公开——所有人看到所有数据；Daml 默认私有——只有 signatory 和 observer 能看到。Solidity 的每个节点执行每笔交易；Daml 只有相关方的节点执行。Solidity 常见重入攻击和整数溢出；Daml 通过设计消除了大部分常见智能合约漏洞。

具体来说：**signatory** 代表义务和责任——创建合约必须获得 signatory 授权，义务不能在未授权下施加。**observer** 用于监管审计——可见合约但不必授权创建。**choice** 是合约上可执行的操作。**consume-create 模式**是核心——合约不可变，"修改"是 archive old + create new，天然生成完整审计轨迹。Daml 没有 gas 概念——交易受限于域的 Decision Time（通常 60-120 秒），标准金融交易的实际解释时间在 100 毫秒以内。

机构生产验证——这是 Canton 最强的地方，而且信号在加速。

**Broadridge DLR** 是最大的生产案例——日均 3680 亿美金、月近 8 万亿回购结算。RWA.xyz 显示 Canton 上代表的资产价值 **3448 亿美金**，其中 Broadridge DLR 占绝大部分。DLR 把回购交易从手工双边流程变成了原子化同日结算。Broadridge 同时是 Global Synchronizer 的 Super Validator。

**Goldman Sachs GS DAP** 做多资产代币化发行和结算，包括为欧洲投资银行（EIB）发行的标志性数字绿色债券。声称结算从 T+5 缩短到 60 秒以内。Goldman 还领投了 Digital Asset（Canton 背后公司）的 D 轮融资，累计投资超过 1.35 亿美金——既是用户又是投资者。但需要注意，GS DAP 的具体生产规模公开数据有限，而且它可能使用的是 Daml 软件加私有许可基础设施，不一定全部跑在 public Canton Network 上。

**HSBC Orion** 做数字债券生命周期——完成了 4 支数字债券，结算从 T+5 改善到 T+1。HSBC 也在 2026 年开始在 Canton 上试点代币化存款。同样的区分适用——需要区分 Orion 是在 Canton 公共网络还是私有 Daml 基础设施上。

**DTCC ComposerX** 做 DTC 托管的美国国债代币化，7 月有限生产、10 月全面上线。这个在 Slide 11 详细讲过了。

还有一个新信号——今年 2 月，DTCC、LSEG、Euroclear、Citadel Securities、Tradeweb、Société Générale、Archax 组成的行业工作组完成了**第四轮跨境日内回购交易测试**——标的是代币化英国国债，使用 Daml 合约做原子化 DvP。这意味着 Canton 不只是美国市场，欧洲的证券基础设施也在参与。

但最后必须讲清楚 Canton 的局限性。第一，**跨 Synchronizer 资产转移是非原子的**——在 source 域 unassignment 成功后、target 域 assignment 完成前，合约处于 pending 状态不可使用。这不能被表述为"跨链桥式原子结算"。第二，**Daml 和 Scala/JVM 技术栈门槛很高**——Scala、sbt、Pekko/cats、PostgreSQL、Flyway、Daml-LF 的组合对非 Scala 团队运维负担很重，这不是 Solidity 加 Hardhat 能上手的东西。第三，**没有独立的性能基准**——vendor 提供的数据口径不一致（$2T+ vs $1.5T+ vs $6T），大额名义金额不等于链上 TPS 和延迟性能。

**Canton 告诉我们一件事**：机构采用需要的是工作流级别的设计——谁能看什么、怎么授权、怎么审计、怎么跨机构结算，不是给通用链加几个 enterprise feature。Canton 的生产验证深度（Broadridge 月 8 万亿、DTCC 10 月上线、Goldman 和 HSBC 在用）是目前所有企业区块链中最强的——但代价是完全独立于 EVM 生态的技术栈。

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

## Slide 24 — 行业动态：币安美股不是链上股票，而是 RWA 合规入口战

在进入结论之前，插一页行业动态。币安 6 月 1 号上线了美股交易，这是本周最大的行业事件，跟我们讨论的 RWA 和机构金融方向直接相关。

先讲核心判断：**币安这次上线的"Stocks"不是链上代币化股票，而是一个嵌入币安前端的传统美股经纪服务**。看左边这张路径图——用户在 Binance 下单，订单经过 Nest Trading 这个 ADGM 持牌实体做 introducing broker，最终由 Alpaca Securities 执行、清算、结算和托管。Alpaca 是美国 FINRA 和 SIPC 成员。关键是，证券交易和持有本身不发生在链上，底层仍是传统券商基础设施。

注意下面虚线区的 bStocks——这才是币安预告的代币化证券产品，由 BTECH Holdings Ltd 发行，但**尚待 FSRA 监管批准，不是当前已上线的东西**。社区容易把这两个混为一谈，我们要区分清楚。

右边这张对比表只留了四个维度。

**资产本质**：传统券商和币安对应的都是美国上市股票/ETF 的权益，只是入口和主体链路不同；xStocks 和 Ondo 拿到的是链上 token，代表经济敞口但通常没有投票权和现金分红。

**用户价值**：币安的优势是加密用户不用离开 Binance 前端，7000 多只标的，5 美金起投——但仍然会进入证券账户和合规条款链路，KYC、W-8BEN、税务居民身份这些要求，仍然可能出现在开户和交易条款里。

**成本摩擦**：币安号称零佣金，但有 10 个基点的 trading spread 加上每笔最低 0.35 美金；如果用 USDT 或 BNB 下单，还有一层稳定币兑换价差。对常规时段的高流动性标的，币安这条路径大概率不比直接券商入口便宜，小额单尤其明显。另外，NVDA 盘前有一个单点样本显示 Binance 价差明显偏宽，但这个只能当早期风险信号，不能当长期平均结论。

**核心风险**：用户需要同时理解 Binance 前端、Nest 证券主体和 Alpaca 执行托管之间的边界，争议处理和投资者保护范围会比直接券商入口更复杂。

看底部这条结论。这件事对我们的启示是什么？行业共识确实在 RWA 和机构金融方向，但你看币安怎么做的——用的是 Alpaca 传统券商基础设施，走的是合规包装加中心化分发的路径，**不是链上原生能力**。这恰恰说明：如果 Mantle 要做差异化，不能只讲"资产上链"，而是要讲链上原生的隐私、合规工作流和机构级结算能力——这就是我们前面花了整个 Chapter 3 评估 Prividium、Canton、Paladin 要解决的问题。

---

## Slide 25 — 结论与下一步

总结三个核心发现。

一，**L2 赛道已进入差异化定位阶段**。头部 L2 各有不可复制的结构性护城河——Base 分发、Arbitrum 金融工具链、Optimism Superchain、zkSync ZK 加企业隐私。L1 通用链和垂直链同时压缩空间。Mantle 必须选择方向。

二，**三个候选方向各有机会与风险**。AgentFi 早期但 Base 先发优势极强。Payment Chain 增长快但原生竞争者已从架构层占位。机构金融增长最快且竞争窗口仍在，但需要从零构建合规技术栈。

三，**方向之间不是互斥的**。Agent 财库管理和 B2B 支付结算都可以作为更大叙事的子场景。关键是确定主叙事锚点，然后让其他方向围绕它展开。

需要团队讨论的问题：Mantle 的主叙事锚点应该放在哪个方向？op-geth EOL 迁移路径如何选择？是否有资源和意愿探索合规隐私基础设施？

以上就是今天的分享。接下来进入 Q&A。

---

## Slide 26 — Q&A

【准备回答方向】

- **技术栈时间线和资源**：合规 RPC 和身份注册是最轻量的，可以 3 个月内做出 MVP。重的部分是 Validium DA，至少 9-18 个月。
- **与 Prividium 的差异化**：我们有国库（40 亿+）、DeFi 收益生态（mETH/cmETH）和 MI4/Securitize 基础。Prividium 没有开放 DeFi 组合性。
- **合规方案选型**：KYC 层面可以集成现有 zkKYC 方案。合规策略引擎参考 ERC-3643/T-REX 体系。
- **支付子场景如何嵌入**：机构金融的 B2B 结算本质上就是支付。Paymaster 加 Payment Intent SDK 加商户财库是第一个落地点。
- **为什么不赌 AgentFi**：短期热度不等于长期壁垒。Base 有 Coinbase 分发，Solana 有性能优势——我们在这个赛道没有结构性护城河。
- **Canton 设计思想如何借鉴**：三个方向——Regulatory Observer 角色（合约级 observer role，监管方获可审计视图）；Sequencer/Mediator 职责分离（可引入独立 compliance service）；ACS Commitment（企业 Zone 可验证状态摘要，供多方 reconciliation）。是概念借鉴，不是技术栈迁移。
- **Paladin 的 Besu 替换可行性**：Layer A 的 Besu 可以直接换成 geth/op-geth，因为 Paladin 只用标准 JSON-RPC 17 个方法，无 Besu 专有 API 依赖。Layer C 的 Pente ephemeral EVM 替换成本更高——需要重实现 PenteDomain、evm_runner 和 statedb 适配层。如果选 geth 做 ephemeral EVM，需解决 vm.StateDB 接口和 trie/snapshot 的隐含耦合；如果选 revm，需要通过 CGO 做 Rust-Go 桥接。估计 3-6 个月工程量。Noto 和 Zeto 不依赖 Layer C，可以先行。
