---
topic: "Base 脱离 OP Stack 战略分析与 Azul 升级总览"
project_slug: base-azul-upgrade
topic_slug: base-strategy-azul-overview
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: base-azul-upgrade/outlines/base-strategy-azul-overview.md
  draft: base-azul-upgrade/research-sections/base-strategy-azul-overview/drafts/round-{n}.md
  final: base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md
  index: base-azul-upgrade/research-sections/_index.md

scope: |
  从 high level 分析 Base 宣布脱离 OP Stack 独立维护 codebase 的战略背景，并梳理 Azul 作为 Base 独立后
  首次 hardfork 的完整升级内容。聚焦三大设计目标（Multiproof 安全与去中心化、单客户端性能优化、
  Ethereum Osaka 对齐的开发者体验），覆盖 feature 全景、客户端架构变更与激活时间线，为
  osaka-evm-changes / multiproof-architecture / flashblocks-network-changes 等下游研究建立全局认知框架。
audience: |
  Base / OP Stack 生态研究者、Multica 研究 squad 内部下游 Research Agent、关注 L2 Stage 2 进展的协议工程师与投资分析师。
  阅读者熟悉 Rollup 基本概念，但不一定了解 Azul 内部细节或 base-reth-node 客户端架构。
expected_output: |
  - Base 战略分析文档：脱离 OP Stack 的动机、对 Superchain 生态的影响、Base Stack vs OP Stack 的定位差异
  - Azul 升级完整 feature 清单与分类表（执行层 EIP / Proof 系统 / Flashblocks / 网络协议 / 客户端）
  - 各 feature 的 high-level 技术描述与三大目标（安全去中心化 / 性能 / DX）的映射
  - 客户端架构变更说明（base-reth-node + base-consensus 单客户端路线）
  - Sepolia / Mainnet 激活时间线与下游研究主题的依赖图
  - 至少 3 张 Mermaid 架构/对比/时间线图

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-17T02:00:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-17T02:00:00Z"
---

# Research Outline: Base 脱离 OP Stack 战略分析与 Azul 升级总览

## Items

### item-1: Base 脱离 OP Stack 的战略动机与背景

调查 Base 在 Azul 升级中宣布以 base-reth-node + base-consensus 为唯一支持客户端、事实上脱离 OP Stack
公共 codebase 的战略动机。需要厘清官方公开叙事（"consolidating onto a streamlined Base stack"、
更快的发版节奏、协议简化）与可观察事实（不再维护 op-geth/op-node 上游兼容、自有客户端发版周期、
Stage 2 路线对独立性的要求）之间的关系，并评估这一决定对 Superchain 共享互操作性叙事的张力。

- **Priority**: high
- **Dependencies**: none

### item-2: Base Stack vs OP Stack 的架构与定位差异

对比 Base Stack（base-reth-node + base-consensus + Multiproof + Flashblocks）与同期 OP Stack
（op-node、op-geth/op-reth、Fault Proofs、Interop）在执行层客户端策略、共识层（derivation）、
证明系统、Sequencer 与 PreConf 子系统、升级治理与发版节奏维度的定位差异。区分"代码 fork 关系"、
"规范 fork 关系"与"治理边界"三层次，避免把工程实现差异误读为战略分裂。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Azul 升级三大设计目标与全局设计哲学

提炼 Azul 公开宣传的三大目标：(a) 安全与去中心化（Multiproof 推进 Stage 2）、(b) 性能（向 1 gigagas/s
吞吐与 Flashblocks 演进的客户端整合）、(c) 开发者体验（与 Ethereum Osaka 对齐）。需要将每一目标的
设计哲学（去中心化与活性的权衡、降低执行层延迟与状态膨胀、与 L1 EVM 同步以减少跨链应用碎片化）
形式化，作为后续 feature 分类与目标映射的判定基准。

- **Priority**: high
- **Dependencies**: item-1

### item-4: Azul 完整 Feature 清单、分类与目标映射

按"执行层 EIP / 共识与网络协议 / Proof 系统 / Flashblocks / 客户端" 五大类，整理 Azul 包含的全部
feature 与对应的官方规范位置；每条 feature 标注：所属 sub-spec、影响层（EL/CL/网络/合约）、对应的三大
目标（安全 / 性能 / DX）。当前已知清单包含 EIP-7823、EIP-7825、EIP-7883、EIP-7939、EIP-7951
（secp256r1 precompile 重新计价）、EIP-7642（eth/69）、EIP-7910（eth_config RPC）、Flashblocks payload
精简（移除账户余额与 receipts）、Multiproof（TEE + ZK）、以及 base-reth-node / base-consensus 单客户端
化。该清单需以 Base Spec /upgrades/azul/overview 与 base 仓库实际 PR 为准做交叉校验。

- **Priority**: high
- **Dependencies**: item-3

### item-5: Multiproof 系统 high-level 架构与提款加速

在不进入合约/Prover 实现细节的前提下，描述 Multiproof 系统的 high-level 架构：TEE Prover 与 ZK Prover
并行运行、Prover Registrar 注册者、Proposer/Challenger 角色、双证明共识下的提款加速逻辑（"both
agree → 1 天提款"，"ZK 永久 override 权限化 TEE"）。重点阐释 Stage 2 视角下，为何这一架构同时
提升安全（链上可验证 Fault Proof）与去中心化（permissionless ZK 证明），以及为下游 multiproof-architecture
与 multiproof-provers-challengers 研究划清边界。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: 单客户端路线：base-reth-node + base-consensus

