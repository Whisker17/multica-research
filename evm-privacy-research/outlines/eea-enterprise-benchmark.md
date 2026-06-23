---
topic: "EEA 企业隐私实现 Benchmark（7 方案 × 8 需求）"
project_slug: "evm-privacy-research"
topic_slug: "eea-enterprise-benchmark"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "evm-privacy-research/outlines/eea-enterprise-benchmark.md"
  draft: "evm-privacy-research/research-sections/eea-enterprise-benchmark/drafts/round-{n}.md"
  final: "evm-privacy-research/research-sections/eea-enterprise-benchmark/final.md"

scope: |
  按 EEA Privacy Working Group 报告（Version 1, April 2026，§09 Readiness Matrix / §10 Solution Profiles
  / §11 Decision Framework）自身的标准化框架，benchmark 其 profile 的 7 个企业隐私方案——Paladin、
  Prividium、Linea Enterprise、Nightfall、COTI、Polygon CDK Enterprise、Silent Data——对照 8 项企业需求
  （交易隐私 / 余额隐私 / 智能合约隐私 / 合规 / 选择性披露 / 主网结算 / 技术栈 / 信任模型），并以
  privacy-landscape-framework（WHI-254）的五轴统一 rubric、R1–R8 需求体系、选择性披露 6 维向量、轻量级
  判定标准为共同评分口径，确保与本项目其他 issue 横向可比。
  显式标注哪些方案提供合约逻辑/业务状态隐私（vs token-only）。Paladin 复用既有深度调研结论，不重做源码级
  深挖，仅核验 EEA/官方文档中的易变事实。补充替代信任模型 sidebar（Oasis Sapphire / Secret(EVM 暂停) /
  Automata；可选 Solana Confidential Transfers 作非 EVM 机构对照）。逐方案给出对 Mantle 相关性 + bolt-on
  可行性 + 候选/参考/出局初判。

audience: "Mantle 工程团队、协议/基础设施负责人、企业金融/RWA/BD 团队、隐私方案评估决策者"

expected_output: |
  一份中文结构化研究 section，包含：
  - benchmark 列定义：8 项企业需求（映射 R1–R8）+ EEA Readiness Matrix（Pilot/Early/GA），与框架 rubric 对齐
  - 7 方案逐方案 profile（路线、隐私原语、合约逻辑隐私、信任模型、披露模型、settlement、成熟度/客户）
  - Paladin 既有研究复用映射摘要（3 份内部来源 → 本项目 rubric），仅核验易变事实
  - 7 方案 × 8 需求 benchmark 矩阵（保护级别 完全/部分/不保护）
  - 合约逻辑/业务状态隐私标注列（token-only vs contract-logic privacy）
  - 五轴 rubric 评分填充（与框架及 Aztec/ERC-7984/EIPs 等 issue 同口径）
  - 替代信任模型 sidebar（Oasis Sapphire / Secret / Automata + 可选 Solana Confidential Transfers）
  - 逐方案对 Mantle 相关性 + bolt-on 可行性 + 候选/参考/出局判定
  - 图表：7×8 benchmark 矩阵、Mantle 相关性总结、部署形态谱、合约逻辑隐私分类
  - 每结论附 URL/路径 + 访问日期/版本；厂商自报数据标注「未独立验证」；commit SHA 用于内部来源

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23T09:40:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-23T09:40:00Z"

multica_issue_id: "2b1c69d1-809b-4857-9e4d-083774dc4c15"
branch_name: "research/evm-privacy-research/eea-enterprise-benchmark"
base_commit: "eceaef1e1b4f7a17d7fc3eb4dd91560207f40629"
language: "中文"
research_depth: "deep-analysis"
mode: "single-issue-lightweight"

