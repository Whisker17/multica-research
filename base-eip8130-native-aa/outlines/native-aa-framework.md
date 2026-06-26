---
topic: "建立 native AA 研究框架、对比 rubric 与证据复用地图"
project_slug: "base-eip8130-native-aa"
topic_slug: "native-aa-framework"
github_repo: "Whisker17/multica-research"
round: 2
status: candidate

artifact_paths:
  outline: "base-eip8130-native-aa/outlines/native-aa-framework.md"
  draft: "base-eip8130-native-aa/research-sections/native-aa-framework/drafts/round-{n}.md"
  final: "base-eip8130-native-aa/research-sections/native-aa-framework/final.md"
  index: "base-eip8130-native-aa/research-sections/_index.md"

scope: "四步骤：(1) 三层 taxonomy 归位表（4337/7702/8130/7560/7701/3074），明确各方案归位与「native AA」边界；(2) 统一 rubric D1~D13（抽象层级/协议改动/基础设施依赖/所有权密钥模型/Gas 代付/批量原子性/nonce 防重放/EOA 兼容/签名灵活性/成熟度生态/安全攻击面/Mantle 适配成本/目标用户·产品场景适配），含判定标准与可填值；(3) 「效果好/不好」四类可观测代理指标（链上采用度/开发者体验/基础设施成本/钱包生态）与取证方式；(4) 证据复用地图（源码路径/PR/WHI/URL），标注复用范围"
audience: "Mantle dev teams、区块链协议工程师、产品决策者，以及 Research Review Agent。读者熟悉 EVM/L2 架构和 AA 基础概念，但需要一份从「原理区别与优势」角度系统对比各 AA 方案的技术分析框架，最终回答 Mantle 是否需要实现类似 native AA 方案。"
expected_output: "base-eip8130-native-aa/outlines/native-aa-framework.md — 三层 taxonomy 归位表 + rubric D1~D13 表（含 D13 目标用户/产品场景 use case 清单）+ 效果判定口径 + 证据复用地图；覆盖 4337/7702/8130/7560/7701/3074；供后续 WHI-276~282 共用口径"

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-06-26T10:40:00Z"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-06-26T11:00:00Z"

multica_issue_id: "8e4aa1e2-2554-48e2-847f-54f9f27a4084"
branch_name: "research/base-eip8130-native-aa/native-aa-framework"
base_commit: "f40eba7e3ed3d7f7c3f077e2aac2c0c45fb8c2a4"
language: "中文"
research_depth: "standard"
---

# Research Outline: 建立 native AA 研究框架、对比 rubric 与证据复用地图

## Research Questions

1. 「native AA」的严格定义边界是什么？应用层 AA（ERC-4337）、EOA 增强（EIP-7702）、协议原生 AA（EIP-8130/RIP-7560/EIP-8141）、以及历史方案（EIP-3074/EIP-7701/EIP-5003）各自归属哪一层？三层 taxonomy 能否无遗漏容纳当前所有主流 AA 方案？
2. 对比各 AA 方案的「原理区别与优势」应使用哪些统一维度？D1~D13 rubric 每维度的判定标准与可填值如何定义，才能确保跨方案对比的客观性和可独立判定性？
3. Mantle 已支持 ERC-4337 和 EIP-7702 但「效果不好」——如何将这一主观判断转化为可观测、可取证的客观指标？链上采用度、开发者体验、基础设施成本、钱包生态四类代理指标的具体度量方式和数据源是什么？
4. Base 为什么没有选择 RIP-7560 或 EIP-8141 而是选择了 EIP-8130？EIP-8130 与 EIP-8141 作为当前两个竞争的 Draft native AA 方案，在验证模型（约束验证 vs 完全可编程验证）、mempool 影响、后量子准备度、实现复杂度上的核心设计哲学差异是什么？
5. 现有证据源（Base 源码、PR、Daily Intelligence WHI、EIP 草案、Mantle op-geth）如何高效复用于后续 WHI-276~282 的各深度调研 issue？哪些证据可直接引用，哪些需重新取证？

## Taxonomy Boundary Guardrails

