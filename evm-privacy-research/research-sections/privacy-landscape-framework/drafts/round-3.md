---
topic: "EVM 隐私需求与技术全景框架 — Mantle 轻量级机构隐私方案宏观框架"
project_slug: "evm-privacy-research"
topic_slug: "privacy-landscape-framework"
github_repo: "Whisker17/multica-research"
round: 3
status: draft

artifact_paths:
  outline: "evm-privacy-research/outlines/privacy-landscape-framework.md"
  draft: "evm-privacy-research/research-sections/privacy-landscape-framework/drafts/round-3.md"
  final: "evm-privacy-research/research-sections/privacy-landscape-framework/final.md"

draft_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23"
  outline_round: 2
  outline_commit: "aaa6b479e99fb76927342b0a571a345f2d4315aa"
  items_covered: ["item-1", "item-2", "item-3", "item-4", "item-5", "item-6"]
  fields_investigated: ["eea_section_ref", "data_dimension", "trust_model", "deployment_pattern", "disclosure_vector", "compliance_mapping", "eea_solution_mapping", "mantle_relevance", "source_confidence"]
  diagrams_produced: ["diagram-1", "diagram-2", "diagram-3", "diagram-4"]
  source_requirement_coverage: "primary source (EEA report) directly fetched and cited by section; secondary sources (IPTF, scheme docs) accessed for vector verification"
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
3. **「轻量级 bolt-on」候选方案极少且需区分部署模式**：在 4 项一票否决条件（新链/VM、新桥、全节点运维、硬分叉）过滤后，候选空间极窄。COTI 存在两种截然不同的部署模式：(a) COTI-L2 模式（在 COTI L2 网络上部署或桥接资产），达到 GA 成熟度但触发 V1（新链）和 V2（新桥）一票否决，不属于轻量级；(b) COTI-Coprocessor 模式（multichain 协处理器，计划覆盖 70+ 链），架构上可能满足轻量级判定但尚未达到 GA（首笔跨链交易已通过 Axelar 完成，全面部署仍在 roadmap 阶段）。Paladin 链上合约套件模式处于轻量级~中量级边界。Linea Enterprise Validium、Prividium、Silent Data L2 和 Polygon CDK 私有链均被一票否决。
4. **COTI 部署模式决定隐私能力评估置信度**：EEA COTI 方案 profile 明确描述其 GC 技术加密 inputs、balances、on-chain state 和 smart contract logic，覆盖范围超出纯值级隐私。但这些能力的 EEA 证据（Privex $25bn、StaTwig 10M 计算、ECB Digital Euro、多次审计）全部来自 COTI-L2 模式。COTI-L2 是唯一达到 General Availability 的方案（≥3 客户跨 ≥2 机构类别、≥12 月运营、≥2 次审计）。COTI-Coprocessor 模式声称继承相同 GC 技术栈，但其在 multichain 部署下的隐私能力尚未经独立验证，成熟度判定为 Pilot。Silent Data 为 Early Production（但 EEA 强制披露未包含审计机构/日期），其余 5 方案处于 Pilot 阶段。
5. **Mantle 关键约束**：作为 institutional blockchain 追求隐私（私密转账/余额/账本），偏好「不改变基础链架构」的 bolt-on 方案。COTI-L2 虽具备最强的 GA 证据和值级+执行级（部分）隐私能力，但其部署模式要求使用 COTI L2 网络，不符合 Mantle 轻量级偏好。COTI-Coprocessor 模式在架构上与 Mantle 轻量级需求对齐，但需等待 multichain 部署成熟。本框架的 rubric 和轻量级判定标准将在后续竞品分析中直接应用。

---

## item-1: EEA 报告核心提炼 — 企业隐私 8 需求、信任模型与评估框架

### 1.1 EEA 报告基本信息

- **报告全称**: *State of Privacy on Ethereum for Enterprise*
- **发布方**: Enterprise Ethereum Alliance (EEA) Privacy Working Group
- **版本**: Version 1, April 2026
- **URL**: https://entethalliance.github.io/wg-privacy/privacy-report.html
- **访问日期**: 2026-06-23
- **参与方**: Applied Blockchain (Silent Data), Consensys (Linea), COTI, EY (Nightfall), Kaleido (Paladin), Polygon, ZKsync (Prividium)；Ethereum Foundation PSE 团队和 IPTF 亦参与贡献 [EEA 报告 §01 Opening Statement; source_confidence: EEA 报告直接引用]

### 1.2 企业隐私 8 需求综合体系

EEA 报告本身未以编号列表形式列出「8 项需求」，以下体系由研究者从 Section 04（Enterprise Privacy Problem）的 4 大屏障、Section 10（Solution Profiles）的数据保护维度、Section 11（Decision Framework）的 5 项评估问题、以及 Section 08（Trust Models）的信任-合规交叉中综合归纳 [推论; source_confidence: EEA 报告推论]。

| # | 需求 | EEA 报告来源 | 说明 |
|---|------|-------------|------|
| **R1** | 交易金额隐私 | §04 Lack of Financial Discretion; §10 各方案 "concealing transaction values" | 交易金额对非授权方不可见。COTI 通过 GC 加密值、Nightfall 通过 ZK commitments 实现 [EEA §10] |
| **R2** | 账户余额隐私 | §04 Lack of Financial Discretion; §10 COTI/Nightfall "concealing account balances" | 账户余额加密存储，仅授权方可查。ERC-7984 Confidential Fungible Token 提供标准化方案 [EEA §06b] |
| **R3** | 对手方身份隐私 | §04; §11-Q1 "counterparty identities"; §10 Stealth Addresses (ERC-5564) | 交易双方身份链接不可被公开观察。ERC-5564 Stealth Addresses + ERC-6538 Registry 提供标准化方案 [EEA §06b] |
| **R4** | 业务逻辑/合约状态隐私 | §04 Exposure of Business Logic; §10 Silent Data/Paladin/COTI "smart contract execution confidentiality" | 智能合约执行逻辑和内部状态对外不可见。Silent Data (TEE)、Paladin/Pente (ephemeral EVM)、Linea Enterprise (Private Validium)、COTI (GC encrypted computation on smart contract logic and on-chain state) 展示四种不同路径 [EEA §10] |
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
- COTI-L2 = Cryptographic (GC) + Organizational (COTI L2 网络 operator)
- COTI-Coprocessor = Cryptographic (GC) + Organizational (multichain operator + Axelar 跨链信任)
- Linea Enterprise = Cryptographic (ZK validity proof) + Organizational (permissioned sequencer)
- Paladin/Pente = Cryptographic (ephemeral EVM hashes) + Organizational (notary validation)

[source_confidence: 三类模型为 EEA 报告直接引用；混合模型分析为研究者推论]

### 1.4 Readiness Matrix

EEA 报告 §09 定义了隐私方案成熟度评估的三阶段模型。以下阶段定义直接取自 EEA 报告原文 [EEA §09; source_confidence: EEA 报告直接引用]：

| 阶段 | EEA 判定标准 |
|------|-------------|
| **Pilot** | 有可演示系统（demonstrable system）；有命名参与方或合作伙伴（named participant or partnership）；无需承载实时受监管流量（no live regulated traffic required） |
| **Early Production** | ≥1 命名客户已在生产环境上线（named customer live in production）；≥3 个月连续运营（continuous operation）；≥1 次第三方安全审计（最近 18 个月内）；处理真实资金或受监管流量（handles real-money or regulated traffic） |
| **General Availability** | ≥3 命名客户跨 ≥2 机构类别（named customers across ≥2 institution categories）；≥12 个月连续运营；≥2 次第三方审计（最近 24 个月内）；公开的交易量/TVL 或交易计数（public volume/TVL or transaction count） |

各方案成熟度评估（截至 2026 年中），基于 EEA 报告 §09 Readiness Matrix 直接判定：

