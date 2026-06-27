---
topic: "Mantle AA 现状：ERC-4337 + EIP-7702 支持与采用效果分析"
project_slug: "base-eip8130-native-aa"
topic_slug: "mantle-aa-status"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "base-eip8130-native-aa/outlines/mantle-aa-status.md"
  draft: "base-eip8130-native-aa/research-sections/mantle-aa-status/drafts/round-{n}.md"
  final: "base-eip8130-native-aa/research-sections/mantle-aa-status/final.md"
  index: "base-eip8130-native-aa/research-sections/_index.md"

scope: "取证 Mantle 当前对 ERC-4337 与 EIP-7702 的支持情况与实际采用效果，对照 WHI-275 / native-aa-framework 的四类可观测指标：(a) 链上采用度、(b) 开发者体验/集成成本、(c) 基础设施成本与中心化、(d) 钱包/SDK 生态支持。研究要验证或证伪「Mantle AA 效果不好」这一前提，并定位差距来源：节点能力、合约生态、钱包/SDK 支持、链上采用。数据源受限时，必须按数据受限口径交付：写明不可访问原因、尝试方式、可得的部分定量/定性证据，不能把数据缺失直接当成效果不好。"
audience: "Mantle dev teams、协议工程师、钱包/AA infra 工程师、产品决策者和 Research Review Agent。读者熟悉 EVM、OP Stack、ERC-4337 与 EIP-7702 基础概念，但需要一份能被复核的 Mantle 侧事实基础，用于后续判断是否需要投入 EIP-8130 或类似 native AA 方案。"
expected_output: "Mantle AA 支持矩阵（节点 7702 能力 + 4337 合约生态现状）+ 采用度证据表（附源 + 日期/区块范围）+ 对照 WHI-275 四类指标的「效果好/不好/一般/证据不足」判定 + 差距来源定位（节点/合约/钱包-SDK/采用），后续 draft 保存于 base-eip8130-native-aa/research-sections/mantle-aa-status/drafts/round-1.md，review 接受后 promote 到 base-eip8130-native-aa/research-sections/mantle-aa-status/final.md。"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-27T00:35:07Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-27T00:35:07Z"

multica_issue_id: "456057db-ab81-4dfb-a6ff-a7ed666477c6"
report_issue_id: "fc840c0d-ac87-41c8-b1ae-6d1318b8eaba"
branch_name: "research/base-eip8130-native-aa/mantle-aa-status"
base_commit: "6bf3e8a39d9a6c069ed23746306108c42714cac2"
language: "zh-CN"
research_depth: "standard"
primary_local_dependency: "base-eip8130-native-aa/research-sections/native-aa-framework/final.md"
local_code_seed:
  mantle_op_geth_path: "/Users/whisker/Work/src/networks/mantle/op-geth"
  mantle_op_geth_commit_seen: "3c1c571e57874019991f28fe99c36cddac7b4bef"
  note: "本地 Mantle op-geth 工作树有未跟踪/本地配置文件；deep draft 引用源码时必须用 git-tracked 文件、commit SHA 和行号重新核验。"
status_sensitive_sources_verified_at: "2026-06-27"
---

# Research Outline: Mantle AA 现状：ERC-4337 + EIP-7702 支持与采用效果分析

## Research Questions

1. Mantle op-geth 当前是否在协议/客户端层具备 EIP-7702 所需能力？Prague/Pectra、`SetCodeTxType`、`authorizationList`、授权 gas、txpool/RPC/receipt/simulation 等路径是否可用，是否被 Mantle 特定 hardfork gate 关闭或延后？
2. Mantle 上 ERC-4337 的合约生态是否真实可用？EntryPoint 部署版本、Bundler、Paymaster、AA SDK、官方文档、示例和 RPC 支持是否构成可运行的开发者路径？
3. Mantle 上 ERC-4337 UserOperation 与 EIP-7702 delegation/set-code 交易的实际采用度如何？与 Base、Ethereum、OP Mainnet、Arbitrum、Polygon 等对照链归一化后，能否支撑「效果好/不好/一般/证据不足」判定？
4. 若 Mantle AA 表现不佳，差距来自哪里：节点能力、合约部署与版本、Bundler/Paymaster 基础设施、钱包/SDK 支持、应用集成、链整体活跃度，还是可观测数据源本身不足？
5. 这些 Mantle 侧事实如何反馈到 native AA 决策：继续优化 4337/7702 是否足够，还是存在只有 EIP-8130 或其他 native AA 方案才能解决的结构性缺口？

