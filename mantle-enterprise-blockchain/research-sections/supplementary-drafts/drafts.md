## 3. Canton 特性详解

Canton 是由 Digital Asset 开发的企业级分布式账本协议，其核心创新在于**子交易级隐私（sub-transaction privacy）**和**Daml 智能合约语言**。与传统区块链（如 Ethereum）追求"全节点持有相同全局状态"的设计范式不同，Canton 从根本上放弃了全局共享状态，转而构建了一个"虚拟全局账本（Virtual Global Ledger）"——这个账本在逻辑上是完整的，但在物理上不存在于任何单一节点之上。每个参与方只能看到和存储自己有权看到的数据切片（projection），形成独立的、因果一致的本地视图。

这一范式选择使 Canton 更像是一个**隐私优先的交易协调协议**，而非传统意义上的区块链。它的架构由三层组成：Participant 层（运行 Daml 引擎，维护本地合约状态）、Synchronizer 层（由 Sequencer + Mediator 组成，负责消息排序和交易确认）、以及 Canton Network 层（通过 Global Synchronizer 提供跨 Synchronizer 互操作）。

本章将围绕三个核心问题展开：在没有全局状态的前提下，Canton 如何保证状态一致性？Canton 的共识机制为何更接近数据库 2PC 而非区块链共识，这样设计的取舍是什么？Canton 的隐私设计方案为何选择了 Merkle DAG 投影而非零知识证明？

---

### 3.1 Canton 在没有全局状态的情况下是如何保证状态一致性的

在传统区块链中，状态一致性的保证非常直观——所有节点维护完全相同的全局状态副本，共识算法确保每个节点以相同顺序执行相同的状态转换。Canton 放弃了这一前提，那么它如何确保分布在不同 Participant 上的、互不完整的本地状态仍然是"正确的"？

答案是：**Canton 维护的不是全局状态一致性，而是合约级别的状态一致性。** 具体而言，Canton 通过多层机制的协作来保证一致性，其保证的粒度和方式取决于交易所涉及的合约分布。

#### 3.1.1 单合约状态一致性：UTxO-like 不可变模型

Canton 使用类似 UTxO（Unspent Transaction Output）的扩展模型来管理合约状态。合约一旦创建就不可变——"修改"合约实际上是**归档（archive）旧合约 + 创建（create）新合约**的原子操作。每个合约有唯一的 `ContractId`，一旦被消耗（consuming exercise），便永久标记为已归档，不可再次使用。

```
Account 模型 (Solidity/EVM):              UTxO-like 模型 (Daml):

  ┌──────────────┐                         ┌──────────────┐
  │ Contract     │                         │ IOU v1       │
  │ balance: 100 │                         │ owner: Alice │
  │              │  ─── transfer ──►       │ amount: 100  │
  │ balance: 80  │  (原地修改)              │              │
  │              │                         │ ARCHIVED ✗   │
  └──────────────┘                         └──────────────┘
  同一地址，                                       │
  可变状态                                         │ Exercise Transfer
                                                   │ (原子操作: 归档旧合约 + 创建新合约)
                                                   ▼
                                           ┌──────────────┐  ┌──────────────┐
                                           │ IOU v2       │  │ IOU v3       │
                                           │ owner: Alice │  │ owner: Bob   │
                                           │ amount: 80   │  │ amount: 20   │
                                           │ ACTIVE ✓     │  │ ACTIVE ✓     │
                                           └──────────────┘  └──────────────┘
                                           新 ContractId,
                                           内容不可变
```

这一模型天然提供了合约级一致性保证：同一合约不能被行使两次（双花防护），因为第一次消耗性行使（consuming exercise）会将其标记为已归档，后续任何尝试使用该合约的交易在 Participant 本地验证时就会被拒绝。

#### 3.1.2 单笔交易中涉及多个合约的状态更新：Merkle DAG 与 2PC 保证原子性

当一笔交易涉及多个合约的状态变更时（例如 DvP 交易中同时转移资金和交付证券），Canton 通过两个机制保证原子性：

