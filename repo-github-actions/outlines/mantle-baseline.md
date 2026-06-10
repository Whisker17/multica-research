---
topic: "Mantle GitHub Actions 基线调研"
project_slug: mantle-github-actions
topic_slug: mantle-baseline
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: "mantle-github-actions/outlines/mantle-baseline.md"
  draft: "mantle-github-actions/research-sections/mantle-baseline/drafts/round-{n}.md"
  final: "mantle-github-actions/research-sections/mantle-baseline/final.md"
  index: "mantle-github-actions/research-sections/_index.md"

scope: |
  Complete baseline research of GitHub Actions workflows and repo-level configurations
  for all 5 Mantle repos (reth, kona, op-geth, op-succinct, mantle-v2). Enumerate every
  workflow file and repo-level config, classify each workflow across 10 automation dimensions,
  and produce a cross-repo capability matrix with maturity ratings.

audience: |
  Mantle infrastructure and DevOps engineers who will use this baseline to identify
  automation gaps and plan GitHub Actions improvements across the organization.

expected_output: |
  A structured research document containing: per-repo workflow inventories in YAML format,
  repo-level configuration summaries, a 5-repo x 10-dimension capability matrix with
  maturity ratings (成熟/基础/缺失), detailed AI workflow analysis, and automation
  maturity assessment.

revision_metadata:
  created_by: deep-research-agent
  created_at: "2026-06-10T10:10:00Z"
  last_modified_by: deep-research-agent
  last_modified_at: "2026-06-10T12:10:00Z"
---

# Research Outline: Mantle GitHub Actions 基线调研

## Items

### item-1: Repo Inventory and Workflow Enumeration

Systematically enumerate all GitHub Actions workflow files and repo-level configuration
files across all 5 Mantle repos. For each repo, record the current HEAD commit SHA,
upstream fork origin, and complete file listing under `.github/`. This establishes the
factual foundation for all subsequent analysis items.

**Preliminary findings from local filesystem scan + GitHub API:**

| Repo | Workflows | Commit SHA | Source | Status |
|------|-----------|------------|--------|--------|
| reth | 29 | `84e6ed12` | GitHub API (local repo broken) | Verified via `gh api` |
| kona | 14 | `72a20ab9` | Local filesystem | Complete |
| op-geth | 5 | `3c1c571e` | Local filesystem | Complete |
| op-succinct | 2 | `664a1bd4` | Local filesystem | Complete |
| mantle-v2 | 3 | `feb2a588` | Local filesystem | Complete |
| **Total** | **53** | | | |

**reth local repo issue**: The `reth` local repo has a corrupted git state (`.git` exists but branch is broken, no working tree files). All reth data is collected via the GitHub API (`gh api repos/mantle-xyz/reth/...`).

**reth remote enumeration checklist** (must be fully satisfied before item-2/item-4 analysis):
- [x] GitHub API endpoint confirmed: `gh api repos/mantle-xyz/reth/contents/.github/workflows`
- [x] Default branch confirmed: `main`
- [x] HEAD commit SHA captured: `84e6ed12858c7be14b0e140758a532813a6bf79d`
- [x] Full workflow filename list captured (29 files): bench.yml, book.yml, compact.yml, dependencies.yml, docker-git.yml, docker-nightly.yml, docker.yml, e2e.yml, hive.yml, integration.yml, kurtosis-op.yml, kurtosis.yml, label-pr.yml, lint-actions.yml, lint.yml, mantle-release.yml, pr-title.yml, prepare-reth.yml, release-dist.yml, release-reproducible.yml, release.yml, reproducible-build.yml, stage.yml, stale.yml, sync-era.yml, sync.yml, unit.yml, update-superchain.yml, windows.yml
- [x] Repo-level `.github/` inventory captured: CODEOWNERS, dependabot.yml, ISSUE_TEMPLATE/, assets/, scripts/

- **Priority**: high
- **Dependencies**: none

### item-2: Per-Workflow Detailed Analysis

For each workflow file identified in item-1, extract structured metadata in the specified
YAML format: workflow_name, file, triggers, purpose, category, ai_features, ai_tool,
and notable_patterns. This provides the granular per-workflow data that feeds into the
dimension classification and capability matrix.

**Preliminary findings (workflow counts by category):**

| Category | reth | kona | op-geth | op-succinct | mantle-v2 |
|----------|------|------|---------|-------------|-----------|
| CI/CD | ~15 (unit, integration, e2e, hive, lint, compact, etc.) | 7 | 3 | 1 | 2 |
| AI | 0 | 2 | 0 | 0 | 0 |
| Release | ~6 (release, release-dist, docker, docker-nightly, docker-git, mantle-release) | 1 | 0 | 0 | 1 |
| Security | 0 | 0 | 0 | 0 | 1 (semgrep) |
| Benchmark | 1 (bench) | 1 | 0 | 1 | 0 |
| Governance | 3 (pr-title, label-pr, stale) | 1 | 1 | 0 | 0 |
| Infra | ~4 (book, dependencies, sync, sync-era, update-superchain, etc.) | 2 | 1 | 0 | 0 |
| Total | 29 | 14 | 5 | 2 | 3 |