> **T1 — 「native AA」边界定义**：
> 「native AA」严格指需要共识层/协议层修改才能实现的 AA 方案。判定标准：(a) 引入新的 EIP-2718 交易类型，(b) 修改 EVM 执行栈或共识验证逻辑，(c) 验证/执行逻辑由协议而非应用层合约强制执行。ERC-4337 不满足上述任一条件，归属应用层；EIP-7702 满足 (a)(b) 但仅增强 EOA 而非实现完整 AA，归属 EOA 增强层；EIP-8130/RIP-7560/EIP-8141 满足全部条件，归属协议原生层。EIP-7701（已 Withdrawn，被 EIP-8141 取代）和 EIP-3074（已 Withdrawn，被 7702 取代）归属历史方案。
>
> **T2 — 方案状态标注要求**：
> 所有涉及 AA 方案的结论必须标注方案当前状态（Final ERC / Deployed / Draft EIP / Stagnant / Withdrawn / RIP），并标注访问日期。EIP-8130 相关结论须标注 "Draft, Base 实现中"；EIP-8141 须标注 "Draft, CFI for Hegotá"；RIP-7560 须标注 "RIP Draft, rollup-targeted"；EIP-7701 须标注 "Withdrawn, superseded by EIP-8141"；EIP-5003 须标注 "Withdrawn"；EIP-3074 须标注 "Withdrawn, superseded by EIP-7702"。
>
> **T3 — Mantle 现状准确描述**：
> 描述 Mantle AA 现状时：Mantle 已通过 op-geth 支持 EIP-7702（Pectra 兼容）、通过 ERC-4337 基础设施支持智能账户，但「效果不好」是项目方主观判断，须用效果判定口径（item-3）的客观指标重新评估，不可作为预设结论直接引用。

## Items

### item-1: 三层 taxonomy 与「native AA」严格定义

确立 AA 方案的三层分类体系，为后续所有对比提供统一归位框架。

**Layer 1 — 应用层 / 链下 AA**：不需要协议层修改，完全在应用层通过智能合约和链下基础设施实现。代表方案：ERC-4337（EntryPoint 合约 + UserOperation + Bundler + Paymaster）。特征：无需硬分叉、跨链可移植、需独立 mempool 和 bundler 基础设施、Gas 开销较高（额外 ~20,000 gas/tx）、与原生 tx 隔离。

**Layer 2 — EOA 增强**：通过协议层修改增强现有 EOA 能力，但不实现完整的账户抽象（EOA 仍保留原始属性，delegation 可逆）。代表方案：EIP-7702（Pectra 硬分叉，2025-05-07 上线）。特征：引入新交易类型、EOA 可临时代理智能合约代码、保留原地址、与 4337 互补而非替代。历史方案：EIP-3074（AUTH/AUTHCALL 操作码，已 Withdrawn，被 7702 取代）。

**Layer 3 — 协议原生 native AA**：通过协议层/共识层修改实现完整账户抽象，使智能账户成为协议一等公民。三个竞争方案：
- **EIP-8130**（Account Abstraction by Account Configuration）：Chris Hunter (Coinbase/Base) 提出，Draft 状态。核心思路——验证通过 authenticator 合约（IAuthenticator 接口）以 STATICCALL 执行，无状态修改、有界 gas；协议定义 canonical authenticator set（节点必须接受的签名算法集），节点可按 authenticator 身份过滤交易而无需模拟任意 EVM 代码。链 MAY 将 canonical authenticator 的执行固化为固定 gas 成本，或按普通 EVM 计量。非 canonical authenticator 可无许可部署但仅在 EVM 执行上下文中使用（不可直接走 8130 交易路径）。执行阶段完全可编程。Base 正在实现。
- **RIP-7560**（Native Account Abstraction for Rollups）：Vitalik Buterin 等提出，RIP Draft 状态。ERC-4337 的协议层 enshrinement，引入 AA_TX_TYPE，验证完全可编程（任意合约逻辑），针对 rollup 环境优化，Gas 比 4337 降低 ~38%。
- **EIP-8141**（Frame Transaction）：Vitalik Buterin 等提出，Draft 状态，2026-03 ACD 会议获得 CFI（Considered for Inclusion）for Hegotá fork。引入 frame transaction（type 0x06），将交易拆分为 VERIFY frame（验证/授权）和 EXECUTE frame（执行），验证完全可编程（任意 EVM 逻辑），支持 default code（EOA 无需部署合约即可使用），原生支持后量子签名方案。EIP-8130 的最直接竞争者——两者核心分歧在验证阶段：8130 约束为 STATICCALL 到声明的 authenticator，8141 允许完全可编程的 EVM 验证。

