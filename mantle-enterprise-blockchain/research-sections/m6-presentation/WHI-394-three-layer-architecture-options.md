# WHI-394: Three Layer Architecture Options
## L1 / Enterprise L2 / Enterprise L3
- **Milestone**: M6 — Decision-Layer Presentation & Three-Path Selection
- **Date**: 2026-05-12
- **Status**: Draft
- **Inputs**: WHI-387 (L1), WHI-388 (L2), WHI-389 (L3), WHI-390 (Report), WHI-364 (Fork Analysis), WHI-391 (Narrative)

---

## Framing: Three Products, Not a Maturity Ladder

These three paths are **different products for different buyers**. The question is not "which is best" — it is "which buyer does Mantle want to serve first."

| | Sovereign L1 | Enterprise L2 | Enterprise L3 |
|---|---|---|---|
| **One-line pitch** | "You own the infrastructure" | "Fastest credible enterprise chain" | "One enterprise, one chain" |
| **Buyer profile** | Financial consortia, sovereign settlement | RWA issuers, institutional pilots, enterprise DeFi | Enterprise SaaS, private registries, bank ledgers |
| **Core promise** | Deterministic sub-second hard finality + full protocol sovereignty | Ethereum/Mantle alignment + production in 8–12 months | Tenant-level data isolation + scalable delivery model |
| **Cost / Timeline** | 15–25 people · 18–24 months · $5M–$12M engineering + audits/integration | 8–15 people · 8–12 months | 10–15 people · 9–13 months |

---

# Path A: Self-Built Enterprise L1 — The Sovereignty Path

