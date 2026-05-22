---
topic: "Sui Gasless Transaction 机制原理分析"
project_slug: sui-gasless-stablecoin-payments
topic_slug: sui-gasless-mechanism
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: sui-gasless-stablecoin-payments/outlines/sui-gasless-mechanism.md
  draft: sui-gasless-stablecoin-payments/research-sections/sui-gasless-mechanism/drafts/round-{n}.md
  final: sui-gasless-stablecoin-payments/research-sections/sui-gasless-mechanism/final.md
  index: sui-gasless-stablecoin-payments/research-sections/_index.md

scope: |
  分析 Sui gasless / sponsored transaction 机制在协议层和产品层的完整设计。重点覆盖：
  TransactionKind 与 GasData 分离带来的 sender / gas owner 分离能力；Gas 对象与
  address balance 两种 gas 支付来源的所有权、签名和对象并发约束；Gas Station / sponsor
  服务如何验证、补全、签名和提交用户交易；Sui gasless stablecoin transfers 在协议配置、
  allowlist、PTB 形状、gasPrice=0、gasPayment=[]、限流和优先级上的特殊路径；以及
  Fireblocks 等托管/机构平台在 stablecoin payments 场景中承担的 custody、policy、
  signing 和 API 集成角色。

audience: |
  Multica 研究 squad 的 Adversarial Agent 与 Technical Writer；希望评估 Sui
  gasless stablecoin payments 方案的支付产品负责人、钱包/托管平台工程师、Gas Station
  服务提供方、合规与风控团队。读者熟悉公链交易、签名和 gas 概念，但不一定熟悉 Sui
  的对象模型、PTB、address balances、funds withdrawal、sponsored transaction 签名
  编排或 2026 年 gasless stablecoin free-tier 机制。

expected_output: |
  - Sui gasless transaction 机制概览：区分通用 sponsored transactions、address-balance
    sponsored gas payment、以及协议内置 gasless stablecoin transfers/free tier
  - Sponsored Transaction 签名流程详细分析：TransactionKind / TransactionDataV1 /
    GasData / SenderSignedTransaction 数据结构、sender 与 gas owner 分离、用户发起和
    sponsor 发起两类流程、签名覆盖范围与顺序无关性、gas object 并发和 censorship 风险
  - Gas Station 服务架构说明：API 边界、策略校验、gas coin 池或 address balance 资金池、
    sponsor key/custody、rate limiting、风控/合规、提交与重试、第三方 sponsor 接入
  - Stablecoin payments 端到端流程：用户发起 stablecoin 转账、SDK/钱包 eligibility 检测、
    allowlisted Move calls、gasPrice=0 / gasBudget=0 / gasPayment=[]、validator admission、
    congestion 下 paid tx 优先、链上确认与监控
  - Fireblocks 集成角色：托管钱包和机构策略引擎、稳定币资产支持、Sui signing/custody
    能力、与 Gas Station 或 Sui native gasless flow 协作的位置；清楚区分已由 primary
    source 证实的能力与需要 Fireblocks 文档/公告确认的推断
  - 至少 3 张 Mermaid 图：Sponsored Transaction 签名与提交流程序列图、Gas Station 服务
    架构图、Stablecoin gasless payment 端到端流程图
  - 至少引用 3 个 primary sources，优先使用 Sui 官方文档、Sui 官方博客、Sui Payments
    产品页、MystenLabs/sui 源码；Fireblocks 仅使用官方文档/公告作为二级或合作方来源

source_requirements_summary: |
  Primary sources 必须包括：Sui 官方 Sponsored Transactions 文档、Sui Gasless Stablecoin
  Transfers 文档、MystenLabs/sui 源码中 TransactionDataV1 / GasData / sponsorship /
  gasless validation / protocol config / rate limiter 的相关文件，Sui 官方博客
  "Sui Launches Gasless Stablecoin Transfers with Support from Fireblocks"，以及 Sui
  Payments 产品页或 onchain finance payments 文档。Secondary sources 可包含 Fireblocks
  官方 Sui 支持/集成文档、Fireblocks 博客、社区讨论；社区资料只用于补充，不可作为协议
  结论的唯一证据。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-22T10:45:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-22T10:45:00+08:00"
