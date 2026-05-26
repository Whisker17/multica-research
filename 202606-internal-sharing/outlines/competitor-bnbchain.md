---
topic: "BNB Chain 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-bnbchain"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/competitor-bnbchain.md"
  draft: "202606-internal-sharing/research-sections/competitor-bnbchain/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/competitor-bnbchain/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  三步法研究 BNB Chain 近期开发与叙事变化：
  (1) 扫描 `bnb-chain`（223 repos）、`node-real`（70 repos）及经验证相关 org 下全部可见 repo，
  按近 3 个月活跃度（PR 数量、commit 频率、contributor 活跃度、release/tag）排序，
  数据驱动筛选 Top 活跃 repo，不预设分析对象；
  (2) 针对筛选 repo 分析主要开发方向与 PR 分类、重大功能变更与架构调整、开发活跃度趋势；
  (3) 结合 GitHub 活动与公开信息，分析叙事变化：BSC 主链性能/EVM 演进、
  reth 双客户端策略、opBNB（L2）策略定位、BNB Greenfield 生态进展、
  Binance 生态整合（CeFi 流量/合规/机构）、AI Agent 赛道布局、
  DeFi/RWA 赛道布局、对 Mantle 的竞争启示。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、Mantle 协议/客户端/基础设施/生态与战略团队、
  Research Review Agent 和 Orchestrator。读者熟悉 L2、OP Stack、Mantle 架构，
  但需要一份以最新公开开发活动和官方叙事为基础、可复核且不预设 repo 结论的竞争对手近况梳理。

expected_output: |
  一份中文结构化 research section，涵盖：
  - BNB Chain 相关 GitHub org/repo 的近 3 个月活跃度数据集、排序方法、Top 活跃 repo 概况和排除项；
  - Top 活跃 repo 的 PR 活动分类、主要开发方向、重大功能变更、架构调整和活跃度趋势变化；
  - BNB Chain 近期叙事演变：Mendel/Pasteur 硬分叉、reth 双客户端、短出块间隔、MEV 基础设施、
    AI Agent 赛道、Greenfield 存储、opBNB L2 定位、Binance 生态整合；
  - 对 Mantle 的竞争启示：直接威胁、可借鉴设计、不可照搬约束、短中长期行动建议；
  - 至少 5 张图/表：org/repo universe 表、repo 活跃度排行榜、Top repo PR 趋势图、
    PR 分类矩阵、叙事演变时间线、Mantle 竞争响应矩阵。

source_requirements_summary: |
  Deep phase 必须优先使用 primary source。第一步必须直接查询 GitHub org/repo/PR/commit/contributor/release
  数据，固定近 3 个月窗口并记录查询时间、查询语句、分页完整性、rate-limit caveat、去重规则和排序公式。
  BNB Chain 官方 blog/docs、BEP 提案、Binance 官方资料和可核验链上/benchmark 数据必须作为一手来源。
  时间敏感事实不得沿用旧 artifact 或本 outline 的示例。

methodology_gate:
  repo_discovery_first: true
  prohibition: "不得预设只分析 bsc 或 reth-bsc；不得在完成 org-wide repo 活跃度排序前决定最终分析 repo 列表。"
  required_orgs: ["bnb-chain", "node-real"]
  related_org_policy: "通过 BNB Chain 官网/docs/blog、GitHub repo metadata、package namespace、官方链接和 GitHub search 发现其他相关 org，并记录纳入/排除理由。"
  time_window: "默认以 deep draft 抓取日向前 3 个月；如 2026-05-26 抓取，记录为 2026-02-26 至 2026-05-26 UTC，并在 draft 中写明实际抓取时间。"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-26T14:10:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-26T14:10:00+08:00"

multica_issue_id: "30e0bc57-0614-46b4-b3e8-7fbe62485e40"
branch_name: "research/202606-internal-sharing/competitor-bnbchain"
base_commit: "196f34d"
language: "中文"
research_depth: "standard"
---

# Research Outline: BNB Chain 近期开发与叙事分析

## Methodology Gate

Deep draft 开始前必须先完成 `item-1` 和 `item-2` 的 org/repo universe 发现与活跃度排名，并把完整排序表写入草稿第一部分。只有在 repo 活跃度排名表完成后，才能确定后续 PR 深挖对象。

