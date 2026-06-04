# 合规 Token 标准调研：最终研究报告

> **项目**: 合规 Token 标准调研（compliance-token-standards）
>
> **版本**: Final Report v1.0
>
> **日期**: 2026-06-05
>
> **编制**: Technical Writer Agent（基于 7 份研究 Section 整合）

---

## 执行摘要（Executive Summary）

本报告整合了合规 Token 标准调研项目的全部 7 份研究产出，为 Mantle（OP Stack L2 / RWA 机构化定位）提供从行业全景到落地策略的完整研究框架。

### 核心发现

**1. 设计范式的结构性分歧**

合规 Token 标准沿两条截然不同的技术路线演进：

- **应用层合规**（ERC-3643 / ERC-1400）：合规逻辑以 Solidity 智能合约形式部署在 EVM 解释执行层。优势为跨链可移植性与独立升级能力，代价为 Gas 开销高（2-8× ERC-20）与合约间调用的执行不确定性。
- **协议层合规**（B20 / TIP-20）：合规逻辑以 precompile 形式固化在节点原生执行层。优势为极低 Gas 开销与行为一致性保证，代价为链锁定与硬分叉升级依赖。

这一分歧不是功能差异，而是架构位置差异——它决定了执行保证强度、Gas 成本结构和升级治理模型。

**2. 成熟度梯度显著**

| 标准 | 成熟度（/30） | 状态 | 生产验证 |
|------|:---:|------|------|
| ERC-3643 | 28 | Final ERC (2023) | $32B+ 代币化，92+ 协会成员（含 DTCC/Apex/Invesco） |
| TIP-20 | 19 | Tempo 链标准 | 主网运行，KlarnaUSD 已部署 |
| ERC-1400 | 11 | Draft（从未 finalize） | 核心维护者全部流失，事实废弃 |
| B20 | 10 | Beryl 硬分叉前 | 零生产部署 |

ERC-3643 是唯一 Final ERC 合规标准，成熟度遥遥领先。ERC-1400 作为标准已失败但其设计遗产（partition/tranche 模型、ERC-1643 文档管理接口）影响了后续标准。B20 和 TIP-20 共同证明协议层合规的技术可行性，但处于 emerging signal 阶段。

**3. 合规能力覆盖呈互补格局**

- ERC-3643 在 Identity/KYC（ONCHAINID claim-based）与 Recovery（identity-level 恢复）上最强
- B20/TIP-20 在 Transfer Policy（multi-slot policy registry）与 Sanctions（BurnBlocked + BLOCKLIST）上更结构化
- TIP-20 在 Payment Reconciliation 上独具全栈优势（Payment Lanes + Fee AMM + StablecoinDEX）
- ERC-1400 在 Legal Document（ERC-1643）上有独特贡献

没有任何单一标准覆盖全部 8 类合规能力。

**4. Mantle 策略建议**

采用 **"ERC-3643 先行 + 混合路线评估 + 原生标准远期决策"** 的分阶段策略：

- **短期（0-3 月）**：ERC-3643 PoC 验证需求并建立合规基础设施（无协议层依赖，可立即启动）
- **中期（3-6 月）**：评估 PolicyRegistry precompile 原型与混合架构可行性（受限于下一次硬分叉窗口尚未公布）
- **长期（6-12 月）**：基于数据做出原生标准的最终路线决策

### 证据分类说明

本报告采用以下证据分类体系，所有 claim 均标注证据类型：

| 证据类型 | 定义 | 适用标准 |
|---------|------|---------|
| primary-source | EIP 规范、官方文档可直接验证 | ERC-3643, ERC-1400 |
| code-confirmed | 代码分析可直接验证（pinned commit） | B20 |
| code-inferred pending spec | 代码推断但公开规范未发布 | B20 |
| docs-stated | 官方文档声明但源码未同步验证 | TIP-20 |
| secondary | 第三方分析 | 所有标准 |
| inferred | 跨源推理 | 所有标准 |
| 本地分支观察 | 仅存在于本地分支，非远程 HEAD | B20Security |

---

## 第一部分：行业背景与评估框架

> 主要来源：WHI-177 compliance-token-landscape

### 1.1 监管环境

全球主要司法管辖区的合规 Token 监管呈现差异化推进态势：

**欧盟**：DLT Pilot Regime（Regulation 2022/858）于 2023 年 3 月正式生效，首次为基于 DLT 的金融工具交易和结算提供法律框架。该法规允许经批准的市场基础设施在 DLT 环境下运营，但对代币化证券设置了严格的资产规模上限。MiCA（Markets in Crypto-Assets Regulation）于 2024 年全面实施，为稳定币与加密资产服务提供者建立了统一的欧盟级监管框架。

> **[G1 监管护栏]** 欧盟的 DLT Pilot Regime 与 MiCA 是独立的法规框架，分别针对 DLT 金融工具与加密资产。本报告引用时严格区分两者适用范围，不做混淆。

**美国**：DTC（Depository Trust Company）于 2025 年 12 月获得 SEC 交易与市场部的 no-action letter，允许其开发 DLT 原型以支持代币化证券的发行、转让和清算。SEC 新任主席 Atkins 在 2025 年讲话中正面引用代币化技术在证券市场的潜在应用。GENIUS Act 为稳定币提供联邦级立法框架。

> **[G2 监管护栏]** DTC no-action letter 是 SEC 工作人员对 DTC 特定方案的不采取行动建议，不构成对任何特定代币标准的监管认可或背书。本报告引用此 letter 时严格限于说明监管环境趋势，不做过度推演。

**亚太**：香港 SFC 于 2023 年发布代币化证券的监管指引（SFC Circular）；新加坡 MAS 通过 Project Guardian 探索代币化债券与基金。

