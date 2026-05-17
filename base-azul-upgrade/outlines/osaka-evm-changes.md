---
topic: "Osaka 执行层 EIP 变更分析与代码实现"
project_slug: base-azul-upgrade
topic_slug: osaka-evm-changes
github_repo: Whisker17/multica-research
round: 2
status: candidate

artifact_paths:
  outline: base-azul-upgrade/outlines/osaka-evm-changes.md
  draft: base-azul-upgrade/research-sections/osaka-evm-changes/drafts/round-{n}.md
  final: base-azul-upgrade/research-sections/osaka-evm-changes/final.md
  index: base-azul-upgrade/research-sections/_index.md

scope: |
  深入分析 Base Azul 升级中对齐 Ethereum Osaka 的五项执行层 EIP：EIP-7825（Transaction Gas Limit
  Cap）、EIP-7823（Upper-Bound MODEXP）、EIP-7883（MODEXP Gas Cost Increase）、EIP-7939（CLZ
  Opcode）、EIP-7951（secp256r1 Precompile 重新计价）。每项 EIP 同时覆盖 spec 解读、base/base 仓库
  (base-reth-node) 中的代码实现路径与关键符号、与 OP Stack 上游执行层（`ethereum-optimism/op-geth`，
  Go 实现）的对应位置、以及 `ethereum-optimism/optimism` monorepo 中的 rollup/config/依赖证据、对
  L1 等价性的影响、对现有合约/precompile 调用者的兼容性影响，以及 Mantle 团队复刻这些变更时需要
  重点关注的工程细节。本研究聚焦执行层 EVM/precompile 行为变更，不覆盖 EIP-7642 (eth/69) 或
  EIP-7910 (eth_config) 等网络/RPC 层变更，也不进入 deposit 交易完整生命周期、L1 bridging 等更广
  OP Stack 议题。
audience: |
  Mantle 协议工程团队（决定是否在自家 L2 复用同样的 Osaka 对齐策略与代码改造）、Base/OP Stack
  生态执行层研究者、依赖 MODEXP/p256Verify/CLZ 的 DeFi 与跨链协议开发者、Multica 研究 squad 下游
  mantle-impact-assessment 研究主题。读者熟悉 EVM 与 Solidity gas 模型，但不一定熟悉 reth/revm 内部
  API、precompile provider 注册机制或 Base 客户端结构。
expected_output: |
  - 五项 EIP 各自的 spec 解读：精确常量（gas、输入字节上限、opcode 编号）、enforcement 位置（mempool
    /block validation/precompile pipeline）、与 L1 主网行为的等价/分歧点
  - 对应 base/base 代码定位表：文件路径 + 行号 + 关键符号 + 入口测试，至少覆盖 cfg_env 装配、
    BaseHandler.validate_env、BasePrecompiles::azul、BaseUpgrade→SpecId 映射、reth/revm 上游依赖与
    专项集成测试
  - 关键代码片段的注释解析（每个 EIP 至少 1 段代码 + 解读，标注 deposit/L2 专有分支）
  - 与 OP Stack 上游的双源差异表：
    - 执行层 (EL) 实现：`ethereum-optimism/op-geth` (Go) 中对应文件/符号、pinned tag/SHA
    - Rollup/config/依赖证据：`ethereum-optimism/optimism` monorepo 中 hardfork 时间戳、op-geth 依赖
      版本、op-program/op-node 中的配置开关
    - 语言与架构层级差异、功能等价性结论
    - 对每个 EIP 在两侧实现源中必须给出"实际位置"或"justified absence"（含搜索证据与理由）
  - 各 EIP 对现有合约/协议的兼容性影响评估：DeFi 协议（RSA 验证、p256Verify、自定义大数运算）、L2
    bridge 与跨链消息、deposit 交易特殊行为，标注 worst-case gas 变化倍数与建议迁移路径
  - 至少 3 张 Mermaid 图：tx gas-limit 校验流程、precompile provider 跨 fork 演进、MODEXP gas 公式
    演进对比
  - 对所有出现冲突的 primary source（首要案例：EIP-7951 在 Base Azul exec-engine spec 中同时出现
    3,450 与 6,900 两个 gas 数值），必须显式声明 conflict、选定权威来源、并以代码/测试证据支持
    resolution
  - Evidence: 至少引用 5 份 EIP 原文、Base Azul exec-engine spec、base/base 关键源码（含行号锚点）、
    `ethereum-optimism/op-geth` 上游对照位置（pinned tag/SHA）以及 `ethereum-optimism/optimism`
    monorepo 中的 rollup/config 证据

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-17T06:40:07Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-17T07:00:00Z"
---