## Guardrails

> **G1 — 不预设「效果不好」**：
> 「Mantle AA 效果不好」是待验证假设。final section 必须按 `native-aa-framework/final.md` 的四类代理指标独立判断；若只有单一数据点、二手评价、服务商缺席或链上数据不可得，结论应写为「证据不足」或「部分指标偏弱」，不能直接写成效果不好。

> **G2 — 先分清支持类型**：
> EIP-7702 是节点/协议交易类型能力；ERC-4337 是合约 + Bundler/Paymaster + SDK/钱包生态能力。deep draft 必须把「节点支持」「合约已部署」「服务商支持」「钱包/SDK 可用」「链上真实采用」分成不同列，不能把其中一项等同为完整 AA 支持。

> **G3 — 数据受限口径强制执行**：
> 链上采用度数据、Bundler API、Paymaster stats、钱包服务商后台、Dune dashboard 或 explorer API 若不可访问，必须记录：尝试的 URL/API/查询、访问日期、失败类型（权限/限流/无索引/无公开口径/数据缺失）、可替代证据与置信度。不可访问不是「无采用」证据。

> **G4 — 使用 WHI-275 framework，不重造 rubric**：
> 判定口径必须引用 `base-eip8130-native-aa/research-sections/native-aa-framework/final.md` 的 D1-D13、D12 Mantle 适配成本、D13 场景适配和四类效果指标。新增 Mantle-specific 维度可以作为字段，但不能替代 framework 判定。

> **G5 — 源码结论必须可复核**：
> Mantle 节点能力结论必须包含本地路径、git commit SHA、文件路径和行号。若本地工作树有未提交/未跟踪文件，只能引用 git-tracked 源码内容；本轮发现的候选路径只是 seed，deep draft 必须重新核验。

## Items

### item-1: Mantle op-geth 的 EIP-7702 / Prague 节点能力核验

核验 Mantle 当前 execution client 是否具备 EIP-7702 所需协议能力，并判断该能力是否在 Mantle 网络配置中实际激活或可激活。研究顺序应从 hardfork gate 开始：`PragueTime`、`MantleSkadiTime`、Isthmus/Skadi 绑定关系、`IsPrague`/`IsMantleSkadi` 路径、以及 block processing 中对 Prague requests 或 Mantle 特殊分支的处理。然后逐层检查交易类型、签名/authorization、intrinsic gas、txpool、RPC transaction args、receipt/simulation、tests，最终给出「节点 7702 能力支持矩阵」。

本轮 outline 的本地 seed：`/Users/whisker/Work/src/networks/mantle/op-geth` 存在，`git rev-parse HEAD` 为 `3c1c571e57874019991f28fe99c36cddac7b4bef`；候选文件包括 `params/optimism_features.go` 中 `PragueTime: hardforks.IsthmusTime` 与 `PragueTime == MantleSkadiTime` 校验、`core/types/transaction.go` 中 `SetCodeTxType = 0x04`、`params/protocol_params.go` 中 `TxAuthTupleGas`、`internal/ethapi/transaction_args.go` 中 `authorizationList -> SetCodeTx`。这些只能作为 deep draft 的起点，必须重新给出源码行号和解释。

- **Priority**: high
- **Dependencies**: none

### item-2: Mantle ERC-4337 合约生态与服务可用性盘点

