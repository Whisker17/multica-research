---
topic: "Mantle 轻量级集成路线与 PoC 计划"
project_slug: "confidential-compliance-token-research"
topic_slug: "integration-roadmap"
github_repo: "Whisker17/multica-research"
round: 1
status: approved

artifact_paths:
  outline: "confidential-compliance-token-research/outlines/integration-roadmap.md"
  draft: "confidential-compliance-token-research/research-sections/integration-roadmap/drafts/round-{n}.md"
  final: "confidential-compliance-token-research/research-sections/integration-roadmap/final.md"
  index: "confidential-compliance-token-research/research-sections/_index.md"

scope: |
  把 WHI-272 协议设计转化为 Mantle 可执行的轻量集成路线与 PoC 计划。覆盖：(1) 最小
  PoC 成功标准，包括 KYC/policy、mint、confidential transfer、audit disclosure、
  freeze/recovery 的最小闭环；(2) Phase 0/1 contract + external backend/SDK 集成路线，
  默认不改 Mantle 执行客户端；(3) Phase 2 native B20-like precompile / PolicyRegistry
  precompile 评估；(4) 合约、SDK、wallet、indexer、auditor tooling、KMS/operator、
  bridge、docs、security review 工程改动面；(5) p50/p95/p99 latency、encrypted op
  cost、burst、audit evidence、monitoring、failure recovery 等生产化观测项；(6) 风险
  门槛与停止条件；(7) 验证计划；(8) 一页路线图与 PoC checklist。
audience: "Mantle 小型协议/工程团队、RWA/机构产品负责人、合规与安全评审、Research Review Agent、后续 Technical Writer"
expected_output: |
  0-3 / 3-6 / 6-12 月阶段路线图，PoC 成功标准，工程改动面分析，性能与生产化观测项，
  风险门槛与停止条件，验证计划，以及面向工程团队的一页路线图和可执行 PoC checklist。

revision_metadata:
  created_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-24T13:15:19Z"
  last_modified_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-24T13:15:19Z"

multica_issue_id: "cf06b8fa-ed51-4b1e-8f3f-bfcd2f76197a"
report_issue_id: "7b29e4a8-01eb-4cbf-9b59-8e363f9a40e4"
branch_name: "research/confidential-compliance-token-research/integration-roadmap"
base_commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
dependencies:
  - "mantle-protocol-design"
  - "zama-confidential-rwa"
  - "compliance-token-private-extension"
language: "zh-CN"
mode: "single-issue"

reference_inputs:
  direct_reuse:
    - path: "confidential-compliance-token-research/research-sections/mantle-protocol-design/final.md"
      commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
      role: "WHI-272 protocol design；六模块 CCT 架构、接口、状态、流程、backend adapter、risk gates"
    - path: "confidential-compliance-token-research/research-sections/zama-confidential-rwa/final.md"
      commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
      role: "Zama / ERC-7984 / OZ RWA 集成细节；Mantle lightweight integration 表；Gateway/KMS/ACL 风险"
    - path: "confidential-compliance-token-research/research-sections/compliance-token-private-extension/final.md"
      commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
      role: "B20 + private feature phase boundary；backend maturity gate；Mantle local code verification boundary"
    - path: "confidential-compliance-token-research/research-sections/route-comparison/final.md"
      commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
      role: "主推 ERC-3643 + ERC-7984/OZ overlay；Inco/VOSA/Fhenix backup/reference buckets；native B20 phase 2 boundary"
    - path: "confidential-compliance-token-research/research-sections/requirements-framework/final.md"
      commit: "0a058bd286ab95d3a1ff7b76421a9e8627b675b4"
      role: "CCT rubric、Mantle lightweight constraints、Inco framework 与 Optalysys 证据分类、engineering delta checklist"
  local_code_verification_target:
    path: "/Users/whisker/Work/src/networks/mantle"
    purpose: "仅当 deep draft 对 Mantle precompile/hardfork/current-client surface 作当前事实声明时使用；引用必须标注 repo path、commit SHA 和文件路径"
---

# 研究大纲：Mantle 轻量级集成路线与 PoC 计划

本 outline 的目标不是重新设计协议，而是把已接受的 WHI-272 CCT 协议设计压成一个可执行、可验收、可停止的 Mantle PoC / pilot roadmap。核心路线必须保持轻量：Phase 0/1 默认是 **application contracts + external confidential backend / SDK / disclosure tooling**，不要求 Mantle 执行客户端、precompile、hardfork 或新 chain。Native B20-like precompile、PolicyRegistry precompile、native encrypted accounting 和 protocol disclosure registry 只进入 Phase 2 评估项。

