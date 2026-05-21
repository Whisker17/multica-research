# WHI-360: L1 路径 — 合规准入与身份管理原生框架设计

> **设计哲学**：合规不是阻碍，而是可编程的基础设施。合规即代码（Compliance as Code）。
>
> **前置依赖**：WHI-355 叙事需求分析 ✅ | WHI-357 架构蓝图 ✅
>
> **文档版本**：v1.0 | 2026-05-07

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [身份管理系统](#2-身份管理系统)
3. [准入控制系统](#3-准入控制系统)
4. [可编程合规框架](#4-可编程合规框架)
5. [M3 vs M4 深度对比](#5-m3-vs-m4-深度对比)
6. [身份互操作方案](#6-身份互操作方案)
7. [各叙事合规配置示例](#7-各叙事合规配置示例)
8. [与 Tempo/Canton/Prividium 合规方案对比](#8-与-tempocanton-prividium-合规方案对比)
9. [实施路线图](#9-实施路线图)

---

## 1. 执行摘要

### 1.1 设计定位

本文档定义一套**协议层原生**的合规准入与身份管理框架。与 M3 方案（在 ERC-20 合约内通过 transfer hook 实现合规检查）不同，本设计将合规和身份能力嵌入协议本身——合规检查发生在 EVM 执行之前（Pre-EVM），身份状态通过预编译合约（Precompile）暴露给所有协议组件，无法被任何合约层逻辑绕过。

### 1.2 核心原则

| 原则 | 含义 | 实现方式 |
|------|------|---------|
| **协议层原生** | 合规检查在 EVM 执行之前发生 | Sequencer 策略引擎 + 预编译合约 |
| **可编程性** | 合规策略可被机构/监管方自定义 | 策略注册表 DSL + 策略市场 |
| **非侵入性** | 对标准 DeFi 用户透明 | 仅需完成 KYC，无需理解合规细节 |
| **全球适配** | 支持不同司法管辖区要求 | 多层策略体系 + 管辖区路由 |
| **可审计** | 所有合规决策有审计追踪 | 专用审计 DA 通道 + Observer 角色 |
| **隐私兼容** | 合规检查不以牺牲隐私为代价 | ZK 合规证明 + 选择性披露 |

### 1.3 架构位置

合规框架在 WHI-357 分层架构中的位置：

```
┌─────────────────────────────────────────────────────┐
│  业务应用层 (DApps)                                   │
│  · RWA 发行平台 · xStocks 交易所 · Payment 钱包      │
├─────────────────────────────────────────────────────┤
│  ★ 业务组件层 — 合规与身份框架 ★                      │
│  · IdentityRegistry (0x0401)                         │
│  · ComplianceCheck  (0x0402)                         │
│  · PolicyRegistry   (0x0403)                         │
│  · SelectiveDisclosure (0x0405)                      │
├─────────────────────────────────────────────────────┤
│  隐私层 (Zone 隔离 + 加密存储)                        │
├─────────────────────────────────────────────────────┤
│  执行层 (Reth SDK + revm)                             │
├─────────────────────────────────────────────────────┤
│  共识层 + 数据可用性层                                │
└─────────────────────────────────────────────────────┘
```

合规框架位于隐私层之上、业务应用层之下。这是一个关键的架构决策：它确保了（a）所有应用必须经过合规组件，无法绕过；（b）合规组件能够感知隐私层的数据边界，实现合规与隐私的协调。

---

## 2. 身份管理系统

### 2.1 身份层级模型（5 层）

身份管理采用五层分层模型。每一层解决不同的关注点，从底层的密钥管理到顶层的业务角色，形成从密码学安全到业务语义的完整链路。

```
┌──────────────────────────────────────────────────────┐
│  Layer 4: 业务角色 (Business Roles)                    │
│  ┌────────────┬──────────┬──────────┬───────────┐    │
│  │ 合格投资者  │  做市商   │  发行方   │  托管方    │    │
│  │ Qualified   │ Market   │ Issuer   │ Custodian │    │
│  │ Investor    │ Maker    │          │           │    │
│  └────────────┴──────────┴──────────┴───────────┘    │
├──────────────────────────────────────────────────────┤
│  Layer 3: 合规属性 (Compliance Attributes)              │
│  ┌────────────┬──────────┬──────────┬───────────┐    │
│  │ KYC 等级    │ 合规认证  │ 制裁状态  │ 投资者类型 │    │
│  │ (0-4)      │ (bitmap) │ (clean/  │ (retail/  │    │
│  │            │          │  flagged)│  accred.) │    │
│  └────────────┴──────────┴──────────┴───────────┘    │
├──────────────────────────────────────────────────────┤
│  Layer 2: 可验证凭证 (Verifiable Credentials)           │
│  ┌────────────┬──────────┬──────────┬───────────┐    │
│  │ KYC VC     │ 认证投资者│ 居住地 VC │ 牌照 VC   │    │
│  │            │ VC       │          │           │    │
│  └────────────┴──────────┴──────────┴───────────┘    │
├──────────────────────────────────────────────────────┤
│  Layer 1: 链上身份锚点 (On-Chain Identity Anchor)       │
│  · 地址 ↔ DID 绑定                                    │
│  · 多地址聚合 (Multi-Address Aggregation)               │
│  · 身份恢复机制 (Recovery)                             │
├──────────────────────────────────────────────────────┤
│  Layer 0: 密钥管理 (Key Management)                    │
│  ┌────────────┬──────────┬──────────┬───────────┐    │
│  │ EOA        │ WebAuthn │ MPC      │ HSM       │    │
│  │ (secp256k1)│ (P-256)  │ (TSS)   │ (PKCS#11) │    │
│  └────────────┴──────────┴──────────┴───────────┘    │
└──────────────────────────────────────────────────────┘
```

#### Layer 0: 密钥管理

密钥管理层支持四种签名方案，参考 Tempo AccountKeychain 的多签名类型分发设计：

| 签名类型 | 算法 | 字节长度 | 目标用户 | 识别方式 |
|---------|------|---------|---------|---------|
| **EOA** | secp256k1 ECDSA | 65 bytes | 加密原生用户/开发者 | 固定长度 |
| **Passkey** | NIST P-256 | 130 bytes | 消费级用户 (Payment) | 固定长度 |
| **WebAuthn** | P-256 + RP assertion | 可变 (max 2KB) | 浏览器用户 (Face ID/指纹) | WebAuthn 帧结构 |
| **Delegated** | AccountKeychain 委托 | 可变 | 企业员工/交易员 | Keychain 标记 |

**关键设计决策**：P-256 和 WebAuthn 是协议级一等公民签名方案（参考 Tempo），不是通过合约层模拟。这意味着消费级用户可以使用 Face ID / 指纹 / YubiKey 直接签名链上交易，无需管理助记词或 secp256k1 私钥。

#### Layer 1: 链上身份锚点

链上身份锚点解决"地址与真实身份的绑定"问题：

**DID 绑定方案**：

```
did:whisker:<network-id>:<address>

示例：
did:whisker:mainnet:0x1234...abcd       # 主链地址
did:whisker:zone-rwa:0x5678...efgh       # RWA Zone 地址
```

- 采用 W3C DID 标准，自定义 `whisker` method
- DID Document 存储在链上（IdentityRegistry 预编译），包含：公钥列表、服务端点、认证方法、合规属性摘要
- 支持 DID Resolution：任何链上组件可通过地址解析到完整身份文档

**多地址聚合**：

```solidity
// IdentityRegistry 预编译接口 (0x0401)
interface IIdentityRegistry {
    // 地址 → 身份查询
    function resolveIdentity(address addr) external view returns (bytes32 identityId);
    
    // 身份 → 所有地址
    function getAddresses(bytes32 identityId) external view returns (address[] memory);
    
    // 绑定新地址（需要 root key 签名）
    function bindAddress(bytes32 identityId, address newAddr, bytes calldata rootSig) external;
    
    // 地址轮换（旧地址 → 新地址，保留身份）
    function rotateAddress(address oldAddr, address newAddr, bytes calldata rootSig) external;
}
```

**身份恢复机制**（三种恢复路径）：

| 恢复方式 | 机制 | 适用场景 | 安全等级 |
|---------|------|---------|---------|
| **社交恢复** | N-of-M 守护者投票 | 个人用户 | 中 |
| **机构恢复** | 认证方 (CA) 重新签发 | 企业用户 | 高 |
| **时间锁恢复** | 48h 延迟 + 新密钥提交 | 紧急情况 | 低（有时间窗口风险） |

#### Layer 2: 可验证凭证 (Verifiable Credentials)

链下签发、链上验证的可验证凭证系统：

**VC 类型定义**：

| VC 类型 | 签发方 | 内容 | 有效期 | Zone 准入关联 |
|---------|-------|------|-------|------------|
| **KYC VC** | 银行/合规服务商 | 姓名哈希 + 国籍代码 + KYC 等级 | 1 年 | Level 1+ |
| **认证投资者 VC** | 持牌认证方 | 净资产范围 + 投资经验等级 | 1 年 | Level 3 (xStocks) |
| **居住地 VC** | 政府/公用事业 | 管辖区代码 + 证明类型 | 6 个月 | 跨管辖区策略路由 |
| **机构 VC (KYB)** | 监管机构/注册处 | 法人实体 ID (LEI) + 牌照类型 | 持续 | Level 4 |
| **VASP VC** | 金融监管机构 | VASP 注册号 + 注册辖区 | 持续 | Payment Zone 运营 |
| **牌照 VC** | 证券监管机构 | 牌照类型 + 编号 + 有效期 | 按牌照周期 | xStocks Zone 运营 |

**链上存储模型（隐私优先）**：

链上**不**存储 VC 明文。存储的是属性承诺 (commitment)：

```
OnChainIdentityRecord {
    identityId:       bytes32,          // 身份唯一标识
    kycLevel:         uint8,            // KYC 等级 (0-4)，明文（需要高频查询）
    sanctionStatus:   uint8,            // 0=clean, 1=flagged, 2=blocked
    attributeRoot:    bytes32,          // 所有 VC 属性的 Merkle root
    vcHashes:         bytes32[],        // 各 VC 的哈希列表
    issuers:          address[],        // 签发方地址列表
    expirations:      uint64[],         // 各 VC 的过期时间
    lastUpdated:      uint64            // 最后更新区块号
}
```

**ZK 验证流程**：

```
场景：用户证明自己是合格投资者，但不暴露身份

1. 用户持有 "认证投资者 VC"（链下）
2. 用户生成 ZK 证明：
   proof = ZK_PROVE(
     private: [vc_content, vc_signature, identity_data],
     public:  [attributeRoot, "accredited_investor=true"]
   )
3. 链上验证：
   SelectiveDisclosure.verify(proof, attributeRoot, "accredited_investor=true")
   → returns bool
4. 策略引擎使用验证结果做准入决策
```

#### Layer 3: 合规属性

合规属性是从 Layer 2 VC 中提取的、供策略引擎直接查询的结构化数据：

```solidity
// 合规属性位图编码
struct ComplianceAttributes {
    uint8   kycLevel;          // 0=none, 1=basic, 2=enhanced, 3=qualified, 4=institutional
    uint8   sanctionStatus;    // 0=clean, 1=pending_review, 2=flagged, 3=blocked
    uint16  jurisdictionCode;  // ISO 3166-1 数字代码
    uint32  certifications;    // 位图: bit0=accredited, bit1=qualified_purchaser,
                               //       bit2=vasp_registered, bit3=broker_licensed, ...
    uint8   investorType;      // 0=retail, 1=accredited, 2=qualified_purchaser,
                               //       3=institutional, 4=sovereign
    uint64  kycExpiration;     // KYC 过期时间戳
    uint64  lastSanctionCheck; // 最后制裁筛查时间
}
```

**属性更新流程**：

```
CA 签发/更新 VC
  → 用户/CA 提交属性更新交易（tx type 0x77: Compliance Transaction）
  → IdentityRegistry 预编译更新链上记录
  → PolicyRegistry 缓存自动失效 + 重新评估
  → 所有 Zone 在下一个区块自动同步更新
```

#### Layer 4: 业务角色

业务角色是对 Layer 3 属性的高级抽象，直接对应业务准入需求：

| 角色 | 属性要求 | 业务权限 |
|------|---------|---------|
| **合格投资者** | kycLevel ≥ 3 + accredited cert + 非制裁 | 参与 RWA/xStocks 投资 |
| **做市商** | kycLevel = 4 + broker_licensed + 资本金证明 | 提供流动性 + 获取做市优惠 |
| **发行方** | kycLevel = 4 + issuer_licensed + KYB | 发行新资产 + 管理资产合规 |
| **托管方** | kycLevel = 4 + custodian_licensed + SOC2 | 托管资产 + 执行结算 |
| **Zone 运营者** | kycLevel = 4 + KYB + 基础设施认证 | 运营 Zone Sequencer |
| **监管方** | 政府/监管机构证书 | Observer 权限 + 审计接入 |

### 2.2 链上身份注册表 (Identity Registry)

#### 预编译接口设计 — `0x0401`

**地址**：`0x0401`
**Gas 成本**：2,000 gas（查询），50,000 gas（注册/更新）
**参考**：Tempo AccountKeychain + Prividium SSO

```solidity
interface IIdentityRegistry {
    // === 查询接口 (2,000 gas) ===
    
    /// @notice 检查地址是否已完成 KYC 验证
    function isVerified(address addr) external view returns (bool);
    
    /// @notice 获取地址的 KYC 等级
    function getKYCLevel(address addr) external view returns (uint8);
    
    /// @notice 获取特定类型的资质认证状态
    /// @param qualType 资质类型（0=accredited, 1=qualified_purchaser, 2=vasp, 3=broker ...）
    function getQualification(address addr, uint8 qualType) external view returns (bool valid, uint64 expiry);
    
    /// @notice 获取完整合规属性
    function getComplianceAttributes(address addr) external view returns (ComplianceAttributes memory);
    
    /// @notice 获取身份绑定的所有地址
    function getLinkedAddresses(address addr) external view returns (address[] memory);
    
    /// @notice 获取制裁筛查状态
    function getSanctionStatus(address addr) external view returns (uint8 status, uint64 lastCheck);
    
    // === 注册/更新接口 (50,000 gas) ===
    
    /// @notice 注册新身份（需要 CA 签名）
    function registerIdentity(
        address addr,
        bytes32 identityId,
        ComplianceAttributes calldata attrs,
        bytes32 attributeRoot,        // VC 属性 Merkle root
        address issuer,               // 签发 CA 地址
        bytes calldata issuerSig       // CA 签名
    ) external;
    
    /// @notice 更新合规属性（需要 CA 或 root key 签名）
    function updateAttributes(
        bytes32 identityId,
        ComplianceAttributes calldata newAttrs,
        bytes32 newAttributeRoot,
        bytes calldata authSig
    ) external;
    
    /// @notice 绑定新地址到已有身份
    function bindAddress(bytes32 identityId, address newAddr, bytes calldata rootSig) external;
    
    /// @notice 地址轮换
    function rotateAddress(address oldAddr, address newAddr, bytes calldata rootSig) external;
    
    // === 事件 ===
    event IdentityRegistered(bytes32 indexed identityId, address indexed addr, address indexed issuer);
    event AttributesUpdated(bytes32 indexed identityId, uint8 newKYCLevel);
    event AddressBound(bytes32 indexed identityId, address indexed newAddr);
    event SanctionStatusChanged(address indexed addr, uint8 oldStatus, uint8 newStatus);
    event KYCExpired(bytes32 indexed identityId, address indexed addr);
}
```

#### 注册流程

```
┌─────────┐     ┌──────────┐     ┌──────────────┐     ┌──────────────────┐
│  用户    │     │  CA      │     │  链上         │     │  Zone (L2)       │
│ (KYC    │     │ (银行/   │     │  Identity     │     │  Auto-Sync       │
│  申请方) │     │  合规商)  │     │  Registry     │     │                  │
└────┬────┘     └────┬─────┘     └──────┬───────┘     └────────┬─────────┘
     │               │                   │                      │
     │  1. 提交 KYC  │                   │                      │
     │  材料         │                   │                      │
     │──────────────>│                   │                      │
     │               │                   │                      │
     │  2. KYC 审核  │                   │                      │
     │  (链下)       │                   │                      │
     │               │                   │                      │
     │  3. 签发 VC   │                   │                      │
     │<──────────────│                   │                      │
     │               │                   │                      │
     │  4. 提交注册交易 (tx type 0x77)    │                      │
     │  [VC 哈希 + 属性摘要 + CA 签名]    │                      │
     │───────────────────────────────────>│                      │
     │               │                   │                      │
     │               │  5. 验证 CA 签名   │                      │
     │               │  + 存储身份记录    │                      │
     │               │                   │                      │
     │               │                   │  6. 下一区块自动     │
     │               │                   │  同步到所有 Zone      │
     │               │                   │─────────────────────>│
     │               │                   │                      │
     │  7. 身份激活，可以访问授权 Zone      │                      │
     │<──────────────────────────────────────────────────────────│
```

#### 隐私保护机制

**链上仅存储最小必要信息**：

| 链上存储 | 链下存储 | 理由 |
|---------|---------|------|
| KYC 等级 (uint8) | 姓名、地址、身份证号 | KYC 等级是高频查询的合规属性 |
| 制裁状态 (uint8) | 制裁匹配详情 | 制裁检查需要实时可用 |
| 管辖区代码 (uint16) | 详细住址 | 跨管辖区策略路由需要 |
| 认证位图 (uint32) | 认证文件原件 | 策略匹配需要快速位运算 |
| VC 属性 Merkle root | VC 完整内容 | ZK 证明的锚点 |
| VC 过期时间 | VC 签发详情 | 自动过期检测 |

**ZK 选择性披露**（通过 SelectiveDisclosure 预编译 `0x0405`）：

```
场景1：RWA Zone 准入 — 证明"我是合格投资者"
  proof = ZK_PROVE(private: [vc, identity], public: [root, "accredited=true"])
  → 验证方获知：此地址是合格投资者
  → 验证方不知：姓名、净资产具体数额、身份证号

场景2：Travel Rule — 证明"我的身份信息已提交给 VASP"  
  proof = ZK_PROVE(private: [originator_info, beneficiary_info], 
                   public: [vasp_commitment, transfer_hash])
  → 链上记录：Travel Rule 已满足
  → 链上不记录：具体的发送方/接收方 PII

场景3：制裁筛查 — 证明"我不在 OFAC SDN 名单上"
  proof = ZK_PROVE(private: [identity_data, ofac_list_merkle_proof],
                   public: [ofac_list_root, "not_on_list=true"])
  → 合规确认：此地址通过制裁筛查
  → 无 PII 泄露
```

#### 多地址管理

参考 Tempo AccountKeychain 的 root key / access key 委托模型：

```
Identity (身份)
├── Root Key (根密钥) — 最高权限，用于身份管理操作
│   └── secp256k1 或 P-256
│
├── Address 1 (主操作地址)
│   ├── Zone: RWA
│   └── 权限: 全部
│
├── Address 2 (xStocks 交易地址)
│   ├── Zone: xStocks
│   └── 权限: 交易 + 查询
│
├── Address 3 (Payment 地址)
│   ├── Zone: Payment
│   └── 权限: 转账 + 查询
│
└── Delegated Access Key (委托密钥)
    ├── Scope: [指定合约地址 + 函数选择器]
    ├── TokenLimit: 每日 10,000 USDC
    ├── ExpiresAt: 2026-06-07T00:00:00Z
    └── 使用场景: 企业交易员日常操作
```

**机构多地址聚合**：

一个机构（如某基金公司）可能拥有多个操作地址（交易部、结算部、资管部），这些地址全部聚合到同一个 KYB 身份下：

```solidity
// 机构多地址查询示例
bytes32 fundIdentity = registry.resolveIdentity(tradingDeskAddr);
address[] memory allAddrs = registry.getLinkedAddresses(fundIdentity);
// allAddrs = [tradingDeskAddr, settlementAddr, assetMgmtAddr]
// 所有地址共享同一套合规属性和业务角色
```

### 2.3 认证方 (Certificate Authority) 模型

#### 去中心化 CA 体系

本协议采用**联盟式 CA 模型**——多个认证方共存，而非单一中心化 CA。

```
┌────────────────────────────────────────────────────┐
│              CA Registry (链上注册表)                 │
├────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ 银行 CA   │  │ 合规服务  │  │ 政府/监管机构 CA  │  │
│  │          │  │ 商 CA    │  │                  │  │
│  │ · 渣打银行│  │ · Chainalysis│ · 新加坡 MAS   │  │
│  │ · 汇丰   │  │ · Elliptic   │ · SEC          │  │
│  │ · 星展   │  │ · Jumio      │ · BaFin        │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                                     │
│  每个 CA 的链上记录:                                  │
│  · CA 地址 (公钥)                                    │
│  · 认证范围 (可签发哪些 VC 类型)                      │
│  · 可信等级 (Tier 1/2/3)                             │
│  · 管辖区 (哪些地区的 KYC 有效)                       │
│  · 信誉分数 (基于历史行为)                            │
│  · 状态 (active / suspended / revoked)               │
└────────────────────────────────────────────────────┘
```

**CA 分级制度**：

| CA 等级 | 资质要求 | 可签发 VC | 签发上限 | 示例 |
|---------|---------|----------|---------|------|
| **Tier 1** | 持牌金融机构 + 监管审批 | 所有类型 | 无限制 | 汇丰银行、星展银行 |
| **Tier 2** | 合规服务商 + 行业认证 | KYC VC、居住地 VC | 年度配额 | Chainalysis, Jumio |
| **Tier 3** | 通过审核的新进入者 | 基础 KYC VC | 月度配额 + 抽检 | 新兴合规科技公司 |

**CA 间互认机制**：

```
场景：用户在 CA-A（渣打银行）完成 KYC，想在 CA-B（汇丰银行）运营的 RWA Zone 交易

1. CA-A 签发的 KYC VC 包含: [identity_hash, kyc_level=2, jurisdiction=SG, issuer=CA-A]
2. CA-B 的 Zone 策略配置:
   acceptedIssuers: [CA-A, CA-B, CA-C]   // 接受这些 CA 签发的 VC
   minKYCLevel: 2                          // 最低 KYC 等级
   acceptedJurisdictions: [SG, US, EU]     // 接受这些管辖区的 KYC

3. 策略引擎评估:
   ✅ issuer=CA-A ∈ acceptedIssuers
   ✅ kycLevel=2 ≥ minKYCLevel
   ✅ jurisdiction=SG ∈ acceptedJurisdictions
   → 准入通过
```

**CA 治理与惩罚**：

| 事件 | 处理 | 执行方式 |
|------|------|---------|
| CA 签发虚假 VC | 立即暂停 + 调查 | 治理多签 |
| CA 泄露用户数据 | 降级 + 罚金 + 受影响 VC 需要重新签发 | 治理投票 |
| CA 密钥泄露 | 立即吊销 + 所有已签发 VC 失效 | 紧急多签 (2-of-3) |
| CA 未能及时更新制裁名单 | 警告 → 暂停 → 吊销 | 自动监控 + 治理 |

### 2.4 WebAuthn / Passkey 集成

面向消费级用户（特别是 Payment 叙事场景），提供无助记词的身份体验。

#### 架构设计

```
┌──────────────────────────────────────────────────┐
│  用户设备                                         │
│  ┌──────────────┐                                │
│  │ Passkey 密钥  │ ← Face ID / 指纹 / YubiKey    │
│  │ (P-256)      │                                │
│  └──────┬───────┘                                │
│         │ WebAuthn Assertion                      │
└─────────┼────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────┐
│  交易类型 0x76 (Tempo 式 AA 交易)                  │
│                                                   │
│  签名字段:                                        │
│  · 130 bytes → P-256 直接验证                     │
│  · WebAuthn framing → 完整 WebAuthn 验证          │
│  · 65 bytes → 标准 secp256k1 回退                 │
│                                                   │
│  执行流程:                                        │
│  1. 签名类型检测（按字节长度）                      │
│  2. AccountKeychain 预编译验证签名                  │
│  3. 身份解析 → IdentityRegistry                    │
│  4. 合规检查 → ComplianceCheck                     │
│  5. EVM 执行                                      │
└──────────────────────────────────────────────────┘
```

#### ERC-4337 账户抽象集成

```solidity
// Smart Account with WebAuthn + Compliance
contract WhiskerSmartAccount is IAccount {
    bytes32 public immutable identityId;     // 关联的身份 ID
    address public immutable identityRegistry; // 0x0401
    
    function validateUserOp(UserOperation calldata userOp, bytes32 userOpHash, uint256 missingAccountFunds)
        external returns (uint256 validationData) 
    {
        // 1. 验证签名（P-256 或 WebAuthn）
        bool sigValid = AccountKeychain.verify(userOp.signature, userOpHash);
        
        // 2. 合规预检查
        bool compliant = ComplianceCheck.checkTransaction(
            address(this), 
            userOp.callData
        );
        
        if (!sigValid || !compliant) return SIG_VALIDATION_FAILED;
        
        // 3. 支付 gas
        if (missingAccountFunds > 0) {
            payable(msg.sender).call{value: missingAccountFunds}("");
        }
        
        return 0;
    }
}
```

#### 恢复机制设计

| 恢复场景 | 方式 | 流程 | 时间窗口 |
|---------|------|------|---------|
| **设备丢失** | Passkey 跨设备同步 | iCloud Keychain / Google Password Manager 自动恢复 | 即时 |
| **单设备用户** | 社交恢复 | 3-of-5 守护者确认 → 新 Passkey 绑定 | 24-48h |
| **企业用户** | 机构恢复 | 企业 IT Admin → CA 重新签发 → 新密钥绑定 | 1-4h (SLA) |
| **高净值用户** | HSM + 纸质备份 | 物理 HSM 取回 + KYC 重新验证 | 即时（如 HSM 可用） |

---

## 3. 准入控制系统

### 3.1 协议层策略注册表 (Policy Registry)

#### 预编译接口设计 — `0x0403`

**地址**：`0x0403`
**Gas 成本**：3,000 gas（查询），100,000 gas（注册/更新策略）
**参考**：Tempo TIP-403 + TIP-1015 compound policies

```solidity
interface IPolicyRegistry {
    // === 策略类型枚举 ===
    enum PolicyType {
        ALWAYS_REJECT,       // 0: 完全拒绝
        ALWAYS_ALLOW,        // 1: 完全允许
        WHITELIST,           // 2: 仅允许列表内地址
        BLACKLIST,           // 3: 拒绝列表内地址
        ATTRIBUTE_CHECK,     // 4: 基于合规属性检查
        COMPOUND,            // 5: 复合策略（sender + recipient 分别评估）
        CUSTOM_DSL           // 6: 自定义 DSL 策略
    }
    
    // === 策略层级 ===
    enum PolicyScope {
        GLOBAL,              // 全局策略（所有交易）
        ZONE,                // Zone 级策略
        ASSET,               // 资产级策略
        CUSTOM               // 自定义策略
    }
    
    // === 核心查询接口 (3,000 gas) ===
    
    /// @notice 综合授权检查 — 策略执行引擎的入口
    function isAuthorized(
        address from,
        address to, 
        uint256 amount,
        bytes calldata context   // 编码: [assetAddress, zoneId, txType, ...]
    ) external view returns (bool authorized, bytes32 reasonCode);
    
    /// @notice 查询特定策略
    function getPolicy(bytes32 policyId) external view returns (Policy memory);
    
    /// @notice 查询地址在特定策略下的授权状态
    function checkPolicy(bytes32 policyId, address user) external view returns (bool);
    
    // === 策略管理接口 (100,000 gas) ===
    
    /// @notice 注册新策略（需要策略管理员权限）
    function registerPolicy(
        PolicyScope scope,
        PolicyType pType,
        bytes calldata policyData,
        address admin
    ) external returns (bytes32 policyId);
    
    /// @notice 更新策略白名单/黑名单
    function updatePolicyList(
        bytes32 policyId,
        address[] calldata addAddresses,
        address[] calldata removeAddresses,
        bytes calldata adminSig
    ) external;
    
    // === 事件 ===
    event PolicyRegistered(bytes32 indexed policyId, PolicyScope scope, PolicyType pType);
    event PolicyUpdated(bytes32 indexed policyId, address indexed admin);
    event AuthorizationChecked(address indexed from, address indexed to, bool authorized, bytes32 reasonCode);
}
```

#### 四级策略层次

```
┌──────────────────────────────────────────────────────────────┐
│                     策略评估优先级（高 → 低）                   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Level 1: 全局策略 (Global Policies)                  │    │
│  │  · 制裁名单检查 — 所有交易必须通过                      │    │
│  │  · 最低 KYC 等级 — kycLevel ≥ 1（全链硬性要求）        │    │
│  │  · 全局暂停开关 — 紧急情况下暂停所有交易                │    │
│  │                                                       │    │
│  │  特性: 优先级最高，任何全局策略拒绝则交易直接失败        │    │
│  └──────────────────────────────────────────────────────┘    │
│                           │                                   │
│                           ▼                                   │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Level 2: Zone 策略 (Zone Policies)                   │    │
│  │                                                       │    │
│  │  RWA Zone:                                            │    │
│  │  · 合格投资者认证 (kycLevel ≥ 3 + accredited cert)     │    │
│  │  · Reg D/S 地域限制（美国发行 → 仅 Reg D 合格投资者）   │    │
│  │  · 反洗钱增强检查 (Enhanced Due Diligence)             │    │
│  │                                                       │    │
│  │  xStocks Zone:                                        │    │
│  │  · 券商/交易商牌照 (broker_licensed)                   │    │
│  │  · 投资者适当性 (suitability check per asset)          │    │
│  │  · Reg NMS 价格保护规则                                │    │
│  │                                                       │    │
│  │  Payment Zone:                                        │    │
│  │  · VASP 注册 (vasp_registered for operators)          │    │
│  │  · Travel Rule (转账 ≥ $3,000)                        │    │
│  │  · 基础 KYC (kycLevel ≥ 1)                            │    │
│  └──────────────────────────────────────────────────────┘    │
│                           │                                   │
│                           ▼                                   │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Level 3: 资产策略 (Asset Policies)                   │    │
│  │                                                       │    │
│  │  Per-Token 配置:                                      │    │
│  │  · 转账白名单/黑名单                                   │    │
│  │  · 每日转账限额 (dailyLimit)                           │    │
│  │  · 锁定期 (lockupPeriod) — Reg D 12个月锁定           │    │
│  │  · 最大持有人数 (maxHolders) — Reg D 506(b) 35人限制   │    │
│  │  · 投资者适当性要求 (per-asset suitability)            │    │
│  │                                                       │    │
│  │  Compound 策略 (TIP-1015):                            │    │
│  │  · Sender Policy: 发送方必须满足的条件                  │    │
│  │  · Recipient Policy: 接收方必须满足的条件               │    │
│  │  → 支持 DvP 场景中买卖双方不同的合规要求               │    │
│  └──────────────────────────────────────────────────────┘    │
│                           │                                   │
│                           ▼                                   │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Level 4: 自定义策略 (Custom Policies)                │    │
│  │                                                       │    │
│  │  机构内部规则:                                         │    │
│  │  · 内部风控限额                                        │    │
│  │  · 交易对手白名单                                      │    │
│  │  · 部门间隔离墙                                        │    │
│  │                                                       │    │
│  │  区域法规:                                             │    │
│  │  · GDPR 数据处理限制 (EU 用户)                         │    │
│  │  · MiCA 资产分类规则 (EU 资产)                         │    │
│  │  · SEC 特定规则 (US 证券)                              │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

#### 策略同步机制（L1 → Zone）

参考 Tempo 的 `ZoneTip403ProxyRegistry` + `SharedPolicyCache` 设计：

```
┌──────────────┐          ┌──────────────────┐          ┌──────────────┐
│  MainChain   │          │  Policy Sync     │          │  Zone (L2)   │
│  PolicyReg   │          │  Mechanism       │          │  PolicyCache │
│  (0x0403)    │          │                  │          │              │
└──────┬───────┘          └────────┬─────────┘          └──────┬───────┘
       │                           │                           │
       │  1. 策略更新事件           │                           │
       │  PolicyUpdated(id, ...)   │                           │
       │──────────────────────────>│                           │
       │                           │                           │
       │                           │  2. Zone Sequencer 观察   │
       │                           │  mainchain 事件           │
       │                           │                           │
       │                           │  3. 通过 StateReader      │
       │                           │  预编译读取最新策略        │
       │                           │                           │
       │                           │  4. 更新 Zone 本地缓存    │
       │                           │──────────────────────────>│
       │                           │                           │
       │                           │  5. Per-Block GC:         │
       │                           │  cache.advance(l1_block)  │
       │                           │  确保策略版本一致          │
       │                           │──────────────────────────>│
```

**缓存一致性保证**（参考 Tempo SharedPolicyCache per-block GC）：

- Zone Sequencer 在构建每个 Zone 区块时，调用 `cache.advance(l1_block_number)` 推进策略缓存
- 确保同一 Zone 区块内的所有交易使用同一版本的策略快照
- L1Subscriber 不能比 Engine 更快地推进缓存（防止竞态条件）
- 策略更新的传播延迟 = 1 个 L1 区块确认时间（~12s）

### 3.2 策略执行引擎 (Policy Execution Engine)

#### 预编译接口设计 — `0x0402`

**地址**：`0x0402`
**Gas 成本**：5,000 gas
**功能**：交易级合规验证门控

```solidity
interface IComplianceCheck {
    /// @notice 交易合规检查 — 评估交易是否满足所有适用策略
    /// @param from 发送方地址
    /// @param to 接收方地址
    /// @param value 交易金额
    /// @param data 交易调用数据
    /// @param context 附加上下文 [zoneId, assetAddr, txType]
    /// @return result 检查结果 (0=pass, 1=reject, 2=pending_review)
    /// @return reasonCode 原因码 (用于审计)
    /// @return failedPolicies 未通过的策略 ID 列表
    function checkTransaction(
        address from,
        address to,
        uint256 value,
        bytes calldata data,
        bytes calldata context
    ) external view returns (
        uint8 result,
        bytes32 reasonCode,
        bytes32[] memory failedPolicies
    );
    
    /// @notice 批量合规检查（优化批量交易场景）
    function batchCheck(
        TransactionInfo[] calldata txns
    ) external view returns (CheckResult[] memory);
}
```

#### 五层纵深防御执行流程

参考 WHI-357 的"五层纵深防御"设计，在 Prividium 四层模型基础上增加预编译层：

```
                    交易提交
                       │
                       ▼
        ┌──────────────────────────────┐
        │  Layer 1: IAM 层              │
        │  · 企业 SSO / OIDC 令牌验证    │
        │  · JWT 签名检查 + 过期检查     │
        │  · 用户 → 钱包地址映射         │
        │                               │
        │  参考: Prividium Okta SSO      │
        └──────────────┬───────────────┘
                       │ ✅ 身份已认证
                       ▼
        ┌──────────────────────────────┐
        │  Layer 2: 认证 RPC 层         │
        │  · 签名访问令牌验证            │
        │  · Zone 授权范围检查           │
        │  · Per-Account 数据过滤        │
        │  · 三步验证:                   │
        │    1. JWT 有效性              │
        │    2. 钱包地址匹配             │
        │    3. 目标合约+函数 RBAC       │
        │                               │
        │  参考: Prividium Proxy RPC     │
        │        Tempo Zone Auth Token  │
        └──────────────┬───────────────┘
                       │ ✅ 访问已授权
                       ▼
        ┌──────────────────────────────┐
        │  Layer 3: Sequencer 策略层    │
        │  · 交易池预过滤:               │
        │    prepare_l1_block() 中执行  │
        │  · TIP-403 策略评估            │
        │  · 非合规交易: 弹回退款         │
        │    (不是 revert，是 graceful   │
        │     bounce-back)              │
        │  · 加密存款解密后检查           │
        │                               │
        │  参考: Tempo prepare_l1_block  │
        │        Sequencer-as-          │
        │        Compliance-Officer     │
        └──────────────┬───────────────┘
                       │ ✅ 策略已通过
                       ▼
        ┌──────────────────────────────┐
        │  Layer 4: 预编译合规层        │
        │  · EVM 执行中强制检查:         │
        │    每笔 TIP-20 transfer()    │
        │    自动调用 isAuthorized()    │
        │  · delegatecall 阻断          │
        │    (DelegateCallNotAllowed)   │
        │  · 无法被合约层逻辑绕过        │
        │                               │
        │  参考: Tempo TIP-403 预编译    │
        └──────────────┬───────────────┘
                       │ ✅ 合规已验证
                       ▼
        ┌──────────────────────────────┐
        │  Layer 5: L1 桥接过滤层       │
        │  · 跨链存取款合规门控          │
        │  · L1 桥接合约白名单           │
        │  · 非白名单地址仅限 ETH/ERC-20│
        │  · Multicall 显式阻断          │
        │                               │
        │  参考: Prividium              │
        │        TransactionFilterer    │
        └──────────────┬───────────────┘
                       │ ✅ 全部通过
                       ▼
                   EVM 执行
                       │
                       ▼
              合规事件记录到审计通道
```

**关键设计决策——为什么需要五层而不是一层**：

| 单层方案 | 风险 | 五层方案如何解决 |
|---------|------|----------------|
| 仅 RPC 层 | Sequencer 直连可绕过 | Layer 3+4 兜底 |
| 仅 Sequencer 层 | 恶意 Sequencer 可跳过检查 | Layer 4 预编译不可绕过 |
| 仅预编译层 | 不合规交易仍会进入交易池消耗资源 | Layer 2+3 提前过滤 |
| 仅 L1 桥接层 | Zone 内部交易不受保护 | Layer 3+4 覆盖内部交易 |

#### 策略语言设计

本协议采用**自定义 DSL + Solidity 预编译后端**的混合方案：

**策略 DSL 设计**：

```yaml
# 示例: RWA Zone 策略定义
policy:
  id: "rwa-zone-qualified-investor"
  scope: ZONE
  zone: "rwa"
  version: 1
  
  rules:
    # 规则 1: 投资者资质
    - name: "investor-qualification"
      condition:
        all:
          - identity.kycLevel >= 3
          - identity.certifications.accredited == true
          - identity.sanctionStatus == "clean"
          - identity.kycExpiration > block.timestamp
      action: ALLOW
      
    # 规则 2: 地域限制 (Reg D)
    - name: "reg-d-geo-restriction"
      condition:
        any:
          - identity.jurisdictionCode == 840    # US: 需要 Reg D 合规
          - identity.certifications.reg_s_eligible == true  # 非 US: Reg S 豁免
      action: ALLOW
      
    # 规则 3: 锁定期
    - name: "lockup-period"
      condition:
        all:
          - asset.lockupEnd <= block.timestamp
          - OR:
            - transfer.recipient.certifications.accredited == true
            - transfer.amount == 0   # 允许查询
      action: ALLOW
      
  default_action: REJECT
  reason_code: "RWA_ZONE_POLICY_VIOLATION"
```

**DSL → 预编译编译流程**：

```
策略 DSL (YAML/JSON)
   │
   ▼
策略编译器 (off-chain)
   │  · 语法检查
   │  · 形式化验证（确保不会误阻合法交易）
   │  · 优化（条件短路、缓存提示）
   │
   ▼
策略字节码 (bytes)
   │
   ▼
PolicyRegistry.registerPolicy(scope, type, bytecode, admin)
   │
   ▼
链上存储 + 自动同步到所有 Zone
```

**形式化验证**（确保策略安全性）：

策略在注册前必须通过以下验证：
1. **可达性检查**：策略不能意外阻止所有交易（至少存在一个满足条件的路径）
2. **冲突检测**：新策略不能与现有策略产生逻辑冲突
3. **终止性保证**：策略评估必须在有限步数内完成
4. **边界条件**：KYC 过期、制裁状态变更等边界条件有明确处理

#### 性能优化

合规检查增加的延迟必须控制在可接受范围内：

| 优化策略 | 机制 | 延迟影响 |
|---------|------|---------|
| **身份属性缓存** | IdentityRegistry 查询结果缓存在 Sequencer 内存中，按区块失效 | 首次查询 ~2ms，缓存命中 ~0.1ms |
| **策略结果缓存** | (from, to, asset) → 合规结果缓存，TTL = 1 区块 | 重复交易对 ~0.05ms |
| **批量评估** | 同一区块内的交易批量通过策略引擎 | 减少 ~40% 重复身份查询 |
| **短路评估** | 全局策略先评估，失败则跳过后续层级 | 制裁命中时 ~0.5ms 即返回 |
| **异步预检** | 交易进入 mempool 时即开始异步合规预检 | 区块构建时直接使用预检结果 |

**延迟预算**：

| 交易类型 | 无合规检查 | 有合规检查 | 增加延迟 | 可接受性 |
|---------|----------|----------|---------|---------|
| 简单转账 | ~3ms | ~5ms | +2ms | ✅ |
| DeFi 交换 | ~8ms | ~12ms | +4ms | ✅ |
| 复杂 DvP | ~15ms | ~22ms | +7ms | ✅（非高频交易） |
| 批量结算 (100 笔) | ~50ms | ~65ms | +15ms | ✅（批量优化） |

### 3.3 多级准入模型

#### 准入等级定义

```
┌─────────────────────────────────────────────────────────────┐
│  准入等级架构                                                 │
│                                                              │
│  Level 4: 机构准入 (Institutional)                            │
│  ├── 要求: KYB + 牌照 + 资本金证明 + 基础设施审计              │
│  ├── 权限: Zone 运营者 / 验证者 / 做市商 / 发行方             │
│  └── 场景: 银行运营 Payment Zone, 券商运营 xStocks Zone       │
│                                                              │
│  Level 3: 合格投资者 (Qualified Investor)                     │
│  ├── 要求: Enhanced KYC + 认证投资者 VC + 适当性评估           │
│  ├── 权限: Level 2 + xStocks Zone 全功能                     │
│  └── 场景: 认证投资者参与股票代币化交易                        │
│                                                              │
│  Level 2: 增强 KYC (Enhanced KYC)                             │
│  ├── 要求: 基础 KYC + 收入证明 + 资金来源                     │
│  ├── 权限: Level 1 + RWA Zone 投资                           │
│  └── 场景: 零售投资者投资代币化房地产、债券                     │
│                                                              │
│  Level 1: 基础 KYC (Basic KYC)                                │
│  ├── 要求: 姓名 + 身份证件 + 地址证明                         │
│  ├── 权限: 公链 + Payment Zone                               │
│  └── 场景: 消费者使用稳定币支付、跨境汇款                      │
│                                                              │
│  Level 0: 无 KYC                                              │
│  ├── 要求: 无                                                 │
│  ├── 权限: 仅公链 DeFi（如果链上存在非许可区域）               │
│  └── 场景: 匿名 DeFi 交互（有限功能）                         │
│                                                              │
│  Regulator: 监管方准入                                        │
│  ├── 要求: 政府/监管机构证书                                  │
│  ├── 权限: Observer 角色 + 审计数据访问 + 合规仪表盘           │
│  └── 场景: SEC 审查 xStocks Zone, MAS 审查 Payment Zone       │
└─────────────────────────────────────────────────────────────┘
```

#### 准入等级 × Zone 矩阵

| 准入等级 | 公链 DeFi | Payment Zone | RWA Zone | xStocks Zone | Zone 运营 | 审计 |
|---------|:---------:|:------------:|:--------:|:------------:|:---------:|:----:|
| Level 0 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Level 1 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Level 2 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Level 3 | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Level 4 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Regulator | ✅ | ✅ (Observer) | ✅ (Observer) | ✅ (Observer) | ❌ | ✅ |

#### 准入升级流程

```
Level 0 用户想进入 RWA Zone (需要 Level 2):

1. 用户选择 CA（如某银行）启动 KYC 流程
2. Level 0 → Level 1:
   · 提交: 姓名 + 身份证件 + 地址证明
   · CA 验证 + 签发 KYC VC (level=1)
   · 用户提交 Compliance Transaction (0x77) 注册身份
   · IdentityRegistry 记录: kycLevel=1
   · 解锁: Payment Zone 访问

3. Level 1 → Level 2:
   · 提交: 收入证明 + 资金来源声明 + 银行对账单
   · CA 执行增强尽职调查 (EDD)
   · CA 签发 Enhanced KYC VC (level=2)
   · 更新 IdentityRegistry: kycLevel=2
   · 解锁: RWA Zone 投资权限

4. Zone 准入检查:
   · 用户调用 RWAZonePortal.deposit()
   · Sequencer 执行策略检查:
     ✅ kycLevel=2 ≥ RWA Zone 要求
     ✅ sanctionStatus=clean
     ✅ kycExpiration > now
   · 资产存入 RWA Zone
```

#### 边界条件处理

**KYC 过期处理**：

```
KYC 过期检测流程:

每个区块开始时:
  FOR EACH address in active_addresses:
    IF identity.kycExpiration <= block.timestamp:
      1. 发出 KYCExpired 事件
      2. 设置 identity.kycLevel = 0 (降级)
      3. 现有 Zone 内资产不会被没收（但无法发起新交易）
      4. 仅允许: 提现到 L1 + 续期 KYC
      5. 续期 KYC 后恢复原有等级

宽限期设计:
  · KYC 过期前 30 天: 发出 KYCExpiringWarning 事件
  · KYC 过期后 0-7 天: 宽限期，现有持仓可以平仓但不能开新仓
  · KYC 过期后 7+ 天: 仅允许提现
```

**制裁状态变更处理**：

```
制裁名单更新流程:

1. 制裁名单提供方（如 OFAC）通过链下 oracle 更新制裁名单 Merkle root
2. 策略引擎对所有活跃地址执行增量筛查
3. 如果地址被新增到制裁名单:
   a. 立即设置 sanctionStatus = FLAGGED
   b. 冻结该地址在所有 Zone 的交易能力
   c. 发出 SanctionStatusChanged 事件
   d. 通知 Zone 运营者 + 合规团队
   e. 人工审核确认后: FLAGGED → BLOCKED (确认) 或 FLAGGED → CLEAN (误报)
4. 冻结的资产处置按照监管机构指示执行
```

---

## 4. 可编程合规框架

### 4.1 合规即代码 (Compliance as Code)

将法规要求编码为链上可执行规则，实现合规的自动化、可审计、可验证。

#### 法规编码矩阵

| 法规 | 管辖区 | 编码实现 | 检查时机 | 违规处理 |
|------|-------|---------|---------|---------|
| **Reg D (SEC Rule 506)** | 美国 | `AccreditedInvestorPolicy`: kycLevel≥3 + accredited cert + investor count ≤ 35 (506b) or unlimited (506c) + 12-month lockup | 发行时 + 二级市场交易前 | 交易拒绝 + 原因码 `REG_D_VIOLATION` |
| **Reg S (SEC)** | 美国/国际 | `OffshoreSafeHarborPolicy`: jurisdiction ≠ US + 40-day distribution compliance period + no directed selling in US | 发行时 + 转账时 | 交易拒绝 + 原因码 `REG_S_VIOLATION` |
| **MiCA (EU)** | 欧盟 | `MiCAClassificationPolicy`: asset_type classification (ARTs/EMTs/other) + white paper disclosure check + reserve proof | 发行时 + 持续监控 | 发行阻止 / 交易暂停 |
| **Travel Rule (FATF)** | 全球 | `TravelRulePolicy`: transfer ≥ $3,000 → originator + beneficiary info attached to tx; VASP-to-VASP info exchange | 转账时 | 转账阻止直到 Travel Rule 数据附加 |
| **AML/CFT** | 全球 | `AMLScreeningPolicy`: real-time sanctions check + transaction pattern analysis + SAR auto-generation | 实时（每笔交易） | 交易冻结 + 自动 SAR 生成 |
| **Reg NMS (SEC)** | 美国 | `BestExecutionPolicy`: trade-through protection + order routing rules | xStocks 交易时 | 订单路由到最优价格 |
| **GDPR (EU)** | 欧盟 | `DataSovereigntyPolicy`: data processing consent tracking + right to erasure support + data portability | 持续 | 数据删除请求处理 |

#### Reg D 详细编码示例

```yaml
# Regulation D Rule 506(c) — 编码为策略
policy:
  id: "sec-reg-d-506c"
  regulation: "Securities Act of 1933, Regulation D, Rule 506(c)"
  scope: ASSET
  
  # 适用资产: Reg D 发行的证券型代币
  applies_to:
    asset_attribute: "regulatory_classification"
    value: "reg_d_506c"
  
  rules:
    # 规则 1: 投资者资质验证
    - name: "accredited-investor-only"
      description: "Rule 506(c) requires all purchasers to be accredited investors"
      condition:
        all:
          - identity.certifications.accredited == true
          - identity.certifications.accredited_verification == "reasonable_steps"
            # SEC 要求 "reasonable steps to verify" — 不能仅依赖自我声明
          - identity.kycExpiration > block.timestamp
      on_failure:
        action: REJECT
        reason: "REG_D_506C_ACCREDITATION_REQUIRED"
    
    # 规则 2: 12 个月锁定期
    - name: "holding-period"
      description: "Rule 144 holding period for restricted securities"
      condition:
        any:
          - asset.holdingStart + 365 days <= block.timestamp
            # 持有满 12 个月后可以转让
          - transfer.type == "issuer_buyback"
            # 发行方回购豁免锁定期
          - transfer.recipient.certifications.accredited == true
            AND asset.holdingStart + 180 days <= block.timestamp
            # 合格投资者之间 6 个月后可转让
      on_failure:
        action: REJECT
        reason: "REG_D_HOLDING_PERIOD_NOT_MET"
    
    # 规则 3: 公开招揽检查 (506(c) 允许, 506(b) 不允许)
    - name: "general-solicitation"
      description: "506(c) permits general solicitation if all buyers are verified accredited"
      condition:
        - all_buyers_verified: true
      note: "This rule is always satisfied for 506(c); included for audit completeness"
    
    # 规则 4: 转售限制通知
    - name: "resale-restriction-notice"
      description: "Securities are restricted and must bear appropriate legend"
      condition:
        - asset.metadata.contains("restricted_legend") == true
      on_failure:
        action: WARN  # 不阻止，但记录审计事件
        reason: "REG_D_RESTRICTED_LEGEND_MISSING"

  # 合规事件
  events:
    - on: "transfer_completed"
      emit: "RegDTransferEvent(asset, from, to, amount, timestamp)"
    - on: "holding_period_elapsed"
      emit: "RegDHoldingPeriodCompleted(asset, holder, startDate)"
    - on: "annual_review"
      emit: "RegDForm D_Filing_Reminder(asset, issuer)"
```

#### Travel Rule 实现

Travel Rule 是 Payment Zone 的核心合规要求，要求 ≥$3,000 的转账必须携带发送方和接收方身份信息：

```
Travel Rule 交易流程:

1. 发送方 (Alice @ VASP-A) 发起转账:
   transfer(to=Bob@VASP-B, amount=5000 USDC)

2. 策略引擎检测到 amount ≥ $3,000, 触发 Travel Rule:
   
3. VASP-A 节点准备 Travel Rule 数据:
   originator_info = {
     name_hash: hash("Alice Smith"),
     account_id: hash(alice_account),
     vasp: "VASP-A",
     jurisdiction: "SG"
   }
   
4. VASP-B 节点提供接收方信息:
   beneficiary_info = {
     name_hash: hash("Bob Jones"),
     account_id: hash(bob_account),
     vasp: "VASP-B",
     jurisdiction: "US"
   }

5. Travel Rule 数据打包:
   方案 A — 链上 (加密存储):
     travel_rule_commitment = hash(originator_info || beneficiary_info)
     encrypted_data = encrypt(originator_info || beneficiary_info, regulator_pubkey)
     → 存入审计 DA 通道
   
   方案 B — 链下 VASP-to-VASP (隐私优先):
     VASP-A ←→ VASP-B 通过 Travel Rule 协议交换信息
     链上仅记录: travel_rule_exchanged = true
     
6. 策略引擎验证:
   ✅ travel_rule_data_attached == true
   ✅ originator_vasp.registered == true
   ✅ beneficiary_vasp.registered == true
   → 转账执行

7. 审计记录:
   TravelRuleEvent(tx_hash, amount, originator_vasp, beneficiary_vasp, timestamp)
```

### 4.2 跨司法管辖区合规

#### 管辖区策略路由

```
跨管辖区交易流程:

场景: 新加坡投资者 (Alice) 向美国投资者 (Bob) 转让 RWA 代币

1. 身份解析:
   Alice: jurisdiction=702 (SG), kycLevel=3
   Bob:   jurisdiction=840 (US), kycLevel=3

2. 管辖区确定:
   · Alice 适用: MAS 法规 (新加坡)
   · Bob 适用: SEC 法规 (美国)
   · 资产适用: 发行地法规 (看资产 metadata)

3. 策略路由:
   applicable_policies = [
     global_policies,                    // 全局制裁检查
     zone_policies["rwa"],              // RWA Zone 准入
     jurisdiction_policies["SG"],        // MAS: 新加坡合规
     jurisdiction_policies["US"],        // SEC: Reg D/S 合规
     asset_policies[token_address]       // 资产特定规则
   ]

4. 策略评估（ALL must pass）:
   ✅ 全局制裁检查: 双方均 clean
   ✅ RWA Zone: 双方均 kycLevel ≥ 2
   ✅ MAS: Alice 符合 MAS 投资者保护要求
   ✅ SEC Reg S: Alice 是非美国人，Reg S 适用
   ✅ SEC Reg D: Bob 是美国认证投资者，Reg D 适用
   ✅ 资产策略: 锁定期已过
   → 交易通过
```

#### 管辖区冲突解决

| 冲突类型 | 示例 | 解决策略 |
|---------|------|---------|
| **合规标准冲突** | SEC 要求 12 个月锁定期，MAS 无此要求 | **从严原则**：适用最严格的标准 |
| **数据处理冲突** | GDPR 要求数据可删除，SEC 要求保留 5-7 年 | **分域处理**：EU 用户数据在 Zone DA 中按 GDPR 存储，SEC 报告数据在独立审计通道保留 |
| **分类冲突** | MiCA 将某资产分类为 ART，SEC 分类为证券 | **双重分类**：资产同时满足两种分类的合规要求 |
| **披露冲突** | 美国要求公开特定信息，中国限制数据出境 | **地域隔离**：通过 Zone 隔离 + 选择性披露实现差异化合规 |

#### 地域证明机制

如何可靠地证明用户的居住地/国籍？

| 证明方式 | 可靠性 | 隐私性 | 适用场景 |
|---------|-------|-------|---------|
| **KYC CA 签发的居住地 VC** | 高 | 中 | 标准流程 — CA 验证地址后签发 |
| **银行对账单 VC** | 高 | 低 | 增强验证 — 银行证明账户地址 |
| **IP 地理位置** | 低（可绕过 VPN） | 高 | 辅助验证 — 与 VC 交叉验证 |
| **手机号归属地** | 中 | 中 | Payment 场景 — SIM 绑定验证 |
| **ZK 居住地证明** | 高 | 高 | 长期方案 — ZK 证明管辖区属性 |

**推荐组合**：KYC CA 签发的居住地 VC（主要）+ IP 地理位置交叉验证（辅助，flag 异常）。

### 4.3 合规事件与报告

#### 合规事件体系

```
┌─────────────────────────────────────────────────────────┐
│  合规事件分层架构                                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Layer 1: 实时事件流 (Real-Time Event Stream)      │   │
│  │                                                    │   │
│  │  · ComplianceCheckResult                           │   │
│  │    {txHash, from, to, result, reasonCode, policies}│   │
│  │  · SanctionAlert                                   │   │
│  │    {address, matchType, listSource, confidence}     │   │
│  │  · AnomalyDetected                                 │   │
│  │    {pattern, addresses, timeWindow, severity}       │   │
│  │  · KYCStatusChange                                 │   │
│  │    {identity, oldLevel, newLevel, reason}           │   │
│  │  · TravelRuleExchange                              │   │
│  │    {txHash, originatorVASP, beneficiaryVASP}        │   │
│  └──────────────────────────────────────────────────┘   │
│                         │                                │
│                         ▼                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Layer 2: 聚合分析 (Aggregated Analytics)          │   │
│  │                                                    │   │
│  │  · 交易合规通过率（按 Zone/资产/时间段）             │   │
│  │  · 拒绝原因分布统计                                 │   │
│  │  · 异常模式聚类分析                                 │   │
│  │  · 活跃身份/到期身份统计                            │   │
│  └──────────────────────────────────────────────────┘   │
│                         │                                │
│                         ▼                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Layer 3: 监管报告 (Regulatory Reports)            │   │
│  │                                                    │   │
│  │  · SAR (Suspicious Activity Report) — 自动生成     │   │
│  │  · CTR (Currency Transaction Report) — > $10,000   │   │
│  │  · Form D (SEC) — Reg D 发行年度申报               │   │
│  │  · MiCA 季度报告 — 资产储备 + 交易统计              │   │
│  │  · FATF Travel Rule 合规报告                       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### 审计 DA 通道设计

参考 WHI-357 的"专用审计数据通道"概念：

```
常规交易数据流:
  交易 → Zone DA (加密存储) → 仅 Zone 参与方可见

审计数据流 (独立通道):
  合规事件 → 审计 DA 通道 (独立加密存储)
  │
  ├── 加密层 1: Zone Sequencer 密钥 (运营审计)
  ├── 加密层 2: 监管方专用密钥 (监管审计)
  └── 加密层 3: 合规团队密钥 (内部审计)

监管方访问模式:
  · Observer RPC: 实时数据流 (类似 Canton Observer 模式)
  · 审计 DA 解密: 用监管方专用密钥解密历史记录
  · Merkle 证明导出: 按需导出特定交易的包含证明 (参考 Prividium)
```

#### 合规仪表盘

参考 Prividium Compliance Explorer，设计角色差异化的合规仪表盘：

| 角色 | 可见数据 | 功能 |
|------|---------|------|
| **Zone 运营者** | 全部 Zone 数据 | 策略管理 + 异常处理 + 报告生成 |
| **合规官** | 合规事件 + 统计 + 报告 | 审核 + SAR 提交 + 策略调整建议 |
| **审计员** | 只读审计数据 | 检查审计追踪 + 验证合规声明 |
| **监管方 (Observer)** | 授权 Zone 的完整数据 | 实时监控 + 执法数据提取 |
| **机构用户** | 自身交易 + 合规状态 | 查看自身合规状态 + 续期提醒 |

---

## 5. M3 vs M4 深度对比

### 5.1 架构对比

| 维度 | M3（合约层 bolt-on） | M4（协议层原生） | 分析 |
|------|---------------------|-----------------|------|
| **合规检查位置** | ERC-20 transfer hook（合约内） | Pre-EVM（Sequencer + 预编译） | M4 更安全：无法被合约层 delegatecall 绕过 |
| **身份存储** | 合约状态变量 | 预编译内置存储 (0x0401) | M4 更高效：避免 SLOAD gas 开销 |
| **策略注册** | Registry 合约 | PolicyRegistry 预编译 (0x0403) | M4 更可靠：预编译级执行，delegatecall 阻断 |
| **隐私保护** | 无内建隐私 | ZK 选择性披露 (0x0405) | M4 有原生隐私方案 |
| **升级方式** | 合约升级 (proxy pattern) | 协议升级 (hard fork) | M3 更灵活：无需全网升级 |
| **EVM 兼容性** | 完全兼容标准 ERC-20 | 需要自定义交易类型 (0x77, 0x78) | M3 兼容性更好：标准工具链直接使用 |
| **覆盖范围** | 仅 ERC-20 转账 | 所有交易类型 | M4 更全面：包括合约部署、跨链、治理 |
| **开发复杂度** | 低（Solidity 合约） | 高（预编译 Rust + 协议修改） | M3 开发门槛低 |
| **审计完整性** | 合约事件日志 | 专用审计 DA 通道 | M4 审计更深入 |

### 5.2 安全性深度对比

**M3 的绕过风险**：

```
M3 场景: ERC-20 transfer hook 检查合规

漏洞 1 — delegatecall 绕过:
  攻击者部署代理合约 → 通过 delegatecall 调用 token 合约
  → transfer hook 中 msg.sender 是代理合约，不是真实发送者
  → 合规检查基于错误的身份

漏洞 2 — 直接 EVM 操作:
  如果 token 合约有任何不经过 transfer hook 的状态修改路径
  → 余额可以被修改而不触发合规检查

漏洞 3 — Flash Loan + 合约组合:
  通过 DeFi 协议的组合性，资产流转可能不经过 transfer hook
  → 合规检查被跳过
```

**M4 如何消除这些风险**：

```
M4 防御:

防御 1 — delegatecall 阻断:
  预编译级别 enforced: DelegateCallNotAllowed
  任何通过 delegatecall 调用合规预编译的尝试 → 直接 revert
  参考: Tempo TIP-403 direct-call-only enforcement

防御 2 — Pre-EVM 检查:
  合规检查在 EVM 执行之前发生（Sequencer 策略引擎）
  即使 EVM 内部有漏洞，不合规交易根本不会到达 EVM

防御 3 — 全交易覆盖:
  不仅仅是 transfer，所有交易类型都经过合规流水线
  包括: 合约部署、合约调用、跨链桥接、治理操作

防御 4 — L1 桥接过滤:
  L1→L2 force transaction 也被过滤（TransactionFilterer）
  消除了 L2 方案中常见的 L1 强制交易绕过路径
```

### 5.3 性能对比

| 指标 | M3 | M4 | 说明 |
|------|-----|-----|------|
| **简单转账 gas** | ~80,000 (含 hook) | ~65,000 (预编译) | 预编译比合约调用节省 ~19% gas |
| **合规检查延迟** | ~5ms (EVM 执行中) | ~3ms (Pre-EVM + 缓存) | M4 可以使用 Sequencer 内存缓存 |
| **策略更新生效** | 立即（合约变量修改） | ~12s（L1 区块确认 + Zone 同步） | M3 更快，但 M4 延迟可接受 |
| **批量处理** | 无特殊优化 | 批量合规检查引擎 | M4 批量场景优势明显 |
| **缓存可能性** | 有限（合约存储读取成本固定） | 丰富（Sequencer 内存缓存） | M4 高频交易场景优势显著 |

### 5.4 升级与治理对比

| 维度 | M3 | M4 |
|------|-----|-----|
| **策略更新** | 合约管理员直接调用 → 立即生效 | 治理提案 → PolicyRegistry 更新 → Zone 自动同步 |
| **紧急暂停** | 合约 pause() → 立即 | 全局暂停开关 + Sequencer 策略 → 秒级 |
| **新法规支持** | 部署新合规合约 → 无需升级 | 注册新策略（如果 DSL 支持）或协议升级 |
| **回滚** | 合约回滚（如有 proxy） | 协议回滚（严重事件） |

### 5.5 综合评估

```
推荐: M4 协议层原生方案

理由:
1. 安全性是企业级区块链的第一优先级
   → M4 的 Pre-EVM + 预编译方案不可绕过
   
2. 覆盖范围决定了合规的有效性
   → M3 仅覆盖 token 转账，M4 覆盖所有交易
   
3. 性能在预编译 + 缓存优化下优于合约方案
   → 企业场景的交易量支持这一优化

4. 升级灵活性的代价可以通过策略 DSL 缓解
   → 大多数策略变更不需要协议升级

5. EVM 兼容性的代价可以通过封装层缓解
   → 面向开发者的 SDK 隐藏底层差异

风险:
· 协议升级的治理复杂度（需要全网共识）
· 自定义交易类型可能影响工具链兼容性
· 预编译开发需要 Rust 专业能力
```

---

## 6. 身份互操作方案

### 6.1 跨 Zone 身份：一次 KYC，多 Zone 通用

```
身份跨 Zone 通用架构:

┌────────────────────────────────────────────────┐
│              MainChain IdentityRegistry          │
│              (0x0401 — 全局身份源)               │
│                                                  │
│  Identity: alice_id                              │
│  ├── kycLevel: 3                                 │
│  ├── certifications: [accredited, kyc_enhanced]  │
│  ├── jurisdiction: SG                            │
│  └── addresses: [addr1, addr2, addr3]            │
└────────┬─────────────┬──────────────┬────────────┘
         │             │              │
    自动同步        自动同步       自动同步
         │             │              │
         ▼             ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Payment  │   │ RWA      │   │ xStocks  │
│ Zone     │   │ Zone     │   │ Zone     │
│          │   │          │   │          │
│ 检查:     │   │ 检查:     │   │ 检查:     │
│ kyc ≥ 1  │   │ kyc ≥ 2  │   │ kyc ≥ 3  │
│ ✅ 通过   │   │ ✅ 通过   │   │ ✅ 通过   │
└──────────┘   └──────────┘   └──────────┘

Alice 只做一次 KYC (Level 3)，自动获得所有 Zone 的准入权限
无需在每个 Zone 重复 KYC 流程
```

**跨 Zone 身份同步机制**：

- MainChain IdentityRegistry 是身份的唯一真实来源 (Single Source of Truth)
- 每个 Zone 通过 StateReader 预编译实时读取 MainChain 身份状态
- 身份更新在下一个 L1 区块自动传播到所有 Zone（~12s 延迟）
- Zone 本地缓存身份属性，per-block GC 保证一致性

### 6.2 跨链身份互操作

```
跨链身份互操作架构:

┌──────────────────────────┐     ┌──────────────────────────┐
│  Whisker Chain             │     │  外部链 (如 Ethereum)      │
│                            │     │                            │
│  IdentityRegistry (0x0401) │     │  ENS / ERC-725            │
│  ├── DID: did:whisker:...  │     │  ├── ENS: alice.eth       │
│  ├── VCs: [kyc, accred.]  │     │  ├── VC: [kyc, ...]       │
│  └── Addresses: [...]      │     │  └── Address: 0x...       │
│                            │     │                            │
└────────────┬───────────────┘     └────────────┬───────────────┘
             │                                   │
             └───────────┬───────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  跨链身份桥            │
              │                      │
              │  · DID 解析器互认     │
              │  · VC 格式转换器      │
              │  · 跨链身份证明       │
              │    (ZK proof of      │
              │     identity on      │
              │     another chain)   │
              └──────────────────────┘
```

**跨链身份标准兼容**：

| 标准 | 支持方式 | 用途 |
|------|---------|------|
| **W3C DID** | `did:whisker:` method + DID Resolution | 全球唯一身份标识 |
| **W3C Verifiable Credentials** | VC 签发/验证/存储 | 可验证凭证互操作 |
| **ERC-725 (Proxy Identity)** | 兼容适配层 | 与以太坊身份系统互操作 |
| **ERC-735 (Claim Holder)** | VC → Claim 转换 | 与以太坊声明系统互操作 |
| **DIF Presentation Exchange** | VP 请求/响应格式 | 跨平台凭证展示 |

### 6.3 传统系统集成

```
传统系统 → 链上身份的桥接:

┌───────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ 银行 KYC 系统   │     │  KYC Bridge      │     │  IdentityRegistry │
│               │     │  (链下适配器)      │     │  (0x0401)         │
│ · 客户档案     │────>│                  │────>│                   │
│ · 合规记录     │     │ · 身份映射        │     │ · 链上身份注册     │
│ · 交易历史     │     │ · VC 签发         │     │ · 属性更新        │
└───────────────┘     │ · 状态同步        │     └──────────────────┘
                      └──────────────────┘
                      
┌───────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ 证券开户系统    │     │  Securities      │     │  IdentityRegistry │
│               │     │  Account Bridge   │     │  (0x0401)         │
│ · 投资者档案   │────>│                  │────>│                   │
│ · 适当性评估   │     │ · 投资者资质映射   │     │ · 合格投资者 VC   │
│ · 牌照信息     │     │ · VC 签发         │     │ · 牌照 VC         │
└───────────────┘     └──────────────────┘     └──────────────────┘

┌───────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ 企业 IAM       │     │  SSO Bridge      │     │  RPC Auth Layer   │
│ (Okta/Azure AD)│     │  (OIDC 适配器)    │     │                   │
│               │────>│                  │────>│ · JWT → 链上身份   │
│ · LDAP 群组    │     │ · OIDC 认证       │     │ · RBAC 映射       │
│ · MFA 策略     │     │ · 角色 → 身份映射  │     │ · Session 管理    │
│ · 设备合规     │     │ · Wallet 绑定     │     │                   │
└───────────────┘     └──────────────────┘     └──────────────────┘
```

参考 Prividium 的 Okta SSO 集成模式：企业员工使用现有企业 SSO 认证，MFA 策略和设备合规策略自动继承到区块链访问控制。LDAP 群组自动映射为链上角色。

### 6.4 身份可移植性

用户应能将身份从一个平台迁移到另一个平台：

```
身份导出/导入流程:

1. 导出 (从 Whisker Chain):
   · 用户请求身份导出
   · IdentityRegistry 生成身份快照:
     {did, vcList, attributeProof, addressList, roleHistory}
   · 用 root key 签名
   · 生成 W3C Verifiable Presentation

2. 导入 (到目标链):
   · 目标链验证 VP 签名
   · 验证 VC 签发方是否在信任列表中
   · 映射属性到目标链的身份模型
   · 注册新的链上身份

限制:
   · VC 的有效性取决于目标链是否信任签发 CA
   · 合规属性可能需要按目标链要求重新评估
   · 交易历史不可移植（但审计记录可按需导出）
```

---

## 7. 各叙事合规配置示例

### 7.1 RWA 叙事 — 代币化房地产投资

```yaml
# RWA Zone 合规配置
zone:
  id: "rwa-zone-01"
  name: "RWA Investment Zone"
  
  # 准入要求
  admission:
    minKYCLevel: 2                    # Enhanced KYC
    requiredCertifications:
      - "accredited_investor"         # 认证投资者
    acceptedJurisdictions:            # 接受的管辖区
      - "US"    # Reg D/S
      - "SG"    # MAS
      - "EU"    # MiCA
      - "UK"    # FCA
    acceptedCAs:                      # 接受的认证方
      - "tier1_banks"
      - "licensed_compliance_providers"
  
  # 策略配置
  policies:
    # 全局策略
    - id: "rwa-sanctions"
      type: BLACKLIST
      source: "ofac_sdn_list"
      updateFrequency: "6h"
    
    # 投资者适当性
    - id: "rwa-investor-suitability"
      type: ATTRIBUTE_CHECK
      rules:
        - attribute: "certifications.accredited"
          operator: "=="
          value: true
        - attribute: "kycExpiration"
          operator: ">"
          value: "block.timestamp"
    
    # Reg D 锁定期
    - id: "rwa-reg-d-lockup"
      type: CUSTOM_DSL
      dsl: |
        IF asset.regulatory_classification == "reg_d_506c":
          REQUIRE asset.holdingSince + 365d <= now
          OR transfer.type == "issuer_buyback"
    
    # DvP 复合策略
    - id: "rwa-dvp-compound"
      type: COMPOUND
      senderPolicy:
        type: ATTRIBUTE_CHECK
        rules:
          - attribute: "kycLevel"
            operator: ">="
            value: 2
      recipientPolicy:
        type: WHITELIST
        source: "qualified_investor_list"
  
  # 报告配置
  reporting:
    realTimeEvents:
      - "ComplianceCheckResult"
      - "SanctionAlert"
    periodicReports:
      - type: "form_d_annual"
        schedule: "yearly"
        regulator: "SEC"
      - type: "investor_count"
        schedule: "quarterly"
    auditAccess:
      observers:
        - role: "SEC_Observer"
          scope: "full_zone_data"
        - role: "MAS_Observer"
          scope: "sg_jurisdiction_data"
```

### 7.2 xStocks 叙事 — 股票代币化交易

```yaml
# xStocks Zone 合规配置
zone:
  id: "xstocks-zone-01"
  name: "xStocks Trading Zone"
  
  admission:
    minKYCLevel: 3                    # 合格投资者
    requiredCertifications:
      - "accredited_investor"
      - "broker_licensed"             # 对做市商/经纪商额外要求牌照
    additionalChecks:
      - "suitability_assessment"      # 投资者适当性评估
  
  policies:
    # 制裁 + AML
    - id: "xstocks-aml"
      type: COMPOUND
      senderPolicy: { type: BLACKLIST, source: "ofac_sdn_list" }
      recipientPolicy: { type: BLACKLIST, source: "ofac_sdn_list" }
    
    # Reg NMS 最优执行
    - id: "xstocks-reg-nms"
      type: CUSTOM_DSL
      dsl: |
        IF order.type == "market_order":
          REQUIRE order.price >= NBBO.bid AND order.price <= NBBO.ask
          # National Best Bid and Offer 价格保护
        IF order.type == "limit_order":
          REQUIRE order.price NOT trade_through NBBO
    
    # Reg SHO 卖空限制
    - id: "xstocks-reg-sho"
      type: CUSTOM_DSL
      dsl: |
        IF order.side == "sell" AND position.balance < order.quantity:
          # 裸卖空检测
          REQUIRE position.borrowed >= order.quantity - position.balance
          REQUIRE position.locate_confirmation != null
    
    # 市场监控
    - id: "xstocks-surveillance"
      type: CUSTOM_DSL
      dsl: |
        # 异常交易模式检测
        IF account.daily_volume > threshold.daily_volume_alert:
          EMIT SurveillanceAlert("high_volume", account, daily_volume)
        IF trade.price_impact > threshold.price_impact_alert:
          EMIT SurveillanceAlert("price_impact", trade, impact)
  
  reporting:
    realTimeEvents:
      - "TradeExecution"
      - "SurveillanceAlert"
      - "RegNMSViolation"
    periodicReports:
      - type: "market_surveillance_daily"
        schedule: "daily"
      - type: "sar_filing"
        schedule: "as_needed"
        trigger: "surveillance_alert_confirmed"
    auditAccess:
      observers:
        - role: "SEC_Observer"
          scope: "full_trading_data"
        - role: "FINRA_Observer"
          scope: "market_surveillance_data"
```

### 7.3 Payment 叙事 — 跨境支付

```yaml
# Payment Zone 合规配置
zone:
  id: "payment-zone-01"
  name: "Payment Zone"
  
  admission:
    # B2C: 基础 KYC 即可
    consumer:
      minKYCLevel: 1
      requiredCertifications: []
    # B2B: VASP 注册
    institutional:
      minKYCLevel: 4
      requiredCertifications:
        - "vasp_registered"
  
  policies:
    # Travel Rule
    - id: "payment-travel-rule"
      type: CUSTOM_DSL
      dsl: |
        IF transfer.amount >= 3000 USD_EQUIVALENT:
          REQUIRE travel_rule.originator_info != null
          REQUIRE travel_rule.beneficiary_info != null
          REQUIRE travel_rule.originator_vasp.registered == true
          REQUIRE travel_rule.beneficiary_vasp.registered == true
    
    # AML 筛查
    - id: "payment-aml"
      type: COMPOUND
      senderPolicy:
        type: BLACKLIST
        source: "combined_sanctions_list"  # OFAC + EU + UN
      recipientPolicy:
        type: BLACKLIST
        source: "combined_sanctions_list"
    
    # 交易限额
    - id: "payment-limits"
      type: CUSTOM_DSL
      dsl: |
        # 个人用户每日限额
        IF identity.investorType == "retail":
          REQUIRE account.daily_total + transfer.amount <= 50000 USD
        # CTR 报告触发
        IF transfer.amount >= 10000 USD_EQUIVALENT:
          EMIT CTR_Report(transfer)
    
    # B2B 白名单
    - id: "payment-b2b-allowlist"
      type: WHITELIST
      scope: "b2b_transfers"
      source: "registered_vasp_list"
  
  reporting:
    realTimeEvents:
      - "TravelRuleExchange"
      - "CTR_Trigger"
      - "SanctionAlert"
    periodicReports:
      - type: "travel_rule_compliance"
        schedule: "monthly"
      - type: "ctr_filing"
        schedule: "daily"
        trigger: "amount >= 10000 USD"
    auditAccess:
      observers:
        - role: "FinCEN_Observer"
          scope: "us_jurisdiction_transfers"
        - role: "MAS_Observer"
          scope: "sg_jurisdiction_transfers"
```

---

## 8. 与 Tempo/Canton/Prividium 合规方案对比

### 8.1 合规架构对比

| 维度 | Tempo | Canton | Prividium | Whisker (M4) |
|------|-------|--------|-----------|-------------|
| **合规层级** | 协议层 (预编译) | 语言层 (Daml) | 中间件层 (Proxy RPC) | 协议层 (预编译) + 五层纵深防御 |
| **核心机制** | TIP-403 策略注册表 | Signatory/Observer/Controller | JWT + RBAC + L1 Filterer | PolicyRegistry + ComplianceCheck + 策略 DSL |
| **绕过风险** | 极低 (delegatecall 阻断) | 极低 (编译时强制) | 中 (Sequencer 直连可绕过) | 极低 (五层防御) |
| **策略灵活性** | 中 (白名单/黑名单 + 复合) | 高 (Daml 任意逻辑) | 高 (6 种 RBAC 类型) | 高 (DSL + 形式化验证) |
| **升级方式** | L1 交易即时更新 | Daml 合约升级 | 热更新 (API 后端) | L1 策略注册 → 自动同步 |

### 8.2 身份模型对比

| 维度 | Tempo | Canton | Prividium | Whisker (M4) |
|------|-------|--------|-----------|-------------|
| **身份基础** | AccountKeychain (密钥委托) | UID (密码学 PKI) | OIDC/SIWE (企业 SSO) | 五层身份模型 (Key → DID → VC → Attribute → Role) |
| **消费者体验** | ✅ WebAuthn/P-256 一等公民 | ❌ 需要 X.509 证书 | ❌ 依赖 MetaMask/浏览器钱包 | ✅ WebAuthn/P-256 + ERC-4337 |
| **企业集成** | 中 (密钥管理为主) | 高 (PKI 体系) | ✅ Okta SSO 原生 | ✅ SSO + PKI + WebAuthn 全覆盖 |
| **密钥委托** | ✅ 完整 (scope + limit + expiry) | ❌ (Party 级，非密钥级) | ❌ (基于角色，非密钥) | ✅ (参考 Tempo AccountKeychain) |
| **隐私** | 中 (链上白名单可见) | 高 (Projection 隔离) | 低 (SSO 身份公开) | 高 (ZK 选择性披露) |
| **跨平台互认** | 有限 | 多 Synchronizer 支持 | ZKsync Connect | DID/VC 标准 + 跨链桥 |

### 8.3 合规能力对比

| 能力 | Tempo | Canton | Prividium | Whisker (M4) |
|------|:-----:|:------:|:---------:|:-----------:|
| **制裁筛查** | ✅ 黑名单 | ❌ 需自建 | ✅ ZK 证明 | ✅ 黑名单 + ZK 证明 |
| **Travel Rule** | ❌ 无内建 | ❌ 无内建 | ❌ 无内建 | ✅ 协议级内建 |
| **Reg D/S 锁定期** | ✅ 策略可实现 | ✅ Daml 逻辑 | ✅ RBAC 限制 | ✅ DSL 编码 + 形式化验证 |
| **跨管辖区** | ✅ 多 Zone | ✅ 多 Synchronizer | ❌ 单链单租户 | ✅ 多 Zone + 管辖区路由 |
| **GDPR** | ❓ Zone DA 可删除 | ✅ 原生支持 | ❌ ZK Rollup L1 永久 | ✅ Zone DA 可删除 |
| **实时监控** | 有限 | Observer 模式 | ✅ Compliance Explorer | ✅ 审计 DA 通道 + 仪表盘 |
| **监管审计** | 有限 | ✅ Observer 直接数据 | ✅ Merkle 证明导出 | ✅ Observer + Merkle 导出 + ZK |
| **形式化验证** | ❌ | ✅ (Daml 类型系统) | ❌ | ✅ (策略 DSL 验证) |

### 8.4 Whisker M4 的独特价值

相比 Tempo/Canton/Prividium，Whisker M4 方案的独特贡献：

1. **五层纵深防御**：融合 Prividium 的中间件层防御 + Tempo 的预编译层防御 + 新增的 L1 桥接过滤层，形成业界最完整的合规防御纵深

2. **策略 DSL + 形式化验证**：Tempo 的策略表达力有限（白名单/黑名单），Canton 的 Daml 太重，Whisker 的 DSL 在表达力和安全性之间取得平衡

3. **Travel Rule 协议级内建**：三个参考平台都没有内建 Travel Rule 支持，Whisker 将其作为 Payment Zone 的核心能力

4. **ZK 合规证明 + Observer 审计的组合**：Prividium 有 ZK 但无 Observer，Canton 有 Observer 但无 ZK，Whisker 两者兼备——日常通过 ZK 保护隐私，监管审计时通过 Observer 提供完整数据

5. **Sequencer-as-Compliance-Officer 的系统化实现**：WHI-346 识别出 Tempo 和 Prividium 都在利用 Sequencer 的全数据可见性做合规，但没有系统化。Whisker 将其设计为明确的架构模式，配合专用审计 DA 通道

6. **消费者 + 企业双轨身份**：Tempo 偏消费者 (Passkey)，Prividium 偏企业 (Okta SSO)，Whisker 的五层身份模型同时支持两种场景

### 8.5 从各平台借鉴的关键机制

| 借鉴来源 | 机制 | Whisker 中的实现 |
|---------|------|-----------------|
| **Tempo** | TIP-403 策略注册表 | PolicyRegistry 预编译 (0x0403) |
| **Tempo** | AccountKeychain 密钥委托 | Layer 0 密钥管理 + 委托密钥 |
| **Tempo** | WebAuthn/P-256 一等公民签名 | Layer 0 多签名类型支持 |
| **Tempo** | SharedPolicyCache per-block GC | Zone 策略缓存一致性保证 |
| **Tempo** | Compound transfer policies (TIP-1015) | 复合策略类型 (sender/recipient 分离) |
| **Tempo** | 加密存款 + 合规检查 | ECIES 加密 + TIP-403 弹回机制 |
| **Canton** | Observer 角色 (监管直接数据访问) | Observer RPC + 审计 DA 通道 |
| **Canton** | 子交易隐私 (Projection) | Zone 隔离 + 选择性披露 |
| **Canton** | GDPR 原生支持 (本地数据删除) | Zone DA 可删除存储 |
| **Canton** | UTxO-like 不可变审计追踪 | 合规事件不可变日志 |
| **Prividium** | Proxy RPC 三步验证 | Layer 2 认证 RPC 层 |
| **Prividium** | RBAC 6 种权限类型 | 策略 DSL 丰富表达力 |
| **Prividium** | Okta SSO 集成 | SSO Bridge (OIDC 适配器) |
| **Prividium** | ZK 制裁筛查 (无 PII 泄露) | SelectiveDisclosure 预编译 (0x0405) |
| **Prividium** | Merkle 证明导出 | 审计数据按需导出 + 包含证明 |
| **Prividium** | L1 TransactionFilterer | Layer 5 L1 桥接过滤层 |
| **Prividium** | Restrict Argument 权限类型 | 策略 DSL 参数约束能力 |

---

## 9. 实施路线图

### Phase 1: 基础框架 (4-6 周)

| 组件 | 交付物 | 优先级 |
|------|-------|-------|
| IdentityRegistry 预编译 (0x0401) | isVerified(), getKYCLevel(), registerIdentity() | P0 |
| PolicyRegistry 预编译 (0x0403) | 基础白名单/黑名单策略 | P0 |
| Sequencer 策略引擎 | prepare_l1_block() 中的合规检查 | P0 |
| 认证 RPC 层 | JWT + 基础身份验证 | P0 |

### Phase 2: 高级能力 (6-8 周)

| 组件 | 交付物 | 优先级 |
|------|-------|-------|
| ComplianceCheck 预编译 (0x0402) | 交易级合规评估 | P1 |
| 策略 DSL 编译器 | DSL → 策略字节码 | P1 |
| 复合策略 (Compound) | sender/recipient 分离评估 | P1 |
| WebAuthn/P-256 支持 | 交易类型 0x76 + Passkey 验证 | P1 |
| L1 桥接过滤 | TransactionFilterer 合约 | P1 |

### Phase 3: 隐私与审计 (8-12 周)

| 组件 | 交付物 | 优先级 |
|------|-------|-------|
| SelectiveDisclosure 预编译 (0x0405) | ZK 选择性披露 | P2 |
| 审计 DA 通道 | 独立加密审计数据流 | P2 |
| Observer 角色 | 监管方 RPC + 数据访问 | P2 |
| Travel Rule 引擎 | VASP-to-VASP 信息交换 | P2 |
| 合规仪表盘 | 实时监控 + 报告生成 | P2 |

### Phase 4: 高级合规 (12-16 周)

| 组件 | 交付物 | 优先级 |
|------|-------|-------|
| ZK 制裁筛查 | STARK proof of non-inclusion in OFAC SDN | P3 |
| 策略形式化验证 | 策略安全性自动验证 | P3 |
| 跨链身份桥 | DID/VC 跨链互操作 | P3 |
| 高级 AML 模式检测 | 机器学习 + 链上模式识别 | P3 |
| SSO Bridge (企业 IAM) | OIDC → 链上身份映射 | P3 |

---

## 附录 A: 预编译接口汇总

| 地址 | 名称 | Gas 成本 | 合规功能 |
|------|------|---------|---------|
| `0x0401` | IdentityRegistry | 2,000 (查询) / 50,000 (更新) | KYC 状态、投资者资质、跨平台身份 |
| `0x0402` | ComplianceCheck | 5,000 | 交易级合规门控 (parties × amount × context) |
| `0x0403` | PolicyRegistry | 3,000 (查询) / 100,000 (注册) | TIP-403 兼容策略执行: 白名单/黑名单/复合 |
| `0x0404` | EncryptedDeposit | 6,000 | ECIES + Chaum-Pedersen ZK — 隐私保护存款 |
| `0x0405` | SelectiveDisclosure | 8,000 | Viewing Key ZK 披露: 仅向授权方暴露特定属性 |

**`no_std` 约束**：所有预编译兼容 `no_std`，可在 SP1/RISC-V ZK 证明器中执行，支持从 BFT 快速终局性迁移到 ZK 有效性证明。

## 附录 B: 原因码 (Reason Code) 定义

| 原因码 | 含义 | 处理 |
|-------|------|------|
| `SANCTION_HIT` | 地址在制裁名单中 | 交易拒绝 + 冻结 + 告警 |
| `KYC_INSUFFICIENT` | KYC 等级不满足要求 | 交易拒绝 + 引导升级 |
| `KYC_EXPIRED` | KYC 已过期 | 交易拒绝 + 引导续期 |
| `NOT_ACCREDITED` | 非认证投资者 | 交易拒绝 + 引导认证 |
| `REG_D_LOCKUP` | Reg D 锁定期未满 | 交易拒绝 + 显示剩余天数 |
| `REG_S_GEO_VIOLATION` | Reg S 地域限制违反 | 交易拒绝 |
| `TRAVEL_RULE_MISSING` | Travel Rule 数据缺失 | 交易暂停 + 等待数据 |
| `DAILY_LIMIT_EXCEEDED` | 超过每日限额 | 交易拒绝 + 显示剩余额度 |
| `SUITABILITY_FAILED` | 投资者适当性不匹配 | 交易拒绝 |
| `ZONE_ADMISSION_DENIED` | Zone 准入被拒 | 交易拒绝 + 引导准入流程 |
| `POLICY_EVALUATION_ERROR` | 策略评估错误 | 交易暂停 + 人工审核 |

## 附录 C: 合规交易类型

| Tx Type | 名称 | 用途 |
|---------|------|------|
| `0x76` | AA Transaction | 账户抽象交易 (WebAuthn/P-256 签名) |
| `0x77` | Compliance Transaction | 携带 KYC 凭证的合规交易 (身份注册/更新) |
| `0x78` | Privacy Transaction | 携带 ZK 证明的隐私交易 (凭证验证无需暴露数据) |

---

*本文档由 WHI-360 任务自动生成，基于 WHI-355 叙事分析、WHI-357 架构蓝图、以及 M1/M2 阶段的 Tempo、Canton、Prividium 调研成果综合设计。*
