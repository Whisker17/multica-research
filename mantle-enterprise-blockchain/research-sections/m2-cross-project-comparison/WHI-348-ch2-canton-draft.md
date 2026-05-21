# 第二章：Canton（Digital Asset）技术深度分析

> **报告编号**：WHI-348 | **章节**：Chapter 2 | **草稿版本**：v0.1  
> **撰写日期**：2026-05-06 | **字数统计**：约 4,200 字（正文）

---

## 2.1 项目概述与市场定位

Canton 是由 Digital Asset 公司研发的隐私优先（privacy-first）分布式账本协议，自 2014 年起历经多年演进，现已作为独立开源项目移交至 Linux Foundation 旗下，并在 **Global Synchronizer Foundation（GSF）** 的治理框架下持续发展 [WHI-334 §overview]。

与绝大多数企业区块链方案不同，Canton 从设计之初便将**隐私性**而非吞吐量置于核心约束条件，其本质诉求来自于资本市场的现实需求——全球银行、资产管理公司和清算机构在同一网络上协作时，必须确保彼此的持仓信息、交易细节不被其他参与方（包括基础设施运营商）所窥探。

**市场定位一览**

| 维度 | Canton 的立场 |
|------|--------------|
| 目标行业 | 资本市场、托管银行、跨企业资产结算 |
| 核心差异化 | Sub-transaction 级别的原生隐私保护 |
| 开源治理 | Linux Foundation / GSF |
| 智能合约语言 | Daml（Digital Asset Modeling Language） |
| 生产网络规模 | 450+ 参与方；单月处理能力超 $2T [WHI-334 §network] |
| 代表参与机构 | Goldman Sachs、HSBC、DTCC 等 |

Canton 既非以太坊的企业改造版，也非 Hyperledger Fabric 的竞争者——它更接近于一套**分布式协调协议**，底层状态机由 Daml 智能合约语言定义，网络层则由称为 Synchronizer 的协调基础设施负责排序与确认。这一架构选择决定了其适用场景的边界：擅长处理多方合约执行与资产转移，但不适合作为单企业内部的简单数据共享账本。

---

## 2.2 核心架构：Participant-Domain 模型

Canton 的架构被设计为两类角色的清晰分离，官方文档将其概括为 **Participant-Synchronizer（参与者-同步器）**模型 [WHI-335 §architecture]。

### 2.2.1 参与者节点（Participant Node）

Participant 节点是企业在 Canton 网络中的代理，承担以下职责：

- **本地状态管理**：维护本节点所见的 **Active Contract Set（ACS，活跃合约集）**。Canton 中不存在任何节点持有完整全局状态，每个 Participant 只持有与其 Party 相关的合约子集 [WHI-335 §virtual-ledger]。
- **Daml 引擎执行**：Participant 内嵌 Daml 解释器，负责本地合约语义验证与执行。
- **交易提交**：Participant 构造 Transaction 并提交给 Synchronizer，提交前需按 Merkle DAG 结构对视图（View）进行加密处理。

### 2.2.2 同步器节点（Synchronizer / Domain）

Synchronizer 由两个功能组件构成：

**Sequencer（排序器）**

Sequencer 在 Canton 隐私模型中扮演了一个极具巧思的角色——它负责提供**有序的加密消息流**，但自身不解密任何内容 [WHI-334 §sequencer]。其具体功能包括：

- 按时间戳为消息分配全局顺序
- 向目标接收方（recipient list）路由加密 blob
- 提供 DDoS 防护与速率限制

值得注意的是，Sequencer 看到的仅仅是加密 blob、接收方列表和时间戳三元组，这一设计从架构层面消除了 Sequencer 运营商实施 **MEV（Miner/Maximal Extractable Value）** 的可能性 [WHI-343 §mev]。

**Mediator（协调器）**

Mediator 负责协调 **Two-Phase Commit（2PC，两阶段提交）**流程：

- 收集各 Confirmer（确认方）的 APPROVE / REJECT 信号
- 对超时情况执行 REJECT 判决
- 支持 Threshold Voting 机制，可配置为去中心化仲裁委员会 [WHI-334 §mediator]

Mediator 同样不接触合约明文数据——它只看到确认/拒绝信号，对合约内容一无所知。

### 2.2.3 架构关系图

