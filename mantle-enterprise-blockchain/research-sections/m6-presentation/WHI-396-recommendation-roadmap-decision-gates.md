# WHI-396: Recommendation, Phased Roadmap & Decision Gates
- **Milestone**: M6 — Decision-Layer Presentation & Three-Path Selection
- **Date**: 2026-05-12
- **Status**: Draft
- **Audience**: Mantle Decision-Makers (CEO / CTO / VP Engineering / Strategy Lead)
- **Dependencies**: WHI-391, WHI-394, WHI-390, WHI-354, WHI-363, WHI-382

---

## 1. Recommended Strategy

**Primary Recommendation: L2-first market entry + L3 platformization + gated L1 strategic option.**

Mantle should not choose a single enterprise blockchain architecture. It should pursue a phased composite strategy that sequences investment by risk profile, validated demand, and structural capability. Enterprise L2 is the fastest credible path to market — it reuses Mantle's existing OP Stack infrastructure, Ethereum settlement narrative, sequencer operations, and EVM ecosystem to deliver a 90-day MVP and an 8–12 month production path at the lowest cost. Enterprise L3 extends this into a scalable delivery model: "one enterprise, one chain," where each client gets a dedicated L3 with its own sequencer, private DA, compliance rules, and data boundary — enabling a genuine SaaS business model for blockchain infrastructure. Sovereign L1, built on Reth SDK + BFT consensus, is the only path that delivers sub-second deterministic hard finality and full protocol sovereignty — but at 15–25 people, 18–24 months, $5M–$12M in engineering cost, and roughly $8M–$18M+ total program exposure after audits, infrastructure, bug bounty, and integrations, it is irrational without a committed anchor client. The L1 path should be treated as a gated strategic option: run a benchmark-first PoC, validate customer demand for sovereign settlement, and activate full investment only when specific, measurable trigger conditions are met.

This sequencing is not compromise — it is strategic discipline. L2 validates whether enterprise demand is real and paid. L3 proves whether tenant isolation can be delivered as a product, not a bespoke build. L1 captures the highest-value segment (financial consortia, payment networks, securities DVP) only when that segment commits. The most dangerous failure mode is not choosing the wrong layer — it is spending 18 months building infrastructure nobody has agreed to pay for.

---

## 2. Phase 1: Months 0–3 — Enterprise L2 MVP

### Scope

Build and launch a standalone permissioned L2 parallel chain alongside Mantle's public network. The MVP must prove that a regulated Ethereum-aligned enterprise chain can onboard its first design partners within 90 days.

**Includes:**
- Standalone chain bootstrap (dedicated sequencer, separate chain ID, permissioned genesis)
- Authenticated RPC with identity-verified access (KYC/KYB credential gating)
- Sequencer policy engine (transaction-level admission, counterparty validation, asset-class restrictions)
- L1 bridge compliance filters (whitelist enforcement on deposits/withdrawals, sanctions screening)
- Identity and compliance registries (on-chain IdentityRegistry and PolicyRegistry as Predeploy contracts)
- Audit event logging (immutable compliance trail with structured event schema)
- Finality labeling API (explicit soft-confirmation vs. ZK-proven vs. L1-settled states exposed to applications)
- L3 foundation track (template requirements, ZonePortal interface sketch, private DA interface, and finality labels) so Phase 2 can start from validated customer requirements rather than a blank sheet

**Explicitly excludes (deferred to Phase 2+):**
- Full native privacy (operator still sees transaction plaintext in Phase 1; only public-observer privacy via private DA)
- Operator-blind transaction privacy
- Production ZK proof acceleration
- Cross-chain atomic DVP
- Full decentralization or shared sequencing

### Customer Validation Tasks

1. Conduct 10–20 structured enterprise interviews during days 0–45 to validate target segment selection
2. Onboard 2–3 design partners by day 60 (RWA issuers, custodians, or enterprise DeFi venues)
3. Run at least one end-to-end pilot transaction workflow (issuance → transfer → compliance check → settlement) by day 75
4. Collect written feedback from design partners on: trust model acceptability, compliance coverage gaps, finality semantics, operational requirements

### Team Requirements