| 方案 | EEA 判定 | EEA 报告证据 |
|------|---------|-------------|
| **COTI-L2** | **General Availability** | Privex（COTI 原生 DEX, $25bn aggregate volume）；StaTwig + UNICEF + 孟加拉国政府（国家级供应链, 10M 私有计算）；ECB Digital Euro Pioneer Partner。~14 个月 COTI 主网运营（自 2025-03）。审计：Sayfer Mar 2026, Sayfer Nov 2025, Hacken Aug 2025, Sayfer Apr 2025, Hacken Mar 2025。**注**：所有 GA 证据均来自 COTI L2 网络部署模式 [EEA §09 `rm-status prod`] |
| **COTI-Coprocessor** | **Pilot** | COTI V2 GC 技术栈的 multichain 协处理器模式。EEA 报告记载 "Multichain expansion to 70+ chains (planned 2026)" [EEA §10 COTI Solution Characteristics]。截至 2026-06-23，首笔跨链交易已通过 Axelar 完成，Privacy Portal 已上线用于 token 转换，但全面 multichain 部署仍处于 roadmap 阶段。无独立于 COTI L2 的命名客户或生产流量记录。成熟度判定为 Pilot（有可演示系统，有合作伙伴 Axelar，但无独立生产流量）[COTI 官方公告 2026-04; Axelar 集成公告; source_confidence: 官方文档补充 + 研究者判定] |
| **Silent Data** | **Early Production**† | Archax 代币化基金（Aberdeen, BlackRock, Fidelity, State Street）2026-02 上线；CRYOPDP/DHL SAP 奖 2025-12；Bank of England Digital Pound Lab Phase 1。**†审计信息缺口**：EEA 强制披露（Mandatory Disclosures）中 Silent Data 的 "Last audit firm + date" 字段为 "Not disclosed" [EEA §10 Silent Data Mandatory Disclosures]。Early Production 判定标准要求「≥1 次第三方安全审计（最近 18 个月内）」；Silent Data 持有 ISO/IEC 27001 认证并声称提供实时密码学证明（cryptographic attestations），但未按 EEA 强制披露格式公开审计机构和日期。此缺口不改变 EEA §09 的 Early Production 判定（EEA 自身已将其归入该阶段），但后续竞品分析应将审计透明度作为评估维度 [EEA §09 `rm-status early`; source_confidence: EEA 报告直接引用] |
| **Nightfall** | **Pilot** | [EEA §09 `rm-status pilot`] |
| **Paladin** | **Pilot** | Bank of Indonesia Digital Rupiah (Project Garuda) PoC；HKMA eHKD Phase 2；Banco Central do Brasil Drex（均为 PoC 阶段）[EEA §09 `rm-status pilot`] |
| **Linea Enterprise** | **Pilot** | SWIFT 合作（private testnet, 12+ 银行参与）；Linea Enterprise 仍处于 pilot 阶段（公共 Linea 主网自 2023-07 但为不同产品）[EEA §09 `rm-status pilot`] |
| **Prividium** | **Pilot** | [EEA §09 `rm-status pilot`] |
| **Polygon CDK** | **Pilot** | T-REX Ledger: Apex Group $100B tokenized RWAs, 使用 Zama FHE + ERC-3643（2026-03 公布）[EEA §09 `rm-status pilot`] |

[source_confidence: 阶段定义和各方案判定均直接取自 EEA 报告 §09 Readiness Matrix HTML 结构（`rm-status prod` / `rm-status early` / `rm-status pilot` CSS class 和对应证据文本），访问日期 2026-06-23]

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
| ⑤ 业务逻辑隐藏 (R4) | **强** | **中** | 中 | **强** | 中 | 中 |
| ⑥ 合约状态隐藏 (R4) | **强** | **中** | 弱 | **强** | 中 | 中 |
| ⑦ 订单流/mempool (R8) | 弱 | 弱 | 中 | **强** | 中 | 弱 |

**评分标准说明**：
- **强**：该技术家族的核心能力直接覆盖该维度，有成熟实现
- **中**：可以实现但非核心优势，或需与其他技术组合
- **弱**：基本不覆盖或仅提供有限保护
- 不适用：该技术家族在原理上无法提供保护（本矩阵中未出现此情况）

**GC 在业务逻辑/合约状态维度的评分说明（Round 2 修订）**：GC 作为通用技术家族，其核心能力是两方加密计算，理论上支持任意布尔电路。在 ⑤ 业务逻辑和 ⑥ 合约状态维度上评为「中」，因为 GC 的计算复杂度与电路规模线性相关，通用智能合约逻辑的电路化成本较高。然而 COTI 的具体实现通过工程优化实现了 EVM 兼容的 GC 执行框架——EEA COTI 方案 profile 明确声称 "sensitive data including inputs, balances, on-chain state, and smart contract logic, remains encrypted end-to-end" [EEA §10 COTI Solution Profile]。因此 GC 技术家族的通用评分为「中」，但 COTI 的方案级评分在轴 2 中根据 EEA 证据独立调整（见 item-3 §3.2）。[source_confidence: EEA 报告直接引用 + 研究者分析]

**关键观察**：

1. **FHE 和 TEE** 在值级+执行级隐私上表现最全面（5/7 强），但在身份/图结构上较弱（需组合 ZKP/stealth addresses）。FHE 在订单流保护上较弱，因其关注的是链上状态加密而非 pre-confirmation 阶段 [EEA §06; 推论]。

2. **ZKP** 在身份/图结构隐私上独具优势（stealth addresses、ring signatures），但在业务逻辑和合约状态隐私上需要电路化全部逻辑（constraint 数量爆炸），目前仅 Aztec 实现了通用 private functions [EEA §10; Aztec 官方文档]。

3. **GC** 是 COTI 的核心技术路线，声称计算速度比 FHE 快 1000×、体积轻 250×。GC 在金额/余额隐藏上表现强。EEA COTI profile 进一步描述其支持 "programmable privacy" 和 "encrypted computation" 覆盖 on-chain state 和 smart contract logic，使 COTI 成为 GC 路线中唯一实现了执行级隐私的方案 [EEA §10 COTI Solution Profile; source_confidence: EEA 报告直接引用]。

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
| **值级隐私** (Value-Level) | 仅 token 转账金额/余额 | Nightfall ZK commitments、ERC-7984 | ZKP commitments / FHE encrypted state |
| **执行级隐私** (Execution-Level) | 全智能合约执行逻辑 | Silent Data TEE 全执行隐私、Paladin/Pente ephemeral EVM、Aztec private functions、COTI GC encrypted computation（开发者标注机密参数的 Solidity 合约）| TEE 隔区执行 / ephemeral 沙盒 EVM / ZK circuits / GC 加密电路 |
| **状态级隐私** (State-Level) | 链上状态完全不可观察 | Linea Enterprise Validium (状态不外泄)、Prividium permissioned L2 (仅 state root 上链) | Validium (链下 DA) / permissioned DA / 独立 VM |

**关键区别**：值级隐私保护的是「数字」（amount/balance），执行级隐私保护的是「计算」（logic/execution），状态级隐私保护的是「存储」（on-chain state）。一个方案可能同时覆盖多个层级——例如 Prividium 和 Polygon CDK 在 permissioned L2 模式下同时隐藏值和执行（A+B 兼备），但其隐私来源不同（Prividium = 准入控制 + ZK validity proof, Polygon CDK = 可配置 FHE/TEE/Validium）[EEA §10; 推论]。

**COTI 隐私层级说明（Round 2 修订，Round 3 部署模式拆分）**：Round 1 将 COTI 归为纯值级隐私，Round 2 基于 EEA 报告修正为值级 + 执行级（部分）。EEA COTI 方案 profile 明确声称 GC 技术加密 "inputs, balances, on-chain state, and smart contract logic"，并描述 COTI 为 "programmable privacy layer"，支持 "Standard Solidity (Fully EVM compatible) with parameters specifying confidential data elements" [EEA §10 COTI Solution Profile]。

