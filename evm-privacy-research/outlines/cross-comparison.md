---
topic: "EVM 隐私方案横向对比分析（[M2-对比] WHI-262）"
project_slug: "evm-privacy-research"
topic_slug: "cross-comparison"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "evm-privacy-research/outlines/cross-comparison.md"
  draft: "evm-privacy-research/research-sections/cross-comparison/drafts/round-{n}.md"
  final: "evm-privacy-research/research-sections/cross-comparison/final.md"
  index: "evm-privacy-research/research-sections/_index.md"

scope: |
  将 evm-privacy-research 上游 8 个 section（WHI-254 框架/rubric、WHI-255 ERC-7984/7945、WHI-256 VOSA、
  WHI-257 Privacy EIP 全景、WHI-258 机密协处理器、WHI-259 Aztec、WHI-260 ZK Shielded-Pool、WHI-261 EEA
  企业 benchmark）全部标准与竞品，按 WHI-254 的统一五轴 rubric、R1–R8 需求体系、选择性披露 6 维向量、
  轻量级判定标准、隐私账本二义口径，汇总为一张横向对比主矩阵（方案 × 全维度，含 EEA 7 方案与合约逻辑隐私
  R4），并按三关键轴——「部署形态/轻量级」「合规-选择性披露」「是否覆盖合约逻辑隐私」——分组裁决，识别
  契合 Mantle 的候选集合。
  本 issue **不引入新调研**，只做交叉对比、去重与口径归一；每个结论须可回溯到上游 section 的 final.md
  源路径 + commit SHA（base_commit 1eac19ed）。bolt-on 候选（Zama/Inco/Fhenix、Railgun/Privacy Pools、
  VOSA、COTI-Coprocessor、Paladin、Stealth/ERC 系列）与独立链/企业链 benchmark（Aztec/Starknet/COTI-L2/
  Nightfall/Prividium/Linea/Polygon CDK/Silent Data）进入主裁决矩阵；Oasis Sapphire / Secret / Automata
  （+ 可选 Solana / Tornado）仅作 sidebar/reference，不与 EEA 7 方案同权重进入主裁决矩阵。

audience: "Mantle 工程团队、协议/基础设施负责人、企业金融/RWA/BD 团队、隐私方案评估决策者、后续策略 issue"

expected_output: |
  一份中文结构化研究 section，包含：
  - 方案全集合并清单（上游 8 section 的全部标准/竞品，去重 + 口径归一，标注源路径 + commit SHA）
  - 横向对比主矩阵（方案 × 全维度：技术家族 / R1–R5,R8 原语 / R4 合约逻辑 / 信任模型 / 部署形态+轻量级 /
    选择性披露 6 维向量 / 隐私账本 A/B / 成熟度 / Mantle verdict），含 EEA 7 方案与合约逻辑隐私
  - 四张分组视图：①部署形态分组（bolt-on 候选 vs 独立链/企业链 benchmark vs sidebar）②合规-选择性披露
    分组（按 6 维向量 sub-taxonomy）③原语覆盖矩阵（金额/余额/身份/图/逻辑/状态/订单流 各由谁满足）
    ④合约逻辑隐私分组 +「私密 token ledger (A) vs 私密业务状态 (B)」候选集合
  - 每方案「候选/参考/出局 + 理由」，可回溯到上游 section 源路径
  - 口径差异与未独立验证项登记表（跨 section 的去重冲突、成熟度词表归一、各 section 自报 caveat 汇总）
  - 图表：主矩阵、部署形态分组/谱、合规-选择性披露分组、原语覆盖矩阵、Ledger A/B 候选集合、候选/参考/出局决策视图
  - 每结论附上游 final.md 路径 + commit SHA（base_commit 1eac19ed）；不重新做外部核验，沿用上游已标注的
    访问日期/版本与「未独立验证」标签；新引入的跨 section 推断显式标注 [cross-comparison 推论]

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23T13:20:15Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-23T13:20:15Z"

multica_issue_id: "836219a8-d7c5-49d7-af1a-cb9335b19072"
report_issue_id: "68d01fa3-fdaa-4b11-b9e4-e449dfafe39c"
branch_name: "research/evm-privacy-research/cross-comparison"
base_commit: "1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0"
language: "中文"
research_depth: "synthesis-cross-comparison"
mode: "single-issue-composable"

