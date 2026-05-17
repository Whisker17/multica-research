---
topic: "Base Azul 升级对 Mantle 执行层客户端的影响评估"
project_slug: base-azul-upgrade
topic_slug: mantle-impact-assessment
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: base-azul-upgrade/outlines/mantle-impact-assessment.md
  draft: base-azul-upgrade/research-sections/mantle-impact-assessment/drafts/round-{n}.md
  final: base-azul-upgrade/research-sections/mantle-impact-assessment/final.md
  index: base-azul-upgrade/research-sections/_index.md

scope: |
  在已有四份上游 final（base-strategy-azul-overview / osaka-evm-changes / multiproof-architecture /
  flashblocks-network-changes）的基础上，针对 **Mantle Network 执行层客户端**（当前为 `mantlenetworkio/
  op-geth` + `mantlenetworkio/mantle-v2`，规划中切换至 RETH+REVM）系统化评估 Base Azul 升级的影响。
  覆盖：
  (1) Mantle 现行执行层基线快照——必须显式包含已上线的官方 release 证据（`mantlenetworkio/op-geth`
  v1.4.2 "Mainnet Limb" 2026-01-14、`mantlenetworkio/mantle-v2` v1.5.4 "Mainnet Arsia" 2026-04-22 及
  其引用的 op-geth pin 版本），并对每项 Osaka EIP 显式标记当前在 Mantle 的部署状态
  （`already_live_on_mantle` / `partially_live` / `not_live` / `unknown`）；ZK validity rollup 架构、
  Succinct Proposer + Kona、EigenDA、RETH+REVM 迁移计划继续覆盖；
  (2) Base Azul 各 feature × Mantle 各组件的相关性矩阵——行严格使用 base-strategy-azul-overview §2.4
  的 **13 项 canonical feature ID**（不替换、不合并、不新增），列保持 Mantle 客户端关键组件；每格使用
  5 档新版 applicability_label，并叠加 deployment status 维度；
  (3) 每个"相关"单元的代码级 diff、行为影响、工程投入、前置依赖与替代方案；
  (4) Base 脱离 OP Stack 的三层（代码 fork / spec fork / 治理）对 Mantle 的战略影响——特别是
  `ethereum-optimism/op-geth` 与 `op-program` 在 2026-05-31 EOL（**hard 约束**）与 OP Stack Karst 硬分叉
  只支持 op-reth/kona-client 的强约束；`specs.base.org` 在本 item 与 item-6 作为战略跟踪源出现，不进入
  矩阵行；
  (5) 排序后的升级建议时间线（P0/P1/P2 + 时间窗），锚定 **op-geth EOL 2026-05-31（hard）**、
  **Base Azul mainnet 2026-05-28（code-set / spec-TBD，须以官方公告复核）**、**OP Stack Karst（具体
  时间窗以官方公告为准）** 三条关键日历；行动必须按"verify current Mantle Limb/Arsia behavior"与
  "implement missing Azul-derived features"两条 track 分别列出，避免把已上线特性误标为"待采纳"；
  (6) 上游跟踪策略：Mantle 在 OP Stack 与 Base Stack 两条轨道上的长期 watch/diff/CI 流程建议；
  `specs.base.org` 作为 Base 轨道 spec 源在本 item 详细展开。
  本研究 **不** 覆盖：Mantle DA 层（EigenDA）独立技术演进、Mantle 治理代币经济、Mantle 商务/生态决策，
  也不重复上游四份 final 已逐 EIP / 逐合约展开的实现细节——本主题以"映射 + 评估 + 建议"为主，引用上
  游 final 作为权威证据。
audience: |
  Mantle 协议工程团队（执行层客户端 owner、节点运营团队、证明系统团队、治理决策层）、Multica 研究
  squad 下游 Technical Writer（聚合到最终报告）、关注 OP Stack 与 Base Stack 分裂的 L2 工程研究者。
  读者已熟悉 EVM、OP Stack 基础架构与 ZK rollup 概念；不要求熟悉 base/base Rust 工作区、Reth 节点
  内部 API、Mantle Succinct Proposer / Kona 内部细节——必要时通过上游 final 与代码锚点反查即可。
