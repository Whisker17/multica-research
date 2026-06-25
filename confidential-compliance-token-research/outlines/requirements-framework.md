---
topic: "建立 Confidential Compliance Token 需求框架与证据复用地图"
project_slug: "confidential-compliance-token-research"
topic_slug: "requirements-framework"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "confidential-compliance-token-research/outlines/requirements-framework.md"
  draft: "confidential-compliance-token-research/research-sections/requirements-framework/drafts/round-{n}.md"
  final: "confidential-compliance-token-research/research-sections/requirements-framework/final.md"
  index: "confidential-compliance-token-research/research-sections/_index.md"

scope: |
  M1 分析任务。目标是为「Confidential Compliance Token 调研」项目建立需求框架、术语口径、
  评估 rubric 与证据复用地图。覆盖：项目必须回答的问题、Confidential Compliance Token 能力模型、
  统一 rubric、旧项目证据复用分层、Inco/Optalysys 证据角色分类，以及 9 个后续 section 的目录/索引初稿。
audience: "Mantle 协议/战略团队、RWA/机构业务负责人、合规架构师、研究评审 agent、后续 deep-draft 作者"
expected_output: |
  outline 阶段输出本文件；final 阶段输出
  confidential-compliance-token-research/research-sections/requirements-framework/final.md。
  final 需给出需求框架、统一 rubric、证据复用地图、Confidential Compliance Token 与普通 privacy token /
  普通 compliance token 的区别、项目目录骨架和 _index.md 写入建议。

revision_metadata:
  created_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-23T15:39:12Z"
  last_modified_by: "agent:Deep Research Agent (id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-23T15:39:12Z"

multica_issue_id: "7d7fa951-8160-4b03-a7ae-8ff1a6a9664c"
branch_name: "research/confidential-compliance-token-research/requirements-framework"
base_commit: "1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0"
language: "中文"
mode: "single-issue-lightweight"

reference_inputs:
  direct_reuse:
    - path: "compliance-token-standards/report/final-report.md"
      commit: "79d472632bd30a5354fbec396f807e0bb63bdea1"
      role: "合规 token 标准、Mantle 策略底座、应用层 vs 协议层合规框架"
    - path: "compliance-token-standards/research-sections/base-b20-analysis/final.md"
      commit: "0041e3a1598751a7d121fecc600ba3d6ad42ad05"
      role: "Base B20 precompile 类比、pinned commit 证据边界"
    - path: "compliance-token-standards/research-sections/mantle-compliance-token-strategy/final.md"
      commit: "0041e3a1598751a7d121fecc600ba3d6ad42ad05"
      role: "Mantle 当前合规 token 路线约束、ERC-3643 先行策略、hardfork 窗口不确定"
    - path: "evm-privacy-research/research-sections/privacy-landscape-framework/final.md"
      commit: "0041e3a1598751a7d121fecc600ba3d6ad42ad05"
      role: "隐私 taxonomy、选择性披露向量、轻量级判定标准"
    - path: "evm-privacy-research/research-sections/erc7984-confidential-token/final.md"
      commit: "0041e3a1598751a7d121fecc600ba3d6ad42ad05"
      role: "ERC-7984 confidential token 标准与 OZ 扩展分析"
    - path: "evm-privacy-research/research-sections/confidential-coprocessor/final.md"
      commit: "0041e3a1598751a7d121fecc600ba3d6ad42ad05"
      role: "Zama/Inco/Fhenix bolt-on 机密计算方案、Inco 角色"
    - path: "evm-privacy-research/research-sections/eea-enterprise-benchmark/final.md"
      commit: "1eac19ed837c8e9a4df1bb1594d5b23cc5a2e9f0"
      role: "EEA 企业隐私 7 方案 benchmark 与合约状态隐私参照"
  issue_inputs:
    - "WHI-254 to WHI-261 all queried on 2026-06-23; current status is done. Treat their persisted final artifacts as hard inputs when present."
    - "evm-privacy-research/issue-plan.md was referenced by dispatch but no such file exists in this checkout; use existing outlines/_index and WHI-254..261 issue records as the substitute issue-plan evidence."
  external_inputs:
    - name: "Inco-fhevm/confidential-erc20-framework"
      url: "https://github.com/Inco-fhevm/confidential-erc20-framework"
      commit: "bb39e4f788742121f2fc93de33af58758360545b"
      access_date: "2026-06-23"
      role: "工程 PoC 参考；README states unaudited proof of concept"
    - name: "Optalysys - Tokenised RWAs are a trillion-dollar opportunity but only if privacy scales"
      url: "https://optalysys.com/resource/tokenised-rwas-are-a-trillion-dollar-opportunity-but-only-if-privacy-scales/"
      published: "2026-03-04"
      modified: "2026-05-06"
      access_date: "2026-06-23"
      role: "FHE 性能与生产化参考；不可作为 token framework 候选"
    - name: "Optalysys - Fully Homomorphic Encryption hits the data movement wall"
      url: "https://optalysys.com/resource/fully-homomorphic-encryption-hits-the-data-movement-wall-why-photonics-is-emerging-as-the-way-forward/"
      published: "2026-03-26"
      modified: "2026-04-02"
      access_date: "2026-06-23"
      role: "FHE 数据搬运瓶颈与 photonics 加速参考"
    - name: "Optalysys - Silicon photonics: our approach to acceleration"
      url: "https://optalysys.com/resource/silicon-photonics-our-approach-to-acceleration/"
      published: "2025-10-07"
      modified: "2026-05-06"
      access_date: "2026-06-23"
      role: "硬件/photonic acceleration 参考"
