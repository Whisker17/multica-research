# WHI-336: Canton 代码库深度分析

> **Issue**: WHI-336 — Canton 代码库深度分析
> **Milestone**: M1: 各项目独立深度调研
> **Date**: 2026-05-06（修订: 2026-05-07）
> **Status**: In Review (Rev.5)
> **Prerequisites**: WHI-334 (文档调研), WHI-335 (架构分析)
> **代码库路径**: `/Users/whisker/Work/src/networks/canton/canton`
> **GitHub**: https://github.com/digital-asset/canton

---

## Executive Verdict

Canton 是一个大型 Scala/JVM monorepo（96% Scala），实现了完整的 Participant-Synchronizer 分离架构，包含隐私层（Merkle Tree 盲化 + 加密视图分发）、可插拔排序层（SequencerDriver trait）和两阶段确认协议（Mediator）。代码质量高，架构设计精密，但以下因素使 Mantle 团队**不应尝试直接复用 Canton 代码**：

1. **语言/生态壁垒**：Scala/JVM + Pekko + cats 生态与 Mantle 的 Go/Rust/TypeScript/EVM 工具链完全不兼容
2. **Daml 引擎深度耦合**：Canton 的交易处理、验证、授权、包管理全部依赖 Daml-LF 引擎，无法独立分离
3. **License 分层复杂**：root `LICENSE.txt` 为 Apache-2.0；`community/` 和 `base/` 下大部分核心模块使用 Apache-2.0 header，但存在例外（如 `community/lib/wartremover` 使用 Proprietary header）；Docker 镜像使用受限商业许可——需逐子项目确认（详见 §2）
4. **构建复杂度极高**：sbt + ScalaPB + Flyway + Buf + Nix + Docker + JMH + scoverage 多层工具链，非 Scala 团队维护成本极高

**推荐策略**：借鉴设计模式和协议分层思想，逐组件评估 Borrow pattern / Build equivalent / Avoid direct reuse（见 §14 决策表）。

---

## 1. 代码库结构概览

### 1.1 顶层目录结构

```
canton/
├── base/                  # 基础工具库（25+ 子模块）
│   ├── crypto/            # 密码学基础（JCE provider, KMS driver, 签名/验证）
│   ├── grpc-utils/        # gRPC 通用工具
│   ├── daml-tls/          # TLS 配置支持
│   ├── daml-jwt/          # JWT 认证
│   ├── errors/            # 错误处理框架
│   ├── logging-entries/   # 结构化日志
│   ├── observability/     # 可观测性
│   └── ...                # timer-utils, ports, resources, scala-utils 等
├── community/             # 核心实现（30+ 子模块）— 主要分析对象
│   ├── app/               # 应用入口（CantonCommunityApp）
│   ├── app-base/          # 应用基础类
│   ├── base/              # 核心数据结构（MerkleTree, Protocol, Topology）
│   ├── common/            # 共享模块（Config, Store, Sequencing handlers）
│   ├── participant/       # Participant 节点完整实现
│   ├── synchronizer/      # Synchronizer（Sequencer + Mediator）实现
│   ├── sequencer-driver/  # Sequencer Driver 接口定义（SequencerDriver trait）
│   ├── reference-sequencer-driver/  # 参考 Sequencer Driver 实现
│   ├── ledger/            # Ledger API 核心
│   ├── ledger-api-proto/  # Ledger API Protobuf 定义
│   ├── ledger-api-scala/  # Ledger API Scala 绑定
│   ├── bindings-java/     # Java 绑定
│   ├── daml-lf/           # Daml-LF 相关
│   ├── kms-driver-api/    # KMS Driver 接口
│   ├── aws-kms-driver/    # AWS KMS 实现
│   └── ...                # testing, conformance, integration 等
├── docker/                # Docker 镜像构建（canton-base, canton 等）
│   └── canton/images/canton-base/LICENSE.txt  # ⚠ Proprietary 许可（非 Apache）
├── docs-open/             # 开源文档
├── performance/           # 性能测试
├── project/               # sbt 构建配置
│   ├── BuildCommon.scala  # 通用构建设置
│   ├── Dependencies.scala # 依赖管理
│   └── Houserules.scala   # 代码规范与 license header 管理
├── scripts/               # 工具脚本
├── build.sbt              # sbt 主构建文件
├── VERSION                # 版本号
├── LICENSE.txt            # ⚠ root: Apache-2.0
├── buf.work.yaml          # Protobuf lint/format 配置
└── community/LICENSE-open-source-bundle.txt  # Apache-2.0
```

### 1.2 语言与构建系统

- **主要语言**: Scala（GitHub 统计 96%），符合文档描述
- **构建系统**: **sbt**（`build.sbt` + `project/BuildCommon.scala`）
  - 使用 `sbt-protoc` / ScalaPB 进行 Protobuf → Scala 代码生成
  - 使用 `sbt-assembly` 进行 fat JAR 打包
  - 使用 `scalafmt` + `scalafix` 进行代码格式化和 linting
  - 使用 `buf` 进行 Protobuf lint/format（`buf.work.yaml`）
  - 使用 `sbt-header` 管理 license header（见 `Houserules.scala`）
  - 使用 `wartremover` 进行静态代码质量检查
  - 组织: `com.digitalasset.canton`

**代码引用**: `build.sbt:1-30`, `project/BuildCommon.scala:41-68`, `project/Houserules.scala:1-55`

### 1.3 模块依赖关系

```
                    ┌──────────────────┐
                    │     base/        │  基础工具层
                    │  (crypto, grpc,  │  (无 Canton 业务逻辑)
                    │   tls, errors)   │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  community/base  │  核心数据结构层
                    │  (MerkleTree,    │  (Protocol, Data,
                    │   Topology,      │   Sequencing client)
                    │   Sequencing)    │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │ community/common │  共享业务层
                    │  (Config, Store, │  (ContractStore,
                    │   Protocol msgs) │   SequencerInfoLoader)
                    └──────┬────┬──────┘
                           │    │
              ┌────────────▼┐  ┌▼────────────────┐
              │ community/  │  │  community/      │
              │ participant │  │  synchronizer    │
              │  (Node,     │  │  (Mediator,      │
              │   Protocol, │  │   Block update,  │
              │   Sync,     │  │   Sequencer)     │
              │   DAMLe)    │  └──────┬───────────┘
              └─────────────┘         │
                                ┌─────▼──────────┐
                                │ sequencer-driver│  Driver 接口
                                │  (trait)        │
                                └─────┬──────────┘
                                      │
                                ┌─────▼──────────┐
                                │ reference-     │  参考实现
                                │ sequencer-     │  (DB-backed)
                                │ driver         │
                                └────────────────┘
```

---

## 2. License 审计

### 2.1 分层 License 结构

Canton 代码库存在明确的 **双轨 license** 体系，通过 `project/Houserules.scala` 中的 sbt-header 插件自动管理：

