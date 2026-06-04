---
topic: "ERC-3643 (T-REX) 深度分析"
project_slug: "compliance-token-standards"
topic_slug: "erc3643-trex-analysis"
github_repo: "Whisker17/multica-research"
round: 2
status: candidate

artifact_paths:
  outline: "compliance-token-standards/outlines/erc3643-trex-analysis.md"
  draft: "compliance-token-standards/research-sections/erc3643-trex-analysis/drafts/round-{n}.md"
  final: "compliance-token-standards/research-sections/erc3643-trex-analysis/final.md"
  index: "compliance-token-standards/research-sections/_index.md"

scope: "ERC-3643（T-REX）标准的单标准深度分析。核心组件架构（Token Contract、Identity Registry、Identity Registry Storage、Compliance Module、Trusted Issuers Registry、Claim Topics Registry）；ONCHAINID 去中心化身份体系（ERC-734/735 基础、claim 结构、密钥管理、隐私最佳实践）；Transfer 合规检查流程（sender balance/freeze 检查 → receiver identity 验证 → Compliance Module 规则检查的标准路径）；Recovery & Freeze 机制（Agent role、partial freeze、forced transfer、pause、batch operations）；与 ERC-20 的兼容性与可升级架构（UUPS proxy、Implementation Authority）；生态与机构采用（$32B+ 资产、180+ 司法管辖区、92+ Association 成员、DTCC ComposerX、Apex Group、Invesco、Chainlink ACE、SEC 引用 [source required]）；局限性分析（Gas 开销、中心化依赖、DeFi 可组合性、跨链挑战）。使用 WHI-177 提炼的 8 类合规能力 Taxonomy 和 7 维度评估框架对 ERC-3643 进行结构化评估。"
audience: "区块链协议工程师、RWA/合规产品负责人、机构金融/BD 团队、Research Review Agent。读者熟悉 EVM 和 ERC-20，但需要 ERC-3643 每个组件的技术细节、合规设计取舍分析、以及与行业趋势的关系。"
expected_output: "compliance-token-standards/outlines/erc3643-trex-analysis.md，包含：标准历史与治理、6 组件架构深度分析、ONCHAINID 身份体系、Transfer 流程、Issuer Controls、ERC-20 兼容性、生态采用、局限性分析、8 类合规能力评估、7 维度框架打分"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-04T08:20:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-04T08:35:00Z"

multica_issue_id: "4036a12f-42fd-4ec1-a113-18df6c26c9a1"
branch_name: "research/compliance-token-standards/erc3643-trex-analysis"
base_commit: "008e66bff9bfb866807c2a1f7f7131be9cba232b"
language: "中文"
research_depth: "deep"
---

# Research Outline: ERC-3643 (T-REX) 深度分析

## Research Questions

1. ERC-3643 的 6 个核心组件（Token Contract、Identity Registry、Identity Registry Storage、Modular Compliance、Trusted Issuers Registry、Claim Topics Registry）如何协同工作实现"架构级不可能的非合规转账"？各组件的接口、职责边界和合约间调用关系是什么？
2. ONCHAINID（基于 ERC-734/735）如何实现可验证的合规身份？Tokeny 参考实现采用的隐私最佳实践（链上仅存 claim hash/引用）与 ERC-735 协议层接口（`bytes data` 和 `string uri` 字段不在协议层阻止 PII 上链）之间的区别是什么？Trusted Issuer 模型引入了什么信任假设？
3. ERC-3643 标准 transfer 路径中，sender 检查（balance/freeze status）和 receiver 检查（`IdentityRegistry.isVerified(receiver)`）、Compliance Module 检查（`canTransfer(from, to, amount)`）各自承担什么角色？如果部署的 compliance module 额外约束 sender identity，这属于模块特定行为还是标准路径？失败时的 revert 行为对用户体验和 DeFi 集成有何影响？
4. Agent role（EIP-173 + Agent 扩展）赋予了哪些行政权力（freeze、forced transfer、recovery、pause）？这些权力如何在合规需要和去中心化理想之间取舍？
5. ERC-3643 作为 ERC-20 扩展的完全兼容性如何实现？UUPS proxy（ERC-1822）+ Implementation Authority 的可升级架构有何设计取舍？
6. $32B+ 资产代币化、180+ 司法管辖区、92+ Association 成员——这些数据背后的机构采用逻辑是什么？DTCC、Apex Group、Invesco、Chainlink ACE 的参与各意味着什么？
7. ERC-3643 的 Gas 开销（多合约跨调用）、中心化依赖（Trusted Issuers）、DeFi 可组合性限制（silent revert）和跨链挑战各有多严重？有哪些缓解策略？
8. 使用 WHI-177 建立的 8 类合规能力 Taxonomy 对 ERC-3643 进行结构化评估时，其在每个能力类别的强弱项如何分布？在 7 维度评估框架下 ERC-3643 的定位是什么？

