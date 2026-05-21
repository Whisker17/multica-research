# Mantle 企业级隐私层设计方案

> **Issue**: WHI-351 | **Milestone**: M3: Mantle 企业级改造可行性设计
> **Date**: 2026-05-07
> **Dependencies**: WHI-350 (Gap 分析), WHI-341 (Mantle 基线), WHI-343 (隐私对比), WHI-338 (Prividium), WHI-340 (Tempo), WHI-345 (共识/DA 对比)
> **Constraint**: 所有改造必须保持 EVM 完全兼容

---

## 执行摘要

本文档为 Mantle V2 设计具体的、组件级的隐私层改造方案。基于 M2 横向对比（WHI-343）和 M3 Gap 分析（WHI-350）的结论，本设计选择 **Validium 模式**作为核心隐私方案——将敏感交易数据从公开 L1 DA 迁移到运营商控制的链下存储，同时通过链上 commitment 保持状态可验证性。

**核心设计原则**：
1. **最小侵入**：优先使用 `op-alt-da` 可插拔框架和 predeploy 合约，最小化对 OP Stack 核心代码的修改
2. **渐进式推进**：从混合 DA 路由（Phase 2）到完整隐私子链（Phase 3），每阶段独立可用
3. **EVM 兼容底线**：所有改造不破坏 EVM 兼容性，不引入自定义 opcode
4. **合规友好**：Sequencer 完整可见性是特性而非缺陷——作为天然合规控制点
5. **单一排序序列**：Phase 2 保持单条 L2 排序链，只把隐私交易数据从公开 DA 中抽离，不拆分出第二条执行链

**关键改造清单**：

| 层 | 改造项 | 侵入性 | Phase |
|---|--------|--------|-------|
| DA 层 | 私有 DA 后端 (`op-alt-da` 扩展) | 低（插件接口） | 2 |
| DA 层 | 混合 DA 路由 (`op-batcher` 修改) | 中（批处理逻辑） | 2 |
| Sequencer 层 | 交易分类器 + 隐私路由 | 中（策略引擎扩展） | 2 |
| 执行层 | 隐私交易 receipt 处理 | 低（op-geth 扩展） | 2 |
| 验证层 | 委任验证 + ZK 过渡方案 | 高（证明系统改造） | 2-3 |
| 桥接层 | ECIES 加密存款/取款 | 中（合约 + 密码学库） | 2 |
| 披露层 | 选择性披露 API + 查看密钥 | 低（新增服务） | 2 |

---

## 第一章：方案选型论证

### 1.1 候选方案评估

WHI-343 识别了三种企业级隐私范式。以下评估每种范式在 Mantle OP Stack 架构上的适用性：

#### 方案 A: Canton 式"需知即知" (Need-to-Know)

| 评估维度 | 分析 |
|---------|------|
| **核心机制** | 子交易 Merkle DAG 投影 + 端到端加密路由 |
| **架构兼容性** | **不兼容**。Canton 无全局共享状态（WHI-335 §1.1），而 Mantle 作为 Optimistic Rollup 必须维护全局状态以支持 Fault Proof |
| **状态模型** | Canton 使用因果一致性 + 虚拟全局账本（WHI-343 §1.2.3），与 Mantle 的强全局一致性模型根本不同 |
| **合约语言** | Canton 使用 Daml（函数式 DSL），与 EVM/Solidity 完全不兼容 |
| **拓扑结构** | Canton 使用 Participant-Synchronizer-Mediator 三角拓扑，Mantle 使用 Sequencer-Verifier 二元拓扑 |
| **结论** | **排除**。将 Canton 范式嫁接到 OP Stack 等于重建整个架构，丧失 Mantle 全部既有优势 |

> **Evidence**: WHI-343 §4.2.1 — "Canton 的隐私范式不适合'嫁接'到 OP Stack 上"

#### 方案 B: Prividium 式 Validium (Prove-Not-Reveal)

| 评估维度 | 分析 |
|---------|------|
| **核心机制** | 运营商持有完整状态 + ZK 有效性证明 + Validium 链下 DA |
| **架构兼容性** | **高**。Mantle 单 Sequencer 架构与 Validium 单运营商模型天然匹配（WHI-343 §4.2.2）。Sequencer 已持有完整状态，切换到链下 DA 不需要新的信任假设 |
| **DA 集成** | Mantle 已有 `op-alt-da` 可插拔 DA 框架（WHI-341 §2.10），提供 `GenericCommitment` 类型，天然支持自定义 DA 后端 |
| **EVM 兼容** | Prividium 保持完整 EVM 兼容，与 Mantle 约束一致 |
| **核心矛盾** | Optimistic Rollup 需要 L1 数据发布以支持 Fault Proof；Validium 要求数据不上链。需要设计验证层过渡方案 |
| **结论** | **选择（Phase 2 主方案）**。架构契合度最高，改造路径最清晰 |

> **Evidence**: WHI-350 §3.1 — "方案 A (Validium) 为 Phase 2 主方案"；WHI-343 §4.2.2 — "Prividium Validium 范式 → Mantle: 可行但需要重大架构变更"

#### 方案 C: Tempo 式 L2 隔离 + 加密桥接

| 评估维度 | 分析 |
|---------|------|
| **核心机制** | 独立隐私 L2 (Zone) + 单 Sequencer + ECIES 加密存款 + 认证 RPC |
| **架构兼容性** | **最高同源性**。Tempo Zones 基于 Reth（与 OP Stack 同属以太坊执行层变体），Zone 架构可翻译为"Mantle L2 → 隐私 L3"层级（WHI-343 §4.2.3） |
| **技术可借鉴** | ECIES 加密存款、认证 RPC、TIP-403 合规框架、`no_std` 预编译均可在 OP Stack 上实现 |
| **完整性** | Zone 架构是最完整的多租户方案，但需要全栈改造（新链实例 + Portal 合约 + 批次提交 + 证明系统） |
| **结论** | **选择（Phase 3 目标方案 + Phase 2 部分技术借鉴）** |

> **Evidence**: WHI-343 §4.2.3 — "Tempo Zones 范式 → Mantle: 最高可行性"；WHI-350 §3.1 — "方案 B (Zone) 为 Phase 3 目标方案"

### 1.2 选型决策：Validium 模式 + 分阶段组合

**最终选择**：以 **Validium 模式**为核心隐私机制，辅以 Tempo Zones 的桥接加密和选择性披露技术，分两阶段实施。

```
Phase 2 (6-9 月):  Validium 混合 DA 模式
  ├─ 核心: op-alt-da 私有 DA 后端 + 混合 DA 路由
  ├─ 借鉴 Prividium: 运营商持有数据 + 链上 commitment
  ├─ 借鉴 Tempo: ECIES 加密桥接 + 选择性披露
  └─ 过渡: 委任验证 (Optimistic) → ZK 验证 (Phase 3)

Phase 3 (12-18 月): 隐私子链 (Zone) + ZK 迁移
  ├─ 核心: 独立隐私 L3 实例 (参照 Tempo Zone 架构)
  ├─ ZK 证明系统替换 kona Fault Proof
  └─ 混合 DA 路由 (交易级 DA 策略选择)
```

### 1.3 选型理由总结

| 决策 | 理由 | 可接受的 Tradeoff |
|------|------|-------------------|
| **选择 Validium** | Mantle 单 Sequencer 已持有完整状态；`op-alt-da` 可插拔框架提供清晰工程路径；不需要新的信任假设 | 数据可用性从"以太坊保证"降级为"运营商保证"——对企业场景可接受（运营商=企业自身，WHI-338 §1.1） |
| **排除 Canton** | 需要完全重构状态模型、合约语言、拓扑结构；丧失 EVM 生态优势 | 放弃了 Canton 的子交易级精细隐私——通过 RBAC + 选择性披露在应用层补偿 |
| **Phase 3 引入 Zone** | Zone 架构提供多租户隔离的完整方案 | 全栈改造复杂度高（12-18 人月），作为长期目标 |
| **渐进式 ZK 迁移** | ZK 化是行业确定性趋势（WHI-347 §6.1），同时解决隐私+终局性+验证 | ZK 迁移工期极长，Phase 2 先用委任验证过渡 |

> **Evidence**: WHI-350 §3.1 (方案矩阵推荐); WHI-343 §4.3 (组合策略建议); WHI-345 §5 (Mantle DA 架构建议)

---

## 第二章：架构设计

### 2.1 总体架构概览