---

# 研究大纲（Research Outline）：建立 Confidential Compliance Token 需求框架与证据复用地图

本项目研究对象不是泛化 privacy token，也不是普通 compliance token，而是 **Confidential Compliance Token**：在 institutional blockchain / private RWA 场景中，把合规资产生命周期、发行方控制、可审计/可披露机制与金额/余额/必要业务状态隐私合并到同一 token 产品口径。

最小判定口径：

| 类型 | 核心目标 | 缺什么 | 本项目关系 |
|------|----------|--------|------------|
| 普通 privacy token | 隐藏金额、余额、身份或交易图 | 缺少发行方控制、合规策略、审计披露、RWA 生命周期 | 只提供隐私原语或候选模块 |
| 普通 compliance token | KYC/AML、转移限制、冻结/强制转移、审计 | 缺少金额/余额/交易隐私 | 只提供合规控制底座 |
| Confidential Compliance Token | 在合规 token 上叠加可治理的机密性，且能按授权披露 | 必须同时解释谁能看、谁能冻、谁能披露、如何桥接/赎回、如何与 DeFi 组合 | 本项目目标 |

本项目默认 Mantle 约束：优先轻量集成现有协议或标准，参考 Base B20 token + private feature 的产品想象，可能锚定 ERC-7984；不默认自建独立隐私链，不默认 hardfork/precompile，除非后续 evidence 显示这是唯一可行路径。

## 研究项（Items）

### item-1：需求拆解与术语口径

拆解 Mantle 为什么做、为谁做、要隐藏什么、谁能披露、如何合规、什么叫轻量。输出术语表和问题树，避免后续 section 把 privacy token、confidential token、compliance token、RWA token 混用。本项还要明确「Base B20 token + private feature」是产品类比，不是直接复制 Base B20 的工程路线。

- **优先级（Priority）**：high
- **依赖（Dependencies）**：none

### item-2：Confidential Compliance Token 能力模型