### 1.2 RWA 市场规模

截至 2026 年 5 月，链上真实世界资产（RWA）代币化市场规模约 **$33.9B**（数据来源：RWA.xyz）。关键增长驱动力包括：

- 机构级参与者入场（DTCC、BlackRock BUIDL 基金、Franklin Templeton FOBXX、Apex Group $3.5T AUM）
- 美国国债代币化快速增长
- 稳定币作为合规支付基础设施的角色强化（KlarnaUSD 等银行级发行）

### 1.3 合规能力分类体系（8 类 Taxonomy）

WHI-177 建立了 8 类合规能力分类体系，作为评估所有标准的统一框架：

| 类别 | 说明 |
|------|------|
| **1. Identity / KYC** | 链上身份验证与准入控制 |
| **2. Transfer Policy** | 转移限制规则引擎 |
| **3. Issuer Controls** | 发行方操作能力（冻结/铸造/销毁/暂停） |
| **4. Sanctions / Blacklist** | 制裁执行与地址过滤 |
| **5. Recovery** | 资产恢复与密钥轮转 |
| **6. Legal Document / Metadata** | 法律文档与结构化元数据管理 |
| **7. Payment Reconciliation** | 支付对账与交易引用 |
| **8. Auditability / Privacy** | 审计追踪与隐私保护 |

### 1.4 评估维度体系（7 维度 + 扩展）

基础 7 维度评估框架：架构层级、合规机制类型、身份模型、DeFi 可组合性、发行方控制力、Gas 开销、标准成熟度。

横评阶段（WHI-182）扩展为 9 维度，新增跨链能力、支付优化、升级与治理。另设独立的 6 维度规范成熟度评估表。

---

## 第二部分：标准深度分析

### 2.1 ERC-3643（T-REX 协议）

> 主要来源：WHI-178 erc3643-trex-analysis

#### 架构

ERC-3643 采用 **6 组件协作架构**，全部以 Solidity 智能合约实现：

| 组件 | 职责 |
|------|------|
| **Token Contract** | ERC-20 兼容的合规 token 主合约，集成转移前合规验证钩子 |
| **ONCHAINID** | 基于 ERC-734/735 的链上自主身份容器（per-user 独立合约） |
| **Identity Registry (IR)** | wallet 地址 → ONCHAINID 身份映射注册表 |
| **Identity Registry Storage (IRS)** | IR 的持久化存储层（允许 IR 逻辑升级而不丢失映射数据） |
| **Trusted Issuers Registry (TIR)** | 受信任的 Claim 签发者白名单管理 |
| **Claim Topics Registry (CTR)** | token 要求的 Claim 主题定义（如 KYC、合格投资者） |
| **Modular Compliance** | 可插拔规则引擎（投资者上限、司法管辖限制、锁定期等） |

#### ONCHAINID 身份系统

ONCHAINID 是四大标准中唯一的完整链上自主身份（self-sovereign identity）系统：

- 4 类密钥：Management（身份管理）/ Action（执行操作）/ Claim Signer（签发声明）/ Encryption（加密通信）
- Claim 存储 hash 引用而非 PII 原文，提供隐私保护（但非协议层强制——ERC-735 的 bytes data / string uri 字段不限制 PII）
- 密钥轮转不影响已签发的 Claims——组织架构变更（如 KYC 服务商更换密钥）不中断持有者的合规状态
- 跨 token 复用同一 ONCHAINID

#### 合规执行流程

标准 transfer 路径执行 **receiver-only** 身份验证：

```
transfer(from, to, amount)
  │
  ├── Identity Registry: isVerified(to)
  │     ├── 查询 to 的 ONCHAINID
  │     ├── 遍历 CTR 要求的 Claim Topics
  │     └── 验证 Claim 签发者是否在 TIR 白名单中
  │
  ├── Compliance Module: canTransfer(from, to, amount)
  │     └── 遍历所有已绑定的 Compliance Module
  │
  └── 执行转账或 revert
```

#### forcedTransfer 作用域

`forcedTransfer` 绕过 `canTransfer()` 检查和发送方余额验证，但接收方仍必须通过 `isVerified(_to)` 验证且 `transferred()` 钩子仍被调用。[primary-source: WHI-178]

#### Agent 角色系统

ERC-3643 的 Agent 角色支持以下操作：freeze（全地址冻结）/ partial freeze（部分冻结）/ forced transfer / recovery（identity-level 恢复：资产转移 + Identity Registry 映射同步更新）/ pause / mint / burn，以及 7 种 batch 操作变体。

#### 升级机制

UUPS Proxy（ERC-1822）+ Implementation Authority pattern 实现多 token 统一升级。Compliance Module 可独立替换。

#### 成熟度与生态

- **成熟度 28/30**——六维度评估中五项最高分
- **$32B+ 资产代币化**（ERC-3643 Association 自报），**92+ 协会成员**
- 机构采用：DTCC（ComposerX，2025-03）、Apex Group（$3.5T AUM）、Invesco、ABN AMRO（€5M green bond）、Fasanara Capital（Polygon MMF）
- 审计：Hacken 10/10 评分、Kaspersky 审计
- DTC no-action letter 引用 [G2 适用]

#### 8 类合规能力覆盖

