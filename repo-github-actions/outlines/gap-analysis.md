---
topic: "Mantle GitHub Actions Gap 分析与优先级排序"
project_slug: repo-github-actions
topic_slug: gap-analysis
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: "repo-github-actions/outlines/gap-analysis.md"
  draft: "repo-github-actions/research-sections/gap-analysis/drafts/round-{n}.md"
  final: "repo-github-actions/research-sections/gap-analysis/final.md"
  index: "repo-github-actions/research-sections/_index.md"

scope: |
  综合 Phase 1 八个项目（Mantle 基线、Tempo、Base、Optimism、paradigmxyz/reth、go-ethereum、
  Solana/Agave、MegaETH）的 GitHub Actions 调研结果，逐维度对比 Mantle 与参考项目，识别差距，
  对每个 gap 进行三维评分（业务影响 + 紧迫度 + 实施可行性），输出优先级排序和分阶段改进路线图。

audience: |
  Mantle 基础设施与 DevOps 工程师、技术管理者，需要以此报告确定 GitHub Actions 改进的优先级、
  资源分配和实施节奏。

expected_output: |
  1. 跨项目维度能力对比矩阵（8 项目 × 10 维度）
  2. Mantle gap 列表（维度、描述、证据引用、三维评分明细、优先级推导、依赖关系）
  3. 优先级排序表（P0/P1/P2，规则：P=业务影响+紧迫度+实施可行性，P≥12→P0，8≤P<12→P1，P<8→P2）
  4. 分阶段改进路线图（尊重 gap 间依赖顺序）

source_data: |
  所有数据来源于 Phase 1 已完成的 8 个 final.md 研究报告，均位于
  repo-github-actions/research-sections/{topic-slug}/final.md：
  - mantle-baseline: Mantle 5 仓库 53 工作流基线
  - tempo: Tempo 29+9 工作流（AI 驱动上游同步、多层加密发布）
  - base: Base 26 工作流（Claude LLM Gateway AI 审查、harden-runner）
  - optimism: Optimism GHA+CircleCI 双轨（Docker 工厂、SLSA）
  - paradigm-reth: paradigmxyz/reth 30 工作流（3 层 benchmark、可重现构建）
  - go-ethereum: go-ethereum 3 工作流（build/ci.go 统一构建程序）
  - solana-agave: Solana/Agave 11 工作流（GHA+Buildkite 混合、完整发布链）
  - megaeth: MegaETH 8+5 工作流（5-job claude.yml AI 集成）

revision_metadata:
  created_by: deep-research-agent
  created_at: "2026-06-11T08:00:00Z"
  last_modified_by: deep-research-agent
  last_modified_at: "2026-06-11T09:00:00Z"
---

# Research Outline: Mantle GitHub Actions Gap 分析与优先级排序

## Source-to-Canonical Dimension Crosswalk

Phase 1 的 8 份研究报告使用了不同的原生维度分类体系。4 份报告（Mantle baseline、Tempo、Base、go-ethereum）直接使用 D1-D10 标准维度命名；另外 4 份（Optimism、paradigmxyz/reth、Solana/Agave、MegaETH）使用各自的原生维度体系。在构建 8×10 对比矩阵前，必须先建立原生维度到标准 D1-D10 的映射关系。

**标准维度定义**：

| 维度编号 | 标准维度名称 | 评判标准摘要 |
|---------|------------|------------|
| D1 | Upstream Auto-Sync | 自动化上游 fork merge/rebase 工作流，同步频率与冲突处理 |
| D2 | AI Code Review | AI 驱动的 PR 审查（Claude、Copilot 等），配置深度与覆盖度 |
| D3 | PR Audit | 自动化 PR 格式/内容/合规验证 |
| D4 | Interactive Agent | 评论触发的 AI Agent（@claude 等），交互式任务执行 |
| D5 | Release Pipeline | Docker 构建/发布、制品签名、SLSA/SBOM 证书、变更日志 |
| D6 | CI/Testing | 构建验证、单元/集成/E2E 测试、矩阵策略 |
| D7 | Security & Supply Chain | 依赖扫描、SAST、supply chain 加固（pinned actions、harden-runner） |
| D8 | Benchmark/Performance | 性能基准测试、回归检测、趋势追踪 |
| D9 | PR Governance | Stale PR 管理、CODEOWNERS 强制、合并策略、分支保护 |
| D10 | Documentation & Infra | 文档部署、链接检查、GitHub Pages、基础设施自动化 |

