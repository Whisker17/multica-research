---
topic: "L2Beat Stage 框架最新标准解析（2026 版）"
project_slug: mantle-stage1-rollup
topic_slug: l2beat-stage-framework-2026
github_repo: Whisker17/multica-research
round: 3
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
  (2) 2025.11 → 2026.02 — Stage 1 Proving System 要求的两次迭代：
      Forum #409 提出初始 ZK setups 要求（含 trusted-setup 红线），
      Forum #413 + 2026.02 Medium 将要求收敛为四项可验证条件：
      (i) no 🔴 trusted setups, (ii) prover source code published,
      (iii) verifiers reproducible（vkey/circuit binding 可被独立重建），
      (iv) ZK programs or fault-proof prestates reproducible；
  (3) 2025.12 — Security Council Walkaway Test（以 proposed update 形式发布，附 rollout
      timing、grace period 与防止批量降级条款，截至 2026.05 的实际执行状态需研究确认）；
  (4) 2026.04 — L2Beat Forum #425 调整 Optimistic Rollup 的最低 Challenge Period
      从 7d 降至 5d，且 withdrawal-period 组件从 active 要求中移除。
  本研究必须明确区分：
    - 规范性提案文本（Forum 帖子）vs L2Beat Stages/项目页实际执行的分类规则；
    - "outside-SC upgrade exit window ≥5d"（适用于所有非 Security Council 发起的升级，
      包含 OR 与 ZK 路径）vs "Optimistic Rollup challenge period ≥5d"（Forum #425 专门
      针对 Optimistic Rollup 的 fraud-proof challenge window）vs "validity/ZK 路径下不存在
      通用 validity-proof challenge period"（不可类比套用）；
    - Stage 0 / Stage 1 / Stage 2 在 proof-system 维度的边界：state-reconstruction software
      与至少 5 个外部参与者可提交 fraud proof 属于 **Stage 0**；Security Council compromise
      condition + proposer-set liveness assumption 属于 **Stage 1**；完全 permissionless
      fraud proof submission 属于 **Stage 2**（除非有 Walkaway 式收紧提案明确改变此边界）。
  为下游 Mantle 差距分析（upgrade/exit-window/security-council、proposer 去中心化、
  Stage 1 路线图）提供精确、可引用、有时间戳与执行状态标注的判定基准。

audience: |
  Mantle / OP Stack 生态研究者与协议工程师；Multica 研究 squad 内部下游 Research Agent
  （upgrade-exitwindow-securitycouncil、proposer-decentralization-zk-compliance、
  stage1-roadmap-recommendation）；关注 L2 Stage 1/2 合规进展的投研分析师与生态合作伙伴。
  阅读者熟悉 Rollup 基本概念（Optimistic vs ZK、fraud proof、validity proof、Security Council），
  但不一定追踪过 L2Beat 在 2025-2026 年间的每一次框架细则更新。

expected_output: |
  - Stage 0/1/2 完整要求对照表（2026.05 版，覆盖 Proof System / Sequencer / Proposer /
    Upgrade / Exit Window / Security Council / Data Availability / ZK Proving System
    八大维度），每行注明：(i) 规范源（Forum/Medium），(ii) 当前 L2Beat 项目页实际执行状态，
    (iii) 适用 rollup 类型（all / OR-only / ZK-only）。
  - 四项重大更新的详细解读（2024.12 / 2025.11→2026.02 / 2025.12 / 2026.04），每项必须标注
    `enforcement_status ∈ {proposed | adopted | enforced-on-project-pages | grace-period-active}`、
    `effective_date`、`grace_period_end`（若适用）、L2Beat 官方公告链接、受影响项目列表。
  - ZK Rollup vs Optimistic Rollup 的 Stage 要求差异矩阵（聚焦 ZK 特有的 proving-system
    四项要求、verifier 评级、recursion / aggregation 信任假设；以及 OR 特有的 fraud-proof
    challenge period 5d 规则、challenger 集合 permissionless 度、bond 机制）。
  - Walkaway Test 通过/失败判定清单：每个命名实例（Arbitrum One、Base、Scroll、Starknet、
    Polygon zkEVM 等）**必须附 L2Beat Stages/项目页快照链接**，验证前一律视为假设。
  - ZK Proving System Stage 1 要求总览（四个子项，锚定 Forum #413 + #409 + 2026.02 Medium）：
    (a) no 🔴 trusted setups,
    (b) prover source code published,
    (c) verifiers reproducible（含 vkey 与 circuit binding 的独立重建路径）,
    (d) ZK programs or fault-proof prestates reproducible（含 program hash / prestate hash
    与源代码/ELF artifact 的对应关系）。
    每个子项给出独立判定标准 + Mantle/OP Succinct 直接关联。
  - Exit Window **三轨表述**（替代原 round-2 的双轨表述）：
    (i) **outside-SC upgrade exit window ≥5d**：所有非 Security Council 主体发起的升级
        必须提供 ≥5d 退出窗口，适用 OR 与 ZK 路径（基于 Stages Framework 通用规则）；
    (ii) **Optimistic Rollup challenge period ≥5d**：Forum #425（2026.04）专门针对
         Optimistic Rollup 的 fraud-proof challenge window 调整（7d → 5d）；
    (iii) **Validity/ZK 适用性说明**：ZK rollup 不存在等价于 OR challenge period 的
          "validity-proof challenge period" 概念；ZK 路径的 finality 由 verifier 接受
          validity proof 后即刻达成，本研究**不得**将 5d 规则套用于 validity proof 流程；
          ZK rollup 仍受 (i) outside-SC upgrade ≥5d 约束。
    历史公式（2026.04 之前 OR challenge ≥7d 与 withdrawal-period 组件）保留作为版本对比。
  - Stage 0 / Stage 1 / Stage 2 Proof System 边界对照表：
    - **Stage 0**: proof system 存在并运行 + state-reconstruction software 可用 + 至少
      5 个外部参与者可提交 fraud proof（对 OR 而言）；
    - **Stage 1**: Security Council compromise condition（>75% 阈值、外部 ≥50%、proof
      system effective power ≥25%）+ proposer-set liveness assumption（permissionless
      proposer 集合的 1-of-N 活性假设，或对 closed proposer 集合的等价活性保障）；
    - **Stage 2**: 完全 permissionless fraud proof submission + Security Council 仅能
      介入可裁决 onchain bug + proposer/sequencer 完全开放。
  - 对 OP Stack 基础上构建 ZK Rollup（如 Mantle 使用 OP Succinct）在 Stage 评估中的特殊考量。
  - 至少 6 张 Mermaid 图（递进图、Stage 1 检查清单流程图、ZK vs OR 对比图、Walkaway Test
    判定流程、Exit Window 三轨规则对照图、L2Beat 框架演进时间线）。
  - Evidence: ≥6 条 L2Beat 官方一手来源（Forum 含 #291/#381/#409/#412/#413/#425、
    2026.02 Medium、Stages 页面快照、Glossary、Monthly Updates）。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-18T15:30:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-18T16:25:00Z"
