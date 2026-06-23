---
topic: "EVM 隐私需求与技术全景框架 — Mantle 轻量级机构隐私方案宏观框架"
project_slug: "evm-privacy-research"
topic_slug: "privacy-landscape-framework"
github_repo: "Whisker17/multica-research"
round: 2
status: candidate

artifact_paths:
  outline: "evm-privacy-research/outlines/privacy-landscape-framework.md"
  draft: "evm-privacy-research/research-sections/privacy-landscape-framework/drafts/round-{n}.md"
  final: "evm-privacy-research/research-sections/privacy-landscape-framework/final.md"

scope: |
  为「Mantle 轻量级机构隐私方案」pre-research 建立宏观框架：锚定 EEA Privacy Working Group 报告
  (Version 1, April 2026)，提炼统一 taxonomy、评分 rubric（对齐 EEA 企业隐私需求体系）与
  「选择性披露」子-taxonomy，作为后续所有标准/竞品分析的共同口径，确保最终报告呈现为设计范式分析。
  本 issue 是首个 issue，为后续全部 issue 提供框架。

audience: "Mantle 工程团队、协议/基础设施负责人、企业金融/RWA/BD 团队、隐私方案评估决策者"

expected_output: |
  一份中文结构化研究 section，包含：
  - 从 EEA 报告提炼的 8 项企业隐私需求体系及信任模型/评估框架
  - 隐私原语 → 技术家族映射（含业务逻辑/合约状态隐私独立维度）
  - 五轴统一评估 rubric 表（显式对齐 EEA 企业需求）
  - 选择性披露多标签 taxonomy（6 维向量模型）
  - 部署形态分类与「轻量级」判定标准（含资源成本子项）
  - 「隐私账本」二义判定口径（token ledger vs business-state ledger）
  - 范围边界定义与后续 issue 接口规范

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23T01:00:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-23T02:00:00Z"

multica_issue_id: "51a89bf9-8955-4ae4-914e-cc6920ffea9a"
branch_name: "research/evm-privacy-research/privacy-landscape-framework"
base_commit: "2a8257b78c5b035ca0079e35c940cfdb47919eb0"
language: "中文"
research_depth: "framework"
mode: "single-issue-lightweight"

primary_sources:
  - name: "EEA Privacy Working Group Report"
    url: "https://entethalliance.github.io/wg-privacy/privacy-report.html"
    version: "Version 1, April 2026"
    access_date: "2026-06-23"
    key_sections: "04 Privacy Problem, 06 Taxonomy, 06b Standards, 07 EF Roadmap, 08 Trust Models, 09 Readiness Matrix, 10 Solution Profiles, 11 Decision Framework"
  - name: "IPTF Privacy Map"
    url: "https://iptf.ethereum.org"
    usage: "补充 EEA 报告中引用的 IPTF CROPS 框架和 I2I/I2U 语境区分"

prerequisite_sections: []
---

# Research Outline: EVM 隐私需求与技术全景框架

## Research Questions

1. EEA 报告定义的企业隐私需求体系可以归纳为哪 8 项核心需求？这些需求之间的层次关系和优先级排序是什么？
2. EEA 6 类隐私技术家族（FHE/GC/MPC/TEE/ZKP/Privacy Groups）如何映射到具体的隐私原语？「业务逻辑/合约状态隐私」作为独立维度应如何纳入 taxonomy？
3. 如何构建一个五轴统一评估 rubric，使其既能覆盖密码学路线、数据维度、信任模型、部署形态和合规-选择性披露，又能显式对齐 EEA 企业需求？
4. 「选择性披露」的正交维度有哪些（披露授权方、触发方式、披露载荷、粒度、可撤销性、残余泄露）？如何构建多标签向量模型使每个方案获得可独立验证的分类？
5. 如何定义「轻量级」部署形态的判定标准？除 ZK 成本指标外，FHE/GC/TEE/MPC/Privacy Group 各自的成本驱动因子是什么？是否存在一票否决条件（如需部署新链、新桥、全节点运维或硬分叉）？
6. 「隐私账本」的二义性（token ledger vs business-state ledger）应如何判定？该判定口径如何影响后续竞品分析的范围边界？

## Items

### item-1: EEA 报告核心提炼 — 企业隐私 8 需求、信任模型与评估框架

