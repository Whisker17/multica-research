# Research Outline: B20 合规 Token 标准体系代码深度分析

## Metadata

| Field | Value |
|-------|-------|
| project_slug | `base-beryl-vs-azul` |
| topic_slug | `b20-token-system` |
| multica_issue_id | `1e03500e-9646-4ca2-84fc-34bfc01301c1` |
| round | 1 |
| github_repo | `Whisker17/multica-research` |
| outline_path | `base-beryl-vs-azul/outlines/b20-token-system.md` |
| draft_path | `base-beryl-vs-azul/research-sections/b20-token-system/drafts/round-1.md` |
| final_path | `base-beryl-vs-azul/research-sections/b20-token-system/final.md` |

## Topic

B20 合规 Token 标准体系代码深度分析 — 对 Beryl 实际 ship 代码（v1.1.1 mainnet / v1.1.0 Sepolia）中 B20 原生 Token 标准的 commit/代码级实现分析。

## Scope

聚焦 Beryl ship 代码实现与审计加固，而非概念综述。引用但不复述既有研究（合规 Token 标准调研项目, issue `bc5cf45c`），仅补充 Beryl 实际 ship 的实现细节与演进差异。

### In-Scope

- B20 组件架构全景：Asset / Stablecoin 两 variant 的职责划分、trait 继承体系、角色模型
- B20Factory 工厂合约：确定性地址派生、keccak 计价、marker code hash 校验、nonpayable 守卫
- PolicyRegistry 与 policy-based transfer：ALLOWLIST/BLOCKLIST、sender/receiver/executor/mint-receiver 四维策略、激活门控
- ActivationRegistry 与激活治理：feature 激活机制、admin 地址配置（Sepolia/Mainnet/Zeronet/Devnet）、零地址拒绝
- 发行方控制能力：mint/burn、freeze/pause、burnBlocked（强制回收）、updateMultiplier（拒绝零乘子）
- B20Stablecoin 特性：decimals 硬编码 6 消除 zero-return 窗口
- 安全/审计加固线索：BOP/PSRC fix 体现的设计权衡
- ≥1 张 B20 组件/角色关系表

### Out-of-Scope

- B20 标准的概念设计与行业对比分析（已在 `bc5cf45c` 研究中覆盖）
- PolicyRegistry 的完整治理流程分析（归 WHI-247 合规与治理分析）
- ActivationRegistry 的治理决策流程（归 WHI-251 激活治理分析）
- Reth V2 性能影响（归 WHI-249）
- Cobalt 相关变更

## Code Baseline

| Network | Release Tag | Commit (解引用) | 用途 |
|---------|------------|-----------------|------|
| Mainnet | `v1.1.1` | `01e732cdbae0c624d652da9e608d7d3fe0f9c74b` | 主基线，多数分析锚定 |
| Sepolia | `v1.1.0` | `a3c3011b16dae73aaea455ec0a5ff614e65b7d0a` | Sepolia 特定检查（激活时间戳差异、admin 地址） |

**本地代码路径**: `/Users/whisker/Work/src/networks/base/base`

**Beryl 激活时间戳**:

| Network | Timestamp | Date |
|---------|-----------|------|
| Mainnet | `1782410400` | 2026-06-25 18:00 UTC |
| Sepolia | `1781805600` | 2026-06-18 18:00 UTC |
| Zeronet | `1780678800` | 2026-06-05 17:00 UTC |

**B20 Precompile 固定地址**:

| Precompile | 地址 | 文件 |
|------------|------|------|
| ActivationRegistry | `0x8453000000000000000000000000000000000001` | `crates/common/precompiles/src/activation/storage.rs` |
| B20Factory | `0xB20F000000000000000000000000000000000000` | `crates/common/precompiles/src/b20_factory/storage.rs` |
| B20 Token (动态) | `0xb200000000{variant}{9-byte-tail}` | `crates/common/precompiles/src/b20_factory/variant.rs` |

## Prior Research Reference

