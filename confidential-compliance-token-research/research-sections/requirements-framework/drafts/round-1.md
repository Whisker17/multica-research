---
topic: "建立 Confidential Compliance Token 需求框架与证据复用地图"
project_slug: "confidential-compliance-token-research"
topic_slug: "requirements-framework"
github_repo: "Whisker17/multica-research"
multica_issue_id: "7d7fa951-8160-4b03-a7ae-8ff1a6a9664c"
branch_name: "research/confidential-compliance-token-research/requirements-framework"
round: 1
status: "draft"
language: "zh-CN"
mode: "single-issue-lightweight"
artifact_paths:
  outline: "confidential-compliance-token-research/outlines/requirements-framework.md"
  draft: "confidential-compliance-token-research/research-sections/requirements-framework/drafts/round-1.md"
  final: "confidential-compliance-token-research/research-sections/requirements-framework/final.md"
  index_proposal: "embedded in this draft; Research Agent must not write _index.md"
draft_metadata:
  created_by: "Deep Research Agent"
  created_at: "2026-06-24"
  outline_commit: "5f531467495adee4c0974599172a4dd7c2ab2b00"
  outline_approval: "outline-approved by Orchestrator dispatch/review comments before deep-draft dispatch 675bdd5c-ab35-4a75-a812-7a28b3c16af7"
  outline_frontmatter_caveat: "The outline file still says status: candidate; this draft treats the Orchestrator approval verdict as authoritative squad state."
  items_covered:
    - "item-1 requirements and terminology"
    - "item-2 capability model"
    - "item-3 unified rubric"
    - "item-4 evidence reuse map"
    - "item-5 candidate layering and reference classification"
    - "item-6 Mantle lightweight constraints"
    - "item-7 project index proposal"
    - "item-8 gap register"
  mandatory_review_carry_forward:
    - "Soft-input class instantiated with concrete observed M2/M3 items: WHI-263 in_progress, WHI-264 todo, plus category rule for future/incomplete M2/M3 outside WHI-254..261."
    - "Direct reuse citations use per-file last-modifying commits instead of a shared snapshot pin."
    - "Evidence citations do not rely on evm-privacy-research/research-sections/_index.md because that index is stale/incomplete in this branch context."
---

# 建立 Confidential Compliance Token 需求框架与证据复用地图

## Executive Summary

Confidential Compliance Token（下称 **CCT**）不是普通 privacy token，也不是普通 compliance token 的改名。本文将 CCT 定义为：面向机构链 / private RWA 场景的资产 token 需求框架，在一个 token 生命周期内同时满足 **合规资产发行与控制**、**金额/余额等账本隐私**、**授权披露与审计**、**桥接/赎回/DeFi 互操作**，并且优先采用 Mantle 可接受的轻量集成方式。

核心结论：

1. **CCT 的最小产品边界是“合规 token + confidential accounting + selective disclosure”。** 普通 privacy token 只回答“公众看不到什么”；普通 compliance token 只回答“谁能交易、谁能冻结、谁能恢复”；CCT 必须同时回答“谁可以在什么条件下看见被隐藏的数据，以及这个披露行为如何被审计”。
2. **Mantle 的短期基线应继承合规 token 项目的“ERC-3643 先行、precompile 远期评估”策略，但把 privacy layer 作为单独评估面。** 合约级合规可以快速 PoC；协议 precompile 仍受硬分叉窗口、双客户端实现和 fraud-proof 一致性约束。
3. **ERC-7984 更适合作为 confidential token 接口锚点，而不是完整 CCT 方案。** 它强覆盖金额/余额隐私，但不隐藏地址、交易图、业务逻辑或订单流；合规能力主要来自 OpenZeppelin Confidential Contracts 的 ObserverAccess / Restricted / Freezable / Rwa / Hooked / Wrapper 等扩展，并带有 FHE ACL 撤销性与 trusted hook 风险。
4. **Inco confidential ERC20 framework 只能归为工程 PoC 参考。** 该仓库可复用 wrapper、delegated viewing、transfer rule、Identity 合约的工程形状，但 README 明确为 unaudited proof of concept；不得作为生产成熟度或审计安全证据。
5. **Optalysys 只能归为 FHE 性能与生产化参考。** 其 RWA privacy scaling、photonic acceleration、confidential RWA tokenisation 页面可作为 FHE SLA / hardware acceleration / productionization 背景输入，不能当作 token 标准、合规模型或 Mantle 集成方案证据。
6. **后续研究应按 9 个 section 组织。** 本 draft 给出 `_index.md` 行提案，但遵守 Research Agent 边界，不直接写 `_index.md`。

本 draft 已落实 outline review 的三项 carry-forward：soft input 具体化、按文件 pin evidence commit、避免依赖 stale `evm-privacy-research/research-sections/_index.md`。

## Item Findings

### item-1: 需求拆解、术语口径与 CCT 边界

#### 1.1 Canonical Definition

**Confidential Compliance Token**：一种面向受监管资产或机构资产流转的 token 设计框架，在标准 ERC-20 / ERC-3643 / ERC-7984 / wrapper / coprocessor / policy registry 等不同实现层之间建立共同评估口径。它必须在 token 生命周期内同时处理：

- 合规资产生命周期：发行、KYC/AML 准入、转账限制、冻结、强制转移、恢复、赎回。
- Confidential accounting：金额、余额、冻结余额、子账户或相关账务字段对公众不可见。
- Selective disclosure：持有人、发行人、审计员、监管方或智能合约在明确授权与触发条件下查看特定数据。
- Auditability：公众、发行人、审计员、监管方分别能验证哪些事实；披露与权限变更是否有可追溯日志。
- Mantle lightweight integration：尽量不要求 Mantle 新链、资产新桥、全节点隐私网络或硬分叉。

