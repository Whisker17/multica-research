---
topic: "zkSync 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-zksync"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/competitor-zksync.md"
  draft: "202606-internal-sharing/research-sections/competitor-zksync/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/competitor-zksync/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  按用户更新后的数据驱动三步法重做 zkSync 近期开发与叙事分析。第一步必须扫描
  `matter-labs`、`zkSync-Community-Hub` 以及发现的相关 org（本 outline 预扫描到
  `zksync-sdk`、`zksync-association`、`zksync`），覆盖全部可见 repo，按
  2026-02-23 至 2026-05-23 的 PR 数量、merged PR、commit 频率、contributor 活跃度、
  pushed/release 等指标排序，数据驱动筛选 Top 活跃 repo；不得预设 `zksync-era`
  是唯一或主要分析对象。第二步只针对筛选出的活跃 repo 做 PR 活动分析、开发方向分类、
  重大功能变更和活跃度趋势。第三步结合 GitHub 活动和公开信息分析 ZKsync 近期叙事变化、
  生态战略调整、竞品差异化和对 Mantle 的竞争启示。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、Mantle 协议/客户端/基础设施工程师、
  生态与战略团队，以及 Multica Research Squad 的 Review Agent。读者熟悉 L2、ZK Rollup、
  ZK Stack、validium/volition、account abstraction、prover 和 appchain 叙事，但需要一份
  不预设主仓、以近 3 个月公开开发活动为事实底座的 zkSync 竞争近况分析。

expected_output: |
  一份中文结构化 research section，涵盖：
  - zkSync 相关 org/repo 的近 3 个月活跃度数据集、排序方法、Top 活跃 repo 概况和筛选理由；
  - Top 活跃 repo 的 PR 活动分类、开发重点变化、重大功能/架构调整和开发节奏变化；
  - ZKsync 近期叙事演变：ZKsync OS、Airbender、Era compatibility/API、contracts/Gateway、
    Prividium/enterprise validium、developer tooling、account abstraction/SSO 等方向；
  - 与 Optimism/Base/Arbitrum/Sui/enterprise private-chain 方案的差异化定位；
  - 对 Mantle 的竞争启示：应跟踪的技术路线、可借鉴设计、不可照搬边界、短中长期行动建议；
  - 至少 5 个表/图：org/repo universe 表、活跃 repo 排名表、Top repo PR 分类矩阵、
    开发/叙事时间线、ZKsync vs Mantle/OP Stack/Arbitrum 对比矩阵。

source_requirements_summary: |
  Deep phase 必须优先使用 primary source。GitHub 活动需直接查询 GitHub REST/GraphQL/gh CLI：
  org repo 列表、PR created/merged/open/closed、commit、contributor、release/tag、touched files、
  PR body/diff 和 representative commits。必须记录查询时间、窗口边界、查询语句、分页完整性、
  GitHub Search 1000-result cap 的规避方式、rate-limit caveat、bot/renovate/dependabot 去噪规则、
  archived/fork/private 不可见处理方式。叙事分析优先引用 ZKsync 官方 docs/blog、Matter Labs GitHub、
  ZKsync Association/Governance、release notes、security/audit docs、生态项目官方资料。二手媒体、
  X/Twitter、社区帖和 PR Tracker 只能作为辅助信号，关键结论必须回链到 primary source。

methodology_gate:
  repo_discovery_first: true
  prohibition: "不得预设 zksync-era 为唯一或主要分析对象；不得在完成 org-wide repo 活跃度排序前决定最终深挖 repo 列表。"
  time_window: "2026-02-23 至 2026-05-23"
  required_section: "Step 1: 活跃 Repo 发现与排序"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-24T00:26:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-24T00:26:00+08:00"

multica_issue_id: "6c75749c-a82f-4264-aa07-3aeb6a758bbd"
branch_name: "research/202606-internal-sharing/competitor-zksync"
base_commit: "7af231e59f7f310c1d10de469bc4d151fcb4d4e8"
language: "中文"
research_depth: "standard"

