---
topic: "Multiproof Prover 与 Challenger 实现深度解析"
project_slug: base-azul-upgrade
topic_slug: multiproof-provers-challengers
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: base-azul-upgrade/outlines/multiproof-provers-challengers.md
  draft: base-azul-upgrade/research-sections/multiproof-provers-challengers/drafts/round-{n}.md
  final: base-azul-upgrade/research-sections/multiproof-provers-challengers/final.md
  index: base-azul-upgrade/research-sections/_index.md

scope: |
  深入分析 Base Azul Multiproof 系统的 off-chain 实现层：Proposer、Challenger、TEE Prover
  （AWS Nitro Enclave 主机/飞地分离的 host + enclave 服务）、ZK Prover（SP1 range +
  Groth16 aggregation 证明服务）以及 Prover Registrar（自动发现 + on-chain TEEProverRegistry
  注册）的代码级实现、生命周期、协议、状态机、retry 与 safety 不变量。链上合约层（AggregateVerifier、
  TEEVerifier、ZKVerifier、DelayedWETH、OptimismPortal2、AnchorStateRegistry）由 multiproof-architecture
  子课题承接，本子课题仅在描述 off-chain 与 on-chain 交互边界时进行最小引用，不重复推导合约状态机。
  执行层 EIP（Osaka）由 osaka-evm-changes 承接。
audience: |
  Multica 研究 squad 内部下游 Adversarial Agent 与 Technical Writer、关注 L2 Stage 2 与
  Rollup 多证明系统运维落地的协议/基础设施工程师、TEE 安全研究者、ZK 工程团队、Sequencer/Proposer
  运营方。读者熟悉 OP Stack op-proposer / op-challenger / op-program 的旧体系，但不一定了解
  Base 在 Azul 引入的 TEE host+enclave 拆分、Boundless Network attestation ZK 化和 SP1 双段
  （compressed + Groth16 aggregation）证明流程。
expected_output: |
  - Proposer / Challenger / TEE Prover / ZK Prover / Prover Registrar 五个 off-chain 组件的代码级
    实现文档，包含模块清单、入口 trait、driver tick 循环结构
  - Proposer 的 parent recovery（`recover_latest_state()` cache + `game_count` + UUID deterministic
    forward walk）+ checkpoint selection + ProofRequest 构造 + pre-submission canonical validation
    完整流程，含 `BLOCK_INTERVAL` 与 `INTERMEDIATE_BLOCK_INTERVAL` 推导规则；显式标注仓库 README 中
    `MAX_FACTORY_SCAN_LOOKBACK` / backward-scan 文字为 stale，需以 Rust 源码为准
  - Challenger 双路径（permissionless ZK challenge vs Base reference TEE nullification）的
    game category 分类表、validator 算法、pending proof phase machine 与 bond claim lifecycle
  - TEE Prover Nitro Enclave 架构：host vsock proxy、enclave NSM attestation、ECDSA signer 密钥永不离开
    enclave 的安全论证、ProofJournal layout、configHash / teeImageHash 双绑定
  - ZK Prover 服务：SP1 Range program + Aggregation program 的 ELF/imageHash 关系、proof request
    state（CREATED→PENDING→RUNNING→SUCCEEDED/FAILED）、backend 三模式（mock/cluster/network）、
    deterministic session_id 幂等性、Groth16 receipt 与 AggregateVerifier framing
  - Prover Registrar 生命周期：AWS ALB target group discovery、`enclave_signerAttestation` 拉取、
    通过 Boundless Network 生成 attestation ZK proof、TEEProverRegistry on-chain 注册，以及实际
    orphan 清理机制 —— active-set 构造 + majority-reachability guard + cancellation guard +
    `deregister_orphans()` + `isRegisteredSigner` ghost-entry guard + single-registrar assumption
    （非 grace-window 状态机；如公共仓库 README/历史 spec 中存在 grace-window 文字，须显式标注为 stale）
  - 五个组件在 happy path（TEE-only 7d）、ZK challenge invalid TEE、fraudulent ZK challenge、
    future TEE+ZK fast-finality 路径下的端到端时序交互
  - 安全模型、信任假设与与 OP Stack 旧体系（op-proposer / op-challenger / cannon fault-proof）的对比表
  - 至少 4 张 Mermaid 图（Proposer 序列图 / Challenger 双路径流程图 / TEE Prover Nitro 架构图 /
    Prover Registrar 决策流程图），每张含 base/base codebase 文件路径与行号引用
  - Gap Analysis：spec stub 页面（tee-provers.md / registrar.md）尚未落地的字段、Boundless Network /
    RISC Zero / Automata SDK 公共文档可达性、生产部署参数（ALB ARN、TEEProverRegistry 链上地址）等

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-17T12:15:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-17T12:40:00Z"
---

