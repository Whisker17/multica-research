---
topic: "Multiproof Prover 与 Challenger 实现深度解析"
project_slug: base-azul-upgrade
topic_slug: multiproof-provers-challengers
github_repo: Whisker17/multica-research
round: 1
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
  - Proposer 的 parent recovery + checkpoint selection + ProofRequest 构造 + pre-submission canonical
    validation 完整流程，含 BLOCK_INTERVAL 与 INTERMEDIATE_BLOCK_INTERVAL 推导规则
  - Challenger 双路径（permissionless ZK challenge vs Base reference TEE nullification）的
    game category 分类表、validator 算法、pending proof phase machine 与 bond claim lifecycle
  - TEE Prover Nitro Enclave 架构：host vsock proxy、enclave NSM attestation、ECDSA signer 密钥永不离开
    enclave 的安全论证、ProofJournal layout、configHash / teeImageHash 双绑定
  - ZK Prover 服务：SP1 Range program + Aggregation program 的 ELF/imageHash 关系、proof request
    state（CREATED→PENDING→RUNNING→SUCCEEDED/FAILED）、backend 三模式（mock/cluster/network）、
    deterministic session_id 幂等性、Groth16 receipt 与 AggregateVerifier framing
  - Prover Registrar 生命周期：AWS ALB target group discovery、`enclave_signerAttestation` 拉取、
    通过 Boundless Network 生成 attestation ZK proof、TEEProverRegistry on-chain 注册、orphaned
    signer 移除流程及 transient outage 保护机制（grace window / restart-window safeguards）
  - 五个组件在 happy path（TEE-only 7d）、ZK challenge invalid TEE、fraudulent ZK challenge、
    future TEE+ZK fast-finality 路径下的端到端时序交互
  - 安全模型、信任假设与与 OP Stack 旧体系（op-proposer / op-challenger / cannon fault-proof）的对比表
  - 至少 4 张 Mermaid 图（Proposer 序列图 / Challenger 双路径流程图 / TEE Prover Nitro 架构图 /
    Prover Registrar 生命周期状态机），每张含 base/base codebase 文件路径与行号引用
  - Gap Analysis：spec stub 页面（tee-provers.md / registrar.md）尚未落地的字段、Boundless Network /
    Automata SDK 公共文档可达性、生产部署参数（ALB ARN、TEEProverRegistry 链上地址）等

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-17T12:15:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-17T12:15:00Z"
---

# Research Outline: Multiproof Prover 与 Challenger 实现深度解析

## Items

### item-1: Proposer 服务架构与 checkpoint 选择流程

代码级解析 `crates/proof/proposer`（`service.rs` / `driver.rs` / `pipeline.rs` /
`output_proposer.rs`）：service 顶层启动如何拼装 L1/L2/Rollup/Prover RPC 客户端、
`DisputeGameFactory` 与 `AnchorStateRegistry` clients、`L1TransactionManager`、admin JSON-RPC
服务器；driver tick 循环如何串联 `recover_latest_state()` → checkpoint selection → ProofRequest →
pre-submission canonical validation → `createWithInitData()`；MAX_FACTORY_SCAN_LOOKBACK
（默认 5000）回溯机制、`BLOCK_INTERVAL` 必须 ≥ 2 / `INTERMEDIATE_BLOCK_INTERVAL` 非零 /
两者整除约束的运行时校验；deterministic forward walk from anchor 的 factory key 唯一性论证。
还需要解释 finalized_l2 vs safe_l2 head 切换、parallel proving 时 L1 submission 仍然严格串行
的保证、`GameAlreadyExists` 被吸收为成功路径、3 次 proof 重试 + 10 分钟提交超时上限。

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

### item-7: Prover Registrar 生命周期与 transient outage 保护机制

代码级解析 `crates/proof/tee/registrar`：
- `discovery.rs`：通过 AWS ALB target group 周期性拉取健康 enclave 实例列表
  （`InstanceDiscovery` trait）；
- `prover.rs`：`ProverClient` 调用 `enclave_signerAttestation` 拉取 Nitro attestation document
  与 signer 公钥；
- `verifier.rs` / `crl.rs`：AWS Nitro Root CA 校验、PCRs 比对、Nitro CRL（Certificate Revocation
  List）检查；
- `driver.rs`：核心循环 —— 新实例进入 → attestation ZK proof via Boundless Network / Automata SDK
  → on-chain `TEEProverRegistry.registerSigner(...)`；正在线 signer 保持心跳追踪；
  消失的 signer 进入 orphaned grace window，超时后调用 on-chain remove；
