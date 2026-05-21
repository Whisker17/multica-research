# WHI-339: Tempo/Zones 官方文档与架构调研

> **Issue**: WHI-339 — Tempo Zones 官方文档与架构调研
> **Milestone**: M1 — 各项目独立深度调研
> **日期**: 2026-05-06（初稿）/ 2026-05-07（Review 修订版）
> **状态**: Review 修订完成
> **数据来源**: 官方文档（docs.tempo.xyz）、Commonware 官网、GitHub 仓库、项目官网（tempo.xyz）、本地文档副本（`.agents/skills/tempo-docs/`）

---

## 目录

1. [项目概述](#1-项目概述)
2. [Tempo L1 核心架构](#2-tempo-l1-核心架构)
3. [Zones L2 隐私架构](#3-zones-l2-隐私架构)
4. [Commonware Simplex BFT 共识](#4-commonware-simplex-bft-共识)
5. [企业级特性评估](#5-企业级特性评估)
6. [与 Canton、Prividium 定位对比](#6-与-cantonprividium-定位对比)
7. [Mantle 适配性分析](#7-mantle-适配性分析)
8. [参考链接](#8-参考链接)

---

## 1. 项目概述

### 1.1 Tempo 是什么？

Tempo 是一条**专为支付场景优化的 Layer-1 区块链**，定位为"the payments-first blockchain"。它是一条兼容 EVM 的通用公链，内置原生稳定币基础设施、亚秒级终局性，并为支付交易提供专属区块空间保障。

**官方描述**: *"A general-purpose blockchain optimized for payments... designed in close collaboration with an exceptional group of design partners"*——合作伙伴用真实支付工作负载验证系统设计。

### 1.2 团队与孵化背景

| 项目 | 详情 |
|------|------|
| **孵化方** | Paradigm + Stripe（tempo.xyz 首页确认） |
| **核心团队** | **Reth**（Paradigm 的 Rust Ethereum 客户端）和 **Foundry**（Solidity 开发框架）的核心开发者 |
| **Commonware 投资** | Tempo 是 Commonware 的"strategic investor"（2025 年 11 月公布） |
| **开源协议** | Apache 2.0 / MIT 双许可 |
| **团队成员** | 官网和文档中未公开披露具体成员 |
| **联系方式** | partners@tempo.xyz（合作咨询） |

> **关键背景**: Tempo 明确标示由 Paradigm 和 Stripe 孵化。团队深度参与 Reth 和 Foundry 的开发是重要背景——Tempo 由构建了 Rust 以太坊执行客户端（驱动 Base 等生产链）的同一批工程师打造。

### 1.3 发展阶段

| 里程碑 | 详情 |
|--------|------|
| **公测网上线** | 2025 年 12 月 9 日（Moderato testnet，Chain ID: `42431`） |
| **主网** | 截至 2026 年 5 月尚未上线 |
| **Zones 状态** | *"Still in early development and available for testing purposes on Tempo Testnet only. Breaking changes are expected."* |
| **代码成熟度** | Tempo L1: v1.6.0（较成熟），Zones: v0.1.0（活跃开发中） |
| **GitHub** | 928 stars，Rust 78.3% |
| **网络升级** | T2、T3、T4 硬分叉已完成（迭代速度快） |

### 1.4 合作伙伴与生态

Tempo 官网展示了 **30+ 合作伙伴 logo**，涵盖以下类别：

- **金融机构**: Deutsche Bank, UBS, Standard Chartered, Mastercard, Visa
- **金融科技**: Brex, Revolut, Klarna, Mercury, Nubank, Payoneer
- **商业/物流**: Shopify, DoorDash, Coupang, Faire
- **企业软件**: Gusto, Deel
- **加密/交易**: OKX, Kalshi
- **AI 公司**: Anthropic, OpenAI

**生态基础设施**: 区块浏览器、跨链桥（LayerZero, Relay）、数据分析服务商、节点基础设施、发行与编排、安全与合规、智能合约库、钱包。

### 1.5 目标用例

- 汇款与跨境支付
- 全球付款与薪资发放
- 嵌入式金融（稳定币轨道）
- 微交易与按用量计费
- Agent 商务（机器对机器支付）
- 代币化存款
- 链上外汇（FX）

---

## 2. Tempo L1 核心架构

### 2.1 Reth SDK 集成模式

Tempo L1 基于 **Reth SDK**（Paradigm 的模块化 Rust 以太坊执行层框架）构建，使用 `reth-node-builder` 模式组装自定义 L1 链。

| 组件 | 来源 | 复用/自定义 |
|------|------|-------------|
| **存储** | MDBX（Reth 原生） | 复用 |
| **执行层网络** | devp2p（Reth 原生） | 复用 |
| **共识层网络** | Commonware P2P（ed25519 认证） | 自定义（独立网络栈） |
| **JSON-RPC** | Reth 原生 + Tempo 扩展 | 扩展 |
| **EVM** | revm v38，目标 Osaka 硬分叉 | 扩展（自定义预编译） |
| **共识** | Commonware Simplex BFT | 完全替换（非 Engine API PoS） |
| **交易类型** | TempoTxEnvelope（EIP-2718 type `0x76`） | 自定义 |
| **区块头** | TempoHeader（扩展以太坊头） | 自定义 |
| **费用系统** | 稳定币计价（attodollars） | 自定义 |

**核心架构特征**: Tempo 运行**双网络栈**——devp2p 用于执行层对等发现/同步，Commonware P2P 用于共识消息传递，二者运行在独立的 Tokio runtime 上。

### 2.2 Payment Lane 架构（核心差异化特征）

Tempo 的区块空间被划分为**三条 Lane**，保证支付交易获得专属吞吐量：

#### Lane 结构

| Lane | 用途 | Gas 预算 |
|------|------|----------|
| **System Lane** | 协议级交易（奖励注册等） | 区块首尾，预定排序 |
| **Payment Lane** | TIP-20 稳定币转账 | 共享 Gas 容量（`general_gas_limit` 消耗后的剩余） |
| **General Lane** | 智能合约调用、DeFi 等 | 受 `general_gas_limit` 上限限制 |

#### Gas 分区机制

区块头将以太坊标准的 `gas_limit` 扩展为两个分区值：

- **`general_gas_limit`**: 非支付交易在 proposer lane 中可消耗的最大 gas
- **`shared_gas_limit`**: 剩余（支付）交易的容量

**有效性规则**: 区块仅在以下条件满足时有效：
```
general_gas_limit >= Σ gas_consumed(tx[i])，对于 proposer lane 中所有非支付交易 tx[i]
```

#### 支付交易分类

交易是否属于**支付交易**仅通过**负载检查**判定（无需状态访问）：

- 接收方地址（`tx.to`）以 TIP-20 支付前缀开头：`0x20c0000000000000000000000000`
- 对于 TempoTransactions，`tx.calls` 中所有条目必须指向带此前缀的地址

**防 Noisy-Neighbor 保证**: 当 `general_gas_limit` 预算耗尽后，即使总 `gas_limit` 仍有剩余，非支付交易也会被阻止。支付交易继续填充剩余共享容量。这为支付场景提供了**确定性吞吐量保障**，不受通用链拥堵影响。

#### 终局性精确说明

| 终局性类型 | 延迟 | 含义 |
|-----------|------|------|
| **Tempo L1 区块终局性（含 Payment Lane）** | ~600ms（Simplex BFT 正常出块） | 确定性终局，零重组风险。Payment Lane 交易继承 Tempo L1 BFT 终局性——Payment Lane 是区块空间/Gas 记账分区，不是独立结算通道 |
| **Zone L2 区块终局性** | 与 L1 同步——每个 L1 区块产生恰好一个 L2 区块 | head = safe = finalized，Zone 终局性绑定到 L1 终局性 |
| **MPP Session voucher 延迟** | 近零（链下） | 这是链下 voucher 延迟，不是链上终局性；最终结算仍通过链上交易完成 |
| **以太坊/L1 锚定** | 不适用（Tempo 自身即为 L1） | Tempo 不锚定到以太坊；Zone validity proof 提交到 Tempo L1 |

#### TempoHeader 扩展字段

| 字段 | 类型 | 用途 |
|------|------|------|
| `timestamp_millis_part` | u16 | 毫秒精度时间戳：`full_timestamp = inner.timestamp * 1000 + timestamp_millis_part` |
| `shared_gas_limit` | u64 | 非标准以太坊头字段，用于 Payment Lane 容量 |
| `general_gas_limit` | u64 | 非标准字段，用于 General Lane 容量 |
| Consensus context | varies | T4 硬分叉（TIP-1031）后嵌入区块头 |

### 2.3 TempoTxEnvelope（自定义交易类型）

Tempo 引入 EIP-2718 交易类型 **`0x76`**，功能集全面：

#### 签名方案（4 种，基于长度检测）

| 类型 | 大小 | 算法 | 用例 |
|------|------|------|------|
| **secp256k1** | 65 bytes | 标准 ECDSA recovery | 传统以太坊钱包 |
| **P256** | 130 bytes | NIST P-256 曲线 | WebAuthn/Passkey 原生 |
| **WebAuthn** | 可变，最大 2KB | WebAuthn assertion | 浏览器原生认证 |
| **Keychain** | 可变 | 通过 AccountKeychain 委托 | Access key 代理根账户签名 |

**P256 地址推导**: `keccak256(abi.encodePacked(pubKeyX, pubKeyY))` → 取后 20 字节作为地址

#### Call Batching（批量调用）

`calls` 向量（`Vec<Call>`）支持**原子批量执行**：所有调用全部成功或整个交易回滚。每个 `Call` 指定目标地址、value 和 calldata。

#### 定时交易

| 字段 | 用途 |
|------|------|
| `valid_after` | 当前时间 < `valid_after` 时交易被拒绝 |
| `valid_before` | 当前时间 > `valid_before` 时交易被拒绝 |

支持归属解锁、限时优惠、延迟执行等模式。

#### 费用赞助（双签名机制）

- **Sender** 使用 magic byte `0x76` 签名（digest 中排除 fee_token）
- **Fee payer** 使用 magic byte `0x78` 签名（包含 fee_token 和 sender_address）
- Domain separation 确保 fee payer 承诺为特定 sender 使用特定 token 支付费用
- 无需 paymaster 合约或 EntryPoint（协议原生支持）

#### 二维并行 Nonce

| Key | 类型 | 行为 |
|-----|------|------|
| Key 0 | 协议 nonce | 传统顺序 nonce |
| Keys 1-N | 用户 nonce | 并行执行，无排序依赖 |

**Gas 成本**: Key 0 = 0 gas；已存在 user key = 5,000 gas；新 user key = 22,100 gas。

Nonce 存储在预编译地址 `0x4E4F4E4345`（ASCII "NONCE"）。

#### Access Keys（TIP-1011）

Root key 可授权具有以下限制的二级密钥：
- **到期时间戳**（时限有效性）
- **每 token 支出限额**，可选周期性重置
- **调用范围**（允许的目标合约和函数选择器白名单）
- Access key 不能调用可变 keychain 函数或创建合约

**AccountKeychain 预编译地址**: `0xAAAAAAAA00000000000000000000000000000000`

### 2.4 TIP-20 原生稳定币标准

TIP-20 是**协议级 token 标准**，以预编译实现而非智能合约：

| 特性 | TIP-20 | ERC-20 |
|------|--------|--------|
| 实现方式 | 原生预编译 | 智能合约 |
| Memo | 内置 32 字节字段 | 无 |
| 转账策略 | TIP-403 集成 | 无 |
| 奖励分配 | 可选的按比例分配 | 无 |
| DEX 报价 token | 内置 | 无 |
| 暂停控制 | 内置 | 可选 |
| 基于角色的访问 | 标准化 | 可选 |
| 小数位 | **固定 6 位** | 可变 |
| Payment Lane | 直接集成 | 不适用 |

**Factory 地址**: `0x20Fc000000000000000000000000000000000000`

**Token 地址方案**: 确定性前缀 `20C000000000000000000000` + `keccak256(msg.sender, salt)` 的最高 64 位。前 1000 个地址保留给协议使用。

**策略执行**: 所有转账通过 `transferAuthorized` 检查对 sender 和 recipient 执行 TIP-403 策略。

**系统函数**（仅协议预编译可调用）：
- `systemTransferFrom()` — 内部转账
- `transferFeePreTx()` — 费用收取（尊重暂停状态）
- `transferFeePostTx()` — 费用退款（暂停时也执行）

#### TIP-20 迁移与集成注意事项

> **面向钱包、索引器、token 发行方和合规运营商的重要说明**：

TIP-20 保留了标准 ERC-20 的函数签名（`transfer`、`approve`、`balanceOf` 等），但作为**预编译套件**实现，与普通 ERC-20 合约存在以下关键差异：

| 维度 | TIP-20 行为 | ERC-20 预期 |
|------|-------------|-------------|
| **存储模型** | 预编译内部存储，无合约 storage slot | 合约 storage 可直接读取 |
| **小数位** | 固定 6 位（不可配置） | 可变，常见 18 位 |
| **Memo 字段** | `transferWithMemo()` 内置 32 字节 memo | 不存在 |
| **合规集成** | 每笔转账自动执行 TIP-403 策略检查 | 无 |
| **费用资格** | 仅满足特定条件的 TIP-20 token 可用于支付 gas | 不适用 |
| **ABI 扩展** | 额外的 `transferWithMemo`、`setTransferPolicies`、`rewardDistribution` 等函数 | 仅标准 ERC-20 ABI |
| **索引方式** | 不能假设普通 ERC-20 合约的 storage 布局；需使用事件或 RPC 查询 | 可直接读取 storage |

**实际影响**：钱包需要适配 6 位小数显示；索引器不应假设合约 storage 行为；token 发行方需要了解 TIP-403 策略绑定；合规运营商需理解 `transferAuthorized` 前置检查机制。

### 2.5 费用系统

#### 稳定币计价费用（无原生 token）

Tempo 消除了对原生 gas token 的需求。用户直接使用任何受支持的 USD 稳定币支付费用。内部费用单位为 **attodollars**（10^-18 USD 精度）。

**固定基础费率**: 非 EIP-1559 可变费率。校准为 *"TIP-20 转账成本低于 $0.001。"*

**费用分配**: 所有费用归属出块提议者（validator）。

#### Fee AMM（自动做市商）

协议级专用 AMM 支持跨稳定币费用支付：

| 交换类型 | 汇率 | 方向 | 访问权限 |
|----------|------|------|----------|
| **Fee Swap** | 0.9970（0.30% 价差） | 用户 token → validator token | 仅协议自动调用 |
| **Rebalancing Swap** | 0.9985（0.15% 价差） | validator token → 用户 token | 无许可 |

**公式**:
```
Fee Swap:      amountOut = (amountIn × 9970) / 10000
Rebalance:     amountIn = (amountOut × 9985) / 10000 + 1
```

**MEV 防护**:
- 固定汇率 → 无法从 fee swap 中获利 backrunning
- 固定汇率 → 无三明治攻击漏洞
- Rebalancing MEV 集中在 top-of-block 拍卖（单次竞争，非概率性垃圾交易）

#### StablecoinDEX

协议内置的**嵌入式交易所**，功能包括：
- 价格-时间优先级订单簿
- Flip order（流动性提供机制）
- 多跳路由的稳定币交易
- DEX Balance（在 DEX 内直接持有 token 以节省交易 gas）
- pathUSD 作为中性报价 token 选项

### 2.6 Machine Payments Protocol（MPP）

与 Stripe 合作制定的**机器对机器支付开放标准**，支持支付网关化的 HTTP 端点：

**流程**: Client 请求 → `402 Payment Required` + `WWW-Authenticate: Payment` → Client 签名交易 → 重试携带 `Authorization: Payment` → `200` + `Payment-Receipt`

**Payment Intent 类型**:
- **Charge**: 按请求一次性支付（~500ms 延迟）
- **Session**: 持续按用量付费（通过链下 voucher 实现近零延迟）

**规范站点**: mpp.dev（含 IETF 规范）

---

## 3. Zones L2 隐私架构

### 3.1 Zone 定义

Tempo Zone 是一条 **Tempo 原生 validium 链**——锚定在 Tempo 主网的专用区块链，由单一 sequencer 控制出块和可见性。

**官方定义**: *"Tempo-native validium chains with multi-asset bridging, validity proofs, and privacy."*

**关键属性**: *"No zone data is published on Tempo Mainnet. Instead, the sequencer publishes commitments to the current zone state along with proofs of correct execution."*

### 3.2 架构概览

| 组件 | 描述 |
|------|------|
| **执行框架** | Reth SDK（与 Tempo L1 相同），复用 Tempo EVM 配置 |
| **共识** | NoopConsensus（中心化 Sequencer） |
| **网络** | 无 P2P（NoopNetworkBuilder）——sequencer 是唯一出块者 |
| **状态存储** | 每个 Zone 独立状态 |
| **L1 锚定** | 通过 Tempo 主网上的 ZonePortal 合约 |

#### Zone Predeploy 合约

| 合约 | 地址 | 用途 |
|------|------|------|
| **TempoState** | `0x1c00...0000` | Zone 对 Tempo 主网状态的视图 |
| **ZoneInbox** | — | 处理存款，在 Zone 侧 mint token |
| **ZoneOutbox** | — | 处理提款请求，通过 burn token |
| **ZoneConfig** | — | 从 L1 读取 sequencer 和 token 注册信息 |

#### Sequencer 角色

Sequencer 管理：
- 区块排序和交易包含
- 隐私（控制谁能看到什么）
- 活性（唯一出块者）

**关键安全属性**: *"The sequencer cannot steal funds or forge state transitions. Validity proofs prevent this."*（注意：validity proof 尚未上线，见第 3.7 节成熟度说明）

**已知 sequencer 风险**: 可以停止运营、审查用户或重排交易以提取 MEV。

### 3.3 出块模型

- Zone 每个 L1 区块产生**恰好一个 L2 区块**
- **即时终局性**: head = safe = finalized
- Sequencer 在 Tempo 主网区块最终确认时同步 Zone 视图
- 出块流程（目标设计）：L1 最终确认 → 执行 Zone 交易 → 生成批次 → 提交 validity proof（当前测试实现的 prover 尚未上线，见第 3.7 节）

### 3.4 ZonePortal 桥接

#### 存款（Tempo → Zone）

1. 用户在 Tempo 主网调用 `ZonePortal.deposit(token, to, amount, memo)`
2. Portal 验证 token 状态，扣除存款费用，锁定资金，排队存款
3. Sequencer 监听 `DepositMade` 事件
4. Sequencer 通过 `ZoneInbox.advanceTempo()` 处理存款，在 Zone 侧 mint token
5. 目标设计中由批次证明验证 Zone 侧存款处理；当前 prover 尚未上线，测试实现依赖 sequencer 诚实处理

**存款费用**: `FIXED_DEPOSIT_GAS (100,000) × zoneGasRate`

#### 加密存款（隐私保护入金）

用户可使用 sequencer 公钥加密敏感字段：

| 字段 | 可见性 | L1 上的公开性 | Sequencer 可见 | Zone 接收方可见 | 外部观察者可见 |
|------|--------|-------------|---------------|---------------|---------------|
| `token` | **公开** | 是 | 是 | 是 | 是 |
| `sender` | **公开** | 是 | 是 | 是 | 是 |
| `amount` | **公开** | 是 | 是 | 是 | 是 |
| `to`（接收方） | **加密** | 否 | 是（解密后） | 是（自身地址） | 否 |
| `memo` | **加密** | 否 | 是（解密后） | 是 | 否 |

> **隐私边界说明**: 加密存款仅隐藏 `to`（接收方地址）和 `memo`（支付上下文）。`token`（币种）、`sender`（发送方）和 `amount`（金额）在 L1 上保持公开——这是链上记账的必要条件。Zone sequencer 始终在隐私信任边界内——它解密并看到所有字段。

**ECIES 实现（secp256k1）**:
1. Sequencer 通过 `setSequencerEncryptionKey()` 发布加密公钥并提供持有证明
2. 用户生成临时密钥对，通过 ECDH 派生共享密钥
3. 用户使用 **AES-256-GCM** 加密 `(to || memo)`
4. 用户调用 `depositEncrypted(token, amount, keyIndex, encryptedPayload)`

**失败处理**: 解密失败时，token 被 mint 到发送方的 Zone 地址；Tempo 资金仍锁定在 Portal 中。

#### 提款（Zone → Tempo）

两阶段流程：
1. **批次最终确认**: Sequencer 调用 `finalizeWithdrawalBatch()`，构建提款哈希链，记录 `withdrawalQueueHash` 和 `withdrawalBatchIndex`
2. **处理**: Sequencer 在 Tempo 上调用 `processWithdrawal()`，从最旧的 slot 出队

**提款时间**: *"As soon as a validity proof is posted (targeting under 10 seconds)."*（当前 prover 尚未上线，实际提款时间取决于 prover 部署进度）

**提款费用**: `gasLimit × tempoGasRate`

#### 可组合提款回调

`ZoneMessenger` 支持原子操作：
- 通过 `transferFrom` 将 token 从 Zone Portal 转给目标
- 使用 callback data 调用目标合约
- 失败时回滚两个操作

```solidity
interface IWithdrawalReceiver {
    function onWithdrawalReceived(
        bytes32 senderTag,
        address token,
        uint128 amount,
        bytes calldata callbackData
    ) external returns (bytes4);
}
```

#### 可验证提款（发送方隐私保护）

发送方身份保护使用承诺验证：
```
senderTag = keccak256(abi.encodePacked(sender, txHash))
```

可选的 `revealTo` 公钥允许 sequencer 通过 ECDH 加密 `(sender, txHash)`，用于选择性跨 Zone 归因。

### 3.5 隐私模型

#### 执行层隐私

| 函数 | 访问控制 |
|------|----------|
| `balanceOf(account)` | 仅 `msg.sender == account` 或 sequencer 可调用 |
| `allowance(owner, spender)` | 仅 owner、spender 或 sequencer |
| `totalSupply()` | 公开（无限制） |
| `name()`, `symbol()`, `decimals()` | 公开（无限制） |

**Allowance 私密化理由**: *"A non-zero allowance reveals that owner has interacted with spender"*——关系隐私同样重要。

**附加保护**:
- **固定 gas 成本**（每个用户级 TIP-20 操作 100,000 gas）防止基于 gas 的侧信道攻击
- **合约创建禁用**（`CREATE` 和 `CREATE2` 被阻止）——Zone 仅运行预定的系统合约和 predeploy

#### ECIES 字段可见性总表

| 数据字段 | L1 公开交易 | L1 加密存款 | Sequencer 视角 | Zone 账户持有者视角 | 外部观察者/区块浏览器 |
|----------|-----------|-----------|---------------|-------------------|---------------------|
| Token（币种） | 公开 | 公开 | 可见 | 可见 | **L1 可见，Zone 内不可见** |
| Sender（发送方） | 公开 | 公开 | 可见 | 可见 | **L1 可见，Zone 内不可见** |
| Amount（金额） | 公开 | 公开 | 可见 | 可见（仅自身） | **L1 可见，Zone 内不可见** |
| To（接收方） | 公开 | **加密** | 可见（解密） | 可见（自身） | 不可见 |
| Memo（备注） | 公开 | **加密** | 可见（解密） | 可见 | 不可见 |
| Zone 内余额 | — | — | 可见 | 仅自身 | 不可见 |
| Zone 内转账历史 | — | — | 可见 | 仅涉及自身的 | 不可见 |
| Zone 区块交易列表 | — | — | 可见 | 不可见（sanitized） | 不可见（sanitized） |

#### RPC 层隐私

Zone RPC 要求通过 `X-Authorization-Token` HTTP 头提供**授权令牌**：
- 短期有效（最长 1 个月）
- 由调用方的 Tempo 账户密钥签名
- 包含 `"TempoZoneRPC"` domain separation、规范版本、Zone ID、Chain ID

**Per-Account Scoping（每账户范围限制）**:

| 方法类别 | 行为 |
|----------|------|
| **无限制** | 链元数据（chainId, blockNumber, gas prices） |
| **受限范围** | 仅返回认证账户的数据；其他账户返回虚拟值 |
| **仅 Sequencer** | 原始 storage 读取、代码检查、交易计数 |
| **已禁用** | Merkle 证明、mempool 观察 |

**计时侧信道缓解**: 受限范围方法有强制 **100ms 最小响应时间**，确保不存在的交易哈希和其他用户的交易查询无法区分。

**事件过滤（TIP-20）**:

| 事件 | 可见对象 |
|------|----------|
| Transfer / TransferWithMemo | 发送方或接收方 |
| Approval | Owner 或 Spender |
| Mint | 接收方 |
| Burn | 发送方 |

**Sanitized 区块**: `transactions` 数组被清空，`logsBloom` 置零以防止活动探测。

### 3.6 TIP-403 合规镜像

Zone **自动从 Tempo L1 同步 TIP-403 策略注册表**：

- *"Compliance policies travel with tokens. When deposited, the policy is provably mirrored into the zone."*
- Validity proof 保证 *"every transaction in the batch followed the issuer's rules"*（注意：当 prover 上线后才可实现）
- Zone 拥有 *"direct, synchronous access to Tempo Mainnet state... such as deposit queues and TIP-403 policy information"*
- 通过 `SharedPolicyCache` 实现，读取 `TempoState` predeploy 中的 Tempo 状态

**企业级意义**: Token 发行方即使在隐私 Zone 内也能保持合规控制。稳定币发行方的 whitelist/blacklist 通过 validity proof **可证明地执行**于每笔 Zone 交易中（待 prover 上线后生效；当前测试阶段依赖 sequencer 诚实执行）。

### 3.7 Validity Proofs（ZK + TEE）——成熟度分层说明

> **⚠️ 重要澄清：Zone prover 尚未上线。** 官方文档（`proving.mdx`）明确标注：
> *"The zone prover is not yet live. This page describes the planned design. The prover will be added in a future release."*
>
> 以下内容区分"已确认的架构设计"和"当前运行状态"。

#### 成熟度分层

| 层面 | 状态 | 依据 |
|------|------|------|
| **架构设计** | 已确认 | 官方文档详细描述了 state transition function、verifier interface、batch submission 结构、ancestry proof 等完整设计 |
| **代码实现** | 已部分实现 | Zone 预编译和 primitives 标记为 `no_std` / SP1 RISC-V 兼容，Portal ABI 已预留 proof 字段（WHI-340 代码分析确认）；SP1/TEE proof generation 与 L1 verifier 尚未实现 |
| **Prover 运行** | **尚未上线** | 官方文档明确声明 prover 将在未来版本中添加 |
| **测试网验证** | 测试阶段 | Zones 整体处于 v0.1.0 早期开发阶段 |

#### 企业风险评估影响

这一区分对企业风险评估至关重要：

- **"具有运行中 validity proof 的 validium"** = 安全模型已完整，sequencer 无法伪造状态转换
- **"具有计划中 prover 的 validium 架构"**（当前状态）= 安全性暂时依赖对 sequencer 的信任；与计划的最终安全模型存在差距

当前阶段，Zone 的执行正确性实际上依赖于 sequencer 诚实运行——validity proof 提供的"sequencer 无法窃取资金"保证尚未在生产中激活。

#### 架构设计细节（已确认但尚未上线的设计）

**State Transition Function**: 官方规划中的核心函数 `prove_zone_batch(witness: BatchWitness)`——设计为 Rust / `no_std` 兼容实现：

1. **Tempo 状态验证**: MPT proof 验证所有 Tempo storage 读取对照 state root
2. **Zone 状态初始化**: 加载 Zone 状态，将初始根绑定到前一个区块哈希
3. **区块执行**: 对每个区块：
   - 验证 parent hash 连续性和区块号递增
   - 验证 beneficiary 匹配注册的 sequencer
   - 执行 `advanceTempo()` 系统交易（如有）以处理存款
   - 通过 revm 运行用户交易
   - 在最终区块执行 `finalizeWithdrawalBatch()`
4. **提取输出承诺**: 区块哈希转换、存款队列转换、提款队列哈希

#### 部署模式（计划中）

| 模式 | 环境 | 证明机制 |
|------|------|----------|
| **ZKVM (SP1)** | Succinct SP1 RISC-V prover | ZK proof 提交到输出 |
| **TEE (SGX/TDX)** | Intel SGX 或 TDX enclave | 硬件签名证明 |

两种模式在 Tempo 主网上实现**相同的 verifier 合约接口**。

#### 批次提交结构

Sequencer 向 Tempo 主网提交：

| 字段 | 用途 |
|------|------|
| `tempoBlockNumber` | Zone 提交到的 Tempo 区块 |
| `blockTransition` | Zone 区块哈希进展（prevBlockHash → nextBlockHash） |
| `depositQueueTransition` | 存款队列处理状态 |
| `withdrawalQueueHash` | 提款哈希链 |
| `verifierConfig` | Domain separation / attestation 数据 |
| `proof` | Validity proof 或 TEE attestation |

#### 证明验证（6 项检查）

1. `prevBlockHash` 到 `nextBlockHash` 之间的有效状态转换
2. Zone 通过 TempoState 对指定 `tempoBlockNumber` 的承诺
3. Anchor 区块哈希的正确性（直接或 ancestry 模式）
4. ZoneOutbox 中正确的 `withdrawalBatchIndex` 和 `withdrawalQueueHash`
5. 通过 Tempo 状态读取验证存款处理的正确性
6. Zone 区块 `beneficiary` 匹配注册的 sequencer

#### Ancestry Proofs

对于非活跃时间超过 EIP-2935 ~8,192 区块哈希窗口的 Zone：
- Portal 读取 `recentTempoBlockNumber` 哈希（必须是近期的）
- Prover 包含从 `tempoBlockNumber + 1` 到 `recentTempoBlockNumber` 的 Tempo header 作为 witness 数据
- Proof 验证 parent hash 链连续性
- 证明时间随区块间隔线性增长；链上验证成本保持恒定

### 3.8 Zone 执行与 Gas 模型

| 方面 | 详情 |
|------|------|
| **Fee Token** | 任何已启用的 TIP-20（USD 计价） |
| **Gas 模型** | 每个用户级操作固定 100,000 gas（防止 gas 侧信道） |
| **合约创建** | 禁用（CREATE/CREATE2 被阻止） |
| **EVM 兼容性** | 刻意缩减——可预测性和隐私优先于完整等价性 |
| **费用收取** | Sequencer 直接处理已启用的 token（无中间市场） |

---

## 4. Commonware Simplex BFT 共识

### 4.1 Commonware 项目概述

Commonware 是一个**区块链和去中心化应用的模块化密码学和分布式系统原语库**。提供 15+ 原语，涵盖：

| 类别 | 原语 |
|------|------|
| **核心基础设施** | broadcast, p2p, runtime, storage, stream |
| **共识与排序** | consensus, collector |
| **密码学** | cryptography, coding |
| **数据管理** | codec, resolver, math |
| **开发工具** | deployer, invariants, parallel, conformance |

**核心贡献者**: Patrick O'Grady, Roberto Bayardo, Ben Clabby, Guru Vamsi Policharla, Andrew Lewis-Pye, Brendan Chou, Lucas Meier

**与 Tempo 的关系**: Tempo 是 Commonware 的 **strategic investor**（2025 年 11 月公布）。

### 4.2 Simplex BFT 算法

**官方描述**: *"A Byzantine Fault Tolerant consensus protocol optimized for fast finality with graceful degradation under adverse network conditions."*

#### 出块参数

| 参数 | 值 |
|------|-----|
| **目标出块时间** | 正常条件下 ~600ms |
| **时间分解** | 500ms builder 循环 + 网络延迟 + 验证时间 |
| **领导者选举** | 可验证随机函数（VRF）进行随机提议者选举 |
| **VRF 优势** | DoS 防护 + MEV 抵抗 |

#### 终局性模型

- **确定性终局**（非概率性）
- 一旦最终确认，区块**不可回滚**——零重组风险
- 等效于 PoS 以太坊的终局性但在亚秒级速度下实现

#### 拜占庭容错

| 验证者数量 | 最大拜占庭容错 |
|-----------|---------------|
| 4 个验证者 | 容忍 1 个拜占庭 |
| 10 个验证者 | 容忍 3 个拜占庭 |
| 一般情况 | 安全性: < 1/3 拜占庭；活性: ≥ 2/3 诚实且在线 |

**当前测试网**: 4 个许可制验证者
**主网计划**: 以机构验证者启动，最终实现无许可

#### 安全优先设计

协议**优先保证安全性而非活性**：在恶劣条件下选择停机而非产出冲突区块。

### 4.3 密码学基础

| 原语 | 用途 |
|------|------|
| **BLS12-381** | 共识门限签名（代码库确认） |
| **ed25519** | Commonware P2P 网络认证 |
| **secp256k1** | 执行层（以太坊兼容性） |
| **P256** | WebAuthn/Passkey 支持 |

### 4.4 双 Runtime 架构

Tempo 运行两个独立的 Tokio runtime：

| Runtime | 用途 | 网络 |
|---------|------|------|
| **执行 Runtime** | Reth SDK（EVM、存储、RPC） | devp2p |
| **共识 Runtime** | Commonware Simplex BFT | Commonware P2P（ed25519 认证，加密） |

这种分离确保共识性能不受执行层负载影响。

### 4.5 DKG（分布式密钥生成）

代码库分析确认：
- BLS12-381 门限签名需要 DKG 仪式
- Commonware 提供 `reshare` 示例，暗示密钥重分享能力
- 具体 DKG 协议细节未在公开文档中记录

---

## 5. 企业级特性评估

### 5.1 特性矩阵

| 特性 | 实现方式 | 成熟度 | 企业关联性 |
|------|---------|--------|-----------|
| **合规框架（TIP-403）** | 协议级预编译 `0x403c...`，whitelist/blacklist 策略；Zone 侧目标状态为通过 proof 可证明镜像 | L1 生产就绪；Zone prover 尚未上线 | **高** — 发行方跨层保持合规控制 |
| **支付优化** | 固定基础费 < $0.001/转账，attodollar 精度，专属 Payment Lane | 生产就绪 | **高** — 可预测成本，无原生 token 波动 |
| **隐私分层** | Tempo L1（公开）+ Zone L2（隐私 validium） | Zone: 仅测试网；Prover: 尚未上线 | **高** — 双层满足监管+隐私需求（待 prover 上线完善） |
| **身份管理** | AccountKeychain 预编译，WebAuthn/P256，带支出限额和调用范围的 access key | 生产就绪（T3 增强） | **高** — 内置企业密钥管理 |
| **稳定币基础设施** | TIP-20 原生标准，Fee AMM，StablecoinDEX | 生产就绪 | **高** — 无需依赖第三方 token 合约 |
| **机器支付（MPP）** | HTTP 原生支付协议，与 Stripe 共同编写 | 规范阶段 | **中** — 创新但早期 |
| **亚秒级终局性** | Simplex BFT ~600ms 出块，确定性终局 | 测试网（4 验证者） | **高** — 近实时结算 |
| **确定性吞吐量** | Payment Lane 防 noisy-neighbor 保证 | 生产就绪 | **高** — 兼容 SLA 的支付保障 |
| **费用赞助** | 原生双签名机制（无 paymaster 合约） | 生产就绪 | **高** — 企业可为终端用户抽象费用 |
| **批量交易** | 单交易原子多调用 | 生产就绪 | **高** — 降低批量操作复杂性 |
| **定时交易** | validAfter/validBefore 时间戳 | 生产就绪 | **中** — 归属解锁、限时优惠、延迟执行 |
| **虚拟地址（TIP-1022）** | TIP-20 存款自动转发到主钱包 | 生产就绪（T3） | **中** — 消除 sweep 交易 |
| **链上外汇** | StablecoinDEX 多跳路由 | 生产就绪 | **中** — 跨币种稳定币转换 |

### 5.2 TIP-403 深入分析（合规框架）

**预编译地址**: `0x403c000000000000000000000000000000000000`

| 策略类型 | 行为 |
|----------|------|
| **policyId = 0** | `always-reject` — 拒绝所有转账 |
| **policyId = 1** | `always-allow` — 允许所有转账（新 token 默认） |
| **Whitelist** | 仅白名单中的地址可转账；其他全部阻止 |
| **Blacklist** | 黑名单中的地址被阻止；其他全部允许 |

**关键操作**:
- `createPolicy(admin, policyType)` — 创建新策略
- `modifyPolicyWhitelist(policyId, account, allowed)` — 更新白名单
- `modifyPolicyBlacklist(policyId, account, restricted)` — 更新黑名单
- `isAuthorized(policyId, user)` — 查询授权状态

**复合转账策略（TIP-1015，T2 硬分叉）**: 对 sender 和 recipient 设置不同的授权规则。

**Zone 镜像**: 策略通过 validity proof *"provably mirrored"* 到 Zone。`SharedPolicyCache` 通过 `TempoState` predeploy 读取 Tempo L1 状态。（注：prover 上线前，镜像依赖 sequencer 诚实执行。）

### 5.3 企业采纳优势

1. **无需原生 token**: Gas 以 USD 稳定币支付，消除企业面临的 token 价格波动风险
2. **内置合规**: TIP-403 提供监管就绪的访问控制，无需自定义智能合约
3. **隐私+合规共存**: Zone 提供交易隐私的同时可证明地执行发行方合规规则（待 prover 上线后完整实现）
4. **确定性成本**: 固定基础费率模型支持可预测的运营成本
5. **现代认证**: WebAuthn/P256 支持无密码的企业用户接入
6. **Paradigm/Stripe 背书**: 机构信誉和支付行业专业知识

### 5.4 企业采纳风险与限制

1. **主网未上线**: 截至 2026 年 5 月尚无生产部署（仅测试网）
2. **Zone 不成熟**: v0.1.0，仅测试网，预期有 breaking changes
3. **Zone validity proof 尚未上线**: Prover 为计划中的设计而非已运行组件——当前安全模型依赖 sequencer 信任
4. **Zone sequencer 中心化**: 单点故障/审查风险（待 validity proof 上线后可证明不能窃取资金）
5. **有限的验证者集**: 当前仅 4 个许可制验证者
6. **Zone 内禁止创建合约**: 不支持自定义智能合约——仅 predeploy
7. **Sequencer 信任模型**: Zone 隐私 *"depends on the integrity of whoever is running the sequencer"*
8. **无跨 Zone 可组合性**: Zone 间转账需通过主网中转

---

## 6. 与 Canton、Prividium 定位对比

| 维度 | Tempo/Zones | Canton | Prividium |
|------|-------------|--------|-----------|
| **架构** | L1 + 隐私 Validium L2 | Participant-Domain DLT | Validium（zkSync 上的 L2） |
| **执行层** | Reth SDK（EVM，Osaka 硬分叉） | Daml VM | zkEVM |
| **共识** | Commonware Simplex BFT（亚秒级，确定性） | 2PC via Sequencer+Mediator | 中心化 Sequencer |
| **隐私模型** | Zone 隔离 + ECIES 加密存款 + 执行层访问控制 | Sub-transaction 隐私（Need-to-know） | ZK proof（Prove-not-reveal） |
| **隐私粒度** | Per-Zone（整条链是隐私的） | Per-sub-transaction（选择性披露） | Per-transaction（ZK proof） |
| **合规** | TIP-403 策略注册表（L1 已实现；Zone 可证明镜像依赖尚未上线的 prover） | Daml 授权模型（内嵌语言） | SSO + RBAC + KYC |
| **核心优化方向** | 稳定币支付 | 多方工作流 | 机构合规链 |
| **稳定币支持** | 原生 TIP-20 标准（协议级） | 无内置 token 标准 | ERC-20 兼容 |
| **费用模型** | USD 稳定币费用（无原生 token） | 应用相关 | ETH 基础 gas |
| **智能合约** | EVM（Solidity）+ 自定义预编译 | Daml（函数式，非图灵完备） | Solidity（zkEVM） |
| **成熟度** | 测试网（2025 年 12 月），v1.6.0 | 生产级（Digital Asset 收购，2017+） | 生产级（主网） |
| **Sequencer 信任** | Zone: 当前受信于隐私和执行正确性；prover 上线后仍受信于隐私，但可降低执行正确性信任 | Mediator 受信于隐私+排序 | 中心化 sequencer 受信 |
| **证明系统** | SP1 ZKVM + TEE（SGX/TDX）——**计划中，尚未上线** | 无（密码学承诺） | ZK rollup proof |
| **机器支付** | MPP 协议（与 Stripe 共同编写） | 非原生 | 非原生 |
| **核心背书方** | Paradigm + Stripe | Digital Asset（Blythe Masters 创立） | Matter Labs（zkSync） |

### 关键差异化分析

**Tempo/Zones 独特优势**:
- 为支付场景专门优化的协议级设计（Payment Lane、TIP-20、Fee AMM）
- 无需原生 token（USD 稳定币 gas）
- WebAuthn/Passkey 原生支持
- Stripe 共同开发的机器支付协议
- 与 Reth/Foundry 共享核心团队（深厚以太坊基础设施专业知识）

**Tempo/Zones 对比 Canton 的差距**:
- 无 sub-transaction 隐私（整个 Zone 是隐私的，非交易内选择性披露）
- 无多方工作流原语（Canton 的 Daml 专为此设计）
- 成熟度较低（测试网 vs 生产级）

**Tempo/Zones 对比 Prividium 的差距**:
- Zone 隐私依赖 sequencer 诚信（Prividium 使用 ZK proof 实现隐私）
- Zone 内不支持自定义智能合约（Prividium 支持完整 zkEVM）
- 生产级记录较少
- Validity proof 尚未上线（Prividium 的 ZK proof 已在生产运行）

---

## 7. Mantle 适配性分析

> 本节分析 Tempo 的技术选择与 Mantle（OP Stack L2）架构之间的映射关系，为 M2/M3 的 Mantle 企业化设计提供参考。

### 7.1 执行层对比：Reth SDK vs op-geth

| 维度 | Tempo（Reth SDK） | Mantle（OP Stack） | 适配含义 |
|------|-------------------|-------------------|----------|
| **执行客户端** | Reth（Rust，模块化） | op-geth（Go，fork of go-ethereum） | 语言和架构差异大；Tempo 的预编译模式在 op-geth 中需用 Solidity 合约或 Go 预编译实现 |
| **节点构建模式** | `reth-node-builder`（组件可插拔） | Monolithic fork + config | Reth 的模块化设计不能直接迁移到 OP Stack；需逐功能移植 |
| **EVM 版本** | revm v38（Osaka 硬分叉目标） | 追随 go-ethereum upstream | Tempo 的自定义 EVM 扩展（固定 gas、CREATE 禁用）需在 op-geth 层面修改 |
| **预编译** | 大量协议级预编译（TIP-20, TIP-403, AccountKeychain, Nonce, Fee AMM） | 标准以太坊预编译 + Mantle 自定义 | Tempo 的预编译密集设计是核心差异；在 Mantle 上需选择：预编译移植 vs 智能合约实现 |

### 7.2 交易与区块头模型

| 维度 | Tempo | Mantle/OP Stack | 移植难度 |
|------|-------|-----------------|----------|
| **交易类型** | `0x76` TempoTxEnvelope（P256、批量调用、定时、费用赞助） | 标准以太坊类型 + OP Stack deposit tx | **高** — 需要在 op-geth 中添加新交易类型或用 ERC-4337 替代部分功能 |
| **区块头** | TempoHeader（`timestamp_millis_part`, `shared_gas_limit`, `general_gas_limit`, consensus context） | OP Stack 标准区块头 | **高** — Payment Lane 需要区块头级修改，影响所有下游工具 |
| **签名方案** | secp256k1 + P256 + WebAuthn + Keychain | 仅 secp256k1 | **中** — P256/WebAuthn 可通过预编译或 ERC-4337 account abstraction 引入 |

### 7.3 共识与终局性

| 维度 | Tempo | Mantle | 适配分析 |
|------|-------|--------|----------|
| **共识** | Simplex BFT（多验证者，确定性终局） | 单一 Sequencer + L1 DA | 完全不同的模型；BFT 验证者终局性 vs L1 锚定终局性 |
| **终局延迟** | ~600ms（L1 BFT 终局） | ~数分钟（L1 确认）到约 7 天（争议窗口） | Tempo 的亚秒终局性源于其 L1 BFT 设计，在 L2 架构中不可直接复制 |
| **Sequencer 模型** | L1 多验证者；Zone L2 单 sequencer | 单一 Sequencer | Zone 的 sequencer 模型与 Mantle 更相似 |

### 7.4 Payment Lane 可移植性

Payment Lane 是 Tempo 最核心的差异化特征之一。将其移植到 Mantle/OP Stack 需要考虑：

| 移植路径 | 可行性 | 所需改动 |
|----------|--------|----------|
| **OP Stack 原生扩展** | **中等** | 修改 op-geth 区块构建逻辑，添加 `general_gas_limit`/`shared_gas_limit` 区块头字段，修改交易排序算法 |
| **Sequencer 级实现** | **较高** | 在 sequencer 的区块构建策略中实现优先级排序，不修改共识规则；但无法提供协议级保证 |
| **智能合约实现** | **不可行** | Payment Lane 是区块空间级保证，无法在合约层面实现 |

**结论**: Payment Lane 如果要在 OP Stack 上提供与 Tempo 同等的协议级保证，需要对 op-geth 的区块构建和验证逻辑进行较深层修改，或者需要基于 Reth 重建执行客户端（类似 OP Stack 的 op-reth 路径）。

### 7.5 Zone 隐私架构移植性

| Tempo Zone 特性 | Mantle 适配路径 | 复杂度 |
|----------------|----------------|--------|
| **Zone 隔离（独立 L2 链）** | 类似 OP Stack L3 或独立 rollup 实例 | 中等（OP Stack 已支持 L3 概念） |
| **ECIES 加密存款** | 可作为桥接合约功能实现 | 低（纯智能合约逻辑） |
| **执行层隐私（`balanceOf` 限制等）** | 需要修改 EVM 或使用隐私 EVM | **高**（需要执行层改造） |
| **RPC 隐私（per-account scoping）** | 可在 RPC 代理层实现 | 中等（不需修改链本身） |
| **TIP-403 合规镜像** | 需要跨链策略同步机制 | 中等（合约+桥接设计） |
| **Validity proof** | 可复用 Mantle 的 fraud proof 框架或引入 ZK proof | **高**（需要证明系统适配） |

### 7.6 总体评估

**可直接借鉴的设计理念**:
- 支付交易的确定性吞吐量保障思路
- 稳定币计价 gas 的设计模式
- 合规策略注册表（TIP-403）的协议级合规模式
- 隐私 L2 与合规 L1 的分层架构理念
- 加密存款的隐私入金模式

**需要深度改造的能力**:
- Payment Lane（需区块头级和区块构建级修改）
- TIP-20 原生预编译（需评估预编译 vs 合约的 trade-off）
- TempoTxEnvelope 的丰富交易功能（需评估 ERC-4337 替代方案 vs 原生集成）
- Simplex BFT 亚秒终局性（L2 架构下不可直接复制，需寻找替代方案如 fast finality gadget）

**Reth vs op-geth 的根本抉择**: Tempo 的许多创新（模块化组件、预编译密集设计、双 runtime）都深度依赖 Reth SDK 的架构。如果 Mantle 企业化路径选择 Reth 作为执行客户端（类似 op-reth），则 Tempo 的技术方案可移植性显著提升；若保持 op-geth，则需要在 Go 生态中重新实现大部分功能。

---

## 8. 参考链接

### 8.1 官方文档

| 资源 | URL |
|------|-----|
| 文档站首页 | https://docs.tempo.xyz/ |
| AI 全量文档（llms-full.txt） | https://docs.tempo.xyz/llms-full.txt |
| AI 文档索引（llms.txt） | https://docs.tempo.xyz/llms.txt |
| 协议概述 | https://docs.tempo.xyz/protocol/ |
| Zones 架构 | https://docs.tempo.xyz/protocol/zones/ |
| Zone 桥接 | https://docs.tempo.xyz/protocol/zones/bridging |
| Zone Proving | https://docs.tempo.xyz/protocol/zones/proving |
| Zone RPC | https://docs.tempo.xyz/protocol/zones/rpc |
| Zone 账户 | https://docs.tempo.xyz/protocol/zones/accounts |
| Zone 执行 | https://docs.tempo.xyz/protocol/zones/execution |
| 区块空间概述 | https://docs.tempo.xyz/protocol/blockspace/overview |
| Payment Lane 规范 | https://docs.tempo.xyz/protocol/blockspace/payment-lane-specification |
| 共识与终局性 | https://docs.tempo.xyz/protocol/blockspace/consensus |
| Tempo Transactions 规范 | https://docs.tempo.xyz/protocol/transactions/spec-tempo-transaction |
| AccountKeychain | https://docs.tempo.xyz/protocol/transactions/AccountKeychain |
| TIP-20 规范 | https://docs.tempo.xyz/protocol/tip20/spec |
| TIP-20 概述 | https://docs.tempo.xyz/protocol/tip20/overview |
| TIP-20 奖励 | https://docs.tempo.xyz/protocol/tip20-rewards/overview |
| TIP-403 概述 | https://docs.tempo.xyz/protocol/tip403/overview |
| TIP-403 规范 | https://docs.tempo.xyz/protocol/tip403/spec |
| 费用系统 | https://docs.tempo.xyz/protocol/fees/ |
| Fee AMM 规范 | https://docs.tempo.xyz/protocol/fees/spec-fee-amm |
| 费用规范 | https://docs.tempo.xyz/protocol/fees/spec-fee |
| Stablecoin DEX | https://docs.tempo.xyz/protocol/exchange/ |
| TIPs 索引 | https://docs.tempo.xyz/protocol/tips/ |
| 性能 | https://docs.tempo.xyz/learn/tempo/performance |
| 隐私概述 | https://docs.tempo.xyz/learn/tempo/privacy |
| 机器支付 | https://docs.tempo.xyz/guide/machine-payments/ |
| EVM 差异 | https://docs.tempo.xyz/quickstart/evm-compatibility |

### 8.2 GitHub 仓库

| 仓库 | URL |
|------|-----|
| Tempo L1 源码 | https://github.com/tempoxyz/tempo |
| Zones L2 源码 | https://github.com/tempoxyz/zones |
| GitHub 组织 | https://github.com/tempoxyz |
| Reth SDK（Paradigm） | https://github.com/paradigmxyz/reth |
| Commonware Monorepo | https://github.com/commonwarexyz/monorepo |

### 8.3 外部资源

| 资源 | URL |
|------|-----|
| Tempo 官网 | https://tempo.xyz |
| Tempo 浏览器 | https://explore.tempo.xyz |
| Tempo 钱包 | https://wallet.tempo.xyz |
| TIPs 提案站点 | https://tips.sh/ |
| Commonware 官网 | https://commonware.xyz/ |
| Commonware 文档 | https://docs.rs/commonware-* |
| MPP 协议 | https://mpp.dev |

### 8.4 指南与集成

| 指南 | URL |
|------|-----|
| 快速开始 / 连接信息 | https://docs.tempo.xyz/quickstart/connection-details |
| 钱包集成 | https://docs.tempo.xyz/quickstart/wallet-developers |
| 集成 Tempo | https://docs.tempo.xyz/quickstart/integrate-tempo |
| 隐私 Zone 指南 | https://docs.tempo.xyz/guide/private-zones/ |
| 节点运营 | https://docs.tempo.xyz/guide/node/ |
| 验证者接入 | https://docs.tempo.xyz/guide/node/validator-setup |
| 稳定币发行 | https://docs.tempo.xyz/guide/issuance/ |
| 支付指南 | https://docs.tempo.xyz/guide/payments/ |

---

## 附录 A: TIPs（Tempo Improvement Proposals）索引

| TIP | 标题 | 状态 |
|-----|------|------|
| TIP-0000 | TIP Process | 活跃 |
| TIP-1000 | State Creation Cost Increase | 已实施 |
| TIP-1001 | Place-only mode for next quote token | 已实施 |
| TIP-1002 | Prevent crossed orders, allow same-tick flip orders | 已实施 |
| TIP-1003 | Client order IDs | 已实施 |
| TIP-1004 | Permit for TIP-20 | 已实施（T2） |
| TIP-1005 | Fix ask swap rounding loss | 已实施 |
| TIP-1006 | Burn At for TIP-20 Tokens | 已实施 |
| TIP-1007 | Fee Token Introspection | 已实施 |
| TIP-1009 | Expiring Nonces | 已实施 |
| TIP-1010 | Mainnet Gas Parameters | 已实施 |
| TIP-1011 | Enhanced Access Key Permissions | 已实施（T3） |
| TIP-1015 | Compound Transfer Policies | 已实施（T2） |
| TIP-1016 | Exempt Storage Creation from Gas Limits | 已实施 |
| TIP-1017 | Validator Config V2 precompile | 已实施（T2） |
| TIP-1020 | Signature Verification Precompile | 已实施（T3） |
| TIP-1022 | Virtual Addresses for TIP-20 Deposit Forwarding | 已实施（T3） |
| TIP-1030 | Allow same-tick flip orders | 已实施 |
| TIP-1031 | Embed consensus context in block Header | 已实施（T4） |
| TIP-1035 | Implicit Approval List | 已实施 |
| TIP-1036 | T2 Hardfork Bug Fixes | 已实施（T2） |
| TIP-1038 | T3 Hardfork Meta TIP | 已实施（T3） |
| TIP-1046 | T4 Hardfork Meta TIP | 已实施（T4） |
| TIP-1047 | Revert code creation at TIP-20 prefix addresses | 已实施 |
| TIP-1056 | Keep same order ID when flip orders flip | 已实施 |

---

## 附录 B: 信息置信度评估

| 章节 | 主要来源 | 置信度 |
|------|---------|--------|
| 项目概述 | tempo.xyz, docs.tempo.xyz | **高** — 官方来源 |
| 团队/融资 | tempo.xyz（有限披露） | **中** — Paradigm/Stripe 孵化已确认；团队成员未公开 |
| Payment Lane | docs.tempo.xyz + 代码分析（WHI-340） | **高** — 官方规范+代码验证 |
| TIP-20 标准 | docs.tempo.xyz（规范页） | **高** — 完整规范可用 |
| TIP-403 合规 | docs.tempo.xyz（规范页） | **高** — 完整规范可用 |
| Zone 架构 | docs.tempo.xyz + 代码分析 | **高** — 详细官方文档 |
| Zone Validity Proof | docs.tempo.xyz（proving.mdx） + 代码分析 | **中** — 架构设计已确认，但 prover **尚未上线**（官方明确声明） |
| Commonware Simplex BFT | docs.tempo.xyz + commonware.xyz | **中** — 算法细节有限；出块时间和 BFT 阈值已确认 |
| DKG 仪式 | 仅代码分析 | **中** — 代码中确认，未公开文档化 |
| Reth SDK 集成 | docs.tempo.xyz + 代码分析 | **高** — 文档完善且代码验证 |
| MPP / Stripe 合作 | docs.tempo.xyz, tempo.xyz | **高** — 共同编写明确声明 |
| 企业评估 | 综合所有来源 | **中高** — 基于已确认特性的主观评估 |
| Mantle 适配性分析 | 综合 Tempo 文档 + OP Stack 架构知识 | **中高** — 基于架构对比的分析性评估 |