---

# Research Outline: L2Beat Stage 框架最新标准解析（2026 版）

## Items

### item-1: L2Beat Stages 框架的设计哲学与三阶段定位

梳理 L2Beat Stages 框架的原始设计意图（由 Luca Donno 2023 年提出，受 Vitalik "training wheels"
模型启发）、三阶段（Stage 0 Full Training Wheels → Stage 1 Limited Training Wheels →
Stage 2 No Training Wheels）的核心定位差异，以及"为什么需要 Stages"的根本逻辑——
在 trust-minimization 与运营灵活性之间提供可测度的台阶。需要明确每个 Stage 的概念边界：
Stage 0 强调 "rollup 必须可被定义为 rollup"（含 proof system 与 DA、state-reconstruction
software、至少 5 个外部参与者的 fraud-proof 提交能力），Stage 1 引入 "用户在 operator
作恶时仍能退出"（核心机制是 Security Council compromise condition + proposer-set liveness
assumption），Stage 2 进一步要求 "完全 permissionless fraud proof submission + Security
Council 仅能介入可裁决 onchain bug"。本 item 不展开具体清单，只奠定后续 item 的概念坐标系，
并显式提示后续 item-2 / item-3 / item-6 在 proof-system 维度的边界划分。

- **Priority**: high
- **Dependencies**: none

### item-2: Stage 0 要求清单（2026 版）——含 "Proof System 必须项" 更新 + Stage 0 fraud-proof 提交边界

整理 Stage 0 在 2026.05 时点的完整要求：

(a) **状态根可在 L1 上验证**（含 fraud proof 或 validity proof 系统的存在与运行）；
(b) **DA 满足 rollup 定义**（calldata 或 blob，非 alt-DA）；
(c) **状态根 Posting 频率与可访问性**；
(d) **operator 集合的透明度**；
(e) **State-reconstruction software**：必须存在公开可用的工具，使任何人能从 L1 上的
    DA 数据重建 L2 state（这是 Stage 0 的基本可观测性要求，不依赖于 operator 的合作）；
(f) **至少 5 个外部参与者可提交 fraud proof**（对 Optimistic Rollup 而言）：
    L2Beat 当前 Stages Framework 将"≥5 个外部 actor 可提交 fraud proof"放在 **Stage 0**
    的硬性要求中，**而不是 Stage 1**。完全 permissionless fraud-proof submission 是
    **Stage 2** 的要求。本 item 必须明确这一边界，避免与 item-3 (Stage 1) 混淆。

重点解读 **2024.12 框架更新**：L2Beat 不再容忍 "无 proof system 的 Stage 0"，过去归类为
Stage 0 的若干 optimium / alt-DA 项目（以及部分 zk-rollup 中 proof system 未实际运行的项目，
如 Starknet）被重新分类。本 item 需要：明确变更生效日期（2024-12 Bartek Kiepuszewski 的
Medium 文章）、列举受影响的代表性项目（含 L2Beat 项目页快照交叉验证，避免引用未经核实的
分类）、说明 "Others" 分类的边界与触发条件、并对 (e)(f) 两项给出 L2Beat 官方文本来源
（Stages Framework 主帖 #291 与 Stages 页面定义）。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Stage 1 完整检查清单（2026 版）——逐项判定标准与边界条件

按"维度 × 要求"二维结构整理 Stage 1 的全部必要条件，并给出每一项的精确判定标准。

**Stage 1 与 Stage 0 / Stage 2 在 proof-system 维度的边界（round 3 重写）**：
Stage 1 的 proof-system 要求**不是** "anyone can submit fraud proof"——后者是 Stage 2 的
完全 permissionlessness 要求。Stage 1 当前 Stages Framework 措辞聚焦于两个核心：

- **Security Council compromise condition**：Council 量化阈值（≥8 名成员、>75% 阈值、
  ≥50% 外部成员、≥2 名外部签名达成共识、成员身份公开、proof system effective power ≥25%）
  确保 Council 不能单方面颠覆 proof 系统结论；
- **Proposer-set liveness assumption**：proposer 集合若开放（permissionless）则假设
  1-of-N (unbounded N) 至少一个活跃；若闭合，需要其他活性保障（具体 permissionless 标准
  与 item-5 子项交叉，但**不要求**任意外部 actor 都能提交 fraud proof——后者属于 Stage 0
  的 "≥5 external actors" 与 Stage 2 的 "fully permissionless"）。

完整维度清单：

(1) **Proof System 存在性与运行**：必须存在并实际在生产中运行（继承 Stage 0 要求，详见 item-2）；
    ZK rollup 的 proving system 还需满足 item-5 的四项子项。
(2) **Security Council 量化要求**：≥8 名成员、>75% 阈值、≥50% 外部成员、≥2 名外部签名
    达成共识、成员身份公开、proof system effective power ≥25%（对应 75% 阈值的虚拟多签
    数学推导）。
