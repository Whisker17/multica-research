---
topic: "合规 Token 底座与 B20 私密扩展需求分析"
project_slug: "confidential-compliance-token-research"
topic_slug: "compliance-token-private-extension"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "confidential-compliance-token-research/outlines/compliance-token-private-extension.md"
  draft: "confidential-compliance-token-research/research-sections/compliance-token-private-extension/drafts/round-{n}.md"
  final: "confidential-compliance-token-research/research-sections/compliance-token-private-extension/final.md"
  index: "confidential-compliance-token-research/research-sections/_index.md"

scope: |
  M1 分析任务。复用 compliance-token-standards 与 requirements-framework 已完成结论，抽取 Mantle
  confidential compliance token 的合规 token 能力模型；分析 B20 协议骨架与 ERC-3643 应用层骨架；
  定义 encrypted balance / amount / allowance、密文事实上的 policy check、auditor disclosure、
  freeze/recovery under ciphertext 等 private feature 对合规骨架的新增要求；输出
  B20 + private feature 的 phase 1 must-have / optional / phase 2 boundary table；并标注哪些结论可
  直接复用旧项目文件，哪些必须对 Base/Mantle local code 重新核验。
audience: "Mantle 协议/战略团队、RWA/机构业务负责人、合规架构师、隐私后端评估作者、研究评审 agent"
expected_output: |
  outline 阶段输出本文件；final 阶段输出
  confidential-compliance-token-research/research-sections/compliance-token-private-extension/final.md。
  final 需给出合规 token 能力到 confidential extension 需求矩阵、B20 / ERC-3643 / TIP-20 复用边界、
  B20 + private feature phase 1 / optional / phase 2 能力表，以及 Base/Mantle 代码核验清单。

revision_metadata:
  created_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-24T00:40:00Z"
  last_modified_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-24T00:40:00Z"

multica_issue_id: "18fbd577-47e2-47f6-bfbf-a7519114df13"
report_issue_id: "7b29e4a8-01eb-4cbf-9b59-8e363f9a40e4"
branch_name: "research/confidential-compliance-token-research/compliance-token-private-extension"
base_commit: "eefb63d9297c823d545a82ce36a2c31f7eceaba8"
dependencies:
  - "requirements-framework"
order: 4
language: "中文"
mode: "composable-single-issue"

reference_inputs:
  direct_reuse:
    - path: "confidential-compliance-token-research/research-sections/requirements-framework/final.md"
      commit: "9eb29a150f380f21add9b431b66fea2ee5d12881"
      role: "CCT 术语口径、能力模型、rubric、证据复用规则、Inco/Optalysys 分类边界"
    - path: "compliance-token-standards/report/final-report.md"
      commit: "79d472632bd30a5354fbec396f807e0bb63bdea1"
      role: "合规 token 8 类 taxonomy、应用层 vs 协议层合规、Mantle 分阶段策略"
    - path: "compliance-token-standards/research-sections/base-b20-analysis/final.md"
      commit: "f42915ecd33c7f099d4ac0de89997390fc52d0b9"
      role: "B20 Factory / PolicyRegistry / ActivationRegistry / RBAC / policy scopes / Asset-Stablecoin variants / issuer controls"
    - path: "compliance-token-standards/research-sections/erc3643-trex-analysis/final.md"
      commit: "a260e40f58b0d8d2e15ba7bd263ab67a3288b6bd"
      role: "ERC-3643 ONCHAINID、Identity Registry、Claim Topics、Trusted Issuers、Modular Compliance、Agent roles"
    - path: "compliance-token-standards/research-sections/tempo-tip20-analysis/final.md"
      commit: "67c509b757699152095a8872b810817f6104aaba"
      role: "TIP-20 / TIP-403 支付型 precompile、memo、Payment Reconciliation、policy registry 生产经验"
    - path: "compliance-token-standards/research-sections/compliance-token-comparison/final.md"
      commit: "f42915ecd33c7f099d4ac0de89997390fc52d0b9"
      role: "ERC-3643 / B20 / TIP-20 横向能力差异与成熟度 trade-off"
    - path: "compliance-token-standards/research-sections/mantle-compliance-token-strategy/final.md"
      commit: "f42915ecd33c7f099d4ac0de89997390fc52d0b9"
      role: "Mantle 当前无自定义 precompile、双客户端/硬分叉约束、ERC-3643 短期先行策略"
  local_code_verification_targets:
    - path: "/Users/whisker/Work/src/networks/base"
      purpose: "仅当 final 需要确认 B20 当前代码是否仍符合旧项目 pinned 结论、是否出现 B20Security/redeem/private extension 新信号时使用"
    - path: "/Users/whisker/Work/src/networks/mantle"
      purpose: "核验 Mantle 当前是否仍无自定义 precompile、下一次 hardfork 是否仍未定义、op-geth/reth precompile 接入面是否有变化"