Deep draft 的审查重点是：PoC 是否能演示最小闭环；路线是否足够小到 Mantle 小工程团队能执行；工程改动面是否完整；性能/生产化观察项是否能支撑 go/no-go；风险门槛是否能阻止研究结论变成不可控工程承诺。

## 条目（Items）

### item-1: 最小 PoC 成功标准与演示闭环

定义 Mantle CCT PoC 的最小成功标准，避免一开始把 production CCT、native precompile、full private DeFi、private identity 或 cross-chain private settlement 混入 MVP。PoC 必须能演示 KYC/policy onboarding、confidential mint、confidential transfer、scoped audit disclosure、freeze/recovery 或明确写入不覆盖项。研究应把成功标准拆成 must-pass、should-pass、explicit non-goal，并为每个标准写出可观察证据、验收方式和失败处理。

所需的 PoC 成功标准表：

| 能力 | 最小 PoC 标准 | 所需证据 | 除非明确加入否则不在范围内 |
|---|---|---|---|
| KYC / 策略 | 通过 ERC-3643 风格的身份/策略基座或等价 adapter 校验收款方与付款方资格 | 通过与失败的转账用例；策略配置快照；来源锚点 | 私密身份、完全加密的 KYC 事实 |
| Mint | 发行方可向合格持有人 mint 加密金额 | 交易/日志证据、加密余额 handle、角色证明 | 原生 mint precompile |
| 机密转账 | 合格持有人可转移加密金额而不泄露金额/余额明文 | 转账 trace、转账前后的加密 handle、无明文金额事件 | 隐藏地址图谱、时序、事件存在性 |
| 审计披露 | 授权的 auditor/issuer/regulator 流程可披露受限范围 payload 并记录 request/grant/result 引用 | 披露请求、批准、decrypt/re-encrypt 证据、过期/撤销日志 | 全历史 viewing key |
| 冻结/恢复 | 定义并可演示最小的 freeze 或 recovery 仪式，或以法律理由明确延后 | freeze/recovery 测试、管理员角色、审计轨迹、失败语义 | 未记录的发行方超级权限 |
| 失败/降级模式 | backend 宕机、披露拒绝、策略失败和畸形 proof 均有文档化结果 | 手动 runbook、失败测试或 mock 宕机场景 | 生产事件自动化 |

- **优先级（Priority）**: high
- **依赖（Dependencies）**: none

### item-2: Phase 0/1 轻量集成路线：contracts、backend、SDK、demo

围绕 contracts 加上 external confidential backend 与 SDK，设计具体的 0-3 月和 3-6 月路线，不改 Mantle 客户端。Phase 0 应为架构 spike 与 backend 就绪验证；Phase 1 应为带有指定 backend 路径、disclosure registry、最小 wallet/indexer UX 和 demo 脚本的窄 PoC / testnet pilot。该路线必须保持 WHI-272 的 backend 可替换性：公开接口使用加密 handle/proof/capability flag，而不是 Zama 的 `euint`、Inco 的 handle 形状、VOSA 的 proof 编码或 native precompile selector。

所需的 Phase 0/1 路线表：

| 阶段 | 时间窗口 | 目标 | 交付物 | Go/no-go 门槛 |
|---|---|---|---|---|
| Phase 0 | 0-3 个月 | 可行性 spike 与设计冻结 | PoC spec、backend 选型备忘录、adapter 接口、威胁模型、来源 trace map、mock disclosure service | 指定 backend 支持路径或界定清晰的非 Mantle PoC 目标 |
| Phase 1a | 3-6 个月 | 带最小闭环的 testnet PoC | Contracts、SDK demo、KYC/policy fixture、mint/transfer/disclosure/freeze 测试、dashboard 指标 | Demo 通过 checklist，未发现 hardfork 依赖 |
| Phase 1b | 3-6 个月 | Pilot 就绪评估 | Security review 范围、operator runbook、latency/cost 度量、wallet/indexer pilot UX、incident drill | 达到生产门槛或路线维持为仅 PoC |

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1

### item-3: Phase 2 原生路线评估：B20-like 与 PolicyRegistry precompile