| 能力 | 覆盖 | 说明 |
|------|------|------|
| Identity/KYC | **Full** | ONCHAINID claim-based 自主身份 |
| Transfer Policy | **Full** | Compliance Module 可插拔规则引擎 |
| Issuer Controls | **Full** | Agent role 全套操作 + batch ops |
| Sanctions | **Partial** | Compliance Module blacklist + Claim 撤销 |
| Recovery | **Full** | 专用 recovery 机制（identity-level 恢复） |
| Legal Doc | **None** | 无原生文档管理 |
| Payment Recon | **None** | 无原生支付功能（定位为证券标准） |
| Audit/Privacy | **Partial** | 全链上审计；ONCHAINID 不存储 PII 但无 ZKP 机制 |

### 2.2 ERC-1400（Security Token Standard）

> 主要来源：WHI-179 erc1400-series-analysis

#### 架构

ERC-1400 是一个 **umbrella standard**，由 4 个子标准组成：

| 子标准 | 职责 |
|--------|------|
| **ERC-1410** | Partially Fungible Token——partition/tranche 模型 |
| **ERC-1594** | Core Security Token——发行控制与 `_data` 参数 |
| **ERC-1643** | Document Management——链上文档管理 |
| **ERC-1644** | Controller Token Operation——"God Mode" 强制操作 |

#### 核心设计哲学

以 **partition（分区）** 为中心的资产建模——同一 token 的不同 partition 可具有不同的权利、限制和属性（如优先级不同的债券 tranche、不同锁仓期的股权份额）。`_data` 参数为 operator 提供灵活的链下信息注入点。

#### 关键安全发现

ConsenSys Diligence 2020 年审计发现 **`setDefaultPartitions` 漏洞**——攻击者可通过设置 default partition 绕过 partition 级别的 whitelist 检查。已在 PR #13 修复。[primary-source: WHI-179]

#### 标准状态与生态

- **Draft 状态**——4 个子标准均为 Draft，从未达到 Last Call 或 Final
- **核心维护者全部流失**：Polymath → 迁移至 Polymesh 链；Securitize → 转向自有协议栈；ConsenSys UniversalToken → 2025-03 archived
- 活跃生产级部署趋近零
- `_data` 参数格式**非标准化**，各实现之间不可互操作

#### 设计遗产

ERC-1400 虽作为标准已失败，但其设计遗产影响了后续标准：
- partition/tranche → ERC-7518 (DyCIST)
- ERC-1643 Document Management → CMTAT v3.0.0 采纳
- ERC-1644 Controller "God Mode" → 后续标准视为反模式，B20/TIP-20 均选择细粒度 RBAC 替代

#### 8 类合规能力覆盖

| 能力 | 覆盖 | 说明 |
|------|------|------|
| Identity/KYC | **Partial** | 无原生身份层，依赖 `_data` 注入 |
| Transfer Policy | **Partial** | `_data` + operator，但格式非标准化 |
| Issuer Controls | **Full** | ERC-1644 Controller 最强单点控制（但权限过度集中） |
| Sanctions | **None** | 无标准级制裁机制 |
| Recovery | **Full** | controllerTransfer 可用于恢复（依赖 controller 权限集中） |
| Legal Doc | **Full** | ERC-1643——四大标准中唯一原生文档管理 |
| Payment Recon | **None** | `_data` 理论上可传支付引用但非结构化 |
| Audit/Privacy | **Partial** | partition 级别事件可审计；无隐私设计 |

### 2.3 TIP-20（Tempo 链预编译标准）

> 主要来源：WHI-180 tempo-tip20-analysis
>
> **关键证据约束（C1）**：TIP-20 的所有 claim 均基于 docs.tempo.xyz 官方文档（docs-stated），C1 代码仓库源码未获得同步验证。报告中标注了 8 项需源码验证才能确认的能力缺口。

#### 架构

TIP-20 以 **precompile 套件**形式实现，包含 4 个固定地址预编译合约：

| 组件 | 地址 | 职责 |
|------|------|------|
| **TIP20Factory** | `0x20Fc` | token 创建工厂，确定性地址推导 |
| **TIP403Registry** | `0x403c` | 合规策略注册表（whitelist/blacklist/compound） |
| **TipFeeManager** | `0xfeec` | 交易费管理（Fee AMM 固定汇率 0.9970） |
| **StablecoinDEX** | `0xdec0` | 稳定币 DEX（end-of-block 批量匹配） |

`tempo_precompile!` 宏强制 direct-call-only 模式，禁止通过中间合约 delegatecall。[docs-stated]

#### TIP-403 策略系统

- 策略类型：whitelist / blacklist / compound（TIP-1015）
- Compound policy 结构：三个独立子策略（sender / recipient / mint recipient），结构不可变但被引用策略可由各自 admin 修改
- 内置策略：always-reject (ID=0) / always-allow (ID=1)
- 存储结构：3-slot（sender / recipient / mint recipient），对比 B20 的 4-slot（多一个 executor 维度）

#### 支付基础设施全栈

TIP-20 在四大标准中**独具全栈支付优化能力**，反映 Tempo 作为支付专用链的定位：

- **Payment Lanes**：55% 区块空间保证分配给支付交易
- **Fee AMM**：per-tx 固定汇率 0.9970，0.3% LP fee——每笔交易独立定价，非批量
- **StablecoinDEX**：end-of-block 批量匹配
- **TIP-1034 Channel Reserve**：protocol-native 支付通道
- **TIP-1035 Implicit Approval List**：免 DEX approve 步骤

#### RBAC 与发行方控制

4 角色模型：ISSUER（mint/burn/mintWithMemo/burnWithMemo）/ PAUSE / UNPAUSE / BURN_BLOCKED。

`burnAt`（TIP-1006）支持从任意地址 burn。Pause/Unpause 角色分离设计——安全团队可暂停，高管审批恢复。无 forced transfer，无 partial freeze。

#### 扩展 TIP 生态

