# WHI-391: Executive Narrative Framework & Decision Question Definition
- **Milestone**: M6 — Decision-Layer Presentation & Three-Path Selection
- **Date**: 2026-05-11
- **Status**: Reviewed
- **Audience**: Mantle Decision-Makers (CEO / CTO / VP Engineering / Strategy Lead)
- **Document Type**: Deck Blueprint / Creative Brief — not a research document

---

## 1. Core Decision Question

**The single question this presentation must answer:**

> Given Mantle's existing position as an OP Stack L2 with $2B+ TVL and a mature EVM ecosystem, what is the right enterprise blockchain strategy: **Enterprise L2** (fastest to market, Ethereum-aligned), **Enterprise L3** (scalable tenant-isolation platform), or **Sovereign L1** (maximum capability, maximum cost)?

### Framing: Resource Allocation, Not Technology Selection

This is NOT a "which technology is best?" question. It is a **resource allocation and strategic positioning** question:

- **Enterprise L2** = Extend what we have. 8–15 people, 8–12 months, roughly 120–152 person-months in M5. Fastest demand validation. Structurally limited in sovereignty and finality.
- **Enterprise L3** = Build a platform product. 10–15 people, 9–13 months, plus per-zone infrastructure economics. Scalable multi-tenant model. Inherits L2 external-finality limitations.
- **Sovereign L1** = Build a new chain. 15–25 people, 18–24 months, highest cost path: M5 estimates $5M–$12M engineering salary before audit, infrastructure, bounty, integration, and long-term operations. Only rational with anchor client commitment.

**The recommended answer** (from M5 research): Don't choose one. Pursue a **phased composite strategy** — L2 as the market-entry product, L3 as the scalable delivery model, L1 as a gated strategic option activated only by validated demand.

### Five Leadership Decisions Before Engineering Proceeds

| # | Decision | What Leadership Must Answer |
|---|----------|-----------------------------|
| 1 | Target Entry Point | First customer segment: RWA issuers, custodians, payment companies, bank consortia, or enterprise DeFi venues? |
| 2 | Operator Positioning | Is Mantle willing to be a regulated sequencer/compliance operator, or only a technology provider? |
| 3 | Privacy Commitment | Phase 1: public-observer privacy only, or also operator privacy? |
| 4 | Finality Commitment | Which transaction states will the product expose, and which business actions are allowed at each state? |
| 5 | L1 Trigger | What client commitment, benchmark result, or funding threshold activates full L1 investment? |

Final deck should assign owners: CEO/Strategy for market entry and Phase 1 authorization; CTO/VP Engineering for feasibility gates; Legal/Compliance for operator-liability acceptance. Track qualified clients, paid pilots, L2 trust acceptance, L3 isolation demand, L1 anchor evidence, and compliance blockers.

---

## 2. Executive Narrative Arc

### The Story in Seven Beats

**Beat 1 — Opening Hook: "Enterprise blockchain is NOT public chain + whitelist"**

Purpose: Disrupt the "just add KYC" assumption. If bridge, sequencer, deployment, DA, and finality remain uncontrolled, the chain remains public in structure.

*Decision-layer takeaway: Canton, Prividium, Tempo, and Paladin understood this. If we gate RPC while leaving other ingress paths open, we have a whitelist, not an enterprise chain.*

**Beat 2 — Context Setting: What four reference projects taught us**

Purpose: Establish credibility. Each reference project solved enterprise control differently and reveals a tradeoff Mantle must navigate.

| Project | Core Innovation | What It Teaches Mantle |
|---------|----------------|----------------------|
| Canton (Digital Asset) | Sub-transaction need-to-know privacy via Merkle DAG projection | Finest privacy granularity possible, but requires non-EVM language (Daml) — proves that EVM compatibility is a hard constraint |
| Prividium (zkSync) | ZK Validium + encrypted DA for 35+ financial institutions | "Settled on Ethereum" narrative is the strongest regulatory credibility claim; STARK proof neutrality drives institutional adoption |
| Tempo Zones | BFT consensus (~600ms finality) + Zone isolation + Payment Lane | Only reference project achieving true sub-second deterministic finality on EVM; validates Reth+BFT L1 technology stack |
| Paladin (LFDT Labs, separate M6 reference) | Privacy middleware with Zeto KYC membership proofs, private EVM groups, and MPL deployment path | Shows where open-source privacy infrastructure can be adopted rather than built from scratch; use Paladin-specific claims only with citations from the Paladin research package |

