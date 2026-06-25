---
topic: "Confidential Compliance Token 路线横向对比"
project_slug: "confidential-compliance-token-research"
topic_slug: "route-comparison"
github_repo: "Whisker17/multica-research"
round: 2
status: candidate

artifact_paths:
  outline: "confidential-compliance-token-research/outlines/route-comparison.md"
  draft: "confidential-compliance-token-research/research-sections/route-comparison/drafts/round-{n}.md"
  final: "confidential-compliance-token-research/research-sections/route-comparison/final.md"
  index: "confidential-compliance-token-research/research-sections/_index.md"

scope: |
  基于 WHI-266（需求框架）、WHI-267（Zama 深挖）、WHI-268（PSE 产品约束）、WHI-269（合规 token 扩展）、
  WHI-270（候选方案补充调研）五篇 final artifacts，形成 confidential compliance token 路线横向对比矩阵，
  裁决 Mantle phase 1 最值得推进的主路线、备选路线和明确出局路线。
  步骤：(1) 汇总候选路线；(2) 按 WHI-266 rubric 建主矩阵（扩展厂商锁定、性能可预测性维度）；
  (3) private token ledger vs private business-state ledger 分叉视图；
  (4) application/contract-only、coprocessor/backend、native precompile/protocol 三类部署视图；
  (5) 路线裁决；(6) 输出对 WHI-272 协议设计的设计约束。
audience: "Mantle 协议/战略团队、RWA/机构业务负责人、合规架构师、研究评审 agent、WHI-272 协议设计作者"
expected_output: |
  confidential-compliance-token-research/research-sections/route-comparison/final.md；
  主对比矩阵 + 三张分组视图（ledger 分叉 / 部署形态 / 合规披露）+ FHE 性能视图 +
  路线裁决表 + WHI-272 设计约束清单

revision_metadata:
  created_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-24"
  last_modified_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-24"
  round_2_revision_source: "Review Verdict outline-needs-revision (round 1) — 3 findings: (1) major: 主推-selection rule undefined, (2) major: WHI-262/263 soft-input handling absent, (3) minor: Inco confidential ERC20 framework not tied as engineering evidence"

multica_issue_id: "d44834f3-e3f7-4174-9200-395052956c18"
report_issue_id: "7b29e4a8-01eb-4cbf-9b59-8e363f9a40e4"
branch_name: "research/confidential-compliance-token-research/route-comparison"
base_commit: "29269d9de5f1399fb66baca2d20967854b50273f"
language: "中文"
mode: "single-issue-composable"

input_artifacts:
  - path: "confidential-compliance-token-research/research-sections/requirements-framework/final.md"
    issue: "WHI-266"
    role: "rubric baseline, CCT definition, capability model, evidence reuse map"
  - path: "confidential-compliance-token-research/research-sections/zama-confidential-rwa/final.md"
    issue: "WHI-267"
    role: "Zama deep dive, rubric scores, standards tension analysis, lifecycle model"
  - path: "confidential-compliance-token-research/research-sections/pse-private-transfers-constraints/final.md"
    issue: "WHI-268"
    role: "PSE product constraints, account vs note model, anti-pattern checklist, UX rubric supplement"
  - path: "confidential-compliance-token-research/research-sections/compliance-token-private-extension/final.md"
    issue: "WHI-269"
    role: "compliance token skeleton, B20 analogy, ERC-3643 application-layer baseline, phase boundary"
  - path: "confidential-compliance-token-research/research-sections/confidential-rwa-candidates/final.md"
    issue: "WHI-270"
    role: "non-Zama candidate survey, tier profiles, screening verdicts, gap register"

