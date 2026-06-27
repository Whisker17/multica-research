---
topic: "Mantle native AA 策略建议与 dev team 科普材料"
project_slug: "base-eip8130-native-aa"
topic_slug: "mantle-native-aa-strategy"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "base-eip8130-native-aa/outlines/mantle-native-aa-strategy.md"
  draft: "base-eip8130-native-aa/research-sections/mantle-native-aa-strategy/drafts/round-{n}.md"
  final: "base-eip8130-native-aa/research-sections/mantle-native-aa-strategy/final.md"
  index: "base-eip8130-native-aa/research-sections/_index.md"

scope: "回答用户 Q2（科普）+ Q3（结论）：基于 WHI-280、WHI-281、WHI-276 已接受 final sections，产出面向 Mantle dev teams 的 ERC-4337 / EIP-7702 / EIP-8130 native AA 科普材料，生成两张 fireworks-tech-graph 架构图（SVG+PNG），并给出 Mantle 是否应实现类似 EIP-8130 native AA 的保守策略建议。结论必须在「现在实现 / 暂缓观察 / PoC 先行」三档中逐项评估；默认不得把 EIP-8130 Draft 包装成立即生产工程化建议。"
audience: "Mantle dev teams、协议/客户端工程师、钱包与 AA infra 工程师、产品技术决策者、Research Review Agent、Technical Writer Agent。读者熟悉 EVM/L2 基础，但不应假设已掌握 4337、7702、8130 的机制差异。"
expected_output: "一份可审查的策略型研究 section：包含 dev team 科普材料、两张 SVG+PNG 架构图、三档决策裁决（现在实现 / 暂缓观察 / PoC 先行）、可回溯到 WHI-280/WHI-281/WHI-276 final.md 路径与 commit SHA 的依据、分阶段路线、轻量 PoC 设想、风险登记，以及暂缓条件/触发点。"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-27T05:28:01Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-27T05:28:01Z"

multica_issue_id: "605b8c4f-1fdf-4e5c-9f04-f2b5e2d1d348"
report_issue_id: "fc840c0d-ac87-41c8-b1ae-6d1318b8eaba"
branch_name: "research/base-eip8130-native-aa/mantle-native-aa-strategy"
base_commit: "b78d2b2d3daa1fdf6a9c81a2a0583750dc0c3be2"
language: "zh-CN"
research_depth: "strategy-synthesis"
source_boundary: "accepted-final-sections-first; no-new-research-unless-a-gap-is-explicitly-marked"
primary_inputs:
  - path: "base-eip8130-native-aa/research-sections/native-aa-cross-comparison/final.md"
    source_id: "S1"
    commit: "b78d2b2d3daa1fdf6a9c81a2a0583750dc0c3be2"
    role: "WHI-281 横向对比裁决；D12 Mantle 适配成本；D13 场景适配；Base 选择 8130 的证据标签"
  - path: "base-eip8130-native-aa/research-sections/mantle-aa-status/final.md"
    source_id: "S2"
    commit: "e507dffc12d5735b113c4a552185915836b09bf6"
    role: "WHI-280 Mantle ERC-4337 / EIP-7702 当前支持、采用效果、DX/provider gap 与 native-AA 决策输入"
  - path: "base-eip8130-native-aa/research-sections/eip8130-deep-dive/final.md"
    source_id: "S3"
    commit: "c4a6deb2d440630b40fcfaad8b371d2d88349987"
    role: "WHI-276 EIP-8130 原理、Base 实现路径、Draft/spec drift 与客户端改造面"
index_entry_proposal:
  order: 8
  topic_slug: "mantle-native-aa-strategy"
  multica_issue_id: "605b8c4f-1fdf-4e5c-9f04-f2b5e2d1d348"
  final_path: "base-eip8130-native-aa/research-sections/mantle-native-aa-strategy/final.md"
  dependencies: "native-aa-cross-comparison, mantle-aa-status, eip8130-deep-dive"
  status: "done"
---

# Research Outline: Mantle native AA 策略建议与 dev team 科普材料

## Items

### item-1: Source Corpus Lock And Evidence Ledger

