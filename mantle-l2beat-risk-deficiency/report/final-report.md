# Mantle L2Beat Risk Chart Deficiency Analysis: Final Report

**Project**: mantle-l2beat-risk-deficiency
**Date**: 2026-05-21
**Status**: Final
**Synthesized from**: WHI-49, WHI-50, WHI-51, WHI-52

---

## Executive Summary

Mantle currently displays **red** on both the **Proposer Failure** and **Exit Window** dimensions of the L2Beat Risk Chart. This report synthesizes four independent research sections to present a unified root-cause analysis and an internally consistent remediation package.

**Core findings:**

1. **Both red ratings are template-driven, not chain-parameter-derived.** L2Beat's OP Stack template hardcodes `OpSuccinct` to `PROPOSER_CANNOT_WITHDRAW` (red) without reading any chain fields, and hardcodes `upgradeDelay = 0` yielding `EXIT_WINDOW(0, finalizationPeriod) = None` (red). Neither rating can be changed by on-chain parameter adjustments alone; the template or a `nonTemplateRiskView` override must also change.
   *(Source: [WHI-49](mention://issue/2e44db1f-a572-47a4-b25e-ea1e2f0fa358), `opStack.ts` L1400 and L1438-1440)*

2. **Proposer Failure is red because no deployed user self-help path exists.** The `OPSuccinctL2OutputOracle` v2.0.1 checks proposer authorization *before* proof verification. A valid SP1 proof from an unauthorized caller is rejected at the L1 boundary. `fallbackTimeout()` reverts on the deployed ABI. `approvedProposers(address(0))` is `false`. Users cannot independently obtain a withdrawable output root during proposer outage.
   *(Source: [WHI-50](mention://issue/b36ff7b9-d4e7-4f8a-99c4-6c4708b4686c), Sourcify-verified oracle source + live reads at block 25143121)*

3. **Exit Window is red because the core rollup upgrade path has zero delay.** ProxyAdmin is owned by a 6/14 Safe multisig (`0x4e59...D40f`) with no timelock interposition. The effective exit window is `0 - 43200s = -0.5d`, displayed as "None." A 7-day timelock would still be insufficient: with `exitDelay = 0.5d`, the minimum non-red `upgradeDelay` is **7.5 days**.
   *(Source: [WHI-51](mention://issue/de290023-0bae-4540-8cae-a194649e19b3), `riskView.ts` L642-687 + on-chain reads)*

4. **The two dimensions are coupled and must be remediated together.** Fixing only Proposer Failure leaves users exposed to instant upgrades; fixing only Exit Window leaves users unable to exit during proposer outage. The cross-dimension invariant is: `fallbackTimeout <= effectiveExitWindow - safetyMargin`.
   *(Source: [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766))*

5. **The minimum credible Phase 1 package** is a 10-day regular timelock with 12h exitDelay and `fallbackTimeout <= 7d`, giving a 9.5-day effective exit window with >= 2.5 days of margin after fallback activation. The stronger Phase 2 target is a 31-day timelock with tightly bounded emergency powers. A 14-day fallback with a 10-day timelock is **explicitly excluded** as minimum-pass because the fallback would activate after the exit window expires.
   *(Source: [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766))*

---

## 1. L2Beat Risk Chart Assessment Mechanism

### 1.1 How Risk Chart Ratings Are Determined

The L2Beat Risk Chart evaluates rollups across five dimensions: State Validation, Data Availability, Sequencer Failure, Proposer Failure, and Exit Window. Each dimension produces a sentiment (good/warning/bad) with an associated description and color.

Risk Chart sentiment is determined **entirely** by `packages/config/src/common/riskView.ts` constants/functions and per-stack template logic. It operates independently from the L2Beat Stage 1/2 framework -- the Stage framework's thresholds (e.g., Exit Window >= 5d) do **not** enter Risk Chart sentiment determination, even where numerical values coincide.
*(Source: [WHI-49](mention://issue/2e44db1f-a572-47a4-b25e-ea1e2f0fa358), `riskView.ts` + [Forum: Risk Rosette Framework](https://forum.l2beat.com/t/the-risk-rosette-framework/292))*

**Three-layer data priority** governs which value appears on the Risk Chart:

| Priority | Source | Mechanism |
|---|---|---|
| 1 (highest) | `nonTemplateRiskView.*` | Project-specific PR override; always wins |
| 2 | Template judgment functions | `getRiskViewProposerFailure()`, `getRiskViewExitWindow()`, etc. |
| 3 (lowest) | Template constants | Direct `RISK_VIEW.*` constant references |

For Mantle, both Proposer Failure and Exit Window fall through to **priority 2** (template functions) because no `nonTemplateRiskView` overrides exist. The template functions then produce hardcoded red outcomes without reading chain state.
*(Source: [WHI-49](mention://issue/2e44db1f-a572-47a4-b25e-ea1e2f0fa358), `opStack.ts` L1285-1287)*

### 1.2 Proposer Failure Assessment Criteria

L2Beat's Proposer Failure dimension answers: *"When the proposer stops, can users independently withdraw L2 assets?"*

The `RISK_VIEW.PROPOSER_*` family in `riskView.ts` L516-640 defines 13 possible outcomes spanning four categories:

| Category | Sentiment | Examples |
|---|---|---|
| Whitelist freeze (no fallback) | bad (red) | `PROPOSER_CANNOT_WITHDRAW` |
| Governance/SC can replace proposer | warning (yellow) | `PROPOSER_WHITELIST_GOVERNANCE`, `PROPOSER_WHITELIST_SECURITY_COUNCIL` |
| Permissionless self-propose after delay | good (green) | `PROPOSER_SELF_PROPOSE_WHITELIST_DROPPED(delay)`, `PROPOSER_SELF_PROPOSE_ROOTS` |
| Escape hatch (user exits independently) | good (green) | `PROPOSER_USE_ESCAPE_HATCH_ZK`, `PROPOSER_USE_ESCAPE_HATCH_MP` |

The Risk Rosette Framework explicitly defines: red = "Proposing state roots is fully centralized"; green = "Users can self-propose state roots permissionlessly" or escape hatch.
*(Source: [WHI-49](mention://issue/2e44db1f-a572-47a4-b25e-ea1e2f0fa358), `riskView.ts` L516-640 at commit `c4d9593`)*

### 1.3 Exit Window Assessment Criteria

L2Beat's Exit Window dimension answers: *"After a non-emergency upgrade is initiated, do users have enough time to exit?"*

The core formula is:

```
effectiveExitWindow = upgradeDelay - exitDelay
```

Where `exitDelay` is the time users need to complete withdrawal after deciding to exit (typically `finalizationPeriodSeconds`).

| Effective Window | Sentiment |
|---|---|
| < 7 days | bad (red) |
| 7-30 days | warning (yellow) |
| >= 30 days | good (green) |
| <= 0 | Displayed as "None" (bad) |

The `withRegularExitWindow` pattern (used by Arbitrum, OP Mainnet) shows a regular/emergency split where the primary sentiment reflects the emergency path. A non-zero regular subfield does **not** change the primary Risk Chart color.
*(Source: [WHI-49](mention://issue/2e44db1f-a572-47a4-b25e-ea1e2f0fa358), `riskView.ts` L642-687)*

---

## 2. Mantle Proposer Failure Root Cause

### 2.1 L2Beat Code Path

Mantle is declared via `opStackL2({...})` at `mantle.ts:14`. When L2Beat's discovery finds `OPSuccinctL2OutputOracle`, `getFraudProofType()` returns `'OpSuccinct'` (`opStack.ts:2360-2368`). The template function `getRiskViewProposerFailure()` then maps both `'OpSuccinct'` and `'OpSuccinctFDP'` directly to `RISK_VIEW.PROPOSER_CANNOT_WITHDRAW` (`opStack.ts:1438-1440`).

**No chain field is read in this path.** The `proposer` address, `approvedProposers(address(0))`, and `fallbackTimeout` values are irrelevant to the template's decision -- it returns red unconditionally for any `OpSuccinct`-typed project.
*(Source: [WHI-49](mention://issue/2e44db1f-a572-47a4-b25e-ea1e2f0fa358) SS2.2.3, [WHI-50](mention://issue/b36ff7b9-d4e7-4f8a-99c4-6c4708b4686c))*

### 2.2 Deployed Contract Evidence

The deployed `OPSuccinctL2OutputOracle` at proxy `0x31d543e7BE1dA6eFDc2206Ef7822879045B9f481` (implementation `0x4059...f50`, Sourcify full match, version 2.0.1) confirms no user self-help path exists:

| Property | Value | Implication |
|---|---|---|
| `optimisticMode` | `false` | Proofs required |
| `approvedProposers(initialProposer)` | `true` | Single approved proposer `0x6667...d77d` |
| `approvedProposers(address(0))` | `false` | No permissionless flag |
| `fallbackTimeout()` | Reverts | Getter absent in deployed ABI |
| `additionalProposers` | `[]` | No additional proposers |

The `proposeL2Output` non-optimistic path checks `approvedProposers[msg.sender] || approvedProposers[address(0)]` at source line 318-322 **before** calling `ISP1Verifier.verifyProof()` at line 350. A valid SP1 proof from an unauthorized caller is rejected at the authorization boundary.
*(Source: [WHI-50](mention://issue/b36ff7b9-d4e7-4f8a-99c4-6c4708b4686c), Sourcify source + live reads at block 25143121)*

### 2.3 Why Morph Passes with SP1

Morph is the primary counterexample. It uses SP1 as a ZK fault-proof mechanism but passes Proposer Failure with `PROPOSER_SELF_PROPOSE_WHITELIST_DROPPED(604800)` (green). The critical difference:

- Morph is modeled as a standalone project (not `opStackL2`)
- Morph's `Rollup.sol` contains `commitBatchWithProof()` (L383-430): an **external function without `onlyActiveStaker` modifier** that becomes callable permissionlessly after `rollupDelayPeriod = 604800s` (7 days)
- This function calls `_verifyProof()` → `IRollupVerifier.verifyAggregateProof()`, providing a real ZK-proof-backed user self-help path

Mantle's architecture lacks an equivalent: `proposeL2Output` gates authorization before proof verification, and no alternate public entry point exists.
*(Source: [WHI-50](mention://issue/b36ff7b9-d4e7-4f8a-99c4-6c4708b4686c), `morph.ts:195-201`, `Rollup.sol:383-430`)*

### 2.4 Withdrawal Impact Under Proposer Outage

| User State | Effect |
|---|---|
| Withdrawal covered by already-accepted output | Can still prove/finalize normally |
| Withdrawal after last accepted output | Cannot prove -- no new state roots available |
| Combined with Exit Window "None" | Assets **permanently unrecoverable** if SC also fails |

*(Source: [WHI-49](mention://issue/2e44db1f-a572-47a4-b25e-ea1e2f0fa358) SS2.2.7, [WHI-50](mention://issue/b36ff7b9-d4e7-4f8a-99c4-6c4708b4686c))*

---

## 3. Mantle Exit Window Root Cause

### 3.1 L2Beat Code Path

Mantle's project config (`mantle.ts`) does not set `nonTemplateRiskView.exitWindow`. The OP Stack template function `getRiskViewExitWindow()` (`opStack.ts:1387-1401`) hardcodes `upgradeDelay = 0` and calls `RISK_VIEW.EXIT_WINDOW(0, finalizationPeriod)`. With Mantle's `finalizationPeriodSeconds = 43200` (12 hours):

```
effectiveExitWindow = 0 - 43200 = -43200s = -0.5 days
```

This renders as "None" with sentiment "bad."
*(Source: [WHI-51](mention://issue/de290023-0bae-4540-8cae-a194649e19b3), `opStack.ts` L1400)*

### 3.2 On-Chain Upgrade Path Analysis

The core rollup upgrade path is controlled by multisigs with zero delay:

| Contract | Role | Controller | Delay |
|---|---|---|---|
| ProxyAdmin `0xca35...7794` | Upgrade all proxies | MantleSecurityMultisig `0x4e59...D40f` (6/14 Safe) | 0 |
| `OPSuccinctL2OutputOracle.owner` | Configure proposers, verifier, finalization period, optimistic mode | MantleSecurityMultisig | 0 |
| `OPSuccinctL2OutputOracle.challenger` | Delete outputs | MantleEngineeringMultisig `0x2F44...daC9` (3/7 Safe) | 0 |
| `OptimismPortal.GUARDIAN` | Pause portal | MantleEngineeringMultisig | 0 |

The instant-upgrade path is: MantleSecurityMultisig -> ProxyAdmin -> upgrade any proxy implementation. This means the multisig can unilaterally change oracle, portal, bridge, and messenger implementations without notice.

The existing L1 MNT TimelockController (`0x6533...447F`, `minDelay = 86400s / 1 day`) governs only the MNT token, **not** core rollup contracts.
*(Source: [WHI-51](mention://issue/de290023-0bae-4540-8cae-a194649e19b3))*

### 3.3 Arithmetic Gap to Non-Red

| Target | Required `upgradeDelay` (with `exitDelay = 0.5d`) |
|---|---|
| Non-red minimum (effective >= 7d) | **7.5 days** (648,000s) |
| Warning upper bound (effective >= 30d) | **30.5 days** (2,635,200s) |

A 7-day timelock yields only 6.5 days effective window -- **still red**. This is a common miscalculation that the research explicitly flags.
*(Source: [WHI-51](mention://issue/de290023-0bae-4540-8cae-a194649e19b3))*

### 3.4 Comparator Analysis

| Project | Exit Window Primary | Regular Subfield | Lesson |
|---|---|---|---|
| **Arbitrum One** | None / bad | ~10d (warning) | Regular subfield does NOT change primary red |
| **OP Mainnet** | None / bad | N/A | SC instant upgrade => red even with mature governance |
| **Polygon Hermez** (archived) | 7d / warning | N/A | Proves the arithmetic: `upgradeDelay=7d, exitDelay=0` => 7d |

[TW inference] All major OP Stack and Orbit rollups currently show red Exit Window on the primary sentiment. Mantle's path to non-red Exit Window would make it an outlier among large OP Stack projects, which may positively differentiate it but also means limited precedent for L2Beat template-level acceptance.
*(Source: [WHI-49](mention://issue/2e44db1f-a572-47a4-b25e-ea1e2f0fa358) SS2.5, [WHI-51](mention://issue/de290023-0bae-4540-8cae-a194649e19b3))*

---

## 4. Remediation Package

### 4.1 Cross-Dimension Invariant

The two dimensions are bound by a single constraint:

```
fallbackTimeout <= effectiveExitWindow - safetyMargin
```

This means a proposer fallback timeout must be **shorter** than the effective exit window so that users can (1) wait for fallback activation, (2) submit their own proof, and (3) complete withdrawal -- all before a malicious upgrade can take effect.

| Package | Verdict |
|---|---|
| L2Beat override / docs only | Fails -- no deployed property |
| Only proposer fallback (no timelock) | Fails -- instant upgrade preempts exit |
| Only timelock (no fallback) | Fails -- users can't get post-outage output roots |
| **Fallback <= 7d + 10d timelock + no unrestricted bypass** | **Minimum credible pass** |
| Fallback 14d + 10d timelock | **NOT minimum-pass** -- fallback activates after window expires |
| **Fallback 7d or 14d + 31d timelock + constrained emergency** | **Best-practice target** |

*(Source: [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766))*

### 4.2 Proposer Failure Remediation

**Recommended approach**: Upgrade the OP Succinct validity oracle to include a bounded permissionless `fallbackTimeout`. During normal operation, approved proposers submit proofs via the fast path. After `fallbackTimeout` seconds since the last valid output, **any caller** can submit a valid SP1 proof to advance the output root.

**Phase 1 parameter**: `fallbackTimeout <= 7 days`. With a 10d timelock and 12h exitDelay (effective window = 9.5d), this leaves >= 2.5 days for users to complete exit actions after fallback activation.

The current `mantle-xyz/op-succinct` source (commit `664a1bd`) already contains a `fallbackTimeout` mechanism with default `FALLBACK_TIMEOUT_SECS = 1209600` (2 weeks), but this is **not deployed** on the v2.0.1 oracle. Storage-layout compatibility between deployed v2.0.1 and a fallback-enabled upgrade must be verified.

**Rejected alternatives:**

| Option | Why Rejected |
|---|---|
| Wider whitelist | Mitigation only, not a pass strategy |
| `approvedProposers(address(0))` fully permissionless | Long-term target only; DoS/optimistic-mode review needed |
| Morph-style `commitBatchWithProof()` | Good design reference but architecturally different |
| L2Beat override / documentation only | Not a remediation -- no deployed property |
| Separate escape hatch | 4-9 month timeline, unnecessary given fallback option |

**Critical implementation considerations:**
- Storage-layout compatibility with deployed v2.0.1
- `tx.origin` vs `msg.sender` in the non-optimistic path (current source uses `tx.origin` due to CWIA/dispute-game patterns)
- Owner setters that could remove fallback must be timelocked
- Public prover tooling must be source-available and reproducible
- `lastProposalTimestamp` reset conditions
- Interactions with optimistic mode (zero-address permissionless is dangerous if outputs skip proof verification)

*(Source: [WHI-50](mention://issue/b36ff7b9-d4e7-4f8a-99c4-6c4708b4686c), [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766))*

### 4.3 Exit Window Remediation

**Recommended approach**: Migrate ProxyAdmin ownership **and** critical direct-owner roles from the current 0-delay Safe/ProxyAdmin model to a `TimelockController` or equivalent delayed executor.

**Coverage required** (not just ProxyAdmin):
- Proxy upgrades: `OPSuccinctL2OutputOracle`, `OptimismPortal`, `SystemConfig`, `L1StandardBridge`, `L1CrossDomainMessenger`
- Direct owner roles: `OPSuccinctL2OutputOracle.owner` setters (proposer management, verifier/vkey configuration, optimistic-mode toggle, finalization-period updates)
- Challenger/guardian: output deletion, portal pause

**Phase 1**: 10-day regular timelock (`minDelay >= 864,000s`)
- Effective window: `10d - 0.5d = 9.5d` (warning band)
- Requires `fallbackTimeout <= 7d` to satisfy cross-dimension invariant

**Phase 2 target**: 31-day regular timelock (`minDelay >= 2,678,400s`)
- Effective window: `31d - 0.5d = 30.5d` (green band)
- Accommodates 14-day fallback with substantial margin

**Emergency path design**: Must NOT be unrestricted instant ProxyAdmin/owner bypass. Must be selector/target-limited, event-rich, time-bounded, and ideally include a short delay with post-action ratification. Unrestricted instant primary route causes L2Beat to show "None" (per Arbitrum/OP Mainnet precedent where emergency paths dominate the primary sentiment).

**Timelock design requirements:**
- ProxyAdmin owner must **be** the timelock (Safe cannot also act directly)
- Timelock delay changes must be self-administered (Safe cannot reduce delay directly)
- Public upgrade calendar and cancellation runbook required

*(Source: [WHI-51](mention://issue/de290023-0bae-4540-8cae-a194649e19b3), [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766))*

### 4.4 Timelock Arithmetic Reference

| Scenario | `upgradeDelay` | `exitDelay` | Effective Window | Verdict |
|---|---|---|---|---|
| Current | 0 | 0.5d | -0.5d (None) | Red |
| 7d timelock | 7d | 0.5d | 6.5d | **Still red** |
| 7.5d timelock | 7.5d | 0.5d | 7d | Non-red minimum |
| **10d timelock (Phase 1)** | **10d** | **0.5d** | **9.5d** | **Warning (recommended)** |
| 31d timelock (Phase 2) | 31d | 0.5d | 30.5d | Green |

*(Source: [WHI-51](mention://issue/de290023-0bae-4540-8cae-a194649e19b3), [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766))*

---

## 5. Implementation Roadmap

### 5.1 Priority and Sequencing

| Priority | Action Cluster |
|---|---|
| **P0** | Freeze evidence baseline; confirm L2Beat reviewer expectations |
| **P1** | Proposer fallback design + implementation |
| **P1** | Core ProxyAdmin + critical owner timelock migration |
| **P1** | Emergency bypass inventory + restriction |
| **P2** | Public prover/fallback runbook + monitoring |
| **P2** | L2Beat evidence package + config PR |
| **P3** | 31d green-target hardening |
| **P3** | Permissionless proposer / FDP migration research |

### 5.2 Timeline Estimates

| Workstream | Estimated Duration |
|---|---|
| Proposer fallback specification | 1-2 weeks |
| Oracle implementation upgrade | 3-6 weeks |
| Prover/fallback tooling | 2-5 weeks |
| Core timelock deployment | 2-4 weeks |
| Critical role migration | 3-6 weeks |
| Emergency path redesign | 3-8 weeks |
| Evidence package + L2Beat PR | 1-2 weeks |

**Overall**: minimum pass in **8-12 weeks**, best-practice target in **12-20 weeks**.

### 5.3 L2Beat Re-Review Package

The evidence package submitted to L2Beat must include:
- Deployed addresses + implementation hashes with verified source links
- On-chain reads (`fallbackTimeout`, `lastProposalTimestamp`, `finalizationPeriodSeconds`, `getMinDelay`, owner/role mappings) with block numbers
- Storage-layout diff + audit report for oracle upgrade
- Timelock role list + delay-change rules + emergency allowlist
- Prover instructions (source-available, reproducible builds)
- The timing arithmetic table: `upgradeDelay - exitDelay = effectiveWindow`, `fallbackTimeout <= effectiveWindow - margin`
- Config PR distinguishing deployed properties from requested Risk View mapping

*(Source: [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766))*

---

## Cross-Cutting Analysis

### Consensus

All four research sections converge on the following:

1. **Template-driven assessment**: Risk Chart ratings are determined by OP Stack template code, not by chain parameters. Both `OpSuccinct -> PROPOSER_CANNOT_WITHDRAW` and `upgradeDelay = 0` are hardcoded in the template. Changing chain state alone is insufficient.

2. **User self-help is the key criterion**: L2Beat evaluates whether users can independently exit, not whether governance or admin mechanisms exist for recovery. Operational/governance proposer replacement does not satisfy the Proposer Failure criterion.

3. **Dual-dimension coupling**: Fixing one dimension without the other leaves an exploitable gap. The cross-dimension invariant (`fallbackTimeout <= effectiveExitWindow - margin`) is the binding constraint.

4. **Arithmetic precision matters**: The minimum non-red `upgradeDelay` is 7.5 days (not 7 days) because `exitDelay = 0.5 days`. A 7-day timelock would still produce a red rating.

5. **No documentation-only path**: Submitting an L2Beat override PR or documentation without deploying the corresponding on-chain properties is not a credible remediation strategy.

### Conflicts

No material contradictions were identified across the four research sections. All sections use consistent L2Beat source references (commit `c4d9593` for framework analysis, commit `aa147da` for Mantle-specific analysis) and consistent on-chain evidence (block 25143121).

### Open Questions

1. **L2Beat reviewer intent**: Only L2Beat can confirm whether an OP Succinct `fallbackTimeout` deployment would be handled as a template-level change (modifying `getRiskViewProposerFailure` for all `OpSuccinct` projects) or as a Mantle-specific `nonTemplateRiskView` override. This does not change the Phase 1 timing constraint but affects the config PR strategy.
   *(Source: [WHI-49](mention://issue/2e44db1f-a572-47a4-b25e-ea1e2f0fa358) SS5.3, [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766))*

2. **OpSuccinct -> PROPOSER_CANNOT_WITHDRAW rationale not found**: Despite exhaustive search across L2Beat's full 25-topic Methodology & Framework Forum category, GitHub PRs/commits, Glossary, and Stages documentation, no official written rationale was found for why `OpSuccinct` maps to `PROPOSER_CANNOT_WITHDRAW`. The mapping is inferred to follow the Risk Rosette Framework's red-sentiment definition ("Proposing state roots is fully centralized").
   *(Source: [WHI-49](mention://issue/2e44db1f-a572-47a4-b25e-ea1e2f0fa358) SS5.3)*

3. **Storage-layout migration**: The current `mantle-xyz/op-succinct` source contains `fallbackTimeout` but the deployed v2.0.1 ABI lacks this getter. Safe upgrade requires exact storage-layout compatibility analysis between deployed and target implementations.
   *(Source: [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766))*

4. **Emergency path design**: Requires Mantle policy input on incident-response requirements, allowed selectors/targets, and acceptable delay for emergency actions. This is a governance decision, not a purely technical one.
   *(Source: [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766))*

5. **Audit schedule**: Timeline estimates assume one major contract upgrade + one governance/role migration review. Vendor availability is not confirmed.
   *(Source: [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766))*

---

## Appendix

### A. Input Research Sections

| Order | Topic Slug | Issue | Final Section Path | Adversarial Approval |
|---|---|---|---|---|
| 1 | l2beat-risk-assessment-framework | [WHI-49](mention://issue/2e44db1f-a572-47a4-b25e-ea1e2f0fa358) | `mantle-l2beat-risk-deficiency/research-sections/l2beat-risk-assessment-framework/final.md` | comment `c7d75ead-5091-483c-b904-46f20157c468` |
| 2 | mantle-proposer-failure-analysis | [WHI-50](mention://issue/b36ff7b9-d4e7-4f8a-99c4-6c4708b4686c) | `mantle-l2beat-risk-deficiency/research-sections/mantle-proposer-failure-analysis/final.md` | comment `53eeeee3-4d36-4430-a8e6-618de5093993` |
| 3 | mantle-exit-window-analysis | [WHI-51](mention://issue/de290023-0bae-4540-8cae-a194649e19b3) | `mantle-l2beat-risk-deficiency/research-sections/mantle-exit-window-analysis/final.md` | comment `93a294a7-92c5-4a8a-b2d9-472c1c23178f` |
| 4 | recommendation-proposal | [WHI-52](mention://issue/ebf09998-4e93-4cf1-af54-fe084bad1766) | `mantle-l2beat-risk-deficiency/research-sections/recommendation-proposal/final.md` | comment `7e352368-183b-44e3-ac99-98c79c05d7a2` |

### B. Sections Index Reference

Path: `mantle-l2beat-risk-deficiency/research-sections/_index.md`

All 4 sections status: `done`. Main integration commits:
- WHI-49: `00ed3e5`
- WHI-50: `0de3520c4e9ba50c5cb9d2e9b750f3187db6b23c`
- WHI-51: `ea8ba477eae7a83faca3254a0a82d3cfb8b7fdac`
- WHI-52: `8abc26b9c464e46ecc0f6629b52f7a0619114a17`

### C. Key Contract Addresses

| Contract | Address |
|---|---|
| OPSuccinctL2OutputOracle (proxy) | `0x31d543e7BE1dA6eFDc2206Ef7822879045B9f481` |
| OPSuccinctL2OutputOracle (impl) | `0x4059509fFb703B048D1e9Ce3118F90E759076f50` |
| ProxyAdmin | `0xca35F8338054739D138884685e08b39EE2217794` |
| OptimismPortal | `0xc54cb22944F2bE476E02dECfCD7e3E7d3e15A8Fb` |
| SystemConfig | `0x427Ea0710FA5252057F0D88274f7aeb308386cAf` |
| L1StandardBridge | `0x95fC37A27a2f68e3A647CDc081F0A89bb47c3012` |
| L1CrossDomainMessenger | `0x676A795fe6E43C17c668de16730c3F690FEB7120` |
| MantleSecurityMultisig | `0x4e59e778a0fb77fBb305637435C62FaeD9aED40f` (6/14 Safe) |
| MantleEngineeringMultisig | `0x2F44BD2a54aC3fB20cd7783cF94334069641daC9` (3/7 Safe) |
| L1 MNT TimelockController | `0x65331ff6F8B0fc2612F2a0deBD9d04Fce60a447F` (`minDelay=86400`, NOT core rollup) |

### D. Source References

- L2Beat source: commits `c4d9593` (framework), `aa147da` (Mantle-specific)
- Mantle deployed oracle: Sourcify full match, keccak `0x397c...0cb`
- Ethereum chain state: block `25143121` (2026-05-21T10:48:11Z)
- Mantle `op-succinct` source: commit `664a1bd`
- Morph contracts: commit `cafa07d`
- L2Beat Forum: [Risk Rosette Framework](https://forum.l2beat.com/t/the-risk-rosette-framework/292) (2024-06-06)

### E. Methodology Notes

- All risk view sentiment determinations are anchored to specific L2Beat source file, line number, and commit hash
- On-chain evidence was gathered via `cast call` to `https://ethereum-rpc.publicnode.com` at a locked block height
- Morph comparison used both L2Beat config source and Morph contract source for independent verification
- The four research sections underwent independent adversarial review before final promotion
- Conclusions marked `[TW inference]` are Technical Writer synthesis not present in any individual research section
- Recommendations are based on deployed code analysis and L2Beat source logic; L2Beat reviewer acceptance is not guaranteed and must be confirmed through direct engagement
