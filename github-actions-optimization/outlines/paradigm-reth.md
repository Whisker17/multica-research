# paradigmxyz/reth GitHub Actions 完整调研 — Structured Outline

> **Project slug**: `github-actions-optimization`
> **Topic slug**: `paradigm-reth`
> **Round**: 2
> **Multica issue**: `9930a544-1a59-4511-b863-73eb8b15e049`
> **Scope**: Complete investigation of paradigmxyz/reth's 30 GitHub Actions workflows and repo-level configuration. Key focus: advanced benchmark system (CPU pinning, SMT disable, ABBA cross-comparison, samply profiling, benchmarkoor-replay), reproducible build verification, upstream dependency compatibility (alloy-rs), Cyclops PR audit, comprehensive lint (16+ checks), multi-arch release with GPG signing, Ethereum integration testing (hive/kurtosis), Depot cloud builder integration.
> **Audience**: Mantle team evaluating which reth CI/CD patterns to adopt or adapt for their reth-fork pipeline.
> **Expected output**: Structured document with (1) complete 30-workflow inventory, (2) repo-level config overview, (3) 10-dimension capability matrix (成熟/基础/缺失), (4) Mantle-applicable patterns with rationale, (5) reth-unique innovations especially benchmark and reproducible build systems.
> **Investigation date**: 2026-06-10
> **Codebase SHA**: `9384bc53d8c0c77e59cac83fdaaf3b372c6d2216` (HEAD of main at investigation time)

---

## Section 1: Repo 级配置概况 (Repo-Level Configuration)

### 1.1 .github 目录结构

**Investigation fields**:
- `.github/workflows/` — 30 workflow files (full inventory in Section 2)
- `.github/CODEOWNERS` — **present** (verified via `gh api repos/paradigmxyz/reth/contents/.github/CODEOWNERS` at commit `9384bc53`); granular per-crate ownership model
- `.github/dependabot.yml` — dual ecosystem: `github-actions` (weekly, 7-day cooldown) + `cargo` (weekly, 7-day cooldown, grouped minor/patch updates under `cargo-weekly`, 1 open PR limit, `A-dependencies` label, `chore(deps)` commit prefix)
- `.github/actionlint.yaml` — self-hosted runner labels whitelist (deep draft to verify)
- `.github/ISSUE_TEMPLATE/` — **present**, 4 template files: `bug.yml`, `config.yml`, `docs.yml`, `feature.yml` (verified via GitHub API at commit `9384bc53`)
- `.github/PULL_REQUEST_TEMPLATE.md` — **absent**. Verified: `gh api repos/paradigmxyz/reth/contents/.github/PULL_REQUEST_TEMPLATE.md` returns HTTP 404 at commit `9384bc53d8c0c77e59cac83fdaaf3b372c6d2216`. Also checked `pull_request_template.md` (lowercase) and root-level `PULL_REQUEST_TEMPLATE.md` — all 404. The repository does not use a PR template.
- `.github/scripts/` — referenced by bench.yml (bench-*.sh, bench-*.py, bench-*.js), hive.yml (hive/ directory), lint.yml (check_wasm.sh, check_rv32imac.sh), integration.yml (install_geth.sh), docker.yml (verify_image_arch.sh), fetch-grafana-dashboard.yml, label-pr.yml (label_pr.js)
- `.github/assets/` — kurtosis_network_params.yaml referenced by kurtosis.yml

**Sources**: `gh api repos/paradigmxyz/reth/contents/.github` (all subdirectories enumerated)

### 1.2 Dependabot 配置分析

**Investigation fields**:
- GitHub Actions: weekly update cadence, 7-day cooldown
- Cargo: weekly update, grouped `cargo-weekly` for minor/patch across all packages (`*`), 7-day cooldown, `open-pull-requests-limit: 1` to avoid PR flood, `chore(deps)` prefix enforcing conventional commits
- Design choice: single PR for all grouped Cargo updates reduces review burden
- Comparison point: this is more conservative than many projects that use Renovate for finer control

### 1.3 CODEOWNERS 分析

**Investigation fields**:
- **Status**: `.github/CODEOWNERS` is **present** at commit `9384bc53` (verified via `gh api repos/paradigmxyz/reth/contents/.github/CODEOWNERS`; note: root-level `CODEOWNERS` returns 404 — the file lives under `.github/`)
- Deep draft to document: full ownership model, per-crate granularity, global vs subsystem maintainers, and implications for review governance

### 1.4 Repo Settings Access Plan

#### 1.4.1 Branch Protection Rules / Repo Rulesets