**Round 3 关键区分——部署模式影响隐私层级置信度**：
- **COTI-L2 模式**：上述隐私能力（值级 + 执行级部分）的全部 EEA 证据来自 COTI L2 网络部署。该模式要求 "Deploy on COTI network or bridge existing assets" [EEA §10 COTI Integration Requirements]，使用 COTI L2 网络为前提 [EEA §10 COTI Commercial Model: "use of COTI L2 network required"]。隐私层级归类：值级 + 执行级（部分），置信度高（GA 证据充分）。
- **COTI-Coprocessor 模式**：COTI 声称将 V2 GC 技术栈以 multichain 协处理器形式扩展至 70+ 链 [EEA §10 COTI Solution Characteristics: "Multichain expansion to 70+ chains (planned 2026)"]。该模式声称继承相同 GC 隐私能力，但截至 2026-06-23 仅完成首笔跨链交易（via Axelar），隐私能力在 multichain 部署下未经独立验证。隐私层级归类：值级 + 执行级（部分, announced），置信度低（Pilot 阶段，能力声称但未独立验证）。

两种模式的隐私层级归类均与 Silent Data TEE 的全自动执行隐私不同——COTI 要求开发者在 Solidity 合约中显式标注哪些参数是机密的 [EEA §10; source_confidence: EEA 报告直接引用 + 研究者分析]。

### 2.5 EEA 7 方案技术家族标签

| 方案 | 主技术家族 | 辅助/混合 | 隐私层级 |
|------|-----------|---------|---------|
| **COTI-L2** | GC | 探索 ZKP (Nightfall 集成)、MPC | 值级 + 执行级（部分） |
| **COTI-Coprocessor** | GC (announced) | — (multichain 模式下的辅助集成未明确) | 值级 + 执行级（部分, announced）† |
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
| COTI-L2 | GC | 不需要 | GC 本身不受量子威胁 [推论] | +ZKP (Nightfall 集成) |
| COTI-Coprocessor | GC (announced) | 不需要 | GC 本身不受量子威胁 [推论] | — (multichain 模式辅助集成未明确) |
| Nightfall | ZKP | 取决于 proof system | ZK 向后量子友好方案迁移 [推论] | +X.509 PKI |
| Paladin | PG + ZKP | Zeto: 取决于 ZK scheme | 未明确 | +Notary +Ephemeral EVM |
| Silent Data | TEE | 不需要 | TEE 不受量子直接威胁但依赖传统加密通道 [推论] | +OP Stack |
| Linea Enterprise | ZKP | 取决于 gnark prover | ZK-SNARK 体系受量子威胁，计划 RISC-V zkVM 迁移 | +PG (permissioned) |
| Prividium | ZKP | 取决于 ZK Stack | 未明确 | +PG (RBAC) |
| Polygon CDK | 可配置 | 取决于模块选择 | 支持 FHE (Zama 集成) → 较好 | FHE/TEE/ZKP 可选 |

#### 轴 2 — 被保护数据维度评估

| 方案 | 金额(R1) | 余额(R2) | 身份(R3) | 图(R5) | 逻辑(R4) | 状态(R4) | 订单流(R8) |
|------|:--------:|:--------:|:--------:|:------:|:--------:|:--------:|:---------:|
| COTI-L2 | ● | ● | ◐ | ◐ | ◐ | ◐ | ○ |
| COTI-Coprocessor | ●† | ●† | ◐† | ◐† | ◐† | ◐† | ○ |
| Nightfall | ● | ● | ◐ | ◐ | ○ | ○ | ○ |
| Paladin | ● | ● | ◐ | ○ | ◐ | ◐ | ○ |
| Silent Data | ● | ● | ◐ | ◐ | ● | ● | ◐ |
| Linea Enterprise | ● | ● | ◐ | ◐ | ● | ● | ◐ |
| Prividium | ● | ● | ◐ | ◐ | ● | ● | ◐ |
| Polygon CDK | ● | ● | ◐ | ◐ | ◐→● | ◐→● | ◐ |

● = 完全保护 ◐ = 部分保护 ○ = 不保护
† = COTI-Coprocessor 标注：评分继承自 COTI-L2 的 GC 技术栈能力声称，但 multichain 协处理器模式下的隐私能力尚未经独立验证（Pilot 阶段）。实际评分需待 Coprocessor 模式 GA 后重新验证。

**评分依据**：
- **金额/余额**：所有方案均提供完全保护（核心卖点）[EEA §10]
- **身份**：COTI-L2/COTI-Coprocessor/Nightfall/Paladin 在 permissioned 模型下提供身份隔离但非密码学匿名（标记 ◐）；Silent Data/Linea/Prividium 在封闭网络内身份仅对成员可见 [各方案官方文档]
- **图结构**：COTI-L2 GC/Nightfall ZK 提供交易级 unlinkability 但 deposit/withdraw 暴露关联（◐）；COTI-Coprocessor 继承相同 GC 架构声称（◐†）；PG 方案在组内透明组外不可见（◐）；Paladin notary 模型下 notary 可见全图（○）[推论]
- **业务逻辑/合约状态（Round 2 修订，Round 3 部署模式拆分）**：
  - **COTI-L2**: Round 1 评为 ○（不保护），Round 2 修订为 ◐（部分保护）。EEA COTI 方案 profile 明确声称 "sensitive data including inputs, balances, on-chain state, and smart contract logic, remains encrypted end-to-end across storage, computation and transmission" [EEA §10 COTI Solution Profile]。COTI 的 GC 框架支持 "Standard Solidity (Fully EVM compatible) with parameters specifying confidential data elements"，即开发者在 Solidity 合约中标注机密参数，GC 引擎对这些参数进行加密计算。评为 ◐ 而非 ● 的原因：COTI 要求开发者显式标注机密数据元素，而非像 Silent Data TEE 那样自动保护全部执行逻辑。此评分基于 COTI L2 网络部署的 EEA 证据，置信度高 [source_confidence: EEA 报告直接引用 + 研究者分析]。
  - **COTI-Coprocessor**: 评分继承 COTI-L2 的 ◐（部分保护），标注为 ◐†。COTI 声称 multichain 协处理器将同一 GC 技术栈带到宿主链，"Developers can integrate COTI's privacy capabilities without altering their existing architectures" [COTI 官方公告 2026-04]。但该模式截至 2026-06-23 仅完成首笔跨链交易（via Axelar），业务逻辑/合约状态的加密计算能力在 multichain 部署下未经独立验证。置信度低，需待 Coprocessor 模式成熟后重新评估 [source_confidence: 官方文档补充 + 研究者判定]。
  - **Silent Data/Linea/Prividium**: ●（完全保护）——TEE/Validium/permissioned L2 自动保护全部执行和状态 [EEA §10]
  - **Paladin/Pente**: ◐（部分保护）——ephemeral EVM 在隐私域内执行合约但域内参与方可见 [Paladin Docs]
  - **Nightfall**: ○（不保护）——聚焦值级隐私（ZK commitments for token transfers），不覆盖通用合约逻辑 [EEA §10]
- **订单流**：所有方案的 pre-confirmation 保护取决于 sequencer/mempool 设计而非隐私层本身。Silent Data TEE 执行环境提供 operator 级保护；Linea/Prividium permissioned sequencer 提供准入级保护（◐）；其他方案不专门保护 [推论]

[source_confidence: COTI 维度修订基于 EEA 报告 §10 COTI Solution Profile 直接引用；其余评分为研究者基于 EEA 报告 §10 方案描述 + 各方案官方文档综合判断]

#### 轴 3 — 信任模型评估

