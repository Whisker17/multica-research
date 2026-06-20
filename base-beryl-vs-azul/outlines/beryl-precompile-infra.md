# Research Outline: Beryl Precompile 基础设施与 EVM 集成分析

## Metadata

| Field | Value |
|-------|-------|
| project_slug | `base-beryl-vs-azul` |
| topic_slug | `beryl-precompile-infra` |
| multica_issue_id | `fb7245dd-682d-445f-b9cd-96c5708e4505` |
| round | 2 |
| github_repo | `Whisker17/multica-research` |
| outline_path | `base-beryl-vs-azul/outlines/beryl-precompile-infra.md` |
| draft_path | `base-beryl-vs-azul/research-sections/beryl-precompile-infra/drafts/round-1.md` |
| final_path | `base-beryl-vs-azul/research-sections/beryl-precompile-infra/final.md` |

## Topic

Beryl Precompile 基础设施与 EVM 集成分析 — 分析支撑 B20 原生 token 标准的底层工程基础设施：native precompile 框架、precompile-storage provider（含 EIP-2200 gas 计价、checkpoint/commit/revert、slot overflow 防护）、EVM fork dispatch 集成、calldata 计价与 Beryl precompile 集合盘点、可观测性指标体系，以及关键的 blast radius 架构判断。

## Scope

### In-Scope

- Native precompile 框架：`#[contract]` / `#[precompile]` 宏系统、`ContractConfig` 解析、属性转发、地址别名拒绝、字段布局/slot packing
- Precompile-storage provider（重点）：`PrecompileStorageProvider` trait 体系、`EvmPrecompileStorageProvider` 生产实现、SLOAD/SSTORE EIP-2929 冷/热计价、EIP-2200 gas-stipend (2300) 守卫、EIP-3529 net-metering refund 传播、checkpoint/commit/revert 原子性、slot 算术 `checked_add` 迁移（BOP-356/380）、`FromWord for bool` 非规范值拒绝、set_code 中的 EIP-8037 state gas 计费
- EVM 集成与 fork dispatch：`BaseUpgrade` enum（Bedrock→Beryl→Cobalt）、`into_eth_spec()` 映射（Beryl→Osaka）、`BasePrecompiles::new_with_spec()` fork dispatch、`beryl()` / `cobalt()` 构造（PR #3342，经 backport #3426 `526d5361c` 落入 v1.1.1）、`install_with_observer()` 动态 precompile 安装门控（`>= BaseUpgrade::Beryl`）、`Builder` trait 集成
- Calldata 计价 `CALLDATA_WORD_GAS = 6` 与 Beryl precompile 完整集合盘点（静态 + 动态）
- 可观测性：`PrecompileCallObserver` trait、`BerylPrecompileMetricsObserver` 生产实现、`PrecompileCallMetric` / `PrecompileCallOutcome` / `BerylErrorKind` 错误分类体系、`BerylCallRecorder` per-call 记录器、`beryl_metrics.rs` 中 11 个 metrics family
- Blast radius 架构判断（关键）：论证 Beryl precompiles 的「附加 + fork 门控」模式如何限制对既有交易状态转移的影响面

### Out-of-Scope

- B20 token 标准业务逻辑（Asset/Stablecoin variant 的 mint/burn/transfer/permit）— 由 WHI-246 覆盖
- PolicyRegistry / ActivationRegistry 的治理策略设计 — 由 WHI-251 覆盖
- Reth V2 性能影响分析 — 由 WHI-249 覆盖
- Cobalt 功能代码分析（仅分析 Cobalt plumbing 骨架以说明 fork dispatch 完整性）
- L1 合约层变更
- BLS12-381 / bn254 等以太坊标准 precompile 的实现（仅追踪 fork 级别的 precompile 集合变更链）
- EIP-8130 transaction context / nonce manager precompiles — PR #3121 (`329fab2c2`) 和 PR #3170 (`771a5e451`) 不是 v1.1.1 或 v1.1.0 的祖先 commit（仅存在于 `main`，门控于 Cobalt），不属于 Beryl v1.1.x 发布基线