## Regulatory Scope Guardrails

> **G1 — EU 监管框架分离**：EU 代币化证券（STO）受 **MiFID II、Prospectus Regulation、CSDR 和 DLT Pilot Regime（EU 2022/858）**规制。MiCA（EU 2023/1114）Article 2 明确排除构成金融工具的加密资产，其适用范围为非金融工具加密资产（ART/EMT/CASP）。本文涉及 EU 代币化证券法律时以 DLT Pilot / MiFID II / Prospectus / CSDR 为主要来源。
>
> **G2 — DTC no-action letter 措辞限定**：DTC 在其 no-action 请求中将 ERC-3643 引用为合规感知协议示例之一；SEC 工作人员（2025 年 12 月）就该 DTC 事实模式授予了有限的、事实限定的三年期 no-action relief；该回复不建立更广泛的法律结论。SEC 主席 Atkins 在 "Project Crypto" 演讲中在 innovation exemption 拟议条件下将 ERC-3643 作为合规特性代币标准的示例点名。两者均不构成 SEC 对 ERC-3643 的正式批准、认可或背书。

## Items

### item-1: 标准概述与历史沿革

建立 ERC-3643 的基本事实底座。覆盖：

**起源与命名**：T-REX（Token for Regulated EXchanges）由 Tokeny Solutions（卢森堡）开发；EIP-3643 于 2021 年提交，2023 年达到 Final 状态——目前唯一 Final 的 Ethereum 合规代币标准。

**治理结构**：ERC-3643 Association（非营利组织），成员包括 DTCC、Apex Group、Invesco、Deloitte、Fireblocks、OpenZeppelin、Ava Labs、Hedera Foundation 等 92+ 机构（截至 2025 年）。

**关键里程碑**：2018 年 T-REX v1 发布 -> 2021 年 EIP-3643 提交 -> 2023 年 Final -> DTCC 加入 Association [source required: 确认具体日期] -> SEC 主席 Atkins 演讲点名 [source required: 确认日期和措辞] -> DTC no-action letter 引用（G2 适用）[source required: 确认日期] -> Chainlink ACE 合作 [source required] -> ISO TC 307 标准化推进 [source required]。

**与先前标准的关系**：ERC-1400（Draft，未 finalize）、ERC-1404（minimal transfer restriction）的对比定位。

- **Priority**: high
- **Dependencies**: none

### item-2: 核心组件架构深度分析

对 ERC-3643 的 6 个核心合约进行技术层面的深度分析，建立组件间依赖关系和调用拓扑的清晰图景。

**Token Contract（IToken）**：ERC-20 扩展，conditional transfer/transferFrom；在每次转账中调用 Identity Registry 和 Compliance Module；继承完整 ERC-20 接口保证向后兼容。

**Identity Registry（IIdentityRegistry）**：wallet address -> ONCHAINID 合约的映射；核心方法 `isVerified(address)`：检查地址是否拥有合规 ONCHAINID 且所需 claims 有效。

**Identity Registry Storage（IIdentityRegistryStorage）**：将身份数据存储与逻辑分离，支持升级 Identity Registry 逻辑而不丢失身份映射数据。

**Trusted Issuers Registry（ITrustedIssuersRegistry）**：维护授权 KYC/claim 提供者地址列表；仅由此注册表中的 issuer 签发的 claims 被系统接受。

**Claim Topics Registry（IClaimTopicsRegistry）**：定义每个 token 所需的 claim 类型（topic ID）；不同 token 可要求不同的 claim topics。

**Modular Compliance（IModularCompliance）**：可插拔合规规则引擎；独立于 Token Contract 升级；支持投资者上限、司法管辖限制、锁定期、认证状态等规则；核心方法 `canTransfer(from, to, amount)` 和 `transferred(from, to, amount)` 回调。

**合约间依赖拓扑**：Token -> Identity Registry -> Identity Registry Storage / Trusted Issuers Registry / Claim Topics Registry -> ONCHAINID；Token -> Compliance Module。

