# WHI-393: Enterprise Blockchain Core Modules — High-Level Overview
- **Milestone**: M6 — Decision-Layer Presentation & Three-Path Selection
- **Date**: 2026-05-12
- **Status**: Draft
- **Audience**: Decision-makers (CEO / CTO / VP Engineering / Strategy Lead)
- **Dependencies**: WHI-386 (design overview), WHI-391 (narrative framework), WHI-349–354 (M2/M3 research)

---

## Introduction: Why Eight Modules, Not One Decision

Enterprise blockchain is not a single technology choice — it is eight coupled design choices. Each module constrains the others. The reason different layer paths (L1 / L2 / L3) diverge is fundamentally because these modules differ in **control ownership**, **trust boundaries**, and **implementation depth**.

This document presents each module as presentation-ready material: one decision-layer summary, the key tradeoffs, reference project examples, and the impact on the three architecture paths. The goal is to equip leadership with the vocabulary to evaluate any enterprise blockchain proposal by asking: *what does this architecture deliver for each of the eight modules, and what does it sacrifice?*

**Five executive constraint propagation chains** make these modules inseparable:

1. **Privacy → DA → L1 Relationship → Bridge Design**: The privacy model determines where data lives, which determines the chain's settlement relationship with Ethereum.
2. **Finality → Settlement Semantics → DVP / Payment Capability**: The consensus model determines whether payment, securities, and DvP businesses are viable.
3. **Compliance Depth → Execution Modification → EVM Compatibility Risk**: How deeply compliance is enforced determines how far the execution layer must deviate from standard EVM.
4. **Access Control → Forced Inclusion → Bridge Model**: Permissioning must cover L1-originated messages, not only RPC and Sequencer paths.
5. **Identity Portability → Bridge Message Format → Interoperability**: If regulated assets move across chains, identity and policy state must travel with them.

---

## Module 1: Execution Layer

### Decision-Layer One-Liner

The execution layer determines whether enterprise rules — identity checks, compliance enforcement, payment channels — are architecturally guaranteed or merely advisory suggestions that sophisticated users can bypass.

### Why Enterprise Scenarios Require Rethinking

Public EVM chains enforce deterministic state transitions, gas accounting, and contract logic. Enterprise systems need more: identity-aware preconditions, compliance precompiles, privacy-aware transaction types, payment lanes, audit hooks, and custom bridge semantics. If these controls exist only in application contracts, they can be bypassed via alternative contracts, L1-initiated messages, delegatecall patterns, or unsupported asset wrappers.

Mantle's current EVM compatibility is a strategic asset — losing it would damage the developer and liquidity ecosystem. The challenge is adding native enterprise capabilities without turning the chain into a custom VM that loses Solidity tooling support. WHI-350 found zero EVM compatibility gap but significant extension risk: enterprise features require deeper hooks than ordinary dApps.

### Key Design Options & Tradeoffs

| Design Choice | Strength | Cost |
|---|---|---|
| **Pure Solidity / App-Layer Controls** | Minimal protocol changes; maximum tooling compatibility | Easily bypassed; inconsistent enforcement; every app re-implements policy |
| **Predeploy Contracts** | Upgradeable and EVM-friendly; ideal for registries and policy queries | Still bypassable unless execution paths are forced to call them |
| **Precompiles / Execution Hooks** | Non-bypassable and efficient; suitable for compliance, identity, cryptography | Requires client changes, custom gas accounting, security audit, and proof/circuit support |
| **Custom Transaction Types** | Cleanly encodes enterprise metadata, sponsored fees, batch calls, privacy payloads | Wallet/RPC/tooling changes; Rollup derivation and proof systems must support them |
| **New Execution Framework (e.g., Reth SDK)** | Maximum modularity for custom chain design | Higher migration cost; new operational and security attack surface |

### Reference Project Examples

- **Canton**: Daml execution with Signatory/Observer/Controller roles and consuming choices. Strongest enterprise semantics, but non-EVM adoption friction makes it a cautionary example — proves that EVM compatibility is a hard constraint (WHI-334–336).
- **Prividium**: EVM-compatible ZK Stack execution wrapped by Proxy RPC and contract/function-level RBAC. Preserves EVM compatibility but shifts enterprise controls to middleware and operational tooling (WHI-337–338).
- **Tempo**: Custom transaction envelopes via Reth SDK/revm — TIP-20 payment types, TIP-403 policy checks, AccountKeychain, and Payment Lane. Demonstrates that EVM compatibility can coexist with protocol-native payment and compliance when the client is designed for extensibility (WHI-339–340).
- **Mantle Baseline**: OP Stack execution (op-geth/op-node) with custom extensions and SP1 proof direction. Valuable OP Stack compatibility, but deep enterprise controls increase fork and proof system complexity (WHI-341, WHI-350).

### Impact on L1 / L2 / L3 Paths

| Path | Execution Approach | Control Level |
|---|---|---|
| **L1** | Reth SDK allows custom precompiles, custom transaction types, dual-runtime separation, and `no_std` proof-friendly primitives. Maximum native enterprise capability. | **Full** |
| **L2** | Conservative: retain EVM compatibility, add enterprise features via Sequencer policy, predeploy contracts, constrained custom transaction formats, and ZK/OP Stack extension points. | **Partial** — constrained by Rollup derivation and proof compatibility |
| **L3** | Inherits L2 execution model. Per-Zone customization possible but adds per-tenant operational complexity. | **Partial** — inherits L2 constraints plus per-zone maintenance |

### Suggested Slide Title & Main Message

**"Execution: Guaranteed Rules vs. Advisory Suggestions"**
Enterprise policy must be enforced at the protocol level, not the application level. The deeper the enforcement, the greater the EVM compatibility risk. L1 can go deepest; L2/L3 must balance enforcement depth against Rollup compatibility.

---

## Module 2: Consensus & Finality

