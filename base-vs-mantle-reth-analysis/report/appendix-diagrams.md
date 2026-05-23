# 附录 B: Mermaid 图汇编

> 本附录汇总 final-report.md 及 M0-M3 分析输出中的所有 Mermaid 图。

---

## B.1 架构总览图

### B.1.1 Base vs Mantle 架构差异总览

```mermaid
graph TB
    subgraph "Base: Rust 单体仓库全栈"
        direction TB
        B_BIN["Binary Layer<br/>18 主入口 + 10 脚本"]
        B_CORE["Core Crates Layer<br/>consensus(13) + execution(20) + batcher(7)<br/>+ builder(3) + proof(32) + common(15)<br/>+ infra(6) + utilities(10)"]
        B_UP["Upstream<br/>reth v2.2.0 直用 · alloy 2.0.4<br/>revm 38.0.0 · SP1 v6.2.1<br/>全部标准版，零 fork"]
        B_BIN --> B_CORE --> B_UP
    end

    subgraph "Mantle: 多仓库多语言 Fork 组合"
        direction TB
        M_GO["Go 层<br/>mantle-v2: op-node + op-batcher<br/>+ op-proposer + op-challenger<br/>+ op-conductor + cannon + contracts<br/>mantle/op-geth: EL + preconf + keeper"]
        M_RUST["Rust 层<br/>mantle/reth: EL fork + flashblocks<br/>mantle/kona: derivation + FPP<br/>mantle/op-succinct: ZK proof"]
        M_FORK["Fork 依赖<br/>mantle-xyz/revm · mantle-xyz/op-alloy<br/>mantle-xyz/evm · mantle-xyz/kona"]
        M_GO --> M_FORK
        M_RUST --> M_FORK
    end
```

### B.1.2 Base Monorepo 分层架构

```mermaid
graph TB
    subgraph "Binary Layer (bin/)"
        B1["base-node"]
        B2["base-batcher"]
        B3["base-proposer"]
        B4["basectl"]
        B5["ingress-rpc"]
        B6["websocket-proxy"]
        B7["load-tester"]
        B8["zk-client"]
    end

    subgraph "Core Crates (crates/)"
        subgraph "consensus/ (13)"
            C1["derive (no_std)"]
            C2["engine"]
            C3["service"]
            C4["sources"]
            C5["gossip"]
            C6["safedb"]
        end
        subgraph "execution/ (20)"
            E1["evm"]
            E2["txpool"]
            E3["flashblocks"]
            E4["metering"]
            E5["trie"]
            E6["rpc"]
        end
        subgraph "batcher/ (7)"
            BA1["comp"]
            BA2["encoder"]
            BA3["core"]
            BA4["service"]
            BA5["source"]
            BA6["admin"]
        end
        subgraph "proof/ (32)"
            P1["client (no_std)"]
            P2["driver"]
            P3["executor"]
            P4["host"]
            P5["zk-client"]
            P6["nitro-enclave"]
        end
        subgraph "builder/ (3)"
            BU1["core"]
            BU2["flashblocks-service"]
        end
    end

    subgraph "Upstream Dependencies"
        U1["reth v2.2.0 (git tag)"]
        U2["alloy 2.0.4"]
        U3["revm 38.0.0"]
        U4["SP1 v6.2.1"]
    end

    B1 --> C3 & E1
    B2 --> BA4
    B8 --> P5
    C1 --> U1
    E1 --> U1 & U3
    P1 --> U1
```

### B.1.3 Mantle 五仓库架构

```mermaid
graph TB
    subgraph "mantle-v2 (Go Monorepo)"
        G1["op-node<br/>derivation + consensus"]
        G2["op-batcher<br/>批次提交"]
        G3["op-proposer<br/>状态提议"]
        G4["op-challenger<br/>争议处理"]
        G5["op-conductor<br/>排序器协调 + WS Relay"]
        G6["cannon<br/>MIPS64 VM"]
        G7["contracts-bedrock<br/>L1 合约"]
    end

    subgraph "mantle/op-geth (Go EL)"
        GE1["core/state_transition.go<br/>BVM_ETH + tokenRatio"]
        GE2["core/types/rollup_cost.go<br/>三层费用"]
        GE3["preconf/<br/>预确认"]
        GE4["cmd/keeper/<br/>Ziren zkVM"]
    end

    subgraph "mantle/reth (Rust EL)"
        R1["crates/optimism/<br/>Mantle 定制"]
        R2["flashblocks/<br/>Consumer"]
    end

    subgraph "mantle/kona (Rust Derivation)"
        K1["derive/<br/>MantleBlobSource"]
        K2["node/<br/>kona-node"]
        K3["fpp/<br/>Fault Proof Program"]
    end

    subgraph "mantle/op-succinct (Rust ZK)"
        S1["validity/<br/>Proposer"]
        S2["contracts/<br/>DisputeGame"]
    end

    subgraph "Fork Dependencies"
        F1["mantle-xyz/revm"]
        F2["mantle-xyz/op-alloy"]
        F3["mantle-xyz/evm"]
        F4["mantle-xyz/kona"]
    end

    R1 --> F1 & F2 & F3
    K1 --> F4
    G1 -.->|Engine API| R1 & GE1
```

