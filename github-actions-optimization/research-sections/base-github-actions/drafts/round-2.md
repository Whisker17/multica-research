---
topic: "Base GitHub Actions 完整调研"
project_slug: github-actions-optimization
topic_slug: base-github-actions
github_repo: Whisker17/multica-research
round: 2
status: draft
artifact_paths:
  outline: github-actions-optimization/outlines/base-github-actions.md
  draft: github-actions-optimization/research-sections/base-github-actions/drafts/round-2.md
  final: github-actions-optimization/research-sections/base-github-actions/final.md
draft_metadata:
  investigation_date: "2026-06-10"
  codebase_shas:
    base_base: "6be38adb50515719ac6d1c9380f423abd7da926f"
    base_contracts: "506a54e0905cf07efe7e862bca645145f1b5201c"
    base_docs: "ea200dda099c479dcd5ac2964b9eae997564af3b"
  items_covered: 6
  fields_investigated: 42
  diagrams_produced: 4
---

# Base GitHub Actions 完整调研

## Executive Summary

本文档对 Base 生态三个核心仓库（base/base、base/contracts、base/docs）的 GitHub Actions 工作流及仓库级配置进行了完整调研。调研覆盖 26 个工作流文件（base/base 23 个、base/contracts 1 个、base/docs 2 个），以及复合 Action、信任数据库、基准测试配置等仓库级资源。

**核心发现**：

1. **AI 代码审查**：Base 通过 `claude-review.yml` 实现了生产级 Claude Code Review，采用 LLM Gateway 代理架构和唯一的 egress block 模式网络隔离，是所有被调研项目中最成熟的 AI 审查实现。
2. **三阶段发布流水线**：6 个工作流组成完整的 start → RC auto-build → final publish → verify 链，包含 GPG 签名、构建溯源证明（SLSA attestation）和部分失败恢复机制。
3. **分级 CI 策略**：通过可复用的 `workflow_call` 核心 + 两个调用方（PR 轻量 / merge queue 完整）实现成本优化。
4. **安全加固**：25/26 工作流采用 `step-security/harden-runner`（`verify-release.yml` 是唯一未配置的工作流）+ 全 SHA 钉扎 Action 引用，达到 SLSA Level 2+ 水准。base/base 所有工作流声明显式顶层 `permissions`，但卫星仓库（contracts/`test.yml`、docs/`chromatic.yml`）缺少顶层权限声明。
5. **PR 治理**：Vouch 信任系统 + merge queue + release branch 保护，形成多层治理体系。

**10 维度能力评级**：成熟 6 项、基础 2 项、缺失 2 项。Base 在 Release Pipeline、CI/Testing、Security & Supply Chain、AI Code Review、PR Governance 五个维度达到"成熟"水准。

---

## Section 1: Repo 级配置概况

### 1.1 base/base 仓库配置

**仓库类型**: Rust（Base Reth Node — 基于 Reth 的以太坊 L2 节点）
**GitHub URL**: `github.com/base/base`
**调研 commit**: `6be38adb50515719ac6d1c9380f423abd7da926f`

#### 1.1.1 复合 Action：`.github/actions/setup/action.yml`

Base 核心仓库定义了一个统一的 CI 设置复合 Action，被几乎所有 CI 工作流引用（`uses: ./.github/actions/setup`）。

| 输入参数 | 默认值 | 说明 |
|---|---|---|
| `toolchain` | `stable` | Rust 工具链通道（stable / nightly） |
| `components` | `""` | Rust 组件（clippy, rustfmt 等） |
| `tools` | `""` | Cargo 工具（通过 `taiki-e/install-action` 安装） |
| `foundry` | `false` | 安装 Foundry（Solidity 工具链） |
| `sp1` | `false` | 安装 SP1 工具链（`cargo-prove`，ZK 证明构建） |
| `sp1-version` | `v6.2.3` | SP1 版本，与 `etc/just/succinct.just` 保持一致 |
| `elf-cache` | `false` | 恢复/保存 ELF 缓存，基于 `manifest.toml` 哈希键 |
| `mold` | `false` | 安装 mold 链接器 |
| `native-deps` | `false` | 安装原生构建依赖（clang, llvm, protobuf 等） |
| `free-disk` | `false` | 构建前释放磁盘空间 |
| `rust-cache-shared-key` | `""` | Rust 缓存共享键 |
| `rust-cache-save` | `false` | 是否保存 Rust 缓存 |

**关键设计模式**：
- 使用 `Swatinem/rust-cache` 进行 Rust 编译缓存，通过 `shared-key` 在工作流间共享
- `mozilla-actions/sccache-action` 作为编译缓存层
- SP1 工具链安装通过 `sp1up` 脚本，支持版本锁定
- ELF 缓存基于 `hashFiles('crates/proof/succinct/elf/manifest.toml')` 键
- `free-disk` 执行两阶段清理：快速预清理（Android/dotnet/CodeQL）+ `jlumbroso/free-disk-space`
- `LIBCLANG_PATH` 自动检测 LLVM 版本

**源文件**: `.github/actions/setup/action.yml`

#### 1.1.2 Vouch 信任数据库：`.github/VOUCHED.td`

```
# Syntax: one handle per line, optional platform:username, minus prefix for denounce
crazywriter1
timrolsh
```

- 平面文件格式，每行一个用户名
- 支持 `platform:username` 语法和 `-username` 谴责（denounce）机制
- 当前已授权用户：`crazywriter1`、`timrolsh`
- 仓库协作者（有写权限）自动绕过 vouch 检查

**源文件**: `.github/VOUCHED.td`

#### 1.1.3 基准测试配置：`.github/benchmark/`

两个配置文件定义不同的基准测试场景：

| 文件 | 场景 | 负载分布 |
|---|---|---|
| `load-test.yml` | 综合负载测试 | transfer(70%) + calldata/256B(20%) + precompile/sha256(10%) |
| `transfer-only.yml` | 转账吞吐量测试 | transfer(100%) |

两者均配置 `gas_limit: 1000000000`，`num_blocks: 10`，使用 `base-builder` 作为排序器、`base-reth-node` 作为验证节点。

**源文件**: `.github/benchmark/load-test.yml`, `.github/benchmark/transfer-only.yml`

#### 1.1.4 自托管 Runner Groups

| Runner Group | 用途 | 使用工作流 |
|---|---|---|
| `BaseRunnerGroup` | LLM Gateway 访问 | `claude-review.yml` |
| `BasePerfRunnerGroup` | 高性能构建 | `ci-core.yml`（build, clippy, test, system-tests）, `action-tests.yml`, `base-std-fork-tests.yml` |

`BaseRunnerGroup` 专用于 AI 代码审查，因为需要访问 LLM Gateway 端点。`BasePerfRunnerGroup` 用于需要更多计算资源的构建和测试任务。

#### 1.1.5 并发策略

| 模式 | 命名约定 | cancel-in-progress | 使用场景 |
|---|---|---|---|
| PR 级 | `${{ github.workflow }}-${{ github.head_ref \|\| github.run_id }}` | `true` | ci-pr, action-tests, no-std, lychee 等 |
| PR 编号 | `claude-review-${{ github.event.pull_request.number }}` | `true` | claude-review |
| PR/Issue 编号 | `vouch-${{ github.event.pull_request.number \|\| github.event.issue.number }}` | `false` | vouch（不可取消） |
| Release 锁 | `release-${{ github.ref_name }}` | `false` | create-rc（release 不可取消） |
| Release 版本锁 | `publish-release-${{ inputs.version }}` | `false` | publish-release |
| 分支级 | `${{ github.workflow }}-${{ github.ref }}` | `true` | ci-main-cache, base-anvil-package |
| 全局唯一 | `${{ github.workflow }}` | `false` | sp1-elf-manifest, udeps-report |
| Ref 级 | `lychee-${{ github.ref }}` | `true` | lychee（防止 rate limit） |

#### 1.1.6 权限模型

所有工作流均声明显式 `permissions` 块，遵循最小权限原则：

| 工作流 | 关键权限 |
|---|---|
| `claude-review.yml` | `contents: read, pull-requests: write` |
| `ci-core.yml` | `checks: write, contents: read` |
| `ci-pr.yml` | `checks: write, contents: read, issues: write, packages: read, pull-requests: write` |
| `build-release.yml` | `actions: read, contents: write, packages: write, id-token: write, attestations: write` |
| `vouch.yml` | 顶层 `contents: read`，manage 作业扩展至 `contents: write, pull-requests: write, issues: write` |

`id-token: write` 和 `attestations: write` 仅在 release 构建中使用，用于 OIDC 令牌和构建溯源证明。

#### 1.1.7 缺失文件

