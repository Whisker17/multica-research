# 桥接合约对比

> **证据说明**：Base 的桥接合约（Portal、Messenger、Bridge）使用上游 OP Stack 原版，本地仓库中仅有地址引用（`AddressList` 结构体），无 Solidity 源码或 ABI 绑定。"使用上游原版"为推断结论。Mantle 侧基于 `mantle-v2/.../src/` 中的 Solidity 源码直接确认。

## 1. 资产模型根本差异

Base 和 Mantle 在资产模型上存在**根本性的架构差异**，这一差异渗透到每一个桥接相关合约：

| 维度 | Base | Mantle |
|------|------|--------|
| L2 原生 gas 代币 | ETH（与上游 OP Stack 一致） | **MNT**（ERC-20 在 L1，原生余额在 L2） |
| L2 上的 ETH | 原生余额 | **BVM_ETH**（ERC-20 预部署合约） |
| L2 上的 MNT | 无特殊处理 | `account.balance`（原生） |
| 影响范围 | 无——复用上游全部桥接合约 | 全面改造 Portal、Messenger、Bridge |

### Mantle 的 BVM_ETH 预部署

`BVM_ETH.sol`（预部署地址 `0xdEAddEaDdeadDEadDEADDEAddEADDEAddead1111`）：

- 继承 `OptimismMintableERC20`，名称 "Ether"，符号 "WETH"
- `mint()` 已**永久禁用**——ETH 铸造只能通过 deposit 交易的状态转换逻辑触发（EVM 层面），而非合约调用
- `burn()` 限制为 `onlyL2Passer`——仅 `L2ToL1MessagePasser` 预部署可以销毁（用于提款）

### Mantle 的 LegacyERC20MNT

`LegacyERC20MNT.sol`（预部署地址 `0xDeadDeAddeAddEAddeadDEaDDEAdDeaDDeAD0000`）：

- `balanceOf(_who)` 返回 `_who.balance`——账户原生余额的 ERC-20 视图
- 所有写操作（`transfer`、`approve` 等）已 revert
- 仅为向后兼容保留

---

## 2. StandardBridge

### Base

完全使用上游 OP Stack 的 `L1StandardBridge`。仅在地址列表中引用 `l1_standard_bridge_proxy`，无任何定制。

上游 L1StandardBridge 支持：
- `depositETH` / `depositETHTo` — ETH 桥接到 L2
- `bridgeERC20` / `bridgeERC20To` — ERC-20 桥接到 L2
- `finalizeBridgeETH` / `finalizeBridgeERC20` — 接收 L2→L1 提款

### Mantle

Mantle 的 `L1StandardBridge.sol`（Semver 1.1.0）在上游基础上新增了**完整的 MNT 桥接路径**：

#### MNT 桥接函数

```solidity
// 充值 MNT 到 L2（限 EOA）
function depositMNT(uint256 _amount, uint32 _minGasLimit, bytes calldata _extraData) external onlyEOA
function depositMNTTo(address _to, uint256 _amount, uint32 _minGasLimit, bytes calldata _extraData) external payable

// 桥接 MNT（限 EOA）
function bridgeMNT(uint256 _amount, uint32 _minGasLimit, bytes calldata _extraData) public payable onlyEOA
function bridgeMNTTo(address _to, uint256 _amount, uint32 _minGasLimit, bytes calldata _extraData) public payable

// 完成 MNT 提款
function finalizeBridgeMNT(address _from, address _to, uint256 _amount, bytes calldata _extraData)
    public payable override onlyOtherBridge
```

#### MNT 桥接内部流程 (`_initiateBridgeMNT`)

```
1. require(msg.value == 0)  ← MNT 充值不应携带 ETH
2. IERC20(L1_MNT).safeTransferFrom(_from, address(this), _amount)  ← 拉取 MNT
3. IERC20(L1_MNT).approve(address(MESSENGER), _amount)  ← 授权给 Messenger
4. MESSENGER.sendMessage(_amount, OTHER_BRIDGE, finalizeBridgeMNT(...), _minGasLimit)
   └─ sendMessage 第一个参数为 MNT 金额（Mantle 扩展的签名）
```

#### ERC-20 路径限制

`_initiateBridgeERC20` 中增加了两个限制：
- **拒绝 MNT**：`require(_localToken != L1_MNT_ADDRESS)` — MNT 必须走专用路径
- **拒绝 ETH**：`require(_remoteToken != Predeploys.BVM_ETH)` — ETH 必须走 ETH 专用路径

#### 存储布局变更

`StandardBridge` 基础合约中的 `__gap` 从上游 49 减为 47，两个额外的 slot 用于 MNT 支持（包含 `l1MantleAddress` 遗留 spacer）。

#### MNT 提款完成

`finalizeBridgeMNT` 调用 `IERC20(L1_MNT).safeTransferFrom(address(MESSENGER), _to, _amount)` ——从 Messenger 合约拉取 MNT 转给接收者（不是从 Bridge 自身余额）。

---

## 3. CrossDomainMessenger

### Base

使用上游 OP Stack 的 `L1CrossDomainMessenger`，无定制。

### Mantle

Mantle 的 `L1CrossDomainMessenger.sol`（Semver 1.5.0）做了深度修改以支持双资产消息传递：

#### 发送消息（双 value 版本）

```solidity
function sendMessage(
    uint256 _mntAmount,     // MNT 金额（Mantle 新增的第一个参数）
    address _target,
    bytes calldata _message,
    uint32 _minGasLimit
) external payable
```

内部流程：
```
1. safeTransferFrom(msg.sender, address(this), _mntAmount)  ← 拉取 MNT
2. approve(address(PORTAL), _mntAmount)                       ← 授权给 Portal
3. PORTAL.depositTransaction{value: msg.value}(
       msg.value,      // _ethTxValue
       _mntAmount,     // _mntValue
       _to,
       _mntAmount,     // _mntTxValue
       _gasLimit,
       false,          // _isCreation
       _data
   )
```

#### 中继消息

```solidity
function relayMessage(
    uint256 _nonce,
    address _sender,
    address _target,
    uint256 _mntValue,    // Mantle 新增
    uint256 _ethValue,    // Mantle 新增（上游仅有 _value）
    uint256 _minGasLimit,
    bytes calldata _message
) external payable
```

- 消息哈希使用 `hashCrossDomainMessageV1`，包含 `_mntValue` 和 `_ethValue` 双字段
- 中继前：`IERC20(L1_MNT).approve(_target, _mntValue)`
- 中继后：重置 approve 为 0
- 接收合约在 call 期间可通过 `transferFrom(messenger, ..., _mntValue)` 获取 MNT

**这是一个非常独特的设计**——MNT 不通过 call value 传递（因为 MNT 在 L1 上是 ERC-20），而是通过 approve + transferFrom 模式在同一个 call 内传递。

#### 安全限制

- `require(_target != Predeploys.BVM_ETH)` — 禁止直接调用 L2 的 BVM_ETH
- 禁止调用 `address(this)` 和 `address(PORTAL)`

---

## 4. Withdrawal 流程差异

### Base：DisputeGame 验证路径

```
L2 发起提款
    ↓
L2ToL1MessagePasser 记录消息
    ↓
等待 output root 被提议（TEE Proposer 提交 AggregateVerifier game）
    ↓
proveWithdrawalTransaction（引用 DisputeGame）
    ↓
等待 game 解决（TEE 证明通过 + 争议期结束，或 ZK 挑战）
    ↓
finalizeWithdrawalTransaction
```

**时间估算**（基于代码分析，非部署配置）：
- TEE 证明提交：每 `BLOCK_INTERVAL` 个区块（可配置）
- 争议期：由 `expectedResolution` 控制，经过证明验证后动态调整
- 保证金领取：需要额外 `DelayedWETH.delay()` 延迟

### Mantle：经典 Bedrock 两步提款

```
L2 发起提款
    ↓
L2ToL1MessagePasser 记录消息
    ↓
等待 PROPOSER 提交 L2 output root（许可制）
    ↓
proveWithdrawalTransaction（引用 L2OutputOracle 的 output）
    ↓
等待 FINALIZATION_PERIOD_SECONDS（固定等待期）
    ↓
finalizeWithdrawalTransaction
```

**关键差异**：

| 维度 | Base | Mantle |
|------|------|--------|
| 证明方式 | 链上验证（TEE+ZK） | 信任 PROPOSER（无链上验证） |
| 等待期机制 | 动态（基于证明状态） | 固定（`FINALIZATION_PERIOD_SECONDS`） |
| 挑战能力 | 任何人可 ZK 挑战 | 仅 CHALLENGER 地址可回滚 |
| Withdrawal 资产 | 单一 ETH | 双资产 ETH+MNT |
| 提款交易结构 | 标准（`_value`） | 扩展（`_mntValue` + `_ethValue`） |

