# WHI-366: L2/L3 路径 — 隐私 Zone (L3) 与数据可用性架构设计

> **Issue**: WHI-366  
> **Path**: L2/L3 Rollup Path  
> **Dependencies**: WHI-355 (Narrative Analysis), WHI-364 (Fork Analysis), WHI-365 (L2/L3 Execution + Sequencer)  
> **Counterpart**: WHI-359 (L1 Path Privacy + Data Sovereignty)  
> **Status**: In Review  
> **Date**: 2026-05-07

---

## Executive Summary

This document designs the privacy and data availability architecture for the L2/L3 rollup path of Mantle's enterprise blockchain rebuild. In this model, Privacy Zones are not L2s of an L1 — they are **L3s (or Validium) of an L2**, fundamentally altering the trust model, DA strategy, and privacy guarantees compared to the L1 BFT path (WHI-359).

The central, L2-unique challenge is the **Sequencer Privacy Problem**: unlike the L1 path where BFT validators see what they execute (consistent), the L2 Sequencer potentially sees **all transaction plaintext** — a severe privacy leak that does not exist in any L1 architecture. This document addresses this challenge as the primary design constraint and proposes a phased mitigation strategy.

**Key architectural decisions:**

1. **Privacy Model**: Recommend **Hybrid B+A** — L3 Privacy Zones (Model B) with Validium DA (Model A) as the default DA backend per Zone. Each Zone is an independent L3 app chain settled on L2, using single-operator Validium for data privacy.
2. **Sequencer Privacy**: Adopt the **"Sequencer-as-Compliance-Officer" paradigm** (Phase 1), evolving to **encrypted mempool + threshold decryption** (Phase 2) for inter-institutional MEV protection.
3. **DA Strategy**: **Hybrid DA** — public transactions use Ethereum Blobs; Privacy Zone data uses operator-controlled Validium; compliance audit data uses encrypted long-term archives with threshold-decryption access.
4. **RPC Architecture**: Four-tier authenticated API gateway with Zone-scoped privacy controls, modeled after Prividium's Proxy RPC but extended for L2's multi-layer data topology.
5. **Cross-Zone Interop**: Phased from non-atomic L2 relay (Phase 1) to Canton-style 2PC and ZK cross-Zone proofs (Phase 3), with Shared Sequencing enabling atomic cross-Zone bundles (Phase 2).

---

## Table of Contents

