---
topic: "L2Beat Stage 框架最新标准解析（2026 版）"
project_slug: mantle-stage1-rollup
topic_slug: l2beat-stage-framework-2026
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: mantle-stage1-rollup/outlines/l2beat-stage-framework-2026.md
  draft: mantle-stage1-rollup/research-sections/l2beat-stage-framework-2026/drafts/round-{n}.md
  final: mantle-stage1-rollup/research-sections/l2beat-stage-framework-2026/final.md
  index: mantle-stage1-rollup/research-sections/_index.md

scope: |
  完整梳理 L2Beat Stages 框架在 2026 年 5 月时点的所有 Stage 0/1/2 具体要求，
  重点解析 2024.12 - 2026.05 期间的三项重大更新：
  (1) 2024.12 — Proof System 成为 Stage 0 必须项（无 proof system 不再算 Stage 0）；
  (2) 2025.11 — ZK Verifier 可信设置（trusted setup）标准，Stage 1 不允许 🔴 评级；
  (3) 2025.12 — Security Council Walkaway Test ("安全委员会消失后用户仍可安全退出")。
  目的是为后续 Mantle 差距分析（upgrade/exit-window/security-council、proposer 去中心化、
  Stage 1 路线图）提供精确、可引用、可对照的判定基准。本章节是 Mantle Stage 1 项目的第一篇
  基础研究，所有下游主题都将以本章节定义的判定标准为锚点。

audience: |
  Mantle / OP Stack 生态研究者与协议工程师；Multica 研究 squad 内部下游 Research Agent
  （upgrade-exitwindow-securitycouncil、proposer-decentralization-zk-compliance、
  stage1-roadmap-recommendation）；关注 L2 Stage 1/2 合规进展的投研分析师与生态合作伙伴。
  阅读者熟悉 Rollup 基本概念（Optimistic vs ZK、fraud proof、validity proof、Security Council），
  但不一定追踪过 L2Beat 在 2025-2026 年间的每一次框架细则更新。

expected_output: |
  - Stage 0/1/2 完整要求对照表（2026.05 版，覆盖 Proof System / Sequencer / Proposer / Upgrade /
    Exit Window / Security Council / Data Availability / ZK Verifier 八大维度）
  - 2025-2026 年三项重大更新的详细解读（变更前 vs 变更后、生效时间点、受影响项目列举）
  - ZK Rollup vs Optimistic Rollup 的 Stage 要求差异矩阵（聚焦 ZK 特有的可信设置、verifier 评级）
  - Walkaway Test 的通过/失败判定清单（含 Arbitrum/Base 通过、Scroll 失败的具体原因拆解）
  - ZK Verifier 可信设置评级标准说明（🟢/🟡/🔴 评级条件、Stage 1 红线）
  - Exit Window 精确计算公式与边界情况（包括 forced-tx delay、withdrawal delay 的扣减规则）
  - 对 OP Stack 基础上构建 ZK Rollup（如 Mantle 使用 OP Succinct）在 Stage 评估中的特殊考量
  - 至少 3 张 Mermaid 图（递进图、检查清单流程图、ZK vs OR 对比图）
  - Evidence: ≥5 条 L2Beat 官方一手来源（Forum、Medium、Stages 页面、Glossary、Monthly Updates）

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-18T15:30:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-18T15:30:00Z"
---

# Research Outline: L2Beat Stage 框架最新标准解析（2026 版）

## Items

### item-1: L2Beat Stages 框架的设计哲学与三阶段定位

梳理 L2Beat Stages 框架的原始设计意图（由 Luca Donno 2023 年提出，受 Vitalik "training wheels"
模型启发）、三阶段（Stage 0 Full Training Wheels → Stage 1 Limited Training Wheels →
Stage 2 No Training Wheels）的核心定位差异，以及"为什么需要 Stages"的根本逻辑——
在 trust-minimization 与运营灵活性之间提供可测度的台阶。需要明确每个 Stage 的概念边界：
Stage 0 强调 "rollup 必须可被定义为 rollup"（含 proof system 与 DA），Stage 1 引入
"用户在 operator 作恶时仍能退出"，Stage 2 进一步要求 "Security Council 仅能介入可裁决的 onchain bug"。
本 item 不展开具体清单，只奠定后续 item 的概念坐标系。

