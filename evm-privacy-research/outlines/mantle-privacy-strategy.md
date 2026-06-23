---
topic: "Mantle 轻量级机构隐私方案策略建议"
project_slug: "evm-privacy-research"
topic_slug: "mantle-privacy-strategy"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "evm-privacy-research/outlines/mantle-privacy-strategy.md"
  draft: "evm-privacy-research/research-sections/mantle-privacy-strategy/drafts/round-{n}.md"
  final: "evm-privacy-research/research-sections/mantle-privacy-strategy/final.md"
  index: "evm-privacy-research/research-sections/_index.md"

scope: |
  基于 WHI-262 横向对比结果（evm-privacy-research/research-sections/cross-comparison/final.md @ 9c81049），在「轻量级 bolt-on」
  与「机构合规-选择性披露」两条约束下，为 Mantle 给出隐私方案策略建议。研究必须先重申私密账本/转账/余额三项需求与两条
  约束，并显式区分「私密 token ledger（A：金额、余额、交易图、对手方）」与「企业业务流程私密执行（B：合约逻辑、业务状态、
  合规计算、RWA 生命周期状态）」两类需求。

  本 section 不重新做全集竞品调研，而是把 WHI-262 与 M1 sections 的候选 verdict 转化为策略路线。每个推荐结论必须可追溯到
  WHI-262 及上游 M1 final.md 路径；新引入的策略判断标注为 [strategy synthesis]。VOSA 必须定位为轻量备选/PoC，而非主推，
  原因包括未审计、单作者论坛草案、概念/Pre-pilot 成熟度、exposed-graph 与链下合规服务信任。

audience: "Mantle 工程团队、协议/基础设施负责人、企业金融/RWA/BD 团队、隐私方案评估决策者、后续集成验证负责人"

expected_output: |
  一份中文结构化策略研究 section，包含：
  - 三需求两约束重申，并用「私密 token ledger」vs「企业业务流程私密执行」作为所有推荐的分叉基准
  - 分叉 A（私密 token ledger）路线推荐：机密代币（ERC-7984/OZ/Zama/Inco 后端）、shielded-pool（Railgun/Privacy Pools）、
    VOSA/VOSA-RWA 的取舍、主推与备选
  - 分叉 B（企业业务流程隐私执行）路线推荐：Zama/Inco/Fhenix/COTI-Coprocessor/Paladin 与 Prividium/Linea/Silent Data/Aztec
    的候选/参考关系，说明 shielded-pool/VOSA 不足以覆盖 R4
  - 接口策略：ERC-7984 作为机构机密代币锚点，VOSA 仅作轻量 PoC/备选；必要时说明 ERC-7945/8065/8302 的观察位
  - 选择性披露落地设计：viewing key / observer ACL / association set / compliance-gated / privacy group 在 Mantle 上的组合方案、
    权限粒度、审计留痕、撤销性风险
  - 集成路径草图、里程碑、关键风险与待验证项：Mantle 支持、KMS/TEE/协处理器运维、prover/性能、ACL 撤销、标准成熟度、审计、
    选择性披露合规流程、R8 订单流缺口
  - 两类需求分别给出 1 主推 + 1 备选，并明确适用条件、不可覆盖范围和下一步验证动作

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23T16:23:56Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-23T16:23:56Z"

multica_issue_id: "d84d0da4-88a7-49b0-a83a-ba171a78adc3"
report_issue_id: "68d01fa3-fdaa-4b11-b9e4-e449dfafe39c"
branch_name: "research/evm-privacy-research/mantle-privacy-strategy"
base_commit: "9c81049ea015a1ca7eec77c655ddc176c4068944"
language: "中文"
research_depth: "strategy-synthesis"
mode: "single-issue-composable"

