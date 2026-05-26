---
topic: "AgentFi 叙事方向技术分析"
project_slug: "202606-internal-sharing"
topic_slug: "narrative-agentfi"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/narrative-agentfi.md"
  draft: "202606-internal-sharing/research-sections/narrative-agentfi/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/narrative-agentfi/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  分析 AgentFi 作为 Mantle 可能叙事转移方向的市场和技术可行性。研究范围包括：
  AgentFi 市场阶段和市场规模、主要竞品（Solana、Base、专用 Agent 链/协议）、
  Agent 钱包与链上身份、账户抽象/Session Key、低延迟低 Gas 执行环境、
  Agent 间协作协议与支付通道、主流 AI Agent 框架与链上交互模式，以及 Mantle
  在 EVM 兼容、账户抽象、低成本执行、流动性和差异化叙事上的适配性。

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享准备者、协议/账户抽象/钱包工程师、
  生态与 BD 团队、战略研究同事，以及 Multica Research Squad 的 Research Review Agent
  和后续写作者。读者熟悉 L2、EVM、账户抽象和 AI agent 基础概念，但需要一份可直接服务
  内部分享 Section 3.1 的中文技术+市场评估，而不是泛化 AI crypto 热点综述。

expected_output: |
  一份中文结构化 research section，最终必须填充以下评估表格：

  | 维度 | 内容 |
  |---|---|
  | **市场阶段** | [研究结论] |
  | **市场规模** | [数据/估算] |
  | **主要竞品** | [竞品列表与分析] |
  | **关键技术** | [技术要点] |
  | **Mantle 优势** | [评估] |
  | **Mantle 挑战** | [评估] |
  | **契合度判断** | [强/中/弱 + 理由] |

  Section 还应输出：市场阶段判断、竞品矩阵、关键技术栈拆解、Mantle 可落地路线、
  叙事适配度判断、风险与开放问题。语言为中文。

source_requirements_summary: |
  Deep draft 必须使用 2026-02-26 至实际撰写日的最近约 3 个月公开信息作为默认窗口；
  市值、交易量、活跃 agent 数、协议收入、x402/ACP 交易量等易过期数字必须记录来源、
  访问日期和口径，并在结论中降级处理。内部 sibling research（Solana、Base、Sui、
  Tempo、Arc、narrative-analysis）只能作为背景和已审事实起点，所有 AgentFi 专项结论
  需要用官方文档、链上/市场数据或主流媒体重新核验。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-26T08:06:47+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-26T08:06:47+08:00"

multica_issue_id: "c0915c5b-036a-43ba-be45-e8e210f07574"
branch_name: "research/202606-internal-sharing/narrative-agentfi"
base_commit: "196f34db73d8d03ce070aa0218825b1cea67e1f6"
language: "中文"
research_depth: "standard"

prerequisite_sections:
  - slug: competitor-solana
    path: 202606-internal-sharing/research-sections/competitor-solana/final.md
    status: existing-research
  - slug: competitor-base
    path: 202606-internal-sharing/research-sections/competitor-base/final.md
    status: existing-research
  - slug: competitor-sui
    path: 202606-internal-sharing/research-sections/competitor-sui/final.md
    status: existing-research
  - slug: payment-tempo
    path: 202606-internal-sharing/research-sections/payment-tempo/final.md
    status: existing-research
  - slug: payment-ark
    path: 202606-internal-sharing/research-sections/payment-ark/final.md
    status: existing-research
  - slug: narrative-analysis
    path: 202606-internal-sharing/research-sections/narrative-analysis/final.md
    status: existing-research
---

# Research Outline: AgentFi 叙事方向技术分析

## Research Questions