(3) **Exit Window — 三轨规则（round 3 重写，替代原 round-2 双轨表述）**：

    (3a) **outside-SC upgrade exit window ≥5d（适用于所有 rollup）**：
         任何**非 Security Council 主体**发起的升级（包括项目方 multisig、治理 DAO 等）
         必须为用户提供 ≥5 天的退出窗口。来源：L2Beat Stages Framework 通用规则
         （Forum #291 + 后续更新），适用于 OR 与 ZK 两类路径。这是 Mantle 等 ZK rollup
         在 Exit Window 维度上**实际承担**的硬性要求。

    (3b) **Optimistic Rollup challenge period ≥5d（仅适用于 OR）**：
         L2Beat Forum #425（2026.04）专门针对 Optimistic Rollup 调整：fraud-proof
         challenge window 最低从 7d 降至 5d；withdrawal-period 组件从 active 要求中移除。
         此规则**不直接套用于 ZK rollup**（详见 (3c)）。

    (3c) **Validity/ZK 适用性说明**：
         ZK rollup 不存在与 OR challenge period 等价的 "validity-proof challenge period"
         概念。validity proof 一经 verifier 合约接受即达成 finality，无需挑战窗口。
         因此对于 Mantle (OP Succinct, validity-proof 路径) 的 Stage 1 评估：
         - 适用 (3a) outside-SC upgrade exit window ≥5d；
         - **不适用** (3b) OR challenge period 5d——任何将 5d 作为 validity-proof
           challenge window 进行检验的做法都构成 false-positive 误判；
         - ZK rollup 仍可在合约层面引入自定义的 finalization delay（如 OP Succinct
           的 finalizationPeriodSeconds），但该 delay 不构成 L2Beat 框架定义的
           "challenge period"，应在下游 issue 单独评估。

    (3d) **历史公式（2026.04 之前，仅用于历史项目状态对比）**：
         `Effective Exit Window(历史) = Upgrade Delay − Challenge/Forced-Tx Delay − Withdrawal Delay`，
         Stage 1 需 ≥7d；Arbitrum (11d upgrade − 1d force-tx = 10d)、ZKsync Lite
         (21d − 14d = 7d)、dYdX v3 (9d, with 14d forced-exit) 三类边界示例在 item-9
         中按新规则重新判定。

(4) **Operator Liveness**：proposer 集合若开放（permissionless）则假设 1-of-N (unbounded N)
    至少一个活跃；若闭合，需要其他活性保障；具体 permissionless 标准与 item-5 (5b)(5c)
    子项交叉。
(5) **Walkaway Test**（2025.12 提案，详见 item-4 — 注意状态判定为 proposed/adopted/
    enforced/grace-period-active 之一）。
(6) **ZK Proving System Stage 1 要求**（2025.11→2026.02 迭代，详见 item-5 — 含四个子项）。

本 item 是整篇研究的核心判定矩阵，必须做到每一项都可被独立打勾/打叉，且每一项必须显式
标注其**规范源（Forum/Medium）**与**当前 L2Beat 项目页实际执行状态**两个独立维度。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 2025.12 提案 —— Security Council Walkaway Test（含执行状态澄清）

详细解读 Walkaway Test 的精确定义、动机、判定方法与**实际执行状态**。核心问题：
"Can users exit, in the presence of malicious operators, even if the Security Council disappears?"
该 test 要求 Stage 1 rollup **不得在非紧急情况下主动使用 Security Council 来提供抗审查 /
活性 / 安全保证**，等价于禁止 Security Council 成为 happy-path 上的必要参与者。

**关键澄清（round 2 → round 3 强化）**：L2Beat Forum #412 以 **proposed update** 形式发布，
包含三类附带条件：(i) rollout timing（何时开始按新规则评估）、(ii) grace period（已有
项目的过渡期）、(iii) 避免批量降级（不应一次性把多个项目从 Stage 1 降到 Stage 0）。
因此**绝不能假设该 test 已经是当前 L2Beat 项目页的硬性分类规则**。本 item 必须独立完成
以下两件事：

(A) **规范性提案文本**：完整记录 Forum #412 的条款、定义、判定路径与原作者意图，作为研究的
    "应然 (should be)" 基线。
(B) **实际执行状态核验**：在 2026.05 时点抓取 L2Beat Stages 页面与代表项目页（Arbitrum One、
    Base、Scroll、Starknet、Polygon zkEVM）快照，**逐项核对该项目当前 Stage 评定是否实际
    依据 Walkaway Test 标准**。`enforcement_status` 字段必须填写为以下四者之一：
    - `proposed`：仅作为 Forum 提案，项目页评定未引用此标准；
    - `adopted`：L2Beat 官方公告（Medium / Monthly Update）确认采纳但未应用于项目页；
    - `grace-period-active`：已采纳并设定 effective_date / grace_period_end，处于过渡期内；
    - `enforced-on-project-pages`：至少一个项目页评定结果可追溯到此标准（如分类调整说明）。

此外需：(a) 列举 proposed Pass/Fail 实例（Arbitrum One、Base "应当"通过；Scroll、Starknet 等
"可能"失败），并明确标注"当前 L2Beat 项目页实际分类"vs"按提案应得分类"的差异；
(b) 整理 Starknet 社区 counterproposal 的核心论点（如 ZK rollup 不应被等同于 Optimistic Rollup 处理）；
(c) 评估该 test 一旦正式 enforced 后对受影响项目的实际降级风险；
(d) 给出该 test 与原有 "Security Council ≥8 / >75%" 量化要求的关系——后者仍然必要但不再充分。

- **Priority**: high
- **Dependencies**: item-3

### item-5: 2025.11→2026.02 迭代 —— ZK Proving System Stage 1 四项要求（Forum #409 + #413 + 2026.02 Medium）

详细解读 L2Beat 在 2025.11（Forum #409 "New Stage 1 requirements for ZK setups"）与
2026.02（Forum #413 + Medium 解释文章 "Stage 1 proving-system requirements"）两次迭代
共同确立的 **ZK proving system Stage 1 四项要求**。本 item 的范围是**ZK proving system
整体**，trusted setup 仅是四项之一。

**核心锚点（round 3 重写）**：

- Forum #409（2025.11）：提出初始 ZK setups 要求，引入 trusted-setup 评级与红线；
- Forum #413（2026.02.16）：将要求收敛为四项可验证条件，并设定 **六个月倒计时 /
  grace period**；
- 2026.02 Medium 解释文章：对四项要求给出官方判定指引与受影响项目示例；
- 2025.07 Forum #381 "ZK Catalog Trusted Setups Framework"：trusted-setup 评级方法
  的基础文本，仍作为子项 (5a) 的判定细则来源。

**四个独立子项**（按 Forum #413 + 2026.02 Medium 的官方表述顺序）：