prerequisite_sections:
  - slug: competitor-optimism
    path: 202606-internal-sharing/research-sections/competitor-optimism/final.md
    status: existing-research-if-present-on-main
  - slug: competitor-arbitrum
    path: 202606-internal-sharing/research-sections/competitor-arbitrum/final.md
    status: existing-research-if-present-on-main
  - slug: competitor-sui
    path: 202606-internal-sharing/research-sections/competitor-sui/final.md
    status: existing-research-if-present-on-main
  - slug: competitor-base
    path: 202606-internal-sharing/research-sections/competitor-base/final.md
    status: existing-research-if-present-on-main
  - slug: enterprise-canton
    path: 202606-internal-sharing/research-sections/enterprise-canton/final.md
    status: existing-research
  - slug: enterprise-privacy
    path: 202606-internal-sharing/research-sections/enterprise-privacy/final.md
    status: existing-research
---

# Research Outline: zkSync 近期开发与叙事分析

## Methodology Gate

Deep draft 开始前必须先完成 `Step 1: 活跃 Repo 发现与排序`，并把 repo universe、排序公式、候选 Top repo 和排除理由写入草稿第一部分。只有在活跃度排名表完成后，才能决定后续 PR 深挖对象。

硬性要求：

- 扫描 `matter-labs`、`zkSync-Community-Hub` 全部公开 repo，并纳入本 outline 预扫描发现的 `zksync-sdk`、`zksync-association`、`zksync` 作为相关 org 候选；如 deep phase 发现更多官方/半官方 org，必须说明发现路径和纳入/排除理由。
- 对 archived、fork、mirror、template、docs/website、SDK、app、infra、compiler、proof system、contracts、governance/community 类 repo 分别标注类型。
- 时间窗口固定为 2026-02-23 至 2026-05-23，所有 GitHub 查询必须说明 UTC 边界是否含首尾日。
- 排序维度至少包含 PR created、merged PR、commit count、active PR authors/contributors、release/tag 或 default-branch push recency。建议权重：PR created 35%、merged PR 25%、commit count 20%、active contributors 15%、release/push recency 5%。如 deep phase 调整权重，必须解释。
- 必须提供敏感性检查：PR-only、commit-only、contributors-only 三种排名是否改变 Top repo 选择。
- 若 `matter-labs/zksync-era` 进入 Top repo，也必须证明来自 org-wide 排名；若 `zksync-era` 未排名第一，不得在后文把它写成唯一主仓。
- 至少选择 Top 5-8 个 repo 作为深挖对象；若第 6-12 名显示不同产品/叙事方向，必须作为 supporting repo 或解释排除。

## Step 1: 活跃 Repo 发现与排序

本节是 deep draft 的独立第一章，不是附录。研究者必须先完成本节再进入 PR 分类与叙事分析。

### 扫描 org

预扫描时间：2026-05-23T16:11Z 至 2026-05-23T16:24Z。

| org | 角色/发现方式 | public repos | 非 archived 且非 fork repo | 2026-02-23..2026-05-23 PR created | 初步处理 |
|---|---:|---:|---:|---:|---|
| `matter-labs` | ZKsync/Matter Labs 核心开发 org | 230 | 151 | 1407 | 必扫，核心数据源 |
| `zkSync-Community-Hub` | 开发者社区 org，dispatch 明确要求 | 8 | 7 | 2 | 必扫；若活跃度低，作为社区/文档背景 |
| `zksync-sdk` | GitHub search 发现的 SDK 历史 org | 24 | 15 | 6 | 纳入 universe；多数 repo 可能 archived/legacy |
| `zksync-association` | ZKsync Association/governance 相关 org | 11 | 11 | 11 | 纳入 governance/contracts 支撑信号 |
| `zksync` | GitHub org 名称匹配 | 1 | 1 | 0 | 纳入 universe，预计低活跃 |

深度阶段需复核：org 名称大小写、是否有 `ZKsync` 官方 docs 链出的其他 repo、是否存在已迁移或改名仓库、是否存在 private/internal work 不可见造成的偏差。

### 排序维度

最小字段：

