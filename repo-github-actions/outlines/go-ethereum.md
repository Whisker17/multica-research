---
topic: "go-ethereum GitHub Actions 完整调研"
project_slug: github-action-optimization
topic_slug: go-ethereum
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: github-action-optimization/outlines/go-ethereum.md
  draft: github-action-optimization/research-sections/go-ethereum/drafts/round-{n}.md
  final: github-action-optimization/research-sections/go-ethereum/final.md
  index: github-action-optimization/research-sections/_index.md

scope: |
  对 ethereum/go-ethereum 仓库的 GitHub Actions workflows 及 repo 级配置进行完整调研。
  枚举 .github/workflows/ 下所有 workflow 文件、.github/ 下的治理和自动化配置文件。
  对 branch protection rules/rulesets、其他 CI 系统（Travis CI、Jenkins 等）、GitHub Apps、
  secrets 名称进行调研——可通过公开 API 或 repo 页面访问的配置直接记录，不可访问的标注
  "不可访问 (权限受限)" 并注明尝试方式。逐个分析每个 workflow。按 10 个改进维度分类并
  输出能力评级。go-ethereum 作为 op-geth 的间接上游（Go 项目 CI 模式参考），重点提炼
  对 Mantle op-geth 有借鉴价值的模式。
audience: |
  Mantle 团队工程师和 DevOps，特别是负责 op-geth CI/CD 管线的工程师；需要评估
  go-ethereum Go CI 模式对 Mantle op-geth 参考价值的技术决策者。读者熟悉 Go 项目
  基本 CI 概念（go test、golangci-lint），但不一定熟悉 go-ethereum 的 build/ci.go
  自定义构建系统。
expected_output: |
  - Workflow 完整列表及逐个分析
  - Repo 级配置概况（CODEOWNERS、issue templates、stale/no-response bot、rulesets）
  - 10 维度能力矩阵（成熟/基础/缺失评级）
  - Go 项目 CI 模式的参考价值（build/ci.go 模式、self-hosted runner 策略、多平台测试）
  - 值得 Mantle op-geth 借鉴的模式

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-10T14:00:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-10T14:10:00Z"
  rounds:
    - round: 1
      commit: "https://github.com/Whisker17/multica-research/commit/064241eb04455cfad4d40fac4cf06f1c915ee34d"
      verdict: revise
    - round: 2
      adversarial_comment_id: null
      patches_applied:
        - "Mandatory: Add explicit 'absent' entries for .github/dependabot.yml and .github/PULL_REQUEST_TEMPLATE.md with verification method"
---

# Research Outline: go-ethereum GitHub Actions 完整调研

> **调研对象**: ethereum/go-ethereum (Go, LGPL-3.0)
> **调研日期**: 2026-06-10
> **Codebase SHA**: `11f0a8318bd8091d1caaf6d47df1bacf83646046` (master)
> **注意**: go-ethereum 仅有 3 个 GitHub Actions workflow 文件，大部分历史 CI 曾运行在 Travis CI 上（现已迁移）。当前 CI 以 GitHub Actions + self-hosted runners 为主。

## Items

### item-1: Repo 级配置概况

枚举并分析 go-ethereum 仓库 .github/ 目录下所有配置文件，以及通过 API 可获取的 repo 级设置。go-ethereum 的 repo 治理模式（CODEOWNERS、issue 模板、bot 自动化）对理解其 CI 策略的上下文至关重要。

调研必须覆盖以下路径并明确记录存在/缺失状态：

| Path | Status | Verification Method |
|------|--------|-------------------|
| `.github/workflows/` | **存在** (3 files: go.yml, freebsd.yml, validate_pr.yml) | GitHub Contents API `GET /repos/ethereum/go-ethereum/contents/.github/workflows` at SHA `11f0a831` |
| `.github/CODEOWNERS` | **存在** (~30 directories, ~10 maintainers) | GitHub Contents API at SHA `11f0a831` |
| `.github/CONTRIBUTING.md` | **存在** | GitHub Contents API at SHA `11f0a831` |
| `.github/ISSUE_TEMPLATE/` | **存在** (bug.md, feature.md, question.md) | GitHub Contents API at SHA `11f0a831` |
| `.github/no-response.yml` | **存在** (30-day auto-close) | GitHub Contents API at SHA `11f0a831` |
| `.github/stale.yml` | **存在** (366-day stale, 42-day close) | GitHub Contents API at SHA `11f0a831` |
| `.github/dependabot.yml` | **缺失** | GitHub Contents API returned HTTP 404 at SHA `11f0a8318bd8091d1caaf6d47df1bacf83646046`; also confirmed absent in `.github/` directory listing which returned only: CODEOWNERS, CONTRIBUTING.md, ISSUE_TEMPLATE, no-response.yml, stale.yml, workflows |
| `.github/PULL_REQUEST_TEMPLATE.md` | **缺失** | GitHub Contents API returned HTTP 404 at SHA `11f0a8318bd8091d1caaf6d47df1bacf83646046`; also confirmed absent in `.github/` directory listing |

- **Priority**: high
- **Dependencies**: none

### item-2: go.yml — 主 CI Workflow 分析

深入分析 go-ethereum 的核心 CI workflow (go.yml)，这是最复杂的 workflow，包含 lint、test（Go 版本矩阵）、32-bit 测试、Windows 构建/测试、keeper 构建等 5 个 jobs。使用 self-hosted runners 和自定义 build/ci.go 构建工具。