| 研究 | Issue | 关系 |
|------|-------|------|
| 合规 Token 标准调研 | `bc5cf45c` | 引用其 B20 标准设计分析结论，仅补充 Beryl ship 实现与加固增量 |
| Beryl 变更范围界定 (WHI-245) | `beryl-scope-inventory` | 引用其 PR/commit 清单中 B20 相关条目和变更域分类 |

## Research Items

### Item 1: B20 组件全景

**Slug**: `b20-component-overview`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `variant_architecture` | B20 两个 variant（Asset=0, Stablecoin=1）的 `B20Variant` enum 定义、地址前缀 `0xb2` + 9 zero bytes + discriminant byte 的结构化地址格式、`from_address` / `has_b20_prefix` 判定逻辑 | `v1.1.1 @ crates/common/precompiles/src/b20_factory/variant.rs` |
| `trait_hierarchy` | 共享 trait 体系：`Token` (核心接口) → `TokenAccounting` (存储抽象) + 能力 trait `Mintable` / `Burnable` / `Transferable` / `Configurable` / `Pausable` / `Permittable` / `RoleManaged`；`B20AssetToken` 与 `B20StablecoinToken` 各自的 trait impl | `v1.1.1 @ crates/common/precompiles/src/common/mod.rs` 导出表，`common/ops/*.rs` 各 trait 定义，`b20_asset/token.rs`，`b20_stablecoin/token.rs` |
| `roles_model` | 7 个内建角色：DefaultAdmin(0x0)、Mint、Burn、BurnBlocked、Pause、Unpause、Metadata；每个角色的 `keccak256` ID 常量；`AccessControl` 风格的 role admin 层级；`renounceLastAdmin` 终态设计；`grant_role` 对 `DEFAULT_ADMIN_ROLE` 的 resurrection guard | `v1.1.1 @ crates/common/precompiles/src/common/ops/roles.rs` |
| `storage_layout` | `B20CoreStorage` (共享存储)、`B20AssetStorage` (含 multiplier、decimals)、`B20StablecoinStorage` (含 currency)、`#[contract]` / `#[namespace]` macro 的命名空间隔离 | `v1.1.1 @ crates/common/precompiles/src/common/core_storage.rs`，`b20_asset/storage.rs`，`b20_stablecoin/storage.rs` |
| `historical_rename` | B20Security → B20Asset 重命名历史 (BOP-241, BOP-246)：`46f6f751d` rename commit，`ad4c7a4ae` feature rename commit；Default variant 移除 `7ee6c48f2` | `v1.1.1 @ git log` 相关 commit |

**Planned Table**: B20 组件/角色关系表

| 组件 | 职责 | 继承 Trait | 特有存储 | 特有操作 |
|------|------|-----------|---------|---------|
| Common (B20 核心) | ERC-20 兼容、角色管理、pause/permit | Token, TokenAccounting, RoleManaged, Mintable, Burnable, Transferable, Configurable, Pausable, Permittable | B20CoreStorage: balances, allowances, supply, roles, pause flags, nonces, policy slots | — |
| B20AssetToken | 通用资产 token，支持弹性精度和 multiplier | 继承全部 common traits | B20AssetStorage: multiplier, decimals(6-18), extra_metadata | updateMultiplier, scaled balance 转换, batch operations |
| B20StablecoinToken | 稳定币 token，固定 6 位精度 | 继承全部 common traits | B20StablecoinStorage: currency code | decimals() 硬编码返回 6 (BOP-349) |
| B20Factory | 工厂 singleton，创建 B20 token | — | 无独立存储 | createB20, isB20, isB20Initialized |
| PolicyRegistry | 策略注册表，管理 ALLOWLIST/BLOCKLIST | Policy, PolicyRegistry | policy 映射存储 | createPolicy, updateAllowlist/Blocklist |
| ActivationRegistry | 功能激活开关 | — | features mapping | activate, deactivate, isActivated |

**Planned Table**: B20 角色矩阵