**历史方案**（已退出或被取代）：
- **EIP-3074**（AUTH/AUTHCALL）：Withdrawn，被 EIP-7702 取代。引入新操作码导致 EVM 技术债务，安全风险（invoker 合约攻击面），与 4337 roadmap 不一致。
- **EIP-7701**（Native Account Abstraction via EOF）：Withdrawn，被 EIP-8141 取代。依赖 EOF（EIP-3540）导致与现有 Solidity 合约不兼容，验证完全可编程但 EOF 前提未能通过治理流程。其核心原则（验证/执行分离、新交易类型、智能账户协议一等公民）被 EIP-8141 继承和发展。
- **EIP-5003**（Insert Code into EOAs with AUTHUSURP）：Withdrawn，提议将 EOA 永久转换为合约账户，与 7702 的可逆 delegation 形成对比。

**归位表**（deep draft 须验证并填充具体证据）：

| 方案 | 层级归属 | 需要协议修改 | 新交易类型 | 完整 AA | 状态 |
|------|---------|------------|-----------|--------|------|
| ERC-4337 | L1 应用层 | 否 | 否（UserOp） | 是（via EntryPoint） | Final ERC (2023) |
| EIP-7702 | L2 EOA 增强 | 是（Pectra HF） | 是 | 否（EOA 增强） | Final, Deployed (2025-05) |
| EIP-8130 | L3 协议原生 | 是 | 是 | 是 | Draft |
| RIP-7560 | L3 协议原生 | 是 | 是（AA_TX_TYPE） | 是 | RIP Draft |
| EIP-8141 | L3 协议原生 | 是 | 是（type 0x06 frame tx） | 是 | Draft, CFI for Hegotá |
| EIP-3074 | 历史（L2 类） | 是（新操作码） | 否 | 否 | Withdrawn |
| EIP-7701 | 历史（L3 类） | 是（需 EOF） | 是（AA_TX_TYPE） | 是 | Withdrawn (superseded by 8141) |
| EIP-5003 | 历史（L3 类） | 是 | 否 | 部分 | Withdrawn |

- **Priority**: high
- **Dependencies**: none

### item-2: 统一 rubric D1~D13 定义

定义 13 个对比维度的判定标准与可填值，确保每维度可独立判定、覆盖用户「原理区别与优势」诉求。

**D1 — 抽象层级（Abstraction Layer）**
- 判定标准：方案的核心逻辑在哪一层执行
- 可填值：`应用层（智能合约）` / `EOA 增强（协议层 + EOA 代理）` / `协议原生（共识/执行层修改）`
- 判定方式：检查是否引入新交易类型、是否修改 EVM/共识逻辑

**D2 — 协议改动范围（Protocol Change Scope）**
- 判定标准：实现该方案需要对以太坊/L2 协议做哪些修改
- 可填值：`无` / `新交易类型` / `新操作码` / `新系统合约` / `共识验证逻辑修改` / `需 EOF` / `需硬分叉`（可多选）
- 判定方式：查阅 EIP/RIP 规范的 "Specification" 和 "Backwards Compatibility" 章节

**D3 — 基础设施依赖（Infrastructure Dependencies）**
- 判定标准：方案运行需要哪些链外基础设施
- 可填值：`Bundler` / `Paymaster 合约` / `EntryPoint 合约` / `Relayer` / `Alt Mempool` / `Verifier 合约` / `Account Config 合约` / `无链外依赖`（可多选）
- 判定方式：分析方案的交易提交流程和参与方

**D4 — 所有权与密钥模型（Ownership & Key Model）**
- 判定标准：账户所有权如何定义，密钥管理的灵活性
- 可填值：`单一 ECDSA 私钥` / `多签（protocol-level）` / `多签（contract-level）` / `可插拔签名验证（任意验证逻辑，完全可编程）` / `可插拔 authenticator（STATICCALL 约束，canonical set 用于 mempool 过滤）` / `社交恢复` / `密钥轮换`（可多选）
- 判定方式：检查验证阶段的执行约束（完全可编程 EVM vs STATICCALL 约束 vs 无 EVM）、是否支持密钥变更、canonical set 与非 canonical authenticator 的能力差异
- 注意：EIP-8130 的 authenticator 是通过 STATICCALL 执行的合约（IAuthenticator 接口），非「无 EVM 执行」；canonical authenticator set 是节点 mempool 过滤所用的白名单，非 canonical authenticator 可在 EVM 执行上下文中使用但不可直接走 8130 交易路径

**D5 — Gas 代付（Gas Sponsorship）**
- 判定标准：是否支持第三方代替用户支付 Gas，实现机制与限制
- 可填值：`不支持` / `Paymaster 合约（需质押）` / `Paymaster 合约（无需质押）` / `payer 字段（permissionless）` / `Paymaster + 协议验证` / `Fee delegation`
- 判定方式：检查方案是否有 paymaster/payer 机制、是否需要白名单/质押、是否支持无许可代付