## A.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Enterprise Applications                    │
│         RWA  ·  xStocks  ·  Payment  ·  Treasury             │
├─────────────────────────────────────────────────────────────┤
│                    Business Components                        │
│    MIP-20/21  ·  DVP Module  ·  Payment Lane  ·  Travel Rule │
├────────────┬────────────┬────────────┬──────────────────────┤
│  RWA Zone  │ xStocks    │  Payment   │  Custom Zones ...    │
│  (Private  │  Zone      │  Zone      │  (Per-enterprise     │
│   DA, own  │ (Dark pool │ (>10K TPS, │   sequencer, own     │
│   policy)  │  privacy)  │  stable    │   compliance)        │
│            │            │  fees)     │                      │
├────────────┴────────────┴────────────┴──────────────────────┤
│              Execution: Reth SDK + revm + Enterprise         │
│              Precompiles (Identity, Policy, ECIES, BLS)      │
├─────────────────────────────────────────────────────────────┤
│           Compliance & Identity Layer                        │
│   KYC/KYB Registry · Policy Registry · Selective Disclosure  │
├─────────────────────────────────────────────────────────────┤
│           Consensus: Permissioned BFT Validators             │
│     Commonware Simplex · BLS12-381 Threshold Certificates    │
│           VRF Leader Election · HSM-backed Keys              │
├──────────────┬──────────────────────────────────────────────┤
│  Public Data │  Private Zone DA   │  Audit Archive           │
│  (mainchain) │  (institution-     │  (immutable, scoped     │
│              │   controlled)      │   regulator access)     │
├──────────────┴──────────────────────────────────────────────┤
│        Optional Ethereum Anchor (ZK Verifier + Bridge)       │
│        State commitments · STARK proofs · Asset bridge       │
└─────────────────────────────────────────────────────────────┘
```

**Key architectural principle:** Ethereum is a bridge and optional assurance layer — not a runtime dependency. Ordinary block production and finality operate independently via BFT consensus. Each Zone is a physically isolated execution environment with its own state, sequencer, DA backend, RPC endpoints, participants, compliance rules, and data retention policy.

## A.2 What Enterprise Problems It Solves

Institutions requiring **legally binding, sub-second deterministic settlement** cannot accept soft confirmations or multi-day challenge windows. The L1 path delivers BFT hard finality (~600ms–2s) where the confirmation IS the settlement — no waiting for proofs, no challenge periods, no dependency on external chain congestion. This is the only path that provides protocol-level compliance enforcement at every layer (RPC, mempool, execution, token transfer, bridge), making bypass paths architecturally constrained and strongly minimized rather than merely policy-discouraged.

## A.3 Core Capabilities & Technology Composition

- **Consensus**: Permissioned BFT (Commonware Simplex candidate) with BLS12-381 threshold certificates, VRF leader election, HSM-backed validator keys
- **Execution**: Reth SDK + revm, EVM-compatible with enterprise precompiles (IdentityRegistry, PolicyRegistry, ComplianceCheck, ECIES, Chaum-Pedersen, BLS verification)
- **Multi-Zone isolation**: Each enterprise/product gets dedicated execution environment, private DA, compliance rules, data residency settings
- **Payment Lane**: 3-channel block model (System > Payment > General) with consensus-enforced gas budgets, targeting >10,000 TPS for payment workflows
- **Block-STM parallel execution**: Optimistic parallel execution with read/write set conflict detection
- **Sub-transaction privacy**: Canton-inspired per-party ledger views for multi-party RWA transactions
- **Zone privacy trust model**: Phase 1 Zones can isolate data from public observers, but Zone sequencers/operators may still have plaintext visibility until later proof, threshold encryption, or operator-blind privacy phases
- **Selective disclosure**: ZK proofs for accredited status, sanctions clearance, Travel Rule, balance thresholds — without exposing PII
- **Custom transaction types**: Account Abstraction, Compliance Transactions, Privacy Deposit (ECIES-encrypted), Governance Transactions
- **MIP-20/21 compliant tokens**: Built-in transfer authorization hooks; cannot move via unauthorized paths
- **Tiered finality**: BFT cert (~600ms–2s) → ZK proof (5–30 min) → Ethereum L1 anchor (optional higher assurance)

## A.4 Best-Fit Customer / Business Scenarios

| Scenario | Why L1 Fits |
|---|---|
| Bank consortia / interbank settlement | Known validators with legal agreements; BFT governance maps to consortium governance |
| Securities settlement / DVP (T+0) | Deterministic hard finality is the confirmation — no waiting for proof windows |
| xStocks trading venues | Sub-second finality + dark pool privacy + market compliance controls |
| B2C stablecoin payments | >10,000 TPS Payment Lane with predictable fees and terminal-speed confirmation |
| Cross-border payment networks | Data sovereignty per jurisdiction via Zone isolation + SWIFT ISO 20022 adapters |
| Regulated custodians owning infrastructure | Must own validator keys, sequencing, incident response — not be tenants |

## A.5 Greatest Advantage

**Sub-second deterministic hard finality with full protocol sovereignty.** The BFT certificate IS the settlement. No soft confirmation → proof → challenge → finality pipeline. For payment terminals, securities DVP, and real-time treasury operations, this eliminates the finality uncertainty that makes L2/L3 paths structurally unsuitable.

## A.5b Cost & Timeline Breakdown

| Phase | Duration | Team | Key Deliverables |
|---|---|---|---|
| Phase 1: Core Execution + Consensus MVP | 6–9 months | 9–15 | Reth SDK node, BFT testnet, custom tx types, initial precompiles, validator lifecycle |
| Phase 2: Privacy, Compliance, First Zone | 6–9 months | 15–25 | ZoneFactory, ZonePortal, ECIES, IdentityRegistry, PolicyRegistry, Travel Rule MVP |
| Phase 3: Business Components + Audits | 6 months | 19–25 | MIP-20/21, DVP, Payment Lane, ZK bridge, Ethereum anchor, SDK, full audits |
| **Total** | **18–24 months** | **15–25** | Production candidate with audited bridge + first enterprise use case |

| Cost Item | Estimate |
|---|---|
| Engineering salaries (18–24 months) | $5M–$12M |
| Security audits (consensus, precompiles, bridge, ZK) | $850K–$1.7M+ |
| Bug bounty reserve | $1M+ |
| Enterprise integration (ERP, SWIFT, KYC, Travel Rule) | $1M–$3M |
| Monthly infrastructure (initial) | ~$85K–$130K |
| Monthly infrastructure (scaled) | $160K–$300K+ |
| Long-term operations team | 16–22 people |

## A.6 Greatest Risk

**Cost, full security responsibility, and execution complexity with unvalidated demand.** 15–25 engineers for 18–24 months at $5M–$12M engineering cost (before $850K–$1.7M in audits, $1M+ bug bounty, $1M–$3M enterprise integration). Mantle would own validator security, consensus failures, bridge exploits, incident response, and long-term protocol operations. Building the full stack — execution, consensus, privacy, compliance, ZK proofs, bridge, SDK — before confirming an anchor client creates a platform without validated product-market fit.

## A.7 Greatest Unknown

**Whether Commonware/Simplex BFT is production-ready for regulated financial infrastructure.** It has promising architecture but limited independent production diversity (only one confirmed reference: Tempo). A formal technology gate — testnet PoC with realistic validator count, Zone load, and failure injection — is required before full commitment.

## A.8 When to Choose / When NOT to Choose

**Choose L1 when:**
- Hard business settlement must complete within 1–2 seconds (payment terminal, DVP, real-time collateral)
- Compliance must be protocol-enforced across RPC, mempool, execution, token transfer, and bridge controls — not app-level opt-in
- Sensitive data must never enter public DA or Ethereum blobs
- Data must reside in institution/jurisdiction-controlled infrastructure with deletion rights
- A large consortium is willing to co-invest and participate as validators
- Program can fund 18–24 months of protocol + security + operations work

**Do NOT choose L1 when:**
- Soft confirmation in 1–3 seconds is acceptable for business operations
- Ethereum Rollup security inheritance is strategically required
- Pilot needed within 3–6 months
- Team is <15 senior protocol engineers
- No committed anchor partner has validated demand
- DeFi composability with public Mantle is a primary product value

---

# Path B: Mantle Enterprise L2 — The Fastest Credible Production Path

## B.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Enterprise Applications                      │
│      RWA Issuance · Institutional DeFi · Custodian Ops       │
├─────────────────────────────────────────────────────────────┤
│              Authenticated RPC Gateway                        │
│        OIDC / SAML / JWT / mTLS · Wallet Binding             │
├─────────────────────────────────────────────────────────────┤
│              Enterprise Sequencer                             │
│   Admission Filters · Policy Engine · KYT/AML Hooks          │
│   Transaction Ordering · Batch Submission · Audit Events      │
├───────────────────────┬─────────────────────────────────────┤
│   Execution Client    │   Identity & Compliance Registry     │
│   (op-geth +          │   IdentityRegistry (KYC/KYB)        │
│    enterprise         │   ComplianceRegistry (sanctions)     │
│    predeployments)    │   PolicyExecutor (transfer hooks)    │
│                       │   ERC-3643/T-REX support             │
├───────────────────────┴─────────────────────────────────────┤
│              Data Availability (Hybrid Routing)               │
│   Public blobs ←→ Private DA / Validium (encrypted off-chain)│
├─────────────────────────────────────────────────────────────┤
│              Enterprise Bridge (Compliance-Filtered)          │
│   EnterpriseOptimismPortal · Deposit/Withdrawal Whitelist    │
├──────────┬──────────────────────────────────────────────────┤
│          │         ↕ Controlled Interop Bridge                │
│ Ethereum │    ┌──────────────────────────┐                   │
│    L1    │    │    Public Mantle L2       │                   │
│(Settlement│   │  (DeFi · Liquidity · MNT) │                   │
│ + Proofs)│    └──────────────────────────┘                   │
└──────────┴──────────────────────────────────────────────────┘
```