*Decision-layer takeaway: The enterprise blockchain market has converged on EVM. Being non-EVM is a dealbreaker. The real differentiators are finality semantics, privacy architecture, and compliance enforcement depth.*

**Beat 3 — Framework: The 8 core modules that define enterprise blockchain design**

Purpose: Give leadership the vocabulary for evaluating three paths through 8 coupled design choices.

The 8 modules: (1) Execution Layer, (2) Consensus/Finality, (3) Privacy, (4) Compliance/Identity, (5) Access Control, (6) Data Availability/Data Sovereignty, (7) Interoperability, (8) Business Components.

Key constraint propagation chains to highlight:
- Privacy choice → DA model → L1 relationship → bridge design
- Finality choice → settlement semantics → DVP/payment capability
- Compliance depth → execution modification depth → EVM compatibility risk

*Decision-layer takeaway: You cannot choose a layer (L1/L2/L3) without first understanding what these 8 modules demand for your target use case. The layer is the consequence of the module requirements, not the starting point.*

**Beat 4 — Three Paths: Architecture, fit, and honest tradeoffs**

Purpose: Present each path as legitimate for a specific buyer profile, with clear strengths and limitations.

| Path | Core Guarantee | Best For | Not Suitable For | Resource Evidence |
|------|---------------|----------|-----------------|-------------------|
| Enterprise L2 | Regulated Ethereum/Mantle extension | RWA issuance, institutional pilots, enterprise DeFi, custodian networks | Clients needing sovereign settlement or sub-second hard finality | 8–15 people, 8–12 months |
| Enterprise L3 | Dedicated tenant environment with isolation | Private RWA registries, bank internal ledgers, B2B payment domains, multi-tenant SaaS | Systemic payment channels, HFT securities, cross-chain exits needing immediate hard finality | 10–15 people, 9–13 months; per-zone annual infra planning varies by workload |
| Sovereign L1 | Sovereign deterministic settlement | Payment channels, securities consortia, real-time DVP, institutional networks treating sub-second finality as non-negotiable | Cost-sensitive pilots, fast market entry, clients satisfied with Ethereum alignment | 15–25 people, 18–24 months; highest cost and operating burden |

Critical honest statements each path MUST make:
- **L2 must say**: "Tenants are guests on Mantle-operated infrastructure. Sequencer has default plaintext visibility. Soft confirmation ≠ legal hard settlement."
- **L3 must say**: "External finality is bounded by the L3 → L2 → L1 chain. Cross-zone atomicity requires explicit design, not assumption."
- **L1 must say**: "This is the highest-cost path, takes 18–24 months, creates a new security narrative, and is irrational without an anchor client who needs sovereign settlement."

*Decision-layer takeaway: L1/L2/L3 are not a maturity ladder — they are different products for different buyers. The question is which buyer Mantle wants to serve first.*

**Beat 5 — Comparison: Horizontal decision matrix**

Purpose: Compare the paths across the resource allocation dimensions that matter: autonomy, finality, privacy, compliance, cost, time-to-market, Ethereum alignment, ecosystem fit, operations, and scalability.

Finality deep-dive (the most consequential technical differentiator):
- L1 BFT: ~600ms–2s hard finality. Payment-grade. No external dependency.
- L2: ~1–2s soft confirmation; ZK hard finality depends on proof cadence and can range from a mature 15–30 minute target to longer current/high-load paths, with 7-day fallback in optimistic modes.
- L3: seconds-level local, but external hard finality bounded by L2→L1 chain (~1 hour+).

*Decision-layer takeaway: If finality matters (payments, DVP, securities), native BFT L1 is categorically different from rollup proof finality. If Ethereum alignment and speed-to-market matter, L2 wins. If tenant isolation and scalable delivery matter, L3 wins.*

**Beat 6 — Recommendation: Phased roadmap with decision gates**

Purpose: Present the composite strategy with phases, triggers, and stop conditions.