primary_sources:
  - name: "EEA Privacy Working Group Report — State of Privacy on Ethereum for Enterprise"
    url: "https://entethalliance.github.io/wg-privacy/privacy-report.html"
    version: "Version 1, April 2026"
    access_date: "2026-06-23"
    key_sections: "09 Readiness Matrix, 10 Solution Profiles, 11 Decision Framework（辅以 04/06/06b/08 作需求与信任模型背景）"
  - name: "privacy-landscape-framework（WHI-254）final.md"
    url: "evm-privacy-research/research-sections/privacy-landscape-framework/final.md"
    usage: "引用五轴 rubric、R1–R8 需求体系、选择性披露 6 维向量、轻量级判定标准（含一票否决）、隐私账本二义口径、Readiness Matrix 三阶段作为统一评分口径"

secondary_sources:
  - name: "Paladin Deep Dive（内部复用）"
    url: "202606-internal-sharing/research-sections/Paladin Deep Dive.md"
    usage: "Paladin Noto/Zeto/Pente 架构、交易流、KYC 合规稳定币转账、RWA 全生命周期、Mantle 集成分析、Besu 依赖与缺陷——复用为 Paladin profile 基础"
  - name: "企业级区块链隐私技术综述（内部复用）"
    url: "202606-internal-sharing/research-sections/enterprise-privacy/final.md"
    usage: "企业隐私需求框架、既有企业链隐私范式复用、代表性项目隐私实现案例、技术路线对比矩阵"
  - name: "WHI-390 企业区块链方案分析 final-report（内部复用）"
    url: "mantle-enterprise-blockchain/report/final-report.md"
    usage: "§5.5 隐私比较 / §5.6 合规比较 / L1-L2-L3-Sidecar 决策框架——复用为 Paladin/Mantle 部署形态与合规背景"
  - name: "各方案官方文档（需逐方案核验）"
    usage: "Prividium(ZKsync/Matter Labs Docs)、Linea Enterprise(Consensys/Lineth)、Nightfall(EY 官方 + GitHub)、COTI(官方文档/Medium)、Polygon CDK Enterprise(Polygon Docs)、Silent Data(Applied Blockchain) — EEA 报告口径为准，差异须标注"
  - name: "替代信任模型 sidebar 官方来源"
    usage: "Oasis Sapphire(ParaTime 机密 EVM)、Secret Network(SecretEVM 状态)、Automata(链上 TEE attestation verifier)、Solana Confidential Transfers(Token-2022 机密转账扩展)"

prerequisite_sections:
  - topic_slug: "privacy-landscape-framework"
    dependency_type: "framework"
    usage: "引用 WHI-254 五轴 rubric、R1–R8 需求体系、选择性披露 6 维向量模型、轻量级判定标准、隐私账本二义口径、EEA Readiness Matrix 三阶段进行评分与横向对比"
---

# Research Outline: EEA 企业隐私实现 Benchmark（7 方案 × 8 需求）

> 本 section 是 evm-privacy-research 系列的「企业方案 benchmark」视角，补全原计划遗漏的「真正被 EEA 报告 profile 的 7 个企业方案」（此前覆盖了 §13 附加未 profile 项却漏了被 profile 的核心 7 方案）。本 outline 不重复定义评估维度，全部引用 privacy-landscape-framework（WHI-254）的 rubric 与口径，仅在其上做逐方案 benchmark 填充与判定。

## Research Questions

1. EEA 报告 §09/§10/§11 如何 profile 这 7 个企业隐私方案？将其 8 项数据保护/合规维度映射到框架 R1–R8 需求体系后，每个方案在每项需求上的保护级别（完全/部分/不保护）是什么？
2. 7 方案中哪些提供「合约逻辑/业务状态隐私」（R4），哪些仅为 token-only（值级）隐私？这一区分对 institutional Mantle 的实质意义是什么？
3. Paladin 既有深度调研（3 份内部来源）如何无损映射到本项目 rubric？哪些是「易变事实」（EEA profile 口径、官方文档入口、项目状态）需要在本轮轻量核验、哪些结论直接复用？
4. 在框架五轴 rubric 下，6 个新调研方案（Prividium / Linea Enterprise / Nightfall / COTI / Polygon CDK Enterprise / Silent Data）各轴评分如何？与 Paladin、与已完成 issue（Aztec/ERC-7984/EIPs）的评分如何横向对齐？
5. 替代信任模型方案（Oasis Sapphire / Secret / Automata；可选 Solana Confidential Transfers）相对 EEA 7 方案补充了哪些信任模型/部署形态选项？它们对 Mantle 的参考价值是什么？
6. 逐方案在框架「轻量级判定标准（含一票否决）」下的部署形态判定如何？据此对 Mantle 的相关性（候选 / 参考 / 出局）初判是什么，bolt-on 可行性如何？

