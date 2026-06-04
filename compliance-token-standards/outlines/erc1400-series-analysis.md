---
topic: "ERC-1400 系列标准分析"
project_slug: "compliance-token-standards"
topic_slug: "erc1400-series-analysis"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "compliance-token-standards/outlines/erc1400-series-analysis.md"
  draft: "compliance-token-standards/research-sections/erc1400-series-analysis/drafts/round-{n}.md"
  final: "compliance-token-standards/research-sections/erc1400-series-analysis/final.md"
  index: "compliance-token-standards/research-sections/_index.md"

scope: "分析 ERC-1400 系列标准的技术架构，重点关注其与 ERC-3643 的差异化设计。ERC-1400 是 Polymath 提出的模块化安全 token 框架，虽然未被 EIP 正式接受，但在 STO 领域有一定历史影响力。调研范围：(1) 模块化架构 — ERC-1410 partition/tranche 机制、ERC-1594 transfer restrictions with reason codes、ERC-1643 文档管理、ERC-1644 强制转移；(2) 合规机制 — off-chain key validation + on-chain rules 混合模式；(3) 与 ERC-3643 的对比 — 身份模型、复杂度、采用情况、ERC-20 fallback 安全风险；(4) 历史地位与现状。优先级 Low，篇幅可控，重点在差异和演化关系。"
audience: "区块链协议工程师、RWA/合规产品负责人，以及 Research Review Agent。读者已阅读 compliance-token-landscape final.md（WHI-177），熟悉 8 类合规能力 Taxonomy 和 7 维度评估框架。本文聚焦 ERC-1400 的差异化设计和历史定位，不重复 landscape 已覆盖的通用背景。"
expected_output: "compliance-token-standards/outlines/erc1400-series-analysis.md，包含：ERC-1400 模块化子标准架构分析、合规机制与 transfer 流程、ERC-20 fallback 安全风险分析、基于统一 Taxonomy 的 ERC-1400 vs ERC-3643 差异对比、历史地位与演化路径"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-04T08:30:00Z"

multica_issue_id: "cf57ea5d-c512-47fc-8c8d-99b1f15a86e5"
report_issue_id: "4c88c789-585a-4c50-965e-628d50cb8bde"
branch_name: "research/compliance-token-standards/erc1400-series-analysis"
base_commit: "008e66bff9bfb866807c2a1f7f7131be9cba232b"
language: "中文"
research_depth: "focused"

dependencies:
  - slug: "compliance-token-landscape"
    issue_id: "f6a0c156-96f4-49df-b7c3-70109c308c5f"
    relationship: "使用其 8 类合规能力 Taxonomy 和 7 维度评估框架作为分析基准"
---

# Research Outline: ERC-1400 系列标准分析

## Positioning

本研究是 compliance-token-standards 项目的聚焦分析篇，依赖 WHI-177（compliance-token-landscape）建立的评估框架。WHI-177 final.md 已覆盖 ERC-1400 的架构概述（Section 4）和 Taxonomy 评估（Section 9-10），本文在其基础上深入分析 ERC-1400 的差异化设计逻辑、安全风险和历史演化，不重复已有内容。

**与 landscape 的分工**：landscape 从五大标准横向对比的角度给出 ERC-1400 的定位；本文从 ERC-1400 自身视角纵深分析其设计选择、trade-off 和失败教训，为理解合规 Token 标准的演化路径提供历史纵深。

## Research Questions

1. ERC-1400 的四个子标准（ERC-1410/1594/1643/1644）如何构成一个模块化安全 token 框架？各子标准的接口设计和协作关系是什么？
2. ERC-1400 的 off-chain key validation + on-chain rules 混合合规模式与 ERC-3643 的全链上 identity verification 模式有何本质差异？这种差异如何影响安全性、互操作性和审计能力？
3. ERC-1400 的 ERC-20 backward compatibility 引入了哪些安全风险？transferByPartition 有合规检查但 transfer/transferFrom 可能绕过的问题有多严重？
4. 在 WHI-177 的 8 类合规能力 Taxonomy 下，ERC-1400 的强项（partition/文档管理/controller 强制转移）和弱项（identity/sanctions/payment）如何定位？
5. ERC-1400 从提出（2018）到事实衰落的历史轨迹如何？Polymath 转向 Polymesh、ConsenSys UniversalToken 停止维护、ERC-7518 (DyCIST) 继承 partition 思想——这条演化线索说明了什么？