通读 EEA Privacy Working Group 报告（Version 1, April 2026），提炼并体系化企业隐私需求。报告本身未以编号列表形式列出「8 项需求」，须从 Section 04（Enterprise Privacy Problem）的 4 大屏障、Section 10（Solution Profiles）的数据保护维度、Section 11（Decision Framework）的 5 项评估问题、以及 Section 08（Trust Models）的信任-合规交叉中综合归纳。

本项提出的 8 项企业隐私需求综合体系：

| # | 需求 | EEA 报告来源 |
|---|------|-------------|
| R1 | 交易金额隐私 | §04 Lack of Financial Discretion; §10 各方案 "concealing transaction values" |
| R2 | 账户余额隐私 | §04 Lack of Financial Discretion; §10 COTI/Nightfall "concealing account balances" |
| R3 | 对手方身份隐私 | §04 §11-Q1 "counterparty identities"; §10 Stealth Addresses (ERC-5564) |
| R4 | 业务逻辑/合约状态隐私 | §04 Exposure of Business Logic; §10 Silent Data/Paladin "smart contract execution confidentiality" |
| R5 | 交易图/资金流隐私 | §04 §11-Q1 隐含; §06b ERC-5564/Stealth 防止链接分析 |
| R6 | 合规可审计性 | §04 Regulatory Non-Compliance; §11-Q3 GDPR/MiCA; §10 各方案 "regulatory engagement" |
| R7 | 选择性披露 | §08 Trust Models 跨信任边界; §10 COTI "permissioned view-keys"; Paladin "privacy domains"; Nightfall "X.509 enterprise identity" |
| R8 | 执行策略保护（反 MEV/前运行） | §04 Impact on Financial Strategy; §06b EIP-8105 Encrypted Mempools |

同时提炼 EEA 报告的三层评估结构：
- **3 类信任模型**（§08）：Cryptographic Trust (ZK)、Hardware-Anchored Trust (TEE)、Organizational Honesty (FHE/组织控制)
- **Readiness Matrix**（§09）：Pilot → Early Production → General Availability，附各阶段判定标准
- **Decision Framework**（§11）：5 项评估问题（隐私对象 / 信任模型 / 监管环境 / 部署时间线 / 集成复杂度）

所有结论须标注 EEA 报告的具体 section 编号、版本号（Version 1, April 2026）和访问日期（2026-06-23）。

- **Priority**: high
- **Dependencies**: none

### item-2: 隐私原语 → 技术家族映射（含业务逻辑/合约状态隐私维度）

基于 EEA 报告 Section 06 的 6 类隐私技术家族 taxonomy，构建隐私原语到技术家族的映射矩阵。EEA 定义的 6 类技术家族：

1. **FHE** (Fully Homomorphic Encryption) — 加密数据上计算
2. **GC** (Garbled Circuits) — 加密输入上的安全计算
3. **MPC** (Multi-Party Computation) — 多方私有输入联合计算
4. **TEE** (Trusted Execution Environments) — 硬件安全隔区
5. **ZKP** (Zero-Knowledge Proofs) — 证明而不泄露
6. **PG** (Privacy Groups) — 指定参与者子网络

映射须覆盖以下隐私原语维度：
- 金额隐藏（commitment/encryption of values）
- 余额隐藏（encrypted state/UTXO）
- 身份隐藏（stealth addresses/ring signatures/pseudonymity）
- 图结构隐藏（unlinkability/mixing/decoy sets）
- 业务逻辑隐藏（encrypted execution/private contracts/confidential state transitions）
- 合约状态隐藏（encrypted on-chain state/private DA）
- **订单流/交易意图/mempool 隐私**（pre-confirmation intent 对 sequencer/validator/公共 mempool 不可见）

**新增维度说明**：订单流/mempool 隐私（对齐 R8 执行策略保护）是独立于上述 6 项的第 7 项被保护数据维度。其保护对象不是已上链的交易数据，而是**交易提交到确认之间的意图信息**——包括交易方向、金额范围、目标合约和执行时序。保护手段包括 encrypted mempool (EIP-8105)、commit-reveal 方案、private sequencing (如 Prividium/Linea Enterprise 的 operator-controlled sequencer)、TEE-protected block building (如 Silent Data TEE 执行环境)。评分标准：
- **完全保护**：交易意图在确认前对所有非授权方（包括 sequencer/validator）不可见
- **部分保护**：sequencer/operator 可见但公众不可见（如 permissioned L2 的私有 mempool），或存在时间窗口暴露
- **不保护**：标准公开 mempool

