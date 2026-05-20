---
topic: "L2Beat Risk Chart Proposer Failure 与 Exit Window 评估标准解析"
project_slug: mantle-l2beat-risk-deficiency
topic_slug: l2beat-risk-assessment-framework
github_repo: Whisker17/multica-research
round: 3
status: candidate

artifact_paths:
  outline: mantle-l2beat-risk-deficiency/outlines/l2beat-risk-assessment-framework.md
  draft: mantle-l2beat-risk-deficiency/research-sections/l2beat-risk-assessment-framework/drafts/round-{n}.md
  final: mantle-l2beat-risk-deficiency/research-sections/l2beat-risk-assessment-framework/final.md
  index: mantle-l2beat-risk-deficiency/research-sections/_index.md

scope: |
  系统化解析 L2Beat Risk Analysis 模型中 **Proposer Failure** 与 **Exit Window** 两项指标的评估口径与判定逻辑，
  为后续 Mantle 在这两项上的根因分析与改进方案提供**通用、可复用的框架基线**。覆盖范围：

  (1) **L2Beat Risk Chart 五维总览**：在解析两项核心指标前，先简要标定 L2Beat 风险五元组
      （Sequencer Failure、State Validation、Data Availability、Exit Window、Proposer Failure）
      的相互关系与位置，明确本研究只解构 Exit Window + Proposer Failure，其他三项仅作 context 链接，
      不在本 issue 内重新评估（与 out-of-scope 一致）。

  (2) **Proposer Failure 指标完整解构**：
      - L2Beat 对该指标"考察的核心问题"——proposer 停止运作时用户能否独立提走 L2 资产；
      - 五种典型 outcome 文案与 sentiment（基于 l2beat/l2beat 仓库 packages/config/src/common/riskView.ts 中的常量定义）：
        `PROPOSER_CANNOT_WITHDRAW`（red, "Cannot withdraw"，proposer 白名单且无 fallback）、
        `PROPOSER_WHITELIST_GOVERNANCE`（warning, "Replace proposer"，可通过 governance 升级替换 proposer）、
        `PROPOSER_WHITELIST_SECURITY_COUNCIL`（warning, "Security Council minority"，SC 少数派可强制出块）、
        `PROPOSER_USE_ESCAPE_HATCH_ZK/MP/...`（good, "Use escape hatch"，用户可凭 ZK proof / Merkle proof 自助退出）、
        `PROPOSER_SELF_PROPOSE_*`（good, "Self propose"，permissionless prover/proposer 路径）；
      - 影响判定的关键技术因素：proposer 是否 permissionless / 白名单是否带 fallback timeout /
        是否存在 escape hatch / 是否依赖 fraud proof system 而非 validity proof；
      - 在 OP Stack + OpSuccinct (validity-proof) 路径下，opStack 模板 `getRiskViewProposerFailure`
        函数直接 hardcode 返回 `PROPOSER_CANNOT_WITHDRAW`（packages/config/src/templates/opStack.ts:1438-1440），
        必须显式分析这条代码路径与"validity proof 路径不需要 challenge 但需要 proposer 出块"的关系；
      - 不满足时用户资产的实际影响：withdrawal 完全冻结、依赖 governance/SC 紧急升级才能恢复、
        最坏情况下若升级权同样冻结则资产永久无法提取。

  (3) **Exit Window 指标完整解构**：
      - L2Beat 对该指标"考察的核心问题"——非紧急合约升级发起后，用户在升级生效前是否有足够时间提走资产；
      - 评估公式：`window = upgradeDelay - exitDelay`（packages/config/src/common/riskView.ts:642-687
        `EXIT_WINDOW(upgradeDelay, exitDelay, options)` 函数），sentiment 阈值
        `< 7 day = bad / 7-30 day = warning / ≥ 30 day = good`，window ≤ 0 显示为 `None`；
      - 七类 Exit Window 函数变体（`EXIT_WINDOW`、`EXIT_WINDOW_NITRO`、`EXIT_WINDOW_PERMISSIONLESS_BOLD`、
        `EXIT_WINDOW_ZKSTACK`、`EXIT_WINDOW_NON_UPGRADABLE`、`EXIT_WINDOW_UNKNOWN`、`EXIT_WINDOW_STARKNET`）
        各自的入参语义与判定边界；
      - 关键技术因素：upgradeDelay（TimelockController.minDelay 或等价的 L1/L2 timelock）、
        exitDelay（提款 finalization period / challenge period / force-inclusion delay）、
        Security Council instant-upgrade 是否绕过 timelock、
        TransactionFilterer 等 censorship vector 是否会变相缩短 window；
      - OP Stack 默认路径：`getRiskViewExitWindow` 调用 `EXIT_WINDOW(0, finalizationPeriod)`
        （packages/config/src/templates/opStack.ts:1387-1401），upgradeDelay 被 **hardcode 为 0**，
        即模板假设"instantly upgradable"——除非项目通过 `nonTemplateRiskView.exitWindow` 覆盖；
        若 `hasSuperchainScUpgrades` 为 true，则直接返回 "None" 红色文案；
      - 不满足时用户资产的实际影响：合约可在用户无感知情况下被恶意/瑕疵升级，用户无 ≥7d 窗口完成
        L2 提款；最坏情况升级后资金被合法路径冻结或重定向。

  (4) **L2Beat 评估管线的数据来源与人工/自动比重**：
      - `ProjectDiscovery` 模块（packages/config/src/discovery/ProjectDiscovery.ts）+
        `discovered.json` 链上抓取的合约值（如 `FINALIZATION_PERIOD_SECONDS`、`respectedGameType`、
        Timelock `minDelay`）；
      - 项目特定 `nonTemplateRiskView.*` 覆盖（人工配置）；
      - 模板默认（opStack / orbitStack / zkStack / agglayer / nitro 等）；
      - 三层数据来源的优先级与人工干预点——这是后续解释"为什么 Mantle 不能通过单纯改链上参数提升评级"的关键。

  (5) **典型项目评级对比（OR vs ZK Validity vs ZK ZKSync 三类典型）**：
      - 选取 3-5 个代表项目对照（如 Arbitrum One BoLD / Optimism Mainnet / Base / Mantle / zkSync Era / Starknet），
        逐项给出 Proposer Failure + Exit Window 文案、对应 RISK_VIEW 常量、对应模板函数；
      - 显式列出每个项目的差异化原因（fraud-proof 类型、是否有 permissionless prover、
        L1/L2 timelock 配置、SC instant-upgrade 权限、escape hatch 是否就绪）；
      - 输出"可复制的评级提升路径"分类——但**不**给出 Mantle 的具体改进方案（由
        mantle-proposer-failure-analysis / mantle-exit-window-analysis / recommendation-proposal 三个下游 issue 覆盖）。

  本 issue 严格限定在"L2Beat 评估框架本身的解读"层面，**不**做 Mantle 现状盘点（由 mantle-proposer-failure-analysis
  与 mantle-exit-window-analysis 两个下游 issue 处理），**不**给出改进建议（由 recommendation-proposal 覆盖），
  **不**评估 State Validation / Data Availability / Sequencer Failure（与 out-of-scope 一致）。
  **硬性 guardrail：L2Beat Stage 1/2 框架与 Risk Chart 是两套独立评估体系。** Stage 框架中的阈值
  （Exit Window ≥5d、Security Council 少数派要求等）**禁止**被用作定义本研究 Risk Chart sentiment
  （`< 7d = bad / 7-30d = warning / ≥ 30d = good`）的依据——两者来自不同的判定系统，混用将导致评估口径错误。
  l2beat-stage-framework-2026 final 仅作为**可选 context**：当且仅当某项对比需要 Stage 体系作为背景脚注时，
  方可以脚注形式引用，且必须显式声明"该阈值不参与 Risk Chart sentiment 判定"。