## Items

### item-1: ERC-1400 模块化子标准架构

分析 ERC-1400 作为 umbrella standard 的四个子标准的技术设计。

**ERC-1410 (Partially Fungible Token)**：partition/tranche 架构的核心创新。嵌套 mapping `(address => bytes32 => balance)` 实现同一地址下不同法律属性的代币分组（如 LOCKED/UNLOCKED/REG_D_RESTRICTED/VESTING）。partition key 使用 `bytes32`（通常为 `keccak256("PARTITION_NAME")`）。双入口：`transferByPartition(partition, to, amount, data)` 携带 partition 上下文和 off-chain 数据；`transfer(to, amount)` 作为 ERC-20 fallback 操作默认 partition。Gas 考量：需维护辅助数组 `userPartitions` 用于枚举，每个新 partition 交互产生 SSTORE + array push 成本；余额计算需遍历所有 partition。

**ERC-1594 (Core Security Token)**：发行与转让控制的核心。`canTransfer(to, amount, data)` 返回 ESC reason code（bytes1 状态码 + bytes32 application-specific code）；`issue(to, amount, data)` 和 `redeem(amount, data)` 控制发行/赎回生命周期；`_data` 参数设计为注入 off-chain 合规证明（如签名的 KYC certificate），但格式非标准化。`isIssuable()` 标志位控制发行是否终止（不可逆）。

**ERC-1643 (Document Management)**：链上文档关联。`setDocument(bytes32 name, string uri, bytes32 documentHash)` 绑定法律文档（招股说明书、合规证书、投资备忘录等）到 token 合约；`getDocument(name)` 返回 URI + hash + timestamp；`getAllDocuments()` 列举所有文档名。hash 允许链下验证文档完整性。这是 ERC-1400 相对于 ERC-3643 的独特能力——ERC-3643 无原生文档管理。

**ERC-1644 (Controller Token Operation)**：强制转移能力。`controllerTransfer(from, to, amount, data, operatorData)` 允许 controller 地址绕过所有 transfer 限制强制转移代币；`controllerRedeem(holder, amount, data, operatorData)` 强制赎回/销毁。`isControllable()` 标志位决定是否启用 controller 功能。controller 是"God Mode"——如果 controller 地址被攻破，可以 drain 任何持有者的余额。

**子标准间的协作**：ERC-1410 提供 partition 数据结构 -> ERC-1594 在此基础上添加 transfer 合规检查 -> ERC-1643 为 token 合约附加法律文档 -> ERC-1644 提供监管执行的最终手段。开发者可选择性采用子标准。

- **Priority**: high
- **Dependencies**: none

### item-2: 合规机制与 Transfer 流程

深入分析 ERC-1400 的合规执行模式及其与 ERC-3643 的根本差异。

**Off-chain key validation 模式**：ERC-1594 的 `_data` 参数是 ERC-1400 合规模式的关键。transfer 发起方需从 off-chain authority（如发行方、合规服务商）获取签名的合规证明，作为 `_data` 注入交易。链上合约验证签名有效性后放行。这种"off-chain 生成证明 + on-chain 验证签名"模式意味着：(a) 合规决策逻辑在链下，链上仅验证授权；(b) 每次 transfer 需与 off-chain 服务交互；(c) `_data` 格式由各实现自定义，无标准化规范。

**与 ERC-3643 全链上模式的对比**：ERC-3643 的合规决策完全在链上执行——Identity Registry 查询 ONCHAINID，验证 claims 来自 Trusted Issuers，Compliance Module 检查规则。两种模式的 trade-off：
- **透明性**：ERC-3643 全链上可审计；ERC-1400 off-chain 决策不透明
- **自主性**：ERC-3643 的 transfer 不依赖外部服务（claims 已预发布在链上）；ERC-1400 需实时请求 off-chain 签名
- **灵活性**：ERC-1400 的 off-chain 逻辑可任意复杂且易更新；ERC-3643 的 Compliance Module 升级需部署新合约
- **互操作性**：ERC-1400 `_data` 非标准化破坏不同实现间的互操作；ERC-3643 的标准接口更利于生态集成
- **活性依赖**：ERC-1400 如果 off-chain 签名服务宕机则无法 transfer；ERC-3643 无此风险

