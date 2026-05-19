---
topic: "Stage 1 L2 案例研究：Arbitrum / OP Mainnet / Base / Starknet / Scroll 的 Stage 1 路径对比与 Mantle 借鉴"
project_slug: mantle-stage1-rollup
topic_slug: stage1-case-studies
github_repo: Whisker17/multica-research
round: 3
status: candidate

artifact_paths:
  outline: mantle-stage1-rollup/outlines/stage1-case-studies.md
  draft: mantle-stage1-rollup/research-sections/stage1-case-studies/drafts/round-{n}.md
  final: mantle-stage1-rollup/research-sections/stage1-case-studies/final.md
  index: mantle-stage1-rollup/research-sections/_index.md

scope: |
  分析已达到 Stage 1 的五个主要 L2 项目（Arbitrum One、OP Mainnet、Base、Starknet、Scroll）的具体 Stage 1
  达成路径与遗留差距，覆盖：(a) 各项目的证明系统设计（BOLD permissionless validation / Cannon fault proof /
  共享 OP Stack fault proof / STARK 证明 + SHARP / Scroll zkEVM proof + ScrollOwner），并按 L2Beat
  2026-02-16 新增的"Stage 1 proving-system 要求"对每个项目检查：(i) 是否使用 red-rated trusted setup、
  (ii) prover 源码是否公开、(iii) onchain verifier 源码与可复现编译路径是否公开、(iv) ZK / optimistic
  program 链上 commitment（如 program hash / prestate hash）是否可由公开源码独立重现；
  (b) Security Council 的具体配置（人数、阈值、外部成员比例、即时升级权限、与团队 multisig 的权责划分）；
  (c) Exit Window 设计（upgrade delay、forced inclusion、permissionless escape hatch 的有无）；
  (d) L2Beat 2025 年新增的 Walkaway Test 通过/未通过情况（即在 Security Council "走开" 的前提下，用户能否
  在 operator 作恶时退出），以及 2026 新增的 proving-system 维度独立判定 —— 即使 walkaway 通过，若
  proving-system gate 不通过仍可能阻塞 Stage 1；
  (e) 各项目 Stage 1 路径中暴露过的工程教训（如 OP Mainnet fault proof bug 与 Stage 0 短期回落、Scroll 解散
  Security Council 提案争议、Starknet SHARP 共享 verifier 治理路径）。在每个案例的事实基础上，构建跨项目对比
  矩阵，最终输出 Mantle（OP Stack + ZK Validity Proof 混合架构）可以借鉴的 Stage 1 推进经验，按对 Mantle 的
  相关性排序。
audience: |
  Mantle 核心协议团队（决定 Stage 1 路线图与时间表的工程与治理负责人）、Mantle 安全 / 治理工作组（负责
  Security Council 组建、合约升级策略、forced inclusion 等机制设计的成员）、Multica 研究 squad 内部下游
  Adversarial Agent 与 Technical Writer。读者熟悉 L2 基础概念（rollup、fault proof、ZK validity proof、
  multisig），但不一定熟悉 L2Beat Stages framework 的最新细则（特别是 2025 年新增的 Walkaway Test、
  2026-02-16 新增的 proving-system Stage 1 要求 —— 详见
  https://forum.l2beat.com/t/new-stage-1-requirements-for-l2-proving-systems/413 ，以及 2026-04-30 把
  Stage 1 最低 challenge period / 升级 exit window 由 7 天下调到 5 天的更新 —— 详见
  https://forum.l2beat.com/t/stage-1-update-minimum-challenge-period-reduction-from-7d-to-5d/425 ）
  以及各 L2 项目最新的合约级配置。
expected_output: |
  - 5 个 L2 项目的 Stage 1 路径详细分析（每个项目独立小节，含时间线、关键技术决定、Stage 1 阻力点、
    proving-system gate 检查结果）
  - Security Council 配置对比矩阵（成员数、阈值、外部成员比例、quorum、即时升级权限、与团队 multisig 关系）
  - Exit Window 设计对比表（upgrade delay、forced inclusion 机制、permissionless escape hatch、是否依赖
    Security Council、对应 L2Beat 评级所需的最低窗口）
  - Walkaway Test 通过/未通过分析：每个项目的 walkaway 判定（pass / fail），fail 项目的具体失败点与可能
    的修复路径，以及 L2Beat 2025 年 Stage 1 walkaway 更新对项目的可能降级影响
  - Proving-System Reproducibility 对比表（基于 L2Beat 2026-02-16 新规）：每项目对四项 gate
    （trusted-setup 颜色 / prover 源码 / verifier 源码与复现 / program commitment 复现）的 pass / fail
    与依据
  - 关键工程教训章节：OP Mainnet permissionless fault proof bug → Stage 0 短期回落（如有公开记录则引用；
    若仅有"Security Council 可回滚"的设计描述而无实际触发事件，必须显式标注 "no documented post-launch
    rollback event found"，禁止伪造事件）、Scroll 解散 Security Council 提案争议、Starknet SHARP 共享
    verifier 的多链耦合风险
  - Mantle 可借鉴经验总结：按"对 Mantle Stage 1 推进的直接适用度"排序（OP Stack 共享基础设施 > Base
    Security Council 组建过程 > Arbitrum BOLD bond 经济模型 > ZK 项目 walkaway 失败的反面教训 > ZK 项目
    proving-system reproducibility 教训 > Starknet/Scroll 治理结构），每条经验配套指出 Mantle 当前架构
    （OP Stack + ZK Validity Proof 混合）下的适配方式与潜在 gap，并对 Mantle 的 ZK Validity Proof 路径
    单独评估 proving-system gate 风险
  - 至少 5 张 Mermaid 图（时间线、Security Council 对比、walkaway 决策树、ZK vs Optimistic proof
    reproducibility 与 governance walkaway 双维度差异图、Mantle 借鉴金字塔）

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-18T15:22:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-19T00:30:00Z"
---