expected_output: |
  - **基线快照**：Mantle 当前执行层客户端的事实清单——含 `mantlenetworkio/op-geth`、`mantlenetworkio/
    mantle-v2`（**当前主线 consensus/op-node 源**）、可选 `mantlenetworkio/mantle`（仅作为 legacy 参照），
    每个仓库给出 pinned tag / commit / 最近活跃日期；显式列出 `op-geth` v1.4.2 "Mainnet Limb"
    （2026-01-14 主网激活）与 `mantle-v2` v1.5.4 "Mainnet Arsia"（2026-04-22 主网激活，pin op-geth v1.5.4）
    两条 release 的 release-note 引用与 code 锚点；针对 Azul §2.4 的 13 项 feature 逐项给出
    `current_mantle_release_status` 字段（four-valued）+ 证据。proof 系统现状、DA 层整合点、已宣布的
    RETH+REVM 迁移路线引用源于公开仓库、博客、L2BEAT。
  - **完整 Azul × Mantle 相关性矩阵**：以 Base Azul **13 项 canonical feature**（来自
    base-strategy-azul-overview §2.4：EIP-7823 / EIP-7825 / EIP-7883 / EIP-7939 / EIP-7951 / EIP-7642 /
    EIP-7910 / Flashblocks payload simplification / Engine API V5 envelope / Multiproof+AggregateVerifier
    finality / TEE Prover + Prover Registrar / ZK Prover / single-client Base-Reth-Node + base-consensus）
    为行（顺序与 ID 严格对齐 §2.4，不替换、不合并、不新增）、Mantle 客户端关键组件为列；每格 5 档
    applicability_label（`already_live_on_mantle` / `manual_backport_to_legacy_op_geth` /
    `via_op_reth_kona_after_migration` / `base_only_reference` / `not_applicable`）+ 一句话理由 +
    `current_mantle_release_status` 字段 + 上游 final 锚点。`specs.base.org` 不出现在行中，作为 item-4
    与 item-6 的战略跟踪源。
  - **逐单元影响分析**：对矩阵中所有非 `not_applicable` 且非 `already_live_on_mantle` 的单元给出：
    (a) 代码级 diff 计划（必须在 Mantle 仓库中变更的文件 + 符号，或若在 Mantle 未来 RETH+REVM 客户端
    中变更应锚定的 base/base 文件），(b) 行为影响（gas、precompile、payload、wire 协议、RPC schema），
    (c) 工程投入档（trivial / moderate / significant / requires-new-component），(d) 前置依赖
    （OP Stack 上游 fork、Mantle RETH 迁移阶段、第三方组件如 Succinct 网络）。对 `already_live_on_mantle`
    单元只输出"验证 track"条目（见 item-5），不重复 diff 设计。
  - **战略分裂影响评估**：把 Base 三层 fork（代码 / spec / 治理）映射成 Mantle 必须回答的三个决策：
    (i) 客户端栈对齐 Base-Reth-Node 还是 op-reth 还是双栈共存；(ii) spec 跟踪 specs.base.org 还是
    specs.optimism.io；(iii) Mantle Succinct Proposer 是否可与 Base AggregateVerifier (TEE+ZK) 形成
    互补/兼容证据。结论必须以代码、L2BEAT、官方公告锚定，不允许仅以"可考虑"或"建议"收尾。
  - **排序后的升级建议时间线**：至少 10 条 actionable item，按 **verify-track**（验证 Mantle Limb/Arsia
    已上线行为是否与 Azul 一致）与 **adopt-track**（采纳 Mantle 尚未实现的 Azul 衍生特性）两条 track
    分别列出；每条带优先级、时间窗（与 op-geth EOL 2026-05-31 / Azul mainnet 2026-05-28（code-set /
    spec-TBD）/ OP Stack Karst 三个锚点的相对位置）、负责团队、验收标准、风险标签。
  - **上游跟踪策略**：Mantle 双轨 watch 流程的工程化建议——CI diff（监控 base/base、`ethereum-optimism/
    optimism`、`ethereum-optimism/op-geth`、specs.base.org、specs.optimism.io 五条源）、季度 review 节
    奏、特性采纳决策模板（go/no-go 表）。
  - **至少 5 张 Mermaid 图**：相关性 + 部署状态双层热力图、三栈分裂演进图、升级优先级甘特图（双 track）、
    证明系统对比图、双轨上游跟踪流程图。
  - **冲突解决**：若研究过程中发现公开声明与代码实测不一致（例如：Mantle 公告 RETH 切换时间表 vs
    `mantlenetworkio/op-geth` 实际活跃度；Base Azul mainnet date 在代码中为 `1_779_991_200`
    （2026-05-28 18:00 UTC）但 spec 仍标 TBD），draft 必须显式声明冲突、选定权威来源、给出 resolution。
  - **Evidence**：至少引用 (a) 5 份 Mantle 官方源（仓库、release notes、博客、文档、L2BEAT 描述），其中
    `op-geth` v1.4.2 Limb release notes、`mantle-v2` v1.5.4 Arsia release notes 为 **mandatory**；
    (b) 4 份 OP Stack 上游源（包括 op-geth deprecation notice、Karst 公告）；(c) 4 份本项目上游 final
    的具体段落/小节锚点；(d) 1 份 Base 官方源（specs.base.org 或 base/base README）。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-17T08:30:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-17T12:40:00Z"
---

# Research Outline: Base Azul 升级对 Mantle 执行层客户端的影响评估

## Items

### item-1: Mantle 执行层客户端基线快照（截至 2026-05）

建立 Mantle 当前执行层栈的事实底盘——没有这个底盘，所有"影响评估"都无法定锚。本 item 必须以 **已上线
release** 为第一手证据，避免把 Mantle 已经主网激活的 Osaka 特性误判为"待采纳"。

