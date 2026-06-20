# Beryl Precompile 基础设施与 EVM 集成分析

## Metadata

| Field | Value |
|-------|-------|
| topic | Beryl Precompile 基础设施与 EVM 集成分析 |
| project_slug | `base-beryl-vs-azul` |
| topic_slug | `beryl-precompile-infra` |
| multica_issue_id | `fb7245dd-682d-445f-b9cd-96c5708e4505` |
| round | 1 |
| status | draft |
| github_repo | `Whisker17/multica-research` |
| artifact_paths.outline | `base-beryl-vs-azul/outlines/beryl-precompile-infra.md` |
| artifact_paths.draft | `base-beryl-vs-azul/research-sections/beryl-precompile-infra/drafts/round-1.md` |
| artifact_paths.final | `base-beryl-vs-azul/research-sections/beryl-precompile-infra/final.md` |

## Draft Metadata

| Field | Value |
|-------|-------|
| draft_round | 1 |
| outline_commit | `9b44e5dcea6b843ae62b353fd06898fb9c419bd3` |
| code_baseline | Mainnet v1.1.1 (`01e732cdbae0c624d652da9e608d7d3fe0f9c74b`), Sepolia v1.1.0 (`a3c3011b16dae73aaea455ec0a5ff614e65b7d0a`) |
| local_codebase | `/Users/whisker/Work/src/networks/base/base` |

---

## Executive Summary

Beryl 的 precompile 基础设施采用「附加 + fork 门控」架构：**静态 precompile 集合与 Azul 完全相同**（`beryl()` 直接返回 `azul()`），Beryl 的新增内容全部通过动态安装（`install_with_observer()` 中 `>= BaseUpgrade::Beryl` 门控）引入 4 个 Beryl-native precompiles（B20Factory、BerylLookup、PolicyRegistryPrecompile、ActivationRegistry）。

支撑这一架构的工程基础设施包括：(1) `#[contract]` / `#[precompile]` 宏系统提供类 Solidity 存储布局的编译期代码生成；(2) `PrecompileStorageProvider` trait 体系提供完整的 EIP-2200/2929/3529 gas 语义实现，附带 checkpoint/commit/revert 原子性保证和 slot 算术 `checked_add` 溢出防护；(3) 11 个 metrics family 的可观测性体系通过 `PrecompileCallObserver` trait 与 precompile 执行解耦。

**Blast radius 结论**：Beryl precompiles 对既有交易状态转移的影响面为**零**，由四层隔离机制保证——fork 时间戳门控、`>= Beryl` 安装门控、B20 地址空间编码隔离、存储地址隔离。

---

## §1 Native Precompile 框架

### 1.1 宏系统架构

Beryl 的 native precompile 框架基于三个核心 proc macro，定义于 `crates/common/precompile-macros/src/lib.rs` @ v1.1.1 (`01e732cd`)：

| 宏 | 类型 | 入口 | 功能 |
|---|---|---|---|
| `#[contract(addr = "0x...")]` | `proc_macro_attribute` | `lib.rs:24-28` | 解析存储结构体，生成 slot 分配、`ContractStorage` impl、构造函数 |
| `#[precompile]` | `proc_macro_attribute` | `lib.rs:44-47` | 生成 precompile singleton `install()` 方法和 `precompile()` dispatcher |
| `#[derive(Storable)]` | `proc_macro_derive` | `lib.rs:50-56` | 生成 `StorableType` / `Storable` trait impl，含 slot 布局常量 |

辅助宏包括 `#[namespace]`（ERC-7201 命名空间，`lib.rs:34-37`）、`#[derive(TokenAccounting)]`/`#[derive(AssetAccounting)]`/`#[derive(StablecoinAccounting)]` 等会计 derive 宏。

### 1.2 代码生成流程

完整展开路径：

```
Source struct (annotated with #[contract])
  → syn::DeriveInput (AST 解析)
  → ContractConfig (地址解析, contract.rs:15-40)
  → Vec<FieldInfo> (字段解析 + 保留名检查, contract.rs:82-129)
  → packing::allocate_slots_from() (slot bin-packing, packing.rs:80-110)
  → Vec<LayoutField> (slot 分配结果)
  → layout::gen_struct() + gen_constructor() + gen_slots_module() + gen_contract_storage_impl()
  → 最终 TokenStream (transformed struct + slots module + ContractStorage impl)
```

**关键数据结构**：

- `ContractConfig`（`contract.rs:15-17`）：仅解析 `addr = "0x..."` 参数，其他 ident 均报错（`contract.rs:27-32`）
- `FieldInfo`（`contract.rs:44-51`）：`{ name, ty, slot, base_slot, namespace }` — 每个字段的存储元数据
- `FieldKind`（`contract.rs:53-57`）：`Direct(&Type)` 或 `Mapping { key, value }` — 字段类型分类
- `LayoutField`（`packing.rs:66-73`）：`{ name, ty, kind, assigned_slot }` — slot 分配后的最终布局

### 1.3 地址别名拒绝与保留名

**两个不同的保护机制分别在两个文件中实现**（按 outline review 修正要求明确区分）：

| 保护规则 | 实施文件 | 行号 | 机制 |
|---------|---------|------|------|
| 保留存储字段名 (`address`, `storage`, `msg_sender`) | `contract.rs` | L42, L112-117 | `parse_fields()` 中检查 `RESERVED` 常量数组，命中则编译报错 `"Field name '{name}' is reserved"` |
| `install(address = X)` 别名拒绝 | `precompile.rs` | L186-192 | `InstallConfig::parse()` 仅接受 `addr` 作为键名；`address` 或其他键产生带提示的诊断信息 |
| `#[contract(addr = ...)]` 未知参数拒绝 | `contract.rs` | L26-32 | `ContractConfig::parse()` 仅接受 `"addr"` |

**测试验证**：`precompile.rs:269-278` 的 `install_config_rejects_address_alias_with_helpful_diagnostic` 测试确认 `install(address = X)` 被拒绝并产生指向 `addr` 的诊断提示。

### 1.4 Slot Bin-Packing 规则

Packing 逻辑实现于 `packing.rs:307-343` 的 `gen_slot_packing_logic()`：

