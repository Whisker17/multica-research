---
topic: "L2Beat Stage 框架最新标准解析（2026 版）"
project_slug: mantle-stage1-rollup
topic_slug: l2beat-stage-framework-2026
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: mantle-stage1-rollup/outlines/l2beat-stage-framework-2026.md
  draft: mantle-stage1-rollup/research-sections/l2beat-stage-framework-2026/drafts/round-{n}.md
  final: mantle-stage1-rollup/research-sections/l2beat-stage-framework-2026/final.md
  index: mantle-stage1-rollup/research-sections/_index.md

scope: |
  完整梳理 L2Beat Stages 框架在 2026 年 5 月时点的所有 Stage 0/1/2 具体要求，
  重点解析 2024.12 - 2026.04 期间的四项重大更新：
  (1) 2024.12 — Proof System 成为 Stage 0 必须项；
  (2) 2025.11 — Stage 1 对 ZK Proving System 的全面新要求（含 proof-system maturity、
      permissionless proposer/validator 验证路径、verifier trusted setup 红线）；
  (3) 2025.12 — Security Council Walkaway Test（以 proposed update 形式发布，附 rollout
      timing、grace period 与防止批量降级条款，截至 2026.05 的实际执行状态需研究确认）；
  (4) 2026.04 — Stage 1 最低 Challenge Period 从 7d 降至 5d，且 withdrawal-period 组件
      从 active 要求中移除（L2Beat Forum #425）。
  本研究必须明确区分"规范性提案文本（Forum 帖子）"与"L2Beat Stages/项目页实际执行的分类规则"，
  并为下游 Mantle 差距分析（upgrade/exit-window/security-council、proposer 去中心化、
  Stage 1 路线图）提供精确、可引用、有时间戳与执行状态标注的判定基准。

audience: |
  Mantle / OP Stack 生态研究者与协议工程师；Multica 研究 squad 内部下游 Research Agent
  （upgrade-exitwindow-securitycouncil、proposer-decentralization-zk-compliance、
  stage1-roadmap-recommendation）；关注 L2 Stage 1/2 合规进展的投研分析师与生态合作伙伴。
  阅读者熟悉 Rollup 基本概念（Optimistic vs ZK、fraud proof、validity proof、Security Council），
  但不一定追踪过 L2Beat 在 2025-2026 年间的每一次框架细则更新。

expected_output: |
  - Stage 0/1/2 完整要求对照表（2026.05 版，覆盖 Proof System / Sequencer / Proposer / Upgrade /
    Exit Window / Security Council / Data Availability / ZK Verifier 八大维度），每行注明
    "规范源（Forum/Medium）" 与 "当前 L2Beat 项目页实际执行状态"。
  - 四项重大更新的详细解读（2024.12 / 2025.11 / 2025.12 / 2026.04），每项必须标注
    `enforcement_status ∈ {proposed | adopted | enforced-on-project-pages}` 与生效日期、
    L2Beat 官方公告链接、受影响项目列表。
  - ZK Rollup vs Optimistic Rollup 的 Stage 要求差异矩阵（聚焦 ZK 特有的 proving-system
    要求、verifier 评级、recursion / aggregation 信任假设）。
  - Walkaway Test 通过/失败判定清单：每个命名实例（Arbitrum One、Base、Scroll、Starknet、
    Polygon zkEVM 等）**必须附 L2Beat Stages/项目页快照链接**，验证前一律视为假设。
  - ZK Proving System Stage 1 要求总览（三个子项：(a) verifier trusted setup 评级与红线，
    (b) proof-system maturity 的判定，(c) permissionless proposer/validator 验证路径），
    每个子项给出独立的判定标准。
  - Exit Window **双轨表述**：
    (i) 历史公式 `Effective Exit Window = Upgrade Delay − Challenge/Forced-Tx Delay − Withdrawal Delay`
        （Stage 1 ≥7d，2026.04 之前生效，仍在历史项目状态评估中使用）；
    (ii) 当前规则（2026.04 起）：Stage 1 challenge period 最低 5d，withdrawal-period 组件
         移除，新公式与旧公式的差异及对边界项目（Arbitrum / ZKsync Lite / dYdX v3）的重新评估。
  - 对 OP Stack 基础上构建 ZK Rollup（如 Mantle 使用 OP Succinct）在 Stage 评估中的特殊考量。
  - 至少 5 张 Mermaid 图（递进图、检查清单流程图、ZK vs OR 对比图、Walkaway Test 判定流程、
    Exit Window 历史 vs 当前公式对照图、时间线图）。
  - Evidence: ≥5 条 L2Beat 官方一手来源（Forum 含 #291/#381/#409/#412/#425、Medium、
    Stages 页面快照、Glossary、Monthly Updates）。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-18T15:30:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-18T15:55:00Z"
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
列举受影响的代表性项目（含 L2Beat 项目页快照交叉验证，避免引用未经核实的分类）、
说明 "Others" 分类的边界与触发条件。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Stage 1 完整检查清单（2026 版）——逐项判定标准与边界条件