## Code Baseline

| Network | Release Tag | Commit (`^{}` 解引用) | 用途 |
|---------|------------|----------------------|------|
| Mainnet | `v1.1.1` | `01e732cdbae0c624d652da9e608d7d3fe0f9c74b` | 主基线 |
| Sepolia | `v1.1.0` | `a3c3011b16dae73aaea455ec0a5ff614e65b7d0a` | Beryl 功能完整集 |

**本地代码路径**: `/Users/whisker/Work/src/networks/base/base`

### Key PRs & Commits (v1.1.1 祖先验证)

所有引用 commit 均已通过 `git merge-base --is-ancestor <commit> v1.1.1` 验证。原始 PR merge commit 不一定是 v1.1.1 直接祖先（部分通过 backport squash 入 release 分支），表中标注实际落入 v1.1.1 的 commit。

| PR# | v1.1.1 落入方式 | v1.1.1 祖先 commit | 标题 | 关联 Item |
|-----|----------------|-------------------|------|----------|
| #3342 | 经 backport #3426 | `526d5361c` | fix(precompiles): add separate match arms and cobalt() constructor for fork dispatch | Item 3 |
| #3389 | 直接祖先 | `9c3c3f54c` | feat(common): add beryl precompile metrics | Item 5 |
| #3119 | 直接祖先 | `213f13ce1` | feat(chains): add Cobalt hardfork plumbing | Item 3 |

**不在 v1.1.1 基线中的 PR（scope boundary）**：
- PR #3121 (`329fab2c2`) — EIP-8130 transaction context + nonce manager precompiles，仅存在于 `main`，门控于 Cobalt
- PR #3170 (`771a5e451`) — EIP-8130 AA txs gated behind Cobalt，仅存在于 `main`
- PR #3338 (`3d2a18fa2`/`47f214d0f`) — 原始 Beryl metrics PR，被 PR #3389 在 release 分支上替代

## Research Items

### Item 1: Native Precompile 框架

**Slug**: `native-precompile-framework`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `contract_macro` | `#[contract(addr = "0x...")]` 宏：`ContractConfig` 解析、字段布局生成（`FieldInfo`, `FieldKind`）、slot packing（Solidity 右对齐规则）、属性转发（`extract_attributes()`） | `crates/common/precompile-macros/src/contract.rs` @ v1.1.1 |
| `precompile_macro` | `#[precompile]` 宏：singleton/constructor 生成、地址别名拒绝（reserved names: `address`, `storage`, `msg_sender`） | `crates/common/precompile-macros/src/precompile.rs` @ v1.1.1 |
| `storable_derive` | `Storable` trait 推导：类型布局描述符 `StorableType`、slot 分配策略、ERC-7201 namespace 支持 | `crates/common/precompile-macros/src/{storable.rs, layout.rs, namespace.rs}` @ v1.1.1 |
| `packing_rules` | Slot bin-packing 规则：`FieldLocation` 计算、Solidity 兼容的右对齐 | `crates/common/precompile-macros/src/packing.rs` @ v1.1.1 |
| `code_generation_flow` | 宏展开完整流程：source → AST → ContractConfig → FieldInfo → slot assignment → StorageOps impl | 综合上述文件 |

**Acceptance Criteria**:
- 宏系统的完整展开流程有代码引用链
- 地址别名拒绝规则有测试用例佐证
- slot packing 规则与 Solidity 布局兼容性有明确说明

### Item 2: Precompile-Storage Provider（重点）