定义能力模型并给出每项的必要/可选等级：confidential accounting、compliance policy、issuer controls、selective disclosure、auditability、bridge/redeem、DeFi composability。能力模型必须兼容两条来源口径：合规 token 8 类 taxonomy 与 EVM privacy 5 轴/8 需求体系。最终 deep draft 应明确哪些能力是 token 本体必须具备，哪些可由 wrapper、observer、oracle、identity registry 或 external coprocessor 提供。

- **优先级（Priority）**：high
- **依赖（Dependencies）**：item-1

### item-3：统一 Rubric 与评分口径

建立后续候选路线统一评分表，覆盖隐私覆盖面、合规能力、选择性披露、部署形态/轻量级、工程改动面、成熟度、Mantle 适配性。Rubric 必须同时能评估 ERC-3643 + ERC-7984/OZ、Base B20 + private feature、Zama/Inco/Fhenix、VOSA-RWA、Railgun/Privacy Pools、Aztec、EEA enterprise 方案以及 Optalysys 性能参考。

- **优先级（Priority）**：high
- **依赖（Dependencies）**：item-1, item-2

### item-4：证据复用地图与来源加权（Source Weighting）

建立 evidence reuse map，分成 direct reuse、new research required、soft input、out-of-scope 四类。必须列出 compliance-token-standards 与 evm-privacy-research 哪些结论可直接复用，哪些只能作为启发，哪些需要重新查一手来源。特别说明：WHI-254..261 当前已 done，可将 final artifacts 作为 hard inputs；dispatch 中的 `evm-privacy-research/issue-plan.md` 在本 checkout 不存在，deep draft 应改用 `_index.md`、outlines 和 issue records。

- **优先级（Priority）**：high
- **依赖（Dependencies）**：item-1

### item-5：标准/协议候选空间分层

将候选空间按角色分层，而不是同权重堆叠：合规底座（ERC-3643、B20/TIP-20）、confidential token interface（ERC-7984/ERC-7945）、bolt-on confidential compute（Zama/Inco/Fhenix）、privacy transfer pools（Railgun/Privacy Pools/VOSA）、native privacy chain（Aztec）、enterprise privacy systems（EEA 7 方案）、performance/hardware references（Optalysys）。本项必须把 Inco confidential ERC20 framework 归为工程 PoC 参考，把 Optalysys 归为 FHE 性能/生产化参考。

- **优先级（Priority）**：high
- **依赖（Dependencies）**：item-2, item-4

### item-6：Mantle 轻量集成约束与工程改动面

定义「轻量」在本项目中的硬门槛和扣分项：无需新链/新桥/全节点/硬分叉为强正项；新增 sidecar、coprocessor、KMS、observer、identity service 为中等成本；执行客户端 precompile/hardfork、独立 L2/L3、资产迁移为高成本或一票否决。结合 Mantle 当前合规 token 策略结论，短期默认应用层/bolt-on 优先，precompile 是中长期选项。

- **优先级（Priority）**：high
- **依赖（Dependencies）**：item-3, item-5

### item-7：后续研究 Section 切分与依赖顺序

给出 9 个 section 的 order、topic_slug、dependencies、status 初稿，供 Orchestrator 写入 `_index.md`。本项不直接写 `_index.md`，只提出 index entry proposal，因为协议规定 `_index.md` 由 Orchestrator 序列化写入。切分必须能支撑后续 Zama、B20、ERC-7984、VOSA-RWA、Inco、Optalysys 等路线比较。

- **优先级（Priority）**：high
- **依赖（Dependencies）**：item-3, item-4, item-5

### item-8：缺口登记表（Gap Register）与新调研待办（New Research Backlog）

列出不能从旧项目直接复用、必须新调研的问题。例如：ERC-3643 与 ERC-7984/OZ RWA 扩展如何组合；B20 是否有公开 Beryl 后 spec；Mantle 是否需要 bridge/redeem 私有化；监管披露如何避免 FHE ACL 不可撤销问题；Optalysys/硬件加速是否能给出 SLA 或仅是长期性能叙事。