1. AgentFi 当前到底处于哪个市场阶段：AI meme/agent token 资产发行热度、可运行 agent 应用、agent-to-agent commerce、还是生产级链上自动化金融？
2. AgentFi 的可量化市场规模应如何估算：AI agents 代币总市值、Virtuals/launchpad 交易与费用、x402/ACP/agent payment 交易量、agent framework 开发者活跃度、链上 agent 钱包/交易数各自代表什么？
3. Solana、Base、Sui、专用 Agent 链/协议（Virtuals、AgentLayer、Kite 等）分别用什么技术和分发优势争夺 AgentFi 叙事？
4. AgentFi 落地需要哪些关键技术栈：agent 钱包、链上身份、账户抽象、Session Key / scoped permissions、支付通道、服务发现、信誉/结算、低延迟低 Gas、数据索引和安全审计？
5. 主流 agent 框架（elizaOS、Coinbase AgentKit、LangChain / Vercel AI SDK、Virtuals ACP SDK、Solana/Kite/Base agent tooling）与链上交互的模式有什么差异？
6. Mantle 作为 EVM-compatible L2，在账户抽象、Paymaster、MNT gas、EigenDA/模块化架构、mETH/cmETH/DeFi 流动性和 ZK roadmap 上有哪些优势？
7. Mantle 在 AgentFi 方向的真实挑战是什么：延迟/finality、gas token UX、CCTP/原生稳定币、agent 开发者入口、分发渠道、生态项目密度、安全责任、差异化叙事？
8. AgentFi 对 Mantle 的契合度应判断为强、中还是弱？若为中/有条件，短中长期分别应该讲什么、做什么、避免什么？

## Items

### item-1: 研究边界、术语定义与证据分级

建立 AgentFi 专项研究的可复核边界，避免把 AI meme 代币、agent framework、agent payment、账户抽象和专用链叙事混成一个不可检验的概念。

必须覆盖：

- 术语定义：AgentFi、AI agent token、agent launchpad、agent wallet、agentic commerce、agent-to-agent payment、DeFAI、autonomous onchain execution、human-in-the-loop agent；
- 范围纳入：链上 agent 资产发行、agent 钱包/交易、agent payment/API commerce、agent 间协作协议、agent framework 的 onchain plugin、面向 agent 的专用链或 L2；
- 范围排除：纯 Web2 agent SaaS、无链上结算的聊天机器人、只有 AI branding 的 meme token、不可核验的 Telegram/X bot 收益宣传；
- 市场阶段标签：`narrative/speculative`、`developer-tooling`、`early-product`、`usage-proven`、`production-infra`；
- 证据等级：`official-primary`、`official-docs`、`open-source-code`、`onchain-data`、`market-data`、`media-reported`、`internal-research`、`inferred`、`unverified`；
- 所有 volatile metrics 必须记录 `as_of_date`、`source_url`、`methodology`、`confidence`，不能把市场页面实时数字写成长期事实。

- **Priority**: high
- **Dependencies**: none

### item-2: 市场阶段与市场规模估算

判断 AgentFi 是否已经从概念验证进入可持续使用阶段，并用多个口径估算市场规模。结论必须区分"投机资产市值"和"真实 agent 经济活动"。

必须覆盖：

- 市场规模口径 1：CoinGecko / CoinMarketCap AI Agents category 市值、24h volume、Top tokens（例如 Virtuals、FET、Venice Token 等）以及 category 构成偏差；
- 市场规模口径 2：Virtuals Protocol、elizaOS/ai16z、Cookie.fun、DeFAI / agent token launchpad 的 token issuance、交易量、FDV、费用/收入；
- 市场规模口径 3：agent payment / API commerce 使用量，例如 x402 官网 last-30-days transactions/volume/buyers/sellers、Virtuals ACP usage、Solana/Kite/Tempo machine payment 数据；
- 市场规模口径 4：developer demand，例如 elizaOS GitHub stars/forks/releases、AgentKit docs/SDK adoption、Base/Solana/Kite agent docs 和 hackathon activity；
- 市场阶段判断：哪些是已上线 production-like payment rails，哪些只是 testnet、docs、hackathon 或 launchpad；
- 风险：AI agent token 市值高度波动，不能等同 TAM；agent 自动交易收益、agent wallet 数和 agent token holder 数需要防刷量/重复钱包处理。

起始快照：CoinGecko AI Agents category 页面在 2026-05-26 搜索结果中显示约 $3.71B market cap 与约 $519M 24h volume；deep draft 必须重新打开页面并记录实际访问日数值。

- **Priority**: high
- **Dependencies**: item-1

### item-3: 主要竞品格局：Solana、Base、Sui 与专用 Agent 链/协议