**Key architectural principle:** Enterprise L2 is a standalone permissioned chain running *parallel* to public Mantle — not inside it. It shares the OP Stack technology, operational knowledge, and Ethereum settlement layer, but has its own chain ID, Sequencer, state, and compliance model. The Sequencer is the central compliance control point: admission, KYT, sanctions filtering, and audit are structurally zero-cost on a centralized sequencer.

**Honest constraint:** Tenants are guests on Mantle-operated infrastructure. The Sequencer has default plaintext visibility over all transaction data. Soft confirmation ≠ legal hard settlement.

## B.2 What Enterprise Problems It Solves

Enterprises that need **compliant Ethereum-aligned infrastructure quickly** — without operating their own validator network, consensus protocol, or wallet ecosystem — get a production-ready EVM chain with identity checks, sanctions screening, private DA, audit logs, and a bridge to public Mantle/Ethereum DeFi liquidity. The OP Stack reuse means operational patterns (Sequencer, batcher, proposer, monitoring) are battle-tested, not greenfield.

## B.3 Core Capabilities & Technology Composition

- **Chain foundation**: Mantle/OP Stack derivative (op-node, op-geth) with separate chain ID and enterprise configuration
- **Access control**: Authenticated RPC (OIDC/SAML/JWT/mTLS), wallet binding, role-based query scoping
- **Sequencer compliance**: Pre-execution filtering for KYC level, sanctions (OFAC/EU/UN), KYT risk scoring, jurisdiction checks
- **Identity layer**: Predeployed IdentityRegistry (KYC/KYB binding), ComplianceRegistry, PolicyExecutor with on-chain transfer hooks
- **Token standards**: ERC-3643/T-REX compliant asset framework, ERC-4337 account abstraction
- **Private DA**: Hybrid routing — public blobs for non-sensitive data, encrypted off-chain Validium storage for sensitive transactions
- **Selective disclosure**: View keys, auditor APIs, regulator export workflows, immutable audit hashes
- **Bridge**: EnterpriseOptimismPortal with deposit/withdrawal whitelist blocking non-compliant L1-initiated transactions
- **Settlement**: State roots + proofs + commitments anchored to Ethereum L1
- **Finality profile**: ~1–2s Sequencer soft confirmation → ~15–30 min ZK validity proof (target) → 7-day optimistic fallback
- **Advanced privacy (roadmap)**: TEE Sequencer, encrypted mempool, threshold decryption, client-side encryption

## B.4 Best-Fit Customer / Business Scenarios

| Scenario | Why L2 Fits |
|---|---|
| RWA tokenization / fund distribution | EVM + ERC-3643 + Ethereum settlement narrative + bridge to DeFi liquidity |
| Institutional sandbox / pilot | Fastest path to production; clear SLA; limited asset scope; rollback plan |
| Custodian digital asset network | Familiar EVM/custody workflows + wallet compatibility + policy registry |
| Enterprise DeFi venue | Permissioned participants + Sequencer fairness + KYT + market surveillance |
| Stablecoin / payment with moderate finality needs | Soft confirmation sufficient for UX; hard settlement deferred to proof window |
| Crypto-native RWA issuers | Value EVM, liquidity, speed; Ethereum settlement is the sales narrative |

## B.4b Cost & Timeline Breakdown

