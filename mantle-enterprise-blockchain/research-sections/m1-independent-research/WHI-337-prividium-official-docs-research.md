# zkSync Prividium — 官方文档与产品调研

> **研究编号**: WHI-337  
> **研究日期**: 2026-05-06（初稿）/ 2026-05-07（Review 修订）  
> **数据来源**: zkSync 官方文档、博客、GitHub 仓库、企业产品页  
> **研究目的**: 为 Mantle 企业级适配方案提供参考架构分析  
> **修订说明**: 根据 Review Gate 反馈扩展文档深度、补充执行边界分析、新增文档缺口清单与 Mantle 适配映射

---

## 1. 项目总结

**Prividium™** 是 Matter Labs 基于 ZK Stack 构建的企业级隐私区块链平台。它采用 **Validium 架构**（交易数据链下存储、仅将状态根和零知识证明提交至以太坊），使机构能够在自有基础设施或云环境中运行**私有、许可制区块链**，同时将每笔交易锚定到以太坊以获得 L1 级安全性和最终性。Prividium 的核心设计目标是消除传统金融中"隐私 vs. 合规"的二元对立——通过零知识证明，机构可以在不暴露敏感数据的前提下，向监管机构证明交易的正确性与合规性。截至 2026 年 5 月，已有 **35+ 金融机构**验证了 Prividium 架构，包括美国五大区域银行（合计存款超 $600B）通过 Cari Network 构建代币化存款网络、BitGo 提供机构级托管整合、以及 Deutsche Bank 确认的合作伙伴关系。

**Prividium 在企业区块链竞争格局中的定位**：Prividium 是唯一一个同时满足以下三个条件的方案——(1) 完全 EVM 兼容，开发者可使用 Solidity/Hardhat/Foundry 直接迁移；(2) 以太坊 L1 作为中立结算层，结算验证基于密码学证明而非组织信任；(3) Validium 模型实现交易数据完全私有化。这一组合使其在与 Canton（基于 Daml 的专有执行引擎）、Hyperledger Fabric（需要 Orderer 组织信任的通道模型）和 Besu/Tessera（EVM 兼容但缺乏 ZK 结算保证）的竞争中占据独特位置。

---

## 2. Validium 架构描述

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ETHEREUM MAINNET (L1)                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  State Root + STARK Proof (仅密码学承诺, 无交易数据)            │  │
│  └───────────────────────────────────────▲───────────────────────┘  │
│                                          │                          │
└──────────────────────────────────────────│──────────────────────────┘
                                           │ 提交证明 + 状态根
                                           │
┌──────────────────────────────────────────│──────────────────────────┐
│                     ZKSYNC GATEWAY                                  │
│  ┌───────────────────────────────────────┴───────────────────────┐  │
│  │  Relayer: 接收 STARK 证明, 提交至以太坊进行链上验证             │  │
│  │  (共享结算层, 连接多条 ZKsync 链)                               │  │
│  └───────────────────────────────────────▲───────────────────────┘  │
│                                          │                          │
└──────────────────────────────────────────│──────────────────────────┘
                                           │ STARK 证明 + 状态根
                                           │
┌──────────────────────────────────────────│──────────────────────────┐
│                   PRIVIDIUM CHAIN (私有 Validium)                    │
│                                          │                          │
│  ┌───────────────┐    ┌─────────────────┴────────────────────┐     │
│  │  DMZ 层        │    │  应用层 (私有子网)                     │     │
│  │  ┌───────────┐ │    │  ┌────────────┐  ┌────────────────┐ │     │
│  │  │ Proxy RPC │◄├────┤──│ Sequencer  │  │ Prover Farm    │ │     │
│  │  │ (访问控制) │ │    │  │ (排序器)    │  │ (CPU/GPU 证明) │ │     │
│  │  └─────┬─────┘ │    │  └─────┬──────┘  └────────────────┘ │     │
│  │        │       │    │        │                              │     │
│  │  ┌─────┴─────┐ │    │  ┌─────┴──────────────────────────┐ │     │
│  │  │ Explorer  │ │    │  │  数据层 (私有子网)               │ │     │
│  │  │ (私有浏览器)│ │    │  │  PostgreSQL + Blob Storage    │ │     │
│  │  └───────────┘ │    │  │  (完整 L2 状态, 加密存储)       │ │     │
│  └───────────────┘    │  └──────────────────────────────────┘ │     │
│                        └──────────────────────────────────────┘     │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Permissioning System (权限系统)                             │   │
│  │  Admin Dashboard → 用户/角色/权限管理 → Prividium API        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  认证: Okta SSO (OIDC) / SIWE (钱包签名) / 混合模式               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

数据流:
用户 → 认证(Okta/SIWE) → Proxy RPC → Prividium API(JWT+地址+权限验证)
    → Sequencer RPC(私有执行) → 状态更新 → Prover(生成 STARK 证明)
    → ZKsync Gateway → Ethereum(链上验证, 不可篡改)