**Phase 1 (0–12 months): L2 Core + L3 Foundation + L1 Feasibility**
- Enterprise L2: Ship permissioned chain, identity-verified RPC, sequencer policy, bridge compliance, audit logs
- L3 Foundation: Define templates, ZonePortal design, finality labels, deploy first pilot L3
- L1 Feasibility: Reth+BFT PoC, payment channel benchmarks, privacy deposit prototype
- Customer Discovery: 10–20 structured interviews → 2–3 design partners → 1–2 production-intent pilots

**Phase 2 (12–24 months): Demand-driven investment**
- Signal: L2 pilots strong → harden L2 (proof acceleration, compliance middleware, client SLAs)
- Signal: clients demand isolation → invest in L3 (chain templates, managed sequencer, per-zone compliance)
- Signal: clients reject L2/L3 for sovereignty → fund L1 path (reuses L2/L3 artifacts)

**Decision gates (the presentation must make these explicit):**
| Signal | Action |
|--------|--------|
| 3+ credible clients accept L2 trust model | Double down on Enterprise L2 |
| Clients accept Mantle settlement but need dedicated environments | Accelerate L3 platform |
| Clients need own sequencer/private DA but can tolerate delayed external settlement | Route to L3 |
| Clients need own validators and sub-second hard finality | Activate L1 funding decision |
| Compliance review prevents Mantle from operating sequencing | Pivot to L3 self-operated or L1 consortium |
| Bridge/finality risk blocks high-value settlement | Treat L1 as necessary for that segment |

*Decision-layer takeaway: Start with L2 to validate demand. Build L3 as the delivery platform. Keep L1 as a funded option, not a default commitment. Let client signals drive investment, not architectural ambition.*

**Beat 7 — Close: What to decide today vs. what can wait**

Purpose: Narrow leadership's decision scope.

**Decide NOW:**
1. Approve the composite strategy (L2 + L3 + gated L1) vs. single-path commitment
2. Choose target entry point (which customer segment first)
3. Define Mantle's operator positioning (regulated operator vs. technology provider)
4. Authorize Phase 1 team and budget

**Can wait 6–12 months:**
1. L1 go/no-go (depends on PoC results and anchor client evidence)
2. L3 investment scale (depends on tenant demand signals)
3. Full privacy roadmap (depends on Phase 1 learnings)

*Decision-layer takeaway: The presentation asks for a strategic direction and Phase 1 authorization, not a multi-year commitment. Every path can be course-corrected at the 12-month gate.*

---

## 3. Deck Chapter Structure

### Recommended Deck Flow: 35 Main Slides + 15 Appendix Slides

---

#### Chapter 0: Title & Agenda (2 slides)

**Slide 0.1 — Title Slide**
- Title: "Enterprise Blockchain Strategy for Mantle: Three Paths, One Decision"
- Subtitle: "L1 / Enterprise L2 / Enterprise L3 — Architecture, Fit, and Roadmap"
- Date, confidentiality, audience

**Slide 0.2 — Agenda & Reading Guide**
- Chapter list with page numbers
- "How to read this deck: conclusions first, evidence second, appendix for deep-dives"
- 10-minute executive version: Chapters 0, 1, 4, 6, 7 (12 slides)
- 30-minute full version: All chapters (35 slides)

**Purpose**: Orient the audience. Signal that this is a decision document, not a research report.
**Visuals**: Clean agenda layout with chapter icons.
**Dependency**: None — produced as part of final deck assembly.

---

#### Chapter 1: The Decision Question (3 slides)

**Slide 1.1 — The Core Question**
- Key message: "Mantle must decide: extend our L2 for enterprise, build isolated L3 environments, or create a sovereign L1 — each serves a different buyer and requires different investment."
- Visual: Three-path fork diagram with cost/timeline callouts

**Slide 1.2 — Conclusion Preview (BLUF)**
- Key message: "Our recommendation: L2 as market entry, L3 as scalable delivery, L1 as gated strategic option. Start with L2, let client demand drive escalation."
- Visual: Phased timeline with decision gates marked

