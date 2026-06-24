# Confidential Compliance Token Traceability Matrix

> **Project slug**: `confidential-compliance-token-research`
> **Report issue**: `7b29e4a8-01eb-4cbf-9b59-8e363f9a40e4`
> **Final report**: `confidential-compliance-token-research/report/final-report.md`
> **Source index**: `confidential-compliance-token-research/research-sections/_index.md` @ `cd5ba23`
> **Access date for upstream web/doc sources**: inherited from final sections; most external sources are access-dated 2026-06-24.

## Source Section Register

| Code | Topic | Issue | Main merge commit | Final path |
|---|---|---|---|---|
| S1 | requirements-framework | `7d7fa951-8160-4b03-a7ae-8ff1a6a9664c` | `9eb29a1` | `confidential-compliance-token-research/research-sections/requirements-framework/final.md` |
| S2 | zama-confidential-rwa | `22741382-2866-4221-8b39-17551f5f400e` | `1a9fad0` | `confidential-compliance-token-research/research-sections/zama-confidential-rwa/final.md` |
| S3 | pse-private-transfers-constraints | `687a44f7-c9b1-42a3-b435-99ea6fd09a29` | `b54e21b` | `confidential-compliance-token-research/research-sections/pse-private-transfers-constraints/final.md` |
| S4 | compliance-token-private-extension | `18fbd577-47e2-47f6-bfbf-a7519114df13` | `bb27379` | `confidential-compliance-token-research/research-sections/compliance-token-private-extension/final.md` |
| S5 | confidential-rwa-candidates | `84e8d44a-f970-4531-a351-f9d801da4947` | `29269d9` | `confidential-compliance-token-research/research-sections/confidential-rwa-candidates/final.md` |
| S6 | route-comparison | `d44834f3-e3f7-4174-9200-395052956c18` | `1728cac` | `confidential-compliance-token-research/research-sections/route-comparison/final.md` |
| S7 | mantle-protocol-design | `dfd8a3e5-1841-4eac-8050-daaecfff89dd` | `0a058bd` | `confidential-compliance-token-research/research-sections/mantle-protocol-design/final.md` |
| S8 | integration-roadmap | `cf06b8fa-ed51-4b1e-8f3f-bfcd2f76197a` | `0d11f05` | `confidential-compliance-token-research/research-sections/integration-roadmap/final.md` |

## Key Claim Traceability