- **Priority**: high
- **Dependencies**: none

### item-2: Stage 0 要求清单（2026 版）——含 "Proof System 必须项" 更新

整理 Stage 0 在 2026.05 时点的完整要求：(a) 状态根可在 L1 上验证（含 fraud proof 或 validity
proof 系统的存在与运行）；(b) DA 满足 rollup 定义（calldata 或 blob，非 alt-DA）；
(c) 状态根 Posting 频率与可访问性；(d) operator 集合的透明度。重点解读 **2024.12 框架更新**：
L2Beat 不再容忍 "无 proof system 的 Stage 0"，过去归类为 Stage 0 的若干 optimium / alt-DA
项目（以及部分 zk-rollup 中 proof system 未实际运行的项目，如 Starknet）被重新分类。
本 item 需要：明确变更生效日期（2024-12 Bartek Kiepuszewski 的 Medium 文章）、
列举受影响的代表性项目（Starknet 暂时降为 Stage 0、未启用 proof system 的 alt-DA 被划入
"Others"）、说明 "Others" 分类的边界。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Stage 1 完整检查清单（2026 版）——逐项判定标准与边界条件

按"维度 × 要求"二维结构整理 Stage 1 的全部必要条件，并给出每一项的精确判定标准。维度包括：
(1) **Proof System**：必须存在、必须 permissionless（任何人可提交 fraud proof / validity proof），
ZK 系统的 verifier 不允许被标记为 🔴（见 item-5）。
(2) **Security Council 量化要求**：≥8 名成员、>75% 阈值、≥50% 外部成员、≥2 名外部签名达成共识、
成员身份公开、proof system effective power ≥25%（对应 75% 阈值的虚拟多签数学推导）。
(3) **Exit Window**：非 Security Council 主体发起的升级必须提供 ≥7 天退出窗口；精确公式
`Effective Exit Window = Upgrade Delay − Forced Transaction Delay − Withdrawal Delay`；
Arbitrum (11d upgrade − 1d force-tx = 10d)、ZKsync Lite (21d − 14d = 7d)、dYdX v3 (9d, with
14d forced-exit) 三类边界示例。
(4) **Operator Liveness**：proposer 集合若开放（permissionless）则假设 1-of-N (unbounded N) 至少一个
活跃；若闭合，需要其他活性保障。
(5) **Walkaway Test**（2025.12 新增）：见 item-4。
(6) **ZK Verifier Trusted Setup**（2025.11 新增）：见 item-5。
本 item 是整篇研究的核心判定矩阵，必须做到每一项都可被独立打勾/打叉。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 2025.12 新增要求 —— Security Council Walkaway Test

详细解读 Walkaway Test 的精确定义、动机、判定方法与生效路径。核心问题："Can users exit,
in the presence of malicious operators, even if the Security Council disappears?" 该 test
要求 Stage 1 rollup **不得在非紧急情况下主动使用 Security Council 来提供抗审查 / 活性 / 安全保证**。
等价于禁止 Security Council 成为 happy-path 上的必要参与者，只允许其在可裁决的 onchain bug
情境中介入。需要：(a) 列举 Pass/Fail 实例并解释根因——Arbitrum One 通过（permissionless
fraud proof + 强制交易路径完整）、Base 通过（同上）、Scroll 不通过（具体原因需基于 L2Beat
项目页交叉验证，例如 proposer 闭合或强制退出路径依赖 Council）；(b) 整理 Starknet 社区
counterproposal 的核心论点（如 ZK rollup 不应被等同于 Optimistic Rollup 处理）；
(c) 评估该 test 对受影响项目的实际降级风险（部分 chain 可能被从 Stage 1 降至 Stage 0）；
(d) 给出该 test 与原有 "Security Council ≥8 / >75%" 量化要求的关系——后者仍然必要但不再充分。

- **Priority**: high
- **Dependencies**: item-3

### item-5: 2025.11 新增要求 —— ZK Verifier 可信设置（Trusted Setup）评级