# Research Outline: Stage 1 L2 案例研究

## Items

### item-1: Stage 1 评估框架 — Walkaway Test 基线 + 2026-02-16 Proving-System Gates

确立后续所有案例分析共用的评估基线，由两组检查点共同构成：

**(A) 治理 / exit window 基线（L2Beat Stages framework + 2025 walkaway 更新 + 2026-04-30 5-day 更新）**：
Stage 1 的硬性要求 —— 功能完整的证明系统、permissionless fraud proof 提交、用户可在无 operator 协助下退出、
Security Council ≥ 8 人且 **quorum 共识阈值 ≥ 75%**（即"至少 3/4 共识"；具体项目可用 9/12 = 75%、
8/10 = 80%、12/16 = 75% 等配置满足此基线，项目特异性 quorum 事实须在 item-2~item-6 的
`security_council_config` 字段中按事实保留）。在此基础上必须把以下**三个独立的时间窗口概念分开陈述**：
  (i) **Stage 1 升级 exit window（Security Council 之外的合约升级路径）**：≥ **5 天**。该阈值自
      2026-04-30 起由原 ≥ 7 天下调到 ≥ 5 天，依据
      https://forum.l2beat.com/t/stage-1-update-minimum-challenge-period-reduction-from-7d-to-5d/425
      与当前 L2Beat Stages Framework 页面。
  (ii) **Optimistic Rollup 的 challenge / dispute period（争议解决窗口）最低值**：≥ **5 天**（同上
       2026-04-30 更新）。**该窗口在概念上独立于 (i)** —— (i) 约束治理升级窗口、(ii) 约束欺诈证明
       争议窗口；部分项目两者实现上复用同一定时器但不必然相等，draft 必须按事实分别记录两者的具体配置。
  (iii) **Stage 2 unwanted-upgrade exit window**：≥ **30 天**。2026-04-30 更新未触及 Stage 2 阈值，
        保持原值；本课题虽聚焦 Stage 1，但 (iii) 仍作为参照基线列出，以避免将 Stage 1 / Stage 2 的
        exit window 阈值在矩阵和叙事中混用。
以及 2025 年新增的 Walkaway Test —— 在 Security Council "走开" 的前提下，用户在 operator 作恶时是否仍
能退出。把 walkaway test 的判定逻辑拆成可机械检查的检查点（permissionless exit、forced inclusion、
Security Council 是否承担非紧急 censorship-resistance / liveness / safety 职责），并明确 walkaway 未通过
等价于在 2026 年框架下被降级到 Stage 0 的可能性。

**(B) 证明系统基线（L2Beat 2026-02-16 新增 "New Stage 1 Requirements for L2 Proving Systems"）**：
依据 https://forum.l2beat.com/t/new-stage-1-requirements-for-l2-proving-systems/413 ，把以下四条
proving-system gate 纳入 Stage 1 评估，并作为下游 item 共用模板：
  1. **No red trusted setups** —— Stage 1 项目的证明系统不得依赖被 L2Beat trusted-setup 框架标记为 red
     的 trusted setup（典型违规：Facet V1 / Zircuit / Loopring）。
  2. **Published prover source** —— prover 源码必须公开，使用户能在原 prover 失效时独立产生证明；当
     prover/proposer 由 assumed-honest minority 担任时可豁免。
  3. **Reproducible onchain verifiers** —— 全部链上 verifier（含 recursion 与 final wrap）必须有公开
     源码与"独立从源码重新生成 verifier 字节码"的明确指引（典型合规示例：Matter Labs Boojum、Polygon
     zkProver；反例：Lighter desert verifier）。
  4. **Reproducible ZK / optimistic program commitments** —— ZK 项目的 program / ZK Stack 自动化脚本，
     或 OP Stack 的 prestate 指引必须使得链上的 program commitment（如 ZK program hash、OP prestate
     hash）能由公开 program 源码独立重现。

需要明确：proving-system gate 与 walkaway test 是 **相互独立** 的两组判定 —— 一个项目可能 walkaway 通过
但 proving-system gate 失败（或反之），任一组失败都构成 Stage 1 阻碍因素；同时，由于该规则发布于
2026-02-16 且 L2Beat 未公布明确生效截止日，每个项目都按 "若立即生效" 评估，并标注"L2Beat 公告中未给出
显式 deadline" 的事实。

此 item 不展开任何具体项目，只输出后续 item-2~item-6 直接套用的判定模板与字段表。

- **Priority**: high
- **Dependencies**: none

### item-2: Arbitrum One — BOLD permissionless validation 路径 + Optimistic Proof Reproducibility

合约 + 治理层分析 Arbitrum One 通过 BOLD（Bounded Liquidity Delay）从 Stage 1（permissioned validator
set） 走向更强 Stage 1 / 接近 Stage 2 的路径：BOLD 的 N-vs-N "battle royale" 争议协议如何替代旧的 1-vs-1
challenge tournament 以解决 delay attack；3600 WETH assertion bond 与 555/79 WETH 子挑战 bond 分层设计
的经济直觉（让攻击者的资金风险与"延迟所有提款 ~一周"的机会成本对齐）；6.4 天 challenge window 与 ~12 天
最坏 dispute 解决上限；bonding pool 在不损害去中心化的同时摊薄 bond 准入门槛的作用。还需描述 Security
Council（9/12 + 7/12 双阈值，7/12 通过 13 天 timelock 提供 ~6 天 exit window）与 Stage 1 walkaway test 的
关系，以及 BOLD 在 Arbitrum One / Nova / Sepolia 上的部署状态与 governance vote 历史。