| Phase | Duration | Team | Key Deliverables |
|---|---|---|---|
| Phase 1: Enterprise L2 MVP | 0–4 months | 8–10 | Chain bootstrap, authenticated RPC, Sequencer policy engine, bridge compliance, identity registry, audit foundation |
| Phase 2: Privacy + Execution Extension | 4–8 months | 10–13 | Hybrid DA router, private DA service, privacy tx envelopes, selective disclosure, execution extensions |
| Phase 3: Business Components + Onboarding | 8–12 months | 12–15 | ERC-3643/T-REX templates, DVP module, finality oracle, Travel Rule, enterprise SDK, governance |
| **Total** | **8–12 months** | **8–15** | Production-ready enterprise L2 with compliance and private DA |

Cost is significantly lower than L1 due to OP Stack reuse: no new validator network, consensus protocol, wallet ecosystem, or explorer required. Primary cost drivers are engineering salaries, private DA infrastructure, security audits for bridge and policy contracts, and enterprise integration.

## B.5 Greatest Advantage

**Fastest credible production path with Ethereum settlement narrative.** Phase 1 enterprise access MVP achievable in 3–4 months. Full production in 8–12 months. Reuses Mantle's existing Sequencer operations, batcher, DA, proving pipeline, bridge patterns, monitoring, and incident response runbooks. Enterprises can tell stakeholders the system has public Ethereum settlement and verifiability — not just a private database.

## B.6 Greatest Risk

**Operator trust is a structural constraint, not an interim shortcoming.** The Sequencer sees all transaction data in plaintext by default. Enterprises cannot independently sequence transactions, recover the chain, or change protocol rules. This is tenant vs. owner — contracts and SLAs can reduce concerns but cannot eliminate them. For institutions where "our core business runs on someone else's chain" is a board-level blocker, no amount of contractual engineering resolves the structural architecture.

## B.7 Greatest Unknown

**Whether regulated financial institutions will accept Mantle as a chain operator for production workloads.** The Sequencer's operational role — transaction ordering, data visibility, batch submission, emergency powers — creates potential regulatory actor status across jurisdictions. The legal liability matrix (who is responsible when compliance filtering fails, freezes assets, or misroutes data) has no market precedent at scale.

## B.8 When to Choose / When NOT to Choose

**Choose L2 when:**
- Ethereum/Mantle alignment, EVM tooling, and a credible product in 8–12 months matter more than maximum sovereignty
- The use case is RWA issuance, enterprise DeFi, compliant asset distribution, or custodian-integrated products
- The customer accepts "Mantle operates the chain" under contractual SLA, audit rights, and exit plan
- Public Mantle/Ethereum DeFi liquidity access is a product differentiator
- Soft Sequencer confirmation is sufficient for UX; hard settlement can be deferred
- Speed and cost matter: OP Stack reuse is faster and cheaper than a new L1

**Do NOT choose L2 when:**
- The enterprise requires full control of sequencing, finality, and data plane
- Sub-second deterministic hard finality is required (payment-grade DVP, securities T+0)
- Operator-blind transaction processing is non-negotiable (order flow must be invisible to infrastructure)
- Canton-style need-to-know sub-transaction privacy is required
- Regulatory regime prohibits engaging a third-party processor for core infrastructure
- Each tenant needs isolated execution with independent recovery — route to L3

---

# Path C: Enterprise L3 App Chain — The Tenant Sovereignty Product Path

## C.1 Architecture Overview

```
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Bank A  │  │ RWA     │  │ Payment │  │ Custom  │
│ L3      │  │ Issuer  │  │ Proc.   │  │ L3 ...  │
│         │  │ L3      │  │ L3      │  │         │
│ Own     │  │ Own     │  │ Own     │  │ Own     │
│ Sequencer│  │ Sequencer│  │ Sequencer│  │ Sequencer│
│ Own DA  │  │ Own DA  │  │ Own DA  │  │ Own DA  │
│ Own     │  │ Own     │  │ Own     │  │ Own     │
│ Policy  │  │ Policy  │  │ Policy  │  │ Policy  │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
     │            │            │            │
     └────────────┴─────┬──────┴────────────┘
                        │  State roots, proofs,
                        │  withdrawal hashes,
                        │  bridge messages
                        ▼
┌─────────────────────────────────────────────────┐
│              Mantle L2 (Settlement Hub)           │
│  ZonePortal Contracts · Proof Verification        │
│  Cross-L3 Relay · Shared Liquidity Pools          │
│  Compliance Routing · SDK / Templates             │
├─────────────────────────────────────────────────┤
│  State root + proof submission to Ethereum L1     │
└─────────────────────┬───────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────┐
│              Ethereum L1 (Final Anchor)           │
│  L2 State Root Verification · Asset Exits         │
│  Public Settlement Guarantee                      │
└─────────────────────────────────────────────────┘
```

**Key architectural principle:** One enterprise = one L3 chain. Each client operates a dedicated chain instance with its own sequencer, full nodes, private DA storage, authenticated RPC, compliance policies, governance keys, and upgrade cadence. Mantle L2 serves as the shared settlement layer, liquidity hub, proof coordinator, and SDK/framework provider. Ethereum L1 is the final external settlement anchor.