# Research Outline: Osaka 执行层 EIP 变更分析与代码实现

## Items

### item-1: EIP-7825 Transaction Gas Limit Cap 与 deposit 豁免实现

逐层拆解 EIP-7825 在 Base Azul 中的实现链路：上游 spec（每笔交易硬上限 2^24 = 16,777,216 gas）、
Base Azul 是否完全采纳 L1 等价语义、deposit 交易豁免的理由（已被 L1 inclusion 限制为 20,000,000
gas）、以及该 cap 在 mempool 与 block validation 两个 enforcement 点的对应代码。需明确：
`BaseEvmEnvBuilder::cfg_env` 在 `is_azul_active_at_timestamp` 为真时如何把 `MAX_TX_GAS_LIMIT_OSAKA`
注入 `CfgEnv::tx_gas_limit_cap`，`BaseHandler::validate_env` 中 deposit 路径的 early-return 与非-deposit
路径委托给 `MainnetHandler::validate_env` 后的实际校验位置，以及 `txpool.max_tx_gas_limit` 在
`node.rs` 中的参数化方式。也要回答：Mantle 复刻时若 deposit 语义不同应如何调整？

- **Priority**: high
- **Dependencies**: none

### item-2: EIP-7823 Upper-Bound MODEXP 输入限制实现

分析 EIP-7823 对 MODEXP precompile 输入字段的硬上限（base/exponent/modulus 各 ≤ 1024 字节）
在 Base Azul 中的接入方式。Base/Reth 复用 revm `modexp::OSAKA` 精度规则，BasePrecompiles 在
`provider.rs::azul()` 中通过 `precompiles.extend([modexp::OSAKA, secp256r1::P256VERIFY_OSAKA])` 实现
opt-in。需要回答：oversize 输入的失败语义（返回错误 + 消耗全部 gas，对应 `PrecompileError::Modexp
Eip7823LimitSize`）、单字段超限即拒绝的边界测试（`provider.rs` 的 `test_modexp_eip7823_each_field
_rejects`）、`eip7823::INPUT_SIZE_LIMIT` 常量来源，以及 Base 是否引入任何 L1 之外的额外限制。

- **Priority**: high
- **Dependencies**: item-1

### item-3: EIP-7883 MODEXP Gas Cost 三重提升与历史影响分析

形式化 EIP-7883 对 EIP-2565 公式的三处修改：(a) `MIN_GAS` 200→500，(b) 去掉 `/3` 分母（相当于
3× 系数），(c) exponent_length>32 时的 multiplier 8→16，以及 `multiplication_complexity` 在
max_length>32 时的 `2*words²`、否则保底 16。结合 base/base 中复用的 revm `modexp::osaka_run` 与
`test_modexp_eip7883_min_gas_increase` / `test_modexp_eip7883_larger_input_gas_increase` 验证 Berlin
vs Osaka 实际 gas 差距。在分析层面，针对历史调用样本（EIP 文档给出的 nagydani/marcin/guido 案例：
150% / 200% / 数千% 上升）总结哪些 DeFi/L2 模式风险最高（RSA 验证、Verifier、zk-bridge），并标注
Mantle 复刻时如何处理已部署但未预期到 gas 涨价的合约。

- **Priority**: high
- **Dependencies**: item-2

### item-4: EIP-7939 CLZ Opcode：语义、激活与 ZK 友好性