### 原生维度直接对齐的报告（4/8）

以下报告的能力矩阵直接使用 D1-D10 标准名称，可逐行对照引用：

| 报告 | 矩阵位置 | 原生维度命名 | 对齐说明 |
|------|---------|------------|---------|
| **Mantle baseline** | `mantle-baseline/final.md:788-809` | D1-D10 标准名称 | 完全对齐，5 仓库×10 维度 |
| **Tempo** | `tempo/final.md:1886-1901` | D1-D10 标准名称 | 完全对齐 |
| **Base** | `base/final.md:1045-1058` | D1-D10 标准名称（编号 1-10） | 完全对齐 |
| **go-ethereum** | `go-ethereum/final.md:494-505` | D1-D10 标准名称（编号 1-10） | 完全对齐 |

### 需要映射的报告（4/8）

以下报告使用各自原生维度体系，需要逐条映射到 D1-D10。

#### Optimism（`optimism/final.md:702-724`）

Optimism 采用 GHA+CircleCI 双轨架构，其原生维度侧重构建/部署管线分工，无 AI/上游同步等维度。

| 原生维度 | → 标准维度 | 映射理由 |
|---------|-----------|---------|
| 1. Build & Compile | → D6 CI/Testing | 构建编译属于 CI 核心环节 |
| 2. Unit/Integration Testing | → D6 CI/Testing | 测试属于 CI |
| 3. Contract Testing & FV | → D6 CI/Testing | 合约测试是特化的测试维度 |
| 4. Docker Image Management | → D5 Release Pipeline | Docker 镜像管理是发布流水线的子集 |
| 5. Supply Chain Security | → D7 Security & Supply Chain | 直接对应 |
| 6. Release & Deployment | → D5 Release Pipeline | 直接对应 |
| 7. Dependency Management | → D7 Security & Supply Chain | 依赖管理属于供应链安全范畴 |
| 8. Code Quality & Linting | → D6 CI/Testing | 代码质量检查是 CI 环节 |
| 9. Scheduled/Maintenance Tasks | → D10 Documentation & Infra | 定时维护任务属于基础设施自动化 |
| 10. Path-based Gating | → D6 CI/Testing | 路径过滤是 CI 优化策略 |
| N/A | D1 Upstream Auto-Sync | Optimism 是 OP Stack 源头，不需要上游同步（标记 N/A-源头项目） |
| N/A | D2 AI Code Review | 报告中未涉及 AI 审查能力 |
| N/A | D3 PR Audit | 报告中未独立评估 PR 审计 |
| N/A | D4 Interactive Agent | 报告中未涉及交互式 Agent |
| N/A | D8 Benchmark/Performance | 报告中未独立评估性能基准 |
| N/A | D9 PR Governance | 报告中未独立评估 PR 治理 |

**Optimism 特殊说明**：Optimism 原生矩阵覆盖 D5/D6/D7/D10 子集较深（D6 有 4 个原生维度映射），但 D1-D4/D8/D9 在原生矩阵中无直接对应。对于未覆盖维度，需从报告的非矩阵章节（如工作流清单、配置分析）补充提取证据，无法提取时标记 "N/A — 源头项目/报告未评估"。

#### paradigmxyz/reth（`paradigm-reth/final.md:711-724`）

paradigmxyz/reth 原生维度侧重工程工具链深度，引入了可复现构建、监控可观测性等非标准维度。