**关键要求**：「业务逻辑/合约状态隐私」须作为独立维度纳入 taxonomy。EEA 报告中 Silent Data (TEE 全图灵完备隐私执行)、Paladin/Pente (ephemeral EVM 隐私执行) 和 Linea Enterprise (Private Validium 状态不外泄) 展示了三种不同路径。须区分：
- **值级隐私**（amount/balance only）— 如 Nightfall commitments、COTI encrypted values
- **执行级隐私**（全智能合约执行隐私）— 如 Silent Data TEE、Aztec private functions
- **状态级隐私**（链上状态不可观察）— 如 Linea Enterprise Validium、Prividium permissioned L2

同时映射 EEA §06b 的 4 项以太坊隐私标准（ERC-5564 Stealth Addresses、ERC-6538 Stealth Meta-Address Registry、ERC-7984 Confidential Fungible Token、EIP-8105 Encrypted Mempools）到技术家族和隐私原语。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 五轴统一评估 Rubric — 对齐 EEA 企业需求

定义统一评估 rubric，覆盖五条评估轴，并显式对齐 item-1 归纳的 8 项企业隐私需求。

**五条评估轴**：

**轴 1 — 密码学路线**：FHE / GC / MPC / TEE / ZKP / Privacy Groups / 混合。每种路线的核心能力、限制、组合方式。

**轴 2 — 被保护数据维度**：金额 / 余额 / 对手方身份 / 转账图 / 业务逻辑 / 合约状态 / **订单流-mempool**。每种方案对每个维度提供的保护级别（完全隐藏 / 部分隐藏 / 不保护）。第 7 项「订单流/mempool 隐私」对齐 R8（执行策略保护/反 MEV），评估交易意图在 pre-confirmation 阶段对 sequencer/validator/公众的可见性。

**轴 3 — 信任模型**：对齐 EEA §08 三类信任模型（Cryptographic / Hardware-Anchored / Organizational），增加混合信任模型评估。信任假设须覆盖：密码学假设、硬件信任、运营方信任、DAC/Sequencer 信任、阈值假设。

**轴 4 — 部署形态**：
- Bolt-on 协处理器（如 COTI multichain 扩展、Zama fhEVM coprocessor）
- 链上合约套件（如 Nightfall ZK rollup contracts、Paladin privacy domains）
- 独立链或 VM（如 Linea Enterprise Validium、Prividium permissioned L2、Silent Data TEE L2、Polygon CDK private chain）

**轴 5 — 合规-选择性披露**：对齐 item-4 的 6 维多标签向量模型，评估每个方案在披露授权方、触发方式、披露载荷、范围粒度、可撤销性和残余泄露上的完整向量。每个方案获得一个可独立验证的多标签向量而非单一分类标签。

**Rubric 表结构设计**：

| 评估轴 | 评分维度 | 对齐 EEA 需求 | 评分等级 |
|--------|---------|-------------|---------|
| 轴 1-密码学路线 | 路线类型、是否需 trusted setup、后量子叙事 | R1-R5（能力边界） | 技术家族标签 |
| 轴 2-数据维度 | 7 项数据维度各自保护级别 | R1(金额) R2(余额) R3(身份) R4(逻辑) R5(图) R8(订单流) | 完全/部分/不保护 |
| 轴 3-信任模型 | 信任假设数量与强度 | R6(合规) R7(披露) | Cryptographic/HW/Org/混合 |
| 轴 4-部署形态 | 部署复杂度、资源成本 | 轻量级判定 | bolt-on/合约套件/独立链 |
| 轴 5-合规披露 | 6 维多标签向量完备性 | R6(合规) R7(披露) | 多标签向量 (authority×trigger×payload×scope×revocability×leakage) |

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 选择性披露多标签 Taxonomy — 6 维向量模型与合规映射