详细解读 L2Beat 2025.11 提出的 "New Stage 1 requirements for ZK setups" 与其背后的 2025.07
"ZK Catalog Trusted Setups Framework"。需要梳理：(a) 评级方法（🟢/🟡/🔴 三级，依据
trusted setup ceremony 的公开性、参与者数量、circuit-dependent 阶段是否公开 audit、是否使用
universal SRS 等）；(b) Stage 1 红线 —— Stage 1 不允许任何 ZK verifier 被评为 🔴；
(c) 实例对照（SP1 的 Plonk 使用 Aztec Ignition 公开 ceremony 评为 🟢、SP1 的 Groth16
wrapper 由 7 人内部完成评为较低等级；ZKsync Era / Scroll / Polygon zkEVM 等的 verifier
现状）；(d) 对 ZK Rollup 走 Stage 1 的实际门槛抬升——proof system 存在性已不再充分，
verifier 来源也必须可独立验证；(e) 与 item-4 的复合效应——一个 ZK rollup 必须同时通过
Walkaway Test 与 verifier trusted setup 评级才能保留 Stage 1。

- **Priority**: high
- **Dependencies**: item-3

### item-6: Stage 2 要求清单与 Stage 1 → Stage 2 的演进路径

整理 Stage 2 的完整要求（Exit Window ≥30 天、Security Council 只能介入可裁决的 onchain bug、
proof system 完全去中心化、proposer / sequencer 完全开放）以及从 Stage 1 升级到 Stage 2
所必须移除的"训练轮"。需要：(a) 引用 L2Beat 对 Stage 2 的官方定义；(b) 列举当前已达成
或接近达成 Stage 2 的项目（截至 2026.05）；(c) 解释为何本研究项目（Mantle Stage 1）暂不
聚焦 Stage 2 实现路径——但仍需理解 Stage 2 边界以避免设计 Stage 1 方案时埋下 Stage 2 阻碍。
本 item 优先级较低，目的是为 Mantle 的长期路线图保留前向兼容性参考。

- **Priority**: medium
- **Dependencies**: item-3

### item-7: ZK Rollup vs Optimistic Rollup 的 Stage 要求差异矩阵

按"通用要求 × ZK 特有 × OR 特有"三栏对照整理两类 rollup 在 Stage 0/1/2 各项要求上的异同。
通用项：Proof System 存在性、DA、Walkaway Test、Security Council 量化阈值、Exit Window 公式；
ZK 特有项：verifier trusted setup 评级、ZK circuit / prover 开源与可独立重现性、
recursion / aggregation 层的信任假设；OR 特有项：fraud proof challenge window、challenger
集合是否 permissionless、bond / bond-slashing 机制设计。该矩阵直接服务于 Mantle ——
作为 OP Stack fork、采用 OP Succinct 走 ZK 路线的混合架构（详见 item-8），其评估同时
触及两栏。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5

### item-8: OP Stack 上的 ZK Rollup（Mantle / OP Succinct 路径）的 Stage 评估特殊考量

