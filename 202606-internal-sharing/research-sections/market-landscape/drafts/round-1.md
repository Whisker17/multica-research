---
topic: "L2 赛道格局与市场现状分析"
project_slug: "202606-internal-sharing"
topic_slug: "market-landscape"
github_repo: "Whisker17/multica-research"
round: 1
status: draft

artifact_paths:
  outline: "202606-internal-sharing/outlines/market-landscape.md"
  draft: "202606-internal-sharing/research-sections/market-landscape/drafts/round-1.md"
  final: "202606-internal-sharing/research-sections/market-landscape/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

draft_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-26T14:30:00+08:00"
  outline_commit: "04b359ee1c92d2dd479cc2acd4de45aa977e43fc"
  branch_name: "research/202606-internal-sharing/market-landscape"
  language: "中文"
  research_depth: "standard"
  items_covered: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  fields_investigated: [chain, metric_name, metric_definition, time_window, data_source, query_or_source_url, last_refreshed_at, evidence_level, confidence, l2_positioning, differentiation_axis, narrative_claim, market_evidence, mantle_relevance, caveat]
  diagrams_produced: [diag-1, diag-2, diag-3, diag-4, diag-5, diag-6, diag-7, diag-8, diag-9]
  source_requirements_coverage:
    src-1: partial
    src-2: met
    src-3: met
    src-4: met
    src-5: met
    src-6: met
    src-7: met
    src-8: partial
  draft_gates:
    scope_focus_gate: "item-5/item-6 用作比较证据，不挤占五链核心对比和 Mantle 定位论证"
    data_artifact_gate: "提供 DuneSQL 查询模板、last-refreshed 时间戳、CSV-ready 图表数据、DAU/交易数据 bot/spam 过滤 caveat"

multica_issue_id: "ae371472-f733-4dcc-a34b-a9194d099148"
---

# L2 赛道格局与市场现状分析

## Executive Summary

Ethereum L2 赛道已从 2023-2024 年的"通用低费 Rollup 扩容"竞争，进入 2025-2026 年的差异化定位与生态整合阶段。截至 2026 年 5 月，73 条活跃 Rollup 合计锁定超过 480 亿美元 TVL，但市场高度集中：Arbitrum（$14.9-16.9B，~40-44%）和 Base（$10.7-12.8B，~28-33%）两链合计占据约 77% 的 L2 DeFi 流动性。OP Mainnet（$1.7-1.9B）、Mantle（~$1.15-1.2B）、zkSync Era（~$404M）构成第二梯队，差距显著。

在用户活跃度维度，分化更为剧烈：Base 以日均 38.3 万-66.3 万活跃地址和 1,289 万笔日交易领跑全部 L2；Arbitrum 约 13.3 万 DAU / 417 万笔日交易；OP Mainnet 约 8.2 万 DAU；zkSync Era 降至约 4,000 DAU / 1.96 万笔日交易。Mantle 未进入主流 dashboard 的 DAU 排名前列，指示用户基数相对有限。

DeFi 叙事在 2026 年面临结构性约束：全链 DeFi TVL 在 $92-140B 区间波动，远低于 $250B 的市场预期；83-95% 的存入流动性处于闲置状态；Aave 以 59% 市场份额高度垄断借贷赛道。与此同时，RWA / 机构金融叙事加速：链上 RWA 总市值从 2025 年初的 ~$6B 增长至 2026 年 5 月的 $31-34B（>200% YoY）；BlackRock BUIDL 达 ~$2.5B AUM；美国国债 tokenization 突破 $12.9-15B。合规基础设施正在成为 L2 差异化的新竞争维度，但 Vitalik 在 2026 年 2 月的 cypherpunk 宣言强调隐私与抗审查优先，与行业 ToB/KYC 转向形成张力。

Mantle 当前定位为 OP Stack + EigenDA 的模块化 L2，mETH（~$925M TVL）和 cmETH（~$515M TVL）构成 yield-bearing 资产底座。Aave V3 于 2026 年 2 月上线后推动 TVL 突破 $1B，但激励驱动的 TVL 粘性存疑。在五链竞争中，Mantle 需要从 mETH/DeFi 基本盘出发，探索 RWA / 机构金融 / 合规结算的差异化叙事，同时面对 Base（Coinbase 分发）、Arbitrum（DeFi/Orbit 生态）、Optimism（Superchain 网络效应）和 zkSync（ZK 隐私/企业）的多维竞争。

---

## Item-1: 数据口径、DuneSQL 查询设计与交叉验证框架

### 1.1 链映射与标识

| 链名称 | Chain ID | Dune Schema | DefiLlama Slug | L2Beat Slug |
|--------|----------|-------------|----------------|-------------|
| Base | 8453 | `base` | `base` | `base` |
| Arbitrum One | 42161 | `arbitrum` | `arbitrum` | `arbitrum` |
| OP Mainnet | 10 | `optimism` | `optimism` | `optimism` |
| zkSync Era | 324 | `zksync` | `era` | `zksync-era` |
| Mantle | 5000 | `mantle` | `mantle` | `mantle` |

**Caveat**: Dune 对各链的表覆盖和索引时效存在差异。zkSync Era 和 Mantle 的 `transactions` 表可能不包含所有 internal transactions；Mantle 的 `traces` 表覆盖可能不完整。Base 和 Arbitrum 的表结构最为成熟。

### 1.2 时间窗口定义

| 窗口名称 | 范围 | 用途 |
|----------|------|------|
| 12m trend | 2025-05-26 至 2026-05-26 | 长期趋势、结构性变化 |
| 90d change | 2026-02-25 至 2026-05-26 | 近期动态、短期分化 |
| YTD | 2026-01-01 至 2026-05-26 | 年度进展 |

所有时间窗口使用 UTC 时区。日频聚合保留 `date`、`chain`、`metric`、`value` 四列。

### 1.3 DuneSQL 查询清单

以下为各核心指标的 DuneSQL 查询模板。所有查询均需在实际执行时替换 `{{chain}}` 和日期参数。

#### 查询 Q1: 日活地址（DAU）

```sql
-- DuneSQL: Daily Active Addresses (sender-based)
-- 适用于 Base / Arbitrum / Optimism / Mantle
-- zkSync Era 使用 zksync.transactions 表
SELECT
  date_trunc('day', block_time) AS date,
  '{{chain}}' AS chain,
  'dau_sender' AS metric,
  COUNT(DISTINCT "from") AS value
FROM {{chain}}.transactions
WHERE block_time >= DATE '2025-05-26'
  AND block_time < DATE '2026-05-27'
  AND success = true
  -- 过滤系统地址 (sequencer, batcher, bridge contracts)
  -- 需要按链维护排除地址列表
  AND "from" NOT IN (
    -- Base: sequencer 0x4200000000000000000000000000000000000011
    -- Arbitrum: sequencer, batcher 等
    -- 需手动维护，此处为模板
    CAST(0x0 AS varbinary)  -- placeholder
  )
GROUP BY 1
ORDER BY 1
```

**⚠️ DAU Caveat**: 此查询统计所有发起成功交易的唯一地址。不区分 EOA 和合约地址，不过滤 bot/spam/farming 地址。低 gas 费链（Base、Mantle）可能产生大量 bot 交易。Base 的 DAU 峰值中 social protocol（如 Farcaster 相关应用）可能贡献显著比例。DAU ≠ 真实用户数。

#### 查询 Q2: 日交易笔数

```sql
-- DuneSQL: Daily Transaction Count
SELECT
  date_trunc('day', block_time) AS date,
  '{{chain}}' AS chain,
  'tx_count' AS metric,
  COUNT(*) AS value
FROM {{chain}}.transactions
WHERE block_time >= DATE '2025-05-26'
  AND block_time < DATE '2026-05-27'
  AND success = true
GROUP BY 1
ORDER BY 1
```

#### 查询 Q3: Gas Used / Fees Paid

```sql
-- DuneSQL: Daily Gas Used and Fees (ETH)
SELECT
  date_trunc('day', block_time) AS date,
  '{{chain}}' AS chain,
  SUM(gas_used) AS gas_used,
  SUM(gas_used * gas_price / 1e18) AS fees_eth
FROM {{chain}}.transactions
WHERE block_time >= DATE '2025-05-26'
  AND block_time < DATE '2026-05-27'
  AND success = true
GROUP BY 1
ORDER BY 1
```

**⚠️ Fees Caveat**: EIP-4844（2024 年 3 月）后 L2 费用下降 80-90%。不同链的 gas_price 结构不同（Base 有 priority fee 占比 86.1%，Arbitrum 有 Timeboost 额外费用）。USD 折算需要对应时间点的 ETH/USD 价格。