依据 L2Beat 2026-02-16 新规，单独评估 Arbitrum 的 optimistic-proof reproducibility：BOLD ChallengeManager
/ OneStepProver 的 verifier 源码是否公开、是否提供独立编译路径，以及 OSP / Nitro WASM module root 等
program commitment 是否能由公开 Nitro 源码独立重现（OP Stack 的 prestate-hash 类比，但 Arbitrum 用 WASM
root）。在 draft 阶段需给出明确 pass / fail 判定与引用，无公开材料则标注 "evidence not found"。

重点回答 key question 1（BOLD 如何解决 1-vs-1 delay attack 与 bond 经济逻辑），并补答"Arbitrum 在 2026
proving-system gates 下是否仍处于 Stage 1"这一问。

- **Priority**: high
- **Dependencies**: item-1

### item-3: OP Mainnet — Cannon fault proof + Permissionless Fault Proofs + Prestate Reproducibility

合约 + 时间线分析 OP Mainnet 通过 Cannon MIPS FPVM + 模块化 Dispute Game + permissionless fault proof
（2024-06-10 主网激活）达到 Stage 1 的路径：Cannon 作为 OP Stack 默认 FPVM 的链上 MIPS.sol 与链下 mipsevm
组成、Dispute Game 的模块化设计（允许未来插入 ZK FPVM）、Security Council 在 fault proof 出现 bug 时通过
"回退到 permissioned 状态 + 重置所有待提款" 的紧急权力。需要严格区分 **设计层面允许 Security Council
回滚** 与 **是否真实发生过 bug 触发回滚事件**：如果在公开来源（governance forum、Optimism Upgrade
proposals、L2Beat 状态变化记录）中能找到具体 Stage 0 短期回落事件则按事实记录并引用 commit / governance
proposal；如果只能找到"回滚机制存在"的设计描述而无实际触发记录，**必须显式标注 "no documented
post-launch rollback event found"，禁止伪造事件或夸大风险**。同时记录 Upgrade 16（Interop Contracts +
Stage 1 + Go 1.23 Cannon 支持）的关键内容与时间。

依据 L2Beat 2026-02-16 新规，单独评估 OP Mainnet 的 proving-system reproducibility：
  - prover 源码：Cannon mipsevm / op-program 仓库可见性；
  - verifier 源码：MIPS.sol / FaultDisputeGame / PreimageOracle 是否提供独立编译指引；
  - program commitment：absolutePrestate / prestate hash 是否可由公开 op-program 源码独立重现
    （OP Stack 官方文档明确给出 prestate guidelines，须引用具体文档与 commit）。

重点回答 key question 2（OP Mainnet 因 bug 回落 Stage 0 的具体原因与改进，若事实成立），并补答 OP Stack
作为 Mantle 直接祖先架构在 proving-system gates 下的样本表现。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Base — OP Stack Stage 1 + 独立 Security Council + 继承 OP Stack Reproducibility

分析 Base 在 2024-10 部署 fault proof（直接复用 OP Stack permissionless Fault Proof System）+ 2025-04
组建独立 Security Council + 2025-04-29 达成 Stage 1 的完整路径：fault proof 复用与 OP Mainnet 共享基础
设施的工程红利、Security Council 由 10 个独立第三方实体 + Optimism + Coinbase 共 12 名签名方构成、
upgrade quorum 设为 9/12 (75%)、其中"Security Council 内部要求 ≥ 75%" 与"Base Coordinator + Security
Council 双方都需要批准"的双重门槛设计。需要核对 L2Beat 关于 Base 是否真正提供 exit window（公开材料显示
合约 instantly upgradable，无标准用户 exit window，依赖 Security Council 的 75% 阈值作为唯一防线），并
结合 walkaway test 评估 Base 是否通过（若 Security Council 走开，用户能否在 operator 作恶下退出）。

依据 L2Beat 2026-02-16 新规，单独评估 Base 的 proving-system reproducibility：Base 直接继承 OP Stack
fault proof，其 prover / verifier / prestate 是否与 OP Mainnet 共用 commit，是否存在 Base 自定义分支
（如有需独立评估），并据此判定 Base 的 proving-system gate 通过状态是否可由"OP Stack 上游通过 ⇒ Base
通过"的传递结论得出。

重点回答 key question 5（Security Council 成员选择标准与组建过程）的 Base 部分，并作为"OP Stack chain
复用路径"的标准样本，为 Mantle 提供最直接可比的样板。

- **Priority**: high
- **Dependencies**: item-1, item-3

### item-5: Starknet — ZK Rollup Stage 1、Walkaway 失败 + STARK Proving-System Reproducibility

分析 Starknet 在 2025-05 达成 Stage 1（首个 ZK Rollup Stage 1）但未通过 walkaway test 的具体原因：核心
rollup 合约与桥（ETHBridge / STRKBridge）治理被 9/12 Security Council（即时升级权限） + 2/4 StarkWare
Multisig 2（8 天 delay）共同控制，且共享 SHARP verifier 由独立 2/4 SHARP Multisig（8 天 delay）控制 ——
这导致 Security Council 即使"走开"，2/4 StarkWare Multisig 与 SHARP Multisig 仍然保留实际控制路径，
walkaway 不成立；同时，Starknet 缺少通用 escape hatch（用户无法强制 freeze 状态），如果 operator 持续
censor 则没有可信的 forced inclusion 路径。需要进一步描述 STARK 证明系统与 SHARP 共享 verifier 的特点
（共享 verifier 在多个 StarkEx / Starknet 部署间复用，治理变更同时影响多链）。

