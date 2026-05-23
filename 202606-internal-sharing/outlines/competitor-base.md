---
topic: "Base 近期开发与叙事分析"
project_slug: 202606-internal-sharing
topic_slug: competitor-base
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: 202606-internal-sharing/outlines/competitor-base.md
  draft: 202606-internal-sharing/research-sections/competitor-base/drafts/round-{n}.md
  final: 202606-internal-sharing/research-sections/competitor-base/final.md
  index: 202606-internal-sharing/research-sections/_index.md

scope: |
  分析 Base 近 3 个月 GitHub PR 活动与对外叙事变化，重点 repo 为 `base/base`。研究需覆盖主要开发方向与 PR
  分类（Azul 升级、预编译合约、性能优化、Flashblocks、Multiproof、客户端/共识层、开发者体验等）、重大功能变更
  与架构调整、开发活跃度趋势；同时分析 Base 脱离 OP Stack 后的独立路线、Azul 升级核心变化、5K Peak TPS
  性能叙事、Beryl 预编译合约系统（Token Factory、Policy Registry 等）、与 Coinbase 生态深度绑定，并提炼
  对 Mantle 的竞争启示。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、协议工程师、生态/BD 团队、战略研究同事，
  以及 Multica Research Squad 的 Review Agent 和后续 Technical Writer。读者熟悉 L2/OP Stack/Rollup
  基本概念，但不一定跟踪 Base 近 3 个月 PR、Azul/Beryl 细节或 Coinbase 产品叙事。

expected_output: |
  一份中文结构化 research section，包含：
  - Base 近 3 个月 `base/base` GitHub PR 活动概况、活跃度趋势和 PR 分类统计
  - 关键开发方向：Azul、Beryl 预编译合约、5K Peak TPS/性能优化、Flashblocks、Multiproof、客户端与共识层演进
  - 重大功能变更与架构调整：Base Stack 独立化、base-reth-node + base-consensus、Engine API/网络协议、合约/预编译系统
  - 叙事方向演变：从 OP Stack/Superchain 成员到 Base Stack 独立性能与 Coinbase 平台化入口
  - 对 Mantle 的竞争启示：必须防守的能力、可借鉴设计、不可照搬约束、短中长期行动建议
  - 至少 4 张图/表：PR 活动趋势、PR 分类矩阵、Base 叙事演变时间线、Mantle 竞争响应矩阵

source_requirements_summary: |
  必须优先使用 primary source：`base/base` GitHub PR/commit/release/spec、Base 官方博客/文档、Coinbase 官方公告或开发者文档。
  必须复用并校验仓库内已有 Base Azul、Base 性能、Mantle 切换 Base codebase 研究产出；旧研究中的时间敏感事实
  不能直接照搬，须以 2026-05-23 之后的最新公开来源重新验证。PR 活动统计应给出查询时间、窗口定义、筛选条件和
  去重规则；若 PR Tracker 每日报告可访问，应作为辅助输入而不是替代 GitHub 原始 PR 证据。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-23T10:55:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-23T10:55:00+08:00"

multica_issue_id: 30956d61-edce-4606-bf76-169d60c817ca
branch_name: research/202606-internal-sharing/competitor-base
base_commit: 7b5b8c35dfe456e21159f7285d3ea38c463d2d91
language: 中文
research_depth: standard

