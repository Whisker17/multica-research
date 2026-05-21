---
topic: "企业级区块链核心需求与评估框架"
project_slug: "mantle-base-codebase-evaluation"
topic_slug: "enterprise-requirements-framework"
github_repo: "Whisker17/multica-research"
round: 2
status: candidate

artifact_paths:
  outline: "mantle-base-codebase-evaluation/outlines/enterprise-requirements-framework.md"
  draft: "mantle-base-codebase-evaluation/research-sections/enterprise-requirements-framework/drafts/round-{n}.md"
  final: "mantle-base-codebase-evaluation/research-sections/enterprise-requirements-framework/final.md"
  index: "mantle-base-codebase-evaluation/research-sections/_index.md"

scope: "从 mantle-enterprise-blockchain 研究成果中提取八大核心组件需求，按六类 ToB 业务场景（Payment L3、RWA/代币化资产、xStocks/证券、合规稳定币、资管、供应链）建立差异化需求矩阵与约束权重，构建结构化评估矩阵，梳理约束传播链，并将需求映射到具体的 codebase 层次（op-node / op-geth / predeploy / middleware）。"
audience: "Mantle 技术决策层、企业区块链产品团队、架构评审委员会"
expected_output: "需求维度表（8 组件 × 具体需求指标）、场景原型矩阵（6 场景 × 8 组件权重 × 约束传播链映射）、Codebase 层级映射、评估矩阵模板（10 轴 + 三组战略权重）、约束传播链总结、全部基于 mantle-enterprise-blockchain 研究证据。"

revision_metadata:
  created_by: "deep-research-agent"
  created_at: "2026-05-21T13:00:00Z"
  last_modified_by: "deep-research-agent"
  last_modified_at: "2026-05-21T15:00:00Z"
---

# Research Outline: 企业级区块链核心需求与评估框架

## Items

### item-1: 八大核心组件需求提取与分类

从 WHI-386 的企业区块链设计总览和 WHI-349 的六维需求框架中，系统提取八大核心组件（执行层、共识与终局性、隐私层、合规与身份、访问控制、DA 与数据主权、互操作性、业务组件）的具体企业需求指标。每个组件需明确功能需求、性能基线和企业级约束条件，形成 8×N 的需求维度表。

- **Priority**: high
- **Dependencies**: none

### item-2: 场景原型矩阵：六类 ToB 业务的差异化需求分析

基于 WHI-388 的企业可接受性矩阵（§6.1–§6.4）、WHI-389 的业务场景影响矩阵（§5.2、§6）和 WHI-386 的产品面→路径映射（§4），建立覆盖六类核心 ToB 场景的原型矩阵。每个场景原型提供三层分析：

**六类场景原型**：
1. **Payment L3**（含 B2C 授权、B2B 结算、商户最终提款）：10K+ TPS、亚秒 UX 确认、Travel Rule 元数据、制裁筛查、Payment Lane 调度、sequencer 保证金经济最终性（≥60–80% 未证明敞口）、L3→L2→L1 提款路径
2. **RWA / 代币化资产**（含代币化基金、投资者注册表）：ERC-3643/T-REX 发行工厂、IdentityRegistry + PolicyRegistry、私有投资者注册表（租户 DA）、选择性披露/查看密钥、审计导出、单区 DVP 原子性、跨区 DVP 需共享排序器（Phase-2）、合规桥/许可 DeFi 路由器
3. **xStocks / 证券**（分 HFT 与非 HFT 两支）：加密 mempool 防 sequencer 抢先交易、市场监控模块、交易时段限制、投资者资格钩子、FCFS 公平排序日志、审计披露工作流；HFT 分支结构性需 L1 BFT（WHI-387），非 HFT 分支可用 L3 + 加密 mempool
4. **合规稳定币**（从 Payment 与 RWA 交叉提取）：类型化最终性预言机、风险分级交易限制、发行方策略注册表（铸造/销毁/冻结权限）、储备证明接口、支付对账导出、合规 DEX/路由器、桥消息合规决策哈希；路径分流——单发行方→L3 Zone、多发行方+公共流动性→L2、CBDC/主权→L1
5. **资管**（从 RWA+托管+资金+SaaS 行综合提取）：资产冻结/解冻控制、每租户 Sequencer+DA+KMS 分区、查看密钥管理、带策略门控的提款队列、NAV/储备证明预言机、投资者入驻工作流（KYB+SSO+API 密钥）、托管集成适配器、角色范围私有浏览器
6. **供应链工作流**（corpus 中非一级原型，基于 WHI-349 §2.1 Need-to-Know 模式综合推导）：链下商业文档存储+链上承诺、参与方投影状态（EVM 不原生适配 Canton 式投影隐私，WHI-349 §2.5 明确警告）、多方 DVP 变体、选择性披露；L2 不适配（WHI-388 §6.3）、L3 中等适配需自定义隐私层——标注为诚实缺口

