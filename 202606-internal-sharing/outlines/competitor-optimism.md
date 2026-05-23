---
topic: "Optimism 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-optimism"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/competitor-optimism.md"
  draft: "202606-internal-sharing/research-sections/competitor-optimism/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/competitor-optimism/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  根据最新 issue 描述重新研究 Optimism 近期开发与叙事变化。研究必须先扫描 Optimism 相关 GitHub
  Organization（包括但不限于 `ethereum-optimism`，如发现 `op-rs`、`ethereum-optimism-archive`
  或其他官方/半官方相关 org 也需说明是否纳入），对所有可见 repo 在近 3 个月内的 PR 数量、commit
  频率、活跃 contributor、release/tag、star/fork 或 issue 活动等指标做数据驱动排序，再选择 Top
  活跃 repo 进入深度分析。不得预设只分析 `optimism` 或 `op-geth`。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、Mantle 协议/客户端/基础设施工程师、
  生态与战略团队，以及 Multica Research Squad 的 Review Agent 和后续写作者。读者熟悉 L2、
  OP Stack、Superchain、interop、op-geth/op-reth、Base/Mantle 背景，但需要一份以近 3 个月
  公开开发活动和官方叙事为基础、可复核且不预设结论的竞争对手近况梳理。

expected_output: |
  一份中文结构化 research section，涵盖：
  - Optimism 相关 GitHub org/repo 的近 3 个月活跃度数据集、排序方法和 Top 活跃 repo 概况；
  - Top 活跃 repo 的 PR 活动分类、主要开发方向、重大功能变更、架构调整和活跃度趋势变化；
  - Optimism 近期叙事演变：Superchain、interop、OP Stack 模块化、op-reth/op-supernode/fault proof、
    governance/standardization，以及 Base 独立化后的定位调整；
  - 对 Mantle 作为 OP Stack fork / OP-derived chain 的直接影响、竞争压力、可借鉴设计、不可照搬边界
    和短中长期行动建议；
  - 至少 4 张图/表：repo 活跃度排行榜、Top repo PR 分类矩阵、开发/叙事时间线、Optimism/Base/Mantle
    定位对比或 Mantle 响应矩阵。

source_requirements_summary: |
  深度研究必须以 primary source 为主。第一步必须直接查询 GitHub org/repo/PR/commit/contributor 数据，
  固定近 3 个月窗口并记录查询时间、查询语句、分页完整性、rate-limit caveat、去重规则和排序公式。
  PR Tracker 每日报告可作为辅助输入，但不能替代 GitHub 原始数据。叙事分析需优先引用 Optimism 官方
  docs、blog、spec、governance forum、release notes、dev notices、GitHub PR/release/tag；Base 相关
  判断需用 Base 官方资料和本仓库既有 Base 研究交叉校验。时间敏感事实必须在 draft 阶段重新核验，不得
  沿用旧 Optimism artifact 或本 outline 的示例。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-23T22:44:45+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-23T22:44:45+08:00"

multica_issue_id: "a3724de9-2cce-4e4e-bfd0-1553680aa666"
branch_name: "research/202606-internal-sharing/competitor-optimism"
base_commit: "57fce87c5b494a341d063e91781435797f12f6ca"
language: "中文"
research_depth: "standard"

prerequisite_sections:
  - slug: competitor-base
    path: 202606-internal-sharing/research-sections/competitor-base/final.md
    status: existing-research-if-present-on-main
  - slug: base-strategy-azul-overview
    path: base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md
    status: existing-research
  - slug: base-vs-optimism-flashblocks
    path: base-azul-upgrade/research-sections/base-vs-optimism-flashblocks/final.md
    status: existing-research
  - slug: mantle-impact-assessment
    path: base-azul-upgrade/research-sections/mantle-impact-assessment/final.md
    status: existing-research
  - slug: architecture-advantage-summary
    path: mantle-base-codebase-evaluation/research-sections/architecture-advantage-summary/final.md
    status: existing-research
  - slug: comprehensive-evaluation-recommendation
    path: mantle-base-codebase-evaluation/research-sections/comprehensive-evaluation-recommendation/final.md
    status: existing-research
  - slug: stage1-case-studies
    path: mantle-stage1-rollup/research-sections/stage1-case-studies/final.md
    status: existing-research
