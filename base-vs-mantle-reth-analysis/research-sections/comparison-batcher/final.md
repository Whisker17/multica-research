# Channel 与 Frame 管理对比

## 1. Channel 构建策略

### Base（`crates/batcher/encoder/`）

**Channel 创建时机**：
- `BatchEncoder` 在当前 channel 为 `None` 或已关闭时创建新 channel
- 每个 channel 使用 `ShadowCompressor` + `Brotli10`（硬编码于 `encoder.rs:331-337`，不依赖 Fjord 判断）

**Channel 关闭条件**（4 种，`encoder/src/metrics.rs`）：

| 关闭原因 | 常量 | 触发条件 |
|---|---|---|
| 大小满 | `REASON_SIZE_FULL` | 压缩器报告 `Full` |
| 超时 | `REASON_TIMEOUT` | L1 head 推进 ≥ `max_channel_duration` 个 L1 block |
| 强制关闭 | `REASON_FORCE` | Admin 命令（pause/flush/shutdown） |
| 丢弃 | `REASON_DISCARD` | Reorg / parent hash 不匹配 |

**Channel 超时配置**：
- `max_channel_duration = 2`（L1 blocks）— **非常激进**
- `sub_safety_margin = 0`
- 含义：每 2 个 L1 block（约 24 秒）至少提交一次，即使 channel 未满

### Mantle（`mantle-v2/op-batcher/batcher/`）

**Channel 创建时机**（`channel_manager.go` → `ensureChannelWithSpace`）：
- 当 `currentChannel == nil` 或当前 channel 已满时创建
- `ChannelBuilder` 根据 `BatchType` 调用 `NewSpanChannelOut` 或 `NewSingularChannelOut`

**Channel 关闭条件**（7 种，`channel_builder.go`）：

| 关闭原因 | 错误常量 | 触发条件 |
|---|---|---|
| 目标大小达到 | `ErrInputTargetReached` | 输入数据达到目标 |
| 最大 frame index | `ErrMaxFrameIndex` | Frame 数量达上限 |
| 最大持续时间 | `ErrMaxDurationReached` | 超过 MaxChannelDuration |
| Channel 超时 | `ErrChannelTimeoutClose` | 接近 ChannelTimeout |
| 序列窗口关闭 | `ErrSeqWindowClose` | 接近 SequencerWindowSize |
| 终止 | `ErrTerminated` | 外部终止信号 |
| 压缩器满 | `ErrCompressorFull` | 压缩器报告满 |

**Channel 超时公式**（`channel_builder.go`）：
```
timeout = min(MaxChannelDuration, ChannelTimeout - SubSafetyMargin, SeqWindowSize - SubSafetyMargin)
```

**Channel 超时配置**：
- `MaxChannelDuration = 0`（默认，无时间限制；仅受序列窗口约束）
- `SubSafetyMargin = 10` blocks
- `ChannelTimeout` = `ChannelTimeoutBedrock`（Granite 后切换为 `ChannelTimeoutGranite`）

### Channel 超时策略对比

```
Base:   ---|-------|-------|-------|---  (每 2 个 L1 block 提交)
             24s     24s     24s

Mantle: ---|--------------------------------|---  (无固定时间限制)
           仅在 channel 满或接近序列窗口时提交
```

**影响**：
- Base 的激进策略优先保证 L2 → L1 提交延迟
- Mantle 的宽松策略优先保证压缩效率（更多数据填满一个 channel）

---

## 2. Frame 切分策略

### Base

**关键常量**（`comp/src/channel_out.rs`）：
- `FRAME_V0_OVERHEAD = 23` bytes（16 channel ID + 2 frame number + 4 length + 1 is_last）

**Frame 编码格式**：
```
frame = channel_id(16) ++ frame_number(2) ++ frame_data_length(4) ++ frame_data ++ is_last(1)
```

**配置**（`bin/batcher/src/cli.rs` + `encoder/src/config.rs`）：
- CLI `--target-frame-size` 默认是 `130044`
- Blob 模式转换为 `EncoderConfig` 时会扣除 `BLOB_DERIVATION_PREFIX_SIZE`，实际 encoder 默认 `target_frame_size = MAX_BLOB_FRAME_SIZE = 130043`
- `max_frame_size = target_frame_size`
- `target_num_frames = 1`（默认每 channel 1 个 frame，即 1 个 blob）

**Blob 打包**（`core/src/submissions.rs`）：
- 多 frame 打包进单个 blob 在**提交队列层**完成（`submit_pending`）
- 逐个 frame 填充 blob 直到 `BLOB_MAX_DATA_SIZE`

### Mantle

**Frame 大小**（`service.go:266-282`）：
- Calldata 模式：`MaxFrameSize = MaxL1TxSize - 1 = 119999`（默认 `MaxL1TxSize = 120000`）
- Blob/Auto 模式：`MaxFrameSize = eth.MaxBlobDataSize - 1 ≈ 130043`
- AltDA 约束：`MaxFrameSize` 不能超过 `altda.MaxInputSize = 130672`

**Frame 提取**（`channel.go` → `NextTxData`）：
- 每次取 `MaxFramesPerTx()` 个 frame
  - Calldata：1 frame/tx
  - Blob：`TargetNumFrames` frames/tx（默认 1）

**Mantle 特有的 Blob 编码**（`tx_data.go`）：

```
Pre-Arsia（Mantle 特化）:
  MantleBlobs() → RLP 编码 frame 数组 → 打包到多个 blob
  格式: [frame_with_version, frame_with_version, ...]

Post-Arsia（标准 OP Stack）:
  Blobs() → 每个 blob 一个 frame（标准格式）
```

这是 Mantle 与上游 OP Stack 的**重要分歧**：在 Arsia 硬分叉前，Mantle 使用 RLP 列表编码将多个 frame 打包到 blob 中。

---

## 3. Span Batch 支持

### Base

**支持状态**: 完全支持

**配置**（`encoder/src/config.rs`）：
- `batch_type = Single`（默认）或 `Span`
- CLI 参数：`--batch-type single|span|0|1`

**限制**：
- `SpanBatchBeforeFjord` — Fjord 前不可用
- `SpanBatchRequiresScheduledFjord` — 需要 Fjord 已在 rollup config 中调度

**每 block 额外开销**：
- `SPAN_BATCH_PER_BLOCK_OVERHEAD = 50` bytes

**压缩策略交互**：
- Span batch 使用 `approx_compr_ratio` 估算压缩后大小，达到 `target_frame_size × target_num_frames` 时关闭 channel
- 实际 channel 压缩器仍是 `ShadowCompressor + Brotli10`，不是单独切到 `RatioCompressor`

### Mantle

**支持状态**: 完全支持

**配置**（`flags/flags.go`）：
- `BatchType = 0`（Singular，默认）或 `1`（Span）
- `MaxBlocksPerSpanBatch = 0`（默认无限制）

**Holocene 后行为**：
- 严格排序：span 开始后不允许 block 间重排序

---

## 4. 多 Frame 管理对比

### Base 的方法

```
BatchEncoder                    SubmissionQueue
    │                               │
    │  产生 frames                   │
    │──────────────────────────────→│
    │                               │
    │                     submit_pending():
    │                     逐 frame 填入 blob
    │                     直到 BLOB_MAX_DATA_SIZE
    │                               │
    │                     一个 blob = 一个 L1 tx
    │                               │
```

- **encoder 与 DA 解耦**：encoder 只产生 frame，不关心最终是 blob 还是 calldata
- **blob 打包在提交层**：`SubmissionQueue::submit_pending` 负责将 frame 打包进 blob
- **并发控制**：`Arc<Semaphore>` 限制 `max_pending_transactions`（默认 1）

### Mantle 的方法

```
ChannelManager                   Driver
    │                               │
    │  NextTxData():                │
    │  取 MaxFramesPerTx 个 frames  │
    │──────────────────────────────→│
    │                               │
    │                     构造 tx candidate:
    │                     Pre-Arsia: MantleBlobs()
    │                     Post-Arsia: Blobs()
    │                               │
    │                     TxManager.Send()
    │                               │
```

- **channel 层直接控制 frame 数量**：`NextTxData` 一次取出固定数量 frame
- **Mantle 特化 blob 编码**：Pre-Arsia 使用 RLP 列表格式
- **并发控制**：`MaxPendingTransactions = 1`（默认）

---

## 5. 配置对比表

| 配置项 | Base 默认 | Mantle 默认 | 说明 |
|---|---|---|---|
| Max Channel Duration | **2** L1 blocks | **0**（无限制） | Base 极其激进 |
| Sub Safety Margin | 0 | 10 blocks | Mantle 更保守 |
| Target Frame Size | CLI 默认 130044；blob 模式下 encoder 实际 130043 | ~130043 (blob) / 119999 (calldata) | 近似一致 |
| Target Num Frames | 1 | 1 | 一致 |
| Batch Type | Single | Singular (0) | 一致，均支持 Span |
| Max Blocks Per Span | 无此配置 | 0（无限制） | Mantle 有额外控制 |
| Max L1 Tx Size | 无（blob 模式） | 120000 | Mantle calldata 限制 |