| Role | Headcount | Notes |
|------|-----------|-------|
| Blockchain core engineers (Go/Solidity) | 3–4 | OP Stack chain config, sequencer policy, Predeploy contracts |
| Application / SDK engineers | 2–3 | RPC auth, bridge filters, audit events, finality API |
| DevOps / SRE | 1–2 | Chain deployment, monitoring, incident response |
| Product / BD | 1–2 | Design partner acquisition, customer interviews |
| **Total** | **8–10** | |

### Key Deliverables

- Running permissioned L2 testnet with authenticated RPC
- Sequencer policy engine with configurable admission rules
- Bridge compliance filter (deposits and withdrawals)
- On-chain IdentityRegistry and PolicyRegistry contracts
- Audit event schema and log export tooling
- Finality label API specification
- L3 foundation brief: first template scope, ZonePortal API draft, private DA assumptions, and candidate design-partner use cases
- 2–3 signed design partner agreements

### Go/No-Go Criteria for Phase 2

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Design partner engagement | ≥2 active design partners running test transactions | Sign-off from partner technical leads |
| Compliance model acceptance | ≥1 partner's legal/compliance team accepts the operator trust model | Written confirmation |
| Policy engine validation | Sequencer policy engine passes red-team bypass testing | Security review report |
| Bridge control validation | L1→L2 forced inclusion path is demonstrably filtered | Audit log evidence |
| Revenue signal | ≥1 partner expresses willingness to pay for production deployment | LOI or equivalent |

**If Go/No-Go fails:** Reassess enterprise strategy. The most important stop criterion is lack of qualified demand, not technical failure.

---

## 3. Phase 2: Months 3–6 — L3 App Chain Framework

### Scope

Build the L3 platform layer that transforms enterprise blockchain from a single shared chain into a scalable multi-tenant delivery model. Each enterprise customer receives a dedicated L3 with isolated data, configurable compliance, and independent operations — while Mantle L2 remains the common settlement and liquidity layer.

**Includes:**
- L3 chain template with configurable parameters (consensus, DA mode, compliance policy, access rules)
- ZonePortal contracts on L2 for L3 registration, state commitment, and bridge management
- Private DA v1 (per-tenant data isolation from public observers and other tenants)
- Per-L3 authenticated RPC and sequencer policy inheritance
- Deployment automation (Helm/Terraform templates for one-click L3 provisioning)
- First 1–2 pilot L3 instances for design partners requiring tenant isolation

**Explicitly excludes (deferred to Phase 3):**
- Cross-zone atomic relay
- Shared sequencing across L3s
- ZK proof pipeline for L3 → L2 settlement
- Production-grade multi-zone monitoring dashboard

### What It Proves

1. **Enterprise self-operation**: Can a customer (or Mantle on their behalf) operate an L3 with their own compliance rules without forking the core chain?
2. **Per-tenant customization**: Can different enterprises on separate L3s have different privacy policies, access rules, data retention, and compliance configurations?
3. **Isolation guarantees**: Does the L3 architecture genuinely isolate tenant data, transaction flows, and operational scope?
4. **Delivery economics**: Is "new customer = new L3 instance" operationally and economically viable as a repeatable business model?

### Team Expansion

| Role | Additional Headcount | Notes |
|------|---------------------|-------|
| Blockchain core engineers | +2–3 | L3 template, ZonePortal, DA routing |
| Infrastructure / Platform | +1–2 | Deployment automation, monitoring, per-zone ops |
| Compliance / Legal | +1 | Per-tenant policy templates, operating agreements |
| **Phase 2 total** | **12–15** | Including Phase 1 team |

### Key Deliverables

- L3 chain template with documented configuration parameters
- ZonePortal contracts deployed on L2 testnet
- Private DA v1 operational for at least 2 isolated L3 instances
- Deployment automation: L3 provisioning in <1 hour from configuration to running chain
- Pilot L3 instances with design partners from Phase 1
- Enterprise pricing model draft (per-zone infrastructure, compliance modules, sequencer operations)