primary_sources:
  - name: "privacy-landscape-framework（WHI-254）final.md — 框架 + 统一 rubric（口径锚）"
    url: "evm-privacy-research/research-sections/privacy-landscape-framework/final.md"
    commit: "1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0"
    usage: "引用五轴 rubric、R1–R8 需求体系、选择性披露 6 维向量、轻量级判定标准（含 V1–V4 一票否决）、隐私账本二义口径（A/B）、EEA Readiness Matrix 三阶段——作为本 issue 全部列定义与评分口径的唯一锚点；COTI-L2/COTI-Coprocessor 拆分口径沿用此 section"
  - name: "erc7984-confidential-token（WHI-255）final.md"
    url: "evm-privacy-research/research-sections/erc7984-confidential-token/final.md"
    commit: "1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0"
    usage: "ERC-7984 / ERC-7945 标准的五轴评分、值级隐私(A)定位、ObserverAccess/Hooked 选择性披露扩展、ACL 撤销性 caveat（M2/M3）"
  - name: "vosa-standards（WHI-256）final.md"
    url: "evm-privacy-research/research-sections/vosa-standards/final.md"
    commit: "1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0"
    usage: "VOSA / VOSA-20 / VOSA-RWA 的 ZK 合约套件部署形态、exposed-graph 模型、compliance-gate（keyHash 语义纠偏）、Concept/Pre-pilot 成熟度"
  - name: "privacy-eips-survey（WHI-257）final.md"
    url: "evm-privacy-research/research-sections/privacy-eips-survey/final.md"
    commit: "1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0"
    usage: "ERC-5564/6538、EIP-8182、ERC-8065、ERC-8302/pERC-20、EIP-7503/8093/8250/8141/8105、Privacy Pools 的协议层 vs 应用层定位、Stealth Address 能力边界（仅 R3）、EIP-8105 非隐私定性"
  - name: "confidential-coprocessor（WHI-258）final.md"
    url: "evm-privacy-research/research-sections/confidential-coprocessor/final.md"
    commit: "1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0"
    usage: "Zama fhEVM / Inco Lightning / Fhenix CoFHE 三个 bolt-on 协处理器的信任模型差异（crypto+org+hw / hw / crypto+econ）、A+B 覆盖、FHE-ACL 撤销性结构缺陷、各自成熟度（Zama ETH GA / Inco Base GA / Fhenix testnet）"
  - name: "zk-privacy-chain-aztec（WHI-259）final.md"
    url: "evm-privacy-research/research-sections/zk-privacy-chain-aztec/final.md"
    commit: "1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0"
    usage: "Aztec 全执行隐私(A+B)、纯密码学信任、独立非 EVM 链一票否决(V1/V2)、Pilot-Alpha 成熟度 + 未修复 critical 漏洞、benchmark-only 判定与可借鉴/不可移植边界"
  - name: "zk-shielded-pool（WHI-260）final.md"
    url: "evm-privacy-research/research-sections/zk-shielded-pool/final.md"
    commit: "1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0"
    usage: "Railgun / Privacy Pools(0xbow) / Starknet STRK20 / Tornado 的部署形态(EVM 合约套件 vs Cairo VM 绑定)、三套选择性披露模型(viewing-key+PPOI / association-set+ASP+ragequit / 加密 viewing-key)、Tornado「无披露=死局」教训"
  - name: "eea-enterprise-benchmark（WHI-261）final.md"
    url: "evm-privacy-research/research-sections/eea-enterprise-benchmark/final.md"
    commit: "1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0"
    usage: "EEA 7 方案(Paladin/Prividium/Linea/Nightfall/COTI-L2/COTI-Coprocessor/Polygon CDK/Silent Data)的 7×8 benchmark、R4 token-only vs contract-logic 标注、Mantle 候选/参考/出局初判、Sapphire/Secret/Automata/Solana sidebar 及其 sidebar-only 理由"

prerequisite_sections:
  - topic_slug: "privacy-landscape-framework"
    dependency_type: "framework"
    usage: "唯一口径锚——五轴 rubric / R1–R8 / 6 维披露向量 / 轻量级判定 / 隐私账本 A/B / Readiness Matrix"
  - topic_slug: "erc7984-confidential-token"
    dependency_type: "input-section"
    usage: "ERC-7984 / ERC-7945 行的源数据"
  - topic_slug: "vosa-standards"
    dependency_type: "input-section"
    usage: "VOSA 系列行的源数据"
  - topic_slug: "privacy-eips-survey"
    dependency_type: "input-section"
    usage: "Stealth / 协议层 EIP / 应用层 ERC 行的源数据"
  - topic_slug: "confidential-coprocessor"
    dependency_type: "input-section"
    usage: "Zama / Inco / Fhenix 行的源数据"
  - topic_slug: "zk-privacy-chain-aztec"
    dependency_type: "input-section"
    usage: "Aztec 行的源数据"
  - topic_slug: "zk-shielded-pool"
    dependency_type: "input-section"
    usage: "Railgun / Privacy Pools / Starknet STRK20 / Tornado 行的源数据"
  - topic_slug: "eea-enterprise-benchmark"
    dependency_type: "input-section"
    usage: "EEA 7 方案 + sidebar 行的源数据"
---

# Research Outline: EVM 隐私方案横向对比分析（[M2-对比] WHI-262）

> 本 section 是 evm-privacy-research 系列的**收敛/裁决**视角：把分散在 8 个上游 section 的全部标准与竞品，按 WHI-254 的统一口径汇总为**一张主矩阵 + 四张分组视图**，并对每个方案给出可回溯的「候选/参考/出局」裁决。本 outline **不重复定义任何评估维度**——全部引用 WHI-254 的 rubric；也**不引入任何新调研**——只做交叉对比、去重、口径归一与未验证项登记。本 issue 的增量价值在于「收敛为可决策视图」，而非新增事实。

## Research Questions