1. **32 字节边界**：相邻字段仅在 `prev_offset + prev_bytes + curr_bytes <= 32` 时共享 slot（`packing.rs:321-325`）
2. **左对齐字节分配**：字段在 slot 内从 byte 0 开始累积偏移（`packing.rs:339`）
3. **溢出换 slot**：超过 32 字节时，新字段从下一 slot 的 offset 0 开始（`packing.rs:327-335`）
4. **手动 slot 覆盖**：`#[slot(N)]` 指定显式 slot，不参与自动 packing，使用 `LayoutCtx::FULL`（`packing.rs:129-137, 346-364`）
5. **ERC-7201 命名空间隔离**：每个 `#[namespace("id")]` 字段获得独立 root slot（`packing.rs:97-99`），命名空间根计算为 `keccak256(keccak256(id) - 1) & (MAX - 0xFF)`（`utils.rs:61-68`），低字节掩零，符合 ERC-7201 规范
6. **调试期碰撞检测**：`packing.rs:368-436` 生成 `#[cfg(debug_assertions)]` 碰撞检查函数，`layout.rs:177` 在构造时调用

**Solidity 兼容性**：packing 模拟 Solidity 存储布局的 32 字节 slot 边界和 bin-packing 行为。`LayoutCtx::packed(offset_bytes)` 机制在运行时处理 256-bit word 内的右对齐读写。

---

## §2 Precompile-Storage Provider（重点）

### 2.1 Trait 层次结构

存储抽象体系的核心是 `PrecompileStorageProvider` trait（`crates/common/precompile-storage/src/provider.rs:19-106` @ v1.1.1）。完整方法签名：

| 类别 | 方法 | 签名 | 行号 |
|------|------|------|------|
| 环境读取 | `chain_id` | `fn chain_id(&self) -> u64` | L21 |
| | `timestamp` | `fn timestamp(&self) -> U256` | L23 |
| | `beneficiary` | `fn beneficiary(&self) -> Address` | L25 |
| | `block_number` | `fn block_number(&self) -> u64` | L27 |
| 存储操作 | `sload` | `fn sload(&mut self, address: Address, key: U256) -> Result<U256>` | L40 |
| | `sstore` | `fn sstore(&mut self, address: Address, key: U256, value: U256) -> Result<()>` | L44 |
| | `tload` | `fn tload(&mut self, address: Address, key: U256) -> Result<U256>` | L42 |
| | `tstore` | `fn tstore(&mut self, address: Address, key: U256, value: U256) -> Result<()>` | L46 |
| 账户操作 | `set_code` | `fn set_code(&mut self, address: Address, code: Bytecode) -> Result<()>` | L30 |
| | `with_account_info` | `fn with_account_info(&mut self, address: Address, f: ...) -> Result<()>` | L33-37 |
| | `emit_event` | `fn emit_event(&mut self, address: Address, event: LogData) -> Result<()>` | L49 |
| Gas 管理 | `deduct_gas` | `fn deduct_gas(&mut self, gas: u64) -> Result<()>` | L52 |
| | `deduct_state_gas` | `fn deduct_state_gas(&mut self, gas: u64) -> Result<()>` | L56-58 |
| | `refund_gas` | `fn refund_gas(&mut self, gas: i64)` | L60 |
| | `gas_limit` / `gas_used` / `gas_refunded` | 查询方法 | L62-70 |
| | `state_gas_used` | `fn state_gas_used(&self) -> u64` | L66-68 |
| | `reservoir` | `fn reservoir(&self) -> u64` | L72-75 |
| 调用上下文 | `is_static` | `fn is_static(&self) -> bool` | L78 |
| | `call_value` | `fn call_value(&self) -> U256` | L81 |
| | `caller` / `replace_caller` | 调用者管理 | L84-86 |
| 原子性 | `checkpoint` | `fn checkpoint(&mut self) -> JournalCheckpoint` | L89 |
| | `checkpoint_commit` | `fn checkpoint_commit(&mut self)` | L91 |
| | `checkpoint_revert` | `fn checkpoint_revert(&mut self, checkpoint: JournalCheckpoint)` | L93 |
| 工具 | `metered_keccak256` | `fn metered_keccak256(&mut self, data: &[u8]) -> Result<B256>` | L96-105 |

**关联 trait 层次**：

- `StorageOps`（`provider.rs:111-116`）：per-address 的 `store()` / `load()` 抽象
- `ContractStorage<'a>`（`provider.rs:121-131`）：`#[contract]` 宏生成的 trait，提供 `address()` 和 `storage()` 访问器
- `StorableType`（`provider.rs:198-226`）：编译期布局信息 + Handler 工厂
- `Handler<T>`（`provider.rs:229-242`）：六操作接口 — `read`, `write`, `delete`, `t_read`, `t_write`, `t_delete`
- `FromWord`（`provider.rs:280-287`）：word 级编解码（primitive types）
- `StorageKey`（`provider.rs:318-343`）：mapping key 编码，`mapping_slot()` 使用 `keccak256(lpad32(key) || slot_be32)`

### 2.2 EvmPrecompileStorageProvider 生产实现

`EvmPrecompileStorageProvider<'a>`（`crates/common/precompile-storage/src/evm.rs:31-43` @ v1.1.1）是 `PrecompileStorageProvider` 的唯一生产实现。核心字段：

- `internals: &'a mut dyn EvmInternals` — EVM journal 访问
- `gas: Gas` — gas 计数器
- `gas_params: GasParams` — EIP-specific gas 参数
- `is_static: bool` — 静态调用标记
- `state_gas_used: u64` — EIP-8037 state gas 独立计数

### 2.3 EIP-2200: Gas-Stipend 守卫

**实现位置**：`evm.rs:195-201` @ v1.1.1

```rust
// L199
if self.gas.remaining() <= self.gas_params.call_stipend() {
    return Err(BasePrecompileError::OutOfGas);
}
```

**语义**：EIP-2200 规定 SSTORE 在剩余 gas ≤ call stipend（2300）时必须失败。此守卫保证 Solidity `.transfer()` 的安全假设——2300 gas 转发时接收者无法执行状态变更 SSTORE。

**测试验证**：`evm.rs:360-367` 的 `eip_2200_stipend_guard_constant_is_2300` 确认 `call_stipend() == 2300`。

### 2.4 EIP-2929: 冷/热存储访问计价

**SLOAD 路径**（`evm.rs:158-183`）：

1. 始终收取 `warm_storage_read_cost()`（100 gas）— L167
2. 若 `s.is_cold`，额外收取 `cold_storage_additional_cost()`（2500 gas，总计 2600 gas）— L169-170

