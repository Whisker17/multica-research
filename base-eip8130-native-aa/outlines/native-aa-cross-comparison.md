---
topic: "native AA 方案横向对比（8130 vs 4337 vs 7702 vs 7560/7701）"
project_slug: "base-eip8130-native-aa"
topic_slug: "native-aa-cross-comparison"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "base-eip8130-native-aa/outlines/native-aa-cross-comparison.md"
  draft: "base-eip8130-native-aa/research-sections/native-aa-cross-comparison/drafts/round-{n}.md"
  final: "base-eip8130-native-aa/research-sections/native-aa-cross-comparison/final.md"
  index: "base-eip8130-native-aa/research-sections/_index.md"

scope: "将已完成的 WHI-275~WHI-280 final sections 汇总为横向对比与裁决：按 WHI-275 rubric D1~D13 形成方案 x 维度主矩阵，抽取 3~4 张原理分组视图，回答用户 Q1（8130 vs 4337/7702 的原理区别与优势）与 Q4（Base 为何选 8130 的裁决）。本 issue 不引入新调研；所有结论必须回溯到输入 final section 路径、已有 commit SHA 或明确标注为未独立验证。"
audience: "Mantle dev teams、协议工程师、钱包/AA infra 工程师、产品与技术决策者、Research Review Agent、Technical Writer Agent。读者熟悉 EVM/L2 与账户抽象基础，需要一份可审查、可决策的横向矩阵和 Base 选型裁决。"
expected_output: "横向对比主矩阵（方案 x D1~D13）+ 3~4 张原理分组视图（突出 8130 vs 4337 vs 7702 的原理性分野）+ 「Base 为何选 8130」裁决（保留「明确陈述 / 合理推断 / 未发现明确理由」标签）+ 各方案适用边界表（含未独立验证项标注）。"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-27T02:26:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-27T02:26:00Z"

multica_issue_id: "97c9c1e3-020f-48c6-a6aa-9f7b7b13801c"
report_issue_id: "fc840c0d-ac87-41c8-b1ae-6d1318b8eaba"
branch_name: "research/base-eip8130-native-aa/native-aa-cross-comparison"
base_commit: "60e395a5b4e7ac967b39261e7fe9ba078dc7079d"
language: "zh-CN"
research_depth: "synthesis"
source_boundary: "accepted-final-sections-only; no-new-research"
primary_inputs:
  - "base-eip8130-native-aa/research-sections/native-aa-framework/final.md"
  - "base-eip8130-native-aa/research-sections/eip8130-deep-dive/final.md"
  - "base-eip8130-native-aa/research-sections/erc4337-mechanism-limits/final.md"
  - "base-eip8130-native-aa/research-sections/eip7702-mechanism-limits/final.md"
  - "base-eip8130-native-aa/research-sections/post7702-native-aa-landscape/final.md"
  - "base-eip8130-native-aa/research-sections/mantle-aa-status/final.md"
---

# Research Outline: native AA 方案横向对比（8130 vs 4337 vs 7702 vs 7560/7701）

## Items

### item-1: Source Corpus Lock And Evidence Normalization

Lock the allowed source corpus to the six accepted final sections named in `primary_inputs`, and normalize their evidence levels before any synthesis. This item prevents the cross-comparison draft from silently introducing fresh web/code claims or upgrading earlier caveats into final facts. The deep draft must produce a compact source ledger showing each input final section path, its promoted draft/final commit metadata when available in frontmatter, and the exact caveats that must be carried forward.

- **Priority**: high
- **Dependencies**: none

Required output details:

| Input section | Required extraction | Must preserve |
|---|---|---|
| `native-aa-framework/final.md` | taxonomy, D1~D13 rubric definitions, D12/D13口径, four-metric effectiveness rules | Mantle效果不能预设为差；Base motivation remains inferred unless explicitly sourced |
| `eip8130-deep-dive/final.md` | 8130 mechanism row, Base implementation path, PR signal categories, D1~D13 row | Draft/spec drift caveat; Base selection motive is implementation-inferred |
| `erc4337-mechanism-limits/final.md` | 4337 mechanism limits, infra/bundler/paymaster evidence, Mantle/Base/Arbitrum UserOp data | 4337 is mature and not a failed scheme; Ethereum table coverage caveat |
| `eip7702-mechanism-limits/final.md` | 7702 capability boundary, EOA-delegation benefits/risks, D1~D13 row, 7702/8130 composition correction | 8130 does not reuse 7702 `SignedAuthorization` as main auth model |
| `post7702-native-aa-landscape/final.md` | RIP-7560 package, EIP-8141, EIP-7701, historical/adjacent routes, Base/OP evidence labels | keep `explicit-public-statement`, `code-pr-signal`, `design-doc-signal`, `roadmap-signal`, `inference`, `unknown` labels |
| `mantle-aa-status/final.md` | Mantle 4337/7702 current support, adoption verdict, DX/provider matrix, native-AA decision inputs | "效果一般 / 部分指标偏弱, 7702 aggregate unknown"; normalized ratio is fragile |