---

# Research Outline: Sui Gasless Transaction 机制原理分析

## Research Questions

1. Sui 如何在协议层把交易发送方、交易 intent 和 gas 支付方拆开？`TransactionKind`、
   `TransactionDataV1`、`GasData`、`SenderSignedTransaction` 的边界分别是什么？
2. Sponsored transaction 的完整签名流程是什么？用户和 sponsor 谁先签、签名覆盖哪些字节、
   signature list 如何验证，gas object 或 address balance 的所有权如何与 sender 协调？
3. Gas Station 服务需要哪些组件？第三方 sponsor 如何接入，如何做 allowlist、风控、gas
   资金管理、key custody、rate limiting、提交和重试？
4. Gasless stablecoin transfers 与普通 sponsored transaction 有何区别？它如何通过
   protocol config、allowlisted stablecoin types、限制 PTB shape、`gasPrice=0` 和
   `gasPayment=[]` 实现无 SUI 转账？
5. 在 stablecoin payments 场景下，从用户在钱包/托管平台发起转账到链上确认，完整端到端
   流程和失败路径是什么？
6. Fireblocks 等托管平台在方案中具体承担什么角色？哪些是 Fireblocks 已公开支持的能力，
   哪些只是与 Gas Station 协作的可行架构假设？

## Items

### item-1: 协议数据模型：TransactionKind、TransactionDataV1 与 GasData 分离

建立 sponsored transaction 的协议层基本模型，解释 Sui 为什么可以让交易 sender 与 gas
owner 分离。必须从官方文档和源码同时确认：

- `TransactionDataV1` 包含 `kind: TransactionKind`、`sender`、`gas_data`、`expiration`；
- `GasData` 包含 `payment: Vec<ObjectRef>`、`owner`、`price`、`budget`；
- 当 `gas_data.owner != sender` 时交易是 sponsored transaction；
- `GasData.payment` 中的 gas objects 必须由 `GasData.owner` 拥有，且由 sponsor 负责提供；
- `TransactionKind` 是业务操作本身，`GasData` 是 gas 支付上下文，二者一起被签名；
- sponsorship 当前只支持 programmable transaction 路径，需核实 `check_sponsorship`
  对非 PTB 的限制。

本 item 还要区分三种相近但不同的机制：

1. **普通交易**：sender 自己提供 gas coin，`gas owner == sender`；
2. **通用 sponsored transaction**：sponsor 提供 gas coin 或 address balance，sender 与
   sponsor 都签名；
3. **gasless stablecoin transfer/free tier**：协议允许符合条件的 stablecoin PTB 以
   `gasPrice=0` 和空 gas payment 通过验证，不等同于任意交易的 sponsor 代付。

- **Priority**: high
- **Dependencies**: none

### item-2: Sponsored Transaction 签名流程与所有权协调

完整拆解 sponsored transaction 的签名编排，覆盖官方文档列出的 user-proposed、
sponsor-proposed 和 wildcard gas payment 三种模式。研究重点：

- `SenderSignedTransaction` / transaction bytes 的签名覆盖范围：sender 和 sponsor 都对
  完整 `TransactionData` 签名，包含 `GasData`，防止第三方篡改 gas payment；
- signature list 顺序无关，但必须包含 sender 与 gas owner/sponsor 的有效签名；
- user-proposed 模式：用户构造 `GasLessTransactionData` 或 only `TransactionKind`，
  sponsor 校验并补齐 `GasData` 后签名，再交还用户签名/提交；
- sponsor-proposed 模式：sponsor 先构造并签署带 gas 的 `TransactionData`，用户确认 intent
  后签名；