- **Priority**: high
- **Dependencies**: item-1

### item-3: ONCHAINID 去中心化身份体系

深度分析 ERC-3643 身份层的技术设计和信任模型。

**ERC-734/735 基础**：ONCHAINID 基于 ERC-734（Key Management）和 ERC-735（Claim Holder）标准。每个用户部署独立的 ONCHAINID 合约，该合约可跨多个 token 复用。

**Claim 结构**：claim = { topic, scheme, issuer, signature, data, uri }。ERC-735 接口中 `bytes data` 和 `string uri` 字段在协议层不阻止 PII 上链——隐私保护是实现层最佳实践而非协议层保证。Tokeny 参考实现采用链上仅存 claim hash/引用、off-chain 存储实际 PII 的隐私模式 [source required: Tokeny/ONCHAINID 官方文档确认]。Claim 由 Trusted Issuer 签发，链上可验证签名有效性。

**密钥管理**：支持多密钥架构（management keys, action keys, claim signer keys, encryption keys）；密钥轮转不影响 claim 有效性。

**隐私设计**：自主身份（self-sovereign）模型；用户控制自己的 ONCHAINID 合约。隐私保证层级需区分：(a) 协议层——ERC-735 `bytes data`/`string uri` 不在协议层阻止 PII 存储；(b) 实现层——Tokeny 参考实现和 ONCHAINID 文档推荐的 hash-only 隐私模式；(c) 部署层——实际隐私取决于 claim issuer 的实现选择。

**信任假设分析**：系统安全性依赖 Trusted Issuers Registry 的正确配置——如果不当 issuer 被信任或合法 issuer 被移除，会导致身份验证失效。Issuer 的选择权集中在 Token Owner/Agent。

**与 wallet-level policy（B20/TIP-20）的差异**：ERC-3643 提供 claim-based identity verification（语义丰富，可表达 KYC 状态、认证类型、司法管辖等），B20/TIP-20 提供 wallet-level allowlist/blocklist（二值判断，依赖 off-chain 流程）。

- **Priority**: high
- **Dependencies**: item-2

### item-4: Transfer 合规检查流程

完整还原 ERC-3643 标准 transfer 路径，这是该标准实现"非合规转账架构级不可能"的核心机制。

**标准 Transfer 路径**（per ERC-3643 spec 和 Token.sol 参考实现）：

**Step 1 — 交易发起**：用户调用 `transfer(to, amount)` 或 `transferFrom(from, to, amount)`，Token Contract 拦截调用。

**Step 2 — Sender 状态检查**：Token Contract 检查 sender 的 frozen status（`isFrozen(sender)` / `getFrozenTokens(sender)`）和可用余额（balance - frozenTokens >= amount）。这是 sender 侧检查——不涉及 Identity Registry 调用。

**Step 3 — Receiver Identity 验证**：Token Contract 调用 `IdentityRegistry.isVerified(receiver)`（注意：标准路径仅验证 **receiver**，不验证 sender identity）。Identity Registry 查找 receiver 地址关联的 ONCHAINID 合约；遍历 Claim Topics Registry 获取该 token 要求的 claim topics；对每个 topic 遍历 Trusted Issuers Registry 验证 ONCHAINID 上是否有合法 issuer 签发的有效 claim。

**Step 4 — Compliance Module 检查**：Token Contract 调用 `Compliance.canTransfer(from, to, amount)` 检查业务规则（投资者上限、国家/地区限制、锁定期、最小/最大持有量、认证要求等）。

**Step 5 — 执行或 Revert**：全部通过则执行转账并调用 `Compliance.transferred(from, to, amount)` 更新内部状态；任一检查失败则整笔交易 revert。

**Module-specific 扩展**：部署的 Compliance Module 可以在 `canTransfer()` 内额外约束 sender identity/status（如要求 sender 也满足特定 claim 条件），但这属于**模块特定行为**，不是 ERC-3643 标准 transfer 路径的一部分。Deep draft 需明确区分标准路径和模块扩展行为。

**Revert 行为分析**：ERC-3643 transfer 失败时产生 EVM revert（不是返回 false），DeFi 协议通常不处理 ERC-3643 特定的 revert reason，导致用户获得通用的"transaction failed"而非具体的合规失败原因。

**canTransfer 预检查**：提供 `canTransfer()` view 函数供前端预检查，避免用户提交注定失败的交易。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: Issuer Controls — Recovery、Freeze 与 Agent 机制

