---
topic: "Mantle 合规 Token 策略建议"
project_slug: "compliance-token-standards"
topic_slug: "mantle-compliance-token-strategy"
scope: |
  基于前序调研（合规 Token 全景、ERC-3643 深度、TIP-20 深度、四标准横评），
  为 Mantle（OP Stack L2 / RWA 机构化定位）输出针对性合规 token 策略建议。
  覆盖三条路线（Smart-contract/ERC-3643、Precompile 自建原生标准、混合路线）
  的技术分析、关键决策因素、竞争态势评估以及分阶段实施建议。
audience: "Mantle 核心开发与战略团队、RWA/机构业务负责人、合规架构师"
expected_output: |
  compliance-token-standards/outlines/mantle-compliance-token-strategy.md —
  包含 4 个分析模块：
  (1) Mantle 现状评估与技术栈约束，
  (2) 三条路线技术分析（优劣对比、适用场景），
  (3) 关键决策因素与竞争态势分析（含 B20 证据边界说明），
  (4) 分阶段实施建议（短期/中期/长期可行动路径）。
artifact_paths:
  - "compliance-token-standards/research-sections/mantle-compliance-token-strategy/drafts/round-1.md"
  - "compliance-token-standards/research-sections/mantle-compliance-token-strategy/final.md"
dependencies:
  - topic_slug: "compliance-token-landscape"
    relationship: "前置：提供合规 token 行业全景、监管环境、能力分类学与评估框架"
  - topic_slug: "erc3643-trex-analysis"
    relationship: "前置：提供 ERC-3643 深度技术分析（合约架构、身份层、Gas 开销、采用案例）"
  - topic_slug: "tempo-tip20-analysis"
    relationship: "前置：提供 TIP-20 协议层合规深度分析（precompile 套件、Policy Registry、Payment Lanes、RBAC）"
  - topic_slug: "compliance-token-comparison"
    relationship: "核心前置：提供四标准横评（9 维技术矩阵、6 维成熟度、8 类合规能力覆盖、交叉洞察）"
source_requirements:
  primary:
    - "前序调研 final.md（compliance-token-landscape、erc3643-trex-analysis、tempo-tip20-analysis、compliance-token-comparison）"
    - "Mantle 技术文档与代码仓库（/Users/whisker/Work/src/networks/mantle/）"
    - "OP Stack 规范（op-node、op-geth、derivation pipeline）"
  secondary:
    - "ERC-3643 官方规范（EIP-3643 Final）与 T-REX 开源实现"
    - "Mantle 公开路线图与治理提案"
    - "mETH/cmETH 协议文档"
  evidence_boundary:
    - "B20 主线能力评估仅使用 base/base@8e8767281d7c8768f6a0aed9124779cd4ed030ae 可验证证据"
    - "B20Security/IB20Security、redeem、batchBurn、securityIdentifier 仅作为本地分支演进线索，不纳入硬证据"
diagram_expectations:
  - id: "diag-1"
    title: "三条路线架构对比图"
    type: "architecture-comparison"
    description: "并排展示 Option A/B/C 的合规层位置（应用层 vs 协议层 vs 混合），标注关键组件交互"
  - id: "diag-2"
    title: "Mantle 合规 Token 决策树"
    type: "decision-tree"
    description: "基于关键决策因素（发行方需求、hardfork 节奏、mETH/cmETH 协同、竞争态势），引导三条路线选择"
  - id: "diag-3"
    title: "分阶段实施时间线"
    type: "timeline"
    description: "短期 0-3 月 → 中期 3-6 月 → 长期 6-12 月，标注里程碑、决策点与依赖"
---

# Mantle 合规 Token 策略建议 — 研究大纲

## Research Questions

1. Mantle 当前技术栈（OP Stack + reth sequencer + Arsia/Hoodi hardfork）对合规 token 实现有哪些具体约束与机遇？
2. 三条路线（ERC-3643 应用层、Precompile 原生标准、混合路线）在 Mantle 上的技术可行性、实现成本与差异化价值如何对比？
3. mETH/cmETH 等 LST 资产能否与合规 token 框架协同，产生机构化增量价值？
4. 竞争格局中 Base B20（pinned commit 证据边界内）和 Tempo TIP-20 的策略信号对 Mantle 路线选择有何启示？
5. 在 Mantle 的 hardfork 节奏与治理流程约束下，分阶段实施的最优节奏与最小可行动作是什么？

## B20 Evidence Constraint

