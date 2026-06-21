# Base Beryl vs Azul 研究报告

> **项目**: base-beryl-vs-azul  
> **基线**: base/base v1.1.1 (`01e732cd`) / v1.1.0 (`a3c3011b`) / v1.0.1 Azul (`955a18b1`)  
> **日期**: 2026-06-21  
> **来源**: 6 份经对抗审查的研究 section（WHI-245/246/247/248/249/251）

---

## 1. Executive Summary

本报告回答两个核心问题：

**Beryl 相对 Azul 增加了什么？** Beryl 在 Azul 已确立的独立基础设施底座（单客户端架构、Multiproof 证明系统、Reth V2 执行引擎、Osaka EVM 对齐）之上，引入三大变更：(1) **协议层合规 Token 原生化**——B20 预编译级 Token 标准，将合规能力（策略引擎、角色权限、功能门控）从应用层下沉至协议层；(2) **资本效率提升**——single-proof 提款最终确认窗口从 7 天计划缩短至 5 天（源码已确认，L1 部署待 Beryl mainnet 激活后完成），执行吞吐 +8.1%（Reth v2.2.0→v2.3.0）；(3) **Precompile 基础设施成型**——宏系统 + 存储提供者接口 + 11 个 metrics 家族，为未来协议层内置模块提供可复用的开发框架。

**上线信心如何评估？** 7 天 Sepolia 公网窗口（2026-06-18→06-25）是一条 23 天多环境测试管线（Devnet E2E → Zeronet 负载 → Sepolia 公网）的最终确认步骤，而非独立测试阶段。信心基础来自四个维度：B20/precompile 子系统的附加式架构（blast radius = 零）、59 个 unique 审计票据、4,851 行专项测试 harness、以及高密度 release 工程（21+4 RC）。残余风险集中在：MEV/经济攻击面不可测、提款 5 天周期覆盖边缘、3 个 L1 部署证据缺口、审计 backport 验证窗口极短（2 天）。核心洞察：7 天窗口的合理性建立在 B20/precompile 子系统的附加性质之上——如涉及共识或 derivation 层修改，同样的窗口将不具备充分的信心基础。

---

## 2. Beryl vs Azul：增加了什么

### 2.1 升级定位：从基础设施到产品化

Azul（2026 年 5 月 28 日主网激活）回答的是「Base 能否脱离 OP Stack 独立运行」——通过单客户端架构、Multiproof 证明系统和 Osaka EVM 对齐，完成了与 OP Stack 的解耦。Beryl（计划 2026 年 6 月 25 日主网激活）回答的是「Base 如何在协议层面服务受监管的机构客户」——通过 B20 预编译级 Token 标准和提款窗口缩短，将战略重心从基础设施建设转向协议层产品化。[TW inference] 这一转向表明 Base 正将 Azul 建立的技术优势转化为面向机构市场的差异化竞争力。

（来源：beryl-narrative-summary/final.md §1；beryl-scope-inventory/final.md §1）

### 2.2 变更全景：141 个功能 Commit 的分域分布

v1.0.1→v1.1.1 range 内共 143 个 non-merge commit，其中 141 个归入 Beryl 功能范围，2 个为 Cobalt-only 排除（`cobalt_timestamp: None` 运行时不可达）。15 域 taxonomy 映射到 3 个官方 scope：

| 官方 Scope | 域 | Commit 数 | 占比 |
|-----------|------|----------|------|
| **B20 Token 标准** | B20-Token-Core(18), B20-Asset(14), B20-Factory(10), PolicyRegistry(4), ActivationRegistry(1) | 47 | 33% |
| **Precompile 基础设施** | Precompile-Infra(11), EVM-Integration(5) | 16 | 11% |
| **Withdrawal 7→5 天 + Reth V2** | Protocol-RethV2(8) | 8 | 6% |
| *非 scope 归属* | Prover-Service(43), CI-Tooling(14), Test-Infra(5), Activation-Governance(6), EIP-8130(2) | 70 | 50% |

Top 域 Prover-Service（43 commit）为 gRPC→JSON-RPC 重构等基础设施变更，不在运行时交易路径中。B20/precompile 子系统合计 63 commit（45%），涵盖全部新增用户可交互 precompile。

（来源：beryl-scope-inventory/final.md §1.2, §3.1, §4.1）

### 2.3 Scope 1：B20 预编译级 Token 标准

#### 2.3.1 架构概览

B20 是 Base 链的预编译级合规 Token 标准，通过 4 个动态 precompile 实现：

