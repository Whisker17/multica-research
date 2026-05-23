# 附录 A: 证据索引

> 本附录汇总 final-report.md 中所有代码路径引用、来源文档和证据等级标注。

---

## A.1 分析对象仓库与版本

| 仓库 | 本地路径 | 版本/标签 | 语言 |
|------|----------|-----------|------|
| `base/base` | `references/codebase/base` | 本地快照 (reth v2.2.0, SP1 v6.2.1) | Rust |
| `mantle/reth` | `references/codebase/mantle/reth` | v1.9.3-mantle-arsia.1 | Rust |
| `mantle/kona` | `references/codebase/mantle/kona` | v2.2.3 | Rust |
| `mantle/op-succinct` | `references/codebase/mantle/op-succinct` | v3.4.1 fork | Rust |
| `mantle-v2` | `references/codebase/mantle/mantle-v2` | 本地快照 | Go |
| `mantle/op-geth` | `references/codebase/mantle/op-geth` | 本地快照 | Go |

---

## A.2 Execution Client 证据索引

### Base 执行客户端

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| 零 fork 上游策略 | `Cargo.toml` → reth git tag v2.2.0 | 直接依赖上游，无 fork | 强 |
| 独立 crate 架构 | `crates/execution/` (20 crates) | 与上游代码物理隔离 | 强 |
| BaseEvmFactory | `crates/execution/evm/` | `ConfigureEvm` trait 实现 | 强 |
| BaseSpecId | `crates/execution/evm/` | 自定义 hardfork spec 标识 | 强 |
| PrecompilesMap | `crates/execution/evm/` | 哈希表分发预编译 | 强 |
| 动态预编译（Beryl） | `crates/execution/evm/` | `install()` + `activation_admin_address` | 强（代码），未激活（部署） |
| BaseTransactionValidator | `crates/execution/txpool/` | 含 `estimated_da_size` DA 估算 | 强 |
| BaseOrdering | `crates/execution/txpool/` | DA 成本感知排序 | 强 |
| FP 窗口 Trie 存储 | `crates/execution/trie/` | 双后端 MDBX + 内存，独立裁剪 | 强 |
| BaseProofStoragePruner | `crates/execution/trie/` | 专用 FP 窗口裁剪器 | 强 |
| CachedExecutor | `crates/execution/flashblocks*/cached_execution.rs` | `FlashblocksCachedExecutionProvider` | 强 |
| spawn_deferred_trie_task | `crates/execution/` | 后台 trie 计算 | 强 |
| MeteringCollector | `crates/execution/metering/` | 多维资源计量 via EVM Inspector | 强 |
| PriorityFeeEstimator | `crates/execution/metering/` | 滚动优先费估算 | 强 |
| ingress-rpc | `bin/ingress-rpc/` + `crates/infra/ingress-rpc-lib/` | 独立交易入口 | 强 |
| base-bundles | `crates/execution/bundles/` | Bundle 竞价 + Tips MEV | 强 |

### Mantle 执行客户端

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| reth fork 定制 | `mantle/reth/crates/optimism/` (~15 文件) | 添加式修改 | 强 |
| mantle.rs / mantle_ext.rs | `mantle/reth/crates/optimism/` | Mantle 特有逻辑入口 | 强 |
| mantle_hardforks/ | `mantle/reth/crates/optimism/` | 硬分叉定义 | 强 |
| MantleHardforks trait | `mantle/reth/crates/optimism/` | Trait bound 实现 | 强 |
| OpSpecId::ARSIA | `mantle-xyz/revm` fork | revm 中新增 spec | 强 |
| op-geth 核心修改 | `mantle/op-geth/core/state_transition.go` | 30+ 文件修改 | 强 |
| BVM_ETH 双代币 | `mantle/op-geth/core/state_transition.go` | State-level BVM_ETH 操作 | 强 |
| tokenRatio | `mantle/op-geth/core/types/rollup_cost.go` | MNT 价格缩放 | 强 |
| Operator Fee | `mantle/op-geth/core/types/rollup_cost.go` | 三层费用模型 | 强 |
| 5 套硬编码分叉表 | `mantle/op-geth/core/vm/` | EVM 配置 | 强 |
| preconf 子系统 | `mantle/op-geth/preconf/` | 预确认检查器 | 中（DefaultMinerConfig.EnablePreconfChecker=false） |
| MetaTx 拒绝 | `mantle/reth/` | 交易池过滤 | 强 |
| FlashBlockBuilder | `mantle/reth/flashblocks/` | Consumer 端重新执行 | 强 |
| 依赖 fork 链 | `mantle/reth → op-reth → paradigmxyz/reth` | 三层 fork | 强 |
| 依赖库 fork | `mantle-xyz/revm`, `mantle-xyz/op-alloy`, `mantle-xyz/evm` | 3 个额外 fork | 强 |

