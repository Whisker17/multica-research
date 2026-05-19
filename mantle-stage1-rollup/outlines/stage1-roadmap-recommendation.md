---
topic: "Mantle Stage 1 路线图综合建议"
project_slug: mantle-stage1-rollup
topic_slug: stage1-roadmap-recommendation
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: mantle-stage1-rollup/outlines/stage1-roadmap-recommendation.md
  draft: mantle-stage1-rollup/research-sections/stage1-roadmap-recommendation/drafts/round-{n}.md
  final: mantle-stage1-rollup/research-sections/stage1-roadmap-recommendation/final.md
  index: mantle-stage1-rollup/research-sections/_index.md

scope: |
  本课题是 Mantle Stage 1 研究项目的**综合 / 收尾课题**（order=6），上游严格依赖另外 5 个已完成的
  final sections：

    1. `l2beat-stage-framework-2026/final.md` (WHI-39) —— L2Beat 2026 版 Stage 框架的事实基线
       （三阶段定位、Exit Window 三轨规则、Walkaway Test、L2 Proving System 5a-5d 子项 applicability
       与 grace period、Forum #425 OR challenge period 5d 调整）；
    2. `mantle-architecture-2026/final.md` (WHI-40) —— Mantle 当前合约拓扑、三路径治理、OP Succinct
       v2.0.1 部署事实、L2Beat 项目页快照（2 CRITICAL + 6 HIGH + 1 MEDIUM 风险）；
    3. `stage1-case-studies/final.md` (WHI-41) —— Arbitrum / OP Mainnet / Base / Starknet / Scroll
       五个 Stage 1 案例的 walkaway × proving-system 双维度评估，含可借鉴样板与反模式；
    4. `upgrade-exitwindow-securitycouncil/final.md` (WHI-42) —— 升级机制 / Exit Window /
       Security Council 三位一体设计方案（含 GuardedExecutor + TargetSelectorWhitelist +
       PauseTimelock 三新合约 + 双 Timelock + 9-12 人 SC + 4 阶段过渡）；
    5. `proposer-decentralization-zk-compliance/final.md` (WHI-43) —— Proposer liveness 与 ZK
       proving system (5a-5d) 透明度 gap 评估，含 v2.0.1 → v3.0.0-rc.1 升级路径与 SP1 reproducibility
       验证流程。

  本课题**不重新评估上游事实**，而是把上游 5 个 final sections 的结论综合为一份可执行的
  Stage 1 升级路线图。研究范围严格限定在以下七个维度：

  (1) **统一 Gap 清单与优先级评分**：把 5 个 final sections 中分散提出的 Stage 1 阻断项（含
      Exit Window、Security Council、Walkaway Test、Proposer liveness、L2 Proving System 5a-5d、
      新合约审计、治理隔离等）统一收敛为一份**带 ID 的 Master Gap List**；为每项 Gap 给出
      （a）CRITICAL / HIGH / MEDIUM 分级与依据、（b）优先级评分（紧急度 × 重要度二维），
      （c）上游 final section 锚定引用（含 §section 与具体段落 anchor），（d）阻塞 Stage 1 与否
      的二元判定（hard blocker / soft prerequisite / non-blocking improvement）。

  (2) **升级依赖关系图与可并行性分析**：基于（1）的 Master Gap List，绘制 Stage 1 各项升级
      之间的**有向依赖图**（DAG）。显式标注：(i) 硬性前置（如 v3.0.0-rc.1 部署是 fallbackTimeout
      生效的硬前置）、(ii) 软性前置（如 GuardedExecutor 审计应在 SC 上线前完成但二者可平行
      推进）、(iii) 可完全并行项（如 (5a-5d) 程序透明度披露与 SC 组建无依赖）、(iv) 串行约束
      （如 Walkaway Test 模拟必须在所有合约部署完成之后）。基于依赖图给出**最优升级顺序**
      与可并行批次划分。

  (3) **分阶段里程碑时间线建议**：把 (1) Master Gap List 与 (2) 依赖图映射到一份**4 阶段
      时间线**（与上游 `upgrade-exitwindow-securitycouncil` final §Item-2 的 4 阶段过渡对齐：
      阶段 0 当前 → 阶段 1 合约部署 + SC 组建 → 阶段 2 Walkaway 模拟 + L2Beat 评估 → 阶段 3
      Stage 1 完整态；远期阶段 4 预留 Stage 2 路径）。每个阶段必须给出：(a) 预计工程时长
      （周 / 月级粒度，考虑审计 + 治理流程）、(b) 关键交付物（合约部署清单、参数变更 tx 列表、
      文档与脚本）、(c) 上下游依赖触发条件、(d) 退出准则（exit criteria）—— 进入下阶段
      的可观测信号。**特别说明**：grace period 硬截止（Forum #413 推算约 2026-08-16）与
      Walkaway Test enforcement_status 演进对时间线的硬约束。

  (4) **多维度风险评估矩阵**：按四象限（技术风险 × 运营风险 × 治理风险 × 外部依赖风险）
      系统列出 Stage 1 升级路径的风险条目，每项给出（a）likelihood（low / medium / high）、
      （b）impact（low / medium / high / critical）、（c）heat 评分（likelihood × impact）、
      （d）触发条件 / 早期信号、（e）缓解措施与责任方、（f）残余风险评估。**禁止**把上游
      已识别的风险简单复制，必须做一次**跨维度交叉相互作用分析**（如：SC 组建延迟 ×
      grace period 倒计时 → 复合外部依赖风险）。

  (5) **审计与验证计划**：基于（1）（2）（3）输出一份**分批次审计计划**：
      (a) Tier-A 必审清单（GuardedExecutor / TargetSelectorWhitelist / PauseTimelock 三新合约，
          v3.0.0-rc.1 OPSuccinctL2OutputOracle 升级，OptimismPortal v1.7.0 → 上游 ≥v1.8.x 升级——
          上游版本号需在 draft 阶段确认）、(b) Tier-B 选审清单（DA 路径变更后的 batcher /
          BatchInbox 配置，proposer key rotation 流程，SP1 verifier route freeze 应急脚本）、
          (c) Tier-C 自查清单（SC 成员身份公开、外部比例、签名设备运维）。每项给出建议审计
          范围（differential / full / focused）、预计周期（基于 OpenZeppelin / Cantina / Sigma Prime /
          Trail of Bits 等公开审计 cadence 参考——这些数据为 secondary 引用）、推荐审计方
          类型（不指定具体公司）。同时给出 L2Beat reproducibility re-verification 的协作
      请求计划（与 L2Beat 评级团队联系窗口、SP1 ELF + toolchain pin 公告需求）。

  (6) **OP Stack 上游协调策略**：识别哪些升级可以 leverage OP Stack 上游进度（如 OptimismPortal
      auto-expiring pause 实现路径 1 vs 路径 2、OP Mainnet 10/13 SC 经验、Base nested ProxyAdminOwner
      模式），哪些必须 Mantle 自研（如三新合约 GuardedExecutor 体系、Mantle 特有的三路径治理隔离）。
      给出与 OP Stack maintainer 协调的具体接触点（OP Stack governance forum / Pull Request 路径）
      与 fork-vs-PR 决策树。

  (7) **可执行 Action Items 清单**：把（1）-（6）的所有结论收敛为一份**带 owner / due date /
      可观测交付物**的扁平 Action Items 清单。Owner 维度遵循"职责类型"而不指定具体姓名（如
      "Mantle 协议工程师"、"治理 / DAO 协调"、"安全审计协调"、"L2Beat 评估窗口对接人"），
      因为本研究不应越权指定具体人员。每个 Action Item 标注（a）所属 Gap ID 与里程碑、
      （b）前置依赖、（c）可观测的完成信号（链上 tx / forum 帖 / 审计报告 commit / L2Beat
      项目页文本变化等）。

  **关键边界**：
  - 本研究**不重新**评估 L2Beat 框架要素本身（由 `l2beat-stage-framework-2026` 提供）；
  - **不重新**评估 Mantle 合约现状（由 `mantle-architecture-2026` 提供）；
  - **不重新**评估其他 L2 案例（由 `stage1-case-studies` 提供）；
  - **不重新**设计 SC / Exit Window 架构细节（由 `upgrade-exitwindow-securitycouncil` 提供）；
  - **不重新**评估 proposer / ZK 透明度细节（由 `proposer-decentralization-zk-compliance` 提供）；
  - **不指定**具体工程排期、不分配具体人力、不替代 Mantle 内部项目管理；
  - **不规划** Stage 2 路径（只在远期里程碑中预留兼容性，远期细节超出本研究范围）；
  - **不**为 Mantle 团队代写治理提案文本（仅给出建议条目与所需要素）；
  - **不**对未识别的"潜在 L2Beat 框架未来变更"做投机预测，但需评估**已公开**的可能变更
      （如 Walkaway Test enforcement 进入 enforced 状态、grace period 过期、Forum 中已讨论
      但未通过的提案）对 Mantle 时间线的影响。

  本研究的**所有结论必须可回溯到上游 5 个 final sections 的具体段落或 frontmatter 字段**，
  使用上游 final 的 commit SHA 或 §section anchor 作为 evidence；上游已闭合的 Gap 不在本研究
  重新展开，上游标记为 Open 或 future-work 的 Gap 才在路线图中给出推进路径。