**D6 — 批量原子性（Batch Atomicity）**
- 判定标准：是否支持将多个操作打包为一个原子交易
- 可填值：`不支持` / `UserOp 内 calldata batching` / `交易级 call batching（协议保证原子性）` / `multicall（合约层）`
- 判定方式：检查交易结构是否原生支持多个 call targets

**D7 — Nonce 与防重放（Nonce & Replay Protection）**
- 判定标准：防重放机制的灵活性与跨链安全性
- 可填值：`协议原生顺序 nonce` / `多维 nonce（key-space）` / `合约层自定义 nonce` / `2D nonce（sequence + key）`
- 判定方式：检查 nonce 管理是否在协议层还是合约层，是否支持并行交易排序

**D8 — EOA 兼容与迁移路径（EOA Compatibility & Migration）**
- 判定标准：现有 EOA 用户如何迁移到该方案，是否需要更换地址
- 可填值：`无需迁移（原地升级）` / `需部署新合约地址` / `可逆代理（保留 EOA 属性）` / `EOA 自动转换` / `不兼容 EOA`
- 判定方式：检查方案对 EOA 的处理方式（delegation、auto-conversion、new deployment）

**D9 — 签名灵活性与后量子准备度（Signature Flexibility & PQ Readiness）**
- 判定标准：支持哪些签名算法，是否能无硬分叉地添加新算法
- 可填值：`仅 ECDSA secp256k1` / `canonical authenticator set（新算法可无许可部署为合约，但纳入 canonical set 需节点客户端更新）` / `任意签名逻辑（合约层，ERC-4337 EntryPoint 内）` / `任意签名逻辑（协议层完全可编程验证，EIP-8141/RIP-7560）`
- 判定方式：检查验证阶段是否限制签名类型、新签名方案的部署路径（无许可部署合约 vs 节点客户端更新 vs 协议硬分叉）
- 注意：EIP-8130 新签名算法可无许可部署为 authenticator 合约，但要被节点 mempool 接受须纳入 canonical set（需客户端更新，不一定需要硬分叉）；enshrined authenticator 可替换 STATICCALL 为原生执行以降低 gas

**D10 — 成熟度与生态（Maturity & Ecosystem）**
- 判定标准：规范状态、部署状态、工具/SDK 支持、活跃开发团队
- 可填值：定性描述，须覆盖规范状态（Final/Draft/Stagnant/Withdrawn/RIP）、主网部署时间、支持的钱包/SDK 数量、活跃 PR/讨论频率
- 判定方式：查阅 EIP 状态、GitHub 活跃度、生态项目列表

**D11 — 安全攻击面（Security Attack Surface）**
- 判定标准：方案引入了哪些新的攻击向量
- 可填值：定性描述，须覆盖验证阶段 DoS（完全可编程 EVM 执行 vs STATICCALL 约束执行 vs 纯密码学检查）、Griefing 攻击（invalidation）、重入风险、代理合约安全、存储碰撞、跨链重放、authenticator/verifier 合约漏洞
- 判定方式：分析验证阶段的计算边界（STATICCALL + bounded gas vs 任意 EVM）、是否有状态修改（STATICCALL 禁止状态修改）、是否有跨合约调用、canonical set 过滤是否有效防止 mempool DoS
- 注意：EIP-8130 的 STATICCALL 约束（无状态修改、有界 gas）显著缩小了验证阶段的攻击面，但 authenticator 合约本身仍可能存在逻辑漏洞（如签名验证绕过）；与 EIP-8141 的完全可编程验证相比，8130 的 DoS 抵抗力更强但灵活性受限

**D12 — Mantle 适配成本（Mantle Adaptation Cost）**
- 判定标准：Mantle（OP Stack L2）实现该方案的工程量和风险
- 可填值：`已支持` / `低（配置/参数调整）` / `中（op-geth/op-node 修改）` / `高（共识层重写 + 硬分叉）` / `极高（需自定义 EVM + 独立生态）` / `不适用（L1-only）`
- 判定方式：评估 Mantle 现有架构（op-geth + OP Stack）与方案要求的差距，参考 Base 实现 EIP-8130 的工程量

