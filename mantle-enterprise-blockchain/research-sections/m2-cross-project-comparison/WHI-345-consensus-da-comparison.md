# WHI-345: 横向对比 — 共识、结算与数据可用性方案对比

> **Issue**: WHI-345 — 横向对比：共识、结算与数据可用性方案对比
> **Milestone**: M2: Horizontal Comparisons
> **Date**: 2026-05-06
> **Status**: In Review
> **Prerequisites**: M1 deep-dive research (WHI-334 through WHI-341) — all complete
> **Scope**: Canton, zkSync Prividium, Tempo L1, Tempo Zones (L2), Mantle (baseline)
>
> **Review note (2026-05-10)**: 原始 issue 描述和初稿将 Mantle 视为“默认 7 天 Optimistic Rollup”。但 `WHI-341` 已明确：自 **2025-09-16** 起 Mantle 默认验证路径为 **OP Succinct SP1 validity proof**，自 **2026-04-22** 起 DA 为纯 **Ethereum blobs/calldata**。因此本文将“7 天挑战期”视为 **optimistic fallback 模式**，而非当前默认路径。

---

## 目录

1. [共识机制横向对比矩阵](#1-共识机制横向对比矩阵)
2. [结算模型对比分析](#2-结算模型对比分析)
3. [数据可用性对比矩阵](#3-数据可用性对比矩阵)
4. [企业终局性需求分析](#4-企业终局性需求分析)
5. [Mantle 共识/结算/DA 架构建议](#5-mantle-共识结算da-架构建议)

---

## 1. 共识机制横向对比矩阵

### 1.1 完整对比矩阵

| 维度 | Canton | Prividium | Tempo (L1) | Tempo Zones (L2) | Mantle (baseline) |
|------|--------|-----------|------------|-------------------|-------------------|
| **共识类型** | 2PC + BFT Sequencer | 中心化 Sequencer | Commonware Simplex BFT | 无共识（NoopConsensus，单 Sequencer 驱动） | 中心化 Sequencer（OP Stack） |
| **拜占庭容错** | 是（Mediator 层阈值投票 + Sequencer BFT 排序） | 否（单一 Sequencer） | 是（BLS12-381 阈值签名，2/3 诚实假设） | 否（信任单一 Sequencer） | 否（单一 Sequencer） |
| **终局性类型** | 确定性即时终局 | 链内即时（~1s）→ L1 数学验证终局（分钟级） | 确定性即时终局（亚秒级 BFT） | 即时终局（head=safe=finalized，继承 L1 排序） | 软终局（~2s Sequencer）→ safe finality（~12min）→ 默认 ZK 数学终局（~1h）；可切回 7 天 optimistic fallback |
| **终局性时间** | 秒级（2PC 完成即终局） | 链内 ~1 秒；到以太坊 L1 ~数分钟到十数分钟 | 亚秒级（~600ms） | 与 L1 出块同步（每个 L1 块产生一个 L2 块） | 软终局 ~2s；safe ~12min；ZK 终局 ~1h（fallback 模式 7 天） |
| **活性假设** | 相关 Synchronizer 在线 + Participant 可达 | Sequencer 在线 | 2/3 验证者在线 | Sequencer 在线 + L1 在线 | Sequencer 在线 + SP1 Prover/Output Submitter 在线（默认 ZK 模式） |
| **抗审查能力** | 中等（多 Synchronizer 可选 + Global Synchronizer 兜底） | 低（单一 Sequencer + TransactionFilterer 限制 L1 强制交易） | 高（BFT 多验证者 + VRF leader 选举） | 低（单一 Sequencer 控制出块） | 低（L1 强制包含存在，但最大延迟约 ~12 小时） |
| **排序机制** | Sequencer 分配批次时间戳（加密 blob 排序，不可见交易内容） | Sequencer 排序（可见交易内容） | Commonware Simplex BFT 全局排序（VRF leader 提议） | L1 事件驱动（ZoneEngine 从 L1 块提取 deposit 事件触发出块） | Sequencer 排序（可见交易内容） |
| **出块方式** | 无区块概念——单笔交易独立提交和确认 | 传统区块打包 | BFT 区块（带 Payment Lane 三通道 gas 分配） | 每个 L1 块生成一个 Zone 块（1:1 映射） | 传统区块打包（2 秒出块） |
| **MEV 风险** | 从架构上消除（Sequencer 无法读取交易内容） | 运营商可控（私有链内部 MEV 由运营商策略管理） | 由 BFT 协议和 VRF leader 选举缓解 | 由 Sequencer 控制（合规场景下非风险） | 存在（中心化 Sequencer 可提取 MEV） |

**数据来源**:
- Canton: WHI-335 §3.1–3.4（2PC 提交流程、BFT Sequencer 安全假设、终局性保证）；WHI-336 §2.2（Mediator 2PC 实现、ResponseAggregation quorum 机制）
- Prividium: WHI-337 §3.2（ZK 证明系统）；WHI-338 §2.3（完整 ZK 证明流程，端到端时间线）
- Tempo L1: WHI-339 §4（Commonware Simplex BFT 共识细节）；WHI-340 §2.2（TempoConsensus、Commonware 集成、双 runtime 设计）
- Tempo Zones: WHI-340 §3.1–3.2（NoopConsensus、ZoneEngine L1 事件驱动出块、instant finality 代码确认）
- Mantle: WHI-341 §4.1–4.2（OP Succinct ZK 终局与 optimistic fallback）；§7.2.4（L1 强制包含延迟）；§8.1（企业终局性评估）

### 1.2 共识架构深度解析

#### 1.2.1 Canton: 2PC + BFT 混合体（更接近分布式数据库协调）

Canton 的共识机制**不是传统区块链共识**，而是将共识分解为两个独立关注点：

1. **消息排序（Sequencer）**：BFT 排序层对加密消息进行全局排序。Sequencer **看不到交易内容**（仅处理加密 blob + 收件人列表 + 时间戳），从架构上消除 MEV。支持可插拔后端（Canton 原生 BFT / Ethereum / Fabric / 数据库）。
   > *Source: WHI-335 §1.2 — "Sequencer 处理排序但看不到内容"*
   > *Source: WHI-336 §2.2.1 — SequencerDriver trait 定义了 send/subscribe/acknowledge 接口，开源代码仅有 reference driver（DB-backed），BFT orderer 可能在企业版*

2. **交易确认（Mediator 2PC）**：Mediator 收集 Participant 的确认/拒绝信号，通过 quorum 阈值投票出具裁决。**所有** confirmer 同意 → APPROVE；任何一方拒绝或超时 → REJECT。这是典型的 2PC 语义，不同于 BFT 的多数投票。
   > *Source: WHI-336 §2.2.2 — ConfirmationRequestAndResponseProcessor 代码确认 2PC 流程；ResponseAggregation 使用 Quorum 机制*

**关键判断**：Canton 更接近**分布式数据库 2PC 协调协议**而非区块链共识。理由：无区块概念、只有利益相关方参与确认、任何一方拒绝即回滚、无概率性终局。但 Sequencer 层的 BFT 排序超越了传统 2PC。
> *Source: WHI-335 §3.3 — "Canton 更接近 2PC 而非区块链共识" 的 5 条论证*

#### 1.2.2 Prividium: 中心化排序 + ZK 数学验证

Prividium 的共识极其简洁：单一中心化 Sequencer 排序执行交易，ZK 证明系统保证执行正确性。

- Sequencer 接收经 Proxy RPC 验证的交易，排序并执行，更新本地状态（PostgreSQL）
- Airbender RISC-V Prover（GPU 加速）生成 STARK 证明（亚秒级）
- 证明经 ZKsync Gateway 提交至以太坊 L1 链上验证
- **共识安全性来源于数学（STARK 证明 soundness）而非节点投票**

> *Source: WHI-338 §2.3 — 完整 ZK 证明流程四阶段图解*
> *Source: WHI-337 §3.2 — "无需可信设置（Trusted Setup-free）…量子安全"*

#### 1.2.3 Tempo L1: Commonware Simplex BFT

Tempo L1 采用由 Commonware 提供的 Simplex BFT 共识：

- **BLS12-381 阈值签名**：DKG 仪式生成共享密钥，验证者对区块进行阈值签名
- **VRF leader 选举**：每轮随机选择 leader 提议区块，减少可预测性
- **双 runtime 隔离**：Reth 执行和 Commonware 共识运行在独立 Tokio runtime 上，防止执行负载影响共识性能
- **亚秒级终局**：BFT 确认后即终局，不可逆

> *Source: WHI-340 §2.2 — "dual-runtime design"*
> *Source: WHI-339 §4 — Commonware Simplex BFT 共识详细说明*

#### 1.2.4 Tempo Zones: 零共识 + L1 事件驱动

Zones 明确使用 `NoopConsensus`（无 P2P 共识），因为 Zone 是**单 Sequencer Validium**：

- ZoneEngine 监听 L1 区块事件（DepositMade、EncryptedDepositMade、TokenEnabled 等）
- 每个 L1 块触发精确一个 Zone 块的构建（1:1 映射）
- Zone 块时间戳锁定为 L1 块的时间戳
- `head = safe = finalized`（代码确认，`ForkchoiceState::same_hash()`）

> *Source: WHI-340 §3.2 — ZoneEngine advance() 方法详解；§3.1 — "NoopConsensus + NoopNetworkBuilder — Why No P2P?"*

#### 1.2.5 Mantle: 中心化 Sequencer + ZK Validity Settlement

Mantle 在**排序/执行层**仍是标准 OP Stack 的单 Sequencer 架构，但在**最终结算层**已经不是原始框架里假设的“纯 Optimistic Rollup”：

- 单一 Sequencer（op-node sequencer mode）排序交易
- op-geth 通过 Engine API 执行
- op-batcher 将批次提交至以太坊 L1 blobs/calldata，任何人可从 L1 重构完整 L2 状态
- 默认由外部 **SP1 Prover + OP Succinct Output Submitter** 向 `OPSuccinctL2OutputOracle` 提交 validity proof；验证通过后进入约 **~1 小时** 的可提款终局
- `MantleSecurityMultisig` 可将系统切换到 optimistic fallback；**仅在 fallback 模式下**才恢复 7 天挑战期
- op-conductor 提供 HA 故障转移（Raft leader 选举），但同一时刻仍只有一个 active Sequencer

**关键判断**：Mantle 的共识层仍是中心化 Sequencer，但其默认**结算安全模型**已更接近 Prividium 的 proof-based model，而不是传统 optimistic rollup。Mantle 当前的短板不再是“没有数学终局”，而是：(1) 软终局仍依赖 Sequencer，(2) 默认 ZK 终局仍有约 ~1 小时延迟，(3) 治理层可以切回 optimistic fallback。

> *Source: WHI-341 §4.1–4.2；§8.1, §8.3*

---

## 2. 结算模型对比分析

### 2.1 结算模型矩阵

| 维度 | Canton | Prividium | Tempo (L1) | Tempo Zones (L2) | Mantle (baseline) |
|------|--------|-----------|------------|-------------------|-------------------|
| **结算层** | Synchronizer 内部（可选锚定以太坊） | 以太坊 L1（经 ZKsync Gateway） | 独立 L1（Commonware BFT 自身终局） | Tempo L1（经 ZonePortal 合约） | 以太坊 L1 |
| **结算保证类型** | 协议信任（2PC + BFT） | 数学保证（STARK 证明 + 以太坊验证） | BFT 信任（2/3 验证者签名） | L1 提交保证（批次锚定 + validity proof 目标） | 数学保证（默认 SP1 validity proof + Ethereum 验证；治理上保留 optimistic fallback） |
| **结算到外部 L1** | 可选（Ethereum 后端作为 Sequencer） | 必需（以太坊是结算层） | 无（独立 L1 自终局） | 必需（锚定 Tempo L1） | 必需（以太坊是结算层） |
| **结算时间** | 秒级（域内终局） | 链内 ~1s；到以太坊 ~数分钟到十数分钟 | 亚秒级 | 与 L1 出块同步 + 批次提交延迟 | 软终局 ~2s；safe ~12min；ZK 终局 ~1h（fallback 模式 7 天） |
| **Validity Proof** | 无（2PC 确认即终局） | STARK 证明（已部署） | 无（BFT 签名即终局） | 架构已准备，当前提交空证明（v0.1.0） | SP1 zkVM validity proof 已部署（默认）；fallback 模式无需 proof |
| **逃生舱机制** | 无全局状态可逃生（各方自持数据） | 受限（TransactionFilterer 限制 L1 强制交易） | N/A（独立 L1） | 依赖 Sequencer 提供数据 | L1 强制包含（最大延迟约 ~12h）；withdrawal 依赖已验证 output root |

**数据来源**:
- Canton: WHI-335 §3.4（终局性保证）；WHI-334 §2.1（Global Synchronizer 可选以太坊锚定）
- Prividium: WHI-338 §2.3（完整证明流程）；WHI-338 §1.1（Validium DA 降级评估）
- Tempo L1: WHI-340 §2.2（TempoConsensus）；WHI-339 §4（BFT 终局性）
- Tempo Zones: WHI-340 §6（Validity Proofs Implementation Status — "proof slot exists, empty proof bytes submitted"）；WHI-340 §3.4（ZonePortal submitBatch ABI）
- Mantle: WHI-341 §4.1–4.2（OP Succinct ZK 终局 + optimistic fallback）；§7.2.4（强制包含延迟）；§8.1（企业终局性评估）

### 2.2 结算保证的本质差异

五个项目并不整齐地落入“三类”，而是分布在一个从**组织/协议信任**到**数学验证**的连续光谱上：

1. **Canton**：局部参与方之间的协议/联盟信任
2. **Tempo L1**：BFT 验证者集合信任
3. **Prividium**：数学证明 + Ethereum 结算
4. **Mantle**：数学证明 + public DA，但带治理可切换的 optimistic fallback
5. **Tempo Zones**：目标是数学证明，但当前实现仍是 Tempo L1 锚定 + Sequencer 信任

#### 类型 1: 协议信任 — Canton

Canton 的结算保证基于**2PC 协议正确性 + Synchronizer 运营商诚实性**。所有 confirmers 同意即终局，无需外部验证。

**优势**：终局性最快（秒级）；无额外验证成本
**劣势**：信任边界限于联盟成员；无外部可验证性（除非添加审计 Observer）

> *Source: WHI-335 §3.4 — "Canton 的终局性是局部的——交易只对参与的 Participant 有效。不存在'全网确认'的概念"*

#### 类型 2: BFT 共识信任 — Tempo L1

Tempo L1 的终局基于 **2/3 验证者 BLS12-381 阈值签名**。这是密码学保证但非数学证明——需信任验证者集合中不超过 1/3 是恶意的。

**优势**：亚秒级终局；去中心化验证者集合
**劣势**：信任边界限于验证者集合；安全性上限为 BFT 阈值

> *Source: WHI-339 §4 — Commonware Simplex BFT 安全假设*

#### 类型 3: 数学保证 — Prividium

Prividium 的结算基于**STARK 证明的密码学 soundness**。证明在以太坊 L1 上被任何人独立验证——"the proof is the guarantee"。

**优势**：无需信任运营商或对手方的数学级结算保证；中立结算层（以太坊）
**劣势**：证明生成成本（GPU prover farm）；到 L1 的延迟（数分钟）

> *Source: WHI-338 §7 Tradeoff #4 — "ZK Proof 提供了唯一不依赖任何第三方的结算验证方式"*

#### 类型 4: 数学保证 + 治理回退 — Mantle

Mantle 的**默认**结算基于 **SP1 validity proof 在以太坊 L1 上的链上验证**。这使它在结算安全性上更接近 Prividium，而不是传统 optimistic rollup。不同之处在于，Mantle 保留了由 `MantleSecurityMultisig` 触发的 optimistic fallback，因此它的风险画像包含一个明确的**治理切换风险**。

**优势**：默认路径下具备数学保证；公共 L1 DA 让任何人都可重构状态；与 OP Stack/以太坊生态兼容性强  
**劣势**：默认硬终局约 ~1 小时而非分钟级；SP1 Prover/Submitter 是额外活性依赖；治理层可切回 7 天 fallback

> *Source: WHI-341 §4.1–4.2；§8.1*

#### 类型 5: 继承信任（当前）/ 目标数学保证（未来）— Tempo Zones

Tempo Zones 继承 Tempo L1 的 BFT 信任，并添加 Sequencer 信任层。当前版本（v0.1.0）提交空证明；目标架构包含 SP1 RISC-V validity proof + TEE 验证。

**优势**：架构为 validity proof 做好了准备（`no_std` precompiles，proof slot in submitBatch）
**劣势**：当前版本无证明验证——完全依赖 Sequencer 诚实性

> *Source: WHI-340 §6.2 — "proof slot present, proof generation not implemented"；§6.1 — "no_std compatible so these precompiles can run inside the SP1 prover guest"*

### 2.3 关键分析问题

#### Q1: 企业更看重哪种结算保证 — 以太坊安全性 vs 独立终局？

**分析**：取决于参与方之间的**信任关系**和**监管要求**。

| 场景 | 推荐结算模型 | 理由 |
|------|------------|------|
| **同一机构内部多实体** | Canton（协议信任）或 Tempo L1（BFT 信任） | 内部实体间信任关系明确，无需外部验证锚；亚秒终局满足内部清算需求 |
| **竞争性金融机构间** | Prividium（数学保证）| 如 Cari Network 案例：竞争银行拒绝在对手基础设施上构建——ZK 证明提供中立信任锚 |
| **需要公共可验证性** | Prividium / Mantle（以太坊锚定 ZK 结算） | 监管要求可审计的外部结算证明 |
| **跨境支付** | Tempo L1（独立 BFT 终局） | 亚秒级终局对支付场景关键；不需要以太坊级别的安全保证 |

> *Source: WHI-338 §2.5 — Cari Network 选择分析："competitors will not build their payments infrastructure on a rival's rails"*

#### Q2: L1-L2 锚定模式对比

| 锚定路径 | 安全性继承 | 终局性路径 |
|----------|-----------|-----------|
| Prividium → ZKsync Gateway → Ethereum | 以太坊安全性（STARK 数学验证） | 链内 1s → Gateway 聚合 → L1 验证（分钟级） |
| Mantle → Ethereum（默认 ZK；可回退 Optimistic） | 以太坊安全性（SP1 validity proof；fallback 时为经济博弈） | 软终局 2s → L1 批次提交（~12min）→ SP1 proof 验证（~1h） |
| Tempo Zones → Tempo L1（Portal 合约） | Tempo L1 BFT 安全性 | Zone 块即时终局 → 批次提交至 L1（可配置间隔） |
| Canton → 可选 Ethereum 锚定 | 视 Sequencer 后端选择 | 域内即时终局（秒级）；锚定为可选 |

**关键差异**：Tempo Zones 的 L1 是**独立 BFT 链**（Tempo L1），而非以太坊。这意味着 Zones 的安全上限是 Tempo L1 的 BFT 安全性，而非以太坊的经济安全性。对企业而言，这是"更快终局 + 更可控安全" vs "更慢终局 + 以太坊级安全"的权衡。

#### Q3: 结算速度 vs 安全级别的取舍

跨模型比较时，必须先区分**链内/运营商确认**和**外部可验证的最终结算**：

- **若比较链内/运营商确认**：Tempo L1（~600ms）≈ Prividium（~1s）> Mantle（~2s soft）≈ Canton（秒级 2PC）> Tempo Zones（跟随 L1 cadence）
- **若比较外部可验证或可提款终局**：Tempo L1（自身 L1 的 ~600ms BFT）> Prividium（Ethereum 上数分钟到十数分钟）> Mantle（默认 ZK 模式约 ~1h）> Tempo Zones（proof 未上线，当前仍依赖 Sequencer + Tempo L1）> Canton（默认不提供外部结算锚）

企业场景的最优解不是单一维度的最大化，而是根据用例选择适当的平衡点。

#### Q4: "结算到 L1"对企业真的重要吗？

**结论：视情况而定。**

- **对竞争性多方场景（如银行间结算）**：重要。中立的外部结算层（以太坊）提供了任何参与方都无法单方面篡改的信任锚。这正是 Prividium 被银行选择的核心原因。
- **对单一运营商场景（如企业内部链）**：不重要。Canton 的域内终局和 Tempo L1 的 BFT 终局已经足够。额外的 L1 锚定增加成本和延迟，但不增加信任（运营商已经被信任）。
- **对合规驱动场景**：取决于监管要求。部分监管机构可能要求交易可追溯到公共结算层；部分可能只要求企业级审计能力。

---

## 3. 数据可用性对比矩阵

### 3.1 DA 方案完整矩阵

| DA 方案 | Canton | Prividium | Tempo L1 | Tempo Zones (L2) | Mantle (baseline) |
|---------|--------|-----------|----------|-------------------|-------------------|
| **数据存储位置** | 各 Participant 本地 PostgreSQL | 运营商私有 PostgreSQL（加密存储） | Tempo 验证者节点 | Zone Sequencer 本地存储 | 以太坊 L1（blob/calldata） |
| **全局状态存在否** | 否——"虚拟全局账本"（逻辑联合，无处存储） | 否——仅运营商持有完整状态 | 是——全节点可重构 | 否——仅 Sequencer 持有完整状态 | 是——任何人可从 L1 重构 |
| **状态可重构性** | 各 Participant 仅能重构自己的投影 | 仅运营商可重构 | 全节点可完整重构 | 依赖 Sequencer（未来 validity proof 目标增强可验证性） | 任何人可完整重构 |
| **数据主权** | 完全自主——各方自持数据；GDPR 原生合规 | 运营商持有——但运营商=机构自身 | L1 级公开——验证者共同持有 | Sequencer 持有——合规控制点 | 完全公开——无数据主权 |
| **DAC / 数据可用性委员会** | N/A（无全局数据需要保证可用性） | 无 DAC——单运营商模型 | N/A（BFT 全节点存储） | 无 DAC——单 Sequencer 模型 | N/A（L1 公开 DA） |
| **L1 可见内容** | N/A（默认不锚定 L1） | 仅状态根 + STARK 证明哈希 | N/A（自身即 L1） | 批次提交（blockTransition, depositQueueTransition, withdrawalQueueHash, proof） | 完整交易数据（blob/calldata） |
| **隐私保护级别** | 最高——子交易级隐私（Merkle DAG 投影） | 高——链级隐私（Validium + RBAC） | 低——L1 级公开透明 | 高——Zone 级隐私（加密存储 + 认证 RPC） | 无——完全透明 |

**数据来源**:
- Canton: WHI-335 §1.1（虚拟全局账本 vs 投影）；WHI-335 §2.1–2.4（Merkle DAG 隐私模型）；WHI-334 §2.1（Participant 自持 ACS）
- Prividium: WHI-338 §1.1–1.2（Validium DA tradeoff、无 DAC 单运营商模型）；WHI-337 §3.1（链下 PostgreSQL 存储）
- Tempo L1: WHI-339 §2.1（Reth SDK + MDBX 存储）；WHI-340 §2.1（全节点架构）
- Tempo Zones: WHI-340 §3.1–3.2（ZoneEngine 本地状态）；WHI-340 §6（validity proof 状态）；WHI-340 §3.4（submitBatch ABI）
- Mantle: WHI-341 §4（DA Solution Analysis — blob/calldata + Alt-DA 框架）

### 3.2 DA 架构深度解析

#### 3.2.1 Canton: 最极端的数据最小化

Canton 的 DA 模型是五个项目中最独特的——**根本不存在需要保证可用性的全局数据集**。

```
传统区块链 DA:
  全局状态 → 需要保证所有人可访问 → DA 层

Canton DA:
  无全局状态 → 每方只持有自己的投影 → 无需全局 DA 层
  
  Participant P1 持有: {Contract A, B, C}  → P1 的"DA"就是 P1 自己的 PostgreSQL
  Participant P2 持有: {Contract B, D}     → P2 的"DA"就是 P2 自己的 PostgreSQL
  Participant P3 持有: {Contract C, E}     → P3 的"DA"就是 P3 自己的 PostgreSQL
  
  不存在 {A, B, C, D, E} 的全集需要被任何人保证可用
```

**对企业的价值**：
- **GDPR 原生合规**：因为不存在全局状态副本，各 Participant 可独立删除自己持有的数据，不影响其他方或系统完整性
- **数据主权最大化**：每个机构完全控制自己的数据存储、备份和访问策略
- **元数据隐私限制**：Sequencer 仍可观察通信模式（消息大小、频率、收件人列表）

> *Source: WHI-335 §1.1 — "Canton 不是一个'更私密的区块链'——它是一个根本不同的架构范式"*
> *Source: WHI-335 §6 Tradeoff 6 — "无法做全局查询（如'网络上总共有多少 Token？'）"*

#### 3.2.2 Prividium: 链下 Validium（隐私 vs DA 去中心化）

Prividium 选择了**最大化隐私**的 DA 策略：

- 所有交易数据存储在运营商私有 PostgreSQL，部署在无互联网暴露的专用子网
- L1 仅可见状态根和证明哈希——L1 观察者**无法看到或推断任何交易输入**
- 无 DAC（数据可用性委员会）——完全信任运营商

**安全降级评估**：

| 风险维度 | Rollup 保证 | Validium (Prividium) 保证 | 降级程度 |
|---------|-----------|-------------------------|---------|
| 状态转换正确性 | ZK 证明（数学） | ZK 证明（数学，完全相同） | **无降级** |
| 数据持久性 | 以太坊永久存储 | 运营商数据库 + 备份 | **显著降级** |
| 资金可提取性 | 无许可 L1 逃生舱 | 需运营商配合提供 Merkle 证明 | **显著降级** |
| 历史可审计性 | 任何人可重放历史 | 仅运营商/授权审计员 | **完全降级（但对企业是特性）** |

> *Source: WHI-338 §1.1 — 运营商宕机场景分析 + 企业可接受性分析*
> *Source: WHI-338 §1.2 — "Prividium 当前不使用 Data Availability Committee (DAC)"*

#### 3.2.3 Tempo L1: 标准公链 DA（全节点可重构）

Tempo L1 作为独立 L1，数据可用性由验证者网络保证：

- 全节点存储完整区块数据（MDBX 存储后端）
- 任何人可运行全节点并重构完整状态
- **无隐私——所有交易对全节点可见**

这与 Tempo 的**支付优先**定位一致——L1 是公开的支付基础设施，隐私需求由 L2 Zones 解决。

> *Source: WHI-340 §2.1 — TempoFullNode 类型定义*

#### 3.2.4 Tempo Zones: Sequencer-held Validium + 未来 Validity Proof

Zones 的 DA 模型本质上是**单 Sequencer Validium**：

- Sequencer 是唯一持有完整 Zone 状态的实体
- Zone 块内容不发布到 L1（仅批次摘要信息提交至 ZonePortal）
- 隐私层包括：Zone 隔离、加密 Deposit（ECIES + Chaum-Pedersen）、认证 RPC、sanitized block（`transactions` 数组清空，`logsBloom` 归零）

**Validity Proof 架构准备状态**（v0.1.0）：

| 组件 | 状态 |
|------|------|
| ABI/合约 proof slot | ✅ 已实现（submitBatch 接受 `proof` 参数） |
| Precompile SP1 兼容 | ✅ 已实现（`no_std`） |
| Primitives SP1 兼容 | ✅ 已实现（`no_std`） |
| Portal verifier 地址 | ✅ 已实现（`verifier()` 函数） |
| Proof generation (SP1 guest) | ❌ 未实现 |
| Proof verification (L1 verifier) | ❌ 未实现 |

> *Source: WHI-340 §6 — "batches submitted with empty proof bytes"*
> *Source: WHI-340 §3.7 — "no_std compatible so these precompiles can run inside the SP1 prover guest (RISC-V) as well as in the zone node"*

#### 3.2.5 Mantle: 公开 DA（blob + Alt-DA 框架）

Mantle 使用以太坊 L1 作为主要 DA 层：

- op-batcher 将 L2 交易批次以 blob 形式提交至 L1
- 任何人可从 L1 数据重新推导完整 L2 状态
- Alt-DA 框架（`op-alt-da/`）提供可插拔 DA 接口（HTTP client/server，支持 S3/file 后端）
- **数据完全公开——这是 public-DA rollup 安全模型的前提，无论验证路径是 Optimistic 还是 ZK**

> *Source: WHI-341 §4 — DA Solution Analysis*
> *Source: WHI-341 §6.1 — "L1 Data Publication Requirement: All transaction data must be posted to L1 to enable fault proofs...This fundamentally limits data privacy"*

### 3.3 关键分析问题

#### Q1: 企业对"数据主权"的真实需求

**分析**：企业对数据主权的需求可以分为三个层次：

| 层次 | 需求描述 | 满足该层次的项目 |
|------|---------|----------------|
| **L1: 数据不公开** | 交易数据不应对公众可见 | Canton, Prividium, Tempo Zones |
| **L2: 数据可控** | 企业能决定谁可以看到什么数据 | Canton（最强——子交易级）, Prividium（RBAC 函数级）, Tempo Zones（认证 RPC） |
| **L3: 数据可删除** | 满足 GDPR"被遗忘权"等法规要求 | Canton（原生支持）, Prividium（Validium 链下存储技术上可行，但与金融数据留存义务矛盾） |

**Mantle 的差距**：Mantle 在数据主权的三个层次上均无法满足——这是**公开 DA rollup 架构**的根本限制，而非实现缺陷。ZK validity proof 改善的是状态正确性，不改变交易数据必须公开发布这一前提。

> *Source: WHI-338 §4.4 — GDPR 删除分析*
> *Source: WHI-335 §1.1 — "数据主权：有（数据只在相关 Participant 上）"*

#### Q2: Tempo Zones Sequencer-held vs Prividium Operator-held — 本质相同还是重要区别？

**结论：本质相同，但合规层设计有重要差异。**

**相同点**：
- 两者都是单一实体持有完整 L2 状态
- 两者都不使用 DAC
- 两者都依赖运营商/Sequencer 的诚实和可用性来保证数据持久性

**差异点**：

| 维度 | Tempo Zones | Prividium |
|------|------------|-----------|
| **合规控制** | TIP-403 政策框架（从 L1 镜像到 L2，SharedPolicyCache per-block GC） | 四层纵深防御（SSO → Proxy RPC → RBAC → TransactionFilterer） |
| **隐私加密** | ECIES 加密 deposit + Chaum-Pedersen 证明 + AES-GCM | Validium 链下存储（无需逐笔加密——整体链下） |
| **Validity Proof 路线** | SP1 RISC-V + TEE（架构准备中） | STARK 证明（已部署生产） |
| **审计机制** | Sequencer 全可见；L1 事件公开可查 | 选择性披露五种机制（审计角色、Merkle 证明导出、ZK 合规证明等） |

> *Source: WHI-340 §7.1 — TIP-403 Registry 实现*
> *Source: WHI-338 §3 — Prividium 四层准入控制*

#### Q3: 混合 DA 模式是否可行？

**结论：可行，且多个项目已有相关设计。**

| 混合模式 | 设计 | 可行性 |
|---------|------|-------|
| **Prividium 多链架构** | Prividium（Validium，隐私交易）+ zkSync Era（Rollup，公开交易）+ ZKsync Connect 跨链 | ✅ 已由 ZKsync 架构原生支持 |
| **Canton 多 Synchronizer** | 不同 Synchronizer 可选择不同后端（Ethereum/Fabric/DB）+ Global Synchronizer 跨域协调 | ✅ 已生产部署 |
| **Mantle Alt-DA** | Alt-DA 框架提供可插拔 DA 接口（`GenericCommitment` 类型设计用于外部 DA 提供商） | ✅ 框架就绪，需实现私有 DA server |
| **Tempo L1 + Zones** | L1 公开（支付基础设施）+ Zones 隐私（Zone 级 Validium） | ✅ 已设计实现 |

**对 Mantle 的启示**：最务实的路径是利用 Alt-DA 框架实现**关键数据 on-chain（公开）+ 敏感数据 off-chain（加密私有 DA server）**的混合模式。这无需修改核心协议，只需实现自定义 `DAServer`。

> *Source: WHI-338 §1.3 — 混合模式可能性分析（路径 A/B/C）*
> *Source: WHI-341 §7.2 — "Alt-DA framework already provides a pluggable DA interface"*

---

## 4. 企业终局性需求分析

### 4.1 终局性需求矩阵

不同企业用例对终局性的需求差异极大：

| 用例 | 终局性需求 | 可接受延迟 | 关键属性 | 最佳匹配 |
|------|-----------|-----------|---------|---------|
| **高频支付（POS/P2P）** | 即时软终局 | < 1 秒 | 速度 > 安全 | Tempo L1（亚秒 BFT）> Canton（秒级 2PC） |
| **跨机构清算** | 确定性硬终局 | 秒 ~ 分钟 | 不可逆性 + 多方确认 | Canton（2PC 全方确认）> Prividium（ZK 数学终局） |
| **代币化资产发行** | L1 级终局 | 分钟 ~ 小时 | 外部可验证性 + 法律效力 | Prividium（隐私发行，分钟级 ZK 结算） / Mantle（公开发行，~1h ZK 结算） |
| **跨境汇款** | 经济终局 | 分钟级 | 成本效率 + 速度 | Tempo L1 > Prividium |
| **合规报告/审计** | 可验证终局 | 小时 ~ 天 | 可审计性 > 速度 | Canton（完整审计轨迹）> Prividium（选择性披露） |
| **DeFi / 公链交互** | 以太坊等价终局 | 接受现有时间 | 互操作性 | Mantle（原生 OP Stack）> Prividium（通过 ZKsync Gateway） |

### 4.2 Mantle 当前终局性的企业可接受性

**核心问题**：Mantle 的**默认 ~1 小时 ZK 终局**与**可切换的 7 天 optimistic fallback**，对企业分别意味着什么？

**分析**：

```
Mantle 终局性的四个层次:

Layer 1: 软终局 (~2 秒)
  ├─ Sequencer 确认交易已包含在区块中
  ├─ 对单一运营商场景（企业自运营 Sequencer）——这已经足够
  └─ 风险: Sequencer 可能重组（理论上）

Layer 2: L1 批次确认 / safe finality (~12 分钟)
  ├─ 交易数据已提交至以太坊 L1
  ├─ 数据不可篡改（以太坊终局性保护）
  └─ 风险: 状态转换尚未完成 ZK 验证

Layer 3: 默认硬终局 (~1 小时)
  ├─ SP1 proof 提交并通过 `OPSuccinctL2OutputOracle` 验证
  ├─ output root 被接受，withdrawal 可执行
  └─ 风险: 依赖 SP1 Prover + Output Submitter 的活性

Layer 4: 回退硬终局 (7 天，仅 fallback 模式)
  ├─ 仅当 `MantleSecurityMultisig` 切换到 optimistic 模式时生效
  ├─ 挑战期结束，无有效欺诈证明
  └─ 风险: 治理层可改变默认终局路径
```

**企业场景评估**：

| 场景 | 可接受性 | 理由 |
|------|---------|------|
| **企业内部链（自运营 Sequencer）** | ✅ 软终局（2s）已足够 | 企业信任自己的 Sequencer；内部交易不需要外部验证 |
| **受信任联盟** | ✅ safe + ZK 终局通常可接受 | ~12 分钟的数据落地和 ~1 小时的可提款终局，比经典 optimistic 模式显著改善 |
| **竞争性多方（银行间）** | ⚠️ 有条件可接受 | 默认 ZK 终局已优于 7 天，但必须限制 multisig 切回 fallback 的权限，否则对手方仍需承受治理切换风险 |
| **高频支付 / POS** | ⚠️ 仅软终局仍偏弱 | 2 秒 Sequencer 确认足够快，但缺乏强约束；需要 preconf 或 BFT fast-finality 作为前置保证 |
| **与 DeFi / 公共桥交互** | ✅ 可接受 | 公共 DA + 以太坊结算天然兼容这类公开交互场景 |

**关键洞察**：Mantle **已经具备数学终局**，因此问题不再是“默认要等 7 天”，而是：
1. 默认 ZK 终局仍有约 ~1 小时延迟；
2. 日常交易的 2 秒软终局仍是 Sequencer 承诺而非强约束；
3. `MantleSecurityMultisig` 可切回 optimistic fallback，形成治理层面的尾部风险。

### 4.3 即时终局机制引入建议

**参考方案**：Tempo Commonware Simplex BFT

Mantle 可以考虑在 Sequencer 层引入 **BFT 快速终局** 机制：

```
当前 Mantle 终局路径:
  Sequencer 排序 → 软终局(2s) → L1 批次提交(~12min) → SP1 proof 验证(~1h) → 硬终局
                                            └─ 极端情况下可被治理切回 optimistic fallback (7天)

可能的改进路径:
  Sequencer 排序 → Bonded/BFT preconfirmation(~1s) → L1 批次提交 → SP1 proof 验证(压缩至 <1h)

参考: Tempo L1 的 Commonware Simplex BFT
  - BLS12-381 阈值签名
  - 2/3 验证者签名即终局
  - 亚秒级确认
  - 双 runtime 隔离（不影响执行性能）
```

**实施路径分析**：

| 方案 | 复杂度 | 安全保证 | 终局速度 |
|------|-------|---------|---------|
| **A: BFT 快速终局层** | 高（新增共识层组件） | BFT 2/3 信任 + 以太坊/ZK 兜底 | ~1 秒确定性前置终局 |
| **B: Bonded Preconfirmation** | 中（扩展现有 preconf 模块） | 经济保证（Sequencer 质押） | ~2 秒经济终局 |
| **C: SP1 proving pipeline 优化** | 中-高（外部 prover/submitter 扩容） | 同样的 ZK 数学保证，但缩短延迟 | 将默认硬终局从 ~1h 继续压缩 |

如果目标是**尽快改善企业用户体验**，最务实的组合是 **B + C**：
- `B` 强化 2 秒内的前置确认
- `C` 直接压缩默认 ~1 小时的硬终局

`A` 适合更强的联盟链场景，但会显著增加共识层复杂度。

> *Source: WHI-341 §5.1 — "Extend the existing preconfirmation module with bonded sequencer for cryptographic preconf receipts — infrastructure already exists"*
> *Source: WHI-341 §7.7 — Preconfirmation Module Enhancement 自然插入点*

---

## 5. Mantle 共识/结算/DA 架构建议

### 5.1 建议总览

基于五个项目的横向对比，我们为 Mantle 的企业适配提出以下架构建议：

```
建议架构: Mantle L2 + Privacy L3 + 增强终局性

┌─────────────────────────────────────────────────────────────────────┐
│                        ETHEREUM L1 (Settlement)                      │
│   状态根 + SP1 validity proof（默认）/ optimistic fallback（备用）    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────────┐
│  MANTLE L2 (增强版)           │                                      │
│  ┌──────────────────────────┐ │ ┌────────────────────────────────┐  │
│  │ BFT 快速终局层 (新增)     │ │ │ Alt-DA 混合模式 (新增)          │  │
│  │ 参考: Tempo Simplex BFT   │ │ │ 公开数据: L1 blob (现有)       │  │
│  │ → 秒级确定性终局          │ │ │ 敏感数据: 加密 DA Server (新增) │  │
│  └──────────────────────────┘ │ └────────────────────────────────┘  │
│  ┌──────────────────────────┐ │ ┌────────────────────────────────┐  │
│  │ 准入控制层 (新增)         │ │ │ 合规注册表 (新增)               │  │
│  │ 参考: Prividium 4 层防御  │ │ │ 参考: Tempo TIP-403 框架       │  │
│  │ → Sequencer + TxPool 过滤│ │ │ → 预编译合约 + 策略缓存        │  │
│  └──────────────────────────┘ │ └────────────────────────────────┘  │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼                       ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  Privacy L3 (Zone 模式)   │  │  Privacy L3 (Zone 模式)   │
│  参考: Tempo Zones         │  │  (可部署多个独立实例)      │
│  ┌──────────────────────┐ │  │                           │
│  │ NoopConsensus         │ │  │  企业 A 的隐私执行环境     │
│  │ 加密 Deposit/取款     │ │  │  企业 B 的隐私执行环境     │
│  │ 认证 RPC              │ │  │  ...                      │
│  │ 合规策略从 L2 镜像     │ │  └──────────────────────────┘
│  │ Validity Proof (目标)  │ │
│  └──────────────────────┘ │
└──────────────────────────┘
```

### 5.2 详细建议

#### 建议 1: 引入 BFT 快速终局层

**优先级**: 高
**参考**: Tempo L1 Commonware Simplex BFT
**目标**: 将 Mantle 的前置终局从“仅 Sequencer 承诺”提升为秒级的确定性/经济保证

**方案**：在 Sequencer 层引入多方 BFT 签名机制。企业级部署中，参与机构各运行一个签名节点，2/3 节点签名即可对高价值交易出具更强的前置终局；Mantle 现有的 ZK 证明路径继续承担最终 settlement。

**实施路径**：
1. 短期：扩展 preconf 模块，引入 Sequencer 质押 + 经济终局
2. 中期：引入 BFT 快速终局层（参考 Commonware 双 runtime 设计）
3. 长期：并行优化 SP1 proving pipeline，压缩默认 ~1 小时硬终局

**复杂度**：中-高
**风险**：需要重新设计共识/执行边界；BFT 签名引入额外延迟和通信开销

> *Basis: §4.3 即时终局机制分析；WHI-340 §2.2 Tempo 双 runtime 架构参考；WHI-341 §7.7 preconf 自然插入点；§8.1 对当前 ~1h 终局的评估*

#### 建议 2: 实现混合 DA 策略

**优先级**: 高
**参考**: Prividium Validium + Mantle Alt-DA 框架
**目标**: 支持"公开数据 on-chain + 敏感数据 off-chain"的混合模式

**方案**：利用 Mantle 现有的 Alt-DA 框架（`op-alt-da/`），实现自定义加密 DA Server：

- **公开交易**：继续使用 L1 blob DA（现有行为不变）
- **隐私交易**：通过 `GenericCommitment` 类型路由至私有 DA Server
  - 加密 blob 存储
  - 准入控制的数据检索
  - 可选 DAC（数据可用性委员会）签名

**实施路径**：
1. 实现自定义 `DAServer` with 加密存储 + 访问控制
2. 在 op-batcher 中添加交易分类逻辑（公开 vs 隐私）
3. 修改 derivation pipeline 支持混合数据源

**复杂度**：中（框架已就绪）
**风险**：隐私交易的状态派生、数据检索和 SP1 证明生成需要特殊处理；公开数据路径与私有数据路径的正确性必须同时可验证

> *Basis: §3.3 Q3 混合 DA 分析；WHI-341 §4.2（Alt-DA 框架）；WHI-341 §7.2（Pluggable DA 自然插入点）*

#### 建议 3: Tempo Zones "L1 + Privacy L2" → Mantle "L2 + Privacy L3" 映射

**优先级**: 中
**参考**: Tempo Zones 架构
**目标**: 提供应用级隐私执行环境

**架构映射**：

| Tempo 架构 | Mantle 等价 | 说明 |
|-----------|-----------|------|
| Tempo L1（公开支付链） | Mantle L2（公开通用链） | 基础结算和公开交易层 |
| Zones L2（隐私 Validium） | Privacy L3（隐私应用链） | 企业隐私执行环境 |
| ZonePortal（L1 合约） | L3 Portal（L2 合约） | 跨层桥接和批次锚定 |
| TIP-403（合规框架） | 合规注册表（L2 预编译） | 策略镜像到 L3 |
| NoopConsensus | NoopConsensus | 单 Sequencer 出块 |
| 加密 Deposit（ECIES） | 加密 Deposit（可复用） | 隐私桥接 |

**Tempo Zones 可直接借鉴的设计**：
- L1 事件驱动的 L2 出块（ZoneEngine 模式）
- 认证 RPC with per-account scoping
- `no_std` 兼容为 validity proof 做准备
- 100ms 最小 RPC 响应时间（防时序侧信道）
- Sanitized blocks（清空 transactions 数组，归零 logsBloom）
- ECIES + Chaum-Pedersen 加密 deposit 方案

**实施路径**：
1. 基于 Reth SDK 构建最小 L3 节点（参考 Tempo Zones v0.1.0 结构）
2. 实现 L2↔L3 Portal 合约（参考 ZonePortal ABI）
3. 添加认证 RPC 层和加密 deposit
4. 策略镜像机制（从 L2 合规注册表读取策略到 L3）

**复杂度**：高（需要完整的 L3 节点开发）
**风险**：L3 安全性依赖 L2 + Sequencer 信任；维护成本高

> *Basis: WHI-340 §3 Zones 完整架构；WHI-340 §8.3（Zone Architecture Mantle Reference）*

#### 建议 4: 准入控制与合规框架

**优先级**: 高
**参考**: Prividium 四层防御 + Tempo TIP-403
**目标**: 在不修改核心协议的前提下添加企业准入控制

**方案**：

```
Layer 1: 身份认证（参考 Prividium SSO 集成）
  → 企业 IdP 集成（OIDC/SAML）+ 钱包地址绑定

Layer 2: 交易过滤（Mantle Sequencer + TxPool 自然插入点）
  → op-node sequencer 级别的 TransactionPolicy 接口
  → op-geth txpool 级别的白名单/黑名单过滤

Layer 3: 合约级权限（参考 Tempo TIP-403 预编译注册表）
  → 合规注册表预编译合约（whitelist/blacklist/compound policies）
  → 每笔 TIP-20 级别的 `transferAuthorized()` 检查

Layer 4: L1 边界防御（参考 Prividium TransactionFilterer）
  → L1→L2 强制交易白名单过滤
```

**实施路径**：
1. Layer 2（TxPool 过滤）→ 最快可落地，利用现有 `op-geth/core/txpool/` 扩展点
2. Layer 3（合规注册表）→ 中期，部署预编译或系统合约
3. Layer 1（身份层）→ 可与 Layer 2 并行，但需要 IdP 集成
4. Layer 4（L1 边界）→ 部署 TransactionFilterer 合约

**复杂度**：中（渐进式添加，无需修改核心协议）

> *Basis: WHI-338 §3（Prividium 四层准入控制）；WHI-340 §7.1（TIP-403 实现细节）；WHI-341 §7.1, §7.3, §7.4（自然插入点）*

#### 建议 5: Sequencer 中心化 — 企业场景的优势与风险

**分析**：Mantle 的中心化 Sequencer 在企业场景下**既是优势也是风险**。

**优势（参考 Tempo Zones 验证）**：
- 合规控制点：Sequencer 可执行 KYC/AML 策略、交易过滤
- 运营简洁性：无需协调多方共识
- 性能可预测：无 BFT 通信开销
- Tempo Zones 证明了单 Sequencer 模式在合规场景下是有效的架构选择

**风险**：
- 单点故障（op-conductor 仅提供 HA，不提供去中心化）
- 审查风险（Sequencer 可选择性排除交易）
- 信任集中（所有参与方必须信任 Sequencer 运营者）

**建议**：
- 短期：接受中心化 Sequencer，将其定位为**合规控制点**（参考 Tempo Zones 模式）
- 中期：引入 BFT 快速终局层（建议 1），将 Sequencer 从单一实体扩展为多方签名委员会
- 长期：评估 shared/based sequencing（OP Stack 生态未来方向）

> *Basis: WHI-341 §5.1 — "The sequencer is already centralized and configurable"；WHI-340 §3.1 — "a Zone is a single-sequencer validium"*

### 5.3 优先级总结

| # | 建议 | 优先级 | 复杂度 | 前置依赖 | 参考项目 |
|---|------|--------|--------|---------|---------|
| 1 | BFT 快速终局层 | 高 | 中-高 | 无 | Tempo L1 |
| 2 | 混合 DA 策略 | 高 | 中 | 无（Alt-DA 框架就绪） | Prividium + Mantle Alt-DA |
| 3 | Privacy L3 (Zone 模式) | 中 | 高 | 建议 2（DA 基础） | Tempo Zones |
| 4 | 准入控制与合规框架 | 高 | 中（渐进式） | 无 | Prividium + Tempo TIP-403 |
| 5 | Sequencer 定位与演进 | 中 | 低→高（分阶段） | 建议 1 | Tempo Zones + Canton |

**推荐实施顺序**：4 → 2 → 1 → 5 → 3

理由：
- 准入控制（4）是企业最基本需求且实施最简单（不修改核心协议）
- 混合 DA（2）利用现有框架，为隐私交易提供基础
- BFT/Preconf 增强（1）把日常交易从“Sequencer 承诺”提升到更强的秒级前置终局
- Sequencer 演进（5）与 BFT 终局配合
- Privacy L3（3）是长期目标，依赖前置基础

---

## 附录 A: 术语对照

| 术语 | 英文 | 定义 |
|------|------|------|
| 共识机制 | Consensus Mechanism | 网络参与者就状态转换达成一致的方法 |
| 终局性 | Finality | 交易被确认为不可逆转的状态 |
| 数据可用性 | Data Availability (DA) | 确保交易数据可被获取以验证/重构状态 |
| 结算层 | Settlement Layer | 交易最终被确认和结算的层级 |
| BFT | Byzantine Fault Tolerance | 系统在部分节点恶意行为下仍能正确运行的能力 |
| 2PC | Two-Phase Commit | 分布式事务协调协议，确保所有参与方一致提交或回滚 |
| Validium | — | ZK Rollup 变体，交易数据链下存储 |
| DAC | Data Availability Committee | 多方签名保证数据可用性的机制 |
| STARK | Scalable Transparent Argument of Knowledge | 无需可信设置的零知识证明系统 |
| Optimistic Rollup | — | 假设状态转换正确，通过挑战期和欺诈证明保障安全 |

## 附录 B: M1 来源文件索引

| 文件 | 主要引用内容 |
|------|------------|
| `m1-research/canton/WHI-334-canton-docs-research.md` | Canton 整体架构、Synchronizer 组件关系、Party-Participant 模型 |
| `m1-research/canton/WHI-335-canton-architecture-analysis.md` | 2PC 提交流程、BFT Sequencer 安全假设、终局性分析、Need-to-Know vs ZK 对比 |
| `m1-research/canton/WHI-336-canton-codebase-analysis.md` | SequencerDriver trait、Mediator 2PC 代码实现、ResponseAggregation quorum、MerkleTree 盲化 |
| `m1-research/prividium/WHI-337-prividium-official-docs-research.md` | Validium 模型定义、ZK 证明系统、四层准入控制、企业案例 |
| `m1-research/prividium/WHI-338-prividium-architecture-deep-analysis.md` | DA tradeoff 深度分析、证明流程、Canton vs Prividium 隐私对比、GDPR 分析 |
| `m1-research/tempo-zones/WHI-339-tempo-docs-research.md` | Commonware Simplex BFT、Payment Lane、Zones 架构、TIP-403 |
| `m1-research/tempo-zones/WHI-340-tempo-code-analysis.md` | 双 runtime 设计、ZoneEngine L1 事件驱动、NoopConsensus、validity proof 状态、ECIES 加密 deposit |
| `m1-research/mantle/mantle-v2-architecture-baseline.md` | OP Succinct ZK validity、optimistic fallback、blob DA、Alt-DA 框架、preconf 模块、强制包含延迟、企业适配评估 |

---

*本文档基于 2026 年 5 月 6 日完成的 M1 深度调研成果编制。所有结论和建议均可追溯至具体 M1 来源文件。未在 M1 文档中有充分依据的判断已标注为分析推断。*