| 文件 | 状态 | 影响 |
|---|---|---|
| `dependabot.yml` | 缺失 | 无自动依赖更新；Cargo 依赖通过 `cargo-deny` 和 `cargo-udeps` 管理 |
| `CODEOWNERS` | 缺失 | 无自动审查者分配；依赖 vouch 系统和团队协作 |
| `PULL_REQUEST_TEMPLATE.md` | 缺失 | 无 PR 模板；依赖 Claude Code Review 的结构化审查 |

### 1.2 base/contracts 仓库配置

**仓库类型**: Solidity（Base 合约）
**GitHub URL**: `github.com/base/contracts`
**调研 commit**: `506a54e0905cf07efe7e862bca645145f1b5201c`

极简配置——`.github/` 目录仅包含 `workflows/` 子目录：
- 无复合 Action
- 无 `CODEOWNERS`
- 无 `dependabot.yml`
- 无 PR 模板
- 无 vouch 系统
- 环境变量 `FOUNDRY_PROFILE: ci` 定义在工作流级别

### 1.3 base/docs 仓库配置

**仓库类型**: 文档站点
**GitHub URL**: `github.com/base/docs`
**调研 commit**: `ea200dda099c479dcd5ac2964b9eae997564af3b`

- **`.github/PULL_REQUEST_TEMPLATE.md`**: 三个简洁问题——"What changed? Why?"、"Notes to reviewers"、"How has it been tested?"
- **`.github/.githooks/`**: 本地 Git hooks 目录（内容未公开）
- 无复合 Action、无 CODEOWNERS、无 dependabot

### 1.4 Repo Settings 访问结果

按照 Outline Section 1.4 的访问计划，执行了以下 API 调用（2026-06-10）：

#### 1.4.1 Branch Protection Rules / Repo Rulesets

| 端点 | base/base | base/contracts | base/docs |
|---|---|---|---|
| `GET /repos/{owner}/{repo}/branches/main/protection` | HTTP 401 | HTTP 401 | HTTP 401 |
| `GET /repos/{owner}/{repo}/rulesets` | HTTP 200，返回 `[]` | HTTP 200，返回 `[]` | HTTP 200，返回 `[]` |

**结果**: Branch protection API — 不可访问 (权限受限)，HTTP 401（需要认证）。Rulesets API 可访问但返回空数组（`[]`），表明三个仓库均未配置公开可见的 repo rulesets。

**间接证据**（从工作流代码推断）：
- `vouch.yml` 注释明确提到 "Branch protection requires changes go through a PR + merge queue. Direct pushes to main are rejected (GH006)"，确认 main 分支有 branch protection
- `ci-merge-queue.yml` 存在，表明启用了 merge queue（需要 branch protection 配合）
- `release-branch-ci.yml` 对 `releases/v*` 分支设置了 PR 保护

#### 1.4.2 GitHub Environments

| 仓库 | 结果 |
|---|---|
| base/base | HTTP 200 — 1 个环境：`copilot`（创建于 2026-06-09，无保护规则，无部署分支策略） |
| base/contracts | HTTP 200 — 0 个环境 |
| base/docs | HTTP 200 — 2 个环境：`staging`（创建于 2025-06-12）、`staging - docs`（创建于 2025-06-17），均无保护规则 |

**工作流引用**：所有工作流文件中均未发现 `environment:` 关键字引用。环境存在但未被当前工作流使用。`copilot` 环境（base/base）创建时间为调研前一天（2026-06-09），可能为新增实验性配置。

#### 1.4.3 Installed GitHub Apps

| 端点 | 结果 |
|---|---|
| `GET /repos/base/base/installation` | 不可访问 (权限受限)——该端点需要以 GitHub App 身份认证，非通用 API |

**间接证据**：
- 工作流中仅引用 `github-actions[bot]`（标准 Actions 机器人），未发现其他 bot 模式
- 无 Dependabot、Renovate 或其他自动化 App 的工作流触发器
- `claude-review.yml` 通过标准 `GITHUB_TOKEN` 而非 GitHub App token 运行

#### 1.4.4 Secrets Names

| 端点 | base/base | base/contracts | base/docs |
|---|---|---|---|
| `GET /repos/{owner}/{repo}/actions/secrets` | HTTP 401 | HTTP 401 | HTTP 401 |

**结果**: 不可访问 (权限受限)——所有仓库均返回 HTTP 401，需要协作者权限。

**从工作流代码提取的 Secrets 清单**：

| Secret 名称 | 使用仓库 | 使用工作流 | 用途 |
|---|---|---|---|
| `secrets.LLM_GATEWAY_API_KEY` | base/base | `claude-review.yml` | LLM Gateway 认证 |
| `secrets.GPG_SIGNING_KEY` | base/base | `build-release.yml` | Release 二进制签名 |
| `secrets.GPG_PASSPHRASE` | base/base | `build-release.yml` | GPG 密钥密码 |
| `secrets.BASE_STD_TOKEN` | base/base | `base-anvil-package.yml`, `base-std-fork-tests.yml` | 跨仓库 PAT（访问 base/base-std） |
| `secrets.CHROMATIC_PROJECT_TOKEN` | base/docs | `chromatic.yml` | Chromatic 可视化回归测试 |
| `secrets.GITHUB_TOKEN` | 所有 | 多个 | 自动提供的标准令牌 |

**Repository Variables**：

| Variable 名称 | 使用仓库 | 使用工作流 | 用途 |
|---|---|---|---|
| `vars.LLM_GATEWAY_HOSTNAME` | base/base | `claude-review.yml` | LLM Gateway 主机名 |

### 1.5 跨仓库配置对比

| 配置项 | base/base | base/contracts | base/docs |
|---|---|---|---|
| 复合 Action | `.github/actions/setup/` | 无 | 无 |
| CODEOWNERS | 无 | 无 | 无 |
| dependabot.yml | 无 | 无 | 无 |
| PR 模板 | 无 | 无 | 有（3 问题模板） |
| Vouch 系统 | 有（VOUCHED.td） | 无 | 无 |
| 本地 Git Hooks | 无 | 无 | 有（.githooks/） |
| 基准测试配置 | 有（2 个配置） | 无 | 无 |
| 自托管 Runner | 有（2 个 group） | 无 | 无 |
| GitHub Environments | 1（copilot） | 0 | 2（staging × 2） |
| harden-runner 版本 | v2.19.4 | v2.12.1 | v2.12.1 |

**治理成熟度差距**：base/base 作为核心仓库，配置远超卫星仓库。contracts 和 docs 仅有最基础的 CI，无 PR 治理、无自动化依赖管理、无 AI 审查。

---

## Section 2: Workflow 完整列表及逐个分析

### 2.1 base/base Workflows（23 个工作流文件）

#### 2.1.1 `claude-review.yml` — Claude Code Review

```yaml
workflow_name: "Claude Code Review"
file: "claude-review.yml"
triggers: [pull_request: opened, synchronize, ready_for_review, reopened]
purpose: "AI 驱动的 PR 代码审查，专注于 Rust 正确性、安全性和惯用法"
category: "AI"
ai_features: true
ai_tool: "Claude Code Action (anthropics/claude-code-action@v1.0.29)"
harden_runner_mode: "block"
```

**详细分析**：

**LLM Gateway 代理架构**：
- 不直接调用 Anthropic API，而是通过 `ANTHROPIC_BASE_URL: https://${{ vars.LLM_GATEWAY_HOSTNAME }}` 代理
- 使用 `secrets.LLM_GATEWAY_API_KEY` 而非直接的 Anthropic API key
- 架构含义：集中化 API 访问控制、使用监控、成本核算

**网络隔离（唯一的 block 模式）**：
```yaml
egress-policy: block
allowed-endpoints: >
  api.github.com:443
  bun.sh:443
  github.com:443
  objects.githubusercontent.com:443
  registry.npmjs.org:443
  release-assets.githubusercontent.com:443
  ${{ vars.LLM_GATEWAY_HOSTNAME }}:443
```
这是所有工作流中唯一使用 `egress-policy: block` 的工作流。AI 审查涉及执行外部代码（Claude Code Action），block 模式确保只能访问预定义的端点列表。

**Prompt 工程**：
- 角色定义："Review like a senior Rust engineer on the team"
- 代码库上下文：4 个 crate 组、错误处理模式、异步模式
- 7 类审查要点：错误处理、内存/性能、并发、安全、API 设计、架构、Rust 惯用法
- 负面指导："DO NOT comment on formatting or style"、"DO NOT post praise, 'looks good', or filler comments"

**去重机制**：
```
Before posting any inline comment, first fetch all existing inline review comments on this PR by running:
gh api repos/{repo}/pulls/{pr}/comments --jq '.[] | select(.user.login == "github-actions[bot]") | {path, body}'
Do NOT post a comment if there is already a comment from github-actions[bot] on the same file raising the same or substantially similar issue.
```

