# Base GitHub Actions 完整调研 — Structured Outline

> **Project slug**: `github-actions-optimization`
> **Topic slug**: `base-github-actions`
> **Round**: 2
> **Multica issue**: `4174a367-ea50-4450-9c4a-8ebac7372dff`
> **Scope**: Complete investigation of GitHub Actions workflows and repo-level configuration across base/base (Rust), base/contracts (Solidity), base/docs — with focus on AI code review, release pipeline, tiered CI strategy, PR governance, and security hardening.
> **Audience**: Mantle team evaluating which Base CI/CD patterns to adopt or adapt.
> **Expected output**: Structured document with (1) per-repo workflow inventory and analysis, (2) repo-level config summary, (3) 10-dimension capability matrix, (4) adoption recommendations for Mantle, (5) Base-unique patterns and innovations.
> **Investigation date**: 2026-06-10
> **Codebase SHAs**: base/base `6be38adb50515719ac6d1c9380f423abd7da926f`, base/contracts `506a54e0905cf07efe7e862bca645145f1b5201c`, base/docs `ea200dda099c479dcd5ac2964b9eae997564af3b`

---

## Section 1: Repo 级配置概况 (Repo-Level Configuration)

### 1.1 base/base Repo Configuration

**Investigation fields**:
- `.github/actions/setup/action.yml` — composite action: inputs, tool matrix (stable/nightly, mold, foundry, sp1, sccache, just, elf-cache), reusable patterns
- `.github/VOUCHED.td` — vouch trust database format, current entries, role in PR gating
- `.github/benchmark/` — benchmark config files (`load-test.yml`, `transfer-only.yml`), payload definitions
- Self-hosted runner groups: `BaseRunnerGroup`, `BasePerfRunnerGroup` — usage patterns across workflows
- Concurrency groups — naming conventions, cancel-in-progress strategies
- Permissions model — per-workflow permissions declarations, principle of least privilege
- Missing files: no `dependabot.yml`, no `CODEOWNERS`, no `PULL_REQUEST_TEMPLATE.md`

**Sources**: Local codebase at `/Users/whisker/Work/src/networks/base/base/.github/`

### 1.2 base/contracts Repo Configuration

**Investigation fields**:
- Minimal `.github/` — only `workflows/` directory
- No composite actions, no CODEOWNERS, no dependabot
- Foundry CI profile (`FOUNDRY_PROFILE: ci`)
- Missing governance files

**Sources**: Local codebase at `/Users/whisker/Work/src/networks/base/contracts/.github/`

### 1.3 base/docs Repo Configuration

**Investigation fields**:
- `.github/PULL_REQUEST_TEMPLATE.md` — template content and review guidance
- `.github/.githooks/` — local hooks directory (purpose and content)
- No composite actions, no CODEOWNERS, no dependabot

**Sources**: Local codebase at `/Users/whisker/Work/src/networks/base/docs/.github/`

### 1.4 Repo Settings Access Plan (Active Access Attempts)

The issue acceptance criteria require documenting four repo-level settings fields that are not available in the local codebase checkout. The deep draft must attempt each access method in order: (a) try the public API endpoint or repo page first, (b) if inaccessible, record `不可访问 (权限受限)` with the exact attempt method. This subsection defines the planned investigation steps.

#### 1.4.1 Branch Protection Rules / Repo Rulesets

| Step | Method | Notes |
|---|---|---|
| (a) Primary | `GET https://api.github.com/repos/base/base/branches/main/protection` | Requires admin or push access to the repo; returns 404 for non-collaborators |
| (a) Fallback | `GET https://api.github.com/repos/base/base/rulesets` | Public rulesets endpoint (may return rulesets if configured with public visibility) |
| (a) Page check | GitHub repo Settings → Branches → Branch protection rules | Manual inspection if API access is restricted |
| (b) Inaccessible | Record `不可访问 (权限受限) — attempted: branches/main/protection API + rulesets API` | Include HTTP status code received |

