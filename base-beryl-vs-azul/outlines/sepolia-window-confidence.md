# Research Outline: Sepolia 短测试窗口与上线信心来源分析

## Metadata

| Field | Value |
|-------|-------|
| project_slug | `base-beryl-vs-azul` |
| topic_slug | `sepolia-window-confidence` |
| multica_issue_id | `7f357aad-260d-4ddd-afb6-89274cd67208` |
| round | 2 |
| github_repo | `Whisker17/multica-research` |
| outline_path | `base-beryl-vs-azul/outlines/sepolia-window-confidence.md` |
| draft_path | `base-beryl-vs-azul/research-sections/sepolia-window-confidence/drafts/round-1.md` |
| final_path | `base-beryl-vs-azul/research-sections/sepolia-window-confidence/final.md` |

## Topic

Sepolia 短测试窗口与上线信心来源分析 — 回答研究问题 2：Base 凭什么敢在 Sepolia 只测了很短时间（7 天公网窗口）就上主网？通过证据重建完整上线节奏，系统拆解信心来源，并强制纳入对抗性残余风险评估。

## Scope

### In-Scope

- **多环境上线节奏重建**：Devnet → Zeronet (load testing) → Sepolia → Mainnet 完整时间线，含每个节点的 commit 证据和 release tag 对应
- **Azul vs Beryl 公网窗口对照**：Azul 38 天 vs Beryl 7 天的量化对比，论证为何不可简单类比
- **信心来源系统拆解**：测试覆盖、审计加固、架构低风险、组织发布节奏四大维度，每条有证据
- **审计票据量化统计**：BOP-/PSRC- 在严格 tag range (`v1.0.1^{}..v1.1.1^{}`) 中的数量（59 unique）、分布与时间密度，含显式 Cobalt/branch-only 排除规则
- **测试基础设施覆盖分析**：beryl test harness（4851 行）+ load testing 基础设施 + devnet E2E
- **架构低风险论证**：引用 WHI-247 blast radius 结论，论证「附加 + fork 门控」模式对上线信心的贡献
- **对抗性残余风险评估（强制）**：7 天公网窗口的真实残余风险、证据不足以证明安全的方面、待主网上线后复核清单
- **协议层风险引用**：引用 WHI-251 提款 7→5 天窗口分析和 3 个待部署确认项

### Out-of-Scope

- B20 token 标准业务逻辑深度分析（WHI-246 覆盖）
- Precompile 基础设施实现细节（WHI-247 覆盖）
- Reth V2 和提款窗口实现细节（WHI-251 覆盖）
- L1 合约层变更的独立分析
- status.base.org 运维事件的实时监控（仅引用已知事实）
- Cobalt 功能分析（WHI-245 已排除）

## Code Baseline

| Network | Release Tag | Commit (`^{}` 解引用) | 用途 |
|---------|------------|----------------------|------|
| Mainnet | `v1.1.1` | `01e732cdbae0c624d652da9e608d7d3fe0f9c74b` | 主网上线版本 |
| Sepolia | `v1.1.0` | `a3c3011b16dae73aaea455ec0a5ff614e65b7d0a` | Sepolia 上线版本 |
| Azul (上一版) | `v1.0.1` | `955a18b189196c6f663235140180e5bcf51cd044` | 对照基线 |

**本地代码路径**: `/Users/whisker/Work/src/networks/base/base`

### Key Timestamps (已核实)