# Research Outline: Multiproof Prover 与 Challenger 实现深度解析

## Items

### item-1: Proposer 服务架构与 parent recovery / checkpoint 选择流程

代码级解析 `crates/proof/proposer`（`service.rs` / `driver.rs` / `pipeline.rs` /
`output_proposer.rs`）：service 顶层启动如何拼装 L1/L2/Rollup/Prover RPC 客户端、
`DisputeGameFactory` 与 `AnchorStateRegistry` clients、`L1TransactionManager`、admin JSON-RPC
服务器；driver tick 循环如何串联 `recover_latest_state()` → checkpoint selection → ProofRequest →
pre-submission canonical validation → `createWithInitData()`。

Parent recovery 必须严格按 base/base @ `84155fef0` 的实际实现 `recover_latest_state()`
（`crates/proof/proposer/src/pipeline.rs` L731-L838）讲解，**不要**使用 README / spec 中
仍存在的 `MAX_FACTORY_SCAN_LOOKBACK` / "backward scan" 文字（该文字为 stale，仓库当前
没有该常量）：

- `game_count` 与 `anchor_snapshot` 同一 L1 快照读取，保证 anchor root 不会与更晚的 anchor
  game 错配；
- cache（`CachedRecovery { game_count, state }`）fast path：当 `game_count` 未变化且 anchor
  仍在 cached tip 之前时直接复用，零额外 RPC；
- 否则执行 deterministic forward walk（`forward_walk`，L865 起），起点二选一：cached tip
  （增量）或 anchor state（冷启动 / anchor 超过 cached tip / `game_count` 回退）；
- 每一步：用 `block_interval` 推导 `expected_block` → 一次批量 `fetch_canonical_roots` →
  以 `(block_number, parent_address, intermediate_roots)` 紧凑编码 `extraData` →
  `factory.games(gameType, rootClaim, extraData)` 查询 UUID；返回 `Address::ZERO` 即
  gap，停止；否则把返回 proxy 作为新的 parent；
- 关键安全论证：deterministic forward walk 因 UUID 由 canonical 数据派生，不需要任何后向
  扫描或"unrelated games"过滤；无效游戏自动获得不同 UUID 从不被命中；walk 不受 safe/finalized
  L2 head 上限约束，因为它只读取已上链的游戏。

此外需要解释：`BLOCK_INTERVAL` 必须 ≥ 2 / `INTERMEDIATE_BLOCK_INTERVAL` 非零 / 两者整除约束的
运行时校验；finalized_l2 vs safe_l2 head 切换；parallel proving 时 L1 submission 仍然严格串行
的保证；`GameAlreadyExists` 被吸收为成功路径；3 次 proof 重试 + 10 分钟提交超时上限。Draft
中所有引用 README / spec 的 backward-scan 段落必须显式标注 `(stale; superseded by
recover_latest_state() in pipeline.rs)`。

- **Priority**: high
- **Dependencies**: none

### item-2: Proposer 的 ProofRequest 构造、TEE Journal 解析与 pre-submission canonical 验证