prerequisite_sections:
  - slug: base-strategy-azul-overview
    path: base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md
    status: existing-research
  - slug: flashblocks-network-changes
    path: base-azul-upgrade/research-sections/flashblocks-network-changes/final.md
    status: existing-research
  - slug: multiproof-architecture
    path: base-azul-upgrade/research-sections/multiproof-architecture/final.md
    status: existing-research
  - slug: multiproof-provers-challengers
    path: base-azul-upgrade/research-sections/multiproof-provers-challengers/final.md
    status: existing-research
  - slug: osaka-evm-changes
    path: base-azul-upgrade/research-sections/osaka-evm-changes/final.md
    status: existing-research
  - slug: mantle-impact-assessment
    path: base-azul-upgrade/research-sections/mantle-impact-assessment/final.md
    status: existing-research
  - slug: block-builder-flashblocks-throughput
    path: base-perf-analysis/research-sections/block-builder-flashblocks-throughput/final.md
    status: existing-research
  - slug: perf-gap-analysis-recommendations
    path: base-perf-analysis/research-sections/perf-gap-analysis-recommendations/final.md
    status: existing-research
  - slug: architecture-advantage-summary
    path: mantle-base-codebase-evaluation/research-sections/architecture-advantage-summary/final.md
    status: existing-research
  - slug: comprehensive-evaluation-recommendation
    path: mantle-base-codebase-evaluation/research-sections/comprehensive-evaluation-recommendation/final.md
    status: existing-research
---

# Research Outline: Base 近期开发与叙事分析

## Research Questions

1. Base 近 3 个月 `base/base` 的 PR 活动是否显示其研发重心已经从 OP Stack 跟随者转向独立 Base Stack 建设者？
2. 这些 PR 可以如何分类：Azul hardfork、Beryl 预编译合约、性能/5K TPS、Flashblocks、Multiproof、客户端/共识层、Coinbase 集成、测试/运维/文档？
3. Azul 与 Beryl 在技术上分别改变什么，二者共同支撑的 Base 叙事是否从"低成本 L2"升级为"Coinbase 驱动的高性能链上金融平台"？
4. 5K Peak TPS 叙事背后的工程支撑是什么：真实吞吐、峰值口径、DA/执行/Flashblocks/客户端优化分别贡献多少？哪些仍是 roadmap 或实验口径？
5. Beryl 预编译合约系统中的 Token Factory、Policy Registry 等能力如何改变资产发行、合规策略、钱包/商户集成和 Coinbase 生态入口？
6. Base 与 Coinbase 产品、钱包、稳定币、onchain commerce、developer platform 的绑定是技术集成、分发渠道、合规入口，还是全部兼具？
7. 对 Mantle 而言，Base 的近期变化构成哪些竞争压力：性能口径、开发者心智、资产发行/合规原语、支付/商户生态、RWA/机构场景、上游维护路线？
8. Mantle 应该立即借鉴什么、持续观察什么、避免直接照搬什么，并如何把这些判断转化为工程/产品/叙事行动？

## Items

### item-1: 研究窗口、数据集与统计方法

建立本研究的数据边界，避免把零散 PR 或外部叙事误读为完整趋势。研究窗口默认定义为撰写时点向前 3 个月（建议记录为具体日期范围，例如 2026-02-23 至 2026-05-23，最终 draft 以实际抓取日期为准）。核心数据集为 `base/base` GitHub PR，必要时补充 `base/contracts`、Base specs、Base blog、Coinbase developer/product 公告以及仓库内 PR Tracker 每日报告。

必须覆盖：

- PR 抓取方式：GitHub Search / GraphQL / CLI / API 查询语句、抓取时间、分页完整性、open/merged/closed 区分；
- 去重与归因规则：同一功能多 PR、revert/fix follow-up、dependabot/CI/formatting、docs-only、generated code 的处理；
- 统计维度：PR 数量、merged 数量、作者/团队分布、review 周期、代码改动规模、目录/模块热度、标签/标题关键词；
- 证据等级：`merged-code`、`open-pr`、`official-doc`、`reported-claim`、`internal-research`、`inferred`；
- 时间敏感 caveat：Base mainnet 激活日期、Beryl 状态、5K Peak TPS 口径、Coinbase 产品集成必须重新验证，不得只引用旧研究；
- 输出形式：一张 PR 数据集摘要表，附查询语句和不可访问/限流时的替代方案。

- **Priority**: high
- **Dependencies**: none

### item-2: Base 近 3 个月 PR 活动总览与活跃度趋势

