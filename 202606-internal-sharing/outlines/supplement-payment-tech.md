---
topic: "Payment Chain 技术架构补充调研（Tempo / Circle Arc）"
project_slug: 202606-internal-sharing
topic_slug: supplement-payment-tech
github_repo: Whisker17/multica-research
round: 1
status: candidate

artifact_paths:
  outline: 202606-internal-sharing/outlines/supplement-payment-tech.md
  draft: 202606-internal-sharing/research-sections/supplement-payment-tech/drafts/round-{n}.md
  final: 202606-internal-sharing/research-sections/supplement-payment-tech/final.md
  supplementary_output: 202606-internal-sharing/report/assets/supplementary/payment-chain-tech-supplement.md
  index: 202606-internal-sharing/research-sections/_index.md

scope: |
  面向 Slides Outline Chapter 3 Section 3.2（Payment Chain 方向）的技术架构补充材料。
  从既有 payment-tempo/final.md、payment-ark/final.md 和 narrative-payment/final.md 中
  提炼架构要点，增加跨项目技术对比和 Mantle Gap 分析。
  四个核心模块：
  1. Payment Chain 技术要求分析（终局性/延迟/稳定币原生支持/跨链/合规/商户接入，与通用 L2 的本质差异）
  2. Tempo 支付链架构深度分析（Payment Lane、BFT ~600ms 终局性、Enterprise Zones、稳定币 Gas、关键代码设计选择）
  3. Circle Arc 支付链架构深度分析（Malachite BFT、CCTP V2、StableFX、USDC Gas、100+ 机构测试网）
  4. 与 Mantle 的 Gap 分析（OP Stack 与 Payment Chain 要求的架构差距，可复用 vs 需新建）

audience: |
  Mantle 工程团队 20260605 bi-weekly 全公司分享的准备者、协议工程师、BD/生态合作团队。
  读者已通过 slides 了解支付方向战略，需要看到更深层的技术架构对比和工程差距分析。
  本补充材料面向"知道要做 Payment Chain 方向，需要理解具体技术差距和参考路径"的读者。

expected_output: |
  - 产出路径: 202606-internal-sharing/report/assets/supplementary/payment-chain-tech-supplement.md
  - 格式: 中文 Markdown，结构化章节，关键架构用文字描述或 Mermaid 图
  - 长度: ~2000-3000 字
  - 关键约束: 深度聚焦架构和技术实现，避免重复既有 sections 中的产品/商业分析
  - 注意: 这是补充材料，不需要完整的 executive summary 和 source coverage；
    但必须准确引用既有 sections 中的关键技术结论，并标注来源

source_requirements_summary: |
  本 supplement 主要从已有研究 sections 中提炼和综合，不要求大量新的 primary source research。
  既有 sections 已包含 code-level 分析和 primary source 验证。
  如果需要补充新信息（如最新公开的 Tempo 代码变更或 Arc 主网进展），则使用 web search 验证。
  必须显式引用既有 sections 路径作为 traceability。

prerequisite_sections:
  - slug: payment-tempo
    path: 202606-internal-sharing/research-sections/payment-tempo/final.md
    status: final
  - slug: payment-ark
    path: 202606-internal-sharing/research-sections/payment-ark/final.md
    status: final
  - slug: narrative-payment
    path: 202606-internal-sharing/research-sections/narrative-payment/final.md
    status: final

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-27T13:15:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-27T13:15:00+08:00"
---

# Research Outline: Payment Chain 技术架构补充调研（Tempo / Circle Arc）

## Research Questions

1. 做 Payment Chain 需要底层链提供哪些通用 L2 不具备的核心能力？这些能力的技术实现路径是什么？
2. Tempo 和 Arc 分别用什么架构设计来满足 Payment Chain 的技术要求？关键设计选择的取舍是什么？
3. 当前 Mantle OP Stack 架构与 Payment Chain 技术要求之间存在哪些结构性差距？哪些可以在现有架构上补齐，哪些需要根本性改造？