- **优先级（Priority）**：medium
- **依赖（Dependencies）**：item-4, item-5, item-6

### 必备核心表格（Required Core Tables）

Deep draft 应包含以下表格，即便 section 标题有所变化：

1. **必答问题（Must-answer Questions）**

| 问题 | 为何重要 | 必需产出 |
|----------|----------------|-----------------|
| 为什么做 | Mantle institutional blockchain / private RWA 定位，需要差异化而非泛 privacy | 业务动机和不做范围 |
| 为谁做 | 发行方、受监管投资者、合规/审计方、DeFi 集成方看到的数据不同 | 角色/数据可见性矩阵（Actor/data visibility matrix） |
| 要隐藏什么 | 金额、余额、对手方、交易图、业务状态、order flow 不能混为一谈 | 受保护数据 taxonomy（Protected data taxonomy） |
| 谁能披露 | holder、issuer、observer、regulator、smart contract、KMS/TEE operator 权力不同 | 披露权限模型（Disclosure authority model） |
| 如何合规 | KYC/AML、sanctions、transfer restrictions、freeze/force-transfer/recovery、audit | 合规能力模型（Compliance capability model） |
| 什么叫轻量 | 不部署新链/新桥/硬分叉，优先应用层/bolt-on | 轻量门控与评分（Lightweight gate and scoring） |

2. **能力模型（Capability Model）**

| 能力 | 定义 | 最低门槛 | 证据锚点 |
|------------|------------|-------------|------------------|
| confidential_accounting | Token 金额/余额机密性 | 对公共观察者隐藏金额和余额；残余图泄露需标注 | ERC-7984 final；WHI-254 rubric |
| compliance_policy | 转移/铸造/持有规则 | KYC/allowlist/blocklist/jurisdiction 限制由机器强制执行 | compliance-token-standards report；ERC-3643；B20 |
| issuer_controls | 发行方/agent 操作 | mint/burn/pause/freeze/force-transfer/recovery 角色模型明确 | ERC-3643 final；B20 final；OZ ERC7984Rwa |
| selective_disclosure | 授权可见性 | 权限、触发、载荷、范围、可撤销性、泄露向量 | WHI-254；ERC-7984 ObserverAccess；Inco delegated viewing |
| auditability | 可验证的合规历史 | 说明公开审计看到什么 vs 私有审计方看到什么 | compliance token taxonomy；privacy final sections |
| bridge_redeem | 跨链资产生命周期或赎回 | Deposit/withdraw/redeem 路径保持合规与隐私假设 | Base B20 local-branch caveat；需新调研 |
| defi_composability | 与钱包、DEX、借贷、托管方的集成 | 说明金额加密后什么会失效、需要哪种 adapter | ERC-7984 final；Zama/Inco final |

3. **Rubric**

| 评估轴 | 评分形态 | 高分意味着 | 低分意味着 |
|------|-------------|------------------|----------------|
| privacy_coverage | 0-5 + 受保护数据标签 | 隐藏金额/余额和相关 RWA 业务状态，残余泄露有界 | 只隐藏一个字段，或把图/身份/金额留在公开状态 |
| compliance_capability | 0-5 + 能力标签 | 支持身份、转移策略、发行方控制、sanctions、recovery、审计 | 只有隐私，没有可强制执行的合规控制 |
| selective_disclosure | 0-5 + 6 维向量 | 权限/触发/载荷/范围/撤销/审计日志清晰 | 临时 viewing key，或治理薄弱的永久 ACL |
| lightweight_deployment | 0-5 + 否决标记 | 现有 EVM 应用/bolt-on，无新链/新桥/硬分叉/全节点负担 | 需要新链、新桥、硬分叉或定制执行客户端 |
| engineering_delta | 0-5 成本反向计分 | 极少的 Solidity/wrapper/SDK 改动，基础设施依赖隔离 | 大范围客户端/协议重写或定制密码学栈 |
| maturity | 0-5 + 证据类型 | 已审计、生产化或最终标准，存在参考实现 | 草案、未审计、单作者或仅营销材料 |
| mantle_fit | 0-5 + 理由 | 契合 private RWA、OP Stack/Mantle 约束、ERC-7984/B20 产品类比 | 解决不相关的隐私问题或与 Mantle 策略冲突 |

