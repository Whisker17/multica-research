# EVM 隐私方案最终调研报告

> **项目**: evm-privacy-research  
> **受众**: Mantle 技术决策层  
> **分支**: `research/evm-privacy-research/final-report`  
> **数据锚点**: 2026-06-23（所有上游研究截至此日期）  
> **综合方**: Technical Writer Agent  

---

## 执行摘要

本报告综合 10 个已完成研究模块的成果，为 Mantle 提供 EVM 生态隐私方案的全景评估与落地策略建议。

**核心发现：**

1. **没有单一"最隐私"方案**——需求必须先区分「代币/价值隐私账本」(Ledger A) 与「业务状态/执行隐私账本」(Ledger B)，两者需要完全不同的技术栈。
2. **轻量级可接入是硬约束**——经四项否决条件 (V1 新链/VM, V2 新桥, V3 全节点运维, V4 硬分叉) 筛选后，27 个规范方案中仅约 10 个 Candidate 级方案通过 Mantle 接入测试。
3. **建议双分叉策略 (Dual-Fork)**：
   - **Fork A（代币隐私）**：主选 ERC-7984 + OpenZeppelin Confidential Contracts 栈；备选 VOSA-RWA 封闭 PoC。
   - **Fork B（业务执行隐私）**：主选 Zama fhEVM 协处理器（须通过 Gate-ZKMS-Mantle 门控）；备选 Paladin 隐私组 Sidecar。
4. **ACL 撤销是跨方案结构性风险**——FHE ACL 不可撤销性和 ERC7984Hooked 模块授权持久性是 GDPR/合规的共性障碍。
5. **R8（订单流/抗 MEV）缺口**——所有推荐方案均未覆盖，需独立工作流。

---

## 一、评估框架与需求定义

> 源：`privacy-landscape-framework/final.md`（WHI-254）

### 1.1 八维企业隐私需求模型

本研究以八维企业隐私需求 (R1–R8) 作为统一评估基准：

| 编号 | 需求维度 | 说明 |
|:---:|---------|------|
| R1 | 金额隐私 | 交易金额对外不可见 |
| R2 | 余额隐私 | 账户余额对外不可见 |
| R3 | 身份/地址隐私 | 交易对手身份不可关联 |
| R4 | 业务逻辑/合约状态隐私 | 智能合约执行过程与中间状态不可见 |
| R5 | 交易图谱隐私 | 资金流向关系不可追踪 |
| R6 | 合规可审计 | 监管/审计方可受控访问隐私数据 |
| R7 | 选择性披露 | 数据所有方可按需向指定方披露指定粒度信息 |
| R8 | 订单流/抗 MEV | 交易意图在执行前不被观测 |

**关键分水岭**：R4 是区分 Ledger A（代币账本）与 Ledger B（业务状态账本）的硬界限。几乎所有代币层和屏蔽池方案均不覆盖 R4，仅 FHE/TEE/GC 协处理器和隐私组 Sidecar 以 Bolt-on 形式提供 R4。

### 1.2 五轴评估标尺

每个方案沿以下五轴评估：

1. **密码学路线** — 技术族系（FHE / ZKP / TEE / GC / MPC / PG）、可信初始化、后量子叙事
2. **数据维度** — 覆盖 R1–R8 的完整度
3. **信任模型** — 密码学信任 / 硬件锚定信任 / 组织信任及混合形态
4. **部署形态** — 从纯合约 Bolt-on 到独立链的光谱，经 V1–V4 否决条件筛选
5. **合规/选择性披露** — 六维选择性披露向量（授权方、触发条件、载荷粒度、范围、可撤销性、泄漏面）

### 1.3 隐私账本二义性

"隐私账本"存在两种语义：

- **Ledger A（Token Ledger）**：代币余额、转账金额和交易图谱的隐私保护。覆盖 R1/R2/R3/R5。
- **Ledger B（Business-State Ledger）**：智能合约执行过程和中间状态的隐私保护。覆盖 R4。