- repo metadata：`full_name`、description、archived/fork、default branch、primary language、stars/forks、pushed_at、last release/tag；
- PR metrics：窗口内 `created`、`merged`、`open`、`closed-unmerged`、weekly created/merged、merge latency、large PR、bot PR；
- commit frequency：default branch 或 relevant release branch 的 commit count、active commit weeks、commit authors；
- contributor activity：unique PR authors、unique commit authors、core vs bot vs external；
- release/push signal：窗口内 release/tag、latest pushed_at、是否有 release-please 或 generated sync noise。

### 初步候选 Top 活跃 repo

以下为 outline 阶段预扫描的候选排序，供 deep phase 复核和扩展。PR 数据来自 `gh search prs --owner matter-labs --created 2026-02-23..2026-05-23` 按 2026-02-23..03-31、04-01..04-30、05-01..05-23 三段抓取后按 URL 去重；merged count 来自 PR state / GitHub issue search；commit count 来自 GitHub commit search `committer-date:2026-02-23..2026-05-23`，deep phase 必须用 branch-aware pagination 复核，避免 Search 对 merge/sync 工作流的低估。

| 初步 rank | repo | PR created | merged | open | closed-unmerged | active PR authors | commit count | 说明 |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `matter-labs/zksync-os-server` | 403 | 238 | 38 | 127 | 35 | 227 | ZKsync OS server，新 server implementation，窗口内最活跃 |
| 2 | `matter-labs/era-contracts` | 154 | 95 | 25 | 34 | 23 | 4 | Era/ZK Stack contracts，可能有 sync/generated commit 低估 |
| 3 | `matter-labs/zksync-os` | 146 | 72 | 32 | 42 | 12 | 2 | Generalized RISC-V STF，PR 活跃但 commit search 需复核 |
| 4 | `matter-labs/zksync-era` | 130 | 88 | 21 | 21 | 27 | 60 | Era core 仍活跃，但不是默认第一 |
| 5 | `matter-labs/zksync-airbender` | 94 | 73 | 9 | 12 | 17 | 2 | Airbender RISC-V prover system，proof narrative 核心 |
| 6 | `matter-labs/solx-llvm` | 56 | 52 | 3 | 1 | 4 | 89 | Solidity compiler/LLVM fork，compiler activity 高 |
| 7 | `matter-labs/airbender-platform` | 49 | 38 | 3 | 8 | 9 | 42 | Airbender developer stack |
| 8 | `matter-labs/zksync-js` | 39 | 30 | 4 | 5 | 6 | 30 | ZKsync OS JavaScript SDK / tooling |
| 9 | `matter-labs/eravm-airbender-verifier` | 32 | 21 | 10 | 1 | 8 | 19 | EraVM Airbender verifier |
| 10 | `matter-labs/foundry-zksync` | 25 | 12 | 3 | 10 | 5 | 61 | Foundry tooling，commit activity 比 PR rank 更高 |
| 11 | `matter-labs/block-explorer` | 22 | 21 | 1 | 0 | 5 | 20 | Explorer/API surface |
| 12 | `matter-labs/zksync-os-interface` | 21 | 20 | 0 | 1 | 7 | 22 | MultiVM interface |
| 13 | `matter-labs/local-prividium` | 20 | 15 | 3 | 2 | 6 | 16 | Prividium/local enterprise stack |
| 14 | `matter-labs/watchdog` | 19 | 14 | 5 | 0 | 7 | 15 | ZKsync OS watchdog/ops |
| 15 | `matter-labs/zksync-airbender-prover` | 17 | 10 | 2 | 5 | 9 | 10 | Airbender prover service |

相关 org 低活跃候选：

- `zksync-association/zk-governance`: 8 PR created，4 open，2 active authors；governance/freezability/audit 信号，应作为 governance supporting repo。
- `zksync-sdk/zksync-ethers`: 6 PR created，legacy bridge removal 等 SDK 维护；如 SDK org 多数 archived，应作为 legacy/DX background。
- `zkSync-Community-Hub/community-code`: 2 PR created，均为依赖/CI 类；社区 org 不应主导工程结论。

### Top repo 初步选择标准

Deep draft 建议将 Top 8 作为主分析对象：