### Mantle op-succinct 路径（代码存在，部署需确认）

若 Mantle 后续把 Portal/Oracle 路径切到 `OPSuccinctL2OutputOracle`，withdrawal 路径将变为：

```
L2 发起提款
    ↓
等待带 SP1 ZK 证明的 output root 提交（或 optimistic 模式下无证明提交）
    ↓
proveWithdrawalTransaction（引用 ZK 验证过的 output）
    ↓
finalizeWithdrawalTransaction（可能缩短等待期）
```

---

## 5. Custom Token Bridge 支持

### Base

依赖上游 OP Stack 的标准机制：
- `OptimismMintableERC20Factory` — L2 上部署对应的 mintable token
- `L1StandardBridge` 的 `bridgeERC20` — 通用 ERC-20 桥接
- `L1ERC721Bridge` — NFT 桥接

无额外定制。

### Mantle

除标准机制外，MNT 原生代币引入了特殊的桥接逻辑：

**三类资产的桥接分离**：

| 资产 | L1 形态 | L2 形态 | 桥接路径 |
|------|---------|---------|---------|
| ETH | 原生 (msg.value) | BVM_ETH (ERC-20) | `depositETH` / `bridgeETH` |
| MNT | ERC-20 (L1_MNT_ADDRESS) | 原生余额 | `depositMNT` / `bridgeMNT`（专用路径） |
| 其他 ERC-20 | ERC-20 | Mintable ERC-20 | `bridgeERC20`（不得为 MNT 或 BVM_ETH） |

这种三路分离是 Mantle 独有的复杂性——每个资产类型都有独立的事件、函数和验证逻辑。

---

## 6. 总结

Mantle 因 MNT 原生代币的选择，在桥接层付出了巨大的架构成本：

1. **代码膨胀**：Portal、Messenger、Bridge 每个合约都需要双 value 字段和 MNT 专用路径
2. **安全表面增加**：`approve` → `transferFrom` 模式引入了新的攻击向量（需要 `require(_tx.target != L1_MNT_ADDRESS)` 等保护）
3. **协议兼容性成本**：deposit 版本号不同（v1 vs v0）、opaqueData 格式不同、消息哈希不同，导致无法直接复用上游工具链
4. **上游同步困难**：每次 OP Stack 升级 Portal/Messenger/Bridge 时，Mantle 都需要手动合并 MNT 相关改动

Base 通过使用 ETH 作为原生 gas 代币，完全避免了这些问题，可以直接复用上游合约而无需任何桥接层定制。


---

# L1 合约架构对比表

## 证据等级说明

本文档使用以下标记区分证据强度：

| 标记 | 含义 |
|------|------|
| ✅ Solidity 源码确认 | 直接阅读了本地检出的 Solidity 合约源码 |
| 🔗 ABI 绑定推断 | 仅通过 Rust ABI 绑定（`alloy_sol_types::sol!`）推断合约接口，Solidity 源码不在检出范围 |
| 📋 地址引用推断 | 仅在地址列表或配置中看到引用，未查看合约实现 |
| ⚠️ 代码存在但部署未确认 | 本地代码仓库中存在合约源码，但无法仅从代码确认其是否已部署至主网 |
| ❌ 无法确认 | 代码中未找到相关证据 |

**重要说明**：本分析基于本地代码仓库，只能证明"代码存在"和"接口定义"。关于生产部署状态的判断，需要结合链上数据（合约地址、proxy 指向、实际调用记录）进一步确认。

---

## 部署状态确认表

以下表格标注各合约的证据来源和部署确认程度。仅从代码仓库可以确认"代码存在"，不能等同于"已部署至主网"。

| 合约 | 侧 | 证据来源 | 部署确认程度 |
|------|-----|---------|-------------|
| SystemConfig | Base | 📋 `AddressList.system_config_proxy` 地址引用 + Rust 解析逻辑 | **推断为上游原版**——无 Base 定制 Solidity 源码，Rust 侧仅有日志解析 |
| SystemConfig | Mantle | ✅ Solidity 源码 (`mantle-v2/.../L1/SystemConfig.sol`, v1.4.0) | ⚠️ 代码存在，部署需链上确认 |
| OptimismPortal | Base | 📋 `AddressList.optimism_portal_proxy` 地址引用 | **推断为上游原版**——无 ABI 绑定，无 Solidity 源码 |
| OptimismPortal | Mantle | ✅ Solidity 源码 (`mantle-v2/.../L1/OptimismPortal.sol`, v1.7.0) | ⚠️ 代码存在，部署需链上确认 |
| L2OutputOracle | Base | 📋 `AddressList.l2_output_oracle_proxy` 地址引用存在 | **推断已迁移至 DisputeGame**——proof 合约体系暗示不再使用 oracle |
| L2OutputOracle | Mantle | ✅ Solidity 源码 (`mantle-v2/.../L1/L2OutputOracle.sol`, v1.3.0) | ⚠️ 代码存在；本地 `OptimismPortal` 实现依赖 immutable `L2_ORACLE`，实际生产指向需链上确认 |
| DisputeGameFactory | Base | 🔗 ABI 绑定 (`crates/proof/contracts/src/dispute_game_factory.rs`) | ⚠️ 接口确认，Solidity 源码在外部仓库 (`github.com/base/contracts`) |
| AggregateVerifier | Base | 🔗 ABI 绑定 (`crates/proof/contracts/src/aggregate_verifier.rs`) | ⚠️ 接口确认，Solidity 源码在外部仓库 |
| TEEProverRegistry | Base | 🔗 ABI 绑定 (`crates/proof/contracts/src/tee_prover_registry.rs`) | ⚠️ 接口确认，Solidity 源码在外部仓库 |
| NitroEnclaveVerifier | Base | 🔗 ABI 绑定 (`crates/proof/contracts/src/nitro_enclave_verifier.rs`) | ⚠️ 接口确认，Solidity 源码在外部仓库 |
| OPSuccinctL2OutputOracle | Mantle | ✅ Solidity 源码 (`op-succinct/.../validity/OPSuccinctL2OutputOracle.sol`) | ⚠️ 代码存在，**生产部署未确认**（Portal 仍指向经典 L2OutputOracle） |
| OPSuccinctFaultDisputeGame | Mantle | ✅ Solidity 源码 (`op-succinct/.../fp/OPSuccinctFaultDisputeGame.sol`) | ⚠️ 代码存在，**生产部署未确认**（需 Portal2，目前仅有 Mock） |
| L1StandardBridge | Base | 📋 `AddressList.l1_standard_bridge_proxy` 地址引用 | **推断为上游原版** |
| L1StandardBridge | Mantle | ✅ Solidity 源码 (`mantle-v2/.../L1/L1StandardBridge.sol`, v1.1.0) | ⚠️ 代码存在，部署需链上确认 |
| L1CrossDomainMessenger | Base | 📋 `AddressList.l1_cross_domain_messenger_proxy` 地址引用 | **推断为上游原版** |
| L1CrossDomainMessenger | Mantle | ✅ Solidity 源码 (`mantle-v2/.../L1/L1CrossDomainMessenger.sol`, v1.5.0) | ⚠️ 代码存在，部署需链上确认 |

---

## 综合对比

| 维度 | Base | Mantle | 备注 |
|------|------|--------|------|
| **合约仓库** | 独立 Solidity 仓库 (`github.com/base/contracts`，不在本次检出范围) + Rust 单仓库 ABI 绑定 | `mantle-v2/packages/contracts-bedrock` (Bedrock fork) + `op-succinct/contracts` | Base Solidity 源码未直接验证 |
| **上游关系** | 桥接层推断复用上游 OP Stack（无定制 Solidity 可见）；proof 层自研（通过 ABI 绑定确认接口） | 桥接层深度定制（MNT 原生代币，Solidity 源码确认）；proof 层 fork op-succinct | Mantle 合并上游成本更高 |

---

## 核心系统合约

