# Research Outline: Beryl 新增内容的叙事性 High-Level 总结

## Metadata

| Field | Value |
|-------|-------|
| project_slug | `base-beryl-vs-azul` |
| topic_slug | `beryl-narrative-summary` |
| multica_issue_id | `2f090be1-2460-4d8c-bc9e-379cb9a358eb` |
| round | 2 |
| github_repo | `Whisker17/multica-research` |
| outline_path | `base-beryl-vs-azul/outlines/beryl-narrative-summary.md` |
| draft_path | `base-beryl-vs-azul/research-sections/beryl-narrative-summary/drafts/round-1.md` |
| final_path | `base-beryl-vs-azul/research-sections/beryl-narrative-summary/final.md` |

## Topic

Beryl 新增内容的叙事性 High-Level 总结 — 综合三篇已完成的 M1 深度研究（B20 Token System、Precompile Infrastructure、Protocol/Reth/Withdrawal），为高管/战略读者产出一篇跨 scope 整合的叙事性总结，阐明 Azul→Beryl 的升级定位转变、核心能力演进、及对 Mantle 的战略含义。

## Scope

### In-Scope

- **定位叙事**：Azul = 性能/证明系统/EVM(Osaka) 时代 vs Beryl = 协议层合规原生 + 资本效率时代——两代升级的战略定位对比
- **3-5 个高层叙事主题**：跨 scope 整合，不重复 M1 代码级细节，提炼 Beryl 的战略意义
- **Azul→Beryl 能力对比表**：覆盖全部 3 个 scope（B20 Token、Precompile Infra、Protocol/Reth/Withdrawal），以结构化表格呈现能力演进
- **Mantle 战略解读**：Base 在协议层嵌入合规能力与资本效率优化对 Mantle（RWA/机构化战略）的含义

### Out-of-Scope

- M1 研究的代码级细节复述（本研究仅引用结论，不重复代码分析）
- 独立的安全审计或代码审查（已由 M1 各专题覆盖）
- 定量性能基准测试（由下游 WHI-249 覆盖）
- L1 合约代码审计（由 protocol-reth-withdrawal 覆盖）
- Cobalt 功能分析（不在 Beryl 运行时执行）

## Audience

高管/战略读者、项目决策者、Mantle 战略团队。非技术专家但具备区块链行业基础认知。语言风格：简洁、结论导向，避免实现细节，强调"为什么重要"而非"怎么实现"。

## Research Items

### Item 1: 升级定位叙事——从 Azul 到 Beryl 的战略转向

**Slug**: `positioning-narrative`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `azul_era_positioning` | Azul 时代的三大战略支柱总结：(1) 性能——脱离 OP Stack、单客户端架构 (base-reth-node + base-consensus)、Reth V2 执行引擎 (v2.2.0，含 Storage V2 + Proof V2，实现 ~50% 磁盘缩减与 state root pipeline 重写)；(2) 证明系统——Multiproof 架构 (TEE+ZK 双证明、PROOF_THRESHOLD=1)；(3) EVM 对齐——Osaka 7 EIPs spec 对齐。提炼「性能/证明/EVM 三位一体」叙事 | `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md`（引用结论不复述）；`protocol-reth-withdrawal/final.md`（Azul reth v2.2.0 基线确认） |
| `beryl_era_positioning` | Beryl 时代的两大战略支柱总结：(1) 协议层合规原生——B20 precompile 级 token 标准，将合规（blocklist/allowlist/policy）从应用层下沉到协议层；(2) 资本效率——提款窗口 7→5 天缩短，释放桥接 LP 资本。提炼「合规原生 + 资本效率」叙事 | 三篇 M1 final.md 结论综合 |
| `era_transition_logic` | Azul→Beryl 的演进逻辑：Azul 解决了"Base 能否独立运行"的基础设施问题（性能、证明、EVM），Beryl 转向"Base 如何服务机构客户"的产品化问题（合规 token、资本效率）。这是从基础设施层到协议产品层的升维 | 分析综合，基于两代升级的 scope 对比 |
| `continuity_thread` | Beryl 对 Azul 的继承而非替代：Beryl 的 precompile infra 建立在 Azul 引入的 BaseUpgrade fork 体系之上；`beryl()` 返回 `azul()` 确保静态 precompile 集不变；Reth v2.2.0→v2.3.0 是 Azul 已确立的 Reth V2 执行引擎路线的增量性能延续（+8.1% benchmark），而非架构切换 | `beryl-precompile-infra/final.md` §2 BaseUpgrade 分析；`protocol-reth-withdrawal/final.md` Reth v2.2.0→v2.3.0 增量分析 |