---

## 6. 关键发现

### Base 的设计亮点

1. **激进的 `max_channel_duration = 2`**：牺牲压缩效率换取极低的 L2→L1 提交延迟
2. **编码器-DA 解耦**：encoder 产出 frame，submission queue 处理 blob 打包，职责清晰
3. **统一的 frame 格式**：无分叉特化编码（如 Mantle 的 MantleBlobs），减少 derivation 端复杂性
4. **`SPAN_BATCH_PER_BLOCK_OVERHEAD` 显式常量**：span batch 开销可预测

### Mantle 的特殊性

1. **`MantleBlobs()` RLP 编码**：Pre-Arsia 特化格式增加了 derivation 复杂性，需要 `MantleBlobSource` 双格式解码 + sticky fallback
2. **7 种 channel 关闭原因**（vs Base 的 4 种）：更细粒度的关闭语义，但也增加了调试复杂性
3. **`MaxBlocksPerSpanBatch` 配置**：提供 span batch 的额外安全阀

### Mantle 可借鉴之处

1. **考虑缩短 `MaxChannelDuration`**：当前默认 0（无限制）导致提交延迟完全取决于 channel 填满速度
2. **简化 blob 编码路径**：Arsia 后已对齐上游，可清理 Pre-Arsia 代码路径减少维护负担
3. **将 frame/blob 打包逻辑从 channel 层分离**：参考 Base 的提交队列设计


---

# Batcher 代码来源确认

## Base Batcher

**语言**: Rust  
**类型**: 完全自研，完整 batcher daemon  
**位置**: `base/crates/batcher/` + `base/bin/batcher/`

### 代码结构

Base 的 batcher 采用模块化 crate 架构，共 8 个子 crate + 1 个 binary：

| 子 Crate | 路径 | 职责 |
|---|---|---|
| `comp` | `crates/batcher/comp/` | 压缩/编码库：Brotli、Zlib 压缩器，Shadow/Ratio 压缩策略，Channel 输出编码 |
| `encoder` | `crates/batcher/encoder/` | 批处理编码引擎：`BatchEncoder` 核心，Channel 管理，Frame 切分，DA 类型选择 |
| `core` | `crates/batcher/core/` | 驱动器：`BatchDriver` 状态机，提交队列，节流控制，Admin 命令处理 |
| `service` | `crates/batcher/service/` | 服务层：RPC 连接管理，配置组装，Safe Head 轮询，最近交易扫描 |
| `source` | `crates/batcher/source/` | 数据源抽象：WS + HTTP 混合模式，L2 Block 订阅，L1 Head 跟踪，Reorg 检测 |
| `blobs` | `crates/batcher/blobs/` | Blob 编解码：EIP-4844 blob 的打包与解包 |
| `admin` | `crates/batcher/admin/` | Admin JSON-RPC 服务：启停控制、节流调整、状态查询 |
| **binary** | `bin/batcher/` | CLI 入口：clap 命令行参数，`main.rs` 仅 4 行 |

### 关键特征

- **单一二进制文件**：所有功能编译进一个可执行文件
- **不依赖 op-reth fork**：直接基于上游 reth 构建
- **Rust async/await**：基于 tokio，使用 `biased select!` 实现事件优先级
- **Metrics 端口默认 7300**（Prometheus）

---

## Mantle Batcher

Mantle 的 batcher 由两个独立组件构成：

### 1. Mantle op-batcher（Go，完整 daemon）

**语言**: Go  
**类型**: OP Stack fork，完整 batcher daemon  
**位置**: `mantle-v2/op-batcher/`

```
op-batcher/
├── batcher/
│   ├── driver.go              # 主驱动器，事件循环
│   ├── service.go             # 服务初始化，配置组装
│   ├── batch_submitter.go     # 批次提交逻辑
│   ├── channel.go             # Channel 状态管理
│   ├── channel_builder.go     # Channel 构建器（7 种关闭原因）
│   ├── channel_config.go      # Channel 配置
│   ├── channel_config_provider.go  # 动态 DA 切换（auto 模式）
│   ├── channel_manager.go     # Channel 生命周期管理
│   ├── config.go              # CLI 配置结构
│   ├── tx_data.go             # 交易数据构造（含 MantleBlobs 特殊编码）
│   ├── sync_actions.go        # 同步操作处理
│   └── throttler/             # 节流控制器
│       ├── controller.go      # 控制器调度
│       ├── linear_strategy.go # 线性策略
│       ├── quadratic_strategy.go  # 二次策略（默认）
│       ├── pid_strategy.go    # PID 策略（实验性）
│       └── step_strategy.go   # 阶跃策略
├── compressor/
│   ├── compressors.go         # 压缩器工厂
│   ├── ratio_compressor.go    # Ratio 压缩器
│   ├── shadow_compressor.go   # Shadow 压缩器
│   └── non_compressor.go      # 无压缩（测试用）
├── flags/                     # CLI flags 定义
├── metrics/                   # Prometheus metrics
├── rpc/                       # Admin RPC API
├── config/                    # 配置类型
└── cmd/main.go                # 入口
```

**关键职责**：收集 L2 block → 压缩编码 → 构建 Channel/Frame → DA 提交（Calldata/Blob/AltDA）→ Nonce 管理 → 确认跟踪 → 节流控制

### 2. Mantle Kona batcher comp（Rust，纯库）

**语言**: Rust  
**类型**: 压缩/编码库，非独立进程  
**位置**: `kona/crates/batcher/comp/`

```
batcher/comp/
├── src/
│   ├── lib.rs          # 模块声明
│   ├── channel_out.rs  # ChannelOut 实现（Frame 输出）
│   ├── config.rs       # 配置结构
│   ├── variant.rs      # 压缩算法调度
│   ├── brotli.rs       # Brotli 压缩
│   ├── zlib.rs         # Zlib 压缩
│   ├── shadow.rs       # Shadow 压缩策略
│   ├── ratio.rs        # Ratio 压缩策略
│   ├── traits.rs       # Compressor 接口
│   └── types.rs        # 枚举定义
└── examples/
    └── batch_to_frames.rs  # 使用示例
```

**关键限制**：
- **不是独立进程**：仅提供 Channel 编码和压缩能力
- **无 DA 处理**：不涉及 Calldata/Blob/AltDA 选择
- **无 L1 提交**：不含 TxManager、Gas/Nonce 管理
- **无节流/Metrics**：纯粹的编解码库

### 两者的集成关系

```
┌─────────────────────────────────────┐
│  mantle-v2/op-batcher (Go daemon)   │
│  ├─ 收集 L2 blocks                  │
│  ├─ 调用内置 Go compressor 包       │
│  ├─ Channel/Frame 管理              │
│  ├─ DA 选择 & L1 提交               │
│  └─ 节流、Metrics、Admin RPC        │
└─────────────────────────────────────┘
            │
            │  无直接运行时依赖
            │  （仅共享协议规范）
            ▼
┌─────────────────────────────────────┐
│  kona/crates/batcher/comp (Rust lib)│
│  ├─ 压缩算法实现                     │
│  ├─ ChannelOut 编码                  │
│  └─ 独立库，未被其他 crate 依赖      │
└─────────────────────────────────────┘
```

**重要说明**：Mantle 的 kona batcher comp 与 Go op-batcher 之间**没有运行时集成**。两者是独立的实现，分别用于不同场景：
- op-batcher（Go）：生产环境的完整 batcher daemon
- kona comp（Rust）：独立的压缩/编码库，声明在 Kona workspace 中但**未被任何 derivation 或 binary crate 依赖**，当前处于未集成状态

---

## 对比总结

| 维度 | Base | Mantle |
|---|---|---|
| 语言 | Rust（单一语言） | Go（daemon）+ Rust（库） |
| 架构 | 单一 monorepo，8 个 crate 模块化 | 两个独立组件，无运行时集成 |
| Batcher daemon | `base/crates/batcher/*` + `base/bin/batcher/` | `mantle-v2/op-batcher/` |
| 压缩库 | 嵌入 daemon 的 `comp` crate | 独立的 `kona/crates/batcher/comp` |
| 代码来源 | 完全自研 | OP Stack fork + Mantle 特化修改 |
| 对上游依赖 | 直接依赖 reth（非 fork） | fork 了 optimism/optimism 全套 |


---

# Batcher 各维度对比表

## 总览对比

| 维度 | Base | Mantle |
|---|---|---|
| **语言** | Rust | Go (daemon) + Rust (库) |
| **代码来源** | 完全自研 | OP Stack fork + 定制 |
| **架构** | 8 crate 模块化 monorepo | Go op-batcher + Kona comp 库 |
| **Batcher daemon** | `base/crates/batcher/*` + `base/bin/batcher/` | `mantle-v2/op-batcher/` |