(5a) **No 🔴 trusted setups**（继承 Forum #381 / #409 评级框架）：
  - 评级方法（🟢/🟡/🔴 三级，依据 trusted setup ceremony 的公开性、参与者数量、
    circuit-dependent 阶段是否公开 audit、是否使用 universal SRS 等）；
  - Stage 1 红线 —— Stage 1 不允许任何 ZK verifier 被评为 🔴；
  - 实例对照（SP1 的 Plonk 使用 Aztec Ignition 公开 ceremony 评为 🟢、SP1 的 Groth16
    wrapper 由 7 人内部完成评级较低；ZKsync Era / Scroll / Polygon zkEVM 等的 verifier 现状）。

(5b) **Prover source code published**：
  - prover 实现（含 circuit、witness generator、aggregation 层）必须以可审计形式公开
    （permissive license 或至少 source-available）；
  - 不能存在 "black-box prover binary" 或 "closed-source proving service" 作为
    proof 提交的必经路径；
  - 与 OP Succinct / SP1 路径直接相关：Mantle 需核验 SP1 上游与 Mantle 自定义层的
    prover 代码可见性。

(5c) **Verifiers reproducible**（独立第三方可重建 verifier 合约 vkey / circuit binding）：
  - L1 verifier 合约部署的 vkey（verification key）必须可由公开 circuit 与公开 setup
    artifacts 独立重新生成，并与链上 vkey 字节一致；
  - 排除 "vkey 来源不可追溯" 或 "circuit binding 需要 trusted operator 介入" 的部署；
  - 与 OP Succinct 直接相关：Mantle 部署的 SP1 verifier 合约 vkey 必须可由开源
    SP1 program ELF + SRS 重建。

(5d) **ZK programs or fault-proof prestates reproducible**：
  - 对 ZK rollup：rollup STF（state transition function）所对应的 ZK program（如
    SP1 ELF / RISC-V binary）必须可由公开源码独立重建，且其 hash 与 verifier 配置中
    的 program hash 一致；
  - 对 Optimistic Rollup：fault-proof prestate（如 MIPS / RISC-V interpreter 的初始状态）
    必须可由公开 monorepo 独立重建，且其 hash 与 dispute game 合约配置一致；
  - 与 OP Succinct 直接相关：Mantle 的 program hash → SP1 program ELF → mantle-v2 /
    op-succinct 源码的可追溯链路必须完整公开。

**复合判定与 enforcement 追踪**：

- (5e) 任一子项不通过即降级 Stage 0（在 grace period 结束后）；
- (5f) 与 item-4 Walkaway Test 的复合效应——一个 ZK rollup 必须同时满足四个子项与
  Walkaway Test 才能保留 Stage 1（前提是后者实际执行状态为 `enforced-on-project-pages`）；
- (5g) **Enforcement 追踪**：四项要求每一项必须独立标注 `enforcement_status ∈
  {proposed | adopted | grace-period-active | enforced-on-project-pages}` + 
  `effective_date`（首次采纳生效日期）+ `grace_period_end`（如 Forum #413 设定的六个月
  倒计时截止日期，约 2026-08-16）+ L2Beat 官方公告链接。

**Mantle / OP Succinct 直接关联（明确入口给下游 issue）**：

- (5a) 适用：核验 SP1 verifier 的 trusted-setup 等级（Aztec Ignition + Succinct 内部
  ceremony 组合的最终评级）；
- (5b) 适用：核验 Mantle 部署链路上 prover 源码（SP1 上游 + mantle-v2 / op-succinct 仓库）
  的公开程度；
- (5c) 适用：核验 Mantle 主网 verifier 合约 vkey 是否可由公开 SP1 program 重建；
- (5d) 适用：核验 Mantle SP1 program (ELF / program hash) 与 mantle-v2 + op-succinct
  monorepo 源码的对应关系；fault-proof prestate 路径（若 Mantle 仍保留任何 fault-proof
  代码）的可重建性。

- **Priority**: high
- **Dependencies**: item-3

### item-6: Stage 2 要求清单与 Stage 1 → Stage 2 的演进路径

整理 Stage 2 的完整要求（Exit Window ≥30 天、Security Council 只能介入可裁决的 onchain bug、
proof system 完全去中心化、proposer / sequencer 完全开放、**完全 permissionless fraud proof
submission**——区别于 Stage 0 "≥5 external actors" 的有限可提交集合）以及从 Stage 1
升级到 Stage 2 所必须移除的"训练轮"。需要：(a) 引用 L2Beat 对 Stage 2 的官方定义；
(b) 列举当前已达成或接近达成 Stage 2 的项目（截至 2026.05，所有命名实例必须附项目页快照）；
(c) 解释为何本研究项目（Mantle Stage 1）暂不聚焦 Stage 2 实现路径——但仍需理解 Stage 2
边界以避免设计 Stage 1 方案时埋下 Stage 2 阻碍；(d) 注意 2026.04 Stage 1 Challenge Period
调整（item-9）是否在 Forum / Medium 中触发了 Stage 2 ≥30d 要求的对应讨论，若有则记录，
若无则明确声明未发现联动证据；(e) 显式列出 Stage 0 → Stage 1 → Stage 2 在 proof-system
permissionlessness 维度的递进：Stage 0 (≥5 external actors for OR) → Stage 1 (Council
compromise condition + proposer liveness) → Stage 2 (fully permissionless submission)。

- **Priority**: medium
- **Dependencies**: item-3, item-9

### item-7: ZK Rollup vs Optimistic Rollup 的 Stage 要求差异矩阵

按"通用要求 × ZK 特有 × OR 特有"三栏对照整理两类 rollup 在 Stage 0/1/2 各项要求上的异同。

**通用项**：
- Proof System 存在性、DA、Walkaway Test（标注其执行状态：proposed/adopted/grace-period-
  active/enforced-on-project-pages）、Security Council 量化阈值、
- **Exit Window 通用规则：outside-SC upgrade exit window ≥5d**（适用 OR + ZK）。

**ZK 特有项**：
- proving system 四子项（5a no 🔴 trusted setup / 5b prover source published / 5c verifiers
  reproducible / 5d ZK programs reproducible，详见 item-5）、
- recursion / aggregation 层的信任假设、
- **不存在"validity-proof challenge period"概念**（明确否定：OR challenge 5d 规则不可
  套用到 ZK 路径）。