需要给出：
(a) `mantlenetworkio/op-geth`（执行层 Go 实现 fork）——
    - 当前主线 release：**v1.4.2 "Mainnet Limb"，2026-01-14 主网激活**（release notes 锚点 mandatory）；
    - 与 `ethereum-optimism/op-geth` 的 pin 关系；
    - Mantle 特有补丁清单（MetaTX 移除遗留、RIP-7212 引入、deposit / blockheight=blocktime 1:1 等已知差异）；
    - 最近活跃 commit + 与 v1.4.2 tag 的差异；
(b) **`mantlenetworkio/mantle-v2`**（**当前主线 consensus/op-node + op-batcher + op-proposer 源**）——
    - 当前主线 release：**v1.5.4 "Mainnet Arsia"，2026-04-22 主网激活**（release notes 锚点 mandatory，
      包含其引用的 op-geth pin 版本 v1.5.4）；
    - rollup config、hardfork 时间戳、op-geth pin、derivation 与 batcher 流水线；
    - 最近活跃 commit；
    - `mantlenetworkio/mantle`（旧 legacy v1 仓库）**仅作为 legacy 参照**，若与 v2 的当前主线决策有差异
      必须显式声明，否则不进入证据集；
(c) Mantle Succinct Proposer 与 Kona 在证明流水线中的位置（替代原 op-proposer，使用 SP1 zkVM）；
(d) EigenDA 整合点（DA blob 接入、`update configuration` 中按区块高度切换 EigenDA 的设计）；
(e) 已宣布的 RETH+REVM 迁移计划（预计 ~2x 吞吐提升）+ 时间表（官方公开 vs 仓库活跃度交叉验证）；
(f) **针对 base-strategy-azul-overview §2.4 的 13 项 canonical feature 逐项给出 `current_mantle_release_
    status` 字段**——四值（`already_live_on_mantle` / `partially_live` / `not_live` / `unknown`），
    每项附 release tag（如 `op-geth v1.4.2 Limb` 或 `mantle-v2 v1.5.4 Arsia`）、commit、activation
    timestamp、code anchor（具体文件 + 函数 + 行号或 EIP 启用 flag）。本字段是 item-2 与 item-3 的输入，
    缺失任何一项即视为本 item 未完成。

本 item 不展开任何 Azul-specific 评估——只交付 Mantle 的"当前状态"快照，作为后续所有 item 的引用基础。

- **Priority**: high
- **Dependencies**: none

### item-2: Base Azul × Mantle 相关性矩阵

把 Base Azul 升级的全部对外可观察 feature 系统化拆解为一张相关性矩阵。

**行——严格使用 base-strategy-azul-overview §2.4 的 13 项 canonical feature（顺序、ID、命名均与 §2.4 对齐，
不替换、不合并、不新增）**：

1. EIP-7823（modexp input bound）
2. EIP-7825（per-transaction gas cap 16,777,216 / 2^24）
3. EIP-7883（MODEXP gas 三重上调）
4. EIP-7939（CLZ 0x1e opcode）
5. EIP-7951（p256Verify precompile gas 翻倍 / Mantle 已通过 RIP-7212 引入入口）
6. EIP-7642（eth/69 wire 升级，强制状态）
7. EIP-7910（`eth_config` RPC）
8. Flashblocks payload 简化（payload diff、pre-confirmation 路径）
9. Engine API V5 envelope（+V4 payload + `EngineGetPayloadVersion::from_cfg` 时间戳门控）
10. Multiproof / AggregateVerifier finality（合约形态、min(7d, secondProof+1d) 最快取证、PROOF_THRESHOLD=1）
11. TEE Prover + Prover Registrar（DelayedWETH 治理结构、TEE 证明流水线）
12. ZK Prover（Base 的 ZK verifier 接入与 SP1 / 其他 zkVM 路径）
13. single-client Base-Reth-Node + base-consensus（Base 客户端 monorepo + consensus 守护进程）

> **`specs.base.org` 不进入矩阵行**——作为 spec 跟踪源在 item-4（战略决策 2：spec 跟踪源）与 item-6
> （双轨上游跟踪监控源清单）中出现，不参与本 item 的相关性评估。

**列（Mantle 客户端关键组件）**：`mantlenetworkio/op-geth`（执行层）、`mantlenetworkio/mantle-v2` op-node /
op-batcher / op-proposer（共识/derivation/批量提交）、Mantle Succinct Proposer + Kona（ZK 证明流水线）、
EigenDA 适配层、Mantle RETH+REVM 未来客户端、Mantle RPC / wire 节点运营、治理与 spec 跟踪流程。

**每格 5 档 applicability_label（替代旧版四档）**：

- `already_live_on_mantle`——已在 Limb / Arsia 或更早 release 主网激活，证据回链 item-1 的
  `current_mantle_release_status` 字段；
- `manual_backport_to_legacy_op_geth`——目前必须由 Mantle 自行 backport 到 `mantlenetworkio/op-geth`
  fork，因为 `ethereum-optimism/op-geth` 已宣布 2026-05-31 EOL，无法依赖上游同步；
