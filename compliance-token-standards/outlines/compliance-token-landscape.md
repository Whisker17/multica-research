---
topic: "合规 Token 标准行业趋势与驱动力分析"
project_slug: "compliance-token-standards"
topic_slug: "compliance-token-landscape"
github_repo: "Whisker17/multica-research"
round: 3
status: candidate

artifact_paths:
  outline: "compliance-token-standards/outlines/compliance-token-landscape.md"
  draft: "compliance-token-standards/research-sections/compliance-token-landscape/drafts/round-{n}.md"
  final: "compliance-token-standards/research-sections/compliance-token-landscape/final.md"
  index: "compliance-token-standards/research-sections/_index.md"

scope: "监管环境变化（EU MiFID II/Prospectus/CSDR/DLT Pilot 对代币化证券的规制、MiCA 对非金融工具加密资产/ART/EMT/CASP 的规制、美国 DTC no-action letter（事实限定）、GENIUS Act 联邦稳定币框架、香港/新加坡 STO 政策）；市场数据（RWA 链上资产规模增长截至 2026 年、机构参与度如 DTCC/Franklin Templeton/BlackRock BUIDL）；技术趋势映射（smart-contract 层合规 ERC-3643/ERC-1400 -> 应用层自治 vs precompile/协议层合规 B20/TIP-20 -> 链原生合规；L2/新链倾向 precompile/协议层路线的原因：性能、Gas 成本、标准化）；合规能力 Taxonomy（8 类能力分类体系：Identity/KYC、Transfer Policy、Issuer Controls、Sanctions/Blacklist、Recovery、Legal Document/Metadata、Payment Reconciliation、Auditability/Privacy）；评估维度框架（7 个对比维度：架构层级、合规机制类型、身份模型、DeFi 可组合性、发行方控制力、Gas 开销、规范成熟度）"
audience: "区块链协议工程师、RWA/合规产品负责人、机构金融/BD 团队，以及 Research Review Agent。读者熟悉 EVM、L2 架构、代币标准和基础合规概念，但需要一份从设计范式角度对比各标准的技术分析框架。"
expected_output: "compliance-token-standards/outlines/compliance-token-landscape.md，包含：行业背景与监管驱动分析、合规能力 taxonomy 表（8 类）、评估维度框架（7 维度）、技术趋势两条路线对比框架、五大标准/方案的架构分析框架"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-04T06:30:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-04T07:15:00Z"

multica_issue_id: "f6a0c156-96f4-49df-b7c3-70109c308c5f"
branch_name: "research/compliance-token-standards/compliance-token-landscape"
base_commit: "fc071ee1ac405a8157588bd341ed91c79da2d435"
language: "中文"
research_depth: "standard"
---

# Research Outline: 合规 Token 标准行业趋势与驱动力分析

## Research Questions

1. 2024-2026 年全球监管环境如何驱动合规 Token 标准的采用？EU 代币化证券框架（MiFID II/Prospectus/CSDR/DLT Pilot）与 MiCA（非金融工具加密资产）分别起什么作用？美国 DTC no-action letter 的事实限定意义是什么？
2. RWA 链上资产规模增长到什么程度？机构参与者（DTCC、Franklin Templeton、BlackRock、Apex Group 等）采用了哪些标准？市场数据支撑什么趋势判断？
3. 应用层合规（ERC-3643/ERC-1400 的 smart-contract 层强制执行）与协议层合规（B20/TIP-20 的 precompile/链原生强制执行）在架构、性能、Gas 成本、可组合性和标准化程度上有何本质差异？
4. 五大标准/方案（ERC-3643、ERC-1400、B20、TIP-20、Circle Arc）各自的架构设计哲学是什么？它们如何在 Identity/KYC、Transfer Policy、Issuer Controls、Sanctions、Recovery、Document Management、Payment Reconciliation、Auditability/Privacy 八个合规能力维度上取舍？
5. 为什么新兴 L2/专用链（Base Beryl、Tempo、Circle Arc、Plume 等）倾向于选择 precompile/协议层路线而非复用现有 ERC 标准？性能、Gas 成本、标准化和监管确定性各自的权重如何？
6. 统一的合规能力 Taxonomy 和评估维度框架应如何构建，以便后续各标准的深度分析使用一致的分类体系？

## Regulatory Scope Guardrails

