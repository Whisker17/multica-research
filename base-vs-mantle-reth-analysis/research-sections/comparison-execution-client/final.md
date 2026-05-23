# Execution Client 各维度对比表

## 总览对比

| 维度 | Base (`base/base`) | Mantle reth (`mantle/reth`) | Mantle op-geth (`mantle/op-geth`) |
|------|-------------------|---------------------------|----------------------------------|
| **语言** | Rust | Rust | Go |
| **上游** | `paradigmxyz/reth` v2.2.0（pin） | `paradigmxyz/reth` v1.9.3（fork） | `ethereum-optimism/op-geth`（fork） |
| **上游策略** | Pin & Extend（零修改） | Fork & Modify（含 3 个依赖 fork） | Fork & Modify（深度侵入） |
| **本地快照版本** | reth v2.2.0 | reth v1.9.3 | 未量化 |

## 1. 上游关系

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| 依赖方式 | `git pin tag = "v2.2.0"` | fork branch `mantle-arsia` | fork |
| 上游代码修改 | 0（仅一处 copy + diff 注释） | 中（散布在 optimism/ 目录） | 高（core/、params/、consensus/ 深度修改） |
| 依赖库 fork | 0 | 3（revm, alloy-evm, op-alloy） | 0（但直接修改 go-ethereum 代码） |
| 升级成本 | 低（bump tag） | 高（5 仓库级联 rebase） | 高（大量合并冲突） |
| 代码边界 | 清晰（独立 crate 目录） | 中（散布 + 新增 crate） | 模糊（嵌入核心路径） |

## 2. EVM 定制

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| 定制方式 | trait 组合（`ConfigureEvm`） | `MantleHardforks` trait bound + revm fork | 直接修改 `core/vm/` |
| Spec 选择 | `BaseSpecId` | `OpSpecId::ARSIA`（revm fork 新增） | `activePrecompiledContracts(rules)` |
| 预编译管理 | `PrecompilesMap` 哈希表 + 动态安装 | 委托给 revm fork | 5 套硬编码分叉表 |
| 动态预编译 | Beryl 支持（B20、Policy 等） | 无 | 无 |
| P256 支持 | Fjord（标准 EIP-7212） | Everest（`p256VerifyEverest` 私有实现 at 0x100） | Everest（私有实现 at 0x100） |
| BLS12-381 | Isthmus（带修改） | Skadi | Skadi |
| MODEXP | Azul（Osaka 定价） | Limb | Limb |

## 3. Gas 模型

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| 原生代币 | ETH | MNT（通过 revm fork） | MNT（直接实现） |
| L1 Data Fee | 标准 OP（Ecotone/Fjord） | tokenRatio 乘法（通过 `RethL1BlockInfo`） | tokenRatio 乘法（完整实现） |
| Token Ratio | 无需 | 从 `GasOracleAddr` slot 0 读取 | 从 `GasOracleAddr` slot 0 读取 |
| Operator Fee | 无 | 通过 revm fork 间接支持 | 完整实现（slot 8, Arsia） |
| Gas Estimation | 标准 + metering 优先费 | op-geth 对齐（无 120% buffer） | Mantle 调整 |
| 资源计量 | 多维度（gas/DA/state-root/opcode） | 无 | 无 |

## 4. 交易池

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| 验证器 | `BaseTransactionValidator` | `OpTransactionValidator` + MetaTx 拒绝 | 标准 + MetaTx 验证 |
| 排序 | `BaseOrdering` / `TimestampOrdering` | 标准 OP | 标准 |
| Bundle 支持 | `eth_sendBundle`（完整） | 无 | 无 |
| 交易转发 | 独立 crate | 标准 OP | 标准 |
| DA 估算 | `estimated_da_size` | 无 | 无 |
| Tracing | 独立 crate | 无 | 无 |
| Preconf 交易 | 无 | 无 | 完整（FIFO set + 白名单） |

## 5. Flashblocks

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| Producer | 自研（`FlashblocksServiceBuilder`） | 使用外部 `op-rbuilder` + `rollup-boost`，`op-conductor` relay | 无 |
| Consumer | 完整（状态重建 + 缓存执行 + RPC） | 基础（状态重建 + RPC） | 无 |
| 默认状态 | Producer 始终开启 | 关闭（opt-in） | N/A |
| Engine 集成 | `CachedExecutor`（跳过已执行 tx） | 无 | N/A |
| 资源预算 | per-flashblock 执行时间/状态根/DA | 无 | N/A |
| 子块间隔 | 250ms（可配置） | N/A | N/A |
| RPC 订阅 | newFlashblocks / pendingLogs / newFlashblockTransactions | pending block/receipt/tx | N/A |

## 6. 状态管理

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| 存储引擎 | MDBX + 专用 FP trie 存储 | MDBX（标准） | Pebble / LevelDB（默认 Pebble） |
| FP 窗口 trie | 独立存储（MDBX + 内存双后端） | 无 | 无 |
| 状态裁剪 | 独立 FP trie pruner | 标准 reth pruning | 标准 geth pruning |
| 状态证明 | 专用 cursor factory + proof API | 标准 | 标准 |
| Deferred trie | 后台 trie 计算（`spawn_deferred_trie_task`） | 无 | 无 |

## 7. RPC 层

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| 架构 | execution rpc + flashblocks rpc + metering rpc | 标准 OP + `MantleEthApiExt` | 标准 + preconf API |
| 自定义方法 | flashblocks 订阅、metering API、builder API | `mantle_getBlockRange`、`mantle_sendRawTransactionWithPreconf`、`mantle_estimateTotalFee` | preconf API |
| Pending 状态 | Flashblock-aware | Flashblock consumer（opt-in） | 标准 |
| Receipt 扩展 | 标准 | token_ratio LRU 缓存 | tokenRatio + operatorFee 字段 |
| Gas Estimation | 标准 OP | op-geth 对齐（无 120% buffer） | Mantle 调整 |

## 8. 网络层

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| P2P 实现 | 自定义 libp2p gossipsub | 标准 reth/OP | 标准 devp2p |
| 节点发现 | 自定义 ENR + BootStore | 标准 discv5 | 标准 discv5 |
| 区块传播 | GossipDriver + BlockHandler | 标准 | 标准 |
| 连接管理 | ConnectionGater + ConnectionGate | 标准 | 标准 |
| Peer 评分 | PeerScoreLevel + PeerMonitoring | 标准 | 标准 |

## 9. 硬分叉

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| 分叉体系 | OP 分叉阶梯（Bedrock → Beryl） | OP 分叉 + Mantle 分叉（Skadi/Limb/Arsia） | OP 分叉 + Mantle 分叉（含早期 BaseFee/MetaTx/Everest） |
| L1 分叉映射 | Shanghai↔Canyon, Cancun↔Ecotone, Prague↔Isthmus, Osaka↔Azul | Prague↔Skadi, Osaka↔Limb | Prague↔Skadi, Osaka↔Limb |
| 独有分叉 | Jovian, Azul, Beryl | Arsia | Arsia + BaseFee + BVMETHMint + MetaTxV2/V3 + ProxyOwner + Everest |

## 10. 特有功能

| 功能 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| MNT 双资产 | 无 | 间接（通过 MantleHardforks） | 完整（state-level BVM_ETH 操作） |
| MetaTx（赞助交易） | 无 | txpool 层拒绝 | 完整 V1/V2/V3 + Everest 禁用 |
| Preconfirmation | 无 | 无 | 完整子系统（`preconf/`） |
| Operator Fee | 无 | 通过 revm fork | 完整（buyGas/refund/routing） |
| 动态预编译 | Beryl（B20/Policy/Activation） | 无 | 无 |
| 资源计量 | 完整（metering crate） | 无 | 无 |
| 专用 trie 存储 | 完整（proofs + trie crate） | 无 | 无 |
| Cached Execution | engine-tree 集成 | 无 | 无 |
| Bundle 支持 | 完整 | 无 | 无 |

## 11. 代码规模概览

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| Execution 子 crate 数 | 20 | ~14（optimism/ 下） + 1（mantle-hardforks） | N/A（单仓库） |
| 新增文件 | 所有 crates/execution/ | mantle-hardforks/, flashblocks/, mantle_ext.rs, mantle.rs, mantle*.rs | preconf/, meta_transaction.go, mantle.go |
| 修改上游文件 | 0 | ~15（evm/build, consensus/proof, txpool/validator, rpc/call 等） | ~30+（core/、params/、consensus/、eth/ 等） |
| 依赖 fork | 0 | 3 个仓库 | 0（但直接修改源码） |


---

# Execution 层定制化对比

## 1. EVM 配置与定制

### Base：BaseEvmConfig + BaseEvmFactory

Base 通过 `ConfigureEvm` trait 实现 EVM 定制，核心组件：

- **`BaseEvmConfig<ChainSpec, N, R, EvmFactory>`**（`crates/execution/evm/src/`）：实现 `ConfigureEvm` 和 `ConfigureEngineEvm<ExecutionData>`，是 EVM 配置的主入口
- **`BaseEvmFactory`**（`crates/common/evm/src/factory.rs`）：实现 `EvmFactory` trait，使用 `PrecompilesMap`（哈希表分发）而非 spec-branch 模式
- **`BaseBlockAssembler<ChainSpec>`**：处理各分叉的区块组装差异（Isthmus withdrawals_root、Canyon、Ecotone、Jovian DA blob_gas_used）
- **`BaseExecutorProvider`**：提供区块执行器
- **`BaseEvmEnvBuilder`**：构建 `EvmEnv`（cfg_env/evm_env/next_evm_env/payload_evm_env）

自定义类型链：`BaseSpecId` → `BaseHaltReason` → `BaseTransaction<TxEnv>` → `BaseHandler` → `BaseEvm`。