按"维度 × 要求"二维结构整理 Stage 1 的全部必要条件，并给出每一项的精确判定标准。维度包括：
(1) **Proof System**：必须存在、必须 permissionless（任何人可提交 fraud proof / validity proof），
ZK rollup 的 proving system 还需满足 item-5 的全部子项。
(2) **Security Council 量化要求**：≥8 名成员、>75% 阈值、≥50% 外部成员、≥2 名外部签名达成共识、
成员身份公开、proof system effective power ≥25%（对应 75% 阈值的虚拟多签数学推导）。
(3) **Exit Window — 双轨表述**：
  (3a) **当前规则（2026.04 起，详见 item-9）**：非 Security Council 主体发起的升级必须提供
       ≥5 天 challenge period（withdrawal-period 组件已从 active 要求移除），来源 Forum #425；
  (3b) **历史公式（2026.04 之前，仍用于历史项目状态对比与边界项目重新评估）**：
       `Effective Exit Window(历史) = Upgrade Delay − Challenge/Forced-Tx Delay − Withdrawal Delay`，
       Stage 1 需 ≥7d；Arbitrum (11d upgrade − 1d force-tx = 10d)、ZKsync Lite (21d − 14d = 7d)、
       dYdX v3 (9d, with 14d forced-exit) 三类边界示例需在 item-9 中按新规则重新判定。
(4) **Operator Liveness**：proposer 集合若开放（permissionless）则假设 1-of-N (unbounded N) 至少一个
活跃；若闭合，需要其他活性保障；具体 permissionless 标准与 item-5 (c) 子项交叉。
(5) **Walkaway Test**（2025.12 提案，详见 item-4 — 注意状态判定为 proposed/adopted/enforced 之一）。
(6) **ZK Proving System Stage 1 要求**（2025.11 新增，详见 item-5 — 含三个子项）。
本 item 是整篇研究的核心判定矩阵，必须做到每一项都可被独立打勾/打叉，且每一项必须显式
标注其**规范源（Forum/Medium）**与**当前 L2Beat 项目页实际执行状态**两个独立维度。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 2025.12 提案 —— Security Council Walkaway Test（含执行状态澄清）

详细解读 Walkaway Test 的精确定义、动机、判定方法与**实际执行状态**。核心问题：
"Can users exit, in the presence of malicious operators, even if the Security Council disappears?"
该 test 要求 Stage 1 rollup **不得在非紧急情况下主动使用 Security Council 来提供抗审查 /
活性 / 安全保证**，等价于禁止 Security Council 成为 happy-path 上的必要参与者。

**关键澄清（round 2 新增）**：L2Beat Forum #412 以 **proposed update** 形式发布，包含三类
附带条件：(i) rollout timing（何时开始按新规则评估）、(ii) grace period（已有项目的过渡期）、
(iii) 避免批量降级（不应一次性把多个项目从 Stage 1 降到 Stage 0）。因此**绝不能假设该 test
已经是当前 L2Beat 项目页的硬性分类规则**。本 item 必须独立完成以下两件事：

(A) **规范性提案文本**：完整记录 Forum #412 的条款、定义、判定路径与原作者意图，作为研究的
    "应然 (should be)" 基线。
(B) **实际执行状态核验**：在 2026.05 时点抓取 L2Beat Stages 页面与代表项目页（Arbitrum One、
    Base、Scroll、Starknet、Polygon zkEVM）快照，**逐项核对该项目当前 Stage 评定是否实际
    依据 Walkaway Test 标准**。`enforcement_status` 字段必须填写为以下三者之一：
    - `proposed`：仅作为 Forum 提案，项目页评定未引用此标准；
    - `adopted`：L2Beat 官方公告（Medium / Monthly Update）确认采纳但未应用于项目页；
    - `enforced-on-project-pages`：至少一个项目页评定结果可追溯到此标准（如分类调整说明）。