分析 ERC-3643 赋予发行方的行政控制权力，这是合规代币标准区别于普通 ERC-20 的关键设计。

**Agent Role 体系**：EIP-173 Ownership + Agent 角色扩展。Owner 设置 Agent；Agent 执行行政操作。权限分离：Owner 管理标准配置（设置 Agent、管理依赖合约、修改 name/symbol），Agent 执行运营操作（mint、burn、freeze、forced transfer、recovery）。

**Freeze 机制**：
- `setAddressFrozen(address, bool)` — 冻结/解冻整个钱包
- `freezePartialTokens(address, amount)` — 冻结钱包内指定数量的 token
- `unfreezePartialTokens(address, amount)` — 解冻部分 frozen token
- 冻结的 token 不可转账但保留在原地址

**Forced Transfer**：Agent 可执行 `forcedTransfer(from, to, amount)`，无需双方同意。用于法院命令执行、监管要求、资产追回。

**Recovery**：`recoveryAddress(lostWallet, newWallet, investorONCHAINID)` — 当投资者丢失钱包私钥时，Agent 可将 token 从旧钱包转移至新钱包，同时更新 Identity Registry 映射。链上保留 recovery 历史记录。

**Pause**：`pause()` / `unpause()` — 全局暂停所有 token 操作（transfer、mint、burn）。

**Batch Operations**：`batchTransfer`、`batchForcedTransfer`、`batchMint`、`batchBurn`、`batchSetAddressFrozen`、`batchFreezePartialTokens`、`batchUnfreezePartialTokens` — 单笔交易处理多个操作，摊薄 Gas 成本。

**与 B20/TIP-20 的对比**：ERC-3643 Agent 拥有 forced transfer 和 identity-level recovery（B20/TIP-20 仅有 burnBlocked，无 forced transfer）；ERC-3643 的 freeze 粒度更细（partial freeze vs 全局 policy）。

- **Priority**: high
- **Dependencies**: item-2

### item-6: ERC-20 兼容性与可升级架构

分析 ERC-3643 如何在保持 ERC-20 完全兼容的同时嵌入合规层，以及其可升级架构设计。

**ERC-20 完全兼容**：Token Contract 实现完整的 ERC-20 接口（`transfer`、`transferFrom`、`approve`、`allowance`、`balanceOf`、`totalSupply`）。任何支持 ERC-20 的钱包和工具可识别 token 余额和基本信息。差异在于 transfer/transferFrom 内嵌合规检查——对外部调用者来说接口相同，但行为不同（可能 revert）。

**"Conditional Transfer" 设计哲学**：不修改 ERC-20 接口签名，而是在同一接口内添加条件检查。ERC-3643 Association 称之为"non-compliant transfers are architecturally impossible"。

**UUPS Proxy（ERC-1822）**：T-REX 使用 Universal Upgradeable Proxy Standard 实现可升级性。不直接在 proxy 存储中保存实现合约地址，而是存储 Implementation Authority 合约地址。Implementation Authority 模式允许多个 proxy 共享同一逻辑合约并统一升级。

**升级风险**：proxy admin 拥有升级 Token 逻辑的权力——理论上可将 Token 实现替换为任意代码。这是所有 UUPS proxy 的固有风险，非 ERC-3643 特有，但在合规代币场景下风险放大（投资者资产安全依赖 admin 诚信）。

**与 ERC-1400 的对比**：ERC-1400 使用 partition/tranche 架构偏离标准 ERC-20，导致 DeFi 集成困难；ERC-3643 维持 ERC-20 接口一致性，集成摩擦更小。

- **Priority**: high
- **Dependencies**: item-2

### item-7: 生态与机构采用

建立 ERC-3643 当前采用规模和机构参与的事实底座，评估其市场地位。

**规模数据**：$32B+ 资产已通过 ERC-3643 代币化 [source required: Association 官方声称，需确认数据来源和口径]；180+ 司法管辖区部署 [source required]。

**ERC-3643 Association 治理**：92+ 成员机构（截至 2025 年底），2025 年新增 24 名成员。按类别：
- 金融基础设施：DTCC（2025 年 3 月加入，集成 ComposerX）、tZERO
- 资管/基金服务：Apex Group（收购 Tokeny）、Invesco、3iQ Corp、Kynthos Fund Services、Bolder Group
- 审计/咨询：Deloitte、Kaspersky、Hacken
- 区块链基础设施：Ava Labs、Hedera Foundation、Wormhole Foundation
- 开发工具：OpenZeppelin、Fireblocks、Halborn
- 银行：ABN AMRO