- TypeScript SDK 方式：`onlyTransactionKind`、`Transaction.fromKind`、`setSender`、
  `setGasOwner`、`setGasPayment`、双签名 `executeTransaction`；
- gas coin model 下 sponsor gas object 的并发使用风险：同一 object version 被多个
  inflight tx 使用会导致失败或 epoch 级 equivocation 风险；
- address balance model 下 `setGasPayment([])` 如何减少 gas coin inventory / locking
  复杂度，同时 storage rebates 如何归属 sponsor；
- censorship 风险：若通过 sponsor/Gas Station 提交，sponsor 可能延迟或不提交，用户可直接
  向 full node 提交双签名交易作为缓解。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Gas Station 服务架构与第三方 Sponsor 接入机制

设计并验证一个可落地的 Gas Station 架构，把协议机制映射到服务组件。该 item 应明确哪些
是 Sui 官方文档中的 role/API 示例，哪些是基于支付场景的架构设计建议。

必须覆盖：

- **API 层**：
  - `request_gas_and_signature(gasless_tx)`：用户发起，Gas Station 校验并返回 sponsor
    签名后的交易数据；
  - `request_gas(...)`：wildcard / gas object 分配；
  - `submit_sole_signed_transaction(...)`：用户单签后由 sponsor 补签并提交；
  - `submit_dual_signed_transaction(...)`：双签名交易提交/代理提交。
- **Policy / Risk Engine**：按 app、用户、asset、amount、recipient、Move call target、
  PTB shape、地理/合规策略、速率和预算校验 sponsorship。
- **Gas Funding Layer**：维护 SUI gas coin pool、coin splitting/merge、object version
  reservation，或使用 address balance 作为 gas payment；需要列出两者的 operational
  tradeoff。
- **Sponsor Signer / Custody**：本地 HSM、KMS、MPC、Fireblocks/TSS 等签名来源；必须说明
  sponsor signature 是链上有效签名，不只是 relayer API token。
- **Submission Layer**：full node / gRPC / GraphQL / JSON-RPC 提交、重试、digest 监控、
  congestion/backoff、失败分类。
- **Accounting & Abuse Controls**：per-user/app budget、gas budget cap、sponsor balance
  reconciliation、rate limit、fraud signals、审计日志。
- **Third-party Sponsor 接入**：第三方 sponsor 可以作为 gas funds provider、signer、
  policy provider 或 full managed Gas Station；接入合同至少需要 quote/approval API、
  signing API、webhook、settlement/accounting、revocation 和 key rotation。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Gasless Stablecoin Transfers / Free Tier 协议路径

单独分析 Sui 2026 年引入的 gasless stablecoin transfers，避免与通用 sponsored transaction
混淆。必须从文档和源码确认以下问题：

- 当前 eligible stablecoin allowlist 由 protocol config 管理，文档表应与
  `get_gasless_allowed_token_types` / protocol config 常量交叉验证；
- mainnet allowlist 的 stablecoin 类型和最小转账门槛（文档称 $0.01 minimum transfer per
  stable，源码以 6 decimals 的 `10_000` 表示）；
- 交易限定为 allowlisted `balance` / `coin` 操作，重点是 `0x2::balance::send_funds<T>`，
  并覆盖 `withdrawal_split`、`redeem_funds`、`send_funds` 等被允许函数；
- `gasPayment` 为空、`gasPrice=0`、`gasBudget=0` 的语义，与 address balance gas payment
  / funds withdrawal 机制的关系；
- 不能写任意 object，不能用于 NFT mint、swap、非 allowlisted token、SUI transfer 或任意
  app interaction；
- validators 如何验证 gasless PTB：command allowlist、unused inputs 限制、pure input
  byte 限制、tx size 限制、computation units cap、remaining balance check；
- gasless 交易在 congestion 下优先级低于 paid transactions，且有 `gasless_max_tps` 和
  local/consensus 双层 rate limiter；