Mantle 的"隐私账本、隐私转账、隐私余额"需求表述存在二义性——**A/B 分叉决策必须先于任何供应商评估**。

### 1.4 轻量级部署否决条件

| 编号 | 否决条件 | 含义 |
|:---:|---------|------|
| V1 | 新链 / 新 VM | 需要用户迁移至新执行环境 |
| V2 | 新桥 | 需要跨链资产桥接 |
| V3 | 全节点运维 | 需要运行独立全节点基础设施 |
| V4 | 硬分叉 | 需要 Mantle 协议层变更 |

触发任一否决条件的方案降级为"参考级"（仅借鉴设计理念，不直接集成）。

---

## 二、标准层：EVM 隐私代币标准全景

> 源：`erc7984-confidential-token/final.md`（WHI-255）、`privacy-eips-survey/final.md`（WHI-257）、`vosa-standards/final.md`（WHI-256）

### 2.1 ERC-7984 机密代币标准

ERC-7984 是账户模型机密可互换代币标准，所有余额和转账金额以 `bytes32` 不透明指针表示，在接口层实现技术中立（FHE / ZK / TEE / MPC 后端均可适配）。

**核心设计特征：**

- 非 ERC-20 兼容——全新设计，互操作性需通过 `ERC7984ERC20Wrapper`
- 操作员模型取代 Allowance——`setOperator(address, uint48)` 授予时间有限的无限额度转账权
- 8 种转账变体——跨三个正交维度（调用者类型 × 数据附加 × 接收方回调）
- 静默失败语义——余额不足时转账金额变为加密零，不 revert

**OpenZeppelin 合规扩展生态：**

| 扩展 | 功能 |
|------|------|
| ObserverAccess | 审计方只读查看余额/转账句柄 |
| Freezable | 账户冻结 |
| Restricted | 黑名单 |
| Rwa | RWA 角色管控（发行方/转让代理/合规检查） |
| Hooked | 可编程合规钩子（模块化） |
| ERC20Wrapper | 与 ERC-20 互操作桥接 |
| Omnibus | 综合地址隐藏 |
| IdentityCheck | ERC-3643 风格身份验证 |

**关键风险：**

- ACL 永久性——`ObserverAccess` 授予的历史句柄访问不可证明撤销；`Hooked` 模块授予的 ACL 在模块卸载后持续存在（源码注释确认）
- `discloseEncryptedAmount` 路径允许临时操作员权限升级为永久明文披露
- 非 FHE 后端实现缺失——技术中立仅限接口层；ZK/TEE/MPC 原型未公开发现
- ERC-7984 仍处于 Draft 状态

**对比 ERC-7945**：ERC-7945 具有更小的 ERC-20-like 接口面（2 函数、加密 Allowance、`bytes memory`），但缺乏等效的参考实现和审计记录，短期工程证据弱。

### 2.2 Privacy 相关 EIP 全景

通过六通道搜索方法学（EIPs 仓库 + ERC 仓库 + Magicians + ethresear.ch + AllEIPs + 上游交叉引用），筛选出 11 个候选标准。

**按 Mantle 相关性分级：**

| 相关性 | 标准 | 部署路径 |
|:---:|------|---------|
| **高** | ERC-5564/6538（隐身地址）、ERC-8065（ZK Wrapper）、Privacy Pools | 纯合约部署，无协议修改 |
| **中** | EIP-8182（统一屏蔽池）、ERC-8302/pERC-20（Open PR）、EIP-8093 `[unverified]` | 需 Mantle 侧适配 |
| **低** | EIP-7503、EIP-8250、EIP-8141、EIP-8105 | L1 硬分叉/协议层/架构不匹配 |

**重要边界说明：**

- ERC-5564/6538 隐身地址**仅**提供接收方匿名 (R3)，不隐藏金额 (R1)、余额 (R2) 或发送方
- EIP-8105（加密内存池）作者明确声明不改善用户隐私，仅针对 MEV 抵抗 (R8)
- 无 EIP 覆盖 R4（业务逻辑/合约状态隐私）
- 无统一的 EIP 级合规-隐私桥接标准 (R6+R7)
- EIP-8093 形式状态不可验证——ethereum/EIPs master 中未找到 `eip-8093.md` `[unverified]`
- EIP-8182 Hegota 纳入时间线 `[unverified]`