初步扫描发现（outline 阶段预览，deep draft 必须重新验证）：
- `bnb-chain` org 共 223 repos，近 3 个月按 PR 数量排序前列：`bsc`（92 PRs）、`reth`（91 PRs）、`reth-bsc`（58 PRs）、`bnbagent-sdk`（30 PRs）、`bnb-chain.github.io`（24 PRs）、`BEPs`（22 PRs）
- `node-real` org 共 70 repos，活跃度显著低于 `bnb-chain`，近 3 个月几乎无显著 PR 活动
- 核心开发集中在 BSC Go 客户端和 reth Rust 客户端两条线

最低执行要求：

- 扫描 `bnb-chain`、`node-real` 全部可见 repo，并通过 BNB Chain 官网/docs/blog、repo README、GitHub topics、package namespace 和 GitHub search 发现其他相关 org/repo。
- 对 archived、fork、template、mirror 等 repo 分别标注类型。
- 统计近 3 个月 PR created、PR merged、PR closed、commit count、active contributors、release/tag、default branch push、issue/discussion activity。
- 形成可复核排序公式。建议基础权重：merged PR 30%、PR created 20%、commit count 20%、active contributors 15%、release/tag/default-branch recency 10%、issue/discussion signal 5%；如调整权重必须解释。
- 选择 Top 5-8 活跃 repo 作为候选，最终深挖数量可按数据分布收敛到 Top 3-6，但必须保留完整排名附录。
- `node-real` org 如活跃度不足，需明确说明并记录排除理由，不得简单忽略。

## Research Questions

1. 近 3 个月内，`bnb-chain`、`node-real` 和其他经验证相关 org 下哪些 repo 实际最活跃？排序依据是什么，Top repo 是否集中在 `bsc` 和 `reth-bsc`，还是 Greenfield、opBNB、SDK、docs、AI agent 或 contracts repo 也显示出显著投入？
2. BNB Chain 的 reth 双客户端策略（`reth-bsc` + `reth`）投入规模如何？与 Go 客户端 `bsc` 的关系是替代、互补还是并行？reth v0.0.9 → v2.0.0 升级意味着什么？
3. Mendel 硬分叉（2026 年 3 月主网）和 Pasteur 硬分叉（准备中）各包含哪些核心 BEP？BEP-670（250ms 出块）、BEP-675（builder-proposed blocks）、BEP-677（EIP-8056）、BEP-667（vote interval）等对 BSC 性能和架构有何影响？
4. BNB Chain 的 AI Agent 叙事（`bnbagent-sdk`、`bnbchain-mcp`、BEP-692）是工程实质还是营销驱动？SDK 活跃度和功能成熟度如何？
5. opBNB（L2）近期 PR 活跃度极低（3 PRs），Laplace 硬分叉进展如何？opBNB 在 BNB Chain 整体战略中的定位是否边缘化？
6. Greenfield 近期仍有多个硬分叉（cerrado、steppe），存储生态实际进展如何？是否从去中心化存储叙事转向其他方向？
7. BSC MEV 基础设施（`bsc-mev-sentry`、BEP-675）发展方向是什么？对 builder/validator 分离有何影响？
8. BNB Chain 的近期发力对 Mantle 构成哪些竞争压力：性能口径（250ms 出块 vs Mantle）、客户端多样性（reth vs Mantle 单客户端）、AI/Agent 叙事、交易所背景优势、生态规模？
9. Mantle 应该立即跟踪什么、借鉴什么、避免照搬什么，并如何转化为工程 watchlist 和行动建议？

## Items

### item-1: GitHub org/repo universe 发现与纳入边界

建立研究对象边界。该项不是分析预设 repo，而是先发现 BNB Chain 相关代码资产和文档/生态资产分布。必须从 GitHub API/GraphQL/gh CLI 拉取 `bnb-chain`（223 repos）、`node-real`（70 repos）全部可见 repo，并补充官方链接和搜索验证是否存在相关 org/repo。

必须覆盖：

