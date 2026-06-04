# Research Outline: Base B20 Token Standard Deep Analysis (Beryl Upgrade)

> **Project slug**: `compliance-token-standards`
> **Topic slug**: `base-b20-analysis`
> **Round**: 2
> **Codebase**: `base/base` at commit [`8e8767281d7c8768f6a0aed9124779cd4ed030ae`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)
> **Branch**: `research/compliance-token-standards/base-b20-analysis`
> **Date**: 2026-06-04

## Scope

Deep analysis of the B20 precompile token standard framework in the Base codebase, anchored at remote HEAD `8e87672`. B20 is a compliance-oriented token framework implemented as EVM precompiles, comprising a shared `IB20` capability layer, a Factory with deterministic address derivation, two production variants (Asset / Stablecoin), a PolicyRegistry for allowlist/blocklist enforcement, and an ActivationRegistry for hardfork-gated feature rollout. This analysis is based entirely on code; Base has not yet published a formal Beryl upgrade spec or public B20 standard document.

**Version disclaimer**: B20Security (`b20_security/`) exists only on a local branch ahead of remote HEAD. It is documented as an evolutionary signal, not current mainline fact.

---

## Section 1: B20 Architecture Overview

> **Goal**: Establish the overall system architecture — modules, their relationships, the capability-trait composition pattern, and how the Beryl hardfork activates the B20 subsystem.

### 1.1 System-Level Module Map

- **Investigation fields**:
  - Enumerate all B20-related crate paths and their responsibilities
  - Map the module dependency graph: common -> b20_factory -> {b20_asset, b20_stablecoin} -> policy -> activation
  - Identify the precompile registration and address scheme
  - Document the Beryl activation sequence (ActivationRegistry -> feature gates)
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/common/mod.rs` — public re-exports, module structure
  - `crates/common/precompiles/src/b20_factory/variant.rs` — B20Variant enum, address prefix `0xb2`
  - `crates/common/precompiles/src/activation/storage.rs` — ActivationFeature enum (PolicyRegistry, B20Asset, B20Stablecoin)
  - `crates/common/precompiles/src/activation/abi.rs` — IActivationRegistry interface
  - `actions/harness/tests/beryl/activation.rs` — activation lifecycle test

### 1.2 Capability-Trait Composition Pattern

- **Investigation fields**:
  - Document the `Token` trait as the central bridge (associated types: `Accounting`, `Policy`)
  - List all 8 capability traits: Transferable, Mintable, Burnable, RoleManaged, Pausable, Configurable, Permittable, B20Guards
  - Explain monomorphic resolution via associated types (zero vtable overhead)
  - Explain the `privileged` flag pattern for factory-initialization bypass
  - Document how each variant opts in by implementing traits with empty bodies
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/common/token.rs` — Token trait definition
  - `crates/common/precompiles/src/common/token_accounting.rs` — TokenAccounting port (30 methods)
  - `crates/common/precompiles/src/common/ops/mod.rs` — capability trait exports
  - `crates/common/precompiles/src/b20_asset/token.rs` — B20AssetToken implementing all traits
  - `crates/common/precompiles/src/b20_stablecoin/token.rs` — B20StablecoinToken implementing all traits

### 1.3 B20Variant Address Encoding

- **Investigation fields**:
  - Document the address format: `[0xb2][9 zero bytes][discriminant byte][9 hash bytes]`
  - Discriminants: Asset=0, Stablecoin=1
  - Deterministic derivation: `keccak256(abi_encode(creator, salt))` -> tail bytes
  - Factory singleton address: `0xB20F000000000000000000000000000000000000`
  - `has_b20_prefix()` vs `is_b20_address()` distinction
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/b20_factory/variant.rs` — full encoding logic, `compute_address()`

---

## Section 2: Shared IB20 Interface & Common Capability Layer

> **Goal**: Document the complete shared interface that all B20 variants inherit, including ERC-20 compatibility, RBAC, policy binding, pause mechanism, permit, memo, supply cap, and contract URI.

### 2.1 IB20 Solidity Interface

- **Investigation fields**:
  - Complete function inventory (44 functions) organized by category
  - All events (17 events) with indexed parameters and semantics
  - All errors (19 error types) with trigger conditions
  - PausableFeature enum: TRANSFER=0, MINT=1, BURN=2
  - ERC compatibility markers: ERC-20, EIP-2612, ERC-5267, ERC-7572
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/common/abi.rs` — complete `sol!` macro expansion

