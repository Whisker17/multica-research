---
topic: "Arbitrum 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-arbitrum"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/competitor-arbitrum.md"
  draft: "202606-internal-sharing/research-sections/competitor-arbitrum/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/competitor-arbitrum/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  分析 Arbitrum 近 3 个月 GitHub PR 活动与叙事变化，重点仓库为 `OffchainLabs/nitro`
  和 `OffchainLabs/stylus-sdk-rs`。研究需覆盖主要开发方向与 PR 分类、重大功能变更与架构调整、
  开发活跃度趋势；同时分析 Stylus WASM 智能合约生态、Orbit L3 生态扩展、Timeboost 拍卖机制、
  BoLD 争议协议、与 Optimism Superchain 的竞争关系，并最终提炼对 Mantle 的竞争启示。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、协议/客户端/基础设施工程师、
  生态与战略团队，以及 Multica Research Squad 的 Review Agent 和后续写作者。读者熟悉
  L2/OP Stack/Rollup、Arbitrum Nitro、fraud proof、sequencer、WASM 智能合约和应用链概念，
  但需要一份以近 3 个月公开开发活动和官方叙事为基础的竞争对手近况梳理。

expected_output: |
  一份中文结构化 research section，涵盖：
  - Arbitrum 近 3 个月 `OffchainLabs/nitro` 与 `OffchainLabs/stylus-sdk-rs` GitHub 活动概况、
    活跃度趋势、PR 分类统计和代表 PR
  - Nitro 的主要开发方向变化：BoLD / fraud proof、Timeboost、Orbit / AnyTrust、Stylus 集成、
    sequencer / batcher / node / validator / tooling / release engineering
  - Stylus WASM 智能合约生态进展：SDK、语言支持、示例、工具链、审计/安全边界、主网采用信号
  - Orbit L3 生态扩展、Timeboost 拍卖机制和 BoLD 争议协议的工程状态与叙事意义
  - Arbitrum 与 Optimism Superchain / Base Stack / Mantle 的竞争定位对比
  - 对 Mantle 的竞争启示：必须跟踪的兼容/安全/MEV 风险、可借鉴设计、不适合照搬的边界、
    短中长期行动建议和需要工程团队复核的问题

source_requirements_summary: |
  深度研究必须以 primary source 为主。GitHub 活动需直接查询 `OffchainLabs/nitro` 与
  `OffchainLabs/stylus-sdk-rs` 在固定 3 个月窗口内的 PR / commit / release 数据，并记录查询时间、
  查询语句、状态分布、去重规则和代表 PR。叙事分析需优先引用 Arbitrum / Offchain Labs 官方 docs、
  blog、release notes、治理论坛、DAO proposal、Orbit / Stylus / Timeboost / BoLD 文档与代码。
  任何来自行业文章、社交媒体或二级数据平台的说法都必须用 GitHub、官方文档、链上/治理或 L2Beat
  等一手/准一手来源交叉验证。时间敏感事实必须在 draft 阶段重新核验，不得只引用旧研究或本 outline。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-23T11:58:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-23T11:58:00+08:00"

multica_issue_id: 764c2f01-8fd0-4620-bf51-3c6a8397bf46
branch_name: research/202606-internal-sharing/competitor-arbitrum
base_commit: 4d52e841496cccc7a4c2640ef0f96cbd6e55a637
language: 中文
research_depth: standard

prerequisite_sections:
  - slug: competitor-optimism
    path: 202606-internal-sharing/research-sections/competitor-optimism/final.md
    status: existing-research
  - slug: competitor-base
    path: 202606-internal-sharing/research-sections/competitor-base/final.md
    status: existing-research
  - slug: stage1-case-studies
    path: mantle-stage1-rollup/research-sections/stage1-case-studies/final.md
    status: existing-research
  - slug: upgrade-exitwindow-securitycouncil
    path: mantle-stage1-rollup/research-sections/upgrade-exitwindow-securitycouncil/final.md
    status: existing-research
  - slug: mantle-impact-assessment
    path: base-azul-upgrade/research-sections/mantle-impact-assessment/final.md
    status: existing-research
  - slug: architecture-advantage-summary
    path: mantle-base-codebase-evaluation/research-sections/architecture-advantage-summary/final.md
    status: existing-research
