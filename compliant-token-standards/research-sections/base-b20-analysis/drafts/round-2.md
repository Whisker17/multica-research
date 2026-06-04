---
topic: "Base B20 标准深度分析（Beryl 升级）"
project_slug: compliant-token-standards
topic_slug: base-b20-analysis
github_repo: Whisker17/multica-research
round: 2
status: draft
artifact_paths:
  outline: outlines/base-b20-analysis.md
  draft: compliant-token-standards/research-sections/base-b20-analysis/drafts/round-2.md
draft_metadata:
  outline_round: 2
  outline_commit: 817448d
  codebase: "base/base @ 8e8767281d7c8768f6a0aed9124779cd4ed030ae"
  language: zh-CN
  date: 2026-06-04
---

# Base B20 Token 标准深度分析（Beryl 升级）

> **代码基准**: `base/base` @ commit [`8e8767281d7c8768f6a0aed9124779cd4ed030ae`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)
>
> **分析性质**: 基于实现的分析（implementation-based）。截至分析日期，Base 尚未发布正式的 Beryl 升级规范或 B20 标准文档。所有结论均从代码推导，待正式规范发布后可能存在偏差。

---

## 执行摘要

B20 是 Base 链在 Beryl 硬分叉中引入的合规导向预编译代币框架。与传统 Solidity 合约代币不同，B20 以 EVM 预编译（precompile）形式实现，将代币逻辑固化在节点执行层，从而实现确定性执行、零部署成本和原生 ZK 可证明性。

**架构核心**：B20 采用 Rust trait 组合模式构建，以 `Token` trait 为中心桥接，通过 7 个能力 trait（Transferable、Mintable、Burnable、RoleManaged、Pausable、Configurable、Permittable）实现功能组合。`B20Guards` 是一个辅助结构体（helper struct），提供统一的授权检查方法，而非能力 trait。所有能力 trait 通过关联类型 `Accounting: TokenAccounting` 和 `Policy: Policy` 实现编译期单态化（monomorphization），消除虚表（vtable）开销。

**产品层面**：框架包含两个生产变体——B20Asset（资产代币，支持乘数缩放、批量铸造、公告机制、扩展元数据）和 B20Stablecoin（稳定币，仅扩展货币标识符）。B20Factory 以单例预编译形式提供确定性地址推导的代币创建服务。PolicyRegistry 提供四维合规策略（发送方、接收方、执行方、铸造接收方），支持黑名单/白名单两种策略类型。ActivationRegistry 实现硬分叉门控的特性激活。

**合规特征**：B20 原生集成 RBAC（7 种角色）、功能级暂停、策略驱动的地址过滤、burnBlocked（合规销毁）等机制，使其成为目前公链 L2 中合规能力最为完整的预编译代币标准之一。

**版本声明**：B20Security（`b20_security/`）仅存在于本地分支（超前于远程 HEAD），本文将其作为演进信号（evolutionary signal）记录，不代表当前 Base 主线事实。

---

## 第一章 B20 架构总览

### 1.1 系统级模块地图

B20 子系统由以下预编译模块组成，代码均位于 `crates/common/precompiles/src/` 目录下：

| 模块 | 路径 | 职责 | 预编译地址 |
|------|------|------|-----------|
| **Shared IB20** | `common/` | 共享接口定义、核心存储、能力 trait、策略类型 | — （内嵌于各变体） |
| **B20Factory** | `b20_factory/` | 代币创建、变体管理、地址推导 | `0xB20F000000000000000000000000000000000000` |
| **B20Asset** | `b20_asset/` | 资产变体扩展（乘数、批量铸造、公告、元数据） | 动态地址（`0xb2` 前缀 + `0x00` 判别字节） |
| **B20Stablecoin** | `b20_stablecoin/` | 稳定币变体扩展（货币标识符） | 动态地址（`0xb2` 前缀 + `0x01` 判别字节） |
| **PolicyRegistry** | `policy/` | 合规策略引擎（黑名单/白名单 CRUD） | `0x8453000000000000000000000000000000000002` |
| **ActivationRegistry** | `activation/` | 硬分叉特性激活门控 | `0x8453000000000000000000000000000000000001` |

> 源码引用: `crates/common/precompiles/src/common/mod.rs` @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

**模块依赖关系**：

```
ActivationRegistry
  │
  ├── 门控 ──→ B20Factory（创建时检查变体激活状态）
  │             │
  │             ├── 初始化 ──→ B20AssetToken
  │             └── 初始化 ──→ B20StablecoinToken
  │
  └── 门控 ──→ PolicyRegistry（写操作需要 PolicyRegistry 特性激活）
                  │
                  └── 被查询 ←── B20AssetToken / B20StablecoinToken
                                 （通过 Policy trait 进行策略授权检查）
```

**Beryl 激活序列**：ActivationRegistry 是 B20 子系统的入口门控。每个特性以 `keccak256(特性名称字符串)` 作为特性 ID：

- `ActivationFeature::PolicyRegistry` → `keccak256("base.policy_registry")`
- `ActivationFeature::B20Asset` → `keccak256("base.b20_asset")`
- `ActivationFeature::B20Stablecoin` → `keccak256("base.b20_stablecoin")`

管理员通过 `activate(feature)` 调用激活特性，此后 Factory 才能创建对应变体的代币，PolicyRegistry 才能执行写操作。视图函数（view functions）始终可访问，不受激活状态约束。

> 源码引用: `crates/common/precompiles/src/activation/storage.rs` — `ActivationFeature` 枚举, `ADDRESS` 常量 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 1.2 能力 Trait 组合模式

B20 的核心设计哲学是**能力 trait 组合**（capability-trait composition）。`Token` trait 作为中央桥接层定义了两个关联类型：

```rust
pub trait Token {
    type Accounting: TokenAccounting;
    type Policy: Policy;

    fn accounting(&self) -> &Self::Accounting;
    fn accounting_mut(&mut self) -> &mut Self::Accounting;
    fn policy(&self) -> &Self::Policy;
    fn policy_mut(&mut self) -> &mut Self::Policy;
    fn token_address(&self) -> Address;
}
```

所有能力 trait 均以 `Token` 为超 trait（supertrait），通过 `Token::accounting()` 访问存储端口，通过 `Token::policy()` 访问策略注册表。由于关联类型在编译期绑定具体类型，Rust 编译器对所有存储和策略调用执行单态化，**消除了虚表分发开销**。

**7 个能力 trait**（位于 `common/ops/`）：

| Trait | 职责 | 关键方法 |
|-------|------|---------|
| `Transferable` | ERC-20 转账、授权、memo 装饰 | `transfer`, `transfer_from`, `approve`, `transfer_with_memo` |
| `Mintable` | 代币铸造、供给上限检查 | `mint`, `mint_with_memo` |
| `Burnable` | 代币销毁、合规强制销毁 | `burn`, `burn_blocked`, `burn_with_memo` |
| `RoleManaged` | RBAC 角色管理 | `grant_role`, `revoke_role`, `renounce_last_admin` |
| `Pausable` | 功能级暂停/恢复 | `pause`, `unpause`, `is_paused` |
| `Configurable` | 供给上限、名称、符号、URI 更新 | `update_supply_cap`, `update_name`, `update_symbol`, `update_contract_uri` |
| `Permittable` | EIP-2612 permit、EIP-712 域 | `permit`, `domain_separator`, `eip712_domain` |

> 源码引用: `crates/common/precompiles/src/common/ops/mod.rs` — 模块导出 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

**B20Guards 辅助结构体**：`B20Guards` 是一个无状态单元结构体（`pub struct B20Guards;`），提供静态方法用于统一授权检查。它**不是能力 trait**，而是被各能力 trait 内部调用的授权守卫层：

- `ensure_not_paused<T>` — 检查暂停位掩码
- `ensure_token_role<T>` / `ensure_role<T>` — 检查 RBAC 角色
- `ensure_policy_type<T>` / `ensure_policy<T>` — 委托外部 PolicyRegistry 检查地址授权
- `ensure_blocked<T>` — 反向检查：确认地址被封锁（用于 `burnBlocked`）

守卫执行顺序：**暂停检查 → 角色检查 → 策略检查 → 业务不变量检查**。

> 源码引用: `crates/common/precompiles/src/common/ops/guards.rs` — `B20Guards` 结构体及方法 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

**变体 opt-in 模式**：每个代币变体通过空体实现（empty body implementation）选择启用能力 trait。例如 `B20AssetToken` 和 `B20StablecoinToken` 均实现了全部 7 个能力 trait，因为所有默认实现均仅依赖 `TokenAccounting` 端口。

**`privileged` 标志**：能力 trait 的方法普遍接受 `privileged: bool` 参数。当 `privileged = true` 时（Factory 初始化窗口期），角色检查和策略检查被跳过，但**暂停检查始终执行**。这确保了即使在初始化阶段，暂停机制也具有最高优先级。