audience: |
  - **Mantle 协议工程团队**（合约升级、proposer / verifier 运维、Security Council 组建的
    直接执行者）—— 本研究的主受众，需要一份能直接转化为内部 sprint 计划的可执行路线图。
  - **Mantle 治理 / DAO 协调团队**（治理提案撰写、SC 成员招募与公开度披露的负责者）——
    需要清晰的治理依赖与决策节点。
  - **Mantle 安全审计协调团队**（与外部审计方对接的负责者）—— 需要分批次审计计划与时间窗口。
  - **L2Beat 评估方与生态合作伙伴**（关注 Mantle Stage 1 升级路径合规性的 community
    stakeholders）—— 需要清晰的可观测里程碑与 evidence 锚定。
  - **OP Stack 生态合作者**（与上游 OP Mainnet / Base / Ink 等 maintainer）—— 需要识别
    Mantle 在 Stage 1 路径上对 OP Stack 升级的依赖与协调点。
  - **Multica 研究 squad 内部 Technical Writer Agent**（aggregate final-report 时的下游）——
    需要清晰的综合结论与可引用的核心数据点。

  阅读者熟悉 EVM 合约升级模式（Proxy / Implementation / ProxyAdmin / TimelockController）、
  multisig（Gnosis Safe）、OP Stack 基础架构（OptimismPortal / SystemConfig）、ZK validity proof
  概念（OP Succinct / SP1 / PLONK / Groth16），并已阅读 / 至少索引过本项目前 5 个 final
  sections（本路线图大量引用其结论与 commit SHA，不重复复述事实基线）。

