# Base (base/base) 架构特点与 OP Stack Go 实现差异

## 一、核心架构特点

### 1. Rust 原生单体仓库

- **127 root-workspace members（含 SP1 guest 子 workspace 共 130 crates）**，统一版本管理（`workspace.package.version = "0.0.0"`）
- 使用 Rust edition 2024，MSRV 1.93
- 单一 `Cargo.toml` 管理所有依赖版本，避免版本碎片化
- 统一 lints/clippy/rustfmt 配置

**对比 OP Stack Go 实现**：Go OP Stack 分散在 `optimism` monorepo（Go）+ `op-geth` + `op-reth`（Rust）+ `kona`（Rust）等多个仓库，跨语言协调成本高。

### 2. 直接依赖上游 reth，非 op-reth fork

Base 直接使用 `paradigmxyz/reth v2.2.0`（60+ crates），主 workspace **不依赖 op-reth**：

- 主 workspace `Cargo.toml` 无直接 `op-reth` 依赖
- 主 workspace `Cargo.toml` 无直接 `kona-*` 依赖  
- 主 workspace `Cargo.toml` 无直接 `op-alloy-*` 依赖

> 注：excluded 的 SP1 guest 子 workspace（`crates/proof/succinct/programs/`）的 `Cargo.lock` 中存在 `op-alloy-consensus` 传递依赖（经由 `reth-codecs` / `reth-primitives-traits` 引入），但不影响主 workspace 的独立性。

所有 OP Stack 特定逻辑（rollup 共识、derivation、EVM 扩展、payload 构建等）均在 `base-*` crates 中自研实现。

**优势**：
- 可以立即跟进上游 reth 新版本，无需等待 op-reth 适配
- 避免 fork 维护的合并冲突开销
- 对 EL 层有完全控制，可自由定制

**对比**：Mantle 使用 `op-reth` fork（依赖链：mantle-reth → op-reth → reth），每次上游更新需要经过两层 fork 合并。

### 3. 自研 Derivation Pipeline

`base-consensus-derive` 是完全自研的 derivation pipeline：

- **no_std 支持**：可直接嵌入 ZK 证明 guest 程序，无需额外适配
- 独立于 kona：不依赖任何 kona-derive 或 kona-client 组件
- 与 consensus engine 紧密集成：同一仓库内直接调用，无跨仓库 API 边界

**对比 OP Stack**：标准 OP Stack 使用 kona 的 derivation pipeline，Mantle fork 了 kona 来适配。Base 完全跳过了 kona。

### 4. Flashblocks 一等公民

Flashblocks 不是后加的 feature，而是架构层面的一等公民：

- **Execution 层**：`base-flashblocks`（核心实现）+ `base-flashblocks-node`（节点集成），内置于执行客户端
- **Builder 层**：`base-builder-core` 生成 Flashblocks，构建器直接支持
- **Common 层**：`base-common-flashblocks` 提供共享类型
- **Infra 层**：`websocket-proxy` 支持 Flashblocks 的实时推送

**对比**：标准 OP Stack 和 Mantle 均无 Flashblocks 概念，Base 是首个在架构层面原生支持 partial block confirmation 的 OP Stack 链。

### 5. 多证明系统（Fault Proof + ZK + TEE）

Base 是目前 OP Stack 生态中证明系统最全面的实现：

```
crates/proof/
├── 核心层：proof, primitives, client, driver, executor, preimage, mpt, host
├── Fault Proof：challenge (challenger), contracts, proposer
├── ZK (SP1)：zk/{client,service,db,outbox}, succinct/{programs,utils,scripts,validity}
└── TEE (Nitro)：tee/{nitro-enclave,nitro-host,registrar,nitro-verifier,nitro-attestation-prover}
```

- **Fault Proof**：自研 challenger + proposer，不依赖 OP Stack 的 cannon
- **ZK Proof**：集成 Succinct SP1 v6.2.1（Hypercube），支持 range proof + aggregation proof
- **TEE Proof**：AWS Nitro Enclaves，通过 risc0/Boundless market 验证 attestation

三种证明路线共享同一套核心 `base-proof-*` crates（no_std），通过不同的 host/client 组合实现。

**关键设计**：核心证明逻辑（`base-proof-client`, `base-proof-driver`, `base-proof-executor` 等）均为 no_std，可同时编译到：
- Native（Fault Proof host 执行）
- SP1 zkVM（ZK guest 程序）
- Nitro Enclave（TEE 执行环境）

**对比**：
- Mantle 使用 `op-succinct`（fork）做 ZK 证明，`kona`（fork）做 fault proof，两者分离
- 标准 OP Stack 使用 `cannon`（Go MIPS VM）做 fault proof，不支持 ZK/TEE