**OR 特有项**：
- **fraud proof challenge window ≥5d**（Forum #425 2026.04，仅适用 OR）、
- challenger 集合是否 permissionless（Stage 0 ≥5 external actors → Stage 2 fully
  permissionless）、
- bond / bond-slashing 机制设计。

该矩阵直接服务于 Mantle ——作为 OP Stack fork、采用 OP Succinct 走 ZK 路线的混合架构
（详见 item-8），其评估同时触及"通用项"+"ZK 特有项"两栏，不应触发"OR 特有项"。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-9

### item-8: OP Stack 上的 ZK Rollup（Mantle / OP Succinct 路径）的 Stage 评估特殊考量

针对"基于 OP Stack derivation 与 op-geth 执行层、但用 ZK validity proof（OP Succinct + SP1）
替代 fault proof"这一混合架构，识别 Stage 评估中的非显然问题。需要：

(a) **Proof System 归属**——验证 ZK proof 的 verifier 合约是否被 L2Beat 视作 "rollup
    proof system"，以及与 OP Stack 原生 Fault Dispute Game 的归类差异；代入 item-5 的
    四子项判定：
    - (5a) 适用：SP1 verifier 的 trusted-setup 等级；
    - (5b) 适用：SP1 + Mantle 自有 prover 部署链路源码公开度；
    - (5c) 适用：Mantle 主网 verifier 合约 vkey 的独立重建；
    - (5d) 适用：Mantle SP1 program hash 与 mantle-v2 / op-succinct monorepo 的对应关系。

(b) **Verifier trusted setup 评级**承继自 SP1 上游（Aztec Ignition + Succinct 内部 ceremony）
    以及在 Mantle 自有 verifier 部署时是否需要额外披露。

(c) **Exit Window 的双层叠加（按 item-3 三轨规则评估）**：
    - 适用 (3a) outside-SC upgrade exit window ≥5d：评估 Mantle SystemConfig 治理路径
      与 Optimism Foundation 上游升级路径在非 SC 主体下的 exit window；
    - **不适用** (3b) OR challenge period 5d：Mantle 走 validity-proof 路径，不应被
      错误套用 OR challenge 规则；
    - (3c) Validity/ZK 适用性：如有自定义 finalization delay 应单独评估，但不构成
      L2Beat "challenge period" 定义。

(d) **Walkaway Test 在 ZK 语境下的重新解释**——关键看 challenger / proposer 路径是否仍
    permissionless（OP Succinct 的 proposer/challenger 模型），且需注意 Walkaway Test
    的实际执行状态（item-4）决定本子项的强制性。

(e) **Stage 0 fraud-proof 提交要求的适用性**：Mantle 走 validity-proof 路径，理论上
    不存在 OR 意义的 fraud proof，因此 item-2 (f) "≥5 external actors" 不直接适用；
    替代要求是 item-5 (5c)(5d) 的 verifier/program 可重建性 + permissionless prover
    路径——本子项必须明确这一映射。

(f) 列出对应 Mantle 现状的开放问题清单，作为后续 deep-draft 与
    upgrade-exitwindow-securitycouncil / proposer-decentralization-zk-compliance 两个下游
    issue 的入口。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-7, item-9

### item-9: 2026.04 Forum #425 —— Optimistic Rollup Challenge Period 7d→5d（及对 ZK 路径的不适用性澄清）

详细解读 2026 年 4 月生效的 L2Beat Forum #425 调整：
**Optimistic Rollup 的最低 challenge period 从 7 天降至 5 天，并将 withdrawal-period
组件从 active 要求中移除**。

**核心边界澄清（round 3 重写，与 round 2 的关键差异）**：

Forum #425 的语境是 **Optimistic Rollup 专用**——L2Beat 在原帖中明确指向 OR 的
fraud-proof challenge window。本研究**不得**将 5d 阈值通用化到 validity-proof / ZK 路径：

- ZK rollup 不存在 "validity-proof challenge period" 概念；
- ZK rollup 的相关 Exit Window 要求由 item-3 (3a) "outside-SC upgrade exit window ≥5d"
  通用规则承担（适用 OR + ZK 两类）；
- 任何将 Forum #425 的 5d 阈值用于 Mantle / OP Succinct 等 validity-proof 路径的
  challenge-period 检验都属于 false-positive 误判。

本 item 必须覆盖：

(a) **规则变更的精确文本**：从 Forum #425 提取原始条款与定义，明确"5 天"指代的是
    **Optimistic Rollup 的 fraud-proof challenge window**（即 fraud proof 提交窗口），
    而非用户提款延迟，也**不**适用于 validity-proof 路径。

(b) **历史公式 vs 当前 OR 规则对照**：
  - 历史公式（2026.04 之前）：
    `Effective Exit Window = Upgrade Delay − Challenge/Forced-Tx Delay − Withdrawal Delay`，
    Stage 1 需 ≥7d；
  - 当前 OR 规则（2026.04 起）：challenge period 最低 5d 直接作为 Optimistic Rollup
    Stage 1 评定阈值，withdrawal-period 不再扣减；
  - 整理 L2Beat 官方对该变更的理由说明（如 withdrawal-period 与 active security
    关联不强、7d 阈值过严导致项目难以达成 Stage 1 等）。

(c) **边界项目的重新评估（仅限 OR）**：
  - Arbitrum (11d upgrade − 1d force-tx)、dYdX v3 (9d challenge, 14d forced-exit)
    等 Optimistic Rollup 项目按新规则的判定结果是否改变；
  - ZKsync Lite (21d − 14d) 等 ZK 项目**不应**按 Forum #425 重新评估，应按 item-3
    (3a) outside-SC upgrade 规则评估；
  - 任何因新规则**新增通过 Stage 1** 的 OR 项目（需附项目页快照确认）；
  - 任何因新规则**当前 Stage 评定调整** 的项目（需附 L2Beat 公告链接）。

(d) **执行状态（enforcement_status）**：截至 2026.05 是否已在 L2Beat 项目页与 Stages
    页面实际应用此 5d 规则；标注 `proposed | adopted | grace-period-active |
    enforced-on-project-pages` 之一，并附 `effective_date` / `grace_period_end`（若适用）。

(e) **对 Stage 2 的潜在影响**（与 item-6 联动）：若 Stage 1 阈值下调，是否在 Forum /
    Medium 中触发了 Stage 2 ≥30d 要求的对应讨论；若无联动证据则明确声明。