```
┌─────────────────────────────────────────────────────────────┐
│                     Canton Network                          │
│                                                             │
│  ┌──────────────┐         ┌──────────────────────────────┐  │
│  │ Participant A│◄───────►│       Synchronizer           │  │
│  │  (Bank A)    │         │  ┌────────────┐ ┌──────────┐ │  │
│  │  - ACS(A)    │         │  │  Sequencer │ │ Mediator │ │  │
│  │  - Daml Eng  │         │  │ (加密路由) │ │ (2PC协调)│ │  │
│  └──────────────┘         │  └────────────┘ └──────────┘ │  │
│                           └──────────────────────────────┘  │
│  ┌──────────────┐                    ▲                       │
│  │ Participant B│◄───────────────────┘                       │
│  │  (Bank B)    │                                            │
│  │  - ACS(B)    │                                            │
│  │  - Daml Eng  │                                            │
│  └──────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```

### 2.2.4 Party 模型与权限体系

Canton 使用 **Party（当事方）** 作为法律实体的网络表示，其唯一标识符格式为 [WHI-334 §party-model]：

```
UID = identifier::namespace
```

其中 `namespace` 由节点的自签名根证书（self-signed root certificate）派生，与 X.509/PKI 体系集成 [WHI-344 §identity]。

Party 与 Participant 之间存在**多对多映射**关系，同一 Party 可托管（host）于多个 Participant 节点（multi-hosting），从而支持冗余部署和机构间的共同托管场景。

Canton 定义了三级权限层次：

| 权限级别 | 角色说明 | 对应 Daml 概念 |
|---------|---------|--------------|
| Submission（提交权） | 可发起交易提交 | — |
| Confirmation（确认权） | 作为 Confirmer 参与 2PC | Signatory |
| Observation（观察权） | 只读可见性 | Observer |

---

## 2.3 隐私模型：Sub-transaction Privacy

Canton 最具技术深度的设计是其**子交易级别隐私（Sub-transaction Privacy）**机制，这在同类企业区块链方案中属于粒度最细的隐私保护方案 [WHI-343 §privacy-granularity]。

### 2.3.1 Merkle DAG 投影机制

Canton 不将整个交易广播给所有参与方，而是将交易树（Transaction Tree）分解为若干 **View（视图）**，构成一棵 **Merkle DAG** 结构 [WHI-335 §merkle-dag]。每个参与方仅接收与其 Party 相关的子树投影（Projection）。

这一投影算法具备一个关键的数学性质——**吸收性（Absorbing Property）**：子集投影必然包含于超集投影之中 [WHI-335 §absorbing-property]。这意味着任何参与方都无法通过拼合多个局部视图来重建他本不该看到的内容，因为局部视图本身就是更大视图的数学子集。

从代码层面看，这一机制在 `GenTransactionTree` 结构中体现为 [WHI-336 §codebase]：

```scala
// WHI-336: 核心 Merkle 树数据结构
trait MerkleTree[+A] {
  def blind(): MerkleTree[A]  // 节点致盲方法
  // ...
}

// GenTransactionTree 包含以下层次：
// - CommonMetadata     (共同元数据，各方可见)
// - ParticipantMetadata (参与者元数据，仅相关参与者可见)
// - SubmitterMetadata  (提交者元数据，仅提交方可见)
// - Views             (交易视图树，按接收方加密分发)
```

`blind()` 方法将不相关的子树节点替换为其哈希摘要，使接收方可以验证整个树的完整性（通过根哈希），同时无法读取已致盲节点的内容。

### 2.3.2 加密传输：EncryptedViewMessage

在消息传输层，每个 View 被封装进 `EncryptedViewMessage`，使用对称密钥加密，密钥仅分发给合法接收方 [WHI-336 §encrypted-view]：

```scala
// 概念示意（简化自 WHI-336 分析）
case class EncryptedViewMessage(
  encryptedView: Encrypted[SerializedView],
  sessionKey: Map[ParticipantId, AsymmetricEncrypted[SessionKey]],
  viewHash: Hash,
  // ...
)
```

Sequencer 在路由此消息时，仅看到外层结构中的接收方列表，无法解密内部 View 内容。

### 2.3.3 Divulgence 与 Disclosure 机制

Canton 支持两种受控信息共享机制 [WHI-335 §divulgence]：

- **Divulgence（溢出披露）**：合约创建时不可见的一方，通过后续交易中的关联引用而"被动"获得合约可见性。常见于"witness"类合约场景。
- **Disclosure（主动披露）**：合约所有方主动将合约内容分享给指定第三方，典型场景为监管报告或审计。

