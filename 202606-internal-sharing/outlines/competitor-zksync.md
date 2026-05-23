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
  分析 zkSync / ZKsync 最近 3 个月的 GitHub PR 活动与叙事变化。时间窗口默认固定为
  2026-02-23 至 2026-05-23，重点仓库为 `matter-labs/zksync-era`，但必须把
  `matter-labs/zksync-os`、`matter-labs/zksync-airbender`、`matter-labs/era-contracts`、
  `matter-labs/zksync-docs`、`matter-labs/era-consensus`、`matter-labs/zksync-sso`、
  `matter-labs/local-prividium` 等相关仓库纳入旁证，因为近期战略性工作可能已经从
  Era 单仓迁移到 ZKsync OS / Airbender / Prividium / interop 等周边仓库。研究需覆盖
  GitHub PR 活动概况、主要开发方向与 PR 分类、重大功能变更与架构调整、ZK Stack 模块化框架、
  Elastic Chain / Gateway 互操作叙事、原生账户抽象演进、Validium / Volition / Prividium
  混合数据可用性路线，以及与 OP Rollup / OP Stack / Base / Optimism 阵营的技术路线竞争。
  最终必须落到对 Mantle 的竞争启示和可执行建议。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、协议和客户端工程师、DA / proof
  / AA / 企业链方向负责人、生态与战略研究同事，以及 Research Review Agent 和后续写作者。
  读者熟悉 L2、ZK Rollup、OP Stack、账户抽象、Validium 和模块化链基本概念，但不一定持续跟踪
  ZKsync 最近 3 个月的 PR、ZKsync OS / Airbender 迁移、Elastic Chain / Gateway 或 Prividium
  叙事。

expected_output: |
  一份中文结构化 research section，能够直接支持 Mantle 内部分享，至少包含：
  - `matter-labs/zksync-era` 近 3 个月 PR 活动概况、活跃度趋势、状态分布、代表 PR 和分类统计
  - ZKsync 近期开发重点变化：Era core / protocol upgrades / bootloader / prover / verifier / API /
    release infra，以及 ZKsync OS、Airbender、Gateway、Prividium 等跨仓库迁移信号
  - 叙事方向演变：从 zkEVM / ZK Rollup 到 ZK Stack、Elastic Chain、native AA、Prividium / bank stack、
    Validium / Volition、proving network / Airbender 的组合叙事
  - 与 OP Rollup 阵营竞争分析：ZK validity proof vs fault proof、Elastic Chain vs Superchain interop、
    ZK Stack hyperchains vs OP Stack / Base Stack、native AA vs EIP-4337 / EIP-7702 / paymaster 路线
  - 对 Mantle 的竞争启示：必须防守的叙事、可借鉴架构、不可直接照搬约束、短中长期行动建议
  - 至少 5 张图/表：PR 活动趋势、PR 分类矩阵、ZKsync 组件/仓库关系图、Elastic Chain / Gateway 架构图、
    Mantle vs ZKsync vs OP/Base 竞争响应矩阵

source_requirements_summary: |
  深度研究必须以 primary source 为主。GitHub 活动需直接查询 `matter-labs/zksync-era` PR / release /
  tag / label / diff，并记录查询时间、时间窗口、过滤条件和去重规则；不能只依赖标题关键词。叙事分析需优先使用
  ZKsync 官方 docs、Matter Labs 官方 blog、ZKsync protocol / Gateway / Elastic Chain / ZK Stack /
  Prividium 文档、GitHub release notes 和官方公告。初步仓库快照显示 Matter Labs 在 2026-05 仍活跃维护
  `zksync-era`，同时 `zksync-os`、`zksync-airbender`、`zksync-os-server`、`eravm-airbender-verifier`、
  `local-prividium` 等仓库更新频繁；这只用于 outline 分类校准，draft 必须重新生成可复现查询、精确计数、
  representative PR 清单和证据等级。仓库内既有 Prividium / enterprise privacy / Base / Optimism 研究可作为
  前置材料，但所有时间敏感事实必须以 2026-05-23 时点公开来源重新验证。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-23T11:56:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-23T11:56:00+08:00"