**Acceptance Criteria**:
- Azul 和 Beryl 各有 1-2 句话的战略定位陈述，非技术读者可理解
- 演进逻辑清晰：不是并列的功能列表，而是有内在递进的叙事
- 继承关系明确：Beryl 不是推翻 Azul，而是在 Azul 基础上的升维

### Item 2: 高层叙事主题（跨 Scope 整合）

**Slug**: `narrative-themes`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `theme_1_compliance_native` | **主题一：合规 Token 原生化——从应用层到协议层**。B20 将 ERC-20 兼容 token 实现为 Rust precompile，自带 PolicyRegistry（4 维策略：TransferSender/Receiver/Executor + MintReceiver）、ActivationRegistry 门控、7 角色权限模型。这意味着合规不再是 DApp 的可选插件，而是链级的原生能力 | `b20-token-system/final.md` 架构层结论 |
| `theme_2_infra_maturity` | **主题二：Precompile 基础设施成型——可编程协议层的技术底座**。`#[contract]`/`#[precompile]`/`#[derive(Storable)]` 宏系统 + PrecompileStorageProvider（30+ 方法、EIP-2200/2929/3529 gas 语义、checkpoint/commit/revert 原子性）构成了可复用的 stateful precompile 开发框架。B20 是第一个产品化应用，但框架本身支持未来更多 precompile | `beryl-precompile-infra/final.md` 架构层结论 |
| `theme_3_capital_efficiency` | **主题三：资本效率提升——缩短提款窗口 + 执行层增量优化**。提款窗口 7→5 天（SLOW_FINALIZATION_DELAY）释放桥接 LP 资本周转；Reth v2.2.0→v2.3.0 增量升级带来 +8.1% 执行吞吐（1.4→1.5 Ggas/s）、80/80 EL peer defaults、Flashblocks pipeline 优化、BLAKE3 snapshotter。注意：~50% 磁盘缩减属于 Azul 已引入的 Reth 2.0 lineage（Storage V2），不计入 Beryl 增量 | `protocol-reth-withdrawal/final.md` §1 + §2 结论 |
| `theme_4_safety_continuity` | **主题四：安全性与向后兼容——additive + fork-gated 设计哲学**。Beryl 的所有新 precompile 通过 `>= BaseUpgrade::Beryl` gate 安装，对标准 precompile 零影响（blast radius 分析：标准 precompile 零风险、B20 结构编码匹配残余 2^{-87}）。Reth v2.2.0→v2.3.0 增量升级不触及共识机制（Storage V2/Proof V2 架构已在 Azul 稳定运行）。Withdrawal 窗口缩短有 Multiproof 双证明架构作为安全网 | 三篇 M1 final.md 安全/风险分析章节 |
| `theme_cross_cutting` | 跨主题关联分析：合规 token (Theme 1) 依赖 precompile infra (Theme 2) 的存储/gas/原子性框架；资本效率 (Theme 3) 的提款窗口缩短以 Multiproof 安全性 (Theme 4) 为前提。主题之间不是孤立的，而是相互支撑的 | 综合分析 |

**Acceptance Criteria**:
- 4 个主题各有 1 段（80-150 字）的叙事文本，非技术读者可理解
- 每个主题从"对 Base 意味着什么"的视角陈述，而非从"技术实现是什么"的视角
- 跨主题关联显式呈现，展示整体性而非堆砌性
- 不复述 M1 代码级细节（如具体 slot 布局、gas 计算公式、commit SHA 等）