---

# Research Outline: Optimism 近期开发与叙事分析

## Research Questions

1. 近 3 个月内，Optimism 相关 GitHub org 下哪些 repo 实际最活跃？用 PR 数、commit 频率、活跃 contributor、release/tag 和维护活动排序后，Top 活跃 repo 是否与外界直觉一致？
2. Top 活跃 repo 的开发重心分别是什么：Superchain interop、op-supernode/supervisor、op-reth/Rust 组件、fault proof、contracts/governance、devnet/CI/release、docs/devrel、op-geth maintenance，还是其他新方向？
3. Top 活跃 repo 的 PR 活动趋势是否显示研发资源正在从传统 OP Stack 核心仓迁移到 interop、supernode、Rust client、标准化部署或生态工具？
4. 近 3 个月是否存在重大功能变更或架构调整？这些变化分别处于 spec、merged code、devnet、testnet、mainnet-active、governance-approved、experimental 或 maintenance-only 哪一阶段？
5. Optimism 的对外叙事是否正从"OP Stack 上游"调整为"Superchain interoperability + standardized multi-chain governance + modular client stack"？
6. Base / Base Stack / Azul 独立化之后，Optimism 与 Base 的关系应如何准确表述：技术分叉、Superchain 成员、合作竞争、生态分层，还是部分替代？
7. 对 Mantle 作为 OP Stack fork / OP-derived chain 而言，哪些变化会带来上游兼容风险、迁移压力、生态/叙事压力或可借鉴机会？

## Items

### item-1: GitHub org/repo 全量扫描、窗口定义与活跃度评分方法

建立本研究的事实底座。第一步不是分析预设 repo，而是扫描 Optimism 相关 GitHub Organization 下所有可见 repo，形成近 3 个月活跃度排行榜。默认窗口以实际抓取日向前 3 个月定义；如果 draft 在 2026-05-23 抓取，则建议记录为 2026-02-23 至 2026-05-23，并在最终稿中写明时区和抓取时间。

必须覆盖：

- org 范围：至少扫描 `ethereum-optimism`；如发现 `op-rs`、`ethereum-optimism-archive`、`oplabs` 或其他官方/半官方相关 org，需要列出发现方式、纳入/排除理由和风险；
- repo 清单：每个 repo 的 name、description、archived/fork/private 可见性、default branch、primary language、stars/forks、last pushed、last release/tag；
- 活跃度指标：近 3 个月 PR created、PR merged、commit count、unique contributors、active days/weeks、release/tag count、issue/discussion activity（如可得）；
- 排序公式：建议给出主排序 `score = normalized(PR created + merged PR + commits + contributors + release signal)`，并附 sensitivity check：按 PR 数、commit 数、contributors 单独排序是否改变 Top repo；
- 去噪规则：bot/dependabot、generated code、fork mirrors、archived repos、monorepo subproject、release branches、backport/cherry-pick/revert 的处理；
- 输出：一张全 repo 活跃度表和 Top repo 选择阈值（例如 Top 8-12，或得分覆盖 80% 近期活动的 repo）。

- **Priority**: critical
- **Dependencies**: none

### item-2: Top 活跃 repo 选择与 repo-by-repo 概况

基于 item-1 的排序结果，确定深度分析对象。该项必须解释为什么选择这些 repo、为什么未选择常被提及但近期不活跃的 repo，并避免把旧研究中的 `optimism`/`op-geth` 作为默认答案。

必须覆盖：

- Top 活跃 repo 列表：repo、活跃度得分、PR 数、commit 数、contributors、主要语言/组件、近 3 个月 activity trend；
- repo 功能定位：monorepo/core protocol、execution client、Rust client、spec/docs、developer tooling、contracts/governance、deployment/ops、ecosystem/devrel 等；
- repo 间关系：哪些是 monorepo 子项目，哪些是独立 client/tooling，哪些是 docs/spec 或 registry；
- 排除清单：活跃度低但叙事重要的 repo 是否仅作为背景补充；例如如果 `op-geth` 未进 Top，也需说明其仍可能因 Mantle 上游兼容而进入专项观察；
- 与 PR Tracker 的关系：PR Tracker 已覆盖的 repo 和本次全量扫描 Top repo 是否一致，差异如何处理；
- 输出：Top repo overview 表，作为后续 PR 分析范围的唯一入口。