### 2.3 VOSA 标准族

VOSA（Virtual One-time Sub-Account）是三个 EVM 隐私代币草案（VOSA 原语、VOSA-20、VOSA-RWA），由单一作者 (louisliu2048) 于 2026 年初发布。

**设计取舍：**

- 显式牺牲交易图谱隐私换取简洁性和合规友好性
- UTXO 语义但无 Merkle 树——平坦 `mapping(address => bytes32)` + SPENT_MARKER，O(1) 查找
- ZK 电路约束量在 ~10³ 量级，支持浏览器端证明 <250ms（作者自报数据，未独立验证）
- VOSA-RWA 通过双 Groth16 证明门控：合规证明 + 交易守恒证明

**关键局限：**

- 转账图谱完全公开（设计意图，非缺陷）
- 无链上冻结机制（UTXO/一次性地址模型的结构性限制）
- 无 `forcedTransfer`——证券监管缺口
- 合规模型依赖链下可信服务——组织信任模型，非免信任密码学合规
- 成熟度极低：概念/预试点阶段，未审计，无 EIP 编号，无已知主网部署
- 所有性能数据为作者自报，未独立复现

**评估定位**：VOSA-RWA 仅适用于封闭机构试点——明确接受暴露图谱和可信服务模型的场景。**不得提升为生产主选**。

---

## 三、竞品层：密码学原语方案

> 源：`confidential-coprocessor/final.md`（WHI-258）、`zk-privacy-chain-aztec/final.md`（WHI-259）、`zk-shielded-pool/final.md`（WHI-260）

### 3.1 机密协处理器（FHE 家族）

三个方案共享同一部署范式：开发者编写带加密类型的标准 Solidity，链上仅存储密文句柄和 ACL，重密码学运算在链下协处理器异步执行。

#### Zama fhEVM

| 维度 | 评估 |
|------|------|
| 密码学路线 | TFHE + 9/13 阈值 MPC；后量子；无可信初始化 |
| 数据维度 | 金额、余额、逻辑、状态全保护 (R1/R2/R4)；身份/图谱不保护 |
| 信任模型 | 密码学 + 组织 + 硬件混合（KMS L1 + AWS Nitro Enclaves） |
| 部署形态 | 轻量级协处理器——通过 V1–V4 |
| 合规栈 | **最强**——完整 OZ 扩展生态（ObserverAccess, Restricted, Freezable, Rwa, Omnibus, IdentityCheck, Hooked） |
| 成熟度 | 2025-12 Ethereum 主网上线 |
| Mantle 障碍 | 当前仅支持 Ethereum 主网 + Sepolia；多链扩展为 H1-2026 路线图项。集成需等待官方支持或自托管全套 KMS/Gateway/Coprocessor 栈 |

**关键风险**：Zama 的信任模型是 FHE + 阈值 MPC KMS + Nitro TEE 混合体，而非纯密码学信任。KMS 层有 9/13 活性假设和 ≤1/3 拜占庭容错边界。

#### Inco Lightning

| 维度 | 评估 |
|------|------|
| 密码学路线 | TEE（Intel TDX）；FHE/MPC 在路线图中；非后量子 |
| 数据维度 | 与 Zama 相同 |
| 信任模型 | 硬件锚定（TEE）为主 |
| 合规栈 | 强——Circle 框架、ERC-3643 协会会员、委托查看 |
| 成熟度 | 2026-06-15 Base 主网上线 |
| Mantle 障碍 | 当前仅支持 Base；逃生舱/强制退出机制未确认 |

#### Fhenix CoFHE

| 维度 | 评估 |
|------|------|
| 密码学路线 | TFHE/BFV + EigenLayer 再质押；后量子 |
| 信任模型 | 密码学 + 经济信任 |
| 合规栈 | 弱——仅 permit 式封装；合规生态有限 |
| 成熟度 | **有争议**——博客称"Ethereum 主网 + Arbitrum 上线"但文档称"即将支持"。评为测试网为主 |

