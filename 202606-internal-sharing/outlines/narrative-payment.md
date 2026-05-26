---
topic: "Payment Chain 叙事方向技术分析"
project_slug: "202606-internal-sharing"
topic_slug: "narrative-payment"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/narrative-payment.md"
  draft: "202606-internal-sharing/research-sections/narrative-payment/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/narrative-payment/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  从 Mantle 视角评估 Payment Chain 作为叙事转移方向的可行性，覆盖三组问题：
  1) 市场数据与规模：稳定币支付市场、跨境支付痛点、主要项目采用数据；
  2) 关键技术对比：终局性、原生稳定币 Gas / Paymaster、Payment Lane、法币 On/Off Ramp；
  3) Mantle 适配性：UR 生态与 preconfs 对支付场景的帮助、L2 软确认与专用支付链的差距、
     B2B 结算子场景是否是更现实切入点。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、协议工程师、生态/BD/战略研究同事、
  支付/稳定币产品方向负责人，以及 Multica Research Squad 的 Review Agent 和后续写作者。
  读者熟悉 L1/L2、稳定币、AA/Paymaster、rollup 终局性和跨境支付概念，但需要一份可直接支持
  内部分享 Section 3.2 的中文方向评估，而不是 Tempo 或 Arc 的单项目重复介绍。

expected_output: |
  一份中文结构化 research section，最终必须输出评估表格：
  市场阶段 / 市场规模 / 主要竞品 / 关键技术 / Mantle 优势 / Mantle 挑战 / 契合度判断。
  正文需包含：
  - 稳定币支付市场与传统跨境支付痛点的量化判断；
  - Tempo、Circle Arc、Sui gasless stablecoin payments、Base/Solana、Canton/Prividium 等方案对比；
  - 终局性、稳定币 Gas/Paymaster、Payment Lane、On/Off Ramp 四类技术 gap 分析；
  - Mantle 进入支付赛道的短中长期路线建议，重点评估 B2B 结算而非泛化 C2C 支付；
  - 至少 3 张图/表：支付市场证据表、关键技术对比矩阵、Mantle 契合度/路线图。

source_requirements_summary: |
  深度研究必须优先复用并交叉引用本仓库已有 payment-tempo、payment-ark、competitor-sui、
  narrative-analysis final sections，避免重复单项目研究。所有市场规模、支付量、链上稳定币交易量、
  跨境支付成本/时延、项目采用数据、网络状态和融资/合作伙伴数据均属于易过期事实，必须在 draft 阶段
  用 2026-05-26 或之后的访问日期重新核验，标注 source date、accessed_at、evidence_confidence。
  行业报告、官方文档和链上数据应优先于媒体二手报道；无法核验的 adoption 或 partner logo 只能作为 caveat。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-26T08:02:17+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-26T08:02:17+08:00"

multica_issue_id: "8687a4a3-5f1e-4d8e-9b33-bea472d9a0b9"
branch_name: "research/202606-internal-sharing/narrative-payment"
base_commit: "196f34d"
language: "中文"
research_depth: "standard"

prerequisite_sections:
  - slug: payment-tempo
    path: 202606-internal-sharing/research-sections/payment-tempo/final.md
    status: existing-research
  - slug: payment-ark
    path: 202606-internal-sharing/research-sections/payment-ark/final.md
    status: existing-research
  - slug: competitor-sui
    path: 202606-internal-sharing/research-sections/competitor-sui/final.md
    status: existing-research
  - slug: narrative-analysis
    path: 202606-internal-sharing/research-sections/narrative-analysis/final.md
    status: existing-research
  - slug: enterprise-canton
    path: 202606-internal-sharing/research-sections/enterprise-canton/final.md
    status: existing-research
  - slug: enterprise-privacy
    path: 202606-internal-sharing/research-sections/enterprise-privacy/final.md
    status: existing-research
---

# Research Outline: Payment Chain 叙事方向技术分析

## Research Questions