针对"基于 OP Stack derivation 与 op-geth 执行层、但用 ZK validity proof（OP Succinct + SP1）
替代 fault proof"这一混合架构，识别 Stage 评估中的非显然问题。需要：(a) Proof System
归属——验证 ZK proof 的 verifier 合约是否被 L2Beat 视作 "rollup proof system"，以及与
OP Stack 原生 Fault Dispute Game 的归类差异；(b) verifier trusted setup 评级如何承继自
SP1 上游（Aztec Ignition + Succinct 内部 ceremony）以及在 Mantle 自有 verifier 部署时
是否需要额外披露；(c) Exit Window 与 OP Stack 升级治理（Optimism Foundation 上游升级 vs
Mantle 自有 SystemConfig 治理）的双层叠加效应；(d) Walkaway Test 在 ZK proof 永久有效、
fraud proof 链路被替换的语境下如何重新解释——关键看 challenger 路径是否仍 permissionless
（OP Succinct 的 proposer/challenger 模型）；(e) 列出对应 Mantle 现状的开放问题清单，
作为后续 deep-draft 与 upgrade-exitwindow-securitycouncil / proposer-decentralization-zk-compliance
两个下游 issue 的入口。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| requirement_summary | 该项要求的 1-3 句精确描述（避免模糊表述，每个动词必须可验证） | all |
| evaluation_criteria | 判定通过/不通过的具体技术条件（含阈值、公式、边界值） | item-2, item-3, item-4, item-5, item-6 |
| pass_fail_examples | 至少 1 个 Pass 与 1 个 Fail 的具体项目实例，含原因拆解 | item-3, item-4, item-5, item-6 |
| delta_from_prior_version | 相比 2025.10（更新前）的版本变化点，含生效日期与官方公告链接 | item-2, item-4, item-5 |
| zk_vs_optimistic_differentials | 对 ZK / OR 两类 rollup 的差异化要求（若该项存在差异） | item-3, item-5, item-7 |
| relevance_to_mantle | 该项对 Mantle（OP Stack + OP Succinct ZK proof）的直接关联与潜在 gap | item-3, item-4, item-5, item-7, item-8 |
| evidence_sources | 一手来源链接清单（Forum / Medium / Stages 页面 / Glossary 永久链接） | all |
| open_questions | 当前公开材料中未明确、需要进一步确认或观察的问题 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy | Stage 0 → Stage 1 → Stage 2 要求递进图：以三阶段为列，每列列出该阶段新增/收紧的要求（Proof System / Walkaway / Council / Exit Window / Verifier Setup），用箭头连接前后阶段并标注"升级触发条件" | mermaid | item-1, item-2, item-3, item-6 |
| diag-2 | flow | Stage 1 检查清单流程图：以决策树形式串联 Stage 1 的 6 个判定维度（Proof System → Permissionless? → ZK Verifier ≠ 🔴? → Council ≥8/>75%/外部≥50%? → Exit Window ≥7d? → Walkaway Pass?），任一 No 即降级 Stage 0 | mermaid | item-3, item-4, item-5 |
| diag-3 | comparison | ZK Rollup vs Optimistic Rollup Stage 要求差异矩阵：左列通用要求、中列 ZK 特有、右列 OR 特有；每行一个维度（Proof System、Verifier、Exit Window、Walkaway、Challenger） | mermaid | item-7 |
| diag-4 | flow | Walkaway Test 判定流程图：以"Security Council 消失"为假设输入，逐步检查 (a) 用户能否强制交易、(b) 提款是否依赖 Council 签名、(c) Proposer 集合是否开放、(d) Verifier 是否独立运行；任一依赖 Council 即 Fail | mermaid | item-4 |
| diag-5 | timeline | L2Beat 框架演进时间线（2023.06 Stages 提出 → 2023.12 Council 量化更新 → 2024.12 Proof System Mandatory → 2025.07 ZK Catalog Setups Framework → 2025.11 ZK Verifier Stage 1 红线 → 2025.12 Walkaway Test → 2026.05 当前快照），标注每个节点对 Mantle 的影响窗口 | mermaid | item-2, item-4, item-5 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | L2Beat 官方 Stages 页面与 Glossary：https://l2beat.com/stages、https://l2beat.com/glossary（必须使用永久版本/快照链接以锁定 2026.05 时点状态） | 2 |
| src-2 | governance_proposals | L2Beat Forum 一手帖子：The Stages Framework (#291)、Security Council Walkaway Test (#412)、New Stage 1 requirements for ZK setups (#409)、Trusted Setups Framework for ZK Catalog (#381) | 4 |
| src-3 | expert_commentary | L2Beat Medium 文章：Introducing Stages (Luca Donno)、Framework update: L2 projects recategorization (Bartek Kiepuszewski, 2024.12)、Stages update: Security Council requirements (Luca Donno) | 3 |
| src-4 | on_chain_data | 至少 3 个代表性 L2 的 L2Beat 项目页快照（Arbitrum One、Base、Scroll、Starknet、Polygon zkEVM 中选取），用于交叉验证 Stage 评定结果与本 outline 列出的判定条件之间的一致性 | 3 |
| src-5 | expert_commentary | 社区 counterproposal 与第三方分析（如 Starknet 团队对 Walkaway Test 的反馈、ZK/SEC Quarterly 的 formal 分析、Vitalik 关于 "Stage 1 or GTFO" 的公开表态） | 2 |
| src-6 | official_docs | L2Beat Monthly Updates（2025.12、2026.01、2026.04 三期）用于捕获 outline 未覆盖的细则变更 | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