audience: |
  Mantle 协议工程师与治理团队（理解 L2Beat 评级机制，作为后续改进 issue 的框架输入）；
  Multica 研究 squad 内部下游 Research Agent（mantle-proposer-failure-analysis、
  mantle-exit-window-analysis、recommendation-proposal）——本 issue 是这三者的**事实基线**与**评估口径**；
  L2Beat 生态参与者（关注其他 OP Stack + OpSuccinct 项目同样面临的评级机制）；
  研究 L2 安全模型的协议研究者、L2Beat 评级争议（如 Forum 上的标准更新讨论）的参与者。
  阅读者熟悉 L2 rollup 基本架构（OptimismPortal、output oracle、proposer、proxy）、
  TypeScript 阅读能力（理解 l2beat/l2beat 仓库的 config 文件结构），但不一定熟悉 L2Beat 评估代码的精确层次
  与 risk-view 函数库的完整 enum。

expected_output: |
  - **Risk Chart 五维总览图**：L2Beat 风险五元组的二维位置图（横轴=运行风险 vs 升级风险；
    纵轴=数据/状态层 vs 治理层），显式标注 Proposer Failure 属于运行/状态层、
    Exit Window 属于治理/升级层，两者的边界与重叠点（如 SC 同时持有 instant-upgrade
    与 proposer registry 时两个指标可能同时失分）。
  - **Proposer Failure 完整字典**：
    (a) L2Beat 该指标的核心考察问题（一句话定义 + 出处 URL/文件行号）；
    (b) 全部 RISK_VIEW 常量与函数枚举表（packages/config/src/common/riskView.ts），
        每项含：常量名、显示文案 (`value`)、`description`、`sentiment`（good/warning/bad）、
        `orderHint`、典型适用场景与代表项目；
    (c) 各模板（opStack、orbitStack、zkStack、agglayer、nitro）中 Proposer Failure 判定函数
        （如 `getRiskViewProposerFailure`）的完整伪代码或精确引用，含 `fraudProofType`
        switch case 与对应分支；
    (d) 不满足判定（"Cannot withdraw" red）下用户资产的故障树：proposer 离线 →
        state root 停止更新 → withdrawal proof 无法生成 → bridge 永冻 → 是否可通过 governance
        升级替换 proposer / 是否存在 escape hatch / 是否需要 SC 强制出块。
  - **Exit Window 完整字典**：
    (a) L2Beat 该指标的核心考察问题（一句话定义 + 出处 URL/文件行号）；
    (b) 评估公式 `window = upgradeDelay - exitDelay` 的精确 TypeScript 代码引用（含行号）
        与 sentiment 阈值表（< 7d / 7-30d / ≥ 30d）；
    (c) 七类 EXIT_WINDOW 变体函数（普通、Nitro、Permissionless BoLD、ZKSync ZKStack、
        Non-upgradable、Unknown、Starknet）的入参与典型适用场景；
    (d) 各模板中 Exit Window 判定函数（如 opStack `getRiskViewExitWindow`、
        orbitStack 中对应函数、zkStack 中对应函数）的逻辑解读，特别强调
        opStack 模板的 hardcode `upgradeDelay = 0` 默认假设；
    (e) 不满足判定（"None" red）下用户资产的故障树：项目方/SC 发起恶意升级 →
        proxy implementation 切换 → 用户提款路径或被改写或被冻结 → 用户是否在升级生效前
        有足够窗口完成 L2-to-L1 withdrawal（包括 force-inclusion delay 与 finalization period）。
  - **L2Beat 评估管线数据来源拓扑**：
    数据流：链上 (Etherscan / RPC) → ProjectDiscovery → discovered.json → 模板默认 +
    nonTemplateRiskView 覆盖 → 最终页面渲染 (frontend rosette/risks)；
    每一步注明：(i) 涉及的文件与函数；(ii) 数据更新频率（discovery 自动 vs 人工配置）；
    (iii) 人工干预点（项目方提交 PR / L2Beat 团队手动 review）。
  - **典型项目评级对比表**：
    | 项目 | Stack | Fraud Proof Type | Proposer Failure 文案 + 常量 | Exit Window 文案 + 公式 | 关键差异化因素 |
    覆盖至少 5 个项目（建议：Mantle、Optimism Mainnet、Base、Arbitrum One BoLD、zkSync Era、Starknet）。
  - **至少 3 张 Mermaid 图**（详见 Diagram Expectations）。
  - **Evidence**：≥5 类一手来源（l2beat/l2beat 仓库源码 commit hash 永久链接、
    L2Beat 项目页快照、L2Beat 官方 Stages/Risk 文档、L2Beat Forum 关于评估方法的帖子、
    上游 final/draft）。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-20T00:35:00Z"
  last_modified_by: "agent:orchestrator (Orchestrator, id=273629f0-3fe7-47c4-aae7-846a11dbbe13)"
  last_modified_at: "2026-05-20T03:00:00Z"