### 2.2 B20CoreStorage Layout

- **Investigation fields**:
  - ERC-7201 namespace: `base.b20`
  - 14 storage slots: metadata (name, symbol, contract_uri), accounting (total_supply, balances, allowances), RBAC (roles, role_admins, admin_count), policies (packed u64 IDs in slots 9-10), pause bitmask, supply_cap, nonces
  - Policy packing: 4 policy IDs in 2 U256 slots (transfer_sender, transfer_receiver, transfer_executor + reserved, mint_receiver + reserved)
  - Admin lifecycle tracking via `admin_count`
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/common/core_storage.rs` — B20CoreStorage struct

### 2.3 RBAC System

- **Investigation fields**:
  - 7 role constants: DEFAULT_ADMIN_ROLE (B256::ZERO), MINT_ROLE, BURN_ROLE, BURN_BLOCKED_ROLE, PAUSE_ROLE, UNPAUSE_ROLE, METADATA_ROLE
  - Grant/revoke mechanics with admin-role hierarchy
  - Terminal admin state: `renounceLastAdmin()` — permanent, freezes all role mutations
  - Guard ordering: pause -> role -> policy -> invariant
  - Admin count tracking for last-admin protection
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/common/ops/roles.rs` — RoleManaged trait, role constants
  - `crates/common/precompiles/src/common/ops/guards.rs` — B20Guards helper methods

### 2.4 ERC-20 + Memo + Permit

- **Investigation fields**:
  - Standard ERC-20: transfer, approve, transferFrom
  - 32-byte memo extension: transferWithMemo, transferFromWithMemo, mintWithMemo, burnWithMemo
  - EIP-2612 permit: secp256k1 recovery, nonce management, deadline enforcement
  - EIP-712 domain: live name hash (name updates invalidate outstanding permits), version="1"
  - ERC-5267 eip712Domain return tuple
  - `U256::MAX` allowance (infinite approval, no decrement)
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/common/ops/transferable.rs` — Transferable trait
  - `crates/common/precompiles/src/common/ops/mintable.rs` — Mintable trait
  - `crates/common/precompiles/src/common/ops/burnable.rs` — Burnable trait (including burnBlocked)
  - `crates/common/precompiles/src/common/ops/permittable.rs` — Permittable trait, PermitArgs

### 2.5 Pausable & Configurable Features

- **Investigation fields**:
  - Feature-level bitmask: TRANSFER | MINT | BURN
  - Pause semantics: always enforced even when `privileged=true` (except in internal methods)
  - Idempotent pause/unpause (OR/AND bitmask operations)
  - Configurable: updateSupplyCap (admin-only, rejects if cap < current supply), updateName (invalidates permits), updateSymbol, updateContractURI (ERC-7572)
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/common/ops/pausable.rs` — Pausable trait
  - `crates/common/precompiles/src/common/pausable_feature.rs` — bitmask helpers
  - `crates/common/precompiles/src/common/ops/configurable.rs` — Configurable trait

---

## Section 3: B20Factory

> **Goal**: Document the Factory's creation flow, variant management, initialization sequence, and ActivationRegistry integration.

### 3.1 createB20 Lifecycle

- **Investigation fields**:
  - Full 10-step creation flow: compute address -> check activation -> decode params -> validate -> check duplicate -> deploy stub (0xef) -> initialize variant -> emit B20Created -> grant initial admin -> execute initCalls
  - Variant-specific params: B20AssetCreateParams (version, name, symbol, initialAdmin, decimals), B20StablecoinCreateParams (version, name, symbol, initialAdmin, currency)
  - Version gating: `check_version()` per variant (currently version=1 for both)
  - Post-creation initCalls: executed as factory address with privilege; errors wrapped as InitCallFailed(index)
  - Supply cap default: U256::MAX
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/b20_factory/precompile.rs` — create_b20, init_stablecoin, init_asset_token
  - `crates/common/precompiles/src/b20_factory/storage.rs` — TokenCreateParams, CommonParams
  - `crates/common/precompiles/src/b20_factory/abi.rs` — IB20Factory interface, params structs, events

### 3.2 Deterministic Address & Variant Identification

- **Investigation fields**:
  - getB20Address(variant, sender, salt) -> deterministic address (never reverts)
  - isB20(token) -> checks structural prefix (includes reserved discriminants)
  - isB20Initialized(token) -> checks factory deployment state
  - Address encoding: prefix + discriminant + keccak256 tail
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/b20_factory/variant.rs` — compute_address, has_b20_prefix, from_address
  - `crates/common/precompiles/src/b20_factory/dispatch.rs` — view function routing