- **Priority**: critical
- **Dependencies**: item-1

### item-3: Top repo PR 活动总览、趋势变化与贡献者结构

对筛选出的 Top repo 做近 3 个月 PR 活动分析，回答"开发活跃度如何变化"。重点不是列出所有 PR，而是按 repo 和时间维度识别研发节奏、峰值周、模块热点、贡献者集中度和维护质量。

必须覆盖：

- 周粒度或双周粒度 PR created / merged / closed / open 趋势，按 repo 分面展示；
- 活跃作者和贡献者结构：OP Labs core、外部 contributor、bot/dependabot、生态合作方或未知账号的比例；
- merge latency、large PR、小修 PR、revert/follow-up、review/test 覆盖、release branch/backport 信号；
- 目录/模块热区：在 monorepo 中按 package/path 归因，例如 interop、op-supervisor、op-supernode、op-reth、op-node、op-contracts、op-deployer、devnet、docs；
- 与 release/governance/devnet/公告节点的对应关系，判断 PR 峰值是否与重要路线推进有关；
- 输出：Top repo PR 活动趋势表、贡献者结构表、关键峰值解释。

- **Priority**: high
- **Dependencies**: item-2

### item-4: PR 分类体系与主要开发方向归因

为 Top repo 的 PR 建立可复核分类框架，服务后续工程和叙事判断。分类应先由数据聚类和路径/标签/标题/PR body 证据生成，再人工合并成研究可读类别。

建议分类（draft 阶段可根据 Top repo 数据调整）：

1. **Superchain interop / dependency set**：跨链消息、dependency set、cross-safe/unsafe、access-list checks、interop notices；
2. **op-supernode / op-supervisor / operator stack**：一体化节点、supervisor sync、log backfill、rewind、observability、devnet；
3. **op-reth / Rust client components**：execution client、payload service、proofs-history、runtime/docker、reth task lifecycle、OP-specific crates；
4. **Fault proof / Cannon / Kona / dispute games**：op-program、op-challenger、absolute prestate、MIPS/MIPS64、multi-proof 或 alt-FPP；
5. **Contracts / governance / standardization**：op-contracts、upgrade tooling、superchain-registry、ProtocolVersions、Security Council / Guardian boundary；
6. **Deployment / devnet / release engineering**：op-deployer、devstack、CI、tests、release tags、network config；
7. **op-geth / execution maintenance**：upstream go-ethereum merge、engine API、interop fixes、runtime/docker、security fixes；
8. **Docs / developer experience / ecosystem communication**：spec/docs/tutorial/devrel examples；
9. **Other data-discovered category**：若 Top repo 显示新方向（如 SDK、analytics、registry、wallet/tooling），必须新增而不是硬塞进旧分类。

每个类别需要输出：

- PR 数量、代表 PR、涉及 repo/path、主要作者、状态分布；
- 技术目标、用户/生态目标、叙事目标；
- implementation status：spec / merged / devnet / testnet / mainnet-active / governance-approved / experimental / maintenance-only；
- 对 Mantle 的影响等级：直接上游依赖、潜在迁移压力、叙事压力、低相关背景。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: 重大功能变更与架构调整深挖

从 Top repo 和 PR 分类中提炼近 3 个月真正的重大变化，避免把高 PR 数的小修误判为战略方向。该项应按"代码 surface + rollout state + risk/impact"描述架构调整。

必须覆盖（按数据结果取舍，不强行预设）：

