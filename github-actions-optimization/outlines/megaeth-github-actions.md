---
topic: "MegaETH GitHub Actions 完整调研"
project_slug: github-actions-optimization
topic_slug: megaeth-github-actions
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: "github-actions-optimization/outlines/megaeth-github-actions.md"
  draft: "github-actions-optimization/research-sections/megaeth-github-actions/drafts/round-{n}.md"
  final: "github-actions-optimization/research-sections/megaeth-github-actions/final.md"
  index: "github-actions-optimization/research-sections/_index.md"

scope: >
  Full audit of GitHub Actions and repo-level configurations across two MegaETH
  repositories (mega-evm and stateless-validator). Focus areas: (1) claude.yml AI
  integration pattern present in both repos, (2) build-and-test.yml CI pipeline
  design, (3) coverage.yml code coverage approach, (4) doc-audit.yml documentation
  audit workflow (rare type), (5) release.yml / release-tracing.yaml release strategy.
  For each workflow: enumerate all files under .github/workflows/, record
  .github/dependabot.yml, CODEOWNERS, .github/pull_request_template.md (check both
  case variants: uppercase PULL_REQUEST_TEMPLATE.md and lowercase pull_request_template.md); attempt
  branch protection rules, GitHub Apps, and secrets names via public API — mark
  inaccessible items as "inaccessible (permission-limited)" with attempted method
  noted. Classify findings along 10 improvement dimensions with maturity ratings
  (mature / basic / missing). Note commit SHA for all findings.

audience: >
  Mantle engineering team evaluating GitHub Actions patterns from peer projects
  for adoption. Readers are familiar with CI/CD and GitHub Actions concepts.

expected_output: >
  Structured document containing: (1) complete workflow file list for both repos,
  (2) repo-level config summary, (3) 10-dimension capability matrix with maturity
  ratings, (4) specific workflows worth Mantle adopting with rationale, (5)
  MegaETH-unique patterns especially doc-audit and AI integration. Each finding
  must include file path or URL and the commit SHA at research time.

revision_metadata:
  created_by: deep-research-agent
  created_at: "2026-06-10T10:30:00Z"
  last_modified_by: deep-research-agent
  last_modified_at: "2026-06-10T11:10:00Z"
---

# Research Outline: MegaETH GitHub Actions 完整调研

## Items

### item-1: Workflow Inventory and Cross-Repo Comparison

Enumerate all workflow files under `.github/workflows/` for both mega-evm (8 workflows) and stateless-validator (5 workflows). Produce a side-by-side inventory table showing which workflows are shared vs. repo-specific, their trigger events, runner configurations, and timeout settings. This item establishes the factual baseline for all subsequent analysis.

- **Priority**: high
- **Dependencies**: none

### item-2: AI Integration via claude.yml

Deep analysis of the Claude Code Action integration pattern used in both repositories. mega-evm has 5 jobs (interactive, pr-review, doc-impact, label-check, issue-triage) while stateless-validator has 4 jobs (no doc-impact). Investigate: trigger conditions and permission scoping per job, allowed tool lists, bot allowlisting (`mega-putin`), OAuth token configuration, Claude Code Action version pinning (`@v1` vs `@v1.0.88`), and the MEMBER/COLLABORATOR/OWNER gating pattern. This is a key differentiator from standard CI setups.

- **Priority**: high
- **Dependencies**: item-1

### item-3: build-and-test.yml CI Pipeline Design

Analyze the CI pipeline structure shared by both repos: lint (cargo-sort, fmt, clippy), test (cargo build + test), and no-std cross-compilation checks. Compare differences: mega-evm targets `riscv64imac-unknown-none-elf` only; stateless-validator targets both `riscv64imac-unknown-none-elf` and `wasm32-unknown-unknown` and adds `codespell`. Examine `workflow_call` reusability, concurrency groups with cancel-in-progress, and the consistent use of `actions/checkout@v4` + `actions-rust-lang/setup-rust-toolchain@v1` + `foundry-rs/foundry-toolchain@v1`.

- **Priority**: high
- **Dependencies**: item-1

### item-4: coverage.yml Code Coverage Approach

Analyze the coverage workflow pattern: `cargo-llvm-cov` for instrumentation, custom shell scripts for test selection, Codecov integration with per-package flags, and artifact upload. Both repos follow an identical structure. Evaluate maturity compared to alternatives (tarpaulin, grcov) and examine the coverage reporting configuration.

- **Priority**: medium
- **Dependencies**: item-3

### item-5: doc-audit.yml Documentation Audit Workflow

This is a rare and distinctive workflow type found only in mega-evm. It uses Claude Code Action on a weekly schedule to perform 3-dimensional documentation audit (freshness, correctness, readability) across `docs/spec/`, `docs/mega-evme/`, and agent files (AGENTS.md, CLAUDE.md, REVIEW.md). It auto-creates/updates a GitHub issue with findings and closes it when clean. Analyze the audit methodology, issue lifecycle management, and potential for adoption.