expected_output: |
  **Final section 结构**（持久化在 `mantle-stage1-rollup/research-sections/stage1-roadmap-recommendation/final.md`）：

  - **§0 Executive Summary**：2-3 段，覆盖（a）当前 Mantle 距离 Stage 1 的总体距离一句话，
    （b）关键阻断项数量与最严重项，（c）推荐总体路径（"递进 + 并行 + 审计前置"或类似一句话
    战略表述），（d）grace period / Walkaway enforcement 等硬时间约束。

  - **§Item-1 Master Gap List 与优先级评分体系**：
    (a) 一张**统一 Gap 清单表**：列 = `[Gap ID, 维度, 上游 section 锚定, 当前状态, Stage 1 要求,
        Severity (CRITICAL/HIGH/MEDIUM), Stage 1 Hard Blocker (yes/no), 紧急度 1-5, 重要度 1-5,
        优先级得分]`；至少覆盖以下 8 个核心维度：(i) outside-SC upgrade exit window ≥5d，
        (ii) Security Council 量化阈值 (≥8 成员 / >75% threshold / ≥50% external)，
        (iii) Walkaway Test 合规（含 auto-expiring pause + permissionless prover + 不依赖 SC
        的 forced withdrawal 路径），(iv) Proposer liveness（v3.0.0-rc.1 + fallbackTimeout），
        (v) L2 Proving System 5a-5d 透明度（与 L2Beat 协作 reproducibility re-verification），
        (vi) 三路径治理隔离（core rollup / MNT TimelockController / mETH），(vii) 新合约审计
        （GuardedExecutor / TargetSelectorWhitelist / PauseTimelock），(viii) Sequencer 去中心化
        与 force-inclusion 6h 优化（Stage 1 边界可接受但属改进项）。
    (b) **评分方法说明与预定权重表**（draft 阶段可调整权重，但须附理由并重跑敏感性检查）：

        **紧急度（U，1-5）子项**：

        | 子项 | 取值尺度 | 默认权重 |
        |------|----------|----------|
        | U1 Grace-period 距离 | 3 = 剩余 <4 周；2 = 4-12 周；1 = >12 周 | 0.40 |
        | U2 L2Beat 项目页文本严重性 | 3 = CRITICAL；2 = HIGH；1 = MEDIUM / 无标注 | 0.35 |
        | U3 受影响 TVS 路径 | 3 = >$1B；2 = $100M-1B；1 = <$100M | 0.25 |

        U（raw）= 0.40×U1 + 0.35×U2 + 0.25×U3（range 1.00-3.00）
        U（1-5）= round((U_raw - 1.0) / 2.0 × 4 + 1)，min=1，max=5

        **重要度（I，1-5）子项**：

        | 子项 | 取值尺度 | 默认权重 |
        |------|----------|----------|
        | I1 Stage 1 hard blocker | 3 = yes；1 = no | 0.45 |
        | I2 DAG 出边数（依赖该项的 Gap 数量） | 3 = ≥3；2 = 1-2；1 = 0 | 0.30 |
        | I3 Walkaway-FAIL 影响 | 3 = 直接触发 FAIL；1 = 无直接影响 | 0.25 |

        I（raw）= 0.45×I1 + 0.30×I2 + 0.25×I3（range 1.00-3.00）
        I（1-5）= round((I_raw - 1.0) / 2.0 × 4 + 1)，min=1，max=5

        **优先级得分** P = U × I（range 1-25）

        **象限分配**：P1 = U≥4 且 I≥4；P2 = P≥9 且不满足 P1；P3 = 4≤P≤8；P4 = P<4

        **平分优先顺序（Tie-breaker，依次适用）**：
        (1) Severity 等级（CRITICAL > HIGH > MEDIUM）；
        (2) DAG 出边数（下游依赖更多者优先）；
        (3) 里程碑阶段（阶段 1 优先于阶段 2/3）。

        **敏感性检查要求**：若任意默认权重 ±0.10 变动导致某 Gap 的象限归属改变（P1↔P2 或
        P2↔P3），该 Gap 须在 §Gap Analysis 中标注为"评分敏感"并给出说明。draft 阶段如调整
        权重，须列出调整前后所有受影响 Gap 的象限变化表。

        每条 Gap 附 2-3 句**评分依据短文**，记录 U1/U2/U3 与 I1/I2/I3 的取值来源（锚定上游
        final §section），避免数字漂移。

  - **§Item-2 升级依赖关系图与可并行性分析**：
    (a) **diag-1 Stage 1 升级依赖关系图（mermaid graph LR）**：节点为 Master Gap List 中的每项
        升级，边为"hard prerequisite"或"soft prerequisite"；显式区分两类边的样式。
    (b) **批次划分**：基于依赖图给出 3-4 个 parallel batches（如 Batch A：v3.0.0-rc.1 升级 +
        fallbackTimeout 上线；Batch B：SC 组建 + GuardedExecutor 审计；Batch C：(5a-5d)
        reproducibility re-verification；Batch D：Walkaway 端到端模拟）。
    (c) **最优升级顺序**：明确 critical path（如果 Walkaway 模拟需要所有合约就绪，则关键路径
        = Batch A → (Batch B 并行 Batch C) → Batch D）。
    (d) **关键路径长度估算**：基于上游已有审计周期参考（如 OpenZeppelin 平均 3-6 周
        per audit）给出 critical path 的最短 / 最长估算（区间，不给单点估值）。

  - **§Item-3 分阶段里程碑时间线建议**：
    (a) **diag-2 分阶段里程碑甘特图（mermaid gantt）**：4 阶段（与上游 §Item-2 4 阶段过渡对齐）
        × 关键交付物 × 时间窗口（**周 / 月级别相对时间，从 T0 = "本路线图采纳日"起算，不绑定
        具体日历日期，避免与 Mantle 内部排期冲突**）。
    (b) **每个阶段的退出准则表**：列 = `[阶段, 退出准则, 可观测信号, 上游依赖, 失败回退路径]`。
    (c) **grace period 硬约束分析**：把 Forum #413 推算 grace cliff（≈ 2026-08-16，已在上游
        §item-2 标 G-8 为推算 estimate）作为外部时钟，叠加到 Mantle 内部时间线，明确"若
        T0 落在哪个时间点之前才能保证 reproducibility 在 grace period 内被 L2Beat 团队
        re-verify"。**特别说明** grace cliff 的不确定性来源（researcher-derived，不是
        L2Beat 官方 announcement）。
    (d) **关键决策点**：标注 3-5 个里程碑级 go/no-go 决策点（如：阶段 1 完成审计后是否进入
        阶段 2 公开 SC 组建；阶段 2 Walkaway 模拟失败如何回滚等）。

  - **§Item-4 多维度风险评估矩阵**：
    (a) **diag-3 风险矩阵热力图（mermaid quadrant 或带颜色的表格 + 注释文本）**：维度 = `技术 ×
        运营 × 治理 × 外部依赖`；每个象限至少 3 条风险条目。
    (b) **风险条目详表**：列 = `[Risk ID, 类别, Likelihood, Impact, Heat (= Likelihood × Impact),
        触发条件 / 早期信号, 缓解措施, 责任方类型, 残余风险]`。
    (c) **跨维度复合风险分析**：至少 3 个跨维度交互场景（如 "SC 组建延迟（治理）+ grace period
        临近过期（外部）→ 框架强制 enforcement 触发 Stage 0 降级"）。
    (d) **diag-4 升级优先级四象限图（mermaid quadrant，紧急度 × 重要度）**：把 §Item-1 Master Gap
        List 的每项映射到 P1-P4 四象限，给出每个象限的处置策略（P1 = 立即启动，P2 = 计划启动，
        P3 = 监控，P4 = 暂缓）。

  - **§Item-5 审计与验证计划**：
    (a) **Tier-A / Tier-B / Tier-C 审计清单**（结构见 scope §5），每项给出审计类型 / 范围 /
        预计周期区间 / 推荐审计方类型。
    (b) **L2Beat reproducibility re-verification 协作请求**：列出与 L2Beat 评级团队的协作步骤
        （SP1 toolchain pin 公告 → reproducibility script 公开 → L2Beat re-run → 项目页文本更新），
        每步附"建议时间窗"与"可观测交付物"。
    (c) **OP Stack 上游审计协调**：识别哪些升级（如 OptimismPortal auto-expiring pause）需要
        关注 OP Stack 上游审计进度，给出与 OP Stack maintainer 同步的接触点（forum / governance
        提案 / OP Labs / Optimism Foundation 的公开沟通渠道——不点名个人）。

  - **§Item-6 OP Stack 上游协调策略**：
    (a) **leverage vs 自研决策树**：基于上游每项升级的 "Mantle 必须自研 / OP Stack 已有 / OP Stack
        即将有" 三态，给出一份**决策表**。
    (b) **PR / Fork 推荐**：对 OP Stack 即将有但 Mantle 时间表更紧的项（如 OptimismPortal
        auto-expiring pause），给出"等待上游 vs 维护 fork vs 提交 upstream PR"的决策建议
        与 trade-off 分析。
    (c) **OP Mainnet 2024-08 rollback 经验沉淀**：把 stage1-case-studies §item-3 的 OP Mainnet
        2024-08-16 Cannon bug rollback 经验作为 Stage 1 上线后的 incident response playbook
        参考点（具体 playbook 由 Mantle 内部撰写，本研究只提供借鉴维度）。

  - **§Item-7 可执行 Action Items 清单**：
    (a) **扁平 Action Items 表**：列 = `[AI ID, Action 描述, 所属 Gap ID, 所属里程碑, 前置依赖
        (AI IDs), Owner 职责类型, 可观测交付物, 是否阻塞 Stage 1]`；按所属里程碑分组排序。
    (b) **Owner 职责类型分类**：（i）Mantle 协议工程，（ii）Mantle 治理 / DAO，（iii）Mantle
        安全审计协调，（iv）Mantle 社区 / 沟通，（v）L2Beat 评估对接人，（vi）OP Stack 上游
        协调人，（vii）外部审计方。**禁止指定具体姓名**。
    (c) **可观测交付物示例**：链上 tx 类（如 "TimelockController.updateDelay calldata 已通过 SC
        签名"）、forum 帖类（如 "Mantle DAO 治理提案 #N 已通过"）、git commit 类（如
        "GuardedExecutor 审计报告已 merge 到 mantle-xyz/op-succinct main"）、L2Beat 项目页
        文本类（如 "L2Beat Mantle 项目页 stage_label 已变更为 Stage 1"）。

  - **§Item-8 框架演进风险与应急路径**：
    (a) 列出**已公开但未生效**的 L2Beat 框架可能变更（如 Walkaway Test 进入 enforced 状态、
        grace period 过期、Forum 中讨论中但未通过的提案、Forum #425 challenge period 进一步
        变化的可能性），逐项评估对 Mantle 时间线的影响。
    (b) **应急路径**：若 L2Beat 在 Mantle 阶段 2 / 阶段 3 之间引入新硬要求，Mantle 的应对
        策略（含部分 Gap 接受 partial 满足、与 L2Beat 协商 grace period、必要时切换实现路径）。
    (c) **不应做的预测**：明确列出本研究**不**预测的事项（如 L2Beat 内部未公开决策、
        SP1 Hypercube 主网时间表、其他 L2 的具体 Stage 1 通过日期），并解释为什么这些不应
        在本研究中给出投机判断。

  - **§Diagrams 汇总**：至少 4 张 Mermaid 图（diag-1 ~ diag-4，详见 Diagram Expectations）。

  - **§Source Coverage**：列出**所有上游 final sections 的精确引用**（包含 commit SHA 与
    §section anchor）+ 本研究新增的外部来源（如 OP Stack 公开审计 cadence 参考、L2Beat 论坛
    讨论帖等）。

  - **§Gap Analysis**：列出**本研究内部未闭合的 Open Question** 与 carry-forward future-work
    （如 Mantle 团队内部排期、具体审计方选型、SC 成员招募的法务 / 合规细节等本研究 out-of-scope
    项），并明确这些 Gap 的所属（Mantle 内部 / L2Beat 协作 / 外部审计方）。

  - **§Revision Log**：标注本 final 与上游 5 个 final 的引用 commit、本课题 Round 1 → Final
    的修订记录。

  **Evidence 引用规则**（贯穿全文）：
  - **每个 Gap、每个 Action Item、每张图的每个节点**必须显式锚定到上游 final section 的具体
    位置（如 `upgrade-exitwindow-securitycouncil/final.md §Item-6 (6.b) GuardedExecutor 设计`）；
  - 上游 final 的 commit SHA 必须在 frontmatter `upstream_final_commits` 字段中固化；
  - 本研究**不引入**未在上游 final 中出现过的新事实陈述（除非是 L2Beat 框架文档 / OP Stack
    上游公开材料 / Mantle 链上数据的 secondary 引用，且必须显式标注 "external source - not from
    upstream final"）。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-19T15:00:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-19T15:00:00Z"