### Item 3: Azul→Beryl 能力对比表

**Slug**: `capability-comparison-table`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `scope_1_token_comparison` | **Scope: Token 标准** — Azul 能力: 无原生 token 标准（依赖 ERC-20 合约部署）→ Beryl 新增: B20 precompile 级 token（Asset/Stablecoin 双变种）、B20Factory 单例部署、PolicyRegistry 策略引擎、ActivationRegistry 门控、7 角色权限模型、ERC-2612 permit/EIP-712 | `b20-token-system/final.md` |
| `scope_2_precompile_comparison` | **Scope: Precompile 基础设施** — Azul 能力: 12 个 BaseUpgrade 分叉（Bedrock→Cobalt）、静态 precompile 集（标准 Ethereum precompile）→ Beryl 新增: 4 个动态 precompile（B20Factory/B20Token/PolicyRegistry/ActivationRegistry）、`#[contract]`/`#[precompile]` 宏系统、PrecompileStorageProvider trait、EIP-2200/2929/3529 完整 gas 语义、BerylLookup 动态地址匹配、11 个 metrics 家族 | `beryl-precompile-infra/final.md` |
| `scope_3_protocol_comparison` | **Scope: 协议/客户端层** — Azul 基线: Reth v2.2.0 执行引擎（已含 Storage V2 + Proof V2，~50% 磁盘缩减属于此基线）、7 天 single-proof 提款窗口、1 天 dual-proof 快路径 → Beryl 增量: Reth v2.3.0 增量执行优化（+8.1% benchmark, 1.4→1.5 Ggas/s）、80/80 EL peer defaults、Flashblocks pipeline 优化（pending-state fast path、metadata 处理）、BLAKE3 snapshotter、提款窗口 7→5 天。**注意**：~50% 磁盘缩减为 Reth 2.0 lineage（Azul 已引入），非 Beryl 新增能力；如在能力表中出现须标注为「inherited Reth 2.0 lineage (background)」 | `protocol-reth-withdrawal/final.md` |
| `table_design` | 表格设计：按维度（Token 能力 / Precompile 基础设施 / 执行层性能 / 提款效率 / 安全模型）分行，Azul 列 vs Beryl 列 vs 变化摘要列。约 8-12 行 | 综合设计 |

**Acceptance Criteria**:
- 表格覆盖全部 3 个 scope，每个 scope 至少 2 行细分维度
- Azul 列展示的是 Beryl 之前的已有能力（或"无"），Beryl 列展示新增/变更
- 变化摘要列用一句话说明每行的战略意义
- 非技术术语优先；必要技术术语附简短解释（如"precompile = 协议级内置模块"）
- 表格可独立阅读，不依赖正文上下文

### Item 4: Mantle 战略解读

**Slug**: `mantle-strategic-interpretation`

**Investigation Fields**:

| Field | Description | Source Requirement |
|-------|-------------|-------------------|
| `rwa_implication` | **RWA 含义**：Base 通过 B20 在协议层嵌入合规 token 标准，意味着 RWA（真实世界资产）token 化可以在 L2 层原生实现，而非依赖应用层合约。对 Mantle 的启示：如果 Mantle 追求 RWA/机构化，是否需要类似的协议层合规能力？还是可以通过应用层实现？两种路径的权衡 | `b20-token-system/final.md` 合规架构结论；Mantle 公开战略信息 |
| `institutional_readiness` | **机构就绪度**：B20 的 PolicyRegistry（blocklist/allowlist）+ 7 角色权限模型 + 供应上限 + 暂停功能，构成了一个面向受监管机构的 token 发行框架。这代表 Base 从"开发者友好的通用 L2"向"机构合规的专用 L2"的定位扩展。Mantle 是否面临类似的定位选择？ | `b20-token-system/final.md`；行业趋势分析 |
| `precompile_framework_value` | **框架可复用性**：Beryl 的 precompile 基础设施不只是 B20 的载体——它是一个可复用的 stateful precompile 开发框架。如果 Mantle 未来需要定制协议层功能（如原生 DID、KYC、或链上身份），Beryl 的框架设计提供了参考路径。评估 Mantle 的 OP Stack 兼容架构是否具备类似扩展性 | `beryl-precompile-infra/final.md` 框架分析；Mantle 架构公开信息 |
| `capital_efficiency_benchmark` | **资本效率对标**：Beryl 将提款窗口从 7 天缩短到 5 天。Mantle 当前的提款窗口是多少？如何对标？Base 宣称"窗口将继续缩短"——这对 Mantle 的 fast-bridge 和流动性策略有何竞争含义？ | `protocol-reth-withdrawal/final.md`；L2Beat Base vs Mantle 对比数据 |
| `strategic_summary` | **战略要点总结**：提炼 2-3 个对 Mantle 最重要的 takeaway，以 actionable insight 形式呈现（如"Base 已在协议层嵌入合规能力，Mantle 需在 [时间框架] 内评估是否需要等价能力"） | 上述所有字段的综合 |

