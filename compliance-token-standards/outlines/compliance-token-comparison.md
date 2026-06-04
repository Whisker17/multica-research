---
topic: "合规 Token 标准横向对比分析"
project_slug: "compliance-token-standards"
topic_slug: "compliance-token-comparison"
github_repo: "Whisker17/multica-research"
round: 2
status: candidate

artifact_paths:
  outline: "compliance-token-standards/outlines/compliance-token-comparison.md"
  draft: "compliance-token-standards/research-sections/compliance-token-comparison/drafts/round-{n}.md"
  final: "compliance-token-standards/research-sections/compliance-token-comparison/final.md"
  index: "compliance-token-standards/research-sections/_index.md"

scope: "四大标准横向对比（ERC-3643、ERC-1400、TIP-20、B20）；技术维度：架构层级 / 合规机制类型 / 身份模型 / Gas 效率 / DeFi 可组合性 / 发行方控制力 / 跨链能力 / 支付优化 / 升级与治理；规范成熟度维度：正式标准化状态 / 公开 Spec 可用性 / 网络激活状态 / 参考实现 / 真实采用 / 单一依赖风险"
audience: "区块链协议工程师、RWA/合规产品负责人、机构金融/BD 团队，以及 Research Review Agent。读者已阅读 M1 阶段各标准深度分析（WHI-177 landscape、WHI-178 ERC-3643、WHI-179 ERC-1400、WHI-180 TIP-20、WHI-181 B20），需要一份系统性横向对比产出，包含可直接引用的矩阵表、成熟度评估和关键 insight。"
expected_output: "compliance-token-standards/outlines/compliance-token-comparison.md 内含 9 个分析模块：(1) 对比框架说明, (2) 技术维度对比矩阵表, (3) 规范成熟度评估表, (4) 合规能力覆盖矩阵（引用 WHI-177 taxonomy）, (5) 架构层级对比图说明, (6) 关键 insight, (7) Trade-off 分析, (8) B20 证据口径边界说明, (9) 引用来源清单"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-04T14:00:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-04T11:10:00Z"

multica_issue_id: "c62bd179-f560-4ab7-b23e-9ffb153b88dd"
report_issue_id: "4c88c789-585a-4c50-965e-628d50cb8bde"
branch_name: "research/compliance-token-standards/compliance-token-comparison"
base_commit: "682b8251a6ad6fdb00bc2b7bbaca4ed5054c174d"
language: "中文"
research_depth: "standard"

source_sections:
  - path: "compliance-token-standards/research-sections/compliance-token-landscape/final.md"
    multica_issue_id: "f6a0c156-96f4-49df-b7c3-70109c308c5f"
    label: "WHI-177 landscape"
  - path: "compliance-token-standards/research-sections/erc3643-trex-analysis/final.md"
    multica_issue_id: "4036a12f-42fd-4ec1-a113-18df6c26c9a1"
    label: "WHI-178 ERC-3643"
  - path: "compliance-token-standards/research-sections/erc1400-series-analysis/final.md"
    multica_issue_id: "cf57ea5d-c512-47fc-8c8d-99b1f15a86e5"
    label: "WHI-179 ERC-1400"
  - path: "compliance-token-standards/research-sections/tempo-tip20-analysis/final.md"
    multica_issue_id: "586341f0-3ee8-4a89-8aa1-3535dd847d90"
    label: "WHI-180 TIP-20"
  - path: "compliant-token-standards/research-sections/base-b20-analysis/final.md"
    multica_issue_id: "bc5cf45c-2932-4631-b707-c75b2ff7ce6e"
    label: "WHI-181 B20"
---

# Research Outline: 合规 Token 标准横向对比分析

## Research Questions