upstream_final_commits:
  l2beat-stage-framework-2026: "d1834f9003ce402a7103a3fb9a4e258925f7ae0d"
  mantle-architecture-2026: "60253749d49bf4723c06b27338d5119d15a16677"
  stage1-case-studies: "854419cca691404c3ec2b709cdfc12c8a7527be5"
  upgrade-exitwindow-securitycouncil: "f8ecb76b8cebfe41978451a1ec6db93f30c0e3d8"
  proposer-decentralization-zk-compliance: "3a7cb957aeccd4581c644e356bd11c95f7461fbd"

upstream_caveats:
  source: "mantle-stage1-rollup/research-sections/_index.md § Caveats Registry"
  C1:
    section: stage1-case-studies
    description: "OP Mainnet and Scroll Item-7(C) exit-window matrix cells require re-verification against current L2Beat live data"
    affected_roadmap_items: [item-1, item-3, item-4, item-6, diag-1, diag-4]
    downstream_reverification_requirement: >
      Before quoting OP Mainnet or Scroll exit-window cell values in any Gap score, scoring
      rationale, diagram node, or §Source Coverage entry, re-verify against L2Beat project pages
      (Stages section + permissions section for OP Mainnet, Scroll). Any cell that cannot be
      re-verified must be annotated [UNVERIFIED - C1] and surfaced in §Gap Analysis.
  C2:
    section: stage1-case-studies
    description: "Starknet gate (4) program-commitment risk sourcing should be re-verified against current L2Beat + ZK Catalog data"
    affected_roadmap_items: [item-1, item-3, item-4, item-6, diag-3]
    downstream_reverification_requirement: >
      Before quoting Starknet gate-4 status in any comparison, diagram node, or §Source Coverage
      entry, re-verify against l2beat.com/scaling/projects/starknet (proof system section) and
      zk-catalog.dev Starknet entry. Any value that cannot be re-verified must be annotated
      [UNVERIFIED - C2] and surfaced in §Gap Analysis.
  draft_gate: >
    Research Agent must complete C1 and C2 re-verification and record pass/fail results in
    §Gap Analysis before any roadmap item, scoring cell, or diagram node that cites
    stage1-case-studies case-study cells is finalized. Silent promotion of accepted-risk values
    from the upstream section without explicit re-check is prohibited.
---

# Research Outline: Mantle Stage 1 路线图综合建议

## Items

### item-1: Master Gap List 与优先级评分体系

把 5 个上游 final sections 中分散提出的 Stage 1 阻断项与 future-work 项统一收敛为一份**带 ID 的
Master Gap List**，作为后续依赖图、时间线、风险矩阵、Action Items 的单一事实源。