### Decision-Layer One-Liner

Consensus and finality determine when a transaction is "done enough" to trigger real-world business obligations — releasing payment, transferring securities, or booking a settlement.

### Why Enterprise Scenarios Require Rethinking

Public L2 users tolerate Sequencer soft confirmations followed by delayed L1 settlement. For institutional DvP workflows, tokenized equity matching engines, payment acceptance, collateral release, or fund transfers, business systems must know *when* a transaction is sufficiently final to trigger downstream obligations. A receipt that could be economically challenged for seven days is not settlement for a payment terminal or securities workflow (WHI-345, WHI-357).

Enterprise finality is not one-dimensional — different business actions require different finality guarantees:

| Business Action | Required Finality | Acceptable Latency |
|---|---|---|
| Retail payment acceptance | Operational (Sequencer) | Seconds |
| Institutional DvP / Securities | BFT or ZK-proven | Seconds to minutes |
| Cross-chain bridge withdrawal | L1-proven | Minutes to hours |
| Regulatory audit evidence | L1-anchored | Hours (acceptable) |

### Key Design Options & Tradeoffs

| Option | Finality Characteristic | Strength | Weakness |
|---|---|---|---|
| **Centralized Sequencer Soft Finality** | Seconds, operator-trusted | Simple and fast | Not legally or cryptographically strong for high-value settlement |
| **Optimistic Rollup Finality** | Fast soft confirmation, delayed hard finality | Strong Ethereum anchoring after challenge period | Challenge delay conflicts with enterprise settlement |
| **BFT Validator Finality** | Sub-second to seconds, deterministic under validator assumptions | Excellent business UX and settlement speed | Requires validator governance and trust in 2/3 honesty assumption |
| **ZK Validity Finality** | Minutes or faster, depending on prover and L1 | Mathematical correctness with public verification | Prover cost, proof system maturity, DA assumptions |
| **Dual Finality (BFT + ZK/L1)** | BFT for daily operations, ZK/L1 for external settlement | Aligns finality levels with business value thresholds | More complex semantics and operational monitoring |

### Reference Project Examples

- **Canton**: Two-phase commit via Sequencer ordering and Mediator coordination. Transaction is final when all required participants confirm and Mediator approves. Enterprise finality can be workflow-specific rather than block-centric (WHI-335–336).
- **Prividium**: Centralized Sequencer for internal execution; STARK proofs submitted via ZKsync Gateway/Ethereum for validity settlement. Private operator provides fast internal finality while external verifiability comes from proof settlement (WHI-337–338).
- **Tempo L1**: Commonware Simplex BFT with BLS threshold signatures and sub-second deterministic finality (~600ms). The only reference project achieving true sub-second hard finality on EVM — validates the Reth+BFT L1 technology stack (WHI-339–340).
- **Tempo Zones**: Single-Sequencer `NoopConsensus` with L1 event-driven block production. Zone internal state treats `head = safe = finalized`. Simplifies consensus when the operator is explicitly trusted, but proof maturity and Sequencer availability become critical risks (WHI-340).

### Impact on L1 / L2 / L3 Paths

| Path | Finality Model | Settlement Capability |
|---|---|---|
| **L1** | Native BFT (~600ms–2s hard finality) + optional ZK anchor to Ethereum. Payment-grade. No external dependency for daily settlement. | **Full** — payment channels, DvP, securities settlement all viable |
| **L2** | ~1–2s soft confirmation; ZK hard finality depends on proof cadence (target 15–30 min, longer under high load); 7-day Optimistic fallback. | **Partial** — soft confirmation sufficient for many use cases; high-value settlement requires waiting for proof or accepting Sequencer trust |
| **L3** | Seconds-level local finality, but external hard finality bounded by L3→L2→L1 chain (~1 hour+). | **Inherited** — local finality is fast, but cross-chain exits and external settlement face compounded delays |

### Suggested Slide Title & Main Message

**"Finality: When Is 'Done' Really Done?"**
Finality is the most consequential technical differentiator between the three paths. L1 BFT delivers payment-grade operational finality, while ZK/L1 anchoring can serve higher-value external settlement when latency is acceptable. L2 provides fast soft confirmations but defers hard finality. L3 inherits L2's external finality limitations. If the target business requires real-time deterministic settlement, L1 is structurally different from L2/L3.

---

## Module 3: Privacy Layer

### Decision-Layer One-Liner

The privacy layer determines who can see what — transaction content, participant identities, balances, contract state, and operational metadata — and is the single largest architectural differentiator between public chains and enterprise systems.

### Why Enterprise Scenarios Require Rethinking

Privacy is the #1 gap between public and enterprise blockchain design (WHI-350 rated it as the only "Critical" severity gap). In public chains, transparency is the default security model. In enterprise systems, confidentiality is the default business requirement. Transaction data, balances, counterparties, order flow, contract state, investor lists, and compliance metadata may all be commercially sensitive or legally protected.

Privacy is not one-dimensional. Different stakeholders need different visibility:

| Stakeholder | What They Should See |
|---|---|
| Transaction counterparties | Their side of the deal |
| Chain operator / Sequencer | Enough to order and enforce policy (potentially everything) |
| Regulators / Auditors | Full data for audited entities, on demand |
| Other tenants | Nothing about transactions they're not party to |
| Public / External observers | State commitments and proofs only, not transaction data |

A system that hides everything from everyone fails audit and AML requirements. A system where the operator sees everything creates trust and data-breach risk. Enterprise privacy is a **controlled visibility** problem, not a pure encryption problem.

### Key Design Options & Tradeoffs