**Honest constraint:** External hard finality is bounded by the L3 → L2 → L1 chain. Cross-zone atomicity requires explicit design, not assumption. The product can feel fast (~1–2s soft confirmation) while settlement is slow (~1 hour ZK, 7 days optimistic fallback).

## C.2 What Enterprise Problems It Solves

Enterprises that need **their own controlled environment** — with chain-level data isolation, independent compliance policies, and operator sovereignty — without building an entire L1 from scratch. Each tenant gets clean separation: one tenant's data, mempool, compliance policy, and upgrade schedule never touches another's. Meanwhile, they retain access to Mantle L2 liquidity and Ethereum settlement when needed.

## C.3 Core Capabilities & Technology Composition

- **Per-enterprise chain**: Dedicated L3 with independent sequencer, full nodes, private DA, authenticated RPC, monitoring, audit exports
- **Enterprise-controlled isolation**: Execution params, allowed contracts, gas model, policy hooks, sequencing strategy, DA mode, access rules, governance keys, upgrade timing
- **Private DA**: Validium-style — transaction data stored in enterprise-controlled DB or DAC, never published to Mantle/Ethereum
- **Authenticated RPC**: JWT/SIWE/mTLS with role-scoped read/write access
- **Configurable compliance**: Per-chain IdentityRegistry, PolicyRegistry, KYC/KYB thresholds, sanction hooks, ERC-3643 support, Travel Rule metadata
- **Sequencer-as-compliance-officer**: Pre-execution filtering for KYC, sanctions, jurisdiction, asset eligibility
- **Typed finality API**: Six explicit finality labels from L3_SOFT_CONFIRMED through L1_FINAL_EXIT
- **Bridge to Mantle L2**: ZonePortal contracts for DeFi liquidity access while keeping core workflows private
- **Chain templates**: Pre-built configurations for RWA, xStocks (non-HFT), Payment, Enterprise Sandbox, Public DeFi
- **GDPR-compatible**: Logical erasure by key destruction, physical purge of off-chain DA after retention window
- **Per-zone independent upgrades**: One client's requirements don't force others to upgrade
- **Roadmap**: Encrypted mempool (Phase 2), shared sequencer for cross-zone DVP (Phase 3)

## C.4 Best-Fit Customer / Business Scenarios

| Scenario | Why L3 Fits |
|---|---|
| Bank internal tokenized deposit ledger | Bank controls sequencer, private DA, identity, audit, and policy independently |
| RWA issuer with private investor registry | Issuer-specific chain maps to issuer-specific compliance and data retention |
| Payment processor (merchant/customer partitions) | High TPS, private flows, Travel Rule metadata, controlled API |
| Enterprise SaaS serving regulated tenants | Per-tenant L3 = clean legal and data separation |
| Small consortium pilot (few institutions) | DAC/shared sequencer can be added as trust matures |
| B2B settlement (soft finality + economic guarantee acceptable) | Counterparties with contractual relationships accept provisional settlement |

## C.4b Cost & Timeline Breakdown

| Phase | Duration | Key Deliverables |
|---|---|---|
| Phase 1: L3 SDK + First Instance | 4–6 months | Chain template, ZonePortal contracts, private DA v1, authenticated RPC, sequencer policy engine, first pilot L3 |
| Phase 2: Privacy + Compliance Toolkit | 3–4 months | IdentityRegistry, PolicyRegistry, ERC-3643 factory, Helm/Terraform automation, DA hardening |
| Phase 3: Cross-L3 Interop + Production | 2–3 months | Cross-zone relay, shared sequencer prototype, ZK proof roadmap, first 1–3 production customers |
| **Total** | **9–13 months** | Credible enterprise L3 platform MVP |

| Per-Zone Annual Cost | DA Mode | Annual Estimate |
|---|---|---|
| RWA Zone | Validium | $60K–$180K |
| xStocks Zone | Validium, higher TPS | $180K–$600K |
| Payment Zone | Validium | $60K–$240K |
| Multi-zone platform total | Mixed | ~$355K–$1.24M/year |

Extended timeline for production-grade ZK L3 with encrypted mempool, DAC, and shared sequencing: 18–24 months.

## C.5 Greatest Advantage

**Modular sovereignty as a scalable product SKU.** New customer = new L3 instance, not a new L1 network. Mantle can sell hosted, self-hosted, and hybrid zones with per-tenant pricing. Each enterprise gets the isolation and control of "their own chain" while Mantle provides the settlement infrastructure, SDK, templates, and operational support — a genuine enterprise SaaS model for blockchain infrastructure.

## C.6 Greatest Risk

**Finality misrepresentation.** Developers and business stakeholders may conflate L3 soft confirmation (~1–2s) with Ethereum-level final settlement (~1 hour ZK, 7 days optimistic). Every external high-value settlement — Ethereum withdrawals, cross-enterprise DVP, collateral release — must traverse the full L3 → L2 → L1 chain. If the product is marketed as "instant Ethereum settlement" rather than "instant internal confirmation with deferred external settlement," business-critical failures will follow.