### 3.3 ActivationRegistry Integration

- **Investigation fields**:
  - Singleton precompile at `0x8453000000000000000000000000000000000001`
  - Feature IDs: keccak256 of feature name strings (PolicyRegistry, B20Asset, B20Stablecoin)
  - Lifecycle: inactive (default) -> activate -> deactivate (idempotent transitions revert)
  - Admin-gated mutations, view functions always accessible
  - Integration with Factory: `ensure_activated()` gate on create_b20
  - Integration with PolicyRegistry: write operations require PolicyRegistry feature activation; view operations bypass
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/activation/` — all files (abi.rs, dispatch.rs, mod.rs, precompile.rs, storage.rs)

---

## Section 4: B20Asset Variant (Remote HEAD Mainline)

> **Goal**: Document the Asset variant's unique capabilities beyond the shared IB20 layer.

### 4.1 Multiplier Mechanism

- **Investigation fields**:
  - WAD_PRECISION = 1e18 fixed-point base
  - Read-time scaling: `toScaledBalance(raw) = raw * multiplier / WAD`; `toRawBalance(scaled) = scaled * WAD / multiplier`
  - `scaledBalanceOf(account)` = convenience wrapper
  - Multiplier does NOT rewrite storage balances — purely a read-time view transformation
  - Initial multiplier: U256::ZERO (Factory sets to zero at creation, meaning 1:1 at WAD)
  - updateMultiplier: requires OPERATOR_ROLE, emits MultiplierUpdated
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/b20_asset/token.rs` — to_scaled_balance, to_raw_balance, update_multiplier
  - `crates/common/precompiles/src/b20_asset/storage.rs` — WAD constant, multiplier storage slot
  - `crates/common/precompiles/src/b20_asset/abi.rs` — IB20Asset interface

### 4.2 Batch Issuance (batchMint)

- **Investigation fields**:
  - All-or-nothing semantics: atomic rollback on any individual mint failure
  - Guard ordering: pause check -> MINT_ROLE check -> input validation (length match, non-empty) -> per-recipient mint with `privileged=true` (skip redundant role checks)
  - LengthMismatch / EmptyBatch errors
  - No batch size cap in the code (but gas-limited in practice)
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/b20_asset/dispatch.rs` — batch_mint handler
  - `crates/common/precompiles/src/b20_asset/token.rs` — batch_mint implementation

### 4.3 Announcement Mechanism

- **Investigation fields**:
  - `announce(internalCalls, id, description, uri)`: posts holder-impacting notification
  - Requires OPERATOR_ROLE
  - Single-use IDs: checked via `is_announcement_id_used`, marked before internal calls
  - Atomic internal call execution: each call dispatched through inner_with_privilege; failures wrapped as InternalCallFailed
  - Reentrancy guard: `in_announcement` flag + selector check prevents recursive announce()
  - Event pair: Announcement (start) + EndAnnouncement (end) for on-chain bracketing
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/b20_asset/dispatch.rs` — announce handler (line ~420)
  - `crates/common/precompiles/src/b20_asset/abi.rs` — Announcement / EndAnnouncement events

### 4.4 Extra Metadata & Role Model

