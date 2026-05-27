---
topic: "Base AgentFi 生态补充调研"
project_slug: "202606-internal-sharing"
topic_slug: "supplement-base-agentfi"
github_repo: "Whisker17/multica-research"
round: 1
status: draft
artifact_paths:
  outline: "202606-internal-sharing/outlines/supplement-base-agentfi.md"
  draft: "202606-internal-sharing/research-sections/supplement-base-agentfi/drafts/round-1.md"
  final: "202606-internal-sharing/research-sections/supplement-base-agentfi/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"
draft_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-27"
  mode: "initial_deep_draft"
  outline_path: "202606-internal-sharing/outlines/supplement-base-agentfi.md"
  outline_commit: "bb2ccb6"
  outline_approval_source: "Multica Orchestrator combined dispatch 4fd25623-252d-456d-b2a6-8bca66e637ce — 'produces outline then deep draft'"
  branch_name: "research/202606-internal-sharing/supplement-base-agentfi"
  language: "zh-CN"
  research_depth: "standard"
  accessed_at: "2026-05-27"
  items_covered:
    - "1.1-base-mcp"
    - "1.2-cdp-agentkit"
    - "1.3-x402"
    - "1.4-cdp-platform"
    - "2.1-social-agents"
    - "2.2-trading-defi-agents"
    - "2.3-gaming-agents"
    - "2.4-market-data"
    - "3.1-flashblocks"
    - "3.2-smart-wallet-aa"
    - "3.3-liquidity-defi"
    - "4.1-agentfi-infra-requirements"
    - "4.2-mantle-gap-analysis"
  diagrams_produced: []
  gaps:
    - "Base 上 Agent 精确总数无权威统计来源，使用 Virtuals Protocol 部署数据作为下限估算"
    - "游戏类 Agent 案例相对稀少，AWE 公开数据有限"
---

# Base AgentFi 生态补充调研

> 本文为 202606 内部分享 AgentFi 方向（Slide 14）的补充材料，聚焦 Base 在 AgentFi 方向的具体技术基础设施与生态构成，与主研究节 narrative-agentfi 互补。

## 1. Base AI Agent 基础设施

Base（Coinbase 孵化的 Ethereum L2）围绕 Coinbase Developer Platform（CDP）构建了一套完整的 AI Agent 使能技术栈，形成了"开发框架 → 钱包基础设施 → 支付协议 → AI 接口层"的四层架构。

### 1.1 Base MCP

Base MCP 是 Base 于 2026 年 5 月 26 日发布的 Model Context Protocol 服务器，定位为"AI Agent 的链上网关"。它基于 Anthropic 于 2024 年提出的 MCP 开放标准，使 Claude Desktop、ChatGPT、Cursor 等 AI 应用能够通过自然语言直接执行链上操作——包括发送代币、兑换、查余额、查交易历史、以及与 DeFi 协议交互。

**核心设计要点**：

- **Skill Plugin 体系**：首发集成 Morpho（借贷）、Moonwell（借贷）、Aerodrome（DEX/流动性）、Uniswap（兑换）、Avantis（永续合约）、Bankr（代币发现）、Virtuals（Agent 代币发现）七大协议插件，覆盖 Base DeFi 主要场景。开发者可通过 Markdown 规范编写自定义 Skill Plugin 扩展协议支持。
- **安全模型**：采用 OAuth 2.1 认证连接 AI Agent 与用户 Base Account。MCP 服务器不持有私钥，不能自主执行交易——Agent 构建交易后生成确认链接，由用户在 Base App 中审核签名。这种架构可有效缓解域名劫持和钓鱼攻击。
- **支付支持**：内置 x402 微支付服务调用能力，并支持跨 EVM 链的余额和交易历史查询。

*（来源：blog.base.org/base-mcp, 2026-05-26; theblock.co, 2026-05-26; fortune.com, 2026-05-26）*

### 1.2 CDP AgentKit

AgentKit 是 CDP 的核心 AI Agent 开发框架，设计原则是"每个 AI Agent 都应有自己的加密钱包"。其架构特点：