7 个扩展 TIP 已分析：TIP-1004（Batch Transfer）、TIP-1006（Burn From）、TIP-1015（Compound Policy）、TIP-1022（Virtual Address Deposit Forwarding）、TIP-1026（Logo URI）、TIP-1034（Channel Reserve）、TIP-1035（Implicit Approval List）。

#### Chainalysis 集成

Chainalysis 自动 token 监控与 memo 解码 AML 监控已确认（2026-03 公告）。但 **自动 policy blacklist 更新**未在公开文档中确认。[docs-stated]

#### Tempo Zones 隐私

Tempo Zones 提供隐私执行环境（parallel blockchains + ZKP/MPC），采用"privacy, not secrecy"模型——Zone operator 有可见性，regulatory access keys 支持审计。TIP-403 政策在 Zone 内仍强制执行。[docs-stated]

#### 8 类合规能力覆盖

| 能力 | 覆盖 | 说明 |
|------|------|------|
| Identity/KYC | **Partial** | TIP-403 whitelist/blacklist + Chainalysis 集成 |
| Transfer Policy | **Full** | TIP-403 + TIP-1015 compound policies |
| Issuer Controls | **Partial** | RBAC 4-role + burnAt |
| Sanctions | **Full** | BURN_BLOCKED + blacklist + Chainalysis |
| Recovery | **Partial** | 无 forced transfer；TIP-1022 存款恢复 |
| Legal Doc | **Partial** | ISO 4217 currency() + TIP-1026 logoURI + memo |
| Payment Recon | **Full** | Payment Lanes + Fee AMM + StablecoinDEX + Channel Reserve + memo |
| Audit/Privacy | **Partial** | 链上审计 + Tempo Zones 隐私 |

### 2.4 B20（Base Beryl 预编译标准）

> 主要来源：WHI-181 base-b20-analysis
>
> **关键证据约束**：B20 的所有 claim 基于 pinned commit `base/base@8e8767281d7c8768f6a0aed9124779cd4ed030ae` 代码分析。公开 Beryl 规范截至分析日期（2026-06-04）尚未发布，所有结论为代码推断（code-inferred pending spec）。B20Security 相关内容仅存在于本地分支，标记为"本地分支观察/演进信号"。

#### 架构

B20 采用 **Rust trait 组合模式** 构建，以预编译合约形式实现：

| 模块 | 地址 | 职责 |
|------|------|------|
| **B20Factory** | `0xB20F...0000` | 单例工厂 precompile，确定性地址推导 |
| **B20Asset** | 动态（`0xb2` + `0x00`） | 资产变体（乘数缩放、批量铸造、公告、扩展元数据） |
| **B20Stablecoin** | 动态（`0xb2` + `0x01`） | 稳定币变体（ISO 4217 货币标识） |
| **PolicyRegistry** | `0x8453...0002` | 四维合规策略引擎 |
| **ActivationRegistry** | `0x8453...0001` | 硬分叉特性激活门控 |

核心设计哲学为**能力 trait 组合**（capability-trait composition）：`Token` trait 作为中央桥接层，7 个能力 trait（Transferable/Mintable/Burnable/RoleManaged/Pausable/Configurable/Permittable）通过关联类型 `Accounting: TokenAccounting` 与 `Policy: Policy` 实现编译期单态化，消除虚表开销。[code-confirmed]

#### IB20 Solidity 接口

完整接口包含 **50 个函数**、**16 个事件**、**22 个错误类型**。支持 ERC-20 / EIP-2612（permit）/ ERC-5267（eip712Domain）/ ERC-7572（contractURI）兼容。[code-confirmed]

#### PolicyRegistry 四维策略

B20 将策略检查细化为四个独立范围——TransferSender / TransferReceiver / TransferExecutor / MintReceiver——每个 token 可为每个范围绑定不同的策略 ID。策略类型为 ALLOWLIST（白名单）或 BLOCKLIST（黑名单）。

策略 ID 为 u64 类型（高 8 位 = 类型判别符，低 56 位 = 单调递增计数器），4 个策略 ID 紧凑打包进 2 个 U256 存储槽。[code-confirmed]

内置策略：`ALWAYS_ALLOW`（空黑名单 → 授权所有人）、`ALWAYS_BLOCK`（空白名单 → 拒绝所有人）。

#### RBAC 7 角色系统

DefaultAdmin / Mint / Burn / BurnBlocked / Pause / Unpause / Metadata。Asset 变体额外有 OPERATOR_ROLE（公告 + 乘数更新）。

`renounceLastAdmin()` 为**不可逆操作**——最后一个 admin 放弃权限后，所有角色变更永久冻结，token 进入不可变状态。[code-confirmed]

#### B20Asset 独有能力

- **乘数机制（Multiplier）**：读时缩放（`scaledBalance = rawBalance × multiplier / WAD`），无需重写所有账户余额存储。WAD_PRECISION = 1e18。
- **批量铸造（batchMint）**：全量或零原子批量铸造，无批次上限（受 gas 约束）。
- **公告机制（Announcement）**：OPERATOR_ROLE 发布通知 + 原子执行配套操作（如批量铸造、乘数更新）。单次 ID + 重入防护双重安全。
- **扩展元数据（extraMetadata）**：任意 KV 存储，已在 Beryl 测试中验证证券标识符（ISIN/CUSIP/FIGI）用例。

#### burnBlocked 合规机制

`burnBlocked(from, amount)` 要求目标账户被 TransferSender 策略阻止（反向检查：`ensure_blocked` 验证 `is_authorized == false`）。这是 B20 合规能力的关键组成——允许合规管理者销毁被冻结账户的 token。[code-confirmed]

#### ZK 证明可行性

