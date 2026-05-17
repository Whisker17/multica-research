---
topic: "Multiproof 系统架构与链上组件分析"
project_slug: base-azul-upgrade
topic_slug: multiproof-architecture
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: base-azul-upgrade/outlines/multiproof-architecture.md
  draft: base-azul-upgrade/research-sections/multiproof-architecture/drafts/round-{n}.md
  final: base-azul-upgrade/research-sections/multiproof-architecture/final.md
  index: base-azul-upgrade/research-sections/_index.md

scope: |
  深入分析 Base Azul 引入的 Multiproof 系统在链上的合约级实现：以 AggregateVerifier 为中心的争议游戏
  设计、TEEVerifier 与 ZKVerifier 专用验证器子系统、DelayedWETH bond 托管、OptimismPortal2 与
  AnchorStateRegistry 在去掉 3.5 天 proof-maturity delay 后的重构，以及三条结算路径
  （TEE only / ZK only / TEE+ZK）的 finality 触发逻辑。聚焦合约接口、状态机、不变量、安全假设与
  代码引用；对 Prover/Challenger/Registrar 的 off-chain 实现与执行层 EIP 变更只做边界引用，
  分别由 multiproof-provers-challengers 与 osaka-evm-changes 子课题承接。
audience: |
  Multica 研究 squad 内部下游 Adversarial Agent 与 Technical Writer、关注 L2 Stage 2 与 Rollup
  Fault Proof 设计的协议工程师、安全审计员、L1↔L2 Bridge 集成方。读者熟悉 OP Stack Fault Proof
  V2 基本结构（FaultDisputeGame、AnchorStateRegistry、OptimismPortal2、DelayedWETH），但不
  一定了解 Azul 的多证明聚合改造。
expected_output: |
  - Multiproof 系统合约级架构分析文档
  - AggregateVerifier 状态机、proposal/challenge/resolve 流程与外部调用序列分析
  - TEEVerifier 与 ZKVerifier 的接口规范、proof payload 结构、immutability 设计的安全论证
  - 三条结算路径（TEE only 7d / ZK only 7d permissionless / TEE+ZK 1d）的 finality 触发逻辑与参数推导
  - DelayedWETH 提款延迟从旧值降至 1 天的原因与 bond 经济影响
  - OptimismPortal2 与 AnchorStateRegistry 在去掉独立 3.5 天 proof-maturity delay 后的新结算流程
  - 与 OP Stack Fault Proof V2 的差异对比表（合约、参数、信任假设）
  - 至少 4 张 Mermaid 架构 / 序列 / 流程图，含代码引用（文件路径、commit、行号）

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-17T03:25:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-17T03:25:00Z"
---

# Research Outline: Multiproof 系统架构与链上组件分析

## Items

### item-1: Multiproof 设计哲学与多证明安全模型

确立 Multiproof 系统的整体设计哲学：为何选择 TEE + ZK 双证明路径而非单一 Fault Proof 或单一 ZK Rollup
路径；single-proof finality 模型（"TEE 或 ZK 任一证明即可 finalize；ZK 可挑战 TEE，反向不允许"）的安全
等价类划分；permissionless ZK override 在 Stage 2 标准下的角色；soundness alert（同类型双证冲突自动
作废）的设计目的。需要把"多证明 = 多客户端的证明侧类比"这一直觉形式化，并梳理 ZK 作为 over-write
机制对 TEE permissioned signer set 的去信任化贡献。

- **Priority**: high
- **Dependencies**: none

### item-2: AggregateVerifier 争议游戏核心合约

合约级分析 AggregateVerifier 作为 checkpoint 争议游戏入口的实现：proposal 提交、bond 锁定、双证明并行
接收、resolve 路径、与 OP Stack FaultDisputeGame 的同构 / 差异点。重点解读其状态机（INITIATED →
PROVED_BY_X → FINALIZED / CHALLENGED）、对子验证器的调用方式（immutable 地址 vs 通过 registry
查找）、intermediate output roots 的存储与争议范围收敛逻辑、以及不变量（如同一 proposal 同类型双证
矛盾时的 soundness 处置）。

- **Priority**: high
- **Dependencies**: item-1

### item-3: TEEVerifier 与 ZKVerifier 专用验证器子系统