**D13 — 目标用户与产品场景适配（Target User & Use Case Fit）**
- 判定标准：方案最适配哪些终端用户群体和产品场景
- 可填值（use case 清单）：
  - `消费者钱包`（社交恢复、密钥轮换、session key、简化 UX）
  - `稳定币/gasless 支付`（Gas 代付、低延迟、高吞吐、memo/payment reference）
  - `企业账户`（多签、权限分级、审计追踪、合规控制）
  - `多签/权限账户`（protocol-level multisig、guardian、time-lock）
  - `Gasless onboarding`（新用户零 Gas 体验、Paymaster/payer sponsorship）
  - `DeFi 高级交易`（批量操作、session key 授权、limit order delegation）
  - `跨链互操作`（chainId=0 签名、跨链账户状态同步）
  - `后量子安全`（可扩展签名方案、无需硬分叉升级验证逻辑）
- 判定方式：分析方案的设计优先级（验证灵活性 vs Gas 效率 vs 实现简洁性）与各场景需求的匹配度

**Rubric 使用规范**：
- 每维度须独立判定，不得因一个维度的评价影响其他维度
- 每格须附可追溯证据（EIP 规范引用、代码路径、PR 链接）或明确标注为 `判断` / `推论` / `code-inferred`
- D12 和 D13 在 WHI-282（Mantle 决策分析）中最终填充，本 framework issue 定义口径和判定方式

- **Priority**: high
- **Dependencies**: item-1

### item-3: 「效果好/不好」四类可观测代理指标与取证方式

将「效果不好」的主观判断转化为客观可测量的指标体系（T3 适用）。

**指标 A — 链上采用度（On-chain Adoption）**
- 度量方式：(a) AA 交易占总交易比例；(b) 活跃智能账户数（日/周/月 unique sender）；(c) AA 相关合约部署数量和 TVL；(d) 特定方案的交易类型占比（如 EIP-7702 delegation tx 占比、4337 UserOp 占比）
- 数据源：Dune Analytics（已有 AA dashboard）、Bundler 公开 API（如 Pimlico/Alchemy stats）、L2 区块浏览器 RPC、链上 EntryPoint 合约事件
- 对比基线：以 Ethereum L1、Base、Polygon 的 4337 采用数据作为跨链对比基线；Mantle 数据与同期同类 L2 对比
- 取证频率：快照式（标注查询日期和区块范围）

**指标 B — 开发者体验与集成成本（Developer Experience & Integration Cost）**
- 度量方式：(a) SDK/工具数量（支持该方案的 wallet SDK、AA SDK 数量）；(b) 文档完整度（官方文档覆盖度、tutorial 数量）；(c) 集成步骤复杂度（从零集成到第一笔 AA 交易的步骤数和时间估算）；(d) 社区活跃度（GitHub stars/forks、Discord/Telegram 开发者频道活跃度）
- 数据源：GitHub repo metrics、SDK 官方文档、Alchemy/Pimlico/ZeroDev/Biconomy 等 AA infra 提供商支持矩阵
- 评估方式：定性 + 定量混合；复杂度估算可用「Mantle 工程师从零到 PoC 的天数」作为标尺
- 取证方式：截图/链接 + 访问日期

**指标 C — 基础设施成本与中心化程度（Infrastructure Cost & Centralization）**
- 度量方式：(a) Bundler 运营成本和数量（公开 Bundler 节点数、是否有去中心化 Bundler 网络）；(b) Paymaster 部署和运营成本；(c) 中心化瓶颈（是否依赖少数 Bundler、是否存在审查风险）；(d) 协议原生方案的硬分叉升级成本
- 数据源：Bundler 运营商公开数据（Pimlico/Alchemy/Biconomy bundler stats）、infra 提供商定价页面、EIP 讨论中的节点运营成本估算
- 评估方式：定性为主；可用 Bundler Herfindahl Index 衡量中心化程度
- 取证方式：链接/截图 + 访问日期

**指标 D — 钱包/SDK 生态支持（Wallet & SDK Ecosystem）**
- 度量方式：(a) 支持该方案的主流钱包数量和市场份额（MetaMask、Safe、Coinbase Wallet、Rabby 等）；(b) AA SDK 集成状态（Alchemy Account Kit、ZeroDev、Biconomy、Pimlico 等）；(c) 基础设施兼容性（区块浏览器 AA 交易解析、索引器支持）；(d) 跨链覆盖度（同一 SDK 支持多少链的同一 AA 方案）
- 数据源：各钱包/SDK 官方文档的 supported chains 列表、AA infra 提供商 blog、Ethereum Magicians 讨论
- 评估方式：支持矩阵表（方案 × 钱包/SDK）
- 取证方式：矩阵表附链接 + 访问日期