| Privacy Paradigm | Mechanism | Strength | Limitation |
|---|---|---|---|
| **Need-to-Know (Canton)** | Merkle DAG transaction projection; each participant sees only their subview | Finest possible visibility granularity; no single entity sees full transaction | Requires non-EVM language (Daml) and no global shared state — incompatible with EVM architecture |
| **Prove-Not-Reveal (Prividium)** | ZK validity proofs + Validium off-chain DA; Ethereum sees only state roots and proofs | Public settlement verifies correctness without seeing data | Operator still sees all on-chain data; DA becomes operator trust assumption |
| **Zone Isolation + Encryption (Tempo)** | Private single-Sequencer Zones, authenticated RPC, ECIES encrypted deposits | Practical multi-tenant privacy; maps well to per-app/per-client isolation | Zone Sequencer sees plaintext; proof path maturity is early |

For Mantle specifically, the design research (WHI-351) selected **Validium hybrid DA** (Phase 2) evolving to **private sub-chain/Zone** (Phase 3) as the recommended path, borrowing ECIES encrypted bridging from Tempo. Canton's model was explicitly rejected as architecturally incompatible with EVM global state.

**Critical constraint**: Mantle cannot achieve enterprise-grade privacy while continuing to publish all sensitive transaction data to public DA. Encrypted blobs only help while key management doesn't fail, and cannot solve GDPR erasure requirements since encrypted data is permanently published.

### Reference Project Examples

- **Canton**: Sub-transaction Merkle DAG projection with end-to-end encrypted routing. Conceptually the purest privacy model — in a DvP workflow, buyer, seller, bank, and registrar each see different parts of the same transaction. Rejected for Mantle due to non-EVM incompatibility (WHI-334–335).
- **Prividium**: Operator holds complete state + ZK validity proofs + Validium off-chain DA. High architectural compatibility with Mantle (single Sequencer already holds complete state). Core tension: Optimistic Rollup needs L1 data for Fault Proof; Validium requires data off-chain — resolved via delegated verification in Phase 2, ZK validity proof in Phase 3 (WHI-337–338).
- **Tempo Zones**: Independent private L2 (Zone) + single Sequencer + ECIES encrypted deposits + authenticated RPC. Highest architectural affinity with Mantle L3 path. Provides per-tenant execution isolation (WHI-339–340).
- **Paladin**: Privacy middleware with Zeto KYC membership proofs and private EVM groups. Shows where open-source privacy infrastructure can be adopted rather than built from scratch.

### Impact on L1 / L2 / L3 Paths

| Path | Privacy Mechanism | Control Level |
|---|---|---|
| **L1** | Native Zones with independent DA and Sequencer control, plus optional ZK/L1 commitments. Operator can architect privacy from the ground up. | **Full** — sovereign privacy architecture |
| **L2** | Validium/private DA mode with ZK validity proofs and constrained public settlement metadata. Requires off-chain DA infrastructure and modified Fault Proof. | **Partial** — privacy against external observers, but operator retains full visibility |
| **L3** | Per-tenant privacy Zones with private DA and bridge commitments. Best multi-tenant isolation model. | **Partial** — strong tenant isolation, but Zone Sequencer sees plaintext; external finality inherits L2 constraints |

### Suggested Slide Title & Main Message

**"Privacy: The #1 Gap — and the #1 Cascade Trigger"**
Privacy is the single most consequential module choice because it cascades to DA, settlement, bridge design, and GDPR compliance. Before choosing cryptography, choose the privacy boundary: hide from public L1? From other tenants? From the operator? Each boundary demands a different architecture — and a different cost.

---

## Module 4: Compliance & Identity

### Decision-Layer One-Liner

Compliance and identity determine whether the chain can satisfy regulated financial infrastructure requirements — KYC/KYB, sanctions screening, Travel Rule, audit trails, and regulator access — at the protocol level rather than as optional application add-ons.

### Why Enterprise Scenarios Require Rethinking

In enterprise scenarios, compliance is a precondition for operation, not an optional feature. A regulated asset network must know whether participants passed KYC/KYB, whether counterparties are sanctioned, whether transfers trigger Travel Rule obligations, whether investors qualify to hold a given security, whether regulators can inspect relevant data, and whether an audit trail can be produced under legal process.

Public chains treat addresses as atomic identity units. Enterprise systems need at minimum three mappings: (1) legal entity → cryptographic key (KYC/KYB, lifecycle, revocation, recovery), (2) key → roles and permissions (trader, issuer, custodian, auditor, regulator, admin), and (3) role + policy → execution outcome (allow, deny, freeze, disclose, route, escalate).

The critical design question: how deep must compliance enforcement go to be non-bypassable for the target use case? Application-layer optional checks are too weak for regulated infrastructure. Protocol-level precompiles are strongest but add client/proof complexity.

### Key Design Options & Tradeoffs

| Enforcement Level | Strength | Risk |
|---|---|---|
| **Middleware Compliance** (RPC gateway) | Fast integration with Okta, AD, AML vendors, sanctions APIs | Bypass risk; policy may not bind cryptographically to execution |
| **Contract-Layer Compliance** (Predeploy registries, transfer hooks) | Flexible, application-specific, easily upgradeable | Each app must implement correctly; wrappers or L1 messages may bypass |
| **Protocol/Precompile Compliance** | Non-bypassable and auditable; universal policy semantics | Client/proof upgrades; governance and emergency handling become critical |

WHI-353 recommends a three-phase approach: Phase 1 middleware MVP (2–3 person-months) → Phase 2 contract-layer enhancement with transfer hooks (3–4 person-months) → Phase 3 optional protocol-layer upgrade (6+ person-months).

### Reference Project Examples

- **Canton**: Daml Signatory/Observer/Controller model. Regulators can be added as Observers who receive actual relevant transaction data — the most mature regulator interface pattern. Compliance is embedded in workflow semantics and visibility (WHI-334–335).
- **Prividium**: SSO/OIDC authentication, JWT-wallet binding, RBAC with 6 permission types, private block explorer, Merkle export for audit, ZK compliance proof direction. Most direct enterprise IAM integration at the gateway/operator level (WHI-337–338).
- **Tempo**: TIP-403 Policy Registry as a protocol-level primitive for TIP-20 transfers. When token and transfer semantics are designed around compliance, enforcement becomes a chain-native capability rather than an application concern (WHI-339–340).
- **Paladin**: Zeto KYC membership proofs that prove compliance without revealing PII. Shows where zero-knowledge techniques can reduce regulatory disclosure burden.