4. **证据复用地图（Evidence Reuse Map）**

| 证据 | 复用类别 | 如何使用 | 边界 |
|----------|-------------|------------|----------|
| compliance-token-standards/report/final-report.md | direct reuse | 合规 token taxonomy、成熟度梯度、Mantle 分阶段策略 | 未覆盖 confidential accounting |
| base-b20-analysis/final.md | direct reuse with boundary | B20 precompile 架构与 policy/RBAC 模型 | Pinned commit；B20Security/redeem/batchBurn/securityIdentifier 仅为 local-branch 信号 |
| mantle-compliance-token-strategy/final.md | direct reuse | Mantle 当前约束、ERC-3643 first 策略、hardfork 不确定性 | 未评估隐私层 |
| privacy-landscape-framework/final.md | direct reuse | 五轴隐私 rubric、选择性披露向量、轻量门控 | 需适配到合规 token 控制 |
| erc7984-confidential-token/final.md | direct reuse | ERC-7984 interface、OZ extensions、ObserverAccess/ACL 注意事项 | ERC-7984 单独只是数值级隐私，不是完整 compliance token |
| confidential-coprocessor/final.md | direct reuse | Zama/Inco/Fhenix 架构及 Mantle bolt-on 影响 | 厂商性能数据须标注为自报/未经核实（self-reported/unverified） |
| vosa/zk/aztec/eea finals | soft-to-direct by use | 候选对比与设计经验 | 不要让非轻量/原生链设计主导产品路线 |
| Inco confidential ERC20 framework | engineering PoC reference | Confidential ERC20 与合规转移规则的合约/接口示例 | README 称其为 unaudited PoC；非生产证据 |
| Optalysys resources | performance/productionization reference | FHE scaling、SLA、data movement、photonic acceleration 相关问题 | 非 token 协议，也非 Mantle 集成候选 |

## 字段（Fields）

| 字段 | 描述 | 适用于 |
|-------|-------------|------------|
| source_anchor | 每条结论使用的 文件路径 / URL / issue id / commit SHA / access date | all |
| evidence_weight | direct_reuse / hard_input / soft_input / engineering_poc / performance_reference / new_research_required | all |
| protected_data | amount, balance, counterparty, graph, business_state, contract_logic, order_flow, metadata | item-2, item-3, item-5 |
| compliance_capabilities | identity_kyc, transfer_policy, issuer_controls, sanctions_blacklist, recovery, legal_metadata, payment_reconciliation, audit_privacy | item-2, item-3, item-5 |
| disclosure_vector | authority, trigger, payload, scope, revocability, residual_leakage | item-2, item-3 |
| lightweight_gate | no_new_chain, no_new_bridge, no_hardfork, no_full_node, sidecar_cost, kms_or_tee_dependency, coprocessor_dependency | item-3, item-6 |
| maturity_status | final_standard, draft_standard, audited, unaudited_poc, production, testnet, marketing_only | item-3, item-5 |
| mantle_fit_rationale | 该来源或路线具体如何帮助 Mantle private RWA | item-3, item-5, item-6 |
| gap_status | answered_by_reuse, needs_primary_research, blocked_by_missing_spec, soft_input_only | item-4, item-8 |

## 图示预期（Diagram Expectations）