**Slug**: `precompile-storage-provider`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `trait_hierarchy` | `PrecompileStorageProvider` trait 的完整方法签名：`sload`, `sstore`, `tload`, `tstore`, `set_code`, `emit_event`, `checkpoint`, `checkpoint_commit`, `checkpoint_revert`, `deduct_gas`, `deduct_state_gas`, `refund_gas`, `metered_keccak256`；以及 `StorageOps`, `ContractStorage`, `StorableType`, `Handler`, `FromWord` 的角色与关系 | `crates/common/precompile-storage/src/provider.rs` @ v1.1.1 |
| `evm_provider_impl` | `EvmPrecompileStorageProvider` 生产实现：从 `PrecompileInput` + `GasParams` 构造、与 `alloy_evm::EvmInternals` journal 的交互 | `crates/common/precompile-storage/src/evm.rs` @ v1.1.1 |
| `eip2200_stipend` | EIP-2200 gas-stipend 守卫实现：`sstore()` 中 `gas.remaining() <= gas_params.call_stipend()` 检查（L199）、2300 gas 不变量、Solidity `.transfer()` 重入防护语义、测试 `eip_2200_stipend_guard_constant_is_2300()` | `evm.rs:190-201` + tests @ v1.1.1 |
| `eip2929_cold_hot` | EIP-2929 冷/热存储访问计价：`sload` 中 `warm_storage_read_cost()` + `cold_storage_additional_cost()`（L167-171）；`sstore` 中 `sstore_static_gas()` + `sstore_dynamic_gas()`（L210-212）；`with_account_info` 中的 account 冷/热访问（L148-150）；测试 `sload_oog_does_not_warm_slot()` 验证 OOG 时不 warm slot | `evm.rs:158-183, 190-226` @ v1.1.1 |
| `eip3529_refund` | EIP-3529 net-metering refund 传播：`sstore()` 中 `gas_params.sstore_refund(true, &s.data)`（L214）；`refund_gas()` 调用 `gas.record_refund()`（L262-264） | `evm.rs:214, 262-264` @ v1.1.1 |
| `checkpoint_atomicity` | Checkpoint/commit/revert 原子性模式：`sload()` 和 `sstore()` 的 checkpoint guard 模式（checkpoint → operation → commit 或 revert）；`StorageCtx` 包装；`JournalCheckpoint` 类型 | `evm.rs:159-183, 202-226`; `storage_ctx.rs` @ v1.1.1 |
| `slot_overflow_checked_add` | Slot 算术 `checked_add` 迁移（BOP-356/380）：`Slot::new_at_offset()` 和 `Slot::new_at_loc()` 中 `base_slot.checked_add(U256::from_limbs(...)).ok_or(SlotOverflow)?`；additive slot 路径的 collection types（`vec`, `set`, `array`, `bytes_like`）均使用 `checked_add`。`mapping` 使用 keccak256 hashed slot 推导（无加法溢出风险），不在 `checked_add` 审计范围内 | `crates/common/precompile-storage/src/types/slot.rs:44-58, 63-82`; `types/{vec,set,array,bytes_like}.rs` @ v1.1.1 (`01e732cd`)；`types/mapping.rs` 使用 hashed derivation（无 `checked_add`） |
| `noncanonical_bool_rejection` | 非规范 bool 值拒绝：`FromWord for bool` 仅接受 `U256::ZERO` 和 `U256::ONE`，其余返回 `enum_conversion_error()` | `crates/common/precompile-storage/src/types/primitives.rs:39-52` @ v1.1.1 |
| `set_code_state_gas` | `set_code()` 中的 EIP-8037 state gas 计费：`create_state_gas()` + `code_deposit_state_gas()` 对新账户/已有账户的差异化处理；Yellow Paper G_codedeposit / G_create / G_sha3 费用 | `evm.rs:91-131` + tests @ v1.1.1 |
| `static_call_guard` | 静态调用保护：`sstore()`, `tstore()`, `set_code()`, `emit_event()` 在 `is_static` 时返回 `StaticCallViolation` | `evm.rs` 各方法入口 @ v1.1.1 |
| `tload_tstore` | 瞬时存储操作：`tload()` / `tstore()` 仅收取 `warm_storage_read_cost()`，无 checkpoint guard | `evm.rs:185-235` @ v1.1.1 |