**Slide 1.3 — Five Decisions Leadership Must Make**
- Key message: "Before engineering proceeds, leadership must answer five questions about target market, operator positioning, privacy commitment, finality commitment, and L1 activation triggers."
- Visual: Decision table (5 rows, each with question + options)

**Purpose**: Anchor the entire presentation. Give leadership the answer upfront so they can evaluate evidence with a hypothesis in mind.
**Dependency**: M6 final deck assembly (all content comes from this narrative framework).

---

#### Chapter 2: Why Enterprise Blockchain Design Has Changed (4 slides)

**Slide 2.1 — "Public Chain + Whitelist" Is Not Enterprise**
- Key message: "If bridge paths, sequencer submission, contract deployment, DA, and finality semantics remain uncontrolled, KYC at the RPC is cosmetic, not architectural."
- Visual: Attack surface diagram showing 7 ingress paths (RPC, sequencer direct, L1 bridge, contract deployment, DA, cross-chain message, admin/governance) — only 1 is gated by simple whitelisting

**Slide 2.2 — What the Market Learned: Four Reference Projects**
- Key message: "Canton, Prividium, Tempo, and Paladin each solved enterprise blockchain differently. The common lesson: enterprise design changes trust boundaries, not just permissions."
- Visual: 2x2 matrix (Privacy Model × Finality Model) placing all four projects

**Slide 2.3 — The EVM Moat**
- Key message: "The market has converged on EVM. Canton's struggle with developer adoption proves that being non-EVM is now a dealbreaker. Every viable enterprise blockchain is EVM-compatible."
- Visual: Ecosystem comparison (EVM developer count vs. non-EVM alternatives)

**Slide 2.4 — Mantle's Unique Position**
- Key message: "Mantle's centralized Sequencer can become a compliance control point, but only if leadership accepts the operator-liability tradeoff. The same visibility that enables screening also makes Mantle part of the regulated operating model."
- Visual: Sequencer-as-compliance-officer diagram showing the control flow

**Purpose**: Establish why this conversation is happening and why the obvious answer (just add KYC) is wrong. Build credibility that we've done the research.
**Visuals**: Attack surface diagram, 2x2 reference project matrix, sequencer reframe.
**Dependency**: WHI-392 (reference project comparison slides) or equivalent M6 issue.

---

#### Chapter 3: The 8 Core Modules (4 slides)

**Slide 3.1 — Module Overview**
- Key message: "Enterprise blockchain is not one design choice — it is 8 interconnected choices. Each choice constrains the others."
- Visual: Octagonal module diagram with connecting arrows showing constraint propagation

**Slide 3.2 — Constraint Propagation: Three Critical Chains**
- Key message: "Privacy determines DA. DA determines L1 relationship. Finality determines settlement capability. Compliance depth determines EVM compatibility risk."
- Visual: Three horizontal propagation chains with callout boxes
  - Privacy → DA → L1 Relationship → Bridge Design
  - Finality → Settlement Semantics → DVP/Payment Capability
  - Compliance Depth → Execution Modification → EVM Compatibility

**Slide 3.3 — The Decision Tree (Gate A through Gate E)**
- Key message: "Five gates determine which path fits your use case: Settlement requirement → Ethereum anchor → Tenant isolation → Compliance depth → Budget/timeline."
- Visual: Flowchart decision tree with 5 gates leading to L1, L2, or L3

**Slide 3.4 — Module Requirements by Use Case**
- Key message: "RWA, payments, DeFi, securities, and supply chain have structurally contradictory requirements. No single architecture covers all five."
- Visual: Heat map matrix (8 modules × 5 use cases, colored by fit)

**Purpose**: Give leadership the analytical framework to evaluate the three paths. This is the vocabulary chapter — if they understand modules and constraints, they can evaluate the comparison independently.
**Visuals**: Module octagon, constraint chains, decision tree flowchart, heat map.
**Dependency**: WHI-393 (module deep-dive slides) or equivalent M6 issue.

---

#### Chapter 4: Three Paths — Architecture and Fit (8 slides)

**Slide 4.1 — Path Overview**
- Key message: "Three architectures, three buyer profiles, three investment levels. None is universally superior."
- Visual: Three-column comparison with architecture thumbnail, buyer profile, and cost/timeline