multica_issue_id: "6c75749c-a82f-4264-aa07-3aeb6a758bbd"
branch_name: "research/202606-internal-sharing/competitor-zksync"
base_commit: "4d52e841496cccc7a4c2640ef0f96cbd6e55a637"
language: "中文"
research_depth: "standard"

prerequisite_sections:
  - slug: competitor-optimism
    path: 202606-internal-sharing/research-sections/competitor-optimism/final.md
    status: existing-research
  - slug: competitor-base
    path: 202606-internal-sharing/research-sections/competitor-base/final.md
    status: existing-research
  - slug: enterprise-privacy
    path: 202606-internal-sharing/research-sections/enterprise-privacy/final.md
    status: existing-research
  - slug: prividium-official-docs-research
    path: mantle-enterprise-blockchain/research-sections/m1-independent-research/WHI-337-prividium-official-docs-research.md
    status: existing-research
  - slug: prividium-architecture-deep-analysis
    path: mantle-enterprise-blockchain/research-sections/m1-independent-research/WHI-338-prividium-architecture-deep-analysis.md
    status: existing-research
  - slug: l3-enterprise-appchain-analysis
    path: mantle-enterprise-blockchain/research-sections/m5-solution-analysis/WHI-389-l3-enterprise-appchain-analysis.md
    status: existing-research
  - slug: mantle-impact-assessment
    path: base-azul-upgrade/research-sections/mantle-impact-assessment/final.md
    status: existing-research
---

# Research Outline: zkSync 近期开发与叙事分析

## Research Questions

1. 2026-02-23 至 2026-05-23 期间，`matter-labs/zksync-era` 的 PR 活动总量、合并节奏、活跃模块、作者分布和 release / protocol upgrade 节奏是什么？
2. 近 3 个月的 PR 是否显示 ZKsync 的研发重心从 Era 单体仓维护转向 ZKsync OS、Airbender、proving network、Gateway / Elastic Chain 和 Prividium 等跨仓库模块化工作？
3. ZK Stack 的模块化框架在代码和文档中推进到哪一层：链模板、shared bridge、Gateway、chainhub / interop、prover、DA 模式、operator tooling，还是仍主要停留在产品叙事？
4. Elastic Chain / Gateway 叙事是否有可验证的工程进展？它与 OP Superchain interop、Base Stack 和 Mantle 潜在 L2/L3 互操作路线相比，核心差异是什么？
5. zkSync 原生账户抽象最近是否有实质演进：account model、paymaster、bootloader、EIP-4337 / 7702 兼容、SSO/passkey、ZKsync SSO、developer SDK 和钱包体验分别发生了什么？
6. Validium / Volition / Prividium / mixed DA 在 ZKsync 技术路线中的角色是什么？它是企业隐私方案、成本优化方案、Elastic Chain 扩展路径，还是三者兼具？
7. 与 OP Rollup 阵营相比，ZKsync 的竞争叙事从"ZK Rollup 技术领先"是否转向"modular ZK chain network + native AA + enterprise validium + high-performance proving"？
8. 对 Mantle 而言，ZKsync 的近期变化构成哪些竞争压力、哪些可借鉴设计、哪些路线存在不可迁移约束，Mantle 应如何回应？

## Items

### item-1: GitHub 数据基线、仓库边界与统计方法

建立近 3 个月 ZKsync 开发活动的事实底座。核心仓库必须是 `matter-labs/zksync-era`，但研究不能把全部战略变化限制在该仓：`zksync-os`、`zksync-airbender`、`era-contracts`、`zksync-docs`、`era-consensus`、`zksync-sso`、`local-prividium`、`zksync-os-server` 等仓库需要作为 cross-repo signal 处理。输出应明确 primary repo 统计和 supporting repo 统计的边界，避免把跨仓库 PR 数混为一个口径。

