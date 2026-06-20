# Research Outline: Beryl vs Azul 变更范围界定与 commit/PR 清单梳理

## Metadata

| Field | Value |
|-------|-------|
| project_slug | `base-beryl-vs-azul` |
| topic_slug | `beryl-scope-inventory` |
| multica_issue_id | `39fb2d70-49f6-4ca5-8b4f-90509cb703fe` |
| round | 3 |
| github_repo | `Whisker17/multica-research` |
| outline_path | `base-beryl-vs-azul/outlines/beryl-scope-inventory.md` |
| draft_path | `base-beryl-vs-azul/research-sections/beryl-scope-inventory/drafts/round-1.md` |
| final_path | `base-beryl-vs-azul/research-sections/beryl-scope-inventory/final.md` |

## Topic

Beryl vs Azul 变更范围界定与 commit/PR 清单梳理 — 为整个 "Base Beryl vs Azul" 研究项目建立权威证据基线。

## Scope

以「官方 docs + release tag + PR/commit」三重证据界定 Beryl 相对 Azul 的完整官方 scope 与代码变更范围，产出可被后续所有 issue 引用的清单与分类，并排除 Cobalt-only 变更。

### In-Scope

- 官方 Beryl scope 三大块的确认与代码锚定
- v1.0.1 (Azul) → v1.1.0 (Beryl sepolia) → v1.1.1 (Beryl mainnet) 所有非合并 commit 的分类
- PR/commit 清单表构建
- 变更域 taxonomy 定义
- Cobalt-only 变更的识别与排除
- `base/node` required software 版本确认

### Out-of-Scope

- 深度机制分析（留给下游 issue WHI-246 ~ WHI-251）
- Azul 升级本身的分析（已有 `base-azul-upgrade/` 研究，本 issue 仅引用）
- Cobalt 功能的详细分析
- L1 合约变更的深层分析（withdrawal 7→5 天的 L1 DisputeGameFactory 参数变更不在 base/base 代码库中，但本研究须在 taxonomy 中显式建模此 scope 的证据边界）

## Code Baseline

| Network | Release Tag | Commit (解引用 `^{}`) | 用途 |
|---------|------------|----------------------|------|
| Mainnet | `v1.1.1` | `01e732cdbae0c624d652da9e608d7d3fe0f9c74b` | 主网上线版本，本研究主基线 |
| Sepolia | `v1.1.0` | `a3c3011b16dae73aaea455ec0a5ff614e65b7d0a` | Sepolia 上线版本，Beryl 功能完整集 |
| Azul (上一版) | `v1.0.1` | `955a18b189196c6f663235140180e5bcf51cd044` | Diff 起点 |

**Commit 统计**（精确值，命令：`git log v1.0.1^{}..v1.1.1^{} --oneline --no-merges | wc -l`）：
- v1.0.1→v1.1.1：**143 个非合并 commit**
- v1.1.0→v1.1.1：**3 个非合并 commit**（mainnet 激活时间戳 #3627、版本号 #3624、backport #3634）
- Beryl 功能代码主体在 v1.0.1→v1.1.0 区间（140 个 commit）。

### Key Timestamps (已核实)

| Network | Timestamp | Date |
|---------|-----------|------|
| Mainnet | `1782410400` | 2026-06-25 18:00 UTC |
| Sepolia | `1781805600` | 2026-06-18 18:00 UTC |
| Zeronet | `1780678800` | 2026-06-05 17:00 UTC |

## Research Items

### Item 1: 官方 Beryl Scope 三大块确认

