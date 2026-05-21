# WHI-340: Tempo/Zones Source Code Deep Analysis

> **Issue**: WHI-340 — Tempo Zones 代码库深度分析
> **Date**: 2026-05-06 (revised 2026-05-07)
> **Status**: Revised per Review
> **Prerequisite**: WHI-339 (Documentation Research) — cross-referenced throughout
> **Data Sources**: Tempo L1 codebase (`v1.6.0`), Zones L2 codebase (`v0.1.0`)

---

## Table of Contents

1. [WHI-339 Claim → Code Reality 映射表](#1-whi-339-claim--code-reality-映射表)
2. [Codebase Structure Overview](#2-codebase-structure-overview)
3. [License and Reuse Constraints](#3-license-and-reuse-constraints)
4. [Commonware Simplex BFT Maturity Assessment](#4-commonware-simplex-bft-maturity-assessment)
5. [Reth SDK Extension Model Summary](#5-reth-sdk-extension-model-summary)
6. [Tempo L1 Core Analysis](#6-tempo-l1-core-analysis)
7. [Zones L2 Core Analysis](#7-zones-l2-core-analysis)
8. [Payment Lane Complete Code Analysis](#8-payment-lane-complete-code-analysis)
9. [Encrypted Deposits End-to-End Flow](#9-encrypted-deposits-end-to-end-flow)
10. [Validity Proofs Implementation Status](#10-validity-proofs-implementation-status)
11. [Enterprise Features Code-Level Findings](#11-enterprise-features-code-level-findings)
12. [TIP-20 / TIP-403 Implementation Characterization](#12-tip-20--tip-403-implementation-characterization)
13. [Component Reuse Decision Table](#13-component-reuse-decision-table)
14. [Mantle Reference Points](#14-mantle-reference-points)

---

## 1. WHI-339 Claim → Code Reality 映射表

> 本节将 WHI-339 文档研究中的关键断言与实际代码实现逐一对照，为 M2/M3 作者提供直接引用依据。

| WHI-339 断言 | 代码产物 | 已验证? | 结论 | M3 影响 |
|---|---|---|---|---|
| **主网状态："仅测试网 (截至 2026 年 5 月)"** | `chainspec/src/constants.rs:55-95` — Chain ID 4217 ("Presto") 主网已有 T1–T3 硬分叉激活时间戳 | ❌ 不正确 | 主网自 genesis 运行，T3 已于 2026-04-27 激活 | M3 设计应以 **生产环境已验证的系统** 为基准，而非概念验证 |
| **Validity Proofs："已确认的架构组成部分"** | `zones/batch.rs:12-14` — "Proof validation is currently **skipped**: both `verifierConfig` and `proof` are set to empty bytes"; `batch.rs:215-216` — `Bytes::new(), Bytes::new()` | ⚠️ 部分正确 | 基础设施已就绪（`no_std` 预编译、合约 proof slot、verifier 地址），但 **批次提交使用空 proof** | M3 gap 分析需注意 validity proof 存在"架构完成 vs 实现缺失"的差距 |
| **Payment Lane："单一分类机制"** | `primitives/src/transaction/envelope.rs:174` (`is_payment_v1`) + `:197` (`is_payment_v2`) | ❌ 不完整 | **双层分类**：v1 仅检查 `0x20C0` 地址前缀（共识层），v2 额外检查函数选择器白名单 + 禁止 access list（构建器层） | Mantle 若移植 Payment Lane 需同时实现两层分类 |
| **基础费用："固定，低于 $0.001"** | `chainspec/src/constants.rs:29` — `TEMPO_T1_BASE_FEE = 20,000,000,000` attodollars/gas | ✅ 基本正确 | 50,000 gas × 20B attodollars = $0.001 per TIP-20 transfer | 精确定价模型可作为 Mantle 企业定价参考 |
| **出块时间："~600ms"** | 代码中无硬编码出块时间；payload builder 有 500ms 构建循环 + 网络延迟 | ⚠️ 近似 | 目标约 600ms，但实际时间由 Commonware Simplex 共识轮次决定 | 性能基准需以实测数据为准 |
| **硬分叉数量："T0 → T4"** | `chainspec/src/hardfork.rs:164-192` — `Genesis, T0, T1, T1A, T1B, T1C, T2, T3, T4, T5` | ❌ 不完整 | 实际 10 个硬分叉变体（含子版本 T1A/T1B/T1C），T5 已规划 | 表明协议迭代速度快，M3 设计需考虑兼容性窗口 |
| **Zone 隔离："数据不在 L1 上发布"** | `engine.rs` — 所有状态本地保存；`zonemonitor.rs` — 仅提交 `BatchData`（区块转换、存款队列转换、提款队列哈希） | ✅ 正确 | Zone 是 validium 模型：L1 仅存储状态承诺，不存储交易数据 | Zone 隔离模型是企业隐私的关键参考 |
| **Simplex BFT 共识："基于 BLS12-381 门限签名"** | `crates/commonware-node/` — 12,702 行集成代码；`crates/dkg-onchain-artifacts/` — DKG 仪式产物 | ✅ 正确 | Commonware Simplex BFT 深度集成，含 DKG 仪式、epoch 管理、双运行时隔离 | Commonware 成熟度评估见第 4 节 |

---

## 2. Codebase Structure Overview

### 2.1 Tempo L1 Workspace (26 crates — verified)

Source: `/Users/whisker/Work/src/networks/tempo/tempo/Cargo.toml` (lines 9-36)

```
Workspace version: 1.6.0, Edition 2024, MSRV 1.93.0

bin/tempo                  — Main node binary
bin/tempo-bench            — Benchmark binary
bin/tempo-sidecar          — Sidecar process

crates/alloy               — Alloy network/provider extensions (tempo-alloy)
crates/chainspec           — TempoChainSpec, hardfork definitions, gas constants
crates/commonware-node     — Commonware Simplex BFT engine integration
crates/commonware-node-config — ⚠️ NOT in original list — Commonware node configuration
crates/consensus           — TempoConsensus (HeaderValidator, FullConsensus)
crates/contracts           — Predeployed contract ABIs, addresses, bindings
crates/dkg-onchain-artifacts — DKG ceremony on-chain artifacts
crates/e2e                 — End-to-end testing utilities
crates/evm                 — TempoEvmConfig
crates/eyre                — Custom error hook
crates/ext                 — Plugin extension system
crates/faucet              — Testnet faucet RPC module
crates/node                — TempoNode, TempoFullNode type alias
crates/payload/builder     — TempoPayloadBuilder (block building)
crates/payload/types       — TempoPayloadTypes, TempoPayloadAttributes
crates/precompiles         — All native precompile implementations
crates/precompiles-macros  — ⚠️ NOT in original list — Procedural macros for precompiles
crates/primitives          — TempoHeader, TempoTxEnvelope, TempoPrimitives
crates/revm                — Reth-REVM integration customization
crates/telemetry-util      — Prometheus/OTEL metrics
crates/transaction-pool    — Custom transaction pool with Payment Lane support
crates/validator-config    — Validator configuration types
xtask                      — Build automation
```

**Corrections to original crate list**:
- ✅ Added `crates/commonware-node-config` (not in original)
- ✅ Added `crates/precompiles-macros` (not in original)
- ✅ Added `xtask` (not in original)

### 2.2 Zones L2 Workspace (5 crates — verified)

Source: `/Users/whisker/Work/src/networks/tempo/zones/Cargo.toml` (lines 9-16)

```
Workspace version: 0.1.0, Edition 2024, MSRV 1.93.0

bin/tempo-zone             — Zone node binary
crates/precompiles         — Zone-specific precompiles (Chaum-Pedersen, AES-GCM, ECIES)
crates/primitives          — ZoneHeader, Zone ABI primitives (no_std)
crates/tempo-zone          — Core zone library (engine, l1, rpc, batch, withdrawals)
crates/rpc                 — Private zone RPC server (auth, handlers, proxy)
xtask                      — Build automation
```

### 2.3 Cross-Repository Dependencies

Zones depends on Tempo via git at commit `bb08bb905b6ee13fafe046aa9531aea2cdf60651`:

| Zones imports from Tempo | Purpose |
|---|---|
| `tempo-alloy` | Network types, provider extensions |
| `tempo-chainspec` | Chain spec, hardfork definitions |
| `tempo-consensus` | Consensus types (default-features disabled) |
| `tempo-contracts` | Contract ABI bindings |
| `tempo-evm` | EVM configuration |
| `tempo-node` | Node types |
| `tempo-payload-types` | Payload types |
| `tempo-precompiles` | Base precompile infrastructure |
| `tempo-precompiles-macros` | Precompile proc macros |
| `tempo-primitives` | Core primitives (with reth, serde, bincode, codec features) |
| `tempo-revm` | REVM integration |
| `tempo-transaction-pool` | Transaction pool types |

Source: `zones/Cargo.toml` lines 81-97

**Version divergence**: Zones uses slightly older dependencies:
- revm v37 (Tempo uses v38)
- alloy 2.0.0 (Tempo uses 2.0.4)
- commonware 2026.2.0 (Tempo uses 2026.4.0)
- Reth at rev `0b33057` (Tempo uses `38c627c`)

### 2.4 Dependency Map (Simplified)

```
                  ┌──────────────────────────────────────────┐
                  │              Tempo L1 (v1.6.0)           │
                  │                                          │
                  │  primitives ─► chainspec ─► evm          │
                  │      │              │          │          │
                  │      ▼              ▼          ▼          │
                  │  contracts ─► precompiles ─► node        │
                  │                     │                     │
                  │  consensus ◄─ commonware-node             │
                  │                                          │
                  │  transaction-pool ─► payload/builder      │
                  └──────────────┬───────────────────────────┘
                                 │ git dependency
                  ┌──────────────▼───────────────────────────┐
                  │              Zones L2 (v0.1.0)           │
                  │                                          │
                  │  primitives (no_std) ─► precompiles      │
                  │         │                   │            │
                  │         ▼                   ▼            │
                  │  tempo-zone (engine, l1, batch, ...)     │
                  │         │                                │
                  │         ▼                                │
                  │  rpc (auth, handlers, proxy)             │
                  └──────────────────────────────────────────┘
```

---

## 3. License and Reuse Constraints

### 3.1 许可证总览

| 组件 | 许可证 | LICENSE 文件 | Cargo.toml 声明 | 复用影响 |
|---|---|---|---|---|
| **Tempo L1** | MIT OR Apache-2.0 | `LICENSE-MIT` + `LICENSE-APACHE` | `license = "MIT OR Apache-2.0"` | ✅ 宽松双许可，允许 fork、修改、商业使用 |
| **Zones L2** | MIT OR Apache-2.0 | `LICENSE-MIT` + `LICENSE-APACHE` | `license = "MIT OR Apache-2.0"` | ✅ 同上 |
| **Commonware** | MIT OR Apache-2.0 | GitHub repo 双许可 | crates.io 版本 + Tempo 通过 `[patch.crates-io]` 固定 git rev | ✅ 宽松许可，可作为库依赖或 fork |
| **Reth** | MIT OR Apache-2.0 | Reth 上游许可 | Git 依赖 `paradigmxyz/reth` | ✅ 宽松许可 |
| **revm** | MIT | revm 上游许可 | Crates.io 依赖 | ✅ 宽松许可 |

### 3.2 复用约束分析

**法律层面**：Tempo、Zones、Commonware 均采用宽松开源许可（MIT/Apache-2.0），从法律角度允许：
- 直接 fork 并修改代码
- 将代码作为库依赖引入
- 提取设计模式作为 blueprint 重新实现
- 商业产品中使用

**技术层面的实际约束**（重于法律约束）：
1. **Rust/Reth 生态锁定**：Tempo 全栈 Rust，Mantle 现为 Go (op-geth)。直接代码复用需要 Reth 迁移或跨语言重写。
2. **Reth SDK 版本耦合**：Tempo 锁定特定 Reth commit (`38c627c`)，Zones 锁定另一 commit (`0b33057`)。Reth 内部 API 尚不稳定，升级可能需要大量适配。
3. **Commonware 深度集成**：Tempo 的共识层与 Commonware 运行时深度耦合（见第 4 节），无法仅提取共识逻辑而不引入整个 Commonware 栈。
4. **Precompile 协议依赖**：TIP-20/TIP-403 是 protocol-level precompiles，依赖 Tempo 的自定义存储提供者和硬分叉门控（见第 12 节），无法直接移植为 EVM smart contracts。

**结论**：许可证不构成障碍。主要约束来自技术栈差异（Rust vs Go）和架构耦合深度。

---

## 4. Commonware Simplex BFT Maturity Assessment

### 4.1 项目概况

| 维度 | 数据 |
|---|---|
| 仓库 | `github.com/commonwarexyz/monorepo` |
| Stars | ~559 |
| 许可证 | MIT OR Apache-2.0 |
| 最新版本 | v2026.4.0 (2026-04-14) |
| 稳定性体系 | 分级制 (ALPHA → EPSILON)，核心原语（consensus, cryptography）标记为较高稳定性 |
| Crate 数量 | 15 个核心原语 + 9 个示例 |
| Tempo 使用方式 | Git 依赖，锁定 commit `2a7dd42` |

### 4.2 Tempo 集成深度

Tempo 的 `crates/commonware-node/` 包含 **12,702 行 Rust 代码**（不含测试），组织为以下子模块：

| 子模块 | 行数 | 功能 |
|---|---|---|
| `consensus/engine.rs` | 638 | Simplex BFT 引擎主循环，管理投票/证书/视图切换 |
| `consensus/application/actor.rs` | 1,074 | 应用层 actor，处理区块提案/验证/确认 |
| `consensus/block.rs` | 367 | 区块类型定义和序列化 |
| `dkg/manager/actor/mod.rs` | 1,627 | DKG 仪式 actor |
| `dkg/manager/actor/state.rs` | 1,695 | DKG 状态管理（BLS12-381 密钥份额） |
| `subblocks.rs` | 881 | 子区块处理（Payment Lane 特有） |
| `epoch/` | ~729 | Epoch/验证者集合轮换 |
| `executor/` | ~789 | 区块执行器 actor |
| `feed/` | ~835 | 交易传播管道 |
| `peer_manager/` | ~522 | P2P 节点管理 |

### 4.3 成熟度评估

**生产可用性指标**：

| 指标 | 状态 | 说明 |
|---|---|---|
| **主网部署** | ✅ 已验证 | Tempo 主网（Chain ID 4217）自 genesis 运行，T3 已于 2026-04-27 激活 |
| **DKG 仪式** | ✅ 已实现 | 完整的 BLS12-381 分布式密钥生成，含链上产物管理 |
| **双运行时隔离** | ✅ 设计优秀 | 共识和执行分别运行在独立 Tokio 运行时，防止执行负载影响共识 |
| **Tempo 测试覆盖** | ⚠️ 中等 | `consensus/src/lib.rs` 包含 19 个 `#[test]`，commonware-node 本身集成测试有限 |
| **上游文档** | ⚠️ 有限 | commonware.xyz 有 API 文档，但无独立的 Simplex BFT 协议规范文档 |
| **API 稳定性** | ⚠️ 不确定 | 使用 calendar versioning (2026.x.0)，无 semver 稳定性承诺 |
| **独立使用者** | ❓ 未知 | 除 Tempo 外，未发现其他公开的生产用户 |
| **Crates.io 发布** | ✅ 是 | `commonware-*` crates 有 2026.4.0 版本；Tempo 通过 `[patch.crates-io]` 固定 PR #3588 之后的 git commit |

**总体判断**：Commonware Simplex BFT 是一个 **由 Tempo 团队深度使用的内部框架**，已通过主网验证。但其独立成熟度（脱离 Tempo 使用）有以下风险：
1. **单一生产用户**：仅 Tempo 主网验证，缺少多样化的生产环境测试
2. **紧耦合风险**：Commonware 的 runtime、p2p、broadcast 作为一个整体被引入，无法选择性使用单一 crate
3. **Calendar versioning**：缺少 semver 风格的稳定性保证
4. **Tempo 使用 git patch**：Tempo 未直接使用 crates.io 发布版，而是固定 PR #3588 之后的 git commit，说明其生产集成依赖特定上游修订

**对 Mantle 的建议**：将 Commonware/Simplex BFT 视为 **设计参考 (blueprint)**，而非可直接引入的生产库。如需 BFT 共识，建议评估更成熟的替代品（如 CometBFT/Tendermint、Narwhal-Tusk/Bullshark），或在 OP Stack 框架内实现定制共识。

---

## 5. Reth SDK Extension Model Summary

> Tempo 对 Reth 的定制 **不是** 简单的 ExEx（Execution Extension）单点扩展，而是一个覆盖 Reth 全栈的深度定制模式。

### 5.1 定制层次

```
┌───────────────────────────────────────────────────────────────┐
│                    Tempo Custom Node Stack                     │
│                                                               │
│  Layer 1: Custom Primitives (tempo-primitives)                │
│    └─ TempoTxEnvelope, TempoHeader, TempoPrimitives           │
│    └─ 自定义交易类型 0x76 + P256/WebAuthn 签名               │
│                                                               │
│  Layer 2: Custom ChainSpec (tempo-chainspec)                  │
│    └─ TempoChainSpec, TempoHardfork                           │
│    └─ 10 个 Tempo 特定硬分叉 + Ethereum Osaka 在 genesis 激活│
│                                                               │
│  Layer 3: Custom EVM Config (tempo-evm, tempo-revm)           │
│    └─ TempoEvmConfig                                          │
│    └─ Attodollar 计价的 gas 费用 + optional_fee_charge        │
│                                                               │
│  Layer 4: Custom Precompiles (tempo-precompiles)              │
│    └─ 12 个原生预编译（TIP-20, TIP-403, DEX, Keychain 等）   │
│    └─ 动态查找 + 硬分叉门控 + delegatecall 禁止              │
│                                                               │
│  Layer 5: Custom Payload Builder (tempo-payload-builder)      │
│    └─ 三车道区块构建（System/Payment/General）                │
│    └─ gas 预算分配 + Payment Lane 分类                        │
│                                                               │
│  Layer 6: Custom Consensus (tempo-consensus + commonware)     │
│    └─ Simplex BFT 验证 + subblock 架构                       │
│    └─ 双 Tokio 运行时隔离                                    │
│                                                               │
│  Layer 7: Custom Transaction Pool (tempo-transaction-pool)    │
│    └─ Payment Lane 路由 + v2 分类                             │
│                                                               │
│  Layer 8: Node Assembly (tempo-node)                          │
│    └─ NodeBuilder<TempoNode> + TempoAddOns                    │
│    └─ 将以上所有层组合为 TempoFullNode                        │
│                                                               │
│  Source: crates/node/src/node.rs:14 — FullNodeComponents,     │
│          NodeTypes, NodeAddOns trait 实现                      │
└───────────────────────────────────────────────────────────────┘
```

### 5.2 关键洞察

1. **全栈定制 vs 插件扩展**：Reth 的 `NodeBuilder` 允许替换从原语到共识的每一层。Tempo 选择了全栈定制路径，而非 ExEx（仅扩展后处理）或 ExExHead（仅扩展头部验证）。
2. **类型安全组合**：通过 Rust 泛型（`NodeTypes`、`EngineTypes`、`PayloadTypes`），Reth 确保自定义组件的类型一致性。`TempoNode` 实现 `NodeTypes` 提供 `TempoPrimitives` + `TempoChainSpec` + `TempoPayloadTypes`。
3. **向前兼容风险**：Reth 内部 API 快速迭代，Tempo 锁定特定 commit。每次 Reth 升级都可能需要适配。
4. **对 Mantle 的启示**：如果 Mantle 从 op-geth (Go) 迁移到 Reth (Rust)，Tempo 的模式提供了完整参考。但这是一个 **重大架构决策**，意味着放弃 OP Stack 的 Go 生态系统。更实际的路径可能是将 Tempo 的设计理念（如 Payment Lane、预编译注册表）移植到 op-geth 或 op-reth，而非照搬其 Reth 定制模式。

---

## 6. Tempo L1 Core Analysis

### 6.1 Node Architecture

**Entry point**: `bin/tempo/src/main.rs`

**TempoFullNode type alias** (`crates/node/src/lib.rs`, lines 25-29):
```rust
type TempoFullNodeTypes = RethFullAdapter<DatabaseEnv, TempoNode>;
type TempoNodeAdapter = NodeAdapter<TempoFullNodeTypes>;
pub type TempoFullNode = FullNode<TempoNodeAdapter, TempoAddOns<TempoFullNodeTypes>>;
```

The node composes Reth's `NodeBuilder` pattern with custom components:
- `TempoNode` — implements `NodeTypes` for Reth, providing `TempoPrimitives`, `TempoChainSpec`, and `TempoPayloadTypes`
- `TempoAddOns` — additional node services (consensus, telemetry, extensions)
- Uses `reth-node-builder` with `DatabaseEnv` (MDBX) as the storage backend

**Module organization** (`crates/node/src/lib.rs`, lines 15-19):
```rust
pub mod engine;
pub mod node;
pub mod rpc;
pub mod telemetry;
pub use tempo_consensus as consensus;
pub use tempo_evm as evm;
pub use tempo_primitives as primitives;
```

### 6.2 Consensus Module

#### TempoConsensus
Located in `crates/consensus/src/` — implements `reth_consensus::HeaderValidator` and `FullConsensus` traits.

Key validation: Verifies block headers carry valid Commonware Simplex BFT certificates, validator set membership, and `shared_gas_limit` / `general_gas_limit` field validity.

#### Commonware Integration
Located in `crates/commonware-node/src/` — bridges Commonware Simplex BFT engine with Reth's execution layer.

Dependencies (from `Cargo.toml`, lines 215-225):
```
commonware-broadcast = "2026.4.0"
commonware-codec = "2026.4.0"
commonware-consensus = "2026.4.0"
commonware-cryptography = "2026.4.0"
commonware-p2p = "2026.4.0"
commonware-runtime = "2026.4.0"
commonware-storage = "2026.4.0"
```

Key architectural decision: **dual-runtime design** — Reth execution runs on one Tokio runtime, Commonware consensus runs on a separate Tokio runtime, isolated to prevent execution load from affecting consensus performance.

#### DKG Artifacts (`crates/dkg-onchain-artifacts`)
Handles BLS12-381 threshold signature ceremony artifacts. DKG (Distributed Key Generation) produces the shared keys used by validators for Simplex BFT threshold signing.

#### Validator Config (`crates/validator-config`)
Manages validator set configuration, including precompile-based on-chain storage (`ValidatorConfig` at `0xCCCCCCCC00000000000000000000000000000000`, `ValidatorConfigV2` at `0xCCCCCCCC00000000000000000000000000000001`).

### 6.3 Custom Transaction Types (`crates/primitives`)

#### TempoTxEnvelope (`crates/primitives/src/transaction/envelope.rs`, lines 41-61)

```rust
pub enum TempoTxEnvelope {
    Legacy(Signed<TxLegacy>),          // type 0x00
    Eip2930(Signed<TxEip2930>),        // type 0x01
    Eip1559(Signed<TxEip1559>),        // type 0x02
    Eip7702(Signed<TxEip7702>),        // type 0x04
    AA(AASigned),                      // type 0x76 — Tempo Transaction
}
```

**Notable**: EIP-4844 (blob transactions) intentionally excluded — returns `UnsupportedTransactionType` (line 71). Tempo is a payments chain, not a data availability layer.

#### TEMPO_TX_TYPE_ID = 0x76

Source: `crates/primitives/src/transaction/tempo_transaction.rs`

Constants (lines 23-26):
```rust
pub const TEMPO_TX_TYPE_ID: u8 = 0x76;
pub const SECP256K1_SIGNATURE_LENGTH: usize = 65;
pub const P256_SIGNATURE_LENGTH: usize = 130;
pub const MAX_WEBAUTHN_SIGNATURE_LENGTH: usize = 2048;
```

Signature type detection is **length-based** (not selector-based):
| Length | Type | Algorithm |
|--------|------|-----------|
| 65 bytes | secp256k1 | Standard ECDSA recovery |
| 130 bytes | P256 | NIST P-256 (WebAuthn/Passkey) |
| Variable (max 2KB) | WebAuthn | Browser-native WebAuthn assertion |
| Variable | Keychain | Delegated via AccountKeychain |

#### Gas Price Scaling (`crates/primitives/src/transaction/mod.rs`, lines 30-46)

```rust
pub const TEMPO_GAS_PRICE_SCALING_FACTOR: U256 = uint!(1_000_000_000_000_U256); // 10^12

pub fn calc_gas_balance_spending(gas_limit: u64, gas_price: u128) -> U256 {
    U256::from(gas_limit)
        .saturating_mul(U256::from(gas_price))
        .div_ceil(TEMPO_GAS_PRICE_SCALING_FACTOR)
}
```

Conversion: attodollars (10^-18 USD) → microdollars (10^-6 USD) via division by 10^12.

#### TIP-20 Payment Prefix (`crates/primitives/src/transaction/envelope.rs`, line 16)

```rust
pub const TIP20_PAYMENT_PREFIX: [u8; 12] = hex!("20C000000000000000000000");
```

### 6.4 Precompile Contracts (`crates/precompiles`)

All precompile addresses (`crates/contracts/src/precompiles/mod.rs`, lines 28-45):

| Precompile | Address | Notes |
|---|---|---|
| **TIP20Token** | `0x20C0...` prefix (any matching address) | Per-token precompile |
| **TIP20Factory** | `0x20FC000000000000000000000000000000000000` | Token deployment |
| **TIP403Registry** | `0x403C000000000000000000000000000000000000` | Compliance policies |
| **TipFeeManager** | `0xFEEC000000000000000000000000000000000000` | Fee configuration |
| **StablecoinDEX** | `0xDEC0000000000000000000000000000000000000` | Fee AMM + exchange |
| **NonceManager** | `0x4E4F4E4345000000000000000000000000000000` | 2D nonce storage ("NONCE" in ASCII) |
| **ValidatorConfig** | `0xCCCCCCCC00000000000000000000000000000000` | Validator config v1 |
| **ValidatorConfigV2** | `0xCCCCCCCC00000000000000000000000000000001` | Validator config v2 |
| **AccountKeychain** | `0xAAAAAAAA00000000000000000000000000000000` | Key delegation |
| **AddressRegistry** | `0xFDC0000000000000000000000000000000000000` | T3+ only |
| **SignatureVerifier** | `0x5165300000000000000000000000000000000000` | T3+ only |
| **pathUSD** | `0x20C0000000000000000000000000000000000000` | First TIP-20 token (default fee token) |

**Precompile lookup** (`crates/precompiles/src/lib.rs`, lines 118-144):
- Dynamic lookup function registered via `set_precompile_lookup()`
- TIP-20 tokens matched by prefix (`address.is_tip20()`)
- `AddressRegistry` and `SignatureVerifier` gated behind T3 hardfork
- All precompiles enforce **direct-call-only** — delegatecall returns `DelegateCallNotAllowed`

**Precompile infrastructure** (`crates/precompiles/src/lib.rs`, lines 152-177):
The `tempo_precompile!` macro enforces:
1. Direct-call check (no delegatecall)
2. Storage context setup via `EvmPrecompileStorageProvider`
3. Gas metering for calldata decoding

### 6.5 Hardfork System (`crates/chainspec`)

#### Hardfork Sequence (`crates/chainspec/src/hardfork.rs`, lines 164-192)

```rust
TempoHardfork {
    Genesis,  // Baseline
    T0,       // Default until T1 activates
    T1,       // Expiring nonce transactions
    T1A,      // Removes EIP-7825 per-transaction gas limit
    T1B,      // (minor fixes)
    T1C,      // Switches to Osaka precompiles
    T2,       // Compound transfer policies (TIP-1015)
    T3,       // AddressRegistry + SignatureVerifier
    T4,       // Consensus context in header (TIP-1031)
    T5,       // (planned)
}
```

#### ⚠️ Critical Correction: Mainnet IS Live

Source: `crates/chainspec/src/constants.rs`, lines 55-95

The WHI-339 documentation report stated "testnet only." **The code reveals Tempo mainnet (chain ID 4217, codename "Presto") is LIVE with real activation timestamps:**

| Hardfork | Mainnet Block | Mainnet Timestamp | Date |
|---|---|---|---|
| Genesis | 0 | 0 | Genesis |
| T0 | 0 | 0 | Genesis |
| T1 | 4,494,230 | 1,770,908,400 | Feb 12, 2026 15:00 UTC |
| T1A | 4,494,230 | Same as T1 | Feb 12, 2026 |
| T1B | 6,253,936 | 1,771,858,800 | Feb 23, 2026 15:00 UTC |
| T1C | 8,967,991 | 1,773,327,600 | Mar 12, 2026 15:00 UTC |
| T2 | 12,286,033 | 1,774,965,600 | Mar 31, 2026 14:00 UTC |
| T3 | — | 1,777,298,400 | Apr 27, 2026 14:00 UTC |
| T4 | — | — | Not yet scheduled |
| T5 | — | — | Not yet scheduled |

Testnet "Moderato" (chain ID 42431) runs an accelerated hardfork schedule.

#### Gas Constants (`crates/chainspec/src/constants.rs`, lines 6-52)

| Constant | Value | Notes |
|---|---|---|
| `TEMPO_T0_BASE_FEE` | 10,000,000,000 attodollars | 10 billion attodollars/gas |
| `TEMPO_T1_BASE_FEE` | 20,000,000,000 attodollars | ~$0.001 per TIP-20 transfer |
| `TEMPO_T1_GENERAL_GAS_LIMIT` | 30,000,000 | 30M gas non-payment cap |
| `TEMPO_T1_TX_GAS_LIMIT_CAP` | 30,000,000 | 30M per-tx cap |

Base fee economic breakdown (from code comment, lines 23-28):
```
50,000 gas × 20 billion attodollars/gas = 1 quadrillion attodollars
1 quadrillion ÷ 10^12 = 1,000 microdollars = $0.001 = 0.1 cents
```

#### Hardfork Feature Changes (`crates/chainspec/src/hardfork.rs`)

| Method | Pre-T1 | T1+ | Notes |
|---|---|---|---|
| `base_fee()` | 10B attodollars | 20B attodollars | Doubled at T1 |
| `general_gas_limit()` | Dynamic | Fixed 30M | Simplified at T1 |
| `tx_gas_limit_cap()` | EIP-7825 Osaka (16.7M) | 30M | Raised at T1A |
| `gas_existing_nonce_key()` | Cold SLOAD + warm reset | + 2 warm SLOADs | Extended at T2 |
| `gas_new_nonce_key()` | Cold SLOAD + SSTORE set | + 2 warm SLOADs | Extended at T2 |

### 6.6 EVM Configuration (`crates/evm`)

Key EVM customizations:
- Pre-T1C: Prague precompiles; T1C+: Osaka precompiles
- All standard Ethereum hardforks (through Osaka) activated at genesis
- revm v38 with `optional_fee_charge` feature enabled
- Custom fee handling for attodollar-denominated gas pricing

---

## 7. Zones L2 Core Analysis

### 7.1 Zone Node Architecture

**Core library**: `crates/tempo-zone/src/lib.rs` — 28 modules organized around:

| Module | Purpose |
|---|---|
| `engine` | L1-event-driven block production (ZoneEngine) |
| `l1` | L1 subscription and deposit extraction (L1Subscriber) |
| `l1_state` | L1 state cache, TIP-403 policy mirroring |
| `batch` | Batch data construction and submission |
| `builder` | Payload builder (block construction) |
| `withdrawals` | Withdrawal store and L1 processor |
| `zonemonitor` | Zone L2 → L1 batch submission monitor |
| `rpc` | Private RPC server integration |
| `evm` | Zone-specific EVM configuration |
| `precompiles` | Zone precompile registration |
| `nonce_keys` | Sequencer nonce key management |

**ZoneSequencerConfig** (`crates/tempo-zone/src/lib.rs`, lines 53-74):
```rust
pub struct ZoneSequencerConfig {
    pub portal_address: Address,      // ZonePortal on L1
    pub l1_rpc_url: String,
    pub retry_connection_interval: Duration,
    pub withdrawal_poll_interval: Duration,
    pub outbox_address: Address,      // ZoneOutbox on L2
    pub inbox_address: Address,       // ZoneInbox on L2
    pub tempo_state_address: Address, // TempoState predeploy
    pub zone_rpc_url: String,
    pub zone_poll_interval: Duration,
    pub batch_interval: Duration,
}
```

#### NoopConsensus + NoopNetworkBuilder — Why No P2P?

Because a Zone is a **single-sequencer validium**. The sequencer is the sole block producer and executor — there is no peer discovery, block propagation, or consensus negotiation needed. Block production is event-driven from L1, not consensus-driven. This is explicitly noted in the `node.rs` module.

### 7.2 ZoneEngine — L1 Event-Driven Block Production

**Source**: `crates/tempo-zone/src/engine.rs` (295 lines, complete)

#### Architecture (from code comment, lines 9-30):

```
L1Subscriber ──enqueue──► DepositQueue ──notify──► ZoneEngine
                               │                       │
                               │                   1. peek queue → L1 block
                               │                   2. build ZonePayloadAttributes
                               │                   3. FCU w/ payload attributes
                               │                       │
                               │               reth payload service
                               │                       │
                               │               4. build payload
                               │                       │
                               │                  ZoneEngine
                               │               5. resolve payload
                               │               6. newPayload
                               │               7. FCU (update head)
                               │                       │
                               ◄── confirm ◄───────────┘
```

#### ZoneEngine struct (`engine.rs`, lines 71-92):

```rust
pub struct ZoneEngine {
    chain_spec: Arc<TempoChainSpec>,
    to_engine: ConsensusEngineHandle<ZonePayloadTypes>,
    payload_builder: PayloadBuilderHandle<ZonePayloadTypes>,
    deposit_queue: DepositQueue,
    last_header: SealedHeader<TempoHeader>,
    fee_recipient: Address,
    sequencer_key: k256::SecretKey,        // For ECIES decryption
    portal_address: Address,               // HKDF context
    policy_provider: PolicyProvider,        // TIP-403 cache
}
```

#### Instant Finality (`engine.rs`, lines 153-156):

```rust
fn forkchoice_state(&self) -> ForkchoiceState {
    ForkchoiceState::same_hash(self.last_header.hash())
}
```

**head = safe = finalized always**, confirmed in code.

#### 1:1 L1→L2 Block Mapping (`engine.rs`, lines 210-293):

The `advance()` method:
1. Locks zone block timestamp to L1 block's timestamp (line 215-216)
2. Propagates `timestamp_millis_part` for sub-second precision (line 217)
3. Builds `ZonePayloadAttributes` with L1 data
4. Sends FCU with attributes → builds payload → submits via `newPayload`
5. Only confirms L1 block removal from queue after successful `newPayload`
6. Runs policy cache GC: `self.policy_provider.cache().advance(l1_num_hash.number)` (line 282)

### 7.3 L1Subscriber — Deposit Extraction

**Source**: `crates/tempo-zone/src/l1.rs`

The `L1Subscriber` (lines 87-98):
```rust
pub struct L1Subscriber {
    config: L1SubscriberConfig,
    local_state: Arc<dyn LocalTempoStateReader>,
    deposit_queue: DepositQueue,
    tracked_tokens: Vec<Address>,           // TIP-403 tracked tokens
    tip403_metrics: Tip403Metrics,
    subscriber_metrics: L1SubscriberMetrics,
}
```

**Transport auto-detection**: Supports both WebSocket (subscription) and HTTP (polling at 500ms) — auto-detected from URL scheme (line 39).

**Events extracted from L1 blocks**:
- `ZonePortal::DepositMade` — regular deposits
- `ZonePortal::EncryptedDepositMade` — encrypted deposits
- `ZonePortal::TokenEnabled` — new token bridging
- `ZonePortal::SequencerTransferStarted` / `SequencerTransferred` — sequencer rotation
- `ZonePortal::BounceBack` — deposit refunds
- TIP-403 policy events (from tracked token contracts)

### 7.4 Bridge & Asset Flow

#### ZonePortal Contract (on Tempo L1)

ABI defined in `crates/primitives/src/abi.rs`, lines 114-259.

Key functions:
| Function | Purpose |
|---|---|
| `deposit(token, to, amount, memo)` | Regular deposit L1→L2 |
| `depositEncrypted(token, amount, keyIndex, encrypted)` | Encrypted deposit |
| `submitBatch(tempoBlockNumber, recentTempoBlockNumber, blockTransition, depositQueueTransition, withdrawalQueueHash, verifierConfig, proof)` | Batch submission with proof |
| `processWithdrawal(withdrawal, remainingQueue)` | Process L1 withdrawal |
| `enableToken(token)` | Enable TIP-20 token for bridging |
| `setSequencerEncryptionKey(x, yParity, popV, popR, popS)` | Set ECIES key with proof-of-possession |

#### ZoneOutbox Contract (on Zone L2)

ABI at `crates/primitives/src/abi.rs`, lines 266-311:
```solidity
function requestWithdrawal(
    address token, address to, uint128 amount, bytes32 memo,
    uint64 gasLimit, address fallbackRecipient,
    bytes calldata data, bytes calldata revealTo
) external;

function finalizeWithdrawalBatch(
    uint256 count, uint64 blockNumber,
    bytes[] calldata encryptedSenders
) external returns (bytes32 withdrawalQueueHash);
```

#### TempoState Predeploy (on Zone L2, `0x1C00...0000`)

ABI at `crates/primitives/src/abi.rs`, lines 318-343. Provides zone's view of Tempo L1:
- `tempoBlockHash()`, `tempoBlockNumber()`, `tempoStateRoot()`
- `tempoTimestamp()`, `tempoTimestampMillis()`
- `generalGasLimit()`, `sharedGasLimit()`
- `finalizeTempo(bytes header)` — system call to advance L1 view

#### TempoStateReader Precompile (on Zone L2)

At `crates/primitives/src/abi.rs`, lines 351-356:
```solidity
function readStorageAt(address account, bytes32 slot, uint64 blockNumber) external view returns (bytes32);
function readStorageBatchAt(address account, bytes32[] slots, uint64 blockNumber) external view returns (bytes32[]);
```

This enables the Zone to **read arbitrary Tempo L1 contract storage** — the foundation for TIP-403 policy mirroring.

#### Sequencer Background Tasks

**Zone Monitor** (`crates/tempo-zone/src/zonemonitor.rs`):
- Polls Zone L2 for new blocks
- Extracts `WithdrawalRequested` events
- Aggregates multiple zone blocks into single L1 batch (lines 9-15)
- Submits `submitBatch()` with multi-block batching
- Supports EIP-2935 direct mode and ancestry mode (lines 17-25)

**Withdrawal Processor** (`crates/tempo-zone/src/withdrawals.rs`):
- Polls ZonePortal withdrawal queue on L1
- Calls `processWithdrawal()` for each pending withdrawal
- Shared `L1 provider + nonce manager` with Zone Monitor (prevents nonce collision)

**WithdrawalStore** (`withdrawals.rs`, lines 89-91):
```rust
pub struct WithdrawalStore {
    batches: BTreeMap<u64, Vec<abi::Withdrawal>>,
}
```
- In-memory store grouped by batch index
- L1 portal queue stores only hash chains; sequencer keeps original data

### 7.5 Compliance Layer — TIP-403 Mirroring

**Source**: `crates/tempo-zone/src/l1_state/` (5 sub-modules)

| Module | Purpose |
|---|---|
| `cache` | L1StateCache — in-memory cache of L1 contract storage slots |
| `precompile` | TempoStateReader — DynPrecompile for `readStorageAt` calls |
| `provider` | L1StateProvider — cache-first, RPC-fallback reader |
| `tip403` | PolicyCache, PolicyProvider, SharedPolicyCache |
| `versioned` | Versioned entries with per-block GC |

**SharedPolicyCache GC** (`engine.rs`, line 282):
```rust
self.policy_provider.cache().advance(l1_num_hash.number);
```

Per-block garbage collection — only the engine drives this, ensuring policy lookups for in-flight blocks return correct results. The subscriber must not advance past blocks the engine hasn't processed.

**Compliance check during encrypted deposit preparation** (`engine.rs`, lines 187-202):
```rust
async fn prepare_l1_block(&self, l1_block: L1BlockDeposits) -> eyre::Result<PreparedL1Block> {
    l1_block.prepare(
        &self.sequencer_key,
        self.portal_address,
        &self.policy_provider,  // TIP-403 check here
    ).await
}
```

### 7.6 Private RPC Authentication

**Source**: `crates/rpc/src/` (12 sub-modules)

#### Authorization Token Format

From `crates/rpc/src/auth/token.rs`:

```rust
// Token format: <signature><version:1><zoneId:4><chainId:8><issuedAt:8><expiresAt:8>
const TEMPO_ZONE_RPC_MAGIC: [u8; 32] = b"TempoZoneRPC" (left-padded to 32 bytes);

pub const X_AUTHORIZATION_TOKEN: &str = "x-authorization-token";
pub const DEFAULT_MAX_AUTH_TOKEN_VALIDITY_SECS: u64 = 2_592_000; // 30 days
```

**AuthorizationToken struct** (lines 47-62):
```rust
pub struct AuthorizationToken {
    pub version: u8,          // Must be 0
    pub zone_id: u32,         // 0 = unscoped (valid for any zone)
    pub chain_id: u64,
    pub issued_at: u64,       // Unix seconds
    pub expires_at: u64,      // Unix seconds
    pub signature: Vec<u8>,   // secp256k1 signature
    pub digest: B256,         // keccak256 of packed message
}
```

**RPC modules** (`crates/rpc/src/`):
- `auth` — Token parsing and signature verification
- `filter` — Per-account privacy redactions
- `handlers` — RPC method implementations
- `proxy` — Proxy to standard Reth RPC
- `subscription` — WebSocket subscription support
- `policy` — Policy-aware method filtering

### 7.7 Zone Precompiles & SP1 Compatibility

**Source**: `crates/precompiles/src/lib.rs` (critical `no_std` annotation at line 20)

```rust
#![cfg_attr(not(feature = "std"), no_std)]
```

**Documentation** (lines 1-18):
> "This crate is `no_std` compatible so these precompiles can run inside the SP1 prover guest (RISC-V) as well as in the zone node."

Zone precompile addresses:

| Precompile | Address | Purpose |
|---|---|---|
| `ChaumPedersenVerify` | `0x1C00000000000000000000000000000000000100` | DLOG equality proof |
| `AesGcmDecrypt` | Defined in `aes_gcm.rs` | AES-256-GCM decryption |
| `ZoneTokenFactory` | Defined in `tip20_factory.rs` | Zone-side TIP-20 factory |
| `ZoneTip403ProxyRegistry` | Defined in `tip403_proxy.rs` | TIP-403 read-only proxy |
| `ZoneTip20Token` | Per-address (prefix match) | Zone TIP-20 with policy |

**Zone primitives are also `no_std`** (`crates/primitives/src/lib.rs`, line 6):
> "This crate is `no_std` compatible so it can be used inside SP1 (RISC-V) guest programs and TEE enclaves, as well as in the host-side prover."

---

## 8. Payment Lane Complete Code Analysis

### 8.1 Payment Classification

**Two-level classification** (`crates/primitives/src/transaction/envelope.rs`):

**v1 — Consensus level** (lines 174-182):
```rust
pub fn is_payment_v1(&self) -> bool {
    match self {
        Self::Legacy(tx) => is_tip20_call(tx.tx().to.to()),
        Self::Eip1559(tx) => is_tip20_call(tx.tx().to.to()),
        Self::AA(tx) => tx.tx().calls.iter().all(|call| is_tip20_call(call.to.to())),
        // ... other types
    }
}
```

**v2 — Builder level, stricter** (lines 197-226):
```rust
pub fn is_payment_v2(&self) -> bool {
    // Same prefix check PLUS:
    // - calldata must match recognized payment selector
    // - NO access lists or authorization lists attached
    // - AA transactions must have at least one call
}
```

v1 is enforced at consensus (block validation); v2 is enforced by the transaction pool and payload builder to prevent DoS of the payment lane. A future TIP will enshrine v2 at protocol level.

### 8.2 Gas Allocation

**General gas limit** (`crates/chainspec/src/hardfork.rs`, lines 101-109):
```rust
fn general_gas_limit_at(&self, timestamp: u64, gas_limit: u64, shared_gas_limit: u64) -> u64 {
    self.tempo_hardfork_at(timestamp)
        .general_gas_limit()
        .unwrap_or_else(|| (gas_limit - shared_gas_limit) / 2)
}
```

- Pre-T1: `(gas_limit - shared_gas_limit) / 2` (dynamic)
- T1+: Fixed 30M gas (`TEMPO_T1_GENERAL_GAS_LIMIT`)

**Shared gas divisor** (`crates/consensus/src/lib.rs`, line 37-38):
```rust
/// shared_gas_limit = block_gas_limit / TEMPO_SHARED_GAS_DIVISOR
pub const TEMPO_SHARED_GAS_DIVISOR: u64 = 10;
```

**Payload builder enforcement** (`crates/payload/builder/src/lib.rs`, lines 303-310):
```rust
let shared_gas_limit = block_gas_limit / TEMPO_SHARED_GAS_DIVISOR;
// The remaining `shared_gas_limit` is reserved for validator subblocks.
let non_shared_gas_limit = block_gas_limit - shared_gas_limit;
let general_gas_limit = chain_spec.general_gas_limit_at(
    timestamp, block_gas_limit, shared_gas_limit,
);
```

Gas lane enforcement 发生在 payload builder 的交易打包循环中（`lib.rs:450-492`）：
- 非支付交易的总 gas 不得超过 `non_shared_gas_limit`（line 465）
- 非支付交易的 gas 不得超过 `general_gas_limit`（line 483）
- 超限交易被跳过并记录指标（`exceeds_non_shared_gas_limit` / `exceeds_general_gas_limit`）

### 8.3 Three-Lane Architecture

| Lane | Priority | Gas Budget | Transaction Types |
|---|---|---|---|
| **System** | Highest | Start/end of block | Reward registry, validator config updates |
| **Payment** | Medium | `shared_gas_limit` (remaining after general) | TIP-20 transfers with `0x20C0` prefix |
| **General** | Lowest | `general_gas_limit` (30M fixed at T1+) | Smart contracts, DeFi, everything else |

**Anti-noisy-neighbor guarantee**: Once `general_gas_limit` budget is consumed, non-payment transactions are blocked even if total `gas_limit` has remaining capacity. Payment transactions continue filling the shared capacity.

### 8.4 Fee Economics

From `crates/chainspec/src/constants.rs`:

| Parameter | Value | Economic Meaning |
|---|---|---|
| T1 base fee | 20 billion attodollars/gas | ~$0.001 per TIP-20 transfer |
| Scaling factor | 10^12 | Converts attodollars → microdollars (TIP-20 units) |
| TIP-20 decimals | 6 | Microdollar precision |
| Standard transfer gas | ~50,000 | Typical TIP-20 transfer cost |

---

## 9. Encrypted Deposits End-to-End Flow

### 9.1 Architecture

```
┌─────────┐    ECIES encrypt    ┌──────────┐  DepositMade event  ┌────────────┐
│ Depositor│ ──────────────────► │ L1 Portal │ ─────────────────► │ L1Subscriber│
│          │  (to, memo)         │           │                    │            │
└─────────┘                     └──────────┘                    └─────┬──────┘
                                                                      │ enqueue
                                                                      ▼
                                                               ┌──────────┐
                                                               │ ZoneEngine│
                                                               │ prepare() │
                                                               └─────┬────┘
                                                                     │ ECIES decrypt
                                                                     │ CP proof generate
                                                                     │ TIP-403 check
                                                                     ▼
                                                               ┌──────────┐
                                                               │ ZoneInbox │
                                                               │ system tx │
                                                               └──────────┘
                                                                     │
                                                               On-chain verify:
                                                               - ChaumPedersen proof
                                                               - AES-GCM decrypt
                                                               - Credit to recipient
```

### 9.2 Step-by-Step Implementation

#### Step 1: Client-side Encryption

From `crates/precompiles/src/ecies.rs`, lines 143-154:

```rust
pub struct EncryptedDepositArgs {
    pub eph_pub_x: B256,           // Ephemeral public key x-coordinate
    pub eph_pub_y_parity: u8,      // Y parity (0x02 or 0x03)
    pub ciphertext: Vec<u8>,       // AES-256-GCM encrypted (to || memo || padding)
    pub nonce: [u8; 12],           // AES-GCM nonce
    pub tag: [u8; 16],             // AES-GCM authentication tag
}
```

Plaintext format: `[address(20)] [memo(32)] [padding(12)]` = 64 bytes total (line 22).

#### Step 2: Sequencer-side ECDH + Proof

`compute_ecdh_proof()` (`ecies.rs`, lines 67-99):
1. Recover ephemeral public key from (x, y_parity)
2. ECDH: `sharedSecretPoint = privSeq × ephemeralPub`
3. Generate Chaum-Pedersen proof: proves `privSeq` links both `pubSeq` and `sharedSecretPoint` without revealing `privSeq`

`decrypt_deposit()` (`ecies.rs`, lines 111-138):
1. Compute ECDH proof (always succeeds if ephemeral key is valid)
2. HKDF-SHA256: derive AES key from shared secret + context
3. AES-256-GCM decrypt with tag verification
4. Parse plaintext: `to = plaintext[0..20]`, `memo = plaintext[20..52]`
5. On decryption failure: returns `None` → refund path (tokens mint to sender instead)

#### Step 3: On-chain Verification

**ChaumPedersenVerify precompile** (`crates/precompiles/src/chaum_pedersen.rs`, lines 27-66):

Address: `0x1C00000000000000000000000000000000000100`
Gas: 6,000 (two EC multiplications + hashing)

Verification equations:
```
R1 = s*G - c*pubSeq
R2 = s*ephemeralPub - c*sharedSecretPoint
c' = keccak256(G, ephemeralPub, pubSeq, sharedSecretPoint, R1, R2)
Check: c == c'
```

This proves the sequencer correctly derived the shared secret without revealing their private key.

#### Step 4: TIP-403 Compliance Check

During `prepare_l1_block()`, before building the zone block, the engine checks TIP-403 policies on the decrypted recipient address. If the recipient is blacklisted, the deposit is bounced back.

### 9.3 Authenticated Withdrawals

`encrypt_authenticated_withdrawal()` (`ecies.rs`, lines 160-198):
- Encrypts `(sender, tx_hash)` using `revealTo` public key
- Output: `compressed_ephemeral_pubkey(33) || nonce(12) || ciphertext(52) || tag(16)` = 113 bytes
- Uses separate HKDF label: `"authenticated-withdrawal-aes-key"`
- Allows selective cross-zone sender attribution without on-chain sender disclosure

---

## 10. Validity Proofs Implementation Status

### 10.1 Code Evidence

**SP1/TEE preparation is real and substantive**:

1. **Zone precompiles are `no_std`** (`crates/precompiles/src/lib.rs`, line 20):
   > "This crate is `no_std` compatible so these precompiles can run inside the SP1 prover guest (RISC-V)"

2. **Zone primitives are `no_std`** (`crates/primitives/src/lib.rs`, line 6):
   > "can be used inside SP1 (RISC-V) guest programs and TEE enclaves"

3. **Batch submission accepts proof bytes** (`crates/primitives/src/abi.rs`, lines 221-229):
   ```solidity
   function submitBatch(
       ...,
       bytes calldata verifierConfig,
       bytes calldata proof      // <-- proof slot exists
   ) external;
   ```

4. **Portal has a `verifier` field** (`abi.rs`, line 198):
   ```solidity
   function verifier() external view returns (address);
   ```

### 10.2 Current Status: Proof Slot Present, Proof Generation Not Implemented

From `crates/tempo-zone/src/batch.rs`, lines 12-14:
> "Proof validation is currently **skipped**: both `verifierConfig` and `proof` are set to empty bytes"

And at `batch.rs`, lines 143-145:
> "`verifierConfig` and `proof` are set to empty bytes — the verifier contract must be configured to accept empty proofs."
> `// TODO: pass real proof bytes once proof generation is implemented.`

Confirmed at `batch.rs`, lines 215-216:
```rust
Bytes::new(),  // verifierConfig — empty
Bytes::new(),  // proof — empty
```

This confirms:
- The proof **slot** exists in the contract interface
- The current implementation sends **empty proof bytes** (`bytes("")`)
- SP1/TEE proof generation logic is **not yet implemented** in the Zones codebase
- However, the `no_std` compatibility of precompiles and primitives is **deliberate preparation** for running inside SP1 RISC-V guest

### 10.3 Assessment

| Aspect | Status |
|---|---|
| ABI/contract proof slot | ✅ Implemented |
| Precompile SP1 compatibility | ✅ Implemented (`no_std`) |
| Primitives SP1 compatibility | ✅ Implemented (`no_std`) |
| Proof generation (SP1 guest) | ❌ Not yet in codebase |
| Proof verification (L1 verifier) | ❌ Not yet in codebase |
| TEE attestation | ❌ Not yet in codebase |

**Correction to WHI-339**: The documentation states validity proofs are "confirmed architectural component." The code shows the infrastructure is prepared but the actual proving/verification is not yet implemented — batches are submitted with empty proofs. This is consistent with Zones being v0.1.0 (early development).

---

## 11. Enterprise Features Code-Level Findings

### 11.1 Access Control — TIP-403 Registry

**Precompile**: `TIP403Registry` at `0x403C000000000000000000000000000000000000`

Implementation in `crates/precompiles/src/tip403_registry.rs`. Key features:
- Policy types: always-reject (0), always-allow (1), whitelist, blacklist
- Compound transfer policies (T2+, TIP-1015): separate sender/recipient rules
- `isAuthorized(policyId, user)` — stateless authorization check
- `transferAuthorized()` — enforced by every TIP-20 transfer

**Zone mirroring**: `ZoneTip403ProxyRegistry` in `zones/crates/precompiles/src/tip403_proxy.rs` — read-only proxy that reads policies from L1 via `TempoStateReader`.

### 11.2 Privacy Implementation — Three Layers

| Layer | Implementation | Code Location |
|---|---|---|
| **Zone Isolation** | No data published on L1; sequencer is sole viewer | `engine.rs` — all state is local |
| **Encrypted Deposits** | ECIES + Chaum-Pedersen + AES-GCM | `ecies.rs`, `chaum_pedersen.rs`, `aes_gcm.rs` |
| **Authenticated RPC** | Per-account scoping via signed tokens | `crates/rpc/src/auth/token.rs` |

Additional privacy measures in code:
- Fixed 100,000 gas per user-facing TIP-20 operation (prevents gas side-channel)
- `CREATE` and `CREATE2` blocked in Zones
- RPC timing side-channel mitigation: 100ms minimum response time
- Sanitized blocks: `transactions` array emptied, `logsBloom` zeroed

### 11.3 Identity Management — AccountKeychain

**Precompile**: `AccountKeychain` at `0xAAAAAAAA00000000000000000000000000000000`

Implementation in `crates/precompiles/src/account_keychain.rs`. Features:
- Root key → access key delegation with scoped permissions
- `KeyAuthorization` struct (`crates/primitives/src/transaction/key_authorization.rs`):
  - `CallScope` — allowlisted contracts and function selectors
  - `TokenLimit` — per-token spending limits with periodic resets
  - Expiry timestamps
- P256 (WebAuthn/Passkey) as first-class signature scheme
- Signature detection by length (65 = secp256k1, 130 = P256, variable = WebAuthn)

### 11.4 Compliance Audit

**Sequencer full visibility**: The sequencer has complete access to all zone state:
- Decrypts all encrypted deposits
- Sees all transactions in plaintext
- Can read any account balance
- Policy enforcement happens in the sequencer's prepare step

**Audit data flow**:
1. L1 events fully logged (ZonePortal events are public on Tempo L1)
2. Batch submissions are public on L1 (block transitions, deposit queue transitions)
3. Withdrawal processing is public on L1
4. Zone-side: sequencer retains all transaction data in-memory (WithdrawalStore)

**No explicit audit export module** in code — this would be a custom integration point.

### 11.5 Deployment Flexibility

**ZoneFactory** pattern visible in the ABI — `createZone()` enables programmatic Zone deployment from L1. The portal's `genesisTempoBlockNumber()` and `zoneId()` functions support multi-zone operation.

The `zone_id` field in the RPC auth token (`token.rs`, line 52) with `0 = unscoped` supports cross-zone authentication.

### 11.6 Performance Configuration

| Parameter | Default | Impact |
|---|---|---|
| `general_gas_limit` | 30M (fixed at T1+) | Caps non-payment throughput |
| `shared_gas_limit` | Block-level parameter | Payment lane capacity |
| L1 poll interval | 500ms | L1 block subscription latency |
| Batch interval | Configurable | L1 tx frequency reduction |
| Withdrawal poll interval | Configurable | L1 withdrawal processing speed |
| L1 fetch concurrency | Configurable | Backfill parallelism |

---

## 12. TIP-20 / TIP-403 Implementation Characterization

> Review 要求明确 TIP-20 和 TIP-403 是 protocol-level precompiles 还是可移植的 EVM smart contracts。本节给出明确结论。

### 12.1 实现性质：Protocol-Native Precompiles

**TIP-20 和 TIP-403 均为 protocol-level precompiles，不是普通 EVM smart contracts。** 它们：

1. **以预编译地址注册**：通过 `set_precompile_lookup()` 在 EVM 初始化时注册，不经过合约部署流程
2. **使用协议级存储**：通过 `EvmPrecompileStorageProvider` trait 直接读写 EVM 状态，而非通过 SLOAD/SSTORE 操作码
3. **受硬分叉门控**：功能集随 Tempo 硬分叉版本变化（如 T2 引入 compound policies，T3 引入 permit/nonces）
4. **禁止 delegatecall**：所有 Tempo 预编译强制 `direct-call-only`（`precompiles/src/lib.rs:152-177`）

### 12.2 关键文件和接口

**TIP-20 Token (`crates/precompiles/src/tip20/`)**:

| 文件 | 行数 | 功能 |
|---|---|---|
| `mod.rs` | ~2,700+ | 核心代币逻辑（余额、转账、铸造/销毁） |
| `dispatch.rs` | ~900+ | ABI 选择器分发 + 硬分叉门控 |
| `rewards.rs` | ~750+ | 代币奖励分发逻辑 |

关键依赖链：
```
TIP-20 Token → EvmPrecompileStorageProvider (protocol-level storage)
            → TempoHardfork (hardfork gating, e.g. T2 for permit, T3 for rewards changes)
            → TIP403Registry (compliance check on every transfer)
            → tempo-chainspec (gas constants, base fee)
```

**TIP-403 Registry (`crates/precompiles/src/tip403_registry/`)**:

| 文件 | 行数 | 功能 |
|---|---|---|
| `mod.rs` | ~1,300+ | 策略管理（创建/更新/查询）+ 授权检查 |
| `dispatch.rs` | ~120+ | ABI 选择器分发 + 硬分叉门控 |

关键依赖链：
```
TIP-403 Registry → EvmPrecompileStorageProvider (protocol-level storage)
                → TempoHardfork (T2 for compound policies)
                → tempo-chainspec (hardfork activation)
```

### 12.3 可移植性评估

| 维度 | 评估 | 说明 |
|---|---|---|
| **接口可移植性** | ✅ 高 | ERC-20 兼容 ABI，策略注册/查询 ABI 清晰 |
| **逻辑可移植性** | ⚠️ 中等 | 核心业务逻辑（白名单/黑名单、compound policies）可提取 |
| **实现可移植性** | ❌ 低 | 深度依赖 Tempo 的 precompile storage provider、硬分叉门控、gas 模型 |
| **Solidity 重写可行性** | ⚠️ 有限制 | 可用 Solidity 实现类似功能，但性能不同（precompile gas < Solidity gas），且 TIP-20 的 gas 固定化（100,000 gas per operation，防 timing 侧信道）需协议级支持 |

**对 Mantle 的结论**：建议将 TIP-20/TIP-403 的 **接口设计和策略模型** 作为 blueprint，在 Mantle 上通过以下两种路径实现：
1. **Solidity system contract 路径**：将策略逻辑实现为 predeploy system contracts（类似 OP Stack 的 L2ToL1MessagePasser），不需要协议层修改
2. **Precompile 路径**：如果性能要求高或需要防止 gas 侧信道，则需要在 op-geth/op-reth 中实现自定义 precompile

---

## 13. Component Reuse Decision Table

> 逐组件给出 borrow（直接复用代码）/ build-equivalent（重新实现等价物）/ blueprint（仅借鉴设计）/ avoid（不建议参考）的明确建议。

| 组件 | 实现位置 | 许可证 | 复用模式 | Mantle 技术栈差距 | 风险 | 建议 |
|---|---|---|---|---|---|---|
| **Payment Lane 分类** | `primitives/src/transaction/envelope.rs:174-226` | MIT/Apache-2.0 | **Blueprint** | Go vs Rust；OP Stack 无 lane 概念 | 中 — 需修改 op-geth 交易池和区块构建器 | 以地址前缀 + 选择器的无状态分类为设计参考，在 OP Stack 中实现 gas lane 隔离 |
| **Payment Lane 构建器** | `payload/builder/src/lib.rs:303-492` | MIT/Apache-2.0 | **Blueprint** | Go 重写 | 中 — 涉及区块构建核心路径 | 提取 `shared_gas_limit` / `general_gas_limit` / `non_shared_gas_limit` 三预算模型 |
| **TIP-20 Token** | `precompiles/src/tip20/` | MIT/Apache-2.0 | **Blueprint** | Precompile vs Solidity | 低 — 接口标准化 | 接口设计可复用；在 Mantle 上用 Solidity predeploy 实现 |
| **TIP-403 Registry** | `precompiles/src/tip403_registry/` | MIT/Apache-2.0 | **Blueprint** | Precompile vs Solidity | 低 — 策略模型通用 | 策略模型（whitelist/blacklist/compound）直接可借鉴；用 Solidity predeploy 实现 |
| **TIP-403 Zone 镜像** | `zones/tempo-zone/src/l1_state/` | MIT/Apache-2.0 | **Blueprint** | OP Stack 已有 L1→L2 读取路径 | 低 | `SharedPolicyCache` + 逐块 GC 模式可移植到 OP Stack 的 L1 block info 推送 |
| **ECIES 加密存款** | `zones/precompiles/src/ecies.rs:67-138` | MIT/Apache-2.0 | **Build-equivalent** | 可直接用 Go 密码学库重写 | 中 — 需安全审计 | ECDH + HKDF-SHA256 + AES-256-GCM 方案可在 Go 中重写；Chaum-Pedersen 需 precompile 支持 |
| **Chaum-Pedersen 证明** | `zones/precompiles/src/chaum_pedersen.rs:66-116` | MIT/Apache-2.0 | **Build-equivalent** | 需新增 precompile | 中 — 椭圆曲线密码学实现 | 6,000 gas 的轻量验证；可在 op-geth 中添加 secp256k1 Chaum-Pedersen precompile |
| **Zone 架构** | `zones/crates/tempo-zone/src/engine.rs` | MIT/Apache-2.0 | **Blueprint** | Mantle 是 OP Stack L2，Zone 是 Reth 自定义节点 | 高 — 架构差异大 | 借鉴 L1-event-driven 单 sequencer validium 模型；实现需在 OP Stack L3 框架中重新设计 |
| **Reth NodeBuilder 模式** | `crates/node/src/node.rs` | MIT/Apache-2.0 | **Blueprint** | 仅当 Mantle 迁移到 Reth 时才相关 | 高 — 重大迁移决策 | 全栈 Reth 定制模式的完整参考；但 Go→Rust 迁移成本极高 |
| **Commonware Simplex BFT** | `crates/commonware-node/` | Apache-2.0/MIT | **Avoid** | 单一生产用户，紧耦合 Commonware 全栈 | 高 — 成熟度不足 | 不建议直接引入；如需 BFT 共识，选择 CometBFT 等成熟方案 |
| **Private RPC Auth** | `zones/crates/rpc/src/auth/` | MIT/Apache-2.0 | **Borrow** (设计) | Go 重写简单 | 低 | 签名令牌认证方案简洁实用，可直接在任何语言中实现 |
| **AccountKeychain** | `precompiles/src/account_keychain/` | MIT/Apache-2.0 | **Blueprint** | Precompile vs Smart Contract | 中 — WebAuthn 集成复杂 | P256/WebAuthn 密钥委托模型有参考价值；ERC-4337 account abstraction 是更标准的替代方案 |
| **Attodollar Gas 定价** | `primitives/src/transaction/mod.rs:30-46` | MIT/Apache-2.0 | **Blueprint** | 需修改 OP Stack gas oracle | 中 | 法币锚定 gas 定价思路有企业价值；但实现需修改 L1→L2 gas oracle |
| **硬分叉门控系统** | `chainspec/src/hardfork.rs` | MIT/Apache-2.0 | **Blueprint** | OP Stack 有自己的升级机制 | 低 | 功能渐进激活模式可参考，但 OP Stack 已有成熟的升级框架 |

---

## 14. Mantle Reference Points

### 14.1 Reth SDK Integration Pattern `[Mantle-Ref]`

**Finding**: Tempo demonstrates a mature pattern for building custom L1/L2 chains on Reth SDK:
- `NodeBuilder` composition with custom `NodeTypes`, `EngineTypes`, `PayloadTypes`
- Custom `TempoTxEnvelope` extending standard Ethereum transaction types
- Dual-runtime architecture (execution + consensus on separate Tokio runtimes)
- Custom precompile system with dynamic lookup and hardfork gating

**Mantle relevance**: If Mantle migrates from op-geth to Reth-based execution, Tempo's `TempoNode` → `TempoFullNode` pattern provides a concrete reference for how to compose custom chain logic with Reth. The `NodeBuilder` pattern is designed for exactly this use case.

**工程判断**：Reth SDK 定制模式仅可作为 **架构 blueprint**。直接代码复用需要 Mantle 从 Go (op-geth) 迁移到 Rust (Reth)，这是一个根本性的技术栈决策，涉及重写整个执行客户端。更实际的路径是将 Tempo 的设计理念（如 custom primitives、hardfork gating、precompile registry）提取为架构模式，在 op-geth 或 op-reth 中按需实现。

### 14.2 Payment Lane Architecture `[Mantle-Ref]`

**Finding**: The Payment Lane is implemented via:
1. Transaction classification by address prefix (stateless, no storage access)
2. Block header extensions (`shared_gas_limit`, `general_gas_limit`)
3. Payload builder lane routing
4. Consensus-level validation of lane gas consumption

**Mantle relevance**: Mantle could introduce similar gas lane separation for specific use cases (e.g., dedicated capacity for MNT staking operations, or priority lanes for specific dApp categories). The key insight is that stateless transaction classification (by address prefix) enables lane routing without additional state access overhead.

**工程判断**：Payment Lane 设计 **可移植到 OP Stack**，但需要在三个层面修改：(1) op-geth 交易池增加 lane 分类逻辑，(2) 区块构建器实现 gas 预算隔离，(3) 在 L1 derivation 中验证 lane gas 约束。分类逻辑（地址前缀检查）是纯计算操作，语言无关，可直接用 Go 实现。这是 Tempo 对 Mantle 最直接可用的参考点。

### 14.3 Zone Architecture `[Mantle-Ref]`

**Finding**: Zones are Reth SDK nodes with:
- `NoopConsensus` — no P2P consensus needed for single-sequencer chains
- Engine API driven block production from L1 events
- Bridge via portal contract with batch submission and proof slots
- EIP-2935 block hash anchoring for proof verification

**Mantle relevance**: Mantle could offer Zone-like privacy sub-chains as application-specific L3s anchored to the Mantle L2. The Zone architecture is essentially an app-specific rollup pattern that could be adapted to OP Stack. The key advantage is simplicity — a Zone is a minimal Reth node with no P2P overhead.

**工程判断**：Zone 架构对 Mantle 应视为 **长期参考**。OP Stack 已有 L3/app-chain 路线图（OP Chains），但 Zone 的 "L1-event-driven validium" 模式提供了一种更轻量的隐私子链实现。实际移植需要在 OP Stack 框架内重新设计，而非直接使用 Tempo 的 Reth 实现。适用场景：企业客户需要独立隐私环境但共享 Mantle 的安全性和流动性。

### 14.4 TIP-403 Compliance Framework `[Mantle-Ref]`

**Finding**: TIP-403 is implemented as a precompile registry with:
- Policy types: always-allow, always-reject, whitelist, blacklist
- Compound policies (sender/recipient rules)
- Automatic mirroring to L2 via `TempoStateReader` precompile
- Per-block policy cache with GC

**Mantle relevance**: The policy registry pattern is portable to OP Stack. Implementation would require:
1. A compliance registry precompile or system contract on Mantle
2. An L1→L2 state reading mechanism (similar to `TempoStateReader`)
3. Integration with token transfer hooks

The `SharedPolicyCache` with per-block GC is an elegant pattern for L2s that need L1 state access.

**工程判断**：TIP-403 策略模型 **直接可移植**。建议在 Mantle 上通过 predeploy system contract 实现，避免修改协议层。核心逻辑（whitelist/blacklist/compound policies）不依赖 Tempo 特有功能，可用 Solidity 实现。L1→L2 策略镜像可复用 OP Stack 现有的 L1 block info 推送机制。

### 14.5 Encrypted Deposits/Withdrawals `[Mantle-Ref]`

**Finding**: ECIES + Chaum-Pedersen pattern:
- Depositor encrypts sensitive fields using sequencer's public key
- Sequencer decrypts and provides zero-knowledge proof of correct decryption
- On-chain precompile verifies proof without seeing private key
- Failure path: refund to sender (not revert)

**Mantle relevance**: This pattern could be applied to Mantle's L1-L2 bridge for privacy-preserving deposits. The Chaum-Pedersen proof ensures the sequencer cannot cheat on decryption results. However, it requires trust in the sequencer for privacy (the sequencer sees all plaintext).

**工程判断**：ECIES + Chaum-Pedersen 方案 **可重新实现**。ECDH/HKDF/AES-GCM 在 Go 标准库中均有成熟实现。Chaum-Pedersen 验证需要新增一个 precompile（约 200 行 Go 代码 + 6,000 gas），在 op-geth 中修改量可控。关键风险点：方案假设 sequencer 不泄露解密后的明文——这在 centralized sequencer 模型下可接受，但不适用于去中心化 sequencer 架构。

### 14.6 Validity Proof Preparation `[Mantle-Ref]`

**Finding**: Tempo Zones are architecturally prepared for validity proofs:
- `no_std` precompiles and primitives for SP1 RISC-V execution
- Proof slot in `submitBatch()` contract interface
- `verifier` address in portal contract
- Dual-mode support planned: ZKVM (SP1) and TEE (SGX/TDX)

**Mantle relevance**: For Mantle's potential Optimistic → ZK transition, Tempo's approach of:
1. Making core logic `no_std` compatible first
2. Adding proof infrastructure to contracts
3. Running with empty proofs during development
4. Supporting both ZK and TEE verification modes

...provides a practical migration path reference.

**工程判断**：Tempo 的 `no_std` 优先策略是 **有价值的方法论参考**。对于 Mantle 的 Optimistic → ZK 过渡，关键启示是：(1) 先确保核心逻辑可在受限执行环境（RISC-V/WASM）中运行，(2) 在合约接口中预留 proof slot，(3) 在开发阶段接受空 proof。这降低了 ZK 迁移的技术风险，允许逐步引入证明生成。但 Mantle 的 Go 栈使 `no_std` 路径不直接适用——等价策略是确保 Go 代码可编译为 WASM 或在 Go-based zkVM 中运行。

---

## Appendix A: Key Constants Reference

| Constant | Value | Source |
|---|---|---|
| `TEMPO_TX_TYPE_ID` | `0x76` | `primitives/src/transaction/tempo_transaction.rs` |
| `TIP20_PAYMENT_PREFIX` | `0x20C000000000000000000000` | `primitives/src/transaction/envelope.rs:16` |
| `TEMPO_GAS_PRICE_SCALING_FACTOR` | `10^12` | `primitives/src/transaction/mod.rs:36` |
| `TEMPO_T1_BASE_FEE` | `20,000,000,000` attodollars | `chainspec/src/constants.rs:29` |
| `TEMPO_T1_GENERAL_GAS_LIMIT` | `30,000,000` gas | `chainspec/src/constants.rs:35` |
| `CP_VERIFY_GAS` | `6,000` gas | `zones/precompiles/src/chaum_pedersen.rs:31` |
| `ENCRYPTED_PAYLOAD_PLAINTEXT_SIZE` | `64` bytes | `zones/precompiles/src/ecies.rs:22` |
| `DEFAULT_MAX_AUTH_TOKEN_VALIDITY_SECS` | `2,592,000` (30 days) | `zones/rpc/src/auth/token.rs:26` |
| Mainnet chain ID | `4217` | `chainspec/src/hardfork.rs:259` |
| Testnet (Moderato) chain ID | `42431` | `chainspec/src/hardfork.rs:260` |

## Appendix B: Precompile Address Map

```
Tempo L1 Precompiles:
  0x20C0000000000000000000000000000000000000  pathUSD (default fee token)
  0x20C0... (prefix)                          TIP-20 Tokens (dynamic)
  0x20FC000000000000000000000000000000000000  TIP20Factory
  0x403C000000000000000000000000000000000000  TIP403Registry
  0x4E4F4E4345000000000000000000000000000000  NonceManager ("NONCE")
  0x5165300000000000000000000000000000000000  SignatureVerifier (T3+)
  0xAAAAAAAA00000000000000000000000000000000  AccountKeychain
  0xCCCCCCCC00000000000000000000000000000000  ValidatorConfig
  0xCCCCCCCC00000000000000000000000000000001  ValidatorConfigV2
  0xDEC0000000000000000000000000000000000000  StablecoinDEX
  0xFDC0000000000000000000000000000000000000  AddressRegistry (T3+)
  0xFEEC000000000000000000000000000000000000  TipFeeManager

Zone L2 Precompiles/Predeploys:
  0x1C00000000000000000000000000000000000000  TempoState
  0x1C00000000000000000000000000000000000001  ZoneInbox
  0x1C00000000000000000000000000000000000100  ChaumPedersenVerify
  + AesGcmDecrypt, ZoneTokenFactory, ZoneTip403Proxy, ZoneTip20Token
  + ZoneOutbox, ZoneConfig, TempoStateReader, ZoneTxContext
```

## Appendix C: Doc vs. Code Discrepancies (Summary)

> 详细映射表已前置到第 1 节（WHI-339 Claim → Code Reality 映射表）。以下为精简版：

| Topic | WHI-339 Documentation | Code Reality |
|---|---|---|
| **Mainnet status** | "Testnet only (as of May 2026)" | Mainnet LIVE since genesis, T3 activated Apr 27, 2026 |
| **Validity proofs** | "Confirmed architectural component" | Infrastructure prepared, but `batch.rs:215-216` submits `Bytes::new()` for both verifierConfig and proof |
| **Payment classification** | Single-level description | Two-level: v1 (`envelope.rs:174`) and v2 (`envelope.rs:197`, stricter) |
| **Base fee** | "Fixed, less than $0.001" | T1+ = exactly 20B attodollars/gas ≈ $0.001 per transfer (`constants.rs:29`) |
| **Block time** | "~600ms" | Code sets 500ms builder loop + network latency — actual time not hardcoded |
| **Hardfork count** | "T0 → T4" | Actually Genesis → T0 → T1 → T1A → T1B → T1C → T2 → T3 → T4 → T5 (10 variants, `hardfork.rs:164-192`) |
