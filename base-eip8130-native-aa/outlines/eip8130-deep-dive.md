---
topic: "EIP-8130 原理与 Base 实现深度分析"
project_slug: "base-eip8130-native-aa"
topic_slug: "eip8130-deep-dive"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "base-eip8130-native-aa/outlines/eip8130-deep-dive.md"
  draft: "base-eip8130-native-aa/research-sections/eip8130-deep-dive/drafts/round-{n}.md"
  final: "base-eip8130-native-aa/research-sections/eip8130-deep-dive/final.md"
  index: "base-eip8130-native-aa/research-sections/_index.md"

scope: "按 WHI-276 Step 0~Step 6：锁定 Base 代码基线；拆解 TxEip8130/Eip8130Signed 字段语义；AccountConfiguration owner/Scope 位掩码与 account_changes 写语义；EOA vs 配置账户双路径、ERC-1271、与 EIP-7702 组合关系、2D nonce/nonce-free；payer/批量/原子分阶段；PR 时间线与设计动机；按 WHI-275 rubric D1~D13 打分。"
audience: "Mantle dev teams、协议工程师、AA 基础设施工程师、Research Review Agent。读者熟悉 EVM/L2 与 ERC-4337/EIP-7702 基础概念，需要源码锚定的 EIP-8130 技术解读，并作为后续横向对比与 Mantle 是否实现 native AA 的输入。"
expected_output: "结构化 deep-dive section：包含 Base 代码基线、交易结构图、账户配置/Scope 写语义表、账户变更语义表、验证/执行管线图、PR 时间线、spec-Draft/TBD 与 Base 实现差异表、WHI-275 D1~D13 rubric 打分框架，最终产出 base-eip8130-native-aa/research-sections/eip8130-deep-dive/drafts/round-1.md 与 final.md。"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-26T16:20:21Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-26T16:20:21Z"

multica_issue_id: "80d86900-2587-4726-a6af-c102dc5febab"
report_issue_id: "fc840c0d-ac87-41c8-b1ae-6d1318b8eaba"
branch_name: "research/base-eip8130-native-aa/eip8130-deep-dive"
base_commit: "aa0d69ba0d85a4ade25cf562f064eef98b64039c"
language: "中文"
research_depth: "deep"
codebase_baseline:
  path: "/Users/whisker/Work/src/networks/base/base"
  commit: "01e732cdbae0c624d652da9e608d7d3fe0f9c74b"
  commit_date: "Thu Jun 18 15:21:24 2026 -0500"
  workspace_status: "dirty: untracked .mcp.json"
  verified_at: "2026-06-27"
---

# Research Outline: EIP-8130 原理与 Base 实现深度分析

## Baseline And Review Contract

本 outline 的 deep draft 必须以 Base 本地 checkout 基线为第一手源码锚点：`/Users/whisker/Work/src/networks/base/base`，commit `01e732cdbae0c624d652da9e608d7d3fe0f9c74b`，commit 日期 `Thu Jun 18 15:21:24 2026 -0500`，核验日期 `2026-06-27`。工作区不是完全 clean：`status --short` 显示 `?? .mcp.json`；后续 draft 必须在文首标注该 dirty 状态，且不要把未跟踪文件当作源码结论来源。

本地 checkout 已含 EIP-8130 类型基础文件：`crates/common/consensus/src/transaction/eip8130/{constants,tx,signed,account_changes,call,mod}.rs`。该 checkout 当前仍落后于 Base `main` 上 2026-06-22 至 2026-06-26 的多项 EIP-8130 PR；deep draft 引用这些后续 PR 时，必须标注取证方式为 PR diff / GitHub PR / fetched remote branch，并写明「未在本地 checkout 基线验证」或「已在本地 fetch 的远端分支验证」。除非 Orchestrator 明确要求，不更新 `/Users/whisker/Work/src/networks/base/base` 的工作树。