---

# Research Outline: Arbitrum 近期开发与叙事分析

## Research Questions

1. 2026-02-23 至 2026-05-23 期间，`OffchainLabs/nitro` 与 `OffchainLabs/stylus-sdk-rs` 的 PR 活动总量、合并节奏、活跃模块和开发者分布如何变化？
2. Nitro 近期 PR 可以归纳出哪些开发主线：BoLD / dispute protocol、Timeboost、Orbit / AnyTrust / L3、Stylus integration、sequencer / batcher / validator、node reliability、release engineering、docs / tooling？
3. `stylus-sdk-rs` 的 PR 活动和 release 节奏是否显示 Stylus 正从技术预览走向更成熟的 Rust / WASM 合约开发生态？哪些只是 SDK/DX 改进，哪些影响合约安全和生产可用性？
4. Arbitrum 近期重大功能变更或架构调整有哪些？这些变化分别处于 spec、merged code、testnet、mainnet-active、governance-approved、experimental 或 deprecated 哪一阶段？
5. Timeboost 是否从 MEV / ordering 叙事推进到可验证的代码、部署、治理或市场机制设计？它对用户体验、sequencer 收入、MEV 外部性和应用链差异化意味着什么？
6. BoLD 争议协议在近 3 个月的开发和治理状态如何？它对 Arbitrum Stage 1、permissionless validation、challenge period、walkaway / exit window 叙事的实际贡献是什么？
7. Orbit L3 生态扩展是否构成 Arbitrum 对 Optimism Superchain 的主要竞争叙事？Orbit 的技术路线、治理边界、DA 选项、共享流动性/互操作性和商业模式与 Superchain 有何差异？
8. 对 Mantle 而言，Arbitrum 的近期开发和叙事变化构成哪些竞争压力、可借鉴设计、不可照搬约束和短中长期行动建议？

## Items

### item-1: GitHub 活动基线、数据口径与 PR 分类方法

建立 Arbitrum 近 3 个月开发活动的事实底座。研究需直接查询 `OffchainLabs/nitro` 与 `OffchainLabs/stylus-sdk-rs` 在 2026-02-23 至 2026-05-23 的 PR 数据，明确 open / merged / closed 口径、默认分支、bot PR、backport、release branch、revert、dependabot、docs-only 和 generated code 的处理规则。输出应包含周粒度 PR 趋势、merged/open/closed 分布、主要作者/模块、merge latency、代表 PR、关键 release 或 governance event 对齐。

必须覆盖：

- GitHub 查询方法：REST / GraphQL / `gh` CLI / GitHub Search 的具体 query、抓取时间、分页完整性和 rate-limit caveat；
- 两个重点 repo 的独立统计与合并视角：`nitro` 作为核心协议/节点仓，`stylus-sdk-rs` 作为 Stylus Rust SDK / WASM DX 仓；
- PR 分类体系：BoLD / fraud proof、Timeboost、Stylus / WASM、Orbit / AnyTrust / L3、sequencer / batcher / validator、node reliability、contracts / bridge / governance、release / CI / deps / docs；
- 代表 PR 选择规则：每类至少选 3-8 个高信号 PR，标注 PR 号、标题、状态、合并时间、作者、主要目录、证据链接；
- 证据等级：`github-search`、`pr-body-reviewed`、`code-diff-reviewed`、`release-confirmed`、`governance-confirmed`、`narrative-inferred`。

- **Priority**: high
- **Dependencies**: none

### item-2: Nitro 核心协议与节点架构开发方向

分析 `OffchainLabs/nitro` 近期 PR 的核心工程重心，而不是只按标题关键词计数。该项需要把 Nitro 改动拆成协议/合约层、validator / dispute 层、sequencer / batcher / feed 层、node / sync / database 层、Orbit / AnyTrust 层、Stylus 集成层和 release/ops 层，判断哪些变化对 Arbitrum One 主网、Nova、Orbit chains 或开发者工具有直接影响。

必须覆盖：