soft_inputs:
  note: |
    WHI-262（Mantle RWA 市场调研）和 WHI-263（Mantle CCT 竞品对标）属于 M2/M3 milestone
    soft inputs。WHI-266 item-4.4 soft-input handling table 记录：WHI-262 status=done 但
    final path 在当前 branch 不存在；WHI-263 status=in_progress。本 outline 遵循 WHI-266
    non-blocking rule：soft inputs 缺失时不阻塞，用 M1 已有输入自行完成 narrow comparison。
  handling:
    - issue: "WHI-262"
      status: "done (per WHI-266 item-4.4 table; final path absent in branch)"
      consumed: false
      fallback: "RWA 市场维度由 WHI-270 candidate profiles 和 WHI-267 Zama RWA lifecycle 覆盖；不依赖 WHI-262 final"
    - issue: "WHI-263"
      status: "in_progress (per WHI-266 item-4.4 table)"
      consumed: false
      fallback: "竞品对标维度由 WHI-270 全候选 survey + WHI-268 PSE 约束分析覆盖；不依赖 WHI-263 final"
  m1_only_fallback: |
    本 issue 路线横向对比严格基于 M1 五篇 final artifacts（WHI-266 至 WHI-270）完成。
    WHI-262/263 finals 即使后续可用，也仅作为 supplementary reference，不改变路线 gate
    判定或 rubric scoring 的证据基础。若 WHI-262/263 后续完成且包含与本 issue 裁决
    矛盾的重要发现，应由 Orchestrator 决定是否触发 WHI-271 re-evaluation。
---

# 研究大纲（Research Outline）：Confidential Compliance Token 路线横向对比

## 研究项（Items）

### item-1: 候选路线汇总与对比方法论

本项汇总所有候选路线并建立对比方法论。候选路线来源于 WHI-267（Zama 深挖）和 WHI-270（候选方案补充调研），加上 WHI-269 提出的合规 token 骨架组合路线。必须覆盖 issue 描述中点名的全部候选：

- **可独立承载路线的候选（Route-capable candidates）**（可独立承载 CCT 路线）：
  - Zama/ERC-7984 + OZ Confidential Contracts backend
  - ERC-3643 + confidential overlay（应用层合规 + 机密记账后端（confidential accounting backend）的组合路线）
  - B20-like native design（Mantle 原生 precompile/protocol 路线）
  - Inco Lightning / 机密 token 路线（confidential token route）
  - VOSA-RWA
  - Nightfall / EY enterprise

- **组件/补强候选（Component/supplement candidates）**（不能独立承载路线，但可补强）：
  - Fhenix/CoFHE（后端可替换的 FHE（backend-replaceable FHE））
  - Railgun/Privacy Pools（合规披露（compliance-disclosure）补强）
  - Paladin/Privacy Groups（企业工作流（enterprise workflow）补强）

- **仅作基准/参考（Benchmark/reference-only）**：
  - Aztec（隐私原生 L2（privacy-native L2）上限参照）
  - Starknet STRK20（非 EVM 原生 token 基准（native token benchmark））
  - EIP-8182（协议级屏蔽池基准（protocol shielded-pool benchmark））
  - Optalysys（FHE 性能/生产化约束参考，单列）

方法论要点：
1. 先用 WHI-270 的 standalone-route-capability gate 划分路线候选与组件/参考候选。
2. 然后用 WHI-266 rubric（扩展两个新维度）逐候选打分。
3. 分数不是简单加总排序器；bucket 先由路线能力门决定，再由分数解释升降级（继承 WHI-270 round-2 规则）。
4. ERC-3643 + confidential overlay 和 B20-like native design 是 WHI-269 定义的组合路线，不是 WHI-270 的独立候选；本 item 需从 WHI-269 phase boundary 中提取并构建为可比较路线。
5. 每条路线的证据必须可回溯到前序 final 的具体路径、commit SHA 或外部 URL + 访问日期。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: none

### item-2: 扩展 WHI-266 Rubric 与评分校准

本项在 WHI-266 七维 rubric 基础上，按 issue 要求增加两个维度，形成九维主矩阵评分体系。必须先校准每个维度的 0-5 分定义和评分锚点，使不同来源的候选能在同一口径下比较。

扩展后的九个维度：