此外需：(a) 列举 proposed Pass/Fail 实例（Arbitrum One、Base "应当"通过；Scroll、Starknet 等
"可能"失败），并明确标注"当前 L2Beat 项目页实际分类"vs"按提案应得分类"的差异；
(b) 整理 Starknet 社区 counterproposal 的核心论点（如 ZK rollup 不应被等同于 Optimistic Rollup 处理）；
(c) 评估该 test 一旦正式 enforced 后对受影响项目的实际降级风险；
(d) 给出该 test 与原有 "Security Council ≥8 / >75%" 量化要求的关系——后者仍然必要但不再充分。

- **Priority**: high
- **Dependencies**: item-3

### item-5: 2025.11 新增要求 —— ZK Proving System Stage 1 全面要求

详细解读 L2Beat 2025.11 通过 Forum #409 "New Stage 1 requirements for ZK setups" 提出的
**整套 ZK proving system 要求**，以及其依托的 2025.07 "ZK Catalog Trusted Setups Framework"
(#381)。本 item 的范围是**ZK proving system 整体**，trusted setup 仅是其中一个子项。

**三个独立子项**：

(5a) **Verifier Trusted Setup 评级与红线**：
  - 评级方法（🟢/🟡/🔴 三级，依据 trusted setup ceremony 的公开性、参与者数量、
    circuit-dependent 阶段是否公开 audit、是否使用 universal SRS 等）；
  - Stage 1 红线 —— Stage 1 不允许任何 ZK verifier 被评为 🔴；
  - 实例对照（SP1 的 Plonk 使用 Aztec Ignition 公开 ceremony 评为 🟢、SP1 的 Groth16
    wrapper 由 7 人内部完成评级较低；ZKsync Era / Scroll / Polygon zkEVM 等的 verifier 现状）。

(5b) **Proof System Maturity 的判定**：
  - proof system 必须**实际在生产中运行**（与 item-2 "Proof System Mandatory" 衔接但更严格）；
  - 必须可被独立重现（circuit / prover 开源、可由第三方在公开输入上得到一致 proof）；
  - 排除 "proof system 部署但未启用"或"仅在 testnet 运行"的过渡状态；
  - 需要给出"启用 (active)"vs"未启用 (inactive)"的具体判定信号（如最近一次 onchain proof
    提交时间戳、verifier 合约状态、是否有 proposer 强制依赖此 proof）。

(5c) **Permissionless Proposer / Validator 验证路径**：
  - 任何人可独立运行 prover/proposer 节点，并将合法 proof 提交到 L1 verifier；
  - 不应存在白名单或 multisig-gated 的 prover 集合；
  - 与 item-3 "Operator Liveness" 项的"permissionless"要求统一定义，但本子项更聚焦
    "提交侧"而非"liveness"，二者共同构成 ZK rollup Stage 1 的去中心化基线。

需补充：(d) 三个子项的复合判定——任一子项不通过即降级 Stage 0；(e) 与 item-4 Walkaway Test
的复合效应——一个 ZK rollup 必须同时满足三个子项与 Walkaway Test 才能保留 Stage 1（前提是
后者实际执行状态为 `enforced-on-project-pages`）。

- **Priority**: high
- **Dependencies**: item-3

### item-6: Stage 2 要求清单与 Stage 1 → Stage 2 的演进路径

整理 Stage 2 的完整要求（Exit Window ≥30 天、Security Council 只能介入可裁决的 onchain bug、
proof system 完全去中心化、proposer / sequencer 完全开放）以及从 Stage 1 升级到 Stage 2
所必须移除的"训练轮"。需要：(a) 引用 L2Beat 对 Stage 2 的官方定义；(b) 列举当前已达成
或接近达成 Stage 2 的项目（截至 2026.05，所有命名实例必须附项目页快照）；(c) 解释为何
本研究项目（Mantle Stage 1）暂不聚焦 Stage 2 实现路径——但仍需理解 Stage 2 边界以避免设计
Stage 1 方案时埋下 Stage 2 阻碍；(d) 注意 2026.04 Stage 1 Challenge Period 调整（item-9）
是否在 Forum / Medium 中触发了 Stage 2 ≥30d 要求的对应讨论，若有则记录，若无则明确声明
未发现联动证据。

- **Priority**: medium
- **Dependencies**: item-3, item-9

### item-7: ZK Rollup vs Optimistic Rollup 的 Stage 要求差异矩阵

按"通用要求 × ZK 特有 × OR 特有"三栏对照整理两类 rollup 在 Stage 0/1/2 各项要求上的异同。
通用项：Proof System 存在性、DA、Walkaway Test（注意标注其执行状态）、Security Council
量化阈值、Exit Window（注意 2026.04 后双轨规则）；ZK 特有项：proving system 三子项
（verifier trusted setup 评级、proof-system maturity、permissionless 验证路径，详见 item-5）、
recursion / aggregation 层的信任假设；OR 特有项：fraud proof challenge window（2026.04
后最低 5d）、challenger 集合是否 permissionless、bond / bond-slashing 机制设计。
该矩阵直接服务于 Mantle ——作为 OP Stack fork、采用 OP Succinct 走 ZK 路线的混合架构
（详见 item-8），其评估同时触及两栏。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-9

### item-8: OP Stack 上的 ZK Rollup（Mantle / OP Succinct 路径）的 Stage 评估特殊考量

针对"基于 OP Stack derivation 与 op-geth 执行层、但用 ZK validity proof（OP Succinct + SP1）
替代 fault proof"这一混合架构，识别 Stage 评估中的非显然问题。需要：(a) Proof System
归属——验证 ZK proof 的 verifier 合约是否被 L2Beat 视作 "rollup proof system"，以及与
OP Stack 原生 Fault Dispute Game 的归类差异，并代入 item-5 的三子项判定；
(b) verifier trusted setup 评级如何承继自 SP1 上游（Aztec Ignition + Succinct 内部 ceremony）
以及在 Mantle 自有 verifier 部署时是否需要额外披露；
(c) Exit Window 与 OP Stack 升级治理（Optimism Foundation 上游升级 vs Mantle 自有
SystemConfig 治理）的双层叠加效应——需同时按 2026.04 之前的历史公式与之后的 ≥5d 新规
进行双轨评估；
(d) Walkaway Test 在 ZK proof 永久有效、fraud proof 链路被替换的语境下如何重新解释——
关键看 challenger / proposer 路径是否仍 permissionless（OP Succinct 的 proposer/challenger
模型），且需注意 Walkaway Test 的实际执行状态（item-4）决定本子项的强制性；
(e) 列出对应 Mantle 现状的开放问题清单，作为后续 deep-draft 与
upgrade-exitwindow-securitycouncil / proposer-decentralization-zk-compliance 两个下游
issue 的入口。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-7, item-9

### item-9: 2026.04 Stage 1 Challenge-Period / Exit-Window 规则更新

详细解读 2026 年 4 月生效的 Stage 1 challenge period 规则变更（L2Beat Forum #425）：
**Stage 1 最低 challenge period 从 7 天降至 5 天，并将 withdrawal-period 组件从 active
要求中移除**。本 item 是 round 2 新增项，承接 item-3 (3a)/(3b) 双轨表述的细节展开，
是下游 Mantle 升级/退出窗口差距分析的关键判定锚点。

必须覆盖：

(a) **规则变更的精确文本**：从 Forum #425 提取原始条款与定义，明确"5 天"指代的是
    challenge period（即 fraud proof / validity proof 提交窗口）而非用户提款延迟。

(b) **历史公式 vs 当前规则对照**：
  - 历史公式（2026.04 之前）：
    `Effective Exit Window = Upgrade Delay − Challenge/Forced-Tx Delay − Withdrawal Delay`，
    Stage 1 需 ≥7d；
  - 当前规则（2026.04 起）：challenge period 最低 5d 直接作为 Stage 1 评定阈值，
    withdrawal-period 不再扣减；
  - 整理 L2Beat 官方对该变更的理由说明（如 withdrawal-period 与 active security 关联不强、
    7d 阈值过严导致项目难以达成 Stage 1 等）。

(c) **边界项目的重新评估**：
  - Arbitrum (11d upgrade − 1d force-tx)、ZKsync Lite (21d − 14d)、dYdX v3 (9d challenge,
    14d forced-exit) 等之前在 7d 阈值附近的项目，按新规则的判定结果是否改变；
  - 任何因新规则**新增通过 Stage 1** 的项目（需附项目页快照确认）；
  - 任何因新规则**当前 Stage 评定调整** 的项目（需附 L2Beat 公告链接）。

(d) **执行状态（enforcement_status）**：截至 2026.05 是否已在 L2Beat 项目页与 Stages 页面
    实际应用此 5d 规则；若仅在公告中，需标注 `adopted` 而非 `enforced-on-project-pages`。

(e) **对 Stage 2 的潜在影响**（与 item-6 联动）：若 Stage 1 阈值下调，是否在 Forum / Medium
    中触发了 Stage 2 ≥30d 要求的对应讨论；若无联动证据则明确声明。

(f) **对 Mantle 的直接关联**：Mantle 当前合约升级延迟、强制交易路径与 withdrawal 配置在
    新旧两套规则下的判定结果（详细分析交由下游 upgrade-exitwindow-securitycouncil issue，
    本 item 仅给出判定接口与所需输入）。

- **Priority**: high
- **Dependencies**: item-3

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| requirement_summary | 该项要求的 1-3 句精确描述（避免模糊表述，每个动词必须可验证） | all |
| evaluation_criteria | 判定通过/不通过的具体技术条件（含阈值、公式、边界值） | item-2, item-3, item-4, item-5, item-6, item-9 |
| pass_fail_examples | 至少 1 个 Pass 与 1 个 Fail 的具体项目实例，含原因拆解；每个命名实例必须附 L2Beat 项目页快照链接（验证前一律视为假设） | item-3, item-4, item-5, item-6, item-9 |
| delta_from_prior_version | 相比 2025.10（或对应基线版本）的版本变化点，含生效日期与官方公告链接 | item-2, item-4, item-5, item-9 |
| enforcement_status | 该要求/变更截至 2026.05 的实际执行状态，三选一：`proposed`（仅 Forum 提案，项目页未引用）/ `adopted`（官方公告确认但未应用于项目页）/ `enforced-on-project-pages`（至少一个项目页评定结果可追溯到此标准） | item-4, item-5, item-9 |
| zk_vs_optimistic_differentials | 对 ZK / OR 两类 rollup 的差异化要求（若该项存在差异） | item-3, item-5, item-7, item-9 |
| relevance_to_mantle | 该项对 Mantle（OP Stack + OP Succinct ZK proof）的直接关联与潜在 gap | item-3, item-4, item-5, item-7, item-8, item-9 |
| evidence_sources | 一手来源链接清单（Forum / Medium / Stages 页面 / Glossary 永久链接），优先永久版本/快照链接 | all |
| open_questions | 当前公开材料中未明确、需要进一步确认或观察的问题 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy | Stage 0 → Stage 1 → Stage 2 要求递进图：以三阶段为列，每列列出该阶段新增/收紧的要求（Proof System / Walkaway / Council / Exit Window / Proving System Trusted Setup），用箭头连接前后阶段并标注"升级触发条件" | mermaid | item-1, item-2, item-3, item-6 |
| diag-2 | flow | Stage 1 检查清单流程图（2026.05 当前规则）：以决策树形式串联 Stage 1 的 6 个判定维度（Proof System → Permissionless? → ZK Proving System 三子项全通过? → Council ≥8/>75%/外部≥50%? → **Challenge Period ≥5d (Forum #425, 2026.04)** ? → Walkaway Test 实际执行状态 ∈ {adopted, enforced} 且 Pass? ），任一 No 即降级 Stage 0。需在节点旁注明"规范源"与"当前是否 enforced"两条独立信息 | mermaid | item-3, item-4, item-5, item-9 |
| diag-3 | comparison | ZK Rollup vs Optimistic Rollup Stage 要求差异矩阵：左列通用要求、中列 ZK 特有、右列 OR 特有；每行一个维度（Proof System、Proving System 三子项、Exit Window 双轨、Walkaway 执行状态、Challenger） | mermaid | item-7 |
| diag-4 | flow | Walkaway Test 判定流程图：以"Security Council 消失"为假设输入，逐步检查 (a) 用户能否强制交易、(b) 提款是否依赖 Council 签名、(c) Proposer 集合是否开放、(d) Verifier 是否独立运行；任一依赖 Council 即 Fail。注：该图描述的是**提案文本的判定逻辑**，实际是否影响项目分类取决于 item-4 的执行状态 | mermaid | item-4 |
| diag-5 | timeline | L2Beat 框架演进时间线（2023.06 Stages 提出 → 2023.12 Council 量化更新 → 2024.12 Proof System Mandatory → 2025.07 ZK Catalog Setups Framework (#381) → 2025.11 ZK Proving System Stage 1 全面要求 (#409) → 2025.12 Walkaway Test 提案 (#412) → **2026.04 Stage 1 Challenge Period 7d→5d (#425)** → 2026.05 当前快照），每个节点标注 enforcement_status 与对 Mantle 的影响窗口 | mermaid | item-2, item-4, item-5, item-9 |
| diag-6 | comparison | Exit Window 历史公式 vs 当前规则对照图：左列 2026.04 之前历史公式 `Upgrade Delay − Challenge/Forced-Tx Delay − Withdrawal Delay ≥7d`，右列 2026.04 起当前规则 `Challenge Period ≥5d`（withdrawal-period 已移除）；中部列出 Arbitrum / ZKsync Lite / dYdX v3 三个边界项目在新旧两套规则下的判定结果差异 | mermaid | item-3, item-9 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | L2Beat 官方 Stages 页面与 Glossary：https://l2beat.com/stages、https://l2beat.com/glossary（必须使用永久版本/快照链接以锁定 2026.05 时点状态） | 2 |
| src-2 | governance_proposals | L2Beat Forum 一手帖子（必须覆盖以下 5 条）：The Stages Framework (#291)、Trusted Setups Framework for ZK Catalog (#381)、New Stage 1 requirements for ZK setups (#409)、Security Council Walkaway Test (#412)、**Stage 1 Challenge Period 7d→5d (#425, 2026.04)** | 5 |
| src-3 | expert_commentary | L2Beat Medium 文章：Introducing Stages (Luca Donno)、Framework update: L2 projects recategorization (Bartek Kiepuszewski, 2024.12)、Stages update: Security Council requirements (Luca Donno)、以及 2026.04 challenge-period 调整对应的公告（若存在） | 3 |
| src-4 | on_chain_data | **每个在大纲中被命名为 pass/fail 示例的项目**（包括但不限于 Arbitrum One、Base、Scroll、Starknet、Polygon zkEVM、ZKsync Lite、dYdX v3）都必须附其 L2Beat 项目页 2026.05 快照链接；未附快照的实例在 draft 中只能作为"假设"出现，不能作为事实陈述。该 src 计数为命名实例总数，下限 5 | 5 |
| src-5 | expert_commentary | 社区 counterproposal 与第三方分析（如 Starknet 团队对 Walkaway Test 的反馈、ZK/SEC Quarterly 的 formal 分析、Vitalik 关于 "Stage 1 or GTFO" 的公开表态） | 2 |
| src-6 | official_docs | L2Beat Monthly Updates（覆盖 2025.11、2025.12、2026.01、2026.04、2026.05 五期，用于捕获 outline 未覆盖的细则变更与四项更新的 enforcement 进展） | 3 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | add_item | item-9 | 新增 2026.04 Stage 1 Challenge-Period / Exit-Window 规则更新专项 item，覆盖 Forum #425 公布的 7d→5d 变更与 withdrawal-period 组件移除，作为 Exit Window 双轨表述（历史 vs 当前）的展开锚点 | Adversarial finding #1 (Major) |
| 2 | modify_item | item-3 | Exit Window 子项重构为双轨表述 (3a) 当前 ≥5d 规则 / (3b) 历史 ≥7d 公式；新增"规范源 vs 当前 L2Beat 项目页执行状态"两个独立维度的强制要求；指向 item-9 与 item-5 的依赖路径 | Adversarial finding #1 + #2 (Major) |
| 2 | modify_item | item-4 | 明确区分"规范性提案文本 (Forum #412)"与"L2Beat 项目页实际执行的分类规则"，要求显式核验 enforcement_status；新增对 rollout timing / grace period / 防批量降级条款的覆盖；pass/fail 实例需附项目页快照 | Adversarial finding #2 (Major) |
| 2 | modify_item | item-5 | 重命名/扩展为 "ZK Proving System Stage 1 全面要求"，拆分为三个独立子项（5a verifier trusted setup 评级 / 5b proof-system maturity / 5c permissionless 验证路径），trusted setup 仅作为子项之一；与 item-3 的 Operator Liveness 项交叉对齐 | Adversarial finding #3 (Major) |
| 2 | modify_item | item-6 | 新增对 2026.04 Stage 1 调整是否触发 Stage 2 ≥30d 联动讨论的核查要求；增加 dependency on item-9 | Adversarial finding #1 (Major) — 一致性传播 |
| 2 | modify_item | item-7 | 通用项注明 Walkaway 执行状态与 Exit Window 双轨；ZK 特有项指向 item-5 三子项；OR 特有项 fraud-proof challenge window 更新为 2026.04 后最低 5d；增加 dependency on item-9 | Adversarial finding #1 + #2 + #3 (Major) — 矩阵同步 |
| 2 | modify_item | item-8 | OP Stack + OP Succinct 评估接入 item-5 三子项判定；Exit Window 子项采用 2026.04 之前/之后双轨评估；Walkaway 子项依赖 item-4 执行状态；增加 dependency on item-9 | Adversarial finding #1 + #2 + #3 (Major) — Mantle 路径同步 |
| 2 | add_field | enforcement_status | 强制 item-4 / item-5 / item-9 在 deep-draft 中显式标注变更的当前执行状态（proposed / adopted / enforced-on-project-pages），避免将提案文本当作硬性规则 | Adversarial finding #2 (Major) |
| 2 | modify_field | pass_fail_examples | 每个命名实例必须附 L2Beat 项目页快照链接，验证前一律视为假设；applies_to 扩展至 item-9 | Adversarial finding #4 (Minor) |
| 2 | modify_field | evaluation_criteria | applies_to 扩展至 item-9 | Adversarial finding #1 (Major) — 一致性传播 |
| 2 | modify_field | delta_from_prior_version | applies_to 扩展至 item-9 | Adversarial finding #1 (Major) — 一致性传播 |
| 2 | modify_field | zk_vs_optimistic_differentials | applies_to 扩展至 item-9（Challenge Period 调整在 ZK vs OR 间的差异） | Adversarial finding #1 (Major) — 一致性传播 |
| 2 | modify_field | relevance_to_mantle | applies_to 扩展至 item-9 | Adversarial finding #1 (Major) — Mantle 路径一致性 |
| 2 | modify_diagram | diag-2 | Stage 1 检查清单流程图：Exit Window 节点更新为"Challenge Period ≥5d (Forum #425, 2026.04)"；每个节点旁注明"规范源"与"当前是否 enforced"两条独立信息；新增 dependency on item-9 | Adversarial finding #1 + #2 (Major) |
| 2 | modify_diagram | diag-3 | ZK vs OR 矩阵：Exit Window 行更新为双轨、Walkaway 行标注执行状态、ZK 特有列指向 item-5 三子项 | Adversarial finding #1 + #2 + #3 (Major) |
| 2 | modify_diagram | diag-5 | 时间线新增 2026.04 节点（Stage 1 Challenge Period 7d→5d, Forum #425），每个节点标注 enforcement_status | Adversarial finding #1 + #2 (Major) |
| 2 | add_diagram | diag-6 | 新增 Exit Window 历史公式 vs 当前规则对照图（comparison），可视化 Arbitrum / ZKsync Lite / dYdX v3 在新旧两套规则下的判定差异 | Adversarial finding #1 (Major) |
| 2 | modify_source_req | src-2 | Forum 一手帖子最小覆盖数从 4 提升到 5，新增 #425 (2026.04 Stage 1 Challenge Period 调整) 作为强制来源 | Adversarial finding #4 (Minor) |
| 2 | modify_source_req | src-3 | Medium 文章列表新增 2026.04 challenge-period 调整对应公告（若存在） | Adversarial finding #1 + #4 (Major + Minor) |
| 2 | modify_source_req | src-4 | 由 "至少 3 个代表性 L2 项目页快照" 提升为 "每个在大纲中被命名为 pass/fail 示例的项目都必须附其 L2Beat 项目页 2026.05 快照链接"，未附快照的实例只能作为"假设"出现；最小数从 3 提升到 5 | Adversarial finding #4 (Minor) |
| 2 | modify_source_req | src-6 | Monthly Updates 覆盖范围扩展到 2025.11、2025.12、2026.01、2026.04、2026.05 五期，用于捕获四项更新的 enforcement 进展 | Adversarial finding #1 + #2 (Major) |