- SDK 自动检测边界：gRPC/GraphQL transports 自动 simulate/set gas；JSON-RPC fallback 需要
  钱包手动设置并先确认 allowlist。

- **Priority**: high
- **Dependencies**: item-1

### item-5: Stablecoin Payments 端到端流程与失败路径

把协议机制组织成支付产品视角的完整流程。应至少包含两条路径：

1. **Native gasless stablecoin transfer path**：用户钱包/Fireblocks vault 持有 allowlisted
   stablecoin；钱包构造 `balance::send_funds<T>` PTB；SDK 或钱包确认 eligibility；
   tx 以 zero gas params 提交；validator admission 通过 gasless validation；共识提交；
   recipient 余额更新；钱包/支付后台监控 digest 和 effects。
2. **Sponsored payment path**：当支付不是 free-tier eligible（例如非 allowlisted token、
   批量支付、业务合约、memo/metadata、合规 wrapper、merchant settlement flow）时，钱包
   或应用把 transaction kind / gasless tx 发给 Gas Station；Gas Station 策略校验、补齐 gas、
   sponsor 签名；用户签名；由用户或 Gas Station 提交；后台 reconciliation。

失败路径需要矩阵化列出：

- token 不在 allowlist；
- PTB 包含不支持的 Move call / 写 object / shared object / receiving object；
- amount 低于最小门槛或 decimals 处理错误；
- SDK 使用 JSON-RPC 而未正确设置 zero gas；
- gasless rate limited / validator overloaded / paid tx congestion 抢占；
- sponsor gas coin object version 冲突；
- sponsor address balance 不足；
- user 或 sponsor 签名缺失/过期/chain identifier 不匹配；
- Fireblocks policy 拒签、travel rule / compliance hold、vault asset 不支持；
- full node 提交失败或 digest 未被索引。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4

### item-6: Fireblocks 与托管平台集成角色

聚焦 Fireblocks 在 Sui gasless stablecoin payments 方案中的实际角色，避免把未证实的产品
能力写成事实。需要分层确认：

- **已证实能力**：Fireblocks 是否官方宣布支持 Sui、哪些资产/交易类型、是否参与 Sui
  gasless stablecoin transfers 发布、是否提供 custody / policy / signing / MPC/TSS /
  WalletConnect 或 API flows；
- **支付流程角色**：
  - 机构用户或商户的 stablecoin 托管钱包；
  - transaction initiation 与 policy approval；
  - sender signature provider（当 Fireblocks 托管 sender wallet）；
  - sponsor signer/custody provider（若企业把 sponsor key 或 SUI/address balance 放在
    Fireblocks）；
  - compliance hold、AML screening、travel rule、webhook 回调；
  - reconciliation source of truth。
- **与 Gas Station 协作模式**：
  1. Fireblocks 只做 sender custody，Gas Station 独立持有 sponsor key；
  2. Fireblocks 同时托管 sponsor treasury/signing key，Gas Station 调 Fireblocks signing API；
  3. Native gasless stablecoin transfer 中无需 sponsor 签名，Fireblocks/钱包只需构造和签署
     eligible zero-gas transaction；
  4. 托管平台作为 third-party Gas Station operator，为多个 merchant/app 提供 sponsorship。
- **待验证问题**：Fireblocks 当前是否原生识别 Sui gasless free-tier eligibility、是否自动
  设置 `gasPrice=0` / `gasPayment=[]`、是否支持 Sui PTB 级别 policy inspection、是否支持
  sponsor-sign-and-return 而非直接广播。

- **Priority**: medium
- **Dependencies**: item-3, item-4, item-5

### item-7: 安全、风控与产品边界

总结该方案的安全和产品边界，形成可供 Technical Writer 写入最终报告的 caveats：