| 方案 | 主信任模型 | 信任假设清单 |
|------|-----------|------------|
| COTI-L2 | Cryptographic + Organizational | GC 安全假设、COTI L2 网络 operator 诚信、密钥管理方诚信 |
| COTI-Coprocessor | Cryptographic + Organizational | GC 安全假设、multichain operator 诚信、Axelar 跨链桥信任、密钥管理方诚信 |
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
| COTI-L2 | 独立 L2 网络 (COTI L2 + 资产桥) | **一票否决** | item-5 |
| COTI-Coprocessor | Bolt-on 协处理器 (multichain) | **候选通过**（非 GA） | item-5 |
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
| `revocable` | 可撤销授权（已有技术文档确认机制） | GDPR right to be forgotten |
| `unverified-revocable` | 声称可撤销但未有公开技术文档确认具体机制 | GDPR 合规待验证 |
| `permanent` | 永久授权 | — |
| `auditable-log` | 披露行为有审计日志（已有技术文档确认实现） | 金融审计要求 |
| `partial-auditable-log` | 声称有审计追踪能力但具体实现细节（日志格式、存储、不可篡改保证）未经公开技术文档确认 | 金融审计合规待验证 |

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

**残余 caveat 处理**：Outline review 要求「验证每个 selective-disclosure example vector 的合规标签（revocability, auditability），尤其是 COTI、Paladin/Noto、Nightfall、Linea Enterprise 的具体文档/版本」。以下逐方案标注证据来源。Round 2 对不确定性标签做了显式降级处理（见 COTI revocability 和 Paladin auditability）。

#### COTI（适用于 COTI-L2；COTI-Coprocessor 继承相同设计但 multichain 模式下未独立验证）

**部署模式说明（Round 3）**：以下选择性披露向量基于 EEA §10 COTI Solution Profile 和 COTI 官方文档，其证据全部来自 COTI L2 网络部署。COTI-Coprocessor 模式声称将相同的 GC 隐私栈（包括 view-key 机制）带到宿主链，因此在架构层面应继承相同向量。但 Coprocessor 模式的实际向量实现（特别是 view-key 在跨链场景下的行为、以及 Axelar 跨链层引入的额外泄露风险）尚未经独立验证。后续竞品分析应分别验证两种模式的向量。

| 维度 | 标签 | 证据 |
|------|------|------|
| a-Authority | `key-holder` | COTI 通过 permissioned view-keys 实现选择性披露，密钥持有者自主决定向谁分发。EEA 报告描述："Programmable smart contracts allow selective disclosure for audits, compliance, or permissions via permissioned view-keys." [EEA §10 COTI Solution Profile; source_confidence: EEA 报告直接引用] |
| b-Trigger | `viewing-key-share` | 通过分发 viewing key 给指定对手方/审计方触发。EEA 报告描述："Institutions can granularly select, on a per party basis, which participants have access to decryption rights." [EEA §10 COTI Solution Profile; COTI 官方文档] |
| c-Payload | `amount+identity` | COTI 「doesn't just hide amounts — it hides who transacted and what was traded」，但可向 right parties 披露交易详情 [COTI Medium, 2026] |
| d-Scope | `per-tx`, `per-account` | View-key 可针对单笔交易或账户级别分发 [推论，基于 COTI view-key 设计] |
| e-Revocability | `unverified-revocable`* | COTI 在市场材料中声称支持可撤销的隐私授权和 GDPR 合规，但截至 2026-06-23 未找到描述具体撤销机制的技术白皮书或文档版本。Round 1 标记为 `revocable*` 附不确定性标注；Round 2 降级为 `unverified-revocable`——承认 COTI 的 revocability 声明但明确标注其技术实现未经独立验证。后续竞品分析 issue 需查阅 COTI 技术文档或直接联系确认。[source_confidence: 官方文档补充 + 未验证] |
| f-Leakage | `existence`, `timing` | 链上 commitment/交易记录存在性和时序模式对公众可见 [推论] |

#### Paladin/Noto

| 维度 | 标签 | 证据 |
|------|------|------|
| a-Authority | `notary/observer`, `key-holder` | Noto 采用 notary-based validation，公证方（或公证方集合）预验证并共签每笔交易；同时隐私域内成员可持有密钥 [LF Decentralized Trust 博客 "Announcing Paladin", 2025-02; Kaleido Webinar Slides, 2025; source_confidence: 官方文档补充] |
| b-Trigger | `automatic`, `compliance-gate` | Notary 自动获取交易数据进行验证（automatic）；域成员准入可设置合规门控（compliance-gate）[Kaleido Paladin 文档] |
| c-Payload | `all` | 域内参与方和 notary 可见全部交易数据（amounts, identities, logic）[Paladin 架构设计: ephemeral EVM 在域内执行全部合约逻辑] |
| d-Scope | `domain-wide` | 隐私域（privacy domain）为作用范围，域内成员共享完整视图 [Paladin Docs] |
| e-Revocability | `partial-auditable-log`* | Round 1 标记为 `auditable-log`；Round 2 降级为 `partial-auditable-log`。Paladin 明确设计为 Project Guardian 等银行间场景服务，审计性是设计目标。Notary 验证过程必然产生日志记录。但截至 2026-06-23，具体 `auditable-log` 实现的技术细节（日志格式、存储位置、不可篡改保证、查询接口）未在 Paladin 公开技术文档中找到确认。标记为 `partial`——承认审计追踪能力的设计意图和 notary 架构的固有审计属性，但具体实现待验证。[LF Decentralized Trust, 2025-11; Paladin 架构文档; source_confidence: 官方文档补充 + 部分未验证] |
| f-Leakage | `existence` | 链上记录 state commitments（masked account state hashes），交易存在性可见但内容不可推断 [Paladin 架构: "records output state commitments to the underlying blockchain"; source_confidence: 官方文档补充] |

#### Nightfall (EY)

| 维度 | 标签 | 证据 |
|------|------|------|
| a-Authority | `key-holder` | 通过 viewing key 向指定方披露交易详情 [EY Nightfall 官方新闻稿 "EY upgrades Nightfall", 2025-04; source_confidence: 官方文档补充] |
| b-Trigger | `compliance-gate`, `viewing-key-share` | X.509 企业级证书为 deposit/withdraw 准入门控（compliance-gate）；viewing key 可分发给审计方（viewing-key-share）[EY Nightfall 公告; zk-X509 论文 arXiv:2603.25190, 2026-03] |
| c-Payload | `amount+identity` | Nightfall 在 Starknet 集成中支持 "confidential B2B payments" 披露金额和身份信息 [Starknet-Nightfall 公告, 2026-02] |
| d-Scope | `per-tx` | Viewing key 按交易级别授权 [推论，基于 Nightfall ZK commitment 结构] |
| e-Revocability | `one-time`* | Viewing key 分发后接收方可保留；当前公开文档未描述显式撤销机制 [source_confidence: EEA 报告推论 + 不确定性标注] |
| f-Leakage | `graph`, `existence` | ZK rollup 的 deposit/withdraw 操作关联了 L1 和 L2 地址，交易图部分可推断；交易存在性（commitment 上链）可见 [推论，基于 ZK rollup 架构特性] |