必须覆盖：

- 时间窗口固定为 2026-02-23 至 2026-05-23；若实际抓取日不同，需要同时记录抓取时间和窗口定义；
- `zksync-era` PR created / merged / closed / open / draft 状态分布，周粒度趋势，bot / human 贡献者区分；
- PR 查询方式：GitHub Search / GraphQL / gh CLI / REST API 的具体 query、分页、rate limit、失败重试和导出字段；
- 清洗规则：release-please / autorelease、dependabot、CI、docs-only、external-contribution、revert、protocol-upgrade bot、backport / cherry-pick 如何处理；
- representative PR 选择规则：每类至少 5 个高信号 PR，必须读 PR body、labels、files changed 和合并状态；
- supporting repos 的纳入规则：只纳入能解释 ZKsync Era / ZK Stack / Elastic Chain / Airbender / Prividium 方向的 PR，不把无关前端或模板仓活动算作核心协议活跃度；
- 证据等级：`merged-code`、`open-pr`、`release-note`、`official-doc`、`official-claim`、`internal-research`、`inferred`、`unverified`。

- **Priority**: high
- **Dependencies**: none

### item-2: `zksync-era` PR 活动总览与开发方向分类

基于 item-1 的数据集，给出 `zksync-era` 近 3 个月研发活动的宏观画像。该项重点不是罗列所有 PR，而是判断 Era 主仓当前是以 release / protocol upgrade / verifier / API / testing 维护为主，还是仍承载核心新功能开发。

建议分类：

1. **Protocol upgrade / release infra**：protocol-upgrade labels、autorelease、upgrade scripts、circuit divergence、server / node compatibility；
2. **Prover / verifier / Airbender bridge**：proof manager、SNARK proofs、Airbender commitment、verifier logging、contract verifier、proof artifacts；
3. **Bootloader / VM / circuits**：bootloader flows、circuit versioning、medium interop bootloader、EraVM / MultiVM compatibility；
4. **API / RPC / traces / explorer support**：debug_trace、eth_fillTransaction、contract verification、indexer / API correctness；
5. **DA / pubdata / commitment handling**：DA commitment decode、pubdata encoding / compression、validium or custom DA hooks；
6. **Interop / Elastic Chain preparation**：shared bridge, Gateway, chain IDs, cross-chain messaging, interop bootloader, settlement / proof aggregation hooks；
7. **Account abstraction / paymaster / SSO compatibility**：AA transaction flow, account validation, paymaster changes, SSO / passkey adjacent integrations；
8. **Testing / reliability / ops**：flaky tests, CI, observability, cargo deny, database errors, external node reliability.

每个类别需要输出：

- PR 数量、merged/open/closed 状态、代表 PR、关键目录和主要作者；
- 技术目标、用户/开发者可见影响、叙事含义；
- 当前成熟度：已合并、release pending、testnet、mainnet active、experimental、docs-only；
- 对 Mantle 的竞争意义：性能 / proof / DA / AA / interop / enterprise 哪个维度受影响。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Era core、protocol upgrade、bootloader、prover / verifier 的近期重点

深入分析 `zksync-era` 主仓内真正影响协议行为或生产系统的 PR。该项需要把 release / protocol upgrade PR 与具体代码变更对应起来，避免只按 PR 标题推断功能完成度。

必须覆盖：