**Transfer 流程对比**（用于 diag-2）：
- ERC-1400: User -> off-chain authority 获取 `_data` -> `transferByPartition(partition, to, amount, data)` -> 链上验证 `_data` 签名 + reason code 检查 -> 执行或 revert（返回 ESC code）
- ERC-3643: User -> `transfer(to, amount)` -> Token Contract -> Identity Registry.isVerified() -> ONCHAINID claim 验证 -> Compliance Module.canTransfer() -> 执行或 revert

**Reason Code 机制**：ERC-1594 的 `canTransfer` 返回 ESC (Ethereum Status Code) + application-specific code，为 DApp 提供 transfer 失败原因。这是 ERC-1400 的有用设计——ERC-3643 的 Compliance Module 通常仅返回 bool，失败原因需解析 revert data。

- **Priority**: high
- **Dependencies**: item-1

### item-3: ERC-20 Fallback 安全风险分析

分析 ERC-1400 backward compatibility 设计引入的安全风险，这是 ERC-1400 标准的关键缺陷之一。

**核心问题：双入口不一致**：ERC-1400 为保持 ERC-20 backward compatibility，同时暴露两套 transfer 接口——`transferByPartition`（partition-aware，携带 `_data`）和继承的 `transfer/transferFrom`（ERC-20 标准接口）。如果实现仅在 `transferByPartition` 中执行合规检查而未 override `transfer/transferFrom`，攻击者可通过 ERC-20 接口绕过所有合规控制。

**攻击向量**：
1. **直接绕过**：用户调用 `transfer(to, amount)` 而非 `transferByPartition`，如果 `transfer` 未被 override 为执行合规检查，代币可在无 KYC/合规验证的情况下转移
2. **DeFi 路由绕过**：将 ERC-1400 token 存入不感知 partition 的 DEX/lending 协议，协议内部调用标准 ERC-20 `transferFrom`，合规检查被完全跳过
3. **Approved Controllable TransferFrom (ACT)**：通过已授权但合规状态已变更的 spender 路由 `transferFrom`，如果实现未在 `transferFrom` 中重新验证 spender 和 owner 的合规状态

**与 ERC-3643 的设计对比**：ERC-3643 从设计层面避免了此问题——`transfer` 和 `transferFrom` 都内置合规检查（Identity Registry + Compliance Module），不存在"未受保护的入口"。这是 ERC-3643 "identity-centric" 设计相对于 ERC-1400 "partition-centric" 设计的关键安全优势。

**缓解措施**：正确实现应使所有 transfer 入口都通过统一的 `_verifyTransfer` 内部 hook。ConsenSys UniversalToken 实现采用此模式，但由于 ERC-1400 标准本身未强制要求，各实现的安全质量参差不齐。

**Partition 隔离风险**：`transferByPartition` 中的验证逻辑不充分可能允许跨 partition 转移（如从 LOCKED 到 UNLOCKED），破坏 partition 设计的语义完整性。需在 `canTransferByPartition` 中严格校验源 partition 和目标 partition 的合法性。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: ERC-1400 vs ERC-3643 差异化分析（基于统一 Taxonomy）

使用 WHI-177 建立的 8 类合规能力 Taxonomy 和 7 维度评估框架，对 ERC-1400 进行系统性差异分析。本 item 不重复 landscape 已有的横向矩阵，而是从 ERC-1400 视角深入分析其设计选择的 trade-off。

**Taxonomy 维度深度对比**：

| 能力类别 | ERC-1400 设计选择 | 与 ERC-3643 的关键差异 |
|---------|-----------------|---------------------|
| Identity/KYC | off-chain `_data` 注入，无原生链上身份 | ERC-3643 ONCHAINID 提供 self-sovereign 链上身份；ERC-1400 依赖 operator 签发合规证明 |
| Transfer Policy | partition-level 控制 + reason codes | ERC-3643 使用可插拔 Compliance Module；ERC-1400 通过 partition 分组实现差异化控制 |
| Issuer Controls | ERC-1644 controller "God Mode" | 最强控制力但最高风险；ERC-3643 使用 Agent role 更细粒度 |
| Sanctions/Blacklist | 无专门机制，依赖 `_data` | ERC-3643 通过 Identity Registry revoke + Compliance Module blacklist |
| Recovery | controllerTransfer 强制转移 | 两者都支持，但 ERC-1400 controller 权限更集中 |
| Legal Document | ERC-1643 完整文档管理 | **ERC-1400 独有优势**——ERC-3643 无原生文档功能 |
| Payment Reconciliation | `_data` 可传支付引用（非标准） | 两者都弱；协议层方案（TIP-20）在此维度远超两者 |
| Auditability/Privacy | 链上审计 + off-chain 决策不透明 | ERC-3643 全链上更可审计；ERC-1400 off-chain 部分不可审计 |

