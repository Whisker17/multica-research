# WHI-335: Canton 架构与隐私模型深度分析

> **Issue**: WHI-335 — Canton 架构与隐私模型深度分析
> **Milestone**: M1: 各项目独立深度调研
> **Date**: 2026-05-06（修订: 2026-05-07）
> **Status**: Done (Rev.2 reviewed)
> **Prerequisite**: WHI-334 — Canton 官方文档与白皮书调研

> **术语说明**：Canton 3.x 已将 "Domain" 重命名为 "Synchronizer"。下文统一使用 **Synchronizer**；仅在引用旧版文档或对比历史概念时使用 "Domain"。参见 [Canton 3.4 文档](https://docs.digitalasset.com/overview/3.4/explanations/canton/topology.html)。

---

## 1. 架构拓扑分析

### 1.1 Participant-Synchronizer 分离架构 vs 传统区块链

Canton 的架构从根本上不同于传统区块链的全节点复制模型。要理解这一差异，需要从两种模型的核心假设出发。

**传统区块链（以 Ethereum 为代表）的核心假设**：
- 所有节点维护**完全相同的全局状态副本**
- 安全性来源于冗余——越多节点持有相同数据，篡改越困难
- 共识的目标是让所有节点就状态转换达成一致
- 代价：每笔交易对所有节点可见，隐私为零；扩展性受限于最慢的全节点

**Canton 的核心假设**：
- **不存在全局共享状态**——只存在"虚拟全局账本"（Virtual Global Ledger）
- 每个 Participant 只存储和看到自己参与的合约子集（projection）
- 安全性来源于密码学和协议设计，而非数据冗余
- 共识的目标不是全局一致，而是**相关方就特定交易达成一致**

```
Traditional Blockchain (Ethereum):              Canton:

┌─────────────────────┐                  ┌─────────────────────────────────┐
│    Global State     │                  │     Virtual Global Ledger       │
│  ┌───────────────┐  │                  │  (logical union, nowhere stored)│
│  │ All Contracts │  │                  └──────────┬──────────────────────┘
│  │ All Balances  │  │                             │
│  │ All History   │  │                   ┌─────────┼─────────┐
│  └───────────────┘  │                   │         │         │
└─────────┬───────────┘                   ▼         ▼         ▼
          │                          ┌────────┐ ┌───────┐ ┌───────┐
    ┌─────┼─────┐                    │  P1    │ │  P2   │ │  P3   │
    │     │     │                    │{A,B,C} │ │{B,D}  │ │{C,E}  │
    ▼     ▼     ▼                    │contracts│ │subset │ │subset │
 ┌────┐┌────┐┌────┐                 └────────┘ └───────┘ └───────┘
 │Node││Node││Node│                  Only sees    Only sees  Only sees
 │ =  ││ =  ││ =  │                  own slice    own slice  own slice
 │Full││Full││Full│
 │Copy││Copy││Copy│
 └────┘└────┘└────┘

Every node: identical           Each Participant: unique projection
```

**本质区别总结**：

| 维度 | 传统区块链 | Canton |
|------|-----------|--------|
| **状态分布** | 全节点完整复制 | 分片式投影（每方只有子集） |
| **一致性模型** | 强全局一致性 | 因果一致性（每个 Synchronizer 内部因果有序） |
| **隐私基线** | 默认全透明 | 默认不可见（need-to-know） |
| **扩展方式** | 垂直（更大节点）或分片 | 水平（增加 Synchronizer） |
| **数据主权** | 无（数据在所有节点上） | 有（数据只在相关 Participant 上） |
| **GDPR 合规** | 几乎不可能（不可变全局副本） | 原生支持（可删除本地数据） |

**关键洞察**：Canton 不是一个"更私密的区块链"——它是一个根本不同的架构范式。传统区块链通过共享一切来建立信任；Canton 通过只共享必要信息来建立信任。这使得 Canton 在概念上更接近**分布式数据库的联邦协调协议**，而非区块链的复制状态机。参见 [Canton 账本隐私模型](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/ledger-privacy.html)。

### 1.2 Sequencer-Mediator 角色分离的设计意图

Canton 将传统区块链中"共识"这一单一概念分解为两个独立的关注点：**消息排序**（Sequencer）和**交易确认**（Mediator）。这一分离不是偶然的——它直接服务于 Canton 的隐私和安全目标。

```
┌──────────────────────────────────────────────────────────────┐
│                     Synchronizer                              │
│                                                              │
│  ┌─────────────────────────┐  ┌───────────────────────────┐  │
│  │       Sequencer         │  │        Mediator            │  │
│  │                         │  │                            │  │
│  │  Knows:                 │  │  Knows:                    │  │
│  │  - Encrypted blobs      │  │  - Which Participants      │  │
│  │  - Recipient lists      │  │    need to confirm          │  │
│  │  - Timestamps           │  │  - Confirm/Reject signals  │  │
│  │  - Message sizes        │  │  - Decision deadline       │  │
│  │                         │  │                            │  │
│  │  Does NOT know:         │  │  Does NOT know:            │  │
│  │  - Transaction content  │  │  - Transaction content     │  │
│  │  - Contract state       │  │  - Contract state          │  │
│  │  - Business logic       │  │  - Business logic          │  │
│  │  - Who sent the message │  │  - Why Participants        │  │
│  │    (to recipients)      │  │    confirmed/rejected      │  │
│  └─────────────────────────┘  └───────────────────────────┘  │
│                                                              │
│  Separation guarantees:                                      │
│  1. No single component sees full transaction                │
│  2. Sequencer compromise ≠ content leak                      │
│  3. Mediator compromise ≠ message ordering manipulation      │
│  4. Each can be independently scaled/decentralized           │
└──────────────────────────────────────────────────────────────┘
```

**为什么分离 Sequencer 和 Mediator？**

1. **最小化信息暴露面（Least Privilege）**：Sequencer 处理排序但看不到内容；Mediator 处理确认但不控制排序。没有任何单一组件拥有完整的交易视图。在传统区块链中，排序器（如 L2 Sequencer）通常同时负责排序和执行——这意味着排序器可以看到所有交易内容，具备 MEV 提取能力。Canton 的分离设计从架构上消除了这种可能性。

2. **独立安全域**：即使 Sequencer 被攻破，攻击者只能影响消息排序（活性攻击），无法读取交易内容或伪造确认。即使 Mediator 被攻破，攻击者只能影响交易的确认/拒绝决策，无法篡改消息传递顺序。

3. **独立扩展和去中心化**：Sequencer 可以使用不同的 BFT 后端（Canton 原生、Ethereum、Fabric），而 Mediator 可以独立部署多个实例并设置阈值投票。两者的去中心化程度可以根据需求独立调整。

4. **可插拔性**：Sequencer 的排序层后端可替换（Canton BFT / Ethereum / Fabric / 数据库），而 Mediator 的 2PC 协调逻辑保持不变。这允许不同 Synchronizer 根据自身监管要求和性能需求选择最合适的排序后端。

**与传统单一共识的对比**：

| 单一共识（PBFT/Tendermint） | Canton Sequencer + Mediator |
|---------------------------|----------------------------|
| 所有验证者看到全部交易 | Sequencer 只看到加密 blob |
| 排序 + 执行 + 确认耦合 | 排序、确认、执行分离 |
| 共识算法变更影响全系统 | Sequencer 后端可独立替换 |
| 固定拜占庭阈值 | 各组件独立配置阈值 |
| 排序器 = MEV 风险 | 排序器看不到交易内容 |

**各角色被攻破时的影响分析（Compromise Impact Matrix）**：

| 角色 | 可见数据 | 被攻破时可做到 | 被攻破时不能做到 | 检测/缓解机制 |
|------|---------|---------------|-----------------|-------------|
| **Sequencer** | 加密 blob、收件人列表、消息大小、时间戳 | 延迟/审查消息（活性攻击）；关联元数据推断通信模式；重排消息顺序（单节点场景） | 读取交易内容；伪造确认/拒绝信号；修改加密 payload | BFT 多节点部署（2/3 阈值）；Write Amplification（向多个 Sequencer 提交同一消息绕过审查）；Participant 可检测消息丢失/延迟 |
| **Mediator** | 需要确认的 Participant 列表、确认/拒绝信号、决策截止时间 | 拒绝有效交易（发出错误 REJECT verdict）；延迟裁决至超时；对特定交易实施选择性拒绝 | 批准无效交易（需所有 Confirmer 同意）；读取交易内容；操纵消息排序 | 去中心化 Mediator 组（阈值投票，至少 threshold 个 Mediator 达成相同裁决）；超时 verdict 机制（`participant-response-timeout`）；审计日志可追溯拒绝决策 |
| **Topology Manager** | 拓扑交易内容（Party-Participant 映射、权限变更、Package vetting 声明） | 错误授予/撤销 Party 托管权限；修改 Package vetting 列表允许恶意代码执行；变更 Synchronizer 参数 | 绕过密码学签名链验证（需持有正确的命名空间密钥）；影响已提交的交易（拓扑变更不追溯生效） | 严格的命名空间委托链（根密钥 → 中间密钥 → 操作密钥）；拓扑变更延迟 ε（给运维人员检测窗口）；序列号严格递增防重放；多方联合命名空间需多签 |
| **Participant** | 该 Participant 托管的 Party 的所有合约和交易子树 | 泄露可见数据给外部（数据泄露）；恶意确认无效交易（如确认已消耗的合约，导致双花）；代表 Party 提交未授权交易 | 看到非托管 Party 的数据（need-to-know 限制）；影响其他 Synchronizer 上的交易；伪造密码学签名 | ACS Commitment 交换（定期检测 Participant 间 Active Contract Set 的不一致）；去中心化 Party 托管（同一 Party 可由多个 Participant 托管，需阈值确认）；Daml 授权模型在其他 Participant 处独立验证 |

> **参考来源**：[Canton Decentralization](https://docs.digitalasset.com/overview/3.4/explanations/canton/decentralization.html)——"threshold-many colluding Participant Nodes hosting a party can confirm inactive contracts, enabling double-spending" 和 "the Participant Node only processes events as long as threshold number of Sequencers have provided the same data"。

### 1.3 Participant 状态管理与一致性保证

每个 Participant 只存储自己参与的合约——那么在没有全局状态的情况下，Canton 如何保证一致性？

**一致性保证机制**：

1. **合约一致性（Contract Consistency）**：通过前序遍历建立 action 之间的"先于"关系（before-after ordering），形成有序森林。合约必须先创建才能行使或获取，消耗后不能再次使用。这直接防止了双花——同一合约不能被行使两次。

2. **密钥一致性（Key Consistency）**：每个 key 维护状态（assigned / free / unknown），通过 action 触发状态转换。系统禁止在 key 已分配时创建新合约，或在 key 状态不匹配时行使/获取合约。

3. **确定性执行（Deterministic Execution）**：Daml 的执行是确定性的——相同输入必然产生相同输出。这意味着每个 Participant 可以独立验证自己可见的交易子树，如果验证结果与提交者的声明不一致，就发送拒绝信号。

4. **2PC 协调**：Mediator 的两阶段提交确保只有当**所有**相关确认方都同意时，交易才会被提交。如果任何一方发现不一致（例如双花尝试），它可以拒绝交易。

5. **ACS 承诺（ACS Commitments）**：Participant 之间定期交换 ACS 承诺（cryptographic commitments），用于检测不一致。这是一种事后检测机制——如果一个 Participant 的 ACS 与其他相关 Participant 的预期不一致，系统可以检测到。

**关键洞察**：Canton 的一致性不是"所有人看到相同数据"（强一致性），而是"所有人对自己可见部分的解释是一致的"（因果一致性 + 验证一致性）。这类似于分布式数据库中的**因果一致性**模型，但增加了密码学验证层。参见 [Canton 账本完整性模型](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/ledger-integrity.html) 和 [Canton 账本结构](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/ledger-structure.html)。

### 1.4 多 Synchronizer 跨域事务协调

当一笔交易涉及分布在不同 Synchronizer 上的合约时，Canton 通过**重新分配（Reassignment）**机制协调。参见 [Canton 多 Synchronizer 操作](https://docs.digitalasset.com/overview/3.4/explanations/canton/multi-synchronizer.html)。

```
┌────────────────┐                    ┌────────────────┐
│ Synchronizer A │                    │ Synchronizer B │
│                │                    │                │
│  Contract X    │  1. Unassign X     │                │
│  (active)      │ ──────────────►    │                │
│                │                    │                │
│  Contract X    │  2. Assign X       │  Contract X    │
│  (inactive)    │ ──────────────►    │  (active)      │
│                │                    │                │
│                │                    │  3. Execute    │
│                │                    │  transaction   │
│                │                    │  using X + Y   │
│                │                    │  Contract Y    │
│                │                    │  (already here)│
└────────────────┘                    └────────────────┘

Note: Steps 1-2 are NON-ATOMIC. Contract X is temporarily
unavailable between Unassign and Assign.
```

**重新分配协议的详细流程**：

1. **Synchronizer 选择**：路由器评估所有候选 Synchronizer，按优先级（最高优先级 > 最少重新分配次数 > 最低 Synchronizer ID）选择目标
2. **Unassignment（源 Synchronizer）**：
   - 利益相关方提交 Unassignment 命令
   - 生成唯一的 Unassign ID 和递增的 Reassignment Counter
   - 设置 Assignment Exclusivity 窗口（限制谁可以发起 Assignment）
   - 合约在源 Synchronizer 上变为非活跃
3. **Assignment（目标 Synchronizer）**：
   - 利益相关方提交 Assignment 命令到目标 Synchronizer
   - 验证 Participant 在目标 Synchronizer 上有足够的权限和签名方代表
   - 合约在目标 Synchronizer 上激活
4. **交易执行**：所有输入合约就位后，在目标 Synchronizer 上执行交易
5. **可选输出路由**：将输出合约重新分配到期望的 Synchronizer

**关键限制与设计取舍**：

- **非原子性**：Reassignment 是非原子的。如果 Assignment 步骤永远不完成，合约将永远处于非活跃状态（"stuck in limbo"）。这是有意为之——要实现跨 Synchronizer 原子性需要全局锁定，这会严重损害性能和可用性。

- **无跨 Synchronizer 全局排序**：不同 Synchronizer 的事件可以以任意顺序出现在 Participant 的更新流中。一个合约的 `Created` 事件不一定先于 `Assigned` 事件出现，`Archived` 也不一定最后出现。只有在**单个 Synchronizer 内**，因果顺序才得到保证。

- **争用考虑**：Reassignment 本质上类似于"锁"——合约在转移期间不可用。应用设计需要显式考虑 Reassignment 的争用影响。

- **Global Synchronizer 的角色**：作为所有 Party 都信任的公共 Synchronizer，Global Synchronizer 提供了一个"最后手段"的协调点——当 Party 之间缺乏共同的私有 Synchronizer 时，可以退而使用 Global Synchronizer。

### 1.5 Topology Management 与信任边界

Canton 的拓扑管理（Topology Management）是理解其信任模型的关键维度——它决定了**谁可以参与网络、谁可以提交/确认交易、哪些 Daml 代码可以执行**。与传统区块链中由共识层统一管理的治理模型不同，Canton 采用分布式拓扑状态机（Distributed Topology State Machine），通过密码学签名和确定性处理保证所有节点对拓扑状态达成一致。参见 [Canton Topology 文档](https://docs.digitalasset.com/overview/3.4/explanations/canton/topology.html)。

#### 1.5.1 命名空间与密钥层级

Canton 的身份体系构建在**命名空间（Namespace）**之上。每个命名空间由一个自签名的根密钥证书定义：

```
Namespace Root of Trust:

  NSD(namespace=ROOT_KEY, target=ROOT_KEY, signedBy=ROOT_KEY)
       ↑ 自签名 = 信任锚点

  ROOT_KEY
    ├── Intermediate Key A  (CanSignAllMappings)
    │   ├── 可签署该命名空间下所有拓扑映射
    │   └── 可进一步委托子密钥
    │
    ├── Intermediate Key B  (CanSignAllButNamespaceDelegations)
    │   ├── 可签署除命名空间委托外的所有映射
    │   └── 适合日常运维（根密钥可离线冷存储）
    │
    └── Intermediate Key C  (CanSignSpecificMappings)
        └── 仅可签署明确列出的映射类型（最小权限）
```

**三级委托限制**使得组织可以将根密钥离线保管（冷存储），同时用受限的中间密钥处理日常拓扑操作，显著降低了根密钥泄露风险。

**唯一标识符（UID）**由标识符字符串 + 命名空间组成（如 `jane_doe::abc123`），命名空间持有者控制其下所有 UID 的创建。`DecentralizedNamespaceDefinition` 还支持多方联合持有命名空间，实现跨组织共治。

#### 1.5.2 Party Hosting 权限分级

Participant Node 对 Party 的托管（hosting）采用**三级权限模型**，每级权限包含其下所有级别：

| 权限级别 | 能力 | 信任要求 |
|---------|------|---------|
| **Observation** | 接收该 Party 作为 stakeholder 的交易通知 | 最低——Participant 仅被动接收数据 |
| **Confirmation** | 参与 2PC 确认协议，为 Party 投票确认/拒绝交易 | **高**——因为验证者无法识别提交节点身份，恶意确认者可以确认无效交易（如确认已消耗的合约） |
| **Submission** | 代表 Party 提交新交易到 Synchronizer | 最高——具备完整的代理能力 |

**关键安全要求**：Party 和 Participant 双方必须通过各自签名的拓扑交易（topology transaction）互相授权托管关系。单方面声明无效。

#### 1.5.3 Package Vetting（代码执行准入）

Participant Node 所有者通过 `VettedPackages` 拓扑映射声明可接受执行的 Daml 代码包。这一机制直接影响交易的可提交性——如果一笔交易涉及的 Daml package 未被某个需要确认的 Participant 审核通过（vetting），该 Participant 将拒绝确认，导致交易失败。

设计考量：Daml 代码可以执行任意长时间并消耗大量内存，package vetting 是防止恶意或低质量代码消耗节点资源的关键防线。支持时间窗口限制（开放式或有限期间）和版本指定。

#### 1.5.4 拓扑交易的安全保证

拓扑交易本身通过以下机制保证完整性和防重放：

1. **密码学签名覆盖全部关键字段**：签名覆盖映射内容（mapping）、序列号（serial）和变更操作（operation），篡改任何属性都会使签名失效。
2. **严格的序列号递增**：每个唯一键的 serial 必须精确递增 1，防止重放攻击（"恶意行为者不能简单地将先前已完全授权的交易重新提交"）。
3. **提案合并机制**：权限不足的拓扑交易作为提案（proposal）存储，累积签名直到达到授权阈值。第一个达到完全授权的提案自动使同一键同一序列的其他竞争提案失效。
4. **广播要求**：拓扑交易必须发送给 `AllMembersOfSynchronizer`。接受非广播拓扑交易可能导致账本分叉（ledger fork）。
5. **拓扑变更延迟（TopologyChange Delay ε）**：拓扑交易的生效时间 = 排序时间 + ε，给其他消息留出不被拓扑变更阻塞的处理窗口。

#### 1.5.5 拓扑管理对交易可提交性的影响

拓扑管理直接决定了一笔交易是否能被成功路由和确认：

```
交易提交前的拓扑检查链:

  [交易 TX] ──► 1. 提交者 Party 是否有 Submission 权限的 Participant？
                     │ NO → 交易无法提交
                     ▼ YES
               2. 所有 Signatory Parties 的 Participant 是否在目标 Synchronizer 上
                  有 Confirmation 权限？
                     │ NO → 交易无法在此 Synchronizer 确认
                     ▼ YES
               3. 交易涉及的 Daml packages 是否被所有 Confirming Participants
                  的 VettedPackages 列表包含？
                     │ NO → Participant 拒绝确认
                     ▼ YES
               4. 签名方密钥链是否从签名密钥到根命名空间密钥完整无断裂？
                     │ NO → 签名验证失败
                     ▼ YES
               5. 交易可以被路由和确认
```

**关键洞察**：Canton 的拓扑管理不是"配置层"——它是信任模型的核心组成部分。拓扑交易的错误（如错误授予 Confirmation 权限给不受信任的 Participant）直接削弱安全保证，其危害不亚于密码学攻击。这是企业部署中运维治理的关键风险点。

---

## 2. 隐私模型深度分析

### 2.1 Merkle DAG 子交易树

Canton 的隐私核心创新在于将交易分解为**子交易树（sub-transaction tree）**，然后为每个参与方计算一个**投影（projection）**——只包含该方有权看到的部分。

#### 2.1.1 交易的树状结构

一笔 Canton 交易不是扁平的操作列表，而是一棵**有向无环图（DAG）**：

```
Transaction TX:
│
├── Action A1: Alice exercises Transfer on IOU-1
│   ├── Sub-action A1.1: Archive IOU-1 (old owner: Alice)
│   └── Sub-action A1.2: Create IOU-2 (new owner: Bob)
│
├── Action A2: Bob exercises Deliver on Share-1
│   ├── Sub-action A2.1: Archive Share-1 (old holder: Bob)
│   └── Sub-action A2.2: Create Share-2 (new holder: Alice)
│
└── Action A3: Bank records settlement
    └── Sub-action A3.1: Create SettlementRecord
```

每个 action 可以有后果（consequences），后果本身构成子交易，这种递归结构使得交易天然可分割。

#### 2.1.2 投影算法

对于参与方集合 P，投影规则如下：

```
projection(P, action) =
  if P ∩ informees(action) ≠ ∅:
    retain action with all consequences  → P sees full subtree
  else if action has consequences:
    replace action with projection(P, consequences)  → skip to children
  else:
    drop action entirely  → P sees nothing here
```

**关键性质**：
- 投影是**吸收的（absorbing）**：对子集的投影包含在对超集投影的信息中
- 投影后的账本是 **DAG 而非线性链**——因为 requester 信息必须被移除（否则会泄露 witness 身份）
- 投影保留了因果关系，但可能丢失全局排序信息

#### 2.1.3 实际运作示例

考虑一个 DvP（Delivery vs Payment）交易：

```
TX: Alice buys 100 shares from Bob, paying via Bank IOU

Full transaction tree:
├── Exercise: Alice→Transfer IOU (signatories: Bank, observers: Alice)
│   ├── Archive: IOU(Alice, Bank, $100k)
│   └── Create: IOU(Bob, Bank, $100k)
└── Exercise: Bob→Deliver Shares (signatories: Registrar, observers: Bob)
    ├── Archive: Share(Bob, Registrar, 100 units)
    └── Create: Share(Alice, Registrar, 100 units)

Alice's projection (sees IOU transfer + share receipt):
├── Exercise: Transfer IOU
│   ├── Archive: IOU(Alice, Bank, $100k)
│   └── Create: IOU(Bob, Bank, $100k)     ← Alice sees Bob gets paid
└── Create: Share(Alice, Registrar, 100)   ← Alice sees she got shares

Bob's projection (sees share delivery + payment receipt):
├── Create: IOU(Bob, Bank, $100k)          ← Bob sees he got paid
└── Exercise: Deliver Shares
    ├── Archive: Share(Bob, Registrar, 100)
    └── Create: Share(Alice, Registrar, 100)

Bank's projection (sees only IOU movement):
└── Exercise: Transfer IOU
    ├── Archive: IOU(Alice, Bank, $100k)
    └── Create: IOU(Bob, Bank, $100k)

Registrar's projection (sees only share movement):
└── Exercise: Deliver Shares
    ├── Archive: Share(Bob, Registrar, 100)
    └── Create: Share(Alice, Registrar, 100)

Sequencer sees: [encrypted_blob_1, encrypted_blob_2, ...]
Mediator sees: {P1: ?, P2: ?, P3: ?, P4: ?} → all confirmed → APPROVE
```

#### 2.1.4 Merkle DAG 的加密实现

交易树通过 Merkle DAG 编码：

1. 每个子交易节点被编码为 DAG 中的一个节点
2. 节点包含：加密的 action 数据 + 子节点的哈希引用
3. 发送给 Participant 的消息只包含其可见的子树节点
4. 被隐藏的节点用其 Merkle 哈希替代——接收者可以验证隐藏部分的存在和完整性，但无法读取内容
5. 整个树的根哈希作为 commitment 发送给 Sequencer

### 2.2 加密承诺方案

**Sequencer 看到什么？**

```
┌─────────────────────────────────────────────────────────┐
│                What Sequencer Receives                   │
│                                                          │
│  Message = {                                             │
│    recipients: [P1, P2, P3],       ← plaintext           │
│    timestamp: 2026-05-06T10:00:00, ← assigned by Seq     │
│    payload: 0xAE3F...B2C1,        ← encrypted opaque    │
│    commitment: SHA256(payload),    ← integrity check      │
│    size: 4096 bytes               ← for traffic mgmt     │
│  }                                                       │
│                                                          │
│  What Sequencer CAN infer:                               │
│  - Number of recipients (metadata)                       │
│  - Message sizes (payload bytes)                         │
│  - Timing patterns (when messages are sent)              │
│  - Communication graph (who talks to whom, roughly)      │
│                                                          │
│  What Sequencer CANNOT infer:                            │
│  - Transaction content (encrypted)                       │
│  - Contract types or values                              │
│  - Business logic or decisions                           │
│  - Sender identity (hidden from recipients too)          │
│  - Whether transaction was approved or rejected          │
└─────────────────────────────────────────────────────────┘
```

**防止 Sequencer 推断交易内容的机制**：

1. **端到端加密**：交易内容使用接收方的公钥加密，Sequencer 只转发密文
2. **发送者匿名**：接收者无法从消息中得知发送者身份
3. **不透明转发**：Sequencer 的角色类似于加密邮件服务器——路由消息但无法阅读
4. **流量混淆**：虽然 Sequencer 可以观察到通信模式（元数据），但无法将其与具体业务行为关联

**已知的元数据泄露和缓解**：

Canton 的文档承认 Sequencer 仍然可以从元数据（消息大小、频率、接收者列表）推断某些信息。这是"need-to-know"模型的固有限制——完全消除元数据泄露需要混淆网络（如 Tor），这会显著增加延迟。Canton 在此做出了务实的权衡：metadata leak 被认为在企业场景中是可接受的风险，因为 Synchronizer 通常由受信任的联盟运营。参见 [ZKP vs Canton 隐私对比](https://www.canton.network/blog/zero-knowledge-proofs-whe-privacy-needs-more)。

### 2.3 Divulgence 控制机制

Divulgence 是 Canton 隐私模型中最微妙的部分——它处理的是**非利益相关方在什么条件下可以看到合约信息**的问题。

#### 2.3.1 两种 Divulgence

**立即 Divulgence（Immediate Divulgence）**：

当一个 Party 是某个 action 的 witness 但不是 informee 时，它可以看到该 action 后果中创建的合约。

- **为什么允许？** Daml 是确定性的——如果一个 Party 知道 action 的输入，它可以自己计算出所有后果。既然结果是可推导的，隐藏它没有意义（反而增加了不必要的复杂性）。
- **影响范围**：只能看到合约创建，不能看到后续的行使或归档。

**追溯 Divulgence（Retroactive Divulgence）**：

当一个 action 的输入合约出现在非 informee witness 的投影中时，该 witness 需要看到输入合约才能验证交易。

- **为什么需要？** 验证一笔交易需要知道输入合约的内容——否则无法检查交易是否符合合约规则。如果 Alice 需要验证 Bob 交付的资产是否合规，她需要看到 Bob 的资产合约。
- **安全含义**：这意味着参与多方交易可能会"拉入"之前不可见的合约信息。这是信息流的必要代价。

#### 2.3.2 Divulgence vs Disclosure 的关键区分

```
Divulgence (被动)                     Disclosure (主动)
─────────────────                     ─────────────────
- 自动发生，作为交易执行的副作用       - 需要显式调用 submitWithDisclosures
- 只能看到合约创建                    - 授予临时使用权
- 不授予后续使用权                    - 发送者主动选择分享
- 无法看到后续归档/修改               - 接收者可以在后续交易中使用

设计原因：
如果 divulgence 自动授予使用权，会导致"脆弱工作流"——
一个非利益相关方可以看到合约被创建，但看不到它何时被归档。
如果它认为合约仍然有效并尝试使用，但合约实际已被归档，
系统行为就变得不可预测。

显式 Disclosure 解决了这个问题：
- 发送者知道合约的当前状态
- 接收者通过正式渠道获得使用权
- 双边通信，不会导致观察者列表的二次方膨胀
```

### 2.4 Canton "Need-to-Know" vs ZK "Prove-Not-Reveal" 的根本对比

这是理解 Canton 隐私哲学最关键的对比。两种模型解决的是同一个问题（交易隐私），但采用了根本不同的方法论。

```
┌─────────────────────────────────────┬───────────────────────────────────┐
│        Canton: Need-to-Know          │      ZK: Prove-Not-Reveal        │
├─────────────────────────────────────┼───────────────────────────────────┤
│                                     │                                   │
│  Philosophy:                        │  Philosophy:                      │
│  "Show data only to those who       │  "Prove computation correctness   │
│   have a right to see it"           │   without revealing input data"   │
│                                     │                                   │
│  Mechanism:                         │  Mechanism:                       │
│  Data is selectively distributed    │  Data is hidden; only proofs      │
│  (encrypted routing + projections)  │  are published on-chain           │
│                                     │                                   │
│  Auditability:                      │  Auditability:                    │
│  Full audit trail available to      │  Audit is mathematically limited  │
│  authorized parties. If system is   │  — "when ZKPs fail, they fail     │
│  compromised, evidence exists.      │  invisibly. You don't get a       │
│                                     │  second chance."                  │
│  Recovery:                          │                                   │
│  System compromise is detectable    │  Recovery:                        │
│  and recoverable — audit trail      │  A single undetected exploit can  │
│  proves what happened.              │  "permanently taint the ledger"   │
│                                     │  with no way to verify integrity. │
│  Trust model:                       │                                   │
│  Trust Participant operators and    │  Trust model:                     │
│  the cryptographic protocol.        │  Trust the math (circuit design,  │
│  Synchronizer operators cannot      │  trusted setup, implementation).  │
│  see content.                       │  No operator trust needed.        │
│                                     │                                   │
│  Information revelation:            │  Information revelation:          │
│  Authorized parties see actual      │  Nobody sees actual data;         │
│  data — can perform rich analysis,  │  only boolean validity signals.   │
│  compliance checks, dispute         │  Limited to what proof circuit    │
│  resolution with real evidence.     │  was designed to prove.           │
│                                     │                                   │
│  Enterprise fit:                    │  Enterprise fit:                  │
│  Strong: regulators can audit,      │  Challenging: regulators cannot   │
│  disputes have evidence trail,      │  audit actual transactions,       │
│  GDPR right-to-deletion possible.   │  "cannot confidently tell users   │
│                                     │  or regulators whether their      │
│                                     │  systems have been compromised."  │
└─────────────────────────────────────┴───────────────────────────────────┘
```

**深层技术差异**：

| 维度 | Canton Need-to-Know | ZK Prove-Not-Reveal |
|------|--------------------|--------------------|
| **隐私粒度** | 子交易级（Merkle DAG 投影） | 交易级（整笔交易被隐藏/证明） |
| **计算开销** | 低（加密路由 + 2PC 协调） | 高（ZK 证明生成，尤其是通用 ZKP） |
| **灵活性** | 可以选择性地向不同方展示不同子集 | 证明电路固定，改变可见性需要重新设计电路 |
| **合规能力** | 监管者可以被添加为 Observer，直接审查数据 | 监管者只能验证证明，无法检查底层数据 |
| **故障模式** | 透明——攻击/错误会留下审计痕迹 | 不透明——攻击可能永远无法检测 |
| **状态模型** | 分布式状态投影 | 全局状态 + 零知识证明层 |
| **成熟度** | 生产级（$2T+/月处理量） | 通用 ZK 智能合约隐私仍在发展阶段 |

**作者解读**：Canton 和 ZK 不是"哪个更好"的问题，而是服务于不同信任假设的不同工具。Canton 的 need-to-know 模型适合**信任关系明确的企业联盟**——参与方知道彼此身份，监管要求可审计性。ZK 更适合**无信任的公开环境**——参与方可能是匿名的，隐私是绝对的。在现实的金融机构场景中，Canton 的"可审计的隐私"比 ZK 的"不可审计的绝对隐私"更符合监管要求。

---

## 3. 共识与终局性分析

### 3.1 Canton 提交协议详细流程

Canton 的交易提交采用**两阶段提交（2PC）**协议，由 Mediator 协调。以下是完整的端到端流程：

```
Timeline ────────────────────────────────────────────────────►

Phase 1: PREPARE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Submitter        Sequencer         Participant(s)      Mediator
     │                │                    │                │
     │ 1. Submit TX   │                    │                │
     │ (encrypted)    │                    │                │
     │───────────────►│                    │                │
     │                │                    │                │
     │                │ 2. Assign batch    │                │
     │                │    timestamp       │                │
     │                │ 3. Route encrypted │                │
     │                │    sub-trees to    │                │
     │                │    relevant        │                │
     │                │    participants    │                │
     │                │───────────────────►│                │
     │                │                    │                │
     │                │                    │ 4. Decrypt own │
     │                │                    │    sub-tree    │
     │                │                    │ 5. Validate:   │
     │                │                    │    - Auth OK?  │
     │                │                    │    - No double │
     │                │                    │      spend?    │
     │                │                    │    - Contract  │
     │                │                    │      active?   │
     │                │                    │    - Model     │
     │                │                    │      conforms? │
     │                │                    │                │

Phase 2: CONFIRM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     │                │                    │                │
     │                │                    │ 6. Send        │
     │                │                    │    confirm or  │
     │                │                    │    reject      │
     │                │                    │───────────────►│
     │                │                    │                │
     │                │                    │                │ 7. Collect
     │                │                    │                │    responses
     │                │                    │                │    until
     │                │                    │                │    deadline
     │                │                    │                │
     │                │                    │                │ 8. Issue
     │                │                    │                │    VERDICT:
     │                │                    │                │    APPROVE
     │                │                    │                │    or REJECT

Phase 3: FINALIZE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     │                │                    │                │
     │                │  9. Broadcast      │                │
     │                │     verdict via    │◄───────────────│
     │                │     Sequencer      │                │
     │                │◄──────────────────►│                │
     │                │                    │                │
     │                │                    │ 10. Apply      │
     │                │                    │     verdict:   │
     │                │                    │     - APPROVE: │
     │                │                    │       update   │
     │                │                    │       ACS      │
     │                │                    │     - REJECT:  │
     │                │                    │       discard  │
     │                │                    │                │
```

**各步骤详解**：

1. **提交者构造交易**：Participant 代表 Party 构造交易，将其编码为 Merkle DAG，按收件人加密不同子树，提交给 Sequencer。
2. **Sequencer 分配时间戳**：Sequencer 为消息批次分配确定性时间戳，确保所有收件人以相同顺序接收消息。
3. **隐私路由**：Sequencer 将加密的子树分发给各自的目标 Participant——每个 Participant 只收到自己有权看到的部分。
4. **本地解密与验证**：每个 Participant 解密自己的子树，使用本地 Daml 引擎验证交易是否符合合约规则。
5. **验证检查项**：授权检查（signatories 是否正确？actors 是否有权？）、状态检查（输入合约是否在 ACS 中？是否已被消耗？）、模型符合性检查（action 是否符合 template 定义？）。
6. **发送确认/拒绝**：通过 Sequencer 将加密的确认或拒绝信号发送给 Mediator。
7. **Mediator 收集响应**：等待所有需要确认的 Participant 响应，或直到 decision deadline 到期。
8. **出具裁决**：所有确认方同意 → APPROVE；任何一方拒绝或超时 → REJECT。
9. **广播裁决**：通过 Sequencer 将裁决分发给所有相关 Participant。
10. **应用裁决**：APPROVE → 更新本地 ACS（归档输入合约、创建输出合约）；REJECT → 丢弃交易效果。

### 3.2 BFT Sequencer 实现与安全假设

**BFT 排序层**：

Canton 的 Sequencer 使用 BFT（拜占庭容错）排序协议对消息进行全局排序。关键安全假设：

| 假设 | 说明 |
|------|------|
| **BFT 阈值** | 2/3 多数诚实假设——最多 1/3 的 Sequencer 节点可以是拜占庭的 |
| **消息完整性** | 加密保证消息在传输中不被篡改 |
| **活性** | 只要 2/3+ 节点在线，系统可以继续排序消息 |
| **安全性** | 即使少数 Sequencer 被攻破，也无法创建分叉（conflicting orderings） |
| **隐私** | Sequencer 看不到消息内容——但可以观察元数据（大小、时间、收件人列表） |

**可插拔后端**：

Sequencer 的排序层支持多种后端，每种有不同的安全/性能特征：

| 后端 | 适用场景 | 安全性 | 性能 |
|------|---------|--------|------|
| **Canton 原生 BFT** | 生产环境 | Canton 自身的 BFT 协议 | 高吞吐、低延迟 |
| **Ethereum** | 需要 Ethereum 安全性继承 | Ethereum 共识安全性 | 受限于 Ethereum 出块时间 |
| **Hyperledger Fabric** | 已有 Fabric 基础设施的企业 | Fabric 共识安全性 | Fabric 吞吐量 |
| **数据库** | 开发/测试 | 单点故障 | 最高（无共识开销） |

**去中心化 Sequencer 的连接模型**：

Participant 可以同时订阅多个 Sequencer，配置阈值（threshold）：
- **写放大（Write Amplification）**：向多个 Sequencer 提交同一消息，防止单个 Sequencer 审查
- **读一致性**：需要阈值数量的 Sequencer 确认同一排序，才认为排序有效

### 3.3 Canton 共识 vs 传统 BFT 共识

Canton 的共识机制是**数据库 2PC 和区块链 BFT 共识的混合体**，但更接近 2PC。

```
                传统 BFT 共识                    Canton 协议
              (Tendermint/PBFT)          (Sequencer + Mediator 2PC)
             ─────────────────          ──────────────────────────

目的:         全局状态转换达成一致        相关方就特定交易达成一致

参与者:       所有验证者                  只有 informees 的 Participants

可见性:       所有验证者看到全部交易      每个 Participant 只看到自己的子树

协调者:       轮转 Leader                 固定 Mediator（可多个，阈值投票）

提议:         Leader 打包区块             提交者构造交易 Merkle DAG

投票:         所有验证者投票              只有 confirmers 确认/拒绝

终局性:       2/3 投票 → 即时终局         所有 confirmers 同意 → 终局
              (Tendermint)                或任一方拒绝 → 回滚

区块:         有（批量交易打包）          无（单笔交易独立提交）

全局排序:     是（区块高度 = 全局序列）   仅 Synchronizer 内排序

冲突解决:     在共识层处理               在 Participant 层检测，
              （mempool 去重）            Mediator 层裁决
```

**关键判断：Canton 更接近 2PC 而非区块链共识。** 理由：
1. **无区块概念**：没有批量打包，每笔交易独立提交和确认
2. **参与方限制**：只有利益相关方参与确认，而非所有验证者
3. **协调者角色**：Mediator 类似于 2PC 的 Coordinator，而非区块链的 Leader/Proposer
4. **回滚机制**：任何一方拒绝即回滚——这是典型的 2PC 语义，而非 BFT 的多数投票
5. **无概率性终局**：不存在确认数累积的概念，交易要么提交要么回滚

**但 Canton 又超越了传统 2PC**：
- Sequencer 层的 BFT 排序保证了消息的全局一致排序（传统 2PC 不需要这个）
- 加密和隐私路由是传统 2PC 没有的
- 支持去中心化 Mediator（阈值投票裁决），而不是单一 Coordinator

### 3.4 终局性保证

交易在以下条件下达到终局（finality）：

```
Finality conditions:
┌──────────────────────────────────────────────────────┐
│                                                      │
│  1. Sequencer has assigned a batch timestamp ✓       │
│  2. All confirming Participants have approved ✓      │
│  3. Mediator has issued APPROVE verdict ✓            │
│  4. Verdict has been distributed via Sequencer ✓     │
│  5. All relevant Participants have applied           │
│     the verdict to their ACS ✓                       │
│                                                      │
│  → Transaction is FINAL                              │
│                                                      │
│  Finality properties:                                │
│  - Deterministic: no probabilistic waiting period    │
│  - Immediate: once verdict is applied, it's done     │
│  - Irrevocable: no reorg, no challenge period        │
│  - Partial: only affects participating Participants  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**终局性 vs 其他系统**：

| 系统 | 终局性类型 | 时间 | 条件 |
|------|-----------|------|------|
| **Canton** | 确定性即时终局 | 交易确认后（秒级） | 所有 confirmers 同意 |
| **Ethereum L1** | 概率性 → 确定性 | ~12min（finalized epoch） | 2/3 验证者签名 |
| **Optimistic Rollup** | 乐观终局 + 挑战 | ~7天挑战窗口 | 无挑战成功 |
| **ZK Rollup** | 证明验证后终局 | 证明生成时间（分钟级） | 有效证明上链 |
| **Tendermint** | 确定性即时终局 | ~6秒 | 2/3 验证者投票 |

**Canton 终局性的特殊之处**：Canton 的终局性是**局部的**——交易只对参与的 Participant 有效。不存在"全网确认"的概念。这意味着终局性不需要等待全网共识，只需要相关方达成一致，因此天然更快。

### 3.5 故障与恢复路径矩阵

Canton 作为生产级系统，需要应对各种故障场景。以下矩阵系统化地梳理了各组件的故障模式、影响范围和恢复路径。

#### 3.5.1 Sequencer 故障场景

| 故障类型 | 影响 | 恢复路径 | 相关机制 |
|---------|------|---------|---------|
| **单节点宕机（非 BFT 部署）** | Synchronizer 完全不可用，所有交易停止排序 | 重启节点或切换到备用 Sequencer 后端；已提交但未排序的消息需要重新提交 | 数据库后端模式适用于开发/测试，生产环境应使用 BFT 部署 |
| **BFT 部署中少数节点宕机（≤1/3）** | 无影响——BFT 协议在 2/3+ 节点在线时保持活性 | 离线节点可异步追赶（catch-up）已排序消息 | BFT 排序层的标准容错保证 |
| **BFT 部署中多数节点宕机（>1/3）** | Synchronizer 丧失排序活性（liveness），无法排序新消息 | 需要恢复足够多的节点至 2/3+ 在线；已确认交易不受影响（安全性保持） | BFT 的安全性-活性分离：安全性在网络分区时仍保持，仅活性受损 |
| **审查攻击（Censorship）** | 特定 Participant 的消息被恶意丢弃/延迟 | Write Amplification——Participant 向多个 Sequencer 提交同一消息，只要有一个诚实 Sequencer 就能传递；去重机制确保不会重复执行 | [Canton Decentralization](https://docs.digitalasset.com/overview/3.4/explanations/canton/decentralization.html): Participant 可同时订阅多个 Sequencer，配置阈值 |
| **排序分叉（Byzantine Sequencer）** | 不同 Participant 看到不同的消息排序，可能导致 ACS 不一致 | BFT 阈值保证——只要 ≤1/3 节点是拜占庭的，无法创建分叉；Participant 通过 ACS Commitment 交换检测不一致 | threshold 配置要求多个 Sequencer 提供一致数据才被 Participant 接受 |

#### 3.5.2 Mediator 故障场景

| 故障类型 | 影响 | 恢复路径 | 相关机制 |
|---------|------|---------|---------|
| **Mediator 宕机** | 正在进行的交易无法获得裁决，新交易无法启动确认流程 | 去中心化 Mediator 组——只要 threshold 个 Mediator 在线就能继续出具裁决；单 Mediator 部署需等待重启 | Mediator 组的阈值投票机制 |
| **超时未裁决（Decision Deadline 过期）** | 交易因超时被自动 REJECT | Participant 可重新提交交易；超时 verdict 通过 Sequencer 广播给所有相关 Participant | `participant-response-timeout` 配置项；超时是确定性的（所有参与方观察到相同的超时事件） |
| **错误裁决（Byzantine Mediator）** | 单个恶意 Mediator 发出错误的 APPROVE 或 REJECT | 去中心化 Mediator 组中，需要 threshold 个 Mediator 达成相同裁决——单个恶意 Mediator 无法左右结果（前提：threshold > 1） | 与 BFT Sequencer 类似的阈值信任模型 |
| **选择性拒绝** | 恶意 Mediator 对特定交易总是发出 REJECT | 在去中心化 Mediator 组中，其他诚实 Mediator 的裁决可以覆盖；在单 Mediator 模式下是不可检测的审查 | 审计日志可追溯裁决历史；切换到去中心化 Mediator 组以消除单点审查能力 |

#### 3.5.3 Participant 故障场景

| 故障类型 | 影响 | 恢复路径 | 相关机制 |
|---------|------|---------|---------|
| **Participant 宕机** | 该 Participant 托管的 Party 无法提交新交易，也无法确认涉及其的交易 | 重启 Participant，从 Sequencer 重放未处理的消息以恢复状态；Sequencer 为每个 Participant 维护消息投递状态 | 消息持久化在 Sequencer 侧——Participant 重启后可从上次确认的时间戳继续消费 |
| **PostgreSQL 数据库损坏** | ACS（Active Contract Set）数据丢失，Participant 无法验证交易 | 从数据库备份恢复；或通过 Sequencer 重放历史消息重建 ACS（理论上可行，但取决于消息保留策略）；去中心化 Party 托管下，其他 Participant 持有相同 Party 的投影数据可用于交叉验证 | 定期 ACS Commitment 交换可帮助验证恢复后的数据一致性 |
| **确认超时（Participant 未在截止时间内响应）** | Mediator 将 Participant 的响应视为缺失；如果该 Participant 是必须确认方，交易因超时被 REJECT | 交易提交者可重新提交交易；Participant 需排查超时原因（网络延迟、处理能力不足、配置问题） | decision deadline 是确定性的，由 Sequencer 时间戳 + 配置参数决定 |
| **恶意确认（Byzantine Participant）** | 确认无效交易（如确认已消耗合约的交易），导致双花 | ACS Commitment 定期交换——其他持有同一 Party 投影的 Participant 会检测到不一致；去中心化 Party 托管下的 threshold 确认可防止单个恶意 Participant 的攻击 | 这是去中心化 Party 托管的核心动机——threshold-many 个 Participant 合谋才能双花 |

#### 3.5.4 跨 Synchronizer Reassignment 故障

| 故障类型 | 影响 | 恢复路径 | 相关机制 |
|---------|------|---------|---------|
| **Unassign 成功但 Assign 未完成** | 合约在源 Synchronizer 上已非活跃，但在目标 Synchronizer 上未激活——合约"卡在半空中"（stuck in limbo） | 在 Assignment Exclusivity 窗口内，只有原始发起者可以完成 Assign；窗口过期后，其他具有权限的 Party 也可以尝试 Assign；最坏情况下合约可能无限期不可用 | Assignment Exclusivity 窗口 + Reassignment Counter（每次重新分配递增，防止旧的 Assign 请求被重放） |
| **目标 Synchronizer 上权限不足** | Assign 步骤被拒绝——目标 Synchronizer 上 Participant 缺少必要的 Confirmation 权限或 signatory 代表 | 需要先在目标 Synchronizer 上建立正确的拓扑关系（Party-Participant 映射、权限授予），然后重新尝试 Assign | 交易提交前的拓扑预检查可以避免此类故障 |
| **跨 Synchronizer 因果序列断裂** | 不同 Synchronizer 的事件在 Participant 更新流中无全局排序——Created 事件不一定先于 Assigned 事件出现 | 应用层需要设计为容忍事件乱序；使用 Reassignment Counter 和 ContractId 重建逻辑因果关系 | 无跨 Synchronizer 全局时钟是有意设计——全局排序需要跨域锁定，会严重损害性能和可用性 |

**故障恢复的总体评估**：Canton 的故障处理设计遵循以下原则：(1) **安全性优先于活性**——宁可交易超时失败也不允许不一致状态；(2) **去中心化作为容错手段**——Sequencer/Mediator/Participant 都支持去中心化部署以消除单点故障；(3) **ACS Commitment 作为事后检测**——即使某些拜占庭行为在发生时不可阻止，定期一致性检查可以在事后发现异常。

> **注意**：Canton 官方协议文档（[protocol.html](https://docs.digitalasset.com/overview/3.4/explanations/canton/protocol.html)）自注为 "work in progress"，部分故障恢复的细节（如 Sequencer BFT view-change、Participant 状态重建的具体实现）可能需要在 WHI-336 的代码库分析中进一步验证。

---

## 4. Daml 授权模型分析

### 4.1 Signatories, Observers, Controllers 的语义

Daml 的授权模型围绕三个核心角色构建，每个角色有精确的权限边界：

```
┌──────────────────────────────────────────────────────────┐
│                   Daml Authorization Roles                 │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │ SIGNATORY (签署方)                                │    │
│  │                                                  │    │
│  │ - MUST authorize contract creation               │    │
│  │ - Notified when contract is archived             │    │
│  │ - Cannot have obligations imposed without consent│    │
│  │ - Rights cannot be unilaterally removed          │    │
│  │ - Determines contract identity and validity      │    │
│  │                                                  │    │
│  │ Analogy: co-signers on a legal contract          │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │ OBSERVER (观察方)                                 │    │
│  │                                                  │    │
│  │ - Can SEE the contract and related events        │    │
│  │ - Does NOT need to authorize creation            │    │
│  │ - Notified of create/consuming exercise          │    │
│  │ - NOT notified of non-consuming exercise/fetch   │    │
│  │ - Cannot exercise choices (unless also controller)│    │
│  │                                                  │    │
│  │ Analogy: a notified third party (e.g., regulator)│    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │ CONTROLLER (控制方)                               │    │
│  │                                                  │    │
│  │ - Can EXERCISE a specific choice on the contract │    │
│  │ - Becomes the ACTOR when exercising              │    │
│  │ - Authorization flows from controller designation│    │
│  │ - Can be: a specific party, signatory, observer  │    │
│  │                                                  │    │
│  │ Analogy: the person with authority to act        │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  Authorization Rules:                                    │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Create → requires ALL signatories               │    │
│  │ Exercise → requires ALL actors (controllers)     │    │
│  │ Fetch → requires ALL actors                      │    │
│  │ Archive → automatic when consuming exercise       │    │
│  │                                                  │    │
│  │ Transitive authorization:                        │    │
│  │ Exercise consequences are jointly authorized     │    │
│  │ by contract's signatories + exercise actor       │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

**授权模型的两个核心不变量**：

1. **义务需要同意（Obligation requires consent）**：一个 Party 不能在未授权的情况下被绑定为 Signatory。这通过 Propose-Accept 模式实现——提议方创建一个提案合约，被提议方通过行使 Accept choice 来授权创建最终合约。

2. **权利不能被单方面移除（Rights cannot be unilaterally removed）**：只有通过授权的 consuming exercise 才能归档合约。如果 Alice 持有一个 IOU，发行方 Bank 不能在 Alice 不参与的情况下归档该 IOU。

### 4.2 编译时与运行时的授权保证

Daml 的授权保证是**编译时约束 + 运行时强制执行**的双层模型。编译器检查结构性约束（类型安全、角色声明），而 Daml 执行引擎（Ledger Model）在运行时计算 required authorizers 并拒绝缺失授权的交易。两者缺一不可。

**编译时检查**——结构性约束：

```daml
-- 编译时检查的例子

template Loan
  with
    bank : Party
    borrower : Party
    amount : Decimal
  where
    signatory bank, borrower  -- 双方签署
    
    choice Repay : ()
      controller borrower    -- 只有借款人可以偿还
      do
        -- 编译器保证：
        -- 1. borrower 必须是有效的 Party 类型
        -- 2. amount 必须是 Decimal 类型
        -- 3. 这个 choice 只能在 Loan 合约上调用
        -- 4. 返回类型必须是 ()
        return ()
    
    -- 以下代码会在编译时失败：
    -- choice Steal : ()
    --   controller someRandomParty  -- ERROR: someRandomParty 未在 with 中声明
    --   do ...
```

**编译时保证清单**：

| 检查项 | 说明 |
|--------|------|
| **Signatory 完整性** | 所有 signatory 必须在 template 的 `with` 字段中声明 |
| **Controller 有效性** | Controller 必须是已声明的 Party |
| **类型安全** | 合约字段类型在编译时检查，运行时不可能类型错误 |
| **Choice 返回类型** | Choice 的返回类型必须与声明匹配 |
| **确定性保证** | Daml 不允许随机数、I/O、系统调用等非确定性操作 |
| **模式匹配完整性** | 编译器检查模式匹配是否覆盖所有可能情况 |

**运行时强制执行**——Daml 执行引擎的授权检查：

编译器无法穷举所有运行时授权场景（例如，signatories 可能依赖于合约参数的动态值）。因此 Daml 的 Ledger Model / 执行引擎在运行时对每个 action 计算 required authorizers 并严格检查：

| Action 类型 | 运行时 Required Authorizers | 缺少授权时的行为 |
|------------|---------------------------|----------------|
| **Create** | 合约的所有 signatories | 交易被执行引擎拒绝（abort），不会到达 Mediator |
| **Exercise** | choice 的所有 actors（controllers） | 交易 abort；如果是子交易的一部分，整个交易树失败 |
| **Fetch** | 所有 actors | 交易 abort |
| **LookupByKey（找到）** | 所有 actors | 交易 abort |
| **LookupByKey（未找到/NoSuchKey）** | key 的所有 maintainers | 交易 abort |

**传递授权（Transitive Authorization）**：当一个 exercise 产生子 action（consequences）时，子 action 的可用授权 = 父合约的 signatories ∪ exercise 的 actor。这意味着 exercise 的后果可以创建新合约，只要新合约的 signatories 是父合约 signatories 和 actor 的子集。

> **修正说明**：早期版本将 Daml 授权描述为"编译期保证授权正确性"，这一措辞过度承诺。更准确的表述是：Daml 将 signatory/observer/controller 作为语言一等概念，编译器约束模型结构；但最终的授权正确性由 Daml 执行引擎在运行时强制执行——缺失授权的交易会被 abort，不会到达提交流程。参见 [Ledger Integrity Model](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/ledger-integrity.html)。

### 4.3 Daml-LF 执行模型：消耗而非修改

Daml 使用 **UTxO 扩展模型**——合约一旦创建就不可变。"修改"合约实际上是**归档（archive）旧合约 + 创建（create）新合约**的原子操作。

```
Account Model (Solidity/EVM):         UTxO-like Model (Daml):

  ┌──────────────┐                    ┌──────────────┐
  │ Contract     │                    │ IOU v1       │
  │ balance: 100 │                    │ owner: Alice │
  │              │  ─── transfer ──►  │ amount: 100  │
  │ balance: 80  │  (mutate in place) │              │
  │              │                    │ ARCHIVED ✗   │
  └──────────────┘                    └──────────────┘
  Same address,                              │
  mutable state                              │ Exercise Transfer
                                             │ (atomic: archive old + create new)
                                             ▼
                                      ┌──────────────┐  ┌──────────────┐
                                      │ IOU v2       │  │ IOU v3       │
                                      │ owner: Alice │  │ owner: Bob   │
                                      │ amount: 80   │  │ amount: 20   │
                                      │ ACTIVE ✓     │  │ ACTIVE ✓     │
                                      └──────────────┘  └──────────────┘
                                      New ContractIds,
                                      immutable content
```

**UTxO-like 模型的优势**：

1. **天然的并发安全**：不可变合约消除了竞态条件。两笔交易不可能同时修改同一个合约——它们会尝试消耗同一输入，其中一个必然失败。
2. **完整的审计轨迹**：每次"修改"都创建新合约，历史完全可追溯。
3. **Transient 合约**：在同一交易中创建和消耗的中间合约，不会持久化——类似于函数式编程中的中间值。
4. **隐私友好**：每个合约有唯一的 ContractId，不存在"看到同一地址的不同状态"的问题。

**非消耗性行使（Non-consuming Exercise）**：Daml 还支持不消耗合约的 exercise——合约保持活跃，但执行了一个 choice。这适合查询、委托和报告场景。

### 4.4 Daml vs Solidity 能力对比

| 维度 | Daml 能做但 Solidity 做不到 | Solidity 能做但 Daml 做不到 |
|------|---------------------------|---------------------------|
| **授权** | 语言级授权建模 + 运行时强制执行；signatory/observer/controller 语义是账本模型的一等概念 | 运行时 modifier 检查（如 onlyOwner），可被绕过 |
| **隐私** | 原生子交易级隐私；Observer 只看到相关部分 | 无原生隐私；所有状态全局可见 |
| **确定性** | 编译器保证确定性执行（无随机、无 I/O） | 依赖 block.timestamp, blockhash 等可操纵变量 |
| **义务绑定** | 不能在未授权时绑定 Party | 合约可以随意 emit 事件或改变任何人的状态 |
| **可组合性** | 跨 Participant 多方工作流；跨 Synchronizer 通过 reassignment 协调但非原子 | DeFi 可组合性（flash loans, composable protocols） |
| **类型安全** | 强类型 + Haskell 级别类型推导 | 基本类型安全，但 ABI encoding 可能出错 |
| **升级** | 合约不可变（通过 migration 模式升级） | 代理模式（Proxy pattern）支持原地升级 |
| **Token 标准** | Daml Finance 库（类型安全但非标准化） | ERC-20/721/1155（广泛采用的标准） |
| **Gas 机制** | 无 Gas（流量管理基于 payload 大小） | Gas 机制（计算复杂度定价） |
| **递归/循环** | Haskell 风格递归（有栈深限制） | 循环（但有 Gas 限制） |
| **存储模型** | 不可变合约（UTxO 扩展） | 可变存储槽（SSTORE/SLOAD） |
| **工具生态** | 较小（IDE, REPL, 少量库） | 巨大（Hardhat, Foundry, OpenZeppelin, 数千库） |
| **开发者池** | 很小（需学习类 Haskell 语法） | 巨大（数十万 Solidity 开发者） |

**关键差异总结**：Daml 在**安全性和隐私保证**上有根本优势——语言级授权建模、运行时授权强制执行、确定性执行、原生隐私。但 Solidity 在**灵活性、可组合性和生态系统**上有压倒性优势——DeFi 可组合性、代理升级模式、标准化 Token 接口、庞大的开发者社区。

---

## 5. 企业级特性清单

| 需求 | Canton 的方案 | 设计取舍 |
|------|-------------|---------|
| **数据隐私** | Sub-transaction privacy via Merkle DAG projections。每个 Participant 只存储和看到自己参与的合约子集。Sequencer 和 Mediator 无法读取交易内容（端到端加密）。GDPR 合规——数据可删除（非全局副本）。 | **+** 原生子交易级隐私，无需额外隐私层；GDPR 原生支持。**-** 元数据泄露（Sequencer 可观察通信模式）；信任 Participant 运营者不泄露数据；隐私保证依赖加密和协议设计而非数学证明（vs ZKP）。 |
| **准入控制** | 许可制网络。Party 必须通过 Participant Node 承载才能参与。三级权限模型（Observation / Confirmation / Submission）。External Party 支持自主密钥管理。 | **+** 精细的权限分级；支持企业治理要求。**-** 非开放网络，参与门槛高；需要 Participant 运营者的配合。 |
| **合规审计** | 完整审计轨迹——所有交易历史在 Participant 的 PostgreSQL 中持久化。监管者可被添加为 Observer，直接看到相关合约和交易。链上 KYC 凭证合约（KYCCredential template）。Explicit Disclosure 支持选择性信息共享。 | **+** 审计轨迹完整且可证明（vs ZKP 的不可审计性）；监管者可获得实时可见性。**-** 需要在 Daml 应用层实现合规逻辑；KYC 映射需要链下配合；增加 Observer 会扩大信息传播范围。 |
| **身份管理** | 密码学身份（key fingerprint-based UID）与法律身份分离。分层命名空间委托（3 级权限）。密钥轮换和撤销支持。DecentralizedNamespaceDefinition 支持多方共有身份。 | **+** 系统有效性不依赖真实身份——隐私更强；密钥轮换不影响系统运行。**-** 密码学身份到法律身份的映射需要链下机制；密钥管理复杂度高于传统 KYC 模型。 |
| **互操作性** | 多 Synchronizer 架构——Participant 可同时连接多个 Synchronizer。Reassignment 协议支持跨 Synchronizer 合约迁移。Global Synchronizer 作为跨域协调的公共基础设施。Sequencer 后端可插拔（Canton BFT / Ethereum / Fabric）。 | **+** 真正的跨链互操作（不是桥接，而是原生协议）；Global Synchronizer 提供通用协调点。**-** Reassignment 非原子，合约在转移中暂不可用；无跨 Synchronizer 全局排序；仅限 Canton 生态内互操作（无法与 Ethereum 主网直接互操作）。 |
| **性能/吞吐量** | 水平扩展——增加 Synchronizer 分散负载。无全局状态瓶颈——每个 Participant 只处理自己相关的交易。流量管理系统（基于 payload 大小 × 收件人数的成本计算）。PostgreSQL 后端存储。 | **+** 理论上线性扩展——增加 Synchronizer 不影响现有 Synchronizer 的吞吐量。**-** 2PC 协议引入额外往返延迟；加密/解密开销；无公开的 TPS 基准数据（但声称每月处理 $2T+ 的资产代币化）。 |
| **可升级性** | 合约不可变——升级通过 migration 模式（archive old + create new）。Daml-LF 字节码版本化。内容寻址 Template ID（通过哈希保证不变性）。Polyglot Canton 白皮书已发布（计划支持 Solidity/Wasm）。 | **+** 不可变合约消除了代理升级的安全风险；版本化保证向后兼容。**-** 升级需要显式迁移所有合约实例；大规模迁移的操作复杂度高；Polyglot 支持尚未落地。 |

---

## 6. 关键设计取舍总结

### Tradeoff 1: 子交易隐私 vs 协议复杂性

| 选择 | Canton 的决策 |
|------|-------------|
| **得到** | 子交易级精细隐私控制；GDPR 原生合规；每方只看到自己相关的数据切片 |
| **付出** | Merkle DAG 构造和投影计算的开销；2PC 协调增加延迟；Divulgence/Disclosure 机制的语义复杂性；应用开发者需要理解隐私边界 |
| **深层影响** | 这个选择使 Canton 从根本上不是传统区块链。它放弃了"全局共享状态"这个区块链的核心属性，换取了企业级隐私。这不是一个优化决策，而是一个范式选择。 |

### Tradeoff 2: 确定性执行 vs 灵活性

| 选择 | Canton 的决策 |
|------|-------------|
| **得到** | 语言级授权建模 + 运行时授权强制执行；隐私投影的可行性（因为结果可预计算）；无 MEV（执行结果不依赖排序） |
| **付出** | 无法访问外部数据（oracle 需要通过额外机制）；无随机性来源；Daml 表达能力受限于函数式范式 |
| **深层影响** | 确定性执行是 Canton 隐私模型的**基石**——如果执行不确定，就无法通过投影让不同方独立验证同一交易。这意味着 Daml 的限制不是疏忽，而是隐私保证的必要条件。 |

### Tradeoff 3: 许可制网络 vs 开放参与

| 选择 | Canton 的决策 |
|------|-------------|
| **得到** | 明确的身份和治理结构；符合金融监管要求；防止匿名攻击；可执行 SLA |
| **付出** | 参与门槛高（需要 Participant Node）；无法实现 DeFi 式的无许可可组合性；网络效应受限于联盟成员 |
| **深层影响** | 这反映了 Canton 的目标市场——受监管的金融机构。这些机构不需要无许可网络，反而需要明确知道谁在网络上。但这也意味着 Canton 不太可能成为"通用计算平台"。 |

### Tradeoff 4: 不可变合约模型 vs 原地升级

| 选择 | Canton 的决策 |
|------|-------------|
| **得到** | 完整审计轨迹；天然并发安全（无竞态条件）；每个合约状态有唯一标识；防止代理模式的安全漏洞 |
| **付出** | 升级需要迁移所有合约实例；大规模系统的迁移操作复杂；ContractId 随每次"修改"变化，引用管理更复杂 |
| **深层影响** | 不可变模型使得 Canton 的存储模式更接近事件溯源（event sourcing）而非可变数据库。这天然适合金融系统的审计要求，但增加了日常运维复杂度。 |

### Tradeoff 5: Sequencer-Mediator 分离 vs 系统简洁性

| 选择 | Canton 的决策 |
|------|-------------|
| **得到** | 最小化信息暴露面——排序器看不到内容，协调器看不到排序；各组件独立扩展和去中心化；可插拔排序后端 |
| **付出** | 额外的网络往返（Participant ↔ Sequencer ↔ Mediator ↔ Sequencer ↔ Participant）；系统运维复杂度增加（两个独立组件）；调试和监控更困难 |
| **深层影响** | 这个分离是对"关注点分离"原则的极致应用。它使得 Canton 在安全分析上更清晰——每个组件的威胁模型是独立的。但代价是额外的延迟和运维开销。 |

### Tradeoff 6: 虚拟全局账本 vs 全局查询能力

| 选择 | Canton 的决策 |
|------|-------------|
| **得到** | 无全局状态瓶颈，理论上线性扩展；数据主权——每方控制自己的数据；GDPR 合规 |
| **付出** | 无法做全局查询（如"网络上总共有多少 Token？"）；跨方数据聚合需要应用层协调；分析和报告依赖于显式数据共享 |
| **深层影响** | 这是 Canton 最反直觉的设计——一个没有全局状态的"区块链"。这使得某些在 Ethereum 上轻而易举的操作（如 `totalSupply()`）在 Canton 上需要完全不同的设计模式。 |

### Tradeoff 7: 非原子跨域转移 vs 协议简洁性

| 选择 | Canton 的决策 |
|------|-------------|
| **得到** | 更简单的协议设计；无需跨域锁定机制；每个 Synchronizer 独立运行不受跨域交易影响 |
| **付出** | 合约在 Reassignment 过程中暂时不可用；Assignment 失败可能导致合约"卡住"；应用需要显式处理争用 |
| **深层影响** | Canton 选择了 CAP 定理中的 AP 而非 CP——优先保证可用性和分区容忍，而非强一致性。这在多 Synchronizer 部署中意味着开发者必须设计容忍不一致的工作流。 |

---

## 7. 优势与局限性评估

### 7.1 核心优势

1. **业界唯一的子交易级隐私**：Canton 的 Merkle DAG 投影机制在所有企业区块链中是独一无二的。Hyperledger Fabric 有 Private Data Collections（通道级隐私），Corda 有事务级隐私——但都没有达到 Canton 的子交易级粒度。这使得 Canton 是唯一一个能在单笔多方交易中让不同参与者看到不同子集的平台。

2. **GDPR 原生合规**：因为不存在全局状态副本，每个 Participant 可以独立删除自己持有的数据，而不影响其他 Participant 或系统完整性。这在其他区块链上几乎不可能实现。

3. **证明系统完整性的审计能力**：与 ZKP 方案不同，Canton 允许授权方查看实际交易数据。如果系统被攻破，审计轨迹可以证明发生了什么。ZKP 方案在失败时"无声失败"——无法区分"正常运行"和"已被攻破"。

4. **确定性执行消除 MEV**：因为 Daml 的确定性和 Sequencer 看不到交易内容，Canton 从架构上消除了 MEV（Miner/Maximal Extractable Value）这一困扰公链的核心问题。

5. **水平扩展性**：增加 Synchronizer 可以线性扩展吞吐量，每个 Synchronizer 独立运行。这避免了单一链的吞吐量瓶颈。

6. **企业级采用验证**：450+ 参与者（包括 Goldman Sachs、HSBC、DTCC 等全球头部金融机构），月处理量 $2T+。这不是理论性项目，而是已被大规模验证的生产系统。

### 7.2 核心局限

1. **开发者生态极小**：Daml 是一个利基语言（类 Haskell DSL）。全球 Daml 开发者可能只有数百到数千人，与 Solidity 的数十万开发者相比微不足道。Polyglot Canton（支持 Solidity/Wasm）已在白皮书阶段，但尚未落地。这是 Canton 最大的战略风险。

2. **无法做全局查询**：因为没有全局状态，像"网络上总共有多少 Token"这样的简单查询需要完全不同的设计模式（显式数据聚合或中心化报告服务）。这增加了应用开发复杂度。

3. **跨域转移的非原子性**：Reassignment 协议是非原子的，合约在转移过程中可能暂时不可用甚至"卡住"。虽然这简化了协议设计，但给应用层增加了额外的错误处理复杂度。

4. **元数据隐私不足**：尽管交易内容被加密，Sequencer 仍然可以观察通信模式（谁和谁通信、多频繁、消息多大）。在某些场景下，元数据本身就包含有价值的信息（例如，两个机构突然开始高频通信可能暗示即将发生的交易）。

5. **许可制限制了网络效应**：Canton 的许可制设计限制了无许可创新（DeFi 的核心驱动力）。它无法实现 flash loans、无许可 AMM 等 DeFi 原语——这些需要任何人都能参与。

6. **无公开性能基准**：尽管声称处理 $2T+/月，Canton 没有公开的 TPS 基准测试。2PC 协议和加密操作引入的额外延迟难以量化。对于需要评估性能的潜在采用者，这是一个信息缺口。

7. **单一供应商依赖**：Canton 的核心开发由 Digital Asset 主导。虽然代码开源（Apache-2.0），但 Scala 技术栈和 Daml 语言的专业性意味着外部贡献者有限。对比 Ethereum 的多客户端生态（Geth, Nethermind, Besu, Erigon），Canton 的技术多样性风险更高。

### 7.3 适用场景评估

```
Canton 最适合的场景：
✅ 多方金融交易（DvP、DVP、跨机构清结算）
✅ 需要 GDPR 合规的受监管环境
✅ 需要精细隐私控制的联盟场景
✅ 需要可审计性的合规密集型行业（金融、医疗、供应链）
✅ 已有明确参与者身份的企业联盟

Canton 不太适合的场景：
❌ 需要无许可参与的公链应用（DeFi）
❌ 需要大量外部数据集成的应用（oracle 密集型）
❌ 需要庞大开发者社区的平台选择
❌ 需要全局查询能力的分析密集型应用
❌ 预算有限的小型项目（Participant 运维成本高）
```

---

## 8. 给 M2/M3 的可复用架构结论

本节从 Mantle 企业化适配的视角，将 Canton 的关键能力分为**可复制、难复制、不建议复制**三类，并提供跨项目对比的标准化字段。此节直接服务于 WHI-343（隐私比较）、WHI-344（权限比较）、WHI-345（共识/DA 比较）、WHI-350（Gap 分析）和 WHI-357（理想架构蓝图）。

### 8.1 Mantle 企业化适配矩阵

| Canton 特性 | 对比维度 | 与 Fabric/Besu/ZK/Tempo 的核心差异 | Mantle（OP Stack）可复制性 | 设计风险 |
|------------|---------|-----------------------------------|--------------------------|---------|
| **Need-to-know 子交易投影** | 隐私粒度 | Fabric: 通道级隐私；Besu: 无原生隐私；ZK: 交易级数学隐藏；Tempo: 加密存款模型 | **难复制**——依赖 Daml 的确定性执行和 UTxO-like 合约模型，与 EVM 的账户模型不兼容。但投影思想可启发基于 access control list 的视图层设计 | 强行在 EVM 上实现子交易投影需要重写执行层，工程量巨大 |
| **Permissioned Participant Registry** | 准入机制 | Fabric: MSP 准入；Besu: 节点白名单；ZK: 无原生准入；Tempo: Zones 准入控制 | **可复制**——OP Stack 可在 Sequencer/Validator 层添加许可制节点注册，不需要改动执行层 | 需要平衡开放性与准入控制，避免过度中心化 |
| **Observer/Audit Party 角色** | 合规审计 | Fabric: 审计通道；Besu: 读权限控制；ZK: 有限的选择性披露；Tempo: 未明确 | **可复制**——在 Rollup 层设计 "审计节点" 角色，可获取全部或子集交易数据的只读访问权 | 审计数据范围和实时性需要明确定义 |
| **Sequencer-Mediator 分离** | 架构分离 | 所有其他系统: Sequencer 同时负责排序和执行 | **部分可复制**——OP Stack 已有 Sequencer-Verifier 分离，可进一步细化角色，但完全分离排序和确认需要重大架构重构 | Sequencer 仍然可以看到交易明文（vs Canton Sequencer 只看到密文） |
| **2PC 共识（利益相关方确认）** | 共识模型 | 传统 BFT: 所有验证者投票；ZK: 数学证明替代投票 | **不建议复制**——2PC 只适合利益相关方明确的场景（Canton 的 Party 模型）；OP Stack 的 Rollup 模型基于 Sequencer+Fraud Proof，引入 2PC 会根本改变安全模型 | 混合 2PC 和 Fraud Proof 会增加攻击面，安全分析复杂化 |
| **Daml 授权模型（Signatory/Observer/Controller）** | 授权模型 | Solidity: runtime modifier 检查；Fabric: endorsement policies | **难复制**——根植于 Daml 语言的类型系统和 UTxO 语义，无法直接移植到 EVM/Solidity。但 signatory-based 授权的理念可通过 smart contract access control patterns 部分实现 | 在 EVM 上的实现退化为 runtime modifier（onlyOwner 等），丧失编译时保证 |
| **不可变合约（UTxO-like 模型）** | 状态模型 | EVM: 可变存储槽；Fabric: KV 存储 | **不建议复制**——EVM 的账户模型和存储槽是 Solidity 生态的基础，改为 UTxO 模型等于放弃整个 EVM 生态兼容性 | 与 Solidity 工具链完全不兼容 |
| **多 Synchronizer 水平扩展** | 可扩展性 | ZK: 多 Rollup；Tempo: 多 Zones | **可复制（部分）**——OP Stack 的 Superchain 理念已有多 Rollup 架构，可参考 Canton 的 Reassignment 协议设计跨链资产转移（但需注意非原子性问题） | 非原子性 Reassignment 在 DeFi 场景中可能不可接受 |
| **端到端加密交易内容** | 数据加密 | 其他系统: 交易通常明文上链 | **可复制**——在 Sequencer 侧实现交易内容加密，只存储加密后的 calldata/blob。挑战在于 Verifier 如何验证加密交易 | 加密交易与 Fraud Proof 验证存在根本张力——Verifier 需要明文才能重执行 |
| **GDPR 合规（数据可删除）** | 合规 | 传统区块链: 不可变历史 | **难复制**——Rollup 的 DA 层（Ethereum calldata/blob）数据上链后不可删除；Canton 能删除是因为没有全局副本 | 可能的折中：将敏感数据存储在链下 DA 层（如 Validium 模式），链上只存储哈希 |

### 8.2 可复制能力的优先级排序

基于实现难度和企业价值的综合评估，建议 Mantle 企业化方案优先复制以下 Canton 能力：

```
优先级 1（高价值、可行性高）:
├── Permissioned Participant Registry（准入注册）
├── Observer/Audit Party 角色（合规审计）
└── 端到端加密交易内容（数据隐私基础）

优先级 2（高价值、需设计适配）:
├── 多 Rollup 水平扩展 + 跨链资产转移
├── Sequencer 角色进一步细化（减少信息暴露面）
└── 基于 smart contract 的 Signatory-like 授权模式

优先级 3（理念参考、不直接复制实现）:
├── Need-to-know 投影思想（转化为 view-based access control）
├── 不可变审计轨迹（在可变存储基础上增加 event sourcing 层）
└── 确定性执行消除 MEV（参考但实现路径不同）
```

### 8.3 WHI-334 开放问题解决状态

以下逐项标注 WHI-334 Section 8 中的 deeper-investigation 清单在本文档中的解决状态：

| # | 问题 | 状态 | 位置/说明 |
|---|------|------|---------|
| 1 | Synchronizer BFT/故障模型、view change、恢复流程 | **部分解决** | Section 3.2 BFT Sequencer + Section 3.5 故障矩阵覆盖架构层故障模型；view-change 和具体恢复实现仍需 WHI-336 代码分析验证 |
| 2 | Mediator Verdict 密码学流程 | **部分解决** | Section 3.1 提交协议流程中描述了 verdict 发出过程；密码学细节（verdict 是否有 ZK 证明）在官方文档中标记为 WIP，留给 WHI-336 代码分析 |
| 3 | 跨 Synchronizer Reassignment 故障/原子性边界 | **已解决** | Section 1.4 + Section 3.5.4 Reassignment 故障矩阵 |
| 4 | 不同 Sequencer 后端的排序差异 | **部分解决** | Section 3.2 的可插拔后端表格覆盖了安全性/性能特征；具体延迟数据无公开基准，留给 WHI-336 |
| 5 | Global Synchronizer 治理/Super Validator 准入 | **未解决** | 官方文档未提供足够细节，非 WHI-335 核心范围；建议在 WHI-342（行业调研）中覆盖 |
| 6 | Canton Coin 经济模型 | **未解决** | 同上，经济模型属于治理层面，留给行业调研 |
| 7 | Synchronizer 间自动路由逻辑 | **已解决** | Section 1.4 描述了路由器优先级逻辑（最高优先级 > 最少重新分配次数 > 最低 Synchronizer ID） |
| 8 | Participant PostgreSQL 恢复 | **部分解决** | Section 3.5.3 覆盖备份恢复、消息重放和 ACS Commitment 校验；消息保留策略与重建实现细节仍需 WHI-336 代码分析验证 |
| 9 | 监管节点/Regulatory Observer 角色 | **已解决** | Section 5 企业特性清单（合规审计行）+ Section 4.1 Observer 语义 |
| 10 | GDPR 数据删除机制 | **部分解决** | Section 1.1、5、7.1 中多次提及 GDPR 合规能力；具体跨 Participant 协调删除的实现细节留给 WHI-336 |
| 11-14 | 代码与实现相关 | **留给 WHI-336** | 这些问题需要代码库分析，不在 WHI-335 范围内 |
| 15-17 | 企业采用验证 | **部分解决** | Section 7.1 引用了采用数据；独立验证和监管认可状态留给 WHI-342 |

---

## 参考来源

- [Canton 协议机制文档](https://docs.digitalasset.com/overview/3.4/explanations/canton/protocol.html)
- [Canton 隐私模型规范](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/ledger-privacy.html)
- [Canton 拓扑管理文档](https://docs.digitalasset.com/overview/3.4/explanations/canton/topology.html)
- [Canton 去中心化机制](https://docs.digitalasset.com/overview/3.4/explanations/canton/decentralization.html)
- [Canton 账本完整性模型](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/ledger-integrity.html)
- [Canton 多 Synchronizer 操作](https://docs.digitalasset.com/overview/3.4/explanations/canton/multi-synchronizer.html)
- [Canton 账本结构](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/ledger-structure.html)
- [Global Synchronizer](https://canton.network/global-synchronizer)
- [ZKP vs Canton 隐私对比博客](https://www.canton.network/blog/zero-knowledge-proofs-whe-privacy-needs-more)
- [Canton vs EVM RWA 代币化对比](https://blog.digitalasset.com/blog/tokenization-of-rwas-on-canton-network-vs-evm-chains-part-2)
- [WHI-334 Canton 官方文档与白皮书调研](./WHI-334-canton-docs-research.md)
