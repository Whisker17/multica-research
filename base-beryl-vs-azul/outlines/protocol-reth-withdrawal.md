# Research Outline: Reth V2、Withdrawal Finalization 与 Required Software 变更分析（协议/客户端层）

## Metadata

| Field | Value |
|-------|-------|
| project_slug | `base-beryl-vs-azul` |
| topic_slug | `protocol-reth-withdrawal` |
| multica_issue_id | `0170ae77-f28e-473f-9059-c98f48691453` |
| round | 2 |
| github_repo | `Whisker17/multica-research` |
| outline_path | `base-beryl-vs-azul/outlines/protocol-reth-withdrawal.md` |
| draft_path | `base-beryl-vs-azul/research-sections/protocol-reth-withdrawal/drafts/round-1.md` |
| final_path | `base-beryl-vs-azul/research-sections/protocol-reth-withdrawal/final.md` |

## Topic

Reth V2、Withdrawal Finalization 与 Required Software 变更分析 — 补齐 Beryl 官方 scope 中的**协议/客户端层变更**，为 B20 以外的两大 scope（提款窗口缩短、Reth V2 客户端升级）及发布工程建立代码级证据基线，并评估风险面。

## Scope

### In-Scope

- Single-proof withdrawal finalization 7→5 天：L1 合约参数变更（`SLOW_FINALIZATION_DELAY`）的证据链；确认 dual-proof (TEE+ZK) 快路径 `FAST_FINALIZATION_DELAY` 仍为 1 天
- Reth V2 依赖升级：磁盘优化（官方最高 −50%）的 Storage V2 机制、state root pipeline 重写（官方 +33% 吞吐）的 Proof V2 架构、Base 所用 v2.3.0 的具体代码变更（8 个 Protocol-RethV2 commit 的逐条分析）
- Required software 版本矩阵：EL (`base-reth-node`) / CL (`base-consensus`) / node (`base/node`) × mainnet / sepolia，含 Reth upstream 版本与构建工具链
- 风险面分析：withdrawal 窗口缩短对安全假设的影响、Reth V2 Storage V2 / Proof V2 是否触及共识机制、与 WHI-249 信心分析的衔接点

### Out-of-Scope

- B20 原生 token 标准深度分析（WHI-246 专题）
- 合规与治理分析（WHI-247 专题）
- Reth V2 性能基准测试与定量评估（WHI-249 专题，本研究仅建立代码级证据供其引用）
- L1 合约代码的完整逐行审计（withdrawal 变更涉及 L1 合约参数调整，本研究须从链上部署获取参数值和部署交易作为 mandatory 证据，但不做完整的 L1 合约安全审计）
- Cobalt 功能分析（`cobalt_timestamp: None`，不在 Beryl 运行时执行）
- B20 以外的 EVM 集成变更（已由 beryl-scope-inventory 覆盖）

## Code Baseline

| Network | Repo | Release Tag | Commit（`git rev-parse <tag>^{}`） | 用途 |
|---------|------|------------|-----------------------------------|------|
| Mainnet | `base/base` | `v1.1.1` | `01e732cdbae0c624d652da9e608d7d3fe0f9c74b` | 主网上线版本，主基线 |
| Sepolia | `base/base` | `v1.1.0` | `a3c3011b16dae73aaea455ec0a5ff614e65b7d0a` | Sepolia 上线版本 |
| Azul (上一版) | `base/base` | `v1.0.1` | `955a18b189196c6f663235140180e5bcf51cd044` | Diff 起点 |
| Mainnet | `base/node` | `v1.1.1` | (tag 解引用) | Node 发布版本 |
| Sepolia | `base/node` | `v1.1.0` | (tag 解引用) | Node 发布版本 |
| Upstream | `paradigmxyz/reth` | `v2.3.0` | — | Reth upstream 基线 |

**引用规则**：所有代码引用须带 tag + commit + file path (+line number)；禁用裸 HEAD 引用。

### Codebase Access Constraint (Hard Requirement for Deep Draft)