核心区别 — Validium vs ZK Rollup:
┌────────────────────┬────────────────────────┬──────────────────────┐
│                    │ ZK Rollup (zkSync Era) │ Validium (Prividium) │
├────────────────────┼────────────────────────┼──────────────────────┤
│ 交易数据存储       │ 以太坊 L1 (链上)       │ 运营商私有数据库     │
│ L1 可见内容        │ Calldata + 证明        │ 仅状态根 + 证明      │
│ 数据可用性保证     │ 以太坊保证             │ 运营商保证           │
│ 隐私性             │ 公开透明               │ 完全私有             │
│ 成本               │ 较高 (L1 DA 费用)      │ 较低                 │
│ 安全假设           │ 以太坊安全性           │ 以太坊 + 运营商信任  │
└────────────────────┴────────────────────────┴──────────────────────┘
```

---

## 3. 关键概念详解

### 3.1 Validium 模型

**定义**: Validium 是 ZK Rollup 的变体。与标准 ZK Rollup 将所有交易数据发布到以太坊 L1 不同，Validium 将交易数据保留在**链下运营商控制的数据库**中，仅将**状态根 (state roots)** 和**零知识证明 (ZK proofs)** 提交到以太坊。

**技术细节**:
- **链上可见内容**: 仅状态根、元数据和证明哈希。L1 观察者**无法**看到或推断任何交易输入、地址或 calldata。
- **链下存储**: 完整 L2 状态存储在私有 PostgreSQL 数据库中，加密存储，支持快照和备份策略。
- **安全模型**: 虽然交易有效性由以太坊上的 ZK 证明保证（与 ZK Rollup 相同），但数据可用性依赖于运营商。如果运营商拒绝提供数据，用户无法独立重构状态。这是隐私与数据可用性之间的设计权衡。
- **适用场景**: 交易敏感性高的金融场景（交易、结算、资产发行），其中数据隐私是法律和商业要求。
- **可选的选择性披露**: 可通过公共只读端点发布经验证的指标（如代币供应量、合约字节码），但这完全由运营商控制。

**与其他企业隐私模型的关键差异**:

Validium 的隐私模型在概念上与其他企业区块链采用的隐私方案有根本不同：

| 隐私模型 | 代表方案 | 隐私实现方式 | 结算验证方式 |
|---------|---------|------------|------------|
| **Validium** | Prividium | 整条链数据链下、L1 仅见证明 | ZK 密码学证明（无信任依赖） |
| **Private Channels** | Hyperledger Fabric | 按通道隔离交易、参与方各自维护账本 | Orderer 组织共识（需信任 Orderer） |
| **Private Data Collections** | Fabric PDC | 链上存储哈希、链下点对点分发私有数据 | Orderer + 背书节点共识 |
| **Privacy Groups** | Besu + Tessera | 私有交易通过 Tessera 加密分发 | 公链共识 + 隐私管理器信任 |
| **Sub-transaction Privacy** | Canton (Daml) | 每个参与方仅看到与己相关的子交易 | Global Domain 排序（需信任 Domain 运营方） |

Prividium 的独特之处在于：**整条链的所有数据**对外部观察者完全不可见，而不是在一条公开链上选择性隐藏部分交易。这意味着隐私是默认的、全局的，而非需要开发者逐交易配置的特性。

### 3.2 ZK 有效性证明 (Zero-Knowledge Validity Proofs)

**定义**: Prividium 使用零知识证明来验证每个区块的交易执行正确性，而不暴露底层交易数据。

**证明系统演进**:

| 阶段 | 系统名称 | 技术特征 | 状态 |
|------|---------|---------|------|
| 第一代 | Boojum | FRI-based STARK-like 证明系统 | 已部署 (zkSync Era) |
| 第二代 | **Airbender** | RISC-V prover, CUDA GPU 加速 | Atlas 升级引入 (2025.10) |

**Airbender 技术细节**:
- 开源 RISC-V 证明系统（Rust + CUDA），官方声称为"全球最高性能的开源 RISC-V 证明系统"
- 支持在**商用 GPU** 上运行，官方声称实现**亚秒级区块证明**
- 支持多种 VM 配置（包括完整 EVM 等价性）
- 官方声称每笔交易证明成本约 **$0.0001**
- GitHub: [matter-labs/zksync-airbender](https://github.com/matter-labs/zksync-airbender)

**证明流程**:
1. Sequencer 完成区块批次最终化
2. Prover 生成 STARK 证明并提交至 ZKsync Gateway
3. Relayer 将状态根和证明提交至以太坊
4. 以太坊链上验证创建不可变记录

**核心价值**: ZK 证明从根本上改变了结算验证的逻辑——在 ZK 密码学出现之前，验证交易结算的正确性需要查看底层数据或信任处理方。ZK 证明提供了"交易被正确处理"的密码学证书，任何交易对手方都可以验证，而无需了解交易内容本身。

**对比传统企业区块链结算**：Canton 的 Global Domain 依赖域运营方排序和确认交易——即使 Daml 引擎保证了模型级一致性，结算仍然依赖"可信第三方来排序交易并确认提交"。Prividium 的 ZK 证明将这一信任要求降低为密码学验证——任何人都可以在以太坊上独立验证证明的有效性，无需信任 Matter Labs、运营商或任何中间人。

### 3.3 数据可用性策略 (Data Availability Strategy)

**模型**: 运营商控制的链下数据存储（Operator-Controlled Off-Chain DA）。

**详细机制**:
- **无 DAC (Data Availability Committee)**: 当前文档中未提及 DAC 的存在。数据可用性完全由链运营商保证，存储在私有子网中的 PostgreSQL 数据库中。
- **数据隔离**: 数据库部署在专用子网中，无互联网暴露。仅 Sequencer 和 Prover 有权访问。
- **安全措施**: 加密存储、快照、备份策略，支持合规和灾难恢复。
- **L1 提交内容**: 每个区块仅提交状态根和 STARK 证明。不提交任何交易数据、地址或 calldata。
- **与存款/提款的交互**: 与公共网络的存款/提款交互在接收链上仍然可见（这是跨链交互的固有特性）。

**设计哲学**: 对于受监管机构而言，交易数据不仅不需要公开——公开反而违反隐私法规和商业保密义务。运营商控制的 DA 是一个功能特性，而非缺陷。

**DA 策略的风险分析**:

运营商完全控制数据可用性意味着以下风险需要企业客户自行评估和缓解：

| 风险场景 | 影响 | 当前官方缓解措施 | 缓解充分性评估 |
|---------|------|----------------|-------------|
| 运营商拒绝提供数据 | 用户无法重构状态、无法证明资产所有权 | 合同约束（SLA）、运营商即客户自身 | ⚠️ 依赖法律约束而非技术保证 |
| 运营商服务中断 | 链停止出块、无法执行新交易 | 灾难恢复、备份策略 | ⚠️ 未见具体 RTO/RPO 承诺 |
| 运营商恶意扣留数据 | ZK 证明仍有效但数据不可用（"数据扣留攻击"） | 运营商信任 + 审计 | ⚠️ 无技术层面防御 |
| 多方部署中的数据主权争议 | 谁持有数据的最终副本？ | 未明确讨论 | ❓ 文档未覆盖 |

> **关键观察**: Prividium 的 DA 模型假设运营商与用户利益一致（通常因为运营商即用户自身——如银行自己运营 Prividium 链）。在 Cari Network 这样的多银行场景中，DA 数据的托管和主权问题可能需要额外的治理机制，但当前文档未明确讨论这一点。

### 3.4 访问控制 (Access Control)

Prividium 实现了多层访问控制体系：

#### 3.4.1 认证层 — SSO 集成

| 认证方式 | 协议 | 适用场景 | 管理方式 |
|---------|------|---------|---------|
| **OIDC 用户** | OAuth 2.0/OIDC (如 Okta) | 企业内部 SSO 集成 | 通过 subject ID 关联 |
| **钱包用户** | SIWE (Sign-In With Ethereum) | 加密原生用户 | 通过钱包地址标识 |
| **混合用户** | OIDC 或 SIWE 均可 | 需要灵活性的场景 | 双重认证方式 |

- 混合用户支持通过企业身份系统或加密钱包进行认证，取决于上下文。
- 一个用户可关联多个钱包，所有关联钱包继承相同的基于角色的权限。

#### 3.4.2 网关层 — Proxy RPC 三步验证

Proxy RPC 是整个网络的**唯一入口**，所有请求必须通过它到达 Sequencer：

**请求流程**: `客户端 → Proxy RPC → Prividium API → Sequencer RPC`

**三步验证**:
1. **JWT 验证**: 验证用户的 JWT 令牌有效性
2. **钱包地址验证**: 确认钱包地址与认证身份匹配
3. **合约函数权限检查**: 验证用户是否有权调用目标合约的特定函数

未授权请求返回 `401 Unauthorized` 或 `HTTP 403`，并记录审计日志。

**安全要求**: 标准 RPC 端点必须保持私有。通过防火墙限制访问，仅公开暴露 Proxy RPC。

**双 RPC 端点**:

| 端点 | 认证方式 | 用途 |
|------|---------|------|
| `/rpc` (Proxy RPC) | Bearer token in header | 脚本 (Viem, Ethers.js) |
| `/wallet/{token}` (User RPC) | Token 嵌入 URL | 浏览器钱包 (MetaMask) |

#### 3.4.3 合约层 — PrividiumTransactionFilterer

处理 L1→L2 强制交易绕过 Proxy RPC 的安全风险：

**风险**: 从以太坊 L1 发起的强制交易可完全绕过 Proxy RPC，导致：
- 任意合约部署
- 未授权写操作
- 盲目攻击导致的数据泄露

**缓解措施**: `PrividiumTransactionFilterer` 合约提供基于白名单的过滤：
- 白名单地址：可执行不受限的强制交易
- 非白名单地址：仅可转移 ETH 或 ERC-20 代币

**Multicall 限制**: Proxy 阻止 Multicall 模式，因其可绕过单个函数的权限检查。

#### 3.4.4 权限模型 — RBAC 框架

**六种函数权限类型**:

| 类型 | 描述 |
|------|------|
| **Forbidden** (默认) | 禁止任何用户调用该函数 |
| **All Users** | 允许任何已认证用户调用，无角色限制 |
| **Check Role** | 仅具有特定角色的已认证用户可调用 |
| **Restrict Argument** | 任何已认证用户可调用，但限制特定函数参数值 |
| **Check Role AND Restrict Argument** | 需同时满足角色要求和参数限制 |
| **Check Role OR Restrict Argument** | 满足角色要求或参数限制之一即可 |

> **关键设计**: 所有合约函数默认为 **Forbidden**。部署后必须由管理员在 Admin Dashboard 中显式配置权限。这是"默认安全"的设计，与公链的"默认开放"形成鲜明对比。

**典型角色模式**:

| 角色 | 职责 | 典型权限 |
|------|------|---------|
| Admin | 系统管理 | 管理用户、角色、权限、披露设置 |
| Trader | 执行交易 | 代币合约、交易函数的写权限 |
| Auditor | 只读观察 | 查看合约数据、公共披露 |
| Operator | 系统运维 | 运维合约的读写权限 |

#### 3.4.5 访问控制执行边界分析

Review 反馈要求明确区分各控制点的执行位置、保护对象和绕过风险。以下是基于官方文档的分层分析：

| 控制点 | 执行位置 | 保护对象 | 绕过风险 | 缓解机制 | 官方文档是否明确 |
|-------|---------|---------|---------|---------|:---------------:|
| **JWT 认证** | Proxy RPC（DMZ 层） | 网络入口——未认证用户完全无法发送请求 | L1→L2 强制交易绕过 Proxy；Sequencer RPC 直连（如防火墙配置错误） | PrividiumTransactionFilterer 合约；防火墙规则要求 Sequencer 仅接受 Proxy 连接 | ✅ 明确 |
| **钱包地址匹配** | Proxy RPC → Prividium API | 身份与链上地址的绑定——防止冒充他人钱包操作 | 无已知绕过（JWT 中嵌入地址声明，API 端验证） | JWT claims 中包含钱包地址列表，与请求签名地址交叉验证 | ✅ 明确 |
| **函数级权限** | Proxy RPC → Prividium API（查询权限数据库） | 合约函数调用——哪些角色可以调用哪些合约的哪些函数 | L1→L2 强制交易绕过；直连 Sequencer RPC | TransactionFilterer 限制强制交易范围；Sequencer 不暴露于公网 | ✅ 明确 |
| **参数值限制** | Proxy RPC → Prividium API | 函数参数的具体值——如限制转账金额范围或目标地址 | 同上 | 同上 | ✅ 明确 |
| **合约部署权限** | Admin Dashboard → Prividium API | 谁可以部署新合约到链上 | 部署后函数默认 Forbidden，但合约字节码已上链 | 默认 Forbidden 策略确保即使合约被部署，函数仍不可调用 | ✅ 明确 |
| **PrividiumTransactionFilterer** | L1 智能合约层（以太坊主网） | L1→L2 强制交易——防止未授权地址通过 L1 绕过 Proxy | 白名单管理权限被窃取；合约升级漏洞 | 白名单管理需链上治理/管理员多签（具体机制文档未详述） | ⚠️ 白名单管理流程未详述 |
| **Sequencer 隔离** | 网络层（防火墙/子网配置） | 内部 RPC 端点——防止外部直接访问 Sequencer | 网络配置错误、内部人员滥用 | 三层部署架构（DMZ/应用/数据层分离） | ✅ 部署文档明确 |
| **Admin Dashboard / Permissioning API** | 应用层（独立 API 服务） | 权限配置本身——谁可以修改角色和权限规则 | Admin 凭证泄露、权限提升 | OIDC/Okta 认证保护管理界面；具体的管理员权限分级文档未详述 | ⚠️ Admin 权限分级未详述 |
| **私有区块浏览器** | DMZ 层（独立前端 + API） | 链上数据的可视化访问——基于角色展示不同级别的数据 | 内部版浏览器如果暴露到外网 | 公开版使用应用配置的访问规则；内部版仅限运营方网络 | ✅ 明确 |

**关键发现**:

1. **Proxy RPC 是核心防线**: 绝大多数访问控制逻辑集中在 Proxy RPC + Prividium API 这一层。这是一个**中间件层执行**的模型，而非协议层原生执行。如果 Proxy RPC 被绕过或 Sequencer 被直连，多数权限检查将失效。
2. **L1→L2 强制交易是唯一的已知架构级绕过路径**: 官方文档明确识别并提供了 `PrividiumTransactionFilterer` 作为缓解措施，但白名单的管理流程和治理机制未充分文档化。
3. **权限数据存储在链下**: 角色和权限规则存储在 Prividium API 后端（而非链上合约），意味着权限配置本身的完整性和审计性依赖于 API 层的实现质量。
4. **"默认 Forbidden" 是关键的安全网**: 即使合约部署权限被绕过，所有函数仍默认不可调用，为合约层提供了额外的防御深度。

### 3.5 KYC/AML 原生执行机制

**设计理念**: KYC/AML 不是外挂的合规监控层，而是**嵌入资产逻辑的系统属性**。

**实现机制**:
- **链级身份绑定**: 每个钱包地址与经过认证的身份（OIDC subject ID 或 SIWE 签名）绑定
- **许可参与**: 只有经过身份验证和管理员授权的用户才能访问网络
- **合约级执行**: KYC/AML 规则可通过函数权限和参数限制在合约层面强制执行
- **Okta SSO 集成**: 利用企业现有的身份管理基础设施（身份验证、多因素认证等）
- **审计追踪**: Proxy RPC 层自动记录所有访问尝试，包括被拒绝的请求

**与传统方案的区别**: 传统 KYC/AML 是在链外系统（如交易所合规团队）中执行，然后手动映射到链上地址。Prividium 将这一过程直接嵌入链的访问控制架构中——未通过身份验证和授权的用户从物理上无法与链交互。

**执行层分析**: 需要注意的是，Prividium 的 KYC/AML "原生执行"并非指链的共识协议层原生理解 KYC 状态。实际执行发生在 Proxy RPC 中间件层——用户的身份和 KYC 状态在 Proxy RPC 接收请求时被验证，未通过验证的请求被拒绝进入 Sequencer。这意味着 KYC 执行的强度取决于 Proxy RPC 和网络隔离的完整性，而非区块链协议本身的内在属性。对于 M2 比较分析（WHI-343 至 WHI-347），这一区分至关重要——Canton 的 Daml 模型将权限检查嵌入了智能合约语言层面（Daml 的 signatory/observer 模型），而 Prividium 将其放在了基础设施中间件层。

### 3.6 选择性披露 (Selective Disclosure)

**定义**: 允许监管机构和审计员在不获得完整数据访问权限的情况下验证和审计交易。

**实现机制**:
1. **范围化审计角色 (Scoped Auditor Roles)**: 创建具有只读权限的审计员角色，仅能查看授权的合约数据和公共披露
2. **Merkle 证明导出**: 按需提供包含证明的链段，验证特定交易的存在和正确性
3. **数据库摘录**: 导出经过筛选的账本视图，仅包含审计所需的数据
4. **可配置的公共端点**: 可选地通过公共只读端点发布经验证的指标（如代币总供应量）
5. **私有区块浏览器**: 根据用户角色展示不同级别的链上数据

**ZK 驱动的合规创新**:
- **无 PII 存储的制裁筛查**: 银行可通过接收密码学证明来验证交易对手方已通过制裁筛查，而无需存储对方的护照号码或地址
- **密码学合规证明**: 参与方可提供数学证明表明其已满足合规义务，而不暴露底层个人数据
- **防篡改合规信号**: 监管机构获得更高质量、不可篡改的合规信号

**实现成熟度评估**: 选择性披露是 Prividium 宣传中最有力的差异化叙事之一，但需要注意文档中描述的实现细节层次不一：
- **已实现且文档化**: 审计角色 RBAC、私有区块浏览器的分级访问、公共只读端点配置——这些在 Prividium 文档中有具体的 API 和配置说明。
- **概念层面描述、缺乏实现细节**: ZK 驱动的合规证明（无 PII 制裁筛查、密码学合规证明）——这些在博客文章（特别是 "Privacy and Compliance Are Not Opposites"）中描述为设计愿景和理论可能性，但 Prividium 文档中未给出具体的 API 接口、SDK 方法或配置步骤。
- **需要 WHI-338 深入验证**: Merkle 证明导出的具体 API、审计日志的保留策略和导出格式、ZK 合规证明的实际链上实现状态。

### 3.7 结算路径 (Settlement Path)

**完整流程**:

```
Prividium Chain (私有执行)
    │
    │ 1. Sequencer 最终化区块批次
    │ 2. Prover 生成 STARK 证明
    │
    ▼