- `bnb-chain`、`node-real` 全 repo 清单：repo name、URL、description、archived/fork/template 状态、default branch、primary language、stars/forks、created/updated/pushed_at；
- 相关 org/repo 发现：从 BNB Chain 官网、docs、blog、GitHub topics、repo README、package metadata 搜索是否存在其他官方/半官方 repo（例如 Binance 旗下相关 org）；
- repo 类型标注：core protocol/client（bsc/reth-bsc/reth）、L2/rollup（opbnb/op-geth）、storage（greenfield 系列）、contracts/BEP/spec、SDK/API/CLI、AI agent、docs/website、MEV/builder、bridge/cross-chain、wallet/app、infra/devops、examples/demo、deprecated/archive；
- 纳入/排除规则：archived repo 默认排除活跃排序但保留清单；fork/mirror 单列；`node-real` 低活跃 repo 需说明排除理由；
- 输出完整 repo universe 表，作为后续 ranking 的输入。

- **Priority**: critical
- **Dependencies**: none

### item-2: 近 3 个月 repo 活跃度排名与 Top repo 选择

对 `item-1` 的 repo universe 做数据驱动排序，决定后续 PR 深挖对象。该项是本研究硬门槛，deep draft 不得跳过。

必须覆盖：

- 时间窗口固定为 deep draft 抓取日向前 3 个月，所有查询使用 UTC 日期并说明边界；
- 每个 repo 的 PR created、PR merged、PR closed、commit count、active contributors、active weeks、default branch pushes、release/tag 数、recent issue/discussion activity；
- 排序公式和权重；至少给出总分、各指标原始值、归一化值、rank；
- 噪声处理：dependabot/renovate、bot-generated、archived/fork repo（如 `greenfield-cometbft-db` 的 14 PRs 全为 dependabot）；
- Top repo 选择规则：初步预览建议 Top 6 候选为 `bsc`、`reth`、`reth-bsc`、`bnbagent-sdk`、`BEPs`、`greenfield`，但必须由 deep draft 数据验证；
- 敏感性检查：PR-only、commit-only、contributors-only 四种视角是否改变 Top repo；
- `node-real` org 活跃度极低的定量说明和排除理由。

- **Priority**: critical
- **Dependencies**: item-1

### item-3: Top repo PR 活动基线与原始数据表

针对 `item-2` 选出的 Top repo，建立 PR 级事实底座。

必须覆盖：

- 每个 Top repo 的 PR 原始表：repo、PR number、title、state、created_at、merged_at/closed_at、author、is_bot、labels、changed files、additions/deletions、touched directories、source URL；
- 每周 PR created / merged / closed / still-open 趋势；
- merge latency、large PR 占比、revert/hotfix/release PR 占比；
- contributor 分布：BNB Chain core team、NodeReal、外部贡献者、bot；
- 跨 repo 协同：同一功能（如 Mendel 硬分叉）是否同时触达 bsc、reth-bsc、BEPs、genesis contracts、docs；
- GitHub API 限制、private work 不可见、squash merge caveats。

- **Priority**: high
- **Dependencies**: item-2

### item-4: PR 分类体系与开发方向分布

把 Top repo 的 PR 数据转化为开发方向图谱。分类应先由 repo/path/labels/title/PR body/changed files 证据生成，再合并成研究可读类别；若数据发现新方向，必须新增分类。

建议分类（基于初步扫描）：

1. **硬分叉与协议升级**：Mendel/Pasteur 相关 BEP 实现、Osaka EVM 对齐、hardfork config、参数调整；
2. **reth 双客户端**：reth-bsc/reth 客户端开发、v2.0.0 升级、prefetcher warmup、system tx 分类、P2P 协议；
3. **短出块间隔与性能**：BEP-670（250ms blocks phase 4）、miner 优化、block timing、vote broadcast tuning（BEP-626 450ms 参数）；
4. **快速最终性与投票机制**：BEP-667（vote interval）、fast finality consensus、votepool 改进、vote rate-limiting；
5. **MEV 基础设施**：BEP-675（builder-proposed blocks with validator blind signing）、bsc-mev-sentry、greedy merge buffer；
6. **AI Agent 与新赛道**：bnbagent-sdk、bnbchain-mcp、BEP-692（BNBAgent SDK Identity/Commerce/Payment）、ERC-8183；
7. **Greenfield 存储**：cerrado/steppe 硬分叉、storage provider 改进、cosmos-sdk/cometbft 上游；
8. **opBNB L2**：Laplace 硬分叉、op-geth/opbnb 维护、op-enclave TEE；
9. **Genesis 合约与系统合约**：bsc-genesis-contract、validator 相关、consensus key rotation；
10. **文档/开发者体验**：bnb-chain.github.io、BEP 文档、developer-tools-list；
11. **桥/跨链**：canonical-bridge、Mayan/LayerZero 集成；
12. **运维/可靠性/安全**：CI、dependency security、node-deploy、snapshot 管理。

