# WHI-386: Enterprise Blockchain — Core Components & Design Principles Overview
- **Milestone**: M5 — Solution Analysis & Final Delivery
- **Date**: 2026-05-08
- **Status**: Draft
- **Audience**: Technical Decision-Makers (CTO / VP Engineering)

## Document TL;DR

Enterprise blockchain design is not "public chain plus a whitelist." It is a different engineering problem shaped by regulated participants, confidential business data, deterministic settlement expectations, and institutional accountability. The core design shift is from universal public verification to selective verification: the right parties must see enough to validate and audit the transaction, while unrelated parties must not receive sensitive data at all.

The prior research across Canton, zkSync Prividium, Tempo/Zones, Mantle, and industry alternatives points to eight components that must be considered together: execution, consensus/finality, privacy, compliance/identity, access control, data availability/data sovereignty, interoperability, and business components. The hardest constraint is that these components do not move independently. A privacy decision changes the data availability model. A DA decision changes the relationship to Ethereum L1. A compliance decision changes how deep enforcement must sit in the execution path. A finality decision changes whether payment and DVP applications can treat settlement as real.

This overview is the entry point for the three deeper solution paths that follow:

| Follow-up issue | Path | Natural fit |
|---|---|---|
| WHI-387 | Standalone enterprise L1 | Maximum native control, strongest finality and compliance depth, highest build cost |
| WHI-388 | Mantle Enterprise L2 parallel chain | Best balance for Ethereum anchoring and EVM ecosystem reuse, with rollup constraints |
| WHI-389 | Enterprise L3 application chains settling to Mantle L2 | Best fit for tenant/application privacy zones, faster productization, inherited L2 limits |

## 1. Enterprise Blockchain vs Public Chains: Fundamental Differences

> **TL;DR**: Public chains optimize for open participation, globally replicated data, and adversarial verification by anyone. Enterprise chains optimize for known participants, controlled visibility, policy enforcement, and operational accountability. The critical design question is not whether the system is decentralized in the abstract; it is who must verify what, who is allowed to see what, and which organization is accountable when policy, privacy, or settlement fails.

Public blockchains such as Ethereum and public Mantle L2 make one powerful assumption: every full verifier can receive enough data to independently reconstruct state. That design gives censorship resistance, open composability, and public auditability, but it also means that transaction metadata, calldata, balances, and contract state are visible either directly or through derivation from published data. For DeFi, this transparency is a feature. For a bank, payment network, tokenized securities platform, or institutional RWA venue, it is usually disqualifying.

Enterprise blockchains invert the default. They start from known or knowable participants, legal accountability, business confidentiality, and compliance obligations. They still need verifiability, but they do not need every observer to verify every detail. A regulator may need actual transaction data. A counterparty may need only its leg of the trade. A public settlement layer may need only a state commitment and proof. A tenant in another jurisdiction may need no data at all. The result is a design space closer to "selective transparency with enforceable accountability" than to either fully public crypto networks or traditional private databases.

### Fundamental Comparison

| Dimension | Public chain model | Enterprise chain model | Design implication | Concrete examples from prior research |
|---|---|---|---|---|
| **Trust model** | Trustless or trust-minimized: assume unknown adversarial participants, expose data for broad verification | Trust-but-verify: known operators, regulated counterparties, cryptographic or procedural checks | Replace "everyone verifies everything" with role-specific validation, attestations, and audit trails | Canton uses Participants and Synchronizers so only relevant parties validate a projected sub-transaction view (WHI-334, WHI-335). Prividium relies on a trusted operator for DA but uses STARK validity proofs for state correctness (WHI-337, WHI-338). |
| **Data model** | Fully transparent: calldata and state can be reconstructed by public observers | Selective transparency: parties, operators, auditors, and settlement layers see different information | DA, privacy, and audit cannot be afterthoughts; the data routing model is a core architecture decision | Canton's Merkle DAG projections implement need-to-know visibility. Prividium publishes state roots and proofs, not transaction data, to Ethereum. Tempo Zones keep Zone data off L1 while encrypting deposit recipient fields (WHI-339, WHI-340). |
| **Access model** | Permissionless: any valid transaction can be submitted, and most RPC access is open | Permissioned and configurable: network, RPC, transaction, bridge, and contract access may each have policy | Access control must cover every ingress path, including L1 forced transactions in rollup designs | Prividium combines SSO, Proxy RPC, RBAC, and L1 TransactionFilterer. Tempo uses TIP-403 policy precompiles and AccountKeychain. Mantle baseline has no native permissioning (WHI-344, WHI-341). |
| **Compliance posture** | Compliance optional at application layer; protocols usually do not know KYC, AML, or sanctions status | Compliance prerequisite: KYC/KYB, AML/CTF, sanctions, Travel Rule, audit exports, and regulator access shape protocol design | Identity and policy need first-class interfaces; "the app can check it" is insufficient for regulated rails | Tempo TIP-403 makes whitelist/blacklist policies a protocol-level primitive for TIP-20 transfers. Canton can include regulators as Observers. Prividium supports private block explorer roles and ZK-based compliance proof concepts (WHI-346). |
| **Performance model** | Optimize for decentralized security, global replication, and shared blockspace; finality may be probabilistic or economically delayed | Optimize for predictable SLAs, deterministic finality, and use-case-specific throughput | Payment lanes, BFT finality, private sequencers, and specialized zones become rational design choices | Tempo's Payment Lane separates payment gas budget from general traffic. Commonware Simplex BFT targets sub-second finality. Mantle's optimistic fallback and seven-day hard finality are a gap for enterprise settlement (WHI-345, WHI-357). |
| **Operational model** | Node operators are loosely coordinated; users self-custody; protocol changes are public governance events | Operators have contractual obligations, runbooks, data retention requirements, and regulated incident response | Monitoring, audit logs, key management, retention policy, and deployment topology become architecture, not DevOps detail | Prividium's private subnet and Proxy RPC model maps to enterprise operations. Canton Participants keep local stores and audit views. M4's Model C proposes Mantle-operated core with institution-controlled Zone data (WHI-362). |

The contrast can be reduced to one sentence: a public chain earns trust by making state universally reproducible; an enterprise chain earns trust by making obligations, visibility, and verification precisely assignable.

### Why "Permissioned Public Chain" Is Not Enough

A common first proposal is to take an EVM chain, add a whitelist, and call it enterprise-ready. The research shows why that fails.

First, a whitelist does not create data privacy. Mantle baseline can restrict a transaction path in theory, but if the batch data is still published to L1 blobs or calldata, every sensitive call can still be reconstructed by observers. WHI-350 identifies data privacy as Mantle's only Critical gap because it requires changes to DA, execution, bridge metadata, and potentially proof systems.

Second, an RPC whitelist does not cover all ingress paths. In an L2 architecture, L1-originated deposits or forced transactions can bypass the normal RPC path unless the bridge contract and sequencer derivation logic enforce the same policy. WHI-344 and WHI-350 both call out this forced-inclusion path as a key enterprise risk. Prividium's L1 TransactionFilterer exists precisely because middleware-only access control is insufficient.

Third, enterprise compliance often needs non-bypassable execution-time checks. If a token transfer must respect sanctions status, investor qualification, jurisdictional limits, or Travel Rule metadata, contract-layer optional checks are too weak. Tempo's TIP-403 model is instructive because the transfer authorization check sits in the token/precompile path, not in an off-chain policy document.

