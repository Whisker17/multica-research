---
topic: "Solana/Agave GitHub Actions 完整调研"
project_slug: repo-github-actions
topic_slug: solana-agave
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: "repo-github-actions/outlines/solana-agave.md"
  draft: "repo-github-actions/research-sections/solana-agave/drafts/round-{n}.md"
  final: "repo-github-actions/research-sections/solana-agave/final.md"
  index: "repo-github-actions/research-sections/_index.md"

scope: >
  Complete audit of GitHub Actions workflows and repo-level configuration in
  github.com/anza-xyz/agave (Rust project, 11 workflows). Focus areas:
  release.yml / bump-version.yml (release automation and version bumping),
  dependabot-pr.yml (automated Dependabot PR handling),
  cargo.yml / crate-check.yml (Rust CI patterns),
  trigger-buildkite-pipeline.yml (external CI integration with Buildkite).
  Also enumerate all .github/workflows/ files, .github/dependabot.yml,
  CODEOWNERS, .github/PULL_REQUEST_TEMPLATE.md. Where accessible via public
  API or repo page, capture branch protection rules / rulesets, configured
  GitHub Apps, and secrets names (values excluded). Access via GitHub API or
  web — repo is not cloned locally.

audience: >
  Mantle engineering team evaluating GitHub Actions patterns from mature
  open-source Rust projects for adoption into their own CI/CD pipelines.

expected_output: >
  Structured document with: (1) complete workflow file list, (2) repo-level
  configuration overview, (3) 10-dimension capability matrix with maturity
  ratings (成熟/基础/缺失), (4) specific workflows worth borrowing for Mantle
  with rationale, (5) Solana/Agave-unique patterns. Every finding must cite
  file path or URL plus the commit SHA captured during research.

revision_metadata:
  created_by: deep-research-agent
  created_at: "2026-06-10T10:15:00Z"
  last_modified_by: deep-research-agent
  last_modified_at: "2026-06-10T10:15:00Z"
---

# Research Outline: Solana/Agave GitHub Actions 完整调研

## Items

### item-1: Workflow Inventory & Classification

Complete enumeration of all 11 workflow files under `.github/workflows/` in anza-xyz/agave. For each workflow, record: file name, `name:` field, trigger events (`on:`), job count, and functional category (CI, release, dependency management, maintenance, external integration). This item provides the foundational inventory that all subsequent items reference.

- **Priority**: high
- **Dependencies**: none

### item-2: Release Automation Pipeline

Deep analysis of the release automation chain: `release.yml` (tag-triggered release creation + Buildkite secondary pipeline trigger), `bump-version.yml` (workflow_dispatch version bump with `xtask` tooling, auto PR creation), and `publish-windows-tarball.yml` (manual Windows binary build + GCS upload + GitHub Release attachment). Map the end-to-end release lifecycle from version bump through artifact publication, including the custom `xtask` tooling and multi-platform release strategy.

- **Priority**: high
- **Dependencies**: item-1

### item-3: Rust CI Patterns

Analysis of `cargo.yml` (multi-platform clippy-nightly with matrix strategy: macOS-15, Ubuntu alpine musl, Windows-2025; sccache integration; path-filtered triggers; concurrency groups) and `crate-check.yml` (commit-range-aware crate validation via `ci/check-crates.sh`). Includes examination of the auxiliary `ci/` script ecosystem (`rust-version.sh`, `install-all-deps.sh`, `check-crates.sh`) that underpins Rust CI. Focus on build caching strategy, cross-platform compilation patterns, and how CI scripts are organized outside workflows.

- **Priority**: high
- **Dependencies**: item-1

### item-4: External CI Integration with Buildkite

Analysis of `trigger-buildkite-pipeline.yml` (PR-triggered Buildkite dispatch with permission-gated access control). This workflow implements a sophisticated two-path authorization model: org member check via GitHub API collaborator permissions, plus a `CI` label trigger for external contributors. Covers the GitHub Actions → Buildkite bridge pattern, permission boundaries, and how the repo splits CI load between GitHub Actions and Buildkite.

- **Priority**: high
- **Dependencies**: item-1

### item-5: Dependency Management Automation

Analysis of `dependabot.yml` (multi-ecosystem configuration: Cargo with directory splitting, npm for docs, github-actions; cooldown rules with anza-team crate exclusions) and `dependabot-pr.yml` (automated PR enrichment that parses bump PR titles, runs `cargo xtask update-crate` for workspace-wide updates, and auto-pushes). Includes the GitHub App token pattern for Dependabot PR operations and the custom `cargo-for-all-lock-files.sh` multi-workspace update strategy.

- **Priority**: high
- **Dependencies**: item-1

### item-6: Repo-Level Configuration & Branch Governance

Audit of non-workflow repo configuration: 10 active rulesets (including merge queue on master with squash-only, required `buildkite/agave` status check, CODEOWNER review, last-push approval; release branch `v[0-9]*` protection; dependabot branch rules; version-bump branch rules; tag protection), PR template (Problem/Summary/Testing/Fixes format), issue templates (community + core-contributor), RELEASE_TEMPLATE.md, and the `.github/scripts/` helper directory. Document what configuration is publicly visible vs. permission-restricted.

- **Priority**: medium
- **Dependencies**: none