**Indirect evidence to collect regardless**: merge queue usage (implies branch protection requiring status checks), vouch system (implies PR-only flow to main, `GH006` direct push rejection noted in vouch.yml comments), release-branch-ci guard.

#### 1.4.2 GitHub Environments Configuration

| Step | Method | Notes |
|---|---|---|
| (a) Primary | `GET https://api.github.com/repos/base/base/environments` | Public for public repos; lists environment names and protection rules |
| (a) Repeat | Same endpoint for `base/contracts` and `base/docs` | |
| (b) Inaccessible | Record `不可访问 (权限受限) — attempted: /repos/{owner}/{repo}/environments API` | Include HTTP status code |

**Indirect evidence to collect regardless**: workflow files referencing `environment:` key (none found in current analysis — note this explicitly).

#### 1.4.3 Installed GitHub Apps

| Step | Method | Notes |
|---|---|---|
| (a) Primary | `GET https://api.github.com/repos/base/base/installation` | Requires repo admin; returns the app installation for authenticated apps |
| (a) Fallback | GitHub repo Settings → Integrations → GitHub Apps | Manual page inspection |
| (a) Heuristic | Infer from workflow bot accounts: `github-actions[bot]` (standard), check for other bot patterns in PR/issue activity | Best-effort inference |
| (b) Inaccessible | Record `不可访问 (权限受限) — attempted: /repos/{owner}/{repo}/installation API + Settings page` | Include HTTP status code |

**Indirect evidence to collect regardless**: `claude-review.yml` uses `github-actions[bot]` for review comments (standard Actions bot, not a custom App). Check for Dependabot, Renovate, or other App patterns in workflow triggers.

#### 1.4.4 Secrets Names List (Values Excluded)

| Step | Method | Notes |
|---|---|---|
| (a) Primary | `GET https://api.github.com/repos/base/base/actions/secrets` | Requires collaborator access; returns secret names only (never values) |
| (a) Repeat | Same endpoint for `base/contracts` and `base/docs` | |
| (b) Inaccessible | Record `不可访问 (权限受限) — attempted: /repos/{owner}/{repo}/actions/secrets API` | Include HTTP status code |

**Indirect evidence to collect regardless**: enumerate all `secrets.*` references across workflow files to build a known-secrets inventory from code. Currently identified: `LLM_GATEWAY_API_KEY`, `GPG_SIGNING_KEY`, `GPG_PASSPHRASE`, `BASE_STD_TOKEN`, `CHROMATIC_PROJECT_TOKEN`, `GITHUB_TOKEN` (automatic). Also check `vars.*` references: `LLM_GATEWAY_HOSTNAME`.

#### 1.4.5 Access Attempt Execution Plan

During deep draft production, the following steps will be executed in order:

1. Run all four API endpoints above using `curl` or `gh api` (unauthenticated for public endpoints, authenticated if a token is available).
2. Record HTTP response codes (200, 403, 404) for each attempt.
3. For each successful response, extract and document the relevant configuration.
4. For each failed response, record the exact error message and mark as `不可访问 (权限受限)`.
5. Regardless of API access results, compile the indirect evidence inventory from workflow files.

### 1.5 Cross-Repo Configuration Comparison

**Investigation fields**:
- Feature matrix: which repos have CODEOWNERS, dependabot, PR templates, composite actions
- Governance maturity gap between main repo and satellite repos
- Common vs. divergent patterns

---

## Section 2: Workflow 完整列表及逐个分析 (Complete Workflow Inventory & Per-Workflow Analysis)

Each workflow is analyzed with: `workflow_name`, `file`, `triggers`, `purpose`, `category`, `ai_features`, `ai_tool`, `notable_patterns`, `harden_runner_mode`.

### 2.1 base/base Workflows (23 workflow files)

#### 2.1.1 AI Code Review

| Field | Value |
|---|---|
| Item | `claude-review.yml` — Claude Code Review |
| Category | AI |
| Triggers | `pull_request: [opened, synchronize, ready_for_review, reopened]` |