每类需要输出 PR 数量/占比、代表 PR、repo 分布、趋势变化、实现状态和置信度。

- **Priority**: high
- **Dependencies**: item-3

### item-5: BSC 主链重大变更与硬分叉路线深挖

从分类结果中筛出真正影响协议行为、架构和性能的变化。

必须覆盖：

- **Mendel 硬分叉**（2026-03-24 主网）：核心 BEP 内容、Osaka/EVM 对齐范围、BSC v1.7.1 release；
- **Pasteur 硬分叉**（准备中）：BEP-657、BEP-670（250ms）、BEP-675（builder blocks）、BEP-677（EIP-8056）、BEP-682（CometBFT light block validator）；计划时间线和当前状态；
- **短出块间隔演进**：从 3s → 1s → 500ms → 450ms → 250ms 的路线，BEP-670 phase 4 的技术挑战和影响；
- **快速最终性改进**：BEP-667 vote interval 放松、vote rate-limiting、finality 分析更新；
- 每个重大变更的实现状态：merged-code / released / testnet / mainnet-active / feature-gated / roadmap；
- BSC v1.7.1 → v1.7.3 release 节奏和内容。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: reth 双客户端策略分析

BNB Chain 在 `reth-bsc`（58 PRs）和 `reth`（91 PRs）上的大量投入是近期最显著的工程方向之一。必须专门分析其战略含义。

必须覆盖：

- `reth-bsc` 与 `reth` 的关系：`reth` 是上游 fork（paradigmxyz/reth），`reth-bsc` 是 BSC 特定功能层？还是两者功能重叠？
- v0.0.9 → v2.0.0 版本升级的范围和含义；
- `reth-bsc` 的 BSC 特有功能：parlia 共识、system tx、BSC protocol、prefetcher warmup、cross region test；
- `reth-bsc-triedb`（fork of geth-compatible trie database）的角色；
- reth-bsc 的产品成熟度：是否已用于生产、测试网状态、性能对比；
- 与 Go 客户端 `bsc` 的关系：替代、互补还是冗余？是否存在客户端多样性战略？
- 已归档的 `reth-bsc-trail` 与当前 `reth-bsc` 的关系；
- 对 Mantle 的启示：Mantle 是否需要 reth 客户端？客户端多样性 vs 单客户端维护成本。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-7: opBNB L2 定位与发展评估

opBNB 近 3 个月 PR 活跃度极低（`opbnb` 3 PRs、`op-geth` 8 PRs），需要评估其在 BNB Chain 整体战略中的实际地位。

必须覆盖：

- Laplace 硬分叉进展：`op-geth` #320（feat: op-geth supports Laplace hardfork）和 `opbnb` #337（feat: implement Laplace hardfork in op-node）均为 open 状态；
- opBNB 的 OP Stack 版本和上游跟进状态；
- opBNB vs BSC 在 BNB Chain 生态中的定位：opBNB 是否被边缘化、BSC 自身性能提升是否减少 L2 需求；
- opBNB 的 TVL、用户活跃度等链上指标（如可获取）；
- `op-enclave`（TEE 状态转换）的状态和意义；
- 与 Mantle 的对比：opBNB 作为 OP Stack L2 vs Mantle 作为 OP Stack L2 的竞争关系和差异。

- **Priority**: medium
- **Dependencies**: item-3, item-4

### item-8: Greenfield 去中心化存储生态评估