---

# Research Outline: L2Beat Risk Chart Proposer Failure 与 Exit Window 评估标准解析

## Items

### item-1: L2Beat Risk Chart 五维总览与本研究的位置标定

简要标定 L2Beat 风险五元组（Sequencer Failure、State Validation、Data Availability、Exit Window、
Proposer Failure）的相互关系与边界，作为后续两个指标深度解构的 context 锚点。

(a) **五元组的概念分层**：
- **数据/状态层**：State Validation（state root 正确性证明机制）、Data Availability（交易数据可获得性）；
- **运行/活性层**：Sequencer Failure（排序中断时用户能否自助包含交易）、Proposer Failure（出块停滞时用户能否提款）；
- **治理/升级层**：Exit Window（合约升级前用户的退出窗口）；
- 三类的相互依赖：若 Exit Window = None 且 Proposer Failure = Cannot withdraw，则用户在升级前夕无法逃逸；
  若 Sequencer Failure = No mechanism 与 Proposer Failure = Cannot withdraw 同时成立，则即使有 Exit Window
  也无法触发 L2→L1 强制交易。

(b) **本研究的边界**：
- **In scope**：Proposer Failure（item-2）+ Exit Window（item-3）的评估口径、源码逻辑、
  数据来源、典型项目对比；
- **Out of scope（仅作 context 链接，不重新评估）**：Sequencer Failure、State Validation、Data Availability；
  L2Beat Stage 1/2 框架不属于本研究范畴，**不得**将其阈值（如 Exit Window ≥5d、SC 少数派要求等）用作
  Risk Chart sentiment 判定依据；l2beat-stage-framework-2026 final 仅作**可选 pointer note**，
  在需要 Stage 体系背景脚注时以脚注形式引用，且必须显式声明"该阈值不参与 Risk Chart sentiment 判定"；
- 与下游 issue 的接口：本 item 输出的"五维总览"是 mantle-proposer-failure-analysis、
  mantle-exit-window-analysis、recommendation-proposal 三个下游 issue 的事实基线。

(c) **L2Beat Risk Chart 的 UI 表征与源码索引**：
- 前端渲染：`packages/frontend/src/server/features/scaling/project/getScalingRosetteValues.ts`
  与 `packages/frontend/src/pages/scaling/risk/components/table/columns.tsx`；
- 数据结构：`packages/config/src/types.ts` 中 `ProjectScalingRiskView` 与 `TableReadyValue`、
  `ExitWindowRisk` 等类型定义；
- 数据汇集：每个项目通过 `packages/config/src/projects/{project}/{project}.ts` 的
  `scaling.riskView` 字段或继承自模板。

- **Priority**: high
- **Dependencies**: none

### item-2: Proposer Failure 指标完整解构（评估问题、判定逻辑、五种 outcome、影响分析）

逐项解构 Proposer Failure 指标的 L2Beat 评估口径，作为后续 mantle-proposer-failure-analysis（下游）的
评估框架。

(a) **L2Beat 对 Proposer Failure 的核心考察问题**：
- "当 proposer 停止运作时，用户能否独立将 L2 资产提走？"
- 评估视角：proposer 是 rollup 中负责把 L2 state root 提交到 L1 的角色——proposer 不出块
  即意味着 L1 上没有 state root 可供 withdrawal proof 引用 → 用户无法完成提款；
- 评估的关键 binary：是否存在 permissionless 的备用路径（任意人提交 proof / 任意人作 proposer）。

(b) **完整 RISK_VIEW 常量与函数枚举**（基于 packages/config/src/common/riskView.ts，行号锚定）：

| 常量/函数 | 行号 | value | sentiment | 适用场景 |
|---|---|---|---|---|
| `PROPOSER_CANNOT_WITHDRAW` | ~516-522 | "Cannot withdraw" | bad | proposer 白名单且无 fallback；OpSuccinct / OP Stack pre-FaultProof |
| `PROPOSER_WHITELIST_GOVERNANCE` | ~524-530 | "Replace proposer" | warning | governance 可升级替换 proposer |
| `PROPOSER_WHITELIST_SECURITY_COUNCIL(config)` | ~532-546 | "Security Council minority" | warning | SC 少数派可强制出块（如 Starknet、Metis） |
| `PROPOSER_USE_ESCAPE_HATCH_ZK` | ~548-554 | "Use escape hatch" | good | 用户可凭 ZK proof 自助退出 |
| `PROPOSER_USE_ESCAPE_HATCH_MP` | ~556-562 | "Use escape hatch" | good | 用户可凭 Merkle proof 自助退出 |
| `PROPOSER_USE_ESCAPE_HATCH_MP_NFT` | ~564-570 | "Use escape hatch" | good | Merkle proof + NFT mint |
| `PROPOSER_USE_ESCAPE_HATCH_MP_AVGPRICE` | ~572-578 | "Use escape hatch" | good | Merkle proof + average price |
| `PROPOSER_SELF_PROPOSE_WHITELIST_DROPPED(delay)` | ~580-590 | "Self propose" | good | 白名单失活后任意人成为 proposer |
| `PROPOSER_SELF_PROPOSE_WHITELIST_DROPPED_ZK(delay)` | ~592-602 | "Self propose" | good | Kailua-style vanguard advantage drop |
| `PROPOSER_SELF_PROPOSE_WHITELIST_MAX_DELAY(delay)` | ~604-614 | "Self propose" | good | 任意人对老区块可 propose |
| `PROPOSER_SELF_PROPOSE_ZK` | ~616-621 | "Self propose" | good | source-available prover 任意人可提交 ZK proof |
| `PROPOSER_SELF_PROPOSE_ROOTS` | ~623-629 | "Self propose" | good | 任意人提交 root（Permissionless fraud proof） |
| `PROPOSER_POS(...)` | ~631-640 | "Cannot withdraw" | warning | PoS validator set（如 Polygon PoS） |