## Items

### item-1: Benchmark 框架与列定义 — 8 企业需求 × Readiness Matrix × 框架 rubric 对齐

定义本 benchmark 的「列」（评估维度），全部锚定既有框架，不自行新造维度。这是 Step 1 的产物，为后续逐方案填充提供统一表头。

**1.1 8 项企业需求 → 框架 R1–R8 映射**：dispatch 给出的 8 项企业需求须显式映射到框架 R1–R8，避免口径漂移。预期映射（须在 draft 中逐项确认）：

| Dispatch 8 需求 | 框架对应 | 说明 |
|---|---|---|
| transaction privacy（交易隐私） | R1 交易金额隐私 (+R5 交易图) | 交易金额/流向对非授权方不可见 |
| balance privacy（余额隐私） | R2 账户余额隐私 | 余额加密存储 |
| smart contract privacy（智能合约隐私） | R4 业务逻辑/合约状态隐私 | **合约逻辑/业务状态隐私维度——本 issue 重点** |
| regulatory compliance（合规） | R6 合规可审计性 | GDPR/MiCA/Travel Rule/AML-CFT |
| selective disclosure（选择性披露） | R7 选择性披露 | 映射到 6 维向量 |
| mainnet settlement（主网结算） | （部署形态/settlement 维度） | L1 结算 / DA / validity proof 上链口径 |
| technology stack（技术栈） | （轴 1 密码学路线 + 轴 4 部署形态） | FHE/GC/MPC/TEE/ZKP/PG + 部署形态 |
| trust model（信任模型） | 轴 3（Cryptographic/HW/Org/混合） | 对齐 EEA §08 三类信任模型 |

注：R3（对手方身份隐私）和 R8（执行策略/反 MEV）虽未在 dispatch 8 需求中显式列出，但属框架 R1–R8 体系；benchmark 矩阵应保留这两列以保证与其他 issue 完全同口径，并在缺少 EEA 证据时标注「未明确」。

**1.2 EEA Readiness Matrix 作为成熟度列**：复用框架已从 EEA §09 直接提取的三阶段判定（Pilot / Early Production / General Availability）及各阶段标准（命名客户数、运营月数、审计次数、公开交易量）。本 issue 不重新定义阶段标准，直接引用 [WHI-254 §1.4]。

**1.3 五轴 rubric 作为评分骨架**：benchmark 的每个方案最终落到框架五轴（轴 1 密码学路线 / 轴 2 被保护数据维度 / 轴 3 信任模型 / 轴 4 部署形态 / 轴 5 合规-选择性披露）。本 item 明确「benchmark 矩阵」= 轴 2（7 项数据维度）+ R6/R7（合规/披露）的逐方案填充，「rubric 评分」= 五轴完整填充。

- **Priority**: high
- **Dependencies**: none

### item-2: Paladin 既有研究复用映射（REUSE ONLY，不重做深挖）

将 Paladin 既有深度调研结论无损映射到本项目 rubric。**严格遵守 dispatch 边界：不做源码级深挖，仅核验易变事实。** 这是 Step 2 中 Paladin 部分的产物。

**2.1 复用来源清单与映射目标**：