**关键设计**：所有 EVM 定制通过 trait 组合，不修改 revm 或 reth 源码。

### Mantle reth：MantleEvmEnvInput + Forked revm

Mantle 的 EVM 定制路径完全不同：

- **`OpEvmConfig`** 加上 `MantleHardforks` trait bound（`crates/optimism/evm/src/lib.rs:120`）
- 所有 `evm_env*` 方法路由到 **`for_mantle(MantleEvmEnvInput)`**（`crates/optimism/evm/src/mantle.rs`），由 `revm_spec_at_timestamp` 选择 spec
- Spec 映射在 `crates/mantle-hardforks/src/lib.rs`：
  - Arsia → `OpSpecId::ARSIA`（Mantle revm fork 新增的 SpecId）
  - Limb → `OpSpecId::OSAKA`
  - Skadi → `OpSpecId::ISTHMUS`
  - 其余 → `alloy_op_evm::spec_by_timestamp_after_bedrock`

**关键差异**：Mantle 需要 fork revm 来添加 `OpSpecId::ARSIA`，而 Base 在 revm 的标准 spec 系统内完成所有定制。

### Mantle op-geth：直接修改 EVM 核心

op-geth 的 EVM 定制是最侵入性的：

- `core/vm/contracts.go`：5 套分叉预编译表（Everest/Skadi/Limb/Arsia + upstream fallback）
- `core/state_transition.go`：MNT/BVM_ETH 双资产处理直接嵌入状态转换
- Gas 计算中的 `tokenRatio` 乘法运算嵌入 `innerExecute()`

## 2. 预编译合约

### Base：模块化预编译 + 动态安装

Base 的预编译系统在 `crates/common/precompiles/src/` 中，采用逐分叉叠加：

| 分叉 | 新增预编译 |
|------|-----------|
| Fjord | `P256VERIFY`（EIP-7212） |
| Granite | 限制 bn254Pairing 输入 |
| Isthmus | Prague BLS12-381 集（带 Isthmus 修改） |
| Jovian | 降低输入限制 |
| Azul | MODEXP / P256VERIFY Osaka 定价 |
| **Beryl** | **动态预编译**：B20Factory、B20（Token/Stablecoin/Security 三种）、PolicyRegistry、ActivationRegistry |

**Beryl 的动态预编译**是 Base 的独特设计——通过 `install()` 方法在运行时注册预编译，由 `activation_admin_address` 控制激活权限。这使得新预编译无需硬分叉即可上线。

`BasePrecompiles<S>` 使用 `PrecompilesMap`（哈希表）而非 spec-branch dispatch，支持运行时动态插入。

### Mantle reth：委托给 revm fork

Mantle reth 自身**不包含预编译模块**。预编译集由 `mantle-xyz/revm` v2.2.2 fork 提供，通过 `revm_spec_at_timestamp` 间接选择。reth 仓库内无法看到预编译实现细节。

### Mantle op-geth：硬编码预编译表

`core/vm/contracts.go` 中定义了 4 套 Mantle 特有预编译表：

| 分叉 | 预编译变化 |
|------|-----------|
| Everest | 标准 1-9 + `p256VerifyEverest{}` at `0x100`（Mantle 私有实现，早于 Prague p256） |
| Skadi | + Prague BLS12-381（`0x0a`-`0x11`），保留 `p256VerifyEverest` at `0x100` |
| Limb | Osaka MODEXP + 标准 `p256Verify{}` 替换 `p256VerifyEverest` at `0x100` |
| Arsia | = Limb（无变化） |

`activePrecompiledContracts(rules)` 按 Arsia → Limb → Skadi → Everest → upstream 顺序 dispatch。

**对比**：Base 的动态预编译机制（Beryl）允许无需硬分叉添加预编译，而 Mantle 的每次预编译变更都需要在 revm fork 或 op-geth 中硬编码。

## 3. Gas 计算模型

### Base：标准 OP Stack Gas

Base 使用标准的 OP Stack L1 data fee 模型（Ecotone → Fjord → Jovian 演进）。L1 fee 以 ETH 计价，无额外转换。

Gas 模型扩展在 `crates/execution/metering/` 中实现：

- **多维度资源计量**：gas、DA bytes、state-root 计算时间、opcode 计数
- **per-flashblock 预算**：执行时间、状态根 gas、DA 字节
- **优先费预估**：`PriorityFeeEstimator` 基于多资源滚动估算
- `MeteringCollector` 通过 EVM `Inspector` 收集数据

### Mantle：Token Ratio 双层 Gas 模型

Mantle 的 gas 模型因 MNT 原生代币而显著复杂化：

**L1 Cost 计算**（`core/types/rollup_cost.go`）：
- Pre-Arsia：标准 Bedrock/Ecotone/Fjord 公式 × `tokenRatio`（MNT/ETH 汇率）
- Post-Arsia：Fjord 公式 × `currentTokenRatio`（无 `/Decimals` 除法）
- `tokenRatio` 从 `GasOracleAddr`（`0x420...000F`）slot 0 读取

**Operator Fee 模型**（Arsia 新增）：
```
operatorFee = (gas × operatorFeeScalar) / 1_000_000 + operatorFeeConstant
```
- 参数从 `GasOracleAddr` slot 8 读取
- `buyGas` 中预扣 L1 cost + operator fee
- 退款时按比例返还

**Gas 购买流程差异**：
- Pre-Arsia：`mgval = gasLimit × gasPrice`，但 gas 在执行时乘以 tokenRatio
- Post-Arsia：`mgval = gasLimit × gasPrice + l1Cost + operatorCost`

**Coinbase 路由**（Arsia）：
- L1 cost → `OptimismL1FeeRecipient`
- Operator fee → `OptimismOperatorFeeRecipient`
- Tip → coinbase

**reth 侧**的 gas 定制通过 `RethL1BlockInfo` trait 注入 `MantleHardforks`，但核心计算逻辑仍依赖 `mantle-xyz/revm` fork。

## 4. 硬分叉阶梯

### Base 硬分叉

完整阶梯（`crates/execution/chainspec/src/hardforks.rs`）：

```
Bedrock → Regolith → Canyon → Ecotone → Fjord → Granite → Holocene → Isthmus → Jovian → Azul → Beryl
```

以太坊主网分叉映射：
- Shanghai ↔ Canyon
- Cancun ↔ Ecotone
- Prague ↔ Isthmus
- Osaka ↔ Azul

Pre-Bedrock 以太坊分叉（Frontier → GrayGlacier）全部 pin 到 block 0。

### Mantle 硬分叉

两套并行的硬分叉系统：

**OP Stack 分叉**（继承上游）：
```
Bedrock → Regolith → Canyon → Ecotone → Fjord → Granite → Holocene → Isthmus → Jovian
```

**Mantle 特有分叉**（`crates/mantle-hardforks/`）：
```
Skadi → Limb → Arsia
```

映射关系（Mainnet 时间戳）：
- Skadi = 1,756,278,000 → 对应 Prague/Isthmus（op-geth 中 `IsMantleSkadiAndOptimism`）
- Limb = 1,768,374,000 → 对应 Osaka
- Arsia = 1,776,841,200 → Mantle 独有（新 L1 cost / operator fee / DA footprint）

**op-geth 还包含更早期的分叉**（`params/mantle.go`）：
- `BaseFeeTime`、`BVMETHMintUpgradeTime`、`MetaTxV2UpgradeTime`、`MetaTxV3UpgradeTime`、`ProxyOwnerUpgradeTime`、`MantleEverestTime`

这些早期分叉是 MNT 原生代币演进的历史记录。

## 5. MNT 双资产模型（Mantle 独有）

这是 Mantle 与 Base 最本质的架构差异——Mantle 的 L2 有两种原生资产：

### 双地址映射

| 地址 | 代表 | 精度 |
|------|------|------|
| `0xDeadDeAddeAddEAddeadDEaDDEAdDeaDDeAD0000` | MNT（原生 gas 代币） | 6 位 |
| `0xdEAddEaDdeadDEadDEADDEAddEADDEAddead1111` | BVM_ETH（影子 ETH ERC-20） | 8 位 |

### State-level BVM_ETH 操作

op-geth 在 `core/state_transition.go` 中直接操作 BVM_ETH 的存储 slot：

- **`mintBVMETH(state, addr, amount)`**：直接写入 `keccak256(leftpad32(addr) || leftpad32(0))`（Solidity `balanceOf` slot）和 `keccak256(2)`（`totalSupply` slot）
- **`transferBVMETH(state, from, to, amount)`**：同样通过 slot 直接操作
- **合成事件**：`generateBVMETHMintEvent` / `generateBVMETHTransferEvent` 在 BVM_ETH 地址上生成 `Mint` / `Transfer` 日志，使区块浏览器看到 ERC-20 语义

### DepositTx 扩展

```go
type DepositTx struct {
    Mint       *big.Int  // MNT 铸造
    Value      *big.Int  // MNT 转账
    EthValue   *big.Int  // BVM_ETH 铸造
    EthTxValue *big.Int  // BVM_ETH 转账给 msg.To
}
```

**Base 完全不需要这套机制**——Base 使用 ETH 作为唯一原生代币，与标准 OP Stack 一致。

## 6. MetaTx（赞助交易）

### Mantle MetaTx V1/V2/V3

op-geth 中完整实现了 MetaTx 框架（`core/types/meta_transaction.go`）：

- `MetaTxPrefix = "MantleMetaTxPrefix"`（32 字节前缀嵌入 calldata）
- `MetaTxParams`：`ExpireHeight`、`SponsorPercent`、`GasFeeSponsor`、签名验证
- V2 增加显式 `From` 字段，V3 强制 `sponsor != sender`
- `buyGas` 中按 `SponsorPercent` 分摊 sponsor 和 sender 的 gas 费
- `returnGasMantle` 按比例退款