> 源码引用: `crates/common/precompiles/src/common/token.rs` — `Token` trait 定义 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 1.3 B20Variant 地址编码

B20 代币使用确定性地址推导，地址格式为 20 字节结构化编码：

```
[0xb2][9 个零字节][判别字节][9 个哈希字节]
 ┃      ┃           ┃          ┗━ keccak256((creator, salt)) 的前 9 字节
 ┃      ┃           ┗━ 变体判别符: 0x00=Asset, 0x01=Stablecoin
 ┃      ┗━ 固定零填充
 ┗━ B20 前缀字节 (PREFIX_BYTE)
```

**变体判别符**：

| 变体 | 判别字节 | 枚举值 |
|------|---------|-------|
| Asset | `0x00` | `B20Variant::Asset = 0` |
| Stablecoin | `0x01` | `B20Variant::Stablecoin = 1` |

**地址推导函数**：`B20Variant::compute_address(self, creator: Address, salt: B256) -> (Address, [u8; 9])`
- 输入：`creator`（调用者地址）+ `salt`（32 字节盐值）
- 计算：`keccak256(abi_encode(creator, salt))` 取前 9 字节作为哈希尾部
- 输出：`[0xb2][0x00 × 9][discriminant][hash_tail]` 拼接为 20 字节地址

**地址识别函数**：
- `has_b20_prefix(address)` — 结构性前缀检查（字节 0-9 为 `0xb2` + 9 个零），包含保留判别符
- `from_address(address)` — 提取变体枚举值（仅 0x00/0x01 有效）
- Factory 的 `is_b20(token)` — 调用 `has_b20_prefix` 进行结构性检查
- Factory 的 `is_b20_initialized(token)` — 检查 Factory 部署状态（是否存在 `0xef` 桩字节码）

Factory 单例地址: `0xB20F000000000000000000000000000000000000`

> 源码引用: `crates/common/precompiles/src/b20_factory/variant.rs` — `B20Variant` 枚举, `compute_address()`, `has_b20_prefix()` @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

---

## 第二章 共享 IB20 接口与通用能力层

### 2.1 IB20 Solidity 接口

IB20 是所有 B20 变体继承的共享接口，通过 Rust `sol!` 宏定义。完整接口包含 **50 个函数**、**16 个事件**和 **22 个错误类型**。

**函数清单（按功能分类）**：

| 类别 | 函数 | 数量 |
|------|------|------|
| **角色常量** | `DEFAULT_ADMIN_ROLE`, `MINT_ROLE`, `BURN_ROLE`, `BURN_BLOCKED_ROLE`, `PAUSE_ROLE`, `UNPAUSE_ROLE`, `METADATA_ROLE` | 7 |
| **策略范围** | `TRANSFER_SENDER_POLICY`, `TRANSFER_RECEIVER_POLICY`, `TRANSFER_EXECUTOR_POLICY`, `MINT_RECEIVER_POLICY` | 4 |
| **ERC-20 核心** | `name`, `symbol`, `decimals`, `totalSupply`, `balanceOf`, `allowance`, `transfer`, `transferFrom`, `approve` | 9 |
| **Memo 扩展** | `transferWithMemo`, `transferFromWithMemo`, `mintWithMemo`, `burnWithMemo` | 4 |
| **铸造/销毁** | `mint`, `burn`, `burnBlocked` | 3 |
| **角色管理** | `hasRole`, `getRoleAdmin`, `grantRole`, `revokeRole`, `renounceRole`, `renounceLastAdmin`, `setRoleAdmin` | 7 |
| **暂停** | `pausedFeatures`, `isPaused`, `pause`, `unpause` | 4 |
| **策略** | `policyId`, `updatePolicy` | 2 |
| **配置** | `supplyCap`, `updateSupplyCap`, `updateName`, `updateSymbol`, `contractURI`, `updateContractURI` | 6 |
| **Permit** | `DOMAIN_SEPARATOR`, `nonces`, `permit`, `eip712Domain` | 4 |

**事件清单**（16 个）：

| 事件 | 索引参数 | 说明 |
|------|---------|------|
| `Transfer(from, to, amount)` | `from`, `to` | ERC-20 标准转账 |
| `Approval(owner, spender, amount)` | `owner`, `spender` | ERC-20 标准授权 |
| `Memo(caller, memo)` | `caller`, `memo` | 32 字节 memo 附加事件 |
| `BurnedBlocked(caller, from, amount)` | `caller`, `from` | 合规强制销毁记录 |
| `RoleGranted(role, account, sender)` | `role`, `account`, `sender` | RBAC 角色授予 |
| `RoleRevoked(role, account, sender)` | `role`, `account`, `sender` | RBAC 角色撤销 |
| `RoleAdminChanged(role, previousAdmin, newAdmin)` | `role`, `previousAdmin`, `newAdmin` | 角色管理员变更 |
| `LastAdminRenounced(lastAdmin)` | `lastAdmin` | 终极管理员放弃 |
| `Paused(updater, features[])` | `updater` | 功能暂停 |
| `Unpaused(updater, features[])` | `updater` | 功能恢复 |
| `PolicyUpdated(policyScope, oldPolicyId, newPolicyId)` | `policyScope` | 策略绑定更新（无 updater 参数） |
| `SupplyCapUpdated(updater, oldCap, newCap)` | `updater` | 供给上限更新 |
| `NameUpdated(updater, newName)` | `updater` | 名称更新 |
| `SymbolUpdated(updater, newSymbol)` | `updater` | 符号更新 |
| `ContractURIUpdated()` | — | ERC-7572 URI 更新 |
| `EIP712DomainChanged()` | — | ERC-5267 域变更（名称更新触发） |

**错误类型**（22 个）：

`AccessControlUnauthorizedAccount(account, neededRole)`、`Unauthorized`、`ContractPaused(PausableFeature)`、`InsufficientAllowance(spender, allowance, needed)`、`InsufficientBalance(sender, balance, needed)`、`InvalidSender(sender)`、`InvalidReceiver(receiver)`、`InvalidApprover(approver)`、`InvalidSpender(spender)`、`InvalidAmount`、`EmptyFeatureSet`、`InvalidSupplyCap(currentSupply, proposedCap)`、`SupplyCapExceeded(cap, attempted)`、`PolicyForbids(policyScope, policyId)`、`PolicyNotFound(policyId)`、`UnsupportedPolicyType(policyScope)`、`AccountNotBlocked(account)`、`ExpiredSignature(deadline)`、`InvalidSigner(signer, owner)`、`LastAdminCannotRenounce`、`NotSoleAdmin`、`AccessControlBadConfirmation`。

**PausableFeature 枚举**：`TRANSFER = 0`、`MINT = 1`、`BURN = 2`

**ERC 兼容性标记**：
- **ERC-20** — 完整的 `transfer`/`transferFrom`/`approve`/`balanceOf`/`totalSupply`/`allowance`/`name`/`symbol`/`decimals` 接口
- **EIP-2612** — `permit`/`nonces`/`DOMAIN_SEPARATOR`
- **ERC-5267** — `eip712Domain()` 返回标准七元组
- **ERC-7572** — `contractURI()`/`updateContractURI()`

**调用标签**：每个 IB20 调用均通过 `as_label()` 映射到稳定的字符串标签（如 `"precompile-b20-transfer"`），用于链上计量和监控。

> 源码引用: `crates/common/precompiles/src/common/abi.rs` — `IB20` 接口完整定义 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 2.2 B20CoreStorage 存储布局

B20CoreStorage 使用 ERC-7201 命名空间存储模式，命名空间为 `base.b20`，存储根为 `0xc78b71fee795ddd74aff64ea9b2474194c938c3196430e10bb5f01ed48434000`。共包含 **14 个存储槽**：

| 槽位 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 0 | `name` | `String` | 代币名称 |
| 1 | `symbol` | `String` | 代币符号 |
| 2 | `contract_uri` | `String` | ERC-7572 合约 URI |
| 3 | `total_supply` | `U256` | 当前总供给 |
| 4 | `balances` | `Mapping<Address, U256>` | 账户余额映射 |
| 5 | `allowances` | `Mapping<Address, Mapping<Address, U256>>` | 授权映射 |
| 6 | `roles` | `Mapping<B256, Mapping<Address, bool>>` | 角色成员映射 |
| 7 | `role_admins` | `Mapping<B256, B256>` | 角色管理员映射 |
| 8 | `admin_count` | `U256` | 管理员计数（终极管理员保护） |
| **9** | **（打包槽）** | — | 转账策略 ID 打包 |
| → offset 0 | `transfer_sender_policy_id` | `u64` | 发送方策略 ID |
| → offset 8 | `transfer_receiver_policy_id` | `u64` | 接收方策略 ID |
| → offset 16 | `transfer_executor_policy_id` | `u64` | 执行方策略 ID |
| → offset 24 | `transfer_reserved_0` | `u64` | 保留填充 |
| **10** | **（打包槽）** | — | 铸造策略 ID 打包 |
| → offset 0 | `mint_receiver_policy_id` | `u64` | 铸造接收方策略 ID |
| → offset 8 | `mint_reserved` | `FixedBytes<24>` | 保留填充 |
| 11 | `paused` | `U256` | 暂停位掩码 |
| 12 | `supply_cap` | `U256` | 最大供给上限 |
| 13 | `nonces` | `Mapping<Address, U256>` | EIP-2612 permit nonce |