### Go/No-Go Criteria for Phase 3

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| L3 pilot success | ≥2 successful L3 pilots with different compliance configurations | Pilot completion reports |
| Isolation verification | Data isolation between L3 instances verified by third-party review | Security assessment |
| Customer demand signal | ≥2 additional enterprises expressing L3 interest beyond initial design partners | Pipeline evidence |
| Deployment repeatability | L3 provisioning achievable by operations team (not core engineers) | SOP documentation + execution proof |
| Finality acceptance | Pilot customers accept L3 internal finality + deferred external settlement semantics | Written acknowledgment |

**If Go/No-Go fails:** Evaluate whether deeper customization is needed (suggesting L1 may be necessary for certain segments) or whether the L2 shared model is sufficient for current demand.

---

## 4. Phase 3: Months 6–12 — Enterprise Productization

### Scope

Harden the L2+L3 platform into a production-grade enterprise product with compliance audit capability, advanced privacy, production monitoring, and commercial packaging.

**Includes:**
- Private DA hardening (replication, backup, disaster recovery, SLA enforcement)
- Compliance audit framework (regulator-facing evidence export, structured audit trails, selective disclosure for auditors)
- Privacy transaction envelopes and selective disclosure (ZK proofs for accredited status, sanctions clearance, balance thresholds — without exposing PII)
- Finality oracle for applications (programmatic access to typed finality states)
- ERC-3643 / T-REX compliant token templates for RWA issuance
- Travel Rule integration module
- Enterprise SDK with onboarding documentation
- Cross-zone relay prototype (L3 ↔ L3 value transfer via L2)
- Pilot expansion: 3–5 production-intent enterprise customers
- Governance artifacts: upgrade procedures, incident response playbooks, change management processes

### Pricing and Packaging

Define the enterprise product as a tiered offering:

| Tier | Description | Target Customer | Indicative Annual Cost |
|------|-------------|-----------------|----------------------|
| **Enterprise L2 Access** | Shared permissioned L2 with authenticated RPC, compliance registry, audit logs | RWA issuers, institutional DeFi | Platform fee + transaction-based |
| **Dedicated L3** | Single-tenant L3 with private DA, custom compliance, dedicated sequencer | Banks, custodians, payment processors | $60K–$240K/year infrastructure + management fee |
| **L3 Premium** | L3 with advanced privacy, cross-zone relay, enhanced SLA, dedicated support | Large financial institutions, consortia | $180K–$600K/year + premium support |

### Team Maturity Requirements

| Role | Headcount | Notes |
|------|-----------|-------|
| Blockchain core | 5–7 | Privacy, finality oracle, cross-zone relay |
| Application / SDK | 3–4 | Token templates, Travel Rule, SDK |
| DevOps / SRE | 2–3 | Production monitoring, DR, SLA |
| Compliance / Legal | 1–2 | Audit framework, regulatory engagement |
| Product / Sales | 2–3 | Enterprise sales, customer success |
| **Phase 3 total** | **14–18** | Including retained Phase 1–2 team |

### Key Deliverables

- Production-hardened L2 and L3 infrastructure with defined SLAs
- Compliance audit export tool (regulator-ready evidence packages)
- Selective disclosure module operational
- ERC-3643 token factory deployed and audited
- Travel Rule integration live for at least one jurisdiction
- Enterprise SDK v1 with documentation and sample applications
- 3–5 enterprise customers in production or advanced pilot
- Cross-zone relay PoC demonstrating L3-to-L3 value transfer

### 12-Month Continuation / Stop Criteria

Phase 3 should not automatically roll into a larger enterprise platform program. At month 12, leadership should treat the roadmap as a portfolio review and decide which path deserves the next 12 months of capital.

| Criterion | Continue / Scale | Pause / Redirect |
|-----------|------------------|------------------|
| Paid demand | ≥3 credible enterprise customers in production or paid advanced pilot | Pilots remain unpaid, innovation-lab-only, or dependent on subsidized professional services |
| L2 trust model | Customers accept Mantle-operated sequencing with explicit finality labels and legal risk limits | Target customers reject operator trust, sequencer visibility, or delayed hard finality |
| L3 repeatability | Operations can provision and monitor new L3s from a standard template with limited core-engineering involvement | Each L3 requires bespoke engineering or unresolved bridge/DA/security review |
| Compliance liability | Legal counsel confirms Mantle's operator or technology-provider role is contractually manageable | Regulatory exposure forces Mantle out of the sequencer/compliance operator role |
| Strategic path | Evidence points clearly to L2 scale, L3 SaaS, MPL privacy product, or L1 trigger | Evidence remains diffuse; leadership cannot identify a paying segment or repeatable product |