1. 稳定币支付是否已经从 crypto-native 转账进入真实支付/结算市场，还是仍处于基础设施和试点阶段？哪些市场数据可以支撑这一阶段判断？
2. 传统跨境支付的主要痛点是什么：时延、费用、中间行链条、透明度、拒付/退款、合规、资金预置和对账分别有多严重？
3. Tempo、Circle Arc、Sui gasless stablecoin payments、Base/Solana、Canton/Prividium 等方案分别解决支付链中的哪一层问题？哪些只是叙事或测试网信号？
4. 支付场景对终局性、费用确定性、交易优先级、账户体验、合规策略和法币出入金的真实要求是什么？Mantle 当前 L2 架构与专用支付链的 gap 有多大？
5. Mantle 的 UR 生态、preconfs、EVM/OP 兼容、mETH/cmETH/yield、DeFi 流动性和潜在 Paymaster 能力，哪些能支持支付叙事，哪些不足以支撑 mass adoption？
6. "支付需要通过 Web2 企业进行分流，纯 crypto 方案很难 mass adoption" 这一论点能否用数据和案例论证？Mantle 更适合 C2C 支付、商户收单、跨境汇款，还是 B2B/treasury 结算？
7. 最终评估表中，Payment Chain 对 Mantle 的契合度应判为强、中、弱，或分子场景判定？判断依据应如何写得可复核、不过度乐观？

## Items

### item-1: 市场阶段与稳定币支付规模校准

建立 Payment Chain 叙事的市场事实底座，区分稳定币链上转账、真实支付、交易所/做市流、DeFi 内循环和企业结算。需要用多源数据判断稳定币支付处于"基础设施加速建设 / 早期商业化 / 已规模化采用"中的哪个阶段。

必须覆盖：

- 稳定币总供应量、链上转账量、活跃地址/钱包、商户/企业采用、稳定币结算网络或支付网络披露数据；
- 交易量口径拆分：交易所/套利/DeFi/桥/做市/真实支付；不得直接把稳定币链上总转账量等同于支付市场规模；
- 跨境支付、B2B payment、remittance、merchant acquiring、treasury settlement 等可服务市场的 TAM/SAM 口径；
- 主要行业报告和官方披露：Visa Onchain Analytics、Circle reports、Artemis/DefiLlama/RWA.xyz、McKinsey/World Bank/BIS/FSB 等；
- 市场阶段判断：基础设施供给（Tempo/Arc/Paymaster/CCTP）是否领先于需求侧采用；Web2 支付/金融机构参与是否是 adoption 的关键瓶颈；
- 数字必须给 source date 和 accessed_at；若不同来源口径冲突，保留区间并解释差异。

- **Priority**: high
- **Dependencies**: none

### item-2: 传统跨境支付痛点与链上支付可替代边界

量化传统跨境支付的痛点，并判断链上稳定币 rails 真正能替代哪一段。需要避免把 SWIFT、correspondent banking、PSP、卡网络、ACH/SEPA/FPS、remittance provider 和 treasury workflow 混成一个对象。

必须覆盖：

- 成本：B2B cross-border、remittance、card acquiring、FX spread、中间行费用、资金预置/nostro-vostro 成本；
- 时延：银行工作日、跨时区、合规审查、银行清结算、卡网络授权 vs settlement、稳定币链上最终性之间的区别；
- 透明度和对账：支付状态可见性、失败/退回、费用扣减、invoice/order reconciliation；
- 合规和风控：KYC/KYB、AML/sanctions、travel rule、chargeback/退款/争议处理、消费者保护；
- On/Off Ramp：本地法币入金、出金、牌照、银行合作、账户体系和区域覆盖；
- 哪些痛点链上 rails 能直接改善，哪些仍依赖 Web2 企业、PSP、银行、发行方或合规服务商；
- B2B/treasury 结算为何可能比零售商户或 C2C 支付更适合 Mantle 初期切入。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 主要竞品与采用数据：Tempo、Circle Arc、Sui、Base/Solana、Canton

建立可复核竞品图谱，把每个方案的定位、发展阶段、采用数据和证据等级放到同一张表中。重点是 Mantle 视角下的方向可行性，不重复 Tempo/Arc 单项目技术介绍。

必须覆盖：