**协处理器家族共性风险**：FHE ACL 不可撤销性是整个家族的结构性弱点，构成 GDPR"被遗忘权"的合规障碍。所有性能数据均为供应商自报，无独立第三方基准测试。

### 3.2 ZK 隐私优先链：Aztec

Aztec 是以太坊首个去中心化隐私优先 L2，通过 Note/UTXO 模型（承诺 + 空值器）、客户端 ZK 证明 (PXE)、Noir/Aztec.nr 合约语言和多密钥架构实现密码学级全执行隐私。

**评估结论：**

- **隐私覆盖最全面**：R1–R5 完整覆盖，R8 部分（公共调用栈在提交后对排序器可见）
- **信任模型最纯粹**：纯密码学信任，排序器不接触隐私数据
- **成熟度最低**：Alpha 主网，存在未修补的关键证明系统漏洞（修复目标 v5，2026 年 7 月）
- **与 Mantle 不兼容**：显式拒绝 EVM、Solidity 和账户模型。触发 V1（独立 VM）+ V2（资产桥）否决

**可借鉴概念（非直接集成）**：

| 概念 | 借鉴优先级 |
|------|:---:|
| ZK 明文-密文证明（选择性披露） | **高** |
| 承诺/空值器模型 | 中 |
| 多密钥分层架构理念 | 中 |
| 全局隐私集（跨应用匿名集） | 中 |
| 读时作废（反关联） | 概念 |
| 标签密钥"发现不解密" | 低（当前未激活） |

### 3.3 ZK 屏蔽池方案

四个 ZK 屏蔽池方案共享 UTXO Note + 承诺 + 空值器 + Merkle 累加器 + 客户端 ZK 证明 + 链上池的表层范式，但在运行时基底和信任假设上存在根本分歧。

#### 方案对比矩阵

| 维度 | Railgun | Privacy Pools | Starknet STRK20 | Tornado Cash |
|------|---------|---------------|-----------------|-------------|
| 部署形态 | EVM 合约套件 ✓ | EVM 合约套件 ✓ | Cairo VM（V1 否决）✗ | EVM 合约套件（R6/R7 失败） |
| R6/R7 合规 | 查看密钥 + PPOI 排除 | 关联集包含/排除 + ASP + ragequit | 声称链上加密查看密钥 `[unverified]` | 无——死胡同 |
| 证明系统 | Groth16（需可信初始化） | zk-SNARK `[stack unverified]` | STARK（透明/后量子，但隐私层未审计） | Groth16 |
| Mantle 适配性 | **最佳 Bolt-on** | **强合规理论** | 最低适配 | 仅作教训参考 |

**Railgun**：Mantle 轻量级偏好下的最佳 EVM 屏蔽池候选。通过 V1–V4 否决条件。注意：查看密钥不可撤销（GDPR 张力）；PPOI 仅排除式（无正向包含证明）；**当前未在 Mantle 部署**——可行性为架构推断。

**Privacy Pools**：合规理论最强（Buterin 等人分离均衡），支持包含证明、可选 ASP 和 ragequit 回退。注意：早期生产阶段（2025 上线）、匿名集小、ASP 当前由 0xbow 半许可式管理而非用户可选。

**Tornado Cash 教训**：2022 年 OFAC 制裁证明"无选择性披露 = 死胡同"。2024-11 Van Loon 裁定和 2025-03 OFAC 解除制裁是狭窄的法律修正，不逆转设计教训。

---

## 四、竞品层：EEA 企业基准

> 源：`eea-enterprise-benchmark/final.md`（WHI-261）

EEA 7 方案（Paladin、Prividium、Linea Enterprise、Nightfall、COTI-L2/Coprocessor、Polygon CDK、Silent Data）对 R1–R8 的覆盖矩阵：