Fourth, finality matters differently. A public L2 user may tolerate soft sequencer confirmation followed by delayed L1 finality. A bank DVP workflow, xStocks matching engine, or payment terminal cannot treat a seven-day challenge period as settlement. WHI-345 and WHI-357 therefore separate everyday BFT finality from L1/ZK anchoring finality.

### Three Enterprise Reference Archetypes

The M1 research identifies three useful archetypes, each with a different answer to the question "who sees what?"

| Archetype | Representative | Core idea | What it teaches |
|---|---|---|---|
| **Need-to-know ledger** | Canton | Transactions are projected so each participant sees only the sub-transaction data relevant to its rights and obligations | Privacy can be achieved by data routing and contract semantics, not only by heavy cryptography |
| **Private EVM with public proof** | zkSync Prividium | Operator holds private DA and execution data; Ethereum sees state roots and validity proofs | Public settlement can verify correctness without receiving transaction data, but DA becomes an operator trust assumption |
| **Public base plus private zones** | Tempo/Zones | Public L1 provides settlement/payment primitives; private single-sequencer Zones isolate sensitive activity | Multi-tenant privacy often wants physical execution separation, not just function-level permissions |

Mantle starts from a fourth archetype: a public EVM rollup with strong ecosystem compatibility and improving proof infrastructure, but no native enterprise privacy, identity, or compliance layer. That makes it attractive as a base, but it also means the enterprise design cannot be evaluated component by component in isolation. The next section decomposes the components, then Section 3 shows how their constraints propagate.

## 2. Core Component Decomposition

> **TL;DR**: Enterprise blockchain architecture is an eight-component system. Execution determines whether enterprise policies can be enforced inside the EVM path. Consensus determines whether business settlement can be treated as final. Privacy determines the DA model. Compliance and identity determine the depth of protocol modification. Access control determines every ingress boundary. DA determines whether data sovereignty is possible. Interoperability determines whether the chain can connect to public liquidity, other enterprise networks, and legacy systems. Business components convert infrastructure into usable enterprise products.

The following decomposition is not a generic blockchain stack. It is the set of components that the prior research repeatedly found to be design-changing for enterprise scenarios. For each component, the question is not "does the chain have this layer?" Every chain has some form of execution, consensus, and data availability. The enterprise question is whether the layer has the right semantics for regulated, confidential, operationally accountable workflows.

### 2.1 Execution Layer

**Why it needs redesign**

The execution layer is where enterprise policy either becomes real or remains advisory. In a public EVM chain, execution primarily enforces deterministic state transitions, gas accounting, and contract rules. Enterprise systems need more: identity-aware preconditions, compliance precompiles, privacy-aware transaction types, payment lanes, audit hooks, and sometimes custom bridge semantics. If these controls live only in application contracts, sophisticated users can route around them through different contracts, L1-originated messages, delegatecall patterns, or unsupported asset wrappers.

For Mantle, WHI-350 finds no EVM compatibility gap, but a major extension risk. This is a subtle but important distinction. Mantle's current EVM compatibility is a strategic asset, and losing it would damage the developer and liquidity ecosystem. Yet the exact features enterprises need, such as compliance checks, identity registries, encrypted deposit verification, and protected token transfers, require deeper hooks than a normal dApp can provide. The execution problem is therefore to add native capability without turning the chain into a bespoke VM that loses Solidity tooling.

**Core design tradeoff: EVM compatibility vs native enterprise capability**

| Design choice | Benefit | Cost |
|---|---|---|
| Pure Solidity/application-layer controls | Minimal protocol changes; maximum tooling compatibility | Easy to bypass; inconsistent enforcement; every app reimplements policy |
| Predeploy contracts | Upgradeable and EVM-friendly; good for registries and policy lookup | Still may be bypassed unless execution paths are required to call them |
| Precompiles / execution hooks | Non-bypassable and efficient; good for compliance, identity, cryptography | Requires client changes, custom gas accounting, security review, and proof/circuit support |
| Custom transaction types | Clean way to encode enterprise metadata, sponsored fees, batched calls, privacy payloads | Wallet/RPC/tooling changes; rollup derivation and proof systems must support them |
| New execution framework, such as Reth SDK | Maximum modularity for custom chain design | Higher migration cost; new operational and security surface |

**Industry approaches**

| Project | Execution model | Enterprise lesson |
|---|---|---|
| **Canton** | Daml execution with signatories, observers, controllers, consuming choices, and participant validation | The strongest enterprise semantics come from making authorization part of the contract language. The cost is non-EVM adoption friction (WHI-334, WHI-335, WHI-336). |
| **Prividium** | EVM-compatible ZK Stack execution with Proxy RPC and contract/function RBAC around it | EVM compatibility can be preserved, but much enterprise control moves to middleware and operator tooling (WHI-337, WHI-338). |
| **Tempo** | Reth SDK/revm with custom Tempo transaction envelope, TIP-20, TIP-403, AccountKeychain, and Payment Lane | EVM compatibility can coexist with protocol-native payments and compliance when the client is designed for extension (WHI-339, WHI-340). |
| **Mantle baseline** | op-geth/op-node OP Stack execution with custom Mantle extensions and SP1 proof direction | Existing OP Stack compatibility is valuable, but deep enterprise controls increase fork and proof-system complexity (WHI-341, WHI-350). |

The M4 blueprint therefore recommends Reth SDK for a clean enterprise L1 path because it allows custom precompiles, custom transaction types, dual runtime separation, and `no_std`-friendly primitives for future proof systems (WHI-357, WHI-358). For L2/L3 paths, WHI-365 is more conservative: preserve EVM compatibility and add enterprise features through sequencer policy, predeploys, constrained custom transaction formats, and ZK Stack or OP Stack extension points.

**Design principle**

The execution layer should enforce only the rules that must be non-bypassable. Identity lookup, policy registry access, encrypted deposit verification, and compliant token-transfer hooks are candidates for native execution support. Business workflow logic, asset lifecycle policy, and institution-specific controls should stay in contracts or SDKs. The boundary matters because every native execution feature becomes part of the chain's security, proof, and client compatibility surface.

**Primary upstream references**: WHI-334, WHI-335, WHI-337, WHI-339, WHI-340, WHI-350, WHI-357, WHI-358, WHI-365.

### 2.2 Consensus & Finality

**Why it needs redesign**

Enterprise settlement is not satisfied by the same finality semantics as public rollups. A public L2 can offer a fast sequencer confirmation, then rely on delayed L1 settlement, fraud proofs, or later validity proofs. For many DeFi interactions, that may be acceptable. For institutional DVP, tokenized stock trading, payment acceptance, collateral release, or treasury movement, the business system must know when a transaction is final enough to trigger downstream obligations.

WHI-345 frames the gap sharply: Mantle's baseline has soft finality around the sequencer path and hard finality tied to optimistic challenge periods or proof submission assumptions. Enterprises need either deterministic BFT finality in seconds or cryptographic validity finality in minutes, with clear semantics. A receipt that may be economically challenged for days is not settlement for a payment terminal or securities workflow.

**Core design tradeoff: BFT instant finality vs rollup inherited security**