| Network | Activation Timestamp | Date (UTC) | Commit Evidence |
|---------|---------------------|------------|-----------------|
| Zeronet Beryl | `1780678800` | 2026-06-05 17:00 | `bb831a49c` / `ea140129a` (#3214 / #3213) |
| Sepolia Beryl | `1781805600` | 2026-06-18 18:00 | `11da71ece` (backport of #3399) |
| Mainnet Beryl | `1782410400` | 2026-06-25 18:00 | `4e84ba3d1` (#3627) |

### Release Tag Timeline (已核实)

| Tag | Date | RC Count | Notes |
|-----|------|----------|-------|
| v1.1.0-rc.1 | 2026-06-02 | 1/21 | 首个 RC |
| v1.1.0-rc.21 | 2026-06-12 | 21/21 | 最后一个 RC |
| v1.1.0 | 2026-06-12 | — | Sepolia 正式 release |
| v1.1.1-rc.1 | 2026-06-18 | 1/4 | Mainnet RC |
| v1.1.1 | 2026-06-18 | — | Mainnet 正式 release |

### Azul Reference Timeline (已核实)

| Network | Timestamp | Date (UTC) | Evidence Source |
|---------|-----------|------------|----------------|
| Azul Sepolia | `1_776_708_000` | 2026-04-20 18:00 | `config.rs:412` + `overview.md:21`（code 与 spec 一致）— 引用 `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` L430 |
| Azul Mainnet | `1_779_991_200` | 2026-05-28 18:00 | `config.rs:340`（code 端）；spec overview 表格为 TBD（commit `5e3a68de0` 写回）；Azul 研究表述为「code-set, spec TBD」— 引用同上 L431。注：Azul mainnet 已实际激活（Beryl 以 v1.0.1 Azul tag 为 diff 起点），因此 2026-05-28 视为已确认日期 |
| **Azul 公网窗口** | — | **~38 天** | Sepolia 2026-04-20 → Mainnet 2026-05-28 = 38 天 |

**Azul 日期溯源说明**：Azul Sepolia 日期有 code + spec 双重确认；Azul Mainnet 日期在 Azul 研究撰写期（2026-05-17）spec 仍标 TBD，但 code 端 `azul_timestamp` 已设为 `1_779_991_200`。该 Mainnet 激活已在 Beryl 研究基线（v1.0.1 Azul tag）中被事实确认。详见 `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` §8 双口径分析。

## Research Items

### Item 1: 多环境上线时间线重建

**Slug**: `multi-env-timeline`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `devnet_beryl_coverage` | Devnet Beryl precompile E2E 覆盖时间点与 commit 证据（PR #3104） | `git log --all --grep="3104"` + commit `092517562` |
| `zeronet_activation` | Zeronet Beryl 激活日期与调度 commit | `bb831a49c` (#3214)；激活 2026-06-05 17:00 UTC |
| `zeronet_load_testing` | Zeronet 上 B20 load testing 开始时间与覆盖范围 | `296a09ffe` (#3266) 2026-06-08；`a6c14c860` (#3474) 2026-06-11 |
| `sepolia_scheduling` | Sepolia Beryl 升级调度时间与 release 过程 | `11da71ece` (backport of #3399) 2026-06-10；v1.1.0 = 2026-06-12 |
| `sepolia_activation` | Sepolia 实际激活时间 | 2026-06-18 18:00 UTC；timestamp `1781805600` |
| `mainnet_scheduling` | Mainnet 激活日期设定与 release 过程 | `4e84ba3d1` (#3627) 2026-06-18；v1.1.1 = 2026-06-18 |
| `mainnet_activation` | Mainnet 计划激活时间 | 2026-06-25 18:00 UTC；timestamp `1782410400` |
| `rc_iteration_density` | Release candidate 迭代密度：v1.1.0 21 个 RC + v1.1.1 4 个 RC | `git tag -l "v1.1*"` |
| `azul_timeline_comparison` | Azul Sepolia→Mainnet 38 天 vs Beryl 7 天的量化对比 | Azul Sepolia `1_776_708_000` (2026-04-20) 引用 `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` L430；Azul Mainnet `1_779_991_200` (2026-05-28) 引用同上 L431（code-set, spec TBD at research time, now confirmed by Beryl baseline v1.0.1） |
| `total_testing_window` | 从 devnet E2E (#3104) 到 mainnet activation 的总测试周期，论证 "Sepolia 窗口短 ≠ 总测试时间短" | 综合 devnet/zeronet/sepolia 时间线 |

**Output Format** (draft 中的表格):

Azul vs Beryl 双列时间线表：

```
| 阶段 | Azul 日期 | Azul 证据 | Beryl 日期 | Beryl 证据 | 间隔 |
|------|----------|----------|-----------|-----------|------|
| Devnet E2E | — | — | ≤2026-06-02 | #3104 (092517562) | — |
| Zeronet 激活 | — | — | 2026-06-05 | #3214 (bb831a49c) | — |
| ...  | ...      | ...      | ...       | ...       | ...  |
```

**Acceptance Criteria**:
- 每个时间线节点有 commit hash 或 PR# 证据
- Azul 和 Beryl 对照清晰
- 总测试周期（devnet→mainnet）与 Sepolia 公网窗口（7 天）明确区分

### Item 2: 信心来源一：测试覆盖深度

**Slug**: `confidence-testing`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `harness_structure` | Beryl test harness 目录结构与文件分布（11 文件，4851 行） | `actions/harness/tests/beryl/*` @ v1.1.1 |
| `harness_coverage_domains` | 每个测试文件覆盖的功能域：activation (140L), b20 (975L), b20_policy (299L), env (657L), factory (433L), policy_registry (733L), policy_transfer (428L), security (549L), stablecoin (448L) | 文件内容分析 + LOC 统计 |
| `devnet_e2e_scope` | Devnet E2E 测试覆盖范围（PR #3104 引入的测试场景） | PR #3104, commit `092517562` |
| `load_test_infra` | Load testing 基础设施：B20 workload (#3050), blocklist policy setup, zeronet config (#3474), sepolia config | `crates/infra/load-tests/` |
| `load_test_parameters` | 负载参数：devnet 100 senders / 20M GPS；sepolia 200 senders / 60M GPS | `examples/devnet.yaml`, `examples/sepolia.yaml` |
| `load_test_b20_pipeline` | B20 特定负载：grant, mint, burn pipeline (2026-06-19, commit `2debf7c1b`) | commit analysis |
| `test_gap_analysis` | 测试覆盖中的明确缺口：哪些场景无法被 harness/devnet/load-test 覆盖 | 分析 + 对抗视角 |

**Acceptance Criteria**:
- 测试覆盖以文件级粒度呈现（含 LOC）
- Load testing 参数有量化数据
- 明确列出测试覆盖缺口（与 Item 6 残余风险呼应）

### Item 3: 信心来源二：审计加固密度

**Slug**: `confidence-audit`

#### Audit Ticket Derivation Rule (Round 2 修正)

审计票据计数必须遵循以下精确、可复现的规则：

1. **Tag range**: `git log v1.0.1^{}..v1.1.1^{} --format="%H %s%n%b"` — 仅限 `v1.0.1` 至 `v1.1.1` 之间的 commit。
2. **Ancestor constraint**: 仅计入 `v1.1.1^{}` (`01e732cd`) 的祖先 commit。不计入 branch-only commit（如 `origin/ericliu/bop-391-fix` 上的修复）。
3. **De-duplication**: 同一 BOP-xxx / PSRC-xx 出现在多个 commit（如原始 fix + backport squash）时，仅计一次 ticket ID。
4. **Batch expansion**: 单个 commit 引用多个 ticket ID 时（如 BOP Batch 6 #3447 引用 BOP-378/PSRC-26），逐个展开并各计一次。
5. **Full message scan**: 检查 commit subject + body（非仅 oneline），因 squash/backport commit 的 body 中包含原始 ticket 引用。
6. **Cobalt exclusion**: WHI-245 §3.2 排除表中的 Cobalt-only commit（#3119、#3426）虽为 v1.1.1 祖先，但因 `cobalt_timestamp: None` 代码路径运行时不可达，不作为 Beryl 运行时审计加固证据。#3426 (`526d5361c`, "backport PSRC precompile fixes to v1.1.0") 包含 Cobalt dispatch 代码（WHI-245 已确认），其 commit message 不含具体 PSRC-xx ticket ID，因此不影响票据计数但须显式标注。

**Derivation command**: `git log v1.0.1^{}..v1.1.1^{} --format="%H %s%n%b" | grep -oP "(BOP-\d+|PSRC-\d+)" | sort -u`

**Revised count** (round 2):
- **57 unique BOP tickets**: BOP-155, BOP-160, BOP-161, BOP-170, BOP-175, BOP-198, BOP-199, BOP-200, BOP-201, BOP-202, BOP-203, BOP-206, BOP-211, BOP-213, BOP-216, BOP-217, BOP-219, BOP-223, BOP-225, BOP-226, BOP-227, BOP-229, BOP-231, BOP-232, BOP-233, BOP-237, BOP-238, BOP-241, BOP-242, BOP-246, BOP-273, BOP-276, BOP-284, BOP-285, BOP-286, BOP-287, BOP-289, BOP-290, BOP-291, BOP-292, BOP-294, BOP-295, BOP-296, BOP-297, BOP-298, BOP-299, BOP-328, BOP-337, BOP-346, BOP-349, BOP-350, BOP-356, BOP-359, BOP-360, BOP-378, BOP-380, BOP-382
- **2 unique PSRC tickets**: PSRC-26, PSRC-27
- **Total: 59 unique audit tickets** (revised from round 1's incorrect 54)

**Excluded tickets**:
- **PSRC-29**: appears only on `origin/ericliu/bop-391-fix` (commit `cb2f413ae`), NOT an ancestor of `v1.1.1^{}` — excluded per ancestor constraint.
- **#3426 (`526d5361c`)**: WHI-245 §3.2 classifies as Cobalt-excluded. Commit body contains no specific PSRC-xx ticket IDs, so does not affect ticket count. Explicitly caveated as "Cobalt-scoped, not runtime Beryl confidence."

**Round 1→2 delta**: Previous count used `git log --all --grep` which included branch-only commits and multiple branches, inflating and distorting the count. The revised derivation uses strict tag-range + ancestor + de-duplication + full-message scan, yielding 59 (not 54).

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `bop_ticket_count` | BOP 审计票据总数：57 个 unique (BOP-155 ~ BOP-382)，tag range `v1.0.1^{}..v1.1.1^{}` 全消息扫描 | `git log v1.0.1^{}..v1.1.1^{} --format="%H %s%n%b" \| grep -oP "BOP-\d+" \| sort -u` |
| `psrc_ticket_count` | PSRC 审计票据总数：2 个 unique (PSRC-26, PSRC-27)，PSRC-29 excluded (branch-only) | 同上 grep PSRC；PSRC-29 验证：`git merge-base --is-ancestor cb2f413ae v1.1.1^{}` → false |
| `total_audit_tickets` | 合计：59 个 unique 审计票据（57 BOP + 2 PSRC） | 汇总 |
| `cobalt_exclusion_caveat` | #3426 (`526d5361c`) Cobalt-scoped caveat：虽为 v1.1.1 祖先，但 WHI-245 §3.2 排除表分类为 Cobalt-only（`cobalt_timestamp: None`，运行时不可达），不计入 Beryl 运行时审计信心 | 引用 WHI-245 `beryl-scope-inventory/final.md` L356, L492, L504 |
| `audit_fix_distribution` | 审计修复的代码分布：按变更域分类（precompile-storage, b20-factory, b20-stablecoin, policy-registry, precompile-macros 等） | commit message + 文件路径分析 |
| `audit_fix_timeline` | 审计修复的时间密度：集中 backport 日期与发布窗口的关系 | git log 日期分析 |
| `backport_batch_pattern` | Backport 批次模式：BOP Batch 4 (#3423), BOP Batch 6 (#3447), straggler fixes (#3453) — 集中在 2026-06-10~11。#3426 (PSRC backport) 为 Cobalt-scoped，不计入 Beryl 加固证据 | backport commit analysis |
| `audit_coverage_assessment` | 审计覆盖评估：59 个票据覆盖了哪些攻击面，哪些攻击面可能未被覆盖 | 对抗视角分析 |

**Acceptance Criteria**:
- BOP/PSRC 票据数量精确（57 + 2 = 59），含完整 derivation command 可复现
- PSRC-29 excluded with ancestor verification evidence
- #3426 Cobalt caveat explicitly stated
- 审计修复有按域分布统计
- 时间密度分析揭示 backport 模式（与 Item 6 残余风险呼应：审计修复仍在 Sepolia release 附近落入）

### Item 4: 信心来源三：架构低风险论证

**Slug**: `confidence-architecture`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `blast_radius_conclusion` | WHI-247 blast radius 核心结论：对标准以太坊 precompile 地址范围 blast radius 为零；`beryl()` = `azul()` 静态集不变 | 引用 `beryl-precompile-infra/final.md` §Executive Summary |
| `fork_gate_mechanism` | Fork 门控机制：`install_with_observer()` 中 `>= BaseUpgrade::Beryl` 门控，动态 precompile 仅在 Beryl 激活后安装 | 引用 WHI-247 |
| `activation_registry_gate` | ActivationRegistry 二级门控：precompile 激活可独立于 fork 激活控制 | 引用 WHI-247 |
| `additive_architecture` | 附加式架构论证：Beryl 不修改任何既有交易执行路径，仅附加新的 precompile 地址空间 | 引用 WHI-247 |
| `rollback_capability` | 可回退性：ActivationRegistry 允许运行时禁用单个 precompile，无需硬分叉 | 引用 WHI-247 |
| `scope_size_argument` | 变更范围论证：141 个 Beryl 功能 commit 全部集中在 precompile 附加层，不触及共识/derivation/sequencer 核心路径 | 引用 WHI-245 scope inventory |
| `architecture_limitation` | 架构低风险论证的局限：理论上非零的 BerylLookup 地址拦截风险 + 新 precompile 与既有状态交互的未知边际 | 对抗视角 |

**Acceptance Criteria**:
- Blast radius 结论有精确的代码路径引用（通过引用 WHI-247）
- 架构低风险论证明确区分「静态集不变」与「动态集附加」
- 包含架构层面的残余风险（与 Item 6 呼应）

### Item 5: 信心来源四：组织与发布节奏

**Slug**: `confidence-organization`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `independent_release` | OP Stack 脱离后 Base 独立发布控制权：不再受 OP Stack release 节奏约束 | Azul 研究引用 + Beryl release 时间线证据 |
| `rc_iteration_pattern` | RC 迭代模式：v1.1.0 21 个 RC（2026-06-02 ~ 2026-06-12，10 天），v1.1.1 4 个 RC（2026-06-18 当天） | `git tag -l "v1.1*"` |
| `sepolia_mainnet_delta` | v1.1.0→v1.1.1 仅 3 个 commit（激活时间戳 + 版本号 + 1 个 backport），说明 Sepolia 版本接近 production-ready | WHI-245 Code Baseline |
| `activation_date_commit_pattern` | 激活日期设定模式：通过单独 commit 设定激活时间戳，可在最后一刻决定/推迟上线日期 | `4e84ba3d1` (#3627), `11da71ece` (#3399) |
| `status_page_monitoring` | status.base.org 监控能力：公网窗口期间的可观测性 | status.base.org 引用 |

**Acceptance Criteria**:
- RC 迭代密度有量化数据
- v1.1.0→v1.1.1 delta 精确
- 激活日期设定模式作为组织灵活性的证据

### Item 6: 残余风险与待主网复核清单（强制对抗节）

**Slug**: `residual-risk-checklist`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `mev_untestable` | MEV/经济攻击面不可测：Sepolia 无真实 MEV 生态，7 天窗口无法暴露 MEV 驱动的 precompile 交互边缘情况 | 分析论证 |
| `withdrawal_cycle_gap` | 提款周期覆盖缺口：新 5 天提款窗口的首个完整周期在 Sepolia 7 天窗口内刚好完成/刚好不足 — 实战验证不充分 | 引用 WHI-251 |
| `deployment_evidence_gaps` | 3 个部署证据缺口（来自 WHI-251）：(a) 新 AggregateVerifier 部署地址；(b) DisputeGameFactory setImplementation 注册 tx；(c) 部署的 5 天 after-state eth_call 确认 | 引用 WHI-251 residual_caveats |
| `zeronet_vs_mainnet_attack_surface` | Zeronet load test 与主网经济攻击面的差距：无真实价值锁定，无真实用户行为模式，负载模式为合成构造 | 分析 load test config vs 主网特征 |
| `long_tail_state` | 长尾状态转移不可测：B20 token 持久使用的长期状态累积（storage bloat, cross-precompile 交互累积效应）7 天不足以暴露 | 分析论证 |
| `late_audit_remediation` | 审计修复时间风险：BOP batch backport 集中在 2026-06-10~11（Sepolia release v1.1.0 2026-06-12 前 1-2 天），部分修复窗口极短 | git log 时间分析 |
| `beryl_lookup_residual` | BerylLookup 地址拦截残余风险：满足 B20 结构编码的非 B20Factory 部署地址会被拦截（WHI-247 已识别，设计选择但影响面未知） | 引用 WHI-247 |
| `post_mainnet_watchlist` | 待主网上线后复核清单：需持续监控的指标和事件 | 综合以上各项产出 |

**Output Format** (draft 中的表格):

残余风险评估表：

```
| 风险项 | 严重度 | Sepolia 窗口覆盖能力 | 需主网复核？ | 首次可观测时间 |
|--------|--------|---------------------|-------------|---------------|
| MEV 攻击面 | 高 | 不可覆盖 | 是 | 上线后即刻 |
| ...    | ...    | ...                 | ...         | ...           |
```

待主网复核清单：

```
| 待观测项 | 复核条件 | 预计可观测时间 | 关联风险项 |
|---------|---------|---------------|----------|
| 提款 5 天窗口首完整周期 | 首笔 Beryl 提款完成 5 天等待 | 上线后 ~5 天 | withdrawal_cycle_gap |
| ...     | ...     | ...           | ...      |
```

**Acceptance Criteria**:
- 至少 7 个独立的残余风险项
- 每个风险项有严重度评级和 Sepolia 窗口覆盖能力评估
- 待主网复核清单有明确的复核条件和预期时间
- 不是一边倒的乐观结论
- 对抗视角必须对信心来源（Items 2-5）形成实质性挑战

## Source Requirements

### Primary Sources

| Source | Type | Access | Notes |
|--------|------|--------|-------|
| `base/base` repo @ v1.1.1 / v1.1.0 / v1.0.1 | Code | 本地 `/Users/whisker/Work/src/networks/base/base` | 时间线 commit 证据、测试代码、load test 配置 |
| `actions/harness/tests/beryl/*` | Test Code | 同上 | Beryl 专项测试 harness（11 文件，4851 行） |
| `crates/infra/load-tests/` | Test Code | 同上 | 负载测试基础设施（devnet.yaml, sepolia.yaml） |
| git tag history (`v1.1.0*`, `v1.1.1*`) | Release History | 同上 | RC 迭代密度证据（21 + 4 个 RC） |
| WHI-245 (`beryl-scope-inventory/final.md`) | Dependency Research | 同仓库 | 143 commit 清单、15 域 taxonomy、Cobalt 排除 |
| WHI-247 (`beryl-precompile-infra/final.md`) | Dependency Research | 同仓库 | Blast radius = 零、fork 门控、ActivationRegistry |
| WHI-251 (`protocol-reth-withdrawal/final.md`) | Dependency Research | 同仓库 | 提款 7→5 天、Reth V2、3 个部署缺口 |
| Azul Overview (`base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md`) | Prior Research | 同仓库 | Azul 激活时间线：Sepolia `1_776_708_000` (L430), Mainnet `1_779_991_200` (L431)；§8 双口径分析 |

### Secondary Sources

| Source | Type | Access | Notes |
|--------|------|--------|-------|
| status.base.org | Web | HTTPS | Sepolia/Mainnet 激活时间确认 |
| `base/node` releases | Code | GitHub / workspace resource | node 版本确认 |
| Base Beryl blog (blog.base.dev) | Docs | HTTPS | 官方上线公告 |

### Source Integrity Rules

1. 所有 commit 引用必须标注 `tag + commit hash + PR#`（如适用）
2. 禁止裸 HEAD 引用
3. 时间线事实须有 commit timestamp 或 tag date 双重验证
4. 引用依赖研究（WHI-245/247/251）时标注 final.md 路径和结论出处，不复述全文
5. 对抗视角中的风险评估须区分「已有证据」和「分析推断」

## Diagram Expectations

### Diagram 1: 多环境上线时间线（Azul vs Beryl 对照）

**Type**: 双轨 Timeline / Gantt 图
**Content**: 左轨 Azul (Sepolia 2026-04-20 → Mainnet 2026-05-28)；右轨 Beryl (Devnet → Zeronet → Sepolia → Mainnet)，标注每个节点的日期和 commit 证据
**Format**: Mermaid gantt
**Purpose**: 直观对比两次升级的测试节奏差异；论证 "Beryl 公网窗口虽短，但总测试周期并非更短"

### Diagram 2: 信心来源与残余风险对照图

**Type**: 四象限/平衡图
**Content**: 左列信心来源（测试覆盖、审计密度、架构低风险、组织节奏），右列对应的残余风险/挑战，中间标注强度评估
**Format**: Mermaid flowchart
**Purpose**: 确保报告不是一边倒论述；每个信心来源都有对应的对抗审视

### Diagram 3: Release Candidate 迭代密度图

**Type**: 时间轴标注图
**Content**: v1.1.0-rc.1 ~ rc.21（10 天 21 个 RC）+ v1.1.1-rc.1 ~ rc.4（1 天 4 个 RC），标注关键 backport 事件
**Format**: Mermaid timeline 或 gantt
**Purpose**: 量化 release 工程密度，作为组织信心来源的证据

## Expected Output Summary

Draft (`round-1.md`) 应包含：

1. **§1 Executive Summary** — 核心结论：7 天 Sepolia 窗口的上下文（非孤立窗口，而是多环境测试管线的最终阶段）、信心来源摘要、残余风险摘要
2. **§2 多环境上线时间线** — Azul vs Beryl 双列对照表 + Mermaid timeline + 总测试周期计算
3. **§3 信心来源拆解** — 四个子节：
   - §3.1 测试覆盖深度（harness LOC 表 + load test 参数 + devnet E2E 覆盖）
   - §3.2 审计加固密度（57 BOP + 2 PSRC = 59 tickets，严格 tag-range 推导含 derivation command，PSRC-29 excluded (branch-only)，#3426 Cobalt caveat，域分布，backport 批次模式）
   - §3.3 架构低风险（blast radius 零 + fork 门控 + ActivationRegistry + 附加式变更）
   - §3.4 组织与发布节奏（独立发布权 + RC 迭代密度 + v1.1.0→v1.1.1 minimal delta + 灵活激活日期机制）
4. **§4 残余风险与待主网复核**（独立节，非嵌套在信心来源下）：
   - §4.1 残余风险评估表（≥7 个风险项，含严重度、Sepolia 覆盖能力、是否需主网复核）
   - §4.2 待主网上线后复核清单（含复核条件和预期可观测时间）
   - §4.3 证据不足以证明安全的明确领域
5. **§5 结论与判断框架** — 不是「安全/不安全」的二元判断，而是证据支持矩阵：哪些信心来源有充分证据，哪些仍需主网验证

## Cross-References

| Reference | Path / Source | Relation |
|-----------|--------------|----------|
| WHI-245 Beryl Scope Inventory | `beryl-scope-inventory/final.md` | 143 commit 清单、15 域 taxonomy — 引用变更范围作为架构论证输入 |
| WHI-247 Precompile Infrastructure | `beryl-precompile-infra/final.md` | Blast radius 零、fork 门控、ActivationRegistry — 核心架构信心来源 |
| WHI-251 Protocol & Withdrawal | `protocol-reth-withdrawal/final.md` | 提款 7→5 天、Reth V2、3 个部署缺口 — 残余风险输入 |
| Azul Upgrade Research | `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` | Azul 激活时间线基线：Sepolia `1_776_708_000` (L430) + Mainnet `1_779_991_200` (L431)；引用不复述。§8 双口径分析为 Mainnet 日期的 caveat 来源 |
| status.base.org | Web | 激活时间确认 |
| WHI-250 (downstream) | 待产出 | 本研究为 WHI-250 的输入 |

## Quality Checklist (for Adversarial Review)

- [ ] 多环境时间线表每个节点有 commit hash / PR# / tag 证据
- [ ] Azul vs Beryl 对照清晰，公网窗口数字（7 天 vs 38 天）有 code timestamp 证据（Azul dates sourced from `base-azul-upgrade` research L430-431, not bare assertions）
- [ ] 总测试周期（devnet→mainnet）与 Sepolia 公网窗口（7 天）明确区分
- [ ] 信心来源四维度每条有量化证据（LOC / 票据数 / RC 数 / commit count）
- [ ] BOP/PSRC 审计票据量化精确（57 BOP + 2 PSRC = 59），含可复现 derivation command
- [ ] PSRC-29 excluded with `git merge-base --is-ancestor` 验证；#3426 Cobalt caveat 显式标注
- [ ] 审计票据推导规则（tag range + ancestor + de-dup + full-message + Cobalt exclusion）在 §3.2 中完整陈述
- [ ] 独立残余风险节至少 7 个风险项，非嵌套在信心来源下
- [ ] 残余风险有严重度评级和 Sepolia 覆盖能力评估
- [ ] 待主网复核清单有明确复核条件和预期时间
- [ ] 对抗视角对信心来源形成实质性挑战（非敷衍带过）
- [ ] 不出现为 Base 背书的措辞（如「完全安全」「毫无风险」）
- [ ] 引用依赖研究（WHI-245/247/251）标注出处路径
- [ ] 所有代码引用含 tag + commit（无裸 HEAD 引用）
- [ ] Mermaid 图可渲染且信息准确
- [ ] §4 残余风险节内容量不少于 §3 任一子节（强制对称性）
