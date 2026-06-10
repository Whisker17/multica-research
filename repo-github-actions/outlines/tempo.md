---
topic: "Tempo GitHub Actions 完整调研"
project_slug: "github-action-opt"
topic_slug: "tempo-github-actions"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "github-action-opt/outlines/tempo-github-actions.md"
  draft: "github-action-opt/research-sections/tempo-github-actions/drafts/round-{n}.md"
  final: "github-action-opt/research-sections/tempo-github-actions/final.md"
  index: "github-action-opt/research-sections/_index.md"

scope: |
  对 tempoxyz/tempo（Rust, 29 个 workflow）和 tempoxyz/zones（Rust, 9 个 workflow）的 GitHub Actions 工作流及 repo 级配置进行完整调研。重点关注：(1) update-reth.yml——AI 驱动的上游追踪：cron 触发 → upstream 检测 → merge → Amp CLI 多轮 AI 修复 → CI 等待重试 → PR 创建 → Slack 通知；(2) amp-review.yml——Sourcegraph CRA AI 代码审查；(3) pr-audit.yml——comment-triggered 深度审计（Cyclops）；(4) release.yml——完整 release pipeline（SLSA、GPG、SBOM）；(5) bench.yml 系列——参数化 benchmark 设计。对每个 repo 枚举所有 .github/workflows/ 文件、.github/dependabot.yml、CODEOWNERS、PR template 及可访问的 branch protection / GitHub Environments / Apps / Secrets 信息。按 10 个改进维度分类并评级（成熟 / 基础 / 缺失），识别可借鉴模式和 Tempo 独特创新。

audience: "区块链基础设施工程师、DevOps/CI/CD 负责人、AI-augmented workflow 实践者，以及 Research Review Agent。读者熟悉 GitHub Actions 基础概念和 Rust 工具链，但需要一份从实际 workflow YAML 出发的深度分析，特别关注 AI agent 在 CI/CD 中的创新应用模式。"

expected_output: |
  github-action-opt/research-sections/tempo-github-actions/final.md，结构化研究文档，包含：
  1. Workflow 完整清单（per-file 结构化分析，含 YAML 元数据）
  2. Repo 级配置概况（CODEOWNERS、dependabot、scripts、无 PR template）
  3. AI workflow 深度分析（update-reth 完整流程、amp-review 实现、pr-audit 安全模型）
  4. Release pipeline 安全链分析（SLSA + GPG + SBOM + cosign）
  5. Benchmark 系统架构分析（参数解析、路由、调度、状态管理）
  6. 10 维度能力矩阵（评级 + 证据）
  7. Mantle 可借鉴模式清单
  8. Tempo 独特创新点总结

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-10T10:10:00Z"

multica_issue_id: "26b203f0-0776-4532-984a-8e4ae3423d76"
branch_name: "research/github-action-opt/tempo-github-actions"
base_commit: "79d472632bd30a5354fbec396f807e0bb63bdea1"
language: "中文"
research_depth: "deep"

codebase_path: "/Users/whisker/Work/src/networks/tempo/"

pinned_commits:
  tempoxyz_tempo: "HEAD at research time (2026-06-10)"
  tempoxyz_zones: "HEAD at research time (2026-06-10)"
---

# Research Outline: Tempo GitHub Actions 完整调研

## Research Questions

1. Tempo 的 AI 驱动上游追踪 workflow（update-reth.yml）完整流程是什么——从 cron 触发到 PR 创建，Amp CLI 如何集成多轮自动修复、CI 等待重试和失败诊断？其安全模型（token 隔离、bot 账户）和容错设计（超时、重试上限、graceful degradation）的具体实现？
2. Tempo 的 AI 代码审查（amp-review.yml）和 AI 深度审计（pr-audit.yml）分别采用什么工具和集成模式？两者在触发方式、安全控制（ACL、mTLS、org 门控）、参数化（命令解析、dry-run）方面有何异同？
3. Tempo 的 release pipeline（release.yml）如何实现多层加密签名（GPG + SLSA Sigstore + SBOM attestation）？与 zones repo 的简化版 release 的差异体现了什么设计取舍？
4. Tempo 的 benchmark 系统（bench.yml → bench-e2e.yml / bench-replay.yml + scheduled 变体）如何通过中央参数解析器（50+ 参数、300+ 行 JS 验证）实现 workflow 路由和复用？nightly regression 的状态管理和 stale detection 机制如何保障结果可靠性？
5. 两个 repo（tempo 29 workflows vs zones 9 workflows）的 CI/Testing 策略有何差异？tempo 的分区测试（2-3 partitions）、条件覆盖率（precompile change detection）、feature powerset 检查、no-std 交叉编译等模式的设计动机和效果？
6. Repo 级配置（CODEOWNERS 25 规则 vs zones 全局通配、dependabot 三生态 vs 两生态、helper scripts 10 个）如何与 workflow 协同工作？缺少 PR template 和 branch protection 信息对分析有何影响？
7. 按 10 个改进维度评估，Tempo 在 Upstream Auto-Sync、AI Code Review、PR Audit、Release Pipeline、Benchmark/Performance Regression 方面的成熟度如何？哪些模式值得 Mantle 借鉴？