- **Investigation fields**:
  - `extraMetadata(key)` / `updateExtraMetadata(key, value)`: arbitrary KV store
  - Empty key rejected (InvalidMetadataKey); empty value removes entry
  - Requires METADATA_ROLE
  - Asset-specific roles: OPERATOR_ROLE (announce, updateMultiplier), METADATA_ROLE (updateExtraMetadata)
  - Storage: ERC-7201 namespace `base.b20.asset` with slots for decimals, multiplier, used_announcement_ids, extra_metadata
  - Custom decimals: 6-18 range, stored once at creation, defaults to 6
  - **Securities-identifier use case**: The Beryl test file `security.rs` creates a `B20Variant::ASSET` token and uses `extraMetadata` to store securities identifiers (ISIN, CUSIP, FIGI) — demonstrating that the Asset variant's KV metadata mechanism natively supports securities-identifier workflows without requiring a separate B20Security variant. The test also exercises `updateMultiplier`, `batchMint`, and `announce` in a securities context.
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/b20_asset/token.rs` — update_extra_metadata, role constants
  - `crates/common/precompiles/src/b20_asset/storage.rs` — B20AssetExtensionStorage, MIN/MAX_DECIMALS
  - `actions/harness/tests/beryl/security.rs` — B20Asset securities-identifier use-case tests (imports `IB20Asset`, creates `B20Variant::ASSET`; uses ISIN/CUSIP/FIGI as `extraMetadata` keys)

---

## Section 5: B20Security Evolutionary Signal (Non-Mainline)

> **Goal**: Document the security token capabilities observed on the local branch as an evolutionary signal. Clearly mark as non-mainline.

### 5.1 Security Token Extensions

- **Investigation fields**:
  - Variant identification: was `b20_asset/` renamed to `b20_security/` on the local branch?
  - New roles: SECURITY_OPERATOR_ROLE, BURN_FROM_ROLE
  - New policy scope: REDEEM_SENDER_POLICY
  - sharesToTokensRatio: replaces multiplier concept
  - `redeem` / `redeemWithMemo`: holder-initiated redemption with minimum threshold
  - `batchBurn`: forced burn / clawback capability
  - `securityIdentifier`: dedicated securities metadata field (distinct from the `extraMetadata` KV store used for ISIN/CUSIP/FIGI at remote HEAD — see Section 4.4)
  - Comparison with B20Asset: what was added, what was renamed, what was removed
- **Sources**:
  - Local HEAD only (not at remote `8e87672`) — label all citations as "local branch observation"
  - `crates/common/precompiles/src/b20_security/` (local branch) — the `b20_security` module directory does not exist at remote HEAD `8e87672`; analysis requires local clone at the ahead-of-remote commit

> **Caveat**: This section must be explicitly labeled as "evolutionary signal, not current BASE mainline." Do not attribute redeem, batchBurn, or securityIdentifier to the verified remote HEAD capabilities. Note: `actions/harness/tests/beryl/security.rs` at remote HEAD is NOT a B20Security test — it tests B20Asset securities use cases via `extraMetadata` (see Section 4.4).

---

## Section 6: B20Stablecoin Variant

> **Goal**: Document the Stablecoin variant's minimal extension over the shared IB20 layer.

### 6.1 Currency Identifier Extension

- **Investigation fields**:
  - Single extension method: `currency()` returning a string
  - Currency validation: non-empty, A-Z uppercase only (ISO 4217 style)
  - Errors: MissingRequiredField (empty currency), InvalidCurrency (non-A-Z)
  - B20Created event: variantParams encodes `B20StablecoinEventParams(version=1, currency)`
  - Storage: ERC-7201 namespace `base.b20.stablecoin`, single String slot
  - Default decimals: 6 (same as Asset variant)
  - All other capabilities inherited from shared IB20 layer
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/b20_stablecoin/abi.rs` — IB20Stablecoin interface
  - `crates/common/precompiles/src/b20_stablecoin/storage.rs` — B20StablecoinExtensionStorage, init validation
  - `crates/common/precompiles/src/b20_stablecoin/token.rs` — B20StablecoinToken
  - `actions/harness/tests/beryl/stablecoin.rs` — stablecoin creation + currency validation tests

---

## Section 7: PolicyRegistry Compliance Mechanism

> **Goal**: Document the PolicyRegistry as the central compliance engine — types, scopes, CRUD, and integration with B20 tokens.

### 7.1 Policy Types & Built-in Policies