具体研究内容：
(a) **覆盖维度（至少 8 项）**：
  (i) outside-SC upgrade exit window ≥5d（来源：`l2beat-stage-framework-2026` §item-3 三轨规则 +
      `upgrade-exitwindow-securitycouncil` Gap matrix G-2）；
  (ii) Security Council 量化阈值 ≥8 成员 / >75% threshold / ≥50% external（来源：
       `l2beat-stage-framework-2026` §item-3 + `upgrade-exitwindow-securitycouncil` 推荐 9-12 人 SC）；
  (iii) Walkaway Test 合规（含 auto-expiring pause + permissionless prover + 不依赖 SC 的 forced
        withdrawal 路径，来源：`l2beat-stage-framework-2026` §item-4 +
        `upgrade-exitwindow-securitycouncil` 不变量 W-1/W-2/W-3 + `stage1-case-studies` §item-7 表）；
  (iv) Proposer liveness（v2.0.1 → v3.0.0-rc.1 + fallbackTimeout，来源：
        `proposer-decentralization-zk-compliance` §item-1 + §item-2）；
  (v) L2 Proving System 5a-5d 透明度（含 L2Beat reproducibility re-verification 协作；来源：
       `l2beat-stage-framework-2026` §item-5 + `proposer-decentralization-zk-compliance` §item-2 + §item-3）；
  (vi) 三路径治理隔离（core rollup / MNT TimelockController / mETH，来源：
        `mantle-architecture-2026` §1 三路径治理 + `upgrade-exitwindow-securitycouncil` G-2 闭合证据）；
  (vii) 新合约审计（GuardedExecutor / TargetSelectorWhitelist / PauseTimelock，来源：
         `upgrade-exitwindow-securitycouncil` §Item-6 6.b + G-14）；
  (viii) Sequencer 去中心化与 force-inclusion 6h 优化（边界改进项，来源：
          `proposer-decentralization-zk-compliance` §item-5）。
(b) **评分方法 + 权重表 + 敏感性检查**（遵循 expected_output §Item-1(b) 中的预定权重表；下文为摘要）：

    紧急度 U（1-5）= f(U1 Grace-period距离×0.40, U2 L2Beat严重性×0.35, U3 TVS暴露×0.25)
    重要度 I（1-5）= f(I1 Stage1硬阻断×0.45, I2 DAG出边数×0.30, I3 Walkaway-FAIL×0.25)
    优先级得分 P = U × I（1-25）；象限分配 P1/P2/P3/P4 见权重表象限规则。

    draft 阶段如调整权重须附理由并列出所有受影响 Gap 的象限变化表。
    若默认权重 ±0.10 变动导致任何 Gap 象限改变，须在 §Gap Analysis 标注"评分敏感"。
    每条 Gap 附 2-3 句评分依据（锚定上游 final §section），避免数字漂移。
(c) **二元判定**：每条 Gap 标注 Stage 1 hard blocker / soft prerequisite / non-blocking improvement。
(d) **上游锚定**：每条 Gap 必须给出"上游 final + §section + 段落 anchor + 关键引用句"四元组，
    可被 Adversarial 与 TW 独立复核。

本 item 是后续 item-2 ~ item-7 的事实基础，**必须先完成且经一致性检查后才能展开后续 item**。

- **Priority**: high
- **Dependencies**: none（直接综合上游 5 个 final sections）

### item-2: 升级依赖关系图与可并行性分析

基于 item-1 的 Master Gap List，构建一张**Stage 1 升级 DAG**，识别 hard prerequisite / soft
prerequisite / parallel / serial 四类边，并给出**最优升级批次划分**与**critical path 估算**。

具体研究内容：
(a) 依据 item-1 每条 Gap 的"依赖来源"字段，建立两类边：(i) hard prerequisite（如
    "v3.0.0-rc.1 部署"是"fallbackTimeout 启用"的硬前置）、(ii) soft prerequisite（如
    "GuardedExecutor 审计"应在"SC 上线"前完成，但两者可平行推进）；
(b) 检查依赖图是否存在 cycle 或 deadlock，识别 critical path；
(c) 把节点按"批次"分组（parallel batches A-D），明确每批次的独立性与可并行性；
(d) 关键路径长度估算：基于公开审计 cadence（OpenZeppelin / Cantina / Sigma Prime / Trail of Bits
    三方独立公开数据）给出 critical path 时长**区间**（低-高），而不是单点估值，且必须标注
    估算依据是 "industry-reference, not Mantle-specific"。
(e) **diag-1**：Mermaid graph LR 形式渲染依赖图，节点 ID 与 item-1 Master Gap List ID 一致。
(f) 当出现"上游 final 之间存在矛盾或边界不清"时，本 item 必须显式标注（如 "v3.0.0-rc.1 部署
    时间表" 在上游中只有 G-6 标 Open，本 item 标注为外部输入需求而不发明数字）。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 分阶段里程碑时间线建议

把 item-1 Master Gap List 与 item-2 依赖图映射到一份**4 阶段时间线**（与上游
`upgrade-exitwindow-securitycouncil` final §Item-2 4 阶段过渡对齐），用甘特图渲染。

具体研究内容：
(a) 阶段划分（与上游对齐）：
  - **阶段 0**（当前态）：Stage 0 5/5 reqs met；MantleSecurityMultisig 6/14 与 Engineering 3/7
    持有所有升级权；单 proposer EOA；OP Succinct v2.0.1；无 SC、无 ≥5d delay、无 auto-expiring pause。
  - **阶段 1**（合约部署 + SC 组建）：部署 GuardedExecutor + TargetSelectorWhitelist +
    PauseTimelock 三新合约；升级至 OPSuccinctL2OutputOracle v3.0.0-rc.1 + 启用 fallbackTimeout；
    组建 9-12 人 SC + ≥50% 外部；TimelockEmergency / TimelockRegular 双轨上线；切换 core rollup
    路径 owner 至 GuardedExecutor。
  - **阶段 2**（Walkaway 模拟 + L2Beat 评估）：在 Sepolia 或主网灰度执行 Walkaway Scenario A / B
    端到端演练；触发 L2Beat reproducibility re-verification；公开 SP1 toolchain pin。
  - **阶段 3**（Stage 1 完整态）：L2Beat 项目页 stage_label 变更为 Stage 1；监控期。
  - （远期阶段 4）：Stage 2 路径预留，但本研究 out-of-scope，仅给出兼容性提示。
(b) **每阶段交付物清单**：合约部署清单（含地址占位）、参数变更 tx 列表（含 calldata 模板）、
    文档与脚本（含 reproducibility script、Walkaway scenario 测试报告）、治理提案要素清单。
(c) **退出准则表**：列 = `[阶段, 退出准则, 可观测信号, 上游依赖触发, 失败回退路径]`。
(d) **diag-2**：Mermaid gantt 渲染 4 阶段时间线，**使用相对时间**（T0、T0+N 周等）而非
    绝对日期，避免与 Mantle 内部排期冲突。
(e) **grace period 硬约束分析**：Forum #413 推算 grace cliff（≈ 2026-08-16，已在上游标 G-8 estimate）
    叠加到时间线上，给出 "T0 应不晚于哪个时间点才能让 reproducibility 在 grace period 内被
    re-verify" 的 backward induction，但**不**作为 hard date 强制约束；强调不确定性来源。
(f) **关键决策点**：标注 3-5 个里程碑级 go/no-go 决策点，配套**回退路径**（如阶段 2 Walkaway
    模拟失败时，是回滚到阶段 1 修补合约还是与 L2Beat 协商 partial-pass）。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 多维度风险评估矩阵

按四象限（技术 × 运营 × 治理 × 外部依赖）系统列出 Stage 1 升级路径的风险条目，并给出
跨维度复合风险分析。