基于 item-1 的数据集，给出 Base 研发活动的宏观快照：近 3 个月 PR 量变化、merged/open 比例、峰值周、关键里程碑前后的活动变化、活跃作者与模块集中度。重点不是列出所有 PR，而是判断研发节奏是否围绕 Azul/Beryl/性能目标形成明显阶段。

必须覆盖：

- 周粒度或双周粒度 PR 趋势：创建数、合并数、关闭未合并数；
- 主要贡献者/维护者群体：Base core、Coinbase、外部贡献者或自动化账号的比例；
- 模块热区：`crates/`、`bin/node`、`bin/consensus`、`docs/specs`、`contracts`、`builder`、`flashblocks`、`precompiles`、`tests` 等目录的改动密度；
- 里程碑映射：Azul Sepolia/Mainnet、Beryl spec/PR、性能测试、Flashblocks/rollup-boost、Coinbase 产品公告等是否对应 PR 峰值；
- 代表性 PR 清单：每类至少 3-5 个关键 PR，注明 PR 号、标题、状态、合并时间、主要文件、证据链接；
- 与历史阶段对比：如可行，对比 Azul 前 3 个月或旧 OP Stack 跟随阶段；若不可行，明确标注不做长期趋势外推。

- **Priority**: high
- **Dependencies**: item-1

### item-3: PR 分类框架：从维护性改动到战略性能力建设

建立一套可复核的 PR 分类体系，把近 3 个月 PR 映射到 Base 的开发方向。分类需要既能服务技术分析，也能服务内部分享中的叙事判断。

建议分类：

1. **Azul / Base Stack 独立化**：base-reth-node、base-consensus、Engine API、hardfork config、migration、spec；
2. **Beryl / 预编译合约与资产发行**：Token Factory、Policy Registry、合规/权限/策略、预编译 ABI、合约或系统地址；
3. **性能与 5K Peak TPS**：执行层优化、state root、block builder、DA/压缩、benchmark、load test、gas limit/tx cap；
4. **Flashblocks / 预确认 UX**：producer、consumer、WebSocket/P2P、rollup-boost、builder separation、pending RPC；
5. **Multiproof / 安全与最终性**：TEE、ZK、AggregateVerifier、Proposer、Challenger、Registrar、withdrawal/finality；
6. **开发者体验 / EVM 对齐**：Osaka EIP、P256、eth/69、eth_config、RPC、SDK、docs；
7. **Coinbase 生态绑定**：钱包、onramp/offramp、稳定币、商户/commerce、Smart Wallet、身份/合规、developer platform；
8. **运维/可靠性/测试**：CI、fuzz、integration tests、release infra、observability、incident/fix follow-up。

每个类别需要输出：

- PR 数量、代表性 PR、关键目录；
- 主要技术目标与叙事目标；
- 当前状态：已合并/已激活/测试网/主网待定/实验性/仅文档；
- 对 Mantle 的竞争压力与可借鉴程度。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Azul 升级与 Base Stack 独立路线的最新进展

复用 `base-azul-upgrade` 相关 final sections，重新验证 Azul 后续 PR 和官方状态，输出 Base 独立路线的最新判断。重点是把"脱离 OP Stack"拆成代码、规范、治理、生态四层，不使用过强或未经证实的措辞。

必须覆盖：

- `base-reth-node + base-consensus` 的当前实现边界、二进制/进程关系、与 reth/Kona/OP Stack 的复用关系；
- Azul feature 状态：Osaka EIP、Engine API、Flashblocks payload、Multiproof 合约/服务、hardfork timestamp/activation；
- OP Stack/Superchain 关系：哪些层继续共享（桥、settlement、治理叙事、interop 方向），哪些层已独立（客户端、spec namespace、发版节奏）；
- 近 3 个月新增 PR 是否改变旧研究结论，例如 mainnet activation 从 TBD 到已激活、spec/code drift 是否收敛；
- 对 Mantle 的意义：跟随 OP Stack、借鉴 Base Stack、或选择性移植能力的决策边界；
- 必须显式标注旧研究可复用结论与需要更新的事实。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: Beryl 预编译合约系统：Token Factory、Policy Registry 与链上金融原语