- **Investigation fields**:
  - PolicyType enum: BLOCKLIST (discriminant 0), ALLOWLIST (discriminant 1)
  - BLOCKLIST semantics: denies only listed accounts; empty blocklist authorizes everyone
  - ALLOWLIST semantics: permits only listed accounts; empty allowlist denies everyone
  - Built-in policies: ALWAYS_ALLOW (ID=0x0, BLOCKLIST with counter=0), ALWAYS_BLOCK (ID=0x01_00000000000001, ALLOWLIST with counter=1)
  - Policy ID encoding: high byte = type discriminant, low 56 bits = monotonic counter
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/policy/storage.rs` — PolicyRegistryStorage, PackedPolicy, built-in IDs
  - `crates/common/precompiles/src/policy/abi.rs` — IPolicyRegistry interface

### 7.2 Four-Dimensional Policy Scope

- **Investigation fields**:
  - TransferSender: checked against `from` address on transfer
  - TransferReceiver: checked against `to` address on transfer
  - TransferExecutor: checked against `spender` on transferFrom (skipped when spender==from)
  - MintReceiver: checked against `to` address on mint
  - Each scope bound independently per token via `updatePolicy(scope, policyId)`
  - Guard enforcement in capability traits: ensure_policy_type called at appropriate points
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/common/policy_type.rs` — B20PolicyType enum with B256 IDs
  - `crates/common/precompiles/src/common/ops/transferable.rs` — policy checks in transfer/transferFrom
  - `crates/common/precompiles/src/common/ops/mintable.rs` — mint-receiver policy check
  - `crates/common/precompiles/src/common/ops/burnable.rs` — blocked account check for burnBlocked

### 7.3 Policy CRUD & Admin Management

- **Investigation fields**:
  - createPolicy / createPolicyWithAccounts: admin assignment, counter increment, type validation
  - updateAllowlist / updateBlocklist: type-checked (ALLOWLIST ops reject BLOCKLIST policies, vice versa), 64-account batch limit
  - Two-step admin transfer: stageUpdateAdmin -> finalizeUpdateAdmin (prevents accidental lockout)
  - renounceAdmin: permanent, zeroes admin field
  - Storage: ERC-7201 namespace `base.policy_registry` (policies mapping, members mapping, pending_admins, next_counter)
  - Events: PolicyCreated, PolicyAdminStaged, PolicyAdminUpdated, AllowlistUpdated, BlocklistUpdated
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/policy/storage.rs` — full CRUD implementation
  - `crates/common/precompiles/src/policy/handle.rs` — PolicyHandle wrapper
  - `crates/common/precompiles/src/policy/dispatch.rs` — activation gate (mutations require feature)
  - `actions/harness/tests/beryl/policy_registry.rs` — policy lifecycle tests

### 7.4 Token-Policy Integration

- **Investigation fields**:
  - Token stores 4 policy IDs in core storage (packed into 2 U256 slots)
  - updatePolicy requires DEFAULT_ADMIN_ROLE
  - Policy checks delegated to external PolicyRegistry via Policy trait
  - Graceful degradation: never-created BLOCKLIST IDs return `is_authorized = true`
  - burnBlocked: requires account to be blocked by transfer-sender policy
- **Sources** (`base/base` @ `8e87672`):
  - `crates/common/precompiles/src/common/policy.rs` — Policy trait (read-only port)
  - `crates/common/precompiles/src/common/ops/guards.rs` — ensure_policy, ensure_blocked
  - `actions/harness/tests/beryl/b20_policy.rs` — token-level policy enforcement tests
  - `actions/harness/tests/beryl/policy_transfer.rs` — policy-gated transfer tests

---

## Section 8: Beryl Hardfork Test Suite & ZK Proving

> **Goal**: Document the test infrastructure, coverage, and ZK proving support for the B20 subsystem.

### 8.1 Test Suite Architecture

- **Investigation fields**:
  - BerylTestEnv: full L2 test environment with sequencer, L1 chain, batcher, rollup node
  - Beryl activation at L2 block height 2 (timestamp=4)
  - Test accounts: Alice, Bob, Carol with predefined balances/roles
  - Staticcall probe pattern: deploy EVM bytecode probes for read-only ABI validation
  - Block building + derivation verification pattern
  - 33 top-level `#[tokio::test]` functions across 8 test modules (some tests contain multiple sub-scenarios within a single function, e.g., the activation test covers 10 sub-tests)
