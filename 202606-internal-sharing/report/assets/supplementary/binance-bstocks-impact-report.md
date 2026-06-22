---
topic: "Binance bStocks 对美股产品体系的影响"
project_slug: "202606-internal-sharing"
topic_slug: "binance-bstocks-impact"
status: draft
created_at: "2026-06-11"
timezone: "Asia/Shanghai"
language: "zh-CN"
related_report: "report/assets/supplementary/binance-us-stocks-research-report.md"
---

# Binance bStocks 对美股产品体系的影响

报告日期：2026-06-11（Asia/Shanghai）

## 0. 结论先行

Binance 的美股产品从 6 月初的「传统券商入口」进入了第二阶段：直接美股仍然负责开户、资金入口和底层股票持有；bStocks 把这些股票敞口包装成 ADGM 体系下的 tokenized securities，并放到 Binance Spot 与 BNB Smart Chain 上交易、转移和组合。

这对原报告最重要的更新是：bStocks 已不再只是「拟推出」。Binance 2026-06-11 公告称 bStocks 由 BTech Holdings Limited 发行，属于 Certificates representing certain Financial Instruments，不是股票或股份，不赋予持有人直接持有底层上市公司股份的权利。ADGM FSRA Official List 已列出 5 个 BTech Holdings Limited 的 bStocks，证券类型为 Certificates over Shares。

产品层面，bStocks 的关键不是多了几个 USDT 交易对，而是 Binance 把「直接美股」和「链上证券代币」用 1:1 转换连起来：用户可将直接持有的股票 tokenizing 成对应 bStocks，股票与 bStocks 之间 1:1 转换，公告称无转换费。这意味着直接美股不只是一个独立经纪服务，也成为 bStocks 的一级入口和库存来源。

技术层面，bStocks 使用 BNB Smart Chain 上的 BEP-20 token，并集成 BEP-677。BEP-677 的核心是 Scaled UI Amount：合约里的 raw balance 不变，但前端、钱包和索引器可以按 `uiMultiplier` 显示调整后的 UI 数量。这个机制很适合处理股票拆分、反向拆分和股息再投资，但也会把「显示数量」和「链上原始数量」分离，DeFi 集成如果没处理好 multiplier，会出现余额展示、抵押估值和会计口径错配。

战略上，bStocks 会增强 Binance 美股产品的增长飞轮：Binance 负责用户、交易与流动性；Nest/ADGM 结构负责证券合规框架；BNB Chain 承接自托管与 DeFi 组合性。约束同样明显：bStocks 明确不向美国或美国人士开放，只在允许地区面向合格用户，且是二级市场 basis；24/7 交易在美股闭市时会有 fair value、价差、折溢价和做市风险；用户也更容易误把「1:1 backing」理解成「直接持股」。

## 1. 和 6 月初报告相比，哪些判断需要更新

原报告在 2026-06-02 的判断大体仍成立：Binance 直接美股不是链上股票代币，而是嵌入 Binance 前端的传统美股经纪服务，Nest/Nest Exchange 相关 ADGM 实体承接证券业务，Alpaca 负责执行、清算、结算和托管。bStocks 是另一个产品层。

需要更新的地方有三点。

第一，bStocks 已从「待监管批准」变成「已进入上币/交易排期」。Binance 2026-06-11 公告称 bStocks 是首批进入 FSRA Official List 的 tokenized securities，并称发行人 prospectuses 已获 ADGM Financial Services Authority 批准。ADGM Official List 页面已显示 Tesla、Circle Internet Group、SanDisk、Micron Technology、NVIDIA 五个 bStocks 条目。

第二，直接股票到 bStocks 的转换路径已经被官方确认到产品层。6 月初报告里「客户可将持有股票转换成 bTSLA」还只能算社区推测；6 月 11 日上币公告明确写到，用户可以开始把 direct stock holdings tokenizing 成 bStocks，conversion is 1:1 between each underlying stock and its bStocks，并且 zero conversion fees。

第三，bStocks 的链和合约地址已经公开。首批资产部署在 BNB Smart Chain，Binance 公告给出了 TSLAB、NVDAB、SNDKB、CRCLB、MUB 的合约地址，并表示 2026-06-12 07:00 UTC 开放存取。换成 Asia/Shanghai 是 2026-06-12 15:00。

## 2. bStocks 到底是什么

从 Binance 公告和 ADGM 名单看，bStocks 的结构可以分成四层。