---

## 压缩策略对比

| 维度 | Base | Mantle |
|---|---|---|
| **支持的压缩算法** | Zlib, Brotli9/10/11 | Zlib, Brotli9/10/11 |
| **默认压缩算法** | Brotli10（硬编码，`encoder.rs:334`） | Zlib (CLI 默认) |
| **压缩策略类型** | Shadow, Ratio | Shadow, Ratio, None |
| **默认压缩策略** | Shadow | Shadow (CLI 默认) |
| **近似压缩比** | 0.6 | 0.6 |
| **自动算法切换** | 硬编码 Brotli10，无需切换（`comp/src/variant.rs` 存在 Fjord 判断逻辑但未被调用） | 需手动配置 |
| **SAFE_COMPRESSION_OVERHEAD** | 51 bytes | 51 bytes |
| **CLOSE_OVERHEAD_ZLIB** | 9 bytes | 9 bytes |
| **no_std 支持** | Zlib 支持, Brotli 需 std | Zlib 支持, Brotli 需 std (Kona) |

---

## Channel 与 Frame 管理对比

| 维度 | Base | Mantle |
|---|---|---|
| **Channel 关闭原因数** | 4 种 | 7 种 |
| **Max Channel Duration** | **2 L1 blocks (~24s)** | **0 (无限制)** |
| **Sub Safety Margin** | 0 | 10 blocks |
| **Target Frame Size (Blob)** | CLI 默认 130044；encoder 实际 130043 | ~130043 |
| **Target Frame Size (Calldata)** | N/A | 119999 |
| **Target Num Frames** | 1 | 1 |
| **Frame V0 Overhead** | 23 bytes | 23 bytes |
| **Batch Type 默认** | Single | Singular (0) |
| **Span Batch 支持** | 是 (Fjord 后) | 是 |
| **Span Batch 每 block 开销** | 50 bytes | N/A (Go 侧计算) |
| **Max Blocks Per Span** | 无此配置 | 0 (无限制) |
| **Blob 编码格式** | 标准 OP 格式 | Pre-Arsia: MantleBlobs (RLP), Post-Arsia: 标准 OP |
| **Frame→Blob 打包位置** | 提交队列层 (解耦) | Channel 层 (耦合) |

---

## DA 策略对比

| 维度 | Base | Mantle |
|---|---|---|
| **默认 DA** | **Blob** | **Calldata** (CLI 默认) |
| **支持的 DA 类型** | Blob, Calldata | Blob, Calldata, Auto, AltDA |
| **Auto 模式 (动态切换)** | 不支持 | 支持 (每 10s 评估) |
| **AltDA / Plasma** | 不支持 | 支持 (通用 HTTP 接口) |
| **EigenDA** | 不支持 | 仅死代码引用 |
| **Blob 格式** | 标准 OP | 双格式 (Mantle RLP + 标准 OP) |
| **节流时强制 Blob** | `force_blobs_when_throttling=true` | Auto 模式下 prefer blob |
| **DA 失败 Fallback** | Requeue + 重试 | Channel invalidation + DA 切换 |
| **Derivation 端格式处理** | 单一格式 | Sticky fallback 状态机 |

---

## L1 提交优化对比

| 维度 | Base | Mantle |
|---|---|---|
| **TxManager** | `base_tx_manager::SimpleTxManager` | `op-service/txmgr.SimpleTxManager` |
| **Max Pending Transactions** | 1 | 1 |
| **Resubmission Timeout** | 48s | TxManager 内部 |
| **Num Confirmations** | 1 | TxManager 内部 |
| **Poll Interval** | **1s** | **6s** |
| **事件优先级模型** | `biased select!` (确定性) | Go `select` (随机) |
| **TxPool 状态机** | `txpool_blocked` 标志 | `Good → Blocked → CancelPending` |
| **Drain Timeout** | `resubmission_timeout × 2 = 96s` | 无显式 drain timeout |
| **冷启动恢复** | `RecentTxScanner` (depth 默认 0) | `CheckRecentTxsDepth` (默认 0) |
| **Max Check Depth** | 128 L1 blocks | 无上限 |
| **Scan 并发度** | 16 | N/A |

---

## 节流控制对比

| 维度 | Base | Mantle |
|---|---|---|
| **节流策略** | Off, Step, Linear | Step, Linear, Quadratic, PID |
| **默认策略** | Linear | **Quadratic** |
| **节流阈值** | 1,000,000 bytes (1 MB) | 3,200,000 bytes (3.2 MB, "4x 6-blob-tx channels") |
| **上限阈值** | 2 × threshold (2 MB) | 12,800,000 bytes (12.8 MB) |
| **Block Size 下限** | 2,000 | 2,000 |
| **Block Size 上限** | 130,000 | 130,000 |
| **Tx Size 下限** | 150 | 150 |
| **Tx Size 上限** | 20,000 | 20,000 |
| **Max Intensity** | 1.0 | 1.0 (OutputMax) |
| **推送方式** | `miner_setMaxDASize` RPC | `miner_setMaxDASize` RPC |
| **Dedup 优化** | `last_applied` 缓存 | 无 |
| **PID 参数** | 不支持 | Kp=0.33, Ki=0.01, Kd=0.05 (实验性) |
| **运行时切换** | Admin RPC 支持 | Admin RPC 支持 |

---

## 监控与运维对比

| 维度 | Base | Mantle |
|---|---|---|
| **Metrics 数量** | ~10+ 核心 | **~30+** |
| **压缩率直方图** | `channel_compression_ratio`（histogram） | `channel_compr_ratio`（14 桶） |
| **Blob 利用率** | `blob_used_bytes_total`（counter，每笔确认 tx 累加） | `blob_used_bytes`（histogram，14 桶，仅记录多 blob tx 的最后一个 blob） |
| **节流 Metrics** | 基础 | 丰富 (PID error/integral/derivative) |
| **Admin RPC 端点** | 8 个 | 3 个 (节流专用) |
| **状态查询** | `getBatcherStatus` (in_flight + da_backlog) | 通过 Metrics |
| **运行时日志级别** | `admin_setLogLevel` | 不支持 |
| **启停控制** | `startBatcher` / `stopBatcher` / `flushBatcher` | 通过 Admin API |
| **Metrics 端口默认** | 7300 | 由 op-service 决定 |

---

## 连接与容错对比

| 维度 | Base | Mantle |
|---|---|---|
| **L1 RPC 多端点** | `Vec<Url>` 启动时 failover | 单端点 |
| **L2 RPC 多端点** | `Vec<Url>` 启动时 failover | 单端点 |
| **WS 订阅** | 可选 (`--l2-ws-url`) | N/A (polling only) |
| **混合数据源** | `HybridBlockSource` (WS + HTTP) | 仅 HTTP polling |
| **Catchup 模式** | 显式 sequential catchup | 无显式 catchup |
| **Reorg 检测** | Block hash 比较 + L1 info deposit | Block hash 比较 |
| **Sliding Window** | 256 blocks dedup window | 无 |
| **等待节点同步** | `--wait-node-sync` (600s timeout) | `--wait-node-sync` |

---

## 语言与运行时对比

| 维度 | Base (Rust) | Mantle (Go) |
|---|---|---|
| **并发模型** | tokio async/await | goroutine + channel |
| **事件优先级** | `biased select!` 确定性 | `select` 随机 |
| **内存管理** | 无 GC, 确定性 | GC, 可能有暂停 |
| **并发控制** | `Semaphore` 精确 | Channel buffer |
| **类型安全** | 编译时所有权检查 | 运行时 |
| **二进制大小** | 单一静态链接 | 单一二进制 + runtime |
| **构建时间** | 较长 (Rust 编译) | 较快 (Go 编译) |
| **调试** | 编译时防数据竞争 | `go vet` + 运行时检测 |


---

# 数据压缩策略对比

## 1. 支持的压缩算法

### Base（`base/crates/batcher/comp/`）

**算法枚举**（`comp/src/types.rs` → `CompressionAlgo`）：
- `Zlib` — 使用 `miniz_oxide::deflate`，级别 `BEST_ZLIB_COMPRESSION = 9`
- `Brotli9` / `Brotli10` / `Brotli11` — 使用 `brotli::CompressorWriter`，仅设置 `quality` 参数（`BrotliEncoderParams { quality: level as i32, ..Default::default() }`）

**Channel 版本前缀**（`comp/src/traits.rs` → `ChannelCompressor::channel_version_byte()`）：
- Zlib → 无前缀（zlib 数据头自带格式标识，trait 默认返回 `None`）
- Brotli → `0x01`（仅写入第一个 frame，`channel_out.rs` 中 `frame_number == 0` 时写入）