---

## A.3 Batcher 证据索引

### Base Batcher

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| 8 crate 模块化架构 | `crates/batcher/` (comp, encoder, core, service, source, blobs, admin, binary) | 清晰职责边界 | 强 |
| poll_interval = 1s | `crates/batcher/service/service.rs` | 轮询间隔配置 | 强 |
| Brotli10 硬编码 | `crates/batcher/encoder/src/encoder.rs:331-337` | `CompressionAlgo::Brotli10 + CompressorType::Shadow` | 强 |
| Shadow Compressor | `crates/batcher/encoder/src/encoder.rs:331-337` | 双压缩器比较取优 | 强 |
| max_channel_duration = 2 | 配置 | 2 L1 blocks (~24s) | 强 |
| HybridBlockSource | `crates/batcher/source/` | WS + HTTP 混合，256-block 去重窗口 | 强 |
| biased select! | `crates/batcher/service/` | 确定性事件优先级 | 强 |
| RecentTxScanner | `crates/batcher/` | `MAX_CHECK_RECENT_TXS_DEPTH = 128`, `SCAN_FETCH_CONCURRENCY = 16` | 强 |
| force_blobs_when_throttling | `crates/batcher/` | 节流时强制 blob | 强 |
| 8 Admin RPC 端点 | `crates/batcher/admin/` | 含 start/stop/flush/status/setLogLevel | 强 |
| getBatcherStatus | `crates/batcher/admin/` | 返回 `{stopped, in_flight, da_backlog_bytes}` | 强 |
| Frame-DA 解耦 | `crates/batcher/encoder/` + `crates/batcher/core/` | Encoder 产出 DA-agnostic frames | 强 |
| BatchComposer | `crates/batcher/comp/src/composer.rs` | Block→SingleBatch 转换器，不涉及压缩 | 强 |
| VariantCompressor | `crates/batcher/comp/src/variant.rs` | `from_timestamp` Fjord 后选 Brotli10（未被 encoder 调用） | 强 |

### Mantle Batcher

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| PollInterval = 6s | `mantle-v2/op-batcher/` | 默认轮询间隔 | 强 |
| 默认 Zlib 压缩 | `mantle-v2/op-batcher/` CLI 默认 `derive.Zlib` | 压缩算法选择 | 强 |
| MaxChannelDuration = 0 | `mantle-v2/op-batcher/` | 无固定超时限制 | 强 |
| CheckRecentTxsDepth = 0 | `mantle-v2/op-batcher/` | 默认禁用 | 强 |
| MantleBlobs() vs Blobs() | `mantle-v2/op-batcher/` | Channel 层耦合 DA 格式 | 强 |
| 30+ Prometheus metrics | `mantle-v2/op-batcher/` | 含 PID 控制器指标 | 强 |
| 4 种 Throttling 策略 | `mantle-v2/op-batcher/` | Step/Linear/Quadratic/PID | 强 |
| Auto DA 模式 | `mantle-v2/op-batcher/` | 每 10 秒评估 blob vs calldata | 强 |
| AltDA 框架 | `mantle-v2/op-batcher/` | Plasma 支持 | 强 |
| 3 个 Admin 端点 | `mantle-v2/op-batcher/` | 仅 throttle 相关 | 强 |
| HTTP only 数据源 | `mantle-v2/op-batcher/` | 无 WS 订阅支持 | 强 |
| MantleDaSwitch 死代码 | `mantle-v2/op-batcher/` | EigenDA 残留引用 | 弱 |