| 原生维度 | → 标准维度 | 映射理由 |
|---------|-----------|---------|
| 1. 基准测试系统 | → D8 Benchmark/Performance | 直接对应 |
| 2. 可复现构建 | → D5 Release Pipeline | 可复现构建是发布流水线的质量保障环节 |
| 3. 发布管线 | → D5 Release Pipeline | 直接对应 |
| 4. CI/测试 | → D6 CI/Testing | 直接对应 |
| 5. 安全与供应链 | → D7 Security & Supply Chain | 直接对应 |
| 6. 上游兼容性 | → D1 Upstream Auto-Sync | 语义近似：上游兼容性检测属于上游同步范畴 |
| 7. PR 治理 | → D9 PR Governance | 直接对应 |
| 8. 文档管线 | → D10 Documentation & Infra | 直接对应 |
| 9. 监控与可观测性 | → D10 Documentation & Infra (辅) / D8 (辅) | 监控主要服务于 benchmark 可视化和基础设施 |
| 10. 依赖管理 | → D7 Security & Supply Chain | 依赖管理属于供应链安全范畴 |
| N/A | D2 AI Code Review | 报告确认无 AI 审查工作流 |
| N/A | D3 PR Audit | 无独立 PR 审计维度（PR 治理部分涵盖 Conventional Commits） |
| N/A | D4 Interactive Agent | 无交互式 Agent |

#### Solana/Agave（`solana-agave/final.md:590-640`）

Solana/Agave 原生维度侧重发布自动化和外部 CI 集成，反映其 GHA+Buildkite 混合架构。

| 原生维度 | → 标准维度 | 映射理由 |
|---------|-----------|---------|
| 1. Release Automation | → D5 Release Pipeline | 直接对应 |
| 2. Version Management | → D5 Release Pipeline | 版本管理是发布流水线的子环节 |
| 3. CI Build Optimization | → D6 CI/Testing | CI 构建优化是测试/CI 的子环节 |
| 4. Dependency Management | → D7 Security & Supply Chain | 依赖管理属于供应链安全 |
| 5. Branch Protection | → D9 PR Governance | 分支保护属于 PR/合并治理 |
| 6. Code Quality Gates | → D6 CI/Testing | 代码质量门控是 CI 环节 |
| 7. Documentation Pipeline | → D10 Documentation & Infra | 直接对应 |
| 8. Performance Tracking | → D8 Benchmark/Performance | 直接对应 |
| 9. Issue/PR Lifecycle | → D9 PR Governance | PR 生命周期管理属于治理 |
| 10. External CI Integration | → D6 CI/Testing | 外部 CI 集成是 CI 策略的组成部分 |
| N/A | D1 Upstream Auto-Sync | Agave 是 Solana 验证器源头，不需要上游同步（标记 N/A-源头项目） |
| N/A | D2 AI Code Review | 报告中未涉及 AI 审查 |
| N/A | D3 PR Audit | 无独立 PR 审计维度 |
| N/A | D4 Interactive Agent | 无交互式 Agent |

#### MegaETH（`megaeth/final.md:497-511`）

MegaETH 原生维度细化了构建/测试/覆盖率，并突出 AI 辅助审查和文档质量。

| 原生维度 | → 标准维度 | 映射理由 |
|---------|-----------|---------|
| 1. Build & Lint | → D6 CI/Testing | 构建和 lint 属于 CI |
| 2. Testing | → D6 CI/Testing | 直接对应 |
| 3. Code Coverage | → D6 CI/Testing | 覆盖率是测试的度量维度 |
| 4. AI-Assisted Review | → D2 AI Code Review + D4 Interactive Agent | MegaETH claude.yml 同时覆盖 PR review 和交互式 Agent（pr-review job → D2, 其余 4 jobs → D4） |
| 5. Documentation Quality | → D10 Documentation & Infra | 文档质量属于文档/基础设施 |
| 6. Release Management | → D5 Release Pipeline | 直接对应 |
| 7. Branch Protection | → D9 PR Governance | 直接对应 |
| 8. Dependency Management | → D7 Security & Supply Chain | 依赖管理属于供应链安全（MegaETH 此项为 missing） |
| 9. Security Scanning | → D7 Security & Supply Chain | 直接对应 |
| 10. Performance Benchmark | → D8 Benchmark/Performance | 直接对应 |
| N/A | D1 Upstream Auto-Sync | 报告中未涉及上游同步（MegaETH 非 fork 项目） |
| N/A | D3 PR Audit | 无独立 PR 审计维度 |