1. 上游 8 个 section 一共覆盖了哪些方案？去重（同一方案被多个 section 提及，如 ERC-7984 出现在 WHI-255/258/261、Privacy Pools 出现在 WHI-257/260、EIP-8105 出现在 WHI-254/257、COTI 出现在 WHI-254/261）后，进入主裁决矩阵的方案全集是什么？哪些仅作 sidebar/reference？
2. 在 WHI-254 五轴 rubric 下，全部方案的横向对比主矩阵（方案 × 全维度，含 R4 合约逻辑隐私）如何填充？各 section 自带的评分是否口径一致（成熟度词表、●/◐/○ 标度），需要哪些归一？
3. 按部署形态/轻量级分组：哪些方案通过 WHI-254 V1–V4 一票否决成为真正的 bolt-on 候选？哪些是独立链/企业链 benchmark（被否决）？为什么 Sapphire/Secret/Automata 只能作 sidebar 而不与 EEA 7 方案同权重？
4. 按选择性披露 6 维向量 sub-taxonomy 分组：各方案落在 viewing-key / observer / association-set / compliance-gated / privacy-group / exposed-graph / 无 的哪一类（可多标签）？哪些类别满足 Mantle 的合规-审计需求？
5. 原语覆盖矩阵：金额(R1)/余额(R2)/身份(R3)/图(R5)/合约逻辑(R4)/合约状态(R4)/订单流(R8) 各由哪些方案满足？哪些维度存在候选缺口（如纯 bolt-on 候选中谁能覆盖 R4）？
6. 区分「私密 token ledger（A，值级）」与「私密业务状态（B，执行/状态级）」两类需求：各自的候选集合是什么？bolt-on 候选里能提供 B 类隐私的方案有哪些？
7. 综合三关键轴（部署形态/轻量级 × 合规-选择性披露 × R4 合约逻辑隐私），每个方案对 Mantle 的「候选/参考/出局 + 理由」裁决是什么？各结论回溯到哪个上游 final.md 路径？

## Items

### item-1: 方案全集合并与横向对比主矩阵（含跨 section 去重与口径归一）

**对应执行步骤 Step 1。** 汇总上游 8 section 的全部方案到一张统一 rubric 主矩阵。这是本 issue 的核心交付物与后续四张分组视图的共同数据源。**先去重 + 口径归一，再填充矩阵**，否则同一方案在不同 section 的评分会冲突。

**1.1 方案全集合并清单（去重后，标注源路径）**：下表为 deep-draft 须确认的方案全集（每行须落到一个 canonical 行 + 主源 section；被多 section 覆盖的方案标注「主源 / 旁证」）。**待 draft 核对，下列为基于上游 final.md 的合并假设：**

| # | Canonical 方案 | 主源 section（final.md）| 旁证 section | 进入主矩阵? |
|---|---|---|---|:---:|
| 1 | ERC-7984 Confidential Fungible Token | erc7984-confidential-token (WHI-255) | confidential-coprocessor(Zama 为 ref impl)、eea-benchmark | ✓ |
| 2 | ERC-7945 Confidential Transactions Supported Token | erc7984-confidential-token (WHI-255) | — | ✓ |
| 3 | VOSA / VOSA-20 | vosa-standards (WHI-256) | — | ✓ |
| 4 | VOSA-RWA | vosa-standards (WHI-256) | — | ✓ |
| 5 | ERC-5564 + ERC-6538 Stealth Addresses | privacy-eips-survey (WHI-257) | vosa(stealth 派生复用)、framework §06b | ✓ |
| 6 | ERC-8065 ZK Token Wrapper | privacy-eips-survey (WHI-257) | — | ✓ |
| 7 | ERC-8302 / pERC-20 Private Fungible Tokens | privacy-eips-survey (WHI-257) | vosa(pERC-20 关系存疑，见 caveat) | ✓ |
| 8 | EIP-8182 Private ETH/ERC-20 Transfers | privacy-eips-survey (WHI-257) | — | ✓（协议层）|
| 9 | EIP-7503 ZK Wormholes | privacy-eips-survey (WHI-257) | — | ✓（协议层）|
| 10 | EIP-8093 Private ERC-20 ZK Burns | privacy-eips-survey (WHI-257) | — | ✓（状态不可核验，标注）|
| 11 | EIP-8250 Keyed Nonces / EIP-8141 Frame Tx (AA) | privacy-eips-survey (WHI-257) | — | 参考（基础设施，非隐私原语）|
| 12 | EIP-8105 Universal Encrypted Mempool | privacy-eips-survey (WHI-257) | framework §2.3/§06b | 参考（R8 反 MEV，非用户隐私）|
| 13 | Zama fhEVM | confidential-coprocessor (WHI-258) | erc7984(ERC-7984 ref impl) | ✓ |
| 14 | Inco Lightning | confidential-coprocessor (WHI-258) | — | ✓ |
| 15 | Fhenix CoFHE | confidential-coprocessor (WHI-258) | — | ✓ |
| 16 | Railgun | zk-shielded-pool (WHI-260) | — | ✓ |
| 17 | Privacy Pools (0xbow) | zk-shielded-pool (WHI-260) | privacy-eips-survey | ✓ |
| 18 | Starknet STRK20 (Shieldnet) | zk-shielded-pool (WHI-260) | aztec(Noir/Starknet 提及) | ✓（benchmark）|
| 19 | Aztec | zk-privacy-chain-aztec (WHI-259) | — | ✓（benchmark）|
| 20 | COTI-L2 | eea-enterprise-benchmark (WHI-261) | framework | ✓（benchmark）|
| 21 | COTI-Coprocessor | eea-enterprise-benchmark (WHI-261) | framework | ✓（bolt-on 候选）|
| 22 | Nightfall (EY) | eea-enterprise-benchmark (WHI-261) | framework | ✓（benchmark）|
| 23 | Paladin (Kaleido) | eea-enterprise-benchmark (WHI-261) | framework | ✓（bolt-on 候选）|
| 24 | Prividium (ZKsync) | eea-enterprise-benchmark (WHI-261) | framework | ✓（benchmark）|
| 25 | Linea Enterprise (Consensys) | eea-enterprise-benchmark (WHI-261) | framework | ✓（benchmark）|
| 26 | Polygon CDK Enterprise | eea-enterprise-benchmark (WHI-261) | framework | ✓（benchmark）|
| 27 | Silent Data (Applied Blockchain) | eea-enterprise-benchmark (WHI-261) | framework | ✓（benchmark）|
| S1 | Oasis Sapphire | eea-enterprise-benchmark (WHI-261) §6.1 | — | sidebar（非主矩阵权重）|
| S2 | Secret Network (SecretEVM 暂停) | eea-enterprise-benchmark (WHI-261) §6.2 | — | sidebar |
| S3 | Automata (TEE attestation verifier) | eea-enterprise-benchmark (WHI-261) §6.3 | confidential-coprocessor(TEE 路线) | sidebar（bolt-on 验证积木）|
| S4 | Solana Confidential Transfers | eea-enterprise-benchmark (WHI-261) §6.4 | — | sidebar（非 EVM 对照）|
| S5 | Tornado Cash | zk-shielded-pool (WHI-260) item-6 | privacy-eips-survey | sidebar（合规教训：无披露=死局）|