1. `matter-labs/zksync-os-server`
2. `matter-labs/era-contracts`
3. `matter-labs/zksync-os`
4. `matter-labs/zksync-era`
5. `matter-labs/zksync-airbender`
6. `matter-labs/solx-llvm`
7. `matter-labs/airbender-platform`
8. `matter-labs/zksync-js`

Supporting repo 需保留：

- Airbender/verifier/prover 支撑：`eravm-airbender-verifier`、`zksync-airbender-prover`、`zksync-os-interface`；
- Developer tooling：`foundry-zksync`、`block-explorer`；
- Enterprise/Prividium：`local-prividium`、`zksync-sso`、`watchdog`；
- Governance: `zksync-association/zk-governance`。

如果 deep phase 复核后的 commit/contributor 排名显著提升某个 supporting repo（例如 `foundry-zksync`、`zksync-os-interface`、`local-prividium`），可把它升入主分析对象，但必须记录变更原因。

## Research Questions

1. 近 3 个月内，ZKsync 相关 org 下哪些 repo 实际最活跃？按 PR created、merged PR、commit count、active contributors 和 release/push signals 排序后，Top repo 是否显示研发重心已经从 `zksync-era` 转向 ZKsync OS / Airbender / contracts / tooling 的多仓协同？
2. Top 活跃 repo 的开发活动分别指向哪些主线：ZKsync OS server、RISC-V STF、Airbender prover、Era compatibility/API、contracts/Gateway/protocol upgrade、compiler/tooling、JS/Foundry/DX、Prividium/enterprise、ops/monitoring？
3. `matter-labs/zksync-era` 在数据驱动排序中扮演什么角色：仍是生产 Era core 的兼容与 release 仓，还是近期主要新增工作正在迁移到 OS/server/prover/contracts 相关 repo？
4. 重大功能变更和架构调整有哪些？分别处于 merged code、release、developer preview、testnet、mainnet-active、enterprise module、docs-only、experimental 还是 narrative-heavy 阶段？
5. ZKsync 近期对外叙事是否从"Era ZK Rollup / ZK Stack"转向"ZKsync OS + Airbender + Elastic Chain/Gateway + enterprise Prividium + native AA/SSO"的组合？
6. GitHub 活动和官方公开信息是否一致？哪些方向工程活动强但公开叙事弱，哪些方向叙事强但代码证据不足？
7. 相比 Optimism Superchain/Base Stack、Arbitrum Orbit/Stylus/BoLD、Sui 支付/Move 叙事，ZKsync 的差异化定位是什么？
8. 对 Mantle 而言，ZKsync 的近期开发和叙事变化构成哪些竞争压力、可借鉴设计、不可迁移约束和短中长期响应建议？

## Items

### item-1: Org 与 repo universe 全量发现

建立研究对象边界。该项必须先于所有 repo 深挖，输出完整 repo universe 表。

必须覆盖：

- `matter-labs`、`zkSync-Community-Hub`、`zksync-sdk`、`zksync-association`、`zksync` 全部可见 repo；
- repo metadata：name、URL、description、archived、fork、default branch、primary language、stars/forks、created/updated/pushed_at、latest release/tag；
- repo 类型标注：core Era、ZKsync OS、server/node、prover/Airbender、contracts/protocol upgrade、compiler、SDK/tooling、docs/community、enterprise/Prividium、governance/association、ops/infra、legacy/archive；
- 发现路径和排除规则：archived/fork 默认排除活跃排序但保留清单；legacy SDK、community/docs、governance 低活跃 repo 可作为叙事 supporting source；
- 输出：完整 repo universe 表和纳入/排除决策表。

- **Priority**: critical
- **Dependencies**: none

### item-2: 近 3 个月活跃度排名与 Top repo 选择

对 item-1 的 repo universe 进行数据驱动排序，决定后续分析对象。该项对应 deep draft 的 `Step 1: 活跃 Repo 发现与排序`。

必须覆盖：

