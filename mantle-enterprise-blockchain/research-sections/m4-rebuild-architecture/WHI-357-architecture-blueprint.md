# WHI-357: 理想企业级区块链架构蓝图设计

> **推倒重建：如果我们今天从零开始，用 2026 年最先进的技术栈，为 RWA + xstocks + Payment 这三大叙事设计一条区块链，它应该长什么样？**

**文档版本**: v1.0
**创建日期**: 2026-05-07
**前置依赖**: WHI-355 (叙事需求分析) · WHI-356 (M3 适配度评估) · M1 全部调研 · M2 全部横向对比
**目标读者**: 架构决策者、后续深入设计 Issue (WHI-358–362, WHI-364–368) 的执行者

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [设计哲学与约束条件](#2-设计哲学与约束条件)
3. [技术栈选型论证](#3-技术栈选型论证)
4. [分层架构总体设计](#4-分层架构总体设计)
5. [多链/多 Zone 架构设计](#5-多链多-zone-架构设计)
6. [与 M3 方案的架构差异对比](#6-与-m3-方案的架构差异对比)
7. [关键技术创新点](#7-关键技术创新点)
8. [分阶段实施路线图](#8-分阶段实施路线图)
9. [开放问题与待决策项](#9-开放问题与待决策项)

---

## 1. 执行摘要

### 1.1 为什么需要推倒重建

WHI-356 的 M3 适配度评估揭示了 OP Stack 方案面对 Mantle 三大叙事的**五个结构性瓶颈**——这些不是参数调优或功能补丁能解决的问题，而是架构选择的天花板：

| 瓶颈 | M3 现状 | 叙事需求 | 差距倍数 |
|---|---|---|---|
| **硬终局性** | ~12 小时（SP1 ZK 证明） | xStocks T+0 <1s、Payment B2C 亚秒级 | **43,000×** |
| **吞吐量** | ~1,000 TPS（reth 单引擎上限） | Payment B2C >10,000 TPS | **10×** |
| **隐私粒度** | 合约级（Validium + Viewing Key） | 子交易级（Canton Merkle DAG 投影） | 架构不兼容 |
| **算子信任** | 单 Sequencer 必须解密所有数据 | 无需算子信任的密码学隐私 | 模型冲突 |
| **多租户物理隔离** | 12-18 个月后的 Phase 3 | 原生 Zone 架构 | 时间差距 |

M3 在 DeFi (4.7/5)、供应链金融 (4.1/5)、RWA 非实时场景 (3.7/5) 上仍然可行。但对于 **xStocks HFT (2.9/5)** 和 **Payment B2C (3.0/5)**，M3 方案需要根本性的架构重构。

### 1.2 蓝图核心主张

本蓝图提出一个**叙事驱动、分层解耦、渐进可行**的企业级区块链架构：

- **执行层**: Reth SDK（Rust 原生、模块化、Tempo 已验证）
- **共识层**: Simplex BFT + ZK 锚定混合方案（亚秒级确定性终局 + Ethereum 数学安全锚定）
- **隐私层**: 原生多 Zone 架构（公开主链 + 叙事专用隐私 Zone）
- **合规层**: 协议层内置（预编译级策略执行 + ZK 合规证明）
- **结算层**: 混合方案——独立 BFT 终局 + 可选 Ethereum ZK 锚定

---

## 2. 设计哲学与约束条件

### 2.1 核心设计原则

| 原则 | 含义 | 落地方式 |
|---|---|---|
| **叙事驱动** | 架构服务于业务，不是业务迁就架构 | 从 WHI-355 每个叙事的具体需求反推技术选型 |
| **最优技术选型** | 不限于 OP Stack，全面评估 2026 年最先进技术栈 | 系统性评估 Reth SDK、ZK Stack、自建执行层等选项 |
| **企业原生** | 隐私、合规、准入是"内置的"，不是"后加的" | 在协议层（预编译/共识规则）而非应用层（合约）实现 |
| **EVM 兼容性保留** | Mantle 生态的基础，不可动摇 | 选择 EVM 兼容的执行框架（Reth SDK / ZK Stack） |
| **渐进式可行** | 理想架构可分阶段实现 | 每个架构层可独立交付，不需要一次性全部完成 |

### 2.2 硬约束条件

来自 WHI-355 的叙事分析和行业研究，以下约束是**不可协商的**：

1. **EVM 兼容性**: Canton 的 Daml 开发者池仅数百人全球，而 Solidity 开发者数十万——生态是 Mantle 的护城河
2. **Ethereum 安全锚定**: 完全脱离 Ethereum 丧失 L1 安全继承——这是 Mantle 相对于 Canton/Tempo 独立 L1 的核心优势
3. **确定性终局**: Optimistic Rollup 的 7 天挑战期对所有企业叙事"完全不可接受"（WHI-355 原文）
4. **物理隔离**: Payment (高 TPS / 低隐私) 和 RWA (低 TPS / 高隐私) 不可能在同一执行环境共存（WHI-355 §5.2 明确要求物理分离）

### 2.3 叙事优先级与架构影响

| 叙事 | 关键指标 | 架构影响 |
|---|---|---|
| **RWA 代币化** | 隐私(5) · 合规(5) · 终局性(4) · 身份(5) | 需要子交易级隐私、完整合规审计、原生身份层 |
| **xStocks (代币化股票)** | 终局性(5) · 性能(4) · 隐私(5) · 合规(5) | 需要 T+0 原子结算、<100ms 延迟、暗池级隐私、实时市场监控 |
| **Payment (稳定币支付)** | TPS(5) · 终局性(5) · 费用(5) · 合规(4) | 需要 >10K TPS、亚秒级终局、<$0.001/tx、Travel Rule |

---

## 3. 技术栈选型论证

### 3.1 执行层选型

#### 3.1.1 候选方案对比矩阵

| 维度 | Reth SDK | op-geth 深度改造 | ZK Stack | 自建执行层 |
|---|---|---|---|---|
| **描述** | Paradigm 模块化以太坊执行框架 (Rust) | 在 Mantle 现有 op-geth 基础上深度改造 | Matter Labs 模块化 ZK 框架 | 全新 EVM 实现 |
| **语言** | Rust | Go | Rust + Solidity | 可选 |
| **EVM 兼容性** | 完整（通过 Osaka hardfork） | 完整 | 完整（zkSync Era EVM） | 需要验证 |
| **模块化程度** | ★★★★★ NodeBuilder + 自定义 NodeTypes | ★★ 三层 fork 链限制 | ★★★★ ZK Stack 模块化 | ★★★★★ 完全自由 |
| **性能潜力** | ★★★★★ Rust + MDBX + 可插拔共识 | ★★★ go-ethereum 性能天花板 | ★★★★ GPU 加速 ZK 证明 | 取决于设计 |
| **生产验证** | Tempo 主网 live (Chain ID 4217) | Mantle 主网运行中 | Prividium 银行联盟已部署 | 无 |
| **ZK 友好度** | ★★★★ `no_std` 预编译设计，SP1/RISC-V 就绪 | ★★ keeper zkVM guest 已存在但初级 | ★★★★★ 原生 STARK 证明 | 取决于设计 |
| **开发生态** | 快速增长（Paradigm 支持） | 成熟但受 geth 架构限制 | ZKsync 生态绑定 | 需要从零建设 |
| **风险** | 需要大量定制工作 | 三层 fork 上游合并困难 | Matter Labs 生态锁定 | 工作量巨大、安全风险 |

#### 3.1.2 推荐选型：Reth SDK

**结论**: **Reth SDK** 是最优选择。理由如下：

**1. Tempo 已验证的实战经验**

Tempo 主网（Chain ID 4217，T2 阶段自 2026 年 3 月 31 日起运行）证明 Reth SDK 可以构建生产级自定义链。其 `TempoFullNode` 基于 `reth-node-builder` 构建，使用 revm v38 和 MDBX 状态数据库——我们可以直接参考这一架构模式。

**2. 模块化设计与叙事需求匹配**

Reth SDK 的 `NodeBuilder` + 自定义 `NodeTypes` + `EngineTypes` 组合允许：
- 替换共识引擎（从 Optimistic Rollup 到 BFT）而不改动执行层
- 插入自定义预编译（合规策略、身份验证、加密操作）
- 自定义交易类型（Tempo 的 `0x76` 交易类型是先例）
- 独立运行时隔离（Tempo 的双 Tokio 运行时：共识和执行互不干扰）

**3. Rust 性能优势**

Rust 原生 + MDBX 状态存储的组合为后续性能优化提供了远高于 Go + LevelDB 的天花板。这对于 Payment B2C (>10K TPS) 和 xStocks HFT (<100ms) 至关重要。

**4. ZK 就绪的 `no_std` 纪律**

Tempo 的预编译和原语都设计为 `no_std` 兼容，刻意准备在 SP1 RISC-V 证明器 guest 内运行。这意味着从 BFT 快速终局到 ZK 有效性证明的迁移路径已经内置于架构中。

**5. 相对于替代方案的优势**

- vs. op-geth：摆脱三层 fork 链（go-ethereum → op-geth → Mantle）的上游合并负担。WHI-356 指出 Mantle 已经在 Arsia fork 上有 6 次自定义硬分叉，企业功能持续加深上游分歧。
- vs. ZK Stack：避免 Matter Labs 生态锁定。ZKsync Connect/Gateway 仅在 ZKsync 生态内工作；Reth SDK 是开源且中立的。
- vs. 自建执行层：复用经过验证的 EVM 实现（revm），而非从零开始承担安全风险。

### 3.2 共识层选型

#### 3.2.1 候选方案对比矩阵

| 维度 | Commonware Simplex BFT | CometBFT (Tendermint) | 自研 BFT | ZK + BFT 混合 |
|---|---|---|---|---|
| **终局性** | 亚秒级（~600ms），确定性 | 秒级，确定性 | 可优化 | 双重终局 |
| **吞吐量** | 高（BLS12-381 阈值签名） | 中等 | 取决于设计 | 取决于组合 |
| **验证者管理** | VRF 领导者选举 + DKG | 成熟的验证者集合管理 | 需自建 | 复合方案 |
| **生产验证** | Tempo 主网 | Cosmos 生态广泛使用 | 无 | 理论方案 |
| **Reth 集成** | ★★★★★ Tempo 已证明 | ★★★ 需要适配 | ★★ 从零集成 | ★★★ 组合复杂度 |
| **EVM 兼容** | 通过 Reth SDK 间接兼容 | 通过 ABCI 接口 | 取决于设计 | 取决于组合 |

#### 3.2.2 推荐选型：Simplex BFT + ZK Ethereum 锚定（混合方案）

**结论**: 采用 **ZK + BFT 混合方案**——以 Commonware Simplex BFT 为基础，结合 ZK 有效性证明锚定 Ethereum L1。

**方案设计**:

```
┌──────────────────────────────────────────────────────┐
│  即时层 (Instant Layer) — Simplex BFT                 │
│                                                        │
│  · 亚秒级确定性终局 (~600ms)                           │
│  · BLS12-381 DKG 阈值签名                              │
│  · VRF 领导者选举，防止 MEV                             │
│  · 2/3 BFT 安全假设                                    │
│  · 满足 xStocks T+0 和 Payment B2C 亚秒需求            │
├──────────────────────────────────────────────────────┤
│  锚定层 (Anchoring Layer) — ZK 有效性证明               │
│                                                        │
│  · 定期批量提交 ZK 证明到 Ethereum L1                   │
│  · 数学安全保证（STARK 可靠性 ≥ 2^{-80}）             │
│  · 保留 Ethereum 安全继承                               │
│  · 满足机构对 L1 安全锚定的要求                         │
│  · 频率：每 N 个 BFT epoch 提交一次（可配置）          │
└──────────────────────────────────────────────────────┘
```

**为什么选择 Simplex BFT 作为基础**:

1. **Tempo 已证明与 Reth SDK 的集成可行性**——双 Tokio 运行时架构将共识和执行隔离在独立线程池中，防止执行负载峰值影响共识延迟
2. **亚秒级终局直接满足最苛刻的叙事需求**——xStocks T+0 原子结算和 Payment B2C 扫码即确认
3. **BLS12-381 阈值签名**提供紧凑的共识证明，便于跨链验证

**为什么增加 ZK 锚定而非纯 BFT**:

1. **Ethereum 安全继承**是 Mantle 相对于 Canton（组织信任）和 Tempo（独立 BFT L1）的核心差异化优势
2. **机构客户要求**：大型金融机构（Goldman Sachs、HSBC 等）明确需要 L1 安全锚定作为风控依据
3. **监管友好**：Basel III/IV 对确定性终局资产的风险权重更有利；ZK 证明提供数学级别的确定性

**为什么不选 CometBFT**: 虽然更成熟，但与 Reth SDK 的集成没有现成先例，且 Simplex BFT 的亚秒级终局优于 CometBFT 的秒级终局。

### 3.3 结算层关系

#### 3.3.1 方案对比

| 方案 | 描述 | 优势 | 劣势 |
|---|---|---|---|
| **纯 L2** | 仍作为 Ethereum L2 运行 | 完整 L1 安全继承 | 受限于 Rollup 模型约束 |
| **独立 L1** | 完全独立链 | 最大架构自由度 | 丧失 Ethereum 安全继承 |
| **混合方案** | 独立 BFT 终局 + 可选 Ethereum ZK 锚定 | 兼得架构自由和安全锚定 | 实现复杂度较高 |

#### 3.3.2 推荐方案：混合结算

**结论**: 采用**混合方案**——主链以 BFT 共识运行，具有独立的确定性终局，同时定期向 Ethereum L1 提交 ZK 有效性证明作为安全锚定。

**关键设计决策**:

- **主链不再是 Rollup**——而是具有自己共识的独立链
- **Ethereum 锚定是可选的增值层**——即使 L1 暂时不可达，主链仍可独立运行
- **ZK 证明批量提交**——不需要每个区块都锚定，以 epoch 为单位批量提交（降低 L1 gas 成本）
- **双重终局语义**:
  - **BFT 终局** (~600ms): 交易被 2/3+ 验证者确认，用于日常交易确认
  - **L1 终局** (minutes-hours): ZK 证明在 Ethereum 上验证通过，用于跨链桥接和机构结算

**为什么不选纯 L2**: Rollup 模型（无论 Optimistic 还是 ZK）要求将所有交易数据发布到 L1——这与数据隐私根本冲突。纯 L2 模型下无法实现 Validium 级别的企业数据隐私。

**为什么不选纯独立 L1**: 完全脱离 Ethereum 将丧失 Mantle 最重要的战略资产——Ethereum 安全继承和 EVM 生态互操作性。Canton 和 Tempo 作为独立网络的经验表明，这增加了机构采纳的信任门槛。

---

## 4. 分层架构总体设计

### 4.1 总体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                    业务应用层 (Business Application Layer)            │
│                                                                       │
│  ┌──────────────┐  ┌──────────────────┐  ┌───────────────────┐      │
│  │  RWA DApps    │  │  xStocks DApps   │  │  Payment DApps    │      │
│  │ · 资产发行    │  │ · 暗池交易        │  │ · 扫码支付         │      │
│  │ · DVP 结算    │  │ · 合规订单簿      │  │ · B2B 跨境        │      │
│  │ · 收益分配    │  │ · 市场监控仪表板  │  │ · 多币种兑换       │      │
│  └──────────────┘  └──────────────────┘  └───────────────────┘      │
├─────────────────────────────────────────────────────────────────────┤
│                    业务组件层 (Business Component Layer)              │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  合规代币标准          │  资产生命周期引擎     │  支付通道引擎  │    │
│  │  · ERC-3643 增强      │  · 发行/交易/赎回     │  · Payment     │    │
│  │  · TransferHook       │  · 估值/分红/清算     │    Lane 路由   │    │
│  │  · FreezeHook         │  · 跨 Zone 资产流转   │  · 多币种 AMM  │    │
│  ├──────────────────────────────────────────────────────────────┤    │
│  │  身份/KYC 预编译       │  合规策略注册表       │  审计框架      │    │
│  │  · 链上身份绑定        │  · 白名单/黑名单     │  · Observer    │    │
│  │  · 投资者资质验证      │  · 复合策略逻辑      │    角色模型    │    │
│  │  · 跨平台身份互认      │  · 自动 L1→Zone 同步 │  · ZK 合规证明 │    │
│  └──────────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────────┤
│                    隐私层 (Privacy Layer)                             │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │            公开主链 (Public Mainchain)                          │   │
│  │  · DeFi 协议 · 资产发行注册表 · 全局流动性池 · 公开状态         │   │
│  ├───────────────────────────────────────────────────────────────┤   │
│  │     ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐    │   │
│  │     │ RWA Zone     │  │ xStocks Zone │  │ Payment Zone    │    │   │
│  │     │ · 子交易隐私 │  │ · 暗池引擎   │  │ · 高 TPS 通道   │    │   │
│  │     │ · Viewing Key│  │ · 仓位隐私   │  │ · ECIES 加密    │    │   │
│  │     │ · 机构准入   │  │ · 订单流保护 │  │ · 亚秒级终局    │    │   │
│  │     └─────────────┘  └──────────────┘  └─────────────────┘    │   │
│  │     ┌──────────────────────────────────────────────────────┐   │   │
│  │     │  自定义 Zone (Custom Zones) — 企业/用户自建隐私空间    │   │   │
│  │     └──────────────────────────────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                    执行层 (Execution Layer)                           │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │  Reth SDK (revm v38+) — EVM 兼容执行环境                       │   │
│  │                                                                 │   │
│  │  · 自定义预编译集合:                                            │   │
│  │    0x0401: IdentityRegistry (身份查询)                          │   │
│  │    0x0402: ComplianceCheck (合规验证)                            │   │
│  │    0x0403: PolicyRegistry (TIP-403 兼容策略注册表)              │   │
│  │    0x0404: EncryptedDeposit (ECIES + Chaum-Pedersen)            │   │
│  │    0x0405: SelectiveDisclosure (选择性披露)                      │   │
│  │                                                                 │   │
│  │  · 自定义交易类型:                                              │   │
│  │    0x76: 企业交易 (Tempo 兼容)                                  │   │
│  │    0x77: 合规交易 (含 KYC 凭证)                                 │   │
│  │    0x78: 隐私交易 (含 ZK 证明)                                  │   │
│  │                                                                 │   │
│  │  · Gas 定价模型:                                                │   │
│  │    公开主链: 标准 EIP-1559                                      │   │
│  │    Payment Zone: 固定低费率 (<$0.001/tx)                        │   │
│  │    RWA/xStocks Zone: 合规操作免 gas (Sequencer 赞助)            │   │
│  │                                                                 │   │
│  │  · 性能优化:                                                    │   │
│  │    Payment Lane 无状态分类 (0x20C0 地址前缀匹配)                │   │
│  │    并行 EVM 执行 (乐观并发控制)                                  │   │
│  │    MDBX 状态数据库                                               │   │
│  └───────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                    共识层 (Consensus Layer)                           │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │  Simplex BFT 即时终局共识                                       │   │
│  │                                                                 │   │
│  │  · 亚秒级确定性终局 (~600ms)                                    │   │
│  │  · BLS12-381 分布式密钥生成 (DKG) 阈值签名                      │   │
│  │  · VRF 领导者选举 (防 MEV)                                      │   │
│  │  · 双 Tokio 运行时: 共识运行时 ⊥ 执行运行时                    │   │
│  │  · 验证者集管理: ValidatorConfig 预编译                          │   │
│  │                                                                 │   │
│  │  Zone 共识: NoopConsensus                                       │   │
│  │  · 单 Sequencer、无 P2P                                         │   │
│  │  · L1 事件驱动区块生产 (1:1 映射)                               │   │
│  │  · head = safe = finalized (始终)                               │   │
│  └───────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                    数据层 (Data Availability Layer)                   │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │  混合 DA 策略                                                    │   │
│  │                                                                 │   │
│  │  ┌─────────────────┐  ┌───────────────────┐  ┌──────────────┐ │   │
│  │  │  公开数据        │  │  隐私数据          │  │  审计数据     │ │   │
│  │  │  · 主链公开交易  │  │  · Zone 交易数据   │  │  · 加密存档   │ │   │
│  │  │  · L1 Blob DA    │  │  · 运营者私有 DB   │  │  · 选择性    │ │   │
│  │  │  · 任何人可验证  │  │  · 访问控制检索    │  │    披露给     │ │   │
│  │  │                  │  │  · DAC 签名 (可选) │  │    监管者     │ │   │
│  │  └─────────────────┘  └───────────────────┘  └──────────────┘ │   │
│  │                                                                 │   │
│  │  路由规则: 每笔交易根据 Zone 类型和策略自动路由到对应 DA 后端   │   │
│  └───────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                    结算/锚定层 (Settlement/Anchoring Layer)           │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │  可选 Ethereum L1 ZK 锚定                                       │   │
│  │                                                                 │   │
│  │  · ZK 有效性证明批量提交 (每 N 个 epoch)                        │   │
│  │  · 状态承诺 (State Commitment) 上链                              │   │
│  │  · L1 验证合约 (Verifier Contract)                               │   │
│  │  · 跨链桥: ZK 证明保护的双向资产桥                              │   │
│  │  · 双重终局语义:                                                │   │
│  │    · BFT 终局 (~600ms): 日常交易确认                             │   │
│  │    · L1 终局 (minutes): 跨链桥接和机构结算                       │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                              │                                        │
│                              ▼                                        │
│                    ┌──────────────────┐                               │
│                    │  Ethereum L1      │                               │
│                    │  · ZK Verifier    │                               │
│                    │  · Bridge Contract│                               │
│                    │  · State Roots    │                               │
│                    └──────────────────┘                               │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 各层详细设计

#### 4.2.1 业务应用层 (Business Application Layer)

**职责**: 面向终端用户和机构的 DApp 层，每个叙事有专门的应用集合。

**关键特性**:
- 标准 Solidity/Vyper 开发——完整 EVM 工具链支持 (Hardhat, Foundry, OpenZeppelin)
- 每个叙事有对应的 SDK 和模板合约
- 与业务组件层通过标准 EVM 调用接口交互

**与下层接口**: 通过 EVM `CALL`/`STATICCALL` 调用业务组件层的预编译和预部署合约。

#### 4.2.2 业务组件层 (Business Component Layer)

**职责**: 提供跨叙事共享的企业级基础设施组件，作为预编译和预部署合约的集合。

**核心组件**:

| 组件 | 类型 | 接口 | 功能 |
|---|---|---|---|
| **合规代币标准** | 预部署合约 | ERC-3643 增强 | TransferHook 合规检查、FreezeHook 资产冻结、合规元数据 |
| **身份/KYC 预编译** | 预编译 (0x0401) | `isVerified(address)`, `getQualification(address, type)` | 链上身份查询、投资者资质验证、跨平台互认 |
| **合规策略注册表** | 预编译 (0x0403) | `isAuthorized(from, to, amount, context)` | 白名单/黑名单/复合策略、自动 L1→Zone 同步 |
| **资产生命周期引擎** | 预部署合约 | 标准化资产操作接口 | 发行、交易、赎回、估值、分红、清算 |
| **支付通道引擎** | 预部署合约 | TIP-20 兼容 | Payment Lane 路由、多币种 AMM/订单簿、FX 定价 |
| **审计框架** | 预编译 (0x0405) + 预部署合约 | Observer 模式 | 监管者直接数据访问、选择性披露、ZK 合规证明 |

**与下层接口**: 预编译通过 Reth SDK 的 `PrecompileRegistrar` 注册；预部署合约通过升级交易模式部署（参考 Mantle Arsia 升级模式）。

**设计参考**:
- 身份预编译 → Tempo `AccountKeychain` + Prividium SSO 集成
- 合规策略注册表 → Tempo TIP-403 预编译（白名单/黑名单/复合策略）
- 审计框架 → Canton Observer 角色模型（监管者作为参与者直接访问数据）+ Prividium Private Explorer（角色化审计视图）

#### 4.2.3 隐私层 (Privacy Layer)

**职责**: 实现多层次隐私架构，从公开主链到完全隔离的隐私 Zone。

**设计哲学**: 采用 **"反向隐私-复杂度法则"** (WHI-349 Pattern P2)——精细化的信息路由控制能以更简单的密码学实现更精细的隐私。ZK 证明仅用于信任边界跨越，不用于数据路由。

**三层隐私模型**:

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: 准入控制隐私 (Admission Control Privacy)       │
│  · 认证 RPC (签名访问令牌, per-account 数据过滤)         │
│  · Sequencer 策略引擎 (白名单/黑名单)                    │
│  · 无密码学开销, 纯路由层控制                            │
│  · 达成效果: 未授权用户无法看到或提交交易                │
├─────────────────────────────────────────────────────────┤
│  Layer 2: DA 层隐私 (Data Availability Privacy)          │
│  · Zone 交易数据不发布到主链                             │
│  · 加密 DA 后端 (运营者私有数据库)                       │
│  · ECIES 加密存款/取款 (隐藏接收者身份)                  │
│  · 达成效果: 外部观察者无法获取 Zone 内交易数据          │
├─────────────────────────────────────────────────────────┤
│  Layer 3: 密码学隐私 (Cryptographic Privacy)             │
│  · ZK 合规证明 (无 PII 制裁筛查)                         │
│  · 选择性披露 (Viewing Key 分层授权)                     │
│  · 远期: FHE/MPC 加密执行 (消除 Sequencer 信任)          │
│  · 达成效果: 即使运营者也无法访问特定数据                │
└─────────────────────────────────────────────────────────┘
```

**与下层接口**: 隐私层通过 Zone 架构实现物理隔离，每个 Zone 拥有独立的执行环境、Sequencer 和 DA 后端。Zone 与主链通过 Portal 合约交互（见第 5 节）。

#### 4.2.4 执行层 (Execution Layer)

**职责**: EVM 兼容的交易执行环境，基于 Reth SDK 构建。

**核心设计**:

**自定义预编译集合**: 所有企业级功能通过预编译实现（不可绕过，EVM 执行级强制）

| 地址 | 名称 | Gas 开销 | 功能 |
|---|---|---|---|
| `0x0401` | IdentityRegistry | 2,000 | 身份查询、资质验证 |
| `0x0402` | ComplianceCheck | 5,000 | 交易前合规验证 |
| `0x0403` | PolicyRegistry | 3,000 | TIP-403 兼容策略查询 |
| `0x0404` | EncryptedDeposit | 6,000 | ECIES + Chaum-Pedersen 验证 |
| `0x0405` | SelectiveDisclosure | 8,000 | ZK 选择性披露验证 |

**Payment Lane 机制**: 参考 Tempo 的无状态地址前缀分类

```
每个区块划分三条交易通道:
1. System Lane (最高优先级): 验证者配置、奖励注册
2. Payment Lane (shared_gas_limit): 匹配 0x20C0 地址前缀的 TIP-20 转账
   · 无状态分类: 不需要存储访问即可路由
   · 独立 gas 预算: 不受 General Lane 拥堵影响
3. General Lane (上限 30M gas): 智能合约、DeFi — 不能挤占 Payment
```

**性能优化路径**:

| 优化 | 技术 | TPS 影响 | 优先级 |
|---|---|---|---|
| MDBX 状态存储 | 替代 LevelDB | 2-3x I/O 提升 | P0 (Reth 默认) |
| 并行 EVM | 乐观并发控制 (Monad/Sei 模式) | 4-8x | P1 |
| Payment Lane 分离 | 无状态地址前缀匹配 | Payment 通道独立 SLA | P1 |
| 状态过期 | EIP-7736 状态树优化 | 减少磁盘 I/O | P2 |

**与下层接口**: 通过 Reth SDK `EngineApi` 与共识层交互。共识层通过 `ForkchoiceState` 通知执行层已确认的区块。

#### 4.2.5 共识层 (Consensus Layer)

**职责**: 提供亚秒级确定性终局的区块共识。

**主链共识: Simplex BFT**

关键架构决策——**双运行时隔离**（参考 Tempo）:

```
┌──────────────────────────────────────────────┐
│                 Process                        │
│  ┌─────────────────┐  ┌─────────────────────┐│
│  │ Tokio Runtime A  │  │  Tokio Runtime B    ││
│  │ (Consensus)      │  │  (Execution)        ││
│  │                  │  │                      ││
│  │ · Simplex BFT    │  │  · Reth SDK / revm  ││
│  │ · BLS 签名       │  │  · 交易执行         ││
│  │ · VRF 选举       │  │  · 状态更新         ││
│  │ · 区块提议       │  │  · 预编译调用       ││
│  └────────┬─────────┘  └──────────┬──────────┘│
│           │     Engine API        │            │
│           └───────────────────────┘            │
└──────────────────────────────────────────────┘
```

这确保了：
- 执行层的高负载（如批量合规检查）不会影响共识延迟
- 共识消息处理有独立的资源保证
- 两者通过 Engine API 异步通信

**Zone 共识: NoopConsensus**

Zone 采用单 Sequencer 模式，无 P2P 共识开销：
- `NoopConsensus + NoopNetworkBuilder` — 零网络开销
- 区块生产由主链 L1 事件驱动（每个主链区块触发恰好一个 Zone 区块）
- `head = safe = finalized` 始终成立
- 终局性继承自主链的 BFT 终局

**验证者管理**: 通过 `ValidatorConfig` 预编译管理验证者集合的加入、退出和权重变更。

#### 4.2.6 数据层 (Data Availability Layer)

**职责**: 为不同隐私级别的数据提供可靠的可用性保证。

**混合 DA 设计**:

| DA 类型 | 适用场景 | 存储位置 | 访问控制 | 安全保证 |
|---|---|---|---|---|
| **公开 DA** | 主链公开交易、DeFi | Ethereum L1 Blob | 任何人可读 | Ethereum 永久存储 |
| **Zone DA** | Zone 内隐私交易 | 运营者私有 DB | 认证 RPC + 权限检查 | 运营者可信度 + 可选 DAC |
| **审计 DA** | 合规审计数据 | 加密存档 | 监管者专用密钥 | 密码学访问控制 |

**路由规则**: DA 策略是每笔交易的路由决策——由 Zone 类型和交易属性自动决定。

**GDPR 合规**: Zone DA（链下存储）原生支持数据删除（Right to Erasure），这是 Rollup 模型（L1 链上永久存储）无法实现的。只有 Validium/Zone 模型和 Canton 的分布式投影满足 GDPR。

#### 4.2.7 结算/锚定层 (Settlement/Anchoring Layer)

**职责**: 将主链状态锚定到 Ethereum L1，提供数学级别的安全保证。

**锚定流程**:

```
主链 BFT 确认 → 状态根累积 → 每 N 个 epoch:
  1. 生成 ZK 有效性证明 (覆盖 N 个 epoch 的状态转换)
  2. 提交 (stateRoot, proof, epochRange) 到 Ethereum L1
  3. L1 Verifier 合约验证 proof
  4. 验证通过 → stateRoot 在 L1 上确认 → 跨链桥可用
```

**ZK 证明系统选择**: 参考 Prividium Airbender 方向——RISC-V 证明器、CUDA GPU 加速、亚秒级证明生成。Reth SDK 的 `no_std` 预编译设计已为 SP1/RISC-V 证明器做好准备。

**跨链桥设计**: ZK 证明保护的双向桥——不同于 Optimistic Rollup 的 7 天挑战期，ZK 桥可以在 L1 确认后立即完成资产转移。

---

## 5. 多链/多 Zone 架构设计

### 5.1 Zone 拓扑总览

```
                        ┌──────────────────────┐
                        │    Ethereum L1         │
                        │  · ZK Verifier         │
                        │  · Bridge Contract     │
                        └──────────┬─────────────┘
                                   │  ZK Proof + State Root
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     公开主链 (Public Mainchain)                       │
│                                                                       │
│  Simplex BFT 共识 · 公开 DeFi · 资产发行注册表 · 全局流动性池        │
│  Zone 治理合约 · PolicyRegistry · IdentityRegistry                   │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────────┐   │
│  │ Zone     │  │ Zone     │  │ Zone     │  │ Zone Factory       │   │
│  │ Portal A │  │ Portal B │  │ Portal C │  │ · createZone()     │   │
│  │ (RWA)    │  │ (xStocks)│  │ (Payment)│  │ · configureZone()  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │ · destroyZone()   │   │
│       │             │             │          └────────────────────┘   │
└───────┼─────────────┼─────────────┼──────────────────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌─────────────┐ ┌───────────────┐ ┌─────────────────┐
│  RWA Zone    │ │ xStocks Zone│ │ Payment Zone  │ │ Custom Zone(s)  │
│              │ │             │ │               │ │                 │
│ · 子交易级   │ │ · 暗池级    │ │ · >10K TPS    │ │ · 企业自建      │
│   隐私       │ │   隐私      │ │ · 亚秒级终局  │ │ · Factory 创建  │
│ · 机构准入   │ │ · HFT 优化  │ │ · <$0.001/tx  │ │ · 自定义策略    │
│ · DVP 结算   │ │ · T+0 结算  │ │ · Payment Lane│ │ · 独立 Seq      │
│ · 合规审计   │ │ · 市场监控  │ │ · Travel Rule │ │                 │
│ · Viewing Key│ │ · Reg NMS   │ │ · 多币种      │ │                 │
│ · 12h finality││ · <100ms    │ │ · Stablecoin  │ │                 │
│  acceptable  │ │   latency   │ │   gas token   │ │                 │
└──────────────┘ └─────────────┘ └───────────────┘ └─────────────────┘
```

### 5.2 各 Zone 详细设计

#### 5.2.1 公开主链 (Public Mainchain)

**角色**: 全系统的信任锚点和协调层

**职责**:
- 运行 Simplex BFT 共识，提供亚秒级确定性终局
- 承载公开 DeFi 协议（AMM、借贷、流动性挖矿）
- 维护全局资产发行注册表——所有叙事的资产首先在主链注册
- 运行 Zone 治理合约（Zone 创建、配置、销毁）
- 存储全局 PolicyRegistry 和 IdentityRegistry（自动同步到所有 Zone）
- 作为跨 Zone 资产流转的中转站

**性能目标**: ~3,000-5,000 TPS（BFT 共识 + Reth SDK 执行），亚秒级终局

#### 5.2.2 RWA Zone

**适配叙事需求** (WHI-355):

| 需求 | Zone 实现 |
|---|---|
| 隐私 (5/5) | Viewing Key 分层授权 + 选择性披露预编译。Phase 2: ZK 子交易证明 |
| 准入 (5/5) | 机构级白名单：只有通过 KYC/KYB 的合格投资者可以进入 Zone |
| 合规 (5/5) | SEC Reg D/S/A+、EU MiCA、MAS 合规策略在 PolicyRegistry 中配置；Observer 角色允许监管者直接数据访问 |
| 终局性 (4/5) | 继承主链 BFT 终局（亚秒级）+ Zone 即时终局 (`head=safe=finalized`) |
| 身份 (5/5) | IdentityRegistry 预编译 — 链上 KYC 状态、投资者资质、跨平台互认 |
| 互操作 (4/5) | SWIFT ISO 20022 网关、CSD/DTCC 集成（链下 API 桥接） |
| 数据主权 (4/5) | GDPR + SEC 5-7 年留存的冲突通过可配置数据保留策略解决——Zone DA 支持物理删除 |

**性能目标**: ~100-500 TPS（足够应对机构级 RWA 交易量），合规检查延迟 <200ms

#### 5.2.3 xStocks Zone

**适配叙事需求** (WHI-355):

| 需求 | Zone 实现 |
|---|---|
| 隐私 (5/5) | 暗池引擎：交易对手身份、价格、数量全保密；大持仓者仓位隐私 |
| 终局性 (5/5) | T+0 原子结算——继承主链 BFT 亚秒终局 |
| 性能 (4/5) | HFT 优化: <100ms 延迟、>5,000 TPS 峰值（订单簿匹配） |
| 合规 (5/5) | SEC Reg NMS（价格保护）、Reg SHO（卖空限制）、Regulation ATS；实时市场监控系统 |
| 审计 (5/5) | 完整的订单到结算审计轨迹；SAR/STR 报告生成；实时市场监控（Canton Observer 模式） |

**专用组件**:
- **暗池引擎**: 加密订单簿匹配——订单提交时加密，只有匹配引擎看到明文
- **市场监控模块**: 实时订单流分析、内幕交易/操纵检测、SAR/STR 自动生成
- **T+0 结算引擎**: 原子 DvP——代币交付和资金支付在同一交易中完成

**性能目标**: >5,000 TPS 峰值，<100ms 延迟，亚秒级确定性终局

#### 5.2.4 Payment Zone

**适配叙事需求** (WHI-355):

| 需求 | Zone 实现 |
|---|---|
| TPS (5/5) | >10,000 TPS — Payment Lane 独立 gas 预算 + 并行执行 |
| 终局性 (5/5) | 亚秒级确定性终局——扫码→即时确认 |
| 费用 (5/5) | <$0.001/tx — 固定低费率 Gas 模型 + Sequencer 赞助 |
| 隐私 (4/5) | 支付流和金额对竞争对手隐藏。B2B 企业机密；B2C 对非参与方隐私 |
| 合规 (4/5) | Travel Rule (≥$3,000 转账附带发送方/接收方信息)、AML/CFT、制裁筛查 |
| 多币种 (4/5) | USDC、USDT、EURC 原生支持；链上 FX 兑换 (AMM) |

**专用组件**:
- **Payment Lane**: 无状态地址前缀分类 (0x20C0)，独立 gas 预算，不受通用交易拥堵影响
- **稳定币 Gas Token**: 用户可以用 USDC/USDT 支付 gas 费用（Sequencer 自动换算）
- **ECIES 加密存款**: 存款时加密 (recipient, memo)，Chaum-Pedersen 证明验证正确解密
- **Travel Rule 引擎**: 自动在 ≥$3,000 转账中附带发送方/接收方机构信息

**性能目标**: >10,000 TPS 峰值，亚秒级终局，<$0.001/tx

#### 5.2.5 Custom Zones (自定义 Zone)

**角色**: 企业或用户自建的隐私执行环境。

**创建方式**: 通过主链上的 `ZoneFactory` 合约程序化创建（参考 Tempo `ZoneFactory.createZone()` 模式）。

**配置参数**:
- `sequencerAddress`: Zone Sequencer 的地址
- `eciesPublicKey`: 加密存款使用的公钥
- `policyConfig`: 准入策略配置（从主链 PolicyRegistry 选择或自定义）
- `daConfig`: DA 配置（私有 DB / DAC / 混合）
- `gasConfig`: Gas 定价模型（固定/动态/赞助）

**运营模型**: 每个 Zone 有独立的 Sequencer——可以是创建者自运营，也可以委托给平台运营。Zone 之间物理隔离——独立状态、独立 DA、独立 RPC 端点。

### 5.3 跨 Zone 互操作

#### 5.3.1 资产流转机制

```
Zone A → 公开主链 → Zone B (两步桥接)

步骤 1: Zone A 提款
  1. 用户调用 ZoneOutbox.requestWithdrawal(token, amount, destination)
  2. Zone A Sequencer 批量打包提款请求
  3. Sequencer 调用 ZonePortalA.submitBatch(
       blockTransition, depositQueueTransition,
       withdrawalQueueHash, proof)
  4. 主链验证 proof（ZK 有效性证明或 BFT Sequencer 签名）
  5. 用户调用 ZonePortalA.processWithdrawal() — 资产回到主链

步骤 2: Zone B 存款
  6. 用户调用 ZonePortalB.deposit(token, amount) 或
     ZonePortalB.depositEncrypted(token, ECIES_payload) (隐私存款)
  7. Zone B Sequencer 观察主链 DepositMade 事件
  8. Zone B Sequencer 执行 TIP-403 策略检查
  9. 合规 → 资产在 Zone B 中生效；不合规 → 存款被退回
```

#### 5.3.2 跨 Zone 原子交换

**当前限制**: 跨 Zone 交换是**非原子的**——两步桥接存在时间窗口（类似 Canton 的 Reassignment 协议——Unassign + Assign 之间资产暂时不可用）。

**远期解决方案**:
- **Option A**: 引入 Canton 式 Global Synchronizer，在主链上实现跨 Zone 2PC 协调
- **Option B**: ZK 跨链证明——Zone A 生成证明 "资产已锁定"，Zone B 验证后直接释放对应资产
- **Option C**: Hash Time-Lock Contracts (HTLC) 在两个 Zone 和主链上部署

**推荐**: Phase 1 采用两步桥接（简单可靠），Phase 2 评估 2PC 或 ZK 跨链方案。

### 5.4 Zone 治理

**Zone 生命周期管理**:

| 操作 | 治理要求 | 执行者 |
|---|---|---|
| **Zone 创建** | 主链治理提案 或 ZoneFactory 权限 | 平台运营者 / DAO |
| **Zone 配置变更** | Zone 管理员多签 | Zone Sequencer 运营者 |
| **Zone 策略更新** | 主链 PolicyRegistry 更新（自动同步到所有 Zone） | 合规管理员 |
| **Zone 暂停** | 主链治理或紧急管理员操作 | 平台运营者 |
| **Zone 销毁** | 主链治理提案 + 资产迁移完成确认 | DAO + Zone 运营者 |

**策略同步机制**: 主链 PolicyRegistry 的更新在下一个区块自动镜像到所有 Zone（参考 Tempo `TempoStateReader` 预编译 + per-block GC `SharedPolicyCache`）。

---

## 6. 与 M3 方案的架构差异对比

### 6.1 核心差异矩阵

| 维度 | M3（最小侵入） | M4（推倒重建） | 差异本质 |
|---|---|---|---|
| **执行层** | op-geth（三层 Go fork 链） | Reth SDK（Rust 原生模块化） | 架构自由度：三层 fork 限制 vs. 从零设计 |
| **共识** | 中心化 Sequencer + Optimistic Rollup | Simplex BFT + ZK L1 锚定 | 终局性模型：7 天/12 小时 vs. 亚秒级确定性 |
| **隐私** | Validium 改造（合约级） | 原生多 Zone（物理隔离 + 多层次） | 隐私粒度：全有/全无 vs. 分层渐进 |
| **合规** | 合约层 bolt-on（预部署合约模拟） | 协议层内置（预编译级 + ZK 合规证明） | 合规深度：可绕过 vs. 不可绕过 |
| **准入控制** | Sequencer 策略 + 预部署 | 五层纵深防御 (IAM→RPC→Sequencer→预编译→L1 桥) | 安全边界：L1 强制交易可绕过 vs. 全路径覆盖 |
| **性能** | ~1,000 TPS 单引擎天花板 | >10,000 TPS（并行 EVM + Payment Lane） | 性能天花板：10× 差距 |
| **多租户** | 12-18 个月后 Phase 3 Zone | 原生 Zone 架构（Day 1） | 时间差距：远期 vs. 内置 |
| **Ethereum 关系** | L2 Rollup（完全依赖） | 混合（独立 BFT + 可选 ZK 锚定） | 依赖模型：完全 vs. 选择性 |
| **上游风险** | 持续加深 OP Stack 分歧（6 次硬分叉） | 完全独立——无上游合并负担 | 维护成本：累积 vs. 可控 |
| **开发工作量** | 低-中（增量修改） | 高（全面重建） | 实施难度：权衡 |
| **风险级别** | 低（在已验证基础上迭代） | 高（新架构需验证） | 技术风险 |

### 6.2 叙事适配度对比

| 叙事 | M3 适配度 | M4 适配度 | M4 关键优势 |
|---|---|---|---|
| **DeFi** | 4.7/5 ✅ | 4.8/5 ✅ | BFT 终局替代 7 天挑战期 |
| **供应链金融** | 4.1/5 ✅ | 4.5/5 ✅ | 原生 Zone 隔离 + 协议级合规 |
| **RWA 非实时** | 3.7/5 ✅ | 4.8/5 ✅ | 原生隐私 Zone + Observer 审计 |
| **RWA 实时 DVP** | 2.5/5 ⚠️ | 4.5/5 ✅ | BFT 亚秒终局 + Zone 子交易隐私 |
| **xStocks HFT** | 2.9/5 ❌ | 4.3/5 ✅ | T+0 原子结算 + <100ms + 暗池 |
| **Payment B2B** | 3.5/5 ⚠️ | 4.7/5 ✅ | BFT 终局 + Zone 隐私 |
| **Payment B2C** | 2.5/5 ❌ | 4.5/5 ✅ | >10K TPS + 亚秒终局 + Payment Lane |

### 6.3 关键数值对比

| 指标 | M3 (Phase 2 完成) | M4 (完整实现) | 倍数提升 |
|---|---|---|---|
| 硬终局性 | ~12 小时 (SP1 ZK) | ~600ms (BFT) | **72,000×** |
| 软终局性 | ~2s (Sequencer ACK) | ~600ms (BFT 确定性) | **3.3×** + 安全性质变 |
| TPS (通用) | ~1,000 (reth 单引擎) | ~3,000-5,000 (主链) | **3-5×** |
| TPS (Payment) | ~1,000 (共享通道) | >10,000 (独立 Zone + Payment Lane) | **>10×** |
| 隐私粒度 | 合约级 (Viewing Key) | 子交易级 (多层隐私) | 质变 |
| 合规执行 | 可绕过 (L1 强制交易) | 不可绕过 (五层纵深) | 质变 |
| Zone 可用时间 | 12-18 个月后 (Phase 3) | Day 1 | **>12 个月提前** |

### 6.4 M3/M4 不是非此即彼

**关键洞见**: M3 和 M4 可以**共存**。

- M3 路径继续服务 DeFi、供应链金融、RWA 非实时场景（这些叙事 M3 已经足够好）
- M4 路径专注于 xStocks HFT 和 Payment B2C（这些叙事 M3 无法胜任）
- M4 主链可以与 Mantle L2 (M3) 通过 Ethereum L1 互操作——两条链共享 Ethereum 安全锚定

**实施策略**: 先在 M3 上交付可交付的部分（6-12 个月），同时并行开发 M4 架构（12-24 个月）。M4 上线后，高要求叙事迁移到 M4，M3 继续运行低要求叙事。

---

## 7. 关键技术创新点

### 7.1 借鉴与溯源

| 创新点 | 来源项目 | 原设计 | 本蓝图采纳 | 为什么借鉴 |
|---|---|---|---|---|
| **子交易级隐私哲学** | Canton | Merkle DAG 投影——每方只看到自己有权看到的子树 | 借鉴"最小知情"哲学，但不采用 Daml/Merkle DAG——在 EVM 上通过 Viewing Key + ZK 选择性披露近似实现 | Canton 是唯一实现子交易级隐私的项目，但其实现路径（Daml + 无全局状态）与 EVM 不兼容 |
| **Observer 审计角色** | Canton | 监管者作为 Daml `observer` 参与者，直接访问交易数据 | 在 Zone 架构中实现 Observer 模式——监管者 RPC 具有完整数据访问权限 | 比 Prividium 的"事后导出审计"更实时、更全面；监管者看到的是真实数据，不只是证明 |
| **四层准入控制** | Prividium | SSO → Proxy RPC → RBAC → L1 TransactionFilterer | 扩展为五层纵深防御 (IAM→认证 RPC→Sequencer 策略→预编译注册表→L1 桥过滤器) | 最全面的企业准入方案；增加预编译层弥补中间件层被绕过的风险 |
| **Default Forbidden 权限** | Prividium | 合约部署后所有函数默认不可访问，需管理员逐一授权 | 作为 Zone 的默认安全策略 | "安全即默认"比"默认开放再加锁"更符合企业安全模型 |
| **ZK 合规证明** | Prividium | STARK 证明"对手方不在 OFAC SDN 名单上"——无需传输 PII | 作为远期合规目标——Phase 3 实现 | 解决 AML 数据共享要求与 GDPR 之间的根本矛盾——目前没有其他解决方案 |
| **Payment Lane** | Tempo | 无状态地址前缀分类 (0x20C0)，独立 gas 预算 | 直接采用 Payment Lane 机制 | 协议级 SLA 保证——支付交易吞吐不受通用交易拥堵影响 |
| **TIP-403 策略注册表** | Tempo | 预编译级合规策略 (allow/reject/whitelist/blacklist/compound) | 作为 PolicyRegistry 预编译 (0x0403) 的设计基础 | 预编译级强制执行——无法通过低级 EVM 调用绕过 |
| **双运行时隔离** | Tempo | 共识和执行在独立 Tokio 运行时——互不影响 | 直接采用双运行时架构 | 防止执行负载峰值影响共识延迟——对亚秒级终局至关重要 |
| **ECIES 加密存款** | Tempo | ECIES + Chaum-Pedersen 证明——可验证正确解密 | 作为 Zone 加密桥存款的实现方案 | 密码学可验证——链上 precompile 验证解密正确性 (6,000 gas) |
| **L1 事件驱动 Zone** | Tempo | `NoopConsensus` + Engine API + 1:1 区块映射 | 作为 Zone 的区块生产模式 | 最小化 Zone 开销——零 P2P、零共识复杂度 |
| **`no_std` ZK 就绪纪律** | Tempo | 所有预编译设计为 `no_std` 兼容，SP1/RISC-V 可运行 | 作为所有自定义预编译的设计约束 | 为 BFT → ZK 迁移路径提前做好架构准备 |
| **Validium DA** | Prividium + Tempo | 链下 DA + 有效性证明 | Zone DA 采用 Validium 模式 | 唯一同时满足数据隐私和 GDPR Right to Erasure 的 DA 方案 |

### 7.2 改进与增强

| 改进点 | 原设计 | 本蓝图改进 | 为什么更好 |
|---|---|---|---|
| **Zone 创建机制** | Tempo: 硬编码 Zone 部署 | 程序化 Zone Factory——通过合约调用创建新 Zone，可配置参数 | 支持多租户平台模式——企业可以自助创建专属 Zone |
| **跨 Zone 策略同步** | Tempo: TempoStateReader per-block GC | 增强为双向同步——Zone 可以向主链报告本地策略执行结果（审计反馈） | 闭环合规——不只是策略下发，还有执行验证 |
| **混合终局模型** | Prividium: ZK 终局仅对 L1 | BFT 即时终局 + ZK L1 锚定——两种终局语义并存 | 日常交易享受亚秒终局，跨链结算享受数学安全——两全其美 |
| **准入控制深度** | Prividium 四层; Tempo 预编译层 | 五层融合——将 Prividium 的中间件层和 Tempo 的预编译层合并为完整纵深 | 消除单层被绕过的系统性风险 |
| **隐私分层** | 各项目各做一种隐私 | 三层隐私模型（准入控制 → DA 隐私 → 密码学隐私）渐进实现 | 不需要一次性部署完整 ZK 堆栈——从路由层隐私开始，逐步升级 |
| **Gas 模型多样化** | Tempo: Payment Lane 固定 gas | 按 Zone 类型差异化 Gas 策略——Payment Zone 固定低费率、RWA Zone 合规操作免 gas、主链标准 EIP-1559 | 不同叙事不同成本模型——Payment 需要极低费用，RWA 需要合规操作零摩擦 |

### 7.3 全新设计

| 全新设计 | 描述 | 为什么需要 | 现有项目为何没有 |
|---|---|---|---|
| **叙事驱动 Zone 配置模板** | 每个叙事（RWA/xStocks/Payment）有预设的 Zone 配置模板——隐私级别、合规策略、性能参数、Gas 模型、审计要求一键配置 | 降低企业部署门槛——不需要理解底层技术栈即可获得叙事优化的执行环境 | Canton/Prividium/Tempo 都是通用平台，没有叙事专属配置 |
| **跨 Zone 资产注册表** | 主链维护全局资产注册表——所有 Zone 中的资产都在主链注册元数据（资产类型、发行者、合规要求），Zone 持有实际余额 | 防止资产在 Zone 间流转时丢失合规上下文；支持跨 Zone 资产搜索和报告 | Canton 无全局状态；Prividium/Tempo 单链模型不需要 |
| **合规策略市场** | 主链上的策略注册表支持"策略市场"——预设合规策略（SEC Reg D、MiCA、Travel Rule、OFAC）可以像软件包一样选用和组合 | 降低合规实施成本——企业不需要从零编写合规规则，而是从经过验证的策略库中选择 | 各项目的合规都是一次性定制实现 |
| **审计数据通道** | 专用的审计 DA 通道——交易数据加密后单独存储，监管者使用专用密钥解锁 | 在交易隐私和监管审计之间找到平衡——交易方看到的是隐私的，监管者看到的是完整的 | Canton Observer 最接近，但不是加密通道模式 |
| **Sequencer-as-Compliance-Officer 模式** | 将 Sequencer 的全数据可见性从"隐私缺陷"重新定义为"合规资产"——Sequencer 即合规官 | 在 Validium/Zone 单 Sequencer 模型中，Sequencer 必然看到所有数据——与其试图消除这一事实，不如利用它作为合规基础设施 | WHI-349 识别出的行业趋势，但未被任何项目系统化实现 |

---

## 8. 分阶段实施路线图

### 8.1 Phase 概览

```
Phase 0: 基础设施 (0-6 个月)
  ├── Reth SDK 节点框架搭建
  ├── Simplex BFT 集成
  ├── 基础预编译集合
  └── 测试网启动

Phase 1: 核心功能 (6-12 个月)
  ├── Zone 架构实现
  ├── ZonePortal 桥合约
  ├── PolicyRegistry + IdentityRegistry
  ├── Payment Lane
  └── 认证 RPC + Sequencer 策略引擎

Phase 2: 叙事 Zone (12-18 个月)
  ├── RWA Zone (Viewing Key + 合规审计)
  ├── Payment Zone (高 TPS + 低费率)
  ├── xStocks Zone (暗池 + 市场监控)
  └── ZoneFactory (自定义 Zone 创建)

Phase 3: 高级功能 (18-24 个月)
  ├── ZK Ethereum L1 锚定
  ├── ZK 合规证明
  ├── 并行 EVM 执行
  ├── 跨 Zone 原子交换
  └── 正式主网启动
```

### 8.2 各 Phase 详细交付物

#### Phase 0: 基础设施 (0-6 个月)

| 交付物 | 描述 | 参考 | 依赖 |
|---|---|---|---|
| Reth SDK 节点框架 | `MantleFullNode` 基于 `reth-node-builder`，自定义 `NodeTypes` + `EngineTypes` | Tempo `TempoFullNode` | 无 |
| Simplex BFT 集成 | 双 Tokio 运行时架构——共识和执行隔离 | Tempo 双运行时 | 节点框架 |
| 基础预编译集合 | IdentityRegistry (0x0401), PolicyRegistry (0x0403) | Tempo TIP-403 | 节点框架 |
| 测试网 | 4 节点 BFT 测试网，验证亚秒终局 | — | 以上全部 |

#### Phase 1: 核心功能 (6-12 个月)

| 交付物 | 描述 | 参考 | 依赖 |
|---|---|---|---|
| Zone 引擎 | NoopConsensus + L1 事件驱动区块生产 | Tempo `ZoneEngine` | Phase 0 主链 |
| ZonePortal 合约 | 存款/取款/批量提交/证明验证 | Tempo `ZonePortal` | Phase 0 主链 |
| ECIES 加密存款 | EncryptedDeposit 预编译 (0x0404) + Chaum-Pedersen 验证 | Tempo ECIES 模式 | Zone 引擎 |
| Payment Lane | 无状态地址前缀分类 + 独立 gas 预算 | Tempo Payment Lane | Phase 0 执行层 |
| 认证 RPC | 签名访问令牌 + per-account 数据过滤 + 100ms 最小响应时间 | Tempo Zone auth | Zone 引擎 |
| Sequencer 策略引擎 | 交易池前置合规检查 + L1 桥存款策略过滤 | Tempo `prepare_l1_block()` + Prividium TransactionFilterer | PolicyRegistry |

#### Phase 2: 叙事 Zone (12-18 个月)

| 交付物 | 描述 | 参考 | 依赖 |
|---|---|---|---|
| RWA Zone | Viewing Key 分层授权 + Observer 审计角色 + 机构白名单 | Prividium RBAC + Canton Observer | Phase 1 Zone |
| Payment Zone | >10K TPS 优化 + 固定低费率 + 稳定币 Gas + Travel Rule | Tempo Payment Lane + Payment Zone | Phase 1 Zone + Payment Lane |
| xStocks Zone | 暗池引擎 + T+0 结算 + 市场监控模块 | 全新设计 | Phase 1 Zone |
| ZoneFactory | 合约化 Zone 创建 + 叙事模板 + 参数配置 | Tempo `ZoneFactory.createZone()` 模式 | Phase 1 Zone |
| 合规策略市场 | 预设策略库 (SEC Reg D, MiCA, Travel Rule, OFAC) | 全新设计 | PolicyRegistry |

#### Phase 3: 高级功能 (18-24 个月)

| 交付物 | 描述 | 参考 | 依赖 |
|---|---|---|---|
| ZK L1 锚定 | SP1/RISC-V 证明器 + Ethereum Verifier 合约 | Prividium Airbender + Tempo SP1 准备 | Phase 0 `no_std` 预编译 |
| ZK 合规证明 | 无 PII 制裁筛查 STARK 证明 | Prividium ZK 合规证明方向 | ZK L1 锚定基础设施 |
| 并行 EVM | 乐观并发控制——状态分区 + 投机执行 | Monad/Sei 模式 | Phase 0 执行层 |
| 跨 Zone 原子交换 | 主链协调的 2PC 或 ZK 跨 Zone 证明 | Canton 2PC / Prividium ZK Bridge | Phase 1 ZonePortal |
| 正式主网 | 全功能主网启动 | — | 以上全部 |

### 8.3 资源估算

| Phase | 时间 | 核心工程师 | 关键风险 |
|---|---|---|---|
| Phase 0 | 6 个月 | 5-8 (Rust + 区块链) | Reth SDK + Simplex BFT 集成复杂度 |
| Phase 1 | 6 个月 | 8-12 | Zone 架构可靠性、桥安全审计 |
| Phase 2 | 6 个月 | 10-15 | 叙事需求变化、性能调优 |
| Phase 3 | 6 个月 | 12-18 | ZK 证明系统成熟度、并行 EVM 正确性 |

---

## 9. 开放问题与待决策项

### 9.1 架构级待决策

| 编号 | 问题 | 选项 | 建议 | 影响范围 |
|---|---|---|---|---|
| **OQ-1** | Simplex BFT 验证者集规模和准入模式 | (A) 许可制 BFT (B) PoS + 质押 (C) 混合 | 许可制 BFT 启动，后续支持 PoS | 共识层安全模型 |
| **OQ-2** | ZK L1 锚定频率 | (A) 每 epoch (B) 每小时 (C) 每天 | 取决于 L1 gas 成本和跨链桥使用频率 | 结算层成本/延迟 |
| **OQ-3** | Zone 数据可用性保证级别 | (A) 纯 Sequencer DA (B) DAC (C) 混合 | Phase 1 纯 Sequencer，Phase 2 评估 DAC | Zone 安全模型 |
| **OQ-4** | MNT Token 在新架构中的角色 | (A) 继续作为 Gas Token (B) 质押 Token (C) 治理 Token (D) 全部 | 需要 Token 经济学专项评估 | Token 经济学 |
| **OQ-5** | 与现有 Mantle L2 (M3) 的互操作方式 | (A) Ethereum L1 桥 (B) 直接跨链消息 (C) 不互操作 | L1 桥（最低风险） | 生态迁移策略 |

### 9.2 技术实现待验证

| 编号 | 问题 | 需验证内容 | 预计验证时间 |
|---|---|---|---|
| **TV-1** | Reth SDK + Simplex BFT 的集成可行性 | PoC: 4 节点 BFT 测试网，验证 <1s 终局 | 8-12 周 |
| **TV-2** | 并行 EVM 在 Reth SDK 上的实现路径 | PoC: 乐观并发控制 + 状态冲突检测 | 12-16 周 |
| **TV-3** | Payment Lane >10K TPS 的可达性 | 基准测试: 单 Zone + Payment Lane 配置 | 8-12 周 |
| **TV-4** | ZK 有效性证明的生成效率和成本 | PoC: SP1/RISC-V 证明器 + 基准测试 | 16-24 周 |
| **TV-5** | ECIES + Chaum-Pedersen 在 Reth 预编译中的 gas 成本 | 实现 + gas 基准测试 | 4-6 周 |

### 9.3 业务和生态待确认

| 编号 | 问题 | 需确认方 |
|---|---|---|
| **BQ-1** | RWA Zone 的首批机构客户和具体合规要求 | 业务团队 + 合规团队 |
| **BQ-2** | xStocks Zone 是否需要 SEC Regulation ATS 牌照 | 法务团队 |
| **BQ-3** | Payment Zone 的目标市场和监管管辖 | 业务团队 + 法务团队 |
| **BQ-4** | M3→M4 迁移期间现有用户和 DApp 的兼容性策略 | 生态团队 |
| **BQ-5** | Zone Sequencer 运营模式——平台运营 vs. 企业自运营 vs. 委托运营 | 业务团队 |

### 9.4 后续深入设计 Issue 映射

本蓝图的各层设计将在后续 Issue 中深入：

| Issue | 层次 | 蓝图对应章节 | 深入方向 |
|---|---|---|---|
| WHI-358 | 执行层 | §3.1, §4.2.4 | Reth SDK 集成详细设计、预编译实现 |
| WHI-359 | 共识层 | §3.2, §4.2.5 | Simplex BFT 集成、双运行时架构 |
| WHI-360 | 隐私层 | §4.2.3, §5.2 | 多层隐私模型、ECIES 实现 |
| WHI-361 | 合规层 | §4.2.2, §7.1 | PolicyRegistry、ZK 合规证明 |
| WHI-362 | 数据层 | §4.2.6 | 混合 DA、审计数据通道 |
| WHI-364 | 多 Zone | §5 | Zone 架构、跨 Zone 互操作 |
| WHI-365 | 结算层 | §3.3, §4.2.7 | ZK L1 锚定、双重终局 |
| WHI-366 | 性能 | §4.2.4 | 并行 EVM、Payment Lane |
| WHI-367 | 身份 | §4.2.2 | IdentityRegistry、跨平台互认 |
| WHI-368 | 治理 | §5.4, §9.1 | Zone 治理、Token 经济学 |

---

## 附录 A: 术语表

| 术语 | 含义 |
|---|---|
| **BFT** | Byzantine Fault Tolerance（拜占庭容错） |
| **Simplex BFT** | Commonware 的 BFT 共识协议，被 Tempo 采用 |
| **Zone** | 隐私执行环境——独立状态、Sequencer、DA 的隔离链 |
| **Validium** | 链下 DA + 有效性证明的 L2 方案 |
| **Payment Lane** | 协议级支付交易优先通道 |
| **DA** | Data Availability（数据可用性） |
| **DAC** | Data Availability Committee（数据可用性委员会） |
| **DVP** | Delivery versus Payment（货银两讫） |
| **T+0** | 交易日当日结算 |
| **ECIES** | Elliptic Curve Integrated Encryption Scheme |
| **Chaum-Pedersen** | 零知识离散对数证明 |
| **TIP-403** | Tempo 的合规策略预编译标准 |
| **Observer** | Canton 的审计角色模型——监管者作为交易参与者直接访问数据 |
| **Viewing Key** | 分层加密访问密钥——不同级别的观察者看到不同层次的数据 |
| **FHE** | Fully Homomorphic Encryption（全同态加密） |
| **MPC** | Multi-Party Computation（多方计算） |

## 附录 B: 参考文献

| ID | 文档 | 引用内容 |
|---|---|---|
| WHI-335 | Canton 架构分析 | Daml 执行模型、Merkle DAG 投影隐私、Observer 角色、2PC 共识 |
| WHI-338 | Prividium 架构深度分析 | ZK Stack Validium、四层准入控制、ZK 合规证明、Default Forbidden |
| WHI-340 | Tempo 代码分析 | Reth SDK 集成、Simplex BFT、Payment Lane、TIP-403、Zone 架构、ECIES 加密存款 |
| WHI-341 | Mantle v2 架构基线 | OP Stack、Arsia fork、Alt-DA 框架、Preconf 模块 |
| WHI-343 | 隐私横向对比 | 三种隐私范式、反向隐私-复杂度法则、分阶段隐私架构 |
| WHI-344 | 准入控制横向对比 | 五层纵深防御、L1 强制交易绕过风险、企业 IAM 集成 |
| WHI-345 | 共识/DA 横向对比 | BFT vs Optimistic vs ZK、混合 DA 策略 |
| WHI-346 | 合规横向对比 | 合规集成层级、ZK 合规证明、监管框架映射 |
| WHI-347 | 互操作性横向对比 | 跨链通信模式、原子交换、ZK 桥 |
| WHI-348 | 项目综合分析报告 | 总体能力排名、叙事适配推荐 |
| WHI-349 | 企业级设计模式报告 | 设计模式库(P1-P8)、实施优先级、推荐架构 |
| WHI-355 | 叙事需求分析 | 各叙事具体需求、跨叙事共享需求、叙事冲突、优先级排名 |
| WHI-356 | M3 适配度评估 | M3 适配度评分、结构性瓶颈、不可修复缺陷、M3/M4 边界 |
