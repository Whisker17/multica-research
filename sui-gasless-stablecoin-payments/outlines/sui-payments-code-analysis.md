---
topic: "Sui Payments 模块与 Sponsored Transaction 代码实现解析"
project_slug: sui-gasless-stablecoin-payments
topic_slug: sui-payments-code-analysis
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: sui-gasless-stablecoin-payments/outlines/sui-payments-code-analysis.md
  draft: sui-gasless-stablecoin-payments/research-sections/sui-payments-code-analysis/drafts/round-{n}.md
  final: sui-gasless-stablecoin-payments/research-sections/sui-payments-code-analysis/final.md
  index: sui-gasless-stablecoin-payments/research-sections/_index.md

scope: "Sui 源码中 TransactionData 结构体的 sender/sponsor 分离实现、Sponsored Transaction 在交易验证和执行路径上的代码逻辑、Gas metering 与 sponsor 预授权/限额机制的代码实现、Payments 相关 Move 合约模块的核心逻辑、Token transfer + sponsor 付 gas 的原子性保证实现。"
audience: "研究 Sui gasless stablecoin payments 方案的工程、产品和技术写作成员，需要代码级证据、路径和函数名支撑最终报告。"
expected_output: "一份代码走读型研究 section，覆盖 TransactionData/GasData 结构、Sponsored Transaction 验证与执行路径、Gas metering/预授权/限额、Payments/coin Move 模块、token transfer + sponsor 付 gas 的原子性，并直接引用源码文件路径和关键函数。"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-22T03:19:21Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-22T03:19:21Z"

upstream_context:
  dependency_topic_slug: sui-gasless-mechanism
  dependency_final_path: sui-gasless-stablecoin-payments/research-sections/sui-gasless-mechanism/final.md
  dependency_main_commit: 27bfbd34617ad115ca052b731e5ff9e66eb5da32
  source_code_revision_observed: MystenLabs/sui@e09f31f7606bca023907740966b3bd8f8f5a4703
---

# Research Outline: Sui Payments 模块与 Sponsored Transaction 代码实现解析

## Items

### item-1: TransactionData / GasData 数据结构与序列化边界

Investigate how Sui represents the business signer and the gas sponsor in core transaction data. The draft should start from `crates/sui-types/src/transaction.rs` and explain `TransactionData::V1`, `TransactionDataV1`, `GasData`, `TransactionDataAPI::required_signers`, `gas_owner`, `is_sponsored_tx`, and the constructor variants that allow a sponsor (`new_with_gas_coins_allow_sponsor`, `new_transfer_sui_allow_sponsor`, `new_programmable_allow_sponsor`). It should also explain what is serialized/signed via `SenderSignedData`, why signatures cover the whole `TransactionData` including `GasData`, and how this differs from the application-level `GasLessTransactionData` interface described in docs.

- **Priority**: high
- **Dependencies**: none

### item-2: Sponsored Transaction 签名验证与交易输入验证路径

Trace the validation path from signed transaction admission through signature verification, transaction validity checks, gas object/address-balance checks, and object ownership checks. The key anchors are `crates/sui-types/src/signature_verification.rs::verify_sender_signed_data_message_signatures`, `TransactionDataV1::check_sponsorship`, `crates/sui-core/src/authority.rs::pre_object_load_checks` / `handle_transaction_deny_checks`, and `crates/sui-transaction-checks/src/lib.rs::check_transaction_input`, `check_gas`, and `check_objects`. The draft should isolate sponsored-specific branches: `required_signers` includes sponsor when `gas_owner != sender`, sponsorship is limited to programmable transactions, gas input objects are checked against `transaction.gas_owner()`, and address-balance gas uses `gas_data.payment = []`.

- **Priority**: high
- **Dependencies**: item-1

### item-3: Execution Engine 中 sponsor、TxContext 与对象所有权不变量