#### 查询 Q4: 新合约部署

```sql
-- DuneSQL: Daily New Contract Deployments
SELECT
  date_trunc('day', block_time) AS date,
  '{{chain}}' AS chain,
  'new_contracts' AS metric,
  COUNT(*) AS value
FROM {{chain}}.creation_traces
WHERE block_time >= DATE '2025-05-26'
  AND block_time < DATE '2026-05-27'
GROUP BY 1
ORDER BY 1
```

**⚠️ 开发者 Proxy Caveat**: 合约部署数 ≠ 开发者数量。一个开发者可能部署多个合约；factory contract 可自动批量部署；测试/spam 合约也会计入。需与 verified contract、GitHub activity 等交叉验证。

#### 查询 Q5: 活跃合约

```sql
-- DuneSQL: Daily Active Contracts (contracts receiving calls)
SELECT
  date_trunc('day', block_time) AS date,
  '{{chain}}' AS chain,
  'active_contracts' AS metric,
  COUNT(DISTINCT "to") AS value
FROM {{chain}}.transactions
WHERE block_time >= DATE '2025-05-26'
  AND block_time < DATE '2026-05-27'
  AND success = true
  AND "to" IS NOT NULL
GROUP BY 1
ORDER BY 1
```

### 1.4 TVL 数据方案

TVL 不从 Dune 直接获取，而使用 DefiLlama 和 L2Beat 交叉验证：

| 数据源 | 口径 | 差异说明 |
|--------|------|----------|
| DefiLlama | DeFi TVL | 仅统计 DeFi 协议中锁定的资产，不含桥接资产 |
| L2Beat TVL | Total Value Locked | 包含 canonical bridged + externally bridged + natively minted |
| L2Beat TVS | Total Value Secured | 更广义的安全保障价值 |

**关键口径差异**：DefiLlama 的 Mantle TVL 主要反映 Aave/DEX/lending 等 DeFi 协议锁定值（~$543M DeFi TVL），而 L2Beat 的 TVL 包括所有桥接进入的资产（~$1.15-1.2B）。两个数字都是事实，但含义不同。本文在比较时会标注使用的口径。

### 1.5 去重与过滤规则

| 过滤类型 | 处理方式 |
|----------|----------|
| 系统地址 | 排除 L2 sequencer、batcher、bridge contract、L1MessageSender 等已知系统地址 |
| 合约内部调用 | DAU 使用 transaction-level `from` 字段，不含 internal transaction 的发起者 |
| 空投/激励 Spike | 标注时间点，不从趋势中移除但在分析中说明影响 |
| Bot/Spam | 无统一过滤方案；以 caveat 形式说明低费链数据可能偏高 |
| 价格波动 | TVL 受资产价格影响；区分 USD-denominated TVL 和 token-denominated TVL |

### 1.6 输出数据字典

| 字段 | 类型 | 说明 |
|------|------|------|
| date | DATE | 日期（UTC） |
| chain | VARCHAR | Base / Arbitrum / Optimism / zkSync / Mantle |
| metric | VARCHAR | dau_sender / tx_count / gas_used / fees_eth / new_contracts / active_contracts |
| value | NUMERIC | 指标值 |
| unit | VARCHAR | addresses / transactions / gas / ETH / contracts |
| source | VARCHAR | dune / defillama / l2beat |
| query_url_or_file | VARCHAR | Dune query URL 或本地文件路径 |
| last_refreshed_at | TIMESTAMP | 数据抓取时间（ISO-8601） |
| confidence | VARCHAR | high / medium / low |
| notes | VARCHAR | 异常说明、过滤条件、caveat |

---

## Item-2: L2 关键数据对比与赛道格局演变

### 2.1 五链核心指标总览

**数据快照时间**: 2026-05-25/26（多源交叉验证）

#### diag-1: L2 核心指标总览表

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        L2 核心指标总览表 (2026-05-25 snapshot)                                               │
├────────────┬───────────────┬──────────┬──────────────┬──────────┬────────────┬──────────┬──────────────────┤
│ 链         │ TVL (DeFiLlama)│ TVL 份额  │ DAU (24h)    │ 日交易量  │ Avg Fee/tx │ 日收入    │ 数据源/置信度    │
├────────────┼───────────────┼──────────┼──────────────┼──────────┼────────────┼──────────┼──────────────────┤
│ Arbitrum   │ $14.9-16.9B   │ ~40-44%  │ ~132,600     │ ~4.17M   │ $0.08-0.09 │ ~$55K    │ DeFiLlama/L2Beat │
│            │               │          │              │          │            │          │ confidence: high │
├────────────┼───────────────┼──────────┼──────────────┼──────────┼────────────┼──────────┼──────────────────┤
│ Base       │ $10.7-12.8B   │ ~28-33%  │ ~382,500     │ ~12.89M  │ ~$0.05     │ ~$185K   │ DeFiLlama/L2Beat │
│            │               │          │              │          │            │          │ confidence: high │
├────────────┼───────────────┼──────────┼──────────────┼──────────┼────────────┼──────────┼──────────────────┤
│ OP Mainnet │ $1.7-1.91B    │ ~4-5%    │ ~82,000      │ ~422K WAU│ $0.03-0.09 │ N/A      │ DeFiLlama/L2Beat │
│            │               │          │              │          │            │          │ confidence: med  │
├────────────┼───────────────┼──────────┼──────────────┼──────────┼────────────┼──────────┼──────────────────┤
│ Mantle     │ ~$1.15-1.2B   │ ~2-3%    │ 未进入主要排名│ N/A      │ 低         │ N/A      │ DeFiLlama/L2Beat │
│            │               │          │              │          │            │          │ confidence: med  │
├────────────┼───────────────┼──────────┼──────────────┼──────────┼────────────┼──────────┼──────────────────┤
│ zkSync Era │ ~$404M        │ ~1%      │ ~4,000       │ ~19,600  │ ~$0.07     │ 极低     │ DeFiLlama/L2Beat │
│            │               │          │              │          │            │          │ confidence: high │
└────────────┴───────────────┴──────────┴──────────────┴──────────┴────────────┴──────────┴──────────────────┘