**Acceptance Criteria**:
- EIP-2200/2929/3529 三个 EIP 的实现均有代码行级引用和语义解释
- checkpoint/commit/revert 模式的正确性论证（OOG 不泄露 warm 状态）
- `checked_add` 迁移的覆盖面统计（additive slot 路径：`slot`, `array`, `vec`, `set`, `bytes_like`）及 `mapping` 的 hashed derivation 说明
- 非规范 bool 拒绝的安全意义解释
- state gas 与 regular gas 的关系说明

### Item 3: EVM 集成与 Fork Dispatch

**Slug**: `evm-integration-fork-dispatch`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `base_upgrade_enum` | `BaseUpgrade` enum 定义（12 个变体：Bedrock→Cobalt）、`LATEST = Azul`（非 Beryl — Beryl 尚非默认）、`#[default]` 标注在 Azul | `crates/common/chains/src/upgrade.rs:6-39` @ v1.1.1 |
| `eth_spec_mapping` | `into_eth_spec()` 映射：Beryl/Azul/Cobalt 均映射到 `SpecId::OSAKA`（通配 `_` 臂）；完整映射表 Bedrock→MERGE, Canyon→SHANGHAI, Ecotone..Holocene→CANCUN, Isthmus..Jovian→PRAGUE | `upgrade.rs:47-57` @ v1.1.1 |
| `fork_activation` | Fork 激活机制：`from_timestamp()` 逆向查找（最新→最早）、`forks_for()` 返回 12 元素数组、`ForkCondition::Timestamp` vs `ForkCondition::Never`；Beryl timestamp 在 mainnet/sepolia/zeronet 均已设置 | `upgrade.rs:59-118` @ v1.1.1 |
| `precompile_dispatch` | `BasePrecompiles::new_with_spec()` fork dispatch：12 个 match 臂，每个 fork 对应一个 precompile 构造方法；Beryl→`Self::beryl()` 返回 `Self::azul()`（静态 precompile 相同）、Cobalt→`Self::cobalt()` 返回 `Self::beryl()` | `crates/common/precompiles/src/provider.rs:34-48, 163-175` @ v1.1.1 |
| `precompile_chain` | 静态 precompile 构造链：`cancun()` → `fjord()` (+RIP-7212) → `granite()` (+bn254 bound) → `isthmus()` (+BLS12-381) → `jovian()` (input limits) → `azul()` (+Osaka MODEXP/P256VERIFY pricing) → `beryl()` = `azul()` → `cobalt()` = `beryl()` | `provider.rs:84-175` @ v1.1.1 |
| `dynamic_install` | 动态 precompile 安装门控：`install_with_observer()` 中 `if self.spec.upgrade() >= BaseUpgrade::Beryl` 安装 B20Factory, BerylLookup, PolicyRegistryPrecompile, ActivationRegistry 四个动态 precompile | `provider.rs:188-205` @ v1.1.1 |
| `beryl_lookup` | `BerylLookup` 动态查找：`B20Variant::from_address()` 判断 → `B20AssetPrecompile` 或 `B20StablecoinPrecompile`；`PrecompileLookup` trait 实现 | `crates/common/precompiles/src/lookup.rs` @ v1.1.1 |
| `builder_integration` | `Builder` trait：`precompiles_for_node()` 安装 `BerylPrecompileMetricsObserver`；`build_base()` / `build_base_with_activation_admin_address()` / `build_with_inspector()` 构建完整 `BaseEvm` | `crates/common/evm/src/api/builder.rs` @ v1.1.1 |
| `cobalt_dispatch_pr3342` | PR #3342（经 backport #3426 `526d5361c` 落入 v1.1.1）：添加 Beryl/Cobalt 独立 match 臂（此前可能 fall-through），构建 `cobalt()` 构造函数 | `git merge-base --is-ancestor 526d5361c v1.1.1` ✓ |