| Option | Finality characteristic | Strength | Weakness |
|---|---|---|---|
| Centralized sequencer soft finality | Seconds, operator-trusted | Simple and fast | Not legally or cryptographically strong enough for high-value settlement |
| Optimistic rollup finality | Fast soft confirmation, delayed hard finality | Strong Ethereum anchoring after challenge period | Challenge delay conflicts with enterprise settlement |
| BFT validator finality | Sub-second to seconds, deterministic under validator assumptions | Excellent business UX and settlement speed | Requires validator governance and trust in 2/3 honest assumption |
| ZK validity finality | Minutes or faster depending on prover and L1 | Mathematical correctness with public verification | Prover cost, proof system maturity, and data availability assumptions |
| Dual finality | BFT for daily operations, ZK/L1 for external settlement | Aligns finality level with business value | More complex semantics and operational monitoring |

**Industry approaches**

| Project | Consensus/finality design | Enterprise lesson |
|---|---|---|
| **Canton** | Sequencer ordering plus Mediator-coordinated two-phase commit. A transaction is final when required participants confirm and the mediator approves. | Enterprise finality can be workflow-specific rather than block-centric; all relevant parties must confirm obligations (WHI-335, WHI-336). |
| **Prividium** | Central sequencer for internal execution; STARK proofs submitted through ZKsync Gateway/Ethereum for validity settlement. | A private operator can provide fast internal finality while external verifiability comes from proof settlement (WHI-337, WHI-338). |
| **Tempo L1** | Commonware Simplex BFT with BLS threshold signatures and sub-second deterministic finality. | Payment-grade settlement benefits from BFT finality rather than rollup challenge semantics (WHI-339, WHI-340). |
| **Tempo Zones** | Single-sequencer `NoopConsensus`, L1-event-driven block production, `head = safe = finalized` inside the Zone. | Zones can simplify consensus when an operator is explicitly trusted, but proof maturity and sequencer availability become key risks (WHI-340). |
| **Mantle baseline** | OP Stack centralized sequencer, L1 batching, SP1 proof direction, optimistic fallback. | Excellent ecosystem fit, but the finality model needs augmentation for enterprise-grade settlement (WHI-341, WHI-345). |

M4 proposes a hybrid: Simplex BFT for operational finality, plus ZK anchoring to Ethereum for public verification and high-value cross-chain settlement (WHI-357, WHI-358). This is not merely a performance optimization. It gives applications a typed finality model: a low-value retail payment can accept BFT finality; an institutional bridge withdrawal can wait for ZK/L1 finality; a DVP contract can enforce a threshold before asset release.

**Design principle**

Finality must be exposed as an application-facing primitive, not buried in node documentation. Enterprise applications need to query finality level, finality source, validator quorum, proof status, and L1 anchoring state. A "FinalityOracle" or equivalent interface becomes a business component because settlement systems will build contractual and operational rules around it.

**Primary upstream references**: WHI-335, WHI-336, WHI-338, WHI-339, WHI-340, WHI-345, WHI-357, WHI-358, WHI-365.

### 2.3 Privacy Layer

**Why it needs redesign**

Privacy is the number one differentiator between public and enterprise blockchain design. In public chains, transparency is the default security model. In enterprise systems, confidentiality is a default business requirement. Transaction data, balances, counterparties, order flow, contract state, investor lists, and compliance metadata may all be commercially sensitive or legally protected.

The privacy problem is not one-dimensional. Different users need different privacy boundaries:

| Privacy subject | Typical enterprise concern |
|---|---|
| Transaction content | Trade terms, payment amounts, settlement instructions |
| Participants | Counterparties, clients, investors, sanctioned-party checks |
| Balances and positions | Treasury exposure, inventory, dark-pool order books |
| Contract state | Asset cap tables, compliance state, issuer metadata |
| Operational metadata | Activity frequency, jurisdiction, liquidity patterns |
| Audit data | Regulator access without public disclosure |

**Core design tradeoff: privacy strength vs auditability vs performance overhead**

More privacy is not always better. A system that hides everything from everyone may satisfy confidentiality but fail audit, AML, or dispute resolution. A system where the operator sees everything may satisfy compliance but create a trust and data breach risk. A ZK-heavy system may reduce disclosure but increase prover cost and implementation complexity. Enterprise privacy is therefore a controlled visibility problem, not simply an encryption problem.

**Three paradigms from prior research**

| Paradigm | Representative | Mechanism | Strength | Limitation |
|---|---|---|---|---|
| **Need-to-Know** | Canton | Merkle DAG transaction projections, Daml authorization, encrypted routing | Finest visibility granularity; no single sequencer sees full transaction content | Hard to port to EVM because it assumes no global shared state and Daml semantics |
| **Prove-Not-Reveal** | Prividium | ZK validity proofs plus Validium off-chain DA | Public settlement verifies correctness without seeing data | Operator still sees full chain data; DA is operator-trusted unless DAC/proof systems mature |
| **L2/L3 Isolation + Encryption** | Tempo Zones | Private single-sequencer Zones, authenticated RPC, ECIES encrypted deposits | Practical multi-tenant privacy; maps well to application-specific zones | Zone sequencer sees plaintext; proof path in current code analysis is immature |

Canton is the most conceptually rigorous privacy model. In a DVP workflow, the buyer, seller, bank, and registrar can each see different parts of the same transaction. The Sequencer sees encrypted messages and routing metadata; the Mediator sees confirmation signals; participants validate only their projected views. That is the purest example of privacy by information minimization (WHI-334, WHI-335).

Prividium takes a different route. The private chain operator sees the data, but Ethereum and external observers receive only state commitments and proofs. This is attractive for a bank consortium where the operator is an accountable entity and external public settlement is valuable. It is less attractive if participants do not want the operator to see all flows (WHI-337, WHI-338).

Tempo Zones are the most portable mental model for Mantle L3s. A Zone is physically isolated execution with authenticated access, private DA, bridge-controlled deposits, and sequencer-enforced policy. The privacy guarantee is operational and architectural first, cryptographic second. ECIES encrypted deposits protect some bridge metadata from L1 observers, but the Zone sequencer still decrypts and enforces policy (WHI-339, WHI-340).

**Mantle implications**

WHI-343 and WHI-350 converge on a key point: Mantle cannot become enterprise-private while continuing to publish all sensitive transaction data to public DA. Encrypting blobs helps confidentiality only until key management fails, and it does not solve GDPR erasure because encrypted data remains permanently published. A credible Mantle enterprise design needs one of the following:

| Path | Privacy approach |
|---|---|
| L1 rebuild | Native Zones with independent DA and sequencer control, plus optional ZK/L1 commitments |
| Enterprise L2 | Validium/private DA mode, possibly with ZK validity proofs and constrained public settlement metadata |
| Enterprise L3 | Application/tenant-specific privacy Zones settling to Mantle L2, with private DA and bridge commitments |

**Design principle**

Choose the privacy boundary before choosing the cryptography. If the boundary is "hide from the public L1," Validium may be enough. If the boundary is "hide from other tenants," Zones may be enough. If the boundary is "hide from the operator," then ZK, MPC, FHE, TEE, or encrypted mempools become relevant, but at much higher maturity and performance cost.

**Primary upstream references**: WHI-334, WHI-335, WHI-337, WHI-338, WHI-339, WHI-340, WHI-343, WHI-351, WHI-357, WHI-359, WHI-366.

### 2.4 Compliance & Identity Layer

**Why it needs redesign**