```
                              ETHEREUM L1 (Settlement Layer)
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │  ┌──────────────┐  ┌───────────────────┐  ┌──────────────────────┐ │
    │  │ Batch Inbox   │  │ L1 SystemConfig   │  │ OptimismPortal       │ │
    │  │ (public batches)│ │ (proxy contract)  │  │ (+白名单, Phase 1)   │ │
    │  └──────┬────────┘  └────────┬──────────┘  └──────────┬───────────┘ │
    │         │                    │                         │             │
    │  ┌──────┴────────┐  ┌───────┴──────────┐  ┌──────────┴───────────┐ │
    │  │ DA Commitment  │  │ DisputeGame      │  │ DataAvailability     │ │
    │  │ Registry (新增) │  │ Factory          │  │ Challenge            │ │
    │  │ (隐私批次hash)  │  │ (+委任验证扩展)   │  │ (Alt-DA mode)        │ │
    │  └───────────────┘  └──────────────────┘  └──────────────────────┘ │
    └────────────────────────────────┬────────────────────────────────────┘
                                     │
                 L1 Data Flow (deposits, public batches, commitments)
                                     │
    ┌────────────────────────────────┼────────────────────────────────────┐
    │  MANTLE V2 (L2) — 企业隐私增强                                      │
    │                                │                                    │
    │  ┌─────────────────────────────▼──────────────────────────────────┐ │
    │  │                  OP-NODE (Consensus Layer)                      │ │
    │  │  ┌───────────────────┐  ┌──────────────┐  ┌─────────────────┐ │ │
    │  │  │  Sequencer        │  │  Derivation  │  │  Privacy        │ │ │
    │  │  │  + Privacy        │  │  Pipeline    │  │  Classifier     │ │ │
    │  │  │    Classifier     │  │  (+隐私tx    │  │  (新增模块)      │ │ │
    │  │  │  + Policy Engine  │  │   重组逻辑)   │  │  公开/隐私分流   │ │ │
    │  │  └──────┬────────────┘  └──────────────┘  └─────────────────┘ │ │
    │  └─────────┼──────────────────────────────────────────────────────┘ │
    │            │ Engine API                                             │
    │            ▼                                                        │
    │  ┌────────────────────────────────────────────────────────────────┐ │
    │  │                  OP-GETH (Execution Layer)                      │ │
    │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │ │
    │  │  │  EVM Engine   │  │  Tx Pool     │  │  State Database      │ │ │
    │  │  │  (无修改)     │  │  + Privacy   │  │  (标准 geth)         │ │ │
    │  │  │              │  │    Filter     │  │                      │ │ │
    │  │  └──────────────┘  └──────────────┘  └──────────────────────┘ │ │
    │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │ │
    │  │  │  Privacy      │  │  Identity    │  │  Selective           │ │ │
    │  │  │  Receipt      │  │  Registry    │  │  Disclosure          │ │ │
    │  │  │  Handler      │  │  Predeploy   │  │  Predeploy           │ │ │
    │  │  │  (新增)       │  │  (Phase 1)   │  │  (新增)              │ │ │
    │  │  └──────────────┘  └──────────────┘  └──────────────────────┘ │ │
    │  └────────────────────────────────────────────────────────────────┘ │
    │                                                                     │
    │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐    │
    │  │  OP-BATCHER    │  │  OP-PROPOSER   │  │  PRIVATE DA        │    │
    │  │  + Hybrid DA   │  │  (+隐私commitment│  │  SERVER (新增)     │    │
    │  │    Router      │  │    提交)        │  │  加密存储+许可检索  │    │
    │  │  (公开→L1,     │  │               │  │  GenericCommitment │    │
    │  │   隐私→私有DA)  │  │               │  │  HTTP 接口          │    │
    │  └────────────────┘  └────────────────┘  └────────────────────┘    │
    │                                                                     │
    │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐    │
    │  │  Selective      │  │  Key           │  │  Audit Event       │    │
    │  │  Disclosure     │  │  Management    │  │  Service           │    │
    │  │  API (新增)     │  │  Service (新增) │  │  (Phase 1)         │    │
    │  └────────────────┘  └────────────────┘  └────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Sequencer 层改造

#### 2.2.1 当前流程

```
用户 → RPC → op-geth tx pool → op-node Sequencer → 排序 → Engine API →
  op-geth 执行 → op-batcher → L1 calldata/blobs (全部公开)
```

#### 2.2.2 改造后流程

```
用户 → 认证 RPC (Phase 1) → op-geth tx pool (+ Privacy Filter) →
  op-node Sequencer → Privacy Classifier (分类) →
    ├─ 公开交易: 原流程 → op-batcher → L1 DA (标准 blobs)
    └─ 隐私交易: 隐私路径 → op-batcher (Hybrid Router) →
         ├─ 交易数据 → Private DA Server (加密存储)
         └─ Commitment hash → L1 DA Commitment Registry
```

#### 2.2.3 Privacy Classifier 设计

**模块位置**: `op-node/rollup/sequencing/privacy_classifier.go` (新增)

**分类机制**: 交易通过以下标准被分类为"隐私交易"：

| 分类标准 | 实现方式 | 优先级 |
|---------|---------|--------|
| **显式声明** | 交易 `to` 地址命中 Privacy Registry Predeploy 中注册的隐私合约列表 | P0 |
| **发送者策略** | 发送者地址在 Identity Registry 中标记为"隐私模式默认" | P1 |
| **合约级策略** | 目标合约在部署时由管理员标记为"全部隐私"或"选择性隐私" | P1 |
| **交易类型** | 新增 EIP-2718 envelope 类型 `PrivateTransaction` (type = 0x70) | P2 (可选) |

**推荐 Phase 2 实现**：优先使用"显式声明"机制——管理员在 Privacy Registry Predeploy 中注册隐私合约地址列表。Sequencer 在交易排序时查询该列表，命中则走隐私路径。

**隐私域边界约束**：Phase 2 的隐私不是"任意合约任意调用都自动保密"，而是建立一个**封闭的隐私合约域**：
- 被注册为隐私合约的地址只允许调用其他隐私合约或显式许可的系统合约/预编译
- 隐私合约默认不得向公开合约写入状态、不得依赖公开事件作为业务输出
- 该约束优先通过部署审批、字节码审计和 Registry 元数据执行，而不是修改 EVM 运行时

这样做的原因是：如果私有交易在内部调用公开合约或发出公开事件，RPC 层再怎么做字段脱敏，也无法阻止状态差异和日志本身形成泄露通道。

**设计权衡**：

| 方案 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| 合约地址级分类 | 简单、确定性、不需要交易格式改动 | 粒度粗（合约级，非函数级） | **Phase 2 首选** |
| 新交易类型 (type=0x70) | 最精细（交易级控制） | 需要修改 tx pool、RLP 编码、工具链适配 | Phase 3 考虑 |
| 函数选择器级分类 | 中等粒度 | Sequencer 需解析 calldata，增加处理延迟 | Phase 3 考虑 |

**Privacy Classifier 接口设计**：

```go
// privacy_classifier.go (新增)
type PrivacyClassifier interface {
    // IsPrivateTransaction 判断交易是否需要走隐私路径
    // 查询 Privacy Registry Predeploy 的缓存
    IsPrivateTransaction(tx *types.Transaction) bool
    
    // ClassifyBatch 对一批交易进行分类，返回公开和隐私两组
    ClassifyBatch(txs []*types.Transaction) (public, private []*types.Transaction)
    
    // RefreshRegistry 从 Privacy Registry Predeploy 刷新缓存
    RefreshRegistry(ctx context.Context) error
}
```

**缓存策略**: Privacy Registry 状态通过 L2 事件（`ContractRegistered`/`ContractDeregistered`）驱动 LRU 缓存刷新，避免每笔交易查询链上状态。

> **Evidence**: WHI-341 §7.4 — "`SequencerStateListener` 和 `AsyncGossiper` 接口允许可插拔行为"；WHI-350 §2.4.A — "Sequencer 策略引擎改造范围最小"

#### 2.2.4 隐私交易数据存储

隐私交易的完整数据（calldata、发送方、接收方、金额等）**仅存储在运营商控制的 Private DA Server 中**，不发布到 L1。

**存储架构**：

```
Private DA Server
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌───────────────┐    ┌───────────────────────────────────┐ │
│  │  HTTP API      │    │  Encrypted Storage Backend        │ │
│  │  (GenericComm-  │    │                                   │ │
│  │   itment 接口)  │───→│  PostgreSQL + AES-256-GCM 列加密  │ │
│  │                │    │  OR                               │ │
│  │  PUT /put      │    │  S3-compatible (SSE-KMS 加密)     │ │
│  │  GET /get      │    │                                   │ │
│  │  AUTH: mTLS    │    │  数据结构:                         │ │
│  │  + API Key     │    │  {commitment_hash, encrypted_data, │ │
│  │                │    │   block_number, batch_index,       │ │
│  └───────────────┘    │   timestamp, retention_policy}     │ │
│                        └───────────────────────────────────┘ │
│                                                              │
│  ┌───────────────┐    ┌───────────────────────────────────┐ │
│  │  Key Mgmt      │    │  Access Control                   │ │
│  │  (HSM/KMS)     │    │  mTLS 客户端证书 + API Key        │ │
│  │  AES-256 密钥  │    │  审计日志（所有访问记录）           │ │
│  │  轮换策略       │    │  IP 白名单                        │ │
│  └───────────────┘    └───────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

**密钥管理**：
- 数据加密密钥 (DEK): AES-256-GCM，每 24 小时自动轮换
- 密钥加密密钥 (KEK): 存储在 HSM（Google Cloud KMS / AWS KMS / HashiCorp Vault）
- Mantle 已有 HSM 集成实践（`op-service/hsm/hsm_signer.go` 支持 Google Cloud KMS，WHI-341 §2.11）