建立竞品地图，重点比较每条链或协议如何把 agent 钱包、支付、身份、低成本执行和开发者入口包装成 AgentFi 叙事。

必须覆盖：

- **Solana**：复用 `competitor-solana/final.md` 中 Solana Pay、Token Extensions、Solana Foundation `pay`、`mpp-sdk`、`x402-sdk`、`awesome-solana-ai`、`solana-dev-skill` 等 watchlist；评估其低延迟、低费、SVM、支付 UX 和 AI tooling 对 AgentFi 的适配性；
- **Base**：复用 `competitor-base/final.md` 中 Base AI Agents、x402、Base Account、AgentKit、Base Skills、Coinbase 分发、Flashblocks/low-latency UX；评估 Base 是否正在占据 EVM agent payment 默认入口；
- **Sui**：复用 `competitor-sui/final.md` 中 gasless stablecoin transfers、Address Balances、Walrus/Seal/MemWal、Sui Stack app infra；评估 Move/object model 对 agent-owned assets 和 policy guardrails 的叙事优势；
- **Virtuals Protocol**：Agent Commerce Protocol (ACP)、agent registry、agent tokenization、agent-to-agent coordination、ACP SDK 和 Base 生态关联；
- **AgentLayer / Kite / 其他专用 Agent 链**：AgentLayer OP Stack / AgentChain / AgentOS / AgentLink / AgentEx；Kite mainnet、Agent Passport、stablecoin settlement、EVM compatibility；标注官方声称与实际主网/生态证据的差距；
- **Tempo / Arc adjacent**：复用 payment-tempo 和 payment-ark 中 machine payments、Agentic Commerce、ERC-8183 / nanopayments、stablecoin gas、Payment Lane，作为支付链对 AgentFi 的旁证；
- 输出竞品矩阵：chain/protocol、AgentFi 主张、技术栈、分发渠道、使用证据、Mantle 压力、caveat。

- **Priority**: high
- **Dependencies**: item-1, item-2

### item-4: Agent 钱包、链上身份与账户抽象 / Session Key

拆解 AgentFi 能否安全落地的核心钱包和权限问题。Agent 不能简单持有热钱包私钥；需要限定额度、时间、合约、函数和回滚/恢复策略。

必须覆盖：

- ERC-4337：UserOperation、EntryPoint、bundler、paymaster、factory、signature validation、ERC-20 gas / sponsored gas 对 agent onboarding 的价值；
- EIP-7702：EOA set-code / delegated smart account 对现有钱包用户和 agent delegation 的意义；必须标注其安全边界和钱包支持成熟度；
- ERC-7579 / modular smart accounts：validator、executor、hook、fallback handler 等模块化账户能力如何支持 agent policy；
- ERC-7715 / wallet permission request、session key / scoped permission、spending limits、time windows、method allowlists、onchain/offchain policy engine；
- Base Account / Coinbase CDP Wallet / AgentKit、Safe / Rhinestone / Biconomy / Privy 等 EVM account stack 作为实现起点；
- Solana / Sui 的不同路径：Solana relayer、keypair/session authority、Sui sponsored/gasless transaction 和 object-level permission 的可比性；
- 安全模型：prompt injection、tool-call hijack、private-key leakage、policy bypass、malicious API response、replay/cross-chain replay、unbounded approval、agent collusion；
- Mantle 适配问题：Mantle 是否已有成熟 bundler/paymaster/RPC/account SDK 生态；若没有，哪些能力可通过第三方 AA providers 补齐。

- **Priority**: high
- **Dependencies**: item-3

### item-5: 低延迟、低 Gas 与执行环境需求

分析 AgentFi 对链性能的真实要求。研究必须把"agent 高频行为"拆成读链、模拟、签名、提交、结算、回滚和对账，不得只比较 TPS。

必须覆盖：