- 时间窗口：2026-02-23 至 2026-05-23，UTC 边界与查询时间；
- 每个 repo 的 PR created、merged、open、closed-unmerged、commit count、active PR authors、active commit authors、active weeks、release/tag、pushed_at；
- 排序公式与权重；至少给出 raw values、normalized values、score、rank；
- 敏感性检查：PR-only、merged-only、commit-only、contributors-only 排名；
- 去噪规则：bot/dependabot/renovate、release-please、generated sync PR、backport/cherry-pick/revert、fork/mirror、large generated files；
- Top repo 选择：建议 Top 8 主分析 + supporting repo；所有高分但排除 repo 需解释；
- 输出：活跃 repo 排名表、候选 Top repo 列表、deep analysis scope 锁定说明。

- **Priority**: critical
- **Dependencies**: item-1

### item-3: Top repo PR 活动基线与趋势

针对 item-2 选出的 Top repo 建立 PR 级事实底座。

必须覆盖：

- 每个 Top repo 的 PR 原始表：repo、PR number、title、state、created_at、merged_at/closed_at、author、labels、changed files、additions/deletions、review count、URL；
- 周粒度或双周粒度 PR created / merged / closed / open 趋势；
- merge latency、large PR、小修 PR、revert/follow-up、release/backport、test-only/docs-only 占比；
- contributor 结构：Matter Labs core、external contributor、bot、生态/审计/关联团队；
- 目录/模块热区：OS server、state transition、API/RPC、contracts、prover、compiler、SDK、Prividium、ops；
- 输出：Top repo PR 活动趋势表、贡献者结构表、关键峰值解释。

- **Priority**: high
- **Dependencies**: item-2

### item-4: PR 分类体系与开发方向归因

把 Top repo 的 PR 数据归类为开发方向图谱。分类应先由 repo/path/title/label/PR body 数据驱动生成，再人工合并。

建议分类：

1. **ZKsync OS server / node runtime**：server implementation、consensus/RPC forwarding、API parity、state sync、metrics、node ops；
2. **ZKsync OS / RISC-V STF / MultiVM**：state transition function、RISC-V execution、protocol interfaces、revm compatibility、VM semantics；
3. **Airbender prover / verifier / platform**：RISC-V proving、GPU prover、commitments、delegations、verifier input、prover service；
4. **Era compatibility / API / release maintenance**：`zksync-era` core releases、RPC methods、EraVM behavior、API compatibility、protocol v29/v31 bridge；
5. **Contracts / Gateway / protocol upgrade**：`era-contracts`、proof aggregation/settlement、SL chain id、batch output hash、freezability、upgrade verification；
6. **Compiler / LLVM / Solidity toolchain**：`solx-llvm`、Era compiler、Foundry integration、alloy/ethers/tooling compatibility；
7. **SDK / developer tooling / explorer**：`zksync-js`、`foundry-zksync`、block explorer APIs、docs/DX；
8. **Enterprise / Prividium / SSO / ops**：`local-prividium`、`zksync-sso`、watchdog、private deployments、TEE/monitoring;
9. **Governance / Association / security audit**：`zk-governance`、audit fixes、chain/bridge freezability、minter contracts；
10. **Other data-discovered category**：若 Top repo 显示新方向，必须新增。

每个类别需输出：PR 数量/占比、代表 PR、repo/path、主要作者、状态分布、技术目标、用户/生态目标、maturity label、对 Mantle 影响等级。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: 重大功能变更与架构调整深挖

从 PR 分类中识别真正影响架构、协议、开发者接口或商业叙事的变化。

重点检查：

- ZKsync OS server 是否成为新的 execution/server surface，和 `zksync-era` 的职责边界如何变化；
- ZKsync OS / RISC-V STF 与 MultiVM interface 是否代表从 EraVM-only 走向 generalized STF；
- Airbender 的 prover/verifier/platform 改动是否显示 RISC-V prover 正从 developer preview 走向更可集成的 proving stack；
- `era-contracts` / Gateway / protocol upgrade 是否改变 proof aggregation、settlement、chain id、batch output hash、upgrade/freezability 模型；
- Era core API/release 改动是否更多是 compatibility/maintenance，还是仍有核心协议新增；
- compiler/tooling/SDK/explorer 改动是否服务 OS/Airbender 迁移、开发者兼容或产品化；
- Prividium/SSO/enterprise/ops 改动是否有可验证代码支撑，还是主要是 local/demo/enterprise packaged module；
- 每项重大变化必须标注 status：merged、released、devnet/testnet、developer preview、mainnet-active、enterprise module、docs-only、experimental。