**Everest 分叉后永久禁用**（`ErrMetaTxDisabled`）。

Mantle reth 在 txpool 层实现了同步的 MetaTx 拒绝：
- `MetaTxDisabled` 错误类型（`crates/optimism/txpool/src/error.rs`）
- `OpTransactionValidator::validate_one` 中匹配 32 字节 `MANTLE_META_TX_PREFIX`（`validator.rs:220`）

**Base 无 MetaTx 支持**——无需此功能。

## 7. Preconfirmation 子系统（Mantle op-geth 独有）

op-geth 内置了完整的 preconf 子系统（`preconf/` 包）：

- **`PreconfChecker`**：健康检查循环，轮询 op-node 同步状态 + L1 deposit 合约
- **`FIFOTxSet`**：确定性排序的交易集合，含超时清理
- **`TxPoolConfig`**：preconf 交易白名单（`FromPreconfs`、`ToPreconfs`）
- **Deposit log 解析**：重新实现了 op-node 的 `UnmarshalDepositLogEvent`
- **Sync status 镜像**：从 op-node 拷贝 `OptimismSyncStatus` 类型到 op-geth 内部
- **Metrics**：完整的 Prometheus metrics 套件

这是一个**反模式**——将 derivation 层的基本概念（deposit source hash、sync status）嵌入执行客户端，增加了耦合度。Base 的设计相反：执行客户端保持精简，derivation 逻辑放在 kona/reth 对齐的 crate 中。

## 8. Receipt 扩展

### Base

标准 OP Stack receipt 格式，无额外字段。

### Mantle

Receipt 新增 `rlp:"optional"` 字段（`core/types/receipt.go`）：
- `TokenRatio *big.Int`：交易执行**前**捕获的 MNT/ETH 汇率
- `OperatorFeeScalar`、`OperatorFeeConstant`：Arsia 后填充

`core/state_processor.go` 在 `ApplyMessage` 前读取 `statedb.GetState(GasOracleAddr, TokenRatioSlot)`，确保 receipt 中记录的 tokenRatio 可用于离线重算 L1 fee。

Mantle reth 侧通过 `token_ratio_after_logs()` + LRU 缓存实现 fee-accurate receipt 构建。

## 9. 一次性治理操作（Mantle op-geth）

op-geth 的 `state_transition.go` 中硬编码了一次性存储写入：

- **L2ProxyAdmin owner 迁移**：当 `IsProxyOwnerUpgradeBlock` 触发时，直接写入 `L2ProxyAdminAddress`（`0x4200...0018`）slot 0 为 `NewProxyAdminOwnerAddress`

这种将治理迁移逻辑嵌入执行客户端的做法非常罕见，通常应通过系统交易或合约升级实现。

## 10. Holocene / Jovian ExtraData（Mantle Arsia）

Mantle 在 Arsia 分叉引入了 Jovian 风格的 ExtraData 编码（`consensus/misc/eip1559/eip1559_optimism.go`）：

- 17 字节格式：`[version=0x01][denom u32][elasticity u32][minBaseFee u64]`
- `DecodeMinBaseFeeExtraData` / `EncodeMinBaseFeeExtraData`
- Pre-Arsia 拒绝非空 extra-data；Arsia 切换到 `ValidateMinBaseFeeExtraData`

## 关键差异总结

| 维度 | Base | Mantle |
|------|------|--------|
| EVM 定制方式 | trait 组合（ConfigureEvm） | fork revm + 修改 op-geth core |
| 预编译管理 | 动态安装（Beryl） | 硬编码分叉表 |
| Gas 模型 | 标准 OP Stack（ETH） | 双资产 tokenRatio + operator fee |
| 原生代币 | ETH（标准） | MNT + BVM_ETH（双资产） |
| MetaTx | 无 | V1/V2/V3（Everest 后禁用） |
| Preconf | 无（分离架构） | 嵌入 op-geth（反模式） |
| Receipt 扩展 | 标准 | + tokenRatio + operatorFee |
| 资源计量 | 完整多维度系统（metering crate） | 无 |
| 代码侵入度 | 零（trait 扩展） | 高（直接修改核心路径） |


---

# Flashblocks 集成对比：Producer vs Consumer

## 1. 总览

| 仓库 | 角色 | 状态 |
|------|------|------|
| **Base** (`base/base`) | **Producer + Consumer + RPC + Metering** | 始终开启（builder 二进制），完整栈 |
| **Mantle reth** (`mantle/reth`) | **Consumer only** | 默认关闭，通过 `--flashblocks-url` 启用 |
| **Mantle mantle-v2** (`mantle/mantle-v2`) | **Relay / Proxy**（`op-conductor`） | 通过外部 `op-rbuilder` + `rollup-boost` 获取流并转发 |
| **Mantle op-geth** (`mantle/op-geth`) | **无** | 代码库中零引用 |

Base 在自有仓库中构建了完整的 Flashblocks **producer**（`bin/builder` + `FlashblocksServiceBuilder`）。Mantle 本地仓库内没有自研 producer 实现，producer 侧使用外部的 `op-rbuilder`（Reth-based block builder）和 `rollup-boost`（middleware/multiplexer），`op-conductor` 作为 leader-gated WebSocket relay 将 flashblock 流转发给下游 consumer。生产环境是否已启用仍需部署配置确认。

## 2. Base：完整的 Producer + Consumer 架构

### 2.1 Producer 端

#### Builder 二进制（`bin/builder/`）

`bin/builder/src/main.rs` 是 Flashblocks 的入口——**block builder 二进制**：

```rust
runner = BaseNodeRunner::new(rollup_args)
    .with_service_builder(FlashblocksServiceBuilder(builder_config));
```

安装三个扩展：`MeteringStoreExtension` → `TxPoolRpcExtension` → `BuilderApiExtension`。

**Flashblocks 始终开启**——没有开关。CLI 参数只调节行为：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--flashblocks.port` | `1111` | WS server 端口 |
| `--flashblocks.addr` | `127.0.0.1` | WS server 地址 |
| `--flashblocks.block-time` | `250ms` | 子块间隔（4 个 flashblock/秒） |
| `--flashblocks.leeway-time` | `75ms` | 延迟缓冲 |

#### Producer 引擎（`crates/builder/core/src/flashblocks/`）

核心组件：

- **`FlashblocksServiceBuilder`**（`service.rs:33`）：公开入口，创建 `WebSocketPublisher` 绑定到 `flashblocks_ws_addr`
- **`BlockPayloadJobGenerator`** / **`BlockPayloadJob`**（`generator.rs`）：按 `block-time` 间隔生成 flashblock payload
- **`PayloadHandler`**（`handler.rs`）：处理 payload 生命周期
- **`BasePayloadBuilderCtx`** / **`FlashblocksExtraCtx`**（`context.rs`）：builder 上下文
- **`BestFlashblocksTxs`**：交易选择器
- **`PayloadBuilder`** trait（`traits.rs`）

每个 flashblock payload 包含：
- `ExecutionPayloadBaseV1`：基础区块数据
- `ExecutionPayloadFlashblockDeltaV1`：增量交易 + 状态变更
- `Metadata`：元数据

#### 资源计量集成（`crates/execution/metering/`）

Producer 强制执行**per-flashblock 资源预算**：

| CLI 参数 | 说明 |
|----------|------|
| `--builder.flashblock-execution-time-budget-us` | 每个 flashblock 执行时间预算 |
| `--builder.max-execution-time-per-tx-us` | 单笔交易最大执行时间 |
| `--builder.block-state-root-gas-limit` | 状态根 gas 上限 |
| `--builder.state-root-gas-coefficient` | 状态根 gas 系数 |
| `--builder.execution-metering-mode` | off / dry-run / enforce |

`MeteringCollector` 通过 EVM `Inspector` 采集多维度数据：
- **gas 使用**
- **DA bytes**
- **state-root 计算时间**
- **opcode 计数**

`PriorityFeeEstimator` 按 flashblock 粒度估算优先费——"每个 tx-pool flashblock 独立估算，因为 builder 中预算按 flashblock 重置"。

### 2.2 Consumer 端

#### 状态库（`crates/execution/flashblocks/`）

核心组件：

- **`FlashblocksState`**（`state.rs`）：中央 pending 状态容器，`Arc<FlashblocksState>` 在 engine-tree 和 RPC 间共享
- **`FlashblocksSubscriber`**（`subscription.rs`）：WebSocket 客户端，连接 builder
- **`StateProcessor`** / **`StateUpdate`**（`processor.rs`）：处理接收到的 flashblock 增量
- **`PendingBlocks`** / **`PendingBlocksBuilder`**（`pending_blocks.rs`）：构建/管理 pending 区块视图
- **`PendingStateBuilder`** / **`ExecutedPendingTransaction`**（`state_builder.rs`）：从 flashblock 重建执行状态
- **`BlockAssembler`** / **`AssembledBlock`**（`block_assembler.rs`）：区块组装
- **`FlashblockCache`**（`cache.rs`）：缓存层

验证组件（`validation.rs`）：
- **`CanonicalBlockReconciler`**：canonical 区块对账
- **`FlashblockSequenceValidator`**：序列校验
- **`ReorgDetector`** / **`ReorgDetectionResult`**：重组检测
- **`ReconciliationStrategy`**：对账策略

#### Engine Validator 集成（`crates/execution/engine-tree/`）

**`FlashblocksCachedExecutionProvider`**（`cached_execution.rs`）：

从 `FlashblocksState::get_pending_blocks()` 读取已执行的交易结果，跳过重复执行：

1. 验证 `pending_blocks.parent_hash() == parent_block_hash`（防止 reorg 污染）
2. 验证 `transaction_position` 是 `prev_cached_hash` 的直接后继
3. 缓存命中时，通过 `load_cache_account` 将账户加载到执行器 DB 缓存

**`BaseEngineValidator`**（`validator.rs`）：
- 集成 `CachedExecutor`（使用 flashblock 缓存跳过已执行交易）
- `ReceiptRootTaskHandle` 后台任务流式计算 receipt root
- `StateRootStrategy`（`StateRootTask | Parallel | Synchronous`）选择状态根计算策略
- `spawn_deferred_trie_task` 后台计算 trie 数据，验证返回后立即完成

#### 节点扩展（`crates/execution/flashblocks-node/`）

`FlashblocksExtension`：Consumer 节点的 opt-in 扩展。

CLI 参数：
- `--flashblocks-url <ws://...>`：必须提供才启用（alias `--websocket-url`）
- `--max-pending-blocks-depth`：默认 3
- `--flashblocks.cached-execution`：启用 flashblock-aware engine validator