**Nightfall revocability 不确定性说明**：Nightfall 当前公开文档（截至 2026-06-23）未描述 viewing key 的显式撤销机制。一旦 viewing key 被分发，接收方在技术上可保留该密钥。GDPR right to be forgotten 要求可能需要额外的密钥轮换机制来实现「等效撤销」。标记为 `one-time` 附不确定性标注。此标签未做 Round 2 降级处理，因为 `one-time` 本身已是保守评估（不声称可撤销）；Orchestrator 评审确认此处无需进一步修改（non-blocking）。

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
| COTI-L2 | key-holder | viewing-key-share | amount+identity | per-tx, per-account | unverified-revocable* | existence, timing |
| COTI-Coprocessor | key-holder† | viewing-key-share† | amount+identity† | per-tx, per-account† | unverified-revocable*† | existence, timing + 跨链路由泄露† |
| Paladin/Noto | notary/observer, key-holder | automatic, compliance-gate | all | domain-wide | partial-auditable-log* | existence |
| Nightfall | key-holder | compliance-gate, viewing-key-share | amount+identity | per-tx | one-time* | graph, existence |
| Linea Enterprise | smart-contract, notary/observer | automatic | all | domain-wide | permanent (RBAC) | none |
| Prividium | smart-contract, regulator | compliance-gate, audit-request, automatic | all | per-contract, chain-wide | permanent, auditable-log | none |
| Polygon CDK | smart-contract, notary/observer | compliance-gate, automatic | all | chain-wide | permanent | none/existence |
| Silent Data | smart-contract | automatic | all | chain-wide | permanent, auditable-log | existence |

\* 附不确定性标注，详见各方案向量说明。Round 2 修订：COTI `revocable*` → `unverified-revocable*`（声称可撤销但技术机制未经公开文档确认）；Paladin `auditable-log` → `partial-auditable-log*`（审计追踪设计意图明确但具体实现待验证）。

† COTI-Coprocessor 标注：向量继承自 COTI-L2 的 GC 技术栈设计，但 multichain 协处理器模式下的实际向量行为未经独立验证（Pilot 阶段）。额外注意：Coprocessor 模式的跨链路由层（Axelar）可能引入 COTI-L2 不存在的残余泄露维度（跨链消息的路由可观察性）。

### 4.5 合规映射

将 6 维向量映射到具体合规要求 [source_confidence: 研究者分析，基于 EEA §11 和监管框架]：

| 合规要求 | 向量约束 | 满足方案 | 部分满足 | 不满足 |
|---------|---------|---------|---------|--------|
| **GDPR right to be forgotten** | 维度 e 包含 `revocable`（已验证机制） | （无方案完全满足） | COTI-L2/COTI-Coprocessor (unverified-revocable — 声称支持但机制未验证) | Nightfall (one-time)、Paladin/Linea/Prividium/CDK/Silent Data (permanent) |
| **MiCA / Travel Rule** | 维度 a 包含 `regulator` 或 `smart-contract` + 维度 c 包含 `identity` | Prividium, Polygon CDK | — | COTI-L2/COTI-Coprocessor (key-holder only, 需 regulator 主动请求 key) |
| **AML/CFT** | 维度 b 包含 `compliance-gate` 或 `audit-request` | Nightfall, Prividium, Polygon CDK | — | COTI-L2/COTI-Coprocessor (无 compliance-gate, 依赖 key-holder 自愿), Silent Data (automatic only) |
| **金融审计** | 维度 e 包含 `auditable-log`（已验证实现） | Prividium, Silent Data† | Paladin (partial-auditable-log — 审计设计意图明确但实现细节未验证) | COTI-L2/COTI-Coprocessor (无明确审计日志), Nightfall (无明确审计日志) |

**Round 2 合规映射修订说明**：
- **COTI GDPR**: Round 1 将 COTI 列为满足 GDPR（基于 `revocable*`）；Round 2 降级为「部分满足」，因为 COTI 的 revocability 声明缺少公开技术文档确认具体撤销机制（key rotation? access revocation? data deletion?）。在 GDPR 合规评估中，未经验证的声称不能等同于满足。Round 3 将此评估拆分适用于 COTI-L2 和 COTI-Coprocessor 两种模式——两者均继承 `unverified-revocable` 标签。
- **Paladin 金融审计**: Round 1 将 Paladin 列为满足金融审计（基于 `auditable-log`）；Round 2 降级为「部分满足」，因为 Paladin 的 notary 架构固有审计追踪属性且明确以 Project Guardian 银行间场景为设计目标，但具体审计日志实现的技术细节（格式、不可篡改性、查询接口）未在公开文档中找到确认。
- **Silent Data 金融审计（Round 3 新增 †）**: Silent Data 列为满足金融审计（基于 `auditable-log` + ISO/IEC 27001 认证），但需注意 EEA 强制披露中 Silent Data 的 "Last audit firm + date" 为 "Not disclosed"。ISO/IEC 27001 认证和 cryptographic attestations 为审计日志提供了制度基础，但审计机构和时间的缺失意味着后续竞品分析应进一步核实其审计透明度。

**Mantle 启示（Round 3 修订）**：作为 institutional blockchain，Mantle 需要方案同时满足 MiCA/Travel Rule（identity 披露给监管方）和金融审计（auditable-log）要求。当前方案中，Prividium 在合规向量上最完整（支持 regulator + compliance-gate + audit-request + auditable-log），但其部署形态（独立 L2）不符合 Mantle 轻量级偏好。COTI-Coprocessor 作为唯一可能通过轻量级判定的 COTI 模式，合规能力存在待验证缺口（revocability 未验证、无 auditable-log）且处于 Pilot 阶段；COTI-L2 虽有最强 GA 证据但触发轻量级一票否决。Paladin 的 auditable-log 实现同样需进一步技术验证。

---

## item-5: 部署形态分类与「轻量级」判定标准

### 5.1 部署形态三级分类

#### diagram-4: 部署形态谱 — 从 Bolt-on 到独立链

> 线性谱图：左端（轻量级）→ 右端（重量级）

```
轻量级 ←———————————————————————————————————————————————→ 重量级

  COTI-         Paladin    Nightfall       COTI-L2    Silent Data    Linea Ent.    Prividium    Polygon CDK
  Coprocessor   sidecar+   ZK rollup      L2/桥接     TEE L2         Validium      Permissioned  Private
  multichain    verifiers   contracts     模式        (Superchain)    (Lineth)      L2 (ZK Stack) chain
  ──────────   ──────────  ──────────     ──────────  ──────────     ──────────    ──────────    ──────────
  Bolt-on       合约套件    合约套件        独立L2       独立链          独立链         独立链         独立链
  协处理器                  (重型)         (需COTI网络)
  (非GA)
                                          ← 轻量级阈值线 →
```

**A. Bolt-on 协处理器**：不改变基础链架构，通过外部计算模块提供隐私能力。
- **COTI-Coprocessor（multichain 模式）**：计划将 V2 GC 技术栈以协处理器形式覆盖 70+ 链，GC 计算在链下执行，链上部署隐私合约接口。集成方无需运维额外基础设施。EEA 报告记载此扩展为 "planned 2026" [EEA §10 COTI Solution Characteristics]。截至 2026-06-23，首笔跨链交易已通过 Axelar 完成，但全面 multichain 部署仍处于 roadmap 阶段。**重要区分**：EEA §10 COTI Integration Requirements 描述的 "Deploy on COTI network or bridge existing assets" 和 Commercial Model 中 "use of COTI L2 network required" 指的是 COTI-L2 模式（见下方 C 类），而非此协处理器模式 [source_confidence: EEA 报告直接引用 + 官方文档补充 + 研究者分析]。
- **Zama fhEVM coprocessor**（EEA 7 方案之外的参考）：FHE 运算由链下 coprocessor 异步执行，链上仅处理加密 handle。host chain 无需修改 [Zama Docs; source_confidence: 官方文档补充]。

**B. 链上合约套件**：在现有 EVM 链上部署隐私合约集 + sidecar 服务。
- **Paladin**：sidecar node + on-chain verifiers。Noto 域需要 notary node；Pente 域需要 ephemeral EVM runtime。核心合约部署在宿主链上，隐私执行在 sidecar 中完成 [Paladin Docs; LF Decentralized Trust]。
- **Nightfall**：ZK rollup 合约套件。需要 rollup operator 运行 sequencer + prover + 验证合约。集成复杂度中等偏重 [EY Nightfall 公告; source_confidence: 官方文档补充]。