具体研究内容：
(a) **风险象限定义**：
  - 技术风险：合约 bug / 实现路径不匹配 / OP Stack 上游兼容性破坏 / SP1 toolchain 升级断链；
  - 运营风险：proposer key 管理 / SC 签名设备 / 监控告警 / incident response 流程；
  - 治理风险：SC 成员独立性 / DAO 提案流程 / Council 成员公开度 / 三路径治理隔离失败；
  - 外部依赖风险：L2Beat 框架进一步变更 / OP Stack 上游延迟 / Succinct Labs 审计或部署延迟 /
    grace period 过期 / 外部审计方排期。
(b) **风险条目详表**：列 = `[Risk ID, 类别, Likelihood (l/m/h), Impact (l/m/h/c), Heat 评分,
    触发条件 / 早期信号, 缓解措施, 责任方类型, 残余风险]`；每象限至少 3 条。
(c) **跨维度复合风险**：至少 3 个交互场景，例如：
    - **复合 1**：SC 组建延迟（治理）+ grace period 临近过期（外部）→ 框架强制 enforcement
      触发 Stage 0 降级；
    - **复合 2**：v3.0.0-rc.1 审计延期（技术）+ 单 proposer 私钥泄露（运营）→ 资金冻结路径
      唯一依赖 6/14 Safe 紧急 addProposer；
    - **复合 3**：GuardedExecutor 上线后 PauseTimelock 配置错误（技术）+ SC 紧急召集失败
      （运营）→ Walkaway Scenario B 失败，状态永久挂起。
(d) **diag-3**：风险矩阵热力图（mermaid quadrant 或 ASCII 颜色表 + 注释文本），把 (b) 表的每条
    Risk 映射到热度色块。
(e) **diag-4**：升级优先级四象限图（mermaid quadrantChart，紧急度 × 重要度），把 §item-1
    Master Gap List 的每项映射到 P1-P4 四象限；给出每个象限的处置策略
    （P1 立即启动 / P2 计划启动 / P3 监控 / P4 暂缓）。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

### item-5: 审计与验证计划

基于 item-1 ~ item-4 输出一份**分批次审计计划 + L2Beat re-verification 协作请求**。

具体研究内容：
(a) **Tier-A 必审清单**（Stage 1 hard prerequisite）：
  - GuardedExecutor + TargetSelectorWhitelist + PauseTimelock（三新合约，full audit）；
  - OPSuccinctL2OutputOracle v3.0.0-rc.1（differential vs v2.0.1，重点 fallbackTimeout + initializer）；
  - OptimismPortal 升级路径（若 Mantle 选择切到 OP Stack 上游 ≥v1.8.x 引入 auto-expiring pause，则
    differential；上游版本号需在 draft 阶段确认，外部输入项）；
  - 双 Timelock（TimelockEmergency / TimelockRegular）配置审计（focused）。
(b) **Tier-B 选审清单**（Stage 1 strongly recommended but not blocking）：
  - DA 路径变更后的 batcher / BatchInbox 配置审计（含 Arsia 后 EigenDA 移除路径的安全 review）；
  - Proposer key rotation 流程审计（运营级，半审计性质）；
  - SP1 verifier route freeze / fallback 应急脚本审计；
  - mETH / LSP 治理路径审计（确认与 core rollup 治理隔离）。
(c) **Tier-C 自查清单**（内部 SOP）：
  - SC 成员身份公开（含法域分布、利益冲突披露）；
  - 外部成员比例 ≥50%；
  - 签名设备运维（硬件钱包、多方签名仪式、密钥备份）；
  - 三路径治理隔离链上 hasRole 周期性自检脚本。
(d) **审计周期区间估算**：基于 OpenZeppelin / Cantina / Sigma Prime / Trail of Bits 公开数据，
    给出 Tier-A 总时长区间（如 8-16 周）+ Tier-B 总时长区间。**禁止**指定具体审计方。
(e) **L2Beat reproducibility re-verification 协作请求计划**：
  - 步骤 1：Mantle / Succinct 联合发布 SP1 toolchain pin（Rust nightly-2025-09-15 + SP1 SDK =6.1.0
    + Docker builder image tag，参考 `proposer-decentralization-zk-compliance` §item-2 的精确
    版本固化），公开 verify-binaries 脚本与 Dockerfile；
  - 步骤 2：在 mantle-research 仓库或 mantle-xyz/op-succinct 发布 reproducibility attestation
    （含 aggregation vkey / range vkey / rollup config hash 与链上 storage slot 直读匹配证据）；
  - 步骤 3：与 L2Beat 评估窗口对接（forum 帖 + L2Beat issue tracker）；
  - 步骤 4：L2Beat 项目页文本更新（从 `Code: unknown / Verification: None` → reproducibility
    判定明示）；
  - 每步附"建议时间窗（相对 T0）"与"可观测交付物"。
(f) **OP Stack 上游审计协调**：识别哪些升级（如 OptimismPortal auto-expiring pause、新的
    OP Stack 治理样板）需要 OP Stack 上游审计前置；列出 OP Stack governance forum / Optimism
    Foundation 公开渠道作为接触点，不点名个人。

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-3

### item-6: OP Stack 上游协调策略

识别哪些升级可以 leverage OP Stack 上游进度，哪些必须 Mantle 自研；给出 fork-vs-PR-vs-wait
决策树与 OP Mainnet 2024-08 rollback 经验沉淀。

具体研究内容：
(a) **leverage vs 自研决策表**：列 = `[升级项, OP Stack 上游状态 (有/即将有/无), Mantle 优先级,
    建议路径 (leverage / fork / 自研 / 等待上游), 决策依据]`。重点条目：
  - OptimismPortal auto-expiring pause 实现路径（已在 stage1-case-studies 中提到 OP Mainnet
    2024-08 之后的设计趋势，Mantle 需评估 leverage 还是 fork）；
  - PauseTimelock 包装层（Mantle 特有设计，需自研但可参考 OP Mainnet GuardedExecutor 概念）；
  - GuardedExecutor + TargetSelectorWhitelist（Mantle 特有设计，自研）；
  - v3.0.0-rc.1 OPSuccinctL2OutputOracle（mantle-xyz/op-succinct fork 而非 succinctlabs/op-succinct
    upstream，需评估是否要把 Mantle-specific 改动 upstream 给 Succinct Labs）；
  - 9-12 人 SC + 嵌套 2/2 ProxyAdminOwner（Base 已有模板，可借鉴但需调整外部成员比例）；
  - Walkaway Scenario A/B 模拟脚本（Mantle 自研，可参考 OP Mainnet 与 Base 的公开 scenario）。
(b) **PR / Fork / Wait 决策树**：对每条 "OP Stack 即将有但 Mantle 时间表更紧" 的项，给出
    决策建议（等待上游 / 维护 fork / 提交 upstream PR）与 trade-off 分析（维护成本 vs 时间风险
    vs 安全审计 vs 生态对齐）。