**Acceptance Criteria**:
- 战略解读不是技术对比，而是从竞争定位和战略决策视角分析
- 每个含义附有 Mantle 的 actionable takeaway
- 不做价值判断（如"Mantle 必须跟进"），而是呈现选择和权衡
- RWA/机构化含义有行业趋势支撑
- 资本效率对标有可引用的数据点

## Source Requirements

### Primary Sources（引用结论不复述内容）

| Source | Type | Relation |
|--------|------|----------|
| `base-beryl-vs-azul/research-sections/b20-token-system/final.md` | M1 Research | B20 合规 token 标准体系——架构、合规模型、角色权限 |
| `base-beryl-vs-azul/research-sections/beryl-precompile-infra/final.md` | M1 Research | Precompile 基础设施——宏系统、存储 provider、gas 语义、fork-gated 安装 |
| `base-beryl-vs-azul/research-sections/protocol-reth-withdrawal/final.md` | M1 Research | 协议/客户端层——Reth V2、提款窗口、版本矩阵、风险面 |
| `base-beryl-vs-azul/research-sections/beryl-scope-inventory/final.md` | M1 Research | Beryl scope 总览——143 commit、15 域 taxonomy、三大官方 scope |

### Secondary Sources（引用结论不复述内容）

| Source | Type | Relation |
|--------|------|----------|
| `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` | Research | Azul 基线——OP Stack 脱离、Multiproof、Osaka EVM、Flashblocks |
| `base-azul-upgrade/research-sections/mantle-impact-assessment/final.md` | Research | Mantle 影响评估——Azul 对 Mantle 的影响、6/13 功能已有、46.2% 覆盖 |
| L2Beat Base & Mantle 风险评估 | Web | 提款窗口对标、Stage 合规对比 |
| 行业公开信息：Base & Mantle 战略声明 | Web | 定位分析的行业背景 |

### Source Integrity Rules

1. 本研究为综合叙事，**仅引用 M1 结论**，不复述代码级细节（如 slot 布局、gas 公式、commit SHA）
2. 引用 M1 内容时标注来源路径（如"参见 b20-token-system/final.md §3"）
3. 能力对比表中的 Azul baseline 数据须与 Azul 研究交叉验证
4. Mantle 战略解读中的竞争对标须基于公开可验证信息，不做内部推测
5. 定性结论（如"这代表定位转变"）须有 M1 研究证据支撑

## Diagram Expectations

### Diagram 1: Azul→Beryl 升级定位演进

**Type**: 双列对比图 (Two-era comparison)
**Content**: 左列 Azul 时代（性能 / 证明 / EVM）→ 右列 Beryl 时代（合规原生 / 资本效率 / 基础设施延续）；中间用箭头标注继承关系（如 Azul 单客户端 → Beryl Reth V2 升级）
**Format**: Mermaid flowchart
**Purpose**: 直观展示两代升级的战略定位差异与继承

### Diagram 2: Beryl 四大叙事主题关系图

