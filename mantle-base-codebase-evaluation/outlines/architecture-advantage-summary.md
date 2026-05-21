# Base Codebase 架构设计优势综述 — Structured Outline

**Project slug**: `mantle-base-codebase-evaluation`
**Topic slug**: `architecture-advantage-summary`
**Phase**: outline
**Round**: 1
**Branch**: `research/mantle-base-codebase-evaluation/architecture-advantage-summary`

---

## 1. Topic Analysis

### 1.1 Research Question

Base 在 Azul 升级中脱离 OP Stack 的架构设计变更有哪些？这些变更各自具有什么技术优势？Mantle 若参考或采纳这些架构改进，可获得哪些具体收益？

### 1.2 Scope

- Base 脱离 OP Stack 后的整体架构变更总览
- 执行层架构差异（Base Reth Fork vs OP Stack op-geth/op-node）
- Flashblocks 预确认与 Builder 分离架构
- Multiproof 安全架构（ZK + TEE 双重验证）
- Osaka EVM 变更（EIP-7825/7823/7883/7939/7951）
- Mantle 现状对照分析（Limb 已有 vs 需新增）
- 各架构变更的 Mantle 获益评估与优先级排名

### 1.3 Audience

Mantle 核心协议团队（需评估是否以及如何切换到 Base codebase）、架构决策者。

### 1.4 Expected Output

- 架构对照表（Base vs OP Stack 按组件分列）
- 各优势项描述及 Mantle 获益评估
- 架构先进性排名（按 Mantle 重要性/影响度）
- 引用 base-azul-upgrade 各 final section 的证据
- 两张 Mermaid 图（Base vs OP Stack 总览图、组件级架构差异映射图）

---

## 2. Outline Items

### Item 1: 整体架构变更总览 — Base 的 OP Stack 脱离路径

**Description**: 概述 Base Azul 升级作为首次脱离 OP Stack 的战略意义，描述 fork 的三层维度（代码 fork、规范 fork、治理 fork），以及对 OP Stack 生态的影响。

**Investigation Fields**:

| Field | Description | Source Type |
|-------|-------------|-------------|
| fork_dimensions | 代码 fork（yes）、规范 fork（partial）、治理 fork（no）的详细描述 | Primary evidence |
| strategic_goals | Azul 三大目标：安全/去中心化（Multiproof/Stage 2）、性能（单客户端）、DX（Osaka 对齐） | Primary evidence |
| op_stack_impact | 对 OP Stack 生态的影响：op-geth EOL（2026-05-31）、Base Stack 与 OP Stack 分叉后的兼容性 | Primary evidence |
| governance_alignment | 仍参与 Optimism Governance 和 Superchain 的关系 | Primary evidence |

**Source Requirements**:
- `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` — fork 维度分析、Base Stack vs OP Stack 对照表
- `base-azul-upgrade/research-sections/mantle-impact-assessment/final.md` — op-geth EOL 时间线

**Mantle Benefit Assessment Fields**:

| Field | Description |
|-------|-------------|
| relevance | Mantle 目前基于 op-geth/op-node 的 OP Stack 架构，面临同样的 op-geth EOL 压力 |
| adoption_path | 可选路径：跟随 OP Stack 迁移 op-reth，或直接采纳 Base codebase |

---

### Item 2: 执行层架构差异 — Base Reth Fork vs OP Stack

**Description**: 深入对比 Base 的单客户端架构（base-reth-node + base-consensus）与 OP Stack 传统的 op-geth + op-node 双组件架构，评估执行层统一带来的性能、可维护性和安全性优势。

**Investigation Fields**:

| Field | Description | Source Type |
|-------|-------------|-------------|
| base_architecture | base-reth-node（基于 paradigmxyz/reth v1.11.4）+ base-consensus（Kona-inspired derivation）单进程架构 | Primary evidence |
| op_stack_architecture | op-geth（EL）+ op-node（CL）双进程 JSON-RPC 通信架构 | Primary evidence |
| performance_gains | 消除进程间通信开销、共享内存池、统一状态管理 | Primary evidence / analysis |
| maintainability | 单代码库 vs 双代码库维护成本对比 | Analysis |
| engine_api_changes | Engine API V5 envelope + V4 payload、无 engine_newPayloadV5 | Primary evidence |
| eth69_protocol | eth/69 wire protocol（via reth v1.11.4 pin） | Primary evidence |