- **Tempo**：payments-first L1、Payment Lane、stablecoin gas、TIP-20/TIP-403、Visa validator 或设计伙伴信号；复用 `payment-tempo/final.md`，刷新网络状态、adoption、SLA/性能证据；
- **Circle Arc**：USDC-native stablecoin finance L1、StableFX、Partner Stablecoins、CCTP、testnet/mainnet 状态、机构/代币预售信号；复用 `payment-ark/final.md`，刷新主网/测试网和采用口径；
- **Sui gasless stablecoin payments**：sponsored transactions、gasless/free-tier stablecoin transfers、Fireblocks/机构托管或钱包集成路径；从 `competitor-sui/final.md` 和官方资料中抽取支付相关部分；
- **Base / Solana**：不是专用支付链，但有分发、稳定币、consumer/payments、CCTP/Paymaster/merchant 叙事；引用 `narrative-analysis/final.md` 并刷新关键近期资料；
- **Canton / Prividium / 企业隐私链**：面向机构工作流和隐私结算，不是通用支付链；用于 B2B/机构支付边界对照；
- 每个竞品都必须标注：市场阶段、主要支付场景、关键技术、公开采用数据、evidence_confidence、主要 caveat、对 Mantle 的直接压力。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: 终局性要求：L2 软确认、preconfs 与 BFT 硬终局

分析支付场景到底需要什么层级的最终性，并把 Mantle 当前 L2/rollup 路线与 Tempo/Arc 等 BFT 硬终局方案对比。需要区分用户体验确认、商户放行、链上经济最终性、L1 最终性、银行/法币结算最终性。

必须覆盖：

- 终局性分类：mempool/排序确认、preconfirmation、L2 soft confirmation、BFT deterministic finality、Ethereum L1 finality、challenge/fraud-proof finality、法币清结算最终性；
- 不同支付场景需求：零售 POS、线上商户收单、B2B invoice payment、treasury transfer、跨境汇款、agent/micropayment、DeFi settlement；
- Mantle 当前或规划 preconfs/UR 相关能力对支付体验的帮助：能否支撑商户先放行、何时需要风险准备金或风控阈值；
- Tempo/Arc 亚秒或亚秒级 BFT 硬终局的优势与 caveat：验证者许可、主网实测、去中心化、链上最终性不等于法币结算；
- L2 软确认 gap 的工程补救：preconf SLA、sequencer reputation/slashing、保险/风险限额、payment-specific confirmation policy、跨链消息最终性；
- 最终输出一个场景 x finality requirement 表，明确 Mantle 在各场景中是足够、需增强、还是结构性劣势。

- **Priority**: high
- **Dependencies**: item-3

### item-5: 原生稳定币 Gas、Paymaster 与账户体验

比较 Tempo/Arc/Sui 的原生或近原生稳定币支付体验，与 Mantle 可通过 ERC-4337 Paymaster、EIP-7702、AA 钱包、合约赞助和稳定币 gas abstraction 实现的路径。目标是判断 Mantle 是否能在不改底层共识的情况下实现接近支付链的 UX。

必须覆盖：

- Tempo stablecoin gas / attodollars / fee sponsorship、Circle Arc USDC gas / Paymaster / StableFX、Sui sponsored/gasless stablecoin transfers；
- Mantle 当前可用路径：ERC-4337 Paymaster、account abstraction、EIP-7702、trusted relayer、merchant-sponsored gas、gas tank、stablecoin-denominated fee quote；
- 支付 UX 关键能力：用户无需持有原生 gas token、固定/可预测费用、批量付款、限额 access key、passkey/P256/WebAuthn、validity window、memo/order id；
- 经济和安全问题：Paymaster 资金池、MEV/拥堵时费用波动、代付滥用、DoS、合规拒绝、退款、商户承担 gas 的定价模型；
- ERC-20 稳定币生态兼容性 vs 协议级稳定币标准的 tradeoff：Mantle 不应轻易复制 TIP-20 替代现有 ERC-20；
- 输出 Mantle 可落地优先级：短期应用层/SDK，中期 system contract/predeploy，长期客户端或 fee market 改造。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: Payment Lane、优先级通道与 Mantle Sequencer 改造可行性

研究 Payment Lane 是否是支付链的关键差异化，以及 Mantle 是否能用 sequencer/payload builder/txpool 策略或应用层通道实现类似效果。需要把协议级 blockspace 保障和普通 private mempool、MEV protection、priority fee 区分开。

必须覆盖：