**机制一：Merkle DAG 交易树结构。** Canton 将整笔交易编码为一棵 Merkle DAG（有向无环图），每个合约操作（创建、行使、归档）是树中的一个节点。这种递归嵌套的树形结构使得一笔交易可以包含多笔内部子交易，同时保持结构上的完整性——整棵树的根哈希（root hash）作为交易的唯一标识和完整性承诺。

**机制二：两阶段提交（2PC）协议保证全有或全无。** Mediator 协调所有相关 Participant 的确认：

1. 提交者构造交易 Merkle DAG，将不同子树加密后分发给各 Participant
2. 每个 Participant 独立验证自己可见的子树（合约是否活跃？授权是否正确？业务逻辑是否符合？）
3. 所有 Confirmer 都发出 APPROVE → Mediator 出具 APPROVE verdict → 所有相关 Participant 同步更新本地 ACS
4. **任何一方**发出 REJECT 或超时未响应 → Mediator 出具 REJECT verdict → 交易整体回滚，没有任何合约状态变更

这意味着在一笔涉及多个合约的交易中，要么所有合约变更同时生效，要么全部不生效。这就是原子性保证。

#### 3.1.3 多笔交易、单个合约、单个 Synchronizer

如果用户连续提交多笔交易，且这些交易都涉及同一个合约（或同一组位于同一 Synchronizer 上的合约），那么一致性由 **Sequencer 的全局排序** 保证。

Sequencer 为所有消息分配确定性的批次时间戳，确保所有 Participant 以完全相同的顺序接收和处理消息。在单个 Synchronizer 内，Canton 提供**因果一致性**：如果交易 A 的输出是交易 B 的输入，那么 A 一定在 B 之前被处理。

由于合约是不可变的（UTxO-like 模型），两笔交易不可能同时修改同一个合约——它们会尝试消耗同一输入，Sequencer 的排序保证其中一个先到，另一个因发现合约已被归档而被本地验证拒绝。

#### 3.1.4 多笔交易涉及多个合约、跨 Synchronizer：Reassignment