> **硬规则**：B20 主线能力评估仅使用 `base/base@8e8767281d7c8768f6a0aed9124779cd4ed030ae` 中可验证的证据。
> `B20Security`/`IB20Security`、`redeem`、`batchBurn`、`securityIdentifier` 等接口仅作为"本地分支演进线索"引用，
> 标注为 `[本地分支演进线索]`，不纳入 B20 当前主线能力评估或 Mantle 策略判断的硬证据。
> 竞争态势分析中涉及 B20 的部分须明确标注证据来源与可信度等级。

---

## Items

### item-1: Mantle 技术栈现状评估

- **priority**: P0
- **module**: 模块一 — Mantle 现状评估与技术栈约束
- **dependencies**: compliance-token-landscape (行业全景), compliance-token-comparison (横评框架)
- **description**: 评估 Mantle 当前技术栈对合规 token 实现的约束与能力基线。
- **sub-items**:
  1. OP Stack 架构约束分析：L1-L2 消息传递、跨链桥合约、derivation pipeline 对合规逻辑的影响
  2. reth sequencer（Arsia/Hoodi）技术特性：custom precompile 可行性、EVM 兼容性边界、hardfork 机制
  3. 当前 ERC-20 生态：标准 ERC-20 无原生合规层的现状与局限
  4. Gas 成本基线：Mantle L2 Gas 模型特征，与 ERC-3643 额外 Gas 开销的兼容性评估

### item-2: Mantle 市场定位与合规需求映射

- **priority**: P0
- **module**: 模块一 — Mantle 现状评估与技术栈约束
- **dependencies**: compliance-token-landscape (监管环境与能力分类学)
- **description**: 将 Mantle 的 RWA/机构化定位映射到具体合规能力需求。
- **sub-items**:
  1. RWA 机构化定位分析：Mantle 目标发行方画像（机构投资者、资产管理公司、合规金融机构）
  2. mETH/cmETH 协同分析：LST 资产与合规 token 框架的集成可能性（身份层复用、合规状态继承）
  3. 监管需求映射：基于前序全景调研的 8 类合规能力分类，识别 Mantle 目标场景的优先能力子集
  4. 竞争差异化定位：Mantle 合规 token 能力如何服务于其机构化 L2 战略差异化

### item-3: 选项 A — ERC-3643 智能合约路线技术分析

- **priority**: P0
- **module**: 模块二 — 三条路线技术分析
- **dependencies**: erc3643-trex-analysis (深度技术分析), compliance-token-comparison (横评)
- **description**: 在 Mantle 上部署 ERC-3643 的完整技术分析。
- **sub-items**:
  1. 部署可行性：ERC-3643 六核心合约 + ONCHAINID 在 Mantle EVM 上的兼容性验证
  2. 实现成本评估：合约部署 Gas、ONCHAINID 身份基础设施搭建、ClaimIssuer 生态对接
  3. 优势分析：成熟标准（$32B+ tokenized）、无协议层改动、已有工具链与审计资源、ERC Final 状态
  4. 劣势分析：Gas 开销 2-8x ERC-20、transfer 路径身份验证延迟、无法利用 Mantle 协议层差异化
  5. 适用场景：合规需求明确但不追求协议层差异化的机构发行场景

### item-4: 选项 B — Precompile 自建原生标准路线技术分析

- **priority**: P0
- **module**: 模块二 — 三条路线技术分析
- **dependencies**: tempo-tip20-analysis (TIP-20 precompile 范例), compliance-token-comparison (横评)
- **description**: Mantle 自建 precompile 原生合规标准的技术分析，以 TIP-20 为参考范例。
- **sub-items**:
  1. Precompile 设计空间：参考 TIP-20 precompile 套件（TIP-403 Policy Registry、4 角色 RBAC），评估 Mantle reth sequencer 上的实现路径
  2. 实现成本评估：precompile 开发、硬分叉协调、测试网验证、EVM 兼容性维护
  3. 优势分析：Gas 效率（原生执行 vs Solidity）、协议层差异化、深度集成 Mantle 特有功能
  4. 劣势分析：开发周期长（TIP-20 经验：从设计到生产 12+ 月）、标准化风险（非 ERC Final）、生态工具缺失、hardfork 依赖
  5. TIP-20 经验教训提取：Payment Lanes 分配、Fee AMM、Channel Reserve 等高级特性的适用性与移植可能
  6. 适用场景：追求协议层差异化且有能力承担长期开发投入的战略场景

### item-5: 选项 C — 混合路线技术分析

