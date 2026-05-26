# English Speech Script — Mantle Competitive Landscape & Narrative Direction

> Target duration: ~20 minutes | Format: Per-slide | [Bracketed text = speaker notes]

---

## Slide 1 — Cover

Hey everyone. Today's internal sharing is about Mantle's competitive landscape and narrative direction. We spent a few weeks doing a systematic research deep-dive across the entire L2 space and adjacent competitors, with one core question: where should Mantle go next.

---

## Slide 2 — Agenda

Three parts today.

Part one: market reality — what's changed and what challenges Mantle faces. Part two: competitors — what everyone else is doing and where the pressure is coming from. Part three: direction — we evaluated three candidate narratives for technical feasibility.

Let me give you the punchline upfront: our analysis shows that **institutional finance** is the strongest-fit direction for Mantle. I'll walk you through the why and the how.

---

## Slide 3 — L2 Landscape Evolution

Let's start with the big picture. This chart shows TVL distribution across the main L2s as of May 25th.

Two numbers tell the story: Arbitrum at roughly $15-17 billion, taking 40-44% share. Base at $11-13 billion, taking 28-33%. Together they hold about 77% of all L2 DeFi liquidity.

Mantle sits at $1.15-1.2 billion — firmly in the second tier. Daily active addresses: about 2,276. I'll come back to this number.

On the right, DAU comparison. Base is at 382K daily actives — roughly 168x Mantle's Q1 2026 figure. That's not a one-order-of-magnitude gap; it's two.

The backdrop: after EIP-4844 in March 2024, gas fees dropped 80-90%. Fee competition is dead as a differentiator. The new competition axes are ecosystem control, user distribution, ZK privacy, and yield-bearing assets.

---

## Slide 4 — Narrative Shift: DeFi → RWA / Institutional Finance

Now the narrative shift. Two contrasting stories on this slide.

Left side: DeFi's ceiling. Global DeFi TVL is in the $92-140 billion range — way below the $250 billion market expectation. 83-95% of deposited liquidity sits idle at any given time. Aave alone has 59% lending market share. And incentive-driven TVL is historically the least sticky — Blast went from $2.7B to $55M.

Right side: RWA acceleration. On-chain RWA market cap went from about $6 billion in early 2025 to $31-34 billion by May 2026 — over 200% year-over-year. US Treasury tokenization alone is at $13-15 billion. BlackRock BUIDL has $2.5B AUM, and in May they filed with the SEC to bring a $7 billion money market fund on-chain.

There's a structural tension to flag. Vitalik's February 2026 essay explicitly advocates for privacy-first and censorship resistance — FOCIL is confirmed for the Hegota hard fork later this year. But institutional finance needs KYC, needs permissioning. These two directions create structural tension within the Ethereum ecosystem. Our recommendation: keep the public L2 as a neutral settlement layer, build compliance capabilities at the L3/Validium layer.

---

## Slide 5 — Mantle's Current Position & Challenges

Where Mantle stands today.

Tech stack: OP Stack, Ethereum-aligned, EigenDA. Industry-standard components — no unique technical moat here.

Asset base: mETH at about $925M TVL, 4th largest ETH LST. cmETH at $515M. Stablecoin supply peaked at $825M, retained 81% at about $669M. This asset base is important for the direction discussion later.

But activity is the hard truth. Look at this trend line — Q1 2025 DAU at 37.8K, drops to 12.2K, spikes to 53K, crashes to 5-6K, then 2,276 in Q1 2026. This rollercoaster pattern means our users aren't organic growth — way too volatile.

New growth pillars — MI4, UR, MantleX, Aave V3 — are all early stage. Aave V3 brought $290M+ in 12 days, but it's assessed as incentive-driven capital.

The core question is clear: TVL has partially recovered, but users are leaving. We need a new narrative anchor.

---

## Slide 6 — Chapter 1 Takeaways

Three takeaways from Chapter 1.

One: DeFi must be defended but cannot drive growth. Two: RWA and institutional finance is the fastest-growing on-chain narrative at over 200% YoY. Three: compliance infrastructure is becoming a new competitive dimension — among the five chains we studied, only zkSync has it.

Let's look at what the competitors are actually doing.

---

## Slide 7 — Competitor Framework

We organized competitors into three categories.