**评估维度聚焦差异**：

| 维度 | ERC-1400 | 与 ERC-3643 对比判断 |
|------|----------|-------------------|
| 架构层级 | 应用层 Solidity | 相同层级，不同设计哲学 |
| 合规机制 | Off-chain cert + on-chain partition | ERC-3643 全链上更透明；ERC-1400 更灵活但更不透明 |
| 身份模型 | Operator-controlled | ERC-3643 self-sovereign 更先进 |
| DeFi 可组合性 | 受限（partition 非标准、`_data` 依赖） | 两者都有限，但 ERC-3643 的 ERC-20 兼容性更好 |
| 发行方控制力 | Controller God Mode（最强但最危险） | ERC-3643 Agent role 更平衡 |
| Gas 开销 | 中-高（partition 存储 + 遍历） | ERC-3643 高（多合约调用）；两者都高于 ERC-20 |
| 规范成熟度 | Draft 2018（从未 finalize） | ERC-3643 Final 2023；差距不可逆 |

**核心设计哲学差异总结**：
- ERC-1400 = **asset-centric**（partition 建模资产结构）+ **operator-centric**（off-chain authority 做合规决策）
- ERC-3643 = **identity-centric**（ONCHAINID 建模持有者身份）+ **on-chain-centric**（全链上合规验证）

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

### item-5: 历史地位、采用现状与演化路径

分析 ERC-1400 在合规 Token 标准演化中的历史定位，以及其设计思想的传承。

**时间线**：
- 2018: Polymath 联合 25 家公司提出 ERC-1400 umbrella standard（包括 Harbor、Securitize、ConsenSys）
- 2018-2019: STO 热潮期间获得广泛关注，成为"第一代"安全 token 标准的代表
- 2019: Polymath 开始转向 Polymesh 专用链，ERC-1400 Ethereum 实现逐步停止维护
- 2022: ConsenSys 发布 UniversalToken 作为较完整实现，但此后不再积极维护
- 2023: ERC-3643 达到 Final 状态，ERC-1400 仍为 Draft/Proposal
- 2023: ERC-7518 (DyCIST) 基于 ERC-1155 提出，继承 partition 思想 + 跨链互操作
- 2025-2026: Polymath 完成 Polymesh Association 收购，推出 Confidential Assets；Securitize 转向多链平台模式，已不依赖 ERC-1400

**采用现状判断**：
- Polymath 已完全转向 Polymesh 专用链，Polymesh Asset Standard 不再使用 ERC-1400
- Securitize 已成为 AUM $4B+ 的主导平台，使用自有协议（DS Protocol）+ ERC-20 + 多链策略，与 NYSE 合作
- ConsenSys UniversalToken 最后活跃更新约 2022 年
- ERC-1400 的 ERC-777 依赖已过时（OpenZeppelin v5.0.0 弃用 ERC-777）
- 据行业分析，ERC-1400 仅满足约 40% 的 31 项监管要求

**设计遗产与思想传承**：
- **Partition 思想**：ERC-7518 (DyCIST) 继承了 partition 概念，使用 ERC-1155 tokenId 作为 partition key，解决了 ERC-1410 的 Gas 效率问题
- **文档管理**：ERC-1643 的链上文档关联理念被认为有价值，但未被其他标准广泛采纳
- **Reason codes**：ERC-1594 的 ESC reason code 影响了后续标准对 transfer 失败反馈的思考
- **Controller 模型反面教训**：ERC-1644 的"God Mode"被视为过度中心化的设计，后续标准（ERC-3643 Agent role、B20 RBAC）采用更细粒度的权限模型
- **协议层转向**：Polymath 从 ERC-1400（应用层）到 Polymesh（协议层）的路径，与 Base B20、Tempo TIP-20 的设计选择形成呼应——复杂合规逻辑在通用 EVM 应用层的局限性推动了协议层方案的兴起