Lock the strategy draft to the three upstream final sections named in `primary_inputs` before writing any recommendation. The deep draft must not re-litigate the full native-AA landscape from scratch; it should preserve WHI-281 as the accepted cross-comparison verdict, WHI-280 as the accepted Mantle status baseline, and WHI-276 as the accepted EIP-8130/Base implementation deep dive. The output must include a compact evidence ledger that lists each upstream final path, commit SHA, what it is used for, and which caveats must be carried into the final recommendation.

- **Priority**: high
- **Dependencies**: none

Required extraction:

| Source | Required use | Caveat to preserve |
|---|---|---|
| `native-aa-cross-comparison/final.md` @ `b78d2b2d3daa1fdf6a9c81a2a0583750dc0c3be2` | 4337/7702/8130 principle contrast, Base selection evidence labels, D12/D13 decision dimensions, scheme applicability boundaries | Do not convert `inference` into official Base rationale; do not say 4337/7702 failed |
| `mantle-aa-status/final.md` @ `e507dffc12d5735b113c4a552185915836b09bf6` | Mantle AA status, 4337 usage metrics, 7702 sample-level support, DX/provider gap, native-AA decision inputs | Mantle effect verdict is "效果一般 / 部分指标偏弱, 7702 aggregate unknown", not "proved bad" |
| `eip8130-deep-dive/final.md` @ `c4a6deb2d440630b40fcfaad8b371d2d88349987` | EIP-8130 mechanics, Base implementation scope, txpool/RPC/receipt/client changes, Draft/spec drift | 8130 is Draft; Base constants and PR surface have drift/open items |

Quality gates:

- Every decision claim must include at least one upstream `final.md` path and commit SHA.
- Any claim based on synthesis must be labelled `inference` or `strategy-judgment`, not `fact`.
- If the draft adds a fresh source or observation, it must be isolated in a "supplemental check" table and cannot override the three accepted upstream finals without explicit caveat.
- The draft must preserve the conservative baseline: no "立即生产实现" recommendation while EIP-8130 remains Draft.

### item-2: Dev Team Primer For ERC-4337, EIP-7702, And EIP-8130

Produce the educational core for Mantle dev teams. This item should explain the three schemes in mechanism-first language: where validation happens, who pays gas, what the protocol sees, how batching works, how EOA migration is handled, and why these differences matter for an OP-Stack L2. The tone should be explanatory rather than advocacy-oriented.

- **Priority**: high
- **Dependencies**: item-1

Required explanation blocks:

| Block | Content requirements | Source anchor |
|---|---|---|
| ERC-4337 | UserOperation, EntryPoint, bundler/alt mempool, paymaster, smart account validation, mature ecosystem, EOA migration friction | S1, S2 |
| EIP-7702 | Pectra type `0x04`, EOA set-code/delegation, original-address UX, residual ECDSA root key, no native payer/account configuration lifecycle | S1, S2 |
| EIP-8130 | AA typed tx, `sender_auth`, `payer_auth`, AccountConfiguration, actor/authenticator/scope, 2D nonce, phased calls, txpool/RPC/receipt visibility | S1, S3 |
| What 8130 improves | Protocol-visible validation and payer semantics, bounded admission, native account-change/batch structure, lower 4337-specific infra dependence | S1, S3 |
| What 8130 does not solve | Wallet distribution, app demand, sponsor economics, SDK docs, provider adoption, Draft/security/client-cost risks | S1, S2, S3 |

The primer should include a compact "one sentence mental model" table:

| Scheme | Mental model |
|---|---|
| ERC-4337 | Smart-account UX implemented above the protocol through UserOps, bundlers, EntryPoint, and paymasters |
| EIP-7702 | Existing EOA temporarily/persistently delegates execution to code while root authority remains EOA authorization |
| EIP-8130 | Account validation, payer, nonce, configuration, and batched execution become first-class transaction/client semantics |

### item-3: Required Architecture Diagrams And Asset Plan

Generate two production-quality architecture diagrams using `fireworks-tech-graph` during the deep draft phase, and export each as both SVG and PNG. The diagrams must be embedded or linked from the draft/final section and committed under the research section asset directory. The outline reviewer should verify that the diagrams are not just decorative: they must teach the core mechanism differences and be directly referenced by the prose.