- **priority**: P0
- **module**: 模块二 — 三条路线技术分析
- **dependencies**: item-3, item-4, compliance-token-comparison (交叉洞察)
- **description**: PolicyRegistry precompile + ERC-20/ERC-3643 adapter 混合路线的技术分析。
- **sub-items**:
  1. 混合架构设计：PolicyRegistry precompile 提供原生合规判定 + 应用层 ERC-20/ERC-3643 token 调用 precompile 进行合规检查
  2. 接口设计要点：precompile ↔ Solidity adapter 的调用约定、Gas 分摊、状态一致性
  3. 实现成本评估：仅 PolicyRegistry precompile 的开发量（vs 完整 precompile 标准），adapter 合约复杂度
  4. 优势分析：兼具协议层 Gas 效率（热路径合规判定）与应用层灵活性（ERC-3643 标准兼容）
  5. 劣势分析：架构复杂性、两层状态同步、升级协调难度、非标准化路径的生态接受度
  6. 与前序交叉洞察的关联：横评 Insight B（ERC-3643 vs B20/TIP-20 互补路径，可信度 1/5 "投机性"）的验证与深化
  7. 适用场景：希望渐进式引入协议层能力同时保持应用层标准兼容的过渡场景

### item-6: 关键决策因素分析

- **priority**: P0
- **module**: 模块三 — 关键决策因素与竞争态势分析
- **dependencies**: item-1, item-2, item-3, item-4, item-5
- **description**: 系统化分析影响 Mantle 路线选择的关键决策因素。
- **sub-items**:
  1. 发行方合规能力需求评估：目标发行方的合规成熟度、身份基础设施现状、对标准化 vs 定制化的偏好
  2. Hardfork 节奏约束：Mantle hardfork 周期（Arsia → Hoodi → 下一次）、治理流程时间成本、precompile 引入的最早可行窗口
  3. mETH/cmETH 协同决策点：LST 合规包装的技术可行性、是否需要协议层支持、用户体验影响
  4. 开发资源与优先级权衡：合规 token 开发与 Mantle 其他技术优先级（性能优化、DA 层、跨链桥）的资源竞争
  5. 标准化与生态接受度：ERC Final（ERC-3643）vs 自建标准的生态信任度、工具链支持、审计资源可用性
  6. 决策矩阵构建：多因素加权评估框架，输出三条路线的综合评分

### item-7: 竞争态势与 B20 证据边界分析

- **priority**: P0
- **module**: 模块三 — 关键决策因素与竞争态势分析
- **dependencies**: compliance-token-comparison (竞争格局洞察), item-6
- **description**: 分析竞争链的合规 token 策略信号，严格遵守 B20 证据边界。
- **sub-items**:
  1. Base B20 主线证据分析（pinned commit `base/base@8e87672`）：已验证的 precompile 设计、Beryl hardfork 定位、合规能力边界
  2. B20 本地分支演进线索 `[本地分支演进线索]`：B20Security/IB20Security、redeem、batchBurn、securityIdentifier 的方向性信号（明确标注不作为硬证据）
  3. Tempo TIP-20 竞争信号：已生产环境验证的协议层合规方案、Payment Lanes/Fee AMM 的商业模式创新、对 Mantle 的启示
  4. 竞争格局综合评估：各链合规 token 成熟度对比（横评 6 维成熟度框架复用）、Mantle 的差异化窗口
  5. 时间窗口分析：B20 pre-hardfork 状态 vs TIP-20 已生产 vs ERC-3643 市场主导 — Mantle 的最优介入时机

### item-8: 分阶段实施建议

- **priority**: P0
- **module**: 模块四 — 分阶段实施建议
- **dependencies**: item-6, item-7
- **description**: 基于前述分析输出分阶段可行动建议。
- **sub-items**:
  1. 短期 0-3 月（需求验证 + ERC-3643 可行性）：
     - 目标发行方需求调研与合规能力需求确认
     - ERC-3643 在 Mantle testnet 的 PoC 部署与 Gas 基准测试
     - ONCHAINID 身份基础设施评估与 ClaimIssuer 对接方案
     - 最小可行产品（MVP）范围定义
  2. 中期 3-6 月（混合路线评估）：
     - PolicyRegistry precompile 原型设计与内部评审
     - ERC-3643 ↔ precompile adapter PoC 开发
     - Hardfork 窗口与治理流程评估
     - mETH/cmETH 合规包装可行性验证
  3. 长期 6-12 月（全面原生标准决策）：
     - 基于短期/中期数据的路线最终决策
     - 完整协议层合规标准设计（如选择 Option B/C）
     - 生态合作伙伴对接与标准化推进
     - 主网部署路线图与里程碑定义

### item-9: 最小可行动建议与风险缓释