### 6. v0.9.0 Pre-1.0 状态

- 版本号 `0.0.0`（workspace 级别）
- 主网 Base 仍在从 Go OP Stack 迁移中
- Devnet E2E 测试框架已就绪（`devnet/` crate）

## 二、组件映射对照表

| OP Stack (Go) 组件 | Base (Rust) 对应 | 说明 |
|---|---|---|
| `op-node` | `base-consensus-*` (13 crates) | 完全自研，不依赖 kona |
| `op-geth` | `base-execution-*` (20 crates) + reth v2.2.0 | 基于上游 reth，非 op-reth fork |
| `op-batcher` | `base-batcher-*` (7 crates) | 自研 |
| `op-proposer` | `base-proof-proposer` | 自研 |
| `op-challenger` | `base-proof-challenge` | 自研 |
| `cannon` (MIPS VM) | `base-proof-*` (no_std core) | 无 MIPS VM，直接 native/ZK/TEE 执行 |
| `kona-derive` | `base-consensus-derive` | 自研，no_std |
| `kona-client` | `base-proof-client` | 自研，no_std |
| `op-succinct` | `base-proof-succinct-*` + `base-zk-*` | 深度集成，非 fork |
| _(无)_ | `base-builder-*` + Flashblocks | Base 独有 |
| _(无)_ | `base-proof-tee-*` | TEE 证明，Base 独有 |
| `op-conductor` | `basectl` Conductor 子命令 | 集成在运维工具中 |

## 三、架构优势总结

| 维度 | Base (Rust 单体仓库) | 标准 OP Stack (多仓库 Go+Rust) |
|---|---|---|
| **代码组织** | 单仓库 127 root-workspace members，统一依赖管理 | 多仓库 (optimism + op-geth + op-reth + kona + op-succinct) |
| **语言** | 纯 Rust | Go + Rust 混合 |
| **EL 依赖** | 上游 reth v2.2.0 直接使用 | op-reth fork → reth (两层 fork) |
| **Derivation** | 自研 no_std，与证明系统共享 | kona (需 fork 适配) |
| **证明系统** | 三合一 (FP + ZK + TEE)，共享核心 | FP (cannon) + ZK (op-succinct) 分离 |
| **Flashblocks** | 架构层面原生支持 | 不支持 |
| **no_std 复用** | common + consensus + proof 核心均 no_std | kona 部分 no_std，但需 fork 维护 |
| **版本管理** | 单一 Cargo.toml | 多仓库独立版本 |
| **升级路径** | 跟进上游 reth tag 即可 | 需逐层 merge fork |

## 四、潜在劣势与风险

1. **维护负担**：自研所有组件意味着 Base 团队需独立维护 consensus、derivation、proof 等所有逻辑，无法直接复用 OP Stack 社区的 bug fix
2. **与 OP Stack 标准偏离**：可能导致与 Superchain 其他链的互操作性问题
3. **Pre-1.0 不确定性**：主网仍在迁移中，Rust 实现尚未经历大规模生产验证
4. **单一技术栈风险**：纯 Rust 堆栈对团队 Rust 技能要求高


---

# Base (base/base) Binary 入口清单

> 从代码实际枚举，基于 `Cargo.toml` 的 `[[bin]]` 定义和 workspace members

## 一、核心链组件（8 个）

### `base`
- **路径**：`bin/base/`
- **职责**：统一 Base 节点 binary，作为 umbrella 入口，通过子命令分发到 consensus + execution 等子系统
- **入口**：`base_cli_utils::run_cli_main!` → `cli::BaseCli`
- **关键依赖**：`base-consensus-cli`, `base-execution-cli`, `base-common-chains`

### `base-reth-node`
- **路径**：`bin/node/`
- **职责**：标准 Base 执行节点（非 builder 模式），基于 reth 的 EL 节点
- **入口**：jemalloc 分配器 → `Cli<StandardNodeArgs>` → `StandardBaseRethNode::run()`
- **关键依赖**：`base-execution-cli`, `base-reth-cli`, `reth-cli-util`

### `base-consensus`
- **路径**：`bin/consensus/`
- **职责**：共识层节点（Rollup Node），替代 op-node，负责 L1 derivation 和 L2 状态推进
- **入口**：`base_cli_utils::run_cli_main!` → `ConsensusCli`
- **关键依赖**：`base-consensus-cli`

### `base-builder`
- **路径**：`bin/builder/`
- **职责**：区块构建器节点（Sequencer 模式），支持 Flashblocks，集成 metering、txpool RPC、builder API
- **入口**：jemalloc → `Cli<Args>` → `BaseNodeRunner` + `FlashblocksServiceBuilder`
- **关键依赖**：`base-builder-core`, `base-builder-metering`, `base-node-runner`, `base-flashblocks-node`