如果用户的交易涉及分布在不同 Synchronizer 上的合约，情况变得更为复杂。Canton 通过**重新分配（Reassignment）**机制处理：将需要参与交易的合约从其当前所在的 Synchronizer 迁移到目标 Synchronizer，然后在同一个 Synchronizer 上执行交易以确保原子性。

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
│                │                    │  3. 在此执行    │
│                │                    │  交易(X + Y)    │
│                │                    │  Contract Y    │
│                │                    │  (已在此处)     │
└────────────────┘                    └────────────────┘
```

Reassignment 分为两个阶段：**Unassignment**（合约在源 Synchronizer 上变为非活跃）和 **Assignment**（合约在目标 Synchronizer 上激活）。

**关键限制**：Reassignment 是**非原子的**。这两个阶段发生在不同的 Synchronizer 上，没有全局锁定机制。这意味着：

- 合约在 Unassign 之后、Assign 之前处于"中间态"——在两个 Synchronizer 上都不可用
- 如果 Assignment 步骤因故障而未完成，合约可能暂时"卡在半空中"（stuck in limbo）
- 不同 Synchronizer 之间没有全局排序保证——事件可以以任意顺序出现在 Participant 的更新流中

Canton 通过 **Assignment Exclusivity 窗口**（限定谁可以在窗口内完成 Assignment）和 **Reassignment Counter**（递增计数器防止旧请求重放）来缓解这些风险，但非原子性是有意为之的设计——要实现跨 Synchronizer 原子性需要全局锁定，这会严重损害性能和可用性。

#### 3.1.5 事后检测：ACS Commitment 交换

除了上述事前和事中的一致性保证，Canton 还提供事后检测机制：**ACS Commitments（活跃合约集承诺交换）**。

Participant 之间定期交换自己 ACS 的密码学承诺（cryptographic commitment），如果一个 Participant 的 ACS 与其他持有同一 Party 投影的 Participant 预期不一致，系统可以检测到异常。这类似于分布式数据库中的"反熵（anti-entropy）"机制——即使某些拜占庭行为在发生时不可阻止，定期一致性检查可以在事后发现。

#### 3.1.6 一致性模型总结

| 场景 | 一致性保证机制 | 保证强度 |
|------|---------------|---------|
| 单合约双花防护 | UTxO-like 不可变模型 | 强：合约只能被消耗一次 |
| 单笔交易多合约原子性 | Merkle DAG + 2PC | 强：全有或全无 |
| 单 Synchronizer 内多笔交易排序 | Sequencer 全局排序 | 强：因果一致性 |
| 跨 Synchronizer 合约迁移 | Reassignment (Unassign + Assign) | 弱：非原子，有中间态 |
| 事后不一致检测 | ACS Commitment 定期交换 | 检测级：发现异常但不自动修复 |

**核心洞察**：Canton 的一致性不是"所有人看到相同数据"（强全局一致性），而是"所有人对自己可见部分的解释是一致的"。这类似于分布式系统中的**因果一致性**模型，但增加了密码学验证层和 2PC 协调层。Canton 选择了 CAP 定理中的 AP（可用性 + 分区容忍）而非 CP——优先保证可用性和水平扩展能力，在跨 Synchronizer 场景中容忍有限的不一致窗口。

---

### 3.2 Canton 的共识机制：为什么更接近 2PC 而非区块链共识

Canton 的共识机制在企业区块链中是独特的：它既不是传统的 BFT 共识（如 PBFT、Tendermint），也不是 Nakamoto 式的概率性共识，而是一种**数据库两阶段提交（2PC）与 BFT 排序层的混合体**。理解这一设计选择，需要从传统区块链共识的核心假设谈起。

#### 3.2.1 传统区块链共识的核心假设

传统 BFT 共识（如 Tendermint、PBFT）的运作逻辑是：

1. **Leader 提议**：轮转的 Leader 将交易打包成区块
2. **全网投票**：**所有验证者**对区块进行投票
3. **阈值确认**：2/3 多数投票通过 → 区块上链
4. **全局执行**：所有节点执行相同的状态转换

关键特征：所有验证者看到全部交易内容，参与每一笔交易的确认。这保证了全局一致性，但代价是：(1) 隐私为零——验证者看到所有数据；(2) 吞吐量受限于最慢的验证者；(3) 排序器/Leader 具备 MEV 提取能力。

#### 3.2.2 Canton 的做法：只有利益相关方参与

Canton 将"共识"这一单一概念分解为两个独立的关注点：

- **消息排序（Sequencer）**：为所有消息分配确定性时间戳，但看不到消息内容
- **交易确认（Mediator + Participants）**：只有利益相关方参与确认，且每方只看到自己有权看到的子树

```
              传统 BFT 共识                       Canton 协议
            (Tendermint/PBFT)             (Sequencer + Mediator 2PC)
           ─────────────────             ──────────────────────────

目的:       全局状态转换达成一致             相关方就特定交易达成一致

参与者:     所有验证者                       只有 informees 的 Participants

可见性:     所有验证者看到全部交易           每个 Participant 只看到自己的子树

协调者:     轮转 Leader                      Mediator（可多个，阈值投票）

终局性:     2/3 投票 → 即时终局              所有 confirmers 同意 → 终局
            (Tendermint)                     或任一方拒绝 → 回滚

区块:       有（批量交易打包）               无（单笔交易独立提交确认）