定义如何仅在已有 PoC 证据后才评估 Mantle 原生集成。本条目不应把原生路线作为 Phase 1 工作来提议；它应明确何时重新审视 B20-like precompile、PolicyRegistry precompile、native encrypted accounting、native disclosure registry、native bridge/redeem adapter 或更深的链层集成。若 deep draft 引用 Mantle 本地代码以论证 precompile 或 hardfork 可行性，必须在 `/Users/whisker/Work/src/networks/mantle` 下核实当前 repo path + commit SHA + 文件路径，并把代码层接线与产品/治理排期区分开。

所需的 Phase 2 评估表：

| 原生选项 | 评估触发条件 | 所需证据 | 预期成本面 | 默认处置 |
|---|---|---|---|---|
| B20-like token precompile | PoC 证明存在需求且 app 层 gas/UX 成为瓶颈 | Mantle op-geth/reth/revm precompile surface、B20 类比、安全 spec | 双客户端执行改动、fork 激活、审计、fraud-proof / op-program review | 仅 Phase 2 |
| PolicyRegistry precompile | 策略评估稳定、通用且被反复使用 | 策略语义、升级规则、scope 模型、本地代码可行性 | 协议治理、兼容性、storage/API 稳定性 | 仅 Phase 2 |
| Native encrypted accounting | 外部 backend latency/cost 不可接受但 CCT 需求已验证 | 密码学 backend spec、precompile/API 设计、密钥治理、客户端集成 | 高密码学 + 协议 + 运维成本 | 长期研究 |
| Protocol disclosure registry | App 层 disclosure 日志被证明有用但不充分 | 法律/审计需求、隐私影响、撤销模型 | 治理与数据留存承诺 | phase 2 候选 |
| Native bridge/redeem adapter | Pilot 需要链层结算集成 | bridge/redeem 法律流程、明文边界、失败恢复 | bridge/安全评审与运营责任 | 单独提案 |

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1, item-2

### item-4: 工程改动面与 ownership map

梳理一个 Mantle 小团队实际需要拥有、集成或外包的每一个工程面。最终输出必须覆盖 contracts、SDK、wallet、indexer/explorer、auditor tooling、KMS/operator、bridge/redeem、docs/runbooks、security review 以及 governance/roles。Inco confidential ERC20 framework 仅可用作 PoC/test/interface 灵感来源，绝不可作为生产安全证据或未经评审的代码复用。

所需的工程改动面表：

| 改动面 | Phase 0/1 工作 | Owner / operator | 测试产物 | 生产阻塞项 |
|---|---|---|---|---|
| Contracts | token、policy、disclosure、issuer control、backend adapter、wrapper/redeem stub | Mantle app team / issuer integrator | 单元/集成测试；ABI 与升级评审 | 审计、治理、升级风险 |
| SDK / backend adapter | 加密输入生成、decrypt 请求、grant/revoke、capability flag | backend partner 或 Mantle 集成团队 | SDK demo、mock 与真实 backend 一致性测试 | backend 支持路径与 SLA |
| Wallet / custody UX | 加密金额、查看/解密余额、批准披露、显示策略失败 | wallet/custody partner | 手动 demo 与 UX 验收脚本 | 不可用的批准/解密流程 |
| Indexer / explorer | 展示加密活动、policy/disclosure 日志、无明文金额泄露 | indexer/explorer team | 已索引事件样本与 dashboard | 缺失审计证据或误导性 UI |
| Auditor tooling | request/grant/result 跟踪、证据导出 | issuer/auditor operator | disclosure 报告样本 | 无受限范围证据或缺撤销叙事 |
| KMS / operator | 密钥仪式、threshold/decrypt 治理、宕机响应 | backend provider、issuer 或 operator set | runbook 与 incident drill | 密钥治理不可接受 |
| Bridge / redeem | 明确的明文结算边界与回退 | issuer/custodian/bridge provider | redeem/unshield demo 或延后理由 | 无合法结算路径 |
| Docs / security review | 部署指南、威胁模型、失败模式、审计范围 | project lead + security | review package | 安全评审对 Phase 1 而言过大 |

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-2

### item-5: 性能、成本与生产化观测计划

把性能与运维转化为可度量的 PoC 输出。研究应为 transfer、policy check、disclosure、freeze/recovery、redeem/unshield、加密输入生成、backend decrypt 和 indexer finality 定义 p50/p95/p99 latency 目标或实测值。Optalysys 可用于构建 FHE throughput/data-movement/hardware acceleration 相关问题的框架，但它必须保持为性能/生产化参考与厂商叙事，而非任何 Mantle CCT 路线满足 SLA 的证明。