- 工作负载类型：API micro-payment、agent-to-agent service escrow、DeFAI rebalancing、NFT/game agent actions、social/token agent launchpad、MEV-sensitive trading bot、long-running workflow settlement；
- 延迟需求：人类交互级、API request/response 级、交易/套利级、异步任务结算级分别需要什么 confirmation / finality；
- Gas 需求：单笔微支付、批量支付、approval/session refresh、service escrow、multi-call、rebalancing 的成本敏感度；
- Base/Solana/Sui/Tempo/Kite 的性能叙事如何与 AgentFi 场景对应：Flashblocks、Solana low-latency finality roadmap、Sui gasless stablecoin、Tempo Payment Lane、Kite deterministic finality；
- Mantle v2 费用机制：MNT gas、L2 execution fee、L1 rollup fee、EigenDA/DA savings、private tx pool、priority fee 和 EIP-1559 support；
- 指标要求：平均/尾延迟、success rate、failed tx cost、reorg/finality assumptions、RPC rate limit、indexer freshness、gas sponsorship cost、batching savings；
- 结论必须说明：AgentFi 不一定要求最高 TPS，但要求可预测费用、可控权限、快速模拟、可靠 RPC/indexing 和清晰 finality UX。

- **Priority**: high
- **Dependencies**: item-3, item-4

### item-6: Agent 间协作协议、支付通道与服务发现

研究 AgentFi 是否存在可复用的协议层，而不是每个 agent app 自建私有 marketplace。

必须覆盖：

- Virtuals ACP：agent registry、service offering、job discovery、escrow/settlement、reputation、agent-to-agent negotiation、ACP SDK 和 current status；
- x402：HTTP 402 payment challenge、stablecoin per-request payment、API access without API keys、supported networks/tokens、Base/Coinbase ecosystem role、usage metrics；
- Machine Payments Protocol / Solana Foundation `mpp-*` / Tempo MPP：机器支付与稳定币结算的设计，是否是 x402 竞争/互补；
- ERC-8183 / agentic commerce 标准：任务范围、funds escrow、deliverables、result parsing 的适用性和成熟度；
- payment channel / streaming payment / state channel / account-based escrow：哪些场景需要链下通道，哪些可直接 L2 settlement；
- agent identity / reputation：DID、attestation、Agent Passport、onchain registry、credential revocation、slashing/deposit；
- Mantle 机会：是否可优先支持 x402/ACP settlement、创建 Mantle agent registry 或 agent payment SDK，而非先做新协议。

- **Priority**: high
- **Dependencies**: item-4, item-5

### item-7: 主流 Agent 框架与链上交互模式

梳理 agent 开发者实际使用的框架和链上插件路径，判断 Mantle 要争取的开发者入口在哪里。

必须覆盖：

- **elizaOS**：TypeScript agent framework、CLI、plugins、memory、actions/providers/services/evaluators、Ethereum/Solana plugins、agent runtime 与安全限制；
- **Coinbase AgentKit / CDP SDK**：wallet management、onchain actions、payments/x402、paymaster、multi-network support、Base/Solana support；
- **LangChain / Vercel AI SDK / OpenAI tools / MCP**：通用 agent 编排框架如何通过 wallet provider、tool calling、MCP server 访问链上能力；
- **Virtuals ACP SDK**：framework-agnostic ACP SDK 如何连接 agent registry / task / escrow；
- **Solana/Kite/Base agent docs**：官方 agent guide、skills、wallet setup、identity registration、paid API request、trading agent demo；
- onchain 交互模式分类：read-only analytics、intent simulation、human-approved execution、delegated scoped execution、fully autonomous signing、multi-agent workflow；
- 输出 developer entry map：框架、语言、链支持、钱包模型、支付模型、安全模型、Mantle 接入成本。

- **Priority**: high
- **Dependencies**: item-3, item-6

### item-8: Mantle 适配性评估：优势、可落地能力与路线

把前述市场和技术分析落到 Mantle。结论必须区分"已有优势"、"可快速补齐"、"中期需工程投入"、"不适合直接做"。

必须覆盖：