In enterprise settings, compliance is not optional and identity is not merely a wallet address. A regulated asset network must know whether a participant has passed KYC/KYB, whether a counterparty is sanctioned, whether a transfer triggers Travel Rule obligations, whether an investor is eligible for a security, whether a regulator can inspect relevant data, and whether an audit trail can be produced under legal process.

The public-chain model treats addresses as the atomic identity unit. That is not enough. Enterprises need at least three mappings:

| Mapping | Purpose |
|---|---|
| Legal entity or user -> cryptographic keys | KYC/KYB, user lifecycle, revocation, account recovery |
| Cryptographic keys -> roles and permissions | Trader, issuer, custodian, auditor, regulator, admin |
| Roles and policies -> execution outcomes | Allow, reject, freeze, disclose, route, escalate |

**Core design tradeoff: protocol-level built-in vs contract-layer bolt-on vs middleware add-on**

| Layer | Advantage | Risk |
|---|---|---|
| Middleware compliance | Fast to integrate with Okta, AD, AML vendors, sanctions APIs | Bypass risk; policy may not be cryptographically bound to execution |
| Contract-layer compliance | Flexible, app-specific, easy to upgrade | Every app must implement correctly; wrappers or L1 messages may bypass |
| Protocol/precompile compliance | Non-bypassable and auditable; common policy semantics | Client/proof upgrades; governance and emergency handling become critical |

**Industry approaches**

| Project | Compliance/identity approach | Enterprise lesson |
|---|---|---|
| **Canton** | Daml signatories/observers/controllers, topology management, Party-to-Participant mapping, package vetting, regulator as Observer | Compliance can be embedded into workflow semantics and visibility, but it depends on Daml and participant topology (WHI-334, WHI-335). |
| **Prividium** | SSO/OIDC or SIWE authentication, JWT-wallet binding, RBAC, Private Block Explorer, Merkle exports, ZK compliance proof direction | Enterprise IAM integration is easiest at the gateway/operator layer; ZK compliance can reduce PII disclosure (WHI-337, WHI-338, WHI-346). |
| **Tempo/Zones** | TIP-403 policy registry, TIP-20 transfer checks, AccountKeychain, Zone policy mirroring | Compliance can be a chain primitive when tokens and transfer semantics are designed around it (WHI-339, WHI-340). |
| **Mantle baseline** | No native compliance or identity; sequencer sees flow but does not enforce compliance | Sequencer visibility is an unused compliance asset, but identity registries and policy engines must be added (WHI-341, WHI-350). |

Tempo's TIP-403 is especially important for design intuition. A whitelist or blacklist policy is not an application note; it is queried during compliant token movement. Prividium contributes the operational pattern: enterprise SSO plus role-aware private explorer and RBAC. Canton contributes the audit pattern: regulators can be participants who receive actual relevant data, not just after-the-fact reports.

M4's compliance/access design turns these into a five-layer model: IAM, authenticated RPC, sequencer policy, precompile/predeploy policy registry, and bridge filtering (WHI-360). The L2/L3 design narrows this to what can realistically be enforced without breaking rollup assumptions, but still requires bridge filters and transaction filters because forced inclusion remains the classic bypass route (WHI-367).

**Design principle**

Identity and compliance should be represented as shared infrastructure, not rebuilt per application. The minimum credible enterprise stack needs an IdentityRegistry, PolicyRegistry, ComplianceCheck interface, audit event stream, revocation path, and bridge ingress policy. The hard question is not whether these exist; it is how deep they must sit to be non-bypassable for the target use case.

**Primary upstream references**: WHI-334, WHI-335, WHI-337, WHI-338, WHI-339, WHI-340, WHI-344, WHI-346, WHI-350, WHI-352, WHI-360, WHI-367.

### 2.5 Access Control Layer

**Why it needs redesign**

Access control is often confused with identity, but it is broader. Identity says who a user or key represents. Access control says which system boundaries that actor may cross. Enterprise blockchains have more boundaries than typical applications:

| Boundary | Example control |
|---|---|
| Network/RPC | Can this user connect, query, or submit? |
| Sequencer/transaction pool | Can this transaction be ordered? |
| L1 bridge ingress | Can this L1-originated message enter the chain? |
| Contract/function | Can this role call this method with these arguments? |
| Token transfer | Can this asset move from this sender to this recipient now? |
| Data/RPC visibility | Can this user query this account, log, or block detail? |
| Admin/governance | Can this party change policy or validator configuration? |

Public EVM chains usually focus on contract-level access control and leave the rest open. Enterprise chains cannot. If the RPC layer is protected but the sequencer accepts direct transactions, the control is weak. If the sequencer is protected but L1 bridge messages can force deposits or contract calls, the control is weak. If token transfers are controlled but read APIs leak balances, the control is incomplete.

**Core design tradeoff: multi-layer granularity vs configuration complexity**

The strongest architecture enforces access at many layers. That also creates more policy surfaces, more failure modes, and more operational burden. A bank can operate a complex policy stack; a developer ecosystem may reject it. The design goal is layered defense with coherent policy inheritance, not a pile of independent allowlists.

**Industry approaches**

| Project | Access model | Strength | Limitation |
|---|---|---|---|
| **Canton** | Permissioned gRPC, topology state, participant permissions, Daml authorization, package vetting | Deepest protocol-native model | Non-EVM and specialized operational model |
| **Prividium** | Private subnet, Proxy RPC, JWT identity, RBAC, default Forbidden functions, L1 TransactionFilterer | Most directly enterprise-IAM-friendly | Heavy reliance on off-chain admin/operator infrastructure |
| **Tempo/Zones** | TIP-403, AccountKeychain, authenticated Zone RPC, no public P2P for Zones | Strong EVM-level policy primitives and user-key delegation | Custom chain behavior; Zone sequencer trust |
| **Mantle baseline** | Permissionless RPC and transactions, standard bridge paths | High openness and compatibility | No native enterprise boundary coverage |

Prividium's default Forbidden function model is a useful security posture: after deployment, functions are not assumed accessible until authorized. Tempo's AccountKeychain adds a user-experience dimension: root keys can delegate access keys with call scopes, token limits, and expiration. Canton shows the strongest semantic model: authorization is not only a permission table but part of the contract and participant validation process.

**Mantle access-control insertion points**

WHI-350 identifies the highest-value, most feasible modifications:

| Insertion point | Why it matters |
|---|---|
| RPC authentication gateway | Fast IAM integration, audit logging, rate limiting |
| Sequencer policy engine | Central control point already sees transaction flow |
| L1 bridge whitelist/filter | Prevents forced L1 ingress from bypassing enterprise rules |
| IdentityRegistry predeploy | Common on-chain source for policies |
| Token Transfer Hook | Non-bypassable compliant asset movement |
| Compliance audit log | Evidence for regulators and internal control |

**Design principle**

Every ingress path must be listed and explicitly assigned to a control layer. A design that protects only normal user RPC traffic is not enterprise access control. The reference checklist is: RPC, direct sequencer submission, peer/network layer, bridge ingress, contract calls, token movement, data reads, admin actions, emergency actions, and cross-chain messages.

**Primary upstream references**: WHI-334, WHI-335, WHI-337, WHI-338, WHI-339, WHI-340, WHI-344, WHI-350, WHI-352, WHI-360, WHI-367.

### 2.6 Data Availability & Data Sovereignty

**Why it needs redesign**