(c) **模板判定函数完整解读**：
- **opStack `getRiskViewProposerFailure`**（packages/config/src/templates/opStack.ts:1403-1442）：
  switch `fraudProofType` ∈ {None, Permissioned, Permissionless, Kailua, KailuaSoon, OpSuccinct, OpSuccinctFDP}：
  - `None` / `Permissioned` / `OpSuccinct` / `OpSuccinctFDP` → `PROPOSER_CANNOT_WITHDRAW`；
  - `Permissionless` / `KailuaSoon` → `PROPOSER_SELF_PROPOSE_ROOTS`；
  - `Kailua` → 根据 `vanguardAdvantage` 走 `PROPOSER_SELF_PROPOSE_WHITELIST_DROPPED_ZK` 或 `PROPOSER_CANNOT_WITHDRAW`；
- **`getFraudProofType`**（行 2360-2396）：通过 `OptimismPortal2.respectedGameType` 链上值映射
  （0=Permissionless, 1=Permissioned, 6=OpSuccinct, 1337=Kailua, 2000=KailuaSoon, 42=OpSuccinctFDP）；
- **orbitStack / zkStack / agglayer / nitro** 模板的对应判定函数也需简要列出，但作为对照（不深挖）。

> **Note**：Round 1 outline 中曾包含一条 `sumRisk`（"OP Stack 假设 6.5 年后 proposer 白名单失活"）声明，
> Round 2 已撤回——审阅认为该声明对应的代码行实际位于 `opStackL3` 的 stacked-risk 聚合，
> 而非一个独立的"6.5 年白名单失活"假设；`PROPOSER_SELF_PROPOSE_WHITELIST_DROPPED` 在那处只是 formatter。
> 该 claim 是否在 opStack.ts 内别处真实存在（具体 commit / 文件 / 行号），改由 open_questions 跟踪，
> 待 deep round 给出确切源码佐证后方可重新纳入 draft contract。

(d) **OpSuccinct 路径下 `PROPOSER_CANNOT_WITHDRAW` 的成因分析**：
- OpSuccinct 是 validity-proof 路径，按设计本应"任意人持有 prover 即可提 proof"；
- 但 L2Beat 当前判定为 "Cannot withdraw" 的原因（待 deep round 核验）：
  - OPSuccinctL2OutputOracle 合约中 `proposeL2Output` 函数是否有 proposer 白名单 modifier？
  - SP1Verifier / vkey 是否任意人可触发？
  - 是否缺少 "permissionless prover" 路径的官方注册（与 Forum #413 ZK Proving System 四子项要求的关系）；
- 此分析为 mantle-proposer-failure-analysis 下游 issue 提供问题树入口。

(e) **不满足时用户资产故障树（按 withdrawal 状态分桶，时间分辨率到具体阶段）**：
- 触发条件：proposer 私钥泄露/丢失/恶意停机 → state root 停止提交到 L1；
- **用户分桶 A：已在 proposer 停机前完成 `proveWithdrawalTransaction` 的 withdrawal**
  （即已针对一个**已存在的**有效 state root 调用过 proveWithdrawalTransaction）：
  - 这些 withdrawal 已经持有有效的 inclusion proof，**不会**因 proposer 停机而立即冻结；
  - 只需等待 challenge / finalization window（如 OpSuccinct 的 `finalizationPeriodSeconds`、
    OptimismPortal2 的 `proofMaturityDelaySeconds`）走完，即可调用
    `finalizeWithdrawalTransaction` 完成 L1 出款；
  - 故障树终态：**可正常退出**（红色判定不适用于这一桶）。
- **用户分桶 B：proposer 停机之后才发起 / 仅完成 `initiateWithdrawal`、尚未 prove 的 withdrawal**：
  - 后果链：
    1. L1 上 `OPSuccinctL2OutputOracle.l2Outputs` 不再追加新条目；
    2. 用户在 L2 已发起但未 prove 的 withdrawal 无法在停机后的任何旧 state root 中获得 inclusion
       proof（如其 L2 区块晚于最新已提交的 state root）；新发起的 withdrawal 同样无法 prove；
    3. `OptimismPortal.proveWithdrawalTransaction` 路径阻塞，进而无法到达
       `finalizeWithdrawalTransaction`；
    4. 这类用户的资产**等同于冻结**，依赖 governance 强制升级合约（替换 proposer / 强行注入 root）
       才能恢复；
  - 这是 L2Beat "Cannot withdraw" red 判定真正对应的群体。
- **红色判定的精确定义**：Proposer Failure red sentiment 衡量的是"**proposer 停机后**才需要 prove
  的 withdrawal 群体能否退出"，并非对所有 in-flight withdrawal 的全称否定。本研究在 deep round
  必须在故障树文本中保留 A/B 两桶的区分，避免下游 issue（mantle-proposer-failure-analysis 等）
  把"已 prove 但未 finalize"误归为冻结。
- 极端场景：若 governance 同样冻结（Exit Window = None 且 SC 失能），对**分桶 B** 的资产
  **永久无法提取**——这是 Proposer Failure × Exit Window 双红的最坏情形，必须在 item-3 中显式衔接。
  对**分桶 A**，最坏情形是 ProxyAdmin 在 finalization window 内升级 OptimismPortal 实现并拦截
  `finalizeWithdrawalTransaction`——但这是 Exit Window 维度的攻击，不是 Proposer Failure 本身的
  后果，归 item-3 讨论。

(f) **Open questions（待 deep round 源码核验）**：
- **Q-2.1（sumRisk / 6.5 年白名单失活假设）**：`opStack.ts` 中是否存在一条 hardcoded 的
  "6.5 年后 proposer 白名单失活" 假设，用于聚合 `PROPOSER_SELF_PROPOSE_WHITELIST_DROPPED`？
  若存在，具体在哪个 commit / 文件 / 行号？Round 1 outline 引用的"行 617-621"经审阅复核实际位于
  `opStackL3` 的 stacked-risk 聚合（仅在两层 sentiment 都非 bad 时合并 `orderHint` 延迟），
  `PROPOSER_SELF_PROPOSE_WHITELIST_DROPPED` 在那处只是 formatter，并不构成"6.5 年" 假设的 evidence。
  在 deep round 提供可验证的 commit + 文件 + 行号之前，**该假设不得**进入 draft contract、diag-2 或
  failure_consequences 字段。