L2 competitors — same-track direct competition: Base, Arbitrum, Optimism, zkSync, StarkNet, X Layer. L1 general-purpose chains — cross-track substitution: Solana, Sui, BNB Chain. L1 vertical chains — new-track positioning: Tempo, Circle Arc, Canton.

Our analysis dimensions: 90-day GitHub code activity plus narrative direction shifts. We want to see what they're actually building, not just what they're talking about.

---

## Slide 8 — L2 Competitors: Tech Comparison (Part 1)

Three L2s on the "platform expansion" track.

Base is pursuing client independence — Azul is their first independent network upgrade, consolidating onto base-reth-node. Flashblocks gives 200ms preconfirmation UX. Beryl is building security token PolicyRegistry. 1,810 PRs in 90 days — highest dev intensity. Their core moat is Coinbase's 110M+ user distribution. You can't copy that.

Arbitrum is running multi-VM plus appchains. Stylus for Rust/C contracts, Orbit for custom appchains, Timeboost for MEV ordering auctions, BoLD for permissionless validation. Deepest DeFi liquidity among L2s.

Optimism is the Superchain coordination layer. 1,202 PRs mostly in the monorepo. One critical risk for us: op-geth support ends May 31st — migration to op-reth is mandatory after that. This directly affects Mantle.

**Key judgment**: these three are all pursuing ecosystem expansion. Mantle's scale — 2.3K DAU versus Base's 382K — is insufficient for this playbook.

---

## Slide 9 — L2 Competitors: Tech Comparison (Part 2)

Three more L2s with very different strategies.

**zkSync** — this is today's most important benchmark. After DeFi TVL collapsed over 96%, they pivoted entirely to ZK privacy plus enterprise. ZKsync OS is a RISC-V level VM rewrite. Airbender is next-gen prover. But the real story is **Prividium** — an enterprise compliance Validium package. They claim 35+ financial institutions. Code evidence includes a full local dev environment with Keycloak identity, protected RPC, and block explorer. The 35+ banks figure is vendor-reported and unverified, but Prividium as a model has code backing.

**StarkNet** — Cairo/STARK ecosystem, STWO next-gen prover actively developed. DeFi TVL only ~$199M but leads in ZK engineering depth. Non-EVM architecture means no direct migration competition.

**X Layer** — pay special attention here because it's most similar to Mantle: exchange-backed, OP Stack L2. Migrated from Polygon CDK. Building Exchange OS and Agent Payment Protocol. OKX's 120M users create a distribution advantage.

---

## Slide 10 — L1 General-Purpose Chains

On the L1 side.

Solana's Alpenglow is a completely new consensus mechanism targeting Q3 mainnet. Jito BAM is building block construction infrastructure. They claim $10B stablecoin supply and $200B monthly stablecoin transfers.

Sui's gasless stablecoin transfers are live on mainnet — this is protocol-level, not subsidized. Seven stablecoins including USDC can be transferred P2P with zero gas. DeepBook is building an on-chain order book.

BNB Chain engineering is focused on BSC client stabilization and the reth dual-client strategy. The 250ms block time target is only a BEP spec — no implementation PR exists. AI Agent narrative has high volume but weak code.

**Key point**: L1 general-purpose chains are accelerating across speed, ecosystem, and institutional adoption. L2s can't survive on the "Ethereum security" narrative alone.

---

## Slide 11 — L1 Vertical Chains

This is the most direct competitive category.

**Tempo** — Stripe and Paradigm-backed payments chain. Payment Lane partitions gas into System, Payment, and General pools — payment transactions get priority. Protocol-level stablecoin gas at roughly $0.001 per payment. BFT consensus targets 600ms finality. Mainnet is operational, but actual transaction volumes and merchant depth are unverified. And Zones' validity proofs are empty — the interface exists but the proofs don't.

**Circle Arc** — the USDC issuer building their own L1. Their CCTP V2 already supports 26 chains with $126 billion cumulative volume. StableFX does institutional cross-currency atomic settlement. 8 non-USD partner stablecoins. Testnet has 100+ institutions and 244 million transactions processed. Mainnet beta expected this summer. ARC token presale: $222M at $3B FDV. **Key fact**: Circle's official docs — CCTP supported chains, USDC contract addresses, Circle Mint supported chains — do not list Mantle.