**策略 ID 打包**：4 个 `u64` 策略 ID 被紧凑打包进 2 个 `U256` 槽位（槽 9 和槽 10），每个 ID 占 8 字节。这种打包设计节省了存储空间（2 个槽位承载 4 个策略绑定），同时保持了策略绑定的独立更新能力。

> 源码引用: `crates/common/precompiles/src/common/core_storage.rs` — `B20CoreStorage` 结构体 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 2.3 RBAC 系统

B20 实现了完整的基于角色的访问控制（RBAC）系统，包含 7 种预定义角色：

| 角色 | 常量值 | 功能 |
|------|--------|------|
| `DEFAULT_ADMIN_ROLE` | `B256::ZERO` | 管理所有角色的超级管理员 |
| `MINT_ROLE` | `keccak256(...)` = `0x154c00...` | 铸造权限 |
| `BURN_ROLE` | `keccak256(...)` = `0xe97b13...` | 销毁权限 |
| `BURN_BLOCKED_ROLE` | `keccak256(...)` = `0x7408fd...` | 合规强制销毁权限 |
| `PAUSE_ROLE` | `keccak256(...)` = `0x139c28...` | 暂停权限 |
| `UNPAUSE_ROLE` | `keccak256(...)` = `0x265b22...` | 恢复权限 |
| `METADATA_ROLE` | `keccak256(...)` = `0x6bd6b5...` | 元数据更新权限 |

**角色层级**：每个角色有一个管理员角色（`role_admins` 映射）。默认情况下，所有角色的管理员都是 `DEFAULT_ADMIN_ROLE`。管理员可以通过 `setRoleAdmin(role, adminRole)` 修改角色的管理员。

**授予/撤销机制**：
- `grantRole(role, account)` — 仅角色管理员可调用，追踪 `admin_count`
- `revokeRole(role, account)` — 仅角色管理员可调用
- `renounceRole(role, account)` — 持有者自行放弃，需 `account == caller` 确认

**终极管理员状态**：`renounceLastAdmin()` 是一个**不可逆操作**。调用者必须是最后一个 `DEFAULT_ADMIN_ROLE` 持有者（`admin_count == 1`，由 `NotSoleAdmin` 错误保护）。一旦执行，所有角色变更永久冻结，代币进入不可变状态。`LastAdminRenounced` 事件标记此终态。

**管理员计数追踪**：`admin_count` 字段（槽 8）精确追踪 `DEFAULT_ADMIN_ROLE` 的持有者数量，在授予和撤销时自动递增/递减，为 `renounceLastAdmin` 的安全性提供保障。

> 源码引用: `crates/common/precompiles/src/common/ops/roles.rs` — `B20TokenRole` 枚举, `RoleManaged` trait @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 2.4 ERC-20 + Memo + Permit

**标准 ERC-20 操作**：

`Transferable` trait 实现了完整的 ERC-20 转账语义：

- `transfer(from, to, amount, privileged)` — 暂停检查 → 策略检查（发送方 + 接收方） → 余额扣减/增加 → 发出 `Transfer` 事件
- `transfer_from(spender, from, to, amount, privileged)` — 暂停检查 → 授权额检查 → 执行方策略检查（`spender != from` 时） → 内部转账 → 授权额扣减（`U256::MAX` 为无限授权，不递减）
- `approve(owner, spender, amount)` — 零地址检查 → 设置授权额 → 发出 `Approval` 事件

**32 字节 Memo 扩展**：
- `transferWithMemo` / `transferFromWithMemo` / `mintWithMemo` / `burnWithMemo` — 在标准操作之后附加发出 `Memo(caller, memo)` 事件，其中 `memo` 为 32 字节 (`B256`)，可用于链下关联交易场景或备注信息

**EIP-2612 Permit**：

`Permittable` trait 实现了 EIP-2612 无 gas 授权：

- **域分隔符**（domain separator）：`(name, version, chainId, verifyingContract)` 四字段规范形式。`version` 固定为 `"1"`，`name` 从存储实时读取，因此 `updateName()` 会使未签出的 permit 签名失效
- **TYPEHASH**: `keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)")`
- **签名恢复**：`v` 值映射为 secp256k1 恢复奇偶性（`27 → even_y`，`28 → odd_y`），支持 ECDSA 恢复。不支持 ERC-1271 合约签名
- **Nonce 管理**：每个所有者维护单调递增的 nonce，防止签名重放
- **截止时间**：`deadline` 超时后 permit 失效（`ExpiredSignature` 错误）

**ERC-5267 eip712Domain()**：返回标准七元组 `(fields=0x0f, name, "1", chainId, verifyingContract, salt=0, extensions=[])`，其中 `fields` 位标志 `0x0f` 表示使用了 name + version + chainId + verifyingContract 四个字段。

> 源码引用: `crates/common/precompiles/src/common/ops/transferable.rs`, `crates/common/precompiles/src/common/ops/permittable.rs` @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 2.5 Pausable 与 Configurable 功能

**功能级暂停（Pausable）**：

B20 采用位掩码（bitmask）实现功能级暂停，三个独立可控的功能：

| 功能 | 枚举值 | 位掩码 |
|------|--------|-------|
| `TRANSFER` | 0 | `1 << 0` |
| `MINT` | 1 | `1 << 1` |
| `BURN` | 2 | `1 << 2` |

- `pause(features[])` — OR 运算添加暂停位，需要 `PAUSE_ROLE`
- `unpause(features[])` — AND NOT 运算清除暂停位，需要 `UNPAUSE_ROLE`
- `isPaused(feature)` — 查询单个功能的暂停状态
- `pausedFeatures()` — 返回所有已暂停功能列表

暂停操作是**幂等**的：重复暂停同一功能不会报错。空功能列表会触发 `EmptyFeatureSet` 错误。

**重要语义**：暂停检查由 `B20Guards::ensure_not_paused()` 执行，在所有能力 trait 方法中**始终是第一个检查**，即使 `privileged = true` 也不跳过（除了在内部方法 `transfer_inner`/`burn_inner` 中，因为外部方法已经执行了暂停检查）。

**可配置功能（Configurable）**：

| 方法 | 所需角色 | 语义 |
|------|---------|------|
| `updateSupplyCap(newCap)` | `DEFAULT_ADMIN_ROLE` | 拒绝 `newCap < totalSupply` |
| `updateName(name)` | `METADATA_ROLE` | 同时发出 `NameUpdated` + `EIP712DomainChanged`（使现有 permit 失效） |
| `updateSymbol(symbol)` | `METADATA_ROLE` | 发出 `SymbolUpdated` |
| `updateContractURI(uri)` | `METADATA_ROLE` | 发出 `ContractURIUpdated`（ERC-7572） |

> 源码引用: `crates/common/precompiles/src/common/ops/pausable.rs`, `crates/common/precompiles/src/common/ops/configurable.rs` @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

---

## 第三章 B20Factory

### 3.1 createB20 创建生命周期

B20Factory 是部署在固定地址 `0xB20F000000000000000000000000000000000000` 的单例预编译。`createB20` 方法执行一个完整的 **10 步创建流程**：

```
步骤 1: 解析变体判别符 → B20Variant 枚举
步骤 2: 检查激活状态 → ActivationRegistryStorage::ensure_activated()
步骤 3: 解码变体参数 → TokenCreateParams (Asset 或 Stablecoin)
步骤 4: 验证版本号 → check_version() (当前两种变体均为 v1)
步骤 5: 变体特定验证 → Asset: decimals ∈ [6, 18]; Stablecoin: currency A-Z
步骤 6: 计算确定性地址 → compute_address(caller, variant, salt)
步骤 7: 检查地址冲突 → 目标地址不得存在字节码
步骤 8: 部署桩字节码 → 写入 0xef 单字节（标记已部署）
步骤 9: 初始化变体 → init_asset_token() 或 init_stablecoin()
         → 写入核心存储 + 扩展存储
         → 授予初始管理员 DEFAULT_ADMIN_ROLE
         → 发出 B20Created 事件
步骤 10: 执行 initCalls → 以 Factory 地址 + privileged=true 逐一执行
          → 失败时原子回滚，错误包装为 InitCallFailed(index)
```

**变体参数结构**：