- `registry.rs`：链上 `TEEProverRegistry` 客户端封装；
- 保护机制：grace window + multi-poll confirm 防止网络瞬断误删；restart 后从链上 + ALB 重建
  signer set；`SigningConfig` L1 signer 与 `BoundlessConfig` ZK 证明 endpoint 分离；
- `metrics.rs` 暴露 Prometheus 指标用于人工监控。

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
| spec_reference | Base 官方 spec 中对应 section 的相对路径与 heading（`docs/specs/pages/protocol/proofs/*.md`、`docs/specs/pages/upgrades/azul/proofs.md`），并明确该 spec 是否为 stub | all |
| code_reference | base/base 仓库中的 Rust crate / 模块 / 文件路径加行号区间（commit `84155fef0`），off-chain Rust 实现优先；如果引用了 contracts，写明 `base/contracts @ commit` 行号 | all |
| inputs_outputs | 组件的 RPC / gRPC / trait 接口入参出参类型、链上方法签名、协议字段表 | all |
| state_machine_or_lifecycle | 组件内部的状态机或生命周期描述（driver tick、phase machine、bond claim lifecycle、proof request state） | item-1, item-3, item-4, item-6, item-7 |
| security_properties | 不变量、信任假设、密钥/签名/attestation 的隔离边界、攻陷条件下的失败模式 | all |
| failure_modes_and_retries | 可重试 vs 永久失败的分类、retry 上限、idempotent 机制（deterministic session_id、`GameAlreadyExists` 处理） | all |
| comparison_to_op_stack | 与 ethereum-optimism/optimism 中等价组件（op-proposer / op-challenger / op-program / op-node）的差异说明，含 commit/路径引用 | item-1, item-3, item-5, item-8 |
| open_gaps_or_caveats | 公共信息缺失项：spec stub 未落地段、私有部署参数（ALB ARN / on-chain registry 地址 / 实际生产 image hash）、Boundless Network 内部细节 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | sequence | Proposer driver tick 序列图：recover_latest_state → checkpoint select → prover_prove → pre-submission canonical validation → DisputeGameFactory.createWithInitData，包含失败分支（GameAlreadyExists、canonical mismatch、invalid TEE signer） | mermaid | item-1, item-2 |
| diag-2 | flow | Challenger 双路径 dispute 决策流程图：scanner 分类 → validator → TEE-first nullification vs ZK fallback → nullify() vs challenge() → pending phase machine | mermaid | item-3, item-4 |
| diag-3 | architecture | TEE Prover Nitro Enclave 系统架构图：Host（vsock proxy、RPC fanout、Backend）↔ Enclave（vsock server、Runtime、NSM、ECDSA signer、Oracle）↔ AggregateVerifier on L1；标注信任边界、attestation 数据流、签名密钥永不离开 enclave | mermaid | item-5 |
| diag-4 | state | Prover Registrar 生命周期状态机：Discovered → AttestationFetched → ZKProofGenerated → Registered → ActiveTracked → Orphaned(GracePeriod) → Removed，含 transient outage 回退到 ActiveTracked 的分支 | mermaid | item-7 |
| diag-5 | sequence | 端到端多场景时序图：happy TEE-only、ZK challenge invalid TEE、fraudulent ZK challenge、future dual-proof fast finality | mermaid | item-8 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | Base 官方 spec：`docs/specs/pages/upgrades/azul/proofs.md`、`docs/specs/pages/protocol/proofs/{proposer,challenger,zk-prover,tee-provers,registrar,contracts,index}.md` | 4 |
| src-2 | code_analysis | base/base 仓库 off-chain Rust crates：`crates/proof/proposer/src/*`、`crates/proof/challenge/src/*`、`crates/proof/tee/{nitro-enclave,nitro-host,registrar}/src/*`、`crates/proof/zk/service/src/*`、`crates/proof/succinct/elf/manifest.toml`，引用须给文件路径 + 行号 + commit SHA | 8 |
| src-3 | official_docs | AWS Nitro Enclaves 官方文档：Nitro Security Module (NSM) API、attestation document 结构、vsock 通信限制、PCRs 与 image hash 计算 | 2 |
| src-4 | official_docs | SP1 / Succinct Labs 官方文档：SP1 range program 接口、Groth16 aggregation、`sp1_lib::verify::verify_sp1_proof`、ELF 工具链与 vkey 派生 | 2 |
| src-5 | code_analysis | ethereum-optimism/optimism 上游对比：`op-proposer`、`op-challenger`、`op-program` 旧版实现，commit/路径明确 | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