| 合约 | Base | Mantle | 确认状态 |
|------|------|--------|---------|
| **SystemConfig** | 推断为上游原版 | 深度定制 (v1.4.0)：新增 `BASE_FEE`、`EIP_1559_PARAMS`、`OPERATOR_FEE_PARAMS`、`MIN_BASE_FEE`、`DA_FOOTPRINT_GAS_SCALAR`、`setGasConfigArsia` | Base: 📋 地址引用 + Rust 解析；Mantle: ✅ Solidity 源码 |
| **OptimismPortal** | 推断为上游原版 | 深度定制 (v1.7.0)：7参数 `depositTransaction`（双资产 ETH+MNT）、`DEPOSIT_VERSION=1`、MNT 安全保护 | Base: 📋 地址引用；Mantle: ✅ Solidity 源码 |
| **L2OutputOracle** | 推断不使用（已迁移至 DisputeGame） | 经典 Bedrock (v1.3.0)：许可制 PROPOSER+CHALLENGER、无链上验证 | Base: 📋 地址引用存在但 proof 体系暗示已弃用；Mantle: ✅ Solidity 源码，生产指向需链上确认 |
| **AddressManager** | 上游标准（Superchain Registry 格式） | 上游标准 + 遗留 RESOLVED 代理支持 | Base: 📋 地址引用；Mantle: ✅ Solidity 源码 |
| **ProxyAdmin** | 推断为上游标准（仅 ERC-1967） | 三模式枚举：ERC-1967 / CHUGSPLASH / RESOLVED | Base: 📋 地址引用；Mantle: ✅ Solidity 源码 |

---

## 验证合约

| 合约 | Base | Mantle | 确认状态 |
|------|------|--------|---------|
| **DisputeGameFactory** | 扩展版：新增 `createWithInitData` 原子化创建+初始化 | 仅在 op-succinct 中存在（`MockOptimismPortal2` 测试环境） | Base: 🔗 ABI 绑定确认接口；Mantle: ⚠️ 代码存在，部署未确认 |
| **AggregateVerifier** | Base 自研核心——TEE+ZK 多证明聚合、中间输出根、细粒度挑战 | ❌ 不存在 | 🔗 ABI 绑定确认接口，Solidity 源码在外部仓库 |
| **TEEProverRegistry** | ZK 证明的 Nitro 认证注册、镜像哈希轮换 | ❌ 不存在 | 🔗 ABI 绑定确认接口 |
| **NitroEnclaveVerifier** | 链上证书撤销、安全响应机制 | ❌ 不存在 | 🔗 ABI 绑定确认接口 |
| **AnchorStateRegistry** | 无需许可推进锚定状态、game 黑名单/退役 | ❌ 不存在（mantle-v2 无 dispute game 体系） | 🔗 ABI 绑定确认接口 |
| **DelayedWETH** | 两阶段保证金领取 | ❌ 不存在 | 🔗 ABI 绑定确认接口 |
| **OPSuccinctL2OutputOracle** | ❌ 不存在 | SP1 ZK 有效性证明、多配置支持、optimistic 模式 | ✅ Solidity 源码确认；⚠️ **生产部署未确认** |
| **OPSuccinctDisputeGame** | ❌ 不存在 | CWIA 包装器，ZK 验证通过即时解决 | ✅ Solidity 源码确认；⚠️ **生产部署未确认** |
| **OPSuccinctFaultDisputeGame** | ❌ 不存在 | SP1 故障证明状态机、5 阶段 ProposalStatus | ✅ Solidity 源码确认；⚠️ **生产部署未确认** |

---

## 桥接合约

| 合约 | Base | Mantle | 确认状态 |
|------|------|--------|---------|
| **L1StandardBridge** | 推断为上游原版 | 定制 (v1.1.0)：新增完整 MNT 桥接路径 (`depositMNT`/`bridgeMNT`/`finalizeBridgeMNT`)；ERC-20 路径拒绝 MNT 和 BVM_ETH | Base: 📋 地址引用；Mantle: ✅ Solidity 源码 |
| **L1CrossDomainMessenger** | 推断为上游原版 | 定制 (v1.5.0)：`sendMessage` 新增 `_mntAmount` 参数；`relayMessage` 双 value；MNT 通过 approve+transferFrom 模式传递 | Base: 📋 地址引用；Mantle: ✅ Solidity 源码 |
| **StandardBridge (通用)** | 推断为上游原版 | 定制：新增 `MNTBridgeInitiated`/`MNTBridgeFinalized` 事件；`__gap` 从 49 减为 47 | Base: 推断；Mantle: ✅ Solidity 源码 |
| **L1ERC721Bridge** | 推断为上游原版 | 推断为上游原版 | 两侧均为 📋 地址引用 |
| **BVM_ETH (L2)** | ❌ 不存在（ETH 为原生） | ETH 的 ERC-20 预部署，mint 仅通过 deposit 交易触发 | Mantle: ✅ Solidity 源码 |
| **LegacyERC20MNT (L2)** | ❌ 不存在 | MNT 原生余额的 ERC-20 视图（只读，写操作 revert） | Mantle: ✅ Solidity 源码 |

---

## 升级机制

| 维度 | Base | Mantle | 确认状态 |
|------|------|--------|---------|
| **代理模式** | ERC-1967 + CWIA | ERC-1967 + CHUGSPLASH + RESOLVED | Base: 🔗 CWIA 在 ABI 绑定中确认；Mantle: ✅ Solidity 源码 |
| **升级入口** | ProxyAdmin（推断为上游标准） | ProxyAdmin（三模式枚举） | Base: 📋 地址引用推断；Mantle: ✅ Solidity 源码 |
| **升级脚本** | 不在检出范围 | `UpgradeL1Contracts.s.sol`（Limb→Arsia） | Mantle: ✅ 脚本确认 |
| **时间锁** | 不在检出范围 | 代码中未见显式 Timelock | ⚠️ 两侧均可能在链上部署层面配置，需链上确认 |
| **紧急响应** | 证书撤销 + TEE 注销 + Game 黑名单 | L2Output 回滚 (CHALLENGER) | Base: 🔗 ABI 绑定确认；Mantle: ✅ Solidity 源码 |

---

## 升级历史（Mantle）

| 升级阶段 | 涉及 L1 合约 | 代码中的证据 | 确认状态 |
|---------|-------------|-------------|---------|
| **BedRock** | 初始部署 | `LegacyERC20MNT` 注释："migrated to the state trie as part of the Bedrock upgrade" | ✅ 注释确认 |
| **Everest** | 未知 | 代码中未找到标记 | ❌ 无法确认 |
| **Euboea** | 未知 | 代码中未找到标记 | ❌ 无法确认 |
| **Skadi** | 未知 | 代码中未找到标记 | ❌ 无法确认 |
| **Limb** | SystemConfig v1.3.0 | 升级脚本标题引用 | ✅ 脚本确认 |
| **Arsia** | SystemConfig v1.4.0、L1Block、GasPriceOracle | `setGasConfigArsia`、`setL1BlockValuesArsia`、`isArsia` | ✅ 代码确认；部署进度需链上或发布资料确认 |

---

## 安全模型对比

| 维度 | Base | Mantle |
|------|------|--------|
| **L1→L2 信任假设** | L1 共识保证 deposit（推断与上游一致） | L1 共识保证 deposit + MNT ERC-20 转账安全（✅ 源码确认） |
| **L2→L1 信任假设** | 任何人可通过 ZK 证明挑战错误 output（🔗 ABI 绑定推断） | 信任 PROPOSER 提交正确 output（✅ 源码确认） |
| **证明安全级别** | 多证明冗余 TEE + ZK（🔗 ABI 绑定推断） | 无链上证明，许可制（✅ 源码确认） |
| **紧急响应速度** | 快——证书撤销、game 黑名单、无需升级（🔗 ABI 绑定推断） | 慢——需 CHALLENGER 回滚或合约升级（✅ 源码确认） |
| **Withdrawal 安全** | DisputeGame 解决 + DelayedWETH 延迟（🔗 ABI 绑定推断） | 固定等待期 + 信任 PROPOSER（✅ 源码确认） |


---

# 合约安全与审计对比

## 1. 审计历史

### Base

**本地仓库中无第三方审计报告。** Base 的 Rust 单仓库 (`base/base`) 不包含 `audits/` 目录或审计 PDF。Solidity 合约源码位于外部仓库 `github.com/base/contracts`（不在本次检出范围），外部审计报告可能存放在该仓库或 Coinbase 内部系统中。

**已知审计线索**：
- `SECURITY.md` 引用了 Coinbase 的 **Cantina** bug bounty 计划（$5M 赏金池，ID `55316f42-3c5e-4746-9bd0-0f18dcbc344b`），覆盖 Base 所有已部署智能合约
- Cantina 平台通常同时提供审计服务，Base 的合约可能已通过 Cantina 进行审计，但本地代码中未找到公开证据

**证据状态**：❌ 未找到公开审计报告（可能在外部仓库或 Coinbase 内部系统）

### Mantle

`mantle-v2/docs/security-reviews/` 目录包含 52 个审计/安全审查文件，其中 39 个在 `optimism/` 目录，12 个为 Mantle 专项审计文件，另有 1 个 README。这里仅按文件名和目录结构统计，未逐份阅读全文确认具体问题范围和修复状态。