- Nitro 节点和 rollup pipeline 的关键改动：sequencer、batch poster、validator、delayed inbox、challenge manager、state transition、database / snapshot / pruning / sync；
- 与 BoLD、Timeboost、Stylus、Orbit 相关的代码 surface：涉及目录、包、配置、合约、测试、部署脚本和 feature flag；
- release engineering：tag、changelog、security fix、backport、network upgrade、config bump、CI / testnet / devnet 工作；
- 架构影响分类：协议行为改变、节点可靠性提升、运营成本优化、开发者 DX 改进、治理/部署准备、纯维护；
- 对 Mantle 的映射：哪些 Nitro 做法可作为 OP Stack 之外 rollup 客户端架构参考，哪些与 Arbitrum fraud proof / WASM AVM 体系强绑定。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Stylus WASM 智能合约生态与 `stylus-sdk-rs` 进展

评估 Stylus 的实际成熟度：Rust/WASM SDK 是否在安全性、标准库、ABI、gas / metering、tooling、examples、docs、testing 和 ecosystem adoption 上持续推进。该项需要把 `stylus-sdk-rs` PR 与 Nitro / Arbitrum docs / Stylus examples / audits / ecosystem announcements 交叉验证，避免把 SDK 小修误读为生态爆发。

必须覆盖：

- `stylus-sdk-rs` PR 分类：ABI / storage / calls / events / ERC examples、proc macro、host I/O、gas/metering helpers、testing, docs, dependencies, release；
- Stylus 与 EVM 互操作边界：EVM 合约调用 WASM、WASM 调用 EVM、precompile / host API、address / calldata / revert / event compatibility；
- 安全与生产可用性：SDK API 稳定性、unsafe boundary、panic/revert semantics、audits、known footguns、version compatibility；
- 生态信号：官方 examples、third-party contracts、hackathon/grant、mainnet deployment、tooling support；必须标注 evidence level；
- 与 Mantle 的竞争含义：WASM 合约能否扩大开发者语言栈、提升高性能合约叙事，Mantle 若要回应应走 EVM+precompile/zkVM/alt-VM/L3 哪条路径。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Orbit L3 / AnyTrust 生态扩展与应用链叙事

分析 Orbit 是否是 Arbitrum 对 Optimism Superchain 的核心差异化叙事。该项需从 Nitro PR、Orbit docs、Arbitrum ecosystem materials、DAO / grant / partnership announcements 和公开链配置数据中验证 Orbit 近期是否在技术能力、部署工具、DA 选择、治理模式和生态规模上有实质推进。

必须覆盖：

- Orbit chain 技术栈：Rollup vs AnyTrust、L2/L3 部署、DA Committee、custom gas token、chain config、bridge / inbox / outbox、batch posting、upgrade path；
- 近 3 个月 Nitro PR 是否增强 Orbit tooling、config、deployment、validator/node ops、chain registry、docs 或 test harness；
- Orbit 生态扩展证据：新增 chain、合作公告、ecosystem page、TVL/交易量/活跃地址、应用类型；必须区分官方 listing 与真实链上采用；
- 与 Optimism Superchain 对比：Orbit 更偏 permissioned appchain / custom stack，Superchain 更偏 shared governance / interoperability / standardization；需要避免简单判定优劣；
- 对 Mantle 的启示：Mantle L3 / enterprise / appchain / EigenDA / custom gas token 叙事如何借鉴 Orbit，同时保留与 OP Stack / Superchain 兼容性的选择权。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: Timeboost 拍卖机制、排序权市场与 MEV 叙事

拆解 Timeboost 的机制设计、代码状态、治理状态和叙事意义。研究必须区分"排序/抢跑缓解机制"、"MEV auction / express lane"、"sequencer revenue"、"user protection"和"应用链可配置排序权"五种语义，避免把 Timeboost 直接等同于最终用户无 MEV。

必须覆盖：