- sponsor 不等于 multisig co-author：sponsor pays gas，但不应被描述为共同批准业务 intent；
- 双签名保护的是完整 transaction bytes，一旦 sponsor 补齐 `GasData`，用户必须重新校验
  business intent、gas owner、gas budget、expiration 和 chain；
- Gas Station 是新的信任和 liveness 组件：可能拒绝、延迟、审查或错误补齐 gas；
- gas coin pool 需要 object reservation 和并发控制；
- address balance sponsorship 简化 gas coin locking，但仍需 sponsor balance、rebate、
  accounting 和 withdrawal 风控；
- gasless stablecoin transfers 的 free tier 是 narrow path，不可包装成 "Sui 上所有
  stablecoin payment 都无 gas"；
- congestion 下 free-tier gasless tx 的 UX 可能弱于 paid/sponsored tx；
- 机构托管 flow 需考虑 policy latency、合规冻结、API 可用性和 custody key 权限；
- 合规和审计要求可能决定选择 native gasless path、Gas Station path 或 Fireblocks-managed
  path。

- **Priority**: medium
- **Dependencies**: item-2, item-3, item-4, item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| protocol_object | 涉及的数据结构、trait、Move function、protocol config key 或 service component 名称 | all |
| source_evidence | Primary/secondary source 链接、源码文件、commit、行号或文档段落 | all |
| transaction_role | sender、gas owner、sponsor、Gas Station、custodian、full node、validator 等角色 | item-1, item-2, item-3, item-5, item-6 |
| signing_requirement | 谁签名、签名覆盖什么、签名顺序、缺失签名的验证结果 | item-2, item-3, item-6 |
| gas_payment_source | gas coin object、address balance、zero gas/free-tier 的来源和所有权 | item-1, item-2, item-3, item-4, item-5 |
| eligibility_rule | stablecoin allowlist、Move call allowlist、PTB shape、gas params、amount threshold、rate limit | item-4, item-5 |
| failure_mode | 失败条件、错误来源、用户影响、恢复/重试策略 | item-2, item-3, item-4, item-5, item-7 |
| trust_assumption | 用户、sponsor、Gas Station、custodian、validator 或 full node 之间的信任边界 | item-3, item-5, item-6, item-7 |
| implementation_guidance | 钱包、支付应用、Gas Station 或托管平台应采取的工程实现建议 | item-3, item-5, item-6, item-7 |
| confidence | 高 / 中 / 低；高=primary source 与源码交叉验证，中=官方公告但缺少实现细节，低=合理架构推断 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | sequence | Sponsored Transaction 签名与提交流程：user-proposed 与 sponsor-proposed 两条 swimlane，展示 TransactionKind/GasData 补齐、双签名和提交 | mermaid sequenceDiagram | item-2 |
| diag-2 | architecture | Gas Station 服务架构图：wallet/app、policy engine、gas funding layer、sponsor signer/custody、submission layer、monitoring/accounting、third-party sponsor/Fireblocks | mermaid flowchart | item-3, item-6 |
| diag-3 | sequence | Stablecoin gasless payment 端到端流程：wallet eligibility detection、zero gas build、validator gasless validation、rate limit、consensus、recipient confirmation | mermaid sequenceDiagram | item-4, item-5 |
| diag-4 | decision | Payment path 决策树：native gasless free-tier vs sponsored tx vs normal paid tx，按 token、PTB shape、transport、custody policy 分支 | mermaid flowchart | item-5, item-7 |
| diag-5 | trust-boundary | Fireblocks / custodian 与 Gas Station 协作模式：sender custody、sponsor custody、managed Gas Station、native free-tier 四种模式 | mermaid flowchart | item-6 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | Sui Sponsored Transactions 文档，包含 roles、TransactionData/GasData、签名流程、风险和 TypeScript 示例 | 1 |
| src-2 | official_docs | Sui Gasless Stablecoin Transfers 文档，包含 allowlist、eligibility、SDK transport、限制和监控 | 1 |
| src-3 | source_code | MystenLabs/sui `crates/sui-types/src/transaction.rs`：GasData、TransactionDataV1、is_gasless_transaction、validate_gasless_transaction、check_sponsorship | 1 |
| src-4 | source_code | MystenLabs/sui `crates/sui-protocol-config/src/lib.rs`：enable_gasless、gasless_allowed_token_types、gasless_max_tps、mainnet allowlist/min thresholds | 1 |
| src-5 | source_code | MystenLabs/sui `crates/sui-core/src/gasless_rate_limiter.rs` 与 authority admission path，验证 gasless rate limiting / congestion behavior | 1 |
| src-6 | official_docs | Sui Address Balances 文档中 sponsored transactions with address balances、`setGasPayment([])`、storage rebate 归属 | 1 |
| src-7 | official_docs | Sui PTB builder / TypeScript SDK 文档，说明 `onlyTransactionKind`、`Transaction.fromKind` 和 sponsored PTB build path | 1 |
| src-8 | official_blog | Sui 官方博客关于 gasless stablecoin transfers 和 Fireblocks support 的公告 | 1 |
| src-9 | product_docs | Sui Payments 产品页或 onchain finance payments 文档，用于支付产品场景定位 | 1 |
| src-10 | partner_docs | Fireblocks 官方文档/博客/API 文档，确认 Sui custody/signing/asset support 和 gasless support 边界 | 1 |
| src-11 | secondary_discussion | 社区技术讨论、钱包/SDK issue、partner examples；仅用于补充实现注意事项 | 0 |