围绕 Beryl 相关 PR 和官方资料，解释 Base 是否正在把资产发行、权限策略和合规控制从应用层合约推进到协议/预编译层。该 item 是本研究区别于旧 Azul 研究的重点之一，必须以最新 `base/base` PR 和 spec 为准。

必须覆盖：

- Beryl 的范围与状态：hardfork/spec 名称、目标网络、激活计划、已合并 PR、open PR、是否已有测试网或主网配置；
- Token Factory：功能边界、token 类型、创建/管理权限、费用/registry、与 ERC-20/ERC-6909/ERC-721 等标准的关系；
- Policy Registry：policy 注册、组合、校验路径、sender/recipient 或 issuer/operator 约束、失败语义和事件；
- 预编译合约设计：系统地址、ABI、gas pricing、状态存储、upgrade/hardfork gating、与普通合约的兼容/索引差异；
- Coinbase 生态意义：让 Coinbase/发行方/商户/钱包更容易创建带策略的链上资产，还是只是底层能力预留；
- 风险与开放问题：中心化策略、合规责任、钱包兼容、索引器支持、开发者采用门槛、与现有 ERC-20 流动性碎片化。

- **Priority**: high
- **Dependencies**: item-1, item-3

### item-6: 性能优化与 5K Peak TPS 叙事的证据拆解

拆解 Base 对 5K Peak TPS 或类似高吞吐口径的叙事，区分"公开性能声明"、"代码层优化"、"benchmark/load test"、"主网真实吞吐"、"用户感知 TPS/延迟"。必须复用 `base-perf-analysis` 和 `mantle-base-codebase-evaluation` 的相关结论，但以最新 Base PR/公告重新校准。

必须覆盖：

- 5K Peak TPS 的来源、日期、测试条件、交易类型、峰值/持续、最终区块 TPS vs Flashblocks 预确认吞吐；
- 性能 PR 分类：builder separation、Flashblocks、state root/cached execution、DA/压缩、gas limit/tx cap、transaction pool、sequencer/consensus；
- 主网指标：近 30 天 TPS、gas/s、empty block、block gas utilization、blob/DA 使用、与历史 Base 性能对比；
- 与旧研究的关系：旧研究中 Base 约 93.7 user-tx/s、DA-bound caveat、Flashblocks 200ms UX 等结论哪些仍成立，哪些需要更新；
- 与 Mantle 对比：Mantle 当前 demand-bound 与 supply-bound 结论如何影响竞争判断，不能把 Base 峰值直接等同于 Mantle 当前必须达到的 sustained TPS；
- 对外表述 guardrail：如果证据不足，使用"reported peak"、"benchmark-only"、"not mainnet sustained"等标签。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-7: Flashblocks、Multiproof 与最终性/预确认叙事的组合

分析 Base 如何把 Flashblocks 的低延迟 UX、Multiproof 的安全/最终性叙事、Azul 的客户端独立路线组合成竞争叙事。该 item 需要避免把预确认、L2 finality、L1 settlement finality、提款 finality 混为一谈。

必须覆盖：

- Flashblocks 当前状态：200ms/250ms 口径、producer/consumer、WebSocket/P2P、pending RPC、rollup-boost；
- Multiproof 当前状态：TEE+ZK dual-proof、AggregateVerifier、Proposer/Challenger/Registrar、withdrawal/finality 窗口；
- 叙事组合：低延迟体验 + 更强安全路径 + 独立客户端迭代速度，如何服务开发者/用户/机构三类受众；
- PR 活动证据：近 3 个月是否仍有 Flashblocks/Multiproof 维护或增强 PR；
- 与 Mantle 的差距：Mantle 已有/缺失的 SP1、Flashblocks POC、op-geth/op-node 路线、最终性叙事；
- caveat：预确认不是最终性，TEE/ZK 双证明不等同于完全去中心化，Path C 加速需要条件满足。