EIP-8130 规范为 Draft，且 Base 源码中明确将若干数字常量标注为 spec TBD 后的项目选择。deep draft 不得把 Base 选择的 `0x7D`、`0xFA`、`15_000`、nonce-free 10 秒窗口等写成最终 spec 定值；必须分开写「EIP 草案要求 / Base 当前实现 / TBD 风险」。

## Research Questions

1. EIP-8130 的「Account Abstraction by Account Configuration」到底把账户、owner、authenticator/verifier、Scope、payer、nonce 与 calls 放在协议的哪一层？它为什么比 ERC-4337 更 native，又为什么不是只等同于 EIP-7702？
2. Base 本地实现中的 `TxEip8130` 与 `Eip8130Signed` 字段如何映射到 EIP-8130 草案？`sender == None` 的 EOA 路径、`sender == Some` 的配置账户路径、`payer` 自付/代付路径，以及 `sender_auth` / `payer_auth` 的签名域分隔如何工作？
3. AccountConfiguration 的 owner 集、`Scope` 位掩码、Create / ConfigChange / Delegation，以及嵌套的 InitialOwner / OwnerChange 写语义如何组合成账户配置模型？哪些语义来自 spec，哪些是 Base 当前 Rust 数据结构或后续 PR 的实现选择？
4. EIP-8130 如何处理 ERC-1271 `verifySignature()`、与 EIP-7702-style delegation 的组合、2D nonce、nonce-free replay control、payer sponsorship、批量执行、分阶段原子执行、`msg.value == 0` 约定？
5. Base 8130 PR 时间线显示怎样的工程推进路径和设计动机？从类型定义、Cobalt fork gate、precompiles、canonical registry、authorization、nonce/gas/account change application、EVM integration、RPC/receipt 到后续 open fixes 的顺序，说明 Base 为什么重视 8130？
6. 按 WHI-275 的 D1~D13 rubric，EIP-8130 在抽象层级、协议改动、基础设施依赖、密钥模型、gas 代付、批量原子性、nonce、EOA 兼容、签名灵活性、成熟度、安全攻击面、Mantle 适配成本、目标场景适配上应如何打分？哪些分数必须等待 WHI-279/WHI-282 横向比较补全？

## Items

### item-1: Step 0 - Base 代码基线、证据边界与 PR 清单补全

锁定本地 Base checkout 的可复现基线，并建立「本地已验证 / 远端 PR diff 取证 / Daily Intelligence 复用」三档证据边界。deep draft 必须先记录 commit SHA、commit 日期、dirty 状态、核验日期，再判断每个 8130 结论是否来自本地基线还是后续 PR。该 item 还要从 Base PR 搜索和 Daily Intelligence 种子补全 EIP-8130 PR 清单，避免只覆盖最早的类型定义 PR。

种子与已检索到的 Base PR 需要至少覆盖：#2863、#2866、#2868、#2926、#3008、#3119、#3121、#3170、#3311、#3440、#3467、#3534、#3535、#3537、#3540、#3553、#3557、#3585、#3586、#3589、#3595、#3605、#3651、#3653、#3680、#3696、#3698、#3720、#3722、#3723、#3748、#3749、#3752、#3753、#3754、#3755、#3763、#3766、#3775。PR state、merge time、base branch、head branch 与是否进入本地 checkout 都要独立记录。

- **Priority**: high
- **Dependencies**: none

### item-2: Step 1 - `TxEip8130` 交易体字段语义与交易结构图

拆解 `TxEip8130` 的字段顺序、RLP wire encoding 与协议语义，覆盖 `chain_id`、`sender`、`nonce_key`、`nonce_sequence`、`expiry`、fee caps、`gas_limit`、`account_changes`、`calls`、`payer`。本地基线的源码锚点包括 `tx.rs:44-68` 字段定义、`tx.rs:155-167` 编码顺序、`tx.rs:202-225` sender/payer signing hash。必须解释 `sender: None` 选择 EOA recovery path，`sender: Some` 选择配置账户 path；`payer: None` 表示 self-pay，`payer: Some` 表示 sponsored pay。