#### RPC 扩展（`crates/execution/flashblocks/src/rpc/`）

完整的 pending 状态感知 RPC：

| RPC 方法 | 说明 |
|----------|------|
| `eth_getBlockByNumber("pending")` | 从 flashblock 状态返回 |
| `eth_getTransactionReceipt` | pending 交易 receipt |
| `eth_call` / `eth_estimateGas`（pending tag） | 基于 flashblock 状态 |
| `eth_getLogs`（pending bound） | 含 pending 日志 |
| `eth_sendRawTransactionSync` | 同步发送交易 |
| `eth_subscribe("newFlashblocks")` | 新 flashblock 订阅 |
| `eth_subscribe("pendingLogs")` | pending 日志订阅 |
| `eth_subscribe("newFlashblockTransactions")` | 新 flashblock 交易订阅 |

通过 `EthApiExt`、`EthApiOverrideServer`、`EthPubSub`、`EthPubSubApiServer` 实现。

### 2.3 Producer ↔ Consumer 连接

```
┌─────────────────────────────────────────┐
│              bin/builder                 │
│  ┌─────────────────────────────────┐    │
│  │  FlashblocksServiceBuilder      │    │
│  │  ┌──────────────────────────┐   │    │
│  │  │ BlockPayloadJobGenerator │   │    │
│  │  │ (每 250ms 生成 flashblock) │   │    │
│  │  └──────────┬───────────────┘   │    │
│  │             │                    │    │
│  │  ┌──────────▼───────────────┐   │    │
│  │  │  WebSocketPublisher      │   │    │
│  │  │  (ws://0.0.0.0:1111)     │   │    │
│  │  └──────────┬───────────────┘   │    │
│  └─────────────│───────────────────┘    │
│  + MeteringExtension (per-flashblock)   │
│  + TxPoolRpcExtension                   │
│  + BuilderApiExtension                  │
└────────────────│────────────────────────┘
                 │ WebSocket stream
                 │ (FlashBlock payloads)
                 ▼
┌─────────────────────────────────────────┐
│         bin/base (full node / RPC)       │
│  ┌─────────────────────────────────┐    │
│  │ FlashblocksSubscriber           │    │
│  │ (--flashblocks-url ws://...)    │    │
│  └──────────┬──────────────────────┘    │
│             │                            │
│  ┌──────────▼──────────────────────┐    │
│  │ StateProcessor → FlashblocksState│    │
│  │ → PendingBlocks                  │    │
│  └──────────┬──────────────────────┘    │
│             │                            │
│  ┌──────────▼──────────────────────┐    │
│  │ BaseEngineValidator             │    │
│  │ (CachedExecutor: 跳过已执行 tx)  │    │
│  └─────────────────────────────────┘    │
│  + EthApiExt (pending RPC overrides)    │
│  + EthPubSub (flashblock subscriptions) │
└─────────────────────────────────────────┘
```

## 3. Mantle 生态：外部 Producer + op-conductor Relay + reth Consumer

### 3.0 Producer 端：op-rbuilder + rollup-boost + op-conductor

Mantle 本地仓库不含自研 Flashblocks producer，而是采用 OP Stack 标准的三进程架构：

1. **op-rbuilder**（外部 Reth-based block builder）：实际的 flashblock 生产者。作为独立子进程运行，通过 `--flashblocks` 标志启用，在 `FlashblocksAddr:FlashblocksPort` 上暴露 WebSocket 流
2. **rollup-boost**（外部 Rust 二进制）：middleware / multiplexer。位于 op-node（CL）与 EL/builder 之间，订阅 op-rbuilder 的 WS 流（`--flashblocks-builder-url`）并在自己的 WS 端口重新暴露
3. **op-conductor**（`mantle-v2/op-conductor/rpc/ws/flashblocks_handler.go`）：leader-gated WebSocket fan-out proxy。订阅 rollup-boost 的 WS 流（`RollupBoostWsURL`），仅当自身为 Raft leader 时将收到的 flashblock 消息广播给下游订阅者；follower 节点静默丢弃消息

Kurtosis devnet 配置（`kurtosis-devnet/flash.yaml`）验证了这一架构：

```yaml
participants:
  node0:
    sequencer: true
    el: { type: op-geth }
    el_builder: { type: op-rbuilder }     # 外部 builder
    mev_params: { enabled: true }
    conductor_params: { websocket_enabled: true }
  node1:
    sequencer: true
    el: { type: op-reth }
    el_builder: { type: op-rbuilder }
flashblocks_rpc_params:
  type: op-reth                           # consumer 是 op-reth
```

Acceptance test（`op-acceptance-tests/tests/flashblocks/flashblocks_stream_test.go`）同时监听 `op-rbuilder` 和 `rollup-boost` 两个 WS 流，确认双层 producer 架构。

**注意**：生产环境是否已启用 Flashblocks 仍需部署配置确认。

### 3.1 Consumer 端：Mantle reth

#### Flashblocks Crate（`crates/optimism/flashblocks/`）

源码注释第一行：**"A downstream integration of Flashblocks."**

模块结构：

| 模块 | 说明 |
|------|------|
| `payload.rs` | `FlashBlock`、`ExecutionPayloadBaseV1`、`ExecutionPayloadFlashblockDeltaV1`（引用 Base Flashblocks 文档） |
| `service.rs` | `FlashBlockService`：消费 WS 流，重建 pending 区块 |
| `worker.rs` | `FlashBlockBuilder`：重新执行收到的交易以组装 `PendingFlashBlock` |
| `sequence.rs` | `FlashBlockPendingSequence` / `FlashBlockCompleteSequence` |
| `consensus.rs` | `FlashBlockConsensusClient`：提交 FCU + new payload 到本地引擎 |
| `ws/` | `WsFlashBlockStream`、`WsConnector`：WebSocket 客户端 |

**依赖是接收侧的**：`tokio-tungstenite`（WS 客户端）、`brotli`（payload 解压）。**无 publisher/server 依赖。**

#### CLI 配置

仅一个参数（`crates/optimism/node/src/args.rs:71-76`）：

```rust
#[arg(long)]
pub flashblocks_url: Option<Url>,
```

默认 `None`，需手动传入 `--flashblocks-url <ws://...>` 启用。无 `--flashblocks.port`、`--flashblocks.block-time` 等 producer 参数。

#### Wiring

- `OpAddOnsBuilder.with_flashblocks(self.args.flashblocks_url.clone())`（`node.rs:201`）
- 当 `flashblocks_url.is_some()` 时（`rpc/src/eth/mod.rs:565-579`）：
  - 创建 `WsFlashBlockStream` 连接
  - 启动 `FlashBlockService`
  - 暴露 `PendingBlockRx` / `FlashBlockCompleteSequenceRx` / `FlashBlockRx` / `InProgressFlashBlockRx` 给 RPC
- 仅影响 RPC 返回（pending tag）——**不驱动 engine 状态**
- `FlashBlockConsensusClient` 存在但**未接入默认节点**

#### Consumer 端局限

- **状态根计算阈值**：仅从 flashblock index ≥ 9 开始计算（`FB_STATE_ROOT_FROM_INDEX = 9`）
- **无 cached execution**——无 engine-tree 层的 flashblock 缓存执行优化
- **无资源计量**——无 per-flashblock 预算 / 优先费估算
- **Brotli 压缩**：consumer 预期 brotli 压缩的 payload（Base 未强制要求）
- **RPC 表面**：pending block/receipt/tx 支持，但无 `newFlashblocks` 等自定义订阅

## 4. Mantle op-geth：零支持

op-geth 代码库中搜索 `flashblock`（不区分大小写）：**零结果**。没有 producer、consumer 或任何 plumbing。

## 5. 维度对比

| 维度 | Base | Mantle |
|------|------|--------|
| Producer | 自研（`FlashblocksServiceBuilder` + `WebSocketPublisher`） | 外部（`op-rbuilder` + `rollup-boost`），`op-conductor` 做 leader-gated relay |
| Consumer 状态库 | 丰富（`FlashblocksState`、`PendingStateBuilder`、`CanonicalBlockReconciler`、`ReorgDetector`、`UnifiedReceiptBuilder`、缓存） | 基础（`FlashBlockService`、`FlashBlockBuilder`、`FlashBlockPendingSequence`） |
| 节点扩展 | 独立 crate（`FlashblocksExtension`） | 内联到 `OpEthApiBuilder::build_eth_api` |
| Engine 集成 | `CachedExecutor`——跳过已执行交易 | 无 engine-tree 集成 |
| RPC | 完整（pending tag、pendingLogs、newFlashblocks、newFlashblockTransactions、`eth_sendRawTransactionSync`） | 基础（pending block/receipt/tx） |
| 默认状态 | Producer 始终开启；Consumer 按需 | 关闭；opt-in |
| Metering | 紧密集成（per-flashblock 预算 + 优先费预估） | 无 |
| 状态根计算 | 所有 flashblock（含 metering 限制） | 仅 index ≥ 9 |
| CLI 参数 | 6+（port、addr、block-time、leeway-time、url、cached-execution） | 1（url） |
| Wire format | `FlashBlock`（Base + rollup-boost 格式） | 兼容（引用同一 Flashbots/rollup-boost 格式） |
| Payload 压缩 | 未见硬依赖 | brotli 压缩 |

