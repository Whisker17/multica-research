# 币安美股功能研究报告

报告日期：2026-06-02（Asia/Shanghai）

## 0. 结论先行

币安这次上线的“美股”首先不是链上股票代币，而是一个嵌入币安前端的传统美股经纪服务：用户在币安下单，Nest Trading / Nest Exchange 相关 ADGM 实体承接证券业务，订单再路由给 Alpaca Securities LLC，由 Alpaca 负责执行、清算、结算和托管。官方明确说 Binance 不处理也不托管用户证券；用户持有的是美国上市股票/ETF 的直接经济权益，可获得适用的分红和公司行动处理。这个产品应与后续拟推出的 bStocks 区分开来。

从用户体验看，币安的优势是用稳定币或 BNB 进入美股，统一账户、最低 5 美元、7000+ 股票和 ETF、部分股票 24/5、后续可能接入证券借贷和 tokenization；短板是交易成本并不等于传统券商的“零成本”。币安官方费率为 0.10% trading spread，且每笔最低 0.35 美元，低于 350 美元时有效费率高于 0.10%；若用 USDT、BNB、USD1、U/USDU 等非 USDC 资产，还会有加密货币兑换的市场价差。

和链上 xStocks / Ondo 这类 tokenized stocks 相比，币安当前“直接美股”更像传统券商入口，资产数量和合规路径更接近 TradFi；xStocks/Ondo 更强调链上可转移、自托管、DeFi 可组合性，但通常不赋予股东投票权、现金分红权或对底层公司的直接股权主张，且依赖发行人/SPV、托管、预言机/做市、智能合约与跨司法辖区限制。

关于价差：币安官方已经把 10 bps trading spread 写进费率表，因此对于大部分流动性很好的美股，币安用户的“可见/不可见总摩擦”大概率高于直接接入传统券商的正常时段交易。0xAA 的 NVDA 盘前截图显示币安某时点买卖价差约 4.24%，富途约 0.014%；这是一个强烈的早期异常样本，但还不足以证明长期平均价差。可确认的是，盘前/盘后和 24h 交易本来就更容易出现宽价差，币安早期流动性接入也可能尚未稳定。

关于 CRS：不要把“用 USDT 买股票”理解成不会触发税务信息交换。币安直接美股涉及证券账户、经纪商/托管商和税务居民身份信息，若账户持有人属于 CRS 可报告对象，且相关实体位于 CRS 参与司法辖区或承担报告金融机构义务，就可能触发 CRS/AEOI 报告；美国券商本身还会按美国非居民税务规则收集 W-8BEN 并对美国源分红做扣缴/1042-S 报告。链上 tokenized stocks 未来还可能被 CARF 或 CRS 2.0 这类框架覆盖。具体到个人是否被报送，取决于税务居民身份、开户主体、产品条款和当地执行细则，需要税务专业意见。

## 1. 三类产品的本质区别

| 维度 | 传统美股券商 | 币安当前“Stocks / Direct Equities” | xStocks / Ondo 等链上 tokenized stocks |
| --- | --- | --- | --- |
| 资产本质 | 通过券商持有美国上市股票/ETF，通常是街名持有下的受益权益 | 仍是美国上市股票/ETF，由 Alpaca 执行/清算/托管，币安做前端和账户体验 | 链上 token，代表底层股票/ETF 的经济敞口，通常由 SPV/发行人持有或安排底层资产 |
| 是否链上 | 否 | 当前产品否；bStocks 是后续待批的 tokenized securities | 是，支持钱包转移、DEX/DeFi 集成 |
| 股东权利 | 通常可通过券商处理投票、分红、公司行动 | 官方称有直接所有权、适用分红与公司行动；具体权利以证券条款和券商安排为准 | 通常没有股东投票权、现金分红或对底层公司直接权利；分红多用 rebasing / total-return 方式体现 |
| 交易时间 | 常规盘 9:30-16:00 ET，部分券商支持盘前盘后/overnight | 官方称最多 24/5，且只有部分股票支持 24h | Kraken xStocks：部分 24/7，其他 24/5；链上二级市场可 24/7；Ondo 通常 24/5 |
| 结算 | 美国证券已于 2024-05-28 进入 T+1 标准结算周期 | 底层 Alpaca 执行、清算、结算和托管 | 链上转移即时/近即时，但发行/赎回、底层再平衡和市场做市仍受传统市场与发行人机制影响 |
| 核心风险 | 市场风险、券商/托管风险、订单执行、税务 | 传统券商风险 + 币安/Nest/Alpaca 分层 + 稳定币兑换和平台价差 | 市场风险 + 发行人/SPV/托管/智能合约/跨链/二级市场流动性/监管限制 |