Quality gates:

- Do not cite any fact in the deep draft unless it comes from one of the six input final sections, or is clearly marked `not independently revalidated in this synthesis`.
- Preserve each upstream section's own evidence language: `spec-cited`, `code-cited`, `data-cited`, `inferred`, `unknown`, `explicit-public-statement`, `code-pr-signal`, `design-doc-signal`, `roadmap-signal`, `inference`.
- If two input sections disagree, report the conflict as a conflict instead of reconciling by invention.
- Add a short "synthesis-only boundary" note to the draft executive summary.

### item-2: Master Cross-Comparison Matrix By D1~D13

Build the main decision artifact: a scheme x D1~D13 matrix covering ERC-4337, EIP-7702, EIP-8130, RIP-7560 package, EIP-8141, EIP-7701, and the historical/adjacent schemes that affect the decision narrative. Each matrix cell must be concise enough for decision use but traceable enough for adversarial review.

- **Priority**: high
- **Dependencies**: item-1

Matrix rows:

| Row class | Schemes | Treatment |
|---|---|---|
| Active baseline | ERC-4337, EIP-7702 | Full D1~D13 row, reused from final sections; mark mature/deployed status and limits |
| Base route | EIP-8130 | Full D1~D13 row; mark Draft + Base active implementation + remaining open/unstable items |
| Native alternatives | RIP-7560 package, EIP-8141 | Full D1~D13 row; use post-7702 final as primary source |
| Withdrawn historical route | EIP-7701, EIP-2938, EIP-3074, EIP-5003 | Condensed row or appendix row; enough to explain why not current route |
| Adjacent post-7702 lifecycle | EIP-7851, EIP-7377, EIP-5806 where useful | Condensed row focused on D1/D2/D4/D8/D9/D11 |

Cell format:

```text
{short value} | evidence={source label} | anchor={input section path + section heading} | caveat={none or carried caveat}
```

Minimum matrix columns:

| D# | Dimension | Required synthesis angle |
|---|---|---|
| D1 | 抽象层级 | application-layer vs EOA enhancement vs protocol-native vs historical/adjacent |
| D2 | 协议改动范围 | no consensus change, new tx type, frames, AccountConfiguration, opcodes, hardfork/RPC/receipt |
| D3 | 基础设施依赖 | bundler/EntryPoint/paymaster/alt mempool vs client/RPC/canonical authenticator vs frame validation |
| D4 | 所有权与密钥模型 | EOA root key, contract-defined validation, actor/authenticator/scope, frame approval |
| D5 | Gas 代付 | 4337 paymaster, 7702 sponsor pattern, 8130 payer/payer_auth, RIP paymaster, 8141 payment approval |
| D6 | 批量原子性 | account calldata, delegate batching, phased calls, execution frames, atomic frame batch |
| D7 | Nonce 与防重放 | protocol nonce, UserOp nonce, 7702 authorization nonce, 2D nonce, keyed nonce, nonce-free expiry |
| D8 | EOA 兼容与迁移 | new smart account, original-address delegation, implicit EOA path, ECDSA-disable adjacent paths |
| D9 | 签名灵活性与 PQ | contract arbitrary validation, canonical authenticator set, P256/PQ frame signatures, root ECDSA residual |
| D10 | 成熟度与生态 | Final/deployed, Draft active, Base PR signal, CFI not scheduled, withdrawn |
| D11 | 安全攻击面 | bundler/paymaster DoS, persistent delegation, authenticator bug, canonical-set governance, arbitrary validation trace complexity |
| D12 | Mantle 适配成本 | existing 4337/7702 support vs OP Stack/client/RPC/hardfork cost; mark Mantle-code gaps |
| D13 | 目标用户/产品场景 | consumer wallet, gasless/stablecoin payment, enterprise/multisig, DeFi batching, cross-chain, PQ |

Quality gates:

- Every active/current candidate row must cover all D1~D13 cells.
- Withdrawn/adjacent rows may be condensed, but must explain why they are not current full-native-AA candidates.
- D12 must not say "Base already implemented, so Mantle can copy"; use the D12 checklist from `native-aa-framework/final.md`.
- D13 must be scenario-based, not scheme-preference-based.

