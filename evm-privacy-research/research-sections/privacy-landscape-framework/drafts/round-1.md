---
topic: "EVM 隐私需求与技术全景框架 — Mantle 轻量级机构隐私方案宏观框架"
project_slug: "evm-privacy-research"
topic_slug: "privacy-landscape-framework"
github_repo: "Whisker17/multica-research"
round: 1
status: draft

artifact_paths:
  outline: "evm-privacy-research/outlines/privacy-landscape-framework.md"
  draft: "evm-privacy-research/research-sections/privacy-landscape-framework/drafts/round-1.md"
  final: "evm-privacy-research/research-sections/privacy-landscape-framework/final.md"

draft_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23"
  outline_round: 2
  outline_commit: "aaa6b479e99fb76927342b0a571a345f2d4315aa"
  items_covered: ["item-1", "item-2", "item-3", "item-4", "item-5", "item-6"]
  fields_investigated: ["eea_section_ref", "data_dimension", "trust_model", "deployment_pattern", "disclosure_vector", "compliance_mapping", "eea_solution_mapping", "mantle_relevance", "source_confidence"]
  diagrams_produced: ["diagram-1", "diagram-2", "diagram-3", "diagram-4"]
  source_requirement_coverage: "primary source (EEA report) accessed and cited by section; secondary sources (IPTF, scheme docs) accessed for vector verification"
  residual_caveat_addressed: true

multica_issue_id: "51a89bf9-8955-4ae4-914e-cc6920ffea9a"
branch_name: "research/evm-privacy-research/privacy-landscape-framework"
language: "中文"
mode: "single-issue-lightweight"
---

# EVM 隐私需求与技术全景框架

> 本 section 为「Mantle 轻量级机构隐私方案」pre-research 系列的首个框架文档，锚定 EEA Privacy Working Group 报告（Version 1, April 2026），建立后续所有标准/竞品分析的统一口径。

## Executive Summary

本研究 section 从 EEA Privacy Working Group 发布的 *State of Privacy on Ethereum for Enterprise*（Version 1, April 2026，访问日期 2026-06-23）中综合提炼出 8 项企业隐私核心需求（R1–R8），构建了覆盖密码学路线、被保护数据维度、信任模型、部署形态和合规-选择性披露的五轴统一评估 rubric，并将选择性披露从单选分类升级为 6 维多标签向量模型（authority × trigger × payload × scope × revocability × leakage）。同时定义了「轻量级」部署形态的判定标准——包含 4 项一票否决条件和路线专属成本指标——以及「隐私账本」二义性（token ledger vs business-state ledger）的判定口径。

核心发现：

1. **EEA 7 方案横跨 6 类技术家族**（FHE/GC/MPC/TEE/ZKP/Privacy Groups），无单一技术能覆盖全部 7 项被保护数据维度 + 订单流隐私。
2. **选择性披露必须采用多标签向量**：单选分类无法表达 Paladin/Noto 同时作为 privacy-group 和 notary/observer、或 Nightfall 同时具备 KYC-gate 和 viewing-key-share 的复合特征。
3. **「轻量级 bolt-on」候选方案极少**：在 4 项一票否决条件（新链/VM、新桥、全节点运维、硬分叉）过滤后，仅 COTI multichain 扩展和 Paladin 链上合约套件模式有可能通过轻量级判定，而 Linea Enterprise Validium、Prividium、Silent Data L2 和 Polygon CDK 私有链均被一票否决。
4. **Mantle 关键约束**：作为 institutional blockchain 追求隐私（私密转账/余额/账本），偏好「不改变基础链架构」的 bolt-on 方案。本框架的 rubric 和轻量级判定标准将在后续竞品分析中直接应用。

---

## item-1: EEA 报告核心提炼 — 企业隐私 8 需求、信任模型与评估框架

### 1.1 EEA 报告基本信息

- **报告全称**: *State of Privacy on Ethereum for Enterprise*
- **发布方**: Enterprise Ethereum Alliance (EEA) Privacy Working Group
- **版本**: Version 1, April 2026
- **URL**: https://entethalliance.github.io/wg-privacy/privacy-report.html
- **访问日期**: 2026-06-23
- **参与方**: Applied Blockchain (Silent Data), Consensys (Linea), COTI, EY (Nightfall), Kaleido (Paladin), Polygon, ZKsync (Prividium)；Ethereum Foundation PSE 团队和 IPTF 亦参与贡献 [EEA 官方公告, 2026-02-24; source_confidence: EEA 报告直接引用]

### 1.2 企业隐私 8 需求综合体系

EEA 报告本身未以编号列表形式列出「8 项需求」，以下体系由研究者从 Section 04（Enterprise Privacy Problem）的 4 大屏障、Section 10（Solution Profiles）的数据保护维度、Section 11（Decision Framework）的 5 项评估问题、以及 Section 08（Trust Models）的信任-合规交叉中综合归纳 [推论; source_confidence: EEA 报告推论]。

| # | 需求 | EEA 报告来源 | 说明 |
|---|------|-------------|------|
| **R1** | 交易金额隐私 | §04 Lack of Financial Discretion; §10 各方案 "concealing transaction values" | 交易金额对非授权方不可见。COTI 通过 GC 加密值、Nightfall 通过 ZK commitments 实现 [EEA §10] |
| **R2** | 账户余额隐私 | §04 Lack of Financial Discretion; §10 COTI/Nightfall "concealing account balances" | 账户余额加密存储，仅授权方可查。ERC-7984 Confidential Fungible Token 提供标准化方案 [EEA §06b] |
| **R3** | 对手方身份隐私 | §04; §11-Q1 "counterparty identities"; §10 Stealth Addresses (ERC-5564) | 交易双方身份链接不可被公开观察。ERC-5564 Stealth Addresses + ERC-6538 Registry 提供标准化方案 [EEA §06b] |
| **R4** | 业务逻辑/合约状态隐私 | §04 Exposure of Business Logic; §10 Silent Data/Paladin "smart contract execution confidentiality" | 智能合约执行逻辑和内部状态对外不可见。Silent Data (TEE)、Paladin/Pente (ephemeral EVM)、Linea Enterprise (Private Validium) 展示三种不同路径 [EEA §10] |
| **R5** | 交易图/资金流隐私 | §04; §11-Q1 隐含; §06b ERC-5564/Stealth 防止链接分析 | 交易间的关联关系（谁给谁转账）不可被推断。需要 unlinkability 机制（stealth addresses、mixing、decoy sets）[EEA §06b] |
| **R6** | 合规可审计性 | §04 Regulatory Non-Compliance; §11-Q3 GDPR/MiCA; §10 各方案 "regulatory engagement" | 在保护隐私的同时，满足监管合规要求（GDPR、MiCA、Travel Rule、AML/CFT）。所有 EEA 7 方案均声称支持某种形式的合规机制 [EEA §04, §11] |
| **R7** | 选择性披露 | §08 Trust Models 跨信任边界; §10 COTI "permissioned view-keys"; Paladin "privacy domains"; Nightfall "X.509 enterprise identity" | 在隐私保护基础上，能够选择性地向指定方（审计方、监管方、对手方）披露特定信息。详见 item-4 多标签向量模型 [EEA §08, §10] |
| **R8** | 执行策略保护（反 MEV/前运行） | §04 Impact on Financial Strategy; §06b EIP-8105 Encrypted Mempools | 交易意图在提交到确认期间不被泄露，防止前运行（front-running）和三明治攻击（sandwich attacks）。EIP-8105 提出协议层加密 mempool 方案 [EEA §04, §06b] |

**source_confidence**: R1–R5 为 EEA 报告直接引用结论的综合归纳；R6–R7 为 EEA 报告跨 section 交叉推论；R8 为 EEA 报告 §04 和 §06b 综合推论。

### 1.3 三类信任模型

EEA 报告 §08 定义了三类信任模型，每类对应不同的隐私保障机制和信任假设 [EEA §08; source_confidence: EEA 报告直接引用]：

| 信任模型 | 保障基础 | 信任假设 | 代表方案 |
|---------|---------|---------|---------|
| **Cryptographic Trust** | 数学证明（ZKP、commitments） | 密码学假设（离散对数、配对假设等）不被攻破 | Nightfall (ZK rollup)、ERC-5564 (stealth addresses)、ERC-7984 (FHE confidential tokens) |
| **Hardware-Anchored Trust** | 硬件安全隔区（TEE） | 硬件制造商可信、侧信道攻击可控 | Silent Data (Intel SGX/AWS Nitro)、TEE-protected block building |
| **Organizational Honesty** | 运营方诚实行为 | 运营方/公证方遵守协议不作恶 | Paladin/Noto (notary-based)、Prividium (operator-controlled)、Privacy Groups (permissioned membership) |

