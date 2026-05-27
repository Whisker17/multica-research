---
topic: "Payment Chain 技术架构补充调研（Tempo / Circle Arc）"
project_slug: 202606-internal-sharing
topic_slug: supplement-payment-tech
github_repo: Whisker17/multica-research
round: 1
status: draft

artifact_paths:
  outline: 202606-internal-sharing/outlines/supplement-payment-tech.md
  draft: 202606-internal-sharing/research-sections/supplement-payment-tech/drafts/round-{n}.md
  final: 202606-internal-sharing/research-sections/supplement-payment-tech/final.md
  supplementary_output: 202606-internal-sharing/report/assets/supplementary/payment-chain-tech-supplement.md
  index: 202606-internal-sharing/research-sections/_index.md

draft_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-27T13:30:00+08:00"
  outline_path: 202606-internal-sharing/outlines/supplement-payment-tech.md
  outline_commit: 8259d6e
  language: zh-CN
  research_depth: synthesis
  verification_date: "2026-05-27"
  note: "Orchestrator dispatch authorized outline + draft in single turn; outline at candidate status. All technical conclusions traced to existing approved final sections."

source_sections:
  - path: 202606-internal-sharing/research-sections/payment-tempo/final.md
    status: final
    used_items: "item-2 to item-8"
  - path: 202606-internal-sharing/research-sections/payment-ark/final.md
    status: final
    used_items: "item-2 to item-7"
  - path: 202606-internal-sharing/research-sections/narrative-payment/final.md
    status: final
    used_items: "item-4 to item-8"
---

# Payment Chain 技术架构补充调研（Tempo / Circle Arc）

## 1. 引言

本文是 Slides Outline Chapter 3 Section 3.2（Payment Chain 方向）的技术架构补充材料。slides 已阐述支付方向的战略判断；本补充材料聚焦**底层技术架构**：做 Payment Chain 到底需要链具备什么能力、Tempo 和 Circle Arc 分别如何在架构层满足这些要求、以及 Mantle 当前 OP Stack 架构与之存在哪些结构性差距。

所有技术结论均可追溯到本仓库已审核通过的 research sections（`payment-tempo/final.md`、`payment-ark/final.md`、`narrative-payment/final.md`），不做新的 primary source 研究。

## 2. Payment Chain 核心技术要求

Payment Chain 不等于"通用链上部署支付合约"。它要求底层链在六个维度提供通用 L2 默认不具备的能力：

| 能力维度 | 技术要求 | 通用 L2 现状 | Payment Chain 方案 |
|---------|---------|------------|------------------|
| **确定性终局** | 资金状态亚秒 ~ 秒级不可重组，商户可据此放行 | L2 soft confirmation 依赖 sequencer 诚实假设；真正不可重组需等 L1 finality（~13min） | BFT 共识提供确定性终局（2/3 验证者提交后不可重组） |
| **费用确定性** | 以稳定币计价、可预测、对终端用户透明或不可见 | gas token（ETH/MNT）价格波动 + gas 竞价；用户需持有并理解 gas token | 原生稳定币 Gas（USDC/attodollars）+ 费用赞助/Paymaster |
| **支付专用 blockspace** | 支付交易有保留容量，不被 DeFi/NFT 拥堵挤出 | 所有交易共享同一 gas pool，无优先级隔离 | Payment Lane / gas budget 分区（协议级 blockspace 隔离） |
| **稳定币原生支持** | 协议级 memo、合规策略、fee eligibility、Payment Lane 集成 | ERC-20 是应用层合约，无协议级支付语义 | TIP-20 预编译标准 / USDC 原生发行 |
| **跨链互操作** | 支付资金需跨链流动，安全、低延迟、无桥接资产风险 | 依赖第三方桥，存在桥接资产 depeg 和延迟 | CCTP burn-and-mint（Circle 原生 1:1 USDC 跨链） |
| **合规基础设施** | 链级 transfer policy 执行，支持 whitelist/blacklist/compound 策略 | 合规逻辑在应用层合约中，无协议级执行保证 | 预编译级合规策略注册表（TIP-403）/ 可选隐私控制 |

**与通用 L2 的本质差异**：通用 L2 优化的是"通用计算的安全和吞吐"，而 Payment Chain 优化的是"资金移动的确定性和体验"。前者的安全模型是 rollup/L1 锚定，后者需要在此之上叠加支付级终局性、费用可预测性和合规执行力。这不是可以通过单个合约部署解决的——它触及共识、交易类型、gas 机制、blockspace 分配和预编译层。