### item-7: Repo Maintenance & Auxiliary Workflows

Analysis of supporting workflows: `manage-stale-issues.yml` (scheduled stale PR management with 60-day window, dry-run on PR self-changes), `changelog-label.yml` (label-gated changelog entry enforcement via custom script), `docs.yml` (conditional doc build with Vercel deploy, pnpm/Node toolchain, channel-based publish logic), and `benchmark.yml` (matrix-based Rust benchmarks on dedicated runner with InfluxDB upload). These workflows reveal the project's approach to repo hygiene, documentation, and performance tracking.

- **Priority**: medium
- **Dependencies**: item-1

### item-8: 10-Dimension Capability Matrix & Mantle Borrowability Assessment

Synthesize findings from items 1-7 into: (a) a 10-dimension capability matrix rating each dimension as 成熟/基础/缺失, (b) specific workflows and patterns worth borrowing for Mantle with concrete rationale, and (c) Solana/Agave-unique patterns that reflect their project-specific constraints (monorepo Rust workspace, Buildkite hybrid CI, validator release cadence). The 10 dimensions are: Release Automation, Version Management, CI Build Optimization, Dependency Management, Branch Protection, Code Quality Gates, Documentation Pipeline, Performance Tracking, Issue/PR Lifecycle, External CI Integration.

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4, item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| trigger_mechanism | Trigger events (push, PR, schedule, workflow_dispatch, tag, label), branch filters, and path filters for each workflow | item-1, item-2, item-3, item-4, item-5, item-7 |
| security_posture | Pin-by-SHA for actions, permission scoping (`permissions:` blocks), secret names used (not values), GitHub App token patterns, org-membership gating (`github.repository_owner == 'anza-xyz'`) | all |
| build_optimization | Caching strategies (sccache, GHA cache), concurrency groups, matrix strategies, path-filtered triggers, conditional job skipping | item-3, item-4, item-7 |
| cross_platform_support | OS matrix coverage (macOS, Linux/alpine-musl, Windows), platform-specific workarounds, container usage | item-2, item-3 |
| maturity_rating | Per-dimension rating (成熟/基础/缺失) based on sophistication, completeness, and industry best-practice alignment | item-8 |
| mantle_borrowability | Assessment of whether a pattern/workflow is transferable to Mantle, considering differences in language ecosystem (Rust monorepo vs. Go modules), CI infrastructure, and release cadence | item-8 |
| unique_patterns | Patterns specific to Solana/Agave that reflect their project constraints: custom `xtask` tooling, Buildkite hybrid CI, multi-workspace Cargo lockfile handling, validator release workflow | item-2, item-3, item-4, item-5 |
| secrets_and_permissions | Enumeration of all referenced secrets names and GitHub token patterns, plus explicit `permissions:` blocks and their scoping | item-2, item-4, item-5, item-6 |
| concurrency_strategy | Use of `concurrency:` groups, `cancel-in-progress`, merge queue configuration, and how parallel/serial job dependencies are structured | item-3, item-4, item-6 |
| external_integration | Integration points with external services: Buildkite API, GCS (Google Cloud Storage), InfluxDB for benchmarks, Vercel for docs deployment | item-2, item-4, item-7 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | flow | End-to-end release lifecycle: version bump (workflow_dispatch) -> PR merge -> tag push -> release.yml (draft release + Buildkite secondary trigger) -> publish-windows-tarball.yml (manual Windows build) -> GCS + GitHub Release artifacts | mermaid | item-2 |
| diag-2 | architecture | CI workflow topology showing how GitHub Actions and Buildkite split responsibilities: GHA handles clippy/crate-check/docs/benchmarks, Buildkite handles the main test suite (required status check `buildkite/agave`), with trigger-buildkite-pipeline.yml as the bridge | mermaid | item-3, item-4 |
| diag-3 | flow | Dependabot PR lifecycle: dependabot.yml config -> Dependabot opens PR -> dependabot-pr.yml triggers -> GitHub App token creation -> title parsing -> cargo xtask update-crate -> multi-lockfile update -> auto-push | mermaid | item-5 |
| diag-4 | comparison | 10-dimension capability matrix as a visual table/radar showing maturity ratings across all dimensions with color-coding for 成熟/基础/缺失 | ascii | item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | Workflow YAML files from .github/workflows/ in anza-xyz/agave at the research commit SHA, accessed via GitHub API | 11 |
| src-2 | code_analysis | Repo configuration files: .github/dependabot.yml, .github/PULL_REQUEST_TEMPLATE.md, .github/RELEASE_TEMPLATE.md, .github/ISSUE_TEMPLATE/, .github/scripts/ | 5 |
| src-3 | official_docs | GitHub API responses for repo rulesets (public endpoint), repo metadata, and branch protection (if accessible) | 3 |
| src-4 | code_analysis | Auxiliary CI scripts from ci/ directory referenced by workflows (rust-version.sh, check-crates.sh, upload-benchmark.sh, publish-tarball.sh, channel-info.sh) | 5 |
| src-5 | official_docs | GitHub Actions documentation for features used (merge queues, rulesets, concurrency groups, pull_request_target security model) | 3 |
| src-6 | official_docs | Buildkite documentation for trigger-pipeline-action and API integration patterns | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