## Evidence Starting Points

- Sui docs: `/develop/transaction-payment/sponsor-txn`
- Sui docs: `/develop/transaction-payment/gasless-stablecoin-transfers`
- Sui docs: `/onchain-finance/asset-custody/address-balances/using-address-balances`
- Sui docs: `/develop/transactions/ptbs/building-ptb`
- Sui docs: `/onchain-finance/payments`
- Sui official blog: "Sui Launches Gasless Stablecoin Transfers with Support from Fireblocks"
- Sui source commit observed during outline generation: `MystenLabs/sui@e09f31f7606bca023907740966b3bd8f8f5a4703`
  - `crates/sui-types/src/transaction.rs`
  - `crates/sui-protocol-config/src/lib.rs`
  - `crates/sui-core/src/gasless_rate_limiter.rs`
  - `crates/sui-core/src/authority_server.rs`

## Draft Structure Recommendation

1. Executive summary: three meanings of "gasless" on Sui.
2. Protocol primitive: TransactionKind + GasData + dual signatures.
3. Sponsored transaction flows: user-proposed, sponsor-proposed, wildcard, address-balance variant.
4. Gas Station architecture and third-party sponsor integration.
5. Native gasless stablecoin transfers/free-tier: allowlist, validation, rate limit, limitations.
6. Stablecoin payments end-to-end: wallet/custodian flow, submission, confirmation, monitoring.
7. Fireblocks integration roles and open verification points.
8. Security, trust boundaries, failure modes, and product recommendations.
9. Mermaid diagrams and source appendix.

## Quality Checklist

- [ ] Clearly distinguishes sponsored transactions from native gasless stablecoin transfers.
- [ ] Uses primary sources for all protocol claims and cites code paths/commit for validation logic.
- [ ] Includes at least 3 primary sources and at least one source-code citation.
- [ ] Does not claim Fireblocks-specific behavior unless supported by Fireblocks or Sui official sources.
- [ ] Includes all three required Mermaid diagrams.
- [ ] Covers gas object ownership, address balance sponsorship, signature flow, Gas Station architecture, stablecoin free-tier flow, and Fireblocks role.
- [ ] Marks low-confidence architecture assumptions explicitly.

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create | full outline | Initial outline from Orchestrator dispatch | Multica issue 3cee9256-14f7-46d2-8df8-c8d72274ec9e comment 178990e8-1c8c-4ee8-a17f-72609c05c918 |