依据 L2Beat 2026-02-16 新规，单独评估 Starknet 的 proving-system reproducibility（这是 ZK 项目最敏感的
维度）：
  - trusted setup：STARK 系统理论上 transparent / 无 trusted setup，但需核对 SHARP 内部组件是否引入
    被 L2Beat 框架标记为 red 的 trusted ceremony；
  - prover 源码：Stone / Stwo 等 STARK prover 仓库可见性；
  - onchain verifier：SHARP verifier 合约（多链共享）源码与独立重新生成路径；
  - program commitment：Starknet OS / cairo program hash 是否能由公开 cairo 源码独立重现（含 Stwo
    或 Stone 工具链）。
若任一 gate 未通过则结合 walkaway 失败一并归类为"治理 + proving-system 双失败"。

重点回答 key question 3（ZK Rollup vs Optimistic Rollup 的 proof system Stage 1 要求差异）的 Starknet
部分，以及 key question 4（Walkaway Test 在实践中如何评估 / Starknet 为何未通过）。

- **Priority**: high
- **Dependencies**: item-1, item-4

### item-6: Scroll — ZK Rollup Stage 1、ScrollOwner 多 Timelock、解散 Security Council 提案 + zkEVM Proof Reproducibility

分析 Scroll 作为第一个 / 早期到达 Stage 1 的 ZK Rollup 的路径：ScrollOwner 中央治理合约通过 4 个 Timelock
分隔权限（其中 2 个由 9/12 Security Council multisig 控制，2 个由 Scroll 团队 multisig 控制），每个 Timelock
对应不同变更类型与延迟保证；Scroll 通过 ProxyAdmin → ScrollOwner 路径升级所有核心合约。需要说明 Scroll
为何同样未通过 walkaway test（虽然有 Security Council，但 Scroll 团队 multisig 仍然持有独立的、不依赖
Security Council 的升级路径），并梳理 2025 年 4 月由 Scroll 团队发起的"解散 Security Council、把控制权
合并到 Scroll Admin multisig（约 10 天 timelock）"提案及其引发的社区争议 —— 这是 Stage 1 项目主动"降低
去中心化等级"的反面案例。

依据 L2Beat 2026-02-16 新规，单独评估 Scroll 的 zkEVM proving-system reproducibility：
  - trusted setup：Scroll zkEVM 所用 KZG / PLONK 类系统的 trusted setup（如 Powers of Tau / KZG
    ceremony 复用 EF Ethereum KZG 仪式）的 L2Beat trusted-setup 评级；
  - prover 源码：scroll-prover / aggregator 仓库可见性；
  - onchain verifier：ScrollChain 中的 Verifier / Aggregator Verifier 合约源码与独立重新生成指引；
  - program commitment：zkEVM batch / chunk 的 commitment 与 verifying key 是否能由公开 scroll-prover
    源码独立重现。

同时与 Starknet 的"Security Council 即时升级 + 团队 multisig 长 timelock"模型对比，并构建"治理 walkaway
× proving-system gate"的二维分类，回答 key question 4（Walkaway Test 的 Scroll 部分）与 key question 5
（Security Council 组建与维护治理标准）的 Scroll 部分。

- **Priority**: high
- **Dependencies**: item-1, item-5

### item-7: 跨项目对比矩阵 —— Security Council / Exit Window / Walkaway / Proving-System Reproducibility

把前五个项目的事实数据规范化为四张可读的对比表：
(a) **Security Council 配置矩阵**（成员总数、外部成员比例、quorum 阈值、即时升级权限、与团队 multisig 的
权责切分、签名地址是否可公开核对、关键事件历史）；
(b) **Exit Window 设计对比表**（普通升级的 upgrade delay、forced inclusion 是否存在、permissionless
escape hatch 是否存在、用户提款标准延迟、是否依赖 Security Council 的 75% 阈值作为唯一防线、L2Beat 评级
所需的最低窗口对照）；
(c) **Walkaway Test 评估表**（每条 walkaway 检查点 pass / fail：permissionless exit、forced inclusion、
Security Council 是否承担非紧急 liveness / safety 职责、是否存在 Security Council 之外的"绕过"治理路径）；
(d) **Proving-System Reproducibility 矩阵（L2Beat 2026-02-16 新规）** —— 行：5 个项目；列：trusted setup
颜色（red / yellow / green / n.a.）、prover 源码（public / partial / closed）、onchain verifier 可复现
（yes / no）、program commitment 可复现（yes / no）、综合 gate 结论（pass / fail / inconclusive），每
cell 必须可回链到 item-2~item-6 的具体引用。

每个 cell 的数据点都与 item-2~item-6 的事实陈述以引用号回链，避免在矩阵里引入未在分析章节中证明的
新事实。同时输出"哪些维度 ZK Rollup（Starknet / Scroll）与 Optimistic Rollup（Arbitrum / OP / Base）
系统性地不同 / 相同"的差异总结，且把这种差异同时投影到 (i) 治理 walkaway 维度 与 (ii) proving-system
reproducibility 维度，两条线分开陈述。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4, item-5, item-6

### item-8: Mantle 可借鉴经验总结（按相关性排序，含 Proving-System 维度）