- `via_op_reth_kona_after_migration`——只在 Mantle 完成向 op-reth + kona-client（或 Mantle RETH+REVM）
  迁移后才能透明继承，迁移前不可用；
- `base_only_reference`——Base 独有设计或治理产物，对 Mantle 不直接适用，仅作为参考；
- `not_applicable`——Mantle 已有等价/更优替代，或与 Mantle 架构无关。

**每格附加字段**：(i) 一句话理由；(ii) `current_mantle_release_status`（继承自 item-1）；(iii) 上游
final 锚点（章节号或文件路径）。

矩阵交付物必须是可被 Item 3 直接消费的结构化表，13 行 × 7 列 = **91 个单元，全部必须填齐**。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 逐单元影响分析（"applicable" 单元的代码级与行为级 diff）

对 Item 2 矩阵中所有非 `not_applicable` 且非 `already_live_on_mantle` 的单元逐一展开。每个被分析的单
元至少给出：

**(a) 代码级 diff 计划**——锚定到 Mantle 仓库的具体文件/符号。例如对 Osaka EIP-7825（tx gas limit cap）
应锚定 `mantlenetworkio/op-geth/core/state_transition.go` 与 `params/protocol_params.go`，并交叉引用
osaka-evm-changes final 中给出的 op-geth 上游对应位置；对 EIP-7951 (p256Verify) 应锚定 `core/vm/
contracts.go` 中 Mantle 已通过 RIP-7212 引入的入口、说明 gas 翻倍如何在 Mantle deposit 豁免语义下接入。

**(b) 行为影响**——按维度分类：(i) gas pricing 变化（含历史 worst-case 倍数）、(ii) precompile 调用兼
容性（是否破坏现有合约）、(iii) Engine API / payload schema 是否需要同步（参考 flashblocks-network-
changes final 中 V5 envelope + V4 payload + `EngineGetPayloadVersion::from_cfg` 时间戳门控）、
(iv) wire 协议（eth/69 retrofit 的强制状态）、(v) RPC schema（`eth_config` 的接入策略）。

**(c) 工程投入档**——四档：`trivial`（< 1 周）/ `moderate`（1–4 周）/ `significant`（1–3 月）/
`requires-new-component`（需要新组件，如证明系统接入新 verifier）。每档必须给出至少 1 个判断依据
（代码行数估计、依赖深度、外部服务接入复杂度）。

**(d) 前置依赖**——三类：(i) OP Stack 上游依赖（**op-geth/op-program 2026-05-31 EOL 后无上游同步路径，
必须明确判断"自行 backport"还是"等待 op-reth/kona 迁移"**），(ii) Mantle 内部前置（如 RETH 迁移阶段
是否已就绪、Succinct 网络是否升级），(iii) 第三方组件依赖（如 Succinct SP1 升级到支持 CLZ 的 zkVM 版
本——参考 osaka-evm-changes final 中 CLZ × ZK rv32im 章节）。

本 item 必须按矩阵单元数完整覆盖。任何被标记为 `manual_backport_to_legacy_op_geth` 或
`via_op_reth_kona_after_migration` 但在本 item 未出现的单元都构成 review 失败；`already_live_on_mantle`
单元在本 item 不展开 diff（其行动以 item-5 的 verify-track 形式出现）。

- **Priority**: high
- **Dependencies**: item-2

### item-4: Base 脱离 OP Stack 的三层 fork 对 Mantle 的战略影响

把 base-strategy-azul-overview final 中"Base 脱离 OP Stack"三层假设（代码 fork / spec fork / 治理）映
射成 Mantle 必须回答的三个具体决策。

**决策 1：客户端栈对齐**——Mantle 应在哪条客户端轨道上长期投资？
- 选项 A：保持 op-geth 直到 EOL（**2026-05-31，hard 约束**），然后跟随 OP Stack 主轨道切换到
  op-reth + kona-client；
- 选项 B：直接对齐 Base-Reth-Node（paradigmxyz/reth v1.11.4 + Base 补丁），脱离 OP Stack 客户端轨道；
- 选项 C：双栈并行（op-reth + Base-Reth-Node 各运行一部分节点，作为客户端多样性手段，类比以太坊主网）；
- 选项 D：自研基于 reth/revm 的 Mantle 客户端（与已宣布的 RETH+REVM 计划合流）。
每个选项必须列：技术成本、维护成本、生态对齐成本、退出成本、对 ZK validity rollup 的兼容性影响。

**决策 2：spec 跟踪源**——Mantle 应订阅哪些 spec 源？
- **`specs.base.org`**（Base Azul 之后的权威源，作为战略跟踪源在本决策展开，但**不**进入 item-2 矩阵行）
  + **`specs.optimism.io`**（OP Stack Karst 之后的权威源）的双订阅策略可行性、冲突解决流程（哪边为准）、
  自家 Mantle-specific spec（如 EigenDA、Mantle Succinct Proposer 接口）的发布形式。