梳理 CLZ 操作码的硬性事实：opcode `0x1e`、gas 5（与 MUL 同级，spec 中由 3 升至 5 以防止 DoS）、栈
效应 1→1、零输入返回 256。Base 侧并不在自身代码中显式加入指令表实现，而是通过 `BaseUpgrade::Azul
=> SpecId::OSAKA` 把指令开关交给 revm 上游；这一点需要明确：哪个 Rust crate 实际承载 CLZ 实现、
`BasePrecompileInstaller` / `BaseHandler` 是否会在 Azul 之前的 fork 上禁用 CLZ。结合
`crates/common/evm/src/handler.rs` 中的 `test_clz_opcode_azul` (验证字节码 `60801E60005260206000F3`
在 Azul 上返回 248)与 `test_clz_opcode_not_on_jovian`（验证 pre-Osaka 上 CLZ 不可用）说明实际激活
边界。分析层面：CLZ 对 sqrt/lnWad/powWad、bitmap 与 ZK rv32im prover 的影响，以及 Mantle 如果开启
ZK Stack 是否值得在更早 fork 引入。

- **Priority**: high
- **Dependencies**: item-1

### item-5: EIP-7951 secp256r1 (p256Verify) Precompile Gas 翻倍

记录 secp256r1 precompile 在 Base 历史上的两段轨迹：Fjord 通过 RIP-7212 引入位于 `0x100` 的
`P256VERIFY`，gas 3450；Azul 借由 EIP-7951 把 gas 提升至 6900 并保持地址与 ABI 完全兼容。需要锚定：
`BasePrecompiles::fjord()` 中 `precompiles.extend([secp256r1::P256VERIFY])`、`BasePrecompiles::azul()`
中再次 extend 后的 `secp256r1::P256VERIFY_OSAKA` 如何在同一地址覆盖原条目；`test_p256verify_osaka
_exact_gas`、`test_p256verify_gas_doubled`（断言新 base fee = 旧 base fee × 2）等测试如何验证翻倍
关系；以及 `P256VERIFY_BASE_GAS_FEE_OSAKA` 常量在 revm 中的真实定义位置。**Source conflict 必须解
决**：Base Azul `exec-engine.md` 第 37–43 行附近同时出现 "p256 verify gas is 3,450" 与 "Azul raises
the cost to 6,900 to match L1" 两条陈述；EIP-7951 原文与 base/base 测试 (`test_p256verify_gas_doubled`,
`test_p256verify_osaka_exact_gas` 断言 6900) 均锚定 6,900。draft 必须显式声明冲突、选定 EIP-7951 +
源码 + 测试为权威来源，并解释 spec 文本中 3,450 是 pre-Azul 历史数值（Fjord/RIP-7212 引入时的费用），
6,900 才是 Azul 之后生效的最终值。兼容性层面：枚举依赖 p256Verify 的 Account Abstraction / Passkey
场景，量化 gas 翻倍对 ERC-4337 paymaster、EIP-7702 委托账户的成本影响，并区分 Base vs L1 在 Osaka
之前的差异（L1 历史上不存在此地址，Base 比 L1 早数轮）。

- **Priority**: high
- **Dependencies**: item-1

### item-6: 跨切面集成：BaseUpgrade→SpecId 映射、OP Stack 双源 diff 与端到端测试矩阵

把前五项 EIP 串成一条完整的激活链路：`crates/common/chains/src/upgrade.rs` 中 `BaseUpgrade::Azul =>
SpecId::OSAKA`、`BasePrecompiles::new_with_spec(Azul) => Self::azul()`、`BaseEvmEnvBuilder::cfg_env`
在 Azul 时间戳开启 tx_gas_limit_cap。