| 内部来源（附 commit SHA） | 复用内容 | 映射到 rubric 的目标字段 |
|---|---|---|
| `202606-internal-sharing/research-sections/Paladin Deep Dive.md` | Noto/Zeto（Layer B）、Pente（Layer C）架构；交易流；KYC 合规稳定币转账；RWA 债券全生命周期；tokenized equities；Besu 依赖；缺陷分析；Mantle 集成可能性 | 轴 1 路线（PG+ZKP）、轴 2 数据维度、R4 合约逻辑隐私（Pente ephemeral EVM）、轴 3 信任模型（notary）、轴 5 披露向量、部署形态、Mantle 相关性 |
| `202606-internal-sharing/research-sections/enterprise-privacy/final.md` | 企业隐私需求框架、既有企业链隐私范式、代表性项目案例、技术路线对比矩阵 | 需求映射背景、Paladin 在技术路线矩阵中的定位 |
| `mantle-enterprise-blockchain/report/final-report.md` | §5.5 隐私比较 / §5.6 合规比较 / Sidecar 决策框架 | 部署形态（sidecar）、Mantle bolt-on 可行性、合规背景 |

**2.2 须轻量核验的「易变事实」**（仅这些需在本轮验证，附访问日期）：
- EEA §09/§10 对 Paladin 的 profile 口径与成熟度判定（框架记为 Pilot：Bank of Indonesia Digital Rupiah / HKMA eHKD Phase 2 / Banco Central do Brasil Drex，均 PoC）——核验是否与 EEA 报告当前 HTML 一致
- Paladin 官方文档入口与项目状态（LFDT 项目化、Kaleido 维护现状）
- 与框架 final.md 中 Paladin 向量（authority: notary/observer + key-holder；payload: all；scope: domain-wide；revocability: partial-auditable-log*）的一致性

**2.3 直接复用、不重新验证的结论**：Noto/Zeto/Pente 三类隐私域机制、ephemeral EVM 在域内执行全部合约逻辑（R4 部分保护）、notary-based 信任模型、sidecar 部署形态、Besu 客户端依赖——这些为既有深度调研结论，直接引用并标注来源路径 + commit SHA。

**复用与新研究的边界声明**：本 item 产出须明确标注每条 Paladin 结论是「复用既有」还是「本轮核验」，避免 review 误判为未做研究。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 6 方案逐方案 deep profile — 对照 8 维度

对 6 个新调研方案逐一 profile（Step 2 主体）。每个方案按统一 8 维 profile 模板调研：①路线/技术家族 ②隐私原语 ③合约逻辑/业务状态隐私（R4，是/部分/否）④信任模型 ⑤选择性披露模型 ⑥主网 settlement 方式 ⑦技术栈/部署形态 ⑧成熟度与命名客户。以 EEA §10 Solution Profile 为锚，官方文档补充与核验，差异须标注。

**3.1 Prividium（ZKsync / Matter Labs）— 许可型 ZK L2**：ZK validity proof + permissioned RBAC（Proxy RPC、Okta/Azure IdP、Selective Disclosure for auditors）；仅 state root + ZK proof 上链；A+B 兼备（值+执行+状态）。须核验 SOC 2 状态、selective disclosure 机制、settlement 到 Ethereum 的口径。

**3.2 Linea Enterprise（Consensys）— Private Validium + ZK**：Lineth stack（Besu 执行 + Maru 共识 + coordinator + gnark prover）；Private Validium 链下 DA，仅 cryptographic fingerprint 上链（状态级隐私 B）；permissioned sequencer/operator 可见全部。须核验 SWIFT 合作/pilot 状态、validium vs rollup 配置、operator 信任口径。

**3.3 Nightfall（EY）— 开源 ZK 机密代币协议**：ZK rollup + ZK commitments for ERC-20/721/1155（值级隐私 A，token-only）；X.509 企业身份 PKI + KYC-gating；viewing key 选择性披露。须核验 Nightfall_4 升级、Starknet 集成（prover 外包路径）、是否覆盖通用合约逻辑（预期否，仅值级）。

