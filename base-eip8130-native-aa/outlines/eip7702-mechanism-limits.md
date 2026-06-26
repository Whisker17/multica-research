---
topic: "EIP-7702 机制与局限性分析（含 EIP-3074 溯源）"
project_slug: "base-eip8130-native-aa"
topic_slug: "eip7702-mechanism-limits"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "base-eip8130-native-aa/outlines/eip7702-mechanism-limits.md"
  draft: "base-eip8130-native-aa/research-sections/eip7702-mechanism-limits/drafts/round-{n}.md"
  final: "base-eip8130-native-aa/research-sections/eip7702-mechanism-limits/final.md"
  index: "base-eip8130-native-aa/research-sections/_index.md"

scope: "拆解 EIP-7702 set-code delegation 的机制、Pectra 上线状态、授权 tuple 校验、持久 delegation 语义与安全边界；回溯 EIP-3074 AUTH/AUTHCALL/invoker 模型及其被 EIP-7702 取代的原因；逐项分析 EIP-7702 未解决的问题，包括 EOA ECDSA key dependency、缺少协议级多 owner/key rotation、sponsorship/batching 仍需 delegated wallet 或 ERC-4337、storage collision/delegation-switch risk、authorization replay semantics；厘清 EIP-7702 与 EIP-8130 的关系，尤其验证当前 EIP-8130 对 EIP-7702 delegation indicator / authorization_list / sender_auth 的复用或替代边界；按 native-aa-framework 的 D1-D13 rubric 打分。"
audience: "Mantle dev teams、协议工程师、钱包/AA infra 工程师和 Research Review Agent。读者熟悉 EVM/OP Stack/账户抽象基础，但需要一份可审查、可引用的技术 section 来判断 EIP-7702 为什么只是半原生 AA，以及为什么它不能替代更完整的 native AA 方案。"
expected_output: "结构化研究 section：7702 机制图、3074→7702 取舍表、7702 局限性表、7702 与 8130 组合关系说明、D1-D13 rubric scoring；后续 draft 保存于 base-eip8130-native-aa/research-sections/eip7702-mechanism-limits/drafts/round-1.md，review 接受后 promote 到 base-eip8130-native-aa/research-sections/eip7702-mechanism-limits/final.md。"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-27T00:20:39+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-27T00:20:39+08:00"

multica_issue_id: "14e24b1d-5f0d-475b-b100-defce4c76216"
branch_name: "research/base-eip8130-native-aa/eip7702-mechanism-limits"
base_commit: "aa0d69ba0d85a4ade25cf562f064eef98b64039c"
language: "zh-CN"
research_depth: "standard"
primary_local_dependency: "base-eip8130-native-aa/research-sections/native-aa-framework/final.md"
status_sensitive_sources_verified_at: "2026-06-27"
---

# Research Outline: EIP-7702 机制与局限性分析（含 EIP-3074 溯源）

## Items

### item-1: EIP-7702 set-code delegation 机制与 Pectra 状态

梳理 EIP-7702 的核心机制：`SET_CODE_TX_TYPE=0x04`、`authorization_list` tuple、`0xef0100 || address` delegation indicator、outer transaction signer 与 authorizing EOA 的分离、authorization processing 顺序、delegated execution 对 `CALL`/`STATICCALL`/tx destination 的影响。必须区分持久 delegation 与早期临时 delegation 设计，解释为何 execution revert 不回滚已处理的 delegation indicator。还要注明 EIP-7702 的官方状态、Pectra inclusion 和主网 activation timestamp，避免把草案时期语义带入当前结论。

- **Priority**: high
- **Dependencies**: none

### item-2: EIP-3074 AUTH/AUTHCALL/invoker 模型与转向 7702 的取舍