Data availability is the component where public-chain security most directly conflicts with enterprise privacy. In a classic rollup, transaction data is published so anyone can reconstruct the state or exit safely. In an enterprise setting, that same publication can reveal confidential business data and may violate data localization, retention, or deletion requirements.

Data sovereignty adds additional constraints:

| Requirement | Architecture impact |
|---|---|
| No sensitive transaction data on a public chain | Requires Validium/private DA, encrypted metadata, or no public DA for sensitive flows |
| GDPR erasure or retention controls | Favors off-chain controlled storage, not permanent L1 blobs |
| Jurisdiction-specific data residency | Requires Zone/tenant-specific storage locations |
| Regulator access | Requires audit DA and selective disclosure, not only deletion |
| Disaster recovery and user exit | Requires data escrow, DAC, commitments, or institutional recovery processes |

**Core design tradeoff: on-chain DA vs off-chain DA vs hybrid**

| DA model | Strength | Enterprise weakness |
|---|---|---|
| Public on-chain DA | Maximum independent reconstructability and ecosystem trust | Public visibility, permanent storage, GDPR/data localization conflict |
| Encrypted public DA | Preserves rollup data publication while hiding plaintext | Permanent ciphertext, key risk, metadata leakage, no true erasure |
| Operator-held Validium DA | Strong privacy and operational simplicity | Data availability trust in operator; exit guarantees need separate design |
| DAC/private DA network | Better distribution and governance than single operator | More operational complexity and validator/committee trust |
| Hybrid DA | Routes public and private data to different backends | More complex derivation, proof, and interoperability semantics |

**Industry approaches**

| Project | DA/data sovereignty model | Enterprise lesson |
|---|---|---|
| **Canton** | No global rollup DA; each Participant stores its own projected data | Data minimization is strongest when unrelated parties never receive data in the first place (WHI-334, WHI-335). |
| **Prividium** | Validium: transaction data stays with operator/private storage; Ethereum receives proof/state commitments | Public verification and private DA can coexist, but DA is a trust and recovery problem (WHI-337, WHI-338). |
| **Tempo Zones** | Zone transaction data not published to L1; sequencer holds Zone state; L1 sees batch commitments and bridge events | Physical execution isolation plus private DA is practical for application/tenant zones (WHI-339, WHI-340). |
| **Mantle baseline** | L1 blobs/calldata with OP Stack derivation; historical EigenDA/Alt-DA paths and current public blob model | Existing Alt-DA interfaces are useful, but public DA is structurally incompatible with private enterprise data (WHI-341, WHI-350). |

WHI-357 and WHI-359 propose hybrid DA: public data goes to public DA, Zone data goes to operator/private storage, and audit data goes to encrypted archival storage with regulator access controls. This is not just an optimization. It is the only way to reconcile public verifiability, private business data, and regulatory retention.

For L2/L3 paths, WHI-366 makes the constraint sharper: if the design remains a pure rollup, privacy is limited because settlement metadata and data commitments remain public. A Validium L3 can keep transaction data private while settling commitments to Mantle L2, but it must solve DAC/operator trust, emergency exit, and proof availability.

**Design principle**

Do not decide DA after deciding the chain type. The DA model determines whether the chain is a rollup, Validium, hybrid, or enterprise database with proofs. If sensitive data cannot be placed on a public chain, a pure rollup is not the right primitive for that data path.

**Primary upstream references**: WHI-337, WHI-338, WHI-339, WHI-340, WHI-341, WHI-345, WHI-350, WHI-357, WHI-359, WHI-366.

### 2.7 Interoperability

**Why it needs redesign**

Enterprise chains cannot live as isolated ledgers. They must connect to public liquidity, Ethereum settlement, other enterprise networks, custodians, exchanges, banks, ERP systems, payment processors, regulatory reporting systems, and sometimes SWIFT or CCIP-style messaging rails. Interoperability is therefore not just bridging tokens. It includes asset movement, message verification, identity and compliance portability, audit evidence, and legacy-system integration.

WHI-347 decomposes enterprise interoperability into four dimensions:

| Dimension | Need | Challenge |
|---|---|---|
| Enterprise chain <-> Ethereum | Liquidity, settlement, proof anchoring, bridge assets | L1 data visibility and settlement latency |
| Enterprise chain A <-> enterprise chain B | Atomic cross-organization transactions | Trust, privacy, legal accountability |
| Enterprise chain <-> legacy systems | ERP, SWIFT, databases, custody, compliance tools | Semantic mapping and operational reliability |
| Platform-internal Zone/Domain interop | Multi-zone asset movement and shared policy | Atomicity, latency, and policy propagation |

**Core design tradeoff: native bridging vs third-party bridges vs messaging protocols**

Native bridges give protocol-level semantics and policy control, but they are expensive to build and secure. Third-party bridges provide ecosystem reach, but add external trust and compliance ambiguity. Messaging protocols such as CCIP can standardize connectivity but may not understand the chain's internal identity, privacy, or finality semantics. Enterprise systems often need all three: native bridges for core settlement, standard messaging for ecosystem integration, and legacy adapters for operations.

Enterprise interoperability also has an identity problem that public bridge designs usually ignore. Moving a token is not enough if the receiving chain cannot verify investor eligibility, sanctions status, issuer restrictions, custody authority, or regulator access rights. A bridge for a regulated asset must therefore carry more than `(token, amount, recipient)`. It may need a credential reference, policy version, jurisdiction tag, finality level, disclosure handle, and audit trail pointer. This is why WHI-347 treats interoperability as a compliance and semantic problem, not only a message-passing problem.

Atomicity is the second hard issue. A retail bridge can tolerate asynchronous lock/mint or burn/release steps. An enterprise DVP or cross-bank settlement workflow may require both legs to succeed or both to abort. Canton solves this inside its own model with cross-domain coordination through Synchronizers and participant confirmation. Ethereum-anchored EVM systems more often rely on bridge messages and delayed finality, which means application designers must explicitly handle in-flight risk, timeout, reversal, and evidence generation. For CTO-level architecture, the question is therefore: "what is the maximum business value that can be in a non-atomic bridge state?"

**Industry approaches**

| Project | Interop model | Enterprise lesson |
|---|---|---|
| **Canton** | Global Synchronizer and cross-domain reassignment for enterprise workflows | Strong for bank-to-bank coordination, shared obligations, and virtual global ledger semantics. The tradeoff is limited public EVM liquidity and a specialized Daml/Canton integration model (WHI-334, WHI-335, WHI-347). |
| **Prividium** | ZKsync Gateway/Ethereum settlement with STARK proofs | Strong for private EVM chains that want Ethereum-verified correctness and public liquidity access. Its bridge story is proof-centric, but compliance credentials and DA recovery remain operator/system design questions (WHI-337, WHI-338). |
| **Tempo/Zones** | ZonePortal for L1 <-> Zone deposits, withdrawals, encrypted deposits, and batch commitments | Strong reference for Mantle L2 -> L3 enterprise Zones because the portal boundary can enforce policy, protect some metadata, and keep Zone data private (WHI-339, WHI-340). |
| **Mantle baseline** | OP Stack bridge and Ethereum settlement | Strong EVM/public-liquidity compatibility and familiar bridge tooling, but optimistic delay, public DA, and lack of enterprise identity semantics limit regulated asset movement (WHI-341). |