**3.4 COTI — 混淆电路（Garbled Circuits）**：**须沿用框架 COTI-L2 / COTI-Coprocessor 部署模式拆分**（[WHI-254 §1.4/§5.6] 已确立此口径，benchmark 须保持一致）。GC 加密 inputs/balances/on-chain state/smart contract logic（值级 + 执行级部分，开发者显式标注机密参数）；permissioned view-keys 披露。须核验：(a) COTI-L2 GA 证据（Privex/StaTwig/ECB、审计）；(b) COTI-Coprocessor multichain（70+ 链 planned，Axelar 首笔跨链）成熟度仍为 Pilot；(c) revocability 仍为 unverified。

**3.5 Polygon CDK Enterprise — 可配置隐私光谱**：「Privacy is a spectrum, not a switch」——permissioned access → confidential validium → confidential compute（可叠加 FHE/TEE）；可配置 A/B；Gateway + enterprise SSO。须核验 T-REX Ledger（Apex Group $100B RWAs，Zama FHE + ERC-3643）pilot、CDK 隐私升级文档当前口径。

**3.6 Silent Data（Applied Blockchain）— TEE-based programmable privacy**：TEE（SGX/Nitro）全执行隐私（执行级 + 状态级 B）；标准 Solidity，operator 不可见敏感数据；OP Stack L2。须核验 Early Production 判定 + EEA 强制披露「Last audit firm + date: Not disclosed」审计缺口、Archax/Bank of England 用例、ISO/IEC 27001。

**统一要求**：每方案 profile 须 (1) 标注 EEA §10 直接引用 vs 官方文档补充 vs 推论；(2) 厂商自报性能/客户数据标注「未独立验证」；(3) 外部结论附访问日期/版本。

- **Priority**: high
- **Dependencies**: item-1

### item-4: 合约逻辑/业务状态隐私标注（R4）— token-only vs contract-logic privacy

显式回答 Step 3：7 方案中哪些提供「合约逻辑/业务状态隐私」（R4），哪些仅为 token-only（值级）。这是本 issue 对 institutional Mantle 的核心增量——token-only 方案不能替代需要业务状态隐私的场景。

**4.1 三层隐私区分**（复用框架 §2.4 口径）：值级（amount/balance only）/ 执行级（全合约执行隐私）/ 状态级（链上状态不可观察）。

**4.2 预期 7 方案 R4 标注**（须在 draft 以 EEA/官方证据逐方案确认，下表为待验证假设）：

| 方案 | token-only? | 合约逻辑/业务状态隐私 | 机制 |
|---|---|---|---|
| Paladin | 否（Pente 提供） | 是（执行级，域内可见） | Pente ephemeral EVM |
| Prividium | 否 | 是（A+B，permissioned） | permissioned L2 + ZK |
| Linea Enterprise | 否 | 是（状态级 B） | Private Validium |
| Nightfall | **是（token-only）** | 否（仅值级 A） | ZK commitments |
| COTI | 否（部分） | 部分（开发者标注机密参数） | GC encrypted computation |
| Polygon CDK | 否（可配置） | 是（confidential validium/compute 模式） | 可配置 FHE/TEE/Validium |
| Silent Data | 否 | 是（执行级+状态级 B） | TEE 全执行隐私 |

**4.3 对 Mantle 的意义**：明确区分哪些方案只能隐藏「数字」（token ledger A）、哪些能隐藏「业务逻辑/状态」（business-state ledger B），并指出 institutional 场景（如 RWA 全生命周期、机构间合约、合规计算）对 B 类的真实需求。引用框架隐私账本二义口径 [WHI-254 item-6]。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: 7×8 Benchmark 矩阵 + 五轴 rubric 评分填充

综合 item-2/3/4，产出本 issue 的核心交付物：7 方案 × 8 需求 benchmark 矩阵，以及五轴 rubric 的逐方案完整填充（Step 1 + Step 6）。

**5.1 7×8 benchmark 矩阵**：行 = 7 方案（COTI 按 L2/Coprocessor 拆为两行以保持框架口径，注明），列 = 8 需求（R1 金额 / R2 余额 / R4 合约逻辑 / R6 合规 / R7 披露 / settlement / 技术栈 / 信任模型；保留 R3 身份、R5 图、R8 订单流为补充列）。单元格 = 保护级别（● 完全 / ◐ 部分 / ○ 不保护）或分类标签（信任模型、技术栈、settlement）。须与框架 §3.2 轴 2 表交叉核对，保证已有方案评分一致。