- **Priority**: medium
- **Dependencies**: item-3, item-4, item-6

### item-8: Coinbase 生态深度绑定与 Base 平台化叙事

把代码层变化与 Coinbase 生态叙事连接起来，分析 Base 是否正在从"L2 网络"转向"Coinbase 链上金融/应用平台底座"。该 item 需要分别处理事实集成和战略推断，避免把品牌背书等同于已上线产品深度集成。

必须覆盖：

- Coinbase 生态入口：Coinbase Wallet / Smart Wallet、Developer Platform、onramp/offramp、Commerce、Exchange/Custody、USDC/稳定币、identity/KYC 相关公开资料；
- Base 技术能力与生态入口的连接点：Beryl Token Factory/Policy Registry、paymaster/sponsorship、batching、P256/passkey、Flashblocks UX、低成本/高吞吐；
- 对外叙事变化：官方博客、docs、social/devrel 内容中从 OP Stack/低费 L2 到 onchain economy、global onchain economy、Coinbase distribution 的措辞变化；
- 真实落地证据：产品文档、SDK、API、合作伙伴、主网使用数据、交易/地址/合约增长；
- 对 Mantle 的威胁：分发渠道、合规信任、稳定币入口、商户/消费者品牌认知、开发者增长；
- 不确定性：Coinbase 内部产品路线不可见，公开集成深度可能不足，监管/合规口径不可外推。

- **Priority**: high
- **Dependencies**: item-5, item-6, item-7

### item-9: Base 叙事演变时间线与竞争定位

综合代码 PR、官方公告、性能声明和 Coinbase 生态资料，建立 Base 过去 3 个月的叙事演变时间线，并判断其竞争定位变化。

必须覆盖：

- 时间线节点：Azul announcement/spec、Sepolia/Mainnet、Beryl PR/spec、5K Peak TPS claim、Coinbase 产品/生态公告、重大 PR 合并；
- 叙事阶段：OP Stack 成员/低费 L2 -> 独立 Base Stack -> 高性能/低延迟链 -> Coinbase 链上金融平台；
- 目标受众变化：开发者、用户、机构、商户、资产发行方、钱包/基础设施；
- 与其他 L2 的差异：Base 不只用 TPS 竞争，而是用 Coinbase 分发 + 协议级能力 + 开发者体验组合竞争；
- 与 Mantle 当前叙事对照：高性能 L2、MNT 生态、modular DA、ToB/RWA/支付方向的重合与缺口；
- 图表要求：输出一张时间线图和一张"叙事 -> 技术证据 -> 商业含义"矩阵。

- **Priority**: high
- **Dependencies**: item-4, item-5, item-6, item-8

### item-10: 对 Mantle 的竞争启示与行动建议

将 Base 的近期开发与叙事变化转化为 Mantle 可执行的竞争判断。结论必须区分工程可行性、产品价值、叙事价值和组织成本，避免简单建议"切 Base codebase"或"追 5K TPS"。

必须输出四类建议：

1. **立即防守/补齐**：
   - 明确 Mantle 性能口径：当前 TPS、峰值 TPS、用户感知延迟、DA/执行天花板；
   - 对外叙事避免只谈理论 gas limit，补足真实使用/开发者体验指标；
   - 梳理稳定币支付、资产发行、合规策略、paymaster/赞助交易能力清单。
2. **可借鉴的设计**:
   - Beryl 风格资产发行/Policy Registry 的 Mantle 版本或应用层替代；
   - Flashblocks/预确认 UX 和 builder separation；
   - Base PR 分类/roadmap 透明化方式；
   - Coinbase 式"链 + 钱包 + 开发者平台 + 商户入口"打包叙事。