| Step | Method | Notes |
|---|---|---|
| (a) Primary | `gh api repos/paradigmxyz/reth/branches/main/protection` | Requires admin access |
| (a) Fallback | `gh api repos/paradigmxyz/reth/rulesets` | Public rulesets endpoint |
| (b) Inaccessible | Record as `不可访问 (权限受限)` | |

**Indirect evidence**: merge_group triggers in 8+ workflows (lint, unit, integration, e2e, compact, stage, grafana, lint-actions) imply merge queue enabled, which requires branch protection with status checks.

#### 1.4.2 GitHub Environments Configuration

| Step | Method | Notes |
|---|---|---|
| (a) Primary | `gh api repos/paradigmxyz/reth/environments` | Public for public repos |
| (b) Inaccessible | Record as `不可访问 (权限受限)` | |

**Indirect evidence**: `book.yml` deploy job uses `environment: name: github-pages` — at least one environment configured.

#### 1.4.3 Installed GitHub Apps

| Step | Method | Notes |
|---|---|---|
| (a) Heuristic | Infer from workflow secrets and action patterns | |
| (b) Inaccessible | Record as `不可访问 (权限受限)` | |

**Indirect evidence**: Depot CI (DEPOT_TOKEN, DEPOT_PROJECT_ID), Cyclops PR audit (EVENTS_KEY/EVENTS_CERT/EVENTS_ARGS), Slack integration (SLACK_WEBHOOK_URL, SLACK_HIVE_WEBHOOK_URL).

#### 1.4.4 Secrets Names List

**Known secrets from workflow files** (values never exposed):
- Build/Deploy: `GITHUB_TOKEN` (automatic), `DEPOT_TOKEN`, `HOMEBREW`
- Signing: `GPG_SIGNING_KEY`, `GPG_PASSPHRASE`
- Benchmark: `DEREK_TOKEN`, `DEREK_PAT`, `GH_PROJECT_TOKEN`, `BENCHMARKOOR_REPLAY_DEPLOY_KEY`, `BENCHMARKOOR_REPLAY_TOKEN`
- PR Audit: `EVENTS_KEY`, `EVENTS_CERT`, `EVENTS_ARGS`
- Notifications: `SLACK_WEBHOOK_URL`, `SLACK_HIVE_WEBHOOK_URL`
- Grafana: `FETCH_GRAFANA_DASHBOARD_URL`, `FETCH_GRAFANA_DASHBOARD_TOKEN`

**Known vars**: `DEPOT_PROJECT_ID`

### 1.5 Runner Strategy

**Investigation fields**:
- **Depot Cloud** as primary CI runner: `depot-ubuntu-latest`, `depot-ubuntu-latest-2/4/8/16` — sized by workload
- **Self-hosted bare metal** for benchmarks: `[self-hosted, Linux, X64, available]` — dedicated hardware for reproducible performance measurement
- **GitHub-hosted** for lightweight jobs: `ubuntu-latest`, `ubuntu-24.04`, `ubuntu-24.04-arm`, `macos-14`
- **Runner selection pattern**: `${{ github.repository == 'paradigmxyz/reth' && 'depot-ubuntu-latest' || 'ubuntu-latest' }}` — fork-friendly fallback to GitHub-hosted
- actionlint.yaml whitelists Depot runner labels to prevent false positives

---

## Section 2: Workflow 完整列表及逐个分析 (Complete Workflow Inventory & Per-Workflow Analysis)

Each workflow analyzed with: `name`, `triggers`, `key_jobs`, `runner_type`, `notable_patterns`, `custom_actions_or_reusable_workflows`.

### 2.1 Benchmark System (3 workflows) — 核心创新

#### 2.1.1 bench.yml — Engine API Block Replay Benchmark

| Field | Value |
|---|---|
| Triggers | `issue_comment` (created), `workflow_dispatch` (13 input parameters) |
| Key Jobs | `bench` (single, self-hosted bare metal, 180min timeout) |
| Runner | `[self-hosted, Linux, X64, available]` |
| Category | Benchmark |

**Investigation fields**:
- **Trigger model**: PR comment `/bench` command parsed via issue_comment event, plus manual dispatch with extensive parameterization
- **Input parameters**: `blocks` (count), `big_blocks` (mode with gas targets like 100M/2G), `bal` (block access lists), `warmup`, `baseline`/`feature` git refs, `wait_time`, `baseline_args`/`feature_args`, `samply` profiling toggle
- **ABBA cross-comparison**: when `repetitions=2`, runs baseline-1, feature-1, feature-2, baseline-2 to control for thermal drift and cache effects
- **System tuning for reproducibility**:
  - CPU governor set to `performance` mode
  - SMT/Hyperthreading disabled (offline sibling CPUs)
  - Transparent Huge Pages disabled
  - ASLR disabled (`randomize_va_space=0`)
  - `cpu_dma_latency` pinned to 0
  - IRQ affinity pinned to CPU 0
  - System services stopped: irqbalance, cron, atd, unattended-upgrades, snapd, prometheus exporters, sysstat
  - `taskset -c` for CPU core pinning during benchmark execution