OP Stack 上游对比必须使用**双源**：
- **执行层 (EL) 实现源** — `ethereum-optimism/op-geth`（Go 单仓，实际承载 EIP-7825/7823/7883/7939/
  7951 的 Go 代码）。需要 pin 到与所审查 `optimism` monorepo 一致的 tag/SHA（通过 monorepo `go.mod`
  中的 `github.com/ethereum-optimism/op-geth` require 行或 `op-program/Dockerfile`、`op-node` go.sum
  pin 来确认），并锚定具体路径/符号：`core/vm/jump_table.go` (CLZ)、`core/vm/contracts.go` 与
  `core/vm/contracts_test.go` (MODEXP, p256Verify)、`core/state_transition.go` (tx gas cap)、相应的
  `params/protocol_params.go` 常量。
- **Rollup/config/依赖证据源** — `ethereum-optimism/optimism` monorepo。锚定：`op-chain-ops`、
  `op-node/rollup` 中的 hardfork timestamp 配置（Holocene/Isthmus/Jovian/Granite 之后 OP Stack 等价
  于 Azul 的 fork）、`op-program/host` 与 `op-batcher` 中是否需要同步硬分叉时间戳、`go.mod` 中
  op-geth 的依赖版本，以确认 monorepo 与 op-geth 在版本上的对齐。

对每个 EIP 必须分别在两侧给出：实际实现位置（含 pinned tag/SHA、文件、符号），或在某侧确认为
"justified absence"（例如 monorepo 不包含 EVM 实现，因为执行层全部下沉到 op-geth）并附搜索证据。
也要识别 base/base 中的 Base-only 补丁（deposit early-return、Azul-only precompile set）以及是否存在
Base 落后或超前于 OP Stack 的特性。