**Note**: reth category assignments above are preliminary estimates based on workflow filenames; exact classification requires full YAML analysis during item-2.

**Mandatory pre-condition**: reth remote enumeration checklist (item-1) must be fully satisfied before this item begins. No `?` placeholders are acceptable in the final output.

- **Priority**: high
- **Dependencies**: item-1

### item-3: Repo-Level Configuration Analysis

Analyze non-workflow GitHub configuration files for each repo: dependabot.yml, CODEOWNERS,
PR templates, issue templates, codecov.yml, stale/no-response bot configs, changelog
generation (cliff.toml), reusable composite actions, and code-review-graph instructions.
These configurations reveal governance maturity and developer experience investment
independent of workflow automation.

**Preliminary findings:**

| Config | reth | kona | op-geth | op-succinct | mantle-v2 |
|--------|------|------|---------|-------------|-----------|
| dependabot.yml | Yes | Yes (daily, cargo+actions) | No | No | No |
| CODEOWNERS | Yes | Yes (5 maintainers) | Yes (detailed per-subsystem) | No | Yes (role-based teams) |
| PR template | TBD (requires API check) | No | No | No | No |
| Issue templates | Yes (ISSUE_TEMPLATE/ dir) | No | Yes (bug/question/feature) | Yes (bug form) | No |
| codecov.yml | TBD (requires API check) | Yes (unit/e2e/proof flags) | No | No | No |
| Stale/no-response | Yes (stale.yml workflow) | Yes (stale PRs) | Yes (stale issues + no-response) | No | No |
| Reusable actions | TBD (requires scripts/ check) | Yes (setup action) | No | Yes (setup action) | No |
| code-review-graph | TBD (not in top-level .github/) | Yes | Yes | Yes | Yes |
| cliff.toml | TBD | No | No | No | Yes |

**Note**: reth `.github/` top-level inventory confirmed via API: `CODEOWNERS`, `dependabot.yml`, `ISSUE_TEMPLATE/`, `assets/`, `scripts/`. Items marked TBD require deeper API traversal during drafting (file-level `gh api` calls to check for specific configs not visible at directory level).

- **Priority**: high
- **Dependencies**: item-1

### item-4: 10-Dimension Capability Classification

Apply the 10-dimension analysis framework to classify each repo's automation maturity.
Map each workflow to one or more dimensions, determine per-repo ratings (成熟/基础/缺失),
and produce the cross-repo capability matrix. This is the core analytical output that
enables gap identification.

**Analysis framework:**

1. **Upstream Auto-Sync**: Automated upstream merge/rebase workflows
2. **AI Code Review**: AI-powered PR review (Claude, Copilot, etc.)
3. **PR Audit**: Automated PR format/content validation
4. **Interactive Agent**: AI agent triggered by comments (@claude, etc.)
5. **Release Pipeline**: Docker build/publish, artifact generation, changelog
6. **CI/Testing**: Build verification, unit tests, integration tests, E2E tests
7. **Security & Supply Chain**: Dependency scanning, SAST, supply chain hardening
8. **Benchmark/Performance Regression**: Cost estimation, proof benchmarks, perf tracking
9. **PR Governance**: Stale PR management, CODEOWNERS enforcement, merge policies
10. **Documentation & Infrastructure**: Docs deployment, link checking, GitHub Pages

**Preliminary capability assessment:**

| Dimension | reth | kona | op-geth | op-succinct | mantle-v2 |
|-----------|------|------|---------|-------------|-----------|
| Upstream Auto-Sync | 基础 (sync.yml, sync-era.yml, update-superchain.yml) | 基础 (sync.yaml) | 缺失 | 缺失 | 缺失 |
| AI Code Review | 缺失 | 成熟 (claude-code-review) | 缺失 | 缺失 | 缺失 |
| PR Audit | 基础 (pr-title.yml) | 缺失 | 基础 (validate_pr) | 缺失 | 缺失 |
| Interactive Agent | 缺失 | 成熟 (claude.yml) | 缺失 | 缺失 | 缺失 |
| Release Pipeline | 成熟 (release, release-dist, docker, docker-nightly, mantle-release) | 成熟 (docker+artifacts) | 缺失 | 缺失 | 基础 (protected.yaml) |
| CI/Testing | 成熟 (unit, integration, e2e, hive, kurtosis, lint) | 成熟 (rust_ci+e2e+proof) | 基础 (go.yml+build) | 基础 (elf.yml) | 成熟 (ci-main-migrated) |
| Security & Supply Chain | TBD (requires YAML analysis) | 基础 (cargo-deny) | 缺失 | 缺失 | 基础 (semgrep+harden-runner) |
| Benchmark/Perf | 基础 (bench.yml) | 基础 (proof.yaml) | 缺失 | 成熟 (cost-estimator q3h) | 缺失 |
| PR Governance | 基础 (pr-title, label-pr, stale) | 基础 (stale.yaml) | 基础 (validate_pr+stale) | 缺失 | 缺失 |
| Doc & Infra | 基础 (book.yml, dependencies.yml) | 成熟 (docs+lychee) | 基础 (pages) | 缺失 | 缺失 |