M4's L1 path proposes a ZK bridge and EnterpriseChainVerifier to connect a standalone enterprise chain back to Ethereum while keeping operational finality local (WHI-362). The L2/L3 path instead leans into inherited bridge infrastructure and builds application-specific ZonePortal-style contracts on top of Mantle (WHI-368). The design choice depends on whether the system's primary interoperability need is public Ethereum liquidity or enterprise/private Zone movement.

**Mantle implications**

Mantle's current advantage is not that it already solves enterprise interoperability. It is that it speaks the EVM/Ethereum interface that most wallets, custodians, indexers, exchanges, and Solidity teams understand. The enterprise design should preserve that advantage while adding three missing semantics: bridge messages that carry compliance context, finality labels that downstream systems can rely on, and privacy-preserving commitments for private DA or Zone state. For L3 paths, the most direct pattern is a ZonePortal-like bridge from Mantle L2 to an enterprise L3. For L2 paths, the bridge must also address forced-inclusion policy and public settlement metadata.

**Design principle**

Bridge verification must match the source chain's privacy and finality model. A bridge from a private Validium cannot require raw transaction data on L1. A bridge from a BFT chain must know whether it accepts BFT signatures, ZK proofs, or L1-anchored state roots. A bridge for regulated assets must also carry policy and identity context, not only token balances.

**Primary upstream references**: WHI-334, WHI-335, WHI-337, WHI-338, WHI-339, WHI-340, WHI-341, WHI-347, WHI-357, WHI-362, WHI-368.

### 2.8 Business Components Layer

**Why it needs redesign**

Enterprise blockchain infrastructure does not become useful until it offers business-level primitives. A chain may have privacy, finality, compliance, and DA, but a bank or asset issuer still needs standardized ways to issue assets, enforce transfer rules, route payments, integrate custody, process DVP, generate audit evidence, and expose developer SDKs.

This layer bridges low-level blockchain mechanics and enterprise workflows. It should not replace the underlying enforcement layers. Instead, it composes them into reusable components that application teams can adopt without re-deriving the entire architecture.

**Core business components**

| Component | Purpose | Dependencies |
|---|---|---|
| Asset issuance framework | Tokenize RWA, securities, deposits, stablecoins, fund shares | Identity, compliance, transfer hooks, audit, metadata |
| Compliant transaction routing | Route transactions through the correct Zone, DA path, policy engine, and finality requirement | Access control, privacy, DA, finality |
| Payment gateway | Stablecoin payments, merchant flows, B2B settlement, multi-currency fee handling | Payment Lane, identity, sanctions screening, finality |
| Custody abstraction | Institutional custody, key policy, approvals, account recovery, delegated keys | Identity, AccountKeychain/WebAuthn, audit logs |
| DVP / settlement engine | Atomic asset-vs-payment settlement with finality checks | Finality oracle, asset standards, compliance |
| Audit and regulator portal | Role-based inspection, exports, evidence, retention | Privacy, compliance, audit DA |
| Developer SDKs | Reduce integration friction for enterprise app teams | All above components |

**Industry approaches**

| Project | Business-component pattern | Enterprise lesson |
|---|---|---|
| **Canton** | Daml Finance libraries, templates for rights and obligations, Observer-aware workflows, DVP-style financial primitives | A mature enterprise ledger should make financial concepts first-class. Asset lifecycle, entitlement, consent, and disclosure should not be rebuilt from generic token contracts each time (WHI-334, WHI-335). |
| **Prividium** | EVM application compatibility plus private explorer, RBAC, SSO, and operator-managed enterprise deployment | Business adoption improves when existing Solidity apps and enterprise IAM can be reused. The cost is that many business controls depend on operator tooling rather than protocol-native standards (WHI-337, WHI-338). |
| **Tempo/Zones** | TIP-20, stablecoin-denominated fees, Payment Lane, AccountKeychain, TIP-403 policies, encrypted Zone deposits | Payment products need more than ERC-20 transfers. They need fee predictability, user-friendly keys, policy-aware transfers, and throughput isolation at protocol level (WHI-339, WHI-340). |
| **Mantle baseline** | Public EVM/DeFi ecosystem, bridge assets, gas oracle, meta-transaction precedent, but no dedicated enterprise component layer | Mantle provides composability and tooling, but enterprise products need new standards above the base EVM: compliant asset issuance, DVP finality checks, audit portals, and Zone routing (WHI-341, WHI-350). |

M4's business component design generalizes these into MIP-style standards for Mantle enterprise paths: compliant token standards, asset lifecycle engines, DVP settlement, Payment Lane routing, Travel Rule support, oracle integration, and governance patterns (WHI-361). The L2/L3 counterpart reuses more existing standards, such as ERC-3643, ERC-4337, and ERC-725-style identity patterns, because preserving ecosystem compatibility is more important there (WHI-367).

**Mantle implications**

Mantle should not try to make every enterprise application write its own compliance token, KYC registry, payment router, and audit export logic. The reusable layer should define a small set of opinionated primitives: a compliant asset standard, a policy-aware transfer interface, a DVP settlement module that queries finality level, a payment gateway that understands lane routing and fee sponsorship, and an audit/regulator portal backed by selective disclosure. For an L2 path, these should look like familiar ERC-style extensions. For an L3 Zone path, they should become the default application template for new enterprise Zones. For a standalone L1, they can be native MIP standards with stronger protocol enforcement.

**Core design tradeoff: domain specificity vs ecosystem composability**

| Approach | Advantage | Risk |
|---|---|---|
| Highly native business standards | Excellent UX and compliance for target use cases | Harder for generic DeFi and wallets to integrate |
| Existing ERC standards plus extensions | Faster ecosystem adoption | Enforcement may be weaker or inconsistent |
| SDK-first abstraction | Hides complexity from developers | SDK becomes a trusted middleware layer unless protocol checks back it |

**Design principle**

Business components should expose the enterprise stack as a product surface: "issue a compliant asset," "settle DVP at finality level X," "route this payment through a low-fee lane," "grant regulator Y access to audit period Z." If application teams must manually stitch identity, policy, DA, bridge, and finality checks for every workflow, the architecture has not solved the enterprise problem.

**Primary upstream references**: WHI-334, WHI-337, WHI-339, WHI-340, WHI-357, WHI-361, WHI-367.

## 3. Component Interdependency & Constraint Map

> **TL;DR**: The enterprise blockchain design space is constrained by dependency chains. You cannot choose privacy without choosing DA. You cannot choose compliance depth without affecting execution compatibility. You cannot choose finality without affecting settlement product design. The correct architecture is the one whose constraint chain matches the target business narrative.

The eight components above form a coupled system. The most common design mistake is to choose a chain category first and then try to retrofit missing features. The research suggests the opposite: start from the business constraints, trace how they propagate, and then choose L1, L2, or L3.

### Constraint Propagation Diagram