**SSTORE 路径**（`evm.rs:190-226`）：

1. 收取 `sstore_static_gas()` — warm 基础费用 — L210
2. 收取 `sstore_dynamic_gas(true, &s.data, s.is_cold)` — 冷罚金 + EIP-2200 net-metering — L212

**Account 访问**（`evm.rs:133-156`）：

1. 收取 `warm_storage_read_cost()`（100 gas）— L148
2. 若 cold，收取 `cold_account_additional_cost()`（2500 gas）— L150-151

### 2.5 EIP-3529: Net-Metering Refund 传播

**实现位置**：`evm.rs:214` @ v1.1.1

```rust
self.refund_gas(self.gas_params.sstore_refund(true, &s.data));
```

Refund 由 `GasParams::sstore_refund()` 计算，通过 `gas.record_refund()` 传播到 gas 计数器。EIP-3529 的 `gas_used / 5` 上限在交易级别由 revm 的 frame handler 应用（`storage_ctx.rs:204` 注释确认），不在 precompile 层处理。

### 2.6 Checkpoint/Commit/Revert 原子性

**模式**：每个可能失败的存储操作（sload、sstore）被 checkpoint guard 包裹：

```
checkpoint = self.internals.checkpoint();
result = (|| {
    // 执行存储操作 + gas 扣除
    // 若 OOG → 返回 Err
})();
match result {
    Ok(_)  → checkpoint_commit()   // 提交 journal 变更
    Err(_) → checkpoint_revert()   // 回滚 journal 变更
}
```

**SLOAD checkpoint**（`evm.rs:159-183`）：确保 OOG 时不泄露 warm 状态。测试 `sload_oog_does_not_warm_slot()`（`evm.rs:431-479`）验证此属性。

**SSTORE checkpoint**（`evm.rs:202-226`）：确保 OOG 时不持久化存储变更。测试 `sstore_oog_reverts_local_journal_mutation()`（`evm.rs:370-421`）验证此属性。

**RAII 辅助**：`StorageCtx` 还提供 `CheckpointGuard`（`storage_ctx.rs:282-312`），其 `Drop::drop()` 在未 commit 时自动 revert，支持 panic 安全。

**tload/tstore 例外**：瞬时存储操作**不使用** checkpoint guard — `tload` 仅收取 `warm_storage_read_cost()`（`evm.rs:186`），`tstore` 收取相同费用后直接调用 `internals.tstore()`（`evm.rs:232-233`）。这是因为瞬时存储的 journal 变更不影响持久状态。

### 2.7 Slot 算术 checked_add 迁移（BOP-356/380）

**核心防护**（`crates/common/precompile-storage/src/types/slot.rs:44-58, 63-82` @ v1.1.1）：

`Slot::new_at_offset()`：
```rust
// slot.rs:51-53
slot: base_slot
    .checked_add(U256::from_limbs([offset_slots as u64, 0, 0, 0]))
    .ok_or(BasePrecompileError::SlotOverflow)?,
```

`Slot::new_at_loc()`：
```rust
// slot.rs:74-76
slot: base_slot
    .checked_add(U256::from_limbs([loc.offset_slots as u64, 0, 0, 0]))
    .ok_or(BasePrecompileError::SlotOverflow)?,
```

**Additive slot 路径覆盖面**（所有均使用 `checked_add` + `SlotOverflow` 错误传播）：

| 类型 | 文件 | checked_add 位置数 |
|------|------|-------------------|
| `Slot` | `types/slot.rs` | 2（`new_at_offset` L51-53, `new_at_loc` L74-76） |
| `Vec` | `types/vec.rs` | ≥8（delete, try_compute_handler, truncate, load/store packed/unpacked） |
| `Array` | `types/array.rs` | 2（`try_compute_handler` packed L94-96, unpacked L101-103） |
| `Set` | `types/set.rs` | 1（`Storable::delete` L138-139） |
| `Bytes`/`String` | `types/bytes_like.rs` | 3（load L197-198, store L223-224, delete L248） |

**Mapping 的 hashed slot 推导**（`types/mapping.rs` @ v1.1.1）：

`MappingHandler<'a, K, V>` 使用 `key.mapping_slot(base_slot)` 推导存储 slot，该方法（`provider.rs:332-342`）计算 `keccak256(lpad32(key) || slot_be32)` — 纯哈希推导，**无加法运算**，因此不存在溢出风险，不在 `checked_add` 审计范围内。

### 2.8 非规范 Bool 值拒绝

**实现位置**：`crates/common/precompile-storage/src/types/primitives.rs:39-52` @ v1.1.1

```rust
fn from_word(word: U256) -> Result<Self> {
    match word {
        w if w == U256::ZERO => Ok(false),
        w if w == U256::ONE  => Ok(true),
        _ => Err(BasePrecompileError::enum_conversion_error()),
    }
}
```

仅接受 `U256::ZERO`（false）和 `U256::ONE`（true），其他值（2、0xff、U256::MAX 等）均被拒绝。测试 `bool_from_word_rejects_noncanonical`（`primitives.rs:132-139`）验证此行为。

**安全意义**：防止 EVM dirty word 攻击 — 攻击者无法通过在 storage slot 中写入非 0/1 值来绕过 bool 条件判断。

### 2.9 set_code 中的 EIP-8037 State Gas 计费

**实现位置**：`evm.rs:91-131` @ v1.1.1

Gas 分层收费：

| 步骤 | Gas 类型 | 条件 | 行号 |
|------|----------|------|------|
| `code_deposit_cost(code_len)` | Regular | 始终 | L99 |
| `create_cost()` | Regular | `has_empty_code` | L112 |
| Keccak256 of code | Regular | `has_empty_code` | L114-115 |
| `create_state_gas()` | **State** | `is_new_account` | L119 |
| `code_deposit_state_gas(code_len)` | **State** | `has_empty_code` | L125 |

**State gas 与 regular gas 的关系**（`evm.rs:255-259`）：`deduct_state_gas()` 首先从 regular gas 中扣除，然后在 `state_gas_used` 字段上累加。生产 provider 的 `reservoir()` 始终返回 0（`evm.rs:283`），意味着 state gas 直接从调用者 gas 中扣除，无独立储备。

