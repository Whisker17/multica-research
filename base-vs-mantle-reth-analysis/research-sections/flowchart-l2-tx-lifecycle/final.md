# Base L2 交易生命周期

## 结论

Base 的路径是单仓 Rust 链路：`bin/ingress-rpc` 是 binary 入口，核心 `IngressService` 在 `crates/infra/ingress-rpc/src/service.rs`，交易进入扩展 txpool 后转发给 builder。builder 生成 Flashblocks sub-block，`crates/builder/publish` 负责 WebSocket 广播，`crates/execution/flashblocks-node` 订阅并交给 `crates/execution/flashblocks` 管理 pending state 和 RPC 可见性。L1 batcher 提交数据后，op 派生路径把区块从 unsafe 推进到 safe；proof 目录下的 challenge、succinct、TEE、proposer、zk service 和 contracts 组成最终确认相关路径。

## Mermaid 流程图

```mermaid
flowchart TD
    user[用户 / 钱包 / 搜索器] --> ingress["bin/ingress-rpc<br/>Rust binary<br/>JSON-RPC / bundle / tips 入口"]
    ingress --> ingressSvc["crates/infra/ingress-rpc<br/>IngressService<br/>mempool / simulation / raw_tx_forward / BuilderConnector"]
    ingressSvc --> txpool["crates/execution/txpool<br/>Rust<br/>基于上游 reth txpool 的验证与排序"]
    txpool --> consumer["txpool consumer<br/>pool.best_transactions()"]
    consumer --> forwarder["txpool forwarder<br/>base_insertValidatedTransaction"]
    forwarder --> builderRpc["builder RPC<br/>BuilderApiImpl::insert_validated_transaction"]
    builderRpc --> builderPool["builder 本地 txpool<br/>BasePooledTransaction"]
    ingressSvc --> metering["MeterBundleResponse<br/>builder metering provider<br/>等待 / 跳过 / 执行限流"]

    builderPool --> fbJob["crates/builder/core/flashblocks<br/>Rust<br/>new_payload_job / build_payload"]
    metering --> fbExec
    fbJob --> fbExec["BasePayloadBuilder::build_next_flashblock<br/>execute_best_transactions"]
    fbExec --> evm["crates/common/evm + crates/execution<br/>Rust / revm<br/>evm.transact + commit state"]
    evm --> fbPublish["crates/builder/publish<br/>WebSocketPublisher<br/>广播 FlashblocksPayloadV1"]
    fbPublish --> fbNode["crates/execution/flashblocks-node<br/>Rust<br/>subscriber / state processor"]
    fbNode --> fbState["crates/execution/flashblocks<br/>Rust<br/>pending state / receipts / calls"]
    fbState --> rpcPending["RPC pending 可见性<br/>pending block / pending receipt / eth_sendRawTransactionSync / newFlashblocks"]

    fbExec --> finalPayload["finalize_payload / build_block<br/>state root / receipts root / BaseBuiltPayload"]
    finalPayload --> unsafe["Unsafe L2 head<br/>sequencer 本地 canonical head"]
    unsafe --> batcher["bin/batcher + crates/batcher<br/>Rust<br/>编码 L2 blocks 为 calldata/blob batch"]
    batcher --> l1["L1 batch inbox<br/>数据可用性提交"]
    l1 --> derive["crates/consensus/derive<br/>Rust no_std<br/>从 L1 派生 L2 block attributes"]
    derive --> safe["Safe L2 head<br/>L1 数据可派生后提升"]
    safe --> proofCore["crates/proof/proof + driver/executor<br/>Rust<br/>proof core / preimage / MPT"]
    proofCore --> proofChallenge["crates/proof/challenge<br/>Fault proof challenge<br/>scanner / submitter / driver"]
    proofCore --> proofSuccinct["crates/proof/succinct<br/>ZK SP1 validity<br/>range / aggregation programs"]
    proofCore --> proofTee["crates/proof/tee<br/>AWS Nitro Enclave<br/>host / enclave / attestation / registrar"]
    proofCore --> proofProposer["crates/proof/proposer + zk/service + contracts<br/>proof proposer / gRPC prover / verifier bindings"]
    proofChallenge --> finalized["Finalized L2 head<br/>证明或最终性条件满足后确认"]
    proofSuccinct --> finalized
    proofTee --> finalized
    proofProposer --> finalized

    classDef rust fill:#e8f4ff,stroke:#2b6cb0,color:#0f172a;
    classDef state fill:#f5f5f5,stroke:#525252,color:#111827;
    classDef l1 fill:#fff7ed,stroke:#c2410c,color:#111827;
    class ingress,ingressSvc,txpool,consumer,forwarder,builderRpc,builderPool,metering,fbJob,fbExec,evm,fbPublish,fbNode,fbState,rpcPending,batcher,derive,proofCore,proofChallenge,proofSuccinct,proofTee,proofProposer rust;
    class unsafe,safe,finalized state;
    class l1 l1;
```