## C.7 Greatest Unknown

**Whether per-enterprise L3s create fatal liquidity fragmentation for secondary markets.** If 50 RWA issuers each run a separate L3, secondary market order books are split 50 ways with non-atomic cross-L3 settlement. This is a structural disadvantage versus a shared L2 or native L1 Zone model. The severity depends entirely on whether the target market requires deep secondary liquidity or primarily operates as a primary issuance/internal ledger platform.

## C.8 When to Choose / When NOT to Choose

**Choose L3 when:**
- The customer's primary requirement is "my own controlled environment" with chain-level data isolation
- Each tenant needs independent sequencer, private DA, compliance policy, and audit trail
- The use case tolerates L3 local soft finality for internal operations with deferred external settlement
- Faster time-to-market (9–13 months) and EVM reuse outweigh the need for sub-second hard finality
- Access to Mantle/Ethereum liquidity is needed but core workflows must remain private
- The product is a multi-tenant platform where per-tenant data separation is legally required

**Do NOT choose L3 when:**
- Sub-second deterministic hard finality is required (HFT securities, payment terminal settlement)
- Ethereum withdrawal hard finality cannot tolerate ~1 hour (ZK) or 7 days (optimistic)
- Atomic cross-zone DVP between multiple enterprises is required immediately (before shared sequencing)
- Protocol-level sovereignty is required (CBDC, national payment infrastructure)
- Secondary market liquidity depth is a core product requirement
- Public DeFi is the primary use case — Mantle L2 is the correct layer

---

# Cross-Path Quick Comparison

## Summary Table

| Dimension | Sovereign L1 | Enterprise L2 | Enterprise L3 |
|---|---|---|---|
| **Enterprise Autonomy** | ★★★★★ Full sovereignty | ★★☆☆☆ Tenant on operator infra | ★★★★☆ Per-chain operator control |
| **Finality Speed** | ★★★★★ ~600ms–2s BFT hard | ★★★☆☆ ~1–2s soft / 15–30min ZK | ★★☆☆☆ ~1–2s soft / ~1hr external |
| **Privacy Depth** | ★★★★★ Zone + sub-tx privacy | ★★★☆☆ Private DA; operator sees all | ★★★★☆ Private DA; operator sees own L3 |
| **Compliance Flexibility** | ★★★★★ Protocol-native enforcement across multiple control points | ★★★★☆ Sequencer + predeployments | ★★★★☆ Per-chain configurable |
| **Development Cost** | ★☆☆☆☆ $5M–$12M + audits | ★★★★☆ Lowest; high OP Stack reuse | ★★★☆☆ Medium; platform + per-zone |
| **Time-to-Market** | ★☆☆☆☆ 18–24 months | ★★★★★ 8–12 months (MVP in 3–4) | ★★★★☆ 9–13 months |
| **Ethereum Security Inheritance** | ★☆☆☆☆ Optional anchor only | ★★★★★ Native Rollup settlement | ★★★★☆ Inherited via Mantle L2 |
| **Ecosystem Compatibility** | ★★☆☆☆ Cold start required | ★★★★★ Full EVM + Mantle DeFi | ★★★☆☆ EVM compatible; fragmented |
| **Operational Simplicity** | ★☆☆☆☆ Full stack self-operated | ★★★★★ Mantle-operated | ★★★☆☆ Three-layer ops complexity |
| **Business Scalability** | ★★★☆☆ Zone-based expansion | ★★☆☆☆ Single shared chain | ★★★★★ New customer = new L3 |

## Key Metrics

| Metric | Sovereign L1 | Enterprise L2 | Enterprise L3 |
|---|---|---|---|
| Soft confirmation | ~600ms–2s (= hard) | ~1–2s | ~1–2s |
| Hard finality | ~600ms–2s BFT cert | ~15–30 min (ZK) / 7d (optimistic) | ~1 hr (ZK) / 7d (optimistic) |
| Team size | 15–25 people | 8–15 people | 10–15 people |
| Timeline to production | 18–24 months | 8–12 months | 9–13 months |
| Engineering cost | $5M–$12M | Not explicitly quantified; significantly lower | Platform build + $60K–$600K/zone/year |
| Monthly infra (initial) | ~$85K–$130K | Lower (Mantle-operated) | ~$5K–$50K per zone |
| Mainchain TPS target | 3,000–5,000 (Payment: >10K) | OP Stack baseline | Per-L3 chain capacity |
| Security model | Self-owned BFT validators | Ethereum economic security | Inherited via Mantle L2 → Ethereum |
| Data sovereignty | Full (institution-controlled DA) | Partial (operator visibility) | High (per-L3 private DA) |
| Ethereum exit path | Optional ZK anchor + bridge | Native Rollup bridge | L3 → L2 → L1 (two hops) |

## Strategic Weight Models