- protocol upgrade pipeline：upgrade labels、版本号、v31 或其他近期 protocol version、circuit divergence、deployment / migration scripts；
- bootloader / VM：transaction validation、AA flow、interop bootloader、EraVM / MultiVM、system contracts 和 compatibility gates；
- prover / verifier：Airbender 相关提交、SNARK proof support、proof manager contracts、contract verifier / bytecode hash logging、verifier error handling；
- API / tracing：debug_trace、eth_fillTransaction、contract verification output、developer / explorer 兼容；
- DA / pubdata：DA commitment decoding、pubdata body / storage diff handling、blob / calldata / custom DA 的可见变更；
- 生产影响：哪些 PR 只是测试或 release plumbing，哪些改变主网协议或即将进入主网；
- 风险：protocol upgrade 自动化、prover migration、DA commitment parsing、debug / tracing correctness 可能对生态工具造成的兼容性问题。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: ZKsync OS、Airbender、Atlas 与 proving stack 的战略迁移信号

分析 ZKsync 是否正在把下一代技术路线从 Era 主仓迁移到 `zksync-os`、`zksync-airbender`、`zksync-os-server`、`eravm-airbender-verifier`、`zksync-airbender-prover` 等仓库。该项需要把这些仓库的 PR 活动与 Era 主仓中的 Airbender / proof manager / verifier PR 连接起来，判断它们是独立研发、测试工具，还是 ZK Stack 下一阶段主路径。

必须覆盖：

- `zksync-os` PR：RISC-V STF、bootloader zk tx flow、pubdata compression、storage write path、bytes32 / history map / oracle IO 性能优化；
- `zksync-airbender` PR：GKR / unified circuit、V2 circuit tests、riscv32 verifier、field arithmetic perf、audit report、non-determinism source；
- `eravm-airbender-verifier` / `zksync-airbender-prover`：是否形成可部署 verifier / prover 服务链路；
- Boojum -> Airbender / Atlas 叙事的实际证据：官方 blog / docs、PR、benchmarks、audit reports、release notes；
- 性能声明：TPS、proving latency、GPU cost、open-source prover 的口径和独立验证情况；
- 与 Mantle SP1 / OP Succinct / Base multiproof 的竞争关系：proof system modularity、prover cost、finality latency、可信假设和 reproducibility。

- **Priority**: high
- **Dependencies**: item-1, item-3

### item-5: ZK Stack、Hyperchains、Elastic Chain / Gateway 与互操作进展

把 ZK Stack 模块化框架和 Elastic Chain 叙事拆成可验证的工程组件。研究需要回答：ZKsync 的多链网络是由 shared bridge / Gateway / proof aggregation / interop messages / chain registry / operator tooling 共同支撑，还是当前仍主要是文档和路线图。

必须覆盖：

- ZK Stack 组件：chain template、L1/L2 contracts、shared bridge、state transition manager、chain admin、prover / DA / sequencer / operator configuration；
- Elastic Chain / Gateway：settlement topology、proof aggregation、shared liquidity / messaging、chain onboarding、Gateway governance / operator model、failure modes；
- 近期 PR 证据：`zksync-era` interop bootloader、`interop-examples`、`cast-interop`、`era-consensus`、`zksync-protocol`、`zksync-docs` 和 Gateway 相关 docs / code；
- 与 OP Superchain interop 对比：dependency set / supervisor / shared bridge / governance / shared security / settlement 的技术差异；
- 与 Base Stack 对比：Base 更偏产品/性能驱动的独立 stack，ZKsync 更偏证明聚合和 ZK hyperchain network，二者对 Mantle 的启示不同；
- 状态标注：mainnet, testnet, devnet, alpha, docs-only, roadmap, deprecated。

- **Priority**: high
- **Dependencies**: item-1, item-4

### item-6: 原生账户抽象、Paymaster、SSO / Passkey 与开发者 UX 演进

分析 zkSync 原生账户抽象是否仍是差异化优势，以及最近 3 个月是否出现新的工程或叙事推进。需要把协议层 AA、bootloader 交易流、paymaster、EIP-4337 / EIP-7702 兼容、ZKsync SSO、passkey / WebAuthn、wallet / SDK / RPC 支持分层处理。

必须覆盖：