- Tempo Payment Lane 的核心机制：System/Payment/General lane、`general_gas_limit`、`shared_gas_limit`、支付交易分类、拥堵时非支付交易被限制；
- Arc/Base/Solana/Sui 是否有等价支付专用 blockspace，还是依赖通用高吞吐/费用模型/Paymaster；
- Mantle 可选实现层：
  1. 应用层：支付 SDK + relayer + merchant API + priority RPC；
  2. Sequencer policy：payment tag、trusted relayer allowlist、fee sponsorship lane、private mempool；
  3. Payload builder/txpool：无状态分类、gas 预算隔离、predeploy policy；
  4. 协议/治理层：SLA、费用市场、监控、公开参数和反滥用规则；
- 技术风险：抗审查、公平性、MEV、DoS、分类绕过、监管/合规责任、与 OP Stack 或 Mantle 当前客户端的兼容性；
- 评估 Payment Lane 对 Mantle 的必要性：哪些支付场景必须要，哪些只靠 paymaster/preconf/SDK 已足够；
- 输出 "Mantle payment lane feasibility" 表：改造层级、工程量、收益、风险、是否建议。

- **Priority**: high
- **Dependencies**: item-4, item-5

### item-7: 法币 On/Off Ramp、Web2 分流与商业闭环

验证 "支付需要通过 Web2 企业进行分流，纯 crypto 方案很难 mass adoption" 这一论点。研究重点不是链上转账本身，而是用户/企业如何进入和离开稳定币 rails，以及商户、PSP、银行和发行方在支付链 adoption 中的角色。

必须覆盖：

- On-ramp/off-ramp 类型：交易所、银行账户、PSP、卡收单、稳定币发行方 mint/redeem、企业 treasury account、本地支付网络；
- Web2 企业角色：Stripe、Circle、Visa、PayPal、Coinbase、Fireblocks、Nubank、Shopify、银行和区域 PSP 如何提供分发、合规、资金通道和商户关系；
- 纯 crypto 支付的 adoption 障碍：用户钱包、私钥、gas、退款/争议、税务、商户对账、法币结算、监管责任；
- Mantle 生态现有或潜在入口：UR 生态、钱包/AA、DeFi/yield、稳定币流动性、桥/CCTP/LayerZero/Relay、merchant/treasury partners；
- B2B 结算、merchant treasury、payroll、跨境供应商付款、stablecoin-to-yield treasury 是否比零售 checkout 更适合 Mantle；
- 输出一个支付商业闭环图：用户/企业 -> on-ramp -> chain settlement -> liquidity/yield -> off-ramp/reconciliation，并标注 Mantle 当前缺口。

- **Priority**: high
- **Dependencies**: item-2, item-3

### item-8: Mantle 适配性评估与 B2B 结算子场景

把前面市场和技术分析落到 Mantle 的方向判断。必须分别评估优势、挑战、差距、可执行路线和契合度，不允许只给泛泛建议。

必须覆盖：

- Mantle 优势：
  - Ethereum-aligned EVM/L2 生态，开发者和资产迁移成本低；
  - UR 生态、钱包/账户体验、preconfs 对支付 UX 的潜在帮助；
  - mETH/cmETH/yield-bearing 生态和 DeFi 流动性可服务企业 treasury / settlement 后资金管理；
  - 模块化 DA/EigenDA、低费和高吞吐路线可支撑批量结算；
  - 可通过 Paymaster/AA/SDK 快速做稳定币支付 UX，不必先改共识。
- Mantle 挑战：
  - L2 soft confirmation 与 BFT 硬终局 gap；
  - 没有原生稳定币发行方或 Web2 支付分发网络；
  - 缺少 payment-specific blockspace、商户 API、on/off ramp、合规策略、reconciliation 标准；
  - 与 Tempo/Arc 的专用架构、Circle/Stripe/Visa 等生态背书相比叙事不够锐利；
  - 监管/牌照/退款/争议等链外问题无法由链本身解决。
- 子场景判断：B2B invoice settlement、merchant treasury settlement、跨境供应商付款、payroll/批量付款、agent/micropayment、retail checkout、C2C remittance 的适配度；
- 路线建议：短期应用层 demo/SDK， 中期 sequencer/payment lane/paymaster 标准，长期企业隐私 L3或支付合作；
- 最终给出契合度判断：建议按子场景给强/中/弱，而不是对 Payment Chain 整体给单一结论。

- **Priority**: high
- **Dependencies**: item-4, item-5, item-6, item-7

### item-9: 最终评估表、风险与事实核验清单

组织最终 section 的决策输出，确保评估表可复核、可用于内部分享，同时显式保留 caveats，避免把叙事写成已验证 adoption。