(c) **OP Mainnet 2024-08 rollback 经验沉淀**：把 stage1-case-studies §item-3 OP Mainnet
    2024-08-16 Cannon / PreimageOracle / FaultDisputeGame 三处 High 级 bug rollback 经验作为
    Stage 1 上线后 incident response playbook 的**借鉴维度**（具体 playbook 由 Mantle 内部
    撰写，本研究不替代撰写）。借鉴维度至少覆盖：
  - 监控信号选取（链上 anomaly detection、proof system 异常）；
  - SC 召集流程（紧急 vs 常规）；
  - 公开通信节奏（incident report 模板）；
  - 上游协调（OP Foundation 的同步窗口）。
(d) **OP Stack governance forum / Optimism Foundation 公开渠道列表**：作为 OP Stack 协调的
    接触点，**不点名个人**，只列出公开 channels。

- **Priority**: medium
- **Dependencies**: item-1, item-2

### item-7: 可执行 Action Items 清单

把 item-1 ~ item-6 的结论收敛为一份**带 owner 职责类型 / due date 相对窗口 / 可观测交付物**的
扁平 Action Items 清单。

具体研究内容：
(a) **扁平 Action Items 表**：列 = `[AI ID, Action 描述 (1-2 句), 所属 Gap ID, 所属里程碑 (阶段 1/2/3),
    前置依赖 (AI IDs), Owner 职责类型, 可观测交付物, 是否阻塞 Stage 1 (yes/no/conditional)]`；
    按所属里程碑分组排序；总数预计 25-40 条（足够细以可执行，不至于碎到无法管理）。
(b) **Owner 职责类型分类**（**禁止指定具体姓名**）：
  - **PE**：Mantle 协议工程（合约部署 / 升级 tx 执行 / 链上参数变更）；
  - **GOV**：Mantle 治理 / DAO 协调（提案撰写 / SC 招募 / 治理流程）；
  - **AUDIT**：Mantle 安全审计协调（与外部审计方对接、审计 deliverable 验收）；
  - **COMM**：Mantle 社区 / 沟通（公开公告 / forum 帖 / 用户通知）；
  - **L2BEAT**：L2Beat 评估对接人（reproducibility re-verification 窗口、Stage label 沟通）；
  - **OPSTACK**：OP Stack 上游协调人（forum / PR / fork 维护）；
  - **EXT**：外部审计方（提交审计报告、修复轮回）。
(c) **可观测交付物**：每条 Action Item 必须给出具体可观察的完成信号，至少属于以下一类：
  - 链上 tx（含 tx hash 占位、calldata 模板）；
  - forum 帖 / 治理提案（含 URL 模板）；
  - git commit / PR / audit report（含 mantle-xyz/op-succinct / mantlenetworkio 仓库占位）；
  - L2Beat 项目页文本变化（含 stage_label / risk row 变化）；
  - 内部文档发布（含路径占位）。
(d) **依赖图自洽性检查**：所有 Action Items 的前置依赖必须能在表内闭合，不留 dangling 引用；
    若某 Action Item 依赖 Mantle 内部排期（如治理 vote turnout、Council 招募），必须标注
    "外部不可控变量"。
(e) **阶段对齐**：每条 Action Item 必须能精确归属到 item-3 4 阶段中的某一阶段（或跨阶段标注）。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6

### item-8: 框架演进风险与应急路径

评估已公开但未生效的 L2Beat 框架变更对 Mantle 时间线的可能影响，并给出应急路径。

具体研究内容：
(a) **已公开未生效变更清单**（不做投机预测）：
  - **Walkaway Test enforcement 进一步推进**：Forum #412 当前是 proposed / upcoming，未来若进入
    enforced 状态（含正式 Stage 0 降级），Scroll / Starknet 与可能的其他 walkaway-FAIL 项目会
    被影响；评估 Mantle 在阶段 1 / 2 / 3 中的暴露窗口。
  - **Forum #413 grace period 过期**：推算 cliff ≈ 2026-08-16（estimate，标 G-8 caveat）。若
    grace period 真实截止，未完成 reproducibility 的项目会被标"failing"或降级。评估 Mantle
    的暴露窗口与应急路径。
  - **Forum #425 OR challenge period 进一步变化的可能性**：当前 5d 已是下调结果。若进一步
    下调或上调，对 Mantle ZK 路径**不直接适用**但可能间接影响生态预期。
  - **新增 Stage 1 项**：若 L2Beat 引入新硬要求（如 force-inclusion delay 上限、proposer 集合
    去中心化阈值等），评估对 Mantle 的影响。
(b) **应急路径**：
  - **Path A**（部分接受 partial 满足）：与 L2Beat 协商在 Stage 1 完整态前接受部分维度的
    partial pass + 显式公开 caveat；
  - **Path B**（push grace period 延期）：通过 forum 帖 + 公开论据请求延期；
  - **Path C**（必要时切换实现路径）：如 OptimismPortal auto-expiring pause 上游进度不及预期，
    Mantle 自维护 PauseTimelock 实现；
  - **Path D**（接受 Stage 0 降级或保持 Stage 0）：若所有 Path A-C 失败，分析"保持 Stage 0
    继续推进 vs 强行宣称 Stage 1"的权衡。
(c) **不应做的预测清单**：明确列出本研究**不**预测的事项：
  - L2Beat 内部未公开决策；
  - SP1 Hypercube（无 trusted-setup）主网迁移时间表（Succinct Labs 内部信息）；
  - 其他 L2 的具体 Stage 1 通过日期；
  - Mantle 内部排期；
  - 具体审计方公司选型与排期。
  并解释为什么这些不应在本研究中给出投机判断（避免数字漂移、避免误导决策、避免越权指定）。