**C. 独立链或 VM**：独立运行的隐私链/L2/L3。
- **COTI-L2（L2/桥接模式）**：在 COTI L2 网络上运行，资产通过桥接迁移。EEA §10 Integration Requirements 明确要求 "Deploy on COTI network or bridge existing assets"，Commercial Model 确认 "use of COTI L2 network required" [EEA §10 COTI Solution Profile]。所有 GA 级证据（Privex、StaTwig、ECB 等）均来自此模式。从 Mantle 集成视角看，此模式要求 Mantle 用户在 COTI L2 上操作或通过桥迁移资产，触发 V1（新链）和 V2（新桥）一票否决 [source_confidence: EEA 报告直接引用]。
- **Silent Data**：TEE L2 on Optimism Superchain。需要运维独立 L2 节点 + TEE 隔区 [Silent Data 官方]。
- **Linea Enterprise**：Validium/permissioned L2 on Lineth stack。需要运维 Besu 执行节点 + Maru 共识 + coordinator + gnark prover [LF Decentralized Trust "Announcing Lineth"]。
- **Prividium**：Permissioned L2 on ZK Stack。需要运维 ZK Stack 全套 + Proxy RPC + Admin Dashboard + IdP 集成 [ZKsync Prividium Docs]。
- **Polygon CDK**：Private chain/validium。需要运维 CDK 全套 + Gateway + permissioned explorer [Polygon CDK Docs]。

### 5.2 一票否决条件

任一条满足即**不可**归类为「轻量级」[source_confidence: 研究者设计，基于 EEA 报告框架推论]：

| 否决条件 | 说明 | 被否决方案 |
|---------|------|----------|
| **V1: 需要部署新 L1/L2/L3/sidechain 或独立 VM** | 集成方须运维独立链基础设施 | COTI-L2 (需 COTI L2 网络), Silent Data (TEE L2), Linea Enterprise (Validium), Prividium (permissioned L2), Polygon CDK (private chain) |
| **V2: 需要新的资产桥 (asset bridge)** | 用户资产须跨桥迁移，引入桥安全风险和流动性碎片化 | COTI-L2 ("bridge existing assets"), 所有独立链方案 (Silent Data, Linea Enterprise, Prividium, Polygon CDK) |
| **V3: 集成方须运维 sequencer/prover/DA 全节点** | 运维成本超出应用层集成范畴 | Nightfall (需 rollup operator), 所有独立链方案 |
| **V4: 需要基础链硬分叉或共识层修改** | 协议层变更，超出应用层范畴 | EIP-8105 encrypted mempools（需 Ethereum 协议升级）|

### 5.3 通用成本指标

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| 链上存储增长 | 不增加或仅增加 commitments/proofs | 增加验证合约 + 状态 | 需要独立 DA 层 |
| 运维复杂度 | 无额外节点 | 1-2 sidecar 服务 | 完整链运维 |
| 基础链侵入性 | 无修改 | precompile/合约部署 | fork 或独立链 |
| 部署时间线 | <3 个月 | 3-9 个月 | >9 个月 |

**通用指标局限性说明（G5 相关）**：上述阈值（如 <3 个月部署时间线、「无额外节点」等）为基于行业经验和 EEA 报告方案描述的理论划分，不基于具体方案的 benchmark 数据。各方案的实际部署时间线和运维复杂度可能因集成场景、团队经验和基础设施现状而有显著差异。后续竞品分析 issue 中应收集各方案的实际部署案例数据来校准这些阈值。

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

**路线专属指标局限性说明（G5 相关）**：上述路线专属阈值（如 ZK 约束数 10^6 分界、FHE 密文膨胀率 10x 分界等）为基于密码学文献和行业标准的理论划分，各方案的实际性能数据可能偏离这些理论值。后续竞品分析 issue 应优先收集各方案的 benchmark 数据以校准分界。

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
| COTI-L2 | **✓**(需 COTI L2 网络) | **✓**(需桥接资产) | ✗ | ✗ | **否决** | — | — | **中量级~重量级** |
| COTI-Coprocessor | ✗ | ✗ | ✗ | ✗ | 通过 | 通过 | GC: 通过 | **轻量级**（非 GA） |
| Nightfall | ✗ | ✗ | **✓**(需 rollup operator) | ✗ | **否决** | — | — | **中量级** |
| Paladin | ✗ | ✗ | ✗ (sidecar, 非全节点) | ✗ | 通过 | 部分通过 | PG: 通过; ZK: 取决于 Zeto 选择 | **轻量级~中量级** |
| Silent Data | **✓** | **✓** | **✓** | ✗ | **否决** | — | — | **重量级** |
| Linea Enterprise | **✓** | **✓** | **✓** | ✗ | **否决** | — | — | **重量级** |
| Prividium | **✓** | **✓** | **✓** | ✗ | **否决** | — | — | **重量级** |
| Polygon CDK | **✓** | **✓** | **✓** | ✗ | **否决** | — | — | **重量级** |

**COTI-L2 判定说明（Round 3 新增）**：COTI-L2 模式要求在 COTI L2 网络上部署或桥接资产。EEA §10 Integration Requirements 明确描述 "Deploy on COTI network or bridge existing assets"，Commercial Model 确认 "use of COTI L2 network required" [EEA §10 COTI Solution Profile]。从 Mantle 集成视角看，此模式触发 V1（需要 COTI L2 网络 = 新链/独立网络）和 V2（需要资产桥）一票否决。所有 COTI GA 级证据（Privex $25bn、StaTwig 10M、ECB、14 个月主网、5 次审计）均来自此模式。判定为中量级~重量级。

**COTI-Coprocessor 判定说明（Round 3 修订）**：COTI 声称将 V2 GC 技术栈以 multichain 协处理器形式扩展至 70+ 链 [EEA §10: "Multichain expansion to 70+ chains (planned 2026)"]。在此模式下，GC 计算由 COTI 协处理器网络执行，宿主链上仅部署隐私合约接口——集成方不需要部署新链、新桥或全节点运维，不需要硬分叉。GC 路线指标（1-2 轮交互、低带宽）满足轻量级。但此模式截至 2026-06-23 仅完成首笔跨链交易（via Axelar），成熟度为 Pilot，无独立于 COTI L2 的命名客户或生产流量记录。判定为轻量级（部署形态），但非 GA（成熟度），后续评估需跟踪 Coprocessor 模式的生产验证进展。Round 2 修订关于 R4 覆盖的内容（GC 框架支持对标注的合约逻辑和状态进行加密计算）在 COTI-Coprocessor 模式下为 announced 但未独立验证 [source_confidence: EEA 报告直接引用 + 官方文档补充 + 研究者分析]。

**Paladin 判定说明**：Paladin sidecar 不等同于「全节点运维」（V3），因为它是应用层服务而非链基础设施。但 Noto notary 节点和 Pente ephemeral EVM runtime 增加了运维复杂度，处于轻量级和中量级边界。最终判定取决于具体 Paladin 域类型选择。

**Nightfall 判定说明**：Nightfall 作为 ZK rollup，虽然不需要部署新链，但 rollup operator 需要运维 sequencer + prover。Nightfall_4 (2025 升级) 声称「near-instant finality」和性能提升，但 prover 基础设施仍属 V3 范畴（集成方须运维 prover 节点）。在 Starknet 集成模式下，Starknet 负责 prover，集成方可降低运维负担 → 此路径下可能降至中量级上界 [推论]。

**Mantle 启示（Round 3 修订——部署模式条件化）**：将 COTI 拆分为 COTI-L2 和 COTI-Coprocessor 后，轻量级判定的格局发生显著变化：