该 item 要产出交易结构图，展示 `EIP8130_TX_TYPE || rlp([...tx fields..., sender_auth, payer_auth])`，并把 sender signature hash 与 payer signature hash 的 domain separation 单独画出。图中必须标注 Base 当前 tx type `0x7D` 与 payer domain byte `0xFA` 是 Base 项目选择，spec 仍 TBD。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Step 1 - `Eip8130Signed` 信封、auth payload 与静态/时间戳 admission

拆解 `Eip8130Signed` 如何把 unsigned body 与 `sender_auth`、`payer_auth` 组合成 EIP-2718 signed envelope。重点回答：EOA path 的 `sender_auth` 是 65-byte ECDSA over sender hash；配置账户 path 的 `sender_auth` 是 `verifier(20) || verifier_data`；payer path 的 `payer_auth` 是 `verifier(20) || verifier_data` over payer hash with resolved sender；self-pay 时为空。源码锚点包括 `signed.rs:35-53`、`signed.rs:160-180`、`signed.rs:195-229`、`signed.rs:350-373`。

该 item 还要规划 admission 规则拆解：chain id mismatch、tip above fee cap、zero gas/fee cap、nonce-free timestamp window、EOA recovery checked vs unchecked、upper-half `s` 的 EIP-2 处理。deep draft 必须区分「当前本地基线可见的 wrapper-level checks」与后续 PR 中 txpool / EVM admission orchestration 的完整规则。

- **Priority**: high
- **Dependencies**: item-2

### item-4: Step 2 - AccountConfiguration、Scope 位掩码与 account_changes 写语义表

构建账户配置模型：owner 被 `(verifier, owner_id, scope)` 描述，`Scope` 通过位掩码限制 owner 可用于哪些上下文。本地基线 Scope bits 为 `SCOPE_SIGNATURE=0x01`、`SCOPE_SENDER=0x02`、`SCOPE_PAYER=0x04`、`SCOPE_CONFIG=0x08`、`SCOPE_UNRESTRICTED=0x00`；源码锚点包括 `constants.rs:50-63` 与 `account_changes.rs:17-72`。deep draft 必须解释 0 表示 unrestricted 的语义，避免误读为无权限。

写语义表需要覆盖 issue 要求的 5 类数据结构/变更语义：`CreateEntry`、`ConfigChange`、`Delegation`、`InitialOwner`、`OwnerChange`。同时要显式说明 top-level `AccountChange` enum 在本地基线只有三类：Create / ConfigChange / Delegation；`InitialOwner` 是 Create 的初始 owner 列表项，`OwnerChange` 是 ConfigChange 中的 authorize/revoke 操作。源码锚点包括 `account_changes.rs:75-87`、`account_changes.rs:89-183`、`account_changes.rs:185-243`、`account_changes.rs:246-270`。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: Step 3 - 验证语义：EOA path、配置账户 path、ERC-1271、7702 组合关系

拆解 EIP-8130 的验证路径如何从 sender/payer/auth payload 进入 owner/authenticator/verifier 体系：EOA path 通过 ECDSA recovery 得到 sender；配置账户 path 直接指定 sender 并通过 account configuration 的 owner scope 验证 sender/payer/config/signature；ERC-1271 `verifySignature()` 需要与 `SCOPE_SIGNATURE` 对应；payer path 需要 `SCOPE_PAYER`；config change auth 需要 `SCOPE_CONFIG`。该 item 要对照 EIP-8130 草案与 Base PR #3534/#3535/#3540/#3557/#3589 的实现路径取证。