primary_sources:
  - name: "cross-comparison（WHI-262）final.md"
    url: "evm-privacy-research/research-sections/cross-comparison/final.md"
    commit: "9c81049ea015a1ca7eec77c655ddc176c4068944"
    usage: "策略主锚：候选全集、bolt-on 分组、A/B 账本分类、合规披露 sub-taxonomy、R1/R2/R3/R4/R5/R8 原语覆盖矩阵、逐方案 Mantle verdict"
  - name: "privacy-landscape-framework（WHI-254）final.md"
    url: "evm-privacy-research/research-sections/privacy-landscape-framework/final.md"
    commit: "9c81049ea015a1ca7eec77c655ddc176c4068944"
    usage: "五轴 rubric、R1-R8、轻量级 V1-V4 一票否决、选择性披露 6 维向量、隐私账本 A/B 口径"
  - name: "erc7984-confidential-token（WHI-255）final.md"
    url: "evm-privacy-research/research-sections/erc7984-confidential-token/final.md"
    commit: "9c81049ea015a1ca7eec77c655ddc176c4068944"
    usage: "ERC-7984/7945 接口策略、OZ Confidential Contracts/RWA/Observer/Hooked/Wrapper、FHE ACL 撤销与 operator 风险"
  - name: "vosa-standards（WHI-256）final.md"
    url: "evm-privacy-research/research-sections/vosa-standards/final.md"
    commit: "9c81049ea015a1ca7eec77c655ddc176c4068944"
    usage: "VOSA/VOSA-20/VOSA-RWA 的轻量纯合约、exposed-graph、链下合规服务 keyHash、单作者未审计 Concept/Pre-pilot caveat"
  - name: "privacy-eips-survey（WHI-257）final.md"
    url: "evm-privacy-research/research-sections/privacy-eips-survey/final.md"
    commit: "9c81049ea015a1ca7eec77c655ddc176c4068944"
    usage: "ERC-5564/6538、ERC-8065、ERC-8302/pERC-20、EIP-8182/8105 等接口/基础设施观察位与边界"
  - name: "confidential-coprocessor（WHI-258）final.md"
    url: "evm-privacy-research/research-sections/confidential-coprocessor/final.md"
    commit: "9c81049ea015a1ca7eec77c655ddc176c4068944"
    usage: "Zama/Inco/Fhenix 协处理器路线、A+B 能力、KMS/TEE/EigenLayer 信任模型、Mantle 集成前提与风险"
  - name: "zk-privacy-chain-aztec（WHI-259）final.md"
    url: "evm-privacy-research/research-sections/zk-privacy-chain-aztec/final.md"
    commit: "9c81049ea015a1ca7eec77c655ddc176c4068944"
    usage: "密码学全执行隐私上界、note/nullifier 与多密钥披露概念、非 EVM 独立链一票否决、仅作参考"
  - name: "zk-shielded-pool（WHI-260）final.md"
    url: "evm-privacy-research/research-sections/zk-shielded-pool/final.md"
    commit: "9c81049ea015a1ca7eec77c655ddc176c4068944"
    usage: "Railgun/Privacy Pools shielded-pool、viewing key/PPOI/association set/ragequit、Tornado 无披露教训、R4 不覆盖边界"
  - name: "eea-enterprise-benchmark（WHI-261）final.md"
    url: "evm-privacy-research/research-sections/eea-enterprise-benchmark/final.md"
    commit: "9c81049ea015a1ca7eec77c655ddc176c4068944"
    usage: "Paladin/Prividium/Linea/Nightfall/COTI/Polygon/Silent Data 的企业 benchmark、R4 标注、Mantle candidate/reference/out 初判"

prerequisite_sections:
  - topic_slug: "cross-comparison"
    dependency_type: "primary-input"
    usage: "WHI-262 横向对比为本策略 section 的主输入，所有路线裁决必须回溯到其矩阵和 verdict"
  - topic_slug: "privacy-landscape-framework"
    dependency_type: "framework"
    usage: "R1-R8、A/B ledger、轻量级一票否决、选择性披露 6 维向量"
  - topic_slug: "erc7984-confidential-token"
    dependency_type: "input-section"
    usage: "ERC-7984 接口锚点与合规扩展"
  - topic_slug: "vosa-standards"
    dependency_type: "input-section"
    usage: "VOSA 备选/PoC 定位和风险"
  - topic_slug: "privacy-eips-survey"
    dependency_type: "input-section"
    usage: "Stealth/ERC wrapper/private-token/protocol EIP 观察位"
  - topic_slug: "confidential-coprocessor"
    dependency_type: "input-section"
    usage: "FHE/TEE/CoFHE 协处理器路线"
  - topic_slug: "zk-privacy-chain-aztec"
    dependency_type: "input-section"
    usage: "全执行隐私参考上界与不可 bolt-on 边界"
  - topic_slug: "zk-shielded-pool"
    dependency_type: "input-section"
    usage: "shielded-pool 路线、association set、viewing key、R4 不覆盖"
  - topic_slug: "eea-enterprise-benchmark"
    dependency_type: "input-section"
    usage: "企业 R4/Privacy-Group/TEE/Validium benchmark 与 Mantle 参考位"