Beryl 包含 ZK 证明干运行基准（`b20_zk_proving.rs`），覆盖 10 种操作。作为 precompile 实现，B20 的执行轨迹固定且可预测，对 ZK 证明器效率至关重要。[code-confirmed]

#### B20Security 演进信号

> **[本地分支观察，非当前 Base 主线事实]**

本地分支超前提交中观察到 `b20_security/` 模块，新增 `SECURITY_OPERATOR_ROLE`、`BURN_FROM_ROLE`、`redeem`/`redeemWithMemo`、`batchBurn`、`securityIdentifier`（专用字段，非 KV extraMetadata）、`sharesToTokensRatio`。表明 B20 演进方向可能包括证券 token 专业化，但这些功能**不纳入 B20 主线能力评估或 Mantle 策略决策的硬证据**。

#### 8 类合规能力覆盖

| 能力 | 覆盖 | 说明 |
|------|------|------|
| Identity/KYC | **Partial** | PolicyRegistry ALLOWLIST/BLOCKLIST 间接实现 |
| Transfer Policy | **Full** | PolicyRegistry 4-slot，跨 token 共享 |
| Issuer Controls | **Full** | RBAC 7-role + Pausable 功能级 + supply cap + announcement |
| Sanctions | **Full** | BurnBlocked + BLOCKLIST policy |
| Recovery | **Partial** | 无 forced transfer；可通过 burnBlocked + mint 间接实现（非原子） |
| Legal Doc | **Partial** | Metadata role + extraMetadata KV + ERC-7572 contractURI + announcement |
| Payment Recon | **Partial** | mintWithMemo/burnWithMemo（32-byte memo）+ currency() |
| Audit/Privacy | **Partial** | 全链上审计 + ZK proving benchmark |

---

## 第三部分：横向对比

> 主要来源：WHI-182 compliance-token-comparison

### 3.1 设计范式分类

| 范式 | 执行位置 | 标准 | 核心特征 |
|------|---------|------|---------|
| **应用层合规** | Solidity → EVM 解释执行层 | ERC-3643, ERC-1400 | 跨链可移植 / 独立升级 / Gas 高 |
| **协议层合规** | Precompile → 原生执行层 | B20, TIP-20 | 链锁定 / 硬分叉升级 / Gas 低 |

### 3.2 技术维度对比核心发现

**架构层级**：ERC-3643 采用 6 协作 Solidity 合约，ERC-1400 为 4 子标准 umbrella。B20 以 Rust precompile 实现（B20Factory + PolicyRegistry + ActivationRegistry），TIP-20 以 4 个 precompile 组成套件。

**合规机制**：ERC-3643 采用 on-chain identity（claim-based）路线，是唯一具备完整链上身份层的标准。B20/TIP-20 均采用 policy registry 路线，无原生身份但在策略结构化程度上不亚于 ERC-3643 Compliance Module。ERC-1400 依赖 `_data` 参数注入（非标准化）。

**Gas 效率**：ERC-3643 约 2-8× ERC-20（多次外部合约调用）[inferred]。ERC-1400 中-高（partition 嵌套 mapping + 辅助数组）[inferred]。B20/TIP-20 均为低开销（precompile 原生执行绕过 EVM 解释器）[code-inferred / docs-stated]。

**DeFi 可组合性**：ERC-3643 保持 ERC-20 兼容但合规检查 revert 可导致 DeFi 协议静默失败。ERC-1400 的 partition 概念与 `_data` 要求破坏标准接口预期。B20 在 Base 生态内 ERC-20 兼容 + ZK-provable。TIP-20 通过 StablecoinDEX 原生集成 + TIP-1035 免 approve。

**跨链能力**：ERC-3643 任意 EVM 链可部署（已在 Ethereum/Polygon/Avalanche/Hedera 多链运行），LayerZero DvP + Wormhole Foundation 成员。B20 仅限 Base 链，TIP-20 仅限 Tempo 链（LayerZero 桥接）。ERC-1400 理论上 EVM 可移植但 `_data` 不兼容导致跨实现不可互操作。

### 3.3 规范成熟度评估（6 维度 × 4 标准）

| 维度 | ERC-3643 | ERC-1400 | B20 | TIP-20 |
|------|:---:|:---:|:---:|:---:|
| 正式标准化状态 | 5 | 2 | 1 | 3 |
| 公开 Spec 可用性 | 5 | 3 | 2 | 4 |
| 网络激活状态 | 5 | 2 | 1 | 4 |
| 参考实现 | 5 | 2 | 3 | 3 |
| 真实采用 | 5 | 1 | 1 | 3 |
| 单一依赖风险 | 3 | 1 | 2 | 2 |
| **总分（/30）** | **28** | **11** | **10** | **19** |

> 总分仅供排序参考。单一维度的阻断性影响（如 B20 零网络激活、ERC-1400 无维护者）无法被其他维度高分补偿。

### 3.4 合规能力覆盖矩阵（8 类 × 4 标准）

| 能力类别 | ERC-3643 | ERC-1400 | B20 | TIP-20 |
|---------|:---:|:---:|:---:|:---:|
| Identity/KYC | Full | Partial | Partial | Partial |
| Transfer Policy | Full | Partial | Full | Full |
| Issuer Controls | Full | Full | Full | Partial |
| Sanctions/Blacklist | Partial | None | Full | Full |
| Recovery | Full | Full | Partial | Partial |
| Legal Doc/Metadata | None | Full | Partial | Partial |
| Payment Recon | None | None | Partial | Full |
| Audit/Privacy | Partial | Partial | Partial | Partial |