| 维度 | 来源 | 评分说明 |
|---|---|---|
| privacy_coverage | WHI-266 item-3 | 隐私覆盖面：R1 金额/R2 余额/R3 身份/R4 业务逻辑/R5 交易图/R8 订单流 |
| compliance_capability | WHI-266 item-3 | KYC/AML、transfer policy、issuer controls、监管动作、recovery |
| selective_disclosure | WHI-266 item-3 | 6 维向量完整性：authority/trigger/payload/scope/revocability/leakage |
| deployment_lightweight | WHI-266 item-3 | 是否符合 Mantle 轻量目标（无新链/桥/全节点/硬分叉） |
| engineering_delta | WHI-266 item-3 | 对 Mantle、钱包、indexer、DeFi、桥、发行流程的改动面 |
| maturity | WHI-266 item-3 | 标准、实现、审计、生产部署、团队/生态 |
| mantle_fit | WHI-266 item-3 | 与 Mantle institutional/private RWA 和 B20 类比的匹配度 |
| vendor_protocol_lock_in | 新增 | 厂商/协议锁定程度：是否依赖单一厂商 KMS/gateway/coprocessor/chain，是否有可替换 backend 路径，ERC-7984 等中立接口是否隔离后端，商业/license 约束 |
| performance_predictability | 新增 | 性能可预测性与生产化运维：FHE/ZK/TEE latency 是否可度量，SLA 是否可定义，硬件依赖和运维模型是否透明，独立验证状态 |

校准规则：
1. WHI-267 已给 Zama 打分（privacy 4, compliance 3, disclosure 3, lightweight 3, eng delta 3, maturity 3, mantle fit 4），本 item 应以此为锚点校准其余候选。
2. WHI-270 已给非 Zama 候选在五维简化 rubric（RWA/合规相关性、轻量集成、选择性披露、成熟度、Mantle 适配）打分，需要映射和扩展到九维。
3. WHI-268 product/UX addendum 可用于调节 maturity 和 mantle_fit 的边界分，但不推翻 WHI-266 主 rubric。
4. WHI-266 轻量级一票否决仍生效：非轻量方案 mantle_fit 最高不超过 3，除非明确定位为长期协议路线。
5. 厂商自报性能降权：未独立验证的 TPS/latency/photonic benchmark 只影响 gap/risk，不直接给 maturity 或 performance_predictability 高分。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1

### item-3: 主对比矩阵

本项产出核心交付物：全候选 × 九维 rubric 的主对比矩阵。每个候选的每个维度必须有分数（0-5）、一句话理由和证据锚点（前序 final 路径 + commit SHA 或外部 URL + 访问日期）。

矩阵结构：

| 候选路线 | privacy | compliance | disclosure | lightweight | eng_delta | maturity | mantle_fit | lock_in | perf_predict | 总评 | 路线 bucket |
|---|---|---|---|---|---|---|---|---|---|---|---|

矩阵填充规则：
1. Zama 分数以 WHI-267 item-7 为基准，补充 lock_in 和 perf_predict 两项新分。
2. Inco 分数以 WHI-270 item-7 五维分为基础，扩展到九维，必须区分产品路线和 PoC 代码。Inco confidential ERC20 framework（WHI-270 Inco code PoC，commit `bb39e4f788742121f2fc93de33af58758360545b`）是 Inco 路线的工程证据锚点，必须在 Inco 行的 engineering_delta 和 maturity 评分中明确引用，与 Optalysys（item-6 性能/生产化约束参考）区分。
3. ERC-3643 + confidential overlay 是组合路线，分数需综合 WHI-269（合规底座）和 WHI-267/WHI-270 对应 backend 评估。
4. B20-like native design 是 WHI-269 phase-2 路线，天然触发轻量级一票否决。
5. VOSA-RWA、Nightfall/EY、Fhenix/CoFHE 以 WHI-270 分为基础扩展。
6. Railgun/Privacy Pools、Paladin、Optalysys、Aztec/Starknet/EIP-8182 不独立参与路线 bucket 排序，但仍需完整九维分数以便横向对照。
7. 每条路线的分数相加不作为排序依据；bucket 先由 item-1 的路线能力门决定。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1, item-2

### item-4: 分叉视图一 — private token ledger vs private business-state ledger

本项单独建立 token ledger 隐私和 business-state ledger 隐私的分叉对照，防止在主矩阵中把两种不同隐私目标混为一谈。

定义（继承 WHI-266 item-3 和 WHI-268 item-3）：
- **Private token ledger**：隐藏 token 金额、余额、冻结余额等 accounting 数据；地址图和交易存在性可见或不可见取决于方案。对应 WHI-266 的 R1 amount + R2 balance + 可选 R3 identity。
- **Private business-state ledger**：隐藏合约逻辑、业务状态、多方协作流程和决策过程；不限于 token 金额。对应 WHI-266 的 R4 business logic/state。