**GDPR 合规设计**：
- 链下数据库由运营商完全控制，支持物理删除（满足"被遗忘权"）
- L1 上仅有 commitment hash（不包含个人数据），无需删除
- 数据保留策略可配置（如金融监管要求保留 5-7 年后自动清理）

> **Evidence**: WHI-338 §4.4 — "Validium 的链下 DA 模型使其成为最 GDPR 友好的架构"；WHI-350 §4.2 关键技术决策 1 — "基于 op-alt-da GenericCommitment 接口实现"

#### 2.2.5 隐私交易元数据（L1 可见信息）

隐私交易在 L1 上**仅**提交以下信息：

| L1 可见信息 | 内容 | 目的 |
|------------|------|------|
| **Commitment hash / segment root** | 私有片段的 Merkle root，以及对 root+metadata 的外层 commitment | 数据完整性锚定——授权节点可对单笔交易或整段数据做存在性验证 |
| **批次元数据** | 批次编号、时间戳、交易数量（不含交易内容） | 排序证明——保证隐私批次存在于全局排序中 |
| **状态根** | 包含隐私交易结果的全局状态根 | 状态验证——通过 Fault Proof 或 ZK Proof 验证 |

**L1 不可见信息**：交易发送方/接收方地址、交易金额、calldata 参数、合约调用详情。

**Commitment Scheme 设计**：

```
Phase 2 (推荐: Merkle Segment commitment):
  merkle_root = build_merkle_tree([tx1, tx2, ..., txN])
  commitment = keccak256(merkle_root ‖ batch_metadata ‖ segment_positions)
  
  优点: 支持 Merkle Proof 导出——可选择性证明某笔交易存在于批次中
       保持 `GenericCommitment` 的外部接口不变，只是把 payload 结构化
  缺点: 需要实现 Merkle Tree 构建和验证逻辑

Phase 2 MVP 兜底 (简单 Keccak256 commitment):
  commitment = keccak256(rlp_encode(private_batch_data))
  
  优点: 零额外密码学工程，最快可上线
  缺点: 不能做单笔交易证明，只能导出整批数据

Phase 3 (延续 Merkle commitment + ZK 证明):
  在 Phase 2 的 Merkle segment 结构之上叠加 validity proof
  无需再次重构披露接口
```

**推荐 Phase 2 直接采用 Merkle Segment commitment**。原因有二：
1. review 要求中的选择性披露和审计证明在工程上依赖单笔证明能力，若先上纯 `keccak256(batch)`，后续还要二次迁移接口；
2. `op-alt-da` 的 `GenericCommitment` 只要求提交一个 commitment 字节串，不限制内部必须是单层 Keccak，因此仍符合最小侵入原则。

> **Evidence**: WHI-341 §2.10 — "op-alt-da 支持 Keccak256 commitments (with on-chain challenge mechanism) 和 Generic commitments"

### 2.3 DA 层改造

#### 2.3.1 当前 DA 流程

```
op-batcher → 收集 L2 交易 → 编码为 frames → 提交到 L1 (blobs/calldata)
所有数据公开可访问，任何人可重构完整 L2 状态
```

#### 2.3.2 改造后：双模式 DA

```
op-batcher (+ Hybrid DA Router)
  │
  ├─ 公开部分 → Mode A: Standard L1 DA
  │    │  编码: 标准 Mantle blob format + 私有片段引用
  │    │  目标: Batch Inbox (L1 EOA)
  │    └─ 结果: 任何人可读取公开交易和私有片段位置/承诺
  │
  └─ 隐私部分 → Mode B: Private DA + L1 Commitment
       │  数据: 加密后存入 Private DA Server
       │  承诺: private segment root 提交到 L1 DA Commitment Registry
       └─ 结果: 仅授权方可读取私有交易正文
```

#### 2.3.3 Hybrid DA Router 设计

**模块位置**: `op-batcher/batcher/hybrid_da_router.go` (新增)

**核心逻辑**: 在 `op-batcher` 的 `blockLoadingLoop` 中，将单个 L2 区块编码为**一个公开 batch envelope + 零到多个私有 segment**，而不是拆成两条相互独立的批次。

```go
// hybrid_da_router.go (新增)
type HybridDARouter struct {
    publicDA   batcher.DABackend      // 标准 L1 DA (blobs/calldata)
    privateDA  altda.DAClient         // Private DA Server (op-alt-da HTTP client)
    classifier PrivacyClassifier      // 交易分类器（从 Sequencer 传递分类结果）
}

type PrivateSegmentRef struct {
    StartIndex   uint32
    TxCount      uint32
    SegmentRoot  common.Hash
    CommitmentID common.Hash
}

type BatchEnvelope struct {
    PublicTransactions []*types.Transaction
    PrivateRefs        []PrivateSegmentRef
}

// RouteBatch 将单个区块编码为公开 envelope + 私有 segment
func (r *HybridDARouter) RouteBatch(batch *Batch) (*BatchEnvelope, []*PrivateSegment, error) {
    // 1. 保留原始排序顺序
    // 2. 公开交易直接进入 envelope
    // 3. 隐私交易按连续区段打包、加密、上传到 Private DA
    // 4. 将 {位置, tx 数量, segment root, commitment id} 写入 envelope
}
```

**关键设计决策**：

| 决策 | 选择 | 理由 |
|------|------|------|
| 同一批次是否可包含公开+隐私交易？ | **是**（单一 envelope + 私有 segment 引用） | 保留单一排序序列，避免引入第二条逻辑链 |
| 隐私交易的顺序证明 | 在 envelope 中记录私有 segment 的起始位置、交易数量和 segment root | 授权节点可无歧义重建完整区块顺序 |
| 批次提交原子性 | 公开 envelope 和私有 commitment 在同一 L1 交易中提交 | 避免 L1 看到的批次索引与私有 DA 中的数据错位 |

**节点模型**：
- **授权 derivation/verifier 节点**：持有 Private DA 读取凭证，能根据 envelope 中的 `PrivateSegmentRef` 重建完整区块并独立验证状态
- **公开 reader 节点**：只能看到公开 envelope 和脱敏 RPC 结果，不能独立重放包含隐私交易的完整链历史

这意味着 Phase 2 从"任何人都能自助重建链"转为"授权节点可重建，公众通过托管 RPC 消费 redacted 视图"。这是 Validium 路径的核心 tradeoff，需要在产品和合规叙事中明确声明。

#### 2.3.4 Private DA Server 接口

基于 `op-alt-da` 的 `DAClient` HTTP 接口实现：

```
PUT /put
  Request:  encrypted_batch_data (bytes)
  Response: commitment (GenericCommitment)
  Auth:     mTLS + API Key
  加密:     AES-256-GCM (DEK from HSM)

GET /get?commitment={hex}
  Request:  commitment hash
  Response: decrypted_batch_data (bytes)
  Auth:     mTLS + API Key + RBAC role check
  审计日志: 记录请求者身份、时间、查询范围
```

**存储架构选项**：

| 选项 | 适用场景 | 优缺点 |
|------|---------|--------|
| **企业自持 PostgreSQL** | 单一运营商、数据主权要求高 | ✅ 完全控制 ✅ 已有运维经验 ❌ 单点故障 |
| **S3-compatible (加密)** | 需要高可用和弹性存储 | ✅ 高可用 ✅ 自动备份 ❌ 依赖云厂商 |
| **分布式存储 (IPFS+加密)** | 多运营商联盟场景 | ✅ 去中心化 ❌ 性能不确定 ❌ 复杂度高 |

**推荐 Phase 2 采用"PostgreSQL + S3 备份"混合方案**——主存储使用加密 PostgreSQL（毫秒级查询），异步备份到 S3 KMS 加密存储。

> **Evidence**: WHI-341 §2.10 — "HTTP-based DA server interface with S3/file backends"；WHI-350 §1.2.6 — "op-alt-da 可插拔框架为 Validium 后端提供清晰的工程路径"

#### 2.3.5 隐私-性能权衡

| 维度 | 公开路径基线 | 隐私路径变化 | 影响评估 |
|------|-------------|-------------|---------|
| **Sequencer 分类延迟** | 无额外分类 | Registry 缓存查询 + 规则判断 | 低，内存命中下接近常数开销 |
| **Batch 提交延迟** | 直接发 blob/calldata | 需等待 Private DA 持久化确认后再发 L1 envelope | 中，私有 DA SLA 将成为出块尾延迟的一部分 |
| **验证节点同步** | 任何节点都可从 L1 重建 | 仅授权节点可从 Private DA 拉取 segment | 高，这是 Phase 2 最大架构 tradeoff |
| **审计证明成本** | 公开数据直接读取 | 需经授权并生成 Merkle proof / 批次导出 | 中，换来对外隐私 |
| **存储成本** | L1 DA 成本高、链下运维低 | L1 DA 成本下降、链下存储/备份/密钥管理成本上升 | 中，成本从 gas 转为企业运维 |