- zkSync native AA 基线：account validation / execution、paymaster flow、bootloader role、system contracts、fee abstraction；
- 近期 `zksync-era` PR 是否触及 AA transaction flow、validation、tracing、debugging、eth_send / fillTransaction、paymaster 兼容；
- `zksync-sso`、`zksync-sso-contracts`、`zksync-sso-clave-contracts`、ZKsync SSO docs / SDK 的状态和与 native AA 的关系；
- EIP-4337 / EIP-7702 / passkey / P256 / smart account 叙事对 zkSync 原生 AA 差异化的影响；
- 开发者和用户体验：钱包接入、gas sponsorship、session keys、recoverability、合约账户安全、SDK maturity；
- 与 Mantle / OP Stack 的对比：Mantle 可通过 ERC-4337/paymaster/app-layer AA 实现哪些能力，哪些需要协议/bootloader 层改造。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-7: Validium、Volition、Prividium 与混合数据可用性路线

分析 ZKsync 的 DA 叙事如何从公共 ZK Rollup 扩展到 Validium、Volition、Prividium 和企业私有链。该项应复用既有 Prividium 研究，但必须重新验证 2026-05-23 时点的 ZKsync docs、Matter Labs blog、`local-prividium`、`era-contracts` 和相关 GitHub PR。

必须覆盖：

- DA 模型分层：Rollup、Validium、Volition、custom DA、DAC、private operator DA、pubdata compression / commitment；
- Prividium：Proxy RPC、permissioning、TransactionFilterer、private explorer、enterprise modules、ZK proof + off-chain DA 的实际边界；
- ZK Stack / Elastic Chain 中 DA 可配置性的证据：operator config、chain template、contracts、docs、examples；
- 近期 PR 证据：DA commitment decode、pubdata compression、local-prividium、era-contracts / PrividiumTransactionFilterer、docs updates；
- 安全和产品 tradeoff：状态转换正确性 vs 数据可用性、强制退出、数据扣留、企业合规、审计/选择性披露、GDPR / 数据主权；
- 对 Mantle 的启示：EigenDA / private DA / L3 Validium / enterprise zones 的可借鉴性，以及哪些 ZK Stack 特性不能直接迁移到 OP Stack。

- **Priority**: high
- **Dependencies**: item-3, item-5

### item-8: 叙事演变与 OP Rollup 阵营技术路线竞争

把工程活动映射到 ZKsync 对外叙事变化，并与 Optimism / Base / OP Stack 阵营对照。该项需要区分官方叙事、代码证据、生态数据和战略推断，避免把 marketing phrase 当作已落地功能。

必须覆盖：

- ZKsync 叙事演变：zkEVM / Era -> ZK Stack -> Elastic Chain -> Gateway -> Prividium / bank stack -> Airbender / ZKsync OS；
- OP 阵营叙事：Optimism Superchain interop / standardization / fault proof / op-reth，Base Stack / Azul / Flashblocks / Multiproof / Coinbase distribution；
- 核心竞争维度：proof system、finality、interop、DA 模型、native AA、developer compatibility、governance、operator tooling、enterprise adoption、distribution；
- 生态指标：TVL、transaction count、active addresses、developer activity、app ecosystem、enterprise partnerships、chain count；
- 叙事强弱：哪些能力有 merged code 和 production evidence，哪些只是 open PR / docs / roadmap；
- 对 Mantle 的定位压力：Mantle 如何在 OP Stack fork + EigenDA / MNT / potential ZK validity / enterprise L3 之间形成清晰反差。

- **Priority**: high
- **Dependencies**: item-4, item-5, item-6, item-7

### item-9: 对 Mantle 的竞争启示与行动建议

把前述发现转化为 Mantle 可以行动的竞争判断。输出需要按工程、产品、生态和叙事分层，并明确短期必须验证的问题、中期可做 POC、长期路线选择。

必须覆盖：