**Slide 4.2 — Enterprise L2: Architecture**
- Key message: "A separate permissioned L2 alongside public Mantle. Reuses OP Stack, Mantle operations, EVM toolchain, Ethereum settlement. Enterprise controls added via identity-verified RPC, sequencer policy, compliance registry, private DA, bridge filters."
- Visual: L2 architecture diagram showing Mantle L2 ↔ Enterprise L2 ↔ Ethereum L1

**Slide 4.3 — Enterprise L2: Honest Limitations**
- Key message: "Enterprise is a tenant of Mantle-operated systems. Sequencer has default plaintext visibility. Soft confirmation ≠ legal hard settlement. If sequencer does compliance screening, Mantle becomes part of the regulated operating model."
- Visual: Trust boundary diagram showing what the tenant controls vs. what Mantle controls

**Slide 4.4 — Enterprise L3: Architecture**
- Key message: "One enterprise, one chain. Each client gets a dedicated L3 with own sequencer, private DA, access rules, compliance policy. Mantle L2 as common settlement. Ethereum as final anchor."
- Visual: L3 architecture diagram showing multiple L3 chains → Mantle L2 → Ethereum L1

**Slide 4.5 — Enterprise L3: Honest Limitations**
- Key message: "External hard finality bounded by L3 → L2 → L1 chain. Cross-zone atomicity requires explicit design. Zone operational burden is real — each L3 needs sequencer, DA, keys, monitoring, upgrades."
- Visual: Finality waterfall diagram (L3 local → L2 submitted → L2 safe → L1 proven → L1 final)

**Slide 4.6 — Sovereign L1: Architecture**
- Key message: "Independent EVM-compatible chain with permissioned BFT validators, ~600ms deterministic finality, protocol-level compliance via precompiles, native Zones, and optional Ethereum ZK anchoring."
- Visual: L1 architecture diagram with BFT consensus, Zone isolation, optional Ethereum anchor

**Slide 4.7 — Sovereign L1: Honest Limitations**
- Key message: "15–25 people, 18–24 months, highest-cost path. Deep Rust/BFT/ZK/security talent required. New security narrative. DeFi cold-start problem. Only rational with anchor client commitment."
- Visual: Resource/risk callout boxes

**Slide 4.8 — What Each Path Must NOT Promise**
- Key message: "Honest selling requires honest limitations. L1 must not promise fast/cheap launch. L2 must not promise full sovereignty. L3 must not promise instant external finality."
- Visual: Three-column "do not promise" table

**Purpose**: The evidence chapter. Show each path's architecture, strengths, and honest limitations so leadership can evaluate fit against their strategic priorities.
**Visuals**: Architecture diagrams (×3), trust boundary diagram, finality waterfall, resource callouts.
**Dependency**: WHI-394 (L1 slides), WHI-395 (L2 slides), WHI-396 (L3 slides) — or equivalent M6 issues for each path.

---

#### Chapter 5: Horizontal Comparison (5 slides)

**Slide 5.1 — 10-Axis Radar Chart**
- Key message: "Each path has a distinct profile. L1 excels at capability but costs the most. L2 excels at speed-to-market but is structurally limited in sovereignty. L3 excels at scalability but inherits L2 finality."
- Visual: Overlapping radar chart (L1 red, L2 blue, L3 green) across 10 axes

**Slide 5.2 — Finality Deep-Dive**
- Key message: "Finality is the most consequential technical differentiator. L1 BFT: ~600ms–2s hard finality. L2: ~1–2s soft confirmation with proof finality depending on cadence. L3: seconds local, delayed external hard finality."
- Visual: Timeline visualization comparing finality across three paths

**Slide 5.3 — Cost & Team Comparison**
- Key message: "L2: 8–15 people, 8–12 months, lower cost through reuse. L3: 10–15 people, 9–13 months, platform plus per-zone economics. L1: 15–25 people, 18–24 months, highest-cost path with new operating obligations."
- Visual: Stacked bar chart (team size × timeline × cost)

**Slide 5.4 — Three Strategic Weighting Models**
- Key message: "The right path depends on what you optimize for. Fast Revenue → L2. Institutional Settlement → L1. Platform Scale → L3."
- Visual: Three weight-distribution bar charts showing how different priorities change the answer