---

## A.4 Derivation Pipeline 证据索引

### Base Derivation

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| base-consensus-derive (no_std) | `crates/consensus/derive/` | 核心 pipeline，`#![cfg_attr(not(feature = "metrics"), no_std)]` | 强 |
| OnlinePipeline | `crates/consensus/derive/` | std RPC provider，节点生产使用 | 强 |
| Oracle-backed pipeline | `crates/consensus/derive/` | no_std oracle provider，ZK 证明使用 | 强 |
| StatefulAttributesBuilder | `crates/consensus/derive/` | Hardfork 升级入口 | 强 |
| base-consensus-engine | `crates/consensus/engine/` | Task Queue 优先级堆 | 强 |
| Task Queue 优先级 | `crates/consensus/engine/` | Seal(4) > Insert(3) > Consolidate(2) > Finalize(1) | 强 |
| Engine::build() | `crates/consensus/engine/` | 绕过 queue 直接 FCU | 强 |
| base-consensus-service | `crates/consensus/service/` | 服务编排 | 强 |
| base-consensus-sources | `crates/consensus/sources/` | 区块签名器（非 L1 数据源） | 强 |
| SafeDB | `crates/consensus/safedb/` | redb B-tree，合成锚点 reset | 强 |
| base-consensus-gossip | `crates/consensus/gossip/` | 区块分发 | 强 |

### Mantle Derivation

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| Go 生产路径 | `mantle-v2/op-node/rollup/derive/` | mantle_pipeline.go, mantle_blob_source.go, mantle_system_config.go | 强 |
| Rust FPP 路径 | `mantle/kona/.../derive/` | DerivationPipeline + MantleBlobSource | 强 |
| mantle_format_failed toggle | `mantle/kona/.../derive/mantle_blob.rs` | 需手动对齐 Go blobToggle() | 强 |
| MantleBlobSource | `mantle/kona/.../derive/` + `mantle-v2/op-node/rollup/derive/` | Go/Rust 双实现 | 强 |
| Arsia 7 upgrade deposit tx | `mantle/kona/` + `mantle-v2/op-node/` | 两种语言各实现一遍 | 强 |
| OpHardforks N:1 映射 | `mantle/reth/` | Skadi = Regolith...Isthmus | 强 |
| OraclePipeline<O, L1, L2, DA> | `mantle/kona/` | 泛化 DA 类型参数 | 强 |
| MantleEthereumDataSource | `mantle/kona/` | DA 注入实现 | 强 |
| WitnessExecutor::type DA | `mantle/op-succinct/` | 一行类型别名完成 DA 切换 | 强 |
| EngineController 事件驱动 | `mantle-v2/op-node/rollup/` | PipelineDeriver → AttributesHandler → EngineController | 强 |
| SafeDB (Go) | `mantle-v2/op-node/` | Pebble LSM-tree，reset 语义差异 | 强 |
| ~14 no_std crates | `mantle/kona/` | 广泛 no_std 覆盖 | 强 |

---

## A.5 证明系统证据索引