- **Q-2.2（OpSuccinct → PROPOSER_CANNOT_WITHDRAW 的真实成因）**：(d) 段提出的待核验问题：
  OPSuccinctL2OutputOracle 是否带 proposer 白名单 modifier？SP1Verifier / vkey 是否任意人可触发？
  L2Beat 的"Cannot withdraw"判定的精确技术理由是否在 commit message / PR description / Forum
  讨论中有显式说明？

- **Priority**: high
- **Dependencies**: item-1

### item-3: Exit Window 指标完整解构（评估问题、计算公式、七类变体、影响分析）

逐项解构 Exit Window 指标的 L2Beat 评估口径，作为后续 mantle-exit-window-analysis（下游）的
评估框架。

(a) **L2Beat 对 Exit Window 的核心考察问题**：
- "非紧急合约升级发起后，用户在升级生效前是否有足够时间将 L2 资产提取到 L1？"
- 评估视角：合约可升级 → implementation 切换 → 用户提款路径可能被改写或冻结；
  Exit Window 度量"用户察觉升级并完成 L2-to-L1 提款"所需的最低时间余量；
- 评估的关键量：upgradeDelay（升级生效前的 timelock）与 exitDelay（用户从 L2 提款至 L1
  finality 所需时间）的差值。

(b) **基础 EXIT_WINDOW 函数完整解读**（packages/config/src/common/riskView.ts:642-687）：

```ts
export function EXIT_WINDOW(
  upgradeDelay: number,
  exitDelay: number,
  options: { upgradeDelay2?: number; existsBlocklist?: boolean } = {},
): TableReadyValue & { seconds?: number } {
  let window = upgradeDelay - exitDelay
  // options.upgradeDelay2 二次升级路径，取较小者
  // sentiment 阈值：< 7d = bad, < 30d = warning, ≥ 30d = good
  // window ≤ 0 → value = "None"
  // options.existsBlocklist → 显式标注用户可被 L1 blocklist 阻止提款
}
```

关键评估边界：
- **sentiment 阈值**：`< 7 day = bad / 7-30 day = warning / ≥ 30 day = good`（行 660-666）；
- **None 文案**：window ≤ 0 时显示 "None"；upgradeDelay = 0 时附加 "since contracts are instantly upgradable"；
- **upgradeDelay2**：若项目有两条独立升级路径（如 emergency + regular），取窗口较小者；
- **existsBlocklist**：若存在 L1 提款黑名单（如 ZKStack 的 TransactionFilterer），附加显式警告文本。

(c) **七类 EXIT_WINDOW 变体函数**（行 642-788）：

| 函数 | 行号 | 入参 | 适用场景 |
|---|---|---|---|
| `EXIT_WINDOW(upgradeDelay, exitDelay, options)` | 642-687 | upgradeDelay + exitDelay | 通用基础公式 |
| `EXIT_WINDOW_ZKSTACK(upgradeDelay)` | 689-704 | upgradeDelay only | ZKStack：central operator 可通过 TransactionFilterer 即时审查 |
| `EXIT_WINDOW_NITRO(l2Timelock, selfSeq, challenge, validatorAfk, l1Timelock, isPostBoLD)` | 706-739 | 复合 | Arbitrum Nitro：双层 timelock + challenge window + validator AFK |
| `EXIT_WINDOW_PERMISSIONLESS_BOLD(l2Timelock, selfSeq, l1Timelock)` | 741-757 | 双层 timelock + selfSeq | Arbitrum BoLD permissionless 路径 |
| `EXIT_WINDOW_NON_UPGRADABLE` | 759-765 | 无 | 不可升级合约（少数）"∞" |
| `EXIT_WINDOW_UNKNOWN` | 767-773 | 无 | 未验证合约 "Unknown" |
| `EXIT_WINDOW_STARKNET(upgradeDelay)` | 775-788 | upgradeDelay only | Starknet：SC minority 反应时间 1 day |

每类函数的"window 计算逻辑"与"warning 文案"必须列出，特别是 ZKStack 与 Starknet 的非对称
（emergency vs regular）规则。

(d) **模板判定函数完整解读**：
- **opStack `getRiskViewExitWindow`**（packages/config/src/templates/opStack.ts:1387-1401）：
  - 若 `hasSuperchainScUpgrades` 为 true → 直接返回 `{ value: 'None', sentiment: 'bad' }`，
    附加文案 "There is no exit window for users to exit in case of unwanted upgrades as they
    are initiated by the Security Council with instant upgrade power and without proper notice."；
  - 否则返回 `RISK_VIEW.EXIT_WINDOW(0, finalizationPeriod)`——upgradeDelay **hardcode 为 0**；
- **`getFinalizationPeriod`**（行 2249-2280）：按 fraud-proof 类型读取不同合约字段：
  - OpSuccinct → `OPSuccinctL2OutputOracle.finalizationPeriodSeconds`；
  - OpSuccinctFDP / Permissionless / Permissioned / Kailua → `OptimismPortal2.proofMaturityDelaySeconds`；
  - None → `L2OutputOracle.FINALIZATION_PERIOD_SECONDS`；
- **opStack 的关键假设**：upgradeDelay = 0 是默认假设；项目方若有真实 timelock（如 Optimism 主网 SC + Timelock），
  必须通过 `nonTemplateRiskView.exitWindow` 显式覆盖；否则即使链上有 timelock 配置，
  L2Beat 评级也会显示 "None"——这是后续 mantle-exit-window-analysis 必须验证的关键链路；
- **stackExitWindowRisk**（行 608-611）：opStack 还会与 baseChain 的 exitWindow 求 max 风险，
  适用 OP Superchain 子链；
- **orbitStack / zkStack** 中对应判定函数的简要对照。

(e) **不满足时用户资产故障树**：
- 触发条件：ProxyAdmin owner 发起恶意/瑕疵升级（如 implementation 切换、proposer registry 改写、
  vkey 替换）；
