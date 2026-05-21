# WHI-359: Privacy Layer & Data Sovereignty Architecture Design

> **L1 Path — Privacy Layer and Data Sovereignty Architecture for an Ideal Enterprise Blockchain**

| Meta | Value |
|------|-------|
| Issue | WHI-359 |
| Dependencies | WHI-355 (Narrative Analysis), WHI-357 (Architecture Blueprint) |
| References | WHI-340 (Tempo), WHI-335 (Canton), WHI-338 (Prividium), WHI-343 (Privacy Comparison), WHI-345 (DA Comparison) |
| Status | In Review |
| Date | 2026-05-07 |

---

## Table of Contents

1. [Design Philosophy & Core Contradictions](#1-design-philosophy--core-contradictions)
2. [Multi-Zone Privacy Architecture](#2-multi-zone-privacy-architecture)
3. [Privacy Technology Approach](#3-privacy-technology-approach)
4. [Data Sovereignty Architecture](#4-data-sovereignty-architecture)
5. [Cross-Zone Interoperability](#5-cross-zone-interoperability)
6. [Comparison with Existing Solutions](#6-comparison-with-existing-solutions)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Appendix: Threat Model & Attack Surfaces](#8-appendix-threat-model--attack-surfaces)

---

## 1. Design Philosophy & Core Contradictions

### 1.1 The Enterprise Privacy Paradox

> **Privacy is not "encrypt everything" — it is "precisely control who can see what."**

Enterprise blockchain privacy must simultaneously satisfy three contradictory stakeholder demands:

| Stakeholder | Demand | Implication |
|-------------|--------|-------------|
| **Participants** | Counterparty invisibility: competitors must not see holdings, strategies, or order flow | Data must be hidden from all non-involved parties |
| **Regulators** | Full audit access: SEC/MAS/BaFin require complete transaction lifecycle traceability | Data must be accessible to authorized regulators on demand |
| **Auditors** | Compliance verification without exposure: verify rules are followed without seeing individual amounts | Proofs of correctness must be constructible without revealing underlying data |

This is not a binary choice between "private" and "transparent." Each narrative demands a different point on the privacy spectrum, and even within a single transaction, different fields require different visibility levels.

### 1.2 Design Principles

**Principle 1 — Selective Transparency over Binary Privacy**
Every data element has a visibility policy. Transaction amount, counterparty identity, asset type, and compliance metadata each have independent access control rules.

**Principle 2 — Reverse Privacy-Complexity Law (from WHI-349 Pattern P2)**
Fine-grained information routing control achieves finer privacy with simpler cryptography. ZK proofs are used only at trust boundary crossings (Zone ↔ mainchain, Zone ↔ regulator), not for internal data routing. This architectural insight — first crystallized in the WHI-343 comparison — is that Canton achieves the finest-grained privacy (sub-transaction) with the simplest cryptography (encrypted routing + Merkle hashes), while Prividium achieves coarser-grained privacy with the most complex cryptography (STARK + GPU farms).

**Principle 3 — Sequencer-as-Compliance-Officer**
In enterprise contexts, the privacy adversary is external observers and competitors — not the operator. The Zone Sequencer's full visibility over Zone state is reframed from "privacy defect" to "compliance asset." The Sequencer is the natural compliance infrastructure: it sees the plaintext needed for AML/sanctions checks, while external parties see only encrypted/filtered data. This pattern, identified in WHI-357, is novel — no existing project has systematized it.

**Principle 4 — Phased Trust Model Migration**
Start with admission control (Layer 1) and DA-level privacy (Layer 2), which require no cryptographic overhead. Add cryptographic privacy (Layer 3: ZK/FHE/MPC) as the technology matures. Each phase independently provides meaningful privacy guarantees.

### 1.3 Per-Narrative Privacy Requirements (from WHI-355)

| Narrative | Privacy Rating | What Must Be Hidden | What Must Be Visible | Key Regulatory Regime |
|-----------|---------------|---------------------|---------------------|----------------------|
| **RWA Tokenization** | 5/5 (Critical) | Counterparty identity, holding size, asset valuation, subscription scale in primary issuance; in DvP: each party sees only their leg | Full lifecycle audit trail, per-counterparty compliance status (KYC/KYB, accredited investor), periodic regulatory reporting | US Reg D/S/A+, EU MiCA, SG MAS |
| **xstocks** | 5/5 (Critical) | Dark pool: counterparty + price + quantity all private; block trade protection; order flow and market-making strategies; large holder positions | Real-time market surveillance (insider trading/manipulation), SAR/STR, complete order-to-settlement audit trail | Reg NMS, Reg SHO, Reg ATS |
| **Payment** | 4/5 (High) | B2B: payment flows and amounts from competitors; B2C: counterparty data from non-participants | Travel Rule data (≥$3,000: sender/receiver institution info), AML/CFT screening results | Travel Rule (FATF R.16), AML Directives |
| **DeFi / Public** | 2/5 (Low) | Nothing — full transparency required for permissionless composability | TVL, prices, contract state, global supply | Minimal (emerging MiCA DeFi rules) |

**Critical insight from WHI-355:** The privacy spectrum is not continuous — it clusters into four distinct tiers:

| Tier | Privacy Approach | Narratives |
|------|-----------------|------------|
| **T0: Public** | No privacy, full transparency | DeFi |
| **T1: DA-Level** | Zone isolation, ECIES-encrypted deposits, sanitized blocks | Payment |
| **T2: Access-Controlled** | Authenticated RPC + sequencer policy + RBAC | Supply chain, Payment B2B |
| **T3: Sub-Transaction** | Each party sees only their relevant subtree (Canton model) or ZK proofs within Zone | RWA DvP, xstocks dark pool |

---

## 2. Multi-Zone Privacy Architecture

### 2.1 Zone Types Mapped to Narratives

A Zone is a **physically isolated execution environment**: independent state, independent Sequencer, independent DA backend, independent RPC endpoint. Zones run `NoopConsensus` with no P2P network — block production is entirely L1-event-driven (one mainchain block triggers exactly one Zone block), and `head = safe = finalized` always holds within a Zone (inherited from the mainchain's Simplex BFT finality at ~600ms).

| Zone Type | Target Narrative | Privacy Tier | Internal Privacy Model | DA Strategy | TPS Target |
|-----------|-----------------|-------------|----------------------|-------------|-----------|
| **Public Mainchain** | DeFi, public asset registry | T0: Public | Fully transparent | Public (L1 blob) | 3,000-5,000 |
| **Institutional RWA Zone** | RWA tokenization | T3: Sub-Transaction | **Option B: Sub-tx privacy** (Canton-inspired Merkle DAG projection) | Single-operator Validium | 100-500 |
| **xstocks Trading Zone** | xstocks securities | T3: Sub-Transaction | **Option C: ZK-enhanced** (order privacy + block trade protection) | Single-operator Validium | 1,000-3,000 |
| **Payment Zone** | Stablecoin payment | T1: DA-Level | **Option A: Zone-internal transparent** (all Zone participants see all txs) | Single-operator Validium | >10,000 |
| **Custom Zone** | Enterprise-specific | T1-T3 (configurable) | Configurable per deployment | Configurable | Configurable |

#### Rationale for Internal Privacy Model Selection

**RWA Zone → Option B (Sub-Transaction Privacy):**
WHI-355 identifies a critical requirement: in a DvP transaction, each party must see only their relevant leg. When Alice trades an RWA token for Bob's IOU, Alice should see the IOU transfer and asset creation, Bob should see the IOU creation and asset delivery, the Bank sees only IOU movement, and the Registrar sees only share movement. This is precisely Canton's Merkle DAG projection model. No other model achieves this granularity.

Implementation approach: Adapt Canton's projection algorithm for the EVM context. Instead of Daml's native sub-transaction decomposition, use a **Transaction Envelope** structure:

```
TransactionEnvelope {
  globalTxHash: bytes32,                    // Links all sub-transactions
  subTransactions: [
    {
      participants: [address],              // Who can see this sub-tx
      encryptedPayload: bytes,              // ECIES-encrypted per participant
      commitmentHash: bytes32,              // SHA256(plaintext) for integrity
      validityProof: bytes                  // ZK proof of correct execution
    }
  ],
  merkleRoot: bytes32                       // Root of sub-transaction Merkle tree
}
```

Each participant receives only the sub-transactions where their address appears in the `participants` list. The remaining sub-transactions are replaced with their `commitmentHash` values, allowing Merkle proof verification without content disclosure.

**xstocks Zone → Option C (ZK-Enhanced):**
Securities trading has a unique privacy profile: pre-trade information (orders, strategies) is extremely sensitive, while post-trade information (execution price, volume) has phased disclosure requirements (immediate to regulators, delayed to public). The Zone-internal transparent model leaks too much — even within the Zone, a market maker should not see other market makers' strategies.

Implementation approach: A **ZK Order Matching Engine** where:
- Orders are submitted as commitments: `Commit(price, quantity, side, nonce)`
- Matching is performed by the Sequencer (who sees plaintext — Sequencer-as-Compliance-Officer)
- Post-match, the Sequencer publishes ZK proofs that:
  - The match respected price-time priority (Reg NMS compliance)
  - No self-dealing occurred (wash trade prevention)
  - Aggregate volume disclosure is correct (post-trade transparency)
- Individual order details remain private from other participants

**Payment Zone → Option A (Zone-Internal Transparent):**
WHI-355 notes that in payment networks, participating banks/VASPs typically already know each other within the payment network. The primary privacy requirement is against *external* observers (competitors, public), not between Zone participants. Travel Rule compliance (≥$3,000) already requires sharing sender/receiver institution information between counterparties. Zone-internal transparency dramatically simplifies the implementation and maximizes TPS for the >10,000 TPS target.

### 2.2 Zone Lifecycle Management

#### 2.2.1 Zone Creation

Zone creation is governed by the mainchain `ZoneFactory` contract:

```solidity
interface IZoneFactory {
    /// @notice Create a new Zone
    /// @param config Zone configuration parameters
    /// @return zoneId The unique identifier for the new Zone
    function createZone(ZoneConfig calldata config) external returns (uint256 zoneId);
    
    struct ZoneConfig {
        // Identity & governance
        address zoneOperator;           // Initial Zone operator
        address[] initialParticipants;  // Initial whitelist (for permissioned Zones)
        
        // Privacy configuration
        PrivacyTier privacyTier;        // T0, T1, T2, or T3
        InternalPrivacyModel internalModel; // A (transparent), B (sub-tx), C (ZK)
        
        // Encryption
        bytes eciesPublicKey;           // Zone encryption public key
        bool thresholdECIES;            // Use threshold ECIES (multi-key)
        
        // Compliance
        uint256 tip403PolicyId;         // TIP-403 compliance policy reference
        bool travelRuleEnabled;         // Travel Rule engine activation
        
        // DA configuration
        DAStrategy daStrategy;          // Validium (default) / Alt-DA / Public
        uint256 dataRetentionDays;      // Configurable retention (GDPR vs SEC)
        
        // Performance
        uint256 maxTPS;                 // Target throughput
        uint256 gasModel;               // Fee structure (subsidized, market, fixed)
    }
}
```

**Creation governance:** In Phase 1, Zone creation requires mainchain governance approval (multisig or governance vote). In Phase 2, permissionless Zone creation with a staking requirement is introduced for Custom Zones.

#### 2.2.2 Zone Configuration Updates

```solidity
interface IZoneRegistry {
    /// @notice Update Zone configuration (operator or governance only)
    function configureZone(uint256 zoneId, ZoneConfigUpdate calldata update) external;
    
    /// @notice Rotate Zone encryption key (threshold ceremony required)
    function rotateEncryptionKey(uint256 zoneId, bytes calldata newPublicKey, 
                                  bytes calldata rotationProof) external;
    
    /// @notice Add/remove participant from Zone whitelist
    function updateParticipant(uint256 zoneId, address participant, bool allowed) external;
}
```

Key rotation uses a threshold ceremony: `t-of-n` key holders must sign the rotation, and the old key remains valid for a grace period (configurable, default 7 days) to allow in-flight transactions to complete.

#### 2.2.3 Zone Upgrade

Zone upgrades follow a **staged rollout** protocol:
1. **Proposal:** Zone operator or governance submits upgrade proposal (new Sequencer binary hash, configuration changes)
2. **Freeze window:** Zone enters read-only mode for `freezePeriod` (default: 1 hour)
3. **State migration:** Sequencer exports current state, new Sequencer imports and validates state root matches
4. **Activation:** New configuration takes effect at next mainchain block boundary
5. **Rollback window:** For `rollbackPeriod` (default: 24 hours), governance can revert to previous configuration

#### 2.2.4 Zone Exit / Closure

Zone closure follows a deterministic wind-down process:

```
Phase 1 — Announcement (configurable, minimum 7 days)
  - ZoneRegistry emits ZoneClosureAnnounced(zoneId, closureBlock)
  - New deposits blocked; existing transactions continue
  
Phase 2 — Settlement (up to 30 days)
  - All open positions must be closed or transferred
  - Cross-Zone transfers processed
  - Outstanding withdrawals processed
  
Phase 3 — Final State
  - Zone Sequencer publishes final state root + validity proof
  - All remaining assets force-withdrawn to mainchain
  - Zone encryption keys escrowed (for regulatory audit period)
  
Phase 4 — Data Handling
  - If dataRetentionDays > 0: encrypted archive created, keys held by escrow
  - If dataRetentionDays = 0 AND no regulatory hold: key destruction = logical deletion
  - Zone DA storage marked for cleanup
```

#### 2.2.5 Zone Governance Boundaries

| Decision | Zone Operator Authority | Mainchain Governance Authority |
|----------|----------------------|------------------------------|
| Participant whitelist changes | ✅ Full control | ❌ No override |
| Privacy tier modification | ❌ Cannot downgrade | ✅ Can enforce minimum |
| Compliance policy updates | ✅ Can add stricter rules | ✅ Can set baseline via TIP-403 |
| Zone closure | ✅ Can initiate | ✅ Can force-close (emergency) |
| Fee model changes | ✅ Within bounds | ✅ Sets bounds |
| Sequencer replacement | ✅ Nominates | ✅ Must approve |
| Encryption key rotation | ✅ Initiates ceremony | ❌ No involvement |

### 2.3 Zone ↔ Mainchain Architecture

```
┌──────────────────────────────── Ethereum L1 ────────────────────────────────┐
│                                                                              │
│  Periodic ZK Proof Anchoring: batch state commitments per N epochs           │
│  (STARK, SP1/RISC-V prover, soundness ≥ 2^{-80})                           │
│                                                                              │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┴──────────────────────────────────────────┐
│                     PUBLIC MAINCHAIN (Simplex BFT, ~600ms finality)           │
│                                                                              │
│  ┌─────────────┐  ┌───────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Asset        │  │ Zone          │  │ Identity     │  │ Governance     │  │
│  │ Registry     │  │ Factory &     │  │ Registry     │  │ Contracts      │  │
│  │ (global      │  │ Registry      │  │ (KYC/KYB     │  │ (global rules, │  │
│  │  supply,     │  │ (creation,    │  │  attestation │  │  policy        │  │
│  │  DeFi pools) │  │  config,      │  │  anchors)    │  │  updates)      │  │
│  │              │  │  lifecycle)   │  │              │  │                │  │
│  └─────────────┘  └───────────────┘  └──────────────┘  └────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ PolicyRegistry (TIP-403) — auto-synced to all Zones per-block       │   │
│  │ Cross-Zone Settlement Layer — asset transit hub                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐                │
│  │ZonePortal│   │ZonePortal│   │ZonePortal│   │ZonePortal│                │
│  │   (RWA)  │   │ (xstocks)│   │ (Payment)│   │ (Custom) │                │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘                │
│       │              │              │              │                        │
└───────┼──────────────┼──────────────┼──────────────┼────────────────────────┘
        │              │              │              │
  ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐
  │ RWA Zone  │  │ xstocks   │  │ Payment   │  │ Custom    │
  │           │  │ Zone      │  │ Zone      │  │ Zone      │
  │ Tier: T3  │  │ Tier: T3  │  │ Tier: T1  │  │ Tier: T1-T3│
  │ Model: B  │  │ Model: C  │  │ Model: A  │  │ Model: cfg│
  │ Sub-tx    │  │ ZK-order  │  │ Transparent│  │           │
  │ privacy   │  │ matching  │  │ >10K TPS  │  │           │
  │ 100-500   │  │ 1K-3K TPS│  │           │  │           │
  │ TPS       │  │           │  │           │  │           │
  └───────────┘  └───────────┘  └───────────┘  └───────────┘
```

**Key architectural relationships:**

1. **Policy Sync (L1 → Zone):** The mainchain `PolicyRegistry` (TIP-403 compatible) auto-mirrors to all Zones in the next block via `TempoStateReader` precompile. Zone `ZoneTip403ProxyRegistry` maintains a read-only proxy with per-block GC (`SharedPolicyCache.advance(l1_block_number)`). This is bidirectional — an improvement over Tempo's one-way sync: Zone execution results can report back to mainchain.

2. **Asset Transit:** Mainchain is the cross-Zone asset transit hub. Zone A → mainchain → Zone B (two-step bridge). Assets are locked in `ZonePortal` contracts on the mainchain during deposit.

3. **State Anchoring:** Each Zone periodically submits batch state transitions to its `ZonePortal`: `submitBatch(blockTransition, depositQueueTransition, withdrawalQueueHash, proof)`. The `proof` parameter is pre-slotted for ZK validity proofs (currently empty in Phase 1; SP1/RISC-V proof in Phase 3).

4. **Finality Inheritance:** Zone finality is inherited from the mainchain's Simplex BFT (~600ms). Since Zone block production is 1:1 mapped to mainchain blocks with `NoopConsensus`, Zone finality = mainchain finality.

---

## 3. Privacy Technology Approach

### 3.1 Three-Layer Privacy Model

The privacy architecture follows a defense-in-depth strategy with three independent layers, each providing meaningful privacy guarantees even without the layers above:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  LAYER 3: CRYPTOGRAPHIC PRIVACY                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ • ZK compliance proofs (PII-free sanctions screening)       │   │
│  │ • Selective disclosure (Viewing Key tiered authorization)    │   │
│  │ • Future: FHE/MPC encrypted execution                       │   │
│  │ Effect: Even the operator cannot access specific data       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  LAYER 2: DA-LAYER PRIVACY                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ • Zone transaction data NOT published to mainchain          │   │
│  │ • ECIES-encrypted deposits/withdrawals                      │   │
│  │ • Operator private database backend (Validium model)        │   │
│  │ Effect: External observers cannot obtain Zone tx data       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  LAYER 1: ADMISSION CONTROL PRIVACY                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ • Authenticated RPC (signed access tokens, per-account      │   │
│  │   data filtering, 100ms minimum response time)              │   │
│  │ • Sequencer policy engine (whitelist/blacklist/compound)     │   │
│  │ • Five-layer defense-in-depth access control                │   │
│  │ Effect: Unauthorized users cannot see or submit transactions│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Encrypted Deposit / Withdrawal (ECIES-Based)

#### 3.2.1 Standard Deposit Flow (Reference: Tempo ECIES)

The encrypted deposit mechanism ensures that when assets move from the public mainchain into a privacy Zone, the recipient identity and transfer metadata are hidden from mainchain observers.

**Plaintext format:** `[recipient address (20 bytes)] [memo (32 bytes)] [padding (12 bytes)]` = 64 bytes total.

**Step-by-step flow:**

```
User                    Mainchain (ZonePortal)           Zone Sequencer
  │                            │                              │
  │ 1. Generate ephemeral      │                              │
  │    secp256k1 keypair       │                              │
  │                            │                              │
  │ 2. ECDH with Zone's        │                              │
  │    registered public key   │                              │
  │    → shared secret point   │                              │
  │                            │                              │
  │ 3. HKDF-SHA256 derives     │                              │
  │    AES-256-GCM key from    │                              │
  │    shared secret +         │                              │
  │    portal address context  │                              │
  │                            │                              │
  │ 4. AES-256-GCM encrypt     │                              │
  │    [recipient, memo]       │                              │
  │    → ciphertext + nonce    │                              │
  │      + tag                 │                              │
  │                            │                              │
  │ 5. depositEncrypted(       │                              │
  │    token, amount, keyIndex,│                              │
  │    [eph_pub_x, y_parity,  │                              │
  │     ciphertext, nonce,     │                              │
  │     tag])                  │                              │
  │ ─────────────────────────►│                              │
  │                            │                              │
  │    L1 VISIBILITY:          │ 6. DepositMade event         │
  │    token ✅                │ ────────────────────────────►│
  │    sender ✅               │                              │
  │    amount ✅               │ 7. ECDH: sequencerPrivKey    │
  │    recipient ❌ (encrypted)│    × ephemeralPub            │
  │    memo ❌ (encrypted)     │    → shared secret           │
  │                            │                              │
  │                            │ 8. Chaum-Pedersen DLOG       │
  │                            │    equality proof:           │
  │                            │    proves correct decryption │
  │                            │    without revealing privKey │
  │                            │                              │
  │                            │ 9. HKDF-SHA256 → AES key    │
  │                            │    → decrypt → (to, memo)    │
  │                            │                              │
  │                            │ 10. TIP-403 compliance check │
  │                            │     on decrypted recipient   │
  │                            │                              │
  │                            │ 11a. COMPLIANT:              │
  │                            │      credit in Zone          │
  │                            │                              │
  │                            │ 11b. NON-COMPLIANT:          │
  │                            │      bounce to sender        │
  │                            │                              │
  │                            │ 12. On-chain Chaum-Pedersen  │
  │                            │     verification:            │
  │                            │     precompile 0x1C00..0100  │
  │                            │     (6,000 gas)              │
  │                            │     R1 = s·G − c·pubSeq      │
  │                            │     R2 = s·eph − c·shared    │
  │                            │     c' = keccak256(...)      │
  │                            │     assert c == c'           │
```

**What is publicly visible on L1:** Only that a deposit of `amount` of `token` was made by `sender` into `zoneId`. The recipient and memo are encrypted. This reveals the existence and size of a deposit, but not who receives it within the Zone.

#### 3.2.2 Withdrawal Flow

```
User (in Zone)              Zone Sequencer              Mainchain (ZonePortal)
  │                              │                              │
  │ 1. ZoneOutbox.               │                              │
  │    requestWithdrawal(        │                              │
  │    token, amount, l1_dest)   │                              │
  │ ─────────────────────────►  │                              │
  │                              │                              │
  │                              │ 2. Aggregate withdrawals    │
  │                              │    into batch                │
  │                              │                              │
  │                              │ 3. Generate state           │
  │                              │    transition proof         │
  │                              │    (validity proof)         │
  │                              │                              │
  │                              │ 4. submitBatch(             │
  │                              │    blockTransition,         │
  │                              │    depositQueueTransition,  │
  │                              │    withdrawalQueueHash,     │
  │                              │    proof)                   │
  │                              │ ────────────────────────────►│
  │                              │                              │
  │                              │                              │ 5. Verify proof
  │                              │                              │    (or trust
  │                              │                              │    sequencer
  │                              │                              │    in Phase 1)
  │                              │                              │
  │ 6. processWithdrawal(withdrawal, remainingQueue)           │
  │ ────────────────────────────────────────────────────────────►│
  │                              │                              │
  │                              │                              │ 7. Release locked
  │                              │                              │    assets to l1_dest
```

**L1 visibility on withdrawal:** The withdrawal destination and amount are visible on L1 (the recipient's L1 address is public). For scenarios requiring withdrawal privacy, an optional **Shielded Withdrawal** variant uses a note commitment scheme:

```
Standard withdrawal:   l1_dest visible, amount visible
Shielded withdrawal:   commitment = hash(l1_dest, amount, nullifier)
                       Claim requires ZK proof of preimage knowledge
```

#### 3.2.3 Improvements over Tempo's Base ECIES

**Improvement 1 — Threshold ECIES (Avoiding Single-Point Trust):**

Tempo's current model uses a single sequencer key pair. If the sequencer key is compromised, all historical encrypted deposits can be decrypted. Our design introduces `t-of-n` threshold ECIES:

```
Key Generation:
  - n Zone operators/validators participate in DKG (Distributed Key Generation)
  - BLS12-381 curve (compatible with mainchain BFT signature scheme)
  - Public key published to ZonePortal
  - Private key shares distributed; no single party holds full key
  
Decryption:
  - t-of-n operators must contribute decryption shares
  - Shares combined to produce plaintext
  - Chaum-Pedersen proof extended to threshold setting
  
Configuration:
  - RWA Zone: 3-of-5 (high security, small participant set)
  - xstocks Zone: 2-of-3 (fast decryption, exchange operation)
  - Payment Zone: 1-of-1 (single operator sufficient — trust model is DA-level)
```

**Improvement 2 — Timelock Encryption (Preventing Front-Running):**

The Sequencer, upon decrypting a deposit, learns the recipient identity before the deposit is executed. This creates a front-running vector: the Sequencer could trade ahead of a large deposit. Timelock encryption addresses this:

```
Deposit encrypted with two keys:
  1. Zone ECIES key → immediate decryption by Sequencer (for compliance check)
  2. Timelock key → decryption only after block T+k (configurable delay)
  
Flow:
  - Sequencer decrypts with key 1: runs compliance check
  - Deposit queued for execution at block T+k
  - At block T+k, timelock key becomes available
  - Execution occurs; by this time, the Sequencer cannot reorder
  
Impact on latency:
  - Payment Zone: k=0 (no timelock — speed prioritized over MEV protection)
  - RWA Zone: k=1 (one block delay — minimal latency impact)
  - xstocks Zone: k=3 (three block delay — strong MEV protection)
```

### 3.3 Authenticated RPC

#### 3.3.1 Problem Statement

Standard Ethereum JSON-RPC allows anyone to query chain state: `eth_getBalance`, `eth_getTransactionByHash`, `eth_call` all return data to any caller. In a privacy Zone, this completely negates the privacy gained by Validium DA — anyone who can reach the RPC endpoint sees everything.

#### 3.3.2 Authentication Token Design

Extending Tempo's `x-authorization-token` format:

```
Token Format:
  ┌───────────────┬─────────┬─────────┬──────────┬──────────┬──────────┬──────────┐
  │ secp256k1 sig │ version │ zone_id │ chain_id │ issued_at│expires_at│ role     │
  │ (65 bytes)    │ (1 byte)│ (4 bytes)│ (8 bytes)│ (8 bytes)│ (8 bytes)│ (1 byte) │
  └───────────────┴─────────┴─────────┴──────────┴──────────┴──────────┴──────────┘
  
  Magic prefix: "TempoZoneRPC" (left-padded to 32 bytes)
  Signature: secp256k1 over keccak256(packed_message)
  Default validity: 30 days (2,592,000 seconds)
  zone_id = 0: unscoped (valid for any Zone — regulatory supervisor use)
  
  Roles (extension over Tempo):
    0x00: Zone Participant (standard user)
    0x01: Zone Operator (full Zone access)
    0x02: Regulatory Supervisor (cross-Zone audit access)
    0x03: External Observer (Zone metadata only)
    0x04: Compliance Auditor (time-bounded audit access)
```

**Supported authentication methods:**
- **Signed token (primary):** secp256k1 signature — cryptographic proof of identity
- **mTLS (enterprise):** Mutual TLS with client certificates — for machine-to-machine integration
- **JWT + Okta SSO (hybrid):** For web-based dashboard access (Prividium Proxy RPC model)

#### 3.3.3 Permission Model

| Role | Can Query Own Txs | Can Query Others' Txs | Can See Zone Aggregate Data | Can Submit Txs | Can See Raw Blocks | Audit Log Required |
|------|-------------------|----------------------|---------------------------|---------------|-------------------|-------------------|
| **Zone Participant** | ✅ | ❌ | ✅ (TVL, volume) | ✅ | ❌ | No |
| **Zone Operator** | ✅ | ✅ | ✅ | ✅ | ✅ | Yes |
| **Regulatory Supervisor** | ✅ | ✅ (with audit trail) | ✅ | ❌ | ✅ (with audit) | Yes (immutable) |
| **External Observer** | ❌ | ❌ | ✅ (limited: Zone exists, participant count) | ❌ | ❌ | No |
| **Compliance Auditor** | ✅ (audit scope) | ✅ (audit scope, time-bounded) | ✅ | ❌ | ✅ (audit scope) | Yes (immutable) |

#### 3.3.4 Query Filtering Implementation

The RPC layer implements per-account data filtering:

```
eth_getTransactionByHash(txHash):
  if caller.role == Participant:
    tx = fetch(txHash)
    if caller.address in tx.participants:
      return tx  // Full transaction data
    else:
      return null  // Tx doesn't exist (from this caller's perspective)
  if caller.role == Operator:
    return fetch(txHash)  // Full data, always
  if caller.role == Supervisor:
    tx = fetch(txHash)
    auditLog.record(caller, txHash, timestamp)
    return tx  // Full data + audit trail

eth_getBlockByNumber(blockNumber):
  if caller.role == Participant:
    block = fetch(blockNumber)
    block.transactions = block.transactions.filter(
      tx => caller.address in tx.participants
    )
    return block  // Only caller's transactions
  if caller.role == External:
    return {
      number: block.number,
      timestamp: block.timestamp,
      transactionCount: block.transactions.length,
      // transactions array omitted
      // logsBloom zeroed
    }
```

#### 3.3.5 Side-Channel Mitigations

Following Tempo's design:

| Attack Vector | Mitigation | Implementation |
|--------------|-----------|---------------|
| **Gas side-channel** | Fixed gas per user-facing TIP-20 operation | 100,000 gas per TIP-20 op (regardless of actual computation) |
| **Timing side-channel** | Minimum RPC response time | 100ms floor — responses held until timer expires |
| **Balance inference** | Sanitized block metadata | `transactions` array emptied, `logsBloom` zeroed for unauthorized callers |
| **Contract deployment inference** | Block opcodes | `CREATE` and `CREATE2` blocked inside Zones |
| **Traffic analysis** | Response padding | All RPC responses padded to nearest 1KB boundary |

### 3.4 Zone-Internal Privacy: Detailed Option Specifications

#### 3.4.1 Option A — Zone-Internal Transparent (Payment Zone)

All Zone participants have full visibility into all transactions. This is a traditional private chain model:

```
Privacy properties:
  - External observers: see nothing (Validium DA)
  - Zone participants: see everything
  - Sequencer: sees everything
  
Advantages:
  - Simplest implementation — standard EVM execution
  - Highest throughput (no encryption/proof overhead)
  - Compatible with standard Solidity tooling
  - Global state queries work natively (TVL, totalSupply)
  
Disadvantages:
  - No intra-Zone privacy — all participants see all transactions
  - Participant count limited by trust model (all members must be trusted)
  
Suitable when:
  - Participants are known institutions with existing relationships (banks in a payment network)
  - Regulatory requirements mandate full visibility within the network (Travel Rule)
  - Throughput is the primary constraint (>10,000 TPS)
```

#### 3.4.2 Option B — Sub-Transaction Privacy (RWA Zone)

Inspired by Canton's Merkle DAG projection model, adapted for EVM:

```
Transaction Decomposition:
  A DvP transaction between Alice (buyer) and Bob (seller) for RWA token:
  
  Global Transaction TX-001:
    ├── SubTx-1: Transfer USDC from Alice to Escrow    [visible to: Alice, Escrow]
    ├── SubTx-2: Transfer RWA token from Bob to Alice   [visible to: Bob, Alice, Registrar]
    ├── SubTx-3: Transfer USDC from Escrow to Bob       [visible to: Bob, Escrow]
    └── SubTx-4: Update Registrar cap table             [visible to: Registrar]
  
  Alice's View:   SubTx-1 (full), SubTx-2 (full), hash(SubTx-3), hash(SubTx-4)
  Bob's View:     hash(SubTx-1), SubTx-2 (full), SubTx-3 (full), hash(SubTx-4)
  Registrar:      hash(SubTx-1), SubTx-2 (full), hash(SubTx-3), SubTx-4 (full)
  Escrow:         SubTx-1 (full), hash(SubTx-2), SubTx-3 (full), hash(SubTx-4)
  Regulator:      SubTx-1, SubTx-2, SubTx-3, SubTx-4 (all — Observer role)

Projection Algorithm:
  projection(participant, subTx):
    if participant ∈ subTx.participants → return subTx (full content)
    elif subTx has children → recurse(participant, subTx.children)
    else → return commitmentHash(subTx)  // Merkle hash, no content

Encryption:
  Each sub-transaction encrypted with each participant's public key
  Sequencer routes encrypted blobs — operates on encrypted data
  Chaum-Pedersen proofs verify correct routing without content disclosure
```

**Implementation on EVM:**

Unlike Canton which uses Daml's native sub-transaction support, the EVM has no concept of sub-transactions. We implement this via a **Privacy-Aware Transaction Executor (PATE):**

```
PATE Architecture:
  1. Transaction Compiler: Decomposes Solidity transactions into sub-transactions
     based on contract-defined privacy annotations (@private, @participants)
  2. Merkle Builder: Constructs Merkle tree from sub-transactions
  3. Encryption Router: Encrypts each sub-tx for its participant set
  4. Projection Server: Maintains per-participant state views
  5. Consistency Verifier: Ensures all projections are consistent via Merkle proofs
```

Trade-off vs. Canton: Canton's Daml language provides native sub-transaction decomposition with minimal developer effort. Our EVM approach requires explicit privacy annotations and a compilation step, but retains full Solidity/Hardhat/Foundry toolchain compatibility — a major developer experience advantage (Solidity developer pool: hundreds of thousands vs. Daml: hundreds to thousands).

#### 3.4.3 Option C — ZK-Enhanced (xstocks Zone)

For securities trading, even intra-Zone participants must not see each other's orders:

```
ZK Order Matching Engine:

  1. Order Submission:
     Trader → Commit(price, quantity, side, nonce, trader_id)
     Commitment published to Zone chain
     Only Sequencer sees plaintext (Sequencer-as-Compliance-Officer)
     
  2. Pre-Trade Compliance (Sequencer):
     Sequencer decrypts order → checks:
       - Trader KYC status (IdentityRegistry precompile 0x0401)
       - Position limits (ComplianceCheck precompile 0x0402)
       - Restricted list screening (PolicyRegistry precompile 0x0403)
       - Short-sale restrictions (Reg SHO)
     Non-compliant orders rejected with generic error (no information leakage)
     
  3. Matching:
     Sequencer runs standard price-time-priority matching on plaintext
     Produces match results: [(order_A, order_B, execution_price, quantity)]
     
  4. Post-Match ZK Proofs:
     Sequencer generates proofs:
       a. PROOF_FAIR_MATCH: matching respected price-time priority
          (prevents Sequencer from preferentially matching certain orders)
       b. PROOF_NO_WASH: no self-dealing (same beneficial owner on both sides)
       c. PROOF_VOLUME: aggregate volume disclosure is correct
       d. PROOF_BEST_EXECUTION: execution price within NBBO (Reg NMS)
     
  5. Settlement:
     Matched orders settled atomically within Zone
     Each trader receives only their fills (not other traders' fills)
     Post-trade report generated per regulatory timeline:
       - Immediate: to regulators via Supervisor RPC
       - T+15min: aggregate volume to participants (post-trade transparency)
       - T+end-of-day: full OATS-equivalent audit trail to compliance

Dark Pool Privacy Guarantee:
  Pre-trade:  Price ❌  Quantity ❌  Identity ❌  (all hidden)
  In-flight:  Price ❌  Quantity ❌  Identity ❌  (Sequencer sees, others don't)
  Post-trade: Price ✅  Quantity ✅  Identity ❌  (delayed disclosure)
  Audit:      Price ✅  Quantity ✅  Identity ✅  (regulatory access only)
```

### 3.5 Validity Proof System

Validity proofs allow Zones to prove correctness to the mainchain and external parties without revealing private data.

#### 3.5.1 Proof Types

| Proof Type | What It Proves | What It Hides | ZK System | Gas Cost | Phase |
|-----------|---------------|--------------|-----------|---------|-------|
| **State Transition Proof** | Zone state transitions follow correct EVM rules (old_root → new_root) | All transaction details, participants, amounts | SP1/RISC-V STARK (soundness ≥ 2^{-80}) | Batch verification on mainchain | Phase 3 |
| **Compliance Proof** | Zone transactions satisfy compliance rules (no sanctioned parties, within limits) | Individual transaction details, participant identities | STARK with public compliance policy input | 5,000 gas (ComplianceCheck precompile) | Phase 2 |
| **Balance Proof (Solvency)** | Zone asset totals match mainchain locked amounts (no assets created/destroyed) | Per-account balances, individual positions | STARK with Merkle commitment to account tree | Batch verification | Phase 2 |
| **Selective Disclosure Proof** | Specific fact about participant (e.g., "balance > X", "identity ∈ accredited set") | Everything else about the participant | SelectiveDisclosure precompile (0x0405, 8,000 gas) | 8,000 gas per proof | Phase 2 |

#### 3.5.2 ZK Compliance Proofs — PII-Free Sanctions Screening

This is the highest-value ZK application identified across all reference systems (WHI-343 Insight 4):

```
Traditional Sanctions Screening:
  Bank A asks Bank B: "Is your customer on the OFAC SDN list?"
  Bank B responds: "No" (self-declaration — trust required)
  Problem: B could lie; A has no verification; PII exchanged

ZK Sanctions Screening:
  Bank B generates ZK proof π:
    Public inputs: OFAC SDN list hash (published, verifiable)
    Private inputs: Customer PII (name, DOB, passport number)
    Statement: "My customer's identity does not match any entry
               in the SDN list with hash H"
  
  Bank A verifies π:
    Checks: proof is valid against known SDN list hash
    Result: Cryptographic certainty of non-match
    PII exposure: ZERO
    
  Regulatory quality: HIGHER than self-declaration
    - Cryptographically unforgeable (vs. honor system)
    - Automatically verifiable (vs. manual review)
    - Auditable (proof can be archived and re-verified)
```

#### 3.5.3 Balance Proofs — Solvency Verification

Balance proofs (also called solvency proofs) address a critical trust question: "How do I know the Zone hasn't created assets out of thin air?" Since Zone DA is off-chain (Validium), external parties cannot independently verify the Zone's internal state. Balance proofs provide cryptographic assurance:

```
Solvency Proof Construction:

  Public Inputs:
    - mainchainLockedAmount: total assets locked in ZonePortal on mainchain
    - stateRoot: Zone's latest committed state root
    - assetId: the token being proven
    
  Private Inputs:
    - accountTree: Sparse Merkle Tree of all Zone account balances
    - totalZoneBalance: sum of all account balances for assetId
    
  Statement:
    "The sum of all account balances in the Zone for assetId equals
     mainchainLockedAmount, and accountTree is consistent with stateRoot."
    
  Proof System: STARK (SP1/RISC-V prover)
  
  Verification:
    Mainchain ZonePortal runs STARK verifier
    Checks: proof valid ∧ mainchainLockedAmount matches on-chain record
    
  Frequency: 
    - Payment Zone: every batch submission (high frequency, small proof)
    - RWA Zone: daily (lower frequency, larger proof due to complex asset types)
    - xstocks Zone: per trading session (end-of-session settlement proof)
```

**What this prevents:** A malicious Sequencer cannot inflate Zone balances (e.g., creating 1M USDC that doesn't exist on mainchain). The proof cryptographically binds Zone-internal balances to mainchain-locked amounts. If the proof fails, the mainchain can halt further withdrawals from the Zone — protecting asset holders.

#### 3.5.4 Selective Disclosure Proof Specification

The `SelectiveDisclosure` precompile (address `0x0405`, 8,000 gas) enables Zone participants to prove specific facts about themselves to third parties without revealing their full state:

```
Selective Disclosure Use Cases:

  1. Accredited Investor Proof:
     Statement: "My account is marked as accredited investor in IdentityRegistry"
     Public: proof of accredited status
     Hidden: name, address, net worth, specific accreditation date
     Use: RWA Zone admission without full KYC re-disclosure
     
  2. Balance Threshold Proof:
     Statement: "My USDC balance in Zone X exceeds $1,000,000"
     Public: proof of threshold satisfaction
     Hidden: exact balance, transaction history, counterparties
     Use: Qualifying for institutional-tier services
     
  3. Transaction History Proof:
     Statement: "I have completed > 100 transactions in Zone X with 0 compliance flags"
     Public: proof of clean trading history
     Hidden: specific transactions, amounts, counterparties
     Use: Reputation/credibility for cross-Zone admission
     
  4. Geographic Compliance Proof:
     Statement: "My verified jurisdiction is in the set {US, EU, SG, HK, JP}"
     Public: proof of permitted jurisdiction
     Hidden: specific country, address, passport details
     Use: Cross-border data localization compliance

Precompile Interface:
  Input:  (proofType, publicInputs, proof)
  Output: (valid: bool)
  Gas:    8,000 (fixed, regardless of proof complexity — side-channel mitigation)
  
  The proof is generated off-chain by the participant using their private data.
  The precompile only verifies — it never sees the private inputs.
```

#### 3.5.5 Viewing Key Architecture for Tiered Authorization

Beyond one-time selective disclosure proofs, the design supports **persistent viewing keys** that grant ongoing read access to specific data scopes:

```
Viewing Key Hierarchy:

  Level 0: No key → sees nothing (external observer default)
  
  Level 1: Zone-level viewing key
    Grants: see Zone existence, participant count, aggregate volume
    Issued by: Zone operator
    Validity: configurable (default: 90 days)
    Use case: business development, market research
    
  Level 2: Account-level viewing key
    Grants: see specific account's balances and transaction history
    Issued by: Account holder (self-sovereign)
    Validity: configurable, revocable by issuer
    Use case: portfolio reporting to fund administrators
    
  Level 3: Audit viewing key
    Grants: see all Zone transactions within a time scope
    Issued by: t-of-n Zone governance threshold
    Validity: time-bounded (audit period only)
    Use case: regulatory audit, compliance review
    
  Level 4: Master viewing key
    Grants: see all Zone data, all time
    Issued by: supermajority Zone governance (emergency only)
    Validity: event-bounded (specific investigation)
    Use case: existential threat response, wind-down

Key Derivation:
  masterKey = threshold_DKG(zone_operators)
  level3_key = HKDF(masterKey, "audit" || auditId || startBlock || endBlock)
  level2_key = participant_privkey (self-sovereign, not derived from master)
  level1_key = HKDF(masterKey, "zone-summary" || validityPeriod)
  
Key Revocation:
  All derived keys are revocable by the issuer via on-chain revocation registry.
  Revoked keys are added to a CRL (Certificate Revocation List) stored in ZoneRegistry.
  RPC layer checks CRL before serving data.
```

#### 3.5.6 Architectural Preparation for Proof System

Following WHI-357's approach, the proof system is architecturally pre-baked even before implementation:

1. **All custom precompiles are `no_std` compatible** — designed to run inside SP1/RISC-V prover guest
2. **`submitBatch()` has a `proof` parameter slot** — currently submitted as empty bytes
3. **`ZonePortal` has a `verifier()` address field** — currently unset
4. **Custom transaction types allocated:** `0x78` = Privacy transaction (carries ZK proof)
5. **Dual verification path planned:** ZKVM (SP1/RISC-V) primary, TEE (SGX/TDX) fallback

Migration path: Phase 1 runs on Sequencer trust only → Phase 2 adds selective disclosure and compliance proofs → Phase 3 adds full state transition proofs, eliminating trust in Sequencer for correctness (trust remains only for liveness/DA).

---

## 4. Data Sovereignty Architecture

### 4.1 Data Layer Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Layer 5: EPHEMERAL DATA                                                    │
│  Storage: Memory / cache                                                    │
│  Visibility: Node-local only                                                │
│  Retention: Duration of session / processing                                │
│  Examples: Mempool contents, unconfirmed transactions, RPC query cache       │
│  Deletion: Automatic on node restart                                        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 4: AUDIT DATA                                                        │
│  Storage: Encrypted archive (Zone operator managed)                         │
│  Visibility: Authorized auditors via Compliance Auditor role                │
│  Retention: Configurable per regulatory regime                              │
│    - MiFID II: 5 years transaction records, 7 years communications          │
│    - SEC Rule 17a-4: 6 years (first 2 in easily accessible location)       │
│    - AML Directives: 5 years post-relationship                             │
│  Encryption: AES-256-GCM with per-Zone audit key (threshold-managed)        │
│  Access: Time-bounded audit sessions with immutable audit trail             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 3: ZONE ENCRYPTED DATA                                               │
│  Storage: Zone DA backend (Operator's private PostgreSQL)                   │
│  Visibility: Zone participants via Authenticated RPC                        │
│  Retention: Configurable per Zone (dataRetentionDays parameter)             │
│  Encryption: ECIES (deposits/withdrawals), per-participant keys (sub-tx)    │
│  Deletion: Physical deletion possible (Validium model — not on L1)          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 2: PUBLIC MAINCHAIN DATA                                             │
│  Storage: Mainchain DA (full nodes + Alt-DA)                                │
│  Visibility: Public (anyone running a node or querying public RPC)          │
│  Retention: Long-term (full node history, prunable with state snapshots)    │
│  Contents: DeFi transactions, asset registry, Zone registration events,     │
│            governance decisions, identity attestation anchors               │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 1: L1 ANCHOR DATA (Ethereum)                                         │
│  Storage: Ethereum mainnet (blob / calldata)                                │
│  Visibility: Global public, permanent                                       │
│  Retention: Permanent (Ethereum's immutability guarantee)                   │
│  Contents: Batch state commitments (state root + proof hash),               │
│            ZK proofs, bridge contract state                                 │
│  Privacy: Contains NO transaction-level data — only aggregate commitments   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**DA routing rule:** The DA target for each transaction is automatically determined by the Zone type and transaction attributes. The Sequencer applies the following routing logic:

```
function routeDA(tx, zone):
  if zone.type == PUBLIC_MAINCHAIN:
    return DA_PUBLIC           // Layer 2: public mainchain DA
  elif zone.privacyTier == T0:
    return DA_PUBLIC
  else:
    primaryDA = DA_ZONE        // Layer 3: Zone encrypted storage
    
    // Generate audit copy if required
    if zone.auditEnabled && tx.requiresAudit():
      auditCopy = encrypt(tx, zone.auditKey)
      store(auditCopy, DA_AUDIT)  // Layer 4
    
    return primaryDA
```

### 4.2 Data Sovereignty Principles

#### 4.2.1 Data Ownership

**Principle:** Zone transaction data belongs to the Zone participants, not the Zone operator.

```
Ownership Model:
  
  Transaction Data:
    - Created by: Transaction participants (sender + receiver)
    - Stored by: Zone operator (custodial storage, not ownership)
    - Owned by: Transaction participants (joint ownership)
    - Operator obligations:
      · Must provide data access to participants on request
      · Must not share data with non-participants without consent or legal order
      · Must not use data for operator's own commercial purposes
      · Must delete data when retention period expires (unless regulatory hold)
    
  Aggregate/Derived Data:
    - TVL, volume statistics, compliance reports
    - Created by: Zone operator from participant data
    - Owned by: Zone operator (derived work)
    - Constraint: Must not allow reverse-engineering of individual transactions
```

**Enforcement mechanism:** The Zone Charter (a smart contract deployed at Zone creation) encodes data ownership rules. Violations are detectable via audit trail and enforceable via governance slashing of Zone operator's stake.

#### 4.2.2 Data Portability (GDPR Article 20)

```
Participant Data Export API:

GET /api/v1/zone/{zoneId}/participant/{address}/export
Authorization: Bearer <participant_token>

Response:
{
  "participantAddress": "0x...",
  "zoneId": 42,
  "exportTimestamp": "2026-05-07T00:00:00Z",
  "format": "application/json",
  "data": {
    "transactions": [
      {
        "hash": "0x...",
        "timestamp": "...",
        "type": "transfer",
        "counterparties": ["0x..."],  // Only if participant is a party
        "amount": "1000.00",
        "asset": "USDC",
        "status": "settled"
      }
    ],
    "balanceHistory": [...],
    "complianceRecords": [...],
    "auditTrail": [...]
  },
  "merkleProof": {
    "stateRoot": "0x...",
    "proof": ["0x...", ...]  // Proves data inclusion in Zone state
  }
}
```

The Merkle proof allows the participant to cryptographically verify that the exported data matches the Zone's committed state — preventing the operator from providing tampered data.

#### 4.2.3 Right to Be Forgotten (GDPR Article 17)

The fundamental tension: blockchain immutability vs. the right to erasure.

**Resolution architecture:**

```
Blockchain Immutability vs. GDPR Erasure:

Layer 1 (Ethereum): 
  Contains only state root hashes and ZK proofs
  → NO personal data on L1 → No GDPR erasure issue

Layer 2 (Public Mainchain):
  Contains DeFi transactions (public, no PII expectation)
  Contains Zone registration events (no PII)
  → Minimal PII exposure → Standard blockchain GDPR stance

Layer 3 (Zone DA — CRITICAL LAYER):
  Contains all privacy-sensitive transaction data
  Stored in operator's private database (NOT on-chain)
  → PHYSICAL DELETION IS POSSIBLE
  
Erasure Protocol:
  1. Participant submits erasure request to Zone operator
  2. Operator verifies identity and request validity
  3. Operator checks regulatory holds:
     - If active regulatory retention requirement → defer, notify participant
     - If no hold → proceed
  4. Operator encrypts participant's data with ephemeral key
  5. Operator archives encrypted data (for retention period if applicable)
  6. At retention period expiry: destroy ephemeral key
     → Encrypted data becomes cryptographically unrecoverable
     → This constitutes "logical deletion" under GDPR guidance
  7. Physical deletion of encrypted blobs (optional, depends on storage backend)
  8. Confirmation receipt issued to participant with timestamp + proof

Zone Closure Erasure:
  When a Zone closes (Section 2.2.4):
  - All participant data encrypted with Zone-closure key
  - Zone-closure key escrowed for regulatory retention period
  - At retention expiry: key destruction = mass logical deletion
  - Physical cleanup of Zone DA storage
```

**GDPR vs. SEC/MiFID II conflict resolution:**

| Regulation | Requirement | Resolution |
|-----------|-------------|-----------|
| GDPR Art. 17 | Right to erasure "without undue delay" | Encryption + key destruction = logical deletion |
| SEC Rule 17a-4 | 6 years retention of transaction records | Retention period defers physical deletion |
| MiFID II Art. 16 | 5 years transaction records, 7 years communications | Layered: PII fields deleted, transaction metadata retained |
| AML 6th Directive | 5 years post-relationship | Anonymized records retained after PII deletion |

**Implementation:** The Zone DA uses a **field-level encryption** scheme where PII fields and non-PII fields use different encryption keys. At GDPR erasure:
- PII key destroyed → PII unrecoverable
- Transaction metadata key retained → aggregate compliance reporting still possible
- After regulatory retention period → all keys destroyed

#### 4.2.4 Cross-Border Data Sovereignty

```
Data Localization Framework:

┌─────────────────────────────────────────────────────┐
│                                                     │
│  Zone Node Geographic Constraints                   │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ EU-Resident  │  │ APAC-Resident│                │
│  │ RWA Zone     │  │ Payment Zone │                │
│  │              │  │              │                │
│  │ Nodes: EU    │  │ Nodes: SG,   │                │
│  │ only (GDPR)  │  │ HK, JP       │                │
│  │              │  │ (MAS, HKMA,  │                │
│  │ DA: EU data  │  │  FSA)        │                │
│  │ center       │  │              │                │
│  └──────────────┘  └──────────────┘                │
│                                                     │
│  Cross-Zone Data Flow Compliance Gate:              │
│                                                     │
│  Zone A (EU) ──► Cross-Border Check ──► Zone B (SG) │
│                  ├─ Standard Contractual Clauses?    │
│                  ├─ Adequacy Decision?               │
│                  ├─ Binding Corporate Rules?          │
│                  └─ Data minimization applied?        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Zone configuration parameters for data localization:**

```solidity
struct DataLocalizationConfig {
    bytes2[] allowedCountryCodes;    // ISO 3166-1 alpha-2
    bool strictLocalization;          // If true, data NEVER leaves jurisdiction
    bytes32 transferMechanism;        // SCC, BCR, adequacy_decision, etc.
    uint256 crossBorderApprovalThreshold; // t-of-n approval for cross-border
}
```

**Enforcement:** Zone Sequencer nodes must prove geographic location via attestation (hardware attestation for TEE-based nodes, IP geolocation + contractual obligation for cloud-hosted nodes). The mainchain `ZoneRegistry` records allowed geographic constraints and rejects batch submissions from nodes outside the allowed region.

### 4.3 Audit & Regulatory Access Framework

#### 4.3.1 Routine Audits

```
Routine Audit Flow:

  Zone Operator                    Compliance System              Regulator
       │                                │                           │
       │ 1. Generate periodic            │                           │
       │    compliance report            │                           │
       │    (daily/weekly/monthly)       │                           │
       │ ──────────────────────────────►│                           │
       │                                │                           │
       │                                │ 2. Report contains:       │
       │                                │    - Aggregate statistics  │
       │                                │      (volume, count,      │
       │                                │       avg size)           │
       │                                │    - Compliance metrics    │
       │                                │      (KYC check pass rate, │
       │                                │       sanctions hits)     │
       │                                │    - Anomaly flags        │
       │                                │    NO individual tx data   │
       │                                │                           │
       │                                │ 3. Generate ZK proof:     │
       │                                │    "This report correctly │
       │                                │     summarizes the Zone   │
       │                                │     state for period P"   │
       │                                │                           │
       │                                │ 4. Deliver report +       │
       │                                │    ZK proof               │
       │                                │ ──────────────────────────►│
       │                                │                           │
       │                                │                           │ 5. Verify ZK proof
       │                                │                           │    against known
       │                                │                           │    Zone state root
       │                                │                           │
       │                                │                           │ 6. ACCEPT/QUERY
```

**Report structure:**

```json
{
  "zoneId": 42,
  "period": { "start": "2026-05-01", "end": "2026-05-31" },
  "aggregate": {
    "transactionCount": 15234,
    "totalVolume": "1,234,567,890.00 USDC",
    "uniqueParticipants": 47,
    "avgTransactionSize": "81,042.00 USDC",
    "maxTransactionSize": "50,000,000.00 USDC"
  },
  "compliance": {
    "kycChecksPassed": 15234,
    "kycChecksFailed": 3,
    "sanctionsScreeningPassed": 15234,
    "sanctionsScreeningFlagged": 0,
    "travelRuleCompliant": 15234,
    "suspiciousActivityReports": 2
  },
  "proof": {
    "type": "STARK",
    "publicInputs": ["stateRoot_start", "stateRoot_end", "reportHash"],
    "proof": "0x..."
  }
}
```

#### 4.3.2 Special Audits (Court Order / Regulatory Investigation)

When a regulator requires access to specific transaction data (e.g., SEC investigation, court order), the system supports **targeted decryption** without exposing the entire Zone:

```
Special Audit Protocol:

  1. LEGAL BASIS VERIFICATION
     - Regulatory request validated by Zone governance
     - Legal basis documented (court order number, regulatory authority, scope)
     - Scope defined: specific accounts, time range, transaction types
     
  2. THRESHOLD DECRYPTION
     - Audit scope parameters → smart contract
     - t-of-n key holders convene
     - Each key holder independently verifies legal basis
     - t signatures collected → threshold decryption key derived
     - Key is SCOPED: can only decrypt data matching the audit parameters
     
  3. AUDIT SANDBOX
     - Isolated environment provisioned for regulator
     - Scoped data decrypted and loaded into sandbox
     - Regulator queries data via Compliance Auditor RPC role
     - All queries logged in immutable audit trail
     - Sandbox has network isolation (data cannot be exfiltrated)
     
  4. AUDIT COMPLETION
     - Regulator signs audit completion attestation
     - Sandbox destroyed
     - Scoped decryption key destroyed
     - Audit trail archived (permanent record of regulatory access)
     
  Access Escalation Hierarchy:
    Level 1: ZK compliance report (no data exposure)
    Level 2: Aggregate statistics with proof (minimal exposure)
    Level 3: Scoped transaction data in sandbox (targeted exposure)
    Level 4: Full Zone decryption (emergency — requires supermajority of key holders
             + documented existential threat + governance approval)
```

#### 4.3.3 Real-Time Monitoring

Privacy-preserving surveillance that operates without exposing individual transaction data:

```
Real-Time Monitoring Stack:

  1. ANOMALY DETECTION (Sequencer-side)
     The Sequencer sees all plaintext (Sequencer-as-Compliance-Officer)
     Runs anomaly detection models on live data:
       - Unusual volume spikes (>3σ from 30-day mean)
       - Rapid account creation + high-value transfers
       - Circular transaction patterns
       - Structuring detection (multiple sub-threshold transfers)
     Alerts: generated as ZK-proofed anomaly flags
       "There exists a pattern matching structuring criteria in the last 24h"
       (does NOT reveal which transactions or accounts)
     
  2. SANCTIONS SCREENING (Pre-execution)
     Every transaction checked against OFAC SDN / EU sanctions lists
     Implemented at Sequencer mempool level (before block inclusion)
     Privacy-preserving: ZK sanctions proof for cross-Zone communication
     Sanctioned addresses: transactions rejected silently (no information leakage)
     
  3. TRAVEL RULE ENGINE (Payment Zone specific)
     Activated for transfers ≥ $3,000 (FATF Recommendation 16)
     Automatically attaches:
       - Originator institution information
       - Beneficiary institution information
     Routing: data sent only to receiving institution + regulators
     Not visible to other Zone participants
     
  4. MARKET SURVEILLANCE (xstocks Zone specific)
     Sequencer runs real-time market surveillance:
       - Insider trading pattern detection
       - Market manipulation indicators (spoofing, layering)
       - Best execution monitoring (Reg NMS compliance)
     Alerts to compliance officer; escalation to regulator if threshold met
```

---

## 5. Cross-Zone Interoperability

### 5.1 Cross-Zone Asset Transfer Protocol

Cross-Zone transfers use the mainchain as a settlement hub. The current design implements a **two-step bridge** (Zone A → mainchain → Zone B) with privacy preservation at each step.

#### 5.1.1 Standard Cross-Zone Transfer

```
Zone A (RWA)              Mainchain Settlement Layer          Zone B (Payment)
    │                              │                              │
    │ 1. User initiates            │                              │
    │    cross-Zone transfer       │                              │
    │    ZoneOutbox.               │                              │
    │    requestWithdrawal(        │                              │
    │    token, amount,            │                              │
    │    destZone=B, destAddr)     │                              │
    │                              │                              │
    │ 2. Zone A Sequencer          │                              │
    │    aggregates into batch     │                              │
    │                              │                              │
    │ 3. submitBatch(              │                              │
    │    blockTransition,          │                              │
    │    withdrawalQueueHash,      │                              │
    │    proof)                    │                              │
    │ ────────────────────────────►│                              │
    │                              │                              │
    │                              │ 4. Verify batch (or trust    │
    │                              │    sequencer in Phase 1)     │
    │                              │                              │
    │ 5. processWithdrawal()       │                              │
    │ ────────────────────────────►│                              │
    │                              │ 6. Assets released to        │
    │                              │    mainchain (user's L1      │
    │                              │    address)                  │
    │                              │                              │
    │                              │ 7. User deposits to Zone B   │
    │                              │    ZonePortalB.              │
    │                              │    depositEncrypted(         │
    │                              │    token, amount, keyIndex,  │
    │                              │    [eph_pub, ciphertext,     │
    │                              │     nonce, tag])             │
    │                              │ ────────────────────────────►│
    │                              │                              │
    │                              │                              │ 8. Zone B Sequencer
    │                              │                              │    decrypts deposit
    │                              │                              │
    │                              │                              │ 9. TIP-403 compliance
    │                              │                              │    check on recipient
    │                              │                              │
    │                              │                              │ 10. Credit in Zone B
```

#### 5.1.2 Privacy Preservation During Transfer

**What is exposed at each step:**

| Step | Visible Data | Hidden Data | Privacy Mechanism |
|------|-------------|-------------|------------------|
| Zone A withdrawal | Withdrawal request exists | Withdrawal destination, purpose | Zone-internal encrypted log |
| Batch submission | Batch state transition hash | Individual withdrawals | Batch aggregation |
| Mainchain transit | Token, amount, sender's L1 address | Destination Zone, ultimate recipient | Standard L1 transaction |
| Zone B deposit (encrypted) | Token, amount, depositor L1 address | Recipient within Zone B, memo | ECIES encryption |
| Zone B internal credit | — | Everything (Zone B is Validium) | Validium DA |

**Privacy gap:** During mainchain transit (steps 5-7), the token and amount are visible on the mainchain. An observer can link the withdrawal from Zone A to the deposit into Zone B by correlating amount, token, and timing. Mitigations:

```
Mitigation 1 — Batched transfers:
  Multiple cross-Zone transfers batched into single mainchain transactions
  Amounts pooled → individual transfer amounts obscured
  Timing: batch processed at fixed intervals (not on-demand)

Mitigation 2 — Amount splitting:
  Large transfers split into multiple smaller transfers
  Each sub-transfer uses different timing
  Reassembled in destination Zone

Mitigation 3 — Cross-Zone Proof (Phase 3):
  ZK proof that "assets leaving Zone A = assets entering Zone B"
  Without revealing amount, sender, or recipient on mainchain
  Requires ZK proof infrastructure (SP1 prover)
```

#### 5.1.3 Atomicity Guarantees

**Current (Phase 1): Non-atomic two-step bridge.**

The two-step process has a time window between withdrawal and deposit. During this window, assets are on the mainchain (user's L1 address). Failure modes:

| Failure | Impact | Recovery |
|---------|--------|----------|
| Zone A withdrawal succeeds, user doesn't deposit to Zone B | Assets remain on mainchain | User can deposit later or use mainchain |
| Zone B deposit rejected (compliance failure) | Assets remain on mainchain | User notified; can retry or deposit elsewhere |
| Zone B Sequencer offline | Deposit pending in ZonePortal queue | Processed when Sequencer recovers |

**Future (Phase 2-3): Atomic cross-Zone options.**

```
Option A — HTLC (Hash Time-Lock Contracts):
  Complexity: Low
  Atomicity: Conditional (timeout-based)
  Privacy: Hash preimage revealed to both Zones (linkable)
  Suitable for: Payment Zone ↔ Payment Zone transfers

Option B — Canton-style 2PC via Global Synchronizer:
  Complexity: High
  Atomicity: True atomic (2PC commit/abort)
  Privacy: Sequencer coordination required (metadata leakage)
  Suitable for: RWA Zone DvP with Payment Zone settlement

Option C — ZK Cross-Zone Proof:
  Complexity: Very high (requires recursive ZK proofs)
  Atomicity: True atomic (proof validity = atomicity)
  Privacy: Maximum (only proof on mainchain, no data)
  Suitable for: Long-term architecture target
```

**Recommendation:** Phase 1 uses non-atomic two-step. Phase 2 introduces HTLC for Payment-to-Payment transfers and evaluates 2PC for RWA DvP. Phase 3 targets ZK cross-Zone proofs.

### 5.2 Cross-Zone Communication Protocol

#### 5.2.1 Message Format

```
CrossZoneMessage {
  header: {
    version: uint8,
    sourceZoneId: uint32,
    destZoneId: uint32,
    messageType: enum { ASSET_TRANSFER, COMPLIANCE_QUERY, POLICY_UPDATE, HEARTBEAT },
    nonce: uint64,
    timestamp: uint64,
    ttl: uint32,        // Time-to-live in blocks
  },
  payload: {
    encrypted: bool,
    encryptionScheme: enum { NONE, ECIES, THRESHOLD_ECIES },
    data: bytes,        // Encrypted or plaintext depending on scheme
  },
  routing: {
    viaMainchain: bool, // Must transit through mainchain settlement
    directChannel: bool, // Operator-to-operator direct channel (if available)
  },
  signature: bytes65,    // Sequencer or participant signature
}
```

#### 5.2.2 Routing & Discovery

Zone discovery is handled by the mainchain `ZoneRegistry`:

```
ZoneRegistry provides:
  - getZone(zoneId) → ZoneConfig (type, privacy tier, endpoint, operator)
  - getZonesByType(zoneType) → ZoneConfig[]
  - isZoneActive(zoneId) → bool
  - getZoneEndpoint(zoneId) → RPC endpoint (for authorized callers only)
```

Cross-Zone message routing:
1. **Via mainchain (default):** All cross-Zone asset transfers and compliance-critical messages route through mainchain events and ZonePortal contracts. This is the trust-minimized path.
2. **Direct channel (optimization):** Zone operators may establish direct encrypted channels for non-asset messages (compliance queries, heartbeats). This is an optimization — the mainchain path remains the fallback.

#### 5.2.3 Failure Handling

| Failure Mode | Detection | Response | Timeout |
|-------------|-----------|----------|---------|
| Destination Zone offline | Heartbeat miss (3 consecutive) | Message queued in mainchain ZonePortal | 24 hours → auto-revert |
| Message corruption | Signature verification failure | Reject + alert source Zone | Immediate |
| Compliance rejection | Zone B TIP-403 check fails | Assets returned to source Zone | 1 hour |
| TTL expiry | Block number exceeds message TTL | Message discarded, source notified | Configurable per message |

---

## 6. Comparison with Existing Solutions

### 6.1 Comprehensive Comparison Matrix

| Dimension | Tempo Zones | Canton Privacy | Prividium | **This Design** |
|-----------|------------|---------------|-----------|-----------------|
| **Privacy model** | Zone isolation + ECIES encrypted deposits | Sub-transaction Merkle DAG projection | Validium + Proxy RPC + RBAC | **Hybrid: Zone isolation (Layer 1-2) + per-Zone selectable internal privacy (A/B/C) + ZK proofs (Layer 3)** |
| **Privacy granularity** | Zone-level + field-level (deposit to/memo) | Sub-transaction (finest grain) | Chain-level + function-level (RBAC) | **Configurable per Zone: from Zone-level (Payment) to sub-transaction (RWA) to ZK-enhanced (xstocks)** |
| **Data visibility** | Zone-internal transparent; sanitized blocks for external | Minimum knowledge — each party sees only their relevant subtree | Full-node visible to operator; RBAC controls external access | **Tier-based: T0 (public) through T3 (sub-transaction), selectable per Zone** |
| **Sequencer trust** | Fully trusted (decrypts all deposits) | Not trusted (sees only encrypted blobs) | Fully trusted (operator controls everything) | **Trusted but reframed: Sequencer-as-Compliance-Officer; trust reduced progressively via ZK proofs in Phase 2-3** |
| **Cross-domain interop** | Zone ↔ L1 (two-step bridge) | Domain ↔ Domain (Global Synchronizer 2PC) | Chain ↔ Chain (L1 bridge) | **Zone ↔ Mainchain (two-step bridge, Phase 1); HTLC + 2PC (Phase 2); ZK cross-Zone proofs (Phase 3)** |
| **Regulatory access** | Sequencer has full visibility; no structured audit module | Observer Node — regulator added as party, sees actual data | Five disclosure mechanisms + Compliance Explorer | **Four-level escalation: ZK report → aggregate stats → scoped sandbox → full decryption; threshold-gated** |
| **ZK usage** | Proof slot prepared, not yet generating proofs | None (encrypted routing sufficient) | Full STARK state transition proofs (Airbender) | **Phased: compliance proofs + selective disclosure (Phase 2); full state transition proofs (Phase 3)** |
| **Sanctions screening** | TIP-403 policy check at Sequencer level | Not native (must be added by application) | ZK sanctions proof (PII-free) | **TIP-403 at Sequencer + ZK sanctions proofs for cross-Zone (combining Tempo + Prividium approaches)** |
| **GDPR compliance** | Validium DA supports deletion | Native: participants delete local data independently | Operator controls off-chain DB, physical deletion possible | **Full GDPR framework: field-level encryption, key destruction = logical deletion, layered retention** |
| **Smart contract model** | EVM (Solidity) | Daml (proprietary) | EVM (Solidity) | **EVM (Solidity) + privacy annotations for Option B sub-transaction decomposition** |
| **Complexity** | Medium | High | Low | **Medium-High (Phase 1: Medium; Full implementation: High)** |
| **Developer experience** | Full Ethereum toolchain | Daml learning curve; small developer pool | Full Ethereum toolchain | **Full Ethereum toolchain + Privacy SDK for sub-tx annotations** |

### 6.2 Deep-Dive: Privacy Model Trade-off Analysis

#### Canton's Sub-Transaction Privacy: Lessons Learned

Canton's Merkle DAG projection model achieves the finest-grained privacy in production today, processing $2T+/month across 450+ participants (Goldman Sachs, HSBC, DTCC). Its core strength is that the "Virtual Global Ledger" exists nowhere — it is the logical union of all participants' local projections stored in individual PostgreSQL databases.

**What we adopt from Canton:**
- The projection algorithm for Option B (RWA Zone): `projection(P, action) = if P ∩ informees(action) ≠ ∅ → retain full subtree, else → drop or hash`
- The principle that encrypted routing (low-complexity crypto) can achieve finer privacy than heavy ZK machinery
- Observer role for regulators: embedded audit access to actual data, not just proofs
- Explicit Disclosure mechanism: bilateral data sharing with consent

**What we improve over Canton:**
- Replace Daml DSL with Solidity + privacy annotations (100,000x larger developer pool)
- Add ZK compliance proofs (Canton has none — it relies on Observer-based audit which requires real-time regulator embedding)
- Add global aggregate queries (Canton's minimum-knowledge model makes `totalSupply()` impossible without explicit aggregation)
- Add quantitative performance targets (Canton publishes no TPS benchmarks)

**What we deliberately reject from Canton:**
- Sequencer blindness. Canton's Sequencer sees only encrypted blobs — theoretically purer, but creates a compliance gap. In enterprise contexts, the Sequencer operator is the institution itself, and regulators expect a compliance control point with full visibility. Our Sequencer-as-Compliance-Officer pattern is a deliberate architectural choice.
- 2PC commit protocol for all transactions. Canton's three-phase PREPARE→CONFIRM→FINALIZE adds latency rounds to every transaction. We use this selectively (cross-Zone DvP in Phase 2) rather than universally.

#### Prividium's Validium + RBAC: Lessons Learned

Prividium takes the opposite approach to Canton: instead of granular privacy at the protocol level, it achieves privacy through infrastructure isolation (Validium DA) and access control (Proxy RPC + RBAC). Its ZK proof infrastructure (Airbender: <1s block proof, <$0.0001/tx) is the most advanced in production.

**What we adopt from Prividium:**
- "Default Forbidden" RBAC policy: all contract functions inaccessible after deployment until admin explicitly grants access
- Four-layer defense-in-depth (extended to five layers in our design)
- ZK sanctions screening: cryptographically unforgeable compliance proofs with zero PII exposure
- Merkle proof export for per-transaction auditability
- Airbender-class prover as target for Phase 3 (sub-second proof, CUDA GPU acceleration)

**What we improve over Prividium:**
- Add intra-Zone privacy options (Prividium has Zone-internal full visibility — all full nodes see everything)
- Add sub-transaction granularity for RWA use cases (Prividium operates at chain-level privacy only)
- Add threshold key management (Prividium uses single-operator model exclusively)
- Add structured regulatory escalation (Prividium's five disclosure mechanisms are ad hoc; our four-level escalation is systematic)

**What we deliberately reject from Prividium:**
- Single-operator-only model. While simpler, it concentrates all trust in one entity. Our threshold ECIES and governance-gated operations distribute trust without adding DAC complexity.
- Multicall blocking. Prividium blocks `multicall` to prevent RBAC bypass, but this limits composability. Our approach uses policy-aware execution at the precompile level, which handles complex calls natively.

#### Tempo Zones: The Closest Reference Architecture

Tempo is the most directly translatable reference because it shares the same L1/L2 architecture pattern. Our design can be understood as "Tempo Zones extended with configurable per-Zone privacy models."

**What we adopt directly from Tempo:**
- Zone architecture: NoopConsensus, 1:1 block mapping, L1-event-driven block production
- ECIES encrypted deposits: full mechanism including Chaum-Pedersen verification
- Authenticated RPC: signed token format, per-account filtering, sanitized blocks
- TIP-403 policy sync: L1→Zone auto-mirror via TempoStateReader + SharedPolicyCache
- ZonePortal bridge: deposit/depositEncrypted/submitBatch/processWithdrawal
- Side-channel mitigations: fixed gas, 100ms response floor, CREATE/CREATE2 blocking

**What we extend beyond Tempo:**
- Per-Zone privacy model selection (Tempo uses Zone-internal transparent for all Zones)
- Threshold ECIES (Tempo uses single sequencer key)
- Timelock encryption for MEV protection
- Sub-transaction privacy (Option B) for RWA
- ZK order matching (Option C) for xstocks
- Comprehensive data sovereignty framework
- Structured audit escalation

### 6.3 Key Architectural Differentiators

**Differentiator 1 — Per-Zone Privacy Model Selection:**
No existing system offers configurable privacy models per Zone. Tempo uses Zone-internal transparent for all Zones. Canton uses sub-transaction privacy for all participants. Prividium uses Validium + RBAC for all transactions. This design allows each Zone to select the privacy model that best fits its narrative requirements (Section 2.1).

**Differentiator 2 — Sequencer-as-Compliance-Officer:**
This design explicitly embraces the Sequencer's visibility as a feature rather than a bug. By positioning the Sequencer as the compliance enforcement point, we eliminate the need for separate compliance infrastructure while maintaining privacy from external observers. Canton's approach of Sequencer blindness is theoretically purer but creates compliance challenges (regulators must be embedded as real-time Observers).

**Differentiator 3 — Phased Trust Model Migration:**
The architecture is designed for progressive trust reduction:
- Phase 1: Sequencer trust only (simple, fast deployment)
- Phase 2: Compliance proofs + selective disclosure (partial cryptographic trust)
- Phase 3: Full state transition proofs (mathematical trust for correctness)

Each phase independently provides meaningful security guarantees. This is more pragmatic than Canton (which requires the full privacy model from day one) or Prividium (which already has full STARK proofs but limited privacy granularity).

**Differentiator 4 — Integrated Data Sovereignty Framework:**
No existing system provides a comprehensive data sovereignty framework that addresses GDPR erasure, cross-border data localization, audit escalation, and regulatory conflict resolution. This design treats data sovereignty as a first-class architectural concern, not an afterthought.

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Months 1-6)

| Component | Specification | Priority |
|-----------|--------------|----------|
| Zone infrastructure | NoopConsensus, 1:1 block mapping, ZonePortal bridge contracts | P0 |
| ECIES encrypted deposits | Standard (single-key) ECIES per Tempo reference | P0 |
| Authenticated RPC | Signed token auth, per-account filtering, sanitized blocks | P0 |
| TIP-403 policy sync | PolicyRegistry L1→Zone auto-mirror | P0 |
| Payment Zone (Option A) | Zone-internal transparent, >10,000 TPS target | P0 |
| Five-layer access control | IAM + Auth RPC + Sequencer policy + Precompile registry + L1 bridge filter | P1 |
| Side-channel mitigations | Fixed gas, 100ms response floor, CREATE/CREATE2 blocking | P1 |
| Basic cross-Zone transfer | Two-step bridge (non-atomic) | P1 |
| Zone lifecycle management | Create, configure, basic upgrade | P1 |

### Phase 2: Enhanced Privacy (Months 7-12)

| Component | Specification | Priority |
|-----------|--------------|----------|
| RWA Zone (Option B) | Sub-transaction privacy via PATE (Privacy-Aware Transaction Executor) | P0 |
| Selective disclosure proofs | SelectiveDisclosure precompile (0x0405, 8,000 gas) | P0 |
| Compliance proofs | ZK compliance reports, PII-free sanctions screening | P0 |
| Balance proofs | Solvency proof (Zone assets = mainchain locked) | P1 |
| Threshold ECIES | t-of-n key management for RWA and xstocks Zones | P1 |
| HTLC cross-Zone | Conditional atomic cross-Zone transfers | P1 |
| Audit framework | Routine reports + scoped sandbox + threshold decryption | P1 |
| Data sovereignty | GDPR export API, field-level encryption, retention policies | P1 |
| Travel Rule engine | Automated compliance for Payment Zone (≥$3,000 threshold) | P1 |

### Phase 3: Advanced (Months 13-18)

| Component | Specification | Priority |
|-----------|--------------|----------|
| xstocks Zone (Option C) | ZK order matching engine, post-trade proofs | P0 |
| State transition proofs | Full SP1/RISC-V STARK proofs for Zone state transitions | P0 |
| ZK cross-Zone proofs | Atomic cross-Zone transfers with privacy preservation | P1 |
| Timelock encryption | MEV protection for RWA and xstocks Zones | P1 |
| 2PC evaluation | Canton-style Global Synchronizer for DvP atomicity | P2 |
| FHE/MPC exploration | Encrypted execution (eliminates Sequencer trust for data) | P2 |
| Cross-border data localization | Geographic node constraints, cross-border compliance gates | P2 |

---

## 8. Appendix: Threat Model & Attack Surfaces

### 8.1 Adversary Classes

| Adversary | Capability | Goal | Primary Defense |
|-----------|-----------|------|----------------|
| **External observer** | Can monitor mainchain transactions, ZonePortal events | Learn Zone participant identities, transaction amounts | ECIES encrypted deposits, Validium DA, sanitized RPC |
| **Curious Zone participant** | Has Zone RPC access, sees own transactions | Learn other participants' transactions, positions, strategies | Sub-tx privacy (Option B), ZK-enhanced (Option C), RPC filtering |
| **Malicious Sequencer** | Full visibility into Zone plaintext, controls block production | Front-run transactions, censor participants, forge state | Timelock encryption (MEV), governance oversight (censorship), validity proofs (forgery) |
| **Compromised operator** | Access to Zone DA backend, encryption keys | Exfiltrate all Zone data | Threshold ECIES (no single key), audit trails, governance slashing |
| **State-level adversary** | Legal authority to compel data access, nation-state capabilities | Mass surveillance, political targeting | Threshold decryption (multi-jurisdiction), data localization, legal basis verification |

### 8.2 Known Limitations & Accepted Tradeoffs

| Limitation | Accepted Because | Mitigation Path |
|-----------|-----------------|----------------|
| Sequencer sees all Zone plaintext (Phase 1-2) | Enables compliance; enterprise adversary model trusts the operator | Phase 3: FHE/MPC encrypted execution |
| Cross-Zone transfers have privacy gap on mainchain | Two-step bridge is simple and well-understood | Phase 3: ZK cross-Zone proofs |
| Metadata leakage (message sizes, timing, participant counts) | Acceptable in enterprise context (Canton makes same tradeoff) | Traffic padding, batching, timing jitter |
| Non-atomic cross-Zone transfers (Phase 1) | Simplicity; atomic alternatives add significant complexity | Phase 2: HTLC; Phase 3: ZK proofs or 2PC |
| EVM sub-transaction privacy requires explicit annotations | Retains Solidity toolchain compatibility (vs. Canton's Daml) | Privacy SDK tooling to reduce annotation burden |
| Single-operator Validium concentrates trust | Operator = institution itself; DAC adds unwanted data distribution | Validity proofs (Phase 3) reduce trust to correctness-only |

### 8.3 Security Invariants

The following invariants MUST hold at all times:

1. **Asset conservation:** Sum of all Zone-internal balances = sum of all mainchain-locked amounts (verified by balance proofs in Phase 2+)
2. **Compliance completeness:** No transaction executes without passing TIP-403 policy check (enforced at Sequencer mempool level)
3. **Audit trail integrity:** All regulatory access events are recorded in an append-only, tamper-evident log (Merkle chain)
4. **Key isolation:** Zone encryption keys are never exposed outside the Zone's security boundary (threshold ceremony for rotation)
5. **Privacy monotonicity:** A Zone's privacy tier can only be upgraded (strengthened), never downgraded, without governance supermajority approval

---

*End of WHI-359 Privacy Layer & Data Sovereignty Architecture Design*