**Slide 5.5 — Client Fit Matrix**
- Key message: "RWA issuers → L2. Bank internal ledgers → L3. Payment channels → L1. Each client type maps to a path."
- Visual: Client-type × path fit matrix with recommended path highlighted per row

**Purpose**: Enable leadership to compare paths quantitatively and see that the "right answer" depends on which weights they assign.
**Visuals**: Radar chart, finality timeline, cost bar chart, weighting models, client fit matrix.
**Dependency**: WHI-397 (comparison matrix slides) or equivalent M6 issue.

---

#### Chapter 6: Recommendation & Roadmap (6 slides)

**Slide 6.1 — The Composite Strategy**
- Key message: "Don't choose one path. Start L2 for market entry, build L3 as scalable delivery, keep L1 as a gated option. Let client demand drive investment."
- Visual: Layered architecture diagram (Public Mantle → Enterprise L2 → Enterprise L3 → L1 if activated)

**Slide 6.2 — Phase 1 Roadmap (0–12 months)**
- Key message: "Ship Enterprise L2 MVP, deploy first L3 pilot, run L1 PoC — all in parallel. Customer discovery throughout."
- Visual: Gantt-style timeline with three parallel workstreams + customer discovery track

**Slide 6.3 — First 90 Days**
- Key message: "Days 0–15: entry point selection. Days 0–30: L2 architecture + compliance model. Days 15–45: L3 template design. Days 30–60: L2 prototype. Days 30–75: L1 feasibility. Days 45–90: design partner validation. Days 75–90: investment gating."
- Visual: 90-day sprint calendar with milestones

**Slide 6.4 — Decision Gates**
- Key message: "At 12 months, three signals determine where to invest: L2 pilot conversion, L3 tenant demand, L1 anchor client commitment."
- Visual: Decision gate diagram with signal → action mappings

**Slide 6.5 — Phase 2 Scenarios (12–24 months)**
- Key message: "Three scenarios based on Phase 1 signals: (A) Harden L2, (B) Scale L3, (C) Fund L1. Can pursue multiple."
- Visual: Branching scenario tree

**Slide 6.6 — Long-Term Portfolio Vision**
- Key message: "Target state: Public Mantle (open DeFi) → Enterprise L2 (regulated institutional channel) → Enterprise L3 (customer-specific chains) → Enterprise L1 if activated (sovereign settlement). This is two different company shapes: Ethereum rollup provider vs. sovereign financial infrastructure."
- Visual: Layered portfolio diagram with revenue model annotations

**Purpose**: The "what to do" chapter. Convert the analysis into action.
**Visuals**: Layered architecture, Gantt timeline, 90-day calendar, decision gates, scenario tree, portfolio diagram.
**Dependency**: WHI-398 (roadmap slides) or equivalent M6 issue.

---

#### Chapter 7: What Leadership Decides Today (3 slides)

**Slide 7.1 — Decide Now vs. Decide Later**
- Key message: "Today: approve composite strategy, choose entry point, define operator positioning, authorize Phase 1. In 6–12 months: L1 go/no-go, L3 scale, full privacy roadmap."
- Visual: Two-column table (Decide Now | Can Wait)

**Slide 7.2 — Risk Summary**
- Key message: "Primary risk of L2-first: may attract lower-value clients while highest-value institutions reject the operator trust model. Mitigation: parallel L1 PoC as an options purchase."
- Visual: Risk/mitigation table for each path

**Slide 7.3 — Next Steps**
- Key message: "If approved: (1) form enterprise team, (2) begin L2 architecture sprint, (3) schedule 10–20 enterprise interviews, (4) initiate L1 PoC design."
- Visual: Four-step action plan with owners and timelines

**Purpose**: Close the presentation with clear asks and next steps. Leave no ambiguity about what leadership is being asked to decide.
**Visuals**: Decision table, risk matrix, action plan.
**Dependency**: None — produced as part of final deck assembly.

---

#### Appendix (15 slides, estimated)