| Precompile | 地址类型 | 功能 |
|-----------|---------|------|
| **B20Factory** | 固定地址（`0xB20F...`） | Token 创建、确定性地址派生（`keccak256(creator, salt)`）、initCalls 特权窗口 |
| **BerylLookup** | 动态匹配（`0xb2` + 9 零字节 + variant 判别值） | B20 地址 → Asset/Stablecoin precompile 分发 |
| **PolicyRegistryPrecompile** | 固定地址（`0x8453...0002`） | 四维策略控制（TransferSender/Receiver/Executor + MintReceiver）、ALLOWLIST/BLOCKLIST |
| **ActivationRegistry** | 固定地址（`0x8453...0001`） | 3 个功能（PolicyRegistry、B20Stablecoin、B20Asset）的 activate/deactivate 门控 |

（来源：b20-token-system/final.md §1-§4；beryl-precompile-infra/final.md §3.6）

#### 2.3.2 Token 变体与能力

B20 支持两个变体，共享 7 trait 能力层：

| 变体 | 精度 | 特有能力 | 适用场景 |
|------|------|---------|---------|
| **B20Asset** | 可配置 | multiplier、批量铸造 | 证券型代币、RWA Token |
| **B20Stablecoin** | 6 位（硬编码，BOP-349/PSRC-27） | currencyCode | 受监管稳定币 |

7 角色权限模型：DEFAULT_ADMIN、SUPPLY_ADMIN、MINTER、BURNER、PAUSE_ADMIN、BLOCKLIST_ADMIN、NETWORK_ADMIN。ERC-2612 permit 和 EIP-712 签名支持。供应上限（mintCap）和三维暂停（mint/burn/transfer 独立暂停）。

#### 2.3.3 合规策略引擎

PolicyRegistry 提供四维策略控制：

- **TransferSender / TransferReceiver / TransferExecutor**：控制转账的发起方、接收方和执行方（如 transferFrom 的 msg.sender）
- **MintReceiver**：控制铸造接收方
- 策略类型：ALLOWLIST（白名单）或 BLOCKLIST（黑名单），ALWAYS_ALLOW=0（EVM 零值默认）
- 2-step admin transfer、activation-gate-aware calldata classification

#### 2.3.4 审计加固

v1.0.1→v1.1.1 tag range 内 **59 个 unique 审计票据**（57 BOP + 2 PSRC），覆盖 B20 全部核心组件（Token Core、Asset、Factory、PolicyRegistry）及底层基础设施（precompile-storage、precompile-macros）。代表性修复：BOP-227（transferFrom executor policy）、BOP-233（role admin mutation guard）、BOP-356/380（slot arithmetic checked_add）、BOP-349（stablecoin decimals hardcode）、PSRC-27（stablecoin decimals verification）。

（来源：b20-token-system/final.md §1-§7；sepolia-window-confidence/final.md §3.2）

### 2.4 Scope 2：Precompile 基础设施

#### 2.4.1 宏系统

三个核心 proc macro 提供类 Solidity 存储布局的编译期代码生成：

- `#[contract(addr = "0x...")]`：解析存储结构体，生成 slot 分配、ContractStorage impl、构造函数
- `#[precompile]`：生成 precompile singleton `install()` 方法和 `precompile()` dispatcher
- `#[derive(Storable)]`：生成 StorableType / Storable trait impl，含 slot 布局常量

Slot bin-packing 规则模拟 Solidity 32 字节边界 + 左对齐累积偏移。ERC-7201 命名空间隔离。调试期碰撞检测。

#### 2.4.2 存储提供者接口

`PrecompileStorageProvider` trait（30+ 方法）提供完整的 EVM 存储抽象：

- **EIP-2200 Gas-Stipend 守卫**：sstore 在剩余 gas ≤ 2300 时失败，保证 `.transfer()` 安全假设
- **EIP-2929 冷/热存储计价**：sload 100（warm）/ 2600（cold）gas；sstore 带冷罚金
- **EIP-3529 Net-Metering Refund**：sstore_refund 传播到 gas 计数器
- **Checkpoint/Commit/Revert 原子性**：每个可能失败的存储操作被 checkpoint guard 包裹，OOG 时不泄露 warm 状态或持久化变更
- **Slot 算术 checked_add**（BOP-356/380）：所有 additive slot 路径使用 `checked_add` + `SlotOverflow` 防护
- **非规范 Bool 值拒绝**：仅接受 `U256::ZERO`/`U256::ONE`，防止 dirty word 攻击