| 方案 | R1 | R2 | R4 | R6 | R7 | 信任模型 | 部署 |
|------|:---:|:---:|:---:|:---:|:---:|---------|------|
| Paladin | ● | ● | ◐ | ◐ | ● | 组织+密码学 | Sidecar ✓ |
| Prividium | ● | ● | ● | ● | ● | 混合 | Validium（V3） |
| Linea Ent. | ● | ● | ● | ◐ | ● | 混合 | Validium（V3） |
| Nightfall | ● | ● | ✗ | ◐ | ◐ | 密码学+组织 | Rollup（V3） |
| COTI-L2 | ● | ● | ◐ | ◐ | ◐ | 混合 | 独立链（V1/V2）|
| COTI-Coproc. | ●† | ●† | ◐† | ◐† | ◐† | 混合 | 协处理器 ✓ |
| Polygon CDK | ● | ● | 可配置 | ● | ● | 可配置 | Validium（V3） |
| Silent Data | ● | ● | ● | ◐ | ● | 硬件锚定 | Optimistic L2（V1/V3） |

● = 完整保护 ◐ = 部分 ✗ = 无 † = 继承但未验证

**轻量级筛选结果**：经 V1–V4 否决条件筛选，7 方案中仅 **Paladin**（Sidecar）和 **COTI-Coprocessor** 通过 Mantle 轻量级接入测试。

**关键发现：**

- R4 是决定性分水岭——Nightfall 是唯一纯代币方案；其余 6 个均提供某种形式的合约逻辑/业务状态隐私
- 成熟度分层：COTI-L2 是唯一 GA 级方案（但触发 V1/V2 否决）；Silent Data 为 Early Production（但审计透明度不足）；其余均为 Pilot
- Prividium 在合规披露向量上最强；Silent Data 是唯一硬件锚定 (TEE) 方案
- **旁注发现**：Secret Network 机密 EVM 路线于 2026 年正式暂停；Automata 链上 TEE 证明验证器是真正的 Bolt-on 验证原语，可强化任何基于 TEE 的方案；Solana Confidential Transfers 的 ZK 证明程序自 2025-06 因可靠性漏洞被禁用

---

## 五、横向对比：统一决策矩阵

> 源：`cross-comparison/final.md`（WHI-262）

### 5.1 候选方案分级

横向对比覆盖 27 个规范方案 + 5 个旁注/参考方案，按三级判定分类：

**Candidate（可直接使用）**：

| 方案 | A/B 类型 | 核心价值 |
|------|:---:|---------|
| ERC-7984 | A | 机密代币接口锚点 + OZ 合规扩展 |
| ERC-7945 | A | 轻量 ERC-20-like 替代接口 |
| ERC-5564/6538 | A（R3 仅） | 接收方匿名基础设施 |
| ERC-8065 | A | ZK 代币包装器 |
| Railgun | A | EVM 最成熟屏蔽池 |
| Privacy Pools | A | 合规理论最强的屏蔽池 |
| Zama fhEVM | A+B | 最完整 FHE 协处理器 + 合规栈 |
| Inco Lightning | A+B | 机构合规叙事 + TEE 速度 |
| Paladin | A+B（Noto=A, Pente=B）| 隐私组 Sidecar + 企业工作流 |
| COTI-Coprocessor | A+B | 混淆电路协处理器（Pilot） |

**Conditional Candidate（方向正确但成熟度不足）**：

VOSA/VOSA-RWA、ERC-8302/pERC-20、Fhenix CoFHE、EIP-8093 `[unverified]`、Automata（TEE 证明组件）

**Reference（不可 Bolt-on 但设计可借鉴）**：

Aztec、Nightfall、Prividium、Linea Enterprise、Polygon CDK、Silent Data、EIP-8182、EIP-7503、Oasis Sapphire、Solana Confidential Transfers

**Out（与 Mantle 轻量级集成根本不匹配）**：

COTI-L2、Starknet STRK20、Secret Network EVM 路线

### 5.2 A/B 账本 × 部署形态矩阵