Greenfield 近期仍有活跃开发（多个硬分叉），但需要评估其生态实际进展。

必须覆盖：

- 近期硬分叉：cerrado、steppe 的核心内容和目标；
- Greenfield 相关 repo 活跃度：`greenfield`（8 PRs）、`greenfield-cosmos-sdk`（17 PRs）、`greenfield-storage-provider`（9 PRs）、`greenfield-cometbft-db`（14 PRs 但多为 dependabot）；
- Greenfield 的核心功能更新：SP2SP auth、bucket counter 性能、数据安全；
- NodeReal 的 dcellar（Greenfield 前端）活跃度下降信号；
- Greenfield 在 BNB Chain 整体叙事中的定位变化：是否仍为战略重点，还是转为维护模式；
- Greenfield 与 AI Agent 的潜在关联（数据存储 + AI）；
- 对 Mantle 的启示：去中心化存储是否为 L1/L2 的必要叙事组件。

- **Priority**: medium
- **Dependencies**: item-3, item-4

### item-9: AI Agent 赛道布局与叙事分析

BNB Chain 近期在 AI Agent 方向投入显著（`bnbagent-sdk` 30 PRs），需要评估其工程实质和叙事意义。

必须覆盖：

- `bnbagent-sdk`：功能范围（Python toolkit for on-chain AI agents）、PR 分类、成熟度、contributor 分布；
- `bnbchain-mcp`（MCP server for BNB Chain）：Model Context Protocol 集成、支持 BSC/opBNB/Greenfield；
- BEP-692（BNBAgent SDK — Identity/Commerce/Payment/Memory）：提案状态和范围；
- ERC-8183（pluggable verifiable evaluator）在 bnbagent-sdk 中的集成；
- `eliza-plugin-bnb-v2`、NodeReal `bnb-chain-agentkit` 等生态工具；
- 与其他链 AI Agent 叙事的对比（Solana、Base 等）；
- 工程实质 vs 营销驱动的判断：代码质量、测试覆盖、生产用例、开发者采用；
- 对 Mantle 的启示：AI Agent 赛道是否值得投入、最小可行策略。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-10: 开发活跃度趋势与工程组织信号

判断 BNB Chain 近期是协议创新加速、产品化推进、维护稳定还是多线并行扩散。

必须覆盖：

- Top repo 每周活动趋势、release 前后峰值、issue/discussion 变化；
- merge latency、review 密度、large PR、revert/hotfix PR 占比；
- contributor 集中度：核心 contributors（allformless、zlacfzy、will-2012、constwz、flywukong、sysvm、chee-chyuan）的跨 repo 分布；
- 多线并行信号：BSC Go + reth Rust + Greenfield + AI Agent + opBNB 五条线的资源分配推测；
- BSC Go 客户端 vs reth 客户端的开发者重合度和分工；
- 跨 repo 节奏：Mendel/Pasteur 硬分叉是否从 BEP → bsc → reth-bsc → genesis contracts → docs 形成完整链条；
- 对 Mantle 可比指标：核心协议变更频率、release velocity、客户端投入、新赛道投入。

- **Priority**: medium
- **Dependencies**: item-3, item-4, item-5, item-6

### item-11: Binance 生态整合与叙事时间线

把 GitHub 活动与 BNB Chain/Binance 公开信息连接起来，分析整体叙事方向。

必须覆盖：

- BNB Chain 官方 blog/docs、Binance 公告中的叙事变化；
- 叙事关键词演变：EVM 高性能 L1、短出块间隔、AI Agent、Greenfield 存储、DeFi/RWA；
- 叙事时间线：Mendel 主网上线（2026-03）、Pasteur 准备、reth 双客户端推进、AI Agent SDK 发布；
- Binance 交易所与 BSC 的生态绑定：CeFi 流量导入、合规策略、机构服务；
- BEP-677（EIP-8056 Scaled UI Amount）与 token 标准演进的叙事意义；
- 代码活动如何支撑或削弱叙事：engineering-heavy（reth、短出块间隔）vs narrative-heavy（AI Agent）的区分；
- BNB Chain 是否从"Binance 的链"转向更独立的生态定位。