**结论**：Phase 2 的性能代价主要不在 EVM 执行，而在"私有 DA 写入确认"和"公开可重建性丧失"。因此工程实施时应把 Private DA 的可用性、写入确认 SLA、灾备切换时间视为与 Sequencer 同级的核心指标。

### 2.4 执行层改造 (op-geth)

#### 2.4.1 设计目标：最小化 EVM 修改

**核心原则**：EVM 执行引擎本身**不做修改**。隐私交易和公开交易在 EVM 内的执行逻辑完全相同——隐私的实现在 DA 层和访问控制层，而非执行层。

**理由**：
1. EVM 兼容性是 Mantle 的核心优势和企业改造的底线约束（WHI-350 §1.2.8）
2. 修改 EVM 执行逻辑会破坏 Solidity/Hardhat/Foundry 等标准工具链的兼容性
3. Prividium 已证明可以在不修改 EVM 的前提下实现完整隐私（WHI-338 §5）

**但需要强调一个边界**：Phase 2 的"不改 EVM"并不意味着"任意 Solidity 代码都自动得到隐私"。只有运行在隐私合约域中的合约、遵守不向公开状态/事件泄露信息的合约，才能获得预期隐私属性。这个约束必须被视为平台规则，而不是可选最佳实践。

#### 2.4.2 需要修改的 op-geth 组件

| 组件 | 修改内容 | 侵入性 |
|------|---------|--------|
| **Tx Pool** (`core/txpool/`) | 添加隐私交易标记识别（如果使用新交易类型），或仅传递 Sequencer 的分类结果 | 低 |
| **Receipt 处理** | 隐私交易的 receipt 中过滤敏感字段（接收方地址、事件日志），仅对授权方可见 | 低 |
| **RPC 层** (`internal/ethapi/api.go`) | `eth_getTransactionReceipt` 和 `eth_getBlockByNumber` 等 RPC 返回结果中，对未授权请求隐藏隐私交易详情 | 中 |
| **新增 Predeploy** | Privacy Registry Predeploy + Selective Disclosure Predeploy | 低（参照已有 predeploy 模式） |

#### 2.4.3 隐私交易 Receipt 处理

**Privacy Receipt Handler 设计**：

```
标准 Receipt:
{
  transactionHash: "0x...",
  from: "0xAlice...",
  to: "0xContract...",
  logs: [{ topic: "Transfer", data: "..." }],
  status: 1,
  gasUsed: 21000
}

隐私 Receipt (未授权视图):
{
  transactionHash: "0x...",
  from: "REDACTED",
  to: "REDACTED",
  logs: [],           // 事件日志完全隐藏
  status: 1,          // 执行状态仍可见（成功/失败）
  gasUsed: 21000,     // gas 消耗仍可见
  isPrivate: true     // 标记为隐私交易
}

隐私 Receipt (授权视图 — 通过 Selective Disclosure API):
{
  // 完整 receipt，与标准格式相同
  // 需要持有 Viewing Key 或通过认证 RPC 的角色检查
}
```

**实现方式**: 在 `internal/ethapi/api.go` 的 RPC handler 中添加中间件，检查请求者的授权状态：
- 持有 Viewing Key → 返回完整 receipt
- 通过认证 RPC 且角色为 Auditor/Admin → 返回完整 receipt
- 其他情况 → 返回 redacted receipt

#### 2.4.4 隐私状态读取访问控制

**问题**: 隐私合约的状态变量如何防止未授权读取？

**设计方案**: **RPC 层过滤**（不修改 EVM 状态存储）

```
eth_call / eth_getStorageAt 请求
  │
  ├─ 目标合约在 Privacy Registry 中？
  │    ├─ 否 → 正常返回
  │    └─ 是 → 检查请求者授权
  │         ├─ 持有 Viewing Key → 正常返回
  │         ├─ 认证 RPC + Auditor/Admin 角色 → 正常返回
  │         └─ 其他 → 返回 "access denied" 错误
  │
  注意: L2 节点本地仍持有完整状态 (与 Prividium 模型一致)
        访问控制在 RPC 层实现，不在存储层
```

**设计权衡**: 本方案**不防止节点运营者直接读取 LevelDB/MDBX 数据库**——这与 Prividium 模型一致（运营商持有完整可见性是设计特性，WHI-338 §1.1）。隐私的对象是**外部观察者**，不是运营商。

#### 2.4.5 新增 Predeploy 合约

**Privacy Registry Predeploy** (地址: `0x4200000000000000000000000000000000000030`)

```solidity
// Privacy Registry — 管理隐私合约地址列表
interface IPrivacyRegistry {
    // 注册合约为隐私模式
    function registerPrivateContract(address target) external onlyAdmin;
    
    // 取消注册
    function deregisterPrivateContract(address target) external onlyAdmin;
    
    // 查询是否为隐私合约
    function isPrivateContract(address target) external view returns (bool);
    
    // 批量查询
    function getPrivateContracts() external view returns (address[] memory);
    
    // 事件（用于 Sequencer 缓存刷新）
    event ContractRegistered(address indexed target, address indexed registrar);
    event ContractDeregistered(address indexed target, address indexed registrar);
}
```

**Selective Disclosure Predeploy** (地址: `0x4200000000000000000000000000000000000031`)

```solidity
// Selective Disclosure — 管理查看密钥授权
interface ISelectiveDisclosure {
    // 授予查看权限（管理员操作）
    function grantViewingAccess(
        address viewer,        // 被授权方地址
        address target,        // 目标隐私合约
        uint256 expiryTime,    // 过期时间
        uint8 accessLevel      // 0=none, 1=receipt, 2=state, 3=full
    ) external onlyAdmin;
    
    // 撤销查看权限
    function revokeViewingAccess(address viewer, address target) external onlyAdmin;
    
    // 查询查看权限
    function hasViewingAccess(
        address viewer, 
        address target
    ) external view returns (bool, uint8 accessLevel);
    
    // 事件
    event ViewingAccessGranted(address indexed viewer, address indexed target, uint8 level);
    event ViewingAccessRevoked(address indexed viewer, address indexed target);
}
```

**部署方式**: 通过 Mantle 风格的升级 deposit 交易部署（参照 `arsia_upgrade_transactions.go` 模式，WHI-341 §2.1）。使用 `DELEGATECALL` 代理模式实现可升级性。

> **Evidence**: WHI-341 §7.3 — "Identity registry predeploy at a reserved address (e.g., 0x4200000000000000000000000000000000000020+)"；WHI-350 §5.1 R1 — "Predeploy 优先原则"

### 2.5 验证层改造

#### 2.5.1 核心矛盾

Mantle 当前使用 Optimistic Rollup 模型：安全性依赖于 7 天挑战期内的 Fault Proof。Fault Proof 需要**完整的交易数据**才能重放和验证状态转换。

**矛盾**: 隐私交易的数据不在 L1 → 挑战者无法获取数据 → 无法执行 Fault Proof → 安全模型被破坏。

#### 2.5.2 解决方案：分阶段过渡

```
Phase 2: 委任验证 (Delegated Verification)
  │
  │  隐私交易的验证由"受信任挑战者集合"执行
  │  这些挑战者拥有 Private DA Server 的访问权限
  │  安全假设: 至少 1 个挑战者是诚实的（与标准 Optimistic 相同）
  │
  │  实现: 在 DisputeGame 合约中添加 "DelegatedChallenger" 角色
  │        仅授权地址可发起针对隐私批次的挑战
  │        挑战过程中，Private DA Server 向挑战者提供数据
  │        kona/challenger 侧增加私有 witness 获取适配器
  │
  ▼
Phase 3: ZK 有效性证明 (Validity Proof)
  │
  │  从 Optimistic 切换为 ZK Rollup 验证
  │  ZK 证明保证状态转换正确性，无需公开交易数据
  │  任何人可在 L1 验证证明，无需访问原始数据
  │
  │  实现: 替换 kona Fault Proof 为 ZK Prover
  │        L1 验证合约接受 STARK/SNARK 证明
  │        证明中包含隐私交易的正确性保证
  │
  └─ 结果: Validium 模式在密码学层面完全合理
           (与 Prividium 架构一致, WHI-338 §2.3)
```

#### 2.5.3 Phase 2: 委任验证方案详细设计

```
隐私批次验证流程:

1. op-proposer 提交包含隐私交易状态的 output root 到 L1
   (output root 覆盖公开和隐私交易的全局状态)

2. 挑战窗口开启 (标准 7 天)

3. 如果挑战者检测到异常:
   a. 授权挑战者从 Private DA Server 获取隐私批次数据
      (通过 mTLS + 挑战者专用 API Key)
   b. 挑战者在本地重放隐私交易
   c. 如果状态不一致，向 L1 DisputeGame 合约提交挑战
   d. 挑战的 bisection game 在受控环境中执行
      (仅授权节点参与，数据不公开)

4. 安全保证:
   - 至少 1 个诚实的授权挑战者 → 与标准 Optimistic 等价
   - 挑战者集合由企业联盟管理 (如运营商 + 审计方 + 监管方)
   - 挑战者数量建议: 最少 3 个，分属不同组织
```