分析两类专用验证器合约：TEEVerifier 验证 AWS Nitro Enclave attestation 与 enclave 签名 output root；
ZKVerifier 验证 ZK proof（推测使用 SP1 / RISC Zero 或类似栈，需以源码为准）的 verifying key 与
public inputs。需要刻画两者的 verify(...) 接口签名、proof payload 编码、可升级/不可升级策略（地址在
AggregateVerifier 中为何"永久固定"，是 immutable constructor arg 还是 registry pinned），以及
TEE 签名者集合维护（Prover Registrar 边界，详见 multiproof-provers-challengers）。

- **Priority**: high
- **Dependencies**: item-2

### item-4: DelayedWETH bond 托管与提款延迟优化

定位 DelayedWETH 在 Multiproof 体系中的角色：作为 proposer / challenger bond 的托管 ERC20-WETH 包装，
withdrawal delay 从旧 OP Stack（典型 7 天）降至 Azul 的 1 天。需要量化提款延迟的具体参数、推导
1 天延迟在新结算窗口下的安全充分性（最短双证 1 天 finality 与 bond 释放窗口的关系），分析 bond 大小、
slashing 路径与 challenger 经济激励，并明确"DelayedWETH 提款延迟"与"用户跨桥提款延迟"是两个独立
概念，避免与三条结算路径的 finality window 混淆。

- **Priority**: high
- **Dependencies**: item-2, item-6

### item-5: OptimismPortal2 与 AnchorStateRegistry 在 Azul 下的重构

分析 OptimismPortal2 与 AnchorStateRegistry 两个 OP Stack 上游合约在 Azul 中的改造：移除各自独立的
3.5 天 proof-maturity delay（旧版本中 proveWithdrawal → finalizeWithdrawal 的等待窗口），将 finality
判定权责集中到 AggregateVerifier。需要追踪新提款流程：用户在 L1 proveWithdrawal 后，何时可调用
finalizeWithdrawal、AnchorStateRegistry 如何对接 AggregateVerifier 的 resolve 结果作为新 anchor，
以及对依赖旧 portal/registry 接口的下游 bridge / messenger 兼容性影响。

- **Priority**: high
- **Dependencies**: item-2, item-6

### item-6: 三条结算路径与 finality window 机制

分别刻画三条结算路径在合约层的触发条件、计时器与可观察事件：(a) TEE only → 7 天（permissioned 单证
finality）；(b) ZK only → 7 天（permissionless 单证 finality，无需 TEE 参与）；(c) TEE + ZK 同时
就位且一致 → 1 天（fast finality）。需要从 AggregateVerifier 源码推导：finality 计时器自哪个事件
开始计、是否分路径独立计时、当一条路径已 finalize 后另一条迟到证据如何处理（含 ZK override 路径），
以及"ZK 永久 override permissioned TEE"在合约里如何体现。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

### item-7: 与旧版 Optimistic Fault-Proof 系统对比与 Stage 2 影响