---

# 研究大纲（Research Outline）：合规 Token 底座与 B20 私密扩展需求分析

本 section 的核心任务不是重做 `compliance-token-standards`，而是把旧项目的合规 token 能力语言迁移到 Confidential Compliance Token（CCT）语境：以 B20 作为协议骨架和能力类比，以 ERC-3643 作为短期应用层合规基线，以 TIP-20 作为支付/对账型 precompile 参考，再定义 private feature 对这些骨架新增的最小要求。

关键边界：`Base B20 token + private feature` 是产品和架构类比，不等于 Mantle phase 1 要复制 Base B20 precompile。Mantle 当前策略仍应默认轻量集成优先；precompile / hardfork / native encrypted accounting 属于 phase 2 或中长期协议路线，除非 local code verification 改变这一约束。

## 研究条目（Items）

### item-1: 合规 Token 能力模型抽取与 CCT 映射

从既有合规 token taxonomy 中抽取 CCT 必须继承的能力模型：identity/KYC、transfer policy、issuer controls、sanctions/blacklist、recovery、legal metadata、payment reconciliation、audit/privacy。研究应把普通 compliance token 能力与 private feature 的新增要求并列表达，避免把“合规能力”与“加密账本能力”混为一谈。本项还要明确哪些能力属于 phase 1 token/product 必须回答的问题，哪些可由外部 identity registry、policy registry、auditor service 或 disclosure workflow 提供。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: none

### item-2: B20 协议骨架与可复用能力语言

分析 B20 的协议骨架：B20Factory、PolicyRegistry、ActivationRegistry、RBAC、四类 policy scopes、Asset/Stablecoin variants、issuer controls、pause / mint / burn / burnBlocked / metadata / permit 等能力。重点不是复制 precompile，而是抽象出 Mantle CCT 可以复用的能力语言：deterministic factory、policy slot、policy registry、role-separated issuer control、feature activation、asset/stablecoin variant split。研究需标注 B20 结论来自既有文件还是需要重新核验 Base local code，尤其是 B20Security、redeem、batchBurn、securityIdentifier 或任何 private extension 相关新信号。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1

### item-3: ERC-3643 应用层合规骨架与短期路线价值

分析 ERC-3643 / T-REX 的应用层骨架：ONCHAINID、Identity Registry、Identity Registry Storage、Claim Topics Registry、Trusted Issuers Registry、Modular Compliance、Agent roles、freeze/partial freeze/forced transfer/recovery/pause/mint/burn。研究应解释 ERC-3643 为什么适合作为 Mantle phase 1 的合规基线或集成参照，并说明它缺少 encrypted amount/balance/allowance、密文 policy check 和 confidential disclosure 的哪些部分。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1

### item-4: TIP-20 / 支付对账能力的边界复用

从 TIP-20 / TIP-403 中抽取与 CCT 相关的支付型能力：memo、ISO currency、Payment Reconciliation、policy registry、StablecoinDEX / payment lane / fee infrastructure 的启发。研究应把 TIP-20 明确定位为支付/对账参考，而不是 Mantle RWA CCT 的主架构来源；同时识别 B20 Stablecoin variant 与 TIP-20 payment metadata 之间哪些能力可以作为 phase 1 optional 或 phase 2 product extension。

- **优先级（Priority）**: medium
- **依赖（Dependencies）**: item-1, item-2

### item-5: Private Feature 新增需求定义

