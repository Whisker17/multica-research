# Paladin Deep Dive

Paladin 不是一条新链，也不是对 EVM client 的分叉改造；更准确地说，它是运行在基础 EVM 旁边的 privacy transaction runtime。它把一笔企业隐私交易拆成两个平面：基础链继续负责公开排序、最终性和可验证事实，Paladin Sidecar 负责私有数据处理、证明、背书、身份解析和节点间分发。这个分离是 Paladin 架构里最重要的判断：不要求底层链理解业务明文，也不要求 EVM 节点内置某一种隐私协议，而是在标准 EVM 之上提供一个可插拔的隐私交易操作层。

## Paladin 的架构设计详解

### 1\.1 High\-Level Architecture

![Image](https://internal-api-drive-stream.larksuite.com/space/api/box/stream/download/authcode/?code=ZTY1YzZjYTQwODQxYTI5YTdhNzE3ZjgwMDAzMTU3NTJfMmMwMzY5MmFlZDg4OTczYTY5Y2NhZjgwMTE3OWQwNDBfSUQ6NzYzOTE3MzM2MDUyNTUxMjExOV8xNzc5OTYyODUzOjE3ODAwNDkyNTNfVjM)

从图上看，Paladin 可以拆成三层。Layer A 是 Base EVM Ledger，可以是未修改的 Besu，也可以是满足接口条件的其他 EVM 链。它负责排序、最终性、双花防护和链上锚定：Zeto 的 ZKP verifier 与 nullifier，Noto 的 notary certificate 或 opaque state hash，Pente 的 privacy group transition、input/output/read state hash、EIP\-712 签名验证结果和 externalCalls 都在这一层落账。链上只保存 hash、commitment、nullifier、root、签名验证结果或 opaque state ID；金额、owner、salt、witness、私有合约 storage 和业务 payload 留在链下 Paladin 节点之间保存和分发。这样做的好处是 EVM 兼容性和公开可审计事实，代价是它不隐藏提交地址、合约地址、时间、gas 或 commitment 数量这类 metadata。



Layer B 是 Paladin Runtime，用户请求先进入 TXManager；私有交易进入 Sequencer 和 Domain Plugin，公共交易交给 PublicTxManager；等 Layer A 确认后，BlockIndexer 再反向驱动 StateManager 做最终化。这条箭头说明了 Paladin 的状态原则：本地发送交易不等于状态前进，只有区块确认被索引后，私有 UTXO 才进入不可逆状态。

Layer B 的组件分工也围绕这个原则展开。

- State Manager 是 SQL\-backed UTXO state store，管理 DomainContext、create/spend/read locks、confirm/finalize 和 nullifier。State Manager 不只是保存余额，它要记录哪些状态可用、哪些状态正在被某笔交易读取、哪些状态已经被本地创建但尚未被基础链确认，以及哪些状态已经因为区块确认进入终态。

- Sequencer 采用 Originator/Coordinator 模型：Originator 在发起节点维护单笔交易状态机，Coordinator 按合约地址排序同一 UTXO 集合上的竞争，并编排 Assemble、Endorse、Prepare。Block Indexer 监听区块和 receipt，是状态最终化的边界。

- Key Manager 解析逻辑身份、查找 secp256k1 或 BabyJubJub verifier，并调用签名模块；

- HSM 或远程签名属于可扩展 signing module 模式，不是固定内置后端。

- Transport 通过 gRPC/mTLS P2P 承担背书请求、远程身份解析、sequencer 协调和可靠状态分发。



Layer C 只在 Pente 中出现。Pente 为 privacy group 提供临时 Besu EVM 和私有 account world state，让组内成员运行 Solidity/EVM 风格的私有合约。它不是另起一条链，而是在 Paladin 节点内按需执行 ephemeral EVM，生成 state diff，再把 input/read/output account state hash 和成员签名提交到 Layer A。这样做的好处是保留 EVM Account 模型的复杂状态表达力，代价是 Pente 的私有 EVM 版本需要和目标链预期保持一致，遇到新 opcode、precompile 或特殊 gas 语义时要单独验证。



三类 domain 则映射到不同层。

- Noto 是 Layer B domain plugin 加 Layer A contract，用 notary 做链下验证和业务背书，适合发行方或转让代理必须参与的监管资产。

- Zeto 也是 Layer B plugin 加 Layer A contract，但信任锚换成 ZKP：完整金额和 owner 留在链下，链上验证 Groth16 proof、commitment 和 nullifier。

- Pente 同时覆盖三层：Layer C 运行 ephemeral EVM，Layer B plugin 负责执行、背书和状态分发，Layer A privacy\-group contract 验证 transition 签名、锚定状态 hash 并原子执行 externalCalls。

Paladin 的核心不是某一个隐私协议，而是让不同信任模型共享同一个隐私交易 runtime。

### 1\.2 交易流介绍

理解 Paladin 最直接的方式，是跟着一笔私有交易走完系统。Noto、Zeto、Pente 共享同一个五阶段骨架：

```Bash
Init → Assemble → Endorse → Prepare → Submit
```

差异主要集中在 Assemble 和 Endorse，因为每个 domain 对“谁能证明状态转换有效”有不同答案；Submit 之后的公共交易管理、确认索引和状态最终化则是统一边界。

```mermaid
sequenceDiagram
    autonumber
    participant User as User / DApp
    participant RPC as RPCServer<br/>(JSON-RPC)
    participant TXM as TXManager<br/>(API Gateway)
    participant DB as Persistence<br/>(SQLite/Postgres)
    participant Seq as SequencerManager
    participant Orig as Originator<br/>(sender node)
    participant Trans as TransportManager<br/>(gRPC mTLS P2P)
    participant Coord as Coordinator<br/>(per-contract)
    participant Domain as Domain Plugin<br/>(Noto/Zeto/Pente)
    participant State as StateManager<br/>(DomainContext)
    participant IdRes as IdentityResolver
    participant SP as SyncPoints
    participant PubTX as PublicTxManager<br/>(EVM TX Engine)
    participant Key as KeyManager
    participant Eth as EthClientFactory
    participant EVM as EVM Chain<br/>(Mantle)
    participant BIdx as BlockIndexer

    Note over User,EVM: ━━━ Phase 1: Init — 身份解析 ━━━

    User->>RPC: ptx_sendTransaction(domain, to, function, from, data)
    RPC->>TXM: SendTransactions()
    TXM->>TXM: resolveNewTransaction()<br/>ABI lookup → function selector → parse inputs
    TXM->>DB: insertTransactions()<br/>(idempotency key dedup)
    TXM->>Seq: HandleNewTx() [post-commit]
    Seq->>Domain: InitTransaction(tx)
    Domain->>IdRes: resolve verifiers<br/>(BJJ keys / secp256k1 / salt-masked)
    IdRes-->>Domain: resolved verifiers
    Domain-->>Seq: PreAssembly{TransactionSpec, RequiredVerifiers}
    Seq->>Orig: QueueEvent(TransactionCreatedEvent)

    Note over User,EVM: ━━━ Phase 2: Assemble — 状态组装与证明生成 ━━━

    Orig->>Trans: SendDelegationRequest → coordinator node
    Trans->>Coord: DelegatedEvent
    Coord->>Coord: action_SelectTransaction()
    Coord->>Trans: sendAssembleRequest → originator node
    Trans->>Orig: AssembleRequest
    Orig->>Domain: AssembleTransaction()
    Domain->>State: FindAvailableStates()<br/>(query available UTXOs)
    State-->>Domain: candidate UTXOs
    Domain->>Domain: UTXO selection<br/>+ output construction<br/>+ ZKP witness build<br/>+ Groth16 proof gen (Zeto)<br/>or attestation request (Noto)<br/>or temp EVM exec (Pente)
    Domain->>State: UpsertStates(new outputs)
    Domain-->>Orig: AssembleResult{inputs, outputs, attestationPlan}
    Orig->>Trans: AssembleSuccessEvent → coordinator
    Trans->>Coord: AssembleSuccessEvent
    Coord->>State: AddStateLocks(spend/create/read)

    Note over User,EVM: ━━━ Phase 3: Endorse — 分布式背书 ━━━

    alt Zeto (SELF mode)
        Coord->>Coord: ZK proof IS the endorsement<br/>No external round-trip needed
    else Noto (ENDORSER_SUBMIT)
        Coord->>Trans: sendEndorsementRequest → notary node
        Trans->>Trans: notary verifies ownership,<br/>balance, ECDSA sig, business rules
        Trans->>Coord: EndorsedEvent(notary signature)
    else Pente (GROUP_SCOPED_IDENTITIES)
        loop For each group member
            Coord->>Trans: sendEndorsementRequest → member node
            Trans->>Trans: member re-executes in temp EVM,<br/>verifies state diff matches
            Trans->>Coord: EndorsedEvent(EIP-712 signature)
        end
    end

    Note over User,EVM: ━━━ Phase 4: Prepare — 交易编码 ━━━

    Coord->>Domain: PrepareTransaction()
    Domain->>Domain: Encode EVM calldata:<br/>Zeto: proof(8 uint256) + commitments + encrypted data<br/>Noto: mint/transfer/createLock calldata<br/>Pente: transition() + endorsement sigs + externalCalls
    Domain-->>Coord: PreparedPublicTransaction{to, calldata, from}
    Coord->>SP: PersistDispatchBatch()
    SP->>PubTX: WriteNewTransactions()<br/>(allocate nonce slot)
    SP->>DB: write dispatches table<br/>(private TX ID → public TX ID)

    Note over User,EVM: ━━━ Phase 5: Submit — 链上提交与确认 ━━━

    PubTX->>PubTX: orchestrator[signingAddr]<br/>dequeue pending TX
    PubTX->>Eth: eth_estimateGas
    Eth->>EVM: estimateGas
    EVM-->>Eth: gas limit
    Eth-->>PubTX: gas limit × safety factor
    PubTX->>Eth: eth_feeHistory
    Eth->>EVM: feeHistory
    EVM-->>Eth: baseFee + rewards
    Eth-->>PubTX: maxFeePerGas, maxPriorityFeePerGas
    PubTX->>Key: Sign(EIP-1559 tx payload)
    Key-->>PubTX: signed raw tx
    PubTX->>Eth: eth_sendRawTransaction
    Eth->>EVM: submit to mempool
    EVM-->>Eth: tx hash

    Note over EVM,BIdx: Block mined with transaction

    BIdx->>Eth: eth_getBlockByNumber (poll / WS subscribe)
    Eth->>EVM: getBlock
    EVM-->>Eth: block with receipts
    Eth-->>BIdx: confirmed block

    Note over User,EVM: ━━━ Post-Confirmation — 状态最终化 ━━━

    BIdx->>TXM: PreCommitHandler
    TXM->>PubTX: MatchUpdateConfirmedTransactions()
    PubTX-->>TXM: PublicTxMatch[]
    TXM->>DB: FinalizeTransactions()<br/>(write receipts, advisory lock for ordering)
    TXM->>Seq: PrivateTransactionsConfirmed()
    Seq->>State: WriteStateFinalizations()<br/>(UTXO: spend records + confirm records)
    Seq->>Coord: ConfirmedSuccessEvent
    Coord->>State: ResetTransactions()<br/>(clear in-memory locks)
    Seq->>Trans: BuildStateDistributions()<br/>→ SendReliable() to UTXO owners
    TXM->>PubTX: NotifyConfirmPersisted() [PostCommit]

    User->>RPC: ptx_getTransactionReceipt(txId)
    RPC->>TXM: GetTransactionReceipt()
    TXM-->>User: receipt{success, blockNumber, txHash, ...}```

五个阶段的职责边界很清楚：Init 做身份解析和交易校验；Assemble 做 UTXO 选择、私有执行和证明材料准备；Endorse 做自证明、notary 背书或组成员签名；Prepare 把私有交易转换成基础 EVM 可执行的 calldata；Submit 由 PublicTxManager 接管 nonce、gas、签名、广播和确认跟踪。前四步属于私有交易状态机，最后一步属于公共 EVM 交易管理。

#### 详细的步骤解析

Init 从 `ptx\_sendTransaction` 开始。TXManager 解析 ABI、函数选择器和参数，DomainManager 根据合约地址定位 domain contract，并把交易写入 SQL 以获得幂等性。随后 domain 的 `InitTransaction` 触发身份解析：Zeto 解析 BabyJubJub key，因为它适合进入 BN254/Circom 电路；Noto 解析 notary、sender、recipient 等 secp256k1/Ethereum 地址；Pente 解析 privacy group scoped identity，也就是带 genesis salt 的组内身份，让同一逻辑身份在不同 group 中呈现不同 verifier。这个阶段的价值是把未知合约、ABI 不匹配、身份缺失和 key 不可用尽早暴露。

Assemble 由 Coordinator 调用 domain plugin。StateManager 通过 DomainContext 查询可用 UTXO，并施加 spend/create/read locks。Zeto 选择输入、构造 output commitment、生成 witness 和 Groth16 proof；Noto 选择 NotoCoin、构造新 coin 或 lock 信息，并准备 notary attestation；Pente 加载 privacy group 的 account state，在临时 Besu EVM 中执行私有合约调用，捕获 read/write 集合和 state diff。locks 不是全网排他锁，它们减少本地和协调器窗口内的冲突；最终双花裁决仍在 Layer A 的 `\_unspent`、nullifier 或 Pente state hash 检查上完成。

Endorse 是三个 domain 差异最大的阶段。Zeto 使用 SELF 模式，ZK proof 本身就是背书，不需要外部往返。Noto 的标准路径是 ENDORSER\_SUBMIT，notary 验证 ownership、balance、ECDSA 签名和业务规则；但 hooks 或 delegated lock 路径可能改变实际 submitter，所以不能写成所有 Noto 状态转换都永远由 notary 提交。Pente 使用 GROUP\_SCOPED\_IDENTITIES：组成员独立重放 ephemeral EVM，确认 state diff 与 assembler 一致，再签署 EIP\-712 transition。它防止单点伪造组内状态转换，代价是延迟和可用性受组成员在线状态影响。

Prepare 把私有材料编码成基础链 calldata。Zeto 编码 proof、commitments、encrypted data 或 nullifier 公开输入；Noto 编码 mint、transfer、createLock、spendLock 等调用；Pente 编码 transition、endorsement signatures、inputs/reads/outputs 和 externalCalls。此时 Paladin 只是形成 public transaction intent。随后 PublicTxManager 按提交地址管理 nonce，估算 gas，获取 EIP\-1559 fee，用 KeyManager 签名，再调用 `eth\_sendRawTransaction`。这样 domain 不需要自己处理 nonceTooLow、underpriced、gas bump 或 mempool 丢弃。

Submit 后还没有完成私有状态最终化。PublicTxManager 可以看到 tx hash，但 StateManager 只有在 BlockIndexer 处理到确认区块和 receipt 后，才会通过 `WriteStateFinalizations\(\)` 把 input 标记为 spent，把 output 标记为 confirmed，并写入 read/info records。随后 Sequencer 构建 state distribution，Transport 用可靠投递把完整私有状态发送给新的 UTXO owner 或相关参与方。发送 raw transaction、收到 alreadyKnown、进入 mempool，都不等于私有状态不可逆。



#### 双花/容错机制

失败恢复也沿着这两个平面展开。UTXO 竞争的典型场景不是两个不同用户争抢同一笔钱，而是同一 owner（或同一组织中持有相同密钥的操作人员）在不同 Paladin 节点上对同一 UTXO 发起了重复花费，由于多个节点各自的 DomainContext 是本地内存视图，互相不可见，因此都认为该 UTXO 仍然可用。

Sequencer 通过三层防线解决：Originator 级别的本地乐观锁、Coordinator 级别的 per\-contract 排序仲裁、以及基础链的链上双花拒绝（Noto 的 `\_unspent` 或 Zeto 的 `\_nullifiers`）。竞争失败的交易可释放锁、重新入池并选择新的 UTXO；背书请求使用 idempotent request，超时后 nudge/retry；Pente 成员长期离线时交易停在背书阶段。公共交易侧由 PublicTxManager 处理 nonce、gas 和重发：underpriced 或长时间未确认时，按 EIP\-1559 替换规则 gas bump，并用同 nonce resubmit；`nonceTooLow` 则等待 BlockIndexer 对账。崩溃恢复依赖 SQL 中的交易、nonce、submission history、reliable messages 和 incomplete transaction poll。Paladin 的一致性不是来自“永不失败”，而是来自每个阶段都有重试边界，并且只有区块确认后的 finalization 才让私有 UTXO 状态真正前进。

## Paladin 的 Layer B/C 中隐私模块详解

### 2\.1 Layer B 中的 Noto 和 Zeto 方式

Noto 和 Zeto 不应被理解为竞争关系，而是 Paladin 在 Layer B 给出的两种隐私 token 工具：

- Noto 把信任放在可信 notary 上，用制度背书换取低复杂度和合规可控性

- Zeto 把信任放在 ZKP（零知识证明）和链上 verifier 上，用数学证明换取不依赖单一中介的隐私验证。

前者适合 issuer\-backed stablecoin、tokenized deposit、custody asset 等本来就需要发行方或银行作为权威方的资产；后者适合需要链上验证合法性、但不希望公开身份和金额的私密转账与受监管交易。

两者共同的底座是 UTXO。Paladin 没有沿用 ERC\-20 那种 `balances\[address\]` 的透明账户模型，而是把每次资产状态变更拆成一次性状态对象：旧状态被花费，新状态被创建。差异在于“谁证明这次花费是合法的”。Noto 的答案是 notary 看见必要明文并签名背书；Zeto 的答案是 prover 在链下生成 proof，链上只验证 proof 与公开输入。

|**维度**|**Noto**|**Zeto**|
|---|---|---|
|信任假设|部署时指定的单一 Ethereum notary 地址是可信背书方|不依赖单一中介，链上验证 Groth16 proof|
|隐私机制|Confidential UTXO；链上只存 opaque state ID、`\_unspent`、`\_locked`、lock hash|Commitment、Nullifier、SMT membership 和 ZKP|
|表达力|mint/transfer/burn/createLock/delegate/spend/cancel|隐私 token 属性组合，受电路形状约束|
|性能瓶颈|notary 吞吐、可用性和密钥安全|proof time、verifier gas、SMT insertion、nullifier SSTORE|
|适用场景|受控发行、银行存款 token、托管资产、监管权威资产|私密转账、KYC\-gated trading、历史隐藏资产|
|主要限制|notary downtime/compromise 是核心风险；链上没有 ZK proof|trusted setup、gas 高、电路升级成本高|

#### 2\.1\.1 Noto 详解

Noto 的模型是 confidential UTXO。`NotoCoin` 明文包含 salt、owner、amount，但基础链只看到 `bytes32` state ID；`Noto\.sol` 用 `\_unspent` 防双花，用 `\_locked` 记录锁定状态，用 lock hash 预承诺后续 spend/cancel。标准路径下，`mint`、`transfer`、`burn`、`createLock` 都由 notary 背书并提交，Solidity 层也以 `onlyNotary` 保护。这里的隐私来自链下状态分发和链上哈希锚定，而不是 ZK proof。

Noto 的提交路径有三个细节必须分清。basic mode 中，标准 mint/transfer/burn/createLock 由 notary 提交；hooks mode 中，Noto 操作先进入 Pente privacy group 的 hook 合约，hook 通过 `PenteExternalCall` 让 Pente group public address 调用 Noto；lock 被 delegation 后，`spendLock`、`cancelLock`、`delegateLock` 由当前 delegated lock spender 提交。也就是说，notary 是核心信任锚，但 submitter 会随 hooks 和 lock 生命周期变化。

lock 机制让 Noto 不只是简单转账工具，而能参与 DvP 这类两阶段结算。`createLock` 先把普通 coin 转成 locked coin，并在链上保存 spend/cancel hash commitment；`delegateLock` 再把执行权交给 Atom 或其他 spender；最终 `spendLock` 或 `cancelLock` 只能由当前 spender 调用，并且 calldata 必须匹配预承诺 hash。这个设计的好处是，资产可以先被冻结在一个可审计状态中，等另一条支付腿准备好后再原子释放；坏处是 lock 的取消、再委托和超时处理必须在业务流程中明确设计，否则容易留下 pending 状态。

这种设计非常适合“权威方本来就存在”的业务。银行发行 tokenized deposit，本来要控制铸造、赎回、冻结和审计；托管机构发行 custody asset，本来要承担资产真实性。Noto 直接把这些制度信任编码成 notary 背书，而不是把所有规则塞进电路。代价也明确：notary 宕机会阻塞交易，notary 私钥被攻破会集中放大风险；coupon、maturity、redemption、reserve reconciliation 等复杂生命周期也不在 Noto base contract 内，需要 Pente hooks 或应用层合约补足。

hooks mode 是 Noto 的重要扩展点。notary 可以不只是一个外部服务地址，而是一个 Pente privacy group 的公开地址；组内 hook 合约在私有 EVM 中检查 KYC、额度、黑名单、审批状态或内部账务，再决定是否 emit `PenteExternalCall` 去调用 Noto base contract。这样 Noto 仍保持 C\-UTXO 的链上隐私外壳，但复杂合规逻辑可以留在私有合约中执行。换句话说，Noto 负责资产状态的受控迁移，Pente hooks 负责解释“为什么这次迁移应当被允许”。

#### 2\.1\.2 Zeto 详解

Zeto 则把合法性放进 ZKP。一个 fungible UTXO 的 commitment 可概括为 `Poseidon\(4\)\(value, salt, ownerPubKey\[0\], ownerPubKey\[1\]\)`，其中 `ownerPubKey\[0/1\]` 是 BabyJubJub 公钥的 x/y 坐标，`Poseidon\(4\)` 表示 4 输入变体；链上只记录 commitment。花费时提交 `nullifier = Poseidon\(3\)\(value, salt, ownerPrivateKey\)`，合约检查 `\_nullifiers` 中是否已出现。commitment 使用公钥、nullifier 使用私钥，二者无法直接关联，因此可以隐藏被花费输入，同时防止 double spend。

Zeto 的变体本质是隐私属性组合：`Anon`、`AnonEnc`、`AnonNullifier`、`AnonEncNullifier`、`AnonNullifierKyc`、`AnonEncNullifierKyc` 覆盖匿名、金额加密、历史隐藏和 KYC；burnable 支持销毁/赎回；non\-repudiation 给审计方提供可解密路径；Qurrency 引入 ML\-KEM 相关路径；NFT variants 把 commitment 扩展到 tokenId/tokenUri。性能上，native `anon` proof 约 0\.3\-0\.5s，nullifier 约 1\-3s，KYC 约 3\-5s，browser/WASM 更慢。gas 方面，`Zeto\_Anon` 约 326k，`AnonEnc` 约 425k，nullifier/KYC 约 2\.0M\-2\.47M，NonRepudiation 约 2\.76M；nullifier 变体贵，主因是 on\-chain SMT insertion 和 nullifier SSTORE。

从工程选型看，Zeto 的强项是把“链上不可见”和“链上可验证”同时成立。它的弱项也来自同一个选择：每个电路都需要 proving key、verification key 和 trusted setup；电路一旦变更，仪式、verifier、SDK 和运维流程都要随之更新。相比之下，Noto 的升级更多是合约和 notary 逻辑治理问题。一个偏制度信任，一个偏密码学信任，这正是它们互补而非替代的原因。

### 2\.2 Layer C 中的 Pente 方式

Noto/Zeto 都围绕 token UTXO 转换建模，表达复杂业务逻辑并不自然。授信额度、债券生命周期、权限表、订单簿、赎回窗口更像 Account 模型和 Solidity 合约的领地。Pente 补上的就是这一层：把完整 EVM 语义放进 privacy group，让企业可以写私有智能合约。

这也是 Paladin Layer C 的定位：不是再发明一种 token，而是给私有业务逻辑一个可编程执行环境。Layer B 解决“资产如何私密转移”，Layer C 解决“复杂业务状态如何私密演进”。如果没有 Pente，Noto/Zeto 可以完成资产相关的操作，但债券簿记、认购分配、合规审批、内部账户镜像等逻辑会散落在链下服务中；有了 Pente，这些逻辑可以用 Solidity 表达，并通过同样的 UTXO 锚定机制进入 Paladin 的状态生命周期。



Pente 不是另一条私有链，而是“EVM 语义包在 UTXO 私有状态里”。它是 Java domain，直接嵌入 Hyperledger Besu EVM；每笔交易实例化一个 `EVMRunner`，按组配置选择 London/Paris/Shanghai EVM version，惰性加载账户状态，执行 calldata，捕获 committed account updates，然后销毁本次 EVM 实例。Ephemeral EVM 的“临时”指执行上下文不持久；持久化的是 Paladin State Store 里的账户快照。

Pente 把 EVM account 编码为 `AccountState\_v24\_10\_0 \{address, nonce, balance, codeHash, storage\}`。如果一笔私有交易修改了合约 storage，旧账户快照成为 spent input，新账户快照成为 output；如果只是读取某个账户，该 state ID 进入 reads。链上的 `PentePrivacyGroup\.transition\(\)` 只锚定 opaque state IDs、reads/inputs/outputs 和 signatures，并验证 inputs 未花费、reads 仍有效、outputs 新增、`txId` 未重复。合约代码、storage diff、nonce/balance 和函数参数都在组内分发，不上链公开。

这层封装很关键。EVM 看到的是 account、nonce、balance、code 和 storage；Paladin 基础设施看到的是 input/read/output 状态集合；基础链看到的是不可解释的 `bytes32` state IDs。Pente 在三者之间做确定性转换：组内成员从相同账户快照出发，执行相同 calldata，得到相同账户更新，再用签名证明大家同意这次转换。链上不需要理解 Solidity 语义，只需要验证 UTXO 可用性和背书签名。

Privacy Group 是 Pente 的信任边界。`group\.salt` 用于生成 salt\-masked identities，使链上背书地址不易直接映射到真实成员。当前产品语义是 N\-of\-N / 100% endorsement：每个成员都要重新执行交易，确认 inputs、reads、outputs 以及 externalCalls 一致后签 EIP\-712。成员集合创建后不可变，牺牲运维灵活性，但让“谁能看状态、谁必须背书、谁能让 transition 生效”非常清楚。

这个模型的限制也直接来自全员重放。每笔交易都要重建执行上下文并从 State Store 读账户；每个成员都要执行一次完整 EVM 并签名；storage\-heavy 合约会带来读取、序列化和分发尾延迟。因此 Pente 更适合 2\-10 人小组，任何成员离线都会阻塞交易。若启用 externalCalls，公开 `contractAddress` 和 `callData` 会进入基础链交易，不能当作私密数据。

## 实际工作流示例

前两节解释了 Paladin 在架构上的分层：隐私域负责私有状态和证明，基础 EVM/QBFT 链负责公开验证、排序和最终性，Paladin 节点负责把两者编排成一个可运维的企业系统。本节用两个业务化示例把这些组件串起来：

### 3\.1 示例 A \- 机**构间隐私稳定币转账（带 KYC 合规）**

假设机构 A 需要向机构 B 转账 100 万 USDT 等值稳定币。业务上，A 的财务系统只希望看到“付款已提交、已确认、对手方可收款”；B 的系统只希望收到一笔可继续花费的私有余额；外部链上观察者不应看见金额、双方身份和 UTXO 明文。合规上，系统又必须证明转账双方都属于 KYC\-approved 集合。这里最自然的域是 Zeto 的 `AnonNullifierKyc` 或加密扩展 `AnonEncNullifierKyc`：前者把 nullifier、commitment SMT 和 KYC identities SMT 组合在一个 Groth16 证明中，后者再增加接收方可恢复输出的加密材料。

```mermaid
sequenceDiagram
    participant App as Institution A App
    participant PA as Paladin A
    participant Z as Zeto Domain
    participant KYC as KYC SMT/Contract
    participant PTM as PublicTxManager
    participant EVM as Base EVM/QBFT
    participant BI as BlockIndexer
    participant PB as Paladin B

    Note over App,PTM: Off-chain/private boundary: business intent, identities, UTXO plaintext, salts, keys and Merkle paths stay inside Paladin/domain systems.
    App->>PA: Submit transfer intent<br/>from A, to B, amount, token, domain=zeto
    PA->>Z: Route through DomainManager
    Z->>PA: Resolve A/B BabyJubJub keys and local state
    Z->>Z: Select spendable UTXOs and change output
    Z->>KYC: eth_call current identitiesRoot
    KYC-->>Z: KYC SMT root
    Z->>Z: Build witness and generate Groth16 proof
    Z-->>PA: transfer calldata with proof and public signals
    PA->>PTM: Estimate gas, fee, nonce / sign raw tx
    Note over PTM,EVM: On-chain/public boundary: nullifiers, output commitments, roots, proof calldata, tx hash, block and gas are visible.
    PTM->>EVM: eth_sendRawTransaction
    EVM->>EVM: Verify proof, roots, nullifier freshness, commitment inserts
    EVM-->>BI: Finalized block event
    BI->>PA: Mark inputs spent and outputs confirmed
    PA->>PB: gRPC/mTLS private state delivery for B output UTXO
    PB-->>App: Business receipt can be reconciled by B-side systems```

1. **用户发起。** 机构 A 的业务系统调用 Paladin API，提交付款意图：付款方、收款方、金额、稳定币标识和 `domain: zeto`。用户可见的是一笔普通的机构付款请求；底层则进入 Paladin 的 TXManager/DomainManager 状态机。

2. **身份解析。** Paladin A 解析 A/B 的链下业务身份到 Zeto 使用的 BabyJubJub 公钥，并取得必要的签名 key 或 registry 记录。如果 A 或 B 的隐私域身份不存在，交易在初始化阶段失败，而不是等到链上才失败。

3. **UTXO 选择。** Zeto domain 通过 StateManager 查询机构 A 本地可花费的 unspent UTXO，选择足以覆盖 100 万等值稳定币的输入，并准备给 B 的输出和给 A 的找零输出。用户看到的是“付款 100 万”；底层看到的是若干输入 commitment 的明文原像、salt 和 owner key。

4. **读取 KYC root。** Domain 通过 `eth\_call` 读取当前 KYC identities SMT root。该树的叶子是已 KYC 的 BabyJubJub 公钥，root 是链上公开承诺。这里的合规语义是 proof of membership：证明 A/B 的隐私公钥属于 KYC 集合，而不是在链上公开 A/B 的真实身份。

5. **构造 witness。** 本地组装 `anon\_nullifier\_kyc\_transfer\.circom` 所需见证：输入 value/salt、`inputOwnerPrivateKey`、输入 UTXO 的 `merkleProof\[\]`、A/B 的 `identityMerkleProof\[\]`、输出 value/salt 和输出 owner public keys。若使用加密变体，还会加入 ECDH 相关私密输入和输出密文材料。

6. **生成 ZKP 证明。** Zeto 生成 Groth16 proof，证明四件事同时成立：输入 commitment 确实存在于 `utxosRoot`；`nullifier = Poseidon\(value, salt, ownerPrivateKey\)` 派生正确且不会暴露被花费的 commitment；输入输出金额守恒；付款方和收款方公钥都属于 `identitiesRoot`。

7. **准备 calldata。** Domain 编码 Zeto `transfer` 调用。KYC nullifier 电路的 public inputs 包括 `nullifiers`、`outputCommitments`、`utxosRoot`、`identitiesRoot`、`enabled\[\]`；加密 KYC 变体还会公开 `encryptionNonce`，并把 `ecdhPublicKey`、`encryptedValues` 等作为 verifier public signal/event payload 的一部分。真实金额、身份、UTXO 原像和 Merkle path 不进入链上 calldata。

8. **公共交易提交。** PublicTxManager 执行 `eth\_estimateGas`、fee 查询、nonce 分配和 EIP\-1559 type\-2 交易签名，然后通过 `eth\_sendRawTransaction` 提交到 Base EVM/QBFT 网络（即 Layer A）。业务系统此时可先拿到 tx hash，但这只是提交凭据，不等同于最终业务确认。

9. **链上验证。** Zeto 合约调用 Groth16 verifier，检查 proof、root、nullifier 是否未花费，并插入新的 output commitments。任何 proof 不匹配、root 过期、nullifier 重复或 calldata 与 public signals 不一致，整笔 EVM 交易都会 revert。

10. **最终性与状态更新。** 等待 Layer A 完成 Finality，然后 BlockIndexer 通过 newHeads/receipts 观察到区块后，Paladin A 将输入 nullifier 标记为 spent，将输出 commitment 标记为 confirmed，并把本地 pending 状态推进到 finalized。

11. **私有状态分发。** 链上只知道“某些旧 UTXO 被 nullifier 消耗，某些新 commitment 被创建”。机构 B 想继续花费新余额，还需要输出 UTXO 的明文材料或可解密材料。Paladin A 通过 gRPC/mTLS transport 把 B 所需的私有状态发送给 Paladin B；B 节点落库后，这个输出才成为 B 业务系统可用的私有资产。

12. **业务回执。** A/B 最终拿到的回执包含 tx hash、block number、finality 状态、Paladin receipt 和业务关联 ID。链上可审计数据是 nullifier、output commitment、`utxosRoot`、`identitiesRoot`、proof calldata、交易哈希、区块和 gas；链下/私有数据是金额、双方真实身份、UTXO 明文、salt、私钥、Merkle path、接收方解密材料和业务 payload。

### 3\.2 示例 B \- RWA 债券的全生命周期

第二个例子展示 Paladin 的多个域如何共同服务一个更长的金融生命周期。假设发行人发行 1000 张企业债，每张面值 1000 美元，总面值 100 万美元，年化票息 5%。

因此整个系统中 Noto 负责受控发行和债券 UTXO，因为债券发行天然需要 issuer/notary 授权；Zeto 负责隐私现金流相关场景；Atom 负责 DvP 和兑付中的原子交换；Pente 负责债券生命周期中的私有业务逻辑，例如持有人快照、票息计算、转让限制、审批和异常状态。尤其要避免一个常见误解：Noto 有 mint/transfer/burn/lock，但没有原生 coupon lifecycle，也没有完整债券条款引擎；付息、到期和合规报告属于 Pente 或应用合约职责。

```mermaid
flowchart LR
    I["Stage 1: Issuance<br/>Noto issuance<br/>issuer/notary mints bond UTXOs"]
    P["Stage 2: Primary Distribution<br/>Atom primary DvP<br/>Noto bond vs Zeto cash"]
    S["Stage 3: Secondary Trading<br/>Atom secondary DvP<br/>locked bond and private cash"]
    C["Stage 4: Interest Payment<br/>Pente coupon calculation<br/>application lifecycle logic"]
    R["Stage 5: Maturity Redemption<br/>Atom burn-and-pay<br/>Noto burn vs Zeto/Noto cash"]
    I --> P --> S --> C --> R```

1. **发行，主域是 Noto。** 发行人或受托 notary 部署 Noto bond domain contract，配置 notary、mint policy、lock/burn 能力以及需要的 hooks。发行请求包含 1000 张、每张 1000 美元、年化 5% 票息、到期日和初始投资人分配。Notary 在链下验证发行授权、额度、KYC/白名单和法律文件后，提交 Noto `mint`。在 Noto 模型中，`mint` 没有输入 UTXO，输出是分配给投资人的 `NotoCoin`/bond UTXO；链上 `Noto\.mint\(\)` 始终由 notary 路径提交，只记录 opaque state IDs、交易事件和必要 hash。参与者包括发行人、notary、初始投资人和可选审计节点。链上可见的是 Noto 合约地址、mint 交易、state IDs 和 notary 提交痕迹；链下私有的是投资人名单、分配数量、认购协议、发行审批材料和每个 bond UTXO 的明文。

2. **一级分销，主编排是 Atom，资产相关是 Noto，现金相关是 Zeto。** 投资人认购债券时，发行人或承销方准备 Noto bond 交割，投资人准备 Zeto cash 付款。例如投资人 X 认购 200 张，面值 20 万美元。Paladin Sequencer 分别准备：Noto 侧创建或准备 bond transfer/lock，Zeto 侧生成 cash transfer 的 nullifier、output commitments 和 KYC proof。随后 AtomFactory 创建一次性 Atom，保存两条 operation；相关 Noto lock 被 delegate 给 Atom，Zeto payment calldata 也被放入同一组操作。`Atom\.execute\(\)` 是单笔 EVM 交易：交券和付款同时成功，或任一失败导致全部 revert。链上可见的是 lock、delegate、AtomDeployed、Atom\.execute、Zeto proof/nullifier/output commitments 和 Noto state IDs；链下私有的是认购金额、投资人真实身份、债券 UTXO 明文、现金 UTXO 明文和认购业务文件。

3. **二级交易，仍然是 Atom DvP。** 假设机构 A 卖出 100 张债券给机构 B，B 支付 10 万美元现金。A 的 Noto bond UTXO 先被 lock/prepare，B 的 Zeto cash 输入生成 nullifier 和新的输出 commitments。Atom 执行后，Noto bond 输出给 B，Zeto cash 输出给 A；BlockIndexer 分别最终化 Noto spend/confirm 和 Zeto nullifier/output，Paladin transport 把新 owner 所需的私有状态分发给对应节点。业务上这是二级市场交易；技术上它复用了一级分销同一个 DvP 模式。链上观察者最多看到某个 Atom 协调了 Noto 和 Zeto 两类状态变化，看不到谁卖给谁、卖了多少张、成交价是多少。链下则保存交易指令、对手方身份、订单/报价、bond UTXO 明文、cash UTXO 明文和合规审批记录。



4. **付息，主域是 Pente。** 年化票息 5% 意味着 100 万美元总面值对应每年 5 万美元利息；若按半年付息，每期总额是 2\.5 万美元。这个计算不应写成 Noto 的原生能力，而应放在 Pente privacy group 的生命周期合约或应用合约中。组成员可以包括发行人、受托管理人、支付代理和必要审计/监管节点。到付息日，Pente ephemeral EVM 从私有状态中读取持有人快照、票息参数、暂停/违约状态和转让限制，计算每个持有人应收利息；所有 group member 重新执行同一交易并签署 EIP\-712 transition。如果需要实际付款，Pente 可以通过 `externalCalls`/hooks 触发 Zeto 或 Noto cash 付款准备；若要求每笔付款与审批状态绑定，也可以把 Pente `transitionWithApproval` 和 cash transfer 放入 Atom。链上可见的是 Pente privacy group 地址、opaque state IDs、EIP\-712 签名、可能的 external call 目标和付款链上状态；链下私有的是持有人快照、票息公式、每个投资人的应收金额、审批意见、违约判断和完整业务 world state。

5. **到期兑付，主编排回到 Atom。** 到期时，投资人准备 burn/redeem bond UTXO，发行人准备本金付款。以仍未赎回的 1000 张为例，总本金是 100 万美元，现金腿可以是 Zeto private cash，也可以是受 notary 控制的 Noto cash，取决于产品设计。Noto 创建 burn lock 或 prepared burn unlock，表示债券状态将被销毁；发行人的现金腿生成 Zeto proof 或 Noto payment operation；Atom 在同一笔 EVM 交易中执行“烧券 \+ 付款”。如果现金付款失败，债券不会被 burn；如果 burn payload 不匹配，现金也不会转出。BlockIndexer 最终化债券 burn 和现金输出后，Pente 生命周期合约记录该债券已兑付/关闭。链上可见的是 Noto burn/lock 状态、Atom execute、现金腿 proof 或 payment state、区块和 gas；链下私有的是最终持有人、兑付明细、税务/对账材料、业务审批和本金支付分解。

### 3\.3 示例 C \- xStocks\-style Tokenized Equities 的隐私调仓与结算

第三个例子更贴近公开市场和 DeFi 语境。这个场景的业务问题不是“怎样发行一只股票”，而是“当 tokenized equity 已经存在时，机构如何私密地持有、调仓、结算和赎回”。例如一家非美国合资格机构持有 10,000 美元等值 AAPLx，希望在不公开交易图谱的情况下，把其中 4,000 美元敞口换成 NVDAx，同时用 USDC 类稳定币补足差价。公开链上如果直接做 swap，观察者可以看到地址、交易时点、资产组合变化和规模；对做市商、基金、交易所 treasury 或 RWA desk 来说，这些信息本身就是商业敏感数据。Paladin 可以把 xStock wrapper、隐私现金、合规检查和原子结算拆成不同域处理。

```mermaid
flowchart LR
    A["Eligibility & account setup<br/>Pente compliance group<br/>KYC / jurisdiction / suitability"]
    B["Wrap or mirror xStock exposure<br/>Noto xStock UTXO<br/>issuer/custodian/notary controlled"]
    C["Private rebalance intent<br/>AAPLx -> NVDAx<br/>order details stay off-chain"]
    D["Atomic settlement<br/>Atom DvP<br/>Noto xStock leg + Zeto cash leg"]
    E["Corporate action sync<br/>Pente multiplier / split rules<br/>rebasing dividend reflection"]
    F["Unwrap / redeem<br/>burn private wrapper<br/>release public xStock or cash"]
    A --> B --> C --> D --> E --> F```

1. **合资格准入，主域是 Pente。** xStocks 这类资产通常有地区、投资者资格和产品条款限制，不能写成完全无门槛的公开股票。Pente privacy group 可以承载准入规则：KYC 状态、非受限司法辖区声明、机构账户授权、交易限额、风险披露版本和产品 terms acceptance。链上只看到 Pente transition 的 state IDs 和签名；链下保留具体身份、合规材料、审批记录和条款版本。这里 Pente 的价值不是“代替法律合规”，而是把合规状态变成后续交易可以引用的私有业务条件。

2. **包装或镜像 xStock position，主域是 Noto。** 如果 xStocks 已经作为 ERC\-20 或其他标准 token 存在，Paladin 不应重新宣称自己发行底层股票；更合理的设计是由受托 gateway/custodian/notary 把外部 xStock 或其托管凭证锁入储备，再在 Paladin 内生成 Noto 形式的 private xStock UTXO，例如 private AAPLx UTXO。Noto 适合这一步，因为它表达的是受控资产凭证：mint、burn、lock 和 redeem 都需要 notary 或 Pente hook 背书。链上可见的是 Noto state IDs 和相关锚定；链下私有的是机构持仓、包装数量、储备对账、客户身份和 custody reference。

3. **私有调仓意图，主域是应用层 \+ Paladin Sequencer。** 机构提交“卖出 4,000 美元等值 AAPLx，买入 NVDAx，价格不低于某个 limit”的调仓意图。这个意图不应直接公开到基础链。Paladin 节点在链下做订单校验、UTXO 选择和对手方匹配：AAPLx 资产来自 Noto，支付或找零现金来自 Zeto，必要的合规状态从 Pente reads 引用。外部观察者不应看到机构正在从哪只股票敞口切换到哪只股票敞口，也不应看到具体金额和对手方。

4. **原子结算，主编排是 Atom。** 当买卖双方或做市商达成价格后，Paladin 准备 calldata：Noto 侧把 private AAPLx UTXO 转给买方或做市商，把 private NVDAx UTXO 转给机构；Zeto 侧生成 USDC/cash 的 nullifier、output commitments 和必要 KYC proof。Atom 把这些 operation 放进单笔 EVM transaction。任一方失败，例如 Noto lock 状态不匹配、Zeto proof 失败、价格检查不满足或 Pente eligibility read 失效，整笔交易 revert。这样可以避免“股票敞口转走但现金没到”或“现金支付成功但资产腿失败”的单边结算。

5. **corporate actions 与 rebasing，同步逻辑放在 Pente。** xStocks 公开口径中，股息经济利益不是传统现金股息，而是通过 rebasing/multiplier 让持仓余额反映 underlying 的经济变化；股票拆分、合并、暂停或产品条款变更也会影响 tokenized equity 表达。Paladin 内部不应该让 Noto 自己理解所有 corporate action。更清晰的做法是：Pente lifecycle/compliance group 读取发行方或 oracle 发布的 multiplier、split ratio、暂停状态和产品事件，计算每个 private xStock UTXO 应如何调整，再由 notary/Pente hook 触发 Noto 状态更新或要求用户在下一次交易前 roll forward。链上仍只锚定状态变化，链下保留具体持仓和计算材料。

6. **赎回或解包，Noto \+ Atom 收束。** 当机构希望退出 private xStock wrapper 时，可以 burn Noto private xStock UTXO，并由 gateway 释放公开 xStock、稳定币或其他约定资产。如果赎回涉及现金支付，Atom 可以把 burn 和 cash release 放进同一笔交易；如果涉及跨链 release，则必须承认 Atom 只保证同链原子性，跨链桥或托管释放还需要独立 finality policy、relayer 监控和储备对账。链上可见 burn/release 的公共锚定，链下保留客户、数量、储备、赎回指令和合规记录。

## 当前方案对 Mantle 的启示

对 Mantle 而言，Paladin 的集成不是“能否跑在 EVM 上”这么简单，因为目前已确认 Mantle op\-geth 在 JSON\-RPC、`newHeads` 订阅、`eth\_getBlockReceipts`、BN254 预编译、EIP\-1559 基础能力上基本满足 Paladin 需求，主要的问题在于产品目标、finality 语义、费用模型、DA 恢复和企业级运维责任这些方面，由此我们也衍生出了不同的集成方案。

### 4\.1 与 Mantle 的集成可能性分析

- **选项一：MPL standalone network。** 

    - 该方案将 Mantle Privacy Layer 作为独立许可网络部署（即 permissioned Alt\-L1），底层为 Paladin \+ Hyperledger Besu \+ QBFT，节点由 Besu、Paladin runtime 和 Postgres state store 组成；初期由 Mantle 或指定机构运营 5\-7 个 validator，成员机构运行 member node，监管或分析方可运行 observer node。MPL 不直接改 Mantle L2，也不把 Paladin 嵌入 op\-geth；与 Mantle L2 的关系是通过桥、状态锚定和身份根互认逐步实现。优点是 Paladin 的 Noto、Zeto、Pente、Atom、K8s Operator、QBFT finality 都按原设计工作，功能覆盖接近 100%；QBFT 的即时终局性更符合企业 DvP、KYC 隐私转账和私有状态最终化

- **选项二：L2 Sidecar。** 

    - 该方案保留 Mantle L2 为唯一结算链，Paladin runtime 作为 Mantle op\-geth 的 sidecar，通过 JSON\-RPC/WS 监听区块、提交交易、部署 Registry/Noto/Zeto/Pente/Atom 等合约，不修改 Mantle core。它的主要价值是 Mantle\-native：不需要桥，用户仍在一条链上操作，资产不必迁移，可直接触达 Mantle L2 资产、DeFi 和现有钱包/浏览器体验；Pente 使用 Besu EVM 语义执行私有合约，仍需与 Mantle op\-geth fork 行为做 opcode、precompile、gas、receipt 相关的适配，但是问题在于 L2 级别的 soft\-confirmation 是否支持企业级别的 Finality

两者的区别在于 MPL 优先服务的是机构后台结算，Sidecar 优先服务的是 Mantle L2 原生用户体验。前者的客户更关心节点准入、对手方治理、审计材料、finality SLA、KYC authority、私有状态备份和故障演练；后者更关心资产不用桥、钱包不切网、DeFi composability 和 explorer/SDK 的一致性。

### 4\.2 参考 Paladin 直接构造 Mantle 原生的方案

第二种则是类似于 fork Paladin，然后从 Paladin 提取设计模式和密码学原语，在 Mantle 生态内重建一套 native privacy layer，这样的好处在于架构上不会割裂，比如 Besu 的使用在 Mantle 上是非常不自然的，问题则是开发和运营的成本问题

## Appendix \- Q\&amp;A

### Q1 \- Besu 是否是必须的，是否可以替换成别的客户端

想要回答这个问题，我们需要先确定 Besu 在 Paladin 中的作用域，Besu 在 Paladin 整个系统中在 Layer A 和 Layer C 中分别扮演不同的角色。

- Layer A 中的 Besu

    - Layer A 中 Besu 是一个作为结算平台的存在，Paladin 通过标准 JSON\-RPC 连接它。研究确认 Paladin 使用的 17 个 RPC 方法全部是标准 EVM 方法（`eth\_sendRawTransaction`、`eth\_getBlockReceipts`、`eth\_subscribe\(\&\#34;newHeads\&\#34;\)` 等），没有任何 Besu 专有 API 依赖。**因此 Layer A 的 Besu 理论上可以被替换**

- Layer C 中的 Besu

    - Layer C 中 Besu 作为 EVM 执行引擎，Pente 域使用的不是运行中的 Besu 节点，而是 Besu 的 Java EVM 库，直接在 Paladin 的 JVM 中加载，因此其实 Paladin 的结构非常复杂（Besu EVM（Java 库）→ Pente 域用 Java 写 → 通过 JAR 加载到 JVM → 通过 gRPC 和 Go 核心通信）

    - 那么如果 evm 执行引擎换成别的，比如 geth 或者 revm，理论上也是可以运行的，但是都需要或多或少的适配/重实现。

        - 如果选择 geth

            - 需要重新实现 `PenteDomain`（就像 Noto/Zeto 那样），`evm\_runner`，`paladin\_statedb`的 geth 适配

            - 这样会比 Besu 更加原生，但是需要重新实现比较多的功能，另外还需要解决 geth 中 `vm\.StateDB` 接口和 geth 的内部状态管理（trie、snapshot）有隐含耦合的问题

        - 如果选择 revm

            - 依然使用 go，所以需要重新实现 `PenteDomain`（就像 Noto/Zeto 那样），`evm\_runner`（在里面通过 CGO 调用 revm 的 C\-API），以及需要一个 `revm\_bridge` 来帮助封装 revm 调用

另外我们发现 Besu 和 Paladin 是同属于一个组织（LFDT），所以我们认为这是 Paladin 选择 Besu 的最主要原因，Besu 在技术层面并没有不可替代性。

### Q2 \- Paladin 这个方案有什么缺陷

主要是以下这些方面：

1. 架构方面

    1. Noto 的单一 notary 模式会有单点风险的问题

    2. Pente 的可扩展性问题，Pente 要求隐私组内所有成员独立重新执行交易并签署 EIP\-712 签名，意味着这个隐私组无法大规模扩展；另外 Pente 的隐私组设计类似于老的状态通道，无法动态管理，所以想要变更成员就需要关闭然后重新开启

    3. Go/Java 混合运行时复杂性

    4. UTXO 的状态爆炸问题

2. 安全方面

    1. 使用 Groth16，因此 trusted setup 的问题还是存在的

    2. 依然是因为 Groth16，所以一旦业务场景发生变化，zkp 电路需要重写

3. 生态方面

    1. 如何将 UTXO 做到 evm 账户体系级别的 ux 需要考虑

    2. 目前协议过于早期，很多功能还在等待实现（MPC 多方计算，合规相关的原生设计等）

### Q3 \- 企业的接入方式是什么样的

如果 Mantle 完成其余所有的适配和集成（包括 Paladin Sidecar 与 Mantle 的集成，Paladin Node 与 Mantle 版本的 evm 的集成），那么企业想要在 Mantle 上做结算只需要运行魔改后的 Paladin Node 即可

### Q4 \- Paladin 这个方案和一般的联盟链有什么区别

传统联盟链（如 Hyperledger Fabric、Quorum/GoQuorum、Corda）是完整的区块链平台，包含共识、执行、存储、P2P 等全栈组件，作为一个整体运行。而 Paladin 是一个 Sidecar，它不修改底层 EVM 链的任何代码。