**关键区分**：`is_new_account`（`info.is_empty()`）vs `has_empty_code`（`info.is_empty_code_hash()`）。预充值账户（有余额，无代码）支付 `code_deposit_state_gas` 但**不**支付 `create_state_gas`（测试 `evm.rs:502-519` 验证）。

### 2.10 静态调用保护

四个状态变更方法在 `is_static` 时返回 `StaticCallViolation`：

| 方法 | 行号 |
|------|------|
| `sstore` | `evm.rs:191-193` |
| `tstore` | `evm.rs:229-231` |
| `set_code` | `evm.rs:92-94` |
| `emit_event` | `evm.rs:238-240` |

---

## §3 EVM 集成与 Fork Dispatch

### 3.1 BaseUpgrade Enum

`BaseUpgrade` 枚举（`crates/common/chains/src/upgrade.rs:6-40` @ v1.1.1）定义 12 个 fork 变体：

```
Bedrock → Regolith → Canyon → Ecotone → Fjord → Granite →
Holocene → Isthmus → Jovian → Azul → Beryl → Cobalt
```

关键细节：
- `LATEST = Azul`（`upgrade.rs:44`）— Beryl 非默认值
- `#[default]` 标注在 `Azul`（`upgrade.rs:33`）
- 测试 `upgrade.rs:191` 确认 `LATEST == Azul`

### 3.2 Ethereum SpecId 映射

`into_eth_spec()` 映射（`upgrade.rs:47-57`）：

| Base Upgrade | Ethereum SpecId |
|---|---|
| Bedrock, Regolith | MERGE |
| Canyon | SHANGHAI |
| Ecotone, Fjord, Granite, Holocene | CANCUN |
| Isthmus, Jovian | PRAGUE |
| Azul, Beryl, Cobalt（`_` 通配臂） | OSAKA |

Azul/Beryl/Cobalt 均映射到 `SpecId::OSAKA`（`upgrade.rs:55-56`），注释说明 "inherit the latest known Ethereum spec until explicitly mapped"。

### 3.3 Fork 激活机制

`from_timestamp()` 逆向查找（`upgrade.rs:62-88`）：从最新 fork (Cobalt) 到最早 (Bedrock) 依次检查激活时间戳。`forks_for()`（`upgrade.rs:91-118`）返回 12 元素数组，Azul/Beryl/Cobalt 的 timestamp 为 `Option<u64>` — 值为 `None` 时使用 `ForkCondition::Never`。

### 3.4 Precompile Fork Dispatch

`BasePrecompiles::new_with_spec()`（`crates/common/precompiles/src/provider.rs:34-55` @ v1.1.1）的 12 臂 match：

| Match 臂 | 构造方法 |
|----------|---------|
| Bedrock \| Regolith \| Canyon \| Ecotone | `Precompiles::new(eth_spec)` [标准以太坊] |
| Fjord | `Self::fjord()` |
| Granite \| Holocene | `Self::granite()` |
| Isthmus | `Self::isthmus()` |
| Jovian | `Self::jovian()` |
| Azul | `Self::azul()` |
| Beryl | `Self::beryl()` |
| Cobalt | `Self::cobalt()` |
| `_`（未知未来） | `panic!` |

### 3.5 静态 Precompile 构造链

每个 fork 在前一个基础上构建（`provider.rs:84-175`）：

| 步骤 | 方法 | 新增/修改 | 行号 |
|------|------|----------|------|
| 1 | `fjord()` | `Precompiles::cancun()` + RIP-7212 P256VERIFY | L84-92 |
| 2 | `granite()` | `fjord()` + bn254Pairing 输入限制 | L95-103 |
| 3 | `isthmus()` | `granite()` + Prague BLS12-381 + G1/G2/Pairing MSM 修改 | L106-120 |
| 4 | `jovian()` | `isthmus()` − 4 个可变输入 precompile + Jovian 版本（缩减限制） | L123-148 |
| 5 | `azul()` | `jovian()` + Osaka MODEXP + P256VERIFY Osaka 定价 | L151-161 |
| 6 | **`beryl()`** | **`Self::azul()`** — **返回相同的 `&'static Precompiles` 实例** | **L163-168** |
| 7 | `cobalt()` | `Self::beryl()` — 进一步链接 | L170-175 |

**关键证据**：`beryl()` 在 `provider.rs:166-168` 直接返回 `Self::azul()`，无克隆、无扩展。注释（L165）明确说明 "Static precompiles are the same as Azul; Beryl adds dynamic precompiles at install time."

### 3.6 动态 Precompile 安装门控

`install_with_observer()`（`provider.rs:189-205`）在 `self.spec.upgrade() >= BaseUpgrade::Beryl`（L194）条件下安装 4 个动态 precompile：

| # | Precompile | 安装调用 | 行号 |
|---|-----------|---------|------|
| 1 | B20Factory | `B20Factory::install_with_observer()` | L195 |
| 2 | BerylLookup | `BerylLookup::install_with_observer()` | L196 |
| 3 | PolicyRegistryPrecompile | `PolicyRegistryPrecompile::install_with_observer()` | L197 |
| 4 | ActivationRegistry | `ActivationRegistry::install_with_observer()` + `activation_admin_address` | L198-202 |

测试确认 Azul 不安装这些 precompile（`provider.rs:552 #[case::azul(BaseUpgrade::Azul, false)]`），Beryl 和 Cobalt 安装（`provider.rs:553-554`）。

### 3.7 BerylLookup 动态查找

`BerylLookup`（`crates/common/precompiles/src/lookup.rs:12-13` @ v1.1.1）是零大小结构体，通过 `B20Variant::from_address()` 实现动态地址匹配：

**B20 地址编码规则**：
- 字节 `[0]` = `0xb2`（`PREFIX_BYTE`）
- 字节 `[1..10]` = 9 个零字节
- 字节 `[10]` = variant 判别值（`0` = Asset, `1` = Stablecoin）
- 字节 `[11..20]` = 9 字节 `keccak256(creator, salt)` 尾部

匹配成功时返回对应的 `B20AssetPrecompile` 或 `B20StablecoinPrecompile`（`lookup.rs:30-47`）；不匹配则返回 `None`。

安装路径：`BerylLookup::install_with_observer()`（`lookup.rs:22-27`）调用 `precompiles.set_precompile_lookup()`，将动态查找函数注册到 `PrecompilesMap`，无需预注册静态条目。

### 3.8 Builder Trait 集成