当前 `base/base` 仓库因 multica repo sync 问题无法在 outline 阶段直接 checkout。

**Deep draft 阶段须满足以下硬性要求**：

1. **必须重试** `multica repo checkout https://github.com/base/base --ref v1.1.1` 获取直接的 tag/commit/file 访问。如 multica checkout 仍不可用，须尝试替代路径（如本地 `/Users/whisker/Work/src/networks/base/` 或 GitHub API）。
2. **不得以 WHI-245 scope inventory 替代直接代码访问**作为合约参数、部署交易、或 Reth upstream 版本映射的证据来源。Scope inventory 提供 commit 级索引，但不能替代实际文件内容读取（如 `Cargo.toml` 中 reth 版本、合约 ABI、constructor args）。
3. **如直接代码访问最终不可用**，draft 中每个受影响的 investigation field 须显式标注 `[ACCESS LIMITATION]`，说明哪些结论依赖间接来源（docs 引用、web research），以及该结论的置信度降级。
4. **Item 1 的 5 个 MANDATORY 字段**（`deployed_contract_address` 等）不依赖 `base/base` 代码库——这些是 L1 链上证据。即使 base/base checkout 失败，这些字段的证据仍须从链上数据、Optimism specs、或已部署合约直接获取，不可降级。

## Research Items

### Item 1: Withdrawal Finalization 7→5 天

**Slug**: `withdrawal-finalization-change`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `deployed_contract_address` | **[MANDATORY]** 存放 finalization delay 参数的 L1 合约（或 proxy）的确切地址。可能是 DisputeGameFactory、FaultDisputeGame implementation、OptimismPortal proxy、或 Beryl 专用的 MultiproofGame 合约。须明确标注合约类型和链（Ethereum mainnet / Sepolia）| L1 链上数据（Etherscan 或等效区块浏览器）；Optimism specs `fault-dispute-game.md`；Base 官方文档 |
| `parameter_name_and_location` | **[MANDATORY]** 控制 single-proof finalization 延迟的参数/变量/immutable 的准确名称。可能是 `SLOW_FINALIZATION_DELAY`、`maxClockDuration`、`gameDuration`、dispute game constructor immutable、或 registry config entry — 须确认实际名称，而非从文档推测。标注该参数是 immutable（合约部署时固定）、storage variable（可通过治理交易修改）、还是 registry config entry | L1 合约代码或已验证的链上 ABI；Optimism specs dispute game 参数表 |
| `before_after_values` | **[MANDATORY]** 参数变更前后的数值，含明确单位：Before = 7 天 = 604,800 秒；After = 5 天 = 432,000 秒。须从链上实际部署或合约 immutable 中读取确认，不得仅依赖官方 docs 声明 | L1 链上合约读取（`eth_call` 或 Etherscan verified source）；或合约部署 constructor args |
| `deployment_tx_or_config_source` | **[MANDATORY]** 确认 Beryl 部署设置了新 finalization delay 值的交易 hash 或 immutable config 来源。如参数为 immutable：部署新 dispute game implementation 的交易 hash + constructor args。如参数为 storage variable：更新参数的治理交易 hash。如参数来自 registry config：registry 更新交易 hash | L1 链上交易记录 |
| `spec_vs_deployment_reconciliation` | **[MANDATORY]** Beryl overview 声明（"single-proof window reduced to 5 days"）与 Optimism proof-contracts spec（可能仍描述 `SLOW_FINALIZATION_DELAY` 固定为 7 天）之间的显式对账。Draft 须回答以下之一：(a) 部署合约的 immutable/config 覆盖了 spec 中的默认值 — 引用具体部署证据；(b) spec 已更新以反映 5 天 — 引用 spec 版本；(c) 存在未解决的差距 — 显式报告为 gap 而非假设 5 天已在代码中确认。**不得将 docs 声明单独视为代码确认** | Optimism specs `fault-dispute-game.md` 当前版本 vs L1 已部署合约的实际参数对比 |
| `fast_finalization_unchanged` | **[MANDATORY]** `FAST_FINALIZATION_DELAY`（dual-proof TEE+ZK 快路径）保持 1 天（86,400 秒）不变的确认。须与 `deployed_contract_address` 同源验证：从同一合约或 registry 中读取 fast path 参数，确认 Beryl 前后无变化 | 同 `deployed_contract_address` 的链上数据源；`base-azul-upgrade/research-sections/multiproof-architecture/final.md`（引用不复述）|
| `dispute_game_architecture` | Multiproof Game 架构回顾：FaultDisputeGame / PermissionedDisputeGame + TEE arm + ZK arm，`PROOF_THRESHOLD = 1`，单证明 vs 双证明的 finalization 路径差异。此字段为背景描述，不替代上述 mandatory 字段的链上证据 | Optimism specs；官方 docs；`base-azul-upgrade/` 既有研究 |
| `base_base_code_evidence` | 确认 base/base EL 代码库**无** withdrawal finalization 相关变更：`git log v1.0.1^{}..v1.1.1^{} --no-merges --grep='withdraw\|dispute.*game\|finalization'` 返回零结果 | beryl-scope-inventory/final.md §1.2（已确认） |
| `capital_efficiency_impact` | 窗口缩短对 fast-bridge LP 资本效率的影响机制：锁仓时间缩短 → LP 资本周转率提升 → 用户桥接费用下降。量化框架（如可行） | 官方 blog 声明；DeFi bridge 经济学文献 |
| `dual_proof_adoption_status` | Dual-proof 快路径（1 天）实际使用率低的原因：ZK proof 生成成本高；对比 single-proof 路径使用情况 | 官方 blog 声明；链上数据分析（如可获取） |