## 6. 跨仓库确认

- **Mantle 使用外部 producer**：`mantle-v2` 中 `op-conductor` 连接外部 `rollup-boost` WebSocket（`flashblocks_handler.go`），Kurtosis devnet 配置 `el_builder: type: op-rbuilder`，acceptance test 分别监听 `op-rbuilder` 和 `rollup-boost` 流
- Mantle 本地仓库（reth、op-geth、kona、op-succinct）内无自研 producer 代码——producer 来自外部 `op-rbuilder`（Reth-based block builder）
- Wire format 兼容：两侧都引用 Flashbots/rollup-boost wire format
- Mantle reth 的 `reth-optimism-flashblocks` 自称 "downstream integration"，文档指向 `docs.base.org`——说明这是直接从上游 reth 的 OP 实现继承的代码

## 7. 结论

Base 构建了完整的 Flashblocks 栈——从 producer（每 250ms 生成子块）到 consumer（状态重建 + 缓存执行 + pending RPC），再到 metering（per-flashblock 资源预算 + 优先费预估），形成了一个紧密集成的流水线。

Mantle 采用了不同的 Flashblocks 策略——使用外部 `op-rbuilder` + `rollup-boost` 作为 producer，`op-conductor` 做 leader-gated relay，`mantle/reth` 作为 consumer。这是 OP Stack 标准的三进程 Flashblocks 架构，与 Base 的自研 producer 路径形成对比。

**关键差距**在 consumer 端的集成深度：
1. Mantle reth consumer 缺少 Base 的 `CachedExecutor`（engine-tree 集成，跳过已执行交易）
2. 无 per-flashblock 资源计量和优先费预估
3. RPC 订阅能力受限（无 `newFlashblocks` 等自定义订阅）
4. 生产环境是否已启用 Flashblocks 仍需部署配置确认


---

# Base 设计亮点和 Mantle 可借鉴之处

## Base 设计亮点

### 1. 零 Fork 上游策略

**核心洞察**：Base 证明了一个 L2 可以在**完全不 fork 上游 reth** 的情况下实现深度定制。

Base 通过 reth 的 trait 系统（`ConfigureEvm`、`EvmFactory`、`EngineValidatorBuilder`、`PayloadValidatorBuilder` 等）实现所有 rollup-specific 逻辑。20 个独立的 `crates/execution/` 子 crate 与上游代码有清晰的物理隔离。

**实际价值**：
- 上游升级主要是 **bump tag + 适配 trait 变化**，而非多仓库 rebase
- 代码审计只需关注 `crates/` 目录，无需在上游代码中搜索散布修改
- 不会引入上游 fork 带来的 bug divergence
- 团队精力集中在**业务创新**而非**维护 fork**

### 2. PrecompilesMap + 动态预编译（Beryl）

**核心洞察**：Base 使用哈希表分发（`PrecompilesMap`）而非 spec-branch dispatch，使预编译集可以在运行时动态安装。

Beryl 分叉引入的动态预编译系统（B20Factory、B20 Token/Stablecoin/Security、PolicyRegistry、ActivationRegistry）允许通过 `install()` 方法和 `activation_admin_address` 注册新预编译，**无需硬分叉**。

**对比**：Mantle 的每次预编译变更都需要在 revm fork 或 op-geth 中硬编码一套新的分叉表。

### 3. Flashblocks 完整栈

**核心洞察**：Base 不仅构建了 Flashblocks producer（250ms 子块），还深度集成了 consumer 端的缓存执行和资源计量。

关键集成点：
- **CachedExecutor**：engine-tree 使用 flashblock 已执行结果跳过重复执行（含 parent hash + tx position 严格验证）
- **ReceiptRootTaskHandle**：后台流式计算 receipt root
- **Deferred trie computation**：后台 trie 计算，验证立即返回
- **Per-flashblock metering**：执行时间、状态根 gas、DA 字节预算

这不是一个"附加功能"——它深度影响了 engine validator、payload builder、txpool、RPC 的设计。

### 4. 多维度资源计量

**核心洞察**：`crates/execution/metering/` 实现了超越 gas 的多维度资源计量：

- **gas 使用**
- **DA bytes**（数据可用性成本）
- **state-root 计算时间**
- **opcode 计数**

`PriorityFeeEstimator` 基于这些维度提供滚动优先费估算。Builder 强制执行 per-flashblock 资源预算。这为用户提供了更精准的费用预估，为网络提供了更细粒度的拥塞管理。

### 5. 专用 FP 窗口 Trie 存储

**核心洞察**：`crates/execution/trie/` 是一个独立于 reth 通用 trie 的存储子系统，专为 Fault Proof 窗口内的状态证明查询优化。

设计亮点：
- **双后端**（MDBX + 内存）：按场景选择
- **独立裁剪**：`BaseProofStoragePruner` 按 FP 窗口裁剪，不影响 reth 全局 pruning
- **Metrics 包装**：`StorageMetrics` 独立监控
- **Cursor 工厂**：`BaseProofsHashedAccountCursorFactory` / `BaseProofsTrieCursorFactory` 提供高效遍历

### 6. 完整的交易池栈

**核心洞察**：4 个 crate（txpool + txpool-rpc + txpool-tracing + tx-forwarding）+ bundle 扩展，形成了从交易验证到排序到 RPC 到可观测性到 MEV 支持的完整链路。

特别值得注意的是 `estimated_da_size` 和 `BundleTransaction` 的集成——这将 DA 成本意识和 MEV 支持直接嵌入交易池层。

### 7. 自定义 P2P 层

**核心洞察**：`crates/consensus/gossip/` 和 `crates/consensus/peers/` 实现了完整的 libp2p gossipsub P2P 层，包括连接门控、peer 评分、节点发现。

这说明 Base 对区块传播的低延迟要求超越了标准 OP Stack P2P 能提供的范围。

---

## Mantle 可借鉴之处

### 1. 采用 Pin & Extend 模型

**现状**：Mantle 维护 5 个 fork 仓库（revm + alloy-evm + op-alloy + reth + op-geth），上游跟进成本高。

**建议**：
- 将 Mantle 的定制逻辑从 fork 中提取到独立 crate
- 通过 reth 的 trait 接口注入，而非直接修改上游代码
- `MantleHardforks` trait 已经是这个方向的雏形——但目前它仍需要配合 revm fork 使用

**具体步骤**：
1. 将 `OpSpecId::ARSIA` 从 revm fork 迁移到一个 `MantleEvmFactory`（类似 Base 的 `BaseEvmFactory`），通过 `EvmFactory` trait 注入
2. 将 op-geth 的核心业务逻辑（MNT 双资产、operator fee）迁移到 Rust crate，通过 `ConfigureEvm` 注入
3. 最终目标：`Cargo.toml` 中只有 `reth = { tag = "vX.Y.Z" }`，无 fork

**难点**：MNT 双资产模型（state-level BVM_ETH 操作、tokenRatio 乘法）需要在 revm handler 层面定制，当前 revm 的 trait 接口可能不足以支持——这需要评估或向上游贡献接口。

### 2. 向单客户端收敛

**现状**：Mantle 维护 reth 和 op-geth 两套执行客户端。从代码覆盖度看，核心业务逻辑（MNT 双资产的 state-level 操作、preconf、operator fee 完整实现）主要在 op-geth 中。两者的生产分工、是否同时运行、哪一个承担 sequencer execution，需要部署配置确认。

**建议**：
- 将 op-geth 的核心功能逐步迁移到 reth fork（或更好地，迁移到独立的 Mantle execution crate）
- 功能迁移优先级：
  1. **operator fee**（已通过 revm fork 间接支持，需完善）
  2. **tokenRatio L1 cost**（`RethL1BlockInfo` 已有基础）
  3. **receipt 扩展**（token_ratio 缓存已实现）
  4. **BVM_ETH 双资产**（需要 EVM handler 层定制，最复杂）
  5. **preconf**（应提取为独立服务，不嵌入执行客户端）

**收益**：若当前确实同时运行两套客户端，收敛到单客户端可消除双客户端的内存/CPU/存储/运维开销。

### 3. 清理 Preconf 架构

**现状**：Preconf 子系统直接嵌入 op-geth（`preconf/` 包），重新实现了 op-node 的 sync status、deposit source hash 等概念。

**建议**：
- 将 preconf 提取为独立服务（类似 Base 的 builder 二进制独立于 node 二进制）
- 通过 RPC 或 IPC 与执行客户端交互，而非嵌入
- 这降低了执行客户端的复杂度，也使 preconf 可以独立迭代

### 4. 深化 Flashblocks Consumer 集成

**现状**：Mantle 使用外部 `op-rbuilder` + `rollup-boost` 作为 Flashblocks producer，`op-conductor` 做 leader-gated relay，`mantle/reth` 作为 consumer。producer 端采用 OP Stack 标准三进程架构，但 consumer 端集成深度不如 Base。

**建议**：
- 参考 Base 的 `CachedExecutor` 设计，在 engine-tree 层利用 flashblock 已执行结果跳过重复执行
- 集成 Base 的 per-flashblock metering 模型以实现资源预算和优先费预估
- 丰富 RPC 订阅能力（`newFlashblocks`、`pendingLogs` 等自定义订阅）

### 5. 引入资源计量

**现状**：Mantle 无多维度资源计量系统。