聚焦 Proposer 与 Prover 接口边界、proposal 提交前的"无信任化"再校验：`ProofRequest` 九个字段
（`l1_head` / `l1_head_number` / `agreed_l2_head_hash` / `agreed_l2_output_root` /
`claimed_l2_output_root` / `claimed_l2_block_number` / `proposer` / `intermediate_block_interval`
/ `image_hash`）；`prover_prove(ProofRequest) -> ProofResult` 的 RPC 契约；aggregate proposal
中的 journal layout（`proposer(20) || l1OriginHash(32) || prevOutputRoot(32) ||
startingL2Block(8) || outputRoot(32) || endingL2Block(8) || intermediateRoots(32*N) ||
configHash(32) || teeImageHash(32)`）以及 `keccak256(journal)` 的 ECDSA 签名；submission 之前
对 rollup output root 与每个 intermediate root 的 canonical-root 比对；可选的
`TEEProverRegistry.isValidSigner(signer)` 预校验语义（RPC 失败时降级到链上强制约束）；signature
v 值归一化（27/28）；`extraData = l2BlockNumber(32) || parentAddress(20) || intermediateRoots(32*N)`
的紧凑编码。说明这套机制如何使 proposer 行为"自检"，并解释 dry-run 模式只跑 validation 不上链。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Challenger 扫描、game 分类与双路径 dispute 提交

代码级解析 `crates/proof/challenge`：scanner 从 `AnchorStateRegistry.anchorGame()` 起始向后扫描所有
post-anchor `IN_PROGRESS` 游戏；按 `(teeProver, zkProver, counteredByIntermediateRootIndexPlusOne)`
三元组分类为四种 GameCategory（`InvalidTeeProposal` / `FraudulentZkChallenge` /
`InvalidZkProposal` / `InvalidDualProposal`，加上"both zero → fully nullified, skip"与
"single-prover with non-zero countered → unexpected, skip"两种异常态）；validator 从 L2 RPC 取
header → 校验 RPC-provided hash 与 consensus hash 一致 → `eth_getProof` 获取
`L2ToL1MessagePasser` 账户证明 → MPT 校验 → 重组 OutputRoot 并与链上 root 比较；fraudulent ZK
challenge 验证只针对被挑战的 checkpoint index；nullify vs challenge 的语义差异
（`nullify(proofBytes, intermediateRootIndex, intermediateRootToProve)` 用于 TEE/ZK 任一证据失效，
`challenge(...)` 用于 ZK 反驳 TEE）；TEE-first nullification 路径与 ZK fallback 切换；safety
invariant（不信任 game 自报根、使用 game.l1Head 请求 dispute proof、submit 前重新检查 game
status）。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Challenger pending proof phase machine 与 bond claim lifecycle

详解 `crates/proof/challenge/src/pending.rs` 与 `bond.rs`：pending proof 状态机（`AwaitingProof` →
`ReadyToSubmit` | `NeedsRetry` → `Dropped`）；ZK proof 轮询 polling 模式、ZK 失败 ≤ 3 次重试；
TEE proof 提交失败立即切换到 ZK fallback；submit 前的 game-state 再校验（gameOver / 槽位已被
零化 / 已有对手挑战）防止重复提交；bond claim 四阶段
（`NeedsResolve` → `NeedsUnlock` → `AwaitingDelay` → `NeedsWithdraw`）与 `DelayedWETH` 1 天
delay 的交互；`AnchorStateRegistry.setAnchorState(game)` permissionless best-effort 推进；
restart 后通过 `bondRecipient()` 与 `zkProver()` 槽位恢复可索取 game。

- **Priority**: high
- **Dependencies**: item-3

### item-5: TEE Prover Nitro Enclave 架构（host / enclave 拆分与签名密钥永不离开 enclave 的安全论证）