| 层级 | 角色 | 说明 |
| --- | --- | --- |
| 底层资产 | 美国上市股票 | 每个 bStock 由一股对应美国股票 1:1 backing，股票由 regulated custodian 持有 |
| 发行人 | BTech Holdings Limited | Binance group affiliate；bStocks 由该主体发行 |
| 法律形态 | Certificates over Shares | Binance 披露其为 Certificates representing certain Financial Instruments，不是股票或股份 |
| 链上载体 | BNB Smart Chain BEP-20 token | 支持提现到兼容 BSC 钱包，并集成 BEP-677 |

这不是「把股票直接搬到链上」。用户持有的是 tokenized security，代表对发行人持有底层证券的一种权益安排，而不是对 Tesla、NVIDIA 等上市公司的直接股权。Binance 公告也明确说，bStocks do not allow holders to directly own a share or stock in the underlying listed company。

首批交易与合约信息如下。

| bStock | 底层 | Binance 交易对 | 开盘时间（UTC） | BSC 合约 |
| --- | --- | --- | --- | --- |
| MUB | Micron Technology | MUB/USDT | 2026-06-11 17:00 | `0xcdf2f3e0fa43C47A6662a91C9E4a7C5f69762699` |
| CRCLB | Circle Internet Group | CRCLB/USDT | 2026-06-11 18:00 | `0x80f3D493EBCe97e343c53D29a137942416B4ffC0` |
| NVDAB | NVIDIA | NVDAB/USDT | 2026-06-11 18:00 | `0x02Fca66C1D1aFB4E2A7884261eB00F63598a7436` |
| SNDKB | SanDisk | SNDKB/USDT | 2026-06-11 18:00 | `0x3eE4dF61bd4F867E349BEaE8bFE07bc31b4850fb` |
| TSLAB | Tesla | TSLAB/USDT | 2026-06-11 18:00 | `0x5b1910eAaD6450E50f816082Aa078C41F10C292f` |

Binance 还说 SpaceX bStocks（SPCXB）会在之后推出，但截至本文档日期，公告没有给出具体上币时间和合约地址。

## 3. BEP-677 解析

BEP-677 的标题是 Implement EIP-8056 Scaled UI Amount，状态为 Draft，创建日期是 2026-04-14。它把 Ethereum 侧的 EIP-8056 引入 BNB Smart Chain，用于 BEP-20 token，并额外增加了 BSC 专属的 scheduled multiplier 查询扩展。

这个标准要解决的问题很具体：RWA、股票代币、债券、计息资产等 token 经常需要调整用户看到的数量，但不一定希望真的对每个地址 mint、burn 或转账。比如 2-for-1 股票拆分，如果对每个 holder 都增发 token，成本高、操作复杂，也容易影响 DeFi 协议内部状态。BEP-677 的处理方式是保留 raw balance，把变化放到 UI multiplier。

核心公式是：

```text
uiAmount = rawAmount * uiMultiplier / 1e18
```

`1e18` 表示 1.0x。`2e18` 表示显示数量放大到 2 倍。raw balance 仍然是链上账户真实记账单位，UI amount 是展示层或索引层的结果。

### 3.1 必须实现的接口

BEP-677 要求兼容 token 实现 `IScaledUIAmount`，接口 ID 是 `0xa60bf13d`。这个接口至少包括：

- `uiMultiplier()`：返回当前生效的 UI multiplier。
- `UIMultiplierUpdated` 事件：记录 multiplier 从旧值更新到新值，以及生效时间。
- `TransferWithUIAmount` 事件：每次 BEP-20 `Transfer` 都要同步发出，用来记录本次转账对应的 UI-adjusted amount。

它还要求实现 EIP-8056 的 pending multiplier 扩展，接口 ID 是 `0x4bd27648`：

- `newUIMultiplier()`：返回已经排期、但可能尚未生效的新 multiplier。
- `effectiveAt()`：返回新 multiplier 的生效时间；没有 pending change 时返回 0。

### 3.2 可选接口和 BSC 扩展

可选接口有两类：

- `IScaledUIAmountConversion`：提供 `toUIAmount()` 和 `fromUIAmount()`，方便 raw amount 与 UI amount 互转。
- `IScaledUIAmountBalances`：提供 `balanceOfUI()` 和 `totalSupplyUI()`，直接查询 UI-adjusted balance 和 supply。

BEP-677 还增加了 `IERC8056Scheduled`，这是 BSC 扩展，不属于上游 EIP-8056。它提供：