盘点 Mantle 上 ERC-4337 是否形成完整可运行生态，而不只看是否存在 EntryPoint 地址。需要取证 EntryPoint v0.6/v0.7/v0.8 或其他版本地址、部署时间、是否官方/服务商引用、AccountDeployed/UserOperationEvent 可观测性、bundler RPC 支持、paymaster 服务、AA SDK chain support、官方 Mantle docs 或开发者示例。每个服务商结论必须区分「官方支持 Mantle」「第三方配置可用」「社区示例」「未发现支持」「不可访问」。

该 item 要产出 Mantle 4337 生态表：组件、证据源、链 ID、版本、生产可用性、是否需要 API key/白名单、最后访问日期、置信度。不得把某 SDK 支持 EVM chains 泛化为明确支持 Mantle，除非 supported chains 或配置示例明确包含 Mantle。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 链上采用度取证：4337 UserOp 与 7702 delegation / set-code 使用量

建立 Mantle AA 采用度证据表，分别覆盖 ERC-4337 和 EIP-7702。ERC-4337 侧应优先用 EntryPoint 事件、UserOperationEvent、AccountDeployed、bundler sender、paymaster address、EntryPoint 版本和时间序列；EIP-7702 侧应扫描 typed transaction `0x04`、authorization list、delegation indicator `0xef0100 || address`、unique authorizer、unique delegate target、成功/失败率和应用场景。每个定量数据必须写查询日期、区块范围、链 ID、合约地址/tx type、过滤条件、去重口径和对照链归一化方法。

若无法获得 Mantle archive/indexer/Dune/API 数据，必须执行数据受限口径：列出尝试的 query/API/dashboard/RPC、失败原因、替代 evidence（例如 explorer 搜索、RPC sampling、小区块范围扫描、第三方服务商声明、官方文档缺席）和结论置信度。数据缺口只能降低置信度，不能自动证明 adoption 低。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 开发者体验、钱包/SDK 与应用集成支持

按照 WHI-275 的指标 B 和 D 评估 Mantle AA 的开发者路径和钱包/SDK 生态。需要检查 Mantle 官方文档、Mantle developer portal、AA provider docs、wallet docs、SDK quickstarts、example repos、chain config、paymaster/bundler dashboard、explorer/indexer 支持。研究要回答开发者从零到第一笔 sponsored/batched AA 交易需要哪些步骤、哪些 API key/服务商、是否有官方推荐路径、错误可诊断性如何、是否能被区块浏览器解析。

钱包/SDK 矩阵至少应覆盖 Alchemy Account Kit、Pimlico、Biconomy、ZeroDev、Safe、Coinbase Smart Wallet、MetaMask/Rabby/OKX/Trust 等适用对象；若服务商不公开 Mantle 支持状态，应标注不可访问或未发现，而不是写成不支持。输出应区分 `4337 support`、`7702 support`、`Mantle chain support`、`paymaster support`、`production readiness`。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: 基础设施成本、中心化与运营风险

评估 Mantle AA 方案的 infra 成本与中心化程度，覆盖 4337 Bundler/Paymaster、7702 sponsor/relayer pattern、RPC/indexer/explorer、服务商集中度和运营风险。4337 侧重点是 bundler 数量、bundle sender 集中度、paymaster 资金占用、API gating、失败 UserOp 成本、审查风险和 alt-mempool 可见性；7702 侧重点是普通 txpool/RPC 支持是否降低 infra 依赖、delegate wallet 安全和 sponsor 风控是否只是转移到应用层。

该 item 需要给出「成本/中心化证据表」：成本项、可观测代理、Mantle 证据、对照链基线、结论、置信度。若无法拿到运营商后台数据，应使用可公开观测代理，例如 unique bundler tx sender、paymaster address 数量、supported chain list、public endpoint 数量、pricing/docs、incident/status page。

- **Priority**: medium
- **Dependencies**: item-2, item-3, item-4

### item-6: 对照 WHI-275 四类指标给出效果判定