**Note**: reth preliminary ratings are based on workflow filename analysis. Items marked TBD require full YAML content analysis. No `?` placeholders are acceptable in the final deliverable.

**Mandatory pre-condition**: reth remote enumeration checklist (item-1) must be fully satisfied before this item begins.

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: AI Workflow Deep Analysis

Perform detailed analysis of all AI-powered workflows across the repos. Currently only
kona has AI workflows (claude-code-review.yml and claude.yml). Document the exact
configuration, permissions model, trigger conditions, integration patterns, and effectiveness
signals. Also examine the code-review-graph instruction files present in 4 repos as a
potential AI-adjacent tool. This item answers the question: what AI automation already
exists and how is it configured?

**Preliminary findings:**
- **kona/claude-code-review.yml**: Anthropic Claude Code Review Action (beta), triggers on PR opened/ready/reopened, OAuth token auth, read-only permissions, reviews for code quality/bugs/performance/security/test coverage.
- **kona/claude.yml**: Interactive Claude agent, triggers on @claude mentions in issues/PRs/reviews, can read CI results, supports custom instructions and environment variables.
- **code-review-graph.instruction.md**: Present in kona, op-geth, op-succinct, mantle-v2. MCP-based tooling for semantic code search, impact radius analysis, and review context. Not a GitHub Actions workflow but an AI-adjacent developer tool.
- **reth**: No AI-powered workflows detected among 29 workflow filenames (verified via GitHub API).
- **op-geth, op-succinct, mantle-v2**: No AI-powered workflows.

- **Priority**: high
- **Dependencies**: item-2

### item-6: GitHub API Data Collection (Branch Protection, Secrets, Apps)

Collect data that cannot be determined from the local filesystem alone: branch protection
rules, GitHub Environments, configured GitHub Apps, and Secrets names (names only, not
values). This requires GitHub API access via `gh api` or the GitHub REST API. The data
completes the governance and infrastructure picture that workflows alone cannot provide.

**Data collection plan:**
- `gh api repos/{owner}/{repo}/branches/{branch}/protection` for each default branch
- `gh api repos/{owner}/{repo}/environments` for deployment environments
- `gh api repos/{owner}/{repo}/actions/secrets` for secret names
- `gh api repos/{owner}/{repo}/installation/repositories` or similar for GitHub Apps
- Repo-level settings: visibility, default branch, merge strategies

**Known secrets (from workflow analysis):**
- kona: `CODECOV_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`, `PAT_TOKEN`, `GITHUB_TOKEN`
- op-succinct: `L1_RPC`, `L1_BEACON_RPC`, `L2_RPC`, `L2_NODE_RPC`, `EIGEN_DA_PROXY_URL` (may be self-hosted runner env vars rather than GitHub secrets)
- mantle-v2: `GITHUB_TOKEN` (standard)

**Known runner configurations:**
- reth: TBD (requires YAML analysis; upstream paradigmxyz/reth uses a mix of GitHub-hosted and self-hosted)
- op-geth: Self-hosted runners (`self-hosted-ghr`, `size-s-x64`, `size-l-x64`)
- op-succinct: Self-hosted on EKS (`self-hosted, Linux, X64, eks, mantle-succinct, mainnetv2`)
- kona: GitHub-hosted (`ubuntu-latest`, `ubuntu-22.04-arm`)
- mantle-v2: GitHub-hosted (`ubuntu-latest`)

- **Priority**: medium
- **Dependencies**: item-1

### item-7: Cross-Repo Patterns and Automation Gap Analysis

Synthesize findings from all previous items into cross-repo observations: shared patterns
(e.g., all 4 active repos have code-review-graph.instruction.md), unique strengths
(kona's AI integration, mantle-v2's comprehensive CI pipeline), common gaps (no upstream
auto-sync in 4/5 repos, no AI review in 4/5 repos), and the relationship between
repo maturity and upstream fork freshness. This item produces the actionable insight
layer on top of the factual baseline.