Round 1 的单选 taxonomy（viewing key / observer / association set / compliance-gated / privacy-group / exposed-graph / 无）混淆了三个正交概念：披露*机制*、访问*边界*和残余*泄露*。Paladin 域可以同时是 privacy-group AND notary/observer；Nightfall 可以同时是 KYC-gated AND selective-disclosure。「Exposed Graph」是泄露*结果*而非披露机制。这使得分类不可独立验证。

本项替换为**多标签向量模型**，每个方案获得一个 6 维向量而非单一标签：

**维度 a — 披露授权方（Disclosure Authority）**：谁有权授予披露
- 标签集：`key-holder`（密钥持有者自主授权）| `notary/observer`（公证方/监管节点被动获取）| `smart-contract`（合约逻辑自动执行）| `regulator`（监管方强制请求）| `none`（无披露能力）
- EEA 示例：COTI = `key-holder`（permissioned view-keys）；Paladin/Noto = `notary/observer`（notary-based）；Polygon CDK/ERC-3643 = `smart-contract`（合规合约自动验证）

**维度 b — 披露触发方式（Disclosure Trigger）**：披露如何发起
- 标签集：`viewing-key-share`（密钥分发/共享）| `on-chain-request`（链上请求/证明验证）| `compliance-gate`（KYC/AML 准入门控）| `audit-request`（审计请求/法律要求）| `automatic`（自动/持续披露）
- EEA 示例：Nightfall = `compliance-gate`（X.509 + KYC-gating）+ `viewing-key-share`；Prividium = `automatic`（RBAC 角色持续可见）

**维度 c — 披露载荷（Disclosed Payload）**：披露的内容
- 标签集：`amount` | `identity` | `amount+identity` | `logic`（业务逻辑/合约状态）| `all`（全部数据）| `existence-only`（仅交易存在性）
- 粒度控制：方案是否支持选择性披露载荷子集（如仅披露金额不披露对手方）

**维度 d — 范围/粒度（Scope & Granularity）**：披露的作用范围
- 标签集：`per-tx`（单笔交易）| `per-account`（账户级）| `association-set`（隐私池/合规集合）| `per-contract`（合约级）| `domain-wide`（privacy group/域级）| `chain-wide`（全链）

**维度 e — 可撤销性与审计性（Revocability & Auditability）**：
- 标签集：`one-time`（一次性披露，不可追溯）| `revocable`（可撤销授权）| `permanent`（永久授权）| `auditable-log`（披露行为有审计日志）
- 合规关键性：GDPR right to be forgotten 要求 `revocable`；金融审计要求 `auditable-log`

**维度 f — 残余公开泄露（Residual Public Leakage）**：即使启用隐私保护后，仍对公众可见的信息
- 标签集：`none`（完全隐藏）| `graph`（交易图/流向可见）| `existence`（交易存在性可见）| `amount-range`（金额范围可推断）| `timing`（时序模式可观察）| `other`
- 说明：此维度不是披露*机制*，而是隐私方案的*副作用*。Round 1 的 "Exposed Graph" 重新归类为此维度的一个标签

**方案向量示例**：

| 方案 | Authority | Trigger | Payload | Scope | Revocability | Leakage |
|------|-----------|---------|---------|-------|-------------|---------|
| COTI | key-holder | viewing-key-share | amount+identity | per-tx, per-account | revocable | existence, timing |
| Paladin/Noto | notary/observer, key-holder | automatic, compliance-gate | all | domain-wide | auditable-log | none (within group) |
| Nightfall | key-holder | compliance-gate, viewing-key-share | amount+identity | per-tx | one-time | graph, existence |
| Linea Enterprise | smart-contract | automatic | all | domain-wide | permanent (RBAC) | none (permissioned) |

每种方案的向量须可独立验证——评审者可逐维度核对 EEA 报告 §10 的方案描述。

**合规映射**：将 6 维向量映射到具体合规要求：
- GDPR right to be forgotten → 要求维度 e 包含 `revocable`
- MiCA/Travel Rule → 要求维度 a 包含 `regulator` 或 `smart-contract`，维度 c 包含 `identity`
- AML/CFT → 要求维度 b 包含 `compliance-gate` 或 `audit-request`
- 金融审计 → 要求维度 e 包含 `auditable-log`

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: 部署形态分类与「轻量级」判定标准（含非 ZK 成本指标与一票否决条件）