#### 1.2 与普通 privacy token / compliance token 的区别

| 类型 | 主要目标 | 典型能力 | 关键缺口 | CCT 要求的增量 |
|---|---|---|---|---|
| 普通 privacy token | 隐藏交易金额、余额、身份或交易图 | shielded pool、confidential transfer、stealth address、viewing key | 常缺 issuer controls、KYC gate、强制干预、监管披露与发行方审计 | 加入合规生命周期、发行方/监管方角色、选择性披露和审计模型 |
| 普通 compliance token | 控制谁能持有/交易，满足证券/RWA 合规 | ERC-3643 identity、transfer policy、freeze/recover、RBAC、文档管理 | 链上金额、余额、交易图通常公开 | 加入 confidential accounting、隐私后端、披露向量和泄露边界 |
| CCT | 在机构/RWA 场景同时满足隐私与合规 | 合规控制 + confidential accounting + selective disclosure + auditability + bridge/redeem | 需要处理 ACL 撤销、性能、DeFi 兼容、运维信任、监管可解释性 | 本项目的评估对象 |

#### 1.3 必须回答的问题

| 问题 | CCT 口径 | 必须输出的判断 |
|---|---|---|
| 为什么做？ | Mantle 想服务 institutional blockchain / private RWA，需要资产在公共或半公共执行环境中避免暴露交易金额、余额和业务状态，同时保留监管与发行方控制。 | 隐私是否解决机构采用障碍，还是只提供“看不见金额”的叙事功能。 |
| 为谁做？ | 发行方、托管方、机构投资者、合规团队、审计员、监管方、DeFi 集成方、桥/赎回服务。 | 每类 actor 的读写权限和信任假设必须分开。 |
| 要隐藏什么？ | P0：金额、余额、冻结余额、赎回金额；P1：子账户身份、KYC 属性、仓位；P2：业务逻辑/合约状态；通常不隐藏 token 元数据、发行方角色、交易存在性。 | 隐藏对象必须映射到 R1/R2/R3/R4/R5/R8，而不是笼统写“private”。 |
| 谁能披露？ | 可由 key-holder、issuer/agent、auditor、regulator、smart-contract policy、observer/notary、KMS/coprocessor 流程触发。 | 必须记录 authority、trigger、payload、scope、revocability、leakage。 |
| 如何合规？ | 事前 gate（KYC/AML/allowlist）、事中 policy（transfer/freeze/limit）、事后 audit（披露和日志）、极端干预（force transfer/recovery/redeem）。 | “加密”不能替代 compliance；“可披露”也不能替代可审计。 |
| 什么叫轻量？ | 不需要新 L1/L2/L3/独立 VM；不需要新资产桥；不要求 Mantle 集成方运维 sequencer/prover/DA 全节点；不要求 Mantle 硬分叉。 | 合约、wrapper、observer、external coprocessor、sidecar 可作为轻量候选；precompile 与独立链默认非轻量或中量以上。 |

#### 1.4 术语控制表

| 术语 | 本项目使用口径 | 禁止/避免的口径 |
|---|---|---|
| `confidential accounting` | 金额、余额、冻结余额、供应量或账务字段以 encrypted handle / commitment / offchain encrypted state 表示，公众无法读明文。 | 把地址匿名、交易图隐藏、业务逻辑隐私全部混称为 accounting。 |
| `compliance policy` | 对持有人、发送方、接收方、operator、mint receiver 等维度做准入和转账判定。 | 只把 sanctions/blocklist 叫 compliance。 |
| `issuer controls` | 发行方或 agent 可执行 mint/burn/pause/freeze/block/recover/force-transfer/redeem 等动作。 | 把 issuer controls 说成去中心化隐私能力。 |
| `selective disclosure` | 6 维向量：authority、trigger、payload、scope、revocability、leakage。 | 单个“viewing key”标签不足以表达合规披露。 |
| `auditability` | 不同观察者能验证不同事实，且披露/权限/合规动作有可追踪记录。 | 只要链上有 event 就等于审计充分。 |
| `bridge/redeem` | confidential token 与底层资产、ERC-20、L1/L2 bridge、现金/基金份额赎回之间的退出路径。 | 只讨论 mint/transfer，不回答最终资产流出。 |
| `DeFi composability` | 钱包、DEX、lending、custody、oracle、risk engine、indexer 对 encrypted value 的适配方式。 | 默认 ERC-20 DeFi 可以直接使用加密金额。 |

### item-2: CCT 能力模型

能力模型分为 **must-have**、**should-have**、**optional/route-specific** 三类，并标注可由 token core、adapter、policy registry、observer、external coprocessor 或 offchain compliance infra 提供。