- **必须防守的叙事**：ZK proof 正确性、Elastic Chain 互操作、native AA、enterprise Validium、proving performance；
- **可借鉴设计**：cross-chain settlement / Gateway 组件化、operator tooling、AA UX、private DA / L3 Validium、proof aggregation observability、Prividium 的企业入口控制模式；
- **不可直接照搬**：ZK Stack bootloader / proof system / native AA / Gateway 合约假设、EraVM / ZKsync OS 兼容边界、Matter Labs 企业模块许可；
- **Mantle 差异化机会**：EigenDA、MNT gas / economics、EVM/OP compatibility、Base / Optimism 上游可借力、SP1 / OP Succinct validity path、enterprise L3 zones；
- **工程 watchlist**：ZKsync OS / Airbender releases、Gateway production status、Prividium public code/docs、native AA compatibility changes、DA commitment / pubdata changes；
- **行动建议**：30 天证据收集、60-90 天 AA / private DA / L3 prototype、6 个月 proof / interop / enterprise roadmap decision points；
- **风险表达**：避免把 ZKsync 官方性能声明当成独立基准，避免把 Validium 隐私等同于无信任 DA，避免把 Elastic Chain 与 OP Superchain 简单类比。

- **Priority**: high
- **Dependencies**: item-2, item-4, item-5, item-6, item-7, item-8

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| evidence_window | 时间窗口、抓取时间、GitHub query、分页完整性、rate limit、是否重新验证 2026-05-23 时点事实 | all |
| repo_scope | 当前证据来自 `zksync-era` 主仓还是 supporting repo；若跨仓库推断战略迁移，需说明连接逻辑 | all |
| pr_count_and_state | PR 总量、created / merged / closed / open / draft、bot / human、周粒度趋势、代表 PR 列表和去重规则 | item-1, item-2, item-3 |
| category_assignment | 每个代表 PR 被归入 release / prover / bootloader / API / DA / interop / AA / ops 等类别的理由，避免只凭关键词 | item-2, item-3 |
| code_surface | 涉及仓库、目录、包、合约、bootloader、prover、verifier、docs 或 operator tooling 的具体位置 | item-3, item-4, item-5, item-6, item-7 |
| implementation_status | 功能处于 merged、release pending、mainnet active、testnet、devnet、experimental、docs-only、roadmap 或 unknown 哪一阶段 | item-3, item-4, item-5, item-6, item-7 |
| proof_stack | Boojum、Airbender、ZKsync OS、SNARK wrapping、prover network、verifier contracts、audit / benchmark 的证据和可信度 | item-3, item-4 |
| interop_and_gateway_model | Elastic Chain / Gateway / shared bridge / proof aggregation / chain registry / messaging 的架构假设、代码证据和 rollout 状态 | item-5, item-8 |
| account_abstraction_ux | native AA、paymaster、SSO/passkey、EIP-4337 / 7702 兼容、wallet / SDK / RPC 对开发者和用户体验的影响 | item-6 |
| data_availability_model | Rollup / Validium / Volition / custom DA / Prividium / pubdata compression 的安全、成本、隐私和可恢复性权衡 | item-7 |
| narrative_signal | 工程活动如何支撑或削弱官方叙事：ZK Stack、Elastic Chain、native AA、Prividium、bank stack、Airbender | item-5, item-6, item-7, item-8 |
| op_competition | 与 Optimism / Base / OP Stack 的路线对比：proof、interop、DA、AA、developer tooling、governance、enterprise | item-8, item-9 |
| mantle_impact | 对 Mantle 的直接影响：兼容性风险、可借鉴设计、上游/竞品压力、叙事回应和行动建议 | item-7, item-8, item-9 |
| confidence_and_gaps | 对关键结论标注证据等级、冲突来源、缺失数据、需工程团队复核的问题和不可外推限制 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | timeline | 2026-02-23 至 2026-05-23 ZKsync 关键 PR、release、protocol upgrade、ZKsync OS / Airbender、Gateway / Elastic Chain、Prividium / docs / blog 事件时间线 | mermaid | item-1, item-2, item-3, item-4, item-5, item-7, item-8 |
| diag-2 | comparison | `zksync-era` PR 分类矩阵：类别 × PR 数量 × 代表 PR × 成熟度 × 叙事含义 × Mantle 影响 | mermaid | item-2, item-9 |
| diag-3 | architecture | ZKsync 仓库与组件关系图：zksync-era、zksync-os、Airbender、era-contracts、Gateway、Prividium、SSO、docs / SDK 的依赖和职责 | mermaid | item-3, item-4, item-5, item-6, item-7 |
| diag-4 | architecture | Elastic Chain / Gateway 架构图：Hyperchain、shared bridge、proof aggregation、Gateway settlement、interop messages、DA / prover / sequencer 的数据流和信任边界 | mermaid | item-5, item-8 |
| diag-5 | flow | Native AA / paymaster / SSO transaction flow：用户签名、account validation、bootloader、paymaster、L2 execution、proof / settlement 的顺序和失败点 | mermaid | item-6 |
| diag-6 | comparison | DA 模式对比图：Rollup vs Validium vs Volition vs Prividium private DA vs Mantle EigenDA / L3 private DA，覆盖成本、隐私、可恢复性、信任假设 | mermaid | item-7, item-9 |
| diag-7 | comparison | ZKsync vs Optimism vs Base vs Mantle 竞争定位矩阵：proof / finality / interop / AA / DA / enterprise / distribution / developer compatibility | mermaid | item-8, item-9 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | github_pr_api | `matter-labs/zksync-era` 近 3 个月 PR 的可复现 GitHub 查询、状态分布、分页导出、代表 PR URL；必须记录 query 和抓取时间 | 20 |
| src-2 | cross_repo_github | `zksync-os`、`zksync-airbender`、`era-contracts`、`zksync-docs`、`era-consensus`、`zksync-sso`、`local-prividium` 等 supporting repo 的代表 PR / commits / releases | 12 |
| src-3 | code_analysis | 对高信号 PR 的 diff 或合并后源码进行文件级验证，重点 bootloader、protocol upgrade、prover、verifier、DA / pubdata、AA、Gateway / interop、Prividium contracts | 15 |
| src-4 | official_docs | ZKsync 官方 docs / protocol docs / ZK Stack / Elastic Chain / Gateway / Account Abstraction / Prividium / DA / prover 文档 | 10 |
| src-5 | official_blog_or_announcements | Matter Labs / ZKsync 官方 blog、release announcement、roadmap、developer update、enterprise / bank stack / Prividium 公告 | 6 |
| src-6 | release_notes_and_protocol_upgrades | `zksync-era` releases、protocol upgrade notes、versioned docs、upgrade scripts、security notices，用于校验 PR 是否进入生产路径 | 5 |
| src-7 | on_chain_or_ecosystem_data | L2Beat、DeFiLlama、GrowThePie、Dune、官方 explorer / chain stats、Gateway / chain registry / bridge data，用于验证 TVL、交易、链数量、DA / proof 状态 | 4 |
| src-8 | internal_research | 仓库内既有 Prividium、enterprise privacy、Optimism、Base、Mantle L3 / private DA、Base multiproof / Mantle impact 研究，用于竞争对比和 Mantle 映射 | 6 |
| src-9 | competitor_primary_sources | Optimism / Base / OP Stack 官方 docs、PR、release、Superchain interop、Base Stack / Azul / Flashblocks / Multiproof 资料，用于路线对比 | 4 |
| src-10 | audit_security_or_governance | Audit reports、security reviews、governance / upgrade documents、admin key / council / verifier / prover reproducibility 资料，用于验证 proof / upgrade / DA 信任假设 | 3 |
| src-11 | industry_commentary | 高可信行业研究、工程博客或专家评论，用于叙事和市场定位；关键事实必须由 primary source 交叉验证 | 3 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