#### 上游 OP Stack 审计（继承）

`docs/security-reviews/optimism/` 目录包含 39 个上游审计/安全审查文件（2020-10 至 2025-11），审计方包括：

| 审计方 | 说明 |
|--------|------|
| Trail of Bits | 多次审计 |
| OpenZeppelin / Zeppelin | 多次审计 |
| ConsenSys Diligence | 早期审计 |
| Sigma Prime | 多次审计 |
| Spearbit | 多次审计 |
| Runtime Verification | 形式化验证 |
| Sherlock | 竞赛审计 |
| Cantina | 审计 |
| Coinbase Protocol Security | 内部审计 |
| 其他 | Trust, 3Doc Security, MiloTruck, Radiant Labs, Offbeat Labs, Wonderland, Aleph_v |

#### Mantle 专项审计

| 升级阶段 | 日期 | 审计方 | 报告数量 | 覆盖范围 |
|---------|------|--------|---------|---------|
| **Tectonic** | 2024-03/04 | OpenZeppelin (×3), Secure3 (×2), Sigma Prime (×1) | 6 份 | Node/Batcher/Proposer/Tooling, Op-Geth, V2 Solidity, Rollup 安全评估 |
| **Everest** | 2025-02/03 | OpenZeppelin, Sigma Prime | 2 份 | Op-geth & Op-stack v1.1.1 差异, EigenDA 集成 |
| **Euboea** | 2025-03/04 | Zenith, OpenZeppelin | 2 份 | 合约审计, Pre-Confirmation 交易 |
| **Skadi** | 2025-12 | Sherlock | 1 份 | 协作审计 |
| **Arsia** | 2026-03 | CertiK | 1 份 | 最新升级审计 |

**证据状态**：✅ 52 个审计/安全审查文件存在于本地仓库；其中 Mantle 专项 12 个、上游 Optimism 39 个、README 1 个

### Mantle op-succinct

`op-succinct/audits/` 目录包含 2 份审计报告：
- `OP Succinct Spearbit.pdf` — Spearbit（通过 Cantina 平台）审计
- `OP Succinct Lite Spearbit.pdf` — Spearbit 审计（Lite 版本）
- FAQ 文档确认："Cantina has audited both OP Succinct and OP Succinct Lite"

**注意**：这些是上游 `succinctlabs/op-succinct` 的审计，非 Mantle fork 的专项审计。Mantle fork 中的定制修改可能未被覆盖。

**证据状态**：✅ 2 份审计报告 PDF（上游项目审计，非 Mantle fork 专项）

---

## 2. 已知安全事件

### Base

代码中包含 4 个具名 Immunefi 安全票据的引用，表明 Base 通过 bug bounty 计划发现并修复了多个问题：

| 票据编号 | 内部编号 | 问题描述 | 修复方式 |
|---------|---------|---------|---------|
| **Immunefi #75608** | CHAIN-4194 | 已撤销的 AWS Nitro 中间证书在 CRL 被清理后可能重新通过注册 | `NitroEnclaveVerifier.revokeCert()` 链上持久化撤销（`crates/proof/contracts/src/nitro_enclave_verifier.rs:31`） |
| **Immunefi #75829** | CHAIN-4297 | 失败的 ZK 证明重试未复用确定性 `session_id`，可能导致重复提交 | 回归测试 `test_step_proof_retry_reuses_deterministic_session_id`（`crates/proof/challenge/tests/driver.rs:594`） |
| **Immunefi #74652** | — | 治理调用 `setImplementation` 后 `INTERMEDIATE_BLOCK_INTERVAL` 过时，应触发 `CheckpointCountMismatch` 而非静默忽略 | 回归测试（`crates/proof/challenge/tests/driver.rs:1563`） |
| **Immunefi #75630** | CHAIN-4254 | SP1 集群上的重复 Groth16 SNARK 任务 | 数据库 migration `009_add_unique_active_session.sql` 增加部分唯一索引 |

此外，`deny.toml` 中明确列出已知 RUSTSEC 告警的处理：
- `RUSTSEC-2023-0089` — 已评估并白名单
- `RUSTSEC-2026-0066` — tar PAX 扩展漏洞，来自 reth-cli-commands 依赖，等待上游修复

**证据状态**：✅ 4 个 Immunefi 票据在代码中有明确引用和回归测试

### Mantle

`docs/postmortems/` 目录包含 1 份事后分析报告：

| 日期 | 事件 | 发现者 | 影响 |
|------|------|--------|------|
| **2022-02-02** | Self-Destruct Inflation Vulnerability | saurik (Jay Freeman) | 上游 Optimism 的 L2Geth 漏洞，最高赏金 $2,000,042 |

**注意**：此事件为上游 Optimism 的历史问题，非 Mantle 独有。Mantle 作为 OP Stack fork 继承了这段历史。

**证据状态**：✅ 1 份事后分析报告（上游继承）。Mantle 自身的安全事件记录——未找到公开证据

---

## 3. 测试覆盖率

### Base

- **未找到测试覆盖率配置**——无 `codecov.yml`、`tarpaulin.toml`、`llvm-cov` 配置
- Rust 单仓库有大量单元测试和集成测试（通过 `#[test]` 和 `tests/` 目录），但无覆盖率报告
- proof 模块有专门的回归测试（包含 Immunefi 票据的测试用例）

**证据状态**：⚠️ 测试存在，覆盖率度量未找到公开证据

### Mantle mantle-v2

测试基础设施较为完善：

**Codecov 配置**（`codecov.yml`）：
- 项目状态：informational（不阻断 CI）
- Patch 覆盖率目标：`auto`，阈值 5%，仅对 `contracts` 目录非 informational
- 排除：`op-e2e`、`*.t.sol`、`test/`、`scripts/`、`vendor/`、`interfaces/`
- Flag：`contracts-bedrock-tests`

**Foundry 测试配置**（`foundry.toml`）：

| Profile | Fuzz Runs | Invariant Runs | Invariant Depth | 用途 |
|---------|-----------|---------------|-----------------|------|
| `default` | 64 | — | — | 本地开发 |
| `ci` | 128 | 64 | 32 | CI 流水线 |
| `cicoverage` | 1 | 1 | 1 | 覆盖率收集（optimizer 关闭） |
| `ciheavy` | 20,000 | 128 | 512 | 深度模糊测试（timeout 300s） |
| `lite` | — | — | — | 轻量测试 |
| `kprove` | — | — | — | Kontrol 形式化证明 |

**测试目录**（`packages/contracts-bedrock/test/`）：
- 单元测试：`.t.sol` 文件覆盖主要合约
- 不变量测试：`invariants/` 子目录包含 CrossDomainMessenger、L2OutputOracle、OptimismPortal、SafeCall、SystemConfig 的不变量检查
- Mantle 特定测试：`LegacyERC20MNT.t.sol`
- Mock 合约：`mocks/` 子目录

**发布流程中的审计门控**：
- `book/src/policies/release-process.md` 明确要求：创建 `-rc.1` 版本后进行审计，审计结果如需修复则需要额外 RC 版本

**证据状态**：✅ 完善的测试基础设施——Codecov + 多级 Foundry profiles + 不变量测试 + 形式化证明配置

### Mantle op-succinct

- **未找到测试覆盖率配置**——无 `codecov.yml`、无 Rust 覆盖率工具配置
- `.dockerignore` 排除了 `/audits` 目录

**证据状态**：⚠️ 未找到测试覆盖率公开证据

---

## 4. Bug Bounty 计划

| 维度 | Base | Mantle |
|------|------|--------|
| **Bug Bounty 平台** | Coinbase HackerOne + Cantina | 未在代码中找到独立引用（SECURITY.md 指向上游 Optimism 的安全政策） |
| **最高赏金** | Cantina $5M（覆盖所有已部署智能合约） | 未找到公开证据（继承上游 Optimism 的赏金计划） |
| **联系方式** | `security@coinbase.com` | 指向上游 `https://github.com/ethereum-optimism/.github/blob/master/SECURITY.md` |
| **已知赏金支出** | 4 个具名 Immunefi 票据有代码引用 | 未找到公开证据 |

---

## 5. 对比总结