### Impact on L1 / L2 / L3 Paths

| Path | Compliance Depth | Control Level |
|---|---|---|
| **L1** | Protocol-native compliance via precompiles, IdentityRegistry, PolicyRegistry, and audit infrastructure. Non-bypassable enforcement for all transactions. | **Full** — deepest enforcement possible |
| **L2** | Predeploy contract registries + Sequencer policy engine + L1 Bridge whitelist. Effective for managed asset domains but cannot enforce globally on arbitrary third-party contracts. | **Partial** — strong for managed assets; bypass risk on unmanaged contracts |
| **L3** | Inherits L2 compliance infrastructure. Per-Zone policy customization possible. Cross-Zone compliance state sharing requires additional protocol work. | **Partial** — per-tenant policy flexibility, but cross-zone coordination is an open design problem |

### Suggested Slide Title & Main Message

**"Compliance: Built-In, Not Bolted-On"**
Regulated financial infrastructure requires compliance at the protocol level — not as optional application checks. The deeper the enforcement, the stronger the guarantee, but the higher the EVM modification cost. Mantle's centralized Sequencer is an unexploited compliance asset: it already sees all transaction flow and can become a natural enforcement point.

---

## Module 5: Access Control

### Decision-Layer One-Liner

Access control determines which actors can cross which system boundaries — connecting to the network, submitting transactions, bridging assets, deploying contracts, reading data, and modifying governance — across every ingress path, not just the front door.

### Why Enterprise Scenarios Require Rethinking

Access control is often confused with identity, but its scope is broader. Identity says who a key represents. Access control says which boundaries that actor can cross. Enterprise blockchains have more boundaries than typical applications:

| Boundary | Example Control |
|---|---|
| Network / RPC | Can this user connect, query, or submit? |
| Sequencer / Txpool | Can this transaction be sequenced? |
| L1 Bridge Entry | Can this L1-initiated message enter the chain? |
| Contract / Function | Can this role call this method with these parameters? |
| Token Transfer | Can this asset move from this sender to this receiver right now? |
| Data / RPC Visibility | Can this user query this account, log, or block detail? |
| Admin / Governance | Can this party change policy or validator configuration? |

If the RPC layer is protected but the Sequencer accepts direct transactions, control is weak. If the Sequencer is protected but L1 bridge messages can force deposits or contract calls, control is weak. WHI-350 and WHI-344 both flag the **L1 forced-inclusion path** as the critical enterprise security gap — without an L1 Bridge whitelist, all RPC/Sequencer admission control is bypassable.

### Key Design Options & Tradeoffs

WHI-352 recommends a **four-layer defense-in-depth** model:

1. **RPC Authentication Gateway** — Envoy Proxy with JWT/OIDC verification, address binding, and rate limiting. Fast to deploy, but only covers the front door.
2. **Sequencer Policy Engine** — Admission filter at the Sequencer level. Mantle's centralized Sequencer is a zero-cost compliance asset requiring no new trust assumptions.
3. **L1 Bridge Whitelist** — `MantleEnterpriseOptimismPortal` with `onlyAllowed` modifier on deposits. Blocks the critical L1 forced-transaction bypass.
4. **Predeploy Identity/Policy Registries** — On-chain IdentityRegistry and PolicyRegistry providing the authoritative source for all access decisions.

| Design Choice | Strength | Cost |
|---|---|---|
| **Sequencer as primary admission control** | Zero new trust assumptions (already centralized); high-value enterprise adaptation point | P2P-propagated transactions and L1 forced transactions need separate handling |
| **L1 Bridge whitelist (separate from L2)** | Blocks L1 forced-transaction bypass (critical security baseline) | Dual-write governance complexity; L1Allowlist can drift from L2 IdentityRegistry |
| **Predeploy over Precompile** | Upgradeable without hard fork; follows existing Mantle predeploy practice | Cannot enforce global EVM-level interception; only managed contract domain benefits |
| **Registry contract over SBT for KYC** | Single SLOAD per check (~2,600 gas); admin can update without burn/mint | Not ERC-5192 compatible; no wallet display |

### Reference Project Examples

- **Prividium**: Proxy RPC three-step verification (token → address binding → permission), `PrividiumTransactionFilterer` for L1 Bridge filtering, dual endpoint design (Bearer JWT + MetaMask-compatible), multicall blocking, RBAC with 6 permission types (WHI-337–338).
- **Tempo**: TIP-403 Policy Registry (precompile-level, highest non-bypassability), AccountKeychain (root key delegates access keys with call scope, token limits, and expiry), Zone authenticated RPC, `ZonePortal` admission check at bridge level (WHI-339–340).
- **Canton**: Permissioned gRPC, topology state, participant permissions, Daml authorization, package vetting. Deepest protocol-native model but non-EVM (WHI-334–335).
- **Mantle Baseline**: Permissionless RPC and transactions, standard bridge paths. No native enterprise boundary coverage (WHI-341).

### Impact on L1 / L2 / L3 Paths

| Path | Access Control Model | Control Level |
|---|---|---|
| **L1** | Protocol-native: permissioned validators, precompile-level policy, native Zone isolation, bridge controls. Every boundary is architect-controlled. | **Full** — all ingress paths controlled from genesis |
| **L2** | Four-layer defense: RPC gateway + Sequencer policy + L1 Bridge whitelist + predeploy registries. Effective but requires dual-write governance between L1 and L2. | **Partial** — strong coverage but L1 Bridge whitelist adds operational complexity |
| **L3** | Inherits L2 access infrastructure. Per-Zone access policies possible. Cross-Zone access control requires coordination protocol. | **Partial** — per-tenant flexibility, but Phase 1 provides only logical isolation (not execution isolation) |