- **Priority**: high
- **Dependencies**: item-2

### item-6: Release Strategy and Artifact Publishing

Compare two distinct release patterns: (a) mega-evm uses `publish.yml` for sequential crates.io publishing of 3 crates with 90-second inter-publish waits and semver tag validation; (b) stateless-validator uses `release.yaml` and `release-tracing.yaml` for binary compilation and GCP upload via shared `megaeth-labs/chain-ops` actions. Examine: cross-repo action reuse, the `prod` environment gate, PAT-based cross-repo access, and GCP artifact management.

- **Priority**: medium
- **Dependencies**: item-1

### item-7: Repo-Level Configuration and Governance

Consolidate non-workflow repository configuration: CODEOWNERS (mega-evm: 4 global owners; stateless-validator: 4 global + 6 CI-specific owners), rulesets (mega-evm: 5 rulesets including branch naming enforcement and Copilot code review; stateless-validator: 2 rulesets with CodeQL scanning), PR templates (mega-evm has `.github/pull_request_template.md` — lowercase filename — with Summary, Test plan, and Labels checklist sections; stateless-validator has no PR template under either case variant), absence of Dependabot in both repos, and secrets inventory (CLAUDE_CODE_OAUTH_TOKEN, CARGO_REGISTRY_TOKEN, PAT_GAO_CI, GCP_AUTH_KEY, CODECOV_TOKEN). When assessing PR template presence for any repo, always check both filename case variants: `.github/PULL_REQUEST_TEMPLATE.md` (uppercase) and `.github/pull_request_template.md` (lowercase). Note items that could not be accessed and the methods attempted.

- **Priority**: medium
- **Dependencies**: item-1

### item-8: 10-Dimension Capability Matrix and Adoption Recommendations

Synthesize findings from items 1-7 into a structured capability matrix rating each dimension as mature / basic / missing for each repo. The 10 dimensions: (1) Build & Lint, (2) Testing, (3) Code Coverage, (4) AI-Assisted Review, (5) Documentation Quality, (6) Release Management, (7) Branch Protection & Governance, (8) Dependency Management, (9) Security Scanning, (10) Performance Benchmarking. Identify specific workflows and patterns worth Mantle adopting with concrete rationale.

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| workflow_files | Complete list of workflow YAML files with paths and names | item-1 |
| trigger_config | Event triggers, conditions, and concurrency settings | item-1, item-2, item-3, item-4, item-5, item-6 |
| permissions_model | GitHub token permissions declared per workflow/job | item-2, item-3, item-4, item-5, item-6 |
| action_dependencies | Third-party actions used and their pinned versions | all |
| secrets_inventory | Secret names referenced (not values), purpose, and scope | item-2, item-6, item-7 |
| cross_repo_comparison | Side-by-side differences between mega-evm and stateless-validator | all |
| maturity_rating | Assessment as mature / basic / missing per capability dimension | item-8 |
| adoption_rationale | Whether and why Mantle should adopt each pattern | item-2, item-5, item-6, item-8 |
| commit_sha | Git commit SHA at time of research for each repository | all |
| ruleset_config | Branch protection rulesets, naming conventions, required checks | item-7 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Side-by-side workflow inventory matrix showing shared vs. repo-specific workflows between mega-evm and stateless-validator | ascii | item-1 |
| diag-2 | architecture | claude.yml job architecture showing trigger flow from GitHub events through 5 jobs (interactive, pr-review, doc-impact, label-check, issue-triage) with permission boundaries | mermaid | item-2 |
| diag-3 | flow | CI pipeline flow from PR open through lint/test/no-std gates to merge, showing required status checks enforced by rulesets | mermaid | item-3, item-7 |
| diag-4 | comparison | 10-dimension capability heatmap showing maturity ratings across both repos | ascii | item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | Workflow YAML files from mega-evm `.github/workflows/` (commit SHA: 55710e326e30c7c90f4c481c88ef2bedc9e455e4) | 8 |
| src-2 | code_analysis | Workflow YAML files from stateless-validator `.github/workflows/` (commit SHA: 7c6ee1f06ab4cd6ee5257cb23e4608909d2ed67c) | 5 |
| src-3 | code_analysis | Repo-level config files (CODEOWNERS, rulesets, PR templates — check both case variants) from both repos | 3 |
| src-4 | official_docs | GitHub Actions documentation for referenced actions (claude-code-action, codecov-action, setup-rust-toolchain) | 3 |
| src-5 | official_docs | GitHub API documentation for rulesets, branch protection, and repository configuration endpoints | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-7 | Corrected PR template finding: mega-evm has `.github/pull_request_template.md` (lowercase) with Summary/Test plan/Labels checklist sections; stateless-validator confirmed absent under both case variants. Added instruction to check both case variants in deep-draft. | adversarial-review-round-1 |
| 2 | modify_source_req | src-3 | Updated to include PR templates and increased min count to reflect CODEOWNERS + rulesets + PR template sources | adversarial-review-round-1 |