- **Snapshot management**: `schelk` (thin-provisioning-based) for instant database state recovery between runs
- **Profiling**: optional `samply` CPU profiling integration
- **Build strategy**: parallel build of baseline, feature, and txgen binaries using background PIDs
- **Result processing**: Python summary scripts, Slack notification, ClickHouse upload for historical tracking, GitHub commit status updates
- **Custom scripts**: 17+ bench-related scripts in `.github/scripts/`
- **External tools**: `schelk` (thin-provisioning snapshot tool), MinIO client for snapshot storage, `benchmarkoor-replay`

**Sources**: `gh api` decoded content, `.github/scripts/bench-*.{sh,py,js}`

#### 2.1.2 bench-scheduled.yml — Nightly/Hourly/Release Regression Benchmarks

| Field | Value |
|---|---|
| Triggers | `schedule` (3 cron entries), `workflow_dispatch` |
| Key Jobs | `bench-scheduled` (self-hosted, 180min timeout) |
| Runner | `[self-hosted, Linux, X64, available]` |
| Category | Benchmark |

**Investigation fields**:
- **Three modes via cron schedule**:
  - `nightly` (05:30 UTC): previous nightly Docker build vs current nightly
  - `hourly` (every hour): main HEAD vs last benchmarked commit, skip if no new commits
  - `release` (09:00 UTC): latest GitHub release tag vs current nightly
- **State persistence**: uses `decofe/reth-bench-charts` repo to persist feature commit SHA between runs, enabling incremental comparison
- **Skip logic**: hourly mode skips if no new commits since last run or if a previous run is still in progress (concurrency lock)
- **Slack notification**: configurable policy (always, on-win, on-error, never)
- **Manual dispatch**: force flag to bypass skip logic, configurable blocks count and warmup
- **Same system tuning** as bench.yml (CPU governor, SMT disable, etc.)
- **ClickHouse integration**: structured metrics upload for historical trend analysis

#### 2.1.3 bench-benchmarkoor.yml — Benchmarkoor Replay Fixture Benchmarks

| Field | Value |
|---|---|
| Triggers | `workflow_dispatch` (20+ input parameters) |
| Key Jobs | `benchmarkoor` (self-hosted, 180min timeout) |
| Runner | `[self-hosted, Linux, X64, available]` |
| Category | Benchmark |

**Investigation fields**:
- **Purpose**: run standardized gas-metering test fixtures from `ethpandaops/benchmarkoor-tests` to measure EVM execution performance
- **Test selection**: multiple selectors (exact test, contains, regex pattern, opcode, gas bucket, cache strategy, account mode) with limit cap
- **Three-phase execution**: prepare (gas bump/funding checkpoint) then run comparison then parse results
- **Reset strategy**: `schelk` (thin-provisioning) or `unwind` for state reset between tests
- **Custom tooling**: `benchmarkoor-replay` (private repo `tempoxyz/benchmarkoor-replay`), `schelk` for snapshot management, MinIO for snapshot storage
- **Infrastructure dependencies**: linux-tools (perf), dmsetup, thin-provisioning-tools, jq, zstd
- **Result artifacts**: per-run JSONL results, summary JSON/Markdown, uploaded to GitHub Actions artifacts
- **Resource constraints**: `BENCH_MEMORY_MAX: 32G`, configurable CPU cores (default 6)
- **Reproducibility**: same system setup as bench.yml (CPU governor, SMT, THP, ASLR, IRQ affinity, service stops)

### 2.2 Release & Distribution (4 workflows)

#### 2.2.1 release.yml — Multi-Architecture Release Build

| Field | Value |
|---|---|
| Triggers | `push: tags: v*`, `workflow_dispatch` (dry_run toggle) |
| Key Jobs | `dry-run`, `extract-version`, `check-version`, `build` (4-target matrix), `draft-release`, `dry-run-summary` |
| Runner | `ubuntu-24.04`, `ubuntu-24.04-arm`, `macos-14` |
| Category | Release |

**Investigation fields**:
- **Build matrix**: 4 targets x 1 binary (`reth`):
  - `x86_64-unknown-linux-gnu` (ubuntu-24.04, `maxperf` profile, `-C target-cpu=x86-64-v3 -C target-feature=+pclmulqdq`)
  - `aarch64-unknown-linux-gnu` (ubuntu-24.04-arm, `maxperf` profile, native build)
  - `x86_64-apple-darwin` (macos-14, `maxperf` profile, x86-64-v3)
  - `aarch64-apple-darwin` (macos-14, `maxperf` profile, native)