### Suggested Slide Title & Main Message

**"Access Control: Every Door, Not Just the Front Door"**
Enterprise access control must cover every ingress path — RPC, Sequencer, L1 Bridge, contract deployment, data reads, and governance. The L1 forced-inclusion path is the critical gap: without a Bridge whitelist, all other controls are bypassable. Mantle's centralized Sequencer is a natural enforcement point, but it's not sufficient alone.

---

## Module 6: Data Availability & Data Sovereignty

### Decision-Layer One-Liner

Data availability determines where transaction data lives and who can reconstruct chain state — and is the point where public blockchain security directly conflicts with enterprise confidentiality, data residency laws, and GDPR deletion rights.

### Why Enterprise Scenarios Require Rethinking

In a classic Rollup, transaction data is published to L1 so that anyone can reconstruct state or safely exit. In enterprise scenarios, this same publication may leak confidential business data and violate data localization, retention, or deletion requirements.

Data sovereignty adds hard legal constraints:

| Requirement | Architectural Impact |
|---|---|
| Sensitive transaction data must not go on public chain | Requires Validium/private DA, encrypted metadata, or no public DA for sensitive traffic |
| GDPR erasure or retention control | Favors off-chain controlled storage over permanent L1 blobs |
| Jurisdiction-specific data residency | Requires Zone/tenant-specific storage locations |
| Full-node sync for external parties | Must work with redacted or commitment-only data |

The core tension: **public DA provides the strongest security guarantee** (anyone can verify), but **enterprise privacy requires restricted DA** (only authorized parties can access data). This is not a configuration toggle — it changes the chain's fundamental security model.

### Key Design Options & Tradeoffs

| DA Model | Security Guarantee | Privacy | GDPR Compatibility |
|---|---|---|---|
| **Public DA (L1 blobs/calldata)** | Strongest: anyone can reconstruct state and challenge | None: all transaction data publicly observable | Incompatible: permanent publication, no deletion |
| **Validium (off-chain DA, on-chain commitments)** | Operator-dependent: data availability relies on operator honesty | Strong against external observers: L1 sees only state roots and proofs | Achievable: operator controls storage and can implement deletion |
| **Hybrid DA (public + private segments)** | Mixed: public batches get full guarantee, private batches get operator guarantee | Selective: per-transaction classification routes sensitive data off-chain | Partially achievable: private segments can be deleted; public segments cannot |
| **Sovereign DA** | Chain-controlled: validators/operators manage their own DA infrastructure | Full control: data stays within the network's trust boundary | Fully achievable: complete control over retention and deletion |

WHI-351 recommends **hybrid DA** for the L2 path: a single L2 block encoded as one public batch envelope plus zero or more private segments. The privacy classifier tags transactions; the hybrid DA router sends public batches to L1 and private batches to a Private DA Server. Commitments for both are submitted atomically in the same L1 transaction to prevent batch index misalignment.

### Reference Project Examples

- **Canton**: Distributed projection model — no single DA layer at all. Each participant stores only their projection of the ledger. Synchronizers coordinate but don't hold complete global state (WHI-334–335).
- **Prividium**: Full Validium — operator holds complete state, publishes only state roots and STARK proofs to Ethereum. Most GDPR-friendly design among reference projects (WHI-337–338).
- **Tempo Zones**: Zone data is isolated from L1. Zones use private DA with bridge-level encryption for deposit metadata. L1 sees commitment hashes only (WHI-339–340).
- **Mantle Baseline**: Public DA via L1 blobs/calldata. `op-alt-da` pluggable DA framework exists with `GenericCommitment` type, providing a clean engineering path for private DA backend with zero core protocol modification (WHI-341).

### Impact on L1 / L2 / L3 Paths

| Path | DA Model | Control Level |
|---|---|---|
| **L1** | Sovereign DA infrastructure. Validators manage data storage, replication, and retention. Optional ZK anchoring to Ethereum for public verifiability. | **Full** — complete data sovereignty from genesis |
| **L2** | Hybrid DA via `op-alt-da` framework: public batches to L1, private batches to Private DA Server. Changes security model for private transactions from "Ethereum guaranteed" to "operator guaranteed." | **Partial** — public transactions retain full Ethereum DA guarantee; private transactions depend on operator |
| **L3** | Per-Zone private DA with commitments settled to L2. Data residency can be jurisdiction-specific per Zone. | **Partial** — strong per-tenant data sovereignty, but DA availability/recovery adds operational burden per Zone |

### Suggested Slide Title & Main Message

**"Data Availability: Security vs. Sovereignty — The Fundamental Tradeoff"**
Public DA is the strongest security guarantee but is incompatible with enterprise privacy and data sovereignty. Every step toward private DA trades Ethereum's verification guarantee for operator trust. The L1 path starts sovereign. The L2 path must engineer hybrid DA. The L3 path inherits L2's DA model but gains per-tenant control.

---

## Module 7: Interoperability

### Decision-Layer One-Liner

Interoperability determines whether the enterprise chain can connect to Ethereum liquidity, Mantle's existing ecosystem, other enterprise networks, and legacy financial infrastructure — without leaking enterprise controls at the boundary.

### Why Enterprise Scenarios Require Rethinking

Enterprise interoperability is harder than public-chain bridging because every cross-chain message is a potential policy leak. If an enterprise chain enforces strict KYC and sanctions screening internally but its bridge to Ethereum accepts deposits from any address, the access control model is broken at the boundary. If finality labels don't propagate across bridges, a receiving chain might treat a soft confirmation as settlement.

Key enterprise interoperability challenges:

| Challenge | Why It's Hard |
|---|---|
| **Policy propagation** | Enterprise rules must follow assets across chain boundaries |
| **Finality label preservation** | Receiving systems must know the finality state of incoming messages |
| **Cross-enterprise atomicity** | DvP across two enterprise chains requires coordinated finality |
| **Legacy system integration** | Banks, custodians, and clearinghouses expect API-based or message-based interfaces, not blockchain events |
| **Regulatory boundary crossing** | Different jurisdictions may have different compliance requirements for the same asset |

### Key Design Options & Tradeoffs

| Interop Model | Strength | Limitation |
|---|---|---|
| **Standard L1 Bridge (OP Stack)** | Maximum Ethereum ecosystem compatibility; proven security model | No enterprise policy filtering; no finality labels; no cross-enterprise semantics |
| **Enterprise Bridge with Policy Filtering** | Bridge-level KYC/sanctions checks; deposit encryption; withdrawal compliance | Added latency; governance complexity for policy sync between L1 and L2 |
| **Cross-Enterprise Federation** | Direct inter-chain messaging between enterprise networks; policy propagation protocols | Requires bilateral agreements; no industry standard yet; coordination overhead |
| **API/Oracle Gateway** | Bridges blockchain state to legacy systems (SWIFT, FIX, core banking) | Introduces trust assumptions at the oracle boundary; latency; operational dependency |

### Reference Project Examples

- **Canton**: Global Synchronization Domain with participant-level routing. Cross-domain transactions are first-class — Canton was designed from the ground up for multi-party workflows across organizational boundaries (WHI-335–336).
- **Prividium**: L1 `TransactionFilterer` for bridge filtering, plus standard ZKsync bridge infrastructure. Enterprise controls added at L1 contract level (WHI-337–338).
- **Tempo**: `ZonePortal` for Zone ↔ L1 bridging with admission checks. Zones communicate through L1 events. ECIES encrypted deposits protect bridge metadata from L1 observers (WHI-339–340).
- **Mantle Baseline**: Standard OP Stack bridge (MNT + ETH dual-token). No native enterprise filtering. L1 forced-inclusion path is the critical interop security gap (WHI-341).

### Impact on L1 / L2 / L3 Paths

| Path | Interop Model | Control Level |
|---|---|---|
| **L1** | Sovereign bridge design. Can implement custom bridge contracts with full policy enforcement. Optional ZK bridge to Ethereum for public verifiability. Cross-enterprise federation as a first-class capability. | **Full** — architect-controlled bridge semantics |
| **L2** | Modified OP Stack bridge with `TransactionFilterer` and enterprise portal. Policy filtering at L1 contract level. Finality labels must be explicitly designed for bridge messaging. | **Partial** — enterprise controls added to existing bridge, but constrained by OP Stack bridge semantics |
| **L3** | Zone ↔ L2 bridging via ZonePortal. Cross-Zone communication routes through L2. External interop inherits L2 bridge constraints. | **Inherited** — per-Zone bridge policies possible, but external interop depends on L2 |

### Suggested Slide Title & Main Message

**"Interoperability: Don't Leak Your Controls at the Border"**
Every bridge is a potential policy boundary violation. Enterprise interoperability requires policy-aware bridges, finality label propagation, and cross-enterprise coordination — none of which exist in standard public-chain bridge designs. The L1 path designs bridges from scratch. L2/L3 must retrofit enterprise controls onto existing bridge infrastructure.

---

## Module 8: Operations & Business Components

### Decision-Layer One-Liner

Operations and business components determine whether the blockchain can be run as production financial infrastructure — with predictable SLAs, disaster recovery, key management, audit export, monitoring, and product-layer components like RWA issuance, DvP settlement, and payment processing.

### Why Enterprise Scenarios Require Rethinking

Public chains are operated by loosely coordinated node operators. Enterprise chains are operated by entities with contractual obligations, operational runbooks, data retention requirements, and regulated incident response. Monitoring, audit logs, key management, retention policies, and deployment topology become architectural concerns, not DevOps details.

Beyond operations, enterprise blockchains must deliver **product-layer components** that transform infrastructure into usable financial products:

| Component | Purpose |
|---|---|
| **RWA Issuance** | Tokenized real-world assets with compliance-aware transfer restrictions |
| **DvP Settlement** | Delivery-versus-payment with atomic finality guarantees |
| **Payment Processing** | Payment lanes with dedicated throughput, gas budgets, and settlement SLAs |
| **Custody Integration** | Institutional key management, HSM signing, multi-sig governance |
| **Audit Export** | Structured compliance reports (TAR, SAR, CTR) with cryptographic proofs |
| **SLA Management** | Contractual availability, throughput, and latency guarantees |

### Key Design Options & Tradeoffs

| Operational Model | Strength | Limitation |
|---|---|---|
| **SaaS (Mantle-managed)** | Lowest operational burden for clients; fastest onboarding | Client depends on Mantle for availability, compliance, and data sovereignty |
| **Dedicated Cloud (Enterprise account)** | Data residency in client's cloud; compliance boundary separation | Higher operational complexity; Mantle provides software, client manages infrastructure |
| **On-Premises** | Maximum data sovereignty; meets strictest regulatory requirements | Highest operational burden; client must maintain blockchain infrastructure expertise |
| **Hybrid (Recommended)** | Mantle operates core infrastructure; enterprise controls Zone-level data and policy | Balanced complexity; requires clear responsibility boundaries |

WHI-353 defines three SLA tiers: Bronze (99.5% / 43.8h downtime), Gold (99.95% / 4.38h), and Platinum (99.99% / 52.6min). Disaster recovery differs fundamentally between public DA (L2 state fully re-derivable from L1, RTO <4h) and private DA/Validium (requires cross-region private DA replicas, RTO 4–24h).

### Reference Project Examples