- Mantle 已有优势：EVM/OP Stack compatibility、Solidity 工具链、Ethereum settlement、ZK validity roadmap、模块化架构、EigenDA/DA 成本优势、MNT gas、mETH/cmETH/yield-bearing 生态、Bybit/Mirana/treasury/liquidity resources；
- 账户抽象适配：ERC-4337/7702/7579/7715 在 Mantle 上的可行性，第三方 bundler/paymaster/wallet provider 支持情况，是否需要 Mantle 官方 SDK/docs；
- 支付与稳定币适配：MNT gas UX、stablecoin paymaster、USDC/CCTP/native stablecoin 状态、USDT0/AUSD/USDy/USDe 等 Mantle 稳定币和收益资产可作为 agent settlement / treasury assets 的可能性；
- 执行与成本：Mantle v2 fee model、EigenDA 成本节省、private tx pool、priority fee、RPC/indexer readiness 对 agent 高频任务的影响；
- 生态叙事：Mantle 可以定位为 "EVM AgentFi settlement + yield/liquidity layer"，而不是与 Solana/Base/Kite 正面争夺全部 agent framework 心智；
- 短期路线：x402/ACP compatible demo、agent wallet + spend limit + paymaster SDK、agent treasury/rebalancing demo、developer docs/skill pack；
- 中期路线：官方 AA/paymaster stack、agent registry / reputation PoC、stablecoin gas abstraction、DeFAI strategy vaults、indexer/RPC SLA；
- 长期路线：AgentFi-specific L3/appchain、privacy/TEE/ZK policy proof、cross-agent payment channel、institutional agent settlement。

- **Priority**: high
- **Dependencies**: item-4, item-5, item-6, item-7

### item-9: Mantle 挑战、不可照搬边界与差异化空间

明确 Mantle 做 AgentFi 的风险与约束，避免内部分享给出过强结论。

必须覆盖：

- 对 Base 的挑战：Coinbase 分发、Base Account、AgentKit/x402、AI Agents docs、Base Skills 形成强入口；Mantle 很难复制 Coinbase consumer/developer funnel；
- 对 Solana 的挑战：低延迟、低费、Solana Pay、Foundation agent payment repos、SVM 原生性能叙事；Mantle 不应直接拼单体 L1 TPS；
- 对 Sui/Kite/Tempo 的挑战：gasless stablecoin、Agent Passport、Payment Lane、stablecoin-native agent commerce；Mantle 需要用 paymaster 和 yield/liquidity 弥补协议层支付原语不足；
- 对专用 Agent 链的挑战：AgentLayer/Kite/Virtuals 等可把 registry、identity、marketplace、token launchpad 集成到默认产品；Mantle 若只提供通用执行层，叙事不够尖锐；
- 工程挑战：AA provider coverage、paymaster economics、RPC/indexer freshness、finality UX、MEV/private order flow、security review、agent policy debugging、fraud/chargeback/legal liability；
- 生态挑战：缺少旗舰 AgentFi 应用、缺少官方 agent SDK/skills、缺少 developer relations 包装、稳定币/CCTP/merchant/API partner 证据不足；
- 差异化空间：EVM neutral settlement、mETH/cmETH/yield assets、DeFi liquidity、treasury incentives、institution-ready rollup/ZK roadmap、agent treasury and portfolio management、cross-chain EVM agent operations。

- **Priority**: high
- **Dependencies**: item-8

### item-10: 最终评估表、契合度判断与行动建议

整合所有发现，输出内部分享可直接引用的评估表和判断。

必须覆盖：

- 必填评估表：市场阶段、市场规模、主要竞品、关键技术、Mantle 优势、Mantle 挑战、契合度判断；
- 契合度规则：强=市场已验证且 Mantle 有独特优势；中=叙事有热度且 Mantle 可切入但需补产品/生态；弱=市场未验证或 Mantle 无明显差异；
- 建议初始假设：AgentFi 对 Mantle 更可能是 "中等契合/可选叙事"，除非 deep draft 找到 Mantle 已有强 AgentFi 项目或数据；
- 内部分享表达：一句话判断、3 个 proof points、3 个 caveats、竞品对照措辞；
- 行动建议分层：0-1 月可做 demo/docs、1-2 季度可做 SDK/paymaster/partner、长期战略观察；
- 不建议：不应把 AgentFi 写成 Mantle 主叙事，除非市场数据和生态证据显著强于支付/RWA/enterprise/privacy 等备选方向。

- **Priority**: high
- **Dependencies**: all

### item-11: 风险、开放问题与事实核验清单

为 adversarial review 和 deep draft 留出明确检查点。

必须覆盖：