### Crosswalk 使用规则

1. **矩阵每个单元格**必须标注其证据来源：若来自原生维度直接对齐，引用 `{final.md} § {原生维度名}`；若来自 crosswalk 映射，引用 `{final.md} § {原生维度名} → D{n}`
2. **多对一映射**（如 Optimism 4 个原生维度映射到 D6）：取相关原生维度中的最高评级作为 D6 代表值，并在证据摘要中列出所有映射维度
3. **一对多映射**（如 MegaETH AI-Assisted Review → D2 + D4）：基于原生报告中的详细描述拆分评级
4. **N/A 标记**：源头项目（go-ethereum for D1, Optimism for D1, Solana/Agave for D1）在 D1 标记 "N/A — 源头项目"，不计入差距分析的参考基准组；报告未评估的维度标记 "N/A — 未评估"，同样不计入参考组
5. **差距分析参考基准**：每个维度的参考基准组仅包含非 N/A 项目。如 D1 的参考基准组为 Mantle/Tempo/Base/paradigmxyz-reth/MegaETH（5 个），排除 go-ethereum/Optimism/Solana-Agave（3 个源头项目）

---

## Items

### item-1: 跨项目维度能力对比矩阵（8×10）

基于上方 crosswalk 表，从 8 个 Phase 1 研究报告中提取每个项目在 10 个标准维度上的能力评级，构建统一的跨项目对比矩阵。对于使用非标准维度的 4 份报告（Optimism、paradigmxyz/reth、Solana/Agave、MegaETH），严格按 crosswalk 映射关系提取并标注证据来源。每个单元格使用三级评级体系（成熟/基础/缺失）或 N/A 标记。

**各项目基线能力速览**（从 Phase 1 研究报告提取，将在 draft 中逐维度展开证据）：

| 项目 | 成熟 | 基础 | 缺失 | 工作流总数 | 主要架构特点 |
|------|------|------|------|-----------|------------|
| Mantle (5 仓库) | ~4 | ~3 | ~3 | 53 | 跨 5 仓库差异大，仅 kona 有 AI |
| Tempo | 5 | 5 | 0 | 29+9 | AI 驱动上游同步，多层加密发布 |
| Base | 6 | 2 | 2 | 26 | LLM Gateway AI 审查，harden-runner 全覆盖 |
| Optimism | 8 | 2 | 0 | GHA+CircleCI | Docker 工厂模式，SLSA，双轨 CI |
| paradigmxyz/reth | 5 | 3 | 2 | 30 | 3 层 benchmark，可重现构建 |
| go-ethereum | 3 | 2 | 5 | 3 | build/ci.go 统一构建，极简 GHA |
| Solana/Agave | 7 | 3 | 0 | 11 | GHA+Buildkite 混合，9 条 ruleset |
| MegaETH | 4 | 3 | 3 | 8+5 | 5-job AI 集成，Criterion benchmark |

**构建规则**：
- 每个单元格（项目×维度）必须引用对应 final.md 中的具体章节或数据点，并按 crosswalk 表标注映射来源
- 对于直接对齐的报告（Mantle baseline/Tempo/Base/go-ethereum），直接引用原生维度评级
- 对于需要映射的报告（Optimism/paradigmxyz-reth/Solana-Agave/MegaETH），引用原生维度名并标注 `→ D{n}` 映射路径
- 多对一映射取最高评级；一对多映射基于报告详细描述拆分
- N/A 单元格（源头项目无上游同步需求、报告未评估的维度）不计入参考基准组
- 对于 Mantle 基线，以 5 仓库中的最高能力为该维度代表值，同时标注仓库间差异
- 多仓库项目（Base 3 仓库、MegaETH 2 仓库）同理取最高值
- go-ethereum 的 build/ci.go 统一构建模式需注明其 GHA 工作流数量极少但功能等价的特殊情况

- **Priority**: high
- **Dependencies**: none

### item-2: Mantle Gap 识别与证据归集

