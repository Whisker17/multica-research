# 20260605 内部分享 — Slides Outline (Final)

> 目标受众：Mantle 全公司工程团队
> 时长：~30 分钟（20 分钟演讲 + 10 分钟 Q&A）
> 核心论点：L2 赛道正从通用竞争转向垂直差异化，Mantle 应以「机构金融」为下一阶段叙事锚点
> 数据截止：2026-05-26

---

## Opening

### Slide 1 — 封面

- **标题**：Mantle 竞争格局与叙事方向分析
- **副标题**：20260605 bi-weekly 内部分享
- **演讲者信息**
- **设计**：Mantle 品牌色，简洁

---

### Slide 2 — 议程

- 三章结构概览，用连接词点明逻辑链：
  1. **现状**：市场发生了什么变化？→ Mantle 面临的挑战
  2. **竞品**：其他人在做什么？→ 竞争压力来自哪里
  3. **方向**：Mantle 应该怎么走？→ 三条路线的技术可行性评估
- **核心结论前置**（一句话）：机构金融是契合度最高的方向——以 zkSync Prividium 为对标，利用国库和收益生态优势构建合规技术栈
- **设计**：三列卡片 + 连接箭头

---

## Chapter 1: 当前市场现状分析

> 演讲目标：建立共识——市场环境已变，Mantle 需要新叙事

### Slide 3 — L2 赛道格局演变

- **数据图表**：5 链 TVL 柱状图（Arbitrum ~$15-17B / Base ~$11-13B / OP Mainnet ~$1.7-1.9B / Mantle ~$1.15-1.2B / zkSync ~$404M），标注市场份额
- **数据图表**：5 链 DAU 对比（Base 382K / Arbitrum 133K / OP 82K / zkSync 4K / Mantle 2.3K）
- **关键洞察文字**：
  - Arbitrum + Base 合计 ~77% L2 DeFi 流动性
  - EIP-4844 后费用竞争失去意义，新竞争维度：生态控制、分发、ZK/隐私、收益资产
  - 长尾 L2 使用量自 2025-06 下降 61%
- **数据来源标注**：DefiLlama / L2Beat / Nansen，2026-05-25 快照

---

### Slide 4 — 叙事转向：DeFi → RWA / 机构金融

- **左半**：DeFi 天花板
  - 全球 DeFi TVL $92-140B，远低于 $250B 预期
  - 83-95% 流动性闲置
  - Aave 59% 借贷市场份额
  - Blast 案例：TVL $2.7B → $55M（激励驱动的极端反面教材）
- **右半**：RWA 加速
  - 链上 RWA $31-34B（>200% YoY）
  - 美国国债代币化 $12.88-15B
  - BlackRock BUIDL ~$2.5B AUM（部署在 Arbitrum/Optimism，不在 Mantle）
  - BlackRock 2026-05 向 SEC 申请 $7B 货币市场基金上链
- **底部警示**：深层矛盾——Vitalik cypherpunk 隐私优先 vs 机构需要 KYC/许可制
- **数据来源标注**：RWA.xyz / DefiLlama / SEC filing

---

### Slide 5 — Mantle 当前定位与挑战

- **技术栈**：OP Stack based / Ethereum aligned / EigenDA / 标准方案
- **资产基本盘**：
  - mETH ~$925M TVL（第 4 大 ETH LST）
  - cmETH ~$515M TVL
  - 稳定币 ~$669M（峰值 $825M，81% 保留率）
- **活跃度困境**：
  - DAU Q1 2026 ~2,276（极端波动趋势图：37K → 12K → 53K → 5K → 2.3K）
  - 日收入 <$1K
- **新支柱（均早期）**：MI4 $400M / UR 银行 / MantleX / Aave V3
- **核心问题**（一句话）：TVL 部分恢复但用户持续流失，需要新叙事锚点

---

### Slide 6 — Chapter 1 小结

- **三个要点**：
  1. DeFi 必须守住但无法带动增长
  2. RWA/机构金融 >200% YoY——最快增长的链上叙事
  3. 合规基础设施成为新竞争维度（五链中仅 zkSync 有）