Follow execution from checked transaction inputs into the latest Sui adapter. The draft should analyze `sui-execution/latest/sui-adapter/src/execution_engine.rs::execute_transaction_to_effects`, especially sponsor derivation from `gas_data.owner`, `TxContext::new_from_components`, `compute_input_reservations`, and the call into `TemporaryStore::check_ownership_invariants`. It should explain how sender and sponsor become authenticated mutation roots, why non-gas owned inputs must belong to sender while gas objects belong to gas owner, and how `tx_context::sponsor` exposes sponsor information to Move natives.

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Gas metering、GasCharger 与 sponsor 预授权/限额机制

Analyze how gas budget, gas price, gas object/address-balance availability, and final charging are enforced. The draft should use `crates/sui-types/src/gas.rs::SuiGasStatus`, `crates/sui-types/src/gas_model/gas_v2.rs::SuiGasStatus`, `crates/sui-transaction-checks/src/lib.rs::check_gas`, and `sui-execution/latest/sui-adapter/src/gas_charger.rs::GasCharger`, `PaymentKind`, `PaymentMethod`, `PaymentLocation`, `charge_gas`, `compute_storage_and_rebate`, and `SmashMetadata::smash_gas`. It should connect sponsor preauthorization to signed `GasData.budget`, available gas coin/address-balance checks, `FundsWithdrawalArg::balance_from_sponsor`, and accumulator reservations, rather than inventing an off-chain allowance model.

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: Gas 对象选择、smashing、转移与回收生命周期

Map the lifecycle of gas payment sources in sponsored scenarios. The draft should cover coin-object sponsorship (`GasData.payment` as sponsor-owned object refs), address-balance sponsorship (`payment=[]`), coin-reservation compatibility limits, gas object owner checks, gas smashing into the primary payment source, and final charge/refund behavior if the gas coin is transferred or sent to address balance. Important files include `sui-execution/latest/sui-adapter/src/gas_charger.rs`, `sui-execution/latest/sui-adapter/src/static_programmable_transactions/execution/context.rs::refund_max_gas_budget` / `finish_gas_coin`, `crates/sui-transaction-checks/src/lib.rs::check_objects`, and `crates/sui-core/src/accumulators/design_docs/coin_reservations.md`.

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: Payments / payment intent / Move coin 模块核心逻辑

Clarify what "Payments" means in Sui docs and code for this topic. The draft should distinguish the documentation-level payment intent pattern from on-chain framework modules: `docs/content/onchain-finance/payments.mdx`, `docs/content/onchain-finance/payment-intents.mdx`, `docs/content/develop/transaction-payment/sponsor-txn.mdx`, `crates/sui-framework/packages/sui-framework/sources/pay.move`, `coin.move`, `balance.move`, `tx_context.move`, and `funds_accumulator.move`. It should explain that `sui::pay` is a coin utility module, while payment intents are PTBs whose atomicity comes from transaction execution semantics rather than a separate "payments contract" that sponsors gas.

- **Priority**: high
- **Dependencies**: item-1

### item-7: Token transfer + sponsor 付 gas 的原子性与失败语义

Explain the exact atomicity guarantee for a sponsored payment PTB: token transfer commands and gas charging are committed in one transaction effects set, and if Move execution fails the business writes are reset while gas/storage charging follows the gas model. The draft should combine item-3 and item-4 evidence with `sui-execution/latest/sui-adapter/src/execution_engine.rs`, `gas_charger.rs::charge_gas`, `TemporaryStore::into_effects`, and the payment intent docs' PTB atomicity statements. It should be explicit about what still can happen on failure: gas may be charged to sponsor for failed non-gasless execution, while token transfers do not partially commit.

- **Priority**: high
- **Dependencies**: item-3, item-4, item-6

### item-8: SDK / API construction evidence and test coverage anchors