基于 item-1 的对比矩阵，逐维度识别 Mantle 相对于参考项目组最佳实践的差距。每个 gap 必须包含：维度归属、差距描述、Mantle 现状证据（引用 mantle-baseline/final.md）、参考项目最佳实践证据（引用对应 final.md）、差距程度评估。

**预期 gap 维度覆盖**（基于 Phase 1 研究速览）：

| 维度 | Mantle 现状 | 最佳参考 | 预期 gap |
|------|-----------|---------|---------|
| D1 Upstream Auto-Sync | 仅 kona 有 sync.yaml 每 7 天自动同步 (基础)；reth 的 sync.yml/sync-era.yml 是链同步测试而非上游 fork 同步 (缺失)；其余 3 仓库缺失 (`mantle-baseline/final.md:794,817-818`) | Tempo update-reth.yml (680 行，3 层 AI 修复循环) | 从手动/半自动升级为 AI 驱动自动同步 |
| D2 AI Code Review | 仅 kona 有 claude-code-review.yml | Base Claude + LLM Gateway 代理 + 出口封锁模式 | AI 审查扩展到全部仓库，引入网关代理架构 |
| D3 PR Audit | reth pr-title.yml, op-geth validate_pr | Solana/Agave 9 条 ruleset + 双路径授权 | 统一 PR 验证规范，引入 ruleset 体系 |
| D4 Interactive Agent | 仅 kona 有 claude.yml | MegaETH 5-job AI（review+doc-impact+label+triage），Tempo comment-driven benchmark | 交互 Agent 扩展到核心仓库 |
| D5 Release Pipeline | reth 有完整流水线，其余仓库碎片化 | Tempo 多层加密发布（GPG+SLSA+SBOM+cosign），Base 3 阶段发布 | 统一发布标准，引入 SLSA/SBOM 证书 |
| D6 CI/Testing | reth/kona/mantle-v2 成熟，op-geth/op-succinct 基础 | Optimism CircleCI 全覆盖，paradigmxyz/reth 高级测试策略 | 补齐低覆盖仓库，统一测试标准 |
| D7 Security & Supply Chain | mantle-v2 有 semgrep，kona 有 cargo-deny，其余弱 | Base harden-runner 25/26 覆盖 + Vouch，Solana 全维度 Dependabot | 全仓库 harden-runner，统一 Dependabot |
| D8 Benchmark/Performance | reth bench.yml (基础)，kona proof (基础) | paradigmxyz/reth 3 层 benchmark (ABBA+ClickHouse)，Tempo 50+ 参数 | 引入系统化 benchmark 框架 |
| D9 PR Governance | 分散的 stale/label/pr-title | Solana/Agave 9 条 ruleset 无旁路 | 集中化分支保护与 ruleset |
| D10 Documentation & Infra | reth book.yml (基础) | paradigmxyz/reth 可重现构建 + book.yml，Optimism Docker 工厂 | 文档自动化与基础设施标准化 |

**Gap 记录格式**：

每个 gap 条目须包含：
1. **Gap ID**: `GAP-D{n}-{seq}`（如 `GAP-D1-01`）
2. **维度**: D1–D10
3. **差距标题**: 一句话描述
4. **Mantle 现状**: 引用 mantle-baseline/final.md 具体章节
5. **最佳参考实践**: 引用参考项目 final.md 具体章节，说明参考项目做到什么程度
6. **差距程度**: 完全缺失 / 功能性差距 / 成熟度差距
7. **影响范围**: 受影响的 Mantle 仓库列表

- **Priority**: high
- **Dependencies**: item-1

### item-3: 三维评分方法论与 Gap 评分

定义并应用三维评分体系（业务影响 + 紧迫度 + 实施可行性），对 item-2 识别的每个 gap 进行量化评分，推导优先级等级。

**三维评分框架**：