- **Priority**: high
- **Dependencies**: item-2

Required assets:

| Asset ID | Output paths | Purpose | Minimum content |
|---|---|---|---|
| `diag-1` | `base-eip8130-native-aa/research-sections/mantle-native-aa-strategy/assets/three-layer-aa.svg` and `.png` | 三层 AA 架构对照图 | ERC-4337 application/infra layer, EIP-7702 EOA enhancement layer, EIP-8130 protocol-native tx/client layer; arrows showing where validation, gas payment, and execution enter the stack |
| `diag-2` | `base-eip8130-native-aa/research-sections/mantle-native-aa-strategy/assets/why-8130-native.svg` and `.png` | "8130 为什么是 native" 示意图 | AA typed transaction -> txpool/sequencer admission -> AccountConfiguration/authenticator/payer/2D nonce/phased calls -> receipt/RPC observability; contrast with 4337/7702 side lanes |

Diagram constraints:

- Use `fireworks-tech-graph` flat technical style, not Mermaid-only output.
- Validate SVG XML and export PNG; if CJK text causes PNG glyph issues, keep SVG as primary and note the render caveat.
- Keep labels short enough for non-AA engineers; put deeper explanations in adjacent prose, not inside diagram nodes.
- The deep draft should include the exact asset paths and mention whether visual self-review was possible.

### item-4: Mantle Decision Frame And Three-Way Recommendation

Build the decision section around the required three-way frame: 「现在实现 / 暂缓观察 / PoC 先行」. The final recommendation must make a clear judgment, not remain at "it depends", while still preserving the conservative baseline that EIP-8130 is Draft and should not be sold as immediate production work. The expected default recommendation is likely `PoC 先行 + 暂缓生产实现`, but the draft must show the evidence that leads there.

- **Priority**: high
- **Dependencies**: item-1, item-2

Required decision table:

| Option | Evaluation lens | Required conclusion content |
|---|---|---|
| 现在实现 | Is the spec stable enough, client/security cost acceptable, and ecosystem ready enough for production engineering? | Explain why immediate production implementation is high risk unless Mantle has an explicit strategic hardfork mandate and accepts Draft churn |
| 暂缓观察 | Would Mantle lose important option value by doing nothing beyond 4337/7702 maintenance? | Define what should be monitored: EIP-8130 spec stabilization, Base mainnet/devnet rollout, OP Stack adoption, wallet/provider support, audits |
| PoC 先行 | Can Mantle cheaply buy learning and prepare decision readiness without production commitment? | Define a bounded PoC using Base implementation as reference, with no user-facing promise, focused on diff sizing, txpool/RPC/receipt feasibility, payer/account config semantics, and developer demo |

Decision guardrails:

- Do not use "Mantle 4337/7702 效果不好" as a premise; use WHI-280's bounded verdict.
- The recommendation must separate protocol mechanism gaps from ecosystem adoption gaps.
- If recommending PoC, explicitly say production implementation should wait for trigger conditions.
- If recommending pause, specify the trigger conditions that would reopen implementation.

### item-5: PoC Roadmap, Reuse Hypothesis, And Engineering Workstreams

If the decision favors `PoC 先行`, define a phased route that Mantle dev teams can evaluate without committing to mainnet production. The roadmap should be concrete enough for engineering planning but not pretend that all scope is known before a Mantle code diff. It should explicitly test how much Base's implementation can be reused and where Mantle-specific OP Stack/op-geth/reth differences may matter.

- **Priority**: high
- **Dependencies**: item-3, item-4

Required phased plan:

| Phase | Goal | Candidate tasks | Exit criteria |
|---|---|---|---|
| Phase 0: Decision prep | Confirm product goal and risk appetite | Pick target scenarios; verify Mantle fork/client constraints; lock source/spec versions; choose PoC network | Written one-page PoC charter with non-production caveat |
| Phase 1: Client diff sizing | Estimate Base-to-Mantle reuse | Compare Base EIP-8130 PR surface against Mantle execution client/RPC/txpool/receipt pipeline; identify hardfork gates and missing modules | Diff map with `reuse / adapt / rewrite / unknown` labels |
| Phase 2: Minimal devnet PoC | Prove one native-AA transaction path | Implement or stub AA tx decode, sender auth, payer auth, simple account config, one phased call, RPC submission, receipt visibility | Local/devnet demo plus test vectors |
| Phase 3: Ecosystem readiness | Test whether protocol feature can become usable | Build SDK/wallet sample, explorer/indexer hooks, sponsor/payer demo, 4337/7702 coexistence story | Developer demo and integration checklist |
| Phase 4: Production decision gate | Decide ship/pause/abandon | Security review, spec drift review, Base rollout review, partner feedback, gas/DoS benchmarks | Go/no-go memo; no default mainnet commitment |

PoC scope boundaries:

- The PoC should not change Mantle mainnet or promise user-facing support.
- It should not replace existing 4337/7702 work; it should test coexistence.
- It should include at least one failure-mode test: invalid authenticator, payer replay/binding issue, account-change cap, phase revert/skip behavior.
- It should produce a reusable checklist for future `final.md` / TW report integration.

### item-6: Risk Register And Trigger Conditions

Create a risk register that can be used by engineering and product decision-makers. The register should cover both "do PoC" and "wait" paths, because a passive wait also has opportunity cost. Each risk must include likelihood/impact, source anchor, mitigation, and the trigger that changes the recommendation.

- **Priority**: high
- **Dependencies**: item-4, item-5

Minimum risks:

| Risk | Why it matters | Required mitigation / trigger |
|---|---|---|
| EIP-8130 Draft/spec drift | Constants, semantics, and Base implementation are still moving | Track spec and Base mainnet/devnet rollout; production gate only after stabilization |
| Client/security complexity | Native AA touches txpool, validation, execution, RPC, receipt, fee settlement | Limit PoC scope, require audit plan, use DoS caps/test vectors |
| Ecosystem maturity | Wallets, SDKs, explorer, provider support may lag | Pair PoC with SDK/demo and partner outreach; no production launch without wallet/provider path |
| Coexistence with 4337/7702 | Mantle already has 4337 and 7702 support; fragmentation risk | Define coexistence matrix and migration path; do not deprecate existing paths |
| Sponsor economics | Native payer does not create demand or subsidy budgets | Keep business/product sponsorship model separate from protocol implementation |
| Base dependency | Reusing Base work may help, but Base route may not map one-to-one to Mantle | Do explicit diff sizing; do not assume copy-paste reuse |

Trigger condition table:

| Trigger | Effect on recommendation |
|---|---|
| EIP-8130 spec reaches stable status or Base locks production constants | Move from `observe` toward expanded PoC / implementation planning |
| Base successfully launches native-AA path on public mainnet/devnet with wallet/provider examples | Raise confidence in OP Stack reuse and ecosystem readiness |
| Mantle product team commits to native payer/session-key/phased-call scenarios not well served by 4337/7702 | Strengthen PoC priority |
| Mantle 4337/7702 metrics materially improve after ecosystem work | Lower urgency for native AA production work |
| Security audit identifies unacceptable client/txpool/payer risks | Pause or abandon implementation path |

### item-7: Draft Structure, Review Hooks, And Final Handoff Requirements

Define the downstream `drafts/round-1.md` structure and review hooks so the adversarial reviewer can quickly check whether the strategy output meets the issue's acceptance criteria. This item should also ensure the later final promotion includes the index proposal for order 8 without Research Agent editing `_index.md` directly.

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6

Proposed draft structure:

1. Executive Summary: one-page recommendation with `PoC 先行 / 暂缓生产实现` or revised final judgment.
2. Evidence Ledger: upstream final paths, commit SHAs, evidence labels and carried caveats.
3. Dev Team Primer: 4337 / 7702 / 8130 mechanism walkthrough.
4. Diagram Section: `three-layer-aa` and `why-8130-native` SVG+PNG paths plus explanation.
5. Mantle Decision Analysis: why current evidence does or does not justify native AA.
6. Three-Way Recommendation: `现在实现 / 暂缓观察 / PoC 先行` table and final choice.
7. PoC Roadmap: phases, workstreams, reuse hypothesis, exit criteria.
8. Risk Register And Trigger Conditions.
9. Coexistence Notes: how 4337, 7702, and native AA should coexist during PoC.
10. Review Checklist And Source Coverage.