**工程含义**：Phase 2 不能简单理解为"完全不动 kona"。Proof 语义可以保持 Optimistic，但 challenger/client 侧至少需要：
- 一个 private witness fetcher/preimage adapter，用 commitment id 拉取私有 segment
- 一套 challenger 凭证与审计日志机制，证明谁在何时读取了哪段私有数据
- 对"仅授权挑战者可挑战私有批次"的合约校验和客户端错误处理

**安全降级评估**：

| 安全属性 | 标准 Optimistic | 委任验证 Validium | 降级程度 |
|---------|----------------|------------------|---------|
| 状态转换正确性 | 任何人可挑战 | 授权方可挑战 | **中度降级** — 挑战者集合受限 |
| 活性假设 | 至少 1 个诚实节点能获取数据 | 至少 1 个授权挑战者能获取数据 | **轻微降级** — 从公开集合变为授权集合 |
| 抗审查 | L1 强制交易 | L1 强制交易 + Bridge 白名单 | **中度降级** — Bridge 白名单限制了逃生路径 |
| 数据可用性 | 以太坊保证 | 运营商保证 | **显著降级** — 但对企业场景可接受 |

**风险缓解**：
1. 挑战者集合需包含至少一个独立第三方（如审计事务所）
2. Private DA Server 实现"挑战者优先"策略——挑战请求优先级最高
3. 定期（每周）执行"挑战演练"——验证挑战流程端到端可用
4. 保留公开交易的标准 Fault Proof 机制不变

> **Evidence**: WHI-338 §1.1 — "运营商是唯一的数据源…但 ZK 证明保证即使运营商作恶也无法伪造状态转换"；WHI-350 §5.2 R3 — "渐进式安全迁移"

#### 2.5.4 Phase 3: ZK 有效性证明目标架构

```
目标: 替换 kona Fault Proof → ZK Prover + L1 Verifier

Prover:
  ├─ 输入: 隐私批次数据 (从 Private DA Server 获取)
  ├─ 计算: STARK 证明 (使用 Airbender 或 SP1 RISC-V Prover)
  └─ 输出: ZK Proof + 新状态根

L1 Verifier:
  ├─ 输入: ZK Proof + 旧状态根 + 新状态根
  ├─ 验证: STARK 验证算法 (O(log n) 复杂度)
  └─ 输出: 接受/拒绝状态转换

证明保证:
  ✅ 状态转换正确性 (数学保证)
  ✅ 所有交易遵循 EVM 规则
  ❌ 不暴露任何交易内容
  ✅ 任何人可独立验证证明 (L1 上)
```

**kona 改造路径**: Mantle 的 kona 已有 RISC-V 目标编译支持（WHI-341 §2.8），`no_std` 兼容的执行器可以作为 ZK Prover 的 guest 程序。Tempo Zones 的 SP1 RISC-V 兼容设计（WHI-340 §6）提供了直接参考。

---

## 第三章：数据流设计

### 3.1 完整数据流图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户/企业客户                                 │
│                                                                     │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐                   │
│  │ 公开交易  │     │ 隐私交易  │     │ 查看请求  │                   │
│  │ (标准 tx) │     │ (to 隐私  │     │ (receipt/ │                   │
│  │          │     │  合约)    │     │  state)   │                   │
│  └────┬─────┘     └────┬─────┘     └────┬─────┘                   │
└───────┼────────────────┼────────────────┼──────────────────────────┘
        │                │                │
        ▼                ▼                ▼
┌───────────────────────────────────────────────────────────────────┐
│  Layer 0: 认证 RPC 网关 (Phase 1)                                  │
│                                                                   │
│  JWT 验证 → 身份确认 → 角色检查 → 请求转发                          │
│  未认证请求 → 403 Forbidden                                       │
└──────────┬────────────────┬────────────────┬──────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌───────────────────────────────────────────────────────────────────┐
│  Layer 1: op-geth (Execution Layer)                               │
│                                                                   │
│  Tx Pool                  Privacy Filter        RPC Handler       │
│  ┌─────────┐              ┌─────────┐          ┌─────────┐      │
│  │ 验证交易 │              │ 标记隐私 │          │ 权限检查 │      │
│  │ gas/nonce│              │ 交易标签 │          │ 过滤响应 │      │
│  └────┬────┘              └────┬────┘          └────┬────┘      │
│       │                       │                     │            │
│       ▼     Engine API        ▼                     │            │
└───────┼───────────────────────┼─────────────────────┼────────────┘
        │                       │                     │
        ▼                       ▼                     │
┌───────────────────────────────────────────────┐     │
│  Layer 2: op-node Sequencer                    │     │
│                                               │     │
│  ┌──────────────────────────────────────────┐ │     │
│  │  Privacy Classifier                       │ │     │
│  │                                          │ │     │
│  │  查询 Privacy Registry Predeploy 缓存    │ │     │
│  │  tx.to ∈ private_contracts?              │ │     │
│  │    ├─ 否 → 写入公开 envelope              │ │     │
│  │    └─ 是 → 写入 private segment           │ │     │
│  └──────────────┬──────────────┬────────────┘ │     │
│                 │              │               │     │
│         public envelope  private segment       │     │
└─────────────────┼──────────────┼───────────────┘     │
                  │              │                      │
                  ▼              ▼                      │
┌─────────────────────────────────────────────────┐    │
│  Layer 3: op-batcher (Hybrid DA Router)          │    │
│                                                  │    │
│  ┌──────────────────┐  ┌──────────────────────┐ │    │
│  │ Public Path       │  │ Private Path          │ │    │
│  │                  │  │                      │ │    │
│  │ frames → blobs   │  │ encrypt(data)        │ │    │
│  │ → L1 Batch Inbox │  │ → Private DA Server  │ │    │
│  │                  │  │ commitment →         │ │    │
│  │                  │  │   L1 DA Commitment   │ │    │
│  │                  │  │   Registry           │ │    │
│  └────────┬─────────┘  └──────────┬───────────┘ │    │
└───────────┼───────────────────────┼──────────────┘    │
            │                       │                    │
            ▼                       ▼                    │
┌───────────────────────────────────────────────────┐   │
│  ETHEREUM L1                                       │   │
│                                                    │   │
│  ┌──────────────┐  ┌────────────────────────────┐ │   │
│  │ Batch Inbox   │  │ DA Commitment Registry     │ │   │
│  │ (公开批次     │  │ (隐私批次 commitment hash) │ │   │
│  │  完整数据)    │  │                            │ │   │
│  └──────────────┘  └────────────────────────────┘ │   │
│                                                    │   │
│  ┌──────────────────────────────────────────────┐ │   │
│  │ DisputeGame Factory                           │ │   │
│  │  + Delegated Challenger (隐私批次验证)         │ │   │
│  └──────────────────────────────────────────────┘ │   │
└────────────────────────────────────────────────────┘   │
                                                         │
┌────────────────────────────────────────────────────┐   │
│  Private DA Server (运营商控制)                      │   │
│                                                    │   │
│  ┌──────────┐  ┌────────────┐  ┌───────────────┐ │   │
│  │ Encrypted │  │ Key Mgmt   │  │ Selective     │◄┼───┘
│  │ Storage   │  │ (HSM/KMS)  │  │ Disclosure    │ │
│  │ (PG+S3)  │  │            │  │ API           │ │
│  └──────────┘  └────────────┘  └───────────────┘ │
└────────────────────────────────────────────────────┘
```

### 3.2 交易生命周期：隐私交易完整流程

```
Step 1: 提交
  用户通过认证 RPC 提交交易 (to = 已注册隐私合约)
  tx: {from: Alice, to: PrivateToken, data: transfer(Bob, 1000)}

Step 2: 分类
  op-node Sequencer 的 Privacy Classifier 检测到
  PrivateToken ∈ Privacy Registry → 标记为隐私交易

Step 3: 执行
  op-geth EVM 正常执行交易（无修改）
  状态更新: Alice.balance -= 1000, Bob.balance += 1000
  生成标准 receipt + events

Step 4: 打包
  Sequencer 保持区块原始交易顺序
  op-batcher 将公开交易写入 public envelope
  将隐私交易折叠为一个或多个 private segment 引用

Step 5: DA 分流
  op-batcher Hybrid DA Router:
  - 生成一个公开 batch envelope → 编码为 blobs → L1 Batch Inbox
  - 将隐私交易整理为一个或多个 private segment → 加密 → Private DA Server
  - 将 {segment root, 起始位置, 数量, commitment id} → L1 DA Commitment Registry

Step 6: 状态提交
  op-proposer 提交全局 output root (覆盖公开+隐私状态)
  output root 包含隐私交易的状态变更结果

Step 7: 查看
  未授权方查询: eth_getTransactionReceipt → redacted receipt
  授权方查询:   Selective Disclosure API → 完整 receipt
  审计方查询:   Viewing Key + Merkle Proof → 可验证的完整数据

Step 8: 验证 (如有挑战)
  授权挑战者从 Private DA Server 获取数据
  → 本地重放 → 验证状态一致性
  → 如不一致，向 L1 提交挑战