定义 private feature 对合规骨架的新增要求：encrypted balance、encrypted transfer amount、confidential allowance、encrypted frozen balance / frozen amount、policy check over encrypted and plain facts、auditor/regulator/issuer disclosure、freeze/recovery/force-transfer under ciphertext、wrap/unwrap 或 redeem 时的披露边界。研究必须明确每项能力的实现责任可能在 token core、hook、policy engine、observer、KMS/coprocessor、identity service 或 offchain audit workflow 中，而不是默认都进入链协议。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1, item-2, item-3

### item-6: B20 + Private Feature 阶段边界表（Phase Boundary Table）

输出 `B20 + private feature` 的 phase 1 must-have / phase 1 optional / phase 2 native-precompile boundary table。phase 1 must-have 应聚焦可用、可审计、能 PoC 的最小 CCT；phase 1 optional 应列出对产品完整性有帮助但不阻塞 MVP 的能力；phase 2 应包含 hardfork/precompile、native encrypted accounting、protocol-level policy over ciphertext、ZK/FHE proof optimizations、native bridge/redeem 等高成本能力。每个划分都必须带理由、依赖和证据来源。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-2, item-3, item-5

### item-7: Base/Mantle 代码核验边界（Code Verification Boundary）

列出哪些结论直接复用旧项目 final，哪些必须在 deep draft 前或 final 前对 local code 重新核验。Base 侧重点：B20 目录、policy/activation/factory 是否仍符合 pinned 结论，是否已有 B20Security 或 confidential/private 扩展进入主线。Mantle 侧重点：当前是否仍无自定义 precompile，硬分叉注册、op-geth/reth precompile 接入面、fraud-proof / op-program precompile 列表是否支持短期协议改动。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-2, item-6

### item-8: 设计风险、开放问题与非目标（Design Risks, Open Questions, and Non-Goals）

整理 CCT 需求边界中的风险和非目标：过度承诺 Mantle 短期复制 B20 precompile、把 ERC-3643 当作 privacy solution、忽略 FHE ACL 撤销和审计日志、忽略 DeFi/bridge/redeem 的明文需求、把 TIP-20 支付链能力照搬到 Mantle RWA、把 vendor PoC 或本地分支信号当作生产事实。输出 deep draft 必须处理的 open question backlog。

- **优先级（Priority）**: medium
- **依赖（Dependencies）**: item-5, item-6, item-7

### 必备输出表格（Required Output Tables）

Deep draft 应包含以下表格，即使 final 阶段的章节标题有所调整：

1. **合规 Token 能力 -> 机密扩展需求矩阵（Compliance Token Capability -> Confidential Extension Requirement Matrix）**

| 合规能力 | 既有标准来源 | 机密扩展需求 | 阶段目标 | 核验类别 |
|---|---|---|---|---|
| identity_kyc | ERC-3643 ONCHAINID / B20 policy list | KYC 事实可保持链下/明文，而转账金额加密；需定义哪些 claim 对 policy engine 可见 | phase_1_must | direct_reuse + new synthesis |
| transfer_policy | B20 policy scopes / ERC-3643 Modular Compliance / TIP-403 | 策略必须处理加密金额、加密 allowance、接收方状态、制裁，以及可选的加密阈值 | phase_1_must | direct_reuse + private feature analysis |
| issuer_controls | B20 RBAC / ERC-3643 Agent roles | freeze、burn、recover、forced transfer 与披露必须定义密文行为与审计日志 | phase_1_must | direct_reuse + new synthesis |
| sanctions_blacklist | B20 BLOCKLIST / TIP-403 blacklist / ERC-3643 modules | 黑名单检查可保持基于明文地址；加密金额不会免除制裁义务 | phase_1_must | direct_reuse |
| recovery | ERC-3643 recovery / B20 burnBlocked-like controls | 恢复加密余额与 allowance，且不泄露无关持有人状态 | phase_1_optional | direct_reuse + new synthesis |
| legal_metadata | ERC-1643 legacy / B20 contractURI / TIP-1026 | Token/法律文档很可能保持公开或权限化链下；不属于密文核心需求 | phase_1_optional | direct_reuse |
| payment_reconciliation | TIP-20 memo / payment infra / B20 memo | 加密转账需要在不暴露金额的前提下设计支付凭据策略；memo 隐私边界需明确 | phase_1_optional | direct_reuse + new synthesis |
| audit_privacy | compliance taxonomy + CCT rubric | 必须区分公开审计、发行方审计与监管方披露 | phase_1_must | requirements-framework reuse |