定义部署形态（Deployment Pattern）分类体系和「轻量级」判定标准。EEA 报告中的 7 方案展现了从轻量 bolt-on 到完全独立链的部署形态谱。Round 1 的判定标准仅覆盖 ZK 成本指标，对 FHE/GC/TEE/MPC/Privacy Group 方案的成本驱动因子缺失，且缺少一票否决条件，会导致「需要部署新链但不用 ZK」的方案被错误分类为轻量级。

**部署形态三级分类**：

**A. Bolt-on 协处理器**：
- 不改变基础链架构，通过外部计算模块提供隐私能力
- 示例：COTI multichain 扩展（计划 70+ 链）、Zama fhEVM coprocessor
- 特征：最低集成成本，功能边界受限

**B. 链上合约套件**：
- 在现有 EVM 链上部署隐私合约集，提供应用层隐私
- 示例：Nightfall ZK rollup contracts、Paladin privacy domains (sidecar node + on-chain verifiers)
- 特征：中等集成复杂度，需要 sidecar 或额外基础设施

**C. 独立链或 VM**：
- 独立运行的隐私链/L2/L3，具备完整隐私执行环境
- 示例：Linea Enterprise Validium、Prividium permissioned L2、Silent Data TEE L2、Polygon CDK private chain
- 特征：最高隐私保障，但集成和运维成本最大

**一票否决条件（Veto Conditions）**——任一条满足即**不可**归类为「轻量级」：

| 否决条件 | 说明 | 触发方案示例 |
|---------|------|-------------|
| 需要部署新 L1/L2/L3/sidechain 或独立 VM | 集成方须运维独立链基础设施 | Linea Enterprise Validium, Prividium, Silent Data L2, Polygon CDK private chain |
| 需要新的资产桥（asset bridge） | 用户资产须跨桥迁移，引入桥安全风险和流动性碎片化 | 所有独立链方案 |
| 集成方须运维 sequencer/prover/DA 全节点 | 运维成本超出应用层集成范畴 | ZK rollup 自建 prover, TEE L2 enclave 节点 |
| 需要基础链硬分叉或共识层修改 | 协议层变更，超出应用层范畴 | EIP-8105 encrypted mempools（需协议变更） |

**通用成本指标（适用于所有技术路线）**：

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| 链上存储增长 | 不增加或仅增加 commitments/proofs | 增加验证合约 + 状态 | 需要独立 DA 层 |
| 运维复杂度 | 无额外节点 | 1-2 sidecar 服务 | 完整链运维 |
| 基础链侵入性 | 无修改 | precompile / 合约部署 | fork 或独立链 |
| 部署时间线 | <3 个月 | 3-9 个月 | >9 个月 |

**ZK 路线专属成本指标**：

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| ZK 约束数/证明生成成本 | <10^6 约束 | 10^6-10^9 约束 | >10^9 约束或递归证明 |
| Trusted Setup | 不需要或通用 CRS | Powers of Tau 等公共仪式 | 方案专属 ceremony |
| Prover 硬件需求 | 标准服务器 / 无需 prover | GPU 加速 | 专用 FPGA/ASIC |

**FHE 路线专属成本指标**：

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| 密钥大小 | <1 MB | 1-100 MB | >100 MB |
| 密文膨胀率 | <10x | 10-1000x | >1000x |
| 单次运算开销（vs 明文） | <100x | 100-10000x | >10000x |
| 密钥管理 | 用户本地 | 阈值解密网络 | 集中式 KMS + escrow |

**TEE 路线专属成本指标**：

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| Enclave 硬件依赖 | 标准云实例（如 AWS Nitro） | 特定 CPU 型号（SGX/TDX） | 定制硬件 |
| 远程证明依赖 | 可选 / 自验证 | 依赖厂商证明服务 | 多方证明链 |
| 侧信道风险缓解 | 无额外措施 | 软件级缓解 | 硬件级隔离 + 审计 |

**MPC/GC 路线专属成本指标**：

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| 交互轮数 | 1-2 轮（如 GC 单轮） | 3-10 轮 | >10 轮或动态轮数 |
| 参与方间带宽 | <1 MB/tx | 1-100 MB/tx | >100 MB/tx |
| 参与方数量要求 | 2 方 | 3-10 方 | >10 方或动态 |

**Privacy Group 路线专属成本指标**：