所需的可观测性表：

| 指标组 | 指标 | 度量方法 | 在决策中的用途 |
|---|---|---|---|
| 用户侧延迟 | mint、transfer、policy check、disclosure request、balance view 的 p50/p95/p99 | testnet 脚本与 dashboard | UX go/no-go 与 wallet 需求 |
| Backend 延迟 | encrypted op latency、decrypt/re-encrypt 时间、KMS quorum 时间、Gateway/coprocessor 重试时间 | backend 日志与合成探针 | backend 成熟度门槛 |
| 成本 | gas、backend 费用、operator 成本、监控成本、审计/评审成本 | 交易 trace 与厂商/operator 估算 | 预算与生产可行性 |
| Burst / 可靠性 | 并发转账、decrypt burst、policy update burst、宕机恢复时间 | 负载测试与失败演练 | pilot 就绪度 |
| 审计证据 | disclosure 日志、policy 日志、管理员操作日志、result hash、留存/导出 | auditor 报告样本 | 合规验收 |
| 监控 | health check、告警、事件索引滞后、卡住的 decrypt 检测 | dashboard spec | 事件响应 |

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-2, item-4

### item-6: 风险门槛、停止条件与降级路线

定义会让项目停止、保持仅 PoC 模式或降级为 reference/Phase 2 研究的明确风险门槛。Deep draft 必须区分阻塞性生产门槛与 PoC 可接受的注意事项。它应涵盖 backend 的 Mantle 支持、KMS/disclosure 治理、vendor lock-in、性能、wallet UX、合规披露充分性、bridge/redeem 缺口、安全评审范围以及意外的 hardfork/precompile 依赖。

所需的停止条件矩阵：

| 风险门槛 | 停止条件 | 降级路径 | 所需证据 |
|---|---|---|---|
| Backend 可用性 | 无 Mantle 支持、无自托管路径或无界定清晰的非 Mantle PoC 目标 | 仅作参考或采用对齐 Base 的 PoC | backend 声明、部署测试或明确的非 Mantle 范围 |
| 披露治理 | grant/revoke/log 权限不清或历史访问不可接受 | pilot 前重新设计 disclosure registry | 权限矩阵与审计日志样本 |
| 性能/SLA | p95/p99 或失败率使 wallet/custody 流程不可用 | 仅 PoC；延后生产 | 实测 benchmark，而非厂商声称 |
| Vendor lock-in | 公开接口泄露 backend 专属 type/API | 重构 adapter 边界 | ABI/API 评审 |
| 合规充分性 | audit disclosure 或 policy proof 无法满足 issuer/regulator 的最低要求 | 停止生产路径 | 合规评审备忘录 |
| Wallet/UX 负担 | 用户/operator 无法可靠完成 encrypt/decrypt/disclosure 流程 | 仅 custody pilot 或停止 | 手动验收与错误日志 |
| Hardfork 依赖 | Phase 1 路径需要 Mantle 客户端改动/precompile | 转入 Phase 2 原生轨道 | 本地代码核实与架构决策 |
| 安全范围 | 审计范围超出小团队能力或需要未审计的 PoC 代码 | 收窄 PoC 或停止 | 安全评审估算 |

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-3, item-4, item-5

### item-7: 验证计划、source traceability 与成本估算

明确 deep draft 与后续 PoC 应如何被验证。计划必须包含 unit tests、integration tests、手动 demo 验收、对抗性评审、source traceability、仅在需要时的 Mantle 本地代码核实、成本估算和证据分类。Final section 中每个实质性结论都必须附上 path/URL 和 commit SHA、version 或 access date；来源缺口应作为阻塞项或注意事项处理，而非用推断填补。

所需的验证计划表：

| 验证层 | 验证内容 | 产物 |
|---|---|---|
| Source traceability | 每个结论映射到 local final path + commit SHA、官方 URL + access date，或 local repo path + commit SHA + 文件路径 | 证据 map |
| 合约单元测试 | 策略 pass/fail、加密转账路径、disclosure registry、issuer 角色、freeze/recovery 语义 | 测试清单与通过标准 |
| 集成测试 | SDK 加密输入、backend decrypt/re-encrypt、indexer 事件、wallet/custody 流程 | testnet 脚本 |
| 手动验收 | mint -> confidential transfer -> audit disclosure -> freeze/recovery demo | checklist 与截图/日志引用 |
| 对抗性评审 | 路线是否真正轻量、原生路线是否正确分阶段、停止条件是否可执行 | review response package |
| 成本估算 | contract/audit/backend/operator/wallet/indexer/security/doc 工作量 | 量级粗估表 |
| 本地代码核实 | 仅当作出当前 Mantle hardfork/precompile 声明时 | repo path、commit SHA、文件路径、检索词 |

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1, item-2, item-3, item-4, item-5, item-6