2. **B20 骨架 -> CCT 产品类比（B20 Skeleton -> CCT Product Analogy）**

| B20 组件 | 复用思路 | CCT 适配 | 不应假定 |
|---|---|---|---|
| B20Factory | 确定性 Token 创建与变体配置 | Factory 或部署器可创建合规的机密 asset/stablecoin 变体 | Mantle phase 1 需要 precompile factory |
| PolicyRegistry | 共享策略注册表与 policy ID | Policy engine 可将地址/KYC/制裁/阈值规则绑定到 Token | 策略无需隐私后端即可检视加密事实 |
| ActivationRegistry | 功能激活门控 | 产品特性开关/升级门控可分阶段上线机密功能 | Mantle hardfork 激活短期内可用 |
| RBAC | 分离 admin/mint/burn/pause/metadata 角色 | 发行方、合规官、审计方、恢复 agent、observer 角色需明确分离 | 单一全能 owner 是可接受的 |
| Policy scopes | sender/receiver/executor/mint receiver 槽位 | 在需要处扩展至 spender/allowance/auditor/disclosure/freeze 作用域 | B20 scopes 已覆盖加密 allowance 或审计方披露 |
| Asset/Stablecoin variants | 按资产类型拆分产品 | RWA/证券类资产与 stablecoin/支付变体可能有不同的隐私/对账需求 | 两类变体需要完全相同的 private feature 集 |

3. **ERC-3643 骨架 -> Private Feature 缺口（ERC-3643 Skeleton -> Private Feature Gaps）**

| ERC-3643 组件 | 解决了什么 | 对 CCT 的缺口 | 候选适配方案 |
|---|---|---|---|
| ONCHAINID | 基于 claim 的 identity/KYC | 不隐藏 Token 金额/余额；claim 隐私有限 | 复用 identity registry，由加密 Token 处理价值 |
| Identity Registry | 接收方验证 | sender/spender/auditor 策略可能需要更多作用域 | 增加 policy hook 或 registry 适配器 |
| Claim Topics / Trusted Issuers | KYC claim 信任模型 | 针对加密值的策略需要后端特定的 proof/check | claim 大体保持明文/链下，仅加密金额 |
| Modular Compliance | 业务转账规则 | 使用金额/余额阈值的规则需要加密比较或披露 | 接入 FHE/ZK/coprocessor，或回退到明文阈值 |
| Agent roles | freeze、forced transfer、recovery | 密文下的操作需要 key/披露/重加密语义 | 定义特权加密操作与日志 |

4. **B20 + Private Feature 阶段边界（B20 + Private Feature Phase Boundary）**

| 能力 | Phase 1 必备 | Phase 1 可选 | Phase 2 / 仅 native | 理由 |
|---|---|---|---|---|
| encrypted balance/amount | yes | - | 后续 native 优化 | CCT 最小要求机密账本，但未必需要 native precompile |
| confidential allowance | 类 ERC-20 UX 下为 yes | - | native allowance registry 可选 | 若余额私密而 allowance 公开，DeFi/托管的授权流程将被破坏 |
| plaintext KYC/sanctions policy | yes | - | - | 可复用 ERC-3643/B20/TIP-403 风格的地址/身份策略 |
| policy over encrypted amount | 最小阈值/限额支持 | 更丰富的自定义模块 | native 加密 policy engine | Phase 1 可依赖隐私后端 hook/coprocessor |
| auditor disclosure | yes | 更丰富的监管方工作流 | protocol disclosure registry | 机构使用需要授权可见性 |
| freeze/recovery under ciphertext | 最小 freeze 与 recovery 语义 | partial freeze 与 force-transfer | native 加密 recovery/precompile | 必须定义谁可移动或解密加密余额 |
| legal metadata | - | yes | - | 对 RWA 重要，但不属于机密核心 |
| payment reconciliation | - | yes | payment lane/native memo 基础设施 | 对 stablecoin/支付变体有用；非 CCT 最小要求 |
| native precompile | - | - | yes | Mantle hardfork/客户端成本使其归入 phase 2 |