唯一生产实现 `EvmPrecompileStorageProvider` 还支持 EIP-8037 State Gas 分层收费和静态调用保护。

#### 2.4.3 可观测性体系

`PrecompileCallObserver` trait 与 precompile 执行解耦，定义 6 个 hook 方法。生产实现 `BerylPrecompileMetricsObserver` 提供 11 个 metrics family（namespace `base.beryl.precompile`）：calls_total、duration_seconds、input_bytes、gas_used、state_gas_used、gas_refunded、errors_total、zero_gas_success_total、b20_created_total、batch_items、internal_calls/bytes。BerylErrorKind 16 种错误分类，通过 SolError selector 匹配 revert bytes。

#### 2.4.4 Blast Radius 结论

**对标准以太坊 precompile 地址（`0x01`–`0x12`、`0x100` 等）——blast radius 为零。**

四层隔离证据：

1. **附加模式**：`beryl()` 直接返回 `azul()`（`provider.rs:166-168`）——静态 precompile 集合完全不变
2. **Fork 门控**：动态 precompile 安装被 `>= BaseUpgrade::Beryl` 条件门控，Beryl 激活前完全不存在
3. **地址空间分区**：`PrecompilesMap::get()` static-first-then-lookup 优先级保证标准 precompile 地址永远不经过 BerylLookup；B20 编码地址（`0xb2` 前缀）与标准 precompile 地址空间不重叠
4. **存储地址隔离**：每个 precompile 使用自身地址作为存储操作的 address 参数，不污染既有合约状态

**残余风险**：满足 B20 结构编码（`0xb2` + 9 零字节 + variant 判别值）的非 B20Factory 部署地址会被 BerylLookup 拦截。碰撞概率 2^{-87}（约 6.5 × 10^{-27} per address），属预期设计选择，受 fork 门控和地址编码双重约束。

（来源：beryl-precompile-infra/final.md §1-§6）

### 2.5 Scope 3：提款窗口 7→5 天 + Reth V2

#### 2.5.1 提款最终确认窗口变更

**核心发现**：`SLOW_FINALIZATION_DELAY` 是 Solidity `constant`（非 immutable、非 storage variable），编译时硬编码入 bytecode。7→5 天的变更**必须部署新的 AggregateVerifier 合约实现**。

| 参数 | Azul（L1 已部署） | Beryl（源码已确认） | 变更方式 |
|------|-----------------|-------------------|---------|
| `SLOW_FINALIZATION_DELAY` | 7 days (604,800s) | 5 days (432,000s) | 部署新合约 |
| `FAST_FINALIZATION_DELAY` | 1 day (86,400s) | 不变 | — |
| `PROOF_THRESHOLD` | 1 | 不变 | — |

- 源码变更：`base/contracts` @ v8.2.0 (`3a25c8cf`)，commit `3a25c8cf`（2026-05-18, author: roger-bai-coinbase）
- 当前已部署：AggregateVerifier `0xeEcb8A5944...D259`（Azul 时期，SLOW=7 天）
- **L1 部署待确认**：新 AggregateVerifier 部署地址、DisputeGameFactory setImplementation 注册交易、链上 after-value eth_call 确认——均待 Beryl mainnet 激活（2026-06-25）后完成

**base/base 代码库无 withdrawal finalization 相关变更**——提款窗口缩短纯粹是 L1 合约参数调整（在 `base/contracts` 仓库），不涉及 L2 执行客户端代码。

**资本效率影响**：Single-proof 路径锁仓期缩短 ~28.6%，LP 资本周转率理论提升 1.4x。Base 官方声明将继续缩短窗口。

（来源：protocol-reth-withdrawal/final.md §1）

#### 2.5.2 Reth V2 增量升级

Reth 版本从 v2.2.0（Azul）升级到 v2.3.0（Beryl）：

| 维度 | Azul (reth v2.2.0) | Beryl (reth v2.3.0) | 变化 |
|------|-------------------|-------------------|------|
| 吞吐 | ~1.4 Ggas/s | ~1.5 Ggas/s | +8.1% |
| Storage 引擎 | Storage V2（已由 v2.0.0+ 默认） | 不变 | — |
| State root | Proof V2 + Sparse Trie Cache | + 增量优化（更快 proof/trie 路径） | — |
| BAL 支持 | 初始 Amsterdam BAL | 扩展验证、存储、网络、RPC | — |
| Flashblocks | 基础支持 | pending-state fast path + metadata 修复 + 可配置 ping | — |
| P2P | reth 默认 | 自定义 80/80 peer defaults | — |
| Snapshotter | 标准文件比较 | BLAKE3 hash 差异化 | — |

