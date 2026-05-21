---
topic: "Mantle Proposer Failure 根因分析与 SP1 项目对标"
project_slug: mantle-l2beat-risk-deficiency
topic_slug: mantle-proposer-failure-analysis
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: mantle-l2beat-risk-deficiency/outlines/mantle-proposer-failure-analysis.md
  draft: mantle-l2beat-risk-deficiency/research-sections/mantle-proposer-failure-analysis/drafts/round-{n}.md
  final: mantle-l2beat-risk-deficiency/research-sections/mantle-proposer-failure-analysis/final.md
  index: mantle-l2beat-risk-deficiency/research-sections/_index.md

dependency_context:
  upstream_issue: WHI-49 / l2beat-risk-assessment-framework
  upstream_final_path: mantle-l2beat-risk-deficiency/research-sections/l2beat-risk-assessment-framework/final.md
  upstream_main_commit: 00ed3e5
  use_as: "Background for L2Beat Risk Chart semantics and OP-Succinct template behavior; re-verify Mantle/Morph current project configs from primary sources."

scope: |
  深入分析 Mantle 在 L2Beat Risk Chart 的 Proposer Failure 维度被标红的具体原因，重点对标同样使用 SP1
  或 SP1-adjacent validity proof 技术路线、但在 L2Beat Proposer Failure 上未被标红的 Morph，以及 Scroll、
  ZKsync 等通过项目。研究需要从合约级访问控制、fallback/escape hatch、用户提款路径、L2Beat 源码配置
  四条链路交叉验证，定位导致 Mantle 不合格的 1-3 个核心技术差异。

  本研究只覆盖 Proposer Failure。Exit Window、Sequencer Failure、State Validation、Data Availability、
  Stage 1/2 合规性和改进建议均不展开，除非作为解释 Proposer Failure 影响面的背景脚注。

audience: |
  Mantle 协议工程师、治理/安全团队、Multica 研究 squad 下游建议撰写者，以及需要理解 L2Beat
  Proposer Failure 评级差异的 L2 研究者。读者预期熟悉 L2 output oracle、withdrawal proof、
  proxy/role-based access control、SP1/zkVM validity proof 的基本概念，但不一定熟悉 L2Beat config
  仓库的模板与项目覆盖机制。

expected_output: |
  - Mantle proposer 机制完整技术解析，包含 SuccinctL2OutputOracle / 相关 output oracle 合约的
    `proposeL2Output` 访问控制、proposer 白名单/role 配置、proof verification 路径与升级/owner 权限。
  - L2Beat 标红 Mantle Proposer Failure 的具体原因定位：项目配置、模板路径、最终 RISK_VIEW 常量、
    页面文案与合约事实之间的对应关系。
  - Mantle vs Morph 详细对比表：架构、SP1 使用方式、proposer 权限、fallback、用户提款路径、
    L2Beat risk 配置、评级文案。
  - Scroll、ZKsync 等通过项目的关键做法总结，限定在 Proposer Failure 相关机制。
  - 导致 Mantle 不合格的 1-3 个核心问题，并标注哪些属于链上机制问题、哪些属于 L2Beat 配置/模板问题、
    哪些仍需项目方或 L2Beat 确认。
  - Evidence：一手合约代码、L2Beat 源码配置、Morph 技术文档/合约、必要时 Etherscan verified source。

guardrails:
  - Proposer Failure 判定口径以 WHI-49 final 的 Risk Chart 框架为背景，但 Mantle/Morph 事实必须重新从当前一手源核验。
  - 不把 L2Beat Stage 1/2 阈值混入 Risk Chart Proposer Failure sentiment 判定。
  - 不把 "uses SP1" 简化为评级结论；必须区分 SP1 proof generation、proposer authorization、oracle accept path、user fallback path。
  - 不把治理可升级替换 proposer 等同于用户自助提款；需按 L2Beat good/warning/bad 语义拆分。
  - 对当前链上白名单地址、role admin、owner、guardian、timelock 等动态配置，必须记录来源、抓取日期、链 ID、合约地址和区块/commit。
  - 如果 L2Beat 源码与生产页面、链上合约或项目文档存在冲突，必须显式列出冲突并给出优先级判断。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-21T10:20:00Z"
---

# Research Outline: Mantle Proposer Failure 根因分析与 SP1 项目对标

## Core Research Questions