- **Sources** (`base/base` @ `8e87672`):
  - `actions/harness/tests/beryl/env.rs` — BerylTestEnv setup (658 lines)
  - `actions/harness/tests/beryl/test_helpers.rs` — StaticcallCase, probe pattern
  - `actions/harness/tests/beryl/main.rs` — module declarations

### 8.2 Test Coverage Summary

- **Investigation fields**:
  - Activation: feature lifecycle (10 sub-tests)
  - Factory: creation, duplicate prevention, deactivation backward compat, views/events (4 tests)
  - B20 Asset: transfers, reverts, approval, staticcall ABI, deactivation compat, mutations, permit (8 tests)
  - B20 Policy: allowlist/blocklist sender/receiver enforcement (4 tests)
  - Stablecoin: currency init, inherited ops, deactivation compat, currency validation (4 tests)
  - Asset securities use-case (`security.rs`): identifiers via extraMetadata, mutations, invalid inputs, deactivation compat (4 tests)
  - Policy Registry: singleton lifecycle, policy CRUD + admin transfer (4 tests)
  - Policy Transfer: allowlist/blocklist gating, built-in policy behavior (4 tests)
  - Notable coverage gaps: no concurrent creation race tests, no large-batch batchMint tests, no scaled balance overflow edge cases
- **Sources** (`base/base` @ `8e87672`):
  - `actions/harness/tests/beryl/` — all test files

### 8.3 ZK Proving Benchmark

- **Investigation fields**:
  - Dry-run benchmark with 10-transaction workload
  - Workload: transfer, transferWithMemo, approve, transferFrom, transferFromWithMemo, updateSupplyCap, grantRole, updateContractURI, updateName, updateSymbol
  - Metrics: gas per operation, block number, proof generation cycles (min/max/avg/total)
  - Prover integration: external ZK prover service at configurable URL
  - Implications for B20 as ZK-provable precompile standard
- **Sources** (`base/base` @ `8e87672`):
  - `etc/systems/benches/b20_zk_proving.rs` — ZK bench (352 lines)
  - `etc/systems/src/b20.rs` — B20 system integration

---

## Section 9: TIP-20 Comparative Analysis

> **Goal**: Provide a structured preliminary comparison between B20 and TIP-20 token standards.

### 9.1 Shared Patterns

- **Investigation fields**:
  - Both use precompile-based implementation (not Solidity contracts)
  - Both use Factory pattern with deterministic address derivation
  - Both have Policy Registry / compliance mechanism
  - Both implement RBAC with role hierarchies
  - Both support 32-byte memo on transfers
  - Both have ERC-20 compatibility layer

### 9.2 B20-Unique Capabilities

- **Investigation fields**:
  - Asset variant with multiplier (read-time scaling)
  - Stablecoin variant with currency identifier
  - Announcement mechanism (holder-impacting notifications with atomic internal calls)
  - Extra metadata (arbitrary KV store)
  - ZK proving support (benchmark infrastructure)
  - ActivationRegistry for hardfork-gated rollout
  - burnBlocked (compliance-driven burn of blocked accounts)
  - ERC-7572 contractURI
  - Batch mint (all-or-nothing)

### 9.3 TIP-20-Unique Capabilities

- **Investigation fields**:
  - Payment Lanes
  - Fee AMM (automated market maker for fee calculation)
  - Rewards distribution mechanism
  - TIP-403 independent specification
  - [Requires cross-reference with TIP-20 analysis from WHI-177 evaluation framework]

### 9.4 Architectural Differences

- **Investigation fields**:
  - Capability composition: B20 uses Rust trait composition; TIP-20 approach TBD
  - Storage model: B20 uses ERC-7201 namespaced storage with packed policy slots
  - Policy model: B20 has 4-scope policy binding per token; compare with TIP-20 approach
  - Variant system: B20 uses discriminant-based variant enum; TIP-20 comparison TBD

---

## Diagram Plan

### Diagram 1: B20 Module Architecture