```solidity
// Asset 变体
struct B20AssetCreateParams {
    uint8 version;      // 当前固定为 1
    string name;
    string symbol;
    address initialAdmin;
    uint8 decimals;     // 范围 [6, 18]（MIN_DECIMALS=6, MAX_DECIMALS=18）
}

// Stablecoin 变体
struct B20StablecoinCreateParams {
    uint8 version;      // 当前固定为 1
    string name;
    string symbol;
    address initialAdmin;
    string currency;    // ISO 4217 风格，A-Z 大写
}
```

**供给上限默认值**：创建时默认设置为 `U256::MAX`（实质上无上限），可通过后续 `updateSupplyCap` 调整。

**initCalls 机制**：创建者可在创建交易中附带一系列初始化调用（如授予额外角色、铸造初始供给、设置策略等）。这些调用以 Factory 地址为调用者、`privileged = true` 执行，确保在初始化窗口内跳过角色检查。任一调用失败则整个创建事务回滚。

**B20Created 事件**：
```solidity
event B20Created(
    address indexed token,
    B20Variant indexed variant,
    string name,
    string symbol,
    uint8 decimals,
    bytes variantParams  // Asset: 空字节; Stablecoin: abi.encode(version, currency)
);
```

> 源码引用: `crates/common/precompiles/src/b20_factory/storage.rs` — `B20FactoryStorage::create_b20()` 方法 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)（注：`precompile.rs` 仅安装预编译结构体，`create_b20()` 实现位于 `storage.rs`）

### 3.2 确定性地址与变体识别

**地址查询**：`getB20Address(variant, sender, salt)` 是纯视图函数，计算并返回确定性地址而不执行任何写操作。该函数**永不回退**（never reverts）。

**三级识别体系**：

| 函数 | 语义 | 返回值 |
|------|------|--------|
| `isB20(token)` | 结构性前缀检查（`0xb2` + 9 零字节） | 包含保留判别符的地址也返回 true |
| `isB20Initialized(token)` | Factory 部署状态检查 | 仅已通过 Factory 创建的代币返回 true |
| `B20Variant::from_address(addr)` | 提取具体变体 | 仅 Asset (0x00) / Stablecoin (0x01) 有效 |

这种分层设计允许协议层快速筛选 B20 地址（`isB20`），然后在需要时验证部署状态（`isB20Initialized`）。

> 源码引用: `crates/common/precompiles/src/b20_factory/variant.rs` — `compute_address()`, `has_b20_prefix()`, `from_address()` @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 3.3 ActivationRegistry 集成

ActivationRegistry 是部署在 `0x8453000000000000000000000000000000000001` 的单例预编译，为 Beryl 硬分叉提供特性门控。

**特性 ID 推导**：

| 特性 | 字符串 | ID = keccak256(字符串) |
|------|--------|----------------------|
| PolicyRegistry | `"base.policy_registry"` | `keccak256("base.policy_registry")` |
| B20Asset | `"base.b20_asset"` | `keccak256("base.b20_asset")` |
| B20Stablecoin | `"base.b20_stablecoin"` | `keccak256("base.b20_stablecoin")` |

**生命周期**：`inactive`（默认） → `activate` → `deactivate`。幂等转换会回退（`AlreadyActivated` / `FeatureNotActivated`）。

**管理员门控**：`activate` 和 `deactivate` 仅管理员可调用（`admin` 参数传入时验证）。视图函数 `isActivated` / `checkActivated` 始终可访问。

**集成点**：
- **Factory 集成**：`create_b20()` 在步骤 2 调用 `ensure_activated(variant.activation_feature().id())` 门控代币创建
- **PolicyRegistry 集成**：写操作（createPolicy、updateAllowlist 等）在 dispatch 层检查 `ensure_activated(ActivationFeature::PolicyRegistry.id())`，视图操作绕过

> 源码引用: `crates/common/precompiles/src/activation/storage.rs`, `crates/common/precompiles/src/activation/abi.rs` @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

---

## 第四章 B20Asset 变体（远程 HEAD 主线）

### 4.1 乘数机制（Multiplier）

B20Asset 引入了读时缩放（read-time scaling）的乘数机制，核心思想是**存储原始余额，读取时动态缩放**，避免对所有账户余额进行存储重写。

**常量与公式**：
- `WAD_PRECISION = 1e18`（`0x0de0b6b3a7640000`）— 固定精度基准
- 缩放公式：`scaledBalance = rawBalance × multiplier / WAD`
- 反向公式：`rawBalance = scaledBalance × WAD / multiplier`

**函数接口**：

| 函数 | 说明 |
|------|------|
| `multiplier()` | 返回当前乘数（未初始化时默认为 WAD，即 1:1） |
| `toScaledBalance(raw)` | 原始余额 → 缩放余额 |
| `toRawBalance(scaled)` | 缩放余额 → 原始余额 |
| `scaledBalanceOf(account)` | 便捷包装：读取原始余额并应用缩放 |
| `updateMultiplier(newMultiplier)` | 更新乘数，需要 `OPERATOR_ROLE`，发出 `MultiplierUpdated` |

**设计意义**：乘数机制使 B20Asset 能够在不修改任何账户余额存储的情况下实现全局余额调整。典型用例包括股票分拆/合并、rebase 代币、以及需要根据外部因子调整面值的金融资产。由于缩放在读取时实时计算，存储操作仍然以原始余额为准，确保了存储一致性和 ZK 可证明性。

**初始乘数**：Factory 创建 Asset 代币时，乘数存储槽初始值为 `U256::ZERO`。`multiplier()` getter 在读取到零值时返回 `WAD`（1e18），实现默认 1:1 缩放。

> 源码引用: `crates/common/precompiles/src/b20_asset/token.rs` — `to_scaled_balance()`, `to_raw_balance()`, `update_multiplier()` @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)
> `crates/common/precompiles/src/b20_asset/storage.rs` — `WAD` 常量, `multiplier` 存储槽 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 4.2 批量铸造（batchMint）

`batchMint(recipients[], amounts[])` 实现了全量或零（all-or-nothing）的原子批量铸造：

**守卫顺序**：
1. **暂停检查** — `ensure_not_paused(MINT)` — 最高优先级
2. **角色检查** — `ensure_token_role(caller, MINT_ROLE)` — 调用者必须有铸造权限
3. **输入验证** — 数组长度匹配（`LengthMismatch`）；非空数组（`EmptyBatch`）
4. **业务逻辑** — 逐个接收者执行 `mint(caller, recipient, amount, privileged=true)`，跳过内部冗余角色检查

**原子性**：由于内部使用 `privileged = true` 跳过冗余角色检查，任一单笔铸造失败（如接收者零地址、供给上限超出）都会导致整个批次回滚。

**无批次上限**：代码层面未设置批次大小上限，实际受 gas 限制约束。

> 源码引用: `crates/common/precompiles/src/b20_asset/token.rs` — `batch_mint()` 实现 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 4.3 公告机制（Announcement）

B20Asset 的公告机制允许 `OPERATOR_ROLE` 持有者发布影响持有者的通知，并在同一交易中原子执行相关操作：

```
announce(internalCalls[], id, description, uri)
  │
  ├── OPERATOR_ROLE 检查
  ├── 重入守卫：检查 in_announcement 标志
  ├── 单次 ID 检查：is_announcement_id_used(id)
  ├── 标记 ID 已使用：mark_announcement_id_used(id)
  ├── 发出 Announcement(caller, id, description, uri) 事件
  ├── 设置 in_announcement = true
  ├── 逐一执行 internalCalls：
  │   ├── 长度 < 4 → InternalCallMalformed
  │   ├── 选择器 == announce → AnnouncementInProgress（防递归）
  │   └── inner_with_privilege(ctx, call) → 失败包装为 InternalCallFailed
  ├── 清除 in_announcement 标志
  └── 发出 EndAnnouncement(id) 事件
```

**安全特性**：
- **单次 ID**：每个公告 ID 只能使用一次，通过 `used_announcement_ids` mapping 追踪
- **重入防护**：`in_announcement` 布尔标志 + 选择器检查双重防护，阻止 `announce` 的递归调用
- **事件对**：`Announcement` / `EndAnnouncement` 事件对形成链上操作括号，方便索引器精确追踪公告生命周期
- **内部调用权限**：所有内部调用以 `privileged = true` 执行，即跳过角色检查但不跳过暂停检查

**典型使用场景**：代币管理者发布公告（如股息分配、合规更新），同时原子执行配套操作（如批量铸造、乘数更新）。

> 源码引用: `crates/common/precompiles/src/b20_asset/dispatch.rs` — `announce()` 处理器 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 4.4 扩展元数据与角色模型

**扩展元数据（extraMetadata）**：

B20Asset 提供任意键值对（KV）存储：

| 函数 | 说明 |
|------|------|
| `extraMetadata(key)` | 读取指定键的值 |
| `updateExtraMetadata(key, value)` | 写入键值对（`METADATA_ROLE` 必需） |