代码级解析 TEE Prover 实现：
- `crates/proof/tee/nitro-host`：`NitroProverServer` 暴露 `prover_*` 与 `enclave_*` JSON-RPC、
  `NitroBackend` 实现 `ProverBackend` trait 并分派到 `NitroTransport`（生产 vsock，开发 in-process）、
  `vsock.rs` 的 frame 协议与超时控制、`registration.rs` 处理 `enclave_signerAttestation` 的代理；
- `crates/proof/tee/nitro-enclave`：`server.rs` vsock listener、`runtime.rs` proof client 流水线、
  `crypto.rs` ECDSA signer（k256）密钥在 enclave 内部 NSM 派生且永不离开、`nsm.rs` 调用
  AWS NSM hypervisor 接口生成 attestation document、`oracle.rs` 验证 host 提交的 preimage、
  `protocol.rs` 定义 vsock 帧消息；
- ProofJournal layout 与 configHash / teeImageHash 双绑定，使 enclave 签名同时绑定到
  软件版本 + Rollup 配置；
- AWS Nitro Enclave 的隔离模型（无持久存储、无外部网络、唯一 vsock 通道、PCRs 测量、签名密钥
  从 NSM 随机源派生）；
- 与 OP Stack 单进程 `op-proposer` 的对比：host/enclave 拆分把 witness 收集与 re-execution + 签名
  分离，攻陷 host 不能伪造 root 签名。

- **Priority**: high
- **Dependencies**: item-2

### item-6: ZK Prover 服务（SP1 range + Groth16 aggregation 双段证明流水线）

代码级解析 `crates/proof/zk/service` 与 `crates/proof/zk/client`：
- gRPC 接口 `ProveBlock` / `GetProof`、`ProveBlockRequest` 七个字段（含 `proof_type` 二选一、
  `session_id` 幂等性、`l1_head` 与 `prover_address` 绑定语义）；
- 证明请求生命周期（`CREATED` → `PENDING` → `RUNNING` → `SUCCEEDED` / `FAILED`）与 backend
  sessions 独立子状态（`RUNNING` / `COMPLETED` / `FAILED`）；
- 三种 backend 模式（`mock` / `cluster` / `network`）、`outbox` + `worker` + `status poller` 结构、
  Postgres 持久化跨进程重启；
- SP1 Range Program（committed `BootInfoStruct`：`l2PreRoot` / `l2PreBlockNumber` / `l2PostRoot` /
  `l2BlockNumber` / `l1Head` / `rollupConfigHash` / `intermediateRoots`）与 Aggregation Program
  （AggregationInputs、L1 header chain 验证、`sp1_lib::verify::verify_sp1_proof` 内嵌验证）的
  分工；
- `imageHash = ZK_RANGE_HASH` 与 `aggregation vkey = ZK_AGGREGATE_HASH` 的链上参数对齐；
- `RECEIPT_TYPE_STARK` / `RECEIPT_TYPE_SNARK` / `RECEIPT_TYPE_ON_CHAIN_SNARK` 的应用差异；
- proof bytes 在被提交到 `AggregateVerifier` 前由 caller 加 proof-type 前缀；
- ELF reproducibility（`crates/proof/succinct/elf/manifest.toml` 钉死 SHA-256）。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

### item-7: Prover Registrar 生命周期与 orphan 清理 / 安全保护机制

代码级解析 `crates/proof/tee/registrar`，**严格以 base/base @ `84155fef0` 的实际实现为准**，
不沿用 README / 历史 spec 中的 "orphaned grace window / multi-poll confirm" 文字。Driver 的
`step()` 循环（`crates/proof/tee/registrar/src/driver.rs` L203-L325）按以下顺序执行：

1. **Discovery**：`InstanceDiscovery::discover_instances()`（`discovery.rs`，AWS ALB target group
   周期性拉取健康 enclave 实例列表）；`should_register()` 用于过滤 healthy 实例做注册。
2. **Signer resolution / attestation**：并发对**所有可达实例**（不论 health 状态）调用
   `prover.rs::ProverClient` 拉取 `enclave_signerAttestation`，得到 Nitro attestation document
   与 signer 公钥。`verifier.rs` / `crl.rs` 完成 AWS Nitro Root CA 校验、PCRs 比对、Nitro CRL
   检查。draining 但仍可达的实例因此进入 `active_signers`，避免被误清理。