ZKsync Gateway (共享结算层)
    │
    │ 3. Relayer 接收证明 (出站连接, 无入站)
    │ 4. 提交状态根 + 证明至以太坊
    │
    ▼
Ethereum Mainnet (L1)
    │
    │ 5. 链上验证 STARK 证明
    │ 6. 状态根被接受 → 不可篡改的最终性
    │
    ▼
✅ 结算完成 — 无中间人, 无运营商信任依赖
```

**关键属性**:
- **证明从出站连接提交**: Prover 仅通过出站连接将证明发送到 Gateway，无需入站连接
- **无运营商信任**: 结算验证基于密码学证明而非运营商诚实性——这是 Prividium 区别于 Canton 等方案的核心优势
- **跨链互操作**: ZKsync Gateway 作为共享结算层，支持多条 ZKsync 链之间的资产转移
- **ZKsync Connect**: 首个面向机构的互操作协议，支持实时、ZK 保护的跨链连接，具有原子性和隐私保护的结算

**结算保证的精确边界**: 需要区分 ZK 证明保证什么和不保证什么：
- ✅ **ZK 证明保证**: 状态转换的计算正确性——即"从状态 A 到状态 B 的所有交易都被正确执行"
- ✅ **以太坊保证**: 状态根一旦被接受即不可篡改、结算具有最终性
- ❌ **ZK 证明不保证**: 数据可用性、Sequencer 的交易排序公平性（MEV）、审查抗性（Sequencer 可拒绝包含特定交易）
- ❓ **Gateway 的额外保证**: Gateway 作为中间层是否引入额外的信任假设？文档描述 Gateway 为"共享结算层"，但其运营方式（去中心化程度、治理模型）在 Prividium 文档中未详细说明

### 3.8 性能基准 (Performance Benchmarks)

| 指标 | 数值 | 来源类型 | 具体来源 |
|------|------|---------|---------|
| 交易吞吐量 (TPS) | **>15,000 TPS** | 🏷️ 官方产品声明 | Atlas 升级公告 (2025.10) |
| ZK 最终性 | **1 秒** | 🏷️ 官方产品声明 | Atlas 升级公告 |
| 区块证明速度 | **亚秒级** | 🏷️ 官方产品声明 | Airbender 技术公告 |
| 单笔交易成本 | **<$0.0001** | 🏷️ 官方产品声明 | Airbender 在商用 GPU 上 |
| 以太坊最终性 | **数分钟** | 🏷️ 官方产品声明 | 通过 ZKsync Gateway |
| 网络跳转 (链间) | **~1 秒** | 📊 ZKsync 网络统计 | ZKsync 网络统计页面 |
| 基金部署周期 | **2-3 周** | 🗣️ 客户案例声明 | 企业产品页 (vs 传统 2-3 个月) |

> ⚠️ **数据来源说明**: 上述所有性能指标均来自 Matter Labs 官方产品页面、博客文章或技术公告。截至本研究日期，未找到独立的第三方基准测试结果来验证这些数字。Atlas 升级相关指标（>15K TPS, 1s ZK finality）来自 ZK Stack 技术升级公告，理论上适用于所有 ZK Stack 链（包括 Prividium），但未找到 Prividium 专项性能测试报告。WHI-338 应进一步调查是否存在独立验证数据。

**Atlas 升级的三大技术突破**:
1. **高性能 Sequencer**: 优化吞吐量（抗流量突增）、延迟（支持时间敏感应用）和系统简洁性
2. **Airbender 集成**: 官方声称为全球最高性能的开源 RISC-V 证明系统
3. **多 VM 支持**: 包括完整 EVM 等价性的多种 VM 配置选项

---

## 4. 企业案例研究

> **合作关系层级说明**: 为区分不同案例的确认程度，本节对每个案例标注合作关系类型：
> - 🟢 **已确认客户 (Confirmed Customer)**: 有明确的产品选型公告、联合新闻稿或官方博客确认
> - 🟡 **设计合作伙伴 (Design Partner)**: 参与产品设计或 PoC，但未见生产部署公告
> - 🔵 **生态/标准参与者 (Ecosystem Participant)**: 参与标准制定或行业联盟，非直接产品用户
> - ⚪ **官方提及的合作伙伴 (Officially Mentioned)**: 在官方材料中被提及，但缺乏独立的联合公告确认

### 4.1 Cari Network + 5 家美国银行 🟢 已确认客户

| 项目 | 详情 |
|------|------|
| **发起方** | Cari Network（创始人 Eugene Ludwig，前美国货币监理署署长） |
| **参与银行** | Huntington Bancshares, First Horizon, M&T Bank, KeyCorp, Old National Bancorp |
| **合计存款规模** | **$600B+** |
| **技术方案** | 基于 Prividium 的代币化存款网络 |
| **核心功能** | 代币化存款发行 → 即时 24/7/365 转账 → 按需赎回为美元 |
| **背书机构** | 美国中型银行联盟 (MBCA) |
| **生产部署时间** | 2026 年晚些时候（官方声明） |
| **确认来源** | 官方博客公告 (2026.03.17, 2026.03.20)——两篇专题文章 |
| **参与银行角色** | "设计合作伙伴 (design partners)"——参与架构定义，非已上线用户 |

**选择 Prividium 而非其他方案的原因**:

| 方案 | 问题 |
|------|------|
| **JPMorgan Coin (私有链)** | 竞争对手不会在对手的支付系统上构建。私有链只在自己网络内有用 |
| **公链** | 实时暴露头寸和交易对手关系，对恶意行为者构成重大风险 |
| **专有协议 (Canton 等)** | 结算依赖"可信第三方来排序交易并确认提交"——用协议运营商的组织信任替代了数学保证 |
| **Prividium** | ZK 证明提供无需运营商验证的密码学结算保证，结算层中立（以太坊），非专有 |

**代币化存款设计**: Cari 代币代表的存款仍然是参与银行资产负债表上的受监管银行负债，受现有监管和 FDIC 保险保护。

**开放问题**: Cari 网络的运营架构——5 家银行是各自运营独立的 Prividium 链并通过 ZKsync Connect 互操作，还是共享一条链？如果共享，DA 数据的托管方和治理结构如何安排？博客文章未详细说明这些部署细节。

### 4.2 BitGo 合作伙伴关系 🟢 已确认客户

| 项目 | 详情 |
|------|------|
| **公告日期** | 2026.03.25 |
| **合作内容** | BitGo 机构级托管 + Prividium 私有区块链整合 |
| **核心功能** | 代币化存款的发行和结算 |
| **BitGo 角色** | 提供机构级托管、钱包基础设施和受监管数字资产服务 |
| **Prividium 角色** | 提供为合规机构设计的许可制区块链层 |
| **部署状态** | "正在与受监管金融机构测试"——生产部署目标 2026 年底（官方声明） |
| **确认来源** | 官方博客联合公告 (2026.03.25) |

**价值主张**: 银行无需自行构建复杂的区块链系统，即可实现全天候结算和可编程资金流动，同时保持对现有监管框架的对齐。

### 4.3 Deutsche Bank (德意志银行) ⚪ 官方提及的合作伙伴

| 项目 | 详情 |
|------|------|
| **确认来源** | Matter Labs 加入 LF Decentralized Trust 博客 (2026.04.21) |
| **合作状态** | 在 LF 博客中被提及为"Prividium 机构合作伙伴" |
| **合作领域** | 代币化基金发行和管理（企业产品页提及 "Deutsche Bank/Memento"）|
| **其他信息** | 无专门的 DAMA 2 + Prividium 联合新闻稿 |

> ⚠️ **证据强度说明**: Deutsche Bank 合作关系的唯一确认来源是 Matter Labs 自己发布的 LF Decentralized Trust 加入公告博客。截至研究日期：
> - 未找到 Deutsche Bank 自身（`db.com` 或 `deutsche-bank.com`）发布的确认公告
> - 未找到独立媒体的验证报道
> - 企业产品页上提及 "Deutsche Bank/Memento — Tokenized fund issuance and management" 作为案例，但这也是 Matter Labs 自有渠道
> 
> 建议在引用时使用"据 Matter Labs 官方材料，Deutsche Bank 为 Prividium 合作伙伴"而非"Deutsche Bank 选择了 Prividium"。

### 4.4 TCMAG (Tokenized Cash Management Advisory Group) 🔵 生态/标准参与者

| 项目 | 详情 |
|------|------|
| **性质** | "企业之声"(voice of the corporate)咨询小组 |
| **目标** | 指导代币化在现金管理中的负责任采用 |
| **核心成员** | Barclays, HSBC, Lloyds Bank, Digital Asset, SWIFT, SAP, BitGo, GLEIF, ZKsync |
| **产出** | 12 条代币化企业现金管理核心原则 |
| **ZKsync 角色** | 赞助商和参与方——非直接的产品客户关系 |

> **注意**: TCMAG 是一个行业标准制定组织，ZKsync 作为赞助商参与。Barclays、HSBC、Lloyds Bank 等参与 TCMAG 并不意味着它们是 Prividium 客户。这些银行同时也与 Digital Asset (Canton) 等其他平台有合作。

**12 条核心原则**:

| # | 原则 | 说明 |
|---|------|------|
| 1 | 合规性 | 在各司法管辖区的法律框架内运营 |
| 2 | 多银行/多发行方 | 支持标准化架构，避免供应商锁定 |
| 3 | 会计标准 | 明确的分类和披露处理 |
| 4 | 集成性 | 与 TMS 和 ERP 平台无缝集成 |
| 5 | 安全性 | 达到或超过现有安全标准 |
| 6 | 互操作性 | 拒绝围墙花园，支持跨层互操作 |
| 7 | 保密性 | 余额和交易保持私有 |
| 8 | 功能等价 | 复制核心资金管理能力（资金池、扫描、净额、内部银行） |
| 9 | 7×24 运营 | 实时连续运营，消除截止时间限制 |
| 10 | 控制 | 维护制造-检查工作流、职责分离和审计追踪 |
| 11 | 结算最终性 | 确保交易以法律最终性结算 |
| 12 | 运营韧性 | 处理错误、撤销和争议解决 |

**对 Mantle 的参考价值**: TCMAG 12 条原则可作为 Mantle 企业方案的**需求验证框架**——任何企业级区块链方案都应逐条对照这些原则评估自身的满足程度。

---

## 5. Prividium vs 公共 zkSync Era 对比表

| 维度 | zkSync Era (公共 L2) | Prividium™ (企业私有) |
|------|---------------------|---------------------|
| **链类型** | 公共 ZK Rollup | 私有 Validium |
| **数据可用性** | 以太坊 L1 (链上) | 运营商私有数据库 (链下) |
| **L1 可见内容** | 完整 calldata + 证明 | 仅状态根 + 证明 |
| **访问模式** | 无许可 (Permissionless) | 许可制 (Permissioned) |
| **RPC 访问** | 开放 | 需认证 (JWT + 角色验证) |
| **合约部署** | 任何人 | 需管理员授权 |
| **函数调用** | 开放 | 基于角色的权限控制 |
| **身份系统** | 钱包地址 (匿名) | SSO (Okta/SIWE) + 钱包绑定 |
| **KYC/AML** | 无原生支持 | 链级原生执行（中间件层） |
| **区块浏览器** | 公共 (完全透明) | 私有 (基于角色的视图) |
| **交易签名** | 钱包签名 | 钱包签名 + Token 授权 |
| **隐私级别** | 无 (全部公开) | 完全私有 + 选择性披露 |
| **合规支持** | 链外实现 | 原生内置 |
| **证明系统** | Boojum / Airbender | 相同 (共享 ZK Stack) |
| **结算层** | 以太坊 (通过 ZKsync Gateway) | 以太坊 (通过 ZKsync Gateway) |
| **互操作性** | ZKsync 网络内 | ZKsync Connect (机构级) |
| **许可模式** | 开源 (MIT/Apache) | 开放核心 (核心开源 + 企业模块闭源) |
| **部署模式** | 公共基础设施 | 自托管 / Matter Labs 托管服务 |
| **目标用户** | DeFi、消费者应用 | 银行、资产管理、合规敏感机构 |
| **TPS** | 数百 ~ 数千 | >15,000 (Atlas 升级后，官方声明) |
| **开发体验** | 标准 EVM 工具链 | 标准 EVM + 认证适配 + Prividium SDK |

---

## 6. 关键设计决策与权衡

### 6.1 Validium over Rollup — 隐私优先于 DA 去中心化

**决策**: 选择 Validium（链下 DA）而非 ZK Rollup（链上 DA）。

**收益**:
- 交易数据完全对 L1 观察者不可见
- 满足金融机构法律合规和商业保密要求
- 降低 L1 数据发布成本

**权衡**:
- 数据可用性依赖运营商。如运营商拒绝提供数据或服务中断，用户无法独立重构状态
- 信任模型中引入了运营商依赖（但对目标客户——受监管金融机构——这是可接受的，因为运营商即其自身或受其控制的实体）

### 6.2 Proxy RPC 网关强制执行 — 安全性 vs. 去中心化

**决策**: 所有访问通过单一 Proxy RPC 网关，而非直接访问节点。

**收益**:
- 实现细粒度的基于角色的访问控制
- 完整的审计日志记录
- 防止未授权访问内部基础设施

**权衡**:
- 单点瓶颈和潜在的单点故障
- 去中心化程度降低（但对企业场景，集中控制是需求而非缺陷）
- L1→L2 强制交易可绕过 Proxy（需通过 PrividiumTransactionFilterer 缓解）

### 6.3 默认 Forbidden 的函数权限 — 安全 vs. 开发效率

**决策**: 所有合约函数部署后默认为 **Forbidden**，必须显式启用。

**收益**:
- "默认安全"设计，消除因遗漏配置导致的安全漏洞
- 强制管理员审查每个函数的访问策略

**权衡**:
- 开发流程比公链复杂——部署后必须立即配置权限
- 需要管理员与开发者之间的协调流程
- 增加了部署周期（但确保了合规性）

### 6.4 开放核心许可 — 采用率 vs. 商业可行性

**决策**: ZK Stack 完全开源（核心协议、执行引擎、SDK 等），企业模块（权限系统、Proxy RPC、私有浏览器）闭源商业许可。

**收益**:
- 核心技术可被社区审计和贡献
- 企业模块的商业化支撑持续开发投入
- 非生产环境免费使用（降低评估门槛）
- SDK 为 MIT 许可（最大化开发者采用）

**权衡**:
- 生产部署需商业协议（增加采购流程复杂度）
- 企业模块不可自由修改或再分发
- 潜在的供应商锁定（但核心 ZK Stack 开源，缓解了这一风险）

### 6.5 以太坊锚定结算 — 中立性 vs. 成本

**决策**: 选择以太坊作为最终结算层，而非自建结算链或使用其他 L1。

**收益**:
- 中立的结算层——不由任何金融机构或协议运营商控制
- 结算验证基于密码学证明而非组织信任
- 利用以太坊的安全性和去中心化特性
- 跨机构结算无需信任中间人

**权衡**:
- 以太坊 gas 费用（虽然 Validium 模式下显著降低）
- 以太坊的最终性时间（~12 分钟）限制了 L1 级结算速度
- 对以太坊网络可用性的依赖

### 6.6 EVM 兼容性保持 — 迁移便利 vs. 性能优化

**决策**: 保持完整 EVM 兼容性（支持 Solidity, Hardhat, Foundry），无需自定义语言或重写。

**收益**:
- 现有以太坊开发者可直接迁移
- 利用成熟的 EVM 工具链和审计生态
- 降低人才招聘和培训成本

**权衡**:
- EVM 的固有限制（如存储模型）无法突破
- 某些性能优化可能因 EVM 约束而无法实现
- 但通过 ZK Stack 的多 VM 支持（Atlas 升级），未来可选择性引入非 EVM 执行环境

### 6.7 三层部署架构 — 深度防御 vs. 运维复杂度

**决策**: 采用 DMZ/应用层/数据层的三层部署模型。

**收益**:
- DMZ 层预过滤阻止未授权访问到达内部系统
- 共识逻辑隔离在不可路由的子网中
- 数据库具有静态加密和灾难恢复能力

**权衡**:
- 运维复杂度高于单层部署
- 需要专业的基础设施团队或使用 Matter Labs 托管服务
- 多层架构增加了调试和故障排除的难度

---

## 7. 附加发现

### 7.1 The Bank Stack 概念

Matter Labs 将 ZKsync 定位为"以太坊的银行堆栈"，包含三个集成平面：
1. **区块链平台**: 以太坊信任根 + Prividium 私有执行层 + ZK 证明完整性验证
2. **货币与资产**: 原生代币化存款、稳定币、RWA、即时结算
3. **服务与治理**: 身份/访问控制、托管、政策执行、断路器、报告

### 7.2 Phylax 安全层

Prividium 集成 Phylax 安全层，支持**预提交断言** (pre-commit assertions)——不变量、限额和策略门控在区块构建期间强制执行，在执行前防止灾难性状态的发生。

### 7.3 ZKsync Connect

面向机构的首个互操作协议：
- 私有 Prividium 实例与以太坊之间的实时、ZK 保护连接
- 原子性、隐私保护的结算
- 机构可维护私有系统并无缝访问公共市场流动性

### 7.4 托管服务 (Managed Services / RaaS)

Matter Labs 提供完整的运营服务：
- **基础设施运营**: 排序器、证明器、节点、RPC 端点、升级——24/7 全天候
- **设计与部署**: 联合架构定义（结算层、DA 配置、吞吐量目标）
- **集成与工具**: 高性能 RPC (>15K TPS，官方声称)、Webhooks、钱包/桥接/索引器集成
- **可定制**: DA 层、Gas 代币、MEV 策略、访问级别均可配置

### 7.5 行业验证与网络规模

- **网络规模**: 18 条链, $4B+ TVL, 700M+ 已处理交易（ZKsync 生态统计，非 Prividium 专项）
- **机构验证**: 35+ 金融机构验证了 Prividium 架构（官方产品页声明）
- **安全审计**: 开源代码库，第三方审计，最高 $1.1M 漏洞赏金

### 7.6 2026 路线图战略方向

2026 年从基础设施建设转向现实用例，聚焦传统金融集成的四大核心需求：
1. **隐私**: 敏感金融数据不能公开（合规、竞争力、法律）
2. **控制**: 机构需要完全控制系统以保证性能和治理
3. **风险管理**: 能够在监管审查下证明决策如何制定、执行和审计
4. **互操作性**: 系统必须连接外部市场，而非作为孤立数据库运行

---

## 8. 竞品高层对比 — Prividium vs 其他企业区块链隐私方案

本节提供 Prividium 与三大主要竞品的高层对比，为 M2 横向比较（WHI-343 至 WHI-347）建立初步框架。深度比较将在 M2 各专题中展开。

| 维度 | Prividium (ZK Stack) | Canton (Digital Asset) | Hyperledger Fabric | Besu + Tessera |
|------|---------------------|----------------------|-------------------|----------------|
| **隐私模型** | Validium（整链数据链下） | Sub-transaction（参与方仅见相关子交易） | Channels + PDC（通道隔离 + 私有数据集合） | Privacy Groups（Tessera 加密分发） |
| **执行引擎** | EVM（Solidity） | Daml（专有函数式语言） | Chaincode（Go/Java/JS） | EVM（Solidity） |
| **结算保证** | ZK 密码学证明 → 以太坊 | Global Domain 排序（需信任 Domain 运营方） | Orderer 共识（需信任 Orderer 组织） | EVM 公链共识 |
| **数据可用性** | 运营商控制 | 参与方各自存储 | 通道参与方各自维护 | 公链 + Tessera 加密存储 |
| **身份/访问控制** | Proxy RPC + RBAC + SSO | Daml Ledger API + Participant 概念 | MSP (Membership Service Provider) | 无原生企业 ACL |
| **许可模式** | 开放核心（核心开源，企业模块闭源） | 核心开源 (Apache 2.0) | 完全开源 (Apache 2.0) | 完全开源 (Apache 2.0) |
| **EVM 兼容** | ✅ 完整 | ❌ 需要 Daml | ❌ 需要 Chaincode | ✅ 完整 |
| **以太坊结算** | ✅ 原生 | ❌ 非以太坊结算 | ❌ 非以太坊结算 | ⚠️ 取决于部署方式 |
| **生产部署成熟度** | 🟡 2026 首批客户部署中 | 🟢 已有多年生产部署 | 🟢 已有多年生产部署 | 🟢 已有生产部署 |

> **对 Mantle 的关键启示**: Prividium 和 Besu 是两个 EVM 兼容的方案，对 Mantle（OP Stack, EVM）的参考价值最高。Canton 的隐私模型在概念上最精细（sub-transaction 级别），但需要完全不同的执行引擎（Daml），对 Mantle 的直接适配参考有限。Fabric 的通道模型在概念上类似于"运营多条独立链"，对 Mantle 的多链/子链架构设计有参考价值。

---

## 9. 官方文档缺口与 WHI-338 待验证问题

以下列出在本次调研中识别的官方文档缺口和需要在 WHI-338（代码库与技术深度分析）中进一步验证的问题：

### 9.1 数据可用性 (DA) 相关

1. **DAC 是否存在或计划引入？** — 当前文档未提及 Data Availability Committee。对于多方部署（如 Cari Network 的多银行场景），仅依赖单一运营商控制 DA 是否足够？是否有计划引入 DAC 或其他 DA 保证机制？
   - 📎 相关文档: [Prividium Overview](https://docs.zksync.io/zk-stack/prividium/overview) — 仅提及运营商控制数据存储
2. **数据保留与审计政策** — 运营商需要保留链下数据多长时间？是否有强制的数据保留策略？审计日志的格式和导出方式如何？
   - 📎 相关文档: [Deployment](https://docs.zksync.io/zk-stack/prividium/deployment) — 提及 PostgreSQL 存储但无保留策略
3. **数据灾难恢复 (DR) 的具体承诺** — 文档提及"快照和备份策略"，但未给出具体的 RTO/RPO 承诺或推荐配置。
   - 📎 相关文档: [Deployment](https://docs.zksync.io/zk-stack/prividium/deployment) — 提及加密存储和灾备能力

### 9.2 访问控制与治理

4. **PrividiumTransactionFilterer 白名单管理流程** — 谁有权修改白名单？是否需要多签或治理投票？白名单变更的审计日志如何记录？
   - 📎 相关文档: [Proxy RPC](https://docs.zksync.io/zk-stack/prividium/proxy) — 描述了 TransactionFilterer 功能，但管理流程未详述
5. **Admin 权限分级** — Admin Dashboard 是否支持管理员权限的进一步分级？是否存在"超级管理员"和"有限管理员"的区分？权限变更是否有四眼原则支持？
   - 📎 相关文档: [Administration & User Management](https://docs.zksync.io/zk-stack/prividium/administration-user-management) — 描述了用户管理但未涉及管理员自身的权限分级
6. **权限配置的链上/链下存储** — 角色和权限规则存储在何处？是 Prividium API 后端数据库还是链上合约？权限变更是否生成链上审计记录？
   - 📎 需要在代码库中验证 Prividium API 的存储后端

### 9.3 选择性披露与合规

7. **ZK 合规证明的实现状态** — 博客中描述的"无 PII 存储的制裁筛查"和"密码学合规证明"是已实现的产品功能，还是设计愿景/路线图项目？
   - 📎 相关文档: [Privacy and Compliance blog](https://zksync.io/blog/privacy-and-compliance-are-not-opposites) — 概念层面描述
8. **Merkle 证明导出 API** — 选择性披露中提到的"Merkle 证明导出"是否有具体的 API 接口文档？审计员如何在实践中请求和验证这些证明？
   - 📎 相关文档: [Features](https://docs.zksync.io/zk-stack/prividium/features) — 提及选择性披露但无 API 细节
9. **监管方访问的技术流程** — 当监管机构（如 OCC 或 FDIC）需要审查 Prividium 上的代币化存款交易时，具体的技术工作流是什么？是通过 Admin Dashboard 创建审计角色，还是有专用的监管接口？
   - 📎 文档中未找到专门的监管方访问流程文档

### 9.4 结算与互操作

10. **ZKsync Gateway 的治理和信任模型** — Gateway 是去中心化运营还是 Matter Labs 中心化运营？Gateway 的可用性如何保证？如果 Gateway 停止运行，Prividium 链的结算是否中断？
    - 📎 相关文档: [Architecture](https://docs.zksync.io/zk-stack/prividium/architecture) — 提及 Gateway 但未详述其治理
11. **ZKsync Connect 的成熟度** — ZKsync Connect 是已部署的产品功能还是路线图项目？跨链原子性结算的具体技术实现是什么？
    - 📎 相关文档: [Features](https://docs.zksync.io/zk-stack/prividium/features) — 提及 Connect 但无实现细节

### 9.5 企业模块与部署

12. **企业模块的源代码可审计性** — Prividium 企业模块（Proxy RPC、Permissioning System、Private Explorer）的源代码是否可供客户审计（即使不公开发布）？还是纯粹的闭源 SaaS？
    - 📎 相关文档: [License](https://docs.zksync.io/zk-stack/prividium/license) — 描述为"开放核心"但未明确客户审计权

---

## 10. Mantle/OP Stack 企业适配映射

本节将 Prividium 的核心企业功能映射到 Mantle/OP Stack 架构，评估哪些可直接复用、哪些需要协议改造、以及主要风险。

| Prividium 机制 | Mantle/OP Stack 对应组件 | 可直接复用？ | 需要协议改造？ | 主要风险/注意事项 |
|:--------------|:----------------------|:----------:|:------------:|:----------------|
| **Proxy RPC 网关** (认证 + 权限检查) | Mantle RPC 节点前加反向代理/API 网关 | ✅ 是 | 否 | 中间件方案，不需修改 OP Stack 核心。但需自建权限 API、RBAC 引擎和 Admin Dashboard |
| **SSO/OIDC 身份集成** (Okta, SIWE) | 在 API 网关层集成 OAuth 2.0 / OIDC | ✅ 是 | 否 | 标准企业认证集成，与链无关。需要设计链上地址与企业身份的绑定机制 |
| **函数级 RBAC** (默认 Forbidden) | 在 API 网关或 Sequencer 准入层实现 | ⚠️ 部分 | ⚠️ 部分 | 网关层可拦截已知合约函数调用，但 Mantle 的 Sequencer 无原生权限检查概念。完整实现需要在 Sequencer 添加准入逻辑或在网关层解析 calldata |
| **PrividiumTransactionFilterer** (L1→L2 过滤) | OP Stack 的 L1 合约 (OptimismPortal) 添加过滤逻辑 | ❌ 否 | ✅ 是 | 需要修改 OP Stack 的 L1 存款合约。这是协议级改动，影响升级兼容性和与 OP Stack 上游同步 |
| **私有区块浏览器** | 部署独立的受限浏览器实例 (基于 Blockscout 等) | ✅ 是 | 否 | 前端和 API 层的工作，不涉及协议改动。需要实现基于角色的数据过滤 |
| **Validium 数据可用性** (链下 DA) | Mantle 已使用 EigenDA/自有 DA 方案 | ⚠️ 部分 | ✅ 是 | Mantle 当前将数据发布到 DA 层（EigenDA）。切换到完全私有 DA 需要修改 DA 提交逻辑，但 Mantle 的 DA 架构已有模块化设计，可能比纯 OP Stack 更容易适配 |
| **ZK 结算证明** | Mantle 当前使用 Optimistic Rollup (欺诈证明) | ❌ 否 | ✅ 是 | 从欺诈证明切换到 ZK 证明是根本性的架构变更，不在企业适配范围内。但可参考 ZK 证明的合规价值（"可验证的正确性证书"）在 Optimistic 模型下寻找替代方案 |
| **选择性披露** (审计角色 + Merkle 证明) | 在浏览器和 API 层实现数据导出工具 | ✅ 是 | 否 | 基于 RBAC 的数据访问控制可在应用层实现。Merkle 证明导出取决于链的状态存储方式 |
| **合约部署权限控制** | 在 Sequencer 准入层或网关层添加部署白名单 | ⚠️ 部分 | ⚠️ 部分 | 网关层可拦截部署交易，但内部绕过风险需要 Sequencer 级改造 |
| **Multicall 限制** | 在网关层识别并阻止 Multicall 模式 | ✅ 是 | 否 | calldata 解析在网关层即可完成 |
| **三层部署架构** (DMZ/App/Data) | 标准基础设施架构设计 | ✅ 是 | 否 | 纯运维/基础设施层面的工作，不涉及协议改动 |

**总体评估**:

Prividium 的企业功能大致分为三类：

1. **中间件层可复用** (~60%): Proxy RPC 网关、SSO 集成、私有浏览器、选择性披露、部署架构——这些功能本质上是在链的外围添加企业控制层，不需要修改 Mantle/OP Stack 核心协议。Mantle 可以参考 Prividium 的设计模式，在 RPC 层前添加类似的中间件。

2. **需要 Sequencer 级改造** (~25%): 函数级 RBAC 的完整执行、合约部署权限——这些需要 Mantle 的 Sequencer 具备交易准入控制能力。OP Stack 的 Sequencer 当前不支持此类逻辑，但改造范围有限且可控。

3. **需要根本性架构变更** (~15%): ZK 结算证明、完全私有 DA——这些涉及 Mantle 从 Optimistic Rollup 到 ZK Validium 的根本性转变，超出了"企业适配"的范畴。但 Mantle 的 DA 模块化设计为 DA 隐私提供了一定的适配空间。

---

## 11. Prividium 术语表

| 术语 | 定义 | 首次出现于 |
|------|------|---------|
| **Validium** | ZK Rollup 的变体，交易数据存储在链下（运营商控制），仅将状态根和 ZK 证明提交到以太坊。隐私的核心保证来源。 | §3.1 |
| **Proxy RPC** | Prividium 网络的唯一外部入口。所有请求必须通过 Proxy RPC 到达 Sequencer，在此执行 JWT 验证、钱包地址匹配和函数级权限检查。 | §3.4.2 |
| **Permissioning System** | Prividium 的核心访问控制引擎，包含 Admin Dashboard（管理界面）和 Prividium API（权限决策后端）。管理用户、角色、钱包绑定和函数权限。 | §2 架构图 |
| **PrividiumTransactionFilterer** | 部署在以太坊 L1 的智能合约，用于过滤从 L1 发起的强制交易（forced transactions），防止绕过 Proxy RPC 的权限控制。基于白名单机制。 | §3.4.3 |
| **ZKsync Gateway** | ZKsync 生态的共享结算层。接收各 ZKsync 链的 STARK 证明，批量提交到以太坊主网进行验证。多条 ZKsync 链通过 Gateway 共享结算基础设施。 | §3.7 |
| **ZKsync Connect** | 面向机构的跨链互操作协议。支持 Prividium 私有链与以太坊公链之间的实时、ZK 保护、原子性结算。 | §7.3 |
| **SIWE (Sign-In With Ethereum)** | 使用以太坊钱包签名进行身份认证的标准。在 Prividium 中用作钱包原生用户的认证方式，替代传统的用户名/密码。 | §3.4.1 |
| **OIDC (OpenID Connect)** | 基于 OAuth 2.0 的身份认证协议。Prividium 通过 OIDC 集成企业 SSO 系统（如 Okta），将企业身份与链上钱包地址绑定。 | §3.4.1 |
| **Airbender** | ZKsync 第二代 ZK 证明系统（Rust + CUDA），基于 RISC-V 架构。Atlas 升级引入，官方声称为全球最高性能的开源 RISC-V 证明系统。 | §3.2 |
| **Boojum** | ZKsync 第一代 ZK 证明系统，FRI-based STARK-like 证明系统。已部署在 zkSync Era 主网。 | §3.2 |
| **Private Block Explorer** | Prividium 的私有区块浏览器。分为公开版（受访问规则限制）和内部版（运营方完全访问），基于用户角色展示不同级别的链上数据。 | §3.4.5 |
| **Selective Disclosure (选择性披露)** | 允许数据所有者向特定方（如监管机构）有选择地证明或展示部分数据，而不暴露全部信息的机制。Prividium 通过审计角色、Merkle 证明和 ZK 合规证明实现。 | §3.6 |
| **Bank Stack** | Matter Labs 提出的概念框架，将 ZKsync 定位为"以太坊的银行堆栈"，包含区块链平台、货币/资产和服务/治理三个集成层。 | §7.1 |
| **Open Core (开放核心)** | Prividium 的许可模式。ZK Stack 核心组件完全开源（MIT/Apache 2.0），而企业模块（Proxy RPC、Permissioning System、Private Explorer）需商业许可。 | §6.4 |

---

## 12. 完整参考链接

### 一级来源 — 官方技术文档 (11 页)

最高证据强度。这些是 Prividium 的正式产品文档，描述当前已实现的功能和架构。

| 页面 | URL |
|------|-----|
| 概述 | https://docs.zksync.io/zk-stack/prividium/overview |
| 功能特性 (5 大支柱) | https://docs.zksync.io/zk-stack/prividium/features |
| 架构 (5 组件 + 认证流) | https://docs.zksync.io/zk-stack/prividium/architecture |
| 部署模型 (三层生产模型) | https://docs.zksync.io/zk-stack/prividium/deployment |
| Proxy RPC (三步验证) | https://docs.zksync.io/zk-stack/prividium/proxy |
| 用户管理 (OIDC/SIWE/混合) | https://docs.zksync.io/zk-stack/prividium/administration-user-management |
| 权限 (RBAC 框架) | https://docs.zksync.io/zk-stack/prividium/permissions-overview |
| TypeScript SDK | https://docs.zksync.io/zk-stack/prividium/sdk |
| 私有区块浏览器 | https://docs.zksync.io/zk-stack/prividium/explorer |
| 开发者指南 | https://docs.zksync.io/zk-stack/prividium/developer-considerations |
| 许可模式 (开放核心) | https://docs.zksync.io/zk-stack/prividium/license |

### 二级来源 — 官方产品声明与博客

来自 Matter Labs 自有渠道。包含产品定位、性能声称和合作关系公告。作为 Prividium 开发方的一手信息，但需注意营销角度。

| 标题 | 日期 | URL |
|------|------|-----|
| 企业登陆页 | — | https://zksync.io/enterprise |
| The Bank Stack | — | https://zksync.io/blog/the-bank-stack |
| Cari Network 旗舰项目 | 2026.03.17 | https://zksync.io/blog/cari-selects-zksyncs-prividium |
| 5 家美国银行深度分析 | 2026.03.20 | https://zksync.io/blog/five-us-banks-are-moving-to-zksync |
| BitGo 合作伙伴关系 | 2026.03.25 | https://zksync.io/blog/bitgo-and-zksync-partner-to-power-bank-adoption |
| LF Decentralized Trust (含 Deutsche Bank 提及) | 2026.04.21 | https://zksync.io/blog/matter-labs-joins-linux-foundation-decentralized-trust |
| TCMAG (12 条核心原则) | 2026.04.21 | https://zksync.io/blog/tokenized-cash-management-advisory-group |
| 隐私 ≠ 反合规 (CLARITY Act) | 2026.02.23 | https://zksync.io/blog/privacy-and-compliance-are-not-opposites |
| 2026 路线图 | 2026.01.13 | https://zksync.io/blog/zksync-roadmap-2026 |
| 托管服务 / RaaS | 2025.12.15 | https://zksync.io/blog/zksync-managed-services-raas |
| Atlas 升级 (>15K TPS) | 2025.10.07 | https://zksync.io/blog/introducing-the-zk-stacks-atlas-upgrade |

### 三级来源 — 代码仓库

开源代码可独立验证。企业模块（Prividium 特有组件）不在公开仓库中。

| 仓库 | 说明 | URL |
|------|------|-----|
| Matter Labs 组织 | 主组织 | https://github.com/matter-labs |
| ZKsync Era 核心 | Rust 87.8% | https://github.com/matter-labs/zksync-era |
| 智能合约 | 含 PrividiumTransactionFilterer | https://github.com/matter-labs/era-contracts |
| Airbender RISC-V Prover | Rust + CUDA | https://github.com/matter-labs/zksync-airbender |
| 文档源码 | 含 Prividium 页面 | https://github.com/matter-labs/zksync-docs |

### 四级来源 — ZK Stack 通用文档

底层技术参考。这些文档描述 ZK Stack 框架，Prividium 构建在其之上。

| 页面 | URL |
|------|-----|
| ZK Stack 概述 | https://docs.zksync.io/zk-stack |
| ZKsync 文档根 | https://docs.zksync.io/ |
| Era 核心开发者文档 | https://matter-labs.github.io/zksync-era/core/latest/ |

### 补充联系信息

| 资源 | URL |
|------|-----|
| Prividium SDK (npm) | `npm: prividium` (MIT 许可) |
| Prividium 商务联系 | bizdev@matterlabs.dev |

---

*本文档基于 2026 年 5 月 6 日可获取的公开信息编制，2026 年 5 月 7 日根据 Review 反馈修订。所有引用内容均来自 zkSync 官方文档、博客和产品页面。性能数据均为官方声明，未经独立第三方验证。企业合作关系信息以各案例标注的证据强度为准。*