---

## B.2 上游依赖模型对比图

### B.2.1 Base: Pin & Extend 模型

```mermaid
graph LR
    BASE["Base Application<br/>130 crates"] -->|git tag v2.2.0| RETH["paradigmxyz/reth<br/>60+ crates"]
    BASE -->|crates.io 2.0.4| ALLOY["alloy"]
    BASE -->|crates.io 38.0.0| REVM["revm"]
    BASE -->|crates.io v6.2.1| SP1["SP1"]

    style BASE fill:#4CAF50,color:white
    style RETH fill:#2196F3,color:white
```

### B.2.2 Mantle: Fork & Modify 模型

```mermaid
graph LR
    MR["mantle/reth"] -->|fork| OPR["op-reth"] -->|fork| RETH["paradigmxyz/reth"]
    MK["mantle/kona"] -->|fork| KONA["ethereum-optimism/kona"]
    MOS["mantle/op-succinct"] -->|fork| OS["succinctlabs/op-succinct"]
    MV["mantle-v2"] -->|fork| OPT["ethereum-optimism/optimism"]
    MOG["mantle/op-geth"] -->|fork| OPG["op-geth"] -->|fork| GETH["go-ethereum"]

    FREVM["mantle-xyz/revm"] -->|fork| REVM2["bluealloy/revm"]
    FOPA["mantle-xyz/op-alloy"] -->|fork| OPA["op-alloy"]
    FEVM["mantle-xyz/evm"] -->|fork| EVM2["alloy-evm"]

    MR -.-> FREVM & FOPA & FEVM

    style MR fill:#FF9800,color:white
    style MK fill:#FF9800,color:white
    style MOS fill:#FF9800,color:white
    style MV fill:#FF9800,color:white
    style MOG fill:#FF9800,color:white
```

---

## B.3 场景流程图

### B.3.1 Batcher 提交流程对比

```mermaid
graph TD
    subgraph "Base Batcher (Rust)"
        B_SRC["HybridBlockSource<br/>WS + HTTP, 1s poll"]
        B_ENC["BatchEncoder<br/>Shadow + Brotli10 硬编码"]
        B_FRM["Frame 产出<br/>(DA-agnostic)"]
        B_PKG["提交队列<br/>Frame → Blob 打包"]
        B_TX["SimpleTxManager<br/>L1 提交"]
        B_DUP["256-block 去重"]
        B_SEL["biased select!<br/>Shutdown > Admin > L1 > Receipts > Blocks"]

        B_SRC --> B_ENC --> B_FRM --> B_PKG --> B_TX --> B_DUP
        B_SEL -.->|控制| B_SRC
    end

    subgraph "Mantle Batcher (Go)"
        M_SRC["HTTP Polling<br/>6s interval"]
        M_CH["Channel 层<br/>Zlib 默认"]
        M_BLOB["Blob 编码<br/>MantleBlobs/Blobs 耦合"]
        M_TX["SimpleTxManager<br/>L1 提交"]
        M_SEL["Go select<br/>随机优先级"]

        M_SRC --> M_CH --> M_BLOB --> M_TX
        M_SEL -.->|控制| M_SRC
    end
```

### B.3.2 Derivation Pipeline 路径对比