**决策 3：proof 系统组合**——Mantle 当前是 SP1-only（Succinct Proposer 单证明），Base 是 TEE+ZK 双证明
聚合（PROOF_THRESHOLD=1，min(7d 创建延迟, secondProof 1d 延迟)）。Mantle 是否应：
- 选项 P1：维持 SP1-only（成本最低，但 Stage 2 仍卡在中心化 validator + 1d timelock）；
- 选项 P2：引入第二证明（TEE 或第二个 ZK 系统）实现 AggregateVerifier 风格的最快取证；
- 选项 P3：评估直接复用 Base AggregateVerifier 合约形态（DelayedWETH、Prover Registrar 等）作为 Mantle
  proof 系统的参照实现。每个选项必须引用 multiproof-architecture final 的具体合约源码位置与门控参数。

输出格式：每个决策提供 1 张选项对比表 + 1 段倾向建议（必须基于事实而非偏好）。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: 排序后的升级建议时间线

把前序 item 的所有结论汇总为 actionable 时间线。至少 10 条 action，按 **verify-track** 与
**adopt-track** 两条 track 分别组织，每条 track 内再按 P0/P1/P2 排序。

**Track 锚点（必须显式标注）**：
- **op-geth EOL 2026-05-31**——`ethereum-optimism/op-geth` + `op-program` 官方 EOL，**hard 约束**；
- **Base Azul mainnet 2026-05-28**——**标注为 "code-set / spec-TBD"**：代码中
  `1_779_991_200`（2026-05-28 18:00 UTC）已 hardcode，但公开 spec 在抓取日期前仍标 TBD。
  在更新到官方公告确认之前，本时间线不得把此日期作为 hard 约束；
- **OP Stack Karst**——具体时间窗以官方公告为准，标注为 "official-pending"。

**verify-track（验证 Mantle Limb / Arsia 已上线的 Azul-aligned 行为是否与 Azul spec 一致；不引入新代码）**：
- 对每个 `already_live_on_mantle` 的 Azul feature，安排回归测试 / 影子节点对账 / 治理通告，确保 Mantle
  的实现与 Azul 主网行为一致（特别是 EIP-7823/7825/7883/7939/7951 的 gas 与边界行为）；
- 验收：影子节点与 Azul 主网相同输入下 24h 无 state diff；任何 diff 必须有 release-note 解释。

**adopt-track（采纳 Mantle 尚未实现的 Azul 衍生特性）**：
- **P0（must-do，由强约束驱动）**：op-geth EOL 2026-05-31、OP Stack Karst 硬分叉、Mantle 现行 ZK proof
  系统的 finality 1h 承诺。例如：
  - "在 2026-05-31 前完成 op-reth 同步与影子运行验证，否则 Karst 后 Mantle 将无法跟随 OP Stack 主轨道"；
  - "评估 Base AggregateVerifier 的 DelayedWETH 路径是否影响 Mantle 现行 1h finality 承诺"；
  - "针对 EIP-7883 MODEXP gas 三重上调（**若在 Mantle Limb/Arsia 中尚未上线**，先到 item-1 复核状态），
    预先识别并通知所有部署在 Mantle 上的 RSA / 大数运算合约"；
  - "针对 EIP-7951 p256Verify gas 翻倍，更新 ERC-4337 paymaster / passkey 钱包 SDK 的 gas 预估表"。
- **P1（应当做，有显著收益）**：例如：
  - "把 EIP-7939 CLZ 引入 Mantle（**若 Limb/Arsia 已上线则降级为 verify-track**），借此优化 Succinct
    SP1 prover 的 rv32im 路径（参考 osaka-evm-changes final 的 CLZ × ZK 章节）"；
  - "采纳 EIP-7642 (eth/69) wire 升级以减少节点带宽"；
  - "暴露 `eth_config` RPC，对齐节点运营生态"。
- **P2（可选/长期）**：例如：
  - "评估 Flashblocks payload 简化思路对 Mantle 排序器的延迟收益（参考 flashblocks-network-changes
    final 的 payload diff 章节）"；
  - "评估 specs.base.org 中关于 Engine API V5 envelope 的设计是否可作为 Mantle 未来 Engine API 演进
    参考"。

每条 action 必须给出：(i) track 归属（verify / adopt）、(ii) 优先级标签、(iii) 时间窗（绝对日期或相对
锚点）、(iv) 负责团队、(v) 验收标准（可测量）、(vi) 风险标签（低 / 中 / 高 / 阻断性）。

输出形式：1 张主时间线表（含 track 列）+ 1 张 Mermaid 甘特图（diag-3，双 track 分区）。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: 双轨上游跟踪策略与工程化建议

针对 Mantle 现状（OP Stack derivative）与未来（可能向 Base/RETH 部分对齐）的双轨现实，给出工程化跟踪
流程建议。覆盖：