（来源：综合 `narrative-payment/final.md` item-4、`payment-tempo/final.md` item-2/3/4、`payment-ark/final.md` item-2）

## 3. Tempo 技术架构要点

Tempo 定位为 payments-first EVM-compatible L1，由 Stripe + Paradigm 孵化，核心思路是**把支付能力下沉到协议和客户端层**，而不是在通用链上堆应用层合约。

### 3.1 共识层：Commonware Simplex BFT

Tempo 采用双进程架构：Reth devp2p 负责执行层同步，Commonware P2P 负责共识消息。共识引擎基于 Commonware Simplex BFT，使用 BLS12-381 门限签名和 VRF leader 选举，目标 ~500-600ms 确定性终局（BFT 2/3 验证者提交后区块不可重组）。

这种双网络隔离的设计意义在于：执行层的负载（大型合约调用、DeFi 交易）不会直接拖慢共识延迟。对支付场景，这意味着支付交易的终局时间不受通用计算拥堵的影响。

⚠️ 性能数据来自设计目标和代码支持方向，实际生产延迟、峰值吞吐和拥堵下 SLA 需要独立验证。Commonware 是 Paradigm 开发、Tempo 深度使用的栈，独立生产用户和稳定 API 较少。

（来源：`payment-tempo/final.md` item-2）

### 3.2 Payment Lane：协议级支付 blockspace 隔离

Payment Lane 是 Tempo 最具差异化的设计。它将区块空间分为三条 lane：

- **System Lane**：协议/系统交易、subblocks metadata
- **Payment Lane**：TIP-20 支付交易，享有保留 gas 容量
- **General Lane**：DeFi、普通合约调用，受 `general_gas_limit` 硬约束

**工作机制**：payload builder 在构建区块时计算 `shared_gas_limit`、`non_shared_gas_limit` 和 `general_gas_limit`。当通用交易累计 gas 超过 `general_gas_limit` 时，builder 以 `ExceedsNonPaymentLimit` 跳过非支付交易——但支付交易仍可继续被纳入区块。

**支付分类规则**经历了两代演进：
- **v1**：以 TIP-20 合约地址前缀做共识层无状态检查
- **v2/TIP-1045**：更严格——要求 selector allow-list、空 access list/authorization list、bounded key authorization

代码层面：`crates/primitives/src/transaction/envelope.rs` 同时存在 `is_payment_v1()` 和 `is_payment_v2()`；`crates/chainspec/src/constants.rs` 定义 `TEMPO_T1_GENERAL_GAS_LIMIT = 30_000_000`。

（来源：`payment-tempo/final.md` item-3，代码引用来自 `tempoxyz/tempo@4a11578`）

### 3.3 稳定币 Gas 与协议级支付原语

**稳定币 Gas**：Tempo 无单独原生 gas token，费用以 attodollars 计价。`TEMPO_T1_BASE_FEE = 20_000_000_000` attodollars/gas，一笔 50,000 gas 的 TIP-20 transfer 约 $0.001。费用以 TIP-20 稳定币支付，通过 Fee AMM/StablecoinDEX 处理跨币种兑换。

**TIP-20**：协议级 token 标准，以预编译实现（非 ERC-20 合约）。固定 6 位小数、原生 memo 字段、pause/role-based access、reward distribution、DEX quote token、fee eligibility。ABI 部分兼容 ERC-20，但 storage/索引/小数/策略行为不能按 ERC-20 假设。

**TIP-403**：合规策略注册表预编译，提供 whitelist/blacklist/compound policy。所有 TIP-20 transfer 经过 sender/recipient 双边策略检查。

**账户体验**：`TempoTxEnvelope` 自定义交易类型支持 P256/WebAuthn/Passkey、access keys（权限限额）、fee sponsorship（商户代付 gas）、call batching（批量付款）、valid_after/valid_before（时间窗口）、二维 nonce（并行交易）。

（来源：`payment-tempo/final.md` item-4）

### 3.4 Enterprise Zones

Zones 是 Tempo-native 的企业隐私执行环境（Reth validium），通过 ZonePortal/ZoneFactory 部署，提供独立状态、authenticated RPC、encrypted deposit。关键限制：单 sequencer 信任模型，`batch.rs` 中 proof bytes 为空（proof generation 未接入），README 明确"not recommended for production use"。