### Base 证明系统

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| base-proof-client (no_std) | `crates/proof/client/` | 共享核心，三种运行时 | 强 |
| base-proof-driver | `crates/proof/driver/` | 证明驱动层 | 强 |
| base-proof-executor | `crates/proof/executor/` | 证明执行层 | 强 |
| base-proof-primitives | `crates/proof/primitives/` | 证明原语 | 强 |
| base-proof-host | `crates/proof/host/` | Native FP 执行 | 强 |
| base-zk-client | `crates/proof/zk-client/` | SP1 zkVM 编译目标 | 强 |
| nitro-enclave | `crates/proof/nitro*/` | TEE 运行时 | 强 |
| SP1 v6.2.1 | `Cargo.toml` | ZK 框架版本 | 强 |
| AggregateVerifier (ABI) | `crates/proof/*/` sol! 绑定 | 多证明协调合约 | 中（仅 ABI） |
| TEEProverRegistry (ABI) | `crates/proof/*/` sol! 绑定 | TEE 签名者注册 | 中（仅 ABI） |
| DisputeGameFactory (ABI) | `crates/proof/*/` sol! 绑定 | 争议游戏工厂 | 中（仅 ABI） |
| AnchorStateRegistry (ABI) | `crates/proof/*/` sol! 绑定 | 锚点状态注册 | 中（仅 ABI） |
| DelayedWETH (ABI) | `crates/proof/*/` sol! 绑定 | Bond 管理 | 中（仅 ABI） |
| INTERMEDIATE_BLOCK_INTERVAL | `crates/proof/` | 默认 512，中间输出根 | 强 |
| Plonk 默认验证 | `crates/proof/` | ZK 验证类型 | 强 |
| TEE 轮询 12s | `crates/proof/` | TEE Proposer 配置 | 强 |
| TEE 512 block 间隔 | `crates/proof/` | TEE 证明间隔 | 强 |

### Mantle 证明系统

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| Validity Proof Proposer | `mantle/op-succinct/validity/` | Rust Proposer 完整实现 | 强 |
| SP1 v6.1.0 | `mantle/op-succinct/Cargo.toml` | ZK 框架版本 | 强 |
| OPSuccinctDisputeGame | `mantle/op-succinct/contracts/` | game type 6 | 强 |
| OPSuccinctFaultDisputeGame | `mantle/op-succinct/contracts/` | game type 42 | 强 |
| ZK FP 服务层已移除 | `mantle/op-succinct/` workspace | Rust 服务不在 workspace | 强 |
| Groth16 默认验证 | `mantle/op-succinct/` | ZK 验证类型 | 强 |
| Cantina 审计 | `mantle/op-succinct/` | 安全审计 | 强 |
| Cannon MIPS64 VM | `mantle-v2/cannon/` | 继承自上游 | 强 |
| op-challenger Go Agent | `mantle-v2/op-challenger/` | 争议代理 | 强 |
| kona FPP | `mantle/kona/` | Fault Proof Program | 强 |
| Keeper Ziren zkVM | `mantle/op-geth/cmd/keeper/` | MIPS ISA，实验性 | 中 |
| VP 公开部署资料 | Succinct 案例研究（2025-09-16）+ L2BEAT | 1h finality，6h withdrawals | 中（链上地址未确认） |

---

## A.6 Flashblocks 证据索引

### Base Flashblocks

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| FlashblocksServiceBuilder | `crates/builder/` | Producer 自研 | 强 |
| 250ms 可配置间隔 | `crates/builder/` | Flashblock 生成间隔 | 强 |
| CachedExecutor | `crates/execution/flashblocks*/cached_execution.rs` | parent_hash + tx position 缓存 | 强 |
| ReceiptRootTaskHandle | `crates/execution/flashblocks*/` | 后台流式 receipt root | 强 |
| Per-flashblock metering | `crates/execution/metering/` | 执行时间/状态根 gas/DA 字节 | 强 |
| websocket-proxy | `bin/websocket-proxy/` | Brotli 压缩、速率限制、API-key 认证 | 强 |
| eth_sendRawTransactionSync | `crates/execution/rpc/` | 同步交易提交 | 强 |
| eth_subscribe("newFlashblocks") | `crates/execution/rpc/` | Flashblocks 订阅 | 强 |

### Mantle Flashblocks

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| FlashBlockBuilder | `mantle/reth/flashblocks/` | Consumer 端重新执行 | 强 |
| op-conductor ws relay | `mantle-v2/op-conductor/ws/` | WebSocket 中继 | 强 |
| rollup-boost Producer | 外部仓库 | 不在分析范围 | N/A |
| op-geth 无 Flashblocks 支持 | `mantle/op-geth/` | 仅 reth 支持 | 强 |
| pending block/receipt/tx | `mantle/reth/` | 基础 pending 状态 | 强 |