### 2.3.4 已知隐私局限性

需要客观指出，Canton 的隐私模型并非无懈可击 [WHI-335 §tradeoffs]：

1. **元数据泄露**：Sequencer 虽看不到消息内容，但能观察到消息大小、发送频率和接收方列表的模式，具备一定的流量分析潜力。
2. **无 ZK 证明**：Canton 采用"加密路由 + Merkle 哈希"方案，而非零知识证明（Zero-Knowledge Proof）。其密码学复杂度评级为低-中（Low-Medium）[WHI-343 §crypto-complexity]，隐私保证强度低于基于 ZK-SNARK 的方案。
3. **无全局查询能力**：由于不存在全局状态，跨参与方的聚合查询在协议层面不可能实现，必须通过应用层数据仓库解决。

---

## 2.4 共识机制与最终性

### 2.4.1 Two-Phase Commit（2PC）执行流程

Canton 的共识机制本质上是**2PC + BFT 混合**架构，在设计哲学上更接近分布式数据库的事务协调，而非传统区块链共识 [WHI-345 §consensus]。完整流程如下：

1. **Phase 1 – Prepare（准备阶段）**
   - Submitter（提交者）的 Participant 节点构造 Transaction，生成 Merkle DAG 视图树
   - 各 View 按接收方加密，封装为 `EncryptedViewMessage`
   - 提交至 Sequencer，Sequencer 分配全局时间戳并路由至各 Confirmer

2. **Phase 2 – Commit/Abort（提交/中止阶段）**
   - 各 Confirmer Participant 解密其 View，执行本地合约验证
   - 向 Mediator 发送 APPROVE 或 REJECT 信号
   - Mediator 执行判决逻辑：**所有 Confirmer 同意 → APPROVE；任一方拒绝或超时 → REJECT**
   - Mediator 将最终结果广播，各 Participant 更新本地 ACS

从代码实现角度，`ConfirmationRequestAndResponseProcessor` 在 Mediator 端实现了上述 2PC 协调逻辑，而 `ResponseAggregation` 则负责基于 Quorum 机制的票数聚合 [WHI-336 §mediator-code]。

### 2.4.2 为什么说 Canton 更像数据库而非区块链？

WHI-335 从五个维度论证了这一观点 [WHI-335 §2pc-vs-blockchain]：

| 维度 | 传统区块链共识 | Canton 2PC |
|------|--------------|-----------|
| 参与方假设 | 拜占庭容错（恶意节点） | 理性参与者（博弈论诚实） |
| 状态存储 | 全节点复制全量数据 | 各 Participant 仅存本地 ACS |
| 最终性机制 | 概率最终性或 BFT 投票 | 确定性即时最终性 |
| 吞吐量瓶颈 | 全网广播 | 点对点 View 分发 |
| 故障恢复 | 链式重放 | Sequencer 消息重放 |

### 2.4.3 最终性特征

Canton 的最终性具有以下特征 [WHI-345 §finality]：

- **确定性（Deterministic）**：2PC 结果无歧义，无需等待多个区块确认
- **即时性（Near-Instant）**：典型确认延迟为秒级
- **局部性（Local Finality）**：最终性仅在参与该交易的 Participant 节点之间成立，不存在"全网确认"的概念

关于信任假设，Canton 的安全模型依赖于**Synchronizer 运营商的诚实性**（Protocol Trust），而非密码学证明的无需信任安全。这是其与公链最本质的设计哲学差异 [WHI-345 §trust-model]。

### 2.4.4 数据可用性（Data Availability）

Canton 对 DA 的处理方式代表了一种极端的数据最小化策略 [WHI-345 §da]：

- 不存在需要全局可用的数据集
- 每个 Participant 自主存储其 ACS，可独立进行 GDPR 合规删除
- Sequencer 的消息历史（Message History）是唯一的共享可审计轨迹，但仅包含加密 blob

这一设计使 Canton 成为目前隐私设计最彻底的企业账本方案之一，同时也意味着系统层面的"全局审计"需要特别的架构设计才能实现。

---

## 2.5 Daml 智能合约语言

### 2.5.1 语言设计哲学

**Daml（Digital Asset Modeling Language）** 是一门专为多方合约设计的函数式领域特定语言（DSL），其核心设计目标是将法律合同语义精确映射为可执行代码。与 Solidity 面向"状态变更"的命令式风格不同，Daml 以**合约模板（Contract Template）**为核心抽象，天然对齐资本市场的金融合约概念 [WHI-344 §daml]。