**Acceptance Criteria**:
- fork dispatch 的完整 match 臂列表
- Beryl 静态 precompile 与 Azul 相同的代码证据
- 动态 precompile 安装的 fork 门控条件精确引用
- `BerylLookup` 地址编码 → variant 映射的机制说明
- PR #3342 的变更内容与动机（经 backport #3426 落入 v1.1.1）

### Item 4: Calldata 计价与 Beryl Precompile 集合

**Slug**: `calldata-pricing-and-precompile-set`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `calldata_word_gas` | Calldata 计价常量 `CALLDATA_WORD_GAS = 6`：模拟 Solidity predeploy 的 `G_copy (3) + G_memory (3)` = 6 gas/word；属于 receipts/gas-used commitment，所有 Base 执行客户端必须一致 | `crates/common/precompiles/src/metrics.rs:546` @ v1.1.1 (`01e732cd`) |
| `calldata_gas_formula` | 计价公式：`(calldata.len() as u64).div_ceil(32).saturating_mul(CALLDATA_WORD_GAS)`；由 `BerylCallRecorder::calldata_gas_cost()` 实现；`deduct_calldata_gas()` 在每个 Beryl precompile dispatch 入口调用 | `metrics.rs:584-586, 589-591` @ v1.1.1 (`01e732cd`) |
| `beryl_static_set` | Beryl 静态 precompile 集合：与 Azul 相同（`beryl() -> azul()`），包含全部以太坊 precompiles + RIP-7212 P256VERIFY + Osaka MODEXP/P256VERIFY 定价 + Jovian input limits + BLS12-381 | `provider.rs:163-168` @ v1.1.1 (`01e732cd`) |
| `beryl_dynamic_set` | Beryl 动态 precompile 集合（`>= BaseUpgrade::Beryl` 门控安装）：B20Factory（固定地址）、BerylLookup（动态 B20 Asset/Stablecoin token 地址）、PolicyRegistryPrecompile（固定地址）、ActivationRegistry（固定地址 + admin address） | `provider.rs:188-205` @ v1.1.1 (`01e732cd`) |
| `beryl_complete_inventory` | Beryl v1.1.x 完整 precompile 清单表：静态集合（继承链 cancun→azul）+ 动态集合（4 个 Beryl-native precompiles） | 综合 `provider.rs` @ v1.1.1 (`01e732cd`) |
| `eip8130_scope_boundary` | **Scope 边界说明**：EIP-8130 transaction context / nonce manager precompiles（PR #3121 `329fab2c2`、PR #3170 `771a5e451`）不是 v1.1.1 / v1.1.0 的祖先 commit，仅存在于 `main` 并门控于 Cobalt，不属于本分析的 Beryl 基线 | `git merge-base --is-ancestor` 验证 |

**Acceptance Criteria**:
- `CALLDATA_WORD_GAS` 的定价依据（G_copy + G_memory 类比）和共识影响说明
- Beryl 完整 precompile 清单表（静态 + 动态），无 EIP-8130
- 明确标注 EIP-8130 precompiles 不在 v1.1.x 基线中（scope boundary）

### Item 5: 可观测性与 Metrics 体系