- **Priority**: medium
- **Dependencies**: item-1, item-3

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| upstream_anchor | 精确引用：上游 final section + §section anchor + 关键引用句，作为该条目的事实基线 | all |
| current_state | Mantle 当前态在该维度的事实摘要（≤3 句，必须 evidence-anchored） | item-1 |
| stage1_requirement | L2Beat Stage 1 在该维度的可量化要求或 enforcement_status | item-1 |
| priority_score_rationale | 紧急度 + 重要度 + 总分 + 2-3 句评分依据，避免数字漂移 | item-1, item-4 |
| hard_blocker_judgement | Stage 1 hard blocker / soft prerequisite / non-blocking improvement 三态二元判定 | item-1 |
| dependency_edges | 该升级在 DAG 中的入边与出边列表（hard / soft 区分） | item-1, item-2 |
| parallel_batch_assignment | 该升级所属的 parallel batch（A/B/C/D） | item-2 |
| critical_path_segment | 该升级是否在 critical path 上；若是，所占时长区间估算 | item-2 |
| milestone_alignment | 该 Gap / Action Item 所归属的里程碑阶段（阶段 1/2/3，或跨阶段） | item-3, item-7 |
| exit_criteria | 阶段退出准则（可观测信号 + 上游依赖触发） | item-3 |
| rollback_path | 失败回退路径（用于 go/no-go 决策与 incident response 借鉴） | item-3, item-4, item-6 |
| risk_category | 技术 / 运营 / 治理 / 外部依赖 四象限归类 | item-4 |
| likelihood_impact_heat | Likelihood × Impact 二维评分与 Heat 总分；附 2-3 句判定依据 | item-4 |
| cross_dimension_interaction | 跨维度复合风险描述（至少 3 个场景） | item-4 |
| audit_tier_and_scope | Tier-A/B/C 归类 + audit type（differential/full/focused）+ 周期区间 | item-5 |
| l2beat_collab_step | L2Beat reproducibility re-verification 协作中的具体步骤与时间窗 | item-5 |
| op_stack_decision | leverage / fork / 自研 / 等待上游 四选一 + 2-3 句决策依据 | item-6 |
| op_mainnet_lesson | 从 stage1-case-studies §item-3 提取的 OP Mainnet 2024-08 rollback 借鉴维度 | item-6 |
| action_item_owner_role | PE / GOV / AUDIT / COMM / L2BEAT / OPSTACK / EXT 七类职责（禁姓名） | item-7 |
| observable_deliverable | 链上 tx / forum 帖 / git commit / L2Beat 项目页文本 / 内部文档 五类可观测交付物 | item-7 |
| framework_evolution_exposure | 已公开未生效变更对 Mantle 时间线的暴露窗口 + 应急 Path A-D 之一 | item-8 |
| evidence_sources | 该条目使用的全部上游 final + 外部 secondary source 列表 | all |
| open_questions | 该 item 内部未闭合的 Open Question / future-work（必须显式归属） | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy / graph | Stage 1 升级依赖关系图：节点 = item-1 Master Gap List 中的每项；边 = hard prerequisite（实线）或 soft prerequisite（虚线）；显式标注 critical path 着色；同时区分 4 个 parallel batches（颜色分组） | mermaid | item-2 |
| diag-2 | timeline / gantt | 分阶段里程碑甘特图：4 阶段 × 关键交付物 × 时间窗口；使用相对时间（T0、T0+N 周）；标注 grace period cliff 推算位置；标注 3-5 个 go/no-go 决策点 | mermaid | item-3 |
| diag-3 | heat / matrix | 风险矩阵热力图：四象限（技术 / 运营 / 治理 / 外部依赖）× Heat 评分（low / medium / high / critical 四色）；每象限至少 3 条 Risk ID，含跨维度复合风险节点连线 | mermaid | item-4 |
| diag-4 | quadrant | 升级优先级四象限图：x = 紧急度 1-5；y = 重要度 1-5；点 = item-1 Master Gap List 每项；点位置由 priority_score_rationale 决定；P1/P2/P3/P4 四象限处置策略 inline 标注 | mermaid | item-4 |
| diag-5 | flow | (可选) OP Stack 上游协调决策树：根节点 = "某升级项"，分支按 leverage / fork / 自研 / 等待上游 四选一，叶节点 = 决策建议 + trade-off 摘要 | mermaid | item-6 |
| diag-6 | timeline | (可选) Action Items 依赖瀑布图：按 item-7 的扁平表生成 dependency waterfall（横轴 = 时间 / 阶段，纵轴 = AI ID，连线 = 前置依赖），用于直观检查依赖闭环 | mermaid | item-7 |

**最少必交付**：diag-1 / diag-2 / diag-3 / diag-4 四张（Dispatch 明示要求）。diag-5 / diag-6 为
增强可读性的可选图，draft 阶段视容量决定是否产出。

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | upstream_research_final | 本项目前 5 个 final sections（commit SHA 在 frontmatter `upstream_final_commits` 固化），是本研究**唯一的 primary 事实基线**；所有 Gap / Action Item / Diagram 节点必须可锚定到此处 | 5 (全部) |
| src-2 | l2beat_framework_docs | L2Beat 公开框架文档（Stages 总览、Glossary、Forum #291 / #409 / #412 / #413 / #425、Monthly Updates、相关 Medium 文章）；本研究在评估 framework_evolution_exposure 时**直接引用上游 §section 已固化的 URL**，避免重新搜索。**注意**：src-1（stage1-case-studies）中 C1/C2 标注的 OP Mainnet / Scroll exit-window 单元格与 Starknet gate-4 状态在引用前必须按 `upstream_caveats` 要求做实时再验证，不可直接复用上游 URL 而绕过再验证门控 | 6 |
| src-3 | mantle_onchain_anchor | Mantle mainnet 链上数据锚点（合约地址、storage slot、role assignment）；本研究**不重新执行**链上 retrieval，仅复用上游 final 已固化的 cast 输出，作为评分与依赖图的事实基础 | 4 (核心合约地址) |
| src-4 | op_stack_upstream_signals | OP Stack 上游公开渠道（OP Stack governance forum、Optimism Collective 公开提案、optimism-org GitHub repo 关键 PR / release notes）；用于 item-6 leverage / fork / 等待上游 决策 | 3 |
| src-5 | audit_cadence_reference | 公开审计方 cadence 参考（OpenZeppelin / Cantina / Sigma Prime / Trail of Bits 等公开 changelog 或 case study）；用于 item-5 审计周期区间估算，**仅作为 industry-reference**，不指定具体公司 | 2 |
| src-6 | reproducibility_collab_anchor | L2Beat 评估窗口与 SP1 reproducibility 协作的公开接触点（L2Beat forum、ZK Catalog、L2Beat issue tracker 或等价 channel）；用于 item-5 协作请求计划 | 2 |

**Evidence 引用规则**：
- src-1（上游 5 个 final）是 primary，**全部 Gap / Action Item / Diagram 节点必须锚定**；
- src-2 ~ src-6 是 secondary，仅在补充 framework_evolution_exposure / OP Stack 协调 / 审计 cadence /
  reproducibility 协作时引用；
- 任何引用必须给出具体 §section + URL / commit SHA，禁止泛指；
- 本研究**不引入**未在上游 final 中固化、且未在 src-2 ~ src-6 公开 channel 中可独立验证的
  新事实陈述（避免新数据漂移）。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| R1→R2 | Pin upstream SHA | frontmatter `upstream_final_commits` | Review finding: "main, post 2026-05-19" is not reproducible anchor | Research Review Agent verdict, 2026-05-19 |
| R1→R2 | Add `upstream_caveats` block | frontmatter | Review finding: C1/C2 caveats from `_index.md` not propagated; src-2 rule risks silent promotion of unverified cells | Research Review Agent verdict, 2026-05-19 |
| R1→R2 | Replace item-1(b) with weight table | expected_output §Item-1(b) + Items §item-1(b) | Review finding: scoring formula under-specified; weights, normalization, tie-breakers, and sensitivity check missing | Research Review Agent verdict, 2026-05-19 |