全局排序:   是（区块高度 = 全局序列）        仅 Synchronizer 内排序
```

#### 3.2.3 Canton 更接近 2PC 的五个理由

1. **无区块概念**：Canton 没有批量打包——每笔交易独立提交和确认。Sequencer 虽然在内部使用 `RawLedgerBlock` 作为排序批次抽象，但这是排序层的实现细节，不等同于 Ethereum 式的全局执行 block。

2. **参与方限制**：只有利益相关方（informees）参与确认，而非网络中的所有验证者。一笔 Alice-Bob 之间的交易，与 Carol 完全无关的 Participant 甚至不知道这笔交易的存在。

3. **协调者角色**：Mediator 类似于数据库 2PC 的 Coordinator——收集各方投票、出具最终裁决。而非区块链的 Leader/Proposer 角色。

4. **回滚语义**：**任何一方拒绝即回滚**——这是典型的 2PC 语义（全票通过才提交）。BFT 共识采用多数投票（2/3 通过即可），容忍少数异议。

5. **无概率性终局**：不存在"确认数累积"的概念。交易要么在 Mediator 裁决后立即提交，要么立即回滚。没有 Optimistic Rollup 的 7 天挑战窗口，也没有 PoW 的概率性终局。

#### 3.2.4 但 Canton 又超越了传统 2PC

Canton 不是简单的数据库 2PC。它在传统 2PC 之上增加了三个区块链/分布式账本领域的特性：

1. **Sequencer 的 BFT 排序层**：传统 2PC 的 Coordinator 直接与参与者通信，不需要全局排序。Canton 的 Sequencer 提供了消息的全局一致排序（在单个 Synchronizer 内），且支持多种后端实现——Canton 原生 BFT、Ethereum、Hyperledger Fabric 或数据库。BFT 部署（2/3 多数诚实假设）保证了排序层的拜占庭容错。

2. **端到端加密和隐私路由**：传统 2PC 的 Coordinator 通常能看到完整的事务内容。Canton 的 Sequencer 和 Mediator 都看不到交易明文——Sequencer 只转发加密 blob，Mediator 只收集 APPROVE/REJECT 信号。

3. **去中心化 Mediator**：可部署多个 Mediator 实例，通过阈值投票出具裁决。单个恶意 Mediator 无法左右结果（前提：threshold > 1）。传统 2PC 的 Coordinator 是单点。

#### 3.2.5 完整的交易提交流程

```
Timeline ────────────────────────────────────────────────────►

Phase 1: PREPARE（准备阶段）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Submitter        Sequencer         Participant(s)      Mediator
     │                │                    │                │
     │ 1. 构造交易    │                    │                │
     │   Merkle DAG   │                    │                │
     │   按接收方加密  │                    │                │
     │───────────────►│                    │                │
     │                │ 2. 分配时间戳      │                │
     │                │ 3. 路由加密子树    │                │
     │                │    给相关          │                │
     │                │    Participant     │                │
     │                │───────────────────►│                │
     │                │                    │ 4. 解密子树    │
     │                │                    │ 5. 本地验证:   │
     │                │                    │   - 授权正确?   │
     │                │                    │   - 合约活跃?   │
     │                │                    │   - 无双花?     │
     │                │                    │   - 模型符合?   │

Phase 2: CONFIRM（确认阶段）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     │                │                    │ 6. 发送        │
     │                │                    │   确认/拒绝     │
     │                │                    │───────────────►│
     │                │                    │                │ 7. 收集响应
     │                │                    │                │    直到截止时间
     │                │                    │                │
     │                │                    │                │ 8. 出具裁决:
     │                │                    │                │    全票通过→APPROVE
     │                │                    │                │    任一拒绝→REJECT

Phase 3: FINALIZE（终结阶段）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     │                │  9. 广播裁决       │                │
     │                │◄──────────────────►│◄───────────────│
     │                │                    │                │
     │                │                    │ 10. 应用裁决:  │
     │                │                    │   APPROVE →    │
     │                │                    │     更新 ACS   │
     │                │                    │   REJECT →     │
     │                │                    │     丢弃       │