- **Priority**: medium
- **Dependencies**: item-4, item-5, item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| workflow_inventory | Complete list of workflow files with names and line counts | item-1, item-2 |
| trigger_configuration | Event triggers (push, PR, schedule, dispatch, comment) and branch filters | item-2 |
| category_classification | Primary category: CI/CD/Release/Security/Benchmark/AI/Governance/Infra | item-2 |
| ai_integration_details | AI tool name, action version, permissions, trigger model, configuration options | item-5 |
| runner_configuration | Runner type (GitHub-hosted vs self-hosted), labels, platform specifics | item-2, item-6 |
| dependency_management | Dependabot config, automated dependency update workflows, update frequency | item-3 |
| code_ownership_model | CODEOWNERS structure, team-based vs individual ownership, minimum reviewer requirements | item-3 |
| security_posture | Supply chain hardening measures: pinned actions, harden-runner, SAST tools, cargo-deny | item-2, item-3 |
| dimension_rating | Per-dimension maturity rating: 成熟/基础/缺失 with justification | item-4 |
| automation_gap | Identified gaps where automation is missing or insufficient compared to best practice | item-7 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | 5-repo x 10-dimension capability heatmap matrix showing maturity ratings (成熟/基础/缺失) with color coding | ascii | item-4 |
| diag-2 | architecture | Workflow trigger flow diagram showing how different event types (push, PR, schedule, comment) route to workflow categories across repos | mermaid | item-2 |
| diag-3 | comparison | AI integration architecture diagram showing Claude Code Review and Interactive Agent data flow in kona, and the code-review-graph MCP tooling across repos | mermaid | item-5 |
| diag-4 | hierarchy | Per-repo CI/CD pipeline structure showing job dependency chains (particularly mantle-v2's 20-job ci-main-migrated and kona's multi-matrix workflows) | mermaid | item-2 |

## Source Requirements

### Per-repo workflow source gates (mandatory — each repo must independently satisfy its minimum)

| ID | Repo | Type | Description | Min Count |
|----|------|------|-------------|-----------|
| src-1a | reth | code_analysis | Workflow YAML files from `mantle-xyz/reth` `.github/workflows/`, fetched via GitHub API | 29 |
| src-1b | kona | code_analysis | Workflow YAML files from `mantle-xyz/kona` `.github/workflows/`, read from local filesystem | 14 |
| src-1c | op-geth | code_analysis | Workflow YAML files from `mantlenetworkio/op-geth` `.github/workflows/`, read from local filesystem | 5 |
| src-1d | op-succinct | code_analysis | Workflow YAML files from `mantle-xyz/op-succinct` `.github/workflows/`, read from local filesystem | 2 |
| src-1e | mantle-v2 | code_analysis | Workflow YAML files from `mantlenetworkio/mantle-v2` `.github/workflows/`, read from local filesystem | 3 |

**Total workflow corpus**: at least 53 files. The draft must recompute exact counts at collection time and report any discrepancy with these minimums. No repo may be skipped — all 5 must have non-null workflow analysis.

### Other source requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-2 | code_analysis | Repo-level configuration files (dependabot, CODEOWNERS, codecov, stale, cliff.toml, setup actions) per repo | 15 |
| src-3 | official_docs | GitHub Actions documentation for referenced actions (anthropics/claude-code-action, step-security/harden-runner, etc.) | 3 |
| src-4 | code_analysis | GitHub API responses for branch protection rules, environments, secrets names, and apps per repo | 5 (one per repo) |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_source_req | src-1 | [MAJOR] Replaced single aggregate src-1 (min 24) with per-repo source gates (src-1a through src-1e) totaling 53 minimum. Prevents draft from satisfying outline while skipping reth entirely. | adversarial-review-round-1 |
| 2 | modify_item | item-1 | [MAJOR] Added concrete reth remote enumeration checklist with hard completion gates: API endpoint, default branch, HEAD SHA, full workflow list (29 files), repo-level .github/ inventory. All items checked. | adversarial-review-round-1 |
| 2 | modify_item | item-2 | [MAJOR] Updated preliminary category table with reth data (29 workflows). Added mandatory pre-condition requiring reth checklist completion. Removed all ? placeholders. | adversarial-review-round-1 |
| 2 | modify_item | item-3 | [MINOR] Updated repo-level config table with confirmed reth data (CODEOWNERS, dependabot.yml, ISSUE_TEMPLATE/). Marked unknown sub-items as TBD with API check required. | adversarial-review-round-1 |
| 2 | modify_item | item-4 | [MAJOR] Updated capability matrix with preliminary reth ratings based on workflow filenames. Added mandatory pre-condition. Removed all ? placeholders. | adversarial-review-round-1 |
| 2 | modify_item | item-5 | [MINOR] Added explicit reth AI status (no AI workflows among 29 files). | adversarial-review-round-1 |
| 2 | modify_item | item-6 | [MINOR] Added reth runner configuration as TBD requiring YAML analysis. | adversarial-review-round-1 |