**建议**：
- 参考 Base 的 `crates/execution/metering/` 实现多维度计量（gas/DA/state-root/opcode）
- 特别是 MNT 双资产场景下，多维度计量有助于更精准的 tokenRatio-aware 费用预估
- `PriorityFeeEstimator` 的滚动估算可以适配 Mantle 的 operator fee 模型

### 6. 构建专用状态证明存储

**现状**：Mantle 依赖标准 reth/geth proof API，无 FP 窗口优化。

**建议**：
- 参考 Base 的 `crates/execution/trie/` 构建 FP 窗口专用存储
- 双后端（MDBX + 内存）设计适用于 ZK proof 场景（Mantle 使用 op-succinct）
- 独立裁剪策略避免影响全局状态

### 7. 动态预编译机制

**现状**：Mantle 每次预编译变更需要修改 revm fork 或 op-geth 源码。

**建议**：
- 参考 Base 的 `PrecompilesMap` + `install()` 机制
- 通过 `EvmFactory` trait 注入预编译集，而非硬编码在 fork 中
- 长期目标：无需硬分叉即可上线新预编译

---

## 总结

Base 的执行客户端设计围绕**零 fork、trait 组合、独立 crate** 三个原则展开，这在实践中带来了显著的维护和升级优势。其 Flashblocks + Metering + 专用 Trie 存储的集成深度也代表了 L2 执行层的前沿水平。

Mantle 面临的核心挑战是**多 fork 的维护成本**，以及**业务逻辑（MNT 双资产、preconf、operator fee）与执行客户端核心路径的深度耦合**。Mantle 维护两套执行客户端（reth + op-geth），其生产分工需要部署配置确认，但代码层面 op-geth 承载了更多核心业务逻辑。借鉴 Base 的 Pin & Extend 模型和模块化架构，是降低技术债务的最直接路径——但 MNT 双资产模型的特殊性（state-level ERC-20 操作、tokenRatio 全链路渗透）使得完全复制 Base 路径需要额外的接口设计工作。


---

# 状态管理、交易池与 RPC 对比

## 1. 状态管理

### 1.1 存储引擎

Base 和 Mantle reth 都使用 **MDBX** 作为底层存储引擎（reth 默认），Mantle op-geth 使用 **Pebble / LevelDB**（默认新库为 Pebble）。Base 额外构建了一个专用的 trie 存储子系统。

#### Base：FP 窗口 trie 存储（`crates/execution/trie/`）

Base 构建了一个独立的 trie 节点存储后端，专门用于在 Fault Proof 窗口内高效提供状态证明：

**双后端架构**：
- **MDBX 后端**：`MdbxProofsStorage`、`MdbxBatchSession`、`MdbxAccountCursor`、`MdbxStorageCursor`、`MdbxTrieCursor`
- **内存后端**：`InMemoryProofsStorage`、`InMemoryBatchSession`、`InMemoryAccountCursor`、`InMemoryStorageCursor`、`InMemoryTrieCursor`

**API 层**：
- `BaseProofsBatchSession` / `BaseProofsBatchStore` / `BaseProofsInitialStateStore` / `BaseProofsStore`
- `BlockStateDiff`：区块状态差异
- `InitializationJob`：初始化任务

**Cursor 工厂**：
- `BaseProofsBatchStateProviderRef`
- `BaseProofsBatchHashedAccountCursorFactory` / `BaseProofsBatchTrieCursorFactory`
- `BaseProofsHashedAccountCursorFactory` / `BaseProofsTrieCursorFactory`

**裁剪器**：
- `BaseProofStoragePruner` / `BaseProofStoragePrunerTask`：在 FP 窗口外裁剪旧的 trie 数据

**Metrics 包装**（`metrics` feature）：
- `BaseProofsStorage`（metrics-wrapped）、`StorageMetrics`

**设计目的**：将 FP 窗口内的 trie 数据与 reth 的通用 trie 存储分离，实现：
1. 高效的状态证明查询（无需扫描整个 trie）
2. 独立的裁剪策略（按 FP 窗口而非 reth 的全局 pruning）
3. 选择性使用 MDBX 或内存后端（按场景优化）

#### Base：Proofs Extension（`crates/execution/proofs/`）

- `ProofsHistoryConfig` / `ProofsHistoryExtension`：节点级别的 trie 存储 wiring

#### Mantle：无定制

Mantle reth 使用上游默认的 MDBX 存储，op-geth 使用 go-ethereum 的 Pebble / LevelDB（默认新库为 Pebble，`node/database.go:99-101`）。两者均无专用 trie 存储或 FP 窗口优化。

### 1.2 State Pruning

#### Base

通过 `BaseProofStoragePruner` 实现 FP 窗口外的 trie 裁剪，与 reth 的全局 pruning 独立运行。

#### Mantle

- **reth**：使用上游 reth 的标准 pruning
- **op-geth**：`prune_delete_limit = 10000`（`mantle_mainnet.rs`），标准 geth pruning

### 1.3 状态证明 / MPT 支持

#### Base

完整的状态证明栈：
- `crates/execution/trie/`：专用存储后端
- `crates/execution/proofs/`：证明扩展
- Builder 开启 `reth-revm = { features = ["witness"] }`——witness 收集功能

#### Mantle

无额外的状态证明基础设施。依赖上游 reth / geth 的标准 MPT proof API。

## 2. 交易池

### 2.1 Base：完整的 Txpool 栈

Base 构建了 4 个相关 crate 组成的完整交易池栈：

#### 核心 Txpool（`crates/execution/txpool/`）

- **`BaseTransactionValidator`**：交易验证器
- **`BasePooledTransaction`**：池交易类型
- **`BundleTransaction`**：Bundle 交易（私有 mempool）
- **`TimestampedTransaction`**：带时间戳交易
- **`BaseOrdering` / `TimestampOrdering`**：排序策略
- **`Consumer` / `Forwarder`**：交易消费和转发
- **`BuilderApiImpl` / `SendBundleApiImpl`**：Builder API
- **`estimated_da_size`**：DA 大小估算

类型别名：
```rust
type BaseTransactionPool<Client, S, Evm, T = BasePooledTransaction, O = BaseOrdering<T>>;
```

#### Txpool RPC（`crates/execution/txpool-rpc/`）

独立的 RPC 表面 crate，暴露 txpool 查询/提交接口。

#### Txpool Tracing（`crates/execution/txpool-tracing/`）

交易池 tracing instrumentation——可观测性。

#### 交易转发（`crates/execution/tx-forwarding/`）

交易转发到上游 sequencer 端点。

#### Bundle 扩展（`crates/execution/bundle/`）

Bundle（私有 mempool）ExEx 风格扩展：
- 支持 `eth_sendBundle` API
- 与 metering 集成（`meter_bundle`）

### 2.2 Mantle reth：MetaTx 拒绝 + 标准 OP Txpool

Mantle 对 OP Stack 的 txpool 做了一处关键修改：

**MetaTx 拒绝**（`crates/optimism/txpool/src/validator.rs:220`）：

```rust
if is_mantle_meta_tx(transaction.input()) {
    return TransactionValidationOutcome::Invalid(
        transaction, ...MetaTxDisabled
    );
}
```

- 匹配 32 字节 `MANTLE_META_TX_PREFIX`（14 zero bytes + ASCII `"MantleMetaTxPrefix"`）
- `MetaTxDisabled` 标记为 `is_bad_transaction() = true`
- 链无关（不检查 chain ID）
- 所有 `OpTransactionValidator` impl 加上 `ChainSpec: OpHardforks + MantleHardforks` bound

**测试覆盖**：
- `validate_rejects_mantle_meta_tx_as_bad_transaction`
- 部分前缀交易不触发拒绝
- 完整 pool 集成测试

其余 txpool 逻辑沿用上游 OP Stack 实现。

### 2.3 Mantle op-geth：Preconf Txpool

op-geth 的交易池有两处 Mantle 定制：

**1. MetaTx 验证**（`core/types/meta_transaction.go`）：
- `MetaTxCheck()` 在交易进入 txpool 前验证
- Everest 后返回 `ErrMetaTxDisabled`

**2. Preconf 交易管理**（`preconf/`）：
- `TxPoolConfig{FromPreconfs, ToPreconfs, AllPreconfs, PreconfTimeout=1s}`
- `FIFOTxSet`：确定性排序，含超时清理
- `Forward(addr, nonce)` 清理过期交易
- `preconf_tx_tracker.go`：preconf 交易跟踪

### 2.4 对比

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| 验证器 | `BaseTransactionValidator` | `OpTransactionValidator` + MetaTx 拒绝 | 标准 + MetaTx 验证 |
| 排序 | `BaseOrdering` / `TimestampOrdering` | 标准 OP | 标准 |
| Bundle 支持 | 完整（`eth_sendBundle`） | 无 | 无 |
| 交易转发 | 独立 crate（`tx-forwarding`） | 标准 OP sequencer forwarding | 标准 |
| DA 估算 | `estimated_da_size` | 无 | 无 |
| Tracing | 独立 crate | 无 | 无 |
| Preconf | 无 | 无 | 完整子系统 |
| RPC 表面 | 独立 crate（`txpool-rpc`） | 标准 OP | 标准 + preconf API |

## 3. RPC 层

### 3.1 Base：Ingress RPC + Execution RPC

Base 的 RPC 架构分为两层：

#### 执行 RPC（`crates/execution/rpc/`）

聚合 RPC 层——eth、debug、engine API，连接 trie、txpool、payload：
- 标准 `eth_*` API
- 扩展 debug API
- Engine API（FCU、newPayload）
- 集成 trie 存储的 proof API
- 集成 txpool 的交易提交 / 查询
- 集成 payload builder 的 block building API

#### Flashblocks RPC（`crates/execution/flashblocks/src/rpc/`）

覆盖标准 RPC 以提供 pending 状态感知：