- Timeboost 机制：auction subject、express lane / ordering rights、bid settlement、latency / fairness assumptions、sequencer integration、fallback path；
- 代码与部署证据：Nitro PR、contracts、config、testnet/mainnet activation、feature flag、docs、governance proposal 或 audit；
- 经济与治理问题：收入归属、DAO / chain owner / sequencer 分配、参与者门槛、应用链自定义、market maker / searcher 影响；
- 用户与开发者影响：交易排序可预测性、MEV 外部性、latency tradeoff、application design、wallet/RPC 透明度；
- 与 Mantle 的相关性：是否值得研究排序权拍卖、preconfirm / MEV-sharing、sequencer decentralization 路径，以及需要规避的公平性和监管叙事风险。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-6: BoLD 争议协议、permissionless validation 与 Stage 1 安全叙事

评估 BoLD 在近 3 个月是否进入稳定化、主网运营、参数调整、审计修复或治理维护阶段。该项必须把 `nitro` PR、BoLD docs/spec、audit/security review、Arbitrum DAO proposal、L2Beat 状态和仓库内 Stage 1 研究交叉验证，避免把"已上线"、"permissionless validation"、"Stage 1"和"Stage 2"混为一谈。

必须覆盖：

- BoLD 技术面：challenge manager、assertion / edge / bisection game、WASM module root、validator permissionlessness、timeout / stake / bond / confirmation path；
- 近 3 个月 PR 是否涉及 BoLD bug fix、parameter tweak、validator tooling、watchtower / monitoring、contracts / deployment scripts、docs or test vectors；
- 治理与安全边界：DAO / Security Council / emergency upgrade path、challenge period、exit window、L2Beat walkaway / proving-system gates；
- 历史争议或风险：pre-mainnet bug、edge case、economic griefing、permissionless validator participation barriers；必须用 primary source 表述；
- 对 Mantle 的映射：BoLD 可作为 optimistic proof 路径参考，但 Mantle 若走 OP Stack / ZK / OP Succinct 路线，哪些经验可迁移，哪些与 Nitro architecture 强绑定。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-7: 开发活跃度趋势与工程组织信号

基于 item-1 的数据集，判断 Arbitrum 近期开发是功能扩张、主网硬化、SDK/DX 扩展、生态支撑还是维护收敛。该项不只统计 PR 数，还要分析 PR 质量、review latency、作者集中度、重大 PR / 小修 PR 比例、release cadence 和跨 repo 依赖。

必须覆盖：

- 周粒度 PR created / merged / closed 趋势，并标注 release、治理投票、testnet/mainnet activation、重大公告节点；
- 贡献者结构：Offchain Labs core、外部贡献者、bot / dependabot、ecosystem contributors 的比例；
- 模块集中度：Nitro core、contracts、validator/dispute、sequencer/feed、Orbit tooling、Stylus SDK、docs / CI / deps；
- 工作流质量：large PR、revert/follow-up、test coverage、release branch/backport、review cycle；
- 与叙事事件的关系：Stylus、Orbit、Timeboost、BoLD 对外叙事前后是否有代码或文档支撑；
- 与 Optimism/Base/Sui 同期竞品开发节奏的可比较口径，避免只用绝对 PR 数做结论。

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-3

### item-8: 叙事变化：Stylus + Orbit + Timeboost + BoLD 的组合定位

把工程活动映射到 Arbitrum 的外部叙事变化。该项应对照 Arbitrum 官方 blog、docs、governance forum、release notes、Offchain Labs engineering posts、ecosystem announcements 和 L2Beat/DAO data，判断 Arbitrum 是否正在把竞争主轴从"领先 optimistic rollup"扩展为"多 VM + appchain/L3 + ordering market + permissionless fraud proof"的组合叙事。

必须覆盖：

- Stylus 叙事：multi-language / WASM smart contracts、Rust/C/C++ developer reach、performance-sensitive contracts；
- Orbit 叙事：application chains、custom gas token、L3 / AnyTrust、ecosystem growth、enterprise/game/social/custom settlement；
- Timeboost 叙事：MEV internalization、sequencer revenue、auctioned ordering, fair ordering caveats；
- BoLD 叙事：permissionless validation、security maturity、Stage 1 / decentralization progress；
- 组合定位：Arbitrum 与 Optimism Superchain 的竞争不是同一维度，Arbitrum 更偏可定制技术栈与生态扩张，Optimism 更偏共享标准/互操作治理；需要用证据支持而非先验判断。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-6, item-7