| 维度 | Base | Mantle |
|------|------|--------|
| **审计报告数量** | 未找到公开报告（可能在外部仓库） | 52 个本地安全审查文件（39 上游继承 + 12 Mantle 专项 + 1 README） |
| **审计方覆盖度** | 未知 | 极广（OpenZeppelin, Sigma Prime, Sherlock, CertiK, Spearbit 等） |
| **升级审计覆盖** | 未知 | Tectonic、Everest、Euboea、Skadi、Arsia 目录均有对应审计文件；覆盖范围需逐份报告确认 |
| **安全事件透明度** | 高——4 个 Immunefi 票据直接在代码中引用和回归测试 | 中——1 份上游继承的事后分析 |
| **Bug Bounty 规模** | Cantina $5M + HackerOne | 指向上游 Optimism |
| **测试基础设施** | 有测试但无覆盖率度量 | 完善——Codecov + 多级 Foundry + 不变量 + 形式化 |
| **op-succinct 审计** | 不适用 | 2 份 Spearbit 审计（上游项目，非 Mantle fork 专项） |

**关键观察**：

1. **Base 的安全透明度体现在代码中**——通过 Immunefi 票据引用和回归测试直接展示了"发现问题 → 修复 → 防回归"的完整闭环。这虽然不等同于审计报告，但显示了活跃的安全响应机制。
2. **Mantle 的本地审计资料更完整**——Tectonic、Everest、Euboea、Skadi、Arsia 目录均有审计文件，且保留了上游 Optimism 审计历史。发布流程中明确要求审计门控。
3. **两者都有盲区**：Base 缺少可见的第三方审计报告（可能在外部仓库）；Mantle 的 op-succinct fork 定制部分尚未经过 Mantle 专项审计（仅有上游 Spearbit 审计）。
4. **Mantle 的 `SECURITY.md` 仅指向上游 Optimism**——没有独立的 Mantle bug bounty 计划引用，这可能意味着 Mantle 依赖 Optimism 的安全框架，或者有独立的计划但未在代码仓库中体现。


---

# 核心系统合约对比

> **证据说明**：Base 的 Solidity 合约源码位于外部仓库 `github.com/base/contracts`（不在本次检出范围）。本文中 Base 侧的分析基于 Rust ABI 绑定（`alloy_sol_types::sol!` 宏定义）和地址配置推断合约接口，而非直接阅读 Solidity 源码。Mantle 侧的分析基于 `mantle-v2/packages/contracts-bedrock/src/` 中的 Solidity 源码直接确认。两侧证据强度不对等，Base 侧标注为"推断"的结论需通过查看 `github.com/base/contracts` 源码或链上数据进一步验证。

## 1. SystemConfig

SystemConfig 是 L2 链参数在 L1 上的配置入口，op-node / derivation pipeline 通过监听其 `ConfigUpdate` 事件来同步参数变更。

### Base

Base 使用**上游 OP Stack 原版 SystemConfig**，未做定制修改。其 Rust 单仓库中仅包含 SystemConfig 的数据类型解析（用于 derivation pipeline 读取 L1 日志），不包含 Solidity 合约源码。

解析的参数集合（`crates/common/genesis/src/system/config.rs`）：
- `batcher_address` — batcher 地址
- `overhead` / `scalar` — L1 数据费用参数
- `gas_limit` — L2 gas limit
- `base_fee_scalar` / `blob_base_fee_scalar` — Ecotone 后的 scalar 拆分
- `eip1559_denominator` / `eip1559_elasticity` — EIP-1559 参数
- `operator_fee_scalar` / `operator_fee_constant` — 运营商费用
- `min_base_fee` — 最低 base fee
- `da_footprint_gas_scalar` — DA 数据成本计量

### Mantle

Mantle 的 SystemConfig（`mantle-v2/.../L1/SystemConfig.sol`，Semver 1.4.0）在上游基础上进行了显著扩展：

| 参数类型 | 说明 |
|---------|------|
| `BASE_FEE` | 可直接设定 L2 base fee（`setBaseFee`），上游不支持 |
| `EIP_1559_PARAMS` | 可调 EIP-1559 denominator 和 elasticity |
| `OPERATOR_FEE_PARAMS` | 独立的运营商费用 scalar 和 constant |
| `MIN_BASE_FEE` | 显式最低 base fee |
| `DA_FOOTPRINT_GAS_SCALAR` | DA 成本计量 scalar |
| `setGasConfigArsia` | Arsia 升级新增，将 `basefeeScalar`/`blobbasefeeScalar` 打包为 Ecotone 风格 scalar（version byte `0x01`） |

**关键差异**：Mantle 的 SystemConfig 不包含 MNT 相关字段——MNT 原生代币的感知集中在 Portal / Messenger / Bridge 层。

### 小结

Base 完全复用上游 SystemConfig，保持与 Superchain 生态的兼容性。Mantle 则深度定制以支持其独特的费用模型（可固定 base fee、独立运营商费用），但这也意味着每次上游升级时需要同步合并。Arsia 升级中 Mantle 才开始引入 Ecotone 风格的 scalar 编码，落后上游数个版本。

---

## 2. OptimismPortal

Portal 是 L1 上的 deposit/withdrawal 入口，负责接收 L1→L2 的充值交易和最终确认 L2→L1 的提款。

### Base

Base 使用**上游 OP Stack 原版 OptimismPortal**。其 Rust 仓库中仅有地址引用（`optimism_portal_proxy: Option<Address>`），不包含合约源码或 ABI 绑定。

上游 `depositTransaction` 签名（4 参数）：
```solidity
function depositTransaction(
    address _to,
    uint256 _value,
    uint64 _gasLimit,
    bool _isCreation,
    bytes memory _data
) external payable
```

### Mantle

Mantle 的 OptimismPortal（`mantle-v2/.../L1/OptimismPortal.sol`，Semver 1.7.0）是整个合约体系中**改动最大**的合约。

#### depositTransaction（7 参数，对比上游 4 参数）

```solidity
function depositTransaction(
    uint256 _ethTxValue,    // L2 上 BVM_ETH 代币发送量
    uint256 _mntValue,      // 从 msg.sender 拉取的 MNT 数量
    address _to,
    uint256 _mntTxValue,    // L2 上发送给接收者的 MNT 数量
    uint64 _gasLimit,
    bool _isCreation,
    bytes memory _data
) public payable
```

- `msg.value` 是 L1 ETH 发送量，在 L2 上转为 BVM_ETH
- `_mntValue` 通过 `IERC20(L1_MNT_ADDRESS).safeTransferFrom` 从调用者拉取，锁定在 Portal
- `opaqueData` 编码为 `(_mntValue, _mntTxValue, msg.value, _ethTxValue, _gasLimit, _isCreation, _data)` — **四个 value 字段**（上游仅两个）
- `DEPOSIT_VERSION = 1`（上游为 0）

#### finalizeWithdrawalTransaction

- `WithdrawalTransaction` 结构体包含 `mntValue` 和 `ethValue` 双字段
- MNT 通过 `IERC20(L1_MNT_ADDRESS).transfer(_tx.target, _tx.mntValue)` 直接转账
- ETH 通过 `SafeCall.callWithMinGas(_tx.target, _tx.gasLimit, _tx.ethValue, _tx.data)` 的 call value 发送
- 安全保护：`require(_tx.target != L1_MNT_ADDRESS, "Directly calling MNT Token is forbidden")` — 防止通过构造 withdrawal hash 来排空 Portal 的 MNT 托管

#### Withdrawal 证明路径

Mantle 的 Portal 仍使用经典 Bedrock 的 `proveWithdrawalTransaction` → `finalizeWithdrawalTransaction` 两步式流程，依赖 `L2_ORACLE.getL2Output().outputRoot`。**未集成 DisputeGame**。

### 小结

| 维度 | Base | Mantle |
|------|------|--------|
| 合约版本 | 上游原版 | Semver 1.7.0，深度定制 |
| Deposit 参数 | 4 个（单资产） | 7 个（双资产 ETH+MNT） |
| Deposit 版本 | 0 | 1 |
| Withdrawal 验证 | DisputeGame 路径 | 经典 L2OutputOracle 路径 |
| 原生代币影响 | 无 | 全面渗透 |

---

## 3. 验证合约架构

这是 Base 和 Mantle 之间**最大的架构分歧**所在。

### Base：多证明聚合验证（AggregateVerifier）

Base 自研了一套完整的多证明验证系统，合约源码位于独立仓库 `github.com/base/contracts`，Rust 仓库中包含完整的 ABI 绑定（`crates/proof/contracts/src/`）。

#### 3.1 DisputeGameFactory（扩展版）

Base 在上游 DisputeGameFactory 基础上新增了 `createWithInitData`：

```solidity
function createWithInitData(
    uint32 gameType,
    bytes32 rootClaim,
    bytes calldata extraData,    // packed: l2BlockNumber(32) + parentAddress(20) + intermediateRoots(32*N)
    bytes calldata initData      // 初始证明数据（TEE 或 ZK）
) external payable returns (address proxy);
```