- `pendingMultiplier()`：一次返回 pending multiplier 和生效时间。
- `hasPendingMultiplier()`：显式判断是否存在尚未生效的 multiplier change。
- `UIMultiplierChangeOverwritten` 事件：记录一个排期中的 multiplier 被新的排期覆盖。

这个 BSC 扩展的意义在于减少前端和索引器的歧义。EIP-8056 的 `newUIMultiplier()` 可能在变更已经生效后仍返回存储里的 next value；`hasPendingMultiplier()` 直接告诉集成方「现在是否真的还有 pending change」。

### 3.3 为什么 bStocks 需要它

Binance 公告明确提到，bStocks 的 dividends and splits 会通过 Multiplier mechanism 自动处理。这里至少有两个用法。

股票拆分时，发行人可以把 multiplier 调整到新的比例，让用户看到的 bStock 数量变化，而不需要逐个地址发 token。比如 1 个 raw token 在 2-for-1 split 后仍是 1 个 raw token，但 UI 侧显示为 2 个单位。

股息处理时，Binance 公告说，底层公司发股息后，net dividend value 会在扣除适用美国预扣税后自动再投资，并通过 on-chain Multiplier 调整反映到用户持有的 fraction 上。用户体验更像 total-return token：不是拿到现金股息，而是 token 的显示价值或显示数量随 multiplier 增长。

这也解释了为什么 Binance 把 BEP-677 称为「native support for real-world assets on BNB Smart Chain」。它不是一个新的交易协议，而是让钱包、区块浏览器、DeFi 协议和数据索引器知道：这个 token 的人类可读数量可能要乘一个公开 multiplier。

### 3.4 集成风险

BEP-677 最大的工程风险是 display/accounting 分离。

对普通钱包来说，如果不支持 BEP-677，就可能只显示 raw balance，用户会觉得余额没有随拆股或再投资变化。对 DeFi 协议来说，风险更大：借贷协议、AMM、收益聚合器、风控系统必须明确自己用 raw amount、UI amount，还是外部 NAV/oracle price 做估值，不能同时把 multiplier 和价格调整重复计算。

几个具体注意点：

- raw amount 是链上记账真相，`toUIAmount()` 和 `fromUIAmount()` 只是展示边界工具，不能用于内部会计假设。
- multiplier 更新是特权操作。生产部署需要多签、timelock、治理或其他权限控制；单一 EOA 可以调整用户看到的余额，中心化风险很高。
- pending multiplier 可以被覆盖，也可能被提前到更近的生效时间。集成方要监听 `UIMultiplierUpdated` 和 `UIMultiplierChangeOverwritten`，不能只缓存第一次看到的时间。
- 极端 multiplier 会导致小余额被截断到 0，或大余额的 UI 值超出可表示范围。实现方需要设置合理上下限。
- BEP-677 不改变 BEP-20 的 transfer 语义。旧协议仍能转 token，但不理解 multiplier 的协议可能会展示或估值错误。

### 3.5 Base B20 Asset 的 multiplier 是同一个东西吗

Base 仓库里的 `B20Asset` 也有 multiplier，但它和 BEP-677 的关系应拆开看：数学模型很接近，标准接口不是同一个。

Base 的实现位于 `crates/common/precompiles/src/b20_asset/`，它是 Base B-20 token 的 asset variant，属于原生 precompile 表面，不是普通 Solidity ERC-20/BEP-20 扩展。`IB20Asset` ABI 暴露了这些和 multiplier 相关的接口：

- `WAD_PRECISION()`：返回 `1e18`。
- `multiplier()`：返回当前 multiplier。
- `toScaledBalance(rawBalance)`：按 `rawBalance * multiplier / WAD_PRECISION` 计算 scaled balance。
- `toRawBalance(scaledBalance)`：按 `scaledBalance * WAD_PRECISION / multiplier` 反算 raw balance。
- `scaledBalanceOf(account)`：等于 `toScaledBalance(balanceOf(account))`。
- `updateMultiplier(newMultiplier)`：更新 multiplier。
- `MultiplierUpdated(uint256 multiplier)`：更新事件。

这和 BEP-677 的核心思想一样：raw balance 不改，显示层按 multiplier 得到 scaled/UI balance。Base 测试里也直接验证了 2x multiplier 下，`toScaledBalance(100)` 变成 `200`，`toRawBalance(200)` 变回 `100`。

差异在接口和治理语义。