（来源：`payment-tempo/final.md` item-6）

### Tempo 六维能力覆盖

| 能力维度 | Tempo 实现 | 覆盖评估 |
|---------|-----------|---------|
| 确定性终局 | Commonware BFT ~500-600ms | ✅ 设计满足，生产 SLA 待验证 |
| 费用确定性 | attodollars + 固定基础费 + fee sponsorship | ✅ 强 |
| 支付 blockspace | Payment Lane + gas budget 分区 | ✅ 核心差异化 |
| 稳定币原生支持 | TIP-20 预编译 + memo + fee eligibility | ✅ 强，但生态迁移成本高 |
| 跨链互操作 | 无内置跨链协议 | ❌ 需依赖第三方桥 |
| 合规基础设施 | TIP-403 双边策略注册表 + Zones 隐私 | ✅ 强（链上合规）；Zones 早期 |

## 4. Circle Arc 技术架构要点

Arc 是 Circle（USDC 发行方、NYSE 上市）构建的开放 L1，定位为 "Economic OS for the internet"——从稳定币发行方向全栈金融基础设施转型的战略载体。

### 4.1 共识层：Malachite BFT

Malachite 最初由 Informal Systems 开发（Tendermint 衍生/Rust 实现），Circle 已接管管理。同样采用双进程架构：共识与执行作为独立进程运行，通过 Engine API 通信。

**性能基准**（测试网数据）：~780ms 终局延迟（100 验证者，1 MB 区块）；330-490ms（小规模地理分布式网络）；~50,000 TPS / 13.5 MB/s。

**关键设计选择**：
- **区块引用传播**：共识层只处理紧凑区块引用，不处理完整交易 payload——降低关键路径延迟
- **定向 Liveness 子协议**：替代通用 gossip，使用专用子协议实现可靠消息传递
- **确定性终局**：2/3 验证者提交即终局，即使执行层升级/停滞也不影响

⚠️ 以上均为测试网/基准数据，主网预计 2026 年夏季，具体日期待定。

（来源：`payment-ark/final.md` item-2，Arc blog "Arc's Deterministic Finality"）

### 4.2 USDC Gas 与费用平滑

Arc 的核心设计决策：使用 USDC 作为原生 Gas 代币。

- **费用平滑**：不逐区块调整费用，使用指数加权移动平均（EWMA）区块利用率 + bounded base fee，抑制短期需求尖峰
- **Paymaster 多币种**：支持 EURC 或其他资产支付交易费用，后台通过内置稳定币 FX 引擎自动兑换为 USDC
- **机构意义**：稳定币计价消除波动性 gas token 依赖，企业财务可精确预测基础设施成本

**与 Tempo 的设计取舍对比**：Tempo 用 attodollars 固定基础费（更稳定但可能在极端拥堵时缺乏市场化调节），Arc 用 EWMA 平滑（保留市场化信号但抑制短期波动）。两者都实现了"用户无需持有波动 gas token"的核心目标。

（来源：`payment-ark/final.md` item-2，Arc blog "How Gas Works on Arc"）

### 4.3 CCTP V2 跨链协议

CCTP（Cross-Chain Transfer Protocol）是 Circle 原生跨链 USDC 转账协议，通过 burn-and-mint 机制实现 1:1 USDC 跨链：

- V2 覆盖 26 个支持区块链/域（含 Arc Testnet）
- 累计转账量 $126B，Q3 2025 季度交易量 $31B（YoY +740%）
- Arc 上 USDC 为**原生发行**（非桥接）——这是任何第三方链无法复制的结构性优势

**对 Mantle 的关键含义**：Circle CCTP/native USDC primary docs 未列出 Mantle。因此 Mantle 上的 USDC 应按非 Circle 原生处理。推动 Circle 将 Mantle 纳入 CCTP 需要合作关系而非纯工程能力。

（来源：`payment-ark/final.md` item-2，Circle developer docs）

### 4.4 StableFX 与可选隐私

**StableFX**：机构级稳定币外汇引擎。RFQ 执行模式（多流动性供应商报价）、原子化链上结算（payment vs delivery atomicity）、24/7 运营、all-to-all 模型。配合 8 个 Partner Stablecoins（BRLA/KRW1/PHPC/AUDF/MXNB/JPYC/QCAD/ZARU），构建多币种链上 FX 网络。