## 调用链 / 组件路径

| 阶段 | 调用链 | 证据路径 |
|---|---|---|
| 用户提交 | `bin/ingress-rpc` 初始化 `IngressService::new`；`IngressService` 处理 mempool / simulation / raw_tx_forward / builder connector | `references/codebase/base/bin/ingress-rpc/src/main.rs`；`references/codebase/base/crates/infra/ingress-rpc/src/service.rs`；`references/codebase/base/crates/infra/ingress-rpc/README.md` |
| txpool 验证与转发 | `pool.best_transactions()` -> `Forwarder` -> `base_insertValidatedTransaction` -> `BuilderApiImpl::insert_validated_transaction` -> `pool.add_external_transaction` | `references/codebase/base/crates/execution/txpool/src/consumer/task.rs`；`references/codebase/base/crates/execution/txpool/src/forwarder/task.rs`；`references/codebase/base/crates/execution/txpool/src/builder/rpc.rs` |
| metering | `ingress-rpc` 广播 `MeterBundleResponse` -> `BuilderConnector` 转发给 builder；builder `metering_provider` 在 Flashblocks 执行时读取 metering 数据并处理 pending/limit | `references/codebase/base/crates/infra/ingress-rpc/src/service.rs`；`references/codebase/base/bin/ingress-rpc/src/main.rs`；`references/codebase/base/crates/builder/core/src/metering.rs`；`references/codebase/base/crates/builder/core/src/flashblocks/context.rs` |
| builder / Flashblocks producer | `BlockPayloadJobGenerator::new_payload_job` -> `BasePayloadBuilder::build_payload` -> `build_next_flashblock` -> `FlashblocksPayloadV1` | `references/codebase/base/crates/builder/core/src/flashblocks/generator.rs`；`references/codebase/base/crates/builder/core/src/flashblocks/payload.rs` |
| Flashblocks publisher | `FlashblocksServiceBuilder` 创建 `WebSocketPublisher`；`WebSocketPublisher::publish` 序列化并广播 payload | `references/codebase/base/crates/builder/core/src/flashblocks/service.rs`；`references/codebase/base/crates/builder/publish/src/publisher.rs`；`references/codebase/base/crates/builder/publish/README.md` |
| EVM 执行 | `execute_sequencer_transactions` / `execute_best_transactions` -> `evm.transact(...)` -> `evm.db_mut().commit(state)` | `references/codebase/base/crates/builder/core/src/flashblocks/context.rs`；`references/codebase/base/crates/common/evm/src/executor/block_executor.rs` |
| Flashblocks subscriber / pending state | builder 发布 `FlashblocksPayloadV1` -> node subscriber -> state processor -> pending blocks / receipts / calls / subscriptions | `references/codebase/base/crates/execution/flashblocks-node/src/extension.rs`；`references/codebase/base/crates/execution/flashblocks/src/state.rs`；`references/codebase/base/crates/execution/flashblocks/README.md` |
| Unsafe -> Safe | `crates/batcher` 提交 batch 到 L1；`crates/consensus/derive` 从 L1 数据派生 L2 状态 | `outputs/WHI-444_component-mapping-and-architecture-diff/component-mapping-table.md` |
| Safe -> Finalized | `crates/proof/challenge` 处理 fault proof challenge；`crates/proof/succinct` 处理 SP1 range / aggregation；`crates/proof/tee` 处理 Nitro Enclave；`crates/proof/proposer`、`crates/proof/zk`、`crates/proof/contracts` 提供 proposer、prover service 和合约绑定 | `references/codebase/base/crates/proof/challenge/src/scanner.rs`；`references/codebase/base/crates/proof/challenge/src/submitter.rs`；`references/codebase/base/crates/proof/challenge/src/driver.rs`；`references/codebase/base/crates/proof/succinct/programs/`；`references/codebase/base/crates/proof/tee/`；`references/codebase/base/crates/proof/proposer/`；`references/codebase/base/crates/proof/zk/service/`；`references/codebase/base/crates/proof/contracts/src/aggregate_verifier.rs`；`references/codebase/base/crates/proof/contracts/src/tee_prover_registry.rs` |