1. **COTI-L2**（GA，中量级~重量级）：具备最强的成熟度证据和值级+执行级（部分）隐私能力，但其部署模式（需 COTI L2 网络 + 资产桥）触发 V1/V2 一票否决，不符合 Mantle 轻量级偏好。
2. **COTI-Coprocessor**（Pilot，轻量级）：架构上满足 bolt-on 协处理器模式（无新链、无新桥、无全节点），通过轻量级判定。但成熟度为 Pilot（仅首笔跨链交易），隐私能力在 multichain 部署下未经独立验证。Mantle 如选择此路径，需承担技术成熟度风险。
3. **Paladin**（Pilot，轻量级~中量级）：处于轻量级和中量级边界。

**核心结论**：Mantle 面临「轻量级部署 vs 生产成熟度」的 tradeoff——满足轻量级判定的 COTI-Coprocessor 尚处 Pilot 阶段，而具备 GA 证据的 COTI-L2 不满足轻量级判定。候选空间极窄。如果扩展到 EEA 7 方案之外，Zama fhEVM coprocessor 也是 bolt-on 架构的候选（链下 FHE 运算 + 链上 encrypted handle），但 FHE 性能开销（当前 ~20 TPS on CPU）是关键瓶颈。

---

## item-6: 「隐私账本」二义判定口径与范围边界

### 6.1 二义性定义

在企业隐私语境中，「隐私账本」（Private Ledger）存在两种截然不同的含义 [source_confidence: 研究者分析，基于 EEA 报告 §10 方案描述推论]：

#### A. 私密 Token Ledger（值级账本）

- **隐藏的对象**：token 转账金额、账户余额、转账对手方
- **隐喻**：「看不见数字的银行流水」
- **典型方案**：
  - Nightfall: ZK commitments for ERC-20/721/1155 [EY Nightfall 公告, 2025-04]
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
- **COTI-L2（Round 2 修订，Round 3 部署模式拆分）**: A + B（部分）。Round 1 归为纯 A (Token Ledger)。Round 2 基于 EEA 报告修正：COTI 的 GC 框架不仅支持 token 值加密（A），还支持 "Standard Solidity (Fully EVM compatible) with parameters specifying confidential data elements" 对合约逻辑和状态进行加密计算。但与 Silent Data TEE 或 Paladin/Pente 的全自动执行隐私不同，COTI 要求开发者显式标注机密参数，因此归类为 A + B（部分）。此分类基于 COTI L2 网络部署的 EEA 证据，置信度高 [EEA §10 COTI Solution Profile; source_confidence: EEA 报告直接引用]。
- **COTI-Coprocessor（Round 3 新增）**: A + B（部分, announced）。声称将同一 GC 技术栈以 multichain 协处理器形式部署到宿主链，因此在架构层面应继承 COTI-L2 的 A + B（部分）分类。但此模式截至 2026-06-23 处于 Pilot 阶段，token ledger 和 business-state ledger 能力在 multichain 部署下未经独立验证。标注为 "announced" 以区分置信度 [source_confidence: 官方文档补充 + 研究者判定]。
- **Prividium**: A+B 兼备。作为 permissioned L2，同时隐藏值和执行。隐私来源 = 准入控制 (RBAC) + ZK validity proof。operator 在执行过程中可见全部数据（Aztec 的批评：「the operator still reads every transaction」），但对外仅暴露 state root + ZK proof [ZKsync Prividium Docs; Aztec 对比分析]。
- **Polygon CDK**: A+B 兼备，但隐私来源可配置。在 permissioned access 模式下属于 A（值可见但身份门控）；在 confidential validium 模式下属于 B（完整执行隐私）；在 confidential compute 模式下可叠加 FHE/TEE [Polygon CDK Privacy Upgrade Docs]。
- **Paladin**: 取决于域类型。Noto (notary token transfers) = A；Pente (ephemeral EVM) = B；两者可在同一 Paladin runtime 内共存 [Paladin Docs]。

### 6.3 EEA 7 方案分类

| 方案 | 分类 | 依据 |
|------|------|------|
| COTI-L2 | A + B（部分） | 值级：encrypted values + GC；执行级（部分）：GC encrypted computation on developer-annotated smart contract logic and on-chain state。基于 COTI L2 网络部署的 EEA 证据 [EEA §10] |
| COTI-Coprocessor | A + B（部分, announced） | 声称继承 COTI-L2 的 GC 技术栈能力；multichain 部署下的实际账本能力未经独立验证（Pilot 阶段）|
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

见 item-2 §2.2 — 6 类技术家族 × 7 项隐私原语维度矩阵，含保护能力等级（强/中/弱）和 EEA 方案技术家族标签（Round 3 COTI 拆分为 COTI-L2 和 COTI-Coprocessor 两行）。Round 2 新增 GC 列在业务逻辑/合约状态维度的评分说明（通用 GC 评「中」，但 COTI 方案级评分在轴 2 中独立调整）。

### diagram-2: 五轴统一 Rubric 评估雷达图模板

见 item-3 §3.2 — 以 Nightfall 为示例的五轴雷达图填充参考。后续竞品分析将对每个方案完成完整雷达图。

### diagram-3: 选择性披露 6 维向量模型示意图

见 item-4 §4.2–4.4 — 6 维并列轴图 + 7 方案向量汇总表。展示多标签向量模型如何表达 Paladin 同时命中 notary/observer + key-holder、Nightfall 同时命中 compliance-gate + viewing-key-share 的复合特征。Round 2 新增 `unverified-revocable` 和 `partial-auditable-log` 标签定义。

### diagram-4: 部署形态谱 — 从 Bolt-on 到独立链

见 item-5 §5.1 — 线性谱图，标注 EEA 方案位置和轻量级判定阈值线。Round 3 将 COTI 拆分为 COTI-Coprocessor（轻量级端，但非 GA）和 COTI-L2（重量级端，GA 但需 COTI L2 网络），两者在谱图上分处阈值线两侧。

---

## Source Coverage

### Primary Source

| 来源 | 版本 | 访问日期 | 覆盖度 | 引用方式 |
|------|------|---------|--------|---------|
| EEA Privacy Working Group Report | Version 1, April 2026 | 2026-06-23 | §01, §04, §06, §06b, §08, §09, §10, §11 | 按 §section 编号引用 |