- **Canton**: Participant nodes maintain local storage and audit views. Operations model is built around institutional self-custody of data with Synchronizer coordination (WHI-334–335).
- **Prividium**: Private subnet and Proxy RPC model maps directly to enterprise operations. 35+ financial institutions operate within a managed infrastructure model (WHI-337–338).
- **Tempo**: Payment Lane separates payment gas budget from general traffic. Zone architecture enables per-tenant operational isolation. Structured audit event pipeline for compliance reporting (WHI-339–340).
- **Mantle Baseline**: Public L2 operations. GCP KMS HSM integration already exists (`op-service/hsm/hsm_signer.go`). Standard OP Stack monitoring and deployment tooling (WHI-341).

### Impact on L1 / L2 / L3 Paths

| Path | Operational Model | Control Level |
|---|---|---|
| **L1** | Full sovereign operations. Validator set management, key ceremonies, BFT governance, independent DA infrastructure, payment lanes, and business components built natively. Highest operational cost. | **Full** — but requires 15–25 person team and 18–24 month build |
| **L2** | Extends Mantle operational infrastructure. Adds enterprise monitoring, compliance middleware, audit export, and business components as layers on existing OP Stack ops. | **Partial** — significant reuse of existing infrastructure; lower operational cost |
| **L3** | Per-Zone operational isolation. Each Zone requires Sequencer, DA, keys, monitoring, and upgrade management. Operations scale linearly with tenant count. | **Partial** — per-tenant flexibility, but operational burden is multiplicative |

### Suggested Slide Title & Main Message

**"Operations: Infrastructure Is the Product"**
Enterprise blockchain is not just software — it's a production financial service. SLA commitments, disaster recovery, key management, audit export, and business components (RWA, DvP, payments) are what transform blockchain infrastructure into a sellable product. L1 offers the deepest native capabilities but the highest operational cost. L2 reuses the most existing infrastructure. L3 multiplies operational burden per tenant.

---

## Constraint Propagation: How Module Choices Cascade

Enterprise blockchain modules are not independent — choices in one module cascade to others in predictable and non-negotiable ways. Understanding these constraint chains is essential for evaluating any architecture proposal.

### Chain 1: Privacy → DA → L1 Relationship → Bridge Design

```
Privacy Choice          DA Impact                L1 Relationship           Bridge Design
─────────────          ──────────               ───────────────           ─────────────
Public transactions → Public DA (blobs)       → Standard Rollup          → Standard bridge
                                                settlement

Validium mode       → Private DA Server       → Commitment-only          → Enterprise portal
                      (operator guarantee)      settlement (no data)       with encryption

Zone isolation      → Per-Zone private DA     → Per-Zone commitments     → ZonePortal with
                      (tenant-controlled)       to L2/L1                   admission checks
```

**Decision-layer implication**: If you need enterprise privacy, you lose Ethereum's DA guarantee. If you lose the DA guarantee, the chain's settlement relationship with Ethereum changes fundamentally. This is not a configuration option — it's an architectural fork in the road.

### Chain 2: Finality → Settlement Semantics → Business Capability

```
Finality Choice         Settlement Semantic       Business Viability
───────────────         ──────────────────        ──────────────────
Sequencer soft confirm → "Probably done"         → Retail payments: OK
  (~1-2s)                                          DVP/Securities: NOT OK

BFT hard finality     → "Deterministically done" → Payment channels: OK
  (~600ms-2s)           under validator quorum     DVP/Securities: OK
                                                   Real-time settlement: OK

ZK/L1 proven          → "Mathematically proven"  → Cross-chain exits: OK
  (minutes-hours)       on Ethereum                High-value settlement: OK
                                                   But latency too high for
                                                   real-time operations
```

**Decision-layer implication**: If the target business requires real-time deterministic operational settlement (payment acceptance, intraday collateral movement, low-latency DvP), BFT hard finality is the cleanest primitive. ZK/L1 finality can support high-value external settlement and bridge exits, but its latency makes it a different business product. L2/L3 soft confirmations can support many enterprise workflows, but they need explicit finality labels and threshold rules before downstream systems treat them as settlement.

### Chain 3: Compliance Depth → Execution Modification → EVM Compatibility

```
Compliance Choice       Execution Impact          EVM Compatibility
─────────────────       ────────────────          ─────────────────
Middleware-only       → No protocol changes       → Full EVM compatibility
  (RPC gateway)         (bypass risk: HIGH)

Contract-layer        → Predeploy registries      → Full EVM compatibility
  (transfer hooks)      + ~30-50K gas overhead      (managed asset domain only)

Protocol-level        → Custom precompiles,       → Reduced EVM compatibility
  (precompile)          client changes, proof        (custom gas, client mods,
                        system modifications          proof system changes)
```

**Decision-layer implication**: Deeper compliance enforcement provides stronger guarantees but increases EVM deviation risk. The L1 path can go deepest because it doesn't need to maintain Rollup compatibility. L2/L3 must balance enforcement depth against the value of staying within the OP Stack / ZK Stack ecosystem.

### Chain 4: Cross-Module Dependencies

| If You Choose... | Then You Must Also... |
|---|---|
| Validium privacy (Phase 2) | Build Private DA Server infrastructure; modify Fault Proof system (delegated verification or ZK); extend access control to Private DA read credentials |
| L1 Bridge whitelist | Implement dual-write governance between L1 Allowlist and L2 IdentityRegistry; add reconciliation worker; test Mantle's dual-token bridge explicitly |
| Sequencer compliance enforcement | Add admission filter interface (~5ms latency budget); build three-level whitelist cache; implement audit event pipeline |
| GDPR-compliant data handling | Implement Validium (Phase 2+) for transaction content; store only event hashes on-chain; build off-chain deletion/anonymization pipeline |
| Per-tenant isolation (Phase 3) | Deploy Zone architecture; independent Sequencer + DA + policy per Zone; cross-Zone compliance state sharing protocol |
| Permissioned access control | Filter L1 forced-inclusion paths; accept that a regulated Rollup weakens the pure permissionless escape narrative; carry access decisions into bridge contracts |
| Payment SLA commitments | Add Payment Lane or equivalent capacity reservation; define token/address classification rules; monitor finality and throughput as product SLAs |
| Data sovereignty guarantees | Separate Zone DA, audit DA, and public commitments; define retention/deletion policy; assign operating responsibility for each storage boundary |
| Ethereum security anchoring | Operate proof generation, relayers, verifier contracts, gas budgeting, and proof-latency monitoring as core infrastructure |
| Portable compliance identity | Include credential proofs, policy version, and disclosure references in bridge messages; ensure wallet/custody systems can preserve those semantics |