**5.2 五轴 rubric 填充**：对每个方案填充轴 1（路线/trusted setup/后量子/组合）、轴 2（7 数据维度）、轴 3（信任模型 + 假设清单）、轴 4（部署形态 + 轻量级判定，详见 item-7）、轴 5（6 维披露向量）。Paladin 行直接复用 item-2 映射结果。

**5.3 横向对齐校验**：将本 issue 评分与框架 final.md 及已完成 issue（zk-privacy-chain-aztec / erc7984-confidential-token / privacy-eips-survey）的评分对照，标注任何因新证据导致的差异（如有），确保 cross-comparison 口径一致。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4

### item-6: 替代信任模型 Sidebar — Oasis Sapphire / Secret / Automata（+ 可选 Solana）

Step 4 的 sidebar：在 EEA 7 方案之外，补充替代信任模型的参考方案，扩展信任模型/部署形态选择空间。明确标注为「补充参考」，非 benchmark 主体，调研深度低于 7 方案。

**6.1 Oasis Sapphire**：机密 EVM ParaTime（TEE-based confidential EVM）；提供「合约逻辑隐私的 EVM 兼容路径」参考；信任模型 Hardware-Anchored。须核验当前状态、与 Mantle EVM 的概念可借鉴性。

**6.2 Secret Network（EVM 暂停）**：SecretEVM / Confidential Computing Layer；**须明确标注 EVM 路线当前状态（暂停/调整）**，作为「曾尝试机密 EVM 但路线受阻」的对照案例。

**6.3 Automata**：链上 TEE attestation verifier（Multi-Prover / attestation 积木）；作为「可 bolt-on 的 attestation 验证组件」参考，与 Silent Data/Oasis 的 TEE 信任互补。

**6.4 Solana Confidential Transfers（可选，非 EVM 对照）**：Token-2022 confidential transfer 扩展（ElGamal 加密 + ZK range proofs，机构机密余额/转账）；作为非 EVM 机构级值级隐私的横向对照（token-only），标注「非 EVM、不可直接集成」。

**统一要求**：每个 sidebar 方案给出信任模型分类、与 EEA 7 方案的差异点、对 Mantle 的参考价值（概念借鉴 vs 不可移植），不做完整五轴填充（仅信任模型 + 部署形态 + R4 标注）。

- **Priority**: medium
- **Dependencies**: item-1

### item-7: 逐方案 Mantle 相关性 + bolt-on 可行性 + 候选/参考/出局判定

Step 5：对 7 方案逐一给出对 Mantle 的初判。应用框架「轻量级判定标准（含 4 项一票否决）」得出部署形态判定，据此给出三档 verdict。

**7.1 轻量级判定**：对每个方案套用框架 V1（新链/VM）/ V2（新桥）/ V3（全节点运维）/ V4（硬分叉）一票否决 + 通用/路线专属指标 [WHI-254 item-5]。预期结果（待 draft 确认，与框架一致性校验）：

| 方案 | 部署形态 | 轻量级判定 | bolt-on 可行性 |
|---|---|---|---|
| Paladin | sidecar + 链上 verifiers | 轻量级~中量级 | 较高（sidecar 应用层） |
| COTI-Coprocessor | bolt-on 协处理器 | 轻量级（非 GA） | 高（架构）但成熟度 Pilot |
| COTI-L2 | 独立 L2 + 桥 | 一票否决（V1/V2） | 低 |
| Nightfall | ZK rollup 合约套件 | 中量级（V3 rollup operator） | 中（Starknet prover 外包可降负担） |
| Prividium | 独立 permissioned L2 | 一票否决（V1/V2/V3） | 低 |
| Linea Enterprise | 独立 Validium L2 | 一票否决 | 低 |
| Polygon CDK | 独立 private chain | 一票否决 | 低 |
| Silent Data | 独立 TEE L2 | 一票否决 | 低（但 TEE 概念/Automata 验证可借鉴） |