```mermaid
graph LR
    subgraph "Base: 单一 Rust 路径"
        B_L1["L1 数据源"]
        B_DER["base-consensus-derive<br/>(no_std 核心)"]
        B_ENG["base-consensus-engine<br/>(Task Queue)"]
        B_SVC["base-consensus-service"]

        B_L1 --> B_DER --> B_ENG --> B_SVC

        B_DER -->|同一代码| B_ZK["ZK 证明 Guest"]
        B_DER -->|同一代码| B_TEE["TEE 证明"]
    end

    subgraph "Mantle: Go + Rust 双路径"
        M_L1["L1 数据源"]
        M_GO["Go op-node<br/>derive/ (生产)"]
        M_RS["Rust kona<br/>derive/ (FPP)"]
        M_EC["Engine Controller"]

        M_L1 --> M_GO --> M_EC
        M_L1 --> M_RS -->|独立实现| M_FPP["Fault Proof"]
    end
```

### B.3.3 证明系统路径对比

```mermaid
graph TB
    subgraph "Base: 三合一架构"
        B_CORE["base-proof-client<br/>(no_std 共享核心)"]
        B_DRV["base-proof-driver"]
        B_EXE["base-proof-executor"]

        B_CORE --> B_DRV --> B_EXE

        B_EXE --> B_TEE["TEE 路径<br/>nitro-enclave<br/>12s 轮询, 512 block"]
        B_EXE --> B_ZK2["ZK 路径<br/>SP1 v6.2.1<br/>Range + Aggregation"]
        B_EXE --> B_FP["FP 路径<br/>Native 执行<br/>Groth16 争议"]

        B_TEE --> B_AGG["AggregateVerifier<br/>(L1 合约)"]
        B_ZK2 --> B_AGG
        B_FP --> B_AGG
    end

    subgraph "Mantle: 分散架构"
        M_VP["Validity Proof<br/>op-succinct SP1 v6.1.0<br/>game type 6"]
        M_CAN["Cannon FP<br/>MIPS64 VM + op-challenger<br/>(继承自上游)"]
        M_ZKFP["ZK Fault Proof<br/>game type 42<br/>(仅合约)"]
        M_KEP["Keeper<br/>Ziren zkVM<br/>(实验性)"]

        M_VP --> M_DG["DisputeGameFactory"]
        M_CAN --> M_DG
        M_ZKFP --> M_DG
    end
```

---

## B.4 Flashblocks 机制图

### B.4.1 Base Flashblocks 全栈

```mermaid
graph TD
    subgraph "Base Flashblocks Producer"
        BP1["FlashblocksServiceBuilder"]
        BP2["250ms 可配置间隔"]
        BP3["Per-flashblock metering<br/>执行时间/状态根 gas/DA 字节"]
    end

    subgraph "Base Flashblocks Consumer"
        BC1["CachedExecutor<br/>parent_hash + tx position"]
        BC2["ReceiptRootTaskHandle<br/>后台流式计算"]
        BC3["spawn_deferred_trie_task<br/>后台 trie 计算"]
    end

    subgraph "Base Flashblocks RPC"
        BR1["eth_sendRawTransactionSync"]
        BR2["eth_subscribe('newFlashblocks')"]
        BR3["websocket-proxy<br/>brotli + 速率限制 + API-key"]
    end

    BP1 --> BC1
    BC1 --> BC2 --> BC3
    BC1 --> BR1 & BR2 & BR3
```

### B.4.2 Mantle Flashblocks 架构

```mermaid
graph TD
    subgraph "External"
        MP1["rollup-boost<br/>(不在分析仓库)"]
    end

    subgraph "Mantle Relay"
        MR1["op-conductor ws/<br/>WebSocket 中继"]
    end

    subgraph "Mantle Consumer"
        MC1["FlashBlockBuilder<br/>重新执行所有交易"]
        MC2["pending block/receipt/tx<br/>(基础)"]
    end

    MP1 -->|flashblock| MR1 -->|relay| MC1
    MC1 --> MC2
```

---

## B.5 实施路线图

### B.5.1 优化实施依赖关系图

```mermaid
graph TD
    S1["S-1~S-4<br/>配置优化<br/>0-2 月"] --> M4b["M-4b HybridBlockSource"]
    S2["S-2 Brotli10"] --> M6["M-6 压缩配置确认"]

    M1["M-1 Go/Rust 一致性测试<br/>3-6 月"] --> L7["L-7 kona-node 评估<br/>6-12 月"]
    M2["M-2 CachedExecutor"] --> L2["L-2 Flashblocks Producer<br/>12-36 月"]
    M3["M-3 Rust Monorepo"] --> M5["M-5 消除 fork 链评估"]
    M5 --> L1["L-1 去 fork 化<br/>6-12 月"]
    M4c["M-4c 负载测试"] --> L5["L-4 Go→Rust 迁移<br/>12-36 月"]

    L31["L-3.1 VP 部署确认<br/>6 月"] --> L32["L-3.2 ZK FP 服务"]
    L31 --> L33["L-3.3 中间输出根"]
    L32 --> L34["L-5 TEE 异构证明<br/>12-36 月"]
    L34 --> L35["L-6 多证明聚合"]

    L7 --> L5
```