---

## Summary Matrix: 8 Modules × 3 Paths

| Module | Enterprise L1 | Enterprise L2 | Enterprise L3 |
|---|---|---|---|
| **1. Execution** | **Full** — Reth SDK, custom precompiles, custom tx types, dual runtime | **Partial** — predeploys, Sequencer policy, constrained custom tx formats within OP/ZK Stack | **Partial** — inherits L2 execution; per-Zone customization adds ops burden |
| **2. Consensus & Finality** | **Full** — native BFT (~600ms hard finality), optional ZK/L1 anchor | **Partial** — soft confirm (~1-2s), ZK hard finality (15-30min target), 7d Optimistic fallback | **Inherited** — local fast, external bounded by L3→L2→L1 chain (~1h+) |
| **3. Privacy** | **Full** — sovereign DA, native Zones, architect-controlled visibility | **Partial** — Validium hybrid DA, operator retains full visibility, modified Fault Proof | **Partial** — per-tenant Zone isolation, private DA per Zone, Zone Sequencer sees plaintext |
| **4. Compliance & Identity** | **Full** — protocol-native precompiles, non-bypassable enforcement | **Partial** — predeploy registries + Sequencer policy; managed-asset domain enforcement | **Partial** — per-Zone policy; cross-Zone compliance sharing is open problem |
| **5. Access Control** | **Full** — all ingress paths controlled from genesis | **Partial** — 4-layer defense; L1 Bridge whitelist adds governance complexity | **Partial** — per-Zone policies; Phase 1 logical isolation only |
| **6. DA & Data Sovereignty** | **Full** — sovereign DA infrastructure | **Partial** — hybrid DA; private segments depend on operator | **Partial** — per-Zone private DA; adds operational burden per Zone |
| **7. Interoperability** | **Full** — custom bridge design, cross-enterprise federation | **Partial** — modified OP Stack bridge, policy filtering at L1 contracts | **Inherited** — per-Zone bridges; external interop depends on L2 |
| **8. Operations & Business** | **Full** — native payment lanes, DvP, RWA; highest ops cost (15-25 people, 18-24mo) | **Partial** — reuses Mantle ops; lower cost (8-15 people, 8-12mo) | **Partial** — per-tenant ops isolation; cost scales per Zone (10-15 people, 9-13mo) |

### Key Divergence Points

The **four modules that most sharply differentiate the paths** are:

1. **Consensus & Finality** — L1's native BFT is a structurally different product from L2/L3's Rollup-derived finality. This single module determines whether payment, DvP, and securities businesses are viable without trust workarounds.

2. **Privacy / DA** — L1 starts sovereign. L2 must engineer Validium. L3 inherits L2's model but adds per-tenant control. The privacy choice cascades to DA, which cascades to the Ethereum settlement relationship.

3. **Execution** — L1 can enforce enterprise rules at the deepest protocol level. L2/L3 are constrained by Rollup compatibility. This determines whether compliance enforcement is architecturally guaranteed or reliant on middleware.

4. **Access / Interoperability Boundary** — L2 and L3 must retrofit permissioning onto bridge and forced-inclusion paths. L1 can design ingress, bridge messages, and credential portability as native protocol semantics.

**Bottom line**: L1/L2/L3 are not a maturity ladder — they are different products for different buyers. The layer is the *consequence* of the module requirements, not the starting point. Leadership must first decide what the target use case demands across these eight modules, then select the path that delivers those requirements within acceptable cost and timeline constraints.

---

## Appendix: Module Interaction Map

```
                    ┌──────────────┐
                    │  Execution   │◄──── Compliance depth changes
                    │    Layer     │      execution modification depth
                    └──────┬───────┘
                           │ enforces
                    ┌──────▼───────┐         ┌───────────────┐
                    │  Compliance  │◄────────►│ Access Control│
                    │  & Identity  │ shared   │               │
                    └──────┬───────┘ identity └───────┬───────┘
                           │ source                   │ L1 Bridge
                           │                          │ whitelist
                    ┌──────▼───────┐                  │
                    │   Privacy    │──────────────────►│
                    │    Layer     │ privacy depends   │
                    └──────┬───────┘ on access infra   │
                           │                           │
              ┌────────────▼────────────┐              │
              │  DA & Data Sovereignty  │◄─────────────┘
              │                         │  bridge filtering
              └────────────┬────────────┘  controls who enters
                           │
              ┌────────────▼────────────┐
              │    Interoperability     │
              │  (Bridge / Federation)  │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐     ┌────────────────┐
              │  Consensus & Finality   │────►│  Operations &  │
              │                         │     │  Business Comp │
              └─────────────────────────┘     └────────────────┘
                finality determines               SLA, monitoring,
                business capability               product viability

Key Constraint Flows:
  Privacy ──→ DA model ──→ Ethereum settlement ──→ Bridge design
  Finality ──→ Settlement semantics ──→ DVP/Payment/Securities viability
  Compliance ──→ Execution modification ──→ EVM compatibility risk
  Access Control ──→ Forced inclusion handling ──→ Bridge model
  Identity portability ──→ Bridge message format ──→ Interoperability
```