1. Mantle `SuccinctL2OutputOracle.proposeL2Output` 是否有访问控制？如果有，具体是 `onlyProposer`、role-based access control、owner gate、whitelist mapping，还是其他机制？
2. 当前 Mantle 主网 proposer 白名单/role 配置是什么？有几个可提交方？谁可以增删 proposer？是否经过 timelock 或 multisig？
3. Mantle proposer 停止运作后，用户是否存在 permissionless self-propose、escape hatch、forced withdrawal、guardian/SC 强制出块或治理替换 proposer 路径？
4. Mantle 使用 SP1 的事实链是什么：SP1 proof 只验证 output，还是允许任意证明者把有效 proof 送入 L1 oracle？proof verifier 与 proposer authorization 的先后关系是什么？
5. L2Beat 当前 Mantle 项目配置如何计算 Proposer Failure？是项目 `nonTemplateRiskView` 手动覆盖，还是 OP Stack / OP-Succinct 模板 hardcode？
6. Morph 同样使用 SP1 或 SP1-derived proof infrastructure 时，proposer 合约与 L2Beat 配置为何可以避免 Mantle 的 red outcome？
7. Scroll、ZKsync 等通过项目在 L2Beat 语义下依赖的是 permissionless proposer、governance/SC fallback、escape hatch，还是其他机制？
8. Mantle 不合格的根因应归纳为链上机制缺失、白名单/权限配置过窄、L2Beat 模板保守处理、文档/配置未证明 fallback，还是多因素组合？

## Items

### item-1: Evidence Baseline and L2Beat Proposer Failure Framework Binding

建立本研究的评价基线：只采用 L2Beat Risk Chart 的 Proposer Failure 语义，继承 WHI-49 对
`PROPOSER_CANNOT_WITHDRAW`、`PROPOSER_SELF_PROPOSE_*`、`PROPOSER_USE_ESCAPE_HATCH_*`、
`PROPOSER_WHITELIST_*` 的解释，同时重新核验当前 L2Beat 源码中 Mantle/Morph/对照项目的实际配置。

Investigation fields:
- WHI-49 final 中与 Proposer Failure 直接相关的结论、源码 commit、风险常量与 OP-Succinct 模板路径。
- 当前 L2Beat repo HEAD 或锁定 commit 中：
  - `packages/config/src/common/riskView.ts`
  - `packages/config/src/templates/opStack.ts`
  - `packages/config/src/projects/mantle/*`
  - `packages/config/src/projects/morph/*`
  - Scroll、ZKsync 等对照项目配置文件。
- L2Beat 生产页面 Mantle/Morph risk-analysis 文案是否与源码一致。

Required evidence:
- WHI-49 final path and commit reference.
- l2beat/l2beat exact commit SHA used for this research.
- File/line permalinks for all risk constants and project config references.

Output:
- A short "evaluation rules used in this section" box.
- A source priority table: L2Beat source config > verified contract source/on-chain state > official docs > production UI text > secondary analysis.

Priority: high
Dependencies: WHI-49 final.

### item-2: Mantle SuccinctL2OutputOracle Contract and Proposer Authorization

解析 Mantle L1 output/proof submission path，重点确认 `proposeL2Output` 或等价函数的调用权限、
proof verification 顺序、状态更新条件、proposer role/whitelist 存储和管理权限。

Investigation fields:
- Contract source:
  - `SuccinctL2OutputOracle` implementation source in Mantle repos and/or Etherscan verified source.
  - Any proxy, verifier, registry, owner, role manager, `AddressManager`, `SystemConfig`, `ProxyAdmin`,
    `L1CrossDomainMessenger`, `OptimismPortal` dependencies relevant to withdrawals.
- Function-level analysis:
  - `proposeL2Output` signature, modifiers, explicit `require` gates, proof verification calls, accepted inputs.
  - Whether authorization checks happen before proof verification.
  - Whether a valid SP1 proof from an arbitrary caller is accepted or rejected.
  - How output root index / L2 block number / timestamp monotonicity is enforced.
- Configuration:
  - Current proposer address(es), owner/admin, role admin, multisig/timelock, upgrade path.
  - Whether there is a way to add/remove proposers without upgrading the oracle.

Required evidence:
- GitHub source from `mantlenetworkio/mantle-v2` and/or Etherscan verified source.
- Deployment address and chain for each referenced contract.
- Line-level code references for every access-control claim.
- On-chain storage/config evidence for current proposer list or role members where available.