- Superchain interop 的架构变化：op-supervisor/op-supernode、dependency set、cross-chain message/checks、EL access-list 或 system tx 变化、operator failure modes；
- OP Stack client/节点演进：op-node/op-supernode 关系、op-reth 与 op-geth 的分工、Rust 组件成熟度、operator 部署路径；
- Fault proof 与安全机制：Cannon/Kona/op-program/dispute game 的近期修复、proof reproducibility、permissionless/Stage 1 相关状态；
- Contracts/governance/registry：op-contracts、deployment tooling、superchain-registry、upgrade bundle、governance control plane；
- 任何由数据发现的其他方向：例如 docs/spec 活跃、dev tooling、ecosystem tooling 或 infra repos；
- 对每项重大变化给出 status、主要证据、仍未验证的问题、Mantle 需要工程复核的点。

- **Priority**: high
- **Dependencies**: item-4

### item-6: 开发重点变化：从活跃度数据到资源配置判断

综合 repo 排名、PR 分类和重大变化，回答 Optimism 近期开发重点是否发生变化。该项需要明确哪些判断是数据直接支持，哪些是基于 PR 内容和官方叙事的推断。

必须覆盖：

- Top repo 排名是否显示资源集中在 monorepo、interop、Rust/client、operator tooling、contracts/governance 或其他方向；
- `optimism` monorepo 内部热点是否从传统 op-node/op-geth maintenance 转向 interop/op-supernode/op-reth/devnet；
- `op-geth` 若活跃度较低，应判断是 maintenance-only、稳定状态、迁移信号，还是只因工作转移到 monorepo/op-reth；
- contributor 和 review 结构是否显示 OP Labs 核心团队集中推进，还是生态 contributor 扩张；
- 与 3 个月前或旧 artifact 的差异：哪些旧结论被新数据推翻、保留或需要降级为不确定；
- 输出：开发重点变化结论表，按 confidence 标注。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5

### item-7: Optimism 叙事演变：Superchain、interop、standardization 与 modular OP Stack

把 GitHub 活动与公开信息连接起来，分析 Optimism 的近期叙事变化。该项应使用官方 blog/docs/forum/dev notices/release notes，与 GitHub 活动做互证，不用社媒或二级文章单独支撑关键结论。

必须覆盖：

- Superchain / interop 叙事：统一流动性、跨链应用、dependency set、shared security/governance、operator coordination；
- OP Stack modularity 叙事：op-reth、op-supernode、op-deployer、superchain registry、standard chain config、multi-client / alternative client 路线；
- Fault proof / Stage 1 / decentralization 叙事：从功能上线到可复现、operator readiness、governance boundary、multi-proof 或 alt proof roadmap；
- ecosystem strategy：Optimism Collective、Retro Funding、Superchain member chains、standardization 与 chain onboarding；
- 开发活动如何支撑或削弱叙事：如果某个叙事热但 PR/activity 弱，必须标注为 narrative-heavy；如果 PR 活动强但公开叙事弱，标注为 engineering-heavy；
- 输出：叙事演变时间线和 evidence map。

- **Priority**: high
- **Dependencies**: item-5, item-6

### item-8: Base 独立化后的 Optimism 定位调整

专门处理 issue 要求的 Base 脱离/独立化问题。该项需复用仓库既有 Base Azul、Base vs Optimism Flashblocks、Mantle Base codebase evaluation 等研究，但所有时间敏感事实必须重新验证。避免把"Base 技术独立化"简化为"Base 离开 Superchain"，也避免把 Base 叙事当作 Optimism 官方回应。

必须覆盖：

- Base Stack / Azul 的核心变化：base-reth-node、base-consensus、Multiproof、Flashblocks、Engine API changes、release cadence；
- Base 与 Optimism 仍共享或仍相关的部分：Superchain membership、治理/registry/bridge assumptions、legacy OP Stack compatibility、interop participation 或公开合作；
- Optimism 的对应定位：Superchain interop、standardization、multi-client modular stack、governance coordination 是否成为对 Base 独立化的再定位；
- 竞争叙事对比：Base 更偏 product/performance/Coinbase distribution；Optimism 更偏 multi-chain coordination/governance/interoperability；Mantle 更偏 fork + EigenDA/MNT/economics/enterprise/perf differentiation；
- 对 Mantle 的决策含义：Base 路线不是唯一迁移路径，但 Base 独立化凸显 op-geth/op-node 跟随成本和性能/产品速度压力。