| 维度 | BEP-677 / EIP-8056 | Base B20 Asset |
| --- | --- | --- |
| 所属形态 | BEP-20/ERC-20 token extension | Base 原生 B-20 asset precompile |
| 当前 multiplier getter | `uiMultiplier()` | `multiplier()` |
| 显示余额名称 | UI amount / UI balance | scaled balance |
| 转换函数 | `toUIAmount()` / `fromUIAmount()`（可选） | `toScaledBalance()` / `toRawBalance()` |
| 当前余额函数 | `balanceOfUI()`（可选） | `scaledBalanceOf()` |
| transfer 辅助事件 | 必须随 `Transfer` 发 `TransferWithUIAmount` | 只有普通 `Transfer`，未看到 `TransferWithUIAmount` |
| 排期机制 | 有 `newUIMultiplier()`、`effectiveAt()`；BSC 扩展还有 `pendingMultiplier()` 和 `hasPendingMultiplier()` | 未看到 pending/effectiveAt；`updateMultiplier()` 是直接更新 |
| 更新事件 | `UIMultiplierUpdated(old, new, effectiveAt)`；BSC 还有 overwrite 事件 | `MultiplierUpdated(multiplier)` |
| 发现机制 | ERC-165 `supportsInterface()` 检查接口 ID | 通过 B20 address/variant、precompile ABI 和链级 feature 激活识别 |
| 权限模型 | 标准不规定 setter；参考实现建议多签/timelock/治理 | `updateMultiplier()` 要求 `OPERATOR_ROLE`，且拒绝 zero multiplier |

所以结论是：如果我们讨论「把链上原始余额按 1e18 精度 multiplier 显示成另一套余额」这个抽象，Base B20 Asset 和 BEP-677 是同一类东西；如果讨论钱包、浏览器、DeFi 协议能不能用同一套 ABI 读取、监听和处理，它们不是同一个标准。

这对跨链 RWA 生态有现实影响。BEP-677 试图做的是通用 token extension，让钱包和协议通过接口 ID 识别支持能力；Base B20 Asset 更像链原生资产标准，把 asset token、角色、策略、memo、metadata、batch mint 和 multiplier 放进 precompile。一个 DeFi 协议如果想同时支持 bStocks 和 Base B20 Asset，不能只写一个「multiplier adapter」，至少要分别适配：

- BSC/bStocks：读 `uiMultiplier()`、`newUIMultiplier()`、`effectiveAt()`，监听 `UIMultiplierUpdated`、`TransferWithUIAmount` 和可能的 overwrite 事件。
- Base/B20 Asset：读 `multiplier()`、`toScaledBalance()`、`scaledBalanceOf()`，监听 `MultiplierUpdated`，并理解 B20 的 role/policy/announcement 机制。

Base 的 `announce()` 值得单独注意。它能发布 holder-impacting announcement，并原子执行一组 `internalCalls`，比如更新 metadata 或 multiplier；但它不是 BEP-677 的 scheduled multiplier。它提供的是公告和批处理语义，不提供未来生效时间、pending multiplier 查询或 overwrite 审计事件。把两者都叫「multiplier」可以，但不要把 Base 的 `Announcement` 等同于 BEP-677 的 `effectiveAt`。

## 4. 对 Binance 美股产品体系的影响

### 4.1 直接美股从「终点产品」变成「入口产品」

6 月初 Binance Stocks 的核心卖点是用户可以用 Binance 账户买 7000+ 美股和 ETF，背后由 Nest/Alpaca 结构承接。bStocks 之后，直接美股多了一层用途：它可以被 tokenizing 成 bStocks。

这会改变 Binance Stocks 的产品定位。它不只是让用户在 Binance 内买股票，也成为 bStocks 的一级转换入口。用户先买直接股票，再按 1:1 转成 bStocks；或者持有 bStocks，在允许路径下转回对应股票。只要这个转换路径稳定，bStocks 的二级市场价格就有了一个靠近底层股票的锚。

但这个锚不是无条件的。它依赖可转换资格、司法辖区限制、转换窗口、底层股票市场时间、托管和发行人运作。Binance 公告确认了 1:1 和 zero conversion fee，但法律条款、赎回限制、暂停条件和地区限制仍要看最终文件。

### 4.2 Binance Spot 拿到新的证券类交易品种

首批 bStocks 以 USDT 现货交易对上线，并接入 Spot Algo Trading Bots。Binance 还给首批交易对安排了 zero maker fees，promotion period 到 2026-08-31 23:59 UTC。