## Source Access Constraints

> **C1 — 本地代码可用**：tempoxyz/tempo 和 tempoxyz/zones 代码库在 `/Users/whisker/Work/src/networks/tempo/` 本地可用，直接从本地文件系统读取 workflow YAML 和配置文件。所有引用基于调研时（2026-06-10）的 HEAD commit。
>
> **C2 — GitHub API 受限**：Branch protection rules、GitHub Environments、GitHub Apps、Secrets 名称列表需通过 GitHub API 访问，可能受权限限制。不可访问的配置将标注"不可访问 (权限受限)"，不作为缺失结论依据。

## Items

### item-1: Workflow 完整清单——tempo repo（29 个 workflow）

逐个分析 tempoxyz/tempo 的全部 29 个 workflow 文件，产出结构化元数据。

**Workflow 列表**（按类别分组）：

**AI 驱动（3 个）**：
- `update-reth.yml`（Update reth deps）——AI 驱动上游追踪，Amp CLI 多轮修复
- `amp-review.yml`（Amp Code Review）——Sourcegraph CRA AI 代码审查
- `pr-audit.yml`（Pull request audit）——Cyclops 深度审计，mTLS 事件发布

**Release/Publishing（5 个）**：
- `release.yml`（Release）——完整 release pipeline，SLSA + GPG + SBOM
- `release-pr.yml`（Release PR）——自动 changelog PR 创建
- `publish.yml`（Publish alloy crates）——crates.io 发布，keyless OIDC
- `publish-check.yml`（Publish check）——发布前 dry-run 验证
- `reproducible-build.yml`（Reproducible Build）——确定性二进制构建

**Benchmark（6 个）**：
- `bench.yml`（bench）——中央参数解析和 workflow 路由
- `bench-e2e.yml`（bench-e2e）——E2E 双节点 benchmark
- `bench-e2e-scheduled.yml`（bench-e2e-scheduled）——nightly E2E regression
- `bench-replay.yml`（bench-replay）——链上 block replay benchmark
- `bench-replay-scheduled.yml`（bench-replay-scheduled）——nightly replay regression
- `codspeed-microbench.yml`（CodSpeed microbenchmarks）——Rust 微基准测试

**CI/Testing（6 个）**：
- `lint.yml`（Lint）——clippy/fmt/crate-checks/docs/typos/deny/zepter/no-std
- `test.yml`（Test）——分区测试/E2E/flaky/CLI/MSRV
- `coverage.yml`（Precompiles Coverage）——cargo + forge 覆盖率合并
- `specs.yml`（Specs）——Solidity/Rust precompile 规范验证
- `rpc-tests.yml`（RPC Tests）——live RPC 端点测试
- `build.yml`（Build binaries）——手动二进制构建

**Docker/Infrastructure（5 个）**：
- `docker.yml`（Docker Build）——多镜像构建 + cosign 签名
- `docker-profiling.yml`（Docker Build Profiling）——性能分析镜像
- `build-devnet.yml`（Build devnet from branch）——PR 触发 devnet 构建
- `deploy-docs.yml`（Deploy TIPs to Docs）——Vercel 文档部署
- `changelog.yml`（Changelog）——AI 辅助 changelog 生成

**PR Governance/Maintenance（4 个）**：
- `label-pr.yml`（Label PRs）——自动 PR 标签
- `stale.yml`（Close Stale PRs）——过期 PR 清理
- `sync-from-upstream.yml`（Sync main with upstream）——fork 同步
- `semver-check.yml`（Semver check）——语义版本检查

**每个 workflow 的结构化分析格式**：

```yaml
workflow_name: "xxx"
file: "xxx.yml"
triggers:
  - type: schedule/push/pull_request/issue_comment/workflow_dispatch/workflow_call/label
    details: "具体触发条件"
purpose: "一句话描述"
category: "AI | Release | Benchmark | CI | Docker | Governance"
ai_features: true/false
ai_tool: "Amp CLI / Sourcegraph CRA / Cyclops / AMP codegen / none"
permissions:
  - "permission: scope"
concurrency:
  group: "xxx"
  cancel_in_progress: true/false
timeout_minutes: N
runner: "ubuntu-latest / depot-xxx / self-hosted"
notable_patterns:
  - "pattern description"
```

- **Priority**: high
- **Dependencies**: none

### item-2: Workflow 完整清单——zones repo（9 个 workflow）