| 维度 | 分值范围 | 5 分标准 | 3 分标准 | 1 分标准 |
|------|---------|---------|---------|---------|
| 业务影响 (Business Impact) | 1–5 | 直接影响生产安全或合规，阻碍产品发布 | 影响开发效率或代码质量，但不阻碍发布 | 仅影响开发者体验或内部流程美观度 |
| 紧迫度 (Urgency) | 1–5 | 安全漏洞已暴露或合规期限临近（<1个月） | 明确的路线图需求或行业标准要求（1-3个月） | 属于长期改进或锦上添花（>6个月无压力） |
| 实施可行性 (Feasibility) | 1–5 | 有现成参考实现可直接复用，<1 周实施 | 需适配但技术路径清晰，2-4 周实施 | 需要基础设施改造或外部依赖，>2个月 |

**优先级推导规则**：

```
P = 业务影响 + 紧迫度 + 实施可行性
P ≥ 12 → P0（立即行动）
8 ≤ P < 12 → P1（短期规划）
P < 8 → P2（中长期储备）
```

**评分约束**：
- 每个分值必须附带 1-2 句评分理由
- 实施可行性评分需引用参考项目的实现复杂度作为估算依据
- 同一维度下的多个 gap 可能有不同评分（如 D7 的 harden-runner 和 Dependabot 可行性不同）
- 评分理由中须标注哪些参考项目的实现可直接移植、哪些需要定制

**评分结果表格式**：

| Gap ID | 维度 | 标题 | 业务影响 | 紧迫度 | 可行性 | P 值 | 优先级 |
|--------|------|------|---------|--------|--------|------|--------|
| GAP-D{n}-{seq} | D{n} | ... | {1-5} ({理由}) | {1-5} ({理由}) | {1-5} ({理由}) | {sum} | P0/P1/P2 |

- **Priority**: high
- **Dependencies**: item-2

### item-4: Gap 间依赖关系映射

分析各 gap 之间的实施依赖关系，识别前置条件和并行机会，为路线图编排提供拓扑约束。

**依赖关系类型**：

| 类型 | 描述 | 示例 |
|------|------|------|
| 技术前置 (hard) | A 的实施在技术上必须先于 B | 统一 Dependabot 配置 → 才能启用自动化安全 PR 审查 |
| 基础设施前置 (hard) | A 提供 B 所需的基础设施 | 自托管 runner 标准化 → 才能部署 benchmark 框架 |
| 经验积累 (soft) | A 的经验降低 B 的实施风险 | 单仓库 AI 审查试点 → 全仓库 AI 审查推广 |
| 资源复用 (soft) | A 和 B 共享实施资源，串行更高效 | 同一维度的多个 gap 由同一团队实施 |

**分析方法**：
1. 对每个 gap 检查其实施是否依赖其他 gap 的产出
2. 识别共享基础设施依赖（如 self-hosted runner、secret 管理、GitHub App 配置）
3. 识别跨仓库推广的渐进依赖（pilot → rollout 模式）
4. 构建有向无环图 (DAG)，识别关键路径和并行组

**依赖矩阵格式**：

| Gap ID | 硬依赖 (blocks) | 软依赖 (benefits from) | 被依赖 (blocked by) |
|--------|----------------|----------------------|-------------------|
| GAP-D{n}-{seq} | [...] | [...] | [...] |

**关键依赖假设**（基于 Phase 1 研究预判，须在 draft 中验证）：
- Mantle 的 5 仓库异构性意味着大多数改进需要 pilot-then-rollout 模式
- kona 作为唯一已集成 AI 的仓库，可能是多项改进的天然试点目标
- reth 作为工作流最多（29 个）的仓库，其改造复杂度最高
- 安全类 gap（D7）通常是其他改进的前置条件（供应链安全 → 可信发布 → 可信 AI 审查）

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: 分阶段改进路线图

基于 item-3 的优先级排序和 item-4 的依赖图谱，编排分阶段改进路线图。路线图须尊重 gap 间的依赖顺序，在每个阶段内最大化并行度，并为每个阶段定义可验证的完成标准。

**路线图结构**：

