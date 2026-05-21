# WHI-392: Four Reference Project High-Level Overviews
## Canton / Prividium / Tempo Zones / Paladin
- **Milestone**: M6 — Decision-Layer Presentation & Three-Path Selection
- **Date**: 2026-05-12
- **Status**: Draft
- **Audience**: Mantle Decision-Makers (CEO / CTO / VP Engineering / Strategy Lead)
- **Dependencies**: WHI-334–340 (M1 research), WHI-369–372 + WHI-382 (Paladin research), WHI-391 (narrative framework)

---

## How to Use This Document

This document provides slide-ready material for four reference blockchain projects that informed Mantle's enterprise strategy. Per the WHI-391 narrative framework (Beat 2), the main deck carries **one slide** (a 2×2 matrix) covering all four projects; deeper per-project profiles feed **Appendix B** (one page each). The material below supports both layers.

**Decision-layer takeaway**: The enterprise blockchain market has converged on EVM. Being non-EVM is a dealbreaker. The real differentiators are finality semantics, privacy architecture, and compliance enforcement depth.

---

# 1. Canton (Digital Asset)

## 1.1 One-Line Positioning

Canton enables multiple regulated financial institutions to transact together atomically while each party sees only the data it is legally and contractually entitled to see — without any global shared ledger.

## 1.2 Core Architecture

Canton replaces the shared ledger with a coordination protocol. There is no global state anywhere — only a "Virtual Global Ledger" that is the logical union of each participant's private projection.

```
┌─────────────────────────────────────────────────────────────┐
│              VIRTUAL GLOBAL LEDGER                          │
│         (logical concept — nowhere physically stored)       │
└──────────────────────────┬──────────────────────────────────┘
                           │
        Coordinated by one or more SYNCHRONIZERS:
┌──────────────────────────▼──────────────────────────────────┐
│                     SYNCHRONIZER                            │
│                                                             │
│  ┌───────────────────┐       ┌────────────────────────┐     │
│  │     SEQUENCER     │       │       MEDIATOR         │     │
│  │                   │       │                        │     │
│  │ Sees: encrypted   │       │ Sees: who must confirm │     │
│  │ blobs + recipient │       │ + yes/no signals only  │     │
│  │ lists only        │       │                        │     │
│  │                   │       │ Runs 2-phase commit;   │     │
│  │ Orders messages;  │       │ issues APPROVE/REJECT  │     │
│  │ cannot read txns  │       │ verdict                │     │
│  └───────────────────┘       └────────────────────────┘     │
└──────────┬──────────────────────────┬───────────────────────┘
           │                          │
           │  Routes encrypted sub-trees to relevant parties
           ▼                          ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ PARTICIPANT  │    │ PARTICIPANT  │    │ PARTICIPANT  │
│  (Bank A)    │    │  (Bank B)    │    │  (Regulator) │
│              │    │              │    │              │
│ Daml Engine  │    │ Daml Engine  │    │ Observer     │
│ ACS: Bank A's│    │ ACS: Bank B's│    │ ACS: audit   │
│ contracts    │    │ contracts    │    │ projection   │
│ only         │    │ only         │    │ only         │
└──────────────┘    └──────────────┘    └──────────────┘
```

A submitting Participant encodes a transaction as a Merkle DAG tree. The Sequencer routes each encrypted sub-tree only to the parties who are informees. The Mediator collects yes/no signals and issues a binding verdict — without ever seeing transaction content. Each Participant updates only its own Active Contract Set. No node ever holds the complete picture.

## 1.3 Core Design Principles

1. **Need-to-know privacy by default.** Every piece of data flows only to parties with a contractual right to see it. The Sequencer sees encrypted blobs; the Mediator sees only confirmation signals. GDPR compliance is structural, not bolted on.

2. **Sub-transaction privacy via Merkle DAG projection.** Within a single multi-party trade (e.g., DvP between Alice, Bob, a bank, and a registrar), each party receives a different slice of the transaction tree. Hidden nodes are replaced by verifiable hashes.