---

# Research Outline: Mantle 轻量级机构隐私方案策略建议

> 本 section 是策略建议，不是新一轮横向竞品全集调研。研究必须把 WHI-262 已收敛的矩阵转化为 Mantle 可执行路线，并把「隐私账本」的二义性放在开头：如果需求是私密 token ledger，主问题是金额/余额/转账图/选择性披露；如果需求是企业业务流程私密执行，主问题是 R4 合约逻辑/业务状态隐私，候选集合会完全不同。

## Items

### item-1: 三需求两约束重申与「隐私账本」二义分叉基准

重申 Mantle 的三项隐私需求（私密账本、私密转账、私密余额）与两条约束（轻量级 bolt-on、机构合规-选择性披露），并把「私密账本」拆成 A/B 两类：A = 私密 token ledger（token/value/flow ledger），B = 企业业务流程私密执行（business-state/execution ledger）。本 item 是全部推荐的决策入口，必须避免把 Privacy Pools、VOSA、ERC-7984 等 token/value 隐私方案误当成业务状态隐私方案。

基准定义要直接复用 WHI-262 的 A/B 分类和 R4 分水岭：A 类足以覆盖金额、余额、交易流、匿名集或合规集合；B 类必须隐藏或私有执行合约逻辑、业务状态、RWA 生命周期状态、机构间合规计算。研究要明确「私密账本/转账/余额」在 token ledger 语境下可以由机密代币或 shielded pool 解决，但在企业业务账本语境下，必须进入 FHE/TEE/GC/Privacy-Group/私有 VM 路线。

- **Priority**: high
- **Dependencies**: none

### item-2: 分叉 A — 私密 token ledger 路线推荐

围绕 A 类需求，比较三组路线：机密代币（ERC-7984/OZ/Zama 或 Inco 后端）、shielded-pool（Railgun/Privacy Pools）、VOSA/VOSA-RWA。输出要给出清晰的主推、备选和不推荐边界，而不是并列罗列。必须同时覆盖私密余额、私密转账、交易图/对手方隐私、机构选择性披露、轻量级部署和成熟度。

研究应重点论证：ERC-7984/OZ 更适合作为机构机密代币/余额/金额的接口锚点和合规扩展基座，但默认地址/图公开，且 FHE ACL/Observer/Hooked/RWA 的撤销与权限审计是核心风险；Railgun/Privacy Pools 更适合隐藏交易图或资金来源集合证明，尤其 Privacy Pools 的 association set 可为「诚实资金/非法资金分离」提供合规设计参考，但它们是 pure A + compliance overlay，不覆盖 R4；VOSA 的优势是极轻量、pure contract、合规友好 exposed-graph，但因未审计、单作者、概念阶段、链下合规服务信任和冻结/强制转账结构缺口，只能定位为轻量 PoC/备选。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 分叉 B — 企业业务流程私密执行路线推荐

围绕 B 类需求，评估 Zama fhEVM、Inco Lightning、Fhenix CoFHE、COTI-Coprocessor、Paladin，以及 Prividium、Linea Enterprise、Silent Data、Aztec 等 reference/benchmark。输出必须说明为什么 shielded-pool、VOSA、ERC-7984 标准本体不能单独满足业务状态隐私：它们只保护 token/value/flow，不能隐藏合约逻辑或业务状态。

研究应把候选分成「可 bolt-on 候选」与「能力上界参考」两层。可 bolt-on 候选内，Zama/Inco/Fhenix/COTI-Coprocessor 是协处理器/机密层路线，Paladin 是 privacy group/sidecar 路线；各自应按信任模型取舍（FHE+KMS、TEE、经济安全、组织 notary/privacy domain）、Mantle 支持前提、性能、合规披露能力和成熟度排序。Prividium/Linea/Silent Data/Aztec 要作为企业链/独立链参考，不应被推荐为 Mantle 轻量主路径，但可借鉴其 RBAC、operator/auditor、validium/private-state、TEE full execution 或密码学全执行隐私设计。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 接口策略 — ERC-7984 vs VOSA，并定位观察位标准