**1.2 口径归一规则**（cross-comparison 须先定义，否则矩阵不可比）：
- **成熟度词表归一**：上游使用了不同的成熟度词表——EEA Readiness Matrix（Pilot / Early Production / GA，WHI-261/254）、VOSA 自定义（Concept / Pre-pilot，WHI-256）、EIP 状态（Draft / Final / Stagnant / Open PR / 不可核验，WHI-257）、产品 GA（Zama ETH-GA / Inco Base-GA / Fhenix testnet，WHI-258）、Railgun/PP（GA / Early production，WHI-260）。须归一为一列「统一成熟度 + 原始词表 + 源路径」，不臆造跨词表等价，缺证据处标注。
- **标度归一**：原语保护用 ●（完全）/◐（部分）/○（不保护），与 WHI-254 §3.2 轴 2 一致；信任模型用 Cryptographic / Hardware-Anchored / Organizational / 混合；部署形态用 bolt-on 协处理器 / 链上合约套件 / 独立链或 VM / 协议层硬分叉。
- **去重裁决**：被多 section 覆盖的方案以「主源 section」评分为准，旁证 section 仅作交叉校验；若主源与旁证冲突，记入 item-6 口径差异表，不在矩阵单元格内静默选边。

**1.3 主矩阵列定义**（= Fields 节字段，全部锚定 WHI-254）：方案 / 技术家族（轴 1）/ R1 金额 / R2 余额 / R3 身份 / R5 图 / R4 合约逻辑 / R4 合约状态 / R8 订单流（轴 2，7 维）/ 信任模型（轴 3）/ 部署形态 + 轻量级判定（轴 4）/ 选择性披露 6 维向量摘要（轴 5）/ 隐私账本 A/B / 统一成熟度 / Mantle verdict / 源路径。

**1.4 主矩阵填充**：逐行填充上述 27 个主矩阵方案（COTI 保持 L2 / Coprocessor 双行）。每个单元格须可回溯到主源 final.md 的具体小节；新引入的跨 section 横向推断标注 `[cross-comparison 推论]`。

- **Priority**: high
- **Dependencies**: none

### item-2: 分组视图① 部署形态 / 轻量级 — bolt-on 候选 vs 独立链/企业链 benchmark vs sidebar

**对应执行步骤 Step 2。** 第一关键轴。按 WHI-254 轻量级判定（V1 新链/VM、V2 新桥、V3 全节点运维、V4 硬分叉一票否决 + 通用/路线专属指标）对主矩阵全集分组，明确 bolt-on 候选集合。

**2.1 三组划分**（待 draft 以 WHI-254 判定逐方案确认；下表为基于上游的分组假设）：
- **A. Bolt-on 候选**（通过 V1–V4，链上合约套件 / 协处理器）：ERC-7984、ERC-7945、ERC-5564/6538、ERC-8065、ERC-8302/pERC-20、VOSA/VOSA-20、VOSA-RWA、Zama fhEVM、Inco Lightning、Fhenix CoFHE、Railgun、Privacy Pools、COTI-Coprocessor、Paladin（轻量~中量级边界）。
- **B. 独立链/企业链 benchmark**（被一票否决）：Aztec（V1/V2 非 EVM 独立链）、Starknet STRK20（V1 绑 Cairo VM）、COTI-L2（V1/V2 需 COTI 网络+桥）、Nightfall（V3 rollup operator，中量级）、Prividium、Linea Enterprise、Polygon CDK、Silent Data（均独立链，V1/V2/V3）。
- **C. 协议层**（V4 硬分叉，单列）：EIP-8182、EIP-7503、EIP-8093、EIP-8250/8141、EIP-8105——L1 协议层方案，Mantle 不能 bolt-on，作架构参考。
- **Sidebar**：Oasis Sapphire（独立 ParaTime + OPL 桥）、Secret（EVM 路线暂停）、Automata（非隐私引擎，仅 TEE 验证积木——是少数真正可 bolt-on 的组件，但须与 TEE 执行环境组合）、Solana（非 EVM）、Tornado（合规死局教训）。