```

#### 3.2.6 Sequencer-Mediator 分离的设计意图

将排序和确认分离到两个独立组件不是偶然的——它直接服务于 Canton 的隐私和安全目标：

**最小化信息暴露面（Least Privilege）**：没有任何单一组件拥有完整的交易视图。

```
┌────────────────────────────┐  ┌─────────────────────────────┐
│       Sequencer            │  │        Mediator              │
│                            │  │                              │
│  知道:                     │  │  知道:                       │
│  - 加密 blob               │  │  - 哪些 Participant          │
│  - 接收方列表              │  │    需要确认                   │
│  - 时间戳                  │  │  - 确认/拒绝信号              │
│  - 消息大小                │  │  - 决策截止时间               │
│                            │  │                              │
│  不知道:                   │  │  不知道:                     │
│  - 交易内容               │  │  - 交易内容                  │
│  - 合约状态               │  │  - 合约状态                  │
│  - 业务逻辑               │  │  - 业务逻辑                  │
│  - 消息发送者身份(对接收者) │  │  - 确认/拒绝的原因           │
└────────────────────────────┘  └─────────────────────────────┘
```

**独立安全域**：即使 Sequencer 被攻破，攻击者只能影响消息排序（活性攻击），无法读取交易内容或伪造确认。即使 Mediator 被攻破，攻击者只能影响裁决（例如拒绝有效交易），无法篡改消息顺序或读取交易内容。

**从架构上消除 MEV**：在传统 L2 中，排序器（Sequencer）同时负责排序和执行，因此可以看到所有交易内容，具备 MEV 提取能力。Canton 的 Sequencer 只处理加密 blob，根本无法知道交易的经济含义。

#### 3.2.7 这样设计的取舍

| 得到 | 付出 |
|------|------|
| 隐私保护：没有单一组件看到完整交易 | 额外的网络往返延迟（Participant ↔ Sequencer ↔ Mediator ↔ Sequencer ↔ Participant） |
| 从架构上消除 MEV | 系统运维复杂度增加（两个独立组件需独立部署和监控） |
| 各组件独立扩展和去中心化 | 调试更困难（问题可能出在排序层或确认层） |
| 排序后端可插拔（Canton BFT / Ethereum / Fabric） | 排序和确认协议的交互增加了协议复杂性 |
| 全票通过制保证了交易的绝对正确性 | 单方拒绝或超时即回滚——在大规模多方交易中活性风险更高 |

#### 3.2.8 终局性对比

Canton 的终局性是**确定性的、即时的、局部的**：

| 系统 | 终局性类型 | 时间 | 条件 |
|------|-----------|------|------|
| **Canton** | 确定性即时终局 | 秒级（裁决后） | 所有 confirmers 同意 |
| **Ethereum L1** | 概率性 → 确定性 | ~12min（finalized epoch） | 2/3 验证者签名 |
| **Optimistic Rollup** | 乐观终局 + 挑战 | ~7天挑战窗口 | 无挑战成功 |
| **ZK Rollup** | 证明验证后终局 | 分钟级（证明生成时间） | 有效证明上链 |
| **Tendermint** | 确定性即时终局 | ~6秒 | 2/3 验证者投票 |

Canton 终局性的特殊之处在于它是**局部的**——交易只对参与的 Participant 有效。不存在"全网确认"的概念。这意味着终局性不需要等待全网共识，只需要相关方达成一致，因此天然更快。但代价是：没有公链那种"全网可验证"的不可篡改性——一致性保证建立在 Synchronizer 运营商的诚实性假设之上。

---

### 3.3 Canton 的隐私设计方案

Canton 的隐私是其作为企业级区块链的核心卖点。与其他企业区块链的通道级隐私（如 Hyperledger Fabric）或密码学隐私（如 ZK 方案）不同，Canton 实现了**子交易级隐私（sub-transaction privacy）**——在同一笔交易中，不同参与方看到的数据切片完全不同。这在多方复杂交易场景（如 DvP、供应链金融、跨机构清算）中具有独特优势。

#### 3.3.1 核心思想：交易树 + 投影

Canton 的隐私核心在于将交易分解为一棵**子交易树（sub-transaction tree）**，然后为每一个参与方（participant）计算一个**投影（projection）**——其中只包含该方有权看到的部分。

**为什么是树形结构？** 一笔 Canton 交易不是扁平的操作列表，而是一棵递归嵌套的树。每个 action（创建、行使、归档合约）可以有后果（consequences），后果本身构成子 action。这种树形结构使得交易天然可分割——你可以沿着树的边界切出任意子集，而不会破坏剩余部分的完整性。

**为什么要投影？** 在传统区块链中，一笔交易要么整体可见，要么整体不可见（如通过 ZKP 隐藏）。但在多方交易中，往往需要更精细的可见性控制。例如在一笔 DvP（Delivery vs Payment）交易中：

- 银行只需要知道资金流转——它不关心（也不应该知道）证券的交割细节
- 登记机构只需要知道股权变更——它不关心（也不应该知道）支付金额
- 买方和卖方需要看到完整的交易流

Canton 的投影机制精确地实现了这种差异化可见性。

#### 3.3.2 Merkle DAG 与投影算法

本质上，Canton 采用了 Merkle DAG 来代替普通的交易列表。这样做的好处是可以用一个递归嵌套的树形结构来表现一笔交易（包含多笔内部子交易），然后可以根据权限设置来切分子树，从而实现子交易级别的隐私效果——这是一般隐私方案（无论是通道隔离还是 ZKP）都无法实现的粒度。

假设一笔 DvP 交易如下：

```
A: Exercise SettleTrade          informees = {Alice, Bob}
├── B: Exercise TransferIOU      informees = {Alice, Bank}
│   ├── C: Archive OldIOU        informees = {Alice, Bank}
│   └── D: Create NewIOU         informees = {Bob, Bank}
└── E: Exercise DeliverShares    informees = {Bob, Registrar}
    ├── F: Archive OldShare      informees = {Bob, Registrar}
    └── G: Create NewShare       informees = {Alice, Registrar}