```
                              Business Narrative
                                      |
          +---------------------------+---------------------------+
          |                           |                           |
      Payment SLA                 RWA / Securities             Enterprise Tenant
  (>10K TPS, sub-sec)          (privacy + compliance)        (data sovereignty)
          |                           |                           |
          v                           v                           v
  Consensus / Finality          Privacy Boundary              Data Residency
          |                           |                           |
          v                           v                           v
  BFT or ZK finality        DA cannot be public L1        Zone/operator DA needed
          |                           |                           |
          v                           v                           v
  Settlement semantics       Chain-to-L1 relationship      Deployment topology
          |                           |                           |
          v                           v                           v
  DVP / payment gateway      Bridge proof format           Ops / audit / retention


Compliance Narrative
        |
        v
KYC/KYB + AML + Travel Rule
        |
        v
Policy must be non-bypassable
        |
        +----------------------+-----------------------+
        |                      |                       |
        v                      v                       v
Authenticated RPC       Sequencer policy       Execution/bridge checks
        |                      |                       |
        +----------------------+-----------------------+
                               |
                               v
                 EVM compatibility and fork depth risk


Interop Narrative
        |
        v
Ethereum liquidity + enterprise privacy + legacy systems
        |
        +----------------------+-----------------------+
        |                      |                       |
        v                      v                       v
Public proof/anchor      Private DA commitments     Legacy adapters
        |                      |                       |
        v                      v                       v
Bridge verifier design   Selective disclosure       SDK/API design


Identity Portability Narrative
        |
        v
Protocol-native credentials + enterprise IAM
        |
        v
Cross-chain regulated asset movement
        |
        v
Bridge messages must carry credential, policy, jurisdiction,
finality, and disclosure context
        |
        v
Interop protocol design and wallet/custody integration
```

### Key Propagation Chains

| Chain | Propagation | Design result |
|---|---|---|
| **Consensus -> finality -> settlement** | If finality is optimistic and delayed, DVP/payment applications cannot treat settlement as complete. The architecture needs BFT, ZK, or explicit dual-finality semantics. | L1 path can use BFT for daily finality and ZK/L1 for external settlement. L2/L3 paths can support many enterprise workflows but struggle with sub-second hard finality. |
| **Privacy -> DA -> L1 relationship -> interoperability** | If sensitive data cannot be public, DA cannot be standard rollup DA. If DA is private, the L1 relationship must use commitments/proofs rather than raw data. Bridges must verify commitments without exposing payloads. | Validium/private DA and Zone architectures become central for enterprise privacy. Pure rollups fit public or low-sensitivity flows better. |
| **Compliance -> execution depth -> EVM compatibility** | If compliance must be non-bypassable, it must sit at sequencer, execution, transfer, or bridge level. Deeper enforcement means more client/proof/tooling changes. | L1 gives maximum enforcement depth; L2/L3 preserve ecosystem compatibility but must accept mitigation complexity. |
| **Access control -> forced inclusion -> bridge model** | Permissioned access must cover L1-originated messages. Filtering L1 ingress protects compliance but weakens the censorship-resistance/escape-hatch story. | Enterprise rollups must explicitly choose regulated ingress control over pure permissionless escape semantics. |
| **Payment performance -> lane design -> token standard** | Payment SLAs require traffic isolation. Traffic isolation needs stateless classification or reserved capacity. That pushes token/address standards into consensus or execution design. | Tempo-style Payment Lane or equivalent becomes necessary for high-volume payment narratives. |
| **Data sovereignty -> storage layers -> operating model** | GDPR erasure and regulatory retention pull in opposite directions. Sensitive business data must be deletable or regionally stored; audit evidence must be retained and disclosed when authorized. | Separate Zone DA, audit DA, and public commitments. Deployment model must define who operates each. |
| **Ethereum safety -> proof system -> cost/ops** | Institutions may want Ethereum anchoring, but proof generation, L1 gas, relayers, and verifier contracts become operational dependencies. | L1 path treats Ethereum anchoring as optional verification. L2/L3 paths treat L1/L2 settlement as core infrastructure. |
| **Identity standard -> credential portability -> bridge message format -> interop protocol** | If identity and compliance status are protocol-native, cross-chain transfers must carry attestations, policy versions, and disclosure references. Otherwise a token can move to a chain that cannot verify whether the holder is eligible. | Regulated bridges need identity-aware message formats and custody/wallet support, not only token lock/mint mechanics. |

### Component Dependency Matrix

| Component | Constrains | Is constrained by |
|---|---|---|
| Execution | Compliance enforcement, custom tx types, business SDKs | EVM compatibility, proof system, client framework |
| Consensus/finality | Payment/DVP UX, bridge latency, legal settlement semantics | Validator governance, proof strategy, Ethereum anchoring |
| Privacy | DA model, RPC visibility, audit workflow | Operator trust, regulatory disclosure, performance budget |
| Compliance/identity | Access control, token transfers, audit, bridge ingress | Legal requirements, IAM integration, execution depth |
| Access control | RPC, sequencer, bridge, contract, data reads | Identity source, governance, forced-inclusion model |
| DA/data sovereignty | Privacy, GDPR, proof/bridge design | Rollup/Validium choice, operator/DAC trust |
| Interoperability | Settlement liquidity, external asset movement, legacy integration | Finality, privacy, proof format, standards |
| Business components | Developer adoption and product fit | All lower-layer primitives |

This map explains why the next three issues are separated by implementation path. The same component list exists in each path, but the constraints bind differently. A standalone L1 can redesign execution, consensus, DA, and compliance natively. A parallel L2 must preserve enough Ethereum/rollup compatibility to justify itself. An L3 can isolate tenants and applications, but it inherits finality, bridge, and settlement constraints from Mantle L2.

## 4. Key Decision Tree for Enterprise Blockchain Design

> **TL;DR**: The first decision is not "L1, L2, or L3." The first decision is which constraints are non-negotiable: privacy boundary, finality requirement, compliance depth, Ethereum anchoring, ecosystem compatibility, and delivery constraints. The path selection follows from those answers.

### Decision Tree

```
Start: What is the primary enterprise product?
  |
  +-- A. High-value regulated settlement, xStocks, institutional DVP,
  |      payment rail requiring sub-second deterministic finality?
  |        |
  |        +-- Yes:
  |        |     Need native finality, deep compliance, private DA, custom lanes.
  |        |     Prefer WHI-387 standalone enterprise L1 unless Ethereum rollup
  |        |     compatibility is more important than settlement semantics.
  |        |
  |        +-- No:
  |              Continue.
  |
  +-- B. Must preserve Ethereum L1 security inheritance and Mantle/EVM
  |      ecosystem compatibility as the core strategic value?
  |        |
  |        +-- Yes:
  |        |     Can sensitive transaction data remain outside public DA through
  |        |     Validium/private DA, with some rollup constraints accepted?
  |        |       |
  |        |       +-- Yes: Prefer WHI-388 Mantle Enterprise L2 parallel chain.
  |        |       +-- No: Requirements conflict; revisit privacy or anchoring.
  |        |
  |        +-- No:
  |              Continue.
  |
  +-- C. Is the product naturally tenant/application-specific, where each
  |      customer or use case benefits from an isolated execution environment?
  |        |
  |        +-- Yes:
  |        |     Prefer WHI-389 Enterprise L3 application chains settling to Mantle L2.
  |        |
  |        +-- No:
  |              Continue.
  |
  +-- D. Are the needs mostly IAM, compliance gating, and audit over otherwise
  |      public or semi-public assets?
  |        |
  |        +-- Yes:
  |        |     A lighter Enterprise L2 or M3-style retrofit may be enough.
  |        |
  |        +-- No:
  |              Continue.
  |
  +-- E. Is the organization prepared for the budget, team size, security
         review, validator/prover operations, and 18-24 month horizon of a
         native enterprise chain?
           |
           +-- Yes:
           |     L1 remains viable if the product constraints require it.
           |
           +-- No:
                 Prefer WHI-388 L2 or WHI-389 L3, even if the long-term
                 architecture may later migrate toward L1.
```