**7.2 三档 verdict 定义**：
- **候选（Candidate）**：架构上可 bolt-on 到 Mantle 且具备所需隐私能力（重点关注 R4 合约逻辑隐私）——预期 Paladin、COTI-Coprocessor
- **参考（Reference）**：不可直接集成但有可借鉴的设计/原语/合规模型——预期 Nightfall（值级标准）、Silent Data（TEE 执行隐私范式）、Prividium（合规向量最完整）
- **出局（Out）**：部署形态与 Mantle 轻量级偏好根本冲突且无独特借鉴价值——按证据判定

**7.3 候选方案的 tradeoff 分析**：对候选方案明确「轻量级部署 vs 生产成熟度 vs R4 能力」的权衡（如 COTI-Coprocessor 轻量但 Pilot、Paladin 轻量且提供 R4 但 notary 信任）。引用 [WHI-254 §5.6 Mantle 启示]。

**7.4 Mantle 相关性总结表/图**：汇总 7 方案的 verdict + 关键约束 + R4 能力 + 成熟度，作为决策视角输出。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4, item-5, item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| eea_section_ref | 该结论对应的 EEA 报告 section 编号（§09/§10/§11 等）+ 版本（Version 1, April 2026）+ 访问日期（2026-06-23） | all |
| requirement_coverage | 该方案对 8 需求（映射 R1–R8）各自的保护级别：完全(●)/部分(◐)/不保护(○)/未明确 | item-3, item-5 |
| contract_logic_privacy | R4 合约逻辑/业务状态隐私标注：token-only(值级A) / 执行级(B) / 状态级(B) / 部分；及机制 | item-2, item-3, item-4 |
| trust_model | 信任模型分类（Cryptographic/Hardware-Anchored/Organizational/混合）及具体信任假设清单，对齐 EEA §08 与框架轴 3 | item-2, item-3, item-5, item-6 |
| disclosure_vector | 选择性披露 6 维多标签向量：authority × trigger × payload × scope × revocability × leakage（对齐框架 item-4） | item-2, item-3, item-5 |
| settlement_model | 主网结算方式：L1 结算 / 链下 DA(validium) / 仅 state root + validity proof 上链 / 桥接；及对公众的残余可见性 | item-3, item-5 |
| deployment_pattern | 部署形态（bolt-on 协处理器 / 链上合约套件 / 独立链或 VM）+ 框架轻量级判定结果（一票否决/通过） | item-3, item-5, item-7 |
| maturity_readiness | EEA Readiness Matrix 判定（Pilot/Early Production/GA）+ 命名客户/运营时长/审计证据；厂商自报标注未独立验证 | item-2, item-3, item-7 |
| mantle_relevance | 对 Mantle 的相关性 + bolt-on 可行性 + 候选/参考/出局 verdict + 关键 tradeoff | item-6, item-7 |
| reuse_provenance | Paladin 结论的来源标注：复用既有（附内部路径 + commit SHA）vs 本轮核验（附访问日期） | item-2 |
| source_confidence | 证据等级：EEA 报告直接引用 / EEA 报告推论 / 官方文档补充 / 内部复用 / 行业分析推断；标注不确定性与「未独立验证」 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison / matrix | **7×8 benchmark 矩阵**：行=7 方案（COTI 拆 L2/Coprocessor），列=8 需求（R1 金额/R2 余额/R4 合约逻辑/R6 合规/R7 披露/settlement/技术栈/信任模型，+R3/R5/R8 补充列）；单元格=●/◐/○ 或分类标签。核心交付图。 | mermaid / ascii (table) | item-5 |
| diag-2 | hierarchy / classification | **合约逻辑隐私分类图**：将 7 方案按 值级(A token-only) / 执行级(B) / 状态级(B) / A+B 兼备 分层，显式标注 token-only 方案（Nightfall）与 contract-logic privacy 方案。 | mermaid | item-4 |
| diag-3 | comparison | **五轴 rubric 对照表/雷达**：7 方案五轴评分汇总，与框架 final.md 评分交叉核对。 | mermaid / ascii (table) | item-5 |
| diag-4 | spectrum / positioning | **部署形态谱 + 轻量级判定**：左(bolt-on 轻量)→右(独立链重量)，标注 7 方案位置与一票否决阈值线（复用并扩展框架 diagram-4 的方案定位）。 | ascii / mermaid | item-7 |
| diag-5 | comparison / summary | **Mantle 相关性总结**：7 方案 verdict（候选/参考/出局）+ R4 能力 + 成熟度 + bolt-on 可行性 + 关键约束汇总表。决策视角核心图。 | mermaid / ascii (table) | item-7 |
| diag-6 | comparison | **替代信任模型 sidebar 对照**：Oasis Sapphire / Secret / Automata（+可选 Solana）的信任模型、部署形态、R4 标注、对 Mantle 参考价值对照。 | ascii (table) | item-6 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | industry_reports (anchor) | EEA Privacy Working Group Report §09 Readiness Matrix / §10 Solution Profiles / §11 Decision Framework（Version 1, April 2026，访问日期 2026-06-23）——所有 7 方案 profile 的锚定来源 | 1 |
| src-2 | internal_reuse | Paladin 三份内部来源（Paladin Deep Dive / enterprise-privacy final.md / mantle-enterprise-blockchain final-report.md），引用附路径 + commit SHA | 3 |
| src-3 | framework_reference | privacy-landscape-framework（WHI-254）final.md——五轴 rubric / R1–R8 / 6 维向量 / 轻量级判定 / 隐私账本口径 / Readiness Matrix | 1 |
| src-4 | official_docs | 6 个新调研方案各自官方文档（Prividium、Linea Enterprise、Nightfall、COTI、Polygon CDK Enterprise、Silent Data）——每方案至少 1 个官方来源核验 EEA profile | 6 |
| src-5 | official_docs (sidebar) | 替代信任模型方案官方来源：Oasis Sapphire、Secret Network、Automata（+ 可选 Solana Confidential Transfers / Token-2022） | 3 |
| src-6 | audit_reports / on_chain_data | 成熟度证据：审计报告、命名客户公告、公开交易量/TVL（用于 Readiness 判定；缺失时标注，厂商自报标注未独立验证） | 2 |