| 层级 | License | 证据文件 | 说明 |
|------|---------|---------|------|
| **Root** (`LICENSE.txt`) | Apache-2.0 | `LICENSE.txt:1-2` | 仓库根目录声明 Apache-2.0 |
| **community/ 核心模块源码** | Apache-2.0（大部分） | `Houserules.scala:46-54` `damlRepoHeaderSettings` | 源码 header: `SPDX-License-Identifier: Apache-2.0`；已验证 `CantonCommunityApp.scala`, `DAMLe.scala`, `TopologyManager.scala`, `BftSequencerFactory.scala` 等。**例外**: `community/lib/wartremover` 使用 Proprietary header（已验证 `ProtobufToByteString.scala:1-3`） |
| **community/ open-source bundle** | Apache-2.0 | `community/LICENSE-open-source-bundle.txt` | 开源捆绑包 Apache-2.0 |
| **base/ 子项目源码** | Apache-2.0（大部分） | `BuildCommon.scala` 中 community/base 使用 `damlRepoHeaderSettings` | 与 community/ 相同的 Apache header；已验证 `MerkleTree.scala`, `TopologyMapping.scala` 等 |
| **community/lib/** | **Mixed / 需逐子目录确认** | 多个子目录各有不同 header | `wartremover`、`magnolify`: Proprietary header（已验证）；`wartremover-annotations`: Apache-2.0（已验证）；`Blake2b`: BouncyCastle fork（无标准 header，原始为 MIT-like）；`scalatest`、`slick`: 第三方 fork/extension（无 DA header，原始项目各有独立许可）。此目录是 internal + third-party 混合区，不可整体归类 |
| **非 community/ 非 base/ 代码** | Proprietary header | `Houserules.scala:22-41` `cantonRepoHeaderSettings` | 默认 repo header: `Proprietary code. All rights reserved.`；适用于企业版/闭源子项目 |
| **Docker 镜像** | **受限/Proprietary** | `docker/canton/images/canton-base/LICENSE.txt:1-70` | 非 Apache-2.0——Proprietary license，**使用前需获得 Digital Asset 书面同意**（Section 5: "You must receive Digital Asset's written consent prior to downloading, installing, or using the Software"）；仅授权用于 TestNet 评估或 MainNet 集成目的；禁止反向工程、转售、子许可；不提供任何担保 |

**重要澄清**: 仓库的 license 结构是 **分层而非二元** 的，且存在子目录级例外。root `LICENSE.txt` 声明 Apache-2.0，`community/` 和 `base/` 下的**大部分核心模块**（participant, synchronizer, base, sequencer-driver, reference-sequencer-driver, ledger 等）通过 `damlRepoHeaderSettings` 使用 Apache-2.0 header。但 `community/lib/` 是 **mixed / third-party-and-internal exceptions bucket**：`wartremover` 和 `magnolify` 使用 Proprietary header；`wartremover-annotations` 使用 Apache-2.0；`Blake2b` 是 BouncyCastle fork（MIT-like）；`scalatest` 和 `slick` 是第三方 fork/extension（各有独立许可）。`Houserules.scala` 同时定义了 `cantonRepoHeaderSettings`（Proprietary header），适用于不在 community/base 路径下的企业版代码。Docker 构建产物使用独立的受限商业许可。**结论**: 不能说"所有 community 都是 Apache"——需逐文件/逐子项目确认，尤其是 `community/lib`、forked third-party code、Docker images 和 enterprise artifacts。

### 2.2 关键发现

**`Houserules.scala:22-54` 的双 header 配置**:

```scala
// cantonRepoHeaderSettings — 用于企业/闭源代码
"Copyright (c) 2026 Digital Asset (Switzerland) GmbH and/or its affiliates.
 Proprietary code. All rights reserved."

// damlRepoHeaderSettings — 用于 community/ 子项目
"Copyright (c) 2026 Digital Asset (Switzerland) GmbH and/or its affiliates. All rights reserved.
 SPDX-License-Identifier: Apache-2.0"
```

**已验证的源码 header 示例**:
- `CantonCommunityApp.scala:1-2`: `// SPDX-License-Identifier: Apache-2.0` ✓
- `DAMLe.scala:1-2`: `// SPDX-License-Identifier: Apache-2.0` ✓
- `TopologyManager.scala:1-2`: `// SPDX-License-Identifier: Apache-2.0` ✓

**Docker 镜像许可**(`docker/canton/images/canton-base/LICENSE.txt`): Proprietary/restricted license，**使用前需获得 Digital Asset 书面同意**（"prior written consent"）。仅授权用于 TestNet 评估或 MainNet 集成两种特定目的；禁止反向工程、转售、子许可、公开性能测试结果；Digital Asset 保留所有 IP 权利，可随时撤销许可。**结论**: 直接使用 Canton Docker 镜像部署需商业许可，且比一般评估许可更为严格。

### 2.3 License 结论

- **代码分析/借鉴安全区**: `community/` 和 `base/` 下的**大部分核心模块**（participant, synchronizer, base, sequencer-driver, BFT ordering 等）使用 Apache-2.0 header，可自由分析、借鉴、衍生
- **需要逐子项目/逐文件确认**: `community/lib/` 是 mixed bucket（wartremover/magnolify 为 Proprietary，Blake2b 为 BouncyCastle/MIT-like，scalatest/slick 为第三方 fork）；非 community/base 路径下的子项目默认使用 Proprietary header
- **Docker 镜像需商业许可**: 直接部署 Canton Docker 镜像需签署 License Agreement 或限于 TestNet 评估
- **未发现 BSL**: 仓库中没有 Business Source License 的引用（与早期 Daml 版本不同）
- **Mantle 影响**: 借鉴 community/base 下的设计模式和算法安全；直接使用构建产物（Docker、JAR）需额外法律评估

---

## 3. 核心模块实现分析

### 3.1 Participant 节点

#### 3.1.1 入口与启动流程

**入口类**: `CantonCommunityApp` → `CantonAppDriver` → `Runner`

```
community/app/src/main/scala/com/digitalasset/canton/CantonCommunityApp.scala:11
```

`CantonCommunityApp` 是一个极简的 `object`（仅 21 行），继承 `CantonAppDriver`，负责加载配置并选择 `CommunityEnvironmentFactory` 创建运行环境。

**Participant 启动**: `ParticipantNodeBootstrap`

```
community/participant/src/main/scala/com/digitalasset/canton/participant/ParticipantNode.scala:98-120
```

```scala
class ParticipantNodeBootstrap(
    arguments: CantonNodeBootstrapCommonArguments[
      ParticipantNodeConfig,
      ParticipantNodeParameters,
      ParticipantMetrics,
    ],
    replicaManager: ParticipantReplicaManager,
    engine: Engine,  // Daml-LF 引擎实例
    resourceManagementServiceFactory: ...,
    ledgerApiServerBootstrapUtils: LedgerApiServerBootstrapUtils,
    setInitialized: ParticipantServices => Unit,
)(implicit ...)
  extends CantonNodeBootstrapImpl[ParticipantNode, ...](arguments)
```

**关键发现**:
- `ParticipantNodeBootstrap` 接收一个 `Engine`（Daml-LF 引擎）实例，这是 Participant 的核心计算组件
- 继承 `CantonNodeBootstrapImpl`，这是所有节点共享的启动框架
- 内部持有 `CantonSyncService`（核心同步服务）和 `MutablePackageMetadataViewImpl`（包元数据管理）

#### 3.1.2 状态存储层

**持久化状态**: `ParticipantNodePersistentState`

```
community/participant/src/main/scala/com/digitalasset/canton/participant/store/ParticipantNodePersistentState.scala:39-59
```

```scala
class ParticipantNodePersistentState private (
    val settingsStore: ParticipantSettingsStore,           // 参与者设置
    val acsCounterParticipantConfigStore: ...,             // ACS 计数器配置
    val ledgerApiStore: LedgerApiStore,                    // Ledger API 存储
    val inFlightSubmissionStore: InFlightSubmissionStore,   // 进行中的提交追踪
    val commandDeduplicationStore: CommandDeduplicationStore, // 命令去重
    val pruningStore: ParticipantPruningStore,              // 修剪状态
    val contractStore: ContractStore,                       // 合约存储（核心）
    ...
)
```

**合约存储**: `ContractStore` trait + `DbContractStore`（PostgreSQL）/ `InMemoryContractStore`

```
community/common/src/main/scala/com/digitalasset/canton/participant/store/ContractStore.scala
community/common/src/main/scala/com/digitalasset/canton/participant/store/db/DbContractStore.scala
community/common/src/main/scala/com/digitalasset/canton/participant/store/memory/InMemoryContractStore.scala
```

**数据库 migration**: 使用 Flyway，支持 PostgreSQL 和 H2

```
community/common/src/main/resources/db/migration/canton/postgres/  # PostgreSQL migrations
community/common/src/main/resources/db/migration/canton/h2/        # H2 migrations (测试)
```

**验证**: WHI-334/335 描述的 "PostgreSQL 存储 ACS" 与代码完全一致。代码额外确认了 H2 支持（用于测试/开发）。

#### 3.1.3 交易处理流程

交易从提交到确认遵循 Canton Protocol 的多阶段流程，核心类链如下：

```
CantonSyncService (入口)
  → TransactionRoutingProcessor (路由：选择 Synchronizer)
    → TransactionProcessor (协议处理器)
      → ProtocolProcessor (通用协议框架 — Phase 3, 4, 7)
        → TransactionProcessingSteps (交易特定步骤)
          → TransactionTreeFactory (构造 Merkle 交易树)
          → TransactionConfirmationRequestFactory (构造确认请求)
          → ModelConformanceChecker (模型一致性检查)
          → AuthenticationValidator (认证验证)
          → ContractConsistencyChecker (合约一致性检查)
          → TimeValidator (时间验证)
```

**关键代码路径**:

```
community/participant/src/main/scala/com/digitalasset/canton/participant/sync/CantonSyncService.scala
community/participant/src/main/scala/com/digitalasset/canton/participant/protocol/ProtocolProcessor.scala:86-100
community/participant/src/main/scala/com/digitalasset/canton/participant/protocol/TransactionProcessingSteps.scala
community/participant/src/main/scala/com/digitalasset/canton/participant/protocol/submission/TransactionTreeFactory.scala:41-70
```

`ProtocolProcessor` 文档注释（第 86 行）明确说明:

> "The ProtocolProcessor orchestrates Phase 3, 4, and 7 of the synchronization protocol."

**Phase 3**: 接收确认请求 → 解密视图 → 验证 → 发送确认响应
**Phase 4**: 不适用于参与者（Mediator 收集响应）
**Phase 7**: 接收确认结果 → 提交/拒绝

#### 3.1.4 与 Synchronizer 的通信

Participant 通过 `SequencerClient` 与 Synchronizer 通信:

```
community/base/src/main/scala/com/digitalasset/canton/sequencing/client/  # SequencerClient 实现
community/participant/src/main/scala/com/digitalasset/canton/participant/sync/ConnectedSynchronizer.scala
```

所有消息都通过 Sequencer 路由（这与 WHI-335 分析一致：Participant 和 Mediator 不直接通信）。

---

### 3.2 Synchronizer（Sequencer + Mediator）

#### 3.2.1 Sequencer 实现

##### 可插拔 Driver 接口

**核心 trait**: `SequencerDriver`

```
community/sequencer-driver/src/main/scala/com/digitalasset/canton/synchronizer/block/SequencerDriver.scala:133-196
```

```scala
trait SequencerDriver extends AutoCloseable {
  def firstBlockHeight: Long
  def adminServices: Seq[ServerServiceDefinition]

  // 写操作
  def acknowledge(acknowledgement: ByteString)(implicit traceContext: TraceContext): Future[Unit]
  def send(signedOrderingRequest: ByteString, submissionId: String, senderId: String)(
      implicit traceContext: TraceContext
  ): Future[Unit]

  // 读操作
  def subscribe()(implicit traceContext: TraceContext): Source[RawLedgerBlock, KillSwitch]
  def sequencingTime(implicit traceContext: TraceContext): Future[Option[Long]]

  // 健康检查
  def health(implicit traceContext: TraceContext): Future[SequencerDriverHealthStatus]
}
```

**关键设计**:
- `subscribe()` 返回一个 Pekko (formerly Akka) `Source[RawLedgerBlock, KillSwitch]`，以 block 为单位流式传输
- 所有写操作是异步的（`Future[Unit]`），不保证写入即排序
- Driver 负责为 `Send` 事件分配时间戳（必须接近真实世界时间）
- **接口极为精简**：仅 5 个核心方法——这是高度可插拔性的关键

##### Driver 工厂

```
community/sequencer-driver/src/main/scala/com/digitalasset/canton/synchronizer/block/SequencerDriver.scala:20-90
```

```scala
trait SequencerDriverFactory {
  def name: String              // 配置中的标识符，如 "reference"
  def version: Int              // Driver API 版本
  type ConfigType               // Driver 特定的配置类型
  def configParser: ConfigReader[ConfigType]
  def configWriter(confidential: Boolean): ConfigWriter[ConfigType]
  def create(...): SequencerDriver
  def usesTimeProvider: Boolean
}
```

**接口稳定性评估**: `SequencerDriverFactory` 包含 `version: Int` 字段，表明 Digital Asset 有意维护 Driver API 的版本兼容性。`name` 字段用于配置文件中的 driver 选择（如 `type = reference`），这是 plugin 发现机制的一部分。

##### Reference Sequencer Driver（参考实现）

```
community/reference-sequencer-driver/src/main/scala/com/digitalasset/canton/synchronizer/sequencing/sequencer/reference/ReferenceSequencerDriver.scala:54-118
```

```scala
class ReferenceSequencerDriver(
    sequencerId: String,
    store: ReferenceBlockOrderingStore,  // 存储后端
    config: ReferenceSequencerDriver.Config[? <: StorageConfig],
    timeProvider: TimeProvider,
    override val firstBlockHeight: Long,
    storage: Storage,                     // 数据库连接
    ...
) extends SequencerDriver with NamedLogging with FlagCloseableAsync
```

**排序机制**:
- 使用 Pekko Streams `Source.queue` 接收请求
- `groupedWithin(n = config.maxBlockSize, d = config.maxBlockCutMillis.millis)` 批量组装 block
- 时间戳由 `timeProvider.nowInMicrosecondsSinceEpoch` 提供
- 通过 `store.insertRequest` 持久化到数据库
- `subscribe()` 从数据库轮询已排序的 block

**Factory name**: `"reference"`（第 30 行），支持 Memory、H2、PostgreSQL 存储后端

##### 存储后端

```
community/reference-sequencer-driver/src/main/scala/com/digitalasset/canton/synchronizer/sequencing/sequencer/reference/store/ReferenceBlockOrderingStore.scala:22-51
```

```scala
trait ReferenceBlockOrderingStore extends AutoCloseable {
  def insertRequest(request: BlockFormat.OrderedRequest)(implicit traceContext: TraceContext): FutureUnlessShutdown[Unit]
  def maxBlockHeight()(implicit traceContext: TraceContext): FutureUnlessShutdown[Option[Long]]
  def queryBlocks(initialHeight: Long, maxQueryBlockCount: Int)(implicit traceContext: TraceContext): FutureUnlessShutdown[Seq[TimestampedBlock]]
}
```

实现类:
- `InMemoryReferenceSequencerDriverStore` — 内存实现（测试用）
- `DbReferenceBlockOrderingStore` — PostgreSQL/H2 实现（生产用）

工厂方法（第 43-51 行）根据 `Storage` 类型自动选择实现，符合 Canton 一贯的 DB/Memory 双实现模式。

##### Block 数据结构

```
community/sequencer-driver/src/main/scala/com/digitalasset/canton/synchronizer/block/SequencerDriver.scala:233-261
```

```scala
final case class RawLedgerBlock(
    blockHeight: Long,
    baseSequencingTimeMicrosFromEpoch: Long,
    events: Seq[Traced[RawLedgerBlock.RawBlockEvent]],
    tickTopologyAtMicrosFromEpoch: Option[Long] = None,
)

sealed trait RawBlockEvent extends Product with Serializable {
    val microsecondsSinceEpoch: Long
}

object RawBlockEvent {
    final case class Send(request: ByteString, microsecondsSinceEpoch: Long, ...) extends RawBlockEvent
    final case class Acknowledgment(acknowledgement: ByteString, ...) extends RawBlockEvent
}
```

**Block 抽象澄清**: Canton 的 `RawLedgerBlock` 是 **sequencer/orderer 层的排序批次抽象**（block height + events sequence），**不是** Ethereum 式的全局执行 block（没有全局状态根、gas 计算、全节点执行语义）。WHI-335 中 "no block concept" 的表述指的是 Canton 没有 Ethereum-style globally executed block semantics——交易不需要全局排序和全局执行。但 sequencer backend 确实使用 block/batch 抽象来组织排序输出，这是两个不同层面的概念。

##### Block 处理管线（Sequencer 后处理）

Sequencer 收到 driver 产生的 blocks 后，进行后处理:

```
community/synchronizer/src/main/scala/com/digitalasset/canton/synchronizer/block/update/
  ├── BlockChunkProcessor.scala        # 逐 chunk 处理
  ├── BlockReorderer.scala             # 重排序（修正 driver 时间戳）
  ├── BlockUpdate.scala                # 更新类型定义
  ├── BlockUpdateGenerator.scala       # 生成更新
  ├── SequencedSubmissionsValidator.scala # 验证已排序的提交
  ├── SubmissionRequestValidator.scala # 验证提交请求
  └── TrafficControlValidator.scala    # 流量控制
```

```
community/synchronizer/src/main/scala/com/digitalasset/canton/synchronizer/block/BlockSequencerStateManager.scala:73-80
```

`BlockSequencerStateManagerBase` trait（第 76 行）提供了状态管理的核心抽象:

```scala
trait BlockSequencerStateManagerBase extends FlagCloseable {
  def getHeadState: HeadState
  // Flow to turn BlockEvents into OrderedBlockUpdates
}
```

**崩溃恢复机制**: `BlockSequencerStateManager` 使用 `AtomicReference[HeadState]`（第 59 行）跟踪当前状态。`HeadState` 包含最新 block 信息和 ephemeral state。重启时从 `SequencerBlockStore` 加载最新持久化状态，重建 ephemeral state。注释（第 65-71 行）明确说明：如果 ephemeral state 与持久化状态不一致，sequencer 需要重启。

**Driver 变体**:
- **Reference Driver**: `community/reference-sequencer-driver/`，单节点 DB-backed，用于开发和测试
- **BFT Block Orderer**: `community/synchronizer/src/.../bftordering/`，完整的多节点 BFT 共识实现（Apache-2.0），包含 `BftSequencerFactory`、`BftBlockOrderer`、ISS 共识模块、P2P gRPC 网络层、Mempool、Availability 模块等（详见 §3.2.3）
- **Fabric/Ethereum Drivers**: 代码注释（`SequencerDriver.scala:96-97`）提到 "The Fabric and Ethereum drivers have separate entry points"，但这些 driver 不在本仓库中

##### Sequencer 代码质量评估

| 维度 | 评估 | 证据 |
|------|------|------|
| **接口稳定性** | 高 | `SequencerDriverFactory.version` 字段表明有版本管理意识 |
| **文档质量** | 优秀 | `SequencerDriver` trait 有 ~100 行 ScalaDoc，覆盖时间戳要求、异常处理、生命周期 |
| **可插拔性** | 极高 | 仅需实现 5 个方法 + 1 个 factory；接口与实现完全分离到不同 sbt 子项目 |
| **测试信号** | 有测试目录 | `community/reference-sequencer-driver/src/test/` 存在；`community/synchronizer/src/test/` 下有 block 处理测试 |
| **Extension 点** | 清晰 | `SequencerDriver` trait + `SequencerDriverFactory` 是唯一的扩展点 |
| **已知限制** | Reference driver 为单节点 | 无 BFT、无分布式排序、无 block 传播——仅适合开发和测试 |

#### 3.2.2 BFT Block Ordering 实现（开源）

Canton 仓库中包含完整的 BFT block ordering 实现，位于 `community/synchronizer/src/.../bftordering/`，全部使用 Apache-2.0 header。

**核心入口**:

```
community/synchronizer/src/main/scala/com/digitalasset/canton/synchronizer/sequencer/block/bftordering/
  ├── bindings/canton/sequencing/
  │   ├── BftSequencerFactory.scala:42-66    # BlockSequencerFactory 子类
  │   └── BftBlockOrderer.scala:1-80         # BlockOrderer 实现，含 P2P 网络、Pekko module system
  ├── bindings/p2p/grpc/                     # P2P gRPC 网络层
  ├── bindings/pekko/                        # Pekko actor system 绑定
  ├── core/
  │   ├── BftOrderingModuleSystemInitializer.scala:88-119  # 模块系统初始化器
  │   ├── BftBlockOrdererConfig.scala         # BFT 配置
  │   ├── modules/
  │   │   ├── availability/                   # 数据可用性模块 + AvailabilityStore
  │   │   ├── consensus/iss/                  # ISS 共识协议实现 + EpochStore
  │   │   ├── mempool/                        # 内存池模块
  │   │   ├── output/                         # 输出模块 + OutputMetadataStore
  │   │   ├── p2p/                            # P2P 网络模块 + P2PEndpointsStore
  │   │   └── pruning/                        # 修剪模块
  │   └── integration/canton/                 # Canton 集成层
  └── framework/                              # BFT ordering 通用框架
```

**`BftSequencerFactory`** (`BftSequencerFactory.scala:42-66`): 继承 `BlockSequencerFactory`，覆盖 `createBlockOrderer()` 创建 BFT block orderer。使用 `OrderingTimeFixMode.ValidateOnly`（第 72-73 行），表明 BFT orderer 自行管理时间戳。

**`BftOrderingModuleSystemInitializer`** (`BftOrderingModuleSystemInitializer.scala:88-119`): 泛型模块系统初始化器，初始化以下子模块:
- `MempoolModule` — 内存池
- `AvailabilityModule` — 数据可用性（含 `AvailabilityStore`）
- `PreIssConsensusModule` — ISS BFT 共识协议（代码中命名为 `PreIssConsensusModule`，位于 `core/modules/consensus/iss/`）
- `OutputModule` — 排序输出（含 `OutputMetadataStore`, `EpochStore`）
- `P2PNetworkInModule` / `P2PNetworkOutModule` — P2P 网络
- `PruningModule` — 数据修剪
- `LeaderSelectionInitializer` — leader 选择（含黑名单策略 `BlacklistLeaderSelectionPolicyState`）

**BFT 特有持久化存储**: `AvailabilityStore`, `EpochStore`, `OutputMetadataStore`, `P2PEndpointsStore`, `BftOrdererPruningSchedulerStore`

**成熟度评估**: BFT ordering 实现在 community/ 下以 Apache-2.0 发布，代码结构完整（共识、可用性、网络、修剪各层独立），但需注意:
- 实现用于 Canton Network Global Synchronizer 场景，生产部署情况需进一步调研
- 依赖 Canton 的 topology provider 和 crypto provider
- 使用 Pekko actor 模型和自定义模块框架（`Module[E]`, `ModuleSystem[E]`）

#### 3.2.3 Mediator 实现

##### 核心类

```
community/synchronizer/src/main/scala/com/digitalasset/canton/synchronizer/mediator/Mediator.scala:85-108
```

```scala
private[mediator] class Mediator(
    val mediatorId: MediatorId,
    val sequencerClient: RichSequencerClient,
    val topologyClient: SynchronizerTopologyClientWithInit,
    private[canton] val syncCrypto: SynchronizerCryptoClient,
    topologyTransactionProcessor: TopologyTransactionProcessor,
    val topologyManager: SynchronizerTopologyManager,
    ...
    val state: MediatorState,            // 持久化状态
    asynchronousProcessing: Boolean,     // 异步/同步处理模式
    ...
)
```

**关键文档注释**（第 61-84 行）清楚描述了崩溃恢复机制:

> "The mediator is crash-fault tolerant: if it crashes before finalizing a request, crash recovery replays that request from the sequenced event store."

**已知限制**:
> "There is a narrow crash window between persisting the finalized response and confirming the verdict was sequenced. If the mediator crashes after storeFinalized but before the verdict send completes, on restart the verdict may not be re-sent."

##### MediatorState — 状态管理深度分析

```
community/synchronizer/src/main/scala/com/digitalasset/canton/synchronizer/mediator/store/MediatorState.scala:44-66
```

```scala
private[mediator] class MediatorState(
    val finalizedResponseStore: FinalizedResponseStore,   // 持久化层
    val deduplicationStore: MediatorDeduplicationStore,    // 去重
    val clock: Clock,
    val metrics: MediatorMetrics,
    protocolVersion: ProtocolVersion,
    ...
) extends NamedLogging with FlagCloseable {

  // outstanding requests are kept in memory while finalized requests will be stored
  private val pendingRequests =
    new ConcurrentSkipListMap[RequestId, ResponseAggregation[?]](implicitly[Ordering[RequestId]])

  private val participantResponseTimeouts = mutable.SortedMultiDict[CantonTimestamp, RequestId]()
}
```

**关键设计决策**:
1. **Pending 请求仅在内存**（`ConcurrentSkipListMap`）：如果 Mediator 崩溃，未完成的请求直接丢失，参与者超时后重试。这是有意为之的 crash-fault tolerance 策略。
2. **Finalized 请求持久化**（`FinalizedResponseStore`）：已完成的裁定写入数据库，用于审计和崩溃恢复。
3. `ConcurrentSkipListMap` 优化了 `fetchPendingRequestIdsBefore` 操作（用于超时扫描）。

**`FinalizedResponseStore`**（`community/synchronizer/src/main/scala/com/digitalasset/canton/synchronizer/mediator/store/FinalizedResponseStore.scala:40-57`）:

```scala
private[mediator] trait FinalizedResponseStore extends AutoCloseable {
  def store(finalizedResponse: FinalizedResponse)(implicit ...): FutureUnlessShutdown[Unit]
  def fetch(requestId: RequestId)(implicit ...): OptionT[FutureUnlessShutdown, FinalizedResponse]
}
```

- 有 DB 实现（PostgreSQL/H2）和 Memory 实现
- 幂等存储：相同 requestId 重复 store 不会出错（支持崩溃恢复重放）
- `@VisibleForTesting` 标注在 `MediatorState` 第 31 行，表明可测试性被显式考虑

##### 确认请求处理（两阶段提交核心）

**核心类**: `ConfirmationRequestAndResponseProcessor`

```
community/synchronizer/src/main/scala/com/digitalasset/canton/synchronizer/mediator/ConfirmationRequestAndResponseProcessor.scala:53-69
```

**处理流程**:

1. **接收请求** (Phase 2): `processRequest()` (第 246-349 行)
   - 验证请求（`validateRequest`）
   - 创建 `ResponseAggregation` 初始状态
   - 注册超时 (`registerTimeoutForRequest`)
   - 如果是零阈值请求，立即完成
   - 记录 `registerPendingRequest` 到 `MediatorState`

2. **接收响应** (Phase 4): `processResponses()` (第 161-180 行)
   - 通过 `processingQueue.enqueueForProcessing` 确保按请求 ID 串行处理
   - 调用 `ResponseAggregation.validateAndProgressInternal` 验证并更新状态

3. **超时处理** (Phase 6): `handleTimeout()` (第 202-232 行)
   - 检查 `pendingTimedoutRequest`
   - 调用 `responseAggregation.timeout`
   - 通过 `sendResultIfDone` 发送最终裁定

4. **发送裁定**: `VerdictSender.sendResult()` → 通过 Sequencer 广播

**关键代码** — 事件分派:

```scala
// ConfirmationRequestAndResponseProcessor.scala:132-180
event match {
  case MediatorEvent.Request(counter, _, requestEnvelope, rootHashMessages, ...) =>
    processRequest(requestId, counter, participantResponseDeadline, decisionTime, ...)
  case MediatorEvent.Response(counter, responseTimestamp, responses, ...) =>
    processResponses(responseTimestamp, counter, ...)
}
```

##### 响应聚合

**核心类**: `ResponseAggregation`

```
community/synchronizer/src/main/scala/com/digitalasset/canton/synchronizer/mediator/ResponseAggregation.scala:58-72
```

```scala
final case class ResponseAggregation[VKEY](
    override val requestId: RequestId,
    override val request: MediatorConfirmationRequest,
    responseTimeout: CantonTimestamp,
    decisionTime: CantonTimestamp,
    override val version: CantonTimestamp,
    state: Either[MediatorVerdict, Map[VKEY, ViewState]],  // Left=已完成, Right=待确认
    finalizedPromise: PromiseUnlessShutdown[Unit],
)
```

**Quorum 机制**（第 100-110 行）:

```scala
private def quorumsSatisfied(quorums: Seq[Quorum]): Boolean =
  quorums.forall(_.threshold.unwrap == 0)

private def quorumsCanBeSatisfied(quorums: Seq[Quorum]): Boolean =
  quorums.forall(quorum =>
    quorum.threshold.unwrap <= quorum.confirmers.map { case (_, weight) => weight.unwrap }.sum
  )
```

**Mediator 如何验证交易而不看内容**:
- Mediator 收到的是 `MediatorConfirmationRequest`，包含**每个 view 的确认参数**（informees、quorum 要求），但**不包含交易内容**
- 参与者发送 `ConfirmationResponse`（approve/reject），Mediator 只需按 view 聚合这些响应
- Mediator 通过 `ViewConfirmationParameters`（含 informees 和 quorums）判断是否达到确认阈值
- **加密**: 交易内容通过 `EncryptedViewMessage` 分发，Mediator 看不到明文

##### Mediator 代码质量评估

| 维度 | 评估 | 证据 |
|------|------|------|
| **崩溃容错** | 有限但有意为之 | Pending 请求在内存，崩溃丢失→参与者超时。已知 narrow crash window 在 `Mediator.scala:79-83` 记录 |
| **并发安全** | 好 | `ConcurrentSkipListMap` + `processingQueue.enqueueForProcessing` 串行化 |
| **状态持久化** | Finalized only | `FinalizedResponseStore` 幂等，支持崩溃后重放 |
| **Extension 点** | `VerdictSender` trait | `VerdictSender.scala:37-66` 定义了可替换的裁定发送接口 |
| **可测试性** | 好 | `@VisibleForTesting` 标注；DB/Memory 双实现 |
| **实现复杂度** | 中等 | ~1500 行核心代码，逻辑清晰但涉及异步流和 Peano queue |

---

### 3.3 隐私层

#### 3.3.1 Merkle Tree 数据结构

**核心 trait**: `MerkleTree[+A]`

```
community/base/src/main/scala/com/digitalasset/canton/data/MerkleTree.scala:34-57
```

```scala
trait MerkleTree[+A] extends Product with Serializable with PrettyPrinting {
  def subtrees: Seq[MerkleTree[?]]
  def rootHash: RootHash
  def unwrap: Either[RootHash, A]  // Left = blinded（只有哈希）, Right = unblinded（有完整内容）
  lazy val blindFully: MerkleTree[A] = BlindedNode[A](rootHash)

  final def blind(blindingPolicy: PartialFunction[MerkleTree[?], BlindingCommand]): MerkleTree[A]
}
```

**Blinding 命令**:
- `BlindSubtree`: 盲化整个子树（只留哈希）
- `RevealSubtree`: 完全展示子树
- `RevealIfNeedBe`: 仅在有需要的后代时展示

**关键设计**: `blind()` 方法（第 68-116 行）使用了优化的 blinding policy:
1. 先遍历整棵树，将 `RevealIfNeedBe` 优化为 `BlindSubtree` 或 `RevealSubtree`
2. 对叶子节点可以 O(1) 盲化
3. 优化后避免了不必要的节点复制

#### 3.3.2 交易树结构

**核心类**: `GenTransactionTree`

```
community/base/src/main/scala/com/digitalasset/canton/data/GenTransactionTree.scala:40-100
```

```scala
final case class GenTransactionTree private (
    submitterMetadata: MerkleTree[SubmitterMetadata],     // 提交者元数据
    commonMetadata: MerkleTree[CommonMetadata],           // 公共元数据（所有方可见）
    participantMetadata: MerkleTree[ParticipantMetadata], // 参与者元数据
    rootViews: MerkleSeq[TransactionView],                // 根级视图列表
)(hashOps: HashOps) extends MerkleTreeInnerNode[GenTransactionTree](hashOps)
```

这是整个交易的 Merkle 树根结构。关键约束（第 48-73 行）:
- 所有子树的哈希必须唯一（`checkUniqueHashes`）
- `commonMetadata` 不能被盲化

#### 3.3.3 TransactionView（交易视图）

```
community/base/src/main/scala/com/digitalasset/canton/data/TransactionView.scala:43-51
```

```scala
final case class TransactionView private (
    viewCommonData: MerkleTree[ViewCommonData],           // 所有成员可见的数据
    viewParticipantData: MerkleTree[ViewParticipantData], // 所有参与者可见的数据
    subviews: TransactionSubviews,                        // 子视图
)(hashOps, representativeProtocolVersion) extends MerkleTreeInnerNode[TransactionView](hashOps)
```

**ViewCommonData** (`community/base/src/.../data/ViewCommonData.scala:24-60`): 包含 `ViewConfirmationParameters`（informees + quorums）和 salt

**ViewParticipantData** (`community/base/src/.../data/ViewParticipantData.scala:47-60`): 包含 `coreInputs`（输入合约）、`createdCore`（创建的合约）、`ActionDescription`（操作描述）

#### 3.3.4 视图加密与分发

**加密**: `EncryptedViewMessage`

```
community/base/src/main/scala/com/digitalasset/canton/protocol/messages/EncryptedViewMessage.scala:60-120
```

加密流程（`EncryptedView.compressed`，第 105-120 行）:
1. 视图先压缩（`CompressedView`）
2. 使用对称密钥加密（`SymmetricKey`）
3. 对称密钥使用接收方的公钥加密分发

**视图树生成**: `TransactionTreeFactory.createTransactionTree()`

```
community/participant/src/main/scala/com/digitalasset/canton/participant/protocol/submission/TransactionTreeFactory.scala:55-70
```

**不同参与方获得不同子树**: `GenTransactionTree.tryBlindForTransactionViewTree(viewPos)`

```
community/base/src/main/scala/com/digitalasset/canton/data/GenTransactionTree.scala:113-120
```

```scala
private[canton] def tryBlindForTransactionViewTree(viewPos: ViewPositionFromRoot): GenTransactionTree =
  viewPos.position match {
    case (head: MerkleSeqIndexFromRoot) +: tail =>
      val sm = if (viewPos.isTopLevel) submitterMetadata else submitterMetadata.blindFully
      val rv = rootViews.tryBlindAllButLeaf(head, ...)
      ...
  }
```

每个参与方只能看到自己是 informee 的 view 的内容，其他 view 被盲化为哈希。

**`FullTransactionViewTree`**: 恰好有一个 view 是完整展开的
**`LightTransactionViewTree`**: 更紧凑的表示，用于传输

---

### 3.4 Daml 引擎集成

#### 3.4.1 DAMLe — Daml-LF 引擎包装器

```
community/participant/src/main/scala/com/digitalasset/canton/participant/util/DAMLe.scala:42-79
```

`DAMLe` 是 Canton 对 `com.digitalasset.daml.lf.engine.Engine` 的包装:

```scala
object DAMLe {
  def newEngine(
      enableLfDev: Boolean,
      enableLfBeta: Boolean,
      enableStackTraces: Boolean,
      profileDir: Option[Path] = None,
      snapshotDir: Option[Path] = None,
      iterationsBetweenInterruptions: Long = 10000,
      paranoidMode: Boolean,
      submissionPhaseLogging: EngineLoggingConfig,
      validationPhaseLogging: EngineLoggingConfig,
      loggerFactory: NamedLoggerFactory,
  ): Engine = new Engine(EngineConfig(...), loggerFactory)
}
```

**Engine 配置关键参数**:
- `packageValidation = false`: 包已预验证，加载时跳过验证
- `forbidLocalContractIds = true`: 禁止本地 contract ID（Canton 使用全局唯一 ID）
- `iterationsBetweenInterruptions = 10000`: 执行中断检查间隔
- `paranoid = paranoidMode`: 严格模式

#### 3.4.2 Re-interpretation 验证模式

```
community/participant/src/main/scala/com/digitalasset/canton/participant/util/DAMLe.scala:114-132
```

```scala
trait HasReinterpret {
  def reinterpret(
      contracts: ReplayContractLookup,
      contractAuthenticator: ContractAuthenticatorFn,
      submitters: Set[LfPartyId],
      command: LfCommand,
      topologySnapshot: TopologySnapshot,
      ledgerTime: CantonTimestamp,
      preparationTime: CantonTimestamp,
      rootSeed: Option[LfHash],
      packageResolution: Map[Ref.PackageName, Ref.PackageId],
      expectFailure: Boolean,
      getEngineAbortStatus: GetEngineAbortStatus,
  )(implicit traceContext: TraceContext): EitherT[FutureUnlessShutdown, ReinterpretationError, ReInterpretationResult]
}
```

Canton 使用 "reinterpret" 模式:
1. 提交方解释（interpret）命令，生成交易
2. 验证方通过 `reinterpret` 重新执行相同命令，验证结果一致性
3. `reinterpret` 需要 `ReplayContractLookup`（合约查找）、`TopologySnapshot`（拓扑快照）和 `ContractAuthenticatorFn`（合约认证）

#### 3.4.3 授权检查

授权检查分布在多个验证器中:

```
community/participant/src/main/scala/com/digitalasset/canton/participant/protocol/validation/
  ├── AuthenticationValidator.scala    # 认证验证（签名检查）
  ├── ModelConformanceChecker.scala    # 模型一致性（通过 re-interpretation）
  ├── ContractConsistencyChecker.scala # 合约一致性
  └── TimeValidator.scala             # 时间有效性
```

Daml-LF 引擎本身实现了内置的授权模型:
- 每个 action 要求特定的 authorization parties
- `signatories` 和 `observers` 由合约模板定义
- `controllers` 由 choice 定义
- 引擎在解释时自动检查授权约束

---

## 4. Topology Manager 代码映射

### 4.1 核心类与文件

WHI-335 描述的拓扑管理（§1.5）在代码中有完整实现。核心入口:

```
community/base/src/main/scala/com/digitalasset/canton/topology/TopologyManager.scala:1-80
```

`TopologyManager` 类依赖链（从 imports 提取）:

| WHI-335 概念 | 代码实现 | 文件路径 |
|-------------|---------|---------|
| **Topology Manager** | `TopologyManager` class | `community/base/.../topology/TopologyManager.scala` |
| **Topology Transaction Processor** | `TopologyTransactionProcessor` class | `community/base/.../topology/processing/TopologyTransactionProcessor.scala:64-78` |
| **Topology State Processor** | `TopologyStateProcessor` trait + `TopologyStateProcessorImpl` | `community/base/.../topology/processing/TopologyStateProcessor.scala:31-80` |
| **命名空间委托 (NSD)** | `NamespaceDelegation` case in `TopologyMapping.Code` | `TopologyMapping.scala:167-168` |
| **去中心化命名空间** | `DecentralizedNamespaceDefinition` | `TopologyMapping.scala:170` |
| **Party-to-Participant 映射** | `PartyToParticipant` | `TopologyMapping.scala:183-184` |
| **Package Vetting** | `VettedPackages` | `TopologyMapping.scala:181` |
| **Owner-to-Key 映射** | `OwnerToKeyMapping` | `TopologyMapping.scala:172-173` |
| **Synchronizer 信任证书** | `SynchronizerTrustCertificate` | `TopologyMapping.scala:175-176` |
| **Participant 权限** | `ParticipantSynchronizerPermission` | `TopologyMapping.scala:177-178` |
| **Mediator 状态** | `MediatorSynchronizerState` | `TopologyMapping.scala:188-189` |
| **Sequencer 状态** | `SequencerSynchronizerState` | `TopologyMapping.scala:190-191` |
| **Synchronizer 参数** | `SynchronizerParametersState` | `TopologyMapping.scala:186-187` |
| **Party-to-Key 映射** | `PartyToKeyMapping` | `TopologyMapping.scala:195-196` |

### 4.2 拓扑交易处理管线

```
TopologyTransactionProcessor (sequencer 事件消费者)
  → TopologyStateProcessor.validateAndApplyAuthorization()
    → 验证签名链完整性
    → 检查序列号递增
    → 检查授权（RequiredAuth）
    → 通过 TopologyMappingChecks 执行额外验证
    → 写入 TopologyStore
    → 通过 TopologyStateWriteThroughCache 更新缓存
```

`TopologyStateProcessor.validateAndApplyAuthorization()` 签名（第 46-55 行）明确了核心验证参数:
- `expectFullAuthorization`: 是否要求完整授权（vs 提案）
- `relaxChecksForBackwardsCompatibility`: 向后兼容降级模式
- `storeIsEmpty`: 创世时间戳优化

### 4.3 所有拓扑映射类型一览

```scala
// TopologyMapping.scala:165-199 — 完整的拓扑映射代码注册表
object Code {
  case object NamespaceDelegation                    // nsd — 命名空间委托
  case object DecentralizedNamespaceDefinition       // dnd — 去中心化命名空间
  case object OwnerToKeyMapping                      // otk — 密钥持有者映射
  case object SynchronizerTrustCertificate           // dtc — Synchronizer 信任证书
  case object ParticipantSynchronizerPermission       // pdp — Participant 权限
  case object PartyHostingLimits                     // phl — Party 托管限制
  case object VettedPackages                         // vtp — 审核通过的包
  case object PartyToParticipant                     // ptp — Party→Participant 映射
  case object SynchronizerParametersState            // dop — Synchronizer 参数
  case object MediatorSynchronizerState              // mds — Mediator 状态
  case object SequencerSynchronizerState             // sds — Sequencer 状态
  case object SequencingDynamicParametersState        // sep — 动态排序参数
  case object PartyToKeyMapping                      // ptk — Party→Key 映射
  case object LsuAnnouncement                        // lsu — LSU 公告
}
```

每种映射类型有唯一的 `dbInt` 值用于数据库索引，`code` 字符串用于日志和调试。

### 4.4 Package Vetting Enforcement Path

WHI-335 描述的 Package Vetting 不仅是一个 topology 定义，还有完整的 enforcement 管线。以下是从交易提交到拒绝的完整代码路径：

**入口点**: `TransactionConfirmationRequestFactory.scala:134` 设置 `validatePackageVettings = true`，触发 transaction tree factory 在构建确认请求时调用 package vetting 检查。同样，`LegacyTransactionTreeFactory.scala:182` 在 `validatePackageVettings` 为 true 时调用 `UsableSynchronizers.checkPackagesVetted()`。

**Phase 1（提交前检查）**: `UsableSynchronizers.check()` → `checkPackagesVetted()`

```
community/participant/src/main/scala/com/digitalasset/canton/participant/protocol/submission/UsableSynchronizers.scala:44-108
```

`UsableSynchronizers.check()` 在 Participant 提交交易前执行 5 项检查（第 102-108 行），其中 `packageVetted` 是第一项:

```scala
for {
  _ <- packageVetted.leftWiden[SynchronizerNotUsedReason]      // 1. Package vetting 检查
  _ <- partiesConnected.leftWiden[SynchronizerNotUsedReason]   // 2. Party 连通性检查
  _ <- partiesWithConfirmingParticipant.leftWiden[...]          // 3. 确认方检查
  _ <- compatibleProtocolVersion.leftWiden[...]                 // 4. 协议版本检查
  _ <- compatibleInteractiveSubmissionVersion                   // 5. 交互提交版本检查
} yield ()
```

**`checkPackagesVetted()` 详细流程** (`UsableSynchronizers.scala:222-252`):

1. 通过 `Blinding.partyPackages(transaction)` 提取每个 party 所需的 package 集合
2. `resolveParticipants()` 将 party→packages 映射转换为 participant→packages 映射
3. 对每个 participant 调用 `TopologySnapshot.loadUnvettedPackagesOrDependencies()`（第 180 行）
4. 如果存在未审核的 package，返回 `UnknownPackage` 错误，交易无法在该 Synchronizer 上提交

**错误类型**: `UnknownPackage(synchronizerId: PhysicalSynchronizerId, unknownTo: List[PackageUnknownTo])`（`UsableSynchronizers.scala:287-290`）— 精确标识哪个 package 在哪个 participant 上未被 vet。注: case class field type 是 `List[PackageUnknownTo]`；non-empty 约束在构造处通过 `NonEmpty.from(u).map(UnknownPackage(...))` 保证（第 251 行）

**关键注释**（第 203-221 行）解释了 Phase 1 和 Phase 3 的不同保证:
- Phase 1: 提交 participant 托管 authorizer，看到完整交易，因此需要所有 package
- Phase 3: participant 收到投影，只需该投影涉及的 package

**完整 enforcement 覆盖**:
- **Submission 侧**: `TransactionConfirmationRequestFactory.scala:134`（`validatePackageVettings = true`）触发 `LegacyTransactionTreeFactory.scala:182` 和 `NextGenTransactionTreeFactory.scala:158` 中对 `UsableSynchronizers.checkPackagesVetted()` 的调用——两种 tree factory 实现均覆盖
- **Validation 侧**: `ModelConformanceChecker.scala:404` 调用 `snapshot.loadUnvettedPackagesOrDependencies(p, packageIds, ledgerTime)`，对每个 participant 逐一检查；第 408 行：`Either.cond(combined.isEmpty, (), UnvettedPackages(combined))` 产生 `UnvettedPackages` validation error

**完整 enforcement 路径**: Submission factory（`validatePackageVettings = true`）→ Transaction tree factory（`checkPackagesVetted()`）→ `UsableSynchronizers`（topology 查询）→ `UnknownPackage` error ‖ `ModelConformanceChecker`（validation 侧）→ `loadUnvettedPackagesOrDependencies` → `UnvettedPackages` error

---

### 4.5 Metadata Leakage 分析

WHI-335 描述的 Sequencer-Mediator 角色分离隐含一个重要隐私边界：**Sequencer 虽然看不到交易内容，但可以观测到哪些元数据**。以下基于源码分析 Sequencer 的可见面。

#### Sequencer 可见数据（通过 `SequencerDriver.send()` 接口）

```
community/sequencer-driver/src/.../SequencerDriver.scala:151-164
```

```scala
def send(signedOrderingRequest: ByteString, submissionId: String, senderId: String)(
    implicit traceContext: TraceContext
): Future[Unit]
```

| 数据项 | Sequencer 可见性 | 代码证据 |
|--------|----------------|---------|
| **senderId** (提交 member ID) | ✅ 可见 | `SequencerDriver.send()` 第三个参数 `senderId: String`；对应 `SubmissionRequest.sender: Member`（`SubmissionRequest.scala:47`） |
| **submissionId** (消息 ID) | ✅ 可见 | `SequencerDriver.send()` 第二个参数 `submissionId: String`；对应 `SubmissionRequest.messageId: MessageId`（`SubmissionRequest.scala:48`） |
| **signedOrderingRequest** (序列化签名请求) | ✅ 可见且可解析 | 第一个参数 `ByteString`——实际是序列化的 `SignedSubmissionRequest`（`DriverBlockOrderer.scala:50` 调用 `signedSubmissionRequest.toByteString`），orderer 可从中提取 request-level metadata（sender, messageId, batch recipients, maxSequencingTime, topologyTimestamp, aggregationRule, submissionCost）。**注意**: 这不是加密 blob，而是签名的明文请求；加密仅在 batch 内的 `EncryptedViewMessage` envelope 层 |
| **maxSequencingTime** | ✅ 可见 | `SubmissionRequest.maxSequencingTime: CantonTimestamp`（`SubmissionRequest.scala:50`）——请求的最大排序时间上限 |
| **topologyTimestamp** | ✅ 可见（可选） | `SubmissionRequest.topologyTimestamp: Option[CantonTimestamp]`（`SubmissionRequest.scala:51`） |
| **aggregationRule** | ✅ 可见（可选） | `SubmissionRequest.aggregationRule: Option[AggregationRule]`（`SubmissionRequest.scala:52`）——聚合规则 |
| **submissionCost** | ✅ 可见（可选） | `SubmissionRequest.submissionCost: Option[SequencingSubmissionCost]`（`SubmissionRequest.scala:53`）——流量控制 |
| **消息大小** | ✅ 可推断 | 从 `ByteString` 长度 |
| **排序时间戳** | ✅ 可见 | Driver 自行分配 `microsecondsSinceEpoch`（`SequencerDriver.scala:92-132` 注释详述时间戳要求） |
| **收件人列表** | ✅ 可见 | `SubmissionRequest.batch: Batch[ClosedEnvelope]`（`SubmissionRequest.scala:49`）中每个 envelope 的 `Recipients`（Sequencer 需要知道向谁投递）；`BlockUpdateGenerator.scala:329` 也通过 `signedOrderingRequest.content.batch.allRecipients` 访问 |
| **交易内容** | ❌ 不可见 | 加密在 `EncryptedViewMessage` 中 |
| **合约状态** | ❌ 不可见 | 仅在 Participant 本地 |
| **Daml 提交者 party** | ❌ 不可见 | 嵌套在加密的 `SubmitterMetadata` 中 |
| **业务逻辑** | ❌ 不可见 | Daml 代码执行仅在 Participant |

#### 隐私边界小结

**Sequencer/Orderer 可获取的信息**:
- 完整的 request-level metadata：sender member ID, message ID, max sequencing time, topology timestamp, aggregation rule, submission cost
- 每个 envelope 的收件人列表（`Recipients`）——即哪个 member 向哪些 member 发送了消息
- 消息的频率、大小和时间模式
- 通信拓扑图（谁与谁频繁通信）
- Batch 结构：envelope 数量和各 envelope 大小

**Sequencer/Orderer 不能获取的信息**:
- envelope 内的 `EncryptedViewMessage` 内容——交易的具体内容（合约创建/行使/归档）被加密
- 涉及的 Daml party 身份（party ≠ participant member，party 信息在 `SubmitterMetadata` 中被加密）
- 金额、资产类型等业务数据（在加密的 view payload 中）

**对 Mantle 的启示**: 这种 metadata leakage 模型类似于 TLS/HTTPS 的加密模型——内容加密但流量分析仍可能泄露信息。Mantle 设计企业隐私层时需要明确这一边界，并考虑是否需要额外的 traffic padding 或 mixnet 来对抗流量分析。

---

## 5. Reassignment（跨 Synchronizer 重新分配）代码映射

WHI-335 §1.4 描述的重新分配机制在代码中有完整实现:

```
community/participant/src/main/scala/com/digitalasset/canton/participant/protocol/reassignment/
  ├── UnassignmentProcessingSteps.scala  # Unassign 处理步骤
  ├── AssignmentProcessingSteps.scala    # Assign 处理步骤
  ├── ReassignmentProcessingSteps.scala  # 共享基类
  └── ReassignmentCoordination.scala     # 跨 Synchronizer 协调
```

**UnassignmentProcessingSteps** (`UnassignmentProcessingSteps.scala:1-60`):
- 包名 `com.digitalasset.canton.participant.protocol.reassignment`
- 依赖 `ActiveContractStore` 的状态枚举: `Active`, `Archived`, `Purged`, `ReassignedAway`（第 44-49 行）
- 使用 `Source[PhysicalSynchronizerId]` / `Target[PhysicalSynchronizerId]` 类型标签区分源/目标 Synchronizer

**AssignmentProcessingSteps** (`AssignmentProcessingSteps.scala:57-60`):
- `val psid: Target[PhysicalSynchronizerId]` — 目标 Synchronizer 标识
- 依赖 `ReassignmentCoordination` 进行跨 Synchronizer 状态协调
- 依赖 `ContractValidator` 验证合约有效性

**关键发现**: 代码中使用 `ReassignmentTag.{Source, Target}` phantom 类型（第 48 行 import）在编译时区分源和目标 Synchronizer，防止参数传递错误。这是 Canton 类型安全设计哲学的又一例证。

---

## 6. ACS Commitments 代码映射

WHI-335 §1.3 描述的 ACS 承诺机制在代码中有深度实现:

### 6.1 存储层

```
community/participant/src/main/scala/com/digitalasset/canton/participant/store/AcsCommitmentStore.scala:32-60
```

```scala
trait AcsCommitmentStore extends AcsCommitmentLookup with PrunableByTime with AutoCloseable {
  def storeComputed(items: NonEmpty[Seq[ParticipantCommitmentData]])(implicit ...): FutureUnlessShutdown[Unit]
  def markOutstanding(periods: NonEmpty[immutable.Iterable[CommitmentPeriod]], counterParticipants: NonEmpty[Set[ParticipantId]])(implicit ...): FutureUnlessShutdown[Unit]
}
```

### 6.2 处理器

```
community/participant/src/main/scala/com/digitalasset/canton/participant/pruning/AcsCommitmentProcessor.scala:1-80
```

`AcsCommitmentProcessor` 是一个大型类（~80 行 imports），实现了:
- 定期计算本地 ACS 承诺
- 与 counter-participants 交换承诺
- 检测不一致（`AcsCommitmentAlarm`，第 60 行）
- 支持 catch-up 参数（`AcsCommitmentsCatchUpParameters`，第 76 行）
- 集成健康检查（`AtomicHealthComponent`，第 47 行）

**关键发现**: ACS Commitment 处理器是 `AcsChangeListener`（第 57 行），它监听每一次 ACS 变更并持续更新承诺。这不是一个简单的定期任务，而是实时集成到交易处理管线中的。

---

## 7. Daml Runtime Separability 分析

### 7.1 耦合点清单

通过分析 `DAMLe.scala` 的 imports（第 1-40 行）和类定义（第 148-156 行），识别出以下耦合点：

| 耦合点 | Canton 侧 | Daml-LF 侧 | 可分离性 |
|--------|-----------|------------|---------|
| **引擎实例** | `DAMLe` wrapper | `com.digitalasset.daml.lf.engine.Engine` | 引擎本身是独立 JAR，**可分离** |
| **合约查找** | `ReplayContractLookup` | `Engine.reinterpret()` 需要 contract lookup callback | 需要 Canton 的 `ContractStore` 提供回调 |
| **拓扑快照** | `TopologySnapshot` | `reinterpret()` 参数 | 引擎需要知道 party-to-participant 映射来做授权 |
| **合约认证** | `ContractAuthenticatorFn` | 验证合约签名 | Canton 特定的密码学层 |
| **包解析** | `PackageResolver` | `Engine` 内部按需加载 package | 需要 Canton 的包存储和 vetting 机制 |
| **时间边界** | `LedgerTimeBoundaries` | 引擎输出 | Canton 协议的时间约束 |
| **交易类型** | `LfVersionedTransaction`, `FatContractInstance` | Daml-LF 核心类型 | 类型共享，无法避免 |
| **引擎控制** | `GetEngineAbortStatus` (第 14 行) | 中断执行 | Canton 控制引擎执行的 abort 机制 |

### 7.2 分离性结论

**Daml-LF Engine (`com.digitalasset.daml.lf.engine.Engine`)** 本身是一个独立的 Scala 库，理论上可以脱离 Canton Node 使用。但要在 Canton 之外运行 Daml-LF，需要自行实现以下 glue 层：

1. **Package Store + Resolution**: Canton 使用 `PackageResolver` trait 按需从本地存储加载 Daml 包。脱离 Canton 需要自建包存储和加载机制。
2. **Contract Store + Lookup**: `ReplayContractLookup` 需要能按 `ContractId` 查找完整的合约实例。脱离 Canton 需要自建合约状态存储。
3. **Authorization / Topology Validation**: `TopologySnapshot` 提供 party-to-participant 映射和权限信息。脱离 Canton 需要自建身份和权限系统。
4. **Ledger API**: Canton 的 Ledger API 是 Daml 应用的标准接入点。脱离 Canton 需要自建或替代 gRPC API 层。
5. **Contract Authentication**: `ContractAuthenticatorFn` 验证合约的密码学签名。脱离 Canton 需要自建签名验证。

**结论**: Daml-LF 引擎**理论上可分离但实际不可行**。需要重新实现的 glue 层涉及 Canton 核心协议的大部分组件（包管理、合约存储、身份系统、API 层）。对于 Mantle 来说，Daml 引擎不适用（Mantle 必须兼容 EVM），因此分离性评估的结论是：**不需要分离 Daml 引擎，而是需要在 EVM 上实现等价的隐私和验证机制**。

---

## 8. 网络协议

### 8.1 通信协议

**gRPC** — Canton 的所有节点间通信使用 gRPC:

```
community/base/src/main/protobuf/com/digitalasset/canton/sequencer/api/v30/
  ├── sequencer_service.proto               # Sequencer gRPC 服务
  ├── sequencer_authentication_service.proto # 认证服务
  ├── sequencer_channel_service.proto        # 通道服务
  └── sequencer_connect_service.proto        # 连接服务
```

**应用层通信**: Participant 和 Mediator **不使用 libp2p 或 gossip 协议**——它们的通信是 client-server 模式，全部通过 Sequencer 中转（`SequencerClient` 是唯一通信渠道）。

**BFT 排序层例外**: BFT block orderer 节点之间**使用 P2P gRPC 网络**进行共识通信（见 `bftordering/bindings/p2p/grpc/` 和 `bftordering/core/modules/p2p/`）。这是 BFT 共识内部的排序网络，独立于应用层的 Sequencer 中转模型。因此，Canton 的网络模型是**双层**的：应用层 client-server（通过 Sequencer）+ BFT 排序层 P2P gRPC。

### 8.2 消息格式

**Protobuf v30** — Canton 使用带版本的 Protobuf 消息:

```
community/base/src/main/protobuf/com/digitalasset/canton/protocol/v30/
  ├── common.proto                  # 通用类型
  ├── common_stable.proto           # 稳定协议类型
  ├── mediator.proto                # Mediator 协议消息
  ├── synchronizer_parameters.proto # Synchronizer 参数
  ├── acs_commitments.proto         # ACS 承诺
  └── ...
```

版本控制: `v30` 后缀表示协议版本 30（而非 Protobuf 3.0），Canton 通过在包名中嵌入版本号实现协议兼容性。

### 8.3 TLS/mTLS 配置

```
base/daml-tls/          # TLS 支持库
community/participant/src/main/scala/com/digitalasset/canton/participant/config/ParticipantNodeConfig.scala
```

配置中的 TLS 支持:
- `LedgerApiServerConfig` 包含 TLS 配置
- `AdminServerConfig` 包含管理 API 的 TLS 配置
- `SequencerClientConfig` 包含与 Sequencer 通信的 TLS 配置

---

## 9. Build 与 Developer Experience 分析

### 9.1 构建工具链全景

Canton 的构建系统远比单一 sbt 复杂。完整的工具链包括:

| 工具 | 用途 | 配置文件/证据 |
|------|------|---------|
| **sbt** | Scala 编译、依赖管理、打包 | `build.sbt`, `project/*.scala` |
| **ScalaPB / sbt-protoc** | Protobuf → Scala 代码生成 | `BuildCommon.scala:24` `import sbtprotoc.ProtocPlugin.autoImport.{AsProtocPlugin, PB}` |
| **Buf** | Protobuf lint/format/breaking change 检测 | `buf.work.yaml` + `BuildCommon.scala:2` `import BufPlugin.autoImport.bufLintCheck` |
| **Flyway** | 数据库 schema migration (PostgreSQL + H2) | `community/common/src/main/resources/db/migration/` |
| **Docker** | 镜像构建（含独立 LICENSE） | `docker/` 目录，`docker/canton/images/canton-base/` |
| **sbt-header** | License header 管理 | `project/Houserules.scala:20` requires `de.heikoseeberger.sbtheader.HeaderPlugin` |
| **scalafmt** | 代码格式化 | `BuildCommon.scala:6` `import org.scalafmt.sbt.ScalafmtPlugin` |
| **scalafix** | 代码重构/lint | `BuildCommon.scala:25-26` `import scalafix.sbt.ScalafixPlugin` |
| **wartremover** | 静态代码质量检查 | `Houserules.scala:67`, `BuildCommon.scala:29-30` |
| **sbt-assembly** | Fat JAR 打包 | `BuildCommon.scala:19-21` `import sbtassembly.*` |
| **JMH** | JVM 微基准测试 | `BuildCommon.scala:11-12` `import pl.project13.scala.sbt.JmhPlugin` |
| **scoverage** | 代码覆盖率 | `BuildCommon.scala:28` `import scoverage.ScoverageKeys.*` |
| **sbt-buildinfo** | 编译时注入版本信息 | `BuildCommon.scala:21-22` `import sbtbuildinfo.BuildInfoPlugin` |
| **GCS Plugin** | Google Cloud Storage artifact 发布 | `BuildCommon.scala:9` `import org.latestbit.sbt.gcs.GcsPlugin.autoImport.*` |
| **JavaFormatter** | Java 代码格式化 | `BuildCommon.scala:6` `import com.lightbend.sbt.JavaFormatterPlugin` |
| **sbt-license-report** | 依赖 license 审计 | `BuildCommon.scala:7` `import sbtlicensereport.SbtLicenseReport` |
| **DamlPlugin** | Daml 编译集成 | `BuildCommon.scala:3` `import DamlPlugin.autoImport.*` |

### 9.2 对非 Scala 团队的维护成本

对于 Mantle 的 Go/Rust/TypeScript 开发团队，直接维护 Canton 代码的成本极高:

1. **语言壁垒**: Scala 高级特性（隐式参数、类型类、高阶类型）学习曲线陡峭
2. **cats 生态**: 广泛使用 `EitherT`, `FutureUnlessShutdown`, `OptionT` 等 monad transformer
3. **Pekko Streams**: 核心数据处理管线使用 Pekko Streams，需要理解背压和 Stream DSL
4. **JVM 运维**: 需要 JVM 调优经验（GC、内存、线程池）
5. **sbt 构建**: sbt 本身的 DSL 和多项目构建需要专门知识
6. **Protobuf 代码生成**: ScalaPB 生成的代码与 Go/Rust protobuf 生成器不兼容
7. **数据库 migration**: Flyway migration 文件为 PostgreSQL 特定 SQL

### 9.3 关键数据

- **community/ 下 Scala 源文件**: 数千个 `.scala` 文件
- **Flyway 迁移目录**: `community/common/src/main/resources/db/migration/canton/postgres/` 和 `h2/` 下包含大量 migration 文件
- **Protobuf 定义**: `community/base/src/main/protobuf/` 下有完整的协议定义
- **构建配置**: `project/` 目录下 `BuildCommon.scala` + `Dependencies.scala` 管理复杂的依赖关系

---

## 10. 文档 vs 代码差异

### 10.1 术语变化
| 文档（WHI-334/335） | 代码实际使用 | 说明 |
|---|---|---|
| Domain | Synchronizer | 代码已完成 Domain → Synchronizer 的重命名迁移 |
| Domain ID | `PhysicalSynchronizerId` | 反映新命名 |
| N/A | `PSID` | 代码中广泛使用的 `PhysicalSynchronizerId` 缩写 |

### 10.2 Sequencer Backend 差异
- **文档描述**: 可插拔 backend 支持内存、数据库、Fabric、Ethereum
- **代码实现**: 开源版包含两种 driver:
  - **Reference Driver**（`community/reference-sequencer-driver/`）: 单节点 DB-backed，支持 Memory/H2/PostgreSQL
  - **BFT Block Orderer**（`community/synchronizer/.../bftordering/`）: 完整的多节点 BFT 共识实现，含 ISS 协议、P2P gRPC、Mempool 等（Apache-2.0）
- Fabric/Ethereum drivers: SequencerDriver 注释（第 96-97 行）提到 "The Fabric and Ethereum drivers have separate entry points"，这些 driver 不在本仓库中

### 10.3 BFT 共识
- **WHI-334 提到**: BFT consensus 用于 Global Synchronizer
- **代码**: 本地 repo 中 `community/synchronizer/.../bftordering/` 下包含完整的 BFT ordering 实现（Apache-2.0），含 `BftSequencerFactory`、ISS 共识模块、Epoch 管理、Leader 选择等（详见 §3.2.3）
- Reference driver 不实现 BFT（它是单节点的简化实现）
- BFT orderer 使用独立的 `BlockOrderer` 接口（非 `SequencerDriver`），通过 `BftSequencerFactory` 集成到 `BlockSequencer` 中

### 10.4 Mediator 崩溃窗口
- **文档**: 未提及 Mediator 的崩溃恢复限制
- **代码**: 明确记录了已知限制（`Mediator.scala:79-83`）—— 在 `storeFinalized` 和 verdict 发送确认之间存在窄崩溃窗口

---

## 11. 架构亮点和代码质量评估

### 11.1 架构亮点

1. **极致的关注点分离**: SequencerDriver trait 将排序逻辑与共识机制完全解耦，使 Canton 能够适配不同的底层共识（从简单的 DB 到 BFT 区块链）。这是 Canton 最核心的架构决策。

2. **Type-safe Merkle Tree**: Scala 的类型系统被充分利用——`MerkleTree[+A]` 的泛型参数确保盲化后类型安全，`unwrap` 返回 `Either[RootHash, A]` 迫使调用方处理盲化情况。

3. **Protocol Versioning**: 通过在 Protobuf 包名中嵌入版本号（`v30`），Canton 实现了优雅的协议版本管理，允许不同版本的节点共存。

4. **Crash Recovery 设计**: Mediator 的 `finalizedPromise` 机制确保 clean sequencer counter 只在裁定持久化后推进，实现了崩溃容错。Peano queue 处理乱序完成。

5. **Stream-based 架构**: 大量使用 Pekko Streams（Sequencer subscription、block processing），实现了背压和资源控制。

6. **Phantom 类型标签**: `ReassignmentTag.{Source, Target}` 在编译时防止源/目标 Synchronizer 参数混淆，这类"利用类型系统防止 bug"的模式在整个代码库中大量使用。

### 11.2 代码质量

**优点**:
- 广泛使用 `cats` 和 `EitherT` 进行函数式错误处理
- 丰富的 ScalaDoc 注释（特别是 `SequencerDriver`、`Mediator`、`ConfirmationRequestAndResponseProcessor`）
- `@VisibleForTesting` 标注测试接口
- `PrettyPrinting` trait 提供一致的调试输出
- 明确的 `FutureUnlessShutdown` 类型，将 shutdown 语义嵌入类型系统
- `wartremover` 静态分析确保代码质量底线

**关注点**:
- 模块间耦合较紧（`community/base` 体量很大，是大部分模块的依赖）
- Scala 代码量巨大，学习曲线陡峭
- 某些文件（如 `TransactionProcessingSteps.scala`）import 列表超过 100 行，表明职责可能过于集中

---

## 12. 完整组件清单与 Reuse Matrix

| Component | Source Module | Entry Point/Class | Key Interfaces | Storage | License | Reuse Verdict | Mantle Note |
|-----------|---------------|-------------------|---------------|---------|---------|--------------|-------------|
| **Participant Node** | `community/participant` | `ParticipantNodeBootstrap` | `CantonSyncService` | PostgreSQL/H2 (Flyway) | Apache-2.0 | **Build equivalent** | 需要在 OP Stack 上构建等价的"企业参与者"节点 |
| **Sequencer Driver Interface** | `community/sequencer-driver` | `SequencerDriver` trait | `SequencerDriverFactory` | N/A (接口) | Apache-2.0 | **Borrow pattern** ⭐ | 接口设计模式可直接借鉴用于 L2 排序器可插拔后端 |
| **Reference Sequencer Driver** | `community/reference-sequencer-driver` | `ReferenceSequencerDriver` | `ReferenceBlockOrderingStore` | PostgreSQL/H2/Memory | Apache-2.0 | **Avoid direct reuse** | 单节点 Scala/JVM 实现，不兼容 |
| **BFT Block Orderer** | `community/synchronizer/.../bftordering` | `BftSequencerFactory`, `BftBlockOrderer` | `BlockOrderer`, ISS consensus, `AvailabilityStore`, `EpochStore` | PostgreSQL (多 store) | Apache-2.0 | **Borrow pattern** | 多节点 BFT 共识设计可借鉴；ISS 协议、epoch 管理、leader 选择模式有参考价值 |
| **Mediator (2PC)** | `community/synchronizer` | `Mediator` | `ConfirmationRequestAndResponseProcessor`, `VerdictSender` | Memory (pending) + DB (finalized) | Apache-2.0 | **Borrow pattern** | 确认协议设计可借鉴用于跨链验证 |
| **Merkle Tree / Blinding** | `community/base` | `MerkleTree[+A]` | `BlindingCommand`, `GenTransactionTree` | N/A (内存) | Apache-2.0 | **Borrow pattern** ⭐ | 核心隐私模式——子交易盲化可直接用于 L2 隐私层设计 |
| **Encrypted View Distribution** | `community/base` | `EncryptedViewMessage` | `EncryptedView`, `CompressedView` | N/A | Apache-2.0 | **Borrow pattern** ⭐ | 对称密钥 + 公钥加密分发模式可直接借鉴 |
| **Topology Manager** | `community/base` | `TopologyManager` | `TopologyStateProcessor`, `TopologyMapping` | `TopologyStore` (DB) | Apache-2.0 | **Build equivalent** | 身份和权限管理模式可借鉴，但需适配 EVM 身份体系 |
| **Daml-LF Engine** | `community/daml-lf` + external | `DAMLe` wrapper | `Engine`, `HasReinterpret` | Package store | Apache-2.0 | **Avoid** | Mantle 必须兼容 EVM，不能使用 Daml |
| **ACS Commitments** | `community/participant` | `AcsCommitmentProcessor` | `AcsCommitmentStore` | DB | Apache-2.0 | **Borrow pattern** | 定期承诺交换模式可用于 L2 状态一致性验证 |
| **Reassignment** | `community/participant` | `UnassignmentProcessingSteps`, `AssignmentProcessingSteps` | `ReassignmentCoordination` | `ActiveContractStore` | Apache-2.0 | **Build equivalent** | 跨 Synchronizer 资产移动模式可借鉴用于跨链桥设计 |
| **gRPC/Protobuf 协议** | `community/base`, `community/ledger-api-proto` | Protobuf v30 definitions | gRPC services | N/A | Apache-2.0 | **Avoid direct reuse** | OP Stack 使用 libp2p，通信模型不同 |
| **Configuration (HOCON)** | `community/common` | `ParticipantNodeConfig` | Typesafe Config | N/A | Apache-2.0 | **Avoid** | OP Stack 有自己的配置体系 |
| **Crypto Layer** | `base/crypto` | JCE provider, KMS drivers | `CryptoConfig`, KMS Driver API | KMS backend | Apache-2.0 | **Build equivalent** | 密码学原语选择可参考，但需适配 |

---

## 13. WHI-335 架构主张 → 代码验证表

| WHI-335 架构主张 | 代码验证 | 代码证据 | 状态 |
|-----------------|---------|---------|------|
| Participant-Synchronizer 分离 | ✅ 代码结构匹配 | `community/participant/` vs `community/synchronizer/` 物理分离 | 已验证（结构级） |
| Sequencer-Mediator 角色分离 | ✅ 代码结构匹配 | `SequencerDriver` trait + `Mediator` class 独立实现 | 已验证（结构级） |
| 消息全部通过 Sequencer 中转 | ✅ 代码结构匹配 | `SequencerClient` 是 Participant 和 Mediator 的唯一通信渠道（应用层）；BFT orderer 节点间有独立 P2P 网络 | 已验证（应用层） |
| Need-to-know 隐私（盲化） | ✅ 代码结构匹配 | `MerkleTree.blind()`, `tryBlindForTransactionViewTree()` 实现存在 | 已验证（结构级；盲化正确性未审计） |
| 加密视图分发 | ✅ 代码结构匹配 | `EncryptedViewMessage` + 对称密钥 + 公钥加密 | 已验证（结构级） |
| 两阶段确认协议 | ✅ 代码结构匹配 | `ConfirmationRequestAndResponseProcessor` Phase 2→4→6→7 | 已验证（协议流程匹配；mediator thresholding 行为保证未完全审计） |
| 命名空间 + 密钥层级 | ✅ 代码结构匹配 | `NamespaceDelegation`, `CanSignAllMappings`, `CanSignAllButNamespaceDelegations` | 已验证（类型存在；分布式一致性保证未审计） |
| Party-to-Participant 权限分级 | ✅ 代码结构匹配 | `ParticipantSynchronizerPermission` + `ParticipantPermission.Observation` (import 在 TopologyManager.scala:59) | 已验证（结构级） |
| Package Vetting | ✅ 代码结构匹配 + enforcement path | 定义: `VettedPackages` in `TopologyMapping.Code`; Enforcement: `TransactionConfirmationRequestFactory.scala:134`（`validatePackageVettings = true`）→ `UsableSynchronizers.checkPackagesVetted()` → `TopologySnapshot.loadUnvettedPackagesOrDependencies()` → `UnknownPackage` error（§4.4） | 已验证（含 submission factory 入口 + enforcement path） |
| Reassignment（非原子跨 Synchronizer） | 🔶 部分验证 | `UnassignmentProcessingSteps` + `AssignmentProcessingSteps` 存在; `ReassignedAway` 状态存在 | 代码结构匹配；跨 Synchronizer 原子性保证和故障恢复行为未逐行审计 |
| ACS Commitments（定期承诺交换） | ✅ 代码结构匹配 | `AcsCommitmentProcessor` + `AcsCommitmentStore`; `AcsCommitmentAlarm` 不一致检测 | 已验证（结构级；不一致检测的完整性未审计） |
| Topology State Machine | 🔶 部分验证 | `TopologyTransactionProcessor` → `TopologyStateProcessor` 处理管线存在 | 代码结构匹配；分布式 topology 一致性保证未完全审计 |
| Sequencer 可插拔后端 | ✅ 代码结构匹配 | 接口存在（`SequencerDriver` trait）+ Reference driver + BFT Block Orderer；Fabric/Ethereum 在注释中提及但不在本仓库 | 已验证（接口 + 两个实现） |
| BFT 共识 | 🔶 部分验证 | `community/synchronizer/.../bftordering/` 下有完整 ISS BFT 实现（Apache-2.0），含 `BftSequencerFactory`, `BftBlockOrderer`, `PreIssConsensusModule` | 代码结构完整；BFT safety/liveness 属性未形式化审计 |
| 无跨 Synchronizer 全局排序 | 🔶 部分验证 | `PhysicalSynchronizerId` 限定排序范围；无全局排序代码 | 定义级匹配；enforcement 和跨 Synchronizer 事件乱序处理未逐行审计 |

---

## 14. 对 Mantle（OP Stack L2）的 Borrow / Build / Avoid 决策表

| Canton 组件/模式 | 决策 | 理由 | Mantle 实施建议 |
|-----------------|------|------|----------------|
| **Merkle Tree 盲化** | 🟢 **Borrow pattern** | 核心隐私创新，与执行层无关 | 在 L2 隐私层设计 EVM 交易的 Merkle 承诺树，支持子交易级可见性控制 |
| **SequencerDriver 可插拔接口** | 🟢 **Borrow pattern** | 接口设计精简（5 个方法），与语言无关 | 为 Mantle 排序器设计类似的可插拔 DA 层接口 |
| **加密视图分发** | 🟢 **Borrow pattern** | 对称密钥 + 公钥的混合加密分发模式通用 | 用于 L2 隐私交易的加密分发 |
| **ViewConfirmationParameters + Quorum** | 🟢 **Borrow pattern** | 多方确认机制设计通用 | 用于 L2 跨链验证或治理场景 |
| **ACS 承诺交换** | 🟢 **Borrow pattern** | 定期状态承诺比对模式通用 | 用于 L2 多方状态一致性验证 |
| **Topology 管理模式** | 🟡 **Build equivalent** | 概念有价值但实现与 Canton 身份体系绑定 | 基于 EVM 账户体系设计等价的许可控制和 Party 管理 |
| **2PC Mediator 协议** | 🟡 **Build equivalent** | 协议逻辑可借鉴但不能直接用 | 在 OP Stack 上实现等价的多方确认层，适配 EVM 交易模型 |
| **Reassignment 协议** | 🟡 **Build equivalent** | 跨 Synchronizer 资产移动模式可借鉴 | 用于设计跨链/跨 rollup 资产移动机制 |
| **Daml-LF 引擎** | 🔴 **Avoid** | Mantle 必须兼容 EVM | 完全不适用——使用 EVM 执行层 |
| **gRPC/Protobuf 通信** | 🔴 **Avoid direct reuse** | OP Stack 使用 libp2p + SSZ/RLP | 通信层完全不同，无法复用 |
| **PostgreSQL 存储层** | 🔴 **Avoid direct reuse** | OP Stack 使用 LevelDB/Pebble | 存储引擎不同，但 Flyway migration 模式可参考 |
| **HOCON 配置** | 🔴 **Avoid** | OP Stack 有自己的 YAML/env 配置体系 | 不适用 |
| **BFT Block Orderer** | 🟢 **Borrow pattern** | 完整 ISS BFT 实现在 community/ 下（Apache-2.0） | ISS 共识协议、epoch 管理、leader 选择、P2P 网络分层可借鉴用于 L2 去中心化排序器 |
| **Fabric/Ethereum Driver** | 🔴 **Avoid** | 不在本仓库中，无法评估 license | 不可用也不需要 |
| **Docker 镜像** | 🔴 **Avoid** + ⚖️ **Needs legal review** | Proprietary license | 仅用于评估/测试，不可用于 Mantle 部署 |

### 14.1 关键洞察

Canton 最值得 Mantle 借鉴的**不是具体实现**，而是**设计哲学**:
1. **Need-to-know 原则**: 只让相关方看到必要信息
2. **子交易级粒度**: 不是整个交易隐私，而是交易内部的不同部分可以有不同的可见性
3. **密码学承诺**: 使用 Merkle 树确保看不到内容的人仍然可以验证完整性
4. **关注点分离**: 将"排序"和"确认"解耦，使系统更灵活
5. **类型安全设计**: 利用类型系统（Phantom types, sealed traits, EitherT）在编译时防止协议错误