### item-8: 一页路线图与 PoC checklist 打包

产出最终面向读者的交付包：一页路线图与详细 PoC checklist，供 Mantle 工程/产品用于决定是否启动。路线图应概括 0-3 / 3-6 / 6-12 月阶段、owners、deliverables、gates 与降级路径。Checklist 应足够具体，可作为项目 kickoff 产物来执行，而不仅是叙事性结论。

所需的输出交付包：

| 输出 | 内容 | 验收条件 |
|---|---|---|
| 一页路线图 | 阶段时间线、deliverables、owners、go/no-go gates、Phase 2 触发条件 | 无需前置章节即可读懂 |
| PoC checklist | 横跨 contracts、SDK/backend、wallet/indexer、auditor tooling、KMS/operator、bridge/redeem、docs/security 的任务 | 每行有 owner、证据、status、blocker |
| 决策备忘录 | start / narrow / stop / defer-native 建议 | 与实测门槛挂钩 |
| 注意事项框 | 本 PoC 未能证明的内容 | 防止生产过度宣称 |

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1, item-2, item-3, item-4, item-5, item-6, item-7

## 字段（Fields）

| 字段 | 描述 | 适用于 |
|-------|-------------|------------|
| source_anchor | 支撑每个声明的精确本地文件路径加 commit SHA、外部 URL 加 access date/version，或 local repo path 加 commit SHA 加文件路径 | all |
| reuse_class | direct_reuse, bounded_reuse, new_synthesis, code_verification_required, vendor_reference, engineering_poc_only, blocker_gap | all |
| phase_window | 0_3_months, 3_6_months, 6_12_months, phase_2_native, out_of_scope | all |
| chain_change_class | no_chain_change, app_integration, sidecar_operator_dependency, bridge_or_redeem_service, client_or_hardfork_required, unknown | item-2, item-3, item-4 |
| poc_success_signal | 每个 PoC 标准的可观察 pass/fail 证据 | item-1, item-2, item-7, item-8 |
| engineering_surface | contract, sdk_backend, wallet_custody, indexer_explorer, auditor_tooling, kms_operator, bridge_redeem, docs_security, governance_roles | item-4, item-8 |
| performance_metric | p50, p95, p99, encrypted_op_cost, gas_cost, burst_capacity, recovery_time, indexing_lag, audit_export_time | item-5 |
| risk_gate | backend_support, disclosure_governance, performance_sla, vendor_lock_in, compliance_sufficiency, wallet_ux, hardfork_dependency, security_scope | item-6 |
| validation_method | unit_test, integration_test, manual_demo, adversarial_review, source_trace, local_code_check, cost_estimate, incident_drill | item-7 |
| checklist_status | not_started, planned, in_progress, passed, failed, deferred, blocked, non_goal | item-8 |

## 图示预期（Diagram Expectations）

| ID | 类型 | 描述 | 格式 | 适用于 |
|----|------|-------------|--------|------------|
| diag-1 | timeline | 0-3 / 3-6 / 6-12 月路线图，展示 Phase 0 可行性、Phase 1 PoC/pilot 和 Phase 2 原生评估触发条件。必须展示各阶段之间的 stop/downgrade gate。 | mermaid | item-2, item-3, item-6, item-8 |
| diag-2 | flow | 最小 PoC 流程，从 KYC/policy onboarding 经 mint、confidential transfer、audit disclosure、freeze/recovery 到证据捕获。标注 plaintext、ciphertext 与 disclosure 边界。 | mermaid | item-1, item-7 |
| diag-3 | architecture | 轻量 Phase 0/1 部署架构：contracts、backend adapter、confidential backend/Gateway/KMS 或 TEE/operator、SDK、wallet、indexer、auditor tooling、bridge/redeem service。标注默认不改 Mantle 客户端。 | mermaid | item-2, item-4, item-5 |
| diag-4 | comparison | 工程改动面矩阵，含 owner、work item、test artifact、blocker 和 phase。 | ascii | item-4, item-8 |
| diag-5 | decision | 风险门槛与停止条件决策树：continue、narrow PoC、defer production、move to Phase 2 native 或 stop。 | mermaid | item-6 |
| diag-6 | checklist | 一页 PoC checklist 表，适合 Technical Writer 转换为 `confidential-compliance-token-research/report/poc-checklist.md`。 | ascii | item-8 |

