# WHI-361: Business Component Layer Design — RWA / xStocks / Payment Native Adaptation

> **Issue**: [WHI-361](https://linear.app/whisker-personal/issue/WHI-361)
> **Milestone**: M4 — Narrative-Driven Analysis & Clean-Sheet Enterprise Design
> **Dependencies**: WHI-355 (Narrative Analysis), WHI-357 (Architecture Blueprint), WHI-358 (Execution+Consensus), WHI-359 (Privacy+Data Sovereignty), WHI-360 (Compliance+Identity)
> **Date**: 2026-05-07

---

## Table of Contents

1. [Design Philosophy & Positioning](#1-design-philosophy--positioning)
2. [RWA Tokenization Infrastructure](#2-rwa-tokenization-infrastructure)
3. [xStocks Tokenized Equities Trading Framework](#3-xstocks-tokenized-equities-trading-framework)
4. [Payment Network Components](#4-payment-network-components)
5. [Cross-Narrative Shared Components](#5-cross-narrative-shared-components)
6. [SDK & Developer Tools](#6-sdk--developer-tools)
7. [Interface Definitions: Components ↔ Infrastructure Layers](#7-interface-definitions-components--infrastructure-layers)
8. [Comparison with Existing Approaches](#8-comparison-with-existing-approaches)

---

## 1. Design Philosophy & Positioning

### 1.1 Architectural Position

The Business Component Layer sits at the boundary between blockchain infrastructure and business applications — **Layer 2 of 7** in the stack architecture defined in WHI-357:

```
┌─────────────────────────────────────────────────────────────────┐
│  Business Application Layer   (DApps — standard EVM CALL/STATICCALL) │
├─────────────────────────────────────────────────────────────────┤
│  ★ BUSINESS COMPONENT LAYER  (this document)                          │
│    - Pre-deployed contracts  (upgradeable via upgrade-tx pattern)      │
│    - Business precompiles    (at 0x20C0… prefix, 0x0104–0x0105)       │
├─────────────────────────────────────────────────────────────────┤
│  Compliance + Identity Layer (0x0401–0x0405 precompiles, WHI-360)     │
├─────────────────────────────────────────────────────────────────┤
│  Privacy Layer               (Zone architecture, WHI-359)             │
├─────────────────────────────────────────────────────────────────┤
│  Execution Layer             (Reth SDK + revm, WHI-358)               │
├─────────────────────────────────────────────────────────────────┤
│  Consensus Layer             (Simplex BFT, ~600ms finality)           │
├─────────────────────────────────────────────────────────────────┤
│  DA + Settlement Layer       (Hybrid DA + Ethereum L1 ZK anchor)      │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Core Design Principles

**Principle 1 — Compliance by Default, Not by Add-On.** Every token transfer auto-invokes the PolicyRegistry (`0x0403`). Application developers cannot accidentally ship non-compliant transfers. This follows the Tempo TIP-403 enforcement model where compliance is baked into the token primitive itself at the protocol level — not an optional application-layer hook.

**Principle 2 — Developer Simplicity over Infrastructure Complexity.** DApp developers call high-level SDK methods (`sdk.rwa.createAsset(...)`, `sdk.payment.send(...)`). The SDK handles compliance proof generation, Zone routing, Travel Rule attachment, and privacy encryption transparently. Developers never interact with precompiles directly.

**Principle 3 — Modular Pick-and-Choose.** Enterprises adopt only the components they need. An RWA issuer deploys the Compliance Token + Asset Lifecycle Engine. A payment processor deploys Payment Lane + Travel Rule Engine. Components are independent but interoperable.

**Principle 4 — Infrastructure Layer Reuse.** Business components never re-implement privacy, compliance, or identity. They compose lower-layer primitives:
- Privacy → Zone architecture from WHI-359
- Compliance → PolicyRegistry (`0x0403`) + ComplianceCheck (`0x0402`) from WHI-360
- Identity → IdentityRegistry (`0x0401`) from WHI-360
- Finality → `IFinalityOracle` from WHI-358

### 1.3 Narrative-Specific Performance Profiles

| Narrative | TPS | Latency | Privacy Tier | Compliance Focus |
|-----------|-----|---------|-------------|------------------|
| **RWA** | 100–500 | Seconds OK | T3 (sub-transaction) | Investor suitability, securities regulation |
| **xStocks** | 1,000–5,000 peak | <100ms (HFT) | T3 (sub-transaction) | Market regulation (Reg NMS/SHO), surveillance |
| **Payment** | >10,000 | <500ms (B2C <2s) | T1 (DA-level) | AML/CFT, Travel Rule, VASP |

---

## 2. RWA Tokenization Infrastructure

### 2.1 Compliance Token Standard (MIP-20)

The Mantle Improvement Proposal 20 (MIP-20) defines the compliance-enhanced token standard for RWA. It extends ERC-20 with mandatory compliance hooks, asset lifecycle functions, and corporate action capabilities. The design draws from Tempo TIP-20's native precompile approach and Canton's signatory/observer authorization model.

#### 2.1.1 Core Interface

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IMantleComplianceToken (MIP-20)
 * @notice Compliance-enhanced ERC-20 for regulated assets.
 *         Every transfer() auto-invokes PolicyRegistry (0x0403) — no opt-out.
 *         Deployed at addresses with 0x20C0 prefix for Payment Lane routing eligibility.
 */
interface IMantleComplianceToken {
    // ═══════════════════════════════════════════════════════
    // ERC-20 Standard Interface (preserved for compatibility)
    // ═══════════════════════════════════════════════════════
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function decimals() external view returns (uint8);
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);

    // ═══════════════════════════════════════════════════════
    // Compliance-Enhanced Transfer
    // ═══════════════════════════════════════════════════════
    
    /**
     * @notice Transfer with explicit compliance proof attachment.
     * @dev    Standard transfer() also enforces compliance via auto-hook,
     *         but this variant allows pre-generated ZK proofs for cross-Zone transfers.
     * @param to           Recipient address
     * @param amount       Transfer amount
     * @param proofType    0=none (auto-check), 1=ZK sanction screening, 2=attestation signature
     * @param proofData    Encoded compliance proof (ZK proof bytes or issuer signature)
     */
    function transferWithCompliance(
        address to,
        uint256 amount,
        uint8 proofType,
        bytes calldata proofData
    ) external returns (bool);

    // ═══════════════════════════════════════════════════════
    // Compliance Query Interface
    // ═══════════════════════════════════════════════════════
    
    /**
     * @notice Pre-check whether a transfer would pass compliance.
     * @return compliant  True if the transfer would succeed
     * @return reasonCode Explanation if non-compliant (e.g., KYC_INSUFFICIENT, SANCTION_HIT)
     */
    function isCompliant(
        address from,
        address to,
        uint256 amount
    ) external view returns (bool compliant, bytes32 reasonCode);
    
    /**
     * @notice Get the compliance policy ID governing this token.
     */
    function compliancePolicyId() external view returns (bytes32);

    // ═══════════════════════════════════════════════════════
    // Asset Lifecycle — Regulatory Actions
    // ═══════════════════════════════════════════════════════
    
    /**
     * @notice Freeze an account (regulatory hold). Only callable by REGULATOR_ROLE.
     * @dev    Frozen accounts cannot send or receive. Emits AccountFrozen event.
     */
    function freeze(address account) external;
    
    /**
     * @notice Unfreeze a previously frozen account.
     */
    function unfreeze(address account) external;
    
    /**
     * @notice Judicial seizure — forcibly transfer assets to a designated address.
     * @dev    Only callable by REGULATOR_ROLE with court order reference.
     */
    function seize(address from, address to, uint256 amount, bytes32 courtOrderRef) external;
    
    /**
     * @notice Clawback — recover tokens (e.g., erroneous issuance, fraud).
     * @dev    Only callable by ISSUER_ROLE with documented reason.
     */
    function clawback(address from, uint256 amount, bytes32 reason) external;

    // ═══════════════════════════════════════════════════════
    // Corporate Actions
    // ═══════════════════════════════════════════════════════
    
    /**
     * @notice Declare a dividend distribution. Creates claimable entitlements
     *         for all holders as of the snapshot block.
     * @param paymentToken  Address of the payment token (e.g., USDC)
     * @param amountPerUnit Dividend per unit of this token
     * @param snapshotId    Block number for the record date
     */
    function declareDividend(
        address paymentToken,
        uint256 amountPerUnit,
        uint256 snapshotId
    ) external returns (uint256 dividendId);
    
    /**
     * @notice Claim a declared dividend.
     */
    function claimDividend(uint256 dividendId) external;
    
    /**
     * @notice Take a snapshot of all holder balances (for record date).
     * @return snapshotId  The snapshot identifier (block number)
     */
    function snapshot() external returns (uint256 snapshotId);
    
    /**
     * @notice Query balance at a historical snapshot.
     */
    function balanceOfAt(address account, uint256 snapshotId) external view returns (uint256);

    // ═══════════════════════════════════════════════════════
    // Asset Metadata
    // ═══════════════════════════════════════════════════════
    
    /**
     * @notice Returns the asset class (REIT, bond, equity, fund, carbon_credit, etc.)
     */
    function assetClass() external view returns (bytes32);
    
    /**
     * @notice Returns the issuer's identity (DID or address)
     */
    function issuer() external view returns (address);
    
    /**
     * @notice Returns the applicable jurisdiction(s) as ISO 3166-1 numeric codes.
     */
    function jurisdictions() external view returns (uint16[] memory);

    // ═══════════════════════════════════════════════════════
    // Role Management (Observer Model from Canton)
    // ═══════════════════════════════════════════════════════
    
    /**
     * @notice Role constants following Canton's signatory/observer/controller model.
     */
    function ISSUER_ROLE() external pure returns (bytes32);
    function REGULATOR_ROLE() external pure returns (bytes32);     // Observer — sees all events
    function TRANSFER_AGENT_ROLE() external pure returns (bytes32); // Controller — manages cap table
    function CUSTODIAN_ROLE() external pure returns (bytes32);

    // ═══════════════════════════════════════════════════════
    // Events
    // ═══════════════════════════════════════════════════════
    event ComplianceTransfer(address indexed from, address indexed to, uint256 amount, bytes32 policyId);
    event AccountFrozen(address indexed account, address indexed regulator);
    event AccountUnfrozen(address indexed account, address indexed regulator);
    event AssetSeized(address indexed from, address indexed to, uint256 amount, bytes32 courtOrderRef);
    event Clawback(address indexed from, uint256 amount, bytes32 reason);
    event DividendDeclared(uint256 indexed dividendId, address paymentToken, uint256 amountPerUnit);
    event DividendClaimed(uint256 indexed dividendId, address indexed holder, uint256 amount);
    event SnapshotCreated(uint256 indexed snapshotId);
}
```

#### 2.1.2 Transfer Compliance Enforcement Flow

The critical property of MIP-20 is that compliance enforcement is inviolable — it happens at two layers simultaneously:

```
Application calls transfer(to, amount)
    │
    ├─[Layer 3: Sequencer Pre-EVM]──────────────────────────────────┐
    │   Sequencer's prepare_l1_block() evaluates TIP-403 policy     │
    │   NON-COMPLIANT → tx excluded from block (bounce-back)        │
    │   COMPLIANT → proceed to EVM execution                        │
    └───────────────────────────────────────────────────────────────┘
    │
    ├─[Layer 4: Precompile]─────────────────────────────────────────┐
    │   MIP-20 transfer() implementation:                           │
    │   1. STATICCALL 0x0403 PolicyRegistry.isAuthorized(           │
    │        from, to, amount, abi.encode(token, assetClass))       │
    │   2. if !authorized → revert ComplianceRejected(reasonCode)   │
    │   3. if authorized → execute ERC-20 balance update            │
    │   4. emit ComplianceTransfer(from, to, amount, policyId)      │
    └───────────────────────────────────────────────────────────────┘
```

**Compound policy evaluation** (adopted from Tempo TIP-403 + TIP-1015):
- **Sender-side rules**: KYC level check, sanctions screening, lockup period, daily transfer limit
- **Recipient-side rules**: Investor suitability (accredited investor), jurisdiction whitelist, holder count limit
- Both sides must pass for the transfer to succeed. A token can have different policies for senders vs. receivers.

**Gas model**: Compliance check gas is **fixed at 5,000 gas** (ComplianceCheck precompile) regardless of policy complexity. This prevents gas-based side-channel attacks that could reveal compliance status. In RWA/xStocks Zones, compliance precompile gas is sponsored by the Zone Sequencer — zero friction for compliance calls.

### 2.2 Asset Lifecycle Engine

The Asset Lifecycle Engine manages RWA tokens from creation through redemption. It is a pre-deployed contract system that orchestrates the compliance token, identity registry, and policy registry.

#### 2.2.1 Lifecycle State Machine

```
              registerAsset()         issue()               list()
    ┌──────┐ ─────────────> ┌──────┐ ──────────> ┌──────┐ ──────────> ┌─────────┐
    │ DRAFT│                │ISSUED│              │ACTIVE│             │ TRADING │
    └──────┘                └──────┘              └──────┘             └─────────┘
        │                                            │                     │
        │ reject()                 distributeDividend()│    freeze()        │ mature() /
        v                          processSplit()      │    │               │ redeem()
    ┌──────────┐               ┌────────────────┐     │    v               v
    │ REJECTED │               │CORPORATE_ACTION│<────┘ ┌────────┐   ┌──────────┐
    └──────────┘               └────────────────┘       │ FROZEN │   │ MATURING │
                                    │                   └────────┘   └──────────┘
                                    │ complete()            │              │
                                    v                       │ unfreeze()   │ settle()
                               ┌─────────┐                 │              v
                               │ TRADING │<─────────────────┘        ┌──────────┐
                               └─────────┘                           │ REDEEMED │
                                                                     └──────────┘
```

#### 2.2.2 Lifecycle Engine Interface

```solidity
interface IAssetLifecycleEngine {
    // ═══════════ Asset Registration (DRAFT → ISSUED) ═══════════
    
    /**
     * @notice Register a new RWA asset. Creates token contract + compliance policy.
     * @param config Asset configuration including class, jurisdiction, and compliance rules.
     * @return assetId   Unique asset identifier
     * @return token     Deployed MIP-20 token address (0x20C0… prefix)
     * @return policyId  Compliance policy ID registered in PolicyRegistry
     */
    function registerAsset(AssetConfig calldata config)
        external returns (bytes32 assetId, address token, bytes32 policyId);
    
    struct AssetConfig {
        string name;
        string symbol;
        bytes32 assetClass;         // REIT, BOND, EQUITY, FUND, CARBON_CREDIT
        uint256 totalSupply;
        uint16[] jurisdictions;     // ISO 3166-1 numeric
        bytes32[] regulations;      // REG_D, REG_S, MICA, MAS
        InvestorRequirements requirements;
        CustodianConfig custodian;
        uint256 lockupPeriod;       // seconds (0 = no lockup)
        uint256 maturityDate;       // unix timestamp (0 = perpetual)
    }
    
    struct InvestorRequirements {
        uint8 minKYCLevel;          // 0–4 (per WHI-360 levels)
        uint32 requiredCertifications; // bitmap: accredited, qualified_purchaser, etc.
        uint16[] allowedJurisdictions;
        uint256 minInvestmentAmount;
        uint256 maxHolderCount;     // 0 = unlimited
    }
    
    struct CustodianConfig {
        address custodianAddress;
        bytes32 custodianDID;       // did:whisker:<network>:<addr>
        string custodyAgreementURI;
    }

    // ═══════════ Primary Market (ISSUED → ACTIVE) ═══════════
    
    /**
     * @notice Issue tokens to investors in primary market allocation.
     * @dev    Each investor's qualification is verified via IdentityRegistry (0x0401)
     *         before allocation. Uses Propose-Accept pattern for bilateral consent.
     */
    function issue(
        bytes32 assetId,
        address[] calldata investors,
        uint256[] calldata amounts
    ) external returns (uint256 issuanceId);
    
    /**
     * @notice Investor accepts their allocation (Propose-Accept pattern from Canton).
     * @dev    Tokens are minted only after investor acceptance.
     */
    function acceptAllocation(uint256 issuanceId) external;

    // ═══════════ Corporate Actions ═══════════
    
    /**
     * @notice Distribute dividends to all holders at a snapshot.
     * @dev    Non-consuming: doesn't modify token balances, creates claimable entitlements.
     *         Follows Canton's nonconsuming-choice pattern.
     */
    function distributeDividend(
        bytes32 assetId,
        address paymentToken,
        uint256 amountPerUnit,
        uint256 recordDateBlock
    ) external returns (uint256 dividendId);
    
    /**
     * @notice Process a stock split / reverse split.
     * @param splitNumerator   e.g., 3 for a 3:1 split
     * @param splitDenominator e.g., 1 for a 3:1 split
     */
    function processSplit(
        bytes32 assetId,
        uint256 splitNumerator,
        uint256 splitDenominator
    ) external;

    // ═══════════ Redemption / Maturity ═══════════
    
    /**
     * @notice Initiate asset maturity process (for bonds, term funds).
     */
    function initiateMature(bytes32 assetId) external;
    
    /**
     * @notice Redeem tokens for underlying value.
     * @param amount    Number of tokens to redeem
     * @param currency  Payment currency for redemption proceeds
     */
    function redeem(
        bytes32 assetId,
        uint256 amount,
        address currency
    ) external returns (uint256 redemptionId);

    // ═══════════ Cross-Zone Transfer ═══════════
    
    /**
     * @notice Transfer asset tokens from one Zone to another.
     * @dev    Routes through mainchain: Zone A → ZonePortal → mainchain → ZonePortal → Zone B
     *         Compliance context (assetClass, issuer, regulations) preserved across zones.
     */
    function crossZoneTransfer(
        bytes32 assetId,
        uint256 amount,
        uint256 destinationZoneId,
        bytes calldata complianceProof
    ) external;

    // ═══════════ Events ═══════════
    event AssetRegistered(bytes32 indexed assetId, address indexed token, bytes32 assetClass);
    event IssuanceCreated(uint256 indexed issuanceId, bytes32 indexed assetId, uint256 totalAmount);
    event AllocationAccepted(uint256 indexed issuanceId, address indexed investor, uint256 amount);
    event SplitProcessed(bytes32 indexed assetId, uint256 numerator, uint256 denominator);
    event MaturityInitiated(bytes32 indexed assetId, uint256 maturityDate);
    event RedemptionRequested(uint256 indexed redemptionId, bytes32 indexed assetId, uint256 amount);
}
```

#### 2.2.3 Per-Stage Roles and Compliance Matrix

| Stage | Participants | Required Roles | Compliance Checks |
|-------|-------------|---------------|-------------------|
| **Registration** | Issuer, Legal Counsel, Custodian | ISSUER_ROLE (signatory), CUSTODIAN_ROLE | Asset verification, legal opinion, custody proof |
| **Issuance** | Issuer, Underwriter, Investors | ISSUER_ROLE, TRANSFER_AGENT_ROLE | Investor suitability (`isVerified` + `getComplianceAttributes`), subscription limits, Reg D/S/A+ check |
| **Trading** | Buyers, Sellers, Market Makers | Any verified participant | Pre-trade compliance (auto via PolicyRegistry), DVP settlement |
| **Corporate Actions** | Issuer, Transfer Agent | ISSUER_ROLE, TRANSFER_AGENT_ROLE | Record date snapshot, tax withholding jurisdiction check |
| **Redemption/Maturity** | Issuer, Investors, Custodian | ISSUER_ROLE, CUSTODIAN_ROLE | Liquidation compliance, capital gains jurisdiction |

### 2.3 DVP (Delivery vs Payment) Settlement Engine

The DVP Engine is the most architecturally significant business component. It must achieve atomic settlement across multiple asset legs while preserving sub-transaction privacy — each counterparty sees only their relevant portions.

#### 2.3.1 Design Reference: Canton Sub-Transaction Atomicity

Canton's DVP transaction tree is the gold standard. In a typical securities DVP:

```
TX: Alice buys 100 shares from Bob, paying $100K via Bank IOU

Full transaction tree:
├── Leg 1 (Payment): Alice → Bob via Bank
│   ├── Archive: IOU(Alice, Bank, $100K)
│   └── Create:  IOU(Bob, Bank, $100K)
└── Leg 2 (Delivery): Bob → Alice via Registrar
    ├── Archive: Share(Bob, Registrar, 100 units)
    └── Create:  Share(Alice, Registrar, 100 units)

Privacy projection:
  Alice:     sees full TX (counterparty)
  Bob:       sees full TX (counterparty)
  Bank:      sees Leg 1 only (IOU movement)
  Registrar: sees Leg 2 only (share movement)
```

Our EVM-compatible implementation achieves equivalent privacy guarantees using Zone isolation + cross-Zone atomic settlement.

#### 2.3.2 Three-Tier DVP Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DVP Settlement Engine                         │
├──────────────────┬──────────────────────┬───────────────────────────────┤
│   Intra-Zone DVP │   Cross-Zone DVP     │   Cross-Chain DVP            │
│   (simplest)     │   (primary use case) │   (bridge-mediated)          │
├──────────────────┼──────────────────────┼───────────────────────────────┤
│ Single atomic TX │ Coordinator contract │ Intermediary escrow +        │
│ within one Zone  │ on mainchain         │ external settlement bridge   │
│                  │                      │                              │
│ Finality: BFT    │ Finality: ZK_PROVEN  │ Finality: L1_ANCHORED       │
│ (~600ms)         │ (5–30 min)           │ (~12+ min)                   │
│                  │                      │                              │
│ Privacy: Zone-   │ Privacy: each Zone   │ Privacy: mainchain data      │
│ internal only    │ sees only its leg    │ visible to bridge operator   │
└──────────────────┴──────────────────────┴───────────────────────────────┘
```

#### 2.3.3 Cross-Zone DVP Protocol (Propose-Accept Model)

The Cross-Zone DVP is the primary enterprise use case: RWA Zone assets settled against Payment Zone stablecoins.

```solidity
interface IDVPEngine {
    enum DVPState { PROPOSED, ACCEPTED, SETTLING, COMPLETED, FAILED, EXPIRED }
    enum DVPType { INTRA_ZONE, CROSS_ZONE, CROSS_CHAIN }
    
    struct DVPLeg {
        address token;          // MIP-20 token address
        uint256 amount;
        uint256 zoneId;         // Zone where this leg executes
        address counterparty;   // Who delivers this leg
    }
    
    struct DVPProposal {
        DVPLeg deliveryLeg;     // Securities delivery
        DVPLeg paymentLeg;      // Cash payment
        uint256 settlementDeadline;
        FinalityLevel requiredFinality; // BFT_CONFIRMED | ZK_PROVEN | L1_ANCHORED
    }

    /**
     * @notice Propose a DVP settlement (Step 1 of Propose-Accept).
     * @dev    Locks proposer's leg in escrow. Counterparty must accept within deadline.
     *         Follows Canton's bilateral consent model.
     */
    function proposeDVP(DVPProposal calldata proposal)
        external returns (uint256 dvpId);
    
    /**
     * @notice Accept a DVP proposal (Step 2 of Propose-Accept).
     * @dev    Locks acceptor's leg in escrow. Both legs are now locked.
     *         Settlement proceeds automatically once both are confirmed.
     */
    function acceptDVP(uint256 dvpId) external;
    
    /**
     * @notice Query DVP settlement status.
     */
    function getDVPStatus(uint256 dvpId)
        external view returns (DVPState state, DVPSettlementDetails memory details);
    
    struct DVPSettlementDetails {
        bool deliveryLegConfirmed;
        bool paymentLegConfirmed;
        FinalityLevel currentFinality;
        uint256 settledAtBlock;
        bytes32 settlementProof;    // ZK proof of atomic execution
    }

    /**
     * @notice Cancel a proposed DVP (only before acceptance).
     */
    function cancelDVP(uint256 dvpId) external;

    // ═══════════ Events ═══════════
    event DVPProposed(uint256 indexed dvpId, address indexed proposer, DVPType dvpType);
    event DVPAccepted(uint256 indexed dvpId, address indexed acceptor);
    event DVPSettled(uint256 indexed dvpId, bytes32 settlementProof);
    event DVPFailed(uint256 indexed dvpId, bytes32 reason);
    event DVPExpired(uint256 indexed dvpId);
}
```

#### 2.3.4 Cross-Zone DVP Execution Flow

```
Phase 1: Proposal & Escrow
  1. Seller calls proposeDVP() → locks shares in RWA Zone escrow
  2. DVPCoordinator (mainchain contract) records proposal

Phase 2: Acceptance & Counter-Escrow
  3. Buyer calls acceptDVP() → locks payment in Payment Zone escrow
  4. DVPCoordinator records both legs locked

Phase 3: Atomic Settlement
  5. DVPCoordinator initiates simultaneous release:
     a. CrossZoneMessage to RWA Zone: "release shares to buyer"
     b. CrossZoneMessage to Payment Zone: "release payment to seller"
  6. Each Zone Sequencer processes its leg atomically
  7. Each Zone submits settlement confirmation to mainchain

Phase 4: Finality Confirmation
  8. DVPCoordinator requires BOTH confirmations within deadline
  9. If both confirmed → DVP status = COMPLETED
  10. If either fails or times out:
      a. Revert both legs (escrow refunds)
      b. DVP status = FAILED; emit DVPFailed with reason

Finality upgrade path:
  - BFT_CONFIRMED (~600ms): immediate trading confirmation
  - ZK_PROVEN (5–30 min): for large-value or regulated DVP
  - L1_ANCHORED (~12+ min): for cross-chain DVP bridge finality
```

#### 2.3.5 Atomicity Guarantee

The DVP Engine achieves atomicity through **coordinator-mediated two-phase commit**, adapted from Canton's Mediator pattern:

| Property | Guarantee | Mechanism |
|----------|-----------|-----------|
| **Atomic execution** | Both legs settle or neither settles | Mainchain Coordinator holds escrow; simultaneous release |
| **No double-spend** | Escrowed assets cannot be used elsewhere | Escrow lock at Zone level; `frozen` flag on escrowed tokens |
| **Timeout safety** | No indefinite lock-up of assets | Configurable deadline; auto-revert on expiry |
| **Privacy** | Each Zone sees only its leg | Cross-Zone messages carry only the relevant leg's details |
| **Compliance** | Both legs pass compliance | Each Zone's PolicyRegistry independently validates its leg |

---

## 3. xStocks Tokenized Equities Trading Framework

### 3.1 Tokenized Stock Standard (MIP-21 — extends MIP-20)

MIP-21 extends the compliance token with equity-specific features: corporate action processing, trading rules enforcement, and market surveillance hooks.

```solidity
interface ITokenizedStock is IMantleComplianceToken {
    // ═══════════ Equity-Specific Metadata ═══════════
    
    /**
     * @notice Returns the ISIN (International Securities Identification Number).
     */
    function isin() external view returns (bytes12);
    
    /**
     * @notice Returns the CUSIP (for US-traded securities).
     */
    function cusip() external view returns (bytes9);
    
    /**
     * @notice Returns the underlying stock exchange and ticker.
     */
    function underlyingTicker() external view returns (string memory exchange, string memory ticker);
    
    /**
     * @notice Returns the custodian holding the physical underlying shares.
     */
    function physicalCustodian() external view returns (address);

    // ═══════════ Corporate Actions (Equity-Specific) ═══════════
    
    /**
     * @notice Process a stock split. Adjusts all holder balances proportionally.
     * @dev    Only callable by ISSUER_ROLE or TRANSFER_AGENT_ROLE.
     *         Implements Canton's nonconsuming-choice pattern: existing positions
     *         are adjusted in-place; holders are notified via events.
     */
    function processSplit(uint256 numerator, uint256 denominator) external;
    
    /**
     * @notice Process a reverse split with fractional share handling.
     * @param  cashInLieu  Payment token for fractional shares
     * @param  pricePerShare Cash-in-lieu price for fractions
     */
    function processReverseSplit(
        uint256 numerator,
        uint256 denominator,
        address cashInLieu,
        uint256 pricePerShare
    ) external;
    
    /**
     * @notice Distribute rights offering to existing shareholders.
     */
    function distributeRights(
        uint256 rightsPerShare,
        uint256 subscriptionPrice,
        address paymentToken,
        uint256 expiryTimestamp
    ) external returns (uint256 rightsOfferingId);
    
    /**
     * @notice Exercise subscription rights from a rights offering.
     */
    function exerciseRights(uint256 rightsOfferingId, uint256 amount) external;
    
    /**
     * @notice On-chain shareholder voting.
     * @param  proposalId   Governance proposal identifier
     * @param  voteChoice   0=abstain, 1=for, 2=against
     */
    function vote(uint256 proposalId, uint8 voteChoice) external;

    // ═══════════ Trading Rules Engine ═══════════
    
    /**
     * @notice Check whether a trade would comply with trading rules.
     * @return allowed    Whether the trade is permitted
     * @return ruleCode   Which rule would be violated (if any)
     */
    function checkTradingRules(
        address trader,
        bool isBuy,
        uint256 amount,
        uint256 price
    ) external view returns (bool allowed, bytes32 ruleCode);

    // ═══════════ Events ═══════════
    event StockSplit(uint256 numerator, uint256 denominator, uint256 recordBlock);
    event RightsOffering(uint256 indexed offeringId, uint256 rightsPerShare, uint256 subscriptionPrice);
    event ShareholderVote(uint256 indexed proposalId, address indexed voter, uint8 choice, uint256 weight);
    event TradingRuleViolation(address indexed trader, bytes32 ruleCode, uint256 amount, uint256 price);
}
```

### 3.2 Trading Rules Engine

The Trading Rules Engine enforces market-integrity regulations at the protocol level, preventing violations before they occur.

```solidity
interface ITradingRulesEngine {
    // ═══════════ Rule Types ═══════════
    enum RuleType {
        PRICE_LIMIT,        // Circuit breaker: max % deviation from reference price
        SHORT_SELL,         // Reg SHO: short-selling restrictions
        LARGE_TRADE_REPORT, // Block trade reporting threshold
        INSIDER_WINDOW,     // Insider trading prevention: blackout periods
        MARKET_HOURS,       // Extended hours trading restrictions
        POSITION_LIMIT      // Maximum position per address/entity
    }

    struct TradingRule {
        RuleType ruleType;
        bytes32 ruleId;
        bytes ruleParams;       // ABI-encoded parameters per rule type
        bool active;
    }

    /**
     * @notice Validate a proposed trade against all active rules.
     */
    function validateTrade(
        address stock,
        address trader,
        bool isBuy,
        uint256 quantity,
        uint256 price
    ) external view returns (bool valid, bytes32[] memory violations);

    /**
     * @notice Register or update a trading rule for a specific stock.
     * @dev    Only callable by EXCHANGE_OPERATOR_ROLE.
     */
    function setRule(address stock, TradingRule calldata rule) external;
    
    /**
     * @notice Report a large trade to the surveillance system.
     * @dev    Auto-triggered when trade exceeds reporting threshold.
     */
    function reportLargeTrade(
        address stock,
        address buyer,
        address seller,
        uint256 quantity,
        uint256 price
    ) external;

    /**
     * @notice Set insider trading blackout window.
     * @param  insiderAddresses  Addresses designated as insiders
     * @param  blackoutStart     Window start timestamp
     * @param  blackoutEnd       Window end timestamp
     */
    function setInsiderBlackout(
        address stock,
        address[] calldata insiderAddresses,
        uint256 blackoutStart,
        uint256 blackoutEnd
    ) external;
}
```

**Rule enforcement integration**: The Trading Rules Engine is invoked by the xStocks Zone Sequencer at Layer 3 (pre-EVM check) for every trade transaction. This means rule violations are caught before block inclusion — not after execution.

### 3.3 Trading Venue Design

#### 3.3.1 Architecture Decision: Hybrid Order Book

For tokenized equities, the order book model is superior to AMMs for price discovery. However, a fully on-chain order book is gas-intensive. The design uses a **hybrid model**: off-chain matching + on-chain settlement.

```
┌─────────────────────────────────────────────────────────────────┐
│                    xStocks Trading Venue                        │
├──────────────────┬──────────────────────┬───────────────────────┤
│   Lit Market     │   Dark Pool          │   Market Maker Desk   │
├──────────────────┼──────────────────────┼───────────────────────┤
│ Visible order    │ Hidden orders        │ RFQ-based quotes      │
│ book             │ within Zone          │                       │
│                  │                      │                       │
│ Off-chain match  │ Encrypted matching   │ Private pricing       │
│ + on-chain       │ engine (TEE-backed)  │ within Zone           │
│ settlement       │                      │                       │
│                  │                      │                       │
│ All participants │ Block trade only     │ Licensed market       │
│                  │ (>$200K threshold)   │ makers only           │
└──────────────────┴──────────────────────┴───────────────────────┘
```

#### 3.3.2 Lit Market (Primary Venue)

```solidity
interface IOrderBook {
    enum OrderType { LIMIT, MARKET, STOP_LIMIT, STOP_MARKET }
    enum Side { BUY, SELL }
    enum TimeInForce { GTC, IOC, FOK, GTD }

    struct Order {
        bytes32 orderId;
        address stock;
        Side side;
        OrderType orderType;
        uint256 quantity;
        uint256 price;          // 0 for market orders
        TimeInForce tif;
        uint256 expiryTimestamp; // for GTD orders
    }

    /**
     * @notice Submit an order. Compliance-checked at submission.
     * @dev    Order is sent to off-chain matching engine.
     *         On match, settlement executes on-chain via DVP.
     */
    function submitOrder(Order calldata order) external returns (bytes32 orderId);
    
    /**
     * @notice Cancel an open order.
     */
    function cancelOrder(bytes32 orderId) external;
    
    /**
     * @notice Settle a matched trade (called by matching engine).
     * @dev    Atomic DVP: shares ↔ payment in single transaction.
     *         Both buyer and seller must have passed compliance pre-check.
     */
    function settleTrade(
        bytes32 buyOrderId,
        bytes32 sellOrderId,
        uint256 matchedQuantity,
        uint256 matchedPrice,
        bytes calldata matchProof     // Matching engine attestation (TEE signature)
    ) external;

    event OrderSubmitted(bytes32 indexed orderId, address indexed trader, Side side, uint256 price, uint256 quantity);
    event OrderCancelled(bytes32 indexed orderId);
    event TradeSettled(bytes32 indexed buyOrderId, bytes32 indexed sellOrderId, uint256 price, uint256 quantity);
}
```

#### 3.3.3 Dark Pool Design

The dark pool operates within a dedicated xStocks Zone with T3 (sub-transaction) privacy. Only the matching engine — running inside a TEE (Trusted Execution Environment) — sees plaintext order data.

**Privacy guarantees**:
- Order price, quantity, and counterparty identity are encrypted
- Only the matching engine TEE decrypts orders for matching
- Post-match: only matched counterparties learn each other's identity
- Block trade threshold: only orders >$200K qualify (prevents retail gaming)
- Regulator Observer role has full visibility (via dedicated viewing key at L3 audit level)

**Market maker framework**:
- Registration: Market makers register via IdentityRegistry with `broker_licensed` certification (bit 3 in `ComplianceAttributes.certifications`)
- Obligations: Minimum bid-ask spread, minimum quote size, continuous quoting requirements (configurable per stock)
- Incentives: Reduced trading fees, priority order routing, rebate programs
- Privacy: Market maker strategies and inventory positions visible only within the xStocks Zone

#### 3.3.4 Market Surveillance Module

Real-time market surveillance is a regulatory requirement for any trading venue (SEC Rule 15c3-5, MAR Article 16). The surveillance module monitors all order flow within the xStocks Zone and generates automated alerts.

```solidity
interface IMarketSurveillance {
    enum AlertType {
        WASH_TRADING,           // Same beneficial owner on both sides
        SPOOFING,               // Large orders placed and cancelled rapidly
        LAYERING,               // Multiple orders at different price levels to create false depth
        FRONT_RUNNING,          // Trading ahead of known pending large orders
        INSIDER_TRADING,        // Trades during blackout window by designated insiders
        PRICE_MANIPULATION,     // Trades intended to artificially move price
        LARGE_TRADE_UNREPORTED  // Block trade exceeding threshold without report
    }

    struct SurveillanceAlert {
        AlertType alertType;
        bytes32 alertId;
        address[] involvedParties;
        bytes32[] involvedOrders;
        uint256 timestamp;
        uint8 severity;             // 1=low, 2=medium, 3=high, 4=critical
        bytes evidence;             // ABI-encoded evidence data
    }

    /**
     * @notice Submit trade data for surveillance analysis.
     * @dev    Called automatically by the matching engine after each trade.
     *         Uses pattern detection algorithms within TEE for privacy.
     */
    function analyzeTradeFlow(
        address stock,
        bytes32[] calldata recentOrderIds,
        bytes32[] calldata recentTradeIds,
        uint256 windowBlocks         // Analysis lookback window
    ) external returns (SurveillanceAlert[] memory alerts);

    /**
     * @notice Generate a Suspicious Activity Report (SAR) or
     *         Suspicious Transaction Report (STR) for regulatory filing.
     * @dev    Only callable by COMPLIANCE_OFFICER_ROLE.
     *         Output encrypted for regulator's viewing key.
     */
    function generateSAR(
        bytes32 alertId,
        bytes calldata additionalContext
    ) external returns (bytes32 sarId, bytes memory encryptedReport);

    /**
     * @notice Get surveillance alerts for a time period.
     */
    function getAlerts(
        address stock,
        uint256 fromBlock,
        uint256 toBlock,
        uint8 minSeverity
    ) external view returns (SurveillanceAlert[] memory);

    /**
     * @notice Halt trading on a specific stock (circuit breaker or regulatory halt).
     * @dev    Only callable by EXCHANGE_OPERATOR_ROLE or via GovernanceTx (0x79).
     */
    function haltTrading(address stock, bytes32 reason) external;
    function resumeTrading(address stock) external;

    event AlertGenerated(bytes32 indexed alertId, AlertType alertType, uint8 severity);
    event TradingHalted(address indexed stock, bytes32 reason);
    event TradingResumed(address indexed stock);
}
```

**Surveillance privacy design**: The surveillance module operates inside the xStocks Zone, with the matching engine and surveillance algorithms running within a TEE. Raw order flow data never leaves the Zone. Only aggregated alerts and SAR/STR reports are exported — encrypted with the regulator's viewing key (L3 audit level per WHI-359). This preserves trader privacy while meeting regulatory surveillance requirements.

**Circuit breaker integration**: When the surveillance module detects extreme price volatility (configurable threshold, e.g., >10% in 5 minutes), it triggers an automatic trading halt. The halt is enforced at the Zone Sequencer level — the Sequencer rejects all new trade transactions for the halted stock until the exchange operator resumes trading. This is the on-chain equivalent of NYSE/NASDAQ circuit breakers.

### 3.4 Settlement System

#### 3.4.1 T+0 Instant Settlement

The BFT instant finality (~600ms) enables T+0 settlement — a revolutionary improvement over traditional T+1/T+2.

```
Traditional Settlement:              On-Chain Settlement:
                                     
Trade Execute ──────────────── T     Trade Execute ──────────────── T
     │                                    │
     │ (clearing house netting)           │ Compliance pre-check
     │                                    │ (auto, <200ms)
     │                                    │
     │                                    │ DVP atomic settlement
     │                                    │ (~600ms BFT finality)
     │                                    │
     │ (CSD settlement)                   ✓ SETTLED at T+0
     │                                    
     ├──────────────────────── T+1
     │ (fail handling)
     │
     ✓ SETTLED at T+2
```

#### 3.4.2 Settlement Finality Mapping

| Settlement Type | Required Finality | Time | Use Case |
|----------------|------------------|------|----------|
| Intra-Zone (same xStocks Zone) | `BFT_CONFIRMED` | ~600ms | Standard trading |
| Cross-Zone (xStocks ↔ Payment) | `ZK_PROVEN` | 5–30 min | Securities DVP |
| Cross-Chain (to external chain) | `L1_ANCHORED` | ~12+ min | Bridge-mediated DVP |

#### 3.4.3 Failed Trade Handling

```solidity
interface ISettlementFailHandler {
    enum FailReason {
        COMPLIANCE_REJECTED,     // Post-trade compliance check failed
        INSUFFICIENT_BALANCE,    // Seller doesn't have enough shares
        INSUFFICIENT_PAYMENT,    // Buyer doesn't have enough cash
        TIMEOUT,                 // Settlement deadline exceeded
        CUSTODIAN_REJECTION      // Physical custodian rejected transfer
    }

    /**
     * @notice Handle a failed settlement.
     * @dev    Returns escrowed assets to original holders.
     *         Logs failure for regulatory reporting.
     */
    function handleFailedSettlement(
        uint256 dvpId,
        FailReason reason,
        bytes calldata details
    ) external;

    /**
     * @notice Query failed settlements for a specific participant.
     */
    function getFailedSettlements(
        address participant,
        uint256 fromBlock,
        uint256 toBlock
    ) external view returns (FailedSettlement[] memory);
}
```

#### 3.4.4 Traditional CSD Interoperability

For the transition period, dual-track settlement is supported:

```
On-chain:    Trade → DVP → T+0 on-chain settlement → Position update
                                    │
                                    │ (async mirror)
                                    v
Off-chain:   Trade → CSD report → T+1 CSD settlement → CSD record update
```

A **CSD Bridge** component reconciles on-chain positions with the traditional CSD registry. This is a custodian-operated service that:
1. Monitors on-chain settlement events
2. Generates SWIFT/ISO 20022 settlement instructions
3. Confirms CSD settlement back on-chain
4. Handles discrepancy alerts

---

## 4. Payment Network Components

### 4.1 Payment Lane Engine

The Payment Lane is a dedicated execution channel with QoS guarantees for payment transactions. It draws directly from Tempo's three-lane block structure.

#### 4.1.1 Lane Architecture

```
Block Structure:
┌──────────────────────────────────────────────────────────────┐
│ Block Header                                                  │
│   shared_gas_limit: dynamic (total block gas)                 │
│   general_gas_limit: 30,000,000 (fixed hard cap)             │
├──────────────┬────────────────────┬──────────────────────────┤
│ System Lane  │ Payment Lane       │ General Lane             │
│ (highest     │ (second priority)  │ (lowest priority)        │
│  priority)   │                    │                          │
│              │ shared_gas_limit   │ general_gas_limit        │
│              │ minus system       │ = 30M gas                │
│              │ minus general      │                          │
│              │ = REMAINING gas    │                          │
│              │                    │                          │
│ Validator    │ TIP-20 transfers   │ Smart contracts          │
│ config,      │ (0x20C0 prefix)    │ DeFi, NFT, all else     │
│ rewards      │                    │                          │
└──────────────┴────────────────────┴──────────────────────────┘
```

**Anti-noisy-neighbor guarantee**: Once `general_gas_limit` (30M) is exhausted, ALL non-payment transactions are blocked — even if total block gas headroom remains. Payment transactions continue filling remaining capacity. This is a **hard QoS boundary enforced at the consensus layer** (block header validation).

#### 4.1.2 Payment Classification (Stateless)

Payment routing is determined purely by transaction target address — no contract calls, no storage reads, zero overhead:

```
Classification v1 (consensus layer — block validation):
  is_payment = target_address starts with 0x20C0

Classification v2 (builder layer — stricter DoS prevention):
  is_payment = v1 checks PLUS:
    - calldata matches recognized payment selector (transfer, transferWithCompliance)
    - NO access lists or authorization lists
    - For AA (0x76) transactions: at least one call, ALL calls target 0x20C0
```

v1 is enforced at consensus (cannot be bypassed). v2 is enforced at the payload builder to prevent gaming of the payment lane. This dual-validation design (from Tempo) prevents DoS vectors while maintaining the simplicity of stateless classification.

#### 4.1.3 Performance Targets

| Metric | Target | Mechanism |
|--------|--------|-----------|
| Finality | <500ms | BFT instant finality (~600ms block, head=safe=finalized) |
| Fee | <$0.001/tx | Fixed gas price: 20B attodollars/gas × 50K gas = $0.001 |
| Throughput | >10,000 TPS | Payment Lane dedicated gas budget + lightweight execution |
| B2C UX | <2s end-to-end | Preconf receipt (~2s) for merchant-facing instant confirmation |

#### 4.1.4 State Channel Optimization (High-Frequency Micro-Payments)

For B2C payment scenarios with very high frequency (e.g., micropayments, streaming payments), a state channel layer reduces on-chain load:

```
┌──────────┐         State Channel         ┌──────────┐
│  Payer   │◄────── off-chain txs ────────►│  Payee   │
│          │   (signed balance updates)     │          │
└────┬─────┘                                └────┬─────┘
     │                                           │
     │ Open channel (on-chain)                   │
     │ Periodic settlement (on-chain)            │
     │ Close channel (on-chain)                  │
     │                                           │
     └───────────── Payment Lane ────────────────┘
```

**Design**: Payer locks funds in a state channel contract. Off-chain, both parties exchange signed balance updates. Periodically (or on close), the final state is settled on-chain via a single Payment Lane transaction. This amortizes gas costs across many micro-payments.

```solidity
interface IPaymentStateChannel {
    enum ChannelState { OPEN, DISPUTE, CLOSED }

    struct Channel {
        bytes32 channelId;
        address payer;
        address payee;
        address token;              // MIP-20 token (0x20C0 prefix)
        uint256 deposit;            // Total locked amount
        uint256 payerBalance;       // Current payer balance in channel
        uint256 payeeBalance;       // Current payee balance in channel
        uint256 nonce;              // Monotonic counter for off-chain updates
        uint256 disputePeriod;      // Blocks for dispute resolution
        ChannelState state;
    }

    /**
     * @notice Open a payment channel by locking funds.
     * @dev    Requires compliance check on both parties.
     */
    function openChannel(
        address payee,
        address token,
        uint256 deposit,
        uint256 disputePeriod
    ) external returns (bytes32 channelId);

    /**
     * @notice Cooperatively close a channel with both parties' signatures.
     * @dev    Settles final balances on-chain in one Payment Lane tx.
     */
    function cooperativeClose(
        bytes32 channelId,
        uint256 payerBalance,
        uint256 payeeBalance,
        uint256 nonce,
        bytes calldata payerSig,
        bytes calldata payeeSig
    ) external;

    /**
     * @notice Initiate unilateral close (dispute path).
     * @dev    Counterparty has `disputePeriod` blocks to submit a higher-nonce state.
     */
    function initiateClose(
        bytes32 channelId,
        uint256 payerBalance,
        uint256 payeeBalance,
        uint256 nonce,
        bytes calldata signature
    ) external;

    /**
     * @notice Challenge a unilateral close with a newer state.
     */
    function challenge(
        bytes32 channelId,
        uint256 payerBalance,
        uint256 payeeBalance,
        uint256 nonce,
        bytes calldata payerSig,
        bytes calldata payeeSig
    ) external;

    /**
     * @notice Finalize a disputed close after the dispute period.
     */
    function finalize(bytes32 channelId) external;

    /**
     * @notice Periodic settlement: settle intermediate state without closing.
     * @dev    Useful for long-running channels (e.g., streaming payments).
     *         Rebalances on-chain while keeping channel open.
     */
    function periodicSettle(
        bytes32 channelId,
        uint256 payerBalance,
        uint256 payeeBalance,
        uint256 nonce,
        bytes calldata payerSig,
        bytes calldata payeeSig
    ) external;

    event ChannelOpened(bytes32 indexed channelId, address indexed payer, address indexed payee, uint256 deposit);
    event ChannelSettled(bytes32 indexed channelId, uint256 payerBalance, uint256 payeeBalance);
    event ChannelClosed(bytes32 indexed channelId);
    event DisputeInitiated(bytes32 indexed channelId, address initiator);
    event DisputeChallenged(bytes32 indexed channelId, address challenger, uint256 nonce);
}
```

**Gas amortization example**: A merchant processing 10,000 micropayments/day at $0.50 each:
- Without state channels: 10,000 × $0.001 = $10/day in gas fees
- With state channels: 2 on-chain txs (open + periodic daily settle) × $0.001 = $0.002/day
- **5,000x gas cost reduction** for high-frequency payment scenarios

**Compliance integration**: State channel open/close operations go through the standard compliance pipeline (PolicyRegistry check). Off-chain updates within the channel are not individually compliance-checked (they are just signed balance updates between two pre-cleared parties). The Travel Rule is checked at channel open time if the deposit exceeds the $3,000 threshold.

### 4.2 Multi-Currency Stablecoin Framework

#### 4.2.1 Stablecoin Registry

```solidity
interface IStablecoinRegistry {
    enum StablecoinType {
        FIAT_COLLATERALIZED,   // USDC, USDT — backed by fiat reserves
        BRIDGE_WRAPPED,         // Cross-chain bridged stablecoins
        NATIVE_ISSUED          // Native on-chain fiat tokenization
    }

    struct StablecoinInfo {
        address token;              // MIP-20 token address (0x20C0 prefix)
        string currencyCode;        // ISO 4217 (USD, EUR, SGD)
        StablecoinType sType;
        address issuer;             // Regulated issuer address
        uint8 decimals;             // Typically 6 (microdollars) per TIP-20
        bool isGasToken;            // Can be used for gas payment
        bytes32 oracleFeedId;       // Price feed for FX conversion
    }

    /**
     * @notice Register a new stablecoin.
     * @dev    Only callable by PROTOCOL_ADMIN. Issuer must be KYC level 4 (institutional).
     */
    function registerStablecoin(StablecoinInfo calldata info) external;
    
    /**
     * @notice Get all registered stablecoins for a currency.
     */
    function getStablecoins(string calldata currencyCode) 
        external view returns (StablecoinInfo[] memory);
    
    /**
     * @notice Get the primary (default) stablecoin for a currency.
     */
    function getPrimaryStablecoin(string calldata currencyCode)
        external view returns (address token);
}
```

#### 4.2.2 Auto-Conversion Engine

Low-slippage stablecoin swaps for multi-currency enterprise operations:

```solidity
interface IAutoConversion {
    /**
     * @notice Swap stablecoins with minimal slippage.
     * @dev    Uses oracle-fed FX rates + liquidity pool depth.
     *         Follows Tempo's StablecoinDEX (0xDEC0) precompile pattern.
     * @param tokenIn     Source stablecoin
     * @param tokenOut    Destination stablecoin
     * @param amountIn    Amount to swap
     * @param minAmountOut Slippage protection
     */
    function swap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minAmountOut
    ) external returns (uint256 amountOut);
    
    /**
     * @notice Get the current FX rate between two stablecoins.
     * @dev    Oracle-fed rate with spread.
     */
    function getRate(address tokenIn, address tokenOut)
        external view returns (uint256 rate, uint256 spread);
    
    /**
     * @notice Enterprise liquidity pool management.
     */
    function addLiquidity(address token, uint256 amount) external returns (uint256 lpTokens);
    function removeLiquidity(address token, uint256 lpTokens) external returns (uint256 amount);
}
```

#### 4.2.3 Stablecoin Gas Payment

Users pay gas fees in any registered stablecoin. The Sequencer auto-converts at execution time:

```
User submits tx with gas token = USDC
    │
    ├── Sequencer reads token ratio oracle (GasPriceOracle predeploy)
    │   conversion: USDC → native gas unit (attodollars)
    │   rate: 50,000 gas × 20B attodollars/gas = 1T attodollars
    │         ÷ 10^12 scaling = 1,000 microdollars = $0.001
    │
    ├── Sequencer deducts USDC from user balance
    ├── Sequencer credits gas budget in native units
    └── Transaction executes with converted gas
```

### 4.3 Travel Rule Engine

Native FATF Travel Rule (Recommendation 16) support for transfers ≥ $3,000.

#### 4.3.1 Travel Rule Interface

```solidity
interface ITravelRuleEngine {
    struct OriginatorInfo {
        bytes32 identityCommitment;  // Hash of PII — NOT plaintext on chain
        bytes32 vaspId;              // Originating VASP identifier
        uint16 jurisdiction;         // ISO 3166-1 numeric
    }

    struct BeneficiaryInfo {
        bytes32 identityCommitment;
        bytes32 vaspId;
        uint16 jurisdiction;
    }

    /**
     * @notice Attach Travel Rule data to a payment.
     * @dev    Called automatically by Payment SDK for transfers ≥ threshold.
     *         PII is NEVER stored on-chain. Two modes:
     *         Mode A: On-chain encrypted — encrypted blob in audit DA channel
     *         Mode B: Off-chain VASP-to-VASP — only flag stored on-chain
     */
    function attachTravelRule(
        bytes32 txHash,
        OriginatorInfo calldata originator,
        BeneficiaryInfo calldata beneficiary,
        uint8 exchangeMode,         // 0 = on-chain encrypted, 1 = off-chain VASP-to-VASP
        bytes calldata encryptedData // Mode A: ECIES-encrypted PII for regulator
    ) external;
    
    /**
     * @notice Check if a transfer requires Travel Rule data.
     * @dev    Threshold: ≥ $3,000 USD equivalent (configurable per jurisdiction)
     */
    function requiresTravelRule(
        address token,
        uint256 amount
    ) external view returns (bool required, uint256 thresholdUSD);
    
    /**
     * @notice Verify Travel Rule compliance for a completed transfer.
     */
    function verifyTravelRule(bytes32 txHash) 
        external view returns (bool compliant, bytes32 status);

    // ═══════════ VASP Registry ═══════════
    
    /**
     * @notice Register a VASP (Virtual Asset Service Provider).
     * @dev    VASP must hold `vasp_registered` certification (bit 2 in ComplianceAttributes).
     */
    function registerVASP(
        bytes32 vaspId,
        string calldata name,
        uint16[] calldata jurisdictions,
        bytes calldata publicKey        // For VASP-to-VASP encrypted exchange
    ) external;
    
    /**
     * @notice Look up a VASP by ID.
     */
    function getVASP(bytes32 vaspId) external view returns (VASPInfo memory);
    
    struct VASPInfo {
        bytes32 vaspId;
        address operator;
        string name;
        uint16[] jurisdictions;
        bytes publicKey;
        bool active;
        uint64 registeredAt;
    }
}
```

#### 4.3.2 Travel Rule Execution Flow

```
Payment of $5,000 USDC (Alice → Bob):

1. SDK detects amount ≥ $3,000 threshold
2. SDK queries Alice's VASP (via IdentityRegistry → VASP mapping)
3. SDK queries Bob's VASP
4. Two execution paths:

   Path A — On-Chain Encrypted:
   ┌─────────────────────────────────────────────────────┐
   │ 1. Collect originator/beneficiary PII              │
   │ 2. Encrypt with regulator's public key (ECIES)     │
   │ 3. Store encrypted blob in Audit DA channel        │
   │ 4. On-chain: hash commitment only                  │
   │ 5. Regulator decrypts via Audit Viewing Key (L3)   │
   └─────────────────────────────────────────────────────┘

   Path B — Off-Chain VASP-to-VASP (preferred for privacy):
   ┌─────────────────────────────────────────────────────┐
   │ 1. VASP-A sends PII to VASP-B via Travel Rule      │
   │    protocol (Notabene, Chainalysis Travel Rule)     │
   │ 2. VASP-B confirms receipt                          │
   │ 3. On-chain: flag `travel_rule_exchanged = true`    │
   │ 4. No PII touches the blockchain                    │
   └─────────────────────────────────────────────────────┘

5. If Travel Rule data missing: tx suspended (not rejected)
   - Reason code: TRAVEL_RULE_MISSING
   - Sender has 72h to provide data before auto-revert
```

#### 4.3.3 ZK Travel Rule (Cross-Zone Transfers)

For cross-Zone payments where PII should not leave the originating Zone:

```
ZK Proof:
  Private inputs: [originator_name, originator_address, beneficiary_name, beneficiary_address]
  Public inputs:  [originator_vasp_commitment, beneficiary_vasp_commitment, transfer_hash]

  Proves: "I have valid originator and beneficiary information matching the committed VASPs"
  Without revealing: actual PII

On-chain verification:
  ISelectiveDisclosure(0x0405).verify(TRAVEL_RULE_ZK, publicInputs, proof)
  Cost: 8,000 gas (fixed)
```

### 4.4 Enterprise Treasury Tools

#### 4.4.1 Multi-Sig Wallet with Role-Based Approvals

```solidity
interface IEnterpriseTreasury {
    enum ApprovalRole { CFO, TREASURER, CONTROLLER, COMPLIANCE_OFFICER, AUDITOR }

    struct ApprovalPolicy {
        uint8 requiredApprovals;     // e.g., 2-of-3
        ApprovalRole[] requiredRoles; // e.g., [CFO, TREASURER] — at least one from each
        uint256 maxAmountPerTx;      // Single-tx limit
        uint256 dailyLimit;          // Rolling 24h limit
        uint256 timelock;            // Delay before execution (seconds)
    }

    /**
     * @notice Propose a payment from the treasury.
     * @dev    Initiates approval workflow based on amount and payment type.
     */
    function proposePayment(
        address token,
        address recipient,
        uint256 amount,
        bytes32 purpose,            // Purchase order, invoice reference, etc.
        bytes calldata metadata     // ERP integration data
    ) external returns (uint256 proposalId);
    
    /**
     * @notice Approve a proposed payment.
     */
    function approvePayment(uint256 proposalId) external;
    
    /**
     * @notice Execute an approved payment (after timelock if applicable).
     */
    function executePayment(uint256 proposalId) external;

    // ═══════════ Payment Routing ═══════════
    
    /**
     * @notice Auto-select optimal payment path (cost, speed, compliance).
     */
    function routePayment(
        address token,
        address recipient,
        uint256 amount,
        PaymentPreference calldata prefs
    ) external returns (PaymentRoute memory route);
    
    struct PaymentPreference {
        bool prioritizeSpeed;       // true = fastest route
        bool prioritizeCost;        // true = cheapest route
        uint256 maxFeePercent;      // Max fee as basis points
        uint256 maxSettlementTime;  // Max seconds to final settlement
    }
    
    struct PaymentRoute {
        address[] path;             // Token addresses in the swap path
        uint256[] amounts;          // Amounts at each step
        uint256 totalFee;           // Total fee in source token
        uint256 estimatedTime;      // Estimated settlement time (seconds)
    }
}
```

#### 4.4.2 Reconciliation Engine

```solidity
interface IReconciliationEngine {
    struct ReconciliationRecord {
        bytes32 txHash;             // On-chain transaction hash
        bytes32 erpReference;       // ERP system reference (PO#, invoice#)
        address token;
        uint256 amount;
        address counterparty;
        uint256 timestamp;
        ReconciliationStatus status;
    }

    enum ReconciliationStatus {
        MATCHED,                    // On-chain tx matches ERP record
        UNMATCHED_ONCHAIN,          // On-chain tx with no ERP match
        UNMATCHED_ERP,              // ERP record with no on-chain tx
        DISCREPANCY                 // Amount/date/counterparty mismatch
    }

    /**
     * @notice Submit an ERP reference for reconciliation matching.
     */
    function submitERPReference(
        bytes32 erpReference,
        address expectedToken,
        uint256 expectedAmount,
        address expectedCounterparty,
        uint256 expectedDate
    ) external;

    /**
     * @notice Get reconciliation status for a time period.
     */
    function getReconciliationReport(
        uint256 fromTimestamp,
        uint256 toTimestamp
    ) external view returns (ReconciliationRecord[] memory records, ReconciliationSummary memory summary);
    
    struct ReconciliationSummary {
        uint256 totalTransactions;
        uint256 matched;
        uint256 unmatchedOnchain;
        uint256 unmatchedERP;
        uint256 discrepancies;
    }

    /**
     * @notice Export reconciliation data in ISO 20022 format for ERP integration.
     */
    function exportISO20022(uint256 fromTimestamp, uint256 toTimestamp)
        external view returns (bytes memory iso20022XML);
}
```

---

## 5. Cross-Narrative Shared Components

### 5.1 Oracle Framework

#### 5.1.1 Multi-Type Oracle Registry

```solidity
interface IOracleFramework {
    enum OracleType {
        PRICE,          // Asset valuations, stock prices, FX rates
        IDENTITY,       // Off-chain KYC status synchronization
        COMPLIANCE,     // Sanctions list updates, regulatory changes
        CORPORATE       // Dividend amounts, split ratios, voting results
    }

    struct OracleConfig {
        OracleType oracleType;
        bytes32 feedId;
        address[] providers;        // Multiple data sources (no single point of failure)
        uint8 minProviders;         // Minimum agreeing providers (consensus threshold)
        uint256 heartbeatInterval;  // Max seconds between updates
        uint256 deviationThreshold; // Max % deviation to trigger update (basis points)
        uint256 stalePeriod;        // Seconds after which data is considered stale
    }

    /**
     * @notice Get the latest value for a price feed.
     */
    function getLatestPrice(bytes32 feedId)
        external view returns (uint256 price, uint256 timestamp, uint8 confidence);
    
    /**
     * @notice Get the latest value with full provenance.
     */
    function getLatestPriceWithProvenance(bytes32 feedId)
        external view returns (
            uint256 price,
            uint256 timestamp,
            address[] memory providers,
            bytes memory aggregationProof
        );
    
    /**
     * @notice Register a new oracle feed.
     */
    function registerFeed(OracleConfig calldata config) external returns (bytes32 feedId);
    
    /**
     * @notice Submit a price update (called by oracle providers).
     */
    function submitPrice(bytes32 feedId, uint256 price, bytes calldata proof) external;
}
```

#### 5.1.2 Enterprise SLA Oracle Requirements

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Availability** | 99.99% | Financial infrastructure standard |
| **Update latency** | <5s for real-time feeds | Stock price feeds for xStocks trading |
| **Staleness threshold** | Configurable (30s–1h) | FX rates: 30s; RWA NAV: 24h |
| **Data sources** | Min 3 per feed | Prevent single-point manipulation |
| **Zone privacy** | Price feeds Zone-scoped if needed | Dark pool reference prices invisible to lit market |

#### 5.1.3 Oracle Types by Narrative

| Oracle Feed | Narrative | Update Frequency | Privacy |
|------------|-----------|-----------------|---------|
| Stock price (real-time) | xStocks | <5s | Public (lit market) or Zone-scoped (dark pool) |
| RWA NAV (Net Asset Value) | RWA | Daily/weekly | Zone-scoped (issuer + holders only) |
| FX rates | Payment | <30s | Public |
| Sanctions list (OFAC SDN) | All | <1h | Global (compliance layer) |
| KYC status update | All | Event-driven | Private (IdentityRegistry only) |
| Corporate action data | xStocks, RWA | Event-driven | Zone-scoped until announcement |

#### 5.1.4 Oracle Security Model

Oracle data integrity is critical for financial infrastructure. The framework implements a multi-layered security model:

**Data source diversity**: Each price feed requires a minimum of 3 independent data sources (configurable per feed). The aggregation algorithm uses a **weighted median** rather than mean, making it resistant to single-source outliers and manipulation.

**Provenance chain**: Every oracle update carries a cryptographic provenance chain: `[source_signature, aggregator_signature, timestamp, block_number]`. Any consumer can verify the complete data path from raw source to on-chain value. The `getLatestPriceWithProvenance()` method exposes this chain.

**Staleness protection**: Contracts consuming oracle data should use `getLatestPrice()` and check the returned `timestamp` against `stalePeriod`. If data is stale (no update within the configured heartbeat), the oracle returns a `confidence` level of 0, signaling that the data should not be used for settlement-critical operations. The DVP Engine, for example, will refuse to execute settlement if the FX rate oracle is stale.

**Zone-scoped feeds**: Certain price data (e.g., dark pool reference prices, RWA internal NAV valuations) must remain confidential within a Zone. Zone-scoped oracle feeds are only accessible via the Zone's `StateReader` precompile (`0x0201…0400`) — main chain contracts cannot read them. This prevents information leakage from private pricing.

**Oracle update gas sponsorship**: In RWA and xStocks Zones, oracle update transactions are gas-sponsored by the Zone Sequencer, ensuring oracle providers are never blocked by gas cost considerations.

### 5.2 Governance Framework

#### 5.2.1 Three-Tier Governance Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Protocol-Level Governance                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Scope: Chain-wide parameters (block time, gas limits,   │ │
│ │        validator set, protocol upgrades)                 │ │
│ │ Voters: Validator nodes + institutional stakers          │ │
│ │ Model: Weighted voting (stake-based)                     │ │
│ │ Timelock: 7 days (standard), 48h (expedited)            │ │
│ │ Emergency: 2/3 validator supermajority → immediate pause │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Zone-Level Governance                                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Scope: Zone policies, admission rules, performance      │ │
│ │        params, compliance policy updates                 │ │
│ │ Voters: Zone operator + Zone participants (institutions) │ │
│ │ Model: Permissioned voting (1-institution-1-vote)        │ │
│ │ Timelock: 48h (standard), 1h (expedited)                │ │
│ │ Emergency: Zone operator → immediate pause              │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Asset-Level Governance                                       │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Scope: Individual asset parameters (compliance policy,  │ │
│ │        investor requirements, corporate action triggers) │ │
│ │ Voters: Issuer + Transfer Agent + (optionally) holders  │ │
│ │ Model: Role-based (issuer proposes, agent confirms)      │ │
│ │ Timelock: 24h (standard)                                │ │
│ │ Emergency: Issuer freeze → immediate                    │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 5.2.2 Governance Interface

```solidity
interface IGovernance {
    enum GovernanceScope { PROTOCOL, ZONE, ASSET }
    enum ProposalState { PENDING, ACTIVE, DEFEATED, SUCCEEDED, QUEUED, EXECUTED, CANCELLED }

    struct Proposal {
        uint256 proposalId;
        GovernanceScope scope;
        uint256 scopeId;            // Zone ID or Asset ID (0 for protocol)
        address proposer;
        bytes calldata_;            // Encoded governance action
        uint256 startBlock;
        uint256 endBlock;
        uint256 timelockExpiry;
        ProposalState state;
    }

    function propose(
        GovernanceScope scope,
        uint256 scopeId,
        bytes calldata action,
        string calldata description
    ) external returns (uint256 proposalId);
    
    function castVote(uint256 proposalId, uint8 support) external;
    function execute(uint256 proposalId) external;
    function cancel(uint256 proposalId) external;
    
    /**
     * @notice Emergency pause — bypasses normal governance for critical situations.
     * @dev    Requires 0x79 GovernanceTx with EmergencyPause action + ThresholdSig.
     */
    function emergencyPause(GovernanceScope scope, uint256 scopeId) external;
    function emergencyUnpause(GovernanceScope scope, uint256 scopeId) external;
}
```

### 5.3 Event Notification System

#### 5.3.1 Business Event Types

```solidity
interface IEventNotificationSystem {
    enum EventCategory {
        TRANSACTION,        // Transfer confirmed, payment settled
        COMPLIANCE,         // Compliance alert, sanctions hit, KYC expiry
        CORPORATE_ACTION,   // Dividend declared, split announced, rights offering
        GOVERNANCE,         // Proposal created, vote result, parameter change
        SETTLEMENT,         // DVP proposed, accepted, settled, failed
        MARKET,             // Price alert, circuit breaker triggered, trading halted
        SYSTEM              // Zone status, sequencer health, finality upgrade
    }

    struct EventSubscription {
        bytes32 subscriptionId;
        EventCategory[] categories;
        address[] tokenFilters;     // Only events for these tokens (empty = all)
        uint256[] zoneFilters;      // Only events from these Zones (empty = all)
        string webhookUrl;          // HTTPS webhook endpoint
        string kafkaTopic;          // Kafka topic (alternative to webhook)
    }

    /**
     * @notice Subscribe to business events.
     */
    function subscribe(EventSubscription calldata sub) external returns (bytes32 subscriptionId);
    
    /**
     * @notice Unsubscribe from events.
     */
    function unsubscribe(bytes32 subscriptionId) external;
    
    /**
     * @notice Query historical events.
     */
    function queryEvents(
        EventCategory category,
        uint256 fromBlock,
        uint256 toBlock,
        address tokenFilter
    ) external view returns (BusinessEvent[] memory events);
    
    struct BusinessEvent {
        EventCategory category;
        bytes32 eventId;
        uint256 blockNumber;
        uint256 timestamp;
        address token;
        uint256 zoneId;
        bytes data;                 // ABI-encoded event-specific data
    }
}
```

#### 5.3.2 Enterprise Integration Architecture

```
On-Chain Events ──── Event Indexer ──── Notification Router
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
              Webhook Service          Kafka Producer          WebSocket Server
                    │                         │                         │
              ┌─────┴─────┐            ┌──────┴──────┐          ┌──────┴──────┐
              │ Enterprise │            │ Enterprise  │          │ Real-time   │
              │ Backend    │            │ Data Lake   │          │ Dashboard   │
              │ (REST API) │            │ (Kafka →    │          │ (Browser)   │
              └────────────┘            │  BigQuery)  │          └─────────────┘
                                        └─────────────┘
```

---

## 6. SDK & Developer Tools

### 6.1 Business SDK Design

The SDK is the developer's primary interface to the business component layer. It hides all privacy, compliance, and Zone complexity behind high-level abstractions.

#### 6.1.1 SDK Architecture

```
@mantle/enterprise-sdk
├── core/           → Connection, auth, Zone routing
├── rwa/            → Asset issuance, lifecycle, DVP
├── xstocks/        → Trading, settlement, corporate actions
├── payment/        → Transfers, Travel Rule, treasury
├── compliance/     → Identity queries, policy checks
├── governance/     → Proposals, voting
└── events/         → Subscriptions, notifications
```

#### 6.1.2 RWA SDK Module

```typescript
import { MantleEnterprise } from '@mantle/enterprise-sdk';

const sdk = new MantleEnterprise({
  rpcUrl: 'https://enterprise.mantle.xyz',
  auth: { type: 'jwt', token: '...' },  // Enterprise SSO integration
  defaultZone: 'rwa-zone-1'
});

// ═══════════ Asset Issuance Workflow ═══════════

// Step 1: Register a new RWA asset
const asset = await sdk.rwa.createAsset({
  name: 'Prime Commercial REIT Fund A',
  symbol: 'PCR-A',
  assetClass: 'REIT',
  totalSupply: 1_000_000,           // 1M tokens
  compliance: {
    regulations: ['reg-d', 'mica'],
    investorRequirements: {
      minKYCLevel: 2,               // Enhanced KYC
      certifications: ['accredited_investor'],
      allowedJurisdictions: ['US', 'EU', 'SG'],
      minInvestment: 10_000,        // $10K minimum
      maxHolders: 2000              // Reg D limit
    }
  },
  custodian: {
    address: '0x...',               // Licensed custodian
    custodyAgreementURI: 'ipfs://...'
  },
  lockupPeriod: 365 * 24 * 3600,   // 1 year lockup
});

console.log(`Asset registered: ${asset.assetId}`);
console.log(`Token contract: ${asset.tokenAddress}`);
console.log(`Compliance policy: ${asset.policyId}`);

// Step 2: Primary market issuance (Propose-Accept pattern)
const issuance = await sdk.rwa.issue({
  assetId: asset.assetId,
  allocations: [
    { investor: '0xAlice...', amount: 50_000 },
    { investor: '0xBob...', amount: 30_000 },
  ]
});
// SDK automatically:
// - Verifies each investor's KYC level via IdentityRegistry (0x0401)
// - Checks accredited investor certification
// - Checks jurisdiction whitelist
// - Creates allocation proposals (investors must accept)

// Step 3: Investor accepts (from investor's SDK instance)
await investorSdk.rwa.acceptAllocation(issuance.issuanceId);
// Tokens minted only after acceptance — bilateral consent

// ═══════════ Compliant Transfer ═══════════

await sdk.rwa.transfer({
  asset: asset.tokenAddress,
  to: '0xCharlie...',
  amount: 5_000,
  // SDK automatically:
  // 1. Pre-checks compliance via isCompliant() [saves gas on failure]
  // 2. Generates ZK compliance proof if needed (cross-Zone)
  // 3. Attaches proof to transferWithCompliance()
  // 4. If compliance fails: returns detailed reason code
});

// ═══════════ Corporate Action: Dividend ═══════════

const dividend = await sdk.rwa.declareDividend({
  assetId: asset.assetId,
  paymentToken: 'USDC',
  amountPerUnit: 0.50,              // $0.50 per token
  recordDate: 'latest',            // Use latest block as record date
});
// SDK automatically:
// - Takes snapshot of all holder balances
// - Creates claimable entitlements
// - Emits events for Event Notification System

// ═══════════ DVP Settlement ═══════════

const dvp = await sdk.rwa.proposeDVP({
  delivery: {
    token: asset.tokenAddress,
    amount: 10_000,
    zone: 'rwa-zone-1',
  },
  payment: {
    token: 'USDC',
    amount: 500_000,                // $500K
    zone: 'payment-zone-1',
  },
  counterparty: '0xBuyer...',
  requiredFinality: 'ZK_PROVEN',   // High-value: wait for ZK proof
  deadline: 3600,                   // 1 hour settlement window
});

// Counterparty accepts
await buyerSdk.rwa.acceptDVP(dvp.dvpId);
// Atomic settlement:
// - Shares released from RWA Zone escrow to buyer
// - USDC released from Payment Zone escrow to seller
// - Both legs atomic: settle together or fail together
```

#### 6.1.3 Payment SDK Module

```typescript
// ═══════════ Simple Payment ═══════════

const receipt = await sdk.payment.send({
  currency: 'USDC',
  amount: 500,
  to: '0xMerchant...',
  memo: 'Invoice #12345',
  // SDK automatically:
  // - Routes through Payment Lane (0x20C0 prefix)
  // - Checks Travel Rule threshold ($3,000)
  // - If ≥ $3,000: attaches Travel Rule data (VASP-to-VASP exchange)
  // - Uses preconf for instant receipt (~2s)
});

console.log(`Payment hash: ${receipt.txHash}`);
console.log(`Finality: ${receipt.finality}`);      // BFT_CONFIRMED
console.log(`Fee: $${receipt.fee}`);                // ~$0.001

// ═══════════ Cross-Currency Payment ═══════════

const receipt = await sdk.payment.send({
  currency: 'EURC',                 // Pay in EUR
  amount: 450,
  to: '0xMerchant...',
  receiveCurrency: 'USDC',         // Merchant receives USD
  maxSlippage: 0.001,              // 0.1% max slippage
  // SDK automatically:
  // - Gets FX rate from oracle
  // - Routes through AutoConversion engine
  // - Executes swap + transfer atomically
});

// ═══════════ Enterprise Treasury ═══════════

// Multi-sig payment with role-based approval
const proposal = await sdk.payment.treasury.proposePayment({
  from: '0xTreasury...',
  currency: 'USDC',
  amount: 1_000_000,               // $1M payment
  to: '0xVendor...',
  purpose: 'Q2 infrastructure payment',
  erpReference: 'PO-2026-0842',
});
// Triggers multi-sig workflow:
// - CFO approval required (amount > $100K)
// - Treasurer approval required
// - 24h timelock before execution

// ═══════════ Reconciliation ═══════════

const report = await sdk.payment.reconciliation.getReport({
  from: '2026-05-01',
  to: '2026-05-07',
  format: 'iso20022',
});
console.log(`Matched: ${report.summary.matched}`);
console.log(`Discrepancies: ${report.summary.discrepancies}`);
```

#### 6.1.4 xStocks SDK Module

```typescript
// ═══════════ Stock Trading ═══════════

// Submit a limit order
const order = await sdk.xstocks.submitOrder({
  stock: '0xAPPL...',              // Tokenized Apple stock
  side: 'BUY',
  type: 'LIMIT',
  quantity: 100,
  price: 195.50,
  timeInForce: 'GTC',
});

// SDK automatically:
// - Checks trading rules (price limits, insider window, Reg SHO)
// - Verifies broker license of the trader's institution
// - Routes to matching engine (lit market or dark pool based on order size)

// Dark pool block trade (>$200K)
const darkOrder = await sdk.xstocks.submitOrder({
  stock: '0xAPPL...',
  side: 'SELL',
  type: 'LIMIT',
  quantity: 5000,                   // $975K block trade → dark pool eligible
  price: 195.00,
  venue: 'dark_pool',
  // Encrypted order: only matching engine (TEE) sees details
});

// ═══════════ Shareholder Voting ═══════════

const proposals = await sdk.xstocks.getActiveProposals('0xAPPL...');
await sdk.xstocks.vote({
  proposalId: proposals[0].id,
  choice: 'FOR',
  // Voting weight automatically calculated from snapshot balance
});
```

### 6.2 Contract Template Library

Pre-audited contract templates for common enterprise use cases:

| Template | Narrative | Description | Key Params |
|----------|-----------|-------------|------------|
| `RWA-REIT` | RWA | Real estate investment trust token | Asset class, jurisdiction, lockup |
| `RWA-Bond` | RWA | Fixed-income bond with coupon | Coupon rate, maturity, denomination |
| `RWA-Fund` | RWA | Open-end or closed-end fund token | NAV oracle, redemption window |
| `RWA-Carbon` | RWA | Carbon credit token with retirement | Vintage, registry, retirement hook |
| `XSTOCKS-Equity` | xStocks | Tokenized stock with full corp actions | ISIN, CUSIP, custodian |
| `XSTOCKS-TradingPair` | xStocks | Order book + settlement for a pair | Stock token, payment token, trading rules |
| `PAY-Merchant` | Payment | Merchant payment acceptance | Accepted currencies, settlement address |
| `PAY-Payroll` | Payment | Batch payroll distribution | Employee registry, multi-currency |
| `GOV-Zone` | Governance | Zone governance with voting | Participants, quorum, timelock |
| `GOV-Asset` | Governance | Asset parameter governance | Issuer, agents, holder voting |

Each template is:
- **Pre-deployed** via upgrade-transaction pattern (same mechanism as Mantle Arsia upgrades)
- **Factory-instantiable** — enterprises deploy instances via factory methods, not raw deployment
- **Compliance-integrated** — PolicyRegistry hooks pre-configured; compliance by default
- **Upgradeable** — proxy pattern with governance-controlled upgrade

#### 6.2.1 Template Deployment Model

Contract templates follow a factory pattern that prevents enterprises from deploying non-compliant variations:

```solidity
interface ITemplateFactory {
    /**
     * @notice Deploy an RWA token from a pre-audited template.
     * @dev    The template is stored as immutable bytecode in the factory.
     *         Factory auto-configures:
     *         - PolicyRegistry hook (ComplianceCheck on every transfer)
     *         - Role assignments (issuer, regulator, transfer agent)
     *         - Zone deployment (if specified)
     *         Address is deterministic: CREATE2 with salt = hash(assetId, issuer, nonce)
     */
    function deployRWAToken(
        bytes32 templateId,     // e.g., "RWA-REIT", "RWA-Bond"
        AssetConfig calldata config
    ) external returns (address tokenAddress, bytes32 policyId);

    /**
     * @notice Get available templates and their configurations.
     */
    function getTemplate(bytes32 templateId)
        external view returns (TemplateInfo memory);

    struct TemplateInfo {
        bytes32 templateId;
        string description;
        bytes32 assetClass;
        uint256 version;
        bytes32 auditHash;         // Hash of audit report
        bool active;
    }
}
```

**Why factory deployment matters**: In enterprise environments, arbitrary contract deployment creates compliance risk — a developer might deploy a token that skips compliance hooks. By restricting deployment to factory-instantiated templates (with `CREATE`/`CREATE2` blocked inside Zones per WHI-359), the platform ensures every deployed token inherits the full compliance stack. The factory pattern also enables deterministic addressing, which simplifies cross-Zone asset tracking.

**Template versioning and upgrades**: Templates use the transparent proxy pattern with upgrade governance. When a new template version is approved (e.g., adding MiCA 2.0 compliance features), existing token instances can be upgraded via Zone-level governance proposal. The upgrade is applied atomically across all instances within the Zone, ensuring no regulatory gap during transitions.

---

## 7. Interface Definitions: Components ↔ Infrastructure Layers

### 7.1 Component → Compliance Layer

```
Business Component                         Compliance Layer (WHI-360)
─────────────────                         ──────────────────────────

MIP-20 Token     ── transfer() hook ───► PolicyRegistry (0x0403)
  │                                        .isAuthorized(from, to, amount, context)
  │                                        ├── GLOBAL: sanctions + KYC ≥ 1
  │                                        ├── ZONE: narrative-specific rules
  │                                        ├── ASSET: token-specific rules
  │                                        └── CUSTOM: institution rules
  │
  ├── isCompliant() ────── STATICCALL ──► ComplianceCheck (0x0402)
  │                                        .checkTransaction(from, to, value, data, context)
  │                                        Returns: (result, reasonCode, failedPolicies[])
  │
  └── issuer verification ── STATICCALL ─► IdentityRegistry (0x0401)
                                            .isVerified(addr) → bool
                                            .getComplianceAttributes(addr) → ComplianceAttributes
                                            .getKYCLevel(addr) → uint8
```

### 7.2 Component → Privacy Layer

```
Business Component                         Privacy Layer (WHI-359)
─────────────────                         ──────────────────────────

DVP Engine       ── cross-Zone msg ─────► ZonePortal (mainchain contract)
  │                                        .deposit(token, to, amount, memo)
  │                                        .depositEncrypted(token, amount, keyIndex, encrypted)
  │                                        .processWithdrawal(withdrawal, remainingQueue)
  │
  ├── Zone routing ─── ZoneFactory ──────► IZoneFactory
  │                                        .createZone(ZoneConfig) → zoneId
  │
  └── privacy deposit ── tx type 0x78 ──► EncryptedDeposit precompile (0x0404)
                                            ECIES + Chaum-Pedersen verification
                                            Bounce-back on compliance failure

Travel Rule      ── ZK proof ───────────► SelectiveDisclosure (0x0405)
                                            .verify(proofType, publicInputs, proof)
                                            8,000 gas fixed
```

### 7.3 Component → Execution Layer

```
Business Component                         Execution Layer (WHI-358)
─────────────────                         ──────────────────────────

Payment Lane     ── 0x20C0 prefix ──────► Three-Lane Block Builder
  │                                        Consensus validates: shared_gas_limit, general_gas_limit
  │                                        Payment txs get dedicated gas budget
  │
  ├── instant UX ── preconf API ────────► Preconfirmation Module
  │                                        eth_sendRawTransactionWithPreconf → receipt (~2s)
  │
  └── finality ─── IFinalityOracle ─────► Finality Oracle
                                            .getFinalityLevel(txHash) → FinalityLevel
                                            .requireFinality(txHash, minLevel) → bool

DVP Engine       ── settlement ─────────► Custom Tx Types
  │                 0x77 ComplianceTx       (KYC attestation in payload)
  │                 0x78 PrivacyDepositTx   (encrypted cross-Zone deposit)
  │                 0x79 GovernanceTx       (protocol governance actions)
  │
  └── crypto ops ─── CALL ─────────────► CryptoSuite (0x0103)
                                            .eciesEncrypt/Decrypt()
                                            .blsVerify()
                                            .chaumPedersenVerify()

Multi-Sig        ── threshold sig ──────► ThresholdSig (0x0105)
                                            .verifyMultisig(threshold, pubkeys, sigs, hash)
                                            .verifyThreshold(t, n, pubkeys, sigs, hash)
                                            Gas: 4,000 + 2,000×n
```

### 7.4 Cross-Component Interactions

```
RWA Lifecycle Engine
    │
    ├── Asset registration → deploys MIP-20 token (via ComplianceTokenFactory)
    │                        → registers compliance policy (via PolicyRegistry 0x0403)
    │                        → registers asset in oracle framework (price/NAV feed)
    │
    ├── Primary issuance → checks investor identity (via IdentityRegistry 0x0401)
    │                     → executes Propose-Accept flow
    │                     → mints tokens on acceptance
    │
    ├── Trading → delegates to DVP Engine (secondary market)
    │           → DVP Engine → ZonePortal (cross-Zone)
    │           → Trading Rules Engine (xStocks only)
    │
    ├── Corporate actions → snapshot balance (MIP-20.snapshot())
    │                     → oracle feed (dividend amount, split ratio)
    │                     → Event Notification System → webhook
    │
    └── Redemption → DVP Engine (token ↔ payment)
                   → Asset state: TRADING → MATURING → REDEEMED

Payment Lane Engine
    │
    ├── Payment classification → stateless 0x20C0 prefix check
    │                          → dedicated gas budget (anti-noisy-neighbor)
    │
    ├── Travel Rule → amount check (≥ $3,000)
    │               → VASP lookup (VASP Registry)
    │               → ZK proof or VASP-to-VASP exchange
    │               → SelectiveDisclosure (0x0405) verification
    │
    ├── Multi-currency → FX oracle rate query
    │                  → AutoConversion engine swap
    │                  → atomic swap + transfer
    │
    └── Treasury tools → multi-sig approval (ThresholdSig 0x0105)
                       → payment routing (optimal path)
                       → reconciliation engine (ERP matching)
```

---

## 8. Comparison with Existing Approaches

### 8.1 Token Standard Comparison

| Feature | **MIP-20 (Our Design)** | **Tempo TIP-20** | **ERC-3643 (T-REX)** | **Securitize DS** |
|---------|------------------------|------------------|---------------------|------------------|
| **Base standard** | ERC-20 compatible | Native precompile | ERC-20 extension | Proprietary |
| **Compliance enforcement** | Precompile + Sequencer (inviolable) | Precompile (TIP-403) | Smart contract hook (bypassable via delegatecall) | Off-chain service |
| **Compliance proof** | ZK + attestation signature | Policy check (binary) | Identity registry check | Off-chain API |
| **Asset lifecycle** | Full (issuance → redemption) | Limited (transfer only) | Transfer + freeze | Full (off-chain) |
| **Corporate actions** | On-chain (dividend, split, vote) | None | None | Off-chain |
| **DVP settlement** | Native cross-Zone atomic | None (TIP-20 only) | None | External |
| **Gas side-channel** | Fixed gas per operation | Fixed 100K gas | Variable (leaks info) | N/A |
| **Privacy** | Zone-scoped + ZK selective disclosure | Zone-scoped + ECIES | No native privacy | Limited |
| **EVM compatibility** | Full (Hardhat/Foundry) | Limited (custom tx types) | Full | N/A |

### 8.2 DVP Settlement Comparison

| Feature | **Our DVP Engine** | **Canton DVP** | **Traditional CSD** | **Atomic Swap (DeFi)** |
|---------|-------------------|---------------|---------------------|----------------------|
| **Atomicity** | Coordinator-mediated 2PC | Merkle DAG sub-tx | CCP-guaranteed | Hash time-locked |
| **Privacy** | Zone isolation (each Zone sees only its leg) | Sub-tx projection (each party sees only their leaf) | Bilateral (buyer-seller-CSD) | None (all public) |
| **Finality** | BFT ~600ms → ZK 5–30min → L1 12+min | Deterministic immediate (all confirmers agree) | T+1/T+2 (legal finality) | Block confirmation |
| **Cross-asset** | Cross-Zone (RWA Zone ↔ Payment Zone) | Cross-Synchronizer (Unassign/Assign) | CSD ↔ CSD (via CSD links) | Same chain only |
| **Bilateral consent** | Propose-Accept pattern | Signatory model (compile-time) | Instruction matching | No consent required |
| **Failed trade** | Auto-revert + escrow refund | Mediator REJECT → rollback | Fail management queue | HTLC timeout refund |
| **Compliance** | Per-leg compliance check (each Zone's PolicyRegistry) | Per-party check (Daml signatory constraint) | Pre-trade compliance (manual) | None |
| **EVM compatible** | Yes | No (Daml/JVM) | No (SWIFT/FIX) | Yes |

### 8.3 Payment Infrastructure Comparison

| Feature | **Our Payment Lane** | **Tempo Payment Lane** | **Visa/Mastercard** | **SWIFT gpi** |
|---------|---------------------|----------------------|--------------------|--------------| 
| **Throughput** | >10,000 TPS | >10,000 TPS (target) | ~65,000 TPS (peak) | ~40M msgs/day |
| **Finality** | <500ms (BFT) + preconf ~2s | ~600ms (BFT) | Real-time auth + T+1 settlement | Seconds → hours |
| **Fee** | <$0.001/tx | ~$0.001/tx | 1.5–3.5% interchange | $5–50/msg |
| **QoS guarantee** | Hard gas lane separation at consensus | Hard gas lane separation at consensus | SLA-based | SLA-based |
| **Travel Rule** | Native (on-chain + ZK) | Not implemented | Not applicable | Not applicable |
| **Multi-currency** | Native (oracle-fed FX + AMM) | TIP-20 multi-token | Network-level | SWIFT GPI multi-currency |
| **Privacy** | Zone-level (Payment Zone) | Zone-level | Tokenized PAN | Correspondent banking |
| **Programmability** | Smart contracts (state channels, auto-convert) | TIP-20 precompiles only | None | None |
| **Enterprise treasury** | Native (multi-sig, routing, reconciliation) | None | Separate corporate cards | Separate treasury mgmt |

### 8.4 Key Advantages of Our Design

**vs. Tempo**: We add full asset lifecycle management, DVP settlement, corporate actions, and enterprise treasury tools that Tempo doesn't have. We preserve Tempo's excellent payment lane QoS guarantees and compliance-at-precompile-level enforcement.

**vs. Canton**: We maintain full EVM compatibility (Hardhat/Foundry/OpenZeppelin) while incorporating Canton's best ideas (Propose-Accept, Observer-as-regulator, sub-transaction privacy semantics). Canton requires Daml — a non-standard language that locks developers into the ecosystem. Our design uses standard Solidity.

**vs. Traditional Finance (CSD/SWIFT)**: T+0 settlement (vs. T+1/T+2), programmable compliance (vs. manual checks), atomic DVP (vs. CCP-mediated), and drastically lower costs ($0.001 vs. $5–50 per transaction).

**vs. DeFi (Uniswap/Aave)**: Enterprise-grade compliance, identity management, privacy, and regulatory reporting that DeFi completely lacks. Regulated institutions cannot use DeFi; they can use our platform.

---

## Appendix A: Precompile Quick Reference

| Address | Name | Gas | Business Component Usage |
|---------|------|-----|-------------------------|
| `0x0401` | IdentityRegistry | 2,000 (query) / 50,000 (write) | Investor verification, KYC level check |
| `0x0402` | ComplianceCheck | 5,000 | Transfer compliance pre-check |
| `0x0403` | PolicyRegistry | 3,000 (query) / 100,000 (write) | Auto-invoked on every MIP-20 transfer |
| `0x0404` | EncryptedDeposit | 6,000 | Cross-Zone privacy deposits (ECIES + Chaum-Pedersen) |
| `0x0405` | SelectiveDisclosure | 8,000 | ZK proofs for Travel Rule, compliance, audit |
| `0x0103` | CryptoSuite | 6,000–12,000 | ECIES, BLS, Chaum-Pedersen operations |
| `0x0104` | TimeLock | 5,000 (query) / 25,000 (write) | Lockup periods, vesting schedules |
| `0x0105` | ThresholdSig | 4,000 + 2,000×n | Multi-sig treasury approvals |
| `0x20C0…` | ComplianceToken | ~50,000/transfer | MIP-20 token instances (Payment Lane eligible) |

## Appendix B: Custom Transaction Type Quick Reference

| Type | Name | Purpose | Business Use |
|------|------|---------|-------------|
| `0x76` | Account Abstraction | Multi-call + P256/WebAuthn | Consumer-facing payment UX (passkeys) |
| `0x77` | Compliance Tx | KYC attestation in payload | Identity registration, credential binding |
| `0x78` | Privacy Deposit | ECIES-encrypted Zone deposit | Cross-Zone DVP, private transfers |
| `0x79` | Governance Tx | Protocol/Zone/Asset governance | Governance proposals, emergency pause |

## Appendix C: Finality Level Quick Reference

| Level | Time | Mechanism | Business Use |
|-------|------|-----------|-------------|
| `PENDING` | 0 | Submitted to mempool | — |
| `BFT_CONFIRMED` | ~600ms | Simplex BFT 2/3 threshold | Payments, intra-Zone trades |
| `COMPLIANCE_CLEARED` | ~600ms + compliance check | BFT + compliance confirmed | Standard regulated transfers |
| `ZK_PROVEN` | 5–30 min | STARK validity proof | High-value DVP, cross-Zone settlement |
| `L1_ANCHORED` | ~12+ min | ZK proof on Ethereum L1 | Cross-chain DVP, highest security |

## Appendix D: Zone Type Configuration

| Zone | Privacy | Gas Model | Compliance Policy | Target Narrative |
|------|---------|-----------|------------------|-----------------|
| Public Mainchain | T0 (transparent) | EIP-1559 | Global only | DeFi, general |
| Payment Zone | T1 (DA-level) | Fixed low (<$0.001/tx) | VASP + Travel Rule | Payment |
| RWA Zone | T3 (sub-transaction) | Sponsored (zero compliance gas) | Securities regulation | RWA tokenization |
| xStocks Zone | T3 (sub-transaction) | Sponsored | Market regulation (Reg NMS/SHO) | Tokenized equities |
| Custom Zone | Configurable | Configurable | Configurable | Enterprise-specific |