## Handoff Format

> 本节记录 outline 阶段对下游 deep-draft 与最终 promotion 的交付约定，便于 Orchestrator/Review/后续 deep-draft 对齐。不替代 squad 协议模板。

- **Deep-draft 产物**：`evm-privacy-research/research-sections/eea-enterprise-benchmark/drafts/round-{n}.md`，按 item-1…item-7 顺序成节，含 diag-1…diag-6，逐结论附来源标签（`[EEA §XX]` / `[内部路径 + commit]` / `[WHI-254 item-N §M]` / 官方文档 + 访问日期 / `[推论]` / `[未独立验证]`）。
- **Artifact Ready: deep-draft** 与本 outline 的 **Artifact Ready: outline** 一致使用 squad 模板：含 issue_id / project_slug / topic_slug / phase / round，单一 Orchestrator mention（`Target agent`），`Next action` 纯文本同名。
- **Final 交付**（lightweight 模式）：review 接受后 promote 到 `final.md`，post **Final Promotion Ready（lightweight 变体，无 Index Entry Proposal）** → Orchestrator 集成到 main、删分支、跑 10 项 Done Gate、发 closing comment。本 issue 无 report_issue_id，不做 TW handoff / Research Complete。
- **验收对齐**：7 方案 × 8 需求全覆盖；R4 合约逻辑隐私显式标注；Paladin 复用映射 + 易变事实核验；每方案 Mantle verdict；外部结论附访问日期/版本；厂商自报标注未独立验证；内部来源附 commit SHA。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create | (all) | Initial outline created from Orchestrator dispatch (outline phase, round 1). | agent:research-agent (Deep Research Agent) |