**Source Requirements**:
- `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` — 单客户端架构描述、Base Stack 组件表
- `base-azul-upgrade/research-sections/flashblocks-network-changes/final.md` — Engine API V5、eth/69、eth_config

**Mantle Benefit Assessment Fields**:

| Field | Description |
|-------|-------------|
| current_state | Mantle 使用 mantlenetworkio/op-geth@v1.4.2 + mantle-v2 op-node |
| migration_effort | 从双组件迁移到单客户端的工程量评估 |
| performance_gain | 消除 EL-CL JSON-RPC 瓶颈的延迟改善预估 |
| risk | 丧失客户端多样性（仅依赖 reth） |

---

### Item 3: Flashblocks 预确认与 Builder 分离

**Description**: 分析 Flashblocks 200ms 预确认架构的设计优势，包括 rollup-boost sidecar、Producer/Builder 分离、WebSocket 推送简化，以及 Azul 升级中的 payload 精简（移除 new_account_balances/receipts）。

**Investigation Fields**:

| Field | Description | Source Type |
|-------|-------------|-------------|
| pre_confirmation | 200ms 预确认机制、FlashblocksPayloadV1 结构 | Primary evidence |
| builder_separation | rollup-boost sidecar 架构、op-rbuilder builder 实现 | Primary evidence |
| azul_payload_changes | Azul 中移除 new_account_balances 和 receipts（#[skip_serializing_none]）、access_list 设为 None | Primary evidence |
| consumer_variants | 三种消费端实现：base/base（heavy reth 扩展）、op-reth flashblocks（reth-native）、flashblocks-rpc（thin overlay） | Primary evidence |
| spec_code_drift | wire format 差异（SSZ spec vs JSON code）、字段集不一致 | Primary evidence |
| p2p_status | builder-side P2P scaffolding 已实现、HA control messages 仅在 spec 中 | Primary evidence |

**Source Requirements**:
- `base-azul-upgrade/research-sections/flashblocks-network-changes/final.md` — Azul payload 变更、eth_config
- `base-azul-upgrade/research-sections/base-vs-optimism-flashblocks/final.md` — Producer/Builder/Consumer 对比、Mantle 推荐方案

**Mantle Benefit Assessment Fields**:

| Field | Description |
|-------|-------------|
| current_state | mantle-v2 v1.5.4 op-conductor 中有 Flashblocks plumbing（partially_live） |
| recommended_path | 推荐 option (b) op-reth flashblocks 最低成本路径 |
| ux_improvement | 200ms 预确认对 DeFi/交易用户体验的提升 |
| engineering_cost | 集成 rollup-boost sidecar 的工程量 |

---

### Item 4: Multiproof 安全架构 — ZK + TEE 双重验证

**Description**: 详细分析 Base 的 Multiproof 系统（AggregateVerifier + TEE + ZK 双证明），包括合约层和链下组件架构、PROOF_THRESHOLD=1 设计、三种结算路径、以及通往 Stage 2 的安全路线图。

**Investigation Fields**:

| Field | Description | Source Type |
|-------|-------------|-------------|
| aggregate_verifier | AggregateVerifier 合约（1041 行）、PROOF_THRESHOLD=1 常量 | Primary evidence |
| settlement_paths | TEE-only 7d、ZK-only 7d、TEE+ZK ≤1d（min 公式） | Primary evidence |
| tee_architecture | TEEVerifier + TEEProverRegistry + NitroEnclaveVerifier、AWS Nitro Enclave | Primary evidence |
| zk_architecture | ZKVerifier + SP1 adapter + Succinct gateway、Groth16 聚合 | Primary evidence |
| offchain_components | Proposer（UUID forward walk）、Challenger（4-way GameCategory）、TEE Prover（host/enclave split via vsock）、ZK Prover（gRPC + PostgreSQL）、Prover Registrar | Primary evidence |
| portal_changes | OptimismPortal2: PROOF_MATURITY_DELAY=0、AnchorStateRegistry: disputeGameFinalityDelay=0 | Primary evidence |
| delayed_weth | DelayedWETH 1-day delay bond escrow | Primary evidence |
| stage2_path | 从 Stage 1 到 Stage 2 的路线图 | Analysis |

