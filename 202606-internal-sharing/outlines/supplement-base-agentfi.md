---
topic: "Base AgentFi 生态补充调研"
project_slug: "202606-internal-sharing"
topic_slug: "supplement-base-agentfi"
github_repo: "Whisker17/multica-research"
round: 1
status: approved

artifact_paths:
  outline: "202606-internal-sharing/outlines/supplement-base-agentfi.md"
  draft: "202606-internal-sharing/research-sections/supplement-base-agentfi/drafts/round-{n}.md"
  final: "202606-internal-sharing/research-sections/supplement-base-agentfi/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

scope: |
  Base 在 AgentFi 方向的具体技术基础设施和生态构成补充调研。覆盖四个层面：
  (1) Base AI Agent 基础设施——Base MCP、CDP AgentKit、x402 协议、CDP 平台角色；
  (2) Base 上 Agent 生态分类——游戏、Social（Clanker 等）、Trading/DeFi 类代表项目及市场数据；
  (3) Base 生态支撑层——Flashblocks 200ms 软确认、Smart Wallet/AA 权限体系、Aerodrome 流动性；
  (4) AgentFi 链技术要求分析及与 Mantle 当前技术栈的 gap。
  重点是 Base 具体的技术和生态事实，不是泛谈 AgentFi。

audience: |
  Mantle 工程团队 20260605 bi-weekly 内部分享准备者、BD/生态团队；
  读者已熟悉 L2/EVM/AgentFi 基本概念（已有 narrative-agentfi 研究节），
  需要一份聚焦 Base 实施细节的中文补充材料，作为分享 slides 的附录数据支撑。

expected_output: |
  中文 Markdown 补充研究文档，约 1500-2500 字，结构化章节，包含数据来源。
  最终产出路径：202606-internal-sharing/report/assets/supplementary/base-agentfi-supplement.md

source_requirements_summary: |
  以 2025 年下半年至 2026 年 5 月的公开信息为主。市值、TVL、交易量等易过期数字
  必须标注来源和访问日期。优先使用官方文档（docs.base.org、docs.cdp.coinbase.com）、
  官方博客（blog.base.org）、DefiLlama、CoinGecko 等一手数据源。

revision_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-27T13:30:00+08:00"
  last_modified_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  last_modified_at: "2026-05-27T13:30:00+08:00"

multica_issue_id: "7322d644-e9a3-4f01-961b-b0437116d39f"
branch_name: "research/202606-internal-sharing/supplement-base-agentfi"
base_commit: "9c26c33"
language: "中文"
research_depth: "standard"
---

## 研究项目（Research Items）

### 1. Base AI Agent 基础设施

**优先级**: P0
**预估篇幅**: 500-700 字

#### 1.1 Base MCP（Model Context Protocol Server）

- **调研要素**:
  - Base MCP 的定位与架构（MCP server → AI 应用 → 链上操作）
  - 支持的 AI 平台（Claude Desktop、ChatGPT、Cursor）
  - Skill Plugin 体系：Morpho、Moonwell、Aerodrome、Uniswap、Avantis、Bankr、Virtuals
  - 安全模型：OAuth 2.1 认证、无私钥托管、用户签名确认
  - 可扩展性：开发者可编写自定义 Skill Plugin
- **数据来源**: docs.base.org/ai-agents, blog.base.org/base-mcp（2026-05-26 发布）

#### 1.2 CDP AgentKit

- **调研要素**:
  - 架构：模型无关 + 框架无关设计
  - Action Provider 体系：50+ TypeScript Actions / 30+ Python Actions
  - 核心能力：DeFi 交互、NFT 操作、代币部署、智能合约部署
  - Agentic Wallets（2026-02）：TEE 非托管钱包、Session Caps、Transaction Limits
  - Smart Wallet 集成：无 Gas 交易、Paymaster 路由
- **数据来源**: docs.cdp.coinbase.com/agent-kit, github.com/coinbase/agentkit

#### 1.3 x402 协议

- **调研要素**:
  - 技术原理：HTTP 402 状态码激活、单请求数据+价值传输
  - 性能数据：最低 $0.001 微支付、亚秒结算、156K 周交易量（截至 2025 年末）
  - 生态整合：Google AP2 集成、Cloudflare 联合治理、V2 升级
  - 对 Agent 经济的意义：机器间自主支付、无需 API Key/人工介入
- **数据来源**: docs.cdp.coinbase.com/x402, x402.org

#### 1.4 CDP 平台整体角色

- **调研要素**:
  - CDP 作为 Agent 使能统一平台的定位
  - AgentKit + Agentic Wallets + x402 + Base MCP 的协同关系
  - 与 Base 链的深度绑定