- 后果链：
  1. 链上升级 transaction 进入 mempool 或直接被打包（若 timelock = 0）；
  2. 用户从社交渠道察觉的延迟（典型 5-30 分钟）远小于 finalization period（OpSuccinct 默认 ≥1h）；
  3. 用户即使立即发起 L2 withdrawal，也无法在升级生效前完成 L2-to-L1 finality；
  4. 升级生效后：用户提款路径或被改写（implementation 中删除/拦截 finalizeWithdrawal）、
     或被冻结（pause）、或被重定向（implementation 把资金转走）；
- 与 Proposer Failure 双红的最坏情形：见 item-2 (e)。

- **Priority**: high
- **Dependencies**: item-1

### item-4: L2Beat 评估管线的数据来源、自动化程度与人工干预点

剖析 L2Beat 评估 Proposer Failure 与 Exit Window 时的数据流：从链上抓取到最终页面渲染的完整路径，
明确哪些字段自动、哪些人工配置、哪些可以通过链上参数变更即时反映。

(a) **数据流拓扑**：
- **链上层**：Etherscan / RPC → `ProjectDiscovery` 模块（packages/config/src/discovery/ProjectDiscovery.ts）
  调用 `getContractValue` / `getContract` 等方法抓取合约字段；
- **配置层**：每个项目 `packages/config/src/projects/{slug}/{slug}.ts` 文件 +
  `discovered.json` 快照（自动生成）+ `config.jsonc`（人工配置 discovery 规则）；
- **模板层**：`packages/config/src/templates/{opStack,orbitStack,zkStack,agglayer,nitro}.ts` 提供默认 riskView；
- **覆盖层**：`nonTemplateRiskView.{proposerFailure,exitWindow,...}` 显式覆盖（人工填写）；
- **聚合层**：`scaling.riskView` 字段写入 ScalingProject，进入 `@l2beat/config` 输出；
- **前端层**：`packages/frontend/src/server/features/scaling/project/getScalingRosetteValues.ts` 与
  `packages/frontend/src/pages/scaling/risk/components/table/columns.tsx` 渲染五边形/表格。

(b) **三层数据来源的优先级**：
- 优先级：`nonTemplateRiskView.*`（人工覆盖）> 模板判定函数 > 默认常量；
- 项目方如何影响评级：
  - 改变链上参数（如 Timelock.minDelay）→ 仅当 `nonTemplateRiskView.exitWindow` 已经从 discovery 取值
    才能反映；否则模板会继续返回 hardcode `EXIT_WINDOW(0, finalizationPeriod)`；
  - 提交 PR 到 l2beat/l2beat 仓库覆盖 `nonTemplateRiskView` 或修改 fraud-proof type 映射；
- L2Beat 团队的人工 review：对 PR 的合并把关 + 周期性 risk view audit。

(c) **自动 vs 人工字段对照表**（item-2 / item-3 两个指标分别给出）：

| 指标 | 字段 | 数据源 | 更新方式 |
|---|---|---|---|
| Proposer Failure | `fraudProofType` | OptimismPortal2.respectedGameType（discovery 自动） | 链上变更 → 自动反映 |
| Proposer Failure | OpSuccinct 路径 → CANNOT_WITHDRAW | 模板 hardcode | 需 PR 修改模板才能改变 |
| Exit Window | `finalizationPeriodSeconds` | OPSuccinctL2OutputOracle 链上（discovery 自动） | 链上变更 → 自动反映 |
| Exit Window | `upgradeDelay = 0`（hardcode） | opStack 模板 hardcode | 需 nonTemplateRiskView.exitWindow 覆盖 |
| Exit Window | `hasSuperchainScUpgrades` | 项目配置（人工） | 人工 PR |

(d) **discovered.json / diffHistory.md 的作用**：
- `discovered.json` 是 ProjectDiscovery 周期性抓取的快照，记录所有合约字段最新值；
- `diffHistory.md` 记录历史变更，对 audit 与争议 trail 有重要价值；
- 本 item 必须列出 Mantle 项目（packages/config/src/projects/mantle/）下这两个文件的当前状态作为参照。

(e) **争议与边界 cases**：
- 若链上参数变更但模板未更新，是否会出现"评级滞后"现象？（实际案例：OP Stack 项目升级到 FaultProof
  但模板未及时切 fraudProofType 映射的情况）；
- 项目方与 L2Beat 团队的争议处理流程（Forum 帖、Discord 沟通、L2Beat Stages 评估争议）。

- **Priority**: medium
- **Dependencies**: item-2, item-3

### item-5: 典型项目评级对比（OR vs ZK Validity vs ZK ZKSync 三类对照）

选取 5-7 个代表项目，逐项对照 Proposer Failure + Exit Window 的评级、对应 RISK_VIEW 常量、对应模板函数与
差异化原因，输出一张可复制的"评级提升路径分类表"。

(a) **对照项目集**（建议覆盖三类典型）：
- **OP Stack + OpSuccinct (validity-proof)**：Mantle（本研究的目标，但仅作 baseline 引用，不深入分析）；
- **OP Stack Permissionless (fault-proof)**：Optimism Mainnet（current FP rollout 状态）、Base（current 状态）；
- **Orbit/Nitro Permissionless**：Arbitrum One BoLD；
- **ZKStack**：zkSync Era；
- **Starknet**：单独类别（SC minority 强制出块路径，与上述均不同）；
- 可选：Polygon zkEVM、Linea、Scroll（如 deep round 容量允许）。

(b) **对比矩阵字段**：

| 项目 | Stack | Fraud Proof Type | Proposer Failure 文案 | Proposer Failure 常量 | Exit Window 文案 | Exit Window 公式入参 | 关键差异化因素 |
|---|---|---|---|---|---|---|---|

(c) **差异化因素的归类**：
- **Proposer Failure 差异化驱动**：
  - 是否存在 permissionless prover 路径（OpSuccinct ❌ / Arbitrum BoLD ✅ / zkSync ✅ via escape hatch）；
  - 是否存在 governance/SC fallback（Optimism ✅ / Starknet ✅ minority / Mantle ❌）；
  - 白名单失活机制：Kailua `vanguardAdvantage` drop（已有源码路径，见 item-2(c)）；
    OP Stack 中是否存在独立的"X 年后白名单失活"机制待 deep round 源码核验（见 open_question Q-2.1），
    **不得**在对比矩阵中写入未经核实的 "6.5 年假设"；