- **Priority**: high
- **Dependencies**: item-4

### item-6: 开发重点变化：从活跃度数据到资源配置判断

综合 repo 排名、PR 分类、趋势和贡献者结构，判断 ZKsync 近期开发重点是否发生变化。

必须覆盖：

- Top repo 排名是否显示资源集中在 OS server、ZKsync OS、Airbender、contracts/protocol upgrade，而非单一 `zksync-era`；
- `zksync-era` 的活动是否以 release/API compatibility/maintenance 为主，或仍承担新 protocol work；
- OS/Airbender/contracts/tooling 是否构成跨 repo 产品化链条；
- contributor 结构是否集中于 Matter Labs core，还是外部 contributor/生态开发者扩张；
- low-code/high-PR 或 high-commit/low-PR repo 的解释，避免单指标误导；
- 与旧错误分析的差异：哪些旧结论因为 Era-first 假设被推翻或降级；
- 输出：开发重点变化结论表，按 evidence grade 和 confidence 标注。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5

### item-7: 公开叙事时间线与 GitHub 活动映射

建立 2026-02-23 至 2026-05-23 的 ZKsync 对外叙事时间线，并和 GitHub 活动映射。

必须覆盖：

- ZKsync 官方 docs/blog：ZKsync OS、Airbender、Elastic Chain、Gateway、Prividium、ZK Stack、native account abstraction/SSO；
- Matter Labs / ZKsync Association 公告、release notes、governance/forum/security/audit materials；
- 生态或合作方官方资料：wallet/account abstraction、enterprise/private chain、proving networks、developer tooling；
- 叙事标签：OS/RISC-V STF、proof performance/Airbender、Elastic Chain/Gateway、enterprise validium/Prividium、native AA/SSO、developer tooling、chain abstraction/interoperability；
- 每个叙事事件对应的代码活动：repo/PR/docs/release 是否支撑，还是 narrative-heavy；
- 输出：叙事时间线、evidence map、maturity label。

- **Priority**: high
- **Dependencies**: item-2, item-5, item-6

### item-8: ZKsync OS + Airbender 技术路线专项分析

基于数据驱动 Top repo 结果，深挖 OS/Airbender 是否构成近期核心技术路线。

必须覆盖：

- `zksync-os-server`、`zksync-os`、`zksync-airbender`、`airbender-platform`、`eravm-airbender-verifier`、`zksync-airbender-prover` 的职责边界；
- RISC-V STF、server runtime、proof generation、verification、protocol interface、GPU prover、developer platform 的端到端链路；
- 与 `zksync-era` 的关系：兼容、迁移、并行、替代还是长期双轨；
- 官方性能/架构声明的状态标注：不要把 Developer Preview 或 internal benchmark 当成独立生产事实；
- 对 Mantle 的启示：ZK/RISC-V prover 投资、alternative STF、prover modularity、zkVM 叙事、迁移成本和技术风险。

- **Priority**: high
- **Dependencies**: item-4, item-5

### item-9: Gateway / Elastic Chain / contracts / governance 方向专项分析

分析 contracts/protocol upgrade/governance repo 的活动如何支撑 Elastic Chain / Gateway / settlement 叙事。

必须覆盖：

- `era-contracts`、`zksync-os-scripts`、`protocol-upgrade-verification-tool`、`zksync-association/zk-governance`、`zkminters` 等 repo；
- proof aggregation / settlement middleware / chain id / batch output hash / protocol version / upgrade verification / freezability；
- Governance 与 security boundary：ZKsync Association、audit fixes、freezing/unfreezing、guardian/security council 类权限；
- Status：mainnet-active、testnet、optional middleware、governance proposal、audit remediation、local/dev only；
- 与 Optimism Superchain shared governance、Arbitrum Orbit custom governance 的差异；
- 对 Mantle 的启示：跨链结算/证明聚合、upgrade governance、security council/exit-window、multi-chain standardization。