**2.2 为什么 Sapphire/Secret/Automata 仅作 sidebar**（验收硬要求，回溯 WHI-261 §6）：Sapphire 需独立网络 + OPL 桥（非 1:1 L2 隐私替代）；Secret 的机密 EVM 路线 2026 已正式暂停（cost-to-benefit 不成立）；Automata 本身不是机密执行引擎而是 TEE attestation 验证层（须与 TEE 执行组合）。三者均不与 EEA 7 方案同权重进入主裁决矩阵，仅作信任模型/部署形态参考。

**2.3 轻量级一票否决核对**：对 B 组每方案标注被哪条 V1–V4 否决；对 A 组每方案标注通过判定 + 路线专属成本指标摘要（ZK 约束数 / FHE 密文膨胀 / TEE 硬件依赖 / GC 交互轮数 / PG 节点数）。须与 WHI-254 §5.6 及各 section 的轻量级判定一致；不一致记入 item-6。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 分组视图② 合规-选择性披露 — 按 6 维向量 sub-taxonomy 分组

**对应执行步骤 Step 3。** 第二关键轴。按 WHI-254 选择性披露 6 维向量（authority × trigger × payload × scope × revocability × leakage）将主矩阵全集按 sub-taxonomy 分组，对应 dispatch 列出的：viewing-key / observer / association-set / compliance-gated / privacy-group / exposed-graph / 无。

**3.1 sub-taxonomy 分组**（方案可多标签；待 draft 逐方案落位）：
- **viewing-key（密钥分发披露）**：COTI（key-holder + viewing-key-share）、Nightfall、Railgun（永久不可撤销 viewing-key）、Aztec（ZK plaintext-to-ciphertext 证明；tagging-key 为保留）、Inco（delegated viewing）、ERC-7984 ObserverAccess、Starknet STRK20（加密 viewing-key，机制未验证）。
- **observer / notary（公证方/观察者）**：Paladin/Noto（notary/observer + key-holder）、Linea Enterprise（operator observer）、Polygon CDK（operator）、ERC-7984 ObserverAccess（账户级观察者）。
- **association-set（合规集合）**：Privacy Pools（inclusion+exclusion + ASP + ragequit）、Railgun PPOI（仅排除）。
- **compliance-gated（准入门控）**：Nightfall（X.509 KYC-gate）、Prividium（Okta SSO）、Polygon CDK（enterprise SSO）、VOSA-RWA（链下合规服务 attestation）、Inco（programmable AML/KYC）、Privacy Pools（withdrawal gate）。
- **privacy-group / domain（域级共享）**：Paladin privacy domains、Linea Enterprise permissioned validium、Polygon CDK permissioned access、Prividium permissioned L2。
- **exposed-graph（残余图泄露 by design）**：VOSA / VOSA-20（one-time address 但 graph 暴露）、ERC-7984/7945（账户地址公开，金额加密）、Stealth Addresses（金额/发送方明文）。
- **无 / 死局**：Tornado（无披露通道 → OFAC 死局，反面教材）；纯基础设施（EIP-8250/8141）不适用。

**3.2 合规-审计满足度归并**：复用 WHI-254 §4.5 合规映射（GDPR / MiCA-Travel Rule / AML-CFT / 金融审计），跨方案归并「哪些方案满足/部分满足/不满足」各合规要求，重点标注 revocability 与 auditable-log 的已验证 vs 声称（unverified-revocable / partial-auditable-log / FHE-ACL 不可撤销结构缺陷）。

**3.3 Mantle 合规视角**：指出对 institutional Mantle 同时需 MiCA/Travel Rule + 金融审计时，哪些 sub-taxonomy 组合可满足（如 compliance-gated + auditable-log + 可撤销），以及 bolt-on 候选在此轴上的缺口（如纯 viewing-key 方案缺 compliance-gate / auditable-log）。

- **Priority**: high
- **Dependencies**: item-1

### item-4: 分组视图③ 原语覆盖矩阵 — 金额/余额/身份/图/逻辑/状态/订单流各由谁满足

**对应执行步骤 Step 4（前半）。** 第三关键轴的基础。**转置主矩阵的轴 2**：以 7 项被保护数据维度为行、方案为列，回答「每项原语由哪些方案满足（●/◐）」，识别每个维度的候选集合与缺口。

**4.1 原语 → 满足方案 反查表**（待 draft 从 item-1 主矩阵转置生成）：
- **R1 金额 / R2 余额**：覆盖最广（几乎所有值级方案）——列出完全保护(●)集合。
- **R3 身份**：Stealth Addresses（密码学匿名）、Aztec（●）、Railgun/PP（●）；permissioned 方案多为 ◐（身份隔离非密码学匿名）。
- **R5 转账图**：Railgun/PP/Aztec/Stealth（●，匿名集/unlinkability）vs VOSA/ERC-7984/COTI（exposed-graph 或 deposit/withdraw 暴露）。
- **R4 合约逻辑 / R4 合约状态**：**本 issue 重点缺口分析**——哪些方案覆盖 R4（Aztec ●、Silent Data ●、Linea ●、Prividium ●、Zama/Inco/Fhenix ●、Paladin ◐、COTI ◐、Polygon CDK 可配置）vs 仅值级（Nightfall/Railgun/PP/VOSA/ERC-7984/Stealth = ○）。
- **R8 订单流**：TEE 路线（Silent Data ◐）、EIP-8105（协议层 R8 专门方案，但非用户隐私）；绝大多数 ○。