给出 Mantle 对接口标准的策略：短期主推 ERC-7984 作为机构机密代币接口锚点，VOSA/VOSA-RWA 作为轻量备选/PoC，不作为生产主推。论证必须区分「标准接口」与「后端实现」：ERC-7984 本体是 token/value 标准，不自动带来 R4；若采用 Zama/OZ 后端才进入 A+B 的 FHE 能力。VOSA 是论坛草案和设计模式，不是成熟标准或已审计实现。

本 item 也要处理观察位：ERC-7945 可作为 ERC-20-like confidential token 的跟踪项但实现生态弱；ERC-8065/8302/pERC-20 可作为 wrapper/native private token 的观察项但成熟度与接口稳定性不足；ERC-5564/6538 是身份/收款方匿名补件，不保护金额/余额；EIP-8182/7503/8105 等协议层方案只作参考，不应进入 Mantle bolt-on 主路径。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-5: 选择性披露落地设计

把 WHI-262 的选择性披露 sub-taxonomy 转化为 Mantle 落地设计。研究要分别设计 A 类 token ledger 与 B 类 business-state 的披露组合，并说明 authority、trigger、payload、scope、revocability、leakage 六维向量如何配置。不能把「viewing key」写成唯一答案；机构合规需要事前准入、事后审计、范围控制、留痕和可撤销性/最小披露边界。

建议结构应覆盖：ERC-7984/OZ 的 ObserverAccess/RWA/Hooked/Restricted/AmountDisclosed 如何用于审计与强制合规；Railgun viewing key 的永久不可撤销风险和 PPOI 的仅排除性质；Privacy Pools association set + ASP + ragequit 如何成为资金来源证明模板；VOSA-RWA 的合规服务 attestation 如何作为 PoC 但需信任链下服务；Paladin privacy group/notary/domain-wide 可见性如何服务企业流程；Prividium/Linea/Silent Data 的 regulator/operator/auditable-log 可作为参考。每种设计必须列出撤销性、披露范围、谁能看到什么、是否有审计事件、哪些信息仍泄露（地址、图、存在性、时序）。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-4

### item-6: 集成路径、里程碑、关键风险与待验证项

提出 Mantle 的分阶段集成路径和验证清单。至少要包含：A 类 confidential token pilot、A 类 shielded/compliance-pool pilot、B 类协处理器/Paladin pilot、合规披露与审计流程验证、生产前安全/审计/性能门槛。里程碑要能对应到实际决策：选型验证、PoC、testnet、limited institutional pilot、production gate。

风险清单必须覆盖：Zama Mantle 支持或自托管 KMS/Gateway/Coprocessor 的工程量；Inco 当前链支持与 TEE 信任、force-exit/liveness；Fhenix/COTI-Coprocessor 成熟度和主网状态；Paladin notary/域内可见/N-of-N 扩展性；FHE ACL 授权撤销与 Hooked module 持久访问；VOSA 未审计/单作者/真实性能未复现；Railgun viewing key 不可撤销；Privacy Pools ASP 半许可与证明栈/审计未完全验证；Prividium/Linea/Silent Data/Aztec 的独立链部署不符合轻量约束；R8 订单流/MEV 隐私基本未被主方案覆盖，需要单独进入 private sequencing/encrypted mempool 设计。

- **Priority**: high
- **Dependencies**: item-2, item-3, item-5

### item-7: 两类需求的 1 主推 + 1 备选总结

输出最终策略建议：分别针对 A 类私密 token ledger 和 B 类企业业务流程私密执行，各给出 1 个主推路径与 1 个备选路径，并明确适用条件。该总结应是可执行推荐，不是矩阵复述。每个推荐必须说明为什么胜过其他路径、为什么不覆盖另一类需求、下一步验证动作是什么。