### `base-batcher`
- **路径**：`bin/batcher/`
- **职责**：L2 → L1 批数据提交器，编码 L2 数据并提交到 L1（blob 或 calldata）
- **入口**：`base_cli_utils::run_cli_main!` → `cli::Cli`
- **关键依赖**：`base-batcher-core`, `base-batcher-service`, `base-batcher-encoder`

### `base-proposer`
- **路径**：`bin/proposer/`
- **职责**：Output root proposer，将 L2 output root 提交到 L1
- **入口**：`base_cli_utils::run_cli_main!(async cli::Cli)`
- **关键依赖**：`base-proposer`

### `base-challenger`
- **路径**：`bin/challenger/`
- **职责**：Fault proof challenger，监控 L2 output proposal 并挑战无效提案
- **入口**：`base_cli_utils::run_cli_main!` → `cli::Cli`
- **关键依赖**：`base-challenger`

### `ingress-rpc`
- **路径**：`bin/ingress-rpc/`
- **职责**：交易/Bundle 入口 RPC 服务（tips 竞价系统），接收用户交易并分发给 builder
- **入口**：`#[tokio::main]` → `IngressService`
- **关键依赖**：`ingress-rpc-lib`, `audit-archiver-lib`, `base-bundles`, `jsonrpsee`

## 二、证明相关（5 个主入口 + 10 个脚本 binary）

### `base-prover-zk`
- **路径**：`bin/prover/zk/`
- **职责**：ZK 证明服务，托管 gRPC 服务器，使用 SP1/Succinct 编排 ZK 证明生成
- **入口**：`base_cli_utils::run_cli_main!` → `cli::Cli`
- **关键依赖**：`base-zk-service`, `base-zk-db`, `sp1-sdk`, `tonic`, `tonic-web`

### `base-prover-nitro-host`
- **路径**：`bin/prover/nitro-host/`
- **职责**：TEE 证明主机端，代理请求到 AWS Nitro Enclave
- **入口**：`base_cli_utils::run_cli_main!` → `cli::Cli`
- **关键依赖**：`base-proof-tee-nitro-host`, `base-proof-host`

### `base-prover-nitro-enclave`
- **路径**：`bin/prover/nitro-enclave/`
- **职责**：TEE 证明 enclave 端，运行于 AWS Nitro Enclave 内部（仅 Linux）
- **入口**：`#[tokio::main]` → `NitroEnclave::run()`
- **关键依赖**：`base-proof-tee-nitro-enclave`
- **限制**：仅 Linux（非 Linux 平台 panic）

### `base-snark-e2e`
- **路径**：`bin/prover/snark-e2e/`
- **职责**：SNARK Groth16 端到端测试，设计为 Kubernetes CronJob 定期验证 ZK 证明管线
- **入口**：`#[tokio::main]` → `SnarkE2e::run()`
- **关键依赖**：`base-zk-service`

### `base-proof-tee-registrar`
- **路径**：`bin/prover-registrar/`
- **职责**：TEE 证明者自动注册服务，管理 Boundless market 注册、签名密钥、余额监控和 EC2/ELB 生命周期
- **入口**：`base_cli_utils::run_cli_main!` → `cli::Cli`
- **关键依赖**：`base-proof-tee-registrar`, `boundless-market`, `aws-sdk-ec2`, `aws-sdk-elasticloadbalancingv2`

### Succinct 证明脚本（非独立 binary，但包含可执行入口）

#### `base-proof-succinct-prove` 包含 2 个 binary：
| Binary | 路径 | 职责 |
|---|---|---|
| `multi` | `crates/proof/succinct/scripts/prove/bin/multi.rs` | 多区块范围证明 |
| `agg` | `crates/proof/succinct/scripts/prove/bin/agg.rs` | 聚合证明 |

#### `base-proof-succinct-scripts` 包含 7 个 binary：
| Binary | 路径 | 职责 |
|---|---|---|
| `fetch-and-save-proof` | `crates/proof/succinct/scripts/utils/bin/fetch_and_save_proof.rs` | 获取并保存证明 |
| `config` | `crates/proof/succinct/scripts/utils/bin/config.rs` | 配置工具 |
| `cost-estimator` | `crates/proof/succinct/scripts/utils/bin/cost_estimator.rs` | 证明成本估算 |
| `block-data` | `crates/proof/succinct/scripts/utils/bin/block_data.rs` | 区块数据工具 |
| `fetch-l2oo-config` | `crates/proof/succinct/scripts/utils/bin/fetch_l2oo_config.rs` | L2OO 配置获取 |
| `gen-sp1-test-artifacts` | `crates/proof/succinct/scripts/utils/bin/gen_sp1_test_artifacts.rs` | SP1 测试制品生成 |
| `parse-receipt` | `crates/proof/succinct/scripts/utils/bin/parse_receipt.rs` | 收据解析 |