**4.2 维度候选缺口标注**：对每个原语维度，特别标注「**bolt-on 候选集合内**谁能满足」——例如 R4 在 bolt-on 候选内仅 Zama/Inco/Fhenix（协处理器）+ Paladin(◐) + COTI-Coprocessor(◐,announced) 能覆盖，纯 shielded-pool/ERC 标准均不覆盖 R4。此缺口直接喂给 item-5。

- **Priority**: high
- **Dependencies**: item-1

### item-5: 分组视图④ 合约逻辑隐私 +「私密 token ledger (A) vs 私密业务状态 (B)」候选集合

**对应执行步骤 Step 4（后半）。** 第三关键轴的裁决。复用 WHI-254 隐私账本二义口径（A = token ledger 值级 / B = business-state ledger 执行+状态级），把方案按 A / B / A+B 分类，并给出**两类需求各自的候选集合**——这是本 issue 对策略层的核心增量。

**5.1 A/B 分类**（待 draft 以上游证据逐方案确认；下表为合并假设）：
- **纯 A（token ledger）**：ERC-7984、ERC-7945、ERC-8065、ERC-8302、VOSA/VOSA-20/VOSA-RWA、Railgun、Privacy Pools、Starknet STRK20、Nightfall。
- **纯 B（business-state ledger）**：Silent Data（TEE 全执行）、Linea Enterprise（state-level validium）。
- **A+B（兼备）**：Aztec（密码学全执行）、Prividium、Polygon CDK（可配置）、Zama fhEVM、Fhenix CoFHE、Inco（state-capable）、Paladin（Noto=A / Pente=B 共存）、COTI-L2 / COTI-Coprocessor（A + B 部分，开发者标注；Coprocessor announced）。
- **N/A / 原语**：Stealth Addresses（身份原语）、协议层 EIP（混合）。

**5.2 两类需求候选集合**（核心裁决）：
- **「私密 token ledger」需求的候选集合**（值级即可，不需 R4）：在 bolt-on 候选内 = ERC-7984(+Zama/Inco ref impl)、Railgun、Privacy Pools、VOSA-20/RWA、ERC-8065/8302、Stealth(补身份)。
- **「私密业务状态」需求的候选集合**（必须 R4 合约逻辑/状态）：在 bolt-on 候选内 = Zama fhEVM、Inco Lightning、Fhenix CoFHE、COTI-Coprocessor（announced）、Paladin（域内可见，◐）；独立链 benchmark 的 B 类（Aztec/Silent Data/Linea/Prividium）作能力上界参考但不可 bolt-on。

**5.3 对 Mantle 的意义**：明确指出 token-only 方案不能替代需要业务状态隐私的 institutional 场景（RWA 全生命周期、机构间合约、合规计算），并点出「既要 bolt-on 又要 R4」的候选极窄（协处理器路线 + Paladin），与 WHI-254 §5.6「轻量级 vs 成熟度 tradeoff」结论衔接。

- **Priority**: high
- **Dependencies**: item-1, item-4

### item-6: 逐方案候选/参考/出局裁决 + 口径差异与未独立验证项登记

**对应执行步骤 Step 5。** 综合三关键轴（item-2 部署形态 × item-3 合规披露 × item-5 R4），对每个方案给出最终「候选/参考/出局 + 理由」，并登记跨 section 的口径差异与未验证项。

**6.1 三档 verdict 定义 + 逐方案裁决**：
- **候选（Candidate）**：架构可 bolt-on 到 Mantle + 具备所需隐私能力 + 成熟度可接受——预期含 Zama fhEVM、Inco Lightning、Railgun、Privacy Pools、ERC-7984、Stealth Addresses、Paladin、COTI-Coprocessor（附成熟度风险）；Fhenix/VOSA/ERC-8065/8302 作「候选（条件/早期）」。
- **参考（Reference）**：不可直接集成但有可借鉴的设计/原语/合规模型——预期含 Aztec（密码学全执行上界）、Silent Data（TEE 范式 + Automata 验证）、Prividium（合规向量最完整）、Linea（状态级范式）、Nightfall（值级标准）、协议层 EIP（L1 架构参考）、Sapphire/Solana/Tornado（信任模型/合规教训）。
- **出局（Out）**：部署形态与 Mantle 轻量级偏好根本冲突且无独特借鉴价值——预期含 COTI-L2（GA 但 V1/V2 否决）、Starknet STRK20（绑 VM + 未审计）、Secret（EVM 路线暂停）；按证据判定。

**6.2 每方案理由 + 源路径回溯**（验收硬要求）：每条 verdict 须给出（a）三关键轴的判定摘要，（b）回溯到的上游 final.md 路径 + commit SHA。