**每个原型包含**：
- (a) 差异化 codebase 层面需求（具体到模块和接口）
- (b) 八大核心组件维度的约束权重（LOW / MEDIUM / HIGH / VERY HIGH / EXTREME，引用 WHI-388/389 具体行号）
- (c) 约束传播链映射（隐私→DA、合规→Sequencer/EVM 兼容性、终局性→产品承诺、访问控制→桥架构 等）

- **Priority**: high
- **Dependencies**: item-1

### item-3: 十维评估矩阵模板构建

基于 WHI-390 的十维比较矩阵（企业自主权、终局性速度、隐私能力、合规灵活性、开发成本、上市时间、以太坊安全继承、生态兼容性、运营简易度、业务可扩展性）构建标准化评估模板。整合三组战略权重模型（快速企业收入、机构结算基础设施、企业平台规模），使矩阵可用于不同战略目标下的方案打分。将 item-2 的场景原型约束权重映射到十维矩阵的权重分配，确保矩阵能反映不同场景的差异化优先级。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 约束传播链梳理与形式化

从 WHI-386 的组件依赖矩阵（§3, lines 505–514）中提取八条核心约束传播链：(1) 共识→终局性→结算（BFT/ZK/双语义决策），(2) 隐私边界→DA 策略→L1 锚定模型→互操作性（Validium/私有 DA），(3) 合规深度→执行层修改→EVM 兼容性影响，(4) 访问控制模型→强制包含策略→桥架构，(5) 支付性能→通道设计→代币标准（Tempo 式 Payment Lane），(6) 数据主权→存储分层→运营模型（Zone DA/审计 DA/公共承诺分离），(7) 以太坊安全性→证明系统→成本/运维，(8) 身份标准→凭证可携带性→桥消息格式→互操作协议。形式化描述各链的因果关系、约束传播方向和决策空间收窄效应。标注每条链在六类场景原型中的激活模式差异。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-5: Codebase 层级需求映射

将八大组件需求映射到具体的 codebase 实现层次。基于 M3 可行性设计报告的四层架构（middleware / op-node / op-geth + predeploy / data layer）和 16 个新增组件（N1-N16）、6 个修改组件（M1-M6）的工程分解，建立需求→模块→代码层的三级追溯表。特别标注 predeploy 合约地址基线（0x42...0020-0034）的对应关系。

- **Priority**: high
- **Dependencies**: item-1, item-4

### item-6: 间隙分析与优先级排序

整合 WHI-350 的九维间隙分析（数据隐私 Critical / 访问控制 High / 身份管理 High / 合规框架 High / 终局性 Medium / DA 灵活性 Medium / 互操作性 Medium / EVM 兼容性 No Gap）和 17 个优先切入点的 V×F 评分方法论，将间隙严重度与需求维度表对齐，产出按优先级排序的需求实现路线图输入。

- **Priority**: medium
- **Dependencies**: item-1, item-5

### item-7: L1/L2/L3 方案路径需求满足度对标

基于 WHI-387/388/389 的三条方案路径分析，对标各方案在八大组件需求上的满足程度。使用 WHI-390 的星级评分矩阵（★-★★★★★）作为锚定参考，产出每条路径的需求覆盖热力图。引入 item-2 的场景原型视角，按场景×路径交叉分析满足度（例如 Payment L3 在 L3 路径强适配但大额赎回为瓶颈，xStocks HFT 在 L1 路径强适配但 L2/L3 结构性不足），分析各路径的需求满足"天花板"和不可弥补的结构性缺陷。

- **Priority**: medium
- **Dependencies**: item-1, item-2, item-3, item-6

### item-8: Sidecar 隐私层（Paladin）补充评估

评估 WHI-390 提出的 Sidecar 隐私层方案（Paladin: Noto/Zeto/Pente/Atom 域）作为非侵入式补充路径的需求满足能力。分析其在不修改核心 codebase 前提下可覆盖的隐私、合规和数据主权需求范围，以及与 L2/L3 方案的组合效应。