**关键集成**（G2 适用）：
- DTCC ComposerX 集成 ERC-3643 [source required: DTCC 公告/Association 新闻]
- Chainlink ACE（Automated Compliance Engine）与 Apex Group、GLEIF、ERC-3643 Association 合作 [source required: Chainlink/Association 公告确认日期]
- Fasanara Capital Polygon 货币市场基金 [source required]
- ABN AMRO 代币化债券 [source required]
- DTC no-action letter 引用（SEC 工作人员就 DTC 事实模式授予有限 relief，不构成 ERC-3643 背书）[source required: DTC no-action letter PDF 确认日期和措辞]
- SEC 主席 Atkins "Project Crypto" 演讲在 innovation exemption 拟议条件中点名 [source required: Atkins 演讲全文确认措辞]
- 西班牙 ISO TC 307 标准化提案 [source required]

**多链部署**：Ethereum（主链）、Polygon、Avalanche、Hedera 等。

**安全审计**：Kaspersky、Hacken 审计。

- **Priority**: high
- **Dependencies**: item-1

### item-8: Gas 开销定性分析

ERC-3643 transfer 的 Gas 成本是其最常被讨论的局限之一。由于无公开 benchmark 数据，本 item 进行结构化定性分析。

**标准路径开销来源分解**：
1. Sender 状态检查 — 内部存储读取（frozen status、balance），无跨合约调用
2. IdentityRegistry.isVerified(receiver) — 跨合约调用（CALL ~2,600 gas base）+ ONCHAINID 查找 + Claim Topics Registry 遍历 + Trusted Issuers Registry 遍历 + claim 签名验证。这是标准路径中唯一的 identity 验证调用
3. Compliance.canTransfer(from, to, amount) — 跨合约调用 + 业务规则逻辑（模块数量和复杂度决定开销）
4. 实际余额转移 — 标准 ERC-20 转账逻辑
5. Compliance.transferred(from, to, amount) — 回调更新内部状态

**估算**：标准路径每次 transfer 涉及 2-3 次外部合约调用（Identity Registry + Compliance canTransfer + Compliance transferred），加上 Identity Registry 内部对 ONCHAINID/Claim Topics/Trusted Issuers 的嵌套调用。估算总 Gas 为标准 ERC-20 transfer 的 2-8x（取决于 claim 数量和 compliance 规则复杂度）。来源：WHI-177 landscape 推断；行业分析一致认为"显著高于 ERC-20"但缺乏精确数字 [inferred]。注：Round 1 outline 错误地将 sender identity 验证计入标准路径，导致开销被高估（4-6+ 外部调用 → 实际 2-3 外部调用 + 嵌套子调用）。

**缓解策略**：
- Batch operations（batchTransfer 等）摊薄单笔固定开销
- Modular architecture 允许按需启用 compliance 模块
- 可优化的 Solidity 模式（unchecked counters、precomputed hashes、inline returns）
- 链选择：L2 上 Gas 绝对成本低

**场景适用性**：低频高价值交易（证券发行/转让）Gas 开销可忽略；高频交易场景不适合直接使用 ERC-3643。

**与 B20/TIP-20 precompile 的对比**：ERC-3643 在 EVM 解释器中执行多合约调用链；B20/TIP-20 在 precompile 中执行编译后原生代码（单次调用）。架构层级差异决定 Gas 差异不可弥合。

- **Priority**: high
- **Dependencies**: item-4

### item-9: DeFi 可组合性、中心化依赖与跨链挑战

综合分析 ERC-3643 的三类主要局限性。

**DeFi 可组合性限制**：
- Silent revert 问题：DEX/借贷协议调用 transfer 时，如果接收方未通过 identity 验证或 compliance 检查，交易 revert。DeFi 协议通常不处理 ERC-3643 特定 revert reason，用户体验差。
- 受限的持有者池：只有 isVerified 地址可持有 token，限制 LP 参与、AMM 流动性池构建。
- 结构性张力：permissioned token（ERC-3643）vs permissionless DeFi（Uniswap 等）的根本矛盾。
- 可能的解决方向：permissioned DeFi pools（如 Aave Arc 模式）、compliance-aware DEX。