**6.3 口径差异 / 去重冲突登记**（cross-comparison 专有产物）：登记跨 section 的不一致与待澄清项，至少覆盖：
- ERC-7984 在 WHI-255（标准，token-only A）vs WHI-258（Zama ref impl，A+B 含合约状态）的覆盖口径差异——同一 handle 模型，标准层仅值级、Zama 实现层含合约状态，须明确「standard vs implementation」边界。
- Privacy Pools 在 WHI-257（标为 A+B，compliance-gated pool）vs WHI-260（标为纯 A token ledger）的账本分类差异。
- EIP-8105 / EIP-8141 / EIP-8250 的「related-non-privacy」定性（WHI-257）——不应作为用户隐私方案进入候选。
- VOSA pERC-20 与 EIP-8287/ERC-8302 pERC-20 的身份关系存疑（WHI-256 gap）。
- COTI-L2 / COTI-Coprocessor 拆分口径（WHI-254/261）——两模式共享 R4 等级，差异在部署形态与成熟度/置信度。

**6.4 未独立验证项汇总**（沿用上游标签，不重新核验）：汇总各 section 已标注的「未独立验证 / 声称 / caveat」，例如——FHE-ACL 不可撤销（Zama OZ v0.5 审计确认，Inco/Fhenix 未验证）、COTI revocability=unverified-revocable、Paladin auditable-log=partial、Nightfall viewing-key one-time、Silent Data 审计透明度缺口（EEA「Not disclosed」）、Fhenix mainnet 状态 blog/docs 矛盾、Aztec v4 critical 漏洞未修复 + tagging-key 保留、Starknet STRK20 加密 viewing-key/审计均未验证、各厂商自报客户/性能数据「press-reported 未独立验证」、WHI-261 carry-forward caveat（EEA 事实层继承自 WHI-254 同日 HTML 提取，对外决策须重新核验）。**本 issue 不消解这些缺口，只做集中登记并提示下游策略 issue。**

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| scheme_family | Canonical 方案名 + 技术家族（FHE/GC/MPC/TEE/ZKP/Privacy-Group/Stealth/混合），对齐 WHI-254 轴 1 | all |
| source_path | 该行/单元格回溯到的上游 final.md 路径 + commit SHA（base_commit 1eac19ed）+ 具体小节；多源时标注主源/旁证 | all |
| primitive_coverage | R1 金额 / R2 余额 / R3 身份 / R5 图 / R4 合约逻辑 / R4 合约状态 / R8 订单流 各自保护级别：●完全 / ◐部分 / ○不保护 / 未明确（对齐 WHI-254 轴 2） | item-1, item-4 |
| contract_logic_privacy | R4 合约逻辑/业务状态隐私：token-only(A) / 执行级(B) / 状态级(B) / A+B / 部分；及机制——本 issue 重点列 | item-1, item-4, item-5 |
| trust_model | 信任模型（Cryptographic / Hardware-Anchored / Organizational / 混合）+ 具体信任假设清单，对齐 WHI-254 轴 3 | item-1, item-6 |
| deployment_veto | 部署形态（bolt-on 协处理器 / 链上合约套件 / 独立链或 VM / 协议层硬分叉）+ WHI-254 轻量级判定（V1–V4 一票否决结果 + 通过/否决）| item-1, item-2 |
| disclosure_vector | 选择性披露 6 维向量（authority × trigger × payload × scope × revocability × leakage）+ sub-taxonomy 分组标签（viewing-key/observer/association-set/compliance-gated/privacy-group/exposed-graph/无）| item-1, item-3 |
| ledger_type | 隐私账本分类：Token Ledger(A) / Business-State Ledger(B) / A+B / N/A（对齐 WHI-254 item-6 二义口径）| item-1, item-5 |
| maturity_unified | 统一成熟度（含原始词表映射：EEA Pilot/Early/GA、VOSA Concept/Pre-pilot、EIP Draft/Final/Stagnant、产品 GA/testnet）+ 源路径；不臆造跨词表等价 | item-1, item-2, item-6 |
| mantle_verdict | 三关键轴综合后的 候选/参考/出局 + 一句理由 + 关键 tradeoff | item-2, item-6 |
| caliber_caveat | 口径差异（跨 section 去重冲突）/ 未独立验证标签（沿用上游 caveat，不重新核验）/ [cross-comparison 推论] 标注 | item-1, item-6 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison / matrix | **横向对比主矩阵**（核心交付图）：行=27 主矩阵方案（COTI 拆 L2/Coprocessor 双行），列=技术家族 / R1 / R2 / R3 / R5 / R4 逻辑 / R4 状态 / R8 / 信任模型 / 部署形态+轻量级 / 披露向量摘要 / 账本 A/B / 成熟度 / verdict；单元格 ●/◐/○ 或分类标签，每方案末列附源路径 | ascii (table) | item-1 |
| diag-2 | spectrum / grouping | **部署形态分组视图 + 谱**：左(bolt-on 候选)→中(协议层)→右(独立链/企业链 benchmark)，标注 V1–V4 一票否决阈值线与各方案位置；sidebar(Sapphire/Secret/Automata/Solana/Tornado) 单列于谱外（复用并扩展 WHI-254 diagram-4 / WHI-261 diag-4）| ascii / mermaid | item-2 |
| diag-3 | comparison / grouping | **合规-选择性披露分组视图**：按 6 维向量 sub-taxonomy（viewing-key / observer / association-set / compliance-gated / privacy-group / exposed-graph / 无）分组列出方案（多标签），叠加 GDPR/MiCA/AML/审计 满足度 | mermaid / ascii (table) | item-3 |
| diag-4 | comparison / matrix | **原语覆盖矩阵**（轴 2 转置）：行=7 原语（R1/R2/R3/R5/R4 逻辑/R4 状态/R8），列=方案；单元格 ●/◐/○；每行末标注「bolt-on 候选内满足者」缺口 | ascii (table) | item-4 |
| diag-5 | hierarchy / sets | **Ledger A/B 候选集合视图**：方案按 纯 A / 纯 B / A+B 分层；并以集合图标注「私密 token ledger 需求候选集」与「私密业务状态需求候选集」（bolt-on 子集高亮）| mermaid | item-5 |
| diag-6 | flow / decision | **候选/参考/出局决策视图**：三关键轴（部署形态/轻量级 → 合规披露 → R4）漏斗 + 每方案 verdict 落位，决策视角核心图 | mermaid | item-6 |