| 判定维度 | 轻量级 | 中量级 | 重量级 |
|---------|--------|--------|--------|
| 许可节点数量 | 无额外节点（链上隔离） | 1-5 sidecar 节点 | 完整许可网络 |
| 成员管理开销 | 静态/合约管理 | 动态成员 + 密钥轮换 | 跨组织 PKI |

**判定决策规则**：
1. **先检查一票否决**：满足任一否决条件 → 直接归类为「非轻量级」（中量级或重量级），不论数值指标如何
2. **再检查通用指标**：4 项通用指标中有 3 项或以上满足「轻量级」列 → 通过通用门槛
3. **最后检查路线专属指标**：该方案所属技术路线的专属指标中，多数项满足「轻量级」列 → 通过路线门槛
4. **最终判定**：仅当否决条件全部不满足 AND 通用门槛通过 AND 路线门槛通过，方案可归类为「轻量级 bolt-on」

该判定标准直接服务于 Mantle 的「轻量级 bolt-on」偏好评估。

- **Priority**: high
- **Dependencies**: item-3

### item-6: 「隐私账本」二义判定口径与范围边界

定义「隐私账本」（Private Ledger）的二义性判定口径，并给出本研究系列的范围边界。

**二义性定义**：

在企业隐私语境中，「隐私账本」存在两种截然不同的含义：

**A. 私密 Token Ledger（值级账本）**：
- 隐藏的对象：token 转账金额、账户余额、转账对手方
- 典型方案：Nightfall (ZK commitments for ERC-20/721/1155)、COTI (encrypted values + GC)、ERC-7984 Confidential Fungible Token
- 隐喻：「看不见数字的银行流水」
- IPTF 语境：属于 "private transfers" + "confidential tokens"

**B. 私密 Business-State Ledger（状态级账本）**：
- 隐藏的对象：智能合约执行逻辑、内部状态变量、业务规则
- 典型方案：Silent Data (TEE 全执行隐私)、Paladin/Pente (ephemeral EVM)、Aztec (private functions + encrypted state)、Linea Enterprise (Private Validium — 状态不外泄)
- 隐喻：「看不见代码和数据的计算机」
- IPTF 语境：属于 "private computation" + "confidential execution"

**判定口径**：
- 当项目描述声称「隐私账本」时，须显式判定其属于 A (Token Ledger)、B (Business-State Ledger)、或 A+B 兼备
- 判定依据：该方案隐藏的数据维度（item-2 映射）和执行模型（值传输 vs 通用计算）
- 边界案例：Prividium 和 Polygon CDK 属于 A+B 兼备（permissioned L2 同时隐藏值和执行），但其隐私机制来源不同（Prividium = 准入控制 + ZK validity proof, Polygon CDK = configurable FHE/TEE/Validium）

**范围边界**：

本研究系列（evm-privacy-research）的范围：
- **IN**：EVM 兼容链/L2/L3 上的企业级隐私方案，包括 EEA 7 方案 + 补充方案（Aztec、Zama/Fhenix、RAILGUN、Panther、Umbra）
- **IN**：与 EVM 生态有交互或桥接能力的非 EVM 隐私链（如 Zcash viewing keys 概念影响）
- **OUT**：纯消费者隐私（Tornado Cash 类 mixer）、纯匿名链（Monero/Zcash 主链本身）、非区块链隐私技术
- **OUT**：不以「企业/机构用户合规使用」为目标的方案
- **判定准则**：方案是否具备选择性披露能力或合规准入机制，是 IN/OUT 的核心判据