### 2.5.2 授权模型：编译时安全

Daml 的访问控制是**编译时强制执行（Compile-time Enforcement）**的，而非运行时检查 [WHI-344 §daml-auth]。合约模板中每个字段和操作都必须明确声明权限归属：

```daml
-- Daml 合约模板示例（债券结算场景）
template BondTransfer
  with
    seller: Party      -- 卖方
    buyer: Party       -- 买方
    bondId: Text
    amount: Decimal
  where
    signatory seller   -- seller 是签署方（必须同意）
    observer buyer     -- buyer 是观察方（可见但不强制）
    
    choice Accept : ContractId BondTransfer
      controller buyer  -- 只有 buyer 可以执行此选择
      do
        -- 执行结算逻辑
        return self
        
    choice Reject : ()
      controller buyer
      do
        return ()
```

三个关键角色的含义如下 [WHI-344 §daml-roles]：

| 角色 | Daml 关键字 | 语义 |
|-----|-----------|-----|
| 签署方 | `signatory` | 合约必须经该方明确授权才能创建/存档 |
| 观察方 | `observer` | 可见合约内容，但无法触发操作 |
| 控制方 | `controller` | 可以执行特定 Choice（操作选项） |

这一设计使得越权操作在编译时即被捕获，从根本上消除了一类常见的智能合约漏洞——未授权的状态修改。

### 2.5.3 与 Canton 协议的集成

Daml 引擎通过 `CommandProgressTracker` 接口集成到 Canton Participant 节点中 [WHI-336 §daml-integration]。执行路径大致为：

```
应用层 API 调用
      ↓
CommandProgressTracker（跟踪命令执行状态）
      ↓
Daml 解释器（本地语义验证）
      ↓
Transaction 构造（生成 Merkle DAG 视图树）
      ↓
提交至 Synchronizer
```

### 2.5.4 可移植性与多账本能力

Daml 的一个重要特性是其**运行时无关性（Runtime Agnosticism）**：同一份 Daml 合约代码可以在 Canton、Hyperledger Fabric（通过 Daml on Fabric）、VMware Blockchain 等不同底层基础设施上运行。这为企业提供了一定程度的账本无关合约开发能力，降低了对特定基础设施的锁定风险。

---

## 2.6 企业级特性评估

### 2.6.1 综合评估矩阵

| 特性维度 | 评分（1-5） | 评估说明 |
|---------|-----------|---------|
| **隐私保护** | ⭐⭐⭐⭐⭐ | Sub-transaction 级别，同类最优；Sequencer 无法解密内容 |
| **最终性确定性** | ⭐⭐⭐⭐⭐ | 确定性即时最终性，无重组风险 |
| **身份与访问控制** | ⭐⭐⭐⭐ | PKI + Daml 编译时授权；Topology Transaction 密钥管理完善 |
| **吞吐量扩展性** | ⭐⭐⭐⭐ | 点对点 View 分发避免全网广播；Multi-Synchronizer 可水平扩展 |
| **智能合约安全性** | ⭐⭐⭐⭐⭐ | Daml 编译时授权检查；强类型函数式语言 |
| **互操作性** | ⭐⭐⭐ | 跨 Synchronizer 需 Reassignment（非原子）；非 EVM 生态 |
| **监管合规** | ⭐⭐⭐⭐⭐ | GDPR 原生兼容；数据主权清晰；支持 Disclosure 审计机制 |
| **开发者生态** | ⭐⭐ | Daml 学习曲线陡峭；非 Web3 主流生态；工具链较封闭 |
| **运维复杂度** | ⭐⭐ | 多组件部署（Participant + Synchronizer）；Topology 管理复杂 |
| **去中心化程度** | ⭐⭐ | 依赖 Synchronizer 运营商诚实；非无需信任架构 |

### 2.6.2 GDPR 与数据主权合规

Canton 是目前企业账本中对 GDPR 合规支持最为原生的方案 [WHI-345 §gdpr]：

- **数据最小化**：各参与方仅存储与己相关的合约数据
- **被遗忘权**：每个 Participant 可独立删除本地 ACS 中的数据，不影响网络其他节点
- **数据境内化**：Party 与 Participant 的灵活映射支持数据主权管辖区约束

### 2.6.3 密钥管理与 Topology Transaction