### item-3: Principle Group Views For 8130 vs 4337 vs 7702

Produce 3~4 focused principle views that answer user Q1: how EIP-8130 differs from ERC-4337 and EIP-7702 at the mechanism level, and why those differences matter. These views should be readable as standalone diagrams/tables and should avoid merely repeating the D1~D13 matrix.

- **Priority**: high
- **Dependencies**: item-2

Required views:

| View ID | Focus | Required contrast |
|---|---|---|
| view-1 | Abstraction layer and validation locus | 4337: UserOp + EntryPoint contract + bundler simulation; 7702: EOA set-code delegation; 8130: typed AA transaction + AccountConfiguration + actor/authenticator |
| view-2 | Infrastructure and mempool admission | 4337 alt mempool/bundler; 7702 normal typed tx but delegate-code risk; 8130 txpool-visible auth/payer/nonce/account_changes and bounded/canonical authenticator admission |
| view-3 | Ownership/key model and EOA migration | 4337 smart account owner model; 7702 residual EOA root key + delegate code; 8130 actor/scope/authenticator + implicit EOA/delegation/account changes |
| view-4 | Gas sponsorship and batching | 4337 paymaster + account calldata; 7702 application sponsor/delegate batching; 8130 native payer/payer_auth + phased calls |

Draft guidance:

- Use compact Markdown tables plus Mermaid or ASCII diagrams.
- Make the causal difference explicit: which layer observes validation, which component pays gas, which actor controls account changes, and which failure modes are shifted.
- Include one "what this does not solve" row for each scheme to avoid sales language.
- Use 8130's advantage language carefully: "more protocol-visible / bounded / native to txpool" rather than "universally better."

### item-4: Base Selection Verdict With Evidence Labels

Synthesize the "Base 为什么选 8130" answer without overstating evidence. The deep draft must separate what Base/OP publicly said, what implementation/PR/design-doc signals show, what is a reasonable inference, and what remains unknown. This item directly answers user Q4 and must preserve WHI-279's label discipline.

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

Required verdict sections:

1. **明确陈述**: Only include statements that upstream final sections label as `explicit-public-statement` or direct design-doc text. The OP design-doc PR comment comparing 8130 and 8141 can be summarized here if it was already captured in `post7702-native-aa-landscape/final.md`.
2. **代码 / PR / design-doc 信号**: Summarize Base's EIP-8130 implementation pipeline as `code-pr-signal` and OP adoption/FMA material as `design-doc-signal`; do not call these official "rejection reasons."
3. **合理推断**: Explain why 8130 likely fit Base/OP constraints: bounded validation, top-level authenticator visibility, txpool/sequencer ingress control, AccountConfiguration/payer/phased-call product surface, OP Stack rollout path, and lower short-term uncertainty than 8141.
4. **未发现明确理由**: State that no public full selection memo was found that formally rejects RIP-7560 or EIP-8141, unless such a memo exists in input finals; since this synthesis does no new research, preserve the upstream "未发现" conclusion.

Verdict matrix format:

| Claim | Label | Source anchor | Confidence | Caveat |
|---|---|---|---|---|
| 8130 explicitly declares authenticator/verifier, making validation method visible to nodes | 明确陈述 | `post7702-native-aa-landscape/final.md` OP #378 comment summary | high | quote/paraphrase from upstream final, not new quote |
| Base implemented tx type, AccountConfiguration, txpool/RPC/receipt/estimateGas/phased calls | code-pr-signal | `eip8130-deep-dive/final.md` and `post7702.../final.md` | high | implementation signal, not selection memo |
| Base likely preferred bounded admission over arbitrary validation simulation | 合理推断 | same anchors | medium-high | not an official Base statement |
| Base formally rejected RIP-7560/EIP-8141 | 未发现明确理由 | `post7702.../final.md` | unknown | do not infer rejection |

Quality gates:

- Do not write "Base 发现 4337/7702 效果不好所以转向 8130" as a fact.
- Phrase the final裁决 as a constrained recommendation: "Based on available public evidence, the strongest defensible explanation is..."
- Carry the Draft/status risks for EIP-8130 and EIP-8141.

### item-5: Scheme Applicability Boundary Table

Produce a decision-facing table that says where each scheme is strongest, where it is weak, and what evidence remains unverified for Mantle. This is the main bridge from mechanism comparison to WHI-282 strategy.