`Builder` trait（`crates/common/evm/src/api/builder.rs:17-88` @ v1.1.1）是 `BaseEvm` 的构建接口：

**关键生产路径**：`precompiles_for_node()`（`builder.rs:25-29`）完成完整的 precompile 安装：
1. `BasePrecompiles::new_with_spec(self.spec())` — 创建 fork-specific precompile 集
2. 可选设置 `activation_admin_address`
3. `.install_with_observer(BerylPrecompileMetricsObserver)` — 安装动态 precompile 并注入 metrics observer

`BerylPrecompileMetricsObserver` 在此处注入，使所有 Beryl 动态 precompile 调用在生产环境中被自动仪表化。测试 `builder.rs:192-213` 确认 observer 在 EVM 执行 precompile 交易时记录调用。

---

## §4 Calldata 计价与 Beryl Precompile 集合

### 4.1 Calldata 计价机制

**常量**：`CALLDATA_WORD_GAS = 6`（`crates/common/precompiles/src/metrics.rs:546` @ v1.1.1）

**定价依据**（注释 `metrics.rs:541-545`）：模拟 Solidity predeploy 读取 calldata 的成本 — `G_copy`（3 gas/word）+ `G_memory`（3 gas/word）= 6 gas/word。此值属于 receipts/gas-used commitment，所有 Base 执行客户端必须一致。

**计价公式**（`metrics.rs:584`）：
```rust
pub const fn calldata_gas_cost(calldata: &[u8]) -> u64 {
    (calldata.len() as u64).div_ceil(32).saturating_mul(CALLDATA_WORD_GAS)
}
```

即 `ceil(len / 32) × 6`。

**扣费路径**：`BerylCallRecorder::deduct_calldata_gas()`（`metrics.rs:589-591`）委托给 `StorageCtx::deduct_gas()`，从 EVM gas 计数器中扣除，gas 不足时 revert。

### 4.2 Beryl 静态 Precompile 集合

Beryl 静态 precompile 集合与 Azul 完全相同（`beryl()` → `azul()`，`provider.rs:163-168`），包含全部以太坊标准 precompile 的 Osaka 定价版本：

| 继承链层级 | 新增/修改 |
|-----------|----------|
| `cancun()` | 以太坊 Cancun 标准 precompiles（ecrecover, sha256, ripemod160, identity, modexp, ecAdd, ecMul, ecPairing, blake2f, KZG point evaluation） |
| `fjord()` | + RIP-7212 P256VERIFY |
| `granite()` | + bn254Pairing 输入限制 |
| `isthmus()` | + Prague BLS12-381 + G1/G2/Pairing MSM |
| `jovian()` | 可变输入 precompile 缩减限制版本 |
| `azul()` = `beryl()` | + Osaka MODEXP + P256VERIFY Osaka 定价/边界 |

### 4.3 Beryl 动态 Precompile 集合

4 个 Beryl-native precompile 通过 `>= BaseUpgrade::Beryl` 门控动态安装：

| Precompile | 地址类型 | 功能 |
|-----------|---------|------|
| B20Factory | 固定地址（`B20FactoryStorage::ADDRESS`） | Token 创建、地址派生、initCalls |
| BerylLookup | 动态查找（`0xb2` + variant 编码） | B20 Asset/Stablecoin token 地址 → precompile 分发 |
| PolicyRegistryPrecompile | 固定地址 | Blocklist/allowlist 策略管理 |
| ActivationRegistry | 固定地址 + admin address | 功能激活/停用门控 |

### 4.4 Beryl v1.1.x 完整 Precompile 清单

**静态集合**（cancun→azul 继承链，≥12 个地址）：ecrecover (`0x01`), sha256 (`0x02`), ripemd160 (`0x03`), identity (`0x04`), modexp (`0x05`), ecAdd (`0x06`), ecMul (`0x07`), ecPairing (`0x08`), blake2f (`0x09`), KZG point evaluation (`0x0A`), P256VERIFY (`0x100`), BLS12-381 系列 (`0x0B-0x12`).

**动态集合**（`>= Beryl` 门控）：B20Factory, BerylLookup（动态地址空间）, PolicyRegistryPrecompile, ActivationRegistry.

### 4.5 EIP-8130 Scope Boundary

**明确排除**：EIP-8130 transaction context / nonce manager precompiles（PR #3121 `329fab2c2`、PR #3170 `771a5e451`）**不是** v1.1.1 / v1.1.0 的祖先 commit，仅存在于 `main` 并门控于 Cobalt。通过 `git merge-base --is-ancestor` 验证。不属于本分析的 Beryl v1.1.x 发布基线。

---

## §5 可观测性与 Metrics 体系

### 5.1 PrecompileCallObserver Trait

`PrecompileCallObserver` trait（`crates/common/precompiles/src/observer.rs:10-38` @ v1.1.1）定义 6 个 hook 方法（全部带默认空实现）：

| # | Hook | 签名 | 行号 |
|---|------|------|------|
| 1 | `start` | `fn start(&self, _label: &'static str)` | L12 |
| 2 | `end` | `fn end(&self, _label: &'static str)` | L15 |
| 3 | `record_call` | `fn record_call(&self, _call: &PrecompileCallMetric, _outcome: &PrecompileCallOutcome)` | L28 |
| 4 | `record_b20_created` | `fn record_b20_created(&self, _variant: &'static str)` | L31 |
| 5 | `record_batch_items` | `fn record_batch_items(&self, _call: &PrecompileCallMetric, _count: usize)` | L34 |
| 6 | `record_internal_calls` | `fn record_internal_calls(&self, _call: &..., _calls: usize, _bytes: usize)` | L37 |

Trait 边界：`Clone + Send + Sync + 'static`（L10）。

**RAII EndGuard 模式**（`observer.rs:43-58`）：`observe()` 方法（L18-25）创建 `EndGuard`，在 `Drop::drop()` 时调用 `observer.end(label)`。测试 `observe_ends_when_observed_work_panics`（L108）验证 panic 时也调用 `end()`。

**Noop 实现**：`NoopPrecompileCallObserver`（`observer.rs:6, 40`）— 零大小类型，所有 hook 均为空操作。用于测试和非 metrics 构建。

**解耦设计**：Trait 定义在 `crates/common/precompiles`，零 metrics crate 依赖。Precompile 执行代码对 `O: PrecompileCallObserver` 泛型。生产 metrics 实现在独立 crate `crates/common/evm` 中。