### item-9: 与 Optimism Superchain / Base Stack / Mantle 的竞争对比

建立横向竞争框架，解释 Arbitrum、Optimism、Base 和 Mantle 在技术路线、治理、生态、性能和叙事上的差异。该项必须复用仓库内既有 `competitor-optimism`、`competitor-base`、Base Azul、Mantle codebase evaluation 和 Stage 1 研究，且对任何时间敏感结论重新校验。

比较维度至少包括：

- **技术栈**：Nitro / AVM / WASM Stylus vs OP Stack / op-reth / Base Stack vs Mantle OP-derived stack；
- **生态扩张**：Orbit L3 / AnyTrust vs Superchain shared standard / interop vs Base Coinbase distribution vs Mantle EigenDA / MNT / enterprise / payment ambitions；
- **MEV / latency / ordering**：Timeboost vs Flashblocks / preconfirm / Base performance claims vs Mantle sequencer roadmap；
- **安全与去中心化**：BoLD / Arbitrum DAO / Security Council vs OP Cannon / Superchain governance vs Base nested SC vs Mantle Stage 1 roadmap；
- **开发者心智**：Stylus WASM vs EVM / Solidity / OP Stack compatibility / Base distribution；
- **可迁移性**：哪些设计 Mantle 可直接借鉴、需要 POC、只适合作为叙事参考或应避免。

- **Priority**: high
- **Dependencies**: item-3, item-4, item-5, item-6, item-8

### item-10: 对 Mantle 的竞争启示与行动建议

将 Arbitrum 近期开发和叙事变化转化为 Mantle 可执行判断。结论必须区分工程可行性、产品价值、生态价值、治理风险和叙事价值，避免简单建议"复制 Stylus"或"推出 L3"。

必须输出四类建议：

1. **必须跟踪 / 防守**：
   - BoLD / Stage 1 / permissionless validation 口径对用户安全叙事的压力；
   - Timeboost 及排序权拍卖对 MEV、sequencer revenue 和应用链商业模式的影响；
   - Orbit L3 / custom gas token / AnyTrust 对 Mantle appchain 和 enterprise 叙事的竞争；
   - Stylus WASM 对非 Solidity 开发者和高性能合约叙事的吸引。
2. **可借鉴的设计**：
   - WASM/alt-VM developer funnel、SDK examples、tooling-first 生态策略；
   - L3 / appchain deployment playbook、custom gas token、DA choice、chain owner economics；
   - BoLD 的 permissionless validation 文档化、validator UX、challenge monitoring；
   - Timeboost 的机制研究和 sequencer revenue / MEV transparency 框架。
3. **需要谨慎验证或不宜照搬**：
   - 直接复制 Timeboost auction，可能引入 fairness、searcher capture、监管和用户感知风险；
   - 直接引入 WASM VM，可能造成 EVM 兼容、安全审计、工具链和生态碎片化成本；
   - 复制 Orbit L3 叙事但缺少明确 appchain demand 或 DA/bridge/ops 能力；
   - 将 Arbitrum BoLD 成功经验直接外推到 OP Stack / ZK 路线。