- 数据口径：AI agent category 是否包含非 agent 项目，Virtuals/agent token 是否重复计入，FDV 与 circulating market cap 如何处理；
- 使用证据：x402/ACP transaction 是否代表真实付费 API/agent commerce，还是测试/空投/刷量；
- 自动化程度：agent 是否真正 autonomous，还是 human-in-the-loop bot；所有"agent executed trade/payment"案例需说明人工审批边界；
- 安全责任：agent wallet 造成损失时的责任归属、policy guardrail 是否可审计、session key 是否可撤销；
- 链上身份与隐私：agent reputation 是否抗 sybil，是否泄露商业策略或用户数据；
- Mantle source gap：需核验 Mantle 当前官方 docs、AA/paymaster provider、stablecoin/native asset 状态、RPC/indexer SLA、生态 AgentFi 项目；
- 所有核心结论必须标注 confidence，低证据叙事不得写成事实。

- **Priority**: high
- **Dependencies**: all

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| market_segment | AI agent token、agent launchpad、agent payment/API commerce、DeFAI、agent infra、dedicated agent chain | item-2, item-3 |
| market_metric | market_cap、FDV、24h_volume、protocol_revenue、fees、transactions、active_agents、buyers/sellers、GitHub stars/forks/releases | item-2 |
| as_of_date | 市场或链上数据的访问/统计日期 | item-2, item-3, item-5 |
| competitor | Solana、Base、Sui、Virtuals、AgentLayer、Kite、Tempo、Arc、其他相关项目 | item-3 |
| chain_or_protocol_role | settlement chain、agent launchpad、payment protocol、identity registry、agent framework、wallet/paymaster provider | item-3, item-6, item-7 |
| agent_wallet_model | EOA hot wallet、smart account、MPC/custodial wallet、session key、scoped permission、sponsored/gasless transaction | item-4 |
| permission_scope | amount limit、token allowlist、contract/function allowlist、time window、rate limit、human approval、kill switch/revocation | item-4 |
| payment_protocol | x402、ACP、MPP、ERC-8183、payment channel、escrow、streaming payment、direct transfer | item-6 |
| agent_framework | elizaOS、Coinbase AgentKit、LangChain、Vercel AI SDK、Virtuals ACP SDK、Solana/Kite/Base agent tooling | item-7 |
| onchain_interaction_mode | read-only、simulation、human-approved execution、delegated execution、autonomous signing、multi-agent workflow | item-7 |
| mantle_advantage | EVM compatibility、AA/paymaster、EigenDA/low cost、ZK roadmap、mETH/cmETH/yield、MNT incentives、liquidity/treasury | item-8 |
| mantle_challenge | latency/finality、gas UX、AA ecosystem gap、stablecoin/CCTP gap、developer distribution、security/liability、ecosystem depth | item-9 |
| evidence_level | official-primary、official-docs、open-source-code、onchain-data、market-data、media-reported、internal-research、inferred、unverified | all |
| confidence | high / medium / low，必须解释影响结论的限制 | all |
| caveat | 数据口径、时间敏感性、实现成熟度、不可外推边界、未验证合作/使用量 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | required_table | AgentFi 最终评估表：市场阶段、市场规模、主要竞品、关键技术、Mantle 优势、Mantle 挑战、契合度判断 | markdown table | item-10 |
| diag-2 | market_map | AgentFi 市场分层图：投机资产/launchpad、agent payment、wallet/identity、agent framework、dedicated chain、DeFAI apps | mermaid flowchart 或 markdown table | item-2 |
| diag-3 | competitor_matrix | Solana/Base/Sui/Virtuals/AgentLayer/Kite/Tempo/Arc vs 技术能力、分发、使用证据、Mantle 压力 | markdown table | item-3 |
| diag-4 | architecture | AgentFi 技术栈架构图：agent runtime -> wallet/permissions -> payment/settlement -> identity/reputation -> data/indexing -> app protocols | mermaid flowchart | item-4, item-5, item-6, item-7 |
| diag-5 | wallet_flow | Agent 钱包执行流程：policy grant/session key -> simulation -> paymaster/gas -> transaction -> monitoring/revocation | mermaid sequenceDiagram | item-4 |
| diag-6 | payment_flow | x402/ACP/MPP payment flow 对比：HTTP 402 / service discovery / escrow / stablecoin settlement / receipt | markdown table 或 mermaid sequenceDiagram | item-6 |
| diag-7 | mantle_fit_matrix | Mantle AgentFi 适配矩阵：能力、当前状态、竞品差距、补齐方式、时间线、风险 | markdown table | item-8, item-9 |
| diag-8 | roadmap | Mantle 行动路线图：0-1 月 demo/docs，1-2 季度 SDK/paymaster/partners，长期 L3/privacy/channel | mermaid gantt 或 markdown table | item-10 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | market_data | CoinGecko/CoinMarketCap AI Agents category、Virtuals token/market pages、Cookie.fun 或同类 agent data dashboard，记录访问日和口径 | 5 |
| src-2 | official_protocol_docs | Virtuals ACP、x402、AgentLayer、Kite、Tempo MPP、ERC-8183 或相关 agent commerce docs | 8 |
| src-3 | ethereum_standards | ERC-4337、EIP-7702、ERC-7579、ERC-7715、EIP-712、相关 wallet permission/session key specs | 5 |
| src-4 | agent_framework_docs | elizaOS、Coinbase AgentKit/CDP、Base AI Agents、LangChain/Vercel AI SDK/MCP、Virtuals ACP SDK、Solana agent tooling | 8 |
| src-5 | chain_official_docs | Mantle、Base、Solana、Sui、Kite/AgentLayer 官方文档中与 agent/payment/wallet/fee/finality 相关页面 | 10 |
| src-6 | internal_research | 本仓库 sibling final sections：Solana、Base、Sui、Tempo、Arc、narrative-analysis；仅作为已审背景 | 6 |
| src-7 | onchain_or_usage_data | x402 stats、Virtuals/ACP usage、Dune/DefiLlama/TokenTerminal/Artemis/Mantle explorer/API 数据，至少覆盖 3 个使用维度 | 5 |
| src-8 | security_sources | Agent wallet / prompt injection / scoped permissions / account abstraction security analysis、audits、incident reports | 4 |
| src-9 | mantle_sources | Mantle official docs、Mantle website、Mantle explorer/dashboard、AA/paymaster provider docs、stablecoin/native asset docs | 6 |
| src-10 | media_context | 主流 crypto 媒体或 research reports 对 AgentFi/AI agents/agentic commerce 的阶段判断；不得替代 primary source | 5 |