**Acceptance Criteria**:
- **[HARD GATE]** 5 个 MANDATORY 字段（`deployed_contract_address`、`parameter_name_and_location`、`before_after_values`、`deployment_tx_or_config_source`、`spec_vs_deployment_reconciliation`）全部须有链上或已部署合约级证据。如某字段证据不可获取，draft 须显式报告为 **unresolved gap**，不得以官方 docs 声明替代
- `FAST_FINALIZATION_DELAY` 保持 1 天须从与 slow path 同源的链上数据确认
- 确认 base/base 代码库零相关变更（引用 scope inventory 证据）
- Beryl overview vs proof-contracts spec 的对账须有明确结论（已确认覆盖 / spec 已更新 / 未解决差距），不得回避
- 明确标注每个证据的层级：L1 链上部署/交易 > 已验证合约源码 > 官方 docs > Optimism specs 默认值

### Item 2: Reth V2 磁盘优化与 State Root Pipeline 重写

**Slug**: `reth-v2-disk-and-stateroot`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `reth_v2_storage_v2` | Reth 2.0 Storage V2 架构：磁盘格式重写、持久化性能（标准 block 40ms vs V1 8.4s，~20x 加速）、Minimal mode（<300GB mainnet）。区分「官方声称」与「代码可验证」 | Paradigm Reth 2.0 发布文章（2026-04）；`paradigmxyz/reth` v2.0.0 release notes；Base 官方 docs `overview.mdx` L10 |
| `reth_v2_proof_v2` | State root pipeline 重写（Proof V2）：merkle proof 计算的 sparse trie 重写、partial proofs、cursor re-use、engine backpressure、shared execution cache。吞吐提升 +33% 的代码层面证据 | Paradigm Reth 2.0 发布文章；`paradigmxyz/reth` 相关 PR/commit |
| `base_reth_v230` | Base 选用 Reth v2.3.0（非 v2.0.0）的原因与增量改进：v2.3.0 trie/proof/cursor 热路径优化，吞吐 1.4→1.5 Ggas/s（+8.1%）| `paradigmxyz/reth` v2.3.0 release notes；`Cargo.toml`（v1.1.1 @ `01e732cdb`）reth deps tag = `v2.3.0` |
| `protocol_rethv2_commits` | base/base 中 8 个 Protocol-RethV2 commit 的逐条分析（来源：beryl-scope-inventory §3.1），每条含变更内容、影响范围、与 Reth upstream 的关系：(1) #3471 v2.3.0 backport 44 files，(2) #3480 overlay builder state trie cache，(3) #3482 EL peer defaults 80/80，(4) #3315 flashblocks pending-state fast path，(5) #3269 flashblocks ping interval configurable，(6) #3114 BLAKE3 static file chunks，(7) #3132 revm-inspectors bump，(8) #3634 backport #3603 flashblocks | beryl-scope-inventory/final.md §3.1 Protocol-RethV2 行；`base/base` repo @ v1.1.1（需 checkout 或引用已有数据） |
| `disk_reduction_evidence` | 磁盘占用降低的代码层面证据：Storage V2 默认启用路径、数据表裁剪、static file 分块策略（BLAKE3 hash — commit `f4042a84e` #3114）| `base/base` repo @ v1.1.1；`paradigmxyz/reth` Storage V2 代码 |
| `state_root_throughput_evidence` | State root 吞吐提升的代码层面证据：overlay builder state trie cache（#3480）、flashblocks pending-state fast path（#3315）与 Proof V2 upstream 的关系 | `base/base` repo @ v1.1.1；`paradigmxyz/reth` Proof V2 代码 |
| `azul_to_beryl_diff` | Reth V2 相对 Azul 时期（v1.0.1 使用 reth v1.x）的执行客户端架构差异：存储引擎切换、state root 计算流程变化、对 flashblocks 的影响 | `base/base` v1.0.1 vs v1.1.1 Cargo.toml reth 版本对比 |