#### `base-proof-succinct-validity` 包含 1 个 binary：
| Binary | 路径 | 职责 |
|---|---|---|
| `validity` | `crates/proof/succinct/validity/bin/validity.rs` | Validity proof 生成入口 |

## 三、运维/测试工具（5 个）

### `basectl`
- **路径**：`bin/basectl/`
- **职责**：基础设施控制 TUI/CLI，提供 Config、Flashblocks、DA、CommandCenter、Conductor、Upgrades 子命令
- **入口**：`#[tokio::main]` → subcommand dispatch → interactive `ViewId`
- **关键依赖**：`basectl-cli`, `ratatui`（TUI）

### `based`
- **路径**：`bin/based/`
- **职责**：出块健康检查 sidecar，定期轮询节点检测出块停滞，通过 StatsD 上报 Datadog
- **入口**：`#[tokio::main]` → `BlockProductionHealthChecker`
- **关键依赖**：`based`（lib）, `cadence`（StatsD）

### `audit-archiver`
- **路径**：`bin/audit-archiver/`
- **职责**：Bundle 审计归档服务，接收 JSON-RPC 事件并归档到 S3（含 Moka LRU 去重）
- **入口**：`#[tokio::main]` → `AuditArchiverRpc` + `AuditArchiver` worker pool
- **关键依赖**：`audit-archiver-lib`, `aws-sdk-s3`, `jsonrpsee`, `moka`

### `base-load-tester`
- **路径**：`bin/load-tester/`
- **职责**：负载测试工具，向 Base 端点生成测试交易负载
- **入口**：`base_cli_utils::run_cli_main!` → `cli::Cli`
- **关键依赖**：`base-load-tests`, `alloy-provider`, `indicatif`

### `websocket-proxy`
- **路径**：`bin/websocket-proxy/`
- **职责**：WebSocket 扇出代理，连接上游 WS 并广播到下游客户端，支持 brotli 压缩、速率限制、API-key 认证、Prometheus 指标
- **入口**：`#[tokio::main]` → axum WS server
- **关键依赖**：`websocket-proxy`（lib）, `axum`, `brotli`, `metrics-exporter-prometheus`

## Binary 总计

| 分类 | 数量 | 说明 |
|---|---|---|
| 核心链组件 | 8 | base, node, consensus, builder, batcher, proposer, challenger, ingress-rpc |
| 证明相关 | 5 主入口 + 10 脚本 binary | zk, nitro-host, nitro-enclave, snark-e2e, prover-registrar + succinct 脚本 binary（prove 2 + scripts 7 + validity 1） |
| 运维/测试工具 | 5 | basectl, based, audit-archiver, load-tester, websocket-proxy |
| **总计** | **18 主入口 + 10 脚本 binary** | |

## 通用模式

- 大多数 binary 使用 `base_cli_utils::run_cli_main!` 宏，将 CLI 解析和逻辑委托给同名 lib crate 的 `cli::Cli` 结构体
- Reth-based 执行节点（builder, node）配置 jemalloc 全局分配器，调用 `base_reth_cli::init_reth!()` + `base_cli_utils::init_common!()`
- 独立服务（audit-archiver, ingress-rpc, websocket-proxy, based）直接使用 `#[tokio::main]` + `clap::Parser`，配合 `define_log_args!` / `define_metrics_args!` 宏


---

# Base (base/base) 关键依赖栈

> 所有版本信息从 `Cargo.toml` workspace dependencies 实际提取

## 核心框架依赖

### reth v2.2.0（上游 paradigmxyz/reth，非 op-reth fork）

Base 直接依赖上游 reth，通过 git tag 锁定版本，共 **60+ reth-\* crates**：

```toml
reth-db = { git = "https://github.com/paradigmxyz/reth", tag = "v2.2.0" }
# ... 共 60+ crates，全部 tag = "v2.2.0"
```

**关键 reth crates 按功能分组**：