与 EIP-7702 的关系必须写成「组合 / 互补」而不是互斥：本地基线已有 `Delegation` 与 `DELEGATION_INDICATOR_PREFIX=[0xef,0x01,0x00]`，并在 `Delegation` 注释中明确为 EIP-7702-style delegation；源码锚点包括 `constants.rs:65-77` 与 `account_changes.rs:215-243`。deep draft 需要说明 8130 如何利用 delegation 表达代码指向，同时仍由 8130 的账户配置与 auth 语义控制 owner/payer/config。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: Step 3 - 2D nonce、nonce-free 与 replay protection

解释 `nonce_key` + `nonce_sequence` 的 2D nonce 语义，区分普通 nonce-bearing transaction 与 `nonce_key == NONCE_KEY_MAX` 的 nonce-free mode。本地基线中的 `NONCE_KEY_MAX=U256::MAX`，nonce-free 模式不读写 nonce state，而依赖非零 `expiry`；`signed.rs:168-180` 还要求 `nonce_sequence == 0`、`expiry` 在当前时间之后且不超过 `NONCE_FREE_MAX_EXPIRY_WINDOW`。源码锚点包括 `tx.rs:49-55`、`constants.rs:44-48`、`constants.rs:109-114`、`signed.rs:160-180`。

deep draft 必须从 PR #3010、#3115/#3585 和后续 txpool PR 核实：2D nonce sidecar、nonce-free 过期索引、pool pending/queued 行为、invalidation/griefing 风险、nonce-free replay surface 如何被短 expiry 约束。若这些实现不在本地基线，必须标注 PR diff 取证。

- **Priority**: high
- **Dependencies**: item-3

### item-7: Step 4 - 原生能力：payer、批量、分阶段原子执行、`msg.value == 0`

梳理 EIP-8130 提供的原生账户抽象能力：payer sponsorship、`Vec<Vec<Call>>` phased calls、批量执行、原子/分阶段失败语义、`msg.value == 0` 约定与 ETH 转账方式。`Call` 本地基线只包含 `to` 与 `data`，注释明确 dispatched call carries no value，ETH transfers must be performed by wallet bytecode via CALL；源码锚点为 `call.rs:8-24`。`TxEip8130::calls` 的 `Vec<Vec<Call>>` 与 RLP nested list encoding 源码锚点为 `tx.rs:62-67`、`tx.rs:99-137`。

该 item 必须核实 PR #3680 和 #3696 中 enshrined pre-call execution、account-management transactions、phased call execution、policy gate、full fee settlement 的语义，特别是不同 phase 之间的原子性边界与 revert/fatal 错误处理。payer 需要结合 `payer_auth`、payer hash、fee settlement 与 operator fee PR #3586/#3754 取证。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-5

### item-8: Step 5 - Base PR 时间线与设计动机重建

建立时间线而不是只列 PR：从 2026-05 类型定义和 RPC gate，到 Cobalt hardfork plumbing / activation gate，到 precompiles、canonical contract registry、authenticator dispatch、AccountConfiguration reader、actor authorization、scope gating、2D nonce、gas/fee validation、account changes application、EVM integration、pre-call pipeline、phased calls、txpool/RPC/receipt support，再到 open follow-ups。每个阶段要提炼设计动机：先保守 gate、再逐步加入 validation/execution、再补 RPC/receipts/tooling、最后处理 pending-state admission 与 EOA auto-delegation edge cases。

该 item 要用 PR 搜索结果、Daily Intelligence WHI-90/106/175/239/241/253/265、以及本地 `git log --grep=8130 --all` 交叉验证。引用 PR 时必须给出 PR URL、state、mergedAt、merge commit 或 head branch commit；如果 PR 仍 open（如 #3698、#3752、#3775），必须标注 open/in-flight，不得写成已落地结论。

- **Priority**: medium
- **Dependencies**: item-1

### item-9: Step 6 - WHI-275 D1~D13 rubric 打分框架