| Capability | 必要性 | Token core / 外部依赖 | 最低验收口径 | 主要复用证据 |
|---|---|---|---|---|
| confidential_accounting | must-have | Token core + privacy backend | 公众不可读 transfer amount、balance、confidential frozen balance；总供应量是否隐藏必须显式说明。 | ERC-7984 final; confidential-coprocessor final |
| compliance_policy | must-have | Token core 或 policy registry | 能表达 KYC/AML、allow/block list、发送方/接收方/执行方/铸造接收方策略，失败语义可审计。 | compliance final; B20 final; ERC-3643 strategy |
| issuer_controls | must-have | Token core + AccessControl/RBAC | mint/burn/pause/freeze/block/recover/force-transfer/redeem 权限、绕过条件和日志必须明确。 | compliance final; ERC-7984 Rwa analysis |
| selective_disclosure | must-have | ACL / observer / viewing key / regulator workflow | 按 6 维向量描述；不能只写“有 viewing key”。历史权限撤销必须单列。 | privacy framework final; ERC-7984 final; coprocessor final |
| auditability | must-have | Events + disclosure logs + offchain audit trail | 明确 public audit sees vs private auditor sees vs regulator sees；记录权限变更与披露行为。 | compliance final; privacy framework final |
| bridge_redeem | should-have | Wrapper / bridge adapter / issuer redeem agent | wrap/unwrap、bridge mint/burn、赎回金额披露、失败/force-exit 路径明确。 | B20 bridge/redeem analogy; ERC-7984 wrapper; Inco PoC |
| defi_composability | should-have | Adapter / oracle / risk engine / wallet/indexer | 说明 DEX/lending/custody 需要哪些明文、密文比较或选择性披露；列出会破坏的 ERC-20 假设。 | ERC-7984 final; confidential-coprocessor final |
| business_state_privacy | optional/route-specific | Coprocessor / TEE / privacy group | 若目标超过 token ledger，需要隐藏合约逻辑和业务状态；否则标为 out of scope。 | privacy framework; EEA benchmark; coprocessor final |
| order_flow_privacy | optional/future | encrypted mempool / sequencer policy | 若要防 MEV/前运行，需单独方案；ERC-7984 本体不覆盖。 | privacy framework; privacy EIP survey |

**最小 CCT（MVP）**：`confidential_accounting + compliance_policy + issuer_controls + selective_disclosure + auditability`。没有 confidential accounting 的方案只是 compliance token；没有 compliance policy/issuer controls 的方案只是 privacy token；没有 selective disclosure/auditability 的方案不适合 institutional RWA。

### item-3: 统一 Rubric

评分采用 0-5。`0` 表示不覆盖或证据缺失；`3` 表示可 PoC/部分满足且关键 caveat 已知；`5` 表示生产级证据、接口/实现/审计均较充分。任何方案若触发“轻量级一票否决”，Mantle fit 最高不超过 3，除非明确作为长期协议路线而非轻量集成。

| 维度 | 评分口径 | 0-1 | 2-3 | 4-5 |
|---|---|---|---|---|
| privacy_coverage | 隐私覆盖面：R1 金额、R2 余额、R3 身份、R4 业务逻辑/状态、R5 交易图、R8 订单流 | 只隐藏 metadata 或无隐私 | 隐藏金额/余额，但地址/图/状态公开 | 覆盖 token ledger，并有可选身份/状态/图隐私扩展且边界清楚 |
| compliance_capability | KYC/AML、transfer policy、issuer controls、监管动作、recovery | 无合规模型 | 有 allow/block list 或基础 freezing | 覆盖身份、策略、强制动作、赎回、审计与多角色治理 |
| selective_disclosure | 6 维向量完整性和撤销/日志可信度 | 无披露或完全黑箱 | 有 viewing key/observer，但撤销/日志不清 | authority/trigger/payload/scope/revocability/leakage 全部可验证，日志完备 |
| deployment_lightweight | 是否符合 Mantle 轻量目标 | 新链/桥/全节点/硬分叉 | 合约套件 + sidecar/隐私后端，存在中等运维 | 无基础链改动、无新桥、低运维，能在现有 EVM L2 上 PoC |
| engineering_delta | 对 Mantle、钱包、indexer、DeFi、桥、发行流程的改动面 | 需改执行客户端或换 VM | 需新增 wrapper、coprocessor、observer、SDK | 只需合约/SDK/少量 adapter，现有协议影响可控 |
| maturity | 标准、实现、审计、生产部署、团队/生态 | 论坛草案、未审计、单作者 | draft standard / PoC / testnet / vendor self-report | Final/ERC 或主网生产、审计、生态和客户证据充分 |
| mantle_fit | 与 Mantle institutional/private RWA 和 Base B20/private feature 类比的匹配度 | 不符合 RWA 或不轻量 | 可作为参考或中期候选 | 直接服务 RWA 发行、机构披露、轻量部署，并可形成 Mantle 差异化 |

#### Rubric 使用规则

1. **先过边界再打分**：普通 privacy token 或 ordinary compliance token 不应因为单项强而被高估为 CCT。
2. **分离接口成熟度与后端成熟度**：ERC-7984 规范可中立，但 OZ/fhEVM 是具体 FHE 后端；二者成熟度分开打。
3. **厂商性能数据降权**：未独立验证的 TPS、latency、photonic/FHE benchmark 只能影响 gap/risk，不直接给 maturity 高分。
4. **合规披露不等于隐私泄露**：合规方能看见数据是功能，不应被视作 privacy failure；但必须记录 scope、revocability 和 audit log。
5. **桥/赎回是 CCT 的产品边界**：只会在链上 confidential transfer、但无法可靠 redeem/unwrap 的方案不适合 RWA 生产。

### item-4: Evidence Reuse Map

本节为后续作者提供证据复用地图。所有可硬复用项均使用 **直接路径 + per-file last-modifying commit**，不依赖 `evm-privacy-research/research-sections/_index.md`，因为该 index 在本 branch context 中并未完整登记所有 on-disk finals。`evm-privacy-research/issue-plan.md` 在当前 checkout 中不存在，因此不作为 hard evidence。

#### 4.1 Direct Reuse / Hard Inputs

