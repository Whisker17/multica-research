# WHI-346: 横向对比——合规、审计与监管适配对比分析

> **Issue**: WHI-346 | **Milestone**: M2 横向对比 | **Date**: 2026-05-06（review 修订：2026-05-10） | **Status**: Review 修订版
>
> **M1 Source Files**:
> - Canton: WHI-334 (docs), WHI-335 (architecture), WHI-336 (codebase)
> - Prividium: WHI-337 (docs), WHI-338 (architecture)
> - Tempo/Zones: WHI-339 (docs), WHI-340 (code)
> - Mantle: WHI-341 (baseline)
> - Industry: WHI-342 (industry survey)

---

## 目录

1. [合规能力矩阵](#1-合规能力矩阵)
2. [审计模型对比分析](#2-审计模型对比分析)
3. [监管框架适配评估](#3-监管框架适配评估)
4. [合规架构层次分析](#4-合规架构层次分析)
5. [对 Mantle 的合规方案推荐](#5-对-mantle-的合规方案推荐)

---

## 1. 合规能力矩阵

### 1.1 完整对比表

| 合规能力 | Canton | Prividium | Tempo/Zones | Mantle (baseline) |
|----------|--------|-----------|-------------|-------------------|
| **KYC/KYB 原生支持** | 应用层实现：Daml 模板可定义 `KYCCredential` 模式；授权模型可把已验证身份映射到合约参与方，但不是协议内建 KYC 注册表 | 网络入口强制：SSO（Okta OIDC / SIWE）+ Proxy RPC 的 JWT/钱包/函数权限验证；属于中间件强制，不是共识原生 | 地址级策略支持：TIP-403 whitelist/blacklist 可强制限制参与地址；但不等同于完整企业身份/KYB 联邦 | 无原生支持：纯无许可架构，任何地址均可提交交易 |
| **AML/CTF 实时监控** | 通过 Observer 模式实现：监管方可作为交易 Observer 实时接收交易通知，结合本地 ACS 数据做监控 | Operator 持有全部链数据，可接外部 AML 系统；“无 PII 制裁筛查”在 M1 中有明确架构描述，但公开实现细节有限 | Zone Sequencer 拥有完全交易可见性，可在 `prepare_l1_block()` 阶段执行 TIP-403 检查；但当前 Zone prover 尚未上线，执行正确性暂仍依赖 sequencer 诚实 | 无原生支持：Sequencer 有完全交易可见性，但未利用此能力做合规检查 |
| **交易监控与筛查** | Participant 本地审计日志支持交易级监控；Observer 获得其所观察合约的完整交易流水 | Private Block Explorer 提供角色化视图：Operator 版有全量数据访问，Auditor 版有只读观察权限；Proxy RPC 的三步验证记录完整审计日志 | Zone Sequencer 完全可见性支持实时监控；TIP-403 在 TIP-20 transfer 时强制执行 `transferAuthorized()` 检查 | L1 公开数据可审计但无结构化监控接口 |
| **OFAC/制裁名单筛查** | M1 研究数据不足：文档未明确描述制裁名单集成机制，但 Observer 模式支持监管方实时审查，可作为集成基础 | ZK 驱动的无 PII 制裁筛查是核心设计亮点；但公开资料更偏架构/产品说明，缺少可核对的实现接口 | TIP-403 blacklist 可承载制裁名单策略；名单同步与运营流程仍需链下 feed / 治理配合 | 无原生支持 |
| **Travel Rule 合规** | 未见直接实现：Daml 可建模所需信息流，但 M1 未给出标准化 Travel Rule 管道 | 未见直接实现：选择性披露、审计角色和证明导出为 Travel Rule 落地提供基础 | 未见直接实现：`revealTo` 仅提供受限 sender 归因能力，不构成完整 Travel Rule 工作流 | 无原生支持 |
| **选择性披露（监管方）** | 原生支持：Daml Observer 角色使监管方可被添加为合约观察者，获得实际交易数据（非证明）；子交易级隐私确保 Observer 仅看到被授权的部分 | 五种机制：(1) Merkle 证明导出，(2) 范围化审计角色，(3) ZK 合规证明，(4) Private Block Explorer 访问控制，(5) 数据室 / 数据库摘录；其中 ZK 合规证明公开接口仍有限 | 可向授权方开放 Private RPC 访问（X-Authorization-Token 认证）；authenticated withdrawal 支持受限 sender 归因（ECIES 加密给 `revealTo` 公钥），但当前无专门监管导出模块 | 无需选择性披露：所有交易数据在 L1 公开可见 |
| **监管报告 / 报表导出** | 强审计、弱全局报表：需由 Participant/Observer 显式聚合或导出，不擅长开箱即用的全网监管报表 | 最完整：审计员角色、Merkle 证明导出、数据库摘录、公共披露端点均可服务监管报告 | 代码中无显式审计导出模块；需基于 Private RPC、L1 events 和 sequencer 数据定制报表服务 | 原始链上数据公开，但无结构化监管报表、受限披露或合规导出接口 |
| **审计追踪不可篡改性** | 每个 Participant 维护本地 PostgreSQL 审计日志；Synchronizer 的 BFT 排序提供消息排序的不可篡改性；但审计追踪分布在各 Participant 本地 | 链上交易不可篡改（Validium ZK 证明提交到以太坊 L1）；Private Block Explorer 提供结构化审计访问；ZK 证明提供数学级别的正确性保证 | Zone batch transitions 锚定在 Tempo L1：`submitBatch()` 提供不可篡改时间线；但当前 batch proof 仍为空值路径，时间线锚定不等同于完整 validity-proof-backed 执行审计 | L1 数据完全不可篡改（以太坊安全性）；但所有数据公开，无结构化合规审计接口 |
| **交易可逆/冻结能力** | Daml 智能合约可定义冻结/撤销逻辑（如消耗性 Exercise 归档合约），但需在合约设计时预先内置 | 可通过 Operator 权限、函数级 RBAC 与合约暂停能力实现局部冻结；但公开文档未给出通用账户级冻结原语 | TIP-20 内置 pause control；TIP-403 blacklist / compound policies 可在预编译层阻断受限地址的转账行为 | 无原生支持：标准 OP Stack 无交易冻结能力；理论上可通过智能合约层实现（如 ERC-20 `pause()`） |
| **地理围栏 (Geofencing)** | M1 研究数据不足：Canton 文档未讨论地理围栏，但 Participant 级别的访问控制可按组织限制参与 | M1 研究数据不足：Prividium 文档未明确讨论地理围栏，但 Proxy RPC 的 SSO 集成可结合 IP/地理限制在网关层实现 | M1 研究数据不足：Tempo 文档未讨论地理围栏，但 TIP-403 whitelist 模式可限制参与地址范围 | 无原生支持 |

> **Source References**:
> - Canton KYC / Observer / GDPR: WHI-334 §3.6.3, §470; WHI-335 §5
> - Prividium KYC / RBAC / 审计导出: WHI-337 §3.4-§3.6; WHI-338 §4.1-§4.4
> - Tempo TIP-403 / Zone 当前状态: WHI-339 §3.7, §5.2; WHI-340 §10, §11.4, §12
> - Mantle baseline / finality: WHI-341 §4, §8.1

### 1.2 能力成熟度总评

| 项目 | 合规成熟度 | 核心优势 | 核心限制 |
|------|-----------|---------|---------|
| **Canton** | ★★★★☆ 生产级 | Observer 模式最成熟；公开材料显示已承载大规模真实资产流转 | 非 EVM；KYC 和全局报表更多依赖 Daml 应用层与显式聚合 |
| **Prividium** | ★★★☆☆ 商业化推进中 | 四层纵深防御最完整；选择性披露和私有浏览器工具链最系统化 | 首批生产部署仍在推进；合规证明部分公开实现细节不足；强依赖 Proxy RPC 中间件层 |
| **Tempo/Zones** | ★★★☆☆ L1 生产、Zone 早期 | TIP-403 预编译级策略模型清晰，地址级强制执行最强 | Zone prover 未上线；Zone 仍为 v0.1.0 早期开发；审计导出需定制开发 |
| **Mantle** | ★☆☆☆☆ 基线仅公开链能力 | Sequencer 拥有完全可见性，且已有明确的策略引擎插入点 | 无原生身份/合规/报表层；L1 数据公开限制隐私 |

---

## 2. 审计模型对比分析

### 2.1 审计架构概览

```
Canton                          Prividium                      Tempo/Zones                    Mantle
───────────                     ──────────                     ───────────                    ──────
                                                                                              
Participant A                   Operator                       Zone Sequencer                 Public L1
┌──────────┐                    ┌──────────┐                   ┌──────────┐                   ┌──────────┐
│ Local DB │ ← 完整审计日志     │ Full DB  │ ← 全量链数据     │ Full     │ ← 全量 Zone 数据  │ Blob/    │
│ (PostgreSQL)│                 │ + ZK     │                   │ Visibility│                  │ Calldata │
└────┬─────┘                    │ Proofs   │                   └────┬─────┘                   │ on L1    │
     │                          └────┬─────┘                        │                         └────┬─────┘
     │ Observer role                 │ Selective                    │ Private RPC                   │ Anyone
     ▼                               │ Disclosure                   │ (X-Auth-Token)                │ can derive
Regulator                            ▼                              ▼                               ▼
┌──────────┐                    Regulator                      Regulator                      Any Node
│ Sees actual│                  ┌──────────┐                   ┌──────────┐                   ┌──────────┐
│ sub-txns  │                   │ Sees what │                   │ Sees all  │                  │ Sees all  │
│ (data)    │                   │ operator  │                   │ Zone txns │                  │ L2 txns   │
└──────────┘                    │ discloses │                   │ via RPC   │                  │ (public)  │
                                └──────────┘                   └──────────┘                   └──────────┘
```

### 2.2 六维对比

#### 2.2.1 谁来审计？（审计主体）

| 维度 | Canton | Prividium | Tempo/Zones | Mantle |
|------|--------|-----------|-------------|--------|
| **主要审计主体** | 各 Participant 自审 + Observer 方外审 | Operator 集中管理 + 按需披露给审计方 | Zone Sequencer (内审) + 认证 RPC 访问者 (外审) | 任何 L1 全节点（无许可审计） |
| **审计数据来源** | Participant 本地 ACS + 交易日志 | 全量链数据 + ZK 证明 + Private Block Explorer | Sequencer 保留的 Zone 状态 + L1 batch commitments | L2 公共状态 + L1 blob/calldata / output roots |
| **自动化程度** | 链上自动记录，链下人工分析 | 链上 ZK 证明自动验证 + 链下 Explorer / 报表查询 | 链上策略自动检查 + 链下 RPC / 定制报表查询 | 链上数据公开、可自动索引；但缺少内建审计角色和监管报表语义 |

> **Source**: Canton — WHI-335 §5 企业特性表 (审计模型); Prividium — WHI-338 §4.3 (审计追踪); Tempo — WHI-340 §11.4 (审计数据流); Mantle — WHI-341 §8.1

#### 2.2.2 审计粒度

| 维度 | Canton | Prividium | Tempo/Zones | Mantle |
|------|--------|-----------|-------------|--------|
| **最细粒度** | **子交易级** — Merkle DAG 中每个 TransactionView 可独立加密/解密，不同 Observer 看到不同子集 | **交易级** — Private Block Explorer 按角色展示不同交易集合；RBAC 6 种权限控制函数级访问 | **交易级** — Sequencer 看到所有交易明文；L1 上 batch transition 为区块级摘要 | **交易级** — 所有 L2 交易可从 L1 数据完整推导 |
| **L1 锚定 / 证明粒度** | N/A（非 L1 rollup 架构） | **批次级** — ZK 证明覆盖整个批次的状态转换正确性 | **批次级锚定** — `submitBatch()` 提交 blockTransition / depositQueueTransition；当前代码路径 proof slot 仍为空 | **批次 / 输出根级** — L1 batch 数据 + `OPSuccinctL2OutputOracle` 的 proof-backed output root（默认 ZK 模式） |

> **Source**: Canton 子交易粒度 — WHI-335 §2.1, WHI-336 §TransactionView; Prividium 角色化视图 — WHI-338 §4.3; Tempo batch 粒度 — WHI-340 §10, §11.4; Mantle — WHI-341 §4

#### 2.2.3 审计延迟

| 维度 | Canton | Prividium | Tempo/Zones | Mantle |
|------|--------|-----------|-------------|--------|
| **实时审计能力** | **近实时** — Observer 通过 Sequencer 的消息路由与交易相关方同时收到通知 | **近实时** — Private Block Explorer 与链同步；Operator 可实时监控所有交易 | **近实时** — Zone Sequencer 在 `prepare_l1_block()` 阶段即可检查合规；Zone 与 L1 block 1:1 映射 | **近实时**（L2 RPC / 全节点可见）；若以 L1 锚定为准则则需等待 batch 提交 |
| **L1 可验证延迟** | N/A | **分钟级** — ZK 证明提交到 L1 的延迟 | **当前为可配置 batch 提交**；完整 validity proof 路径仍待 prover 上线 | **双层** — 约 12 分钟获得 L1 batch 可见性；约 1 小时获得默认 ZK 模式的 proof-backed output root |

> **Source**: Canton Observer 实时性 — WHI-335 §3.1; Tempo 1:1 mapping — WHI-340 §7; Mantle finality — WHI-341 §4, §8.1

#### 2.2.4 审计成本

| 维度 | Canton | Prividium | Tempo/Zones | Mantle |
|------|--------|-----------|-------------|--------|
| **全量审计** | 每个 Participant 的本地存储成本；Observer 需要独立的 Participant 节点 | Operator 已持有全量数据，边际成本低；Private Block Explorer 已内置 | Zone Sequencer 已持有全量数据（WithdrawalStore 等），但无显式审计导出模块——需定制开发 | 任何全节点均可审计，但需完整推导 L2 状态（计算成本高） |
| **采样审计** | Daml 合约可设计抽样查询；Observer 可选择性订阅特定合约类型 | Merkle 证明支持选择性数据导出——可只导出特定交易的证明 | Private RPC 支持按账户/合约过滤查询 | 从 L1 数据中筛选特定交易成本较高 |

> **Source**: Prividium Merkle 证明导出 — WHI-338 §4.3 (选择性披露); Tempo 无审计模块 — WHI-340 §7.4 "No explicit audit export module in code"

#### 2.2.5 报表与导出能力

| 维度 | Canton | Prividium | Tempo/Zones | Mantle |
|------|--------|-----------|-------------|--------|
| **内置报告能力** | 强在可审计数据获取，弱在全局聚合；需要显式数据共享或外部报表服务 | 最完整：审计员角色、私有浏览器、公共披露端点、数据库摘录 | 无显式审计导出模块；需自建 exporter / reporting service | 无内置报告能力；主要依赖 block explorer、indexer 或第三方数据管道 |
| **证明型导出** | 可提供实际交易数据与合约事件，但不是 ZK / Merkle 风格的轻量证明导出 | Merkle 证明导出最强，可对单笔交易做独立验证 | 当前主要是 L1 events + batch commitments；无成型 proof export 工具 | 可导出原始链上数据与 output roots，但并非面向监管语义设计 |
| **监管报告适配度** | 中等：适合联盟内定制监管报表 | 高：最接近开箱即用的监管 reporting toolkit | 中等偏低：需要显式产品化补齐 | 低：需大量二次开发 |

> **Source**: Canton 全局聚合限制 — WHI-335 §1.1, §7.1; Prividium 报表工具链 — WHI-337 §3.6, WHI-338 §4.3; Tempo 导出缺口 — WHI-340 §11.4; Mantle — WHI-341 §8.1

#### 2.2.6 Sequencer 作为合规角色 ⭐

这是本次横向对比中的一个核心发现：**Tempo Zones 和 Prividium 都将 Sequencer（或 Operator）的完全交易可见性视为合规优势，而非隐私缺陷**。

| 维度 | Prividium (Operator) | Tempo/Zones (Sequencer) | Mantle (Sequencer) |
|------|---------------------|------------------------|-------------------|
| **角色定位** | Operator 是链的运营方和合规责任方 | Zone Sequencer 是"单序列器 Validium"的唯一执行者和合规检查方 | Sequencer 仅用于交易排序和区块生产 |
| **可见性** | 持有全部链数据 + ZK 证明 | 解密所有 encrypted deposits；看到所有交易明文；可读任意账户余额 | 有完全交易可见性（接收所有用户交易） |
| **合规利用** | 四层准入控制 + ZK 制裁筛查 + 选择性披露 + Private Block Explorer | TIP-403 检查在 `prepare_l1_block()` 中执行；黑名单地址 deposit 被 bounce back；但当前 Zone prover 未上线，因此正确性仍主要依赖 sequencer 诚实 | **未利用** — 当前仅做标准 OP Stack 排序 |
| **信任模型** | 用户必须信任 Operator 不滥用数据 | 用户必须信任 Sequencer 不滥用解密后的数据 | 用户已信任 Sequencer（中心化架构），但 Sequencer 不主动做合规 |

> **Source**: Prividium Operator 角色 — WHI-338 §2.3 (信任假设); Tempo Sequencer 合规 — WHI-340 §11.4, §7; Mantle Sequencer — WHI-341 §8.1

**关键洞察**：Mantle 的 Sequencer 已具备与 Tempo Zone Sequencer 和 Prividium Operator 相同的数据可见性条件。差异仅在于 Mantle 尚未将此可见性转化为合规功能。这是 Mantle 企业合规的最低成本切入点——不需要修改协议，仅需在 Sequencer 层添加策略引擎。

### 2.3 审计模型优劣势综合评估

| 审计特性 | 最优方案 | 理由 |
|---------|---------|------|
| **监管审计深度** | Canton | Observer 获得实际数据（非证明），可进行丰富分析、合规检查、纠纷解决 |
| **数学可验证性** | Prividium / Mantle（ZK 模式） | 二者都以 L1 验证的有效性证明保证状态转换；Prividium 额外结合私有数据面与选择性披露 |
| **协议层强制执行** | Tempo/Zones | TIP-403 precompile 级检查不可绕过（包括 delegatecall 被阻止） |
| **审计基础设施完整性** | Prividium | Private Block Explorer + RBAC + 选择性披露 + Merkle 证明导出——最完整的审计工具链 |
| **无许可审计** | Mantle | 完全公开——任何人可审计全部数据（但这也是隐私的缺失） |

> **Source**: Canton Observer 数据质量 — WHI-335 §2.4 "当 ZKP 失败时，它们是无声地失败——你无法确定性地告诉用户或监管方系统是否被攻破"; Tempo precompile 不可绕过 — WHI-340 §2.4 "All precompiles enforce direct-call-only — delegatecall returns DelegateCallNotAllowed"

---

## 3. 监管框架适配评估

### 3.1 MiCA（欧盟加密资产市场法规）

MiCA 对加密资产服务提供商 (CASP) 的关键要求包括：资产储备透明度、运营韧性、客户资产隔离、AML/CTF 合规。

| MiCA 要求 | Canton | Prividium | Tempo/Zones | Mantle |
|-----------|--------|-----------|-------------|--------|
| **CASP 注册/许可** | Canton Network 有 GSF 治理框架支持许可运营；Canton Coin MiCA 白皮书表明团队主动适配 MiCA | Prividium 作为企业私有链，运营方可按 MiCA 要求注册 | Tempo L1 主网已上线（WHI-340 代码校正）；但 Zone 私有栈仍早期，公开资料不足以判断其 CASP / EMT 合规边界 | Mantle 作为公开 L2，可复用现有加密资产服务框架；但 baseline 未显示面向 MiCA 的定向能力 |
| **AML/CTF** | Observer 模式支持监管接入 | ZK 制裁筛查 + 四层准入控制 | TIP-403 blacklist 支持制裁名单集成 | 无原生支持 |
| **客户资产隔离** | Participant 本地存储实现天然隔离 | 运营方持有全部数据，需通过流程保证隔离 | Zone 间天然隔离（每 Zone 独立 Sequencer） | 链上资产公开，无隔离机制 |
| **运营韧性** | 多 Synchronizer 后端（BFT/Ethereum/Fabric）支持冗余 | Validium 架构：执行层可冗余，但 Operator 是单点 | Zone Sequencer 无 P2P 冗余（NoopConsensus）；L1 锚定提供安全性 | op-conductor 提供 HA Sequencer 容错 |

> **Source**: Canton Coin MiCA — WHI-334 §3.7.4; Prividium CASP 适配 — WHI-337 (TCMAG 12 principles); Tempo mainnet 校正 — WHI-340 §1

### 3.2 SEC/CFTC 框架（美国）

美国监管框架聚焦于证券法合规（Howey Test）、商品交易合规、以及对 DeFi 协议的监管趋势。

| SEC/CFTC 维度 | Canton | Prividium | Tempo/Zones | Mantle |
|--------------|--------|-----------|-------------|--------|
| **证券合规（Howey Test）** | Daml 合约可编码证券合规逻辑（如持有期限制、合格投资者验证） | RBAC 可实施合格投资者访问控制（Check Role + Restrict Argument 组合） | TIP-403 whitelist 可限制仅 KYC 完成的合格投资者参与 | 无原生支持；需通过智能合约层实现 |
| **交易报告** | Observer 模式可将监管方纳入交易流水 | Private Block Explorer Auditor 角色提供只读审计访问 | Zone Sequencer 完全可见性 + L1 batch 公开记录 | 所有数据公开可查 |
| **CLARITY Act 相关性** | M1 研究数据不足 | WHI-338 分析指出 Prividium 对 CLARITY Act 关于"隐私保护 + 监管可访问"的平衡有直接参考价值 | M1 研究数据不足 | M1 研究数据不足 |

> **Source**: Prividium CLARITY Act — WHI-338 §4 (CLARITY Act 分析); Canton 证券合约模式 — WHI-334 §3.6.2 (Daml 模板模式)

### 3.3 MAS 框架（新加坡）

新加坡金融管理局 (MAS) 通过 Project Guardian 积极推动受监管 DeFi 和资产代币化。

| MAS 维度 | Canton | Prividium | Tempo/Zones | Mantle |
|----------|--------|-----------|-------------|--------|
| **Project Guardian 参与** | Canton 是 Project Guardian 的底层技术之一；450+ 参与方包含多家新加坡机构 | M1 研究数据不足 | M1 研究数据不足 | M1 研究数据不足 |
| **资产代币化支持** | Daml 原生支持复杂金融工具建模（Canton Coin, 证券合约） | Prividium 支持代币化资产的隐私交易（Cari Network 案例） | TIP-20 precompile 原生代币标准 + pathUSD 稳定币 | 标准 ERC-20/ERC-721 支持 |

> **Source**: Canton Project Guardian — WHI-334 §3.7 (Canton Network); WHI-342 §CBDC (Project Guardian 描述)

### 3.4 GDPR（数据保护）⭐

GDPR 的"被遗忘权"（Right to Erasure, Article 17）与区块链不可变性的矛盾是企业区块链面临的核心挑战之一。

| GDPR 维度 | Canton | Prividium | Tempo/Zones | Mantle |
|-----------|--------|-----------|-------------|--------|
| **数据存储模型** | 参与方本地 PostgreSQL 存储 | Validium 链下 DA（Operator 管理） | Zone 数据由 Sequencer 持有（链下）；L1 仅有 batch transition 摘要 | L1 blob/calldata 公开存储 |
| **被遗忘权实现** | ✅ **原生支持** — 各 Participant 可删除自身本地副本满足 GDPR 要求；但跨 Participant 留存策略仍需治理协调 | ✅ **可实现** — Validium 链下数据由 Operator 管理生命周期；WHI-338 评估 Validium 为"最 GDPR 友好的 ZK L2 架构" | ✅ **理论可行** — Zone 数据由 Sequencer 持有（链下），可删除；前提是避免将 PII 放入 L1-facing 事件 / 承诺 | ❌ **极度困难** — L2 交易数据作为 blob/calldata 提交到以太坊 L1，不可删除 |
| **数据最小化原则** | ✅ **原生支持** — Need-to-Know 模型确保每方仅持有与自己相关的数据 | ⚠️ **部分满足** — Operator 持有全部数据（与数据最小化矛盾），但可通过数据保留策略管理 | ⚠️ **部分满足** — Sequencer 持有全部 Zone 数据，但 Zone 间隔离 + L1 仅有摘要 | ❌ **不满足** — 所有数据公开可访问 |
| **跨境数据传输** | 各 Participant 可控制数据存储地理位置 | Operator 可选择数据中心位置 | Zone Sequencer 可部署在特定地理位置 | L1 数据全球分布 |

> **Source**: Canton GDPR — WHI-335 §5 企业特性表 (GDPR 原生支持通过可删除本地数据); Prividium GDPR — WHI-338 §4.4 ("Validium 是最 GDPR 友好的 ZK L2"); Tempo 数据模型 — WHI-340 §7, §11.4; Mantle L1 数据 — WHI-341 §8.1

> **注**：GDPR 友好并不等同于自动合规。金融记录留存义务（如 MiFID II、SEC books-and-records）通常仍要求保留部分交易元数据，现实方案往往是“删除或匿名化 PII + 保留审计必需元数据”。

### 3.5 Basel III/IV（银行资本充足率）

Basel III/IV 框架下，银行持有的链上资产需根据风险类型确定资本权重。

| Basel 维度 | Canton | Prividium | Tempo/Zones | Mantle |
|-----------|--------|-----------|-------------|--------|
| **资产类型分类** | Daml 可精确建模金融工具属性（底层资产类型、到期日、信用评级），便于风险权重计算 | 支持代币化资产的精确属性定义（Cari Network 银行联盟用例验证） | TIP-20 代币标准 + pathUSD 稳定币；TIP-403 策略注册表可标记资产合规状态 | 标准 ERC-20，无内置风险属性 |
| **结算终局性** | 2PC 协议提供确定性终局（所有 confirmers 同意即终局，或任一拒绝即回滚） | ZK 证明提交到 L1 后获得以太坊级终局性 | Zone 即时终局（head=safe=finalized）+ L1 batch 提交；完整 validity proof 仍待 prover 上线 | 默认 ZK 模式下约 1 小时 proof-backed 终局；~2s soft finality；若治理切回 Optimistic 回退则恢复 7 天挑战期 |
| **风险权重影响** | 确定性终局有利于较低风险权重 | 以太坊 L1 终局有利于较低风险权重 | 即时终局 + L1 锚定有利于风险管理，但 prover 未上线使其更接近受信 validium | 默认 ZK 模式显著优于传统 optimistic 路径，但治理可回退到 7 天模式会增加政策 / 操作风险 |

> **Source**: Canton 终局性 — WHI-335 §3.3 (Canton 共识 vs 传统 BFT); Prividium L1 终局 — WHI-338 §2.4 (信任假设); Tempo 即时终局 — WHI-340 §7; Mantle 终局性 — WHI-341 §4, §8.1

### 3.6 监管适配总评

| 监管框架 | 最适配方案 | 理由 |
|---------|-----------|------|
| **MiCA** | Canton | 团队主动适配（MiCA 白皮书）+ GSF 治理框架 + 大规模生产验证 |
| **SEC/CFTC** | Prividium | CLARITY Act 分析 + RBAC 合格投资者控制 + ZK 隐私-合规平衡 |
| **MAS** | Canton | Project Guardian 直接参与 + 资产代币化成熟支持 |
| **GDPR** | Canton | 唯一原生满足数据最小化原则和被遗忘权的方案 |
| **Basel III/IV** | Canton / Prividium | Canton 确定性终局 + Prividium L1 终局均有利于风险权重 |

---

## 4. 合规架构层次分析

### 4.1 四层合规架构框架

| 层次 | 实现方式 | 优势 | 劣势 | 代表方案 |
|------|---------|------|------|---------|
| **协议层原生** | 共识规则 / 预编译合约中嵌入合规检查 | 不可绕过；最高安全性 | 灵活性低；升级需硬分叉 | Tempo TIP-403 (precompile 级) |
| **智能合约层** | 通过合约逻辑实现合规检查 | 灵活可升级；标准 EVM 工具链 | 可被绕过（direct low-level calls） | 通用 ERC-20 合规扩展 (pause, blacklist) |
| **中间件层** | RPC / API 网关验证 | 部署简单；复用企业 SSO | 安全性最弱（可被绕过） | Prividium Proxy RPC |
| **链下集成** | 与外部合规系统对接 | 复用企业现有系统；灵活 | 延迟高；一致性挑战 | 传统 AML/KYC 接入 |

### 4.2 各项目合规层次定位

#### Canton: 应用层 + 协议层混合

```
┌─────────────────────────────────────────────┐
│  协议层: Daml 授权模型 (Signatory/Observer)  │  ← Daml 运行时强制执行
│  协议层: 2PC 确认协议 (Participant 验证)     │  ← 每方独立验证合规性
├─────────────────────────────────────────────┤
│  应用层: KYCCredential 模板模式              │  ← Daml 合约逻辑
│  应用层: Observer 角色定义                   │  ← 合约设计时配置
├─────────────────────────────────────────────┤
│  链下集成: 企业身份系统 (X.500 PKI)         │  ← Doorman 服务
└─────────────────────────────────────────────┘
```

**主要层次**: **协议层 + 应用层**。Canton 的合规模型独特之处在于：Daml 语言本身将授权（Signatory/Observer/Controller）嵌入了语言语义——这不是可选的合约逻辑，而是运行时强制执行的协议规则。同时，具体的合规业务逻辑（如 KYC 验证）在应用层通过 Daml 模板实现。

> **Source**: WHI-334 §3.6.3 (Daml 授权模型); WHI-336 (AuthenticationValidator, ModelConformanceChecker 代码实现)

#### Prividium: 中间件层 + L1 边界防御

```
┌─────────────────────────────────────────────┐
│  L1 边界: PrividiumTransactionFilterer       │  ← L1 合约层白名单
├─────────────────────────────────────────────┤
│  合约层: RBAC 六种权限类型 (默认 Forbidden)  │  ← 合约函数级权限
├─────────────────────────────────────────────┤
│  中间件层: Proxy RPC 三步验证               │  ← JWT → 钱包 → 权限
│  (这是合规的主要执行层)                      │
├─────────────────────────────────────────────┤
│  身份层: SSO 集成 (Okta OIDC / SIWE)       │  ← 企业 SSO 联邦
└─────────────────────────────────────────────┘
```

**主要层次**: **中间件层** (Proxy RPC)，辅以 L1 边界防御。Prividium 的核心合规逻辑在 Proxy RPC 执行——JWT 验证、钱包地址匹配、合约函数权限检查。L1 TransactionFilterer 是防止绕过 Proxy RPC 的安全网（拦截 L1→L2 强制交易）。

**⚠️ 安全考量**: 中间件层合规的固有弱点是"可绕过性"——如果攻击者能直接访问 Sequencer RPC（绕过 Proxy），则所有合规检查失效。Prividium 通过 L4 层的 PrividiumTransactionFilterer 和网络架构（Sequencer RPC 不对外暴露）来缓解此风险。但 Prividium 文档也明确指出 Multicall 被主动阻止，因为它可以绕过单函数权限检查——这说明中间件层合规需要持续应对绕过场景。

> **Source**: WHI-338 §3 (四层纵深防御); WHI-337 §3.4 (RBAC); WHI-338 §3.4 (L1 TransactionFilterer)

#### Tempo/Zones: 协议层原生

```
┌─────────────────────────────────────────────┐
│  协议层: TIP-403 Registry (precompile)       │  ← 0x403C... 地址
│  协议层: TIP-20 precompile transferAuthorized│  ← 每次 transfer 强制检查
│  协议层: Direct-call-only enforcement        │  ← delegatecall 返回错误
├─────────────────────────────────────────────┤
│  Zone 层: SharedPolicyCache (L1→L2 镜像)    │  ← 策略自动同步
│  Zone 层: ZoneTip403ProxyRegistry            │  ← 只读策略代理
├─────────────────────────────────────────────┤
│  RPC 层: Zone Private RPC (X-Auth-Token)    │  ← 认证访问
│  RPC 层: 隐私保护 (sanitized blocks,        │
│          private balanceOf, 100ms min delay)  │
└─────────────────────────────────────────────┘
```

**主要层次**: **协议层原生** (precompile)。TIP-403 作为预编译合约（地址 `0x403C...`），在共识规则中嵌入合规检查。关键特征：
- 每次 TIP-20 transfer 都强制调用 `transferAuthorized()`
- 所有 precompile 强制 direct-call-only（delegatecall 被阻止）
- 策略通过 SharedPolicyCache 自动从 L1 镜像到 Zones
- T2 hardfork 引入 compound transfer policies (TIP-1015) 分离 sender/recipient 规则

这是三个项目中合规强制执行力度最高的方案——在 EVM 执行层面，合规检查不可绕过。需要补充的是：**L1 上的 TIP-403 与其策略模型已经生产可用，但 Zone 侧“可证明镜像”仍受 prover 未上线限制**；因此当前 Zone 更接近“协议级策略 + 受信 sequencer 执行”，而不是完全 proof-backed 的私密合规层。

> **Source**: WHI-340 §2.4 (precompile 系统), §3.5 (TIP-403 Mirroring), §7.1 (TIP-403 Registry); WHI-339 §5.2 (TIP-403 策略注册表)

#### Mantle: 无原生合规层

```
┌─────────────────────────────────────────────┐
│  (空) — 无协议层合规                         │
├─────────────────────────────────────────────┤
│  (空) — 无合约层合规                         │
├─────────────────────────────────────────────┤
│  (空) — 无中间件层合规                       │
├─────────────────────────────────────────────┤
│  潜在切入点 (未实现):                        │
│  - Sequencer 策略引擎 (WHI-341 §10 / §8.1)   │
│  - Transaction Pool 过滤 (WHI-341 §10)       │
│  - Identity Registry Predeploy (WHI-341 §10) │
│  - Meta-tx 基础设施 (已禁用但代码完整)       │
│  - Gas Oracle 扩展模式                       │
└─────────────────────────────────────────────┘
```

**主要层次**: **无**。但 baseline 分析识别了 10 个自然切入点（§7.1-§7.10），难度从"Low (config change)"到"Very High (architectural redesign)"不等。

> **Source**: WHI-341 §8.1, §10

### 4.3 合规层次对比矩阵

| 项目 | 协议层 | 合约层 | 中间件层 | 链下集成 | 主要层次 |
|------|--------|--------|---------|---------|---------|
| **Canton** | ✅ Daml 授权 + 2PC 验证 | ✅ Daml 模板 (KYC 等) | — | ✅ X.500 PKI | 协议 + 应用 |
| **Prividium** | ✅ TransactionFilterer (L1) | ✅ RBAC 权限 | ✅✅ Proxy RPC (核心) | ✅ Okta SSO | **中间件** |
| **Tempo/Zones** | ✅✅ TIP-403 precompile (核心) | — | ✅ Private RPC | — | **协议层** |
| **Mantle** | — | — | — | — | **无** |

### 4.4 层次选择的工程权衡

| 权衡维度 | 协议层 (Tempo 模式) | 中间件层 (Prividium 模式) | 应用层 (Canton 模式) |
|---------|--------------------|-----------------------|-------------------|
| **不可绕过性** | ★★★★★ | ★★☆☆☆ | ★★★★☆ |
| **升级灵活性** | ★★☆☆☆ (需硬分叉) | ★★★★★ (热更新) | ★★★☆☆ (需重部署) |
| **开发复杂度** | ★★★★★ (修改共识) | ★★☆☆☆ (网关开发) | ★★★☆☆ (合约开发) |
| **EVM 兼容性影响** | ★★★☆☆ (预编译改变 EVM 行为) | ★★★★★ (无影响) | ★★★★★ (无影响) |
| **合规覆盖面** | 完整 (所有交易) | 部分 (仅通过网关的交易) | 部分 (仅使用合规合约的交易) |
| **部署速度** | 慢 (需节点升级) | 快 (独立服务部署) | 中等 (合约部署 + 集成) |

---

## 5. 对 Mantle 的合规方案推荐

### 5.1 Mantle 合规层次选择分析

**核心问题**: 作为 OP Stack 链，Mantle 应该在哪个层次建设合规框架？

#### 选项分析

| 层次 | 适合 Mantle 程度 | 理由 |
|------|----------------|------|
| **协议层 (Tempo 模式)** | ⚠️ 高价值但高成本 | 需修改 op-geth 核心代码（添加预编译或修改 state transition）；影响 OP Stack 兼容性；升级需与 Optimism 上游协调 |
| **智能合约层** | ✅ 中等价值，中等成本 | 利用 Mantle predeploy 模式（已有先例：L1Block, GasPriceOracle, OperatorFeeVault）部署 Identity Registry 和 Compliance Registry；灵活可升级但可被绕过 |
| **中间件层 (Prividium 模式)** | ✅ 高价值，低成本 | Sequencer 层策略引擎 + Transaction Pool 过滤；最快速的 MVP 路径；baseline 已识别为 §7.1/§7.4 自然切入点 |
| **链下集成** | ✅ 辅助价值 | 复用企业现有 KYC/AML 系统；Gas Oracle 扩展模式提供参考（§7.6） |

**推荐**: **分阶段混合策略——中间件层 MVP → 合约层增强 → 可选协议层升级**

> **Source**: WHI-341 §8.1, §10

### 5.2 TIP-403 预编译模式 vs Proxy RPC 模式

| 对比维度 | Tempo TIP-403 预编译 | Prividium Proxy RPC | **对 Mantle 的适用性** |
|---------|--------------------|--------------------|---------------------|
| **实现难度** | 需修改 EVM 执行层；添加自定义预编译 | 需开发独立的 RPC 代理服务 | Proxy RPC 在 Mantle 上更容易实现（不改核心协议） |
| **不可绕过性** | ★★★★★ (预编译层强制) | ★★☆☆☆ (L1→L2 force tx 可绕过) | 预编译模式安全性更高，但 Mantle 的 L1→L2 bridge 也需要保护 |
| **OP Stack 兼容** | 需要 Mantle 硬分叉（已有先例：6 个 Mantle 硬分叉） | 独立于 OP Stack，不影响兼容性 | Proxy RPC 不影响上游 merge |
| **升级灵活性** | 需硬分叉升级（T2 引入 compound policies 的先例） | 热更新策略配置 | Proxy RPC 更适合快速迭代 |
| **对标方案** | 类似 Avalanche compliance precompiles | 类似 Besu Privacy Manager 模式 | — |

**推荐**: MVP 阶段采用 **Proxy RPC 模式** (Prividium 风格)，配合 **PrividiumTransactionFilterer 思路** 在 L1 bridge 合约中添加白名单（保护 L1→L2 force transaction 路径）。长期演进可评估 TIP-403 预编译模式的 ROI。

### 5.3 Sequencer 合规角色转化方案

Mantle 的中心化 Sequencer 已拥有完全交易可见性——这与 Tempo Zone Sequencer 和 Prividium Operator 的条件完全相同。

#### 转化路径

```
当前状态 (Mantle Baseline):
┌─────────────────────────────────────────────────────┐
│  用户 → Sequencer (排序) → op-geth (执行) → L1      │
│         ↑ 可见所有交易                               │
│         ↑ 但不做任何合规检查                          │
└─────────────────────────────────────────────────────┘

Phase 1: Sequencer 策略引擎 (MVP)
┌─────────────────────────────────────────────────────┐
│  用户 → [Policy Engine] → Sequencer → op-geth → L1  │
│         ↑ 检查发送方白名单/黑名单                     │
│         ↑ 检查交易金额阈值                            │
│         ↑ 记录审计日志                                │
└─────────────────────────────────────────────────────┘
  实现点: op-node/rollup/sequencing/sequencer.go
          op-geth/core/txpool/ (transaction pool 过滤)

Phase 2: Identity Registry 集成
┌─────────────────────────────────────────────────────┐
│  用户 → Policy Engine → Sequencer → op-geth → L1    │
│         ↑ 查询链上 Identity Registry                  │
│         ↑ (predeploy 合约, 类似 GasPriceOracle 模式)  │
│         ↑ 验证 KYC 状态 + 角色权限                    │
└─────────────────────────────────────────────────────┘
  实现点: Identity Registry predeploy（见 WHI-341 §10）
          升级 deposit tx 模式 (arsia_upgrade_transactions.go)

Phase 3: 结构化审计导出
┌─────────────────────────────────────────────────────┐
│  Sequencer → Policy Engine → [Audit Exporter]       │
│                                ↑ 实时事件流           │
│                                ↑ 结构化审计报告       │
│                                ↑ 合规系统集成 API     │
└─────────────────────────────────────────────────────┘
  实现点: 新服务，复用 op-service 基础设施（见 WHI-341 §10）
```

> **Source**: WHI-341 §10

### 5.4 最小可行合规方案 (MVP Compliance)

#### MVP 定义

能够让 Mantle（或其企业衍生链）满足最基本企业合规准入要求的最小功能集合。

#### MVP 组件

| 组件 | 描述 | 实现方式 | 难度 | 参考方案 |
|------|------|---------|------|---------|
| **1. 地址白名单** | 仅允许 KYC 完成的地址提交交易 | Sequencer 层 TransactionPolicy 接口 + tx pool 过滤 | Low-Medium | Tempo TIP-403 whitelist 概念 + Besu Account Ingress |
| **2. 基础审计日志** | 记录所有交易的发送方、接收方、金额、时间戳到结构化存储 | Sequencer 侧事件流 + 数据库存储 | Low | Tempo Zone Sequencer 数据流模式 |
| **3. 合规 RPC 网关** | 认证访问（JWT/API Key）+ 基础访问控制 | 独立 RPC Proxy 服务 | Low-Medium | Prividium Proxy RPC 简化版 |
| **4. L1 Bridge 白名单** | 防止未授权地址通过 L1→L2 强制交易绕过合规 | L1 bridge 合约添加 sender 白名单（类似 PrividiumTransactionFilterer） | Medium | Prividium TransactionFilterer |
| **5. 管理面板** | 白名单管理、审计日志查询、基础报告 | Web 应用 + 管理 API | Low-Medium | Prividium Admin Dashboard 简化版 |

#### MVP 架构图

```
                          ┌─────────────────┐
                          │  Admin Dashboard │
                          │  (白名单管理)    │
                          └────────┬────────┘
                                   │ API
                                   ▼
┌─────────┐    JWT Auth    ┌──────────────┐    ┌─────────────┐
│  用户    │──────────────►│ Compliance   │───►│ Sequencer   │
│  (KYC'd)│               │ RPC Proxy    │    │ + Policy    │
└─────────┘               │ (组件 3)      │    │ Engine      │
                          └──────────────┘    │ (组件 1+2)  │
                                              └──────┬──────┘
                                                     │
                          ┌──────────────┐           │
                          │ L1 Bridge    │           ▼
                          │ Whitelist    │      ┌──────────┐
                          │ (组件 4)      │      │ op-geth  │
                          └──────────────┘      └──────────┘
                                                     │
                          ┌──────────────┐           │
                          │ Audit Log DB │◄──────────┘
                          │ (组件 2)      │    审计事件
                          └──────────────┘
```

#### MVP 实现优先级

| 优先级 | 组件 | 理由 |
|--------|------|------|
| P0 | 地址白名单 (Sequencer 层) | 最基本的企业准入控制 |
| P0 | L1 Bridge 白名单 | 防止白名单被绕过的安全关键组件 |
| P1 | 合规 RPC 网关 | 提供企业级认证入口 |
| P1 | 基础审计日志 | 监管审计的基本要求 |
| P2 | 管理面板 | 运维便利性，可先用 CLI 替代 |

#### MVP 实现估计

| 维度 | 估计 |
|------|------|
| **核心开发量** | ~2-3 人月（Sequencer 策略引擎 + RPC Proxy + L1 合约修改） |
| **OP Stack 改动** | 最小化——主要在 Sequencer 层和独立服务；L1 合约改动独立于 OP Stack |
| **上游兼容性风险** | 低——Sequencer 层策略引擎和 RPC Proxy 不影响核心 derivation pipeline |
| **参考代码** | Mantle meta-tx 基础设施（已禁用但代码完整）提供 state-transition 级策略的参考 |

> **Source**: WHI-341 §8.1, §10; WHI-342 §5

### 5.5 长期演进路线

```
Timeline ──────────────────────────────────────────────────────────────►

Phase 1 (MVP, 0-3个月):
├── Sequencer 地址白名单/黑名单
├── L1 Bridge TransactionFilterer
├── 基础合规 RPC Proxy (JWT auth)
├── 审计事件日志
└── 管理 CLI/API

Phase 2 (增强, 3-6个月):
├── Identity Registry Predeploy (链上身份注册表)
├── RBAC 权限框架 (参考 Prividium 六种权限模型)
├── 选择性披露 API (参考 Prividium Merkle 证明导出)
├── 管理 Web Dashboard
└── 企业 SSO 集成 (OIDC/SAML)

Phase 3 (高级, 6-12个月):
├── 评估 Compliance Precompile (参考 TIP-403, Avalanche compliance precompiles)
├── Private Block Explorer (参考 Prividium 角色化视图)
├── 交叉链合规 (跨 L2 合规状态共享)
└── ZK 合规证明 (参考 Prividium ZK 制裁筛查)

Phase 4 (创新, 12+个月):
├── 隐私子链 (Zone-like L3, 参考 Tempo Zones 架构)
├── 链上 KYC 凭证 (参考 Coinbase Verifications 模式)
├── 合规即服务 (Compliance-as-a-Service 产品化)
└── 跨链合规互操作 (参考 Canton Global Synchronizer 跨域模式)
```

> **Source**: 行业趋势参考 — WHI-342 §3 ("compliance is becoming a first-class architectural concern"), §5 (Besu permissioning, Coinbase Verifications, Avalanche compliance precompiles)

---

## 附录 A: 术语对照表

| 术语 | 英文 | 说明 |
|------|------|------|
| 合规能力矩阵 | Compliance Capability Matrix | 系统化比较各项目合规功能的表格 |
| 审计追踪 | Audit Trail | 不可篡改的操作记录 |
| 选择性披露 | Selective Disclosure | 向特定方（如监管机构）有条件地暴露数据 |
| 预编译合约 | Precompile Contract | 在 EVM 中以固定地址存在的原生实现合约 |
| 中间件层 | Middleware Layer | RPC/API 网关等位于客户端和执行层之间的组件 |
| 被遗忘权 | Right to Erasure/Right to be Forgotten | GDPR Article 17, 数据主体要求删除个人数据的权利 |
| 数据最小化 | Data Minimization | GDPR 原则，仅收集和存储必要的个人数据 |
| 策略注册表 | Policy Registry | 存储和管理合规策略（白名单/黑名单）的链上组件 |

## 附录 B: 源文件引用索引

| 引用标识 | 文件路径 | 关键章节 |
|---------|---------|---------|
| WHI-334 | `m1-research/canton/WHI-334-canton-docs-research.md` | §3.1 Participants, §3.6.3 授权模型, §3.7.4 Canton Coin |
| WHI-335 | `m1-research/canton/WHI-335-canton-architecture-analysis.md` | §2.4 Need-to-Know vs ZK, §3 共识, §5 企业特性表 |
| WHI-336 | `m1-research/canton/WHI-336-canton-codebase-analysis.md` | AuthenticationValidator, ModelConformanceChecker, TopologyManager |
| WHI-337 | `m1-research/prividium/WHI-337-prividium-official-docs-research.md` | §3.4 RBAC, §3.5 KYC, §3.6 选择性披露 |
| WHI-338 | `m1-research/prividium/WHI-338-prividium-architecture-deep-analysis.md` | §2.5 Canton 对比, §3 四层防御, §4.1 ZK 制裁筛查, §4.4 GDPR |
| WHI-339 | `m1-research/tempo-zones/WHI-339-tempo-docs-research.md` | §5.1 企业特性矩阵, §5.2 TIP-403 |
| WHI-340 | `m1-research/tempo-zones/WHI-340-tempo-code-analysis.md` | §2.4 Precompiles, §3.5 TIP-403 Mirroring, §7 企业特性 |
| WHI-341 | `m1-research/mantle/WHI-341-mantle-v2-architecture-baseline.md` | §4 状态验证与终局性, §8 企业适配, §10 天然插入点 |
| WHI-342 | `m1-research/industry/WHI-342-industry-survey.md` | §3 行业趋势, §5 Mantle 相关性评估 |