| 功能 | Crates |
|---|---|
| 节点框架 | `reth-node-builder`, `reth-node-core`, `reth-node-api`, `reth-node-metrics`, `reth-node-ethereum` |
| 存储 | `reth-db`, `reth-db-api`, `reth-db-common`, `reth-provider`, `reth-storage-api`, `reth-storage-errors` |
| EVM | `reth-evm`, `reth-revm`, `reth-evm-ethereum` |
| 网络 | `reth-network`, `reth-network-p2p`, `reth-network-peers`, `reth-discv4`, `reth-discv5`, `reth-net-nat` |
| RPC | `reth-rpc`, `reth-rpc-api`, `reth-rpc-eth-api`, `reth-rpc-eth-types`, `reth-rpc-engine-api`, `reth-rpc-layer`, `reth-rpc-convert`, `reth-rpc-server-types` |
| Engine | `reth-engine-tree`, `reth-engine-primitives` |
| Payload | `reth-payload-builder`, `reth-payload-primitives`, `reth-payload-util`, `reth-payload-validator`, `reth-basic-payload-builder`, `reth-payload-builder-primitives` |
| 交易池 | `reth-transaction-pool` |
| Trie | `reth-trie`, `reth-trie-db`, `reth-trie-common`, `reth-trie-parallel` |
| 共识 | `reth-consensus`, `reth-consensus-common` |
| ExEx | `reth-exex`, `reth-exex-test-utils` |
| 原语 | `reth-primitives`, `reth-primitives-traits`, `reth-ethereum-primitives`, `reth-execution-types`, `reth-execution-errors`, `reth-ethereum-forks` |
| CLI | `reth-cli`, `reth-cli-util`, `reth-cli-runner`, `reth-cli-commands` |
| 其他 | `reth-tracing`, `reth-tracing-otlp`, `reth-chain-state`, `reth-ipc`, `reth-tasks`, `reth-errors`, `reth-testing-utils`, `reth-e2e-test-utils`, `reth-chainspec` |

**发布 crate 依赖**（非 git）：
```toml
reth-codecs = "0.3.1"
reth-primitives-traits = "0.3.1"
reth-zstd-compressors = "0.3.1"
```

### 关键事实：主 workspace 无直接 op-reth / kona / op-alloy 依赖

根 workspace 的 `Cargo.toml` 中 **没有** 以下直接依赖，根 `Cargo.lock` 中也没有对应包：
- ~~`op-reth`~~（optimism 的 reth fork）
- ~~`kona-*`~~（Kona derivation / fault proof 库）
- ~~`op-alloy-*`~~（OP Stack 的 alloy 扩展）

这意味着 Base 主 workspace 没有通过这些 OP Stack crates 复用 rollup-specific 逻辑。

> **注意**：excluded 的 SP1 guest 子 workspace（`crates/proof/succinct/programs/`）的 `Cargo.lock` 中存在 `op-alloy-consensus` 作为传递依赖（经由 `reth-codecs` / `reth-primitives-traits` 引入）。这不影响主 workspace 的独立性结论，但不能概括为全仓库完全没有 op-alloy 传递依赖。

---

### Alloy 2.0.4

Alloy 是以太坊 Rust 生态的统一类型库，Base 使用 v2.0.4：

```toml
alloy-provider = "2.0.4"
alloy-contract = "2.0.4"
alloy-consensus = "2.0.4"     # default-features = false (no_std)
alloy-primitives = "1.5.6"    # default-features = false (no_std)
alloy-sol-types = "1.5.6"     # default-features = false (no_std)
alloy-eips = "2.0.4"          # default-features = false (no_std)
alloy-evm = "0.34.0"
alloy-hardforks = "0.4.7"
alloy-rlp = "0.3.13"
alloy-trie = "0.9.4"
# ... 共 25+ alloy crates
```

### revm 38.0.0

EVM 执行引擎：

```toml
revm = "38.0.0"
revm-bytecode = "10.0.0"
revm-database = "13.0.0"
revm-inspectors = "0.39.0"
revm-precompile = "34.0.0"
revm-primitives = "23.0.0"
revm-context-interface = "17.0.1"
```

---

## 证明系统依赖

### SP1 v6.2.1（Succinct ZK 证明）

```toml
sp1-sdk = "=6.2.1"
sp1-build = "=6.2.1"
sp1-prover-types = "=6.2.1"
sp1-cluster-artifact = { git = "https://github.com/succinctlabs/sp1-cluster", tag = "v2.3.2" }
sp1-cluster-common = { git = "https://github.com/succinctlabs/sp1-cluster", tag = "v2.3.2" }
sp1-cluster-utils = { git = "https://github.com/succinctlabs/sp1-cluster", tag = "v2.3.2" }
```

> 注：SP1 guest programs 子 workspace 使用 `sp1-zkvm = "=6.1.0"` 和 `sp1-lib = "=6.1.0"`（版本略低于主 workspace）

### risc0 / Boundless（TEE 认证证明）

```toml
boundless-market = "1.1"
risc0-ethereum-contracts = "3.0.1"
risc0-zkvm = "^3.0"
```

---

## 运行时与网络