**Source Requirements**:
- `base-azul-upgrade/research-sections/multiproof-architecture/final.md` — 合约层架构、结算路径、PROOF_THRESHOLD
- `base-azul-upgrade/research-sections/multiproof-provers-challengers/final.md` — 链下组件（Proposer/Challenger/TEE Prover/ZK Prover/Registrar）

**Mantle Benefit Assessment Fields**:

| Field | Description |
|-------|-------------|
| current_state | Mantle 已有 OP Succinct SP1 ZK prover（partially_live），无 TEE 验证 |
| security_uplift | 双证明模型 vs 单证明的安全性提升（TEE+ZK 互补、加速最终性 7d→≤1d） |
| finality_improvement | 快速最终性 min(createdAt+7d, secondProofAt+1d) 对桥接和 DeFi 的价值 |
| implementation_complexity | TEEProverRegistry + NitroEnclaveVerifier 部署复杂度 |

---

### Item 5: Osaka EVM 变更

**Description**: 分析 Base Azul 引入的 Osaka EVM 变更（5 个 EIP），评估每个变更的技术意义及 Mantle 的当前采纳状态。

**Investigation Fields**:

| Field | Description | Source Type |
|-------|-------------|-------------|
| eip_7825 | Tx gas cap 2^24（deposit tx 豁免、state_transition.go 中 `!IsOptimism()` guard） | Primary evidence |
| eip_7823 | MODEXP 1024-byte input cap | Primary evidence |
| eip_7883 | MODEXP gas 增加（min 200→500、multiplier 8→16、remove /3 divisor） | Primary evidence |
| eip_7939 | CLZ opcode 0x1e, gas 5 | Primary evidence |
| eip_7951 | P256VERIFY gas 3450→6900 | Primary evidence |
| activation_mechanism | BaseUpgrade::Azul => SpecId::OSAKA 单一切换 | Primary evidence |

**Source Requirements**:
- `base-azul-upgrade/research-sections/osaka-evm-changes/final.md` — 5 个 EIP 的完整分析
- `base-azul-upgrade/research-sections/mantle-impact-assessment/final.md` — Mantle 已采纳状态（Limb 已有 4/5）

**Mantle Benefit Assessment Fields**:

| Field | Description |
|-------|-------------|
| already_adopted | Mantle Limb 已采纳：EIP-7823、7883、7939、7951 |
| not_adopted | EIP-7825 未采纳（通过 `!IsOptimism()` guard 主动排除） |
| gap_analysis | 仅 EIP-7825 为差距项，需评估是否采纳 |

---

### Item 6: Mantle 现状对照分析 — 13 项特性矩阵

**Description**: 基于 mantle-impact-assessment 的 13×7 特性矩阵，全面对比 Base Azul 与 Mantle 当前实现状态，识别差距项和 BREAK-CHANGE 项。

**Investigation Fields**:

| Field | Description | Source Type |
|-------|-------------|-------------|
| feature_matrix | 13 项特性的完整对比（live/partially_live/not_live） | Primary evidence |
| already_live | 6/13 features 已通过 Mantle Limb 上线 | Primary evidence |
| partially_live | Flashblocks plumbing、ZK Prover（OP Succinct SP1） | Primary evidence |
| not_live | 需新增的特性项 | Primary evidence |
| break_changes | 4 个 BREAK-CHANGE 项识别 | Primary evidence |
| mantle_fork_chain | BaseFee → Everest → Euboea → Skadi → Limb → Arsia 升级路线 | Primary evidence |
| code_anchors | op-geth@v1.4.2 (9c428cf)、mantle-v2@v1.5.4 (fccacf5b) | Primary evidence |