**Slug**: `observability-metrics`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `observer_trait` | `PrecompileCallObserver` trait：6 个 hook 方法（`start`, `end`, `record_call`, `record_b20_created`, `record_batch_items`, `record_internal_calls`）；`NoopPrecompileCallObserver` 空实现；`EndGuard` RAII 模式确保 panic 时也调用 `end()` | `crates/common/precompiles/src/observer.rs` @ v1.1.1 |
| `metrics_observer` | `BerylPrecompileMetricsObserver` 生产实现：11 个 metrics family（`calls_total`, `duration_seconds`, `input_bytes`, `gas_used`, `state_gas_used`, `gas_refunded`, `errors_total`, `zero_gas_success_total`, `b20_created_total`, `batch_items`, `internal_calls` / `internal_call_bytes`）| `crates/common/evm/src/beryl_metrics.rs` @ v1.1.1 |
| `metric_labels` | Label 维度设计：4 通用标签 `[precompile, method, variant, status]` + errors 额外 `[error]` label；每个 Beryl precompile surface 的 method label 由 `BerylMetricLabels` 从 ABI selector 反查 | `metrics.rs:374-506` @ v1.1.1 |
| `error_classification` | `BerylErrorKind` 16 种错误类别：从 `BasePrecompileError` 和 ABI-encoded revert bytes 分类；`BerylErrorClassifier` 基于 `SolError::SELECTOR` 匹配；覆盖 IActivationRegistry, IB20, IB20Factory, IB20Asset, IB20Stablecoin, IPolicyRegistry 全部错误类型 | `metrics.rs:166-340` @ v1.1.1 |
| `call_recorder` | `BerylCallRecorder<O>`：per-call 生命周期管理（start → deduct calldata gas → execute → record_base_result/record_base_error）；timer（std 下 `Instant::now()`, no_std 下 no-op） | `metrics.rs:548-631` @ v1.1.1 |
| `call_outcome` | `PrecompileCallOutcome`：`status` + `gas_used` + `state_gas_used` + `gas_refunded` + `duration_seconds` + `error`；从 `PrecompileResult` 构造 | `metrics.rs:100-163` @ v1.1.1 |
| `pr_references` | PR #3389 `9c3c3f54c`（直接 v1.1.1 祖先）：引入 Beryl precompile metrics 完整基础设施。原始 PR #3338 (`3d2a18fa2`/`47f214d0f`) 不是 v1.1.1 祖先，其内容被 #3389 在 release 分支上替代 | `git merge-base --is-ancestor 9c3c3f54c v1.1.1` ✓ |

**Acceptance Criteria**:
- 11 个 metrics family 的完整清单及其 label 维度
- Observer 模式与 precompile 执行的解耦方式说明
- 错误分类覆盖面分析（是否覆盖全部 Beryl revert 路径）
- call recorder 的生命周期图

### Item 6: Blast Radius 架构判断（关键）

**Slug**: `blast-radius-analysis`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `additive_pattern` | 「附加模式」证据：Beryl 静态 precompile 集合 = Azul（`beryl() -> azul()`，provider.rs:166-168）；动态 precompile 是 **新增安装**（`install_with_observer` L194-203）而非替换或修改既有 precompile | `provider.rs:163-205` @ v1.1.1 |
| `fork_gate` | Fork 门控证据：动态安装条件为 `self.spec.upgrade() >= BaseUpgrade::Beryl`；`fork_activation` 中 Beryl timestamp 控制激活时间；`ForkCondition::Never` 可完全禁用 | `provider.rs:194`; `upgrade.rs:96-99` @ v1.1.1 |
| `address_space_isolation` | 地址空间隔离：B20Factory 使用固定地址 `B20FactoryStorage::ADDRESS`；B20 token 使用 `B20Variant::compute_address()` 从 (variant, sender, salt) 派生的确定性地址；`BerylLookup::lookup()` 仅对满足 variant 编码规则的地址返回 precompile | `provider.rs:556-563` tests; `lookup.rs:39-47` @ v1.1.1 |
| `storage_isolation` | 存储隔离：每个 precompile 使用自身地址作为 `sload`/`sstore` 的 `address` 参数（`Slot` 构造中的 `address` 字段）；precompile 内部 storage 不与 EOA/contract storage 冲突 | `types/slot.rs:20, 27, 44`; `evm.rs:158, 190` @ v1.1.1 |
| `existing_tx_flow` | 对既有交易流的影响分析：(1) 非 Beryl precompile 地址的 CALL/DELEGATECALL 不受影响（`contains()` → `inner.contains()` 仅查静态 precompile 表）；(2) 既有以太坊 precompile (ecrecover, sha256 等) 行为不变（azul/beryl 静态集合相同）；(3) Beryl precompile 的存储操作使用与普通合约相同的 EIP-2200/2929/3529 gas 语义 | `provider.rs:240-243`; EVM handler 路径分析 @ v1.1.1 |
| `activation_registry_guard` | ActivationRegistry 作为额外门控层：`ActivationRegistry::install_with_observer()` 接受 `activation_admin_address` 参数；可在 Beryl 激活后仍对特定功能进行运行时启/停 | `provider.rs:198-202` @ v1.1.1 |
| `blast_radius_conclusion` | 综合判断：Beryl precompiles 对既有交易状态转移的 blast radius 为**零或极低**，因为 (1) 静态 precompile 集合不变（beryl()=azul()）、(2) 4 个动态 precompile 仅通过新增安装引入、(3) fork 门控 + 地址空间编码确保不被意外触发、(4) 存储操作遵循标准 EVM gas 语义 | 综合 Items 1-5 |