### Tokio 生态

```toml
tokio = "1.48.0"
tokio-util = "0.7.4"
tokio-stream = "0.1.17"
tokio-tungstenite = "0.28.0"
```

### P2P 网络

```toml
discv5 = "0.10"
libp2p = "0.56.0"
libp2p-identity = "0.2.12"
libp2p-stream = "0.4.0-alpha"
```

### RPC

```toml
jsonrpsee = "0.26.0"        # JSON-RPC 框架
tonic = "0.14"               # gRPC
axum = "0.8.3"               # HTTP/WS
```

### HTTP

```toml
reqwest = "0.13.1"
hyper = "1.8"
tower = "0.5"
tower-http = "0.6"
```

---

## 可观测性

### Tracing & Metrics

```toml
tracing = "0.1.43"
tracing-subscriber = "0.3.22"
tracing-appender = "0.2.4"
opentelemetry = "0.31"
opentelemetry-otlp = "0.31"
metrics = "0.24.3"
metrics-exporter-prometheus = "0.18.1"
```

---

## 数据库

```toml
rocksdb = "0.24"             # 嵌入式 KV 存储
redb = "2"                   # 嵌入式 KV 存储（proof 相关）
sqlx = "0.8"                 # SQL 数据库（ZK proof 状态）
```

---

## AWS 集成（TEE）

```toml
aws-config = "1.1.7"
aws-sdk-s3 = "1.106.0"
aws-sdk-ec2 = "1.217.0"
aws-sdk-elasticloadbalancingv2 = "1.109.0"
aws-nitro-enclaves-nsm-api = "0.4"
```

---

## 密码学

```toml
sha2 = "0.10"                # SHA-256
sha3 = "0.10"                # SHA-3 / Keccak
k256 = "0.13"                # secp256k1 椭圆曲线
p384 = "0.13"                # P-384 曲线
secp256k1 = "0.30"           # libsecp256k1
c-kzg = "2.1.5"              # KZG 承诺（blob）
rustls = "0.23.35"           # TLS
```

---

## 序列化

```toml
serde = "1.0.228"
serde_json = "1.0.145"
bincode = "2"
ethereum_ssz = "0.10"        # SSZ（以太坊序列化）
rkyv = "0.8"                 # 零拷贝序列化
```

---

## 依赖栈总结

```
┌─────────────────────────────────────────────┐
│              Base Application               │
│  (consensus, execution, batcher, builder,   │
│   proposer, challenger, proof)              │
├─────────────────────────────────────────────┤
│           reth v2.2.0 (upstream)            │
│     60+ crates — 非 op-reth fork            │
├──────────────────┬──────────────────────────┤
│  Alloy 2.0.4     │    revm 38.0.0          │
│  25+ crates      │    EVM 执行引擎          │
├──────────────────┴──────────────────────────┤
│     SP1 v6.2.1    │  risc0 3.0  │  Nitro   │
│     ZK 证明        │  TEE 认证    │  TEE     │
├──────────────────┴───────────┴──────────────┤
│  tokio 1.48  │ libp2p 0.56 │ jsonrpsee 0.26│
│  运行时       │  P2P 网络    │   RPC        │
└─────────────────────────────────────────────┘
```


---

# Base (base/base) 仓库结构总览

> 版本：v0.9.0 (pre-1.0)  |  Rust edition 2024  |  MSRV 1.93  |  License: MIT

## 顶层目录

```
base/
├── bin/                    # Binary 入口（18 个可执行文件）
├── crates/                 # 8 大功能域，106 个 root-workspace packages
│   ├── batcher/            # L1 数据提交器（7 crates）
│   ├── builder/            # 区块构建器 / Flashblocks（3 crates）
│   ├── common/             # 共享类型与原语（15 crates）
│   ├── consensus/          # Rollup Node 自研实现（13 crates）
│   ├── execution/          # reth-based 执行客户端（20 crates）
│   ├── infra/              # 运维基础设施（6 crates）
│   ├── proof/              # 多证明系统（32 crates）
│   └── utilities/          # 通用工具库（10 crates）
├── etc/tools/              # 开发工具（witness-diff）
├── actions/                # CI/CD harness
├── devnet/                 # 系统/E2E 测试
├── baseup/                 # 安装脚本
├── docs/                   # 文档
├── Cargo.toml              # Workspace 根配置
├── Justfile                # 构建/测试命令
└── deny.toml               # cargo-deny 供应链审计
```

## 8 大功能域解析

### 1. `crates/consensus/` — Rollup Node（自研，替代 op-node/kona）

Base 完全自研了 rollup consensus 层，不依赖 kona 或 op-node。核心是 `base-consensus-derive`（no_std，derivation pipeline）和 `base-consensus-engine`（共识引擎）。