1. 四大合规 Token 标准（ERC-3643、ERC-1400、B20、TIP-20）在 9 个技术维度上的具体差异如何量化？哪些差异是设计范式导致的结构性差异，哪些是实现选择的差异？
2. 四大标准在规范成熟度的 6 个子维度上各处于什么阶段？成熟度差异对"能否被机构跟进"产生什么实质影响？
3. WHI-177 定义的 8 类合规能力 Taxonomy 在四大标准中的覆盖情况如何？哪些能力类别存在结构性缺失（因设计范式限制而非功能遗漏），哪些是可补齐的功能缺口？
4. 应用层合规（ERC-3643/ERC-1400）与协议层合规（B20/TIP-20）在架构层级上的根本差异——合规检查在 EVM 执行栈中的位置——如何影响执行保证强度、Gas 成本、可组合性和升级灵活性？
5. 从 M1 阶段的四份深度分析中能提炼出哪些超越单一标准的 cross-cutting insight？例如：precompile 路线是否正在形成趋势？ERC-3643 与 B20/TIP-20 是竞争还是互补？ERC-1400 的设计遗产如何影响后续标准？
6. 四大标准各自的核心 trade-off 是什么？在不同部署场景（公链 DeFi、合规机构发行、支付优化、企业链）下，trade-off 的权重如何变化？

## B20 Evidence Constraint

> **B20 横向对比证据边界**：B20 横向对比只使用 `base/base@8e8767281d7c8768f6a0aed9124779cd4ed030ae` 与 `base/docs@bfff9ef27f2333ff57c3a62417f6c1f0174992f0` 可验证证据。B20Security / IB20Security 只能作为"本地分支观察/演进线索"单独标注，不得纳入 B20 主线成熟度评分、合规能力覆盖矩阵或 Mantle 策略判断的硬证据。`redeem`、`batchBurn`、`securityIdentifier` 如仅存在于本地分支，矩阵中应标为 "local branch only / not evidenced at pinned resource commit"。

## Items

### item-1: 对比框架说明

建立横向对比的方法论基础。明确：

**对比对象与边界**：四大标准为 ERC-3643（T-REX，应用层，Final ERC 2023）、ERC-1400（Security Token Standard umbrella，应用层，Draft 2018 从未 finalize）、B20（Base Beryl precompile，协议层，code-confirmed at `base/base@8e8767281d`）、TIP-20（Tempo precompile suite，协议层，production）。Circle Arc 在 WHI-177 landscape 中作为补充参考，不纳入本横向对比矩阵的主列。

**输入来源**：本对比基于 M1 阶段已完成的 5 份研究产出——WHI-177 landscape（合规能力 Taxonomy 和评估维度框架来源）、WHI-178 ERC-3643 深度分析、WHI-179 ERC-1400 深度分析、WHI-180 TIP-20 深度分析、WHI-181 B20 深度分析。所有 claim 须可追溯至源 section 的具体章节。

**对比维度体系**：两个独立矩阵——(a) 技术维度对比矩阵（9 维度，扩展自 WHI-177 的 7 维度，新增跨链能力、支付优化、升级与治理）；(b) 规范成熟度评估表（6 子维度）。加一个交叉矩阵——(c) 合规能力覆盖矩阵（WHI-177 Taxonomy 8 类 × 4 标准）。

**证据分类原则**：每个矩阵格需标注证据类型——primary-source（EIP 规范、官方文档）、code-confirmed（代码分析可验证）、code-inferred pending spec（B20 代码推断但公开规范未发布）、secondary（第三方分析）、docs-stated（TIP-20 官方文档声明但源码未同步验证，C1 约束）、inferred（跨源推理）。B20 相关 claim 须遵守 B20 Evidence Constraint。

**设计范式分类**：应用层合规（Solidity smart contract，EVM 解释执行，合规逻辑作为应用代码部署）vs 协议层合规（precompile/链原生，直接编译执行，合规逻辑内嵌于链协议层）。这是贯穿全部对比维度的分类轴。

- **Priority**: high
- **Dependencies**: none

### item-2: 技术维度对比矩阵表

构建 9 维度 × 4 标准的技术对比矩阵。每格须有可追溯证据或明确标注为判断/推论/code-inferred。

**9 个技术维度**（前 6 个沿用 WHI-177 框架，后 3 个为本对比新增；规范成熟度独立为 item-3 成熟度评估表，不重复）：