- **Priority**: high
- **Dependencies**: item-6, item-7

### item-9: 对 Mantle 的直接影响与竞争启示

将 Optimism 近期开发和叙事变化转化为 Mantle 可执行判断。结论必须分层：工程依赖、产品/生态、治理/安全、竞争叙事，不应只给泛化建议。

必须覆盖：

- **必须跟踪 / 防守**：Top 活跃 repo watchlist、op-geth maintenance/EOL 信号、op-reth maturity、interop specs、superchain-registry、op-contracts upgrade path、fault proof reproducibility；
- **值得借鉴 / POC**：dependency set/supervisor observability、op-supernode operator packaging、standardized deployment tooling、interop devnet test harness、fault proof reproducible prestate；
- **谨慎 / 不适合直接照搬**：完整加入 Superchain governance、无差异跟随 op-reth、直接复制 Base Stack、把 interop 当作短期产品承诺；
- **竞争叙事回应**：Mantle 如何解释自己与 Optimism/Base 的差异：EigenDA/DA strategy、MNT gas/economics、ZK / OP Succinct 路线、企业/支付/隐私场景、性能路线；
- **行动建议**：短期 PR watchlist 和 monthly dashboard，中期 migration/proof-of-concept，长期互操作性/客户端路线选择，以及需要 Mantle 工程团队验证的 blockers。

- **Priority**: high
- **Dependencies**: item-6, item-7, item-8

### item-10: 证据完整性、反例和风险控制

为 adversarial review 预留独立可检查的质量门。该项确保 final section 不会重复旧问题：预设 repo、只看关键词、把 open PR 当完成、把叙事当事实、把 Base 独立化过度简化。

必须覆盖：

- 数据完整性：GitHub API/Search 是否漏页、rate limit、private repo 不可见、archived/fork 处理、PR Tracker 缺口；
- 结论反例：高活跃 repo 可能只是 docs/CI/deps；低活跃 repo 可能因成熟稳定但战略重要；monorepo PR 数可能掩盖子模块变化；
- 状态误读防线：open PR、merged PR、released code、testnet、mainnet、governance-approved、production-ready 必须分开；
- 叙事误读防线：官方叙事、生态媒体、第三方评论、内部推断必须分层；
- Base/Mantle 比较防线：不可把 Base 脱离等同于 Superchain 退出，不可把 Mantle fork 关系等同于自动继承 OP roadmap；
- 输出：confidence/gaps 表和 "claims not supported" 列表，明确哪些说法最终稿不能写或只能低置信度写。

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-3, item-4, item-7, item-8, item-9

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| evidence_window | 近 3 个月窗口、时区、抓取时间、GitHub query/API endpoint、分页/rate-limit 状态、PR Tracker 覆盖情况 | all |
| org_repo_inventory | org 名称、repo 清单、纳入/排除理由、repo metadata、archived/fork/default branch/release 状态 | item-1, item-2 |
| activity_score | PR created/merged、commit count、contributors、active weeks、release/tag 等指标、标准化方法、排序公式和 sensitivity check | item-1, item-2 |
| top_repo_selection | Top repo 阈值、被选中 repo、未选但重要 repo、选择理由和 bias/caveat | item-2 |
| pr_count_and_state | 每个 Top repo 的 created/merged/open/closed、bot/human、周趋势、merge latency、代表 PR 列表和去重规则 | item-3, item-4 |
| category_assignment | PR 或代表 PR 被归入 interop/op-supernode/op-reth/fault proof/contracts/op-geth/docs 等类别的理由，避免只凭关键词 | item-4, item-5 |
| implementation_status | 功能处于 spec、merged、released、devnet、testnet、mainnet-active、governance-approved、experimental、maintenance-only 或 unknown 哪一阶段 | item-4, item-5, item-7, item-8 |
| code_surface | 涉及 repo、package、path、组件和关键文件，例如 op-supervisor、op-supernode、op-reth、op-node、op-geth、op-contracts、superchain-registry | item-4, item-5 |
| narrative_signal | 工程活动如何支撑或削弱官方叙事：Superchain interop、OP Stack modularity、fault proof maturity、standardization、governance | item-7, item-8 |
| base_relationship | 与 Base / Base Stack / Azul 的关系：共享、分叉、替代、竞争、互补或未知；必须区分 Base 技术独立与 Superchain 关系 | item-8 |
| mantle_impact | 对 Mantle 的直接影响：兼容性风险、迁移压力、上游跟踪成本、可借鉴设计、竞争叙事压力和行动建议 | item-5, item-6, item-8, item-9 |
| confidence_and_gaps | 证据等级、未验证假设、冲突来源、缺失数据、反例、需要 Mantle 工程团队复核的问题 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | table/bar | Optimism 相关 repo 近 3 个月活跃度排行榜：repo × PR created/merged × commits × contributors × releases × score × Top 选择结果 | markdown table + optional mermaid xychart |
| diag-2 | heatmap/table | Top repo PR 分类矩阵：repo × category × PR count × representative PR × implementation status × Mantle impact | markdown table |
| diag-3 | timeline | 近 3 个月关键 PR/release/governance/devnet/Base 关系事件时间线，按 interop、client stack、fault proof、contracts/governance、Base/Mantle implications 分泳道 | mermaid |
| diag-4 | architecture | 若数据支持，绘制 Superchain interop / op-supernode / supervisor / client stack 关系图；若 Top repo 不支持该方向，改为数据发现的主要架构变化图 | mermaid |
| diag-5 | comparison | Optimism vs Base vs Mantle 定位对比：governance/interoperability/product-performance/client-stack/DA-proof/economics/enterprise differentiation | markdown table or mermaid |
| diag-6 | decision matrix | Mantle 响应矩阵：必须跟踪、值得 POC、暂不照搬、叙事回应 × 影响等级 × 证据置信度 × owner 建议 | markdown table |