- 空键被拒绝：`InvalidMetadataKey` 错误
- 空值表示删除：写入空字符串等同于移除该键
- 发出 `ExtraMetadataUpdated(key, value)` 事件

**Asset 特有角色**：

| 角色 | 常量 | 功能 |
|------|------|------|
| `OPERATOR_ROLE` | `keccak256("OPERATOR_ROLE")` = `0x97667070...` | 公告(`announce`)、乘数更新(`updateMultiplier`) |
| `METADATA_ROLE` | `keccak256("METADATA_ROLE")` = `0x6bd6b531...` | 扩展元数据更新(`updateExtraMetadata`) |

**存储布局**：B20Asset 扩展存储使用 ERC-7201 命名空间 `base.b20.asset`（存储根：`0xfdc6d4552d1286ade4d9facdbf0fb50d2ec9b89a90e104f26fd277585e374b00`）：

| 槽位 | 字段 | 类型 |
|------|------|------|
| 0 | `decimals` | `u8` |
| 1 | `multiplier` | `U256` |
| 2 | `used_announcement_ids` | `Mapping<String, bool>` |
| 3 | `extra_metadata` | `Mapping<String, String>` |

**自定义精度**：Asset 变体支持 6–18 位小数精度（`MIN_DECIMALS = 6`，`MAX_DECIMALS = 18`），在创建时设置，默认为 6。

**证券标识符用例**：Beryl 测试文件 `security.rs` 创建了一个 `B20Variant::ASSET` 代币，并使用 `extraMetadata` 存储证券标识符（ISIN、CUSIP、FIGI），展示了 Asset 变体的 KV 元数据机制原生支持证券标识符工作流，无需单独的 B20Security 变体。该测试还在证券场景中演练了 `updateMultiplier`、`batchMint` 和 `announce` 功能。

> 源码引用: `crates/common/precompiles/src/b20_asset/storage.rs` — `B20AssetExtensionStorage`, `MIN_DECIMALS`/`MAX_DECIMALS` @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)
> `actions/harness/tests/beryl/security.rs` — B20Asset 证券标识符用例测试（导入 `IB20Asset`，创建 `B20Variant::ASSET`） @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

---

## 第五章 B20Security 演进信号（非主线）

> **版本声明**：本章内容基于本地分支观察（local branch observation），`b20_security/` 目录在远程 HEAD `8e8767281d7c8768f6a0aed9124779cd4ed030ae` 不存在。以下所有内容标记为"**演进信号（evolutionary signal），非当前 BASE 主线事实**"。

### 5.1 证券代币扩展

在本地分支的超前提交中观察到 `b20_security/` 模块，代表 B20 框架向证券代币（security token）方向的演进。与远程 HEAD 的 B20Asset 变体相比，新增了以下能力：

**新增角色**：
- `SECURITY_OPERATOR_ROLE` — 取代 Asset 的 `OPERATOR_ROLE`，专用于证券操作
- `BURN_FROM_ROLE` — 授权强制销毁（替代通用的 `BURN_ROLE`）

**新增策略范围**：
- `REDEEM_SENDER_POLICY` — 赎回操作的发送方策略检查

**核心新功能**：

| 功能 | 说明 |
|------|------|
| `sharesToTokensRatio` | 份额到代币的比率，替代 Asset 的 `multiplier` 概念 |
| `redeem` / `redeemWithMemo` | 持有者发起的赎回操作，带最低阈值检查 |
| `batchBurn` | 强制批量销毁/追回（clawback）能力 |
| `securityIdentifier` | 专用证券标识符字段（区别于远程 HEAD 中使用 `extraMetadata` KV 存储的 ISIN/CUSIP/FIGI——参见第四章 4.4 节） |

**与 B20Asset 的对比**：

| 维度 | B20Asset（远程 HEAD） | B20Security（本地分支） |
|------|----------------------|----------------------|
| 乘数 | `multiplier` + WAD 缩放 | `sharesToTokensRatio` |
| 证券标识 | `extraMetadata` KV 存储 | 专用 `securityIdentifier` 字段 |
| 赎回 | 无 | `redeem` / `redeemWithMemo` |
| 批量销毁 | 无 | `batchBurn`（追回） |
| 操作角色 | `OPERATOR_ROLE` | `SECURITY_OPERATOR_ROLE` |
| 销毁授权 | `BURN_ROLE` | `BURN_FROM_ROLE` |

**解读**：B20Security 本质上是 B20Asset 的证券专业化版本。远程 HEAD 的 `security.rs` 测试文件实际上测试的是 B20Asset 的证券用例（通过 `extraMetadata` 实现），而非 B20Security 变体。这表明 Base 团队在主线上先用 Asset 变体的通用 KV 机制验证证券工作流，再在实验分支上发展专用的 Security 变体。

> 注意：`actions/harness/tests/beryl/security.rs` 在远程 HEAD 并非 B20Security 测试——它导入 `IB20Asset` 并创建 `B20Variant::ASSET`（参见第四章 4.4 节）。
>
> 源码引用: `crates/common/precompiles/src/b20_security/`（**仅本地分支**，远程 HEAD `8e87672` 不存在此目录）

---

## 第六章 B20Stablecoin 变体

### 6.1 货币标识符扩展

B20Stablecoin 是 B20 框架中最精简的变体，在共享 IB20 层之上仅新增一个方法：

```solidity
function currency() external view returns (string memory);
```

**创建参数与验证**：

`B20StablecoinCreateParams` 包含 `currency` 字段，在初始化时经过严格验证：

1. **非空检查**：空字符串触发 `MissingRequiredField { field: "currency" }` 错误
2. **大写字母检查**：每个字节必须在 A-Z (0x41-0x5A) 范围内，否则触发 `InvalidCurrency { code }` 错误

这种验证确保货币代码符合 ISO 4217 风格（如 "USD"、"EUR"、"CNY"），但代码中未强制三字符限制，理论上允许任意长度的大写字母字符串。

**存储布局**：ERC-7201 命名空间 `base.b20.stablecoin`（存储根：`0x35827975a06ca0e9367ea3129b19441d45d0ca58e30b7693f09e73d0943d6200`），包含单个存储槽：

| 槽位 | 字段 | 类型 |
|------|------|------|
| 0 | `currency` | `String` |

**继承能力**：B20Stablecoin 继承共享 IB20 层的全部能力——转账、铸造、销毁、RBAC、暂停、配置、permit、策略绑定、memo 扩展。创建时默认精度为 6 位小数（与 Asset 变体一致）。

**B20Created 事件**：Stablecoin 创建时，`variantParams` 字段编码为 `abi.encode(B20StablecoinEventParams { version: 1, currency })`（Asset 变体此字段为空字节）。

**设计评价**：Stablecoin 变体的极简设计体现了 B20 框架的组合哲学——差异化功能通过变体扩展实现，共享功能由通用能力层提供，避免代码重复。

> 源码引用: `crates/common/precompiles/src/b20_stablecoin/abi.rs` — `IB20Stablecoin` 接口 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)
> `crates/common/precompiles/src/b20_stablecoin/storage.rs` — `B20StablecoinExtensionStorage`, 初始化验证 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

---

## 第七章 PolicyRegistry 合规机制

### 7.1 策略类型与内置策略

PolicyRegistry 是 B20 的核心合规引擎，部署在固定地址 `0x8453000000000000000000000000000000000002`。

**策略类型枚举**：

| 类型 | 判别符 | 语义 |
|------|--------|------|
| `BLOCKLIST` | 0 | 拒绝列表中的账户；空黑名单授权所有人 |
| `ALLOWLIST` | 1 | 仅允许列表中的账户；空白名单拒绝所有人 |

**策略 ID 编码**：

策略 ID 是 `u64` 类型，高字节（bits [63:56]）为类型判别符，低 56 位（bits [55:0]）为单调递增计数器：

```
[type_discriminant: 8 bits][counter: 56 bits]
```

**内置策略**：

| 策略 | ID | 类型 | 语义 |
|------|----|------|------|
| `ALWAYS_ALLOW` | `0x0000000000000000` | BLOCKLIST（判别符 0）+ 计数器 0 | 空黑名单 → 授权所有人 |
| `ALWAYS_BLOCK` | `0x0100000000000001` | ALLOWLIST（判别符 1）+ 计数器 1 | 空白名单 → 拒绝所有人 |

自定义策略从计数器 2 开始分配。常量 `COUNTER_MASK = (1u64 << 56) - 1 = 0x00FFFFFFFFFFFFFF`。

**存储布局**：ERC-7201 命名空间 `base.policy_registry`：

| 槽位 | 字段 | 类型 |
|------|------|------|
| 0 | `policies` | `Mapping<u64, U256>` |
| 1 | `members` | `Mapping<u64, Mapping<Address, bool>>` |
| 2 | `pending_admins` | `Mapping<u64, Address>` |
| 3 | `next_counter` | `u64` |