**If Phase 3 fails:** Stop broad platform expansion. Preserve reusable assets (identity schema, policy registry, audit format, finality API), but do not increase headcount until a paying segment and operating model are validated.

---

## 5. L1 Strategic Option

### Framing

The Sovereign L1 path is **NOT a default build**. It is a gated strategic option that Mantle should prepare for but not commit to unless specific conditions are met. Building a full L1 (Reth SDK + BFT consensus + multi-zone architecture + payment lane + enterprise precompiles) requires 15–25 people, 18–24 months, and $5M–$12M in engineering cost before audits, infrastructure, bug bounty, and integrations; total program exposure is closer to $8M–$18M+. This is the highest-risk, highest-reward path and should be funded only when demand, PoC performance, budget, and talent gates all pass together.

The L1 is the only architecture that delivers sub-second deterministic hard finality (~600ms–2s BFT certificate that IS the settlement), full protocol sovereignty (enterprise controls consensus, execution, DA, compliance, and governance), and payment-grade throughput (>10,000 TPS via dedicated Payment Lane). For bank consortia, securities DVP, real-time treasury operations, and CBDC/sovereign payment rails, these capabilities are non-negotiable. For every other use case, L2/L3 is structurally sufficient.

### What To Do Now (Months 0–6)

1. **Benchmark PoC** (months 0–4, 2–3 engineers): Build a minimal Reth+BFT testnet (4–11 nodes) to validate consensus latency, block production, and fault tolerance under realistic validator topology
2. **Payment Lane benchmark** (months 2–5): Test >10,000 TPS throughput with consensus-enforced gas budgets and congestion isolation
3. **Privacy deposit prototype** (months 3–6): Validate ECIES-encrypted transaction flow and compliance bypass resistance through red-team testing
4. **Customer demand validation** (ongoing): Track whether any enterprise prospect explicitly requires sovereign validators, sub-second hard finality, or protocol-level compliance that cannot be delivered by L2/L3

### Conditions to Trigger Full L1 Build

All of the following must be satisfied — any single missing condition means L1 remains a PoC:

| # | Condition | Evidence Required |
|---|-----------|-------------------|
| 1 | Anchor customer commitment | Signed LOI, co-funding agreement, or regulatory mandate from a financial consortium, payment network, or securities venue requiring sovereign settlement |
| 2 | PoC passes technical gates | Reth+BFT latency ≤2s at 7+ validators; Payment Lane ≥10K TPS; privacy deposit passes security audit; policy bypass red-team shows no critical bypasses |
| 3 | Funding secured | >$10M total L1 program envelope approved or externally co-funded, including at least $5M engineering budget plus audit, infrastructure, bug bounty, and integration reserves |
| 4 | Talent acquisition plan | Core team (consensus, cryptography, security, SRE) identified and recruitable within 3 months |

G1 and G4 are deliberately coupled. An anchor client without a passing PoC is not enough to fund a full L1; it only justifies accelerating benchmark work and commercial negotiation. A passing PoC without anchor demand is also not enough; it remains R&D.

### Conditions That Confirm L2/L3 Is Sufficient

If any of the following hold at the 12-month review, L1 should remain theoretical:

- No enterprise prospect has explicitly rejected L2/L3 due to finality or sovereignty requirements
- All paying customers accept Mantle-operated or customer-operated L3 sequencing
- Compliance review confirms Mantle can legally operate as sequencer/compliance operator without unacceptable regulatory liability
- L2 ZK proof acceleration reaches ≤15 minutes, reducing the hard-finality gap to acceptable levels for current customer needs

---

## 6. Paladin Positioning

### MPL as a Standalone Privacy Product Evaluation Option