**核心判断**：ERC-1400 是合规 Token 标准的重要先驱，其 partition 架构和文档管理设计仍有参考价值，但作为标准本身已被 ERC-3643 在生态位上取代。其失败教训（过度复杂性、`_data` 非标准化、ERC-20 fallback 安全风险、标准碎片化）为后续标准设计提供了有价值的参考。Polymath 自身从应用层 ERC-1400 转向协议层 Polymesh 的选择，是合规 Token 标准演化方向的一个缩影。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| sub_standard_interface | 子标准名称、核心函数签名、参数类型、返回值、函数间调用关系 | item-1 |
| compliance_flow | 从 transfer 发起到执行/拒绝的完整流程，标注每步检查内容和 on-chain/off-chain 边界 | item-2 |
| security_risk | 安全风险名称、攻击向量、影响范围、缓解措施、是否为标准设计缺陷 vs 实现缺陷 | item-3 |
| taxonomy_capability | 在 WHI-177 8 类 Taxonomy 中的具体实现方式、强弱判断及与 ERC-3643 的差异理由 | item-4 |
| evaluation_dimension | 在 WHI-177 7 维度框架中的定位、与 ERC-3643 的对比判断及证据来源 | item-4 |
| adoption_evidence | 标准/实现的采用证据：项目名称、状态（active/deprecated/abandoned）、最后活跃时间、迁移方向 | item-5 |
| design_legacy | 设计理念的传承：原始设计 -> 继承标准 -> 改进点 | item-5 |
| evidence_classification | 每个关键 claim 的证据类型：primary-source / secondary / inferred；区分标准规范文本 vs 实现分析 vs 行业评论 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | ERC-1400 模块化子标准关系图：ERC-1410 Partition -> ERC-1594 Core -> ERC-1643 Document -> ERC-1644 Controller 的子标准层次、接口依赖和功能分工 | mermaid | item-1 |
| diag-2 | comparison | ERC-1400 vs ERC-3643 Transfer 流程对比图：左侧 ERC-1400 off-chain authority -> _data -> transferByPartition -> 链上验证 -> ESC code；右侧 ERC-3643 transfer -> Identity Registry -> ONCHAINID -> Compliance Module -> 执行。标注 on-chain/off-chain 边界 | mermaid | item-2 |
| diag-3 | security | ERC-20 Fallback 攻击路径图：正常路径（transferByPartition + compliance check）vs 绕过路径（ERC-20 transfer 无 compliance check）；标注攻击向量和影响 | mermaid | item-3 |
| diag-4 | timeline | ERC-1400 演化时间线：2018 提出 -> STO 热潮 -> Polymath 转 Polymesh -> ConsenSys UniversalToken -> ERC-3643 Final -> ERC-7518 继承；标注关键事件和标准状态变更 | mermaid | item-5 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_standard | ERC-1400/ERC-1410/ERC-1594/ERC-1643/ERC-1644 EIP 规范文本（ethereum/EIPs issues/discussions）、Polymath 官方文档和博客 | 3 |
| src-2 | implementation | ConsenSys UniversalToken GitHub 仓库代码分析、Polymath 原始实现（如仍可访问）、其他公开 ERC-1400 实现 | 2 |
| src-3 | comparison_analysis | Tokeny ERC-3643 vs ERC-1400 对比文档、Taurus CMTAT vs ERC-1400 vs ERC-3643 分析、NYALA 对比分析、Zealynx RWA 安全分析 | 3 |
| src-4 | security_analysis | ERC-1400 安全审计报告或安全分析（QuillAudits、Zealynx 等）、ERC-20 fallback 漏洞分析文章 | 2 |
| src-5 | ecosystem_status | Polymath/Polymesh 最新公告和路线图、Securitize 平台和标准策略、ConsenSys UniversalToken 仓库状态 | 2 |
| src-6 | successor_standard | ERC-7518 (DyCIST) EIP 规范、Zoniqx 文档、与 ERC-1400 partition 思想的传承关系分析 | 2 |
| src-7 | landscape_reference | WHI-177 compliance-token-landscape final.md（本项目已有产出，作为评估框架基准） | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create | all | 初始 outline 创建 | Orchestrator Dispatch (d1b85875) |
