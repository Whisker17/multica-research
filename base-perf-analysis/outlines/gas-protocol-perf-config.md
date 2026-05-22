---
topic: "Gas 参数与协议层性能配置三方对比"
project_slug: "base-perf-analysis"
topic_slug: "gas-protocol-perf-config"
github_repo: "Whisker17/multica-research"
round: 2
status: "candidate"
artifact_paths:
  outline: "base-perf-analysis/outlines/gas-protocol-perf-config.md"
  draft: "base-perf-analysis/research-sections/gas-protocol-perf-config/drafts/round-{n}.md"
  final: "base-perf-analysis/research-sections/gas-protocol-perf-config/final.md"
  index: "base-perf-analysis/research-sections/_index.md"
scope: "Compare protocol-layer gas and performance configuration across Base Rust stack, Mantle Go stack, and Mantle Rust/kona stack; quantify direct TPS ceilings from gas limit and block time; validate Mantle Go/Rust chain spec consistency; identify parameter-only quick wins and migration risks."
audience: "Mantle engineering and research stakeholders evaluating Base performance lessons, Mantle current-production tuning options, and Mantle Rust-stack migration compatibility."
expected_output: "A research section with three-way protocol parameter tables, theoretical TPS calculations for representative transaction mixes, quick-win priority matrix, safety-risk assessment, and Mantle Go/Rust configuration consistency report."
revision_metadata:
  created_by: "Deep Research Agent"
  created_at: "2026-05-22T11:19:08Z"
  last_modified_by: "Deep Research Agent"
  last_modified_at: "2026-05-22T11:31:47Z"
---

# Research Outline: Gas 参数与协议层性能配置三方对比

## Items

### item-1: Three-Stack Chain Spec Baseline

Establish the comparable configuration surfaces for Base Rust, Mantle Go, and Mantle Rust. This item should extract the source-of-truth files, chain IDs, genesis system config, block time, hardfork schedules, base-fee config pathways, and execution-client enforcement surfaces before any performance modeling is attempted. It should explicitly distinguish deploy-time genesis values from runtime `SystemConfig` values that may be changed by governance or L1 events, and it must record whether each observed value is currently active, scheduled, or unknown.

- **Priority**: high
- **Dependencies**: none

### item-2: Gas Limit, Target Gas, and EIP-1559 Parameter Comparison

Compare block gas limit, target gas, EIP-1559 elasticity, denominator, Canyon/Holocene/Jovian variants, minimum base fee, and any Mantle-specific base-fee or gas-config fields across the three stacks. The deep research should show both static configured values and live/current values where RPC or official chain data is available, with `activation_status`, `measurement_window`, and `source_date` recorded for every current-effective claim. It must identify which differences are performance-relevant versus purely fee-market or encoding differences.

- **Priority**: high
- **Dependencies**: item-1

### item-3: Block Time and Sequencing Timing Constraints

Compare configured L2 block time and related timing parameters such as sequencer drift, sequencing window, payload build budget, and derivation timestamp validation. The analysis should quantify the TPS effect of changing block time while documenting the engineering constraints that make shorter block time risky: execution headroom, propagation latency, batcher/derivation cadence, payload-builder filtering, and finality or reorg exposure.

- **Priority**: high
- **Dependencies**: item-1

### item-4: Per-Transaction Gas Caps and Protocol Guardrails

Investigate Base's EIP-7825-style per-transaction gas cap / Azul transaction gas limit behavior and compare whether Mantle Go or Mantle Rust has equivalent transaction admission, payload-building, state-transition rejection, or txpool guardrails. This item must use execution-client source code, not only rollup/genesis configs: for Mantle Go EL, inspect `mantlenetworkio/op-geth` paths `core/state_transition.go`, `core/txpool/validation.go`, `miner/worker.go`, and `params/protocol_params.go`; for Mantle Rust EL, inspect `mantle-xyz/reth` as a required source if available, otherwise explicitly classify Rust EL per-tx-cap behavior as out-of-scope/unknown and explain that `kona` alone is insufficient for execution-client enforcement claims. This item should also cover transaction-to-block packing efficiency, sequencer DoS protection, and whether a cap is a performance enabler, a safety control, or both, with `activation_status`, `measurement_window`, and `source_date` attached to any current enforcement claim.

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: Other Protocol-Layer Gas and Execution-Cost Parameters

Inventory protocol parameters beyond block gas limit that directly affect throughput, gas accounting, or execution safety: max init code size, max runtime code size, contract deployment cost rules, calldata/blob/scalar handling, DA footprint gas scalar, MODEXP/P256/BLS and other precompile gas costs, operator fee fields, min base fee, and hardfork upgrade transactions that mutate Gas Price Oracle or L1Block behavior. The output must trace execution-client enforcement paths for max init/code size and precompile gas schedules, including Mantle Go EL `op-geth` and Mantle Rust EL `reth` when available; if Rust EL code cannot be sourced, mark Rust EL execution behavior as `unknown` rather than inferring it from `kona` hardfork timestamps. The output should separate L2 throughput knobs from DA-pricing/batcher economics that are out of scope except where the same config field influences execution payloads.