这能帮助 Binance 把美股敞口变成更熟悉的 crypto 交易体验：USDT 计价、Spot order book、交易机器人、24/7、可提现。对存量加密用户来说，门槛比传统券商低；对专业交易者来说，关键看深度、价差、做市质量和 conversion arbitrage 是否顺畅。

这也会带来新的市场微结构问题。bStocks 24/7 交易，但底层美股不是 24/7 交易。美股闭市期间，bStocks 的价格会依赖做市商 fair value、相关期货/ETF/盘后信息和订单簿深度。遇到财报、宏观数据或突发新闻时，bStocks 可能先于美股常规盘反映预期，也可能出现较大折溢价。

### 4.3 BNB Chain 得到一个高辨识度 RWA 用例

bStocks 支持提现到 BNB Smart Chain 钱包，并被 Binance 明确放进 DeFi 叙事。对 BNB Chain 来说，这比普通 RWA 代币更有信号意义：底层是用户熟悉的美股标的，入口是 Binance，合约标准是 BEP-677。

潜在影响包括：

- BNB Chain 可以围绕 bStocks 建 AMM、借贷、结构化产品、收益策略和组合资产。
- BEP-677 可能成为 BNB Chain RWA token 的事实接口，尤其是需要拆股、再投资、单位重计价的资产。
- 链上应用会被迫处理 regulated token、transfer restriction、KYC/eligibility 和 multiplier-aware accounting，这和普通 meme/DeFi token 的集成方式不同。

这里不能把「Use in DeFi」理解成完全 permissionless。Binance 公告同时写明，bStocks 只面向 permitted jurisdictions 的 eligible users，且可因法律、制裁、资格或 offering documents 限制被拒绝、取消、暂停或 unwind。链上可转移性与证券合规约束之间会长期存在张力。

### 4.4 公司行动处理从券商后台进入链上显示层

直接美股产品里，分红、公司行动和税务处理主要由经纪/托管链路完成。bStocks 把其中一部分结果通过 multiplier 显示到链上 token。

股息不会简单以现金发到用户账户，而是公告所说的 net dividend value 自动再投资，再通过 multiplier 反映到每个 fraction 上。这个设计有两个好处：用户不用处理零碎现金股息；链上 token 更像自动复投的 total-return exposure。

代价是用户更难直观看出收益来源。一个 bStock 的「数量变多」可能来自拆股，也可能来自股息再投资；如果前端、税表和链上浏览器没有讲清楚，用户会把 multiplier 增长误解成免费增发。对研究和数据分析也一样，不能只看 raw transfer 和 raw balance，需要把 multiplier event 纳入时间序列。

### 4.5 与 xStocks/Ondo 的竞争维度变化

原报告把 Binance 直接美股和 xStocks/Ondo 区分得很清楚：前者像传统券商入口，后者强调链上转移和 DeFi 组合。bStocks 让 Binance 进入后者的战场，但打法不同。

Binance 的优势是前端流量、USDT 现货订单簿、直接美股入口和 BNB Chain 生态。尤其是「直接股票 1:1 转 bStocks」如果体验稳定，会比单纯发行链上 token 更容易解释 backing。

短板是合规限制更重，且首批资产只有 5 个，远少于 Binance 直接美股的 7000+ 覆盖。它能否超过 xStocks/Ondo，不取决于公告本身，而取决于三个后续指标：资产扩展速度、24/7 订单簿深度、以及 DeFi 协议对 BEP-677 和 transfer restrictions 的适配质量。

## 5. 对用户、交易和风控的具体影响

| 维度 | 正面影响 | 新风险 |
| --- | --- | --- |
| 用户入口 | 从 Binance 账户、USDT 和直接美股自然进入 bStocks | 用户可能混淆直接持股、证券账户权益和 tokenized certificates |
| 交易时间 | bStocks 24/7 交易，不受美股常规开盘限制 | 闭市期间底层无现货价格锚，折溢价和宽价差风险更高 |
| 资金效率 | bStocks 可提现、自托管，并进入 BSC DeFi | DeFi 协议未适配 multiplier 时可能错误估值 |
| 公司行动 | 股息和拆分可通过 multiplier 自动反映 | 用户拿到的是自动再投资效果，不是现金股息；税务解释更复杂 |
| 流动性 | Binance Spot 和 zero maker fee 可快速引导做市 | 早期订单簿深度、赎回能力和做市商行为需要实测 |
| 合规 | ADGM prospectus、FSRA Official List 和明确主体结构提升可解释性 | 美国人士排除、地区限制、二级市场 basis 和 unwind 权利会限制可用性 |