逐个分析 tempoxyz/zones 的全部 9 个 workflow 文件，对比 tempo repo 的对应 workflow 标注差异。

**Workflow 列表**：
- `build.yml`——手动构建（增加 tempo-bench binary，使用 `just build`）
- `docker.yml`——Docker 构建（仅 ghcr.io，双 daily schedule）
- `docker-profiling.yml`——性能分析镜像
- `label-pr.yml`——自动标签
- `lint.yml`——Lint（pinned nightly-2026-02-21）
- `pr-audit.yml`——PR 审计（reusable workflow from tempoxyz/gh-actions）
- `release.yml`——Release（无 SLSA/SBOM/GPG）
- `specs.yml`——Specs（zone-only forge tests，无覆盖率）
- `test.yml`——测试（单 job，无分区）

**关键对比维度**：
- zones 缺少的 workflow 类别：AI review（无 amp-review）、上游追踪（无 update-reth）、benchmark 系统（无 bench 全系列）、覆盖率、RPC 测试
- zones 简化的 workflow：release（无加密签名链）、lint（无 feature powerset/no-std）、test（无分区/flaky/MSRV）
- zones 独有模式：reusable workflow（pr-audit.yml 调用 tempoxyz/gh-actions）

- **Priority**: high
- **Dependencies**: none

### item-3: Repo 级配置分析

分析两个 repo 的非 workflow 配置文件及其与 workflow 的协同关系。

**tempo repo 配置**：

- **CODEOWNERS**（25 条规则）：
  - 路径级所有权：bin/tempo、crates/precompiles、crates/contracts、crates/evm、crates/node、crates/primitives、tips 等
  - 核心维护者：@0xKitsune、@klkvr、@mattsse、@SuperFluffy、@0xrusowsky、@fgimenez
  - TIPs 审查者包含 @danrobinson、@dankrad（学术/协议设计背景）
  - 与 specs.yml、semver-check.yml 的 path filter 对齐程度分析

- **dependabot.yml**（三生态系统）：
  - cargo：weekly，open PR limit 1，minor/patch 分组，7 天 cooldown
  - github-actions：weekly，分组
  - docker：weekly，分组
  - 标签：A-dependencies、A-ci