**Investigation fields**:
- Anthropic Claude Code Action integration (`anthropics/claude-code-action@v1.0.29`)
- Model selection: `claude-opus-4-6-default`
- LLM Gateway proxy pattern: `ANTHROPIC_BASE_URL` via `vars.LLM_GATEWAY_HOSTNAME` — architecture implications
- Fork exclusion guard: `github.event.pull_request.head.repo.full_name == github.repository`
- Prompt engineering: Rust-specific review guidelines (error handling, concurrency, safety), negative guidance (no style comments, no praise filler)
- Duplicate avoidance: pre-fetch existing `github-actions[bot]` comments via `gh api`, skip if same/similar issue exists
- Comment management: delete previous summary comments before posting new one with `<!-- CLAUDE_REVIEW_SUMMARY -->` marker
- `harden-runner` in **block mode** — the only workflow using egress blocking, explicit allowlist for github.com, api.github.com, registry.npmjs.org, LLM gateway
- Concurrency: cancel-in-progress per PR number
- `track_progress: false` configuration choice
- Tool allowlist via `claude_args --allowedTools` — restricted to inline comment + PR comment + diff/view/api commands

**Sources**: `/Users/whisker/Work/src/networks/base/base/.github/workflows/claude-review.yml`

#### 2.1.2 Tiered CI Strategy

| Field | Value |
|---|---|
| Items | `ci-core.yml`, `ci-pr.yml`, `ci-merge-queue.yml`, `ci-main-cache.yml` |
| Category | CI/Testing |

**Investigation fields**:
- **ci-core.yml** — reusable `workflow_call` with parameterized inputs: `build_command`, `test_command`, `clippy_command`, `run_sigsegv`, `run_system_tests`, `allow_registry_login`, `save_rust_cache`, `base_ref`
  - Job matrix: changes (Docker detect), metadata-checks (cargo-deny, lock validation, crate deps), format (nightly rustfmt), build (BasePerfRunnerGroup), clippy, test (nextest + JUnit), bench, docker (conditional), test-musl-sigsegv (conditional), system-tests (conditional, 60min timeout)
  - Affected-only vs full build strategy
  - `dorny/paths-filter` for Docker change detection
  - JUnit test reporting via `mikepenz/action-junit-report`
- **ci-pr.yml** — lightweight: affected-only build/clippy/test, no system tests, no sigsegv, no cache save, cancel-in-progress
- **ci-merge-queue.yml** — full: complete build/clippy/test, system tests + sigsegv enabled, no cancel-in-progress implied by merge queue
- **ci-main-cache.yml** — push to main: warm stable cache, SP1 ELF input change detection, conditional stubbed ELF build
- Design pattern: one reusable core, two callers with different parameter profiles (lightweight PR vs full merge queue)

**Sources**: Local codebase workflow files

#### 2.1.3 Three-Stage Release Pipeline

| Field | Value |
|---|---|
| Items | `start-release.yml`, `create-rc.yml`, `build-release.yml`, `publish-release.yml`, `release-branch-ci.yml`, `verify-release.yml` |
| Category | Release |

**Investigation fields**:
- **start-release.yml** — `workflow_dispatch` with bump_type (minor/patch/major), creates release branch, runs version-sync script, creates tracking issue
- **create-rc.yml** — auto-triggers on push to `releases/v*`, version validation (skip if 0.0.0), creates RC tag, calls `build-release.yml` with `is_final: false`
- **build-release.yml** — `workflow_call` reusable:
  - Multi-platform binary matrix: x86_64-linux, aarch64-linux, aarch64-apple-darwin × 4 binaries (base, base-reth-node, base-consensus, basectl)
  - Build features: maxperf profile, sccache, mold/lld linkers
  - GPG signing of archives
  - Build provenance attestation via `actions/attest`
  - Multi-arch Docker images via `docker buildx bake` with HCL config
  - Resilient artifact detection: `find-release-artifacts` job for partial failure recovery
  - Docker manifest creation with semver tag aliases (v1.2.3, v1.2, v1, latest)
  - GitHub Release creation (draft for finals)