3. **Daml authorization model.** Every contract declares Signatories (must authorize creation), Observers (see but don't authorize), and Controllers (may exercise choices). No obligation can be imposed without cryptographic consent — a language-level guarantee that Solidity modifiers do not provide.

## 1.4 Inspiration for Mantle

1. **Privacy projection model.** The Merkle DAG blinding pattern — different recipients receive different sub-trees with hidden nodes replaced by verifiable hashes — is the most portable concept from Canton. Mantle could adopt this at the DA/calldata layer for selective data visibility without requiring ZK proofs.

2. **Observer/regulator hooks.** Canton's Observer role gives regulators read-only visibility into specific contracts without participating in authorization. Mantle can borrow this as a permissioned "audit node" role at the Sequencer or RPC layer.

3. **Synchronizer federation for horizontal scaling.** Each Synchronizer is independently governed and scaled, serving different jurisdictions or counterparty clusters. This maps to a multi-L3 federation model where enterprise deployments operate isolated environments that interoperate through a shared coordination layer.

## 1.5 Limitations and Non-Portability

1. **Non-EVM Scala/Daml stack with no extraction path.** Canton is 96% Scala, built on Pekko (Akka) actors, cats monads, sbt, and ScalaPB. For a Go/Rust/TypeScript team on OP Stack, direct code reuse is not viable — porting cost exceeds a ground-up build.

2. **Privacy model is inseparable from Daml's deterministic, UTxO-like ledger model.** Sub-transaction privacy works because Daml combines deterministic execution, immutable contract consumption, explicit signatory/observer/controller roles, and Merkle projections: each party can verify its visible subtree without seeing the whole transaction. The EVM is deterministic at block execution level, but its mutable account/storage model, ambient block inputs, oracle patterns, and global state assumptions do not provide Canton's projection boundary. Transplanting the privacy mechanism requires redesigning the execution model or accepting a weaker privacy guarantee.

## 1.6 Key Facts

| Dimension | Detail |
|---|---|
| Production institutions | Goldman Sachs (GS DAP), HSBC (Orion), Nasdaq, Broadridge, DTCC, Citi, BNY Mellon, Bank of America |
| Ecosystem | 450+ projects/apps/validators on Canton Network |
| Monthly tokenization volume | $1.5–2T+ (Digital Asset sources, May 2026) |
| Codebase | 96% Scala, Apache-2.0 (community/base modules); Docker images carry restricted commercial license |
| GitHub | 114 stars, latest v3.5.1-rc3 (April 2026) |

## 1.7 Suggested Slides

**Slide C-1 — "The Privacy Problem Traditional Blockchains Cannot Solve"**
Main message: Every existing public or consortium blockchain requires all validators to see all transaction data. Canton eliminates the global ledger entirely — Goldman Sachs, HSBC, and DTCC settle on the same rail without seeing each other's books.

**Slide C-2 — "What Mantle Borrows and What It Cannot"**
Main message: Three portable patterns (Merkle projection, Observer/audit role, Synchronizer federation). Two non-portable elements (Daml runtime, full sub-transaction privacy guarantee). Mantle borrows Canton's privacy philosophy and adapts it to EVM.

---

# 2. Prividium (zkSync / Matter Labs)

## 2.1 One-Line Positioning

Prividium lets competing financial institutions settle transactions through cryptographic proof on a neutral layer (Ethereum) while keeping transaction data private from external and L1 observers — reducing counterparty trust without eliminating operator trust.

## 2.2 Core Architecture

Prividium is a private, permissioned Validium chain built on ZK Stack. Transaction data never leaves the operator's infrastructure; only a state root and STARK proof reach Ethereum.

```
┌──────────────────────────────────────────────────────────┐
│               ETHEREUM L1 (Settlement Layer)             │
│                                                          │
│  State Root + STARK Proof only (zero transaction data)   │
│  PrividiumTransactionFilterer: whitelist for L1→L2 txns  │
└─────────────────────────▲────────────────────────────────┘
                          │  STARK proof + state root
┌─────────────────────────┴────────────────────────────────┐
│                    ZKsync GATEWAY                        │
│  Aggregates proofs from multiple ZKsync chains           │
│  Shared settlement layer                                 │
└─────────────────────────▲────────────────────────────────┘
                          │  STARK proof + state root
┌─────────────────────────┴────────────────────────────────┐
│              PRIVIDIUM CHAIN (Private Validium)           │
│                                                          │
│  ┌──────────────┐     ┌──────────────┐                   │
│  │   DMZ Layer  │     │ Private Net  │                   │
│  │              │     │              │                   │
│  │  Proxy RPC   │◄────│  Sequencer   │                   │
│  │  - JWT auth  │     │  (ordering)  │                   │
│  │  - RBAC      │     │              │                   │
│  │  - 3-step    │     │  Prover Farm │                   │
│  │    verify    │     │  (GPU/CUDA)  │                   │
│  └──────────────┘     │              │                   │
│                       │  PostgreSQL  │                   │
│   IdP (Okta OIDC      │  + Blob Store│                   │
│    or SIWE wallet)    └──────────────┘                   │
└──────────────────────────────────────────────────────────┘
```

Access control operates at four layers: (1) Identity via Okta SSO or SIWE wallet, (2) Proxy RPC gateway with JWT validation + identity-to-wallet binding + function-level RBAC, (3) Contract-level permissions (all functions default to Forbidden), (4) L1 TransactionFilterer that blocks unauthorized forced L1→L2 deposits.

## 2.3 Core Design Principles

1. **ZK Validium: external privacy without sacrificing state-transition verifiability.** Transaction data stays off-chain with the operator; only state roots and STARK proofs reach Ethereum. The proof verifies correct state transitions, while data availability, operator visibility, and access-control enforcement remain governed by enterprise operations.

2. **Ethereum L1 as the neutral, cryptographic settlement anchor.** No institution controls the settlement layer. Public STARK verification makes state-transition correctness independently checkable on Ethereum; "the proof is the guarantee" applies to settlement validity, not to data availability, ordering fairness, or Proxy RPC permission enforcement.

3. **Multi-layer access control, default-closed.** Identity, gateway, contract-function RBAC, and L1 boundary defense form a four-layer, defense-in-depth permissioning model. All contract functions are Forbidden by default until explicitly authorized.

## 2.4 Inspiration for Mantle

1. **Closest L2/Validium architectural template.** Prividium demonstrates the complete pattern: off-chain DA for privacy, ZK proof for settlement correctness, Ethereum as neutral anchor. For Mantle's enterprise L2/L3 track, this is the most directly applicable blueprint.

2. **Proxy RPC gateway as enterprise middleware.** The single authenticated entry point enforcing JWT validation, identity-to-wallet binding, and function-level RBAC is a strong Mantle design pattern that can be rebuilt without protocol changes. The strategic point is that much of Prividium's enterprise value sits in middleware and operations, not only in the proving system.

3. **TransactionFilterer as L1 boundary defense.** The L1 contract filtering forced L1→L2 transactions solves a problem unique to L2 architectures: anyone can bypass the gateway via forced inclusion. Prividium's whitelist-based L1 contract is the direct pattern for modifying Mantle's OptimismPortal deposit contract.

## 2.5 Limitations and Non-Portability

1. **Deep dependency on ZK Stack and Matter Labs infrastructure.** The STARK proof system (Airbender), ZKsync Gateway, ZKsync Connect, and closed-source enterprise modules (Proxy RPC, Permissioning API, Admin Dashboard, Private Explorer) are all proprietary. Mantle cannot lift these components — it must build equivalents on OP Stack, including a GPU prover if cryptographic settlement is desired.

2. **Proof generation cost and operational complexity.** Running Airbender at production scale requires GPU prover farms (H100-class), specialized CUDA DevOps, and estimated $20K–$50K/month for high-throughput deployments. The three-tier deployment architecture and per-function permission configuration add ongoing operational overhead demanding a specialized team.

## 2.6 Key Facts

| Dimension | Detail |
|---|---|
| Institutional validation | 35+ financial institutions have validated the architecture |
| Cari Network | 5 US regional banks ($600B+ combined deposits), tokenized deposit network, production target late 2026 |
| BitGo | Institutional custody integration confirmed March 2026 |
| Deutsche Bank | Cited as partner (April 2026 blog); no independent DB-side confirmation |
| Proof system | STARK (no trusted setup, post-quantum secure); Airbender RISC-V + CUDA GPU prover |
| Performance claims | >15,000 TPS, 1-second ZK finality (Atlas upgrade, Oct 2025 — official claims) |
| Settlement | Ethereum mainnet via ZKsync Gateway; state root + STARK proof only |

## 2.7 Suggested Slides

**Slide P-1 — "Why Banks Can't Share Rails — and How ZK Proof Changes the Equation"**
Main message: Institutions need multi-bank settlement without trusting a rival's infrastructure. Prividium replaces organizational trust with STARK mathematical proof on Ethereum. The Cari Network (5 US banks, $600B deposits) is the proof-of-concept.

**Slide P-2 — "What Mantle Borrows: Middleware Patterns, Not ZK Stack Code"**
Main message: The Proxy RPC gateway, default-Forbidden permission model, and L1 TransactionFilterer are rebuildable Mantle patterns, with the gateway layer requiring no consensus change. The STARK proof system and ZKsync Gateway are not portable — they require a root architecture change from Optimistic to ZK proving.

---

# 3. Tempo Zones

## 3.1 One-Line Positioning

Tempo is a payment-first EVM blockchain combining sub-second deterministic finality on a compliant public L1 with optional private, compliance-enforced Zone sub-chains — eliminating the gas token volatility, throughput uncertainty, and compliance gaps that block institutional stablecoin adoption.

## 3.2 Core Architecture

Tempo is built on the Reth SDK (Paradigm's modular Rust Ethereum execution framework) with Commonware Simplex BFT consensus delivering ~600ms deterministic finality. Zones are validium sub-chains for enterprise privacy.

```
                      TEMPO L1 (Presto Mainnet, Chain ID 4217)
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────────────┐  │
│  │ System Lane │   │ General Lane │   │     Payment Lane       │  │
│  │ (protocol)  │   │ (contracts,  │   │ (TIP-20 transfers,     │  │
│  │             │   │  DeFi, DApps)│   │  guaranteed throughput, │  │
│  │             │   │  30M gas cap │   │  ~$0.001/transfer)     │  │
│  └─────────────┘   └──────────────┘   └────────────────────────┘  │
│                                                                    │
│  Commonware Simplex BFT  (~600ms deterministic finality)           │
│  BLS12-381 threshold signatures · DKG ceremonies                   │
│                                                                    │
│  TIP-20: Native stablecoin precompile (not a smart contract)       │
│  TIP-403: Compliance registry (whitelist/blacklist per token)      │
│  AccountKeychain: Root→access key delegation, spending limits      │
└─────────────────────────────┬──────────────────────────────────────┘
                              │  ZonePortal contract
                              │  (commitments only; no tx data on L1)
┌─────────────────────────────▼──────────────────────────────────────┐
│                  ZONE L2 (Privacy Validium)                        │
│                                                                    │
│  Single sequencer · No P2P · head = safe = finalized               │
│  ECIES encrypted deposits (recipient hidden, Chaum-Pedersen proof) │
│  Per-account RPC scoping                                           │
│  TIP-403 policy mirror from L1                                     │
│  Batch commitment → L1 (validity proof architecture ready,         │
│                         proof generation not yet live)              │
└────────────────────────────────────────────────────────────────────┘
```

The three-partition Payment Lane guarantees dedicated throughput for stablecoin transfers regardless of general-purpose chain load. Zones anchor to L1 via state commitments only — no transaction data is published on-chain.

## 3.3 Core Design Principles

1. **Payment-first block architecture with sub-second BFT finality.** The Payment Lane guarantees stablecoin throughput at <$0.001 per transfer regardless of chain load. Simplex BFT delivers ~600ms deterministic, zero-reorg finality for near-real-time settlement.

2. **Zone isolation for enterprise data sovereignty.** A Zone is a dedicated, sequencer-controlled validium sub-chain where no transaction data appears on L1. TIP-403 compliance rules travel with tokens across the bridge automatically.

3. **TIP-403 as a portable compliance policy framework.** Token issuers register whitelist/blacklist policies once on L1; every transfer on L1 and inside every Zone enforces these policies automatically at the protocol level.

## 3.4 Inspiration for Mantle

1. **Reth SDK lineage shared with potential Mantle L2/L3 builds.** Tempo demonstrates the full Reth NodeBuilder pattern — custom transaction types, precompile registries, dual-runtime consensus/execution isolation. This is a concrete reference for any Mantle migration from op-geth to a Reth-based execution client.

2. **BFT finality model as L1 track reference and Payment Lane as portable gas-lane blueprint.** Among the reviewed reference projects, Tempo is the clearest production-mainnet example of sub-second deterministic finality. Commonware/Simplex should still be treated as a design reference rather than a library to adopt directly. Payment Lane is portable as a blueprint, but OP Stack implementation would require txpool, payload builder, and L1 derivation changes; classification includes address-prefix rules plus selector/access-list constraints.

3. **Zone isolation as L3 template with portable building blocks.** The Zone architecture — L1-event-driven, single-sequencer validium, direct L1 state reads for compliance mirroring — is a lightweight template for enterprise privacy sub-chains. AccountKeychain scoped-key delegation and ECIES encrypted deposits are re-implementable with manageable engineering scope.

## 3.5 Limitations and Non-Portability

1. **Single-sequencer Zone model creates trust and liveness dependencies.** Each Zone has a single sequencer who sees all transaction plaintexts, controls ordering, and is the sole liveness provider. There is no current path to decentralized sequencing within the Zone architecture.

2. **Validity proofs are architecturally prepared but not yet production-complete.** The Zone batch submission contract has proof slots, precompiles are compiled `no_std` for SP1 compatibility, and verifier addresses are reserved — but current batches submit with empty proof bytes. Zone correctness depends entirely on sequencer honesty today.

## 3.6 Key Facts

| Dimension | Detail |
|---|---|
| Incubation | Paradigm + Stripe |
| Core team | Reth (Paradigm's Rust Ethereum client) and Foundry core developers |
| Mainnet | Presto chain (ID 4217) live; T3 hardfork activated April 27, 2026 |
| Testnet | Moderato (ID 42431), launched December 9, 2025 |
| Zone maturity | v0.1.0, testnet only, breaking changes expected |
| License | Apache 2.0 / MIT dual license |
| GitHub | 928 stars; 78.3% Rust; 26 L1 crates, 5 Zone crates |
| Design partners | Deutsche Bank, UBS, Standard Chartered, Mastercard, Visa, Stripe, Revolut, Shopify |

## 3.7 Suggested Slides

**Slide T-1 — "The Problem: General-Purpose Chains Cannot Be Payment Rails"**
Main message: Tempo fixes three institutional blockers: gas token volatility (replaced with USD stablecoin fees), probabilistic finality (replaced with ~600ms BFT finality), and compliance gaps (replaced with protocol-enforced TIP-403 policy registry).

**Slide T-2 — "What Mantle Takes From Tempo (and What It Cannot)"**
Main message: Three portable elements: Reth SDK customization pattern, Payment Lane gas-partition design, Zone isolation as L3 template. Two cautions: Commonware Simplex BFT is a single-production-user library (design reference only), and Zone validity proofs are not yet live.

---

# 4. Paladin (LFDT Labs / Linux Foundation)

## 4.1 One-Line Positioning

Paladin enables regulated institutions to conduct confidential, compliance-verified transactions on unmodified EVM networks without forking the chain — adding programmable privacy as a sidecar layer rather than a protocol change.

## 4.2 Core Architecture

Paladin deploys as a sidecar process alongside an unmodified EVM node (Hyperledger Besu). It manages private state off-chain and submits only opaque `bytes32` commitments to the base ledger. For Mantle, this sidecar pattern is evaluated but not recommended as the primary path; WHI-382 recommends MPL as a separate Besu/QBFT privacy network.

```
┌──────────────────────────────────────────────────────────────────┐
│  LAYER C — Private EVM / Pente (Privacy Groups)                  │
│  Full Solidity programmability within isolated privacy worlds    │
│  [Ephemeral in-memory Besu EVM instances per transaction]        │
├──────────────────────────────────────────────────────────────────┤
│  LAYER B — Private TX Manager / Sidecar (Paladin Runtime)        │
│  UTXO state store · Distributed sequencer · Domain plug-points   │
│  [Go + Java process running alongside unmodified Besu node]      │
├──────────────────────────────────────────────────────────────────┤
│  LAYER A — Base EVM Ledger (Hyperledger Besu, unmodified)        │
│  On-chain ZKP verification · Nullifiers · Notary certificates    │
│  [Only opaque bytes32 state hashes ever touch the chain]         │
└──────────────────────────────────────────────────────────────────┘

     ┌─────────┐       ┌──────────┐       ┌──────────────┐
     │  Noto   │       │   Zeto   │       │    Pente     │
     │ Domain  │       │  Domain  │       │   Domain     │
     │         │       │          │       │              │
     │Notarized│       │  ZKP     │       │ Private EVM  │
     │ Tokens  │       │  Tokens  │       │   Groups     │
     └────┬────┘       └────┬─────┘       └──────┬───────┘
          │                 │                     │
          └─────────────────┼─────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Atom/Factory  │
                    │  Cross-domain  │
                    │  atomic settle │
                    └────────────────┘
```

Universal UTXO state model: every private state (token balance, account slot, lock record) is stored as an unspent output with a `bytes32` hash on-chain. Full data retained exclusively by authorized parties off-chain.

## 4.3 Three Privacy Domains

**Noto (Notarized Tokens):** Confidential UTXO model backed by a trusted notary. The chain stores only opaque state ID hashes. Supports Basic mode (standalone notary) and Hooks mode (compliance logic delegated to a Pente smart contract with 13 callbacks including KYC/AML). Full lock lifecycle (`createLock` → `delegateLock` → `spendLock`) enables two-phase commit for DvP workflows. Best for regulated token issuance where the issuer acts as notary.

**Zeto (ZKP Tokens):** Zero-knowledge transfers using Groth16 proofs, BabyJubJub curves, and Poseidon hashing. Eleven token variants from basic anonymity to full-stack privacy with encrypted amounts, nullifiers, and native KYC membership proofs. KYC is proven in zero-knowledge: the ZK circuit proves the transactor's public key is a member of an on-chain identities Sparse Merkle Tree without revealing the identity. The `Qurrency` variant adds ML-KEM (CRYSTALS-KYBER) post-quantum key encapsulation inside the circuit. Best for privacy-first scenarios requiring regulatory attestation without identity disclosure.

**Pente (Private EVM):** Full Solidity programmability within Privacy Groups. Each participating node runs an ephemeral in-memory Besu EVM, re-executes the private transaction, and signs an EIP-712 endorsement. The chain records only endorsement signatures and opaque state IDs. Current: 100% group consensus; contract layer supports configurable M-of-N for future use. `externalCalls` allow private execution to atomically trigger public base-layer contract calls. Best for complex multi-party business logic requiring full EVM programmability under confidentiality.

**Atom / AtomFactory:** Cross-domain atomic settlement via EIP-1167 minimal-proxy factory. `Atom.execute()` runs all legs atomically in one base-layer transaction — any leg revert cancels all. Enables DvP between heterogeneous privacy models (e.g., Noto bond + Zeto cash) in a single chain transaction.

## 4.4 Core Design Principles

1. **Sidecar non-invasiveness.** Connects to any unmodified EVM node via standard JSON-RPC. No protocol fork, no consensus modification, no custom block processing. Compatible with public L1/L2 and permissioned networks equally.

2. **Pluggable privacy domains.** Privacy mechanisms are modular gRPC plugins. Noto, Zeto, and Pente coexist on one runtime. Different trust models (trusted-party, ZKP, full-consensus group) are first-class options, not configurations.

3. **Cross-domain atomicity via Atom.** A single on-chain transaction can span multiple heterogeneous privacy domains. All-or-nothing execution is enforced at the EVM level — no coordination gap between settlement legs.

## 4.5 Inspiration for Mantle

1. **Zeto's KYC membership proof pattern.** Embedding compliance proof inside the ZK circuit — proving KYC membership without revealing identity — is directly adoptable for Mantle's enterprise products and any scenario requiring regulatory attestation without disclosure.

2. **MPL as standalone privacy product.** Paladin's architecture demonstrates that enterprise privacy infrastructure is best launched as an independent permissioned network (Besu + QBFT) rather than bolted onto an existing L2. This validates the Mantle Privacy Layer product concept with 88% open-source component reuse.

3. **Atom pattern for cross-domain DvP.** The `AtomFactory` + lock/delegate/spend workflow is a reusable blueprint for multi-asset settlement across heterogeneous privacy contexts — directly applicable to RWA tokenization, securities DvP, and cross-currency payment on MPL.

## 4.6 Limitations and Non-Portability

1. **Better suited as standalone product than Mantle L2 core component.** WHI-382 evaluated two approaches: L2 Sidecar integration (20/30 score, 3 critical blockers, 60–70% feature coverage, 3–6 months) versus MPL standalone network (26/30 score, zero blockers, 100% feature coverage, 2–4 months). The Sidecar path faces block confirmation semantic mismatch, ZKP calldata L1 rollup fees at scale (~$0.67/proof without batching), and DA migration uncertainty.

2. **Pente's Java/Besu EVM dependency creates an L2 integration blocker.** Pente embeds Besu EVM as a Java library. Mantle L2 uses op-geth (Go). Running Pente as a sidecar to op-geth requires non-trivial investigation; the JVM dependency adds 15–30 person-days. On MPL (native Besu), this issue disappears.

## 4.7 Key Facts

| Dimension | Detail |
|---|---|
| Governance | LFDT Labs (Linux Foundation Decentralized Trust) / Kaleido (commercial backer) |
| License | Apache 2.0 |
| Real-world deployment | Project Guardian Wholesale Network (major banks) |
| WHI-382 recommendation | MPL (standalone): 26/30 vs. Sidecar 20/30; zero critical blockers; 2–4 month MVP |
| Recommended stack | Hyperledger Besu + QBFT permissioned consensus |
| Languages | Go (core, Noto/Zeto) + Java (Pente/Besu EVM) + TypeScript (SDK) |
| Deployment | Kubernetes Operator with CRDs; one-command devnet |
| Architecture maturity | 8/10 — production-viable with standard hardening |

## 4.8 Suggested Slides

**Slide Pa-1 — "Privacy as Infrastructure, Not Protocol Change"**
Main message: Paladin adds programmable confidentiality to any unmodified EVM chain via a sidecar. Three privacy domains (Noto, Zeto, Pente) + Atom cross-domain settlement. No fork required.

**Slide Pa-2 — "One Framework, Three Trust Models"**
Main message: Noto for notary-controlled regulated issuance. Zeto for ZKP privacy with built-in KYC membership proofs. Pente for full Solidity programmability within private consensus groups. Atom connects them atomically for DvP.

**Slide Pa-3 — "MPL: Open-Source Foundation, 88% Reuse"**
Main message: WHI-382 recommends deploying Paladin as the Mantle Privacy Layer — standalone Besu/QBFT network. MPL score 26/30 vs. Sidecar 20/30; 2–4 months to MVP; zero critical blockers.

---

# 5. Summary Comparison Table

| Dimension | Canton | Prividium | Tempo Zones | Paladin |
|---|---|---|---|---|
| **Architecture paradigm** | Participant-Synchronizer coordination protocol; no global ledger | ZK Validium on ZK Stack; off-chain DA + STARK proofs to Ethereum | Payment-optimized L1 (Reth SDK + BFT) + Validium Zone L2 | Sidecar on unmodified EVM (Besu); UTXO state model |
| **Privacy model** | Sub-transaction Merkle DAG projection; each party sees only its slice | Validium: all transaction data off-chain; only state root + proof on L1 | Zone: no tx data on L1; ECIES encrypted deposits; per-account RPC scoping | Three pluggable domains: notary (Noto), ZKP (Zeto), private EVM groups (Pente) |
| **Compliance approach** | Daml contract-level Signatory/Observer/Controller roles | Proxy RPC RBAC + L1 TransactionFilterer; all functions default-Forbidden | TIP-403 protocol-level compliance registry; policies mirror into Zones | Zeto KYC membership proofs in ZK; Noto hooks for KYC/AML callbacks |
| **EVM compatibility** | None — Daml/Scala only | Full EVM (Solidity/Hardhat/Foundry) | Full EVM (Reth-based) | Full EVM (sidecar model; Besu base layer) |
| **Finality** | Mediator 2PC verdict (seconds) | ~1s ZK finality claim; Ethereum L1 settlement via STARK proof | ~600ms deterministic BFT (L1); Zone finality bound to L1 | Base layer finality (Besu QBFT: seconds) |
| **Relevance to Mantle L2 path** | Design inspiration only (Merkle projection, Observer hooks) | **Closest template** — Validium DA, Proxy RPC, and TransactionFilterer are rebuildable patterns | Zone isolation as L3 template; Payment Lane is an OP Stack engineering blueprint | MPL as standalone privacy product; Zeto KYC proofs adoptable |
| **Relevance to Mantle L3 path** | Synchronizer federation maps to multi-L3 model | Validium DA model applicable per-L3 | **Direct template** — Zone-like L3 validium with compliance mirroring | Atom pattern for cross-L3 settlement |
| **Relevance to Mantle L1 path** | Privacy projection philosophy | Not directly relevant (L2 architecture) | **Clearest reviewed BFT finality reference** — Reth SDK + Simplex BFT validates the design pattern | Not directly relevant (sidecar model) |
| **Key limitation for Mantle** | Non-EVM; no code reuse path | Proprietary ZK Stack dependency; GPU prover costs | Single-sequencer Zone trust; validity proofs not yet live | Better as standalone MPL than L2 integration (3 critical blockers on Sidecar) |

---

# 6. What This Means for Mantle's Layer Path Decision

Each reference project illuminates a different dimension of the enterprise blockchain design space:

**Canton** proves that the deepest privacy (sub-transaction, need-to-know) is achievable — but only at the cost of abandoning EVM. This establishes EVM compatibility as a hard constraint for Mantle and frames the privacy design challenge: how close can we get to Canton-grade privacy while remaining EVM-native?

**Prividium** provides the closest architectural blueprint for Mantle's L2/Validium enterprise track. Its Proxy RPC gateway, default-Forbidden RBAC, and L1 TransactionFilterer are rebuildable patterns, with the gateway layer especially relevant because it can sit in front of existing chain infrastructure. Its STARK settlement narrative ("settled on Ethereum") is the strongest regulatory credibility claim in the market, but only for state-transition validity; DA, ordering, and permission enforcement still depend on enterprise operations. The ZK proving infrastructure remains ZK Stack-proprietary.

**Tempo Zones** validates the L1 and L3 tracks simultaneously. For L1: among the reviewed references, it is the clearest production-mainnet example of sub-second deterministic finality on an EVM chain, using the Reth SDK lineage Mantle could adopt in a future Reth/op-reth path. For L3: its Zone architecture is a lightweight, compliance-aware validium sub-chain template. The Payment Lane demonstrates a dedicated-throughput design pattern that Mantle could reproduce with txpool, builder, and derivation changes.

**Paladin** demonstrates that enterprise privacy infrastructure delivers maximum value as a standalone product (MPL) rather than a bolted-on L2 integration. Its Zeto KYC membership proof pattern and Atom cross-domain settlement are directly adoptable open-source building blocks. The WHI-382 recommendation (MPL: 26/30, zero blockers, 2–4 month MVP) positions Paladin as the fastest path to a shippable enterprise privacy product under the Mantle brand.

**The composite lesson**: No single reference project provides a complete enterprise blockchain solution. Mantle's strategy should borrow Canton's privacy philosophy, Prividium's middleware patterns, Tempo's finality and Zone architecture, and Paladin's privacy domains — assembling them into a phased composite strategy (L2 → L3 → L1) tailored to Mantle's specific market position and resource constraints.