分叉视图需回答：
1. 每条候选路线的隐私目标是 token ledger、business-state ledger 还是两者？
2. Mantle phase 1 的产品底线是 private token ledger（即 CCT minimum）；如果一个候选主要解决 business-state privacy（如 Paladin），它的 CCT 适配性如何？
3. 候选如果同时覆盖 token 和 business-state（如 Aztec），其 Mantle 轻量集成代价如何？
4. 账户模型（ERC-7984/OZ/fhEVM）vs UTXO/note 模型（Railgun/Privacy Pools/EIP-8182）对 token ledger 隐私的不同取舍（继承 WHI-268 item-3 比较结论）。

输出格式：分叉对照表 + mermaid 分叉决策图。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1, item-3

### item-5: 分叉视图二 — 部署形态视图

本项按 application/contract-only、coprocessor/backend、native precompile/protocol 三类部署形态分组，映射每条候选路线的集成形态和 Mantle 工程改动。

三类部署形态（继承 WHI-266 item-6 和 WHI-269 item-6）：

| 部署形态 | 定义 | Mantle 工程代价 | 典型候选 |
|---|---|---|---|
| application/contract-only | 纯应用层 Solidity 合约 + SDK/wrapper/observer service | 最低：无协议改动、无新桥、可独立 PoC | ERC-3643 application 路线、VOSA-RWA |
| coprocessor/backend | 应用合约 + 外部 FHE/TEE/ZK coprocessor/backend 服务 | 中等：需 sidecar/operator dependency、callback/relay、KMS/Gateway | Zama + ERC-7984、Inco Lightning、Fhenix/CoFHE |
| native precompile/protocol | Mantle 执行客户端改动、硬分叉、新 precompile 或协议层 shielded pool | 最高：需双客户端实现、fraud proof 一致性、治理/审计 | B20-like native、EIP-8182、Aztec-style |

每个候选路线必须映射到一个主要部署形态和可选的次要形态。部署视图还需回答：
1. 部署形态与轻量级一票否决的关系：application/contract-only 通常 pass，coprocessor/backend 需看具体 operator dependency，native 默认 fail 除非定位为长期。
2. 混合部署是否可行：例如 phase 1 用 application + coprocessor，phase 2 再引入 native precompile。
3. 每种形态下的运维模型、SLA 和信任假设差异。

输出格式：部署形态分组表 + mermaid 分层图。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-1, item-3

### item-6: FHE 性能与生产化约束视图

本项单独建立 FHE/TEE/ZK 性能和生产化约束视图，把 Optalysys 作为约束参考而非候选路线。

覆盖内容：
1. **FHE performance baseline**：Zama fhEVM 的 encrypted add/comparison/select 的已知延迟和吞吐量约束（从 WHI-267 和 coprocessor final 提取）；Fhenix CoFHE 的已知/声称性能差异。
2. **TEE performance reference**：Inco Lightning TEE-first model 的延迟/信任/硬件约束（从 WHI-270 Inco profile 提取）。
3. **ZK proof constraints**：PSE dashboard 的 Groth16/Halo2 gas 和 proving time（从 WHI-268 提取）；Privacy Pools/Railgun/EIP-8182 的 proof cost。
4. **Optalysys productionization reference**（单列）：photonic acceleration 叙事、FHE data movement wall、硬件依赖、SLA 所有权问题。标注为 vendor self-report，不可作为性能证据直接打分。
5. **生产化约束 checklist**：每条依赖 FHE/TEE/ZK 的候选路线需回答：(a) latency budget 是否可度量；(b) SLA 是否可定义；(c) 硬件依赖是否透明；(d) 运维模型是谁的责任；(e) 是否有独立验证。

输出格式：性能约束对照表 + Optalysys 参考摘要 + 生产化 checklist。

- **优先级（Priority）**: medium
- **依赖（Dependencies）**: item-3

### item-7: 路线裁决表