**中心化依赖**：
- Trusted Issuers 选择权集中：Token Owner/Agent 决定信任哪些 KYC 提供者。如果 Issuer 作恶或被攻破，虚假 claim 可通过验证。
- Agent 权力集中：freeze、forced transfer、recovery 权力赋予 Agent 角色。虽然是监管合规所需，但构成单点风险。
- UUPS proxy admin：可替换 Token 实现逻辑。
- 缓解策略：多签 Owner/Agent、时间锁、治理委员会、审计。

**跨链挑战**：
- ERC-3643 作为 Solidity 应用层标准天然可移植到任何 EVM 链——这是相对 B20/TIP-20 的重大优势。
- 但跨链 transfer 需要目标链上同样部署完整的 ERC-3643 基础设施（Identity Registry、Trusted Issuers 等），且两条链的身份系统需互认。
- Wormhole Foundation 加入 Association 表明跨链互操作性是活跃研发方向。
- 非 EVM 链（Solana、Cosmos 等）需完全重新实现。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-6, item-8

### item-10: 合规能力 Taxonomy 结构化评估

使用 WHI-177 建立的 8 类合规能力 Taxonomy 对 ERC-3643 进行逐项深度评估。每个能力类别需给出实现方式、强弱判断、关键证据和与其他标准的差异化定位。

| 能力类别 | 预期评级 | 关键分析点 |
|---------|---------|-----------|
| **Identity / KYC** | 强 | ONCHAINID 完整 claim 验证链（标准路径验证 receiver identity）；self-sovereign 模型；ERC-734/735 基础；跨 token 复用；vs B20/TIP-20 无原生身份。注：PII 保护是 Tokeny 实现层最佳实践，非 ERC-735 协议层保证 |
| **Transfer Policy** | 中 | Compliance Module 可插拔规则；但粒度不如 B20 4-slot policy（无 sender/receiver/executor 分离）；无 compound policy 概念 |
| **Issuer Controls** | 强 | Agent role freeze(partial)/forced transfer/recovery/pause；batch operations；最强控制力之一（仅 ERC-1644 controllerTransfer 可比） |
| **Sanctions / Blacklist** | 中 | Compliance Module blacklist + Identity Registry claim revocation；无专门 BurnBlocked role（vs B20/TIP-20）；无原生 Chainalysis 集成（Chainlink ACE 补充） |
| **Recovery** | 强 | recoveryAddress 机制 + ONCHAINID 密钥轮转；链上 recovery 历史记录；唯一提供 identity-level recovery 的标准 |
| **Legal Document / Metadata** | 弱 | 无原生文档管理（vs ERC-1643/ERC-1400）；无 ISO 4217、无 security identifier；可通过外部合约补充 |
| **Payment Reconciliation** | 无 | 无 memo 字段、无 Payment Lanes、无 currency identifier；定位为证券标准非支付标准 |
| **Auditability / Privacy** | 中 | 全链上可审计；ONCHAINID 隐私取决于实现层（Tokeny 参考实现采用 hash-only 模式，但 ERC-735 协议层不阻止 PII 上链）；无 selective disclosure 或 ZKP 隐私子系统（vs Circle Arc） |

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-9

### item-11: 评估框架 7 维度分析

使用 WHI-177 建立的 7 维度评估框架对 ERC-3643 进行定位分析，明确其在合规代币标准谱系中的位置。

| 维度 | ERC-3643 定位 | 关键证据 |
|------|-------------|---------|
| **架构层级** | 应用层 Solidity | 6 个 Solidity 智能合约在 EVM 应用层协同执行 |
| **合规机制类型** | On-chain identity (claim-based) | ONCHAINID + Identity Registry + Compliance Module 三层 on-chain 验证 |
| **身份模型** | Self-sovereign (ONCHAINID) | 用户部署独立 ONCHAINID 合约，跨 token 复用 |
| **DeFi 可组合性** | ERC-20 compatible（有限制） | 完整 ERC-20 接口但 transfer 可能 revert；与 $50B+ DeFi TVL 生态可交互但受限 |
| **发行方控制力** | Agent role 完整控制 | freeze(partial)/forced transfer/recovery/pause/mint/burn/batch |
| **Gas 开销** | 高（多合约调用） | 标准路径 2-3 外部调用 + 嵌套子调用，估算 ERC-20 的 2-8x [inferred] |
| **规范成熟度** | Final ERC 2023 | 唯一 Final 合规代币标准；$32B+；180+ 司法管辖区；DTCC/Apex/Invesco/92+ 成员；DTC no-action 引用 |

