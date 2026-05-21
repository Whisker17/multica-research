# WHI-358: L1 路径 — 执行层与共识终局性设计

> **Status**: In Review
> **Dependencies**: WHI-355 (Narrative Analysis), WHI-357 (Architecture Blueprint)
> **References**: WHI-340 (Tempo Code Analysis), WHI-335 (Canton Architecture), WHI-341 (Mantle Baseline), WHI-345 (Consensus/DA Comparison)
> **Output**: `m4-rebuild/execution-consensus/WHI-358-execution-consensus-design.md`

---

## Executive Summary

本文档是企业级 L1 区块链推倒重建方案的核心技术设计 — 执行层与共识终局性架构。这是整个系统的心脏，决定了链的性能上限、终局性模型、以及上层隐私/合规功能的可行性基础。

**核心设计决策**:
- **执行引擎**: Reth SDK (`reth-node-builder` + revm v38+) — 完全 EVM 等价，Rust 原生，模块化可插拔
- **共识协议**: Commonware Simplex BFT — 亚秒级确定性终局 (~600ms)，BLS12-381 门限签名
- **终局性模型**: 三层渐进式终局 — BFT 即时终局 (亚秒) → ZK 证明终局 (分钟级) → Ethereum L1 锚定 (12+ 分钟)
- **核心创新**: 双重终局性 + 叙事驱动的可配置终局性层级，满足 RWA (DVP 安全) / xstocks (T+0 公平) / Payment (超高吞吐) 三个截然不同的业务需求

**设计目标与性能指标**:

| 指标 | 目标值 | 参考基准 |
|------|--------|----------|
| 主链 TPS | 3,000–5,000 | Mantle: ~50–200, Tempo: 未公开基准 |
| Payment Zone TPS | >10,000 | Visa 日均 ~2K, 峰值 ~65K |
| xStocks Zone TPS | >5,000 (峰值) | HFT 场景需求 |
| BFT 终局延迟 | ~600ms | Tempo: ~600ms, CometBFT: ~6s |
| xStocks 交易延迟 | <100ms | HFT 低延迟需求 |
| 交易费用 (Payment) | <$0.001/tx | Tempo: ~$0.001, Prividium: <$0.0001 |
| L1 锚定延迟 | 分钟级 (可配置) | Mantle: 7 天 (挑战期) |

---

## 目录