**默认选择**：
- `BatchEncoder::open_new_channel`（`encoder/src/encoder.rs:331-337`）**硬编码** `CompressionAlgo::Brotli10` + `CompressorType::Shadow`
- 当前 daemon 路径不使用 `VariantCompressor::from_timestamp` 做 Fjord 时间戳判断
- 注：`comp/src/variant.rs` 中存在 `VariantCompressor::from_timestamp`（Fjord 后选 Brotli10，否则 Zlib），但未被 encoder 调用

### Mantle

#### op-batcher（Go，`mantle-v2/op-batcher/compressor/`）

**算法**（`compressor/config.go`，使用 `derive` 包常量）：
- `derive.Zlib` — 默认
- `derive.Brotli9` / `Brotli10` / `Brotli11` — Fjord 激活后可用

**限制**（`service.go:315-317`）：Fjord 激活前使用 Brotli 会被拒绝（`"cannot use brotli compression before Fjord"`）

**CLI 默认**（`flags/flags.go`）：
- `CompressionAlgoFlag.Value: derive.Zlib`

#### kona comp（Rust，`kona/crates/batcher/comp/`）

**算法枚举**（`src/types.rs` → `CompressionAlgo`）：
- `Zlib` — `miniz_oxide`，`BEST_ZLIB_COMPRESSION = 9`，支持 `no_std`
- `Brotli9` / `Brotli10` / `Brotli11` — 需要 `std` feature

**库 helper**（`src/variant.rs` → `VariantCompressor::from_timestamp`）：
- 该构造器会按 timestamp/Fjord 状态选择 Zlib 或 Brotli10
- 这只代表 Kona comp 库能力；当前未发现 Go op-batcher 或 Kona derivation runtime 调用它

---

## 2. 压缩策略

### 压缩策略类型

| 策略 | Base | Mantle (Go) | Mantle (Kona) | 描述 |
|---|---|---|---|---|
| **Shadow** | `comp/src/shadow.rs` | `compressor/shadow_compressor.go` | `comp/src/shadow.rs` | 双缓冲区技术，精确测量压缩大小 |
| **Ratio** | `comp/src/ratio.rs` | `compressor/ratio_compressor.go` | `comp/src/ratio.rs` | 基于估算比率的简单预测 |
| **None** | 不支持 | `compressor/non_compressor.go` | 不支持 | `zlib.NoCompression`，仅测试用 |

### Shadow Compressor 工作原理

Shadow compressor 是 Base 和 Mantle 都使用的核心压缩策略：

```
┌─────────────────────────────────────────┐
│           ShadowCompressor              │
│                                         │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │ Real Compressor │  │ Shadow Compressor │ │
│  │  (不 flush)    │  │  (每次写入 flush) │ │
│  │  → 最终输出    │  │  → 精确大小测量   │ │
│  └──────────────┘  └──────────────────┘ │
│                                         │
│  SAFE_COMPRESSION_OVERHEAD = 51 bytes   │
│  CLOSE_OVERHEAD_ZLIB = 9 bytes          │
└─────────────────────────────────────────┘
```

**核心常量**（Base 和 Mantle 一致）：
- `SAFE_COMPRESSION_OVERHEAD = 51` — zlib/deflate 最坏情况开销（2 byte header + 4 byte digest + 5 byte eof + 5×8 flate block headers）
- `CLOSE_OVERHEAD_ZLIB = 9` — 关闭时额外预留

**关键行为**：Shadow compressor 允许第一个 block 超出大小限制，确保单个大 block 也能被编码到 frame 中。

### Ratio Compressor 工作原理

```
输入阈值 = target_output_size / approx_compr_ratio
is_full() = 累计输入字节 >= 输入阈值
```

- 简单粗暴但快速
- 默认 `approx_compr_ratio = 0.6`（Base 和 Mantle 一致）
- 适用于 Span Batch 场景（最终大小在关闭前不可知）

### 默认策略选择

| 项目 | 默认压缩策略 | 默认压缩算法 |
|---|---|---|
| Base | Shadow（硬编码） | Brotli10（硬编码，见 `encoder.rs:334`） |
| Mantle (Go) | Shadow（CLI 默认） | Zlib（CLI 默认，Fjord 后可切 Brotli） |
| Mantle (Kona) | 调用方决定 | 调用方决定；`from_timestamp` helper 可按 Fjord 状态选 Zlib/Brotli10 |

---

## 3. 压缩率 vs 解压速度的 Tradeoff

### Brotli vs Zlib 对比

| 指标 | Zlib (level 9) | Brotli 10 | Brotli 11 |
|---|---|---|---|
| 压缩率 | 基准 | 比 Zlib 好 ~15-20% | 比 Zlib 好 ~20-25% |
| 压缩速度 | 快 | 慢 ~3-5x | 慢 ~10x+ |
| 解压速度 | 基准 | 略快 | 略快 |
| Fjord 前可用 | 是 | 否 | 否 |
| 适合场景 | 低延迟需求 | 平衡选择 | 最大压缩 |

### 对 Derivation 性能的影响

- **压缩率更高 = DA 成本更低**：Brotli10 能在相同 blob 空间内编码更多 L2 block 数据
- **解压速度影响 derivation 延迟**：但 Brotli 的解压速度实际略优于 Zlib（算法设计特点）
- **Fjord 硬分叉是关键节点**：Brotli 在 OP Stack 语义下依赖 Fjord；Base 当前 daemon 路径固定使用 Brotli10，Mantle Go 侧只有在配置 Brotli 且 Fjord 已激活时才会使用

---

## 4. Base 特有的压缩优化

### `BatchComposer`（`comp/src/composer.rs`）— 职责澄清

**注意**：`BatchComposer` **不是**压缩策略选择器。它是一个无状态工具，负责将 L2 `BaseBlock` 转换为 `SingleBatch`（等价于 Go 侧的 `BlockToSingularBatch`）。具体职责：
- 验证首笔交易为 deposit
- 从 deposit 的 calldata 解码 L1BlockInfoTx
- 过滤所有 deposit 交易
- EIP-2718 编码剩余用户交易
- 组装 `SingleBatch`

压缩算法选择实际在 `BatchEncoder::open_new_channel`（`encoder/src/encoder.rs:331-337`）中硬编码：

```rust
// 实际代码（非伪逻辑）
let compressor_config = Config {
    target_output_size: self.config.target_frame_size as u64,
    kind: CompressorType::Shadow,
    compression_algo: CompressionAlgo::Brotli10,  // 固定 Brotli10
    approx_compr_ratio: self.config.approx_compr_ratio,
};
let compressor = ShadowCompressor::from(compressor_config);
```

### Span Batch 与压缩策略的交互

- Base 在 Span Batch 模式下使用 `approx_compr_ratio` 做压缩后大小估算；实际 channel 压缩器仍由 `open_new_channel` 固定创建为 `ShadowCompressor + Brotli10`
- Span Batch 每 block 额外开销：`SPAN_BATCH_PER_BLOCK_OVERHEAD = 50` bytes

---

## 5. 配置对比

| 配置项 | Base 默认值 | Mantle (Go) 默认值 |
|---|---|---|
| 压缩策略 | Shadow | Shadow |
| 压缩算法 | Brotli10（硬编码） | Zlib |
| 近似压缩比 | 0.6 | 0.6 |
| 目标输出大小 | 由 `target_frame_size` 计算 | 由 `TargetFrameSize × TargetNumFrames` 计算 |

---

## 6. 关键发现

### Base 的优势

1. **Brotli10 硬编码默认**：在网络支持 Brotli/Fjord 语义的前提下，无需运维配置即可使用 Brotli10；Mantle Go 侧 CLI 默认仍为 Zlib 需手动切换
2. **`BatchComposer` 职责清晰**：专注 block→batch 转换，与压缩解耦
3. **编码器-压缩器解耦**：`comp` crate 作为独立模块可被测试和复用
4. **统一语言栈**：压缩库和 daemon 使用同一语言，消除跨语言序列化开销

### Mantle 可借鉴之处

1. **将 CLI 默认算法从 Zlib 升级为 Brotli10**（前提：Fjord 已在 Mantle 网络激活）
2. **参考 Base 硬编码 Brotli10 的方式**，减少运维配置负担（或在代码中引入类似 `VariantCompressor::from_timestamp` 的自动选择逻辑）
3. **如果未来接入 Kona comp**，需要先明确它与 Go op-batcher 的协议兼容边界，并用测试保证压缩输出和 frame 编码一致


---

# DA 策略差异与成本分析

## 1. DA 路径总览

### 从代码确认的 DA 能力

| DA 类型 | Base | Mantle (代码支持) | Mantle (CLI 默认) |
|---|---|---|---|
| **EIP-4844 Blob**（标准 OP 格式） | 默认 | 支持（Post-Arsia） | 非默认（需显式配置） |
| **Mantle 特化 Blob**（RLP 列表格式） | 不支持 | 支持（Pre-Arsia → MantleEverest） | 非默认 |
| **Calldata** | Fallback | 支持 | **CLI 默认值**（`CalldataType`） |
| **Auto**（Blob/Calldata 动态切换） | 不支持 | 支持 | 非默认 |
| **AltDA**（通用 Plasma 承诺） | 不支持 | 支持（`op-alt-da` 模块） | 未默认启用 |
| **EigenDA** | 不支持 | **仅有死代码引用** | 未使用 |