**Canton** — the enterprise financial workflow benchmark. Broadridge DLR settles $368 billion per day, roughly $8 trillion per month. Goldman Sachs, HSBC, DTCC are on it. Daml contract language with need-to-know privacy. Non-EVM, small dev ecosystem, but unmatched production deployment in institutional finance.

**Core warning**: vertical tracks already have native competitors who optimized for specific scenarios at the architecture level.

---

## Slide 12 — Chapter 2 Key Findings

Three conclusions that lead into Chapter 3.

One: the ecosystem expansion playbook — what Base, Arbitrum, Optimism are doing — requires scale Mantle doesn't have. Two: vertical tracks have native competitors already in position — doing a pure vertical chain isn't realistic for Mantle. Three: there's a differentiation opportunity at the intersection — L2 plus compliance infrastructure, between general-purpose and vertical. zkSync Prividium has proven this position exists.

So what paths can Mantle take? We evaluated three directions.

---

## Slide 13 — Evaluation Framework

We analyzed each direction across four dimensions: market size, competitive landscape, key technical barriers, and Mantle fit.

The three directions and our conclusions: AgentFi — weak. Payment Chain — medium. Institutional finance — strong. Let me walk through each.

---

## Slide 14 — AgentFi (Weak)

AgentFi is one of the hottest narratives right now. CoinGecko's AI Agents category is at about $3.68 billion market cap. But real usage signals are limited — x402 has 50K+ listed resources, but the overall market is still a mix of narrative, dev tools, and early product.

Competition is fierce: Base has AgentKit plus Coinbase distribution, X Layer has Agent Payment Protocol and Agentic Wallet, Solana has pay-kit. All serious EVM or high-performance agent infrastructure.

Mantle currently has no first-party Agent SDK, no Paymaster, no flagship application. We can position as an "EVM AgentFi settlement and yield layer," but this doesn't constitute a primary narrative.

**Verdict: weak.** Hot narrative, but Mantle lacks structural advantage. We can participate, but shouldn't bet the house on it.

---

## Slide 15 — Payment Chain (Medium)

Payments is a fast-growing market. Stablecoin supply at $320.7B. USDC's single-quarter on-chain volume hit $21.5 trillion, up 263% YoY. But actual stablecoin payment penetration is only 0.02% of global payments. Supply-side rails are accelerating; demand-side is still bottlenecked by off-ramps, merchant relations, and compliance.

Critical gaps: Mantle's L2 soft confirmation doesn't meet payment-grade hard finality requirements. More importantly, Circle's CCTP does not list Mantle — that's a structural barrier for cross-chain stablecoin flows.

But there's space in certain sub-scenarios. B2B invoice settlement and merchant treasury settlement are medium-to-strong fit. Mantle's DeFi yield ecosystem can provide "post-payment treasury management" — something Tempo and Arc can't match.

**Verdict: medium.** We can't win the pure payment chain narrative, but B2B settlement as a sub-scenario within institutional finance is viable.

One more point: payments need Web2 distribution. Without Stripe-level or Coinbase-level partnerships, pure crypto payment solutions struggle to reach mass adoption.

---

## Slide 16 — Institutional Finance: Market Opportunity

Now the strongest-fit direction.

On-chain RWA went from $6 billion to $31-34 billion — more than doubled in a year. Several catalysts behind this: BlackRock BUIDL at $2.5B AUM, SEC's statement on tokenized securities, GENIUS Act signed into law. This isn't projection — it's happening.

What do institutions need? Four things: compliance, privacy, data sovereignty, and audit. Without these, real institutional capital doesn't come on-chain.

The core thesis: this isn't a "should we do this" question — it's "who gets there first." zkSync's Prividium is already on this path, claiming 35+ financial institutions. Even if that's vendor-reported, it tells us institutions have this demand, and someone is capturing it.

---

## Slide 17 — Institutional Finance: Prividium Benchmark

Prividium's architecture is worth examining closely.

The core is ZK Validium plus enterprise privacy. Transaction data stays off L1 — only state roots and validity proofs go on-chain. Proxy RPC handles access control, RBAC manages role permissions, private DA layer stores data, STARK proofs ensure state correctness.

What's zkSync-native? The RISC-V virtual machine and Airbender prover — we don't need and shouldn't try to copy these.