| Source | Commit pin | Reuse class | 可直接复用的结论 | 边界 |
|---|---|---|---|---|
| `compliance-token-standards/report/final-report.md` | `79d472632bd30a5354fbec396f807e0bb63bdea1` | direct_reuse | 合规 token 8 类 taxonomy、ERC-3643 成熟度优势、B20/TIP-20 precompile 路线、Mantle 分阶段策略。 | 不覆盖 confidential accounting；隐私只作为合规 token 的 P2 背景。 |
| `compliance-token-standards/research-sections/base-b20-analysis/final.md` | `f42915ecd33c7f099d4ac0de89997390fc52d0b9` | direct_reuse | Base B20 的 trait composition、PolicyRegistry、RBAC、ActivationRegistry、precompile 架构和 B20 private feature 类比。 | B20 主线不等于 confidential token；B20Security 等本地分支信号不能当生产事实。 |
| `compliance-token-standards/research-sections/mantle-compliance-token-strategy/final.md` | `f42915ecd33c7f099d4ac0de89997390fc52d0b9` | direct_reuse | Mantle 当前无自定义 precompile；op-geth + reth 双客户端；ERC-3643 短期先行、precompile/混合路线中长期评估。 | 未评估隐私后端；硬分叉状态应在 final 前按最新 Mantle repo 再确认。 |
| `evm-privacy-research/research-sections/privacy-landscape-framework/final.md` | `5d6c94f6877227aadaf731852a08f46da1213c54` | direct_reuse | EEA 8 需求、五轴 privacy rubric、6 维 selective disclosure、轻量级一票否决、token ledger vs business-state ledger。 | 需适配到 compliance token 能力模型，不能直接替代 CCT rubric。 |
| `evm-privacy-research/research-sections/erc7984-confidential-token/final.md` | `fdbda370e9e9137890c5bd2deb7752e03d76d0bc` | direct_reuse | ERC-7984 接口、bytes32 pointer 技术中立性、OZ extensions、ObserverAccess/Hooked ACL caveats、RWA 扩展。 | ERC-7984 本体只覆盖 value-level privacy；不覆盖身份、图、业务状态或订单流。 |
| `evm-privacy-research/research-sections/confidential-coprocessor/final.md` | `0041e3a1598751a7d121fecc600ba3d6ad42ad05` | direct_reuse | Zama/Inco/Fhenix 架构、bolt-on 集成、FHE/TEE/economic trust 差异、合规披露能力与性能 caveat。 | 该 commit 仅作为本文件 last-modifying pin；厂商自报性能未独立验证。 |
| `evm-privacy-research/research-sections/eea-enterprise-benchmark/final.md` | `1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0` | direct_reuse | EEA 7 方案 benchmark、R4 合约逻辑隐私标注、轻量级候选/参考/出局分类。 | 本 CCT 需求框架只复用分类口径，不提前采用其 route verdict。 |
| `evm-privacy-research/research-sections/vosa-standards/final.md` | `c9c16b3eb8956584d63efcf2fe155d9acc271f2f` | bounded_reuse | VOSA/VOSA-20/VOSA-RWA 作为 exposed-graph、轻量但未审计草案的对照。 | 单作者论坛草案、未审计；不能作为主推 CCT 标准。 |
| `evm-privacy-research/research-sections/privacy-eips-survey/final.md` | `957773b13b2f5a66354ccda4b7d0c79a7236b222` | bounded_reuse | Privacy EIP 全景、stealth / shielded / encrypted mempool 边界。 | 多数 EIP 不是 CCT 直接实现；作为 taxonomy completeness 保障。 |
| `evm-privacy-research/research-sections/zk-shielded-pool/final.md` | `788453b4097f37003337b943bcf6d7f8f68b02ba` | bounded_reuse | Shielded pool / compliance pool 的匿名集与资金来源证明思路。 | 可能不符合 issuer controls / RWA transfer policy；DeFi/bridge 复杂度高。 |
| `evm-privacy-research/research-sections/zk-privacy-chain-aztec/final.md` | `eceaef1e1b4f7a17d7fc3eb4dd91560207f40629` | reference_only | Aztec 作为密码学级业务状态隐私上限参照。 | 独立链/VM，非 Mantle 轻量集成。 |

Traceability note: the confidential-coprocessor row legitimately points to `0041e3a...` because that is the file's own last-modifying commit. Other reused files that previously shared that snapshot pin have been moved to their individual file pins above.

#### 4.2 Engineering PoC Reference

| Source | Pin / Access | Classification | Use | Boundary |
|---|---|---|---|---|
| `Inco-fhevm/confidential-erc20-framework` | GitHub HEAD `bb39e4f788742121f2fc93de33af58758360545b` verified 2026-06-24 | engineering_poc | wrapper、confidential ERC20、CompliantConfidentialERC20、Identity、ExampleTransferRules 的工程结构参考。 | README 明确“not audited”且仅 proof of concept；不得作为生产安全或标准成熟度证据。 |

可复用工程信号：`ConfidentialERC20Wrapper` 展示 wrap/unwrap；`CompliantConfidentialERC20` 展示 transferRules 合约；`Identity` 展示 encrypted DOB / age check；`ExampleTransferRules` 展示加密金额限额和年龄条件组合。CCT 后续 PoC 可借鉴模块切分，但必须重新设计审计、升级、ACL 撤销、权限日志和 failure semantics。

#### 4.3 Performance / Productionization Reference