**评论管理**：
- 通过 `<!-- CLAUDE_REVIEW_SUMMARY -->` HTML 标记识别旧摘要
- 发布新摘要前删除所有旧摘要（`gh pr comment --delete-last` 循环）

**工具限制**：
通过 `claude_args --allowedTools` 严格限制 Claude 可用工具：
- `mcp__github_inline_comment__create_inline_comment` — 行内评论
- `Bash(gh pr comment ...)` — PR 评论（发布/编辑/删除）
- `Bash(gh pr diff/view ...)` — PR 信息读取
- `Bash(gh api repos/.../pulls/.../comments ...)` — 评论 API 查询

**Fork 排除**：
```yaml
if: github.event.pull_request.head.repo.full_name == github.repository
```
外部贡献者的 PR（来自 fork）不触发 AI 审查——secrets 和 runner group 不可用。

**模型配置**: `claude-opus-4-6-default`，`track_progress: false`

**源文件**: `.github/workflows/claude-review.yml`

---

#### 2.1.2 `ci-core.yml` — CI 核心（可复用工作流）

```yaml
workflow_name: "CI Core"
file: "ci-core.yml"
triggers: [workflow_call]
purpose: "参数化的可复用 CI 核心，被 ci-pr 和 ci-merge-queue 调用"
category: "CI"
ai_features: false
harden_runner_mode: "audit"
```

**参数化输入**：

| 输入 | 类型 | 说明 |
|---|---|---|
| `base_ref` | string | 基准分支（用于 affected-only 构建） |
| `build_command` | string (required) | 构建命令 |
| `test_command` | string (required) | 测试命令 |
| `clippy_command` | string (required) | Clippy 命令 |
| `run_sigsegv` | boolean | 运行 SIGSEGV 测试 |
| `run_system_tests` | boolean | 运行系统测试 |
| `allow_registry_login` | boolean (required) | 允许 GHCR 登录 |
| `save_rust_cache` | boolean | 保存 Rust 缓存 |

**作业矩阵（10 个作业）**：

| 作业 | Runner | 条件 | 说明 |
|---|---|---|---|
| `changes` | ubuntu-latest | 始终 | Docker 文件变更检测（`dorny/paths-filter`） |
| `metadata-checks` | ubuntu-latest | 始终 | `cargo-deny`、Cargo.lock 验证、crate 依赖检查 |
| `format` | ubuntu-latest | 始终 | nightly rustfmt |
| `build` | BasePerfRunnerGroup | 始终 | 构建（支持 affected-only） |
| `clippy` | BasePerfRunnerGroup | 始终 | Clippy 静态分析 |
| `test` | BasePerfRunnerGroup | 始终 | nextest + JUnit 报告 |
| `bench` | ubuntu-latest | 始终 | `cargo bench --test`（仅编译验证） |
| `docker` | ubuntu-latest | Docker 文件变更 | Docker 镜像构建验证 |
| `test-musl-sigsegv` | ubuntu-latest | `run_sigsegv` | musl 环境下的 SIGSEGV 处理测试 |
| `system-tests` | BasePerfRunnerGroup | `run_system_tests` | 端到端系统测试（60 分钟超时） |

**源文件**: `.github/workflows/ci-core.yml`

---

#### 2.1.3 `ci-pr.yml` — PR 级 CI（轻量）

```yaml
workflow_name: "CI PR"
file: "ci-pr.yml"
triggers: [pull_request]
purpose: "PR 触发的轻量 CI，仅运行受影响的构建/测试"
category: "CI"
ai_features: false
harden_runner_mode: "audit"（继承自 ci-core）
```

调用 `ci-core.yml`，参数配置为轻量模式：
- `build_command`: `just build::affected-ci "origin/${{ github.base_ref || 'main' }}"` — 仅构建受影响的 crate
- `test_command`: `just test-affected-ci "origin/${{ github.base_ref || 'main' }}"` — 仅测试受影响的 crate
- `clippy_command`: `just check::clippy-affected-ci "origin/${{ github.base_ref || 'main' }}"` — 仅 lint 受影响的 crate
- `run_system_tests: false`, `run_sigsegv: false`, `save_rust_cache: false`
- `cancel-in-progress: true`

**源文件**: `.github/workflows/ci-pr.yml`

---

#### 2.1.4 `ci-merge-queue.yml` — Merge Queue CI（完整）

```yaml
workflow_name: "CI Merge Queue"
file: "ci-merge-queue.yml"
triggers: [merge_group]
purpose: "Merge queue 触发的完整 CI，包含系统测试和 SIGSEGV 测试"
category: "CI"
ai_features: false
harden_runner_mode: "audit"（继承自 ci-core）
```

调用 `ci-core.yml`，参数配置为完整模式：
- `build_command`: `just build::ci` — 完整工作区构建
- `test_command`: `just test-ci` — 完整测试
- `clippy_command`: `just check::clippy-ci` — 完整 Clippy
- `run_system_tests: true`, `run_sigsegv: true`

**源文件**: `.github/workflows/ci-merge-queue.yml`

---

#### 2.1.5 `ci-main-cache.yml` — Main 分支缓存预热

```yaml
workflow_name: "CI Main Cache"
file: "ci-main-cache.yml"
triggers: [push: branches: [main], workflow_dispatch]
purpose: "在 main 分支推送后预热 Rust 编译缓存"
category: "CI"
ai_features: false
harden_runner_mode: "audit"
```

- 检测 SP1 ELF 输入变更（`check-succinct-elf-inputs.py`）
- 无变更时执行标准 `just build::ci`
- 有 ELF 输入变更时使用 stubbed ELF 构建：`BASE_SUCCINCT_ELF_STUB=1 cargo build`
- `save_rust_cache: true` — 唯一显式保存缓存的工作流

**源文件**: `.github/workflows/ci-main-cache.yml`

---

#### 2.1.6 `start-release.yml` — 启动发布

```yaml
workflow_name: "Start Release"
file: "start-release.yml"
triggers: [workflow_dispatch: inputs: bump_type(minor/patch/major)]
purpose: "创建 release 分支，执行版本同步，创建跟踪 issue"
category: "Release"
ai_features: false
harden_runner_mode: "audit"
```

**流程**：
1. `./etc/scripts/release/start-release.sh "${{ inputs.bump_type }}"` — 创建 `releases/vX.Y.Z` 分支
2. `./etc/scripts/release/version-sync.sh "$BRANCH"` — 同步 Cargo.toml 版本号，创建 PR
3. `./etc/scripts/release/create-issue.sh "$BRANCH"` — 创建 release 跟踪 issue
4. 输出 Step Summary：版本变更、分支名、下一步指引

**源文件**: `.github/workflows/start-release.yml`

---

#### 2.1.7 `create-rc.yml` — 自动创建 RC

```yaml
workflow_name: "Create RC"
file: "create-rc.yml"
triggers: [push: branches: ['releases/v*']]
purpose: "release 分支推送时自动创建 RC tag 并构建"
category: "Release"
ai_features: false
harden_runner_mode: "audit"
```

**流程**：
1. 检查 Cargo.toml 版本（如果仍为 `0.0.0` 则跳过，等待版本同步 PR 合入）
2. `./etc/scripts/release/create-tag.sh "${{ github.ref_name }}" rc` — 创建 RC tag（如 `v0.6.0-rc.1`）
3. 调用 `build-release.yml` 并传入 `is_final: false`

**关键设计**：版本检查防止在版本同步 PR 合入前误触发构建。

**源文件**: `.github/workflows/create-rc.yml`

---

#### 2.1.8 `build-release.yml` — 构建发布（可复用）

```yaml
workflow_name: "Build Release"
file: "build-release.yml"
triggers: [workflow_call: inputs: tag, is_final]
purpose: "多平台二进制构建 + Docker 镜像构建 + 发布"
category: "Release"
ai_features: false
harden_runner_mode: "audit"
```

**4 个作业**：

**build-binaries（矩阵策略）**：
- 平台：x86_64-linux (ubuntu-24.04)、aarch64-linux (ubuntu-24.04-arm)、aarch64-apple-darwin (macos-14)
- 二进制：base、base-reth-node、base-consensus、basectl（共 12 个构建组合）
- 构建配置：`cargo build --locked --profile maxperf`
- 打包：tar.gz + sha256 校验和
- **GPG 签名**：从 `secrets.GPG_SIGNING_KEY`（base64 编码）导入，使用 `--armor --detach-sign`
- **构建溯源证明**：`actions/attest@v4.1.0` 生成 SLSA provenance
- harden-runner 仅在 Linux 上启用（macOS 不支持）