**Acceptance Criteria**:
- 每个隔离层（fork 门控、地址空间、存储隔离、gas 语义一致性）均有代码行级证据
- blast radius 结论的论证链完整且可被 adversarial review 验证
- 明确标注唯一可能的影响路径（如有）及其缓解措施
- 结论分为「对既有 precompile 行为」和「对既有 contract/EOA 交易」两个维度

## Source Requirements

### Primary Sources

| Source | Type | Access | Notes |
|--------|------|--------|-------|
| `base/base` repo @ v1.1.1 | Code | 本地 `/Users/whisker/Work/src/networks/base/base` | 禁用裸 HEAD 引用；所有引用须带 tag+commit+path |
| `base/base` repo @ v1.1.0 | Code | 同上 | Sepolia 基线，用于交叉验证 |
| `crates/common/precompile-storage/` | Code | 本地 | Item 2 核心分析对象 |
| `crates/common/precompiles/` | Code | 本地 | Item 1/3/4/5 核心分析对象 |
| `crates/common/evm/` | Code | 本地 | Item 3/5 核心分析对象 |
| `crates/common/chains/` | Code | 本地 | Item 3 fork 定义 |
| `crates/common/precompile-macros/` | Code | 本地 | Item 1 宏系统 |

### Secondary Sources

| Source | Type | Access | Notes |
|--------|------|--------|-------|
| `base-beryl-vs-azul/outlines/beryl-scope-inventory.md` | Research | 同仓库 | Beryl scope 清单（引用不复述） |
| `base-beryl-vs-azul/research-sections/beryl-scope-inventory/` | Research | 同仓库 | 上游依赖 WHI-245 的产出 |
| PR #3389 (`9c3c3f54c`), #3119 (`213f13ce1`) — 直接祖先；PR #3342 经 backport #3426 (`526d5361c`) 落入 | Git | `git merge-base --is-ancestor` 逐一验证 | PR #3338 不是 v1.1.1 祖先（被 #3389 替代），不作为本研究证据源 |

### Source Integrity Rules

1. 所有代码引用必须标注 `v1.1.1 (01e732cd)` 或 `v1.1.0 (a3c3011b)` + commit + file path + line number
2. 禁止裸 HEAD 引用
3. PR# 必须附带对应 commit hash（已在 Code Baseline 表中确认）
4. 引用上游研究（WHI-245）时仅引用路径和结论，不复述内容

## Diagram Expectations

### Diagram 1: Precompile-Storage Provider 层次结构

**Type**: 层次关系图 (Hierarchy)
**Content**: `PrecompileStorageProvider` trait → `EvmPrecompileStorageProvider` 实现 → 内部依赖（`EvmInternals`, `GasParams`, `Gas`）→ EIP 关联（EIP-2200 stipend, EIP-2929 cold/hot, EIP-3529 refund）
**Format**: Mermaid classDiagram
**Purpose**: 展示 precompile storage 的 trait 抽象与生产实现之间的关系，以及各 EIP 的作用点