- **Priority**: medium
- **Dependencies**: item-1

### item-6: Mantle Go vs Mantle Rust Configuration Consistency and Drift

Validate whether `mantlenetworkio/mantle-v2`, `mantle-xyz/kona`, and, where execution-layer behavior is in scope, `mantle-xyz/reth` represent the same Mantle chain spec and hardfork semantics. The comparison should map Go fields to Rust fields, including Mantle-specific hardfork timestamps, OP Stack hardfork alignment, EIP-1559 defaults, system config update decoders, AltDA and DA footprint parameters, hardfork upgrade transaction bundles, and execution-client protocol constants. Any missing field, divergent default, differently gated fork, repo-head-only behavior, or new Rust-only parameter must be classified as intentional, unknown, or migration risk; do not report Go/Rust alignment based only on fork timestamps or SystemConfig decoders when EL enforcement code is unavailable.

- **Priority**: high
- **Dependencies**: item-1, item-2, item-5

### item-7: TPS Modeling, Quick Wins, and Risk Matrix

Build a simple theoretical TPS model using gas-per-block divided by representative per-transaction gas, then adjust by block time and transaction mix. The analysis should model at minimum transfers, swaps, NFT mints, and contract deployments, plus scenario deltas for gas-limit increases and block-time reductions. It should rank recommendations by performance gain, implementation complexity, and safety risk, tagging each with `change_class`: `live_systemconfig_governance` (no code change, operator/governance action only), `sequencer_config_only` (sequencer restart/config change, no upgrade), `hardfork_client_upgrade` (coordinated hardfork or client binary change), or `contextual_out_of_scope_economics` (gas pricing/economic policy, not protocol config). The quick-wins section must keep "无需代码修改" recommendations (`live_systemconfig_governance` and `sequencer_config_only`) strictly separate from `hardfork_client_upgrade` items, and it must list prerequisites for Mantle to match or approach Base settings.

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4, item-5, item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| source_surface | Exact repo paths, config files, structs, generated genesis artifacts, RPC endpoints, or specs used as evidence. | all |
| parameter_name | Canonical parameter name plus aliases in Base Rust, Mantle Go, and Mantle Rust. | item-1, item-2, item-3, item-4, item-5, item-6 |
| base_rust_value | Value and source evidence for Base Rust stack. | item-1, item-2, item-3, item-4, item-5, item-7 |
| mantle_go_value | Value and source evidence for Mantle Go production stack. | item-1, item-2, item-3, item-4, item-5, item-6, item-7 |
| mantle_rust_value | Value and source evidence for Mantle Rust/kona stack. | item-1, item-2, item-3, item-4, item-5, item-6, item-7 |
| runtime_vs_static | Whether a value is genesis-static, rollup-config static, hardfork-gated, live SystemConfig, or governance-updatable. | item-1, item-2, item-3, item-5, item-6 |
| activation_status | Whether the value or enforcement path is active on the measured network, scheduled by a future fork/timestamp, or unknown. Required for live gas limit, base fee behavior, hardfork activation, and per-tx cap enforcement. | item-1, item-2, item-3, item-4, item-5, item-6, item-7 |
| measurement_window | Block range, date range, commit range, or explicit observation window used to characterize current values or behavior. Required for any current-effective parameter claim. | item-2, item-3, item-4, item-5, item-7 |
| source_date | Block number, block timestamp, repo commit date, spec date, or observation timestamp associated with the cited value. Required for live gas limit, base fee behavior, hardfork activation, and per-tx cap enforcement. | item-1, item-2, item-3, item-4, item-5, item-6, item-7 |
| enforcement_layer | Whether the parameter is enforced in rollup config, genesis/state, execution-client state transition, txpool admission, payload builder, precompile gas schedule, sequencer config, or governance-updated SystemConfig. | item-1, item-4, item-5, item-6, item-7 |
| performance_effect | Direct effect on TPS ceiling, block packing, payload build time, DoS resistance, or no direct TPS effect. | item-2, item-3, item-4, item-5, item-7 |
| alignment_status | For three-way or Mantle Go/Rust comparisons: aligned, divergent, absent, unknown, or not applicable. | item-1, item-2, item-3, item-4, item-5, item-6 |
| migration_risk | Compatibility risk if Mantle production config is migrated to the Rust stack, including consensus split, fee-market mismatch, replay/hash mismatch, or operational drift. | item-6, item-7 |
| tps_formula_inputs | Gas limit, target gas, block time, gas per transaction, and transaction mix assumptions used for calculations. | item-2, item-3, item-7 |
| quick_win_assessment | Benefit, prerequisite, required config change, complexity, risk, and rollback considerations for parameter-only improvements. | item-7 |
| change_class | Recommendation taxonomy: `live_systemconfig_governance`, `sequencer_config_only`, `hardfork_client_upgrade`, or `contextual_out_of_scope_economics`. Required for every item-7 recommendation, with no-code items separated from hardfork/client-upgrade items. | item-7 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Three-way protocol parameter matrix covering Base Rust, Mantle Go, and Mantle Rust for gas limit, block time, EIP-1559, hardfork gates, per-tx cap, and relevant gas-cost parameters. | mermaid | item-1, item-2, item-3, item-4, item-5, item-6 |
| diag-2 | comparison | TPS scenario table or curve showing baseline, gas-limit increase, block-time reduction, and combined scenarios for representative transaction mixes. | mermaid | item-7 |
| diag-3 | matrix | Benefit-vs-risk priority quadrant for recommendations, separating no-code quick wins (`live_systemconfig_governance`, `sequencer_config_only`) from `hardfork_client_upgrade` and `contextual_out_of_scope_economics` items. | mermaid | item-7 |
| diag-4 | flow | Mantle Go-to-Rust configuration consistency validation flow from source extraction through field mapping, default comparison, runtime override check, and migration-risk classification. | mermaid | item-6 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | Base Rust stack primary sources, especially `base/base` chain spec, genesis, hardfork, payload, and Azul/EIP-7825-related tests or implementation files. Candidate paths include `crates/common/chains/res/genesis/base.json`, `crates/common/genesis`, `crates/execution/chainspec`, `crates/execution/payload`, `etc/scripts/devnet/test-base-azul.sh`, and hardfork tests. | 5 |
| src-2 | code_analysis | Mantle Go production rollup/config primary sources, especially `mantlenetworkio/mantle-v2` chain spec, genesis builder, rollup config, system config update parsing, Mantle hardfork alignment, and relevant tests. Candidate paths include `op-chain-ops/genesis`, `op-node/rollup`, `op-node/rollup/derive/system_config.go`, `op-node/rollup/mantle_types.go`, and `op-core/forks/mantle_forks.go`. | 5 |
| src-3 | code_analysis | Mantle Rust/kona primary sources in `mantle-xyz/kona`, especially `crates/protocol/genesis` and `crates/protocol/hardforks` for config structs, system config updates, hardfork semantics, and upgrade transactions. | 5 |
| src-4 | code_analysis | Mantle Go execution-client primary sources in `mantlenetworkio/op-geth` for protocol guardrail enforcement. Required paths: `core/state_transition.go`, `core/txpool/validation.go`, `miner/worker.go`, and `params/protocol_params.go`. Use these to verify EIP-7825/per-tx caps, max init/code size, MODEXP/P256/BLS/precompile gas costs, txpool admission, state-transition rejection, and payload-builder filtering. | 4 |
| src-5 | code_analysis | Mantle Rust execution-client primary sources in `mantle-xyz/reth` for protocol guardrail enforcement. Required if available; if unavailable or not allowed in the workspace, explicitly mark Rust EL behavior as out-of-scope/unknown and avoid inferring txpool/state-transition/payload-builder behavior from `kona` alone. | 4 |
| src-6 | on_chain_data | Current Base and Mantle mainnet chain/RPC data for block gas limit, recent block timestamps, base fee behavior, hardfork activation, per-tx cap observability where practical, and SystemConfig-derived runtime values. Use official RPC endpoints or verified explorers and record block numbers/timestamps as `source_date` plus a block/date `measurement_window`. | 2 |
| src-7 | official_specs | EIP-1559, EIP-7825, OP Stack rollup/genesis/SystemConfig specifications, and OP hardfork specs relevant to Ecotone, Fjord, Granite, Holocene, Isthmus, Jovian, Interop, and Base Azul. | 4 |
| src-8 | official_docs | Base and Mantle official docs or release notes for mainnet parameters, upgrade activation, or protocol-parameter rationale, with publication or capture dates recorded. | 2 |
| src-9 | calculations | Transparent TPS calculation sheet/table in the draft showing formulas, assumptions, sensitivity cases, activation status, and source-date metadata for all inputs; all inputs must cite a primary source or be explicitly labeled as modeling assumptions. | 1 |

## Change Class Taxonomy

| change_class | Definition | Quick-Win Handling |
|--------------|------------|--------------------|
| live_systemconfig_governance | Runtime `SystemConfig` or governance/operator action with no client code change. | Eligible for "无需代码修改" quick-win list if safety prerequisites are met. |
| sequencer_config_only | Sequencer or operator config change that may require restart/redeploy but no protocol upgrade or client binary change. | Eligible for "无需代码修改" quick-win list if rollback path and monitoring are defined. |
| hardfork_client_upgrade | Requires coordinated hardfork, execution/rollup client binary change, or protocol-constant change. | Must be listed separately from no-code quick wins as an upgrade-gated recommendation. |
| contextual_out_of_scope_economics | Gas pricing or economic-policy change that does not directly alter protocol performance configuration. | Mention only as context; do not count as protocol-config quick win. |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | Revised outline | item-1, item-2, item-3, item-4, item-5, item-6, item-7, Fields, Source Requirements, Change Class Taxonomy | Add execution-client enforcement sources, current-vs-scheduled gating metadata, and quick-win change taxonomy requested by outline review. | Orchestrator Revision Request `37b5449c-4753-4e24-ba94-c6d88de0d3c5` |