| Source | Access | Classification | Use | Boundary |
|---|---|---|---|---|
| Optalysys `Tokenised RWAs are a trillion-dollar opportunity - but only if privacy scales` | Official WP search result id 3165, URL `https://optalysys.com/resource/tokenised-rwas-are-a-trillion-dollar-opportunity-but-only-if-privacy-scales/`, accessed 2026-06-24 | performance_reference | RWA privacy scaling narrative、FHE 性能瓶颈与 institutional adoption 背景。 | Vendor article；不能当独立 benchmark。 |
| Optalysys `Fully Homomorphic Encryption hits the data movement wall - why photonics is emerging as the way forward` | Official WP search result id 3368, accessed 2026-06-24 | performance_reference | FHE data movement wall、硬件/photonic acceleration 生产化背景。 | Vendor article；只影响 performance/SLA gap。 |
| Optalysys `Silicon photonics: our approach to acceleration` | Official WP search result id 2868, accessed 2026-06-24 | performance_reference | Photonic acceleration 路线参考。 | 不提供 CCT token model。 |
| Optalysys `Confidential RWA Tokenisation` | Official WP search result id 2750, accessed 2026-06-24 | performance_reference | Confidential RWA tokenisation 用例包装和生产化叙事。 | 不是标准、不是 Mantle 集成方案、不是第三方审计。 |

#### 4.4 Soft Input Set

Outline review 要求显式实例化 `soft_input` class。当前 dispatch 中确认 WHI-254 到 WHI-261 均为 done M1 issue；因此 **M2/M3 soft-input 集合位于 WHI-254..261 之外**。

| Item | Observed status on 2026-06-24 | Soft-input treatment |
|---|---|---|
| `WHI-262` `[M2-对比] EVM 隐私方案横向对比分析` | Multica issue list shows status `done`, but `evm-privacy-research/research-sections/cross-comparison/final.md` is not present in this branch snapshot. | Do not cite as hard evidence in this draft. It can become hard reuse only after a direct path and commit pin are present in the branch used by this project. |
| `WHI-263` `[M2-策略] Mantle 轻量级机构隐私方案策略建议` | `in_progress`; no final artifact available in this branch. | Soft input only; non-blocking. Future route recommendation must not override this CCT requirements framework until promoted to final and commit-pinned. |
| `WHI-264` `[M3-报告] EVM 隐私方案最终调研报告整合` | `todo`; no final artifact. | Soft input only; non-blocking. It is downstream synthesis, not upstream evidence. |
| Future/incomplete evm-privacy-research M2/M3 material outside WHI-254..261 | Exact future IDs may change. | Treat as `soft_input` by category: cross-comparison drafts, strategy drafts, final-report drafts, route recommendations, comments, issue plans, and not-yet-promoted material. |

**Non-blocking rule**：soft inputs may guide framing and identify future questions, but cannot be used to settle a CCT requirement, score a candidate, or claim Mantle route preference. Only commit-pinned final artifacts, primary standards/docs, audited code, or explicitly classified PoC/performance references can support hard claims.

### item-5: Candidate Layering and Reference Classification

#### 5.1 CCT Layer Stack

| Layer | Role | Example references | CCT interpretation |
|---|---|---|---|
| Asset/compliance base | Identity, transfer policy, issuer controls, legal lifecycle | ERC-3643, B20 PolicyRegistry, TIP-20, ERC-1400 legacy | Compliance substrate; does not by itself hide accounting data. |
| Confidential token interface | Encrypted amount/balance API, operator/callback, wrapper | ERC-7984, ERC-7945 | Interface anchor; still needs compliance and privacy backend. |
| Privacy backend | FHE/ZK/TEE/MPC/GC computation and disclosure | Zama fhEVM, Inco Lightning, Fhenix CoFHE, COTI Coprocessor | Supplies encrypted state and decrypt/re-encrypt flow; trust/performance varies. |
| Compliance/disclosure modules | Observer, policy hooks, RWA agent, identity check, audit logs | OZ ERC7984ObserverAccess/Rwa/Hooked/IdentityCheck; Inco transfer rules | Converts privacy token into compliance-capable CCT. |
| Bridge/redeem/asset adapter | Wrap/unwrap, L1/L2 bridge, redemption, reserve accounting | ERC7984ERC20Wrapper, Inco wrapper, B20 mint/burn/redeem analogies | Required for RWA production and DeFi/custody integration. |
| DeFi/custody integration | Wallet/indexer/risk engine/DEX/lending support | Future sections | Not assumed; encrypted amount breaks many ERC-20 assumptions. |

#### 5.2 Inco Classification

Inco appears in this project in two different roles:

1. **Inco Network / Lightning as privacy backend candidate**：from `confidential-coprocessor/final.md`, Lightning is TEE-first, Base mainnet current support, Atlas FHE is roadmap. This is candidate/reference evidence for backend route evaluation.
2. **`Inco-fhevm/confidential-erc20-framework` as engineering PoC reference**：from the GitHub repo at `bb39e4f...`, it is unaudited PoC code and must not be elevated to production standard.

For this CCT framework, the GitHub framework is classified only as **engineering_poc**. It can inspire:

- how to split wrapper vs confidential token,
- how to route transfers through an external transfer-rules contract,
- how to represent encrypted identity attributes,
- how delegated viewing / owner balance access might shape UX.

It cannot support:

- production security claims,
- maturity scoring above PoC,
- regulatory sufficiency,
- Mantle deployment readiness,
- auditability claims.

#### 5.3 Optalysys Classification

Optalysys is not a token standard, privacy protocol, compliance token framework, or Mantle integration path in current evidence. It belongs to **FHE performance / productionization reference**.

Use Optalysys for:

- FHE throughput/latency bottleneck framing,
- photonic acceleration and hardware roadmap questions,
- RWA privacy scaling as a production-readiness narrative,
- SLA questions that later `fhe-performance-and-production-sla` section should investigate.

Do not use Optalysys for:

- ERC-7984 or ERC-3643 interface decisions,
- issuer controls taxonomy,
- selective disclosure vector,
- maturity score except as vendor self-report / performance context.

### item-6: Mantle Lightweight Constraints and Engineering Delta

Mantle constraints inherited from compliance-token research:

- Mantle is OP Stack based with op-geth + reth dual execution clients.
- Current evidence says no Mantle custom precompile; adding one requires execution-client work and hard-fork deployment.
- ERC-3643-style application contracts can deploy without protocol changes.
- B20-style precompile offers strong gas/determinism benefits but is a long-cycle route.

For CCT, this yields a practical decision tree:

| Path | Description | Lightweight result | Engineering delta | When to study |
|---|---|---|---|---|
| A: Application compliance + confidential wrapper | ERC-3643/issuer policy contracts + ERC-7984/OZ-style confidential token or wrapper. | Likely lightweight if privacy backend is bolt-on. | Contracts, SDKs, observer/audit services, indexer/wallet changes. | First PoC path. |
| B: Confidential token with external coprocessor | ERC-7984-like token uses Zama/Inco/Fhenix/COTI-style backend. | Lightweight if no new chain/bridge/full-node/hardfork. | Backend service dependency, KMS/TEE/coprocessor trust, latency, ACL logging. | Main privacy-backend research. |
| C: B20-style private feature / PolicyRegistry precompile | Protocol-level token or policy execution with privacy feature. | Not lightweight for immediate Mantle; medium/heavy due hard fork. | op-geth/reth changes, fraud-proof, governance, audits. | Long-term Mantle differentiation, not M1 dependency. |
| D: Independent privacy chain / validium / private L2 | Use Aztec/Prividium/Linea/Silent Data/COTI-L2-like environment. | Fails lightweight for Mantle private feature. | New chain/bridge/liquidity, operator stack. | Reference only unless Mantle strategy changes. |
| E: Shielded pool / VOSA | Application-layer privacy with anonymity set or exposed-graph model. | Potentially lightweight, but compliance/issuer controls vary. | Proof circuits, pool accounting, source-of-funds proofs, wallet UX. | Compare as alternative to ERC-7984 CCT. |

**Engineering delta checklist for any CCT candidate**:

| Surface | Questions |
|---|---|
| Token contract | Does it expose ERC-20 compatibility, ERC-7984 compatibility, or a new interface? What breaks in wallets/indexers? |
| Identity and policy | Is KYC identity onchain, offchain, claim-based, encrypted, or hash/attestation based? |
| ACL/disclosure | Who grants access, who revokes, how historical access is handled, and what log proves it? |
| Bridge/redeem | How does confidential amount become public or issuer-visible at redemption? What if decrypt backend is unavailable? |
| DeFi | Can DEX/lending/risk engines compare encrypted balances? Are adapters trusted? |
| Operations | Who runs KMS/TEE/coprocessor/notary; what is the SLA; what happens during outage? |
| Legal/compliance | Does the model satisfy issuer books, auditor evidence, regulator request, Travel Rule, AML, and GDPR caveats? |

### item-7: Project Directory Skeleton and Index Entry Proposal

#### 7.1 Directory Skeleton Status

Current branch contains the project skeleton needed for this section:

| Path | Status | Note |
|---|---|---|
| `confidential-compliance-token-research/outlines/requirements-framework.md` | exists | Approved outline artifact. |
| `confidential-compliance-token-research/research-sections/requirements-framework/drafts/` | exists | This draft persists `round-1.md` here. |
| `confidential-compliance-token-research/research-sections/requirements-framework/final.md` | planned | To be created only after approved draft promotion. |
| `confidential-compliance-token-research/report/assets/` | exists | Placeholder for final report assets. |
| `confidential-compliance-token-research/research-sections/_index.md` | proposed only | Research Agent boundary: do not write; Orchestrator/TW integrates. |

#### 7.2 `_index.md` Proposal

| order | topic_slug | multica_issue_id | final_path | dependencies | status |
|---:|---|---|---|---|---|
| 1 | requirements-framework | `7d7fa951-8160-4b03-a7ae-8ff1a6a9664c` | `confidential-compliance-token-research/research-sections/requirements-framework/final.md` | - | planned |
| 2 | erc3643-erc7984-composition | TBD | `confidential-compliance-token-research/research-sections/erc3643-erc7984-composition/final.md` | requirements-framework | planned |
| 3 | base-b20-private-feature-analogy | TBD | `confidential-compliance-token-research/research-sections/base-b20-private-feature-analogy/final.md` | requirements-framework | planned |
| 4 | zama-oz-confidential-rwa-path | TBD | `confidential-compliance-token-research/research-sections/zama-oz-confidential-rwa-path/final.md` | requirements-framework, erc3643-erc7984-composition | planned |
| 5 | inco-confidential-erc20-poc-fit | TBD | `confidential-compliance-token-research/research-sections/inco-confidential-erc20-poc-fit/final.md` | requirements-framework, erc3643-erc7984-composition | planned |
| 6 | vosa-rwa-and-shielded-pool-tradeoffs | TBD | `confidential-compliance-token-research/research-sections/vosa-rwa-and-shielded-pool-tradeoffs/final.md` | requirements-framework | planned |
| 7 | bridge-redeem-and-defi-composability | TBD | `confidential-compliance-token-research/research-sections/bridge-redeem-and-defi-composability/final.md` | erc3643-erc7984-composition, base-b20-private-feature-analogy | planned |
| 8 | fhe-performance-and-production-sla | TBD | `confidential-compliance-token-research/research-sections/fhe-performance-and-production-sla/final.md` | zama-oz-confidential-rwa-path, inco-confidential-erc20-poc-fit | planned |
| 9 | mantle-route-comparison-and-recommendation | TBD | `confidential-compliance-token-research/research-sections/mantle-route-comparison-and-recommendation/final.md` | erc3643-erc7984-composition, base-b20-private-feature-analogy, zama-oz-confidential-rwa-path, inco-confidential-erc20-poc-fit, vosa-rwa-and-shielded-pool-tradeoffs, bridge-redeem-and-defi-composability, fhe-performance-and-production-sla | planned |