### Diagram 2: Fork Dispatch 与 Precompile 安装流程

**Type**: 流程图 (Flowchart)
**Content**: `BaseUpgrade` → `new_with_spec()` dispatch → 静态 precompile 构造链 (cancun→azul) → `install_with_observer()` 动态安装门控 (>= Beryl) → B20Factory / BerylLookup / PolicyRegistry / ActivationRegistry
**Format**: Mermaid flowchart
**Purpose**: 展示从 fork 判定到 precompile 完整集合的构建路径

### Diagram 3: Blast Radius 隔离层

**Type**: 分层架构图
**Content**: 四层隔离：L1=Fork 时间戳门控 → L2=`>= Beryl` 安装门控 → L3=地址空间编码隔离 → L4=存储地址隔离 → 结论：既有 tx 状态转移不受影响
**Format**: Mermaid flowchart (horizontal)
**Purpose**: 可视化 blast radius 论证的多层防护结构，为 WHI-249 信心分析提供图形化技术依据

## Expected Output Summary

Draft (`round-1.md`) 应包含：

1. **§1 Native Precompile 框架** — 宏系统架构、代码生成流程、slot packing 规则
2. **§2 Precompile-Storage Provider（重点）** — trait 层次、EIP-2200/2929/3529 实现、checkpoint 原子性、slot overflow 防护、非规范值拒绝、state gas 计费
3. **§3 EVM 集成与 Fork Dispatch** — `BaseUpgrade` 定义、eth_spec 映射、precompile 构造链、动态安装门控、`BerylLookup`、Builder 集成
4. **§4 Calldata 计价与 Beryl Precompile 集合** — calldata 定价机制、Beryl 完整 precompile 清单（静态 + 动态）、EIP-8130 scope boundary 说明
5. **§5 可观测性与 Metrics** — Observer trait、metrics observer、11 个 metric families、错误分类体系
6. **§6 Blast Radius 架构判断** — 四层隔离证据、结论与信心度评估
7. **Mermaid 图** — 3 个 diagram 内嵌

## Cross-References

| Reference | Path | Relation |
|-----------|------|----------|
| Beryl Scope Inventory | `base-beryl-vs-azul/outlines/beryl-scope-inventory.md` | 上游依赖 (WHI-245): Beryl 变更域分类基线 |
| Beryl Scope Research | `base-beryl-vs-azul/research-sections/beryl-scope-inventory/` | 上游依赖: PR/commit 清单与变更域 taxonomy |
| WHI-246 B20 Token 标准 | N/A (下游) | 本 issue 的 precompile 框架为 B20 业务逻辑提供基础设施 |
| WHI-248 合规与治理 | N/A (下游) | 本 issue 的 PolicyRegistry/ActivationRegistry 基础设施分析为其输入 |
| WHI-249 Beryl 信心分析 | N/A (下游) | 本 issue 的 blast radius 结论是其关键技术依据 |

## Quality Checklist (for Adversarial Review)

- [ ] 6 个 Research Items 均有代码行级引用（tag + commit + file path + line number）
- [ ] EIP-2200/2929/3529 三个 EIP 实现均有独立分析和代码证据
- [ ] Checkpoint/commit/revert 原子性模式有正确性论证
- [ ] Slot overflow `checked_add` 的覆盖面分析（additive slot 路径：slot/array/vec/set/bytes_like）及 mapping hashed derivation 说明
- [ ] Fork dispatch match 臂完整性验证（12 个变体无遗漏）
- [ ] 动态 precompile 安装的门控条件精确引用
- [ ] EIP-8130 scope boundary 明确标注（不在 v1.1.x 基线中）
- [ ] 11 个 metrics family 的完整清单
- [ ] Blast radius 结论的论证链完整且每一层有代码证据
- [ ] 所有 PR# 引用附带 commit hash
- [ ] 无裸 HEAD 引用
- [ ] Mermaid 图可渲染且信息准确
