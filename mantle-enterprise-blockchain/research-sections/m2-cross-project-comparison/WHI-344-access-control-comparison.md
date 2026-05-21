# WHI-344: 横向对比 — 权限控制与准入机制对比分析

> **Issue**: WHI-344 — 横向对比：权限控制与准入机制对比分析  
> **Milestone**: M2: Horizontal Comparisons  
> **Date**: 2026-05-06  
> **Status**: In Review  
> **Input Sources**: WHI-334, WHI-335, WHI-336 (Canton); WHI-337, WHI-338 (Prividium); WHI-339, WHI-340 (Tempo/Zones); Mantle V2 Baseline

---

## 目录

1. [Access Control Layer Model — 分层访问控制对比](#1-access-control-layer-model--分层访问控制对比)
2. [Identity Model Comparison — 身份模型对比](#2-identity-model-comparison--身份模型对比)
3. [Governance Model Comparison — 治理模型对比](#3-governance-model-comparison--治理模型对比)
4. [Enterprise IAM Integration — 企业身份管理集成分析](#4-enterprise-iam-integration--企业身份管理集成分析)
5. [Implications for Mantle — Mantle 访问控制架构建议](#5-implications-for-mantle--mantle-访问控制架构建议)

---

## 1. Access Control Layer Model — 分层访问控制对比

不同项目在不同架构层实现访问控制，其设计哲学和实现深度差异显著。以下按 Network → Consensus → Transaction → Contract → Data 五层模型进行对比。

### 1.1 分层对比总表

| Layer | Canton | Prividium | Tempo/Zones | Mantle (baseline) |
|-------|--------|-----------|-------------|-------------------|
| **Network** | 许可制 gRPC 通信。Participant 通过 TLS 认证端点连接 Synchronizer；应用层无开放式 P2P gossip。需注意：若启用 BFT Sequencer，其排序层节点之间仍使用独立的 P2P gRPC 网络。**[WHI-334 §3.3; WHI-336 §2.4, §8.1]** | 私有子网部署。Sequencer 和数据库部署在无互联网暴露的专用子网中，仅 Proxy RPC 公开暴露在 DMZ 层。标准 RPC 端点必须通过防火墙限制访问。**[WHI-337 §3.4; WHI-338 §3.2]** | **Tempo L1**: Commonware 认证 P2P 网络（ed25519 节点身份）。**Zones**: 无 P2P 网络（单 Sequencer 架构，Zone 节点通过 L1 事件驱动）。**[WHI-339 §2.1; WHI-340 §3.2]** | 无许可。标准 OP Stack P2P 网络（libp2p），任何节点可连接；标准 JSON-RPC 默认对任何可达客户端开放。**[WHI-341 §2.1, §8.1]** |
| **Consensus** | 许可制 2PC 协议。Mediator 协调两阶段提交，仅持有 Confirmation 权限的 Participant 可参与交易确认。BFT Sequencer 可选（2/3 多数拜占庭容错），支持去中心化 Mediator（阈值投票裁决）。**[WHI-334 §3.4; WHI-335 §1.2]** | 单 Sequencer 运营。状态转换正确性由 ZK 证明保障，但排序/准入本身不由拜占庭多方共识保护。Sequencer 排序后由 Prover Farm 生成 STARK 证明。**[WHI-337 §3.7; WHI-338 §2.3, §3.6]** | **Tempo L1**: 许可制验证者集合。BLS12-381 阈值签名，Simplex BFT 共识（~600ms 出块），VRF leader 选择。通过 ValidatorConfig/ValidatorConfigV2 precompile 管理验证者。**Zones**: 单 Sequencer（NoopConsensus），由 L1 事件驱动出块。**[WHI-339 §2.1; WHI-340 §3.1, §3.4]** | 中心化单 Sequencer。`op-conductor` 提供 HA 故障转移（Raft 仅用于副本 leader election），而状态验证当前默认由 SP1 ZK Validity Proof 完成；仅在 `MantleSecurityMultisig` 切换回退模式时退化为 7 天 Optimistic 挑战期。**[WHI-341 §1.3, §3.9, §8.1]** |
| **Transaction** | 交易提交需要 Submission 权限（三级权限中最高级）。交易是否可提交同时受 Daml 授权、Party-Participant 拓扑映射和 Package Vetting 约束。**[WHI-335 §1.5.2-§1.5.5; WHI-336 §4.4]** | **四层纵深防御**中的 Layer 2: Proxy RPC 三步验证（JWT → 钱包地址 → 合约函数权限检查）。所有常规交易必须通过 Proxy RPC 这一唯一入口。Layer 4: PrividiumTransactionFilterer 合约拦截 L1→L2 强制交易（白名单机制，非白名单仅可转移 ETH/ERC-20）。Multicall 被主动阻止。**[WHI-337 §3.4; WHI-338 §3.2, §3.4]** | **Tempo L1**: 常规交易提交本身仍沿用 EVM 账户模型；**合规准入主要体现在资产转账和 Zone 入口**。TIP-403 Policy Registry precompile（地址 `0x403c...`）为 TIP-20 转账定义 always-reject / always-allow / whitelist / blacklist 等策略；Zone 侧通过认证 RPC 和入金时的 TIP-403 检查控制访问。**[WHI-339 §3.1, §3.2; WHI-340 §3.5, §7.6]** | 无许可。任何地址可提交交易。Tx pool 仅做基本有效性校验（nonce、余额、gas）。**[WHI-341 §8.1, §10.1]** |
| **Contract** | **Daml Template 授权模型**（编译时强制）。Signatories 必须授权合约创建；合约归档时 Signatories 被通知；只有 Controller 可行使 Choice。授权规则编码在 Template 中，编译为 Daml-LF 字节码，Participant 的 Daml Engine 确定性执行时自动验证。义务需同意（Party 不能在未授权时被绑定），权利不能被单方移除。**[WHI-334 §3.6.2, §3.6.3]** | **RBAC 六种权限类型**（Admin Dashboard 配置）。所有合约函数默认为 Forbidden。部署后由管理员逐个配置：Forbidden / All Users / Check Role / Restrict Argument / Check Role AND Restrict Argument / Check Role OR Restrict Argument。权限在 `eth_call`（读）和执行（写）时均检查。**[WHI-337 §3.4.4; WHI-338 §3.3]** | **TIP-20 precompile 内置合规检查**。每个 TIP-20 token 转账自动调用 `transferAuthorized()` 检查 TIP-403 策略。Zone 内通用合约创建被禁止（`CREATE` / `CREATE2` 被阻止）。AccountKeychain 的 access key 支持 `CallScope`（限定可调用的合约和函数选择器）。**[WHI-339 §3.1; WHI-340 §7.1, §7.3]** | 无内置合约级访问控制。合约权限由 Solidity 代码自行实现（如 OpenZeppelin AccessControl）。**[Mantle Baseline §5.1]** |
| **Data** | **子交易级隐私（need-to-know）**。Merkle DAG 结构确保每个 Participant 仅看到自己有权查看的子树。Sequencer 仅看到加密后的 opaque 消息（不可读取交易内容）。Mediator 仅知道哪些 Participant 需确认及其确认/拒绝状态。Informee/Witness 规则精确控制每个 action 的可见性。**[WHI-334 §3.5; WHI-335 §1.2]** | **链级隐私 + RBAC 可见性控制**。L1 上仅可见状态根和 STARK 证明（无交易数据、地址或 calldata）。链内通过 RBAC 角色控制数据可见性。私有区块浏览器根据用户角色展示不同级别数据（Admin/Auditor/Trader/Public 四种视图）。Merkle 证明导出支持选择性披露。**[WHI-337 §3.6; WHI-338 §2.4, §4]** | **Zone 认证 RPC**。访问 Zone 数据需签名授权 token（secp256k1 签名，含 version/zoneId/chainId/issuedAt/expiresAt，最长有效期 30 天）。Zone 内隐私措施：`balanceOf` 仅可由 `msg.sender` 查询自身余额；区块数据经消毒（transactions 数组清空，logsBloom 归零）；RPC 固定 100ms 最短响应时间（防时序侧信道）；固定 100,000 gas 用于用户操作（防 gas 侧信道）。加密存款使用 ECIES（secp256k1 + AES-256-GCM）隐藏接收方地址。**[WHI-339 §3.2, §3.3; WHI-340 §3.6, §7.2]** | 完全公开。所有 L2 交易数据以 blob/calldata 形式发布到 L1，任何人可从 L1 数据推导完整 L2 状态。标准 JSON-RPC 无访问控制。**[Mantle Baseline §5.1, §6.1]** |

### 1.2 分层深度分析

#### 1.2.1 设计哲学对比

三个项目代表了三种截然不同的访问控制设计哲学：

| 项目 | 设计哲学 | 核心机制 | 优势 | 局限 |
|------|---------|---------|------|------|
| **Canton** | **协议原生**（Protocol-native）— 访问控制内嵌于共识协议和智能合约语言中 | Daml 授权模型 + 2PC 权限 + Merkle DAG 隐私 | 编译时安全保证；最小化信息暴露面；不依赖外部系统 | 需学习专用 DSL（Daml）；EVM 不兼容；生态系统较小 |
| **Prividium** | **纵深防御**（Defense-in-depth）— 多层叠加的访问控制，从网络边界到合约内部 | SSO → Proxy RPC → RBAC → L1 TransactionFilterer | 与企业 IAM 原生集成；EVM 兼容；细粒度函数级权限 | 权限配置全部离链（Admin Dashboard），非链上强制；单运营商信任 |
| **Tempo/Zones** | **precompile 原生**（Precompile-native）— 在 EVM 执行层通过 precompile 强制合规 | TIP-403 策略注册表 + AccountKeychain + Zone 隔离 | EVM 兼容且链上强制；策略动态可更新；Zone 多租户隔离 | precompile 是硬编码的；合规检查增加 gas 成本；Zone 的 Sequencer 全知 |

**[综合分析]**：Canton 的访问控制最深（语言、拓扑与确认流程联动），Prividium 的覆盖面最广（从 SSO 到 L1 边界的纵深防御），Tempo 的链上合规最强（TIP-403/AccountKeychain），但其 Zone 侧很多保证在 prover 上线前仍有一部分依赖 Sequencer 诚实执行。

#### 1.2.2 L1→L2 强制交易防护对比

这是企业许可链的关键安全问题——在基于 Ethereum 的 L2 架构中，L1 上任何人都可发起强制交易绕过 L2 访问控制：

| 项目 | 防护方案 | 安全等级 |
|------|---------|---------|
| **Canton** | 不适用——Canton 不是 Ethereum L2，无 L1 强制交易路径 | N/A |
| **Prividium** | `PrividiumTransactionFilterer` 合约：白名单地址可执行不受限的强制交易；非白名单仅可转移 ETH/ERC-20。**[WHI-337 §3.4.3; WHI-338 §3.4]** | 高（合约级强制） |
| **Tempo/Zones** | Zone 的 L1→L2 入金通过 ZonePortal 合约，Sequencer 在 `prepare_l1_block()` 中对解密后的接收方地址执行 TIP-403 合规检查，不合规存款退回（bounce back）。该保护在 Zone prover 上线前属于 Sequencer 可信执行点，而非已完全 proof-covered 的保证。**[WHI-339 §3.6, §5.2; WHI-340 §7.5, §9 Step 4]** | 中高（Sequencer 级强制，prover 上线前非纯密码学） |
| **Mantle** | 无防护。L1 上的 OptimismPortal 合约接受任何存款。**[Mantle Baseline §2.6]** | 无 |

**[分析]**：Prividium 和 Tempo 都解决了这一关键问题，但方案不同：Prividium 在 L1 合约层拦截（白名单准入），Tempo 在 L2 Sequencer 层拦截（策略检查后退回不合规存款）。对 Mantle 而言，两种方案都可参考——L1 合约过滤器更前置但灵活性较低，Sequencer 层检查更灵活但依赖 Sequencer 诚实。

---

## 2. Identity Model Comparison — 身份模型对比

### 2.1 身份模型对比总表

| Dimension | Canton | Prividium | Tempo/Zones | Mantle (baseline) |
|-----------|--------|-----------|-------------|-------------------|
| **Identity system** | **X.509/PKI 密码学身份**。Namespace 由自签名根证书定义，密钥指纹即为 namespace 标识符。UID = identifier + namespace（如 `jane_doe::abc123`）。密码学身份与法律身份分离——系统有效性不依赖真实身份映射。**[WHI-334 §6.2; WHI-335 §1.3]** | **SSO 集成身份（Okta OIDC / SIWE / Hybrid）**。OIDC 用户通过 OAuth 2.0/OIDC subject ID 标识；SIWE 用户通过钱包签名认证；混合用户支持任一方式认证且映射到同一用户记录。JWT 令牌承载身份和角色声明。**[WHI-337 §3.4.1; WHI-338 §3.1]** | **AccountKeychain precompile（WebAuthn/P256 + 传统 EOA）**。precompile 地址 `0xAAAAAAAA...`。支持 root key → access key 委托。签名类型通过长度自动检测：65 = secp256k1，130 = P256，可变长度 = WebAuthn。P256（Passkey/WebAuthn）为一等公民签名方案。**[WHI-339 §3.4; WHI-340 §7.3]** | **仅地址身份**。Mantle baseline 直接沿用 secp256k1 地址模型，无原生身份层、无企业目录映射、无 KYC 注册表。**[WHI-341 §8.1]** |
| **Identity-address relationship** | **Party-Participant 多对多映射**。一个 Party 可被多个 Participant Node 承载（Multi-hosting），一个 Participant 可承载多个 Party。Local Party（有 SPN，密钥由节点管理）与 External Party（无 SPN，自行控制密钥）支持不同信任模型。去中心化 Party（threshold > 1）需多节点阈值确认。**[WHI-334 §3.1; WHI-335 §1.3]** | **用户-钱包一对多映射**。单个用户可关联多个钱包地址，所有关联钱包继承相同的 RBAC 权限。身份管理（users）与访问控制（roles/permissions）独立分离。**[WHI-337 §3.4.1; WHI-338 §3.1]** | **AccountKeychain 多键绑定**。Root key 可委托 access key，access key 具有 `KeyAuthorization` 结构：`CallScope`（限定可调用的合约和函数选择器）、`TokenLimit`（每 token 支出限额，周期性重置）、过期时间戳。**[WHI-339 §3.4; WHI-340 §7.3]** | **一地址一密钥为默认模型**。若要支持企业身份，需要新增身份注册 predeploy/合约或链下目录服务。**[WHI-341 §8.1, §10.3]** |
| **Identity revocability** | **拓扑事务 REMOVE 操作**。通过 REMOVE 操作广播 namespace 委托撤销。含序列号（防重放）、多方签名支持。撤销不影响已验证的历史交易。三级委托权限控制撤销范围：CanSignAllMappings / CanSignAllButNamespaceDelegations / CanSignSpecificMappings。**[WHI-334 §6.2; WHI-336 §2.3]** | **Admin Dashboard 管理**。管理员通过 Prividium API 禁用/删除用户或移除钱包关联。至少需两个 Admin 用户以防锁定。撤销后用户的 JWT 失效，无法通过 Proxy RPC 认证。**[WHI-337 §3.4.1; WHI-338 §3.1]** | **TIP-403 blacklist 即时生效**。将地址加入 blacklist 策略后，该地址的后续 TIP-20 交易在策略检查中被拒绝。Zone 中策略传播在 prover 上线前仍由 Sequencer 驱动，不能等同于已完全由 validity proof 覆盖。**[WHI-339 §3.6; WHI-340 §7.5, §11.1]** | **无原生撤销层**。只能依赖账户迁移、合约级黑名单或上层策略引擎补救。**[WHI-341 §8.1, §10.1, §10.3]** |
| **Anonymous/pseudonymous support** | **原生假名支持**。密码学身份与法律身份分离是核心设计。UID 中的 identifier 可以是任意标识符，namespace 是密钥指纹——不包含真实身份信息。合规映射需要链下机制。**[WHI-334 §6.2; 设计决策 §4.7]** | **不支持匿名**。所有用户必须经过 SSO 认证（Okta OIDC 或 SIWE），钱包地址绑定到已知身份。这是设计目标——"未通过身份验证和授权的用户从物理上无法与链交互"。**[WHI-337 §3.5; WHI-338 §3.1]** | **Zone 加密存款支持接收方隐匿**。存款使用 ECIES（secp256k1 + AES-256-GCM）加密 `(to, memo)`，仅 Sequencer 可解密。Zone 内提款支持 `revealTo` 选择性跨 Zone 发送方归因。需要强调：Zone Sequencer 仍拥有全量可见性。**[WHI-339 §3.3, §3.5; WHI-340 §11.2, §11.4]** | **仅地址假名**。地址默认不绑定法律身份，但所有交易和状态完全公开，无法提供企业场景常需的受控匿名。**[WHI-341 §8.1, §9.1]** |
| **KYC integration method** | **链上凭证合约**（KYCCredential template）。KYC 通过 Daml 合约模型实现，可作为交易的前置条件。Canton Network 参与者（如 Goldman Sachs、HSBC 等）通过链下 KYC 流程后获得链上凭证。**[WHI-334 §5, §6.4]** | **链级身份绑定 + SSO 联邦**。每个钱包地址与经认证的身份（OIDC subject ID 或 SIWE 签名）绑定。KYC/AML 嵌入资产逻辑——是"系统属性"而非外挂层。利用企业现有 Okta/AD 基础设施实现身份验证和 MFA。ZK 驱动的合规创新：无 PII 存储的制裁筛查。**[WHI-337 §3.5; WHI-338 §3.1, §4]** | **TIP-403 策略注册表 + Zone Sequencer 合规角色**。TIP-403 的 whitelist 策略本质上是地址级 KYC 许可列表——仅白名单地址可进行 TIP-20 转账。Zone Sequencer 负责在入金路径执行策略检查。**[WHI-339 §3.1, §3.6; WHI-340 §3.5, §7.4]** | **无原生 KYC**。需新增身份注册 predeploy、认证网关或合约级 allowlist 才能把 KYC 状态与地址绑定。**[WHI-341 §8.1, §10.3]** |

### 2.2 身份模型架构对比

```
Canton:                         Prividium:                       Tempo/Zones:
┌──────────────────┐           ┌──────────────────┐            ┌──────────────────┐
│  Legal Identity  │           │  Legal Identity  │            │  Legal Identity  │
│  (off-chain)     │           │  (Okta/AD SSO)   │            │  (off-chain)     │
└────────┬─────────┘           └────────┬─────────┘            └────────┬─────────┘
         │ 链下映射                      │ OIDC/SIWE                     │ 链下映射
┌────────▼─────────┐           ┌────────▼─────────┐            ┌────────▼─────────┐
│  Crypto Identity │           │  JWT Bearer Token│            │  EOA / P256 Key  │
│  (X.509/PKI)     │           │  (身份+角色声明)  │            │  (secp256k1/P256)│
│  namespace::id   │           └────────┬─────────┘            └────────┬─────────┘
└────────┬─────────┘                    │                               │
         │                     ┌────────▼─────────┐            ┌────────▼─────────┐
┌────────▼─────────┐           │  Wallet Address  │            │  AccountKeychain │
│  Party + UID     │           │  (多钱包绑定)     │            │  (root→access    │
│  (多 Participant │           └──────────────────┘            │   key 委托)      │
│   可承载)        │                                           └────────┬─────────┘
└──────────────────┘                                                    │
                                                               ┌────────▼─────────┐
                                                               │  TIP-403 Policy  │
                                                               │  (whitelist/     │
                                                               │   blacklist)     │
                                                               └──────────────────┘
```

**[综合分析]**：

- **Canton** 的身份模型最为独立——密码学身份与法律身份完全分离，系统有效性不依赖真实身份。这提供了最强的隐私保护，但 KYC 合规需要额外的链下机制。
- **Prividium** 的身份模型与企业 IAM 集成最深——直接复用 Okta/AD，零额外身份系统建设成本。但这也意味着最强的身份绑定（不支持匿名）。
- **Tempo** 的身份模型最具创新性——AccountKeychain 将 WebAuthn/Passkey 作为一等公民，支持细粒度的 access key 委托（含支出限额和合约调用范围限制）；但身份到法律主体的映射仍需链下治理。
- **Mantle baseline** 几乎没有身份层，只提供最基础的地址假名模型。因此在企业场景下，身份、撤销和 KYC 都不是“配置打开”，而是需要新增系统组件。

---

## 3. Governance Model Comparison — 治理模型对比

### 3.1 验证者集合变更

| Dimension | Canton | Prividium | Tempo/Zones | Mantle (baseline) |
|-----------|--------|-----------|-------------|-------------------|
| **验证者/排序者角色** | Sequencer（排序）+ Mediator（2PC 确认），角色分离。**[WHI-335 §1.2]** | 单 Sequencer（运营商控制），ZK 证明保证正确性。**[WHI-338 §1.1]** | **Tempo L1**: ValidatorConfig/ValidatorConfigV2 precompile 管理验证者集合。**Zones**: 单 Sequencer，NoopConsensus。**[WHI-340 §3.1]** | 单一 Sequencer；`op-conductor` 只负责副本级 HA 和 leader election，不构成去中心化验证者集合。**[WHI-341 §3.9, §7]** |
| **变更机制** | Synchronizer 运营者通过拓扑事务管理 Sequencer/Mediator 成员。DecentralizedNamespaceDefinition 支持多方共有（threshold > 1）。去中心化 Mediator 通过阈值投票裁决。去中心化 Sequencer 运行在 BFT 排序层上。**[WHI-334 §3.2]** | 运营商单方控制。Sequencer 由链运营方管理，无链上治理机制用于 Sequencer 变更。**[WHI-337 §2; WHI-338 §1.2]** | ValidatorConfig precompile 管理链上验证者注册。BLS12-381 阈值签名验证者参与 Simplex BFT 共识。验证者变更通过 precompile 调用执行。**[WHI-339 §2.1; WHI-340 §3.1]** | 运行层由运维控制 Sequencer 副本，协议层关键模式切换和核心升级由 `MantleSecurityMultisig` 与 L1 系统合约控制。**[WHI-341 §1.3, §7, §8.1]** |
| **多方同意要求** | 去中心化 Synchronizer 需 threshold 数量的管理者同意。Super Validators（Global Synchronizer）通过链上治理应用协调。**[WHI-334 §3.7]** | 无多方同意要求——单运营商决策。**[WHI-338 §1.2]** | 验证者集合变更需通过 ValidatorConfig precompile 的权限控制（具体阈值机制需进一步研究，M1 文档未详细说明变更的多签要求）。**[WHI-340 §3.1]** | 关键模式切换由 `MantleSecurityMultisig` 6/14 多签控制；但当前缺少时间锁，因此属于“有多签、弱延迟保护”的治理。**[WHI-341 §1.3, §9.1]** |

### 3.2 规则/策略变更

| Dimension | Canton | Prividium | Tempo/Zones | Mantle (baseline) |
|-----------|--------|-----------|-------------|-------------------|
| **权限策略升级** | 拓扑事务系统。权限变更通过含序列号的拓扑事务广播，支持 REPLACE/REMOVE 操作，需授权密钥签名。三级委托权限控制变更范围。**[WHI-334 §6.2]** | Admin Dashboard 配置。管理员通过 Prividium API 更新 RBAC 权限配置。所有变更通过管理员角色执行，至少两个 Admin 用户以防锁定。**[WHI-337 §3.4.4; WHI-338 §3.3]** | **双轨机制**: (1) **TIP-403 策略动态更新** — 链上 precompile 调用即时生效，无需硬分叉；(2) **协议级变更通过硬分叉序列** — 已执行 T0→T1→T1A→T1B→T1C→T2→T3→T4→T5 共 10 个变种。**[WHI-339 §2.3; WHI-340 §3.1]** | 无原生权限策略层。若要做企业准入，需要自行新增 predeploy、Sequencer policy engine 或 RPC gateway。协议升级本身通过 deposit transaction 和系统合约完成。**[WHI-341 §8.1, §10.1, §10.3]** |
| **升级治理流程** | 每个 Synchronizer 可独立配置治理流程。Global Synchronizer Foundation (GSF，与 Linux Foundation 合作) 管理全局治理。**[WHI-334 §3.7.4]** | 运营商单方升级。运营商对合约和 RBAC 配置拥有完全控制权。**[WHI-338 §1.2]** | Tempo L1 硬分叉由协议开发者驱动，通过 chainspec 中的时间戳激活。TIP-403 策略变更可由策略管理者通过 precompile 调用链上执行。**[WHI-340 §3.1, §7.1]** | 通过 L1 deposit 交易与系统合约升级实现。`MantleSecurityMultisig` 可即时升级核心合约并切换 ZK/Optimistic 模式，当前缺少退出窗口。**[WHI-341 §7, §9.1]** |

### 3.3 紧急操作

| Dimension | Canton | Prividium | Tempo/Zones | Mantle (baseline) |
|-----------|--------|-----------|-------------|-------------------|
| **冻结/撤销** | 密钥撤销通过 REMOVE 拓扑事务。Synchronizer 运营者可拒绝 Participant 连接（断开 gRPC 连接）。不影响已验证的历史交易。**[WHI-334 §6.2]** | Admin 通过 Dashboard 禁用用户/移除钱包。JWT 失效后用户无法通过 Proxy RPC。PrividiumTransactionFilterer 可立即阻止 L1→L2 路径。**[WHI-337 §3.4; WHI-338 §3.1, §3.4]** | **TIP-403 blacklist 即时生效**。将地址加入 blacklist 后，该地址的后续所有 TIP-20 转账被拒绝。Zone 中 TIP-403 镜像自动同步——L1 blacklist 变更在下一个 L1 区块处理时传播到 Zone。**[WHI-339 §3.1; WHI-340 §3.5]** | **无原生冻结工具**。需要依靠多签升级、Sequencer 过滤器、合约暂停开关或上层 allowlist/blacklist 机制实现。**[WHI-341 §8.1, §9.1, §10.1]** |
| **响应速度** | 依赖拓扑事务广播到所有相关 Synchronizer 的时间。断开 gRPC 连接可立即生效。**[WHI-334 §6.2]** | JWT 失效 = 即时阻止新请求。已在进行中的交易不受影响。**[WHI-338 §3.1]** | **接近即时**。TIP-403 blacklist 变更在 precompile 存储更新后的下一次 `isAuthorized` 调用即生效。Zone 镜像延迟约为一个 L1 区块处理周期；但 Zone 路径的强制性在 prover 上线前仍部分依赖 Sequencer 诚实执行。**[WHI-339 §3.6; WHI-340 §3.5, §7.5]** | 取决于企业自己扩展的控制层是否预先部署；baseline 本身不提供针对地址或身份的快速冻结路径。**[WHI-341 §8.1, §10.1]** |

### 3.4 多租户支持

| Dimension | Canton | Prividium | Tempo/Zones | Mantle (baseline) |
|-----------|--------|-----------|-------------|-------------------|
| **多企业隔离** | **原生多 Synchronizer 架构**。每个 Synchronizer 可有独立的治理、权限、性能配置和成本模型。不同 Synchronizer 服务于不同监管辖区/应用场景。Participant 可同时连接多个 Synchronizer，合约通过 Reassignment 跨 Synchronizer 转移。**[WHI-334 §3.2]** | **单链 = 单租户**。每个企业部署自己的 Prividium 链。多租户需部署多条独立的 Prividium 链，通过 ZKsync Gateway / ZKsync Connect 跨链桥接。**[WHI-338 §1.3]** | **原生多 Zone 部署**。`ZoneFactory.createZone()` 支持程序化创建新 Zone。每个 Zone 拥有独立的状态、RPC 认证（`zone_id` 字段，0 = unscoped）、Sequencer 加密密钥和 TIP-403 策略。多个互不信任的企业可使用同一 Tempo L1 但各自拥有独立 Zone。**[WHI-339 §3.6; WHI-340 §7.5]** | **无原生多租户隔离层**。若要服务多个企业，需在同一链上构建应用级隔离，或在 Mantle L2 之上叠加企业专属 L3/rollup。**[WHI-341 §8.1, §10.3, §10.4]** |
| **跨租户交互** | 通过 Reassignment 跨 Synchronizer 转移合约（非原子，两阶段：Unassign + Assign）。Global Synchronizer 提供共同协调点，但现有 M1 资料并不支持“原子跨 Synchronizer 交易已实现”的结论。**[WHI-335 §1.4; WHI-336 §5]** | 通过 ZKsync Connect 跨链结算。原子性和隐私保护的跨链交互主要来自产品文档声明，公开实现细节仍有限。**[WHI-337 §3.7; WHI-338 §5, §12]** | Zone 之间通过 Tempo L1 的 ZonePortal 合约交互。存款/提款流经 L1 合约。TIP-403 策略在 L1 定义后自动镜像到所有 Zone。**[WHI-339 §3.6; WHI-340 §5]** | baseline 无跨租户框架；若采用 L3/多 rollup 方案，跨租户交互需额外设计桥接、共享排序或共享身份层。**[WHI-341 §10.3, §10.4]** |

**[综合分析]**：

- **Canton** 和 **Tempo/Zones** 提供原生的多租户隔离架构，适合需要在同一基础设施上服务多个独立企业的场景。Canton 通过 Synchronizer 实现，Tempo 通过 Zone 实现——两者的共同点是每个租户拥有独立的状态和治理空间。
- **Prividium** 的"一链一租户"模型更简单但更重——每个企业需要独立的链基础设施部署（Sequencer、Prover、数据库）。ZKsync Gateway 的共享结算层和 ZKsync Connect 跨链协议提供了跨租户交互能力，但需要额外的基础设施协调。
- 对 Mantle 而言，Tempo 的 ZoneFactory 模式最具参考价值——它在单个 L1 上创建多个隔离的 L2 环境，类似于在 Mantle L2 之上创建企业专属 L3。

---

## 4. Enterprise IAM Integration — 企业身份管理集成分析

企业拥有成熟的 Identity & Access Management (IAM) 系统（Active Directory、Okta、Azure AD 等）。区块链访问控制与企业 IAM 的集成深度直接影响企业的采纳成本。

### 4.1 集成模式对比

| 集成模式 | 描述 | 代表项目 | 集成深度 | 企业采纳成本 |
|---------|------|---------|---------|-----------|
| **API Gateway 级集成** | 在区块链 RPC 前置 API 网关，由网关执行 IAM 认证/授权 | **Prividium** Proxy RPC | 浅（网关层拦截，链不感知身份） | 最低——复用现有 API 网关基础设施 |
| **合约/Precompile 级集成** | 通过链上合约或 precompile 存储和执行身份/权限规则 | **Tempo** TIP-403 + AccountKeychain | 中（链上策略，但身份映射在链下） | 中等——需开发链上合约和链下身份映射 |
| **协议原生集成** | 身份和权限内嵌于协议和智能合约语言中 | **Canton** Daml 授权模型 | 最深（编译时强制） | 最高——需要全新的开发范式（Daml 语言） |

### 4.2 Prividium — API Gateway 级集成（最直接的企业 IAM 桥接）

**[WHI-337 §3.4.1; WHI-338 §3.1]**

```
企业 IAM 系统                    Prividium 访问控制
┌──────────────┐                ┌──────────────────────────┐
│  Okta / AD   │  OIDC Token   │  Proxy RPC               │
│  ┌────────┐  │ ──────────►   │  ┌──────────────────┐    │
│  │  Users │  │                │  │ Step 1: JWT 验证  │    │
│  │  Groups│  │                │  │ Step 2: 地址验证  │    │
│  │  MFA   │  │                │  │ Step 3: 权限检查  │    │
│  └────────┘  │                │  └──────────────────┘    │
└──────────────┘                └──────────────────────────┘
```

**核心优势**：
- **零额外身份系统建设**——直接利用企业现有 Okta/AD 基础设施
- **熟悉的 RBAC 模型**——Admin/Trader/Auditor/Operator 角色直接映射到企业组织结构
- **MFA 集成**——Okta 的 MFA 能力自动继承
- **SSO 联邦**——用户使用企业 SSO 凭证，无需管理额外密码

**核心局限**：
- **Proxy RPC 是单点故障/单点信任**——所有访问控制逻辑集中在 Proxy RPC，绕过它（如 L1 强制交易）则需要 PrividiumTransactionFilterer 兜底
- **权限配置不在链上**——RBAC 规则存储在 Prividium API 后端而非智能合约中，无法被链上逻辑引用
- **Multicall 限制**——为安全而阻止 Multicall，降低了 DeFi 组合性

### 4.3 Tempo — Precompile 级集成（链上强制 + 链下身份桥接）

**[WHI-339 §3.4; WHI-340 §7.3]**

```
企业 IAM 系统                    Tempo 访问控制
┌──────────────┐                ┌──────────────────────────┐
│  Enterprise  │  链下映射       │  链上 Precompile          │
│  IAM         │ ──────────►   │  ┌──────────────────┐    │
│  ┌────────┐  │  地址↔身份      │  │ TIP-403 Registry │    │
│  │ WebAuthn│  │  白名单维护     │  │ (whitelist/      │    │
│  │ Passkey │  │                │  │  blacklist)       │    │
│  │ P256    │  │                │  ├──────────────────┤    │
│  └────────┘  │                │  │ AccountKeychain   │    │
└──────────────┘                │  │ (access key       │    │
                                │  │  delegation)      │    │
                                │  └──────────────────┘    │
                                └──────────────────────────┘
```

**核心优势**：
- **WebAuthn/Passkey 原生支持**——AccountKeychain 将 P256 签名作为一等公民，WebAuthn 可直接桥接企业 FIDO2 基础设施
- **链上策略强制**——TIP-403 策略存储在 precompile 中，TIP-20 转账路径会自动调用；但 Zone 镜像与 Zone 入金路径在 prover 上线前仍不能等同于“纯密码学、零信任”的执行保证
- **细粒度 access key 委托**——`KeyAuthorization` 支持 `CallScope`（限定合约和函数）+ `TokenLimit`（支出限额）+ 过期时间，可映射到企业的审批层级
- **Zone 级 RPC 认证**——授权 token 含 `zone_id`，支持多 Zone 的差异化认证

**核心局限**：
- **身份-地址映射在链下**——TIP-403 本身只管理地址级白名单/黑名单，不存储身份信息。身份与地址的映射需要链下系统管理
- **白名单维护成本**——大规模企业部署需要持续维护大量地址的白名单状态
- **无原生 OIDC/SAML 集成**——需要自行开发 IAM 到 TIP-403 的桥接层

### 4.4 Canton — 协议原生集成（最深但成本最高）

**[WHI-334 §3.1, §3.6.3, §6.2; WHI-335 §1.3]**

```
企业 IAM 系统                    Canton 访问控制
┌──────────────┐                ┌──────────────────────────┐
│  Enterprise  │  链下映射       │  协议原生                  │
│  PKI / CA    │ ──────────►   │  ┌──────────────────┐    │
│  ┌────────┐  │  X.509 证书    │  │ Namespace (PKI)  │    │
│  │  CA    │  │  namespace     │  │ (自签名根证书)    │    │
│  │  LDAP  │  │  委托          │  ├──────────────────┤    │
│  │  HSM   │  │                │  │ Party-Participant│    │
│  └────────┘  │                │  │ Mapping          │    │
└──────────────┘                │  ├──────────────────┤    │
                                │  │ Daml Template    │    │
                                │  │ (Signatory/      │    │
                                │  │  Observer/       │    │
                                │  │  Controller)     │    │
                                │  └──────────────────┘    │
                                └──────────────────────────┘
```

**核心优势**：
- **编译时安全保证**——授权规则编码在 Daml Template 中，不可能被运行时绕过
- **PKI 与企业 CA 自然对接**——X.509 证书体系与企业 PKI 基础设施无缝集成
- **Party 抽象与法律身份分离**——提供最强的隐私保护，同时支持链下合规映射
- **最小权限原则**——Sequencer 看不到交易内容，Mediator 看不到合约状态

**核心局限**：
- **需要学习全新语言**——Daml 是 Haskell 风格的 DSL，学习曲线陡峭
- **非 EVM 兼容**——无法使用 Solidity 生态系统（Polyglot Canton 白皮书已发布但未实现）
- **生态系统较小**——开发者社区和工具链远小于 EVM 生态

### 4.5 IAM 集成推荐路径

对于计划基于 EVM 兼容链（如 Mantle）构建企业访问控制的场景：

| 推荐优先级 | 集成模式 | 参考项目 | 实施路径 |
|-----------|---------|---------|---------|
| **1（快速起步）** | RPC 层 API Gateway | Prividium Proxy RPC | 在 Mantle RPC 前置认证网关，接入企业 Okta/AD，实现 JWT 验证 + 地址绑定 |
| **2（增强安全）** | Predeploy 合约策略注册表 | Tempo TIP-403 | 在 Mantle 部署身份注册合约（predeploy），配合 Sequencer/Tx Pool 策略引擎 |
| **3（深度集成）** | Precompile 级 AccountKeychain | Tempo AccountKeychain | 为 Mantle op-geth 添加自定义 precompile，支持 WebAuthn/P256 和 access key 委托 |

---

## 5. Implications for Mantle — Mantle 访问控制架构建议

### 5.1 Mantle Sequencer 中心化优势的利用

**问题**：Mantle 的 Sequencer 已经是中心化的——能否将此作为访问控制的切入点？

**分析**：Tempo Zones 的架构恰好验证了"中心化 Sequencer + 合规层"的可行性：

| Tempo Zones 的 Sequencer 模式 | Mantle 的适用性 |
|------------------------------|----------------|
| Zone Sequencer = 单一排序者 + 合规执行者（NoopConsensus） | Mantle Sequencer 同样是单一排序者，可直接承担合规角色 |
| Sequencer 在 `prepare_l1_block()` 中执行 TIP-403 合规检查 | Mantle 可在 `op-node/rollup/sequencing/sequencer.go` 中添加类似策略检查 |
| Sequencer 拥有全部 Zone 状态的完全可见性 | Mantle Sequencer 同样拥有全部 L2 状态可见性 |
| Zone 的认证 RPC（签名授权 token） | Mantle 可在 op-geth RPC 层添加类似认证 |

**[WHI-340 §3.4, §7.4]**

**建议**：Mantle 的中心化 Sequencer 是企业访问控制的**天然切入点**。但这不是“零新增信任”——而是把企业合规信任显式叠加在已经中心化的排序角色之上。因此更稳妥的做法是把 Sequencer 过滤与链上注册表/合约检查组合使用，而不是只依赖 Sequencer 判断。

### 5.2 TIP-403 模式对 OP Stack 的可移植性

**问题**：Tempo 的 TIP-403 策略注册表模式是否可移植到 OP Stack？

**分析**：

| TIP-403 组件 | OP Stack 实现路径 | 难度 |
|-------------|-----------------|------|
| **策略注册表 precompile** | 选项 A: 作为 op-geth 自定义 precompile（需修改 EVM）<br>选项 B: 作为 L2 predeploy 合约（参照 L1Block、GasPriceOracle 模式） | A: High / B: **Medium** |
| **策略类型（whitelist/blacklist/compound）** | 纯 Solidity 实现即可，参照 Tempo 的四种策略类型和 TIP-1015 复合策略 | **Low** |
| **EVM 执行层强制** | 需在 op-geth `state_transition.go` 中添加 transfer hook，调用策略注册表检查 | **Medium-High** |
| **L1→L2 策略镜像** | OP Stack 已有 L1Block predeploy 的 L1→L2 数据通道，可复用该模式传递策略更新 | **Medium** |
| **Sequencer 策略缓存** | 参照 Tempo 的 `SharedPolicyCache` + per-block GC 模式 | **Medium** |

**[WHI-340 §7.1, §8.4]**

**建议**：采用 **Predeploy 合约**（选项 B）作为策略注册表，而非 Precompile。原因：
1. Predeploy 合约可通过 Mantle 的升级流程（deposit transaction）部署和升级，已有成熟模式（参照 `arsia_upgrade_transactions.go`）
2. 无需修改 EVM 核心逻辑，降低维护负担
3. 可用 Solidity 编写，利用现有开发工具
4. 代价：每次 transfer 额外一次 CALL 的 gas 开销，但对许可链场景可接受

### 5.3 RPC 层 vs EVM 执行层访问控制

**问题**：RPC 层访问控制是否足够？还是需要深入 EVM 执行层？

| 控制层级 | 能防御什么 | 不能防御什么 | 代表方案 |
|---------|----------|-----------|---------|
| **RPC 层** | 未授权的 RPC 请求；未认证用户的链交互 | L1→L2 强制交易；MEV 搜索者通过其他 RPC 端点提交的交易；合约间调用 | Prividium Proxy RPC; Tempo Zone 认证 RPC |
| **Sequencer 层** | 所有进入 tx pool 的交易；基于策略的交易过滤 | 已进入 tx pool 后的合约间调用；L1→L2 强制交易（除非 Sequencer 明确检查） | Tempo Zone Sequencer 合规检查 |
| **EVM 执行层** | 所有交易（包括 L1→L2 强制交易和合约间调用）；token transfer 级别的合规检查 | 无（最彻底，但实现成本最高） | Tempo TIP-403 + TIP-20 `transferAuthorized()`; Canton Daml 授权 |

**[WHI-337 §3.4; WHI-338 §3.2, §3.4; WHI-340 §3.5, §7.1]**

**建议**：对于企业许可链，**RPC 层不够**。至少需要 RPC + Sequencer 两层，最好加上 EVM 执行层的 token transfer hook：

1. **RPC 层**（必要 + 低成本）：认证网关过滤未授权请求，审计所有访问尝试
2. **Sequencer 层**（必要 + 中等成本）：策略引擎过滤不合规交易，防止 tx pool 污染
3. **EVM 执行层**（建议 + 高成本）：token transfer hook 检查合规状态，防御合约间调用和 L1 强制交易

### 5.4 Proxy RPC vs Authenticated Private RPC 模式对比

**问题**：Prividium 的 Proxy RPC 模型与 Tempo Zone 的认证 Private RPC 模型，哪个更适合 Mantle？

| 维度 | Prividium Proxy RPC | Tempo Zone 认证 RPC |
|------|--------------------|--------------------|
| **认证方式** | JWT Bearer Token（SSO 签发） | 签名授权 token（用户自签名，secp256k1） |
| **认证粒度** | 用户级（JWT 含身份+角色声明） | 地址级（授权 token 含 zoneId/chainId/expiry） |
| **有效期** | JWT 过期时间由 SSO 配置 | 最长 30 天（`DEFAULT_MAX_AUTH_TOKEN_VALIDITY_SECS = 2,592,000`） |
| **双端点** | `/rpc`（Bearer token）+ `/wallet/{token}`（URL 嵌入） | 单一 RPC 端点 + `x-authorization-token` header |
| **权限检查** | 3 步：JWT → 地址 → 函数级权限 | 1 步：签名验证 + zone_id 匹配 |
| **SSO 集成** | 原生 Okta OIDC + SIWE | 无原生 SSO（需自行桥接） |
| **隐私措施** | 无特殊 RPC 级隐私措施 | 100ms 最短响应时间；区块消毒；per-account 数据过滤 |
| **实现复杂度** | 中等（需部署 Proxy + API 后端） | 低（仅需 token 验证中间件） |

**[WHI-337 §3.4.2; WHI-338 §3.2; WHI-340 §3.6]**

**建议**：Mantle 应采用**混合模式**：

1. **对外接口**：采用 Prividium 的 Proxy RPC 模式——在 op-geth RPC 前置认证网关，集成企业 Okta/AD SSO。这利用了企业已有的 IAM 基础设施，降低采纳门槛。
2. **对内接口**（如果部署企业专属 L3 / Zone）：采用 Tempo 的认证 token 模式——用户自签名授权 token，无需中心化 SSO 依赖，更适合跨组织场景。
3. **RPC 隐私增强**：参考 Tempo 的隐私措施——100ms 最短响应时间、per-account 数据过滤——防止通过 RPC 时序和数据侧信道泄露信息。

### 5.5 推荐的 Mantle 企业访问控制分层架构

基于以上分析，推荐以下分层架构：

```
┌────────────────────────────────────────────────────────────────────┐
│  Layer 5: Enterprise IAM Integration (Prividium 模式)              │
│  Okta/AD SSO → JWT 签发 → API Gateway → 认证/授权/审计            │
│  参考: WHI-337 §3.4.1, WHI-338 §3.1                               │
├────────────────────────────────────────────────────────────────────┤
│  Layer 4: Authenticated RPC (Tempo Zone 模式)                     │
│  op-geth RPC 中间件 — 签名授权 token 验证                          │
│  per-account 数据过滤 + RPC 时序保护                               │
│  参考: WHI-340 §3.6                                                │
├────────────────────────────────────────────────────────────────────┤
│  Layer 3: Sequencer Policy Engine (Tempo Zone + Mantle 原生)      │
│  op-node sequencer.go — 策略引擎 hook                             │
│  op-geth tx pool — 基于 Identity Registry 的准入过滤              │
│  参考: WHI-340 §3.4, §7.4; Mantle Baseline §7.1, §7.4            │
├────────────────────────────────────────────────────────────────────┤
│  Layer 2: Compliance Registry Predeploy (TIP-403 移植)            │
│  Solidity 合约 @ 预留 predeploy 地址                               │
│  whitelist/blacklist/compound 策略 + isAuthorized() API           │
│  L1→L2 策略同步（复用 L1Block 通道）                               │
│  参考: WHI-340 §7.1, §8.4; Mantle Baseline §7.3                  │
├────────────────────────────────────────────────────────────────────┤
│  Layer 1: L1 Transaction Filter (Prividium 模式)                  │
│  OptimismPortal 扩展 — TransactionFilterer                        │
│  白名单地址准入 L1→L2 强制交易                                     │
│  参考: WHI-337 §3.4.3; WHI-338 §3.4                               │
└────────────────────────────────────────────────────────────────────┘
```

### 5.6 实施优先级建议

| 阶段 | 实施内容 | 难度 | 依赖 | 价值 |
|------|---------|------|------|------|
| **Phase 1** | RPC 认证网关（Proxy RPC 模式）+ 基础 Identity Registry predeploy | Medium | 无 | 快速实现基本准入控制；企业可用 SSO 认证访问链 |
| **Phase 2** | Sequencer 策略引擎 + Tx Pool 过滤 + L1 TransactionFilterer | Medium-High | Phase 1 Identity Registry | 完整的交易级访问控制；防御 L1 强制交易路径 |
| **Phase 3** | Token Transfer Hook（EVM 执行层合规检查）+ TIP-403 风格策略注册表 | High | Phase 2 Sequencer 策略 | 最彻底的合规执行；覆盖合约间调用 |
| **Phase 4（可选）** | AccountKeychain precompile（WebAuthn/P256）+ Zone-like L3 多租户 | Very High | Phase 3 | 企业级身份管理；多租户隔离 |

### 5.7 关键设计决策点

| 决策点 | 选项 A | 选项 B | 推荐 |
|-------|--------|--------|------|
| **策略注册表位置** | Precompile（Tempo 模式） | Predeploy 合约（OP Stack 模式） | **选项 B** — 可升级、Solidity 开发、已有部署模式 |
| **身份存储** | 链上合约 | 链下数据库 + 链上哈希承诺 | **混合** — 白名单存链上（快速链上查询），身份详情存链下（GDPR 合规） |
| **策略执行层** | 仅 Sequencer 层 | Sequencer + EVM 执行层 | **双层** — Sequencer 层快速拦截 + EVM 层兜底 |
| **RPC 模型** | Proxy RPC（中心化认证） | 签名授权 token（去中心化认证） | **Proxy RPC 优先**（企业 IAM 集成）+ **授权 token 选项**（跨组织场景） |
| **多租户方案** | 单链 RBAC（Prividium 模式） | L3 Zone（Tempo 模式） | **L3 Zone** — 更强隔离、独立状态、利用 OP Stack 可组合性 |

---

## 附录 A: 数据来源索引

| 源文件 | 编号 | 本文引用的关键内容 |
|--------|------|-----------------|
| Canton 官方文档调研 | WHI-334 | §3.1 权限模型（三级）; §3.2 Synchronizer; §3.3 Sequencer; §3.4 Mediator; §3.5 子交易隐私; §3.6 Daml 授权; §3.7 Canton Network; §6.2 拓扑管理 |
| Canton 架构分析 | WHI-335 | §1.1 Participant-Synchronizer 分离; §1.2 Sequencer-Mediator 角色分离; §1.3 状态一致性; §1.4 跨域协调 |
| Canton 代码库分析 | WHI-336 | §2.1 Participant 节点; §2.3 Identity Management; §2.4 网络通信 |
| Prividium 文档调研 | WHI-337 | §2 Validium 架构; §3.4 访问控制（SSO, Proxy RPC, RBAC, TransactionFilterer）; §3.5 KYC/AML; §3.6 选择性披露; §3.7 结算路径 |
| Prividium 架构分析 | WHI-338 | §1 Validium 深度分析; §2 ZK 证明系统; §3 四层纵深防御; §4 合规设计 |
| Tempo 文档调研 | WHI-339 | §2.1 共识架构; §3.1 TIP-403; §3.2 Zone 隐私; §3.3 加密存款; §3.4 AccountKeychain; §3.6 ZoneFactory |
| Tempo 代码分析 | WHI-340 | §3.1 TempoNode; §3.4 ZoneEngine; §3.5 TIP-403 镜像; §3.6 Private RPC 认证; §5 加密存款流程; §7 企业特性; §8 Mantle 参考点 |
| Mantle V2 基线 | WHI-341 | §1 架构概览; §2 组件描述; §5 企业适配潜力; §6 约束与限制; §7 自然插入点 |

## 附录 B: 术语对照表

| 英文术语 | 中文 | 所属项目 | 说明 |
|---------|------|---------|------|
| Participant | 参与者节点 | Canton | 运行 Daml 引擎的节点 |
| Synchronizer (Domain) | 同步器（域） | Canton | 由 Sequencer + Mediator 组成的协调服务 |
| Sequencer | 排序器 | All | 交易排序组件 |
| Mediator | 调解器 | Canton | 2PC 确认协调者 |
| Party | 参与方 | Canton | 法律实体在 Canton 中的代表 |
| Signatory | 签署方 | Canton | 必须授权合约创建的角色 |
| Observer | 观察方 | Canton | 可查看合约但不需授权的角色 |
| Controller | 控制方 | Canton | 可行使 Choice 的角色 |
| Proxy RPC | 代理 RPC | Prividium | 唯一的网络入口，执行三步验证 |
| RBAC | 基于角色的访问控制 | Prividium | 六种权限类型的访问控制框架 |
| TransactionFilterer | 交易过滤器 | Prividium | 拦截 L1→L2 强制交易的 L1 合约 |
| TIP-403 | TIP-403 合规框架 | Tempo | precompile 级策略注册表 |
| AccountKeychain | 账户密钥链 | Tempo | 支持 WebAuthn/P256 的身份管理 precompile |
| Zone | 隐私区 | Tempo | 单 Sequencer 的 L2 隐私执行环境 |
| Predeploy | 预部署合约 | OP Stack | 创世块中部署的系统合约 |
| Precompile | 预编译合约 | EVM | 硬编码在 EVM 中的特殊合约 |