- **原子化创建+初始化**：上游需要 `create` + 后续 `initialize`，Base 在同一笔交易中完成
- **CWIA 编码**：`extraData` 使用 Clone-With-Immutable-Args 打包（非 ABI 编码），通过固定字节偏移读取
- 唯一性约束：`(gameType, rootClaim, extraData)` 元组唯一，重复创建返回 `GameAlreadyExists`

#### 3.2 AggregateVerifier（核心 Dispute Game）

每个 game 实例是一个 CWIA 代理克隆，同时追踪 TEE 和 ZK 两种证明：

**证明类型判别**：`proofBytes` 的第一个字节为判别器
- `0x00` = TEE 证明
- `0x01` = ZK 证明

**核心操作**：

| 函数 | 说明 |
|------|------|
| `nullify(proofBytes, intermediateRootIndex, intermediateRootToProve)` | 证伪某个中间输出根。TEE 或 ZK 证明均可 |
| `challenge(proofBytes, intermediateRootIndex, intermediateRootToProve)` | ZK 证明挑战 TEE 证明的 game。第一字节必须为 `0x01` |
| `resolve()` | 在争议期结束后解决 game |
| `claimCredit()` | 两阶段保证金领取：第一次调用触发 `DelayedWETH.unlock()`，第二次（延迟后）提取 ETH |

**架构设计理念**：**TEE 优先，ZK 作为仲裁者**

```
TEE Proposer ──→ createWithInitData(TEE proof) ──→ AggregateVerifier
                                                        │
                                              等待争议期...
                                                        │
ZK Challenger ──→ challenge(ZK proof) ──────────────────┘
                  （仅在不同意 TEE 结果时触发）
```

- TEE 提议者以低成本频繁提交证明（每 `BLOCK_INTERVAL` 个区块）
- ZK 挑战者仅在检测到不一致时生成证明——节省 ZK 计算成本
- ZK 作为最终仲裁者具有更高权威

**中间输出根**：每个 game 不仅包含最终输出根，还包含一组中间输出根（间隔 `INTERMEDIATE_BLOCK_INTERVAL`），允许**细粒度的非二分法挑战**——挑战者可以精确定位并证伪某个特定中间根，而非回滚整个 game。

**保证金机制**：
- `bondRecipient` 默认为创建者，若 game 以 `CHALLENGER_WINS` 解决则转给 ZK 挑战者
- 通过 `DelayedWETH` 实现两阶段领取，增加安全延迟

#### 3.3 TEEProverRegistry（TEE 证明者注册）

```solidity
function registerSigner(bytes output, bytes proofBytes) external
function deregisterSigner(address signer) external
function isValidSigner(address signer) external view returns (bool)
function isRegisteredSigner(address signer) external view returns (bool)
```

- 注册过程本身需要 **ZK 证明的 AWS Nitro 认证**——即通过 ZK 验证 Nitro Enclave 的硬件远程证明
- `isValidSigner` 检查注册状态 + 镜像哈希匹配（当前期望值）
- `isRegisteredSigner` 仅检查注册状态（支持镜像轮换后的历史有效性判断）

#### 3.4 NitroEnclaveVerifier

```solidity
function revokeCert(bytes32 certHash) external
function revokedCerts(bytes32) external view returns (bool)
```

链上持久化的证书撤销机制，用于处理被入侵的中间证书（源于 Immunefi #75608 安全响应）。

#### 3.5 AnchorStateRegistry

```solidity
function setAnchorState(address game) external  // 无需许可，合约自验证资格
function getAnchorRoot() external view returns (bytes32 root, uint256 l2SequenceNumber)
```

任何人都可以推进锚定状态——合约内部验证 game 是否 proper、respected、finalized、`DEFENDER_WINS` 且比当前更新。

### Mantle：双轨制证明系统（代码存在，部署需确认）

Mantle 的验证相关代码分为两层。以下只能说明本地仓库中的合约实现和接口关系，不能单独证明主网实际部署状态；实际部署需结合 proxy 地址、implementation 地址和 Portal 指向的 oracle/factory 做链上确认。

#### 3.6 当前 contracts-bedrock 路径：L2OutputOracle（经典 Bedrock）

文件：`mantle-v2/.../L1/L2OutputOracle.sol`（Semver 1.3.0）

```solidity
function proposeL2Output(bytes32, uint256, bytes32, uint256) external  // 仅 PROPOSER 可调用
function deleteL2Outputs(uint256 _l2OutputIndex) external              // 仅 CHALLENGER 可调用
```

- `PROPOSER` 和 `CHALLENGER` 为 **immutable 地址**——单一许可提议者 + 单一许可挑战者
- 无链上验证——纯粹信任 PROPOSER 提交的 outputRoot
- `FINALIZATION_PERIOD_SECONDS` 为固定等待期
- 等同于早期 Optimism 的安全模型
- `OptimismPortal` 构造函数把 `L2_ORACLE` 设为 `immutable`，本地源码中的 Portal 路径依赖该 oracle；是否为当前主网实现需链上确认

#### 3.7 op-succinct 有效性证明路径（代码存在，部署未确认）

文件：`op-succinct/contracts/src/validity/OPSuccinctL2OutputOracle.sol`（v3.0.0-rc.1）

- 接口上保留经典 `proposeL2Output(bytes32,uint256,bytes32,uint256)`，并新增带证明参数的提议函数
- 但 Mantle 当前 `OptimismPortal` 的 `L2_ORACLE` 是 `immutable`，不能在现有 Portal 实例上简单改指向；迁移需要部署指向新 oracle 的 Portal 新实现并通过 ProxyAdmin 升级，同时验证 MNT 双资产逻辑与存储布局兼容
- `proposeL2Output` 扩展为 6 参数，新增 `configName`、`proof`、`proverAddress`
- 通过 `ISP1Verifier(verifier).verifyProof(aggregationVkey, publicValues, _proof)` 进行 **SP1 ZK 链上验证**
- 支持多配置（`OpSuccinctConfig`：`aggregationVkey`、`rangeVkeyCommitment`、`rollupConfigHash`）
- 具有 `optimisticMode` 降级和 `fallbackTimeout` 活性逃逸阀
- `approvedProposers` 白名单，`address(0)` 可切换为无需许可

`OPSuccinctDisputeGame` 是适配 DisputeGameFactory 的 CWIA 包装器：
- `initialize()` 调用 oracle 的 `proposeL2Output` 然后立即 `resolve()` 为 `DEFENDER_WINS`
- ZK 验证通过即视为**即时解决**，无争议窗口

#### 3.8 op-succinct 故障证明路径（代码存在，部署未确认）

文件：`op-succinct/contracts/src/fp/OPSuccinctFaultDisputeGame.sol`（Semver 1.0.0）

状态机：

```
Unchallenged ──→ Challenged ──→ ChallengedAndValidProofProvided ──→ Resolved
     │                                                                  ↑
     └──→ UnchallengedAndValidProofProvided ────────────────────────────┘
```

- 挑战者需发送 `CHALLENGER_BOND` 保证金
- 任一方可通过提交 SP1 证明解决争议（非交互式二分法）
- `AccessManager` 控制提议/挑战权限
- 需要 `OptimismPortal2` 风格的 Portal——当前仅以 `MockOptimismPortal2` 测试用途存在

### 验证架构对比总结

| 维度 | Base | Mantle |
|------|------|--------|
| 部署状态 | 当前检出仅能通过 ABI 绑定确认 Base proof 合约接口；是否已部署需链上确认 | `mantle-v2` 和 `op-succinct` 合约代码存在；实际生产使用哪一路需链上确认 |
| 证明类型 | TEE + ZK（多证明聚合） | SP1 ZK（有效性 + 故障证明双轨） |
| 设计理念 | TEE 快速提交，ZK 作为仲裁者 | ZK 直接验证，或 ZK 挑战式解决 |
| 链上验证 | ABI 显示支持 TEE 签名验证 + ZK 证明验证 | op-succinct 代码支持 SP1 验证；是否部署未确认 |
| Dispute Game | 自研 AggregateVerifier | 上游 + OPSuccinctFaultDisputeGame |
| 中间输出根 | 支持（细粒度挑战） | 不支持 |
| TEE 硬件证明 | 完整（Nitro 认证 → ZK 验证 → 链上注册） | 无 |
| 活性保障 | 无需许可提议 | 白名单提议者 + fallbackTimeout |

---

## 4. AddressManager / ProxyAdmin

### Base

使用上游 OP Stack 标准配置。地址列表（`AddressList` struct）严格遵循 Superchain Registry 格式：