1. **架构层级**：应用层 (Solidity smart contract) / 协议层 (precompile) / 混合。标注 EVM 执行栈中的具体位置。
2. **合规机制类型**：on-chain identity (claim-based) / off-chain certificate + operator / policy registry（slot 结构差异）/ 无原生合规。
3. **身份模型**：self-sovereign (ONCHAINID, ERC-734/735) / operator-controlled (ERC-1400 _data 参数) / wallet-level policy (B20 PolicyRegistry 4-slot / TIP-403) / 无原生身份。
4. **Gas 效率**：per-transfer overhead 定性对比——ERC-3643 多合约调用（Identity Registry + Compliance Module，约 2-8× ERC-20）/ ERC-1400 partition 存储（嵌套 mapping + array push SSTORE）/ B20 precompile 原生执行（code-inferred）/ TIP-20 precompile（TIP-1034 节省最高 72% Gas）。
5. **DeFi 可组合性**：ERC-20 compatible（有限制，合规检查失败静默失败）/ ERC-20 compatible（partition 增加集成复杂度，_data 非标准化）/ Base 生态内（EVM L2 优势）/ TIP-20 生态内（独立 L1）。
6. **发行方控制力**：Agent role 粒度（ERC-3643）/ Controller "God Mode"（ERC-1644）/ RBAC 7-role（B20）/ RBAC 4-role（TIP-20）。
7. **跨链能力**（新增）：ERC-3643 任何 EVM 链可部署（ONCHAINID 跨链绑定需额外工作）/ ERC-1400 同上（但实现碎片化）/ B20 仅限 Base 链 / TIP-20 仅限 Tempo 链。
8. **支付优化**（新增）：无原生支付优化（ERC-3643/ERC-1400）/ B20 Stablecoin 变体（6 decimals, currency()）+ mintWithMemo/burnWithMemo（32-byte memo）/ TIP-20 Payment Lanes + memo + Fee AMM + StablecoinDEX + ISO 4217。
9. **升级与治理**（新增）：Solidity 合约可独立升级（proxy pattern / module swap）/ precompile 升级需链级硬分叉协调。

**矩阵格式要求**：

| 维度 | ERC-3643 | ERC-1400 | B20 | TIP-20 |
|------|----------|----------|-----|--------|
| 架构层级 | 待填充 [evidence_type] | 待填充 [evidence_type] | 待填充 [evidence_type] | 待填充 [evidence_type] |
| ... | ... | ... | ... | ... |

- **Priority**: high
- **Dependencies**: item-1

### item-3: 规范成熟度评估表

构建 6 子维度 × 4 标准的规范成熟度评估表。成熟度维度关注"一个标准是否已被充分定义、实现和验证，以至于机构能基于它进行生产级部署决策"。

**6 个成熟度子维度**：

1. **正式标准化状态**：EIP/ERC 流程阶段（Draft / Review / Last Call / Final）/ Chain-specific TIP 阶段 / 无正式标准化流程。
   - ERC-3643: Final ERC (2023) — Ethereum 社区唯一正式获批的合规代币标准
   - ERC-1400: Draft proposal (2018, EIP-1400) — 从未达到 Last Call 或 Final；子标准 ERC-1410/1594/1643/1644 均为 Draft
   - B20: 无 EIP/ERC 流程，Base 链专属 precompile，code-confirmed at pinned commit，公开 Beryl 规范尚未发布
   - TIP-20: Tempo L1 TIP 标准，production 部署

2. **公开 Spec 可用性**：是否有公开、版本化、完整的技术规范可供第三方独立实现？
   - ERC-3643: EIP-3643 全文 + T-REX GitHub 开源实现 + Tokeny 文档
   - ERC-1400: EIP-1400 系列 Draft（但 _data 参数和跨子标准集成未标准化）
   - B20: Beryl 公开规范尚未发布（pinned commit 代码可分析但不构成公开 spec）
   - TIP-20: docs.tempo.xyz 公开文档（C1 约束：源码未公开同步验证）