**Source Requirements**:
- `base-azul-upgrade/research-sections/mantle-impact-assessment/final.md` — 完整特性矩阵、BREAK-CHANGE 分析

**Mantle Benefit Assessment Fields**:

| Field | Description |
|-------|-------------|
| adoption_gap | 需弥合的 7/13 特性差距 |
| break_change_risk | 4 个 BREAK-CHANGE 的迁移风险评估 |
| timeline_pressure | op-geth EOL 2026-05-31 带来的时间压力 |

---

### Item 7: 架构优势排名与获益评估总结

**Description**: 综合前 6 项分析，按 Mantle 重要性/影响度对各架构变更进行排名，给出采纳优先级建议和总体评估结论。

**Investigation Fields**:

| Field | Description | Source Type |
|-------|-------------|-------------|
| ranking_criteria | 排名维度：安全性提升、性能改善、工程成本、时间紧迫性、生态对齐 | Analysis |
| priority_ranking | 各架构变更的优先级排名（综合评分） | Synthesis |
| adoption_strategy | 渐进式采纳 vs 全面切换的策略分析 | Synthesis |
| risk_assessment | 总体风险评估：客户端多样性丧失、fork 维护成本、与 OP Stack 生态脱钩 | Analysis |
| timeline_recommendation | 建议时间表（考虑 op-geth EOL） | Synthesis |

**Source Requirements**:
- 所有前述 evidence sources 的综合
- `base-azul-upgrade/research-sections/mantle-impact-assessment/final.md` — BREAK-CHANGE 和时间线

**Mantle Benefit Assessment Fields**:

| Field | Description |
|-------|-------------|
| top_benefits | 排名前 3 的最高价值架构改进 |
| quick_wins | 低成本高收益的可快速采纳项 |
| strategic_decision | 是否切换到 Base codebase 的战略判断依据 |

---

## 3. Diagram Expectations

### Diagram 1: Base vs OP Stack 总览架构图

**Type**: Mermaid flowchart (LR)
**Purpose**: 并列展示 Base Stack 和 OP Stack 的整体架构，突出关键差异点。

**Expected Elements**:
- 左侧：OP Stack 架构（op-geth EL + op-node CL + op-batcher + op-proposer + DisputeGame）
- 右侧：Base Stack 架构（base-reth-node + base-consensus + rollup-boost + Multiproof AggregateVerifier）
- 连接线标注关键差异（单进程 vs 双进程、Flashblocks、Multiproof vs DisputeGame）
- 颜色区分：共享组件（绿）、Base 独有（蓝）、OP Stack 独有（灰）

**Source**: `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` 中的 Base Stack vs OP Stack 对照表

### Diagram 2: 组件级架构差异映射图

**Type**: Mermaid flowchart (TB)
**Purpose**: 按功能层（执行层、共识层、结算层、数据可用性层）映射 Base 与 OP Stack 的组件级差异。

**Expected Elements**:
- 四层横向分组：Execution / Consensus / Settlement / Data Availability
- 每层内展示 OP Stack 组件 → Base 替代组件的映射关系
- 标注迁移方向箭头（op-geth → base-reth-node, op-node → base-consensus 等）
- 标注 Mantle 当前位置（与 OP Stack 或 Base 的对齐状态）

**Source**: 综合 base-strategy-azul-overview、flashblocks-network-changes、multiproof-architecture

---

## 4. Source Requirements

### Primary Evidence Sources (from base-azul-upgrade project)