4. **短中长期行动**：
   - 短期：建立 Arbitrum PR watchlist、BoLD/Timeboost/Stylus/Orbit evidence dashboard、竞品叙事 rebuttal；
   - 中期：评估 Mantle L3 / appchain / custom gas token / MEV-sharing POC，补强开发者工具和安全叙事；
   - 长期：明确 Mantle 在 OP Stack compatibility、ZK proof、EigenDA、enterprise/payment 和 appchain 方向的组合定位。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7, item-8, item-9

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| evidence_window | 固定时间窗口、数据源、查询语句、抓取时间、分页完整性、PR Tracker 是否使用及覆盖缺口 | all |
| evidence_type | 证据类型：`merged-code` / `open-pr` / `closed-unmerged` / `release-note` / `official-doc` / `governance` / `onchain` / `internal-research` / `industry-commentary` / `inferred` | all |
| evidence_confidence | high / medium / low，并说明不确定性来源；open PR、二级评论和叙事推断默认不得标 high | all |
| pr_metadata | PR 号、标题、状态、创建/合并/关闭时间、作者、review 周期、标签、改动行数、主要目录、关联 issue/release | item-1, item-2, item-3, item-7 |
| pr_category | PR 分类：BoLD / Timeboost / Stylus / Orbit-AnyTrust / sequencer-batcher / node-validator / contracts-governance / release-ops / docs-deps-other | item-1, item-2, item-3, item-7 |
| implementation_status | 功能状态：spec-only / open-pr / merged-not-activated / testnet-active / mainnet-active / governance-approved / deprecated / unknown | item-2, item-3, item-4, item-5, item-6 |
| code_surface | 涉及 repo、目录、包、合约、配置、测试和关键文件；必须记录 commit 或 PR permalink | item-2, item-3, item-4, item-5, item-6 |
| protocol_or_architecture_change | 是否改变协议行为、节点架构、合约接口、排序机制、DA/Orbit 部署、validation/dispute 或开发者 ABI/API | item-2, item-3, item-4, item-5, item-6 |
| narrative_claim | 官方或社区叙事主张：Stylus multi-language、Orbit L3 ecosystem、Timeboost MEV auction、BoLD permissionless validation、Arbitrum vs Superchain | item-8, item-9 |
| narrative_evidence | 支撑叙事的证据：官方 blog/docs、PR、release、governance vote、ecosystem announcement、链上数据；区分事实与推断 | item-4, item-5, item-6, item-8, item-9 |
| orbit_chain_signal | Orbit 生态证据：chain listing、DA type、custom gas token、交易/地址/TVL、合作公告、是否 production；标注 adopted / announced / experimental | item-4, item-8, item-9 |
| stylus_ecosystem_signal | Stylus SDK release、contract examples、tooling、audit、mainnet deployment、developer adoption；标注 evidence level | item-3, item-8, item-9 |
| timeboost_economics | auction object、participant、settlement、revenue allocation、fairness / MEV caveat、deployment status | item-5, item-8, item-10 |
| bold_security_signal | BoLD challenge period、validator permissionlessness、bug/security fix、L2Beat state、DAO/SC controls、exit window relation | item-6, item-9, item-10 |
| competitor_comparison | 与 Optimism Superchain、Base Stack、Mantle 的维度化对比：技术栈、互操作性、治理、安全、MEV、开发者生态、分发 | item-8, item-9 |
| mantle_competitive_impact | 对 Mantle 的竞争影响：security narrative、developer mindshare、MEV/sequencer revenue、appchain/L3、enterprise/payment、ecosystem strategy | item-9, item-10 |
| transferability | 对 Mantle 的可迁移性：borrow_now / prototype / monitor / avoid / not_applicable，并说明工程成本与依赖 | item-3, item-4, item-5, item-6, item-10 |
| caveats_open_questions | 需要在 final section 中显式保留的事实缺口、冲突来源、口径争议、过期风险和需 Mantle 工程团队复核的问题 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | timeline | 2026-02-23 至 2026-05-23 Arbitrum 关键 PR / release / governance / ecosystem 事件时间线，按 Nitro core、Stylus、Orbit、Timeboost、BoLD 分泳道展示 | mermaid | item-1, item-2, item-3, item-4, item-5, item-6, item-7 |
| diag-2 | matrix | PR 分类矩阵：repo × 分类 × PR 数量/代表 PR × 状态 × 技术目标 × 叙事含义 × Mantle 影响 | markdown table | item-1, item-2, item-3, item-10 |
| diag-3 | architecture | Arbitrum Nitro + Stylus + Orbit + BoLD + Timeboost 关系图：sequencer、Nitro node、Stylus WASM execution、validator/dispute、Orbit chain、auction path、L1 settlement | mermaid | item-2, item-3, item-4, item-5, item-6 |
| diag-4 | flow | Timeboost 排序权拍卖流程图：bidder/searcher/app -> auction -> express lane / ordering rights -> sequencer inclusion -> revenue / fallback / user impact | mermaid | item-5 |
| diag-5 | comparison | Arbitrum vs Optimism Superchain vs Base vs Mantle 定位对比：governance、interop/appchain、VM/client stack、MEV/latency、proof/security、DA/economics、developer distribution | markdown table or mermaid | item-8, item-9, item-10 |
| diag-6 | flow | Mantle 响应决策流：跟踪 BoLD、研究 Timeboost、评估 Stylus-like alt-VM、推进 L3/appchain、强化 OP/ZK/EigenDA 路线的触发条件和风险 | mermaid | item-10 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | github_pr_data | `OffchainLabs/nitro` 近 3 个月 PR 原始数据：PR 号、标题、状态、时间、作者、改动目录、标签/里程碑、关联 commit；需保存查询语句和抓取日期 | 30 |
| src-2 | github_pr_data | `OffchainLabs/stylus-sdk-rs` 近 3 个月 PR 原始数据和 release tag；需独立统计并与 Nitro 交叉引用 | 15 |
| src-3 | github_code_analysis | 关键 merged PR 的代码/diff/file-level 验证，覆盖 BoLD、Timeboost、Stylus、Orbit/AnyTrust、sequencer/batcher/node、contracts/governance | 12 |
| src-4 | official_arbitrum_docs | Arbitrum / Offchain Labs 官方 docs、Nitro docs、Stylus docs、Orbit docs、Timeboost docs、BoLD docs、release notes；时间敏感页面标注访问日期 | 10 |
| src-5 | governance_and_dao | Arbitrum DAO forum / Snapshot / Tally / proposal / vote / Security Council materials，用于验证 BoLD、Timeboost、Orbit funding、upgrade/governance 状态 | 5 |
| src-6 | audits_security_reviews | BoLD、Nitro、Stylus、Timeboost 或相关合约/协议审计、安全公告、bug disclosure；必须区分 pre-mainnet、resolved、active risk | 4 |
| src-7 | onchain_or_ecosystem_data | Arbitrum One/Nova/Orbit chain data、L2Beat、Arbiscan、chain registry、TVL/usage dashboard、Orbit ecosystem listing，用于验证生产状态和采用信号 | 5 |
| src-8 | internal_research | 仓库内既有 Optimism、Base、Stage 1、Mantle codebase / Azul / performance 研究，用于横向对比和 Mantle 影响交叉引用 | 6 |
| src-9 | competitor_primary_sources | Optimism/Base 官方文档、GitHub、release/governance，用于对比 Superchain / Base Stack；优先引用仓库内对应 final section，关键事实需重新核验 | 4 |
| src-10 | industry_commentary | 高可信行业文章、研究报告、工程博客或公开访谈，用于叙事变化和市场定位；必须用 primary source 交叉验证关键事实 | 3 |