构建新旧系统对比矩阵：旧版 OP Stack Fault Proof V2（FaultDisputeGame + AnchorStateRegistry + 3.5 天
proof-maturity + 7 天 withdrawal）vs Azul Multiproof（AggregateVerifier + TEEVerifier + ZKVerifier +
1 天 bond delay + 双证 1 天 / 单证 7 天 finality）。维度包括：信任假设、Prover 集合权限模型、争议范围
（block-level vs subgame bisection）、用户提款总等待、合约升级权限、紧急停止机制。在此基础上，按 L2Beat
Stage 2 标准（permissionless ZK proof + sufficient decentralization 等）评估 Multiproof 对 Stage 2
推进的贡献与剩余 gap。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4, item-5, item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| high_level_summary | 该 item 的 2-4 句 high-level 概括，作为最终章节首段素材 | all |
| contract_interface_and_state | 关键函数签名（external / public）、events、状态变量、storage slots、modifiers / access control | item-2, item-3, item-4, item-5 |
| proof_aggregation_and_dispute_logic | 多证明聚合的状态机、resolve / challenge / override 路径与 soundness 处置 | item-1, item-2, item-3, item-6 |
| finality_timer_and_parameters | finality / withdrawal 延迟的具体参数、计时起点、可配置项与默认值 | item-4, item-5, item-6 |
| bond_economics | bond 类型（WETH / DelayedWETH）、bond 大小、slashing 条件、对 challenger 经济激励的影响 | item-2, item-4 |
| security_assumptions_and_attack_surface | 信任假设（TEE attestation、ZK verifier key、Prover Registrar 边界）、已知 / 推测的攻击向量 | all |
| legacy_vs_azul_diff | 与上游 OP Stack（FaultDisputeGame、OptimismPortal2、AnchorStateRegistry、DelayedWETH）的字段级 / 参数级差异，附 commit / file 引用 | item-2, item-4, item-5, item-7 |
| governance_and_immutability | 升级权限（ProxyAdmin / Guardian / Safe）、immutable 字段、紧急停机机制（pause / blacklist） | item-2, item-3, item-4, item-5 |
| code_references | 代码引用：base/base 与 ethereum-optimism/optimism 仓库的文件路径、commit 短 hash、行号区间、永久链接 | all |
| on_chain_deployments | Sepolia / Mainnet 已知部署地址、constructor args、proxy → implementation 映射；若 Mainnet 未部署则注明 | item-2, item-3, item-4, item-5 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | Multiproof 系统整体架构图：标注 Proposer / Challenger 外部 actor、L1 上的 AggregateVerifier / TEEVerifier / ZKVerifier / DelayedWETH / OptimismPortal2 / AnchorStateRegistry 合约簇、以及它们之间的调用与数据流；旁注 off-chain Prover Registrar 边界 | mermaid | item-1, item-2, item-3, item-5 |
| diag-2 | sequence | AggregateVerifier proposal lifecycle 序列图：propose → TEE proof submit → (optional) ZK proof submit / challenge → resolve / finalize；包括对 TEEVerifier / ZKVerifier / DelayedWETH 的调用 | mermaid | item-2, item-3, item-6 |
| diag-3 | flow | 三条结算路径对比流程图：以决策节点（"TEE 已到达？" / "ZK 已到达？" / "两证一致？"）分支出 TEE-only 7d / ZK-only 7d / TEE+ZK 1d 三条路径，并标注 ZK override TEE 的回退分支 | mermaid | item-6 |
| diag-4 | comparison | 新旧 proof 系统差异对比图：左侧 OP Stack Fault Proof V2（FaultDisputeGame + 3.5d proof-maturity + 7d withdrawal）；右侧 Azul Multiproof（AggregateVerifier + 双证 1d / 单证 7d + 1d bond delay）；高亮被移除 / 新增 / 重命名的合约与参数 | mermaid | item-7 |
| diag-5 | hierarchy | 合约升级权限与依赖关系图：ProxyAdmin / Guardian / Safe / OptimismPortal2 / AnchorStateRegistry / AggregateVerifier / 子验证器 / DelayedWETH 间的 admin / dependency 边；标注 immutable 字段与升级路径 | mermaid | item-2, item-3, item-4, item-5 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | Base 官方 Azul Proof 规范与相关 sub-spec：specs.base.org/upgrades/azul/proofs 及子页（aggregate-verifier、tee-verifier、zk-verifier、delayed-weth 等如存在） | 3 |
| src-2 | code_analysis | base/base 合约源码：AggregateVerifier、TEEVerifier、ZKVerifier、DelayedWETH、OptimismPortal2、AnchorStateRegistry 实现文件，含 commit hash 与行号锚点 | 6 |
| src-3 | code_analysis | ethereum-optimism/optimism 上游合约源码（FaultDisputeGame、OptimismPortal2、AnchorStateRegistry、DelayedWETH 旧版）用于差异对比 | 4 |
| src-4 | audit_reports | Base Azul Immunefi 审计竞赛 scope、in-scope 合约清单、critical impacts 描述，以及 Azul 引入前任何相关 OP Stack 审计/Cantina 报告 | 1 |
| src-5 | expert_commentary | Stage 2 标准（L2Beat Stages framework）、Vitalik 关于 multiproof 的公开论述、reth / Kona 等客户端文档对证明子系统的引用 | 2 |
| src-6 | on_chain_data | Sepolia / Mainnet 上 AggregateVerifier、TEEVerifier、ZKVerifier、DelayedWETH 等合约的实际部署地址与 constructor args（若 Mainnet 尚未部署，记录 Sepolia 数据并注明） | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