Paladin (LFDT Labs / Linux Foundation Decentralized Trust) should be evaluated as the **Mantle Privacy Layer (MPL)** — a standalone permissioned privacy network using Paladin + Hyperledger Besu + QBFT consensus. Per the WHI-382 research, MPL scored 26/30 vs. 20/30 for the L2 sidecar integration approach, with zero critical blockers (vs. three critical/high blockers for the sidecar path). WHI-382 correctly recommends MPL as the primary Paladin architecture; this roadmap treats it as an optional portfolio investment because Mantle's first enterprise dollar should still validate L2/L3 demand before funding a separate privacy network as a product line.

**MPL is NOT default-embedded into the Mantle L2 core path.** The reasons are structural:
- Paladin's architecture targets BFT permissioned networks; forcing it onto an optimistic rollup breaks Atom cross-domain atomicity and creates confirmation semantic mismatches
- L2 sidecar integration caps Paladin feature coverage at 60–70% vs. 100% on MPL
- MPL ships as an independently sellable enterprise privacy product with 2–4 month time-to-MVP (3.0 FTE)

### Evaluation Criteria

Paladin/MPL partnership has independent value if:

| Criterion | Threshold |
|-----------|-----------|
| Customer demand | ≥1 enterprise customer explicitly needs privacy capabilities (confidential transfers, selective disclosure, multi-party privacy) beyond what L2/L3 private DA provides |
| Product-market fit | MPL MVP (private stablecoin transfer with on-chain KYC proof) attracts ≥2 institutional evaluation partners within 6 months |
| Business case | Total cost of MPL deployment (121–247 person-days customization + ongoing operations) is justified by revenue potential or strategic partnership value |
| Technical viability | Paladin component reuse ≥85% (current assessment: 88% direct reuse, 12% light customization) |
| Bridge feasibility | L2 ↔ MPL bridge design (Phase 2: multi-sig; Phase 3: ZKP) is architecturally sound and does not introduce unacceptable security risk |

**If evaluation is negative:** Table Paladin. The privacy gap can be partially addressed by L2/L3 private DA, Validium-mode data routing, and selective disclosure without a separate permissioned network.

---

## 7. Decision Gates

Five gates govern the strategy. Each gate asks a specific question with measurable trigger conditions and binary outcomes.

| Gate | Question | Trigger Condition | Outcome if YES | Outcome if NO |
|------|----------|-------------------|----------------|---------------|
| **G1** | Is there an anchor customer requiring sovereign validators / hard finality? | Signed LOI, co-funding agreement, or regulatory mandate from a financial consortium, payment network, or securities venue | Advance L1 to funding review and commercial negotiation; authorize full build only if G4 plus funding/talent gates also pass | L2/L3 path sufficient; L1 remains benchmark-only PoC |
| **G2** | Does Enterprise L2 MVP validate real paid demand? | ≥1 paying pilot within 6 months of launch; ≥2 design partners with production intent | Scale L2 infrastructure; begin L3 framework (Phase 2) | Reassess enterprise strategy; consider pivot to technology licensing or partnership model |
| **G3** | Can L3 templates satisfy different customer isolation needs without core chain rewrite? | ≥2 successful L3 pilots with different compliance/privacy configurations operating simultaneously | Productize L3 platform; develop pricing, automation, and sales enablement | Evaluate whether deeper architectural customization (potentially L1-grade) is needed |
| **G4** | Does L1 PoC prove Reth/BFT/privacy/compliance stack meets minimum performance + security? | BFT latency ≤2s at 7+ validators; Payment Lane ≥10K TPS; privacy audit passes; no critical policy bypasses | If G1 also passes and >$10M program funding is secured, begin L1 full-build Phase 1; otherwise keep as validated R&D | L1 remains theoretical; revisit only with new technology or demand evidence |
| **G5** | Does Paladin MPL have independent product/partnership value? | ≥2 institutional evaluation partners within 6 months; positive business case; ≥85% component reuse confirmed | Pursue Paladin partnership; fund MPL to V1 (month 14 target) | Table Paladin; address privacy needs through L2/L3 native mechanisms |

### Gate Timeline