**Index integration note**：status remains `planned` until Orchestrator creates child issues and later Technical Writer / Orchestrator updates project index. This draft is only the proposal.

### item-8: Gap Register and New Research Required

| Gap | Why it matters | Treatment now | Follow-up section |
|---|---|---|---|
| Exact future M2/M3 issue set may change | Downstream route/comparison work can be mistaken for hard evidence. | Soft-input rule instantiated; WHI-263/WHI-264 explicitly non-blocking; WHI-262 not used as hard evidence in this branch. | All downstream sections |
| `evm-privacy-research/issue-plan.md` absent | Dispatch referenced it, but no local file exists. | Use direct commit-pinned final artifacts and Multica issue records instead. | Orchestrator can add issue-plan later if needed |
| ERC-3643 + ERC-7984 composition not yet designed | CCT likely needs both compliance identity and confidential accounting. | New research required. | `erc3643-erc7984-composition` |
| Base B20 private feature analogy is not a confidential token design | B20 provides precompile/policy architecture, not privacy backend. | Use as architecture analogy only. | `base-b20-private-feature-analogy` |
| FHE ACL revocation remains structurally weak | GDPR/minimum disclosure depends on revocation and auditability. | Mark revocability as unverified/constrained unless proven otherwise. | `zama-oz-confidential-rwa-path`, `fhe-performance-and-production-sla` |
| Inco PoC unaudited | Engineering code can be over-weighted by readers. | Engineering PoC only. | `inco-confidential-erc20-poc-fit` |
| Optalysys evidence is vendor performance narrative | Production SLA cannot rely on marketing claims. | Performance reference only. | `fhe-performance-and-production-sla` |
| Bridge/redeem and force-exit semantics unclear | RWA tokens need legal redemption and failure recovery. | Must be separate section. | `bridge-redeem-and-defi-composability` |
| DeFi composability with encrypted amounts is unresolved | ERC-20 integrations assume public balances/amounts. | Identify as should-have but not solved. | `bridge-redeem-and-defi-composability` |
| Mantle latest hardfork/precompile state may change | Protocol route feasibility is time-sensitive. | Use pinned prior research for M1; refresh in final/report if Mantle repo changed. | `mantle-route-comparison-and-recommendation` |

## Diagrams

### diag-1: CCT Capability Stack

```mermaid
flowchart TB
  Asset["RWA / institutional asset"]
  Compliance["Compliance base\nIdentity + policy + issuer controls"]
  Confidential["Confidential accounting\nEncrypted amount / balance / frozen balance"]
  Disclosure["Selective disclosure\nauthority + trigger + payload + scope + revocability + leakage"]
  Audit["Auditability\npublic facts + private auditor view + regulator evidence"]
  Bridge["Bridge / redeem / wrapper\nmint-burn, wrap-unwrap, force-exit"]
  Defi["DeFi / custody adapters\nwallets, indexers, DEX, lending, risk"]

  Asset --> Compliance --> Confidential --> Disclosure --> Audit
  Confidential --> Bridge --> Defi
  Compliance --> Bridge
  Disclosure --> Defi
```

### diag-2: Evidence Reuse Map

```mermaid
flowchart LR
  CCT["CCT requirements-framework"]

  subgraph HardReuse["direct_reuse / bounded_reuse"]
    CTS["compliance final report\n79d4726"]
    B20["base-b20-analysis\nf42915e"]
    Mantle["mantle-compliance-token-strategy\nf42915e"]
    Framework["privacy-landscape-framework\n5d6c94f"]
    ERC7984["erc7984-confidential-token\nfdbda37"]
    Coproc["confidential-coprocessor\n0041e3a"]
    EEA["eea-enterprise-benchmark\n1eac19e"]
    VOSA["vosa / shielded / eips\nbounded reuse"]
  end

  subgraph Soft["soft input"]
    WHI262["WHI-262 done but path absent here"]
    WHI263["WHI-263 in_progress"]
    WHI264["WHI-264 todo"]
    Future["future incomplete M2/M3"]
  end

  subgraph External["external classified references"]
    IncoPoC["Inco confidential ERC20\nengineering PoC"]
    Opta["Optalysys\nFHE performance reference"]
  end

  CTS --> CCT
  B20 --> CCT
  Mantle --> CCT
  Framework --> CCT
  ERC7984 --> CCT
  Coproc --> CCT
  EEA --> CCT
  VOSA --> CCT
  IncoPoC -.-> CCT
  Opta -.-> CCT
  WHI262 -. non-blocking .-> CCT
  WHI263 -. non-blocking .-> CCT
  WHI264 -. non-blocking .-> CCT
  Future -. non-blocking .-> CCT
```

### diag-3: Actor and Visibility Flow