Different enterprise priorities lead to different optimal paths:

| Priority Model | Weighting | Winner |
|---|---|---|
| **Model A: Fast Enterprise Revenue** | Time-to-market 25% · Cost 20% · Ecosystem 20% | **Enterprise L2** |
| **Model B: Institutional Settlement** | Hard finality 25% · Autonomy 25% · Data sovereignty 15% · Compliance 15% | **Sovereign L1** |
| **Model C: Enterprise Platform Scale** | Tenant isolation 25% · Scalability 20% · Compliance config 20% | **Enterprise L3** |

## Three Fundamental Trade-Offs (from WHI-364 Fork Analysis)

Every path selection implicitly resolves three architectural tensions. These are not parameter-tuning problems — they are structural commitments.

### Trade-Off 1: Autonomous Finality vs. Security Inheritance

L1 gives sub-second BFT finality. The cost is self-built economic security — every validator compromise, consensus bug, and bridge exploit is Mantle's burden. L2 gives Ethereum's billions in economic security. The cost is minutes-to-days hard finality. L3 inherits L2's security model but adds another settlement hop, making the trade-off even more pronounced. **There is no path that simultaneously provides sub-second hard finality AND Ethereum economic security inheritance.**

### Trade-Off 2: Architectural Freedom vs. Ecosystem Connection

L1 gives full customization: consensus, gas model, Payment Lane, Zone architecture, custom transaction types. The cost is ecosystem isolation — wallets, indexers, explorers, market makers, stablecoin issuers, and institutional trust all start from zero. L2 gives Ethereum DeFi composability and existing tooling. The cost is OP Stack framework constraints — deep execution replacement for native programmable privacy requires fork maintenance. L3 sits in between, gaining EVM compatibility but fragmenting liquidity across per-tenant chains.

### Trade-Off 3: Ideal Architecture vs. Launch Speed

L1 delivers the optimal architecture for regulated financial infrastructure. It needs 18–24 months and $5M–$12M+ to reach production. L2 needs 8–12 months and significantly less investment for fast market validation, but with a structural capability ceiling. **The key risk is that L2-first validates demand for a product that cannot structurally serve the highest-value customers, while L1-first risks building without validated demand.**

## Use Case Fit Matrix

No single path satisfies all enterprise use cases. This split is architectural, not solvable by tuning parameters:

| Use Case | L1 Fit | L2 Fit | L3 Fit | Best Path |
|---|:---:|:---:|:---:|---|
| xStocks HFT | ★★★★★ | ★★★☆☆ | ★★☆☆☆ | **Clear L1** — sub-second deterministic finality required |
| Payment B2C (terminal-grade) | ★★★★★ | ★★★★☆ | ★★★☆☆ | **L1 preferred** — Payment Lane from genesis |
| RWA tokenization | ★★★★☆ | ★★★★☆ | ★★★★☆ | **Tie** — depends on finality and sovereignty requirements |
| Payment B2B | ★★★★☆ | ★★★★☆ | ★★★★☆ | **Tie** — counterparty trust model determines choice |
| DeFi (institutional) | ★★☆☆☆ | ★★★★★ | ★★★★☆ | **Clear L2** — Mantle liquidity is the product |
| Enterprise SaaS / multi-tenant | ★★★☆☆ | ★★☆☆☆ | ★★★★★ | **Clear L3** — per-tenant isolation at scale |
| Bank internal ledger | ★★★★☆ | ★★☆☆☆ | ★★★★★ | **L3 or L1** — depends on settlement speed requirements |
| CBDC / sovereign payment rails | ★★★★★ | ★☆☆☆☆ | ★★☆☆☆ | **Clear L1** — sovereignty is non-negotiable |

## Operational Comparison

| Operational Dimension | Sovereign L1 | Enterprise L2 | Enterprise L3 |
|---|---|---|---|
| **Who operates consensus** | Enterprise/consortium validators (7–15, scaling to 21–50) | Mantle Sequencer (centralized) | Per-L3 enterprise sequencer |
| **Who sees transaction data** | Zone participants + Zone sequencer/operator in early phases + scoped auditors; operator-blind privacy is later-phase | Sequencer sees all by default | L3 operator sees own chain data |
| **Who controls upgrades** | Validator governance + enterprise consortium | Mantle multi-sig + enterprise notification | Per-L3 enterprise + Mantle L2 governance |
| **Incident response** | Self-operated: validators, provers, relayers, Zone sequencers, HSM, audit | Mantle SRE team with enterprise SLA | Three-layer: L3 ops + Mantle L2 ops + Ethereum |
| **Recovery model** | Self-recovery via BFT validator set | Depends on Mantle operator framework | L3 self-recovery limited; depends on L2 liveness |
| **Long-term team** | 16–22 people (protocol, SRE, security, ZK, compliance) | Mantle-operated + enterprise integration team | Platform team 10–15 + per-zone support |
| **Key management** | HSM-backed, DKG ceremonies, epoch rotation | Mantle-managed Sequencer keys + enterprise RPC keys | Per-L3 enterprise keys + Mantle bridge keys |
| **Audit model** | View keys, scoped sandboxes, threshold decryption, immutable logs | Structured audit events, selective disclosure portal | Per-L3 audit trail + L2 settlement proof |

