---
topic: "Mantle 合约升级机制、退出窗口与安全委员会设计"
project_slug: mantle-stage1-rollup
topic_slug: upgrade-exitwindow-securitycouncil
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: mantle-stage1-rollup/outlines/upgrade-exitwindow-securitycouncil.md
  draft: mantle-stage1-rollup/research-sections/upgrade-exitwindow-securitycouncil/drafts/round-{n}.md
  final: mantle-stage1-rollup/research-sections/upgrade-exitwindow-securitycouncil/final.md
  index: mantle-stage1-rollup/research-sections/_index.md

scope: |
  系统设计 Mantle 进入 L2Beat Stage 1 所需的"合约升级机制 + 退出窗口 + 安全委员会"三位一体方案，覆盖：

  (1) **现状盘点**：基于 mantle-architecture-2026 三路径治理（core rollup contracts / L1MantleToken / mETH 产品层）
      与 Arsia 升级 (2026-04-16) 后的合约拓扑，逐合约梳理 Mantle 当前升级权限链——
      ProxyAdmin → TimelockController（当前约 1 天 delay）→ 各 proxy（OptimismPortal、SystemConfig、
      L1StandardBridge、L1CrossDomainMessenger、SP1VerifierGateway 等）的 owner / proposer / executor 角色，
      并显式区分 L1 vs L2 合约、core rollup vs MNT vs mETH 三条独立治理路径。

  (2) **L2Beat Stage 1 要求映射**：基于 l2beat-stage-framework-2026 final，把 Stage 1 在
      Security Council、Exit Window、Walkaway Test 三维度的具体阈值锚定到 Mantle 实际场景：
      - Security Council 量化要求：≥8 成员、>75% 阈值、≥50% 外部、≥2 外部签名、成员公开、
        proof system effective power ≥25%；
      - **Exit Window 三轨规则（来自 l2beat-stage-framework-2026 item-3）**：
        (i) outside-SC upgrade exit window ≥5d（适用 OR + ZK，**Mantle 实际承担此规则**）、
        (ii) Optimistic Rollup challenge period ≥5d（Forum #425，**Mantle ZK 路径不适用**）、
        (iii) Stage 2 unwanted-upgrade ≥30d（远期目标，本研究不主推但需预留路径）；
      - Walkaway Test (Forum #412)：用户必须能在 Security Council 永久消失情况下安全退出；
        本研究必须显式核验 enforcement_status（proposed / adopted / grace-period-active /
        enforced-on-project-pages 四态）以避免把提案文本当作硬性规则。

  (3) **Security Council 架构设计**：成员数、阈值、外部比例、签名机制、紧急 vs 常规权限边界、
      可选嵌套多签（Base 模式）、与 MNT DAO governance 的隔离；显式与 stage1-case-studies 中
      Arbitrum (9/12 + 7/12 SC, 17d 8h timelock)、OP Mainnet (10/13 SC, 2024-08 rollback 事件)、
      Base (9/12 SC, nested 2/2 ProxyAdminOwner) 三个 **参考架构** 对照，并将 Starknet (3/12 SC =
      Operator) 与 Scroll (Team 2/4 TimelockEmergency, 2026-04-13 dissolve SC 提案) 两个
      **反模式** 作为禁区。

  (4) **Exit Window 过渡设计**：从当前 ~1d timelock 演进到 ≥5d outside-SC upgrade exit window 的
      分阶段路径（含中间态、紧急回退机制、链上参数变更脚本）；显式指出 Mantle 走 OP Succinct
      validity-proof 路径，不承担 OR challenge period 5d 规则，本研究主轴是 (3a) outside-SC
      upgrade ≥5d 与 Walkaway Test 配套的强制提款路径。

  (5) **双轨制升级路径**：紧急升级（Security Council 即时多签，需 >75% + ≥2 外部签名，
      仅限可裁决 onchain bug 或安全事件）vs 常规升级（DAO governance + ≥5d Timelock，
      用户可在 timelock 期间退出），在合约层（TimelockController 角色 + ProxyAdmin owner）
      的具体分离方案。

  (6) **Walkaway Test 合规验证**：设计 Security Council 消失情况下的用户强制退出路径——
      强制提款合约（OptimismPortal forceTransaction）、L1 fallback proposer、
      permissionless prover 入口（与 proposer-decentralization-zk-compliance 协调）、
      bridge withdrawal finality 不依赖 Council 任何签名。

  (7) **MNT 治理与 Security Council 的关系**：明确 L1MantleToken / MNT governance 路径
      （影响 token 供应、tokenomics）与 core rollup contracts 升级路径（影响用户资金安全）的
      治理隔离原则；避免一个 multisig 同时持有两类权限。

  (8) **过渡路线图与风险分析**：列出从 Stage 0 (当前) → Stage 1 推荐架构的具体迁移步骤、
      合约部署/参数变更 transaction 序列、回滚机制、过渡期间的安全风险（如 timelock 延长
      期间的 stuck-upgrade 风险、SC 签名密钥管理风险、参数变更治理漏洞）与对应缓解措施。

  本研究是 stage1-roadmap-recommendation 的核心上游依赖，必须为路线图提供精确、可落地、
  与现有 Mantle 合约拓扑兼容的设计建议；不重新评估 L2Beat Stage 1 框架本身（由
  l2beat-stage-framework-2026 final 提供），不重复 case study 的项目分析（由
  stage1-case-studies 提供），但需要把这两个上游的结论精确翻译到 Mantle 场景。

audience: |
  Mantle 协议工程师与治理团队（合约升级与多签运维的直接执行者）；
  Multica 研究 squad 内部下游 Research Agent（stage1-roadmap-recommendation）；
  L2Beat Stage 1 评估方与生态合作伙伴（关注 Mantle 升级路径与 SC 设计的合规性）；
  关注 OP Stack + ZK validity-proof 混合架构在 Stage 1 落地的协议研究者与投研分析师。
  阅读者熟悉 EVM 智能合约升级模式（Proxy / Implementation / ProxyAdmin / TimelockController）、
  multisig 多签机制（Gnosis Safe / threshold signatures）、L2 rollup 基本架构（OptimismPortal、
  SystemConfig、output oracle），但不一定熟悉 Mantle 具体合约拓扑与 L2Beat 最新 (2026.05) 框架细节。

expected_output: |
  - **Mantle 当前合约升级机制全景表**：按"合约 × 升级权限链"二维结构整理：
    (a) 每个核心合约（ProxyAdmin、TimelockController、OptimismPortal、SystemConfig、
        L1StandardBridge、L1CrossDomainMessenger、SP1VerifierGateway、SuccinctL2OutputOracle、
        L1MantleToken、mETH/staking 相关合约）的当前实现地址（以 mainnet 链上数据为准）、
        owner、admin、可升级路径；
    (b) 每条升级路径的精确 delay 配置（含 TimelockController.minDelay、proposer / executor 角色、
        ProxyAdmin.owner、各 proxy 的 admin 是 ProxyAdmin 还是直接 multisig）；
    (c) 三路径治理（core rollup / MNT / mETH）的边界与重叠点；
    (d) Arsia 升级 (2026-04-16) 后从 EigenDA → Ethereum blobs + SP1VerifierGateway 路由层的
        升级路径变化。
  - **L2Beat Stage 1 要求 → Mantle 现状 Gap 矩阵**：按"维度 × 当前状态 × Stage 1 要求 × Gap × 推荐"
    五列展示。维度包括：(1) Security Council 量化阈值、(2) outside-SC upgrade exit window ≥5d、
    (3) Walkaway Test 合规、(4) ZK Proving System 四子项 (5a-5d)（参考 l2beat-stage-framework-2026
    item-5，主要由 proposer-decentralization-zk-compliance 处理，本研究只引用最终判定）、
    (5) Council 外部成员比例、(6) Council 成员公开度、(7) Council 紧急权限边界。
  - **推荐 Security Council 架构设计书**：
    (a) 成员组成（≥8 人，建议 9-12 人覆盖时区与法域；外部 ≥50% 推荐 7/12 或 8/12）；
    (b) 阈值（>75%，建议 7/9 或 9/12，**严禁** 5/8 因为 62.5% 不达 75% 阈值，亦严禁 7/9 以下
        当外部成员不足 ≥50% 时）；
    (c) 签名机制（Gnosis Safe / 等价多签合约 + 链上签名公示）；
    (d) 紧急权限边界（仅限可裁决 onchain bug 与已发生的安全事件，**不得**作为常规升级 happy-path 的必要参与者，
        以避免 Walkaway Test fail）；
    (e) 嵌套多签可选方案（Base 模式：core SC + nested 2/2 ProxyAdminOwner 增加冗余）；
    (f) 与现有 Mantle multisig（如 deployer EOA、DAO multisig）的迁移与角色分离。
  - **Exit Window 过渡方案（分阶段）**：
    (a) 阶段 0：当前 ~1d Timelock + 即时升级权（Stage 0）；
    (b) 阶段 1：Timelock 延至 ≥5d outside-SC upgrade + Security Council 紧急即时升级权 + 强制提款合约部署（Stage 1 候选态）；
    (c) 阶段 2：Walkaway Test 合规验证（用户在 SC 消失情况下可独立完成强制提款）+ proving system 四子项验证通过（Stage 1 完整态）；
    (d) 阶段 3（远期）：Exit Window 延至 ≥30d，Security Council 退化为仅介入可裁决 onchain bug（Stage 2 目标，本研究不主推但需预留路径）；
    每个阶段必须列出：(i) 链上参数变更 transaction（含调用 TimelockController.updateDelay 等的 calldata）、
    (ii) 合约部署清单、(iii) 治理投票/Council 签名要求、(iv) 用户提款/退出窗口预估变化、
    (v) 失败/回滚条件。
  - **双轨制升级路径合约层设计**：
    - 紧急轨：Security Council 多签作为 TimelockController.PROPOSER_ROLE + EXECUTOR_ROLE 持有者，
      在 minDelay = 0 的紧急路径上执行（**仅限白名单函数 / 紧急 pause**，需明确合约层的函数选择器白名单）；
    - 常规轨：DAO governance 或更宽 multisig 作为 TimelockController.PROPOSER_ROLE 持有者，
      在 minDelay ≥ 5d 的常规路径上执行（OpenZeppelin TimelockController 的 schedule → execute 流程）；
    - 两轨在合约层的具体分离方式（两个独立 TimelockController vs 单个 TimelockController 多角色 vs
      两个独立 ProxyAdmin）的方案比较与推荐选择。
  - **Walkaway Test 合规验证文档**：
    - 列出 SC 消失情况下，用户从 L2 退出到 L1 的完整路径（OptimismPortal.forceWithdrawalTransaction
      或等价机制 → L1 出口合约 → 用户拿回资金）；
    - 显式核验每一步是否需要任何 Council 成员签名或 Council 控制的合约函数；
    - 列出 proving system 在 SC 消失情况下的活性假设（permissionless prover 路径，
      由 proposer-decentralization-zk-compliance 详细评估，本研究只引用结论）。
  - **MNT 治理与 SC 隔离设计文档**：
    - 明确 L1MantleToken / MNT governance（token 供应、tokenomics 决策）不应控制 core rollup contracts 升级；
    - 列出 mETH/staking 产品层合约（LSP）的独立治理路径；
    - 三路径 multisig 成员重叠的禁止/允许规则（建议禁止任何成员同时持有 core SC 与 MNT 多签签名权）。
  - **过渡路线图（时间线视图）**：从 2026.06（当前）→ Stage 1 候选态 → Stage 1 完整态的关键里程碑，
    每个里程碑标注 (i) 所需上游依赖（如 l2beat-stage-framework-2026 final 已发布、
    proposer-decentralization-zk-compliance 完成）、(ii) 阻塞条件、(iii) 风险与缓解、(iv) 可观察的链上信号。
  - **风险分析矩阵**：至少覆盖 (a) Timelock 延长期间紧急 bug 修复的窗口、(b) SC 签名密钥泄露/丢失、
    (c) 单一 multisig 持有过多权限、(d) Walkaway Test enforcement_status 不确定导致的合规风险、
    (e) Mantle ZK 路径与 OP Stack 上游升级窗口不一致、(f) DA 路径变更（Arsia: EigenDA → blobs）后的
    新升级风险面、(g) 嵌套多签（Base 模式）增加的运维复杂度。
  - **至少 5 张 Mermaid 图**（详见 Diagram Expectations）。
  - **Evidence**：≥5 类一手来源（Mantle 合约链上数据/源码、L2Beat Mantle 项目页、L2Beat Stages 文档、
    其他 L2 SC 公开配置、OpenZeppelin 合约文档）+ 上游 final/draft 的精确引用。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-19T04:00:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-19T04:00:00Z"
---

# Research Outline: Mantle 合约升级机制、退出窗口与安全委员会设计

## Items

### item-1: Mantle 当前合约升级机制全景（三路径治理 × 核心合约 × 权限链）

系统盘点 Mantle 当前（2026.05，Arsia 升级后）的合约升级机制全景，作为 Stage 1 设计的现状基线。
基于 mantle-architecture-2026 outline 中识别的**三路径治理结构**（core rollup contracts /
L1MantleToken / mETH 产品层）展开，覆盖：

(a) **Core rollup contracts 路径**：ProxyAdmin → TimelockController（当前约 1 天 delay）→
    各 L1 proxy 合约（OptimismPortal、SystemConfig、L1StandardBridge、L1CrossDomainMessenger、
    SP1VerifierGateway、SuccinctL2OutputOracle 或等价 output oracle）的 owner / admin 关系。
    Arsia 升级（2026-04-16）后新增 SP1VerifierGateway 作为 ZK verifier 路由层，需单独梳理其
    upgrade authority 与 vkey 更新机制（vkey 升级是否走同一 timelock？还是单独 admin？）。

(b) **L1MantleToken / MNT 治理路径**：MNT token 供应控制、tokenomics 参数变更涉及的 multisig
    与 timelock（与 core rollup contracts 是否共用？是否独立？）。

(c) **mETH / 产品层路径**：mETH 相关合约（LSP / staking router 等）的独立 admin 链路。

(d) **L2 合约升级路径**：L2 上游 (L1) 触发的 L2 系统合约升级（如 L2CrossDomainMessenger、
    L2StandardBridge、GasOracle 等）的 message-passing 机制，明确"L2 系统合约的最终升级权限
    仍在 L1"这一关键事实。

(e) **当前 timelock 精确配置**：TimelockController.minDelay (当前约 1 天的精确值)、PROPOSER_ROLE、
    EXECUTOR_ROLE、TIMELOCK_ADMIN_ROLE 持有者；ProxyAdmin.owner 的当前持有者（EOA / multisig /
    timelock）；是否存在任何 proxy 直接以 EOA 或低门槛 multisig 作为 admin 的"未走 timelock"的
    后门路径。

(f) **L2Beat Mantle 项目页当前快照**：核验 L2Beat 对 Mantle 升级路径的现有标注
    （"upgradable" / "delay X days" / "Security Council: none" 等），作为 Gap 分析的输入。

本 item 是后续所有设计的**事实基线**，必须基于链上数据（Etherscan + mantlenetworkio/networks 仓库）+ 
mantle-v2 / op-geth / op-succinct 源码 + L2Beat 项目页快照三方交叉验证，**禁止**仅凭官方文档或
非一手解读。

- **Priority**: high
- **Dependencies**: none (依赖 mantle-architecture-2026 作为上游 context，但 item-1 自身是事实盘点)

### item-2: L2Beat Stage 1 要求 → Mantle 现状 Gap 矩阵（Council × Exit Window × Walkaway × Proving System）

把 l2beat-stage-framework-2026 final 中的 Stage 1 完整检查清单（item-3 三轨 Exit Window 规则 +
item-4 Walkaway Test + Council 量化阈值 + item-5 ZK Proving System 四子项）精确映射到 Mantle 现状，
逐项给出 Gap 评估。

**核心维度**：

(1) **Security Council 量化要求**（≥8 成员、>75% 阈值、≥50% 外部成员、≥2 外部签名达成共识、
    成员身份公开、proof system effective power ≥25%）—— Mantle 当前缺失情况（Stage 0：5/5 reqs met
    但无独立 SC，由 Mantle Foundation multisig 直接持有升级权）。

(2) **Exit Window 三轨规则的 Mantle 适用性**（**核心边界澄清，与 l2beat-stage-framework-2026
    item-3 + item-9 严格对齐**）：
    - **适用 (3a)**：outside-SC upgrade exit window ≥5d 适用于 Mantle（OP Stack + OP Succinct
      ZK validity-proof 混合架构同样承担此通用规则）；
    - **不适用 (3b)**：Optimistic Rollup challenge period ≥5d (Forum #425) **不适用** Mantle
      —— Mantle 走 validity-proof 路径，不存在 fraud-proof challenge window；任何把 Forum #425
      5d 阈值当作 Mantle "validity-proof challenge period" 进行检验的做法都是 false-positive；
    - **(3c) 的 Mantle 注解**：Mantle 可能存在自定义 finalization delay（如 OP Succinct 的
      finalizationPeriodSeconds 参数），但该 delay 不构成 L2Beat 框架定义的 challenge period，
      本研究不把 finalizationPeriodSeconds 当作 Exit Window 组件来设计；
    - **预留 Stage 2 路径**：unwanted-upgrade ≥30d 作为远期目标，但 Stage 1 推荐方案不强制达到。

(3) **Walkaway Test (Forum #412)**：用户在 Security Council 永久消失情况下必须能安全退出。
    Mantle 当前是否通过？需要核验 (a) 强制提款合约（OptimismPortal.forceTransaction 或等价）的
    存在与运行、(b) prover/proposer 路径是否独立于 Council、(c) bridge withdrawal finality 是否
    依赖任何 Council 签名。
    **enforcement_status 边界**：l2beat-stage-framework-2026 item-4 明确要求显式追踪
    enforcement_status ∈ {proposed | adopted | grace-period-active | enforced-on-project-pages} —
    本 item 必须把核验出的 enforcement_status 直接引用，避免把提案文本当作硬性合规标准；
    在 enforcement_status 不是 enforced-on-project-pages 的情况下，本研究的 Walkaway Test 设计
    应当**作为 Stage 1 推荐方案的内在质量目标**，而**不**作为"L2Beat 强制要求"陈述给读者。

(4) **ZK Proving System 四子项 (5a-5d)**（参考 l2beat-stage-framework-2026 item-5）：
    (5a) no 🔴 trusted setups、(5b) prover source published、(5c) verifiers reproducible (vkey)、
    (5d) ZK programs reproducible。**本研究只在 Gap 矩阵中列出这四项的 Mantle 现状 + Stage 1 要求**，
    详细 verifier/prover/program 重建验证由 proposer-decentralization-zk-compliance 处理；
    在 Gap 矩阵中需要标注每子项的 enforcement_status + grace_period_end（Forum #413 约 2026-08-16），
    用于与 upgrade/exit-window 设计的时间表对齐。

(5) **Council 外部成员定义**：l2beat-stage-framework-2026 final 中"外部"的精确定义
    （非项目核心团队、非投资人、独立机构代表等），本 item 必须直接引用而非自行重新定义。

(6) **Council 成员公开度**：身份公开、签名地址公开、签名行为可链上验证（multisig 合约地址、
    各成员 EOA 地址、签名 transaction）三层公开度要求。

(7) **Council 紧急权限边界**：仅限可裁决 onchain bug 的范围；不得作为常规升级 happy-path 的
    必要参与者；与 item-6 双轨制设计直接对接。

输出形式：5 列表格（维度 / 当前状态 / Stage 1 要求 / Gap / 推荐解决方向），每行附 L2Beat 项目页
快照链接 / Mantle 链上数据交叉验证。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Security Council 推荐架构设计（成员 / 阈值 / 外部 / 签名 / 嵌套 / 权限边界）

设计符合 L2Beat Stage 1 要求且与 Mantle 现有合约拓扑兼容的 Security Council 架构。

**(3.a) 成员组成**：
- **数量**：建议 9-12 人（>L2Beat 最低 8 人门槛，覆盖时区与法域，应对单点失联）；
- **外部比例**：≥50%（建议 7/12 或 6/9 为外部，**严禁**外部比例不足 50%——参考
  stage1-case-studies 中 Starknet 3/12 SC = Operator 的反模式）；
- **法域分布**：避免单一法域占多数（参考 Arbitrum 9/12 + 7/12 SC 的两层结构对法域分布的处理）；
- **角色多样性**：建议覆盖独立安全研究者、生态合作伙伴、用户代表、外部审计机构等。

**(3.b) 阈值**：
- **必须 >75%**：参考 Stage 1 量化阈值——给出几种合规组合（7/9 = 77.8%、9/12 = 75% 是否满足
  ">75%" 的精确边界？需对照 l2beat-stage-framework-2026 final 的措辞——是 "≥75%" 还是 ">75%"
  严格大于，并据此调整推荐组合）；
- **proof system effective power ≥25%**：解释该数学推导（与 75% 阈值的关系），并在 Mantle
  context 给出推荐：是否将 SP1Verifier / SuccinctL2OutputOracle 的 emergency upgrade 路径
  与 Council 阈值绑定。

**(3.c) 签名机制**：
- Gnosis Safe (或等价 multisig 合约) + 链上签名公示；
- 签名地址轮换机制（成员变更时的多签 ownerOf 更新流程）；
- 离线签名 / 硬件钱包要求；
- 与 ProxyAdmin / TimelockController 的合约层集成方式。

**(3.d) 嵌套多签可选方案**：
- 评估 **Base 模式**（参考 stage1-case-studies 中 Base 9/12 SC + nested 2/2 ProxyAdminOwner）—— 
  外层 SC 控制核心升级权限，内层 nested 2/2（如 Mantle Foundation 2/2）增加冗余与防误操作；
  - 优点：双重失败模式隔离、运维便利；
  - 缺点：增加复杂度、可能违反 Walkaway Test（如果 nested 2/2 是 happy-path 必要参与者）；
- **不推荐方案**：单层 multisig（无 nested）；多层嵌套（>2 层，过于复杂）。

**(3.e) 紧急权限边界（与 item-6 双轨设计对接）**：
- **紧急路径合法范围**：可裁决 onchain bug、verifier 配置错误、已发生的安全事件（如 hack 进行中）、
  upstream OP Stack 紧急补丁；
- **不得**作为常规升级 happy-path 必要参与者（Walkaway Test 红线）；
- **函数选择器白名单**：紧急路径只能调用预先公示的 pause / vkey rotation / emergency upgrade
  函数选择器，不得调用任意 setter；
- **每次紧急升级的事后公示要求**（链上 event + L2Beat 监控）。

**(3.f) 与现有 Mantle multisig 的迁移**：
- 当前 ProxyAdmin.owner / TimelockController PROPOSER 持有者（具体地址待 item-1 核验）→
  迁移到新 Security Council multisig 的步骤；
- 角色分离：Mantle Foundation multisig 不应同时持有 SC + MNT governance（参考 item-7）。

**输出**：架构设计书（含表格 + 至少 1 张 Mermaid 嵌套多签架构图）；
对照表（Arbitrum / OP Mainnet / Base / Mantle 推荐）；
与 stage1-case-studies final 的精确交叉引用。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Exit Window 过渡设计（当前 ~1d → ≥5d outside-SC upgrade exit window）

详细规划 Mantle 从当前 ~1d Timelock 演进到 Stage 1 ≥5d outside-SC upgrade exit window 的
分阶段方案。

**关键边界澄清（与 l2beat-stage-framework-2026 item-3 + item-9 严格对齐）**：

- 本研究主轴是 **(3a) outside-SC upgrade exit window ≥5d**——所有非 Security Council 主体发起的
  升级必须提供 ≥5d 退出窗口（适用 OR + ZK，Mantle 实际承担此规则）；
- **(3b) Optimistic Rollup challenge period ≥5d (Forum #425) 不适用 Mantle**——
  Mantle 走 OP Succinct validity-proof 路径，不存在 fraud-proof challenge window；
  本 item 设计的 5d 阈值是 outside-SC upgrade delay，**不**是任何 "validity-proof challenge period"；
- Mantle 可能存在自定义 finalization delay（OP Succinct.finalizationPeriodSeconds）；
  本 item 评估该 delay 与 outside-SC upgrade delay 的关系（是叠加还是并行？），但不把它当作
  L2Beat 定义的"challenge period"处理。

**(4.a) 分阶段路径**：

- **阶段 0（基线，2026.05 当前）**：Timelock delay ≈ 1d，无独立 Security Council，
  Mantle Foundation multisig 直接持有升级权（Stage 0 状态）。
- **阶段 1（过渡态，约 +1-2 个月）**：
  (i) 部署 Security Council multisig（按 item-3 推荐方案）；
  (ii) Timelock delay 调整为 ≥5d（推荐 5-7d，保留余量）；
  (iii) 双轨制升级路径合约层部署（按 item-6）；
  (iv) Council 与原 Foundation multisig 的角色切换 transaction。
- **阶段 2（Stage 1 候选态，阶段 1 完成后立即）**：
  (i) 强制提款合约部署或验证（OptimismPortal.forceTransaction 或等价）；
  (ii) Walkaway Test 内部模拟通过（按 item-5）；
  (iii) 提交 L2Beat 重新评估申请；
  (iv) ZK Proving System 四子项（5a-5d）由 proposer-decentralization-zk-compliance 同步推进；
        其 grace_period_end (Forum #413 约 2026-08-16) 是本阶段的硬约束截止时间窗。
- **阶段 3（Stage 1 完整态）**：L2Beat 项目页评定为 Stage 1。
- **阶段 4（远期 Stage 2 预留，本研究不主推）**：Exit Window 延至 ≥30d，
  SC 退化为仅介入可裁决 onchain bug；本研究在此阶段只画路径不做详细设计，
  以避免 Stage 1 设计中埋下 Stage 2 阻碍。

**(4.b) 每个阶段的精确 deliverable**：
- 链上参数变更 transaction（含 TimelockController.updateDelay calldata、PROPOSER_ROLE
  grantRole/revokeRole calldata、ProxyAdmin.transferOwnership calldata）；
- 合约部署清单（含新 SC multisig 地址、新 Timelock 实例 if any、强制提款合约 if any）；
- 治理要求（是否需要 MNT DAO 投票？还是仅 Council multisig 签名？）；
- 用户提款/退出窗口预估变化（用户视角）；
- 失败/回滚条件与回滚 transaction 序列。

**(4.c) 紧急 bug 修复窗口的兼容性**：
- Timelock 延至 ≥5d 后，紧急 bug 如何在 ≤5d 内修复？
- 设计 Security Council 紧急即时升级权（minDelay = 0 + Council >75% 签名）的合法范围
  与函数选择器白名单（与 item-3.e 紧急边界 + item-6 双轨设计协同）；
- 紧急升级后的事后公示要求（链上 event、L2Beat 监控、社区通报）。

**(4.d) 与 OP Stack 上游升级窗口的协调**：
- OP Stack 主线（Optimism Mainnet / Bedrock / Holocene）的紧急升级窗口可能短于 5d；
- Mantle 作为 OP Stack fork 如何处理上游紧急补丁？是否需要"upstream emergency adopt"路径
  豁免 5d timelock？该豁免本身是否需要 Council >75% 签名？

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

### item-5: Walkaway Test 合规验证与用户强制退出路径设计

详细设计 Security Council 永久消失情况下，Mantle 用户从 L2 退出到 L1 的完整路径，并核验该路径
**不**依赖任何 Council 成员签名或 Council 控制的合约函数。

**Walkaway Test 的来源与执行状态澄清**：
- 来源：l2beat-stage-framework-2026 item-4（Forum #412, 2025-12-19）；
- enforcement_status：本研究**必须**直接引用 l2beat-stage-framework-2026 final 中的核验结果，
  不得自行重新判定；
- 若 enforcement_status ∈ {proposed, adopted, grace-period-active}：本研究的 Walkaway Test 设计
  作为 Stage 1 推荐方案的内在质量目标，但**不**作为"L2Beat 当前强制要求"陈述；
- 若 enforcement_status = enforced-on-project-pages：本研究的设计直接作为 Stage 1 合规硬要求。

**(5.a) 用户强制退出的完整路径**：

(i) **L2 → L1 message-passing 入口**：核验 Mantle OptimismPortal.forceTransaction (或等价)
    是否存在、是否 permissionless 调用（任何用户可触发）、调用所需 gas / 费用机制；

(ii) **强制提款交易在 L2 的执行**：核验 L2 sequencer 是否可以审查 / 延迟 / 拒绝 force transaction；
     **Stage 1 关键问题**：当 sequencer 离线或恶意时，用户能否通过 L1 直接 enqueue
     L2 transaction 并保证执行？需评估 Mantle 当前 sequencer/proposer 拓扑下的 censorship resistance
     窗口；

(iii) **L2 state root post 到 L1**：proposer 路径（OP Succinct prover + proposer）
      在 SC 消失情况下的活性假设——是否仍有 permissionless prover 接管？
      （详细评估由 proposer-decentralization-zk-compliance 处理，本 item 只列引用接口与所需结论）；

(iv) **L1 bridge withdrawal finality**：用户提交 L1 提款 transaction 后的 finality 延迟
      （SP1Verifier accept validity proof 后即刻 finality）；
      核验该路径不依赖 Council 任何签名；

(v) **failure paths**：每一步可能失败的场景与用户的备用路径
    （如 OptimismPortal 暂停状态下用户如何退出？SP1Verifier vkey 升级停滞时的备用 verifier 路径？）。

**(5.b) Council 依赖点逐项核验**：

对每一步显式给出"是否依赖 Council 签名 / 是否依赖 Council 控制的合约函数"二元判定；
任何依赖点都必须重设计或迁移到 permissionless 路径。

**(5.c) 与 Stage 0 提交人路径的边界**：
- l2beat-stage-framework-2026 item-2 (f) "至少 5 个外部参与者可提交 fraud proof" 属于 **Stage 0**
  且**针对 Optimistic Rollup**；Mantle 走 validity-proof 路径不直接适用，但替代要求
  （item-5 (5c)(5d) verifier/program 可重建性 + permissionless prover 路径）必须满足；
- 本 item 在 ZK 路径下的 Walkaway Test 含义是：**permissionless prover** 可在 Council 消失情况下
  继续生成与提交 validity proof，且 verifier vkey 不在 Council 单方面控制下被冻结。

**(5.d) Walkaway Test 内部模拟方案**：
- 设计一个"Security Council 全员失联"的内部演练：所有 Council 私钥销毁的假设下，
  跑通 force withdrawal → L1 finality 的完整路径；
- 演练 deliverable：测试网交易序列、链上 event log、用户视角的 timing & UX 评估。

**(5.e) 与 stage1-case-studies 反模式对照**：
- **Starknet 反模式**：3/12 Council seats = Operator——Walkaway 一旦执行，proposer 路径也消失；
  Mantle 设计必须**禁止**任何 Council 成员同时持有 proposer / sequencer 单点角色；
- **Scroll 反模式**：Team 2/4 TimelockEmergency 控制紧急路径——Mantle 设计必须把 emergency 角色
  完全交给 Security Council 多签，**禁止** team multisig 持有独立紧急升级权。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4

### item-6: 双轨制升级路径合约层设计（紧急 SC 轨 vs 常规 DAO+Timelock 轨）

设计紧急升级（Security Council 即时多签，>75% + ≥2 外部签名，仅可裁决 onchain bug 与安全事件）
与常规升级（DAO governance / 更宽 multisig + ≥5d Timelock）在 EVM 合约层的具体分离方案。

**(6.a) 三种合约层架构对比**：

- **架构 A：单 TimelockController 多角色**
  - 同一个 TimelockController 实例同时持有"紧急轨"（minDelay = 0，PROPOSER 仅 Council）和
    "常规轨"（minDelay ≥ 5d，PROPOSER 为 DAO/multisig）的双角色；
  - 优点：合约简单、状态集中；
  - 缺点：单合约不能同时持有两个 minDelay 值（OpenZeppelin TimelockController 是单 minDelay 设计）；
    需要在 schedule 时通过 delay 参数区分（但 minDelay 是下限，无法实现"紧急路径 = 0"与"常规路径 ≥ 5d"
    同时执行）；该架构**不可行**——必须排除。

- **架构 B：双 TimelockController 实例（推荐）**
  - **TimelockEmergency**：minDelay = 0，PROPOSER_ROLE = Security Council multisig，
    EXECUTOR_ROLE = Security Council multisig（或开放给任意调用者），**函数选择器白名单**
    限制只能调用 pause / emergency vkey rotation / 已审计的 hotfix；
  - **TimelockRegular**：minDelay ≥ 5d（推荐 5-7d），PROPOSER_ROLE = DAO governance multisig
    或更宽 multisig，EXECUTOR_ROLE 开放；调用任意 setter；
  - 两个 Timelock 都是 ProxyAdmin.owner 的有效 caller，但**白名单层**保证 TimelockEmergency
    只能调用白名单函数；
  - 优点：路径完全隔离，符合 Stage 1 "Council 仅介入紧急情况"边界；
  - 缺点：两个合约的状态需要同步维护；emergency 函数选择器白名单需要严谨的链上更新机制
    （白名单本身的更新走 TimelockRegular ≥ 5d 路径）。

- **架构 C：双 ProxyAdmin 实例**
  - 每个 proxy 同时被两个 ProxyAdmin 控制（一个紧急 admin / 一个常规 admin）；
  - EVM 单 admin 限制：proxy ERC-1967 admin slot 单值，**不可行**——必须排除。

**结论**：推荐**架构 B（双 TimelockController）**。

**(6.b) 函数选择器白名单设计**：
- 白名单维护合约：独立 contract 存储 selector → bool whitelist mapping；
- 白名单初始集合：
  - `pause()` / `unpause()` (OptimismPortal, L1StandardBridge, L1CrossDomainMessenger)；
  - `setVerifier(address)` / `rotateVerifier(...)` (SP1VerifierGateway emergency vkey rotation)；
  - `setRespectedGameType(...)` 或等价 dispute game emergency function (如适用)；
  - `setOwner(...)` / `transferOwnership(...)` ?（**风险高**，应排除——SC 不应单独转让任何 owner）；
- 白名单更新走 TimelockRegular ≥ 5d，禁止 emergency 自我提权。

**(6.c) ProxyAdmin.owner 持有者设计**：
- ProxyAdmin.owner 不直接是 multisig，而是一个**Router 合约**，
  - Router 接收升级调用，按"是否在 emergency 白名单"路由到 TimelockEmergency 或 TimelockRegular；
  - 或：ProxyAdmin.owner 直接是 TimelockRegular（默认路径），TimelockEmergency 只对白名单函数有
    setter 权限（不经 ProxyAdmin 而是直接 setter on proxy）；
  - 两种方案的对比与推荐选择。

**(6.d) 升级 transaction 链与监控**：
- 每次紧急升级链上 event：emergency function selector + caller (Council) + 签名集 + 调用 calldata；
- 每次常规升级链上 event：schedule timestamp + execute timestamp + 5d 间隔验证；
- 用户监控接入点：L2Beat / Etherscan / Mantle 自有 dashboard 应展示两轨的所有 pending upgrade。

**(6.e) 与 stage1-case-studies 参考架构对照**：
- **Arbitrum 模式**：Council 9/12 + 7/12 两层（紧急 7/12 SC + 常规 9/12 SC），17d 8h timelock —
  Mantle 是否采用两层 SC？还是单 SC + 双 timelock？给出选择理由；
- **OP Mainnet 模式**：10/13 SC，2024-08 rollback 事件后单 timelock 路径 —— Mantle 风险偏好对比；
- **Base 模式**：9/12 SC + nested 2/2 ProxyAdminOwner，instantly upgradable —— Mantle **不**采用
  instant upgrade（违反 outside-SC upgrade ≥5d 规则）。

- **Priority**: high
- **Dependencies**: item-1, item-3, item-4

### item-7: MNT 治理与 Security Council 的隔离设计（三路径治理分离原则）

明确 Mantle 三路径治理（core rollup contracts / L1MantleToken-MNT / mETH 产品层）的治理分离原则，
设计三类 multisig 的成员重叠规则。

**(7.a) 三路径治理的边界澄清**：

- **core rollup contracts 路径**（本研究主轴）：升级 OptimismPortal、SystemConfig、
  L1StandardBridge、SP1VerifierGateway 等核心合约的 multisig / Security Council；
- **L1MantleToken / MNT 路径**：MNT token 供应控制、tokenomics 参数变更（如 mint / burn cap、
  transfer restrictions）涉及的 multisig 与 timelock；
- **mETH / 产品层路径**：mETH 相关合约（LSP / staking router / 等）的独立 admin 链路；
  本 item 仅做边界标注，详细治理由独立产品团队负责，不在本研究范围内。

**(7.b) 隔离原则**：

- **成员重叠禁止规则**：
  - **强禁止**：任何成员同时持有 core rollup SC + L1MantleToken multisig 签名权
    （理由：token 供应控制权与用户资金安全升级权混合 = 单点合谋风险）；
  - **强禁止**：任何成员同时持有 core rollup SC + mETH multisig 签名权
    （理由：产品风险与协议风险混合）；
  - **允许**：信息层面共享治理可见性（如 Council 列表公示，但签名权独立）。

- **TimelockController / ProxyAdmin 隔离**：
  - core rollup contracts 的 TimelockController 与 L1MantleToken 的 TimelockController
    **必须**是独立合约实例；
  - ProxyAdmin 实例同上独立。

**(7.c) 现状核验与迁移**：
- 核验 Mantle 当前是否存在 multisig 同时控制 core rollup + MNT（基于 item-1 链上数据）；
- 若存在，列出迁移步骤（成员拆分、签名权重新分配、合约 owner 转移 transaction）；
- 迁移期间的临时安全风险（multi-step transaction 间的 inconsistent state）与缓解措施。

**(7.d) DAO governance 与 Council 的关系**：
- MNT DAO governance 决议是否可作为 core rollup contracts 升级的合法 PROPOSER？
  - 推荐：DAO governance 作为 TimelockRegular.PROPOSER_ROLE（常规升级路径）；
  - **禁止**：DAO governance 作为 TimelockEmergency.PROPOSER_ROLE（紧急路径仅限 Council）；
- DAO 投票通过的升级仍走 ≥5d Timelock（满足 outside-SC upgrade ≥5d 规则）。

**(7.e) 与 stage1-case-studies 对照**：
- 大多数 L2（Arbitrum / OP / Base）的 Council 与 token DAO 治理在合约层是独立的；
- 给出 Mantle 当前与推荐的对照表。

- **Priority**: medium
- **Dependencies**: item-1, item-3

### item-8: 过渡路线图与风险分析矩阵

整合 item-3 ~ item-7 的所有设计，输出可执行的端到端过渡路线图，并系统识别风险与缓解。

**(8.a) 时间线**：
- **2026.05–2026.06**（外部依赖准备）：
  - l2beat-stage-framework-2026 final 已发布（done，order=1）；
  - mantle-architecture-2026 完成（order=2）；
  - stage1-case-studies 完成（order=3）；
  - proposer-decentralization-zk-compliance 启动（与本研究并行，order=5）；
- **2026.06–2026.08**（合约部署与参数调整）：
  - 部署新 Security Council multisig + TimelockEmergency + 函数选择器白名单合约；
  - 调整 TimelockRegular minDelay 至 ≥5d；
  - 完成现有 ProxyAdmin.owner 迁移；
  - 完成 MNT / mETH 与 core rollup contracts 的治理隔离；
  - **硬约束**：Forum #413 grace_period_end ≈ 2026-08-16（ZK Proving System 四子项），
    需与 proposer-decentralization-zk-compliance 协调；
- **2026.08–2026.10**（Walkaway Test 模拟与 L2Beat 评估）：
  - 内部 Walkaway Test 模拟与公开演练；
  - 提交 L2Beat 重新评估申请；
  - 应对 L2Beat / Adversarial 反馈，调整方案；
- **2026.10+**：Stage 1 完整态评定（理想路径）。

**(8.b) 风险与缓解矩阵**：

| 风险 ID | 风险 | 触发条件 | 缓解措施 | 监控信号 |
|---------|------|----------|----------|----------|
| R-1 | Timelock 延长期间紧急 bug 修复窗口不足 | 5d delay 内发现严重 bug | TimelockEmergency 白名单覆盖关键 pause/setter；事后审计 | 紧急升级 event 频率 |
| R-2 | Security Council 签名密钥泄露/丢失 | 私钥管理失误 | ≥75% 阈值 + ≥2 外部签名 + 硬件钱包要求 | 多签 ownerOf 变更 event |
| R-3 | 单一 multisig 持有过多权限 | 迁移期间临时配置错误 | 治理隔离 audit + 链上 owner 关系图谱监控 | ProxyAdmin.owner 变更 |
| R-4 | Walkaway Test enforcement_status 不确定导致合规风险 | L2Beat 提案未 enforced 但社区认为已生效 | 直接引用 l2beat-stage-framework-2026 final enforcement_status；不自我判定 | L2Beat 项目页公告 |
| R-5 | Mantle ZK 路径与 OP Stack 上游升级窗口不一致 | 上游紧急补丁 < 5d | "upstream emergency adopt" 路径（白名单 + Council 签名） | OP Stack release notes |
| R-6 | Arsia 升级后新的升级风险面（SP1VerifierGateway） | vkey 错误升级 | vkey rotation 走白名单 emergency 路径 + 事后公示 | SP1VerifierGateway event |
| R-7 | 嵌套多签运维复杂度（如采用 Base 模式） | 内层多签密钥失联 | 嵌套层文档化 + 定期 drill | 内外层 multisig event |
| R-8 | 函数选择器白名单更新被滥用 | TimelockRegular 路径上 Council 提议扩展白名单 | 白名单更新需 DAO 投票 + ≥5d Timelock + 用户退出窗口 | 白名单合约 event |
| R-9 | DA 路径变更（EigenDA → blobs）后的新升级路径风险 | Arsia 升级后未审计的新路径 | 全量 audit 新合约 + 走完整 TimelockRegular 路径 | DA 相关合约升级 event |

**(8.c) 路线图与上下游协调**：
- 与 stage1-roadmap-recommendation（下游）的接口：本研究输出的所有"阶段 / 风险 / 缓解"
  作为 roadmap 的合约/治理章节直接输入；
- 与 proposer-decentralization-zk-compliance（并行）的接口：
  Walkaway Test 中 permissionless prover 假设由该 issue 验证，本研究只引用结论；
  ZK Proving System 四子项（5a-5d）由该 issue 详细评估，本研究只在 Gap 矩阵中列出。

**(8.d) 失败/回滚路径**：
- 若 Stage 1 评定失败，列出回滚到阶段 0 / 阶段 1 的链上 transaction 序列；
- 回滚本身是否需要 Council 签名？是否走 ≥5d Timelock？给出明确答案。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| current_state | Mantle 当前实际配置（含 L1 / L2 合约地址、owner、admin、delay 等链上数据）；必须基于 Etherscan + mantlenetworkio/networks + mantle-v2 源码三方交叉验证，注明数据抓取时间 | item-1, item-2, item-3, item-4, item-5, item-6, item-7 |
| l2beat_requirement | L2Beat Stage 1 / Stage 2 的对应要求文本与规范源（必须直接引用 l2beat-stage-framework-2026 final，不自行重新解读）；包括 enforcement_status ∈ {proposed, adopted, grace-period-active, enforced-on-project-pages} | item-2, item-3, item-4, item-5 |
| applicable_rollup_type | 该要求/子项适用的 rollup 类型：`all` / `optimistic-only` / `zk-only`；用于显式标注 Mantle 走 validity-proof 路径**不适用** Forum #425 OR challenge 5d、**适用** outside-SC upgrade ≥5d 等边界 | item-2, item-4, item-5 |
| gap_analysis | 当前状态与 L2Beat Stage 1 要求之间的量化 gap（含 delay 差、阈值差、外部成员差、enforcement 状态差） | item-2, item-3, item-4, item-5, item-7 |
| design_recommendation | 针对该项的具体设计推荐，含合约层实现方案（函数选择器、角色、阈值）、参数取值、备选方案对比 | item-3, item-4, item-5, item-6, item-7 |
| case_study_reference | 直接引用 stage1-case-studies final 中的对应实践（Arbitrum 9/12+7/12 / OP 10/13 / Base 9/12+nested 2/2 等参考架构，Starknet 3/12=Operator / Scroll Team 2/4 TimelockEmergency 等反模式），含具体配置参数与适用性评估 | item-3, item-4, item-6, item-7 |
| contract_implementation | 合约层实现方案：具体合约名（TimelockController / ProxyAdmin / Gnosis Safe 等）、函数签名、角色（PROPOSER_ROLE / EXECUTOR_ROLE / TIMELOCK_ADMIN_ROLE）、calldata 草稿、部署顺序 | item-1, item-3, item-4, item-5, item-6 |
| transition_steps | 从当前状态到推荐方案的迁移步骤（按时间顺序），每步含 transaction 序列 / 治理要求 / 失败回滚 / 用户影响 | item-3, item-4, item-5, item-6, item-7, item-8 |
| risk_and_mitigation | 实施风险与缓解措施，含触发条件、概率/严重性评估、缓解策略、可观察的链上信号 | item-3, item-4, item-5, item-6, item-7, item-8 |
| evidence_sources | 一手来源链接清单（Mantle 链上地址 + Etherscan 永久链接 + mantle-v2 / op-geth / op-succinct GitHub commit hash 永久链接 + L2Beat 项目页快照 + 其他 L2 SC 公开文档），优先使用 commit hash / 区块号锁定时间点 | all |
| open_questions | 当前公开材料中未明确、需要进一步链上核验或团队访谈确认的问题 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | Mantle 当前合约升级权限链全景图：以三路径治理（core rollup / MNT / mETH）为三列，列出每条路径的 ProxyAdmin → TimelockController → proxies 关系，每个节点旁标注 owner / admin 地址（脱敏后的角色名）+ 当前 delay 配置；显式标注 Arsia 升级（2026-04-16）后新增的 SP1VerifierGateway 节点及其 vkey 升级路径 | mermaid | item-1 |
| diag-2 | architecture | 推荐 Stage 1 双轨制升级架构图：Security Council multisig + TimelockEmergency（minDelay=0，函数选择器白名单）vs DAO/multisig + TimelockRegular（minDelay≥5d）；显式画出两条路径在 ProxyAdmin / 各 proxy 上的合约层分离方式（推荐架构 B 双 TimelockController）；可选展示 Base 模式 nested 2/2 ProxyAdminOwner 作为冗余层 | mermaid | item-3, item-6 |
| diag-3 | timeline | Exit Window 过渡时间线：阶段 0（当前 1d Timelock）→ 阶段 1（部署 SC + Timelock 5d）→ 阶段 2（Walkaway Test 验证 + L2Beat 评估）→ 阶段 3（Stage 1 完整态）→ 阶段 4（远期 Stage 2 ≥30d，预留路径）；每个节点标注硬约束日期（如 Forum #413 grace_period_end ≈ 2026-08-16）、依赖完成项、关键 transaction 序列 | mermaid | item-4, item-8 |
| diag-4 | flow | Walkaway Test 场景下的用户强制退出路径流程图：以"Security Council 全员消失"为输入，逐步检查 (a) 用户能否调用 OptimismPortal.forceTransaction、(b) L2 sequencer 是否可审查、(c) proposer/prover 路径是否独立于 SC、(d) verifier 是否独立运行、(e) bridge withdrawal 是否依赖任何 SC 签名；任一依赖 SC 即 Fail；标注每个节点是否依赖 stage1-case-studies 中识别的反模式（Starknet/Scroll）；同时标注本研究的 Walkaway Test 设计基于 l2beat-stage-framework-2026 item-4 的 enforcement_status，不自我判定 | mermaid | item-5 |
| diag-5 | comparison | Mantle vs 其他 L2 Security Council 配置对照矩阵（基于 stage1-case-studies）：Arbitrum (9/12 + 7/12 双层 SC, 17d 8h timelock) / OP Mainnet (10/13 SC, 2024-08 rollback) / Base (9/12 SC + nested 2/2 ProxyAdminOwner, instantly upgradable) / Starknet (3/12 = Operator, Walkaway FAIL) / Scroll (Team 2/4 TimelockEmergency, 2026-04-13 dissolve SC 提案) / Mantle 推荐 (9-12 SC, ≥50% 外部, ≥75% 阈值, TimelockEmergency + TimelockRegular 双轨 ≥5d) | mermaid | item-3, item-6 |
| diag-6 | comparison | 风险与缓解矩阵图：横轴=阶段（0/1/2/3/4），纵轴=风险类型（R-1 至 R-9，参见 item-8.b）；矩阵单元格显示风险等级（高/中/低）+ 缓解措施 ID；显式标注每个风险与上游/下游 issue（l2beat-stage-framework-2026, stage1-case-studies, proposer-decentralization-zk-compliance, stage1-roadmap-recommendation）的对接点 | mermaid | item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | on_chain_data | Mantle 主网核心合约链上数据快照：ProxyAdmin / TimelockController / OptimismPortal / SystemConfig / L1StandardBridge / L1CrossDomainMessenger / SP1VerifierGateway / SuccinctL2OutputOracle / L1MantleToken / mETH 相关合约的当前实现地址、owner、admin、delay 配置；优先使用 Etherscan 永久链接 + 抓取 blocknumber + 时间戳 | 8 |
| src-2 | code_analysis | mantle-v2 / op-geth / op-succinct / kona 仓库源码（含 contracts/L1 目录、proxy 设计、TimelockController 配置），需附 commit hash 永久链接 | 4 |
| src-3 | official_docs | L2Beat Mantle 项目页（含风险标注、Stage 评定、升级路径标注）2026.05 快照链接；L2Beat Stages 框架文档（必须直接引用 l2beat-stage-framework-2026 final 中对应章节，**不**重新解读） | 3 |
| src-4 | governance_proposals | L2Beat Forum 一手帖子：#291 The Stages Framework、#412 Security Council Walkaway Test、#413 ZK Proving System Stage 1 四项要求、#425 OR Challenge Period 7d→5d（最后一项仅用于显式说明对 Mantle 非适用） | 4 |
| src-5 | code_analysis | 其他 L2 Security Council 实现的公开合约 / 文档（Arbitrum L1ArbitrumTimelock + SecurityCouncilManager、OP Mainnet ProxyAdminOwner + Security Council、Base L1MultisigController + nested ProxyAdminOwner）；必须直接引用 stage1-case-studies final 中的精确配置参数 | 3 |
| src-6 | official_docs | OpenZeppelin TimelockController 文档与最佳实践、Gnosis Safe multisig 文档；用于函数选择器白名单 / minDelay 配置 / 角色管理的实现细节 | 2 |
| src-7 | expert_commentary | 上游 final/draft 的精确引用：l2beat-stage-framework-2026 final（必须，作为所有 L2Beat 要求的单一权威来源）、mantle-architecture-2026 final-or-latest-draft（必须，作为三路径治理与现状合约拓扑的输入）、stage1-case-studies final-or-latest-draft（必须，作为其他 L2 SC 对照的输入） | 3 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