## 2. 币安当前美股的实现路径

官方信息拼出来的路径是：

1. 用户在 Binance 股票入口发起订单，资产主要用 USDC；USDT、BNB、USD1、U/USDU 等会在下单时转换。
2. 官方公告称 Nest Trading Limited 作为 introducing broker，把证券订单路由给 Alpaca。
3. Alpaca Securities LLC 负责执行、清算、结算和托管。
4. Binance 官方免责声明写明 Binance 不处理或托管证券。

这解释了为什么社区说“币安 + Nest + Alpaca”的分层模式基本成立。BitHappy 的推文把它概括为币安前端、Nest 证券经纪主体、Alpaca 清算托管；Phyrex 的长文进一步强调 ADGM 牌照分层。官方材料能支持大方向：Binance ADGM 实体受 FSRA 监管，Nest Trading 被列有 Dealing in Investments as Agent/Principal、Arranging Deals、Arranging Custody、Providing Money Services 等活动；Alpaca 官方也说明其证券经纪服务由 Alpaca Securities LLC 提供，且是 FINRA/SIPC 成员。

需要注意一个文档细节：Binance landing page 和新闻稿强调 Nest Trading Limited 是 introducing broker；Binance fee page 末尾有一句写“Stock trading services are provided by Nest Exchange Limited”。这可能是官方文案的主体表述不一致。做严肃合规判断时，应以最终用户签署的 Securities Trading Product Terms、开户文件和适用地区披露为准。

## 3. bStocks 与当前美股不是同一个东西

Binance 在 2026-06-01 的公告里同时预告 bStocks，但它尚未等同于已上线的直接美股交易。官方披露要点是：

- bStocks 将由 BTECH Holdings Ltd 这个 ADGM SPV 发行。
- 上线需取得 FSRA 监管批准。
- bStocks 不是股票或股份，不让持有人直接拥有底层上市公司的股票。
- 官方把 bStocks 分类为代表某些金融工具的 Certificates。
- 不向美国或美国人士提供。

因此，当前 Binance Stocks 更像“币安前端中的传统券商入口”；bStocks 才是“证券代币化”。社区关于“把持有的股票转换成 bTSLA 并接入 DeFi”的方向，与 Binance 公告中“从传统股票所有权到可编程、always-on tokenized assets 的原生桥”一致，但具体转换机制、链、费用、二级市场、赎回和转让限制，截至本报告日期还不能从官方页面完整确认。

## 4. 手续费和交易摩擦比较

### 4.1 币安直接美股

Binance fee page 给出的核心费率：

| 项目 | 费率/规则 |
| --- | --- |
| 佣金 | 0 commission |
| Trading spread | 0.10%，每笔最低 0.35 美元 |
| 最低投资 | 5 美元 |
| USDC ↔ USD | Binance 吸收转换费和转换价差 |
| USDT、USD1、USDU/U、BNB → USDC | 按实时加密市场价差转换 |
| 股息处理 | Binance 不收处理费；默认美国股息预扣税 30% |
| SEC/FINRA/CAT 监管费 | Binance 当前吸收 |
| ADR 费 | 0.01-0.03 美元/股，穿透收取 |
| 自愿公司行动 | 200 美元/次 |
| DTC 转出 | 100 美元/证券/提交；ACATS 不支持 |

0.35 美元最低费用意味着：

| 单笔名义金额 | Binance spread/平台摩擦 | 有效率 |
| --- | ---: | ---: |
| 50 美元 | 0.35 美元 | 0.70% |
| 100 美元 | 0.35 美元 | 0.35% |
| 350 美元 | 0.35 美元 | 0.10% |
| 1,000 美元 | 1.00 美元 | 0.10% |
| 10,000 美元 | 10.00 美元 | 0.10% |