> **注意**：Mantle 的 CLI 默认 DA 类型为 `Calldata`（`flags/flags.go:131-138`）。实际生产环境可能通过配置使用 Blob，但从代码层面无法确认生产运行时配置。

---

## 2. Base 的 DA 策略

### 2.1 代码位置

- 编码器 DA 类型：`crates/batcher/encoder/src/submission.rs` → `DaType { Blob, Calldata }`
- Blob 编码：`crates/batcher/blobs/src/encoder.rs` → `BlobEncoder`
- 提交队列：`crates/batcher/core/src/submissions.rs` → blob 打包逻辑
- CLI 配置：`bin/batcher/src/cli.rs` → `--data-availability-type`

### 2.2 策略详情

**默认 DA**：`Blob`（EIP-4844）

**CLI 选项**：
```
--data-availability-type blobs    # 默认
--data-availability-type calldata # Fallback
# 注意：不支持 "auto" 模式（CLI 会拒绝）
```

**Blob 编码**（`blobs/src/encoder.rs`）：
- `BLOB_ENCODING_VERSION = 0`
- `BLOB_ENCODING_ROUNDS = 1024`
- 编码方式：每 32 字节 field element = 1 byte high bits + 31 payload bytes
- 每轮从 4 个高位字节中恢复 3 bytes，最大化 BLS12-381 field 下的载荷利用率

**Calldata 编码**（`encoder/src/submission.rs`）：
- 前置 `DERIVATION_VERSION_0` 版本字节
- 然后拼接所有 frame 数据

**节流时强制使用 Blob**：
- `force_blobs_when_throttling = true`（默认开启）
- 当 DA backlog 触发节流时，即使配置为 calldata，也切换到 blob 模式
- 原因：blob 在拥堵时 DA 成本效率更高
- 可通过 `--no-force-blobs-when-throttling` 关闭

### 2.3 Base 不支持 Auto 模式

Base 的 CLI 明确拒绝 `auto` 选项。设计哲学是：**运维人员预先选择 DA 类型，而不是运行时动态切换**。唯一的例外是节流时的强制 blob 模式。

---

## 3. Mantle 的 DA 策略

### 3.1 代码位置

- DA 类型定义：`op-batcher/flags/types.go` → `CalldataType / BlobsType / AutoType`
- 动态切换：`op-batcher/batcher/channel_config_provider.go` → `DynamicEthChannelConfig`
- Mantle Blob 编码：`op-batcher/batcher/tx_data.go` → `MantleBlobs()` / `Blobs()`
- AltDA 模块：`op-alt-da/` → `daclient.go`, `damgr.go`
- Kona Mantle Blob 解码：`kona/crates/protocol/derive/src/sources/mantle_blob.rs`
- Derivation 路由：`op-node/rollup/derive/data_source.go`

### 3.2 Blob 策略——双格式演化

Mantle 的 blob 策略经历了格式演化：

```
时间线:
  Pre-MantleEverest  →  MantleEverest → Arsia  →  Post-Arsia
  ├─ Calldata only    ├─ MantleBlobs()          ├─ Blobs()（标准 OP）
                      │  (RLP 列表编码)          │
                      │  frame 数组打包到多 blob  │  一 blob 一 frame
```

**MantleBlobs() 编码**（`tx_data.go`，Pre-Arsia）：
```go
// RLP 编码 frame 数组，然后打包到多个 blob
frames := [frame_with_version_0, frame_with_version_1, ...]
rlpBytes := rlp.Encode(frames)
blobs := packIntoBlobs(rlpBytes)
```

**标准 Blobs() 编码**（Post-Arsia）：
```go
// 每个 blob 包含一个 frame（与上游 OP Stack 一致）
for _, frame := range frames {
    blob := encodeToBlobData(frame)
    blobs = append(blobs, blob)
}
```

**分叉检测**（`driver.go`）：
```go
if l.RollupConfig.IsMantleArsia(l.prevCurrentL1.Time) {
    // 使用标准 OP 格式
} else {
    // 使用 Mantle 特化 RLP 格式
}
```

### 3.3 Derivation 端的双格式解码

Mantle 的 derivation pipeline 需要处理两种 blob 格式（`data_source.go:73-97`）：

```
OpenData(ref, batcherAddr):
  if ecotoneTime reached AND blobSourceChanged:
    → 标准 OP BlobDataSource
  else if mantleEverestTime reached:
    → MantleBlobDataSource（先尝试 Mantle 格式，失败后切标准格式）
  else:
    → CalldataSource
  
  if altDAEnabled:
    → wrap with AltDADataSource
```

**Sticky Fallback 机制**（`mantle_blob.rs` / `mantle_blob_source.go`）：
- `MantleBlobSource` 首先尝试 Mantle RLP 列表格式解码
- 如果 RLP 解码失败 → 设置 `mantle_format_failed` / `blobSourceChanged` 标志
- 该标志**持久化**（跨 `clear()` 调用），仅在完整 `reset()`（L1 reorg）时重置
- 一旦标志被设置，后续所有 block 永久使用标准 OP blob 格式

```
Mantle Blob 解码流程:
  Read blobs
    → EIP-4844 标准解码每个 blob
    → 拼接所有 blob 载荷
    → 尝试 RLP VecOfBytes 解码
       成功 → 返回 Mantle 格式 frames
       失败 → 设置 sticky fallback → 使用标准 OP 格式
```

### 3.4 Auto 模式（动态 DA 切换）

**实现**（`channel_config_provider.go` → `DynamicEthChannelConfig`）：
- 每 10 秒计算 blob vs calldata 的单字节成本
- 基于 Pectra EIP-7623 参数：`totalCostFloorPerToken = 10`，`standardTokenCost = 4`
- `blobCostPerByte > calldataCostPerByte` → 切换为 calldata
- 反之 → 切换为 blob
- 当节流激活时，优先选择 blob

**Calldata Fallback 配置**（`service.go:337-345`）：
```
MaxFrameSize = 120_000
TargetNumFrames = 1
UseBlobs = false
```

### 3.5 AltDA 支持

**模块位置**：`mantle-v2/op-alt-da/`

**工作流程**：
```
Batcher → publishToAltDAAndL1:
  1. l.AltDA.SetInput(ctx, frame)
     → HTTP POST 到 DAServerURL
     → 接收 CommitmentData
  2. 将 commitment (不是 frame) 作为 L1 calldata 提交
```

**承诺类型**（`op-alt-da/commitment.go`）：
- `Keccak256CommitmentType = 0` — batcher 预计算，读取时验证
- `GenericCommitmentType = 1` — 服务器计算，不透明字节串

**限制**：
- `UseAltDA && UseBlobs` → 报错（`"cannot use data availability type blobs or auto with Alt-DA"`）
- `MaxConcurrentDARequests = 1`（默认）
- `MaxInputSize = 130672`

**重要说明**：AltDA 是上游 OP Stack 的通用 Plasma 框架，Mantle **未对其进行定制化**。

### 3.6 EigenDA 状态确认

**结论：Mantle 代码中不存在 EigenDA 集成**

证据：
- `op-node/rollup/types.go:192-196` 中有 `MantleDaSwitch` 和 `DataLayrServiceManagerAddr` 字段，但这些是**死代码**——仅被反序列化，从未被运行时路径读取
- 整个 op-batcher 和 op-alt-da 中唯一的 "eigenDA" 引用是 `damock.go` 中的测试注释：`"to mimic a DA service with slow responses (eg. eigenDA with 10 min batching interval)"`
- 无 EigenDA 客户端实现、无 DA 桥接合约交互、无 disperser RPC 调用
- 如需接入 EigenDA，只能通过通用 AltDA HTTP 接口（op-alt-da）间接连接

---

## 4. DA 成本分析

### 基于确认路径的成本对比

| 成本维度 | Base（Blob） | Mantle（Blob） | Mantle（Calldata） |
|---|---|---|---|
| L1 存储 | blob 空间（临时） | blob 空间（临时） | calldata（永久） |
| 单位成本 | ~1-5 gwei/byte（blob gas） | ~1-5 gwei/byte（blob gas） | ~16 gas/byte × gas price |
| 有效载荷/blob | ~126 KB（标准编码） | ~126 KB（标准编码） | N/A |
| 额外开销 | KZG 承诺 + 验证 | KZG 承诺 + 验证 | 无 |
| 成本波动 | 独立 blob gas 市场 | 独立 blob gas 市场 | 跟随 L1 gas 价格 |

### DA 类型选择对运营成本的影响