- **Performance optimization**: `maxperf` Cargo profile, `x86-64-v3` ISA level targeting, `pclmulqdq` for CRC acceleration
- **Build tools**: `mold` linker, `cross` for cross-compilation (non-native targets)
- **GPG signing**: all binary tarballs GPG-signed with repo secret key
- **Version validation**: Cargo.toml version must match git tag (allows RC suffixes)
- **Dry run mode**: builds artifacts but skips upload and release creation
- **Draft release**: auto-generated changelog from git log, pre-release flag for `-rc` tags, structured release notes template
- **Derived from Lighthouse**: workflow comments credit Lighthouse/OpenEthereum lineage
- **Permissions model**: explicit `permissions: {}` at workflow level, per-job grants

#### 2.2.2 release-dist.yml — Homebrew Distribution

| Field | Value |
|---|---|
| Triggers | `release: types: [published]` |
| Key Jobs | `release-homebrew` |
| Runner | `ubuntu-latest` |
| Category | Release |

**Investigation fields**:
- Auto-publishes to Homebrew via `dawidd6/action-homebrew-bump-formula`
- Uses `paradigmxyz/brew` tap (custom Homebrew tap)
- `no_fork: true` — direct push to tap repo
- Triggered only on published (non-draft) releases

#### 2.2.3 release-reproducible.yml — Reproducible Build Release Artifacts

| Field | Value |
|---|---|
| Triggers | `workflow_run: workflows: [release], types: [completed]` |
| Key Jobs | `extract-version`, `build-reproducible` |
| Runner | `ubuntu-latest` |
| Category | Release |

**Investigation fields**:
- **Chain trigger**: fires after `release.yml` completes successfully
- **Reproducible binary**: built via `Dockerfile.reproducible` with pinned Rust toolchain
- **Output artifacts**: reproducible binary tarball + `.deb` package, both GPG-signed
- **Docker image**: pushed to `ghcr.io/paradigmxyz/reth-reproducible:{version}` and `:latest`
- **GitHub release upload**: artifacts appended to existing release
- **Version extraction**: resolves tag from `workflow_run.head_sha` via GitHub refs API

#### 2.2.4 docker-tag-latest.yml — Manual Docker Latest Tag

| Field | Value |
|---|---|
| Triggers | `workflow_dispatch` (version input, tag_reth toggle) |
| Key Jobs | `tag-reth-latest` |
| Runner | `ubuntu-24.04` |
| Category | Release |

**Investigation fields**:
- Manual-only: allows retroactively tagging a specific release version as `:latest`
- Simple pull, tag, push pattern via GHCR

### 2.3 Docker & Container Builds (2 workflows)

#### 2.3.1 docker.yml — Primary Docker Image Build

| Field | Value |
|---|---|
| Triggers | `push: tags: v*`, `schedule: 0 1 * * *`, `workflow_dispatch` (build_type, dry_run) |
| Key Jobs | `build`, `notify` |
| Runner | `ubuntu-24.04` |
| Category | CD/Infra |

**Investigation fields**:
- **Depot cloud builder**: `depot/setup-action` + `depot/bake-action` with `docker-bake.hcl`
- **Three build types**: tagged release (v* push), nightly (cron), git-sha (manual dispatch)
- **Tag strategy**: release = `{version}` + `latest` (non-RC only); nightly = `nightly`; manual = `{sha}`
- **Image arch verification**: `.github/scripts/verify_image_arch.sh`
- **vergen integration**: Git SHA/describe/dirty injected as build args
- **Slack notification on nightly failure** with specific user ping
- **Dry run**: `push: false` when dry_run enabled

#### 2.3.2 docker-test.yml — Reusable Test Image Builder

| Field | Value |
|---|---|
| Triggers | `workflow_call` (hive_target, artifact_name inputs) |
| Key Jobs | `build` (45min timeout) |
| Runner | `ubuntu-latest` |
| Category | CI/Testing |

**Investigation fields**:
- Reusable workflow called by `hive.yml` and `kurtosis.yml`
- Fork detection: Depot for upstream, Docker Buildx for forks
- Artifact output: Docker image saved to tarball, uploaded as artifact
- `docker-bake.hcl` targets with vergen metadata

### 2.4 Ethereum Integration Testing (2 workflows)

#### 2.4.1 hive.yml — Ethereum Hive Test Suite