最后列出端到端验证矩阵：`crates/execution/flashblocks-node/tests/azul.rs` 的
`eth_sendRawTransaction` 拒绝/接受测试、`etc/scripts/devnet/test-base-azul.sh` 的 devnet 集成测试、
以及 `test_osaka_opcodes_activated_azul` 这类单元测试，告诉 Mantle 团队如果做相同迁移应该补齐哪
些层级的测试。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| spec_summary | EIP/Base spec 给出的纯事实定义：常量、字段语义、enforcement 位置 | item-1, item-2, item-3, item-4, item-5 |
| gas_constants_and_bounds | 该变更涉及的所有数值（gas 上限、字节上限、gas 费率、opcode 号、地址） | item-1, item-2, item-3, item-4, item-5 |
| code_paths | base/base 仓库中实现该 EIP 的文件路径（含行号锚点）与关键符号（struct/fn/常量） | item-1, item-2, item-3, item-4, item-5, item-6 |
| code_excerpt_with_annotation | 至少一段不超过 25 行的代码片段配 1-3 句注释解析，标注 deposit/L2 分支 | item-1, item-2, item-3, item-4, item-5 |
| deposit_or_l2_specific_behavior | 该 EIP 在 Base L2 上是否存在与 L1 不同的分支（如 deposit 豁免、Base-only precompile 集合） | item-1, item-2, item-3, item-4, item-5, item-6 |
| l1_equivalence_or_divergence | Base Azul 与 Ethereum Osaka 行为差异点：完全等价 / 部分等价 / 显式偏离 | item-1, item-2, item-3, item-4, item-5 |
| backward_compatibility_impact | 对既有合约/调用者的影响：raise/revert、gas 变化倍数、迁移建议 | item-1, item-2, item-3, item-4, item-5 |
| test_coverage | base/base 中覆盖该 EIP 的单元/集成/devnet 测试清单 | item-1, item-2, item-3, item-4, item-5, item-6 |
| op_stack_upstream_mapping | OP Stack 上游对应实现的双源证据：必须分别给出 (a) `ethereum-optimism/op-geth` 中的 EL 实现位置（文件+符号+pinned tag/SHA），(b) `ethereum-optimism/optimism` monorepo 中的 rollup/config/依赖证据（hardfork 时间戳、op-geth pinned 版本、相关 config 文件）。"在 optimism monorepo 中无对应"仅在同时给出 op-geth 实际位置（或经过解释的 justified absence + 搜索证据）时才成立；不允许仅以 "no equivalent in optimism monorepo" 一句结案。 | item-1, item-2, item-3, item-4, item-5, item-6 |
| mantle_replication_notes | 复刻该变更时 Mantle 团队需要关注的工程点（deposit 语义、precompile 地址冲突、已部署合约影响） | item-1, item-2, item-3, item-4, item-5, item-6 |
| source_conflicts_and_resolution | 列出该 item 涉及的 primary source 冲突（数值、语义、激活时间）、选定权威来源（EIP 原文 / Base spec / base/base 源码 / op-geth 源码 / 测试），并以代码 + 测试证据支持最终 resolution。最低限度必须覆盖 item-5：Base Azul `exec-engine.md` (~37–43 行) 同时出现 p256Verify gas 3,450 与 6,900，draft 必须解释 3,450 为 Fjord/RIP-7212 历史值、6,900 为 Azul 之后的最终值，并以 EIP-7951、`P256VERIFY_BASE_GAS_FEE_OSAKA`、`test_p256verify_gas_doubled` 等证据落实。其他 item 若实际研究中出现 primary source 冲突也必须填写此字段；无冲突时记录 "no conflict observed"。 | item-5, all-if-encountered |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | flow | EIP-7825 交易 gas-limit 校验流程：tx 提交 → mempool 检查 → BaseHandler.validate_env (deposit early-return vs 非-deposit 委托给 mainnet) → revm cfg_env.tx_gas_limit_cap 比较 | mermaid | item-1, item-6 |
| diag-2 | hierarchy | BasePrecompiles 跨 fork 演进图：Cancun → Fjord(+P256VERIFY) → Granite(+bn254 GRANITE) → Isthmus(+bls12_381) → Jovian(替换为 reduced limits) → Azul(extend modexp::OSAKA + P256VERIFY_OSAKA) | mermaid | item-2, item-5, item-6 |
| diag-3 | comparison | MODEXP gas 公式演进对比矩阵：EIP-2565 (Berlin) 公式 vs EIP-7883 (Osaka) 公式，标注 min-gas / multiplier / iteration_count / multiplication_complexity 三处差异 | mermaid | item-3 |
| diag-4 | flow | p256Verify (0x100) 调用路径：Fjord (RIP-7212, 3450 gas) → Azul (EIP-7951, 6900 gas)；展示同地址下 PrecompileFn 替换与 EVM gas 计费分支；标注 spec 文本 3,450 vs 6,900 的冲突来源与解决路径 | mermaid | item-5 |
| diag-5 | architecture | Base/base vs OP Stack upstream 实现层级映射图：Rust workspace (crates/common, crates/execution) vs Go 双仓 (`ethereum-optimism/optimism` monorepo: op-node/op-batcher/op-program; `ethereum-optimism/op-geth`: core/vm, core/state_transition)，展示 EL 实现源 vs rollup/config 源的边界 | mermaid | item-6 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | EIP 原文：EIP-7825, EIP-7823, EIP-7883, EIP-7939, EIP-7951 | 5 |
| src-2 | official_docs | Base Spec：`/upgrades/azul/exec-engine`, `/upgrades/azul/overview`, 以及 RIP-7212 原文 | 3 |
| src-3 | code_analysis | base/base 源码（带行号锚点）：至少覆盖 `crates/common/chains/src/upgrade.rs`、`crates/execution/evm/src/env.rs`、`crates/common/precompiles/src/provider.rs`、`crates/common/evm/src/handler.rs`、`crates/execution/flashblocks-node/tests/azul.rs`、`etc/scripts/devnet/test-base-azul.sh` | 6 |
| src-4 | code_analysis | OP Stack rollup/config/依赖证据源 `ethereum-optimism/optimism` monorepo：仅用于 rollup hardfork 时间戳配置、`go.mod` 中对 op-geth 的依赖 pin、op-node/op-program/op-batcher 中是否需要同步硬分叉时间戳，以及搜索证明 monorepo 不包含执行层 EVM 实现（justified absence 证据）。**不再用于 EVM/precompile/tx 验证 Go 实现的引用**——那部分由 src-7 承担。 | 2 |
| src-5 | code_analysis | revm/reth 上游引用：`MAX_TX_GAS_LIMIT_OSAKA`、`modexp::OSAKA`/`osaka_run`、`secp256r1::P256VERIFY_OSAKA`、`P256VERIFY_BASE_GAS_FEE_OSAKA`、`eip7823::INPUT_SIZE_LIMIT` 等常量的定义来源 | 3 |
| src-6 | expert_commentary | 至少一份 Base/OP/Reth 团队工程师或外部审计/研究对 Osaka 这五项 EIP 的公开评估（博客、Ethereum Magicians 帖、PEEPanEIP、audit 报告） | 1 |
| src-7 | code_analysis | OP Stack 执行层实现源 `ethereum-optimism/op-geth`：pinned 到所审查 `optimism` monorepo 同步使用的 tag 或 commit SHA（来源：monorepo `go.mod` 或 `op-program/Dockerfile`/`op-node` go.sum）。每个 EIP 必须给出对应 Go 文件 + 符号（如 `core/vm/jump_table.go` 中 CLZ 的 jump table 注册、`core/vm/contracts.go` 与 `core/vm/contracts_test.go` 中的 MODEXP / p256Verify、`core/state_transition.go` 中 tx gas cap 校验、`params/protocol_params.go` 中常量），或在该 EIP 在 op-geth 中尚未实现/位置不存在时给出 justified absence + 搜索证据（grep 关键字、PR 链接、issue 链接）。 | 5 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-6 | 将 OP Stack 对比拆分为双源：`ethereum-optimism/op-geth`（EL Go 实现，pinned tag/SHA）与 `ethereum-optimism/optimism` monorepo（rollup/config/依赖证据），以避免把 monorepo 当作 EVM 实现源造成 diff 错误。 | agent:research-agent (round-1 review verdict cf082a5e, orchestrator revision request 334e5772) |
| 2 | modify_field | op_stack_upstream_mapping | 强制要求双源 provenance：必须分别给出 op-geth 的 EL 实现位置和 optimism monorepo 的 rollup/config 证据；不允许仅以 "no equivalent in optimism monorepo" 结案。 | agent:research-agent (round-1 review verdict cf082a5e) |
| 2 | modify_source_req | src-4 | 把 src-4 收敛为 optimism monorepo rollup/config/依赖证据来源，min_count 维持 2；EL Go 实现引用迁出至新增的 src-7。 | agent:research-agent (round-1 review verdict cf082a5e) |
| 2 | add_source_req | src-7 | 新增 OP Stack 执行层实现源 `ethereum-optimism/op-geth`，要求 pinned tag/SHA 与每个 EIP 的 Go 文件/符号或 justified absence，min_count 5。 | agent:research-agent (round-1 review verdict cf082a5e) |
| 2 | add_field | source_conflicts_and_resolution | 显式要求 draft 列出 primary source 冲突、选定权威来源、并以代码+测试证据支持 resolution；最低限度覆盖 item-5 中 Base Azul spec 文本 p256Verify gas 3,450 vs 6,900 的冲突。 | agent:research-agent (round-1 review verdict cf082a5e, finding on EIP-7951 gas conflict) |
| 2 | modify_item | item-5 | 在 EIP-7951 item 描述中显式纳入 spec 文本 3,450 vs 6,900 冲突的命名、权威来源选定（EIP-7951 + base/base 测试）、以及 resolution 解释（3,450 = Fjord/RIP-7212 历史值，6,900 = Azul 最终值）。 | agent:research-agent (round-1 review verdict cf082a5e) |
| 2 | modify_diagram | diag-4 | 在 p256Verify 调用路径图中加入 spec 文本 3,450 vs 6,900 冲突来源与解决路径标注。 | agent:research-agent (round-1 review verdict cf082a5e) |
| 2 | modify_diagram | diag-5 | 把 OP Stack 侧从单仓 (`ethereum-optimism/optimism`) 扩为双仓（optimism monorepo + op-geth），以反映 EL 实现源 vs rollup/config 源的边界。 | agent:research-agent (round-1 review verdict cf082a5e) |