**build-and-push（Docker 矩阵）**：
- 平台：linux/amd64 (ubuntu-24.04)、linux/arm64 (ubuntu-24.04-arm)
- 使用 `docker buildx bake -f etc/docker/docker-bake.hcl`
- digest-based push（`push-by-digest=true`），后续合并 manifest

**find-release-artifacts（部分失败恢复）**：
- `if: ${{ !cancelled() }}` — 即使上游失败也执行
- 检查哪些构建产物存在（`has_digests`、`has_binaries`）
- 允许部分成功发布

**publish（合并 + 发布）**：
- Docker manifest 创建，支持 semver 标签层级（`v1.2.3`, `v1.2`, `v1`, `latest`）
- RC 版本仅使用 tag 标签，不设 `latest`
- GitHub Release 创建（仅 `is_final: true` 时，draft 模式）
- 二进制上传到 GitHub Release（`gh release upload --clobber`）

**源文件**: `.github/workflows/build-release.yml`

---

#### 2.1.9 `publish-release.yml` — 发布正式版本

```yaml
workflow_name: "Publish Release"
file: "publish-release.yml"
triggers: [workflow_dispatch: inputs: version(string)]
purpose: "验证 release 分支，创建正式 tag，触发最终构建"
category: "Release"
ai_features: false
harden_runner_mode: "audit"
```

**验证链**：
1. semver 格式验证（`^[0-9]+\.[0-9]+\.[0-9]+$`）
2. release 分支存在验证（`releases/v${VERSION}`）
3. Cargo.toml 版本匹配验证
4. 幂等 tag 处理：已存在的 tag 在指向同一 commit 时复用，否则报错拒绝
5. 调用 `build-release.yml` 并传入 `is_final: true`

**源文件**: `.github/workflows/publish-release.yml`

---

#### 2.1.10 `release-branch-ci.yml` — Release 分支保护

```yaml
workflow_name: "Release Branch CI"
file: "release-branch-ci.yml"
triggers: [pull_request: branches: ['releases/v*']]
purpose: "防止对已完成 release 的分支进行修改"
category: "Release"
ai_features: false
harden_runner_mode: "audit"
```

运行 `./etc/scripts/release/check-finalized.sh` 检查 release 是否已定型。

**源文件**: `.github/workflows/release-branch-ci.yml`

---

#### 2.1.11 `verify-release.yml` — 验证发布签名

```yaml
workflow_name: "Verify Release"
file: "verify-release.yml"
triggers: [pull_request, release: published, workflow_dispatch: inputs: tag]
purpose: "验证 release 二进制的 GPG 签名"
category: "Release"
ai_features: false
harden_runner_mode: "无"
```

通过 `baseup/baseup verify-release` 脚本验证签名完整性。三种触发方式确保签名验证可在 PR、发布后、手动三个阶段执行。

**源文件**: `.github/workflows/verify-release.yml`

---

#### 2.1.12 `vouch.yml` — PR 信任门控

```yaml
workflow_name: "Vouch"
file: "vouch.yml"
triggers: [pull_request_target: opened/reopened, issue_comment: created]
purpose: "外部贡献者 PR 信任门控"
category: "Governance"
ai_features: false
harden_runner_mode: "audit"
```

**两个作业**：

| 作业 | 触发 | 功能 |
|---|---|---|
| `check-pr` | `pull_request_target` | 检查 PR 作者是否在 VOUCHED.td 中，未授权则自动关闭 PR (`auto-close: true`) |
| `manage` | `issue_comment`（包含 vouch/denounce/unvouch） | 处理授权/取消授权命令，通过 PR 修改 VOUCHED.td |

- 使用 `pull_request_target` 确保 fork PR 安全（在 base 上下文执行，可访问 secrets）
- vouch 修改通过 PR + merge queue，不直接推送（`pull-request: true`）
- `cancel-in-progress: false` — vouch 操作不可取消

**源文件**: `.github/workflows/vouch.yml`

---

#### 2.1.13 `action-tests.yml` — Action/集成测试

```yaml
workflow_name: "Action Tests"
file: "action-tests.yml"
triggers: [pull_request, merge_group]
purpose: "合约构建 + Action 级别的 lint 和测试"
category: "CI"
ai_features: false
harden_runner_mode: "audit"
```

在 `BasePerfRunnerGroup` 上运行，执行 `just build::contracts` → `just actions::lint-ci` → `just actions::test-ci`。

**源文件**: `.github/workflows/action-tests.yml`

---

#### 2.1.14 `no-std.yml` — no_std 兼容性检查

```yaml
workflow_name: "no_std"
file: "no-std.yml"
triggers: [pull_request, merge_group]
purpose: "验证 RISC-V/no_std 嵌入式兼容性"
category: "CI"
ai_features: false
harden_runner_mode: "audit"
```

两个作业：
- `check-no-std`：stable 工具链 + `riscv32imac-unknown-none-elf` 目标
- `check-no-std-proof`：nightly 工具链 + `rust-src` 组件，用于证明系统的 no_std 兼容性

**源文件**: `.github/workflows/no-std.yml`

---

#### 2.1.15 `base-std-fork-tests.yml` — 跨仓库接口测试

```yaml
workflow_name: "Base Std Interface Tests"
file: "base-std-fork-tests.yml"
triggers: [pull_request, merge_group, workflow_dispatch]
purpose: "验证 base/base 变更与 base-std 规范的兼容性"
category: "CI"
ai_features: false
harden_runner_mode: "audit"
```

**复杂的跨仓库测试流程**：
1. 克隆 `base/base-anvil`（公开）和 `base/base-std`（内部，需要 `BASE_STD_TOKEN` PAT）
2. 使用 Cargo patch 替换 precompiles 和 chains crate：
   ```
   cargo --config "patch.\"https://github.com/base/base.git\".base-common-precompiles.path=\"$GITHUB_WORKSPACE/crates/common/precompiles\""
   ```
3. 构建 patched anvil + forge 二进制
4. 运行 base-std fork 测试（`./script/run-fork-tests.sh`）
5. 在 PR 上发布测试结果评论：
   - 使用 `<!-- fork-test-results -->` HTML 标记实现幂等更新
   - 分类输出：通过/失败/未运行三种状态
   - 既有评论则更新，无则创建

**源文件**: `.github/workflows/base-std-fork-tests.yml`

---

#### 2.1.16 `zepter.yml` — Feature 依赖检查

```yaml
workflow_name: "Zepter"
file: "zepter.yml"
triggers: [pull_request: branches: [main], merge_group]
purpose: "检查 Substrate/Polkadot 风格的 Cargo feature 依赖正确性"
category: "CI"
ai_features: false
harden_runner_mode: "audit"
```

使用 `taiki-e/install-action` 安装 `just` 和 `zepter`，运行 `just zepter`。

**源文件**: `.github/workflows/zepter.yml`

---

#### 2.1.17 `lychee.yml` — 链接检查

```yaml
workflow_name: "Lychee Checks"
file: "lychee.yml"
triggers: [pull_request, merge_group, workflow_dispatch]
purpose: "检测文档中的死链接"
category: "CI"
ai_features: false
harden_runner_mode: "audit"
```

使用 `lycheeverse/lychee-action@v2.8.0` + `lychee.toml` 配置文件。并发组 `lychee-${{ github.ref }}` 防止 GitHub rate limit。

**源文件**: `.github/workflows/lychee.yml`

---

#### 2.1.18 `docker.yml` — Dev Docker 镜像

```yaml
workflow_name: "Docker"
file: "docker.yml"
triggers: [push: branches: [main], workflow_dispatch]
purpose: "构建并推送开发 Docker 镜像 + 预热 devnet 缓存"
category: "CD"
ai_features: false
harden_runner_mode: "audit"
```

**三个作业**：

| 作业 | 说明 |
|---|---|
| `build-and-push` | 多架构（amd64/arm64）客户端镜像，digest-based push |
| `warm-devnet-cache` | 预热 builder/consensus/batcher Docker 构建缓存（`dev` profile，cacheonly 输出） |
| `merge` | 合并 digest 创建 manifest list，设置分支名 + SHA 标签 |

镜像：`ghcr.io/{owner}/node-reth-dev`，OCI 标签包含 source、revision、created。

**源文件**: `.github/workflows/docker.yml`

---

#### 2.1.19 `base-anvil-package.yml` — Base Anvil 打包

```yaml
workflow_name: "Base Anvil Package"
file: "base-anvil-package.yml"
triggers: [push: branches: [main], workflow_dispatch: inputs: base_anvil_ref, base_std_ref]
purpose: "构建 patched Foundry (anvil+forge) Docker 镜像"
category: "CD"
ai_features: false
harden_runner_mode: "audit"
```