## Source Plan

1. **GitHub primary data**：GitHub REST/GraphQL/Search 或 `gh` CLI。必须记录 org/repo 列表查询、PR 查询、commit/contributor 查询、rate-limit 状态和抓取时间。
2. **Repo-level evidence**：Top repo 的 PR body、diff、merged commit、release notes、tags、code paths、README/docs/spec。
3. **Optimism official sources**：Optimism docs、specs、blog、governance forum、dev notices、release notes、superchain registry、OP Labs engineering posts。
4. **Base official and existing research**：Base docs/blog/repo/release notes，以及仓库内 `base-azul-upgrade`、`mantle-base-codebase-evaluation`、`competitor-base`（若 main 上存在）相关 final sections；所有时间敏感事实需重新核验。
5. **Mantle internal comparison inputs**：本仓库既有 Mantle Stage 1、Base codebase evaluation、performance/architecture sections，用于 Mantle impact，不用于替代 Optimism 数据。
6. **Secondary sources**：L2Beat、Dune/Artemis/TokenTerminal、行业文章、social/devrel 内容仅作补充或交叉验证；关键结论不能只依赖二级来源。

## Acceptance Checklist for Deep Draft

- [ ] 已扫描 `ethereum-optimism` 下所有可见 repo，并说明是否发现/覆盖其他相关 org。
- [ ] 已给出全 repo 活跃度排行榜、排序公式、Top repo 阈值和 sensitivity check。
- [ ] Top 活跃 repo 的 PR 活动分析来自数据驱动筛选，而非预设仓库。
- [ ] PR 分类有代表 PR、代码路径、状态和 evidence level，不只用标题关键词。
- [ ] 重大功能/架构变更区分 spec、merged、released、devnet、testnet、mainnet 和 governance 状态。
- [ ] 叙事分析同时引用 GitHub 活动和 Optimism 官方公开信息。
- [ ] Base 独立化讨论区分技术独立、Superchain 关系、竞争叙事和公开证据。
- [ ] Mantle 启示分为必须跟踪、值得 POC、谨慎不照搬、叙事回应和行动建议。
- [ ] 明确列出低置信度结论、缺失数据、反例和需要 Mantle 工程团队复核的问题。
- [ ] 未复用旧 Optimism artifact 的结论作为事实；旧 artifact 只能作为反例和质量风险提醒。