所以“低于 350U 固定 0.35U，高于之后 0.1%”这个理解与官方费率表一致。只是这对“小额友好”需要分两层看：它让 5-100 美元这种小单可以成交，但有效费率并不低；对 350 美元以上，它稳定在 10 bps，还要考虑非 USDC 资金的兑换价差。

### 4.2 传统券商

美国主流零售券商的显性佣金通常更低：

- Charles Schwab：在线美股和 ETF 交易 0 美元佣金；交易成本反映在买卖价差中。
- Fidelity：在线美国股票/ETF/期权交易 0 美元佣金；期权另有合约费。
- Robinhood：股票和 ETF 佣金免费，但会向客户转嫁部分监管费用。
- IBKR Lite：美国交易所上市股票/ETF 0 佣金；IBKR Pro 有 tiered/fixed 费率，固定费率常见为 0.005 美元/股，最低/最高规则另算。

传统券商的“0 佣金”不等于没有成本：订单路由、PFOF、价差、盘前盘后流动性、市场数据和监管费用都会影响实际成交。Binance 自己在 landing page 免责声明里也披露，可能因订单路由收到 payment for order flow remuneration。

### 4.3 xStocks

Kraken xStocks FAQ 给出的费用结构：

- Kraken 普通界面：用 USDG 或 USD 买 xStocks 不收 trading fee；用其他资产买入适用 Instant Buy 标准费用；资产价格里可能包含 spread。
- Kraken Pro：现货订单簿 maker -2 bps rebate，taker 10 bps。
- xStocks 转换：固定 1% trading fee。
- 最低投资：1 美元。
- 若链上交易，还要看 DEX/聚合器滑点、gas、桥费、LP 深度和二级市场溢价/折价。

xStocks 的费用优势不一定来自“永远更便宜”，而是某些入口（USD/USDG、maker、链上流动性好的路径）可能比币安 10 bps + 最低 0.35 美元更低；劣势是转换费、链上滑点、gas 和二级市场流动性波动可能很高。

### 4.4 Ondo Global Markets

Ondo 官方说没有 mint/burn fee，但在生成报价时，用户买/卖价格可能与 Ondo 买/卖底层股票的价格有轻微差异，差额和费用由 Ondo 保留；用户还要承担 gas。Ondo 的 USDon 机制会把 USDC 等稳定币原子交换成 USDon，再买入 tokenized stock。

这能解释你看到的“同样 USDT 在 Ondo 上能买到更多股数”的可能来源：如果某一时点 Ondo 报价内含成本低于 Binance 的 10 bps spread + USDT/USDC 转换价差 + 盘前/盘后宽价差，就会出现 Ondo 可买份额更多。但这个判断必须用同一时间、同一股票、同一订单大小、同一资金路径的 quote preview 对比才能坐实。

## 5. 价差：什么已经能确认，什么还需要数据

价差需要拆成四层：

1. 底层美股 NBBO / 交易所买卖价差。
2. 平台加收的 trading spread 或 quote markup。
3. 稳定币到结算货币的兑换价差。
4. 非常规时段、24h 模型、链上二级市场带来的额外流动性折价。

### 5.1 正常美股市场的高流动性标的价差很窄

我在 2026-06-01 13:03 ET 从 Nasdaq quote API 抽样看到：

| 标的 | Bid | Ask | 绝对价差 | 中间价价差 |
| --- | ---: | ---: | ---: | ---: |
| NVDA | 221.78 | 221.81 | 0.03 | 约 1.35 bps |
| AAPL | 305.71 | 305.76 | 0.05 | 约 1.64 bps |
| TSLA | 419.77 | 419.80 | 0.03 | 约 0.71 bps |
| SPY | 757.55 | 757.58 | 0.03 | 约 0.40 bps |

这和 Binance 10 bps 的官方 trading spread 不是一个量级。也就是说，在常规交易时段，对于这些极高流动性股票/ETF，传统美股市场本身的买卖价差通常显著小于 Binance 的平台 spread。