- **publish-release.yml** — `workflow_dispatch` with version input, validates release branch exists, validates Cargo.toml version matches, idempotent tag creation (allows rerun), calls `build-release.yml` with `is_final: true`
- **release-branch-ci.yml** — PR guard on release branches: checks finalized state to prevent post-release changes
- **verify-release.yml** — signature verification via `baseup verify-release`, triggered on release publish + PR + manual
- Pipeline invariants: version-sync → RC auto-build → final publish → verify chain

**Sources**: Local codebase workflow files, shell scripts in `etc/scripts/release/`

#### 2.1.4 PR Governance — Vouch System

| Field | Value |
|---|---|
| Item | `vouch.yml` |
| Category | Governance |

**Investigation fields**:
- `mitchellh/vouch` action — PR trust gating for external contributors
- Trust database: `.github/VOUCHED.td` — flat file format with platform prefix support, denounce mechanism
- Two jobs: `check-pr` (on `pull_request_target`) auto-closes unvouched PRs, `manage` (on `issue_comment`) handles vouch/denounce/unvouch commands
- `pull_request_target` security model — safe execution context for fork PRs
- Branch protection integration: vouch changes go through PR + merge queue (no direct push)
- Current vouched users: `crazywriter1`, `timrolsh`

**Sources**: `vouch.yml`, `VOUCHED.td`

#### 2.1.5 Compatibility & Quality Testing

| Field | Value |
|---|---|
| Items | `action-tests.yml`, `no-std.yml`, `base-std-fork-tests.yml`, `zepter.yml`, `lychee.yml` |
| Category | CI/Testing |

**Investigation fields**:
- **action-tests.yml** — action/integration test suite: contracts build + lint + test on BasePerfRunnerGroup
- **no-std.yml** — embedded/RISC-V compatibility: `riscv32imac-unknown-none-elf` target, two variants (standard + proof with nightly)
- **base-std-fork-tests.yml** — cross-repo interface testing: clones `base/base-anvil` + `base/base-std` (internal, needs PAT), patches precompiles, runs fork tests, posts results as PR comment with marker-based idempotent updates
- **zepter.yml** — Substrate/Polkadot feature dependency checker
- **lychee.yml** — dead link checker with concurrency group for rate limiting

**Sources**: Local codebase workflow files

#### 2.1.6 Docker & Packaging

| Field | Value |
|---|---|
| Items | `docker.yml`, `base-anvil-package.yml` |
| Category | CD/Infra |

**Investigation fields**:
- **docker.yml** — dev image build on push to main: multi-arch (amd64/arm64), digest-based manifest merge, devnet cache warming (builder/consensus/batcher targets), GHCR with OCI labels
- **base-anvil-package.yml** — patched Foundry (anvil+forge) packaging: Cargo patch for precompiles, smoke test with base-std fork tests, multi-arch Docker image with MANIFEST.json provenance, semver-aware tagging

**Sources**: Local codebase workflow files

#### 2.1.7 Maintenance & Automation

| Field | Value |
|---|---|
| Items | `stale.yml`, `udeps-report.yml`, `sp1-elf-manifest.yml` |
| Category | Infra/Maintenance |

**Investigation fields**:
- **stale.yml** — issue/PR lifecycle: 7-day stale for issues, 21-day for PRs, 1-day close, `active` label exemption
- **udeps-report.yml** — daily cargo-udeps: scheduled at 13:00 UTC, JSON output parsing, auto-creates/updates GitHub issue with findings, Python report renderer
- **sp1-elf-manifest.yml** — SP1 ELF manifest auto-refresh: detects input changes on push to main, rebuilds ELFs, opens/updates automation PR, idempotent force-with-lease push

**Sources**: Local codebase workflow files

#### 2.1.8 Benchmarking

| Field | Value |
|---|---|
| Item | `benchmark.yml` |
| Category | Benchmark |

**Investigation fields**:
- Manual dispatch, two-phase (build-binaries + run-benchmark)
- External benchmark repo (`base/benchmark`) with Go runner
- Binary caching by source hash (Cargo.toml + crates)
- Load test config: transfer(70%), calldata(20%), precompile/sha256(10%)
- HTML report generation (Node.js)