| 组件 | 说明 |
|------|------|
| `EthApiExt` | 扩展 `eth_*` with pending tag 支持 |
| `EthApiOverrideServer` | 覆盖标准 eth 方法 |
| `EthPubSub` / `EthPubSubApiServer` | Flashblock 订阅 |
| `BaseSubscriptionKind` / `ExtendedSubscriptionKind` | 自定义订阅类型 |
| `TransactionWithLogs` | 交易 + 日志组合返回 |
| `BlockNumberOrTagExt` | 扩展 block tag 解析 |

#### Builder API（`crates/execution/txpool/`）

- `BuilderApiImpl`：Builder API 实现
- `SendBundleApiImpl`：`eth_sendBundle` 实现

#### Metering RPC（`crates/execution/metering/`）

- `MeteringApiImpl` / `MeteringApiServer`：
  - `base_setMeteringInformation`：设置计量数据
  - `MeterBlockResponse` / `MeteredPriorityFeeResponse` / `ResourceFeeEstimateResponse`：查询计量结果

### 3.2 Mantle reth：MantleEthApiExt

Mantle 在标准 OP RPC 上新增了一个扩展模块（`crates/optimism/rpc/src/eth/mantle_ext.rs`）：

| 方法 | 说明 |
|------|------|
| `mantle_getBlockRange(start, end, fullTx)` | 批量获取区块（最多 1000 个） |
| `mantle_sendRawTransactionWithPreconf(bytes)` | 通过 `SequencerClient` 转发 preconf 交易 |
| `mantle_estimateTotalFee(request, blockId)` | L2 gas fee + L1 data fee（FastLZ + 80-byte overhead）+ operator fee |

`mantle_estimateTotalFee` 从 `GAS_ORACLE_CONTRACT` 的 `TOKEN_RATIO_SLOT` 读取 MNT/ETH 汇率。Arsia 前调用会报错。

**始终安装**（`node.rs:612-631`）——所有节点均注册 `MantleEthApiExt`。

#### Gas Estimation 对齐（`crates/optimism/rpc/src/eth/call.rs`）

完全替换上游的 `eth_estimateGas` 二分搜索：
- 返回**原始估算值**（无 120% buffer）——对齐 op-geth 的 `IsMantleArsia` 路径
- geth 乐观公式：`(MaxUsedGas + CallStipend) * 64 / 63`
- 二分搜索中点偏低：`mid = lo * 2 if mid > lo * 2`

#### Receipt Token Ratio 缓存（`crates/optimism/rpc/src/eth/receipt.rs`）

- `MAX_REASONABLE_TOKEN_RATIO = 1_000_000_000`
- `TOKEN_RATIO_PREFIX_CACHE_MAX_BLOCKS = 1024`
- `token_ratio_after_logs()`：扫描 `TokenRatioUpdated` 事件
- LRU 缓存：per block hash 缓存 token ratio 前缀数组

### 3.3 Mantle op-geth：标准 + Preconf API

op-geth 的 RPC 扩展：
- 标准 `eth_*` + OP Stack 扩展
- Preconf API（`eth/catalyst/api_optimism.go`）
- Mantle-aware `eth_getTransactionReceipt`（包含 tokenRatio）
- Gas estimation 调整（`eth/gasestimator/gasestimator.go`）

### 3.4 对比

| 维度 | Base | Mantle reth | Mantle op-geth |
|------|------|-------------|----------------|
| 核心 RPC | execution rpc crate | 标准 OP | 标准 + Mantle 字段 |
| 自定义方法 | flashblocks 订阅、metering API、builder API | `mantle_getBlockRange`、`mantle_sendRawTransactionWithPreconf`、`mantle_estimateTotalFee` | preconf API |
| Pending 状态 | Flashblock-aware（完整 pending tag 支持） | Flashblock consumer（opt-in） | 标准 |
| Gas Estimation | 标准 OP + metering-based 优先费预估 | op-geth 对齐（无 120% buffer） | Mantle 调整 |
| Receipt 扩展 | 标准 | token_ratio LRU 缓存 | tokenRatio + operatorFee 字段 |
| Proof API | trie 存储集成 | 标准 | 标准 |

## 4. 网络层对比

### 4.1 Base：自定义 P2P（`crates/consensus/`）

Base 在 `crates/consensus/` 下构建了完整的 P2P 层：

#### Gossip 驱动（`gossip/`）

完整的 libp2p gossipsub 实现用于 L2 区块传播：

- **`GossipDriver`** / **`GossipDriverConfig`** / **`GossipDriverBuilder`**：驱动核心
- **`Behaviour`** / **`BehaviourError`**：libp2p 行为定义
- **`BlockHandler`** / **`Handler`**：区块消息处理
- **`ConnectionGate`** / **`ConnectionGater`** / **`GaterConfig`**：连接门控
- **事件**：`Event`，**验证**：`BlockInvalidError`

关键常量：
- `DEFAULT_MESH_D` / `DEFAULT_MESH_DHI` / `DEFAULT_MESH_DLAZY` / `DEFAULT_MESH_DLO`：gossipsub mesh 参数
- `MAX_GOSSIP_SIZE` / `MIN_GOSSIP_SIZE`：消息大小限制
- `GOSSIP_HEARTBEAT`：心跳间隔
- `SEEN_MESSAGES_TTL`：已见消息 TTL
- `GLOBAL_VALIDATE_THROTTLE` / `MAX_VALIDATE_QUEUE`：验证限流

P2P RPC 类型：`Connectedness`、`Direction`、`GossipScores`、`P2pRpcRequest`、`PeerCount`、`PeerDump`、`PeerInfo`、`PeerScores`、`PeerStats`、`ReqRespScores`、`TopicScores`。

#### 节点发现（`peers/`）

- **`PeerId`** / **`BootNodes`** / **`BootStore`** / **`BootStoreFile`**：节点标识和引导
- **`BaseEnr`** / **`BaseEnrError`** / **`EnrValidation`**：ENR 处理
- **`AnyNode`** / **`BootNode`** / **`NodeRecord`**：节点类型
- **`PeerMonitoring`** / **`PeerScoreLevel`**：节点监控和评分
- **`SecretKeyLoader`**：密钥管理

### 4.2 Mantle：无自定义 P2P

**Mantle reth**：搜索 `crates/net/` 中 `mantle|Mantle|MetaTx` 返回**零结果**。网络层完全沿用上游 reth/OP Stack 实现。

**Mantle op-geth**：使用标准 op-geth P2P（devp2p + discv5）。

### 4.3 对比

| 维度 | Base | Mantle |
|------|------|--------|
| P2P 实现 | 自定义 libp2p gossipsub（`crates/consensus/gossip`） | 上游 reth/op-geth 标准 |
| 节点发现 | 自定义 ENR + BootStore（`crates/consensus/peers`） | 标准 discv5 |
| 区块传播 | 自定义 BlockHandler + GossipDriver | 标准 OP gossip |
| 连接管理 | ConnectionGater + ConnectionGate | 标准 |
| Peer 评分 | PeerScoreLevel + PeerMonitoring | 标准 |

## 5. 性能与资源

### 5.1 EVM 引擎

两者都基于 **revm**，执行性能差异主要来自上层架构：

- Base 使用 upstream revm，通过 `PrecompilesMap` 哈希表 dispatch
- Mantle reth 使用 `mantle-xyz/revm` fork，通过 `OpSpecId::ARSIA` 扩展 spec
- Mantle op-geth 使用 Go 的 EVM 实现（性能低于 Rust revm）

### 5.2 状态读写路径

| 维度 | Base | Mantle |
|------|------|--------|
| 存储引擎 | MDBX + 专用 FP trie 存储 | reth: MDBX（标准）; op-geth: Pebble/LevelDB（默认 Pebble） |
| 写路径优化 | `spawn_deferred_trie_task`（后台 trie 计算） | 标准 |
| 读路径优化 | `FlashblockCache` + `CachedExecutor` | 标准 |
| Proof 查询 | 专用 cursor factory + metrics wrapper | 标准 geth/reth proof API |

### 5.3 Mantle 双客户端潜在资源开销

Mantle 维护 reth (Rust) 和 op-geth (Go) 两套执行客户端。两者在代码层面并行存在，可能用于迁移或并行替代。生产环境的具体分工（哪一个承担 sequencer execution、哪一个提供公开 RPC、是否同时运行）需要部署配置确认。

若两者同时运行，潜在的资源开销包括：

- **内存**：两份完整状态数据库
- **CPU**：两套 EVM 执行
- **存储**：两份 chain data
- **运维**：双客户端版本管理、配置同步、健康监控

从代码功能覆盖来看，reth fork 目前尚未完全覆盖 op-geth 的核心业务逻辑（MNT 双资产的 state-level 操作、preconf 子系统等），这意味着完全替代 op-geth 仍需要进一步的功能迁移。


---

# 上游关系模型对比：Base 直用 reth vs Mantle Fork

## 1. 架构概览

### Base：Git Pin + Trait 扩展

Base 采用**零修改上游**策略，直接依赖 Paradigm 官方的 reth：

```toml
# base/Cargo.toml
[workspace.dependencies]
reth = { git = "https://github.com/paradigmxyz/reth", tag = "v2.2.0" }
```

所有 rollup 定制逻辑封装在 `base/crates/execution/` 下的 20 个独立 crate 中，通过 reth 暴露的 trait 接口（`ConfigureEvm`、`EngineValidatorBuilder`、`EvmFactory`、`PayloadValidatorBuilder` 等）进行扩展。**不 fork、不修改上游任何一行代码。**

唯一的例外是 `crates/execution/engine-tree/src/validator.rs`，其源头注释明确写道：

> *"Cloned from `reth_engine_tree::tree::BasicEngineValidator`. To update, copy that file and review the diff."*