## Items

### item-1: Payment Chain 核心技术要求与通用 L2 差异分析

建立 Payment Chain 的技术能力框架，为后续 Tempo/Arc 架构分析和 Mantle Gap 分析提供统一评估基准。

必须覆盖：

- **终局性要求**：支付场景对"资金状态不可重组"的时间要求（亚秒 ~ 秒级 BFT 确定性终局 vs L2 soft confirmation + L1 finality），以及不同支付子场景（POS、商户结算、B2B）对终局性的差异化要求；
- **交易费用确定性**：支付交易需要费用可预测、以稳定币计价、对用户透明或不可见；与通用链 gas token 波动和 gas 竞价的根本矛盾；
- **支付专用 blockspace**：为什么通用链无法保证支付交易的 SLA（拥堵时支付被 DeFi/NFT 挤出）；Payment Lane / gas budget 隔离的技术原理；
- **稳定币原生支持**：协议级稳定币标准 vs 应用层 ERC-20 的差异——memo、合规策略、fee eligibility、Payment Lane 分类；
- **跨链互操作**：支付资金需要跨链流动——burn-and-mint（CCTP）vs lock-and-mint vs bridge 的安全/延迟/UX 取舍；
- **合规基础设施**：链级 transfer policy（whitelist/blacklist/compound）vs 应用层合约级合规的差异；
- **六维能力框架表**：终局性、费用确定性、支付专用 blockspace、稳定币原生支持、跨链、合规——标注"通用 L2 默认不具备"vs"可通过改造补齐"vs"需要架构级变更"。

- **Priority**: high
- **Dependencies**: none

### item-2: Tempo 支付链架构深度分析

从技术架构角度深度分析 Tempo 如何满足 item-1 定义的 Payment Chain 能力框架。

必须覆盖：

- **Commonware Simplex BFT 共识**：双进程架构（Reth devp2p + Commonware P2P）、BLS12-381 门限签名、VRF leader、~600ms 确定性终局的机制原理、与 Tempo 支付延迟承诺的关系；标注性能数据的验证状态（测试网 vs 主网）；
- **Payment Lane 设计原理**：三条 lane（System/Payment/General）的 gas budget 分区、`general_gas_limit` / `shared_gas_limit` 的工作机制、v1/v2 支付分类规则的演进（v1: TIP-20 地址前缀共识层检查；v2/TIP-1045: selector allow-list + 空 access list + bounded key auth）、拥堵时 `ExceedsNonPaymentLimit` 的跳过逻辑；
- **稳定币 Gas 实现**：无原生 gas token、attodollars 计价、`TEMPO_T1_BASE_FEE = 20_000_000_000` attodollars/gas、TIP-20 transfer ~$0.001、Fee AMM/StablecoinDEX 在跨稳定币费用支付中的作用；
- **TIP-20/TIP-403 协议级稳定币原语**：预编译实现而非 ERC-20 合约、固定 6 位小数/memo/pause/role-based access、TIP-403 双边合规策略注册表、对 Payment Lane 分类和 fee eligibility 的耦合；
- **Enterprise Zones 架构**：Reth validium、ZonePortal/ZoneFactory、authenticated RPC、encrypted deposit、单 sequencer 信任模型、proof slot 存在但 proof bytes 为空的成熟度限制；
- **关键代码设计选择**：TempoTxEnvelope 自定义交易类型（batching/sponsor/P256/WebAuthn/validity window/二维 nonce）、TempoHeader 毫秒级 timestamp、TempoChainSpec T0-T5 硬分叉、Reth SDK 深度 fork（26+ crates, 依赖 paradigmxyz/reth@1be17eb）；
- **Tempo 对 item-1 六维能力框架的覆盖评估**。

数据来源：综合 `payment-tempo/final.md` item-2 到 item-6 的代码级分析结论。如本地 Tempo 代码库（`/Users/whisker/Work/src/networks/tempo`）可用则做增量验证。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Circle Arc 支付链架构深度分析