```
                    Bolt-on (V1-V4 通过)          中等            独立链 (V1/V2+)
                    ────────────────────    ─────────────    ─────────────────
Ledger A (代币)     ERC-7984, ERC-7945,     Nightfall        EIP-8182,
                    ERC-8065, ERC-8302,                      EIP-7503,
                    Railgun, Privacy Pools,                  Starknet STRK20
                    Stealth (R3 only),
                    VOSA/VOSA-RWA

Ledger B (业务)     —                       —                Silent Data,
                                                             Linea Enterprise

Ledger A+B          Zama, Inco, Fhenix,     —                Aztec, Prividium,
                    COTI-Coproc., Paladin                    Polygon CDK,
                                                             COTI-L2
```

### 5.3 已解决冲突

| 编号 | 冲突 | 解决方案 |
|:---:|------|---------|
| F1 | 主矩阵 Axis-1 对技术族系处理过浅 | 扩展为包含可信初始化、后量子叙事和路线可组合性列 |
| F2 | Privacy Pools 在 WHI-257 标为"A+B"但 WHI-260 标为"非 R4" | **判定**：Privacy Pools = 纯 A（代币/流量隐私）+ R6/R7 合规叠加层 |
| M1 | Privacy Pools R3 在不同模块间标记不一致 | **归一化**：R3 = 完整 (●) |

---

## 六、Mantle 隐私策略建议

> 源：`mantle-privacy-strategy/final.md`（WHI-263）

### 6.1 双分叉策略 (Dual-Fork)

A/B 分叉决策必须先于任何供应商洽谈。将需求错误归类会导致选择错误的技术栈。

#### Fork A：代币隐私账本

```
主选 ─── ERC-7984 / OZ Confidential Contracts
  │       接口锚点 + ObserverAccess/RWA/Restricted/Freezable/Hooked/Wrapper
  │       门控：Mantle 上可验证的机密代币后端 + 可审计 ACL/观察者历史 + KMS/解密 SLA
  │
备选 ─── VOSA-RWA 封闭 PoC
  │       仅限明确接受暴露图谱和可信服务模型的封闭机构试点
  │       单一作者、未审计、无主网部署——不得提升为生产主选
  │
组件 ─── Railgun（资金来源 + 图谱隐私组件）
          Privacy Pools（合规叠加层组件）
```

#### Fork B：业务执行隐私

```
主选 ─── Zama fhEVM 协处理器
  │       任意加密合约状态 (R4) + ERC-7984/OZ 合规栈最强耦合
  │       门控 (Gate-ZKMS-Mantle)：
  │         ① 确认 Mantle 链支持（官方或自托管全栈）
  │         ② 商业许可
  │         ③ 性能验证
  │         ④ ACL 撤销/审计追踪验证
  │
备选 ─── Paladin 隐私组 Sidecar (Pente/Noto/Zeto)
          Zama 门控失败或业务域天然为小封闭群体时激活
          Pente 在隐私组内实例化临时私有 EVM，状态哈希锚定到主链
          限制：域内可见性、N-of-N 活性（最适合 2–10 成员）、有限公共匿名性
```

### 6.2 实施路线图

| 阶段 | 内容 |
|:---:|------|
| **Phase 0** | 冻结 A/B 范围：将所有用例映射到 R1–R8；建模合规角色（发行方/审计方/监管方/ASP/隐私组成员） |
| **Phase 1** | 运行 ERC-7984/OZ 测试网 PoC（Observer/RWA/Restricted/Wrapper）；VOSA-RWA 封闭 PoC；Privacy Pools + Railgun 资金来源组件实验 |
| **Phase 2** | 执行 Gate-ZKMS-Mantle（Zama 门控）；并行运行 Paladin Sidecar PoC |
| **Phase 3** | 受限机构试点——资产上限、披露注册表（ACL/查看/关联/组审计追踪） |
| **Phase 4** | 生产门控——全合约审计、后端 SLA/活性验证、撤销策略、治理签批、独立 R8 路线图项 |

---

## 七、跨切面分析

### 7.1 共识

以下结论在多个研究模块中独立得出并互相印证：