- **Blob 模式**：在 L1 blob gas 价格低时通常显著低于 calldata；具体倍数取决于 blob gas 和 L1 gas 的实时价格，不能仅由本仓库代码确认
- **Base 的 `force_blobs_when_throttling`**：在 DA backlog 高峰时强制使用 blob，利用 blob 的容量优势降低单位成本
- **Mantle 的 Auto 模式**：动态切换在 blob gas 飙升时可以切回 calldata 避免高成本，但失去了 blob 的容量优势

---

## 5. DA 可用性保障对比

| 维度 | Base | Mantle |
|---|---|---|
| 默认/配置路径 | Blob（EIP-4844） | Calldata（CLI 默认；Blob 需显式配置；生产配置未在本仓库确认） |
| Fallback | Calldata（需重启切换） | Auto 动态切换 / Calldata |
| DA 故障处理 | 重试 + requeue | Channel invalidation + DA 类型切换 |
| 格式复杂度 | 单一标准 OP 格式 | 双格式（Mantle RLP + 标准 OP）+ sticky fallback |
| 外部 DA | 不支持 | AltDA 框架可选 |

---

## 6. 关键发现

### Base 的设计亮点

1. **极简 DA 策略**：Blob 为默认，Calldata 为备选，无 Auto / AltDA 复杂性——降低运维风险和 derivation 实现复杂度
2. **`force_blobs_when_throttling` 创新**：在 DA 拥堵时利用 blob 的批量效率自动优化成本
3. **单一 blob 格式**：使用标准 OP blob 编码，derivation 端无需处理格式切换
4. **Blob 打包解耦**：frame→blob 打包在提交队列层完成，encoder 保持 DA-agnostic

### Mantle 的复杂性代价

1. **双格式 blob 编码**：`MantleBlobs()` + `Blobs()` 增加了 batcher 和 derivation 的代码路径
2. **Sticky fallback 状态机**：`mantle_format_failed` 标志在 pipeline 中引入额外状态，增加调试难度
3. **AltDA 模块未定制**：保留了上游框架但未实际使用 EigenDA
4. **EigenDA 死代码**：`MantleDaSwitch` 等字段残留增加误导风险

### Mantle 可借鉴之处

1. **清理双格式 blob 编码**：Arsia 后全面使用标准 OP 格式，移除 `MantleBlobs()` 代码路径
2. **保留并测试 Auto 模式下的节流 blob 偏好**：Mantle 已在 `DynamicEthChannelConfig` 中实现 throttling 时返回 blob config，建议补覆盖用例和运行指标，避免后续改动破坏该行为
3. **清理 EigenDA 死代码**：移除 `MantleDaSwitch` 和 `DataLayrServiceManagerAddr` 等不再使用的字段
4. **评估 Auto 模式的实际收益**：动态切换虽灵活，但增加了状态管理复杂性，且 blob gas 市场通常显著便宜


---

# Base Batcher 设计亮点和 Mantle 可借鉴之处

## Base Batcher 核心设计亮点

### 1. 模块化 Crate 架构

Base 将 batcher 分解为 8 个独立 crate（comp, encoder, core, service, source, blobs, admin, binary），每个 crate 有清晰的职责边界和独立的测试。这种架构带来三个关键优势：

- **可测试性**：每个 crate 可独立单元测试，`comp` 和 `blobs` 甚至支持 `no_std` 环境测试
- **可复用性**：`comp` 压缩库作为独立 crate 具备被 derivation 端复用的潜力
- **可替换性**：DA 策略、数据源、节流控制器均通过 trait 抽象，替换实现不影响其他模块

对比之下，Mantle 的 Go op-batcher 虽有包分离，但模块间耦合更紧（如 channel 层直接处理 blob 编码），且 Kona comp 库与 op-batcher 之间无运行时集成。

### 2. 编码器-DA 解耦设计

Base 的一个关键架构决策是将 **frame 产出** 和 **blob 打包** 放在不同层：

```
encoder (comp crate)  →  产出 frames (DA-agnostic)
                              ↓
submission queue (core)  →  打包 frames 到 blob / calldata
```

这意味着 encoder 完全不需要了解最终 DA 类型，所有 frame 格式统一。对比 Mantle 的实现：channel 层直接控制 frame 提取数量并决定 `MantleBlobs()` vs `Blobs()` 编码格式，导致 channel 逻辑与 DA 策略紧耦合。

### 3. 激进的低延迟提交策略

Base 的 `max_channel_duration = 2`（~24s）明显短于 Mantle 默认的 `MaxChannelDuration = 0`（无固定时间限制）。配合 `poll_interval = 1s` 和 WS 订阅优先的数据源设计，Base batcher 整体偏向最小化 L2→L1 提交延迟。

代价是压缩效率可能降低（channel 可能未满就被强制关闭），代码配置体现出用更多提交频率换取低延迟的取向。

> **注意**：Base batcher 代码中不包含 Flashblocks 相关逻辑。`sub_safety_margin = 0` 是 channel 超时计算中的 L1 block 缓冲量，与 Flashblocks 预确认机制无关。

### 4. `biased select!` 事件优先级模型

Base 使用 Rust tokio 的 `biased select!` 宏实现确定性的事件优先级：

```
Shutdown > Admin > L1 Head > Safe Head > Receipts > Block Ingestion
```

这带来三个行为特征：
- Shutdown/reorg 分支排在数据输入前，控制面事件更不容易被待处理 block 抢占
- Admin 命令（启停、flush）排在 L1/L2 数据事件前
- 交易收据确认优先于新 block 编码（避免 in-flight 积压）

Go 的 `select` 不支持原生优先级；Mantle 若要获得同等确定性的控制面优先级，需要在事件循环中显式分层处理。

### 5. `HybridBlockSource` 混合数据源

Base 的 `HybridBlockSource` 设计解决了 op-batcher 的一个已知问题：WS 订阅和 HTTP 轮询并存时的 block 乱序。

关键机制：
- **Catchup 模式**：启动时或 reorg 后，仅使用 HTTP 顺序拉取，WS 订阅被抑制
- **Dedup 滑动窗口**：256 blocks 的 `(number, hash)` 缓存去重
- **Reorg 检测**：相同 number 不同 hash → 触发 reorg 事件

Mantle 的 op-batcher 仅使用 HTTP polling（6s 间隔），无 WS 订阅支持。

### 6. `force_blobs_when_throttling` 成本优化

当 DA backlog 触发节流时，Base 强制使用 blob 而非 calldata，利用 blob 的批量效率降低单位 DA 成本。这是一个反直觉但有效的优化：拥堵时更应该用容量更大、单位成本更低的 DA 方式。

### 7. Shadow Compressor + 硬编码 Brotli10

Base 在 `BatchEncoder::open_new_channel`（`encoder/src/encoder.rs:331-337`）中硬编码 `CompressionAlgo::Brotli10` + `CompressorType::Shadow`，无需运维人员手动配置。这个结论成立的前提是网络已经支持 Brotli/Fjord 语义；在此前提下，它降低了运行时配置错误的空间。

> **注意**：`BatchComposer`（`comp/src/composer.rs`）是 block→SingleBatch 的转换器（等价于 Go 侧 `BlockToSingularBatch`），**不涉及压缩算法选择**。`comp/src/variant.rs` 中存在 `VariantCompressor::from_timestamp`（Fjord 后选 Brotli10），但未被 encoder 调用。

---

## Mantle 的现有优势

### 1. 更丰富的 Prometheus Metrics

Mantle 的 op-batcher 暴露 30+ Prometheus metrics，包括：
- `channel_compr_ratio` 压缩率直方图（14 桶）
- `blob_used_bytes` blob 利用率直方图（14 桶，但仅记录多 blob tx 的最后一个 blob）
- PID 节流器的 error/integral/derivative 指标
- `throttle_intensity_history` summary (p50/p90/p99)

Base 也有压缩率和 blob 利用率指标（`channel_compression_ratio` histogram、`blob_used_bytes_total` counter），但总体 metrics 数量较少（~10+），Mantle 在可观测性维度上更丰富。

### 2. 多种节流策略（含 PID 实验性）

Mantle 提供 4 种节流策略：Step, Linear, Quadratic, PID（实验性），且支持运行时通过 Admin RPC 切换。PID 控制器虽标记为实验性，但为自适应节流提供了探索方向。Base 仅支持 Off, Step, Linear。

### 3. Auto DA 模式

Mantle 的动态 DA 切换每 10 秒评估 blob vs calldata 成本，在 blob gas 飙升时自动切换到 calldata。虽然增加了复杂性，但提供了成本优化的灵活性。

### 4. AltDA 框架

Mantle 保留了上游 OP Stack 的 AltDA（Plasma）框架，支持通用 HTTP DA 服务器接入。虽然当前未使用 EigenDA，但框架本身为未来接入外部 DA 提供商提供了扩展性。

---

## Mantle 可借鉴的具体改进

### 高优先级