**PackedPolicy 结构**（U256）：
- Bit 255 = 存在标志（标记策略已创建）
- Bits [159:0] = 管理员地址（160 位）
- Bits [254:160] = 保留位（零值）

> 源码引用: `crates/common/precompiles/src/policy/storage.rs` — `PolicyRegistryStorage`, `PackedPolicy`, `ALWAYS_ALLOW_ID`/`ALWAYS_BLOCK_ID` @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 7.2 四维策略范围

B20 将策略检查细化为四个独立范围，每个代币可为每个范围绑定不同的策略 ID：

| 范围 | B256 标识 | 检查点 |
|------|----------|--------|
| `TransferSender` | `keccak256(...)` = `0xb81736...` | 转账的 `from` 地址 |
| `TransferReceiver` | `keccak256(...)` = `0x8a4b3f...` | 转账的 `to` 地址 |
| `TransferExecutor` | `keccak256(...)` = `0x10be51...` | `transferFrom` 的 `spender`（`spender == from` 时跳过） |
| `MintReceiver` | `keccak256(...)` = `0xa0d5ae...` | 铸造的 `to` 地址 |

**策略执行流程**（以 `transferFrom` 为例）：

```
transferFrom(spender, from, to, amount)
  │
  ├── ensure_not_paused(TRANSFER)
  ├── 零地址检查
  ├── 授权额检查
  ├── ensure_policy_type(TransferExecutor, spender)  ← spender ≠ from 时
  ├── transfer_inner(from, to, amount)
  │   ├── ensure_policy_type(TransferSender, from)    ← 非 privileged 时
  │   ├── ensure_policy_type(TransferReceiver, to)    ← 非 privileged 时
  │   └── 余额操作
  └── 授权额递减（非 U256::MAX 时）
```

**策略委托**：`B20Guards::ensure_policy_type()` → `B20Guards::ensure_policy()` → `token.policy().is_authorized(policy_id, account)`。策略检查完全委托给外部 PolicyRegistry 预编译。

**优雅降级**：对于从未创建的 BLOCKLIST 策略 ID，`is_authorized` 返回 `true`（因为空黑名单不阻止任何人）。这确保了未设置策略的代币默认允许所有操作。

> 源码引用: `crates/common/precompiles/src/common/policy_type.rs` — `B20PolicyType` 枚举 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)
> `crates/common/precompiles/src/common/ops/transferable.rs` — 转账策略检查 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 7.3 策略 CRUD 与管理员管理

**创建操作**：

| 函数 | 说明 |
|------|------|
| `createPolicy(admin, policyType)` | 创建策略，分配单调递增 ID，初始成员列表为空 |
| `createPolicyWithAccounts(admin, policyType, accounts[])` | 创建策略并初始化成员列表 |

**成员更新**：

| 函数 | 说明 |
|------|------|
| `updateAllowlist(policyId, allowed, accounts[])` | ALLOWLIST 专用，类型检查（BLOCKLIST 策略调用会回退） |
| `updateBlocklist(policyId, blocked, accounts[])` | BLOCKLIST 专用，类型检查（ALLOWLIST 策略调用会回退） |

批量上限：`MAX_ACCOUNTS_PER_BATCH = 64`。超出触发 `BatchSizeTooLarge` 错误。

**两步管理员转移**：

```
stageUpdateAdmin(policyId, newAdmin)  → 记录候选管理员
finalizeUpdateAdmin(policyId)         → 候选管理员调用确认，完成转移
```

这种两步设计防止管理员因误输入地址而永久丧失策略控制权。

**管理员放弃**：`renounceAdmin(policyId)` 将管理员设为零地址，**永久不可逆**，策略成为不可变。

**事件**：
- `PolicyCreated(policyId indexed, creator indexed, policyType)`
- `PolicyAdminStaged(policyId indexed, currentAdmin indexed, pendingAdmin indexed)`
- `PolicyAdminUpdated(policyId indexed, previousAdmin indexed, newAdmin indexed)`
- `AllowlistUpdated(policyId indexed, updater indexed, allowed, accounts[])`
- `BlocklistUpdated(policyId indexed, updater indexed, blocked, accounts[])`

> 源码引用: `crates/common/precompiles/src/policy/storage.rs` — CRUD 实现 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)
> `crates/common/precompiles/src/policy/dispatch.rs` — 激活门控 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 7.4 代币-策略集成

**存储绑定**：每个 B20 代币在核心存储中维护 4 个策略 ID（打包于槽 9-10），通过 `updatePolicy(scope, policyId)` 更新，需要 `DEFAULT_ADMIN_ROLE`。

**Policy trait 抽象**：

```rust
pub trait Policy {
    fn is_authorized(&self, policy_id: u64, account: Address) -> Result<bool>;
    fn policy_exists(&self, policy_id: u64) -> Result<bool>;
}
```

代币通过 `Token::policy()` 关联类型访问 PolicyRegistry，所有策略查询在编译期绑定到具体的 `PolicyRegistryStorage` 实现。

**burnBlocked 机制**：`burnBlocked(from, amount)` 要求目标账户被 TransferSender 策略阻止（`ensure_blocked` 验证 `is_authorized == false`）。这使得合规管理者能够销毁被冻结账户的代币，是 B20 合规能力的关键组成部分。

**授权语义总结**：

| 策略类型 | 成员在列表中 | 成员不在列表中 | 空列表 |
|---------|-------------|---------------|--------|
| BLOCKLIST | 被阻止 | 被授权 | 所有人被授权 |
| ALLOWLIST | 被授权 | 被阻止 | 所有人被阻止 |

> 源码引用: `crates/common/precompiles/src/common/policy.rs` — `Policy` trait @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)
> `crates/common/precompiles/src/common/ops/guards.rs` — `ensure_policy()`, `ensure_blocked()` @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

---

## 第八章 Beryl 硬分叉测试套件与 ZK 证明

### 8.1 测试套件架构

Beryl 测试套件位于 `actions/harness/tests/beryl/`，使用完整的 L2 测试环境。

**BerylTestEnv**：

核心测试环境结构体，包含：
- `sequencer: L2Sequencer` — L2 排序器
- `harness: ActionTestHarness` — 操作测试工具
- `batcher_cfg: BatcherConfig` — 批处理器配置
- `node: TestRollupNode<VerifierPipeline>` — Rollup 验证节点
- `chain: SharedL1Chain` — 共享 L1 链
- `bob_account: TestAccount` — 预配置测试账户

**关键常量**：
- `BERYL_ACTIVATION_TIMESTAMP = 4` — Beryl 硬分叉在 L2 时间戳 4 激活
- `B20_GAS_LIMIT = 10_000_000` — B20 交易 gas 限制
- `B20_PROBE_GAS_LIMIT = 1_000_000` — staticcall 探针 gas 限制
- 预配置代币：`B20_NAME = "Action B20"`, `B20_SYMBOL = "AB20"`, `B20_DECIMALS = 6`

**Staticcall 探针模式**：测试使用部署 EVM 字节码探针（probe）进行只读 ABI 验证。探针通过 staticcall 调用目标预编译，将返回值写入特定存储槽（`PROBE_CALL_SUCCESS_SLOT`、`PROBE_RETURN_WORD_SLOT`、`PROBE_RETURN_SIZE_SLOT`、`PROBE_RETURN_HASH_SLOT`），然后测试读取这些槽位验证 ABI 正确性。

**区块构建 + 推导验证模式**：测试先通过排序器构建包含 B20 交易的区块，然后通过 Rollup 节点执行推导验证（derivation verification），确保预编译行为在 L1 推导路径中的确定性。

> 源码引用: `actions/harness/tests/beryl/env.rs` — `BerylTestEnv` 结构体 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 8.2 测试覆盖摘要

测试套件包含 8 个测试模块、**33 个顶层 `#[tokio::test]` 函数**（部分测试包含多个子场景）：

| 模块 | 测试数 | 覆盖领域 |
|------|--------|---------|
| `activation.rs` | 1（含 10 子测试） | 特性生命周期：激活/停用/重复操作/未授权访问 |
| `factory.rs` | 4 | 创建、重复防护、停用后向兼容、视图/事件验证 |
| `b20.rs` | 8 | 转账、回退、授权、staticcall ABI、停用兼容、变更操作、permit |
| `b20_policy.rs` | 4 | 白名单/黑名单发送方/接收方策略执行 |
| `stablecoin.rs` | 4 | 货币初始化、继承操作、停用兼容、货币验证 |
| `security.rs` | 4 | 证券标识符（via extraMetadata）、变更操作、无效输入、停用兼容 |
| `policy_registry.rs` | 4 | 单例生命周期、策略 CRUD + 管理员转移 |
| `policy_transfer.rs` | 4 | 白名单/黑名单门控、内置策略行为 |

**值得注意的覆盖空白**：
- 无并发创建竞态测试
- 无大规模 `batchMint` 测试（仅小批量）
- 无缩放余额溢出边界测试
- 无 permit 到期边界条件测试