**重要区分**：~50% 的磁盘占用缩减属于 Azul 时期已引入的 Reth 2.0 lineage（Storage V2 架构跃迁），不计入 Beryl 增量。Beryl 的增量贡献为 +8.1% 吞吐和上述 Flashblocks/P2P/Snapshotter 优化。

8 个 Protocol-RethV2 commit 分析：核心 backport `#3471`（572a3c564）完成 reth v2.2.0→v2.3.0 依赖升级（44 文件，1618+/1280-）；`#3480`（a3c3011b1）修复 overlay builder state trie cache；`#3482` 设置 EL peer defaults 80/80；`#3315` flashblocks pending-state fast path；`#3269` flashblocks ping interval 可配置化；`#3114` BLAKE3 static file chunks。

#### 2.5.3 Required Software 版本矩阵

| 层级 | Binary | Mainnet | Sepolia | Upstream |
|------|--------|---------|---------|----------|
| EL | `base-reth-node` | v1.1.1 (`01e732cd`) | v1.1.0 (`a3c3011b`) | reth v2.3.0 |
| CL | `base-consensus` | v1.1.1 | v1.1.0 | — |
| Utility | `basectl` | v1.1.1 | v1.1.0 | — |
| Node | `base/node` | v1.1.1 (`7dc1d2b`) | v1.1.0 (`f565946`) | — |

构建工具链：Rust 1.93、mold 2.40.4、ubuntu:24.04、`--profile maxperf`。三个 binary 均从 `base/base` 仓库构建。v1.1.0→v1.1.1 仅 3 个 commit（flashblocks metadata backport + mainnet 激活时间戳 + 版本号），功能代码近乎完全相同。

（来源：protocol-reth-withdrawal/final.md §2-§3）

### 2.6 Azul→Beryl 能力对照表

| 维度 | Azul 基线 | Beryl 新增/变更 |
|------|----------|----------------|
| 原生 Token 标准 | 无（依赖 ERC-20 合约部署） | B20 预编译级 Token（Asset/Stablecoin 双变种）、B20Factory |
| 合规策略引擎 | 无 | PolicyRegistry 四维策略 + ActivationRegistry 功能门控 |
| Token 权限模型 | 无 | 7 角色 AccessControl + ERC-2612 permit + 供应上限 + 三维暂停 |
| 预编译框架 | 静态预编译集（标准 Ethereum） | 4 个动态预编译 + 宏系统 + 存储提供者接口 + 11 metrics 家族 |
| 动态预编译安装 | 无 | `>= BaseUpgrade::Beryl` fork-gated + BerylLookup 动态地址匹配 |
| 执行引擎 | Reth v2.2.0（含 Storage V2 + Proof V2） | Reth v2.3.0 增量：+8.1% 吞吐、80/80 peers、Flashblocks 优化 |
| 提款窗口（single-proof） | 7 天 | 5 天（源码已确认，L1 部署待完成） |
| 提款窗口（dual-proof） | 1 天（proofCount ≥ 2） | 不变（ZK 成本高，实际触发率低） |
| 证明系统 | Multiproof（TEE+ZK, PROOF_THRESHOLD=1） | 不变（Beryl 继承） |
| EVM 对齐 | Osaka 7 EIPs | 不变（Beryl 继承） |

（来源：beryl-narrative-summary/final.md §3）

---

## 3. 上线信心分析

### 3.1 多环境上线时间线

Beryl 的 Sepolia→Mainnet 窗口为 **7 天**（2026-06-18→06-25），相比 Azul 的 38 天窗口缩短 5.4 倍。但 7 天不是完整测试周期——Beryl 遵循 Devnet → Zeronet → Sepolia → Mainnet 四阶段递进管线：