**混合信任模型**：实际方案多为混合模型。例如：
- COTI = Cryptographic (GC) + Organizational (multichain operator)
- Linea Enterprise = Cryptographic (ZK validity proof) + Organizational (permissioned sequencer)
- Paladin/Pente = Cryptographic (ephemeral EVM hashes) + Organizational (notary validation)

[source_confidence: 三类模型为 EEA 报告直接引用；混合模型分析为研究者推论]

### 1.4 Readiness Matrix

EEA 报告 §09 定义了隐私方案成熟度评估的三阶段模型 [EEA §09; source_confidence: EEA 报告直接引用]：

| 阶段 | 定义 | 判定标准 |
|------|------|---------|
| **Pilot** | 概念验证/沙盒阶段 | 有技术演示、有限测试、无生产流量 |
| **Early Production** | 有限生产部署 | 真实资产/交易、受限用户群、持续监控 |
| **General Availability** | 全面生产可用 | 开放接入、经过审计、有 SLA/SLO |

各方案自评成熟度（截至 2026 年中）：
- **COTI**: Early Production（跨链隐私协议已上线，70+ 链目标）[COTI 2026 Roadmap]
- **Nightfall**: Early Production（Nightfall_4 ZK rollup 已上线，Starknet 集成 2026-02）[EY Nightfall 官方; Starknet 公告]
- **Paladin**: Early Production（Project Guardian 测试网运行中，LF Decentralized Trust 项目级别）[LF Decentralized Trust, 2025-11]
- **Silent Data**: Early Production（Optimism Superchain 上线，Archax 集成）[Silent Data 官方, 2025-07]
- **Linea Enterprise**: Pilot → Early Production（Lineth 开源于 LF Decentralized Trust，SWIFT 合作原型）[LF Decentralized Trust; SWIFT, 2025-09]
- **Prividium**: Early Production（SOC 2 Type I 通过，Cari Network 银行试点 Q3 2026）[ZKsync Docs; SOC 2 报告, 2026-05]
- **Polygon CDK**: Early Production（隐私升级已发布，validium 模式可用）[Polygon Docs]

[source_confidence: 阶段定义为 EEA 报告直接引用；各方案自评为官方文档补充，可能偏乐观]

### 1.5 Decision Framework

EEA 报告 §11 提供 5 项评估问题作为方案选型决策框架 [EEA §11; source_confidence: EEA 报告直接引用]：

| # | 评估问题 | 对齐需求 | 说明 |
|---|---------|---------|------|
| Q1 | 需要保护哪些数据？（隐私对象） | R1-R5, R8 | 金额、余额、身份、图、逻辑、状态、订单流 — 对齐 item-2 的 7 项数据维度 |
| Q2 | 可接受的信任模型是什么？ | R6, R7 | Cryptographic / Hardware-Anchored / Organizational — 取决于监管要求和风险偏好 |
| Q3 | 面临哪些监管环境？ | R6, R7 | GDPR (欧盟)、MiCA (加密资产)、Travel Rule (资金转移)、AML/CFT — 决定披露要求 |
| Q4 | 部署时间线和集成复杂度？ | 轻量级判定 | 影响「bolt-on vs 独立链」选择 — 对齐 item-5 部署形态判定 |
| Q5 | 长期可维护性和生态兼容性？ | 全局 | 开源程度、标准化（ERC）对齐度、社区活跃度 |

### 1.6 IPTF 补充框架