**Slug**: `official-scope-confirmation`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `b20_scope` | B20 原生 token 标准的官方定义与功能边界：ERC-20 compatible Rust precompiles, Asset/Stablecoin 两个 variant, PolicyRegistry, ActivationRegistry, B20Factory | 官方 docs `overview.mdx` + `b20.mdx`；代码 `crates/common/precompiles/src/` |
| `withdrawal_scope` | single-proof 提款最终确认 7→5 天的变更定义；dual-proof TEE+ZK 快路径仍为 1 天不变。**证据边界**：`git log v1.0.1^{}..v1.1.1^{} --no-merges --grep='withdraw\|dispute.*game\|finalization'` 返回零结果 — base/base EL 代码库无直接实现；变更完全在 L1 合约层（DisputeGameFactory finalization window 参数），权威证据来源为官方 docs + L1 链上交易 | 官方 docs `overview.mdx` L43-46；docs.base.org Beryl overview 页面 |
| `reth_v2_scope` | Reth V2 的升级定义：最高 −50% 磁盘、状态根 pipeline +33% 吞吐 | 官方 docs `overview.mdx` L10；`Cargo.toml` reth 依赖版本 v2.3.0；backport commit `572a3c564` (#3471) |
| `scope_completeness_check` | 三大块是否覆盖所有官方公告的 Beryl 变更；是否存在遗漏的第四块 | 官方 docs + status.base.org；与 `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` 交叉验证 |

**Acceptance Criteria**:
- 每个 scope 块须引用官方 docs 原文 + 对应代码路径（tag + commit + file path）
- 明确标注 withdrawal 7→5 天在 base/base 中的代码表现（如果有）与 L1 合约的关系

### Item 2: PR/Commit 清单表

**Slug**: `pr-commit-inventory`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `commit_enumeration` | v1.0.1^{}..v1.1.1^{} 全部 143 个非合并 commit 枚举，含 PR 号提取 | `git log v1.0.1^{}..v1.1.1^{} --oneline --no-merges` |
| `pr_classification` | 每个 PR 按变更域分类：B20-Token-Core / B20-Factory / B20-Asset / B20-Stablecoin / PolicyRegistry / ActivationRegistry / Precompile-Infra / Withdrawal-Finality / Protocol-RethV2 / EVM-Integration / Activation-Governance / EIP-8130 / Prover-Service / Test-Infra / CI-Tooling（共 15 个域，与 taxonomy 表对齐） | Commit message + 变更文件路径分析 |
| `audit_ticket_mapping` | 标注 BOP-xxx / PSRC-xxx 审计票据（约 30 个 commit 引用了 BOP/PSRC） | Commit message grep `BOP-\|PSRC-` |
| `key_files_per_pr` | 每个 PR 的关键变更文件路径（不超过 3 个最重要的） | `git diff --stat` per commit |
| `tag_attribution` | 每个 commit 属于 v1.1.0 还是 v1.1.1（v1.1.0→v1.1.1 仅 3 commit） | Commit 范围比对 |

**Output Format** (draft 中的表格):

```
| PR# | 标题 | 变更域 | 审计票据 | 关键文件 | Tag 归属 |
|-----|------|--------|----------|----------|----------|
| #NNNN | ... | B20-core | BOP-xxx | path/to/file.rs | v1.1.0 |
```

**Acceptance Criteria**:
- 覆盖 v1.0.1→v1.1.1 所有非合并 commit
- 每行 PR 至少标注一个变更域
- BOP/PSRC 票据号准确对应 commit message
- 无裸 HEAD 引用；文件路径标注 tag

### Item 3: 变更域 Taxonomy

**Slug**: `change-domain-taxonomy`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `taxonomy_definition` | 定义变更域分类体系，与官方三大 scope 可对应 | 官方 docs scope + 代码目录结构 |
| `taxonomy_mapping` | 每个变更域映射到哪个官方 scope 块 | 交叉验证 |
| `boundary_cases` | 跨域变更（如 precompile-storage 同时服务 B20 和 ActivationRegistry）的归类规则 | 代码分析 |

**Proposed Taxonomy (基于代码分析)**:

| 变更域 | 说明 | 对应 Scope | 代码路径模式 |
|--------|------|-----------|-------------|
| **B20-Token-Core** | B20 token 共享逻辑：roles, pause, permit, transfer, burn, mint | B20 | `crates/common/precompiles/src/common/` |
| **B20-Asset** | B20 Asset variant：multiplier, announcements, batch mint, extra metadata | B20 | `crates/common/precompiles/src/b20_asset/` |
| **B20-Stablecoin** | B20 Stablecoin variant：6 decimals, currency code | B20 | `crates/common/precompiles/src/b20_stablecoin/` |
| **B20-Factory** | B20Factory singleton：token creation, address derivation, initCalls | B20 | `crates/common/precompiles/src/b20_factory/` |
| **PolicyRegistry** | Policy registry：blocklist/allowlist, admin model | B20 | `crates/common/precompiles/src/policy/` |
| **ActivationRegistry** | Feature activation registry：Beryl precompile 激活门控 | B20 (激活治理) | `crates/common/precompiles/src/activation/` |
| **Precompile-Infra** | Precompile 基础设施：storage macros, lookup, observer, metrics, gas metering | B20 (基础设施) | `crates/common/precompiles/src/{lookup,observer,metrics,spec,macros}.rs`；`base-precompile-storage` crate |
| **Withdrawal-Finality** | Single-proof 提款最终确认 7→5 天：L1 DisputeGameFactory finalization window 参数变更 | Withdrawal 7→5 | **无 base/base 直接代码变更** — `git log v1.0.1^{}..v1.1.1^{} --no-merges --grep='withdraw\|dispute.*game\|finalization'` 返回零结果。变更完全在 L1 合约层（DisputeGameFactory 参数调整），权威证据来源为官方 docs `overview.mdx` L43-46 + L1 链上交易。本域在 taxonomy 中显式保留以确保三大 scope 完整映射 |
| **Protocol-RethV2** | Reth V2 依赖升级 + 状态根 pipeline 相关 | Reth V2 | `Cargo.toml` reth deps; `crates/execution/`; backport #3471 |
| **EVM-Integration** | EVM spec 映射、handler、Beryl precompile 安装、beryl_metrics | B20 (EVM) | `crates/common/evm/src/{spec,handler,beryl_metrics,lib}.rs` |
| **Activation-Governance** | Fork activation：upgrade enum, chain config, timestamp scheduling, chainspec | Activation | `crates/common/chains/src/`; `crates/execution/chainspec/src/` |
| **EIP-8130** | Account Abstraction tx type 0x7D 保守接受门控 | Protocol | `crates/common/consensus/src/`; txpool #2926 |
| **Prover-Service** | Prover service 重构 (gRPC→JSON-RPC, TEE types, client crate, nitro-host) | Infra (非 Beryl scope) | `crates/proof/` |
| **Test-Infra** | 测试基础设施：system tests, action tests, devnet, load tests | Test | `etc/systems/`; `actions/harness/` |
| **CI-Tooling** | CI/CD, Docker, release 版本号 | Infra | CI files, Dockerfile |

**Acceptance Criteria**:
- Taxonomy 能覆盖全部 143 个非合并 commit
- 每个变更域有明确的代码路径模式和对应 scope 块
- 跨域 commit 有明确归类规则

### Item 4: Cobalt-Only 变更排除

**Slug**: `cobalt-exclusion`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `cobalt_identification` | 识别所有 Cobalt-only 变更的方法论 | `BaseUpgrade::Cobalt` enum entry; `cobalt_timestamp: None` in all chain configs |
| `cobalt_commits` | 具体的 Cobalt-only commit 清单（仅限 v1.0.1^{}..v1.1.1^{} 范围内的 commit） | `git log v1.0.1^{}..v1.1.1^{} --oneline --no-merges --grep='Cobalt\|cobalt'` |
| `cobalt_plumbing_vs_beryl` | 区分 Cobalt plumbing（hardfork enum/config 骨架）与 Cobalt 功能代码 | 代码分析 |
| `cobalt_blame_attribution` | 通过 `git blame` 确认 Cobalt provider 代码在 v1.1.1 中的来源 commit | `git blame` on provider.rs at v1.1.1 |
| `exclusion_evidence` | 排除判定依据：cobalt_timestamp 为 None, Cobalt 条件分支未激活 | `crates/common/chains/src/config.rs` L354, L428, L493 |

**Key Evidence (已收集，仅含 v1.0.1^{}..v1.1.1^{} 范围内 commit)**:
- `ChainConfig::mainnet().cobalt_timestamp == None` (v1.1.1 @ config.rs:354)
- `ChainConfig::sepolia().cobalt_timestamp == None` (v1.1.1 @ config.rs:428)
- `213f13ce1` — `feat(chains): add Cobalt hardfork plumbing (#3119)` — 仅添加 enum variant + config 骨架，在 v1.0.1→v1.1.1 范围内
- `526d5361c` — `backport PSRC precompile fixes to v1.1.0 (#3426)` — 此 backport 包含 Cobalt provider/dispatch 分支代码（通过 `git blame` 归因），在 v1.0.1→v1.1.1 范围内

**Acceptance Criteria**:
- 明确列出所有 Cobalt-only commit
- 每个排除判定附带代码证据（config.rs 中 `cobalt_timestamp: None`）
- 说明 Cobalt plumbing commit 虽然在 Beryl tag 内但不影响 Beryl 运行时行为

### Item 5: 跨库 Required Software 确认

**Slug**: `required-software-confirmation`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `base_base_versions` | base/base release tag 与 binary 版本号确认 | `v1.1.1` (mainnet), `v1.1.0` (sepolia) |
| `base_node_versions` | base/node release tag 确认 | 官方 docs overview.mdx L21-25; `v1.1.1` / `v1.1.0` |
| `reth_upstream_version` | Reth upstream 版本确认 | `Cargo.toml` reth tag = `v2.3.0` |
| `binary_components` | 列出 Beryl 涉及的 binary 组件：base-reth-node (EL), base-consensus (CL), base/node | 官方 docs Required Software 表 |

**Acceptance Criteria**:
- Required Software 表与官方 docs 一致
- Reth V2 版本号与 Cargo.toml 一致
- 明确标注 EL/CL/node 三层组件

## Source Requirements

### Primary Sources

| Source | Type | Access | Notes |
|--------|------|--------|-------|
| `base/base` repo @ v1.1.1 / v1.1.0 | Code | 本地 `/Users/whisker/Work/src/networks/base/base` (已 checkout v1.1.1) | 禁用裸 HEAD 引用 |
| 官方 docs overview.mdx | Docs | 本地 `/Users/whisker/Work/src/networks/base/docs/docs/base-chain/specs/upgrades/beryl/overview.mdx` | Beryl scope 定义 |
| 官方 docs b20.mdx | Docs | 本地同上 `/beryl/b20.mdx` | B20 spec |
| `base/node` releases | Code | GitHub `base/node` v1.1.1 / v1.1.0 | Required software 确认 |

### Secondary Sources

| Source | Type | Access | Notes |
|--------|------|--------|-------|
| `base-azul-upgrade/` 既有研究 | Research | 同仓库 `base-azul-upgrade/research-sections/` | 引用不复述 |
| status.base.org | Web | HTTPS | 激活时间表确认 |
| Reth upstream releases | Web | GitHub `paradigmxyz/reth` v2.3.0 | Reth V2 changelog |

### Source Integrity Rules

1. 所有代码引用必须标注 `tag + commit + file path (+line number)`
2. 禁止裸 HEAD 引用
3. Tag commit 必须使用 `git rev-parse <tag>^{}` 解引用值
4. 引用 `base-azul-upgrade/` 既有研究时仅引用路径和结论，不复述内容

## Diagram Expectations

### Diagram 1: Beryl 变更域 Taxonomy 架构图

**Type**: 分层结构图 (Hierarchy/Tree)
**Content**: 展示三大官方 scope → 变更域 → 代码路径模式的三级映射关系
**Format**: Mermaid flowchart (draft 中内嵌)
**Purpose**: 让下游 issue 快速定位自己关注的变更域

### Diagram 2: Beryl Precompile 地址空间与调用关系

**Type**: 组件关系图
**Content**: B20Factory → B20Asset/B20Stablecoin tokens (dynamic lookup) → PolicyRegistry → ActivationRegistry 的调用关系
**Format**: Mermaid flowchart
**Purpose**: 辅助理解 B20 体系的组件交互

**Note**: 不需要 timeline 图（时间戳已在表格中明确）；不需要 commit 分布图（PR 清单表已覆盖）。

## Expected Output Summary

Draft (`round-1.md`) 应包含：

1. **§1 官方 Scope 确认** — 三大块逐一确认，附官方 docs 引用 + 代码锚点
2. **§2 代码基线与激活参数** — tag/commit/timestamp 表 + chainspec 代码引用
3. **§3 PR/Commit 清单表** — 完整表格（143 行），每行含 PR#、标题、变更域、审计票据、关键文件、tag 归属
4. **§4 变更域 Taxonomy** — taxonomy 定义表 + Mermaid 架构图 + scope 映射
5. **§5 Cobalt-Only 变更排除** — 排除清单 + 判定依据 + 代码证据
6. **§6 Required Software** — EL/CL/node 版本确认表
7. **§7 跨研究引用** — 与 `base-azul-upgrade/` 的关系说明

## Cross-References

| Reference | Path | Relation |
|-----------|------|----------|
| Azul Overview | `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` | Azul scope 基线（引用不复述） |
| Osaka EVM Changes | `base-azul-upgrade/research-sections/osaka-evm-changes/final.md` | Azul 引入的 Osaka EVM spec (Beryl 继承) |
| Multiproof Architecture | `base-azul-upgrade/research-sections/multiproof-architecture/final.md` | Dual-proof TEE+ZK 快路径（withdrawal scope 背景） |
| Downstream: WHI-246 | B20 原生 token 标准深度分析 | 本 issue PR 清单中 B20 域为其输入 |
| Downstream: WHI-247 | 合规与治理分析 | 本 issue ActivationRegistry/PolicyRegistry 信息为其输入 |
| Downstream: WHI-249 | Reth V2 性能影响分析 | 本 issue Protocol-RethV2 域为其输入 |
| Downstream: WHI-251 | 激活治理分析 | 本 issue Activation-Governance 域为其输入 |

## Quality Checklist (for Adversarial Review)

- [ ] 官方三大 scope 均已确认，无遗漏
- [ ] PR/commit 清单覆盖 v1.0.1→v1.1.1 全部非合并 commit
- [ ] 每个 PR 至少一个变更域分类
- [ ] BOP/PSRC 审计票据准确对应
- [ ] 所有代码引用含 tag + commit + file path（无裸 HEAD）
- [ ] Cobalt-only 变更已排除并附判定依据
- [ ] taxonomy 与官方三大块完整对应（含 Withdrawal-Finality 域，显式标注无 base/base 代码证据）
- [ ] Required Software 表与官方 docs 一致
- [ ] 无复述 `base-azul-upgrade/` 内容（仅引用）
- [ ] Mermaid 图可渲染且信息准确