**核心观察**：没有任何单一标准覆盖全部 8 类能力。ERC-3643 在 Identity 与 Recovery 上独占 Full 评级；ERC-1400 在 Legal Doc 上独占 Full；TIP-20 在 Payment Recon 上独占 Full；B20/TIP-20 在 Sanctions 上优于 ERC-3643/ERC-1400。

### 3.5 关键跨切面洞察

**Insight A: 协议层合规趋势判断**

协议层合规（precompile 路线）正在形成 **emerging signal**（趋势强度 2/5），但尚未成为 established pattern。B20 + TIP-20 两个数据点 + Circle Arc（testnet 2025）+ Plume（Arbitrum Orbit L2）提供补充信号。驱动力清晰（性能、Gas、标准化、监管确定性），但大规模 production 验证不足。

**Insight B: 应用层 vs 协议层——竞争还是互补？**

短期竞争，长期存在**互补路径**的结构性条件（趋势强度 1/5，speculative）。假设路径：ERC-3643 ONCHAINID 作为跨链合规身份层 + B20/TIP-20 policy registry 作为链内高效执行层。实现条件：policy registry 需能读取链上 ONCHAINID claim 状态——目前两者均不支持。

**Insight C: 成熟度阻断效应**

公开 Spec 可用性与真实采用是阻断性维度。B20 公开规范未发布 → 第三方无法独立审计 → 机构无法评估 → 采用阻断。ERC-1400 核心维护者流失 → 无持续支持保障 → 机构无法依赖。

**Insight D: ERC-1400 的设计遗产**

标准的失败不等于设计的失败。`_data` 非标准化 + 子标准碎片化 + 维护者流失 → 生态瓦解。后续标准（ERC-3643 Compliance Module、B20/TIP-20 policy registry）均选择标准化合规接口替代灵活但非标准的 `_data` 注入。

**Insight E: TIP-20 支付独特性**

TIP-20 的支付全栈（Payment Lanes + Fee AMM + StablecoinDEX + Channel Reserve）在四大标准中无对应。这不是其他标准的功能缺口，而是 Tempo 作为支付专用链的差异化定位决定的。

**Insight F: B20 架构成熟度 vs 部署成熟度**

B20 的架构设计（7-role RBAC + 4-slot policy + ActivationRegistry + ZK proving）展现较高的架构成熟度，但零网络激活与零生产部署构成实质限制。

### 3.6 核心 Trade-off

| 标准 | 核心优势 | 核心代价 |
|------|---------|---------|
| **ERC-3643** | 跨链可移植 + 成熟生态 + 唯一 Final ERC + 完整链上身份 + 机构信任 | Gas 高 + DeFi 可组合性受限 + Tokeny 中心化风险 |
| **ERC-1400** | partition/tranche 建模能力 + ERC-1643 文档管理 | Draft 未 finalize + 非标准互操作 + 核心维护者流失 + 事实废弃 |
| **B20** | 协议层行为一致性 + Base 生态 + RBAC 精细 + ZK proving | 仅限 Base + 规范未发布 + 零生产部署 + 无 forced transfer |
| **TIP-20** | 支付全栈 + precompile 低 Gas + Chainalysis 集成 + Stripe/Klarna 背景 | 仅限 Tempo + 源码未验证 + 生态早期 + RBAC 粒度粗 + 无 forced transfer |

---

## 第四部分：Mantle 策略建议

> 主要来源：WHI-183 mantle-compliance-token-strategy

### 4.1 Mantle 技术栈现状

**OP Stack 架构**：Mantle 基于 OP Stack 构建，采用 Optimistic Rollup，运行 **op-geth + reth 双执行客户端架构**。

**硬分叉演进**（本地代码仓库验证）：

| 硬分叉 | 对齐 | 主网激活日期 | 状态 |
|---|---|---|---|
| Everest | — | 2025-03-19 | 已激活 |
| Skadi | Ethereum Prague | 2025-08-27 | 已激活 |
| Limb | Ethereum Osaka | 2026-01-14 | 已激活 |
| Arsia | 重大架构升级（Gas 重构） | 2026-04-22 | 已激活 |
| 下一次 | 未知 | **未公布** | 代码中仅有 `// ADD NEW FORKS HERE!` 占位符 |

**关键技术约束**：
- Mantle **当前不存在任何自定义 precompile**，仅包含标准 EVM 预编译与 BLS12-381 曲线操作
- 引入合规 precompile 需修改 op-geth 与 reth 双客户端，通过硬分叉部署
- **下一次硬分叉尚未规划**——precompile 部署窗口当前不确定
- Mantle reth 基于 Rust 实现，理论上适合 B20 式 Rust trait 组合的 precompile 开发

### 4.2 市场定位与合规需求映射

Mantle 的战略定位指向 **RWA 机构化**场景。目标发行方画像包括机构投资者、RWA 发行方、合规金融机构。

**优先合规能力需求**：

| 优先级 | 能力 |
|------|------|
| P0 必需 | Identity/KYC、Transfer Policy、Issuer Controls（mint/burn/pause）、监管操作（冻结/强制转移/恢复） |
| P1 高度需要 | RBAC 权限管理、合规审计与链上可追溯 |
| P2 重要 | 跨链合规一致性、隐私保护合规 |

**mETH/cmETH 协同**：合规包装可使 mETH 进入机构可投资资产池，cmETH 合规版本可作为机构级抵押品。两条路线均可实现，但时间因素有利于 ERC-3643（选项 A 可在 3 月内实现）。

> **[TW inference]** mETH/cmETH 合规包装的具体技术方案尚未设计，协同分析为方向性评估。

### 4.3 三条路线技术分析

#### 选项 A：ERC-3643 智能合约路线