```
Month 0          Month 3          Month 6          Month 9          Month 12
  |                |                |                |                |
  |-- Phase 1 ---->|-- Phase 2 ---->|-- Phase 3 ---->|                |
  |                |                |                |                |
  |    G2 checkpoint (design       G2 decision       G3 decision     G1/G4/G5
  |    partner feedback)           (paid demand?)    (L3 viable?)    (12-month
  |                                                                   review)
  |-- L1 PoC (benchmark only) --->|                                  |
  |                                G4 checkpoint                     G4 decision
  |                                (PoC results)                     |
  |-- Paladin eval --------------->|                                 |
  |                                G5 checkpoint                     G5 decision
  |                                (partner interest)                |
  |                                                                  |
  |                                                  G1 evaluation   G1 decision
  |                                                  (anchor client  (fund L1?)
  |                                                   evidence)      |
```

---

## 8. Resource & Risk Summary

### Per-Phase Resource Requirements

| Phase | Duration | Team Size | Engineering Type | Estimated Cost |
|-------|----------|-----------|-----------------|----------------|
| **Phase 1** (L2 MVP) | Months 0–3 | 8–10 | Blockchain core (Go/Solidity), application/SDK, DevOps, product/BD | ~$400K–$600K (salaries + infra) |
| **Phase 2** (L3 Framework) | Months 3–6 | 12–15 | +L3 platform, infrastructure/automation, compliance | ~$600K–$900K incremental |
| **Phase 3** (Productization) | Months 6–12 | 14–18 | +Privacy, audit framework, SDK, sales/customer success | ~$1.2M–$1.8M incremental |
| **L1 PoC** (parallel) | Months 0–6 | 2–3 | Rust/consensus specialists | ~$200K–$400K |
| **Paladin eval** (parallel) | Months 0–6 | 1–2 (+ Paladin partnership) | Go, Solidity, Besu | ~$100K–$200K (Mantle-side) |
| **L1 Full Build** (if triggered) | 18–24 months | 15–25 | Rust, BFT consensus, ZK cryptography, security, SRE | $5M–$12M engineering; ~$8M–$18M+ total program exposure |

**Total Months 0–12 (excluding L1 full build):** $2.5M–$3.9M with 14–18 peak headcount. These are planning envelopes derived from upstream headcount and timeline estimates, not procurement quotes; finance should refresh salary, infrastructure, audit, and partner-service assumptions before authorization.

### Maximum Risk Per Phase

| Phase | Maximum Risk | Description | Mitigation |
|-------|-------------|-------------|------------|
| **Phase 1** | No qualified demand | Enterprise interviews and design partner outreach reveal no willingness to pay for permissioned L2 | Narrow scope to 3-month validation sprint; treat Phase 1 as a market experiment, not a product launch |
| **Phase 2** | L3 operational complexity | Per-tenant L3 provisioning, monitoring, and support overwhelm small team | Invest heavily in automation; limit initial L3 count to 2–3; define clear SLA boundaries |
| **Phase 3** | Compliance liability | Operating as sequencer/compliance operator creates regulatory exposure Mantle is unprepared for | Engage legal counsel early (Phase 1); define Mantle's operator vs. technology-provider positioning before production |
| **L1 PoC** | Talent scarcity | Rust/BFT/ZK specialists unavailable within timeline | Begin recruiting pipeline in month 0; consider acqui-hire or partnership for consensus expertise |
| **L1 Full Build** | 18-month commitment without demand validation | Building sovereign infrastructure before confirming anchor client creates platform without product-market fit | Gate L1 on anchor commitment (G1); never authorize full build without signed LOI or co-funding |

### Management Actions Required

| Action | Owner | Timeline |
|--------|-------|----------|
| Authorize Phase 1 budget and team allocation | CEO / CFO | Week 0 |
| Select target entry point (customer segment) | CEO / Strategy | Days 0–15 |
| Define Mantle's operator positioning (regulated operator vs. technology provider) | CEO / Legal | Days 0–30 |
| Define privacy commitment (public-observer privacy only vs. operator privacy roadmap) | CEO / CTO / Legal | Days 0–30 |
| Define finality commitment and permitted business actions per finality state | CTO / Legal / Product | Days 0–30 |
| Engage regulatory counsel on compliance operator liability | Legal / Compliance | Month 1 |
| Launch enterprise customer interview program | Product / BD | Weeks 1–6 |
| Begin L1 PoC engineer recruiting pipeline | CTO / Engineering | Month 0 |
| Evaluate Paladin partnership terms | Strategy / CTO | Months 1–3 |
| Conduct 12-month strategy review (all gates) | CEO / CTO / Strategy | Month 12 |