**使用规范**：
- 四类指标须分别独立取证，不得混为一谈
- Mantle 数据须与同类 L2（Base、Arbitrum、Optimism）对比，避免孤立数据无法判断好坏
- 「效果不好」的结论须至少两类指标支撑，且需控制混淆变量（如 L2 整体活跃度、市场周期影响）
- 定量指标标注查询时间和区块范围；定性指标标注来源和访问日期

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 证据复用地图

整理现有证据源，标注每项可复用范围与需重新取证项，建立后续 WHI-276~282 的证据索引。

**4.1 源码证据**

| 证据源 | 路径 / 标识 | 用于 | 复用范围 | 备注 |
|---|---|---|---|---|
| Base EIP-8130 交易类型 | `src/networks/base/base/crates/common/consensus/src/transaction/eip8130/` (`constants.rs`, `tx.rs`, `signed.rs`, `account_changes.rs`, `call.rs`, `mod.rs`) | WHI-276（8130 深度分析）主源 | D1/D2/D4/D5/D6/D7/D8 rubric 填充 | 本地 checkout 可用 |
| Mantle op-geth 7702 支持 | `src/networks/mantle/op-geth/` + `src/networks/mantle/revm/crates/bytecode/src/eip7702.rs` | WHI-280（Mantle 现状分析） | D8/D12 rubric 填充 | Pectra 兼容实现 |

**4.2 PR / 提交证据**