```mermaid
sequenceDiagram
  participant Holder
  participant Token as CCT Contract
  participant Policy as Compliance Policy
  participant Backend as Privacy Backend
  participant Issuer as Issuer/Agent
  participant Auditor
  participant Regulator

  Holder->>Token: submit encrypted transfer amount
  Token->>Policy: check identity / transfer rules
  Policy-->>Token: allow, block, freeze, or require disclosure
  Token->>Backend: operate on encrypted handles
  Backend-->>Token: result handle / decrypt proof / callback
  Token-->>Holder: confidential balance update
  Issuer->>Token: freeze, force transfer, recover, redeem
  Auditor->>Token: request scoped view or audit log
  Token->>Backend: re-encrypt / disclose authorized payload
  Backend-->>Auditor: scoped amount/balance evidence
  Regulator->>Issuer: legal or policy request
  Issuer->>Token: regulator-scoped disclosure workflow
```

### diag-4: Proposed 9-Section Dependency Graph

```mermaid
flowchart TB
  R1["1 requirements-framework"]
  R2["2 erc3643-erc7984-composition"]
  R3["3 base-b20-private-feature-analogy"]
  R4["4 zama-oz-confidential-rwa-path"]
  R5["5 inco-confidential-erc20-poc-fit"]
  R6["6 vosa-rwa-and-shielded-pool-tradeoffs"]
  R7["7 bridge-redeem-and-defi-composability"]
  R8["8 fhe-performance-and-production-sla"]
  R9["9 mantle-route-comparison-and-recommendation"]

  R1 --> R2
  R1 --> R3
  R1 --> R4
  R1 --> R5
  R1 --> R6
  R2 --> R4
  R2 --> R5
  R2 --> R7
  R3 --> R7
  R4 --> R8
  R5 --> R8
  R4 --> R9
  R5 --> R9
  R6 --> R9
  R7 --> R9
  R8 --> R9
  R2 --> R9
  R3 --> R9
```

## Source Coverage

### Source Requirements Coverage

| Source requirement | Coverage | Notes |
|---|---|---|
| src-1 prior compliance research | covered | Compliance final report, Base B20 final, Mantle strategy final are direct commit-pinned. |
| src-2 prior privacy research | covered | Privacy framework, ERC-7984, coprocessor, EEA benchmark, VOSA/EIP/shielded/Aztec finals are direct or bounded commit-pinned. |
| src-3 Inco PoC source | covered | GitHub HEAD verified as `bb39e4f...`; classified engineering_poc only. |
| src-4 Optalysys external source | covered | Official Optalysys WP search results verified 2026-06-24; classified performance_reference only. |
| src-5 project skeleton / index | covered | Skeleton status recorded; `_index.md` proposal embedded, not written. |
| src-6 Multica issue records | covered | WHI-254 and WHI-261 sampled as done M1 records; project issue list used to instantiate WHI-263/WHI-264 soft input. |

### Evidence Confidence Summary

| Confidence | Evidence type | Examples |
|---|---|---|
| High | Commit-pinned final research artifacts and issue records marked done | Compliance final report; privacy framework; ERC-7984 final; B20 final |
| Medium | Commit-pinned final artifacts used only for bounded analogy | VOSA, shielded pool, Aztec, EEA benchmark |
| Medium-low | Engineering code PoC with explicit unaudited warning | Inco confidential ERC20 framework |
| Low for hard claims / useful for questions | Vendor performance and productionization material | Optalysys pages; FHE performance claims |
| Non-blocking | In-progress/todo downstream M2/M3 material | WHI-263, WHI-264, future M2/M3 drafts |

## Gap Analysis

This draft is a requirements framework, not a final route recommendation. The highest-risk unresolved questions are:

1. **Composition gap**：No existing source proves a clean ERC-3643 + ERC-7984 production composition with identity, confidential accounting, issuer controls, and revocable selective disclosure. This requires new primary research.
2. **Disclosure revocation gap**：FHE ACL models appear structurally hard to revoke. Any CCT score must separate future authorization revocation from historical handle access revocation.
3. **Audit log gap**：Many schemes expose events, but few prove that disclosure grants, re-encryption, regulator requests, and offchain audit evidence are tamper-evident and queryable.
4. **Performance/SLA gap**：FHE throughput and latency remain vendor-claimed in several sources. Optalysys helps frame production questions but does not close them.
5. **Mantle integration gap**：Coprocessor “no hardfork” claims still require checking host contracts, finality/callback timing, sequencer behavior, data availability, KMS availability, and operational ownership on Mantle.
6. **Bridge/redeem gap**：RWA production requires cash/fund-share redemption and reserve accounting, not just confidential transfer. Disclosure at redemption must be designed.
7. **DeFi gap**：Encrypted balances break normal indexer, DEX, lending, liquidation, and oracle assumptions. Adapters may reintroduce trusted parties or public leakage.
8. **Legal/product gap**：GDPR, MiCA, Travel Rule, AML/CFT, broker-dealer books, fund accounting, and regulated custody all need jurisdiction-specific interpretation outside this M1 technical framework.

## Revision Log

| Round | Date | Change |
|---:|---|---|
| 1 | 2026-06-24 | Initial deep draft from approved outline. Added CCT definition, capability model, unified rubric, evidence reuse map, soft-input instantiation, Inco/Optalysys classification, Mantle lightweight constraints, index proposal, diagrams, source coverage, and gap register. Addressed outline review carry-forward items: explicit WHI-263/WHI-264 soft input, per-file commit pins, and direct citations instead of stale index reliance. |