---

## 9. What Leadership Needs to Decide TODAY

These decisions cannot be deferred without stalling the entire enterprise strategy. Each requires an explicit yes/no or selection by named owners within the first 30 days.

### Decision 1: Authorize Phase 1 Budget and Team

**Question:** Does Mantle commit $400K–$600K and 8–10 people for a 3-month Enterprise L2 MVP sprint?

**Why it can't wait:** Every month of delay is a month competitors (Canton with $2T+/month volume, Prividium with 35+ financial institutions) accumulate enterprise customers. Phase 1 is deliberately sized as a low-cost market experiment — the cost of not running it is learning nothing about enterprise demand while competitors learn everything.

**Owner:** CEO / CFO

### Decision 2: Select Enterprise Target Entry Point

**Question:** Which customer segment does Mantle pursue first — RWA issuers, custodians, payment companies, bank consortia, or enterprise DeFi venues?

**Why it can't wait:** The target segment determines Phase 1 scope, compliance requirements, finality semantics, and design partner outreach. Building "enterprise blockchain for everyone" builds for nobody. The first segment should be where Mantle has the strongest existing relationships and where the L2 trust model (Mantle-operated sequencer, Ethereum settlement) is most readily accepted.

**Owner:** CEO / Strategy Lead

### Decision 3: Authorize L1 PoC (Yes/No)

**Question:** Should Mantle allocate 2–3 engineers for a parallel 6-month L1 benchmark PoC (Reth+BFT testnet, Payment Lane throughput test, privacy deposit prototype)?

**Why it can't wait:** If L1 PoC is deferred, the earliest L1 technical evidence arrives at month 12+ instead of month 6. This delays the G4 gate decision by 6 months, which means Mantle cannot respond to anchor client demand for sovereign settlement until month 24+. The PoC cost (~$200K–$400K) is insurance against missing the highest-value market segment.

**Recommendation:** Yes. The PoC is low-cost, non-committal, and provides essential data for the G1/G4 gates.

**Owner:** CTO / VP Engineering

### Decision 4: Authorize Paladin Evaluation (Yes/No)

**Question:** Should Mantle engage LFDT Labs / Paladin team for a 6-month MPL evaluation, including partnership terms exploration and MPL MVP scoping?

**Why it can't wait:** Paladin is open-source and available today. If a competitor adopts Paladin's privacy framework first and establishes the "enterprise privacy on EVM" positioning, Mantle loses the first-mover opportunity. The evaluation cost (~$100K–$200K Mantle-side, 1–2 engineers) is minimal relative to the cost of building equivalent privacy infrastructure from scratch.

**Recommendation:** Yes, but as evaluation only — not as a commitment to integrate.

**Owner:** CTO / Strategy Lead

### Decision 5: Define Operator, Privacy, and Finality Commitments

**Question:** Is Mantle willing to operate as a regulated sequencer/compliance operator for enterprise customers, or will it position exclusively as a technology provider? In the same decision, what privacy promise is allowed in Phase 1 (public-observer privacy only, or operator-blind privacy roadmap), and which business actions are permitted at each finality state (soft sequencer confirmation, ZK-proven, L1-settled)?

**Why it can't wait:** This decision determines the entire compliance architecture, legal liability structure, product promise, and operating model. If Mantle operates the sequencer and enforces compliance, it becomes a regulated entity subject to jurisdiction-specific obligations. If Mantle provides technology only, enterprises must operate their own infrastructure (pushing toward L3 or L1). If Mantle over-promises privacy or finality, the product will be mis-sold before it launches. Every Phase 1 design decision — from policy engine design to audit log structure, finality labels, disclosure workflows, and customer contracts — depends on this answer.

**Owner:** CEO / Legal / Compliance

---

*This document synthesizes findings from M3 (WHI-354), M4 (WHI-363), M5 (WHI-390), M6 (WHI-391, WHI-394), and Paladin (WHI-382) research. All resource estimates, timelines, and cost projections are based on the analysis in those upstream documents and should be validated against current market conditions and Mantle's actual hiring pipeline before commitment.*