1. [执行层架构设计](#1-执行层架构设计)
   - 1.1 [基础执行引擎: Reth SDK 定制化路径](#11-基础执行引擎-reth-sdk-定制化路径)
   - 1.2 [自定义预编译合约](#12-自定义预编译合约)
   - 1.3 [交易类型扩展](#13-交易类型扩展)
   - 1.4 [Gas 经济模型](#14-gas-经济模型)
2. [共识层架构设计](#2-共识层架构设计)
   - 2.1 [共识协议选型与定制](#21-共识协议选型与定制)
   - 2.2 [验证者集管理](#22-验证者集管理)
   - 2.3 [出块机制与 MEV 防护](#23-出块机制与-mev-防护)
3. [双重终局性模型详细设计](#3-双重终局性模型详细设计)
   - 3.1 [三层终局性架构](#31-三层终局性架构)
   - 3.2 [叙事驱动的可配置终局性](#32-叙事驱动的可配置终局性)
   - 3.3 [终局性状态机](#33-终局性状态机)
4. [ZK 证明系统设计](#4-zk-证明系统设计)
   - 4.1 [证明范围与架构](#41-证明范围与架构)
   - 4.2 [证明生成管线](#42-证明生成管线)
   - 4.3 [证明验证与 L1 锚定](#43-证明验证与-l1-锚定)
5. [Engine API 接口规范](#5-engine-api-接口规范)
   - 5.1 [执行-共识接口设计](#51-执行-共识接口设计)
   - 5.2 [区块生命周期](#52-区块生命周期)
   - 5.3 [状态管理接口](#53-状态管理接口)
6. [交易池分层设计](#6-交易池分层设计)
   - 6.1 [多层交易池架构](#61-多层交易池架构)
   - 6.2 [交易排序策略](#62-交易排序策略)
   - 6.3 [合规预检流程](#63-合规预检流程)
7. [性能分析与优化策略](#7-性能分析与优化策略)
   - 7.1 [理论性能上限分析](#71-理论性能上限分析)
   - 7.2 [并行执行策略](#72-并行执行策略)
   - 7.3 [瓶颈分析与优化路径](#73-瓶颈分析与优化路径)
8. [技术对比: Tempo / Canton / Prividium / Mantle](#8-技术对比)

---

## 1. 执行层架构设计

### 1.1 基础执行引擎: Reth SDK 定制化路径

#### 选型理由

基于 WHI-357 架构蓝图的决策，执行引擎选择 **Reth SDK** (`reth-node-builder` + revm v38+)。这一决策基于以下核心考量:

| 考量维度 | Reth SDK | op-geth (Mantle 现状) | 自研 EVM | 结论 |
|----------|---------|----------------------|----------|------|
| **语言** | Rust — 内存安全、零成本抽象、`no_std` 兼容 | Go — GC 暂停、不支持 `no_std` | 任意 | Rust 胜出 |
| **模块化** | NodeBuilder trait 组合模式 — 共识可热插拔 | 3 层 fork 链 (go-ethereum → op-geth → Mantle) | 完全自定义 | Reth SDK 胜出 |
| **EVM 兼容性** | revm v38+ 完整 Osaka 硬分叉支持 | 原生 go-ethereum EVM | 需自实现 | 两者均满足 |
| **ZK 就绪** | `no_std` 预编译可直接运行在 SP1/RISC-V prover guest | Go 无法编译为 RISC-V guest | 自定义 | Reth SDK 胜出 |
| **上游追踪** | 直接组合 Reth 版本更新 | 三层 fork 每次合并极其痛苦 | 无上游 | Reth SDK 胜出 |
| **生产验证** | Tempo 主网 (Chain ID 4217, 2026-03-31 上线) | Mantle 主网 (Chain ID 5000) | 无 | 均已验证 |
| **安全风险** | 低 — 复用成熟 EVM 实现 | 低 — 原生 geth | 高 — 无生产验证 | Reth/op-geth 均低风险 |

**核心结论**: Reth SDK 在模块化、Rust 生态、ZK 就绪性、上游维护成本四个维度全面领先 op-geth。Tempo 主网已证明 Reth SDK 的生产可行性。

#### Reth SDK 组合模式: Tempo 参考实现分析

Tempo 的 Reth SDK 使用方式 (WHI-340) 是我们设计的主要参考。其核心架构模式:

```rust
// Tempo 的节点类型组合 (来自 WHI-340 代码分析)
type TempoFullNodeTypes = RethFullAdapter<DatabaseEnv, TempoNode>;
type TempoNodeAdapter   = NodeAdapter<TempoFullNodeTypes>;
pub type TempoFullNode  = FullNode<TempoNodeAdapter, TempoAddOns<TempoFullNodeTypes>>;
```

**Tempo 复用的 Reth 模块:**
- `reth-node-builder` — `NodeBuilder`, `NodeTypes`, `FullNode`, `NodeAdapter`, `RethFullAdapter`
- `reth_consensus::HeaderValidator` + `FullConsensus` traits
- `DatabaseEnv` (MDBX) — 存储后端
- `revm` v38 — EVM 执行引擎 (通过 `TempoEvmConfig`)
- `alloy` 2.0.4 — 网络/Provider 扩展
- 标准以太坊交易类型 (`TxLegacy`, `TxEip2930`, `TxEip1559`, `TxEip7702`)

**Tempo 自研的模块 (我们必须类似自研):**

| 自研 Crate | 功能 | 复用/自研原因 |
|-----------|------|-------------|
| `commonware-node` | Simplex BFT 引擎桥接 + 双 Tokio 运行时 | Reth 默认无 BFT 共识 |
| `consensus` (`TempoConsensus`) | 自定义 `HeaderValidator`/`FullConsensus`: 验证 BFT 证书 | BFT 区块头验证逻辑不同 |
| `primitives` | 自定义 `TempoHeader`, `TempoTxEnvelope` (含 0x76 AA 交易) | 企业级交易类型扩展 |
| `chainspec` | 自定义链规范 + 10 个硬分叉定义 + gas 常量 (attodollar) | 自有 gas 经济模型 |
| `transaction-pool` | Payment Lane 交易池 (v1/v2 分类, 车道路由) | 三车道区块构建 |
| `payload/builder` | 三车道区块构建器 | Payment Lane 架构 |
| `precompiles` | 全部原生预编译 (12+ L1, 7+ Zone) | 企业级功能 |
| `contracts` | 预部署合约 ABI 绑定 | — |
| `dkg-onchain-artifacts` | BLS12-381 DKG 密钥仪式产物 | BFT 门限签名 |

**Reth 模块明确不复用:**
- EIP-4844 blob 交易 — `TempoTxEnvelope` 对 blob 类型返回 `UnsupportedTransactionType`
- Reth 默认共识引擎 — 完全替换为 `commonware-node` 双运行时 Simplex BFT
- Reth 默认交易池 — 替换为 Payment Lane 感知的自定义池

#### 我们的定制化路径

基于 Tempo 的参考和我们的三叙事需求，定义以下 Node 类型组合:

```rust
// 企业级 L1 节点类型定义
pub struct EnterpriseLNode;

impl NodeTypes for EnterpriseLNode {
    type Primitives   = EnterprisePrimitives;   // 自定义: 含合规/隐私交易类型
    type ChainSpec    = EnterpriseChainSpec;     // 自定义: 多维 Gas, 硬分叉定义
    type StateCommitment = MerklePatriciaTrie;   // 复用 Reth 默认
    type Storage      = DatabaseEnv;             // 复用 Reth MDBX
}

impl EngineTypes for EnterpriseEngineTypes {
    type PayloadAttributes = EnterprisePayloadAttributes; // 含 Lane 分配
    type PayloadBuiltType  = EnterpriseBuiltPayload;      // 三 Lane 区块
}

// NodeBuilder 组合
impl NodeBuilder for EnterpriseLNode {
    fn components() -> NodeComponentsBuilder {
        NodeComponentsBuilder::default()
            .consensus(SimplexBftConsensus::new())    // 替换: BFT 共识
            .pool(EnterpriseTxPool::new())            // 替换: 多 Lane 交易池
            .evm(EnterpriseEvmConfig::new())          // 扩展: 自定义预编译
            .payload(EnterprisePayloadBuilder::new()) // 替换: 三 Lane 构建器
            .network(EnterpriseNetwork::new())        // 扩展: BFT P2P
    }
}
```

#### EVM 兼容性层级

**选择: EVM 扩展模式 (EVM Extended)**

| 层级 | 含义 | 对开发者影响 | 我们的选择 |
|------|------|-------------|-----------|
| **EVM 等价** (Equivalence) | 100% 字节码兼容 + 所有 opcode 行为一致 | 零影响 | 基线 |
| **EVM 兼容** (Compatible) | 标准 Solidity 合约可部署运行，但某些边缘行为不同 | 极小影响 | 基线 |
| **EVM 扩展** (Extended) | 基线等价 + 额外预编译 + 额外交易类型 | 使用新功能需新 ABI | **选择此项** |

**具体扩展内容:**
1. **预编译扩展**: 6 个企业级原生预编译 (§1.2)
2. **交易类型扩展**: 4 个自定义交易类型 (§1.3)
3. **Gas 模型扩展**: 多维度 Gas 定价 (§1.4)
4. **Opcode 行为**: 保持 100% 标准 EVM 行为, 不修改任何现有 opcode

**对 Solidity/Vyper 开发者的影响评估:**
- **标准 DeFi 合约**: 零修改可部署 — `Uniswap`, `Aave`, `Compound` 等完全兼容
- **使用企业功能的合约**: 需要通过预编译地址静态调用 (standard `staticcall` pattern) — 与调用任何预编译合约的方式一致
- **合规交易**: 使用新交易类型 (0x77) 需要前端/SDK 适配; 链上合约逻辑无影响
- **开发工具链**: Hardhat, Foundry, Remix, OpenZeppelin 全部兼容; 仅需额外 ABI 定义文件

---

### 1.2 自定义预编译合约

基于 Tempo 的 12+ 预编译实现 (WHI-340) 和三叙事需求 (WHI-355)，设计以下企业级预编译体系:

#### 预编译地址空间规划

```
0x0000...0001 ~ 0x0000...0009  — 标准以太坊预编译 (ecRecover, SHA-256, etc.)
0x0100...0000 ~ 0x01FF...FFFF  — 企业核心预编译 (身份, 合规, 加密)
0x0200...0000 ~ 0x02FF...FFFF  — Zone/隐私相关预编译
0x0300...0000 ~ 0x03FF...FFFF  — 治理与系统预编译
0x20C0...0000                   — 合规代币前缀 (参考 Tempo TIP-20)
```

#### L1 主链预编译

| 预编译 | 地址 | 功能 | Tempo 参考 | Gas 成本模型 |
|--------|------|------|-----------|-------------|
| **IdentityRegistry** | `0x0101...0000` | 链上 KYC/AML 状态查询: `isVerified(address)`, `getKycLevel(address)`, `getJurisdiction(address)` | Tempo `AccountKeychain` (0xAAAAAAAA...) | 读: 2,600 gas (cold SLOAD); 写: 20,000 gas (SSTORE) |
| **PolicyRegistry** | `0x0102...0000` | 合规策略注册与评估: `isAuthorized(policyId, from, to, amount)`, `transferAuthorized(policyId, from, to, token, amount)` | Tempo `TIP403Registry` (0x403C...) | 评估: 5,000-15,000 gas (取决于策略复杂度) |
| **CryptoSuite** | `0x0103...0000` | 企业级加密原语: ECIES 加解密, BLS 签名验证, Chaum-Pedersen 零知识证明验证 | Tempo `ChaumPedersenVerify` (6,000 gas), ECIES deposits | ECIES 加密: 10,000 gas; 解密: 12,000 gas; Chaum-Pedersen: 6,000 gas; BLS 验证: 12,000 gas |
| **ComplianceToken** | `0x20C0...` 前缀 | 合规代币标准: 内置 TransferHook + FreezeHook + PolicyEnforcement | Tempo `TIP20Token` (0x20C0... 前缀匹配) | 转账: ~50,000 gas (含策略检查) |
| **TimeLock** | `0x0104...0000` | 合规锁定期管理: `lock(address, amount, unlockTime)`, `vest(address, schedule)`, `checkRelease(address)` | — (新设计) | 锁定: 25,000 gas; 释放检查: 5,000 gas; 批量释放: 5,000 + 3,000/recipient |
| **ThresholdSig** | `0x0105...0000` | 企业级门限签名验证: `verifyMultisig(threshold, signers[], signatures[], message)`, `verifyThreshold(t, n, partialSigs[])` | — (新设计, 参考 Tempo BLS DKG) | 2-of-3: 8,000 gas; 3-of-5: 12,000 gas; t-of-n: 4,000 + 2,000*n gas |

#### Zone L2 预编译

| 预编译 | 地址 | 功能 | Tempo 参考 |
|--------|------|------|-----------|
| **ZoneState** | `0x0201...0000` | Zone 对主链的视图: `mainchainBlockHash()`, `mainchainStateRoot()`, `mainchainTimestamp()` | Tempo `TempoState` (0x1C00...0000) |
| **ZoneInbox** | `0x0201...0001` | 系统存款处理 | Tempo `ZoneInbox` (0x1C00...0001) |
| **ChaumPedersenVerify** | `0x0201...0100` | DLOG 等价证明验证 (ECIES 存款解密正确性) | Tempo (6,000 gas) |
| **AesGcmDecrypt** | `0x0201...0101` | AES-256-GCM 解密 (Zone 内加密通信) | Tempo `aes_gcm.rs` |
| **ZoneTokenFactory** | `0x0201...0200` | Zone 内合规代币工厂 | Tempo `ZoneTip20Factory` |
| **PolicyProxy** | `0x0201...0300` | 从主链 L1 镜像合规策略的只读代理 | Tempo `ZoneTip403ProxyRegistry` |
| **StateReader** | `0x0201...0400` | 读取主链任意合约存储 — Zone 内合规策略镜像的基础 | Tempo `TempoStateReader` |

#### 预编译设计原则

1. **仅限直接调用 (direct-call-only)**: 所有企业级预编译禁止 `delegatecall`, 返回 `DelegateCallNotAllowed` — 防止合约伪装身份调用敏感操作 (参考 Tempo 实现)

2. **`no_std` 强制纪律**: 所有预编译必须 `no_std` 兼容 — 预备 SP1/RISC-V ZK prover guest 执行路径。这是 WHI-357 的核心设计约束。

3. **宏驱动开发**: 类似 Tempo 的 `tempo_precompile!` 宏, 设计 `enterprise_precompile!` 宏强制执行:
   - 直接调用检查
   - 通过 `EvmPrecompileStorageProvider` 的存储上下文获取
   - 标准化 calldata 解码 gas 计量
   - 统一的错误处理和日志

```rust
enterprise_precompile! {
    name: "IdentityRegistry",
    address: 0x0101_0000_0000_0000_0000_0000_0000_0000_0000_0000,
    functions: {
        fn is_verified(address: Address) -> bool [gas: 2_600];
        fn get_kyc_level(address: Address) -> u8 [gas: 2_600];
        fn register_identity(address: Address, level: u8, jurisdiction: u16) -> bool [gas: 20_000];
    }
}
```

4. **前缀匹配模式**: 合规代币 (ComplianceToken) 使用地址前缀匹配 (`0x20C0...`), 支持任意数量的合规代币实例, 无需逐一注册 (参考 Tempo `address.is_tip20()`)

---

### 1.3 交易类型扩展

基于标准以太坊交易类型 (EIP-2718 Typed Transaction Envelope) 和 Tempo 的自定义交易类型 (0x76 AA), 设计以下企业级交易类型体系:

#### 交易类型定义

```rust
pub enum EnterpriseTxEnvelope {
    // === 标准以太坊交易类型 (完全兼容) ===
    Legacy(Signed<TxLegacy>),          // type 0x00 — 传统交易
    Eip2930(Signed<TxEip2930>),        // type 0x01 — 访问列表
    Eip1559(Signed<TxEip1559>),        // type 0x02 — EIP-1559 基础费
    Eip7702(Signed<TxEip7702>),        // type 0x04 — 账户委托

    // === 企业级扩展交易类型 ===
    AccountAbstraction(AASigned),       // type 0x76 — AA 交易 (Tempo 兼容)
    Compliance(ComplianceTx),           // type 0x77 — 合规交易
    PrivacyDeposit(PrivacyDepositTx),   // type 0x78 — 隐私存款
    Governance(GovernanceTx),           // type 0x79 — 治理交易
}
```

**注意**: EIP-4844 blob 交易 **不支持** — 本链不是 DA 层, 与 Tempo 决策一致。

#### 各交易类型详细规范

##### Type 0x76: Account Abstraction (AA) — Tempo 兼容

```rust
pub struct AATx {
    pub chain_id: u64,
    pub nonce: u64,
    pub calls: Vec<AACall>,        // 批量调用 (multi-call)
    pub max_fee_per_gas: u128,
    pub gas_limit: u64,
    pub valid_until: u64,          // 过期时间
}

pub struct AACall {
    pub to: Address,
    pub value: U256,
    pub data: Bytes,
}
```

**签名检测** (参考 Tempo 的基于长度的检测):

| 签名长度 | 算法 | 用途 |
|----------|------|------|
| 65 字节 | secp256k1 ECDSA | 标准以太坊签名 |
| 130 字节 | NIST P-256 | WebAuthn / Passkey |
| 可变 (最大 2KB) | WebAuthn browser assertion | 浏览器原生验证 |
| 可变 | AccountKeychain 委托签名 | 企业级密钥委托 |

**企业关键特性**: P256 (WebAuthn/Passkey) 作为一等公民签名方案 — 支持硬件安全密钥、移动设备生物识别, 降低企业用户的密钥管理门槛。

##### Type 0x77: Compliance Transaction — 合规交易

```rust
pub struct ComplianceTx {
    pub chain_id: u64,
    pub nonce: u64,
    pub to: Address,
    pub value: U256,
    pub data: Bytes,
    pub max_fee_per_gas: u128,
    pub gas_limit: u64,

    // === 合规扩展字段 ===
    pub compliance_proof: ComplianceProof,  // 合规证明
    pub kyc_attestation: Option<Bytes>,     // KYC 证明 (可选)
    pub jurisdiction: u16,                  // 司法管辖区代码
}

pub struct ComplianceProof {
    pub policy_id: u64,                     // 适用的合规策略 ID
    pub proof_type: ProofType,              // ZK 证明 / 签名证明 / 预编译引用
    pub proof_data: Bytes,                  // 证明数据
    pub expires_at: u64,                    // 证明有效期
}

pub enum ProofType {
    ZkSanctionScreening,   // ZK 证明: 不在制裁名单上 (不泄露 PII)
    AttestationSignature,  // 可信第三方签名证明
    PrecompileRef,         // 引用链上 PolicyRegistry 实时检查
}
```

**设计理由**: 合规交易将合规证明嵌入交易本体, 使验证者可在执行前评估合规性, 不合规交易直接拒绝进入区块 (而非执行后 revert)。这参考了 Tempo TIP-403 的 `transferAuthorized()` 模式, 但将其提升到交易类型级别。

##### Type 0x78: Privacy Deposit — 隐私存款

```rust
pub struct PrivacyDepositTx {
    pub chain_id: u64,
    pub nonce: u64,
    pub zone_id: u64,                      // 目标 Zone ID
    pub token: Address,                    // 存款代币地址
    pub amount: U256,                      // 存款金额
    pub max_fee_per_gas: u128,
    pub gas_limit: u64,

    // === 隐私扩展字段 ===
    pub encrypted_payload: Bytes,          // ECIES 加密负载 (64 字节明文)
    pub reveal_to: Option<Address>,        // 可选: 选择性披露目标
}
```

**ECIES 加密流程** (参考 Tempo Zone 实现):

```
明文: [to_address(20)] [memo(32)] [padding(12)] = 64 bytes
   ↓
存款人使用 Sequencer 公钥 ECIES 加密
   ↓
加密文: ECIES ciphertext (可变长度)
   ↓
Sequencer ECDH 导出共享密钥 → AES-256-GCM + HKDF-SHA256 解密
   ↓
Chaum-Pedersen 证明: Sequencer 解密正确 (不泄露私钥)
   ↓
Zone L2 链上验证: ChaumPedersenVerify 预编译 (6,000 gas)
```

**失败路径**: 解密失败 → 退款到发送方 (非 revert), 保障用户资产安全。

##### Type 0x79: Governance Transaction — 治理交易

```rust
pub struct GovernanceTx {
    pub chain_id: u64,
    pub nonce: u64,
    pub proposal_id: u64,                   // 提案 ID
    pub action: GovernanceAction,
    pub max_fee_per_gas: u128,
    pub gas_limit: u64,
    pub multisig_data: ThresholdSigData,    // 门限签名
}

pub enum GovernanceAction {
    UpdateGasParameters(GasConfig),
    UpdateValidatorSet(ValidatorChange),
    UpdateCompliancePolicy(PolicyUpdate),
    EmergencyPause(PauseScope),
    ProtocolUpgrade(UpgradeSpec),
}
```

---

### 1.4 Gas 经济模型

#### 多维度 Gas 定价

企业级场景的 Gas 定价不能是单一维度 — 计算、存储、隐私、合规的资源成本截然不同。设计四维 Gas 模型:

```
Total Gas = Compute Gas + Storage Gas + Privacy Gas + Compliance Gas
```

| Gas 维度 | 定义 | 定价策略 | 参考 |
|----------|------|---------|------|
| **Compute Gas** | 标准 EVM 操作码执行成本 | 与以太坊一致 (EIP-1559 基础费 + 小费) | 以太坊 EVM gas schedule |
| **Storage Gas** | 状态写入成本 (SSTORE, 合约创建) | 标准 EVM 存储定价 (cold 2,100 / warm 100) | 以太坊 EIP-2929 |
| **Privacy Gas** | ZK 证明生成/验证、ECIES 加解密的额外成本 | 固定额外成本 per 操作 | Tempo: ChaumPedersen 6,000 gas |
| **Compliance Gas** | 合规策略评估的额外成本 | 策略复杂度线性递增 | Tempo TIP-403: ~5,000-15,000 gas |

#### Gas 单位与定价

**参考 Tempo 的 attodollar 体系**:

```
1 attodollar = 10^{-18} USD
Gas Price Scaling Factor = 10^{12}
即: gas_balance = gas_limit * gas_price / 10^{12}
```

| 操作 | Gas 消耗 | 按 T1 基础费 (20B attodollar/gas) 的 USD 成本 |
|------|---------|---------------------------------------------|
| 标准 ETH 转账 | 21,000 | ~$0.00042 |
| 合规代币转账 | ~50,000 (含策略检查) | ~$0.001 |
| 合规交易 (带 ZK 证明) | ~100,000 | ~$0.002 |
| 隐私存款 (ECIES) | ~80,000 | ~$0.0016 |
| 复杂 DeFi 操作 | ~200,000-500,000 | ~$0.004-0.01 |

**Payment 场景的性能满足**: 按 $0.001/tx 计, Payment Zone 需要 >10,000 TPS, 每秒 gas 消耗 = 10,000 × 50,000 = 500M gas/s。Payment Lane 的 `shared_gas_limit` 需要相应配置。

#### Payment Lane 特殊定价

参考 Tempo Payment Lane 的设计 (WHI-340):

**三车道 Gas 预算**:

```
区块总 Gas 限制
├── System Lane: 系统预留 (奖励分发, 验证者配置更新)
├── Payment Lane: shared_gas_limit (区块头字段, 可动态调整)
│   └── 仅限合规代币转账 (0x20C0 前缀匹配)
└── General Lane: general_gas_limit (30M 固定, 与 Tempo T1+ 一致)
    └── 智能合约, DeFi, 所有其他交易
```

**反噪声邻居保证**: 当 `general_gas_limit` 耗尽时, 非 Payment 交易被阻止, 即使区块总容量仍有剩余。Payment 交易继续使用 `shared_gas_limit`。这确保了 Payment 吞吐量不受 DeFi/合约执行高峰的影响。

**Payment Lane 分类逻辑** (参考 Tempo v1/v2):

```rust
// v1 分类 (共识级别 — 宽松)
fn is_payment_v1(tx: &EnterpriseTxEnvelope) -> bool {
    match tx {
        Legacy(tx) | Eip1559(tx) => is_compliance_token_call(tx.to()),
        AA(tx) => tx.calls.iter().all(|c| is_compliance_token_call(c.to())),
        _ => false,
    }
}

// v2 分类 (构建器级别 — 严格)
fn is_payment_v2(tx: &EnterpriseTxEnvelope) -> bool {
    is_payment_v1(tx)
        && has_recognized_payment_selector(tx)
        && !has_access_list(tx)
        && !has_authorization_list(tx)
}

fn is_compliance_token_call(addr: Address) -> bool {
    addr.as_slice()[..12] == COMPLIANCE_TOKEN_PREFIX // 0x20C0...
}
```

#### 企业级 Gas 代付 (Paymaster/Meta-Transaction)

| 模式 | 适用场景 | 实现方式 |
|------|---------|---------|
| **Paymaster (ERC-4337)** | 企业为员工代付 gas | Paymaster 合约验证 + 代付; AA 交易 (0x76) 原生支持 |
| **Fee Sponsorship** | 机构为客户代付 | 链级别: 指定 sponsor address, 从 sponsor 余额扣除 gas |
| **Stablecoin Gas** | 用稳定币支付 gas | 合规代币 (0x20C0) 作为 gas 代币; 通过 DEX 预编译自动兑换 |
| **Zero-Fee Zone** | Payment Zone 内特定操作免 gas | Zone 级别配置: 特定交易类型 gas 为 0; Sequencer 承担成本 |

**参考**: Mantle 曾实现 meta-transaction V1-V3 但在 MantleEverestTime 禁用 (WHI-341)。我们将其作为一等公民功能保留并完善, 因为企业用户不应被迫管理 gas 代币。

---

## 2. 共识层架构设计

### 2.1 共识协议选型与定制

#### 选型: Commonware Simplex BFT

基于 WHI-357 架构蓝图和 WHI-345 共识对比分析, 选择 **Commonware Simplex BFT** 作为主链共识协议。

**选型对比**:

| 维度 | Simplex BFT (选中) | CometBFT/Tendermint | HotStuff | Canton 2PC |
|------|-------------------|---------------------|----------|-----------|
| **终局延迟** | ~600ms (亚秒) | ~6 秒 | ~2-3 秒 | 秒级 (2PC) |
| **消息复杂度** | O(n) 阈值签名 (优于经典 PBFT O(n²)) | O(n²) | O(n) (线性) | O(n) (n=确认方数) |
| **容错** | f < n/3 (BFT) | f < n/3 | f < n/3 | 任一方可否决 (2PC) |
| **签名方案** | BLS12-381 门限签名 (DKG) | Ed25519 | BLS (变体) | N/A |
| **Leader 选举** | VRF (防 MEV) | 确定性轮换 | 确定性轮换 | N/A (Sequencer 排序) |
| **Reth SDK 集成** | 已验证 (Tempo 主网) | 无已知集成 | 无已知集成 | 不适用 |
| **生产验证** | Tempo 主网 (2026-03-31) | Cosmos 生态广泛使用 | Meta Diem (已停运) | Canton (Digital Asset, $2T+/月) |
| **企业适配** | 强 — 许可制, VRF 抗 MEV | 中 — 主要面向公链 | 中 — 理论优美但落地少 | 强 — 但不兼容 EVM |

**核心优势**:
1. **亚秒终局 (~600ms)**: 满足 Payment 实时结算和 xstocks T+0 的严苛需求 — CometBFT 的 6 秒无法满足
2. **Reth SDK 生产验证**: Tempo 主网已跑通 Simplex BFT + Reth SDK 的完整路径, 我们无需从零验证可行性
3. **BLS12-381 门限签名**: 区块证书是聚合签名而非个体签名集合, 验证效率高, 区块头更紧凑
4. **VRF 领导者选举**: 每轮随机选择出块者, 降低 MEV 提取 (相比确定性轮换, 攻击者无法预测下一轮出块者)
5. **双运行时隔离**: 共识和执行分别运行在独立 Tokio 运行时上, 执行层负载波动不会影响共识延迟

#### Simplex BFT 深度技术分析

**协议流程 (单轮)**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Simplex BFT 单轮                          │
│                                                              │
│  1. VRF Leader Election                                      │
│     └─ 当前轮次的 VRF 输出决定 Leader                         │
│                                                              │
│  2. Leader Propose                                           │
│     └─ Leader 从交易池取交易 → 构建区块 → 广播 Propose 消息    │
│                                                              │
│  3. Validators Vote                                          │
│     └─ 验证者验证区块 → 签署 BLS 部分签名 → 发送给 Leader      │
│                                                              │
│  4. Leader Aggregate                                         │
│     └─ 收集 ≥2/3 部分签名 → 聚合为 BLS 门限签名 (区块证书)     │
│                                                              │
│  5. Certificate Broadcast                                    │
│     └─ 区块 + 证书广播 → 所有节点验证证书 → 提交区块 → 终局    │
│                                                              │
│  延迟: ~500ms (构建) + ~100ms (网络) ≈ 600ms 总终局延迟        │
└─────────────────────────────────────────────────────────────┘
```

**BLS12-381 DKG (Distributed Key Generation)**:

```
初始化阶段:
  1. n 个验证者运行 DKG 协议
  2. 生成共享公钥 PK 和每个验证者的私钥份额 sk_i
  3. 门限参数 t = ⌈2n/3⌉

签名阶段:
  1. 验证者 i 对区块哈希 H 生成部分签名: σ_i = Sign(sk_i, H)
  2. 任意 t 个部分签名可恢复完整签名: σ = Aggregate(σ_1, ..., σ_t)
  3. 验证: Verify(PK, H, σ) = true

安全性:
  - 至少 t 个诚实验证者才能生成有效签名
  - 攻击者控制 < t 个验证者无法伪造签名
  - 区块证书 = (区块哈希, 聚合 BLS 签名) — 紧凑且高效验证
```

**双运行时隔离架构** (参考 Tempo `commonware-node`):

```
┌──────────────────────────────────────────────┐
│              Enterprise L1 Node               │
│                                               │
│  ┌───────────────┐    ┌───────────────────┐   │
│  │  Tokio Runtime │    │   Tokio Runtime    │  │
│  │  (Consensus)   │    │   (Execution)      │  │
│  │                │    │                    │  │
│  │  Simplex BFT   │◄──►│  Reth Execution   │  │
│  │  P2P Network   │EngAPI  revm v38+       │  │
│  │  VRF Leader    │    │  State DB (MDBX)  │  │
│  │  BLS DKG       │    │  TX Pool          │  │
│  │                │    │  Payload Builder  │  │
│  └───────────────┘    └───────────────────┘  │
│                                               │
│  隔离保证: 执行层的 heavy EVM 计算 (DeFi 合约,  │
│           ZK 验证) 不会阻塞共识消息处理和投票     │
└──────────────────────────────────────────────┘
```

---

### 2.2 验证者集管理

企业级 L1 的验证者管理与公链截然不同 — 采用**许可制准入**而非无许可质押。

#### 验证者准入机制

| 维度 | 设计 | 理由 |
|------|------|------|
| **准入模式** | 许可制 (Permissioned) | 验证者必须通过 KYC/AML, 绑定企业实体 |
| **身份绑定** | 验证者地址 ↔ 企业实体 ↔ 司法管辖区 (通过 IdentityRegistry 预编译) | 监管要求: 可追溯、可问责 |
| **最低要求** | 企业级 KYC (Lv3+), 合格托管商, 监管合规证明 | 金融级基础设施安全要求 |
| **初始验证者数** | 7-15 个 (启动阶段); 扩展到 21-50 个 | BFT 消息复杂度 vs 去中心化权衡 |
| **BFT 安全门限** | f < n/3 — 即 7 个验证者允许最多 2 个拜占庭 | Simplex BFT 标准 |
| **地理分布** | 至少 3 个大洲, 满足数据本地化要求 | 司法管辖区合规 + 网络延迟优化 |

#### 验证者配置管理

参考 Tempo 的 `ValidatorConfig` / `ValidatorConfigV2` 预编译 (WHI-340):

```rust
// 验证者配置预编译 (0x0301...0000)
pub struct ValidatorConfig {
    // v1: 基本验证者信息
    fn register_validator(bls_pubkey: Bytes, enterprise_id: u64) -> bool;
    fn deregister_validator(validator: Address) -> bool;
    fn get_validator_set() -> Vec<ValidatorInfo>;

    // v2: 高级管理
    fn rotate_key(old_key: Bytes, new_key: Bytes, proof: Bytes) -> bool;
    fn update_stake(validator: Address, new_stake: U256) -> bool;
    fn slash(validator: Address, evidence: Bytes) -> bool;
}
```

#### 验证者轮换与退出

```
验证者加入流程:
  1. 企业实体提交 KYC → IdentityRegistry 注册
  2. 运行 DKG 协议获取 BLS 密钥份额
  3. 治理交易 (0x79) 提案: 添加验证者
  4. 现有 ≥2/3 验证者投票通过
  5. 下一个 epoch 生效

验证者退出流程:
  1. 验证者提交退出请求 (或被治理投票移除)
  2. 冷却期: N 个 epoch (防止快速退出攻击)
  3. DKG 重新运行 (剩余验证者)
  4. 冷却期结束后正式退出
```

---

### 2.3 出块机制与 MEV 防护

#### Leader 轮换策略

| 策略 | 机制 | 优缺点 |
|------|------|--------|
| **确定性轮换** (Round-Robin) | 按验证者索引依次轮换 | 简单可预测 — 但攻击者可预知下一轮 Leader |
| **加权随机** (Weighted Random) | 按 stake 加权的伪随机选择 | 更公平 — 但种子可被预测 |
| **VRF 随机** (Verifiable Random Function) | VRF 输出决定 Leader, 可验证但不可预测 | **选择此项** — 最强抗 MEV |

**VRF Leader Election 详细设计**:

```
每轮 r 的 Leader 选举:
  1. 每个验证者 i 计算: (π_i, y_i) = VRF(sk_i, r || prev_block_hash)
  2. y_i 是 VRF 输出 (伪随机数)
  3. Leader = argmin(y_1, y_2, ..., y_n) — 输出最小的验证者成为 Leader
  4. 任何人可验证: VRF.Verify(pk_i, r || prev_block_hash, π_i, y_i)

抗 MEV 性质:
  - 攻击者无法预测下一轮 Leader (需要所有验证者的 VRF 输出)
  - Leader 在被选中后才知道自己是 Leader (commit-then-reveal)
  - 无法提前贿赂或攻击目标 Leader
```

#### 空块处理 (企业场景的交易稀疏期)

企业链与公链不同 — 可能出现长时间无交易的空闲期 (如非工作时间、假期)。

| 策略 | 描述 | 适用场景 |
|------|------|---------|
| **固定出块** | 即使无交易也产生空块 | 保持恒定心跳, 简化客户端同步逻辑 |
| **按需出块** | 仅在有交易时出块; 空闲时仅发心跳 | 节省存储和网络开销 |
| **混合策略** | 有交易时 ~600ms 出块; 空闲时每 N 秒一个心跳块 | **选择此项** |

**混合策略详细设计**:

```
if pending_tx_count > 0 {
    // 活跃模式: ~600ms 出块 (标准 Simplex BFT 节奏)
    produce_block(pending_txs);
} else if time_since_last_block > HEARTBEAT_INTERVAL {
    // 心跳模式: 每 5 秒产生心跳空块
    produce_heartbeat_block();
} else {
    // 静默: 等待交易到达
    wait_for_tx_or_timeout();
}

const HEARTBEAT_INTERVAL: Duration = Duration::from_secs(5);
```

**心跳块的作用**: 维持时间线连续性 (Zone 通过 L1 区块事件驱动); 供轻客户端同步; 验证者活性证明。

#### MEV 防护: 多层防御

xstocks 叙事要求公平交易 (WHI-355): "大单信息不能泄露 — 暗池要求隐含了订单流保护"。

| 防护层 | 机制 | 防护目标 |
|--------|------|---------|
| **L1: VRF Leader Election** | 不可预测的 Leader 选择 | 无法提前锁定目标 Leader |
| **L1: Payment Lane 隔离** | Payment 交易与 General 交易物理隔离 | 无法跨车道套利 |
| **L2: 排序公平性** | 时间戳排序 (FIFO within lane) | 无法通过 gas 竞价前置交易 |
| **L2: xStocks Zone 暗池** | 加密订单簿匹配 (Zone 内 ECIES 加密) | 订单信息不泄露 |
| **协议级: 序列器可见性** | Zone 序列器看到明文但受合规约束 (Canton 模式) | 将 MEV 提取从技术问题转化为合规问题 |

**与 Canton 的对比**: Canton Sequencer **无法看到交易内容** (仅处理加密 blob), 从架构层面消除了 MEV。我们的设计在 Zone 内无法完全达到 Canton 的隐私级别 (Zone Sequencer 能看到明文), 但通过合规约束 + 加密订单簿 + 市场监控模块, 将 MEV 风险控制在可接受范围内。长期演进方向: 参考 Canton 的加密排序模式, 逐步将 Zone Sequencer 升级为 "看不到交易内容的排序者"。

---

## 3. 双重终局性模型详细设计

### 3.1 三层终局性架构

这是本设计的**核心创新点** — 基于 WHI-357 架构蓝图的双重终局性概念, 进一步细化为三层渐进式终局性:

```
交易提交
   │
   ▼
┌──────────────────────────────────────────────────────┐
│  Layer 1: BFT 即时终局性 (Instant Finality)            │
│  ─────────────────────────────────────────            │
│  机制: Simplex BFT 2/3 验证者共识                       │
│  延迟: ~600ms                                         │
│  安全假设: ≥2/3 验证者诚实                               │
│  适用: Payment 实时结算, xstocks T+0, 日常交易确认        │
│  语义: head = safe = finalized (BFT 不分叉)             │
└────────────────────┬─────────────────────────────────┘
                     │ 每 N 个 BFT epoch 批量
                     ▼
┌──────────────────────────────────────────────────────┐
│  Layer 2: ZK 证明终局性 (Validity Proof Finality)      │
│  ─────────────────────────────────────────            │
│  机制: STARK validity proof (SP1/RISC-V prover)       │
│  延迟: 5-30 分钟 (取决于证明生成速度和批量大小)            │
│  安全假设: 数学证明 (可靠性 ≥ 2^{-80})                   │
│  适用: 跨链桥接, 跨 Zone 资产转移安全保证                  │
│  语义: 状态转换经过数学验证, 不依赖诚实多数假设              │
└────────────────────┬─────────────────────────────────┘
                     │ 证明提交到 Ethereum L1
                     ▼
┌──────────────────────────────────────────────────────┐
│  Layer 3: Ethereum L1 锚定终局性 (L1 Anchor Finality)  │
│  ─────────────────────────────────────────            │
│  机制: ZK proof + state root 提交到 Ethereum Verifier  │
│  延迟: ~12 分钟 (Ethereum finality) + 证明提交延迟       │
│  安全假设: Ethereum L1 安全性 (最强)                     │
│  适用: 最高安全级别 RWA 资产, 跨链桥存/取款结算            │
│  语义: 继承以太坊 L1 安全性, 可被任何 L1 合约验证          │
└──────────────────────────────────────────────────────┘
```

**关键设计决策: 主链不是 Rollup**

本链拥有**独立共识** (Simplex BFT), 不依赖 Ethereum 出块或数据可用性。Ethereum 锚定是**可选增值层**, 不是依赖:
- 即使 Ethereum L1 暂时不可达, 主链继续独立运行 (BFT 终局)
- Ethereum 锚定为跨链桥和最高安全级别资产提供额外安全保证
- 这与 WHI-357 的设计原则一致: "Rollup 模型要求所有交易数据发布到 L1 — 与数据隐私根本不兼容"

### 3.2 叙事驱动的可配置终局性

不同叙事对终局性的需求截然不同 (WHI-355 §5.2):

| 叙事 | 需要的终局性层级 | 理由 | 配置 |
|------|----------------|------|------|
| **Payment B2C** | Layer 1 (BFT) 即可 | 用户扫码 → 即时确认; 单笔金额小 | `finality_acceptance = BFT` |
| **Payment B2B** | Layer 1 (BFT) + 合规确认 | 跨境转账需合规审核但不需 L1 锚定 | `finality_acceptance = BFT_COMPLIANCE` |
| **xstocks T+0** | Layer 1 (BFT) + 合规确认 | 即时终局 + 合规确认 = 可做后续交易 | `finality_acceptance = BFT_COMPLIANCE` |
| **xstocks Dark Pool** | Layer 1 (BFT) | 暗池内部匹配, 单方风险 | `finality_acceptance = BFT` |
| **RWA 日常交易** | Layer 1 (BFT) + 合规确认 | 中等金额, 需机构确认 | `finality_acceptance = BFT_COMPLIANCE` |
| **RWA DVP 大额** | Layer 2 (ZK) | DVP 结算需数学证明级安全 | `finality_acceptance = ZK_PROOF` |
| **RWA 最高安全** | Layer 3 (L1 Anchor) | 超大额 RWA, 需以太坊 L1 安全背书 | `finality_acceptance = L1_ANCHOR` |
| **跨链桥** | Layer 2/3 (ZK/L1) | 跨链资产转移需不可伪造的证明 | `finality_acceptance = ZK_PROOF` |

**合约级别的终局性查询 API**:

```solidity
interface IFinalityOracle {
    enum FinalityLevel {
        PENDING,           // 交易在 mempool
        BFT_CONFIRMED,     // BFT 2/3 共识确认 (~600ms)
        COMPLIANCE_CLEARED,// BFT + 合规策略通过
        ZK_PROVEN,         // ZK validity proof 生成
        L1_ANCHORED        // Ethereum L1 验证通过
    }

    /// 查询交易的当前终局性级别
    function getFinalityLevel(bytes32 txHash) external view returns (FinalityLevel);

    /// 查询区块的终局性级别
    function getBlockFinality(uint256 blockNumber) external view returns (FinalityLevel);

    /// 等待特定终局性级别 (供合约逻辑使用)
    function requireFinality(bytes32 txHash, FinalityLevel minLevel) external view returns (bool);
}
```

**使用示例**:

```solidity
// RWA DVP 合约
function settleDVP(uint256 tradeId) external {
    Trade storage trade = trades[tradeId];

    // 证券转移: 需要 ZK_PROVEN 级别终局
    require(
        finalityOracle.getFinalityLevel(trade.securityTxHash) >= FinalityLevel.ZK_PROVEN,
        "Security transfer not yet ZK proven"
    );

    // 资金转移: BFT 即可 (同链内)
    require(
        finalityOracle.getFinalityLevel(trade.paymentTxHash) >= FinalityLevel.BFT_CONFIRMED,
        "Payment not yet confirmed"
    );

    // 执行 DVP 结算
    _executeSettlement(trade);
}

// Payment 合约
function confirmPayment(bytes32 txHash) external {
    // Payment: BFT 终局即可
    require(
        finalityOracle.getFinalityLevel(txHash) >= FinalityLevel.BFT_CONFIRMED,
        "Payment not confirmed"
    );
    emit PaymentConfirmed(txHash);
}
```

### 3.3 终局性状态机

每笔交易经历以下终局性状态转换:

```
┌──────────┐   submit    ┌──────────┐  BFT 2/3   ┌──────────────┐
│ PENDING  │────────────►│ INCLUDED │───────────►│ BFT_CONFIRMED│
└──────────┘             └──────────┘            └──────┬───────┘
                                                        │
                                               compliance check
                                                        │
                                                        ▼
                                               ┌────────────────────┐
                                               │COMPLIANCE_CLEARED  │
                                               └────────┬───────────┘
                                                        │
                                              ZK proof batch covers
                                                   this block
                                                        │
                                                        ▼
                                               ┌──────────────┐
                                               │  ZK_PROVEN   │
                                               └──────┬───────┘
                                                      │
                                            L1 Verifier confirms
                                                      │
                                                      ▼
                                               ┌──────────────┐
                                               │ L1_ANCHORED  │
                                               └──────────────┘
```

**状态持久化**: 终局性状态存储在链上 (FinalityOracle 合约), 由以下系统组件更新:
- `BFT_CONFIRMED`: 共识层在区块被 finalize 时自动设置 (BFT 不分叉, head=finalized)
- `COMPLIANCE_CLEARED`: PolicyRegistry 预编译在合规检查通过时设置
- `ZK_PROVEN`: ZK Prover 提交证明时更新
- `L1_ANCHORED`: L1 Anchor Relayer 在 Ethereum Verifier 合约确认后更新

---

## 4. ZK 证明系统设计

### 4.1 证明范围与架构

ZK 证明系统服务于 Layer 2 终局性 (跨链安全) 和 Layer 3 终局性 (L1 锚定)。

**需要证明什么?**

| 证明范围 | 内容 | 目的 | 复杂度 |
|----------|------|------|--------|
| **状态转换正确性** | 给定前状态 S₁ + 区块 B → 后状态 S₂ 的计算正确 | 类 ZK Rollup 的有效性证明; 使 L1 不信任主链直接验证 | 高 (全 EVM 证明) |
| **合规规则执行正确性** | PolicyRegistry 的每次 `isAuthorized` 调用结果正确 | 合规审计者可验证合规规则确实被执行 | 中 |
| **Zone Validity Proof** | Zone 状态转换正确 (Zone 内交易正确执行) | Zone 数据不上链 (Validium), 需要有效性证明替代数据可用性 | 高 |
| **跨 Zone 转移证明** | Zone A → 主链 → Zone B 的资产转移正确 | 跨 Zone 桥安全 | 中 |

#### 证明架构总览

```
┌──────────────────────────────────────────────────────────────┐
│                    ZK 证明系统架构                              │
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  主链 Prover     │  │  RWA Zone Prover │  │ xStocks Zone │ │
│  │  (状态转换)      │  │  (Zone validity) │  │    Prover    │ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬───────┘ │
│           │                    │                    │         │
│           ▼                    ▼                    ▼         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Proof Aggregator (证明聚合)                   │ │
│  │  多个 Zone 证明 + 主链证明 → 单一递归聚合证明                 │ │
│  └────────────────────────┬────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │          Ethereum L1 Verifier Contract                    │ │
│  │  验证聚合证明 → 更新 state root → 启用跨链桥操作             │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 证明生成管线

#### 技术栈选型

| 组件 | 选型 | 理由 |
|------|------|------|
| **证明系统** | STARK (可靠性 ≥ 2^{-80}) | 无需 trusted setup; 量子抗性; WHI-357 选定 |
| **Prover 框架** | SP1 / RISC-V | 通用 zkVM — 用 Rust 写逻辑, 编译到 RISC-V, SP1 自动生成 STARK 证明 |
| **硬件加速** | CUDA GPU | Prividium Airbender 方向; 证明生成提速 10-100x |
| **聚合方式** | 递归 STARK | 多个子证明递归聚合为单个证明, 降低 L1 验证成本 |

#### SP1 Prover Guest 设计

**核心约束**: 所有预编译和状态转换逻辑必须 `no_std` 兼容 — 这是 WHI-357 设定的强制纪律, Tempo 已在代码层面实践。

```rust
// SP1 Guest 程序: 证明区块执行正确性
#![no_std]
#![no_main]

sp1_zkvm::entrypoint!(main);

pub fn main() {
    // 1. 读取公共输入: 前状态根, 后状态根, 区块头
    let pre_state_root: [u8; 32] = sp1_zkvm::io::read();
    let post_state_root: [u8; 32] = sp1_zkvm::io::read();
    let block_header: BlockHeader = sp1_zkvm::io::read();

    // 2. 读取私有输入: 完整状态, 交易列表
    let state: StateDB = sp1_zkvm::io::read();
    let transactions: Vec<Transaction> = sp1_zkvm::io::read();

    // 3. 验证前状态根
    assert_eq!(state.root(), pre_state_root);

    // 4. 执行所有交易 (使用 no_std 兼容的 revm)
    let mut executor = EvmExecutor::new(state);
    for tx in transactions {
        executor.execute(tx);
    }

    // 5. 验证后状态根
    assert_eq!(executor.state().root(), post_state_root);

    // 6. 写出公共输出 (供 L1 Verifier 验证)
    sp1_zkvm::io::commit(&pre_state_root);
    sp1_zkvm::io::commit(&post_state_root);
    sp1_zkvm::io::commit(&block_header.hash());
}
```

**参考**: Mantle 的 `cmd/keeper/` zkVM binary (WHI-341) 和 Tempo Zones 的 `no_std` 预编译已为 SP1 guest 执行做好准备。

#### 证明生成时间估算

| 工作负载 | 区块数 | 交易数 | 估计证明时间 (GPU) | 估计证明时间 (CPU) |
|----------|--------|--------|-------------------|-------------------|
| 轻负载 | 100 (1 min) | ~1,000 | ~3 分钟 | ~30 分钟 |
| 标准负载 | 500 (5 min) | ~10,000 | ~10 分钟 | ~100 分钟 |
| 重负载 | 1000 (10 min) | ~50,000 | ~20 分钟 | ~200 分钟 |

**批量策略**: 每 N 个 BFT epoch 生成一次证明。N 可配置:
- 高频 (N=100, ~1 分钟): 适合高安全性场景, 证明生成成本高
- 标准 (N=500, ~5 分钟): 平衡安全性和成本
- 低频 (N=3000, ~30 分钟): 成本敏感场景

### 4.3 证明验证与 L1 锚定

#### Ethereum L1 Verifier Contract

```solidity
// 部署在 Ethereum L1 上的验证合约
contract EnterpriseChainVerifier {
    // 最新验证过的状态
    bytes32 public latestStateRoot;
    uint256 public latestBlockNumber;
    uint256 public latestBatchIndex;

    // Zone 状态
    mapping(uint64 => bytes32) public zoneStateRoots;

    /// 提交并验证聚合 STARK 证明
    function verifyBatch(
        uint256 batchIndex,
        bytes32 prevStateRoot,
        bytes32 newStateRoot,
        uint256 blockRange_start,
        uint256 blockRange_end,
        ZoneProof[] calldata zoneProofs,
        bytes calldata aggregatedProof
    ) external {
        require(prevStateRoot == latestStateRoot, "State root mismatch");
        require(batchIndex == latestBatchIndex + 1, "Batch sequence error");

        // STARK 证明验证
        require(
            starkVerifier.verify(
                aggregatedProof,
                abi.encode(prevStateRoot, newStateRoot, blockRange_start, blockRange_end)
            ),
            "Invalid proof"
        );

        // 更新状态
        latestStateRoot = newStateRoot;
        latestBlockNumber = blockRange_end;
        latestBatchIndex = batchIndex;

        // 更新 Zone 状态
        for (uint i = 0; i < zoneProofs.length; i++) {
            zoneStateRoots[zoneProofs[i].zoneId] = zoneProofs[i].stateRoot;
        }

        emit BatchVerified(batchIndex, newStateRoot, blockRange_end);
    }

    /// 跨链桥: 验证主链上的存款/提款
    function verifyWithdrawal(
        bytes32 withdrawalHash,
        bytes32[] calldata merkleProof,
        uint256 batchIndex
    ) external view returns (bool) {
        require(batchIndex <= latestBatchIndex, "Batch not yet verified");
        return MerkleProof.verify(merkleProof, latestStateRoot, withdrawalHash);
    }
}
```

#### 验证频率与成本权衡

| 频率 | Ethereum L1 Gas 成本/次 | 月度成本 (假设 ETH=$3000) | 安全延迟 |
|------|----------------------|--------------------------|---------|
| 每 1 分钟 | ~300,000 gas (~$0.90) | ~$38,880 | 1 分钟 + L1 finality |
| 每 5 分钟 | ~300,000 gas (~$0.90) | ~$7,776 | 5 分钟 + L1 finality |
| 每 30 分钟 | ~300,000 gas (~$0.90) | ~$1,296 | 30 分钟 + L1 finality |
| 每 1 小时 | ~300,000 gas (~$0.90) | ~$648 | 1 小时 + L1 finality |

**建议**: 默认每 5 分钟提交一次证明 (月度成本 ~$7,776), 为跨链桥和高安全资产提供合理的安全延迟。高安全模式可切换到每 1 分钟。

---

## 5. Engine API 接口规范

### 5.1 执行-共识接口设计

参考 Ethereum Engine API 和 Tempo 的实现 (WHI-340), 设计执行层与共识层之间的标准化接口:

```
┌─────────────────────────────────────────────────────────────┐
│                    Engine API 接口                            │
│                                                              │
│   ConsensusLayer (Simplex BFT)    ExecutionLayer (Reth SDK)  │
│          │                                │                  │
│          ├─ engine_forkchoiceUpdatedV3 ──►│                  │
│          │   (payload_attributes)          │                  │
│          │                                ├─ build payload   │
│          │ ◄── payload_id ───────────────┤                  │
│          │                                │                  │
│          ├─ engine_getPayloadV3 ─────────►│                  │
│          │                                ├─ return payload  │
│          │ ◄── ExecutionPayload ──────────┤                  │
│          │                                │                  │
│          ├─ engine_newPayloadV3 ──────────►│                  │
│          │   (execution_payload)           ├─ execute block  │
│          │                                ├─ validate state  │
│          │ ◄── PayloadStatus ─────────────┤                  │
│          │                                │                  │
│          ├─ engine_forkchoiceUpdatedV3 ──►│                  │
│          │   (finalized_block_hash)        ├─ commit state   │
│          │ ◄── ForkchoiceState ───────────┤                  │
│          │                                │                  │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 区块生命周期

#### 主链区块生命周期 (Simplex BFT + Reth)

```
Phase 1: Leader Selection (VRF)
  └─ VRF 选举当前轮次 Leader

Phase 2: Block Construction
  └─ Leader 发送 engine_forkchoiceUpdatedV3(head, payload_attributes)
  └─ Reth 执行层:
       1. 从 PaymentLane 取交易 → 执行, 消耗 shared_gas_limit
       2. 从 GeneralLane 取交易 → 执行, 消耗 general_gas_limit
       3. 计算状态根, 组装 EnterprisePayload
  └─ Leader 调用 engine_getPayloadV3 获取区块

Phase 3: Block Proposal
  └─ Leader 向所有验证者广播 Propose(block)

Phase 4: Voting
  └─ 每个验证者:
       1. 调用 engine_newPayloadV3(block) — 本地执行验证
       2. 验证状态根匹配
       3. 验证交易合法性 (合规检查等)
       4. 生成 BLS 部分签名 → 发送回 Leader

Phase 5: Aggregation & Commit
  └─ Leader 收集 ≥2/3 部分签名
  └─ 聚合为 BLS 门限签名 (区块证书)
  └─ 广播区块 + 证书

Phase 6: Finalization
  └─ 所有节点验证证书 → engine_forkchoiceUpdatedV3(finalized=block_hash)
  └─ 状态提交 → 区块终局 (~600ms 总延迟)
```

#### Zone 区块生命周期 (NoopConsensus + L1 Event-Driven)

参考 Tempo Zone 的 `ZoneEngine` 设计 (WHI-340):

```
Phase 1: L1 Event Detection
  └─ L1Subscriber 监听主链新区块
  └─ 提取 deposit 事件 → DepositQueue

Phase 2: Zone Block Construction
  └─ ZoneEngine 从 DepositQueue peek 当前 L1 区块
  └─ 构建 ZonePayloadAttributes (含 L1 block info)
  └─ engine_forkchoiceUpdatedV3(head, zone_payload_attributes)

Phase 3: Zone Block Execution
  └─ Reth 执行层处理 Zone 交易:
       1. 系统存款 (deposits from L1)
       2. Zone 内部交易 (如果有)
       3. 合规策略镜像更新 (SharedPolicyCache)

Phase 4: Instant Finalization
  └─ NoopConsensus: head = safe = finalized
  └─ engine_forkchoiceUpdatedV3(finalized=zone_block_hash)
  └─ Zone 区块与 L1 区块 1:1 映射
```

### 5.3 状态管理接口

```rust
/// 企业级 Engine API 扩展
trait EnterpriseEngineApi {
    // === 标准 Engine API (Ethereum 兼容) ===
    fn engine_forkchoice_updated_v3(
        forkchoice_state: ForkchoiceState,
        payload_attributes: Option<EnterprisePayloadAttributes>,
    ) -> ForkchoiceUpdateResult;

    fn engine_new_payload_v3(
        payload: EnterpriseExecutionPayload,
    ) -> PayloadStatus;

    fn engine_get_payload_v3(
        payload_id: PayloadId,
    ) -> EnterprisePayload;

    // === 企业级扩展 ===

    /// 查询终局性状态
    fn engine_get_finality_status(
        block_hash: H256,
    ) -> FinalityStatus;

    /// 获取合规检查结果 (供共识层在投票前查询)
    fn engine_check_compliance(
        transactions: Vec<EnterpriseTxEnvelope>,
    ) -> Vec<ComplianceResult>;

    /// Zone 状态同步
    fn engine_sync_zone_state(
        zone_id: u64,
        l1_block_number: u64,
    ) -> ZoneSyncResult;

    /// ZK 证明请求 (触发 prover 为指定区块范围生成证明)
    fn engine_request_proof(
        from_block: u64,
        to_block: u64,
    ) -> ProofRequestId;
}
```

#### 回滚/重组处理

**BFT 共识的核心优势: 不会分叉** — 一旦区块被 2/3 验证者签署证书, 该区块即为终局, 不可能被回滚。

但仍需考虑异常情况:

| 异常场景 | 处理方式 |
|----------|---------|
| **Leader 超时** | VRF 选择新 Leader; 旧 Leader 的未完成区块被丢弃 |
| **验证者宕机** | 只要在线验证者 ≥2/3, 共识继续; 宕机验证者重启后同步 |
| **网络分区** | 超过 1/3 验证者不可达 → 共识暂停 (safety > liveness); 分区恢复后自动恢复 |
| **拜占庭验证者** | < 1/3 拜占庭 → 无影响 (BFT 安全保证); ≥ 1/3 拜占庭 → 共识不安全, 需人工干预 |
| **Zone Sequencer 宕机** | Zone 停止出块; 用户可通过 L1 forced inclusion 提款; Zone 恢复后从 L1 事件重放 |

---

## 6. 交易池分层设计

### 6.1 多层交易池架构

参考 Tempo 的 Payment Lane 交易池设计 (WHI-340), 扩展为企业级多层交易池:

```
┌──────────────────────────────────────────────────────┐
│               Enterprise Transaction Pool              │
│                                                        │
│  ┌──────────────────┐                                 │
│  │  System Queue     │  最高优先级                      │
│  │  (治理, 验证者)    │  系统交易: 奖励分发, 配置更新      │
│  └────────┬─────────┘                                 │
│           │                                            │
│  ┌────────▼─────────┐                                 │
│  │  Payment Lane     │  高优先级                        │
│  │  (支付车道)       │  合规代币转账 (0x20C0 前缀)       │
│  │                   │  Gas 预算: shared_gas_limit       │
│  └────────┬─────────┘                                 │
│           │                                            │
│  ┌────────▼─────────┐                                 │
│  │  Compliance Queue │  中优先级                        │
│  │  (合规待审队列)    │  需额外合规检查的交易              │
│  │                   │  通过 → 移入 Standard / Payment   │
│  │                   │  拒绝 → 驳回                      │
│  └────────┬─────────┘                                 │
│           │                                            │
│  ┌────────▼─────────┐                                 │
│  │  Standard Pool    │  标准优先级                      │
│  │  (标准池)         │  DeFi, 合约调用, 普通交易          │
│  │                   │  Gas 预算: general_gas_limit      │
│  └──────────────────┘                                 │
│                                                        │
└──────────────────────────────────────────────────────┘
```

#### Payment Lane 分类逻辑

两级分类 (参考 Tempo v1/v2):

```rust
/// v1 分类: 共识级别 (宽松 — 用于 gas 预算分配)
/// 判断依据: 交易目标地址是否为合规代币 (0x20C0 前缀)
pub fn classify_payment_v1(tx: &EnterpriseTxEnvelope) -> bool {
    match tx {
        EnterpriseTxEnvelope::Legacy(tx) => is_compliance_token(tx.to()),
        EnterpriseTxEnvelope::Eip1559(tx) => is_compliance_token(tx.to()),
        EnterpriseTxEnvelope::AccountAbstraction(tx) => {
            tx.calls.iter().all(|c| is_compliance_token(c.to()))
        }
        _ => false,
    }
}

/// v2 分类: 构建器级别 (严格 — 用于实际 Lane 路由)
/// 额外检查: calldata 必须匹配识别的 payment selector, 无 access list
pub fn classify_payment_v2(tx: &EnterpriseTxEnvelope) -> bool {
    classify_payment_v1(tx)
        && has_payment_selector(tx)
        && !has_access_list(tx)
        && !has_authorization_list(tx)
}
```

#### 三车道区块构建

```rust
/// 区块构建器: 三车道并行填充
pub fn build_block(
    system_txs: Vec<SystemTx>,
    payment_pool: &PaymentLane,
    general_pool: &StandardPool,
    block_gas_limit: u64,
    shared_gas_limit: u64,
    general_gas_limit: u64, // 30M (固定, 参考 Tempo T1+)
) -> Block {
    let mut block = Block::new();
    let mut payment_gas_used = 0u64;
    let mut general_gas_used = 0u64;

    // Lane 1: System transactions (开头)
    for tx in system_txs {
        block.push_system(tx);
    }

    // Lane 2: Payment transactions
    while payment_gas_used < shared_gas_limit {
        if let Some(tx) = payment_pool.pop_best() {
            let result = execute_tx(&tx);
            payment_gas_used += result.gas_used;
            block.push_payment(tx, result);
        } else {
            break;
        }
    }

    // Lane 3: General transactions
    while general_gas_used < general_gas_limit {
        if let Some(tx) = general_pool.pop_best() {
            let result = execute_tx(&tx);
            general_gas_used += result.gas_used;
            block.push_general(tx, result);
        } else {
            break;
        }
    }

    block
}
```

### 6.2 交易排序策略

不同 Lane 使用不同的排序策略:

| Lane | 排序策略 | 理由 |
|------|---------|------|
| **System** | 固定顺序 (协议定义) | 系统交易有严格的执行顺序 |
| **Payment** | FIFO (先进先出) | 公平性: 支付交易不应按 gas 竞价排序; 防止抢先交易 |
| **Compliance Queue** | 优先级队列 (合规紧迫度) | 高优先级: 到期日临近的合规检查; 低优先级: 常规检查 |
| **Standard** | EIP-1559 有效小费排序 | 标准 gas 市场: max_priority_fee_per_gas 排序 |

#### 防 MEV 排序: xStocks 公平交易

对于 xStocks Zone, 额外实施公平排序机制:

```
xStocks Zone 交易排序:
1. 收集窗口: 每 T 毫秒 (如 100ms) 收集所有到达的交易
2. 确定性随机排列: 使用 VRF(sequencer_sk, window_id) 作为种子,
   对窗口内交易进行确定性伪随机排列 (Shuffle)
3. 批量执行: 排列后的交易按序执行

效果:
- 无法通过提前 1ms 提交来获得排序优势
- Sequencer 无法选择性排序 (排列算法是确定性的, 可被验证)
- 同一窗口内的交易被视为 "同时到达"
```

### 6.3 合规预检流程

合规待审队列 (Compliance Queue) 的交易需要通过预检后才能进入 Payment Lane 或 Standard Pool:

```
交易到达
   │
   ▼
┌──────────────────┐
│  基础验证          │  签名, nonce, gas limit, 格式
│  (毫秒级)         │
└────────┬─────────┘
         │ PASS
         ▼
┌──────────────────┐
│  身份检查          │  IdentityRegistry.isVerified(sender)
│  (毫秒级)         │  是否在 KYC 白名单中?
└────────┬─────────┘
         │ PASS
         ▼
┌──────────────────┐
│  合规策略评估      │  PolicyRegistry.isAuthorized(policyId, from, to, amount)
│  (~1-10ms)        │  制裁名单, 交易限额, 地理限制
└────────┬─────────┘
         │ PASS          │ PENDING (需异步检查)
         ▼               ▼
┌──────────────┐  ┌──────────────────┐
│  分类路由      │  │  Compliance Queue │
│  Payment/Std  │  │  等待异步合规结果   │
└──────────────┘  └──────────────────┘
```

**合规检查策略** (参考 Tempo TIP-403):

| 策略类型 | 检查方式 | 延迟 | 示例 |
|----------|---------|------|------|
| **always-allow** (Policy 1) | 跳过检查 | 0 | 公共 DeFi 交易 |
| **always-reject** (Policy 0) | 直接拒绝 | 0 | 被禁止的操作 |
| **whitelist** | 检查白名单 | <1ms | 机构级别准入 |
| **blacklist** | 检查黑名单 | <1ms | 制裁名单筛查 |
| **compound** (T2+) | 多策略组合: sender 规则 + recipient 规则 | 1-10ms | RWA 合规: 发送方 KYC Lv3 + 接收方合格投资人 |

---

## 7. 性能分析与优化策略

### 7.1 理论性能上限分析

基于选定技术栈 (Reth SDK + Simplex BFT), 分析各层级的理论性能上限:

#### 性能分解

```
端到端延迟 = 交易传播 + 交易池处理 + 合规检查 + 区块构建 + 区块执行 + BFT 共识 + 状态提交
          ≈ 20ms     +   5ms      +   5ms     +  100ms    +  200ms    +  200ms   +   70ms
          ≈ 600ms (与 Tempo ~600ms 终局延迟一致)
```

#### 各组件性能上限

| 组件 | 性能瓶颈 | 理论上限 | 优化方向 |
|------|---------|---------|---------|
| **Simplex BFT 共识** | 消息传播 + 签名验证 | ~200ms (7-15 验证者) | BLS 聚合签名减少验证数 |
| **EVM 执行 (revm)** | 串行状态读写 | ~2,000-3,000 TPS (串行) | 并行执行 (§7.2) |
| **MDBX 状态存储** | 磁盘 I/O | 2-3x LevelDB (Go geth 默认) | NVMe SSD + 内存缓存 |
| **网络传播** | 区块大小 × 验证者数 | ~50ms (同数据中心) | 压缩 + 增量传播 |
| **合规检查** | 策略评估复杂度 | <10ms (compound 策略) | 缓存 + 预计算 |

#### 性能目标与基准对比

| 指标 | 我们的目标 | Tempo L1 | Mantle | Ethereum L1 | Canton |
|------|-----------|---------|--------|-------------|--------|
| **主链 TPS** | 3,000-5,000 | 未公开基准; 30M general gas/block ÷ ~600ms | ~50-200 | ~15-30 | 未公开 ($2T+/月) |
| **Payment Zone TPS** | >10,000 | shared_gas_limit 可配 | N/A | N/A | N/A |
| **xStocks Zone TPS** | >5,000 | N/A | N/A | N/A | N/A |
| **BFT 终局** | ~600ms | ~600ms | 2s (soft), 7 天 (hard) | ~12 分钟 (finalized) | 秒级 (2PC) |
| **出块时间** | ~600ms (活跃); 5s (心跳) | ~600ms | 2s | 12s | 无区块 |
| **交易费** | <$0.001 | ~$0.001 | ~$0.01-0.10 | ~$1-50 | 无 gas |
| **L1 锚定** | 5-30 分钟 | N/A (独立 L1) | 7 天 (挑战期) | N/A | N/A |
| **硬终局改进** | 600ms vs Mantle 7 天 = **1,008,000x** | — | 基准 | — | — |

### 7.2 并行执行策略

串行 EVM 执行是吞吐量的核心瓶颈。设计三层并行执行策略:

#### Layer 1: Block-STM 乐观并行执行

参考 Aptos/Sei 的 Block-STM 算法:

```
Block-STM 执行流程:
1. 所有交易并行启动执行 (乐观假设无冲突)
2. 每个交易维护 read-set 和 write-set
3. 执行完成后, 验证 read-set 中的值是否被其他交易修改
4. 冲突检测:
   - 无冲突 → 提交
   - 有冲突 → 回滚 + 重新执行 (使用更新后的状态)
5. 重复直到所有交易提交

并行度 = min(CPU 核数, 独立交易数)
典型企业场景并行度: 4-8x (不同合规代币、不同 Zone 的交易互不冲突)
```

**预期 TPS 提升**: 4-8x (从 ~2,000 串行 → ~8,000-16,000 并行)

#### Layer 2: Zone 天然并行性

不同 Zone 的状态完全隔离, 可以真正并行执行:

```
主链区块 N:
├── 主链交易 (Block-STM 并行)
├── RWA Zone 区块 N (独立执行)     ──┐
├── xStocks Zone 区块 N (独立执行)  ──┼── 完全并行, 零冲突
├── Payment Zone 区块 N (独立执行)  ──┘
└── Custom Zone 区块 N (独立执行)
```

**Zone 间隔离保证**: Zone 使用独立的 `NoopConsensus` 和独立的 Reth 执行实例。Zone A 的 heavy DeFi 合约执行不会影响 Zone B 的交易处理延迟。

#### Layer 3: 预编译调用并行安全性

| 预编译 | 并行安全? | 理由 |
|--------|----------|------|
| **IdentityRegistry 读** | ✅ 安全 | 只读操作, 无状态修改 |
| **IdentityRegistry 写** | ⚠️ 需要锁 | 修改身份状态, 需串行化 |
| **PolicyRegistry 评估** | ✅ 安全 | 只读策略评估 |
| **CryptoSuite** | ✅ 安全 | 纯计算, 无状态 |
| **ComplianceToken 转账** | ⚠️ 需要余额锁 | 修改余额状态 (同地址转账需串行) |
| **TimeLock 检查** | ✅ 安全 | 只读时间检查 |
| **ThresholdSig 验证** | ✅ 安全 | 纯计算 |

**设计规则**: 所有预编译标注 `#[parallel_safe]` 或 `#[requires_lock(scope)]`, Block-STM 调度器据此决定是否可并行。

### 7.3 瓶颈分析与优化路径

#### 优化路径优先级

| 优先级 | 优化项 | 预期提升 | 复杂度 | 依赖 |
|--------|--------|---------|--------|------|
| **P0** | MDBX 存储后端 (Reth 默认) | 2-3x I/O vs LevelDB | 低 (已内置) | 无 |
| **P0** | 双 Tokio 运行时隔离 | 共识延迟稳定性 | 中 (参考 Tempo) | 架构级 |
| **P1** | Block-STM 并行执行 | 4-8x TPS | 高 | revm 修改 |
| **P1** | Payment Lane 隔离 | Payment 吞吐不受 DeFi 影响 | 中 (参考 Tempo) | 交易池改造 |
| **P2** | Zone 并行执行 | 线性扩展 (N Zones = Nx TPS) | 中 | Zone 架构 |
| **P2** | 状态裁剪 (Zone 分离) | 降低主链状态大小 | 中 | Zone 架构 |
| **P3** | GPU 加速 ZK 证明 | 10-100x 证明速度 | 高 | SP1 CUDA |
| **P3** | 增量状态传播 | 降低网络开销 | 中 | P2P 改造 |

#### 关键瓶颈: Payment Zone >10,000 TPS 可行性分析

WHI-355 要求 Payment 场景 >10,000 TPS。验证此目标的可行性:

```
Payment Zone TPS 分析:
- 每笔 Payment 交易 gas: ~50,000 (合规代币转账)
- 10,000 TPS 所需 gas/s: 50,000 × 10,000 = 500,000,000 gas/s
- 出块时间: ~600ms
- 每区块所需 gas: 500M × 0.6 = 300,000,000 gas/block

对比:
- Tempo shared_gas_limit: 可配置 (区块头字段)
- Ethereum gas limit: ~30M/block (12s) = ~2.5M gas/s
- 我们的 Payment Lane: 300M gas/block (600ms) = 500M gas/s

要求:
- shared_gas_limit ≥ 300,000,000 (300M) gas
- 单节点 EVM 执行: 50K gas/tx × 10K tx = 500M gas ÷ 600ms
  → 需要 ~833M gas/s 的执行吞吐
- revm 在现代硬件上: ~1B gas/s (简单转账, 参考 Reth benchmarks)
- ✅ 可行, 但需要优化的硬件 (NVMe SSD, 高频 CPU)

结论: Payment Zone >10,000 TPS 在技术上可行,
      但需要专用硬件 + Payment Lane gas 预算配置
```

---

## 8. 技术对比

### 与 Tempo / Canton / Prividium / Mantle 的全面对比

#### 执行层对比

| 维度 | 我们的设计 | Tempo L1 | Canton | Prividium | Mantle |
|------|-----------|---------|--------|-----------|--------|
| **执行引擎** | Reth SDK (revm v38+) | Reth SDK (revm v38+) | Daml-LF (非 EVM) | EVM (zkSync 系) | op-geth (Go) |
| **EVM 兼容** | 完全等价 + 扩展 | 完全等价 + 扩展 | ❌ 不兼容 | 兼容 (ZK 限制) | 完全等价 |
| **自定义预编译** | 12+ L1 + 7+ Zone | 12 L1 + 7 Zone | N/A (Daml) | 有 (未公开详情) | 4 组预编译 |
| **交易类型** | 4 标准 + 4 企业 | 4 标准 + 1 AA (0x76) | Daml command | 标准 EVM | 标准 OP Stack |
| **合规原生** | ✅ 交易类型级 (0x77) | ✅ TIP-403 策略级 | ✅ Daml 编译时授权 | ✅ 4 层访问控制 | ❌ 无 |
| **隐私原生** | ✅ Zone + ECIES | ✅ Zone + ECIES | ✅ Merkle DAG 投影 | ✅ Validium + RBAC | ❌ 全部公开 |
| **Gas 模型** | 多维度 (计算/存储/隐私/合规) | attodollar + Payment Lane | 无 gas (负载大小) | 未公开 | MNT 双代币 |
| **Payment Lane** | ✅ 三车道区块构建 | ✅ 三车道 (System/Payment/General) | ❌ 无 | ❌ 无 | ❌ 无 |
| **开发者生态** | Solidity/Vyper (数十万人) | Solidity/Vyper (有限) | Daml (数百人) | Solidity (受限) | Solidity (完整) |
| **`no_std` 纪律** | ✅ 所有预编译 | ✅ Zone 预编译 | N/A | 未知 | ❌ Go 不支持 |

#### 共识层对比

| 维度 | 我们的设计 | Tempo L1 | Canton | Prividium | Mantle |
|------|-----------|---------|--------|-----------|--------|
| **共识类型** | Simplex BFT | Simplex BFT | 2PC + BFT Sequencer | 单 Sequencer | 单 Sequencer (OP Stack) |
| **终局性** | ~600ms (BFT) | ~600ms (BFT) | 秒级 (2PC) | ~1s (链内) | 2s (soft), 7 天 (hard) |
| **容错** | f < n/3 | f < n/3 | 全部确认方 (2PC) | N/A | N/A |
| **MEV 防护** | VRF + Lane 隔离 + Zone 暗池 | VRF + Lane 隔离 | 架构级消除 (加密排序) | 运营商控制 | 无 (Sequencer 可提取) |
| **验证者模型** | 许可制 + 企业身份绑定 | DKG 门限签名 | 许可制 Synchronizer | 单运营商 | 单 Sequencer + HA |
| **去中心化** | 高 (7-50 验证者 BFT) | 高 (BFT 验证者集) | 中 (多 Synchronizer) | 低 (单运营商) | 低 (单 Sequencer) |
| **L1 安全锚定** | ✅ ZK + Ethereum | ❌ 独立 L1 | ❌ 可选锚定 | ✅ ZK + Ethereum | ✅ Optimistic + Ethereum |

#### 终局性模型对比

| 维度 | 我们的设计 | Tempo L1 | Canton | Prividium | Mantle |
|------|-----------|---------|--------|-----------|--------|
| **最快终局** | ~600ms (BFT) | ~600ms (BFT) | 秒级 (2PC) | ~1s (链内) | 2s (soft confirm) |
| **跨链终局** | 5-30 分钟 (ZK) | N/A (独立 L1) | N/A | 分钟级 (ZK) | 7 天 (挑战期) |
| **L1 锚定终局** | ~12+ 分钟 | N/A | N/A | ~12+ 分钟 | 7 天 |
| **可配置终局** | ✅ 按叙事选择层级 | ❌ 单一 BFT | ❌ 单一 2PC | 部分 (链内 vs L1) | ❌ 固定 7 天 |
| **终局性模型** | 三层渐进 (BFT → ZK → L1) | 单层 BFT | 单层 2PC | 两层 (链内 → L1) | 两层 (soft → hard) |
| **核心创新** | 叙事驱动可配置终局 | Payment Lane + BFT | 子交易隐私 | ZK 合规 | 预确认 |

#### 综合评估矩阵

| 评估维度 | 权重 | 我们的设计 | Tempo | Canton | Prividium | Mantle |
|----------|------|-----------|-------|--------|-----------|--------|
| **EVM 兼容性** | 25% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ (Daml) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **终局性** | 20% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **隐私能力** | 20% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **合规原生** | 15% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **吞吐量** | 10% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **安全模型** | 10% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**我们的核心差异化**: 唯一同时具备 (1) 完全 EVM 兼容 (2) 亚秒 BFT 终局 (3) Zone 隐私 (4) ZK + L1 锚定安全 (5) 叙事驱动可配置终局 的企业级方案。

- **vs Tempo**: 增加 ZK + L1 锚定 (Tempo 是独立 L1, 无 Ethereum 安全锚定); 增加可配置终局性层级
- **vs Canton**: 保持 EVM 兼容性 (Canton 的 Daml 开发者池只有数百人); 保持公链生态互操作
- **vs Prividium**: 增加 BFT 多验证者去中心化 (Prividium 是单 Sequencer); 增加 Payment Lane 高吞吐
- **vs Mantle**: 从 7 天终局降低到 600ms (1,008,000x 改进); 增加原生合规/隐私; 从 Go 单体到 Rust 模块化

---

## 附录 A: 关键设计约束追溯

| 约束 | 来源 | 影响 |
|------|------|------|
| "Optimistic Rollup 7 天挑战期完全不可接受" | WHI-355 §4.1 | → BFT 确定性终局 |
| "Payment 和 RWA 不能在同一执行环境共存" | WHI-355 §5.2 | → Zone 物理隔离 |
| "EVM 兼容性不可妥协" | WHI-357 设计原则 | → Reth SDK (非 Daml, 非自研) |
| "所有预编译必须 `no_std`" | WHI-357 设计约束 | → SP1/RISC-V ZK 就绪 |
| "企业级功能必须在协议层而非应用层" | WHI-357 设计原则 | → 预编译 + 交易类型 + 共识规则原生支持 |
| "Payment >10K TPS, <$0.001/tx" | WHI-355 §4.3 | → Payment Lane + Zone 并行 |
| "xstocks <100ms, T+0, anti-MEV" | WHI-355 §4.2 | → VRF + 公平排序 + Zone 暗池 |
| "RWA DVP 需原子结算 + 子交易隐私" | WHI-355 §4.1 | → Zone ECIES + 可配置终局性 |

## 附录 B: 术语表

| 术语 | 定义 |
|------|------|
| **Simplex BFT** | Commonware 实现的 BFT 共识协议, 使用 BLS12-381 门限签名 |
| **BLS12-381 DKG** | 分布式密钥生成 — 多方协作生成共享密钥, 用于门限签名 |
| **VRF** | 可验证随机函数 — 生成可验证但不可预测的随机数, 用于 Leader 选举 |
| **Payment Lane** | 专用于合规代币交易的区块空间车道, 有独立 gas 预算 |
| **Zone** | 私有执行环境 — 单 Sequencer 运行, 状态不公开, 通过 ECIES 加密通信 |
| **NoopConsensus** | Zone 使用的空共识 — 单 Sequencer 直接出块, 终局性继承自主链 |
| **DVP** | Delivery vs Payment — 证券和资金同时结算 |
| **T+0** | 交易日当天完成结算 (vs 传统金融的 T+2) |
| **Block-STM** | 乐观并行执行算法 — 交易并行执行, 冲突时回滚重试 |
| **STARK** | 可扩展透明知识论证 — 无需 trusted setup 的零知识证明系统 |
| **SP1** | Succinct 实验室的 zkVM — 将 Rust 程序编译为 RISC-V 并生成 STARK 证明 |
| **attodollar** | 10⁻¹⁸ USD — Tempo 的 gas 价格单位 |
| **TIP-403** | Tempo 的合规策略协议 — 定义转账授权检查接口 |
| **ECIES** | 椭圆曲线集成加密方案 — 用于 Zone 存款加密 |

---

> **文档版本**: v1.0
> **作者**: Claude (WHI-358 Session B Agent)
> **日期**: 2026-05-07
> **字数**: ~14,000 words
> **审阅状态**: Pending Review