## 来源要求（Source Requirements）

| ID | 类型 | 描述 | 最小数量 |
|----|------|-------------|-----------|
| src-1 | prior_research_final | 来自当前 `origin/main` 的 commit 锚定直接输入：`mantle-protocol-design/final.md`、`zama-confidential-rwa/final.md` 和 `compliance-token-private-extension/final.md`，均在 commit `0a058bd286ab95d3a1ff7b76421a9e8627b675b4`。 | 3 |
| src-2 | supporting_prior_research | 使用 `requirements-framework/final.md` 和 `route-comparison/final.md` 获取 rubric、Inco/Optalysys 分类、engineering delta 和 route bucket 规则。引用路径和 commit SHA。 | 2 |
| src-3 | code_analysis | 仅当 draft 作出当前 precompile/hardfork/client-surface 声明时才做 Mantle 本地 repo 分析。所需引用形态：`/Users/whisker/Work/src/networks/mantle` + subrepo commit SHA + 文件路径 + 检索/检视方法。 | 1 |
| src-4 | official_backend_docs | 所选 backend 与标准边界的官方文档/规范：ERC-7984、ERC-3643、OpenZeppelin Confidential Contracts、Zama docs、Inco docs 或其他所选 backend 文档。需包含 access date 或 version。 | 4 |
| src-5 | performance_reference | Optalysys 与 backend 性能/SLA 材料仅可用于构建 latency/throughput/production 问题的框架。厂商声称必须标注为 vendor_reference 或 self_report，而非 benchmark 证据。 | 2 |
| src-6 | engineering_poc_reference | Inco confidential ERC20 framework 或可比代码仅可用作工程 PoC/test/interface 灵感。若使用，需引用 repo commit 并明确声明未审计/非生产状态。 | 1 |
| src-7 | issue_record | Multica issue 描述与 Orchestrator dispatch，用于 scope、expected output、Agent Directory 和验收标准。 | 1 |

## 修订日志（Patch Log）

| 轮次 | 操作 | 目标 | 原因 | 来源 |
|-------|--------|--------|--------|--------|

## 验证验收标准（Verification Acceptance Criteria）

| ID | 标准 | 适用于 |
|----|-----------|------------|
| vc-1 | 定义一个最小可演示的 PoC 闭环，覆盖 KYC/policy、mint、confidential transfer、audit disclosure 和 freeze/recovery 或明确延后。 | item-1 |
| vc-2 | Phase 0/1 路线默认采用 contracts + external backend/SDK/services，且不要求 Mantle hardfork、执行客户端改动或 precompile。 | item-2 |
| vc-3 | Native B20-like precompile、PolicyRegistry precompile、native encrypted accounting 和更深的链层集成均被视为仅 Phase 2 评估，并附证据要求与触发条件。 | item-3 |
| vc-4 | 工程改动面覆盖 contracts、SDK、wallet/custody、indexer/explorer、auditor tooling、KMS/operator、bridge/redeem、docs、governance 和 security review。 | item-4 |
| vc-5 | 性能/生产计划包含 p50/p95/p99 latency、加密操作成本、gas/backend/operator 成本、burst 行为、审计证据、监控和失败恢复。 | item-5 |
| vc-6 | 停止条件和降级路径足够明确，能防止 PoC 结果被宣传为生产就绪。 | item-6 |
| vc-7 | 验证计划包含测试、手动 demo、对抗性评审、source traceability、成本估算，以及针对 Mantle hardfork/precompile 声明的本地代码核实规则。 | item-7 |
| vc-8 | 产出一页路线图和可执行 PoC checklist，含 owner/evidence/status/blocker 字段。 | item-8 |
| vc-9 | Inco framework 被分类为仅工程 PoC/参考，Optalysys 被分类为仅性能/生产化参考。 | item-4, item-5, item-7 |
| vc-10 | Final section 中每个实质性结论都有 path/URL 和 commit SHA、version 或 access date。 | all |