What's reproducible on other L2s? Proxy RPC, RBAC, private DA layer, compliance policy engine, audit logs — these are Prividium's core value, and they don't depend on the ZK proof system. We can build a similar compliance isolation layer within the OP Stack framework.

---

## Slide 18 — Institutional Finance: Mantle Compliance Tech Stack Roadmap

This is the most important slide today — the technical gap matrix.

[Walk through each row]

Validium private DA: we currently use EigenDA with no private DA capability. Needs EigenDA adaptation or standalone DA layer. High complexity.

Compliance execution layer: there's reportedly an ERC-3643 demo foundation, but we couldn't find public source confirmation. Target: identity registry plus policy engine plus audit logs plus selective disclosure.

Multi-layer access control: Bridge to RPC to Sequencer to Execution — four-layer filtering. Currently at zero.

Enterprise Zone/L3: MIX4 provides some foundation to build on.

ZK compliance proofs: KYC-in-ZK, can integrate existing solutions.

**Core message**: the tech stack is almost entirely greenfield — but the path is clear, and we have a benchmark to reference.

---

## Slide 19 — Institutional Finance: Mantle Fit Assessment

Strengths.

First, EVM ecosystem plus Ethereum L2 legitimacy — institutional integration costs are lower. Second, mETH and cmETH yield ecosystem — this is what Tempo, Arc, and Canton don't have. Institutions don't just need settlement; post-settlement capital needs yield management. This is our unique value. Third, MI4 and Securitize partnership with up to $400M treasury anchor. Fourth, USDY and mUSD are already live.

Challenges. Tech stack is greenfield, but path is clear. CCTP absence is a hard gap. No production institutional client case yet.

**Phased approach**: first 3 months, compliance RPC and identity registry — no mainchain privacy changes needed. Months 3-9, Enterprise Zone and zkKYC PoC. Months 9-18, Validium DA and full-stack compliance.

One strategic principle: **productize compliance visibility before productizing cryptographic privacy**. Permissioning, audit, and disclosure APIs are closer to enterprise revenue than FHE.

---

## Slide 20 — Three Directions Compared

Let's put all three side by side.

AgentFi — weak. Early-stage market, red ocean competition, no structural advantage for Mantle. Payment Chain — medium. Viable as a sub-scenario but not as a primary narrative. Institutional finance — strong. Accelerating market, few first movers, clear path, and Mantle has unique advantages.

---

## Slide 21 — Conclusions & Next Steps

Three core conclusions.

One: the L2 space has moved from generic competition to differentiated positioning. Not choosing a direction means choosing to be marginalized.

Two: competitive pressure comes from three dimensions — L2 platform expansion, L1 substitution, and vertical chain positioning. A three-front squeeze.

Three: **institutional finance is Mantle's highest-fit narrative direction**. Benchmark against zkSync Prividium. Leverage treasury and yield ecosystem advantages to build a compliance tech stack.

Suggested next steps: immediately evaluate CCTP and Circle partnership feasibility — this is a structural gap. Q3, build compliance RPC plus identity registry MVP. Q4, begin Enterprise Zone PoC.

A few open items for follow-up: op-geth EOL migration planning, quantifying Mantle developer activity, confirming ERC-3643 demo status.

That's the end of the presentation. Let's move to Q&A.

---

## Slide 22 — Q&A

[Prepared answers]

- **Tech stack timeline and resources**: Phase 1's compliance RPC and identity registry is the lightest lift — MVP feasible in 3 months. The heavy part is Validium DA, at least 9-18 months.
- **Differentiation from Prividium**: We have treasury ($4B+), DeFi yield ecosystem (mETH/cmETH), and MI4/Securitize foundation. Prividium doesn't have open DeFi composability.
- **Compliance approach choices**: KYC layer can integrate existing zkKYC solutions like Polygon ID or Sismo. Compliance policy engine references the ERC-3643/T-REX framework.
- **How payments fit into institutional finance**: B2B settlement is fundamentally a payment use case. Paymaster plus Payment Intent SDK plus merchant treasury is the first landing point.
- **Why not bet on AgentFi**: Short-term hype doesn't equal long-term moat. Base has Coinbase distribution, Solana has performance advantage — we have no structural edge in this arena.