Collect secondary SDK/API and test evidence to cross-check the code walk-through. The draft should include official construction examples from `docs/content/develop/transaction-payment/sponsor-txn.mdx` and address-balance sponsorship from `docs/content/onchain-finance/asset-custody/address-balances/using-address-balances.mdx`, plus source-level tests such as `crates/sui-core/src/unit_tests/authority_tests.rs::test_handle_sponsored_transaction`, `crates/sui-core/src/unit_tests/gas_tests.rs::test_invalid_gas_owners`, `crates/sui-core/src/unit_tests/transaction_deny_tests.rs`, `crates/sui-e2e-tests/tests/gasless_tests.rs`, and SDK builder methods such as `setGasOwner`, `setGasPayment`, and `executeTransaction` where present. Use tests as corroboration, not as the primary source of protocol truth.

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-4

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| core_claim | The precise technical claim the section will make for this item, phrased so it can be falsified by code. | all |
| primary_code_paths | Exact repository-relative source files, structs, functions, traits, and modules to inspect. | all |
| control_flow | Step-by-step runtime path, including caller/callee boundaries and sponsored-specific branches. | item-2, item-3, item-4, item-5, item-7 |
| data_model | Relevant structs/enums/fields, serialization/signing boundaries, and ownership semantics. | item-1, item-2, item-4, item-5 |
| sponsor_specific_logic | Branches where `gas_owner != sender`, `sponsor`, `GasData.owner`, or `WithdrawFrom::Sponsor` changes behavior. | item-1, item-2, item-3, item-4, item-5, item-7, item-8 |
| gas_payment_mode | Whether the path uses gas coin objects, address balance, coin reservations, protocol-level gasless mode, or unmetered/system mode. | item-2, item-4, item-5, item-7, item-8 |
| preauthorization_and_limits | How budgets, gas price, object versions, reservations, allowlists, rate limits, and balance checks constrain sponsor exposure. | item-2, item-4, item-5, item-8 |
| atomicity_and_failure_semantics | What commits, what rolls back, and what gas/rebate effects remain when execution succeeds, aborts, or runs out of gas. | item-3, item-4, item-5, item-7 |
| payment_module_role | Whether the source is a Move framework module, SDK/doc payment pattern, or protocol/execution layer component. | item-6, item-7 |
| evidence_strength | Label each finding as high/medium/low confidence, with rationale and any missing source caveats. | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | Sponsored Transaction data structure relationship: `SenderSignedData`, `IntentMessage<TransactionData>`, `TransactionDataV1`, `GasData`, sender, gas owner/sponsor, gas payment, required signers, and signatures over full bytes. | mermaid | item-1, item-2 |
| diag-2 | flow | Verification and execution path from submitted transaction to signature verification, sponsorship check, gas/object checks, execution engine, ownership invariant check, gas charging, and effects. Mark the branches where sponsored transaction behavior diverges from ordinary sender-paid transactions. | mermaid | item-2, item-3, item-4, item-7 |
| diag-3 | flow | Gas payment source lifecycle for coin-object sponsorship versus address-balance sponsorship: selection, signing/preauthorization, input loading, gas smashing/materialization, budget refund, charge location override, final deduction/rebate. | mermaid | item-4, item-5 |
| diag-4 | comparison | Payments concept map distinguishing `sui::pay` Move utilities, `coin`/`balance`/`funds_accumulator`, payment intents as PTBs, sponsored transactions, and native gasless stablecoin transfer eligibility. | mermaid | item-6, item-7 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | Primary Rust protocol/source evidence from `MystenLabs/sui`, especially `crates/sui-types`, `crates/sui-transaction-checks`, `crates/sui-core`, and `sui-execution/latest/sui-adapter`. Quote repository-relative paths and function/struct names. | 12 |
| src-2 | code_analysis | Primary Sui Framework Move evidence from `crates/sui-framework/packages/sui-framework/sources`, especially `pay.move`, `coin.move`, `balance.move`, `tx_context.move`, and `funds_accumulator.move`. | 5 |
| src-3 | official_docs | Official Sui documentation for sponsored transaction construction, transaction payment, address balances, payment intents, and payments overview. | 4 |
| src-4 | tests | Source test evidence validating sponsored transaction signing, gas owner mismatch rejection, address-balance/gasless behavior, and payment/gas edge cases. | 4 |
| src-5 | upstream_dependency | Reuse only as context from `sui-gasless-mechanism/final.md`; do not duplicate its broad gasless mechanism findings unless needed to explain this code-level topic. | 1 |
| src-6 | sdk_api | SDK/API examples for `setGasOwner`, `setGasPayment`, `setGasBudget`, `build`, `signTransaction`, and `executeTransaction`, preferably official docs or SDK source. | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