Output:
- "Mantle proposer path" technical narrative.
- Function access-control table:
  | Function | Caller restriction | Proof verification | State mutation | Admin/fallback path |
- Mermaid flowchart: sequencer/batcher/output derivation -> SP1 proof generation -> whitelisted proposer -> L1 oracle -> withdrawal proof availability.

Priority: high
Dependencies: item-1.

### item-3: Mantle Failure Mode and User Withdrawal Path Under Proposer Outage

Model what happens when the authorized Mantle proposer(s) stop submitting outputs. This item must separate
"operator/governance can eventually recover" from "user can independently withdraw" because L2Beat Proposer Failure
centers on user self-help.

Investigation fields:
- Withdrawal dependency chain:
  - L2 withdrawal initiation, L2 output root requirement, proof finalization, L1 portal finalization.
  - Whether stale output roots can help users withdraw after proposer outage, and only for which pre-outage state.
  - Whether new withdrawals initiated after the last output root can ever be proven without a new output.
- Fallback/escape-hatch search:
  - Permissionless `proposeL2Output` or alternate `submitProof` route.
  - Timeout after which whitelist drops.
  - Governance/security council proposer replacement.
  - Emergency withdrawal / escape hatch independent of output oracle.
  - Force-inclusion path interaction, if any; explicitly avoid confusing Sequencer Failure with Proposer Failure.
- Impact analysis:
  - Asset classes affected.
  - Duration of freeze under current admin/upgrade path.
  - Difference between "temporary freeze until governance acts" and "L2Beat bad because users cannot self-withdraw."

Required evidence:
- Mantle bridge/portal/oracle contracts and docs.
- L2Beat risk constant descriptions from item-1.
- If fallback is absent, record exact negative evidence searched: functions, docs, repo paths, and keywords.

Output:
- Fault tree: proposer stops -> no new L2 output -> withdrawal proof cannot reference post-outage state -> user outcome.
- A crisp answer to "Mantle 是否存在 proposer 失效后的 fallback/escape hatch 机制？"

Priority: high
Dependencies: item-2.

### item-4: L2Beat Mantle Risk Configuration and Exact Red Reason

Trace Mantle from L2Beat project config through template logic to the final Proposer Failure risk view shown on L2Beat.
The goal is to locate the exact code/data path that produces the red Proposer Failure state.

Investigation fields:
- Mantle project file(s) in `l2beat/l2beat`:
  - stack/template invocation;
  - `nonTemplateRiskView.proposerFailure`, if present;
  - discovery references to `OPSuccinctL2OutputOracle`, `OptimismPortal`, `respectedGameType`, output oracle, verifier.
- Template path:
  - Whether Mantle is classified as `OpSuccinct`, `OpSuccinctFDP`, `Permissioned`, `None`, or another proof type.
  - Whether `getRiskViewProposerFailure` directly returns `PROPOSER_CANNOT_WITHDRAW`.
  - Whether any project-specific override could change this.
- Production/UI cross-check:
  - L2Beat Mantle risk-analysis page text and value.
  - Whether page matches source constant text.

Required evidence:
- L2Beat repo commit SHA.
- File/line references for Mantle project config and template branch.
- L2Beat production page snapshot/fetch date.

Output:
- Exact "why red" paragraph:
  "Mantle is red because [config/template branch] maps [proof/oracle condition] to [RISK_VIEW constant], whose L2Beat semantics are [description]."
- Code-path diagram or bullet trace:
  `mantle.ts` -> template -> fraud/proof type detection -> `RISK_VIEW.PROPOSER_CANNOT_WITHDRAW`.

Priority: high
Dependencies: item-1 and item-2.

### item-5: Morph Proposer Mechanism and L2Beat Passing Logic

Analyze Morph as the core comparison case. The research must determine whether Morph passes because its proposer path is
permissionless, because it has a fallback/escape hatch, because L2Beat config treats it differently, or because "uses SP1"
means something different in Morph's architecture.

Investigation fields:
- Morph contract source:
  - L1 rollup / state commitment / batch proof / verifier / challenge/finalization contracts.
  - Proposer, sequencer, relayer, prover roles and whether any caller can submit a valid proof.
  - SP1 integration points and whether SP1 proof acceptance is permissionless.
- Morph docs:
  - Official architecture/proof/finality/proposer docs.
  - Any emergency exit, forced transaction, or withdrawal liveness mechanism.