| 阶段 | 时间窗口 | 优先级范围 | 选取原则 |
|------|---------|-----------|---------|
| Phase 1: 立即行动 | 0-4 周 | P0 gap + 无前置依赖 | 高 P 值 + 依赖图入度为 0 |
| Phase 2: 短期规划 | 5-12 周 | P0 剩余 + P1 高优 | Phase 1 解锁的 gap + 高 P 值 P1 |
| Phase 3: 中期建设 | 13-24 周 | P1 剩余 + P2 高优 | 系统性改造项 + 需要基础设施投入 |
| Phase 4: 长期优化 | 25+ 周 | P2 | 锦上添花 + 前沿探索 |

**每个阶段须包含**：
1. 纳入的 Gap ID 列表及排序
2. 并行实施分组（哪些 gap 可同时推进）
3. 里程碑定义（可验证的完成标准）
4. 所需资源估算（人力、基础设施、第三方服务）
5. 风险与缓解措施
6. 上一阶段的完成是下一阶段启动的前提条件清单

**路线图设计约束**：
- 须体现 pilot-then-rollout 的渐进模式：先在 kona/reth 试点，再推广至全部 5 仓库
- 跨仓库标准化改进（如统一 Dependabot、统一 harden-runner）可在确认模板后批量部署
- 需考虑 Mantle 团队现有的运维带宽（避免单阶段过载）
- 每个阶段至少有一个"速赢"项（实施简单但改进可见）提振团队信心

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: 执行摘要与决策建议

综合前述分析，提炼面向决策层的执行摘要，突出 Top 3 优先行动、预期收益和所需投入，为技术管理者提供决策依据。

**执行摘要结构**：
1. **现状总结**: Mantle 在 10 维度中的总体定位（相对于 7 个参考项目的百分位）
2. **核心发现**: 最关键的 3-5 个洞察
3. **Top 3 优先行动**: 从 P0 gap 中提炼最高 ROI 的 3 项具体行动
4. **预期收益**: 量化或定性描述每项行动的预期效果
5. **投入估算**: 人力、时间、基础设施成本
6. **风险与依赖**: 影响路线图执行的外部因素

- **Priority**: medium
- **Dependencies**: item-1, item-3, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| project_capability_rating | 每个项目在单一维度上的能力评级（成熟/基础/缺失），附证据引用 | item-1 |
| capability_matrix_cell | 矩阵单元格：项目名×维度→评级+关键证据摘要+来源 final.md 路径 | item-1 |
| gap_record | 完整 gap 记录：ID、维度、标题、Mantle 现状、参考最佳实践、差距程度、影响仓库 | item-2 |
| gap_evidence_ref | 指向 Phase 1 final.md 的具体章节引用（文件路径+章节标题+关键数据点） | item-2 |
| scoring_rubric_entry | 三维评分条目：Gap ID、各维度分值(1-5)、评分理由、P 值、优先级 | item-3 |
| dependency_edge | 依赖关系边：源 Gap ID → 目标 Gap ID、依赖类型（hard/soft）、理由 | item-4 |
| roadmap_phase | 阶段定义：编号、时间窗口、纳入 Gap 列表、并行分组、里程碑、资源估算 | item-5 |
| executive_action_item | 决策建议条目：优先行动、预期收益、投入估算、风险 | item-6 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | heatmap | 8 项目 × 10 维度能力热力矩阵，使用 成熟(绿)/基础(黄)/缺失(红) 三色编码，Mantle 行加粗突出 | ascii | item-1 |
| diag-2 | comparison | Mantle gap 雷达图/维度对比图，展示 Mantle 在各维度与参考组最佳值的差距 | ascii | item-2 |
| diag-3 | dag | Gap 间依赖关系有向无环图，节点标注 Gap ID + 优先级，边标注依赖类型(hard/soft)，关键路径高亮 | mermaid | item-4 |
| diag-4 | timeline | 分阶段路线图甘特图，展示各阶段时间窗口、gap 分配和并行分组 | mermaid | item-5 |
| diag-5 | quadrant | P0/P1/P2 gap 的业务影响-可行性四象限图，帮助决策者直观理解优先级分布 | ascii | item-3, item-6 |

## Source Requirements

所有数据来源于 Phase 1 已完成的 8 份研究报告。本 gap 分析不需要额外的代码分析或外部数据采集，全部基于已有研究成果进行综合分析。