- **数据来源**: coinbase.com/developer-platform

### 2. Base 上 Agent 生态组成与分类

**优先级**: P0
**预估篇幅**: 400-600 字

#### 2.1 Social 类 Agent

- **调研要素**:
  - Clanker：Farcaster 自动发币机器人、累计费用 $50M+、周费用峰值 $8M
  - Virtuals Protocol：18,000+ 部署 Agent、累计协议收入 $75M+、VIRTUAL 市值 ~$5.4 亿
  - Moltbook：AI-only 社交平台、Agent 自驱微经济
- **数据来源**: CoinGecko, DefiLlama, 项目官方

#### 2.2 Trading/DeFi 类 Agent

- **调研要素**:
  - 自主 DeFi Agent：收益监控、流动性管理、跨协议再平衡
  - 代表项目：基于 AgentKit 构建的交易机器人
  - Agent 发币与流动性自动化
- **数据来源**: 项目官方, DeFi 数据平台

#### 2.3 游戏类 Agent

- **调研要素**:
  - AWE（Autonomous Worlds Engine）：去中心化持久世界中 Agent 协作
  - Virtuals Protocol 的游戏垂直应用
- **数据来源**: 项目官方

#### 2.4 市场数据

- **调研要素**:
  - Base 上 Agent 总体规模估算
  - AI Agent 加密市场总市值（~$2.3-2.6B，2026 年）
  - Base 在 Agent 赛道的份额定位
- **数据来源**: CoinMarketCap, CoinGecko, 行业报告

### 3. Base 生态支撑层

**优先级**: P0
**预估篇幅**: 400-500 字

#### 3.1 Flashblocks（200ms 软确认）

- **调研要素**:
  - 技术实现：每 2 秒区块内流式 10 个子块、200ms 间隔
  - 实际延迟：300-500ms（含网络传播）
  - 对 Agent 的意义：实时余额/价格/流动性变化感知、前置交易防护
  - 时间线：2025 年 7 月上线
- **数据来源**: chainstack.com, theblock.co, docs.base.org

#### 3.2 Smart Wallet 与 AA 权限体系

- **调研要素**:
  - Coinbase Smart Wallet：ERC-4337 + ERC-7715 Session Keys
  - Spend Permissions：SpendPermissionManager 单例、额度限制、可撤销
  - Agent 钱包权限模式：注册式、范围限定、可过期、可撤销的签名密钥
  - 链上规则强制执行（非 Agent 行为信任）
  - Agentic Wallets 的策略引擎：Session Caps + Transaction Limits
- **数据来源**: github.com/coinbase/smart-wallet-permissions, docs.base.org

#### 3.3 流动性与 DeFi 生态

- **调研要素**:
  - Aerodrome：Base 最大 DEX、TVL 峰值 $1B+（2025-12）、日均交易量 ~$810M
  - Slipstream V2 集中流动性：资本效率提升 34x
  - veAERO 治理与 Momentum Fund 财库管理
  - 对 Agent 财库管理的支撑：深度流动性 + 低滑点 + Flashblocks 加速
- **数据来源**: DefiLlama, aerodrome.finance

### 4. 技术要求分析

**优先级**: P1
**预估篇幅**: 300-400 字

#### 4.1 AgentFi 链 infra 需求总结

- **调研要素**:
  - 从 Base 案例提炼 AgentFi 链的核心 infra 需求：
    - MCP/标准化 AI 接口层
    - Agent 钱包 + 权限管理（AA/Session Keys）
    - 低延迟执行环境（<500ms 确认）
    - 机器间支付协议
    - 深度 DeFi 流动性
    - Agent 发行与注册平台
- **数据来源**: 前三章研究结论综合

#### 4.2 与 Mantle 当前技术栈 gap 分析（简要）

- **调研要素**:
  - Mantle 已有：EVM 兼容、低 Gas（MNT）、账户抽象基础
  - Mantle 缺失/待建：MCP server、Agent 专用钱包权限、<500ms 确认、Agent 发行平台、机器间支付协议
  - 优先级建议
- **数据来源**: narrative-agentfi 研究节结论 + 本研究提炼

## 图表期望

本补充研究为附录性质材料（~2000 字），不设独立图表。关键数据以表格形式内嵌在正文中。

## 质量检查清单

- [ ] 每个研究项目有明确调研要素和数据来源
- [ ] 覆盖全部 4 个 Scope 领域
- [ ] 聚焦 Base 具体技术和生态事实，非泛谈 AgentFi
- [ ] 数据需标注来源和时效性
- [ ] 中文输出，约 1500-2500 字
- [ ] 与已有 narrative-agentfi 研究节互补而非重复