### Decision 1: What Is the Privacy Boundary?

| Answer | Architecture implication |
|---|---|
| Hide from the public internet only | Private RPC and permissioning may be enough for non-sensitive data, but not for transaction privacy |
| Hide from Ethereum/L1 observers | Need Validium/private DA or L3 Zone; pure rollup DA conflicts with the requirement |
| Hide from other tenants | Need Zone/domain isolation and scoped RPC/data access |
| Hide from the operator | Need advanced cryptography or trusted execution roadmap; none of the near-term patterns fully solve this |
| Disclose to regulators only | Need Observer/private explorer/selective disclosure and audit DA |

This decision often eliminates pure L2 rollup designs for sensitive enterprise workflows. If raw or derivable data cannot be published to L1, the solution must move toward Validium, hybrid DA, or Zone isolation.

### Decision 2: What Finality Does the Business Treat as Settlement?

| Finality requirement | Suitable paths |
|---|---|
| Seconds-level soft confirmation is enough | M3 retrofit, L2, or L3 may work |
| Deterministic sub-second business finality | Standalone L1 with BFT is the cleanest fit |
| Minutes-level cryptographic proof finality | ZK L2 or L1 with ZK anchor can work |
| Seven-day hard finality unacceptable | Avoid optimistic-only settlement for the critical path |
| Different finality levels by transaction value | Dual finality model: BFT for operations, ZK/L1 for external settlement |

Finality must be matched to business consequence. A payment gateway and a high-value bridge withdrawal should not necessarily use the same confirmation threshold.

### Decision 3: How Deep Must Compliance Enforcement Be?

| Compliance depth | Architecture implication |
|---|---|
| Best-effort monitoring | Middleware and analytics may be enough |
| User/role gating | IAM + Proxy RPC + RBAC is required |
| Non-bypassable token transfer controls | Execution/precompile/transfer hook needed |
| L1-originated ingress must be controlled | Bridge filter/TransactionFilterer required |
| Regulator must see real transaction data | Observer/private explorer/selective disclosure needed |
| Sanctions/PII cannot be shared | ZK compliance proof roadmap needed |

This decision determines how much the execution layer must change. If compliance is a legal prerequisite, optional dApp checks are not enough.

### Decision 4: Is Ethereum Anchoring a Security Requirement or a Market Requirement?

Ethereum anchoring can mean different things:

| Meaning | Design consequence |
|---|---|
| Public liquidity access | Bridges and EVM compatibility matter most |
| Security inheritance | L1-verified proofs or rollup settlement matter |
| Regulatory comfort | Public commitments and auditability may be enough |
| Ecosystem tooling | Preserve Solidity, wallets, RPC, indexers |
| Brand/strategic continuity with Mantle | L2/L3 path becomes more attractive |

A standalone L1 can still anchor to Ethereum with ZK proofs, but it no longer inherits Ethereum as a rollup in the same way. A parallel L2 or L3 keeps the strategic link stronger but accepts settlement and DA constraints.

### Decision 5: What Is the Product Surface?

| Product surface | Component emphasis | Likely path |
|---|---|---|
| Institutional settlement network | Finality, privacy, regulator access, DVP | WHI-387 L1 |
| Enterprise DeFi/RWA platform tied to Mantle liquidity | EVM compatibility, bridge, compliance, hybrid DA | WHI-388 L2 |
| Tenant-specific bank/payment/customer environments | Zone isolation, private DA, app-specific policy | WHI-389 L3 |
| Stablecoin payment rail | Payment Lane, sub-second finality, low fees, sanctions | WHI-387 or WHI-389 depending on scale |
| Tokenized securities venue | Identity, transfer restrictions, audit, dark-pool privacy | WHI-387 for native control; WHI-389 for isolated venue |
| Compliance wrapper for public assets | IAM, policy registry, audit logs | L2/M3-style retrofit may suffice |

### Decision 6: What Timeline and Budget Are Realistic?

| Delivery constraint | Architecture implication |
|---|---|
| Need a credible pilot in 3-6 months | Start with L2/M3-style controls: authenticated RPC, sequencer policy, identity registry, audit logs, bridge filter |
| Need a production enterprise chain in 6-12 months | Prefer a parallel L2 or focused L3 with private DA and constrained scope |
| Can fund 18-24 months of protocol engineering | Standalone L1 becomes viable if native finality, privacy, and compliance depth justify it |
| Small protocol/security team | Avoid deep execution or consensus rewrites; use standards and managed infrastructure |
| Large regulated-infrastructure program | Budget for validator/prover operations, formal audits, incident response, data residency, and regulator-facing tooling |

Timeline and budget do not change the technical ideal, but they often eliminate a path. A standalone L1 is the broadest answer technically, but it demands the largest engineering, security, operations, and ecosystem investment. L2 and L3 paths are more constrained, yet they can deliver enterprise-visible capability earlier by preserving Mantle/Ethereum tooling and narrowing the first product surface.

### How the Three Paths Fit Together

The three solution approaches are not mutually exclusive. They occupy different points in the design space:

| Path | Core bet | Best at | Weak at |
|---|---|---|---|
| **WHI-387: Standalone enterprise L1** | Rebuild the stack around enterprise-native execution, BFT finality, hybrid DA, and optional Ethereum ZK anchoring | Native compliance, deterministic finality, performance lanes, data sovereignty | Build cost, ecosystem bootstrapping, validator/governance complexity |
| **WHI-388: Mantle Enterprise L2 parallel chain** | Preserve Ethereum/Mantle strategic alignment while adding permissioning, Validium/private DA, and compliance controls | EVM ecosystem reuse, public settlement story, faster adoption than L1 | Rollup/DA constraints, forced inclusion tradeoffs, limited native finality |
| **WHI-389: Enterprise L3 application chains** | Use Mantle as settlement/base layer while isolating enterprise tenants or applications into private Zones | Multi-tenant privacy, app-specific configuration, product modularity | Inherited L2 finality, bridge complexity, operator/DAC trust |

The decision is not philosophical. It is a product and risk decision:

- Choose **L1** when the business cannot compromise on deterministic finality, native compliance, data sovereignty, or payment-grade performance.
- Choose **L2** when Ethereum/Mantle alignment, EVM ecosystem compatibility, and public settlement are central, and the enterprise use case can accept rollup/Validium tradeoffs.
- Choose **L3** when isolation is the product: one bank, issuer, payment network, venue, or enterprise tenant per Zone, with configurable privacy and policy.

### Bridge to WHI-387, WHI-388, and WHI-389

This overview establishes the component vocabulary and design constraints. The next three documents apply the same framework to concrete architectures:

- **WHI-387** analyzes the standalone L1 path: how to rebuild execution, consensus, privacy, compliance, business components, and interoperability with maximum native control.
- **WHI-388** analyzes the Mantle Enterprise L2 path: how far a parallel L2 can go while preserving Ethereum settlement and Mantle ecosystem compatibility.
- **WHI-389** analyzes the L3 application-chain path: how enterprise Zones can settle to Mantle L2 while isolating privacy, policy, and DA per tenant or business vertical.

The reader should carry forward one principle: there is no single "enterprise blockchain" architecture. There is a set of interdependent design choices. The right architecture is the one whose constraint propagation matches the business narrative, regulatory posture, and operating model.