本项基于 item-3 主矩阵和 item-4/5/6 分组视图，产出最终路线裁决表。每条路线必须被归入以下 bucket 之一：

| Bucket | 定义 | 裁决条件 |
|---|---|---|
| 主推 | Mantle phase 1 最值得优先投入的路线 | 通过 standalone-route gate + 九维综合最优 + 无 critical gating item 或有可信近期解决路径 |
| 备选 | Phase 1 的 fallback 路线或 phase 2 主候选 | 通过 standalone-route gate + 存在明确降权项但可作为替代 |
| 局部补强 | 不独立承载路线，但其组件/能力可增强主推或备选路线 | 不通过 standalone-route gate 但在特定维度有高价值 |
| 参考 | 提供 benchmark、约束或设计借鉴，不应被当作实现路线 | 主要是 architecture/performance/standard benchmark |
| 出局 | 作为 Mantle phase 1 直接路线明确不可行 | 需要新链/非 EVM VM/硬分叉/协议 activation，或完全缺少 RWA issuer controls |

裁决要求：
1. 每条路线的 bucket 裁决必须有理由和证据路径。理由必须可回溯到主矩阵分数和分组视图。
2. 抽查 ≥5 个裁决理由能否回溯到前序 final 或外部源（满足 issue 验收标准中的 review 要求）。
3. 复核裁决是否严格来自矩阵，而非对 Zama 或任何厂商的主观偏好。
4. 如果主推路线需要 Mantle host-chain support 但尚未确认，必须标注为 gating item，不得假设已解决。
5. 对于同时可作为路线和组件的候选（如 Fhenix 可作为 backend 替代），分开给出路线 bucket 和组件补强价值。

**主推-selection synthesis rule**（round 2 新增，回应 review finding #1）：

WHI-270 bucket-decision rule 仅完成 route-capable vs component/reference 的初筛分类，且明确声明"不是路线选择结论"。从多个 route-gate-passing 候选中选出唯一主推属于 WHI-271 新增职责，必须有定义明确、可复现的方法，不得依赖未定义的"综合最优"判断。

**步骤 1：Gate-first 过滤。** 仅 standalone-route gate = pass 的候选进入主推竞争。不通过 gate 的候选直接归入局部补强/参考/出局，不参与后续排序。

**步骤 2：维度优先级排序（dimension-priority ordering）。** 在 gate-passing 候选之间，采用 lexicographic comparison with dimension priority ordering 而非分数加总。九维按以下优先级排列（高→低）：

1. compliance_capability（合规能力）— Mantle CCT 的核心产品要求，不可妥协
2. selective_disclosure（选择性披露）— CCT 区别于普通 privacy token 的关键差异化
3. mantle_fit（Mantle 适配）— 直接决定 phase 1 可落地性
4. deployment_lightweight（轻量集成）— Mantle 轻量级一票否决的量化延伸
5. privacy_coverage（隐私覆盖面）— CCT 基础能力
6. engineering_delta（工程改动面）— 落地成本
7. maturity（成熟度）— 实施风险
8. vendor_protocol_lock_in（厂商锁定）— 长期战略风险
9. performance_predictability（性能可预测性）— 生产化运维风险

比较规则：按优先级从高到低逐维比较。若候选 A 在更高优先级维度的分数严格高于候选 B，则 A 优于 B，无论低优先级维度的分数如何。若某维度分数相同，向下一维度比较。若所有九维分数均相同，标注为"矩阵无法区分"，由 item-8 WHI-272 约束优先级和 gating item 严重性决定。

**步骤 3：Pairwise-elimination 验证。** 对 gate-passing 候选进行两两配对比较，验证步骤 2 的排序结果是否一致。若出现非传递性（A > B > C > A），说明维度优先级排序在具体分数分布下无法产生全序，须在裁决表中标注并说明冲突维度。此时退回到逐维拆解，在裁决理由中分别说明每对冲突候选的优劣权衡。