- **Priority**: medium
- **Dependencies**: item-5, item-6, item-8, item-9

### item-12: 横向竞争定位与对 Mantle 的行动建议

将 BNB Chain 近期开发和叙事变化转化为 Mantle 可执行判断。

必须覆盖：

- **必须跟踪 / 防守**：BSC 短出块间隔路线（250ms 目标）、reth 双客户端进展、Pasteur 硬分叉上线、AI Agent SDK 采用情况、opBNB 与 Mantle L2 竞争态势；
- **值得借鉴 / POC**：reth 客户端投入评估、BEP-675 builder separation 设计、快速最终性参数调优方法、MCP/Agent 集成模式、BEP 流程效率；
- **谨慎 / 不适合直接照搬**：BSC 250ms 出块对 Mantle 架构的适用性（Mantle 基于 OP Stack 而非 Parlia 共识）、AI Agent SDK 全量复制（Mantle 生态规模差异）、Greenfield 存储层整合（Mantle DA 方案不同）；
- **竞争叙事回应**：Mantle 如何解释自己与 BNB Chain 的差异：EigenDA/DA strategy、MNT economics、L2 定位 vs L1 竞争、OP Stack 生态优势；
- **定量对比**：BSC vs Mantle 的核心开发投入差异（contributor 数量、PR velocity、多客户端投入）；
- **行动建议**：短期工程 watchlist，中期架构/功能 POC，长期客户端/性能/新赛道路线选择。

- **Priority**: high
- **Dependencies**: item-5, item-6, item-7, item-8, item-9, item-10, item-11

### item-13: 证据完整性、反例和风险控制

为 adversarial review 预留独立可检查的质量门。

必须覆盖：

- 数据完整性：GitHub API 是否漏页、rate limit、private repo 不可见、archived/fork 处理、bot PR 去噪；
- 结论反例：高活跃 repo 可能只是 dependabot/CI/deps（如 `greenfield-cometbft-db`）；低活跃 repo 可能因成熟稳定但战略重要（如 `opbnb`）；
- 状态误读防线：open PR、merged PR、released code、testnet、mainnet-active 必须分开（如 Laplace 硬分叉 PRs 仍为 open）；
- 叙事误读防线：BNB Chain 官方叙事、BEP 提案、生态媒体、第三方评论、内部推断必须分层；
- BNB Chain / Mantle 比较防线：不可把 BSC L1 性能参数直接对标 Mantle L2、不可把交易所背景优势当作可复制资产；
- 输出：confidence/gaps 表和 "claims not supported" 列表。