- **过渡句**：「市场在变，竞争对手在动——我们需要看看他们在做什么」
- **设计**：三个数字卡 + 箭头指向 Chapter 2

---

## Chapter 2: 竞争对手的开发与叙事分析

> 演讲目标：全景扫描竞争格局，识别威胁与机会

### Slide 7 — 竞品分析框架

- **三类竞争者矩阵**：
  - **L2 竞品**（同赛道直接竞争）：Base / Arbitrum / Optimism / zkSync / StarkNet / X Layer
  - **L1 通用链**（跨赛道替代竞争）：Solana / Sui / BNB Chain
  - **L1 垂直链**（新赛道抢位竞争）：Tempo / Circle Arc / Canton
- **分析维度说明**：近期代码活动（90 天 GitHub PR）+ 叙事方向变化
- **设计**：三行分组表 + 图标

---

### Slide 8 — L2 竞品：技术路线对比（上）

| 竞品 | 核心叙事 | 关键技术动向 | 90d PRs |
|---|---|---|---|
| **Base** | Coinbase 分发 + 独立 Stack | Azul 硬分叉 / Flashblocks 200ms / Beryl PolicyRegistry / x402 Agent | 1,810 |
| **Arbitrum** | 多 VM + 应用链 | Stylus/WASM / Orbit appchain / BoLD / Timeboost | 256 (Nitro) |
| **Optimism** | Superchain 互操作 | op-reth 迁移 / Interop 协议 / ZK dispute game / op-contracts v7 | 1,202 |

- **要点**：三家都在走「生态扩张/平台化」路线——Mantle 体量不够走这条路
- **口述提示**：Base 的 Coinbase 110M+ 用户分发不可复制

---

### Slide 9 — L2 竞品：技术路线对比（下）

| 竞品 | 核心叙事 | 关键技术动向 | 关注点 |
|---|---|---|---|
| **zkSync** | ZK 原生 + 企业隐私 | ZKsync OS (RISC-V) / Airbender / **Prividium** (35+ 银行*) | **机构金融对标** |
| **StarkNet** | 可证明计算 + Cairo | STWO 证明器 / appchains / 预确认 / BTCFi (弱代码信号) | ZK 深度领先但非 EVM |
| **X Layer** | 交易所分发 + Onchain OS | OP Stack 迁移 / Exchange OS / APP Agent 支付 | 同为交易所背景 L2 |

- **红色标注**：zkSync Prividium 是机构金融赛道的标杆
- **黄色标注**：X Layer 与 Mantle 同为交易所背景 OP Stack L2
- \* 35+ 银行为供应商声称，未独立验证

---

### Slide 10 — L1 通用链叙事动态

| 竞品 | 核心方向 | 对 Mantle 的竞争压力 |
|---|---|---|
| **Solana** | Alpenglow 新共识 + DePIN + 机构采用加速 | 性能+终局+支付 UX 组合压力 |
| **Sui** | Gasless 稳定币支付 + Move 安全 + Fireblocks | 协议级免费 P2P 转账已上线 |
| **BNB Chain** | Binance 全栈（BSC + opBNB + Greenfield）| 交易所流量 + 完整生态栈（opBNB 近弃用）|

- **要点**：L1 通用链在速度、生态和机构采用上全面加速——L2 不能只靠 Ethereum 安全性
- **口述提示**：Sui gasless 是协议层特性，非应用层补贴

---

### Slide 11 — L1 垂直链的冲击

- **支付/结算方向**：
  - **Tempo**：Stripe/Paradigm 孵化，Payment Lane / 稳定币 Gas / BFT ~600ms / 企业 Zones（proof 尚空）
  - **Circle Arc**：USDC 发行方自建 L1 / Malachite BFT / StableFX 跨币种 / CCTP V2 $126B 累计 / 100+ 测试网机构
- **企业/RWA 方向**：
  - **Canton**：Daml 合约 / need-to-know 隐私 / Broadridge DLR $368B/日 ~$8T/月 / DTCC 2026H1 MVP
- **核心警示**（红色框）：垂直赛道已有原生竞争者占位，从架构层就针对特定场景优化
- **口述提示**：这些链不是"也许"——Tempo 已有主网，Arc $222M 预售，Canton $8T/月结算