把前面所有项目的事实结论投影到 Mantle 当前架构（OP Stack 派生 + ZK Validity Proof 混合证明路径）的语境
下，输出按"对 Mantle Stage 1 推进的直接适用度"排序的借鉴清单：
(1) **OP Stack 共享 fault proof / Dispute Game 基础设施**（OP Mainnet & Base 路径） —— 直接复用的工程
红利与代价（包括 OP Mainnet 任何回滚事件 / Cannon bug 的教训如确有记录），并说明 OP Stack 的 prestate
reproducibility guideline 如何让 Mantle 沿用上游成果直接通过 2026 proving-system gate (4)；
(2) **Base 式独立 Security Council 组建**（10 个外部实体 + 团队双方 + 75% 阈值 + Coordinator 双重门槛）
作为 Mantle Security Council 组建的标准样板；
(3) **Arbitrum BOLD 的 bond 经济模型与"battle royale" 争议协议**，对 Mantle 未来若引入更去中心化的
证明者 / 挑战者集合时的参考意义（bond 大小 = TVL × 一周延迟机会成本 + 利息补偿）；
(4) **ZK 项目治理 walkaway 反面教训**：Starknet SHARP 共享 verifier 的多链耦合风险、Scroll 提议解散
Security Council 的去中心化倒退、以及两者共有的"walkaway 失败 = 团队 multisig 与 Security Council 并行
控制路径"反模式；
(5) **ZK 项目 proving-system reproducibility 教训（2026 新规）**：将 Starknet / Scroll 的 verifier 源码、
trusted-setup 评级、program commitment 复现状态作为 Mantle ZK Validity Proof 路径的直接对标 ——
Mantle 在引入 ZK Validity Proof 时必须明确：使用哪条 prover 工具链、是否依赖被 L2Beat 标 red 的 trusted
setup、verifier 合约是否提供"从公开源码独立重新生成 bytecode"的指引、program / batch commitment 是否能
被第三方独立重现；并对照 Matter Labs Boojum / Polygon zkProver / ZK Stack / OP Stack prestate 工具链等
合规样本，给出 Mantle ZK 路径的最小满足清单；
(6) **Mantle 作为 OP Stack + ZK Validity Proof 混合架构的特殊性**：可同时借鉴 OP Stack 的 fault proof
Stage 1 路径与 ZK Rollup 的 validity proof permissionless 优势，但需要避免 Starknet / Scroll 在 (4) 治理
walkaway 与 (5) proving-system reproducibility 两条维度上踩过的同类型坑。