- **priority**: P1
- **module**: 模块四 — 分阶段实施建议
- **dependencies**: item-8
- **description**: 提炼可立即执行的最小可行动集合与关键风险缓释措施。
- **sub-items**:
  1. 即时可行动清单：无需等待路线决策即可启动的基础工作（身份基础设施调研、Gas 基准测试、发行方需求访谈）
  2. 路线锁定前的期权策略：如何在路线未锁定时最大化选择权（ERC-3643 PoC 同时评估 precompile 可行性）
  3. 关键风险识别与缓释：hardfork 延迟风险、标准化失败风险、竞争窗口关闭风险、mETH/cmETH 协同失败风险
  4. 决策门控机制：定义各阶段的 go/no-go 标准与决策升级路径

---

## Fields

| Field | Source | Notes |
|-------|--------|-------|
| Mantle OP Stack 架构版本 | Mantle 本地代码仓库、公开文档 | op-node / op-geth / reth sequencer 版本与配置 |
| Hardfork 历史与规划 | Mantle 治理提案、公开路线图 | Arsia → Hoodi → 后续 |
| reth sequencer precompile 能力 | Mantle 本地代码仓库 | custom precompile 注册机制、EVM 兼容性 |
| Mantle L2 Gas 模型 | Mantle 文档、链上数据 | L2 execution gas + L1 data gas 分摊模型 |
| ERC-3643 合约 Gas 基准 | erc3643-trex-analysis final.md | transfer 2-8x ERC-20 的具体数值与场景 |
| TIP-20 precompile Gas 基准 | tempo-tip20-analysis final.md | precompile vs Solidity 执行的 Gas 对比 |
| B20 pinned commit 可验证证据 | base/base@8e87672 | 严格限定为该 commit 可验证内容 |
| B20 本地分支演进线索 | 横评 final.md 引用 | 标注为线索，不作为硬证据 |
| 四标准成熟度评分 | compliance-token-comparison final.md | ERC-3643: 28/30, TIP-20: 19/30, ERC-1400: 11/30, B20: 10/30 |
| 合规能力覆盖矩阵 | compliance-token-comparison final.md | 8 类合规能力 × 4 标准覆盖情况 |
| 交叉洞察可信度 | compliance-token-comparison final.md | 协议层合规趋势 2/5, 互补路径 1/5 |
| mETH/cmETH 协议规范 | Mantle 文档、合约代码 | LST 资产合规包装可行性依据 |
| 发行方合规需求 | 行业访谈、监管框架 | EU DLT Pilot, US DTC no-action, GENIUS Act, HK stablecoin |

## Diagram Expectations

| ID | Title | Type | Description |
|----|-------|------|-------------|
| diag-1 | 三条路线架构对比图 | architecture-comparison | 并排展示 Option A（纯应用层 ERC-3643）、Option B（纯协议层 precompile）、Option C（混合：PolicyRegistry precompile + adapter）的合规层位置，标注 Mantle 技术栈各层级（L1 ↔ Bridge ↔ Sequencer ↔ EVM ↔ Application）中的组件交互 |
| diag-2 | Mantle 合规 Token 决策树 | decision-tree | 以关键决策因素（发行方需求紧迫度、hardfork 窗口可用性、mETH/cmETH 协同需求、差异化战略优先级）为分支节点，引导至三条路线的推荐选择 |
| diag-3 | 分阶段实施时间线 | timeline | 横轴 0-12 月，纵轴三条路线的并行/串行工作流，标注关键里程碑（PoC 完成、决策门控、hardfork 窗口、主网部署）与路线切换决策点 |

## Source Requirements

| Category | Sources | Usage |
|----------|---------|-------|
| 前序调研（核心依赖） | compliance-token-landscape/final.md, erc3643-trex-analysis/final.md, tempo-tip20-analysis/final.md, compliance-token-comparison/final.md | 全部 item 的基础数据与分析框架 |
| Mantle 技术栈 | /Users/whisker/Work/src/networks/mantle/ 本地代码仓库, Mantle 公开技术文档 | item-1, item-4, item-5, item-6 |
| OP Stack 规范 | /Users/whisker/Work/src/networks/optimism/ 本地代码仓库 | item-1 (架构约束分析) |
| ERC-3643 规范 | EIP-3643 Final 规范, T-REX 开源实现 (tokeny-solutions/T-REX) | item-3 |
| B20 证据 (pinned) | base/base@8e8767281d7c8768f6a0aed9124779cd4ed030ae | item-7 (竞争态势, 严格证据边界) |
| mETH/cmETH | Mantle LST 协议文档与合约代码 | item-2, item-6, item-8 |
| 监管框架 | EU DLT Pilot Regime, US GENIUS Act, HK stablecoin licensing, DTC no-action letters | item-2, item-6 |

---

## Patch Log

| Round | Date | Summary |
|-------|------|---------|
| R1 | 2026-06-04 | Initial outline: 4 modules, 9 items, 3 diagrams, B20 evidence boundary enforced |
