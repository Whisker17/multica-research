---
topic: "X Layer 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-xlayer"
github_repo: "Whisker17/multica-research"
round: 1
status: candidate

artifact_paths:
  outline: "202606-internal-sharing/outlines/competitor-xlayer.md"
  draft: "202606-internal-sharing/research-sections/competitor-xlayer/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/competitor-xlayer/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: "分析 X Layer（OKX 旗下 L2）的近期开发活动与叙事方向变化。涵盖：从 Polygon CDK/zkEVM 迁移到 OP Stack 的架构背景；扫描 okx GitHub Organization，按近 3 个月活跃度筛选 Top 活跃 repo；主要开发方向与 PR 分类；Exchange OS、Agent Payments Protocol、Onchain OS 等新叙事方向；OKX 生态整合与分发策略；对 Mantle 的竞争启示。"
audience: "Mantle 工程团队（20260605 bi-weekly 全公司分享）"
expected_output: "一份结构化的研究 section，涵盖架构迁移背景、活跃 repo 概况、开发重点变化、新叙事方向分析和竞争启示。"

revision_metadata:
  created_by: "deep-research-agent"
  created_at: "2026-05-26T06:10:00Z"
  last_modified_by: "deep-research-agent"
  last_modified_at: "2026-05-26T06:10:00Z"
---

# Research Outline: X Layer 近期开发与叙事分析

## Items

### item-1: 架构迁移背景 — Polygon CDK/zkEVM 到 OP Stack

分析 X Layer 从 2024 年 3 月主网上线使用 Polygon zkEVM (Validium) 架构，经历 2025 年 8 月 PP Upgrade，到 2025 年 10 月/12 月完成 OP Stack 迁移的完整历程。重点分析迁移动机（Polygon CDK 战略调整与 zkEVM Mainnet Beta 日落、OP Stack 生态优势、EVM 等效性提升、开发工具链兼容性），以及迁移带来的技术变化（验证机制从 ZK 有效性证明到 Optimistic 欺诈证明、数据可用性从 DAC 到 L1 calldata/blobs、EVM 兼容性提升）。

- **Priority**: high
- **Dependencies**: none

### item-2: GitHub 活跃 Repo 概况与开发方向分析

扫描 `okx` GitHub Organization 近 3 个月活跃 repo，基于已获取的活动数据进行分类分析。重点 repo 包括：基础设施层（`optimism` fork ~100 commits/40 PRs、`xlayer-toolkit` ~47 commits/51 PRs、`xlayer-reth`、`op-geth`、`op-succinct`、`reth`）、AI/Agent 方向（`onchainos-skills` ~100 commits/26 PRs、`agent-skills`、`agent-trade-kit` 312 stars、`dapp-connect-agenticwallet`）、支付协议（`payments`、`mpp-specs`、`base-contracts` ERC-8183）、文档与生态（`xlayer-docs`、`plugin-store`）。按 PR 分类归纳主要开发方向变化趋势。

- **Priority**: high
- **Dependencies**: item-1

### item-3: Exchange OS — 链上交易所基础设施新叙事

深入分析 Exchange OS（2026 年 5 月 26 日发布）的定位与架构设计。涵盖：双环境架构（X Layer EVM 负责资产锚定与治理 + X Layer TradeZone 负责高频撮合与执行）；OKB 质押部署市场机制（permissionless 但有经济门槛）；共享流动性与统一账户模型（单账户跨所有市场）；支持市场类型（现货、永续合约、预测市场）；性能指标（300,000 TPS、毫秒级撮合）；CeDeFi 混合模式与全自托管交易设置。分析其作为"开放市场协议"与传统 CEX/DEX 二元叙事的差异。

- **Priority**: high
- **Dependencies**: item-1

### item-4: Agent Payments Protocol 与 Onchain OS 生态

分析 OKX 在 AI Agent 基础设施方向的布局。涵盖：Onchain OS 开发者平台（四大支柱：Agentic Wallet、Payments、Trade、AI Toolkit；三种接入方式：Skills/CLI、MCP、Open API）；Agent Payments Protocol (APP) 的三层架构（Wallet Layer - Agentic Wallet TEE 自托管 + 会话密钥、Implementation Layer - Payment SDK 零 gas、Protocol Layer - 支付模式定义）；支持的支付类型（单次/批量/按量计费/托管）；与 x402 和 MPP 的关系（采用 MPP 的 EVM 语法，在 x402 之上扩展多轮次商务场景）；Agentic Wallet（2026 年 3 月上线，TEE 私钥保护，支持 20+ 链）；ERC-8183 标准提案。