## Finality Comparison (The Most Consequential Differentiator)

| Finality Event | Sovereign L1 | Enterprise L2 | Enterprise L3 |
|---|---|---|---|
| Internal soft confirmation | ~600ms–2s | ~1–2s | ~1–2s |
| Cryptographic hard finality | ~600ms–2s (BFT cert) | ~15–30 min (ZK proof) | L3 local commitment: seconds, but single-sequencer local finality is trusted/operational unless a BFT committee is added |
| Ethereum-verifiable settlement | 5–30 min (optional ZK anchor) | ~15–30 min (ZK) / 7d (optimistic) | ~1 hr (ZK) / 7d (optimistic) |
| Cross-domain relay | ~1.2s (BFT → BFT) | N/A (single chain) | ~5–15s via L2 relay |
| External withdrawal complete | Minutes (bridge) | After proof finality | After L2 proof finality |

**Business implication:** For internal ledger operations, all three paths feel fast. The differentiation surfaces at external settlement: L1 provides deterministic hard finality at the same speed as soft confirmation. L2 and L3 have a structural gap between "feels done" and "is done."

---

# What Each Path Must NOT Promise

| | Sovereign L1 | Enterprise L2 | Enterprise L3 |
|---|---|---|---|
| **Do NOT promise** | "Affordable and quick to launch" | "Full enterprise sovereignty" | "Sub-second hard settlement" |
| **Do NOT promise** | "Ethereum-level economic security" | "Operator-blind transaction privacy" | "Atomic cross-enterprise DVP (Phase 1)" |
| **Do NOT promise** | "Immediate Mantle ecosystem liquidity" | "Deterministic settlement finality" | "Deep secondary market liquidity" |
| **Must disclose** | 15–25 people, 18–24 months, highest cost. Only rational with anchor client commitment. | Tenants are guests on Mantle-operated infrastructure. Sequencer has default plaintext visibility. | External finality bounded by L3→L2→L1 chain. ~1 hour ZK, 7 days optimistic fallback. |

---

# Recommended Composite Strategy

The three paths are not mutually exclusive. Based on the analysis in WHI-390 and the narrative framework in WHI-391:

```
Phase 1 (Months 0–12):   Enterprise L2 as market-entry product
                          → Validate demand, onboard first clients, prove compliance model

Phase 2 (Months 6–18):   Enterprise L3 as scalable delivery model
                          → Per-tenant isolation for clients outgrowing shared L2

Phase 3 (Gated):         Sovereign L1 as strategic option
                          → Activated ONLY when anchor client commits to sovereign settlement
```

**L1 trigger conditions** (any one activates):
1. Large financial consortium funds/co-commits to sovereign infrastructure
2. Payment or securities use case requires hard finality within 1–2 seconds with no L2/L3 settlement semantics
3. Regulatory/client governance requires enterprise group to end-to-end own validators, DA, compliance policy, and incident response

**Primary risk of the composite strategy:** L2-first attracts lower-value clients while highest-value institutions leave for competitors offering sovereign settlement from day one. The most important stop criterion is lack of qualified demand, not technical failure.

---

# Decision Framework for Slide Deck

| If the customer says... | Recommended path |
|---|---|
| "We need our own chain, our own data boundary, and our own compliance policy." | **Enterprise L3** |
| "We need Mantle/Ethereum liquidity and a credible product in 6 months." | **Enterprise L2** |
| "We need deterministic sub-second settlement and protocol-native control." | **Sovereign L1** |
| "We need to hide data from public observers but can trust a regulated operator." | **L2 or L3** (depends on tenancy) |
| "We need to hide data from the operator." | Future advanced-privacy **L1/L3** only; Phase 1 Zones still trust the sequencer/operator |
| "We most value DeFi composability and liquidity." | **Enterprise L2** |
| "We need payment-grade deterministic settlement." | **Sovereign L1** |

---

# Appendix: Architecture Diagram Specifications for Deck

Three formal architecture diagrams are needed (to be generated separately):

1. **Enterprise L1 Architecture**: Permissioned BFT validators → Zone isolation (RWA / xStocks / Payment / Custom) → Compliance & Identity layer → Private Zone DA → Optional Ethereum ZK anchor. Emphasize sovereignty and independence.

2. **Enterprise L2 Architecture**: Ethereum L1 ↔ Public Mantle L2 ↔ Enterprise L2 (parallel). Show Authenticated RPC → Enterprise Sequencer → Hybrid DA → Enterprise Bridge. Emphasize speed and Ethereum alignment.

3. **Enterprise L3 Architecture**: Multiple L3 boxes (Bank A, RWA Issuer, Payment Proc.) each with own sequencer/DA → Mantle L2 settlement hub → Ethereum L1. Emphasize per-tenant isolation and scalable delivery.