**(a) 监控源清单**——五条权威源 + 各自变更类型：
- `ethereum-optimism/optimism`（rollup config、hardfork 时间戳、op-geth pin）；
- `ethereum-optimism/op-geth`（执行层 Go 实现，已宣告 EOL 2026-05-31）；
- `base/base`（Base 客户端 monorepo，crates/common, crates/execution）；
- **`specs.base.org`（Base spec，作为战略跟踪源；不进入 item-2 矩阵行）**；
- `specs.optimism.io`（OP Stack spec）。

**(b) CI diff-watch 流程**——给出最小可行实现示例：每条源的 webhook / cron 监听、变更分类 bot、issue
自动创建模板（包含变更类型、关联 EIP、初判优先级）。

**(c) 季度 review 节奏**——Mantle 内部决策会议节奏建议、go/no-go 决策模板（特性名、影响评估、投入估
计、决策、负责人、deadline），并示范一个用 Azul 实际特性走完决策模板的样本案例。

**(d) Mantle 自身 spec 发布建议**——基于 Base specs.base.org 与 OP Stack specs.optimism.io 的双源经验，
建议 Mantle 是否值得建立 specs.mantle.xyz（或等价物），用于固化 Mantle-only 设计（EigenDA、Mantle
Succinct Proposer 接口、Mantle hardfork timestamps）。