**标准 L1 合约**：`address_manager`、`l1_cross_domain_messenger_proxy`、`l1_standard_bridge_proxy`、`l1_erc721_bridge_proxy`、`optimism_portal_proxy`、`system_config_proxy`、`proxy_admin`

**Fault Proof 合约**：`anchor_state_registry_proxy`、`delayed_weth_proxy`、`dispute_game_factory_proxy`、`fault_dispute_game`、`permissioned_dispute_game`、`preimage_oracle`、`mips`

注意：Base 自研的 `AggregateVerifier`、`TEEProverRegistry`、`NitroEnclaveVerifier` 地址**不在此结构体中**——它们通过独立的 proof-specific 配置管理，与上游兼容的 AddressList 解耦。

### Mantle

`ProxyAdmin`（`mantle-v2/.../universal/ProxyAdmin.sol`）支持三种代理类型的枚举：

| 代理类型 | 说明 | 使用场景 |
|---------|------|---------|
| `ERC1967` | 标准透明代理 | SystemConfig、L2OutputOracle、OptimismPortal |
| `CHUGSPLASH` | 旧版 L1ChugSplashProxy | 旧部署迁移中 |
| `RESOLVED` | ResolvedDelegateProxy | L1CrossDomainMessenger |

`AddressManager`（`mantle-v2/.../legacy/AddressManager.sol`）仍在使用，为 `ResolvedDelegateProxy` 实例提供地址解析。

**遗留代理债务**：Mantle 仍需维护 CHUGSPLASH 和 RESOLVED 代理类型，因为 L1CrossDomainMessenger 运行在 ResolvedDelegateProxy 上。部署脚本中明确指出这一约束。Base 通过使用上游标准避免了此问题。


---

# 合约治理模型差异摘要

## 核心发现

### 1. 两者的定制重心完全不同

**Base** 的合约定制集中在**证明验证层**——AggregateVerifier、TEEProverRegistry、NitroEnclaveVerifier 等构成了一套完整的多证明验证系统，而桥接层（Portal、Messenger、Bridge）完全复用上游 OP Stack 不做任何改动。

**Mantle** 的合约定制集中在**桥接层**——因 MNT 原生代币的选择，Portal、Messenger、Bridge 都需要深度改造以支持双资产模型，而验证层仍停留在经典 Bedrock 的许可制 oracle。

这导致了截然不同的维护成本分布：
- Base：proof 合约独立演进，桥接合约自动跟随上游
- Mantle：桥接合约每次上游升级都需手动合并 MNT 改动，proof 合约虽有 op-succinct 代码路径，但实际部署状态需链上确认

### 2. Mantle 的证明系统存在"代码路径与当前 Portal 路径分离"的问题

Mantle 在 op-succinct 仓库中拥有两套证明合约：
- **OPSuccinctL2OutputOracle** — SP1 ZK 有效性证明，接口上可替换经典 L2OutputOracle
- **OPSuccinctFaultDisputeGame** — SP1 故障证明状态机，支持挑战-证明式争议解决

本地 `mantle-v2` 的 Portal 路径仍依赖经典 Bedrock `L2OutputOracle`（许可制 PROPOSER + CHALLENGER）。这不能单独证明主网实际部署状态，但能说明迁移 op-succinct 不是单独替换 oracle 地址即可完成。关键阻碍在于：
- **Portal 的 `L2_ORACLE` 是 `immutable`**——不能在现有 Portal 上简单切换 oracle 指向。切换到 OPSuccinctL2OutputOracle 需要：(1) 部署包含新 oracle 地址的 Portal 新实现合约，(2) 通过 ProxyAdmin 升级 Portal 代理指向新实现，(3) 确保新实现与现有 MNT 双资产存储布局兼容
- 故障证明路径需要 OptimismPortal2（支持 DisputeGame 接口），目前仅以 `MockOptimismPortal2` 测试形式存在
- Portal 的 MNT 双资产改动使得从 Portal v1 升级到 Portal2 工程量更大——需要在 Portal2 接口上重新实现全部 MNT 双 value 字段和安全保护逻辑

### 3. MNT 原生代币是一把双刃剑

**收益**：MNT 持有者作为 Mantle 生态的 gas 支付者，与网络利益深度绑定。

**成本**：
- **代码膨胀**：Portal（7 参数 vs 4 参数）、Messenger（双 value sendMessage）、Bridge（三类资产独立路径）
- **协议不兼容**：`DEPOSIT_VERSION=1`（上游为 0）、opaqueData 四字段（上游两字段）、消息哈希包含 `_mntValue`
- **安全表面扩大**：MNT approve/transferFrom 模式引入新攻击向量、需要 `target != L1_MNT_ADDRESS` 保护
- **上游同步摩擦**：每次 OP Stack 升级 Portal/Messenger/Bridge 时都需要手动合并

### 4. Base 的多证明架构代表更激进的证明层设计

Base 的 AggregateVerifier 设计解决了一个核心工程权衡：

```
TEE 证明 → 成本低、速度快、但需信任硬件
ZK 证明 → 成本高、速度慢、但数学可验证

AggregateVerifier 方案：TEE 提交日常证明，ZK 仅在不同意时介入
→ 兼顾 TEE 的效率和 ZK 的安全性
```

关键创新点：
- **中间输出根**：支持细粒度挑战，无需回滚整个 game
- **ZK 证明的 TEE 注册**：即使是 TEE 的注册过程也经过 ZK 验证（Nitro 认证 → ZK 证明 → 链上注册）
- **链上证书撤销**：无需升级合约即可应对 TEE 安全事件
- **原子化 game 创建**：`createWithInitData` 在一笔交易中完成创建+证明提交

### 5. Mantle 的升级路径存在不确定性

从代码中可以观察到：
- Arsia 升级**仅升级了 SystemConfig**，Portal 和 L2OutputOracle 明确未动
- 版本号不一致（Portal 文档注释 1.6.0 vs 构造函数 1.7.0）暗示升级管理不够严谨
- 遗留代理债务（CHUGSPLASH、RESOLVED）限制了升级灵活性
- 从许可制 oracle 向 ZK 验证的迁移涉及 Portal 的 MNT 改动重做，工程量巨大

### 6. 治理模型差异源于不同的信任假设

| 维度 | Base | Mantle |
|------|------|--------|
| **提议者信任** | 信任 TEE 硬件 + ZK 仲裁 | 信任单一 PROPOSER 地址 |
| **挑战能力** | 无需许可（任何人可提交 ZK 挑战） | 需 CHALLENGER 地址（许可制回滚） |
| **紧急响应** | 多层次（证书撤销、TEE 注销、game 黑名单） | 单一（CHALLENGER 回滚 output） |
| **升级权限** | ProxyAdmin（上游标准） | ProxyAdmin（含遗留兼容） |
| **去中心化程度** | 较高（无需许可挑战 + 无需许可锚定推进） | 较低（许可制提议+挑战） |

---

## 对 Mantle 的建议

### 短期（可立即执行）

1. **统一代理模式**：将 L1CrossDomainMessenger 从 ResolvedDelegateProxy 迁移至 ERC-1967，消除遗留代理债务
2. **修复版本号不一致**：统一 OptimismPortal 的文档注释和构造函数 Semver
3. **引入升级时间锁**：在 ProxyAdmin 和 PROPOSER/CHALLENGER 之间增加 Timelock，提高升级透明度

### 中期（需要规划）

4. **部署 OPSuccinctL2OutputOracle**：接口上可替换经典 L2OutputOracle，但由于 Portal 的 `L2_ORACLE` 为 `immutable`，实际迁移需要：部署新 Portal 实现（指向新 oracle）→ 验证 MNT 双资产存储布局兼容性 → 通过 ProxyAdmin 升级代理。这不是"最小改动"，而是一次需要审慎规划的 Portal 升级
5. **评估 MNT 兼容 Portal2 的工程量**：这是从有效性证明迈向故障证明的关键路径，Portal2 需要在 DisputeGame 接口之上重新实现全部 MNT 双 value 逻辑

### 长期（架构层面）

6. **考虑 Base 式的多证明聚合**：TEE+ZK 模式可以显著降低证明成本，同时保持安全性
7. **评估中间输出根的价值**：细粒度挑战可以减少争议解决时间和成本


---

# 升级机制对比

## 1. Proxy 模式

### Base

Base 使用上游 OP Stack 的标准代理架构：

- **ERC-1967 透明代理**：所有核心合约（SystemConfig、OptimismPortal、L2OutputOracle 等）均通过 `Proxy.sol` 部署
- **Clone-With-Immutable-Args (CWIA)**：Dispute Game 使用 CWIA 最小代理克隆，每个 game 实例是一个轻量级代理，immutable 参数通过字节偏移读取。这比 ERC-1967 代理更省 gas，适合大量短生命周期的 game 实例