**可行性**：ERC-3643 全部合约为标准 Solidity，可在 Mantle 上**无修改直接部署**。ONCHAINID 的 `ecrecover` 使用标准 EVM precompile，完全可用。

**优势**：
- 最高标准成熟度（28/30）
- 无协议层改动，不依赖硬分叉，可立即启动
- 监管认可度最高（DTC no-action letter [G2 适用]、ERC Final 状态）
- 审计资源丰富

**劣势**：
- Gas 开销 2-8× ERC-20（Mantle L2 低 Gas 环境下绝对成本可控）
- 无法利用 Mantle 协议层差异化——与其他 EVM L2 的 ERC-3643 部署无差异
- 身份基础设施需在 Mantle 上建立或桥接

**开发周期**：1-3 月

#### 选项 B：Precompile 原生标准路线

以 Base B20（pinned commit）为主要 EVM L2 precompile 类比，TIP-20 为生产经验参考。

**优势**：
- Gas 效率——precompile 原生执行可降至 ERC-3643 的 1/3-1/5
- 协议层差异化——Mantle 成为原生支持合规 token 的 L2
- 与 B20 竞争对称
- reth 客户端 Rust 实现与 B20 Rust precompile 模式兼容

**劣势**：
- 开发周期长（12-18 月，参考 TIP-20 经验）
- 标准化风险——自建标准非 ERC Final，生态接受度不确定
- 双客户端维护负担（op-geth + reth）
- **硬分叉窗口不确定**

**开发周期**：12-18 月（不含等待硬分叉窗口）

#### 选项 C：混合路线

PolicyRegistry precompile + ERC-3643/ERC-20 adapter。

**优势**：
- 热路径（策略查询）由 precompile 原生执行，Gas 效率显著
- 保持应用层标准兼容，可复用 ERC-3643 生态
- 渐进式引入——可作为选项 A → 选项 B 的中间跳板
- 部分协议层差异化

**劣势**：
- 两层架构增加系统复杂度
- precompile 与 adapter 状态同步难度
- 升级协调难（precompile 需硬分叉，adapter 需代理模式）
- **硬分叉窗口同样不确定**
- 无先例验证

**开发周期**：6-9 月（不含等待硬分叉窗口）

### 4.4 决策矩阵

| 决策因素 | 权重 | 选项 A | 选项 B | 选项 C |
|---|:---:|:---:|:---:|:---:|
| 发行方需求匹配度 | 25% | 9 | 4 | 7 |
| 上市时间 | 20% | 10 | 2 | 5 |
| 协议层差异化价值 | 15% | 2 | 9 | 6 |
| 标准化与生态接受度 | 15% | 10 | 2 | 6 |
| 资源效率 | 15% | 9 | 4 | 6 |
| mETH/cmETH 协同 | 10% | 7 | 5 | 6 |
| **加权总分** | **100%** | **8.10** | **4.15** | **6.05** |

> 详细评分证据与置信度说明见 WHI-183 item-6.6。需验证维度：发行方需求匹配度（需实际调研验证）、mETH/cmETH 协同（具体方案未设计，投机性评估）。

### 4.5 分阶段实施建议

**短期 0-3 月：需求验证 + ERC-3643 可行性**

| 行动项 | 时间 | 产出 |
|---|---|---|
| 目标发行方需求调研 | M1 | 需求矩阵（合规能力需求 × 发行方类型） |
| ERC-3643 Mantle testnet PoC | M1-M2 | 完整部署报告 |
| ONCHAINID 身份基础设施评估 | M1-M2 | ClaimIssuer 对接方案 |
| Gas 基准测试（Arsia 后模型） | M2 | ERC-3643 vs ERC-20 Gas 对比数据 |
| mETH 合规 wrapper PoC | M2-M3 | 可行性报告 |
| MVP 范围定义 | M3 | 最小可行产品规格文档 |

**门控 G1**：发行方需求确认 + Gas 数据可接受 → 继续中期；需求不足 → 暂缓

**中期 3-6 月：混合路线评估**

| 行动项 | 时间 | 产出 |
|---|---|---|
| PolicyRegistry precompile 原型设计 | M4-M5 | 技术设计文档 |
| ERC-3643 ↔ precompile adapter PoC | M5-M6 | 混合架构 PoC + 对比数据 |
| 下一次硬分叉窗口评估 | M4 | 可行硬分叉窗口确认（如有） |
| B20 Beryl 发布后竞争分析更新 | M4-M6 | 竞争态势更新报告 |

**门控 G2**：混合路线正面 + 硬分叉窗口已确认 → 纳入硬分叉；否则 → 维持选项 A

**长期 6-12 月：原生标准最终决策**

基于短期/中期数据做出最终路线决策：

- **情景 1**（纯 ERC-3643）：需求满足、Gas 可控、差异化需求不强
- **情景 2**（混合路线）：PolicyRegistry 验证成功、硬分叉窗口已确认 → A + C
- **情景 3**（完整原生标准）：战略全面差异化、资源充足、B20 竞争压力明确 → A + B

### 4.6 即时可行动清单

以下基础工作无需等待路线决策即可启动：

1. 建立 KYC/AML 服务对接评估（2 周）
2. ERC-3643 在 Mantle testnet 的部署测试（1-2 周）
3. Gas 基准测试——ERC-3643 vs ERC-20（1 周）
4. 发行方需求访谈（3-5 家目标机构，2-3 周）
5. ONCHAINID 文档与 SDK 评估（1 周）

### 4.7 关键风险与缓释