```

那么在 **Bank 的视角**下，投影是：
```
B: Exercise TransferIOU
├── C: Archive OldIOU
└── D: Create NewIOU
```

Bank 只看到了资金流转部分——IOU 从 Alice 转到 Bob。它完全不知道这笔交易还涉及股权交割。

而 **Registrar（登记机构）**看到的则是：
```
E: Exercise DeliverShares
├── F: Archive OldShare
└── G: Create NewShare
```

Registrar 只看到了股权变更——股份从 Bob 转到 Alice。它完全不知道这笔交易还涉及 IOU 支付。

**Alice 的投影**（作为买方，看到完整交易）：
```
A: Exercise SettleTrade
├── B: Exercise TransferIOU
│   ├── C: Archive OldIOU
│   └── D: Create NewIOU
└── G: Create NewShare（她是新股权的持有者）
```

**Bob 的投影**（作为卖方，也看到完整交易）：
```
A: Exercise SettleTrade
├── D: Create NewIOU（他是新 IOU 的持有者）
└── E: Exercise DeliverShares
    ├── F: Archive OldShare
    └── G: Create NewShare
```

**投影算法**的规则是递归的：

```
projection(P, action) =
  if P ∩ informees(action) ≠ ∅:
    保留 action 及其所有后果  → P 看到完整子树
  else if action 有后果:
    用后果的投影替换 action  → 跳过当前节点，递归处理子节点
  else:
    丢弃 action 及其整个子树  → P 对此部分完全不可见