## Evidence Starting Points

### Market and Data

- CoinGecko AI Agents category: `https://www.coingecko.com/en/categories/ai-agents`
- CoinMarketCap AI Agents category: `https://coinmarketcap.com/view/ai-agents`
- Cookie.fun / Cookie DAO AI agent data: `https://dao.cookie.fun/`
- DefiLlama protocols / fees pages for Virtuals and related projects: `https://defillama.com/`
- x402 usage page: `https://www.x402.org/`

### Agent Protocols and Dedicated Agent Chains

- Virtuals Protocol website: `https://www.virtuals.io/`
- Virtuals ACP whitepaper/docs: `https://whitepaper.virtuals.io/get-started-with-acp`
- Virtuals ACP current status: `https://whitepaper.virtuals.io/about-virtuals/agent-commerce-protocol/current-status`
- Virtuals ACP technical deep dive: `https://whitepaper.virtuals.io/about-virtuals/agent-commerce-protocol/technical-deep-dive`
- AgentLayer whitepaper: `https://whitepaper.agentlayer.xyz/`
- AgentLayer website whitepaper: `https://agentlayer.xyz/whitepaper`
- Kite website: `https://gokite.ai/`
- Kite docs/tokenomics: `https://docs.gokite.ai/get-started-why-kite/tokenomics`

### Wallets, AA, Permissions and Payment Standards

- ERC-4337: `https://eips.ethereum.org/EIPS/eip-4337`
- EIP-7702: `https://eips.ethereum.org/EIPS/eip-7702`
- ERC-7579: `https://eips.ethereum.org/EIPS/eip-7579`
- ERC-7715: `https://eips.ethereum.org/EIPS/eip-7715`
- x402 docs: `https://docs.x402.org/`
- Coinbase AgentKit docs: `https://docs.cdp.coinbase.com/agent-kit/welcome`
- Base AI Agents docs: `https://docs.base.org/ai-agents/index`