**说明**：EEA 报告全文 URL (https://entethalliance.github.io/wg-privacy/privacy-report.html) 在 Round 2 修订过程中成功直接获取 HTML 内容。§09 Readiness Matrix 各方案状态、判定标准和证据文本均直接从报告 HTML 结构中提取验证（CSS class `rm-status prod` / `rm-status early` / `rm-status pilot` + 对应 `rm-evidence` 和 `rm-disclosure` 文本）。§10 Solution Profiles（特别是 COTI profile）的 Privacy Approach、Integration Requirements、Commercial Model 和 Solution Characteristics 文本亦直接提取用于 Round 2/3 修订——Round 3 中 COTI 部署模式拆分的关键证据（"Deploy on COTI network or bridge existing assets"、"use of COTI L2 network required"、"Multichain expansion to 70+ chains (planned 2026)"）均来自 §10 直接提取。§10 Silent Data Mandatory Disclosures 中 "Last audit firm + date: Not disclosed" 亦直接提取用于 Round 3 审计信息缺口标注。Round 1 中标注的 G1 缺口（EEA 报告无法直接获取）在 Round 2 中已部分消解。

### Secondary Sources

| 来源 | 用途 | 访问日期 |
|------|------|---------|
| IPTF (https://iptf.ethereum.org) | CROPS 框架、I2I/I2U 语境区分 | 2026-06-23 |
| COTI Medium / 2026 Roadmap | COTI GC 技术细节、multichain 扩展、selective disclosure | 2026-06-23 |
| COTI 跨链隐私协议公告 / Axelar 集成公告 (2026-04) | COTI-Coprocessor multichain 部署进展：首笔跨链交易完成、Axelar Amplifier 集成、Privacy Portal 上线 | 2026-06-23 |
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

| # | 缺口描述 | 影响 | 建议处理 | Round 2 状态 |
|---|---------|------|---------|-------------|
| G1 | EEA 报告全文无法直接获取完整 HTML 内容 | 部分 section 引用依赖间接来源 | 后续 issue 中直接获取报告内容补充 | **部分消解** — Round 2 成功直接获取 EEA 报告 HTML，§09 Readiness Matrix 和 §10 COTI Solution Profile 已直接验证。§07 EF Roadmap 仍未覆盖 |
| G2 | COTI revocability 机制缺少技术白皮书级文档 | item-4 向量中 revocable 标签降级为 `unverified-revocable` | 后续竞品分析 issue 查阅 COTI 技术文档或直接联系确认 | **显式降级** — Round 2 将 COTI revocability 从 `revocable*` 降级为 `unverified-revocable*`，合规映射从「满足 GDPR」降级为「部分满足」 |
| G3 | Nightfall viewing key 撤销机制不明确 | item-4 向量中 one-time 标签附不确定性标注 | 后续查阅 Nightfall_4 技术规范 | **保持** — `one-time` 本身已是保守评估，Orchestrator 确认为 non-blocking |
| G4 | Paladin auditable-log 实现细节不完整 | 审计日志的格式/存储/不可篡改保证未确认 | 后续查阅 Paladin 技术规范 | **显式降级** — Round 2 将 Paladin auditability 从 `auditable-log` 降级为 `partial-auditable-log*`，合规映射从「满足金融审计」降级为「部分满足」 |
| G5 | 路线专属成本指标的具体数值为理论划分而非基准测试 | ZK 约束数、FHE 密文膨胀率等阈值需要实际方案的 benchmark 数据支撑 | 后续竞品分析 issue 中收集各方案的实际性能数据 | **新增局限性说明** — Round 2 在通用指标和路线专属指标两处新增了局限性说明段落，明确标注阈值为理论划分 |
| G6 | §07 EF Roadmap 内容未覆盖 | Ethereum Foundation 自身隐私路线图未在本 section 详述 | 可在后续 issue 中单独覆盖 EF Privacy Roadmap | **保持** |
| G7 | Silent Data 审计信息缺口 — EEA 强制披露 "Last audit firm + date: Not disclosed" | Silent Data 被 EEA 判定为 Early Production，但 Early Production 标准要求 "≥1 third-party security audit (last 18 months)"。EEA 强制披露未包含审计机构和日期信息。Silent Data 持有 ISO/IEC 27001 认证，可能满足审计要求但透明度不足 | 后续竞品分析 issue 将审计透明度作为独立评估维度；必要时直接联系 Applied Blockchain 确认审计详情 | **Round 3 新增** |
| G8 | COTI-Coprocessor 成熟度缺口 — multichain 协处理器模式处于 Pilot 阶段 | COTI-Coprocessor 是唯一通过轻量级判定的 COTI 模式，但仅完成首笔跨链交易（via Axelar），无独立命名客户或生产流量。隐私能力在 multichain 部署下未经独立验证 | 后续竞品分析 issue 需跟踪 COTI multichain 部署进展，区分 L2 模式和 Coprocessor 模式的证据边界 | **Round 3 新增** |

### 无缺口项

- ✓ 8 项企业隐私需求体系完整覆盖 (R1–R8)
- ✓ 6 类技术家族 × 7 项数据维度映射矩阵完整
- ✓ 五轴 rubric 结构和 EEA 方案评估完整（Round 2 修订 COTI 维度；Round 3 拆分 COTI-L2/COTI-Coprocessor）
- ✓ 选择性披露 6 维向量模型定义 + 方案向量填充完整（Round 2 修订不确定性标签；Round 3 拆分 COTI 向量并标注 Coprocessor 置信度）
- ✓ 轻量级判定标准（一票否决 + 路线指标 + 决策规则）完整（Round 2 新增局限性说明；Round 3 COTI-L2 否决、COTI-Coprocessor 通过但非 GA）
- ✓ 隐私账本二义判定口径定义 + 方案分类完整（Round 2 修订 COTI 分类；Round 3 拆分为 COTI-L2 A+B(部分) / COTI-Coprocessor A+B(部分, announced)）
- ✓ IPTF CROPS 框架和 I2I/I2U 语境区分已覆盖
- ✓ EEA §06b 4 项以太坊隐私标准映射完整
- ✓ EEA §09 Readiness Matrix 状态已直接从报告 HTML 验证（Round 2）
- ✓ Residual caveat（向量合规标签验证）已处理，不确定性已标注并做显式降级

---

## Revision Log

| Round | Date | Changes |
|-------|------|---------|
| 1 | 2026-06-23 | Initial deep draft covering all 6 outline items. Research conducted via web search on EEA report, 7 solution profiles, IPTF/CROPS, EIP/ERC standards. Selective-disclosure vectors verified against scheme documentation per residual caveat; uncertainties flagged in G2/G3/G4. |
| 2 | 2026-06-23 | **3 required changes from adversarial review**: (1) Readiness Matrix corrected from EEA report direct HTML extraction — COTI→General Availability, Silent Data→Early Production, Nightfall/Paladin/Linea/Prividium/Polygon CDK→Pilot; stage definitions updated to EEA exact criteria. (2) COTI business-logic/contract-state privacy dimensions upgraded from ○ to ◐ based on EEA §10 COTI Solution Profile evidence ("inputs, balances, on-chain state, and smart contract logic encrypted end-to-end"); COTI隐私层级 revised from pure value-level to value + partial execution; item-6 classification revised from A to A+B(partial). (3) Uncertainty-flagged compliance labels downgraded: COTI `revocable*`→`unverified-revocable*`, Paladin `auditable-log`→`partial-auditable-log*`; compliance mapping table updated accordingly. **Non-blocking additions**: G5 qualification language added to lightweight veto logic sections. G1 partially resolved via direct EEA report HTML fetch. |
| 3 | 2026-06-23 | **2 required changes from adversarial review (FINAL round, max 3)**: (1) **MAJOR — COTI 部署模式拆分**: 将单一 COTI 行拆分为 COTI-L2（GA，在 COTI L2 网络上部署或桥接资产，触发 V1/V2 一票否决，中量级~重量级）和 COTI-Coprocessor（Pilot，multichain 协处理器模式，通过轻量级判定但非 GA，能力 announced 但未独立验证）。拆分覆盖全部相关表格和段落：Executive Summary findings #3/#4/#5、Readiness Matrix（新增 COTI-Coprocessor Pilot 行）、混合信任模型、Table 2.5 技术家族标签、轴1~轴4 全部 COTI 行、选择性披露向量（新增部署模式说明和 Coprocessor † 标注）、向量汇总表、合规映射、部署形态谱图（COTI-L2 移至 C 类独立链，COTI-Coprocessor 留在 A 类 bolt-on）、一票否决条件（COTI-L2 加入 V1/V2 被否决列表）、轻量级判定结果表（双行）、判定说明（双段）、Mantle 启示（条件化结论：轻量级 vs 生产成熟度 tradeoff）、item-6 边界案例和分类表（双行）。新增 G8 COTI-Coprocessor 成熟度缺口。EEA 证据基础：§10 Integration Requirements "Deploy on COTI network or bridge existing assets"、Commercial Model "use of COTI L2 network required"、Solution Characteristics "Multichain expansion to 70+ chains (planned 2026)"；辅助证据：COTI 官方公告首笔跨链交易 via Axelar 完成、Axelar Amplifier 集成进行中。(2) **MINOR — Silent Data 审计信息缺口**: EEA 强制披露 Silent Data "Last audit firm + date: Not disclosed"。在 Readiness Matrix Silent Data 条目新增 † 审计信息缺口说明；合规映射金融审计列 Silent Data 新增 † 标注；新增 G7 缺口项。不改变 EEA §09 的 Early Production 判定。 |