> 源码引用: `actions/harness/tests/beryl/` — 全部测试文件 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

### 8.3 ZK 证明基准

Beryl 包含一个 ZK 证明干运行基准（dry-run benchmark），位于 `etc/systems/benches/b20_zk_proving.rs`。

**工作负载配置**：
- 交易数量：`WORKLOAD_TXS = 10`
- 初始供给：`INITIAL_SUPPLY = 1_000_000`
- 测试操作序列：`transfer` → `transferWithMemo` → `approve` → `transferFrom` → `transferFromWithMemo` → `updateSupplyCap` → `grantRole` → `updateContractURI` → `updateName` → `updateSymbol`

**基准参数**：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `l2-rpc-url` | `http://localhost:8645` | L2 RPC 端点 |
| `rollup-rpc-url` | `http://localhost:8649` | Rollup RPC 端点 |
| `zk-prover-url` | `http://localhost:9000` | ZK 证明器端点 |
| `l2-chain-id` | `84538453` | L2 链 ID |
| `proof-timeout-secs` | `900` | 证明超时（15 分钟） |
| `proof-poll-interval-secs` | `5` | 证明轮询间隔 |

**度量指标**：每次操作的 gas 消耗、区块号、证明生成周期数（最小/最大/平均/总计）。

**意义**：该基准证明了 B20 预编译操作在 ZK 证明框架下的可证明性。作为预编译实现（而非 Solidity 合约），B20 操作的执行轨迹（execution trace）是固定和可预测的，这对 ZK 证明器的效率至关重要。基准中包含外部 ZK 证明器服务的集成，暗示 Base 正在为 B20 构建端到端的 ZK 可验证性。