| Crate | 职责 |
|---|---|
| `base-consensus-cli` | 共识节点 CLI 入口 |
| `base-consensus-derive` | **自研 derivation pipeline**（no_std，可嵌入 ZK 证明） |
| `base-consensus-disc` | 节点发现（discv5） |
| `base-consensus-engine` | 共识引擎，驱动 L2 状态推进 |
| `base-consensus-gossip` | P2P gossip 协议（libp2p） |
| `base-consensus-peers` | 对等节点管理 |
| `base-consensus-protocol` | 协议类型定义 |
| `base-consensus-providers` | 数据提供者抽象 |
| `base-consensus-rpc` | 共识层 RPC 接口 |
| `base-consensus-safedb` | Safe head 持久化 |
| `base-consensus-service` | 共识服务编排 |
| `base-consensus-sources` | L1 数据源（日志、交易） |
| `base-consensus-upgrades` | 硬分叉升级管理（no_std） |

### 2. `crates/execution/` — reth-based 执行客户端（含 Flashblocks）

基于上游 reth v2.2.0（非 op-reth fork）构建，内置 Flashblocks 支持。

| Crate | 职责 |
|---|---|
| `base-node-core` | 节点核心配置 |
| `base-execution-cli` | 执行层 CLI |
| `base-execution-evm` | EVM 执行扩展（Base 预编译等） |
| `base-execution-rpc` | 执行层 RPC |
| `base-metering` | Gas metering |
| `base-node-runner` | 节点运行时 |
| `base-execution-exex` | Execution Extensions |
| `base-execution-trie` | 状态 trie 管理 |
| `base-txpool-rpc` | 交易池 RPC |
| `base-engine-tree` | Engine API 树管理 |
| `base-flashblocks` | **Flashblocks 核心实现** |
| `base-execution-txpool` | 交易池 |
| `base-bundle-extension` | Bundle 交易支持 |
| `base-proofs-extension` | 证明相关扩展 |
| `base-tx-forwarding` | 交易转发 |
| `base-execution-chainspec` | 链规范定义 |
| `base-execution-consensus` | 执行层共识验证 |
| `base-txpool-tracing` | 交易池追踪 |
| `base-execution-payload-builder` | Payload 构建 |
| `base-flashblocks-node` | **Flashblocks 节点集成** |

### 3. `crates/batcher/` — L1 数据提交器

自研 batcher，替代 Go OP Stack 的 op-batcher。

| Crate | 职责 |
|---|---|
| `base-batcher-core` | Batcher 核心驱动逻辑 |
| `base-batcher-service` | 服务层（metrics、生命周期） |
| `base-batcher-encoder` | 批数据编码 |
| `base-batcher-source` | L2 数据源 |
| `base-batcher-admin` | 管理 API（暂停/恢复等） |
| `base-blobs` | Blob 编码/解码 |
| `base-comp` | 压缩库（brotli/zlib，no_std 可选） |

### 4. `crates/builder/` — 区块构建器（Sequencer / Flashblocks）

| Crate | 职责 |
|---|---|
| `base-builder-core` | 区块构建核心（含 Flashblocks 生成） |
| `base-builder-metering` | 构建计量 |
| `base-builder-publish` | 区块发布 |

### 5. `crates/proof/` — 多证明系统

**最复杂的功能域**，同时支持 Fault Proof、ZK (SP1)、TEE (AWS Nitro) 三种证明路线。

#### 核心证明层（12 crates）

| Crate | 职责 | no_std |
|---|---|---|
| `base-proof` | 证明系统核心抽象 | yes |
| `base-proof-primitives` | 证明原语 | yes |
| `base-proof-client` | 证明客户端（guest 侧） | yes |
| `base-proof-driver` | 证明驱动 | yes |
| `base-proof-executor` | 证明执行器 | yes |
| `base-proof-preimage` | Preimage oracle | yes |
| `base-proof-mpt` | MPT 证明 | yes |
| `base-proof-host` | 证明主机端 | no |
| `base-proof-contracts` | L1 合约交互 | no |
| `base-proof-rpc` | 证明 RPC | no |
| `base-proof-proposer` | Output proposer | no |
| `base-proof-challenge` | Fault proof challenger | no |

#### TEE 子系统（5 crates）

| Crate | 职责 |
|---|---|
| `base-proof-tee-nitro-enclave` | Nitro Enclave 内运行的证明程序 |
| `base-proof-tee-nitro-host` | Enclave 主机代理 |
| `base-proof-tee-registrar` | TEE 证明者注册服务 |
| `base-proof-tee-nitro-verifier` | Nitro 认证验证（no_std） |
| `base-proof-tee-nitro-attestation-prover` | 基于 risc0/Boundless 的认证证明 |