1. **R4 是 A/B 分水岭**——所有研究模块一致认定 R4 区分代币隐私与业务状态隐私
2. **轻量级 Bolt-on 是硬约束**——V1–V4 否决条件在框架 (WHI-254)、企业基准 (WHI-261) 和横向对比 (WHI-262) 中一致应用
3. **Zama fhEVM 是 Fork B 的首选**——机密协处理器 (WHI-258)、横向对比 (WHI-262) 和策略 (WHI-263) 三个模块独立推荐
4. **ERC-7984 是 Fork A 的接口锚点**——标准分析 (WHI-255)、横向对比 (WHI-262) 和策略 (WHI-263) 一致认定
5. **ACL 撤销是跨方案结构性风险**——ERC-7984 (WHI-255)、协处理器 (WHI-258) 和策略 (WHI-263) 均独立标记
6. **"无选择性披露 = 死胡同"**——Tornado Cash 教训在屏蔽池 (WHI-260)、EIP 全景 (WHI-257) 和横向对比 (WHI-262) 中反复引用

### 7.2 冲突与解决

| 编号 | 冲突描述 | 解决结果 | 来源 |
|:---:|---------|---------|------|
| F1 | 横向对比 Axis-1 对技术族系处理过浅 | 扩展列（可信初始化、后量子、可组合性） | WHI-262 |
| F2 | Privacy Pools A/B 标记不一致 | 判定：纯 A + R6/R7 叠加层 | WHI-257 vs WHI-260，WHI-262 裁定 |
| M1 | Privacy Pools R3 覆盖度不一致 | 归一化为完整 (●) | WHI-260，WHI-262 确认 |
| — | Zama 信任模型描述差异 | 统一为"FHE + 阈值 MPC KMS + Nitro TEE 混合"，非纯密码学 | WHI-258 vs WHI-263 |

### 7.3 开放问题

| 编号 | 问题 | 影响范围 | 负责方 |
|:---:|------|---------|-------|
| O1 | Zama 官方 Mantle 链支持时间表不明 | Fork B 主选可行性 | Mantle BD / Zama |
| O2 | FHE ACL 历史撤销语义——ObserverAccess 和 Hooked 模块 | Fork A + B 合规基础 | 需深入 Zama ACL 文档/源码审查 |
| O3 | Inco 强制退出/逃生舱机制未确认 | Inco 作为 Fork B 替代方案可行性 | Inco 团队确认 |
| O4 | Fhenix 主网真实状态（博客 vs 文档矛盾） | Conditional Candidate 评级准确性 | 链上合约地址或团队确认 |
| O5 | COTI-Coprocessor 多链能力为公告/Pilot，非 GA | Candidate 评级可靠性 | 独立验证 |
| O6 | VOSA 可信初始化仪式是否完成 | PoC 安全性基准 | 未知 |
| O7 | R8（订单流/抗 MEV）——所有推荐栈均未覆盖 | 需独立工作流 | Mantle 产品/研究 |
| O8 | 各方案后量子叙事为上游继承或推断，未独立密码学验证 | 长期安全评估 | 密码学专项审查 |

### 7.4 研究注记

- Aztec "约 185,000"数据须使用「测试网/社区参与者」表述，非主网用户
- EIP-8182 Hegota 时间线 `[unverified]`；Discourse 搜索计数为时间点快照
- 所有供应商性能数据为自报，无独立基准测试
- 横向对比中的后量子叙事为上游研究继承或 TW 推断，非独立密码学验证 `[TW inference]`

---

## 附录

### A. 输入研究模块清单