分析 Base 仅支持 base-reth-node（执行）+ base-consensus（共识，基于 Kona）作为 Azul hardfork 唯一客户端
的决定：客户端来源（reth fork + Kona fork）、与 OP Stack 多客户端（op-node、op-geth、op-reth、op-besu 等）
策略的本质区别、性能动机（向 1 gigagas/s 推进、未来 single binary 整合）、以及对客户端多样性 / 单点
风险的权衡。需要从 high level 描述运营者的迁移路径与回滚边界，不替代后续 client-architecture 子课题。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-7: Ethereum Osaka 对齐：EIP 选择逻辑与开发者影响

阐释 Base 在 Azul 中选择对齐的 Osaka EIP 集合（EIP-7823 Upper-Bound MODEXP、EIP-7825 Transaction Gas
Limit Cap、EIP-7883 MODEXP Gas Cost Increase、EIP-7939 CLZ Opcode、EIP-7951 secp256r1 Precompile
计价、EIP-7642 eth/69、EIP-7910 eth_config）背后的选择逻辑：保留与 L1 EVM 等价性、降低跨链应用碎片化、
为 ZK Prover 友好性铺路（MODEXP、CLZ、secp256r1）、以及 P2P 与 RPC 层的标准化。识别明确排除/延后的
Osaka EIP（若有），并解释原因。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-8: Azul 激活时间线、迁移路径与 Superchain / Mantle 生态影响

整理 Azul 的关键时间节点（Sepolia: 1776708000 / 2026-04-20 18:00 UTC、Audit Competition: 2026-04-21–05-04、
Base Vibenet: 2026-05 中、Mainnet: 截止本研究为 TBD，需以 base/base 仓库与官方公告交叉校验）、运营者
迁移路径（升级 op-node/op-geth → base-consensus + base-reth-node）以及对依赖 OP Stack 升级路径的下游
项目（如 Mantle 等 OP Stack fork、Superchain interop 路线）的 high-level 影响判断。不进入具体影响评估
（由 mantle-impact-assessment 等子课题接手），只建立全局认知。

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-4, item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| high_level_summary | 该 item 的 2-4 句 high-level 概括，作为最终章节首段素材 | all |
| design_motivation | 设计/决策背后的动机与目标对齐（含官方叙事 vs 可观察事实的对照） | all |
| target_goal_mapping | 该 item 对应 Azul 三大目标（安全去中心化 / 性能 / DX）的映射与权重 | item-3, item-4, item-5, item-6, item-7 |
| comparison_to_op_stack | 与上游 OP Stack（op-node、op-geth、Fault Proofs、Interop 等）的差异点 | item-1, item-2, item-6, item-7, item-8 |
| key_artifacts_and_specs | 关键 spec 路径、PR/commit、EIP 编号与永久链接，便于下游 deep-draft 引用 | all |
| risks_open_questions | High-level 风险、开放问题、与官方叙事冲突或证据不足之处 | all |
| cross_topic_dependencies | 与下游子课题（osaka-evm-changes、multiproof-architecture、multiproof-provers-challengers、flashblocks-network-changes、mantle-impact-assessment）的边界与依赖 | all |
| activation_timeline_relevance | 与 Sepolia/Mainnet 激活节点、迁移窗口的相关性 | item-3, item-4, item-6, item-8 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | comparison | Base Stack vs OP Stack 架构对比图：左侧 base-reth-node + base-consensus + Multiproof + Flashblocks；右侧 op-node + op-geth/op-reth + Fault Proofs + Interop；高亮 fork 边界与共享上游（reth、Kona） | mermaid | item-2 |
| diag-2 | hierarchy | Azul Feature 分类与三大目标依赖图：以 Azul 为根，分支为 EL EIPs / CL & 网络 / Proof 系统 / Flashblocks / 客户端；每个叶子节点标注其服务的目标（安全 / 性能 / DX） | mermaid | item-3, item-4 |
| diag-3 | architecture | Multiproof 系统 high-level 架构图：包含 Proposer、Challenger、TEE Prover、ZK Prover、Prover Registrar、L1 settlement 合约，以及"双证一致 → 1 天提款 / ZK override TEE"的逻辑流 | mermaid | item-5 |
| diag-4 | architecture | 单客户端路线示意图：base-reth-node（EL，源于 reth）+ base-consensus（CL，源于 Kona）+ 未来 single-binary 整合方向；与 OP Stack 多客户端集合的对照 | mermaid | item-6 |
| diag-5 | timeline | Azul 激活与生态时间线：Sepolia 激活、Audit Competition、Vibenet、Mainnet TBD、与 Ethereum Osaka mainnet 节点的相对位置；标注下游研究主题在时间轴上的关注窗口 | mermaid | item-3, item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | Base 官方文档与 Spec：blog.base.dev/introducing-base-azul、specs.base.org/upgrades/azul/overview 及其全部子页面（multi-proof、provers、flashblocks 等） | 5 |
| src-2 | code_analysis | Base 与 OP Stack 代码仓：github.com/base/base（Azul 相关 PR / hardfork 配置 / 客户端 README）、github.com/ethereum-optimism/optimism（用于交叉校验差异） | 2 |
| src-3 | eip_specs | 对齐的 Ethereum Osaka EIP 原文：EIP-7823、EIP-7825、EIP-7883、EIP-7939、EIP-7951、EIP-7642、EIP-7910（eips.ethereum.org 永久链接） | 7 |
| src-4 | expert_commentary | Stage 2 / Multiproof / 客户端多样性背景：L2Beat Stage 定义、reth & Kona 项目文档、相关 Ethereum Magicians / ethresearch 帖子 | 2 |
| src-5 | governance_proposals | 与升级激活、Superchain 治理相关的公开提案或 Optimism Foundation 公告（用于补充脱离 OP Stack 的治理侧叙事） | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