- L2Beat Morph config:
  - Project file, template used, `riskView.proposerFailure`, `nonTemplateRiskView`, discovery values.
  - Final displayed Proposer Failure sentiment and text.
- Contrast with Mantle:
  - Same/different SP1 usage.
  - Same/different authorization gate before proof verification.
  - Same/different fallback semantics.

Required evidence:
- `morph-l2/morph` repo contract references.
- Morph official docs references.
- L2Beat Morph config file/line references.
- If Morph is not actually SP1 in the relevant L2Beat path, state that explicitly and adjust comparison.

Output:
- Detailed Mantle vs Morph table:
  | Dimension | Mantle | Morph | Why it matters for L2Beat Proposer Failure |
- Direct answer to "Morph 是否允许任何人提交有效 ZK proof?"
- Mermaid architecture comparison diagram.

Priority: high
Dependencies: item-1.

### item-6: Other Passing Project Benchmarks

Use Scroll, ZKsync, and optionally one OP/fraud-proof project as control cases to avoid overfitting the conclusion to
Morph. The goal is to summarize which concrete mechanisms L2Beat treats as sufficient to avoid red Proposer Failure.

Candidate projects:
- Scroll: validity proof / prover and finalization model; determine L2Beat Proposer Failure risk value.
- ZKsync Era: zkStack default or project override, likely governance/validator fallback; verify from source.
- Optimism/Base: permissionless fault-proof self-propose path, useful as non-SP1 green control.
- Arbitrum One BoLD: permissionless validator/self-propose path, useful as different stack control.

Investigation fields:
- Project config and riskView constant for each project.
- Whether the passing status is good or warning.
- Mechanism class:
  - permissionless self-propose;
  - escape hatch;
  - governance/SC proposer replacement;
  - validator set / PoS;
  - other.
- Whether the mechanism helps users independently withdraw or only gives trusted recovery.

Required evidence:
- L2Beat project config file/line references.
- Contract or official docs only where needed to explain the mechanism; avoid full unrelated architecture digressions.

Output:
- Proposer Failure comparison table.
- Mermaid table summarizing project, stack, sentiment, constant, mechanism, evidence.
- Short "patterns that pass" list and "patterns that remain red" list.

Priority: medium
Dependencies: item-1.

### item-7: Root Cause Synthesis and Residual Gaps

Synthesize 1-3 root causes explaining why Mantle is not qualified under L2Beat Proposer Failure while Morph/others pass.
This item should be concise, evidence-linked, and careful about uncertainty.

Candidate root-cause buckets to test:
- Mantle requires a whitelisted proposer even when a valid SP1 proof exists, so proof validity alone does not create permissionless liveness.
- Mantle lacks a user-accessible fallback/escape hatch or whitelist-drop timeout that lets users withdraw if proposers stop.
- L2Beat's OP-Succinct template conservatively maps Mantle-like configurations to `PROPOSER_CANNOT_WITHDRAW`, and Mantle has no project-specific override/evidence proving a stronger fallback.

Required synthesis discipline:
- Each root cause must cite at least one Mantle contract fact and one L2Beat config/constant fact.
- If Morph is used as a counterexample, cite Morph contract/config facts in the same paragraph.
- Label unresolved items as "needs confirmation" rather than implying facts.
- Keep recommendations out of scope; only state implications for later recommendation issue.

Output:
- Root cause table:
  | Root cause | Evidence | Compared project evidence | Confidence | What would falsify it |
- Final answer bullets for the four dispatch key questions.

Priority: high
Dependencies: items 2-6.

## Source Plan

### Primary Sources

1. Mantle:
   - `mantlenetworkio/mantle-v2` contracts and deployment/config files.
   - `mantlenetworkio/op-geth` only if needed to interpret withdrawal/state-root derivation dependencies.
   - Etherscan verified Mantle L1 contracts for deployed implementation and proxy state.
2. L2Beat:
   - `https://github.com/l2beat/l2beat` at an exact commit.
   - `packages/config/src/common/riskView.ts`.
   - `packages/config/src/templates/opStack.ts` and any relevant stack templates.
   - `packages/config/src/projects/mantle/*`, `morph/*`, `scroll/*`, `zksync/*`, `optimism/*`, `base/*`, `arbitrum/*`.
3. Morph:
   - `morph-l2/morph` contracts and deployment/config files.
   - Morph official technical docs for rollup/proof/proposer/withdrawal architecture.