| Appendix Section | Slide Count | Content |
|-----------------|:-----------:|---------|
| A. Glossary & Acronyms | 2 | Technical terms, layer definitions, abbreviation glossary |
| B. Reference Project Summaries | 3 | Canton, Prividium, Tempo, Paladin — one-page each + comparison table |
| C. Detailed Finality Analysis | 2 | Per-path finality timeline, finality label taxonomy |
| D. 14-Dimension Comparison Matrix | 2 | Full scoring matrix with methodology notes |
| E. Compliance Architecture | 2 | Access cascade, policy enforcement depth, compliance bypass scenarios |
| F. Cost Model Detail | 2 | Team/timeline/cost model, separating M5-backed numbers from finance-model estimates |
| G. Paladin / MPL Integration | 2 | MPL architecture, bridge strategy, deployment timeline, sourced from the Paladin research package |

---

## 4. Recommended Deck Metadata

### Deck Title & Subtitle

**Title**: Enterprise Blockchain Strategy for Mantle
**Subtitle**: Three Paths — L1 / Enterprise L2 / Enterprise L3 — Architecture, Fit, and Decision Roadmap

### Target Slide Counts

| Section | Slide Count |
|---------|:-----------:|
| Title & Agenda | 2 |
| Chapter 1: Decision Question | 3 |
| Chapter 2: Why Design Changed | 4 |
| Chapter 3: 8 Core Modules | 4 |
| Chapter 4: Three Paths | 8 |
| Chapter 5: Comparison | 5 |
| Chapter 6: Recommendation | 6 |
| Chapter 7: Decision & Next Steps | 3 |
| **Main Deck Total** | **35** |
| Appendix | ~15 |
| **Grand Total** | **~50** |

### 5 Core Conclusions the Audience MUST Remember

1. **Enterprise blockchain is not "public chain + whitelist."** KYC at the RPC is cosmetic if 6 other ingress paths remain uncontrolled. Enterprise design changes trust boundaries, not just permissions.

2. **L1, L2, and L3 are not a maturity ladder — they are different products for different buyers.** L1 sells sovereign settlement. L2 sells regulated Ethereum/Mantle access. L3 sells dedicated enterprise environments. Choosing the wrong one for the wrong buyer is worse than choosing none.

3. **Finality is the most consequential technical differentiator — and it is not a UX detail.** It affects accounting, legal certainty, risk limits, bridge release, DVP, payments, and regulatory reporting. Native BFT hard finality and rollup proof finality are different settlement products, not merely different latencies.

4. **The composite strategy (L2 + L3 + gated L1) is stronger than picking a single path.** L2 validates demand fastest. L3 scales enterprise delivery. L1 captures sovereign-finality clients if they materialize. Start with L2 because it reuses Mantle advantages and generates irreplaceable market intelligence.

5. **The most important stop criterion is not technical failure — it is lack of qualified demand.** Do not build enterprise infrastructure for an abstract market. Build for concrete buyers with specific settlement, privacy, compliance, and operational needs. If anchor clients do not appear within 12 months, re-evaluate.

### Main Deck vs. Appendix Allocation

**Main deck** (what every audience member must see): The strategic narrative, comparison framework, recommendation, and decision asks. No code-level implementation details, no deep technical specifications, no exhaustive component breakdowns.

**Appendix** (reference on demand): Detailed finality analysis, full comparison matrices, cost model assumptions, compliance architecture, reference project deep-dives, Paladin/MPL integration details, glossary. Paladin evidence should be attributed to the separate Paladin research package, not to WHI-390.

**Rule of thumb**: If a slide answers "what should we do and why?" → main deck. If a slide answers "how exactly does this work?" → appendix.

### 10-Minute vs. 30-Minute Versions

**10-minute executive version (12 slides)**:
- Chapter 0: Title (1 slide)
- Chapter 1: Decision Question + BLUF + Five Decisions (3 slides)
- Chapter 4: Path Overview + "What Each Path Must Not Promise" (2 slides)
- Chapter 5: Radar Chart + Finality Deep-Dive (2 slides)
- Chapter 6: Composite Strategy + Phase 1 Roadmap (2 slides)
- Chapter 7: Decide Now vs. Later + Next Steps (2 slides)

**30-minute full version**: All 35 main slides in order. Allow 5 minutes for Q&A and appendix references.

---

## 5. Narrative Guardrails

### What Technical Detail to Compress