- **Exit Window 差异化驱动**：
  - 是否人工配置 `nonTemplateRiskView.exitWindow`（Optimism ✅ / Mantle ❌ 默认走 hardcode 0）；
  - L1/L2 timelock 实际配置（Arbitrum 17d 8h / Optimism 7d / Mantle ~1d）；
  - SC instant-upgrade 权限是否独立于 timelock（Base nested 2/2 / Optimism Superchain SC / Mantle 无独立 SC）；
  - TransactionFilterer 等 censorship vector（ZKStack 存在 / OP Stack 不存在）。

(d) **可复制的"评级提升路径"分类**（仅作框架描述，**不**给出 Mantle 具体改进方案）：
- **路径 A：引入 permissionless prover/proposer** → Proposer Failure 从 red 升级至 good
  （如从 OpSuccinct → OpSuccinct + permissionless prover registry）；
- **路径 B：配置 ≥7d upgradeDelay + 通过 nonTemplateRiskView 覆盖** → Exit Window 从 red 升级至 warning/good
  （如部署 L1 Timelock + 提交 L2Beat PR 显式声明）；
- **路径 C：部署 escape hatch（ZK proof / Merkle proof）** → Proposer Failure 直接 bypass，
  适用 ZKStack/StarkEx 类项目；
- **路径 D：引入 Security Council + minority 强制出块路径** → Proposer Failure 从 red 升级至 warning
  （Starknet 模式）；
- 每条路径列出：触发评级变化的关键合约/链上参数、需要的 L2Beat 配置变更、潜在副作用。

(e) **与下游 issue 及历史上游 final 的接口**：
- **stage1-roadmap-recommendation 历史 final 仅作为可选 pointer note**：该 final 属于 Stage 框架范畴，
  与本研究 Risk Chart sentiment 判定体系无直接关系；若 deep round 需要在某条"评级提升路径"旁补充
  Stage 体系的背景脚注，可以 pointer note 形式（"参见 stage1-roadmap-recommendation final"）引用，
  **不得**将该 final 的结论作为 Risk Chart 路径定义依据；
- 显式标注路径 A/B/C/D 与 mantle-proposer-failure-analysis、mantle-exit-window-analysis、
  recommendation-proposal 三个下游 issue 的对接点（此为本 item 的主要 downstream handoff）。