> 源码引用: `etc/systems/benches/b20_zk_proving.rs` — ZK 基准 @ [`8e87672`](https://github.com/base/base/tree/8e8767281d7c8768f6a0aed9124779cd4ed030ae)

---

## 第九章 TIP-20 对比分析

### 9.1 共享模式

B20 和 TIP-20 作为两个 L2 的预编译代币标准，共享以下核心设计模式：

| 共享模式 | 说明 |
|---------|------|
| **预编译实现** | 均采用 EVM 预编译形式，代币逻辑固化在节点执行层，非 Solidity 合约 |
| **Factory 模式** | 均使用工厂模式创建代币，支持确定性地址推导 |
| **合规策略** | 均具备策略注册表/合规机制，支持地址级别的授权/阻止 |
| **RBAC** | 均实现基于角色的访问控制，具有角色层级 |
| **32 字节 Memo** | 均支持转账附带 32 字节 memo |
| **ERC-20 兼容** | 均保持与 ERC-20 标准的完整兼容 |

### 9.2 B20 独有能力

| 能力 | 说明 |
|------|------|
| **Asset 变体 + Multiplier** | 读时缩放乘数，支持全局余额调整而不重写存储 |
| **Stablecoin 变体** | 专用货币标识符，ISO 4217 风格验证 |
| **公告机制（Announcement）** | 持有者影响通知 + 原子内部调用，带重入防护和单次 ID |
| **扩展元数据（Extra Metadata）** | 任意 KV 存储，支持证券标识符等场景 |
| **ZK 证明支持** | 内置 ZK 证明基准基础设施 |
| **ActivationRegistry** | 硬分叉门控特性激活，支持渐进式功能启用 |
| **burnBlocked** | 合规驱动的被封锁账户代币销毁 |
| **ERC-7572 contractURI** | 链上合约元数据 URI |
| **批量铸造（batchMint）** | 全量或零原子批量铸造 |
| **终极管理员放弃** | `renounceLastAdmin` 不可逆冻结角色 |

### 9.3 TIP-20 独有能力

| 能力 | 说明 |
|------|------|
| **Payment Lanes** | 支付通道机制 |
| **Fee AMM** | 自动化做市商费率计算 |
| **奖励分配** | 内置奖励分配机制 |
| **TIP-403 独立规范** | 已有独立规范文档 |

> 注：TIP-20 的详细分析需交叉引用合规代币标准项目（WHI-177 评估框架）的分析结果。

### 9.4 架构差异

| 维度 | B20 | TIP-20 |
|------|-----|--------|
| **能力组合** | Rust trait 组合，7 个能力 trait + B20Guards 辅助结构体，编译期单态化 | 待对比 |
| **存储模型** | ERC-7201 命名空间存储，策略 ID 打包（2 个 U256 槽位承载 4 个 u64 策略 ID） | 待对比 |
| **策略模型** | 四维策略绑定（发送方/接收方/执行方/铸造接收方），外部 PolicyRegistry 预编译 | 待对比 |
| **变体系统** | 判别符驱动的变体枚举（`0xb2` 前缀 + 判别字节），地址结构编码变体类型 | 待对比 |
| **地址推导** | `keccak256(abi_encode(creator, salt))` 哈希尾部 + 结构化前缀 | 待对比 |
| **激活机制** | ActivationRegistry 硬分叉门控 | 待对比 |

---

## 图表

### 图 1: B20 模块架构

```
┌─────────────────────────────────────────────────────┐
│                 ActivationRegistry                   │
│          0x8453...0001 (单例预编译)                   │
│  ┌───────────┬──────────────┬──────────────────┐    │
│  │PolicyReg  │  B20Asset    │  B20Stablecoin   │    │
│  │ 特性      │  特性        │  特性             │    │
│  └─────┬─────┴──────┬───────┴────────┬─────────┘    │
└────────│────────────│────────────────│───────────────┘
         │            │                │
         │ 门控       │ 门控           │ 门控
         ▼            ▼                ▼
┌────────────┐  ┌──────────────────────────────┐
│PolicyRegistry│  │        B20Factory            │
│0x8453...0002│  │   0xB20F...0000 (单例)       │
│             │  │                              │
│ 黑名单/白名单│  │  createB20() → 确定性地址     │
│ CRUD        │  │  initCalls → 原子初始化       │
│             │  └──────┬──────────┬────────────┘
│             │         │          │
│    ◄────────┼─ 策略查询 │          │ 初始化
│             │         ▼          ▼
│             │  ┌──────────┐ ┌──────────────┐
│             │  │B20Asset  │ │B20Stablecoin │
│             │  │Token     │ │Token         │
│             │  │          │ │              │
│             │  │ 乘数     │ │ 货币标识     │
│             │  │ 批量铸造 │ │              │
│             │  │ 公告     │ │              │
│             │  │ 扩展元数据│ │              │
│             │  └────┬─────┘ └──────┬───────┘
│             │       │              │
│             │       └──────┬───────┘
│             │              │
│             │              ▼
│             │  ┌────────────────────────┐
│             │  │  共享 IB20 能力层       │
│             │  │                        │
│             │  │ Transferable ─ 转账     │
│             │  │ Mintable ─── 铸造       │
│             │  │ Burnable ─── 销毁       │
│             │  │ RoleManaged ─ RBAC      │
│             │  │ Pausable ─── 暂停       │
│             │  │ Configurable  配置      │
│             │  │ Permittable ─ Permit    │
│             │  │                        │
│             │  │ B20Guards (辅助结构体)   │
│    ◄────────┼──│ TokenAccounting (端口)  │
│  策略查询   │  │ B20CoreStorage (存储)   │
│             │  └────────────────────────┘
└─────────────┘
```

### 图 2: 能力 Trait 组合

```
                    ┌─────────────┐
                    │  Token      │
                    │  trait      │
                    │             │
                    │ Accounting  │◄─── type Accounting: TokenAccounting
                    │ Policy      │◄─── type Policy: Policy
                    │ token_addr  │
                    └──────┬──────┘
                           │
         ┌────────┬────────┼────────┬────────┬──────────┬──────────┐
         ▼        ▼        ▼        ▼        ▼          ▼          ▼
   ┌──────────┬────────┬────────┬────────┬────────┬───────────┬──────────┐
   │Transfer- │Mintable│Burnable│Role-   │Pausable│Config-    │Permit-   │
   │able      │        │        │Managed │        │urable     │table     │
   │          │        │        │        │        │           │          │
   │transfer  │mint    │burn    │grant   │pause   │updateCap  │permit    │
   │approve   │mint_   │burn_   │revoke  │unpause │updateName │domain_   │
   │transfer_ │with_   │blocked │renounce│is_     │updateSym  │separator │
   │from      │memo    │burn_   │last_   │paused  │updateURI  │eip712_   │
   │memo 变体  │        │with_   │admin   │        │           │domain    │
   │          │        │memo    │        │        │           │          │
   └──────────┴────────┴────────┴────────┴────────┴───────────┴──────────┘
         │                                                          │
         │   B20Guards (辅助结构体，非 trait)                         │
         │   ┌────────────────────────────────────────────────┐     │
         ├──►│ ensure_not_paused  ensure_role  ensure_policy  │◄────┘
         │   │ ensure_token_role  ensure_blocked               │
         │   └────────────────────────────────────────────────┘
         │
         ▼
   ┌───────────────────────┐    ┌───────────────────────┐
   │ B20AssetToken          │    │ B20StablecoinToken     │
   │ impl all 7 traits      │    │ impl all 7 traits      │
   │                        │    │                        │
   │ + OPERATOR_ROLE         │    │ + currency()           │
   │ + multiplier/scaling    │    │                        │
   │ + batchMint             │    │                        │
   │ + announce              │    │                        │
   │ + extraMetadata         │    │                        │
   └───────────────────────┘    └───────────────────────┘
```

### 图 3: 代币创建流程

```
  调用者                  B20Factory                 ActivationRegistry      代币地址
    │                        │                            │                    │
    │  createB20(variant,    │                            │                    │
    │    salt, params,       │                            │                    │
    │    initCalls)          │                            │                    │
    │───────────────────────►│                            │                    │
    │                        │  ensure_activated(feature) │                    │
    │                        │───────────────────────────►│                    │
    │                        │◄───────────────────────────│                    │
    │                        │                            │                    │
    │                        │  decode TokenCreateParams  │                    │
    │                        │  check_version(v1)         │                    │
    │                        │  validate(params)          │                    │
    │                        │                            │                    │
    │                        │  compute_address(caller,   │                    │
    │                        │    variant, salt)          │                    │
    │                        │  check no bytecode exists  │                    │
    │                        │                            │                    │
    │                        │  deploy 0xef stub ─────────┼───────────────────►│
    │                        │                            │                    │
    │                        │  init_{variant}():         │                    │
    │                        │    write core storage      │                    │
    │                        │    write extension storage  │                    │
    │                        │    grant DEFAULT_ADMIN      │                    │
    │                        │    emit B20Created          │                    │
    │                        │                            │                    │
    │                        │  for each initCall:        │                    │
    │                        │    execute(privileged=true) ├───────────────────►│
    │                        │                            │                    │
    │◄───────────────────────│  return token address      │                    │
    │                        │                            │                    │
```

### 图 4: 策略执行流程

```
         transfer / transferFrom 调用
                    │
                    ▼
          ┌─────────────────┐
          │ 暂停检查         │ ── ContractPaused(TRANSFER)
          │ ensure_not_paused│
          └────────┬────────┘
                   │ 通过
                   ▼
          ┌─────────────────┐
          │ 发送方策略检查    │ ── PolicyForbids(TRANSFER_SENDER, id)
          │ TransferSender   │
          │ 查询 PolicyReg   │
          └────────┬────────┘
                   │ 授权
                   ▼
          ┌─────────────────┐
          │ 接收方策略检查    │ ── PolicyForbids(TRANSFER_RECEIVER, id)
          │ TransferReceiver │
          │ 查询 PolicyReg   │
          └────────┬────────┘
                   │ 授权
                   ▼
          ┌─────────────────┐
          │ 执行方策略检查    │ ── PolicyForbids(TRANSFER_EXECUTOR, id)
          │ TransferExecutor │  (仅 transferFrom 且 spender ≠ from)
          │ 查询 PolicyReg   │
          └────────┬────────┘
                   │ 授权
                   ▼
          ┌─────────────────┐
          │ 授权额检查       │ ── InsufficientAllowance
          │ (transferFrom)  │  (U256::MAX 跳过递减)
          └────────┬────────┘
                   │ 通过
                   ▼
          ┌─────────────────┐
          │ 余额检查与更新    │ ── InsufficientBalance
          │ from -= amount   │
          │ to += amount     │
          └────────┬────────┘
                   │ 成功
                   ▼
          ┌─────────────────┐
          │ 发出 Transfer    │
          │ (+ Memo 事件)    │
          └─────────────────┘
```

### 图 5: B20 vs TIP-20 特性矩阵

| 特性 | B20 | TIP-20 |
|------|:---:|:------:|
| 预编译实现 | ✅ | ✅ |
| Factory 确定性地址 | ✅ | ✅ |
| ERC-20 兼容 | ✅ | ✅ |
| RBAC 角色管理 | ✅ (7 角色) | ✅ |
| 策略注册表（合规） | ✅ (4 维) | ✅ |
| 32 字节 Memo | ✅ | ✅ |
| 功能级暂停 | ✅ (3 功能) | — |
| 变体系统（Asset/Stablecoin） | ✅ | — |
| 乘数缩放 | ✅ | — |
| 公告机制 | ✅ | — |
| 扩展元数据 KV | ✅ | — |
| 批量铸造 | ✅ | — |
| burnBlocked | ✅ | — |
| ZK 证明基准 | ✅ | — |
| ERC-7572 contractURI | ✅ | — |
| ActivationRegistry | ✅ | — |
| Payment Lanes | — | ✅ |
| Fee AMM | — | ✅ |
| 奖励分配 | — | ✅ |
| TIP-403 独立规范 | — | ✅ |
| EIP-2612 Permit | ✅ | — |
| ERC-5267 eip712Domain | ✅ | — |
| 终极管理员放弃 | ✅ | — |

---

## 源码覆盖

### 主要源码（代码）

所有代码引用均指向 `base/base` @ commit `8e8767281d7c8768f6a0aed9124779cd4ed030ae`，除非明确标注为本地分支观察。

| 模块 | 路径 | 覆盖文件 | 覆盖状态 |
|------|------|---------|---------|
| Shared IB20 | `crates/common/precompiles/src/common/` | abi.rs, core_storage.rs, token.rs, token_accounting.rs, policy.rs, policy_type.rs, pausable_feature.rs, ops/*.rs | ✅ 完整覆盖 |
| Factory | `crates/common/precompiles/src/b20_factory/` | abi.rs, precompile.rs, storage.rs, variant.rs, dispatch.rs | ✅ 完整覆盖 |
| Asset | `crates/common/precompiles/src/b20_asset/` | abi.rs, token.rs, storage.rs, accounting.rs, dispatch.rs, precompile.rs | ✅ 完整覆盖 |
| Stablecoin | `crates/common/precompiles/src/b20_stablecoin/` | abi.rs, token.rs, storage.rs, accounting.rs | ✅ 完整覆盖 |
| Policy | `crates/common/precompiles/src/policy/` | abi.rs, storage.rs, handle.rs, dispatch.rs | ✅ 完整覆盖 |
| Activation | `crates/common/precompiles/src/activation/` | abi.rs, storage.rs, precompile.rs | ✅ 完整覆盖 |
| Beryl Tests | `actions/harness/tests/beryl/` | 全部 8 个模块 + env.rs + test_helpers.rs + main.rs | ✅ 完整覆盖 |
| ZK Bench | `etc/systems/benches/` | b20_zk_proving.rs | ✅ 完整覆盖 |

### 次要源码

| 源码 | 覆盖状态 |
|------|---------|
| ERC/EIP 标准 (ERC-20, EIP-2612, ERC-5267, ERC-7201, ERC-7572) | ✅ 引用覆盖 |
| `base/docs` 仓库 | ⚠️ 未检查（无公开 B20/Beryl 文档） |
| TIP-20 分析 (WHI-177 评估框架) | ⚠️ 部分覆盖（待交叉引用） |

---

## 缺口分析

| 缺口 | 类型 | 影响 | 说明 |
|------|------|------|------|
| 无正式 B20 规范文档 | 源码缺口 | 中 | 所有结论基于代码实现推导，待 Base 发布正式规范后可能存在偏差 |
| B20Security 仅本地分支可观察 | 访问限制 | 低 | 第五章内容完整性依赖本地分支状态，无法在远程 HEAD 验证 |
| TIP-20 对比不完整 | 交叉引用缺口 | 中 | 第九章的 TIP-20 列标记为"待对比"，需交叉引用 WHI-177 评估框架 |
| `base/docs` 未检查 | 源码缺口 | 低 | 可能存在未公开的 Beryl 文档或 B20 设计文档 |
| ZK 基准无运行数据 | 数据缺口 | 低 | 基准代码已分析但无实际运行指标（需实际环境执行） |
| 无并发创建竞态测试覆盖 | 测试覆盖缺口 | 低 | 已在覆盖空白中记录 |

---

## 修订日志

| 版本 | 日期 | 修改 |
|------|------|------|
| Round 1 | 2026-06-04 | 初始草稿，覆盖大纲全部 9 个章节 |
| Round 2 | 2026-06-04 | 修订：[Major] 修正 IB20 ABI 清单计数（函数 44→50，事件 17→16，错误 19→22）；修正 PolicyUpdated 事件签名（移除不存在的 updater 参数）；完整列出全部 22 个错误类型。[Major] 修正 Asset decimals 范围 [0,18]→[6,18]，与 MIN_DECIMALS=6 对齐。[Minor] 修正 create_b20() 源码引用 precompile.rs→storage.rs。 |