使用 `native-aa-framework/final.md` 的四类指标与判定规则，对 Mantle 当前 4337 + 7702 AA 表现作出审慎 verdict。结论必须分别给出：链上采用度、开发者体验/集成成本、基础设施成本与中心化、钱包/SDK 生态支持四项评分，再合成为总体判断：`效果好`、`效果一般`、`效果不好` 或 `证据不足`。总体「效果不好」至少需要两类指标明显弱于同类 L2 基线，并排除链整体活跃度、市场周期、单一应用缺失、数据源不可访问等混淆变量。

该 item 还要给出差距来源定位：节点能力、合约生态、Bundler/Paymaster、钱包/SDK、应用需求、链上采用、数据可观测性。若差距主要来自钱包/SDK 或应用采用，则不能把它写成 4337/7702 机制失败；若节点 7702 能力未激活或不可用，需明确其对 adoption 结论的影响。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

### item-7: 对 Mantle native AA 决策的事实输入

把 Mantle 现状映射回 D12 Mantle 适配成本与 D13 场景适配，但不越权做最终 WHI-282 决策。需要回答：当前 4337/7702 的问题中，哪些可以通过更好文档、SDK、bundler/paymaster、钱包合作或应用激励修复；哪些是 4337/7702 机制边界导致，可能需要 EIP-8130 或其他 native AA 才能改善；哪些问题即使上 native AA 也不会自动解决。该 item 应输出「native AA need signal」表，列出问题、证据、是否 native AA-specific、是否 8130 可改善、替代路径、残余风险。

此 item 只能作为后续策略建议输入，不应直接写「Mantle 应该/不应该实现 EIP-8130」。最终判断应留给后续 implementation assessment / decision recommendation。