## 待确认点

- Base 生产合约源码不在本仓库内，本图只引用仓库内 Rust 合约绑定和证明组件。
- Safe -> Finalized 的实际生产策略可能按 Fault Proof、ZK、TEE 路线配置不同；本地代码能确认多套路径存在，但不能仅凭代码确认当前主网启用组合。


---

# L2 交易生命周期关键差异

## 差异摘要

| 维度 | Base | Mantle | 影响 |
|---|---|---|---|
| 交易入口 | 独立 `ingress-rpc`，统一接收交易、bundle、tips，并连接 builder；`IngressService` 在 `crates/infra/ingress-rpc` | 直连 execution RPC；reth 可转发到 sequencer；op-geth 另有 `eth_sendRawTransactionWithPreconf` | Base 入口更集中；Mantle 入口随执行客户端和 preconf 路径分散 |
| 语言栈 | Rust 单仓 | Go + Rust 多仓 | Base 调用链更短；Mantle 需要跨 repo、跨语言确认行为一致性 |
| txpool / builder 关系 | `txpool consumer/forwarder` 直接把已验证交易送到 builder RPC | `op-node` 通过 engine API 驱动 execution engine 构块，交易池在 reth/op-geth 侧；op-geth preconf 交易在 txpool 中被单独追踪并优先 seal | Base 的 builder 是一等组件；Mantle 更接近 OP Stack 标准 sequencer 架构，但 op-geth 增加了 Mantle 自有 preconf 扩展 |
| Flashblocks | builder 生成 sub-block delta，`crates/builder/publish` 广播，execution 节点订阅并写入 pending state/RPC | reth consumer 与 op-conductor relay 在仓库内；producer 看起来来自外部 rollup-boost | Base 可从本地代码闭环验证 producer -> consumer -> RPC；Mantle 的 Flashblocks 完整生产链路需部署配置和外部服务确认 |
| 预确认机制 | Flashblocks 通过 sub-block 增量和 pending RPC 提供更快可见性 | op-geth preconf 通过 `preconfChecker.Preconf(tx)` 在 miner env 中预执行交易，返回 receipt/status；必要时 `RevertTx` 回滚，`PausePreconf` / `UnpausePreconf` 和 seal 协调 | Mantle 有自己的 preconf 路径，但不是 Base Flashblocks 的同构实现 |
| 执行引擎 | 基于上游 reth + revm 的 Rust execution | mantle/reth(Rust/revm) 与 mantle/op-geth(Go/go-ethereum EVM) 并行 | Mantle 需要维护双 execution client 行为一致 |
| Unsafe -> Safe | Rust batcher + Rust derivation | Go op-batcher + Go op-node derivation，另有 Mantle blob RLP 格式 | Mantle 的 DA/derivation 路径有 Mantle 专用 blob 兼容逻辑 |
| Safe -> Finalized | `challenge`、`succinct`、`tee`、`proposer`、`zk`、`contracts` 等 proof 子目录覆盖 Fault Proof、ZK SP1、TEE 和 proposer/verifier 绑定 | op-succinct validity proof + fault-proof contracts + Go OP Stack challenger/Cannon 路径 | Base 证明系统集中在一个仓库下但子系统较多；Mantle 证明路径分散在多个仓库 |

## Mermaid 对比图

```mermaid
flowchart LR
    subgraph Base["Base: Rust 单仓闭环"]
        b1["ingress-rpc<br/>crates/infra/ingress-rpc"]
        b2["execution txpool"]
        b3["builder + Flashblocks producer"]
        b4["crates/builder/publish<br/>WebSocketPublisher"]
        b5["flashblocks-node + flashblocks pending RPC"]
        b6["Rust batcher + derivation"]
        b7["challenge / ZK / TEE proof"]
        b1 --> b2 --> b3 --> b4 --> b5
        b3 --> b6 --> b7
    end

    subgraph Mantle["Mantle: Go + Rust 多仓组合"]
        m1["reth RPC / txpool"]
        m2["op-geth RPC / txpool"]
        m3["op-geth preconf checker"]
        m4["op-node sequencer"]
        m5["op-conductor HA"]
        m6["reth or op-geth execution"]
        m7["Flashblocks relay + consumer<br/>producer 待确认"]
        m8["Go op-batcher + op-node derivation"]
        m9["op-succinct validity proof"]
        m1 --> m6
        m2 --> m6
        m3 --> m2
        m5 --> m4
        m4 --> m6 --> m8 --> m9
        m7 -. pending state .-> m1
    end

    b3 -.->|Flashblocks producer/builder 一体化| m7
    b5 -.->|pending RPC vs miner 预执行 receipt| m3
    b7 -.->|证明系统集中 vs 分散| m9
```