从技术架构角度深度分析 Arc 如何满足 item-1 定义的 Payment Chain 能力框架。

必须覆盖：

- **Malachite BFT 共识引擎**：Informal Systems 开发 / Circle 接管、Tendermint 衍生 Rust 实现、双进程架构（共识与执行独立进程通过 Engine API 通信）、区块引用传播（共识层只处理紧凑引用不处理完整 payload）、~780ms 终局（100 验证者）/ 330-490ms（小网络）的基准数据——标注为测试网数据；
- **USDC Gas 模型**：USDC 作为原生 Gas 代币、指数加权移动平均（EWMA）费用平滑、bounded base fee、Paymaster 多币种支持（EURC 等自动兑换 USDC）、与 Tempo attodollars 固定费模型的设计取舍对比；
- **CCTP V2 跨链协议升级**：从 V1 到 V2 的架构改进、原生 burn-and-mint 机制、26 个支持区块链/域、$126B 累计转账量、Arc 上 USDC 为原生发行（非桥接）的结构性优势——这是任何第三方链无法复制的；
- **StableFX 跨币种汇兑**：RFQ 执行模式（多流动性供应商报价）、原子化链上结算（payment vs delivery atomicity）、24/7 可编程结算窗口、all-to-all 模型、8 Partner Stablecoins 的多币种支持；
- **可选隐私控制**：selectively shielded balances、TEE 可信执行环境、view keys 审计、opt-in 设计——与 Tempo Zones 独立执行环境方案的设计差异；
- **100+ 机构测试网架构支撑**：PoA 渐进式去中心化路线、验证者选择标准（运营稳定性/地理多样性/监管合规）、双层安全模型（身份层 + 经济层）；
- **Arc 对 item-1 六维能力框架的覆盖评估**。

数据来源：综合 `payment-ark/final.md` item-2 到 item-7 的分析结论，白皮书直接解析的 primary claims。

- **Priority**: high
- **Dependencies**: item-1

### item-4: 与 Mantle 的 Gap 分析

以 item-1 的六维能力框架为基准，对比 Mantle 当前 OP Stack 架构与 Payment Chain 要求的结构性差距，区分"可在现有架构上补齐"和"需要架构级改造"。

必须覆盖：

- **终局性 Gap**：Mantle L2 soft confirmation（sequencer 签名，秒级 UX）vs Tempo/Arc BFT 确定性终局（~600ms/~780ms）；L2 soft confirmation 不等于资金不可重组；preconf / sequencer slashing 作为中间路径的技术可行性和限制；
- **费用确定性 Gap**：MNT 作为原生 gas token 的价格波动 vs USDC/attodollars 稳定币计价；Paymaster/AA 可在应用层实现稳定币 Gas UX 但不改变协议层 gas 计价；
- **支付 blockspace Gap**：OP Stack 无协议级 Payment Lane；可行中间方案——priority RPC、trusted payment relayer、sequencer policy soft reservation；完整 gas budget 隔离需要 txpool/payload builder 改造，进入 OP Stack/op-geth 改造区；
- **稳定币原生支持 Gap**：Mantle 上 USDC 为桥接资产（Circle primary docs 未列 Mantle 为 CCTP/native USDC 支持链）；ERC-20 缺少协议级 memo/合规策略/fee eligibility；可通过 system contract/predeploy 补齐部分能力但与 TIP-20/原生发行的差距是结构性的；
- **跨链 Gap**：无 CCTP 原生支持；依赖第三方桥（LayerZero/Relay 等）；推动 Circle 将 Mantle 纳入 CCTP 需要合作而非纯工程；
- **合规 Gap**：无链级 transfer policy 注册表；可通过 Solidity predeploy 实现 TIP-403 风格策略但执行保证弱于预编译级；
- **可复用 vs 需新建矩阵**：对每个能力维度标注"Mantle 当前状态"、"短期可补齐（应用/SDK 层）"、"中期需改造（system contract/sequencer）"、"长期需架构变更（客户端/共识）"。