#### ZK 子系统（4 crates）

| Crate | 职责 |
|---|---|
| `base-zk-service` | ZK 证明服务 |
| `base-zk-client` | ZK 客户端（SP1 guest，no_std） |
| `base-zk-db` | 证明状态数据库 |
| `base-zk-outbox` | 证明输出队列 |

#### Succinct / SP1 集成（11 crates）

| Crate | 职责 |
|---|---|
| `base-proof-succinct-client-utils` | SP1 客户端工具（guest 侧，no_std） |
| `base-proof-succinct-host-utils` | SP1 主机端工具 |
| `base-proof-succinct-build-utils` | SP1 ELF 构建 |
| `base-proof-succinct-proof-utils` | 证明工具 |
| `base-proof-succinct-signer-utils` | 签名工具 |
| `base-proof-succinct-elfs` | 预编译 ELF 二进制 |
| `base-proof-succinct-ethereum-client-utils` | 以太坊客户端（guest，no_std） |
| `base-proof-succinct-ethereum-host-utils` | 以太坊主机端 |
| `base-proof-succinct-prove` | 证明脚本（multi, agg） |
| `base-proof-succinct-scripts` | 辅助脚本 |
| `base-proof-succinct-validity` | Validity proof 生成 |

#### SP1 Guest Programs（独立子 workspace，3 crates）

位于 `crates/proof/succinct/programs/`，使用独立 workspace（excluded from root），编译目标为 `riscv32im-succinct-zkvm-elf`：

| Crate | 职责 |
|---|---|
| `aggregation` | 聚合证明 guest 程序 |
| `range/ethereum` | 范围证明 guest 程序（以太坊） |
| `range/utils` | 范围证明工具 |

### 6. `crates/infra/` — 运维基础设施

| Crate | 职责 |
|---|---|
| `audit-archiver-lib` | Bundle 审计归档（→ S3） |
| `basectl` | 基础设施控制 TUI/CLI |
| `based` | 出块健康检查 sidecar |
| `ingress-rpc-lib` | 交易/Bundle 入口 RPC |
| `load-tests` | 负载测试 |
| `websocket-proxy` | WebSocket 扇出代理 |

### 7. `crates/common/` — 共享类型

大部分 crate 支持 no_std，供证明系统 guest 程序复用。

| Crate | 职责 | no_std |
|---|---|---|
| `base-common-consensus` | 共识类型 | yes |
| `base-common-genesis` | Genesis 配置 | yes |
| `base-common-chains` | 链定义 | yes |
| `base-common-evm` | EVM 工具 | yes |
| `base-common-flz` | FastLZ 压缩 | yes |
| `base-common-precompiles` | 预编译合约 | yes |
| `base-common-precompile-storage` | 预编译存储 | yes |
| `base-precompile-macros` | 预编译 proc-macro | yes |
| `base-common-rpc-types` | RPC 类型 | yes |
| `base-common-rpc-types-engine` | Engine API 类型 | yes |
| `base-access-lists` | 访问列表 | yes |
| `base-common-flashblocks` | Flashblocks 类型 | no |
| `base-bundles` | Bundle 类型 | no |
| `base-common-network` | 网络定义 | no |
| `base-common-signer` | 签名器 | no |

### 8. `crates/utilities/` — 通用工具库

| Crate | 职责 |
|---|---|
| `base-cli-utils` | CLI 公共宏和初始化 |
| `base-reth-cli` | Reth CLI 集成 |
| `base-jwt` | JWT 认证 |
| `base-health` | 健康检查服务（axum） |
| `base-metrics` | 指标收集（Prometheus） |
| `base-runtime` | Tokio 运行时配置 |
| `base-tx-manager` | L1 交易管理 |
| `base-balance-monitor` | 余额监控 |
| `base-ring-buffer` | 环形缓冲区 |
| `base-test-utils` | 测试工具 |

## 其他 Workspace Members

| 路径 | 职责 |
|---|---|
| `devnet/` | 系统/E2E 测试框架 |
| `etc/tools/witness-diff` | Witness 差异比较工具 |
| `actions/harness` | CI/CD 测试 harness |

## Workspace 规模统计

- **Root workspace members**：127
  - `bin/`：18（binary 入口）
  - `crates/`：106（8 大功能域）
  - 其他：3（`devnet`, `actions/harness`, `etc/tools/witness-diff`）
- **独立子 workspace**（SP1 guest programs，excluded from root）：3 crates
- **总计**：130 crates
- **功能域**：8 个主要域 + 3 个辅助域（etc/tools, actions, devnet）