| # | Source Path | Items Covered | Key Data Points |
|---|-----------|---------------|-----------------|
| 1 | `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` | Items 1, 2 | Fork 三层维度、Base Stack 组件表、Azul 三大目标、5 张 Mermaid 图 |
| 2 | `base-azul-upgrade/research-sections/mantle-impact-assessment/final.md` | Items 1, 5, 6 | 13×7 特性矩阵、6/13 已 live、4 BREAK-CHANGE、op-geth EOL 时间线 |
| 3 | `base-azul-upgrade/research-sections/flashblocks-network-changes/final.md` | Items 2, 3 | Azul payload 精简、Engine API V5、eth/69、eth_config |
| 4 | `base-azul-upgrade/research-sections/base-vs-optimism-flashblocks/final.md` | Item 3 | Producer/Builder/Consumer 对比、3 种消费端、Mantle 推荐 option (b) |
| 5 | `base-azul-upgrade/research-sections/multiproof-architecture/final.md` | Item 4 | AggregateVerifier 1041 行、PROOF_THRESHOLD=1、三种结算路径 |
| 6 | `base-azul-upgrade/research-sections/multiproof-provers-challengers/final.md` | Item 4 | 5 个链下组件、TEE host/enclave split、ZK gRPC + Groth16 |
| 7 | `base-azul-upgrade/research-sections/osaka-evm-changes/final.md` | Item 5 | 5 个 EIP 完整分析、BaseUpgrade::Azul => SpecId::OSAKA |

### Cross-Reference Requirements

- Item 7（排名与评估）需要综合所有 7 个 primary sources
- Diagram 1 和 Diagram 2 需要综合 sources 1, 3, 5
- Mantle 获益评估字段需要 source 2（mantle-impact-assessment）作为基准

---

## 5. Architecture Comparison Table (Draft Structure)

将在 deep draft 阶段填充的对照表框架：

| Component Category | OP Stack | Base Stack (Azul) | Key Difference | Mantle Status |
|-------------------|----------|-------------------|----------------|---------------|
| Execution Client | op-geth | base-reth-node (reth v1.11.4 fork) | Rust single-binary vs Go EL | op-geth v1.4.2 |
| Consensus / Derivation | op-node | base-consensus (Kona-inspired) | Embedded in EL vs separate CL | mantle-v2 op-node |
| Pre-confirmation | N/A (standard 2s blocks) | Flashblocks (200ms) | rollup-boost sidecar | Partially plumbed |
| Block Building | Sequencer-integrated | op-rbuilder (separated) | PBS-style separation | Not separated |
| Fault Proof | DisputeGame (single proof) | Multiproof AggregateVerifier | TEE+ZK dual proof | OP Succinct SP1 (partial) |
| Settlement Finality | 7-day challenge period | min(7d, secondProof+1d) | Fast finality with dual proof | 7-day standard |
| EVM Version | Varies by fork | Osaka (5 EIPs) | Single SpecId switch | 4/5 EIPs via Limb |
| Wire Protocol | eth/68 | eth/69 (via reth pin) | Protocol upgrade | eth/68 |
| Engine API | V3 | V5 envelope + V4 payload | Extended for Flashblocks | V3 |
| Bond Escrow | Standard WETH | DelayedWETH (1d delay) | Enhanced security | Standard |

---

## 6. Architecture Advancement Ranking (Draft Framework)

将在 deep draft 阶段基于以下维度评分：

| Rank | Architecture Change | Security | Performance | Engineering Cost | Urgency | Ecosystem Alignment | Overall Score |
|------|-------------------|----------|-------------|-----------------|---------|---------------------|---------------|
| - | Multiproof (TEE+ZK) | TBD | TBD | TBD | TBD | TBD | TBD |
| - | Single Client (reth) | TBD | TBD | TBD | TBD | TBD | TBD |
| - | Flashblocks (200ms) | TBD | TBD | TBD | TBD | TBD | TBD |
| - | Osaka EVM | TBD | TBD | TBD | TBD | TBD | TBD |
| - | Engine API V5 / eth/69 | TBD | TBD | TBD | TBD | TBD | TBD |

Scoring: 1-5 per dimension, weighted by Mantle priority.

---

## 7. Quality Checklist

- [ ] All 7 outline items have defined investigation fields
- [ ] All items have source requirements pointing to specific evidence files
- [ ] All items include Mantle benefit assessment fields
- [ ] Two diagram expectations are fully specified with elements, type, and sources
- [ ] Architecture comparison table framework covers all major component categories
- [ ] Ranking framework defines clear scoring dimensions
- [ ] Outline is independently reviewable by adversarial agent
- [ ] No Linear IDs used as slugs
- [ ] All source paths are valid and reference existing final.md files