**最复杂的工作流之一**（410 行）：
- 两个作业 + manifest 合并
- Cargo patch 构建 base-anvil（替换 precompiles + chains）
- 可选 smoke test（仅 amd64）：运行 base-std fork 测试
- Docker 镜像包含 `MANIFEST.json`（记录所有源仓库的 SHA、ref、是否通过 smoke test）
- 标签策略：main + 默认 ref → `main-{date}-{sha}`；自定义 ref → `manual-{date}-{sha}`

**源文件**: `.github/workflows/base-anvil-package.yml`

---

#### 2.1.20 `stale.yml` — Issue/PR 生命周期

```yaml
workflow_name: "Mark stale issues and PRs"
file: "stale.yml"
triggers: [schedule: '30 0 * * *', workflow_dispatch]
purpose: "标记和关闭不活跃的 issue/PR"
category: "Infra"
ai_features: false
harden_runner_mode: "audit"
```

| 参数 | Issue | PR |
|---|---|---|
| 标记 stale | 7 天 | 21 天 |
| 关闭 | 标记后 1 天 | 标记后 1 天 |
| 豁免标签 | `active` | `active` |

**源文件**: `.github/workflows/stale.yml`

---

#### 2.1.21 `udeps-report.yml` — 未使用依赖报告

```yaml
workflow_name: "Udeps Report"
file: "udeps-report.yml"
triggers: [schedule: '0 13 * * *', workflow_dispatch]
purpose: "每日扫描未使用的 Cargo 依赖并创建/更新 GitHub Issue"
category: "Infra"
ai_features: false
harden_runner_mode: "audit"
```

**流程**：
1. `cargo +nightly udeps --locked --workspace --all-features --all-targets --output json`
2. Python 渲染器（`udeps-report.py render`）生成 Issue body
3. 查找已有 open issue（标题精确匹配），更新或创建新 issue
4. 使用 `BASE_SUCCINCT_ELF_STUB=1` 避免 SP1 ELF 构建依赖

**源文件**: `.github/workflows/udeps-report.yml`

---

#### 2.1.22 `sp1-elf-manifest.yml` — SP1 ELF Manifest 自动刷新

```yaml
workflow_name: "SP1 ELF Manifest"
file: "sp1-elf-manifest.yml"
triggers: [push: branches: [main], workflow_dispatch]
purpose: "当 SP1 ELF 输入变更时，自动重建 ELF 并打开/更新 manifest 刷新 PR"
category: "Infra"
ai_features: false
harden_runner_mode: "audit"
```

**流程**：
1. 检测 SP1 ELF 输入变更（`check-succinct-elf-inputs.py`）
2. 重建 ELF：`just succinct build-elfs` + `just succinct write-manifest`
3. 验证 manifest：`check-elf-manifest.py --print-hashes`
4. 如有变更：创建/更新 `automation/update-sp1-elf-manifest` 分支
5. `git push --force-with-lease` 幂等推送
6. 打开/更新 PR（标题："fix(proof): refresh succinct elf manifest"）

**源文件**: `.github/workflows/sp1-elf-manifest.yml`

---

#### 2.1.23 `benchmark.yml` — 基准测试

```yaml
workflow_name: "Benchmark"
file: "benchmark.yml"
triggers: [workflow_dispatch]
purpose: "运行性能基准测试（Go 驱动的外部测试框架）"
category: "Benchmark"
ai_features: false
harden_runner_mode: "audit"
```

**两阶段**：
1. `build-binaries`：构建 base-reth-node + base-builder + base-load-test（`maxperf` profile），通过 `hashFiles('Cargo.toml', 'Cargo.lock', 'crates/**', 'bin/**')` 缓存
2. `benchmark`：检出外部 `base/benchmark` 仓库（Go），运行 `go run benchmark/cmd/main.go`，生成 HTML 报告

**源文件**: `.github/workflows/benchmark.yml`

---

### 2.2 base/contracts Workflows（1 个工作流）

#### 2.2.1 `test.yml` — Solidity CI

```yaml
workflow_name: "CI"
file: "test.yml"
triggers: [pull_request]
purpose: "Foundry 项目 CI：格式化、构建、semver-lock、测试"
category: "CI"
ai_features: false
ai_tool: "none"
harden_runner_mode: "audit"
```

**步骤**：
1. `harden-runner` v2.12.1（审计模式）
2. 递归检出子模块
3. 安装 Foundry (stable) + Go + just
4. `just deps` → `just lint-check` → `just forge-build` → `just semver-lock` + `git diff --exit-code snapshots/semver-lock.json` → `just test`

**semver-lock 机制**：通过快照文件 `snapshots/semver-lock.json` 验证 ABI 兼容性，`git diff --exit-code` 确保没有未提交的 ABI 变更。

**源文件**: `.github/workflows/test.yml`

---

### 2.3 base/docs Workflows（2 个工作流）

#### 2.3.1 `chromatic.yml` — Storybook 可视化回归

```yaml
workflow_name: "Chromatic Publish"
file: "chromatic.yml"
triggers: [push: paths: ['storybook/**']]
purpose: "在 Storybook 变更时触发 Chromatic 可视化回归测试"
category: "CI/Documentation"
ai_features: false
harden_runner_mode: "audit"
```

仅在 `storybook/` 路径变更时触发，使用 `chromaui/action` + `onlyChanged: true` 优化构建。

**源文件**: `.github/workflows/chromatic.yml`

#### 2.3.2 `file-size-checker.yml` — 文件大小检查

```yaml
workflow_name: "File Size Checker"
file: "file-size-checker.yml"
triggers: [pull_request: opened, synchronize]
purpose: "防止超大文件进入仓库"
category: "CI/Documentation"
ai_features: false
harden_runner_mode: "audit"
```

| 阈值 | 行为 |
|---|---|
| > 10MB | 警告评论 |
| > 40MB | 阻止 + 错误评论 |

使用 `github-script` 自动在 PR 上发布检查结果评论。

**源文件**: `.github/workflows/file-size-checker.yml`

---

### 2.4 Workflow 完整汇总表