### B.5.2 分阶段时间线

```
月份  0───1───2───3───4───5───6───9───12───18───24───36
      ┌─────────┐
 P0   │ S-1~S-4 │  配置优化
      │ 0-2 月  │
      └─────────┘
            ┌───────────────────────────────┐
 P1         │ M-1~M-6                       │  架构微调
            │ 3-6 月                        │
            └───────────────────────────────┘
                              ┌──────────────────────────────┐
 P2                           │ L-3, L-7, L-9                │  能力扩展
                              │ 6-12 月                      │
                              └──────────────────────────────┘
                                          ┌─────────────────────────────┐
 P3                                       │ L-1, L-2, L-4, L-5, L-6    │  战略演进
                                          │ 12-36 月                   │
                                          └─────────────────────────────┘
```

---

## B.6 特性对比热力图

### B.6.1 功能覆盖对比

```mermaid
graph LR
    subgraph "功能覆盖"
        direction TB
        F1["Flashblocks Producer"]
        F2["Flashblocks Consumer"]
        F3["CachedExecutor"]
        F4["多维 Metering"]
        F5["多证明协调"]
        F6["TEE 证明"]
        F7["ZK 证明"]
        F8["Fault Proof"]
        F9["Validity Proof"]
        F10["Auto DA"]
        F11["AltDA 框架"]
        F12["PID 节流"]
        F13["ingress-rpc"]
        F14["动态预编译"]
        F15["Bundle 竞价"]
    end

    subgraph "Base"
        B1["✅"] --- F1
        B2["✅"] --- F2
        B3["✅"] --- F3
        B4["✅"] --- F4
        B5["✅"] --- F5
        B6["✅"] --- F6
        B7["✅"] --- F7
        B8["✅"] --- F8
        B9["❌"] --- F9
        B10["❌"] --- F10
        B11["❌"] --- F11
        B12["❌"] --- F12
        B13["✅"] --- F13
        B14["✅(未激活)"] --- F14
        B15["✅"] --- F15
    end

    subgraph "Mantle"
        M1["❌(外部)"] --- F1
        M2["✅(基础)"] --- F2
        M3["❌"] --- F3
        M4["❌"] --- F4
        M5["❌"] --- F5
        M6["❌"] --- F6
        M7["✅"] --- F7
        M8["✅(继承)"] --- F8
        M9["✅"] --- F9
        M10["✅"] --- F10
        M11["✅"] --- F11
        M12["✅"] --- F12
        M13["❌"] --- F13
        M14["❌"] --- F14
        M15["❌"] --- F15
    end
```

---

## B.7 升级路径对比图

### B.7.1 Base 升级流程

```mermaid
graph LR
    A["修改 Cargo.toml<br/>bump reth tag"] --> B["cargo build<br/>编译检查"]
    B --> C["修复 trait 变化<br/>(如有)"]
    C --> D["运行测试"]
    D --> E["1 PR 合并"]

    style A fill:#4CAF50,color:white
    style E fill:#4CAF50,color:white
```

### B.7.2 Mantle 升级流程

```mermaid
graph TD
    A1["rebase mantle-xyz/revm"] --> A2["rebase mantle-xyz/op-alloy"]
    A2 --> A3["rebase mantle-xyz/evm"]
    A3 --> B1["rebase mantle/reth"]
    A3 --> B2["rebase mantle/kona"]
    B1 & B2 --> C1["更新 mantle/op-succinct"]
    C1 --> D1["升级 mantle-v2"]
    C1 --> D2["升级 mantle/op-geth"]
    D1 & D2 --> E1["跨仓库集成测试"]
    E1 --> F1["多个 PR 合并"]

    style A1 fill:#FF9800,color:white
    style F1 fill:#FF9800,color:white
```

---

*本附录中的所有 Mermaid 图均基于本地代码分析，反映分析时点的代码结构。*