回溯 EIP-3074 如何通过 `AUTH` 和 `AUTHCALL` 让 EOA 授权 invoker contract 代表自己发起调用，并解释它试图解决的 batching、sponsorship、scripting 等 EOA UX 问题。研究必须说明 3074 的 authority/invoker/relayer 参与方、签名 payload、授权生命周期、安全假设和 invoker 合约风险。最终要以表格对比 3074 与 7702：新 opcode vs 新 transaction type、invoker temporary control vs persistent code delegation、对 ERC-4337/未来 AA 的兼容性、EVM 技术债务和治理上被 7702 supersede 的原因。

- **Priority**: high
- **Dependencies**: item-1

### item-3: EIP-7702 的能力边界与“半原生 AA”定位

把 EIP-7702 能直接改善的 UX 能力和不能直接解决的问题分开：它能让 EOA 原地址执行 delegated wallet code，从而支持 batching、sponsorship pattern 和 privilege de-escalation，但这些能力依赖被委托代码和应用/infra 设计，而不是 7702 自身定义完整智能账户协议。需要明确 EIP-7702 仍由 ECDSA EOA 授权 tuple 驱动，不提供协议级多 owner、key rotation、guardian、paymaster lifecycle 或 account configuration。该项要产出一张 limitations table，逐项列出机制原因、影响范围、可缓解方式和残余风险。

- **Priority**: high
- **Dependencies**: item-1

### item-4: 7702 新攻击面：storage、delegation switching、replay 与 wallet safety

从安全角度拆解 7702 的新增风险，而不是只列出抽象缺点。必须覆盖 delegated code 与 EOA storage 的碰撞/布局迁移、用户切换 delegation target 导致状态解释变化、front-running initialization、授权 tuple replay 语义（`chain_id == 0` 与 authority nonce）、delegate 合约升级/恶意 code 指针、应用诱导用户签 delegation 的安全边界。研究要区分规范直接规定的风险、delegate wallet 实现风险、钱包 UI/签名流程风险和 relayer/sponsor operational risk。

- **Priority**: high
- **Dependencies**: item-1, item-3

### item-5: EIP-7702 与 EIP-8130 的组合关系与术语校正

厘清 7702 与 8130 的关系：7702 是已部署的 EOA set-code delegation 基础能力，8130 是更完整的 account configuration / actor / authenticator / payer / phased calls native AA 方案。深度研究必须验证并精确表述当前 EIP-8130 如何依赖或复用 7702：至少检查 delegation indicator `0xef0100 || target`、standard EIP-7702 transaction portability、8130 `account_changes` delegation entry、`sender_auth`、以及是否仍复用 7702 `authorization_list` / SignedAuthorization。若调度文本“8130 reuses 7702 SignedAuthorization”与当前规范不一致，draft 应显式写成“dispatch claim vs current spec”核验结果，并给出可引用证据。

- **Priority**: high
- **Dependencies**: item-1, item-3

### item-6: 按 D1-D13 rubric 对 EIP-7702 打分并给 Mantle 后续判断输入