| 风险 | 概率 | 缓释 |
|------|------|------|
| 下一次硬分叉延迟或排除合规 precompile | 中-高 | 选项 A 先行覆盖；推动合规 precompile 纳入硬分叉规划 |
| B20 Beryl 快速推进 | 中 | 加速混合路线评估；必要时提前启动选项 B |
| 发行方需求不足 | 中 | 需求调研前置，go/no-go 门控 |
| 自建标准生态接受度低 | 中-高 | 混合路线（选项 C）降低风险——保持 ERC-3643 兼容 |

---

## 第五部分：可溯源性矩阵

### 研究 Section → 报告章节映射

| Section | Issue ID | 报告章节 | 核心贡献 |
|---------|----------|---------|---------|
| WHI-177 compliance-token-landscape | f6a0c156 | 第一部分（行业背景）、第三部分（评估框架） | 8 类 Taxonomy、7 维度框架、监管环境、RWA 市场、范式分类 |
| WHI-178 erc3643-trex-analysis | 4036a12f | 第二部分 §2.1 | ERC-3643 六组件架构、ONCHAINID、Agent role、forcedTransfer 作用域、成熟度 |
| WHI-179 erc1400-series-analysis | cf57ea5d | 第二部分 §2.2 | 4 子标准、partition/tranche、ConsenSys 审计、设计遗产 |
| WHI-180 tempo-tip20-analysis | 586341f0 | 第二部分 §2.3 | Precompile 套件、TIP-403、Payment Lanes、Chainalysis、Tempo Zones |
| WHI-181 base-b20-analysis | bc5cf45c | 第二部分 §2.4 | B20 Rust 架构、PolicyRegistry 4-slot、RBAC、ZK proving、B20Security 演进信号 |
| WHI-182 compliance-token-comparison | c62bd179 | 第三部分（横向对比） | 9 维技术矩阵、6 维成熟度、8 类覆盖矩阵、6 跨切面洞察、Trade-off |
| WHI-183 mantle-compliance-token-strategy | 2f99210d | 第四部分（Mantle 策略） | 技术栈现状、三条路线、决策矩阵、分阶段实施 |

### 证据类型分布

| 证据类型 | 适用标准 | 报告中标注方式 |
|---------|---------|--------------|
| primary-source | ERC-3643, ERC-1400 | [primary-source: WHI-xxx] |
| code-confirmed | B20 | [code-confirmed: WHI-181] |
| code-inferred pending spec | B20 | [code-inferred] |
| docs-stated | TIP-20 | [docs-stated: WHI-180] |
| 本地分支观察 | B20Security | [本地分支演进线索] |
| TW inference | 报告综合推理 | [TW inference] |

---

## 第六部分：证据附录

### A. 监管护栏

| ID | 护栏内容 | 适用范围 |
|----|---------|---------|
| G1 | 欧盟 DLT Pilot Regime 与 MiCA 为独立法规框架，分别适用于 DLT 金融工具与加密资产 | 第一部分 §1.1 监管环境 |
| G2 | DTC no-action letter 为 SEC 工作人员对 DTC 特定方案的不采取行动建议，不构成对任何特定代币标准的监管认可或背书 | ERC-3643 成熟度引用 |

### B. 证据约束与缺口

| 约束/缺口 | 影响 | 严重度 | 缓释 |
|-----------|------|------|------|
| TIP-20 源码未验证（C1 约束） | TIP-20 所有 claim 为 docs-stated | 中 | 系统性标注证据边界 |
| B20 公开 Beryl 规范未发布 | B20 claim 为 code-inferred | 中 | 标注 pending spec |
| B20Security 仅本地分支可观察 | 不纳入主线评估 | 低 | 标记为演进信号 |
| Gas 定量对比缺失 | 无跨标准 per-transfer Gas benchmark | 中 | 使用定性描述 + 证据分类 |
| Mantle 下一次硬分叉未规划 | 选项 B/C 部署窗口不确定 | 高 | 选项 A 先行；推动硬分叉规划 |
| 发行方需求未经实际调研验证 | 策略建议的需求基础为推断 | 中 | 短期行动项 #4 前置验证 |
| mETH/cmETH 合规包装方案未设计 | 协同评估为方向性 | 低-中 | 需独立 PoC |
| 混合路线（选项 C）无先例验证 | 可行性信心水平受限 | 中 | 中期阶段 PoC 前置 |

### C. 代码基准与 Pinned Commits

| 仓库 | Commit | 用途 |
|------|--------|------|
| base/base | `8e8767281d7c8768f6a0aed9124779cd4ed030ae` | B20 全套分析 |
| base/docs | `bfff9ef27f2333ff57c3a62417f6c1f0174992f0` | Beryl 文档（有限） |
| Mantle 本地代码 | `/Users/whisker/Work/src/networks/mantle/` | 硬分叉时间线、precompile 现状 |

### D. 外部来源

| 类别 | 来源 |
|------|------|
| EIP/ERC 规范 | EIP-3643 (Final), EIP-1400/1410/1594/1643/1644 (Draft) |
| 官方文档 | docs.tempo.xyz, erc3643.org, T-REX GitHub |
| 监管文件 | DTC no-action letter (2025-12-11), Commissioner Peirce statement |
| 市场数据 | RWA.xyz (2026-05 查询) |
| 审计报告 | ConsenSys Diligence 2020 (ERC-1400), Hacken/Kaspersky (ERC-3643) |
| 第三方分析 | Chainalysis Tempo coverage (2026-03) |

---

## 修订日志

| 版本 | 日期 | 说明 |
|------|------|------|
| Final Report v1.0 | 2026-06-05 | 基于 7 份研究 Section（WHI-177/178/179/180/181/182/183）整合的最终报告。覆盖行业背景、4 标准深度分析、横向对比、Mantle 策略建议。证据分类体系贯穿全文。 |