**步骤 4：Anti-vendor-preference check。** 裁决完成后，执行以下检查：
- (a) 将主推候选的路线名称替换为匿名标签（Route-X/Y/Z），仅保留分数和证据路径，重新检查裁决是否仍然成立。
- (b) 检查主推候选是否在任何维度获得了无证据支撑的高分（分数 ≥4 但 evidence_anchor 为 vendor_claimed 或 absent）。
- (c) 检查是否存在另一个 gate-passing 候选在 compliance_capability 或 selective_disclosure（前两优先级维度）上与主推得分相同但在其他维度被不合理降分。
- 若 (a)/(b)/(c) 任一项触发，裁决理由中必须增加专门段落说明为何仍选择该主推，或调整裁决。

输出格式：路线裁决表 + 裁决理由逐条展开 + anti-vendor-preference check 结果附录。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-3, item-4, item-5, item-6

### item-8: WHI-272 协议设计约束清单

本项从路线裁决和主矩阵中提取对 WHI-272 协议设计的设计约束，包括：

1. **必须继承的接口和能力**：基于主推路线，WHI-272 协议设计必须支持的接口（如 ERC-7984 confidential token interface、ERC-3643 identity integration、issuer controls、selective disclosure primitives）。
2. **必须避免的反模式**：从 WHI-268 anti-pattern checklist、WHI-267 risk register 和 WHI-270 gap register 中提取，转化为协议设计级约束（如不得依赖 single full-history viewing key、不得假设 ERC-20 DeFi 兼容、不得省略 gas sponsor/paymaster）。
3. **暂不进入 phase 1 的能力**：从 WHI-269 phase boundary table 和本 item-7 路线裁决中提取 phase 2/out-of-scope 能力，作为 WHI-272 的 non-goal boundary（如 native precompile、private identity、fully private DeFi、order-flow privacy）。
4. **Backend maturity gate**：从 WHI-269 gate statement 继承，要求 WHI-272 设计必须支持 backend 可替换性或至少不与单一 backend 绑死。
5. **Disclosure governance requirements**：从 WHI-267 ACL/observer 风险和 WHI-268 disclosure matrix 提取，要求 WHI-272 设计必须内建 scoped/logged/revocable disclosure，而非后补。
6. **Bridge/redeem boundary**：从 WHI-266 bridge/redeem gap 和 WHI-267 redeem lifecycle 提取，明确赎回时何时需要 plaintext disclosure 以及 failure path。

输出格式：结构化约束清单，每条约束附来源 final 路径和 commit SHA。

- **优先级（Priority）**: high
- **依赖（Dependencies）**: item-7

## 字段（Fields）

| 字段 | 描述 | 适用范围 |
|-------|-------------|------------|
| route_id | 候选路线的标准 ID，用于矩阵和裁决表中一致引用 | all |
| rubric_score | 九维 rubric 的逐维分数 (0-5)，附一句话理由 | item-2, item-3, item-7 |
| evidence_anchor | 每个分数/结论的证据来源：前序 final 路径 + commit SHA 或外部 URL + 访问日期 | all |
| route_bucket | 主推 / 备选 / 局部补强 / 参考 / 出局 | item-7 |
| standalone_route_gate | pass / fail + 理由，判断候选是否能独立承载 CCT 路线 | item-1, item-7 |
| ledger_type | private_token_ledger / private_business_state_ledger / both / neither | item-4 |
| deployment_shape | application_contract_only / coprocessor_backend / native_precompile_protocol / hybrid | item-5 |
| privacy_backend | Zama_fhEVM / Inco_Lightning / Fhenix_CoFHE / ZK_circuit / TEE / none / custom | item-3, item-5, item-6 |
| lock_in_factors | 厂商/协议/硬件/license 锁定因素列表 | item-2, item-3 |
| performance_evidence | measured / vendor_claimed / roadmap / absent + 具体数据引用 | item-6 |
| whI272_constraint_type | must_inherit / must_avoid / phase1_non_goal / backend_gate / disclosure_req / bridge_boundary | item-8 |
| gating_item | 阻塞路线落地的关键未解决问题 | item-3, item-7 |
| reuse_class | direct_reuse / bounded_reuse / new_synthesis / reference_only / soft_input | all |

## 图示预期（Diagram Expectations）