- **Priority**: medium
- **Dependencies**: item-4, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| baseline_facts | Mantle 现行客户端的事实清单：仓库 + pinned tag/SHA + 已知特殊补丁 + 活跃度（最近 commit 日期） | item-1 |
| current_mantle_release_status | 针对每个 Azul §2.4 feature，标记 Mantle 当前部署状态：`already_live_on_mantle` / `partially_live` / `not_live` / `unknown`；附 release tag（如 `op-geth v1.4.2 Limb` / `mantle-v2 v1.5.4 Arsia`）、commit、activation timestamp、code anchor（文件 + 函数 / EIP 启用 flag）。本字段是 item-2 与 item-3 的输入。 | item-1, item-2, item-3 |
| azul_feature_id | Base Azul 单个 feature 的稳定标识：必须取自 base-strategy-azul-overview §2.4 的 13 项 canonical 列表（EIP-7823 / 7825 / 7883 / 7939 / 7951 / 7642 / 7910 / Flashblocks payload / Engine API V5 / Multiproof+AggregateVerifier / TEE Prover+Prover Registrar / ZK Prover / Base-Reth-Node+base-consensus）；不允许使用其他 ID 集 | item-2, item-3 |
| mantle_component | Mantle 客户端栈中对应组件的稳定标识：repo（`mantlenetworkio/op-geth` / `mantlenetworkio/mantle-v2` / 等）+ 子目录 + 文件 + 关键符号 | item-2, item-3, item-5 |
| applicability_label | 五档相关性标签：`already_live_on_mantle` / `manual_backport_to_legacy_op_geth` / `via_op_reth_kona_after_migration` / `base_only_reference` / `not_applicable`；不允许使用旧版 `transitively_via_op_stack`（被拆分以暴露 op-geth EOL 约束） | item-2 |
| upstream_final_anchor | 上游本项目 final 的具体锚点：文件路径 + 章节号或代码块行号，用于证据回链 | item-2, item-3, item-4 |
| code_paths_in_mantle | 实际需要在 Mantle 仓库中修改的文件/符号路径，或在 Mantle 未来 RETH+REVM 客户端中应对齐的 base/base 路径 | item-3, item-5 |
| behavior_impact_dimensions | 行为影响按维度分类：gas / precompile 兼容 / Engine API / wire / RPC schema / proof system | item-3 |
| engineering_effort_tier | 工程投入档：trivial / moderate / significant / requires-new-component，须给出判断依据 | item-3, item-5 |
| prerequisite_dependencies | 三类前置依赖：OP Stack 上游、Mantle 内部、第三方组件 | item-3, item-5 |
| strategic_decision_options | 战略选项枚举（决策 1/2/3 的所有子选项）+ 各选项的成本/收益/风险 | item-4 |
| track_assignment | 行动 track 归属：`verify-track`（验证 Mantle 已上线行为是否与 Azul 一致）/ `adopt-track`（采纳 Mantle 尚未实现的特性）；必须能映射回 `current_mantle_release_status` | item-5 |
| priority_tier | 行动优先级 P0/P1/P2，必须给出绑定到具体强约束的理由 | item-5 |
| time_window | 行动时间窗：绝对日期或相对锚点（"op-geth EOL -1m"、"Azul mainnet -2w（code-set / spec-TBD）"、"Karst -1m（official-pending）"），且必须可被时间线甘特图消费 | item-5 |
| owner_team | 行动负责团队：执行层客户端 / 共识 / 证明系统 / DevOps / 治理 / 多团队协同 | item-5 |
| acceptance_criteria | 行动可测量的完成标准（影子节点 24h 无 diff、SDK gas 估算表全网推送、合约通告完成 100 个高 TVL 项目等） | item-5 |
| risk_label | 行动风险等级：低 / 中 / 高 / 阻断性；每条必须给出具体风险情景 | item-5 |
| tracking_source | 上游跟踪源：repo / spec URL / 发布渠道；每条须配变更类型（rollup config / EVM 代码 / spec 章节） | item-6 |
| source_conflicts_and_resolution | 列出研究过程中发现的 primary source 冲突（例如：Base Azul mainnet date 代码常量 vs spec-TBD；Mantle 官方公告时间表 vs 仓库活跃度），并选定权威来源 + 给出证据；无冲突时记录 "no conflict observed" | all-if-encountered |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Base Azul × Mantle 相关性 + 部署状态双层热力图：**13 项 Azul §2.4 canonical feature 行** × 7 个 Mantle 组件列；色块表示 5 档 `applicability_label`，每格叠加一个状态标记（✓=`already_live_on_mantle` / ↻=`partially_live` / ✗=`not_live` / ?=`unknown`，源自 `current_mantle_release_status`），让"已上线 + 高相关"与"未上线 + 高相关"在视觉上严格区分；每格附 final 锚点文件路径作为脚注 | mermaid | item-2 |
| diag-2 | architecture | 三栈分裂演进图：OP Stack 主轨道（op-geth → op-reth + kona-client，Karst 起强制）vs Base Stack（Base-Reth-Node，Reth v1.11.4 + Base 补丁）vs Mantle 当前栈（`mantlenetworkio/op-geth` v1.4.2 Limb + `mantlenetworkio/mantle-v2` v1.5.4 Arsia）+ Mantle 未来栈（RETH+REVM），标注共同祖先、fork 点、EOL 节点 | mermaid | item-1, item-4 |
| diag-3 | timeline | 升级优先级甘特图：横轴 2026 Q2 → 2027 Q1，纵轴 verify-track + adopt-track 两条分区（每条 track 内再按 P0/P1/P2 排序）；锚点 **op-geth EOL 2026-05-31（hard）**、**Azul mainnet 2026-05-28（code-set / spec-TBD）**、**OP Stack Karst（official-pending）**；每条 action 展示开始/结束、track 归属、依赖箭头、负责团队；甘特图标题与图例必须显式说明 "code-set / spec-TBD" 与 "official-pending" 两类软约束的语义 | mermaid | item-5 |
| diag-4 | comparison | 证明系统对比图：Mantle Succinct Proposer + SP1 + Kona（单证明、1h finality）vs Base AggregateVerifier(TEE+ZK) + DelayedWETH + Prover Registrar（PROOF_THRESHOLD=1，min(7d, secondProof+1d) 最快取证）；标注共用技术栈（SP1）与分歧组件 | mermaid | item-4 |
| diag-5 | flow | 双轨上游跟踪流程图：五条源（base/base, optimism, op-geth, specs.base.org, specs.optimism.io）→ webhook/cron 监听 → diff bot → 变更分类（rollup config / EVM 代码 / spec 章节）→ Mantle 内部 issue 自动创建 → 季度 review go/no-go → 实施 / 跟踪 / 拒绝三分支 | mermaid | item-6 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | Mantle 仓库公开源（minimum，不可省略）：(a) `mantlenetworkio/op-geth` —— **必须锚定到 v1.4.2 "Mainnet Limb" tag**（2026-01-14 主网激活），含 release notes 引用 + 至少 1 处代码锚点（如 chain config / EIP 启用 flag / Mantle-specific 补丁）；(b) `mantlenetworkio/mantle-v2` —— **必须锚定到 v1.5.4 "Mainnet Arsia" tag**（2026-04-22 主网激活，pin op-geth v1.5.4），含 release notes 引用 + 至少 1 处代码锚点（rollup config / op-node derivation / hardfork 时间戳）；(c) `mantlenetworkio/mantle`（legacy v1）仅在与 v2 存在差异时引用，否则不进入证据集。**总计至少 2 个 mandatory release-note 锚点 + 3 个代码锚点。** | 3 |
| src-2 | official_docs | Mantle 官方 release notes 与文档（minimum，不可省略）：(a) **`mantlenetworkio/op-geth` v1.4.2 "Mainnet Limb" release notes**（mandatory，作为已上线 Osaka 特性的第一手证据）；(b) **`mantlenetworkio/mantle-v2` v1.5.4 "Mainnet Arsia" release notes**（mandatory，作为已上线 op-node / batcher / proposer 行为的第一手证据）；(c) Mantle v2 Tectonic upgrade 公告 / Mantle Succinct Proposer + SP1 集成公告 / RETH+REVM 客户端迁移路线图 / EigenDA 整合说明，至少 2 篇。**前两项 release notes 为强制最小要求，不是可选背景。** | 4 |
| src-3 | official_docs | OP Stack 上游公告：op-geth/op-program deprecation notice（2026-05-31 EOL）、Karst 硬分叉计划、Isthmus/Holocene 历史 release notes、Upgrade 19 公告 | 3 |
| src-4 | upstream_final | 本项目上游 final 锚点：base-strategy-azul-overview final（**§2.4 13 项 canonical feature 列表 mandatory** + "Base 脱离 OP Stack" 三层假设）、osaka-evm-changes final（逐 EIP 实现 + `mantle_replication_notes` + G-6 gap）、multiproof-architecture final（AggregateVerifier / TEE / ZK / DelayedWETH / Prover Registrar 合约源码位置 + 门控参数）、flashblocks-network-changes final（payload 简化 + Engine API V5+V4 + eth/69 + eth_config） | 4 |
| src-5 | official_docs | Base 官方源：specs.base.org（Azul spec 章节，**含 Base Azul mainnet date 的官方表述以核验 code-set / spec-TBD 冲突**）、base/base README、Base-Reth-Node 仓库说明 | 2 |
| src-6 | industry_reports | L2BEAT Mantle 当前状态描述（Stage 阶段、validator 配置、timelock 时长）、Messari State of OP Stack Q1 2026、Mantle Op-Geth Audit（OpenZeppelin）等第三方评估 | 2 |
| src-7 | expert_commentary | Mantle / Succinct / Base / OP Labs 工程师公开评论（博客、Discord 公开记录、Ethereum Magicians 帖、PEEPanEIP 录像、conference talk）至少 1 条，用于核验官方公告与实际工程进度的对齐 | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-1 | 把 `mantlenetworkio/mantle-v2` 上升为当前主线 consensus/op-node 源；强制要求 `op-geth` v1.4.2 "Mainnet Limb"（2026-01-14）与 `mantle-v2` v1.5.4 "Mainnet Arsia"（2026-04-22）release-note 锚点；新增对 §2.4 13 项 feature 逐项给出 `current_mantle_release_status` 的硬性输出要求，防止把已上线特性误判为"待采纳" | Adversarial review round-1 finding 1 |
| 2 | modify_item | item-2 | 行集合改为 base-strategy-azul-overview §2.4 的 13 项 canonical feature ID（顺序、命名严格对齐），移除 `specs.base.org` 行（迁至 item-4/item-6 战略跟踪源），proof 系统细分为 AggregateVerifier finality / TEE Prover+Prover Registrar / ZK Prover 三行，新增 Base-Reth-Node + base-consensus 行；每格新增 `current_mantle_release_status` 维度 | Adversarial review round-1 finding 2 |
| 2 | add_field | current_mantle_release_status | 新增字段，四值（`already_live_on_mantle` / `partially_live` / `not_live` / `unknown`），附 release tag、commit、activation timestamp、code anchor；作为 item-2 矩阵与 item-3 diff 计划的输入，避免对已上线特性重复"采纳"建议 | Adversarial review round-1 patch proposal 3 |
| 2 | modify_field | applicability_label | 从旧版四档（`directly_applicable` / `transitively_via_op_stack` / `strategically_relevant` / `not_applicable`）拆分为五档（`already_live_on_mantle` / `manual_backport_to_legacy_op_geth` / `via_op_reth_kona_after_migration` / `base_only_reference` / `not_applicable`），暴露 op-geth EOL 约束并区分已上线 / 待 backport / 待迁移 / 仅参考 / 不适用 | Adversarial review round-1 patch proposal 4 |
| 2 | modify_diagram | diag-1 | 热力图叠加部署状态维度：5 档 applicability 色块 + 4 值 deployment status 标记（✓ / ↻ / ✗ / ?），让"已上线 + 高相关"与"未上线 + 高相关"在视觉上严格区分 | Adversarial review round-1 patch proposal 5 |
| 2 | modify_item | item-5 | 行动按 verify-track（验证 Mantle Limb/Arsia 已上线行为）与 adopt-track（采纳 Mantle 尚未实现的特性）双 track 分列；op-geth EOL 2026-05-31 保留为 hard 锚点，Azul mainnet 2026-05-28 标注为 "code-set / spec-TBD"，Karst 标注为 "official-pending"；新增 `track_assignment` 字段并修订 `time_window` 描述以反映软约束语义 | Adversarial review round-1 patch proposal 6 |
| 2 | modify_diagram | diag-3 | 甘特图分区为 verify-track / adopt-track 双轨；锚点标签显式区分 hard / code-set / spec-TBD / official-pending 四种约束语义；图例必须解释这些标签 | Adversarial review round-1 patch proposal 6 |
| 2 | modify_source_req | src-1 | 强制要求 `mantlenetworkio/op-geth` v1.4.2 Limb tag 与 `mantlenetworkio/mantle-v2` v1.5.4 Arsia tag 各至少 1 处代码锚点；提升为 minimum source requirement | Adversarial review round-1 patch proposal 7 |
| 2 | modify_source_req | src-2 | 强制要求 `op-geth` v1.4.2 Limb 与 `mantle-v2` v1.5.4 Arsia 官方 release notes 两篇均纳入 mandatory 集合，不再视为可选背景 | Adversarial review round-1 patch proposal 7 |