预期 deep draft 要验证并形成如下类型的结论：A 类可优先考虑「ERC-7984/OZ 作为机密代币接口锚点 + 合规模块 + 可选 Privacy Pools/Railgun 资金来源/匿名集组件」作为主推，VOSA-RWA 或 shielded-pool 单独路线作为备选/PoC；B 类可优先考虑「协处理器路线（Zama 或 Inco，取决于 Mantle 支持、合规披露、性能和信任模型验证）」或「Paladin privacy group sidecar」作为候选，并把 Prividium/Linea/Silent Data/Aztec 放在参考位。最终结论应避免提前锁死具体厂商，必须用待验证项定义主推成立条件。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5, item-6

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| requirement_branch | 标注该研究项服务于 A 私密 token ledger、B 企业业务流程私密执行，或同时服务两者 | all |
| recommendation_role | 标注方案在该项中的角色：primary, backup, reference, out, component, poC-only | item-2, item-3, item-4, item-7 |
| protected_dimensions | 用 WHI-254 R1/R2/R3/R4/R5/R6/R7/R8 标注覆盖范围，尤其区分 R4 业务逻辑/状态 | all |
| trust_model | 记录 FHE/ZK/TEE/GC/Privacy-Group/组织信任/经济安全等信任假设及其合规含义 | item-2, item-3, item-5, item-6 |
| deployment_weight | 按 WHI-254 V1-V4 与 bolt-on/sidecar/coprocessor/independent-chain/protocol-layer 分类记录 Mantle 集成重量 | item-2, item-3, item-6, item-7 |
| disclosure_vector | 按 authority/trigger/payload/scope/revocability/leakage 六维记录选择性披露设计 | item-2, item-3, item-5 |
| interface_strategy | 记录 ERC-7984、VOSA、ERC-7945、ERC-8065、ERC-8302、ERC-5564 等接口标准的主推/备选/观察位 | item-4 |
| mantle_integration_path | 记录在 Mantle 上的集成步骤、依赖前提、里程碑与生产 gate | item-6, item-7 |
| risk_and_validation | 记录每个结论成立前必须验证的安全、性能、审计、合规、运维与成熟度风险 | all |
| source_trace | 每个关键结论需回溯到 WHI-262 或上游 M1 final.md 路径，策略推断标注 [strategy synthesis] | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | decision_tree | Mantle 隐私需求分叉决策树：三需求两约束 → A token ledger vs B business-state ledger → 候选路线收敛 | mermaid | item-1, item-7 |
| diag-2 | comparison | 分叉 A 路线对比矩阵：ERC-7984/OZ、Railgun、Privacy Pools、VOSA/VOSA-RWA、ERC-8065/8302 的覆盖、合规、轻量、成熟度、推荐角色 | ascii | item-2, item-4 |
| diag-3 | comparison | 分叉 B 路线对比矩阵：Zama、Inco、Fhenix、COTI-Coprocessor、Paladin、Prividium、Linea、Silent Data、Aztec 的 R4 能力、信任模型、部署重量、Mantle verdict | ascii | item-3 |
| diag-4 | flow | Mantle 选择性披露组合流程：事前准入、加密转账/私有执行、审计请求、association set/viewing key/privacy group 披露、留痕与撤销边界 | mermaid | item-5 |
| diag-5 | timeline | 集成路径与里程碑：PoC → testnet → institutional pilot → production gate，并列出每阶段验证项 | mermaid | item-6 |
| diag-6 | comparison | 最终 1 主推 + 1 备选总结表，按 A/B 两类需求分别列适用条件、不可覆盖范围、下一步验证动作 | ascii | item-7 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | upstream_synthesis | 必须引用 WHI-262 cross-comparison/final.md 作为主锚，并回溯其 A/B 分类、合规披露分组、原语矩阵、逐方案 verdict | 1 |
| src-2 | framework | 必须引用 WHI-254 privacy-landscape-framework/final.md 的 R1-R8、V1-V4、A/B ledger 和 6 维选择性披露向量 | 1 |
| src-3 | upstream_sections | 必须覆盖 M1 final.md：ERC-7984、VOSA、privacy EIPs、confidential coprocessor、Aztec、ZK shielded pool、EEA enterprise benchmark | 7 |
| src-4 | standard_interface_sources | 接口策略须至少引用 ERC-7984 与 VOSA 上游 final.md，并说明 VOSA 未审计/单作者/论坛草案 caveat | 2 |
| src-5 | enterprise_disclosure_sources | 选择性披露设计须至少引用 ERC-7984/OZ、Railgun/Privacy Pools、Paladin/EEA benchmark、Zama/Inco/Fhenix 中的披露模型 | 4 |
| src-6 | validation_backlog | 待验证项必须列明哪些事实仍需未来外部或官方确认，不能把 upstream 的 unverified/claimed/announced caveat 升级为事实 | 1 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