| 阶段 | 日期 (UTC) | 关键事件 |
|------|-----------|---------|
| RC 起始 | 06-02 | v1.1.0-rc.1 + B20 Load Test 框架（PR #3050） |
| Zeronet 激活 | 06-05 17:00 | `bb831a49c` (#3214), timestamp `1780678800` |
| Devnet E2E | 06-08 | Beryl precompile E2E 测试覆盖（`092517562` #3104） |
| Zeronet B20 激活 | 06-08 | B20 负载测试（`296a09ffe` #3266） |
| BOP Batch Backport | 06-10 | 至少 6 个 backport commit 集中合入 |
| v1.1.0 Release | 06-12 | Sepolia 版本定稿（`a3c3011b`），21 个 RC |
| Sepolia 激活 | 06-18 18:00 | timestamp `1781805600`；status.base.org 公告确认 |
| v1.1.1 Release | 06-18 | 4 个 RC + release（`01e732cd`），仅 3 commit delta |
| Mainnet 激活 | 06-25 18:00 | timestamp `1782410400`；status.base.org 公告确认 |

**总测试周期**：从首个 RC（06-02）到 Mainnet 激活（06-25）为 **23 天**。

### 3.2 四大信心来源

#### 3.2.1 测试覆盖深度

- **Beryl 专项 Test Harness**：`actions/harness/tests/beryl/` 下 11 个文件、4,851 行代码，覆盖 B20 全生命周期（mint→transfer→burn）、PolicyRegistry CRUD、Factory 创建与地址推导、安全边界（role mutation guard、executor policy、overflow 防护）、ActivationRegistry 开关、fork 门控行为
- **Devnet E2E**：PR #3104 验证 precompile 在完整 block production 环境中的端到端行为
- **负载测试**：Zeronet（100 senders / 20M GPS / 30s）和 Sepolia 配置（200 senders / 60M GPS / 60s），含 B20 workload 支持

**测试缺口**：Sepolia 负载测试配置中 B20 类型为 commented out；跨 precompile 复合序列未覆盖；gas metering 边界条件未专项测试。

#### 3.2.2 审计加固密度

v1.0.1→v1.1.1 tag range 内 **59 个 unique 审计票据**（57 BOP + 2 PSRC），覆盖 B20 全部核心组件及底层基础设施。Backport 集中在 2026-06-10（至少 6 个 backport commit），v1.1.0 release 在 2 天后（06-12）——审计修复与 Sepolia release 之间的验证窗口仅 1-2 天。

#### 3.2.3 架构低风险

B20/precompile 子系统（63/141 commit）为纯附加式设计，blast radius = 零（见 §2.4.4）。ActivationRegistry 提供运行时回退能力——通过 `setActivation(address, false)` 可禁用单个 precompile 而无需硬分叉。非 precompile 域（Reth V2 8 commit、Prover-Service 43 commit 等）风险由独立研究和生产运维数据约束，但不享有同等的架构隔离保证。

#### 3.2.4 组织与发布节奏

- v1.1.0（Sepolia）：21 个 RC / 10 天，其中 06-10~06-12 密集迭代 14 个 RC（审计 backport 后）
- v1.1.1（Mainnet）：4 个 RC / 当天，仅 3 commit delta
- 激活日期通过独立 commit 设定，保留最后一刻推迟的能力

### 3.3 残余风险与待主网复核

| # | 风险项 | 严重度 | Sepolia 覆盖能力 |
|---|--------|--------|-----------------|
| 1 | MEV/经济攻击面不可测 | **高** | 不可覆盖——测试网无真实 MEV 生态 |
| 2 | 提款 5 天周期覆盖边缘 | **高** | 边缘——7 天窗口内首次完整验证刚好完成，无冗余 |
| 3 | 3 个 L1 部署证据缺口 | **高** | 不可覆盖——时序性限制 |
| 4 | 审计 backport 验证窗口极短 | **中-高** | 弱——06-10 backport 到 06-12 release 仅 2 天 |
| 5 | Zeronet 与主网经济攻击面差距 | **中** | 不可覆盖——无真实价值锁定 |
| 6 | 长尾状态累积效应 | **中** | 不可覆盖——需数月暴露 |
| 7 | BerylLookup 地址拦截影响面 | **中** | 弱——概率 2^{-87} 理论可忽略，实际未量化 |
| 8 | Sepolia 负载测试 B20 缺失 | **中** | 自身缺口——B20 类型 commented out |

**3 个 L1 部署证据缺口（来自 WHI-251）**：

| # | 缺口 | 预期解决 |
|---|------|---------|
| (a) | 新 AggregateVerifier 部署地址 | Beryl 主网激活前 |
| (b) | DisputeGameFactory setImplementation tx | Beryl 主网激活前 |
| (c) | 5 天 after-state eth_call 确认 | 部署后 |

**待主网上线后复核清单**（8 项）：B20 precompile 首笔主网调用 → PolicyRegistry 首次 blocklist 生效 → 提款 5 天窗口首完整周期 → L1 AggregateVerifier 部署确认 → DisputeGameFactory 参数确认 → 负载行为对照 → B20 实例数 100+ 观察 → 首次 ActivationRegistry 紧急禁用验证。

### 3.4 核心判断

[TW inference] 7 天窗口的上线决策是一个已知风险收益权衡：信心基础来自「附加式架构 + 多环境管线 + 高密度审计 + 回退能力」的组合，而非 Sepolia 公网测试本身。7 天 Sepolia 窗口更像是部署管线的最终确认步骤。这一策略的合理性建立在 Beryl 用户可见风险面（B20/precompile）的附加性质之上——blast-radius-zero 仅适用于该子系统。非 precompile 域（Reth V2、Prover-Service）的风险由独立研究和生产运维数据约束，但不享有同等的架构隔离保证。

（来源：sepolia-window-confidence/final.md §1-§5）

---

## 4. 对 Mantle 的启示

### 4.1 协议层合规 vs 应用层合规

Base 通过 B20 在协议层引入合规 Token 标准（随 mainnet 激活生效），RWA Token 化可在 L2 层原生实现。Mantle 目前采用应用层方案。两种路径各有权衡：

- **协议层**：更强一致性保证、更低 DApp 集成成本，但牺牲灵活性、增加协议升级复杂度
- **应用层**：更灵活、不增加协议负担，但合规执行依赖各 DApp 自行实现

[TW inference] 如果 Mantle 追求 RWA/机构化战略，需在下一个升级周期内评估是否需要等价的协议层合规能力，以及在 OP Stack 兼容架构下实现的可行性。

### 4.2 资本效率对标

Base 计划将 single-proof 提款窗口从 7 天缩短至 5 天，且声明将继续缩短。根据 L2Beat 数据，Mantle 当前挑战期为 7 天。Mantle 已通过 OP Succinct 引入 ZK 证明（partially live），为未来缩短窗口提供技术基础。

需关注：(a) Mantle 自身是否有缩短挑战窗口的路线图；(b) Base 持续缩短窗口对两链桥接流动性竞争格局的影响。

### 4.3 Precompile 框架的可复用性

Beryl 的 precompile 基础设施不只是 B20 载体，而是通用的 stateful precompile 开发框架。如果 Mantle 未来需要定制协议层功能（如原生 DID、链上身份、定制化 gas 模型），Beryl 的框架设计提供了参考路径。需评估：Mantle 基于 OP Stack 的架构（op-geth / mantle-v2）是否具备类似的协议层扩展性。

### 4.4 战略要点

1. **合规能力差距正在形成**——Base 通过 B20 在协议层引入合规 Token 标准。Mantle 需评估等价能力的需求和可行性
2. **资本效率竞争即将启动**——Base 提款窗口计划从 7 天缩短至 5 天，且将继续缩短。Mantle 需评估自身缩短窗口的技术可行性
3. **协议层可编程性值得关注**——Beryl 的 precompile 框架展示了协议层快速构建定制功能的能力

（来源：beryl-narrative-summary/final.md §4）

---

## 5. Traceability Matrix

| 报告章节 | 源 Section | Multica Issue | Topic Slug | 研究轮次 | Final Commit |
|---------|-----------|---------------|------------|---------|-------------|
| §2.2 变更全景 | beryl-scope-inventory/final.md | WHI-245 (`39fb2d70-49f6-4ca5-8b4f-90509cb703fe`) | beryl-scope-inventory | Round 2 | `5d04446` (integration) |
| §2.3 B20 Token 标准 | b20-token-system/final.md | WHI-246 (`1e03500e-9646-4ca2-84fc-34bfc01301c1`) | b20-token-system | Round 2 | integration on main |
| §2.4 Precompile 基础设施 | beryl-precompile-infra/final.md | WHI-247 (`fb7245dd-682d-445f-b9cd-96c5708e4505`) | beryl-precompile-infra | Round 2 | integration on main |
| §2.5 提款窗口 + Reth V2 | protocol-reth-withdrawal/final.md | WHI-251 (`0170ae77-f28e-473f-9059-c98f48691453`) | protocol-reth-withdrawal | Round 2 | integration on main |
| §2.1, §2.6 升级定位与对照 | beryl-narrative-summary/final.md | WHI-248 (`2f090be1-2460-4d8c-bc9e-379cb9a358eb`) | beryl-narrative-summary | Round 2 | integration on main |
| §3 上线信心分析 | sepolia-window-confidence/final.md | WHI-249 (`7f357aad-260d-4ddd-afb6-89274cd67208`) | sepolia-window-confidence | Round 3 | integration on main |
| §4 对 Mantle 的启示 | beryl-narrative-summary/final.md | WHI-248 | beryl-narrative-summary | — | — |

---

## 6. Evidence Appendix

### 6.1 代码仓库引用

| Repo | Tag / Branch | Commit | 引用章节 | 结论来源类型 |
|------|-------------|--------|---------|-------------|
| `base/base` | v1.1.1 (mainnet) | `01e732cdbae0c624d652da9e608d7d3fe0f9c74b` | §2.2, §2.3, §2.4, §2.5, §3 | 代码分析 |
| `base/base` | v1.1.0 (Sepolia) | `a3c3011b16dae73aaea455ec0a5ff614e65b7d0a` | §2.5.3, §3.1 | 代码分析 |
| `base/base` | v1.0.1 (Azul baseline) | `955a18b189196c6f663235140180e5bcf51cd044` | §2.2, §2.5.2 | 代码分析 |
| `base/contracts` | v8.2.0 | `3a25c8cfe300fdf62b8d860876c1fa86fc9885b4` | §2.5.1 | 代码分析 |
| `base/node` | v1.1.1 | `7dc1d2b8727e0eaf78180368bc39ffa3e3dc1b6b` | §2.5.3 | 代码分析 |
| `base/node` | v1.1.0 | `f56594616b9d47cdfc3cd8d18d7735890789dd02` | §2.5.3, §3.1 | 代码分析 |
| `paradigmxyz/reth` | v2.3.0 | — | §2.5.2 | 官方 release notes |
| `alloy-evm` | v0.36.0 (dep) | checksum `a6e494...` | §2.4.4 | 代码分析（依赖库） |

### 6.2 关键文件与行号引用

| 文件路径 | Tag | 行号 | 观察内容 | 引用章节 |
|---------|-----|------|---------|---------|
| `crates/common/precompiles/src/provider.rs` | v1.1.1 | L163-168 | `beryl()` 返回 `azul()` | §2.4.4 Layer 1 |
| `crates/common/precompiles/src/provider.rs` | v1.1.1 | L189-205 | `install_with_observer()` Beryl 门控 | §2.4.4 Layer 2 |
| `crates/common/precompiles/src/lookup.rs` | v1.1.1 | L30-47 | BerylLookup 地址匹配 | §2.4.4 Layer 3 |
| `crates/common/precompile-storage/src/provider.rs` | v1.1.1 | L19-106 | PrecompileStorageProvider trait | §2.4.2 |
| `crates/common/precompile-storage/src/evm.rs` | v1.1.1 | L195-201 | EIP-2200 stipend guard | §2.4.2 |
| `crates/common/precompile-storage/src/evm.rs` | v1.1.1 | L158-226 | EIP-2929 cold/hot + checkpoint | §2.4.2 |
| `crates/common/precompile-storage/src/types/slot.rs` | v1.1.1 | L44-82 | checked_add 溢出防护 | §2.4.2 |
| `crates/common/precompile-storage/src/types/primitives.rs` | v1.1.1 | L39-52 | 非规范 Bool 拒绝 | §2.4.2 |
| `crates/common/precompile-macros/src/lib.rs` | v1.1.1 | L24-56 | 三个核心 proc macro | §2.4.1 |
| `crates/common/chains/src/upgrade.rs` | v1.1.1 | L6-40, L44-57 | BaseUpgrade enum + ETH spec mapping | §2.4.4 |
| `crates/common/evm/src/beryl_metrics.rs` | v1.1.1 | L15-83 | 11 个 metrics family | §2.4.3 |
| `crates/common/precompiles/src/observer.rs` | v1.1.1 | L10-58 | PrecompileCallObserver trait | §2.4.3 |
| `crates/common/precompiles/src/metrics.rs` | v1.1.1 | L166-200, L546-591 | BerylErrorKind + calldata gas | §2.4.3 |
| `src/L1/proofs/AggregateVerifier.sol` | v8.2.0 | L48-68 | SLOW/FAST constants | §2.5.1 |
| `Cargo.toml` | v1.1.1 | — | reth deps tag=v2.3.0 | §2.5.2 |
| `Cargo.toml` | v1.0.1 | — | reth deps tag=v2.2.0 | §2.5.2 |
| `versions.env` | base/node v1.1.1 | L1-3 | BASE_RETH_NODE_TAG=v1.1.1 | §2.5.3 |
| `Dockerfile` | base/node v1.1.1 | L1, L40 | Rust 1.93, maxperf build | §2.5.3 |
| `crates/execution/cli/src/node.rs` | v1.1.1 | L24-25 | EL peer defaults 80/80 | §2.5.2 |
| `actions/harness/tests/beryl/` | v1.1.1 | — | 11 文件 4851 行 | §3.2.1 |
| `crates/infra/load-tests/examples/` | v1.1.1 | — | devnet.yaml + sepolia.yaml | §3.2.1 |
| `crates/common/precompiles/src/b20_factory/variant.rs` | v1.1.1 | L66-73 | B20Variant::from_address() | §2.4.4 |

### 6.3 PR 与 Commit 引用

| PR# | Commit | 描述 | Tag 归属 | 引用章节 |
|-----|--------|------|---------|---------|
| #3471 | `572a3c564` | Reth v2.2.0→v2.3.0 backport | v1.1.0 | §2.5.2 |
| #3480 | `a3c3011b1` | Overlay builder state trie cache fix | v1.1.0 | §2.5.2 |
| #3482 | `611f50563` | EL peer defaults 80/80 | v1.1.0 | §2.5.2 |
| #3315 | `9ea1c2c34` | Flashblocks pending-state fast path | v1.1.0 | §2.5.2 |
| #3269 | `779f91815` | Flashblocks ping interval configurable | v1.1.0 | §2.5.2 |
| #3114 | `f4042a84e` | BLAKE3 static file chunks | v1.1.0 | §2.5.2 |
| #3132 | `1b86d43d0` | Bump revm-inspectors | v1.1.0 | §2.5.2 |
| #3634 | `01e732cdb` | Flashblocks metadata backport (v1.1.1) | v1.1.1 | §2.5.2 |
| #3627 | `4e84ba3d1` | Mainnet activation date | v1.1.1 | §3.1 |
| #3624 | `d21284244` | Version bump to 1.1.1 | v1.1.1 | §3.1 |
| #3104 | `092517562` | Beryl precompile E2E (Devnet) | v1.1.0 | §3.2.1 |
| #3050 | — | B20 workload for load test | — | §3.2.1 |
| #3214 | `bb831a49c` | Zeronet Beryl activation | — | §3.1 |
| #3266 | `296a09ffe` | Zeronet B20 activation | — | §3.1 |
| #293 | `3a25c8cf` | Update finalization delay (base/contracts) | v8.2.0 | §2.5.1 |

### 6.4 外部来源

| 来源 | URL / 标识 | 引用章节 | 结论来源类型 | 观察日期 |
|------|-----------|---------|-------------|---------|
| L2BEAT Base Chain | l2beat.com/scaling/projects/base | §2.5.1, §4.2 | 官方（链上数据聚合） | 2026-06-20 |
| Paradigm Reth 2.0 Blog | paradigm.xyz/2026/04/releasing-reth-2-0 | §2.5.2 | 官方 | 2026-06-20 |
| reth v2.3.0 Release Notes | github.com/paradigmxyz/reth/releases | §2.5.2 | 官方 | 2026-06-20 |
| Base Beryl Blog | blog.base.dev/introducing-base-beryl | §2.5.1, §4.2 | 官方 | 2026-06-20 |
| status.base.org 公告 | status.base.org | §3.1 | 官方 | 2026-06-21 |
| Optimism specs fault-dispute-game.md | ethereum-optimism/specs | §2.5.1 | 官方（规范文档） | 2026-06-20 |
| Etherscan AggregateVerifier | etherscan.io/address/0xeEcb8A5944...D259 | §2.5.1 | 官方（链上验证） | 2026-06-20 |
| base-azul-upgrade multiproof-architecture/final.md | 本仓库 | §2.5.1 | 前期研究 | — |

### 6.5 结论来源类型说明

- **代码分析**：直接从代码仓库特定 tag/commit 的源文件推导的结论，附行号引用
- **官方**：项目方官方发布的文档、博客、release notes、链上合约数据
- **代码推断**：基于代码分析但涉及推理判断的结论（报告中标注为 `[TW inference]`）
- **前期研究**：引用本仓库中已完成对抗审查的前期研究 section

---

## Unresolved Items

| 项目 | 状态 | 说明 |
|------|------|------|
| 提款窗口 L1 部署 | 待 2026-06-25 | 新 AggregateVerifier 部署地址、DisputeGameFactory 注册交易、链上 after-value 确认 |
| Sepolia 负载测试 B20 覆盖 | 未确认 | `sepolia.yaml` 中 B20 类型为 commented out，实际是否运行未知 |
| Beryl mainnet 激活 | 待 2026-06-25 | 计划 2026-06-25 18:00 UTC 激活 |