Canton 采用 **Topology Transaction** 机制处理密钥轮换和权限变更 [WHI-344 §topology]：

- 每次密钥更新操作均有序列号（Sequence Number）防重放
- REMOVE 操作（删除密钥/权限）支持多方签名授权
- Topology Transaction 通过 Sequencer 有序广播，确保全网视图一致性

---

## 2.7 代码实现亮点

本节聚焦于 Canton 开源代码库中若干值得关注的实现细节，技术依据来源于 WHI-336 的代码分析报告。

### 2.7.1 技术栈特征

Canton 代码库以 Scala 为主（占比约 96%），使用 sbt 构建系统 [WHI-336 §tech-stack]。Scala 的函数式编程特性与类型安全机制与 Canton 的设计哲学高度契合：

- 不可变数据结构保证合约状态的确定性
- 代数数据类型（ADT）精确建模协议状态机
- 强类型系统在编译时捕获协议层错误

### 2.7.2 MerkleTree 的核心实现

`MerkleTree[+A]` trait 是整个隐私机制的核心数据结构 [WHI-336 §merkle-impl]：

```scala
// 简化示意——来源 WHI-336 分析
trait MerkleTree[+A] {
  // 将当前节点致盲（blinded），仅保留哈希
  def blind(): MerkleTree[A]
  
  // 获取节点哈希（用于完整性验证）
  def rootHash: RootHash
  
  // 判断节点是否已被致盲
  def isBlinded: Boolean
}

// GenTransactionTree 组织全部 Merkle 节点
case class GenTransactionTree(
  submitterMetadata: MerkleTree[SubmitterMetadata],
  commonMetadata: MerkleTree[CommonMetadata],
  participantMetadata: MerkleTree[ParticipantMetadata],
  rootViews: MerkleSeq[TransactionView]
)
```

`blind()` 方法的设计实现了一个优雅的属性：接收方可以通过根哈希验证整棵树未被篡改，即便树中大量节点已被致盲；同时，致盲节点的内容不可逆推导，确保了隐私边界。

### 2.7.3 Sequencer 驱动接口

`SequencerDriver` trait 定义了 Sequencer 底层实现的抽象接口 [WHI-336 §sequencer-driver]：

```scala
// 概念接口（简化自 WHI-336 分析）
trait SequencerDriver {
  // 向 Sequencer 提交消息
  def send(submission: SubmissionRequest): Future[SendResult]
  
  // 订阅消息流（按序接收）
  def subscribe(request: SubscriptionRequest): Source[SequencedEvent, _]
  
  // 确认已处理至某序列号
  def acknowledge(member: Member, timestamp: CantonTimestamp): Future[Unit]
}
```

**值得关注的文档与代码差异**：WHI-336 的分析指出，官方文档中提及了 **BFT Sequencer** 的存在（基于 BFT 共识协议的高可用排序器），但开源代码库中目前仅提供了**基于关系数据库的参考实现（DB-backed Reference Driver）** [WHI-336 §doc-code-gap]。这意味着：

1. 开源部署的 Sequencer 故障容错能力取决于底层数据库的高可用方案
2. BFT Sequencer 可能存在于 Digital Asset 商业版本或未来开源路线图中
3. 企业生产部署前需评估此单点风险

### 2.7.4 Mediator 的 2PC 实现

`ConfirmationRequestAndResponseProcessor` 实现了 Mediator 端的核心 2PC 协调逻辑，而 `ResponseAggregation` 基于 **Quorum 机制**进行票数聚合 [WHI-336 §mediator-code]——这为配置去中心化 Mediator（门限投票委员会）提供了代码层支撑。

```scala
// ResponseAggregation 概念示意
class ResponseAggregation {
  // 聚合各 Confirmer 的响应
  def addResponse(response: ConfirmationResponse): AggregationResult
  
  // 判断是否已达到 Quorum（满足阈值投票）
  def isQuorumReached: Boolean
  
  // 超时时触发 REJECT 判决
  def timeout(): Unit
}
```

---

## 2.8 优势、局限性与适用场景

### 2.8.1 核心优势

**1. 行业最优的原生隐私保护**

Canton 的 Sub-transaction Privacy 是当前企业账本方案中粒度最细的隐私机制 [WHI-343 §comparison]。对于监管严格的金融机构，这意味着可以在同一网络与竞争对手合作，而无需担忧持仓或交易策略泄露。

**2. 与资本市场语义天然契合的 Daml**