| # | 仓库 | 文件 | 名称 | 类别 | 触发 | harden-runner | AI |
|---|---|---|---|---|---|---|---|
| 1 | base/base | claude-review.yml | Claude Code Review | AI | PR | **block** | Claude Opus 4.6 |
| 2 | base/base | ci-core.yml | CI Core | CI | workflow_call | audit | - |
| 3 | base/base | ci-pr.yml | CI PR | CI | PR | (继承) | - |
| 4 | base/base | ci-merge-queue.yml | CI Merge Queue | CI | merge_group | (继承) | - |
| 5 | base/base | ci-main-cache.yml | CI Main Cache | CI | push:main | audit | - |
| 6 | base/base | start-release.yml | Start Release | Release | workflow_dispatch | audit | - |
| 7 | base/base | create-rc.yml | Create RC | Release | push:releases/v* | audit | - |
| 8 | base/base | build-release.yml | Build Release | Release | workflow_call | audit | - |
| 9 | base/base | publish-release.yml | Publish Release | Release | workflow_dispatch | audit | - |
| 10 | base/base | release-branch-ci.yml | Release Branch CI | Release | PR:releases/v* | audit | - |
| 11 | base/base | verify-release.yml | Verify Release | Release | release+PR+dispatch | 无 | - |
| 12 | base/base | vouch.yml | Vouch | Governance | PR_target+comment | audit | - |
| 13 | base/base | action-tests.yml | Action Tests | CI | PR+merge_group | audit | - |
| 14 | base/base | no-std.yml | no_std | CI | PR+merge_group | audit | - |
| 15 | base/base | base-std-fork-tests.yml | Base Std Interface Tests | CI | PR+merge_group+dispatch | audit | - |
| 16 | base/base | zepter.yml | Zepter | CI | PR:main+merge_group | audit | - |
| 17 | base/base | lychee.yml | Lychee Checks | CI | PR+merge_group+dispatch | audit | - |
| 18 | base/base | docker.yml | Docker | CD | push:main+dispatch | audit | - |
| 19 | base/base | base-anvil-package.yml | Base Anvil Package | CD | push:main+dispatch | audit | - |
| 20 | base/base | stale.yml | Stale | Infra | schedule+dispatch | audit | - |
| 21 | base/base | udeps-report.yml | Udeps Report | Infra | schedule+dispatch | audit | - |
| 22 | base/base | sp1-elf-manifest.yml | SP1 ELF Manifest | Infra | push:main+dispatch | audit | - |
| 23 | base/base | benchmark.yml | Benchmark | Benchmark | workflow_dispatch | audit | - |
| 24 | base/contracts | test.yml | CI | CI | PR | audit | - |
| 25 | base/docs | chromatic.yml | Chromatic Publish | CI/Docs | push:storybook/** | audit | - |
| 26 | base/docs | file-size-checker.yml | File Size Checker | CI/Docs | PR | audit | - |

---

## Section 3: Security & Supply Chain Hardening 详细分析

### 3.1 step-security/harden-runner 使用模式

| 模式 | 工作流数量 | 具体工作流 |
|---|---|---|
| **block**（出站阻止） | 1 | `claude-review.yml` |
| **audit**（出站审计） | 24 | 所有其他工作流（包括 ci-core 的所有子作业） |
| **无** | 1 | `verify-release.yml` |

**Block 模式分析**（仅 `claude-review.yml`）：
- 明确列出 7 个允许的出站端点
- 包括 GitHub API、npm registry（bun.sh/registry.npmjs.org 用于 Claude Code Action 依赖安装）、LLM Gateway
- 设计原则：AI 审查执行外部代码（Claude Code Action），需要最严格的网络隔离

**版本策略**：
- base/base：所有工作流统一使用 `step-security/harden-runner@9af89fc71515a100421586dfdb3dc9c984fbf411` (v2.19.4)
- base/contracts 和 base/docs：使用 `step-security/harden-runner@002fdce3c6a235733a90a27c80493a3241e56863` (v2.12.1)
- 差异表明卫星仓库的更新频率较低

### 3.2 Action SHA 钉扎

所有三个仓库的所有工作流均使用完整 SHA 引用 Action，无一例外。示例：
- `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd` (base/base, v6.0.2)
- `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683` (base/contracts+docs, v4.2.2)

每个 SHA 引用均附带注释标注版本号，便于审计。

### 3.3 权限最小化

**base/base**：所有 23 个工作流均声明显式顶层 `permissions` 块，不依赖默认的 `GITHUB_TOKEN` 权限。特别值得注意：
- `id-token: write` 仅在需要 OIDC 令牌的工作流中出现（`build-release.yml`、`publish-release.yml`、`create-rc.yml`）
- `attestations: write` 仅在 build-release 中出现
- vouch.yml 使用分层权限：顶层 `contents: read`，manage 作业扩展权限

**卫星仓库权限缺口**：
- `base/contracts/.github/workflows/test.yml`：**未声明顶层 `permissions`**，依赖仓库默认的 `GITHUB_TOKEN` 权限
- `base/docs/.github/workflows/chromatic.yml`：**未声明顶层 `permissions`**，依赖仓库默认权限
- `base/docs/.github/workflows/file-size-checker.yml`：已声明顶层 `permissions: pull-requests: write`

卫星仓库的权限缺口表明 base/base 的安全实践未完全传播到组织内其他仓库。

### 3.4 GPG 签名链

Release 二进制签名流程：
1. `secrets.GPG_SIGNING_KEY`（base64 编码）导入临时 GNUPGHOME
2. 使用 `secrets.GPG_PASSPHRASE` 解锁密钥
3. 对所有 `.tar.gz` 归档执行 `gpg --armor --detach-sign`
4. 临时密钥环在 trap EXIT 时清理（`rm -rf "$GNUPGHOME"`）
5. `verify-release.yml` 通过 `baseup verify-release` 验证签名

### 3.5 Build Provenance Attestation

`build-release.yml` 使用 `actions/attest@v4.1.0` 生成构建溯源证明：
```yaml
- name: Attest build provenance
  uses: actions/attest@59d89421af93a897026c735860bf21b6eb4f7b26 # v4.1.0
  with:
    subject-path: "*.tar.gz"
```
需要 `id-token: write` 和 `attestations: write` 权限，符合 SLSA Level 2+ 要求。

### 3.6 Docker 供应链

- 所有 Docker 镜像推送到 GHCR（`ghcr.io`）
- 使用 digest-based push + manifest merge（不依赖 tag 引用）
- OCI 标签：`org.opencontainers.image.source`、`.revision`、`.created`、`.version`
- base-anvil 镜像包含 `MANIFEST.json`，记录所有源仓库的确切 SHA

### 3.7 Fork 安全

| 机制 | 工作流 | 方法 |
|---|---|---|
| Fork 排除 | `claude-review.yml` | `if: head.repo.full_name == github.repository` |
| 安全触发 | `vouch.yml` | `pull_request_target`（在 base 上下文执行） |
| Registry 登录限制 | `ci-pr.yml` | `allow_registry_login: ${{ !fork }}` |

---

## Section 4: 10 维度能力矩阵

### 评级标准

| 评级 | 定义 |
|---|---|
| **成熟** | 有专门的工作流/配置，设计完善，涵盖边缘场景 |
| **基础** | 有基本实现但功能有限或未完全自动化 |
| **缺失** | 未找到相关工作流或配置 |

### 能力矩阵

| # | 维度 | 评级 | 关键证据 | 支持工作流 | 差距 |
|---|---|---|---|---|---|
| 1 | Upstream Auto-Sync | **缺失** | 未发现上游同步工作流；无 Reth 上游代码自动合并机制 | 无 | Base 已独立于 OP Stack，可能不需要传统上游同步 |
| 2 | AI Code Review | **成熟** | Claude Opus 4.6 + LLM Gateway 代理 + block 模式网络隔离 + 去重 + 负面指导 prompt | `claude-review.yml` | 仅覆盖 base/base，contracts 和 docs 无 AI 审查 |
| 3 | PR Audit | **基础** | AI 审查提供代码质量审计，但无 CODEOWNERS、无必须审查者配置（不可验证）| `claude-review.yml`, `vouch.yml` | 缺少 CODEOWNERS 和可验证的审查者策略 |
| 4 | Interactive Agent | **缺失** | 无交互式 bot/agent 工作流（如 `/fix` 命令、PR 内 issue 创建） | 无 | Claude Code Review 为只读审查模式 |
| 5 | Release Pipeline | **成熟** | 6 个工作流组成完整链：start → RC → build → publish → verify，含 GPG 签名、SLSA attestation、部分失败恢复 | `start-release.yml`, `create-rc.yml`, `build-release.yml`, `publish-release.yml`, `release-branch-ci.yml`, `verify-release.yml` | 无自动回滚机制 |
| 6 | CI/Testing | **成熟** | 分级策略（PR 轻量/merge queue 完整）+ 系统测试 + 跨仓库测试 + no_std 兼容 + 基准 | `ci-core.yml`, `ci-pr.yml`, `ci-merge-queue.yml`, `action-tests.yml`, `no-std.yml`, `base-std-fork-tests.yml`, `zepter.yml`, `lychee.yml` | contracts/docs CI 较简单 |
| 7 | Security & Supply Chain | **成熟** | 25/26 工作流 harden-runner（`verify-release.yml` 除外）+ 全 SHA 钉扎 + GPG 签名 + build attestation + base/base 全量显式权限 | 所有工作流（1 个 harden-runner 缺口） | `verify-release.yml` 无 harden-runner；contracts/docs harden-runner 版本滞后；contracts/`test.yml` 和 docs/`chromatic.yml` 缺少顶层 permissions |
| 8 | Benchmark | **基础** | 专用基准测试工作流但仅手动触发，无自动回归检测 | `benchmark.yml` | 无 PR 级性能回归检测 |
| 9 | PR Governance | **成熟** | Vouch 信任系统 + merge queue + release 分支保护 + 并发控制 | `vouch.yml`, `ci-merge-queue.yml`, `release-branch-ci.yml` | 仅 base/base 有治理，contracts/docs 无 |
| 10 | Documentation & Infrastructure | **基础** | Stale bot + udeps 报告 + SP1 ELF 自动刷新，但无 dependabot、无 Renovate | `stale.yml`, `udeps-report.yml`, `sp1-elf-manifest.yml`, `chromatic.yml`, `file-size-checker.yml` | 无自动依赖更新 |

### 跨仓库维度评分

| 维度 | base/base | base/contracts | base/docs |
|---|---|---|---|
| AI Code Review | 成熟 | 缺失 | 缺失 |
| CI/Testing | 成熟 | 基础 | 基础 |
| Security (harden-runner) | 成熟 (v2.19.4) | 基础 (v2.12.1) | 基础 (v2.12.1) |
| Release Pipeline | 成熟 | 缺失 | 缺失 |
| PR Governance | 成熟 | 缺失 | 缺失 |

---

## Section 5: 值得 Mantle 借鉴的具体 Workflow 及理由

### 优先级排名

| 优先级 | 推荐项 | 实现复杂度 | 前置条件 | 理由 |
|---|---|---|---|---|
| **P0** | Claude Code Review + LLM Gateway | 中 | LLM Gateway 基础设施、Anthropic API | 最高 ROI 的自动化审查，block 模式提供安全保障 |
| **P0** | Universal harden-runner (audit) | 低 | 无 | 零成本供应链可见性，直接添加到所有工作流 |
| **P0** | Action SHA 钉扎 | 低 | 一次性迁移 | 防止供应链攻击的基础措施 |
| **P1** | 分级 CI (workflow_call) | 中 | 重构现有 CI | PR 轻量/merge queue 完整分级显著降低 CI 成本 |
| **P1** | 三阶段 Release Pipeline | 高 | 脚本开发、GPG 密钥 | 完整的 start → RC → final → verify 链 |
| **P1** | 复合 Setup Action | 中 | 工具链标准化 | DRY 原则，统一所有 CI 工作流的环境设置 |
| **P2** | Vouch 系统 | 低 | mitchellh/vouch Action | 轻量级外部贡献者信任管理 |
| **P2** | GPG 签名 + Build Attestation | 中 | GPG 密钥基础设施 | Release 完整性链 |
| **P2** | cargo-udeps 每日报告 | 低 | nightly 工具链 | 依赖卫生自动化 |
| **P3** | 跨仓库接口测试 | 高 | 跨仓库 PAT、测试框架 | 下游兼容性信心（适用于多仓库项目） |

### 详细推荐

#### P0-1: Claude Code Review + LLM Gateway

**是什么**: 基于 Anthropic Claude Code Action 的自动化 PR 代码审查，通过 LLM Gateway 代理路由 API 请求。

**为什么重要**:
- 每个 PR 自动获得高质量代码审查，减少人工审查负担
- LLM Gateway 提供：集中化访问控制、使用监控、成本核算、请求日志
- block 模式 harden-runner 确保 AI 执行环境的网络隔离
- 去重机制避免重复评论

**实现步骤**:
1. 部署 LLM Gateway（可使用现有 API proxy 方案如 litellm）
2. 配置 `LLM_GATEWAY_API_KEY` secret 和 `LLM_GATEWAY_HOSTNAME` variable
3. 复制 `claude-review.yml`，调整 prompt 为 Mantle 代码库特定指南
4. 添加 `BaseRunnerGroup` 或等效的 runner group 以访问 Gateway
5. 配置 harden-runner block 模式和允许端点列表

#### P0-2: Universal harden-runner

**是什么**: 在所有工作流中添加 `step-security/harden-runner`（至少 audit 模式）。

**为什么重要**: 零入侵成本，立即获得 CI/CD 供应链可见性。审计模式记录所有出站网络调用，无需 allowlist 维护。

**Base 自身的覆盖情况**: base/base 广泛采用 harden-runner 但并非全覆盖——`verify-release.yml` 是已知缺口。Mantle 在借鉴时应追求完全覆盖，避免遗漏。

**实现步骤**: 在每个工作流的第一个 step 添加 harden-runner，确保无遗漏（包括验证类和工具类工作流）。

#### P1-1: 分级 CI

**是什么**: 一个可复用的 `workflow_call` CI 核心，被轻量（PR）和完整（merge queue）两个调用方使用。

**为什么重要**: PR 级 CI 只构建/测试受影响的 crate（显著减少 CI 时间和成本），而 merge queue 运行完整测试（确保合并质量）。

**实现关键**: 需要实现 affected-only 构建检测（Base 使用 `just` + git diff 实现）。

---

## Section 6: Base 独特模式或创新点

### 6.1 LLM Gateway 代理架构

Base 不直接使用 Anthropic API key，而是通过内部 LLM Gateway 代理所有 AI 请求。这是生产级 AI 集成的标杆模式：
- **访问控制**: API key 不暴露给 CI 环境，通过 Gateway 统一管理
- **可观测性**: 所有 AI 请求可集中监控和审计
- **成本管理**: 可在 Gateway 层实现配额和计费
- **安全隔离**: 结合 harden-runner block 模式，AI 工作流只能访问 Gateway 和 GitHub

### 6.2 唯一的 Block 模式网络隔离

在 26 个工作流中，只有 `claude-review.yml` 使用 `egress-policy: block`。设计考量：
- AI 审查执行第三方 Action（Claude Code Action），比纯 shell 脚本风险更高
- block 模式确保即使 Action 被篡改，也无法向非预期端点泄露数据
- 其他工作流使用 audit 模式，在可见性和维护成本间取得平衡

### 6.3 部分失败恢复（Release Pipeline）

`build-release.yml` 的 `find-release-artifacts` 作业是独特设计：
```yaml
if: ${{ !cancelled() }}  # 即使上游失败也执行
```
检查哪些构建产物成功创建，允许后续 publish 作业使用可用的子集继续。例如：如果 macOS 构建失败但 Linux 构建成功，仍可发布 Linux 二进制和 Docker 镜像。

### 6.4 跨仓库 Cargo Patch 测试

`base-std-fork-tests.yml` 和 `base-anvil-package.yml` 使用 Cargo `--config patch` 机制在 CI 中测试预编译器变更对下游的影响：
```bash
cargo --config "patch.\"https://github.com/base/base.git\".base-common-precompiles.path=\"$GITHUB_WORKSPACE/crates/common/precompiles\""
```
这避免了发布新版本再测试的等待周期，在 PR 阶段就能发现下游兼容性问题。

### 6.5 SP1 ELF Manifest 自动化

ZK 证明系统的 ELF 二进制管理是区块链项目独特的 CI 需求：
- 自动检测 ELF 输入变更（通过 Python 脚本分析 Cargo 依赖图）
- 重建 ELF 并更新 manifest
- 通过 automation PR 流程确保变更可追踪和可审查
- `force-with-lease` 确保幂等推送

### 6.6 Affected-Only 构建策略

Base 通过 `just` 任务运行器实现精确的受影响 crate 检测：
- `just build::affected-ci "origin/main"` — 仅构建受影响的 crate
- `just test-affected-ci "origin/main"` — 仅测试受影响的 crate
- 基于 git diff 分析变更文件，映射到 Cargo workspace 的 crate 依赖图
- PR 级 CI 使用 affected-only，merge queue 使用完整构建，形成成本-质量平衡

### 6.7 Vouch 信任数据库

轻量级外部贡献者信任管理，无需复杂的权限系统：
- 平面文件格式（`.github/VOUCHED.td`），一行一个用户名
- 通过 issue 评论命令管理（vouch/denounce/unvouch）
- 修改通过 PR + merge queue，确保审计追踪
- 自动关闭未授权的外部 PR

### 6.8 Binary Source Hash 缓存

`benchmark.yml` 使用 Cargo 源文件哈希（而非 git SHA）作为缓存键：
```yaml
key: ${{ runner.os }}-binaries-${{ hashFiles('Cargo.toml', 'Cargo.lock', 'crates/**', 'bin/**') }}
```
这意味着即使 git commit 变化（如文档或 CI 配置变更），只要源代码不变，就能复用已缓存的构建产物。

### 6.9 Devnet Cache Warming

`docker.yml` 在每次 main 推送时预热三个 devnet Docker 构建目标：
- `builder`、`consensus`、`batcher`
- 使用 `output=type=cacheonly`——仅写入缓存，不推送镜像
- 确保后续 devnet 构建（如系统测试）可以快速获取缓存层

### 6.10 幂等 PR 评论更新

`base-std-fork-tests.yml` 使用 HTML 标记实现 PR 评论的幂等更新：
```bash
marker="<!-- fork-test-results -->"
existing_id=$(gh api "repos/${repo}/issues/${pr}/comments" \
  --jq ".[] | select(.body | startswith(\"${marker}\")) | .id" | head -1)
```
既有评论则更新（`PATCH`），无则创建。避免多次推送导致的评论堆积。

---

## Diagrams

### Diagram 1: Base CI Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Pull Request 触发                            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌──────────┐  ┌───────────┐  ┌────────────┐
        │ ci-pr.yml│  │claude-    │  │ action-    │  + no-std, lychee,
        │(affected)│  │review.yml │  │ tests.yml  │    zepter, base-std-
        └────┬─────┘  │(AI审查)   │  │            │    fork-tests
             │        └───────────┘  └────────────┘
             │
             ▼
    ┌──────────────────┐
    │   ci-core.yml    │  ← workflow_call (affected-only params)
    │  ┌────────────┐  │
    │  │ metadata   │  │  cargo-deny, Cargo.lock, crate deps
    │  │ format     │  │  nightly rustfmt
    │  │ build      │  │  affected-only build (BasePerfRunnerGroup)
    │  │ clippy     │  │  affected-only clippy
    │  │ test       │  │  affected-only test (nextest + JUnit)
    │  │ bench      │  │  cargo bench --test
    │  │ docker*    │  │  conditional (Docker file changes only)
    │  └────────────┘  │
    └──────────────────┘
                               │
                     ┌─────────┴─────────┐
                     ▼                   │
              ┌─────────────┐            │
              │ Merge Queue │            │
              └──────┬──────┘            │
                     ▼                   │
            ┌──────────────────┐         │
            │   ci-core.yml    │         │
            │  (full params)   │         │
            │  ┌────────────┐  │         │
            │  │ + sigsegv  │  │         │
            │  │ + system   │  │         │
            │  │   tests    │  │         │
            │  └────────────┘  │         │
            └──────────────────┘         │
                     │                   │
                     ▼                   ▼
              ┌─────────────┐    ┌────────────────┐
              │  main 合并   │    │ci-main-cache   │
              └─────────────┘    │(warm cache)     │
                                 └────────────────┘
```

### Diagram 2: Release Pipeline Sequence

```
                  手动触发
                     │
                     ▼
           ┌─────────────────┐
           │ start-release   │  workflow_dispatch(bump_type)
           │                 │  → 创建 releases/vX.Y.Z 分支
           │                 │  → version-sync.sh → PR
           │                 │  → 创建跟踪 issue
           └────────┬────────┘
                    │ push to releases/v*
                    ▼
           ┌─────────────────┐
           │   create-rc     │  自动触发
           │                 │  → 版本检查 (skip if 0.0.0)
           │                 │  → create-tag.sh (rc)
           └────────┬────────┘
                    │ calls
                    ▼
           ┌─────────────────┐
           │  build-release  │  workflow_call(tag, is_final=false)
           │                 │  → 12 个二进制构建 (3 平台 × 4 二进制)
           │                 │  → 2 个 Docker 构建 (amd64/arm64)
           │                 │  → GPG 签名 + attestation
           │                 │  → Docker manifest merge
           └─────────────────┘
                    │
                    │ ... RC 测试验证 ...
                    │
                  手动触发
                    │
                    ▼
           ┌─────────────────┐
           │ publish-release │  workflow_dispatch(version)
           │                 │  → semver 验证
           │                 │  → Cargo.toml 版本匹配
           │                 │  → 幂等 tag 创建
           └────────┬────────┘
                    │ calls
                    ▼
           ┌─────────────────┐
           │  build-release  │  workflow_call(tag, is_final=true)
           │                 │  → 同上 + GitHub Release (draft)
           │                 │  → 二进制上传到 Release
           └────────┬────────┘
                    │ release published
                    ▼
           ┌─────────────────┐     ┌──────────────────┐
           │ verify-release  │     │ release-branch-ci │
           │                 │     │                   │
           │ → baseup verify │     │ → check-finalized │
           └─────────────────┘     └──────────────────┘
```

### Diagram 3: 10 维度能力矩阵可视化

```
维度                      base/base    contracts    docs
─────────────────────────────────────────────────────────
Upstream Auto-Sync        ░░░ 缺失     ░░░ 缺失    ░░░ 缺失
AI Code Review            ███ 成熟     ░░░ 缺失    ░░░ 缺失
PR Audit                  ▓▓░ 基础     ░░░ 缺失    ░░░ 缺失
Interactive Agent         ░░░ 缺失     ░░░ 缺失    ░░░ 缺失
Release Pipeline          ███ 成熟     ░░░ 缺失    ░░░ 缺失
CI/Testing                ███ 成熟     ▓▓░ 基础    ▓▓░ 基础
Security & Supply Chain   ███ 成熟     ▓▓░ 基础    ▓▓░ 基础
Benchmark                 ▓▓░ 基础     ░░░ 缺失    ░░░ 缺失
PR Governance             ███ 成熟     ░░░ 缺失    ░░░ 缺失
Documentation & Infra     ▓▓░ 基础     ░░░ 缺失    ▓▓░ 基础

图例: ███ 成熟  ▓▓░ 基础  ░░░ 缺失
```

### Diagram 4: Security Hardening Coverage Matrix

```
工作流                    harden-runner   SHA pin   permissions   签名/attestation
──────────────────────────────────────────────────────────────────────────────────
claude-review.yml         BLOCK ████      ✓         ✓             -
ci-core.yml               AUDIT ▓▓▓▓      ✓         ✓             -
ci-pr.yml                 (继承) ▓▓▓▓     ✓         ✓             -
ci-merge-queue.yml        (继承) ▓▓▓▓     ✓         ✓             -
build-release.yml         AUDIT ▓▓▓▓      ✓         ✓             GPG + SLSA
publish-release.yml       AUDIT ▓▓▓▓      ✓         ✓             -
verify-release.yml        无    ░░░░      ✓         ✓             GPG verify
vouch.yml                 AUDIT ▓▓▓▓      ✓         ✓(分层)       -
docker.yml                AUDIT ▓▓▓▓      ✓         ✓             -
benchmark.yml             AUDIT ▓▓▓▓      ✓         ✓             -
stale.yml                 AUDIT ▓▓▓▓      ✓         ✓             -
contracts/test.yml        AUDIT ▓▓▓▓*     ✓         ✗             -
docs/chromatic.yml        AUDIT ▓▓▓▓*     ✓         ✗             -
docs/file-size-checker.yml AUDIT ▓▓▓▓*    ✓         ✓             -

图例: BLOCK ████ = egress block   AUDIT ▓▓▓▓ = egress audit   无 ░░░░ = 未配置
     ✓ = 已配置   ✗ = 未配置   * = v2.12.1 旧版（contracts/docs）
```

---

## Source Coverage

| Source 类型 | 描述 | 覆盖状态 |
|---|---|---|
| **Primary** | 本地工作流 YAML 文件 | ✅ 全部 26 个工作流已读取并分析 |
| **Primary** | 仓库配置文件 | ✅ VOUCHED.td, action.yml, benchmark configs, PR template |
| **Primary** | Git commit SHA | ✅ 三个仓库的调研时 commit 已记录 |
| **Primary** | GitHub API 访问尝试 | ✅ 4 个端点类别已执行，结果已记录（详见 Section 1.4） |
| **Secondary** | GitHub Action 文档 | ⚠️ 未直接访问；基于工作流代码中的版本注释和已知功能推断 |

**注意**: Section 1.4 的 API 访问尝试已执行。Branch protection 和 secrets API 返回 401（权限受限），已标注 `不可访问 (权限受限)` 并记录了精确的端点和 HTTP 状态码。Rulesets 和 Environments API 成功访问（HTTP 200），数据已纳入分析。

---

## Gap Analysis

| Gap | 严重程度 | 说明 |
|---|---|---|
| Branch Protection 规则不可读 | 低 | API 返回 401；通过间接证据（merge queue、vouch 注释）确认存在但无法获取具体配置 |
| Secrets 名称列表不可读 | 低 | API 返回 401；通过代码扫描 `secrets.*` 引用构建了完整的已知清单 |
| GitHub Apps 不可确认 | 低 | installation API 非通用端点；间接证据仅发现 github-actions[bot] |
| `verify-release.yml` 缺少 harden-runner | 中 | base/base 唯一未配置 `step-security/harden-runner` 的工作流；该工作流执行 release 签名验证，下载外部二进制，存在供应链风险敞口 |
| 卫星仓库 harden-runner 版本滞后 | 中 | contracts/docs 使用 v2.12.1（base/base 使用 v2.19.4），存在安全更新延迟 |
| 卫星仓库缺少顶层 permissions 声明 | 中 | `base/contracts/test.yml` 和 `base/docs/chromatic.yml` 未声明顶层 `permissions`，依赖仓库默认的 `GITHUB_TOKEN` 权限，与 base/base 的最小权限实践不一致 |
| 缺少 dependabot/Renovate | 中 | 所有仓库均无自动依赖更新工具 |
| Action 文档未直接验证 | 低 | 未访问 Action marketplace 页面验证版本兼容性 |

---

## Revision Log

| 版本 | 日期 | 变更 |
|---|---|---|
| round-1 | 2026-06-10 | 初始深度调研草稿，覆盖全部 6 个 Outline 章节 |
| round-2 | 2026-06-10 | 修正两个过度声明：(1) harden-runner 覆盖率——`verify-release.yml` 未配置，从"全仓库"修正为"25/26"，影响 Executive Summary、Section 3.1、能力矩阵、Diagram 4、Gap Analysis、Mantle 推荐；(2) 顶层 permissions 声明——`contracts/test.yml` 和 `docs/chromatic.yml` 未声明，从"所有工作流"修正为"base/base 全量 + 卫星仓库部分缺失"，影响 Section 3.3、能力矩阵、Diagram 4、Gap Analysis |