3. **需要谨慎验证的设计**:
   - 直接迁移 Base Stack / reth/kona 路线；
   - 协议级预编译替代应用层合约；
   - 以 benchmark peak TPS 作为核心竞争口径；
   - 合规策略内置带来的责任边界。
4. **短中长期路线**:
   - 短期：事实核验 dashboard、性能/UX benchmark、支付/资产发行 demo、开发者文档强化；
   - 中期：Flashblocks POC 产品化、稳定币 gas/paymaster 标准化、Policy Registry 原型、merchant/RWA 场景试点；
   - 长期：Reth/op-reth/Base Stack 迁移评估、企业/支付 L3、合规资产发行平台、生态分发合作。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7, item-8, item-9

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| source_anchor | 每个关键论断对应的来源链接、PR 号、commit、文件路径或内部研究路径；所有时间敏感事实标注访问/抓取日期 | all |
| evidence_type | 证据类型：`merged-code` / `open-pr` / `closed-unmerged` / `official-doc` / `official-blog` / `benchmark` / `mainnet-data` / `internal-research` / `inferred` | all |
| evidence_confidence | 证据可信度：high / medium / low，并说明不确定性来源；PR open、reported TPS、叙事推断默认不得标 high | all |
| pr_metadata | PR 号、标题、状态、创建/合并/关闭时间、作者、review 周期、标签、改动行数、主要目录、关联 issue/release | item-1, item-2, item-3 |
| pr_category | PR 分类：Azul / Beryl / performance / Flashblocks / Multiproof / DX-EVM / Coinbase-integration / ops-testing / docs-other | item-2, item-3 |
| activation_status | 功能状态：merged-not-activated / testnet-active / mainnet-active / spec-only / open-pr / reverted / unknown | item-3, item-4, item-5, item-6, item-7 |
| technical_change | 具体技术变化：客户端、共识、预编译、合约、RPC、Engine API、builder、benchmark、配置或文档 | item-3, item-4, item-5, item-6, item-7 |
| narrative_claim | 官方或社区叙事主张，例如 independent Base Stack、5K Peak TPS、onchain economy、Coinbase distribution | item-4, item-6, item-8, item-9 |
| narrative_evidence | 支撑叙事的证据：公告、docs、PR、产品集成、链上数据、合作伙伴；区分事实与推断 | item-8, item-9 |
| performance_metric | TPS、gas/s、block time、preconfirm latency、empty block、DA bytes/UOP、benchmark window、peak vs sustained 口径 | item-6, item-7 |
| coinbase_linkage | 与 Coinbase 钱包、交易所、开发者平台、商户、稳定币、身份/合规或分发渠道的连接方式 | item-5, item-8, item-9 |
| mantle_competitive_impact | 对 Mantle 的竞争影响：developer mindshare、performance narrative、asset issuance、payment/merchant、RWA/institutional、operations | item-6, item-8, item-9, item-10 |
| transferability | 对 Mantle 的可迁移性：borrow_now / prototype / monitor / avoid / not_applicable，并说明工程成本与依赖 | item-5, item-6, item-7, item-10 |
| caveats_open_questions | 需要在 final section 中显式保留的事实缺口、过期风险、口径争议和不能外推的边界 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | timeline | Base 近 3 个月 PR 活动趋势图：按周展示 created/merged/open PR 数，并标注 Azul/Beryl/5K TPS/Coinbase 公告节点 | mermaid or table | item-1, item-2 |
| diag-2 | matrix | PR 分类矩阵：行为分类（Azul、Beryl、性能、Flashblocks、Multiproof、DX、Coinbase、运维），列为 PR 数、代表 PR、状态、技术目标、叙事含义、Mantle 影响 | markdown table | item-3 |
| diag-3 | architecture | Base Stack 近期能力架构图：base-reth-node/base-consensus、Flashblocks/rollup-boost、Multiproof、Beryl precompiles、Coinbase ecosystem entry points 的关系 | mermaid | item-4, item-5, item-7, item-8 |
| diag-4 | flow | Beryl Token Factory + Policy Registry 资产发行/转账策略流程图：issuer -> token factory -> policy registry -> transfer validation -> wallet/indexer/merchant | mermaid | item-5 |
| diag-5 | comparison | 5K Peak TPS 证据拆解图：reported claim、benchmark 条件、代码优化、mainnet sustained metrics、Flashblocks perceived latency 分层 | mermaid | item-6 |
| diag-6 | timeline | Base 叙事演变时间线：OP Stack member -> Base Stack independence -> Azul performance/security -> Beryl asset/compliance primitives -> Coinbase platform | mermaid | item-9 |
| diag-7 | matrix | Mantle 竞争响应矩阵：Base 能力 x 威胁等级 x Mantle 当前状态 x 可借鉴性 x 建议行动 x 时间窗口 | markdown table or mermaid | item-10 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | github_pr_data | `base/base` 近 3 个月 PR 原始数据：PR 号、标题、状态、时间、作者、改动目录、标签/里程碑、关联 commit；需要保存查询语句和抓取日期 | 30 |
| src-2 | github_code_analysis | `base/base` 关键 merged PR 对应源码/commit/spec 文件，至少覆盖 Azul、Beryl、性能、Flashblocks、Multiproof、客户端/共识层 | 10 |
| src-3 | official_base_sources | Base 官方 blog、docs、specs，包括 Azul、Flashblocks、Beryl、性能声明、Base chain/developer docs；时间敏感页面标注访问日期 | 6 |
| src-4 | coinbase_sources | Coinbase 官方公告、developer platform、wallet/smart wallet/onramp/commerce/USDC 或生态相关文档，用于验证 Coinbase 生态绑定 | 5 |
| src-5 | internal_research | 复用仓库内已有研究：`base-azul-upgrade`、`base-perf-analysis`、`mantle-base-codebase-evaluation` 中列为 prerequisite 的 final sections | 6 |
| src-6 | onchain_or_benchmark_data | Base 主网/测试网性能数据、benchmark 或公开 dashboard：TPS、gas/s、empty blocks、block gas utilization、DA/blob 指标、peak vs sustained 口径 | 3 |
| src-7 | comparative_mantle_sources | Mantle 相关内部研究、Mantle docs/code/链上数据，用于竞争启示和可迁移性判断 | 3 |
| src-8 | tracker_or_secondary_sources | PR Tracker 每日跟踪报告、可信第三方分析或社区讨论；只能作为辅助，不得替代 GitHub/官方 primary source | 1 |

## Quality Checklist for Deep Draft

- [ ] PR 数据集包含明确日期窗口、查询语句、抓取时间、去重规则和统计口径。
- [ ] 每个高层叙事判断至少有一个代码/PR 证据和一个官方叙事证据；若只有其一，必须降级为推断。
- [ ] Beryl 相关能力必须以最新 PR/spec 为准，不得只按 issue dispatch 中列名展开。
- [ ] 5K Peak TPS 必须拆分 peak/sustained、benchmark/mainnet、final TPS/perceived latency，不得混用。
- [ ] "脱离 OP Stack"必须拆成代码、规范、治理、生态四层，并保留 Superchain/OP 关系 caveat。
- [ ] Coinbase 生态绑定必须区分已上线产品集成、公开 roadmap、品牌/分发推断。
- [ ] Mantle 建议必须分为 borrow/prototype/monitor/avoid，并标注工程成本与证据置信度。
- [ ] 所有时间敏感事实标注 2026-05-23 之后的验证日期或说明未能验证。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create_outline | all | 初版研究大纲，覆盖 `base/base` 近 3 个月 PR 活动、Azul/Beryl/性能/Coinbase 叙事与 Mantle 竞争启示 | Orchestrator Dispatch: outline round 1 |