必须覆盖：

- 必填评估表：
  - 市场阶段：数据支撑的阶段判断；
  - 市场规模：区分链上稳定币规模、跨境支付 TAM、B2B/merchant 可服务市场；
  - 主要竞品：Tempo、Circle Arc、Sui、Base/Solana、Canton/Prividium；
  - 关键技术：终局性、稳定币 Gas/Paymaster、Payment Lane、On/Off Ramp；
  - Mantle 优势：必须对应具体能力；
  - Mantle 挑战：必须对应具体 gap；
  - 契合度判断：按 B2B/treasury、merchant、retail、C2C 等子场景给强/中/弱。
- 风险清单：市场数据口径、partner logo 过度解读、主网/测试网混淆、链上最终性与法币最终性混淆、paymaster 经济性、sequencer 改造风险、监管和牌照责任；
- 事实核验清单：所有高风险数字必须有 source date、accessed_at、confidence；所有竞品 adoption 数据必须注明 official/testnet/media/secondary；
- Presentation-ready 输出：最后应给 3-5 条可直接放入内部分享的短句，但每条后面必须有 caveat 或证据来源指向。

- **Priority**: high
- **Dependencies**: all

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| market_segment | 稳定币链上转账、跨境 B2B、remittance、merchant acquiring、treasury settlement、payroll、agent/micropayment、零售/C2C | item-1, item-2, item-7, item-8 |
| metric_name | 市场或采用指标名称：供应量、转账量、活跃地址、费用、时延、采用机构数、testnet tx、payment volume、TAM/SAM 等 | item-1, item-2, item-3, item-9 |
| metric_value | 指标数值及单位；不确定时给区间或标注 unavailable | item-1, item-2, item-3, item-9 |
| source_url | 可追溯 URL 或仓库内路径，必须支持 reviewer 复核 | all |
| source_date | 来源发布日期、报告日期、数据快照日期或链上查询日期 | all |
| accessed_at | 实际访问/核验日期；draft 阶段建议统一使用撰写日期 | all |
| evidence_confidence | `verified-primary`、`verified-data`、`official-announcement`、`existing-research`、`media-reported`、`secondary-only`、`inferred`、`stale-needs-refresh`、`speculative` | all |
| payment_scenario | 跨境汇款、B2B invoice、merchant checkout、merchant treasury、payroll、batch payment、agent/micropayment、链上 FX、企业隐私结算 | item-2, item-4, item-5, item-7, item-8 |
| finality_requirement | 用户体验确认、商户放行、链上经济最终性、L1 finality、fraud-proof/challenge finality、法币清结算最终性 | item-4 |
| technology_component | BFT finality、preconfs、soft confirmation、Paymaster、stablecoin gas、Payment Lane、sequencer policy、CCTP、on/off ramp、memo/reconciliation、TIP-403/compliance policy | item-3, item-4, item-5, item-6, item-7 |
| competitor | Tempo、Circle Arc、Sui、Base、Solana、Canton、Prividium、traditional PSP、Mantle | item-3, item-4, item-5, item-6 |
| competitor_pressure_on_mantle | 对 Mantle 的压力类型：finality、stablecoin_issuer、web2_distribution、payment_lane、gas_ux、institutional_trust、on_off_ramp、merchant_api、liquidity | item-3, item-8 |
| mantle_advantage | Mantle 相关优势：EVM/L2、UR、preconfs、Paymaster 可行性、mETH/cmETH/yield、DeFi liquidity、low fee、modular DA、enterprise L3 潜力 | item-8, item-9 |
| mantle_challenge | Mantle 相关挑战：soft finality、无原生支付分发、缺少 on/off ramp、缺少 payment lane、缺少合规/对账标准、监管责任、生态证据不足 | item-8, item-9 |
| implementation_effort | Mantle 若采用相关设计的工程量级：application_sdk、paymaster_config、system_contract、sequencer_policy、client_txpool_builder、architecture_level、bd_partnership | item-5, item-6, item-8 |
| fit_assessment | strong / medium / weak / monitor，并给出数据或技术理由 | item-8, item-9 |
| caveat | 证据限制、口径冲突、测试网/主网差异、链上/链下边界、媒体偏差、未验证伙伴关系 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | evidence_table | 支付市场证据表：稳定币链上规模、跨境支付痛点、B2B/merchant/remittance 市场、代表来源、口径 caveat | markdown table | item-1, item-2 |
| diag-2 | comparison_matrix | 竞品与技术对比矩阵：Tempo、Arc、Sui、Base/Solana、Canton/Prividium、Mantle，维度包括 finality、gas UX、payment lane、on/off ramp、adoption、trust boundary | markdown table | item-3, item-4, item-5, item-6 |
| diag-3 | flow | 支付商业闭环流程：payer/enterprise -> on-ramp -> wallet/account -> chain settlement -> liquidity/yield -> off-ramp/reconciliation，标注 Web2 企业和 Mantle 缺口 | mermaid flowchart | item-7, item-8 |
| diag-4 | scenario_matrix | Mantle 子场景契合度矩阵：B2B invoice、merchant treasury、payroll、merchant checkout、agent micropayment、retail/C2C；列出优势、挑战、所需能力、契合度 | markdown table | item-8, item-9 |
| diag-5 | roadmap | Mantle payment narrative roadmap：短期 SDK/Paymaster/demo，中期 preconf/payment lane/system contract，长期 enterprise L3/partner rails；标注工程量和风险 | mermaid gantt or flowchart | item-8 |
| diag-6 | final_table | 最终必填评估表：市场阶段/市场规模/主要竞品/关键技术/Mantle 优势/Mantle 挑战/契合度判断 | markdown table | item-9 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | existing_research | 本仓库 `202606-internal-sharing/research-sections/payment-tempo/final.md`，用于 Tempo 技术与 caveat baseline | 1 |
| src-2 | existing_research | 本仓库 `202606-internal-sharing/research-sections/payment-ark/final.md`，用于 Circle Arc 技术、市场阶段与 caveat baseline | 1 |
| src-3 | existing_research | 本仓库 `202606-internal-sharing/research-sections/competitor-sui/final.md`，抽取 gasless stablecoin / sponsored transaction 相关内容 | 1 |
| src-4 | existing_research | 本仓库 `202606-internal-sharing/research-sections/narrative-analysis/final.md`，用于支付叙事趋势、Base/Solana/Tempo/Arc 公开传播 baseline | 1 |
| src-5 | existing_research | 本仓库 enterprise-canton 与 enterprise-privacy final sections，用于 B2B/机构/隐私结算对照 | 2 |
| src-6 | official_docs | Tempo、Circle Arc、Sui、Base/Coinbase、Solana、Canton/Prividium 官方文档或公告，刷新网络状态和支付能力 | 8 |
| src-7 | market_data | 稳定币供应/交易/支付相关数据：Visa Onchain Analytics、Artemis、DefiLlama、RWA.xyz、Circle reports、Coin Metrics 或等价数据源 | 5 |
| src-8 | industry_reports | 跨境支付与支付成本/时延报告：World Bank remittance、McKinsey Global Payments、BIS/FSB、Swift、JPMorgan/BCG 等 | 4 |
| src-9 | official_announcement | Web2 支付/金融机构公告：Visa、Stripe、Circle、PayPal、Coinbase、Fireblocks、Shopify/Nubank 等，验证分发和采用信号 | 4 |
| src-10 | technical_standards | ERC-4337、EIP-7702、AA/Paymaster、OP Stack/Mantle preconf 或 sequencer 相关技术资料，用于 Mantle 可行性判断 | 3 |
| src-11 | data_integrity | 对融资、估值、主网/测试网、交易量、partner logo、采用数据等高风险事实，至少使用 2 类来源交叉验证，无法验证则降级为 caveat | 8 |