| 角色 | ID (keccak256 hash 前缀) | 权限 | admin |
|------|--------------------------|------|-------|
| DefaultAdmin | `0x00...00` | 管理所有角色、updateSupplyCap | DefaultAdmin |
| Mint | `0x154c0081...` | mint, mintWithMemo | DefaultAdmin |
| Burn | `0xe97b1372...` | burn, burnWithMemo | DefaultAdmin |
| BurnBlocked | `0x7408fdc0...` | burnBlocked (强制销毁被冻结账户) | DefaultAdmin |
| Pause | `0x139c2898...` | pause | DefaultAdmin |
| Unpause | `0x265b220c...` | unpause | DefaultAdmin |
| Metadata | `0x6bd6b531...` | updateName, updateSymbol, updateContractURI | DefaultAdmin |

**Acceptance Criteria**:
- variant 地址格式完整描述，含 discriminant byte 位置与 keccak tail 计算
- trait 继承树完整列出，含 common → variant 的分层关系
- 7 个角色及其 ID 精确列出
- renounceLastAdmin 终态语义说明
- B20Security → B20Asset 重命名历史附 commit 引用

### Item 2: B20Factory

**Slug**: `b20-factory`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `address_derivation` | 确定性地址派生公式：`keccak256(abi_encode(creator, salt))` → 取前 9 字节作为 tail → `[0xb2, 0x00*9, variant_discriminant, tail[0..9]]` 组成 20 字节地址；`compute_address` 与 `compute_address_from_hash` 双路径设计（后者避免重复 hashing） | `v1.1.1 @ crates/common/precompiles/src/b20_factory/variant.rs:116-140` |
| `keccak_gas_metering` | Factory dispatch 中 `ctx.metered_keccak256` 先计价再调用 `create_b20_with_observer`，将 address_hash 作为参数传入避免 re-hash | `v1.1.1 @ crates/common/precompiles/src/b20_factory/dispatch.rs`; fix commit `b12d0c913` (#3369) |
| `marker_code_hash` | `isB20Initialized` 通过 `code_hash == FACTORY_MARKER_CODE_HASH` (`keccak256(0xef)` = `309b8896...`) 验证 token 是否由 factory 部署；factory 在创建时写入 `Bytecode::new_legacy(0xef)` 作为 marker stub | `v1.1.1 @ crates/common/precompiles/src/b20_factory/storage.rs:36-37,117-122`; fix commit `7c824c5ad` (#3382, BOP-311) |
| `nonpayable_guard` | 所有 factory selector 前置 `NonPayable` 检查，`call_value().is_zero()` 为 false 时 revert `IB20::NonPayable` | `v1.1.1 @ crates/common/precompiles/src/b20_factory/dispatch.rs`; 同理 b20_asset/b20_stablecoin dispatch 也有; fix commit `037ff71b3` (#3381), `7eb308d2a` (#3362) |
| `prefunded_create_cost` | 当 token 地址已有余额但无 code（预充值场景），`set_code` 前收取 create gas；`is_static` guard 阻止 static call 中的 `set_code` | `v1.1.1 @ crates/common/precompiles/src/b20_factory/storage.rs:91-93`; fix commits `0eef808b3` (#3371), `6a15a147d` (#3370, BOP-321) |
| `init_calls_window` | Factory 创建后通过 `with_caller(Self::ADDRESS)` 建立 privileged 窗口，执行 `initCalls` 数组中的 mint/supplyCap/contractURI 调用；窗口内操作 bypass role 和 policy 检查 | `v1.1.1 @ crates/common/precompiles/src/b20_factory/storage.rs:162-177` |
| `activation_gate` | 创建前调用 `ActivationRegistryStorage::ensure_activated(variant.activation_feature().id())` 检查 B20Asset 或 B20Stablecoin feature 是否已激活 | `v1.1.1 @ crates/common/precompiles/src/b20_factory/storage.rs:76-77` |
| `duplicate_prevention` | 创建时检查 `!info.is_empty_code_hash()` 防止重复部署到同一地址 | `v1.1.1 @ crates/common/precompiles/src/b20_factory/storage.rs:83-89` |
| `checkpoint_semantics` | 创建过程使用 `storage.checkpoint()` + `checkpoint.commit()` 事务语义：init 失败时全部回滚 | `v1.1.1 @ crates/common/precompiles/src/b20_factory/storage.rs:91,105`; related fix `21bb92a93` (#3387, BOP-359) |
| `strict_abi_decoding` | Factory dispatch 使用严格 ABI 解码拒绝 dirty words | fix commit `bddf7f879` (#3368) |

**Acceptance Criteria**:
- 地址派生公式精确描述，含具体 byte 位置
- keccak gas metering 的代码路径与 fix commit
- marker code hash 验证逻辑与 BOP-311 修复
- nonpayable 守卫的实施位置
- prefunded 场景的 gas 收取逻辑
- initCalls 特权窗口的安全边界

### Item 3: PolicyRegistry 与 policy-based transfer

**Slug**: `policy-registry-transfer`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `policy_types` | 四个内建 policy slot：`TransferSender` / `TransferReceiver` / `TransferExecutor` / `MintReceiver`，各自的 `keccak256` ID 常量 | `v1.1.1 @ crates/common/precompiles/src/common/policy_type.rs` |
| `allowlist_blocklist` | `PolicyType::ALLOWLIST` vs `PolicyType::BLOCKLIST` 语义：allowlist 中的账户被授权 (`is_authorized=true`)，blocklist 中的账户被拒绝 (`is_authorized=false`)；空 blocklist 允许所有人；`ALWAYS_ALLOW_ID` 和 `ALWAYS_BLOCK_ID` 内建策略 | `v1.1.1 @ crates/common/precompiles/src/policy/storage.rs`; `common/policy.rs` trait 文档 |
| `transfer_guard_chain` | Transfer 操作的 guard 顺序：pause → zero-address → sender policy → receiver policy → balance check → state mutation；`transfer_from` 额外添加 allowance → executor policy 检查 | `v1.1.1 @ crates/common/precompiles/src/common/ops/transferable.rs`; guard ordering test |
| `policy_delegation` | Token 通过 `policy_id(policy_scope)` 读取 per-token policy slot → 将实际授权判定委托给 `PolicyRegistry.is_authorized(policy_id, account)` | `v1.1.1 @ crates/common/precompiles/src/common/ops/guards.rs:53-66` |
| `activation_gate_calldata_classification` | BOP-378/PSRC-26 修复：PolicyRegistry dispatch 中将 calldata 在 activation gate 之前分类，view (read-only) call 绕过激活检查，仅 mutation call 需要 feature activated | `v1.1.1 @ crates/common/precompiles/src/policy/dispatch.rs:19-21,57-58`; fix commit `ce1b1df05` (#3421) |
| `policy_admin_model` | Policy 的 admin 管理：`stage_update_admin` → `finalize_update_admin` 两步转移；`renounce_admin` 永久放弃；零地址清除 pending | `v1.1.1 @ crates/common/precompiles/src/common/policy.rs` trait 定义 |
| `batch_size_cap` | BOP-391/PSRC-29 修复：policy registry 在 ABI 解码前强制执行批量大小上限 | fix commit `cb2f413ae` (#3453-backport 含此修复) |

**Acceptance Criteria**:
- 四个 policy slot 的 ID 精确列出
- ALLOWLIST/BLOCKLIST 语义清晰对比
- Transfer guard 顺序以代码行级证据支持
- BOP-378/PSRC-26 calldata 分类修复的设计逻辑
- BOP-391/PSRC-29 batch size cap 修复

### Item 4: ActivationRegistry / activation admin

**Slug**: `activation-registry`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `activation_features` | 三个 ActivationFeature：`PolicyRegistry` = `keccak256("base.policy_registry")`、`B20Stablecoin` = `keccak256("base.b20_stablecoin")`、`B20Asset` = `keccak256("base.b20_asset")`；各自的 storage key 与 feature test | `v1.1.1 @ crates/common/precompiles/src/activation/storage.rs:27-50` |
| `activation_mechanism` | `activate(feature)` 写入 `features.at_mut(&feature).write(true)` + emit `FeatureActivated`；`deactivate` 使用 `delete()` 清零 + emit `FeatureDeactivated`；deactivate 触发 EIP-3529 SSTORE refund | `v1.1.1 @ crates/common/precompiles/src/activation/storage.rs:97-126` |
| `admin_addresses` | 激活 admin 地址配置（ChainConfig.activation_admin_address）：Mainnet `0xcE3a3bEE7E72E2A24079f3c0Cb3b97740ED425A9`，Sepolia `0x5F43072722f59964d886CBb507F6a85ca0759D42`，Zeronet `0xF5969A85a555671EeD766C4ff0C61426AA626b11`，Devnet `0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc` | `v1.1.1 @ crates/common/chains/src/config.rs` MAINNET/SEPOLIA/ZERONET/DEVNET 常量 |
| `admin_address_update` | BOP-382 修复：更新 Sepolia 和 Mainnet 的 B20 activation admin 地址 | fix commit `996ebbf20` (#3450), backport `bd4d4ba53` (#3463) |
| `zero_address_rejection` | 零地址 caller 即使 admin 也配置为 Address::ZERO 仍被拒绝；防止 deposit tx (`msg.sender == 0x0`) 意外切换激活状态 | `v1.1.1 @ crates/common/precompiles/src/activation/storage.rs:84-87`; test `zero_address_caller_with_zero_admin_is_rejected` |
| `static_call_guard` | Activation mutation 前置 `is_static()` 检查，static call 中拒绝修改 | `v1.1.1 @ crates/common/precompiles/src/activation/storage.rs:78-80` |
| `idempotency_guard` | 重复 activate/deactivate revert `AlreadyActivated` / `FeatureNotActivated` | `v1.1.1 @ crates/common/precompiles/src/activation/storage.rs:90-101` |

**Acceptance Criteria**:
- 三个 feature 的 ID 与 canonical name 精确对应
- 四个网络的 admin 地址完整列出
- BOP-382 admin 地址更新的 commit 引用
- 零地址拒绝的安全设计意图明确
- activate/deactivate 的存储操作与事件发射

### Item 5: 发行方控制

**Slug**: `issuer-controls`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `mint_burn` | Mint：pause check → role check (Mint) → zero-address receiver reject → MintReceiver policy → supply cap check → balance/supply mutation → Transfer(0x0→to) event。Burn：pause check → role check (Burn) → balance check → balance/supply mutation → Transfer(from→0x0) event。Both 支持 WithMemo 变体 | `v1.1.1 @ crates/common/precompiles/src/common/ops/mintable.rs`, `common/ops/burnable.rs` |
| `burn_blocked` | BurnBlocked：pause check → BurnBlocked role → `ensure_blocked` (sender policy 未授权=被冻结) → burn_inner → emit BurnedBlocked event；允许发行方销毁被策略冻结账户的 token | `v1.1.1 @ crates/common/precompiles/src/common/ops/burnable.rs:67-78` |
| `pause_unpause` | 三个可暂停 feature：TRANSFER / MINT / BURN；bitmask 存储 `paused` 字段；`pause()` OR 合并位，`unpause()` AND NOT 清除位；空 feature 集 revert `EmptyFeatureSet`；Pause 需 `PAUSE_ROLE`，Unpause 需 `UNPAUSE_ROLE`（独立角色） | `v1.1.1 @ crates/common/precompiles/src/common/ops/pausable.rs`; `common/pausable_feature.rs` |
| `update_multiplier` | Asset-only 操作：`updateMultiplier(new_multiplier)` 修改余额缩放比例；拒绝零乘子 `new_multiplier.is_zero()` → revert `ZeroMultiplier`；需 DefaultAdmin 角色。Scaled balance 转换：`rawBalance * multiplier / WAD`（读），`scaledBalance * WAD / multiplier`（写）。初始 multiplier 存储为 0，读取时映射为 WAD (1:1) | `v1.1.1 @ crates/common/precompiles/src/b20_asset/token.rs:174-210`; factory storage line 33 `INITIAL_MULTIPLIER = U256::ZERO` |
| `supply_cap` | `updateSupplyCap`：需 DefaultAdmin 角色；`new_cap >= total_supply && new_cap <= B20_MAX_SUPPLY_CAP` (`u128::MAX`)；factory 创建时默认 cap = `B20_MAX_SUPPLY_CAP` | `v1.1.1 @ crates/common/precompiles/src/common/ops/configurable.rs:18-30`; `common/token_accounting.rs:8` |
| `metadata_updates` | `updateName` / `updateSymbol` / `updateContractURI`：需 Metadata 角色（不是 DefaultAdmin）；updateName 额外 emit `EIP712DomainChanged` (ERC-5267) | `v1.1.1 @ crates/common/precompiles/src/common/ops/configurable.rs:36-68` |
| `max_balance_cap` | B20 token 账户余额上限修复 | fix commits `56fd4a4cc` (#3464), `39ccde519` (cap b20 account balances) |

**Acceptance Criteria**:
- Mint/Burn guard 顺序精确描述
- BurnBlocked 的 `ensure_blocked` 逻辑说明
- Pause bitmask 存储与 feature 独立性
- Multiplier 的 WAD 精度转换公式
- 零乘子拒绝的代码位置
- Supply cap 范围约束

### Item 6: B20Stablecoin 特性

**Slug**: `b20-stablecoin-specifics`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `decimals_hardcode` | BOP-349/PSRC-27 修复：stablecoin `decimals()` 调用直接返回 `B20Variant::Stablecoin.decimals()` (固定 6)，不读取存储；消除 factory bootstrap 窗口中 `decimals` 存储尚未写入时返回 0 的问题 (zero-return window) | `v1.1.1 @ crates/common/precompiles/src/b20_stablecoin/dispatch.rs:132-137`; `b20_factory/variant.rs` `decimals()` 方法; fix commit `fb638bcbe` (#3385) |
| `asset_decimals_comparison` | 对比：Asset variant `decimals()` 从存储读取（6-18 范围，创建时写入），Stablecoin variant 硬编码返回 6。`B20Variant::decimals()` 返回 `Option<u8>` — Stablecoin `Some(6)`，Asset `None`，fix commit `3b68c8084` (#3345) | `v1.1.1 @ crates/common/precompiles/src/b20_factory/variant.rs:99-103` |
| `currency_code` | Stablecoin 特有 `currency` 字段，存储于 `B20StablecoinStorage` 命名空间；通过 `IB20Stablecoin::currency()` ABI 暴露；factory 创建时 `B20StablecoinEventParams` 编码 currency 到 `B20Created` 事件的 `variantParams` | `v1.1.1 @ crates/common/precompiles/src/b20_stablecoin/storage.rs`; factory storage 创建路径 |
| `stablecoin_init` | Stablecoin 创建参数 `B20StablecoinInit`：name, symbol, currency；与 Asset 的 `B20AssetInit`(name, symbol, decimals) 对比 | `v1.1.1 @ crates/common/precompiles/src/b20_stablecoin/` init 类型 |
| `currency_validation` | Factory 创建时验证 stablecoin currency 在 token existence check 之前 | fix commit `82552f3f0` |

**Acceptance Criteria**:
- BOP-349/PSRC-27 修复的完整代码路径（variant.rs + dispatch.rs）
- Zero-return window 问题的精确描述
- Asset vs Stablecoin decimals 处理对比
- Currency code 存储与 ABI 暴露

### Item 7: 安全/审计加固线索

**Slug**: `security-audit-hardening`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `bop_psrc_inventory` | 全部 BOP/PSRC 修复清单（在 v1.1.1 tag 可达范围内），按安全维度分类 | `v1.1.1 @ git log --grep="BOP\|PSRC"` |
| `gas_metering_fixes` | Gas 相关修复：keccak gas metering in factory (#3369)、gas deduction before sload (BOP-380 #3438)、prefunded create costs (#3371)、is_static guard (BOP-321 #3370) | 各 fix commit + 代码位置 |
| `abi_integrity_fixes` | ABI 相关修复：strict ABI decoding (#3368)、batch size cap before decode (BOP-391/PSRC-29)、stablecoin currency validation before existence check | 各 fix commit |
| `access_control_fixes` | 权限相关修复：role admin mutation guard for privileged calls (BOP-233 #3160)、executor policy in transferFrom regardless of allowance (BOP-227 #3150)、LastAdminCannotRenounce 终态保护 | 各 fix commit |
| `storage_integrity_fixes` | 存储相关修复：checkpoint_revert field restoration (BOP-359 #3387)、checkpoint_commit cleanup (BOP-350 #3406)、slot arithmetic checked-add migration (#3427)、CallerGuard hardening (#3404) | 各 fix commit |
| `view_function_availability` | View 函数在 feature disabled 时仍可用 (BOP-232 #3156)：policy registry calldata classification (BOP-378/PSRC-26)、b20 token dispatch view bypass | 各 fix commit |
| `design_tradeoffs` | 审计加固体现的设计权衡总结：(1) 预防性 vs 反应性安全（nonpayable guard, zero-address rejection）；(2) gas 精确性 vs 实现简单性（metered keccak, deduct-before-sload）；(3) 终态不可逆性（renounceLastAdmin, resurrection guard）；(4) 向后兼容性（decimals hardcode, view-function availability） | 综合分析，供 WHI-249 信心分析引用 |

**BOP/PSRC 分类表（计划）**:

| 维度 | BOP/PSRC IDs | 修复要点 | 相关 PR |
|------|-------------|---------|--------|
| Gas Metering | — | keccak pricing, sload ordering, create costs | #3369, #3438, #3371, #3370 |
| ABI Integrity | PSRC-29 | strict decode, batch cap | #3368, BOP-391 backport |
| Access Control | BOP-233, BOP-227 | privileged role guard, executor policy | #3160, #3150 |
| Storage Safety | BOP-359, BOP-350 | checkpoint revert/commit, checked arithmetic | #3387, #3406, #3427 |
| Activation UX | BOP-232, BOP-378/PSRC-26 | view bypass, calldata classification | #3156, #3421 |
| Address Derivation | BOP-311, BOP-229 | marker hash verification, zero on invalid | #3382, #3155 |
| Token Precision | BOP-349/PSRC-27 | stablecoin decimals hardcode | #3385 |
| Admin Governance | BOP-382 | activation admin address update | #3450 |

**Acceptance Criteria**:
- BOP/PSRC 清单完整，每条附 commit + PR 引用
- 按安全维度分类的表格
- 设计权衡总结明确可被 WHI-249 引用
- 涵盖从 gas metering 到 access control 到 storage integrity 的全谱

## Source Requirements

### Primary Sources

| Source | Type | Access | Notes |
|--------|------|--------|-------|
| `base/base` repo @ v1.1.1 | Code | 本地 `/Users/whisker/Work/src/networks/base/base` | 主基线，tag checkout |
| `base/base` repo @ v1.1.0 | Code | 同上 (切换 tag) | Sepolia 检查 |
| `crates/common/precompiles/src/` | Code | 同上 | B20 precompile 实现核心目录 |
| `crates/common/chains/src/config.rs` | Code | 同上 | ChainConfig 含 activation admin 地址 |
| 官方 B20 spec | Docs | `docs.base.org/base-chain/specs/upgrades/beryl/b20` | B20 规范定义 |

### Secondary Sources

| Source | Type | Access | Notes |
|--------|------|--------|-------|
| 合规 Token 标准调研 (issue `bc5cf45c`) | Research | Multica issue | 引用 B20 设计分析结论，不复述 |
| Beryl 变更范围界定 (WHI-245) | Research | `base-beryl-vs-azul/research-sections/beryl-scope-inventory/` | 引用 PR/commit 清单中 B20 条目 |
| BOP/PSRC commit messages | Code | `git log --grep="BOP\|PSRC" v1.1.1` | 审计加固线索 |

### Source Integrity Rules

1. 所有代码引用必须标注 `tag + commit + file path (+line number)`
2. 禁止裸 HEAD 引用
3. v1.1.1 commit 使用 `01e732cdb`，v1.1.0 使用 `a3c3011b1`
4. 引用既有研究时仅引用路径和结论，不复述内容
5. BOP/PSRC 票据号必须与 commit message 精确对应

## Diagram Expectations

### Diagram 1: B20 组件交互与继承关系图

**Type**: 组件关系图 (Component Diagram)
**Content**: B20Factory → (creates) B20AssetToken / B20StablecoinToken → (consults) PolicyRegistry → (gated by) ActivationRegistry 的调用关系；加上 Common Traits 层的 trait 继承关系
**Format**: Mermaid flowchart
**Purpose**: 一图展示 B20 体系的组件交互与 trait 分层

### Diagram 2: B20 Token 操作 Guard 链

**Type**: 流程图 (Flowchart)
**Content**: Transfer / Mint / Burn / BurnBlocked 四种操作的 guard 检查顺序：pause → role → address → policy → balance → state mutation
**Format**: Mermaid flowchart
**Purpose**: 展示 guard ordering 的安全设计，辅助理解 BOP/PSRC 修复的上下文

## Expected Output Summary

Draft (`round-1.md`) 应包含：

1. **§1 B20 组件全景** — variant 架构、trait 继承、角色模型 + 组件/角色关系表
2. **§2 B20Factory** — 确定性地址派生、keccak 计价、marker code hash、nonpayable、prefunded、initCalls
3. **§3 PolicyRegistry 与 policy-based transfer** — 四维策略、guard chain、calldata 分类 (BOP-378)
4. **§4 ActivationRegistry / activation admin** — 激活机制、admin 地址表、零地址拒绝
5. **§5 发行方控制** — mint/burn/burnBlocked/pause/multiplier/supplyCap/metadata
6. **§6 B20Stablecoin 特性** — decimals=6 硬编码、zero-return window、currency code
7. **§7 安全/审计加固线索** — BOP/PSRC 分类表、设计权衡、WHI-249 信心分析供料

## Cross-References

| Reference | Path / Issue | Relation |
|-----------|-------------|----------|
| 合规 Token 标准调研 | issue `bc5cf45c` | 引用 B20 标准设计分析，不复述 |
| Beryl 变更范围界定 | `base-beryl-vs-azul/research-sections/beryl-scope-inventory/` | 引用 PR/commit 清单中 B20 相关条目 |
| Downstream: WHI-247 | 合规与治理分析 | 本 issue PolicyRegistry/ActivationRegistry 信息为其输入 |
| Downstream: WHI-249 | 信心分析 | 本 issue §7 安全加固线索为其输入 |
| Downstream: WHI-251 | 激活治理分析 | 本 issue ActivationRegistry 信息为其输入 |

## Quality Checklist (for Adversarial Review)

- [ ] 7 个执行步骤均有对应 Research Item，每个 item 含 PR/commit + 文件路径 (+ 行号)
- [ ] B20 组件/角色关系表（≥1 张）含组件职责、继承 trait、特有存储、特有操作
- [ ] 角色矩阵表列出全部 7 个 B20 角色及其 keccak256 ID 前缀
- [ ] 地址派生公式精确（含 byte 位置）
- [ ] BOP/PSRC 分类表覆盖所有在 v1.1.1 可达的审计修复 commit
- [ ] 所有代码引用含 tag + commit + file path（无裸 HEAD）
- [ ] 引用既有 B20 研究 (issue `bc5cf45c`) 而非复述
- [ ] Stablecoin decimals=6 hardcode 的 zero-return window 问题有完整 fix 路径
- [ ] activation admin 地址四网全部列出
- [ ] guard ordering (pause → role → address → policy → balance) 有代码证据
- [ ] Mermaid 图可渲染且信息准确
- [ ] 无 Cobalt-only 内容混入