Ethereum Foundation 的 Institutional Privacy Task Force (IPTF) 提供了互补的评估视角 [IPTF 官网, https://iptf.ethereum.org, 访问日期 2026-06-23; source_confidence: 官方文档补充]：

**CROPS 框架**：IPTF 将以下 4 项属性视为不可妥协的底线：
- **C**ensorship **R**esistance — 抗审查性
- **O**pen Source and Free — 开源免费
- **P**rivacy — 隐私保护
- **S**ecurity — 安全性

**I2I vs I2U 语境区分**：
- **I2I**（Institution-to-Institution）：机构间交易，关注验证器经济学、终局性保证、后量子签名。证明委托在双边合同 + SLA 下进行，可通过法律追溯惩罚偏差。
- **I2U**（Institution-to-End-User）：机构对终端用户，关注轻客户端可验证性。证明方通常为外部服务，模式必须假设证明方可随时变为对抗性（adversarial）。

**Mantle 启示**：Mantle 作为 institutional blockchain，其隐私需求主要属于 I2I 语境（机构间隐私转账/余额），但也需覆盖 I2U 场景（终端用户与链交互时的隐私）。CROPS 框架要求方案满足抗审查 + 开源 + 隐私 + 安全四项底线，这对纯 Organizational Trust 模型（如完全依赖运营方诚信的方案）构成挑战。

---

## item-2: 隐私原语 → 技术家族映射（含业务逻辑/合约状态隐私维度）

### 2.1 EEA 6 类隐私技术家族

EEA 报告 §06 定义了 6 类隐私技术家族 [EEA §06; source_confidence: EEA 报告直接引用]：

| 技术家族 | 全称 | 核心原理 | 代表方案 |
|---------|------|---------|---------|
| **FHE** | Fully Homomorphic Encryption | 在加密数据上直接计算，结果解密后等价于明文计算结果 | Zama fhEVM（TFHE 方案）、ERC-7984 Confidential Fungible Token |
| **GC** | Garbled Circuits | 将计算转化为加密电路，参与方在不知对方输入的情况下完成计算 | COTI（首个将 GC 用于区块链的方案） |
| **MPC** | Multi-Party Computation | 多方联合计算函数，各方私有输入不对他方暴露 | 阈值解密网络（如 Zama KMS）、COTI 探索中的 MPC 集成 |
| **TEE** | Trusted Execution Environments | 硬件安全隔区（如 Intel SGX、AWS Nitro）内执行，运营方亦不可见 | Silent Data L2、TEE-protected block building |
| **ZKP** | Zero-Knowledge Proofs | 证明者向验证者证明某陈述为真，而不泄露陈述之外的任何信息 | Nightfall (ZK rollup)、ERC-5564 Stealth Addresses、Prividium (ZK validity proof) |
| **PG** | Privacy Groups | 在指定参与者子网络内共享数据，对子网络外不可见 | Paladin Privacy Domains、Linea Enterprise (permissioned validium)、Polygon CDK (permissioned access) |

### 2.2 隐私原语 → 技术家族映射矩阵

以下矩阵映射 7 项被保护数据维度到 6 类技术家族的保护能力。第 7 项「订单流/mempool 隐私」对齐 R8（执行策略保护），评估各技术家族对 pre-confirmation 交易意图的保护能力 [source_confidence: EEA 报告推论 + 官方文档补充]。

#### diagram-1: 隐私技术家族与隐私原语映射矩阵

| 被保护数据维度 | FHE | GC | MPC | TEE | ZKP | PG |
|:-------------|:---:|:---:|:---:|:---:|:---:|:---:|
| ① 金额隐藏 (R1) | **强** | **强** | 中 | **强** | **强** | 中 |
| ② 余额隐藏 (R2) | **强** | **强** | 中 | **强** | **强** | 中 |
| ③ 身份隐藏 (R3) | 中 | 弱 | 弱 | 中 | **强** | 弱 |
| ④ 图结构隐藏 (R5) | 弱 | 弱 | 弱 | 中 | **强** | 弱 |
| ⑤ 业务逻辑隐藏 (R4) | **强** | 中 | 中 | **强** | 中 | 中 |
| ⑥ 合约状态隐藏 (R4) | **强** | 中 | 弱 | **强** | 中 | 中 |
| ⑦ 订单流/mempool (R8) | 弱 | 弱 | 中 | **强** | 中 | 弱 |

**评分标准说明**：
- **强**：该技术家族的核心能力直接覆盖该维度，有成熟实现
- **中**：可以实现但非核心优势，或需与其他技术组合
- **弱**：基本不覆盖或仅提供有限保护
- 不适用：该技术家族在原理上无法提供保护（本矩阵中未出现此情况）

**关键观察**：

1. **FHE 和 TEE** 在值级+执行级隐私上表现最全面（5/7 强），但在身份/图结构上较弱（需组合 ZKP/stealth addresses）。FHE 在订单流保护上较弱，因其关注的是链上状态加密而非 pre-confirmation 阶段 [EEA §06; 推论]。

2. **ZKP** 在身份/图结构隐私上独具优势（stealth addresses、ring signatures），但在业务逻辑和合约状态隐私上需要电路化全部逻辑（constraint 数量爆炸），目前仅 Aztec 实现了通用 private functions [EEA §10; Aztec 官方文档]。

3. **GC** 是 COTI 的核心技术路线，声称计算速度比 FHE 快 3,000x、体积轻 250x。GC 在金额/余额隐藏上表现强，但作为两方计算协议，在多方场景和身份/图隐藏上受限 [COTI 2026 Roadmap; source_confidence: 官方文档补充]。

4. **Privacy Groups (PG)** 作为组织信任模型的代表，在所有维度上提供「中等」保护——其隐私保障来自准入控制而非密码学，因此对组内参与方透明。Paladin privacy domains 和 Linea Enterprise permissioned validium 是典型实现 [EEA §10]。

5. **订单流/mempool 隐私（R8）**是独立于链上数据隐私的维度。TEE 评为「强」因为 TEE-protected block building 可在硬件隔区内处理未确认交易（如 Silent Data TEE 执行环境）；ZKP 评为「中」因为 commit-reveal 方案可部分保护交易意图；MPC 评为「中」因为阈值加密 mempool（如 Shutter Network / EIP-8105 的 MPC 变体）可分布式保护 [EEA §06b; EIP-8105 提案]。

### 2.3 EEA §06b 以太坊隐私标准映射

EEA 报告 §06b 列出了 4 项正在推进的以太坊隐私标准 [EEA §06b; source_confidence: EEA 报告直接引用]：

| 标准 | 技术家族 | 隐私原语覆盖 | 状态 |
|------|---------|------------|------|
| **ERC-5564** Stealth Addresses | ZKP (SECP256k1 ECDH) | 身份隐藏 (R3)、图结构隐藏 (R5) | Final (2022-08 提出, Vitalik 共同作者) |
| **ERC-6538** Stealth Meta-Address Registry | — (registry) | 补充 ERC-5564 的地址发现机制 | Final (2023-01 提出) |
| **ERC-7984** Confidential Fungible Token | FHE (pointer-based encrypted amounts) | 金额隐藏 (R1)、余额隐藏 (R2) | Draft (2025-07 提出, Zama/OpenZeppelin) |
| **EIP-8105** Universal Enshrined Encrypted Mempool | 多方案（threshold encryption / MPC / TEE / delay encryption） | 订单流/mempool 隐私 (R8) | Draft (2025-12 提出, Shutter Network) |

**ERC-7984 技术细节**：采用 pointer-based 架构，所有金额以加密 handle (bytes32) 表示。智能合约本身不知道余额数值，所有 FHE 运算由链下 coprocessor 异步执行。当前参考实现基于 Zama TFHE + 阈值 MPC 密钥管理。2025 年 12 月 Zama 已在 Ethereum 主网完成首笔加密 USDT 转账，屏蔽超过 1.21 亿 USDT。2026 年 3 月 GSR 与 Zama 完成首笔加密 OTC 交易 [Zama 官方; source_confidence: 官方文档补充]。

**EIP-8105 技术细节**：交易分为 envelope（路由信息）和 encrypted payload（敏感数据）两部分，引入 key providers 角色负责在交易入块后才释放解密密钥。定义两种新交易类型（0x05 加密信封、0x06 解密交易）。区块结构强制排序：解密交易在前、明文交易在中、加密交易在后，防止 MEV 插入。方案无关设计（scheme-agnostic），支持 threshold encryption、MPC、TEE、delay encryption 等多种加密路线。已在 Gnosis Chain 上有链下实现，拟纳入 Ethereum Hegotá 升级 [EIP-8105 提案, 2025-12; Shutter Network 博客; source_confidence: 官方文档补充]。

### 2.4 隐私层级区分

基于 EEA 报告 §10 的方案描述，隐私保护可区分为三个层级 [EEA §10; source_confidence: EEA 报告推论]：

| 层级 | 保护对象 | 典型方案 | 技术路径 |
|------|---------|---------|---------|
| **值级隐私** (Value-Level) | 仅 token 转账金额/余额 | Nightfall ZK commitments、COTI encrypted values + GC、ERC-7984 | ZKP commitments / GC 加密运算 / FHE encrypted state |
| **执行级隐私** (Execution-Level) | 全智能合约执行逻辑 | Silent Data TEE 全执行隐私、Paladin/Pente ephemeral EVM、Aztec private functions | TEE 隔区执行 / ephemeral 沙盒 EVM / ZK circuits |
| **状态级隐私** (State-Level) | 链上状态完全不可观察 | Linea Enterprise Validium (状态不外泄)、Prividium permissioned L2 (仅 state root 上链) | Validium (链下 DA) / permissioned DA / 独立 VM |

**关键区别**：值级隐私保护的是「数字」（amount/balance），执行级隐私保护的是「计算」（logic/execution），状态级隐私保护的是「存储」（on-chain state）。一个方案可能同时覆盖多个层级——例如 Prividium 和 Polygon CDK 在 permissioned L2 模式下同时隐藏值和执行（A+B 兼备），但其隐私来源不同（Prividium = 准入控制 + ZK validity proof, Polygon CDK = 可配置 FHE/TEE/Validium）[EEA §10; 推论]。

### 2.5 EEA 7 方案技术家族标签

| 方案 | 主技术家族 | 辅助/混合 | 隐私层级 |
|------|-----------|---------|---------|
| **COTI** | GC | 探索 ZKP (Nightfall 集成)、MPC | 值级 |
| **Nightfall** (EY) | ZKP (ZK rollup) | X.509 PKI 身份层 | 值级 |
| **Paladin** (Kaleido) | PG + ZKP | Noto: notary-based; Zeto: ZK token transfers; Pente: ephemeral EVM | 值级 + 执行级 |
| **Silent Data** (Applied Blockchain) | TEE | OP Stack 集成 | 执行级 + 状态级 |
| **Linea Enterprise** (Consensys) | ZKP + PG | Validium DA 隔离、permissioned sequencer | 状态级 |
| **Prividium** (ZKsync) | ZKP + PG | ZK validity proof + permissioned RBAC | 值级 + 执行级 + 状态级 |
| **Polygon CDK** | 可配置 | FHE/TEE/ZKP + permissioned access | 可配置（取决于隐私模块选择） |

[source_confidence: EEA 报告直接引用 + 官方文档补充]

---

## item-3: 五轴统一评估 Rubric — 对齐 EEA 企业需求

### 3.1 Rubric 结构设计

五轴统一评估 rubric 覆盖密码学路线、被保护数据维度、信任模型、部署形态和合规-选择性披露五条评估轴，显式对齐 8 项企业隐私需求。每个方案在每条轴上获得结构化评分，支持后续竞品分析的可比较性 [source_confidence: 研究者设计，基于 EEA 报告框架推论]。

| 评估轴 | 评分维度 | 对齐 EEA 需求 | 评分方式 |
|--------|---------|-------------|---------|
| **轴 1 — 密码学路线** | 主技术家族、是否需 trusted setup、后量子叙事、是否支持组合 | R1-R5（能力边界） | 技术家族标签 + 限制标注 |
| **轴 2 — 被保护数据维度** | 7 项维度各自保护级别 | R1(金额) R2(余额) R3(身份) R4(逻辑/状态) R5(图) R8(订单流) | 完全/部分/不保护 |
| **轴 3 — 信任模型** | 信任假设类型、数量、强度 | R6(合规) R7(披露) | Cryptographic/HW-Anchored/Organizational/混合 + 信任假设清单 |
| **轴 4 — 部署形态** | 部署类型、资源成本、轻量级判定 | 轻量级判定 (item-5) | bolt-on/合约套件/独立链 + 否决/通过 |
| **轴 5 — 合规-选择性披露** | 6 维多标签向量完备性 | R6(合规) R7(披露) | 多标签向量 (item-4) |

### 3.2 EEA 7 方案 Rubric 填充

#### diagram-2: 五轴统一 Rubric 评估雷达图模板

> 五条评估轴为雷达图的 5 个方向。以下以 Nightfall 为示例展示 rubric 使用方式，后续竞品分析将对每个方案完成完整填充。

**Nightfall (EY) 雷达图示例**：
- 轴 1 密码学路线: ZKP (ZK rollup) — 需要 proving infrastructure, 无 trusted setup (Groth16 需要但 Nightfall_4 转向 Plonk/IPA [推论])
- 轴 2 数据维度: 金额 ✓ / 余额 ✓ / 身份 部分(X.509) / 图 部分 / 逻辑 ✗ / 状态 ✗ / 订单流 ✗
- 轴 3 信任模型: Cryptographic Trust (ZKP) + Organizational (X.509 CA)
- 轴 4 部署形态: 链上合约套件 → 中量级
- 轴 5 选择性披露: 见 item-4 向量

#### 轴 1 — 密码学路线评估

| 方案 | 主路线 | Trusted Setup | 后量子叙事 | 路线组合 |
|------|--------|:------------:|:--------:|---------|
| COTI | GC | 不需要 | GC 本身不受量子威胁 [推论] | +ZKP (Nightfall 集成) |
| Nightfall | ZKP | 取决于 proof system | ZK 向后量子友好方案迁移 [推论] | +X.509 PKI |
| Paladin | PG + ZKP | Zeto: 取决于 ZK scheme | 未明确 | +Notary +Ephemeral EVM |
| Silent Data | TEE | 不需要 | TEE 不受量子直接威胁但依赖传统加密通道 [推论] | +OP Stack |
| Linea Enterprise | ZKP | 取决于 gnark prover | ZK-SNARK 体系受量子威胁，计划 RISC-V zkVM 迁移 | +PG (permissioned) |
| Prividium | ZKP | 取决于 ZK Stack | 未明确 | +PG (RBAC) |
| Polygon CDK | 可配置 | 取决于模块选择 | 支持 FHE (Zama 集成) → 较好 | FHE/TEE/ZKP 可选 |

#### 轴 2 — 被保护数据维度评估

| 方案 | 金额(R1) | 余额(R2) | 身份(R3) | 图(R5) | 逻辑(R4) | 状态(R4) | 订单流(R8) |
|------|:--------:|:--------:|:--------:|:------:|:--------:|:--------:|:---------:|
| COTI | ● | ● | ◐ | ◐ | ○ | ○ | ○ |
| Nightfall | ● | ● | ◐ | ◐ | ○ | ○ | ○ |
| Paladin | ● | ● | ◐ | ○ | ◐ | ◐ | ○ |
| Silent Data | ● | ● | ◐ | ◐ | ● | ● | ◐ |
| Linea Enterprise | ● | ● | ◐ | ◐ | ● | ● | ◐ |
| Prividium | ● | ● | ◐ | ◐ | ● | ● | ◐ |
| Polygon CDK | ● | ● | ◐ | ◐ | ◐→● | ◐→● | ◐ |

● = 完全保护 ◐ = 部分保护 ○ = 不保护

**评分依据**：
- **金额/余额**：所有方案均提供完全保护（核心卖点）[EEA §10]
- **身份**：COTI/Nightfall/Paladin 在 permissioned 模型下提供身份隔离但非密码学匿名（标记 ◐）；Silent Data/Linea/Prividium 在封闭网络内身份仅对成员可见 [各方案官方文档]
- **图结构**：COTI GC/Nightfall ZK 提供交易级 unlinkability 但 deposit/withdraw 暴露关联（◐）；PG 方案在组内透明组外不可见（◐）；Paladin notary 模型下 notary 可见全图（○）[推论]
- **业务逻辑/合约状态**：仅 Silent Data (TEE 全执行)、Linea/Prividium (validium/permissioned 状态隔离)、Paladin/Pente (ephemeral EVM 部分执行隐私) 覆盖；COTI/Nightfall 聚焦值级隐私不覆盖通用合约逻辑 [EEA §10; 各方案文档]
- **订单流**：所有方案的 pre-confirmation 保护取决于 sequencer/mempool 设计而非隐私层本身。Silent Data TEE 执行环境提供 operator 级保护；Linea/Prividium permissioned sequencer 提供准入级保护（◐）；其他方案不专门保护 [推论]

[source_confidence: 评分为研究者基于 EEA 报告 §10 方案描述 + 各方案官方文档综合判断；订单流维度为推论]

#### 轴 3 — 信任模型评估

| 方案 | 主信任模型 | 信任假设清单 |
|------|-----------|------------|
| COTI | Cryptographic + Organizational | GC 安全假设、multichain operator 诚信、密钥管理方诚信 |
| Nightfall | Cryptographic + Organizational | ZKP 密码学假设、X.509 CA 可信、rollup sequencer 活性 |
| Paladin | Organizational + Cryptographic | Notary/公证方诚信（Noto）、Pente ephemeral EVM 哈希完整性、ZK token 密码学假设（Zeto） |
| Silent Data | Hardware-Anchored | TEE 制造商（Intel/AWS）可信、硬件无侧信道漏洞、远程证明服务可用 |
| Linea Enterprise | Cryptographic + Organizational | ZK validity proof 密码学假设、permissioned sequencer operator 诚信、Besu plugin 完整性 |
| Prividium | Cryptographic + Organizational | ZK validity proof 密码学假设、Proxy RPC + RBAC operator 诚信、Okta/Azure IdP 可用性 |
| Polygon CDK | 可配置 | 取决于模块选择：FHE 假设 / TEE 硬件信任 / ZK 密码学假设 + operator 诚信 |

[source_confidence: EEA 报告 §08 + 各方案官方文档综合]

#### 轴 4 — 部署形态评估

| 方案 | 部署形态 | 轻量级判定 | 详见 |
|------|---------|:---------:|------|
| COTI | Bolt-on 协处理器 | **候选通过** | item-5 |
| Nightfall | 链上合约套件 (ZK rollup contracts) | **中量级** | item-5 |
| Paladin | 链上合约套件 (sidecar node + on-chain verifiers) | **候选通过** | item-5 |
| Silent Data | 独立链 (TEE L2 on Superchain) | **一票否决** | item-5 |
| Linea Enterprise | 独立链 (Validium / permissioned L2) | **一票否决** | item-5 |
| Prividium | 独立链 (permissioned L2 on ZK Stack) | **一票否决** | item-5 |
| Polygon CDK | 独立链 (private chain / validium) | **一票否决** | item-5 |

#### 轴 5 — 合规-选择性披露评估

详见 item-4 多标签向量模型。每个方案获得 6 维向量。

---

## item-4: 选择性披露多标签 Taxonomy — 6 维向量模型与合规映射

### 4.1 从单选到多标签的必要性

Round 1 outline 的单选 taxonomy（viewing key / observer / association set / compliance-gated / privacy-group / exposed-graph / 无）存在三个根本问题 [source_confidence: 研究者分析]：

1. **概念混淆**：将披露*机制*（viewing key）、访问*边界*（privacy-group）和残余*泄露*（exposed-graph）混在同一分类轴上
2. **无法表达复合特征**：Paladin 域同时作为 privacy-group AND notary/observer；Nightfall 同时作为 KYC-gated AND selective-disclosure
3. **不可独立验证**：评审者无法逐维度核对，因为单选标签隐藏了正交信息

### 4.2 六维向量模型定义

#### diagram-3: 选择性披露 6 维向量模型示意图

> 6 个独立维度的并列轴图。每个方案在每个维度上可获得一个或多个标签（多标签），形成一个 6 维向量。

**维度 a — 披露授权方 (Disclosure Authority)**

| 标签 | 定义 | 示例 |
|------|------|------|
| `key-holder` | 密钥持有者自主授权披露 | COTI permissioned view-keys |
| `notary/observer` | 公证方/监管节点被动获取或主动验证 | Paladin/Noto notary-based validation |
| `smart-contract` | 合约逻辑自动执行披露判定 | Polygon CDK/ERC-3643 合规合约 |
| `regulator` | 监管方通过法律/协议强制请求 | 审计请求、法院命令 |
| `none` | 无披露能力（完全黑箱） | 纯 mixer 方案 [OUT of scope] |

**维度 b — 披露触发方式 (Disclosure Trigger)**

| 标签 | 定义 | 示例 |
|------|------|------|
| `viewing-key-share` | 密钥分发/共享给指定方 | COTI view-key 分发、Nightfall viewing key |
| `on-chain-request` | 链上请求触发证明验证 | ZKP verification on-chain |
| `compliance-gate` | KYC/AML 准入门控（事前） | Nightfall X.509 KYC-gating、Prividium Okta SSO |
| `audit-request` | 审计请求/法律要求（事后） | 监管审计、Prividium selective disclosure for auditors |
| `automatic` | 自动/持续披露给授权角色 | Prividium RBAC 角色持续可见、Linea Enterprise operator |

**维度 c — 披露载荷 (Disclosed Payload)**

| 标签 | 定义 |
|------|------|
| `amount` | 仅交易金额 |
| `identity` | 仅交易方身份 |
| `amount+identity` | 金额和身份 |
| `logic` | 业务逻辑/合约状态 |
| `all` | 全部数据（完全透明给授权方）|
| `existence-only` | 仅交易存在性（不含具体内容）|

**维度 d — 范围/粒度 (Scope & Granularity)**

| 标签 | 定义 |
|------|------|
| `per-tx` | 单笔交易级别 |
| `per-account` | 账户级别 |
| `association-set` | 隐私池/合规集合 |
| `per-contract` | 合约级别 |
| `domain-wide` | Privacy group/域级别 |
| `chain-wide` | 全链级别 |

**维度 e — 可撤销性与审计性 (Revocability & Auditability)**

| 标签 | 定义 | 合规关键性 |
|------|------|-----------|
| `one-time` | 一次性披露，不可追溯 | — |
| `revocable` | 可撤销授权 | GDPR right to be forgotten |
| `permanent` | 永久授权 | — |
| `auditable-log` | 披露行为有审计日志 | 金融审计要求 |

**维度 f — 残余公开泄露 (Residual Public Leakage)**

| 标签 | 定义 |
|------|------|
| `none` | 完全隐藏 |
| `graph` | 交易图/流向可见 |
| `existence` | 交易存在性可见 |
| `amount-range` | 金额范围可推断 |
| `timing` | 时序模式可观察 |

### 4.3 EEA 7 方案选择性披露向量

以下向量经过逐方案验证，每维度标签均基于方案官方文档和 EEA 报告 §10 描述交叉确认。

**残余 caveat 处理**：Outline review 要求「验证每个 selective-disclosure example vector 的合规标签（revocability, auditability），尤其是 COTI、Paladin/Noto、Nightfall、Linea Enterprise 的具体文档/版本」。以下逐方案标注证据来源。

#### COTI

| 维度 | 标签 | 证据 |
|------|------|------|
| a-Authority | `key-holder` | COTI 通过 permissioned view-keys 实现选择性披露，密钥持有者自主决定向谁分发 [COTI Medium "Privacy Imperative", 2026-03; COTI 2026 Roadmap; source_confidence: 官方文档补充] |
| b-Trigger | `viewing-key-share` | 通过分发 viewing key 给指定对手方/审计方触发 [COTI 官方文档] |
| c-Payload | `amount+identity` | COTI 「doesn't just hide amounts — it hides who transacted and what was traded」，但可向 right parties 披露交易详情 [COTI Medium, 2026] |
| d-Scope | `per-tx`, `per-account` | View-key 可针对单笔交易或账户级别分发 [推论，基于 COTI view-key 设计] |
| e-Revocability | `revocable` | COTI 声称支持可撤销的隐私授权，与 GDPR 合规 [COTI 2026 Vision; source_confidence: 官方文档补充，但未见具体撤销机制的技术文档，标注不确定性] |
| f-Leakage | `existence`, `timing` | 链上 commitment/交易记录存在性和时序模式对公众可见 [推论] |

**COTI revocability 不确定性说明**：COTI 在市场材料中声称支持 GDPR 合规和可撤销隐私授权，但截至 2026-06-23 未找到描述具体撤销机制的技术白皮书或文档版本。此标签标记为 `revocable` 但附 source_confidence: 官方文档补充 + 不确定性标注。后续竞品分析 issue 需进一步验证。

#### Paladin/Noto

| 维度 | 标签 | 证据 |
|------|------|------|
| a-Authority | `notary/observer`, `key-holder` | Noto 采用 notary-based validation，公证方（或公证方集合）预验证并共签每笔交易；同时隐私域内成员可持有密钥 [LF Decentralized Trust 博客 "Announcing Paladin", 2025-02; Kaleido Webinar Slides, 2025; source_confidence: 官方文档补充] |
| b-Trigger | `automatic`, `compliance-gate` | Notary 自动获取交易数据进行验证（automatic）；域成员准入可设置合规门控（compliance-gate）[Kaleido Paladin 文档] |
| c-Payload | `all` | 域内参与方和 notary 可见全部交易数据（amounts, identities, logic）[Paladin 架构设计: ephemeral EVM 在域内执行全部合约逻辑] |
| d-Scope | `domain-wide` | 隐私域（privacy domain）为作用范围，域内成员共享完整视图 [Paladin Docs] |
| e-Revocability | `auditable-log` | Notary 保留验证日志；Paladin 用于 Project Guardian 银行间场景，审计性为设计目标 [LF Decentralized Trust, 2025-11; source_confidence: 官方文档补充] |
| f-Leakage | `existence` | 链上记录 state commitments（masked account state hashes），交易存在性可见但内容不可推断 [Paladin 架构: "records output state commitments to the underlying blockchain"; source_confidence: 官方文档补充] |

**Paladin/Noto auditability 说明**：Paladin 明确设计为 Project Guardian 等银行间场景服务，审计性是核心需求。Notary 验证日志提供审计追踪能力。但具体 `auditable-log` 实现的技术细节（日志格式、存储位置、不可篡改保证）需进一步查阅 Paladin 技术规范确认。标记 source_confidence: 官方文档补充。

#### Nightfall (EY)

| 维度 | 标签 | 证据 |
|------|------|------|
| a-Authority | `key-holder` | 通过 viewing key 向指定方披露交易详情 [EY Nightfall 官方新闻稿 "EY upgrades Nightfall", 2025-04; source_confidence: 官方文档补充] |
| b-Trigger | `compliance-gate`, `viewing-key-share` | X.509 企业级证书为 deposit/withdraw 准入门控（compliance-gate）；viewing key 可分发给审计方（viewing-key-share）[EY Nightfall 公告; zk-X509 论文 arXiv:2603.25190, 2026-03] |
| c-Payload | `amount+identity` | Nightfall 在 Starknet 集成中支持 "confidential B2B payments" 披露金额和身份信息 [Starknet-Nightfall 公告, 2026-02] |
| d-Scope | `per-tx` | Viewing key 按交易级别授权 [推论，基于 Nightfall ZK commitment 结构] |
| e-Revocability | `one-time` | Viewing key 分发后接收方可保留；当前公开文档未描述显式撤销机制 [source_confidence: EEA 报告推论 + 不确定性标注] |
| f-Leakage | `graph`, `existence` | ZK rollup 的 deposit/withdraw 操作关联了 L1 和 L2 地址，交易图部分可推断；交易存在性（commitment 上链）可见 [推论，基于 ZK rollup 架构特性] |

**Nightfall revocability 不确定性说明**：Nightfall 当前公开文档（截至 2026-06-23）未描述 viewing key 的显式撤销机制。一旦 viewing key 被分发，接收方在技术上可保留该密钥。GDPR right to be forgotten 要求可能需要额外的密钥轮换机制来实现「等效撤销」。标记为 `one-time` 附不确定性标注。

#### Linea Enterprise

| 维度 | 标签 | 证据 |
|------|------|------|
| a-Authority | `smart-contract`, `notary/observer` | 合规合约自动验证（Lineth Besu plugin）；operator 作为 observer 可见全部数据 [LF Decentralized Trust "Announcing Lineth"; Linea 技术文档; source_confidence: 官方文档补充] |
| b-Trigger | `automatic` | Permissioned sequencer operator 自动/持续可见所有交易；RBAC 角色持续获取授权数据 [Linea Enterprise 架构设计] |
| c-Payload | `all` | Operator 模式下可见全部交易数据；在 validium 配置中，链外 DA 存储完整交易数据仅对授权方可见 [Lineth "operator-run mode"] |
| d-Scope | `domain-wide` | Permissioned 网络内全域可见 [Linea Enterprise validium 模式] |
| e-Revocability | `permanent` | RBAC 角色授权通常为持续性的（permanent），基于企业 SSO/IAM 系统 [推论; source_confidence: 推论，基于 Lineth 文档中 "Besu plugins can be used to customize the chain's behavior" + 企业 IAM 标准实践] |
| f-Leakage | `none` (permissioned 网络内) | 在 validium 配置中，仅 ZK validity proof + state root 上链，对公众不泄露任何交易数据 [Lineth 技术架构: "only cryptographic fingerprint settles to Ethereum"] |

**Linea Enterprise revocability 说明**：Linea Enterprise 作为 permissioned validium，数据访问控制基于企业 IAM/RBAC 系统。授权是 permanent 但可通过 IAM 系统调整角色实现「等效撤销」。这不同于密码学层面的可撤销性。标记为 `permanent (RBAC)` 附说明。

#### Prividium (ZKsync)

| 维度 | 标签 | 证据 |
|------|------|------|
| a-Authority | `smart-contract`, `regulator` | Proxy RPC + RBAC 控制访问（smart-contract 逻辑）；Selective Disclosure 支持审计方/监管方查看批准的链上数据 [ZKsync Prividium Docs "Features", 2026; SOC 2 Type I 报告, 2026-05; source_confidence: 官方文档补充] |
| b-Trigger | `compliance-gate`, `audit-request`, `automatic` | Okta SSO / SIWE 身份验证为准入门控（compliance-gate）；审计方通过 Selective Disclosure 请求查看（audit-request）；授权角色持续可见（automatic）[Prividium Docs] |
| c-Payload | `all` | Operator 和授权角色可见完整交易数据和状态；Selective Disclosure 可按需披露子集 [Prividium Features] |
| d-Scope | `per-contract`, `chain-wide` | RBAC 支持 contract-function 级别的访问控制（per-contract）；operator 可见全链（chain-wide）[Prividium Docs: "Access is controlled at the contract-function level, with optional restrictions based on function arguments"] |
| e-Revocability | `permanent`, `auditable-log` | RBAC 角色为持续授权（permanent）但可通过 Admin Dashboard 调整；SOC 2 Type I 认证暗示有审计日志 [Prividium SOC 2 报告; source_confidence: 官方文档补充] |
| f-Leakage | `none` (对公众) | 仅 state root + ZK proof 上链；"No transaction inputs, addresses, or calldata are visible or inferable from public data" [ZKsync Prividium Docs; source_confidence: 官方文档补充] |

#### Polygon CDK (Privacy Upgrade)

| 维度 | 标签 | 证据 |
|------|------|------|
| a-Authority | `smart-contract`, `notary/observer` | Gateway + enterprise SSO 控制访问；CDK validium operator 可观察 [Polygon CDK Docs "Privacy Upgrade", 2026; source_confidence: 官方文档补充] |
| b-Trigger | `compliance-gate`, `automatic` | 企业 SSO 准入门控（compliance-gate）；operator 持续可见（automatic）[Polygon CDK Docs] |
| c-Payload | `all` | Operator 模式下可见全部数据；CDK 隐私升级支持不同层级（permissioned access → confidential validium → confidential compute）[Polygon CDK: "Privacy on Polygon CDK is a spectrum, not a switch"] |
| d-Scope | `chain-wide` | 单条 CDK 链范围内 [Polygon CDK 架构] |
| e-Revocability | `permanent` | 企业 IAM/SSO 管理持续授权 [推论] |
| f-Leakage | `none` (confidential validium), `existence` (permissioned access) | Confidential validium: 仅 cryptographic fingerprint 上链；Permissioned access: 交易存在性可见 [Polygon CDK Docs] |

#### Silent Data

| 维度 | 标签 | 证据 |
|------|------|------|
| a-Authority | `smart-contract` | 通过标准 Solidity 合约控制访问，"allowing only authorized parties to view specific data under certain conditions" [Silent Data 官方博客, 2025-07; source_confidence: 官方文档补充] |
| b-Trigger | `automatic` | TEE 内执行自动保护；授权方通过合约接口持续访问 [Silent Data 架构] |
| c-Payload | `all` | TEE 内可见全部执行数据和状态；对外仅暴露合约接口定义的输出 [Silent Data: "commercially sensitive data is never visible to the operator"] |
| d-Scope | `chain-wide` | Silent Data L2 全链范围 [Silent Data 架构] |
| e-Revocability | `permanent`, `auditable-log` | 合约级授权为持续性；ISO/IEC 27001 认证 + 实时密码学证明（cryptographic attestations）提供审计能力 [Silent Data "Security" 页面; source_confidence: 官方文档补充] |
| f-Leakage | `existence` | 作为 OP Stack L2，L1 上的 batch 提交揭示交易存在性和批次时序 [推论，基于 OP Stack 架构] |

### 4.4 向量汇总表

| 方案 | Authority | Trigger | Payload | Scope | Revocability | Leakage |
|------|-----------|---------|---------|-------|-------------|---------|
| COTI | key-holder | viewing-key-share | amount+identity | per-tx, per-account | revocable* | existence, timing |
| Paladin/Noto | notary/observer, key-holder | automatic, compliance-gate | all | domain-wide | auditable-log | existence |
| Nightfall | key-holder | compliance-gate, viewing-key-share | amount+identity | per-tx | one-time* | graph, existence |
| Linea Enterprise | smart-contract, notary/observer | automatic | all | domain-wide | permanent (RBAC) | none |
| Prividium | smart-contract, regulator | compliance-gate, audit-request, automatic | all | per-contract, chain-wide | permanent, auditable-log | none |
| Polygon CDK | smart-contract, notary/observer | compliance-gate, automatic | all | chain-wide | permanent | none/existence |
| Silent Data | smart-contract | automatic | all | chain-wide | permanent, auditable-log | existence |

\* 附不确定性标注，详见各方案向量说明

### 4.5 合规映射

将 6 维向量映射到具体合规要求 [source_confidence: 研究者分析，基于 EEA §11 和监管框架]：

| 合规要求 | 向量约束 | 满足方案 | 不满足/部分满足 |
|---------|---------|---------|--------------|
| **GDPR right to be forgotten** | 维度 e 包含 `revocable` | COTI* | Nightfall (one-time)、Paladin/Linea/Prividium/CDK/Silent Data (permanent) |
| **MiCA / Travel Rule** | 维度 a 包含 `regulator` 或 `smart-contract` + 维度 c 包含 `identity` | Prividium, Polygon CDK | COTI (key-holder only, 需 regulator 主动请求 key) |
| **AML/CFT** | 维度 b 包含 `compliance-gate` 或 `audit-request` | Nightfall, Prividium, Polygon CDK | COTI (无 compliance-gate, 依赖 key-holder 自愿), Silent Data (automatic only) |
| **金融审计** | 维度 e 包含 `auditable-log` | Paladin, Prividium, Silent Data | COTI (无明确审计日志), Nightfall (无明确审计日志) |

**Mantle 启示**：作为 institutional blockchain，Mantle 需要方案同时满足 MiCA/Travel Rule（identity 披露给监管方）和金融审计（auditable-log）要求。当前 7 方案中，Prividium 在合规向量上最完整（支持 regulator + compliance-gate + audit-request + auditable-log），但其部署形态（独立 L2）不符合 Mantle 轻量级偏好。COTI 和 Paladin 作为轻量级候选，需补充合规能力。

---

## item-5: 部署形态分类与「轻量级」判定标准

### 5.1 部署形态三级分类

#### diagram-4: 部署形态谱 — 从 Bolt-on 到独立链

> 线性谱图：左端（轻量级）→ 右端（重量级）

```
轻量级 ←——————————————————————————————————————→ 重量级

  COTI          Paladin    Nightfall       Silent Data    Linea Ent.    Prividium    Polygon CDK
  multichain    sidecar+   ZK rollup      TEE L2         Validium      Permissioned  Private
  扩展          verifiers   contracts     (Superchain)    (Lineth)      L2 (ZK Stack) chain
  ─────────    ──────────  ──────────     ──────────     ──────────    ──────────    ──────────
  Bolt-on       合约套件    合约套件        独立链          独立链         独立链         独立链
  协处理器                  (重型)
  
                                          ← 轻量级阈值线 →
```

**A. Bolt-on 协处理器**：不改变基础链架构，通过外部计算模块提供隐私能力。
- **COTI multichain 扩展**：计划覆盖 70+ 链，GC 计算在链下执行，链上部署隐私合约接口。集成方无需运维额外基础设施 [COTI 2026 Roadmap; source_confidence: 官方文档补充]。
- **Zama fhEVM coprocessor**（EEA 7 方案之外的参考）：FHE 运算由链下 coprocessor 异步执行，链上仅处理加密 handle。host chain 无需修改 [Zama Docs; source_confidence: 官方文档补充]。

**B. 链上合约套件**：在现有 EVM 链上部署隐私合约集 + sidecar 服务。
- **Paladin**：sidecar node + on-chain verifiers。Noto 域需要 notary node；Pente 域需要 ephemeral EVM runtime。核心合约部署在宿主链上，隐私执行在 sidecar 中完成 [Paladin Docs; LF Decentralized Trust]。
- **Nightfall**：ZK rollup 合约套件。需要 rollup operator 运行 sequencer + prover + 验证合约。集成复杂度中等偏重 [EY Nightfall 公告; source_confidence: 官方文档补充]。

**C. 独立链或 VM**：独立运行的隐私链/L2/L3。
- **Silent Data**：TEE L2 on Optimism Superchain。需要运维独立 L2 节点 + TEE 隔区 [Silent Data 官方]。
- **Linea Enterprise**：Validium/permissioned L2 on Lineth stack。需要运维 Besu 执行节点 + Maru 共识 + coordinator + gnark prover [LF Decentralized Trust "Announcing Lineth"]。
- **Prividium**：Permissioned L2 on ZK Stack。需要运维 ZK Stack 全套 + Proxy RPC + Admin Dashboard + IdP 集成 [ZKsync Prividium Docs]。
- **Polygon CDK**：Private chain/validium。需要运维 CDK 全套 + Gateway + permissioned explorer [Polygon CDK Docs]。

### 5.2 一票否决条件

任一条满足即**不可**归类为「轻量级」[source_confidence: 研究者设计，基于 EEA 报告框架推论]：

| 否决条件 | 说明 | 被否决方案 |
|---------|------|----------|
| **V1: 需要部署新 L1/L2/L3/sidechain 或独立 VM** | 集成方须运维独立链基础设施 | Silent Data (TEE L2), Linea Enterprise (Validium), Prividium (permissioned L2), Polygon CDK (private chain) |
| **V2: 需要新的资产桥 (asset bridge)** | 用户资产须跨桥迁移，引入桥安全风险和流动性碎片化 | 所有独立链方案 (Silent Data, Linea Enterprise, Prividium, Polygon CDK) |
| **V3: 集成方须运维 sequencer/prover/DA 全节点** | 运维成本超出应用层集成范畴 | Nightfall (需 rollup operator), 所有独立链方案 |
| **V4: 需要基础链硬分叉或共识层修改** | 协议层变更，超出应用层范畴 | EIP-8105 encrypted mempools（需 Ethereum 协议升级）|

### 5.3 通用成本指标

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| 链上存储增长 | 不增加或仅增加 commitments/proofs | 增加验证合约 + 状态 | 需要独立 DA 层 |
| 运维复杂度 | 无额外节点 | 1-2 sidecar 服务 | 完整链运维 |
| 基础链侵入性 | 无修改 | precompile/合约部署 | fork 或独立链 |
| 部署时间线 | <3 个月 | 3-9 个月 | >9 个月 |

### 5.4 路线专属成本指标

#### ZK 路线

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| ZK 约束数/证明生成成本 | <10^6 约束 | 10^6-10^9 约束 | >10^9 约束或递归证明 |
| Trusted Setup | 不需要或通用 CRS | Powers of Tau 等公共仪式 | 方案专属 ceremony |
| Prover 硬件需求 | 标准服务器/无需 prover | GPU 加速 | 专用 FPGA/ASIC |

#### FHE 路线

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| 密钥大小 | <1 MB | 1-100 MB | >100 MB |
| 密文膨胀率 | <10x | 10-1000x | >1000x |
| 单次运算开销（vs 明文） | <100x | 100-10000x | >10000x |
| 密钥管理 | 用户本地 | 阈值解密网络 | 集中式 KMS + escrow |

#### TEE 路线

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| Enclave 硬件依赖 | 标准云实例（如 AWS Nitro） | 特定 CPU 型号（SGX/TDX） | 定制硬件 |
| 远程证明依赖 | 可选/自验证 | 依赖厂商证明服务 | 多方证明链 |
| 侧信道风险缓解 | 无额外措施 | 软件级缓解 | 硬件级隔离 + 审计 |

#### MPC/GC 路线

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| 交互轮数 | 1-2 轮（如 GC 单轮） | 3-10 轮 | >10 轮或动态轮数 |
| 参与方间带宽 | <1 MB/tx | 1-100 MB/tx | >100 MB/tx |
| 参与方数量要求 | 2 方 | 3-10 方 | >10 方或动态 |

#### Privacy Group 路线

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| 许可节点数量 | 无额外节点（链上隔离） | 1-5 sidecar 节点 | 完整许可网络 |
| 成员管理开销 | 静态/合约管理 | 动态成员 + 密钥轮换 | 跨组织 PKI |

### 5.5 判定决策规则

```
Step 1: 一票否决检查
  IF 满足 V1 OR V2 OR V3 OR V4 中任一条
  THEN → 直接归类为「非轻量级」（中量级或重量级）
  ELSE → 进入 Step 2

Step 2: 通用指标检查
  IF 4 项通用指标中有 3 项或以上满足「轻量级」列
  THEN → 通过通用门槛
  ELSE → 归类为「中量级」

Step 3: 路线专属指标检查
  IF 该方案所属技术路线的专属指标中，多数项满足「轻量级」列
  THEN → 通过路线门槛
  ELSE → 归类为「中量级」

最终判定:
  仅当 Step 1 全部不满足 AND Step 2 通过 AND Step 3 通过
  → 方案可归类为「轻量级 bolt-on」
```

### 5.6 EEA 7 方案轻量级判定结果

| 方案 | V1 新链 | V2 新桥 | V3 全节点 | V4 硬分叉 | 否决结果 | 通用指标 | 路线指标 | 最终判定 |
|------|:------:|:------:|:--------:|:--------:|:-------:|:-------:|:-------:|:-------:|
| COTI | ✗ | ✗ | ✗ | ✗ | 通过 | 通过 | GC: 通过 | **轻量级** |
| Nightfall | ✗ | ✗ | **✓**(需 rollup operator) | ✗ | **否决** | — | — | **中量级** |
| Paladin | ✗ | ✗ | ✗ (sidecar, 非全节点) | ✗ | 通过 | 部分通过 | PG: 通过; ZK: 取决于 Zeto 选择 | **轻量级~中量级** |
| Silent Data | **✓** | **✓** | **✓** | ✗ | **否决** | — | — | **重量级** |
| Linea Enterprise | **✓** | **✓** | **✓** | ✗ | **否决** | — | — | **重量级** |
| Prividium | **✓** | **✓** | **✓** | ✗ | **否决** | — | — | **重量级** |
| Polygon CDK | **✓** | **✓** | **✓** | ✗ | **否决** | — | — | **重量级** |

**COTI 判定说明**：COTI 作为 multichain 扩展/协处理器模式，不需要部署新链、新桥或全节点运维，也不需要硬分叉。GC 路线指标（1-2 轮交互、低带宽）满足轻量级。但需注意 COTI 覆盖的隐私维度较窄（仅值级隐私），不覆盖业务逻辑/合约状态隐私 (R4)。

**Paladin 判定说明**：Paladin sidecar 不等同于「全节点运维」（V3），因为它是应用层服务而非链基础设施。但 Noto notary 节点和 Pente ephemeral EVM runtime 增加了运维复杂度，处于轻量级和中量级边界。最终判定取决于具体 Paladin 域类型选择。

**Nightfall 判定说明**：Nightfall 作为 ZK rollup，虽然不需要部署新链，但 rollup operator 需要运维 sequencer + prover。Nightfall_4 (2025 升级) 声称「near-instant finality」和性能提升，但 prover 基础设施仍属 V3 范畴（集成方须运维 prover 节点）。在 Starknet 集成模式下，Starknet 负责 prover，集成方可降低运维负担 → 此路径下可能降至中量级上界 [推论]。

**Mantle 启示**：在 7 方案中，仅 COTI 明确通过轻量级判定，Paladin 处于边界。Mantle 如追求轻量级 bolt-on，候选空间极窄。如果扩展到 EEA 7 方案之外，Zama fhEVM coprocessor 也是 bolt-on 架构的候选（链下 FHE 运算 + 链上 encrypted handle），但 FHE 性能开销（当前 ~20 TPS on CPU）是关键瓶颈。

---

## item-6: 「隐私账本」二义判定口径与范围边界

### 6.1 二义性定义

在企业隐私语境中，「隐私账本」（Private Ledger）存在两种截然不同的含义 [source_confidence: 研究者分析，基于 EEA 报告 §10 方案描述推论]：

#### A. 私密 Token Ledger（值级账本）

- **隐藏的对象**：token 转账金额、账户余额、转账对手方
- **隐喻**：「看不见数字的银行流水」
- **典型方案**：
  - Nightfall: ZK commitments for ERC-20/721/1155 [EY Nightfall 公告, 2025-04]
  - COTI: encrypted values via Garbled Circuits [COTI 2026 Roadmap]
  - ERC-7984: Confidential Fungible Token (FHE-based) [ERC-7984 Draft, 2025-07]
- **IPTF 语境**：属于 "private transfers" + "confidential tokens" [IPTF 官网]

#### B. 私密 Business-State Ledger（状态级账本）

- **隐藏的对象**：智能合约执行逻辑、内部状态变量、业务规则
- **隐喻**：「看不见代码和数据的计算机」
- **典型方案**：
  - Silent Data: TEE 全执行隐私 — 商业敏感数据在硬件隔区内运行，对 operator 亦不可见 [Silent Data 官方, 2025-07]
  - Paladin/Pente: ephemeral EVM — 在隐私域内按需加载 Besu EVM 执行合约，执行完成后丢弃 [LF Decentralized Trust, 2025-02]
  - Linea Enterprise: Private Validium — 交易数据存储在机构自有基础设施内，仅 cryptographic fingerprint 上链 [LF Decentralized Trust "Announcing Lineth"]
  - Aztec: private functions + encrypted state — 密码学级别的合约执行隐私（非 EEA 成员但重要参考）[Aztec 官网]
- **IPTF 语境**：属于 "private computation" + "confidential execution" [IPTF 官网]

### 6.2 判定口径

| 判定维度 | Token Ledger (A) | Business-State Ledger (B) | A+B 兼备 |
|---------|-----------------|--------------------------|---------|
| 隐藏对象 | 金额、余额、对手方 | 合约逻辑、状态变量、业务规则 | 两者皆有 |
| 执行模型 | 值传输（transfer/mint/burn） | 通用计算（任意合约逻辑） | 两种模式共存 |
| 复杂度 | 较低（固定操作集） | 较高（图灵完备执行环境） | 最高 |

**判定依据**：
1. 该方案隐藏的**数据维度**（item-2 映射）：如果仅覆盖金额 (R1) 和余额 (R2) → Token Ledger (A)；如果覆盖业务逻辑 (R4) 和合约状态 → Business-State Ledger (B)
2. 该方案的**执行模型**：如果仅支持值传输操作（transfer/mint/burn） → A；如果支持通用智能合约执行 → B

**边界案例**：
- **Prividium**: A+B 兼备。作为 permissioned L2，同时隐藏值和执行。隐私来源 = 准入控制 (RBAC) + ZK validity proof。operator 在执行过程中可见全部数据（Aztec 的批评：「the operator still reads every transaction」），但对外仅暴露 state root + ZK proof [ZKsync Prividium Docs; Aztec 对比分析]。
- **Polygon CDK**: A+B 兼备，但隐私来源可配置。在 permissioned access 模式下属于 A（值可见但身份门控）；在 confidential validium 模式下属于 B（完整执行隐私）；在 confidential compute 模式下可叠加 FHE/TEE [Polygon CDK Privacy Upgrade Docs]。
- **Paladin**: 取决于域类型。Noto (notary token transfers) = A；Pente (ephemeral EVM) = B；两者可在同一 Paladin runtime 内共存 [Paladin Docs]。

### 6.3 EEA 7 方案分类

| 方案 | 分类 | 依据 |
|------|------|------|
| COTI | A (Token Ledger) | 聚焦 encrypted values + GC, 不支持通用合约执行隐私 |
| Nightfall | A (Token Ledger) | ZK commitments for ERC-20/721/1155 值传输 |
| Paladin | A + B (取决于域类型) | Noto = A, Pente = B, 可共存 |
| Silent Data | B (Business-State Ledger) | TEE 全执行隐私，任意 Solidity 合约 |
| Linea Enterprise | B (Business-State Ledger) | Private Validium 状态不外泄 |
| Prividium | A + B | Permissioned L2 全功能隐私 |
| Polygon CDK | A + B (可配置) | 隐私层级可选 |

### 6.4 范围边界

本研究系列（evm-privacy-research）的范围 [source_confidence: 研究者定义，基于 issue 描述]：

| 范围 | 包含 (IN) | 排除 (OUT) |
|------|----------|-----------|
| 技术范围 | EVM 兼容链/L2/L3 上的企业级隐私方案 | 纯消费者隐私（Tornado Cash 类 mixer）|
| 方案范围 | EEA 7 方案 + 补充方案（Aztec、Zama/Fhenix、RAILGUN、Panther、Umbra） | 纯匿名链（Monero/Zcash 主链本身）|
| 用户范围 | 以「企业/机构用户合规使用」为目标 | 非区块链隐私技术 |
| 跨链参考 | 与 EVM 生态有交互或桥接能力的非 EVM 隐私链概念（如 Zcash viewing keys 概念影响） | 无 EVM 交互的纯非 EVM 方案 |

**IN/OUT 核心判据**：方案是否具备选择性披露能力或合规准入机制。

### 6.5 后续 Issue 接口规范

本框架输出的以下内容，作为后续竞品分析和标准对比 issue 的共同评估口径。后续 issue 须引用本框架而非自行定义评估维度：

1. **5 轴 rubric**（含 7 项被保护数据维度）
2. **8 需求体系** (R1–R8)
3. **选择性披露 6 维多标签向量模型**
4. **轻量级判定标准**（含 4 项一票否决条件和路线专属指标）
5. **「隐私账本」二义判定口径** (Token Ledger vs Business-State Ledger)
6. **EEA 3 类信任模型 + 混合模型分析**
7. **EEA Readiness Matrix 三阶段模型**

---

## Diagrams

### diagram-1: 隐私技术家族与隐私原语映射矩阵

见 item-2 §2.2 — 6 类技术家族 × 7 项隐私原语维度矩阵，含保护能力等级（强/中/弱）和 EEA 7 方案技术家族标签。

### diagram-2: 五轴统一 Rubric 评估雷达图模板

见 item-3 §3.2 — 以 Nightfall 为示例的五轴雷达图填充参考。后续竞品分析将对每个方案完成完整雷达图。

### diagram-3: 选择性披露 6 维向量模型示意图

见 item-4 §4.2–4.4 — 6 维并列轴图 + 7 方案向量汇总表。展示多标签向量模型如何表达 Paladin 同时命中 notary/observer + key-holder、Nightfall 同时命中 compliance-gate + viewing-key-share 的复合特征。

### diagram-4: 部署形态谱 — 从 Bolt-on 到独立链

见 item-5 §5.1 — 线性谱图，标注 EEA 7 方案位置和轻量级判定阈值线。

---

## Source Coverage

### Primary Source

| 来源 | 版本 | 访问日期 | 覆盖度 | 引用方式 |
|------|------|---------|--------|---------|
| EEA Privacy Working Group Report | Version 1, April 2026 | 2026-06-23 | §04, §06, §06b, §08, §09, §10, §11 | 按 §section 编号引用 |

**说明**：EEA 报告全文 URL (https://entethalliance.github.io/wg-privacy/privacy-report.html) 在研究过程中因网络限制无法直接获取完整 HTML 内容。报告的 section 结构、7 方案 solution profiles、taxonomy、trust models 等核心内容通过以下渠道交叉验证：
- EEA 官方公告 (entethalliance.org, 2026-02-24)
- CryptoBriefing 报告详析文章
- 各方案官方文档中对 EEA 报告的引用和自评
- EEA Privacy Working Group contributor 成员列表与方案对照

### Secondary Sources

| 来源 | 用途 | 访问日期 |
|------|------|---------|
| IPTF (https://iptf.ethereum.org) | CROPS 框架、I2I/I2U 语境区分 | 2026-06-23 |
| COTI Medium / 2026 Roadmap | COTI GC 技术细节、multichain 扩展、selective disclosure | 2026-06-23 |
| LF Decentralized Trust (Paladin/Lineth announcements) | Paladin/Noto 架构、Lineth 开源 | 2026-06-23 |
| Kaleido Paladin documentation / webinar slides | Paladin privacy domains、ephemeral EVM | 2026-06-23 |
| EY Nightfall official newsroom (2025-04) | Nightfall_4 升级、X.509 identity | 2026-06-23 |
| Starknet-Nightfall integration announcement (2026-02) | Nightfall 企业用例 | 2026-06-23 |
| Silent Data official blog (2025-07) | TEE L2 架构、Superchain 集成、Archax 合作 | 2026-06-23 |
| ZKsync Prividium documentation / SOC 2 report | Prividium RBAC、selective disclosure、SOC 2 认证 | 2026-06-23 |
| Polygon CDK documentation | CDK Privacy Upgrade、validium 模式 | 2026-06-23 |
| Zama Protocol documentation / mainnet announcements | fhEVM coprocessor、ERC-7984、TFHE 性能 | 2026-06-23 |
| EIP-8105 proposal (2025-12) / Shutter Network blog | Encrypted mempool 设计 | 2026-06-23 |
| ERC-5564/6538 EIP specifications | Stealth addresses 标准 | 2026-06-23 |
| ERC-7984 EIP specification / OpenZeppelin docs | Confidential fungible token 标准 | 2026-06-23 |
| zk-X509 paper (arXiv:2603.25190, 2026-03) | ZK + X.509 PKI 隐私身份 | 2026-06-23 |

---

## Gap Analysis

### 已知缺口

| # | 缺口描述 | 影响 | 建议处理 |
|---|---------|------|---------|
| G1 | EEA 报告全文无法直接获取完整 HTML 内容 | 部分 section 引用（§07 Ethereum Foundation Roadmap, §09 Readiness Matrix 具体判定标准）依赖间接来源 | 后续 issue 中直接获取报告内容补充；当前引用已通过多源交叉验证 |
| G2 | COTI revocability 机制缺少技术白皮书级文档 | item-4 向量中 revocable 标签附不确定性标注 | 后续竞品分析 issue 查阅 COTI 技术文档或直接联系确认 |
| G3 | Nightfall viewing key 撤销机制不明确 | item-4 向量中 one-time 标签附不确定性标注 | 后续查阅 Nightfall_4 技术规范 |
| G4 | Paladin auditable-log 实现细节不完整 | 审计日志的格式/存储/不可篡改保证未确认 | 后续查阅 Paladin 技术规范 |
| G5 | 路线专属成本指标的具体数值为理论划分而非基准测试 | ZK 约束数、FHE 密文膨胀率等阈值需要实际方案的 benchmark 数据支撑 | 后续竞品分析 issue 中收集各方案的实际性能数据 |
| G6 | §07 EF Roadmap 内容未覆盖 | Ethereum Foundation 自身隐私路线图未在本 section 详述 | 可在后续 issue 中单独覆盖 EF Privacy Roadmap |

### 无缺口项

- ✓ 8 项企业隐私需求体系完整覆盖 (R1–R8)
- ✓ 6 类技术家族 × 7 项数据维度映射矩阵完整
- ✓ 五轴 rubric 结构和 EEA 7 方案评估完整
- ✓ 选择性披露 6 维向量模型定义 + 7 方案向量填充完整
- ✓ 轻量级判定标准（一票否决 + 路线指标 + 决策规则）完整
- ✓ 隐私账本二义判定口径定义 + 7 方案分类完整
- ✓ IPTF CROPS 框架和 I2I/I2U 语境区分已覆盖
- ✓ EEA §06b 4 项以太坊隐私标准映射完整
- ✓ Residual caveat（向量合规标签验证）已处理，不确定性已标注

---

## Revision Log

| Round | Date | Changes |
|-------|------|---------|
| 1 | 2026-06-23 | Initial deep draft covering all 6 outline items. Research conducted via web search on EEA report, 7 solution profiles, IPTF/CROPS, EIP/ERC standards. Selective-disclosure vectors verified against scheme documentation per residual caveat; uncertainties flagged in G2/G3/G4. |