- **Priority**: high
- **Dependencies**: item-2, item-4

Required rows:

| Scheme | Strong fit | Weak fit / limits | Mantle relevance | Unverified / caveat |
|---|---|---|---|---|
| ERC-4337 | mature smart accounts, paymaster, gasless onboarding, SDK ecosystem | alt mempool/bundler dependency, EOA address migration, paymaster ops | Mantle already has active but small/sponsor-heavy usage | rejected UserOps/provider SLA not visible |
| EIP-7702 | original EOA address, delegation, batching UX, short/medium-term wallet bridge | not full native AA, residual ECDSA root key, no native payer lifecycle | Mantle op-geth/live sample support exists | aggregate adoption unknown |
| EIP-8130 | protocol-visible validation, payer, actor/scope, 2D nonce, phased calls, Base-aligned OP Stack experimentation | Draft, high client/tooling/security cost, canonical-set governance | relevant if Mantle wants native account/payer semantics and lower bundler dependence | Mantle adaptation cost not fully code-diffed in this issue |
| RIP-7560 | 4337 mental model native-ized for rollups, paymaster/account validation continuity | arbitrary validation/mempool sandbox complexity, no Base implementation signal | possible if Mantle wants 4337-compatible native route | public Base/OP rejection not found |
| EIP-8141 | general frame abstraction, flexible validation/payment, stronger long-term PQ narrative | Draft/CFI, higher mempool/trace complexity, broad protocol surface | long-term L1-aligned route to watch | not scheduled; short-term L2 rollout risk |
| EIP-7701 / historical | explains route evolution into 8141 | withdrawn | background only | not a current adoption candidate |
| EIP-7851 / adjacent | improves 7702 lifecycle / ECDSA-disable story | not full native AA | possible future 7702 complement | not enough for Mantle native-AA decision alone |

Applicability principles:

- Keep "scheme fit" separate from "Mantle should implement now."
- Mark every row with upstream evidence source and `unverified` notes.
- Do not rank by a single score; if scoring is needed, use per-scenario fit rather than global winner.

### item-6: Mantle Decision Inputs And Effectiveness Caveats

Integrate Mantle-specific evidence from the accepted Mantle status section into the cross-comparison. The goal is to prevent the final draft from treating "current 4337/7702效果不好" as a premise instead of a bounded finding.

- **Priority**: high
- **Dependencies**: item-1, item-5

Required synthesis points:

- Mantle ERC-4337 is active but small and sponsor-heavy: 11,479 UserOps, 1,107 smart accounts, 66 bundle senders, 3 paymasters, 98.28% sponsored, 99.85% success for the cited 2026 YTD window.
- Normalized UserOps / 100 canonical tx did not support a simple "significantly worse than Base" conclusion, but this ratio is fragile because absolute volume is small.
- Mantle EIP-7702 has op-geth plumbing and at least one live type `0x04` transaction sample; aggregate adoption remains unknown.
- The effectiveness verdict is "效果一般 / 部分指标偏弱, 7702 聚合采用证据不足", not "proved bad."
- Native AA can address protocol-visible validation, native payer, txpool/RPC observability, and lower bundler dependence, but it does not automatically solve wallet distribution, application demand, sponsor economics, or SDK docs.

Required output:

| Decision input | Evidence from Mantle status | Implication for native-AA decision | Caveat |
|---|---|---|---|
| protocol-visible account/payer semantics gap | 4337/7702 limitations and sponsor-heavy usage | strengthens case for evaluating 8130-style native semantics | not proof that current AA failed |
| infra/ecosystem gap | provider matrix uneven | native AA needs ecosystem plan too | protocol change alone not enough |
| adoption data gap | 7702 aggregate unknown | need future analytics before hard conclusion | synthesis does not add new data |

### item-7: Draft Structure, Review Hooks, And Downstream Handoff

Define the final deep draft structure and review hooks so the Adversarial Agent can check coverage quickly. This item should produce the proposed section outline for `drafts/round-1.md`, plus explicit "what to inspect" notes.

- **Priority**: medium
- **Dependencies**: item-2, item-3, item-4, item-5, item-6

Proposed draft structure:

1. Executive Summary: one-page answer to Q1 and Q4, with evidence-boundary note.
2. Source Corpus And Evidence Labels: accepted final sections only; no new research.
3. Master Matrix: scheme x D1~D13, with source anchors and caveats.
4. Principle Views: 8130 vs 4337 vs 7702 across layer/admission/key model/sponsorship-batching.
5. Base Selection Verdict: 明确陈述 / code-pr-design signals / 合理推断 / 未发现明确理由.
6. Applicability Boundaries: scheme by scenario and unverified items.
7. Mantle Decision Inputs: current AA status, effectiveness caveats, what native AA would and would not solve.
8. Gap Analysis: remaining unknowns for final report and WHI-282.
9. Source Coverage Table and Patch Log.