- **模型无关 + 框架无关**：支持 OpenAI、Anthropic、Llama 等多种 LLM，兼容 LangChain、OpenAI Agents SDK 等框架。
- **Action Provider 体系**：提供 50+ TypeScript Actions 和 30+ Python Actions，按功能分组为 DeFi Provider、Social Provider 等，覆盖转账、兑换、NFT 铸造、智能合约部署等操作。
- **Agentic Wallets**（2026 年 2 月发布）：专为自主 Agent 设计的钱包基础设施——使用 TEE（可信执行环境）保护非托管密钥，内置策略引擎支持 Session Caps（单次运行总额度）和 Transaction Limits（单笔上限），在 Base 上通过 Paymaster 实现无 Gas 交易。

*（来源：docs.cdp.coinbase.com/agent-kit; coinbase.com/developer-platform/discover/launches/agentic-wallets, 2026-02）*

### 1.3 x402 协议

x402 由 Coinbase 开发的开源协议，通过激活 HTTP 402 状态码实现"单次 HTTP 请求同时传输数据和价值"。其核心能力：

| 指标 | 数据 |
|------|------|
| 最低支付额 | $0.001 |
| 结算速度 | 亚秒级 |
| 周交易量（2025 年末峰值） | 156,000 笔 |
| 治理方 | Coinbase + Cloudflare 联合基金会（2025-09 成立） |
| 外部集成 | Google Agent Payments Protocol (AP2) |

x402 使 Agent 能够自主付费获取 API、算力、数据流和存储等资源，无需人工干预。2026 年 V2 升级进一步支持钱包身份、动态支付接收方、多链/法币扩展。

*（来源：docs.cdp.coinbase.com/x402; x402.org/writing/x402-v2-launch; blockeden.xyz, 2025-10）*

### 1.4 CDP 平台协同

CDP 的战略定位是将 Base 打造为 Agent 经济的默认执行层。四层组件的协同关系：AgentKit 提供开发框架和链上操作能力 → Agentic Wallets 提供安全钱包和权限控制 → x402 提供机器间支付通道 → Base MCP 提供标准化 AI 接口层。这种垂直整合使得开发者可以通过 `npm create onchain-agent@latest` 一键启动具备钱包、DeFi 操作和支付能力的 Agent 应用。

## 2. Base 上 Agent 生态组成

### 2.1 Social 类

**Clanker** 是 Base 上最具代表性的 Social Agent。它运行在 Farcaster 社交协议上，用户只需在帖子中标记 @clanker，即可自动完成 ERC-20 代币铸造、Uniswap V3 流动性设置和 LP 锁定。截至 2026 年初：

| 指标 | 数据 |
|------|------|
| 累计协议费用 | >$50M |
| 周费用峰值 | $8.02M（2026-02） |
| 累计交易量 | >$7B |
| 日创建代币峰值 | 21,870 个（2026-02-02） |
| 交易者总数 | >558,000 |

2025 年 10 月 Clanker 被 Farcaster 收购，2026 年 1 月转入 Farcaster 基础设施商 Neynar。

**Virtuals Protocol** 是 Base 上最大的 AI Agent 发行和代币化平台：

| 指标 | 数据 |
|------|------|
| 部署 Agent 数 | >18,000 |
| 累计协议收入 | >$75M |
| VIRTUAL 市值 | ~$5.39 亿（2026-05-27, CoinMarketCap） |
| 月交易量 | ~$13.2B |
| 年度协议收入排名 | Base 第二（>$59M） |

Virtuals 通过 Agent Commerce Protocol (ACP) 实现 Agent 间安全交易，每笔交易需消耗 VIRTUAL 代币。2026 年已扩展至 Arbitrum、Solana、Ronin 多链。

*（来源：CoinMarketCap, 访问日期 2026-05-27; CoinGecko; KuCoin Research）*

### 2.2 Trading/DeFi 类