## 关键判断

- Base 的最大差异是把交易入口、builder、Flashblocks、execution pending state 和证明系统都放在 Rust 单仓内，代码链路可以本地闭环追踪。
- Mantle 的最大差异是多执行客户端和多仓组合：Go `op-node/op-batcher/op-conductor` 负责生产链路，Rust `reth/op-succinct` 负责 execution 替代实现和 ZK validity proof，op-geth 还增加了 Mantle 自有 preconf 路径。
- Flashblocks 对比需要分开看：Base 有 producer 到 RPC 可见性的完整路径；Mantle 本地代码确认 relay/consumer，但 producer 和生产启用状态仍需外部配置验证。
- 预确认不能简单写成 Base 有、Mantle 无：Mantle op-geth 的 preconf 是完整代码路径，但它通过 miner 预执行和 receipt/status 返回实现，不是 Flashblocks 的 sub-block 广播模型。
- 最终确认路径不能只按“有代码”判断：Base 的多证明路线和 Mantle 的 op-succinct validity 路线都需要结合实际部署配置确认主网使用状态。

## 证据索引

| 主题 | Base 路径 | Mantle 路径 |
|---|---|---|
| 入口 | `references/codebase/base/bin/ingress-rpc/`；`references/codebase/base/crates/infra/ingress-rpc/src/service.rs` | `references/codebase/mantle/reth/crates/optimism/rpc/src/eth/transaction.rs`；`references/codebase/mantle/op-geth/internal/ethapi/api.go` |
| txpool / builder | `references/codebase/base/crates/execution/txpool/`；`references/codebase/base/crates/builder/core/src/flashblocks/` | `references/codebase/mantle/mantle-v2/op-node/rollup/sequencing/sequencer.go`；`references/codebase/mantle/mantle-v2/op-node/rollup/engine/`；`references/codebase/mantle/op-geth/core/txpool/` |
| Flashblocks | `references/codebase/base/crates/builder/core/src/flashblocks/`；`references/codebase/base/crates/builder/publish/`；`references/codebase/base/crates/execution/flashblocks-node/`；`references/codebase/base/crates/execution/flashblocks/` | `references/codebase/mantle/reth/crates/optimism/flashblocks/`；`references/codebase/mantle/mantle-v2/op-conductor/rpc/ws/flashblocks_handler.go` |
| Preconf | Base Flashblocks 是主要预确认/快速可见路径 | `references/codebase/mantle/op-geth/internal/ethapi/api.go`；`references/codebase/mantle/op-geth/eth/api_backend.go`；`references/codebase/mantle/op-geth/core/txpool/legacypool/legacypool_preconf.go`；`references/codebase/mantle/op-geth/miner/preconf_checker.go`；`references/codebase/mantle/op-geth/tests/preconf/` |
| Batcher / derivation | `references/codebase/base/crates/batcher/`；`references/codebase/base/crates/consensus/derive/` | `references/codebase/mantle/mantle-v2/op-batcher/batcher/`；`references/codebase/mantle/mantle-v2/op-node/rollup/derive/` |
| Proof | `references/codebase/base/crates/proof/challenge/`；`references/codebase/base/crates/proof/succinct/`；`references/codebase/base/crates/proof/tee/`；`references/codebase/base/crates/proof/proposer/`；`references/codebase/base/crates/proof/zk/`；`references/codebase/base/crates/proof/contracts/` | `references/codebase/mantle/op-succinct/validity/`；`references/codebase/mantle/op-succinct/contracts/src/` |

## 待确认清单