```

### 3.3 跨层桥接的隐私保护 (ECIES 加密存款)

借鉴 Tempo Zones 的 ECIES 加密存款方案（WHI-340 §5），保护 L1→L2 存款的接收者隐私：

```
标准存款 (当前):
  L1 OptimismPortal.depositTransaction(to, value, gasLimit, data)
  → L1 事件公开: from, to, value, data 全部可见

加密存款 (改造后):
  1. 用户在链下用 Sequencer 的公钥进行 ECIES 加密:
     encrypted_to = ECIES.encrypt(sequencer_pubkey, to_address)
     encrypted_memo = ECIES.encrypt(sequencer_pubkey, memo_data)
  
  2. 提交到新增的包装合约:
     EnterprisePrivacyPortal.encryptedDeposit(
       encrypted_to,     // ECIES 加密的接收方
       encrypted_memo,   // ECIES 加密的备注
       token,           // 代币地址 (公开)
       amount           // 金额 (公开 — 用于 L1 资产锁定验证)
     )
  
  3. EnterprisePrivacyPortal:
     - 记录 `EncryptedDepositInitiated(depositId, ciphertext, token, amount)`
     - 调用标准 `OptimismPortal.depositTransaction(...)`
       其中 calldata 只携带 `depositId` 和必要路由元数据
     - 因此不要求直接改写 OptimismPortal 的存款语义

  4. L1 事件: token + sender + amount 公开; to + memo 仅出现在包装合约的密文字段中
  
  5. Sequencer 解密:
     sequencer_privkey → ECIES.decrypt → 获取真实 to 和 memo
     → 在 L2 执行存款: mint(to, amount)
  
  6. Chaum-Pedersen 证明 (可选):
     Sequencer 生成证明: "解密的 to 地址与加密 blob 一致"
     → 链上验证 (ChaumPedersen precompile, 6000 gas)
     → 防止 Sequencer 篡改接收方
```

**为何采用包装合约而非直接修改 `OptimismPortal`**：
- 符合 WHI-350 的最小侵入原则，避免把企业隐私逻辑直接焊进 OP Stack 核心桥接合约
- 更容易灰度上线；企业模式失败时可只停用包装合约，不影响标准公开桥
- 对下游钱包/托管方更友好，可以把 `encryptedDeposit` 作为新的企业专用入口而非替换默认桥

**密码学参数** (参照 Tempo Zones, WHI-340 §5.2):
- 椭圆曲线: secp256k1
- 对称加密: AES-256-GCM
- 密钥派生: HKDF-SHA256
- 身份证明: Chaum-Pedersen DLOG 等式证明
- 预编译合约: `ChaumPedersenVerify` at reserved address, 6000 gas

---

## 第四章：选择性披露设计

### 4.1 设计目标

| 披露场景 | 需求 | 技术要求 |
|---------|------|---------|
| **监管审计** | 监管方按需查看特定合约/地址的完整交易历史 | 细粒度权限 + 时间范围过滤 + 审计日志 |
| **外部审计** | 审计事务所验证特定交易的正确性 | Merkle Proof 导出 + 可独立验证 |
| **合规证明** | 向对手方证明"已满足合规要求"但不暴露底层数据 | ZK 合规证明 (Phase 3) |
| **跨机构协作** | 合作方选择性查看部分交易数据 | 按合约/按地址的粒度化授权 |

### 4.2 四种披露机制

#### 机制 1: 查看密钥 (Viewing Key) — Phase 2 首选

```
授权流程:
  管理员 → Selective Disclosure Predeploy
    → grantViewingAccess(viewer, targetContract, expiry, level)
  
查看流程:
  授权方 → 认证 RPC (JWT + 角色)
    → eth_getTransactionReceipt(txHash)
    → RPC 层检查 Viewing Access
    → 返回完整 receipt (含隐私字段)

OR:
  授权方 → Selective Disclosure API
    → GET /api/v1/transactions?contract=0x...&from=2026-01-01&to=2026-06-30
    → 返回时间范围内的完整交易列表

权限级别:
  Level 1: receipt-only (交易 hash、状态、gas)
  Level 2: receipt + state (+ 合约状态读取)
  Level 3: full (+ 事件日志、calldata、内部调用)
```

#### 机制 2: Merkle Proof 导出 — Phase 2

```
场景: 审计事务所需要验证"某笔交易确实存在且被正确执行"

流程:
  1. 管理员授权审计方的 Viewing Key
  
  2. 审计方请求 Merkle Proof:
     GET /api/v1/merkle-proof?txHash=0x...
     
  3. Private DA Server 返回:
     {
       transaction_data: { ... },           // 完整交易数据
       merkle_proof: {
         leaf: keccak256(tx_data),           // 叶节点
         proof: [hash1, hash2, ...],         // Merkle 路径
         root: "0x..."                       // 批次 Merkle 根
       },
       l1_commitment: {
         registry_address: "0x...",          // L1 DA Commitment Registry
         commitment_hash: "0x...",           // L1 上的 commitment
         l1_block_number: 12345678           // commitment 所在的 L1 区块
       }
     }
  
  4. 审计方独立验证:
     a. 验证 Merkle Proof: verify(leaf, proof, root) == true
     b. 验证 root 与 L1 commitment 一致: keccak256(root) == l1_commitment
     c. 验证 L1 commitment 存在于 DA Commitment Registry 中
     → 密码学保证: 此交易确实存在于 Mantle 的隐私批次中
```

**说明**：本机制依赖第二章推荐的 Phase 2 `Merkle Segment commitment`。如果实施时为了抢进度先落到 `keccak256(batch)` MVP，则本机制会降级为"导出整批数据 + 批次 commitment 验证"，不能做单笔证明。

#### 机制 3: 专用审计节点 — Phase 2

```
部署模型:
  ┌──────────────┐
  │ 审计方        │
  │ (监管机构/    │
  │  审计事务所)   │
  │              │
  │ 运行只读      │
  │ Mantle 节点   │◄── 从 Private DA Server 同步隐私批次数据
  │              │     (需授权 + 审计日志)
  │ 本地完整状态  │
  │ 独立验证能力  │
  └──────────────┘

优势:
  - 审计方拥有独立验证能力 (不依赖运营商的 API 返回)
  - 可运行历史重放 (完整审计追踪)
  - 离线分析能力

实现:
  - 标准 Mantle L2 节点 + Private DA 数据源配置
  - op-node derivation pipeline 从 Private DA Server 获取隐私批次
  - 节点启动时验证所有历史批次的 commitment 一致性
```

#### 机制 4: ZK 合规证明 — Phase 3 远期

```
场景: 银行 A 需要向银行 B 证明"我的客户通过了 AML 检查"
      但不能暴露客户的 PII (参照 Prividium ZK 合规证明, WHI-338 §4.1)

流程:
  1. 银行 A 在本地执行 AML 检查
  2. 银行 A 生成 ZK 证明: "客户地址 0x... 不在 OFAC 制裁名单上"
  3. 银行 B 验证 ZK 证明 (链上或链下)
  4. 银行 B 确信合规性，但从未接触任何 PII

技术要求:
  - ZK Prover 基础设施 (STARK/SNARK)
  - 合规证明电路设计
  - L2 上的 ZK Verifier 预编译合约

预计时间: Phase 3 (12-18 月), 依赖 ZK 证明系统迁移完成
```

### 4.3 选择性披露架构总览

```
┌─────────────────────────────────────────────────────────┐
│  Selective Disclosure Service (新增)                      │
│                                                         │
│  ┌──────────────┐  ┌───────────┐  ┌──────────────────┐ │
│  │  REST API     │  │  Auth     │  │  Audit Logger    │ │
│  │              │  │  Module   │  │                  │ │
│  │  /transactions│  │  JWT +    │  │  所有查询请求    │ │
│  │  /merkle-proof│  │  Viewing  │  │  记录到审计日志  │ │
│  │  /state       │  │  Key      │  │  含身份、时间、  │ │
│  │  /compliance  │  │  验证     │  │  查询范围        │ │
│  └──────┬───────┘  └─────┬─────┘  └──────────────────┘ │
│         │                │                               │
│         ▼                ▼                               │
│  ┌──────────────────────────────────────────┐           │
│  │  Data Layer                               │           │
│  │                                          │           │
│  │  Private DA Server  ←→  Identity Registry │           │
│  │  (隐私交易数据)      ←→  Selective Disclosure │       │
│  │                      ←→  Predeploy         │           │
│  └──────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

> **Evidence**: WHI-338 §4.1 — "选择性披露五种技术机制"；WHI-340 §5.3 — "取款支持 revealTo 参数，允许指定方解密发送者信息"

---

## 第五章：具体代码改动点评估

### 5.1 mantle-v2 代码库改动