数据来源: DefiLlama (https://defillama.com/chains), L2Beat (https://l2beat.com/scaling/activity)
          Token Terminal (https://tokenterminal.com/explorer/metrics/user-dau)
Last refreshed: 2026-05-25/26
⚠️ DAU 使用 active sender addresses，未过滤 bot/spam/系统地址
⚠️ 低费链 (Base, Mantle) 的 tx count 和 DAU 可能因 bot 活动偏高
⚠️ TVL 范围反映 DefiLlama 与 L2Beat 不同口径
```

#### CSV-Ready 图表数据: TVL 对比

```csv
chain,tvl_defillama_usd,tvl_l2beat_usd,market_share_pct,confidence,last_refreshed
Arbitrum,16900000000,14900000000,40-44,high,2026-05-25
Base,12800000000,10700000000,28-33,high,2026-05-25
OP Mainnet,1910000000,1700000000,4-5,medium,2026-05-25
Mantle,1200000000,1150000000,2-3,medium,2026-05-25
zkSync Era,404000000,404000000,1,high,2026-05-25
```

#### CSV-Ready 图表数据: DAU 对比

```csv
chain,dau_24h,daily_tx,avg_fee_usd,daily_revenue_usd,confidence,last_refreshed,caveat
Base,382500,12890000,0.05,185000,high,2026-05-25,includes bot/social protocol traffic
Arbitrum,132600,4170000,0.085,55000,high,2026-05-25,higher-value DeFi interactions
OP Mainnet,82000,422000,0.06,,medium,2026-05-25,WAU figure; DAU estimated
Mantle,,,,,,medium,2026-05-25,not in major DAU rankings
zkSync Era,4000,19600,0.07,,high,2026-05-25,minimal retail activity
```

### 2.2 TVL 趋势分析

**12 个月趋势总结**:

- **Arbitrum**: 维持 L2 TVL 第一，但份额从 2025 年中的 ~55% 下降至 ~40-44%，反映 Base 的快速增长对其构成持续分流。DeFi 基本盘（GMX、Aave、Uniswap）仍然稳固。
- **Base**: 最快速增长的 L2，TVL 从 2025 年中的 ~$5B 增长至 $10.7-12.8B，近 12 个月翻倍以上。Coinbase 分发渠道和 consumer app 生态（Farcaster 等）是核心驱动力。
- **OP Mainnet**: TVL 在 $1.7-1.9B 区间相对稳定，未见显著增长。但 Optimism 的战略重心在 Superchain 生态网络效应而非单链 TVL。
- **Mantle**: TVL 在 2024 年从 $340M 增长至 $2.36B（年末），但 2025-2026 年出现波动。Aave V3（2026-02-11 上线）在 12 天内带入 $290M+ 存款，推动 DeFi TVL 突破 $543M。总 TVL（含桥接）约 $1.15-1.2B。
- **zkSync Era**: DeFi TVL 从 >$1B 暴跌至 ~$36.4M（>96% 下降），但 bridged TVL 仍有 ~$795M，说明用户桥接进入但未使用 DeFi。zkSync 正从零售 DeFi 转向企业/机构定位（Prividium、Elastic Chain）。

**90 天变化**:

Arbitrum 和 Base 继续主导增量流入；zkSync Era 的 DeFi TVL 进一步收缩；Mantle 因 Aave V3 上线获得阶段性提升，但激励驱动 TVL 的粘性是核心风险——"incentive-fueled TVL is historically among the least sticky in DeFi"。

### 2.3 用户活跃度分化

Base 在用户和交易维度的领先是压倒性的：

- Base DAU 约为 Arbitrum 的 3 倍、OP Mainnet 的 4.7 倍、zkSync Era 的 96 倍
- Base 日交易量约为 Arbitrum 的 3 倍
- Base 以 89 TPS（2026-04）领跑所有 Optimistic Rollup

**但 DAU 需谨慎解读**: Base 的高 DAU 中 social protocol（Farcaster 生态）、NFT mint、小额 retail 交易贡献显著比例。Arbitrum 的用户虽然较少，但平均交易价值更高（DeFi 为主）。OP Mainnet 的 DAU 数据较少被单独统计，其战略价值更多体现在 Superchain 网络层面。Mantle 未进入主要 DAU 排名，表明用户基数和链上活跃度相对有限。

### 2.4 L2 市场集中度

Base + Arbitrum + Optimism 处理约 90% 的 L2 交易量，其余 50+ 链分享约 10%。自 2025 年 6 月以来，较小 L2 的使用量下降 61%。Dencun（EIP-4844）的 90% 费用削减引发激烈费用战，推动大多数 Rollup 陷入亏损。分析师预期 L2 整合将围绕三大支柱展开：Ethereum-aligned、高性能、交易所背书。

**数据来源**:
- DefiLlama: https://defillama.com/chains | Last refreshed: 2026-05-25
- L2Beat: https://l2beat.com/scaling/tvl | Last refreshed: 2026-05-25
- L2Beat Activity: https://l2beat.com/scaling/activity | Last refreshed: 2026-05-25
- Token Terminal: https://tokenterminal.com/explorer/metrics/user-dau | Last refreshed: 2026-05-25
- Dune: https://dune.com/jhackworth/i-loves-l2s | Last refreshed: 2026-05-25

**Evidence level**: dashboard-data / industry-data
**Confidence**: high (TVL, Base/Arbitrum DAU), medium (Mantle DAU, OP Mainnet DAU)

---

## Item-3: L2 差异化路线——基础设施网络 vs 应用导向链

### 3.1 赛道演变：从"谁更便宜"到"谁控制入口"

EIP-4844（2024-03）将 L2 费用压缩到 $0.001-0.05 区间后，纯费用竞争失去意义。L2 竞争从"谁更便宜更快"转向"谁控制生态入口、应用场景、开发者网络和发行渠道"。

#### diag-2: L2 赛道演变时间线

```mermaid
timeline
    title Ethereum L2 赛道演变: 通用 Rollup → 差异化定位
    section 2023: 通用 Rollup 扩容竞争
        Arbitrum One 主导 DeFi TVL
        Optimism OP Stack 开源
        zkSync Era mainnet 上线
        Base 依托 Coinbase 快速起步
    section 2024: 费用竞争 → 差异化启动
        2024-03 EIP-4844 Dencun: L2 费用下降 80-90%
        Optimism 启动 Superchain 生态
        Arbitrum Orbit / L3 框架落地
        zkSync ZK Stack + Elastic Chain 方向
        Mantle EigenDA 上线, mETH 增长
        Base 用户和交易量快速超越其他 L2
    section 2025: 生态整合与分层
        Base 成为用户/交易量第一 L2
        Superchain 生态链数量扩张
        Arbitrum Stylus + Timeboost
        zkSync Prividium 企业隐私产品
        Mantle Aave V3 上线, MI4 概念
        RWA 叙事从边缘进入主流
    section 2026: 差异化定位明确
        Base Azul 独立升级 (Flashblocks, Multiproof)
        Optimism op-reth/kona 客户端现代化, FOCIL
        Arbitrum Nitro v3.10, BoLD, consensus v60
        zkSync zkOS + Airbender 原生证明器
        Mantle 探索 RWA/机构转型
        L2 整合: 3 支柱 (Ethereum-aligned, 高性能, 交易所背书)
```

### 3.2 基础设施型路线

#### Optimism Superchain

- **定位**: L2 网络即基础设施，通过 OP Stack 共享安全、互操作和治理
- **网络效应**: 多条 Superchain 成员链（Base、Zora、Mode 等）共享 sequencer 和 interop 协议
- **开发重心**: Superchain interop（94 PRs from core contributors，2026 Q1）、op-reth/kona 客户端现代化、op-contracts v7
- **收入逻辑**: 上游 Stack 采用费而非单链交易费
- **2026 关键**: FOCIL 抗审查机制纳入 Hegota 硬分叉路线图；op-geth 支持截止 2026-05-31

#### Arbitrum Orbit / L3

- **定位**: 应用链框架 + DeFi 流动性引力
- **核心资产**: Nitro（256 PRs/186 merged，3 个月内）+ Stylus（Rust/C++ 智能合约，7 releases）+ Timeboost（MEV 排序，~$2M 额外费用）
- **生态**: Orbit L3 部署、BoLD 挑战协议、consensus v60
- **TVL 优势**: DeFi 基本盘最强（GMX、Aave、Uniswap），$14.9-16.9B
- **2026 关键**: 从 DeFi 流动性中心向 Orbit 生态网络扩张

#### zkSync Elastic Chain / ZK Stack

- **定位**: ZK 原生基础设施网络 + 企业隐私
- **核心投入**: zksync-os-server（404 PRs/238 merged，排名第一）、Airbender 原生证明器、solx-llvm 编译器
- **企业产品**: Prividium（Validium/private DA、SSO、许可管理）、local-prividium（开发沙箱，20 PRs）
- **TVL 困境**: DeFi TVL 暴跌 >96%，retail 活跃度极低（~4,000 DAU）
- **2026 方向**: 放弃零售 DeFi 竞争，转向 ZK 隐私 + 机构结算的高溢价赛道

### 3.3 应用导向型路线

#### Base

- **定位**: Coinbase 分发渠道 + 链上经济入口
- **核心优势**: Coinbase 1.1 亿+ 用户基数、consumer app 分发、支付/资产发行/开发者漏斗
- **产品进展**: Azul 独立升级（2026-05-28）、Flashblocks（200ms 预确认）、Multiproof、Token Factory / PolicyRegistry（B20 预编译）
- **开发强度**: base/base 仓库 1,810 PRs/1,377 merged（3 个月）
- **2026 关键**: 从 OP Stack 分叉实现客户端独立（op-reth），建立自有 identity + policy primitives

#### Mantle

- **定位**: Ethereum-aligned 模块化 L2，yield-bearing 资产驱动
- **核心资产**: MNT（gas/governance）、mETH（LST，~$925M TVL）、cmETH（LRT，~$515M TVL）、FBTC
- **技术栈**: OP Stack based + EigenDA（hybrid DA）+ OP Succinct（ZK rollup 方向）
- **生态**: 180+ dApps，Aave V3、Agni Finance、Merchant Moe
- **2026 方向**: 六大支柱（Mantle Network、mETH、ƒBTC、MI4 机构基金、UR 银行、MantleX AI/DeFi），从 DeFi 向 RWA/机构金融探索

### 3.4 差异化路线对照

#### diag-3: 基础设施型 vs 应用导向型 L2 定位矩阵

```
                       高 ← 生态/Stack 控制 → 低
                 ┌────────────────────────────────────┐
        高       │  Optimism         │                 │
                 │  Superchain       │                 │
        ↑        │  (Stack+Interop   │                 │
        │        │   生态网络)        │                 │
  用户/应用       ├──────────────────┼─────────────────┤
  分发   │       │  Arbitrum         │  Base           │
        │        │  Orbit/Stylus     │  (Coinbase      │
        ↓        │  (DeFi+L3框架)    │   分发+消费者)   │
                 ├──────────────────┼─────────────────┤
        低       │  zkSync           │  Mantle         │
                 │  Elastic/Prividium│  (mETH/DeFi     │
                 │  (ZK隐私+机构)     │   → RWA 探索)   │
                 └────────────────────────────────────┘

                 基础设施网络路线          应用/资产导向路线

指标映射:
- 基础设施型: 生态链数量、Stack adoption、interop、shared security
- 应用导向型: 终端用户、资金流、应用交易、稳定币/RWA/DeFi 活动
```

**数据来源**: 
- 各链竞品研究 final（competitor-base, competitor-arbitrum, competitor-optimism, competitor-zksync）
- 官方 blog / docs / GitHub
- Last refreshed: 2026-05-23/24

**Evidence level**: official-primary (GitHub data), internal-research (competitor finals)
**Confidence**: high

---

## Item-4: DeFi 叙事天花板与监管收紧证据

### 4.1 DeFi 增长约束的数据证据

**全链 DeFi TVL 现状（2026-05）**:
- 全链 DeFi TVL: $92-140B 区间波动（2026 年初 $130-140B → 3 月底 $92.18B → 5 月回升）
- 远低于市场 $250B 预期，增长停滞信号明确
- DeFi 借贷协议存款: $54B（2026-04）
- Aave V3 TVL: $19.4B，占借贷市场 59% 份额，部署在 15+ EVM 链

**结构性问题**:
1. **流动性闲置**: 83-95% 的存入流动性在任何给定时刻处于未使用状态
2. **收益压缩**: 更多资本涌入稳定币 yield 套利，spreads 快速压缩
3. **协议集中**: Aave 以 59% 市场份额高度垄断；头部协议虹吸效应加剧
4. **激励依赖**: "Depositors arrived for the yield, not the product. When emissions slowed or token prices fell, capital fled."
5. **Revenue density 低**: 真实协议收入与锁定资本的比率极低，TVL 作为核心指标的有效性受质疑

**L2 层面的 DeFi 困境**:
- Base DAU 中 social/NFT/小额交易占比高，DeFi 深度不如 Arbitrum
- Mantle Aave V3 上线后快速吸引 $290M+，但粘性存疑
- zkSync Era DeFi TVL 暴跌 >96%，retail DeFi 事实上已放弃
- 竞品普遍减少纯 DeFi 表达，转向 payments、RWA、institutional adoption、consumer apps

### 4.2 监管收紧时间线

#### diag-4: DeFi 天花板与 RWA 机构入场并行时间线

```mermaid
timeline
    title DeFi 增长约束 / 监管事件 / RWA 机构入场并行线
    section 2024: DeFi 增长放缓
        EIP-4844 L2 费用下降 80-90%
        DeFi TVL 在 $80-100B 区间震荡
        收益率持续压缩
        BlackRock BUIDL 上线 (2024-03)
    section 2025 H1: 监管框架成型
        MiCA 生效: compliant by design 要求
        US SEC 加强 DeFi 前端责任审查
        DeFi TVL $130-140B 低于 $250B 预期
        RWA 市场从 ~$6B 起步快速增长
        BUIDL AUM 突破 $2B
    section 2025 H2: 叙事转向明确
        小型 L2 usage 下降 61%
        zkSync DeFi TVL 暴跌 >96%
        Ondo OUSG + USDY 成为 RWA 标杆
        RWA 市场突破 $18.2B (年末)
    section 2026 H1: 机构加速 + 监管落地
        2026-01 JPMD 宣布 Canton 分阶段集成
        2026-02 BUIDL 上线 UniswapX (DeFi 入口)
        2026-03 Ondo-Franklin Templeton 合作 (5 只 ETF tokenization)
        2026-04 FDIC GENIUS Act NPRM (稳定币发行人审慎框架)
        2026-04 Standard Chartered-BlackRock-OKX: BUIDL 作为交易抵押品
        2026-05 BlackRock 新 SEC filing: on-chain shares for $7B MMF
        2026-05 RWA 市场突破 $31-34B
```

### 4.3 DeFi 增长约束证据表

| 约束维度 | 证据 | 数据来源 | 时间 | 置信度 |
|----------|------|----------|------|--------|
| TVL 增长停滞 | $92-140B vs $250B 预期 | DeFiLlama | 2026-Q1 | high |
| 流动性闲置 | 83-95% 存款未使用 | FinTech Weekly 分析 | 2026-03 | medium |
| 收益压缩 | Spread 随资本流入快速压缩 | Portals DeFi Weekly | 2026-03 | medium |
| 协议集中 | Aave 59% 借贷份额 | DeFiLlama | 2026-04 | high |
| 激励退坡 | Blast TVL $2.7B → $55M，DAU 18万→3,800 | L2Beat, CoinBureau | 2026-05 | high |
| L2 整合 | 小型 L2 usage 下降 61% | Industry reports | 2025-06 至今 | medium |
| 监管框架 | MiCA "compliant by design"，GENIUS Act NPRM | Official filings | 2026-04 | high |

### 4.4 DeFi Basic Layer vs Narrative Ceiling 判断框架

DeFi 并非"过时"，而是作为 L2 核心基础设施仍然不可或缺（Aave、Uniswap 是 TVL 和交易的基本盘）。但作为**新增叙事驱动力和机构入口**，DeFi 面临以下边际递减：

1. **增量用户有限**: Base 的 DAU 增长主要来自 consumer/social，非 DeFi 深度用户
2. **机构合规门槛**: MiCA、GENIUS Act 等框架要求 "compliant by design"，传统 DeFi 的匿名/无许可模式难以直接满足
3. **收益竞争力**: 链上 DeFi yield 与传统固收在 Fed 降息环境下差距缩小
4. **叙事空间饱和**: 多条 L2 同时争夺 "DeFi liquidity hub" 定位，叙事区分度下降

**结论**: DeFi 仍是 TVL 和交易的基本盘（defend），但作为新叙事引擎和机构入口已面临天花板（narrative ceiling）。L2 需要在 DeFi 基本盘之上构建新的差异化叙事。

**数据来源**:
- DeFiLlama: https://defillama.com/ | Last refreshed: 2026-05-25
- FinTech Weekly: https://www.fintechweekly.com/magazine/articles/defi-capital-efficiency-tvl-revenue-density-institutional-2026
- Portals.fi: https://www.blog.portals.fi/portals-defi-weekly-27th-march-2026/
- FDIC GENIUS Act NPRM: 2026-04-07 | US Treasury NPRM: 2026-04-08

**Evidence level**: dashboard-data, regulatory-filing, media-reported
**Confidence**: high (TVL, regulatory), medium (yield compression, idle capital)

---

## Item-5: RWA / 机构金融加速的市场证据

> **⚠️ Scope Focus Gate 说明**: 本 item 作为 DeFi → RWA 叙事转向的市场证据，服务于五链 L2 竞争格局分析和 Mantle 定位论证。RWA 案例和数据用作**比较证据**，不单独展开为独立叙事。

### 5.1 RWA 市场总量与增长

| 指标 | 数值 | 来源 | 时间 | 置信度 |
|------|------|------|------|--------|
| 链上 RWA 总市值（不含稳定币） | $31-34B | RWA.xyz | 2026-05 | high |
| YoY 增长 | >200%（从 ~$6B） | RWA.xyz | 2025-01 至 2026-05 | high |
| 美国国债 tokenization | $12.88-15B | RWA.xyz | 2026-04/05 | high |
| 国债占 RWA 总量 | ~45-50% | RWA.xyz | 2026-05 | high |
| 链上公司债 | ~$1.77B | RWA.xyz | 2026-Q1 | medium |
| Ethereum 承载 RWA 占比 | >56% | RWA.xyz | 2026-04 | high |
| McKinsey 2030 预测 | $2T | McKinsey report | 2025 | medium |
| BCG-Ripple 2033 预测 | $18.9T | BCG report | 2025 | low |

### 5.2 关键机构案例（比较证据）

| 机构/产品 | AUM/TVL | 部署链 | 关键里程碑 | 与 L2 的关系 |
|-----------|---------|--------|------------|-------------|
| BlackRock BUIDL | ~$2.5B | ETH, Solana, Polygon, Avalanche, Arbitrum, Optimism, Aptos | 2026-02 上线 UniswapX；2026-04 Standard Chartered 抵押品框架；2026-05 新 SEC filing（$7B MMF on-chain shares） | 多链部署包含 Arbitrum + Optimism；未部署在 Mantle/zkSync/Base |
| Ondo OUSG + USDY | ~$2.5B 总 TVL | ETH, Solana | 2026-03 与 Franklin Templeton 合作 tokenize 5 只 ETF | 暂未部署在主要 L2 |
| Franklin Templeton FOBXX/BENJI | ~$844M | ETH, Stellar, Polygon, Arbitrum, Avalanche, Aptos, Base | 与 Ondo 合作扩展 on-chain 分发 | 已在 Arbitrum + Base |
| Circle ARC | 测试网 244.1M tx；$222M presale | 独立 L1（预计 2026 夏季主网） | a16z, BlackRock, ICE, Standard Chartered 投资；$3B FDV | 独立基础设施，非部署在现有 L2 |

### 5.3 RWA 对 L2 基础设施需求

#### diag-5: RWA / 机构金融对 L2 的能力需求栈

```mermaid
flowchart TB
    subgraph "Application Layer"
        A1[RWA Token 发行/赎回]
        A2[机构资产管理]
        A3[合规交易/二级市场]
    end
    subgraph "Compliance Layer"
        B1[KYC/AML 身份验证]
        B2[Transfer Policy Registry]
        B3[Regulatory Observer/Audit]
        B4[Sanctions Screening]
    end
    subgraph "Privacy Layer"
        C1[Selective Disclosure]
        C2[ZK KYC Proofs]
        C3[Private DA / Validium]
    end
    subgraph "Settlement Layer"
        D1[L2 Finality / Settlement]
        D2[Institutional Custody]
        D3[Cross-chain Bridge]
        D4[Reporting / Reconciliation]
    end

    A1 --> B1
    A1 --> B2
    A2 --> B3
    A3 --> B4
    B1 --> C1
    B1 --> C2
    B3 --> C3
    C1 --> D1
    C2 --> D1
    C3 --> D2
    D1 --> D3
    D2 --> D4
```

**对 L2 的含义**: RWA 机构采用需要 L2 提供的不仅是低费和高吞吐，还包括 identity/KYC、transfer policy、custody、audit、privacy 等合规基础设施。这些能力在当前五条 L2 上均不完整，构成新的竞争维度。

**数据来源**:
- RWA.xyz: https://app.rwa.xyz/ | Last refreshed: 2026-05-25
- CoinDesk: https://www.coindesk.com/business/2026/05/09/blackrock-deepens-tokenization-push-with-new-onchain-fund-offerings
- CryptoTimes: https://www.cryptotimes.io/2026/05/23/blackrock-tokenized-treasury-filings-2026/
- Crypto.news: https://crypto.news/tokenized-real-world-assets-triple-to-34-billion-as-treasuries-and-ethereum-lead/

**Evidence level**: industry-data (RWA.xyz), official-primary (SEC filings), media-reported
**Confidence**: high (AUM/TVL), medium (deployment chain details, adoption metrics)

---

## Item-6: 合规基础设施竞争与 cyberpunk / ToB 分歧

> **⚠️ Scope Focus Gate 说明**: 本 item 聚焦于合规基础设施如何影响 L2 竞争格局，作为五链对比的补充维度。Canton、Arc/Tempo、Prividium 等案例仅作为 L2 能力参照，不展开为独立分析。

### 6.1 合规能力对照（比较证据）

| 能力维度 | Base | Arbitrum | Optimism | zkSync | Mantle | 参照: Canton/Arc |
|----------|------|----------|----------|--------|--------|-----------------|
| KYC/AML | Token Factory 信号(B20) | 无原生支持 | 无原生支持 | Prividium (SSO/Okta) | 无原生支持 | Canton: 原生 KYB；Arc: 核心能力 |
| Transfer Policy | PolicyRegistry (Beryl, 待激活) | 无 | 无 | Prividium permissioning | 无 | Canton: Daml 合约级；Arc: 内置 |
| Privacy | 无 | 无 | 无 | Prividium Validium/private DA | 无 | Canton: need-to-know；Arc: Zones |
| Regulatory Observer | 无 | 无 | 无 | Selective disclosure API | 无 | Canton: 原生 observer role |
| Institutional Custody | Coinbase Custody 集成 | 无原生 | 无原生 | 企业级 | 无原生 | Canton: Participant model |
| Audit/Reporting | 无 | 无 | 无 | Export API + Merkle proofs | 无 | Canton: ACS commitments |

**关键发现**: 在五条主要 L2 中，只有 zkSync 通过 Prividium 提供了 workflow-level 的合规基础设施。Base 通过 Token Factory / PolicyRegistry 展示了合规资产发行的信号（但仍在 Beryl 激活门后）。Arbitrum、Optimism、Mantle 均无原生合规基础设施。Canton 和 Arc 作为专用合规网络，在合规能力上远超公链 L2，但缺乏 EVM 兼容性和 DeFi 可组合性。

### 6.2 Vitalik cypherpunk 方向 vs ToB 转向

**Vitalik 2026 cypherpunk 宣言**（2026-02-22，柏林）:
- 发表 "Reclaiming the Cypherpunk Soul of the World Computer" 宣言
- 核心立场: crypto 过度关注金融投机和机构合规，忽视了隐私、抗审查、去中心化的原始使命
- 技术路线: ZK-SNARKs + 隐私池 → "privacy by default"；FOCIL → 抗审查
- FOCIL: 随机选择 validator committee 强制包含所有有效交易，包括违反 OFAC 制裁的交易
- FOCIL 已确认纳入 Hegota 硬分叉（2026 年底）

**行业 ToB 转向的现实**:
- Canton: $368B 日吞吐量（Broadridge DLR 回购平台）；DTCC 2026 H1 tokenized US Treasuries 生产 MVP
- Arc (Circle): $222M presale，BlackRock/Standard Chartered 投资，$3B FDV
- Tempo: Visa 验证节点（2026-04-14）
- zkSync Prividium: enterprise 许可/隐私/审计

#### diag-6: Cyberpunk vs ToB 张力矩阵

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│              Cyberpunk / CR / Privacy  vs  ToB / KYC-AML / Permissioned          │
├─────────────────────┬──────────────────────────┬──────────────────────────────────┤
│ 维度                │ Cypherpunk 路线           │ ToB / Institutional 路线         │
├─────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ 隐私               │ Privacy by default        │ Selective disclosure             │
│                     │ ZK-SNARKs, privacy pools  │ Need-to-know, permissioned DA   │
├─────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ 审查抵抗           │ FOCIL: 强制包含所有交易    │ Sanctions screening, OFAC 合规   │
│                     │ 包括违反制裁的交易         │ Transfer restrictions            │
├─────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ 身份               │ 匿名优先                  │ KYC/KYB 强制                    │
│                     │ Account abstraction        │ Okta/SIWE/identity attestation  │
├─────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ 收益               │ Credible neutrality        │ 机构信任, 监管接受               │
│                     │ 最大化去中心化             │ 传统资本入场                     │
│                     │ 抗国家级审查               │ 合规产品化, 大规模 AUM           │
├─────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ 风险               │ 监管对抗, 合规成本         │ 可组合性损失, 中心化风险          │
│                     │ 机构资本排斥               │ 用户隐私让渡, cypherpunk 社区反对 │
├─────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ 适配场景           │ 公共 DeFi, 社交应用        │ RWA, 机构结算, 支付              │
│                     │ 隐私保护应用               │ 企业工作流, 合规资产管理          │
├─────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ L2 代表            │ Ethereum L1 roadmap        │ zkSync Prividium, Canton         │
│                     │ OP Mainnet (FOCIL)         │ Arc/Tempo, Base Token Factory    │
├─────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ 对 Mantle 的含义    │ 保持 public L2 中立性      │ RWA/机构叙事需要合规能力          │
│                     │ 不牺牲 permissionless      │ 可在 L3/appchain 层实现           │
│                     │ 符合 Ethereum alignment    │ 合规产品作为差异化而非替代公链     │
└─────────────────────┴──────────────────────────┴──────────────────────────────────┘
```

**对 Mantle 的关键含义**: Mantle 若进入 RWA / 机构金融叙事，需要在 Ethereum-aligned / permissionless 的公链身份与 institutional-ready / compliance 能力之间找到平衡。参照 enterprise-privacy 研究的建议，最佳路径是：公共 L2 保持中立结算层，合规/隐私能力通过 L3/Validium/appchain 层实现，避免在公链层面引入许可机制。

**数据来源**:
- Vitalik 宣言: 2026-02-22 | https://coingenius.news/vitalik-buterin-advocates-cypherpunk-revival-for-2026/
- enterprise-canton final: competitor research | Last refreshed: 2026-05-22
- enterprise-privacy final: competitor research | Last refreshed: 2026-05-22

**Evidence level**: expert-commentary (Vitalik), official-primary (Canton, Prividium docs), internal-research
**Confidence**: high (Vitalik position, Prividium capabilities), medium (adoption maturity)

---

## Item-7: Mantle 技术栈、生态定位与转型背景

### 7.1 技术栈现状

| 组件 | 现状 | 说明 |
|------|------|------|
| 执行层 | OP Stack based | Ethereum-aligned，与 upstream OP Stack 保持兼容 |
| 数据可用性 | EigenDA (hybrid) | 降低成本但引入额外信任假设，安全性低于 Ethereum blob DA |
| 结算 | Ethereum L1 | 标准 Rollup 结算 |
| Sequencer | 中心化 sequencer | 标准 L2 模式 |
| 证明系统 | 计划引入 OP Succinct (ZK) | 从 optimistic 向 ZK 验证过渡 |
| 桥 | 标准 L2 bridge | canonical bridge + 第三方桥 (Stargate 等) |

### 7.2 生态资产地图

#### diag-7: Mantle 现有资产与能力地图

```mermaid
graph TB
    subgraph "Core Assets"
        MNT[MNT<br/>Gas + Governance]
        mETH[mETH<br/>LST, ~$925M TVL<br/>4th largest ETH LST]
        cmETH[cmETH<br/>LRT, ~$515M TVL<br/>5th in ETH staking]
        FBTC[ƒBTC<br/>Bitcoin yield asset]
    end

    subgraph "DeFi Ecosystem"
        AAVE[Aave V3<br/>$290M+ deposits<br/>2026-02-11 launch]
        DEX[DEXs: Agni, Merchant Moe<br/>~$117M TVL combined]
        LENDING[Lending: INIT Capital<br/>$21M TVL]
        YIELD[Yield: Pendle, Stargate<br/>$28M TVL]
    end

    subgraph "New Pillars (Planned/Early)"
        MI4[MI4<br/>Institutional Crypto Fund]
        UR[UR<br/>Integrated Banking]
        MantleX[MantleX<br/>AI for DeFi]
    end

    subgraph "Infrastructure"
        OPStack[OP Stack<br/>Execution Layer]
        EigenDA[EigenDA<br/>Data Availability]
        OPSuccinct[OP Succinct<br/>ZK Proof (planned)]
    end

    subgraph "GAP: Compliance/RWA"
        style GAP fill:#ff6b6b,color:#fff
        GAP[❌ KYC/AML<br/>❌ Transfer Policy<br/>❌ Privacy/Selective Disclosure<br/>❌ Institutional Custody (native)<br/>❌ Regulatory Observer<br/>❌ Audit API]
    end

    MNT --> OPStack
    mETH --> AAVE
    mETH --> DEX
    cmETH --> YIELD
    FBTC --> LENDING
    OPStack --> EigenDA
    EigenDA --> OPSuccinct

    MI4 -.-> GAP
    UR -.-> GAP
```

### 7.3 转型背景

**从 mETH/DeFi 到 RWA 探索的逻辑**:

1. **mETH 成功但边际递减**: mETH 已是第 4 大 ETH LST（~$925M），cmETH 第 5 位（~$515M），在 yield-bearing 资产赛道建立了位置。但 LST 市场已高度成熟，增量空间有限。
2. **DeFi 依赖激励**: Aave V3 上线后快速吸引 $290M+，但"激励驱动的 TVL 是 DeFi 中粘性最低的"。激励退坡后的资金留存是核心风险。
3. **六大支柱愿景**: Mantle Network + mETH + ƒBTC（已有）+ MI4（机构基金）+ UR（银行集成）+ MantleX（AI/DeFi）——后三者指向机构/金融方向，但均处于早期。
4. **竞品差异化明确**: Base 有 Coinbase 分发，Arbitrum 有 DeFi/Orbit/Stylus，Optimism 有 Superchain，zkSync 有 ZK/Elastic/Prividium。Mantle 需要找到可差异化的证据。

### 7.4 与竞品差异矩阵

| 差异化维度 | Base | Arbitrum | Optimism | zkSync | Mantle |
|-----------|------|----------|----------|--------|--------|
| 分发渠道 | Coinbase 1.1亿用户 | DeFi 生态自增长 | Superchain 生态 | ZK 技术叙事 | mETH/MNT 社区 |
| 技术独特性 | Flashblocks, Multiproof | Stylus, Timeboost | Superchain interop | ZK 原生, Airbender | EigenDA (modular DA) |
| 机构能力 | Token Factory/PolicyRegistry | 无 | 无 | Prividium | 无 (MI4 计划中) |
| Yield 资产 | 弱 | 弱 | 弱 | 弱 | mETH/cmETH/FBTC (强) |
| 开发者生态 | 1,810 PRs/3m (高) | 256 PRs Nitro/3m (高) | 1,202 PRs monorepo/3m (高) | 1,427 PRs/3m (高) | 未量化 |

**Mantle 可差异化证据**: Yield-bearing asset base（mETH/cmETH）是当前唯一明确的差异化优势。技术栈（OP Stack + EigenDA）不独特。进入 RWA/机构叙事需要补齐合规/隐私/identity 能力。

**数据来源**:
- Mantle official: https://www.mantle.xyz/blog/ecosystem/from-meth-to-cmeth-whats-cookin
- CoinBureau: https://coinbureau.com/review/mantle-network-review
- OAK Research: https://oakresearch.io/en/reports/protocols/mantle-mnt-comprehensive-overview-full-stack-on-chain-banking-infrastructure
- Competitor research finals | Last refreshed: 2026-05-23/24

**Evidence level**: official-primary, industry-data, internal-research
**Confidence**: high (tech stack, existing assets), medium (planned pillars)

---

## Item-8: Mantle 活跃度下降与生态健康度诊断

### 8.1 Mantle 链上指标趋势

#### diag-8: Mantle 生态健康度 Dashboard

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                    Mantle 生态健康度 Dashboard (2026-05-25)                                │
├────────────────┬──────────────────┬───────────────┬──────────────┬───────────────────────┤
│ 指标           │ 当前值            │ 12m 前 (~)     │ 90d 变化     │ 备注/异常              │
├────────────────┼──────────────────┼───────────────┼──────────────┼───────────────────────┤
│ TVL (L2Beat)   │ ~$1.15-1.2B      │ ~$2.36B (峰值) │ ↑ Aave 效应  │ Aave V3 2026-02 推升   │
│ DeFi TVL       │ ~$543M           │ N/A           │ ↑ 显著       │ Aave $290M+ 快速流入   │
│ DAU            │ 未进入排名        │ N/A           │ N/A          │ 主流 dashboard 未展示   │
│ 日交易量       │ N/A              │ N/A           │ N/A          │ 缺乏公开可比数据       │
│ mETH TVL       │ ~$925M (1.6B协议)│ 增长中         │ 稳定/增长    │ 4th largest ETH LST   │
│ cmETH TVL      │ ~$515M           │ 新产品         │ 增长         │ 5th in ETH staking    │
│ mETH 持有人    │ 9,949 (L1)       │ 增长           │ N/A          │ L2: 163,934 holders   │
│               │ 163,934 (L2)     │               │              │                       │
│ DEX TVL        │ ~$117M (Agni+MM) │ N/A           │ N/A          │ Merchant Moe + Agni   │
│ Bridge Flow    │ N/A              │ N/A           │ N/A          │ 缺乏公开数据           │
│ 合约部署       │ N/A              │ N/A           │ N/A          │ 未在公开 dashboard 展示│
│ Gas/Fees       │ 低               │ 低            │ N/A          │ EigenDA 降低 DA 成本   │
└────────────────┴──────────────────┴───────────────┴──────────────┴───────────────────────┘

⚠️ Mantle 的 DAU、交易量、合约部署等活跃度指标在主流分析工具中缺乏可比数据
⚠️ TVL 从 2024 年末峰值 $2.36B 回落至 ~$1.15-1.2B，部分因资产价格波动
⚠️ Aave V3 带来的 TVL 增长可能受激励退坡影响
```

### 8.2 与五条 L2 90 天变化对照

| 链 | TVL 90d 趋势 | DAU 90d 趋势 | 交易量 90d 趋势 | 整体判断 |
|----|-------------|-------------|----------------|---------|
| Base | ↑ 持续增长 | ↑ 持续增长 | ↑ 持续增长 | 全面领先 |
| Arbitrum | → 稳定 | → 稳定 | → 稳定 | DeFi 基本盘稳固 |
| OP Mainnet | → 稳定 | → 稳定 | → 稳定 | Superchain 价值在网络层 |
| Mantle | ↑ Aave 效应 | ? 数据不足 | ? 数据不足 | TVL 短期提升，粘性存疑 |
| zkSync Era | ↓ DeFi 萎缩 | ↓ 持续下降 | ↓ 持续下降 | 转型企业/机构定位 |

### 8.3 下降原因假设与诊断

| 假设 | 证据强度 | 说明 |
|------|---------|------|
| 激励退坡 | **高** | 历史数据显示激励驱动 TVL 粘性最低；Blast 案例 ($2.7B → $55M) 为极端参照 |
| 市场整体降温 | **中** | DeFi 全链 TVL 波动，但 Base/Arbitrum 未见同比例下降 |
| 竞品吸流 | **中** | Base 用户和交易量快速增长，可能从 Mantle 等较小 L2 分流 |
| 叙事疲劳 | **中** | mETH/DeFi 叙事空间饱和，MI4/UR/MantleX 尚未产出实质成果 |
| 应用不足 | **中** | 180+ dApps 但头部协议集中（Aave + DEX 占 DeFi TVL 大部分） |
| 开发者减少 | **低** | 缺乏 Mantle GitHub 活跃度的公开量化数据 |
| 数据口径变化 | **中** | TVL 从峰值 $2.36B 回落部分因资产价格波动（MNT/ETH 价格影响 mETH 计价 TVL） |

### 8.4 诊断结论

Mantle 的情况更准确地描述为**"相对竞争压力 + 激励依赖风险"**而非简单的"活跃度下降"：

1. **TVL 绝对值有所回落**（从 $2.36B 峰值），但 Aave V3 上线后 DeFi TVL 恢复增长至 $543M+
2. **用户活跃度数据不足**，无法确定是绝对下降还是数据覆盖问题
3. **相对于 Base/Arbitrum 的差距在扩大**：Base 的 DAU/tx 领先优势加速拉开
4. **mETH/cmETH 资产底座仍在增长**：作为 yield-bearing 资产的差异化优势保持
5. **核心风险是叙事转型的空窗期**：mETH/DeFi 边际递减，MI4/RWA 尚未落地

**⚠️ Caveat**: 如果数据不支持"活跃度下降"的结论，应改写为"结构变化"或"相对竞争压力"。当前数据更支持后者。

**数据来源**:
- DefiLlama: https://defillama.com/chain/mantle | Last refreshed: 2026-05-25
- BanklessTimes: https://www.banklesstimes.com/articles/2026/03/11/the-aave-effect-mantle-crosses-1b-tvl-in-under-two-weeks/
- L2Beat: https://l2beat.com/scaling/tvl | Last refreshed: 2026-05-25

**Evidence level**: dashboard-data, media-reported
**Confidence**: medium (TVL trends), low (DAU/activity due to data gaps)

---

## Item-9: 下一叙事点必要性与内部分享结论框架

### 9.1 论证链

#### diag-9: 内部分享结论链

```mermaid
flowchart LR
    A[L2 赛道分化<br/>73 rollups, 3 链占 90%] --> B[DeFi 叙事<br/>边际递减<br/>TVL $92-140B<br/>远低预期]
    B --> C[RWA/机构金融<br/>加速<br/>$31-34B, >200% YoY]
    C --> D[合规基础设施<br/>成为差异化<br/>zkSync/Canton 领先]
    D --> E[Mantle 需要<br/>新叙事证据<br/>mETH→RWA/机构]

    style A fill:#4a90d9,color:#fff
    style B fill:#d9534f,color:#fff
    style C fill:#5cb85c,color:#fff
    style D fill:#f0ad4e,color:#fff
    style E fill:#9b59b6,color:#fff
```

### 9.2 五个 Slide-Ready 结论

**Slide 1: L2 赛道从通用扩容进入差异化竞争**
- 主 Claim: 73 条 Rollup、$48B TVL，但 Base + Arbitrum 占 77%；差异化定位（Stack 网络 / 分发渠道 / ZK 隐私 / yield 资产）取代纯费用竞争
- 证据: TVL 份额对比、DAU/tx 集中度数据
- 图表: diag-1 核心指标总览、diag-3 定位矩阵

**Slide 2: DeFi 仍是基本盘，但作为新叙事引擎面临天花板**
- 主 Claim: DeFi TVL $92-140B 远低于 $250B 预期；83-95% 流动性闲置；Aave 59% 份额垄断；激励退坡 → 资金流出
- 证据: 全链 DeFi TVL、Blast 崩塌案例、yield 压缩数据
- 图表: DeFi 增长约束证据表
- Caveat: DeFi 仍是交易和 TVL 基础，不应被简单否定

**Slide 3: RWA / 机构金融是增速最快的链上叙事**
- 主 Claim: 链上 RWA 从 $6B → $34B（>200% YoY）；BlackRock BUIDL $2.5B、Ondo $2.5B、Franklin Templeton $844M；美国国债 tokenization 突破 $15B
- 证据: RWA.xyz 市场数据、机构案例表
- 图表: diag-4 DeFi/RWA 并行时间线、diag-5 RWA 能力需求栈
- Caveat: RWA 增长可能慢且合规复杂；机构采用 ≠ 公链活跃

**Slide 4: 合规基础设施正在重塑 L2 竞争维度**
- 主 Claim: KYC/AML、transfer policy、privacy、custody、audit 能力成为 RWA/机构采用的前置条件；zkSync Prividium 和 Base Token Factory 率先布局；Mantle 在此维度空白
- 证据: 合规能力对照表、Canton/Arc 参照
- 图表: diag-6 cyberpunk vs ToB 张力矩阵
- Caveat: Vitalik cypherpunk 方向与 ToB 转向存在张力；合规不应牺牲 public L2 的中立性

**Slide 5: Mantle 需要新叙事——从 mETH/DeFi 基本盘出发的 RWA/机构探索**
- 主 Claim: mETH/cmETH yield 资产底座是差异化优势；TVL 受激励依赖风险；MI4/UR/MantleX 指向机构方向但需要工程和生态支撑；合规/隐私/identity 基础设施是 gap
- 证据: Mantle 生态数据、能力 gap list、与竞品对照
- 图表: diag-7 Mantle asset-capability map、diag-8 健康度 dashboard
- Caveat: 不得夸大 RWA 机会或低估 DeFi 基本盘

### 9.3 反论点

| 反论点 | 评估 | 应对 |
|--------|------|------|
| DeFi 仍是基本盘 | **成立** | 不否定 DeFi，而是论证 DeFi 作为**新增叙事和机构入口**面临天花板 |
| RWA 增长慢且合规复杂 | **部分成立** | RWA >200% YoY 增长事实驳斥"增长慢"，但合规复杂性是真实挑战 |
| 机构采用 ≠ 公链活跃 | **成立** | BUIDL 在多链部署但 DeFi 使用有限；需区分"合规资产发行"和"链上活跃度" |
| Base/Arc/Canton 已占据心智 | **部分成立** | 竞争窗口存在但在收窄；Mantle 的 yield-bearing 资产底座是差异化切入点 |
| Mantle 缺乏合规能力 | **成立** | 需要明确 roadmap：短期 compliance RPC + KYC registry → 中期 private DA / audit API → 长期企业 L3/Validium |

### 9.4 必要前置条件

| 条件 | 优先级 | 说明 |
|------|--------|------|
| 合规基础设施原型 | P0 | Compliance RPC gateway, KYC registry, sequencer policy engine |
| 机构合作伙伴 | P0 | RWA issuer (Ondo/Securitize 等), institutional custody partner |
| Identity / Privacy 原语 | P1 | ZK KYC proofs, selective disclosure, audit log exporter |
| 开发者工具 | P1 | RWA token template, compliance middleware SDK |
| 数据改善 | P1 | 改善 Mantle 在 Dune/L2Beat/Token Terminal 的数据覆盖和可见度 |
| RWA/Payments Pilot | P2 | 具体的 tokenized asset 发行或支付结算试点 |

---

## Item-10: 风险、开放问题与事实核验清单

### 10.1 Dune 数据可得性

| 问题 | 影响 | 处理 |
|------|------|------|
| zkSync / Mantle schema 差异 | 查询模板需要按链适配 | 每个查询标注适用链和 schema |
| 系统地址过滤 | DAU 可能偏高 | 维护排除地址列表，标注 caveat |
| Internal transaction 覆盖 | Mantle traces 表可能不完整 | DAU 使用 transaction-level from |
| 合约创建识别 | creation_traces 表覆盖可能不一致 | 交叉验证 verified contracts |
| 索引延迟 | 最新数据可能有 24-48h 延迟 | 标注 last_refreshed_at |

### 10.2 TVL 口径

| 口径 | DefiLlama | L2Beat | 差异原因 |
|------|-----------|--------|----------|
| 定义 | DeFi 协议锁定值 | Total Value Locked (canonical + external + native) | L2Beat 包含桥接资产 |
| Mantle 差异 | ~$543M DeFi TVL | ~$1.15-1.2B TVL | L2Beat 包含 mETH/cmETH 桥接价值 |
| 价格影响 | USD 计价受资产价格波动 | 同 | MNT/ETH 价格变化影响 TVL |

### 10.3 地址与交易

- Active address ≠ 真实用户: 一个用户可能有多个地址，一个地址可能是 bot
- 低费链 bot 风险: Base 的高 DAU 中 social protocol / MEV bot 贡献显著
- 交易笔数 ≠ 经济价值: Base 12.89M 日交易量包含大量小额/社交交易
- MEV 交易: Base/Optimism >50% gas 被 optimistic MEV 消耗，但仅贡献 <25% 费用

### 10.4 开发者 Proxy

- 合约部署数: 受 factory contract 批量部署、测试合约、spam 影响
- Verified contracts: 仅反映选择验证的合约，低估真实部署量
- GitHub activity: 本研究中 Mantle 的 GitHub 活跃度未被量化，构成数据 gap

### 10.5 RWA 事实边界

- AUM / TVL / Token Supply: 三个数字可能不同，需明确使用的口径
- Onchain liquidity ≠ AUM: BUIDL $2.5B AUM 不等于 $2.5B 链上可交易流动性
- 合作公告 ≠ 生产部署: JPMD Canton 集成宣布 2026-01 但"尚未上线"；Arc 预计 2026 夏季主网
- Permissioned transfer: 许多 RWA token 有 transfer restriction，不参与 DeFi 可组合性
- 机构数量冲突: Canton 报告的机构数量在不同来源间有冲突（400/450/600）

### 10.6 监管与观点

- Vitalik 观点必须保留上下文: 2026-02-22 宣言是在 cypherpunk/privacy 框架下发表的，不应被断章取义为"反对机构采用"
- 政策解读: MiCA、GENIUS Act 等解读需标注条文来源和生效时间
- OFAC / FOCIL: FOCIL 强制包含违反制裁交易的立场是 Ethereum 社区内部争议，不应简单等同于"Ethereum 支持违反制裁"

### 10.7 Mantle 结论约束

- 若 DAU/活跃度数据不支持"下降"结论，应使用"相对竞争压力"或"数据可见度不足"
- 不得为叙事需求强行下"活跃度下降"结论——当前数据更支持"TVL 从峰值回落 + 结构转型期"
- RWA/机构方向是"探索方向"而非"已验证策略"——MI4/UR/MantleX 均处于早期
- mETH/DeFi 基本盘不应被贬低为"过时"——仍是 Mantle 最大的差异化资产

---

## Source Coverage

### src-1: on_chain_data (Dune Analytics)

| 状态 | 说明 |
|------|------|
| **Partial** | 提供了 5 个 DuneSQL 查询模板（DAU、tx count、gas/fees、new contracts、active contracts），覆盖所有 5 条链。查询为模板形式，需实际执行获取数据。未提供已执行查询的 Dune URL（因 Dune 需登录执行）。 |

**Gap**: 需要实际执行查询并获取 Dune query permalink。当前提供的是可复现的 DuneSQL 代码，满足"reproducible query artifacts"要求，但缺少已执行查询的 URL。

### src-2: industry_data (DefiLlama, L2Beat, RWA.xyz, Token Terminal)

| 来源 | 覆盖 | 状态 |
|------|------|------|
| DefiLlama | TVL, DeFi TVL, protocol breakdown | ✅ Met |
| L2Beat | TVL/TVS, activity (TPS, DAU) | ✅ Met |
| RWA.xyz | RWA market size, Treasury tokenization, BUIDL/OUSG data | ✅ Met |
| Token Terminal | DAU, revenue | ✅ Met |

### src-3: official_docs

| 链/项目 | 覆盖 | 状态 |
|---------|------|------|
| Base | Azul blog, Flashblocks, Token Factory/PolicyRegistry signals | ✅ |
| Arbitrum | Nitro releases, Stylus, Timeboost, Orbit | ✅ |
| Optimism | Superchain interop, op-reth/kona, FOCIL | ✅ |
| zkSync | Prividium, Elastic Chain, Airbender, zkOS | ✅ |
| Mantle | mETH, cmETH, EigenDA, MI4/UR/MantleX | ✅ |
| Canton | Need-to-know privacy, DvP, Daml | ✅ (comparative) |
| Arc/Tempo | Circle ARC, Visa/Tempo | ✅ (comparative) |
| Vitalik/EF | Cypherpunk essay, FOCIL | ✅ |

**状态**: ✅ Met (8+ sources)

### src-4: regulatory_filing

| 文件 | 覆盖 | 状态 |
|------|------|------|
| BlackRock BUIDL SEC filings | 2026-05 new filing for $7B MMF on-chain shares | ✅ |
| FDIC GENIUS Act NPRM | 2026-04-07 | ✅ |
| US Treasury GENIUS Act NPRM | 2026-04-08 | ✅ |
| Ondo/Securitize | Product page and issuer disclosure references | ✅ |

**状态**: ✅ Met (3+ sources)

### src-5: media_reports

| 来源 | 覆盖文章 |
|------|---------|
| CoinDesk | BlackRock tokenization push |
| The Block | 2026 L2 outlook |
| CoinBureau | L2 comparison, Mantle review |
| Crypto.news | RWA market $34B |
| BanklessTimes | Mantle Aave effect |
| FinTech Weekly | DeFi capital efficiency |
| Yellow.com | Ethereum fee revenue, RWA growth |
| CCN | Vitalik cypherpunk, BUIDL guide |

**状态**: ✅ Met (6+ sources)

### src-6: expert_commentary

| 来源 | 覆盖 |
|------|------|
| Vitalik 2026-02-22 cypherpunk essay | ✅ 核心 privacy/CR 观点 |
| Vitalik FOCIL position | ✅ 抗审查技术路线 |
| Ethereum Foundation 2026 priorities | ✅ scalability, hardening, simplification |
| Sandy Kaul (Franklin Templeton) | ✅ tokenization / $30T ETF market |

**状态**: ✅ Met (3+ sources)

### src-7: internal_research

| 研究 | 覆盖 | 复用方式 |
|------|------|---------|
| competitor-base final | ✅ | GitHub activity, Azul/Flashblocks |
| competitor-arbitrum final | ✅ | Nitro/Stylus/Orbit data |
| competitor-optimism final | ✅ | Superchain/interop/client stack |
| competitor-zksync final | ✅ | Prividium/Airbender/enterprise |
| narrative-analysis final | ✅ | DeFi ceiling, RWA acceleration, cyberpunk tension |
| enterprise-canton final | ✅ | Canton capabilities (comparative) |
| enterprise-privacy final | ✅ | Prividium, privacy infrastructure (comparative) |

**状态**: ✅ Met (5+ sources)

### src-8: code_or_developer_data

| 来源 | 覆盖 | 状态 |
|------|------|------|
| GitHub org activity (Base, Arbitrum, Optimism, zkSync) | ✅ PR/merge data from competitor finals | Partial |
| Mantle GitHub activity | ❌ 未量化 | Gap |
| Contract deployment data | ✅ Query template provided | Partial |

**状态**: Partial (Mantle GitHub activity 未量化)

---

## Gap Analysis

| Gap ID | 描述 | 影响 | 严重度 | 可能解决路径 |
|--------|------|------|--------|-------------|
| GAP-1 | Dune 查询为模板形式，未提供已执行查询的 permalink URL | 降低可复核性，但查询代码可复现 | Medium | 实际执行查询并记录 Dune URL |
| GAP-2 | Mantle DAU / 日交易量 / 合约部署缺乏公开可比数据 | 无法精确判断 Mantle 活跃度绝对水平和趋势 | Medium | 使用 Dune Q1-Q5 查询获取 Mantle 数据，或联系 Mantle 团队获取内部 dashboard |
| GAP-3 | Mantle GitHub 活跃度未量化 | 无法与竞品进行开发者维度对比 | Low | 对 mantlenetworkio / mETH 相关 GitHub org 执行类似竞品研究的 PR/commit 分析 |
| GAP-4 | OP Mainnet DAU 数据精度较低 | OP Mainnet 在活跃度维度的比较不够精确 | Low | 使用 Dune Q1 查询获取 Optimism DAU |
| GAP-5 | RWA 产品在各 L2 的具体部署和使用数据有限 | 无法精确判断哪些 L2 正在获得 RWA 流量 | Low | 查询 RWA.xyz 的 chain breakdown 数据 |
| GAP-6 | 12 个月历史 TVL/DAU/tx 趋势的日频数据未实际拉取 | 图表依赖 dashboard 快照而非自有时间序列 | Medium | 执行 Dune 查询获取 12m 日频数据，或使用 DefiLlama API |

---

## Revision Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
| 1 | Initial draft | All items (1-10) | Orchestrator dispatch: deep-draft round 1 | Dispatch cb2286d6 |