**Acceptance Criteria**:
- 8 个 Protocol-RethV2 commit 逐条列出变更内容与影响
- 磁盘优化 (−50%) 和 state root 吞吐 (+33%) 分别标注「代码可验证」vs「官方声称」
- Reth v2.3.0 相对 v2.0.0 的增量改进有来源
- 标注 base/base 代码层面的直接证据 vs Reth upstream 继承的间接证据

### Item 3: Required Software 版本矩阵

**Slug**: `required-software-matrix`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `el_version_matrix` | 执行层 (EL) 版本矩阵：`base-reth-node` binary × mainnet v1.1.1 / sepolia v1.1.0，含 commit SHA | `base/base` release tags；`base/node` `versions.env`（v1.1.1：`BASE_RETH_NODE_COMMIT=01e732cd...`, `BASE_RETH_NODE_TAG=v1.1.1`）|
| `cl_version_matrix` | 共识层 (CL) 版本矩阵：`base-consensus` binary（与 `base-reth-node` 同仓库构建）× mainnet / sepolia | `base/base` Dockerfile（`cargo build --bin base-consensus`）；`base/node` Dockerfile |
| `node_version_matrix` | Node 发布版本矩阵：`base/node` v1.1.1 (mainnet) / v1.1.0 (sepolia)，包含 Docker image 构建信息（Rust 1.93, ubuntu:24.04, mold 2.40.4）| `base/node` repo @ v1.1.1 `versions.env`, `Dockerfile` |
| `reth_upstream_version` | Reth upstream 版本确认：`Cargo.toml` 中所有 reth crate 的 `tag = "v2.3.0"` | `base/base` @ v1.1.1 `Cargo.toml` |
| `utility_binaries` | 辅助工具 binary 清单：`basectl`（功能、用途）| `base/base` Dockerfile；`base/node` Dockerfile |
| `sepolia_vs_mainnet_delta` | v1.1.0→v1.1.1 仅 3 个 commit（#3634 backport, #3627 mainnet 激活时间戳, #3624 版本号）— 确认 Sepolia 与 Mainnet 功能等价 | beryl-scope-inventory/final.md §2.2 |
| `node_config_diff` | `base/node` mainnet vs sepolia 配置差异：`.env.mainnet` vs `.env.sepolia` 的关键参数对比（chain ID、sequencer URL、RPC 端口）| `base/node` @ v1.1.1 `.env.mainnet`, `.env.sepolia` |
| `upgrade_prerequisites` | 节点运维升级前置动作清单：版本升级路径、激活时间戳前的操作窗口、回滚方案 | 官方 docs Required Software 表；`base/node` README.md |

