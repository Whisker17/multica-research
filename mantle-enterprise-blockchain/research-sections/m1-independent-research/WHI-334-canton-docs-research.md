# WHI-334: Canton 官方文档与白皮书调研

> **Issue**: WHI-334 — Canton 官方文档与白皮书调研
> **Milestone**: M1: 各项目独立深度调研
> **Date**: 2026-05-07
> **Status**: Done（Revision 2 — GPT review 通过）

---

## 1. Canton 项目概述

Canton 是由 Digital Asset 开发的企业级分布式账本协议，其核心创新在于 **子交易级隐私 (sub-transaction privacy)** 和 **Daml 智能合约语言**。与传统区块链（如 Ethereum）不同，Canton 没有全局共享账本——每个参与方只能看到自己有权限看到的数据切片（need-to-know 原则）。Canton 通过将全局状态分区（state partitioning），在 Synchronizer（原称 Domain）上协调交易，同时保证 GDPR 合规性和可审计性。2024 年启动的 Canton Network 是一个公共许可网络（public permissioned network），根据 Canton 生态目录（cantonecosystem.com）列出 450+ projects/apps/validators，Global Synchronizer 页面声称每月代币化超过 $2T 的真实世界资产（[来源: canton.network/global-synchronizer](https://canton.network/global-synchronizer)，截至 2026 年 5 月访问）。Digital Asset 官方 tokenization 用例页面则引用 $1.5T+/月的数据（[来源: digitalasset.com/use-cases/tokenization](https://www.digitalasset.com/use-cases/tokenization)）——两个数字存在差异，可能反映不同统计口径或时间窗口。主要参与机构包括 Goldman Sachs（GS DAP™）、HSBC（Orion）、BNY Mellon、DTCC、Citi、Nasdaq 等（详见 §7.4）。Canton 代码库以 Scala 为主（96%），采用 Apache-2.0 开源许可，GitHub 仓库有 114 stars，最新版本 v3.5.1-rc3（2026年4月）。

---

## 2. 核心架构

### 2.1 架构概览图

```
                          ┌─────────────────────────────────────────────┐
                          │          Canton Network (Layer 2)           │
                          │                                             │
                          │   ┌──────────────────────────────────────┐  │
                          │   │      Global Synchronizer (GSF)       │  │
                          │   │  BFT Consensus · Super Validators    │  │
                          │   │  Canton Coin · Cross-Domain Interop   │  │
                          │   └──────────────────────────────────────┘  │
                          │          ▲              ▲           ▲       │
                          │          │              │           │       │
                ┌─────────┼──────────┼──────────────┼───────────┼───┐  │
                │         │          │              │           │   │  │
    ┌───────────┼─────┐   │  ┌───────┼──────┐  ┌───┼───────┐   │  │  │
    │ Synchronizer A  │   │  │ Synchro. B   │  │ Synchro. C│   │  │  │
    │ ┌─────────────┐ │   │  │              │  │           │   │  │  │
    │ │ Sequencer(s)│ │   │  │ Sequencer(s) │  │Sequencer  │   │  │  │
    │ │  - Ordering │ │   │  │              │  │           │   │  │  │
    │ │  - Multicast│ │   │  │  Mediator(s) │  │ Mediator  │   │  │  │
    │ │  - Privacy  │ │   │  │              │  │           │   │  │  │
    │ ├─────────────┤ │   │  └──────────────┘  └───────────┘   │  │  │
    │ │ Mediator(s) │ │   │                                     │  │  │
    │ │  - 2PC      │ │   │                                     │  │  │
    │ │  - Verdicts │ │   │                                     │  │  │
    │ └─────────────┘ │   │                                     │  │  │
    └────────┬────────┘   │                                     │  │  │
             │            │                                     │  │  │
    ─────────┼────────────┼─────────────────────────────────────┼──┘  │
             │            │                                     │     │
   ┌─────────┴──────┐  ┌─┴────────────┐  ┌────────────────┐   │     │
   │ Participant P1 │  │Participant P2│  │ Participant P3  │   │     │
   │                │  │              │  │                 │   │     │
   │  Party: Alice  │  │ Party: Bob   │  │  Party: Bank   │   │     │
   │  Party: Carol  │  │ Party: SR    │  │                │   │     │
   │                │  │              │  │                 │   │     │
   │  ┌──────────┐  │  │ ┌──────────┐│  │  ┌──────────┐  │   │     │
   │  │Daml      │  │  │ │Daml      ││  │  │Daml      │  │   │     │
   │  │Engine    │  │  │ │Engine    ││  │  │Engine    │  │   │     │
   │  ├──────────┤  │  │ ├──────────┤│  │  ├──────────┤  │   │     │
   │  │Active    │  │  │ │Active    ││  │  │Active    │  │   │     │
   │  │Contract  │  │  │ │Contract  ││  │  │Contract  │  │   │     │
   │  │Set (ACS) │  │  │ │Set (ACS) ││  │  │Set (ACS) │  │   │     │
   │  ├──────────┤  │  │ ├──────────┤│  │  ├──────────┤  │   │     │
   │  │PostgreSQL│  │  │ │PostgreSQL││  │  │PostgreSQL│  │   │     │
   │  └──────────┘  │  │ └──────────┘│  │  └──────────┘  │   │     │
   └────────────────┘  └─────────────┘  └────────────────┘   │     │
                                                              │     │
                          └───────────────────────────────────┘     │
                          └─────────────────────────────────────────┘

      ┌─────────────────────────────────────────────────────────┐
      │                   Application Layer                     │
      │  ┌──────────────────┐  ┌─────────────────────────────┐  │
      │  │   gRPC Ledger    │  │   HTTP JSON API Service     │  │
      │  │   API (v1/v2)    │  │   (REST bridge → gRPC)      │  │
      │  └──────────────────┘  └─────────────────────────────┘  │
      │  ┌──────────────────────────────────────────────────┐   │
      │  │  Daml Finance Library (bonds, equity, swaps...)  │   │
      │  └──────────────────────────────────────────────────┘   │
      └─────────────────────────────────────────────────────────┘
```

### 2.2 核心组件关系

Canton 的架构由三层组成：

1. **Participant 层**：运行 Daml 引擎，维护 Active Contract Set (ACS)，代表 Party 参与交易
2. **Synchronizer 层**（原称 Domain）：由 Sequencer + Mediator 组成，提供消息排序、交易协调和隐私路由
3. **Canton Network 层**：通过 Global Synchronizer 提供跨应用/跨子网互操作与原子智能合约调用能力；底层跨 Synchronizer Reassignment 仍为非原子流程（见 §3.7.2 / §4.6）

**关键设计原则**：Participant 和 Mediator 之间**不直接通信**，所有消息都通过 Sequencer 路由。Sequencer 只看到加密后的消息元数据，无法读取交易内容。

### 2.3 术语边界澄清

Canton 生态中有多个容易混淆的术语，下表明确其边界：

| 术语 | 定义 | 部署单位 | 关系说明 |
|------|------|----------|----------|
| **Canton Protocol** | 分布式账本通信和共识协议规范 | — | 协议层，定义了 Participant/Synchronizer 间的交互规则 |
| **Canton Node** | 运行 Canton 协议的软件进程 | 单个进程/容器 | 可以是 Participant Node、Sequencer Node 或 Mediator Node |
| **Participant (Node)** | 承载 Party、运行 Daml 引擎、维护 ACS 的节点 | 单进程 + PostgreSQL | 一个 Participant 可承载多个 Party，也可同时连接多个 Synchronizer |
| **Party** | 法律实体或逻辑角色 | 逻辑概念 | 由 Participant Node 承载；可 multi-hosted 在多个 Participant 上 |
| **Synchronizer** (原 Domain) | 协调服务层 = Sequencer(s) + Mediator(s) | 一组节点的集合 | 提供消息排序和 2PC 协调；一个网络可有多个 Synchronizer |
| **Canton Network** | 公共许可网络，由 Global Synchronizer + 多个 Synchronizer + Participant 组成 | 整体网络 | 2024 年启动，由 Global Synchronizer Foundation 治理 |
| **Global Synchronizer** | Canton Network 中的特殊 Synchronizer，提供跨 Synchronizer 互操作 | 一组 Super Validator 节点 | BFT 共识，Canton Coin 经济模型 |

> **常见混淆**：
> - "Canton" 可指协议（Canton Protocol）、软件（Canton Node）或网络（Canton Network），需根据上下文判断。
> - "Synchronizer" 取代了 3.x 之前版本中的 "Domain" 术语，旧文档中仍可能使用 Domain。
> - "Participant" 是节点层概念，"Party" 是业务层概念，二者是多对多关系。

---

## 3. 关键概念详解

### 3.1 Participants（参与者节点）

**定义**：Participant Node 是 Canton 网络中承载 Party（参与方/法律实体）的节点，运行 Daml 引擎来执行智能合约逻辑。

**核心能力**：
- **Active Contract Set (ACS)**：维护该节点所承载 Party 可见的所有活跃合约集合，提供流式事件通知（创建、归档、行使）
- **交易历史**：存储并提供交易查询能力
- **交易确认**：在 2PC 协议中代表 Party 发送确认/拒绝响应（需要 Confirmation 权限）
- **交易提交**：向 Sequencer 提交新交易请求（需要 Submission 权限）

**权限模型（三级）**：
| 权限级别 | 能力 | 说明 |
|---------|------|------|
| **Observation** | 只读通知 | 仅接收 Party 相关交易的通知 |
| **Confirmation** | 参与 2PC | 可在两阶段提交中确认交易（包含 Observation） |
| **Submission** | 提交交易 | 可代表 Party 向网络提交新交易（包含 Confirmation） |

**Multi-hosting**：一个 Party 可以同时被多个 Participant Node 承载，实现分布式验证和高可用。对于去中心化 Party（threshold > 1），需要阈值数量的 Participant Node 达成一致才能确认交易。

**Local Party vs External Party**：
- **Local Party**：至少有 1 个 Submitting Participant Node (SPN)，密钥由 SPN 管理，适合自动化操作
- **External Party**：没有 SPN，自行控制签名密钥，每笔交易需要 Party 显式签名，适合需要独立控制的场景（如合规要求高的机构）

**存储后端**：每个 Participant Node 使用 PostgreSQL 数据库存储 ACS、交易历史和元数据。

### 3.2 Domains / Synchronizers（域/同步器）

**定义**：Synchronizer（3.x 版本中的术语，旧版称 Domain）是 Canton 的协调服务层，由 Sequencer 和 Mediator 两个子组件组成，负责交易的消息排序、隐私路由和共识协调。

**架构**：

```
Synchronizer = Sequencer(s) + Mediator(s) + Ordering Layer
```

**职责**：
- 为 Participant 之间的交易提供安全的消息传递通道
- 保证消息的全局一致性排序
- 协调两阶段提交 (2PC) 流程以确认交易
- 实施隐私路由——确保每个 Participant 只收到自己有权看到的消息

**Synchronizer 的独立性**：
- 每个 Synchronizer 可以有独立的治理、权限、性能配置和成本模型
- 不同的 Synchronizer 可以服务于不同的监管辖区、应用场景或性能要求
- Participant 可以同时连接多个 Synchronizer

**去中心化选项**：
- **所有权去中心化**：通过 DecentralizedNamespaceDefinition，Synchronizer 可由多方共同拥有（threshold > 1）
- **Mediator 去中心化**：多个 Mediator 基于阈值共识出具裁决
- **Sequencer 去中心化**：多个 Sequencer 运行在 BFT 排序层上
- **连接去中心化**：Participant 同时订阅多个 Sequencer，需要阈值数量达成一致

### 3.3 Sequencer（排序器）

**定义**：Sequencer 是 Synchronizer 的消息排序和分发组件，提供"带隐私保护的安全多播"（secure multicast with privacy）服务。

**核心功能**：
1. **消息排序**：为所有消息分配批次时间戳，确保所有接收者以相同的确定性顺序接收消息
2. **隐私路由**：每条消息指定明确的接收者列表，Sequencer 只将消息分发给指定接收者
3. **不透明转发**：Sequencer 转发的是加密后的 opaque 消息，无法读取交易内容
4. **发送者匿名**：接收者无法得知消息发送者的身份

**安全机制**：
- 认证服务端点（Authenticated endpoints）
- DDoS 防护（通过 Traffic Management）
- 确认请求速率限制
- 加密消息转发

**流量管理**：
- 提交请求的成本基于三个维度计算：存储成本（payload 大小）、网络成本（payload × 收件人数 × 缩放因子）、基础事件成本（固定开销）
- 成员随时间被动积累基础流量额度，也可通过 `SetTrafficPurchased` RPC 购买额外流量
- 两阶段执行：接收时初步检查 → BFT 排序后最终验证

**可插拔后端**：
Sequencer 的排序层支持多种后端实现：
- **Canton 原生**：内置 BFT 排序协议
- **Ethereum**：可以使用 Ethereum 链作为排序层后端
- **Hyperledger Fabric**：可以使用 Fabric 作为排序层后端
- **数据库驱动**：开发和测试场景中可使用数据库

### 3.4 Mediator（调解器）

**定义**：Mediator 是两阶段提交 (2PC) 协议的协调者，负责在不查看合约内容的情况下协调交易确认，最终出具"裁决"（verdict）以决定交易是提交还是回滚。

**工作流程（以 DvP 交易为例）**：

```
1. Alice 提交交易 → Sequencer
2. Sequencer 将加密的交易分片分发给相关 Participant
3. 各 Participant 验证自己可见的部分：
   - P1 (Alice): 验证 IOU 合约的行使
   - P2 (Bob): 验证 Share 合约的行使
   - P3 (Bank): 验证 IOU 的创建/归档
4. 各 Participant 发送确认/拒绝 → Sequencer → Mediator
5. Mediator 收集所有确认者的响应
6. 在 decision deadline 之前：
   - 如果所有 confirmer 都确认 → Mediator 出具 APPROVE verdict
   - 如果任何 confirmer 拒绝或超时 → Mediator 出具 REJECT verdict
7. Verdict 通过 Sequencer 分发给所有相关 Participant
8. 各 Participant 根据 verdict 更新各自的 ACS
```

**隐私保护**：
- Mediator **看不到**合约内容——它只接收加密的确认/拒绝信号
- 交易内容使用 Merkle DAG 结构，每个 Participant 只看到自己有权看到的子树
- Mediator 仅知道：哪些 Participant 需要确认、它们的确认/拒绝状态、decision deadline

**处理的协议类型**：
- **Daml 交易**：合约状态变更（创建、行使、归档）
- **重新分配 (Reassignment)**：跨 Synchronizer 的合约转移

**去中心化 Mediator**：可部署多个 Mediator 实例，通过阈值投票出具裁决。

### 3.5 Sub-transaction Privacy（子交易级隐私）

**定义**：Canton 的核心隐私创新——通过 Merkle DAG 结构实现交易的部分可见性。每个参与方只能看到交易中与自己相关的子集，而非整个交易。

**原理**：

Canton 的隐私模型基于以下层次：

#### 3.5.1 Informees（知情方）

每个 action 的 informee 由合约角色决定：

| Action 类型 | Informees |
|-------------|-----------|
| **Create** | Signatories + Contract Observers |
| **Consuming Exercise** | Signatories + Observers + Actors + Choice Observers |
| **Non-consuming Exercise** | Signatories + Actors + Choice Observers（**不包含** Contract Observers） |
| **Fetch** | Signatories + Contract Observers |

关键设计选择：Contract Observer 不会被通知非消耗性 Exercise 和 Fetch，因为这些操作不改变合约状态。

#### 3.5.2 Witnesses（见证方）

Witness 是"包含该节点的所有子 action 的 informee 的并集"。一个 witness 可能看到一个节点而不是该节点的 informee——这是因为 Daml 的确定性执行意味着如果一个 Party 是根 action 的 informee，它就能看到所有后果。

#### 3.5.3 Transaction Projection（交易投影）

对于参与方集合 P，投影规则：
1. 如果 P 包含根 action 的至少一个 informee → 保留整个 action 及其后果
2. 否则，如果该 action 有后果 → 用后果的投影替换
3. 否则 → 丢弃该 action

**关键性质**：投影后的账本不再是线性账本，而是一个 **DAG（有向无环图）**，因为 requester 信息无法保留。

#### 3.5.4 Divulgence（泄露）

- **立即泄露**：Witness 看到他们不是 informee 的合约创建——因为 Daml 是确定性的，actor 本可以计算出结果
- **追溯泄露**：输入合约出现在非 informee witness 的投影中——验证必需

#### 3.5.5 Explicit Disclosure（显式披露）

- 被泄露的合约**不自动**授予后续使用权
- 需要通过 `submitWithDisclosures` 显式披露
- 设计原因：非利益相关方能看到创建但看不到后续归档/修改，隐式持久性规则不安全
- 链下披露（off-ledger disclosure）是双边的，可扩展到多方而不会导致二次方投影膨胀

#### 3.5.6 Merkle DAG 实现

交易被编码为 Merkle DAG 结构：
- 每个子交易是 DAG 中的一个节点
- 每个 Participant 只收到自己有权查看的子树
- 哈希链接保证了被隐藏部分的完整性
- Sequencer 和 Mediator 无法读取加密的交易内容

### 3.6 Daml（智能合约语言）

**定义**：Daml 是一种函数式、强类型的领域特定语言 (DSL)，专为多方分布式应用设计。语法类似 Haskell，编译为 Daml-LF 字节码在账本上执行。

#### 3.6.1 语言特性

- **函数式编程**：基于 Haskell 范式，支持模式匹配、类型约束、monadic 操作
- **强类型系统**：编译时类型检查，支持原生类型、复合类型（Record, Variant）、Optional 类型
- **标准库**：包含 Prelude、重要 Typeclass（Eq, Ord, Show, Functor）
- **接口 (Interfaces)**：支持合约多态和 trait-like 能力
- **异常处理**：内置异常处理机制

#### 3.6.2 Template 结构

Template 是 Daml 合约的基本单元，定义了：

```daml
template IOU
  with
    issuer : Party
    owner : Party
    amount : Decimal
    currency : Text
  where
    signatory issuer        -- 签署方：必须授权合约创建/归档
    observer owner          -- 观察方：可以看到合约但不需要授权
    
    choice Transfer : ContractId IOU
      with newOwner : Party
      controller owner      -- 控制方：可以行使该选择权的 Party
      do
        create this with owner = newOwner
```

#### 3.6.3 授权模型（Signatories / Observers / Controllers）

| 角色 | 定义 | 权限 |
|------|------|------|
| **Signatory** | 合约签署方 | 必须授权合约创建；合约归档时被通知 |
| **Observer** | 合约观察方 | 可以看到合约和相关事件，但不需要授权 |
| **Controller** | 选择权控制方 | 可以行使特定的 Choice（类似方法调用） |
| **Actor** | 实际行使者 | 行使选择权的 Party（是 Controller 的子集） |

**授权规则**：
- Create actions 需要所有 Signatories 授权
- Exercise/Fetch actions 需要所有 Actors 授权
- 义务需要同意：Party 不能在未授权的情况下被绑定
- 权利不能被单方面移除：只有授权的 exercise 才能消耗合约

**常见工作流模式**：
- **Propose-Accept 模式**：用于一次性授权（如转让提案 → 接受）
- **Role Contract 模式**：用于持续性授权委托

#### 3.6.4 Daml-LF 字节码

Daml 编译为 Daml-LF（Ledger Format），一种与账本无关的中间表示：
- **DAR 文件**：打包的 Daml 归档文件，包含一个或多个 DALF 文件
- **DALF 文件**：单个 Daml-LF 包
- **类型映射**：Daml 类型 → Daml-LF 原始类型、元组类型、数据类型、同义类型、模板类型
- **内容寻址**：Template ID 通过内容哈希寻址，确保不可变性
- **JSON 编码**：支持类型导向的 JSON 序列化/反序列化

#### 3.6.5 执行模型

- 基于 **UTxO 扩展模型**：合约创建产生 output，消耗性行使消耗 input
- **Transient 合约**：在同一交易中创建和消耗的中间合约
- **非消耗性行使**：保留合约不被消耗，适合委托和查询场景
- **确定性执行**：相同输入必定产生相同输出，这是隐私模型的基础

#### 3.6.6 代码仓库

- **主仓库**：[github.com/digital-asset/daml](https://github.com/digital-asset/daml)
- **语言**：Haskell 65.7%, Scala 15.2%, Starlark 9.9%
- **星标**：891 stars
- **许可证**：Apache-2.0
- **当前稳定版**：2.10.4 / 3.4.11

### 3.7 Canton Network（跨 Domain 互操作与原子可组合性）

**定义**：Canton Network 是一个于 2024 年启动的公共许可网络，通过 Global Synchronizer 提供 transaction-level interoperability 和跨子网的原子智能合约调用能力，连接独立的区块链应用；当合约需要迁移到另一个 Synchronizer 时，底层仍依赖非原子 Reassignment。

#### 3.7.1 Global Synchronizer

- **BFT 共识**：使用 2/3 多数拜占庭容错共识协议进行消息排序和确认
- **Super Validators**：独立组织运营的验证节点，通过链上治理应用协调活动
- **隐私保护**：即使交易跨多个应用和子网，只有利益相关方才能看到、验证和记录自己相关的部分

#### 3.7.2 跨 Synchronizer 交易流程

当交易涉及多个 Synchronizer 上的合约时：

```
1. 选择 Synchronizer：找到所有利益相关方都有节点的 Synchronizer
2. 重新分配 (Reassignment)：将输入合约移动到选定的 Synchronizer
   - Unassignment（源 Synchronizer）：合约在源上变为非活跃
   - Assignment（目标 Synchronizer）：合约在目标上激活
3. 执行交易：在选定的 Synchronizer 上运行交易
4. 可选路由：将输出合约重新分配到期望的 Synchronizer
```

**注意**：Reassignment 是**非原子的**（non-atomic），涉及两个不同 Synchronizer 上的两个独立阶段。跨 Synchronizer 没有全局排序保证——不同 Synchronizer 的事件可以以任意顺序出现在 Participant 的更新流中，但每个 Synchronizer 的投影保持因果一致。

#### 3.7.3 合约分配 (Contract Assignation)

- 利益相关方之间就哪个 Synchronizer 协调特定合约的变更达成一致
- 不是永久性的——可以通过 Reassignment 改变
- 自动路由器按优先级选择 Synchronizer（最高优先级 → 最少重新分配 → 最低 Synchronizer ID）

#### 3.7.4 治理结构

- **Global Synchronizer Foundation (GSF)**：与 Linux Foundation 共同建立
- **Canton Coin**：原生实用代币，用于支付 Global Synchronizer 流量费用，激励基础设施提供者、应用开发者和跨链连接器

#### 3.7.5 Synchronizer-Aware Projection

跨 Synchronizer 场景中的可见性通过 Enter/Leave 事件管理：
- **Enter**：Party 可以在其 Synchronizer 上使用合约
- **Leave**：合约正在离开，暂停本地使用权
- **Witnessed Actions**：当 action 在 Party 未托管的 Synchronizer 上提交时，标记为"仅见证"（merely witnessed）

---

## 4. 关键设计决策与权衡

### 4.1 Need-to-Know 隐私 vs 全局可见性

| 决策 | Canton 选择 | 替代方案 | 权衡 |
|------|------------|----------|------|
| **隐私粒度** | 子交易级隐私（Merkle DAG） | 交易级隐私（ZKP）或全局可见（Ethereum） | + 精细隐私控制，GDPR 合规<br>- 更复杂的协议设计，更高的协调开销 |
| **可审计性** | 完整审计轨迹 + 隐私 | ZKP（失败时不可见） | + 可证明系统未被入侵<br>- 需要信任 Participant 节点运营者 |

### 4.2 Virtual Global Ledger vs Shared State

| 决策 | Canton 选择 | 替代方案 | 权衡 |
|------|------------|----------|------|
| **状态模型** | 虚拟全局账本（每方只看到投影） | 全局共享状态（Ethereum） | + 无全局状态瓶颈，水平扩展<br>- 无法做全局查询，依赖应用层聚合 |
| **数据存储** | 各 Participant 独立存储（PostgreSQL） | 全节点完整副本 | + GDPR 合规（可删除数据）<br>- Party 间状态同步更复杂 |

### 4.3 Sequencer-Mediator 分离 vs 单一共识

| 决策 | Canton 选择 | 替代方案 | 权衡 |
|------|------------|----------|------|
| **共识架构** | 排序（Sequencer）与确认（Mediator）分离 | 单一 BFT 共识（PBFT/Tendermint） | + 各组件独立扩展和去中心化<br>+ Sequencer 不知道交易内容<br>- 额外的网络往返（2PC） |
| **排序后端** | 可插拔（Canton 原生/Ethereum/Fabric） | 固定共识算法 | + 灵活适配不同企业环境<br>- 不同后端的安全性和性能特征不同 |

### 4.4 Daml DSL vs 通用语言

| 决策 | Canton 选择 | 替代方案 | 权衡 |
|------|------------|----------|------|
| **合约语言** | 专用 DSL（Daml） | 通用语言（Solidity/Rust） | + 编译时授权检查，更安全<br>+ 确定性执行保证<br>- 开发者需学习新语言<br>- 生态系统较小 |
| **扩展方向** | Polyglot Canton（Solidity/Wasm 支持白皮书已发布） | 仅 Daml | + 未来将支持更广泛的开发者社区<br>- 可能牺牲一些安全保证 |

### 4.5 Explicit Disclosure vs Implicit Divulgence

| 决策 | Canton 选择 | 替代方案 | 权衡 |
|------|------------|----------|------|
| **披露模型** | 显式披露（submitWithDisclosures） | 自动使用被泄露合约 | + 防止脆弱性（非利益相关方看不到归档）<br>+ 双边披露可扩展<br>- 应用层需要更多逻辑 |

### 4.6 Non-Atomic Reassignment vs Atomic Cross-Domain

| 决策 | Canton 选择 | 替代方案 | 权衡 |
|------|------------|----------|------|
| **跨域转移** | 非原子 Reassignment（Unassign + Assign） | 原子跨域交易 | + 更简单的协议，无需跨域锁定<br>- 合约在转移过程中可能暂时不可用<br>- 无跨 Synchronizer 全局排序 |

### 4.7 Cryptographic Identity vs Legal Identity

| 决策 | Canton 选择 | 替代方案 | 权衡 |
|------|------------|----------|------|
| **身份模型** | 密码学身份（密钥指纹）与法律身份分离 | KYC 内置身份（Corda） | + 系统有效性不依赖真实身份<br>+ 隐私保护更强<br>- 合规映射需要链下机制 |

---

## 5. 与传统区块链（Ethereum L2）的关键区别

| 维度 | Canton | Ethereum L2 (如 Mantle/OP Stack) |
|------|--------|--------------------------------|
| **状态模型** | 虚拟全局账本，每方只看到投影 | 全局共享状态，所有节点看到相同数据 |
| **隐私** | 子交易级隐私（need-to-know） | 默认全透明（需 ZKP 等额外方案） |
| **共识** | Sequencer 排序 + Mediator 2PC | 排序器 + L1 结算（Optimistic/ZK Rollup） |
| **智能合约** | Daml（函数式 DSL，编译时授权检查） | Solidity/Vyper（EVM 通用执行） |
| **合约模型** | UTxO 扩展（不可变合约，创建/归档） | Account 模型（可变状态） |
| **数据存储** | 分布式（各 Participant 仅存自己可见的数据） | 集中式（所有节点存完整状态） |
| **GDPR 合规** | 原生支持（可删除数据，因为不是全局副本） | 极难实现（链上数据不可变且全局复制） |
| **可扩展性** | 水平扩展（增加 Synchronizer） | 受限于单一排序器和 L1 结算吞吐 |
| **互操作性** | Global Synchronizer 提供跨子网原子调用/价值交换；合约 Reassignment 为非原子 | 跨 L2 桥接（需要消息传递协议） |
| **许可模型** | 许可制（Party 需要 Participant 节点承载） | 无许可（任何人可参与） |
| **交易终局性** | 由 Mediator 确认（确定性终局） | Optimistic: 7 天挑战期 / ZK: 证明验证后 |
| **Token 模型** | Daml Finance 库（不可变合约 + 显式转移） | ERC-20/721/1155（可变余额映射） |
| **KYC/合规** | 链上凭证合约（KYCCredential template） | 链下 or 第三方合规层 |
| **开发者生态** | 较小（需学习 Daml），但正通过 Polyglot 扩展 | 巨大（Solidity 开发者 + 工具生态） |
| **去中心化程度** | 联邦制（许可网络，Super Validators） | 更高（开放参与，但 Sequencer 常中心化） |

**核心区别总结**：Canton 不是传统意义上的区块链。它是一个**隐私优先的交易协调协议**，通过虚拟全局账本将多方的私有数据投影统一为一个逻辑整体。而 Ethereum L2 是**全局共享状态的执行层**，通过 Rollup 压缩和 L1 安全继承实现扩展。两者的设计出发点根本不同：Canton 服务于企业合规场景（隐私、GDPR、机构治理），Ethereum L2 服务于开放金融和通用计算。

### 5.1 隐私方案横向对比

Canton 的子交易级隐私并非企业链隐私的唯一方案，下表将其与其他主流隐私技术对比：

| 维度 | Canton Sub-transaction Privacy | Fabric Channels + Private Data Collections | ZK/Confidential Transactions (如 zkSync Prividium) | Public L2 + 链下隐私 |
|------|------|------|------|------|
| **隐私粒度** | 子交易级（action 级别） | Channel 级别（粗粒度）+ PDC 可做字段级别 | 交易级别（ZKP 证明完整交易有效性） | 无链上隐私（calldata 公开） |
| **隐私机制** | Merkle DAG 投影 + need-to-know | 物理隔离（独立账本）+ gossip 哈希锚定 | 零知识证明（不透露输入输出） | 依赖链下通道或 TEE |
| **验证者可见性** | Sequencer/Mediator 看不到交易内容 | Orderer 看不到 PDC 数据；但 Channel 内节点看到全部 | 验证者仅验证证明，不看交易细节 | 验证者/排序器看到全部 calldata |
| **合规审计** | 完整审计轨迹（投影给审计方即可） | Channel 成员有完整账本；PDC 需要显式分享 | ZKP 失败时不可见；需要额外的审计电路 | 链上数据公开可审计 |
| **GDPR 合规** | ✅ 原生（各方只存自己数据，可删除） | ⚠️ Channel 内全复制；PDC 可设 TTL | ⚠️ ZK 证明可能包含不可删除的链上锚点 | ❌ 链上数据不可变 |
| **跨域/跨链** | 跨 Synchronizer Reassignment（非原子） | 跨 Channel 需要中间合约或 relay | 跨链 ZKP 验证（实验性） | 跨 L2 桥接 |
| **性能开销** | 2PC + Merkle 构建（中等） | Channel 隔离低开销，PDC gossip 有上限 | ZKP 生成高计算成本 | 无隐私开销 |
| **开发者体验** | Daml DSL（学习成本高） | Go/Java/Node chaincode（生态较大） | Solidity + ZK 电路（ZK 部分学习曲线陡） | Solidity（最大生态） |
| **适用场景** | 多方复杂交易（DvP、供应链、跨机构结算） | 多组织联盟（已知成员、较少跨 Channel 需求） | 公链上的隐私 DeFi、合规代币 | 通用 DeFi、NFT |

**关键洞察**：
- Canton 的隐私在**多方复杂交易**场景（如 DvP、供应链金融）中最有优势，因为它能在同一笔交易中给不同参与方展示不同的数据切片。
- Fabric Channels 的隐私是**组织级隔离**，粒度较粗，但运维和理解成本更低。
- ZKP 方案的隐私是**密码学保证**，理论安全性最强，但计算开销大、审计灵活性差。
- 这些方案并非互斥——Polyglot Canton 白皮书探索了在 Canton 上支持 ZKP 的可能性。

---

## 6. 对 Mantle/OP Stack 企业级改造的启示

基于本文档对 Canton 的调研，以下分析哪些设计可借鉴、哪些难以迁移、需要新增什么模块、以及主要风险。

### 6.1 可借鉴的 Canton 设计

| Canton 设计 | Mantle 可借鉴方式 | 改造复杂度 |
|------------|------------------|-----------|
| **Need-to-know 隐私投影** | 在 OP Stack 执行层引入交易可见性过滤——特定交易/状态仅对授权地址可见。可通过 access-controlled state tries 或加密 calldata + 密钥分发实现 | 🔴 高：需修改状态存储和 P2P 层 |
| **Signatory/Observer 授权模型** | 在合约层引入角色化访问控制（类似 RBAC），通过 modifier 或 precompile 实现合约操作的多方授权要求 | 🟡 中：可在合约层实现，不需修改底层 |
| **审计方投影（Regulatory Observer）** | 为监管节点提供增强的状态可见性，类似 Canton 中给 observer Party 的投影能力。可通过特殊全节点模式或 DA 层选择性解密实现 | 🟡 中：需定义监管节点角色和数据流 |
| **身份与密码学身份分离** | 采用 DID/VC 体系将链上地址与链下 KYC 身份解耦，保持链上交互的隐私性同时满足合规 | 🟢 低：可在应用层/中间件实现 |
| **可插拔共识/排序后端** | OP Stack 已有 Sequencer 架构，可扩展为支持多种排序模式（中心化/去中心化/联邦制），类似 Canton 的可插拔 Sequencer | 🟢 低：OP Stack 架构已支持 |

### 6.2 难以迁移的 Canton 前提

| Canton 前提 | 为什么难以迁移到 Mantle/OP Stack | 影响评估 |
|------------|--------------------------------|---------|
| **Daml 运行时** | Canton 的隐私模型深度依赖 Daml 的确定性执行和 signatory/observer 语义。EVM 的 account 模型和 Solidity 缺乏这些原语——在 EVM 上实现等价语义需要全新的执行层或 precompile 集 | 高：不能直接移植，需要替代设计 |
| **虚拟全局账本（非共享状态）** | Canton 每方只存自己的投影。OP Stack/Ethereum 的核心假设是全局共享状态——所有节点维护相同的状态树。改为分区状态会破坏 EVM 兼容性和现有工具链 | 高：与 EVM 范式根本冲突 |
| **Synchronizer 治理模型** | Canton 的 Synchronizer 可独立治理、独立定价。OP Stack 的 Sequencer 没有内置的多 Synchronizer 联邦治理机制 | 中：需要新的治理框架 |
| **Merkle DAG 交易结构** | Canton 的 Merkle DAG 允许选择性披露子树。EVM 交易是原子的扁平结构，没有子交易的概念 | 高：需要扩展交易格式 |

### 6.3 Mantle 企业化需要新增的模块

1. **隐私层**：在 DA 层或执行层引入加密/选择性可见性机制（可参考 Canton 的 need-to-know 但需适配 EVM）
2. **身份/权限层**：链上 DID 注册表 + 角色化访问控制 precompile
3. **合规可观测层**：监管节点专用 API + 审计日志 + 可配置的交易透明度级别
4. **企业级排序器**：联邦制/许可制排序器选项，配合 MEV 保护和交易优先级
5. **跨机构互操作**：类似 Canton 跨 Synchronizer 的机制，允许不同企业部署实例间的受控跨域互操作/原子调用，并显式处理 Reassignment 的非原子边界

### 6.4 风险与成本

| 风险 | 说明 | 缓解方向 |
|------|------|---------|
| **EVM 兼容性损失** | 深度隐私改造可能破坏 EVM 兼容性，失去 Solidity 生态优势 | 采用 precompile/系统合约方式而非修改 EVM 核心 |
| **开发者生态分裂** | 企业级功能可能与公链 OP Stack 生态分叉 | 保持核心 OP Stack 升级兼容，企业功能作为可选模块 |
| **性能退化** | 隐私层（加密/解密/ZKP）会显著增加计算和延迟 | 采用硬件加速（TEE/GPU）或混合方案（敏感交易走隐私层，其余走标准层） |
| **治理复杂度** | 企业许可制与 L2 开放参与的理念冲突 | 采用 L2/L3 分层：L2 开放 + 企业 L3 许可制 |

---

## 7. 补充发现

### 7.1 Daml Finance 库

Canton 的金融应用建立在 Daml Finance 库之上，这是一个全面的金融工具库：

**支持的工具类型**：
- **固定收益**：定息/浮息/通胀挂钩/零息/可赎回债券
- **股权与衍生品**：股权（含分红）、欧式期权（现金/实物交割）、障碍期权
- **结构化产品**：自动赎回票据、障碍反向可转债
- **互换**：利率互换、货币互换、资产互换、信用违约互换、外汇互换、FpML 合规互换
- **通用工具**：Token/加密货币模型、基于 Contingent Claims 的自定义收益结构

**结算框架**：内部结算、中介结算、批量处理、路由提供者

### 7.2 拓扑管理

Canton 使用基于密码学的分层身份和授权系统：
- **Namespace**：由自签名根证书定义，密钥指纹即为 namespace 标识符
- **委托限制**：三级权限（CanSignAllMappings / CanSignAllButNamespaceDelegations / CanSignSpecificMappings）
- **UID**：identifier + namespace 组合，如 `jane_doe::abc123`
- **拓扑事务**：含序列号（防重放）、变更操作（REPLACE/REMOVE）、多方签名
- **密钥撤销**：通过 REMOVE 操作广播 namespace 委托，但不影响已验证的历史交易

### 7.3 API 层

- **gRPC Ledger API (v1/v2)**：底层 protobuf 接口，支持命令提交/完成、交易读取、活跃合约查询、Party/User 管理等
- **HTTP JSON API**：REST 桥接层，将 HTTP/JSON 请求转换为 gRPC 调用
- **SDK 绑定**：Java、Python、TypeScript/JavaScript

### 7.4 企业采用证据（Institutional Adoption Evidence）

下表逐机构整理 Canton/Daml 的企业部署情况。**重要说明**：Canton 生态包含多种参与层次——从签署 MOU 的早期合作到生产环境运行的成熟部署。下表尽可能区分这些层次。

| 机构 | 产品/平台 | 用例类型 | 部署状态 | 关键指标 | 来源 | 日期/时间窗口 |
|------|----------|----------|----------|----------|------|--------------|
| **Goldman Sachs** | GS DAP™ | 多资产类代币化发行与结算 | ✅ 生产部署 | 结算从 T+5 缩至 <60s；EIB €1亿数字原生债券首发 | [digitalasset.com/use-cases/tokenization](https://www.digitalasset.com/use-cases/tokenization); [cantonecosystem.com](https://www.cantonecosystem.com/) | 持续运营中 |
| **HSBC** | Orion | 债券生命周期管理（发行→结算→回购） | ✅ 生产部署（4支数字债券已完成） | 结算从 T+5 缩至 T+1；"前所未有的投资者需求和二级交易" | [digitalasset.com/use-cases/tokenization](https://www.digitalasset.com/use-cases/tokenization) | 持续运营中 |
| **Nasdaq** | — | 碳信用发行、结算与托管代币化 | ✅ 生产部署 | 支持市场运营商和注册机构 | [digitalasset.com/use-cases/tokenization](https://www.digitalasset.com/use-cases/tokenization) | 持续运营中 |
| **Broadridge** | — | UST 回购代币化 | ✅ 生产部署 | "每月处理数万亿美元代币化 UST 回购" | [cantonecosystem.com](https://www.cantonecosystem.com/) | 持续运营中 |
| **Bank of China** | — | HKSAR 首支代币化绿色债券协调 | ✅ 已完成 | 香港特区首支代币化绿色债券 | [cantonecosystem.com](https://www.cantonecosystem.com/) | 已完成 |
| **J.P. Morgan (Kinexys)** | JPM Coin (JPMD) | 将 USD JPM Coin 原生接入 Canton Network | 🔵 概念验证阶段 | — | [digitalasset.com/newsroom](https://www.digitalasset.com/newsroom) | 2026-01-07 公告 |
| **HQLAX** | — | 抵押品管理/转换 | ✅ 活跃部署 | Broadridge 和 Digital Asset 战略投资 | [digitalasset.com/newsroom](https://www.digitalasset.com/newsroom) | 2026-04-21 投资公告 |
| **Hanwha Securities** | — | 待定（MOU 签署） | 🟡 早期合作 | 签署谅解备忘录 | [digitalasset.com/newsroom](https://www.digitalasset.com/newsroom) | 2026-04-22 MOU |
| **BNY Mellon** | — | 生态参与者 + 战略投资方 | 🟡 战略合作 | 参与 $5000 万融资轮 | [digitalasset.com/newsroom](https://www.digitalasset.com/newsroom) | 2025-12-04 |
| **DTCC** | — | 生态参与者 | 🟡 生态列名 | 列于 Canton 生态目录 | [cantonecosystem.com](https://www.cantonecosystem.com/) | — |
| **Citi** | — | 生态参与者 | 🟡 生态列名 | 列于 Canton 生态目录 | [cantonecosystem.com](https://www.cantonecosystem.com/) | — |
| **Bank of America** | — | 生态参与者 | 🟡 生态列名 | 列于 Canton 生态目录 | [cantonecosystem.com](https://www.cantonecosystem.com/) | — |

**网络规模统计**：

| 指标 | 数值 | 来源 | 说明 |
|------|------|------|------|
| 生态项目/应用/验证者数 | 450+ | [cantonecosystem.com](https://www.cantonecosystem.com/)（2026-05 访问） | 包含 projects、apps、validators，非单纯节点数 |
| 月度代币化规模 | $2T+ | [canton.network/global-synchronizer](https://canton.network/global-synchronizer)（2026-05 访问） | Global Synchronizer 页面声称 |
| 月度代币化规模（替代来源） | $1.5T+ | [digitalasset.com/use-cases/tokenization](https://www.digitalasset.com/use-cases/tokenization)（2026-05 访问） | 标注为"across all customers" |
| 年度交易流 | $4.5T | [digitalasset.com/use-cases/clearing-settlement](https://www.digitalasset.com/use-cases/clearing-settlement)（2026-05 访问） | Daml 应用支撑的年化交易流 |

> ⚠️ **数据解读注意**：
> - "$2T+/月"和"$1.5T+/月"出自不同页面，可能反映不同统计口径（名义金额 vs 结算金额、全网 vs 仅代币化）或不同更新时间。后续引用时应注明来源页面。
> - "450+"包含所有类型的生态参与者（项目、应用、验证者），并非都是独立运营 Participant Node 的机构。
> - 生态目录列名（🟡 生态列名）仅表示该机构出现在 cantonecosystem.com 上，不等同于生产部署或深度集成。

---

## 8. 开放问题与后续研究清单（Open Questions for WHI-335 / WHI-336）

以下问题在本次官方文档调研中尚未完全解答，需要在 WHI-335（Canton 架构深度分析）和 WHI-336（Canton 代码库分析）中通过白皮书精读和源码分析进一步澄清。

### 8.1 协议与共识层（→ WHI-335）

1. **Synchronizer BFT/故障模型**：Canton 的 BFT 共识具体采用什么算法？容错阈值是多少（文档提到 2/3 多数）？在 Sequencer 或 Mediator 节点故障时，恢复流程如何？是否有 view change 机制？
2. **Mediator Verdict 细节**：Mediator 在出具 APPROVE/REJECT verdict 时的具体密码学流程是什么？它如何在不看到交易内容的情况下验证确认消息的完整性？verdict 是否有密码学证明？
3. **跨 Synchronizer Reassignment 的原子性边界**：Reassignment 的 Unassign 和 Assign 两步之间如果发生故障会怎样？合约是否可能在两个 Synchronizer 上都不可用？回滚机制是什么？
4. **消息排序的确定性**：不同 Sequencer 后端（Canton 原生 vs Ethereum vs Fabric）在排序的确定性、延迟和安全性上有何具体差异？

### 8.2 治理与经济模型（→ WHI-335）

5. **Global Synchronizer 治理**：Super Validator 的选举/准入机制是什么？GSF 的治理决策流程（如参数变更、升级）如何执行？
6. **Canton Coin 经济模型**：流量费用定价机制的细节？Canton Coin 的发行、分配、通胀模型？对 Participant 的成本影响？
7. **Synchronizer 间竞争与选择**：当多个 Synchronizer 可用时，自动路由器的优先级逻辑如何处理延迟、成本和信任度权衡？

### 8.3 运维与数据管理（→ WHI-335 / WHI-336）

8. **Participant 数据恢复**：如果一个 Participant Node 的 PostgreSQL 数据库损坏，恢复流程是什么？能否从其他 Participant 获取缺失的投影数据？
9. **监管节点/审计可见性**：Canton 是否有内置的 Regulatory Observer 角色？监管机构如何获得跨 Participant 的全局视图而不违反 need-to-know 原则？
10. **数据删除与 GDPR**：当 Party 请求删除数据（GDPR right to erasure）时，已经提交的历史交易中与该 Party 相关的数据如何处理？是否需要所有持有投影的 Participant 配合？

### 8.4 代码与实现（→ WHI-336）

11. **Daml Engine 性能**：Daml-LF 解释器的执行性能如何？是否有基准测试数据？大规模合约（如 1000+ signatory）的执行瓶颈在哪？
12. **Polyglot Canton 进展**：Solidity/Wasm 支持的白皮书已发布，但实际实现进度如何？代码库中是否有 EVM 适配器的原型？
13. **可扩展性上限**：单个 Synchronizer 能支持多少 Participant？Sequencer 吞吐量的理论和实测上限？
14. **密码学选择**：Canton 使用哪些具体的密码学原语（签名算法、哈希函数、加密方案）？是否支持后量子密码学？

### 8.5 企业采用验证（→ WHI-335）

15. **采用数据二次验证**：$2T+/月和$1.5T+/月两个数字的差异原因？是否有第三方审计或独立验证？
16. **生产部署深度**：Goldman Sachs GS DAP™ 和 HSBC Orion 的实际生产规模（日交易量、用户数）？是否有公开的性能报告？
17. **监管认可状态**：Canton Network 是否获得任何金融监管机构的正式认可或批准？Canton Coin 的 MiCA 合规状态？

---

## 9. 参考链接

### 官方文档
- [Daml SDK 2.10.4 文档](https://docs.daml.com)
- [Canton Network 3.x 平台文档](https://docs.digitalasset.com/)
- [Canton Network 3.4 概览](https://docs.digitalasset.com/overview/3.4/)
- [Canton 详解索引](https://docs.digitalasset.com/overview/3.4/explanations/)
- [运维文档](https://docs.digitalasset.com/operate/3.4/index.html)
- [HTTP JSON API](https://docs.daml.com/json-api/index.html)
- [Daml Finance 库](https://docs.daml.com/daml-finance/index.html)

### 架构深度文档
- [Canton 白皮书索引](https://canton.network/whitepaper)
- [Canton 核心技术白皮书 PDF](https://www.canton.io/publications/canton-whitepaper.pdf)
- [拓扑管理](https://docs.digitalasset.com/overview/3.4/explanations/canton/topology.html)
- [协议机制](https://docs.digitalasset.com/overview/3.4/explanations/canton/protocol.html)
- [隐私模型](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/ledger-privacy.html)
- [Global Synchronizer](https://canton.network/global-synchronizer)
- [账本结构](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/ledger-structure.html)
- [账本完整性](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/ledger-integrity.html)
- [Daml 合约模型](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/ledger-daml.html)
- [去中心化](https://docs.digitalasset.com/overview/3.4/explanations/canton/decentralization.html)
- [多 Synchronizer 操作](https://docs.digitalasset.com/overview/3.4/explanations/canton/multi-synchronizer.html)
- [外部 Party](https://docs.digitalasset.com/overview/3.4/explanations/canton/external-party.html)
- [流量管理](https://docs.digitalasset.com/overview/3.4/explanations/canton/traffic-management.html)
- [互操作性/Synchronizer-Aware Projection](https://docs.digitalasset.com/overview/3.4/explanations/ledger-model/interoperability.html)

### GitHub 代码库
- [Canton (Scala)](https://github.com/digital-asset/canton) — 114 stars, Apache-2.0, v3.5.1-rc3
- [Daml (Haskell)](https://github.com/digital-asset/daml) — 891 stars, Apache-2.0, v2.10.4
- [CN Quickstart](https://github.com/digital-asset/cn-quickstart) — Docker Compose 架构
- [Daml Finance](https://github.com/digital-asset/daml-finance) — 企业级代币化库

### 技术博客
- [ZKP vs Canton 隐私](https://www.canton.network/blog/zero-knowledge-proofs-whe-privacy-needs-more)
- [Canton vs EVM RWA 代币化](https://blog.digitalasset.com/blog/tokenization-of-rwas-on-canton-network-vs-evm-chains-part-2)
- [代币化平台与金融基础设施未来](https://blog.digitalasset.com/blog/tokenization-platforms-and-the-future-of-financial-infrastructure)

### 第三方深度分析
- [Deep Dive on Permissioned Blockchains: The Canton Network (Flashbots Collective)](https://collective.flashbots.net/t/deep-dive-on-permissioned-blockchains-the-canton-network/5517)
- [Canton Is Not a Blockchain — Here's Why That Matters for RWAs (W2D)](https://w2d.co/insights/canton-is-not-a-blockchain-heres-why-that-matters-for-rwas/)

### API/SDK 参考
- [gRPC Ledger API](https://docs.daml.com/app-dev/grpc/)
- [Canton 3.4 Protobuf 参考](https://docs.digitalasset.com/build/3.4/reference/lapi-proto-docs.html)
- [Daml 社区论坛](https://discuss.daml.com/)

### 企业案例与生态
- [Canton 生态目录 (450+ 参与者)](https://www.cantonecosystem.com/)
- [代币化用例](https://www.digitalasset.com/use-cases/tokenization)
- [清算结算用例](https://www.digitalasset.com/use-cases/clearing-settlement)
- [Digital Asset 新闻室](https://www.digitalasset.com/newsroom)

### 白皮书
- Canton Coin MiCA 白皮书（EU MiCA 合规）
- Polyglot Canton 白皮书（Solidity/Wasm 支持）
- Canton Coin 应用白皮书（激励机制）
- Canton Network 白皮书（网络架构）
- The Canton Blockchain Protocol（核心技术论文）