3. **网络激活状态**：标准是否已在生产网络上激活运行？
   - ERC-3643: 主网部署，$32B+ 资产代币化，180+ 司法管辖区
   - ERC-1400: 多链零散部署，Polymath 已迁移至 Polymesh
   - B20: Beryl 硬分叉前，未激活（code-inferred pending hardfork）
   - TIP-20: Tempo 主网运行，KlarnaUSD 已部署

4. **参考实现**：是否存在经过审计的参考实现？
   - ERC-3643: TokenySolutions/T-REX（多次审计）
   - ERC-1400: ConsenSys Universal Token（ConsenSys Diligence 审计，发现 default partition bypass 漏洞，PR #13 修复）；Polymath 实现自 2019 年起未公开维护
   - B20: Base 链核心 codebase（base/base），Rust precompile 实现
   - TIP-20: tempo-std SDK，Tempo 链核心

5. **真实采用**：生产级部署的规模和多样性。
   - ERC-3643: $32B+，DTCC、Fasanara Capital、ABN AMRO、Apex Group
   - ERC-1400: 早期部署后收缩，Polymath 迁移至 Polymesh 造成主要开发者流失
   - B20: 零生产部署（pre-hardfork）
   - TIP-20: KlarnaUSD 首个银行发行 token，AllUnity 集成

6. **单一依赖风险**：标准生态是否过度依赖单一组织/链/实现？
   - ERC-3643: Association 治理（DTCC/Apex/Invesco 为成员），但核心实现和生态围绕 Tokeny
   - ERC-1400: Polymath 撤离后缺少核心维护者
   - B20: 完全依赖 Base 团队和 Coinbase（Base 链专属）
   - TIP-20: 完全依赖 Tempo Labs（Tempo 链专属）

**评估量化方法**：每个子维度使用 5 级评分（5=完全成熟, 4=高, 3=中, 2=低, 1=不适用/缺失），并附评分依据和证据类型。总分仅供参考排序，不构成综合质量判断。

- **Priority**: high
- **Dependencies**: item-1

### item-4: 合规能力覆盖矩阵

基于 WHI-177 landscape 定义的 8 类合规能力 Taxonomy，构建 8 类 × 4 标准的覆盖矩阵。

**矩阵结构**：每格须标注——(a) 实现方式（具体合约/precompile/角色/接口），(b) 覆盖程度（Full / Partial / None / N/A），(c) 证据类型，(d) B20 相关须遵守 B20 Evidence Constraint。

**8 类合规能力**（引用 WHI-177 Taxonomy）：

1. **Identity / KYC**：
   - ERC-3643: ONCHAINID (ERC-734/735) claim-based 自主身份，Identity Registry 绑定 wallet -> ONCHAINID，isVerified() 检查，Trusted Issuers Registry 管理授权 KYC 提供者
   - ERC-1400: 无原生身份层，依赖 _data 参数注入 off-chain KYC 证书，operator model
   - B20: 无原生身份层，通过 PolicyRegistry 4-slot 的 ALLOWLIST/BLOCKLIST 间接实现 wallet-level 准入控制
   - TIP-20: 无原生身份层，通过 TIP-403 PolicyRegistry whitelist/blacklist + Chainalysis 集成 实现 wallet-level 准入控制

2. **Transfer Policy**：
   - ERC-3643: Compliance Module 可插拔规则（投资者上限、司法管辖限制、锁定期、认证状态）
   - ERC-1400: _data 参数 + operator 验证，partition 级别权限控制
   - B20: PolicyRegistry 4-slot（TransferSender/TransferReceiver/TransferExecutor/MintReceiver），ALLOWLIST/BLOCKLIST 策略，跨 token 共享
   - TIP-20: TIP-403 whitelist/blacklist + TIP-1015 compound policies（sender/recipient 不同授权规则）

3. **Issuer Controls**：
   - ERC-3643: Agent role — freeze/partial freeze/forced transfer/recovery/pause/batch ops
   - ERC-1400: ERC-1644 Controller "God Mode" — controllerTransfer/controllerRedeem；partition 级别 mint/burn
   - B20: RBAC 7-role — DefaultAdmin/Mint/Burn/BurnBlocked/Pause/Unpause/Metadata；batchMint（Asset 变体）；renounceLastAdmin 保护
   - TIP-20: RBAC 4-role — ISSUER/PAUSE/UNPAUSE/BURN_BLOCKED；burnAt（TIP-1006）

