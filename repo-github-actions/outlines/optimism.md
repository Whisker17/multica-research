---
topic: "Optimism GitHub Actions 完整调研"
project_slug: "github-action-optimization"
topic_slug: "optimism-github-actions"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "github-action-optimization/outlines/optimism-github-actions.md"
  draft: "github-action-optimization/research-sections/optimism-github-actions/drafts/round-{n}.md"
  final: "github-action-optimization/research-sections/optimism-github-actions/final.md"
  index: "github-action-optimization/research-sections/_index.md"

scope: "Complete audit of the Optimism monorepo (ethereum-optimism/optimism) GitHub Actions workflows, CircleCI configuration overview, Dependabot config, branch protection rules, CODEOWNERS, PR templates, and monorepo module structure. Codebase available locally at /Users/whisker/Work/src/networks/optimism/optimism/. Key focus areas: build-images.yaml (Docker build orchestration for 25+ components using a factory action pattern), security.yml (SLSA provenance verification), CircleCI configuration overview under .circleci/ (coverage scope, not exhaustive per-job analysis), Dependabot strategy (Go modules and Cargo), monorepo module breakdown as reference for mantle-v2 upstream sync planning. Note: Optimism's primary CI runs on CircleCI; GitHub Actions handles specific tasks only — both must be documented."
audience: "Mantle/mantle-v2 engineering team planning upstream sync strategy and CI/CD design"
expected_output: "Structured research document containing: (1) complete GitHub Actions workflow list with per-workflow analysis in standard format, (2) CircleCI config overview (which modules are covered, not exhaustive), (3) repo-level config overview (dependabot.yml, CODEOWNERS, PULL_REQUEST_TEMPLATE.md, branch protection if accessible, GitHub Environments if accessible, Secrets names if accessible), (4) 10-dimension capability matrix with maturity ratings (成熟/基础/缺失) annotated with GHA vs CircleCI attribution, (5) monorepo module structure overview for mantle-v2 sync reference, (6) patterns worth borrowing for Mantle. All conclusions must include specific file paths or URLs and the commit SHA at research time."

revision_metadata:
  created_by: "Deep Research Agent"
  created_at: "2026-06-10T13:45:00Z"
  last_modified_by: "Deep Research Agent"
  last_modified_at: "2026-06-10T13:45:00Z"
---

# Research Outline: Optimism GitHub Actions 完整调研

## Items

### item-1: GitHub Actions Workflow — build-images.yaml

Docker image build orchestration workflow covering 22 images (15 Go, 6 Rust, 1 infra) using the `ethereum-optimism/factory` reusable action pattern. This is the most complex GHA workflow in the repo and demonstrates a data-driven approach to multi-component Docker builds with path-based change detection, dynamic matrix generation via `.github/images.json`, cross-platform (amd64/arm64) verification, and GCP Artifact Registry publishing. Understanding this pattern is critical for mantle-v2 Docker build strategy.

- **Priority**: high
- **Dependencies**: none

### item-2: GitHub Actions Workflow — security.yml

SLSA provenance verification workflow that validates the `ci-base-clang` Docker image pinned in CircleCI config. It uses `gh attestation verify` with `--bundle-from-oci` to check supply chain provenance against `ethereum-optimism/factory`. This represents Optimism's supply chain security posture for CI base images. Analysis should cover the attestation verification mechanism, the pinning strategy (digest-based), and how changes to CircleCI config or the workflow itself trigger re-verification.

- **Priority**: high
- **Dependencies**: none

### item-3: Custom Actions & Factory Pattern

Analysis of the local composite action `.github/actions/docker-build-prep/` (git version computation via `just compute-git-versions`) and the external `ethereum-optimism/factory` reusable workflows/actions (plan action for matrix generation, docker.yaml for builds). This item covers the factory pattern architecture: how `images.json` declares the build manifest, how the plan action computes which images need rebuilding, and how `docker-bake.hcl` provides the build definition. This is the core abstraction that makes build-images.yaml manageable at scale.

- **Priority**: high
- **Dependencies**: item-1

### item-4: CircleCI Configuration Overview

Overview of the primary CI system covering the dynamic configuration setup (config.yml as setup config), the continuation pipeline architecture (3 continuation configs: main.yml at 3081 lines, rust-ci.yml at 985 lines, rust-e2e.yml at 261 lines, plus helpers.yml), the decision tree logic for workflow activation (15+ c-run_* flags), path-based change detection, and dispatch parameter system. Not an exhaustive per-job analysis — focus on architecture, module coverage mapping (which workflows test which monorepo modules), and the PR/merge-queue/post-merge lifecycle stages.

- **Priority**: high
- **Dependencies**: none

### item-5: Repo-Level Configuration