| 序号 | 模块 | 议题 | 主题 | 主分支合并提交 | 对抗审查 |
|:---:|------|------|------|:---:|:---:|
| 0 | WHI-254 | privacy-landscape-framework | 评估框架与需求定义 | — | 轻量模式 |
| 1 | WHI-255 | erc7984-confidential-token | ERC-7984 机密代币标准 | `fdbda370` | approve, minor |
| 2 | WHI-256 | vosa-standards | VOSA 标准族 | — | ‡ |
| 3 | WHI-257 | privacy-eips-survey | Privacy EIP 全景 | `957773b1` | approve, minor |
| 4 | WHI-258 | confidential-coprocessor | 机密协处理器 | — | ‡ |
| 5 | WHI-259 | zk-privacy-chain-aztec | ZK 隐私优先链 Aztec | `eceaef1e` | approve, minor |
| 6 | WHI-260 | zk-shielded-pool | ZK 屏蔽池 | — | ‡ |
| 7 | WHI-261 | eea-enterprise-benchmark | EEA 企业基准 | — | ‡ |
| 8 | WHI-262 | cross-comparison | 横向对比 | `9c81049e` | approve, minor |
| 9 | WHI-263 | mantle-privacy-strategy | Mantle 隐私策略 | `eefb63d9` | approve, minor |

> ‡ WHI-256/258/260/261 已完成研究流程（final.md 在 main 上，issue 状态 done），但未通过 Orchestrator 向 TW 保留议题投递正式 Research Complete。内容已纳入综合，溯源标记保留。

### B. 模块索引参考

引用自 `evm-privacy-research/research-sections/_index.md`：

| order | topic_slug | multica_issue_id | status |
|:---:|-----------|-----------------|:---:|
| 1 | erc7984-confidential-token | f0035b6e-4f0d-4a98-80ad-2f68d46c40be | done |
| 2 | privacy-eips-survey | 3f53d683-eefb-4af0-ae59-8ee77f02c537 | done |
| 3 | zk-privacy-chain-aztec | e7283682-53ae-4f3f-a33b-df6393c27d52 | done |
| 4 | cross-comparison | 836219a8-d7c5-49d7-af1a-cb9335b19072 | done |
| 5 | mantle-privacy-strategy | d84d0da4-88a7-49b0-a83a-ba171a78adc3 | done |

> 另有 5 个模块的 final.md 在 main 上但不在 _index.md 中：privacy-landscape-framework（轻量模式）、vosa-standards、confidential-coprocessor、zk-shielded-pool、eea-enterprise-benchmark（pipeline 缺口，非内容缺口）。

### C. 方法论说明

1. **评估框架**：基于 WHI-254 建立的八维需求模型 (R1–R8)、五轴评估标尺和四项轻量级否决条件 (V1–V4)
2. **搜索方法学**：WHI-257 采用六通道搜索（EIPs 仓库 + ERC 仓库 + Magicians + ethresear.ch + AllEIPs + 上游交叉引用），搜索记录可重现
3. **信任模型分类**：密码学信任 / 硬件锚定信任 / 组织信任三类，含混合形态
4. **成熟度分级**：参考 EEA Readiness Matrix（Pilot / Early Production / General Availability）
5. **溯源规则**：每个结论追溯到具体 issue ID 和 GitHub section 路径；TW 添加的推断标记为 `[TW inference]`
6. **未验证标记**：来源无法独立确认的数据点标记为 `[unverified]`
7. **数据锚点**：所有上游研究截至 2026-06-23

### D. 术语表

| 缩写 | 全称 |
|------|------|
| FHE | Fully Homomorphic Encryption 全同态加密 |
| GC | Garbled Circuit 混淆电路 |
| MPC | Multi-Party Computation 多方计算 |
| TEE | Trusted Execution Environment 可信执行环境 |
| ZKP | Zero-Knowledge Proof 零知识证明 |
| PG | Privacy Group 隐私组 |
| ACL | Access Control List 访问控制列表 |
| KMS | Key Management Service 密钥管理服务 |
| ASP | Association Set Provider 关联集提供方 |
| PPOI | Private Proof of Innocence 私有清白证明 |
| UTXO | Unspent Transaction Output 未花费交易输出 |
| PXE | Private eXecution Environment 私有执行环境 |
| DA | Data Availability 数据可用性 |
| EEA | Enterprise Ethereum Alliance 企业以太坊联盟 |
| RWA | Real-World Assets 现实世界资产 |
| GDPR | General Data Protection Regulation 通用数据保护条例 |