(f) **对 Mantle 的直接关联（重要：明确非适用）**：
  - Mantle 当前合约升级延迟与 outside-SC upgrade 路径在 (3a) ≥5d 通用规则下的判定结果
    （详细分析交由下游 upgrade-exitwindow-securitycouncil issue，本 item 仅给出判定接口
    与所需输入）；
  - Mantle 走 validity-proof 路径，**不**承担 Forum #425 OR challenge 5d 规则；
  - 本 item 在 Mantle 章节必须显式声明此非适用关系，避免下游误用。

- **Priority**: high
- **Dependencies**: item-3

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| requirement_summary | 该项要求的 1-3 句精确描述（避免模糊表述，每个动词必须可验证） | all |
| evaluation_criteria | 判定通过/不通过的具体技术条件（含阈值、公式、边界值） | item-2, item-3, item-4, item-5, item-6, item-9 |
| applicable_rollup_type | 该要求/子项适用的 rollup 类型：`all` / `optimistic-only` / `zk-only`；用于显式标注 Forum #425 5d 规则仅适用 OR、outside-SC upgrade ≥5d 适用 all、ZK proving-system 四子项仅适用 ZK 等边界 | item-3, item-5, item-7, item-9 |
| stage_boundary | 该要求所属的 Stage 边界（Stage 0 / Stage 1 / Stage 2），用于显式标注 "≥5 external actors fraud-proof submission" 在 Stage 0、"Council compromise condition + proposer liveness" 在 Stage 1、"fully permissionless submission" 在 Stage 2 等关键边界 | item-2, item-3, item-6 |
| pass_fail_examples | 至少 1 个 Pass 与 1 个 Fail 的具体项目实例，含原因拆解；每个命名实例必须附 L2Beat 项目页快照链接（验证前一律视为假设） | item-3, item-4, item-5, item-6, item-9 |
| delta_from_prior_version | 相比 2025.10（或对应基线版本）的版本变化点，含生效日期与官方公告链接 | item-2, item-4, item-5, item-9 |
| enforcement_status | 该要求/变更截至 2026.05 的实际执行状态，四选一：`proposed`（仅 Forum 提案，项目页未引用）/ `adopted`（官方公告确认但未应用于项目页）/ `grace-period-active`（已采纳并设定 effective_date / grace_period_end，处于过渡期内）/ `enforced-on-project-pages`（至少一个项目页评定结果可追溯到此标准） | item-4, item-5, item-9 |
| effective_date | 该要求/变更的首次生效日期（ISO-8601），用于精确锚定执行起点 | item-4, item-5, item-9 |
| grace_period_end | 该要求/变更的过渡期截止日期（ISO-8601），仅 `grace-period-active` 状态适用；Forum #413 设定的六个月倒计时约 2026-08-16 | item-5, item-9 |
| zk_vs_optimistic_differentials | 对 ZK / OR 两类 rollup 的差异化要求（若该项存在差异） | item-3, item-5, item-7, item-9 |
| relevance_to_mantle | 该项对 Mantle（OP Stack + OP Succinct ZK proof）的直接关联与潜在 gap；必须显式标注是"适用"还是"非适用"（如 Forum #425 OR challenge 5d 对 Mantle 非适用） | item-3, item-4, item-5, item-7, item-8, item-9 |
| evidence_sources | 一手来源链接清单（Forum / Medium / Stages 页面 / Glossary 永久链接），优先永久版本/快照链接 | all |
| open_questions | 当前公开材料中未明确、需要进一步确认或观察的问题 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy | Stage 0 → Stage 1 → Stage 2 要求递进图：以三阶段为列，每列列出该阶段新增/收紧的要求；显式标注 proof-system 维度的边界（Stage 0: state-reconstruction + ≥5 external actors for OR；Stage 1: Council compromise + proposer liveness；Stage 2: fully permissionless submission），并标注 Walkaway / Council / Exit Window / ZK Proving System 子项归属 | mermaid | item-1, item-2, item-3, item-6 |
| diag-2 | flow | Stage 1 检查清单流程图（2026.05 当前规则）：决策树形式串联 Stage 1 的判定维度。Exit Window 节点拆分为三个并列子分支（与 item-3 三轨规则对应）：(i) outside-SC upgrade exit window ≥5d (适用 OR+ZK)、(ii) OR-only: challenge period ≥5d (Forum #425)、(iii) ZK-only: validity-proof 不适用 challenge period 概念，仅承担 (i)。ZK Proving System 节点展开为四子项 (5a-5d) 全通过检查。其他节点：Proof System 存在 → Council ≥8/>75%/外部≥50% → Walkaway Test enforcement_status 检查。每个节点旁注明"规范源"与"当前是否 enforced"两条独立信息 | mermaid | item-3, item-4, item-5, item-9 |
| diag-3 | comparison | ZK Rollup vs Optimistic Rollup Stage 要求差异矩阵：三栏对照（通用 / ZK 特有 / OR 特有）。通用栏包含 outside-SC upgrade ≥5d、Walkaway 执行状态、Council 阈值；ZK 特有栏指向 item-5 四子项 + 显式标注"不存在 validity-proof challenge period"；OR 特有栏包含 Forum #425 challenge 5d + Stage 0 ≥5 external actors + Stage 2 fully permissionless 演进 | mermaid | item-7 |
| diag-4 | flow | Walkaway Test 判定流程图：以"Security Council 消失"为假设输入，逐步检查 (a) 用户能否强制交易、(b) 提款是否依赖 Council 签名、(c) Proposer 集合是否开放、(d) Verifier 是否独立运行；任一依赖 Council 即 Fail。注：该图描述的是**提案文本的判定逻辑**，实际是否影响项目分类取决于 item-4 的 enforcement_status（proposed/adopted/grace-period-active/enforced-on-project-pages） | mermaid | item-4 |
| diag-5 | timeline | L2Beat 框架演进时间线：2023.06 Stages 提出 → 2023.12 Council 量化更新 → 2024.12 Proof System Mandatory → 2025.07 ZK Catalog Setups Framework (#381) → 2025.11 ZK Proving System 初始要求 (#409) → 2025.12 Walkaway Test 提案 (#412) → **2026.02 ZK Proving System 四项要求收敛 (#413 + Medium)** → **2026.04 OR Challenge Period 7d→5d (#425)** → 2026.05 当前快照。每个节点标注 enforcement_status、effective_date、grace_period_end（若适用）与对 Mantle 的影响窗口 | mermaid | item-2, item-4, item-5, item-9 |
| diag-6 | comparison | **Exit Window 三轨规则对照图（round 3 重写）**：三列并列展示 (1) outside-SC upgrade exit window ≥5d（适用 OR + ZK，基于 Stages Framework 通用规则）、(2) Optimistic Rollup challenge period ≥5d（Forum #425 2026.04，仅适用 OR）、(3) Validity/ZK 适用性说明（明确否定"validity-proof challenge period"概念）。底部展示历史公式（2026.04 之前 OR ≥7d + withdrawal-period 扣减）作为版本对比。各列标注代表项目（OR: Arbitrum / dYdX v3；ZK: ZKsync Lite / Mantle）在该轨规则下的判定路径 | mermaid | item-3, item-9 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | L2Beat 官方 Stages 页面与 Glossary：https://l2beat.com/stages、https://l2beat.com/glossary（必须使用永久版本/快照链接以锁定 2026.05 时点状态） | 2 |
| src-2 | governance_proposals | L2Beat Forum 一手帖子（必须覆盖以下 6 条）：The Stages Framework (#291)、Trusted Setups Framework for ZK Catalog (#381)、New Stage 1 requirements for ZK setups (#409)、Security Council Walkaway Test (#412)、**ZK Proving System Stage 1 四项要求 (#413, 2026.02.16)**、**Optimistic Rollup Challenge Period 7d→5d (#425, 2026.04)** | 6 |
| src-3 | expert_commentary | L2Beat Medium 文章：Introducing Stages (Luca Donno)、Framework update: L2 projects recategorization (Bartek Kiepuszewski, 2024.12)、Stages update: Security Council requirements (Luca Donno)、**2026.02 Medium 解释文章（ZK Proving System Stage 1 四项要求的官方判定指引）**、2026.04 challenge-period 调整对应的公告（若存在） | 4 |
| src-4 | on_chain_data | **每个在大纲中被命名为 pass/fail 示例的项目**（包括但不限于 Arbitrum One、Base、Scroll、Starknet、Polygon zkEVM、ZKsync Lite、dYdX v3）都必须附其 L2Beat 项目页 2026.05 快照链接；未附快照的实例在 draft 中只能作为"假设"出现，不能作为事实陈述。该 src 计数为命名实例总数，下限 5 | 5 |
| src-5 | expert_commentary | 社区 counterproposal 与第三方分析（如 Starknet 团队对 Walkaway Test 的反馈、ZK/SEC Quarterly 的 formal 分析、Vitalik 关于 "Stage 1 or GTFO" 的公开表态） | 2 |
| src-6 | official_docs | L2Beat Monthly Updates（覆盖 2025.11、2025.12、2026.01、2026.02、2026.04、2026.05 六期，用于捕获 outline 未覆盖的细则变更与四项更新的 enforcement 进展） | 3 |

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
| 3 | modify_item | item-3 | Exit Window 子项由 round-2 双轨表述重构为**三轨规则** (3a) outside-SC upgrade exit window ≥5d (适用 OR+ZK) / (3b) Optimistic Rollup challenge period ≥5d (Forum #425 仅适用 OR) / (3c) Validity/ZK 适用性说明（明确否定 validity-proof challenge period 概念）；并将 Stage 1 proof-system 措辞由 round-2 的 "permissionless (anyone can submit fraud proof / validity proof)" 改为 Stage 1 准确的 "Security Council compromise condition + proposer-set liveness assumption"，明确 "≥5 external actors" 属 Stage 0、"fully permissionless" 属 Stage 2 | Round-2 Adversarial Major #1 (Exit Window 过度泛化) + Major #3 (Stage 边界模糊) |
| 3 | modify_item | item-2 | Stage 0 清单显式新增 (e) state-reconstruction software 必须存在、(f) 至少 5 个外部参与者可提交 fraud proof（OR），并明确这两项属于 **Stage 0**（而非 Stage 1）；与 item-6 Stage 2 的 "fully permissionless submission" 形成完整边界对照 | Round-2 Adversarial Major #3 (Stage 0/1/2 proof system 边界模糊) |
| 3 | modify_item | item-5 | 重锚定为 Forum #413 (2026.02.16) + Forum #409 + 2026.02 Medium 的迭代过程；四项要求重构为：(5a) no 🔴 trusted setups、(5b) prover source code published、(5c) verifiers reproducible (vkey)、(5d) ZK programs or fault-proof prestates reproducible；移除 round-2 的 "proof-system maturity / permissionless proposer 三段结构"（来源不匹配）；显式追踪 effective_date 与 grace_period_end（Forum #413 六个月倒计时约 2026-08-16）；Mantle/OP Succinct 关联拆解到四子项 | Round-2 Adversarial Major #2 (Proving System 要求来源不匹配) |
| 3 | modify_item | item-6 | Stage 2 清单显式新增"完全 permissionless fraud proof submission"作为 Stage 2 边界，并新增 (e) Stage 0→1→2 proof-system permissionlessness 维度的递进说明，与 item-2 / item-3 形成统一边界对照 | Round-2 Adversarial Major #3 (Stage 边界一致性传播) |
| 3 | modify_item | item-7 | ZK vs OR 矩阵更新：通用项新增 outside-SC upgrade ≥5d（适用 all）；ZK 特有项更新为 item-5 **四子项**（替代原三子项）并显式包含"不存在 validity-proof challenge period"否定项；OR 特有项明确 Forum #425 challenge 5d 仅 OR、Stage 0 ≥5 external actors → Stage 2 fully permissionless 演进 | Round-2 Adversarial Major #1 + #2 + #3 (三项一致性传播) |
| 3 | modify_item | item-8 | OP Stack + OP Succinct 评估更新：(a) 接入 item-5 **四子项**判定；(c) Exit Window 子项采用 item-3 **三轨规则**评估，明确 Forum #425 OR challenge 5d **不适用** Mantle；(e) 新增 Stage 0 "≥5 external actors" 在 validity-proof 路径下的不适用性与替代映射（item-5 (5c)(5d) + permissionless prover 路径） | Round-2 Adversarial Major #1 + #2 + #3 (Mantle 路径一致性) |
| 3 | modify_item | item-9 | 严格限定 Forum #425 5d 阈值为 **Optimistic Rollup challenge period 专用**；新增 (a) 文本中显式标注非 validity-proof 适用、(c) 边界项目重新评估按 OR / ZK 分别走 (3b) / (3a) 规则、(f) 对 Mantle 章节显式声明 Forum #425 非适用关系；与 item-3 (3a)(3b)(3c) 三轨规则形成完整闭环 | Round-2 Adversarial Major #1 (Exit Window 过度泛化) |
| 3 | modify_item | item-1 | 三阶段定位描述与 item-2/item-3/item-6 的 proof-system 维度边界对齐：Stage 0 含 state-reconstruction + ≥5 external actors (for OR)、Stage 1 = Council compromise + proposer liveness、Stage 2 = fully permissionless + Council 仅介入可裁决 onchain bug | Round-2 Adversarial Major #3 (Stage 边界一致性传播) |
| 3 | modify_field | enforcement_status | 取值集合由 round-2 的三态扩展为**四态**：`proposed | adopted | grace-period-active | enforced-on-project-pages`；新增 grace-period-active 用于显式追踪 Forum #413 六个月倒计时窗口与类似过渡期 | Round-2 Adversarial Major #2 (Proving System enforcement 追踪) |
| 3 | add_field | effective_date | 强制 item-4/item-5/item-9 标注变更首次生效日期（ISO-8601），用于精确锚定执行起点 | Round-2 Adversarial Major #2 (Proving System enforcement 追踪) |
| 3 | add_field | grace_period_end | 强制 item-5/item-9 在 grace-period-active 状态下标注过渡期截止日期（ISO-8601），如 Forum #413 约 2026-08-16 | Round-2 Adversarial Major #2 (Proving System enforcement 追踪) |
| 3 | add_field | applicable_rollup_type | 强制 item-3/item-5/item-7/item-9 在每条要求/子项上显式标注 `all | optimistic-only | zk-only`，用于在 deep-draft 中防止 OR-only 规则误用到 ZK 路径（如 Forum #425 5d）或反向误用 | Round-2 Adversarial Major #1 (Exit Window 过度泛化) |
| 3 | add_field | stage_boundary | 强制 item-2/item-3/item-6 在每条要求上显式标注 `Stage 0 | Stage 1 | Stage 2`，用于在 deep-draft 中精确划分 "≥5 external actors" (Stage 0)、"Council compromise + proposer liveness" (Stage 1)、"fully permissionless" (Stage 2) 等关键边界 | Round-2 Adversarial Major #3 (Stage 0/1/2 边界) |
| 3 | modify_field | relevance_to_mantle | 描述更新：必须显式标注"适用"或"非适用"——如 Forum #425 OR challenge 5d 对 Mantle (validity-proof) **非适用**，Stage 0 "≥5 external actors fraud-proof" 对 Mantle **非适用**且映射到 item-5 替代要求 | Round-2 Adversarial Major #1 + #3 (Mantle 边界澄清) |
| 3 | modify_diagram | diag-2 | Stage 1 检查清单流程图重构：Exit Window 节点拆分为**三个并列子分支**与 item-3 三轨规则对应——(i) outside-SC upgrade ≥5d (适用 OR+ZK)、(ii) OR-only Forum #425 challenge ≥5d、(iii) ZK-only 不适用 challenge period 概念仅承担 (i)；ZK Proving System 节点由原三子项展开为**四子项** (5a-5d) | Round-2 Adversarial Major #1 + #2 (Exit Window + Proving System 来源) |
| 3 | modify_diagram | diag-3 | ZK vs OR 矩阵更新：通用栏新增 outside-SC upgrade ≥5d 行；ZK 特有栏指向 item-5 **四子项**并显式包含"不存在 validity-proof challenge period"否定项；OR 特有栏明确 Forum #425 challenge 5d 仅 OR + Stage 0 ≥5 external actors + Stage 2 fully permissionless 演进 | Round-2 Adversarial Major #1 + #2 + #3 |
| 3 | modify_diagram | diag-5 | 时间线新增 **2026.02 节点（ZK Proving System 四项要求收敛, Forum #413 + Medium）**；每个节点扩展标注 effective_date 与 grace_period_end（若适用） | Round-2 Adversarial Major #2 |
| 3 | modify_diagram | diag-6 | Exit Window 对照图由 round-2 的"历史 vs 当前"二列重构为**三轨规则对照**：(1) outside-SC upgrade ≥5d (适用 OR+ZK)、(2) OR challenge ≥5d (Forum #425)、(3) Validity/ZK 适用性说明（明确否定 validity-proof challenge period 概念）；底部保留历史公式作为版本对比；各轨标注代表项目（OR: Arbitrum / dYdX v3；ZK: ZKsync Lite / Mantle） | Round-2 Adversarial Major #1 (Exit Window 过度泛化) |
| 3 | modify_diagram | diag-1 | Stage 递进图显式标注 proof-system 维度的三阶段边界：Stage 0 (state-reconstruction + ≥5 external actors for OR)、Stage 1 (Council compromise + proposer liveness)、Stage 2 (fully permissionless submission)，避免后续 item-2/item-3/item-6 解读时出现边界混淆 | Round-2 Adversarial Major #3 |
| 3 | modify_source_req | src-2 | Forum 一手帖子最小覆盖数由 5 提升到 **6**，新增 **#413 (2026.02.16 ZK Proving System Stage 1 四项要求)** 作为强制来源（与 #409 / #425 并列） | Round-2 Adversarial Major #2 (Proving System 来源) |
| 3 | modify_source_req | src-3 | Medium 文章列表新增 **2026.02 Medium 解释文章（ZK Proving System Stage 1 四项要求官方判定指引）** 作为强制来源；最小数由 3 提升到 4 | Round-2 Adversarial Major #2 (Proving System 来源) |
| 3 | modify_source_req | src-6 | Monthly Updates 覆盖范围扩展到 2025.11、2025.12、2026.01、2026.02、2026.04、2026.05 **六期**（新增 2026.02 期以捕获 Forum #413 + Medium 发布同期的 enforcement 进展） | Round-2 Adversarial Major #2 |