## 6. 需要后续跟踪的问题

1. bStocks 与直接美股之间的转换是否全天候可用，还是受美股市场、托管、清算或地区资格影响。
2. 1:1 conversion 的实际价格路径：是否只按 share count 转换，还是还会受税费、暂停、公司行动、碎股处理影响。
3. Proof of Collateral 页面如何披露 backing：更新频率、托管方、审计/证明方式、是否逐资产披露。
4. BEP-677 multiplier 的权限控制是谁：发行人、多签、timelock、监管/托管触发，还是其他治理结构。
5. Binance Spot 的 bStocks 订单簿价差、深度和闭市期间溢价水平。
6. BNB Chain DeFi 协议如何识别 BEP-677：是否使用 `supportsInterface()`，是否监听 multiplier 事件，是否防止价格和数量重复调整。
7. 跨链 RWA 协议如何同时适配 BEP-677 和 Base B20 Asset：是否抽象出 raw/scaled balance adapter，而不是硬编码某一条链的函数名。
8. 税务报告如何呈现：股息再投资、美国预扣税、token 买卖损益、从股票转 bStocks 是否构成应税事件。

## 7. 对原报告可直接替换的更新摘要

可以把原报告第 3 节和第 9 节里关于 bStocks 的表述更新为：

> Binance 在 2026-06-11 公告中正式推出 bStocks。bStocks 由 BTech Holdings Limited 发行，属于 ADGM 体系下的 Certificates representing certain Financial Instruments，不是股票或股份，不赋予持有人直接持有底层上市公司股份的权利。首批 bStocks 包括 Tesla、NVIDIA、SanDisk、Circle Internet Group 和 Micron Technology，均已出现在 ADGM FSRA Official List，Binance Spot 对应 USDT 交易对按 2026-06-11 17:00/18:00 UTC 排期开盘。用户可以把 direct stock holdings 以 1:1、无转换费的方式 tokenizing 成 bStocks；bStocks 是 BNB Smart Chain 上的 BEP-20 token，集成 BEP-677，用 multiplier 处理拆股和股息再投资。bStocks 仍不向美国或美国人士开放，只面向允许地区的合格用户，并受流动性、发行人、托管、经纪、运营、技术、监管、税务、费用、预扣和转让限制等风险影响。

## 8. 来源与抓取说明

Binance 普通公告网页在本地抓取时返回 CloudFront/WAF challenge；本文使用同一 article code 对应的 Binance public CMS detail API 提取正文，并以用户可访问的公告 URL 作为来源入口。Binance 法律条款页和 Proof of Collateral 页未能通过本地抓取成功抽取，本文不引用这些页面中未读取到的细节。

主要来源：

- Binance bStocks 公告：<https://www.binance.com/en/support/announcement/detail/2c0c92ed15ac42d1b14bb1eac00d22bb>
- Binance bStocks 上币公告：<https://www.binance.com/en/support/announcement/detail/5646e3f9ea6b4c989cb76aa18bd99245>
- ADGM FSRA Official List of Securities：<https://www.adgm.com/financial-services-regulatory-authority/listing-authority/official-list-of-securities>
- BEP-677：<https://raw.githubusercontent.com/bnb-chain/BEPs/master/BEPs/BEP-677.md>
- EIP-8056：<https://eips.ethereum.org/EIPS/eip-8056>
- BEP-677 reference implementation：<https://github.com/bnb-chain/bep-677-contracts>
- Base B20 Asset ABI：`/Users/whisker/Work/src/networks/base/base/crates/common/precompiles/src/b20_asset/abi.rs`
- Base B20 Asset storage：`/Users/whisker/Work/src/networks/base/base/crates/common/precompiles/src/b20_asset/storage.rs`
- Base B20 Asset token logic：`/Users/whisker/Work/src/networks/base/base/crates/common/precompiles/src/b20_asset/token.rs`
- Base B20 factory initialization：`/Users/whisker/Work/src/networks/base/base/crates/common/precompiles/src/b20_factory/storage.rs`
- Base B20 system tests：`/Users/whisker/Work/src/networks/base/base/etc/systems/tests/b20_precompile.rs`
- 既有研究报告：`report/assets/supplementary/binance-us-stocks-research-report.md`