基于 AgentKit + Agentic Wallets 构建的自主 DeFi Agent 构成 Base Agent 生态的重要部分。典型模式包括：7×24 收益监控与自动再平衡、跨协议流动性管理、以及通过 Clanker 自动发币后的流动性引导。Coinbase 官方描述的 "Autonomous DeFi" 场景——Agent 在凌晨 3 点发现更优收益机会后自动完成仓位调整——已通过 Agentic Wallets 的预设权限实现。

### 2.3 游戏类

AWE（Autonomous Worlds Engine）提供去中心化持久世界框架，支持 Agent 在链上环境中协作、竞争和进化。Virtuals Protocol 旗下的 AI 角色（如 Luna）也在探索游戏和娱乐场景。但整体而言，Base 上游戏类 Agent 仍处于早期探索阶段，落地案例有限。

### 2.4 市场规模

加密 AI Agent 赛道的整体市值约 $2.3-2.6B（2026 年，多家分析机构估算）。Virtuals Protocol 及其生态占约四分之一。Base 上 Agent 部署数下限为 18,000+（仅 Virtuals 平台），加上 Clanker 系、独立 Agent 和 Moltbook（被 Meta 收购前约有 200,000 验证 Agent），Base 在 Agent 部署密度上处于行业领先。

## 3. Base 生态支撑层

### 3.1 Flashblocks（200ms 预确认）

Flashblocks 于 2025 年 7 月上线，由 Base 与 Flashbots 联合开发。技术原理：在保持 2 秒标准区块周期的同时，每 200ms 流式产出一个子块（Sub-block），一个完整区块包含 10 个 Flashblocks。每个子块的交易排序一旦广播即锁定，防止后到高 Gas 交易插队。

实际端到端确认时间约 300-500ms（200ms 子块间隔 + 网络传播），较标准 2 秒降低约 10 倍。这对 Agent 场景至关重要：Agent 可以近实时感知余额变化、流动性迁移和价格波动，实现类似 CEX 的交易体验。

*（来源：chainstack.com/flashblocks-base-rpc; theblock.co, 2025-07; chainstacklabs/base-flashblocks-transaction-latency-test）*

### 3.2 Smart Wallet 与 AA 权限体系

Base 的 Agent 钱包权限模型遵循"给 Agent 权限，让钱包执行规则"的原则：

- **ERC-4337 + ERC-7715**：Coinbase Smart Wallet 基于 ERC-4337 账户抽象标准，通过 ERC-7715 Session Keys 实现临时签名权限的注册、范围限定、过期和撤销。
- **SpendPermissionManager**：独立单例合约，被添加为用户 Smart Wallet 的 owner，仅能在严格的消费权限逻辑内代表 sender 移动资金（如"每月 10 USDC"），不能发起任意外部调用。用户可随时调用 `revoke` 撤销。
- **Agentic Wallets 策略引擎**：在签名层之上运行策略检查——Session Caps 限制一次 Agent 运行期间的总消费、Transaction Limits 限制单笔支付。策略由运营方在创建时配置，可即时收紧。
- **关键安全原则**：Agent 始终是 `isAdmin: false`；所有关键策略在链上强制执行，不依赖 Agent 端的行为可信。

*（来源：github.com/coinbase/smart-wallet-permissions; github.com/coinbase/spend-permissions; docs.base.org）*

### 3.3 DeFi 流动性支撑

Aerodrome 作为 Base 最大 DEX，为 Agent 财库管理提供核心流动性支撑：

| 指标 | 数据 |
|------|------|
| TVL 峰值 | >$1B（2025-12，占 Base 总 TVL 约 25%） |
| 日均交易量 | ~$810M |
| 年化 Swap 收入 | ~$202M |
| 关键升级 | Slipstream V2（集中流动性，资本效率提升 34x） |

Aerodrome 的 veAERO 治理和 Momentum Fund 为协议级 Agent 资产管理提供了链上可编程的财库管理框架。2026 年 Aerodrome 正向"Aero"统一平台迁移，整合 Velodrome（Optimism），扩展至以太坊主网和 Circle Arc Chain，为 Agent 提供跨链流动性访问。