| Field | Value |
|---|---|
| Triggers | `workflow_dispatch`, `schedule: 0 0 * * *` |
| Key Jobs | `build-reth`, `prepare-hive` (Amsterdam/Osaka), `test-amsterdam` (20+ scenarios), `test-osaka` (19+ scenarios), `notify-on-error` |
| Runner | Depot `depot-ubuntu-latest-4` / `depot-ubuntu-latest-8` |
| Category | Integration Testing |

**Investigation fields**:
- **Dual fork variants**: Amsterdam and Osaka tested in parallel
- **40+ test scenarios**: smoke, sync, devp2p, engine API, rpc-compat, EELS consume-engine (10 fork eras), EELS consume-rlp (10 fork eras)
- **Hive assets caching**: Go simulators cached by commit hash + build script hash
- **Expected failure management**: `expected_failures.yaml` + `ignored_tests.yaml`
- **Runner sizing**: 8-core for eels tests (memory-intensive)
- **Slack notification**: dedicated hive webhook
- **Uses reusable workflow**: `docker-test.yml`

#### 2.4.2 kurtosis.yml — Multi-Client Network Testing

| Field | Value |
|---|---|
| Triggers | `workflow_dispatch`, `schedule: 0 0 * * *`, `push: tags: *` |
| Key Jobs | `build-reth`, `test`, `notify-on-error` |
| Runner | Depot `depot-ubuntu-latest` |
| Category | Integration Testing |

**Investigation fields**:
- `ethpandaops/kurtosis-assertoor-github-action` for multi-client devnet testing
- Network params: `.github/assets/kurtosis_network_params.yaml`
- Uses reusable workflow: `docker-test.yml` (kurtosis target)
- Slack notification on failure

### 2.5 Lint & Static Analysis (3 workflows, 16+ check types)

#### 2.5.1 lint.yml — Comprehensive Rust Lint Suite

| Field | Value |
|---|---|
| Triggers | `pull_request`, `merge_group`, `push: branches: [main]` |
| Key Jobs | 15 jobs: clippy-binaries, clippy, wasm, riscv, crate-checks (3 partitions), msrv, docs, fmt, udeps, book, typos, check-toml, grafana, no-test-deps, feature-propagation, deny, lint-success |
| Runner | Depot (various sizes) + `ubuntu-latest` |
| Category | Lint/Quality |

**Investigation fields**:
- **16+ check types**: clippy (stable + nightly), wasm, riscv, crate-checks (partitioned 3-way), MSRV (1.93), docs, fmt, udeps, book CLI staleness, typos, TOML format, Grafana JSON, no-test-deps, feature-propagation (zepter), cargo-deny
- **Success gate**: `re-actors/alls-green` aggregation
- **Build acceleration**: sccache + rust-cache + mold across all Rust jobs
- **Partitioned compilation**: crate-checks split into 3 partitions
- **Fork-friendly runner selection**

#### 2.5.2 lint-actions.yml — GitHub Actions Workflow Linting