即便是这个唯一的"拷贝"，也附带了清晰的更新指引，而非变成一个分叉维护负担。

### Mantle：多层 Fork 链

Mantle 维护两个执行客户端，外加三个核心依赖库的 fork：

| 组件 | 上游 | Mantle Fork |
|------|------|-------------|
| 执行客户端 (Rust) | `paradigmxyz/reth` v1.9.3 | `mantle-xyz/reth`（branch `mantle-arsia`） |
| 执行客户端 (Go) | `ethereum-optimism/op-geth` | `mantle-xyz/op-geth` |
| EVM 引擎 | `bluealloy/revm` | `mantle-xyz/revm` v2.2.2（添加 `OpSpecId::ARSIA`） |
| EVM 集成 | `alloy-rs/evm` | `mantle-xyz/evm` v2.2.1 |
| OP Alloy 类型 | `alloy-rs/op-alloy` | `mantle-xyz/op-alloy` v2.2.0 |

Mantle 的 fork 链深度为 **3 层**：revm → alloy-evm → reth，每一层都有 Mantle 的修改。

## 2. 上游版本跟进成本

### Base：Bump Tag

Base 的升级路径：

1. 修改 `Cargo.toml` 中的 tag：`v2.2.0` → `v2.3.0`
2. 编译，检查 trait 接口变化
3. 如有 breaking change，更新 `crates/execution/` 中的 trait 实现
4. 更新 `validator.rs` 的拷贝（按注释说明 diff 即可）

**预计成本**：一次 PR，通常不涉及合并冲突。

### Mantle：五仓库级联 Rebase

Mantle 的升级路径：

1. **revm fork**：rebase `mantle-xyz/revm` 到新版 upstream revm → 解决 `OpSpecId::ARSIA` 相关冲突 → 发新 tag
2. **alloy-evm fork**：rebase `mantle-xyz/evm` → 更新对 revm fork 的依赖 → 发新 tag
3. **op-alloy fork**：rebase `mantle-xyz/op-alloy` → 发新 tag
4. **reth fork**：rebase `mantle-xyz/reth` → 更新对上述三个 fork 的依赖 → 解决 Mantle 特有改动冲突
5. **op-geth fork**：独立 rebase → 解决 MNT 双资产模型、MetaTx、Preconf、Operator Fee 等大量改动冲突

**预计成本**：多个 PR，需按 revm → alloy-evm → op-alloy → reth 严格排序。op-geth 因改动面大（state transition、gas 模型、receipt 格式均有深度修改），rebase 冲突概率高。

### 量化对比

| 维度 | Base | Mantle |
|------|------|--------|
| 需要 rebase 的仓库数 | 0 | 5（revm + alloy-evm + op-alloy + reth + op-geth） |
| 本地快照版本 | reth v2.2.0 | reth v1.9.3 |
| 合并冲突风险 | 低（仅 trait 接口变化） | 高（直接修改上游代码） |
| 升级路径复杂度 | 单仓库 tag bump + trait 适配 | 多仓库需按依赖顺序 rebase / 发布 / 测试 |
| CI/CD 复杂度 | 单仓库 | 五仓库需串行发布 |

## 3. 代码边界清晰度

### Base：清晰的 Crate 边界

Base 的所有定制化代码都在 `crates/execution/` 和 `crates/common/` 下，与上游 reth 代码有明确的物理隔离：

```
base/
├── Cargo.toml                    # git pin reth v2.2.0
├── crates/
│   ├── execution/                # 20 个 rollup 扩展 crate
│   │   ├── evm/                  # BaseEvmConfig: impl ConfigureEvm
│   │   ├── payload/              # BasePayloadBuilder
│   │   ├── txpool/               # BaseTransactionPool
│   │   ├── engine-tree/          # BaseEngineValidator（唯一的"拷贝"）
│   │   ├── chainspec/            # BaseChainSpec + hardfork ladder
│   │   ├── flashblocks/          # Flashblocks consumer 状态库
│   │   ├── flashblocks-node/     # Flashblocks 节点扩展
│   │   ├── metering/             # 资源计量系统
│   │   ├── proofs/               # 状态证明扩展
│   │   ├── trie/                 # FP 窗口 trie 存储
│   │   └── ...                   # rpc, cli, runner, exex, bundle 等
│   ├── common/
│   │   ├── evm/                  # BaseEvmFactory, BasePrecompiles
│   │   └── precompiles/          # 自定义预编译合约
│   ├── consensus/
│   │   ├── gossip/               # P2P gossipsub 驱动
│   │   └── peers/                # 节点发现 / 评分
│   └── builder/
│       └── core/                 # Flashblocks producer 引擎
└── bin/
    └── builder/                  # Block builder 二进制
```

**关键设计原则**：上游 reth 代码作为 `workspace.dependencies` 引入，Base 代码通过 trait 组合（composition）而非继承来扩展功能。要回答"Base 改了什么"，只需看 `crates/` 目录。

### Mantle reth：散布式修改

Mantle 的修改分散在 upstream reth 的目录结构中：

```
mantle/reth/
├── crates/
│   ├── mantle-hardforks/         # 新增：MantleHardfork 定义
│   ├── optimism/
│   │   ├── evm/src/mantle.rs     # 修改：MantleEvmEnvInput
│   │   ├── evm/src/l1.rs         # 修改：L1 fee 取 MantleHardforks
│   │   ├── evm/src/build.rs      # 修改：OpBlockAssembler 加 MantleHardforks bound
│   │   ├── chainspec/src/mantle*.rs  # 新增：Mantle 链配置
│   │   ├── consensus/src/proof.rs    # 修改：receipt root 计算
│   │   ├── txpool/src/validator.rs   # 修改：MetaTx 拒绝
│   │   ├── rpc/src/eth/mantle_ext.rs # 新增：Mantle RPC 扩展
│   │   ├── rpc/src/eth/call.rs       # 修改：gas estimation 对齐 op-geth
│   │   ├── rpc/src/eth/receipt.rs    # 修改：token_ratio receipt 缓存
│   │   ├── flashblocks/              # 新增：Flashblocks consumer
│   │   └── node/src/node.rs          # 修改：注入 MantleEthApiExt
│   ├── engine/tree/src/tree/
│   │   └── payload_validator.rs      # 修改：state-export debug hook
│   └── rpc/rpc-eth-api/src/ext.rs    # 修改：MantleEthApiExtServer trait
```

要回答"Mantle 改了什么"，需要在整个代码库中搜索 `mantle`/`MNT` 关键字，修改没有统一的物理边界。

### Mantle op-geth：深度侵入式修改

op-geth 的修改更深——直接嵌入 go-ethereum 核心路径：

- `core/state_transition.go`：MNT mint、BVM_ETH mint/transfer、MetaTx sponsor 分账、operator fee 路由
- `core/types/rollup_cost.go`：token_ratio L1 cost 计算
- `core/types/deposit_tx.go`：新增 `EthValue`、`EthTxValue` 字段
- `core/types/meta_transaction.go`：完整 MetaTx 框架
- `core/vm/contracts.go`：5 套分叉预编译表
- `core/state_processor.go`：receipt 填充 token_ratio
- `params/config.go`：9 个 Mantle 分叉时间戳字段
- `preconf/`：完整的 preconfirmation 子系统

## 4. Mantle 双客户端：代码层面的功能对比

Mantle 维护 reth 和 op-geth **两套执行客户端**。两者在代码层面并行存在，可能用于迁移或并行替代。生产环境的具体分工（哪一个承担 sequencer execution、哪一个提供公开 RPC、是否同时运行）需要部署配置确认。

从代码功能覆盖来看：

| 维度 | mantle/reth | mantle/op-geth |
|------|-------------|----------------|
| 语言 | Rust | Go |
| 上游 | reth v1.9.3 | op-geth |
| MNT 双资产模型 | 仅通过 `MantleHardforks` trait 间接支持 | 完整实现（state-level BVM_ETH 操作） |
| MetaTx | txpool 层拒绝 | 完整 V1/V2/V3 + Everest 禁用 |
| Preconf | 无 | 完整子系统（`preconf/` 包） |
| Operator Fee | 通过 revm fork 间接支持 | 完整实现（buyGas/refund/routing） |
| Flashblocks | Consumer（opt-in via `--flashblocks-url`） | 无支持 |

**观察**：从代码覆盖度看，op-geth 包含了 Mantle 最核心的业务逻辑（MNT 双资产的 state-level 操作、operator fee 完整实现、preconf 子系统），而 reth fork 通过 `MantleHardforks` trait 注入 OP Stack 的 Rust 路径，但尚未完全覆盖 op-geth 的所有特性。这暗示 reth 可能处于逐步接管 op-geth 功能的过程中，但具体迁移状态需要结合部署配置判断。

## 5. 核心结论

| 维度 | Base | Mantle |
|------|------|--------|
| 上游策略 | Pin & Extend（不 fork） | Fork & Modify（多层 fork 链） |
| 升级成本 | O(1) — bump tag | O(N) — N 个仓库级联 rebase |
| 代码边界 | 清晰（独立 crate 目录） | 模糊（散布在上游目录中） |
| 客户端数量 | 1（纯 Rust） | 2（Rust + Go） |
| 维护负担 | 低 | 高（双客户端 × 多 fork） |
| 技术债务 | 可控 | 持续累积 |

**Base 的核心优势**：通过 trait 组合而非 fork 继承来实现 rollup 定制化，这使得上游跟进成为一个低风险的常规操作，而非一个高成本的工程项目。这一设计选择的前提是 reth 本身提供了足够丰富的 trait 接口——而 reth 确实做到了（`ConfigureEvm`、`EvmFactory`、`EngineValidatorBuilder` 等），使 Base 成为上游 reth 设计理念的最佳验证。