| ID | Report claim | Source section(s) | Evidence path / URL / version | Commit / access | Confidence and caveat |
|---|---|---|---|---|---|
| C-01 | CCT minimum boundary is compliance token + confidential accounting + selective disclosure + auditability. | S1 | `requirements-framework/final.md`, Executive Summary and item-2 | `9eb29a1` | High; framework definition. |
| C-02 | Mantle phase 1 should avoid new chain/VM, new bridge, full privacy-node operations, hardfork, or execution-client change. | S1, S6, S8 | `requirements-framework/final.md`; `route-comparison/final.md`; `integration-roadmap/final.md` | `9eb29a1`, `1728cac`, `0d11f05` | High; repeated across route and roadmap sections. |
| C-03 | Recommended route is ERC-3643-style compliance substrate plus ERC-7984/OZ confidential overlay with replaceable backend. | S6, S7 | `route-comparison/final.md`, Executive Summary and §2.4; `mantle-protocol-design/final.md`, Executive Summary | `1728cac`, `0a058bd` | High; core route decision. |
| C-04 | Zama/OZ is the first backend validation path, but not an unconditional production claim. | S2, S6, S7 | `zama-confidential-rwa/final.md`; `route-comparison/final.md`; `mantle-protocol-design/final.md` | `1a9fad0`, `1728cac`, `0a058bd` | High for candidate status; Mantle support and SLA remain gating. |
| C-05 | ERC-3643 consists of six core T-REX contracts plus ONCHAINID identity layer. | S4 | `compliance-token-private-extension/final.md`, final fixes and item-3 | `bb27379` | High; dispatch caveat explicitly incorporated. |
| C-06 | Plain ERC-3643 amount-dependent modules do not directly consume encrypted ERC-7984 amount/balance handles. | S2, S4, S7 | `zama-confidential-rwa/final.md` items 3-4; `compliance-token-private-extension/final.md`; `mantle-protocol-design/final.md` | `1a9fad0`, `bb27379`, `0a058bd` | High; key technical tension. |
| C-07 | Encrypted amount/balance predicates must not use predicate-dependent revert because it leaks the comparison result. | S7, S8 | `mantle-protocol-design/final.md`, final refinement and item-3; `integration-roadmap/final.md` PoC gates | `0a058bd`, `0d11f05` | High; production gate. |
| C-08 | B20 supplies policy/compliance vocabulary, not current confidentiality. | S4, S6, S7 | `compliance-token-private-extension/final.md` items 2, 6, 7; `route-comparison/final.md` §3.2; `mantle-protocol-design/final.md` | `bb27379`, `1728cac`, `0a058bd` | High; local/current-state code checks remain bounded. |
| C-09 | Base/Mantle code observations are current-state checks and not production facts. | S4, S8 | `compliance-token-private-extension/final.md` item-7; `integration-roadmap/final.md` local Mantle code analysis | `bb27379`, `0d11f05` | Medium-high; bounded scans, not proof of absence or roadmap. |
| C-10 | Phase-1 encrypted balance is mandatory as product requirement but gated by backend production readiness. | S4, S6, S8 | `compliance-token-private-extension/final.md` Executive Summary and item-5; `route-comparison/final.md`; `integration-roadmap/final.md` | `bb27379`, `1728cac`, `0d11f05` | High; product vs production distinction. |
| C-11 | Inco Lightning is the strongest non-Zama backend backup, but Mantle support and TEE trust remain gaps. | S5, S6 | `confidential-rwa-candidates/final.md` Inco profile; `route-comparison/final.md` backup bucket | `29269d9`, `1728cac` | Medium-high; Base/mainnet and audit claims are vendor-labeled unless independently pinned. |
| C-12 | Inco confidential ERC20 framework is unaudited PoC only and should not be reused as production code. | S1, S5 | `requirements-framework/final.md` item-5; `confidential-rwa-candidates/final.md` Inco PoC row | `9eb29a1`, `29269d9` | High; README caveat carried forward by source sections. |
| C-13 | VOSA-RWA/VOSA-20 is a lightweight PoC fallback, not production main route. | S5, S6 | `confidential-rwa-candidates/final.md`; `route-comparison/final.md` | `29269d9`, `1728cac` | Medium; forum draft, unaudited, exposed graph, issuer-control gaps. |
| C-14 | Railgun/Privacy Pools provide source-of-funds and association-set/disclosure lessons but not issuer-token lifecycle. | S3, S5, S6 | `pse-private-transfers-constraints/final.md`; `confidential-rwa-candidates/final.md`; `route-comparison/final.md` | `b54e21b`, `29269d9`, `1728cac` | Medium-high; component classification. |
| C-15 | Paladin/Pente is a business-workflow privacy supplement, not the minimal token-ledger route. | S5, S6 | `confidential-rwa-candidates/final.md`; `route-comparison/final.md` | `29269d9`, `1728cac` | Medium; component classification. |
| C-16 | Optalysys is an FHE performance/productionization reference, not token standard or CCT route. | S1, S5, S6 | `requirements-framework/final.md`; `confidential-rwa-candidates/final.md`; `route-comparison/final.md` | `9eb29a1`, `29269d9`, `1728cac` | Medium; vendor performance material unverified. |
| C-17 | Account-based confidential token is better near-term substrate than note-based pool for Mantle CCT. | S3, S6 | `pse-private-transfers-constraints/final.md` item-3; `route-comparison/final.md` | `b54e21b`, `1728cac` | Medium-high; product fit, not privacy-ceiling claim. |
| C-18 | Disclosure must be modeled by authority, trigger, payload, scope, revocation, residual leakage, and log. | S1, S2, S3, S7 | `requirements-framework/final.md`; `zama-confidential-rwa/final.md`; `pse-private-transfers-constraints/final.md`; `mantle-protocol-design/final.md` | `9eb29a1`, `1a9fad0`, `b54e21b`, `0a058bd` | High; cross-section consensus. |
| C-19 | Full-history viewing key or unbounded observer access is an anti-pattern. | S2, S3, S6, S7 | Zama ACL/OZ ObserverAccess caveats; PSE disclosure anti-patterns; route disclosure view; protocol design | `1a9fad0`, `b54e21b`, `1728cac`, `0a058bd` | High; backend-specific historical revocation remains unresolved. |
| C-20 | Phase-1 CCT does not hide address graph, event existence, timing, mempool/order flow, or private identity by default. | S1, S2, S3, S7 | `requirements-framework/final.md`; Zama lifecycle; PSE account vs note model; protocol non-goals | `9eb29a1`, `1a9fad0`, `b54e21b`, `0a058bd` | High; residual leakage must be stated. |
| C-21 | Bridge/redeem is an intentional disclosure boundary and must be logged. | S1, S2, S6, S7, S8 | requirements bridge/redeem capability; Zama lifecycle; route constraints; protocol flows; roadmap checklist | `9eb29a1`, `1a9fad0`, `1728cac`, `0a058bd`, `0d11f05` | High; legal settlement path remains product-specific. |
| C-22 | Generic ERC-20 DeFi compatibility should not be claimed without adapters. | S1, S3, S6 | requirements DeFi caveat; PSE DeFi blockers; route non-goals | `9eb29a1`, `b54e21b`, `1728cac` | High; adapter-specific future work. |
| C-23 | BackendAdapter must keep public interfaces backend-neutral. | S6, S7, S8 | route hybrid shape; protocol backend abstraction; roadmap Phase 0 tasks | `1728cac`, `0a058bd`, `0d11f05` | High; avoids Zama/Inco/native lock-in. |
| C-24 | Phase 0 should stop if no credible backend path exists. | S8 | `integration-roadmap/final.md`, phase table and risk tree | `0d11f05` | High; roadmap gate. |
| C-25 | Pilot readiness requires measured p50/p95/p99 and cost plus numeric thresholds before decision. | S8 | `integration-roadmap/final.md`, Executive Summary, item-5, item-8 checklist C-20 | `0d11f05` | High; no vendor-only SLA acceptance. |
| C-26 | Native B20-like / PolicyRegistry / encrypted-accounting precompile belongs to phase 2 only. | S4, S6, S8 | phase boundary table; route verdict; native roadmap | `bb27379`, `1728cac`, `0d11f05` | High; requires separate protocol proposal. |
| C-27 | Vendor roadmap, performance, partnership, and audit claims are unverified unless independently confirmed. | S2, S5, S6, dispatch caveats | Zama T-REX post handling; Inco audit claim; Fhenix status; Optalysys performance material | `1a9fad0`, `29269d9`, `1728cac` | High; report preserves unverified labels. |
| C-28 | The PoC minimum loop is KYC/policy onboarding, confidential mint, confidential transfer, scoped audit disclosure, freeze or recovery, and evidence export. | S8, S7 | `integration-roadmap/final.md` item-1; `mantle-protocol-design/final.md` flows | `0d11f05`, `0a058bd` | High; operational acceptance gate. |
| C-29 | [TW inference] Mantle should frame the first program as a gated feasibility and PoC track, not production launch. | S6, S7, S8 | route verdict + protocol gates + integration roadmap | `1728cac`, `0a058bd`, `0d11f05` | High synthesis; combines accepted route, protocol, and roadmap outputs. |
| C-30 | [TW inference] Disclosure UX and audit export are core product surfaces, not documentation appendices. | S1, S3, S7, S8 | requirements selective-disclosure vector; PSE product constraints; protocol DisclosureRegistry; PoC checklist | `9eb29a1`, `b54e21b`, `0a058bd`, `0d11f05` | High synthesis; cross-section product conclusion. |

## External Source Handling

| Source family | Treatment |
|---|---|
| Standards and docs | ERC-3643, ERC-7984, OpenZeppelin Confidential Contracts, Zama docs, Inco docs are cited through final sections with 2026-06-24 access dates unless otherwise noted. |
| Vendor claims | Roadmap, performance, partnership, audit, and mainnet-support claims remain vendor/self-report unless a source section pinned independent code, audit, or observed chain evidence. |
| Local code checks | Base and Mantle checks are bounded `current-state-checked` evidence. They are not production release commitments. |
| Soft prior research | Prior EVM privacy sections are used only where the accepted CCT sections incorporated them or explicitly marked them as soft corroboration. |