**Type**: 主题关系图 (Theme relationship diagram)
**Content**: 4 个叙事主题的相互关系——合规 token 依赖 precompile infra、资本效率依赖安全模型、各主题共同支撑"协议层合规原生 + 资本效率"的总定位
**Format**: Mermaid flowchart
**Purpose**: 展示主题之间的逻辑关联而非孤立列举

**Note**: 能力对比表已以结构化 Markdown 表格呈现，不需要额外图表。不需要 timeline 图。

## Expected Output Summary

Draft (`round-1.md`) 应为一篇 800-1200 字的中文叙事性总结，包含：

1. **§1 升级定位叙事** (~200 字) — Azul = 性能/证明/EVM 时代 → Beryl = 合规原生 + 资本效率时代。演进逻辑而非功能堆砌。含 Mermaid 演进图
2. **§2 四大叙事主题** (~300-400 字) — 合规 token 原生化 / Precompile 基础设施成型 / 资本效率提升 / 安全性与兼容性。每个主题从"对 Base 意味着什么"的视角展开，跨主题关联显式呈现。含 Mermaid 关系图
3. **§3 Azul→Beryl 能力对比表** (~200 字 + 表格) — 结构化表格覆盖全部 3 个 scope，约 8-12 行，Azul vs Beryl vs 战略意义三列
4. **§4 Mantle 战略解读** (~200-300 字) — RWA 含义、机构就绪度、框架可复用性、资本效率对标、2-3 个 actionable takeaway

全文语言风格：高管/战略读者友好，避免代码级细节（不出现 commit SHA、slot 布局、gas 公式），技术术语附简短解释。

## Cross-References

| Reference | Path / ID | Relation |
|-----------|-----------|----------|
| B20 Token System | `base-beryl-vs-azul/research-sections/b20-token-system/final.md` | M1 输入：合规 token 标准体系 |
| Precompile Infra | `base-beryl-vs-azul/research-sections/beryl-precompile-infra/final.md` | M1 输入：precompile 基础设施 |
| Protocol/Reth/Withdrawal | `base-beryl-vs-azul/research-sections/protocol-reth-withdrawal/final.md` | M1 输入：协议/客户端层变更 |
| Scope Inventory | `base-beryl-vs-azul/research-sections/beryl-scope-inventory/final.md` | M1 输入：scope 总览 |
| Azul Overview | `base-azul-upgrade/research-sections/base-strategy-azul-overview/final.md` | Azul 基线 |
| Mantle Impact Assessment | `base-azul-upgrade/research-sections/mantle-impact-assessment/final.md` | Mantle 影响评估基线 |

## Quality Checklist (for Adversarial Review)

- [ ] 升级定位叙事有清晰的"Azul 时代 vs Beryl 时代"对比，而非功能列表
- [ ] 演进逻辑（基础设施层→协议产品层升维）有 M1 证据支撑
- [ ] 4 个叙事主题从"战略意义"而非"技术实现"视角陈述
- [ ] 叙事主题之间的跨主题关联显式呈现
- [ ] 能力对比表覆盖全部 3 个 scope（Token / Precompile / Protocol），每个 scope ≥ 2 行细分
- [ ] 能力对比表 Azul 列与 Azul 研究交叉验证（特别是 Azul 基线已含 Reth v2.2.0 + Storage V2 + Proof V2）
- [ ] ~50% 磁盘缩减如被提及，须标注为「inherited Reth 2.0 lineage (background)」而非 Beryl 新增
- [ ] 协议/客户端层 Beryl 增量准确限定为 v2.2.0→v2.3.0（+8.1%、80/80 peers、Flashblocks 优化、BLAKE3、7→5 天提款窗口）
- [ ] Mantle 战略解读包含 RWA 含义和 actionable takeaway
- [ ] 战略解读呈现选择和权衡，而非单向价值判断
- [ ] 全文 800-1200 字（不含表格和图），语言面向非技术读者
- [ ] 不出现代码级细节（commit SHA、slot 布局、gas 公式、具体 line number）
- [ ] 技术术语附简短解释
- [ ] 引用 M1 内容标注来源路径，不复述
- [ ] Mermaid 图可渲染且传达战略定位信息
- [ ] 资本效率对标有可引用数据点