---

### Slide 12 — Chapter 2 关键发现

- **三个结论**（编号，逻辑递进）：
  1. **生态扩张路线** → Mantle 体量不够（DAU 2.3K vs Base 382K）
  2. **垂直赛道** → 已有原生竞争者（Tempo/Arc/Canton）占位，纯垂直链不现实
  3. **差异化切入点** → L2 + 合规基础设施——通用链和垂直链之间的位置
- **过渡句**：「那 Mantle 可以走哪条路？我们评估了三个方向」
- **设计**：三行，每行左边是 X 或 checkmark 图标

---

## Chapter 3: Mantle 叙事转移方向的技术分析

> 演讲目标：从技术角度评估三个叙事方向的可行性，给出明确推荐

### Slide 13 — 评估框架

- **四维评估**：市场规模 → 竞品格局 → 关键技术壁垒 → Mantle 适配性
- **三个候选方向**（颜色编码）：
  - AgentFi 🔴 弱
  - Payment Chain 🟡 中
  - 机构金融 🟢 强
- **判断标准**：技术可行性 x 市场空间 x Mantle 差异化优势
- **设计**：简洁方法论图，不占太多注意力

---

### Slide 14 — 方向一：AgentFi（契合度：弱）

| 维度 | 内容 |
|---|---|
| **市场阶段** | 早期/概念验证——CoinGecko AI Agents ~$3.68B 市值，但真实使用信号有限 |
| **竞品** | Base（x402 + Coinbase 分发）/ Solana（低费+pay-kit）/ Sui（gasless）/ X Layer（APP+Agentic Wallet）|
| **关键技术** | Agent 钱包/链上身份 / 低延迟+低 Gas / Agent 协作协议+支付通道 |
| **Mantle 优势** | EVM 兼容 / mETH/DeFi 收益生态支撑 Agent 财库 |
| **Mantle 缺失** | 无第一方 Agent SDK / 无 Paymaster / 无旗舰应用 / 无链上 Agent 活动数据 |
| **判断** | 🔴 **弱** — 赛道早期且竞争者众，Mantle 差异化壁垒有限 |

- **一句话总结**：AgentFi 是热门叙事，但 Mantle 没有结构性优势

---

### Slide 15 — 方向二：Payment Chain（契合度：中）

| 维度 | 内容 |
|---|---|
| **市场阶段** | 快速增长——稳定币供给 $320.7B / USDC Q1 $21.5T / 但渗透率仅 0.02% |
| **竞品** | Tempo（BFT + Payment Lane）/ Arc（USDC 发行方 + CCTP + StableFX）/ Sui（gasless）|
| **关键差距** | L2 软确认 ≠ BFT 硬终局 / **Circle CCTP 未列 Mantle** / 无商户网络 |
| **Mantle 优势** | DeFi 收益层——"支付后财库管理" / EVM/OP Stack 低迁移成本 |
| **判断** | 🟡 **中** — 纯支付链不占位，但 B2B 结算 + 财库层定位可行 |

- **补充**：支付需要 Web2 分发，纯 crypto 方案很难 mass adoption
- **注意**：Payment 作为机构金融的子场景仍然重要，不是完全放弃

---

### Slide 16 — 方向三：机构金融 — 市场机会

- **数据图表**：RWA 增长曲线——$6B (2025 初) → $31-34B (2026-05)，>200% YoY
- **机构需求清单**（四个图标）：合规 / 隐私 / 数据主权 / 审计
- **核心论点**：这不是「要不要做」，而是「谁先做好」
- **验证案例**：zkSync Prividium 已吸引 35+ 银行*，证明 L2 + 企业隐私模式可行
- **监管催化**：GENIUS Act 签署 / SEC 代币化证券声明 / MiCA / FATF
- \* 供应商声称

---

### Slide 17 — 方向三：机构金融 — 对标 zkSync Prividium

- **Prividium 架构图**：
  - ZK Validium + 企业隐私
  - Proxy RPC → RBAC 访问控制 → 私有 DA → STARK 证明 → L1 结算
  - 本地开发环境已开源（Docker Compose）