3. **Active-set construction**：把成功解析到的 signer 地址塞入 `active_signers: HashSet<Address>`；
   `reachable_instances` 计数器统计成功的实例数。失败实例仅记 warning + metrics，不进 active set。
4. **Cancellation guard**：在并发处理段使用 `tokio::select!` 监听 `CancellationToken`；一旦
   cancel，立即丢弃 in-flight futures 并 `return Ok(())`，**不会**进入后续清理路径，避免在
   active set 不完整的情况下误删 on-chain signer。
5. **Majority-reachability guard**：要求严格多数（`reachable_instances * 2 > instances.len()`）
   discovered 实例可达才允许清理；若不满足直接 `return`。该判定以 instance 为单位（不是
   signer），避免多 enclave 实例膨胀比例。
6. **Zero-discovery edge case**：当 `instances.is_empty()`（ASG scale-down 后 target group 已
   清空）时绕过 majority guard，正常进入 orphan 清理路径——下线的实例已离开 target group，不会
   抬高 `instances.len()`。
7. **`deregister_orphans()`**（L862-L926 区段）：以 `registry.get_registered_signers()` 拿到当前
   链上注册集合；不在 `active_signers` 内的视为 orphan；对每个 orphan **先调用
   `registry.is_registered(addr)`**（背后是 `isRegisteredSigner` mapping）以避开 Solady v0.0.245
   `EnumerableSetLib.AddressSet` 的 ghost-entry bug——`getRegisteredSigners()` 可能返回的"幽灵"
   地址其 `isRegisteredSigner == false`，跳过后才提交 deregister tx，避免无限循环 burn gas。
8. **Single-registrar assumption**（注释 L876-L882）：`deregister_orphans` 把链上所有 signer 视
   为本 registrar 管辖。若多个 registrar 同时连接同一 registry，会互相误删；当前部署模型假设
   每个 registry 合约只有一个 registrar 实例。

此外：
- 注册路径：未注册且 `should_register()` 通过的实例会触发 `try_register`，先经 Boundless
  Network / Automata SDK 生成 attestation ZK proof，再提交 `TEEProverRegistry.registerSigner(...)`；
  `unhealthy_registration_window` 允许新启动但 ALB health 尚未通过的实例在窗口内尝试注册；
- restart 后 active set 完全从 ALB + on-chain registry 重建，无本地持久状态；
- `SigningConfig` L1 signer 与 `BoundlessConfig` ZK 证明 endpoint 分离；
- `metrics.rs` 暴露 `RegistrarMetrics::{discovery_success_total, processing_errors_total, ...}`
  Prometheus 指标，用于在 majority-guard / cancellation-guard 阻止清理时做人工监控。

draft 中所有引用 README / 历史 spec 中 "orphaned grace window / multi-poll confirm" 段落必须
显式标注 `(stale; superseded by active-set + majority-reachability guard in driver.rs)`，并
按本 item 描述更新。

- **Priority**: high
- **Dependencies**: item-2, item-5

### item-8: 端到端组件协同 + 与 OP Stack 旧体系对比 + 未来 TEE+ZK 一并提交方向

整合前 7 项，把 Proposer / Challenger / TEE Prover / ZK Prover / Prover Registrar 在四种典型
场景下的端到端交互画清楚：
1. Happy path（TEE-only proposal → 7 天 long window 内无挑战 → 自然 finalize）；
2. ZK challenge invalid TEE（challenger 发现非法 TEE proof → 请求 ZK proof → `challenge()` →
   AggregateVerifier 切换路径）；
3. Fraudulent ZK challenge（challenger 校验被挑战 checkpoint 实为有效 → `nullify()` 反作弊）；
4. Future TEE+ZK 双证 fast finality（proposer 直接同时附带两类 proof → 1 天短窗，需要 proposer
   集成 ZK，目前尚未上线）。