- **No code-level implementation**: No Solidity, Go hooks, Rust, or circuit definitions.
- **No OP Stack internals**: Say "OP Stack-derived infrastructure" rather than explaining op-node or op-geth.
- **No ZK proof mechanics**: Say "cryptographic proofs" and cite proof timing; do not explain circuits or prover architecture.
- **No consensus protocol details**: Say "BFT consensus with ~600ms–2s deterministic finality" and cite validator assumptions.
- **Reference projects**: One slide per project maximum in the main deck; deeper detail goes to appendix.

### What Must NOT Be Omitted

- **Resource estimates**: Every path must show team size, timeline, and cost posture. Use M5-backed dollars where available; when M5 only provides person-months or per-zone planning economics, label deck numbers as finance-model estimates rather than research conclusions.
- **Risk factors**: Every path must show its primary risk and what would trigger a stop. Leadership must understand downside, not just upside.
- **Decision gates**: The roadmap must show explicit go/no-go decision points with criteria. Open-ended commitments are not acceptable at the decision layer.
- **Honest limitations**: Every path must state what it cannot do and what it must not promise. Overselling kills credibility.
- **Finality semantics**: The difference between soft confirmation and hard settlement must be clear. Conflating them is the #1 enterprise blockchain sales mistake.
- **Operator positioning question**: Whether Mantle becomes a regulated operator or stays a technology provider is a business model choice, not a technical detail. It cannot be deferred.

### Tone

- **Strategic advisory, not academic research**: Write as a strategy consultant presenting options to a board, not as a researcher presenting findings to peers.
- **Conclusions before evidence**: Every chapter opens with the takeaway. Supporting data follows. Audience should know the recommendation before seeing the proof.
- **Honest about tradeoffs, not neutral**: Neutral comparison is useless at the decision layer. State the recommended path and explain why, while being transparent about what you're giving up.
- **L1 cost without dismissal**: Present L1's 18–24 month, highest-cost commitment honestly, but frame it as "the price of sovereign settlement" rather than "too expensive." Some buyers will pay it.
- **L2/L3 limitations without undermining**: Present L2's operator-trust and L3's finality limitations honestly, but frame them as "right for specific buyers."
- **Numbers over adjectives**: "8–15 people for 8–12 months" is better than "relatively affordable." "~600ms vs. ~1 hour" is better than "much faster finality."

### Balance

- **Do not oversell L2** as "enterprise-ready" without acknowledging operator trust, sequencer visibility, and soft finality limitations.
- **Do not undersell L1** as "too expensive" without acknowledging that some clients will pay for sovereign settlement and that the PoC costs a fraction of the full build.
- **Do not oversell L3** as "best of both worlds" without acknowledging external finality limitations and operational complexity.
- **Do not present the composite strategy as risk-free** — the primary risk is that L2-first attracts lower-value clients while highest-value institutions leave for competitors offering sovereign settlement from day one.

---

## 6. M6 Issue Dependency Map

Each chapter maps to one or more downstream M6 tasks:

| Chapter | Downstream M6 Work | Content Source |
|---------|--------------------|----|
| Ch 0: Title & Agenda | Final deck assembly | This document |
| Ch 1: Decision Question | Final deck assembly | This document + WHI-390 executive summary |
| Ch 2: Why Design Changed | Reference project slides | WHI-386 (design overview) + WHI-334–342 (M1 research) |
| Ch 3: 8 Core Modules | Module framework slides | WHI-386 (design overview, sections 2–3) |
| Ch 4: Three Paths | Per-path architecture slides (×3) | WHI-387, WHI-388, WHI-389 (M5 path reports) + WHI-390 |
| Ch 5: Comparison | Comparison matrix slides | WHI-390 (section 3: three-path comparison) |
| Ch 6: Recommendation | Roadmap slides | WHI-390 (sections 4–5: roadmap + decision triggers) |
| Ch 7: Decision & Next Steps | Final deck assembly | WHI-390 (section 5: leadership decisions) |
| Appendix A–G | Appendix slides | All M1–M5 reports as source material |

Each downstream task can be executed independently by a separate AI agent using this narrative framework as its creative brief. The agent needs only this document + the specific source files listed above.