| ID | 类型 | 描述 | 格式 | 适用范围 |
|----|------|-------------|--------|------------|
| diag-1 | matrix | 九维 rubric 主矩阵热力图：全候选 × 九维分数的可视化对比 | mermaid/table | item-3 |
| diag-2 | fork | Private token ledger vs private business-state ledger 分叉视图：每条路线映射到 ledger 类型，配合 account-model vs note-model 对照 | mermaid flowchart | item-4 |
| diag-3 | layer | 三类部署形态分层图：application/contract-only、coprocessor/backend、native precompile/protocol，每层映射候选路线 | mermaid flowchart | item-5 |
| diag-4 | comparison | FHE/TEE/ZK 性能约束对照图：按 backend 类型比较延迟/信任模型/硬件依赖，Optalysys 标注为参考 | mermaid/table | item-6 |
| diag-5 | verdict | 路线裁决决策树/裁决表可视化：从 standalone-route gate 到 bucket 分配的决策流程 | mermaid flowchart | item-7 |
| diag-6 | checklist | WHI-272 设计约束来源追溯图：约束 → 来源 final/item → 约束类型 | mermaid flowchart | item-8 |

## 来源要求（Source Requirements）

| ID | 类型 | 描述 | 最少数量 |
|----|------|-------------|-----------|
| src-1 | prior_final | WHI-266 需求框架 final：rubric 定义、能力模型、证据复用映射、Mantle 轻量约束、Inco/Optalysys 分类边界 | 1 |
| src-2 | prior_final | WHI-267 Zama 深挖 final：架构、标准张力、生命周期模型、风险登记册、rubric 分数、裁决 | 1 |
| src-3 | prior_final | WHI-268 PSE 约束 final：阻塞项分类、account vs note 模型对比、反模式清单、产品/UX rubric 补充、披露矩阵 | 1 |
| src-4 | prior_final | WHI-269 合规 token 扩展 final：合规能力模型、B20 骨架、ERC-3643 基线、阶段边界表、后端成熟度门、披露向量 | 1 |
| src-5 | prior_final | WHI-270 候选 survey final：候选画像、筛选裁决、rubric 可回溯矩阵、Inco code PoC、gap 登记册、bucket 决策规则 | 1 |
| src-6 | prior_privacy_final | evm-privacy-research 已接受的 finals，涵盖 ERC-7984、confidential coprocessor、VOSA、shielded pool、Aztec、EEA benchmark、隐私 EIPs；每条结论需附路径和 commit SHA | 5 |
| src-7 | prior_compliance_final | compliance-token-standards 已接受的 finals，涵盖 ERC-3643、B20、Mantle 战略；仅在 WHI-269 尚未综合之处复用 | 2 |
| src-8 | external_standard | ERC-7984、ERC-3643、EIP-8182 官方规范，用于接口/标准边界相关结论 | 2 |
| src-9 | external_vendor | Zama 文档、Inco 文档/博客、Fhenix 文档、Optalysys 页面 —— 仅用于前序 finals 尚未覆盖的性能/路线图/部署相关结论；所有厂商声明必须标注 | 按需 |
| src-10 | issue_record | WHI-266 至 WHI-270 依赖验证的 Multica issue 记录；WHI-271 派发与大纲批准 | 1 |
| src-11 | soft_input | WHI-262（Mantle RWA 市场调研，status=done/path absent）和 WHI-263（Mantle CCT 竞品对标，status=in_progress）—— M2/M3 soft inputs；未被消费；按 WHI-266 item-4.4 non-blocking rule 适用 M1-only fallback | 0 |

## 补丁日志（Patch Log）

| 轮次 | 动作 | 目标 | 原因 | 来源 |
|-------|--------|--------|--------|--------|
| 2 | add | item-7: 主推-selection synthesis rule | （major）主推选择方法此前未定义；新增维度优先级排序、两两淘汰验证和反厂商偏好检查，使裁决可回溯到矩阵 | Review finding #1 |
| 2 | add | frontmatter: soft_inputs section | （major）WHI-262/263 soft-input 处理此前缺失；按验收标准新增状态/来源跟踪和 M1-only fallback 声明 | Review finding #2 |
| 2 | add | item-3 rule 2: Inco engineering evidence | （minor）Inco confidential ERC20 framework 此前未绑定为 Inco 路线的工程证据；新增明确引用并附 commit SHA `bb39e4f7` | Review finding #3 |