**Output Format** (draft 中的版本矩阵表):

```
| 层级 | Binary | Mainnet Version | Mainnet Commit | Sepolia Version | Sepolia Commit |
|------|--------|----------------|----------------|-----------------|----------------|
| EL   | base-reth-node | v1.1.1 | 01e732cd... | v1.1.0 | a3c3011b... |
| CL   | base-consensus | v1.1.1 | 01e732cd... | v1.1.0 | a3c3011b... |
| Node | base/node      | v1.1.1 | ...         | v1.1.0 | ...          |
| Upstream | paradigmxyz/reth | v2.3.0 | ... | v2.3.0 | ... |
```

**Acceptance Criteria**:
- 版本矩阵覆盖 EL/CL/node/upstream 四层 × mainnet/sepolia 两网
- 每层版本号与 commit SHA 对齐
- 构建工具链版本（Rust、mold、base image）完整
- v1.1.0→v1.1.1 的 3 commit 差异已确认
- 与官方 docs Required Software 表交叉验证

### Item 4: 风险面分析

**Slug**: `risk-surface-analysis`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `withdrawal_window_risk` | Withdrawal 窗口 7→5 天缩短的安全影响：(a) challenger 响应时间是否足够；(b) Multiproof 架构下窗口缩短的安全前提（检测并禁用故障 prover）；(c) 与 Stage 1 rollup 合规的关系 | Optimism specs `fault-dispute-game.md`；L2Beat 标准；`base-azul-upgrade/` multiproof 研究 |
| `further_reduction_path` | 官方对进一步缩短窗口的声明（「allows the window to keep shrinking」）：路线图依据与技术前提 | 官方 blog 声明 |
| `reth_v2_consensus_safety` | Reth V2 Storage V2 / Proof V2 是否触及共识机制：(a) 存储引擎切换是否影响 state 一致性；(b) state root 计算重写是否改变最终状态根；(c) 新旧存储格式的迁移安全性 | Reth 2.0 release notes 安全性声明；代码层面 state root 计算等价性分析 |
| `flashblocks_interaction` | Reth V2 与 Flashblocks 的交互风险：pending-state fast path (#3315) 和 metadata 处理 (#3634) 是否引入新的 edge case | `base/base` Protocol-RethV2 commit 分析 |
| `peer_defaults_impact` | EL peer defaults 80/80 (#3482) 的网络拓扑影响：更高的 peer 数量对节点资源消耗与网络连通性的影响 | `base/base` @ v1.1.1 `crates/execution/cli/src/node.rs` |
| `whi_249_handoff` | 与 WHI-249（信心分析）的衔接点：本研究的风险面如何为信心评级提供输入——哪些风险已缓解、哪些需要 WHI-249 进一步定量评估 | 本研究其他 Items 的结论汇总 |

**Acceptance Criteria**:
- 每个风险点标注严重程度评级（Critical / Major / Minor / Info）
- Withdrawal 窗口缩短与共识安全的关系有 Multiproof 架构支撑
- Reth V2 风险明确区分「存储层变更」（不触及共识）vs「state root 计算变更」（可能触及共识）
- 与 WHI-249 的衔接点显式列出，供下游 issue 引用
- 区分「已缓解风险」与「待进一步评估风险」

## Source Requirements

### Primary Sources

| Source | Type | Access | Notes |
|--------|------|--------|-------|
| `base/base` repo @ v1.1.1 / v1.1.0 / v1.0.1 | Code | `multica repo checkout` (需重试) | 8 个 Protocol-RethV2 commit 的代码分析；Cargo.toml reth 版本 |
| `base/node` repo @ v1.1.1 / v1.1.0 | Code | 已 checkout | versions.env, Dockerfile, .env.*, entrypoint scripts |
| 官方 docs `overview.mdx` | Docs | `base/base` repo 内 `docs/base-chain/specs/upgrades/beryl/overview.mdx` | Beryl scope 定义，withdrawal 7→5 天, Reth V2 声明 |
| `beryl-scope-inventory/final.md` | Research | 同仓库 `base-beryl-vs-azul/research-sections/beryl-scope-inventory/final.md` | 143 commit 清单、15 域 taxonomy、Protocol-RethV2 commit 列表（引用不复述） |

### Secondary Sources

| Source | Type | Access | Notes |
|--------|------|--------|-------|
| Paradigm Reth 2.0 发布文章 | Web | `paradigm.xyz/2026/04/releasing-reth-2-0` | Storage V2, Proof V2 架构细节 |
| `paradigmxyz/reth` v2.3.0 release | Web | GitHub releases | v2.3.0 增量改进 |
| Optimism specs `fault-dispute-game.md` | Spec | `github.com/ethereum-optimism/specs` | Dispute game finalization 参数定义 |
| `base-azul-upgrade/` 既有研究 | Research | 同仓库 | Multiproof 架构、Azul 基线（引用不复述） |
| 官方 blog `blog.base.dev/introducing-base-beryl` | Web | HTTPS | Withdrawal 动机、Reth V2 声明、路线图 |
| L2Beat Base 风险评估 | Web | `l2beat.com/scaling/projects/base` | Stage 1 合规与 finalization window 标准 |

### Source Integrity Rules

1. 所有代码引用必须标注 `tag + commit + file path (+line number)`
2. 禁止裸 HEAD 引用
3. Tag commit 必须使用 `git rev-parse <tag>^{}` 解引用值
4. 引用 `beryl-scope-inventory/final.md` 和 `base-azul-upgrade/` 既有研究时仅引用路径和结论，不复述内容
5. 官方声称的性能数字（−50% 磁盘、+33% 吞吐）须区分「代码可验证」与「官方声称」
6. L1 合约参数变更的证据层级（从强到弱）：L1 链上已部署合约读取 > 已验证合约源码/constructor args > 官方 docs 声明 > Optimism specs 默认值。Item 1 的 MANDATORY 字段要求最高层级证据；docs 声明单独不构成充分证据
7. WHI-245 scope inventory 提供 commit 级索引参考，但不得作为合约参数、部署交易、或文件内容的直接证据来源

## Diagram Expectations

### Diagram 1: Withdrawal Finalization 路径对比

**Type**: 流程对比图 (Side-by-side flowchart)
**Content**: Single-proof path（7→5 天）vs Dual-proof fast path（1 天）的 finalization 流程对比；标注 `SLOW_FINALIZATION_DELAY` 和 `FAST_FINALIZATION_DELAY` 参数位置
**Format**: Mermaid flowchart
**Purpose**: 直观展示两条 withdrawal finalization 路径的时间差异与触发条件

### Diagram 2: Reth V2 架构变化概览

**Type**: 层次结构图 (Architecture overview)
**Content**: Storage V1 → Storage V2 的存储引擎变化；State Root Pipeline V1 → Proof V2 的计算流程变化；标注 Base v2.3.0 选用的具体组件
**Format**: Mermaid flowchart
**Purpose**: 展示 Reth V2 的两大核心变更及 Base 的采用路径

### Diagram 3: Required Software 组件关系

**Type**: 组件关系图 (Component diagram)
**Content**: `base/node` → Docker image → `base-reth-node` (EL) + `base-consensus` (CL) + `basectl` 的构建与部署关系；标注 Reth upstream v2.3.0 的依赖位置
**Format**: Mermaid flowchart
**Purpose**: 展示 Required Software 组件间的层次关系与版本依赖

**Note**: 不需要风险矩阵图（文字表格已足够）；不需要 timeline 图（时间戳已在 scope inventory 中明确）。

## Expected Output Summary

Draft (`round-1.md`) 应包含：

1. **§1 Withdrawal Finalization 7→5 天** — 5 个 MANDATORY 字段的链上证据（合约地址、参数名、before/after 值、部署交易、spec 对账）；`FAST_FINALIZATION_DELAY` 同源确认不变；Multiproof Game 架构回顾；base/base 零代码变更确认；资本效率影响；Mermaid 路径对比图。任何无法获取链上证据的字段须报告为 unresolved gap
2. **§2 Reth V2 磁盘优化与 State Root Pipeline 重写** — Storage V2 架构与磁盘优化机制；Proof V2 与 state root 吞吐提升；Base v2.3.0 选型与增量改进；8 个 Protocol-RethV2 commit 逐条分析；「代码可验证」vs「官方声称」标注；Mermaid 架构图
3. **§3 Required Software 版本矩阵** — EL/CL/node/upstream × mainnet/sepolia 版本表；构建工具链；v1.1.0→v1.1.1 差异；node 配置差异；升级前置动作；Mermaid 组件图
4. **§4 风险面分析** — Withdrawal 窗口缩短安全影响；Reth V2 共识安全性；Flashblocks 交互风险；网络拓扑影响；WHI-249 衔接点

## Cross-References

| Reference | Path / ID | Relation |
|-----------|-----------|----------|
| Beryl Scope Inventory | `base-beryl-vs-azul/research-sections/beryl-scope-inventory/final.md` | 上游依赖：143 commit 清单、Protocol-RethV2 8 commit、Withdrawal-Finality 零代码证据（引用不复述） |
| Multiproof Architecture | `base-azul-upgrade/research-sections/multiproof-architecture/final.md` | Azul Multiproof 基线：TEE+ZK dual-proof 架构、PROOF_THRESHOLD、finalization delay 定义（引用不复述） |
| Azul Overview | `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` | Azul scope 基线（引用不复述） |
| Downstream: WHI-248 | Multica issue | 本研究 §1 withdrawal finalization 证据为 WHI-248 L1 合约分析的输入 |
| Downstream: WHI-249 | Multica issue | 本研究 §2 Reth V2 代码证据 + §4 风险面为 WHI-249 信心分析的输入 |

## Quality Checklist (for Adversarial Review)

- [ ] **[HARD GATE]** Finalization delay 参数有确切 L1 合约地址（或 proxy）
- [ ] **[HARD GATE]** 参数名（immutable/variable/config entry）从链上或已验证合约源码确认，非推测
- [ ] **[HARD GATE]** Before-value = 7 天 (604,800s) 和 After-value = 5 天 (432,000s) 从链上数据读取确认
- [ ] **[HARD GATE]** 部署/更新交易 hash 或 immutable config constructor args 已记录
- [ ] **[HARD GATE]** Beryl overview vs proof-contracts spec 对账有明确结论（confirmed override / spec updated / unresolved gap）
- [ ] `FAST_FINALIZATION_DELAY` 保持 1 天从同源链上数据确认
- [ ] base/base EL 代码库 withdrawal 零变更已引用 scope inventory 证据
- [ ] 8 个 Protocol-RethV2 commit 逐条列出变更内容与影响
- [ ] 磁盘优化 (−50%) 标注「代码可验证」vs「官方声称」
- [ ] State root 吞吐 (+33%) 标注「代码可验证」vs「官方声称」
- [ ] Required Software 版本矩阵覆盖 EL/CL/node/upstream × mainnet/sepolia
- [ ] 版本号与 commit SHA 与 `base/node` versions.env 一致
- [ ] v1.1.0→v1.1.1 仅 3 commit 差异已确认
- [ ] 所有代码引用含 tag + commit + file path（无裸 HEAD）
- [ ] 风险面每个风险点有严重程度评级
- [ ] Reth V2 风险区分「存储层变更」vs「state root 计算变更」
- [ ] 与 WHI-249 衔接点显式列出
- [ ] 无复述 `beryl-scope-inventory/` 或 `base-azul-upgrade/` 内容（仅引用）
- [ ] Mermaid 图可渲染且信息准确
- [ ] 引用 Reth upstream 变更时区分 Base 直接代码 vs upstream 继承