4. **Sanctions / Blacklist**：
   - ERC-3643: 通过 Identity Registry + Compliance Module 实现司法管辖限制；无专用 OFAC 集成
   - ERC-1400: 无原生制裁机制，依赖 off-chain operator 决策
   - B20: BLOCKLIST policy + BurnBlocked role（销毁违规地址余额）
   - TIP-20: blacklist policy + BURN_BLOCKED role + Chainalysis 集成

5. **Recovery**：
   - ERC-3643: 专用 recovery 机制（Agent 可执行 forced transfer 恢复丢失资产）
   - ERC-1400: ERC-1644 controllerTransfer 可用于恢复场景
   - B20: 无专用 recovery 接口（可通过 Admin 角色组合 burn + mint 间接实现）
   - TIP-20: 无专用 recovery 接口（类似 B20 的间接路径）

6. **Legal Document / Metadata**：
   - ERC-3643: 无原生文档管理（可通过 claim 扩展）
   - ERC-1400: ERC-1643 Document Management — bytes32 唯一名 + URI + hash + 时间戳
   - B20: Metadata role + announcement 机制 + extraMetadata（Asset 变体）；Stablecoin 变体有 currency() 返回 ISO 4217
   - TIP-20: ISO 4217 货币标识符 + 32-byte memo

7. **Payment Reconciliation**：
   - ERC-3643: 无原生支付对账机制
   - ERC-1400: 无原生支付对账机制
   - B20: mintWithMemo/burnWithMemo（32-byte memo，token 操作级支付引用）+ Stablecoin 变体 currency()（ISO 4217 货币标识符）。注：multiplier 属于 B20Asset 变体的 WAD-precision 缩放能力，不属于 Stablecoin 支付对账范畴。
   - TIP-20: 32-byte memo（支付引用/发票 ID）+ Payment Lanes（保留 55% 区块空间）+ Fee AMM + StablecoinDEX + ISO 4217 currency

8. **Auditability / Privacy**：
   - ERC-3643: 全链上可审计；ONCHAINID 不存储 PII（存储 hash/引用），提供 selective disclosure 能力
   - ERC-1400: 链上可审计（partition 级别）；无原生隐私设计
   - B20: 链上可审计（Base L2 继承 Ethereum 透明性）；ZK proving benchmark 数据存在
   - TIP-20: 链上可审计 + Tempo Zones 隐私保护（选择性披露）

**B20 Evidence Constraint 在矩阵中的应用**：B20 列中 `redeem`、`batchBurn`、`securityIdentifier` 等功能如仅存在于本地分支（B20Security/IB20Security），矩阵中标为 "local branch only / not evidenced at pinned resource commit"，不纳入覆盖评级。

- **Priority**: high
- **Dependencies**: item-1

### item-5: 架构层级对比图说明

设计应用层 vs 协议层合规的架构对比可视化，说明合规检查在 EVM 执行栈中的位置差异及其技术后果。

**核心图示内容**：

(a) **EVM 执行栈分层图**：展示从 Transaction 发起 → EVM 解释器 → Opcode 执行 → Precompile 调用 的完整路径，标注应用层合规（ERC-3643/ERC-1400 的 Solidity 合约在 EVM 解释层执行 identity/compliance 检查）和协议层合规（B20/TIP-20 的 precompile 在 Native Execution 层直接执行 policy 检查）的位置差异。

(b) **Transfer 路径对比**：四大标准的 transfer 调用流程并列对比——
- ERC-3643: `transfer()` → Token Contract → Identity Registry.isVerified(receiver) → Trusted Issuers 验证 claims → Compliance Module 检查规则 → 执行/拒绝
- ERC-1400: `transferByPartition()` → Partition 检查 → _data 参数验证（off-chain certificate）→ Operator 检查 → 执行/拒绝
- B20: `transfer()` → B20 precompile → PolicyRegistry 4-slot 检查（TransferSender → TransferReceiver → TransferExecutor）→ 执行/拒绝
- TIP-20: `transfer()` → TIP-20 precompile → TIP-403 policy 检查 → 执行/拒绝