### 5.2 BerylPrecompileMetricsObserver

`BerylPrecompileMetricsObserver`（`crates/common/evm/src/beryl_metrics.rs:89-90` @ v1.1.1）— 零大小、`#[derive(Debug, Default, Clone, Copy)]`。

**11 个 Metrics Family**（`beryl_metrics.rs:15-83`，namespace `base.beryl.precompile`）：

| # | Metric | 类型 | Label 维度 | 行号 |
|---|--------|------|-----------|------|
| 1 | `calls_total` | counter | `[precompile, method, variant, status]` | L19-23 |
| 2 | `duration_seconds` | histogram | `[precompile, method, variant, status]` | L24-29 |
| 3 | `input_bytes` | histogram | `[precompile, method, variant, status]` | L30-35 |
| 4 | `gas_used` | histogram | `[precompile, method, variant, status]` | L36-41 |
| 5 | `state_gas_used` | histogram | `[precompile, method, variant, status]` | L42-47 |
| 6 | `gas_refunded` | histogram | `[precompile, method, variant, status]` | L48-53 |
| 7 | `errors_total` | counter | `[precompile, method, variant, error]` | L54-59 |
| 8 | `zero_gas_success_total` | counter | `[precompile, method, variant]` | L60-64 |
| 9 | `b20_created_total` | counter | `[variant]`（default: `["asset", "stablecoin"]`） | L65-67 |
| 10 | `batch_items` | histogram | `[precompile, method, variant]` | L68-72 |
| 11 | `internal_calls` + `internal_call_bytes` | 2×histogram | `[precompile, method, variant]` | L73-82 |

注：`internal_calls` 和 `internal_call_bytes` 由同一 `record_internal_calls()` hook 记录（`beryl_metrics.rs:180-192`），视为一个 "metrics family"。在 `define_metrics!` 宏声明中实际有 12 个独立系列。

**Status label 值**：`success` | `revert` | `halt` | `fatal`（`PrecompileCallStatus`，`metrics.rs:63-95`）。

**条件发射逻辑**（`beryl_metrics.rs:107-193`）：`gas_refunded` 通过 `.max(0)` 钳制为非负；`duration_seconds` 仅在 `Some` 时记录；`errors_total` 仅在有 error 时递增；`zero_gas_success_total` 仅在 Success + `gas_used == 0` 时触发。所有方法在 `#[cfg(not(feature = "metrics"))]` 时编译为空操作。

### 5.3 BerylErrorKind 错误分类体系

`BerylErrorKind`（`metrics.rs:166-200` @ v1.1.1）— 16 种错误类别：

| # | Variant | Label | 行号 |
|---|---------|-------|------|
| 1 | `StaticWrite` | `"static_write"` | L169 |
| 2 | `UnknownSelector` | `"unknown_selector"` | L171 |
| 3 | `AbiDecode` | `"abi_decode"` | L173 |
| 4 | `FeatureInactive` | `"feature_inactive"` | L175 |
| 5 | `Unauthorized` | `"unauthorized"` | L177 |
| 6 | `PolicyDenied` | `"policy_denied"` | L179 |
| 7 | `PolicyMissing` | `"policy_missing"` | L181 |
| 8 | `Paused` | `"paused"` | L183 |
| 9 | `DuplicateCreate` | `"duplicate_create"` | L185 |
| 10 | `InvalidInput` | `"invalid_input"` | L187 |
| 11 | `InternalCallFailed` | `"internal_call_failed"` | L189 |
| 12 | `OutOfGas` | `"out_of_gas"` | L191 |
| 13 | `Panic` | `"panic"` | L193 |
| 14 | `Fatal` | `"fatal"` | L195 |
| 15 | `SlotOverflow` | `"slot_overflow"` | L197 |
| 16 | `OtherRevert` | `"other_revert"` | L199 |

**分类机制**：`BerylErrorClassifier`（`metrics.rs:357-368`）使用 `SolError::SELECTOR` 4 字节选择器匹配 revert bytes。`from_revert_bytes()`（`metrics.rs:247-339`）按优先级链式检查 `IActivationRegistry`, `IPolicyRegistry`, `IB20`, `IB20Factory`, `IB20Asset`, `IB20Stablecoin` 全部接口的错误类型。

### 5.4 BerylCallRecorder 生命周期

`BerylCallRecorder<O: PrecompileCallObserver>`（`metrics.rs:549-631` @ v1.1.1）管理单次 precompile 调用的完整生命周期：

```
start() → 创建 recorder + 启动 BerylCallTimer + 存储 PrecompileCallMetric
  ↓
deduct_calldata_gas() → 通过 StorageCtx::deduct_gas 收取 calldata gas
  ↓
[Precompile 执行]
  ↓
record_result() → 构建 PrecompileCallOutcome::from_result() + 调用 observer.record_call()
```

`PrecompileCallOutcome`（`metrics.rs:101-115`）字段：`status`, `gas_used`, `state_gas_used`, `gas_refunded`, `duration_seconds`, `error`。

**Method label 推导**：`BerylMetricLabels`（`metrics.rs:371-506`）为每个 precompile surface 从 ABI selector 反查 method name — `factory_method()` 匹配 4 个 selector, `activation_method()` 匹配 5 个, `policy_method()` 匹配 11 个, `b20_asset_method()` 和 `b20_stablecoin_method()` 使用 `name_by_selector` 查找表，无匹配时返回 `"unknown"`。

---

## §6 Blast Radius 架构判断（关键）

### 6.1 四层隔离证据

#### Layer 1: 附加模式（Additive Pattern）

**证据**：Beryl 静态 precompile 集合与 Azul 完全相同。

- `beryl()` 直接返回 `azul()`（`provider.rs:166-168` @ v1.1.1）— 相同的 `&'static Precompiles` 指针，无克隆、无扩展
- 注释（L165）："Static precompiles are the same as Azul; Beryl adds dynamic precompiles at install time"
- 4 个 Beryl-native precompile 是**新增安装**（`install_with_observer()` L194-203），不是替换或修改既有 precompile

**结论**：Beryl 不修改任何既有 precompile 的行为，ecrecover (`0x01`)、sha256 (`0x02`) 等标准 precompile 在 Beryl 下与 Azul 行为完全一致。

#### Layer 2: Fork 门控（Fork Gate）

**证据**：动态 precompile 安装被 fork 时间戳门控。