**可选隐私**：L1 层交易级隐私——confidential transfers（屏蔽金额保持地址可见）、TEE 可信执行环境、view keys（审计用只读密钥）、opt-in 设计。与 Tempo Zones 的设计差异：Arc 在 L1 做交易级隐私，Tempo 在 L2 做独立执行环境隐私。

（来源：`payment-ark/final.md` item-3）

### Arc 六维能力覆盖

| 能力维度 | Arc 实现 | 覆盖评估 |
|---------|---------|---------|
| 确定性终局 | Malachite BFT ~780ms / 330-490ms | ✅ 设计满足，主网待上线验证 |
| 费用确定性 | USDC Gas + EWMA + Paymaster 多币种 | ✅ 强 |
| 支付 blockspace | 无专用 Payment Lane | ❌ 所有交易共享 blockspace |
| 稳定币原生支持 | USDC 原生发行 + EVM 兼容 | ✅ 发行方结构性优势 |
| 跨链互操作 | CCTP V2 原生支持（26 域，$126B） | ✅ 强，无可复制 |
| 合规基础设施 | 可选隐私 + TEE + view keys + PoA 验证者 | ✅ 中-强（合规隐私方向不同于 Tempo） |

## 5. Tempo vs Arc 技术架构对比

| 维度 | Tempo | Circle Arc |
|------|-------|-----------|
| **共识引擎** | Commonware Simplex BFT（Paradigm 自研/Rust） | Malachite BFT（Tendermint 衍生/Rust，Circle 接管） |
| **终局时间** | ~500-600ms ⚠️ 设计目标 | ~780ms（100 验证者）⚠️ 测试网 |
| **客户端** | Reth SDK 深度 fork（26+ crates） | 自研（未公开具体框架） |
| **Gas 模型** | attodollars + 固定基础费 | USDC Gas + EWMA 平滑 + bounded base fee |
| **Payment Lane** | ✅ System/Payment/General 三条 lane + gas 分区 | ❌ 无专用 lane |
| **稳定币标准** | TIP-20 协议级预编译（新标准，需迁移） | ERC-20（Circle 原生发行，低迁移摩擦） |
| **跨链** | ❌ 无内置跨链协议 | ✅ CCTP V2（26 域，发行方优势） |
| **FX 能力** | StablecoinDEX / Fee AMM | StableFX RFQ + 8 Partner Stablecoins |
| **隐私方案** | Zones L2 独立执行环境（早期） | L1 可选隐私（TEE + view keys） |
| **合规** | TIP-403 预编译级双边策略 | PoA 验证者 + 可选隐私审计 |
| **背后力量** | Stripe 商户网络 + Paradigm | Circle USDC 发行方 + 资本市场机构 |
| **差异化总结** | 支付交易处理管道的极致优化 | 稳定币发行方的全栈金融基础设施 |

## 6. 与 Mantle 的 Gap 分析

以下矩阵以六维能力框架为基准，评估 Mantle 当前 OP Stack 架构的差距及补齐路径：

| 能力维度 | Mantle 当前状态 | 差距性质 | 短期可补齐（0-3月，应用/SDK） | 中期需改造（3-9月，sequencer/system contract） | 长期需架构变更（9-18月+） |
|---------|---------------|---------|---------------------------|---------------------------------------------|------------------------|
| **确定性终局** | L2 soft confirmation（sequencer 签名）；真正不可重组需等 L1 ~13min | 结构性差距 | preconf + merchant risk policy（小额放行） | sequencer slashing / fast-finality gadget POC | BFT finality research（改变信任模型） |
| **费用确定性** | MNT 原生 gas，价格波动 | 可补齐 | Paymaster + AA + 稳定币 fee quote SDK | system contract 级 fee quote、Paymaster risk engine | 协议级稳定币 gas 抽象 |
| **支付 blockspace** | 所有交易共享 gas pool，无隔离 | 需改造 | priority RPC + trusted payment relayer | sequencer payment tag + soft reservation | txpool/builder gas budget 分区（OP Stack 改造） |
| **稳定币原生支持** | ERC-20 合约层；USDC 为桥接资产（Circle docs 未列 Mantle） | 结构性差距 | memo/order id event schema + Payment Intent SDK | system contract predeploy（合规策略/fee eligibility） | 推动 Circle 原生 USDC / CCTP 合作 |
| **跨链互操作** | 依赖第三方桥（LayerZero/Relay） | 结构性差距 | 聚合路由 SDK | 评估 CCTP 集成优先级 | 推动 Circle 将 Mantle 纳入 CCTP |
| **合规基础设施** | 无链级 transfer policy | 可补齐 | 应用层合约 whitelist/blacklist | Solidity predeploy 合规策略注册表 | 预编译级合规执行（op-geth 改造） |