## Quality Checklist for Deep Draft

- [ ] PR 数据集包含明确日期窗口、查询语句、抓取时间、去重规则、分页完整性和统计口径。
- [ ] `nitro` 与 `stylus-sdk-rs` 分别统计，不能把 SDK/DX 活动和核心协议活动混为一谈。
- [ ] 每个高层叙事判断至少有一个工程/代码证据和一个官方/治理/生态证据；若只有其一，必须降级为推断。
- [ ] Timeboost 必须拆分机制设计、代码状态、部署状态、经济模型和 fairness/MEV caveat，不得只写"缓解 MEV"。
- [ ] BoLD 必须区分 permissionless validation、challenge period、Stage 1、Stage 2、Security Council / DAO upgrade path 和 exit window。
- [ ] Orbit 生态扩展必须区分 announced/listed、testnet、mainnet-active、真实链上采用和商业合作。
- [ ] Stylus 成熟度必须覆盖 SDK release、工具链、合约安全、EVM 互操作、主网采用信号和 developer adoption caveat。
- [ ] 与 Optimism Superchain / Base / Mantle 的对比必须使用相同维度，避免按 Arbitrum 强项单方面设题。
- [ ] Mantle 建议必须分为 borrow/prototype/monitor/avoid，并标注工程成本、组织依赖和证据置信度。
- [ ] 所有时间敏感事实标注 2026-05-23 之后的验证日期或说明未能验证。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create_outline | all | 初版研究大纲，覆盖 Arbitrum 近 3 个月 PR 活动、Stylus/Orbit/Timeboost/BoLD 叙事与 Mantle 竞争启示 | Orchestrator Dispatch: outline round 1 |