### 5.2 0xAA 的 NVDA 盘前截图

0xAA 在 2026-06-01 发的截图显示，07:01 ET 左侧 Binance、右侧富途：

| 平台 | Bid | Ask | 价差 | 中间价价差 |
| --- | ---: | ---: | ---: | ---: |
| Binance 截图 | 209.88 | 218.97 | 9.09 | 约 4.24% |
| 富途截图 | 215.900 | 215.930 | 0.030 | 约 0.014% |

这个样本支持“币安上线初期、至少在 NVDA 盘前某时点价差非常宽”的观察。但它只是单一标的、单一时点、来自截图的观察。要把它升级成严谨结论，需要至少采集多标的、多时段、多订单大小的 Binance order preview、传统券商 NBBO、xStocks/Ondo quote，并且区分常规盘、盘前、盘后和 overnight。

## 6. 股票数量和可交易范围

| 产品 | 当前覆盖 |
| --- | --- |
| 币安直接美股 | 官方 landing page 正文和新闻稿称 7000+ US-listed stocks and ETFs；页面 title 出现 8000+，正文与 FAQ 仍以 7000+ 为主 |
| xStocks | Kraken FAQ 称 131 个资产：100 只股票、27 个 ETF、4 个 specialist assets |
| Ondo GM | 官方称当前 100+ tokenized stocks and ETFs，计划未来数月扩展到 thousands |
| 传统券商 | 通常不按 token 白名单，而是覆盖绝大多数美国交易所上市股票/ETF；是否支持 OTC、期权、海外市场、盘前盘后、碎股取决于券商 |

币安当前的 7000+ 是很强的覆盖，相比 xStocks/Ondo 当前 100+ 量级大很多；但传统券商在深度、订单类型、市场数据、税表、转仓、投票和公司行动处理上仍更成熟。

## 7. 合规与资产保护

### 7.1 币安直接美股

合规结构的关键不是“币安自己变成美国券商”，而是把证券业务分层：

- Binance 负责入口、账户体验和稳定币资金路径。
- Nest Trading / Nest Exchange 相关 ADGM 实体负责证券业务承接或安排。
- Alpaca Securities LLC 作为美国券商/清算托管基础设施。

这种结构的好处是监管责任更清晰：加密交易所前端、ADGM 金融实体、美国 broker-dealer/clearing/custody 之间有边界。风险是用户要同时理解多层主体：Binance/Nest 的服务条款、Alpaca 的执行和托管、所在司法辖区可用性、PFOF、SIPC 保护范围、稳定币转换路径，以及发生争议时到底由哪个主体负责。

SIPC 只保护 SIPC 成员券商失败且客户证券/现金短缺的场景，不保护市场价格下跌，也不等同于 FDIC 存款保险。若用户持有的是 tokenized securities 而不是 Alpaca 证券账户中的证券，SIPC 保护是否覆盖不能简单套用，需要看具体账户和托管法律结构。

### 7.2 xStocks / Ondo

xStocks/Ondo 这类 tokenized stocks 通常采用 SPV/发行人 + 托管底层股票 + 链上 token 的结构。用户拿到的是链上 token，而不是传统意义上的上市公司股份。它们的优势是转移和组合性，风险是：

- 发行人/SPV 破产隔离是否真正可执行；
- 托管资产、担保权益、审计和 proof-of-reserves 的可靠性；
- 链上合约、跨链桥、DEX/借贷协议风险；
- 禁止美国人或受限地区用户参与的合规执行；
- 二级市场 token 价格偏离底层股票净值；
- 股东权利和税务处理与直接持股不同。

Kraken FAQ 称 xStocks 底层股票由 Alpaca 持有，另有 InCore Bank 作为 secondary custodian、每周 proof-of-reserves 和季度 ISAE 3000 审计；Ondo 则强调 bankruptcy-remote legal structure、overcollateralization、第三方 security agent、daily attestations、monthly reconciliations 和 annual audits。这些都是重要保护，但不是“等同于直接持有股票”。

## 8. CRS、CARF 与税务处理