> **G1 — EU 监管框架分离（Review R1 修正）**：
> EU 代币化证券（STO）受 **MiFID II、Prospectus Regulation、CSDR 和 DLT Pilot Regime（EU 2022/858）**规制，而非 MiCA。MiCA（EU 2023/1114）Article 2 明确排除构成金融工具的加密资产，其适用范围为非金融工具加密资产、资产引用代币（ART）、电子货币代币（EMT）和加密资产服务提供商（CASP）。MiCA 可提供市场结构和披露相关的参考背景，但不得作为代币化证券 KYC/transfer 控制的监管依据。引用 EU 代币化证券法律时，必须以 DLT Pilot / MiFID II / Prospectus / CSDR 为主要来源。
>
> **G2 — DTC no-action letter 措辞限定（Review R1 修正）**：
> 所有涉及 SEC 与 ERC-3643 关系的表述必须准确反映：DTC 在其 no-action 请求中将 ERC-3643 作为合规感知协议的示例之一；SEC 工作人员（2025 年 12 月）仅就 DTC 的初步服务事实模式授予了有限的、事实限定的 no-action relief；该工作人员回复明确不建立更广泛的法律结论。要求的表述："DTC 在其 no-action 请求中引用了 ERC-3643；SEC 工作人员就该 DTC 事实模式授予了有限的、事实限定的 no-action relief"——不得使用"SEC 认可/批准/背书 ERC-3643"。要求引用来源：DTC no-action letter PDF (https://www.sec.gov/files/tm/no-action/dtc-nal-121125.pdf) + SEC Commissioner Peirce 关于 DLT Pilot 范围限制的声明。

## Items

### item-1: 监管环境变化与合规驱动力

梳理 2024-2026 年驱动合规 Token 标准兴起的关键监管事件和政策框架。

**EU 代币化证券框架**（G1 适用）：EU 代币化证券受 MiFID II（投资服务）、Prospectus Regulation（证券发行）、CSDR（证券结算）和 DLT Pilot Regime（EU 2022/858，允许 DLT 交易和结算基础设施的沙盒测试）规制。MiCA（EU 2023/1114）2024 年 12 月全面生效，适用于非金融工具加密资产（ART/EMT/CASP），提供市场结构和披露参考背景，但不适用于代币化证券的 transfer 控制或 KYC 要求。

**美国 SEC/DTC no-action letter**（G2 适用）：DTC 在其 no-action 请求（2025 年 12 月 11 日）中将 ERC-3643 引用为合规感知协议示例；SEC 工作人员就该 DTC 初步服务的事实模式授予了有限的、事实限定的三年期 no-action relief。SEC 主席 Paul Atkins 在 2025 年 7 月 "Project Crypto" 演讲中提及 ERC-3643。这些事件表明监管机构对链上合规机制的关注度提升，但不构成对 ERC-3643 的正式批准或背书。要求引用来源：DTC no-action letter PDF + SEC Commissioner Peirce 声明。

**美国 GENIUS Act**：2025 年 7 月通过的联邦稳定币框架，要求储备、审计、金融完整性。

**亚太**：香港稳定币条例和 STO 政策（SFC Type 1 + Type 7 牌照、ASPIRe 路线图）；新加坡 MAS Project Guardian 框架（使用 ERC-3643 基础设施的试点）。

分析这些监管事件如何从"可选合规"推向"标准化合规"，以及对 Token 标准选择的影响。

- **Priority**: high
- **Dependencies**: none

### item-2: RWA 市场数据与机构采用

建立合规 Token 标准的市场事实底座。覆盖：RWA 链上资产总规模（截至 2026 年已超 $25B-$33B，不含稳定币）；资产类别分布（国债代币化如 BlackRock BUIDL、私人信贷、房地产、商品等）；链分布（Ethereum、Polygon、Avalanche、专用链）；关键机构参与：DTCC 2025 年 3 月加入 ERC-3643 Association 并集成 ComposerX、Franklin Templeton 代币化基金、Apex Group 加入 ERC-3643 Association、Invesco 参与、Fasanara Capital 在 Polygon 上使用 ERC-3643 的货币市场基金、ABN AMRO 的代币化债券/绿色债务工具。标注数据来源、访问日期和口径差异。判断市场处于 early adoption、institutional pilot、scaling 或 mainstream adoption 哪一阶段。

- **Priority**: high
- **Dependencies**: item-1

### item-3: ERC-3643 (T-REX Protocol) 架构与合规机制

深度分析 ERC-3643 作为唯一正式获批的 Ethereum 合规代币标准的架构设计。覆盖：

**架构组件**：Token Contract（ERC-20 扩展）、ONCHAINID（基于 ERC-734/ERC-735 的自主身份合约，存储 hash/引用而非 PII）、Identity Registry（wallet -> ONCHAINID 映射，isVerified() 检查）、Trusted Issuers Registry（授权 KYC 提供者地址）、Claim Topics Registry（可信 claim 类型）、Compliance Module（可插拔合规规则，可独立升级）。

**Transfer 流程**：发起 -> Validator 检查 -> Identity Registry 验证 sender/receiver ONCHAINID -> Trusted Issuers 验证 claims -> Compliance Module 检查规则（投资者上限、司法管辖限制、锁定期、认证状态等）-> 执行或拒绝。

**Gas 成本特征**：每次 transfer 需执行 identity + compliance 检查，比 ERC-20 有额外 Gas 开销；模块化设计和批量操作可部分缓解；低频交易场景开销可忽略，高频交易场景有复合成本。

**DeFi 可组合性挑战**：基于 ERC-20 可与 DEX/借贷协议集成，但合规检查失败会导致交易静默失败（用户无明确错误提示）；结构性流动性受限（持有者池受限）；与 permissionless DeFi 的根本张力。

**标准成熟度与市场地位**（G2 适用）：唯一正式获批 ERC 标准（2023 年）；超 $32B 资产代币化；180+ 司法管辖区部署；ERC-3643 Association 治理（DTCC、Apex Group、Invesco 为成员）；ISO 标准化推进中。DTC 在其 no-action 请求中引用 ERC-3643 为合规感知协议示例（SEC 工作人员就该事实模式授予有限 no-action relief，不构成对 ERC-3643 的正式批准）。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: ERC-1400 (Security Token Standard) 架构与合规机制

深度分析 ERC-1400 作为早期安全代币标准框架的架构设计和当前状态。覆盖：

**模块化子标准**：ERC-1410（Partially Fungible Token -- partition/tranche 架构，单地址下不同法律属性的代币分组，如 LOCKED/UNLOCKED/REG_D_RESTRICTED）；ERC-1594（Core Security Token -- 发行验证、transfer 限制与原因码、off-chain 数据注入）；ERC-1643（Document Management -- 链上文档关联，bytes32 唯一名 + URI + hash + 时间戳）；ERC-1644（Controller Token Operation -- 强制转移/合规操作/安全修复的控制者权限）。

**Transfer 限制机制**：operator model，每次交易需 off-chain 生成的特定密钥验证；ERC-1594 要求检查发行方合规状态、接收方合规状态、资产类别和上下文；与 ERC-3643 的 on-chain identity verification 形成对比。

**Partition/Tranche 架构**：嵌套 mapping（address -> bytes32 -> balance），每个 partition 有独立权限控制；支持复杂资本结构（vesting、锁定期、不同 share class、司法管辖限制）建模；Gas 代价：需维护辅助数组 userPartitions，每个新 partition 交互产生 SSTORE + array push 成本。

**标准成熟度**：2018 年由 Polymath 提出，仍为 proposal 状态（从未达到 ERC final stage）；Polymath 实现自 2019 年起似乎不再公开维护；ConsenSys Universal Token 2022 年发布为较完整实现；子标准独立提出导致集成复杂度高；_data 参数非标准化破坏互操作性；仅满足约 40% 的 31 项监管要求。

**后续演进**：ERC-7518 (DyCIST) 基于 ERC-1155 扩展 partition + 跨链互操作 + 动态合规。

- **Priority**: high
- **Dependencies**: item-3

### item-5: B20 (Base Beryl Precompile) 协议层合规架构

深度分析 B20 作为 Base 链 Beryl 硬分叉引入的 precompile 级代币标准的架构设计。**B20 证据基于代码分析（base/base@8e8767281d），公开 Beryl 规范尚未发布，结论归类为 code-inferred pending 最终硬分叉规范。**

**Precompile 架构**（代码确认）：B20 token 通过 B20Factory precompile 创建，使用特殊地址格式（0xb2 前缀字节 + 9 零字节 + variant discriminant 字节 + 9 字节 hash tail）；地址由 creator + salt 确定性派生（keccak256）。位于 `crates/common/precompiles/src/b20/` 模块。

**Token 变体**（代码确认，base/base@8e8767281d `crates/common/precompiles/src/b20_factory/variant.rs`）：两种变体通过 B20Variant 枚举定义——Asset (=0, 18 decimals) 和 Stablecoin (=1, 6 decimals)；变体编码在地址字节 [10]，discriminant 值直接匹配 ABI 枚举序号。注：本地分支 a052beb 出现第三变体 Security (=2)，属 b20_security/ 模块扩展，尚未合入 pinned resource commit，归类为未来演进观察。

**Policy 系统**（代码确认）：PolicyRegistry 全局单例 precompile，B20 token 通过 4 个内置 policy slot 控制 transfer 资格——TransferSender、TransferReceiver、TransferExecutor、MintReceiver；policy 可跨 token 共享，由 PolicyHandle 封装访问。与 TIP-20 的 TIP-403 PolicyRegistry 设计理念一致。

**RBAC**（代码确认）：7 个内置角色——DefaultAdmin、Mint、Burn、BurnBlocked（销毁违规地址余额）、Pause、Unpause、Metadata；通过 B20TokenRole 枚举和 RoleManaged trait 管理。

**共享操作层**（代码确认）：`crates/common/precompiles/src/common/ops/` 提供 Burnable、Mintable、Pausable、Permittable（EIP-2612 permit）、Transferable、Configurable 等 trait，两种变体复用共享逻辑。

**ActivationRegistry**（代码确认）：Beryl precompile 通过 ActivationFeature（B20Factory, B20Token 等）按特性激活，而非一次性全部上线。

**硬分叉位置**（代码确认）：Beryl 在 Base 硬分叉序列中位于 Azul 之后（hardforks.rs），是 Base 链自主架构演进的一部分。

**与 TIP-20 的关键异同**：两者均为 precompile 级代币标准，均有 Factory/Policy/RBAC 架构；B20 提供 Asset 和 Stablecoin 两种变体覆盖通用代币与稳定币场景，TIP-20 通过扩展 TIPs 实现支付优化（memo/Payment Lanes）；B20 在 EVM L2 上实现协议层合规（继承 Ethereum 安全模型），TIP-20 在独立 L1 上实现。

- **Priority**: high
- **Dependencies**: item-3

### item-6: TIP-20 (Tempo) 协议层合规架构

深度分析 TIP-20 作为 precompile 级代币标准的架构设计，重点对比与 ERC-3643 应用层方案和 B20 协议层方案的差异。覆盖：

**Precompile 架构**：TIP-20 合约通过 precompile 创建，使用特殊地址格式（12 字节前缀 0x20c0...00 + token ID）；precompile 系统将 Tempo 特定 precompiles 注册到 PrecompilesMap（TIP20、TIP20Factory、TIP403Registry、TipFeeManager、StablecoinDEX 等）；通过 tempo_precompile! 宏强制 direct-call-only（禁止 delegatecall）并设置 storage context。

**合规机制（TIP-403 Policy Registry）**：每个 TIP-20 代币可引用 policy 控制 sender/receiver 资格：whitelist policies、blacklist policies；policy 可跨 token 共享，实现一致合规执行；TIP-1015 扩展 TIP-403 支持 compound policies（sender/recipient 不同授权规则）。

**RBAC**：ISSUER_ROLE（mint/burn）、PAUSE_ROLE/UNPAUSE_ROLE（暂停/恢复）、BURN_BLOCKED_ROLE（销毁违规地址余额）；grantRole/revokeRole/renounceRole/setRoleAdmin 管理。

**支付优化**：32 字节 memo 支持（支付引用/发票 ID）；ISO 4217 货币标识符（"USD"/"EUR"/"GBP"）；专用 Payment Lanes（保留区块空间，非支付交易上限 45% 总 Gas 限制 = 225 MGas）；Gas 目标 < $0.001/transfer；sub-second finality (~0.5s)；TIP-1034 Channel Reserve Precompile 比 legacy 合约节省最高 72% Gas。

**与 ERC-3643 的关键差异**：合规逻辑在协议层而非应用层执行；precompile 执行比 Solidity 合约更高效（无 EVM 解释开销）；标准行为跨 token 一致（ERC-20 各 token 实现可能不同）；升级需链级硬分叉而非合约重部署。

**与 B20 的关键差异**：TIP-20 在独立 L1 上实现，B20 在 EVM L2 上实现；TIP-20 有专用 Payment Lanes 和 StablecoinDEX 原生集成，B20 通过 Asset/Stablecoin 双变体覆盖通用与稳定币发行场景；TIP-20 生态包含 Chainalysis/AllUnity/Bridge/LayerZero 集成，B20 继承 Base/Ethereum 生态。

**生态系统**：Chainalysis 集成（TIP-20 memo 解码/监控）；KlarnaUSD 首个银行发行 token；AllUnity/Bridge/LayerZero 基础设施支持；20,000 TPS testnet / 200,000+ TPS 路线。

**扩展 TIPs**：TIP-1004（EIP-2612 permit）、TIP-1006（burnAt）、TIP-1022（虚拟地址存款转发）、TIP-1035（Implicit Approval List）。

- **Priority**: high
- **Dependencies**: item-3, item-5

### item-7: Circle Arc 与其他协议层合规方案

分析 Circle Arc 和 Plume 等新兴专用链如何从链级别嵌入合规。Circle Arc 作为补充参考方案，与 B20/TIP-20 precompile 路线对比。

**Circle Arc**：2025 年 8 月公开测试网；定位为 "purpose-built for stablecoin finance" 的 L1；USD 计价 Gas 费；sub-second settlement (~780ms / 100 validators)；permissioned validator set（合规机构运营商）；隐私子系统通过 EVM precompile 暴露（可插拔密码学后端）；StableFX 机构级外汇引擎；CCTP 跨链分发；$222M ARC token presale（a16z/Apollo/BlackRock/ICE/Standard Chartered 参投，$3B 估值）；计划 2026 年主网上线。

**Plume Network**：基于 Arbitrum Orbit 的 RWA 专用 L2；协议层嵌入 KYC/AML 和合规代币标准支持；Arc 代币化引擎 + Nexus 数据桥（zkTLS）+ Passport 智能钱包；SEC 注册转让代理；WisdomTree 14 支代币化基金；Apollo $50M 部署；$645M 托管资产。

- **Priority**: medium
- **Dependencies**: item-5, item-6

### item-8: 应用层合规 vs 协议层合规 -- 设计范式对比

基于前序 items 的分析，提炼两条技术路线的系统性对比。这是本研究的核心产出之一，不是功能清单而是设计范式分析。覆盖：

**合规执行层级**：应用层（Solidity 合约，EVM 解释执行）vs 协议层（precompile/链原生，直接编译执行）。

**性能与 Gas**：ERC-3643 每次 transfer 多次跨合约调用（Identity Registry + Compliance Module）的 Gas 开销 vs B20/TIP-20 precompile 单次原生调用的 Gas 优势；TIP-1034 比 legacy 合约节省最高 72% Gas 的证据；quantify 差异的困难性和现有 qualitative 证据。

**标准化与一致性**：ERC-20 各实现行为可能不同 vs B20/TIP-20 所有 token 行为一致（同一 precompile 逻辑）；ERC-3643 Compliance Module 可独立升级 vs precompile 升级需硬分叉。

**可组合性**：ERC-3643 与 $50B+ DeFi TVL 生态即插即用（但有合规失败问题）vs B20 继承 Base/Ethereum 生态（EVM L2 优势）vs TIP-20/Arc 生态系统仍在早期建设。

**可移植性**：ERC-3643 可在任何 EVM 链部署 vs B20 仅限 Base 链 vs TIP-20 仅限 Tempo 链 vs Circle Arc 仅限 Arc 链。

**监管确定性**：协议层执行提供更强的不可绕过保证 vs 应用层可能存在合约漏洞/绕过路径。

**升级灵活性**：smart-contract 可独立升级 vs precompile 需链级协调。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-6, item-7

### item-9: 合规能力 Taxonomy

定义统一的 8 类合规能力分类体系，确保后续各标准分析使用一致的分类。每类需明确定义、子能力列举、以及该能力在各标准中的实现差异概述。

| 能力类别 | 包含能力 |
|---------|---------|
| **Identity / KYC** | 链上身份绑定（ONCHAINID / wallet-identity mapping）、claim-based verification、trusted issuers、off-chain KYC 桥接、self-sovereign identity |
| **Transfer Policy** | allowlist/blocklist、sender/receiver/executor 维度分离（B20 4-slot policy / TIP-1015）、policy registry（B20 PolicyRegistry / TIP-403）、跨 token 共享 policy、jurisdiction-specific 规则、lockup/vesting |
| **Issuer Controls** | mint/burn/batchMint/batchBurn、freeze/pause（全局 + 地址级）、forced transfer/clawback（ERC-1644 controllerTransfer）、supply cap |
| **Sanctions / Blacklist** | Chainalysis 集成、OFAC 合规、blocked address 处理、BurnBlocked role（B20/TIP-20） |
| **Recovery** | 密钥丢失恢复、token 强制转移（ERC-1644）、identity 恢复流程 |
| **Legal Document / Metadata** | 链上文档关联（ERC-1643 bytes32 + URI + hash）、security identifier（ISIN/CUSIP）、announcement 机制、currency identifier（ISO 4217）、Metadata role（B20） |
| **Payment Reconciliation** | memo 字段（TIP-20 32-byte memo）、currency identifier、传统支付系统对接、invoice ID/payment reference |
| **Auditability / Privacy** | 链上可审计性（全部交易可追溯）vs 持有者隐私保护（ONCHAINID 不存储 PII，存储 hash/引用）、selective disclosure、regulator observer access、Circle Arc 隐私子系统 |

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-6, item-7

### item-10: 评估维度框架与横向对比矩阵

提炼后续横向对比的统一维度，并构建初步对比矩阵。

**7 个评估维度**：

1. **架构层级**：应用层 (Solidity smart contract) / 协议层 (precompile) / 混合
2. **合规机制类型**：on-chain identity (claim-based) / off-chain certificate / policy registry / permissioned validator
3. **身份模型**：self-sovereign (ONCHAINID) / centralized issuance / wallet-level / no native identity
4. **DeFi 可组合性**：ERC-20 compatible / custom standard / permissioned-only / ecosystem-limited
5. **发行方控制力**：freeze/pause/forced-transfer/clawback/burn 的粒度和权限模型
6. **Gas 开销**：per-transfer overhead（identity check + compliance check + token transfer 的复合成本）
7. **规范成熟度**：Final ERC / Draft EIP / Chain-specific precompile (code-confirmed) / Testnet-only / Proposal

**初步横向对比矩阵**（Deep draft 需填充具体证据）：

| 维度 | ERC-3643 | ERC-1400 | B20 | TIP-20 | Circle Arc |
|------|----------|----------|-----|--------|------------|
| 架构层级 | 应用层 (Solidity) | 应用层 (Solidity) | 协议层 (precompile, EVM L2) | 协议层 (precompile, L1) | 协议层 (链原生, L1) |
| 合规机制 | On-chain identity (claim-based) | Off-chain certificate + operator | Policy registry (4-slot) | Policy registry (TIP-403) | Permissioned validators + precompile privacy |
| 身份模型 | Self-sovereign (ONCHAINID) | Operator-controlled | Wallet-level policy | Wallet-level policy | Institutional validator set |
| DeFi 可组合性 | ERC-20 compatible（有限制） | ERC-20 compatible（有限制） | Base 生态内（EVM L2 优势） | TIP-20 生态内 | Arc 生态内 |
| 发行方控制力 | Agent role: freeze/forced transfer/recovery | Controller: forced transfer (ERC-1644) | RBAC 7-role: mint/burn/burnBlocked/pause/unpause/metadata/admin | RBAC: issuer/pause/burn_blocked | Institutional operator controls |
| Gas 开销 | 高（多合约调用） | 中-高（partition 存储开销） | 低（precompile 原生执行, code-inferred） | 低（precompile 原生执行） | 低（链原生） |
| 规范成熟度 | Final ERC (2023) | Draft proposal (2018, 未 finalize) | Chain precompile (code-confirmed, Beryl hardfork, 公开规范未发布) | Chain-specific TIP (production) | Testnet (2025, 主网 2026 计划) |

- **Priority**: high
- **Dependencies**: item-8, item-9

### item-11: L2/新链为何倾向 precompile/协议层路线

综合分析新兴 L2 和专用链选择 precompile/协议层合规路线的驱动力。不是简单列举优势，而是分析架构选择背后的商业和技术逻辑。覆盖：

**性能优势**：precompile 绕过 EVM 解释器，直接执行编译后代码；Tempo 20,000 TPS testnet + 专用 Payment Lanes 保证支付交易不被挤出；Base B20 继承 Flashblocks sub-second confirmation；Circle Arc < 1s finality。

**Gas 成本**：TIP-1034 Channel Reserve Precompile 比 legacy 合约节省最高 72% Gas；sub-millidollar transfer 成本 vs ERC-3643 多合约调用开销；B20 precompile 同样避免 EVM 解释开销（具体 Gas 数据待 Beryl 规范发布）。

**标准化优势**：协议层强制所有 B20/TIP-20 token 行为一致，消除实现差异；integrator 只需对接一个标准而非每个 token 的不同实现。

**监管确定性**：协议层执行 = 不可绕过的合规保证（vs 应用层合约可能存在绕过路径或 bug）；permissioned validator set（Arc）提供额外监管信任层。

**新链优势**：无历史包袱，可从 genesis/hardfork 嵌入合规能力；Base 选择通过 Beryl hardfork 在成熟 L2 上追加协议层合规，说明 precompile 路线对现有链同样可行。

**代价**：失去跨链可移植性（B20 限 Base，TIP-20 限 Tempo）；生态系统需从零建设或继承（B20 继承 Base/Ethereum 生态的程度待评估）；升级需全链协调；标准仅限本链有效。

- **Priority**: high
- **Dependencies**: item-8

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| regulatory_event | 监管事件名称、日期、管辖区、对 Token 标准的具体影响、来源链接；EU 监管须区分 MiFID II/DLT Pilot（代币化证券）与 MiCA（非金融工具加密资产）（G1） | item-1, item-2 |
| market_metric | RWA 总规模、资产类别、链分布、机构名称/参与方式、数据来源和访问日期 | item-2 |
| architecture_component | 标准的架构组件名称、角色、接口、合约间调用关系 | item-3, item-4, item-5, item-6, item-7 |
| transfer_flow | 从发起到执行/拒绝的完整 transfer 流程，标注每一步的检查内容和涉及合约/precompile | item-3, item-4, item-5, item-6 |
| gas_characteristic | 定性/定量 Gas 特征描述、与 ERC-20 baseline 的对比、batch 优化效果 | item-3, item-4, item-5, item-6, item-8, item-11 |
| composability_constraint | 与 DeFi 协议交互时的限制、失败场景、用户体验影响 | item-3, item-4, item-8 |
| compliance_capability | 在 8 类 Taxonomy 中的具体实现方式、能力强弱、缺失项 | item-3, item-4, item-5, item-6, item-7, item-9 |
| standard_maturity | 规范状态（Final/Draft/Proposal/Testnet/Code-confirmed）、关键里程碑日期、治理结构、社区采用 | item-3, item-4, item-5, item-6, item-7, item-10 |
| design_paradigm | 应用层 vs 协议层的设计选择理由、trade-off 分析、适用场景判断 | item-8, item-11 |
| evidence_classification | 每个关键 claim 的证据类型：primary-source / code-inferred / secondary / inferred；B20 相关 claim 须标注 "code-inferred pending Beryl spec" | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | ERC-3643 架构图：Token Contract、ONCHAINID、Identity Registry、Trusted Issuers Registry、Claim Topics Registry、Compliance Module 的组件关系和 transfer 检查流程 | mermaid | item-3 |
| diag-2 | architecture | ERC-1400 模块化架构图：ERC-1410 Partition、ERC-1594 Core、ERC-1643 Document、ERC-1644 Controller 的子标准关系和 transfer 验证流程 | mermaid | item-4 |
| diag-3 | architecture | B20 Precompile 架构图：B20Factory、B20Asset/Stablecoin 两变体、PolicyRegistry、ActivationRegistry、RBAC 角色的系统级组件关系和地址派生流程 | mermaid | item-5 |
| diag-4 | architecture | TIP-20 Precompile 架构图：Precompile 地址空间、TIP20Factory、TIP403Registry、Payment Lanes、FeeManager 的系统级组件关系 | mermaid | item-6 |
| diag-5 | comparison | 应用层 vs 协议层合规范式对比图：合规检查在 EVM 执行栈中的位置差异（Solidity 合约层 vs Precompile 层），transfer 路径和 Gas 消耗对比 | mermaid | item-8 |
| diag-6 | comparison | 五大标准/方案横向对比矩阵可视化：按 7 个评估维度展示 ERC-3643、ERC-1400、B20、TIP-20、Circle Arc 的对比结果 | mermaid | item-10 |
| diag-7 | taxonomy | 合规能力 Taxonomy 可视化：8 类能力及其子能力的分类树状图 | mermaid | item-9 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_standard | ERC-3643 EIP 规范、T-REX GitHub 仓库（TokenySolutions/T-REX）、ERC-3643 Association 公告、Tokeny 官方文档 | 4 |
| src-2 | official_standard | ERC-1400/ERC-1410/ERC-1594/ERC-1643/ERC-1644 EIP 规范、Polymath 官方文档、ConsenSys Universal Token 实现 | 3 |
| src-3 | code_analysis | Base B20 precompile 源码（base/base@8e8767281d，crates/common/precompiles/src/b20*、policy/、common/ops/），代码确认的架构组件和接口 | 3 |
| src-4 | official_docs | Tempo TIP-20 规范（docs.tempo.xyz/protocol/tip20/spec）、TIP-403 Policy Registry、tempo-std 接口、TIP-1015/TIP-1034 等扩展 TIP | 4 |
| src-5 | official_docs | Circle Arc 公告、技术文档、测试网信息；Plume Network 官方文档和部署数据 | 3 |
| src-6 | regulatory_sources | EU MiFID II、Prospectus Regulation、CSDR、DLT Pilot Regime (EU 2022/858)、MiCA (EU 2023/1114) Article 2 排除条款（G1）；DTC no-action letter PDF (SEC)、Commissioner Peirce 声明（G2）；GENIUS Act；MAS Project Guardian；香港稳定币条例 | 5 |
| src-7 | on_chain_data | RWA 市场数据（rwa.xyz、Dune Analytics、DefiLlama），标注查询时间和口径 | 2 |
| src-8 | industry_analysis | 第三方对比分析（Tokeny ERC-3643 vs ERC-1400 对比、Chainalysis ERC-3643 introduction、Oraclizer regulatory gaps 分析、Zealynx 对比） | 3 |
| src-9 | institutional_evidence | DTCC 加入 ERC-3643 Association、Franklin Templeton 代币化基金、BlackRock BUIDL、KlarnaUSD on Tempo、Circle Arc presale 参与者 | 3 |

## Required Output Tables

### 合规能力 Taxonomy 表

Deep draft 必须包含以下 8 类 Taxonomy 表，每行需有定义、子能力列举和各标准的实现差异概述：

| 能力类别 | 定义 | 子能力 | ERC-3643 | ERC-1400 | B20 | TIP-20 | Circle Arc |
|---------|------|--------|----------|----------|-----|--------|------------|
| Identity / KYC | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Transfer Policy | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Issuer Controls | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Sanctions / Blacklist | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Recovery | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Legal Document / Metadata | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Payment Reconciliation | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Auditability / Privacy | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |

### 评估维度横向对比矩阵

Deep draft 必须包含以下 7 维度对比矩阵，每格需有可追溯证据或明确标注为判断/推论/code-inferred：

| 维度 | ERC-3643 | ERC-1400 | B20 | TIP-20 | Circle Arc |
|------|----------|----------|-----|--------|------------|
| 架构层级 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| 合规机制类型 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| 身份模型 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| DeFi 可组合性 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| 发行方控制力 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Gas 开销 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| 规范成熟度 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-1 | G1: 分离 MiCA（非金融工具加密资产）与 EU 代币化证券框架（MiFID II/Prospectus/CSDR/DLT Pilot）；MiCA Article 2 排除金融工具 | Review Verdict R1 (928aea05) — major finding |
| 2 | modify_item | item-1 | G2: DTC no-action letter 措辞限定；SEC 工作人员授予有限的事实限定 relief，不构成对 ERC-3643 的正式批准 | Review Verdict R1 (928aea05) — major finding |
| 2 | modify_item | item-3 | G2: 标准成熟度部分增加 DTC no-action letter 准确措辞 | Review Verdict R1 (928aea05) — major finding |
| 2 | add_item | item-5 (B20) | 恢复 B20（Base Beryl precompile）为协议层主要参照方案；代码确认于 base/base@8e8767281d；原 item-6 Circle Arc 降级为补充参考 | Orchestrator Revision Request — Change 3 |
| 2 | modify_item | item-6 (原 item-5 TIP-20) | 重编号为 item-6；增加与 B20 的对比维度 | Orchestrator Revision Request — Change 3 (renumber) |
| 2 | modify_item | item-7 (原 item-6 Circle Arc) | 重编号为 item-7；降级为补充参考方案，不再替代 B20 | Orchestrator Revision Request — Change 3 |
| 2 | modify_item | item-8-11 | 重编号 item-7→8, item-8→9, item-9→10, item-10→11；所有对比矩阵扩展为 5 列（+B20） | Orchestrator Revision Request — Change 3 (renumber + expand) |
| 2 | add_section | Regulatory Scope Guardrails | 新增 G1/G2 guardrail 块，确保 deep draft 不重犯 MiCA 和 SEC/DTC 措辞错误 | Review Verdict R1 (928aea05) |
| 2 | modify_field | evidence_classification | 新增字段，要求 B20 相关 claim 标注 "code-inferred pending Beryl spec" | Orchestrator Revision Request — Change 3 |
| 2 | add_diagram | diag-3 (B20) | 新增 B20 架构图 | Orchestrator Revision Request — Change 3 |
| 2 | modify_diagram | diag-5, diag-6 | 横向对比扩展为 5 列 | Orchestrator Revision Request — Change 3 |
| 2 | add_source_req | src-3 (code_analysis) | 新增 B20 代码分析来源要求 | Orchestrator Revision Request — Change 3 |
| 2 | modify_source_req | src-5→src-6 (regulatory) | 增加 MiFID II/DLT Pilot/CSDR 作为 EU 代币化证券法源要求（G1），增加 DTC no-action letter PDF 和 Peirce 声明要求（G2） | Review Verdict R1 (928aea05) |
| 3 | modify_item | item-5 Token 变体 | B20Variant 在 pinned commit 8e8767281d 仅定义 Asset(=0) 和 Stablecoin(=1) 两种变体；移除 Security(=2) 相关表述，标注为本地分支 a052beb 未来演进观察 | Orchestrator R3 Verdict (3d0ad114) — surgical fix |
| 3 | modify_item | item-5 共享操作层 | "三种变体复用共享逻辑" → "两种变体复用共享逻辑" | Orchestrator R3 Verdict (3d0ad114) — variant count alignment |
| 3 | modify_item | item-5 TIP-20 对比 | 移除 "B20 定义了 Security 变体（6 decimals，含赎回机制）"，改为 Asset/Stablecoin 双变体场景覆盖描述 | Orchestrator R3 Verdict (3d0ad114) — surgical fix |
| 3 | modify_item | item-6 B20 对比 | 移除 "B20 更侧重 Security token 变体和赎回机制"，改为 Asset/Stablecoin 双变体覆盖描述 | Orchestrator R3 Verdict (3d0ad114) — surgical fix |
| 3 | modify_diagram | diag-3 | "B20Token/Stablecoin/Security 三变体" → "B20Asset/Stablecoin 两变体" | Orchestrator R3 Verdict (3d0ad114) — variant count alignment |