**Sources**: `benchmark.yml`, `.github/benchmark/load-test.yml`

### 2.2 base/contracts Workflows (1 workflow)

| Field | Value |
|---|---|
| Item | `test.yml` — CI |
| Category | CI/Testing |

**Investigation fields**:
- Foundry-only CI: `forge fmt`, `forge build`, `forge test`
- `semver-lock` validation — snapshot-based ABI compatibility check
- Go FFI dependency for cross-language testing
- `just` task runner integration
- `harden-runner` in audit mode (older version pinning: v2.12.1)

**Sources**: `/Users/whisker/Work/src/networks/base/contracts/.github/workflows/test.yml`

### 2.3 base/docs Workflows (2 workflows)

| Field | Value |
|---|---|
| Items | `chromatic.yml`, `file-size-checker.yml` |
| Category | CI/Documentation |

**Investigation fields**:
- **chromatic.yml** — Storybook visual regression: push-triggered on `storybook/**` path, Chromatic integration with `onlyChanged`
- **file-size-checker.yml** — binary/media size guard: 10MB warning, 40MB block, automated PR commenting via `github-script`
- Both use `harden-runner` audit mode (older v2.12.1 pinning)

**Sources**: Local codebase workflow files

---

## Section 3: Security & Supply Chain Hardening Analysis

**Investigation fields**:
- **step-security/harden-runner** usage patterns:
  - Block mode (egress-policy: block): only `claude-review.yml` — explicit endpoint allowlist
  - Audit mode (egress-policy: audit): all other workflows — universal adoption
  - Version pinning strategy: base/base uses v2.19.4 (latest), contracts/docs use v2.12.1 (older)
- Action pinning by full SHA — universal pattern across all repos, no tag-only references
- Permission scoping — per-workflow `permissions` declarations, minimal privilege
- GPG signing — release binary archives signed with repo secret
- Build provenance — `actions/attest` for SLSA-compliant provenance on release binaries
- Docker supply chain — digest-based image references, OCI labels, GHCR
- Secret management patterns — `LLM_GATEWAY_API_KEY`, `GPG_SIGNING_KEY/PASSPHRASE`, `BASE_STD_TOKEN`
- Fork safety — `pull_request_target` for vouch (safe), fork exclusion in claude-review

**Sources**: All workflow files, cross-referenced

---

## Section 4: 10-Dimension Capability Matrix

Rate each dimension as 成熟 (Mature) / 基础 (Basic) / 缺失 (Missing), with evidence from specific workflow files.

| # | Dimension | Expected Rating | Key Evidence |
|---|---|---|---|
| 1 | Upstream Auto-Sync | Assessment needed | No sync workflow found; check if handled externally |
| 2 | AI Code Review | Mature | `claude-review.yml` with advanced prompt, dedup, block-mode security |
| 3 | PR Audit | Basic–Mature | Vouch system + claude review, but no CODEOWNERS |
| 4 | Interactive Agent | Missing–Basic | No interactive bot/agent workflow found |
| 5 | Release Pipeline | Mature | 6-workflow pipeline: start → RC → build → publish → verify |
| 6 | CI/Testing | Mature | Tiered strategy, system tests, fork tests, no-std, benchmarks |
| 7 | Security & Supply Chain | Mature | Universal harden-runner, SHA pinning, GPG signing, attestation |
| 8 | Benchmark | Basic–Mature | Dedicated benchmark workflow but manual-dispatch only |
| 9 | PR Governance | Mature | Vouch system, merge queue, release branch guards |
| 10 | Documentation & Infrastructure | Basic | Stale bot, udeps report, but no dependabot, minimal docs CI |

**Investigation fields**:
- Per-dimension: list supporting workflows, configuration evidence, and gaps
- Cross-repo dimension scoring (base/base vs contracts vs docs)
- Comparison methodology and rating criteria

---

## Section 5: 值得 Mantle 借鉴的具体 Workflow 及理由 (Mantle Adoption Recommendations)