1. [Privacy Architecture Model Selection](#1-privacy-architecture-model-selection)
2. [Sequencer Privacy Problem and Solutions](#2-sequencer-privacy-problem-and-solutions)
3. [Enterprise DA Hybrid Strategy](#3-enterprise-da-hybrid-strategy)
4. [Authenticated RPC Architecture](#4-authenticated-rpc-architecture)
5. [Cross-Zone Interop Design](#5-cross-zone-interop-design)
6. [Comparison with L1 Path Privacy (WHI-359)](#6-comparison-with-l1-path-privacy-whi-359)
7. [Per-Narrative Privacy Mapping](#7-per-narrative-privacy-mapping)
8. [Implementation Roadmap](#8-implementation-roadmap)
9. [Risk Analysis and Mitigations](#9-risk-analysis-and-mitigations)

---

## 1. Privacy Architecture Model Selection

### 1.1 Model Evaluation

Three candidate privacy models were evaluated against the narrative requirements from WHI-355 and the L2/L3 structural constraints from WHI-364/WHI-365.

#### Model A: Validium Mode

**Architecture**: Transaction data stays off-chain in operator-controlled storage. L1 (Ethereum) receives only `{state_root, STARK_proof_hash}`. A Data Availability Committee (DAC) or single operator guarantees data persistence.

```
Ethereum L1 (State Root + STARK Proof Verification)
        │
Enterprise L2 (Transaction Ordering + State Transitions)
        │
   ┌────┴────────────────────────────────┐
   │  Validium DA Layer                   │
   │  (Data NOT published on-chain)       │
   │                                      │
   │  Storage: Operator's private DB      │
   │  Security: STARK proof (correctness) │
   │  DA guarantee: Operator/DAC trust    │
   └──────────────────────────────────────┘
```

**Strengths:**
- Data never reaches any public chain — strongest privacy baseline
- Near-zero per-tx DA cost (<$0.0001/tx at scale with Airbender GPU prover)
- GDPR-compliant: physical deletion of off-chain data is technically feasible
- Production-validated: Prividium serves 35+ financial institutions with this exact model
- "Math-neutral settlement" — STARK proof verifiable by any party on Ethereum without trusting the operator

**Weaknesses:**
- DA depends on operator/DAC trust — no cryptographic data availability guarantee
- No permissionless escape hatch (fund extraction requires operator Merkle proof)
- Historical auditability restricted to authorized parties (not a weakness for enterprise — it's a feature)

**Enterprise Fit**: **High**. DAC composed of certified institutions maps naturally to permissioned enterprise networks. The single-operator variant (Prividium model) is already in production.

#### Model B: L3 Privacy Zones

**Architecture**: Each Privacy Zone is an independent L3 chain settled on the Enterprise L2. Frameworks: Arbitrum Orbit L3 / OP Stack L3 / ZKsync Hyperchain.

```
Ethereum L1
     │
Enterprise L2 (Public Mainchain + Settlement Layer)
     │
     ├── L3: RWA Zone (Validium DA)
     │   └── Sub-tx privacy: Canton-inspired Merkle DAG projection
     │
     ├── L3: xStocks Zone (Validium DA)
     │   └── ZK order matching engine + dark pool isolation
     │
     ├── L3: Payment Zone (Volition DA)
     │   └── ECIES encrypted deposits + Travel Rule metadata
     │
     └── L3: Custom Zone (configurable)
         └── Per-tenant privacy model selection
```

**Strengths:**
- Zone-level autonomy: each Zone selects its own execution environment, privacy model, and DA strategy
- Physical isolation: Zone state is completely separate from other Zones and L2 public state
- Framework maturity: Arbitrum Orbit L3 and OP Stack L3 are production-ready
- Natural fit for multi-tenant enterprise: each institution or business vertical operates its own Zone

**Weaknesses:**
- Multi-layer latency: L3→L2→L1 adds settlement delay (mitigated by soft finality at each layer)
- Fragmentation: liquidity and composability split across Zones
- Cross-Zone communication complexity: L3-to-L3 requires routing through L2

**Enterprise Fit**: **High**. Maps directly to enterprise organizational structure (one Zone per business unit / compliance jurisdiction).

#### Model C: In-Protocol Privacy

**Architecture**: Privacy as a protocol-level L2 capability — encrypted mempool, encrypted state tree, selective disclosure — without L3 separation.

```
Enterprise L2
├── Public Transaction Domain
├── Private Transaction Domain (protocol-internal encryption)
│   · Encrypted mempool (Sequencer orders without decrypting)
│   · Encrypted state tree (ZK proofs over encrypted state)
│   · Selective disclosure via Viewing Keys
└── Compliance Audit Interface
```

**Strengths:**
- No L3 latency overhead — unified execution environment
- Simpler topology — no multi-chain management
- Potentially strongest privacy (Aztec-like protocol-native encryption)

**Weaknesses:**
- **Deep protocol modification**: requires custom EVM or zkEVM with native encryption support — 12–18 months of additional development vs. existing frameworks
- **Privacy granularity**: one-size-fits-all privacy model cannot satisfy the divergent needs across narratives (WHI-355: RWA needs sub-transaction projection; xStocks needs dark pool isolation; Payments needs Travel Rule compliance)
- **No production precedent**: Aztec's approach is still in development for general-purpose L2; no enterprise deployment exists
- **Ecosystem lock-in**: custom protocol-level changes break standard Ethereum toolchain compatibility

**Enterprise Fit**: **Low-Medium**. Theoretically elegant but practically infeasible within the project timeline. The per-narrative privacy diversity requirement (WHI-355) makes a single protocol-level model insufficient.

### 1.2 Recommendation: Hybrid B+A (L3 Privacy Zones with Validium DA)

**Selected approach: Model B (L3 Privacy Zones) with Model A (Validium) as the default DA backend per Zone.**

This hybrid maximizes both flexibility and privacy:

| Design Dimension | Decision | Rationale |
|---|---|---|
| Zone topology | L3 Privacy Zones (Model B) | Per-narrative privacy customization; physical isolation; organizational mapping |
| DA backend per Zone | Validium (Model A) | Data never on-chain; GDPR-compliant deletion; near-zero DA cost |
| Privacy model per Zone | Configurable (A/B/C per Zone) | RWA Zone uses Canton-style sub-tx projection; xStocks uses ZK dark pool; Payment uses ECIES + Travel Rule |
| Settlement layer | Enterprise L2 | Aggregates Zone state transitions; posts STARK proofs to Ethereum L1 |
| In-Protocol Privacy (Model C) | **Deferred to Phase 3+** | Future option for unified privacy within individual Zones if Aztec-style tooling matures |

**Why not Model A alone?** Validium without L3 separation forces all private transactions into a single execution environment. WHI-355 shows that RWA, xStocks, and Payments have fundamentally different privacy requirements (sub-transaction projection vs. dark pool isolation vs. Travel Rule compliance). L3 Zones allow each narrative to select its optimal privacy model.

**Why not Model C alone?** No production-ready implementation exists. The per-narrative diversity requirement cannot be satisfied by a single protocol-level privacy mechanism. Development timeline (12–18 months additional) is incompatible with the project's delivery schedule.

**Why the hybrid?** L3 Zones provide the organizational structure and isolation; Validium provides the data privacy guarantee; the combination delivers the "best of both" while staying within the capability envelope of production-ready technology (Prividium Validium + Arbitrum Orbit L3 / OP Stack L3 frameworks).

### 1.3 Zone Type Mapping to Privacy Requirements

Based on WHI-355 narrative analysis:

| Zone Type | Privacy Tier | Internal Privacy Model | DA Strategy | Target TPS | Key Regulatory Requirement |
|---|---|---|---|---|---|
| RWA Zone | T3: Sub-Transaction | Canton-inspired Merkle DAG projection — each DvP counterparty sees only its own subtree | Single-operator Validium | 100–500 | SEC Reg D/S/A+, MiCA, MAS; 5–7yr retention |
| xStocks Zone | T3: Sub-Transaction | ZK order matching engine; dark pool execution fully private | Single-operator Validium | 1,000–3,000 | SEC Reg NMS, Reg ATS, Reg SHO; market surveillance |
| Payment Zone | T1: DA-Level | ECIES encrypted deposits; sanitized block data externally | Volition (public summary + private details) | >10,000 | Travel Rule ($3K+), AML/CFT, sanctions screening |
| DeFi Zone | T0: Public | Transparent (global state visibility for composability) | Ethereum Blobs (public L2 DA) | 3,000–5,000 | Minimal — standard DeFi transparency requirements |
| Custom Zone | Configurable (T0–T3) | Per-tenant selection | Configurable | Configurable | Per-jurisdiction |

---

## 2. Sequencer Privacy Problem and Solutions

### 2.1 Problem Statement

**The Sequencer Privacy Problem is the #1 unique challenge of the L2/L3 path.** It does not exist in the L1 BFT path.

In the L1 path (WHI-359), BFT validators see what they execute — this is consistent. Every validator sees the same data, and the consensus protocol ensures this visibility is a feature, not a bug. There is no Sequencer.

In the L2 path, the **centralized Sequencer** occupies a privileged position:

```
Transaction Lifecycle — L2 Sequencer Visibility:

User submits tx → [Sequencer receives PLAINTEXT]
                        │
                        ├── Sees: sender address, recipient, amount, calldata
                        ├── Sees: function signatures, contract interactions
                        ├── Sees: order flow (who is trading what, when, how much)
                        ├── Can: front-run, sandwich, information-extract
                        │
                        ▼
                   Sequencer orders tx into block
                        │
                        ▼
                   L2 Execution (EVM processes tx)
                        │
                        ▼
                   ZK Proof Generation (Airbender STARK)
                        │
                        ▼
                   L1: state_root + proof_hash ONLY
```

**Severity by narrative** (from WHI-355):
- **xStocks**: **CRITICAL**. Sequencer seeing order flow = front-running risk. In securities markets, this is a **criminal offense** (SEC/FINRA rules). A Sequencer operator with order flow visibility in a dark pool environment faces the same legal risk as a broker-dealer trading ahead of client orders.
- **RWA**: **HIGH**. Sequencer seeing DvP counterparty details and asset valuations = competitive intelligence leak. Competing banks would not participate if the Sequencer operator (potentially a competitor) can see their positions.
- **Payment**: **MEDIUM**. Sequencer seeing payment flows = business intelligence leak (competitors could infer revenue, supplier relationships, customer concentration).
- **DeFi**: **LOW**. Standard MEV concerns apply, but DeFi is inherently transparent.

### 2.2 Solution Design: Phased Sequencer Privacy

#### Phase 1 (Months 0–12): Sequencer-as-Compliance-Officer

**Accept the Sequencer's full visibility as a compliance feature, not a privacy defect.**

This is not a compromise — it is a deliberate design choice validated by production systems:
- **Canton**: The Synchronizer (Sequencer equivalent) at Global Synchronizer processes $2T+/month with full ordering visibility. Financial institutions accept this because the Synchronizer operator has legal obligations.
- **Prividium**: 35+ financial institutions, including 5 US banks with $600B+ combined deposits, use a single-operator Sequencer with full transaction visibility.

**Design:**

```
Phase 1: Permissioned Sequencer with Compliance Obligations

User → Authenticated RPC (JWT + wallet verification)
  → Sequencer (FULL VISIBILITY — by design)
     │
     ├── Real-time AML/CFT monitoring
     ├── OFAC sanctions screening (every tx)
     ├── Anomaly detection (unusual patterns)
     ├── Full audit logging (immutable, timestamp-certified)
     ├── FCFS ordering (strict timestamp — no reordering)
     │
     └── Legal framework:
         ├── NDA: Sequencer operator signs binding confidentiality agreements
         ├── Fiduciary duty: Sequencer operator has legal obligation not to exploit information
         ├── Chinese walls: Sequencer operation isolated from operator's trading/business units
         ├── Regulatory oversight: Sequencer audit logs accessible to regulators on demand
         └── Penalties: Financial + legal liability for information misuse
```

**Sequencer Audit Log Schema:**

| Field | Type | Description |
|---|---|---|
| `timestamp` | uint64 | Nanosecond-precision reception time |
| `tx_hash` | bytes32 | Transaction hash |
| `sender` | address | Sender address |
| `zone_id` | uint32 | Target Zone |
| `function_sig` | bytes4 | Function selector |
| `compliance_result` | enum | PASS / REJECT / FLAG |
| `rejection_reason` | string | If rejected: AML, sanctions, policy, etc. |
| `sequencer_node_id` | bytes32 | Which Sequencer node processed this tx |
| `ordering_position` | uint64 | Final position in block |

Audit logs are append-only, hash-chained (each entry includes hash of previous entry), and stored with the same retention requirements as the Zone's regulatory framework.

**FCFS Ordering — MEV Mitigation:**
- Strict First-Come-First-Served: transactions ordered by Sequencer reception timestamp
- No reordering, no insertion, no delay manipulation
- Sequencer publishes ordering commitment before execution — deviation is detectable and slashable
- Already implemented in WHI-365 Sequencer design (Phase 1)

**Limitations:**
- Sequencer operator still *sees* all data — trust is legal/contractual, not cryptographic
- Single point of trust — operator compromise exposes all Zone data
- Does not satisfy xStocks dark pool requirements where *no one* should see order flow

#### Phase 2 (Months 12–24): Encrypted Mempool + Threshold Decryption

**Eliminate Sequencer plaintext visibility for sensitive Zones.**

```
Phase 2: Encrypted Mempool Architecture

Step 1: Encryption
  User encrypts tx with SHARED PUBLIC KEY (of N Sequencer nodes)
  Encrypted tx = Enc(shared_pk, {sender, recipient, amount, calldata})

Step 2: Ordering
  Sequencer receives ENCRYPTED tx (cannot read contents)
  Sequencer orders based on: arrival time (FCFS) + encrypted metadata envelope
  Encrypted metadata: {zone_id, gas_limit, nonce} — Sequencer needs these for ordering

Step 3: Threshold Decryption
  After ordering is committed (ordering is now immutable):
  t-of-N Sequencer nodes each provide partial decryption share
  Combined shares → plaintext tx
  Threshold: t = ⌈2N/3⌉ (e.g., 3-of-5, 5-of-7)

Step 4: Execution
  Decrypted tx executed in order → state transition → STARK proof
```

**Detailed Flow:**

```
┌─────────┐    Enc(shared_pk, tx)    ┌──────────────────────┐
│  User   │ ──────────────────────── │ Encrypted Mempool    │
│  DApp   │    + metadata envelope   │ (Sequencer sees only │
└─────────┘                          │  encrypted blobs)    │
                                     └──────────┬───────────┘
                                                │
                                     FCFS ordering on
                                     encrypted blobs
                                                │
                                     ┌──────────▼───────────┐
                                     │ Ordering Commitment  │
                                     │ (immutable sequence) │
                                     └──────────┬───────────┘
                                                │
                              ┌─────────────────┼─────────────────┐
                              │                 │                 │
                        ┌─────▼─────┐     ┌─────▼─────┐    ┌─────▼─────┐
                        │ Node 1    │     │ Node 2    │    │ Node 3    │
                        │ Partial   │     │ Partial   │    │ Partial   │
                        │ Decrypt   │     │ Decrypt   │    │ Decrypt   │
                        └─────┬─────┘     └─────┬─────┘    └─────┬─────┘
                              │                 │                 │
                              └─────────────────┼─────────────────┘
                                                │
                                     ┌──────────▼───────────┐
                                     │ Threshold Combine    │
                                     │ (t-of-N shares)      │
                                     │ → Plaintext tx       │
                                     └──────────┬───────────┘
                                                │
                                     ┌──────────▼───────────┐
                                     │ EVM Execution        │
                                     │ → State Transition   │
                                     │ → STARK Proof        │
                                     └──────────────────────┘
```

**Threshold Key Management:**

| Parameter | Value | Rationale |
|---|---|---|
| Key type | BLS12-381 threshold keys | Standard for threshold cryptography; efficient pairing-based verification |
| N (total nodes) | 5–9 (certified institutions) | Sufficient decentralization for enterprise; manageable key ceremony |
| t (threshold) | ⌈2N/3⌉ | Byzantine fault tolerance — survives up to ⌊(N-1)/3⌋ compromised nodes |
| Key rotation | Quarterly | Limits exposure window; proactive secret sharing (PSS) enables rotation without ceremony |
| Key ceremony | Distributed Key Generation (DKG) | No single party ever holds the complete key |
| Backup | Each institution stores its share in HSM | Hardware security module — tamper-resistant |

**Compliance Integration with Encrypted Mempool:**

A critical design tension: if the Sequencer cannot read transactions, how does it perform AML/CFT compliance checks?

**Solution: Post-Ordering, Pre-Execution Compliance Window**

```
Encrypted ordering → Threshold decryption → [COMPLIANCE CHECK WINDOW] → Execution

In the compliance check window:
1. Decrypted tx is checked against AML/OFAC/sanctions lists
2. If PASS: tx proceeds to execution
3. If FAIL: tx is rejected, rejection logged, counterparty notified
4. Compliance check is performed by the THRESHOLD GROUP collectively
   (no single node can unilaterally pass/reject)
```

This preserves the compliance guarantee while eliminating pre-ordering information asymmetry. The Sequencer cannot front-run because it cannot read the transaction before ordering is committed.

**Phase 2 Trust Assumption**: 2/3 of N institutional Sequencer nodes are honest. No single node can decrypt transactions alone. Ordering is committed before decryption — MEV is structurally impossible.

#### Phase 3 (Month 24+): TEE-Enhanced Sequencing

**For maximum-security Zones (xStocks dark pools), add hardware-level privacy guarantees.**

```
Phase 3: TEE Sequencer Architecture

┌────────────────────────────────────────────┐
│ Intel SGX / ARM TrustZone / AWS Nitro      │
│ Enclave                                     │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Sequencer Logic                     │   │
│  │ - Receives plaintext (inside TEE)   │   │
│  │ - Orders transactions (FCFS)        │   │
│  │ - Compliance checks (inside TEE)    │   │
│  │ - Produces ordering commitment      │   │
│  │ - Attests execution integrity       │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Host machine CANNOT read enclave memory    │
│  Remote attestation proves code integrity   │
└────────────────────────────────────────────┘
```

**TEE Sequencer Properties:**
- Sequencer operator (host machine) cannot read transaction data — hardware-enforced
- Remote attestation: any party can verify the Sequencer is running the expected code
- Side-channel resistance: SGX v2+ and Nitro Enclaves have mitigations for known side-channel attacks
- Combines compliance (code runs compliance checks inside enclave) with privacy (no human access to plaintext)

**TEE Limitations:**
- Hardware trust: ultimately depends on Intel/ARM/AWS — nation-state adversary could compromise hardware
- Performance overhead: ~10–30% compared to native execution (acceptable for enterprise TPS targets)
- Supply chain risk: TEE hardware availability and vendor lock-in

**Recommendation**: TEE as an **optional enhancement** for high-security Zones (xStocks dark pool). Not required for all Zones.

#### Phase 4 (Speculative): Timelock Encryption

**Transactions encrypted with a timelock puzzle — automatically decryptable after a predetermined time.**

```
Phase 4: Timelock Encryption Flow

User encrypts tx: TLE.Encrypt(tx, target_time = current_block + 10)
  → Sequencer orders encrypted blob (cannot decrypt — insufficient time has passed)
  → At target_time: anyone can decrypt (mathematical guarantee, no key needed)
  → Execution proceeds on decrypted tx
```

**Properties:**
- No threshold key management required
- No TEE hardware dependency
- Mathematical guarantee — no trust assumptions
- Time delay is inherent (the security property IS the delay)

**Limitations:**
- Time delay is fixed and inflexible — unsuitable for low-latency narratives
- Computational cost: generating timelock puzzles is expensive for high-TPS scenarios
- Still experimental — no production-ready implementation for blockchain sequencing

**Recommendation**: Monitor research progress. Not recommended for Phase 1–3 deployment.

### 2.3 Sequencer Privacy Solution Selection by Narrative

| Narrative | Phase 1 | Phase 2 | Phase 3+ |
|---|---|---|---|
| **RWA** | Sequencer-as-Compliance-Officer + NDA + Chinese walls | Encrypted mempool (threshold 3-of-5 institutional nodes) | Optional TEE |
| **xStocks** | Sequencer-as-Compliance-Officer + strict FCFS | Encrypted mempool (**mandatory** for dark pool) | TEE Sequencer (recommended for dark pool) |
| **Payment** | Sequencer-as-Compliance-Officer + ECIES deposits | Encrypted mempool (optional — Travel Rule already requires disclosure) | — |
| **DeFi** | Sequencer-as-Compliance-Officer + FCFS | Standard (DeFi is transparent by design) | — |

---

## 3. Enterprise DA Hybrid Strategy

### 3.1 DA Selection Matrix

| DA Option | Cost | Security Guarantee | Privacy Level | Enterprise Fit | GDPR Compliance | Recommended Use Case |
|---|---|---|---|---|---|---|
| **Ethereum Calldata** | High (~16 gas/byte) | Highest (Ethereum L1) | None (fully public) | Low | ❌ Permanent | — (legacy, replaced by blobs) |
| **EIP-4844 Blobs** | Medium (~0.1x calldata) | Highest | None (public during availability window) | Low | ❌ Public during window | L2 public mainchain non-sensitive data |
| **DAC (permissioned)** | Low | Medium-High (N-of-M honest DAC) | High (off-chain) | High | ✅ Physical deletion possible | Privacy Zone data with multi-party trust |
| **Celestia/EigenDA** | Low | Medium-High (DAS + erasure coding) | Low (public DA sampling) | Medium | ❌ Public | Public DeFi Zone DA (cost optimization) |
| **Self-built DA (Mantle-style)** | Medium (infrastructure) | Medium (operator trust) | Configurable | High | ✅ Operator controls deletion | Custom enterprise requirements |
| **Single-Operator Validium** | Near-zero per tx | Medium (single operator trust) | Highest (operator-only) | Highest | ✅ Physical deletion possible | Prividium-style institutional Zones |
| **Hybrid DA** | Variable | Configurable per tx class | Configurable | Highest | ✅ Per-class compliance | **Recommended default** |

### 3.2 Recommended Hybrid DA Architecture

```
Enterprise L2/L3 Hybrid DA Architecture:

                    Transaction Classification
                           │
              ┌────────────┼────────────┐
              │            │            │
         Public Txs   Privacy Zone  Compliance
         (DeFi,       Txs (RWA,    Audit Data
          governance)  xStocks,     
                       Payment)     
              │            │            │
              ▼            ▼            ▼
     ┌────────────┐ ┌───────────┐ ┌──────────────┐
     │ Ethereum   │ │ Validium  │ │ Encrypted    │
     │ Blobs      │ │ (per-Zone │ │ Archive      │
     │ (EIP-4844) │ │  operator │ │ (threshold   │
     │            │ │  private  │ │  decryption)  │
     │ Highest    │ │  DB)      │ │              │
     │ security   │ │           │ │ MiFID: 7yr   │
     │ Public     │ │ Highest   │ │ SEC: 6yr     │
     │            │ │ privacy   │ │ AML: 5yr     │
     └────────────┘ └───────────┘ └──────────────┘
```

#### Tier 1: Public Transaction DA (Ethereum Blobs)

**Scope**: L2 public mainchain transactions — DeFi, governance, asset registry, cross-Zone settlement summaries.

**Architecture**: Standard OP Stack / ZK Stack blob submission to Ethereum L1 via EIP-4844.

| Parameter | Value |
|---|---|
| DA backend | Ethereum L1 Blobs (EIP-4844) |
| Cost | Standard blob gas market pricing |
| Security | Highest — Ethereum L1 consensus |
| Privacy | None — all data publicly reconstructible |
| Retention | Blob availability window (~18 days) + archival nodes |
| Fault proof compatibility | Full — challengers can reconstruct and verify |

**When to use**: Any transaction that does not contain confidential business data.

#### Tier 2: Privacy Zone DA (Single-Operator Validium)

**Scope**: All transactions within Privacy Zones (RWA, xStocks, Payment).

**Architecture**: Transaction data stored exclusively in Zone operator's private database. L2 receives only `{state_root, zone_batch_proof}`. Ethereum L1 receives the aggregated L2 state root + recursive STARK proof.

```
Zone Internal State (Private)           L2 Settlement (Semi-Public)     L1 Anchor (Public)
┌─────────────────────┐                 ┌──────────────────────┐        ┌──────────────┐
│ Operator's Private  │  submitBatch()  │ ZonePortal Contract  │ STARK  │ Ethereum L1  │
│ PostgreSQL          │ ──────────────► │ (state_root,         │ ─────► │ (aggregated  │
│                     │                 │  batch_proof,        │        │  state_root  │
│ • Full tx data      │                 │  withdrawal_hash)    │        │  + proof)    │
│ • Account states    │                 │                      │        │              │
│ • Contract storage  │                 │ No tx data posted    │        │ No tx data   │
│ • Audit logs        │                 └──────────────────────┘        └──────────────┘
└─────────────────────┘
```

| Parameter | Value |
|---|---|
| DA backend | Operator's private PostgreSQL (Prividium model) |
| Cost | Near-zero per tx (~infrastructure costs only) |
| Security | STARK proof guarantees state transition correctness; DA depends on operator trust |
| Privacy | Highest — data never leaves operator's infrastructure |
| Retention | Configurable per regulatory requirement (5–7 years typical) |
| GDPR | ✅ Physical deletion possible (data is off-chain) |
| Fault proof compatibility | N/A — ZK validity proof replaces fault proof |

**DAC Option (for multi-operator Zones):**

When a Zone is operated by multiple institutions (e.g., an interbank RWA Zone), a DAC replaces the single operator:

| DAC Parameter | Design |
|---|---|
| **Membership** | Certified financial institutions with regulatory licenses |
| **Threshold** | N-of-M signature (e.g., 3-of-5) — data considered "available" when t members confirm |
| **Member selection criteria** | (1) Financial institution license; (2) Geographic diversity; (3) AML compliance certification; (4) SOC 2 Type II attestation |
| **Rotation** | Semi-annual rotation with 1-month overlap; proactive secret sharing for key continuity |
| **Incentives** | Transaction fee share (proportional to DA attestation participation rate) |
| **Penalties** | Data withholding (failure to respond to DA attestation request within 4 hours): (1) Warning; (2) Fee reduction; (3) Temporary suspension; (4) Ejection + bond slashing |
| **Data distribution** | Each DAC member stores encrypted Zone data; threshold decryption required for reads |

#### Tier 3: Compliance Audit Archive (Encrypted Long-Term Storage)

**Scope**: Regulatory audit data — complete transaction records required for multi-year retention.

**Architecture**: Encrypted archive with threshold-decryption access. Stored independently from operational Zone data.

```
Compliance Archive Architecture:

Zone Sequencer → [Audit event stream] → Archive Ingestion Pipeline
                                              │
                                    ┌─────────▼──────────┐
                                    │ Encrypted Archive   │
                                    │                     │
                                    │ Encryption: AES-256 │
                                    │ Key: Split across   │
                                    │   - Zone operator   │
                                    │   - Compliance dept  │
                                    │   - External auditor │
                                    │                     │
                                    │ Threshold: 2-of-3   │
                                    │ for read access      │
                                    └─────────────────────┘
```

| Regulatory Framework | Retention Period | Data Scope |
|---|---|---|
| SEC Rule 17a-4 | 6 years | All securities transactions |
| MiFID II Article 16 | 5 years (txs), 7 years (comms) | Transaction metadata (PII fields encrypted separately) |
| AML 6th Directive | 5 years post-relationship | KYC records, transaction monitoring alerts |
| GDPR Article 17 | "Without undue delay" | PII — resolved via key destruction (logical deletion) |

**GDPR vs. Retention Conflict Resolution:**
- PII fields encrypted with separate key from transaction metadata
- PII key destruction = "logical deletion" under GDPR (data becomes cryptographically unreadable)
- Transaction metadata retained for regulatory period using separate key
- After retention period expires: physical deletion of all data

### 3.3 DA Cost Projections

| Zone Type | DA Backend | Per-Tx DA Cost | Monthly Infra Cost | Annual Total |
|---|---|---|---|---|
| L2 Public (DeFi) | Ethereum Blobs | ~$0.01–0.05 | — (L1 gas only) | $50K–200K (volume-dependent) |
| RWA Zone | Validium | <$0.0001 | $5K–15K (prover + DB) | $60K–180K |
| xStocks Zone | Validium | <$0.0001 | $15K–50K (high TPS prover) | $180K–600K |
| Payment Zone | Validium | <$0.0001 | $5K–20K (prover + DB) | $60K–240K |
| L1 Anchor (all Zones) | Ethereum (proof only) | — | — | $5K–20K/year (proof submission only) |

**Total estimated DA cost**: $355K–$1.24M/year across all Zones and layers — an order of magnitude less than publishing all transaction data to Ethereum L1.

---

## 4. Authenticated RPC Architecture

### 4.1 Design Rationale

L2 RPC is more complex than L1 RPC because of the **multi-layer data topology**: L2 public state, Zone-private state, cross-Zone settlement data, compliance audit data, and Sequencer submission APIs all coexist. A single RPC endpoint cannot serve all consumers with the same data view.

### 4.2 Four-Tier API Architecture

```
                         Users / DApps / Institutions / Regulators
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │    Authenticated API Gateway   │
                        │                               │
                        │  • JWT validation (Okta SSO)  │
                        │  • mTLS (enterprise M2M)      │
                        │  • SIWE (wallet-native auth)  │
                        │  • Rate limiting per identity  │
                        │  • Audit logging (all access)  │
                        └───────────────┬───────────────┘
                                        │
                              Request routing by:
                              - Target (Zone ID / L2 public)
                              - Role (participant / operator / regulator)
                              - Method (read / write / audit)
                                        │
              ┌─────────────┬───────────┼───────────┬──────────────┐
              │             │           │           │              │
              ▼             ▼           ▼           ▼              ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Tier 1   │ │ Tier 2   │ │ Tier 3   │ │ Tier 4   │ │ Tier 5   │
        │ L2 Public│ │ Zone     │ │ Audit    │ │Sequencer │ │ Cross-   │
        │ RPC      │ │ Privacy  │ │ API      │ │ Submit   │ │ Zone     │
        │          │ │ RPC      │ │          │ │ API      │ │ Query    │
        │ Standard │ │ Scoped   │ │ Regulator│ │ Tx       │ │ Bridge   │
        │ eth_*    │ │ per-Zone │ │ access   │ │ submit   │ │ status   │
        └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### 4.3 Tier Specifications

#### Tier 1: L2 Public RPC

Standard Ethereum JSON-RPC serving L2 public mainchain state. No authentication required for read operations.

| Method Category | Authentication | Data Scope |
|---|---|---|
| `eth_blockNumber`, `eth_chainId` | None | Public L2 metadata |
| `eth_getBalance`, `eth_getTransactionReceipt` | None | Public L2 accounts/txs |
| `eth_sendRawTransaction` | Wallet signature (standard) | Submit to L2 public mempool |
| DeFi Zone queries | None | Public DeFi state (TVL, prices) |

#### Tier 2: Zone Privacy RPC (Prividium Proxy RPC Model)

Authenticated access to Zone-internal state. Modeled after Prividium's four-layer access control.

**Authentication Flow:**

```
Step 1: Identity Authentication
  → JWT (Okta OIDC / SIWE / hybrid)
  → Extract: user_id, wallet_address, roles[], zone_permissions[]

Step 2: Wallet Verification
  → Match JWT wallet_address with tx.from
  → Reject if mismatch (prevents identity spoofing)

Step 3: Zone Authorization
  → Check zone_permissions[] includes target zone_id
  → Check role has required permission for requested method

Step 4: Method-Level RBAC
  → Six permission types (Prividium model):
    (1) Forbidden (default for all methods)
    (2) AllUsers (within Zone)
    (3) CheckRole (role-based)
    (4) RestrictArgument (parameter-level filtering)
    (5) CheckRole AND RestrictArgument
    (6) CheckRole OR RestrictArgument
```

**Token Format** (adapted from WHI-359):

```
Token = secp256k1_sig(65B) | version(1B) | zone_id(4B) | chain_id(8B) 
      | issued_at(8B) | expires_at(8B) | role(1B) | permissions_hash(32B)
Magic prefix: "EntL2ZoneRPC"
Default validity: 30 days
zone_id = 0: cross-Zone regulatory supervisor access
```

**Role-Permission Matrix:**

| Role | Own Txs | Others' Txs | Aggregate Data | Submit Txs | Raw Blocks | Audit Log | Cross-Zone |
|---|---|---|---|---|---|---|---|
| Zone Participant | ✅ | ❌ | ✅ (TVL, volume) | ✅ | ❌ | ❌ | Own bridges only |
| Zone Operator | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Zone-to-L2 |
| Regulatory Supervisor | ✅ | ✅ (audit trail) | ✅ | ❌ | ✅ (with audit) | ✅ (immutable) | All Zones (zone_id=0) |
| Compliance Auditor | ✅ (scope) | ✅ (scope, time-bounded) | ✅ | ❌ | ✅ (scope) | ✅ (immutable) | Scoped |
| External Observer | ❌ | ❌ | ✅ (Zone exists + count) | ❌ | ❌ | ❌ | ❌ |

**Multicall Protection**: Following Prividium, multicall (`aggregate()`, `tryAggregate()`) is **actively blocked** at the Proxy RPC layer. This prevents RBAC bypass by bundling forbidden calls inside an allowed multicall container.

**Side-Channel Mitigations** (from WHI-359/WHI-365):
- Minimum RPC response time: ≥100ms (prevents timing analysis)
- Response padding: all responses padded to nearest 1KB (prevents size analysis)
- Fixed gas: 100,000 gas per TIP-20 operation (prevents gas-based inference)
- `transactions[]` array cleared, `logsBloom` zeroed for unauthorized callers

#### Tier 3: Audit API

Regulator-specific access with elevated permissions and immutable audit trails.

| Feature | Design |
|---|---|
| Authentication | mTLS with regulator-issued client certificate + JWT |
| Access scope | Per-Zone or cross-Zone (zone_id=0 for supervisory access) |
| Data format | Structured compliance reports (not raw blockchain data) |
| Escalation levels | (1) ZK compliance report; (2) Aggregate stats + ZK proof; (3) Scoped tx data in sandbox; (4) Full Zone decryption (emergency, supermajority threshold) |
| Audit of audit | All regulator access is logged, timestamped, and hash-chained |
| Time-bounded access | Compliance Auditor access tokens expire; renewal requires re-authorization |

#### Tier 4: Sequencer Submission API

Transaction submission to the Sequencer with compliance checks.

```
Sequencer Submission Flow:

User → Tier 4 API:
  1. JWT authentication (identity verification)
  2. Wallet-address match (sender = authenticated identity)
  3. Zone routing (target Zone identified)
  4. Compliance pre-check:
     - KYB/KYC verification (is sender authorized for this Zone?)
     - Transaction policy check (TIP-403 transferAuthorized())
     - Sanctions screening (real-time OFAC check)
  5. If encrypted mempool (Phase 2):
     - Validate encryption format
     - Route to encrypted ordering pipeline
  6. If plaintext (Phase 1):
     - Route to Sequencer with full compliance check
  7. Return: tx_hash + soft confirmation (preconf)
```

#### Tier 5: Cross-Zone Query API

Bridge status and cross-Zone settlement queries.

| Method | Description | Auth Required |
|---|---|---|
| `bridge_getDepositStatus(zone_id, tx_hash)` | Track deposit from L2 → Zone | Zone Participant |
| `bridge_getWithdrawalStatus(zone_id, tx_hash)` | Track withdrawal from Zone → L2 | Zone Participant |
| `bridge_getCrossZoneStatus(src_zone, dst_zone, tx_hash)` | Track Zone-to-Zone transfer | Participant in both Zones |
| `bridge_getSettlementBatch(zone_id, batch_id)` | Get Zone batch settlement details | Zone Operator / Regulator |

---

## 5. Cross-Zone Interop Design

### 5.1 Challenge: L3-to-L3 Communication

Cross-Zone communication in the L2/L3 model is inherently more complex than in the L1 path:

| Dimension | L1 Path (WHI-359) | L2/L3 Path |
|---|---|---|
| Routing | Zone A → L1 Mainchain → Zone B (single hop) | Zone A (L3) → L2 → Zone B (L3) (double hop) |
| Latency | ~1–2 L1 block times (~600ms × 2 = ~1.2s) | ~2–4 L2 block times (~2–5s × 2 = ~4–10s) |
| Privacy during transit | L1 mainchain sees asset type + amount (mitigated by batching) | L2 sees ZonePortal events (deposit/withdrawal) |
| Atomicity | Non-atomic Phase 1 → Canton 2PC Phase 2 | Non-atomic Phase 1 → Shared Sequencer Phase 2 |

### 5.2 Communication Modes

#### Mode 1: L2 Relay (Phase 1 — Default)

**The safest mode. All cross-Zone communication routes through L2.**

```
Zone A (L3)                    L2 Settlement Layer                Zone B (L3)
┌──────────┐                  ┌──────────────────┐              ┌──────────┐
│ User     │                  │                  │              │          │
│ initiates│  Zone A          │  L2 ZonePortal   │  Zone B      │ Asset    │
│ transfer │  withdrawal      │  contracts       │  deposit     │ received │
│          │ ─────────────►   │ ─────────────►   │ ─────────►   │          │
│          │                  │                  │              │          │
│ Lock     │  submitBatch()   │  processWithdraw │  DepositMade │ Activate │
│ asset    │  {proof, hash}   │  + deposit()     │  event       │ asset    │
│ in Zone  │                  │  to Zone B       │              │ in Zone  │
└──────────┘                  └──────────────────┘              └──────────┘

Latency: Zone A batch time + L2 processing + Zone B block time
         ≈ 5–15 seconds end-to-end (non-atomic)
```

**Privacy characteristics:**
- Zone A internal state: private (Validium)
- L2 settlement layer: sees `{from_zone, to_zone, asset_type, amount}` in ZonePortal events
- Zone B internal state: private (Validium)

**Privacy mitigation for L2 transit visibility:**
- **Batching**: Aggregate multiple cross-Zone transfers into single batch submissions — reduces information leakage per individual transfer
- **Amount splitting**: Split large transfers into multiple smaller batches with randomized timing
- **Encrypted deposit payloads**: Use ECIES to encrypt the deposit recipient address in the L2 ZonePortal call — L2 observers see the deposit event but not the Zone B recipient

**Failure handling:**
- Zone B offline: 24-hour timeout → automatic revert to Zone A
- Compliance rejection at Zone B: assets returned to Zone A within 1 hour
- Partial failure (withdrawal succeeds, deposit fails): L2 ZonePortal holds assets in escrow → manual resolution or automatic retry

#### Mode 2: Shared Sequencer Atomic Bundles (Phase 2)

**If multiple L3 Zones share the same Sequencer (or Shared Sequencer set), the Sequencer can guarantee atomic cross-Zone execution.**

```
Shared Sequencer Atomic Cross-Zone Flow:

User submits atomic bundle: {tx_A (Zone A), tx_B (Zone B)}

Shared Sequencer:
  1. Receives bundle
  2. Orders tx_A and tx_B as an ATOMIC PAIR
  3. Commits ordering for both simultaneously
  4. Zone A executes tx_A → produces state transition A
  5. Zone B executes tx_B → produces state transition B
  6. If either fails: BOTH are reverted (atomicity guarantee)
  7. Settlement: both Zone state roots submitted to L2 in same batch

Latency: Single Sequencer ordering cycle ≈ 1–2 seconds
Atomicity: GUARANTEED (Sequencer enforces all-or-nothing)
```

**Key advantage**: This is the strongest cross-Zone atomicity guarantee available in the L2/L3 model. It is structurally equivalent to Canton's Synchronizer-guaranteed atomicity, but implemented at the Sequencer level.

**Limitation**: Only works for Zones sharing the same Sequencer. Cross-Sequencer atomic transactions require Mode 3.

**Enterprise use case**: RWA DvP (Delivery-versus-Payment) — asset leg in RWA Zone, payment leg in Payment Zone. The Shared Sequencer ensures both legs execute atomically or neither does.

#### Mode 3: ZK Cross-Zone Proofs (Phase 3+)

**Maximum privacy: Zone A proves to Zone B that an asset was locked, without revealing any internal state.**

```
ZK Cross-Zone Proof Flow:

Zone A:
  1. Lock asset in Zone A escrow
  2. Generate ZK proof π_A: "Asset X is locked in Zone A escrow contract
     at address 0x... with hash H_A. Zone A state root is R_A,
     verified by L2 ZonePortal."
  3. Submit π_A to L2 ZonePortal relay

L2 ZonePortal:
  4. Verify π_A against Zone A's committed state root
  5. Relay π_A + verification result to Zone B

Zone B:
  6. Verify π_A (check L2 relay + ZK proof)
  7. Release counterpart asset to recipient in Zone B
  8. Generate π_B: "Counterpart released in Zone B"
  9. (Optional) Submit π_B back to complete round-trip verification
```

**Privacy properties:**
- Zone A internal state: fully private (only the proof about the locked asset is revealed)
- Zone B internal state: fully private
- L2 sees: ZK proofs and verification results only — no asset types, amounts, or addresses
- **Strongest cross-Zone privacy guarantee available**

**Complexity**: Requires recursive STARK/SNARK composition — Zone A proof must be verifiable inside Zone B's proof system. This is feasible with the Airbender prover (supports recursive STARKs) but adds proving overhead (~2–5 seconds per cross-Zone proof).

### 5.3 Cross-Zone Communication Summary

| Mode | Phase | Latency | Atomicity | Privacy | Complexity | Use Case |
|---|---|---|---|---|---|---|
| L2 Relay | 1 | 5–15s | Non-atomic | Medium (L2 sees events) | Low | General cross-Zone transfers |
| Shared Sequencer | 2 | 1–2s | Guaranteed | Medium-High (Sequencer sees bundles) | Medium | DvP (RWA↔Payment) |
| ZK Cross-Zone | 3+ | 10–20s | Verified (ZK) | Highest (ZK proofs only) | High | High-privacy interbank settlement |
| Direct L3-L3 | Deferred | <1s | Best-effort | Low (direct channel) | Medium | Not recommended — bypasses L2 security |

**Design decision: Direct L3-L3 communication (without L2 relay) is explicitly deferred.** It requires additional trust assumptions (direct channel between Zone operators) and bypasses the L2 settlement layer's security guarantees. The Shared Sequencer (Mode 2) achieves comparable latency with stronger guarantees.

---

## 6. Comparison with L1 Path Privacy (WHI-359)

### 6.1 Dimension-by-Dimension Comparison

| Dimension | L1 Path (WHI-359) | L2/L3 Path (This Document) | Assessment |
|---|---|---|---|
| **Zone Autonomy** | Full — Zone is an independent L2 with its own consensus (NoopConsensus + L1 event-driven) | Constrained — Zone is L3, inherits L2 block timing and settlement constraints | **L1 wins.** L1 Zones have complete sovereignty over execution parameters. L2/L3 Zones are bounded by L2 Sequencer timing. |
| **Privacy Depth** | Protocol-native: three-layer defense (admission → DA → cryptographic); precompiles (IdentityRegistry 0x0401, ComplianceCheck 0x0402) are unskippable at EVM level | Layered: Validium DA + L3 isolation + Proxy RPC + encrypted deposits; but compliance is contract-layer (bypassable via L1 forced inclusion) | **L1 wins.** L1 path has precompile-level compliance enforcement. L2/L3 relies on contract-layer controls that can technically be bypassed by L1 forced inclusion. |
| **Sequencer Privacy** | No Sequencer — BFT validators see what they execute (consistent and expected) | **Core challenge** — Sequencer sees all plaintext. Mitigated via Phase 1 (legal), Phase 2 (encrypted mempool), Phase 3 (TEE) | **L1 wins.** The Sequencer privacy problem is structural to L2 and cannot be fully eliminated — only mitigated. |
| **DA Flexibility** | Fully self-sovereign — Zone operator controls DA backend entirely | Bound to L2 DA strategy — Validium provides privacy, but L2 settlement still posts state roots to L1 | **L1 wins.** L1 Zones have zero mandatory public data. L2/L3 Zones must post settlement data to L2 (which posts to L1). |
| **Cross-Zone Latency** | Low — Zone A → L1 Mainchain → Zone B (~1.2s with Simplex BFT 600ms finality) | High — Zone A (L3) → L2 → Zone B (L3) (~4–10s non-atomic; ~1–2s with Shared Sequencer) | **L1 wins.** One fewer layer = lower latency. Shared Sequencer closes the gap but adds trust. |
| **Cost** | Self-determined — Zone operator sets gas pricing; no L1 gas dependency for operation | L2 gas + Validium prover cost + L1 proof anchoring cost. More predictable but less controllable | **L2/L3 wins.** Despite L1's self-determination, L2/L3 has lower absolute costs due to Ethereum security amortization. Validium per-tx cost (<$0.0001) is lower than L1 BFT node operation. |
| **Security Guarantee** | Zone operator + BFT validators + L1 anchor (optional) | Zone operator + Sequencer + L2 + Ethereum L1 (mandatory). STARK proof soundness ≥ 2⁻⁸⁰ | **L2/L3 wins.** Ethereum L1 settlement provides math-guaranteed state transition correctness — the "neutral referee" that competing banks require. L1 path's ZK proofs are Phase 3. |
| **GDPR Compliance** | Direct control — Zone operator handles all data; physical deletion trivial | Requires DAC/operator cooperation for Validium data; L2 settlement events are permanent | **L1 wins slightly.** Both use Validium (off-chain deletion possible), but L2/L3 has permanent settlement events on L2/L1 that may contain metadata. |
| **Settlement Neutrality** | Zone operator is the settlement authority — potential trust issue for competing institutions | Ethereum L1 is the ultimate settlement authority — STARK proof is math, not trust | **L2/L3 wins decisively.** This is the primary value proposition of L2/L3: "math-neutral settlement" via STARK proofs verifiable on Ethereum. |
| **Regulatory Credibility** | Self-operated chain — regulators may question independence of settlement | Ethereum-anchored — regulators recognize Ethereum L1 as a neutral public infrastructure | **L2/L3 wins.** "Settled on Ethereum" is a meaningful compliance narrative that simplifies regulatory conversations. |
| **Development Ecosystem** | Custom chain — requires custom tooling, limited developer pool | Full Ethereum ecosystem — Solidity, Hardhat, Foundry, OpenZeppelin, MetaMask | **L2/L3 wins.** Orders of magnitude larger developer and tooling ecosystem. |
| **Time to Market** | 18–24 months (custom BFT + Zone architecture from scratch) | 12–18 months (fork ZK Stack / OP Stack + L3 framework) | **L2/L3 wins.** Existing frameworks (Prividium, Arbitrum Orbit) provide a 6–12 month head start. |
| **Finality** | ~600ms (Simplex BFT) — deterministic, instant | Soft: ~1–2s (Sequencer preconf); Hard: minutes–hours (STARK proof + L1 finality) | **L1 wins for hard finality.** L1 BFT finality is deterministic and instant. L2/L3 has fast soft finality but slow hard finality. |

### 6.2 Honest Assessment of L2/L3 Limitations

1. **Sequencer Privacy is an inherent structural weakness.** No amount of engineering fully eliminates the information asymmetry of a centralized ordering entity. The L1 path simply does not have this problem.

2. **L1 forced inclusion breaks Zone access control.** The `TransactionFilterer` (Prividium's solution) is a whitelist-based patch that weakens the L2 escape hatch. In the L1 path, there is no external L1 that can force transactions into a Zone.

3. **Multi-layer latency is irreducible.** L3→L2→L1 always adds settlement delay compared to L2→L1. Shared Sequencing reduces ordering latency but not settlement latency.

4. **Privacy metadata leakage at L2 settlement layer.** Even with Validium (no tx data on-chain), ZonePortal events (deposits, withdrawals, batch submissions) create a metadata trail on L2. An observer can infer Zone activity levels, cross-Zone transfer patterns, and timing correlations.

5. **Fault proof incompatibility with privacy.** If the L2 base layer is an Optimistic Rollup, all L2 data must be public for challengers. This means Zone settlement events on L2 cannot be encrypted. **Critical constraint**: either the L2 uses ZK validity proofs (no fault proofs needed), or Zone settlement metadata is public on L2.

### 6.3 Where L2/L3 Path Decisively Wins

1. **Settlement Neutrality.** For multi-institution deployments where competing banks must share a settlement layer, Ethereum L1 STARK verification is the "math-neutral referee" that eliminates trust assumptions. This is the strongest argument for L2/L3 — and the reason Prividium (35+ financial institutions) chose this architecture.

2. **Regulatory Credibility.** "Settled on Ethereum" is a meaningful narrative for regulators who are skeptical of private chain operators' claims.

3. **Ecosystem and Time to Market.** Full Ethereum toolchain compatibility + existing L3 frameworks = dramatically faster deployment.

4. **Cost at Scale.** Ethereum security amortization makes per-tx costs lower than operating an independent BFT chain at equivalent security levels.

---

## 7. Per-Narrative Privacy Mapping

### 7.1 RWA Tokenization

| Design Element | Decision | Rationale |
|---|---|---|
| Zone Type | Dedicated L3 (RWA Zone) | Regulatory isolation + sub-tx privacy |
| Privacy Model | Canton-inspired Merkle DAG projection | DvP parties see only their own subtree; production-validated ($2T+/month) |
| DA | Single-operator Validium | Off-chain data; GDPR deletion; lowest cost |
| Sequencer Privacy | Phase 1: NDA + Chinese walls; Phase 2: encrypted mempool | Banks will not participate if Sequencer operator (potential competitor) sees positions |
| Cross-Zone | Shared Sequencer atomic bundles (Phase 2) | DvP requires atomicity: asset leg (RWA Zone) ↔ payment leg (Payment Zone) |
| Compliance | SEC Reg D/S/A+, MiCA, MAS; 5–7yr archive; TIP-403 transferAuthorized() | Precompile-level enforcement preferred; identity precompile mandatory |
| Finality | Soft: 2–5s (adequate for T+1/T+0 settlement); Hard: minutes (ZK proof) | RWA settlement is not sub-second; 2–5s soft finality is acceptable |

### 7.2 xStocks / Tokenized Equities

| Design Element | Decision | Rationale |
|---|---|---|
| Zone Type | Dedicated L3 (xStocks Zone) with isolated dark pool sub-Zone | Dark pool requires extreme privacy; general trading requires market surveillance |
| Privacy Model | ZK order matching + dark pool physical isolation | Order flow privacy is legally mandatory (SEC); front-running = criminal offense |
| DA | Single-operator Validium | Full audit trail for regulators; public market data (price, volume) published selectively |
| Sequencer Privacy | Phase 2: encrypted mempool (**mandatory**); Phase 3: TEE recommended for dark pool | Sequencer seeing dark pool order flow = structural equivalent of insider trading |
| Cross-Zone | L2 relay (Phase 1) for settlement; Shared Sequencer (Phase 2) for DvP with RWA Zone | Post-trade settlement is non-realtime; atomicity important for DvP |
| Compliance | SEC Reg NMS, Reg ATS, Reg SHO; market surveillance mandatory; SAR/STR reporting | Real-time anomaly detection in Sequencer compliance pipeline |
| Finality | **CRITICAL**: WHI-355/WHI-364 both flag that <1s finality is required for HFT. **L2/L3 cannot achieve this** — structural limitation. Soft preconf (~1–2s) is the best available. | xStocks HFT may require L1 BFT path. L2/L3 adequate for non-HFT equities (T+1 settlement). |

### 7.3 Payment / Stablecoin

| Design Element | Decision | Rationale |
|---|---|---|
| Zone Type | Dedicated L3 (Payment Zone) | Travel Rule isolation; B2C scalability |
| Privacy Model | ECIES encrypted deposits + sanitized block data | Competitors must not see payment flows/scale; Travel Rule metadata captured internally |
| DA | Volition (public summary + private details) | Aggregate volume publishable; individual tx details private |
| Sequencer Privacy | Phase 1: Sequencer-as-Compliance-Officer (adequate) | Travel Rule already requires Sequencer to process sender/receiver info for $3K+ transfers |
| Cross-Zone | L2 relay (Phase 1); Shared Sequencer (Phase 2) for atomic DvP | Payment Zone is a counterpart to RWA/xStocks Zones in DvP flows |
| Compliance | Travel Rule, AML/CFT, sanctions screening | Real-time AML monitoring; metadata available to compliance but not public |
| Finality | Soft: 1–2s (Sequencer preconf — adequate for B2B/B2C payments) | Sub-second for POS payments requires L1 BFT path |

### 7.4 DeFi Infrastructure

| Design Element | Decision | Rationale |
|---|---|---|
| Zone Type | L2 Public Mainchain (no Zone isolation needed) | DeFi requires global state visibility for composability (TVL, prices) |
| Privacy Model | Transparent (standard L2) | Privacy not a core DeFi requirement; composability > privacy |
| DA | Ethereum Blobs (EIP-4844) | Maximum security; public data acceptable |
| Sequencer Privacy | Phase 1: FCFS ordering (standard MEV protection) | Standard DeFi MEV mitigation; no enterprise-specific requirements |
| Cross-Zone | DeFi on L2 mainchain can interact with Zone assets via ZonePortal bridge | Wrapped Zone assets tradeable on L2 DeFi; original assets locked in ZonePortal |
| Compliance | Minimal — standard DeFi AML tooling | Transaction monitoring at RPC level (standard) |
| Finality | Soft: 1–2s (preconf); Hard: L1 finality | DeFi users accustomed to L2 finality timelines |

---

## 8. Implementation Roadmap

### Phase 1: Foundation (Months 0–12)

| Milestone | Deliverable | Dependencies |
|---|---|---|
| **M1: L2 + Single Zone** | Enterprise L2 (ZK Stack or OP Stack fork) + 1 pilot Zone (Payment Zone) | WHI-365 Sequencer design |
| **M2: Validium DA** | Single-operator Validium DA backend for pilot Zone | Airbender GPU prover deployment |
| **M3: Authenticated RPC** | Four-tier API Gateway + Zone Privacy RPC + Audit API | Prividium Proxy RPC reference implementation |
| **M4: Sequencer Compliance** | Sequencer-as-Compliance-Officer: FCFS + AML/OFAC + audit logging + NDA framework | Phase 1 Sequencer from WHI-365 |
| **M5: Cross-Zone Bridge** | L2 relay bridge (non-atomic): Zone A → L2 → Zone B | ZonePortal contracts |

### Phase 2: Enterprise Scale (Months 12–24)

| Milestone | Deliverable | Dependencies |
|---|---|---|
| **M6: Multi-Zone** | RWA Zone + xStocks Zone + Payment Zone (all L3s on L2) | Phase 1 complete |
| **M7: Encrypted Mempool** | Threshold encryption for Sequencer-blind ordering | Permissioned Shared Sequencing (WHI-365 Phase 2) |
| **M8: Shared Sequencer** | Multi-institution Sequencer set; atomic cross-Zone bundles | BFT ordering consensus between institutions |
| **M9: DAC** | DAC for multi-operator Zones; threshold signatures; rotation mechanism | M6 multi-Zone operational |
| **M10: ZK Compliance** | ZK sanctions screening; ZK audit reports; regulatory sandbox API | M6 + compliance framework operational |

### Phase 3: Advanced Privacy (Month 24+)

| Milestone | Deliverable | Dependencies |
|---|---|---|
| **M11: TEE Sequencer** | SGX/Nitro enclave for xStocks dark pool Sequencer | Phase 2 encrypted mempool operational |
| **M12: ZK Cross-Zone Proofs** | Recursive STARK proofs for cross-Zone settlement (maximum privacy) | Airbender recursive proving capability |
| **M13: In-Protocol Privacy** | (Exploratory) Aztec-style protocol-native encryption within individual Zones | Dependent on ecosystem maturity |
| **M14: Canton-Style 2PC** | Full Canton-like sub-transaction privacy via global Synchronizer | Phase 2 Shared Sequencer operational |

---

## 9. Risk Analysis and Mitigations

### 9.1 Critical Risks

| Risk | Severity | Probability | Mitigation |
|---|---|---|---|
| **Sequencer data breach** | Critical | Medium | Phase 2 encrypted mempool; Phase 3 TEE; NDAs + Chinese walls (Phase 1); audit logging; incident response plan |
| **L1 forced inclusion bypass** | High | Low-Medium | TransactionFilterer whitelist; L2 Sequencer compliance filter; economic penalties; legal agreements; **accept that escape hatch is weakened** |
| **DAC data withholding** | High | Low | N-of-M threshold (survive minority failures); financial penalties; automatic suspension; bond slashing; rotation |
| **ZK prover failure** | Medium | Low | Prover cluster redundancy; fallback to Optimistic mode (temporary, with degraded privacy); multiple GPU vendors |
| **Cross-Zone privacy leakage via L2 metadata** | Medium | Medium | Batching; amount splitting; encrypted deposit payloads; Phase 3 ZK cross-Zone proofs |
| **Regulatory rejection of L2/L3 model** | Medium | Low-Medium | Ethereum settlement narrative; early regulatory engagement; comparison with Prividium's 35+ institution validation |
| **xStocks HFT latency inadequacy** | High | High | **Acknowledged limitation**: L2/L3 cannot achieve <1s hard finality. HFT use case may require L1 BFT path. Soft preconf (~1–2s) is a partial mitigation. |
| **Framework vendor lock-in** | Medium | Medium | Abstract Zone interface; standard EVM compatibility; portable Solidity contracts; DA backend abstraction layer |

### 9.2 Dependency Risks

| Dependency | Risk | Mitigation |
|---|---|---|
| Airbender GPU prover | Performance claims unverified in our specific workload | Benchmark during M2; fallback to alternative provers (SP1, RISC Zero) |
| ZK Stack / OP Stack L3 framework | Framework immaturity for production L3 deployment | Start with most mature framework; contribute upstream fixes; maintain internal fork |
| Threshold cryptography libraries | Limited production-ready implementations for BLS threshold encryption | Use audited libraries (e.g., threshold-bls, drand); independent security audit before deployment |
| Institutional willingness to run Shared Sequencer nodes | Business/operational coordination challenge | Start with single operator (Phase 1); demonstrate value before requesting multi-institution participation |

---

## Appendix A: Glossary

| Term | Definition |
|---|---|
| **Validium** | L2 variant where transaction data is stored off-chain (not on Ethereum L1). Only state roots and validity proofs are posted on-chain. |
| **DAC** | Data Availability Committee — a permissioned set of entities that attest to the availability of off-chain data. |
| **FCFS** | First-Come-First-Served — transaction ordering policy where transactions are sequenced by arrival time. |
| **ZonePortal** | Smart contract on L2 that manages Zone deposits, withdrawals, and batch settlement. |
| **Airbender** | ZKsync's GPU-accelerated RISC-V STARK prover. Produces block proofs in <1 second at production scale. |
| **TIP-403** | Tempo protocol standard for `transferAuthorized()` — a precompile-level compliance check invoked automatically on every token transfer. |
| **Preconf** | Pre-confirmation — Sequencer's soft commitment to transaction inclusion before formal block finalization. |
| **TEE** | Trusted Execution Environment — hardware-enforced isolated computation (Intel SGX, ARM TrustZone, AWS Nitro). |
| **Canton 2PC** | Canton's Two-Phase Commit protocol for atomic multi-party transactions via a global Synchronizer. |
| **Volition** | A hybrid DA mode where the user chooses per-transaction whether data goes on-chain (Rollup mode) or off-chain (Validium mode). |

---

## Appendix B: References

| Source | Relevance |
|---|---|
| WHI-355: Narrative Analysis | Per-narrative privacy requirements and regulatory frameworks |
| WHI-359: L1 Path Privacy Design | L1 counterpart for comparison; Zone architecture reference |
| WHI-364: Fork Analysis | L1 vs L2/L3 tradeoff analysis; Validium recommendation |
| WHI-365: L2/L3 Execution + Sequencer | Sequencer architecture; L3 Zone design; DA integration |
| WHI-338: Prividium Architecture | Validium + Proxy RPC production reference |
| WHI-341: Mantle DA Baseline | Mantle DA cost model; Alt-DA framework |
| WHI-343: Privacy Comparison | Three privacy paradigms; eight-dimension comparison |
| WHI-345: DA Comparison | DA cost/security/privacy tradeoff matrix |