Review hooks:

- Check that the final recommendation is explicit and conservative; no hidden immediate-production recommendation.
- Check that every conclusion cites upstream final path and commit SHA.
- Check that the diagrams exist as both SVG and PNG and are referenced from the prose.
- Check that Base-selection statements keep `explicit`, `signal`, `inference`, and `unknown` labels separate.
- Check that the PoC plan has bounded exit criteria and does not mutate `_index.md`.
- Check that the Index Entry Proposal remains: order `8`, dependencies `native-aa-cross-comparison, mantle-aa-status, eip8130-deep-dive`, final path `base-eip8130-native-aa/research-sections/mantle-native-aa-strategy/final.md`.

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| evidence_anchor | Upstream final.md path, commit SHA, and source label supporting each claim | all |
| caveat_preserved | Which upstream caveat must be carried forward without overstatement | all |
| audience_takeaway | One-sentence explanation for Mantle engineers or decision-makers | item-2, item-3, item-4 |
| mechanism_layer | Whether the concept sits at application/infra, EOA enhancement, protocol-native tx/client, or ecosystem/product layer | item-2, item-3, item-4 |
| decision_option | Mapping to 「现在实现 / 暂缓观察 / PoC 先行」 | item-4, item-5, item-6 |
| engineering_workstream | Client, txpool, RPC/receipt, SDK/wallet, explorer/indexer, security, product/ecosystem, or data analytics workstream | item-5, item-6 |
| risk_level | Qualitative likelihood/impact plus mitigation and trigger condition | item-4, item-5, item-6 |
| asset_path | SVG/PNG asset path and render/validation status for architecture diagrams | item-3, item-7 |
| coexistence_impact | How the recommendation interacts with Mantle's existing ERC-4337 and EIP-7702 paths | item-4, item-5, item-6 |
| review_gate | Specific adversarial-review check that must pass before final promotion | item-7 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison / architecture | 三层 AA 架构对照图：show ERC-4337 as application/infra-layer AA, EIP-7702 as EOA enhancement, and EIP-8130 as protocol-native tx/client path; label validation locus, payer/gas path, batching path, and protocol visibility. Output to `assets/three-layer-aa.svg` and `.png`. | fireworks-tech-graph SVG+PNG | item-2, item-3 |
| diag-2 | architecture / flow | "8130 为什么是 native"：show AA typed transaction carrying sender_auth/payer_auth/account_changes/calls, txpool/sequencer admission, AccountConfiguration/authenticator/payer/2D nonce/phased calls, and receipt/RPC observability. Output to `assets/why-8130-native.svg` and `.png`. | fireworks-tech-graph SVG+PNG | item-2, item-3, item-4 |
| diag-3 | roadmap | Optional PoC route diagram: decision prep -> client diff sizing -> minimal devnet PoC -> ecosystem readiness -> production decision gate. Use only if it clarifies the final section without distracting from the required two diagrams. | mermaid or ascii | item-5, item-6 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | accepted_final_sections | Use the three upstream accepted final sections as primary sources, preserving paths and commit SHAs in the evidence ledger. | 3 |
| src-2 | source_traceability | For every recommendation and risk, include upstream final.md path + commit SHA + evidence label (`fact`, `signal`, `inference`, `strategy-judgment`, `unknown`). | 1 table |
| src-3 | diagram_generation_evidence | Record SVG XML validation and PNG export status for the two required fireworks-tech-graph diagrams. | 2 assets |
| src-4 | no_new_research_boundary | State whether any supplemental sources were used; if none, explicitly say the draft is synthesis-first over WHI-280/WHI-281/WHI-276. | 1 note |
| src-5 | acceptance_criteria_mapping | Map the final draft sections to the issue acceptance criteria: primer, two diagrams, three-way recommendation, upstream evidence, PoC/roadmap/risk or pause triggers. | 1 table |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