- 安装条件：`self.spec.upgrade() >= BaseUpgrade::Beryl`（`provider.rs:194`）
- Fork 激活由 `ChainConfig` 中的时间戳控制（`upgrade.rs:96-99`）
- `ForkCondition::Never` 可完全禁用 fork（`upgrade.rs:91-118`）
- 测试确认 Azul 不安装动态 precompile（`provider.rs:552`）

**结论**：在 Beryl 激活时间戳之前，这 4 个 precompile 完全不存在于 EVM 执行环境中。

#### Layer 3: 地址空间编码隔离

**证据**：B20 token 地址使用独特编码，与既有地址空间不冲突。

- B20 地址格式：`0xb2` + 9 零字节 + variant 判别 + 9 字节哈希尾 — 总共 20 字节地址（`variant.rs:24, 66-73`）
- `BerylLookup::lookup()`（`lookup.rs:30-47`）仅对满足此编码规则的地址返回 precompile，其他地址返回 `None`
- 标准以太坊 precompile 地址空间为 `0x01`-`0x12` — 与 `0xb2` 前缀不冲突
- B20Factory 和 PolicyRegistryPrecompile 使用固定地址（由 `*Storage::ADDRESS` 常量定义），不在标准 precompile 地址范围内
- `contains()` 方法（`provider.rs:240-242`）委托给 `inner.contains()`，仅检查静态 precompile 集

**结论**：B20 地址编码在数学上保证与既有 precompile 和 EOA/contract 地址空间不冲突。

#### Layer 4: 存储地址隔离

**证据**：每个 precompile 使用自身地址作为存储操作的 address 参数。

- `Slot<'a, T>` 结构体持有 `address: Address` 字段（`types/slot.rs:16-22`）— 存储操作绑定到 precompile 自身地址
- `sload(address, key)` 和 `sstore(address, key, value)` 的 `address` 参数来自 `ContractStorage::address()`（`evm.rs:158, 190`）
- `#[contract]` 宏生成的 `new()` 方法硬编码 precompile 地址（`layout.rs:155-163`）
- Precompile 内部 storage slot 空间独立于 EOA/contract 的 storage 空间 — EVM journal 按 address 隔离存储

**结论**：Beryl precompile 的存储操作不会读写其他地址的 storage slot，不可能污染既有合约状态。

### 6.2 ActivationRegistry 额外门控

`ActivationRegistry`（`provider.rs:198-202`）接受 `activation_admin_address` 参数，提供 Beryl 激活后的运行时功能启/停能力。这是在 fork 门控之上的第二层治理控制，允许在不修改 fork 参数的情况下对特定 B20 功能进行精细化管控。

### 6.3 对既有交易流的影响分析

**维度 1: 对既有 precompile 行为**

既有以太坊 precompile（ecrecover、sha256 等）在 Beryl 下的行为与 Azul 完全一致，因为 `beryl()` 返回与 `azul()` 相同的 `&'static Precompiles` 实例。静态集合不发生任何变更。

**维度 2: 对既有 contract/EOA 交易**

1. 非 Beryl precompile 地址的 CALL/DELEGATECALL 不受影响 — `BerylLookup` 仅匹配 `0xb2` 前缀地址
2. 既有合约的 storage 不受影响 — Beryl precompile 使用独立地址空间
3. Gas 语义完全一致 — Beryl precompile 的 storage 操作使用与普通合约相同的 EIP-2200/2929/3529 gas 语义（相同的 `GasParams`）

### 6.4 Blast Radius 综合结论

**判定**：Beryl precompiles 对既有交易状态转移的 blast radius 为**零**。

**论证链**：
1. 静态 precompile 集合不变（`beryl()` = `azul()`）→ 既有 precompile 行为不变
2. 4 个动态 precompile 仅通过新增安装引入 → 不替换或修改任何既有代码路径
3. Fork 门控 (`>= Beryl`) → 激活前完全不存在
4. B20 地址编码（`0xb2` 前缀）→ 数学上与既有地址空间不冲突
5. 存储地址隔离 → 不可能污染既有合约状态
6. Gas 语义一致 → 不改变 EVM 执行的经济模型

**信心度**：**高**。每一层隔离均有代码行级证据支撑，且有测试验证。唯一的理论风险路径是 `B20Variant::compute_address()` 产生的地址意外碰撞 — 但该地址由 `(variant, sender, salt)` 的 keccak256 派生，碰撞概率在密码学上可忽略。

**对下游研究的支撑**：本结论为 WHI-249（Beryl 信心分析）提供关键技术依据 — Beryl 升级在 precompile 基础设施层面不引入对既有系统的回归风险。

---

## Diagrams

### Diagram 1: Precompile-Storage Provider 层次结构

```mermaid
classDiagram
    class PrecompileStorageProvider {
        <<trait>>
        +sload(address, key) Result~U256~
        +sstore(address, key, value) Result
        +tload(address, key) Result~U256~
        +tstore(address, key, value) Result
        +set_code(address, code) Result
        +emit_event(address, event) Result
        +checkpoint() JournalCheckpoint
        +checkpoint_commit()
        +checkpoint_revert(checkpoint)
        +deduct_gas(gas) Result
        +deduct_state_gas(gas) Result
        +refund_gas(gas)
        +is_static() bool
    }

    class EvmPrecompileStorageProvider {
        -internals: EvmInternals
        -gas: Gas
        -gas_params: GasParams
        -is_static: bool
        -state_gas_used: u64
    }

    class StorageOps {
        <<trait>>
        +store(slot, value) Result
        +load(slot) Result~U256~
    }

    class ContractStorage {
        <<trait>>
        +address() Address
        +storage() StorageCtx
    }

    class StorableType {
        <<trait>>
        +LAYOUT
        +SLOTS
        +BYTES
        +handle() Handler
    }

    class Handler {
        <<trait>>
        +read() +write() +delete()
        +t_read() +t_write() +t_delete()
    }

    class FromWord {
        <<trait>>
        +to_word() U256
        +from_word(U256) Result~Self~
    }

    PrecompileStorageProvider <|.. EvmPrecompileStorageProvider : implements
    EvmPrecompileStorageProvider ..> GasParams : EIP-2200 stipend\nEIP-2929 cold/hot\nEIP-3529 refund
    EvmPrecompileStorageProvider ..> EvmInternals : journal access
    ContractStorage ..> StorageCtx : provides
    StorableType ..> Handler : creates
    Handler ..> StorageOps : uses
    FromWord <.. Handler : decodes
```