使用 `native-aa-framework/final.md` 的 D1-D13 维度给 EIP-7702 单方案评分，并标注每格证据类型：`spec-cited`、`framework-cited`、`code-cited`、`data-cited`、`inferred` 或 `unknown`。评分不能直接下 Mantle 是否实现 8130 的最终结论，但要为后续 native AA 对比提供输入，尤其是 D4 key model、D5 sponsorship、D6 batching、D7 replay、D8 EOA compatibility、D10 maturity、D11 attack surface、D12 Mantle adaptation cost、D13 target use case fit。D12/D13 允许保留为 bounded assessment，但不能用“效果不好”作无证据前提。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| source_status | 记录每个规范/文档的 official status、访问日期、是否 Final/Draft/Withdrawn、是否有 activation 或 fork inclusion。 | all |
| mechanism_summary | 用简洁步骤说明方案机制、交易结构、参与方、状态变更和执行顺序。 | item-1, item-2, item-5 |
| protocol_surface | 标注协议改动面：tx type、opcode、delegation indicator、transaction validation、mempool/RPC/receipt、account storage 或 execution semantics。 | all |
| security_assumption | 描述安全边界和信任假设，包括 ECDSA key、delegate code、invoker contract、wallet UI、relayer/sponsor、authenticator 等。 | item-2, item-3, item-4, item-5 |
| limitation_category | 将限制分为 key model、account model、sponsorship/batching、storage/delegation、replay/nonce、ecosystem/DX、Mantle adoption evidence。 | item-3, item-4, item-6 |
| mitigation_or_workaround | 对每项限制列出 7702 delegated wallet、ERC-4337、钱包 UI、审计、protocol-native AA、8130 等缓解路径，并注明是否仍有残余风险。 | item-3, item-4, item-5, item-6 |
| evidence_type | 标注结论证据类型：official spec、local framework file、local code path、upstream PR/comment、ecosystem doc、on-chain data、inference。 | all |
| rubric_dimension | 映射到 D1-D13 的对应维度，避免最后评分表与正文脱节。 | item-3, item-4, item-5, item-6 |
| open_question | 记录 draft 阶段必须解决或明确无法解决的问题，例如 8130 是否复用 SignedAuthorization 的术语差异、Mantle 7702 adoption 数据是否可得。 | item-5, item-6 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | flow | EIP-7702 set-code transaction flow：outer tx sender、authorization tuple signer、authority nonce check、delegation indicator write、delegated execution、revert 不回滚 delegation 的路径。 | mermaid | item-1 |
| diag-2 | comparison | 3074 invoker flow vs 7702 delegation flow：EOA signature、invoker/delegate contract、who pays gas、where code executes、state persistence。 | mermaid | item-2 |
| diag-3 | architecture | 7702 与 8130 组合关系：standard 7702 transaction、8130 AA transaction、delegation indicator、account_changes delegation entry、sender_auth/authenticator/payer 的边界。 | mermaid | item-5 |
| diag-4 | matrix | EIP-7702 局限性矩阵：限制类别、机制原因、影响、可缓解方案、残余风险、D1-D13 映射。 | ascii | item-3, item-4, item-6 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | EIP-7702 official spec：必须引用 status=Final、`SET_CODE_TX_TYPE=0x04`、authorization tuple、delegation indicator、persistence/revert semantics、security considerations；外部结论附访问日期。 | 1 |
| src-2 | official_docs | EIP-7600 Pectra meta：必须引用 EIP-7702 included in Pectra 和 mainnet activation timestamp `1746612311`；外部结论附访问日期。 | 1 |
| src-3 | official_docs | EIP-3074 official spec：必须引用 status=Withdrawn、withdrawal reason superseded by EIP-7702、AUTH/AUTHCALL/invoker model、security considerations。 | 1 |
| src-4 | official_docs | EIP-8130 official spec：必须核验 7702 delegation indicator、standard EIP-7702 transaction portability、delegation entry/account_changes/sender_auth，以及是否复用或替代 7702 authorization_list / SignedAuthorization。 | 1 |
| src-5 | local_research | `base-eip8130-native-aa/research-sections/native-aa-framework/final.md`：必须使用其 D1-D13 定义、taxonomy 边界和 evidence_type 口径，不得重新发明 rubric。 | 1 |
| src-6 | code_analysis | 如可用，读取本地 `/Users/whisker/Work/src/networks/base/base` 或上游 Base EIP-8130 实现路径，验证 8130 与 7702 delegation/auth 的实现关系；如果本轮 draft 无法读取，需明确标注未取证。 | 1 |
| src-7 | ecosystem_docs | Wallet/AA infra 或 ERC-4337/7702 互补资料，用于验证 sponsorship/batching 仍依赖 delegate wallet 或 4337 的实操边界；优先官方文档或 EIP rationale。 | 2 |
| src-8 | security_discussion | 安全讨论来源：EIP security considerations、wallet guidance、audit/writeups 或 Ethereum Magicians/ACD 讨论，用于 storage collision、delegation switching、replay、front-running initialization 等风险。 | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