### 可复用 vs 需新建

**可在现有 OP Stack 上构建（无需共识/客户端改造）**：
- Paymaster/AA 稳定币 Gas UX
- Payment Intent SDK（memo、order id、webhook、retry）
- 应用层合规策略合约
- merchant treasury dashboard（DeFi/yield 集成）
- batch payment 合约

**需要 system contract / sequencer 改造**：
- payment lane sequencer policy（交易分类 + soft reservation）
- predeploy 级合规策略注册表
- 稳定币 fee quote system contract
- Paymaster risk engine

**需要架构级决策和合作**：
- 推动 Circle CCTP / 原生 USDC 支持（合作关系问题）
- BFT fast-finality gadget（改变 L2 安全模型）
- 协议级稳定币 Gas（替换 MNT 计价，影响代币经济学）
- 企业隐私 L3 / Zone-like appchain

**核心判断**：Mantle 不需要为了支付叙事复制一条 Payment L1。更现实的路径是 **Paymaster + Payment Intent SDK + merchant treasury + DeFi yield 的组合**作为短期切入，同时在 sequencer policy 层做 payment lane POC 验证。只有在 product-market fit 确认后，才推进更重的客户端和架构改造。B2B invoice settlement 和 merchant treasury 是最匹配的切入子场景（对退款、消费者保护和强监管牌照的依赖低于 retail checkout）。

（来源：`narrative-payment/final.md` item-4/5/6/8、`payment-tempo/final.md` item-8、`payment-ark/final.md` item-7）

## 7. 来源引用

本补充材料的所有技术结论均来自以下已审核通过的 research sections：

| 引用 | 路径 | 状态 | 主要引用内容 |
|------|------|------|------------|
| Tempo 技术架构 | `202606-internal-sharing/research-sections/payment-tempo/final.md` | final | Commonware BFT、Payment Lane、TIP-20/TIP-403、稳定币 Gas、Zones、Mantle 路线建议 |
| Arc 技术架构 | `202606-internal-sharing/research-sections/payment-ark/final.md` | final | Malachite BFT、USDC Gas、CCTP V2、StableFX、可选隐私、机构生态 |
| Payment Chain 叙事 | `202606-internal-sharing/research-sections/narrative-payment/final.md` | final | 终局性要求分析、Paymaster/Gas UX、Payment Lane 可行性、Mantle 适配性评估 |

Tempo 代码引用基于 `tempoxyz/tempo@4a11578111b57c5ceeab619ac9800b98f9c576dc`（workspace v1.7.1）。Arc 白皮书数据基于官方 PDF 直接解析（截至 2026-05-23）。Malachite 性能数据来自 Arc blog primary source。所有易过期事实的验证日期见各源 section 的 `draft_metadata.verification_date`。

## 8. Gap Analysis

1. **Tempo 本地代码库不可用**：dispatch 指定的 `/Users/whisker/Work/src/networks/tempo` 路径不存在。本 draft 的 Tempo 代码引用来自 `payment-tempo/final.md` 中已验证的 commit snapshot，未做增量代码验证。
2. **Arc 主网未上线**：Arc 的性能数据和架构设计均为测试网/基准状态。主网 beta 预计 2026 年夏季，实际生产表现待验证。
3. **Mantle 当前代码路径未审计**：Gap 分析基于 Mantle 常识和 OP Stack 架构约束推断。工程设计阶段应另做 Mantle repo 代码审计。
4. **CCTP/native USDC on Mantle 需持续跟踪**：若 Circle 后续新增 Mantle 支持，跨链 Gap 评估需刷新。

## 9. Revision Log

| Round | Change |
|-------|--------|
| 1 | Created first draft synthesizing from three approved final sections (payment-tempo, payment-ark, narrative-payment). Established six-dimension capability framework; produced Tempo/Arc architecture deep dives; generated Mantle Gap matrix with remediation tiers. ~2800 words. |