| # | 文件/模块 | 改动类型 | 改动内容 | Phase | 工作量 |
|---|----------|---------|---------|-------|--------|
| 1 | `op-node/rollup/sequencing/privacy_classifier.go` | **新增** | Privacy Classifier 模块——交易分类逻辑、Privacy Registry 缓存、事件驱动刷新 | 2 | 2-3 周 |
| 2 | `op-node/rollup/sequencing/sequencer.go` | **修改** | 在交易排序流程中注入 Privacy Classifier 检查点；将分类结果传递给 batcher | 2 | 1-2 周 |
| 3 | `op-node/rollup/derive/privacy_da_source.go` | **新增** | Derivation pipeline 新增隐私 DA 数据源——从 Private DA Server 获取隐私批次数据（用于验证节点和审计节点） | 2 | 2-3 周 |
| 4 | `op-node/rollup/derive/data_source.go` | **修改** | `DataSourceFactory.OpenData()` 添加隐私 DA 路由——对于隐私批次，从 Private DA Server 获取数据而非 L1 | 2 | 1 周 |
| 5 | `op-batcher/batcher/hybrid_da_router.go` | **新增** | Hybrid DA Router 模块——接收分类结果，将公开批次发送到 L1、隐私批次发送到 Private DA Server + L1 commitment | 2 | 3-4 周 |
| 6 | `op-batcher/batcher/driver.go` | **修改** | 在 `blockLoadingLoop` 和 `publishingLoop` 中集成 Hybrid DA Router | 2 | 1-2 周 |
| 7 | `op-alt-da/private_da_server.go` | **新增** | Private DA Server 实现——加密存储、许可制检索、HSM 密钥管理、审计日志 | 2 | 4-6 周 |
| 8 | `op-alt-da/daclient.go` | **修改** | 扩展 DAClient 支持 Private DA Server 的 mTLS 认证和加密传输 | 2 | 1 周 |
| 9 | `op-proposer/` | **修改** | 保持 output root 格式不变；新增与 proposal index 关联的私有 segment manifest 发布逻辑 | 2 | 1 周 |
| 10 | L1 合约: `DACommitmentRegistry.sol` | **新增** | L1 上的隐私批次 commitment/segment root 注册表合约 | 2 | 2-3 周 |
| 11 | L1 合约: `EnterprisePrivacyPortal.sol` | **新增** | 企业专用加密存款包装合约，复用标准 `OptimismPortal.depositTransaction()` | 2 | 3-4 周 |
| 12 | L1 合约: `DisputeGameFactory.sol` | **修改** | 添加 `DelegatedChallenger` 角色和隐私批次挑战逻辑 | 2 | 2-3 周 |

### 5.2 op-geth 代码库改动

| # | 文件/模块 | 改动类型 | 改动内容 | Phase | 工作量 |
|---|----------|---------|---------|-------|--------|
| 1 | `core/txpool/privacy_filter.go` | **新增** | 交易池隐私标记过滤——识别隐私交易并附加标签 | 2 | 1-2 周 |
| 2 | `internal/ethapi/api.go` | **修改** | RPC handler 添加隐私过滤中间件——对未授权请求隐藏隐私交易详情（receipt、state、logs） | 2 | 2-3 周 |
| 3 | `internal/ethapi/privacy_middleware.go` | **新增** | Privacy RPC Middleware——查询 Selective Disclosure Predeploy 确认请求者权限，过滤响应 | 2 | 2-3 周 |
| 4 | Predeploy: `PrivacyRegistry.sol` | **新增** | Privacy Registry Predeploy 合约（地址 `0x42...0030`）——隐私合约地址注册/查询 | 2 | 2-3 周 |
| 5 | Predeploy: `SelectiveDisclosure.sol` | **新增** | Selective Disclosure Predeploy 合约（地址 `0x42...0031`）——查看权限管理 | 2 | 2-3 周 |
| 6 | Precompile: `ChaumPedersenVerify` | **新增** (Phase 2 可选) | Chaum-Pedersen DLOG 等式证明验证预编译合约，6000 gas（参照 Tempo Zones 实现） | 2 | 3-4 周 |
| 7 | `core/vm/contracts.go` | **修改** (Phase 2 可选) | 注册 ChaumPedersenVerify 预编译合约地址 | 2 | 1 周 |

### 5.3 kona 代码库改动

| # | 改动内容 | Phase | 需要改动？ |
|---|---------|-------|-----------|
| 1 | **Phase 2: 小规模适配** | 2 | ✅ — proof 语义不变，但 challenger/client 需要增加私有 witness 获取适配器和授权读取流程 |
| 2 | **Phase 2 具体改动** | 2 | `crates/proof/` 或 preimage/witness 读取模块增加 private segment fetch adapter；challenger CLI 增加 mTLS/API Key 配置；错误路径区分公开批次与隐私批次 |
| 3 | **Phase 3: 需要重大改造** | 3 | ✅ — 从 Optimistic (Fault Proof) 迁移到 ZK (Validity Proof) 需要替换整个证明系统 |
| 4 | Phase 3 具体改动 | 3 | `crates/proof/` — 替换为 ZK Prover guest 程序；`bin/client` — 替换为 ZK 证明生成客户端；L1 验证合约 — 从 DisputeGame 替换为 ZK Verifier |

**Phase 2 为何仍需 kona 侧适配**：
- 授权挑战者如果要对隐私批次发起挑战，仍然需要把私有 segment 喂给既有 fault proof/challenger 流程
- 因此"不改 kona"只在狭义的证明语义上成立，在客户端接线、witness 拉取和权限控制上并不成立
- 这类改动比 Phase 3 小得多，但应在工程估算中明确计入

### 5.4 新增独立服务

| # | 服务 | 描述 | Phase | 工作量 |
|---|------|------|-------|--------|
| 1 | **Private DA Server** | 加密数据存储 + 许可制检索 + HSM 密钥管理 | 2 | 4-6 周 |
| 2 | **Selective Disclosure API** | REST API 提供选择性披露功能 + 审计日志 | 2 | 3-4 周 |
| 3 | **Key Management Service** | 企业密钥管理（DEK 轮换、Viewing Key 生成和分发） | 2 | 2-3 周 |
| 4 | **Privacy Admin Dashboard** | Web UI 管理隐私合约注册、查看权限授予、审计日志查询 | 2 | 2-3 周 |

### 5.5 改动总量统计

| 类别 | 新增文件 | 修改文件 | 预估代码行数 |
|------|---------|---------|------------|
| mantle-v2 (Go) | 4 文件 | 4 文件 | ~3,000-4,000 行 |
| op-geth (Go) | 3 文件 | 2 文件 | ~2,000-3,000 行 |
| Predeploy 合约 (Solidity) | 2 合约 | — | ~500-800 行 |
| L1 合约 (Solidity) | 1 合约 | 2 合约 | ~500-800 行 |
| Precompile (Go/Rust) | 1 文件 | 1 文件 | ~300-500 行 |
| 独立服务 (Go) | 4 服务 | — | ~4,000-6,000 行 |
| **合计** | **~15 文件** | **~9 文件** | **~10,000-15,000 行** |

> **Evidence**: WHI-341 附录 A (Repository Map); WHI-350 附录 A (代码改造点速查表)

---

## 第六章：技术风险和限制

### 6.1 风险矩阵

| # | 风险 | 可能性 | 影响 | 风险等级 | 缓解策略 |
|---|------|--------|------|---------|---------|
| R1 | **委任验证安全性低于标准 Optimistic** | 高 | 高 | **High** | 挑战者集合至少包含 1 个独立第三方；定期挑战演练；Phase 3 迁移到 ZK 后消除此风险 |
| R2 | **Private DA Server 成为单点故障** | 中 | 高 | **High** | 多可用区部署 + S3 异步备份 + 灾难恢复演练；SLA 保障 99.9%+ 可用性 |
| R3 | **运营商删除数据导致状态不可重构** | 低 | 极高 | **High** | 加密快照 + 异地备份 + 审计方持有独立副本；保留"最后已知状态"的 L1 锚定 |
| R4 | **EVM 兼容性破坏** | 低 | 极高 | **Critical** | Predeploy 优先原则（不修改 EVM 核心）；持续兼容性测试套件；灰度发布 |
| R5 | **ECIES 加密实现缺陷** | 低 | 高 | **Medium** | 复用成熟密码学库 (`go-ethereum/crypto`, `libsodium`)；独立密码学审计 |
| R6 | **OP Stack 分叉维护负担增加** | 高 | 中 | **Medium** | 企业代码放在独立目录 (`enterprise/`)；通过 Go interface 与核心交互；分叉预算管理 |
| R7 | **隐私分类器误判导致数据泄露** | 中 | 高 | **High** | 默认安全策略（如有疑虑，走隐私路径）；注册表变更需双人审批；实时监控分类结果 |
| R8 | **混合 DA 路由引入批次一致性问题** | 中 | 中 | **Medium** | 公开 envelope 和隐私 commitment 在同一 L1 交易中原子提交；全局排序由 Sequencer 保证 |
| R9 | **Private DA 写入延迟拖慢出块尾延迟** | 中 | 中 | **Medium** | 对 Private DA 设置写入确认 SLA；允许小批量 segment flush；将写入超时视为批次失败而非静默降级 |

### 6.2 已知限制