## Evidence Starting Points

### Internal Research

- Tempo final: `202606-internal-sharing/research-sections/payment-tempo/final.md`
- Circle Arc final: `202606-internal-sharing/research-sections/payment-ark/final.md`
- Sui final: `202606-internal-sharing/research-sections/competitor-sui/final.md`
- Narrative analysis final: `202606-internal-sharing/research-sections/narrative-analysis/final.md`
- Canton final: `202606-internal-sharing/research-sections/enterprise-canton/final.md`
- Enterprise privacy final: `202606-internal-sharing/research-sections/enterprise-privacy/final.md`

### Market And Payment Data

- Visa Onchain Analytics: `https://visaonchainanalytics.com/`
- Artemis stablecoin dashboards: `https://app.artemis.xyz/`
- DefiLlama stablecoins: `https://defillama.com/stablecoins`
- Circle reports / Internet Financial System materials: `https://www.circle.com/reports`
- World Bank Remittance Prices Worldwide: `https://remittanceprices.worldbank.org/`
- BIS / FSB stablecoin and cross-border payments reports: verify latest versions during draft
- McKinsey Global Payments Report: verify latest version during draft

### Competitor Primary Sources

- Tempo website/docs: `https://tempo.xyz/`, `https://docs.tempo.xyz/`
- Circle Arc website/docs/blog: `https://www.arc.io/`, `https://docs.arc.io/`, `https://www.circle.com/blog`
- Sui docs/blog for sponsored transactions and gasless stablecoin transfers: verify latest source during draft
- Base blog/docs for Paymaster, Flashblocks, stablecoin/onchain commerce: `https://base.org/blog`, `https://docs.base.org/`
- Solana news/Foundation for PayFi, stablecoins and consumer payments: `https://solana.com/news`, `https://solana.org/news`
- Canton Network and Digital Asset docs/news: `https://www.canton.network/`, `https://www.digitalasset.com/`