数据来源：综合 `narrative-payment/final.md` item-4 到 item-8 的 Mantle 适配性评估，以及 `payment-tempo/final.md` item-8 和 `payment-ark/final.md` item-7 的 Mantle 路线建议。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| capability_dimension | Payment Chain 六维能力：终局性、费用确定性、支付 blockspace、稳定币原生支持、跨链、合规 | all |
| tempo_implementation | Tempo 对该能力的实现方式和关键代码/设计选择 | item-2 |
| arc_implementation | Arc 对该能力的实现方式和关键设计选择 | item-3 |
| mantle_gap | Mantle 当前状态与目标能力的差距描述 | item-4 |
| remediation_tier | 差距补齐层级：应用/SDK（0-3月）、system contract/sequencer（3-9月）、架构级（9-18月+） | item-4 |
| evidence_confidence | 证据置信度：verified-primary、verified-code、existing-research、inferred | all |
| source_section | 引用的既有 section 路径和 item 编号 | all |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | architecture | Payment Chain 六维能力框架图：终局性/费用确定性/支付 blockspace/稳定币原生/跨链/合规，每维度标注 Tempo/Arc/Mantle 的实现层级 | mermaid flowchart 或 markdown table | item-1, item-4 |
| diag-2 | comparison | Tempo vs Arc 技术架构对比图：共识层/执行层/支付原语/跨链/隐私/Gas 模型并排对比 | markdown table | item-2, item-3 |
| diag-3 | gap-matrix | Mantle Gap 分析矩阵：六维能力 x 当前状态/短期可补/中期改造/长期架构变更 | markdown table | item-4 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | existing_research | payment-tempo/final.md 中的技术架构分析（item-2 到 item-6） | 1 |
| src-2 | existing_research | payment-ark/final.md 中的技术架构分析（item-2 到 item-3） | 1 |
| src-3 | existing_research | narrative-payment/final.md 中的 Mantle 适配性评估（item-4 到 item-8） | 1 |
| src-4 | official_docs | Tempo/Arc 官方文档或公告，仅在需要补充既有 sections 未覆盖的新信息时使用 | 0（optional） |

## Draft Structure Recommendation

1. **引言**（~200 字）：本补充材料的定位和阅读方式——面向 Slides 15 的技术架构深度支撑。
2. **Payment Chain 技术要求框架**（~400 字）：六维能力分析，建立评估基准。
3. **Tempo 技术架构要点**（~600-800 字）：聚焦 Commonware BFT + Payment Lane + 稳定币 Gas + TIP-20/TIP-403 + Zones 的架构设计和关键代码选择。
4. **Arc 技术架构要点**（~600-800 字）：聚焦 Malachite BFT + USDC Gas + CCTP V2 + StableFX + 可选隐私 + 验证者模型的架构设计。
5. **Mantle Gap 分析**（~500-600 字）：六维能力差距矩阵、可复用部分和需新建部分、分层路线建议。
6. **来源引用**（~100 字）：标注本 supplement 引用的既有 section 路径。

## Quality Checklist

- [ ] 所有技术结论可追溯到既有 sections 的具体 item 编号
- [ ] 不重复既有 sections 的产品/商业/生态分析，聚焦架构和技术实现
- [ ] 六维能力框架在 item-1 定义后一致贯穿 item-2/3/4
- [ ] Mantle Gap 分析区分"可补齐"和"结构性差距"，不过度乐观也不过度悲观
- [ ] 长度控制在 ~2000-3000 字
- [ ] 包含至少 2 张结构化对比表（技术对比 + Gap 矩阵）
- [ ] 对易过期事实标注验证日期和来源 section

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | create | full outline | Initial outline from Orchestrator dispatch for supplement-payment-tech | Multica issue 5e2e8d68-49d7-491e-b2d8-8e458c7633e9 comment 48b4ed9c-e4dd-4fd1-b16b-608672932a93 |