| 证据源 | 标识 | 用于 | 复用范围 | 备注 |
|---|---|---|---|---|
| Base 8130 相关 PR（种子） | 本地 checkout 已含 #2863/#2866/#2868/#2926/#3008 + #3119 plumbing | WHI-276 时间线/设计动机 | D2/D10 rubric | **种子列表，须经 base/base PR 搜索补全** |
| Base 8130 上游 in-flight PR | #3121/#3534/#3651/#3653/#3680/#3535/#3540/#3557/#3585/#3586/#3589/#3537/#3553 等 | WHI-276 最新进展 | D10 rubric | **须验证当前合并状态** |
| EIP-8130 spec PR (ethereum/EIPs) | 需检索 | WHI-276 规范演进 | D2/D9 rubric | 主要 PR: naming, cross-chain sig, verifier gas, permissionless payer (#11388) |

**4.3 Daily Intelligence / WHI 引用**

| 证据源 | WHI 编号 | 用于 | 复用范围 |
|---|---|---|---|
| Daily Intelligence 提及 8130 | WHI-90, WHI-106, WHI-175, WHI-239, WHI-241, WHI-253, WHI-265 | WHI-276, WHI-279（Base 选型信号） | 时间线背景 |
| OP 设计文档提及 8130 | `202606-internal-sharing/research-sections/competitor-optimism/final.md`（design-docs 行） | WHI-279 Base/OP 选型语境 | 竞争分析背景 |

**4.4 外部规范与文档**

| 证据源 | URL / 标识 | 用于 | 复用范围 | 备注 |
|---|---|---|---|---|
| EIP-8130 草案 | eips.ethereum.org/EIPS/eip-8130 | WHI-276 全面源 | D1~D11 全部 rubric | Draft 状态，标注访问日期 |
| EIP-7702 规范 | eips.ethereum.org/EIPS/eip-7702 | WHI-277（7702 分析）、本 framework D1~D11 | 全部 rubric | Final, Deployed |
| ERC-4337 规范 | eips.ethereum.org/EIPS/eip-4337 | WHI-278（4337 分析）、本 framework D1~D11 | 全部 rubric | Final ERC |
| RIP-7560 规范 | github.com/ethereum/RIPs/blob/master/RIPS/rip-7560.md | WHI-279（选型分析） | D1~D11 rubric | RIP Draft |
| EIP-8141 规范 | eips.ethereum.org/EIPS/eip-8141 | WHI-279（选型分析，8130 vs 8141 对比） | D1~D11 全部 rubric | Draft, CFI for Hegotá |
| EIP-8141 项目页 | eip8141.io | WHI-279（8130 vs 8141 竞争分析） | 全景综述 | 含 EIP-8130 对比分析 |
| EIP-7701 规范 | eips.ethereum.org/EIPS/eip-7701 | 历史参照 | D1~D11 rubric | Withdrawn, superseded by EIP-8141 |
| EIP-3074 规范 | eips.ethereum.org/EIPS/eip-3074 | 历史参照 | D1/D2/D11 rubric | Withdrawn |
| Biconomy native AA blog (Q1/26) | blog.biconomy.io/native-account-abstraction-state-of-art-and-pending-proposals-q1-26/ | WHI-279 方案对比 | 全景综述 | 二手来源，须交叉验证 |
| Ethernal EIP-8130 技术解析 | tryethernal.com/blog/eip-8130-protocol-level-account-abstraction | WHI-276 技术细节 | D4/D5/D9 rubric | 二手来源 |

**4.5 取证状态与复用规则**

| 复用类型 | 含义 | 使用规则 |
|---------|------|---------|
| 直接引用 | 证据可直接用于 rubric 填充，无需重新取证 | 附原始路径/URL + commit SHA / 访问日期 |
| 需更新验证 | 证据基础有效但需检查最新状态 | 基于种子重新检索，标注更新时间 |
| 需重新取证 | 证据不存在或不适用，需从零调研 | 明确标注「需新取证」和建议数据源 |

**下游 issue 证据需求预估**（deep draft 须验证）：

| Issue | 主要证据需求 | 本 framework 可提供 |
|-------|------------|-------------------|
| WHI-276 EIP-8130 深度 | Base 源码、EIP spec、PR 时间线 | 源码路径 + PR 种子 + EIP URL |
| WHI-277 EIP-7702 深度 | EIP spec、Mantle op-geth、Pectra 部署数据 | EIP URL + Mantle 路径 |
| WHI-278 ERC-4337 深度 | ERC spec、链上数据、SDK 生态 | ERC URL + 数据源指引 |
| WHI-279 选型分析 | 所有方案 spec + Base 选型信号 | 全部 EIP/RIP URL + WHI 引用 |
| WHI-280 Mantle 现状 | Mantle 源码、链上数据、生态调查 | Mantle 路径 + 效果指标口径 |
| WHI-281 实施评估 | 实现难度 + 风险分析 | D12 rubric 口径 |
| WHI-282 决策建议 | 全部 rubric 填充结果 + 效果数据 | 完整 rubric 框架 + D13 use case 清单 |

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| taxonomy_layer | 方案归属层级（L1 应用层 / L2 EOA 增强 / L3 协议原生 / 历史），附判定依据 | item-1 |
| protocol_change | 方案要求的协议修改类型（新交易类型/新操作码/新系统合约/共识修改/EOF/硬分叉），附 EIP 章节引用 | item-1, item-2 |
| rubric_dimension | D1~D13 各维度的判定标准、可填值、判定方式 | item-2 |
| effectiveness_metric | 四类可观测指标的度量方式、数据源、对比基线、取证频率 | item-3 |
| evidence_source | 证据源的路径/URL/标识、用途、复用范围、取证状态 | item-4 |
| proposal_status | 方案的规范状态（Final/Draft/Stagnant/Withdrawn/RIP）+ 访问日期（T2 适用） | all |
| mantle_context | 与 Mantle 现有架构的关系、适配难度、现状描述（T3 适用） | item-2 (D12), item-3, item-4 |
| design_tradeoff | 方案间的设计哲学差异（验证灵活性 vs 实现复杂度 vs 可预测性 vs 后量子准备度） | item-1, item-2 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | taxonomy | AA 方案三层 taxonomy 分类树状图：L1 应用层（4337）→ L2 EOA 增强（7702, 3074-历史）→ L3 协议原生（8130, 7560, 8141）+ 历史方案（7701, 5003），标注每层定义特征和方案状态 | mermaid | item-1 |
| diag-2 | comparison | D1~D13 rubric 横向对比矩阵热力图：活跃方案（4337/7702/8130/7560/8141）× 13 个维度，用颜色深浅表示各维度的相对强弱 | mermaid | item-2 |
| diag-3 | architecture | 三种 native AA 方案的验证流程对比图：EIP-8130（声明 authenticator → STATICCALL 到 authenticator 合约 → canonical set 过滤 → 无状态修改/有界 gas）vs RIP-7560（AA_TX_TYPE → 合约验证 → 完全可编程 EVM 执行）vs EIP-8141（frame tx → VERIFY frame → 完全可编程 EVM 验证 → EXECUTE frame），展示验证阶段的计算边界与 mempool 影响差异 | mermaid | item-1, item-2 |
| diag-4 | flowchart | 效果判定指标取证流程图：四类指标的数据源 → 采集方式 → 对比基线 → 结论判定路径 | mermaid | item-3 |
| diag-5 | mapping | 证据复用地图可视化：证据源节点 → 下游 issue 节点的有向图，边标注复用类型（直接引用/需更新/需重新取证） | mermaid | item-4 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_standard | EIP-8130 草案全文、EIP-8130.com 项目页面、ethereum/EIPs 仓库中的 spec PR（含 permissionless payer #11388）、Ethereum Magicians 讨论帖 | 3 |
| src-2 | official_standard | EIP-7702 规范全文（Final, Deployed）、Pectra 硬分叉规范、EIP-7702 Ethereum Magicians 讨论帖 | 3 |
| src-3 | official_standard | ERC-4337 规范全文（Final ERC）、ERC-4337 Documentation (docs.erc4337.io)、EntryPoint v0.7 部署地址 | 3 |
| src-4 | official_standard | RIP-7560 规范全文（ethereum/RIPs 仓库）、Ethereum Magicians 讨论帖、OP Stack specs discussion #202 (bringing RIP-7560 into OP Stack) | 3 |
| src-5 | official_standard | EIP-8141 规范全文（Draft, CFI for Hegotá）、ethereum/EIPs 仓库 eip-8141.md、Ethereum Magicians 讨论帖、eip8141.io 项目页面 | 3 |
| src-5b | official_standard | EIP-7701 规范全文（Withdrawn, superseded by EIP-8141）、EIP-7701 explained page (eips.ethereum.org/assets/eip-7701/)——作为历史参照 | 1 |
| src-6 | code_analysis | Base EIP-8130 实现源码（`crates/common/consensus/src/transaction/eip8130/`）、Base 8130 相关合并 PR（种子 #2863/#2866/#2868/#2926/#3008/#3119）、base/base 仓库 HEAD 提交 | 3 |
| src-7 | code_analysis | Mantle op-geth EIP-7702 实现（revm `eip7702.rs`、op-geth tracer testdata）、Mantle 4337 基础设施部署（EntryPoint 合约地址） | 2 |
| src-8 | secondary_analysis | Biconomy "Native AA: State-of-Art and Pending Proposals (Q1/26)" blog、Ethernal EIP-8130 技术解析、Alchemy EIP-3074 vs 7702 vs 4337 对比指南 | 3 |
| src-9 | on_chain_data | AA 采用数据（Dune Analytics AA dashboard、Pimlico/Alchemy bundler stats）、Mantle AA 链上数据（需新取证） | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create | all | 初始创建 | Orchestrator Dispatch (5e99f9a5) |
| 2 | modify | item-1 Layer 3, taxonomy table | EIP-7701 status Stagnant→Withdrawn (superseded by EIP-8141); EIP-5003 status Stagnant→Withdrawn; 新增 EIP-8141 (Frame Transaction, Draft, CFI for Hegotá) 到 L3 协议原生层; EIP-7701 移至历史方案 | Review Verdict (2a62803f) — major finding |
| 2 | modify | item-1 taxonomy table | 新增 EIP-8141 行; EIP-7701 从 L3 移至历史; EIP-5003 状态更新为 Withdrawn | Review Verdict (2a62803f) — major finding |
| 2 | modify | item-2 D4/D9/D11 | 修正 EIP-8130 验证模型：authenticator 是通过 STATICCALL 执行的合约（非「无 EVM 执行」）; 区分 canonical authenticator set（mempool 过滤）与非 canonical authenticator（EVM 上下文可用）; 链 MAY enshrine 或按普通 EVM 计量 | Review Verdict (2a62803f) — major finding |
| 2 | modify | T1/T2 guardrails | T1 更新 L3 列表（+8141, -7701）; T2 新增 EIP-8141/EIP-5003 状态标注要求, 修正 EIP-7701 为 Withdrawn | Revision Request (76660a17) |
| 2 | modify | Research Questions Q1/Q4 | Q1 更新方案列表（+8141, 7701 移至历史）; Q4 重写为 8130 vs 8141 竞争分析视角 | Revision Request (76660a17) |
| 2 | modify | diag-1/diag-2/diag-3 | diag-1 更新 L3 方案列表; diag-2 更新为活跃方案矩阵; diag-3 修正 8130 验证流程为 STATICCALL 模型, 7701→8141 | Revision Request (76660a17) |
| 2 | modify | src-5, evidence map | src-5 替换为 EIP-8141 规范; 新增 src-5b 作为 EIP-7701 历史参照; 证据复用地图新增 EIP-8141 规范和项目页 | Revision Request (76660a17) |