### Agent Frameworks

- elizaOS docs: `https://docs.elizaos.ai/`
- elizaOS GitHub: `https://github.com/elizaos/eliza`
- Coinbase AgentKit GitHub from docs: `https://github.com/coinbase/agentkit`
- LangChain agents docs: `https://docs.langchain.com/`
- Vercel AI SDK docs: `https://ai-sdk.dev/docs`
- MCP specification: `https://modelcontextprotocol.io/`

### Mantle and Internal Research

- Mantle website: `https://www.mantle.xyz/`
- Mantle Network docs overview: `https://docs.mantle.xyz/network`
- Mantle architecture: `https://docs.mantle.xyz/network/system-information/architecture`
- Mantle fee mechanism: `https://docs.mantle.xyz/network/system-information/fee-mechanism`
- Mantle vs OP Stack / Ethereum differences: `https://docs.mantle.xyz/network/for-developers/the-differences-between-mantle-op-stack-and-ethereum`
- Existing Solana final: `202606-internal-sharing/research-sections/competitor-solana/final.md`
- Existing Base final: `202606-internal-sharing/research-sections/competitor-base/final.md`
- Existing Sui final: `202606-internal-sharing/research-sections/competitor-sui/final.md`
- Existing Tempo final: `202606-internal-sharing/research-sections/payment-tempo/final.md`
- Existing Arc final: `202606-internal-sharing/research-sections/payment-ark/final.md`
- Existing narrative analysis final: `202606-internal-sharing/research-sections/narrative-analysis/final.md`

## Draft Structure Recommendation

1. Executive summary：一句话判断 AgentFi 对 Mantle 的契合度，列 3 个机会和 3 个 caveats。
2. 方法与定义：市场阶段、证据等级、数据口径、AgentFi 范围。
3. 市场阶段与规模：AI agent category、Virtuals/agent launchpad、x402/ACP/payment usage、developer activity。
4. 竞品格局：Solana、Base、Sui、Virtuals、AgentLayer、Kite、Tempo/Arc adjacent。
5. 关键技术栈：agent 钱包/身份/AA/session key、低延迟低 Gas、agent 协作协议、支付通道、framework/tooling。
6. Mantle 适配性：优势、当前缺口、可快速补齐能力、中长期投入。
7. Mantle 差异化与风险：对 Base/Solana/Sui/Kite 等竞品的差异化表达和不可照搬边界。
8. 必填评估表：市场阶段、市场规模、主要竞品、关键技术、Mantle 优势、Mantle 挑战、契合度判断。
9. 行动建议：0-1 月、1-2 季度、长期路线；每项标注工程复杂度和证据需求。
10. Source appendix：列出所有 source、访问日期、confidence、volatile metric caveat。

## Quality Checklist

- [ ] 必填评估表完整填写，且每个结论有 source/confidence/caveat。
- [ ] 市场规模同时区分 token 市值、协议/支付 usage、developer activity，不把市值当成真实使用。
- [ ] Solana/Base/Sui/Virtuals/AgentLayer/Kite 的竞品判断均使用 primary source 或已审 sibling research。
- [ ] 账户抽象部分覆盖 ERC-4337、EIP-7702、ERC-7579、ERC-7715/session permission，并解释 Mantle 可用性。
- [ ] Agent wallet 安全风险（prompt injection、key leakage、policy bypass、revocation）单独成节，不只是附带说明。
- [ ] x402、ACP、MPP、ERC-8183 等协议状态必须标注 production/testnet/docs/hackathon/experimental。
- [ ] Mantle 优势和挑战分开写，避免只列优势；所有 Mantle-specific claims 使用 Mantle 官方 docs 或可核验 provider/source。
- [ ] 契合度判断应保守：若证据主要是叙事和 market cap，默认不应给 "强"。
- [ ] 不新增 `_index.md`，不写 final.md；outline 仅作为 Phase A artifact。

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | created | full outline | Initial structured outline for AgentFi narrative technical analysis dispatch | Orchestrator dispatch `11f230a3-8da3-46a3-9f18-2021910d0b2d` |