- **Priority**: high
- **Dependencies**: item-4, item-5, item-7

### item-10: Developer tooling / SDK / compiler / explorer 方向专项分析

评估 ZKsync 是否在通过 tooling 和 compiler 维持开发者兼容与迁移路径。

必须覆盖：

- `solx-llvm`、`foundry-zksync`、`zksync-js`、`block-explorer`、`zksync-docs`、`zksync-os-interface` 的 PR 分类；
- Solidity/compiler、Foundry、JS SDK、Explorer API、Ethereum RPC compatibility、docs/DX 的实际进展；
- 与 OS/Airbender 迁移的关系：是否在为新 stack 铺平开发者入口；
- 兼容性风险：EVM feature gaps、EraVM/RISC-V differences、tooling version lock、legacy bridge/API removal；
- 对 Mantle 的启示：开发者迁移成本、RPC/tooling parity、explorer/indexer quality、docs-first vs code-first。

- **Priority**: medium
- **Dependencies**: item-4, item-5

### item-11: Enterprise / Prividium / SSO / private-chain 方向专项分析

评估企业/隐私/私有部署叙事是否有近期代码和文档支撑。

必须覆盖：

- `local-prividium`、`zksync-sso`、`zksync-sso-contracts`、`watchdog`、TEE/ops 相关 repo；
- Prividium 的 license/module/status、local deployment、private DA / Validium、access control、monitoring、SSO/session handling；
- 哪些是 production customer evidence，哪些只是 local/demo/enterprise module；
- 与 Canton/Tempo/Base enterprise/private-chain 方向的差异；
- 对 Mantle 的启示：企业链隐私、KYC/permissioning、private DA、SSO/native AA、运营监控、商业化包装。

- **Priority**: medium
- **Dependencies**: item-2, item-4, item-7

### item-12: 横向竞争定位与 Mantle 行动建议

把 GitHub 活动和叙事分析转化为 Mantle 可用的竞争判断。

比较维度：

- 技术路线：ZKsync OS/Airbender vs Optimism OP Stack/Superchain vs Arbitrum Nitro/Orbit/Stylus vs Mantle OP-derived/EigenDA/roadmap；
- 多链/互操作：Elastic Chain/Gateway vs Superchain interop vs Orbit appchain vs Mantle L2/L3/appchain optionality；
- 证明/安全：ZK/RISC-V prover vs OP fault proof vs BoLD vs Mantle Stage 1/upgrade/DA strategy；
- 开发者体验：Era/EVM compatibility/tooling vs OP Stack ecosystem vs Stylus/WASM vs Mantle EVM/EigenDA tooling；
- 企业/隐私/机构：Prividium/SSO vs Canton/Tempo/Base/Mantle enterprise possibilities；
- 生态战略：Matter Labs/Matter Labs repo activity and governance vs Foundation/Association/governance/onboarding;
- 输出：Mantle threat/opportunity matrix、短期跟踪清单（1-2 个月）、中期技术/叙事建议（1-2 季度）、不可照搬边界。

- **Priority**: high
- **Dependencies**: item-6, item-7, item-8, item-9, item-10, item-11

## Fields To Capture