| 限制 | 描述 | 影响 | 缓解 |
|------|------|------|------|
| **运营商完全可见性** | Sequencer 和 Private DA Server 运营商可看到所有隐私交易明文 | 隐私对象是"外部观察者"而非运营商 | 对企业场景可接受——运营商=企业自身（WHI-338 §1.1）。如需更强隐私（运营商也不可见），需 Phase 3 的 ZK 方案 |
| **L1 逃生路径受限** | 隐私交易的数据不在 L1，用户无法独立从 L1 重构状态 | 资金提取依赖运营商活性 | Validium 模型的固有特性；通过灾难恢复预案和审计方独立副本缓解 |
| **公开 full node 兼容性下降** | 不持有 Private DA 凭证的节点无法独立重放包含隐私交易的完整链历史 | 生态从"完全开放验证"降级为"授权验证 + 托管读取" | 作为企业模式的显式取舍；保留公开模式链或公开子网供非敏感业务使用 |
| **Phase 2 仍非硬隔离多租户** | 不同企业客户的隐私主要靠访问控制和合约域隔离，而非独立 Zone | 多租户强隔离不足 | Phase 3 迁移到 Zone/子链架构实现每租户独立执行环境 |
| **交易级 gas 侧信道** | 隐私交易的 gas 消耗仍然公开可见，可能泄露交易复杂度信息 | 外部观察者可推断交易类型 | Phase 3 参考 Tempo Zones 的固定 gas 成本方案（100,000 gas/操作，WHI-340 §7.2）防止侧信道 |
| **不支持交易级混合模式** | Phase 2 以合约地址为粒度分类隐私/公开，不支持同一合约的部分函数隐私 | 粒度限于合约级 | Phase 3 支持函数选择器级分类或新交易类型 |

### 6.3 隐私-性能 tradeoff 总结

Phase 2 的主要收益是把敏感业务数据从公开 L1 DA 中移除，并保留 EVM 兼容和单 Sequencer 架构；主要代价则是：
- 公共可重建性下降，验证者集合从"任何人"收缩到"授权节点"
- 出块尾延迟与 Private DA 的写入确认绑定
- 选择性披露、审计和挑战流程都转化为有状态的企业运维能力，而不是单纯的链上特性

因此，从产品定位上，Phase 2 更像"企业可用的许可式隐私 L2 模式"，而不是继续维持公链式的完全开放可验证体验。

### 6.4 与 Phase 1 准入控制的依赖关系

隐私层设计**依赖** Phase 1 的准入控制基础设施：

| Phase 1 依赖项 | 隐私层使用方式 |
|---------------|--------------|
| **认证 RPC 网关** | 所有隐私交易提交和数据查询都通过认证 RPC，确保身份可追溯 |
| **Identity Registry Predeploy** | Privacy Registry 和 Selective Disclosure 基于 Identity Registry 的身份凭证进行权限检查 |
| **Sequencer 策略引擎** | Privacy Classifier 作为策略引擎的扩展模块集成 |
| **L1 Bridge 白名单** | 加密存款功能在 Bridge 白名单的基础上添加 ECIES 加密逻辑 |

---

## 附录 A：改造时间线

```
Phase 2 (6-9 月) — 隐私层改造并行执行计划

月份:    1    2    3    4    5    6    7    8    9

        ┌──────────────┐
私有DA  │ Private DA    │
Server  │ Server 开发    │
        └──────┬───────┘
               │
        ┌──────┴──────────────────────────────┐
混合DA  │ Hybrid DA Router + Batcher 集成      │
路由    │                                      │
        └─────────────────────────────────────┘

        ┌─────────────────────────┐
Privacy │ Classifier + Sequencer  │
分类器  │ 集成 + 测试              │
        └─────────────────────────┘

        ┌──────────────────────┐
Predeploy│ Privacy Registry +   │
合约    │ Selective Disclosure  │
        └──────────────────────┘

             ┌──────────────────────────┐
执行层  　　 │ op-geth Privacy Middleware │
改造         │ + Receipt Handler         │
             └──────────────────────────┘

                  ┌──────────────────────────┐
选择性         　 │ Selective Disclosure API  │
披露               │ + Merkle Proof 导出      │
                  └──────────────────────────┘

                       ┌──────────────────────────┐
加密桥接           　  │ ECIES 加密存款/取款       │
                       │ + Chaum-Pedersen 预编译   │
                       └──────────────────────────┘

                            ┌──────────────────────┐
验证层                  　  │ 委任验证方案          │
改造                        │ + 挑战者集合部署      │
                            └──────────────────────┘

                                 ┌─────────────────┐
集成测试                     　  │ 端到端集成测试   │
                                 │ + 安全审计       │
                                 └─────────────────┘

团队规模: 4-5 名工程师 (含密码学专家) + 2 名智能合约工程师
预估总工作量: ~30-40 人月
```

## 附录 B：与 M2/M3 结论的映射

| M2/M3 结论 | 本设计对应 | 应用方式 |
|-----------|----------|---------|
| Validium 模式适合单运营商企业链 (WHI-343 §3.2) | Phase 2 核心方案 | 直接采纳——Mantle 单 Sequencer 天然匹配 |
| `op-alt-da` 可插拔框架 (WHI-341 §2.10) | Private DA Server 基于 `GenericCommitment` 接口 | 直接采纳——零核心协议修改 |
| Sequencer 完整可见性是合规资产 (WHI-346 §2.2.5) | 运营商持有完整隐私数据 = 天然合规控制点 | 直接采纳——不追求 Canton 式信任最小化 |
| Predeploy 优于 Precompile (WHI-344 §4.3) | Privacy Registry + Selective Disclosure 均为 Predeploy | 直接采纳——可升级、不需硬分叉 |
| ECIES 加密存款 (WHI-340 §5) | L1→L2 桥接的接收者隐私保护 | 技术借鉴——密码学参数直接参照 Tempo Zones |
| Merkle Proof 导出 (WHI-338 §4.1) | Phase 2 Merkle Segment commitment 支持选择性交易证明 | 直接采纳——如为赶进度退回 Keccak MVP，则该能力同步降级 |
| ZK 合规证明 (WHI-338 §4.1) | Phase 3 密码学合规证书 | 远期目标——依赖 ZK Prover 基础设施 |
| 混合 DA 方案 (WHI-345 §3.3) | Hybrid DA Router 实现公开+隐私双路径 | 直接采纳——同一批次中不同交易使用不同 DA |
| 委任验证过渡方案 | Phase 2 Delegated Challenger 方案 | 新设计——平衡隐私需求和安全保证 |
| ZK 化是长期必由之路 (WHI-347 §6.1) | Phase 3 目标——替换 kona 为 ZK Prover | 长期目标——kona 的 RISC-V 支持为此奠定基础 |

## 附录 C：术语对照

| 术语 | 英文 | 在本设计中的含义 |
|------|------|----------------|
| 隐私分类器 | Privacy Classifier | Sequencer 中的模块，判断交易是否走隐私路径 |
| 混合 DA 路由 | Hybrid DA Router | Batcher 中的模块，将公开和隐私批次分流到不同 DA |
| 私有 DA 服务器 | Private DA Server | 运营商控制的加密数据存储服务 |
| 委任验证 | Delegated Verification | 由授权挑战者集合验证隐私交易的过渡方案 |
| 查看密钥 | Viewing Key | 允许特定方查看隐私交易详情的授权凭证 |
| 加密存款 | Encrypted Deposit | 使用 ECIES 加密接收方地址的 L1→L2 存款 |
| 隐私注册表 | Privacy Registry | Predeploy 合约，管理隐私合约地址列表 |
| 选择性披露 | Selective Disclosure | 按需向授权方提供隐私数据访问的机制 |
| DA 承诺注册表 | DA Commitment Registry | L1 合约，存储隐私批次的 commitment hash |

---

## 数据来源

| 来源编号 | 文件 | 主要贡献 |
|---------|------|---------|
| WHI-341 | `m1-research/mantle/mantle-v2-architecture-baseline.md` | Mantle V2 架构基线、组件接口、自然插入点、op-alt-da 框架 |
| WHI-343 | `m2-comparison/privacy/WHI-343-privacy-comparison.md` | 三种隐私范式对比、Mantle 适用性分析、组合策略建议 |
| WHI-338 | `m1-research/prividium/WHI-338-prividium-architecture-deep-analysis.md` | Validium 模型、ZK 证明系统、RBAC 准入控制、选择性披露 |
| WHI-340 | `m1-research/tempo-zones/WHI-340-tempo-code-analysis.md` | ECIES 加密存款、Chaum-Pedersen 证明、认证 RPC、Zone 架构 |
| WHI-345 | `m2-comparison/consensus-da/WHI-345-consensus-da-comparison.md` | DA 模式对比、终局性光谱、混合 DA 方案 |
| WHI-350 | `m3-design/gap-analysis/WHI-350-gap-analysis.md` | Gap 矩阵、改造方案推荐、分阶段路径、风险评估 |

---

*本文档基于 2026 年 5 月 7 日完成的 M1/M2 研究成果和 M3 Gap 分析编制。所有设计决策、代码改动点和风险评估均可追溯至具体来源文件。*