此外整理与 OP Stack 旧体系的对比矩阵（op-proposer 单进程 vs Base proposer + TEE host/enclave
拆分；op-challenger 7 天交互式 fault-proof vs Base challenger 双路径 dispute；cannon vs SP1
range+aggregation；trusted setup / 信任假设变化），并给出 Stage 2 视角下的安全级别评估与
未来演进路径（multi-ZK、更强 TEE、proposer 内嵌 ZK 等）。

- **Priority**: medium
- **Dependencies**: item-1, item-3, item-5, item-6, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| spec_reference | Base 官方 spec 中对应 section 的相对路径与 heading（`docs/specs/pages/protocol/proofs/*.md`、`docs/specs/pages/upgrades/azul/proofs.md`），并明确该 spec 是否为 stub；任何与 Rust 源码不一致的段落必须显式标注 stale | all |
| code_reference | base/base 仓库中的 Rust crate / 模块 / 文件路径加行号区间（commit `84155fef0`），off-chain Rust 实现优先；如果引用了 contracts，写明 `base/contracts @ commit` 行号 | all |
| inputs_outputs | 组件的 RPC / gRPC / trait 接口入参出参类型、链上方法签名、协议字段表 | all |
| state_machine_or_lifecycle | 组件内部的状态机或生命周期描述（driver tick、phase machine、bond claim lifecycle、proof request state、registrar step() 决策流程） | item-1, item-3, item-4, item-6, item-7 |
| security_properties | 不变量、信任假设、密钥/签名/attestation 的隔离边界、攻陷条件下的失败模式（如 registrar 的 cancellation/majority/ghost-entry/single-registrar guards） | all |
| failure_modes_and_retries | 可重试 vs 永久失败的分类、retry 上限、idempotent 机制（deterministic session_id、`GameAlreadyExists` 处理、majority-reachability guard 跳过清理） | all |
| comparison_to_op_stack | 与 ethereum-optimism/optimism 中等价组件（op-proposer / op-challenger / op-program / op-node）的差异说明，含 commit/路径引用 | item-1, item-3, item-5, item-8 |
| open_gaps_or_caveats | 公共信息缺失项：spec stub 未落地段、私有部署参数（ALB ARN / on-chain registry 地址 / 实际生产 image hash）、Boundless Network / RISC Zero / Automata SDK 内部细节 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | sequence | Proposer driver tick 序列图：`recover_latest_state()`（game_count + anchor_snapshot → cache fast path / forward walk via factory.games() UUID lookup）→ checkpoint select → prover_prove → pre-submission canonical validation → DisputeGameFactory.createWithInitData，包含失败分支（GameAlreadyExists、canonical mismatch、invalid TEE signer、forward walk gap） | mermaid | item-1, item-2 |
| diag-2 | flow | Challenger 双路径 dispute 决策流程图：scanner 分类 → validator → TEE-first nullification vs ZK fallback → nullify() vs challenge() → pending phase machine | mermaid | item-3, item-4 |
| diag-3 | architecture | TEE Prover Nitro Enclave 系统架构图：Host（vsock proxy、RPC fanout、Backend）↔ Enclave（vsock server、Runtime、NSM、ECDSA signer、Oracle）↔ AggregateVerifier on L1；标注信任边界、attestation 数据流、签名密钥永不离开 enclave | mermaid | item-5 |
| diag-4 | flow | Prover Registrar `step()` 决策流程图（不再是线性 grace-period 状态机）：discovery → 并发 signer resolution / attestation 验证 → registration eligibility（`should_register` + Boundless attestation proof + on-chain `registerSigner`）→ active-set 构造 → cancellation guard（已 cancel → 跳过清理）→ majority-reachability guard（reachable*2 ≤ total 且非零 → 跳过清理）→ zero-discovery 旁路 → `deregister_orphans()`（含 `isRegisteredSigner` ghost-entry guard + single-registrar 假设）。每个判定节点写明 driver.rs 行号 | mermaid | item-7 |
| diag-5 | sequence | 端到端多场景时序图：happy TEE-only、ZK challenge invalid TEE、fraudulent ZK challenge、future dual-proof fast finality | mermaid | item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | Base 官方 spec：`docs/specs/pages/upgrades/azul/proofs.md`、`docs/specs/pages/protocol/proofs/{proposer,challenger,zk-prover,tee-provers,registrar,contracts,index}.md` | 4 |
| src-2 | code_analysis | base/base 仓库 off-chain Rust crates：`crates/proof/proposer/src/*`、`crates/proof/challenge/src/*`、`crates/proof/tee/{nitro-enclave,nitro-host,registrar}/src/*`、`crates/proof/zk/service/src/*`、`crates/proof/succinct/elf/manifest.toml`，引用须给文件路径 + 行号 + commit SHA。**Proposer parent recovery 必须引用 `crates/proof/proposer/src/pipeline.rs` L731-L838（`recover_latest_state` + `forward_walk`）。Registrar orphan 清理必须引用 `crates/proof/tee/registrar/src/driver.rs` L203-L325（`step()`）与 L862-L926 区段（`deregister_orphans()`）** | 8 |
| src-3 | official_docs | AWS Nitro Enclaves 官方文档：Nitro Security Module (NSM) API、attestation document 结构、vsock 通信限制、PCRs 与 image hash 计算 | 2 |
| src-4 | official_docs | SP1 / Succinct Labs 官方文档：SP1 range program 接口、Groth16 aggregation、`sp1_lib::verify::verify_sp1_proof`、ELF 工具链与 vkey 派生 | 2 |
| src-5 | code_analysis | ethereum-optimism/optimism 上游对比：`op-proposer`、`op-challenger`、`op-program` 旧版实现，commit/路径明确 | 2 |
| src-6 | official_docs | Registrar attestation 证明栈：RISC Zero zkVM、Boundless Network proof market、Automata DCAP attestation SDK 三个项目的公开文档/规范（用于解释 attestation ZK proof 生成流程）。若任一项目缺乏公开材料，须在 `open_gaps_or_caveats` 字段明确标注 caveat，并禁止编造细节 | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-1 | 移除已过时的 `MAX_FACTORY_SCAN_LOOKBACK` / backward-scan 描述，替换为代码实际的 `recover_latest_state()` cache + `game_count` + UUID deterministic forward walk（`crates/proof/proposer/src/pipeline.rs` L731-L838）；要求 draft 显式标注 README/spec 中的 backward-scan 文字为 stale | review verdict 58004088-7a64-4d57-b664-faed495db3cb (round 1, major) |
| 2 | modify_item | item-7 | 移除虚构的 "orphaned grace window / multi-poll confirm" 描述，替换为 driver.rs 实际的 active-set 构造 + cancellation guard + majority-reachability guard + zero-discovery 旁路 + `deregister_orphans()` + `isRegisteredSigner` ghost-entry guard + single-registrar 假设（`crates/proof/tee/registrar/src/driver.rs` L203-L325, L862-L926） | review verdict 58004088-7a64-4d57-b664-faed495db3cb (round 1, major) |
| 2 | modify_diagram | diag-4 | 把 Registrar 图从线性 grace-period 状态机改为 `step()` 决策流程：discovery → signer resolution/attestation → registration eligibility → active-set 构造 → cancellation guard → majority guard → zero-discovery 旁路 → `deregister_orphans()` | review verdict 58004088-7a64-4d57-b664-faed495db3cb (round 1, minor) |
| 2 | add_source_req | src-6 | 新增 RISC Zero / Boundless Network / Automata SDK 公开文档为 attestation 证明栈的 source requirement，缺失时必须以 caveat 显式标注，禁止编造 | review verdict 58004088-7a64-4d57-b664-faed495db3cb (round 1, minor) |