- **Priority**: medium
- **Dependencies**: item-1, item-4, item-7

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| requirement_dimensions | 该 item 涉及的具体需求指标清单，含功能需求、性能基线和企业约束 | all |
| evidence_sources | 支撑该 item 分析的具体文献引用（WHI-xxx 节号 + 关键数据点） | all |
| mantle_current_state | Mantle 当前 codebase 在该维度的现状评估（含 WHI-350 间隙评分） | item-1, item-5, item-6 |
| scenario_archetype_profile | 每个场景原型在该维度的差异化需求描述：(a) codebase 级需求清单、(b) 八组件约束权重矩阵、(c) 激活的约束传播链及其场景特异性参数 | item-2, item-3, item-4, item-7 |
| codebase_mapping | 需求到 op-node / op-geth / predeploy / middleware 的层级映射 | item-1, item-5 |
| constraint_impact | 约束传播链在该维度的影响描述，含上下游依赖和决策空间变化 | item-4, item-5, item-8 |
| path_coverage | L1/L2/L3/Sidecar 各方案在该维度的需求满足度（星级 + 定性说明），按场景原型交叉呈现 | item-3, item-7, item-8 |
| implementation_effort | 工程实现的人月估算和阶段归属（Phase 1/2/3），引用 M3 工作量数据 | item-5, item-6 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | hierarchy | 企业需求总览图：展示八大核心组件的层次关系与分组（基础设施层：执行/共识/DA；企业治理层：隐私/合规/访问控制；连接层：互操作性；商业层：业务组件），以及六维需求框架（数据主权、合规审计、访问控制、系统共存、运营可控、开发体验）的覆盖映射 | mermaid | item-1, item-2 |
| diag-2 | comparison | 评估矩阵模板图：展示十轴雷达评估框架的维度布局，叠加三组战略权重模型（快速收入/机构结算/平台规模）的权重分配差异，以及 L1/L2/L3 方案的典型得分轮廓对比 | mermaid | item-3, item-7 |
| diag-3 | flow | 约束传播链流程图：展示八条核心约束传播路径的因果链、决策节点和空间收窄效应，标注各节点的关键参数（如隐私级别选择如何限定 DA 选项，合规深度如何影响 EVM 兼容性），以及六类场景的激活差异 | mermaid | item-4, item-5 |
| diag-4 | comparison | 场景原型×组件权重热力图：以六类场景原型为行、八大核心组件为列，呈现每个单元格的约束权重等级（LOW/MEDIUM/HIGH/VERY HIGH/EXTREME），叠加主激活约束传播链的标识，使不同场景的需求差异一目了然 | mermaid | item-2, item-7 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | internal_research | mantle-enterprise-blockchain 项目的研究成果文档（WHI-386~390、WHI-343/348/349/350、M3 可行性设计报告），作为本研究的核心一手证据来源。这是唯一的必需证据基础。 | 10 |
| src-2 | code_analysis | Mantle codebase 中与企业需求相关的模块分析（op-node、op-geth、predeploy 合约、middleware 层），引用 M3 报告的组件编号 N1-N16 / M1-M6 | 4 |
| src-3 | industry_reports | 【可选/验证用】企业区块链行业对标案例（Canton/Digital Asset、Prividium、Tempo Zones、Hyperledger Besu、Paladin）的公开文档和技术规格。仅用于交叉验证 mantle-enterprise-blockchain 研究中已有的对比结论，不作为独立必需证据。 | 0 |
| src-4 | official_docs | 【可选/验证用】OP Stack / Ethereum 相关的官方技术文档。仅在需要验证 EVM 兼容性、终局性模型或 DA 约束的具体技术细节时引用，不作为独立必需证据。 | 0 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 2 | modify_item | item-2 | [scenario-matrix] 将三客户画像分割（传统金融/Web3 原生/支付）替换为六类 ToB 场景原型矩阵（Payment L3、RWA/代币化资产、xStocks/证券、合规稳定币、资管、供应链），每个原型包含 (a) 差异化 codebase 需求 (b) 八组件约束权重 (c) 约束传播链映射。基于 WHI-388 §6、WHI-389 §5.2/§6、WHI-386 §4 的场景信号综合提取 | deep-research-agent |
| 2 | modify_source_req | src-3 | [src-scope] 从必需证据降级为可选/验证用。issue 明确标注新增行业调研为 out of scope，主要证据基础应排他性地依赖 mantle-enterprise-blockchain 的八份核心文档 | deep-research-agent |
| 2 | modify_source_req | src-4 | [src-scope] 从必需证据降级为可选/验证用。同 src-3 理由，官方文档仅在需要验证具体技术细节时引用 | deep-research-agent |
| 2 | add_field | scenario_archetype_profile | 新增场景原型维度字段，支撑 item-2 的六场景矩阵分析在 item-3/4/7 中的交叉引用 | deep-research-agent |
| 2 | add_diagram | diag-4 | 新增场景原型×组件权重热力图，可视化呈现六场景在八组件上的约束权重差异 | deep-research-agent |
| 2 | modify_item | item-3 | 增加与 item-2 场景原型约束权重到十维矩阵权重分配的映射要求 | deep-research-agent |
| 2 | modify_item | item-4 | 扩展约束传播链从四条到八条（完整覆盖 WHI-386 §3 lines 505–514），增加每条链在六类场景中的激活模式差异标注 | deep-research-agent |
| 2 | modify_item | item-7 | 增加场景原型×路径交叉分析视角，引入场景级满足度判定 | deep-research-agent |