## 字段（Fields）

| 字段 | 描述 | 适用于 |
|-------|-------------|------------|
| source_anchor | 支撑某项主张的精确文件路径、commit SHA、本地仓库路径，或 URL/访问日期 | all |
| reuse_class | direct_reuse / bounded_reuse / new_synthesis / code_verification_required / local_branch_signal / out_of_scope | all |
| compliance_capability | identity_kyc, transfer_policy, issuer_controls, sanctions_blacklist, recovery, legal_metadata, payment_reconciliation, audit_privacy | item-1, item-5, item-6 |
| architecture_layer | application_contract, precompile_protocol, policy_registry, identity_registry, privacy_backend, observer_disclosure, bridge_redeem_adapter | item-2, item-3, item-4, item-5 |
| private_feature | encrypted_balance, encrypted_amount, confidential_allowance, encrypted_policy_check, auditor_disclosure, encrypted_freeze, encrypted_recovery, confidential_redeem | item-5, item-6 |
| phase_boundary | phase_1_must_have, phase_1_optional, phase_2_native, non_goal | item-5, item-6, item-8 |
| actor_scope | holder, issuer, agent, auditor, regulator, spender/operator, policy_admin, bridge_or_redeem_agent, defi_integrator | item-1, item-5, item-6 |
| disclosure_vector | authority, trigger, payload, scope, revocability, residual_leakage, audit_log | item-5, item-6, item-8 |
| code_verification_status | not_needed_reuse_only, base_code_required, mantle_code_required, both_code_required, blocked_by_missing_spec | item-2, item-7 |
| risk_label | overcommit_precompile, privacy_not_compliance, compliance_not_privacy, acl_revocation, defi_breakage, bridge_redeem_gap, vendor_or_branch_overclaim | item-8 |

## 图示预期（Diagram Expectations）

| ID | 类型 | 描述 | 格式 | 适用于 |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy | CCT 能力栈，展示合规底座、机密账本、policy engine、issuer controls、披露/审计、bridge/redeem 与 DeFi 适配器 | mermaid | item-1, item-5 |
| diag-2 | architecture | B20 骨架映射到 CCT 适配：Factory、PolicyRegistry、ActivationRegistry、RBAC、scopes、variants 与 private feature 新增项 | mermaid | item-2, item-6 |
| diag-3 | flow | ERC-3643 转账路径加上 private feature 插入点：身份检查、modular compliance、加密金额策略、披露/审计 hook | mermaid | item-3, item-5 |
| diag-4 | comparison | 阶段边界矩阵，从 phase 1 必备到可选再到 phase 2/native，并高亮 hardfork/precompile 边界 | ascii | item-6 |
| diag-5 | flow | 代码核验决策树：旧 final 复用 vs Base 本地代码核验 vs Mantle 本地代码核验 vs 阻塞/缺少 spec | mermaid | item-7 |

## 来源要求（Source Requirements）

| ID | 类型 | 描述 | 最小数量 |
|----|------|-------------|-----------|
| src-1 | prior_research_final | 来自 `confidential-compliance-token-research` 与 `compliance-token-standards`、并在 `reference_inputs.direct_reuse` 中列出的 commit 钉定（commit-pinned）的先前 final | 7 |
| src-2 | code_analysis | 仅当主张超出 `base-b20-analysis/final.md` 或需要当前状态核验时，使用 Base 本地代码 | 1 |
| src-3 | code_analysis | 当 final 提出新的 Mantle 实现主张时，使用 Mantle 本地代码核验当前 precompile/hardfork/客户端约束 | 1 |
| src-4 | official_spec_or_primary_docs | 仅当 final 主张超出先前研究或需要更新确认时，使用 ERC-3643 / B20 / TIP-20 / 相关官方 spec | 2 |
| src-5 | issue_record | 当引用流程状态或依赖验收时，使用 WHI-269 及依赖 `requirements-framework` 的 Multica issue/dispatch 上下文 | 1 |

## 补丁日志（Patch Log）

| 轮次（Round） | 操作（Action） | 目标（Target） | 原因（Reason） | 来源（Source） |
|-------|--------|--------|--------|--------|