用 WHI-275 的统一 rubric 对 EIP-8130 建立打分行，至少覆盖：D1 抽象层级、D2 协议改动范围、D3 基础设施依赖、D4 所有权与密钥模型、D5 Gas 代付、D6 批量原子性、D7 Nonce 与防重放、D8 EOA 兼容与迁移路径、D9 签名灵活性与后量子准备度、D10 成熟度与生态、D11 安全攻击面、D12 Mantle 适配成本、D13 目标用户与产品场景适配。每格要写「score / evidence / confidence / caveat」。

该 item 的目标不是完成 WHI-282 的最终决策，而是给 EIP-8130 deep dive 提供可复用、证据锚定的一行。D12/D13 可以给出初步判断，但必须标注哪些部分依赖后续 Mantle codebase 分析、WHI-279 native AA 方案横向比较与 WHI-282 Mantle 决策分析。

- **Priority**: high
- **Dependencies**: item-2, item-4, item-5, item-6, item-7, item-8

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| source_anchor | 每个结论的主证据：本地源码路径:行 + Base commit、PR URL + commit、EIP URL + accessed date、或 WHI issue/comment。 | all |
| verification_status | `local-baseline-verified` / `remote-pr-diff` / `daily-intelligence-reuse` / `spec-only` / `inference`，明确是否在本地 checkout 验证。 | all |
| spec_vs_base | 区分 EIP-8130 Draft 要求、Base 当前实现选择、Base open PR、以及尚未确定的 TBD。 | all |
| semantic_claim | 该 item 要证明的核心语义结论，必须可被 reviewer 反证。 | all |
| security_or_dos_implication | 对 mempool DoS、signature bypass、replay、griefing、payer abuse、phase failure、state mutation 边界的影响。 | item-3, item-5, item-6, item-7, item-9 |
| 7702_relation | 是否与 EIP-7702 delegation / SignedAuthorization / EOA migration 组合，还是只作为背景比较。 | item-5, item-7, item-9 |
| pr_timeline_stage | PR 属于 type/plumbing/gate/auth/nonce/gas/account-change/EVM/RPC/receipt/open-fix 哪个阶段。 | item-1, item-8 |
| rubric_dimension | 映射到 WHI-275 D1~D13 的维度和初步打分理由。 | item-9 |
| confidence | `high` / `medium` / `low`，并说明不确定性来自 Draft spec、local checkout drift、open PR、还是推论。 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | EIP-8130 signed transaction envelope：`TxEip8130` fields、`sender_auth`、`payer_auth`、EIP-2718 type byte、sender/payer signature hash domain separation。 | mermaid | item-2, item-3 |
| diag-2 | flow | 验证/执行管线：decode -> static admission -> sender resolution -> account configuration / owner scope auth -> nonce validation -> account changes -> phased calls -> fee settlement / receipt。 | mermaid | item-3, item-5, item-6, item-7 |
| diag-3 | table | AccountConfiguration 与 Scope 写语义表：scope bit、context、auth payload、required owner permission、Base source anchor。 | ascii | item-4, item-5 |
| diag-4 | table | account_changes 写语义表：CreateEntry、InitialOwner、ConfigChange、OwnerChange、Delegation 的字段、写入对象、auth requirement、replay protection、source anchor。 | ascii | item-4 |
| diag-5 | timeline | Base EIP-8130 PR 时间线，按阶段展示 merged/open PR、merge date、local-baseline coverage、未本地验证标记。 | mermaid | item-8 |
| diag-6 | comparison | WHI-275 D1~D13 rubric row for EIP-8130：score、evidence、confidence、caveat。 | ascii | item-9 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | code_analysis | 本地 Base checkout `01e732cdbae0c624d652da9e608d7d3fe0f9c74b` 中 `crates/common/consensus/src/transaction/eip8130/{constants,tx,signed,account_changes,call,mod}.rs`，逐字段引用路径:行。 | 6 |
| src-2 | code_analysis | Base 后续 EIP-8130 PR / remote branch diff：至少覆盖 AccountConfiguration storage reader、authenticator dispatch、actor authorization、2D nonce、gas/fee validation、account changes apply、EVM integration、phased calls、RPC/receipts。 | 12 |
| src-3 | official_docs | EIP-8130 Draft 原文，标注 status 与 accessed date；引用时区分 spec TBD 与 Base 实现。 | 1 |
| src-4 | official_docs | EIP-7702、ERC-1271、ERC-4337/EIP-4337、RIP-7560、EIP-8141，作为组合关系与 rubric 背景，不展开成横向报告。 | 5 |
| src-5 | project_prs | Base/base PR 搜索结果，包含 PR number、title、state、mergedAt、headRefName、URL、是否在本地基线可验证。 | 25 |
| src-6 | daily_intelligence | WHI-90/106/175/239/241/253/265 与 WHI-275 final/framework，复用 Base 选型信号、PR seed list、rubric 定义。 | 8 |
| src-7 | implementation_tests | 本地或 PR 中的 tests / fixtures / e2e inclusion tests，用于确认 encoding、nonce-free、scope gating、phased call failure、receipt semantics。 | 5 |