**后续 Issue 接口**：本框架输出的 5 轴 rubric（含 7 项被保护数据维度）、8 需求体系、选择性披露 6 维多标签向量模型、轻量级判定标准（含一票否决条件和路线专属指标），作为后续竞品分析和标准对比 issue 的共同评估口径。后续 issue 须引用本框架而非自行定义评估维度。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| eea_section_ref | 该结论对应的 EEA 报告具体 section 编号（如 §04, §06, §08 等），附报告版本号和访问日期 | all |
| data_dimension | 该项涉及的被保护数据维度：金额/余额/身份/图/逻辑/状态/订单流-mempool，及保护级别（完全/部分/不保护） | item-2, item-3, item-6 |
| trust_model | 信任模型分类（Cryptographic/Hardware-Anchored/Organizational/混合）及具体信任假设 | item-1, item-3, item-4 |
| deployment_pattern | 部署形态分类（bolt-on/合约套件/独立链）及轻量级判定结果 | item-3, item-5, item-6 |
| disclosure_vector | 选择性披露 6 维多标签向量：authority×trigger×payload×scope×revocability×leakage（每维可含多个标签） | item-3, item-4, item-6 |
| compliance_mapping | 合规标准映射（GDPR/MiCA/Travel Rule/AML-CFT/KYC-KYB）及满足程度 | item-1, item-4, item-6 |
| eea_solution_mapping | 映射到 EEA 7 方案中的具体实现示例，作为 rubric 验证参照 | item-2, item-3, item-4, item-5 |
| mantle_relevance | 该结论对 Mantle 轻量级机构隐私方案的具体启示或约束 | item-3, item-5, item-6 |
| source_confidence | 证据等级：EEA 报告直接引用 / EEA 报告推论 / 官方文档补充 / 行业分析推断；标注不确定性 | all |

## Diagrams

### diagram-1: 隐私技术家族与隐私原语映射矩阵

6 类技术家族（FHE/GC/MPC/TEE/ZKP/PG）为列，7 项隐私原语维度（金额/余额/身份/图/逻辑/状态/订单流-mempool）为行的矩阵图。单元格标注保护能力等级（强/中/弱/不适用）。右侧附 EEA 7 方案的技术家族标签。第 7 行「订单流/mempool」对齐 R8，评估各技术家族对 pre-confirmation 交易意图的保护能力。

- **Type**: matrix / heatmap
- **Applies to**: item-2
- **Purpose**: 一眼看清各技术家族的能力边界，避免方案选型时的 capability-washing

### diagram-2: 五轴统一 Rubric 评估雷达图模板

五条评估轴为雷达图的 5 个方向，每个方向有 3-5 个刻度。附一个示例方案（如 Nightfall）的填充参考，展示 rubric 的使用方式。

- **Type**: radar chart (template)
- **Applies to**: item-3
- **Purpose**: 为后续竞品分析提供可视化评估模板

### diagram-3: 选择性披露 6 维向量模型示意图

6 个独立维度（authority / trigger / payload / scope / revocability / leakage）的并列轴图，每个轴列出其标签集。附 2-3 个 EEA 方案（如 COTI、Paladin、Nightfall）的向量连线，展示同一方案如何在多个维度上获得多标签。对比 Round 1 单选 taxonomy 的局限（如 Paladin 同时命中 privacy-group 和 observer 无法表达）。

- **Type**: parallel-axis / multi-label vector
- **Applies to**: item-4
- **Purpose**: 展示多标签向量模型的表达力，说明为何单选分类不够

### diagram-4: 部署形态谱 — 从 Bolt-on 到独立链

线性谱图，左端为 bolt-on 协处理器（最轻量），右端为独立链/VM（最重量）。谱上标注 EEA 7 方案的位置和「轻量级」判定阈值线。

- **Type**: spectrum / scale
- **Applies to**: item-5
- **Purpose**: 直观展示 Mantle「轻量级偏好」的选择空间

## Source Requirements

### Primary Source
- **EEA Privacy Working Group Report** (Version 1, April 2026)
  - URL: https://entethalliance.github.io/wg-privacy/privacy-report.html
  - 访问日期: 2026-06-23
  - 使用方式: 作为本框架的锚定文档，所有 taxonomy、需求提炼和信任模型定义均以此为基线
  - 引用要求: 每个提炼结论须标注 §section 编号

### Secondary Sources
- **IPTF (Institutional Privacy Task Force)**
  - URL: https://iptf.ethereum.org
  - 使用方式: 补充 CROPS 框架、I2I/I2U 语境区分、PoC 案例
- **EEA 7 方案各自官方文档**
  - 用于验证 EEA 报告中的方案描述准确性
  - 优先级低于 EEA 报告本身（以 EEA 报告为准，差异须标注）

### 引用规范
- 每个结论附 `[EEA §XX]` 标签
- 推论性结论（EEA 报告未直接陈述但由研究者综合推断）标注 `[推论]`
- 外部补充来源标注访问日期
- 「8 项企业需求」作为综合归纳产物，须在 item-1 中逐项说明其 EEA 来源依据