Review hooks:

- Check whether every D1~D13 active-candidate cell has source anchor/caveat.
- Check whether Base selection claims preserve labels and do not convert inference into official reason.
- Check whether Mantle current-AA verdict preserves "mixed/partial" conclusion.
- Check whether historical/adjacent schemes are not over-promoted into current choices.
- Check whether all required outputs from dispatch are present: main matrix, 3~4 principle views, Base裁决, applicability table, unverified markers.

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| source_anchor | Input final section path and section heading that supports the claim; use commit metadata from frontmatter where available. | all |
| evidence_label | One of `spec-cited`, `code-cited`, `data-cited`, `explicit-public-statement`, `code-pr-signal`, `design-doc-signal`, `roadmap-signal`, `inference`, `unknown`, or `not-independently-validated`. | all |
| matrix_value | The concise D1~D13 cell value or scheme-boundary value used in the final matrix. | item-2, item-5 |
| caveat_or_unknown_reason | Required caveat for any inferred, unknown, Draft, withdrawn, or Mantle-specific unverified claim. | all |
| scheme_class | `active-baseline`, `base-route`, `native-alternative`, `withdrawn-historical`, or `adjacent-post7702`. | item-2, item-5 |
| principle_difference | Mechanism-level contrast that explains why the schemes differ, not just whether one scores higher. | item-3 |
| verdict_label | `明确陈述`, `代码/PR/design-doc 信号`, `合理推断`, or `未发现明确理由`. | item-4 |
| mantle_implication | What the comparison implies for Mantle specifically, separated from generic protocol merit. | item-5, item-6 |
| unverified_marker | Explicit marker for items not independently rechecked in this synthesis or dependent on future code/data review. | all |
| downstream_handoff_note | Short note for WHI-282 / Technical Writer about what conclusion can safely be reused and what must stay qualified. | item-7 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Master scheme x D1~D13 matrix; can be a Markdown table with compact cells and source/caveat markers. | ascii | item-2 |
| diag-2 | architecture | Validation/admission path comparison: ERC-4337 UserOp/Bundler/EntryPoint, EIP-7702 set-code delegation, EIP-8130 typed AA tx + AccountConfiguration/authenticator. | mermaid | item-3 |
| diag-3 | flow | Sponsorship and batching flow: 4337 Paymaster + account calldata, 7702 sponsor/delegate wallet, 8130 payer/payer_auth + phased calls. | mermaid | item-3 |
| diag-4 | comparison | Base selection evidence ladder: explicit statement -> design-doc signal -> code-pr signal -> inference -> unknown. | ascii | item-4 |
| diag-5 | comparison | Applicability boundary table by scheme and user/product scenario. | ascii | item-5 |
| diag-6 | flow | Mantle decision funnel: current 4337/7702 status -> mechanism gaps -> ecosystem gaps -> native-AA implementation decision. | mermaid | item-6 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | accepted_research_section | Framework/rubric final section: `base-eip8130-native-aa/research-sections/native-aa-framework/final.md`. | 1 |
| src-2 | accepted_research_section | EIP-8130 deep-dive final section: `base-eip8130-native-aa/research-sections/eip8130-deep-dive/final.md`. | 1 |
| src-3 | accepted_research_section | ERC-4337 mechanism/limits final section: `base-eip8130-native-aa/research-sections/erc4337-mechanism-limits/final.md`. | 1 |
| src-4 | accepted_research_section | EIP-7702 mechanism/limits final section: `base-eip8130-native-aa/research-sections/eip7702-mechanism-limits/final.md`. | 1 |
| src-5 | accepted_research_section | Post-7702 native AA landscape/Base selection final section: `base-eip8130-native-aa/research-sections/post7702-native-aa-landscape/final.md`. | 1 |
| src-6 | accepted_research_section | Mantle AA status final section: `base-eip8130-native-aa/research-sections/mantle-aa-status/final.md`. | 1 |
| src-7 | source_traceability | Every active/current candidate matrix row includes source anchors to one or more of src-1 through src-6. | 1 |
| src-8 | caveat_preservation | Every upstream caveat relevant to Base selection, Draft status, Mantle effectiveness, or unverified adoption is carried into the draft or gap analysis. | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