- **Priority**: high
- **Dependencies**: none

### item-5: OKX 生态整合与分发策略

分析 OKX 如何利用交易所资源为 X Layer 导流。涵盖：DeFi 蓝筹协议部署（Uniswap 2026 年 1 月上线且零协议费、Aave v3.6 2026 年 3 月上线支持 xBTC/xETH/xSOL 等原生资产）；OKX Wallet 原生集成（130+ 链支持，Aave 直接访问无需跨链）；统一 USD 订单簿（USDT/USDC 合并为 USDS 标记）；ICE（纽交所母公司）战略投资 250 亿美元估值及代币化股票合作；OKB 代币经济学（销毁 6500 万至 2100 万上限，gas token + 治理 + 质押）；生态合作伙伴阵容（Chainlink、Pyth、Nansen、Alibaba Cloud 等）；X Layer TVL 增长轨迹（此前约 2500 万美元，蓝筹部署后提升）。

- **Priority**: medium
- **Dependencies**: item-1, item-3

### item-6: 对 Mantle 的竞争启示

基于上述分析，提炼对 Mantle 的竞争启示。涵盖：同为交易所背景 OP Stack L2 的战略路径对比（OKX/X Layer vs Bybit/Mantle）；Exchange OS 的"开放市场协议"模式对 Mantle DeFi 生态建设的参考意义；Agent/AI 基础设施赛道的先发布局启示（APP 协议设计 vs Mantle 当前 Agent 策略）；生态导流策略差异（OKX 全栈整合 vs Mantle 独立生态）；OKB 代币经济学对 MNT 的参考（gas token + 质押 + 治理多角色设计）；关键差异化机会与潜在威胁。

- **Priority**: high
- **Dependencies**: item-1, item-2, item-3, item-4, item-5

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| architecture_stack | 当前和历史技术栈组件（共识机制、执行层、DA 方案） | item-1 |
| migration_rationale | 架构迁移的具体动机、触发因素和权衡 | item-1 |
| repo_activity_metrics | 近 3 个月 commit 数、PR 数、contributor 活跃度、star 增长 | item-2 |
| pr_classification | PR 按功能方向分类统计（基础设施/Agent/支付/文档） | item-2 |
| narrative_positioning | 官方叙事定位、品牌口号、白皮书核心主张 | item-3, item-4 |
| technical_design | 核心技术架构设计、性能指标、安全模型 | item-3, item-4 |
| ecosystem_partnerships | 主要合作伙伴、集成协议、生态支持 | item-5 |
| token_economics | OKB 的 gas/治理/质押多角色设计与代币经济学 | item-3, item-5 |
| competitive_comparison | 与 Mantle 的直接对比维度（技术/生态/策略/代币） | item-6 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | timeline | X Layer 关键里程碑时间线（2024.03 主网 → 2025.08 PP Upgrade → 2025.10 OP Stack 迁移 → 2026.01 Uniswap → 2026.03 Aave/Agentic Wallet → 2026.04 APP → 2026.05 Exchange OS） | mermaid | item-1, item-3, item-4 |
| diag-2 | architecture | Exchange OS 双环境架构图（X Layer EVM + TradeZone、OKB 质押机制、共享流动性层） | mermaid | item-3 |
| diag-3 | architecture | Agent Payments Protocol 三层架构图（Wallet Layer → Implementation Layer → Protocol Layer，含支付模式与通信通道） | mermaid | item-4 |
| diag-4 | comparison | X Layer vs Mantle 竞争维度对比矩阵（技术栈/生态策略/代币经济/AI Agent 布局/交易所整合度） | ascii | item-6 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | official_docs | X Layer 官方文档、Exchange OS 白皮书、APP 白皮书、架构迁移公告 | 4 |
| src-2 | code_analysis | okx GitHub Organization 活跃 repo 的 PR/commit 数据扫描（覆盖基础设施、Agent、支付三大方向） | 6 |
| src-3 | official_docs | OKX/Optimism/Aave/Uniswap 官方公告（协议部署、迁移声明） | 3 |
| src-4 | industry_reports | 第三方行业媒体报道与分析（CryptoBriefing、The Block、L2BEAT 等） | 3 |
| src-5 | on_chain_data | X Layer 网络数据（TVL、TPS、地址数、交易量）— 如 L2BEAT、DeFiLlama | 2 |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