| Field | Value |
|---|---|
| Triggers | `pull_request` (paths: .github/**), `merge_group`, `push` (paths: .github/**) |
| Key Jobs | `actionlint` |
| Runner | `ubuntu-latest` |

**Investigation fields**:
- `actionlint` with `SHELLCHECK_OPTS="-S error"`
- Path-filtered: only on `.github/` changes

#### 2.5.3 pr-title.yml — Conventional Commit PR Title Enforcement

| Field | Value |
|---|---|
| Triggers | `pull_request: [opened, reopened, edited, synchronize]` |
| Key Jobs | `conventional-title` |
| Runner | `ubuntu-latest` |

**Investigation fields**:
- `amannn/action-semantic-pull-request`
- Allowed types: feat, fix, chore, test, bench, perf, refactor, docs, ci, revert, deps
- Sticky PR comment for invalid titles, auto-deleted on fix

### 2.6 Testing Workflows (5 workflows)

#### 2.6.1 unit.yml — Unit & State Tests

| Field | Value |
|---|---|
| Triggers | `pull_request`, `merge_group`, `push: branches: [main]` |
| Key Jobs | `test`, `state` (ef-tests), `doc` (doctests), `unit-success` |
| Runner | Depot `depot-ubuntu-latest-4/8` |

**Investigation fields**:
- `cargo-nextest` for parallel test execution
- Ethereum state tests: pinned `ethereum/tests` + EEST v4.5.0 fixtures
- `unit-success` aggregation via `re-actors/alls-green`

#### 2.6.2 integration.yml — Integration Tests

| Field | Value |
|---|---|
| Triggers | `pull_request`, `merge_group`, `push: branches: [main]`, `schedule: 0 3 * * *` |
| Key Jobs | `test`, `integration-success`, `era-files` (scheduled) |
| Runner | Depot `depot-ubuntu-latest-4` |

**Investigation fields**:
- Geth installation for cross-client testing
- ERA file integration tests daily (scheduled, `--ignored` flag)

#### 2.6.3 e2e.yml — End-to-End Tests

| Field | Value |
|---|---|
| Triggers | `pull_request`, `merge_group`, `push: branches: [main]` |
| Key Jobs | `test` (e2e_testsuite), `rocksdb` |
| Runner | Depot `depot-ubuntu-latest-4` |

**Investigation fields**:
- Separate RocksDB backend e2e testing
- 90min timeout

#### 2.6.4 stage.yml — Staged Sync Execution Tests

| Field | Value |
|---|---|
| Triggers | `pull_request`, `merge_group`, `push: branches: [main]` |
| Key Jobs | `stage` (merge_group only) |
| Runner | Depot `depot-ubuntu-latest` |

**Investigation fields**:
- **Merge-group-only execution**: runs only in merge queue, not on regular PRs
- Sequential stage execution: headers, bodies, senders, execution, merkle, tx-lookup, account-history, storage-history (blocks 0-50000)
- Deliberately omits account-hashing/storage-hashing (no-ops with storage v2)

#### 2.6.5 compact.yml — Compact Codec Backward Compatibility

| Field | Value |
|---|---|
| Triggers | `pull_request`, `merge_group`, `push: branches: [main]` |
| Key Jobs | `compact-codec` |
| Runner | Depot `depot-ubuntu-latest` |

**Investigation fields**:
- Two-phase: generate test vectors on `main`, deserialize on PR branch
- Protects against breaking `Compact` codec serialization changes

### 2.7 Reproducible Build Verification (1 workflow)

#### 2.7.1 reproducible-build.yml — Cross-Machine Build Verification

| Field | Value |
|---|---|
| Triggers | `workflow_dispatch`, `schedule: 0 1 */2 * *` (every 2 days) |
| Key Jobs | `build` (2-machine matrix), `compare` |
| Runner | `ubuntu-latest`, `ubuntu-22.04` |

**Investigation fields**:
- Dual-machine strategy: `ubuntu-latest` vs `ubuntu-22.04` both build via `Dockerfile.reproducible`
- SHA256 comparison: mismatch = non-reproducible
- Docker-based build with pinned Rust toolchain
- Two different Ubuntu versions prove Docker isolation

### 2.8 Upstream Compatibility (1 workflow)

#### 2.8.1 check-alloy.yml — Alloy Breaking Change Detection

| Field | Value |
|---|---|
| Triggers | `workflow_dispatch` (alloy_branch, alloy_evm_branch, op_alloy_branch) |
| Key Jobs | `check` |
| Runner | Depot `depot-ubuntu-latest-16` |

**Investigation fields**:
- Detects breaking changes from alloy-rs before they land
- `scripts/patch-alloy.sh` applies Cargo patches for 3 upstream repos
- `cargo clippy --workspace --all-features` after patching
- Manual-only (not automated on upstream changes)
- 16-core runner for full workspace compile

### 2.9 PR Audit & Governance (2 workflows)

#### 2.9.1 pr-audit.yml — Cyclops PR Audit

| Field | Value |
|---|---|
| Triggers | `pull_request: types: [labeled]` |
| Key Jobs | `publish` |
| Runner | `ubuntu-latest` |

**Investigation fields**:
- Label-gated: fires only on `cyclops` label
- Publishes PR event to external audit service via mTLS
- Minimal permissions: `permissions: {}`

#### 2.9.2 label-pr.yml — Automated PR Labeling

| Field | Value |
|---|---|
| Triggers | `pull_request: types: [opened]` |
| Key Jobs | `label_prs` |
| Runner | `ubuntu-latest` |

**Investigation fields**:
- Custom JS logic: `.github/scripts/label_pr.js` via `actions/github-script`

### 2.10 Sync & Blockchain Tests (2 workflows)

#### 2.10.1 sync.yml — Mainnet Sync Test

| Field | Value |
|---|---|
| Triggers | `workflow_dispatch`, `schedule: 0 */6 * * *` |
| Key Jobs | `sync` |
| Runner | Depot `depot-ubuntu-latest` |

**Investigation fields**:
- Syncs mainnet blocks 0-100000, verifies block hash, tests unwind

#### 2.10.2 sync-era.yml — ERA-Enabled Sync Test

| Field | Value |
|---|---|
| Triggers | `workflow_dispatch`, `schedule: 0 */6 * * *` |
| Key Jobs | `sync` |
| Runner | Depot `depot-ubuntu-latest` |

**Investigation fields**:
- Same as sync.yml but with `--era.enable` flag

### 2.11 Documentation (1 workflow)

#### 2.11.1 book.yml — Vocs Documentation Site

| Field | Value |
|---|---|
| Triggers | `push: branches: [main]`, `pull_request: branches: [main]`, `merge_group` |
| Key Jobs | `build` (90min timeout), `deploy` (main-only) |
| Runner | Depot `depot-ubuntu-latest-8`, `ubuntu-latest` |

**Investigation fields**:
- Vocs framework with Cargo docs integration
- Playwright Chromium for Mermaid diagram rendering
- Build verification: explicit file existence checks
- GitHub Pages deployment

### 2.12 Infrastructure & Monitoring (3 workflows)

#### 2.12.1 grafana.yml — Dashboard Validation

| Field | Value |
|---|---|
| Triggers | `pull_request`, `merge_group`, `push: branches: [main]` |
| Key Jobs | `check-dashboard` |
| Runner | `ubuntu-latest` |

**Investigation fields**: Python validation of dashboard JSON structure

#### 2.12.2 fetch-grafana-dashboard.yml — Dashboard Sync from Grafana

| Field | Value |
|---|---|
| Triggers | `workflow_dispatch` (dashboard_uid, target_path) |
| Key Jobs | `fetch` |
| Runner | `ubuntu-latest` |

**Investigation fields**: Exports live Grafana dashboard to repo, auto-creates PR

#### 2.12.3 stale.yml — Issue/PR Lifecycle

| Field | Value |
|---|---|
| Triggers | `workflow_dispatch`, `schedule: 30 1 * * *` |
| Key Jobs | `close-issues` |
| Runner | `ubuntu-latest` |

**Investigation fields**: 21-day stale, 7-day close, `M-prevent-stale` exemption

### 2.13 Dependency Management (1 workflow)

#### 2.13.1 dependencies.yml — Automated Cargo Update

| Field | Value |
|---|---|
| Triggers | `schedule: 0 0 * * SUN`, `workflow_dispatch` |
| Key Jobs | `update` (reusable from `tempoxyz/ci`) |
| Runner | (defined by reusable workflow) |

**Investigation fields**: Weekly `cargo update` PR via `tempoxyz/ci/.github/workflows/cargo-update-pr.yml@main`

---

## Section 3: Security & Supply Chain Analysis

**Investigation fields**:
- **Action pinning**: ALL actions pinned by full SHA hash (e.g., `actions/checkout@de0fac2e...`)
- **Permissions model**: `permissions: {}` at workflow level (deny all), explicit per-job grants
- **persist-credentials: false**: universal on all `actions/checkout` calls
- **GPG signing**: release binaries + reproducible binaries
- **No harden-runner**: unlike Base, reth does not use `step-security/harden-runner`
- **Fork-friendly runner fallback**: expression-based runner selection
- **OIDC tokens**: `id-token: write` only for Depot authentication
- **Reusable workflow trust**: `tempoxyz/ci` from `@main` (not SHA-pinned)
- **Secret isolation**: secrets scoped to specific jobs

---

## Section 4: 10-Dimension Capability Matrix

| # | Dimension | Expected Rating | Key Evidence |
|---|---|---|---|
| 1 | Benchmark System | 成熟 | 3 workflows, bare-metal runners, ABBA comparison, CPU pinning, SMT disable, samply, ClickHouse, hourly regression, benchmarkoor |
| 2 | Reproducible Build | 成熟 | `reproducible-build.yml` (dual-machine SHA256), `release-reproducible.yml`, `Dockerfile.reproducible` |
| 3 | Release Pipeline | 成熟 | Multi-arch (4 targets), GPG signing, dry run, Homebrew, reproducible artifacts, Docker nightly/release |
| 4 | CI/Testing | 成熟 | 5 test workflows, 16+ lint checks, nextest, ef-tests/EEST, hive (40+ scenarios), kurtosis, compact compat, staged sync |
| 5 | Security & Supply Chain | 成熟 | Universal SHA pinning, `permissions: {}`, `persist-credentials: false`, GPG signing, Cyclops audit |
| 6 | Upstream Compatibility | 基础 | `check-alloy.yml` manual-only |
| 7 | PR Governance | 成熟 | Conventional commits, merge queue, Cyclops audit, automated labeling, CODEOWNERS (present at `.github/CODEOWNERS`); no PR template |
| 8 | Documentation | 基础-成熟 | Vocs + Cargo docs, Mermaid, GitHub Pages; single workflow |
| 9 | Monitoring & Observability | 基础 | Grafana dashboard GitOps, Slack notifications, ClickHouse metrics; benchmark-focused |
| 10 | Dependency Management | 成熟 | Dependabot (dual ecosystem), weekly cargo update, udeps, cargo-deny |

**Investigation fields per dimension**: supporting workflows, evidence, gaps, Mantle comparison

---

## Section 5: 值得 Mantle 借鉴的具体 Workflow 及理由 (Mantle Adoption Recommendations)

**Investigation fields** — priority-ranked:

1. **Benchmark System** — CPU pinning, SMT disable, ABBA comparison, hourly regression; Mantle lacks automated perf regression on reth fork
2. **Reproducible Build Verification** — dual-machine SHA256; critical for L2 node supply chain trust
3. **Compact Codec Backward Compatibility** — prevents breaking serialization; directly applicable to Mantle reth fork DB layer
4. **Merge-Group-Gated Heavy Tests** — stage.yml pattern saves CI cost
5. **Check-Alloy Upstream Compatibility** — adaptable for OP Stack or reth upstream change detection
6. **Universal SHA Pinning + persist-credentials: false** — security baseline
7. **Conventional Commit Enforcement** — improves changelog and release notes
8. **CODEOWNERS with Granular Crate Ownership** (present at `.github/CODEOWNERS`) — expert review per subsystem
9. **Depot Cloud Builder** — faster Docker builds, `docker-bake.hcl` multi-target pattern
10. **Grafana Dashboard GitOps** — dashboard as code with PR review

---

## Section 6: Reth 独特模式或创新点 (Reth-Unique Patterns & Innovations)

**Investigation fields**:
- **schelk thin-provisioning snapshots** — instant DB state recovery via Linux thin provisioning
- **Benchmarkoor-replay fixture testing** — standardized gas-metering fixtures with per-opcode selectors
- **Three-mode scheduled benchmarks** — nightly/hourly/release with external state persistence
- **ABBA cross-comparison** — thermal/cache drift control in benchmarks
- **System-level benchmark isolation** — 15+ system tuning steps
- **ClickHouse metrics pipeline** — structured upload for trend analysis
- **Compact codec backward compat testing** — generate on main, deserialize on PR
- **Dual reproducible build verification** — two Ubuntu versions prove Docker isolation
- **Workflow-run chain trigger** — release completion auto-triggers reproducible build
- **Fork-friendly runner expression** — Depot fallback for forks
- **docker-bake.hcl multi-target** — HCL Docker Bake for multiple image targets
- **Hive dual-fork testing** — Amsterdam + Osaka in parallel, 40+ scenarios
- **re-actors/alls-green gate** — lint/test job aggregation pattern

---

## Source Requirements

| Source Type | Description | Usage |
|---|---|---|
| **Primary** | GitHub API via `gh api repos/paradigmxyz/reth/contents/` | All workflow YAML, decoded from base64 |
| **Primary** | Commit SHA `9384bc53d8c0c77e59cac83fdaaf3b372c6d2216` | Time-anchored analysis |
| **Secondary** | GitHub Action marketplace docs | Action capability context |
| **Not available** | Branch protection, Environments, Apps, secrets list | Attempt API; record `不可访问` if blocked |

---

## Diagram Expectations

| # | Diagram | Type | Purpose |
|---|---|---|---|
| 1 | Benchmark Architecture | Flowchart | Three bench workflows, triggers, shared infra (schelk, self-hosted, ClickHouse), ABBA pattern |
| 2 | Release Pipeline Chain | Sequence | release.yml, release-reproducible.yml, release-dist.yml, docker.yml |
| 3 | CI/Testing Pyramid | Layered | lint (PR+merge), unit/integration/e2e (PR+merge), stage (merge-only), hive/kurtosis (scheduled), sync (6h), bench (on-demand) |
| 4 | 10-Dimension Capability Matrix | Heatmap | Rating grid with evidence per dimension |

---

## Quality Checklist

- [ ] All 30 workflow files listed and categorized
- [ ] Per-workflow analysis includes triggers, key jobs, runner type, notable patterns
- [ ] Repo-level config documented (CODEOWNERS, dependabot, actionlint, scripts, issue templates)
- [ ] Benchmark system has detailed analysis (runner config, comparison methods, profiling, system tuning)
- [ ] Reproducible build system fully analyzed
- [ ] 10-dimension matrix has evidence-backed ratings
- [ ] Adoption recommendations are priority-ranked with rationale
- [ ] Commit SHA recorded for reproducibility
- [ ] Inaccessible configurations noted per issue instructions
- [ ] Diagrams planned for key architectural patterns
- [ ] All custom scripts enumerated
- [ ] Reusable workflows and workflow chains documented