- **Priority**: high
- **Dependencies**: item-1 through item-12

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| repo_universe_record | repo/org 基础信息、纳入/排除理由、repo 类型、archived/fork 状态 | item-1 |
| activity_metrics | PR created/merged/closed、commit count、contributors、active weeks、release/tag、push recency、bot PR 占比 | item-2 |
| activity_score | 排序公式、权重、归一化值、rank、敏感性检查结果 | item-2 |
| pr_evidence | 代表 PR 的 number、title、state、date、author、changed paths、source URL、status | item-3, item-4, item-5, item-6 |
| classification_label | PR/变更所属开发方向分类，可多标签但必须说明主标签 | item-4, item-5, item-9 |
| implementation_status | spec / open-pr / merged-code / released / testnet / mainnet-active / feature-gated / roadmap / experimental / docs-only / inferred | item-4, item-5, item-6, item-7, item-8, item-9 |
| evidence_confidence | 证据置信度：primary-verified / cross-verified / code-observed / official-claim / inferred / unsupported | all |
| hardfork_status | 硬分叉名称、BEP 列表、目标网络、activation time、当前状态 | item-5, item-7, item-8 |
| narrative_signal | 叙事标签、官方措辞、发布日期、对应 GitHub 证据、narrative-heavy 或 engineering-heavy 判断 | item-9, item-11 |
| reth_client_maturity | reth 客户端版本、功能覆盖、生产就绪度、与 Go 客户端差异 | item-6 |
| mantle_implication | 对 Mantle 的威胁、借鉴价值、不可迁移约束、行动建议 | item-6, item-7, item-9, item-12 |
| gaps_and_risks | 数据缺口、反例、unsupported claims、需刷新的事实 | item-13 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | table | BNB Chain 相关 org/repo universe 表：org、repo、类型、archived/fork、last pushed、primary language、纳入/排除理由 | markdown table | item-1 |
| diag-2 | ranked-table | Top repo 活跃度排行榜：repo、PR created/merged、commits、contributors、release signal、activity score、rank | markdown table | item-2 |
| diag-3 | timeline | Top repo 周度 PR created/merged 趋势，标注 release/hardfork/major PR 峰值 | mermaid xychart or markdown table | item-3, item-10 |
| diag-4 | matrix | PR 分类矩阵：分类 x Top repo，填入 PR 数量、代表 PR、status | markdown table | item-4, item-5 |
| diag-5 | architecture | BNB Chain 技术栈分层图：BSC L1 (Go + reth)、opBNB L2、Greenfield 存储、AI Agent SDK，标注各层活跃度和核心 BEP | mermaid flowchart | item-5, item-6, item-7, item-8 |
| diag-6 | timeline | BNB Chain 叙事演变时间线：Mendel → Pasteur 硬分叉、reth 双客户端里程碑、AI Agent SDK、250ms 出块目标 | mermaid timeline | item-5, item-9, item-11 |
| diag-7 | matrix | Mantle 竞争响应矩阵：威胁面、BNB Chain 证据、Mantle 当前状态、可行动作、优先级 | markdown table | item-12 |
| diag-8 | evidence-map | 关键 claims 证据地图：claim、primary source、supporting source、status、confidence | markdown table | item-13 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | github_org_data | `bnb-chain`、`node-real` 及发现的相关 org 的 repo list、metadata、PR、commit、contributors、release/tag 原始查询结果，需记录查询时间和命令/API | 2 orgs |
| src-2 | github_pr_analysis | Top 活跃 repo 的 PR/commit/release 永久链接；每个 Top repo 至少 5 个代表 PR | 5 per Top repo |
| src-3 | bep_proposals | BEP-667、BEP-670、BEP-675、BEP-677、BEP-682、BEP-692 等近期 BEP 全文，用于硬分叉和新功能验证 | 6 |
| src-4 | official_bnbchain_docs | BNB Chain 官方 blog、docs、release notes、hardfork 公告，用于叙事和路线验证 | 4 |
| src-5 | on_chain_data | BSC/opBNB 主网/测试网指标：TPS、block time、gas、TVL、用户活跃度，需区分 official claim 和 third-party dashboard | 3 |
| src-6 | comparison_sources | Mantle 现有代码/研究、OP Stack 资料、L2Beat 等，用于竞品与 Mantle 影响判断 | 3 |

## Quality Checklist

- [ ] `item-1` 和 `item-2` 在 draft 首部完成，且 final repo list 来自数据排序而非先验。
- [ ] 完整 repo universe、activity ranking、Top repo selection/exclusion 表均可复核。
- [ ] 每个重大 claim 都有 implementation_status 与 evidence_confidence。
- [ ] Mendel/Pasteur 硬分叉的 BEP 列表和激活状态有 primary source 支持。
- [ ] reth 双客户端分析区分了 `reth`（上游 fork）和 `reth-bsc`（BSC 特定）。
- [ ] opBNB 低活跃度判断有定量数据支持，未简单等同于"被放弃"。
- [ ] AI Agent 叙事区分了工程实质（代码成熟度）和营销驱动（BEP 提案/官方宣传）。
- [ ] `node-real` org 低活跃度有明确排除理由和数据支持。
- [ ] BSC L1 性能参数未与 Mantle L2 直接对标（不同共识和架构）。
- [ ] 对 Mantle 建议可执行，包含 watchlist、POC、不可照搬项。
- [ ] `claims not supported` / gaps 表列出 final 中不能写或需降级的说法。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create_outline | all | 根据 Orchestrator dispatch 创建 BNB Chain 近期开发与叙事分析 outline；基于初步 GitHub org 扫描数据（bnb-chain 223 repos, node-real 70 repos）设计研究框架 | Orchestrator dispatch comment 76055cbf-bf59-4b92-b84e-21d306fd085f |