(c) **Gas 成本路径对比**：标注每种 transfer 路径中各阶段的 Gas 消耗特征——EVM CALL opcode 跨合约开销（ERC-3643/ERC-1400）vs precompile 单次直接调用（B20/TIP-20）。

(d) **Factory/Registry 架构对比**：四大标准的 token 创建和注册架构——ERC-3643 标准合约部署 vs ERC-1400 标准合约部署 vs B20Factory precompile（地址派生: 0xb2 前缀 + creator + salt keccak256）vs TIP20Factory precompile（地址: 0x20c0...00 + token ID）。

- **Priority**: high
- **Dependencies**: item-2

### item-6: 关键 Insight

从 M1 阶段各标准深度分析和横向对比矩阵中提炼 cross-cutting insight。不是重复前序 items 的结论，而是提炼超越单一标准的模式判断。

**要求提炼的 insight 方向**（每个 insight 须有矩阵证据支撑）：

(a) **合规在哪一层实现——趋势判断**：新兴链/L2（Base Beryl、Tempo）选择协议层合规的原因分析。从 item-2 矩阵中提取架构层级、Gas 效率、升级与治理三个维度的对比证据，判断 precompile 路线是否正在形成行业趋势，以及这一趋势的边界条件。

(b) **Precompile 路线趋势**：B20 和 TIP-20 的设计选择在多大程度上代表"新建链默认选择协议层合规"？从 item-3 成熟度矩阵中提取网络激活状态和真实采用数据，判断这一趋势处于 early signal 还是 established pattern。

(c) **ERC-3643 vs B20/TIP-20：竞争还是互补？**：ERC-3643 的跨链可移植性优势 vs B20/TIP-20 的性能和一致性优势。是否存在"ERC-3643 作为跨链合规身份层 + B20/TIP-20 作为链内高效执行层"的互补路径？从 item-4 合规能力覆盖矩阵中提取 Identity/KYC 维度和 Transfer Policy 维度的对比证据。

(d) **成熟度对"能否跟进"的影响**：机构在评估合规 Token 标准时，哪些成熟度子维度是阻断性的（e.g., 无公开 spec = 无法独立审计 = 机构无法采用），哪些是渐进性的？从 item-3 提取各标准的成熟度瓶颈。

(e) **ERC-1400 的设计遗产**：ERC-1400 虽未 finalize，但其 partition/tranche 概念如何影响后续标准（ERC-7518 DyCIST、B20 Asset 变体的 multiplier 机制）？从 item-2 和 item-4 矩阵中提取具体继承关系。

(f) **TIP-20 支付优化的独特性**：Payment Lanes / Fee AMM / StablecoinDEX / memo 的组合在四大标准中无对应。这是 TIP-20 的差异化定位还是其他标准的功能缺口？从 item-2 支付优化维度和 item-4 Payment Reconciliation 维度提取证据。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4, item-5

### item-7: Trade-off 分析

系统分析每个标准的核心 trade-off，以及不同部署场景下 trade-off 权重的变化。

**标准级 Trade-off**：

(a) **ERC-3643**：跨链可移植性 + 成熟生态 + 机构信任 <-> Gas 开销高 + DeFi 可组合性受限（合规检查静默失败）+ 升级灵活但碎片化风险
(b) **ERC-1400**：partition 模型强大的资本结构建模能力 <-> Draft 状态从未 finalize + _data 非标准化 + 核心维护者流失 + ERC-777 依赖已 deprecated
(c) **B20**：协议层一致性 + Base/Ethereum 生态继承 + RBAC 粒度精细 <-> 仅限 Base 链 + Beryl 规范未公开 + 零生产部署 + 单一依赖（Coinbase/Base）
(d) **TIP-20**：支付优化全栈（Payment Lanes + Fee AMM + memo + StablecoinDEX）+ precompile 低 Gas <-> 仅限 Tempo 链 + 源码未公开（C1 约束）+ 生态早期 + 单一依赖（Tempo Labs）