- **Priority**: medium
- **Dependencies**: item-2, item-3, item-4

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| l2beat_definition | L2Beat 对该指标"考察的核心问题"原文与出处（仓库文件 + 行号 / 官方文档 URL / Forum 帖 URL）；必须直接引用，禁止改写 | item-2, item-3 |
| risk_view_constants | 该指标在 packages/config/src/common/riskView.ts 中定义的所有相关常量与函数的完整枚举（常量名、value、sentiment、行号、典型场景） | item-2, item-3 |
| template_logic | 各模板（opStack、orbitStack、zkStack、agglayer、nitro）中对应判定函数的伪代码或精确源码引用（含行号、commit hash） | item-2, item-3 |
| evaluation_formula | 指标计算公式（如 Exit Window 的 `window = upgradeDelay - exitDelay`）与 sentiment 阈值表 | item-3 |
| data_sources | 该指标数据的来源（自动 discovery / 人工 nonTemplateRiskView / 模板 hardcode），含合约字段名、文件位置、更新方式 | item-2, item-3, item-4 |
| failure_consequences | 不满足判定（red sentiment）下用户资产的故障树：触发条件、后果链（步骤化）、最坏情况；必须**只论述用户资产层面的影响**，不混入治理/合规层面 | item-2, item-3 |
| applicable_rollup_type | 指标/子项适用的 rollup 类型：`all` / `optimistic-only` / `zk-validity-only` / `zksync-only` / `starknet-only`；用于显式标注模板适用边界 | item-2, item-3, item-5 |
| project_comparison | 典型项目在该指标上的评级与差异化原因（含 fraud-proof type、timelock 配置、SC 配置） | item-5 |
| upstream_reference | 引用上游 final/draft 的精确链接与章节；l2beat-stage-framework-2026 final 仅作**可选背景脚注**，其 Stage 1 阈值（Exit Window ≥5d、SC 少数派要求等）**不得**被用作本研究 Risk Chart sentiment 判定依据；其他 final-or-latest-draft 仅当本研究需要 evidence 链接时引用 | item-2, item-3, item-5 |
| downstream_handoff | 与下游 issue（mantle-proposer-failure-analysis、mantle-exit-window-analysis、recommendation-proposal）的接口：本研究输出哪些"事实基线"与"评估口径"供下游使用 | all |
| evidence_sources | 一手来源链接清单：l2beat/l2beat 仓库 commit hash 永久链接（packages/config 源码 + packages/frontend 渲染层）、L2Beat 项目页快照、官方 docs、Forum 帖、上游 final | all |
| open_questions | 当前公开材料中未明确、需要在 deep round 进一步链上核验或团队访谈确认的问题（如：OpSuccinct 路径下 PROPOSER_CANNOT_WITHDRAW 的精确技术理由是否在 commit message / PR description 中有解释） | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy | L2Beat Risk Chart 五维总览二维位置图：横轴=运行/活性 vs 治理/升级，纵轴=数据/状态 vs 用户提款；五项指标（Sequencer Failure、State Validation、Data Availability、Exit Window、Proposer Failure）按位置标注；显式标注 Proposer Failure 与 Exit Window 的交集区（"用户提款全冻"双红极端情形），其他三项以浅色作 context | mermaid | item-1 |
| diag-2 | flow | Proposer Failure 判定流程图：以 `OptimismPortal2.respectedGameType` 为根节点，沿 `getFraudProofType` 的 switch case 展开（0/1/6/42/1337/2000），每个分支汇入对应 `RISK_VIEW.PROPOSER_*` 常量；显式标注 OpSuccinct (6) → PROPOSER_CANNOT_WITHDRAW 路径，并在分支末端附 sentiment 颜色（good/warning/bad）。**禁止**在本图旁注未经源码核实的 sumRisk / WHITELIST_DROPPED 聚合层；若 deep round 在 opStack.ts 中找到经核实的 sumRisk / opStackL3 聚合路径，方可作为补充分支加入，且必须附 commit + 行号 | mermaid | item-2 |
| diag-3 | flow | Exit Window 计算逻辑图：upgradeDelay (timelock minDelay) ↔ exitDelay (finalization period / challenge window / force-inclusion delay) → window = max(0, upgradeDelay - exitDelay) → sentiment 阈值切片（<7d=bad / 7-30d=warning / ≥30d=good / window≤0=None）；显式标注 opStack 模板的 `upgradeDelay = 0` hardcode 分支与 hasSuperchainScUpgrades 直返分支；旁注七类 EXIT_WINDOW 变体（基础、ZKStack、Nitro、PermissionlessBoLD、NonUpgradable、Unknown、Starknet）的入参对照 | mermaid | item-3 |
| diag-4 | architecture | L2Beat 评估管线数据流拓扑：链上(Etherscan/RPC) → ProjectDiscovery → discovered.json → 模板默认 → nonTemplateRiskView 覆盖 → ScalingProject.riskView → frontend 渲染；每层节点旁标注涉及文件路径（如 packages/config/src/templates/opStack.ts、packages/frontend/src/server/features/scaling/project/getScalingRosetteValues.ts）；显式标注"自动 vs 人工"字段（Proposer Failure 自动 discovery + 模板 hardcode；Exit Window 多数项目需 nonTemplateRiskView 人工覆盖） | mermaid | item-4 |
| diag-5 | comparison | 典型项目 Proposer Failure × Exit Window 评级对照矩阵：行=项目（Mantle / Optimism / Base / Arbitrum BoLD / zkSync Era / Starknet），列=两个指标 + 差异化驱动因素（fraud-proof type、permissionless prover 是否就绪、L1 timelock 实际值、SC 配置、escape hatch 是否存在）；单元格用 sentiment 颜色码（red/yellow/green）标注，并附常量名 | mermaid | item-5 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | l2beat/l2beat 仓库 packages/config/src/common/riskView.ts（PROPOSER_* 与 EXIT_WINDOW_* 常量/函数完整定义）；必须给出 commit hash 永久链接 + 行号锚定 | 1 |
| src-2 | code_analysis | l2beat/l2beat 仓库 packages/config/src/templates/opStack.ts（getRiskViewProposerFailure、getRiskViewExitWindow、getFraudProofType、getFinalizationPeriod、stackExitWindowRisk、sumRisk）；必须含 commit hash + 行号；建议同时给出 orbitStack / zkStack 等模板的对应函数作 context | 2 |
| src-3 | code_analysis | l2beat/l2beat 仓库 packages/config/src/projects/mantle/{mantle.ts, discovered.json, config.jsonc, diffHistory.md}：作为 item-4 数据源拓扑的实证锚点（仅引用，不深入分析 Mantle，本研究边界严格遵守） | 1 |
| src-4 | code_analysis | l2beat/l2beat 仓库 packages/frontend/src 中 Risk Chart 渲染相关文件：getScalingRosetteValues.ts、scaling/risk/components/table/columns.tsx、rosette/individual/IndividualRosetteIcon.tsx | 1 |
| src-5 | official_docs | L2Beat 官方网站 Mantle 项目页 (https://l2beat.com/scaling/projects/mantle#risk-analysis) 当前快照；L2Beat Stages 文档；L2Beat Risk Analysis methodology 页（若存在）；必须含访问日期 + 截图 / archived URL | 3 |
| src-6 | governance_proposals | L2Beat Forum 关于评估方法的一手帖子（涉及 risk-view 标准更新的讨论帖、与 Proposer/Exit Window 直接相关的提案）；至少包括 Forum 上关于 Proposer Failure 与 Exit Window 评估口径变更的最近 1-2 年帖子 | 2 |
| src-7 | optional_context | l2beat-stage-framework-2026 final 仅作为**可选背景脚注**，**禁止**用其 Stage 1 阈值（Exit Window ≥5d、SC 少数派要求等）来定义本研究 Risk Chart sentiment——两者属于不同评估体系。仅当某项对比需要 Stage 体系作为背景说明时，方可以脚注形式引用，并显式声明"该阈值不参与 Risk Chart sentiment 判定"。无强制引用要求。 | 0 |
| src-8 | code_analysis | 对比项目源码：l2beat/l2beat 仓库 packages/config/src/projects/{optimism,base,arbitrum,zksync2,starknet}/ 至少 3 个项目的 .ts 配置文件，作为 item-5 项目对比的实证；优先取每个项目 nonTemplateRiskView 的 Exit Window/Proposer Failure 覆盖代码。**注**：ZKsync Era 的 L2Beat 配置目录名为 `zksync2`（页面 slug 为 `zksync-era`），勿混淆 | 3 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | revise | item-2(c), item-2(e), item-2(f-new open_questions), item-5(e), scope, src-7, src-8, diag-2 | Review Round 1: Stage scope leak（src-7/scope/item-5(e) 降级为可选 context，禁止 Stage 阈值定义 Risk Chart sentiment）；sumRisk "6.5 年"代码路径未经源码核实（item-2(c) 撤回 claim、diag-2 删除聚合层旁注、新增 open_questions Q-2.1 跟踪源码核验）；stale zksync 路径（src-8 zksync-era → zksync2）；imprecise failure tree（item-2(e) 拆分为已 prove vs 未 prove 双桶，精确定义 red sentiment 所对应群体） | Research Review Agent verdict comment b39ff472 |
| 3 | revise | item-1(b), upstream_reference field, item-5(c) | Review Round 2: item-1(b) 仍包含 "本研究直接引用" Stage 框架语言，重新引入 round-1 scope leak——改为可选 pointer note 语言，并增加禁止 Stage 阈值定义 Risk Chart sentiment 的显式声明；upstream_reference 字段仍将 l2beat-stage-framework-2026 final 描述为 "Exit Window ≥5d / SC 阈值的权威来源"——改为可选背景脚注，禁止作为判定依据；item-5(c) 仍保留已撤回的 "OP Stack 6.5 年假设"——删除该断言，改为引用 open_question Q-2.1 跟踪源码核验，仅保留 Kailua vanguardAdvantage drop 作为已有源码路径 | Research Review Agent verdict comment a00ae161 |