| field | type | applies_to | description |
|---|---|---|---|
| `repo_full_name` | string | repo/pr | GitHub owner/repo |
| `org` | string | repo | GitHub organization |
| `repo_type` | enum | repo | core-era / os-server / os-stf / prover / contracts / compiler / sdk-tooling / explorer / docs / enterprise / governance / ops / legacy |
| `archived_or_fork` | bool | repo | 是否 archived/fork，是否排除活跃排序 |
| `pr_created_count` | integer | repo | 2026-02-23..2026-05-23 PR created |
| `pr_merged_count` | integer | repo | 同窗口 merged PR |
| `pr_open_count` | integer | repo | 同窗口创建且抓取时 open PR |
| `pr_closed_unmerged_count` | integer | repo | 同窗口 closed-unmerged PR |
| `commit_count` | integer | repo | 同窗口 default branch 或 relevant branch commits |
| `active_contributors` | integer | repo | 去噪后的 active PR/commit authors |
| `activity_score` | number | repo | 归一化活跃度总分 |
| `rank_sensitivity` | object | repo | PR-only、commit-only、contributors-only rank |
| `pr_category` | enum | pr | OS server / OS STF / Airbender / Era compatibility / contracts-Gateway / compiler / tooling / enterprise / governance / other |
| `maturity_status` | enum | change/narrative | docs-only / experimental / developer-preview / merged / released / devnet / testnet / mainnet-active / enterprise-module / deprecated |
| `evidence_grade` | enum | claim | github-search / pr-body-reviewed / code-diff-reviewed / release-confirmed / docs-confirmed / governance-confirmed / external-unverified / narrative-inferred |
| `mantle_impact` | enum | claim | direct engineering watch / roadmap pressure / narrative pressure / optional inspiration / low relevance |
| `confidence` | enum | claim | high / medium / low |

## Diagram And Table Expectations

1. **Org/Repo Universe Table**：按 org、repo type、archived/fork、pushed_at 汇总扫描范围。
2. **活跃 Repo 排名表**：Top 15 repo，展示 PR created、merged、commit count、contributors、score、rank sensitivity。
3. **Top Repo PR 分类矩阵**：repo x category，显示 PR 数量/占比和代表 PR。
4. **开发活动时间线**：2026-02-23 至 2026-05-23 周粒度 PR 活动 + release/docs/governance events。
5. **ZKsync 技术路线图**：ZKsync OS server -> OS STF -> Airbender prover/verifier -> contracts/Gateway -> developer tooling 的关系图。
6. **叙事证据地图**：ZKsync OS、Airbender、Elastic Chain/Gateway、Prividium、SSO/tooling 各自的 GitHub/docs/release evidence 与 maturity。
7. **Mantle 竞争启示矩阵**：威胁/机会/不可照搬/行动建议。

## Source Plan

Primary sources:

- GitHub REST/GraphQL/gh CLI for orgs: `matter-labs`, `zkSync-Community-Hub`, `zksync-sdk`, `zksync-association`, `zksync`；
- GitHub PRs, commits, releases, tags, PR bodies, changed files and representative diffs for selected Top repos；
- ZKsync official docs: ZKsync OS, Airbender, Gateway, Elastic Chain, Prividium, ZK Stack, account abstraction / SSO；
- Matter Labs/ZKsync official blog and release notes；
- ZKsync Association governance/security/audit repositories and official governance surfaces；
- Existing internal research sections for Optimism, Arbitrum, Sui, Base, Canton, enterprise privacy, only after time-sensitive claims are rechecked.

Secondary/supporting sources:

- L2Beat for public risk/rollup/validium stage context；
- Ecosystem partner official docs/announcements for wallet, SSO, Prividium, enterprise, proving network or tooling claims；
- PR Tracker / community summaries only as leads, never as sole evidence.

## Quality Checklist For Deep Draft

- [ ] `Step 1: 活跃 Repo 发现与排序` appears as an independent first chapter with scanned org list, ranking dimensions, formula, candidate Top repos and data support.
- [ ] No section assumes `zksync-era` is primary before presenting ranking evidence.
- [ ] All GitHub queries record timestamp, exact query, pagination/cap handling and rate-limit caveat.
- [ ] Top repo selection is reproducible and includes sensitivity checks.
- [ ] Era main statistics are kept separate from ZKsync OS/Airbender/contracts/supporting repo statistics.
- [ ] Official Airbender/Gateway/Prividium claims are not treated as production facts without maturity status.
- [ ] Representative PRs include links, statuses, authors and touched paths; important conclusions have evidence grades.
- [ ] Narrative claims are mapped to both public docs/announcements and GitHub activity, or explicitly labeled narrative-heavy.
- [ ] Mantle recommendations distinguish direct engineering actions from narrative monitoring and optional inspiration.
- [ ] Known limitations are explicit: private/internal work invisibility, GitHub Search caps, generated sync PRs, commit count under/over-counting, public docs lag.