### Diagram 2: Fork Dispatch 与 Precompile 安装流程

```mermaid
flowchart TD
    A[BaseUpgrade enum] --> B{new_with_spec}
    B -->|Bedrock..Ecotone| C[Precompiles::new eth_spec]
    B -->|Fjord| D[fjord: +P256VERIFY]
    B -->|Granite/Holocene| E[granite: +bn254 bound]
    B -->|Isthmus| F[isthmus: +BLS12-381]
    B -->|Jovian| G[jovian: input limits]
    B -->|Azul| H[azul: +Osaka pricing]
    B -->|Beryl| I["beryl() = azul()"]
    B -->|Cobalt| J["cobalt() = beryl()"]

    I --> K{install_with_observer}
    J --> K

    K -->|"spec >= Beryl?"| L{Yes}
    K -->|No| M[Static precompiles only]

    L --> N[B20Factory]
    L --> O[BerylLookup]
    L --> P[PolicyRegistryPrecompile]
    L --> Q[ActivationRegistry]

    O --> R["B20Variant::from_address()"]
    R -->|"0xb2 + Asset"| S[B20AssetPrecompile]
    R -->|"0xb2 + Stablecoin"| T[B20StablecoinPrecompile]
    R -->|No match| U[None]

    style I fill:#e1f5fe
    style L fill:#c8e6c9
    style N fill:#fff9c4
    style O fill:#fff9c4
    style P fill:#fff9c4
    style Q fill:#fff9c4
```

### Diagram 3: Blast Radius 隔离层

```mermaid
flowchart LR
    subgraph L1["Layer 1: 附加模式"]
        A1["beryl() = azul()"] --> A2["静态 precompile 不变"]
        A3["动态 precompile = 新增安装"] --> A4["不替换既有代码"]
    end

    subgraph L2["Layer 2: Fork 门控"]
        B1["spec >= Beryl 检查"] --> B2["激活前不存在"]
        B3["ForkCondition::Never 可禁用"] --> B4["完全可控"]
    end

    subgraph L3["Layer 3: 地址空间隔离"]
        C1["B20: 0xb2 前缀编码"] --> C2["与 0x01-0x12 不冲突"]
        C3["BerylLookup: 仅匹配编码地址"] --> C4["非 B20 地址返回 None"]
    end

    subgraph L4["Layer 4: 存储隔离"]
        D1["Slot 绑定 precompile address"] --> D2["独立 storage 空间"]
        D3["EVM journal 按 address 隔离"] --> D4["无法污染既有合约"]
    end

    L1 --> L2 --> L3 --> L4 --> E["Blast Radius = 零"]

    style E fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style L1 fill:#e3f2fd
    style L2 fill:#e8f5e9
    style L3 fill:#fff3e0
    style L4 fill:#fce4ec
```

---

## Source Coverage

### Primary Sources

| Source | Status | Items Covered |
|--------|--------|--------------|
| `crates/common/precompile-macros/src/` @ v1.1.1 | ✅ 完整覆盖 | Item 1 |
| `crates/common/precompile-storage/src/` @ v1.1.1 | ✅ 完整覆盖 | Item 2 |
| `crates/common/precompiles/src/provider.rs` @ v1.1.1 | ✅ 完整覆盖 | Items 3, 4, 6 |
| `crates/common/precompiles/src/lookup.rs` @ v1.1.1 | ✅ 完整覆盖 | Items 3, 6 |
| `crates/common/precompiles/src/observer.rs` @ v1.1.1 | ✅ 完整覆盖 | Item 5 |
| `crates/common/precompiles/src/metrics.rs` @ v1.1.1 | ✅ 完整覆盖 | Items 4, 5 |
| `crates/common/evm/src/beryl_metrics.rs` @ v1.1.1 | ✅ 完整覆盖 | Item 5 |
| `crates/common/evm/src/api/builder.rs` @ v1.1.1 | ✅ 完整覆盖 | Item 3 |
| `crates/common/chains/src/upgrade.rs` @ v1.1.1 | ✅ 完整覆盖 | Item 3 |

### Secondary Sources

| Source | Status | Notes |
|--------|--------|-------|
| `base-beryl-vs-azul/outlines/beryl-scope-inventory.md` | ✅ 引用 | WHI-245 上游依赖 |
| PR #3389 (`9c3c3f54c`) | ✅ 祖先验证 | 直接 v1.1.1 祖先 |
| PR #3342 via backport #3426 (`526d5361c`) | ✅ 祖先验证 | 经 backport 落入 v1.1.1 |
| PR #3119 (`213f13ce1`) | ✅ 祖先验证 | 直接 v1.1.1 祖先 |

### Source Integrity

- ✅ 所有代码引用标注 `@ v1.1.1 (01e732cd)` + file path + line number
- ✅ 无裸 HEAD 引用
- ✅ PR# 附带 commit hash + v1.1.1 祖先验证方式
- ✅ EIP-8130 明确标注为 scope boundary（不在 v1.1.x 基线中）

---

## Gap Analysis

| Gap | Severity | Mitigation |
|-----|----------|-----------|
| `B20Variant::compute_address()` 的完整实现细节（creator + salt → keccak256 → address）未深入分析 | Minor | 地址派生机制属 WHI-246（B20 token 标准）范围；本研究引用了 `from_address()` 的验证逻辑，足以支撑 blast radius 结论 |
| ActivationRegistry 的 admin model 和激活/停用流程未深入分析 | Minor | 属 WHI-251（激活治理）范围；本研究仅分析其作为安装时门控层的角色 |
| `GasParams` 的具体数值（cold_storage_additional_cost、sstore_static_gas 等）未列出 | Minor | 这些值由 revm 的 SpecId (OSAKA) 决定，属以太坊规范常量，非 Base/Beryl 特有实现 |
| `PrecompilesMap` 的 `contains()` 行为（对比 `BasePrecompiles::contains()`）未深入分析 | Minor | Item 3 已说明 `BasePrecompiles::contains()` 仅检查静态集，生产 EVM 使用 `PrecompilesMap` 的 `get()` 检查静态 + 动态 |

---

## Revision Log

| Round | Date | Changes |
|-------|------|---------|
| 1 | 2026-06-21 | Initial deep draft covering all 6 research items + 3 Mermaid diagrams |