| ID | Type | Description | Source Path | Min References |
|----|------|-------------|-------------|----------------|
| src-1 | research_synthesis | Mantle 基线研究报告 — 5 仓库 53 工作流全量数据 | repo-github-actions/research-sections/mantle-baseline/final.md | 10（每维度至少 1 条证据） |
| src-2 | research_synthesis | Tempo 研究报告 — AI 上游同步、多层发布、comment benchmark | repo-github-actions/research-sections/tempo/final.md | 5 |
| src-3 | research_synthesis | Base 研究报告 — LLM Gateway AI 审查、harden-runner、Vouch | repo-github-actions/research-sections/base/final.md | 5 |
| src-4 | research_synthesis | Optimism 研究报告 — GHA+CircleCI 双轨、Docker 工厂、SLSA | repo-github-actions/research-sections/optimism/final.md | 5 |
| src-5 | research_synthesis | paradigmxyz/reth 研究报告 — 3 层 benchmark、可重现构建 | repo-github-actions/research-sections/paradigm-reth/final.md | 5 |
| src-6 | research_synthesis | go-ethereum 研究报告 — build/ci.go 统一构建 | repo-github-actions/research-sections/go-ethereum/final.md | 3 |
| src-7 | research_synthesis | Solana/Agave 研究报告 — GHA+Buildkite 混合、9 条 ruleset | repo-github-actions/research-sections/solana-agave/final.md | 5 |
| src-8 | research_synthesis | MegaETH 研究报告 — 5-job AI 集成、Criterion benchmark | repo-github-actions/research-sections/megaeth/final.md | 3 |

**总计最低引用数**: 41 条跨报告证据引用

**引用格式规范**: 每条引用须标明 `{final.md 路径} § {章节标题}` 并附关键数据点（如工作流名、行数、覆盖率等具体数值）。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | add_section | Source-to-Canonical Dimension Crosswalk | [MAJOR] 4/8 Phase 1 报告（Optimism、paradigmxyz/reth、Solana/Agave、MegaETH）使用非标准维度体系。新增完整的原生维度→D1-D10 映射表，包含映射理由、N/A 规则和多对一/一对多处理规范。确保矩阵每个单元格可追溯到源报告具体章节。 | adversarial-review-round-1 via Orchestrator |
| 2 | modify_item | item-2 (D1 seed evidence) | [MAJOR] Mantle baseline 明确将 reth 的 D1 评为"缺失"（sync.yml/sync-era.yml 是链同步测试，不是上游 fork 合并），仅 kona 为"基础"。修正 item-2 预期 gap 表中的 D1 行，移除错误的 reth "基础"引用，使用 kona 作为唯一"基础"参考，并引用 mantle-baseline/final.md:794,817-818 作为证据。 | adversarial-review-round-1 via Orchestrator |
| 2 | modify_item | item-1 (construction rules) | [MINOR] 更新构建规则，新增 crosswalk 映射来源标注要求和 N/A 处理规则。 | 配合 crosswalk 新增 |
| 2 | modify_checklist | Quality Checklist | [MINOR] 新增 4 项 crosswalk 相关检查项。 | 配合 crosswalk 新增 |

## Quality Checklist

- [ ] Crosswalk 表完整覆盖 4 份非标准报告的全部原生维度，每条映射有理由
- [ ] 每个矩阵单元格（80 个：8 项目×10 维度）都有证据支撑的评级或 N/A 标记
- [ ] 使用 crosswalk 映射的单元格标注了 `原生维度名 → D{n}` 映射路径
- [ ] N/A 单元格（源头项目等）未被纳入差距分析的参考基准组
- [ ] 每个 Mantle "缺失"或"基础"维度都有对应的 gap 记录
- [ ] 每个 gap 都有完整的三维评分和优先级推导
- [ ] 依赖图是有向无环图（无循环依赖）
- [ ] 路线图尊重依赖顺序（无 gap 在其前置依赖完成前被安排）
- [ ] 路线图每个阶段有可验证的完成标准
- [ ] 全部 5 张图表都已生成且数据与正文一致
- [ ] 引用总数 ≥ 41 且覆盖全部 8 份研究报告