- **技术栈拆解**：
  - zkSync 原生：ZKsync OS / Airbender prover / RISC-V STF
  - 可在其他 L2 复现：Proxy RPC / RBAC / 私有 DA 层 / 合规策略引擎 / 审计日志
- **Mantle 路径**：OP Stack 框架下实现类似的合规隔离层
- **口述提示**：我们不需要复制 ZK 证明系统——合规和准入是 Prividium 的价值核心

---

### Slide 18 — 方向三：机构金融 — Mantle 合规技术栈路线图

- **技术差距矩阵**（核心 Slide）：

| 技术组件 | 当前状态 | 目标状态 | 实现路径 | 复杂度 |
|---|---|---|---|---|
| Validium 隐私 DA | 无（EigenDA）| 链下 DA + ZK 证明 | EigenDA 改造 | 高 |
| 合规执行层 | ERC-3643 demo* | 身份+策略+审计+披露 | ERC-3643 扩展 | 中-高 |
| 多层准入控制 | 无 | Bridge→RPC→Seq→Exec | 逐层构建 | 中 |
| 企业 Zone/L3 | MIX4 基础 | 独立执行环境 | 基于 MIX4 | 中 |
| ZK 合规证明 | 无 | KYC-in-ZK | 集成现有方案 | 中 |

\* 无公开来源确认

---

### Slide 19 — 方向三：机构金融 — Mantle 适配性评估

| 维度 | 评估 |
|---|---|
| **Mantle 优势** | EVM 生态 + 以太坊 L2 合法性 / mETH/收益生态（Tempo/Arc 没有）/ MI4/Securitize 基础 / ~$4B+ 国库 |
| **Mantle 挑战** | 技术栈几乎从零构建——但路径明确 / CCTP 缺失 / 无生产机构客户案例 |
| **判断** | 🟢 **强** — 可走 Prividium 模式，且有独特国库和收益生态优势 |

- **分阶段**：
  - Phase 1 (0-3m): 合规 RPC + 身份注册 + 审计日志
  - Phase 2 (3-9m): 企业 Zone/L3 + zkKYC PoC
  - Phase 3 (9-18m): Validium DA + 全栈合规
- **口述提示**：先产品化合规可见性（许可/审计/披露），再产品化密码学隐私

---

### Slide 20 — 三方向对比总结

| 维度 | AgentFi | Payment Chain | 机构金融 |
|---|---|---|---|
| 契合度 | 🔴 弱 | 🟡 中 | 🟢 **强** |
| 市场阶段 | 早期概念 | 快速增长 | 加速落地 |
| Mantle 差异化 | 有限 | 有限（可作子场景）| **明确（L2 + 合规）** |
| 竞争格局 | 红海 | 垂直链占位 | 先发者少 |
| 技术可行性 | 无特殊壁垒 | 架构受限 | 路径明确 |
| 已有基础 | 第三方 AA | 稳定币 $557.8M | MI4/Securitize + USDY + 国库 |

- **设计**：三列并排，机构金融列高亮

---

## Closing

### Slide 21 — 结论与下一步

- **核心结论**（三个编号要点）：
  1. L2 赛道已从通用竞争进入差异化定位——Mantle 必须选择方向
  2. 竞争压力来自三维：L2 平台化 / L1 替代 / 垂直链抢位
  3. **机构金融是 Mantle 契合度最高的叙事方向**——以 zkSync Prividium 为对标构建合规技术栈
- **建议下一步**（可选，根据演讲者判断）：
  - 立即：评估 CCTP/Circle 合作可行性
  - Q3：合规 RPC + 身份注册 MVP
  - Q4：企业 Zone/L3 PoC
- **开放问题**：op-geth EOL 迁移 / Mantle 开发者活动量化 / ERC-3643 demo 现状确认

---

### Slide 22 — Q&A

- 预留 10 分钟讨论
- **准备可能的问题方向**：
  - 技术栈构建时间线和资源估算
  - 与 zkSync Prividium 的差异化——我们有什么他们没有的？（答：国库 + DeFi 收益生态 + mETH）
  - 合规要求的具体细节——KYC/AML 方案选型
  - 支付子场景如何嵌入机构金融框架
  - 为什么不做 AgentFi——短期热度不等于长期壁垒