### Mantle / Technical Sources

- Mantle docs and roadmap pages for current architecture, preconfs, UR, account/payment capabilities: verify latest source during draft
- ERC-4337 documentation and EIP-7702 specification for Paymaster / account UX feasibility
- OP Stack / preconfirmation references relevant to Mantle sequencing and finality

## Draft Structure Recommendation

1. Executive summary：Payment Chain 对 Mantle 的一句话判断，先给结论和契合度。
2. 市场阶段与规模：稳定币支付、跨境支付痛点、可服务市场和 adoption 证据。
3. 竞品格局：Tempo、Circle Arc、Sui、Base/Solana、Canton/Prividium 的定位、采用和 caveat。
4. 技术 gap 分析 I - 终局性：soft confirmation / preconfs / BFT finality / 法币最终性。
5. 技术 gap 分析 II - 稳定币 Gas 与账户体验：Paymaster、AA、fee sponsorship、passkey/access key。
6. 技术 gap 分析 III - Payment Lane 与 sequencer 改造：Mantle 可行性和风险。
7. 商业闭环：On/Off Ramp、Web2 分流、PSP/银行/发行方角色和纯 crypto 支付限制。
8. Mantle 适配性：优势、挑战、B2B 结算子场景、路线建议。
9. 最终评估表：市场阶段/规模/竞品/技术/Mantle 优势/挑战/契合度。
10. 风险、开放问题和 source appendix。

## Quality Checklist

- [ ] 所有市场规模、支付量、交易量、费用、时延和采用数据都有 source date、accessed_at、evidence_confidence。
- [ ] 明确区分链上稳定币转账量、真实支付 volume、跨境支付 TAM、B2B 可服务市场，避免直接等同。
- [ ] 明确区分用户体验确认、L2 soft confirmation、preconf、BFT 链上最终性、Ethereum L1 finality 和法币清结算最终性。
- [ ] 复用 payment-tempo、payment-ark、competitor-sui、narrative-analysis 等已有 final，但不把旧事实自动当作当前事实。
- [ ] 对 Tempo/Arc/Sui/Base/Solana/Canton 的 adoption 数据分别标注 official/testnet/mainnet/media/secondary，不把 partner logo 当生产集成。
- [ ] 对 Mantle 的建议分短期应用层、中期 sequencer/system contract、长期战略合作/企业 L3，不把架构级改造写成轻量工作。
- [ ] 必须论证 Web2 企业/PSP/银行/发行方在支付 adoption 中的角色，并说明纯 crypto 方案的 mass adoption 障碍。
- [ ] 最终表格必须覆盖用户指定的 7 个维度，且契合度最好按子场景拆分强/中/弱。
- [ ] 至少包含 3 个图/表，其中必须有竞品技术对比矩阵和 Mantle 子场景契合度矩阵。
- [ ] 所有 presentation-ready 结论都必须能回溯到正文证据或明确 caveat。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create | full outline | Initial outline from Orchestrator dispatch | Multica issue 8687a4a3-5f1e-4d8e-9b33-bea472d9a0b9 comment 7b04940d-3dc8-43fa-9893-245f44103808 |