Daml 的合约模板直接映射金融合约的法律语义（义务、权利、选择权），极大降低了将法律文本转化为可执行代码时的语义漂移风险。

**3. 确定性即时最终性**

相较于概率性最终性（如 PoW 链）或需多轮投票的 BFT 方案，Canton 的 2PC 提供了确定性的交易结果，这对于 T+0 结算场景至关重要。

**4. GDPR 原生合规**

数据主权与被遗忘权在协议层面原生支持，无需通过应用层补丁实现，显著降低合规成本。

**5. 成熟的机构级生态**

Goldman Sachs、HSBC、DTCC 等顶级金融机构的参与验证了方案的可行性，$2T+/月的处理量提供了生产级规模参考 [WHI-334 §network]。

### 2.8.2 主要局限性

**1. 信任假设较强**

Canton 的安全性依赖于 Synchronizer 运营商的诚实性，这与公链的无需信任（Trustless）哲学存在本质差异 [WHI-345 §trust-limitations]。如果 Synchronizer 运营商被攻破或主动作恶，协议层面没有密码学保障。

**2. 缺乏全局状态与查询能力**

"虚拟全局账本"设计虽然保护了隐私，但也意味着协议层面不可能执行跨参与方的聚合查询。Analytics 和 Reporting 需要独立的链下数据仓库架构。

**3. 跨 Synchronizer 交易非原子性**

Multi-Synchronizer 场景下的 **Reassignment** 操作是**非原子的（Non-atomic）** [WHI-335 §multi-synchronizer]，跨域资产转移存在中间状态窗口，需要应用层设计补偿机制。

**4. Daml 生态相对封闭**

Daml 虽然功能强大，但学习曲线陡峭，与主流 Web3 开发生态（EVM、Solidity）完全不兼容，难以复用现有以太坊生态的工具链和人才。

**5. BFT Sequencer 开源缺失**

如前文代码分析所述，开源版本仅提供 DB-backed 参考实现的 Sequencer，生产级 BFT 容错能力的获取路径尚不清晰 [WHI-336 §doc-code-gap]。

**6. 运维复杂度高**

Participant + Synchronizer（Sequencer + Mediator）的多组件架构，叠加复杂的 Topology Transaction 管理，使得初期部署和日常运维门槛远高于单链方案。

### 2.8.3 适用场景评估

**高度适合的场景** [WHI-343 §use-cases]：

| 场景 | 适合原因 |
|------|---------|
| 银行间债券/衍生品结算 | 隐私保护 + 确定性最终性 + Daml 金融语义 |
| 供应链金融（多银行联合） | 多方合约 + Need-to-Know 隐私 |
| 跨企业资产通证化发行 | Party 多托管 + 原生访问控制 |
| 监管报告与审计（选择性披露） | Disclosure 机制 + GDPR 合规 |
| DTCC 级别机构清算网络 | 高吞吐 + 机构级信任假设可接受 |

**不适合的场景**：

| 场景 | 不适合原因 |
|------|-----------|
| 企业内部单链账本 | 架构过度复杂，单节点 DB 更高效 |
| 稳定币支付网络 | 非 EVM，无支付优化，生态不兼容 |
| 公开可验证的公链应用 | 非无需信任架构，Sequencer 信任依赖 |
| 需要全局聚合分析的业务 | 无全局状态，Analytics 成本高 |

---

## 本章小结

Canton 代表了企业级分布式账本在**隐私优先**路线上走得最远的方案。其 Sub-transaction Privacy、Daml 编译时授权、以及协议层 GDPR 合规，构成了一套在资本市场场景下难以替代的技术组合。然而，Synchronizer 运营商信任假设、跨域非原子性、Daml 生态封闭以及运维复杂度，限制了其适用场景的边界。

对于正在评估企业账本基础设施的机构而言，Canton 最适合的投资回报比场景是：**多家竞争性金融机构之间存在强隐私约束、且需要高频次确定性结算的协作网络**。在此场景之外，其架构复杂度带来的成本可能超过其隐私收益。

---

*本章引用来源：WHI-334（Canton 文档研究）、WHI-335（Canton 架构分析）、WHI-336（Canton 代码库分析）、WHI-343（隐私对比分析）、WHI-344（访问控制对比分析）、WHI-345（共识与数据可用性对比分析）*

*下一章：Chapter 3 — Hyperledger Fabric（Linux Foundation）技术深度分析*