| # | 改进项 | 预期收益 | 复杂度 |
|---|---|---|---|
| 1 | **评估将 CLI 默认 DA 从 Calldata 切换为 Blob** | 在 blob gas 低于 calldata 时降低 DA 成本；需要先确认生产链 fork、beacon 配置和回滚策略 | 低 |
| 2 | **缩短 `PollInterval` 从 6s 到 1-2s** | 降低 L2→L1 提交延迟 | 低 |
| 3 | **将默认压缩算法升级为 Brotli10**（前提：Fjord 已激活） | 提升压缩率 15-20% | 低 |
| 4 | **启用 `CheckRecentTxsDepth`**（如设为 32） | 减少冷启动后的重复提交 | 低 |

### 中优先级

| # | 改进项 | 预期收益 | 复杂度 |
|---|---|---|---|
| 5 | **评估缩短 `MaxChannelDuration`**（如设为 5-10 L1 blocks） | 降低提交延迟 | 低 |
| 6 | **清理 Pre-Arsia `MantleBlobs()` 代码路径** | 减少维护负担和 derivation 复杂性 | 中 |
| 7 | **清理 EigenDA 死代码**（`MantleDaSwitch` 等） | 减少误导和配置混乱 | 低 |
| 8 | **为 Auto throttling 偏向 blob 增加测试和告警** | Mantle 已实现该行为，重点是防回退和可观测 | 中 |

### 长期方向

| # | 改进项 | 预期收益 | 复杂度 |
|---|---|---|---|
| 9 | **明确 Kona comp 是否会进入运行时路径** | 若未来接入，需要协议兼容测试；当前未发现它被 Go op-batcher 或 derivation runtime 直接使用 | 高 |
| 10 | **将 frame→blob 打包从 channel 层分离** | 提高架构灵活性，简化 DA 策略切换 | 高 |
| 11 | **考虑 Rust batcher 重写**（参考 Base 架构） | 类型安全、性能可预测、与 Kona 统一 | 很高 |
| 12 | **引入 WS 订阅 + 混合数据源** | 减少 polling 延迟 | 中 |

---

## 架构层面的核心差异总结

```
Base 设计哲学:
  "低延迟 > 压缩效率 > 灵活性"
  → 激进超时 (2 L1 blocks)
  → 简单 DA (Blob 为主，无 Auto)
  → 确定性事件处理 (biased select!)
  → 单一语言栈 (全 Rust)

Mantle 设计哲学:
  "灵活性 > 压缩效率 > 低延迟"
  → 宽松超时 (无限制)
  → 多 DA 选项 (Calldata/Blob/Auto/AltDA)
  → 丰富配置 (4 种节流策略，运行时切换)
  → 双语言栈 (Go daemon + Rust 库)
```

两种设计哲学各有优劣，但 Base 的方法在以下场景下更优：
1. **对用户体验敏感的应用场景**（如 DeFi 交易确认）
2. **运维简单性优先**（更少的配置旋钮 = 更少的配置错误）
3. **代码可维护性**（单一语言、模块化 crate、编译时安全）

Mantle 的方法在以下场景下更优：
1. **成本优化敏感**（Auto 模式可动态选择最便宜的 DA）
2. **需要外部 DA 扩展**（AltDA 框架现成可用）
3. **运维可观测性**（更丰富的 metrics）


---

# L1 提交优化对比

## 1. Gas 管理

### Base

**实现位置**：`crates/batcher/service/src/service.rs` → `SimpleTxManager`

- 使用 `base_tx_manager` 库的 `SimpleTxManager`
- **`TxManagerConfig`**：
  - `resubmission_timeout = 48s` — 超时后重新提交（fee bump）
  - `num_confirmations = 1` — 等待 1 个 L1 确认
- Gas 估算由底层 tx manager 自动处理（EIP-1559 base fee + priority fee）
- `drain_timeout = resubmission_timeout × 2 = 96s` — shutdown 时等待所有 in-flight tx 的最大时间

**Fee Bumping 策略**：
- 当交易在 `resubmission_timeout`（48s）内未被确认，自动重新提交并提高 gas 价格
- 底层使用 RBF（Replace-By-Fee）机制

### Mantle

**实现位置**：`mantle-v2/op-batcher/batcher/service.go` → `op-service/txmgr.NewSimpleTxManager`

- 使用 OP Stack 的 `op-service/txmgr` 库
- 与 Base 类似的 `SimpleTxManager` 接口
- Gas 管理委托给共享的 tx manager 层

**TxManager 状态机**（`driver.go`）：
```
TxpoolGood → TxpoolBlocked → TxpoolCancelPending → TxpoolGood
```

- `TxpoolGood`：正常提交
- `TxpoolBlocked`：txpool 拒绝（`ErrAlreadyReserved`），触发 `cancelBlockingTx`
- `TxpoolCancelPending`：等待取消交易确认

---

## 2. Nonce 管理

### Base

**并发控制**（`core/src/submissions.rs`）：
- 使用 `Arc<Semaphore>` 限制并发提交数
- `max_pending_transactions = 1`（默认）
- 提交队列使用 `FuturesUnordered` 管理 in-flight 交易

**Nonce 逻辑**：
- 单并发（默认 1）意味着严格顺序 nonce
- Semaphore 机制支持增大 `max_pending_transactions` 实现多交易并发
- `txpool_blocked` 标志：当 mempool 拒绝时暂停新提交，直到 `cancel_tx` 恢复

### Mantle

**并发控制**（`flags/flags.go`）：
- `MaxPendingTransactions = 1`（默认）
- `MaxConcurrentDARequests = 1`（AltDA 模式，默认）

**Receipt 处理**（`driver.go` → `receiptsLoop`）：
- 异步跟踪交易确认
- 成功：`channelManager.TxConfirmed`
- 失败：`channelManager.TxFailed` → 触发 requeue

---

## 3. 重试与容错

### Base

**重试机制**：

```
提交失败
  → SubmissionQueue::handle_outcome
    → TxOutcome::Failed → requeue frames
    → TxOutcome::TxpoolBlocked → 设置 txpool_blocked 标志
       → 后续提交被暂停
       → 调用 cancel_tx 解除阻塞
    → TxOutcome::Confirmed → 确认成功，释放资源
```

**Reorg 处理**：
- 检测到 reorg 时，**所有 in-flight + queued frames 被丢弃**
- Pipeline 完全重置
- 从 `safe_head + 1` 重新开始编码

**Shutdown 优雅退出**：
- 强制关闭当前 channel → 生成剩余 frames
- 等待所有 in-flight 提交确认或失败（最长 `drain_timeout = 96s`）
- 使用 `biased select!` 确保 shutdown 信号优先级最高

**冷启动恢复**（`service/src/recent_txs.rs`）：
- `RecentTxScanner`：扫描最近 N 个 L1 block（`MAX_CHECK_RECENT_TXS_DEPTH = 128`）
- 并发扫描：`SCAN_FETCH_CONCURRENCY = 16`
- 仅解析 calldata 格式的 Frame（blob tx 跳过——数据在 KZG sidecar 中）
- 识别已提交的最高 L2 block number → 跳过已提交数据

### Mantle

**重试机制**：

```
提交失败
  → channelManager.TxFailed → requeue frames
  → ErrAlreadyReserved → cancelBlockingTx
  → Channel invalidation → 丢弃 channel，rewind blocks
     → 可选：通过 ChannelConfigProvider 切换 DA 类型
```

**Reorg 处理**：
- `channel_manager.go` → `handleChannelInvalidated`
- 清除 `currentChannel`，回退 blocks
- 可通过 `ChannelConfigProvider` 动态切换 DA 类型

**冷启动恢复**：
- `CheckRecentTxsDepth = 0`（默认禁用）
- 可选功能，与 Base 类似但默认关闭

---

## 4. 批量大小优化

### Base

**提交间隔计算**：
- `poll_interval = 1s` — 每秒轮询新 L2 block
- `max_channel_duration = 2` L1 blocks — 每 ~24s 至少提交一次
- `target_num_frames = 1` — 默认每次提交 1 个 blob

**最优提交策略**：
- Base 不追求 channel 填满后再提交，而是**优先保证低延迟**
- `STEP_BUDGET = 128`：每次主循环迭代最多处理 128 步，然后 yield
- channel 未满时仍然在 2 个 L1 block 内强制关闭提交

**Blob 利用率优化**：
- `submit_pending` 将连续 frame 打包到单个 blob 中直到 `BLOB_MAX_DATA_SIZE`
- 但由于 `max_channel_duration = 2` 和 `target_num_frames = 1`，实际上通常是单 frame 单 blob

### Mantle

**提交间隔计算**：
- `PollInterval = 6s` — 每 6 秒轮询
- `MaxChannelDuration = 0`（无限制）— 仅在 channel 满时提交
- `TargetNumFrames = 1`

**最优提交策略**：
- Mantle 等待 channel 满后再提交 → **优先保证压缩效率和 blob 利用率**
- `MaxL1TxSize = 120000`（calldata 模式的安全上限）