**定位总结**：ERC-3643 是应用层合规范式的旗舰标准——身份系统最完整（ONCHAINID）、发行方控制力最强（Agent role）、规范成熟度最高（唯一 Final ERC）。代价是 Gas 开销高和 DeFi 可组合性受限。其设计优先级明确：合规确定性 > 性能 > 可组合性。

- **Priority**: high
- **Dependencies**: item-8, item-9, item-10

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| architecture_component | ERC-3643 各合约组件的名称、Solidity 接口、核心方法、存储结构、合约间调用关系 | item-2, item-3, item-4, item-5, item-6 |
| transfer_flow | 从 transfer 发起到执行/revert 的完整 4 步流程，标注每步的检查内容、涉及合约、Gas 消耗来源 | item-4, item-8 |
| identity_model | ONCHAINID 的 claim 结构、密钥管理、隐私设计、信任假设、与 wallet-level policy 的差异 | item-3, item-10 |
| agent_control | Agent role 的权限范围、操作接口、与 Owner 的权限分离、风险分析 | item-5, item-10 |
| gas_characteristic | Gas 开销来源分解、定性估算、batch 优化效果、场景适用性、与 precompile 方案的结构性差异 | item-8, item-11 |
| ecosystem_metric | Association 成员数/类别、资产代币化规模、司法管辖区覆盖、关键机构集成、安全审计、标准化进展 | item-7 |
| composability_constraint | DeFi 集成时的 silent revert 问题、受限持有者池、permissioned vs permissionless 张力 | item-9 |
| compliance_capability | 在 8 类 Taxonomy 中的具体实现方式、强弱评级、与其他标准的差异化对比 | item-10 |
| standard_maturity | Final ERC 状态、关键里程碑、治理结构、监管引用（G2 适用）、ISO 标准化 | item-1, item-7, item-11 |
| evidence_classification | 每个关键 claim 的证据类型：primary-source（EIP spec/code）/ secondary（官方文档/白皮书）/ inferred（行业分析推断） | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | ERC-3643 完整架构图：6 个核心合约（Token、Identity Registry、Identity Registry Storage、Trusted Issuers Registry、Claim Topics Registry、Modular Compliance）+ ONCHAINID 的组件关系、依赖方向和核心接口方法标注 | mermaid | item-2 |
| diag-2 | flow | Transfer 合规检查完整流程图：标准路径（sender balance/freeze check → receiver identity verification via `isVerified(receiver)` → Compliance Module `canTransfer` → execute/revert），标注每步的合约调用、检查内容和 pass/fail 路径。Module-specific sender identity 检查标注为可选扩展 | mermaid | item-4 |
| diag-3 | architecture | ONCHAINID 身份体系图：ERC-734 Key Management + ERC-735 Claim Holder 结构，claim 签发/验证流程，Trusted Issuer 信任链 | mermaid | item-3 |
| diag-4 | architecture | Agent 控制权限图：Owner 与 Agent 的权限分离，Agent 可执行操作（freeze/forced transfer/recovery/pause/mint/burn）及其影响范围 | mermaid | item-5 |
| diag-5 | comparison | ERC-3643 合规能力雷达图：8 类 Taxonomy 能力的强/中/弱评级可视化，标注与 B20/TIP-20/ERC-1400 的关键差异 | mermaid | item-10 |
| diag-6 | comparison | ERC-3643 在 7 维度评估框架中的定位图：按 WHI-177 维度展示 ERC-3643 的位置及与其他标准的对比 | mermaid | item-11 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_standard | ERC-3643 EIP 规范（eips.ethereum.org）、ERC-734/ERC-735 相关标准 | 2 |
| src-2 | reference_implementation | T-REX GitHub 仓库（TokenySolutions/T-REX 或 ERC-3643/ERC-3643）：Solidity 接口定义、核心合约代码 | 2 |
| src-3 | official_docs | Tokeny 官方文档（tokeny.com/erc3643）、ERC-3643 白皮书、ONCHAINID 文档 | 3 |
| src-4 | association | ERC-3643 Association 官网（erc3643.org）：成员列表、新闻公告、治理文档 | 2 |
| src-5 | regulatory_sources | DTC no-action letter PDF、SEC Commissioner Peirce 声明、SEC 主席 Atkins "Project Crypto" 演讲（G2 适用） | 3 |
| src-6 | institutional_evidence | DTCC ComposerX 集成、Apex Group/Tokeny 收购、Chainlink ACE 合作、Fasanara/ABN AMRO 部署案例 | 3 |
| src-7 | security_audit | Kaspersky、Hacken 安全审计报告或公告 | 1 |
| src-8 | industry_analysis | 第三方技术分析（Chainalysis ERC-3643 introduction、QuillAudits 解析、Taurus 标准对比、ChainScore Labs 对比） | 3 |
| src-9 | prior_research | WHI-177 合规能力 Taxonomy 和评估框架（compliance-token-standards/research-sections/compliance-token-landscape/final.md） | 1 |

