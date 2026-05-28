# 20260605 内部分享 — Slides Outline (Final)

> 目标受众：Mantle 全公司工程团队
> 时长：~30 分钟（20 分钟演讲 + 10 分钟 Q&A）
> 核心论点：L2 赛道正从通用竞争转向垂直差异化，Mantle 应以「机构金融」为下一阶段叙事锚点
> 数据截止：2026-05-26
> Slides Language: English

---

## Opening

### Slide 1 — 封面

- **标题**：Mantle 竞争格局与叙事方向分析
- **演讲者信息** Mantle Engineering Team

**Design**
- **背景**：纯黑 (#0A0A0A)，中央 Mantle logo 微光效果，底部几何线条装饰
- **颜色**：标题白色，副标题 #A0A0A0，演讲者信息 #666666
- **布局**：全屏居中，标题占页面 40% 垂直区域
- **高亮方式**：Mantle 品牌绿 (#00D395) 用于 logo 和底部装饰线

---

### Slide 2 — 议程

- 三章结构概览，用连接词点明逻辑链：
  1. **现状**：市场发生了什么变化？→ Mantle 面临的挑战
  2. **竞品**：其他人在做什么？→ 竞争压力来自哪里
  3. **方向**：Mantle 应该怎么走？→ 三条路线的技术可行性评估
- **核心结论前置**（一句话）：机构金融是契合度最高的方向——以 zkSync Prividium 为对标，利用国库和收益生态优势构建合规技术栈

**Design**
- **背景**：#0A0A0A，右侧纵向细线分隔装饰
- **颜色**：章节标题白色，描述文字 #CCCCCC，核心结论 #00D395
- **布局**：三列卡片（等宽），卡片底色 #1A1A1A 圆角 8px，卡片间用绿色箭头连接
- **图表类型**：三列卡片 + 连接箭头流程
- **高亮方式**：核心结论行底部绿色下划线强调

---

## Chapter 1: 当前市场现状分析

> 演讲目标：建立共识——市场环境已变，Mantle 需要新叙事

### Slide 3 — L2 赛道格局演变

- **数据图表 ①**：6 链 TVL 趋势折线图（近一年每日数据）+ 市场份额饼图
  - Base $4.47B (67.0%) / Arbitrum $1.51B (22.7%) / OP Mainnet $342M (5.1%) / **Mantle $232M (3.5%)** / X Layer $93M (1.4%) / zkSync $18M (0.3%)
  - Base + Arbitrum = 89.7% 六链流动性
  - 年度变化：Base +40.8% / Arbitrum -34.3% / zkSync -61.4% / Mantle +2.1%
- **数据图表 ②**：5 链 DAU 趋势折线图（7 日移动均线）+ 市场份额饼图（X Layer 无 Dune 数据）
  - Base 435K (72.6%) / Arbitrum 140K (23.3%) / OP 16K (2.7%) / zkSync 6K (1.0%) / **Mantle 1.6K (0.3%)**
  - 所有链 DAU 大幅下降：Base -74.7% / Arbitrum -56.6% / OP -84.5% / Mantle -81.0% / zkSync -31.6%
- **数据图表 ③**：6 链手续费中位数趋势（对数坐标）+ 柱状图对比
  - OP Mainnet $0.00002 / X Layer $0.00014 / **Mantle $0.0011** / Base $0.0015 / Arbitrum $0.003 / zkSync $0.015
  - EIP-4844 后所有链手续费极低（$0.00002 — $0.015），费用不再是差异化竞争维度
- **关键洞察文字**（长尾效应）：
  - **TVL 赢家通吃**：Base + Arbitrum 占 89.7%，剩余四链合计 10.3%
  - **DAU 更极端**：Base 独占 72.6%，Mantle 仅 0.3%——用户集中度远超资金集中度
  - **全行业用户萎缩**：六链 DAU 均大幅下降（2025-06 至 2026-05），不仅是长尾问题
  - **费用竞争失去意义**：EIP-4844 后中位数费用均在亚美分级别，新竞争维度 = 生态控制 + 分发 + ZK/隐私 + 收益资产
- **数据来源标注**：DefiLlama（TVL）/ Dune Analytics（DAU + Fees），2026-05-26 快照
- **图表文件**：`charts/slide3-tvl-line.png` / `slide3-tvl-pie.png` / `slide3-dau-line.png` / `slide3-dau-pie.png` / `slide3-fees-line.png` / `slide3-fees-bar.png`

**Design**
- **背景**：#0A0A0A
- **颜色**：品牌色编码——Base #0052FF / Arbitrum #28A0F0 / OP #FF0420 / Mantle #00D395 / zkSync #8C8DFC / X Layer #F0B90B；Mantle 数据加粗强调
- **布局**：三行分栏——TVL 折线图+饼图（35%）/ DAU 折线图+饼图（35%）/ 费用折线图+柱状图（20%）+ 底部洞察文字
- **图表类型**：折线趋势图（每日数据，7 日移动均线平滑）+ 饼图（市场份额）+ 柱状图（费用对比，对数坐标）
- **高亮方式**：Mantle 线条加粗（3px vs 1.5px）+ 白色描边柱体；饼图中 Mantle 切片弹出；下降数字用 #FF4444 标注

---

### Slide 4 — 叙事转向：DeFi → RWA / 机构金融

- **数据图表 ①**：DeFi TVL vs RWA TVL 双轴折线图（近一年每日数据）——两条趋势线呈剪刀差走势
  - 全球 DeFi TVL: $96B (2025-05) → 峰值 $171B (2025-10) → $81B (2026-05)，YoY **-15.3%**
  - 链上 RWA: $10.7B (2025-05) → $33.8B (2026-05)，YoY **+215.7%**
- **数据图表 ②**：YoY 增长率柱状对比图（DeFi 三项 vs RWA 三项，红绿对比）
  - DeFi 侧: 全球 DeFi TVL -15% / Aave V3 TVL -30% / Blast TVL -72%
  - RWA 侧: 链上 RWA +216% / 美国国债代币化 +143% / BlackRock BUIDL +14%
- **数据图表 ③**：RWA 资产类别堆叠面积图（rwa.xyz 数据）
  - 美国国债 $15.05B / 大宗商品 $7.08B / 资产支持信贷 $2.32B / 特种金融 $1.67B / 股票 $1.61B / 非美政府债 $1.41B / 其他 $5.70B
  - 12 个子类别 YoY 全部正增长，最高：企业信贷 +1552%，最低：美国国债 +143%
- **数据图表 ④**：Blast TVL 崩塌曲线（DeFi 激励驱动反面教材）
  - Peak $2.26B (2024-06) → $31M (2026-05)，**-99%**
- **数据图表 ⑤**：Top RWA 协议个体增长折线图（BUIDL / USYC / Ondo / Spiko / Superstate）
- **数据图表 ⑥**：RWA 各资产类别 YoY 增长率横向柱状图（全部为正，按增速排序）
- **左半**：DeFi 天花板
  - 全球 DeFi TVL $81B，较 2025-10 峰值 $171B 回落 53%
  - Aave V3 独占借贷 TVL 34%（$13.5B / $40.3B），高度集中但整体萎缩 -30%
  - Blast 案例：Peak $2.26B → $31M（激励驱动的极端反面教材，-99%）
- **右半**：RWA 加速
  - 链上 RWA $33.8B（YoY +216%，数据来源：rwa.xyz）
  - 美国国债代币化 $15.05B（YoY +143%）
  - BlackRock BUIDL ~$3.0B AUM（部署在 Arbitrum/Optimism，不在 Mantle）
  - BlackRock 2026-05 向 SEC 申请 $7B 货币市场基金上链
- **底部警示**：深层矛盾——Vitalik cypherpunk 隐私优先 vs 机构需要 KYC/许可制
- **数据来源标注**：RWA.xyz（RWA 分类数据导出，2026-05-26 快照）/ DefiLlama API（DeFi TVL + 协议 TVL，2026-05-27 快照）/ SEC filing
- **图表文件**：`charts/slide4-defi-vs-rwa.png` / `slide4-growth-comparison.png` / `slide4-rwa-breakdown.png` / `slide4-blast-collapse.png` / `slide4-top-rwa-protocols.png` / `slide4-rwa-category-growth.png`

**Design**
- **背景**：#0A0A0A
- **颜色**：主文字白色，DeFi 侧数字 #FF4444（红色警示），RWA 侧数字 #00D395（绿色增长）
- **布局**：三行分栏——DeFi vs RWA 双轴折线图+增长率柱状图（40%）/ RWA 堆叠面积图+Top协议折线图（35%）/ Blast 崩塌图+类别增长率图（25%）+ 底部洞察文字
- **图表类型**：双轴折线趋势图（DeFi 红 / RWA 绿）+ 红绿柱状对比图 + 堆叠面积图（资产类别分色）+ 协议折线图 + Blast 崩塌面积图 + 横向增长率柱状图
- **高亮方式**：底部警示条用 #FF4444 左边框 + #1A1A1A 底色；DeFi 下降数字 #FF4444，RWA 增长数字 #00D395

---

### Slide 5 — Mantle 当前定位与挑战

- **技术栈**：OP Stack based / Ethereum aligned / OP Succinct（底层 zkVM 为 SP1 Hypercube）/ Ethereum blob DA（已移除 EigenDA，L2Beat 重新分类为 rollup）
- **数据图表 ①**：Mantle TVL + DAU 双轴合并折线图（近一年每日数据）
  - TVL（绿色，左轴）：$219M (2025-06) → 峰值 $705M (2026-04, Aave V3 驱动) → $232M (2026-05)，YoY +6%
  - DAU（红色，右轴）：8,143 (2025-06) → 1,608 (2026-05)，YoY **-80%**，持续下降无反弹
  - **关键标注**：Aave V3 上线时间线 (2026-02-19) 竖线——TVL 因 Aave V3 激励驱动短暂飙升，但 DAU 在整个周期内单调下降
- **数据图表 ②**：Mantle DeFi 协议 TVL 堆叠面积图（Merchant Moe / Agni / CIAN / MI4 / Ondo USDY / Aave V3）
  - **原生 DeFi 持续萎缩**（Aave V3 上线前已在下滑）：
    - Merchant Moe（Mantle 最大 DEX）：$84M → $37M（**-56%**）
    - Agni Finance（第二大 DEX）：$39M → $23M（**-41%**）
  - **Aave V3 激励驱动的短暂飙升**：
    - 2026-02-19 上线，12 天内存款超 $290M，峰值 $592M（占总 DeFi TVL 56%），五月回落至 $132M
  - **其他协议平稳或小幅变动**：
    - CIAN Yield Layer：$115M → $162M / MI4：$170M → $143M / Ondo USDY：~$29M
  - **核心洞察**：Mantle 原生 DeFi（Merchant Moe + Agni）在 Aave V3 上线前就已持续萎缩，Aave V3 带来的 TVL 增量是激励驱动——激励结束后回落，整体 DeFi 基本面并未改善
- **资产基本盘**：
  - mETH ~$925M TVL（第 4 大 ETH LST）
  - cmETH ~$515M TVL
  - 稳定币 ~$669M（峰值 $825M，81% 保留率）
- **活跃度困境**：
  - DAU 月均持续下行：Jun'25 8.6K → Aug'25 79.8K (峰值，疑似空投) → Jan'26 2.6K → May'26 1.6K
  - 日收入 <$1K
- **DeFi 努力的教训**：Aave V3 是 Mantle 在 DeFi 方向上的重大投入，带来了短期 TVL 恢复（$163M → $705M），但未能带动用户增长——DAU 在同期仍从 2.6K 降至 1.6K
- **核心问题**（一句话）：TVL 部分恢复但用户持续流失，DeFi 激励驱动已证伪，需要新叙事锚点
- **数据来源标注**：DefiLlama API（TVL + 协议 TVL，2026-05-27 快照）/ Dune Analytics（DAU，2026-05-26 快照）
- **图表文件**：`charts/slide5-tvl-dau-combined.png` / `slide5-protocol-breakdown.png`

**Design**
- **背景**：#0A0A0A
- **颜色**：主文字白色，TVL 数据 #00D395，DAU/困境数据 #FF4444，Aave V3 #4DA6FF，核心问题 #FFFFFF
- **布局**：两行区域——TVL+DAU 合并折线图（顶部 45%）+ 协议堆叠面积图（中部 40%）+ 底部结论横幅（15%）
- **图表类型**：双轴折线图（TVL 绿色面积 + DAU 红色线条）+ 堆叠面积图（协议分色）+ Aave V3 上线竖线标注
- **高亮方式**：Aave V3 上线虚线标注 + 蓝色标签；核心问题行全宽绿色左边框；DAU 下降百分比 #FF4444 加粗

---

### Slide 6 — Chapter 1 小结

- **三个要点**：
  1. DeFi 必须守住但无法带动增长
  2. RWA/机构金融 >200% YoY——最快增长的链上叙事
  3. 合规基础设施成为新竞争维度（五链中仅 zkSync 有）
- **过渡句**：「市场在变，竞争对手在动——我们需要看看他们在做什么」

**Design**
- **背景**：#0A0A0A
- **颜色**：要点编号 #00D395，要点文字白色，过渡句 #A0A0A0
- **布局**：三个数字卡（横排），每卡底色 #1A1A1A，右下角绿色箭头指向 Chapter 2
- **图表类型**：三列数字卡 + 过渡箭头
- **高亮方式**：第二张卡（RWA 增长）绿色描边突出

---

## Chapter 2: 竞争对手的开发与叙事分析

> 演讲目标：全景扫描竞争格局，识别威胁与机会

### Slide 7 — 竞品分析框架

- **三类竞争者矩阵**：
  - **L2 竞品**（同赛道直接竞争）：Base / Arbitrum / Optimism / zkSync / StarkNet / X Layer
  - **L1 通用链**（跨赛道替代竞争）：Solana / Sui / BNB Chain
  - **L1 垂直链**（新赛道抢位竞争）：Tempo / Circle Arc / Canton
- **分析维度说明**：近期代码活动（90 天 GitHub PR）+ 叙事方向变化

**Design**
- **背景**：#0A0A0A
- **颜色**：分组标题白色，链名 #CCCCCC，维度说明 #A0A0A0
- **布局**：三行分组表，每行一类竞争者，行底色交替 #111111 / #0A0A0A，左侧图标列
- **图表类型**：分组矩阵表 + 链 logo 图标
- **高亮方式**：L1 垂直链行用 #FF4444 左边框标记为"高威胁"

---

### Slide 8 — L2 竞品：技术路线对比（上）

| 竞品 | 核心叙事 | 关键技术动向 | 90d PRs |
|---|---|---|---|
| **Base** | Coinbase 分发 + Base-owned Stack + onchain economy 品牌 | Azul 硬分叉（2026-05-28 主网激活，收敛至 base-reth-node + base-consensus）/ Flashblocks 200ms 预确认（主网已上线）/ Multiproof TEE+ZK（推进中，未完成）/ Beryl 合规资产原语 B20Factory + PolicyRegistry（代码已合并，**mainnet 未激活**）/ Base Account + x402 Agent 微支付协议 | 1,810 |
| **Arbitrum** | 金融原生 + 可定制 Nitro stack | BoLD 无许可验证（Draft 阶段，多个 DO NOT MERGE PR）/ Timeboost MEV 排序竞拍 / Stylus SDK v0.10.2→v0.10.7 WASM 多语言合约 / Orbit 应用链部署工具（近期代码信号较弱，主要靠官方文档支撑）/ 窗口内 22 个 release 信号 | 256 (Nitro)，34 贡献者 |
| **Optimism** | Superchain 互操作 + client 栈现代化 | op-reth/kona Rust 迁移（**op-geth 2026-05-31 停止支持**）/ op-supernode/supervisor 互操作 devnet / op-contracts v7 RC / ZK dispute game 设计中 / 窗口内 49 个 monorepo release，周 PR 从 W09 50 个加速至 W21 129 个 | 1,202（751 merged），98 PR 作者 |

- **要点**：
  - Base 的护城河不是纯技术——Coinbase 120M+ 用户分发 + 独立 client stack + 合规资产原语（Beryl/PolicyRegistry）构成不可复制的组合优势；但 Beryl 仍在激活门控后面，尚非已上线能力
  - Arbitrum 近期重心是底层硬化（BoLD 验证 / Timeboost 排序 / Stylus SDK），而非 Orbit 应用链代码爆发——叙事上讲的是「金融原生 + 可定制」，实际工程集中在安全与排序
  - **op-geth EOL 直接影响 Mantle**：Optimism 要求所有 OP Stack 链在 2026-05-31 前迁移至 op-reth/cannon-kona，Mantle 需评估迁移路径
  - † Base 5,000 TPS 为 burst 口径，非持续吞吐

**Design**
- **背景**：#0A0A0A
- **颜色**：表头白色底色 #1A1A1A，PR 数字 #4DA6FF，要点白色，op-geth EOL 警告 #FF4444
- **布局**：全宽表格（占页面 65%），底部要点文字区域（35%）
- **图表类型**：四列数据表，PR 列带横向条形微图
- **高亮方式**：Base 行 PR 数字 #00D395 强调（最高活跃度）；op-geth EOL 行用 #FF4444 左边框

---

### Slide 9 — L2 竞品：技术路线对比（下）

| 竞品 | 核心叙事 | 关键技术动向 | 关注点 |
|---|---|---|---|
| **zkSync** | ZK 正确性 + Elastic Chain + 企业隐私 | 工程重心从 zksync-era 扩展为多仓库栈：**ZKsync OS Server**（最活跃，404 PRs）/ ZKsync OS RISC-V 多 VM（EVM/EraVM/Wasm，146 PRs）/ Airbender GPU 证明器（94 PRs）/ Gateway v31 互操作 + era-contracts（154 PRs）/ **Prividium** 企业隐私（本地开发环境已开源†，Docker Compose 全栈）/ native AA + SSO | **机构金融对标**；跨 5 组织 1,427 PRs |
| **StarkNet** | STARK 技术正统 + BTCFi/隐私应用连接 | **Sequencer/OS**（1,324 PRs，最高活跃度）/ Cairo 2.16→2.19 四版本发布（227 PRs）/ STWO Circle STARK 电路（223 PRs）/ 预确认 p2p 脚手架（pathfinder 已合并）/ v0.14.2 主网已激活（SNIP-36 链内 S-Two 证明验证）/ **BTCFi 叙事强但代码信号极弱**（strkBTC 仅 2 PRs/8 commits） | ZK 深度领先但非 EVM；BTCFi/STRK20 隐私资产仍在叙事→工程转化阶段 |
| **X Layer** | OKX 交易所分发 + Onchain OS + Agent 支付 | Exchange OS 白皮书 V1.0（双环境：X Layer EVM 治理 + TradeZone 300K TPS 撮合，**仅白皮书无生产部署**）/ APP Agent 支付协议（charge/escrow/session/upto 四类 intent，ERC-8183 参考实现）/ Agentic Wallet（TEE 安全，20+ 链，2026-03-18 上线）/ xlayer-reth 执行客户端（107 PRs）/ op-succinct SP1 ZK 证明 | 同为交易所背景 OP Stack L2；OKX 120M+ 用户；ICE $200M 投资 |

- **红色标注**：zkSync 已从单仓库演变为多仓库工程栈（OS Server + OS + Airbender + Gateway + Prividium），总活跃度（1,427 PRs）远超 era 单仓库（130 PRs）数据所暗示；Prividium 是机构金融赛道标杆，但目前为**本地开发环境，非生产部署证明**
- **黄色标注**：X Layer 叙事从「OP Stack 迁移」转向「交易所原生链」——Exchange OS + APP Agent 支付 + OKX 120M+ 用户分发；但 L2BEAT TVS 仅 $10.23M，Exchange OS 尚无生产实例
- † Prividium 本地环境含 Keycloak + Protected RPC + Admin Panel + zkSync OS + Sequencer + Prover + Block Explorer + Prometheus/Grafana
- \* "35+ 银行" 来自合作方 Cari Network 声称，非 zkSync 直接披露，未独立验证

**Design**
- **背景**：#0A0A0A
- **颜色**：表头白色，关注点列分色——机构金融 #00D395，ZK 深度 #4DA6FF，交易所 #FFA500；PR 数字 #4DA6FF
- **布局**：全宽表格 + 底部标注区域
- **图表类型**：四列数据表，关注点列带颜色标签
- **高亮方式**：zkSync 行用 #FF4444 左边框（红色标注），X Layer 行用 #FFA500 左边框（黄色标注）

---

### Slide 10 — L1 通用链叙事动态

| 竞品 | 核心方向 | 关键动向 | 对 Mantle 的竞争压力 |
|---|---|---|---|
| **Solana** | 高性能 consumer → PayFi/RWA/AI commerce 转型 | Alpenglow/Votor 新共识（BLS 聚合 + 亚秒终局，Q3 主网目标，仍在压力测试）/ 开发重心从 Solana Labs 迁移至 **Anza**（client/SDK）+ **Jito**（MEV/validator）双客户端分工 / Pay.sh 稳定币 Checkout（Google Cloud 合作，2026-05-05）/ Agave v4 发布 | 性能 + consumer 分发 + 支付 UX 组合压力；Solana 正在把零售流量与 PayFi/机构叙事连成一条线 |
| **Sui** | 可编程支付 + 组合金融 + BTC 托管 + 数据应用栈 | 协议级 **Gasless 稳定币转账**（7 币种白名单：USDC/USDSUI/SUI_USDE/USDY/FDUSD/AUSD/USDB，mainnet-v1.72.2 已上线，gasless_max_tps=300）/ DeepBook 现货+保证金（主网）/ **Hashi** BTC 机构托管（BitGo/FalconX/Ledger 等 6 家）/ Walrus 存储 + Seal 加密密钥 + MemWal / 新 VM 开发中 / RedotPay 集成（7M+ 用户） | 协议级免费 P2P 转账 + BTC 托管 + 数据栈打包成产品叙事；MystenLabs 跨组织 2,966 PRs（sui 主仓 1,151 PRs） |
| **BNB Chain** | BSC Go + reth 双客户端 + 超短出块迭代 | **Mendel 硬分叉**（2026-04-28 主网激活，对齐 Ethereum Osaka）/ Pasteur 硬分叉筹备（BEP-675 builder 出块 + BEP-682 验证者唯一性，实现 PR 仍 open）/ 250ms 出块目标（BEP-670 spec 已合并，**无实现 PR**，当前 450ms）/ reth v0.0.9-beta 双客户端（~5-6 人团队）/ **opBNB 实质废弃**（1 名开发者，90 天 0 合并 PR）/ Greenfield 维护模式（2 维护者）/ AI Agent 叙事量大但代码弱（bnbchain-mcp 89% PR 关闭率） | 交易所流量 + BSC 出块性能持续迭代；但 opBNB/Greenfield 已边缘化，「全栈」叙事名不副实 |

- **要点**：L1 通用链的威胁不是单一维度——Solana 把 consumer + PayFi + 机构连成一条线，Sui 把协议级支付 UX + BTC 托管 + 数据栈打包成产品，BNB Chain 靠交易所流量但技术栈实际在收缩（opBNB/Greenfield 边缘化，核心团队仅 ~15 人）

**Design**
- **背景**：#0A0A0A
- **颜色**：表头白色，竞争压力列 #FF4444，关键动向数据 #4DA6FF
- **布局**：全宽四列表格（占 60%），底部要点区域双行
- **图表类型**：四列对比表，左侧带链 logo
- **高亮方式**：竞争压力列统一红色文字，强调威胁性；关键数据（PR 数、TPS 上限等）用 #4DA6FF

---

### Slide 11 — L1 垂直链：赛道已有原生占位者

> 设计意图：Slides 8-10 全部使用表格，此 Slide 切换为三卡片布局打破视觉疲劳，同时用 Chapter 3 方向色（Payment 橙 / 机构绿）预告后续评估

- **三张 Profile Card**（横排等宽，各占 ~30%）：

  **Card 1 — Tempo** `🟠 Payment`
  - **定位**：Stripe/Paradigm 孵化 · 支付专用 L1
  - **标志性进展**（大号文字）：**Visa 运行验证节点**（2026-04-14）
  - **技术快照**：
    - T4 硬分叉 2026-05-18 主网激活 / Payment Lane v2 安全分类收紧
    - MPP 机器支付协议已上线 / Commonware BFT ~600ms 终局目标
    - ⚠️ Zones 企业隐私仍在测试网（proof stub，非生产就绪）
  - **商业信号**：
    - Visa SDK 对接自主代理支付
    - 合作伙伴生态扩展中（生产集成深度未验证）
  - **状态**：`🟢 Mainnet`（T4 硬分叉已激活）

  **Card 2 — Circle Arc** `🟠 Payment`
  - **定位**：USDC 发行方自建 · 全栈金融 OS L1
  - **标志性进展**（大号文字）：**$222M 预售 / $3B FDV**（2026-05-11）
  - **技术快照**：
    - Malachite BFT ~780ms 终局 / USDC 原生 Gas + EWMA 费用平滑
    - CCTP V2 跨链 26 域 / 累计 $126B（YoY +740%）——**结构性垄断**
    - StableFX 机构 FX 引擎 / 8 国 Partner Stablecoins
  - **商业信号**：
    - a16z $75M 领投 + **BlackRock/Apollo/ICE/Standard Chartered** 参投
    - 测试网 244.1M 交易 / 100+ 机构参与 / 1,200+ 开发者黑客松
    - Circle Q1 营收 $694M / USDC 流通 $77B
  - **状态**：`🟠 Testnet`（主网 2026 夏季预期，尚未上线）

  **Card 3 — Canton** `🟢 Institutional`
  - **定位**：Daml + Need-to-Know 隐私 · 企业结算网络
  - **标志性进展**（大号文字）：**DTCC 2026H1 受控生产 MVP**
  - **技术快照**：
    - Global Synchronizer 公共互操作层已运行 / 测试网 244M+ 交易
    - Reassignment Protocol 跨 Synchronizer 合约迁移
    - Need-to-know 隐私：Sequencer/Mediator 均不可见交易明文
  - **商业信号**：
    - **Broadridge DLR $368B/日**回购结算（月近 $8T）
    - JPMD/Kinexys 存款合作意向（分阶段 2026，**尚未部署**）
    - HQLAX 战略投资 + 迁移计划（待 CSSF 批准）/ **Chainlink** 数据层上线
  - **状态**：`🟢 Mainnet`（Global Synchronizer 运行中）

- **底部警示条**（全宽）：三条垂直链在 2026 Q1-Q2 密集推进——**赛道不是空白，原生竞争者已从架构层做场景优化，通用 L2 后发难以追赶**

**Design**
- **背景**：#0A0A0A
- **颜色**：卡片标题白色，方向标签 Payment #FFA500 / Institutional #00D395，标志性进展 #FFFFFF 1.2x 字号加粗，技术数据 #4DA6FF，机构名（Visa/BlackRock/DTCC/Broadridge）#FFFFFF 加粗，状态 badge 文字 #0A0A0A，⚠️ 未就绪标注 #FFA500
- **布局**：三等宽卡片横排（各 ~30%，卡片间 5% 间距），卡片占页面 75% 垂直区域；底部警示条占 25%
- **图表类型**：三列 Profile Card（非表格），底部全宽警示条
- **卡片样式**：底色 #1A1A1A，圆角 8px，顶部 2px 色带——Tempo/Arc 用 #FFA500（Payment 方向色），Canton 用 #00D395（机构方向色）；卡片内部分区用 0.5px #333333 分隔线
- **状态 badge**：圆角药丸形——Mainnet = #00D395 底色 / Testnet = #FFA500 底色，文字 #0A0A0A
- **高亮方式**：底部警示条用 #FF4444 左边框 + #1A1A1A 底色（与 Slide 4 底部警示条风格一致）；「尚未上线」「非生产就绪」「尚未部署」用 #FFA500 文字标注

---

### Slide 12 — Chapter 2 关键发现

- **四个结论**（编号，逻辑递进）：
  1. **通用平台路线已无 Mantle 的位置** → L2 平台化路线已被先行者占据：Optimism 以 Superchain 定义 OP Stack 生态（op-reth/kona 迁移主导 + op-supervisor 互操作，1,202 PRs），Arbitrum 以 Orbit 可定制 Nitro stack 覆盖应用链市场（BoLD/Timeboost/Stylus）。Base 在 Coinbase 120M+ 用户基础上选择从 OP Stack 独立——构建 base-reth + base-consensus 自有技术栈（1,810 PRs），正是因为 OP Stack 本身无法提供差异化。Mantle 同为 OP Stack L2，既非 Stack 提供者，也无百万级 DAU 支撑独立技术栈投入（当前 DAU ~1.6K），通用平台路线不可行
  2. **交易所分发未能有效转化为链上生态** → 三个交易所背景 L2 均证实交易所用户基数 ≠ DeFi 链上活跃度：**OKX**（120M+ 用户）支持 X Layer，DeFiLlama TVL 仅 $91M；**Bitget**（120M+ 用户）将 440M BGB 代币迁移至 Morph 作为 gas/治理代币，Morph TVL 仅 ~$8.9M；**Bybit** Alpha 2026-03-10 集成 Mantle 后，Fluxion（Mantle 原生 DEX、首批流动性合作方）TVL 从 $448K 缓慢增长至 ~$2.55M——对比 Base（Coinbase 同为 120M+ 用户）TVL $4.3B，说明链上生态增长的关键不是交易所导流，而是产品与技术栈的差异化
  3. **垂直赛道已有原生竞争者从架构层占位** → 支付方向有 Tempo（T4 硬分叉主网激活 + Visa 验证节点 + Payment Lane 协议级设计）和 Arc（$222M 预售 + CCTP $126B 不可复制跨链优势 + BlackRock/ICE 投资方）；企业/RWA 方向有 Canton（DTCC 2026H1 生产 MVP + need-to-know 隐私 + Chainlink 数据层 + Broadridge $368B/日结算）——这些链从共识层、blockspace 设计到合规预编译都针对特定场景优化，通用 L2 后发难以追赶
  4. **竞争窗口正在快速收窄** → 2026 Q1-Q2 各赛道密集推进：Tempo 主网持续迭代 + Visa 验证节点落地，Arc $222M 预售冲刺夏季主网，Canton 连续签约 DTCC/JPMD/HQLAX，zkSync Prividium 已开源但仍为本地开发环境。成功的链都在从基础设施层做场景化设计——Mantle 需要选择方向并做同等深度的基础设施投入，但选哪个方向需要系统评估
- **过渡句**：「平台化走不了，交易所导流不够，垂直赛道有人占，窗口还在收窄——Mantle 应该往哪个方向走？接下来我们逐一评估三个候选方向」

**Design**
- **背景**：#0A0A0A
- **颜色**：第 1/2 条 #FF4444（否定），第 3 条 #FFA500（警示），第 4 条 #4DA6FF（分析/中性），文字白色
- **布局**：四行，每行左侧图标（✗ / ✗ / ⚠ / ⏳），右侧文字描述；每条结论下方用小字列出关键证据数据
- **图表类型**：图标列表（逻辑递进）+ 证据子行
- **高亮方式**：第 1/2 行 #FF4444 左边框；第 3 行 #FFA500 左边框；第 4 行 #4DA6FF 左边框；关键对比数据（$2.55M vs $4.3B / $8.9M / $91M）用对应颜色高亮

---

## Chapter 3: 三个叙事方向的深度分析

> 演讲目标：通过案例和数据，帮助团队理解三个候选方向的市场、竞争和技术全貌

### Slide 13 — 评估框架

- **分析结构**：每个方向按「市场格局 → 技术前提 → 行业案例」三步展开
- **三个候选方向**（颜色编码）：
  - 🔵 AgentFi — AI Agent 经济基础设施
  - 🟠 Payment Chain — 稳定币支付专用链
  - 🟢 机构金融 — 合规隐私与企业结算
- **目标**：全面理解每个方向的机会与挑战，为 Mantle 叙事决策提供依据

**Design**
- **背景**：#0A0A0A
- **颜色**：方向名颜色编码——AgentFi #4DA6FF / Payment #FFA500 / 机构金融 #00D395
- **布局**：左侧三步分析流程（纵向箭头），右侧三个方向标签横排
- **图表类型**：分析流程图 + 颜色编码方向标签
- **高亮方式**：三个方向标签等权重呈现，均为描边样式

---

### Slide 14 — AgentFi：市场格局与技术前提

- **市场现状**：
  - CoinGecko AI Agents 分类：**$3.68B** 市值 / $538M 24h 成交额
  - 加密 AI Agent 赛道整体 ~$2.3-2.6B（多家估算）
  - **阶段判断**：代币投机 > 真实使用——仍处早期/概念验证阶段
  - 真实使用信号：x402 Discovery **50,566 资源** / **72,141 独立付费方** / L30 **326,224 次调用**
- **主要竞品**：

| 竞品 | 核心能力 | 竞争优势 |
|---|---|---|
| **Base** | AgentKit + x402 + Base MCP + Agentic Wallets | Coinbase 120M+ 用户分发 + 四层垂直整合 |
| **Solana** | pay-kit/MPP + Token Extensions + SVM 低延迟 | 低费 + 支付 UX + Agent 微支付适配 |
| **X Layer** | APP Agent 支付协议 + Agentic Wallet (TEE) | OKX 120M+ 交易所分发 |

- **六层基础设施前提**（链要支撑 AgentFi 需要什么？）：
  1. **标准化 AI 接口** — MCP server 或等效协议，让 AI 直接调用链上操作
  2. **Agent 钱包 + 权限管理** — AA + Session Keys + 策略引擎（链上执行，不依赖 Agent 端信任）
  3. **低延迟执行** — <500ms 确认，支撑 Agent 实时决策
  4. **机器间支付协议** — HTTP 原生微支付（如 x402），Agent 自主消费无需人工
  5. **DeFi 流动性** — 深度 DEX 支撑 Agent 财库管理和再平衡
  6. **Agent 发行平台** — 注册、代币化、交易市场

**Design**
- **背景**：#0A0A0A
- **颜色**：市场数据 #4DA6FF，竞品表头白色，六层编号 #4DA6FF
- **布局**：上部市场数据区（25%）+ 中部竞品表格（30%）+ 下部六层框架（45%，六列微型卡片横排）
- **图表类型**：数据卡 + 竞品对比表 + 六列基础设施卡片
- **高亮方式**：市场阶段判断用 #FFA500 标注「早期/概念验证」；六层卡片用 #4DA6FF 描边

---

### Slide 15 — 案例：Base AgentFi 生态

- **架构图**（四层垂直整合，从底向上）：
  - **图片文件**：`charts/slide15-base-agentfi-arch.png`
  - **使用方式**：置于 Slide 左侧 50% 区域，暗色背景无需额外处理，蓝色 (#4DA6FF) 主色调
  - **内容**：Layer 4 Base MCP（7 DeFi Plugins + OAuth 2.1）→ Layer 3 x402（HTTP 402 微支付）→ Layer 2 Agentic Wallets（TEE + Session Caps + Paymaster）→ Layer 1 CDP AgentKit（50+ TS / 30+ Python Actions）+ 底部基础设施（Flashblocks 200ms / Smart Wallet / Aerodrome）

- **生态分类与数据**：

| 类别 | 代表项目 | 关键数据 | 状态 |
|---|---|---|---|
| **Social Agent** | Clanker（Farcaster 自动发币）| 累计费用 >$50M / 558K 交易者 / 峰值日创建 21,870 token | 已被 Farcaster 收购 |
| **Agent 发行** | Virtuals Protocol | >18,000 Agent 部署 / 累计收入 >$75M / Base 第 2 大协议（按年收入 >$59M）| 已扩展至 Arbitrum/Solana |
| **Trading/DeFi** | 自主 DeFi Agent | 7×24 收益监控 + 自动再平衡 / 跨协议流动性管理 | 早期产品，多为 human-in-loop |
| **Gaming** | AWE 持久世界引擎 | 去中心化持久世界框架，Agent 协作/竞争/进化 | 早期探索，公开数据有限 |

- **关键洞察**：Base AgentFi 生态的核心竞争力不是单个协议，而是 Coinbase 分发 + 四层垂直整合的组合效应——开发者用 `npm create onchain-agent@latest` 即可获得钱包 + DeFi + 支付 + AI 接口全套能力
- **数据校准**：Agent 代币市值 $3.68B 为投机定价，真实经济活动远小于此——x402 是目前最接近生产级的 Agent 支付信号

**Design**
- **背景**：#0A0A0A
- **颜色**：架构层名 #4DA6FF，数据 #FFFFFF，生态分类标题按类别分色
- **布局**：左侧 50% 为四层架构图（从底向上堆叠），右侧 50% 为生态分类表格 + 关键数据
- **图表类型**：垂直堆叠架构图（四层 + 基础设施底座）+ 四行生态分类表
- **高亮方式**：架构图每层用不同深浅的 #4DA6FF 渐变填充；生态表 Social 行高亮（数据最强）

---

### Slide 16 — Payment Chain：市场格局与技术前提

- **市场现状**：
  - 全球稳定币供给：**$320.7B**（DefiLlama）
  - USDC Q1 2026 链上交易量：**$21.5T**（+263% YoY）
  - **关键区分**：链上交易量 ≠ 真实支付——真实稳定币支付年化仅 ~$390B，渗透率 **0.02%**
  - 跨境支付 TAM：**$179T**（McKinsey）；全球汇款平均成本 **6.36%**（World Bank）
- **主要竞品**：

| 竞品 | 定位 | 核心优势 |
|---|---|---|
| **Tempo** | 支付优先 L1（Stripe/Paradigm） | Payment Lane 协议级 blockspace + TIP-20 预编译 + Visa 验证节点 |
| **Circle Arc** | USDC 发行方金融 OS（Circle） | USDC 原生发行 + CCTP V2 跨链 + StableFX + $222M 预售 |
| **Sui** | 协议级免费 P2P（MystenLabs） | Gasless 7 币种白名单 + Move 对象安全 + RedotPay 7M+ 用户 |

- **六维技术框架**（Payment Chain ≠ 在通用链上部署支付合约）：
  1. **确定性终局** — BFT 亚秒不可重组（非 L2 soft confirmation）
  2. **费用确定性** — 稳定币计价，可预测或用户不可见
  3. **支付专用 blockspace** — 保留容量，不被 DeFi/NFT 挤出
  4. **稳定币原生支持** — 协议级 memo / 合规策略 / fee eligibility
  5. **跨链互操作** — 安全低延迟 burn-and-mint（非桥接资产）
  6. **合规基础设施** — 链级 transfer policy 执行（非应用层合约）
- **核心洞察**：支付需要 Web2 分发（Stripe/Visa/Circle 网络），纯 crypto 方案很难 mass adoption

**Design**
- **背景**：#0A0A0A
- **颜色**：市场数据 #FFA500，竞品表头白色，六维编号 #FFA500
- **布局**：上部市场数据区（25%）+ 中部竞品表格（25%）+ 下部六维框架（40%，六列微型卡片）+ 底部洞察（10%）
- **图表类型**：数据卡 + 竞品对比表 + 六列基础设施卡片
- **高亮方式**：「0.02% 渗透率」用 #FF4444 强调巨大差距；六维卡片用 #FFA500 描边

---

### Slide 17 — 案例：Tempo 支付链架构

- **架构图**（高层级交易流程）：
  - **图片文件**：`charts/slide17-tempo-arch.png`
  - **使用方式**：置于 Slide 左侧 55% 区域，暗色背景直接适配，橙色 (#FFA500) 主色调，Payment Lane 层以绿色 (#00D395) 高亮标注核心创新
  - **内容**：自上而下交易流程——Users/Merchants → TempoTxEnvelope → L1 TIP-403 合规策略 → L2 Payment Lane 三分区（System/Payment/General，标注 "CORE INNOVATION"）→ L3 TIP-20 预编译 Token → L4 Reth EVM 执行层 → L5 Commonware Simplex BFT → Optional Enterprise Zones

- **关键技术创新**：
  - **Payment Lane**：通过 `general_gas_limit` 硬约束非支付交易 gas 容量——即使 DeFi 拥堵，支付交易仍有保留 blockspace
  - **TIP-20 预编译**：非 ERC-20 合约，而是协议级 token 标准——固定 6 位精度、原生 memo 字段（支付对账必需）、pause/role-based 权限、fee eligibility、Payment Lane 集成
  - **稳定币 Gas**：attodollars 计价，固定基础费，50,000 gas TIP-20 转账 ≈ **$0.001**——无需持有原生代币
  - **账户体验**：P256/WebAuthn/Passkey 支持 + Access Keys（限额+时间窗口）+ 交易批处理 + Fee Payer 代付
- **六维覆盖**：✅ 终局 ✅ 费用确定 ✅ 支付 blockspace ✅ 稳定币原生 ❌ **跨链互操作** ✅ 合规
- **⚠️ 注意**：性能数据为设计目标，生产 SLA 待独立验证；Visa 2026-04-14 宣布运行 Tempo 验证节点

**Design**
- **背景**：#0A0A0A
- **颜色**：架构层名 #FFA500，Payment Lane 高亮 #00D395，六维打勾 #00D395 / 打叉 #FF4444
- **布局**：左侧 55% 为垂直架构图（六层堆叠），右侧 45% 为关键创新要点 + 六维覆盖状态
- **图表类型**：垂直堆叠架构图 + 六维状态指示器（打勾/打叉）
- **高亮方式**：Payment Lane 层用 #00D395 描边突出（核心差异化）；跨链互操作缺失用 #FF4444 标注

---

### Slide 18 — 案例：Circle Arc 金融 OS 架构

- **架构图**（高层级平台栈）：
  - **图片文件**：`charts/slide18-arc-arch.png`
  - **使用方式**：置于 Slide 左侧 55% 区域，暗色背景直接适配，橙色 (#FFA500) 主色调，协议服务层以绿色 (#00D395) 高亮标注核心差异化
  - **内容**：五层平台栈——L5 Applications（DeFi/Payments/Capital Markets/Agentic Commerce）→ L4 Developer Kits（App Kits/Build with AI/Smart Contracts/Nanopayments SDK）→ L3 Protocol Services（CCTP V2/Wallets/StableFX/CPN/Paymaster/Nanopayments，标注 "CORE DIFFERENTIATOR"）→ L2 Assets（USDC/8 Partner Stablecoins/ARC Token）→ L1 Arc Core（Malachite BFT/USDC Gas/EVM/Privacy/Validators）

- **关键技术创新**：
  - **USDC 原生 Gas**：USDC 为协议级 gas 代币 + EWMA 费用平滑（抑制需求尖峰）+ Paymaster 多币种自动换汇——机构可精确预测成本，无波动性原生代币
  - **CCTP V2**：Circle 原生跨链 USDC，**26 个域 / 累计 $126B / YoY +740%**——这是 Circle 发行方地位带来的**结构性优势，第三方链不可复制**
  - **StableFX**：机构 FX 引擎——RFQ 多报价执行 + 原子链上结算 + 可编程结算窗口/净额 + **8 国 Partner Stablecoins**（覆盖巴西/韩国/菲律宾/澳大利亚/墨西哥/日本/加拿大/南非）
  - **可选隐私**：L1 级 confidential transfers（屏蔽金额，保留地址）+ TEE + view keys（审计只读）
  - **验证者**：PoA 许可制，**100+ 机构测试网参与者**（BlackRock/Goldman Sachs/Mastercard/State Street/Visa/AWS/Coinbase/Kraken）
- **融资与里程碑**：**$222M ARC Token 预售 / $3B FDV**（Circle Q1 2026 官方披露，a16z 领投 $75M）；testnet **244.1M 交易**（截至 2026-05-05）；主网 **2026 夏季**预期（尚未上线）
- **六维覆盖**：✅ 终局 ✅ 费用确定 ❌ **支付 blockspace** ✅ 稳定币原生 ✅ 跨链互操作 ✅ 合规
- **Tempo vs Arc 核心差异**：Tempo 优化支付交易管道（Payment Lane + 固定费 + 预编译 token），Arc 构建全栈金融 OS（USDC 原生发行 + CCTP 跨链 + StableFX FX + 机构验证者）——Tempo 缺跨链；Arc 缺 Payment Lane

**Design**
- **背景**：#0A0A0A
- **颜色**：架构层名 #FFA500，CCTP/StableFX 高亮 #00D395，六维打勾 #00D395 / 打叉 #FF4444
- **布局**：左侧 55% 为垂直平台栈架构图（五层），右侧 45% 为关键创新要点 + 六维覆盖 + Tempo vs Arc 对比
- **图表类型**：垂直堆叠平台栈 + 六维状态指示器 + 底部 Tempo vs Arc 双列对比卡
- **高亮方式**：协议服务层用 #00D395 描边突出（核心差异化）；支付 blockspace 缺失用 #FF4444 标注

---

### Slide 19 — 机构金融：市场机会与监管催化

- **市场数据**：
  - 链上 RWA（非稳定币）：**$31-34B**（2026-05），YoY **>200%**
  - 含稳定币的广义数字资产结算规模：**>$400B**
  - 集中在低风险资产：美国国债 $15B+ / 大宗商品 $7B+ / 资产支持信贷 $2.3B+
  - **阶段判断**：机构试点 → 规模化早期（尚非主流采用）
- **机构需求**（不是低费 + 高 TPS，而是）：
  - **合规** — KYC/KYB/AML/Travel Rule，谁能进来、谁能交易
  - **隐私** — 交易数据谁能看、看多少、怎么证明不多看
  - **数据主权** — 数据存在哪、谁控制、能否删除
  - **审计** — 监管方怎么观察、怎么导出、怎么验证
  - **工作流** — 托管/抵押品/DvP/结算/对账，不是单笔转账
- **监管催化剂**：
  - 🇺🇸 **GENIUS Act** 签署——稳定币监管框架落地
  - 🇺🇸 **SEC 2026-01-28 声明**：代币化证券 = 证券，所有合规角色（transfer agent/broker-dealer/custody）仍然适用
  - 🇪🇺 **MiCA** 统一框架
  - 🌐 **FATF Travel Rule** — 要求 VASP 传输交易双方身份信息
- **三种已验证/探索中的模式**：
  - zkSync Prividium — "**Prove-Not-Reveal**"：整链对外不可见，ZK 证明保证正确性
  - Canton — "**Need-to-Know**"：子交易级投影，每方只看到与自己相关的部分
  - Paladin — "**Pluggable Sidecar**"：不改链、多隐私域共存，按场景选择信任模型

**Design**
- **背景**：#0A0A0A
- **颜色**：RWA 增长数字 #00D395，机构需求图标白色，监管标签按国旗分色，两种模式 #4DA6FF / #00D395
- **布局**：上部 RWA 增长曲线（30%）+ 中部需求图标五宫格（30%）+ 下部监管催化 + 两种模式标签（40%）
- **图表类型**：RWA 增长面积图 + 需求图标卡片 + 监管标签列表 + 双模式对比标签
- **高亮方式**：>200% YoY 用 #00D395 加大强调；需求列表中「合规」和「隐私」用白色加粗

---

### Slide 20 — 案例：zkSync Prividium — "Prove-Not-Reveal" 企业隐私

- **架构图**（端到端结算路径）：
  - **图片文件**：`charts/slide20-prividium-arch.png`
  - **使用方式**：居中占页面 60%，暗色背景直接适配，绿色 (#00D395) 主色调，含信任边界虚线分隔私有链与 L1
  - **内容**：自上而下结算路径——Institutional Users → IdP (Keycloak, Okta OIDC/SIWE) → Proxy RPC Gateway（三步验证：JWT/Wallet/Permission）→ Sequencer 私有执行（PostgreSQL + Blob Store）→ Prover (Airbender GPU, STARK) → ZKsync Gateway → **Trust Boundary 虚线** → Ethereum L1（仅 state root + STARK proof）；左侧含四层准入控制侧栏（Identity Auth / Proxy RPC GW / RBAC Permissions / L1 TxFilterer）

- **核心理念**：**整链对外不可见**——这不是额外功能，而是 Validium 架构的固有特性。L1 仅看到状态根 + STARK 验证结果，零交易数据泄露。运营方可见全部数据（可作为审计资产）
- **四层准入控制**：
  1. **身份认证** — Okta SSO / SIWE / 多钱包支持
  2. **Proxy RPC 网关** — 三步验证 + 审计日志（标准 RPC 端点保持私有）
  3. **RBAC 权限** — Admin Dashboard 管理用户/角色/权限，合约函数级粒度，**无需改代码**
  4. **L1 TransactionFilterer** — 链上白名单过滤强制交易路径
- **开发环境**：本地 Docker Compose 全栈已开源（`local-prividium`）——含 Protected RPC / Keycloak / Admin Panel / zkSync OS / Sequencer / Prover / Block Explorer / Prometheus+Grafana
- **机构采用信号**：Cari Network（5 家美国区域银行，合计存款 >$600B，目标 2026 Q3 试点）/ Deutsche Bank 确认合作 / BitGo 机构托管
- **关键论点**：Prividium 的价值核心是**合规和准入控制，不是 ZK 证明本身**——合规 RPC + RBAC + 审计就已经解决了机构最关心的问题；ZK 只是隐私保证的实现手段
- \* "35+ 银行" 来自合作方 Cari Network 声称，非 zkSync 直接披露，未独立验证

**Design**
- **背景**：#0A0A0A
- **颜色**：架构组件名 #00D395，数据流箭头白色，信任边界 #00D395 虚线
- **布局**：中央为垂直结算路径架构图（占页面 60%），左侧为四层准入控制堆叠卡片（20%），右侧为机构采用信号列表（20%）
- **图表类型**：垂直结算流程图 + 准入控制层级图 + 采用信号列表
- **高亮方式**：「仅状态根+证明」出口处用 #00D395 虚线框标注信任边界；Proxy RPC 三步验证用编号圆点

---

### Slide 21 — 案例：Canton — "Need-to-Know" 机构工作流网络

- **架构图**（参与者模型）：
  - **图片文件**：`charts/slide21-canton-arch.png`
  - **使用方式**：占页面上部 55%，暗色背景直接适配，绿色 (#00D395) 主色调，三个 Participant 分色（A: #4DA6FF / B: #FFA500 / C: #8C8DFC）
  - **内容**：四层结构——Application Layer（DvP/Repo/Collateral/Bond）→ Participant Layer（Alice Bank / Bob Fund / Regulator，各自维护 Local ACS，标注 "Only sees own contracts"）→ Synchronizer（Sequencer 排序加密消息 + Mediator 2PC 确认聚合，均标注 "Cannot see plaintext/contract content"）→ Global Synchronizer（Super Validators / Governance / Canton Coin）；右侧含 DvP Visibility Matrix 表格和 Key Privacy Guarantees 列表

- **核心理念**：**没有任何一个节点持有完整全局状态**——每个 Participant 只维护与自身 Party 相关的合约/投影。Synchronizer 排序加密消息但看不到明文，Mediator 聚合确认信号但看不到合约内容
- **Daml 合约模型**（为金融工作流设计）：
  - **signatory** — 必须授权创建合约的一方（代表义务/责任）
  - **observer** — 可看到合约但不授权创建（用于监管/审计/托管）
  - **controller** — 被授权执行合约 choice 的一方
  - **consume-create 模式** — 合约不可变；「修改」= 归档旧合约 + 创建新合约（天然审计轨迹）
- **隐私可视性示例**（一笔 DvP 交易中各方看到什么）：

| 角色 | 能看到 | 看不到 |
|---|---|---|
| Alice（买方） | 自己的资产转移 + 必要对手方输出 | 其他客户的合约 |
| Bob（卖方） | 自己的资产转移 + 必要对手方输出 | Alice 的内部详情 |
| Bank 1 | 自行发行资产的转移投影 | 交易原因、对手方细节 |
| 监管方 | 被显式设为 Observer 的合约 | 未授权的交易 |

- **机构生产验证**：
  - **Broadridge DLR**：日均 **$368B** / 月近 **$8T** 回购结算（2026-04 官方数据）
  - **HSBC Orion**：债券生命周期/结算/回购，4 支数字债券，结算从 T+5 改善至 T+1
  - **Goldman Sachs DAP**：多资产代币化和结算，报告 <60 秒结算
  - **DTCC**：2026H1 控制生产 MVP，DTC 托管的美国国债代币化
- **关键洞察**：机构采用需要的是**工作流级别的设计**（谁能看什么、怎么授权、怎么审计），不是给通用链加几个 enterprise feature
- ⚠️ 机构指标口径和日期不一，需按 source-attributed 处理；「$6T+ 资产上链 / 600+ 机构」为供应商声称

**Design**
- **背景**：#0A0A0A
- **颜色**：架构组件名 #00D395，Participant 分色（A #4DA6FF / B #FFA500 / C #8C8DFC），Daml 关键词 #FFFFFF 加粗
- **布局**：上部 55% 为参与者模型架构图，下部左侧 DvP 可视性表格（25%），下部右侧机构采用列表（20%）
- **图表类型**：分层参与者架构图 + 可视性对比表 + 采用案例列表
- **高亮方式**：每个 Participant 用不同颜色标注「只看到自己相关的合约」；Broadridge $368B/日用 #00D395 加大

---

### Slide 22 — 案例：Paladin — "Pluggable Privacy Sidecar" 可插拔隐私运行时

- **架构图**（三层组件架构）：
  - **图片文件**：`charts/slide22-paladin-arch.png`
  - **使用方式**：置于 Slide 左侧 55% 区域，暗色背景直接适配，绿色 (#00D395) 主色调
  - **内容**：三层结构——Layer A Base EVM Chain（EVM Executor / P2P Consensus / Tx Mempool / Block Storage / State Trie，不修改底层链）→ Plugin Boundary（gRPC Bidirectional Streaming）→ Layer B Paladin Runtime（TXManager / Sequencer / StateManager / KeyManager / Transport / BlockIndexer，JVM + Go 混合运行时）→ Layer C Private EVM（Pente ephemeral Besu EVM，按需实例化执行私有 Solidity 合约）

- **核心理念**：**隐私作为 Sidecar，不是链的分叉**——Paladin 不修改底层 EVM 客户端，而是作为独立进程运行在标准 EVM 旁边，通过 JSON-RPC/WS 交互。链上只存 hash/commitment/nullifier/签名验证结果，所有业务明文留在 Paladin 节点间私有分发
- **三种隐私域**（不同信任模型共享同一运行时）：

| 域 | 信任锚 | 机制 | 适用场景 |
|---|---|---|---|
| **Noto** | Notary（指定可信背书方） | Confidential UTXO + 链上 opaque state ID + notary 签名 | 受控发行、银行存款 token、托管资产 |
| **Zeto** | ZKP（Groth16 数学证明） | Commitment + Nullifier + SMT + 链上 proof 验证 | KYC-gated 私密转账、历史隐藏资产 |
| **Pente** | Privacy Group（N-of-N 全员重放） | 临时 Besu EVM + EIP-712 签名 + externalCalls | 私有智能合约、债券生命周期、合规审批 |

- **企业级关键能力**：
  - **Private Groups**：Pente 支持 2-10 方组建私有合约组——组内全员执行、组外不可见状态，salt-masked identity 防止链上身份映射
  - **原子 DvP 结算（Atom）**：跨域原子交换——Noto 债券 + Zeto 现金在单笔 EVM 交易中同时结算，任一失败全部 revert
  - **五阶段交易流**：Init（身份解析）→ Assemble（UTXO 选择 + 证明生成）→ Endorse（notary/ZKP/组签名）→ Prepare（编码 EVM calldata）→ Submit（公共交易提交）
  - **KYC 合规**：Zeto 的 `AnonNullifierKyc` 变体在 ZKP 内验证 KYC SMT membership，证明交易方属于合规集合而不暴露真实身份

- **与 Prividium / Canton 的对比**：

| 维度 | Prividium | Canton | Paladin |
|---|---|---|---|
| **隐私模型** | 整链隐私（Validium 固有特性） | 子交易级投影（need-to-know） | 可插拔多域（Noto/Zeto/Pente 按场景选） |
| **与底层链的关系** | **是链本身**——zkSync OS 即隐私链 | **是链本身**——Daml + Global Synchronizer | **Sidecar**——不修改底层 EVM，JSON-RPC 旁挂 |
| **部署方式** | 部署一条新的 Validium 链 | 部署 Canton 网络 + Daml runtime | 在已有 EVM 旁运行 Paladin 进程 |
| **Mantle 适配成本** | 需要运行 zkSync OS 技术栈（与 OP Stack 无关） | 需要运行 Daml/Canton 全栈（非 EVM 体系） | 理论上可旁挂 op-geth，复用现有 L2 |
| **核心优势** | ZK 证明保证正确性 / 零数据泄露 / 已有机构信号 | 工作流级隐私 / 生产验证（Broadridge $368B/日） | **最轻量集成路径**——不换链、不换栈、渐进式引入隐私能力 |

- **Paladin 对 Mantle 的核心价值**：Prividium 和 Canton 都要求「换一条链」，而 Paladin 是唯一能作为**现有 EVM 链的隐私附加层**的方案——这意味着 Mantle 可以不改底层架构、不迁移资产、不放弃 DeFi composability，就能渐进式获得企业隐私能力

- **关键风险与限制**：
  - **Besu 绑定**：Paladin 与 Besu 同属 LFDT（Linux Foundation Decentralized Trust），Layer C 的 Pente 直接嵌入 Besu Java EVM 库。**Mantle 执行层是 geth/reth 体系，不可能再维护第三个 EVM 客户端**——如果要在 Mantle L2 上原生运行 Pente，需要将 ephemeral EVM 从 Besu 替换为 geth 或 revm，涉及 PenteDomain、evm_runner、statedb 适配层的重实现
  - **协议成熟度**：Pente 组成员不可变（类似早期状态通道）、Groth16 trusted setup、Go/Java 混合运行时复杂性、UTXO 状态膨胀均为已知限制；MPC 多方计算、合规原生设计等功能尚在路线图中
  - **生产验证缺失**：Prividium 有 Cari Network / Deutsche Bank 信号，Canton 有 Broadridge $368B/日生产验证——Paladin 尚无公开的机构生产部署案例

**Design**
- **背景**：#0A0A0A
- **颜色**：架构层名 #00D395，三域表头白色，域名分色——Noto #FFA500 / Zeto #4DA6FF / Pente #8C8DFC，集成路径表用 #00D395 描边
- **布局**：左侧 55% 为三层组件架构图（Layer A/B/C），右侧 45% 分为三域对比表（上 40%）+ 企业能力要点（中 30%）+ 集成路径对比（下 30%）
- **图表类型**：三层组件架构图 + 三域对比表 + 集成路径双列对比
- **高亮方式**：Plugin Boundary 用 #00D395 虚线标注（关键分离点）；「不修改底层链」用 #00D395 加粗；⚠️ 限制用 #FFA500 标注

---

### Slide 23 — 三方向全面评估

| 维度 | AgentFi | Payment Chain | 机构金融 |
|---|---|---|---|
| **市场规模** | $3.68B（代币市值，非真实 TAM）| $320.7B 稳定币供给 / $179T 跨境 TAM / 0.02% 渗透率 | $31-34B RWA / >200% YoY |
| **市场阶段** | 早期投机 → 概念验证 | 快速增长，原生竞争者已占位 | 试点 → 规模化早期 |
| **竞争强度** | Base 四层整合 + Coinbase 分发构成不可复制优势 | Tempo + Arc 从架构层针对支付优化，CCTP 结构性垄断 | 仅 zkSync Prividium（本地开发环境），窗口期存在 |
| **Mantle 已有基础** | EVM + 第三方 AA（Etherspot/Particle）| 稳定币 $557.8M（USDT/USDe/USDC）| MI4/Securitize + USDY + mETH/cmETH 收益生态 + ~$4B 国库 |
| **Mantle 优势** | EVM 兼容 / mETH 支撑 Agent 财库 / DeFi 收益生态 | EVM 低费 / DeFi yield 支撑支付后资金管理 / Paymaster+AA 可快速实现 | EVM 生态 + Ethereum L2 合法性 / 收益资产（Tempo/Arc 没有）/ 国库规模 / Solidity 工具链 |
| **Mantle 挑战** | 六维均需从零补建 / 无 Coinbase 级分发 / 赛道早期不确定性高 | L2 soft confirmation ≠ BFT 终局 / CCTP 未列 Mantle / 无协议级稳定币支持 / 支付需要 Web2 分发 | 合规技术栈从零构建 / 无生产机构客户案例 / CCTP 缺失 |
| **技术路径** | MCP 接口 → Agent 钱包权限 → 发行平台 BD | Paymaster + Payment Intent SDK → Sequencer 支付标签 → CCTP 合作 | Compliance RPC → RBAC → Paladin Privacy Sidecar（或 Native 重建）→ Enterprise Zone/L3 |
| **关键风险** | 赛道可能停留在投机阶段；Base 先发优势难以逾越 | 纯支付链不占位，六维中三维为结构性差距 | 机构采用周期长；需要合作伙伴验证 |
| **可作为子场景** | Agent 财库管理可嵌入 DeFi/机构方向 | B2B 结算 + 财库层可嵌入机构金融方向 | — |

**Design**
- **背景**：#0A0A0A
- **颜色**：AgentFi 列 #4DA6FF，Payment 列 #FFA500，机构金融列 #00D395，表头白色
- **布局**：全宽十行四列对比表，等宽三列（不做视觉引导偏向）
- **图表类型**：彩色编码对比矩阵表
- **高亮方式**：三列等权重呈现；每列用对应颜色顶部色带标识；「可作为子场景」行用虚线分隔表示关联性

---

## Closing

### Slide 24 — 结论与下一步

- **核心发现**（三个编号要点）：
  1. **L2 赛道已进入差异化定位阶段** — 头部 L2 各有不可复制的结构性护城河（Base 分发、Arbitrum 金融工具链、Optimism Superchain、zkSync ZK+企业隐私），L1 通用链和垂直链同时压缩空间——Mantle 必须选择方向
  2. **三个候选方向各有机会与风险** — AgentFi 早期但 Base 先发优势极强；Payment Chain 增长快但原生竞争者已从架构层占位；机构金融增长最快且竞争窗口仍在，但需要从零构建合规技术栈
  3. **方向之间不是互斥的** — Agent 财库管理和 B2B 支付结算都可以作为更大叙事的子场景；关键是确定主叙事锚点，然后让其他方向围绕它展开
- **需要团队讨论的问题**：
  - Mantle 的主叙事锚点应该放在哪个方向？
  - op-geth EOL 迁移路径如何选择？
  - 是否有资源和意愿探索合规/隐私基础设施？

**Design**
- **背景**：#0A0A0A
- **颜色**：发现编号 #00D395，第三条白色，讨论问题 #A0A0A0
- **布局**：上部三条发现（编号列表，占 60%），底部讨论问题灰色区域（40%）
- **图表类型**：编号列表 + 底部讨论区
- **高亮方式**：第三条发现「不是互斥」用 #00D395 左边框强调

---

### Slide 25 — Q&A

- 预留 10 分钟讨论

**Design**
- **背景**：#0A0A0A，中央大号 "Q&A" 文字
- **颜色**："Q&A" #00D395
- **布局**：中央 Q&A 标题（占页面 60% 垂直区域），底部演讲者信息和日期
- **高亮方式**：Q&A 文字带微光效果