每条经验都要给出"Mantle 当前状态 → Stage 1 所需变更"的具体落地映射，并在不能在公开来源里直接确认 Mantle
当前配置时显式标注 "Mantle 现状待 stage1-roadmap-recommendation 子课题确认"。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| high_level_summary | 该 item 的 2-4 句 high-level 概括，作为最终章节首段素材 | all |
| stage1_path_timeline | 该项目达到 Stage 1 的关键里程碑时间线（fault proof / validity proof 上线、Security Council 组建、L2Beat 状态变化、相关 governance proposal 通过时间），按 ISO 日期与对应 commit / proposal / blog 引用列出 | item-2, item-3, item-4, item-5, item-6 |
| proof_system_design | 该项目证明系统的关键设计：proof 类型（Optimistic fault proof / ZK validity proof / STARK）、permissionless 提交是否可用、challenge window / proof submission window、争议协议（1-vs-1 vs battle royale）、proof verifier 是否专属或共享、可观测的 verifier 合约地址。**必须同时记录 prover / verifier 源码仓库可见性（public / partial / closed）与"从公开源码独立重新生成 verifier bytecode / WASM module root / prestate hash"是否有官方 documented 路径**，并把这些事实直接喂给 `proof_system_reproducibility_and_trusted_setup` 字段做 gate 判定 | item-2, item-3, item-4, item-5, item-6 |
| proof_system_reproducibility_and_trusted_setup | **(round 2 新增)** 基于 L2Beat 2026-02-16 "New Stage 1 Requirements for L2 Proving Systems" 的四条 gate 判定：(1) trusted setup 评级（red / yellow / green / n.a.，必须给出依据，例如 STARK = n.a.、Scroll KZG = 引用 L2Beat trusted setups 评级页或同类公开评估）；(2) prover 源码公开度（public / partial / closed，含豁免说明：若 prover 由 assumed-honest minority 担任，给出 L2Beat 公告中该豁免条款的引用）；(3) onchain verifier 可复现性（是否存在公开的"从源码独立重新生成 verifier bytecode"指引，参考合规样本：Matter Labs Boojum / Polygon zkProver / ZK Stack）；(4) program commitment 可复现性（ZK program hash / OP prestate hash / Arbitrum WASM module root 等是否可由公开 program 源码独立重现）。每条 gate 单独给出 pass / fail / inconclusive 与引用链接；未找到证据时必须使用 "evidence not found" 而非默认 pass 或 fail | item-2, item-3, item-4, item-5, item-6, item-7, item-8 |
| security_council_config | Security Council 的具体配置：成员总数、外部成员数、成员选择标准（地理分布、独立性要求）、quorum 阈值（绝对人数和百分比都需要给出，例如 9/12 = 75%）、即时升级权限范围、与团队 multisig 的并行 / 串行关系、签名地址是否可在链上核对 | item-2, item-3, item-4, item-5, item-6 |
| exit_window_design | Exit window 设计：常规升级的 upgrade delay（如有）、forced inclusion 机制（是否存在、由谁触发、最长延迟）、permissionless escape hatch（用户能否绕开 operator 直接 finalize 提款）、用户提款标准延迟（fault proof window / validity proof finality）、是否依赖 Security Council 阈值作为唯一防线、**与 L2Beat 三类阈值分别对照**：(i) Stage 1 升级 exit window 最低值（自 2026-04-30 起为 ≥ 5 天，原为 ≥ 7 天）、(ii) optimistic challenge period 最低值（自 2026-04-30 起为 ≥ 5 天）、(iii) Stage 2 unwanted-upgrade exit window 最低值（≥ 30 天，2026-04-30 未变）。draft 须明确每个项目当前配置落在哪一档，并标注 7d→5d 更新前后的合规判定差异（若 7d 时代仍合规、5d 时代仍合规则注明"两版均合规"；若仅 5d 时代合规须显式标注） | item-2, item-3, item-4, item-5, item-6, item-7 |
| walkaway_test_evaluation | Walkaway Test 评估：本项目在每条检查点（permissionless exit、forced inclusion、Security Council 是否承担非紧急 liveness / safety、是否存在 Security Council 之外的绕过路径）上的 pass / fail，并给出最关键的失败点（如有）；如未通过，给出最小修复路径假设。**与 `proof_system_reproducibility_and_trusted_setup` 字段独立判定，但综合判定时需说明任一组失败均阻碍 Stage 1。** | item-2, item-3, item-4, item-5, item-6, item-7 |
| key_incidents_and_lessons | 项目 Stage 1 路径中可记录的工程 / 治理事件：bug / rollback、proposal 争议、L2Beat 状态变化等。**如未在公开来源（governance forum、Optimism Upgrade / Base / Scroll 公告、L2Beat 状态历史）中找到具体事件，必须显式标注 "no documented post-launch incident found"，禁止伪造事件或夸大风险** | item-2, item-3, item-4, item-5, item-6 |
| governance_upgrade_authority | 合约升级权限链：从 ProxyAdmin / Timelock / Security Council / Team Multisig / Coordinator 一直到根权限的拓扑（建议在 draft 中以图表 + 引用 commit / 合约地址呈现），需明确每条边的 delay 与签名阈值。链上证据必须由 `references` 中的 L2Beat Discovery diff / Etherscan / Arbiscan / Starkscan / Scrollscan 合约页直接对应 | item-2, item-3, item-4, item-5, item-6 |
| mantle_applicability | 该项目经验对 Mantle（OP Stack 派生 + ZK Validity Proof 混合架构）的直接适用度（高 / 中 / 低）与适配方式：哪些机制可直接复用、哪些需要改造、哪些是反面教训需要避免；**必须分别给出"治理 walkaway 维度"与"proving-system gate 维度"两条独立适配建议** | item-2, item-3, item-4, item-5, item-6, item-8 |
| references | 引用清单，按强制四桶组织（详见 Source Requirements src-7）：(1) 该项目的 L2Beat 项目页快照（含抓取日期）；(2) 该项目至少 1 条官方文档 / 官方博客 / governance forum 帖；(3) 该项目至少 1 条 on-chain Discovery / Etherscan / Arbiscan / Starkscan / Scrollscan 截图或链接，覆盖 Security Council、Timelock、ProxyAdmin、Verifier、Proposer / Validator 角色；(4) 该项目至少 1 份审计报告或显式 "no public audit report found for {project}" 标注。每条记录 URL + 标题 + 抓取日期 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | timeline | 五个项目达成 Stage 1 关键里程碑的时间线对比（横轴时间，纵轴项目）：标注 fault proof / validity proof 上线、Security Council 组建、L2Beat Stage 1 evaluation 时间、关键 governance proposal 通过、以及 L2Beat 2026-02-16 proving-system 新规发布点等节点，所有时间点必须能在 stage1_path_timeline 字段中找到对应引用 | mermaid | item-2, item-3, item-4, item-5, item-6 |
| diag-2 | comparison | Security Council 配置对比矩阵（项目 × 维度），每行一个项目（Arbitrum / OP / Base / Starknet / Scroll），列包括 总人数 / 外部成员数 / quorum 阈值 / 即时升级权限 / 与团队 multisig 关系 / walkaway 评估结果 | mermaid | item-7 |
| diag-3 | flow | Walkaway Test 决策树：从用户视角出发的 "Security Council 走开后还能否在 operator 作恶下退出" 检查流程（permissionless exit 可用？→ forced inclusion 可用？→ 是否存在 Security Council 之外的治理绕过？→ ZK / Optimistic 路径差异分支），叶节点标注哪些项目落到每个 pass / fail 分支 | mermaid | item-1, item-7 |
| diag-4 | comparison | **(round 2 修订)** ZK vs Optimistic Rollup Stage 1 双维度差异图 —— 用一个二维矩阵分离两条独立失败模式：x 轴 = governance walkaway（pass / fail）、y 轴 = proving-system reproducibility gate（pass / fail / inconclusive）。把 Arbitrum / OP / Base / Starknet / Scroll / Mantle（预估位置）按事实定位到四象限之一，分别在 ZK（Starknet, Scroll）与 Optimistic（Arbitrum, OP, Base）的分组内做高亮，明确"proving-system reproducibility 与 governance walkaway 是两条独立失败维度，任一失败都阻碍 Stage 1"的结论；并在图例中列出每个项目落点对应的最关键证据引用号 | mermaid | item-1, item-5, item-6, item-7 |
| diag-5 | hierarchy | Mantle 借鉴经验优先级金字塔：自顶向下按 mantle_applicability 排序，分层标注每个借鉴来源（OP Stack Base 模式 → Security Council 组建 → BOLD bond 经济 → ZK 项目治理 walkaway 反面教训 → ZK 项目 proving-system reproducibility 反面教训），并标注每层"Mantle 当前状态 → Stage 1 所需变更"的概括 | mermaid | item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | L2Beat 各项目页快照与 Glossary（Arbitrum One、OP Mainnet、Base、Starknet、Scroll；每个项目页都需要至少一次直接引用，并记录抓取日期）；L2Beat Stages 总览页 / 当前 Stages Framework 页面（须为 2026-04-30 之后版本，覆盖 ≥75% 共识阈值与 5 天最低 exit / challenge period 表述）与 Stage 1 walkaway test 论坛帖；L2Beat 2026-02-16 "New Stage 1 Requirements for L2 Proving Systems" 论坛帖 (https://forum.l2beat.com/t/new-stage-1-requirements-for-l2-proving-systems/413)；L2Beat 2026-04-30 "Stage 1 update: minimum challenge period reduction from 7d to 5d" 论坛帖 (https://forum.l2beat.com/t/stage-1-update-minimum-challenge-period-reduction-from-7d-to-5d/425)；以及 L2Beat trusted setups 评级页 | 10 |
| src-2 | official_docs | 各项目官方协议文档：Arbitrum BOLD（gentle-introduction、bold-economics-of-disputes、bold-technical-deep-dive、bold-adoption-for-arbitrum-chains）、OP Stack Stage 1 specs（specs.optimism.io/protocol/stage-1.html）、Optimism Cannon docs 与 op-program prestate guidelines、Base Security Council docs、Starknet 协议 docs（含 SHARP / Stone / Stwo 仓库说明）、Scroll docs（ScrollOwner / Timelock 结构、scroll-prover / aggregator 仓库说明） | 9 |
| src-3 | governance_proposals | 关键 governance proposal 与 forum 帖：Arbitrum AIP BOLD permissionless validation、Optimism Upgrade 16（Interop Contracts + Stage 1 + Go 1.23 Cannon）、Base Stage 1 / Security Council 上线公告、Scroll 解散 Security Council 提案及社区反对帖、Starknet 治理结构相关帖 | 5 |
| src-4 | industry_reports | L2Beat / Luca Donno 关于 Stages framework 演进的 Medium 文章（Introducing Stages、Stages update: Security Council requirements、Proving-System Stage 1 requirements 解读）；以及对 Matter Labs Boojum / Polygon zkProver / ZK Stack 等"合规样本"的独立技术解读；其他独立分析（如 Hacken Fault Proofs 101、The Block / CryptoSlate / Cointelegraph 对 Stage 1 milestone 的报道作为时间线 cross-check） | 4 |
| src-5 | audit_reports | **每个项目（Arbitrum / OP / Base / Starknet / Scroll）必须至少 1 份与 fault proof / validity proof / 治理合约相关的公开审计报告（如 Trail of Bits / Cantina / Sigma Prime 对 OP Stack fault proof / Cannon / Starknet 合约 / Scroll zkEVM 的审计；BOLD 相关安全报告）。若任一项目未公开对应审计报告则必须在 draft 中显式标注 "no public audit report found for {project}"，禁止伪造引用** | 5 |
| src-6 | on_chain_data | **每个项目（5 个）至少 1 条 on-chain Discovery / Etherscan / Arbiscan / Starkscan / Scrollscan 证据**，覆盖以下角色（缺失角色须显式标注 "evidence not found for {role} on {project}"）：Security Council multisig 合约地址、Timelock 合约地址、ProxyAdmin / ScrollOwner / 主升级根合约地址、Verifier 合约地址（OP MIPS.sol / Arbitrum OSP / Starknet SHARP verifier / Scroll Verifier）、Proposer / Validator bond 合约地址。每条记录 地址 + 当前 owner + 当前 quorum / delay 配置 | 5 |
| src-7 | per_project_evidence_bundle | **(round 2 强化)** 每个项目（共 5 个）在 draft 中必须维持一个独立的"evidence bundle"小节，由四桶证据共同构成：(a) 至少 1 条 L2Beat 项目页快照（src-1）；(b) 至少 1 条官方文档 / 博客 / governance forum 帖（src-2 或 src-3）；(c) 至少 1 条 on-chain Discovery / 区块浏览器证据（src-6），覆盖 Security Council / Timelock / ProxyAdmin / Verifier / Proposer 中至少 3 个角色；(d) 至少 1 份审计报告或显式 "no public audit report found for {project}" 标注（src-5）。**矩阵 cell（item-7）与 Mantle 借鉴结论（item-8）禁止只依赖二手综述、Wikipedia、未引用的博客；任一未覆盖项必须在 draft 中显式列为 gap** | 5 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-1 | 把 L2Beat 2026-02-16 "New Stage 1 Requirements for L2 Proving Systems" 四条 gate（no red trusted setups / published prover source / reproducible onchain verifiers / reproducible program commitments）纳入 Stage 1 评估框架基线，并说明与 walkaway test 独立判定的关系；引用 https://forum.l2beat.com/t/new-stage-1-requirements-for-l2-proving-systems/413 | adversarial-review round 1 finding 1 |
| 2 | modify_item | item-2 | 增加 "Optimistic Proof Reproducibility" 子任务：评估 Arbitrum BOLD OSP / WASM module root 等 program commitment 与 verifier 源码可复现性，按 2026 新规独立给出 pass / fail | adversarial-review round 1 finding 1 |
| 2 | modify_item | item-3 | 增加 OP Stack Cannon / op-program / prestate hash 的 reproducibility 评估子任务，对应 2026 新规 (2)(3)(4) 三条 gate | adversarial-review round 1 finding 1 |
| 2 | modify_item | item-4 | 增加对 Base 继承 OP Stack proving-system gate 的传递性评估（是否存在 Base 私有分支偏离上游） | adversarial-review round 1 finding 1 |
| 2 | modify_item | item-5 | 增加 Starknet STARK / SHARP verifier / Stone-Stwo 工具链的 4 项 gate 单独评估，明确与 walkaway 失败的双轴关系 | adversarial-review round 1 finding 1 |
| 2 | modify_item | item-6 | 增加 Scroll zkEVM KZG / scroll-prover / Verifier / Aggregator Verifier 的 4 项 gate 单独评估 | adversarial-review round 1 finding 1 |
| 2 | modify_item | item-7 | 新增第 (d) 张矩阵：Proving-System Reproducibility 矩阵；并把"治理 walkaway × proving-system gate"的差异作为独立维度陈述 | adversarial-review round 1 finding 1 |
| 2 | modify_item | item-8 | 把 ZK proving-system reproducibility 教训（条目 5）独立列入 Mantle 借鉴优先级清单，并对 OP Stack 上游可继承的 prestate reproducibility 收益做明示 | adversarial-review round 1 finding 1 |
| 2 | add_field | proof_system_reproducibility_and_trusted_setup | 新增字段，承接 L2Beat 2026-02-16 四条 gate 的项目级 pass / fail / inconclusive 判定（含豁免与 "evidence not found" 处理） | adversarial-review round 1 finding 1 |
| 2 | modify_field | proof_system_design | 显式要求记录 prover / verifier 源码可见性与 verifier bytecode / WASM module root / prestate hash 的独立重新生成路径，作为 reproducibility 字段的输入 | adversarial-review round 1 finding 1 |
| 2 | modify_field | walkaway_test_evaluation | 增补"与 proving-system gate 独立判定，但综合判定时任一失败均阻碍 Stage 1" 的说明 | adversarial-review round 1 finding 1 |
| 2 | modify_field | mantle_applicability | 要求分别给出"治理 walkaway 维度"与"proving-system gate 维度"两条独立适配建议 | adversarial-review round 1 finding 1 |
| 2 | modify_field | references | 重新定义引用清单的强制四桶组织（L2Beat snapshot + 官方文档 / 治理 + 链上证据 + 审计或显式 no-report 标注），对应新增 src-7 | adversarial-review round 1 finding 2 |
| 2 | modify_diagram | diag-4 | 由原"ZK vs Optimistic Stage 1 路径差异图"修订为二维矩阵：x 轴 governance walkaway pass/fail × y 轴 proving-system reproducibility pass/fail/inconclusive，定位 5 个项目 + Mantle 预估位置，明确两维度独立 | adversarial-review round 1 finding 1 |
| 2 | modify_diagram | diag-5 | 在 Mantle 借鉴金字塔中新增 "ZK 项目 proving-system reproducibility 反面教训" 层，与原 ZK 治理 walkaway 反面教训层并列 | adversarial-review round 1 finding 1 |
| 2 | modify_source_req | src-1 | 在源清单中显式加入 L2Beat 2026-02-16 proving-system 新规论坛帖与 L2Beat trusted setups 评级页，min_count 7 → 8 | adversarial-review round 1 finding 1 |
| 2 | modify_source_req | src-2 | 补充 op-program prestate guidelines、Starknet Stone / Stwo 仓库说明、scroll-prover / aggregator 仓库说明，min_count 8 → 9 | adversarial-review round 1 finding 1 |
| 2 | modify_source_req | src-3 | governance proposals min_count 4 → 5（要求 5 个项目各至少 1 条） | adversarial-review round 1 finding 2 |
| 2 | modify_source_req | src-4 | industry reports 增补 "Matter Labs Boojum / Polygon zkProver / ZK Stack 合规样本" 独立解读，min_count 3 → 4 | adversarial-review round 1 finding 1 |
| 2 | modify_source_req | src-5 | audit reports min_count 2 → 5（每个项目至少 1 份；缺失项目必须显式标注 "no public audit report found for {project}"） | adversarial-review round 1 finding 2 |
| 2 | modify_source_req | src-6 | on-chain data min_count 1 → 5（每个项目至少 1 条链上证据，覆盖 Security Council / Timelock / ProxyAdmin / Verifier / Proposer 角色，缺失角色显式标注） | adversarial-review round 1 finding 2 |
| 2 | add_source_req | src-7 | 新增"per-project evidence bundle"强制要求：每个项目在 draft 中必须有四桶证据（L2Beat 快照 + 官方文档/治理 + 链上证据 + 审计或显式 no-report 标注），矩阵与结论禁止只依赖二手综述 | adversarial-review round 1 finding 2 |
| 3 | modify_item | item-1 | (A) 治理 / exit window 基线按 L2Beat 2026-04-30 更新重写：把 quorum 共识阈值从 `> 75%` 改为 `≥ 75%`（保留项目特异 quorum 事实如 9/12 = 75%）；把原"Security Council 之外的升级须 ≥ 7 天 exit window、Stage 2 则要求 ≥ 30 天"重写为**三个独立时间窗口分别陈述**：(i) Stage 1 升级 exit window 外 SC ≥ 5 天、(ii) optimistic challenge period ≥ 5 天、(iii) Stage 2 unwanted-upgrade exit window ≥ 30 天；引用 https://forum.l2beat.com/t/stage-1-update-minimum-challenge-period-reduction-from-7d-to-5d/425 | adversarial-review round 2 finding (narrow) |
| 3 | modify_field | exit_window_design | 把"与 L2Beat 最低 7d / 30d 要求的对照"改写为对三档阈值分别对照：(i) Stage 1 升级 exit window ≥ 5d（2026-04-30 由 7d 下调）、(ii) optimistic challenge period ≥ 5d、(iii) Stage 2 unwanted-upgrade exit window ≥ 30d；并要求 draft 显式标注每个项目在 7d 时代 / 5d 时代的合规判定差异 | adversarial-review round 2 finding (narrow) |
| 3 | modify_field | audience | 在 framework 最新细则列表里补充 2026-04-30 5-day 更新链接，避免读者沿用 7d 旧基线 | adversarial-review round 2 finding (narrow) |
| 3 | modify_source_req | src-1 | 把"L2Beat Stages 总览页"明确限定为 2026-04-30 后的当前 Stages Framework 页面；新增 2026-04-30 "Stage 1 update: minimum challenge period reduction from 7d to 5d" 论坛帖 (https://forum.l2beat.com/t/stage-1-update-minimum-challenge-period-reduction-from-7d-to-5d/425) 引用；min_count 8 → 10 | adversarial-review round 2 finding (narrow) |