- **.github/scripts/**（10 个 helper 脚本）：
  - benchmark 基础设施：bench-e2e-classify.js、bench-e2e-scheduled-refs.sh、bench-replay-charts.py、bench-replay-scheduled-refs.sh、bench-replay-summary.py、bench-slack-notify.js、bench-slack-users.json、bench-tempo-replay.sh、bench-update-status.js
  - 编译检查：check_no_std.sh
  - 脚本与 workflow 的调用关系映射

- **缺失配置**：无 PULL_REQUEST_TEMPLATE.md

**zones repo 配置**：
- **CODEOWNERS**：全局通配 `* @mattsse @0xKitsune`
- **dependabot.yml**：cargo + github-actions（无 docker）
- **缺失配置**：无 PULL_REQUEST_TEMPLATE.md、无 scripts 目录

**不可访问配置**（需 GitHub API）：
- Branch protection rules / repo rulesets
- GitHub Environments 配置
- 已配置的 GitHub Apps
- Secrets 名称列表

- **Priority**: medium
- **Dependencies**: none

### item-4: AI Workflow 深度分析——update-reth.yml

对 Tempo 核心创新 workflow update-reth.yml 进行逐步骤深度分析。这是本调研的核心产出之一。

**完整流程分析**：

1. **触发机制**：
   - 每日 3 AM UTC cron + 手动 workflow_dispatch
   - 并发控制：`update-reth` group，cancel-in-progress: false（保证顺序执行）

2. **上游检测与 Merge**：
   - 从 reth upstream 拉取最新 commit
   - 自动 rebase，冲突自动解决（Cargo.toml/Cargo.lock 采用 ours 策略，保留 source fixes）

3. **AI 修复循环**（核心创新）：
   - **Round 1**：cargo clippy 编译修复
     - Amp CLI 安装：`https://ampcode.com/install.sh`
     - 自定义 amp-run wrapper：`--stream-json --take-me-back`
     - 最大 10 次尝试，60 分钟 deadline
   - **Round 2**：cargo nextest 测试编译修复
     - 同样 max 10 attempts，60-min deadline
   - **Feature lint**：zepter feature propagation 检查

4. **PR 创建与描述生成**：
   - Amp CLI 生成 PR description（总结 upstream reth commits 和 source migrations）
   - 计算 revision 范围，创建/更新 PR

5. **CI 等待与修复循环**：
   - 30 分钟 timeout 等待 CI 完成
   - CI 失败 → Amp 分析失败原因 → 修复 → 重新触发
   - 最大 10 次 CI fix 尝试，总 60 分钟 window

6. **通知**：
   - Slack webhook（SLACK_ENG_TEMPO_WORKFLOWS_WEBHOOK_URL）
   - Emoji-coded 状态

**安全模型**：
- Derek bot 账户 token（DEREK_UPDATE_RETH_TOKEN）——git push 身份隔离
- AMP_API_KEY——AI 工具认证
- RPC URL secrets——testnet/devnet 访问
- `set +e/set -e` graceful failure handling

**容错设计**：
- Amp failure 不阻塞 workflow（exit 0）
- 局部成功推进（push partial work）
- Job timeout 120 分钟（硬限制）

- **Priority**: high
- **Dependencies**: item-1

### item-5: AI Workflow 深度分析——amp-review.yml 与 pr-audit.yml

对比分析 Tempo 的两个 AI 辅助审查 workflow。

**amp-review.yml**（AI 代码审查）：
- 触发：PR opened/reopened/ready_for_review/labeled + "amp" label 门控 + 非 draft
- AI 工具：Sourcegraph CRA（ghcr.io/sourcegraph/cra-github:latest Docker 镜像）
- 集成方式：Docker entrypoint `node /app/dist/bin/review-action.js`
- 安全：GITHUB_TOKEN + AMP_API_KEY + 可配置 AMP_SERVER_URL
- 并发：per-PR group，cancel-in-progress: true（新 push 取消旧运行）
- 设计理念：最小配置，delegating 全部逻辑到 Sourcegraph CRA

**pr-audit.yml**（深度审计）：
- **双触发模式**：
  - Label trigger：PR 添加 `cyclops` 或 `agentic-audit` 标签
  - Comment trigger：`cyclops audit`、`@decofe cyclops audit`、`derek audit`
- **ACL 检查**：tempoxyz org 成员验证（commenter + PR author）
- **参数解析**（300+ 行 JS）：
  - 灵活语法：key=value、key:value、quoted values、boolean flags
  - 支持参数：config、iterations、hours、models、run-label、dry-run、note、fast
  - 验证规则：iterations/hours 整数验证、note max 160 chars、fast shorthand
- **事件发布**：
  - mTLS 认证（EVENTS_KEY + EVENTS_CERT + EVENTS_ARGS）
  - JSON payload（pr_number、sha、source、actor、config 参数）
  - Base64 编码复杂内容
- **UX 设计**：
  - Eyes emoji 即时确认
  - 回复 comment 展示解析结果和配置摘要
  - 发布状态更新
- **Token 隔离**：DEREK_BENCH_ACK_TOKEN（成员验证）、DEREK_BENCH_TOKEN（comment 操作）

**zones pr-audit.yml**——Reusable workflow 模式：
- 调用 `tempoxyz/gh-actions/.github/workflows/pr-audit.yml@main`
- 仅传递 secrets（EVENTS_KEY/EVENTS_CERT/EVENTS_ARGS）
- 标志着 Tempo 向共享 workflow 基础设施的演进

**对比总结**：
- amp-review：轻量级、Docker-based、仅限 PR 级审查
- pr-audit：重量级、事件驱动、支持深度审计、丰富参数化、org 门控

- **Priority**: high
- **Dependencies**: item-1

### item-6: Release Pipeline 安全链分析

深度分析 tempo release.yml 的多层加密安全链和 zones release.yml 的简化版对比。

**tempo release.yml 安全链**：

1. **Version 验证**：check-version job 确保 Cargo.toml 版本与 tag 一致
2. **Multi-platform 构建**：matrix（x86_64-linux、aarch64-linux、aarch64-darwin）
3. **SBOM 生成**：anchore/sbom-action@v0.24.0，SPDX-JSON 格式
4. **GPG 签名**：GPG_SIGNING_KEY + GPG_PASSPHRASE，生成 .asc 签名文件
5. **SLSA Attestation**：actions/attest@v4.1.0，SLSA v1 predicate，keyless Sigstore via GitHub OIDC
6. **SBOM Attestation**：attests both archive and bare binary
7. **Checksum**：.sha256 per artifact
8. **Release 创建**：draft release，auto-detect prerelease（alpha/beta/rc）
9. **Cloudflare R2 上传**：私有 fork sha-based routing，公开 binaries/ path

**zones release.yml 差异**：
- 相同：multi-platform matrix、version check、checksum
- 缺少：SLSA attestation、GPG 签名、SBOM 生成和 attestation
- 缺少：Cloudflare R2 上传
- 差异体现的取舍：zones 是辅助项目，安全链需求低于主项目

**相关 publishing workflow**：
- release-pr.yml：GitHub App token 驱动的自动 changelog PR
- publish.yml：keyless OIDC auth via crates-io-auth-action
- publish-check.yml：path-filtered dry-run 验证
- reproducible-build.yml：SOURCE_DATE_EPOCH 确定性构建 + 3 次重试逻辑

**Docker 签名**：
- docker.yml 使用 cosign 签署所有推送的镜像
- 镜像标签策略：semver、latest、edge、nightly、sha

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-7: Benchmark 系统架构分析

深度分析 Tempo 的 benchmark 系统——从参数解析到结果可视化的完整流程。

**系统架构**：bench.yml 作为中央路由器 → 按 mode 分发到 bench-e2e.yml 或 bench-replay.yml。

**中央参数解析器（bench.yml）**：
- 触发：issue_comment（@decofe bench / derek bench）
- Org 成员门控（tempoxyz）
- 50+ 参数，300+ 行 JS 验证逻辑
- 参数类别：
  - Mode/Preset：e2e/replay，preset name（tip20、tip20_2d_nonces、mpp、mix 等）
  - E2E 调优：duration（default 300s/e2e 90s）、bloat（1/10/100 GiB）、tps、accounts
  - Hardfork 测试：baseline-hardfork/feature-hardfork（T0-T6，必须成对）
  - Feature flags：baseline-features/feature-features（Cargo features）
  - Refs：baseline/feature（git refs）、txgen-ref
  - Profiling：samply、tracy（off/on/full）、tracy-seconds/offset
  - Observability：otlp、valscope、metrics
  - Replay-specific：blocks（default 5000）、warmup（default blocks/4）、chain
  - Run 控制：force-bloat、no-cache、no-slack、run-pairs
- PR head SHA pinning：ack job 时锁定 SHA（可重现性保证）

**E2E Benchmark（bench-e2e.yml）**：
- Runner：self-hosted bare-metal-dual-schelk
- Timeout：300 分钟
- 双节点对比：baseline vs feature builds
- State bloat 模拟：0-100 GiB
- Hardfork 测试：独立 hardfork 版本
- Profiling 集成：Samply（Firefox Profiler URL）、Tracy（native viewer）
- Observability：OTLP traces/logs → ClickHouse → Grafana 动态 URL
- ValScope 静态报告
- Nushell 脚本驱动（bench-e2e.nu）

**Replay Benchmark（bench-replay.yml）**：
- 真实链上数据 replay via Engine API
- Chain 选择：mainnet/testnet
- 交替执行：baseline-1 → feature-1 → baseline-2 → feature-2
- Python 分析 + matplotlib 图表（latency_throughput、wait_breakdown、gas_vs_latency）
- 图表推送到 decofe/tempo-bench-charts repo

**Nightly Regression（scheduled 变体）**：
- bench-e2e-scheduled：02:00 UTC，tip20 preset，state persistence
- bench-replay-scheduled：00:00/01:00 UTC（mainnet/testnet 错峰），per-chain 状态
- Stale Docker 检测（>24h）→ Slack 告警 → 中止 benchmark
- State 管理：成功运行 → push feature-ref 到 charts repo → 下次作为 baseline

**CodSpeed Microbenchmarks（codspeed-microbench.yml）**：
- Push main + PR 触发
- Criterion-compatible Rust benchmark
- 包：tempo-evm、tempo-precompiles
- Feature 隔离：build phase only

- **Priority**: high
- **Dependencies**: item-1

### item-8: CI/Testing 策略分析

分析 Tempo 的 CI/Testing workflow 设计模式及其效果。

**lint.yml 多层检查**：
- clippy（nightly，all-targets，all-features，strict warnings）
- fmt（nightly formatting）
- crate-checks（feature powerset，2 分区）——验证 feature flag 组合兼容性
- docs（cargo doc，发布到 GitHub Pages）
- typos（拼写检查）
- deny（外部 workflow from tempoxyz/ci，依赖安全）
- zepter（feature propagation 一致性）
- no-std（RISC-V 32 交叉编译）
- lint-success 聚合器（re-actors/alls-green）

**test.yml 分区与条件覆盖**：
- genesis 检查：生成 genesis + 100 accounts，验证与 test-genesis.json 一致
- test：2 分区，nextest，条件 coverage（precompile change detection）
- e2e：3 分区，RUST_MIN_STACK=8388608（栈溢出缓解）
- e2e-flaky：独立 flaky test suite，continue-on-error
- cli：smoke test（test-cli.sh）
- msrv：Rust 1.93 最低版本检查
- test-success 聚合器

**coverage.yml 覆盖率合并**：
- workflow_call：从 test.yml 和 specs.yml 调用
- 等待 Test workflow 完成（max 30 min）
- 合并 cargo test + forge test 覆盖数据
- LLVM profdata → lcov → HTML 报告
- PR comment 覆盖率摘要

**specs.yml 规范验证**：
- forge build + ABI alignment check（Rust vs Solidity）
- foundry-resolver-smoke test
- 条件 forge test coverage（precompile change detection）
- 覆盖率数据传递到 coverage.yml

**rpc-tests.yml**：
- 路径过滤：crates/node、crates/primitives、crates/revm
- Matrix：testnet（required）、devnet（optional）
- 使用 ci-rpc nextest profile

**zones 差异**：
- test.yml：单 job、无分区、builds forge artifacts
- lint.yml：pinned nightly-2026-02-21（shellexpand 兼容）、无 feature powerset/no-std
- specs.yml：zone-only forge tests、无覆盖率

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-9: Docker/Infrastructure 与 PR Governance

分析 Docker 构建策略和 PR 管理 workflow。

**docker.yml（tempo）**：
- 镜像矩阵：tempo、tempo-sidecar、tempo-xtask
- Registry：ghcr.io + Docker Hub 双推
- 标签策略：semver、latest、edge、nightly、sha
- cosign 镜像签名
- Events 发布（devnet/registry 编排）
- Friday timeout 延长（172800s vs 18000s）
- fork 过滤（github.repository != 'tempoxyz/tempo' → skip main push）

**docker.yml（zones）**：
- 仅 ghcr.io
- 双 daily schedule（09:05、20:30 UTC）
- 简化标签策略

**build-devnet.yml**：
- PR comment 触发（/build-devnet）
- Member 权限验证
- Events 发布到外部编排服务
- Devnet 命名：devnet-pr-{PR_NUMBER}

**PR Governance**：
- label-pr.yml：PR opened → 运行 label_pr.js → 基于文件变更自动标签
- stale.yml：7 天 stale + 3 天 close（含 draft PR）
- sync-from-upstream.yml：每小时 fork 同步（官方 repo skip）
- semver-check.yml：publish-crates.sh --semver-check（path-filtered）

**Documentation**：
- changelog.yml：PR 变更 → AMP AI codegen 自动 changelog 条目（tempoxyz/changelogs）
- deploy-docs.yml：tips/ 变更 → Vercel webhook 触发部署

- **Priority**: medium
- **Dependencies**: item-1, item-2

### item-10: 10 维度能力矩阵

按以下 10 个维度对 Tempo 的 GitHub Actions 能力进行分类评估，产出结构化能力矩阵。

**评级标准**：
- **成熟**：有专门 workflow，设计完善，生产可用，包含安全模型和容错机制
- **基础**：有相关功能但较简单，或分散在其他 workflow 中
- **缺失**：没有对应的 workflow 或功能

**维度定义与初步评估**：

| 维度 | 评估范围 | 相关 Workflow |
|------|----------|--------------|
| Upstream Auto-Sync | 上游追踪、自动合并、AI 修复、CI 验证 | update-reth.yml, sync-from-upstream.yml |
| AI Code Review | AI 辅助代码审查的触发、执行、集成 | amp-review.yml |
| PR Audit | 深度 PR 审计的触发、参数化、安全模型 | pr-audit.yml (tempo + zones) |
| Interactive Agent | 基于 comment 的交互式 agent 能力 | bench.yml (comment trigger), pr-audit.yml (comment trigger), build-devnet.yml |
| Release Pipeline | 构建、签名、发布、验证的完整流程 | release.yml, release-pr.yml, publish.yml, publish-check.yml, reproducible-build.yml |
| CI / Testing | 代码质量检查、测试、覆盖率的完整性 | lint.yml, test.yml, coverage.yml, specs.yml, rpc-tests.yml |
| Security & Supply Chain | 依赖管理、签名、attestation、SBOM | dependabot.yml, release.yml (SLSA/GPG/SBOM), docker.yml (cosign) |
| Benchmark / Performance Regression | 性能测试、回归检测、结果分析的完整性 | bench.yml series (6 files), codspeed-microbench.yml |
| PR Governance | PR 生命周期管理、标签、过期、模板 | label-pr.yml, stale.yml, semver-check.yml |
| Documentation & Infrastructure | 文档部署、changelog、helper scripts | deploy-docs.yml, changelog.yml, .github/scripts/ |

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6, item-7, item-8, item-9

### item-11: Mantle 可借鉴模式与 Tempo 独特创新

基于全面分析，提炼 Tempo 的核心创新和 Mantle 可借鉴的具体模式。

**Tempo 独特创新点**（初步识别）：

1. **AI 驱动上游追踪（update-reth.yml）**：
   - 行业首创：cron → upstream detection → merge → AI fix loop → CI verification → PR creation 的完整自动化
   - Amp CLI wrapper 设计：--stream-json 结构化输出 + --take-me-back 上下文恢复
   - 双循环修复（clippy + nextest compilation）+ CI 修复循环的三层容错

2. **Comment-driven Benchmark 系统**：
   - 50+ 参数的 JS 验证框架，支持复杂语法（key=value、quoted、flags）
   - 中央路由器模式（bench.yml → e2e/replay）
   - Nightly regression 的状态管理（external charts repo）
   - Stale Docker 检测防止无效数据

3. **多层加密安全链**：
   - GPG + SLSA Sigstore + SBOM attestation 的组合
   - 确定性构建（reproducible-build.yml）
   - cosign Docker 镜像签名

4. **Event-driven 审计架构**：
   - mTLS 认证的事件发布（PR audit → external audit service）
   - 解耦 GitHub workflow 与审计执行
   - Reusable workflow 基础设施（gh-actions repo）

5. **Token 隔离策略**：
   - 5+ 独立 token（DEREK_UPDATE_RETH_TOKEN、DEREK_BENCH_ACK_TOKEN、DEREK_BENCH_TOKEN、AMP_API_KEY、EVENTS_KEY/CERT）
   - 每个 workflow/功能域独立 token

**Mantle 可借鉴清单**（待 deep draft 细化）：
- 上游追踪自动化的 Amp CLI 集成模式
- Comment-triggered benchmark 参数解析框架
- Release pipeline 安全链升级路径
- Event-driven PR 审计架构
- Nightly regression 状态管理模式
- Conditional coverage 的 precompile change detection 模式

- **Priority**: high
- **Dependencies**: item-4, item-5, item-6, item-7, item-8, item-10

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| workflow_metadata | 结构化 YAML 元数据：workflow_name、file、triggers、purpose、category、ai_features、ai_tool、permissions、concurrency、timeout、runner、notable_patterns | item-1, item-2 |
| ai_integration_model | AI 工具的具体调用方式（CLI/Docker/API）、参数、wrapper 设计、输出解析 | item-4, item-5 |
| security_model | Token 权限（per-workflow 隔离）、ACL（org 门控）、认证方式（mTLS/OIDC/API key）、dry-run 支持 | item-4, item-5, item-6 |
| error_handling | 重试策略（max attempts + deadline）、graceful degradation（exit 0 on AI failure）、continue-on-error 使用、超时控制 | item-4, item-5, item-7 |
| concurrency_control | 并发组设计、cancel-in-progress 策略、workflow 间依赖（workflow_call） | item-1, item-2, item-4, item-5 |
| benchmark_parameters | 参数定义（名称、类型、默认值、验证规则）、mode-specific defaults、PR SHA pinning | item-7 |
| state_management | Nightly regression 状态持久化（external repo）、stale detection、baseline tracking | item-7 |
| crypto_signing_chain | GPG 签名 → SLSA attestation → SBOM → cosign 的完整链路和工具版本 | item-6 |
| test_partitioning | Nextest 分区策略、conditional coverage、flaky test 隔离、MSRV 检查 | item-8 |
| repo_config | CODEOWNERS 结构、dependabot 配置、helper scripts 调用关系、缺失的配置 | item-3 |
| capability_rating | 10 维度评级（成熟/基础/缺失）、评级依据（具体 workflow 和功能点）、与其他项目的对比基准 | item-10 |
| borrowable_patterns | 可借鉴模式描述、适用场景、迁移难度、依赖条件 | item-11 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | Tempo GitHub Actions 全景图：29 个 workflow 按类别分组（AI/Release/Benchmark/CI/Docker/Governance），展示 workflow 间的调用关系（workflow_call）和共享基础设施（helper scripts、reusable workflows、shared secrets） | mermaid | item-1, item-2 |
| diag-2 | flow | update-reth.yml 完整流程图：cron trigger → upstream fetch → rebase → conflict resolution → Amp clippy fix loop (max 10, 60min) → Amp nextest fix loop → zepter lint → PR create/update → Amp PR description → CI wait loop (30min) → CI fix loop → Slack notification，标注每步的超时和失败分支 | mermaid | item-4 |
| diag-3 | comparison | AI Workflow 对比矩阵：update-reth（Amp CLI fix）vs amp-review（Sourcegraph CRA review）vs pr-audit（Cyclops audit）vs changelog（AMP codegen），按触发方式、AI 工具、安全模型、参数化、输出类型对比 | table | item-4, item-5 |
| diag-4 | architecture | Benchmark 系统架构图：bench.yml（参数解析+路由）→ bench-e2e.yml / bench-replay.yml，scheduled variants → state persistence（charts repo），展示 runner 类型、数据流（ClickHouse/Grafana/Slack）和 helper scripts 调用链 | mermaid | item-7 |
| diag-5 | flow | Release 安全链流程图：build-release → SBOM generation（anchore/sbom-action）→ GPG signing → SLSA attestation（actions/attest）→ SBOM attestation → checksum → create-release → upload-cloudflare，标注每步的工具和 secret | mermaid | item-6 |
| diag-6 | taxonomy | 10 维度能力矩阵可视化：雷达图或热力图展示 Tempo 在 10 个维度的评级（成熟/基础/缺失），标注每个维度的关键 workflow | mermaid/table | item-10 |
| diag-7 | comparison | tempo vs zones Workflow 对比矩阵：并列展示两个 repo 的 workflow 覆盖差异，标注 zones 缺少的类别和简化的实现 | table | item-1, item-2 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | local_codebase | tempoxyz/tempo .github/workflows/ 下全部 29 个 YAML 文件——从本地 `/Users/whisker/Work/src/networks/tempo/tempo/.github/workflows/` 直接读取 | 29 |
| src-2 | local_codebase | tempoxyz/zones .github/workflows/ 下全部 9 个 YAML 文件——从本地 `/Users/whisker/Work/src/networks/tempo/zones/.github/workflows/` 直接读取 | 9 |
| src-3 | local_codebase | Repo 级配置文件：CODEOWNERS、dependabot.yml（两个 repo）——从本地直接读取 | 4 |
| src-4 | local_codebase | Helper scripts：`.github/scripts/` 下全部 10 个文件——从本地直接读取 | 10 |
| src-5 | github_api | Branch protection rules、GitHub Environments、GitHub Apps、Secrets 名称（如可访问）——通过 GitHub API 或 gh CLI 查询 | 0 (best effort) |
| src-6 | external_reference | GitHub Actions 官方文档：workflow syntax、reusable workflows、OIDC token、attestations——用于验证 Tempo 使用的 Actions 特性 | 2 |
| src-7 | external_reference | Amp CLI / Sourcegraph CRA / Cyclops / CodSpeed 工具文档——用于验证 AI 工具的能力和集成方式 | 2 |

## Required Output Tables

### Workflow 完整清单（per-file 结构化元数据）

| workflow_name | file | repo | triggers | category | ai_features | ai_tool | notable_patterns |
|---------------|------|------|----------|----------|-------------|---------|-----------------|
| Update reth deps | update-reth.yml | tempo | schedule, dispatch | AI | true | Amp CLI | 多轮 AI fix loop, CI wait/retry |
| ... | ... | ... | ... | ... | ... | ... | ... |

### 10 维度能力矩阵

| 维度 | 评级 | 关键 Workflow | 证据摘要 | 可借鉴价值 |
|------|------|--------------|----------|-----------|
| Upstream Auto-Sync | 待评估 | update-reth.yml | 待填充 | 待评估 |
| AI Code Review | 待评估 | amp-review.yml | 待填充 | 待评估 |
| PR Audit | 待评估 | pr-audit.yml | 待填充 | 待评估 |
| Interactive Agent | 待评估 | bench.yml, pr-audit.yml | 待填充 | 待评估 |
| Release Pipeline | 待评估 | release.yml series | 待填充 | 待评估 |
| CI / Testing | 待评估 | lint.yml, test.yml | 待填充 | 待评估 |
| Security & Supply Chain | 待评估 | dependabot, release, docker | 待填充 | 待评估 |
| Benchmark / Performance Regression | 待评估 | bench.yml series | 待填充 | 待评估 |
| PR Governance | 待评估 | label-pr, stale, semver-check | 待填充 | 待评估 |
| Documentation & Infrastructure | 待评估 | deploy-docs, changelog | 待填充 | 待评估 |

### AI Workflow 对比表

| 维度 | update-reth.yml | amp-review.yml | pr-audit.yml | changelog.yml |
|------|----------------|----------------|--------------|---------------|
| AI 工具 | Amp CLI | Sourcegraph CRA | Cyclops (external) | AMP codegen |
| 触发方式 | 待填充 | 待填充 | 待填充 | 待填充 |
| 安全模型 | 待填充 | 待填充 | 待填充 | 待填充 |
| 参数化 | 待填充 | 待填充 | 待填充 | 待填充 |
| 输出类型 | 待填充 | 待填充 | 待填充 | 待填充 |
| 容错设计 | 待填充 | 待填充 | 待填充 | 待填充 |

### tempo vs zones Workflow 覆盖矩阵

| 类别 | tempo Workflow | zones 对应 | 差异说明 |
|------|--------------|-----------|---------|
| AI 驱动 | update-reth, amp-review, pr-audit | pr-audit (reusable) | zones 无 AI review/upstream sync |
| Release | release (+SLSA/GPG/SBOM) | release (简化) | zones 无加密签名链 |
| Benchmark | bench 全系列 (6 files) | 无 | zones 完全缺失 benchmark |
| CI/Testing | lint (8 checks), test (6 jobs) | lint (3 checks), test (1 job) | zones 大幅简化 |
| Docker | docker + docker-profiling | docker + docker-profiling | zones 仅 ghcr.io |
| Governance | label-pr, stale, sync, semver | label-pr | zones 缺少多项 |