## Required Output Tables

### 合规能力 Taxonomy 评估表

Deep draft 必须包含 ERC-3643 在 8 类合规能力 Taxonomy 下的详细评估表：

| 能力类别 | 评级 | 实现机制 | 关键接口/方法 | 优势 | 局限 | 与 B20/TIP-20 对比 |
|---------|------|---------|-------------|------|------|-------------------|
| Identity / KYC | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Transfer Policy | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Issuer Controls | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Sanctions / Blacklist | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Recovery | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Legal Document / Metadata | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Payment Reconciliation | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |
| Auditability / Privacy | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 | 待填充 |

### 7 维度评估表

Deep draft 必须包含 ERC-3643 在 7 维度评估框架下的详细分析：

| 维度 | 定位 | 证据 | 证据分类 |
|------|------|------|---------|
| 架构层级 | 待填充 | 待填充 | 待填充 |
| 合规机制类型 | 待填充 | 待填充 | 待填充 |
| 身份模型 | 待填充 | 待填充 | 待填充 |
| DeFi 可组合性 | 待填充 | 待填充 | 待填充 |
| 发行方控制力 | 待填充 | 待填充 | 待填充 |
| Gas 开销 | 待填充 | 待填充 | 待填充 |
| 规范成熟度 | 待填充 | 待填充 | 待填充 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-4 | **[Major]** 修正 transfer 流程 identity 检查方向：标准路径仅调用 `isVerified(receiver)`，不调用 `isVerified(sender)`。Sender 检查为 balance/freeze status。移除"双重 sender/receiver identity verification"框架；Compliance Module 内的 sender identity 约束标注为模块特定行为 | Revision Request (Orchestrator, round 1->2) — Review finding |
| 2 | modify_item | item-8 | **[Major]** 更正 gas 开销估算：标准路径 2-3 外部调用 + 嵌套子调用（非 4-6+），估算 2-8x ERC-20（非 3-10x）。Round 1 错误地将 sender identity 验证计入标准路径导致开销高估 | Revision Request — transfer flow correction cascade |
| 2 | modify_diagram | diag-2 | **[Major]** 更新 transfer 流程图描述：反映 sender balance/freeze → receiver isVerified → Compliance canTransfer 的标准路径；module-specific sender identity 标注为可选扩展 | Revision Request — transfer flow correction cascade |
| 2 | modify_item | item-10 | **[Major]** 更新 Identity/KYC 和 Auditability/Privacy taxonomy 评级说明：Identity/KYC 明确标准路径验证 receiver；Auditability/Privacy 区分 PII 保护的协议层与实现层 | Revision Request — transfer flow + PII correction cascade |
| 2 | modify_item | item-11 | **[Major]** 更新 Gas 开销维度：2-3 外部调用 + 嵌套子调用，2-8x ERC-20 | Revision Request — transfer flow correction cascade |
| 2 | modify_item | item-3 | **[Minor]** 降级 ONCHAINID PII 保护声明：ERC-735 `bytes data`/`string uri` 协议层不阻止 PII 上链；Tokeny 参考实现的 hash-only 模式是实现层最佳实践非协议保证；标注 [source required: Tokeny/ONCHAINID 文档] | Revision Request — PII claim downgrade |
| 2 | modify_item | item-1, item-7 | **[Minor]** 标记未验证的监管/采用声明为 [source required]：DTC no-action 日期、Atkins 演讲措辞、DTCC 加入日期、Chainlink ACE 日期、$32B+ 规模数据、180+ 司法管辖区等均标注待 deep-draft 阶段确认 | Revision Request — source-required tagging |
| 2 | modify_section | scope, Research Questions | 连锁更新：scope 中 transfer 流程描述修正为标准路径；Research Question 2 区分协议层和实现层 PII 保护；Research Question 3 修正为 sender/receiver 分离检查模型 | Revision Request — cascade from major + minor fixes |