Audit of repository configuration files: `dependabot.yml` (gomod daily + cargo/kona daily with minor/patch ignore), `CODEOWNERS` (monorepo-reviewers default, consensus team exclusives, contract-reviewers with min:2, cloud-security for CODEOWNERS), `cliff.toml` (git-cliff changelog), `code-review-graph.instruction.md` (MCP tooling), `.github/images.json` (Docker build manifest). Also assess accessibility of: branch protection rules, GitHub Environments, configured GitHub Apps, and Secrets names — document what is accessible vs. permission-restricted.

- **Priority**: medium
- **Dependencies**: none

### item-6: Monorepo Module Structure

Catalog the 27+ top-level modules with their language, purpose, and CI coverage mapping. Key categories: Go services (op-node, op-batcher, op-proposer, op-challenger, op-conductor, op-deployer, etc.), Rust components (rust/kona, cannon), Solidity contracts (packages/contracts-bedrock), testing infrastructure (op-e2e, op-acceptance-tests), shared libraries (op-service, op-core, op-chain-ops), and developer tooling (op-devstack, op-wheel). Map each module to its Docker image (from images.json) and primary CI workflow (CircleCI vs GHA). This serves as the reference for mantle-v2 upstream sync module-by-module planning.

- **Priority**: medium
- **Dependencies**: item-1, item-4

### item-7: 10-Dimension Capability Matrix

Cross-cutting analysis producing a maturity rating (成熟/基础/缺失) for each of 10 CI/CD dimensions, annotated with whether the capability resides in GHA, CircleCI, or both. Proposed dimensions: (1) Build & Compile, (2) Unit/Integration Testing, (3) Contract Testing & Formal Verification, (4) Docker Image Management, (5) Supply Chain Security, (6) Release & Deployment, (7) Dependency Management, (8) Code Quality & Linting, (9) Scheduled/Maintenance Tasks, (10) Path-based Gating & Efficiency. Each dimension must cite specific file paths and distinguish between GHA and CircleCI implementations.

- **Priority**: high
- **Dependencies**: item-1, item-2, item-4, item-5

### item-8: Patterns Worth Borrowing for Mantle

Synthesis of actionable takeaways for the Mantle/mantle-v2 CI/CD design. Based on findings from all previous items, identify: (a) patterns to adopt directly (e.g., factory action pattern, data-driven image manifests, SLSA provenance), (b) patterns to adapt (e.g., dynamic CircleCI configuration adapted to GHA), (c) patterns to skip (e.g., CircleCI-specific features without GHA equivalents), and (d) gaps to address that Optimism hasn't solved. Each recommendation must reference the specific Optimism implementation and provide a concrete adoption path for mantle-v2.

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| file_paths | Exact file paths within the Optimism repo relevant to the item | all |
| trigger_events | GitHub/CI events that activate the workflow or feature (push, PR, schedule, dispatch) | item-1, item-2, item-4 |
| permissions_and_secrets | GitHub token permissions, OIDC, and secrets referenced (names only) | item-1, item-2, item-5 |
| external_dependencies | Third-party actions, orbs, services, or registries used | item-1, item-2, item-3, item-4 |
| path_filters | File path patterns used for change detection and conditional execution | item-1, item-2, item-4 |
| module_mapping | Which monorepo modules are covered by or related to this item | item-1, item-4, item-6 |
| maturity_rating | 成熟/基础/缺失 rating with justification and GHA vs CircleCI attribution | item-7 |
| mantle_relevance | Assessment of how relevant or transferable this finding is for mantle-v2 | all |
| commit_sha | Git commit SHA at which the analysis was performed | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | flow | build-images.yaml pipeline flow: plan → prep → build (matrix) → cross-platform check, showing data flow through images.json, factory/plan action, docker-bake.hcl, and GCP registry | mermaid | item-1, item-3 |
| diag-2 | architecture | CircleCI dynamic configuration architecture: config.yml (setup) → decision tree → continuation configs merge → workflow activation via c-run_* flags | mermaid | item-4 |
| diag-3 | hierarchy | Monorepo module taxonomy: Go services, Rust components, Solidity contracts, testing, shared libs, tooling — with Docker image and CI coverage annotations | mermaid | item-6 |
| diag-4 | comparison | 10-dimension capability matrix as a visual comparison chart with GHA vs CircleCI attribution and maturity ratings | ascii | item-7 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | Direct analysis of workflow YAML files, action definitions, CircleCI configs, and repo config files from the Optimism monorepo at a pinned commit SHA | 10 |
| src-2 | official_docs | GitHub Actions documentation for reusable workflows, OIDC, attestations; CircleCI docs for dynamic configuration and continuation | 3 |
| src-3 | code_analysis | Analysis of the `ethereum-optimism/factory` repository for understanding the reusable action/workflow patterns | 1 |
| src-4 | official_docs | SLSA framework documentation and GitHub attestation verification docs | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