- Mantle Flashblocks producer 是否为外部 rollup-boost，以及生产是否启用。
- Mantle op-geth preconf 是否在生产打开 `--miner.enablepreconfchecker`，以及 preconf tx 的 from/to/all 过滤规则。
- Mantle reth 与 op-geth 当前生产分工：哪一个服务公开 RPC，哪一个承担 sequencer execution。
- Base 当前主网最终确认采用 Fault Proof、ZK、TEE 中的哪一种或哪几种组合。
- Mantle op-succinct validity proof 是否已作为主网 finalized/proven output 的实际路径。


---

# Mantle L2 交易生命周期

## 结论

Mantle 的路径是 Go + Rust 混合链路：交易可进入 mantle/reth 或 mantle/op-geth 的 RPC/txpool，生产排序主体在 `mantle-v2/op-node`，execution engine 可由 reth 或 op-geth 执行。Flashblocks 在本地代码中主要表现为 reth consumer 和 op-conductor relay；另外，op-geth 有独立 preconf 预确认系统，`eth_sendRawTransactionWithPreconf` 会把交易送入 txpool preconf 路径，由 miner 内的 `preconfChecker` 预执行并返回 receipt/status。这个 preconf 机制和 Base Flashblocks 都服务于更快确认，但实现方式不同；本地代码能确认完整执行路径，生产是否开启仍需部署参数确认。

## Mermaid 流程图

```mermaid
flowchart TD
    user[用户 / 钱包 / 搜索器] --> rethRpc["mantle/reth RPC<br/>Rust<br/>send_raw_transaction / send_raw_transaction_sync"]
    user --> gethRpc["mantle/op-geth RPC<br/>Go<br/>eth_sendRawTransaction"]
    user --> preconfRpc["mantle/op-geth preconf RPC<br/>Go<br/>eth_sendRawTransactionWithPreconf"]

    rethRpc --> rethTx["mantle/reth txpool<br/>Rust<br/>raw_tx_forwarder + local pool"]
    gethRpc --> gethPool["op-geth txpool<br/>Go<br/>plain/blob/local tx"]
    preconfRpc --> preconfApi["EthAPIBackend.SendTxWithPreconf<br/>Go<br/>本地 preconf 或转发 sequencer"]
    preconfApi --> preconfPool["legacypool preconf<br/>Go<br/>FifoTxSet / NewPreconfTxRequest"]
    preconfPool --> preconfChecker["miner preconfChecker<br/>Go<br/>Preconf(tx) 预执行 -> receipt + returnData"]
    preconfChecker --> preconfResult["NewPreconfTxEvent<br/>Go<br/>predicted L2 block / status / receipt"]
    preconfChecker -. timeout / seal 协调 .-> preconfCoord["RevertTx / PausePreconf / UnpausePreconf<br/>fillTransactions 协调"]
    preconfPool --> gethPool

    opnode["mantle-v2/op-node<br/>Go<br/>Sequencer"] --> attrs["Sequencer.startBuildingBlock<br/>PreparePayloadAttributes"]
    leader["op-conductor<br/>Go<br/>Raft leader / sequencer start-stop 控制"] --> opnode
    attrs --> buildStart["EngineController.BuildStartEvent<br/>ForkchoiceUpdate + PayloadAttributes"]
    rethTx --> execution["Execution engine<br/>Rust reth(revm) 或 Go op-geth(EVM)<br/>GetPayload / NewPayload / ForkchoiceUpdate"]
    gethPool --> execution
    buildStart --> execution
    execution --> sealed["BuildSealedEvent<br/>payload sealed"]
    sealed --> conductorCommit["conductor.CommitUnsafePayload<br/>leader 提交 unsafe payload"]
    conductorCommit --> unsafe["Unsafe L2 head<br/>PayloadProcessEvent / InsertUnsafePayload"]

    rollupBoost["外部 rollup-boost<br/>producer 待确认，不在分析仓库"] -.-> conductorWs["op-conductor/rpc/ws<br/>Go<br/>Flashblocks relay"]
    conductorWs -.->|leader only broadcast| rethFb["mantle/reth flashblocks<br/>Rust<br/>WsFlashBlockStream / FlashBlockService"]
    rethFb -.-> pending["pending_flashblock<br/>Rust<br/>pending block / pending receipt / send_raw_transaction_sync"]
    pending -.-> rethRpc

    unsafe --> batcher["mantle-v2/op-batcher<br/>Go<br/>load unsafe blocks / channelManager / txData"]
    batcher --> l1["L1 batch inbox / blob / calldata<br/>Mantle blob RLP 格式或标准 blob"]
    l1 --> derive["mantle-v2/op-node/rollup/derive<br/>Go<br/>MantleBlobDataSource / derivation pipeline"]
    derive --> pendingSafe["pending safe / local safe"]
    pendingSafe --> safe["PromoteSafe<br/>safe L2 head"]
    safe --> finalizedByNode["PromoteFinalized<br/>finalized L2 head in op-node"]
    safe --> succinct["mantle/op-succinct validity<br/>Rust / SP1<br/>range proof -> aggregation proof"]
    succinct --> l1Proof["L1 OPSuccinctL2OutputOracle 或 DisputeGameFactory"]
    l1Proof --> finalized["Finalized / proven output<br/>实际部署状态待确认"]

    classDef rust fill:#e8f4ff,stroke:#2b6cb0,color:#0f172a;
    classDef go fill:#eefdf4,stroke:#15803d,color:#0f172a;
    classDef mixed fill:#f5f3ff,stroke:#7c3aed,color:#0f172a;
    classDef state fill:#f5f5f5,stroke:#525252,color:#111827;
    classDef external fill:#fff7ed,stroke:#c2410c,color:#111827;
    class rethRpc,rethTx,rethFb,pending,succinct rust;
    class gethRpc,preconfRpc,gethPool,preconfApi,preconfPool,preconfChecker,preconfResult,preconfCoord,opnode,leader,attrs,buildStart,sealed,conductorCommit,batcher,derive,pendingSafe,safe,finalizedByNode,conductorWs go;
    class execution mixed;
    class unsafe,finalized state;
    class rollupBoost,l1,l1Proof external;
```