## Source Requirements

> **本 issue 为纯交叉对比综合（synthesis），不引入新外部调研。** 因此 source 要求不含「最少 N 篇外部一手/二手来源」——上游 8 个 section 已完成外部核验。本 issue 的 source 要求是「**对 8 个上游 final.md 的穷尽覆盖 + 每个结论的回溯性**」。新外部 web/官方文档检索仅在出现无法用上游解决的去重冲突时按需进行，且须显式标注为本轮新增并附访问日期。

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | framework_reference (anchor) | privacy-landscape-framework（WHI-254）final.md @1eac19ed——五轴 rubric / R1–R8 / 6 维披露向量 / 轻量级判定（V1–V4）/ 隐私账本 A/B / Readiness Matrix，全部列定义与口径的唯一锚 | 1 |
| src-2 | internal_reuse (input sections) | 其余 7 个上游 final.md @1eac19ed（WHI-255/256/257/258/259/260/261）——主矩阵每行的源数据，须全部覆盖、逐行回溯路径 + commit SHA | 7 |
| src-3 | traceability | 主矩阵每个单元格、每张分组视图、每条 verdict 均须可回溯到上述 final.md 的具体小节；新引入的跨 section 横向推断标注 `[cross-comparison 推论]`，不得无源 | all cells |
| src-4 | caveat_carryforward | 上游各 section 已标注的「未独立验证 / caveat / 口径差异」标签须沿用并集中登记（item-6），不在本 issue 重新核验或静默消解 | n/a (汇总) |
| src-5 | on_demand_external (optional) | 仅当出现上游无法解决的去重冲突时按需新增的外部一手来源；须显式标注「本轮新增」+ 访问日期 + 版本/commit；默认期望为 0 | 0 |

## Handoff Format

> 本节记录 outline 阶段对下游 deep-draft / promotion / TW handoff 的交付约定，便于 Orchestrator / Review / 后续 deep-draft 对齐。不替代 squad 协议模板。本 issue 为**composable 单 issue 模式**（含 `report_issue_id` 68d01fa3-fdaa-4b11-b9e4-e449dfafe39c），final-promotion 须附 Index Entry Proposal，且在 Orchestrator 提供 `main_merge_commit` 后做 TW handoff（Research Complete + Done Gate Request）。

- **Deep-draft 产物**：`evm-privacy-research/research-sections/cross-comparison/drafts/round-{n}.md`，按 item-1…item-6 顺序成节，含 diag-1…diag-6，逐结论附来源标签（`[WHI-254 item-N §M]` / `[<topic-slug> final.md §X @1eac19ed]` / `[cross-comparison 推论]` / 沿用上游 `[未独立验证]` 标签）。
- **Artifact Ready** 与本 outline 的 **Artifact Ready: outline** 一致使用 squad 模板：含 issue_id / project_slug / topic_slug / phase / round，单一 Orchestrator mention（`Target agent`），`Next action` 纯文本同名目标。
- **Final 交付（composable 模式）**：review 接受后 promote 到 `final.md`，post **Final Promotion Ready**（含 Index Entry Proposal：order / topic_slug=cross-comparison / multica_issue_id / final_path / dependencies=上游 8 topic-slug / status=done）→ Orchestrator 校验、集成 allowlisted research package + `_index.md` 到 main、删分支 → Research Agent 在 report_issue（68d01fa3…）post Research Complete（附 main_merge_commit）→ post Done Gate Request。
- **验收对齐**：主矩阵覆盖全部输入方案 + 全部 rubric 维度（含 EEA 7、R4 合约逻辑）；四张分组视图齐备、bolt-on 候选集合明确；Sapphire/Secret/Automata 仅作 sidebar（非主矩阵权重）；区分 token ledger(A) vs business-state(B) 候选；每方案 候选/参考/出局 + 理由可回溯源路径 + commit SHA；`_index.md` 行更新（Orchestrator 写）。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create | (all) | Initial outline created from Orchestrator dispatch (outline phase, round 1). Synthesis/cross-comparison topic; no new research, anchors all dimensions to WHI-254 rubric; aggregates 27 main-matrix schemes (+5 sidebar) from 8 upstream final.md. | agent:research-agent (Deep Research Agent) |