**场景化权重分析**（矩阵格式）：

| 场景 | 最重要维度 | ERC-3643 适配度 | ERC-1400 适配度 | B20 适配度 | TIP-20 适配度 |
|------|-----------|----------------|----------------|-----------|--------------|
| 公链 DeFi 代币化证券 | 跨链 + DeFi 可组合 | 待分析 | 待分析 | 待分析 | 待分析 |
| 合规机构发行（STO） | 成熟度 + 监管确定性 | 待分析 | 待分析 | 待分析 | 待分析 |
| 支付稳定币 | 支付优化 + Gas 效率 | 待分析 | 待分析 | 待分析 | 待分析 |
| 企业链/专用链部署 | 发行方控制 + 升级治理 | 待分析 | 待分析 | 待分析 | 待分析 |

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4, item-6

### item-8: B20 证据口径边界说明

独立说明 B20 在本横向对比中的证据口径限制，确保读者理解对比矩阵中 B20 列的 claim 强度和适用范围。

**说明内容**：

(a) **Pinned resource commit 范围**：B20 的所有横向对比 claim 基于 `base/base@8e8767281d7c8768f6a0aed9124779cd4ed030ae`（代码分析）和 `base/docs@bfff9ef27f2333ff57c3a62417f6c1f0174992f0`（文档分析）。超出此范围的信息不纳入矩阵评分。

(b) **B20Security/IB20Security 本地分支观察**：本地分支 a052beb 存在第三变体 Security (=2)，含 `redeem`、`batchBurn`、`securityIdentifier` 等功能。这些功能归类为"本地分支观察/演进线索"，在矩阵中标注为 "local branch only / not evidenced at pinned resource commit"，不纳入 B20 主线成熟度评分或合规能力覆盖评级。

(c) **Beryl 规范状态**：截至本研究，公开 Beryl hardfork 技术规范尚未发布。B20 的架构和功能分析基于代码推断（code-inferred），最终行为须以正式规范为准。矩阵中标注 "code-inferred pending Beryl spec"。

(d) **证据层级区分**：B20 claim 使用 code-confirmed（pinned commit 代码直接验证）和 code-inferred pending spec（代码推断但规范未发布）两个证据等级，与 ERC-3643/ERC-1400 的 primary-source（EIP 规范）和 TIP-20 的 docs-stated（C1 约束）形成证据强度的梯度对比。

- **Priority**: high
- **Dependencies**: none

### item-9: 引用来源清单

汇编本横向对比所有引用来源，按来源类型分组。要求每条来源可追溯至具体 item 和矩阵格。

**来源分组**：
- M1 阶段源 section（5 份 final.md 路径和 multica_issue_id）
- EIP/ERC 规范（EIP-3643、EIP-1400/1410/1594/1643/1644）
- 代码仓库（base/base@pinned commit、TokenySolutions/T-REX、ConsenSys UniversalToken）
- 官方文档（Tempo docs、Base docs@pinned commit）
- 监管文件（DTC no-action letter、GENIUS Act、MiCA、DLT Pilot Regime）
- 市场数据（rwa.xyz，标注查询日期和口径）
- 第三方分析（Tokeny 对比、Chainalysis introduction、Oraclizer 分析）