CRS 是“金融账户信息自动交换”框架，不是交易税，也不是股息预扣税。它关注的是金融机构识别账户持有人的税务居民身份，并把可报告账户信息报送给本地税务机关，再由税务机关与账户持有人的税务居民辖区交换。

对币安直接美股，较稳妥的判断是：

- 这是证券/经纪/托管相关账户关系，不应因为入口是 Binance 或资金是 USDT 就认为 CRS 不适用。
- UAE/ADGM 相关金融实体处于 CRS/AEOI 环境中；若 Nest 相关实体或其他账户服务实体构成报告金融机构，且用户是可报告税务居民，CRS 触发是合理风险。
- Alpaca 是美国券商，美国不是 CRS 参与国，但美国对非美国人投资美国证券有 W-8BEN、Chapter 3/4 withholding、1042-S 等规则。美国源股息通常有 30% 默认预扣，若适用税收协定可能降低，取决于税务居民地和表格。

对 xStocks/Ondo：

- 如果通过 Kraken、Ondo app、Bitget、OKX 等 KYC 平台买卖，平台所在司法辖区的 CRS/CARF/本地税务报告规则可能适用。
- 即使 token 提到“self-custody / permissionless transfer”，链上自托管不等于税务匿名；入口、出口、KYC 平台、发行/赎回和法币/稳定币兑换都可能形成报告点。
- OECD 已把 CARF 作为加密资产自动信息交换框架，并把 CRS 与 CARF 放在同一税务透明度体系下。tokenized securities/RWA 未来被纳入报告链路的概率高于被永久豁免。

实务结论：如果用户关心 CRS，不应只问“币安会不会报”，而要问：我的开户主体是谁、账户合同由谁签、税务居民身份填给谁、W-8BEN/自证表给谁、资产由谁托管、哪一个实体在什么司法辖区承担报告义务、我的居住国/税务居民国是否与该司法辖区有激活交换关系。

## 9. 未来可扩展性

币安的扩展潜力主要来自四点：

1. 资产数量：直接接 Alpaca 这类美股基础设施，理论上覆盖从 100+ token 白名单扩到数千标的更容易。
2. 账户入口：Binance 用户本来持有稳定币和加密资产，USDT/USDC → 股票的资金路径很顺。
3. 产品组合：直接股票、bStocks、全额支付证券借贷（FPSL）、DeFi 抵押/LP/借贷、结构化产品都有组合空间。
4. 流动性：如果 bStocks 能把一级发行/赎回和二级交易打通，币安有机会把传统市场流动性、交易所撮合和链上可组合性连接起来。

主要瓶颈也很明确：

- bStocks 仍待监管批准；
- tokenized securities 的转让限制和禁止美国人士访问会削弱“permissionless”叙事；
- 24/5 或 24/7 的 fair value 模型在美股闭市时天然更难，价差会更宽；
- 税务报告、CRS/CARF、股息预扣、公司行动和跨境投资者适当性会显著增加后台复杂度；
- 如果早期价差和报价体验不稳定，会影响高频交易者和大额用户信任。

## 10. 对你列出的几个社区观点逐条校验

| 观点来源 | 校验结论 |
| --- | --- |
| BitHappy：Binance + Nest Trading + Alpaca，bStocks 后续上链 | 当前直接美股的 Nest/Alpaca 分层可由 Binance 官方公告与 landing page 支持；bStocks 后续推出也由官方公告支持。具体链和转换细节需等 bStocks 正式条款。 |
| Phyrex：极致谨慎的牌照分层模式 | 大方向成立。官方确实把 ADGM 实体、Nest Trading、Alpaca 分层披露出来。但推文中的 FSP 编号和“不允许持有或控制客户资金/投资”等细节，本报告未独立从 ADGM register 抓到原始页面，需进一步核验。 |
| 0xAA：NVDA 盘前 Binance 价差很大 | 截图支持该时点结论：Binance 约 4.24%，富途约 0.014%。但它是单点观察，不能代表所有时间/标的。 |
| FORAB：当前是第一步，后续股票可转 bStocks、证券借贷、USDC 路径、Alpaca/Nest | USDC 路径、Alpaca/Nest、FPSL、bStocks 方向有官方支持；“客户可将其持有股票转换成 bTSLA”这一具体路径截至本报告日期还未被官方条款完整确认；X 合作属于推测。 |