**Investigation fields**:
- Priority-ranked list of workflows/patterns worth adopting
- Per recommendation: what it is, why it matters, implementation complexity, prerequisites
- Candidate recommendations (to be validated and expanded in deep draft):
  1. **Claude Code Review with LLM Gateway proxy** — production AI review with security isolation
  2. **Tiered CI with reusable workflow_call** — cost optimization via affected-only PR builds
  3. **Three-stage release pipeline** — reproducible releases with RC → final flow
  4. **Universal harden-runner (audit mode)** — immediate supply chain visibility
  5. **Vouch system for external contributors** — trust gating without blocking
  6. **Cross-repo interface testing** (base-std fork tests) — integration confidence
  7. **SP1 ELF manifest auto-refresh** — ZK proof artifact management pattern
  8. **Composite setup action** — DRY CI infrastructure across workflows
  9. **cargo-udeps daily report with issue tracking** — dependency hygiene automation
  10. **GPG signing + build provenance attestation** — release integrity chain

---

## Section 6: Base 独特模式或创新点 (Base-Unique Patterns & Innovations)

**Investigation fields**:
- **LLM Gateway proxy for AI review** — enterprise-grade AI integration without direct API key exposure
- **Egress block mode for AI workflow** — only the AI review workflow uses strict network isolation
- **Vouch trust database** — lightweight contributor trust system via flat file + comment commands
- **Affected-only CI builds** — just-based change detection for Rust workspace (`build::affected-ci`, `test-affected-ci`)
- **Partial failure resilience in release pipeline** — `find-release-artifacts` job + `!cancelled()` conditions
- **Cross-repo patched binary testing** — Cargo `--config patch` for testing precompile changes against downstream
- **SP1 ELF manifest automation** — ZK-specific CI for proof system artifacts
- **Binary source hash caching** — benchmark binaries cached by `hashFiles()` of source, not git SHA
- **Devnet cache warming** — separate Docker build targets (builder/consensus/batcher) cached on main push
- **Duplicate-aware AI review** — pre-check existing bot comments before posting new findings

---

## Source Requirements

All analysis is based on local codebase reading. No external API calls or web scraping required.

| Source Type | Description | Usage |
|---|---|---|
| **Primary** | Local workflow YAML files at `/Users/whisker/Work/src/networks/base/` | All per-workflow analysis |
| **Primary** | Local repo config files (VOUCHED.td, action.yml, benchmark configs) | Repo configuration analysis |
| **Primary** | Git commit SHAs at investigation time | Reproducibility anchoring |
| **Secondary** | GitHub Action marketplace docs (step-security/harden-runner, anthropics/claude-code-action, mitchellh/vouch) | Context for action capabilities |
| **Not available** | Branch protection rules, GitHub Environments, configured Apps, Secrets names | Noted as "不可访问 (权限受限)" per issue instructions |

---

## Diagram Expectations

| # | Diagram | Type | Purpose |
|---|---|---|---|
| 1 | Base CI Pipeline Flow | Flowchart | Show ci-pr → ci-core → ci-merge-queue tiered strategy with job dependencies |
| 2 | Release Pipeline Sequence | Sequence/Flow | start-release → create-rc → build-release → publish-release → verify-release chain |
| 3 | 10-Dimension Capability Matrix | Table/Heatmap | Visual rating grid across all three repos |
| 4 | Security Hardening Coverage | Matrix | harden-runner mode (block/audit/none) × workflow coverage |

---

## Quality Checklist

- [ ] Every workflow file from all three repos listed and categorized
- [ ] Per-workflow analysis includes triggers, purpose, category, notable patterns
- [ ] Repo-level config documented including explicitly missing files
- [ ] 10-dimension matrix has evidence-backed ratings
- [ ] Adoption recommendations are priority-ranked with complexity assessment
- [ ] All commit SHAs recorded for reproducibility
- [ ] Inaccessible configurations (branch protection, environments, apps) noted per issue instructions
- [ ] Diagrams planned for key architectural patterns