**动态批量调整**（Auto 模式）：
- `DynamicEthChannelConfig` 每 10 秒评估 blob vs calldata 成本
- 可在运行时切换 DA 类型，间接调整批量大小

---

## 5. Base 低延迟提交设计

### 提交节奏与配置特征

Base batcher 整体设计偏向低延迟提交：

1. **更频繁的轮询**：`poll_interval = 1s`（Mantle 为 6s），能更及时捕获新产出的 L2 block
2. **激进的 channel 超时**：`max_channel_duration = 2` L1 blocks（~24s），即使 channel 未满也强制提交
3. **`force_blobs_when_throttling = true`**：高负载时强制使用 blob，利用 blob 的批量效率降低单位成本
4. **WS 订阅优先**：`HybridBlockSource` 在 WS 可用时优先使用订阅模式，减少 polling 延迟

> **注意**：`sub_safety_margin` 是 channel 超时计算中的 L1 block 缓冲量（Base 设为 0，Mantle 设为 10），与 Flashblocks 预确认机制无关。Base batcher 代码中不包含 Flashblocks 相关逻辑。

### 低延迟提交链路

```
L2 block 产出
  → WS 订阅实时接收 / poll_interval 1s 兜底
  → BatchEncoder 持续编码
  → max_channel_duration 2 L1 blocks
  → 每 ~24s 提交到 L1
```

---

## 6. 语言差异对并发提交的影响

### Rust async（Base）

**并发模型**：
- tokio 异步运行时
- `biased select!` 实现事件优先级（control plane > data plane）
- `FuturesUnordered` + `Arc<Semaphore>` 管理 in-flight 提交
- 零成本抽象：无 GC 暂停，可预测的内存使用

**优势**：
- `biased select!` 把 shutdown/reorg 分支放在最高优先级，控制面响应更可预测
- Semaphore 精确控制并发度
- 类型系统保证 channel 所有权安全（编译时防止 data race）
- `watch::Sender::send_if_modified` 避免 spurious wake-up

**代码示例**（`core/src/driver.rs`）：
```rust
// biased select! — 优先级从上到下
select! { biased;
    _ = shutdown => { /* 最高优先级 */ }
    cmd = admin_rx.recv() => { /* Admin 命令 */ }
    l1_head = l1_head_rx.changed() => { /* L1 头更新 */ }
    safe_head = safe_head_rx.changed() => { /* Safe head */ }
    receipt = submissions.next() => { /* 交易收据 */ }
    block = source.next() => { /* L2 block 输入 */ }
}
```

### Go goroutine（Mantle）

**并发模型**：
- goroutine + channel 通信
- `errgroup` 管理并发 DA 请求
- GC 管理内存

**优势**：
- goroutine 轻量，创建开销低
- channel 语义直观
- `errgroup` 简化错误传播

**代码示例**（`driver.go`）：
```go
for {
    select {
    case <-l.shutdownCtx.Done():
        // shutdown
    case <-ticker.C:
        l.loadBlocksIntoState(l.shutdownCtx)
        l.publishStateToL1(...)
    }
}
```

### 对并发提交的实际影响

| 维度 | Base (Rust) | Mantle (Go) |
|---|---|---|
| 事件优先级 | `biased select!` 固定分支轮询顺序 | Go `select` 无原生优先级 |
| 内存可预测性 | 无 GC，确定性内存 | GC 可能引入延迟 |
| 并发控制精度 | `Semaphore` 精确 | Channel 缓冲区大小 |
| Shutdown 响应 | 最高优先级分支先被轮询 | 需要代码显式分层才能模拟优先级 |
| 调试难度 | 编译时类型安全 | 运行时 goroutine 泄漏风险 |

实际影响有限，因为两者都默认 `MaxPendingTransactions = 1`（单并发）。在增大并发度时，Rust 的 `Semaphore` + `biased select!` 提供更可预测的行为。

---

## 7. 监控与运维

### Base

**Metrics**（端口 7300，`encoder/src/metrics.rs`）：

| Metric | 标签/类型 | 说明 |
|---|---|---|
| channel close reason | `REASON_SIZE_FULL / TIMEOUT / FORCE / DISCARD` | Channel 关闭原因分布 |
| submission outcome | `SUBMITTED / CONFIRMED / FAILED / REQUEUED` | 提交结果 |
| DA type | `DA_TYPE_BLOB / DA_TYPE_CALLDATA` | DA 类型统计 |
| `channel_compression_ratio` | histogram | 压缩率分布 |
| `blob_used_bytes_total` | counter | 每笔确认 tx 累加的 blob 字节数 |

**Admin RPC**（`admin/src/api.rs`）：
- `admin_startBatcher` / `admin_stopBatcher` — 启停
- `admin_flushBatcher` — 强制 flush
- `admin_getBatcherStatus` → `{ stopped, in_flight, da_backlog_bytes }`
- `admin_getThrottleController` / `setThrottleController` / `resetThrottleController`
- `admin_setLogLevel` — 运行时日志级别

### Mantle

**Metrics**（`metrics/metrics.go`，namespace `op_batcher`）：

Channel/Block 流：
- `pending_blocks_count{stage}`, `pending_blocks_bytes_total`, `pending_blocks_bytes_current`
- `pending_da_bytes`, `unsafe_da_bytes`
- `input_bytes{stage}`, `ready_bytes`, `output_bytes`
- `channel_compr_ratio`（14 线性桶，0.3 起步，0.05 步长）
- `channel_num_frames`, `channel_closed_reason`, `channel_queue_length`
- `blob_used_bytes`（14 桶，每桶 `MaxBlobDataSize/13`）
- Channel 事件：opened, closed, fully_submitted, timed_out
- Batcher tx 事件：submitted, success, failed

节流：
- `throttle_intensity{type}`, `throttle_max_tx_size`, `throttle_max_block_size`
- `throttle_controller_type{type}`, `unsafe_bytes_ratio{type}`
- `throttle_intensity_history`（summary p50/p90/p99）
- PID 专用：`pid_controller_error`, `pid_controller_integral`, `pid_controller_derivative`

**Admin RPC**（`rpc/api.go`）：
- `SetThrottleController` / `GetThrottleController` / `ResetThrottleController`
- PID 参数校验：`Kp/Ki/Kd >= 0`, `IntegralMax > 0`, `OutputMax ∈ (0,1]`

### 对比

| 维度 | Base | Mantle |
|---|---|---|
| Metrics 数量 | ~10+ 核心指标 | **~30+ 指标**（更丰富） |
| 压缩率 | `channel_compression_ratio`（histogram） | `channel_compr_ratio`（histogram，14 桶） |
| Blob 利用率 | `blob_used_bytes_total`（counter，每笔确认 tx 累加） | `blob_used_bytes`（histogram，14 桶，仅记录多 blob tx 的最后一个 blob） |
| 节流 PID 指标 | 无（仅 Linear） | error/integral/derivative |
| Admin API | 8 个端点 | 3 个端点（节流专用） |
| 状态查询 | `getBatcherStatus` 含 in_flight + da_backlog | 通过 metrics 间接获取 |
| Log Level 控制 | `setLogLevel` | 无此功能 |

---

## 8. 关键发现

### Base 的设计亮点

1. **`biased select!` 事件优先级**：把 shutdown/reorg 放在数据面之前处理，控制面响应更可预测
2. **冷启动恢复默认启用路径**：`RecentTxScanner` 虽默认 depth=0，但提供了完整的扫描框架
3. **`force_blobs_when_throttling`**：创新的成本优化——拥堵时利用 blob 批量效率
4. **Drain 超时设计**：`drain_timeout = resubmission_timeout × 2` 确保 shutdown 时有充足时间清理
5. **低延迟提交设计**：1s polling + 激进 channel 超时（2 L1 blocks）+ WS 订阅优先 = 端到端快速提交

### Mantle 的优势

1. **更丰富的 Prometheus Metrics**：30+ 指标包括压缩率直方图和 blob 利用率，运维可观测性更强
2. **多种节流策略**：Linear / Quadratic / Step / PID（实验性），运行时可切换
3. **Auto DA 模式**：动态成本优化，在 blob gas 飙升时自动切换
4. **TxPool 状态机**：显式处理 blocked/cancel 状态，避免 nonce 卡死

### Mantle 可借鉴之处

1. **参考 `biased select!` 模式**：在 Go 中实现类似的事件优先级（虽然 Go select 不支持原生 bias，但可通过多层 select 模拟）
2. **考虑启用 `CheckRecentTxsDepth`**：默认禁用增加了冷启动时重复提交的风险
3. **评估缩短 `PollInterval`**：从 6s 缩短到 1-2s 以减少提交延迟
4. **增加 Admin 状态查询端点**：参考 Base 的 `getBatcherStatus` 提供 in-flight 和 da_backlog 快照