## 调用链 / 组件路径

| 阶段 | 调用链 | 语言 | 证据路径 |
|---|---|---|---|
| 用户提交到 reth | `OpEthApi::send_raw_transaction` -> 可选 `raw_tx_forwarder.forward_raw_transaction` -> 本地 `pool.add_transaction` | Rust | `references/codebase/mantle/reth/crates/optimism/rpc/src/eth/transaction.rs` |
| reth pending / Flashblocks receipt | `send_raw_transaction_sync` 同时监听 canonical stream 和 `pending_block_rx`；`transaction_receipt` 可查 pending flashblock | Rust | `references/codebase/mantle/reth/crates/optimism/rpc/src/eth/transaction.rs`；`references/codebase/mantle/reth/crates/optimism/rpc/src/eth/pending_block.rs` |
| reth Flashblocks consumer | `WsFlashBlockStream` -> `FlashBlockService` -> `FlashBlockBuilder::execute` -> pending block | Rust | `references/codebase/mantle/reth/crates/optimism/flashblocks/src/service.rs`；`references/codebase/mantle/reth/crates/optimism/flashblocks/src/worker.rs`；`references/codebase/mantle/reth/crates/optimism/node/src/args.rs` |
| op-geth 普通交易入口 | `eth_sendRawTransaction` -> `SubmitTransaction` / `SendTx` -> txpool pending | Go | `references/codebase/mantle/op-geth/internal/ethapi/api.go`；`references/codebase/mantle/op-geth/eth/api_backend.go` |
| op-geth preconf RPC | `TransactionAPI.SendRawTransactionWithPreconf` -> `EthAPIBackend.SendTxWithPreconf` -> `sendTxWithPreconf` -> `SendTx` -> 等待 `NewPreconfTxEvent` 返回 status / receipt | Go | `references/codebase/mantle/op-geth/internal/ethapi/api.go`；`references/codebase/mantle/op-geth/eth/api_backend.go`；`references/codebase/mantle/op-geth/eth/filters/api.go` |
| op-geth preconf txpool / miner | `LegacyPool.addPreconfTx` -> `handlePreconfTx` -> `NewPreconfTxRequest` -> `Miner.preconfLoop` -> `preconfChecker.Preconf` -> `applyPreconfTransaction`；超时或冲突时 `RevertTx` 回滚快照 | Go | `references/codebase/mantle/op-geth/core/txpool/legacypool/legacypool_preconf.go`；`references/codebase/mantle/op-geth/core/txpool/txpool_preconf.go`；`references/codebase/mantle/op-geth/miner/miner_preconf.go`；`references/codebase/mantle/op-geth/miner/preconf_checker.go` |
| op-geth preconf sealing 协调 | `miner.fillTransactions` 调用 `PausePreconf`；优先提交 `PendingPreconfTxs`；结束后 `UnpausePreconf` 用新 env 恢复预确认 | Go | `references/codebase/mantle/op-geth/miner/worker.go`；`references/codebase/mantle/op-geth/miner/preconf_checker.go`；`references/codebase/mantle/op-geth/core/txpool/locals/preconf_tx_tracker.go` |
| op-geth preconf 配置与测试 | CLI 暴露 `--miner.enablepreconfchecker`、preconf txpool 过滤和 timeout 参数；`preconf/` 包含 config、FIFO、sync status、metrics、deposit log/source；`tests/preconf/` 覆盖压力和集成场景 | Go | `references/codebase/mantle/op-geth/cmd/utils/flags.go`；`references/codebase/mantle/op-geth/preconf/`；`references/codebase/mantle/op-geth/tests/preconf/` |
| op-conductor HA / relay | `OpConductor` 初始化 Raft、RPC、health monitor、flashblocks handler；handler 从 rollup-boost WS 读取消息，仅 leader 广播给客户端 | Go | `references/codebase/mantle/mantle-v2/op-conductor/conductor/service.go`；`references/codebase/mantle/mantle-v2/op-conductor/consensus/raft.go`；`references/codebase/mantle/mantle-v2/op-conductor/rpc/ws/flashblocks_handler.go` |
| op-node sequencer 排序 | `Sequencer.startBuildingBlock` -> `PreparePayloadAttributes` -> `BuildStartEvent` -> `EngineController.startPayload` | Go | `references/codebase/mantle/mantle-v2/op-node/rollup/sequencing/sequencer.go`；`references/codebase/mantle/mantle-v2/op-node/rollup/engine/build_start.go`；`references/codebase/mantle/mantle-v2/op-node/rollup/engine/engine_controller.go` |
| execution / unsafe 写入 | `BuildSealEvent` -> `GetPayload` -> `BuildSealedEvent` -> `PayloadProcessEvent` -> `InsertUnsafePayload` / `NewPayload` / `ForkchoiceUpdate` | Go 调度；执行端 Rust 或 Go | `references/codebase/mantle/mantle-v2/op-node/rollup/engine/build_seal.go`；`references/codebase/mantle/mantle-v2/op-node/rollup/engine/build_sealed.go`；`references/codebase/mantle/mantle-v2/op-node/rollup/engine/engine_controller.go` |
| unsafe -> safe | `op-batcher` 拉取 unsafe blocks -> `channelManager.AddL2Block` -> `TxData` -> blob/calldata tx -> L1；`op-node/derive` 读取 L1 batcher data 并推进 `TryUpdatePendingSafe` / `TryUpdateLocalSafe` / `PromoteSafe` | Go | `references/codebase/mantle/mantle-v2/op-batcher/batcher/driver.go`；`references/codebase/mantle/mantle-v2/op-batcher/batcher/channel_manager.go`；`references/codebase/mantle/mantle-v2/op-node/rollup/derive/mantle_blob_source.go`；`references/codebase/mantle/mantle-v2/op-node/rollup/engine/engine_controller.go` |
| safe -> finalized / proof | `op-succinct/validity` proposer 增加 range requests、请求 range/aggregation proof、提交 aggregation proof 到 `OPSuccinctL2OutputOracle` 或 `DisputeGameFactory` | Rust | `references/codebase/mantle/op-succinct/validity/bin/validity.rs`；`references/codebase/mantle/op-succinct/validity/src/proposer.rs`；`references/codebase/mantle/op-succinct/validity/src/proof_requester.rs` |

## 待确认点

- Mantle reth 的 Flashblocks consumer 和 op-conductor relay 在代码中存在，但生产是否启用 `--flashblocks-url` / `RollupBoostWsURL` 需要部署配置确认。
- 本地分析仓库没有看到 Flashblocks producer；op-conductor 连接的是外部 rollup-boost WebSocket，因此 producer 归属不能从本仓库确认。
- op-geth preconf 的 RPC、txpool、miner、config 和测试路径完整存在；默认 `EnablePreconfChecker=false`，生产是否启用 `--miner.enablepreconfchecker` 以及 preconf tx 过滤规则需要部署配置确认。
- op-succinct validity proof 服务和合约路径完整存在，但是否已在 Mantle 主网承担最终确认，需要部署状态确认。