- **Priority**: medium
- **Dependencies**: item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| core_claim | 本 item 需要证明或反驳的核心判断，尤其是「支持」和「采用效果」的边界。 | all |
| evidence_type | 证据类型：local_code、official_docs、on_chain_data、provider_docs、wallet_sdk_docs、explorer_data、dashboard、inference、unavailable。 | all |
| source_status_date | 外部文档/网页/数据源访问日期；链上数据需写查询日期、区块范围、链 ID 和合约地址/tx type。 | all |
| mantle_component | 涉及的 Mantle 组件：op-geth、hardfork config、txpool/RPC、EntryPoint、bundler、paymaster、wallet、SDK、explorer、app integration。 | all |
| support_level | 支持等级：protocol-enabled、contract-deployed、provider-supported、sdk-configurable、wallet-supported、app-used、not-found、unavailable。 | item-1, item-2, item-4 |
| measurement_method | 定量指标的计算口径、采样范围、去重方式、归一化基线和可复现查询说明。 | item-3, item-5, item-6 |
| comparison_baseline | 对照链/对照方案：Base、Ethereum、OP Mainnet、Arbitrum、Polygon、普通 EOA tx、ERC-4337、EIP-7702。 | item-3, item-5, item-6 |
| data_limitation | 数据不可访问、权限受限、无公开索引、无 dashboard、API 限流、样本太小或口径不透明等限制及尝试方式。 | item-3, item-4, item-5, item-6 |
| confidence_level | 高/中/低，并说明限制：源码可复核、数据新鲜度、样本偏差、二手来源、服务商口径不透明。 | all |
| whi275_metric | 映射到 WHI-275 四类效果指标：链上采用度、开发者体验/集成成本、基础设施成本与中心化、钱包/SDK 生态支持。 | item-3, item-4, item-5, item-6 |
| rubric_dimensions | 映射到 D1-D13，重点是 D3、D5、D8、D10、D11、D12、D13。 | item-1, item-2, item-5, item-6, item-7 |
| gap_source | 差距来源分类：节点能力、合约生态、Bundler/Paymaster、钱包/SDK、应用采用、数据可观测性、外部市场因素。 | item-6, item-7 |
| native_aa_implication | 对 EIP-8130/native AA 决策的事实含义：可由 4337/7702 优化解决、native AA 可能改善、native AA 也无直接帮助、证据不足。 | item-7 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | flow | Mantle AA 支持分层图：op-geth/Pectra/7702 节点能力 -> 4337 EntryPoint/Bundler/Paymaster -> wallet/SDK -> app/user adoption，标明每层证据和失败点。 | mermaid | item-1, item-2, item-4 |
| diag-2 | comparison | Mantle 4337 UserOp path vs 7702 set-code tx path：谁构造交易、谁验证、谁付 gas、进入哪个 mempool/RPC、如何上链和可观测。 | mermaid | item-1, item-2, item-3 |
| diag-3 | matrix | WHI-275 四类效果指标评分矩阵：每格包含 Mantle 证据、对照链基线、结论、置信度、数据限制。 | ascii | item-6 |
| diag-4 | flow | 数据受限处理流程：目标数据源 -> 查询尝试 -> 成功/失败 -> 替代证据 -> 置信度 -> 不能下结论的边界。 | mermaid | item-3, item-6 |
| diag-5 | matrix | 差距来源定位表：节点/合约/infra/钱包-SDK/采用/数据可观测性 × 4337/7702 × 可能修复路径 × native AA implication。 | ascii | item-6, item-7 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | local_research | `base-eip8130-native-aa/research-sections/native-aa-framework/final.md`：必须引用四类效果指标、D1-D13、D12/D13 和判定规则；不得重造 rubric。 | 1 |
| src-2 | code_analysis | 本地 Mantle op-geth：`/Users/whisker/Work/src/networks/mantle/op-geth`，必须给出 commit SHA、文件路径、行号，核验 Prague/7702 activation、`SetCodeTxType`、authorization list、gas、RPC/txpool/simulation/receipt/tests。 | 6 |
| src-3 | official_docs | Mantle 官方文档、developer portal、network/hardfork/release docs、AA/Account Abstraction/7702/4337 相关页面；外部结论附访问日期。 | 3 |
| src-4 | official_specs | ERC-4337、EIP-7702、EIP-7600 Pectra、相关 EntryPoint/Bundler/Paymaster specs；用于支持机制边界和状态，不替代 Mantle 实证。 | 4 |
| src-5 | contract_deployments | Mantle 上 EntryPoint 地址、版本、部署交易、事件、factory/account/paymaster 合约地址；优先 explorer、official docs、服务商 docs 或 verified source。 | 3 |
| src-6 | on_chain_data | Mantle 4337 UserOp/Event 与 7702 type-0x04/delegation 数据；至少包含 Mantle，并尽力包含 Base、Ethereum、OP Mainnet、Arbitrum、Polygon 中两个以上对照链；写查询日期、区块范围和口径。 | 4 |
| src-7 | provider_docs | Bundler/Paymaster/AA infra 服务商支持矩阵与文档：Alchemy、Pimlico、Biconomy、ZeroDev、Stackup、Candide 或其他可验证服务；必须记录 Mantle support 状态和访问日期。 | 5 |
| src-8 | wallet_sdk_docs | 钱包/SDK 文档与 supported chains：Safe、Coinbase Smart Wallet、MetaMask、Rabby、OKX、Trust、Alchemy Account Kit、Pimlico permissionless、Biconomy、ZeroDev 等；区分 4337、7702、Mantle chain support。 | 6 |
| src-9 | explorer_indexer_data | Mantle explorer、Blockscout/Etherscan 风格 API、Dune/Flipside/BundleBear/Jiffyscan 或可替代索引源；若不可访问，按数据受限口径记录。 | 3 |
| src-10 | comparison_baselines | Base/Ethereum/OP/Arbitrum/Polygon 的 4337/7702 adoption 或支持状态，用于归一化对照，不能只比较绝对 tx 数。 | 3 |
| src-11 | expert_or_provider_commentary | 服务商博客、AA working group、Ethereum Magicians、provider engineering notes 等可用于解释 DX/infra 成本；只能辅助解释，不能替代 primary code/data。 | 3 |
| src-12 | unavailable_sources_log | 不可访问或数据受限来源清单：URL/API/query、尝试时间、失败原因、替代方法、对结论影响。若所有关键数据均可访问，该表可为空但必须保留。 | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