| ID | 类型 | 描述 | 格式 | 适用于 |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy | Confidential Compliance Token 概念栈：privacy layer、compliance layer、issuer controls、disclosure/audit layer、bridge/redeem、DeFi adapters | mermaid | item-1, item-2 |
| diag-2 | comparison | 证据复用地图，展示 compliance-token-standards、evm-privacy-research、Inco PoC、Optalysys 性能参考和新调研缺口 | mermaid | item-4 |
| diag-3 | flow | 角色/数据可见性流：holder、issuer、regulator/auditor、observer/KMS、public chain、DeFi protocol | mermaid | item-2, item-3 |
| diag-4 | roadmap | 项目 index proposal 的 9-section 依赖/顺序图 | mermaid | item-7 |

## 来源要求（Source Requirements）

| ID | 类型 | 描述 | 最少数量 |
|----|------|-------------|-----------|
| src-1 | prior_research_final | compliance-token-standards final report 及相关 final sections，附 commit SHA | 3 |
| src-2 | prior_privacy_final | evm-privacy-research final sections，必要时附 WHI-254..261 status/ledger | 5 |
| src-3 | official_spec | 若结论超出既有研究，则需 ERC-7984、ERC-3643、B20/TIP-20 的 ERC/EIP 或官方文档 | 2 |
| src-4 | code_analysis | Inco confidential ERC20 framework 及任何用作工程证据的后续候选代码 | 1 |
| src-5 | external_vendor_reference | Optalysys 页面或其他厂商页面，标注 access date 与角色 | 2 |
| src-6 | issue_record | WHI-254..261 与 WHI-266 的 Multica issue records | 1 |

### 项目索引提案（Project Index Proposal）

Research Agent 不得直接写 `_index.md`。下表为供 Orchestrator 序列化使用的初始 index 提案。

| order | topic_slug | multica_issue_id | final_path | dependencies | status |
|-------|------------|------------------|------------|--------------|--------|
| 1 | requirements-framework | 7d7fa951-8160-4b03-a7ae-8ff1a6a9664c | confidential-compliance-token-research/research-sections/requirements-framework/final.md | - | planned |
| 2 | erc3643-erc7984-composition | TBD | confidential-compliance-token-research/research-sections/erc3643-erc7984-composition/final.md | requirements-framework | planned |
| 3 | base-b20-private-feature-analogy | TBD | confidential-compliance-token-research/research-sections/base-b20-private-feature-analogy/final.md | requirements-framework | planned |
| 4 | zama-oz-confidential-rwa-path | TBD | confidential-compliance-token-research/research-sections/zama-oz-confidential-rwa-path/final.md | requirements-framework, erc3643-erc7984-composition | planned |
| 5 | inco-confidential-erc20-poc-fit | TBD | confidential-compliance-token-research/research-sections/inco-confidential-erc20-poc-fit/final.md | requirements-framework, erc3643-erc7984-composition | planned |
| 6 | vosa-rwa-and-shielded-pool-tradeoffs | TBD | confidential-compliance-token-research/research-sections/vosa-rwa-and-shielded-pool-tradeoffs/final.md | requirements-framework | planned |
| 7 | bridge-redeem-and-defi-composability | TBD | confidential-compliance-token-research/research-sections/bridge-redeem-and-defi-composability/final.md | erc3643-erc7984-composition, base-b20-private-feature-analogy | planned |
| 8 | fhe-performance-and-production-sla | TBD | confidential-compliance-token-research/research-sections/fhe-performance-and-production-sla/final.md | zama-oz-confidential-rwa-path, inco-confidential-erc20-poc-fit | planned |
| 9 | mantle-route-comparison-and-recommendation | TBD | confidential-compliance-token-research/research-sections/mantle-route-comparison-and-recommendation/final.md | erc3643-erc7984-composition, base-b20-private-feature-analogy, zama-oz-confidential-rwa-path, inco-confidential-erc20-poc-fit, vosa-rwa-and-shielded-pool-tradeoffs, bridge-redeem-and-defi-composability, fhe-performance-and-production-sla | planned |

## 补丁日志（Patch Log）

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