```

#### 3.3.3 为什么这构成了一个 DAG

这就是为什么投影后的结果是 DAG 而非链的原因：每一方看到的交易子集不同，它们之间的排序关系可能无法确定——因为中间的交易节点被投影掉了。

具体来说：Bank 看到的 TransferIOU 和 Registrar 看到的 DeliverShares 在完整交易中是兄弟节点（同属根节点 SettleTrade 的子操作），但在各自的投影中，它们互相不可见。如果 Bank 和 Registrar 各自查看自己的本地账本，它们无法确定这两个操作之间的先后顺序——因为连接它们的共同祖先节点（SettleTrade）可能在某些投影中被省略。

所以投影后的账本只保留**因果关系（happens-before）**，形成 DAG 而非线性链。这是 Canton "虚拟全局账本"概念的密码学基础——每方看到的不是完整的链，而是自己参与部分的因果子图。

#### 3.3.4 Merkle DAG 的加密实现

投影只是逻辑层面的可见性控制。在传输层面，Canton 通过以下机制确保只有有权看到的参与方能读取对应的子树内容：

1. **Merkle 树编码**：整棵交易树被编码为 Merkle 树，每个子交易节点包含加密的 action 数据和子节点的哈希引用
2. **子树致盲（Blinding）**：发送给某个 Participant 的消息中，只有该 Participant 有权看到的子树节点包含完整内容，其他节点被替换为其 Merkle 哈希——接收者可以验证隐藏部分的存在和完整性（通过根哈希），但无法读取内容
3. **端到端加密**：每个 View（可见子树）使用对称密钥加密，对称密钥再用接收方的公钥加密后分发。Sequencer 只看到加密 blob
4. **根哈希承诺**：整棵树的根哈希作为 commitment 发送给所有参与方，用于验证交易完整性

代码中的核心数据结构是 `MerkleTree[+A]` trait，它提供了 `blind()` 方法实现子树致盲，和 `unwrap` 方法返回 `Either[RootHash, A]`（`Left` = 已致盲只有哈希，`Right` = 完整内容），迫使调用方在代码层面处理"这部分可能对我不可见"的情况。

#### 3.3.5 Informees 的确定规则

每个 action 的 informee（知情方）由合约角色决定，规则如下：

| Action 类型 | Informees |
|-------------|-----------|
| **Create** | Signatories + Contract Observers |
| **Consuming Exercise** | Signatories + Observers + Actors + Choice Observers |
| **Non-consuming Exercise** | Signatories + Actors + Choice Observers（**不包含** Contract Observers） |
| **Fetch** | Signatories + Contract Observers |

一个重要的设计选择：Contract Observer **不会**被通知非消耗性 Exercise 和 Fetch——因为这些操作不改变合约状态。这种"最小通知原则"进一步减少了信息的不必要扩散。

#### 3.3.6 Divulgence 与 Disclosure：受控的信息扩散

在实际的多方交易中，有时候一个参与方需要看到它原本不是 informee 的合约内容。Canton 通过两种机制处理：

**Divulgence（被动泄露）**：当一个 Party 是某个 action 的 witness 但不是 informee 时，它可以看到该 action 后果中创建的合约。这是因为 Daml 的确定性执行——如果一个 Party 知道 action 的输入，它可以自己计算出所有后果，隐藏结果没有意义。但 Divulgence **不自动授予后续使用权**——被泄露的合约只是可见的，不能在后续交易中直接使用。

**Disclosure（主动披露）**：通过 `submitWithDisclosures` 显式授权第三方查看和使用合约。这是双边的——发送者知道合约的当前状态，接收者通过正式渠道获得使用权。

这两种机制的关键区别在于：Divulgence 是交易执行的被动副作用，只提供可见性不提供使用权；Disclosure 是主动的授权行为，同时授予可见性和使用权。设计 Disclosure 为显式操作而非隐式是有意为之——如果被泄露的合约自动授予使用权，非利益相关方可能看到合约被创建但看不到它何时被归档，导致基于过时状态的操作。

#### 3.3.7 为什么 Canton 选择了 Merkle DAG 投影而非 ZKP

这是理解 Canton 隐私哲学最关键的问题。零知识证明（ZKP）是当前密码学隐私的热门方案——它可以证明计算正确性而不揭示输入数据。为什么 Canton 没有选择 ZKP？

**核心差异在于隐私的哲学**：

| 维度 | Canton: Need-to-Know（需要知道才展示） | ZKP: Prove-Not-Reveal（证明但不展示） |
|------|--------------------------------------|--------------------------------------|
| **隐私粒度** | 子交易级（Merkle DAG 投影）| 交易级（整笔交易被隐藏/证明）|
| **隐私机制** | 加密路由 + 选择性分发 | 数学证明替代数据展示 |
| **可审计性** | 授权方可看到实际数据，审计轨迹完整 | 审计者只能验证证明，无法检查底层数据 |
| **故障模式** | 透明——攻击/错误会留下审计痕迹 | 不透明——攻击可能永远无法检测 |
| **计算开销** | 低-中（加密路由 + 2PC 协调）| 高（ZK 证明生成，尤其是通用 ZKP）|
| **灵活性** | 可以选择性地向不同方展示不同子集 | 证明电路固定，改变可见性需要重新设计电路 |
| **信任模型** | 信任 Participant 运营者和密码学协议 | 信任数学（电路设计、可信设置、实现） |

**Canton 选择 Merkle DAG 投影而非 ZKP 的三个根本原因**：

**原因一：企业场景需要"可审计的隐私"而非"绝对的隐私"。** 在受监管的金融市场中，监管者必须能够审计交易。Canton 的 need-to-know 模型允许将监管者添加为 Observer，直接查看实际交易数据——这在 ZKP 方案中几乎不可能实现（除非为每种审计需求设计专门的 ZK 电路）。更关键的是，如果系统被攻破，Canton 的审计轨迹可以证明发生了什么。Canton 官方博客引用了一个关于 ZKP 的关键洞察：**"当 ZKP 失败时，它们会无声地失败——你无法区分正常运行和已被攻破的系统。一次未被发现的漏洞利用可以永久地污染账本，且无法验证完整性。"**

**原因二：子交易级粒度是 ZKP 的结构性盲区。** ZKP 证明的是"整笔交易是有效的"，但不提供"向不同参与方展示交易的不同部分"的能力。要在 ZKP 框架下实现 Canton 的差异化投影（Bank 只看到资金、Registrar 只看到股权），需要为每一种参与方角色设计不同的 ZK 电路——这在多方复杂交易中的组合爆炸使其不可行。Canton 的 Merkle DAG 投影是结构性的——投影算法自动适应任意的交易树结构和参与方配置，无需预定义。

**原因三：确定性执行使投影成为可能。** Canton 投影机制的一个前提是 Daml 的确定性执行——相同输入必然产生相同输出。这意味着每个 Participant 可以独立验证自己可见的子树，无需看到完整交易。如果执行不确定（如依赖 block.timestamp 或外部 oracle），不同 Participant 可能计算出不同的结果，投影验证就会失败。这是 Daml 的限制（无随机性、无外部数据访问）不是疏忽而是隐私保证的必要条件。

#### 3.3.8 已知的隐私局限性

Canton 的隐私模型并非无懈可击：

1. **元数据泄露**：Sequencer 虽然看不到交易内容，但可以观察到通信模式——消息大小、发送频率、接收方列表。在某些场景下，元数据本身就包含有价值的信息（例如两个机构突然开始高频通信可能暗示即将发生的交易）。代码分析确认 Sequencer 可见的信息包括：sender member ID、每个 envelope 的收件人列表（`Recipients`）、消息大小、maxSequencingTime、submissionCost 等。完全消除元数据泄露需要混淆网络（如 Tor），Canton 在此做出了务实的权衡——在企业联盟场景中，Synchronizer 通常由受信任的运营商运营，元数据泄露被认为是可接受的风险。

2. **非数学保证**：Canton 的隐私建立在加密和协议设计之上，而非数学证明（如 ZKP）。如果 Participant 运营者恶意泄露数据，协议层面没有防护——这依赖于法律合同和信任关系。

3. **无全局查询**：由于不存在全局状态，"网络上总共有多少 Token？"这样的查询在协议层面不可能实现，必须通过应用层数据聚合解决。

#### 3.3.9 隐私方案横向对比

| 维度 | Canton Sub-transaction Privacy | Fabric Channels + PDC | ZK/Confidential Transactions | Public L2 + 链下隐私 |
|------|------|------|------|------|
| **隐私粒度** | 子交易级（action 级别）| Channel 级别（粗粒度）+ PDC 可做字段级别 | 交易级别（ZKP 证明整笔交易有效性）| 无链上隐私 |
| **验证者可见性** | Sequencer/Mediator 看不到交易内容 | Orderer 看不到 PDC 数据；但 Channel 内节点看到全部 | 验证者仅验证证明，不看交易细节 | 验证者看到全部 calldata |
| **合规审计** | 完整审计轨迹（添加 Observer 即可）| Channel 成员有完整账本；PDC 需显式分享 | ZKP 失败时不可见；需额外审计电路 | 链上数据公开可审计 |
| **GDPR 合规** | 原生支持（各方只存自己数据，可删除）| Channel 内全复制；PDC 可设 TTL | ZK 证明可能包含不可删除的链上锚点 | 链上数据不可变 |
| **性能开销** | 中等（2PC + Merkle 构建）| 低（Channel 隔离低开销）| 高（ZKP 生成高计算成本）| 无隐私开销 |
| **适用场景** | 多方复杂交易（DvP、供应链金融）| 多组织联盟（已知成员）| 公链上的隐私 DeFi | 通用 DeFi、NFT |

**关键结论**：Canton 的隐私在**多方复杂交易**场景中最有优势——它是唯一一个能在单笔交易中给不同参与方展示不同数据切片的方案。这些隐私方案并非互斥：Polyglot Canton 白皮书已探索了在 Canton 上支持 ZKP 的可能性，未来可能实现两种模型的互补。