*（来源：DefiLlama/aerodrome, 访问日期 2026-05-27; dwf-labs.com/research; coindesk.com, 2026-01）*

## 4. 技术要求分析

### 4.1 AgentFi 链 Infra 需求总结

从 Base 的实践可提炼 AgentFi 链需要提供的六项核心基础设施：

| 基础设施层 | 说明 | Base 对标 |
|-----------|------|----------|
| 标准化 AI 接口 | MCP server 或等效协议，使 AI 应用直接调用链上操作 | Base MCP |
| Agent 钱包 + 权限管理 | AA 钱包 + Session Keys + 策略引擎，链上强制执行 | Coinbase Smart Wallet + Agentic Wallets |
| 低延迟执行 | <500ms 确认，支持 Agent 实时决策 | Flashblocks（200ms 子块） |
| 机器间支付 | HTTP 原生微支付协议，支持 Agent 自主消费 | x402 |
| DeFi 流动性 | 深度 DEX 流动性 + 集中流动性，支撑 Agent 财库运作 | Aerodrome |
| Agent 发行平台 | Agent 注册、代币化、交易市场 | Virtuals Protocol + Clanker |

### 4.2 与 Mantle 技术栈 Gap 分析

| 维度 | Mantle 现状 | Gap |
|------|-----------|-----|
| AI 接口层 | 无 MCP server 或等效标准化接口 | 需构建 |
| Agent 钱包 | 有 AA 基础（ERC-4337 兼容），无 Agent 专用权限体系 | 需扩展 Session Keys + 策略引擎 |
| 执行延迟 | 标准 L2 区块时间（~2s），无子块机制 | 需评估 Flashblocks 等预确认方案 |
| 机器支付 | 无 x402 或等效协议支持 | 需引入或自建 |
| DeFi 流动性 | 有 DEX 生态但深度不及 Base/Aerodrome | 需持续建设 |
| Agent 发行 | 无 Virtuals/Clanker 类平台 | 需生态引入 |
| 优势基础 | EVM 完全兼容、MNT 低 Gas、已有账户抽象基础 | 可复用 |

**优先级建议**：(1) MCP server 或等效 AI 接口层——门槛低、差异化明显；(2) Agent 钱包权限体系——基于现有 AA 基础扩展；(3) 生态引入 Agent 发行平台——需 BD 驱动。

---

## 数据来源汇总

| 来源 | 类型 | 访问日期 |
|------|------|---------|
| blog.base.org/base-mcp | 官方博客 | 2026-05-27 |
| docs.cdp.coinbase.com/agent-kit | 官方文档 | 2026-05-27 |
| docs.cdp.coinbase.com/x402 | 官方文档 | 2026-05-27 |
| x402.org | 协议官方 | 2026-05-27 |
| coinbase.com/developer-platform | 官方平台 | 2026-05-27 |
| CoinMarketCap (VIRTUAL) | 市场数据 | 2026-05-27 |
| DefiLlama (Aerodrome) | DeFi 数据 | 2026-05-27 |
| chainstack.com | 技术文档 | 2026-05-27 |
| theblock.co | 行业媒体 | 2026-05-27 |
| github.com/coinbase/agentkit | 开源代码 | 2026-05-27 |
| github.com/coinbase/smart-wallet-permissions | 开源代码 | 2026-05-27 |
| KuCoin Research (Clanker) | 行业报告 | 2026-05-27 |
| dwf-labs.com/research | 行业报告 | 2026-05-27 |

## Gap Analysis

1. **Base Agent 总数**：无权威统计来源。Virtuals Platform 的 18,000+ 部署 Agent 为可引用下限，实际 Base 全链 Agent 数量（包含独立部署）可能数倍于此。
2. **游戏类 Agent**：AWE 等项目公开数据有限，该分类的案例深度不足。
3. **x402 最新交易量**：仅引用 2025 年末峰值数据（156K/周），2026 年日均约 57K 笔但波动较大。

## Revision Log

- Round 1 (2026-05-27): 初始深度草稿，覆盖全部 4 个 Scope、13 个研究项目。