4. WHI-49 final:
   - `mantle-l2beat-risk-deficiency/research-sections/l2beat-risk-assessment-framework/final.md`.

### Secondary Sources

- L2Beat Mantle and Morph production project pages for UI text cross-check.
- L2Beat forum methodology posts only if a specific Risk Chart interpretation is disputed.
- Project blog posts only when official docs or code do not explain SP1 integration.

### Evidence Capture Requirements

- Record source type, URL/path, commit SHA or fetch date, and line numbers where possible.
- For chain state/config claims, record chain, contract address, method/storage field, and fetch date/block if available.
- For negative claims ("no fallback found"), record searched files/keywords and why the search would likely find such a mechanism if present.

## Diagram Plan

### diag-1: Mantle Current Proposer Flow

Mermaid flowchart showing:
`L2 blocks/batches` -> `output derivation` -> `SP1 proof generation` -> `authorized proposer` -> `SuccinctL2OutputOracle.proposeL2Output` -> `L1 output root accepted` -> `withdrawal proof/finalization`.

Must include explicit red gate for proposer authorization before/around proof verification if confirmed by item-2.

### diag-2: Mantle vs Morph Proposer Architecture

Mermaid flowchart or two-lane diagram comparing:
- who can generate proof;
- who can submit proof/output;
- what L1 contract verifies;
- what fallback exists when primary proposer stops;
- what L2Beat risk constant results.

### diag-3: Proposer Failure Project Rating Comparison

Mermaid-compatible table or markdown table covering at least Mantle, Morph, Scroll, ZKsync, Optimism/Base, Arbitrum One:
project, stack, proof/fallback class, L2Beat sentiment, risk constant, key evidence.

### diag-4: Mantle Proposer Outage Fault Tree

Mermaid graph showing:
proposer outage -> no new accepted output root -> post-outage withdrawal cannot be proven -> possible recovery branches
(governance replacement / upgrade / permissionless proof / escape hatch) with absent/present labels.

## Draft Structure

1. Executive Summary
   - 3-5 bullets with Mantle red reason, Morph contrast, and root causes.
2. Evaluation Baseline
   - WHI-49 binding, L2Beat source priority, terminology.
3. Mantle Contract-Level Analysis
   - `SuccinctL2OutputOracle`, proposer roles, deployed config, withdrawal dependency.
4. Mantle L2Beat Config Trace
   - exact source path from config/template to displayed red risk.
5. Morph Deep Comparison
   - contract/config/docs analysis and detailed table.
6. Other Passing Benchmarks
   - Scroll, ZKsync, Optimism/Base, Arbitrum or equivalent.
7. Root Causes
   - 1-3 core problems with evidence and confidence.
8. Key Questions Answered
   - Direct answers to the four dispatch questions.
9. Evidence Appendix
   - Source table, code permalinks, chain config references, searched-negative-evidence log.

## Quality Checklist

- [ ] Mantle `proposeL2Output` access-control answer is based on line-level code, not docs.
- [ ] Current proposer whitelist/role configuration is sourced from deployed contracts or authoritative config.
- [ ] Mantle failure-mode analysis distinguishes pre-outage withdrawals from post-outage withdrawals.
- [ ] L2Beat Mantle red reason is traced through source files to a named `RISK_VIEW` constant.
- [ ] Morph comparison verifies whether proof submission is permissionless at the L1 contract boundary.
- [ ] "Same SP1" claims are decomposed into proof generation, proof verification, and output submission permissions.
- [ ] Other-project benchmarks classify good vs warning separately; both are "not red" but not equivalent.
- [ ] All dynamic facts include fetch date/block/commit.
- [ ] All diagrams map to evidence-backed claims in the text.
- [ ] Recommendations are explicitly deferred to the recommendation-proposal issue.

## Open Risks for Review

- Morph's current L2Beat configuration may not map cleanly to "SP1 project" if L2Beat models it under a different stack or proof category; the draft must report that if found.
- Mantle deployed implementation may differ from the repository source branch; Etherscan verified source or deployment metadata should resolve this.
- L2Beat config may have changed after WHI-49's source commit; this research must record the exact commit used and explain any drift.
- If current on-chain proposer role enumeration is not directly available from public contract methods, the draft may need event-log or storage-slot evidence; confidence should be downgraded if only docs/config are available.