## 11. 后续如果要做“坐实价差”的数据方案

最小可行采样：

1. 标的：NVDA、AAPL、TSLA、SPY、QQQ、一个小盘股、一个 ADR。
2. 时段：常规盘、盘前、盘后、overnight，各采 10-20 个时间点。
3. 平台：Binance order preview、富途/IBKR/Nasdaq NBBO、Kraken xStocks、Ondo quote。
4. 订单大小：50、350、1,000、10,000 USDC/USDT。
5. 字段：bid/ask、quote price、预计获得股数/token 数、平台 fee、稳定币转换价、gas、订单有效期。

只有这样才能严谨回答“同样 USDT 到底在哪个平台买到更多股票”。

## 12. 主要来源

- Binance Stocks landing page: https://www.binance.com/en/stocks-landing
- Binance stock fee page: https://www.binance.com/en/fee/stocks
- Binance Securities Trading Terms: https://www.binance.com/en/about-legal/terms-securities-trading
- Binance 2026-06-01 PRNewswire announcement: https://www.prnewswire.com/news-releases/binance-launches-us-stocks-trading-and-previews-bstocks-tokenized-securities-302787226.html
- BitHappy X post: https://x.com/BitHappy/status/2061415974289740252
- Phyrex X post: https://x.com/PhyrexNi/status/2061446340396343441
- 0xAA X post: https://x.com/0xAA_Science/status/2061404730728034667
- FORAB X post: https://x.com/_FORAB/status/2061435661186654602
- xStocks docs introduction: https://docs.xstocks.fi/
- xStocks dividends and stock splits: https://docs.xstocks.fi/docs/dividends-and-stock-splits
- Kraken xStocks FAQ: https://support.kraken.com/articles/xstocks-faq
- Ondo Global Markets overview: https://docs.ondo.finance/ondo-global-markets
- Ondo fees and taxes: https://docs.ondo.finance/ondo-global-markets/fees-and-taxes
- Ondo comparison to other tokenized stocks: https://docs.ondo.finance/ondo-global-markets/comparison-to-other-tokenized-stocks
- Ondo available assets: https://docs.ondo.finance/ondo-global-markets/available-assets
- Alpaca about page: https://docs.alpaca.markets/us/docs/about-alpaca
- FINRA BrokerCheck Alpaca Securities LLC: https://brokercheck.finra.org/firm/summary/288202
- SEC / Investor.gov T+1 settlement bulletin: https://www.investor.gov/newT1settlement-cycle
- SEC T+1 statement: https://www.sec.gov/newsroom/press-releases/2024-62
- SIPC investor protection overview: https://www.investor.gov/introduction-investing/investing-basics/glossary/securities-investor-protection-corporation-sipc
- Charles Schwab pricing: https://www.schwab.com/pricing
- Fidelity commissions: https://www.fidelity.com/commissions
- Interactive Brokers commissions: https://www.interactivebrokers.com/en/pricing/commissions-stocks.php
- Robinhood trading fees: https://robinhood.com/us/en/support/articles/trading-fees-on-robinhood/
- OECD Tax Transparency Resource Centre / CRS / CARF: https://www.oecd.org/tax/automatic-exchange/common-reporting-standard/
- UAE Ministry of Finance AEOI / FATCA / CRS: https://mof.gov.ae/en/public-finance/international-relations/automatic-exchange-of-information-aeoi-fatca-crs/
- IRS Form 1042-S instructions: https://www.irs.gov/instructions/i1042s
- IRS W-8BEN instructions: https://www.irs.gov/instructions/iw8ben
- Nasdaq quote API samples used at 2026-06-01 13:03 ET: https://api.nasdaq.com/api/quote/NVDA/info?assetclass=stocks , https://api.nasdaq.com/api/quote/AAPL/info?assetclass=stocks , https://api.nasdaq.com/api/quote/TSLA/info?assetclass=stocks , https://api.nasdaq.com/api/quote/SPY/info?assetclass=etf