Base 的代理架构特点：
- 所有 `_proxy` 后缀的地址对应 ERC-1967 代理
- DisputeGameFactory 通过 `gameImpls(gameType)` 管理不同 game 类型的实现合约
- CWIA 打包编码（非 ABI 编码）使 `extraData` 的 gas 成本更低

### Mantle

Mantle 的 `ProxyAdmin.sol` 支持三种代理模式的枚举：

```solidity
enum ProxyType {
    ERC1967,       // 标准透明代理（主流使用）
    CHUGSPLASH,    // 旧版 ChugSplash 代理（遗留）
    RESOLVED       // ResolvedDelegateProxy（通过 AddressManager 解析）
}
```

当前使用情况：

| 合约 | 代理类型 | 说明 |
|------|---------|------|
| SystemConfig | ERC1967 | 标准 |
| OptimismPortal | ERC1967 | 标准 |
| L2OutputOracle | ERC1967 | 标准 |
| L1StandardBridge | ERC1967 | 标准 |
| L1CrossDomainMessenger | **RESOLVED** | 通过 AddressManager 解析实现地址 |
| 旧合约 | CHUGSPLASH | 迁移过渡期保留 |

**遗留代理债务**：`L1CrossDomainMessenger` 仍运行在 `ResolvedDelegateProxy` 上，这意味着：
1. `AddressManager` 合约不能退役——它仍是 Messenger 的地址解析依赖
2. `ProxyAdmin` 必须维护三套升级逻辑
3. 部署脚本中有明确注释指出这一约束

---

## 2. 升级权限管理

### Base

Base 的合约仓库 (`github.com/base/contracts`) 不在当前检出范围内，无法直接查看升级权限配置。但从架构上：

- `ProxyAdmin` 作为所有代理合约的 owner，控制实现地址的升级
- 通过上游 OP Stack 标准流程管理
- `AnchorStateRegistry.setAnchorState()` 为无需许可操作——任何人都可以推进锚定状态，无需多签
- TEE prover 注册/注销通过 `TEEProverRegistry` 管理，与代理升级解耦

### Mantle

从代码中可以观察到的升级权限模式：

- `ProxyAdmin` 是所有代理的唯一 owner
- 升级脚本（`UpgradeL1Contracts.s.sol`）直接调用 `IProxyAdmin(_proxyAdmin).upgrade()`
- 无可见的 Timelock 合约或多签 wrapper——升级路径看起来是**直接的单一 owner 调用**
- `L2OutputOracle` 的 `PROPOSER` 和 `CHALLENGER` 为 immutable，更换需要重新部署实现合约并升级代理

---

## 3. 时间锁与社区审查

### Base

基于上游 OP Stack 的标准机制。Superchain 生态中，Base 作为 Coinbase 运营的链，其安全委员会和多签配置遵循 Optimism Foundation 的治理框架。

与验证相关的时间延迟：
- `DelayedWETH.delay()` — 保证金领取的延迟期
- `AggregateVerifier.expectedResolution` — 争议期时间戳
- 这些是协议层面的安全延迟，而非升级层面的时间锁

### Mantle

代码中未见显式的 Timelock 合约。已观察到的时间相关机制：
- `FINALIZATION_PERIOD_SECONDS`（L2OutputOracle）— 提款最终确认的等待期，为 immutable 值
- 升级脚本中无 Timelock 调用

---

## 4. 紧急升级路径

### Base

- `NitroEnclaveVerifier.revokeCert(bytes32 certHash)` — 可紧急撤销被入侵的 TEE 证书（来源于 Immunefi #75608 安全响应）
- `TEEProverRegistry.deregisterSigner(address)` — 可紧急注销 TEE 签名者
- `AnchorStateRegistry` 支持 game 黑名单和退役：`isGameBlacklisted`、`isGameRetired` — 可标记恶意或有问题的 game

这些机制提供了**无需升级合约即可响应安全事件**的能力。

### Mantle

- `L2OutputOracle.deleteL2Outputs(uint256 _l2OutputIndex)` — CHALLENGER 可在 finalization period 内回滚 output
- 这是唯一的链上紧急响应机制
- 更大规模的安全事件需要通过 ProxyAdmin 升级合约实现

---

## 5. Mantle 升级历史

Mantle 经历了多个命名的升级阶段。以下基于代码中可追溯的证据：

### BedRock（基础版本）

- 初始部署基于 Optimism Bedrock 架构
- `LegacyERC20MNT.sol` 注释："All MNT balances held within this contract were migrated to the state trie as part of the Bedrock upgrade"
- 建立了 MNT 原生代币 + BVM_ETH 的双资产模型

### 中间升级（Everest → Euboea → Skadi）

- 代码中**未找到 Everest、Euboea、Skadi 的直接标记**
- 这些可能是基础设施/客户端层面的升级，不涉及 L1 合约变更
- 或者其合约变更已被后续版本覆盖，无法从当前代码追溯

### Limb

- 作为 Arsia 升级的前一版本被提及
- SystemConfig 版本为 1.3.0

### Arsia（当前进行中的升级）

从代码中找到的 Arsia 相关变更：

**L1 合约**：

| 合约 | 变更 |
|------|------|
| `SystemConfig` | 1.3.0 → 1.4.0：新增 `setGasConfigArsia()`，引入 Ecotone 风格的 scalar 打包（version byte `0x01`） |
| `L2OutputOracle` | **未升级**（脚本明确注释） |
| `OptimismPortal` | **未升级**（脚本明确注释） |

**L2 合约**：

| 合约 | 变更 |
|------|------|
| `L1Block` | `setL1BlockValuesArsia()` — 新的 deposit 属性编码，包含 blob base fee、operator fee、DA footprint |
| `GasPriceOracle` | `isArsia` 单向标志位、`setArsia()`（仅 depositor 账户可调用）、`_getL1FeeArsia`、`getL1FeeUpperBound`（Arsia-only） |

**升级脚本**（`UpgradeL1Contracts.s.sol`）：
```
"Script to upgrade L1 SystemConfig contract for Mantle Limb to Arsia upgrade"
```
使用 `IProxyAdmin.upgrade()` 直接升级 SystemConfig 代理的实现地址。

### 合约版本汇总

| 合约 | 当前 Semver | 说明 |
|------|-----------|------|
| SystemConfig | 1.4.0 | Arsia 升级后 |
| OptimismPortal | 1.7.0 | 文档注释写 1.6.0，构造函数为 1.7.0 |
| L2OutputOracle | 1.3.0 | 经典 Bedrock |
| L1CrossDomainMessenger | 1.5.0 | MNT 双资产消息 |
| L1StandardBridge | 1.1.0 | MNT 桥接路径 |
| OPSuccinctDisputeGame (op-succinct) | v3.0.0-rc.1 | 代码存在，部署需链上确认 |
| OPSuccinctFaultDisputeGame (op-succinct) | 1.0.0 | 代码存在，部署需链上确认 |

### 升级轨迹观察

1. **增量升级为主**：每次升级仅涉及少量合约，而非全面替换
2. **Portal 版本号不一致**：文档注释与构造函数 Semver 不匹配（1.6.0 vs 1.7.0），暗示存在未完全同步的升级过程
3. **渐进式对齐上游**：Arsia 引入 Ecotone 风格 scalar，表明 Mantle 正在逐步向上游 OP Stack 标准靠拢
4. **证明系统升级尚未开始**：L2OutputOracle 和 OptimismPortal 在 Arsia 中明确未升级，意味着从许可制 oracle 向 ZK 验证的迁移还在规划阶段

---

## 6. 对比总结

| 维度 | Base | Mantle |
|------|------|--------|
| 代理模式 | ERC-1967 + CWIA（统一） | ERC-1967 + CHUGSPLASH + RESOLVED（混合遗留） |
| 代理管理 | ProxyAdmin（上游标准） | ProxyAdmin（三模式枚举，含遗留支持） |
| 升级脚本 | 未在检出范围内 | 单一 `UpgradeL1Contracts.s.sol` |
| 时间锁 | 未在检出范围内 | 代码中未见显式 Timelock |
| 紧急响应 | 证书撤销 + TEE 注销 + Game 黑名单（无需升级） | L2Output 回滚（需 CHALLENGER 权限） |
| 上游同步 | 桥接层完全复用上游，仅 proof 层自研 | 每次升级需手动合并 MNT 双资产改动 |
| 升级频率 | 不适用（仅 proof 合约独立演进） | 渐进式（每次仅升级部分合约） |
