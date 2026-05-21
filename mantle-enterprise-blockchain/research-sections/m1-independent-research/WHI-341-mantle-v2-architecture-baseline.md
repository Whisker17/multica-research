# Mantle V2 架构基线文档

> **项目：** 企业区块链适配可行性研究  
> **阶段：** M1 - 架构基线  
> **主题：** Mantle V2（基于 OP Stack 的 Ethereum L2）  
> **日期：** 2026-05-06（修订于 2026-05-07）  
> **Linear Issue：** WHI-341  
> **分析基准版本：** mantle-v2 v1.5.4 / op-geth v1.5.4（Arsia 主网）

---

## 目录

1. [当前主网版本 / 升级状态](#1-当前主网版本--升级状态)
2. [架构概览](#2-架构概览)
3. [组件功能描述](#3-组件功能描述)
4. [状态验证与终局性架构](#4-状态验证与终局性架构)
5. [与标准 OP Stack 的差异](#5-与标准-op-stack-的差异)
6. [DA 方案分析](#6-da-方案分析)
7. [Sequencer 与运营商风险分析](#7-sequencer-与运营商风险分析)
8. [企业适配潜力](#8-企业适配潜力)
9. [关键约束与限制](#9-关键约束与限制)
10. [天然插入点](#10-天然插入点)

---

## 1. 当前主网版本 / 升级状态

> **分析基准日期:** 2026-05-07  
> **当前主网版本:** mantle-v2 v1.5.4 / op-geth v1.5.4  
> **最新升级:** Arsia (L2 block timestamp `1776841200` = 2026-04-22 07:00:00 UTC)

### 1.1 版本标识

| 组件 | 版本 | 备注 |
|------|------|------|
| mantle-v2 | v1.5.4 | Arsia 主网激活版本，基于 OP Stack op-node v1.16.3 |
| op-geth | v1.5.4（可选补丁 v1.5.5） | Arsia 执行层，含 DA 容量验证修复 |
| kona | Mantle fork（pinned op-alloy v2.1.0, revm v2.1.1） | Rust 故障证明组件 |
| Go toolchain | 1.24.13 | |
| gnark-crypto | v0.18.1 | ZK 密码学库 |

### 1.2 升级历史时间线

| 日期 | 事件 | 影响 |
|------|------|------|
| 2024-12-19 | Mantle × Succinct SP1 合作公告 | 宣布从 Optimistic Rollup 向 ZK Validity Rollup 转型 |
| 2025 Q1 | SP1 测试网启动 | OP Succinct ZK 证明系统测试 |
| **2025-09-16** | **OP Succinct 主网上线** | **状态验证从 Optimistic 切换为 ZK Validity Proof (SP1)**；部署 `OPSuccinctL2OutputOracle` 合约 |
| **2026-04-22** | **Arsia 升级激活** | EigenDA 代码路径移除；DA 切换为纯以太坊 blobs；L2BEAT 将 Mantle 从 Validium 重分类为 ZK Rollup；新三组件费用模型；OP Stack fork 对齐 (Canyon→Jovian) |

### 1.3 当前分类

自 2025-09-16 OP Succinct 上线后，Mantle 使用 **ZK Validity Proof** 进行状态验证。自 2026-04-22 Arsia 升级后，EigenDA 被移除，DA 完全依赖以太坊 L1 blobs。因此 **L2BEAT 当前将 Mantle 分类为 Stage 0 ZK Rollup**（而非此前的 Optimistic Rollup / Validium）。

**关键状态：**
- **证明系统:** OP Succinct (SP1 zkVM) — STARKs wrapped in SNARKs (Plonk: Gnark)
- **状态验证合约:** `OPSuccinctL2OutputOracle` (proxy: `0x31d5...f481`)
- **DA 机制:** Ethereum L1 blobs（calldata 回退）
- **回退模式:** `MantleSecurityMultisig` (6/14 多签) 可在 ZK 模式与 Optimistic 模式之间切换

---

## 2. 架构概览

### 2.1 文本架构图

```
                                    ETHEREUM L1（结算层）
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                                                                             │
    │   ┌──────────────┐  ┌──────────────────┐  ┌────────────────────────────┐   │
    │   │  Batch Inbox  │  │ L1 SystemConfig  │  │  Deposit Contract          │   │
    │   │  (EOA 地址)   │  │  (proxy 合约)    │  │  (OptimismPortal)          │   │
    │   └──────┬───────┘  └───────┬──────────┘  └─────────┬──────────────────┘   │
    │          │                  │                        │                       │
    │   ┌──────┴───────────────────────────────────────────┴──────────────────┐   │
    │   │  OPSuccinctL2OutputOracle (proxy: 0x31d5...f481)                    │   │
    │   │  ┌─────────────────────┐  ┌──────────────────────────────────────┐  │   │
    │   │  │  ZK 模式（默认）    │  │  Optimistic 回退（可切换）           │  │   │
    │   │  │  - SP1 validity     │  │  - 无需证明                          │  │   │
    │   │  │    proofs 通过      │  │  - 挑战者可在终局期                   │  │   │
    │   │  │    proposeL2Output  │  │    内发起质疑                         │  │   │
    │   │  │  - SP1VerifierGW    │  │  - 由 MantleSecurityMultisig          │  │   │
    │   │  │    (0x3B60...185e)  │  │    (6/14 多签) 切换                   │  │   │
    │   │  └─────────────────────┘  └──────────────────────────────────────┘  │   │
    │   └────────────────────────────────────────────────────────────────────┘    │
    └───────────────────────────────┬─────────────────────────────────────────────┘
                                    │
                          L1 数据流  │（存款、批次、配置更新）
                                    │
    ┌───────────────────────────────┼─────────────────────────────────────────────┐
    │  MANTLE V2（L2）             │                                              │
    │                              ▼                                              │
    │  ┌────────────────────────────────────────────────────────────────────────┐ │
    │  │                    OP-NODE（共识层）                                   │ │
    │  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐   │ │
    │  │  │  Sequencer   │  │  Derivation  │  │  L1 Origin Selector       │   │ │
    │  │  │  （区块      │  │  Pipeline    │  │  （epoch 管理）            │   │ │
    │  │  │   构建）      │  │  ┌─────────┐ │  └───────────────────────────┘   │ │
    │  │  └──────┬───────┘  │  │ Mantle  │ │                                  │ │
    │  │         │          │  │ Blob Src │ │  ┌───────────────────────────┐   │ │
    │  │         │          │  └─────────┘ │  │  Conductor (HA sequencer) │   │ │
    │  │         │          └──────────────┘  └───────────────────────────┘   │ │
    │  └─────────┼────────────────────────────────────────────────────────────┘ │
    │            │ Engine API (FCU, NewPayload, GetPayload)                      │
    │            ▼                                                               │
    │  ┌────────────────────────────────────────────────────────────────────────┐ │
    │  │                    OP-GETH（执行层）                                   │ │
    │  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐   │ │
    │  │  │  EVM 引擎    │  │  Tx Pool     │  │  State Database           │   │ │
    │  │  │  （标准      │  │  （L1 cost   │  │  （标准 geth）             │   │ │
    │  │  │   + L1 cost）│  │   感知）      │  │                           │   │ │
    │  │  └──────────────┘  └──────────────┘  └───────────────────────────┘   │ │
    │  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐   │ │
    │  │  │  Preconf     │  │  Miner       │  │  L2 Predeploys            │   │ │
    │  │  │  模块        │  │  （区块      │  │  (L1Block, GasPriceOracle │   │ │
    │  │  │  （预确认    │  │   组装）      │  │   OperatorFeeVault 等)    │   │ │
    │  │  │   支持）      │  │              │  │                           │   │ │
    │  │  └──────────────┘  └──────────────┘  └───────────────────────────┘   │ │
    │  └────────────────────────────────────────────────────────────────────────┘ │
    │                                                                             │
    │  ┌────────────────┐  ┌────────────────┐  ┌──────────────────────────────┐  │
    │  │  OP-BATCHER    │  │  OP-PROPOSER   │  │  GAS-ORACLE                  │  │
    │  │  （将 L2 交易  │  │  （向 L1 提交  │  │  （更新 MNT/ETH token        │  │
    │  │   批量提交到   │  │   L2 output    │  │   比率用于 L1 费用计算）      │  │
    │  │   L1 via       │  │   roots）      │  │                              │  │
    │  │   blobs/calldata)│ │               │  │                              │  │
    │  └────────────────┘  └────────────────┘  └──────────────────────────────┘  │
    │                                                                             │
    │  ┌────────────────┐  ┌────────────────┐  ┌──────────────────────────────┐  │
    │  │  OP-CHALLENGER │  │  CANNON        │  │  KONA (Rust)                  │  │
    │  │  （争议博弈    │  │  (MIPS fault   │  │  （故障证明 client/host，    │  │
    │  │   代理）        │  │   proof VM)    │  │   rollup node，derivation）  │  │
    │  └────────────────┘  └────────────────┘  └──────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 叙述性描述

Mantle V2 是一个**基于 OP Stack 的 ZK Validity Rollup**，部署在 Ethereum 上（2025 年 9 月从 Optimistic Rollup 重新分类，2026 年 4 月 Arsia 升级后从 Validium 升级为完整 Rollup）。该链经历了六次 Mantle 特有的硬分叉：**BaseFee → Everest → Euboea → Skadi → Limb → Arsia**。最新的 Arsia 升级（v1.5.4，于 2026-04-22 在 L2 时间戳 `1776841200` 激活）使 Mantle 与 OP Stack 从 Canyon 到 Jovian 的分叉对齐，引入了新的 L1 数据费用模型并移除了 EigenDA 代码路径。

**当前证明架构：** Mantle 于 2025-09-16 部署了 `OPSuccinctL2OutputOracle` 合约，将状态验证从 7 天 Optimistic 挑战窗口切换为基于 Succinct SP1 zkVM 的 ZK Validity Proof。该合约支持双模式运行：ZK 模式（默认，通过 `proposeL2Output` 提交 SP1 证明）和 Optimistic 回退模式（由 `MantleSecurityMultisig` 6/14 多签切换，回退时允许挑战者在终局期内质疑状态根）。

与标准 OP Stack 的关键架构差异：

1. **MNT 作为原生代币**（非 ETH）— 需要 token ratio oracle 进行 L1 费用转换
2. **自定义 blob 数据源**（MantleBlobDataSource）使用 Mantle 特有的编码格式
3. **六个 Mantle 特有硬分叉**与 OP Stack 分叉时间表并行运行
4. **Arsia L1 数据费用模型** — 替代标准 OP Stack L1 成本模型的新费用计算方式
5. **遗留 EigenDA 支持**（MantleDaSwitch 配置标志）与 OP Stack 的 Alt-DA 框架并存
6. **预确认模块（Preconfirmation module）** 在 op-geth 中提供预确认支持
7. **Gas Oracle 服务** 用于维护链上 MNT/ETH token 比率

系统遵循标准 OP Stack 的**共识/执行分离**架构：
- **op-node**（共识层）：处理从 L1 派生区块、排序以及 L1 origin 追踪
- **op-geth**（执行层）：运行 EVM、管理状态、通过 Engine API 构建区块
- **op-batcher**：将 L2 交易批次提交到 L1（blobs 或 calldata）
- **op-proposer**：将 L2 output root 提交到 L1 用于 withdrawal 验证
- **kona**：基于 Rust 的故障证明程序和 rollup node 组件

---

## 3. 组件功能描述

### 3.1 op-node（共识层）

**代码仓库：** `mantle-v2/op-node/`

op-node 实现了 rollup 共识逻辑，通过以下方式驱动 L2 链：
- 从 L1 数据派生 L2 区块（验证者模式）
- 排序新的 L2 区块（Sequencer 模式）
- 管理每个 L2 epoch 的 L1 origin
- 通过 Engine API 与 op-geth 通信

**关键 Mantle 定制化：**

| 文件 | 描述 |
|------|-------------|
| `rollup/mantle_types.go` | 定义 Mantle 分叉激活逻辑（6 个分叉：BaseFee 到 Arsia） |
| `rollup/types.go` | 扩展的 `Config` 结构体，包含 Mantle 分叉时间、MantleDaSwitch、DataLayrServiceManagerAddr 和 EigenDA 遗留字段 |
| `rollup/derive/mantle_blob_source.go` | 自定义 blob 数据源，先尝试 Mantle 格式（合并 blob 后 RLP 编码帧数组），失败则回退到标准逐 blob 解码 |
| `rollup/derive/mantle_pipeline.go` | Mantle 分叉激活的 pipeline 转换逻辑（如 MantleArsia 触发等效于 Holocene 的 OP Stack 转换） |
| `rollup/derive/mantle_system_config.go` | 解析 base fee 系统配置更新 |
| `rollup/derive/arsia_upgrade_transactions.go` | Arsia 网络升级 deposit 交易：部署新的 L1Block、GasPriceOracle 和 OperatorFeeVault 合约 |
| `rollup/derive/l1_block_info.go` | 扩展了 `L1InfoFuncArsiaSignature` 用于 Arsia 特定的 L1 区块信息格式 |
| `rollup/derive/data_source.go` | `DataSourceFactory.OpenData()` 将 post-Everest 区块路由到 MantleBlobDataSource |

**分叉对齐逻辑**（`mantle_types.go:AlignOpWithMantle()`）：
```
MantleArsia 激活 => 同时激活：
  Canyon, Delta, Ecotone, Fjord, Granite, Holocene, Isthmus, Jovian
```
这是一个关键的架构决策：Mantle 将多个 OP Stack 分叉映射到单个 Mantle 分叉，简化了升级管理，但在分叉语义上产生了分歧。

### 3.2 op-geth（执行层）

**代码仓库：** `op-geth/`

Mantle 的 op-geth 是一个**三层 fork**：go-ethereum（基础 hash `a38f4108`）→ op-geth（Optimism）→ Mantle 定制化。它是修改最多的组件之一。

**关键修改：**

| 领域 | 文件 | 描述 |
|------|-------|-------------|
| **双代币模型** | `core/state_transition.go`, `core/types/deposit_tx.go` | MNT 是原生 gas 代币；ETH 以 `BVM_ETH` ERC-20 形式存在于 `0xdEAD...1111`。Deposit 交易携带 `EthValue`（铸造 BVM_ETH）和 `EthTxValue`（转账 BVM_ETH）。状态转换通过直接 storage 写入管理 BVM_ETH 余额 |
| **L1 Cost（Mantle）** | `core/types/rollup_cost.go` | 基于 token ratio 的 L1 费用计算。Arsia 前：`tokenRatio` 乘以 intrinsic gas 和 L1 cost。Arsia 后：独立的 L1 cost + operator cost 模型 |
| **Operator Fee** | `core/types/rollup_cost.go` | Arsia 后：`fee = gas * operatorFeeScalar * 100 + operatorFeeConstant`，路由到 `0x...001B`。参数从 L1Block slot 8 读取 |
| **Meta-Transactions** | `core/types/meta_transaction.go`（新增） | Gas 赞助机制：任何 EIP-1559 交易都可以嵌入一个支付可配置比例 gas 费用的 sponsor。版本化（V1→V3）。**在 MantleEverestTime 已禁用** |
| **Preconf 模块** | `preconf/`（11 个文件）, `miner/preconf_checker.go`, `miner/miner_preconf.go` | 完整的同步预确认：`eth_sendRawTransactionWithPreconf` RPC 在区块密封前即返回收据。FIFO 排序，预确认环境预应用 L1 deposits，journal 持久化 |
| **Precompiles** | `core/vm/contracts.go` | 4 个 Mantle 时代的预编译合约集。EIP-7212 (secp256r1) 在 Everest 时使用非标准 gas（3450 vs 6900）。BLS12-381 在 Skadi 时引入。从 Limb 起使用标准 6900 gas |
| **状态转换** | `core/state_transition.go` | deposits 的 BVM_ETH 铸造/转账、meta-tx gas 分配、operator fee 路由、在 `ProxyOwnerUpgradeTime` 一次性 `L2ProxyAdmin` 所有权修补 |
| **DA Footprint 限制** | `miner/worker.go` | 将 `BlobGasUsed` 复用为 DA footprint 计数器。`daFootprintGasScalar` 限制每笔交易的 calldata 等效空间。超出 DA 预算的交易将被跳过 |
| **Superchain** | `superchain/` | 以 ZIP 形式嵌入 OP-Stack superchain 链注册表；自动加载链配置 |
| **Tx Pool** | `core/txpool/txpool_preconf.go`, `legacypool.go` | 预确认感知的 FIFO 交易集、预确认状态追踪、基于 journal 的持久化 |
| **自定义 CLI** | `cmd/keeper/` | zkVM guest 二进制文件，用于无状态区块执行（MIPS/RISC-V）。是 ZK 证明生成的前置条件 |
| **自定义 CLI** | `cmd/workload/` | 用于节点资质验证的 RPC 测试套件 |
| **自定义 RPC** | `internal/ethapi/api.go` | `eth_sendRawTransactionWithPreconf`、`eth_estimateTotalFee`、`eth_getBlockRange` |
| **链配置** | `params/mantle.go`, `params/config.go` | 9 个新的分叉时间戳字段；`ApplyMantleUpgrades` 将 OP Stack 分叉锁定到 Mantle 分叉 |

**分叉时间表耦合**（`params/config.go`）：
```
MantleSkadiTime => Shanghai + Cancun + Prague（EVM 分叉）
MantleArsiaTime => Canyon + Delta + Ecotone + Fjord + Granite + Holocene + Isthmus + Jovian（OP Stack 分叉）
```

**L1 费用模型（Arsia 前）：**
```
L1Cost = (rollupDataGas + overhead) * l1BaseFee * scalar * tokenRatio / (10^6 * 10^6)
```
其中 `tokenRatio` 是存储在 `GasPriceOracle` predeploy slot 0 中的 MNT/ETH 汇率。

**L1 费用模型（Arsia 后）— 三组件：**
```
总费用 = L2 执行费用 + L1 数据费用 + Operator 费用
- L1 数据费用：Fjord/Ecotone 公式 * tokenRatio（压缩数据成本估算）
- Operator 费用：gas * operatorFeeScalar * 100 + operatorFeeConstant
- 费用路由：BaseFee → 0x...0019，L1Cost → 0x...001A，OperatorFee → 0x...001B
```

**预确认系统详情：**
- `preconfChecker`（在 miner 中）每 1 秒轮询 op-node 同步状态，预取 L1 deposits，维护推测性区块环境
- `eth_sendRawTransactionWithPreconf`：同步 RPC，在区块包含前即返回收据
- 区块填充：预确认交易优先处理（FIFO），当存在未密封的预确认交易时暂停常规交易
- 持久化：`PreconfTxTracker` 将成功的预确认记录到磁盘，重启时重放

### 3.3 op-batcher

**代码仓库：** `mantle-v2/op-batcher/`

将 L2 交易批次提交到 L1。支持 calldata 和 blob 交易。Mantle 的 blob 格式与标准 OP Stack 不同：

- **标准 OP Stack**：每个 blob 包含独立数据
- **Mantle 格式**（Arsia 前，Everest 后）：多个 blob 合并在一起，结果以 RLP 方式解码为帧数组。如果 Mantle 格式解码失败则回退到逐 blob 解码。

**Mantle 特有：DA 吞吐量节流**

batcher 包含一个自定义的 `ThrottleController`（上游无对应实现），通过自定义 `miner_setMaxDASize` RPC 调用从 batcher 向 op-geth 的区块生产层产生背压。

四种可插拔的节流策略实现了 `ThrottleStrategy` 接口：

| 策略 | 行为 | 状态 |
|----------|----------|--------|
| `LinearStrategy` | 从阈值到最大值线性扩展强度 | 稳定 |
| `QuadraticStrategy` | 二次曲线——低负载时温和，高负载时陡峭 | 稳定 |
| `StepStrategy` | 在可配置阈值处二元开/关 | 稳定 |
| `PIDStrategy` | 带 Kp/Ki/Kd 参数的 PID 控制器 | 实验性 |

配置（`op-batcher/batcher/config.go`）：
- `ThrottleThreshold`：开始节流前的待处理字节数
- `ThrottleMaxBlockSize`/`ThrottleMaxTxSize`：全力节流时的限制
- `ThrottleAlwaysBlockSize`/`ThrottleAlwaysTxSize`：硬上限（始终生效）

batcher 运行四个 goroutine：`blockLoadingLoop`、`publishingLoop`、`receiptsLoop` 和 `throttlingLoop`（Mantle 新增）。

**来源：** `op-batcher/batcher/driver.go`、`op-batcher/batcher/throttler/`

### 3.4 op-proposer（标准 OP Stack Output Proposer）

**代码仓库：** `mantle-v2/op-proposer/`

标准 OP Stack 的 output root 提交组件，**无 Mantle 特定定制**。

**关键代码证据：**
- Binding 仍指向标准 `L2OutputOracle` 合约 ABI（`op-proposer/bindings/l2outputoracle.go`）
- `proposeL2Output()` 仅接受 4 个参数：`_outputRoot`, `_l2BlockNumber`, `_l1BlockHash`, `_l1BlockNumber`——**不包含任何 proof 参数**
- 这意味着仓库内的 `op-proposer` 二进制文件是为标准 Optimistic 模式设计的，**不是**当前 OP Succinct ZK 证明提交的入口

> ⚠️ **重要区分：** 仓库内的 `op-proposer` 与 Mantle 当前主网部署的 OP Succinct 证明提交组件是**不同的**。当前主网通过外部的 OP Succinct prover infrastructure 生成 SP1 证明并提交到 `OPSuccinctL2OutputOracle` 合约。详见 [第 4 节：状态验证与终局性架构](#4-状态验证与终局性架构) 中对三个不同角色的区分。

### 3.5 gas-oracle

**代码仓库：** `mantle-v2/gas-oracle/`

**Mantle 特有服务。** 维护链上 MNT/ETH token 比率，用于 L1 费用计算。这是必需的，因为 Mantle 使用 MNT（而非 ETH）作为原生 gas 代币。

**关键组件：**
- `oracle/gas_price_oracle.go`：主 Oracle 服务，以可配置间隔运行 `TokenRatioLoop()`
- `oracle/token_ratio.go`：`wrapUpdateTokenRatio()` 调用 GasPriceOracle predeploy 上的 `contract.SetTokenRatio()`
- `tokenratio/tokenratio.go`：从多个来源计算 Token Ratio
- `tokenratio/tokenratio_dex.go`：基于 DEX 的比率（链上价格）
- `tokenratio/tokenratio_v1.go`、`tokenratio_v5.go`：不同的比率计算版本
- 通过 Google Cloud KMS 支持 **HSM**（硬件安全模块）签名

**Token Ratio 来源：**
- CEX 价格源（`TokenRatioCexURL`）
- DEX 价格源（`TokenRatioDexURL`）
- 可配置标量（`TokenRatioScalar`）
- 显著性阈值以避免不必要的更新（`TokenRatioSignificanceFactor`）

### 3.6 Bridge 与 Withdrawal 架构（双代币）

Withdrawal 协议相比标准 OP Stack 进行了根本性修改，以支持双代币（MNT + ETH）提款。

**关键 bindings（`op-service/txintent/bindings/`）：**

| 组件 | 标准 OP Stack | Mantle |
|-----------|-------------------|--------|
| `OptimismPortal` | 带有单一 `value` 的 `WithdrawalTransaction` | 带有 `MNTValue` + `ETHValue` 的 `MantleWithdrawalTransaction` |
| `L1StandardBridge` | `DepositETH()` | `DepositMNT()`、`DepositMNTTo()`、`FinalizeMantleWithdrawal()` |
| `L2ToL1MessagePasser` | `InitiateWithdrawal(target, gasLimit, data)` | `InitiateWithdrawal(target, gasLimit, data, ethValue)` — ETH 显式传递，因为 MNT 是原生代币 |
| Bridge 函数 | ETH 通过 `msg.value` | MNT 通过 `msg.value`，ETH 作为单独参数指定 |
| L1 MNT 地址 | 不适用 | `L1MNTAddress()` — 读取 L1 MNT ERC-20 地址（主网为 `0x3c3a81e81dc49a522a592e7622a7e711c06bf354`） |

**来源：** `op-service/txintent/bindings/MantleOptimismPortal.go`、`MantleL1StandardBridge.go`、`MantleL2ToL1MessagePasser.go`

### 3.7 op-challenger 与 cannon（故障证明系统）

**代码仓库：** `mantle-v2/op-challenger/`、`mantle-v2/cannon/`

标准 OP Stack 的争议博弈和基于 MIPS 的故障证明虚拟机。op-challenger 监控并响应 L1 上的争议博弈。

### 3.7.1 当前角色说明

> **重要更新：** 自 2025-09-16 OP Succinct 主网上线后，`op-challenger` 和 `cannon` 不再是 Mantle 状态验证的主要路径。当前主路径为 SP1 ZK Validity Proof。但这些组件仍保留在代码库中：(1) 作为 Optimistic 回退模式的基础设施（当 `MantleSecurityMultisig` 切换到 optimistic 模式时需要）；(2) `kona` 中的故障证明 client/host 作为 ZK 证明系统的补充验证层。

### 3.8 kona（Rust 故障证明与 Rollup Node）

**代码仓库：** `kona/`（同时作为 `mantle-v2/kona/` 的子模块引用）

Kona 是 OP Stack 组件的 Rust 实现：

**二进制文件：**
- `bin/client`：在 prover（MIPS/RISC-V VM）内执行状态转换的故障证明程序
- `bin/host`：作为 Preimage Oracle 服务器的本地 host
- `bin/node`：Rollup node 实现
- `bin/supervisor`：用于互操作协调的 Supervisor

**Crates：**
- `crates/proof/`：无状态区块执行器、证明 SDK、MPT 工具、FPVM kernel API
- `crates/protocol/`：Derivation pipeline（`derive`）、协议类型、genesis、hardforks、压缩
- `crates/node/`：Rollup node 服务、engine client、RPC、P2P、数据源
- `crates/supervisor/`：用于跨链消息安全的 Supervisor 服务
- `crates/batcher/`：批次提交逻辑
- `crates/providers/`：数据提供者抽象

**目标架构：**
- MIPS64（cannon 目标）— 用于链上故障证明
- RISC-V（asterisc 目标）— 替代故障证明虚拟机
- Native — 用于链下验证

**kona 中的 Mantle 特有定制化：**

| 领域 | 上游 | Mantle 修改 |
|------|----------|---------------------|
| `RollupConfig` | 增量式 OP Stack 分叉阶梯 | 双时间戳模型：`mantle_skadi_time` 同时激活 Bedrock 到 Isthmus；`mantle_limb_time` 激活 Osaka |
| `BootInfo` | 先尝试硬编码注册表 | 始终从 oracle 加载配置（注册表已注释掉） |
| `TxDeposit` | 仅 Version 0（ETH） | 新增 Version 1 用于 MNT 原生代币，包含 `eth_value` 和 `eth_tx_value` 字段 |
| 区块头组装 | 基于 hardfork 状态的条件判断 | 硬编码：`withdrawals_root` 始终设置、blob gas 始终为 (0,0)、base fee 始终为 optimism 默认值 |
| DA 源路由 | 使用 `ecotone_time` 作为 blob 切换点 | 使用 `mantle_skadi_time` 作为 blob 切换点 |
| 依赖项 | 上游 `op-alloy`、`revm` | 锁定到 `mantle-xyz` fork（`op-alloy` v2.1.0、`revm` v2.1.1）以支持 MNT 代币 |

**故障证明就绪性：** Skadi 后单链场景代码完整。FPVM prestate 生成基础设施已就绪（用于 RISC-V/MIPS64 的 Docker 构建）。已知缺口：Docker prestate 仍引用上游 kona 仓库（非 Mantle fork），span batch 的 `is_last_in_span` 硬编码为 `true`，以及若干 hardfork 门控功能被硬编码为 Mantle 简化值。

**来源：** `crates/protocol/genesis/src/rollup.rs`、`crates/proof/proof/src/boot.rs`、`crates/proof/executor/src/builder/assemble.rs`、`crates/protocol/protocol/src/deposits.rs`

### 3.9 op-conductor

**代码仓库：** `mantle-v2/op-conductor/`

高可用 Sequencer 服务，用于 leader election 和故障转移。标准 OP Stack 组件。

### 3.10 op-alt-da（替代 DA）

**代码仓库：** `mantle-v2/op-alt-da/`

OP Stack 的可插拔 DA 框架，支持：
- **Keccak256 commitments**，配合链上挑战机制
- **Generic commitments**，面向外部 DA 提供者（如 EigenDA）
- 基于 HTTP 的客户端/服务端接口（`DAClient`、`DAServer`）
- S3 和基于文件的存储后端
- 用于挑战追踪的 DA 状态机（`dastate.go`）

### 3.11 op-service（共享库）

**代码仓库：** `mantle-v2/op-service/`

通用基础设施：交易管理器（`txmgr/`）、HSM 支持（`hsm/`）、指标、RPC 工具、TLS、事件系统等。这是所有 OP Stack 服务的基础工具库。

**HSM 集成（`op-service/hsm/hsm_signer.go`）：**

生产级 Google Cloud KMS 签名，具备以下特性：
- `ManagedKey` 结构体封装 GCP KMS 客户端 + Ethereum 地址
- `SignHash()`：调用 GCP KMS `AsymmetricSign`，解析 ASN.1 DER 签名
- **EIP-2 low-s 规范化** 以防止签名可变性
- **Recovery ID 暴力破解** — 测试两个可能的 v 值
- 产出标准 Ethereum 签名 — KMS 仅执行原始 ECDSA

配置标志（在 op-batcher、op-proposer、gas-oracle 中可用）：
- `EnableHsm`：在原始私钥和 HSM 之间切换
- `HsmAddress`：对应 KMS 密钥的 Ethereum 地址
- `HsmKeyName`：完整 GCP KMS 密钥路径

**Fork Override CLI 标志（`op-service/flags/mantle_flags.go`）：**

运营者可在运行时覆盖 Mantle 分叉激活时间戳：
- `--override.skadi`、`--override.limb`、`--override.arsia`
- 早期分叉（BaseFee、Everest、Euboea）不可覆盖——被视为稳定版本

---

## 4. 状态验证与终局性架构

### 4.1 当前状态验证模型：OP Succinct (SP1)

自 2025-09-16 起，Mantle 的状态验证合约从标准 OP Stack 的 `L2OutputOracle`（optimistic 模型）升级为 `OPSuccinctL2OutputOracle`——一个支持 ZK Validity Proof 的修改版本。

**核心机制：**

| 属性 | 详情 |
|------|------|
| **合约名称** | `OPSuccinctL2OutputOracle` |
| **Proxy 地址** | `0x31d5...f481` |
| **Implementation 地址** | `0x4059...6f50` |
| **证明系统** | SP1 zkVM (Succinct) — STARKs wrapped in SNARKs |
| **可信设置** | Plonk: Gnark |
| **验证器合约** | SP1VerifierGateway (`0x3B60...185e`) |
| **SP1 Verifier 版本** | v5.0.0 (`0x0459...C459`), v6.0.0 (`0x8a0f...Fc5C`) |

> **注意：** OP Succinct 的 program hashes（aggregation / range）属于可变部署参数，随 SP1 版本升级频繁变化。本文不列出具体 hash 值，请在需要时直接查阅 L2BEAT 或链上合约获取当前值。

### 4.1.1 三个不同角色的区分

> ⚠️ **关键架构区分：** 当前 Mantle 的状态提交 pipeline 涉及三个不同的组件/角色，不应混为一体：

| 角色 | 组件 | 位置 | 合约 ABI | 说明 |
|------|------|------|----------|------|
| **① op-proposer（标准 OP Stack 二进制）** | `mantle-v2/op-proposer/` | 仓库内 | 标准 `L2OutputOracle`（4 参数 `proposeL2Output`，**无 proof**） | 仓库中签入的标准 OP Stack output proposer；binding 仍指向旧的 `L2OutputOracle` ABI。此组件**不**生成或提交 ZK 证明。当前主网**不使用此路径**作为主验证机制。 |
| **② SP1 Prover（外部基础设施）** | Succinct SP1 zkVM prover | 外部/部署层 | — | 执行 L2 状态转换的 ZK 证明生成。运行在链下，非仓库内组件。使用 SP1 Hypercube prover 生成 STARKs→SNARKs 证明。 |
| **③ OP Succinct Output Submitter（外部/部署层）** | OP Succinct 提交服务 | 外部/部署层 | `OPSuccinctL2OutputOracle`（含 proof 参数的 `proposeL2Output`） | 将 SP1 Prover 生成的证明与 output root 一起提交到 `OPSuccinctL2OutputOracle` 合约。当 `whenNotOptimistic` 时调用带 proof 的 `proposeL2Output`；在 optimistic 回退模式下退化为标准 4 参数调用。 |

**ZK 模式工作流（当前主路径）：**
1. **SP1 Prover** 在链下执行 L2 状态转换并生成 SP1 ZK 证明（STARKs wrapped in SNARKs）
2. **OP Succinct Output Submitter** 调用 `OPSuccinctL2OutputOracle.proposeL2Output()` 提交 L2 output root + SP1 proof
3. `OPSuccinctL2OutputOracle` 通过 `SP1VerifierGateway` 在链上验证证明
4. 验证通过后，output root 被接受，对应的 withdrawal 可以在 L1 上完成

**Optimistic 回退工作流（备用路径）：**
1. `MantleSecurityMultisig` 将 `OPSuccinctL2OutputOracle` 切换到 optimistic 模式
2. 提交者调用 `proposeL2Output()` **无需**附带 proof（退化为标准 4 参数调用）
3. 此时可使用仓库内的标准 `op-proposer` 二进制文件
4. 挑战者可在终局期内质疑提交的 output root

> **代码证据：** 仓库内 `op-proposer/bindings/l2outputoracle.go` 的 `proposeL2Output` 函数签名为 `(opts, _outputRoot, _l2BlockNumber, _l1BlockHash, _l1BlockNumber)` — 4 个参数，无 proof。这确认仓库内的 `op-proposer` 是为标准 Optimistic 模式设计的，不处理 ZK 证明提交。

### 4.2 双模式运行与 Optimistic 回退

`OPSuccinctL2OutputOracle` 通过 `whenNotOptimistic` modifier 支持双模式运行：

**ZK 模式（默认）：**
- `proposeL2Output` 需要由 **OP Succinct Output Submitter** 携带有效的 SP1 validity proof 调用
- 无需挑战期——证明本身就是状态正确性的保证
- Withdrawal 在证明提交后即可完成（目标：~1 小时终局性）

**Optimistic 回退模式：**
- 由 `MantleSecurityMultisig` (6/14 多签) 触发切换
- 切换后，`proposeL2Output` 不需要证明——此时可使用仓库内的标准 **op-proposer** 二进制
- 恢复为传统 Optimistic 模式：挑战者可在终局期内质疑提交的 output root
- 设计为 SP1 证明系统临时不可用时的安全网

**企业影响分析：**

| 维度 | ZK 模式 | Optimistic 回退 |
|------|---------|-----------------|
| **终局性** | ~1 小时（证明生成 + 验证） | 7 天挑战期 |
| **安全假设** | 密码学证明（trustless） | 至少 1 个诚实挑战者 |
| **Withdrawal 延迟** | 证明提交后可立即执行 | 需等待整个挑战期 |
| **Liveness 依赖** | SP1 Prover + OP Succinct Output Submitter 必须在线 | op-proposer（或等效组件）+ Challenger 必须在线 |
| **模式切换权限** | MantleSecurityMultisig (6/14) | MantleSecurityMultisig (6/14) |

### 4.3 L1 合约架构

当前 Mantle L1 上的关键合约：

| 合约 | 地址（截断） | 功能 |
|------|-------------|------|
| `OPSuccinctL2OutputOracle` | Proxy: `0x31d5...f481` | 状态验证（ZK/Optimistic 双模式） |
| `OptimismPortal` | `0xc54c...A8Fb` | 存取款门户（含双代币 MNT+ETH） |
| `L1CrossDomainMessenger` | `0x676A...7120` | 跨域消息传递 |
| `L1StandardBridge` | `0x95fC...3012` | 标准桥接 |
| `SystemConfig` | `0x427E...6cAf` | 链上参数配置 |
| `ProxyAdmin` | `0xca35...7794` | 代理合约管理 |
| `SP1VerifierGateway` | `0x3B60...185e` | SP1 证明验证网关 |
| `TimelockController` | `0x6533...447F` | 时间锁控制（仅 L1MantleToken） |

### 4.4 升级与治理风险

> ⚠️ **关键风险：** L2BEAT 将以下问题标记为 CRITICAL：

1. **零延迟升级：** `MantleSecurityMultisig` (6/14 多签) 可以即时升级所有核心合约（`OptimismPortal`、`OPSuccinctL2OutputOracle`、`L1StandardBridge` 等），无任何时间锁延迟。这意味着用户在升级发生前没有退出窗口。

2. **证明模式切换：** 同一多签可以在 ZK 模式和 Optimistic 模式之间切换，影响终局性保证和 withdrawal 延迟。

3. **仅 L1MantleToken 有时间锁：** `TimelockController`（1 天延迟）仅应用于 `L1MantleToken` 的修改，不覆盖核心基础设施合约。

**企业启示：**
- 企业部署需要添加独立的升级时间锁机制
- 多签治理模式对企业场景有参考价值，但安全阈值（6/14）可能需要调整
- ZK/Optimistic 模式切换权限应纳入企业治理框架

### 4.5 与标准 OP Stack 状态验证的对比

| 属性 | 标准 OP Stack | Mantle（当前） |
|------|--------------|---------------|
| **验证合约** | `L2OutputOracle` 或 `DisputeGameFactory` | `OPSuccinctL2OutputOracle` |
| **验证方式** | Optimistic (fault proof) | ZK Validity Proof (SP1) + Optimistic 回退 |
| **终局性** | 7 天挑战期 | ~1 小时（ZK 模式） |
| **安全假设** | 至少 1 个诚实挑战者 | 密码学证明 + 可信设置 |
| **故障证明** | cannon (MIPS) / kona (RISC-V) | 保留但非主路径，用于回退模式 |
| **Withdrawal** | 等待 7 天 | 证明验证后即可执行 |
| **ZK Prover** | 不需要 | 需要 SP1 Prover + OP Succinct Output Submitter 持续运行（外部/部署层组件，非仓库内） |

---

## 5. 与标准 OP Stack 的差异

### 5.1 Mantle 特有硬分叉时间表

Mantle 在 OP Stack 之外维护自己的并行分叉时间表：

| Mantle 分叉 | OP Stack 等效 | 关键变更 |
|------------|---------------------|-------------|
| **BaseFee** | （Canyon 之前） | 自定义 base fee 机制 |
| **Everest** | （Canyon 之前） | 引入 MantleBlobDataSource；开始基于 blob 的 DA |
| **Euboea** | （Canyon 之前） | 进一步优化 |
| **Skadi** | 等效于 Regolith/Bedrock | Engine API v4 支持，Skadi 区块使用 NewPayloadV4 |
| **Limb** | （Canyon 之前） | Arsia 前准备 |
| **Arsia** | Canyon+Delta+Ecotone+Fjord+Granite+Holocene+Isthmus+Jovian（一次性全部） | 新 L1 费用模型、L1Block/GasPriceOracle 合约升级、OperatorFeeVault |

**来源：** `op-node/rollup/mantle_types.go`、`op-node/rollup/types.go`（第 138-158 行）

### 5.2 原生代币：MNT + BVM_ETH 双代币模型

| 方面 | 标准 OP Stack | Mantle V2 |
|--------|-------------------|-----------|
| Gas 代币 | ETH | MNT |
| ETH 表示 | 原生余额 | `BVM_ETH` ERC-20 位于 `0xdEAD...1111` |
| L1 费用计价 | ETH | MNT（通过 token ratio 转换） |
| Token ratio oracle | 不需要 | `gas-oracle/` 服务 + GasPriceOracle predeploy |
| Deposit 交易字段 | `Mint`、`Value`（ETH） | `Mint`、`Value`（MNT）+ `EthValue`（BVM_ETH 铸造）+ `EthTxValue`（BVM_ETH 转账） |
| 费用公式 | `L1Cost = f(gasUsed, l1BaseFee, scalar)` | `L1Cost = f(gasUsed, l1BaseFee, scalar) * tokenRatio` |

BVM_ETH 操作发生在状态转换层面（直接 storage 写入 ERC-20 合约状态 + 合成事件发射），而非通过 EVM 调用。这是与 Ethereum 语义的根本性偏离。

**来源：** `op-geth/core/state_transition.go`（BVM_ETH 铸造/转账函数）、`op-geth/core/types/deposit_tx.go`（EthValue/EthTxValue 字段）、`op-geth/core/types/rollup_cost.go`

### 5.3 自定义 Blob 数据源

标准 OP Stack 对每笔交易的 blob 进行逐个处理。Mantle 引入了 `MantleBlobDataSource`，其工作流程为：
1. 将一笔交易中的所有 blob 合并在一起
2. 尝试以 RLP 方式解码为帧数组（Mantle 格式）
3. 如果 Mantle 格式解码失败则回退到逐 blob 解码
4. Arsia 激活后如果 Mantle 格式解码失败，则切换到标准 BlobDataSource

**来源：** `op-node/rollup/derive/mantle_blob_source.go`

### 5.4 Arsia L1 数据费用模型

Arsia 升级通过 deposit 交易部署新的 predeploy 合约：
1. **L1Block**（部署在从 `0x4250000000000000000000000000000000000000` 派生的地址）
2. **GasPriceOracle**（部署在从 `0x4250000000000000000000000000000000000001` 派生的地址）
3. **OperatorFeeVault**（部署在从 `0x4250000000000000000000000000000000000002` 派生的地址，接收方：`0x2f44bd2a54ac3fb20cd7783cf94334069641dac9`）

新模型引入了 `setArsia()` 激活，之后 `isArsia` 标志启用：
- 使用类 `flzCompress` 算法的压缩数据成本估算
- 新的 operator fee scalar 和 constant
- DA footprint gas scalar（来自 Jovian）

**来源：** `op-node/rollup/derive/arsia_upgrade_transactions.go`、`op-geth/core/types/rollup_cost.go`

### 5.5 Meta-Transactions（Gas 赞助）

Mantle 实现了一套 gas 赞助系统（标准 OP Stack 中不存在），允许任何 EIP-1559 交易在其 calldata 中嵌入 `MetaTxParams` 前缀。第三方 `GasFeeSponsor` 支付可配置比例（1-100%）的 gas 费用。

- **魔术前缀：** `0x00000000000000000000000000004D616E746C654D6574615478507265666978`（"MantleMetaTxPrefix"）
- **参数：** `ExpireHeight`、`SponsorPercent`、`Payload`（真实 calldata）、sponsor 地址 + ECDSA 签名
- **版本：** V1（签名不含 `From`）、V2（包含 `From` 以防止重放）、V3（sponsor ≠ sender 要求）
- **状态：** **在 MantleEverestTime 已禁用** — `MetaTxCheck` 对所有新交易返回 `ErrMetaTxDisabled`

**来源：** `op-geth/core/types/meta_transaction.go`、`op-geth/core/state_transition.go`

**企业相关性：** 虽然在主网上已禁用，但 meta-transaction 基础设施展示了 Mantle 实现自定义交易级 gas 策略的能力——这一模式可直接应用于企业 gas 赞助/补贴场景。

### 5.6 预确认支持

op-geth 包含一个完整的 `preconf/` 模块，标准 op-geth 中不存在：
- `fifo_tx_set.go`：用于预确认排序的 FIFO 交易集
- `miner_config.go`：预确认感知的矿工配置
- `tx_pool_config.go`：预确认感知的交易池
- `deposit_log.go`、`deposit_source.go`：预确认 deposit 处理
- `sync_status.go`：预确认的同步状态追踪

**来源：** `op-geth/preconf/`

### 5.7 Engine API 版本映射

Mantle 基于 Mantle 分叉覆盖了 Engine API 版本选择：

```go
// ForkchoiceUpdatedVersion
if c.IsEcotone(ts) || c.IsMantleSkadi(ts) { return FCUV3 }

// NewPayloadVersion / GetPayloadVersion
if c.IsIsthmus(timestamp) || c.IsMantleSkadi(timestamp) { return V4 }
```

这意味着 MantleSkadi 独立于 OP Stack 分叉时间表激活 V3/V4 Engine API。

**来源：** `op-node/rollup/types.go`（第 717-758 行）

### 5.8 遗留 EigenDA 配置

Rollup 配置中保留了 EigenDA 集成的遗留字段：
```go
MantleDaSwitch             bool   `json:"mantle_da_switch,omitempty"`
DataLayrServiceManagerAddr string `json:"datalayr_service_manager_addr,omitempty"`
```
这些字段表明在过渡到当前基于 blob 的方式之前，历史上曾使用 EigenDA（通过 DataLayr 协议）。

**来源：** `op-node/rollup/types.go`（第 194-197 行）

### 5.9 总结：与上游一致 vs. 定制化组件

| 组件 | 状态 |
|-----------|--------|
| op-challenger | 基本与上游一致 |
| cannon | 基本与上游一致 |
| op-conductor | 基本与上游一致（Hashicorp Raft、BoltDB，无 Mantle 变更） |
| op-supervisor | 基本与上游一致 |
| op-deployer | 基本与上游一致 |
| op-proposer | 与上游一致（无 Mantle 变更）；binding 仍指向标准 `L2OutputOracle` ABI。**注意：** 当前主网状态提交由外部 OP Succinct Output Submitter 处理，非此组件 |
| op-alt-da | 与上游一致（标准 OP Stack Alt-DA） |
| op-preimage | 与上游一致 |
| op-service | 上游 + Mantle 新增（HSM/GCP KMS 集成、fork override CLI 标志） |
| op-node | **大量定制化**（6 个 Mantle 分叉、blob 数据源、pipeline 转换、费用模型、Skadi 时的 P2P BlockV4） |
| op-geth | **大量定制化**（BVM_ETH 双代币状态转换、带 token ratio 的三组件 L1 费用模型、带 FIFO 排序的 preconf 模块、meta-tx 基础设施（已禁用）、4 个自定义预编译合约集、DA footprint 限制器、operator fee 路由、zkVM keeper 二进制文件） |
| op-batcher | **显著定制化**（带 4 种可插拔策略的 DA 吞吐量节流、`miner_setMaxDASize` RPC、Mantle blob 格式） |
| gas-oracle | **Mantle 特有**（完整服务：CEX/DEX 价格聚合、链上结算、HSM 签名） |
| kona | **上游 kona 的 Fork**（双时间戳模型、MNT deposit v1、Skadi 时的 DA 源路由） |
| Bridge 合约 | **大量定制化**（MantleOptimismPortal、MantleL1StandardBridge — 双代币 MNT+ETH 提款） |

---

## 6. DA 方案分析

### 6.1 DA 演进阶段与安全假设

Mantle 的 DA 策略经历了三个显著不同的阶段，每个阶段的安全假设和信任模型不同：

#### 阶段一：EigenDA / DataLayr 时代（V1 → V2 早期）

| 属性 | 详情 |
|------|------|
| **DA 提供者** | EigenDA (DataLayr 协议) |
| **信任假设** | EigenDA 运营商诚实多数假设；数据可用性依赖外部委员会 |
| **安全模型** | 非以太坊 L1 保障——数据可用性不受以太坊共识保护 |
| **L2BEAT 分类** | **Validium**（数据不在以太坊上） |
| **代码遗留** | `MantleDaSwitch` 和 `DataLayrServiceManagerAddr` 配置字段仍保留在 `op-node/rollup/types.go` |
| **风险** | DA 委员会串谋可导致数据不可用；用户无法独立验证数据可用性 |

#### 阶段二：Mantle Blob 格式（Everest → Arsia 前）

| 属性 | 详情 |
|------|------|
| **DA 提供者** | 以太坊 L1 Blobs (EIP-4844) |
| **Blob 编码** | Mantle 自定义格式：多个 blob 合并后 RLP 解码为 frame array |
| **信任假设** | 以太坊 L1 共识保障数据可用性 |
| **安全模型** | 继承以太坊 L1 安全性——但仍可能同时使用 EigenDA（`MantleDaSwitch`） |
| **代码位置** | `op-node/rollup/derive/mantle_blob_source.go`（`MantleBlobDataSource`） |
| **L2BEAT 分类** | 视 EigenDA 使用情况可能仍为 **Validium** |

#### 阶段三：标准 OP Stack Blob 格式（Arsia 之后，当前）

| 属性 | 详情 |
|------|------|
| **DA 提供者** | **仅以太坊 L1 Blobs**（calldata 回退） |
| **Blob 编码** | 标准 OP Stack 格式（每 blob 独立帧），`MantleBlobDataSource` 自动检测并回退 |
| **EigenDA** | **代码路径已移除**（Arsia 升级明确删除 EigenDA 依赖） |
| **信任假设** | 纯以太坊 L1 安全性——数据可用性完全由以太坊共识保障 |
| **安全模型** | 与标准以太坊 L2 Rollup 一致 |
| **Batcher 变更** | v1.5.4 从 Mantle 自定义 blob 编码切换到标准 OP Stack 格式（一帧一 blob） |
| **L2BEAT 分类** | **ZK Rollup**（DA 在以太坊 + ZK 证明验证） |
| **日均数据量** | ~7.14 MiB/天，~69.54 bytes/交易（L2BEAT 统计） |

### 6.2 DA 架构详情（当前 Arsia 后）

**批次提交数据流：**
1. op-batcher 将 L2 交易收集为帧
2. 帧被编码（Mantle 格式：RLP 编码帧数组，分布在多个 blob 中）
3. 以携带 blob 的交易形式提交到 L1 的 `BatchInboxAddress`
4. op-node 的 `DataSourceFactory.OpenData()` 路由到适当的数据源：
   - Post-Ecotone + blob 源切换后：`NewBlobDataSource`（标准）
   - Post-Everest：`NewMantleBlobDataSource`（先尝试 Mantle 格式）
   - Pre-Everest：`NewCalldataSource`（仅 calldata）
5. 如果启用了 Alt-DA，则将数据源包装在 `NewAltDADataSource` 中

**Alt-DA 框架：**
- 可用但非主要 DA 机制
- 支持 Keccak256 commitments（带链上挑战）和 Generic commitments
- 基于 HTTP 的 DA 服务端接口，配合 S3/文件后端
- 挑战机制：`DAChallengeWindow` + `DAResolveWindow` 用于数据可用性争议

### 6.3 EigenDA 遗留与残留代码路径

`MantleDaSwitch` 和 `DataLayrServiceManagerAddr` 字段在 rollup 配置中表明 Mantle V1 曾使用 EigenDA（通过 DataLayr 协议）。在 V2 中，已被 L1 blob 交易（EIP-4844）替代为主要 DA 机制。遗留字段为历史链数据派生而保留。

**残留代码路径详情：**

| 残留项 | 位置 | 状态 | 企业影响 |
|--------|------|------|---------|
| `MantleDaSwitch` 配置字段 | `op-node/rollup/types.go` L194 | 保留但无活跃代码消费 | 可能导致新开发者对实际 DA 机制产生误解 |
| `DataLayrServiceManagerAddr` | `op-node/rollup/types.go` L195 | 同上 | 同上 |
| `MantleBlobDataSource` 回退逻辑 | `mantle_blob_source.go` | 活跃——用于解析 Arsia 前历史区块 | 企业 fork 可移除（仅同步历史数据需要） |
| `blobSourceChanged` latch | `mantle_blob_source.go` | 活跃——L1 reorg 时正确重置 | 保留以确保链同步正确性 |

**企业启示：** 企业 fork 如果不需要同步 Arsia 前的历史数据，可以安全移除 `MantleBlobDataSource` 和 EigenDA 残留字段，简化代码库。但如果需要完整历史数据同步，这些代码路径必须保留。

---

## 7. Sequencer 与运营商风险分析

### 7.1 当前 Sequencer 架构

Mantle 运行**单一中心化 Sequencer**，由 Mantle 团队运营。`op-conductor` 提供高可用性故障转移（Hashicorp Raft 共识 + BoltDB），但仅在 Sequencer 副本之间进行 leader election，并非去中心化排序。

**Sequencer 运营细节：**

| 属性 | 当前状态 |
|------|---------|
| **Sequencer 类型** | 单一活跃 Sequencer + HA 备份 |
| **Sequencer EOA** | `0x2f40...d749`（L2BEAT 标识） |
| **区块时间** | 2 秒 |
| **HA 方案** | op-conductor（Raft leader election） |
| **排序策略** | FIFO（preconf 模式）/ 标准 op-geth mempool 优先级 |

### 7.2 中心化风险详解

#### 7.2.1 审查风险（Censorship）

**风险等级：中**

Sequencer 可以选择性排除特定交易或地址的交易。这是所有中心化 Sequencer 的固有风险。

**缓解措施：**
- **强制包含机制：** 用户可以通过 L1 `OptimismPortal` 提交强制包含交易（deposit transaction），绕过 Sequencer 审查。
- **最大延迟：** L2BEAT 记录最大强制包含延迟为 **~12 小时**（由 `SeqWindowSize` 和 `MaxSequencerDrift` 参数决定）。
- **企业影响：** 12 小时延迟对某些企业用例可能不可接受。企业 fork 可缩短此窗口，但需权衡 Sequencer 运营灵活性。

#### 7.2.2 MEV 提取风险

**风险等级：中**

中心化 Sequencer 具有完全的交易排序权力，理论上可以进行前跑（frontrunning）、三明治攻击（sandwich attacks）或其他 MEV 提取。

**当前状态：**
- Mantle 的预确认模块使用 FIFO 排序，在一定程度上限制了 MEV
- 无公开的 MEV 提取策略或承诺
- L2BEAT 明确标注："The Sequencer can censor and frontrun user transactions"

**企业影响：** 企业场景中，Sequencer 由企业自身运营，MEV 风险可通过运营治理消除。但跨组织场景中需要额外的公平排序保证。

#### 7.2.3 Proposer 失效风险

**风险等级：⚠️ CRITICAL**

**当前状态：** 仅白名单 Proposer（EOA: `0x6667...d77D`）可以提交 state root 到 L1。

**L2BEAT 标注：** "The centralized validator goes down. Users cannot produce blocks themselves and exiting the system requires new block production."（中心化验证者宕机。用户无法自行生产区块，退出系统需要新区块的生产。）

**影响分析：**
- 如果 Proposer 下线，新的 L2 state root 无法提交到 L1
- 用户无法发起 withdrawal——因为 withdrawal 需要 L1 上已验证的 output root
- 资金不会丢失（L2 数据在 L1 上可用），但会被**冻结**直到 Proposer 恢复
- 在 ZK 模式下风险更大：需要 SP1 Prover + Proposer 同时在线

**企业影响：** 企业 fork 应考虑：(1) 多 Proposer 白名单机制；(2) Proposer 失效时的紧急恢复流程；(3) 独立运营的 Proposer 基础设施。

#### 7.2.4 强制包含延迟

| 参数 | 值 | 影响 |
|------|-----|------|
| `SeqWindowSize` | 配置值（epochs） | Sequencer 必须在此窗口内包含 L1 deposit |
| `MaxSequencerDrift` | 配置值（秒） | L2 时间与 L1 时间的最大偏差 |
| **实际最大延迟** | ~12 小时 | L2BEAT 计算值 |

#### 7.2.5 升级与多签信任

**风险等级：⚠️ CRITICAL**

| 治理角色 | 实体 | 权限 | 延迟 |
|---------|------|------|------|
| `MantleSecurityMultisig` | 6/14 多签 | 升级所有核心合约、切换 ZK/Optimistic 模式 | **零延迟** |
| `TimelockController` | — | 仅 L1MantleToken 修改 | 1 天 |
| Sequencer 运营 | Mantle 团队 EOA | 区块生产、交易排序 | — |
| Proposer | 白名单 EOA | 状态根提交 | — |

**风险：** 6/14 多签意味着仅需 6 个签名者即可即时升级所有合约。如果多签密钥泄露，攻击者可以修改合约逻辑窃取资金，且用户没有退出窗口。

**企业启示：**
- 企业 fork 必须添加合约升级时间锁（建议 7-14 天）
- 考虑将治理多签阈值提高到更保守的比例（如 8/14 或更高）
- 需建立独立的紧急暂停机制
- Sequencer 和 Proposer 的密钥管理应使用 HSM（Mantle 已有 GCP KMS 支持）

---

## 8. 企业适配潜力

### 8.1 评估表

| 维度 | 当前状态 | 企业需求 | 适配难度 | 备注 |
|-----------|--------------|-----------------|----------------------|-------|
| **访问控制** | 无许可。任何地址都可以提交交易。Sequencer 接受所有有效交易。 | 可配置访问：白名单/黑名单、基于角色的权限、交易级过滤。 | **中等**（扩展/插件） | Sequencer（`op-node/rollup/sequencing/sequencer.go`）和交易池（`op-geth/core/txpool/`）是天然插入点。Sequencer 级别的交易过滤器可以实现访问控制。op-node 和 op-geth 之间的 Engine API 边界提供了清晰的拦截点。 |
| **数据隐私** | 所有 L2 交易数据均为公开：以 blobs/calldata 形式发布到 L1，在 L2 状态中可见。 | 选择性隐私：加密交易、私有状态、保密计算。 | **极高**（架构重设计） | L1 数据发布是 rollup 安全模型的基础（无论 Optimistic 还是 ZK——ZK 证明状态正确性，但不隐藏交易数据）。加密批次数据会破坏 derivation pipeline 和证明系统。私有执行覆盖层或保密计算方案需要根本性的架构重构。 |
| **身份管理** | 基于地址（secp256k1 密钥）。无身份层。 | KYC + 企业身份：X.509 证书、OIDC 集成、身份注册表。 | **中等**（扩展/插件） | 可作为上层添加：身份注册合约 + sequencer/交易池策略执行。op-geth 的账户管理（`accounts/`）和 op-service 的签名者基础设施提供了集成点。gas-oracle 中已有 HSM 支持。 |
| **合规/审计** | 无结构化合规支持。所有数据在链上，但未为合规目的组织。 | 内置合规：审计追踪、监管报告、数据保留策略。 | **中等**（扩展/插件） | 可利用现有 L2 predeploy 模式构建基于事件的审计追踪。合规规则可在 Sequencer 级别执行。结构化的 L1 批次提交已提供防篡改排序。 |
| **Sequencer 控制** | 中心化单一 Sequencer（由 Mantle 团队运营）。op-conductor 在 Sequencer 副本之间提供 HA 故障转移。 | 企业可控：组织运营的 Sequencer、可配置的区块参数、交易排序策略。 | **低**（配置变更） | Sequencer 已经是中心化且可配置的。企业可通过控制 op-node 并设置 `--sequencer.enabled` 来运行自己的 Sequencer。op-conductor 已支持 leader election。区块时间、gas 限制和批次参数均可配置。 |
| **DA 策略** | L1 blobs（公开）。遗留 EigenDA 支持。Alt-DA 框架可用。 | 可选的私有 DA：加密 blobs、许可制 DA 委员会、私有 DA 层。 | **中等**（扩展/插件） | Alt-DA 框架（`op-alt-da/`）已提供可插拔 DA 接口。企业可在 `DAClient` HTTP 接口后实现私有 DA 服务端。`GenericCommitment` 类型专为外部 DA 提供者设计。 |
| **EVM 兼容性** | 完全 EVM 兼容。标准 Ethereum JSON-RPC。 | 必须保持 EVM 兼容性。 | **无差距** | Mantle 保持完全 EVM 兼容。Solidity 合约、标准工具（Hardhat、Foundry 等）均可正常工作。Arsia 升级在通过 predeploy 合约引入新费用模型的同时明确保持了兼容性。 |
| **Gas 赞助** | Meta-transaction 基础设施已存在（V1-V3 sponsor 模型）但**在 EverestTime 已禁用**。 | 为终端用户提供企业 gas 补贴。 | **低-中等**（重新启用 + 扩展） | 完整的 meta-tx gas 赞助系统已经实现（`core/types/meta_transaction.go`，状态转换集成）。它是被禁用而非删除。相比从零构建，重新启用并适配企业用途（如组织代付 gas）非常直接。 |
| **终局性** | **ZK 模式（默认）：** ~1 小时终局性（SP1 证明生成 + 验证后 withdrawal 可执行）。**Soft finality：** ~2 秒（Sequencer 确认）。**Safe finality：** ~12 分钟（L1 批次确认）。**预确认：** 同步 receipt（区块密封前返回）。**Optimistic 回退：** 7 天挑战期（`MantleSecurityMultisig` 切换时）。 | 分钟或秒级硬终局性。 | **低-中等**（已基本满足） | ZK 模式下 ~1 小时终局性已显著优于 7 天。企业可利用：(1) Sequencer 确认（~2s soft finality）+ 经济担保用于日常交易，(2) ZK 证明（~1h）用于跨链 withdrawal 和高价值结算，(3) 预确认模块（`op-geth/preconf/`）提供密码学预确认收据——基础设施已就绪。企业 fork 可进一步优化 SP1 证明生成速度或运行私有 Prover 集群。**关键风险：** `MantleSecurityMultisig` 可切换回 Optimistic 模式，导致终局性退化为 7 天——企业 fork 应限制此切换权限。 |
| **吞吐量** | 标准 OP Stack 吞吐量（~50-200 TPS，取决于交易复杂度）。2 秒区块时间。 | 企业级：数千 TPS，可配置区块时间。 | **低-中等** | 区块时间在 rollup 配置中可调。Gas 限制通过 SystemConfig 可配置。更高 TPS 可通过：缩短区块时间、增加 gas 限制、优化 op-geth 执行来实现。Preconf 模块可能有助于并行区块构建。 |
| **治理** | 通过 deposit 交易实现链上升级（predeploy 合约升级）。链下治理。 | 可配置治理：多签管理员、升级时间锁、基于角色的管理。 | **低**（配置变更） | L1 上的 `SystemConfig` 合约已管理关键参数（gas 限制、batcher 地址、scalar）。L1 合约可配置多签所有权。OperatorFeeVault 有可配置的接收方。 |

### 8.2 难度定义

- **低**（配置变更）：通过配置参数、部署选项或合约级变更即可实现，无需修改核心协议代码。
- **中等**（扩展/插件）：需要新的模块/服务或对现有组件的扩展，但不改变核心协议机制。
- **高**（核心协议修改）：需要变更核心协议逻辑（共识、derivation、状态转换），影响安全假设。
- **极高**（架构重设计）：需要对架构进行根本性重新思考，可能破坏 rollup 模型的核心安全属性。

---

## 9. 关键约束与限制

### 9.1 基本约束

1. **ZK Validity Proof 安全模型（当前）+ Optimistic 回退：** Mantle 当前使用 SP1 ZK Validity Proof 作为主状态验证路径，终局性约 1 小时。但 `MantleSecurityMultisig` 可切换回 Optimistic 回退模式（7 天挑战期）。ZK 模式依赖 SP1 Prover 的持续可用性和 Plonk/Gnark 可信设置的安全性。企业需评估这些密码学假设是否满足其安全标准。

2. **L1 数据发布要求：** 所有交易数据必须以 blobs/calldata 形式发布到 L1（Arsia 后 EigenDA 已移除），以支持状态派生和证明验证。这从根本上限制了数据隐私——任何人都可以从 L1 数据派生完整的 L2 状态。这是对企业隐私需求最为棘手的单一约束。ZK 证明不改变此约束：ZK 证明验证状态转换正确性，但不隐藏交易数据本身。

3. **单一 Sequencer 架构：** 虽然 op-conductor 提供 HA，但架构假定单一活跃 Sequencer。真正的多 Sequencer 或去中心化排序需要协议变更（共享排序、基于排序或 Sequencer 之间的共识）。

4. **MNT 原生代币：** MNT 代币集成（gas oracle、token ratio、费用计算）深度嵌入。切换到不同的原生代币或添加多 gas 代币支持需要横跨 op-geth 的成本模型、gas oracle 和 predeploy 合约的变更。

5. **分叉对齐复杂性：** Mantle 的 `AlignOpWithMantle()` 将多个 OP Stack 分叉映射到单个 Mantle 分叉。这简化了升级，但意味着 Mantle 无法选择性地采用单个 OP Stack 分叉功能——每个 Mantle 分叉都是全有或全无的。企业运营者在 Arsia 分叉点继承所有 OP Stack 升级作为单一原子事件。

6. **双代币 Withdrawal 复杂性：** `MantleWithdrawalTransaction` 同时携带 `MNTValue` 和 `ETHValue`，这是 Mantle 独有的。Bridge 合约（`MantleOptimismPortal`、`MantleL1StandardBridge`、`MantleL2ToL1MessagePasser`）均偏离标准 OP Stack bridge 接口。任何 bridge 修改或 L3 堆叠都需要考虑这种双代币模型。

### 9.2 技术债务 / 复杂性

1. **双 Blob 格式：** `MantleBlobDataSource` 的回退逻辑增加了复杂性。Arsia 后系统过渡到标准 blob 格式，但必须为历史 derivation 保持向后兼容。`blobSourceChanged` latch 在 L1 reorg 时正确重置。

2. **遗留 EigenDA 字段：** 配置中的 `MantleDaSwitch` 和 `DataLayrServiceManagerAddr` 是遗留产物，无活跃代码消费。它们增加了对实际 DA 机制的理解混淆。

3. **注释掉的代码：** `op-node/rollup/mantle_chain_spec.go` 包含注释掉的分叉映射代码，表明分叉管理系统正在进行中重构。

4. **已禁用的 Meta-Transactions：** 完整的 meta-tx 基础设施保留在 op-geth 中（类型、状态转换、交易池），但自 Everest 以来已禁用。增加了维护负担和代码表面积。

5. **三层 Fork 链：** op-geth 是 `go-ethereum → op-geth → Mantle`，使上游合并变得复杂。`fork.yaml` 记录了基础 geth hash（`a38f4108`）用于追踪。

### 9.3 运营依赖

运行 Mantle V2 节点需要：
1. **op-geth**（fork 的执行客户端）— 非标准 go-ethereum
2. **Token ratio oracle**（`gas-oracle/`）— 必须持续运行；否则链上比率将偏离市场价格
3. **Beacon node**（用于 blob DA）— 标准 EIP-4844 beacon node，用于 blob sidecar 检索
4. **SP1 Prover + OP Succinct Output Submitter**（ZK 模式）— 外部/部署层基础设施（非仓库内组件），用于生成 SP1 ZK 证明并提交到 `OPSuccinctL2OutputOracle`；Prover 停机将阻止新 state root 提交（可由 `MantleSecurityMultisig` 切换到 Optimistic 回退模式，此时可使用仓库内标准 `op-proposer` 作为临时措施）
5. **DA 服务端**（如使用 alt-DA）— 任何实现 OP Stack DA 协议的 HTTP 服务端
6. **GCP KMS**（如使用 HSM）— 或适配到其他 KMS 提供者（AWS KMS、HashiCorp Vault）

### 9.4 最难变更的部分

按难度排序：

1. **数据隐私**（极高）— 破坏 rollup 基本假设（ZK 证明在此无能为力——它们证明状态正确性，而非数据保密性）
2. **治理/升级时间锁**（高）— 添加有意义的退出窗口需要变更所有 L1 proxy 合约和多签治理
3. **Derivation pipeline**（高）— 核心状态派生逻辑深度耦合
4. **L1 费用模型**（中-高）— 嵌入在 op-geth 状态转换和 predeploy 中
5. **硬终局性优化**（中等）— ZK 模式已提供 ~1h 终局性，进一步优化需要 SP1 Prover 加速或并行证明
6. **Sequencer 访问控制**（中等）— 需要在 Sequencer + 交易池中引入策略引擎
7. **DA 策略**（中等）— Alt-DA 框架已提供插件架构
8. **区块参数**（低）— 已可配置
9. **治理/管理**（低）— L1 合约所有权模式

---

## 10. 天然插入点

以下是架构中可以在对现有代码最小干扰的情况下添加企业功能的位置：

### 10.1 交易准入控制

**位置：** `op-geth/core/txpool/` 和 `op-node/rollup/sequencing/sequencer.go`

交易池已有过滤逻辑（L1 成本感知、blob pool 限制）。在此添加基于策略的过滤器可以控制哪些交易进入内存池以及哪些被排序。

**方法：** 实现 `TransactionPolicy` 接口并在以下位置检查：
- `op-geth/core/txpool/legacypool/legacypool.go`（交易池准入）
- `op-geth/miner/`（区块构建包含）
- `op-node/rollup/sequencing/`（Sequencer 级过滤）

### 10.2 可插拔 DA 后端

**位置：** `op-alt-da/daclient.go` 和 `op-alt-da/daserver.go`

Alt-DA 框架已提供基于 HTTP 的客户端/服务端接口。企业 DA 需求（加密存储、许可制访问、私有 DA 委员会）可在此接口后实现。

**方法：** 实现自定义 `DAServer`，具备：
- 加密 blob 存储
- 访问控制检索
- 私有 DA 委员会验证
- `GenericCommitment` 类型已专为此用例设计

### 10.3 身份注册 Predeploy

**位置：** L2 predeploy 合约（遵循 `L1Block`、`GasPriceOracle` 的模式）

Mantle 已广泛使用 predeploy 合约模式。一个部署在保留地址（如 `0x4200000000000000000000000000000000000020+`）的身份注册 predeploy 可以将 Ethereum 地址映射到企业身份声明。

**方法：** 通过 Mantle 风格的升级 deposit 交易部署（与 `arsia_upgrade_transactions.go` 相同的模式），由 Sequencer 和交易池检查注册表。

### 10.4 带策略引擎的自定义 Sequencer

**位置：** `op-node/rollup/sequencing/sequencer.go`，接口定义在 `op-node/rollup/sequencing/iface.go`

Sequencer 接口定义明确。企业 Sequencer 可以实现自定义排序策略、交易过滤和合规规则。

**方法：** `SequencerStateListener` 和 `AsyncGossiper` 接口允许可插拔行为。标准 Sequencer 的包装器可以添加：
- 交易排序策略（如 FIFO、基于身份的优先级）
- 区块级合规检查
- 审计事件发射

### 10.5 Engine API 中间件

**位置：** op-node 和 op-geth 之间（Engine API 边界）

Engine API（`ForkchoiceUpdated`、`NewPayload`、`GetPayload`）是一个清晰的 RPC 边界。此处的企业中间件层可以：
- 记录所有状态转换用于审计
- 执行区块级策略
- 向 payload 属性添加元数据

### 10.6 Gas Oracle 扩展

**位置：** `gas-oracle/`

Gas oracle 已经展示了如何运行一个特权链下服务来更新链上状态。此模式可扩展用于：
- 企业可配置费用模型
- 合规数据源
- 身份 oracle 更新
- 企业逻辑所需的外部数据源

**关键优势：** 已通过 Google Cloud KMS（`op-service/hsm/`）支持 HSM。

### 10.7 预确认模块增强

**位置：** `op-geth/preconf/`

现有预确认模块为快速交易确认提供了带排序保证的基础设施。这直接与需要亚秒级"soft finality"的企业用例相关。

**方法：** 扩展 preconf，具备：
- 绑定的 Sequencer 承诺
- 密码学预确认收据
- 与企业身份集成的合格预确认

### 10.8 Meta-Transaction 基础设施（企业 Gas 策略先例）

**位置：** `op-geth/core/types/meta_transaction.go`、`op-geth/core/state_transition.go`

已禁用的 meta-transaction 系统展示了在状态转换层面的完整 gas 赞助实现。虽然在主网上已禁用（自 Everest 以来），但代码完好，可作为企业 gas 策略的模板。

**方法：** 以企业特定修改重新启用：
- 组织代付 gas 模型（sponsor = 企业部署者）
- 基于百分比的费用分摊
- 通过身份注册 predeploy 实现 sponsor 白名单
- 与合规规则集成（仅赞助已批准的交易）

### 10.9 Batcher 节流策略扩展

**位置：** `op-batcher/batcher/throttler/`

`ThrottleStrategy` 接口清晰且可插拔。企业用例可能需要自定义节流：
- 基于 SLA 的策略（为优先租户保证吞吐量）
- 成本感知策略（预算限制的 L1 gas 支出）
- 合规驱动策略（监管窗口的批次提交时序）

**方法：** 实现新的 `ThrottleStrategy` 并注册到 `ThrottleController` — 无需变更 batcher 核心。

### 10.10 合规事件系统

**位置：** 新服务，遵循 `op-service/` 的模式

合规事件服务可以：
- 通过 op-geth WebSocket 订阅 L2 区块
- 从交易 traces 中提取结构化审计事件
- 输出到企业合规系统（SIEM、GRC 平台）
- 利用现有的指标基础设施（`op-service/metrics/`）进行可观测性

---

## 附录 A：仓库地图

```
mantle-v2/                          # Mantle V2 主 monorepo（Go）
├── op-core/
│   ├── forks/mantle_forks.go       # 分叉名称和排序（MANTLE）
│   └── predeploys/addresses.go     # OperatorFeeVault 0x...001B（MANTLE）
├── op-node/                        # 共识层（已定制化）
│   └── rollup/
│       ├── derive/                 # Derivation pipeline
│       │   ├── mantle_blob_source.go    # Mantle blob 解码
│       │   ├── mantle_pipeline.go       # Mantle 分叉转换
│       │   ├── mantle_system_config.go  # 系统配置解析
│       │   ├── arsia_upgrade_transactions.go  # Arsia 升级交易
│       │   └── l1_block_info.go         # L1 区块信息（+ Arsia 格式）
│       ├── sequencing/             # Sequencer 实现
│       ├── mantle_types.go         # Mantle 分叉定义 + AlignOpWithMantle
│       ├── mantle_chain_spec.go    # 分叉映射（已注释掉）
│       └── types.go                # Rollup 配置（+ Mantle 字段）
├── op-batcher/                     # 批次提交器（显著定制化）
│   └── batcher/
│       ├── driver.go               # ThrottleController 集成
│       ├── config.go               # 节流配置
│       └── throttler/              # 4 种可插拔策略（Linear/Quadratic/Step/PID）
├── op-proposer/                    # 状态根提交器（上游）
├── op-alt-da/                      # Alt-DA 框架（上游）
│   ├── daclient.go                 # HTTP DA 客户端
│   ├── daserver.go                 # HTTP DA 服务端
│   ├── damgr.go                    # 挑战管理器
│   └── commitment.go               # Keccak256 + Generic commitment 类型
├── op-challenger/                  # 争议博弈代理（上游）
├── cannon/                         # MIPS 故障证明虚拟机（上游）
├── op-conductor/                   # HA Sequencer（上游）
├── op-service/                     # 共享库（上游 + MANTLE 新增）
│   ├── hsm/hsm_signer.go          # GCP KMS 签名（MANTLE）
│   ├── flags/mantle_flags.go      # Fork override CLI 标志（MANTLE）
│   └── txintent/bindings/          # Mantle 特有合约 bindings
│       ├── MantleOptimismPortal.go     # 双代币 withdrawal
│       ├── MantleL1StandardBridge.go   # MNT bridge 函数
│       ├── MantleL2ToL1MessagePasser.go # ETH 显式 withdrawal
│       └── GasPriceOracle.go           # TokenRatio + IsArsia
├── gas-oracle/                     # Token ratio oracle（MANTLE 特有）
│   ├── oracle/
│   │   ├── gas_price_oracle.go     # Oracle 服务 + ensure()
│   │   ├── token_ratio.go          # 链上结算
│   │   └── config.go               # Oracle 配置
│   └── tokenratio/
│       ├── tokenratio.go           # CEX/DEX 聚合
│       ├── tokenratio_dex.go       # DEX 来源
│       └── tokenratio_v1.go, v5.go # 比率计算版本
├── op-acceptance-tests/            # Mantle 特有验收测试
│   └── mantle-tests/
│       ├── arsia/fees_test.go      # 费用公式验证
│       └── custom_gas_token/       # CGT 模式探测
├── packages/contracts-bedrock/
│   └── deploy-config/
│       ├── mantle-mainnet.json     # Chain 5000 配置
│       └── mantle-sepolia.json     # Chain 5003 配置
└── kona/                           # Rust 子模块引用

op-geth/                            # 执行层（大量定制化）
├── core/
│   ├── types/
│   │   ├── rollup_cost.go          # 带 token ratio 的 L1 成本（已定制化）
│   │   ├── deposit_tx.go           # EthValue/EthTxValue 字段（已定制化）
│   │   └── meta_transaction.go     # Meta-tx gas 赞助（MANTLE，已禁用）
│   ├── state_transition.go         # BVM_ETH 铸造/转账、meta-tx、operator fee（已定制化）
│   ├── vm/contracts.go             # 4 个 Mantle 预编译合约集（已定制化）
│   └── txpool/
│       ├── txpool_preconf.go       # 预确认交易池（MANTLE）
│       └── blobpool/
│           └── blobpool_preconf.go # 预确认 blob 池（MANTLE）
├── preconf/                        # 预确认模块（MANTLE 特有，11 个文件）
│   ├── fifo_tx_set.go              # FIFO 排序
│   ├── miner_config.go             # 预确认矿工配置
│   └── tx_pool_config.go           # 预确认交易池配置
├── miner/
│   ├── worker.go                   # DA footprint 限制器（已定制化）
│   ├── preconf_checker.go          # 预确认 L1 deposit 预取（MANTLE）
│   └── miner_preconf.go            # 预确认区块填充（MANTLE）
├── superchain/                     # Superchain 注册表（嵌入 ZIP）
├── params/
│   ├── mantle.go                   # Mantle 链特有参数（MANTLE）
│   └── config.go                   # 9 个分叉时间戳、ApplyMantleUpgrades（已定制化）
├── internal/ethapi/api.go          # 自定义 RPC（已定制化）
├── cmd/
│   ├── keeper/                     # zkVM guest 二进制文件（MANTLE）
│   └── workload/                   # RPC 测试套件（MANTLE）
└── fork.yaml                       # 三层 fork 文档

kona/                               # 基于 Rust 的 OP Stack 组件（FORK）
├── bin/
│   ├── client/                     # 故障证明客户端
│   ├── host/                       # Preimage oracle host
│   ├── node/                       # Rollup node（Rust）
│   └── supervisor/                 # 互操作 supervisor
└── crates/
    ├── proof/                      # 证明 SDK、执行器、MPT
    ├── protocol/                   # Derivation、协议类型
    │   └── genesis/src/rollup.rs   # 双时间戳模型（MANTLE）
    ├── node/                       # Node 服务、engine、P2P
    └── supervisor/                 # Supervisor 服务
```

## 附录 B：链配置

### 主网（Chain ID 5000）

**来源：** `packages/contracts-bedrock/deploy-config/mantle-mainnet.json`

| 参数 | 值 | 备注 |
|-----------|-------|-------|
| L1 链 | 1（Ethereum 主网） | |
| L2 链 | 5000 | |
| L1 MNT Token | `0x3c3a81e81dc49a522a592e7622a7e711c06bf354` | Ethereum 上的 ERC-20 |
| 初始 Token Ratio | 4000 | 1 ETH = 4000 MNT |
| L2 区块时间 | 2 秒 | |
| 终局化周期 | 604800 秒（7 天） | Optimistic 回退模式下的挑战期；ZK 模式下终局性约 ~1 小时 |
| 治理代币 | MNT | |

### Sepolia 测试网（Chain ID 5003）

**来源：** `packages/contracts-bedrock/deploy-config/mantle-sepolia.json`

| 参数 | 值 | 备注 |
|-----------|-------|-------|
| L1 链 | 11155111（Sepolia） | |
| L2 链 | 5003 | |
| L1 MNT Token | `0x65e37B558F64E2Be5768DB46DF22F93d85741A9E` | Sepolia 测试代币 |
| 初始 Token Ratio | 4500 | 与主网不同 |
| 终局化周期 | 1800 秒（30 分钟） | 为测试加速 |

## 附录 C：关键配置参数

来自 `op-node/rollup/types.go` Config 结构体：

| 参数 | 类型 | 企业相关性 |
|-----------|------|---------------------|
| `BlockTime` | uint64 | 可配置的区块间隔 |
| `MaxSequencerDrift` | uint64 | 与 L1 时间的最大偏移 |
| `SeqWindowSize` | uint64 | 排序窗口（epochs） |
| `ChannelTimeoutBedrock` | uint64 | Channel 超时 |
| `BatchInboxAddress` | address | L1 上批次发送目标 |
| `DepositContractAddress` | address | L1 存款桥 |
| `L1SystemConfigAddress` | address | 链上配置 |
| `AltDAConfig` | struct | 替代 DA 设置 |
| `MantleDaSwitch` | bool | 遗留 EigenDA 开关 |
| `MantleBaseFeeTime` 至 `MantleArsiaTime` | *uint64 | Mantle 分叉激活时间 |

## 附录 D：Mantle 分叉时间线

```
Genesis ─── BaseFee ─── Everest ─── Euboea ─── Skadi ─── Limb ─── Arsia
                │           │          │         │         │        │
                │           │          │         │         │        └─ Canyon+Delta+Ecotone+Fjord+
                │           │          │         │         │           Granite+Holocene+Isthmus+Jovian
                │           │          │         │         └─ Arsia 前准备
                │           │          │         └─ Engine API V4, NewPayloadV4
                │           │          └─ 优化
                │           └─ Blob DA (MantleBlobDataSource)
                └─ 自定义 base fee 机制
```