- **Priority**: high
- **Dependencies**: item-1

### item-3: freebsd.yml — FreeBSD CI 分析

分析 FreeBSD 平台测试 workflow，使用 vmactions/freebsd-vm 在 ubuntu-latest 上运行 FreeBSD 15.0 VM。调研其触发策略（仅 freebsd-github-action 分支 + workflow_dispatch）及 VM-based 跨平台测试模式。

- **Priority**: medium
- **Dependencies**: none

### item-4: validate_pr.yml — PR 格式验证分析

分析 PR 格式验证 workflow，包含两个阶段：自动关闭 conventional-commit 格式的疑似 spam PR（feat:/fix:/chore:）以及验证 PR 标题的 `directory: description` 格式并检查目录是否存在。

- **Priority**: medium
- **Dependencies**: none

### item-5: build/ci.go 自定义构建系统分析

go-ethereum 使用 ~45KB 的 Go 程序 (build/ci.go) 作为统一 CI 入口点，封装 lint、test、install、archive、debsrc、keeper 等命令。Makefile 作为薄封装层。checksums.txt 提供构建工具的 SHA256 校验（Go、golangci-lint、protoc）。这是一个值得 Mantle 参考的 Go 项目 CI 模式。

- **Priority**: high
- **Dependencies**: item-2

### item-6: 其他 CI 系统与外部构建基础设施

调研 go-ethereum 除 GitHub Actions 以外的 CI 系统，包括：历史 Travis CI 使用（build/ci-notes.md、travis_keepalive.sh）、Launchpad PPA Debian 包构建（build/bot/ppa-build.sh）、macOS 构建/Azure 上传（build/bot/macos-build.sh）、以及 GitHub 提供的动态服务（Copilot code review/agent、Dependabot Updates/Dependency Graph）。

- **Priority**: medium
- **Dependencies**: item-1

### item-7: 10 维度能力矩阵

按照项目统一的 10 个改进维度对 go-ethereum 进行能力评级（成熟/基础/缺失），每个评级需有具体 workflow 文件或配置的证据支撑。go-ethereum 作为成熟 Go 项目，某些维度（如 release pipeline、AI review）可能评级较低，但其 Go CI 基础设施和 repo 治理模式具有参考价值。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6

### item-8: 值得 Mantle op-geth 借鉴的模式

从 go-ethereum 的 CI 实践中提炼对 Mantle op-geth 有借鉴价值的具体模式，按优先级排序并评估实施复杂度。重点关注：build/ci.go 模式、self-hosted runner 策略、Go 版本矩阵测试、多平台覆盖（Linux/Windows/FreeBSD/32-bit）、PR 格式治理、repo 治理自动化等。

- **Priority**: high
- **Dependencies**: item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| file_path | Workflow 文件在仓库中的完整路径 | item-2, item-3, item-4 |
| triggers | Workflow 触发条件（push/PR/schedule/dispatch/workflow_call） | item-2, item-3, item-4 |
| runner_type | 运行器类型（self-hosted 规格/ubuntu-latest/windows） | item-2, item-3, item-4 |
| job_dependency_graph | Jobs 之间的依赖关系和执行顺序 | item-2 |
| concurrency_strategy | 并发控制策略（group 命名、cancel-in-progress） | item-2, item-3, item-4 |
| go_version_strategy | Go 版本选择和矩阵策略 | item-2, item-3, item-5 |
| cache_strategy | 缓存策略（build tools cache、checksums.txt key） | item-2, item-5 |
| ci_go_commands | build/ci.go 提供的命令及其功能 | item-5 |
| security_patterns | 安全相关模式（action pinning、permissions、fork safety） | all |
| capability_rating | 能力评级（成熟/基础/缺失）及支撑证据 | item-7 |
| adoption_priority | 对 Mantle op-geth 的借鉴优先级和实施复杂度 | item-8 |
| access_method | 数据获取方式（API/repo page/code/不可访问） | item-1, item-6 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | flow | go.yml workflow 的 job 依赖关系流程图：lint → test(matrix) → test-32bit/keeper, lint → windows(matrix) | mermaid | item-2 |
| diag-2 | architecture | build/ci.go 构建系统架构：Makefile → ci.go → (lint/test/install/archive/debsrc/keeper)，checksums.txt 校验链 | mermaid | item-5 |
| diag-3 | comparison | 10 维度能力矩阵可视化：维度 × 评级热力表 | ascii | item-7 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | go-ethereum .github/workflows/ 下所有 workflow YAML 文件的完整分析 | 3 |
| src-2 | code_analysis | go-ethereum .github/ 目录下的配置文件（CODEOWNERS、stale.yml、no-response.yml、ISSUE_TEMPLATE/） | 4 |
| src-3 | code_analysis | build/ 目录下的 CI 相关文件（ci.go、Makefile、checksums.txt、ci-notes.md、bot/） | 3 |
| src-4 | official_docs | GitHub API 获取的 repo 配置（rulesets、branch protection） | 1 |
| src-5 | code_analysis | go-ethereum GitHub Actions 最近运行记录（验证 workflow 活跃状态） | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-1 | Add explicit "absent" entries for `.github/dependabot.yml` and `.github/PULL_REQUEST_TEMPLATE.md` with verification method (HTTP 404 + directory listing), per issue acceptance criteria | Adversarial review via Orchestrator revision request |