- **Priority**: medium
- **Dependencies**: item-2, item-3, item-4

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| comparison_dimension | 对比维度名称、定义、评价标准、在矩阵中的列位置 | item-1, item-2, item-3 |
| matrix_cell | 矩阵格内容——标准名、维度名、评价内容、证据类型、证据来源（源 section 章节引用） | item-2, item-3, item-4 |
| maturity_score | 成熟度评分（1-5）、评分依据、证据类型；B20 相关须标注 code-inferred | item-3 |
| capability_coverage | 合规能力覆盖评级（Full/Partial/None/N/A）、实现方式、证据类型；B20 须遵守 Evidence Constraint | item-4 |
| architecture_layer | EVM 执行栈位置、transfer 路径步骤、Gas 消耗特征、合规检查嵌入位置 | item-5 |
| cross_cutting_insight | Insight 陈述、支撑证据（矩阵格引用）、趋势判断强度（established/emerging/speculative）、边界条件 | item-6 |
| trade_off | Trade-off 对（advantage <-> cost）、场景敏感性分析、权重变化条件 | item-7 |
| evidence_boundary | B20 claim 的证据类型、pinned commit 范围、本地分支观察标注、规范未发布说明 | item-8 |
| source_reference | 来源类型、完整引用、对应 item/矩阵格、访问日期（市场数据） | item-9 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | 技术维度对比矩阵可视化：9 维度 × 4 标准的 heatmap 或 radar chart，标注各标准在每个维度的相对位置 | mermaid | item-2 |
| diag-2 | assessment | 规范成熟度评估雷达图：6 子维度 × 4 标准的 radar chart，直观展示各标准的成熟度 profile | mermaid | item-3 |
| diag-3 | matrix | 合规能力覆盖矩阵热力图：8 类 × 4 标准，覆盖程度用颜色编码（Full=绿, Partial=黄, None=红, N/A=灰） | mermaid | item-4 |
| diag-4 | architecture | EVM 执行栈分层对比图：Transaction → EVM Interpreter → Opcode → Precompile 路径，标注应用层和协议层合规的检查位置 | mermaid | item-5 |
| diag-5 | flowchart | 四大标准 Transfer 路径并列流程图：从 transfer() 发起到执行/拒绝的完整路径对比 | mermaid | item-5 |
| diag-6 | comparison | 场景适配度矩阵图：4 场景 × 4 标准的适配度评估可视化 | mermaid | item-7 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | m1_source_section | WHI-177 landscape final.md — 合规能力 Taxonomy (8 类)、评估维度框架 (7 维度)、设计范式分类、监管环境综述 | 1 |
| src-2 | m1_source_section | WHI-178 ERC-3643 final.md — 架构组件、transfer 流程、Gas 特征、DeFi 可组合性、Agent role、标准成熟度 | 1 |
| src-3 | m1_source_section | WHI-179 ERC-1400 final.md — 子标准模块、partition/tranche 架构、_data 非标准化、ConsenSys 审计、标准状态 | 1 |
| src-4 | m1_source_section | WHI-180 TIP-20 final.md — precompile 架构、TIP-403、RBAC、Payment Lanes、Fee AMM、StablecoinDEX、生态 | 1 |
| src-5 | m1_source_section | WHI-181 B20 final.md — B20Factory、双变体、PolicyRegistry 4-slot、RBAC 7-role、ActivationRegistry、代码确认范围 | 1 |
| src-6 | official_standard | EIP-3643 全文、EIP-1400/1410/1594/1643/1644 Draft 全文 | 2 |
| src-7 | code_analysis | base/base@8e8767281d（B20 precompile 代码）——仅用于验证 WHI-181 分析中的代码确认 claim | 1 |
| src-8 | official_docs | Tempo docs (docs.tempo.xyz) — TIP-20 spec、TIP-403、扩展 TIP | 1 |
| src-9 | regulatory_sources | DTC no-action letter PDF (SEC)、Commissioner Peirce 声明——仅用于验证 ERC-3643 成熟度评分中的监管维度 | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-2 | Remove `规范成熟度` row (was row 7) from technical matrix — maturity is owned by item-3 standalone table; renumber remaining rows 7-9 (跨链能力/支付优化/升级与治理) to restore exact 9-dimension count | Review Verdict R1 (91624030) — structural inconsistency |
| 2 | modify_item | item-2 row 8 (支付优化) | Add B20 `mintWithMemo`/`burnWithMemo` (32-byte memo) to B20 payment optimization description | Aligned with item-4 fix below |
| 2 | modify_item | item-4 Payment Reconciliation B20 cell | Remove `multiplier` (B20Asset WAD-precision scaling, not B20Stablecoin payment); replace with `mintWithMemo`/`burnWithMemo` (32-byte memo on token ops) + `currency()` as correct B20 payment reconciliation evidence per WHI-181 pinned commit | Review Verdict R1 (91624030) — evidence boundary violation |