---

## A.7 基础设施与工程工具证据索引

### Base

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| basectl | `bin/basectl/` | TUI 监控/控制 | 强 |
| load-tester | `bin/load-tester/` + `crates/infra/load-tests/` | 负载测试工具 | 强 |
| Justfile | 根目录 `Justfile` | 统一构建/测试/部署 | 强 |
| workspace.package.version = "0.0.0" | `Cargo.toml` | 统一版本管理 | 强 |
| Rust edition 2024, MSRV 1.93 | `Cargo.toml` | 编译器版本 | 强 |

### Mantle

| 证据项 | 代码路径 | 说明 | 证据等级 |
|--------|----------|------|----------|
| 三仓库 Rust workspace | `mantle/reth`, `mantle/kona`, `mantle/op-succinct` | 独立管理 | 强 |
| 升级顺序约束 | 跨仓库 | `revm → op-alloy → evm → reth/kona → op-succinct` | 强 |
| Go monorepo | `mantle-v2/` | op-node + op-batcher + op-proposer + contracts | 强 |

---

## A.8 来源文档索引

本报告整合了以下研究输出文档的分析结果：

### M0 阶段（架构映射）

| 文档编号 | 文件路径 | 内容概要 |
|----------|----------|----------|
| WHI-442 | `outputs/WHI-442_base-rust-monorepo-architecture/` | Base monorepo 6 大架构特征 |
| WHI-443 | `outputs/WHI-443_mantle-multi-repo-architecture/` | Mantle 多仓库架构分析 |
| WHI-444 | `outputs/WHI-444_component-mapping-and-architecture-diff/` | 组件映射表、架构图、上游依赖、tradeoff 分析 |

### M1 阶段（流程分析）

| 文档编号 | 文件路径 | 内容概要 |
|----------|----------|----------|
| WHI-445 | `outputs/WHI-445_flowchart-l2-tx-lifecycle/` | L2 交易生命周期流程图 |
| WHI-446 | `outputs/WHI-446_flowchart-batcher-lifecycle/` | Batcher 批次提交流程图 |
| WHI-447 | `outputs/WHI-447_flowchart-derivation-pipeline/` | Derivation pipeline 流程图 |
| WHI-448 | `outputs/WHI-448_flowchart-proof-system/` | 证明系统流程图 |
| WHI-449 | `outputs/WHI-449_flowchart-supplementary-scenarios/` | 补充场景流程图 |

### M2 阶段（深度对比）

| 文档编号 | 文件路径 | 内容概要 |
|----------|----------|----------|
| WHI-450 | `outputs/WHI-450_comparison-execution-client/` | 执行客户端对比 |
| WHI-451 | `outputs/WHI-451_comparison-batcher/` | Batcher 对比 |
| WHI-452 | `outputs/WHI-452_comparison-derivation-pipeline/` | Derivation pipeline 对比 |
| WHI-453 | `outputs/WHI-453_comparison-proof-system/` | 证明系统对比 |
| WHI-454 | `outputs/WHI-454_comparison-l1-contracts-bridge/` | L1 合约对比 |

### M3 阶段（综合评估与路线图）

| 文档编号 | 文件路径 | 内容概要 |
|----------|----------|----------|
| WHI-455 | `outputs/WHI-455_base-advantages-assessment/` | Base 优势特性评估与优先级排序 |
| WHI-456 | `outputs/WHI-456_mantle-optimization-roadmap/` | Mantle 优化实施路线图 |
| WHI-457 | `outputs/WHI-457_final-report/` | 本最终报告 |

---

## A.9 证据等级汇总统计

| 证据等级 | 数量 | 占比 | 说明 |
|----------|------|------|------|
| 强证据 | ~90+ 项 | ~85% | 代码中明确存在且可确认 |
| 中证据 | ~10 项 | ~10% | 代码存在但部署/启用未确认 |
| 弱证据 | ~5 项 | ~5% | 基于推断 |

所有"弱证据"项均在报告正文中明确标注，不用于支撑核心结论或 P0/P1 建议。