## Expected Deep Draft Structure

1. **文首基线声明**：Base code baseline、dirty status、核验日期、EIP accessed date、source reliability levels。
2. **Executive technical thesis**：8130 的核心不是「又一个 smart wallet」，而是把 account configuration、auth scope、payer、nonce 与 phased call envelope 放入协议交易类型；与 4337/7702 的差异用三句话定位。
3. **Transaction anatomy**：`TxEip8130` + `Eip8130Signed` 字段表、wire format、signature hash、payer domain separation、Base constants vs spec TBD。
4. **Account configuration model**：owner tuple、Scope bits、Create/ConfigChange/Delegation/InitialOwner/OwnerChange、write semantics、AccountConfiguration storage reader PR。
5. **Validation and execution pipeline**：EOA vs configured-account path、ERC-1271 signature scope、payer auth、config auth、EIP-7702 delegation combination、pre-call/account-management pipeline。
6. **Replay and ordering**：2D nonce、nonce-free expiry、txpool sidecar、parallelism / invalidation / DoS considerations。
7. **Native UX primitives**：gas sponsorship, batching, phased atomicity, `msg.value == 0`, fee settlement and receipts。
8. **Base implementation timeline and design motivation**：staged PR narrative, local vs remote verification table, open issues。
9. **WHI-275 D1~D13 EIP-8130 rubric row**：score/evidence/confidence/caveat。
10. **Open questions and drift risks**：Draft spec TBD constants, in-flight PRs, local checkout drift, Mantle-specific follow-up needed。

## Quality Checklist

- [ ] 文首记录 Base commit SHA、commit 日期、dirty 状态、核验日期；所有源码结论锚定路径:行 + commit。
- [ ] 每个 EIP-8130 PR 标注 state、mergedAt/head branch、是否在本地 baseline 中验证；open PR 不写成已落地。
- [ ] `TxEip8130` 与 `Eip8130Signed` 字段逐一解释，包含 nullable sender/payer、auth payload、signature hash、RLP order。
- [ ] Scope bits 与 account_changes 写语义表明确区分 3 个 top-level AccountChange 与 5 类结构/写语义。
- [ ] 讲清 EOA vs 配置账户双路径、ERC-1271、EIP-7702-style delegation 组合关系、2D nonce 与 nonce-free expiry。
- [ ] payer、批量、分阶段 calls、`msg.value == 0` 与 fee settlement 均有源码/PR 证据。
- [ ] WHI-275 D1~D13 每格有 evidence/confidence/caveat，不把 D12/D13 的初步判断当最终 Mantle 决策。
- [ ] spec-Draft/TBD 与 Base 项目选择分开写；Base constants 不被表述为最终规范。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