- **Type**: Block diagram
- **Content**: Show module hierarchy and data flow: ActivationRegistry -> B20Factory -> {B20AssetToken, B20StablecoinToken} -> common/IB20 capability traits -> PolicyRegistry
- **Purpose**: Provide visual map of the B20 subsystem for Section 1

### Diagram 2: Capability Trait Composition

- **Type**: Class diagram / trait hierarchy
- **Content**: Token trait at center with associated types (Accounting, Policy); 8 capability traits branching out; B20AssetToken and B20StablecoinToken implementing all traits; AssetAccounting extending TokenAccounting
- **Purpose**: Illustrate the composable architecture for Section 2

### Diagram 3: Token Creation Flow

- **Type**: Sequence diagram
- **Content**: Caller -> Factory.createB20 -> [validate] -> [compute address] -> [deploy stub] -> [initialize variant] -> [emit B20Created] -> [grant admin] -> [execute initCalls] -> return address
- **Purpose**: Illustrate the 10-step creation lifecycle for Section 3

### Diagram 4: Policy Enforcement Flow

- **Type**: Flowchart
- **Content**: Transfer call -> pause check -> sender policy check -> receiver policy check -> (if transferFrom) executor policy check -> allowance check -> balance check -> emit Transfer
- **Purpose**: Illustrate the guard ordering and 4-scope policy enforcement for Section 7

### Diagram 5: B20 vs TIP-20 Feature Matrix

- **Type**: Comparison table / matrix
- **Content**: Feature rows x Standard columns, marking shared/unique capabilities
- **Purpose**: Visual comparative summary for Section 9

---

## Source Requirements

### Primary Sources (Code)

All code citations must reference `base/base` at commit `8e8767281d7c8768f6a0aed9124779cd4ed030ae` unless explicitly marked as local-branch-only.

| Module | Path | Key Files |
|--------|------|-----------|
| Shared IB20 | `crates/common/precompiles/src/common/` | abi.rs, core_storage.rs, token.rs, token_accounting.rs, policy.rs, policy_type.rs, pausable_feature.rs, ops/*.rs |
| Factory | `crates/common/precompiles/src/b20_factory/` | abi.rs, precompile.rs, storage.rs, variant.rs, dispatch.rs |
| Asset | `crates/common/precompiles/src/b20_asset/` | abi.rs, token.rs, storage.rs, accounting.rs, dispatch.rs, precompile.rs |
| Stablecoin | `crates/common/precompiles/src/b20_stablecoin/` | abi.rs, token.rs, storage.rs, accounting.rs |
| Policy | `crates/common/precompiles/src/policy/` | abi.rs, storage.rs, handle.rs, dispatch.rs |
| Activation | `crates/common/precompiles/src/activation/` | abi.rs, storage.rs, precompile.rs |
| Beryl Tests | `actions/harness/tests/beryl/` | All 11 test files |
| ZK Bench | `etc/systems/benches/` | b20_zk_proving.rs |

### Secondary Sources

- `base/docs` repository (commit `bfff9ef27f2333ff57c3a62417f6c1f0174992f0`) — if public B20/Beryl docs exist
- ERC/EIP standards: ERC-20, EIP-2612, ERC-5267, ERC-7201, ERC-7572
- TIP-20 analysis from the compliance-token-standards project (WHI-177 evaluation framework)

### Source Integrity Notes

- Base has not published a formal Beryl upgrade spec or B20 standard document as of analysis date
- All findings are derived from code implementation; label accordingly as "implementation-based, pending formal spec"
- B20Security content is local-branch-only and must be labeled as "evolutionary signal"
- Commit hash `8e8767281d7c8768f6a0aed9124779cd4ed030ae` must be cited in all source references

---

## Quality Checklist

- [ ] Every section maps to a clear research question
- [ ] Investigation fields are specific and verifiable against source code
- [ ] Source paths include commit hash reference
- [ ] B20Security clearly marked as non-mainline throughout
- [ ] Diagram plan covers architecture, composition, creation flow, and compliance flow
- [ ] TIP-20 comparison structured for later cross-reference with evaluation framework
- [ ] No Linear/internal IDs used as slugs
- [ ] Outline is independently reviewable by adversarial agent
