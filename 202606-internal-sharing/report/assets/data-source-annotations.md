# 数据来源标注表 — Mantle 竞争格局与叙事方向分析

> **用途**: 为 final-report.md 和 slides-outline.md 中引用的所有关键数据提供来源追溯，供 GPT 复核数据可信度。
>
> **标注格式**: 数据点 → 研究 Section 来源 → 原始数据源 → 可信度等级 → 备注/Caveat
>
> **可信度等级**: `verified-primary`（官方一手数据/API）| `verified-data`（第三方数据平台）| `industry-report`（行业报告）| `vendor-claimed`（供应商声称）| `secondary`（二手引用）| `inferred`（研究推断）| `unverified`（未验证）

---

## Chapter 1: 当前市场现状分析

### 1.1 L2 赛道格局数据

| # | 数据点 | 报告引用 | 研究 Section | 原始数据源 | 快照时间 | 可信度 | Caveat |
|---|--------|---------|-------------|-----------|---------|--------|--------|
| 1 | Base TVL $4.47B, 六链份额 67.0% | slides Slide 3 | Slide 3 数据重建 | DefiLlama API: `GET /v2/historicalChainTvl/Base` → 每日 TVL 365 天时序 → CSV `data/slide3-tvl-daily.csv` | 2026-05-26 | `verified-data` | DefiLlama DeFi 协议锁仓值口径；六链份额非全 L2 份额（全 L2 TVL ~$7.9B，见 L2Beat） |
| 2 | Arbitrum TVL $1.51B, 六链份额 22.7% | slides Slide 3 | Slide 3 数据重建 | DefiLlama API: `GET /v2/historicalChainTvl/Arbitrum` | 2026-05-26 | `verified-data` | 同上；YoY -34.3% |
| 3 | OP Mainnet TVL $342M, 六链份额 5.1% | slides Slide 3 | Slide 3 数据重建 | DefiLlama API: `GET /v2/historicalChainTvl/Optimism`（返回名为 "OP Mainnet"）| 2026-05-26 | `verified-data` | |
| 4 | Mantle TVL $232M, 六链份额 3.5% | slides Slide 3, 5 | Slide 3 数据重建 | DefiLlama API: `GET /v2/historicalChainTvl/Mantle` | 2026-05-26 | `verified-data` | DefiLlama DeFi 口径；YoY +2.1%；Feb 2026 异常峰值 $648M（Aave V3 激励驱动） |
| 5 | zkSync Era TVL $18M, 六链份额 0.3% | slides Slide 3 | Slide 3 数据重建 | DefiLlama API: `GET /v2/historicalChainTvl/zkSync Era` | 2026-05-26 | `verified-data` | YoY -61.4% |
| 5b | X Layer TVL $93M, 六链份额 1.4% | slides Slide 3 | Slide 3 数据重建 | DefiLlama API: `GET /v2/historicalChainTvl/X Layer` | 2026-05-26 | `verified-data` | YoY 大幅增长（2025-06 仅 $5.7M） |
| 6 | Base DAU ~435K（May 2026 日均）, 五链份额 72.6% | slides Slide 3 | Slide 3 数据重建 | Dune Analytics query #7586359: `SELECT block_date, blockchain, approx_distinct("from") AS dau FROM evms.transactions` → CSV `data/slide3-dau-daily.csv` | 2026-05-26 | `verified-data` | `approx_distinct` 使用 HyperLogLog，~2% 误差；sender-based，含 bot；X Layer 不在 `evms.transactions` 覆盖范围 |
| 7 | Arbitrum DAU ~140K（May 2026 日均）, 五链份额 23.3% | slides Slide 3 | Slide 3 数据重建 | Dune Analytics query #7586359 同上 | 2026-05-26 | `verified-data` | YoY -56.6% |
| 8 | OP Mainnet DAU ~16K（May 2026 日均）, 五链份额 2.7% | slides Slide 3 | Slide 3 数据重建 | Dune Analytics query #7586359 同上 | 2026-05-26 | `verified-data` | YoY -84.5% |
| 9 | Mantle DAU ~1.6K（May 2026 日均）, 五链份额 0.3% | slides Slide 3, 5 | Slide 3 数据重建 | Dune Analytics query #7586359 同上 | 2026-05-26 | `verified-data` | YoY -81.0%；与 Nansen Q1 季报 ~2,276 一致 |
| 10 | zkSync Era DAU ~6K（May 2026 日均）, 五链份额 1.0% | slides Slide 3 | Slide 3 数据重建 | Dune Analytics query #7586359 同上 | 2026-05-26 | `verified-data` | YoY -31.6%（降幅最小） |
| 10b | X Layer DAU: 数据不可用 | slides Slide 3 | Slide 3 数据重建 | Dune `evms.transactions` 不覆盖 xlayer；Blockscout API 无链级 DAU | 2026-05-26 | — | **数据缺口**：无可用公开 DAU 数据源 |
| 11 | Base + Arbitrum 六链 TVL 合计 89.7% | slides Slide 3 | Slide 3 数据重建 | 由 DefiLlama TVL 数据计算：($4.47B + $1.51B) / $6.67B | 2026-05-26 | `verified-data` | 六链内部份额，非全 L2 市场份额 |
| 12 | 73 条活跃 Rollup 合计 >$48B TVL | final-report L39 | `market-landscape/final.md` Executive Summary | L2Beat: https://l2beat.com/scaling/tvl | 2026-05-25 | `verified-data` | |
| 13 | 全行业 DAU 大幅下降（2025-06 至 2026-05） | slides Slide 3 | Slide 3 数据重建 | Dune Analytics query #7586359: 所有五链 YoY 均下降——Base -74.7% / Arbitrum -56.6% / OP -84.5% / Mantle -81.0% / zkSync -31.6% | 2025-06 ~ 2026-05 | `verified-data` | 基于实际链上 DAU 时序数据计算 |
| 14 | EIP-4844 后中位数费用均在亚美分级别（$0.00002 — $0.015） | slides Slide 3 | Slide 3 数据重建 | Dune Analytics query #7586361: `SELECT block_date, blockchain, approx_percentile(tx_fee_usd, 0.5) FROM gas.fees` → CSV `data/slide3-median-fees-daily.csv`；May 2026 中位数: OP $0.000023 / X Layer $0.000139 / Mantle $0.001144 / Base $0.001452 / Arbitrum $0.003001 / zkSync $0.014785 | 2026-05-26 | `verified-data` | `gas.fees` 为 Dune Spellbook 模型，含 gas_price × gas_used × native_token_price 计算 |
| 15 | Mantle 日收入 <$1K/day | final-report L59 / slides Slide 5 | `market-landscape/final.md` Item-2 diag-1 | 可由 Dune `gas.fees` 日均手续费收入交叉验证 | 2026-05-26 | `verified-data` | Dune 数据可验证 |

### 1.2 开发者活动数据

| # | 数据点 | 报告引用 | 研究 Section | 原始数据源 | 快照时间 | 可信度 | Caveat |
|---|--------|---------|-------------|-----------|---------|--------|--------|
| 16 | Base 1,810 PRs (3m) | final-report L47 / slides Slide 8 | `competitor-base/final.md` | GitHub `base/base` 仓库 PR search, 2026-02-24..2026-05-24 | 2026-05-24 | `verified-primary` | 公开 GitHub 数据 |
| 17 | zkSync 1,427 PRs | final-report L48 / slides Slide 9 | `competitor-zksync/final.md` Item-1 | GitHub `matter-labs` org 多仓 PR search, 2026-02-23..2026-05-23 | 2026-05-23 | `verified-primary` | 多仓聚合，含 zksync-os-server 等 |
| 18 | Optimism 1,202 PRs | final-report L49 / slides Slide 8 | `competitor-optimism/final.md` | GitHub `optimism` monorepo PR search | 2026-05-24 | `verified-primary` | |
| 19 | Arbitrum 256 PRs (Nitro) | final-report L50 / slides Slide 8 | `competitor-arbitrum/final.md` | GitHub `arbitrum/nitro` PR search | 2026-05-24 | `verified-primary` | 仅 Nitro 仓库 |
| 20 | Mantle 开发者活动未量化 | final-report L51 | `market-landscape/final.md` GAP-3 | — | — | `unverified` | **明确数据缺口** |

### 1.3 DeFi 天花板数据

| # | 数据点 | 报告引用 | 研究 Section | 原始数据源 | 快照时间 | 可信度 | Caveat |
|---|--------|---------|-------------|-----------|---------|--------|--------|
| 21 | 全球 DeFi TVL $92-140B，远低于 $250B 预期 | final-report L67 / slides Slide 4 | `market-landscape/final.md` Item-4.1 | DefiLlama: https://defillama.com/ | 2026-05-25T18:00:00Z | `verified-data` | $250B 为市场预期引用 |
| 22 | 83-95% DeFi 流动性闲置 | final-report L68 / slides Slide 4 | `market-landscape/final.md` Item-4.1 | FinTech Weekly: https://www.fintechweekly.com/magazine/articles/defi-capital-efficiency-tvl-revenue-density-institutional-2026 | 2026-03-15 | `industry-report` | medium confidence |
| 23 | Aave 59% 借贷市场份额，$19.4B TVL | final-report L69 / slides Slide 4 | `market-landscape/final.md` Item-4.1 | DefiLlama: https://defillama.com/ | 2026-04-30 | `verified-data` | |
| 24 | Blast TVL $2.7B → $55M, DAU 180K → 3,800 | final-report L70 / slides Slide 4 | `market-landscape/final.md` Item-4.1 | L2Beat + CoinBureau | 2026-05-25 | `verified-data` | |

### 1.4 RWA / 机构金融数据

| # | 数据点 | 报告引用 | 研究 Section | 原始数据源 | 快照时间 | 可信度 | Caveat |
|---|--------|---------|-------------|-----------|---------|--------|--------|
| 25 | 链上 RWA 总市值（不含稳定币）$31-34B | final-report L76 / slides Slide 4, 16 | `market-landscape/final.md` Item-5.1 + `narrative-institutional/final.md` Item-1 | RWA.xyz（通过二手引用）: Cryptoadventure 2026-05-07 引用 RWA.xyz ~$31.12B; Rekord 2026-05 引用 RWA.xyz ~$33.7B | 2026-05-25T12:00:00Z | `secondary` | **关键 caveat**: 非 RWA.xyz API 直接导出，是第三方文章引用 RWA.xyz view；需在 2026-06-05 前刷新 |
| 26 | RWA YoY 增长 >200%（从 ~$6B） | final-report L76 / slides Slide 4, 16 | `market-landscape/final.md` Item-5.1 + `narrative-institutional/final.md` Item-1 | RWA.xyz 2025-01 至 2026-05 趋势 | 2025-01 ~ 2026-05 | `verified-data` | |
| 27 | 美国国债代币化 $12.88-15B | final-report L77 / slides Slide 4 | `market-landscape/final.md` Item-5.1 + `narrative-institutional/final.md` Item-1 | RWA.xyz: https://app.rwa.xyz/treasuries (public page, as of 2026-01-28 显示 $10.00B); Rekord 2026-05 引用 ~$15.35B | 2026-05-25T12:00:00Z | `secondary` | RWA.xyz 公开页面 2026-01 快照为 $10B，2026-05 数字来自 Rekord 二手引用 |
| 28 | BlackRock BUIDL ~$2.5B AUM | final-report L78 / slides Slide 4, 16 | `market-landscape/final.md` Item-5.2 + `narrative-institutional/final.md` Item-1 | RWA.xyz + CoinDesk: https://www.coindesk.com/business/2026/05/09/blackrock-deepens-tokenization-push-with-new-onchain-fund-offerings | 2026-05-25 | `verified-data` | 部署在 ETH/Solana/Polygon/Avalanche/Arbitrum/Optimism/Aptos，**不在 Mantle/zkSync/Base** |
| 29 | Ondo OUSG + USDY ~$2.5B | final-report L79 | `market-landscape/final.md` Item-5.2 | RWA.xyz + Ondo official | 2026-05-20 | `verified-data` | 仅 ETH + Solana |
| 30 | Franklin Templeton FOBXX ~$844M | final-report L80 | `market-landscape/final.md` Item-5.2 | RWA.xyz + Franklin official | 2026-05-20 | `verified-data` | 部署在 Arbitrum/Base 等 |
| 31 | BlackRock 2026-05 向 SEC 申请 $7B MMF 上链 | final-report L81 / slides Slide 4 | `market-landscape/final.md` Item-5 diag-4 | SEC filing + CoinDesk 报道 | 2026-05-09 | `verified-primary` | SEC filing 为一手监管文件 |
| 32 | 分布式 + 代表式 RWA ~$406B（不含稳定币） | final-report L428 | `narrative-institutional/final.md` Item-1 | Rekord 2026-05 报告引用 RWA.xyz | 2026-05 | `secondary` | 含 represented/platform-locked/permissioned 资产 |

### 1.5 Mantle 生态数据

| # | 数据点 | 报告引用 | 研究 Section | 原始数据源 | 快照时间 | 可信度 | Caveat |
|---|--------|---------|-------------|-----------|---------|--------|--------|
| 33 | mETH ~$925M TVL，第 4 大 ETH LST | final-report L99 / slides Slide 5 | `market-landscape/final.md` Item-7.2 | DefiLlama: https://defillama.com/protocol/meth-protocol + Mantle official | 2026-05-25 | `verified-data` | |
| 34 | cmETH ~$515M TVL | final-report L100 / slides Slide 5 | `market-landscape/final.md` Item-7.2 | DefiLlama: https://defillama.com/protocol/meth-protocol | 2026-05-25 | `verified-data` | |
| 35 | 稳定币峰值 $825M，保留 ~$669M（81%） | final-report L101 / slides Slide 5 | `market-landscape/final.md` Item-8.1 | Nansen Q4 2025 Report: https://nansen.ai/post/mantle-q4-2025-report | 2026-01-15 | `verified-data` | Q4 2025 数据 |
| 36 | MI4 $400M 代币化基金 | final-report L105 / slides Slide 5 | `narrative-institutional/final.md` Item-4 | BusinessWire/Securitize: https://www.businesswire.com/news/home/20250424178524/en/ | 2025-04-24 | `verified-primary` | 官方新闻稿，Mantle Treasury 为 anchor investor |
| 37 | Aave V3 上线后 12 天内 $290M+ 存款 | final-report L108 / slides Slide 5 | `market-landscape/final.md` Item-7.3 | BanklessTimes: https://www.banklesstimes.com/articles/2026/03/11/the-aave-effect-mantle-crosses-1b-tvl-in-under-two-weeks/ | 2026-03-11 | `industry-report` | 被评估为激励驱动型 TVL |
| 38 | Mantle DAU 历史波动: 37K→12K→53K→5K→2.3K | final-report L57 / slides Slide 5 | `market-landscape/final.md` Item-8 | Nansen Q1-Q4 2025 季报 + Messari State of Mantle | 多季度 | `verified-data` | 波动极大，单一快照不可靠 |
| 39 | ~$4B+ 国库 | final-report L473 / slides Slide 19 | `narrative-institutional/final.md` Item-4 | Mantle 2025 blog: https://group.mantle.xyz/ | 2025 | `vendor-claimed` | 官方博客声称 |
| 40 | mETH L2 163,934 持有者 + L1 9,949 | final-report L99 | `market-landscape/final.md` Item-8.1 diag-8 | Etherscan + Mantlescan | 2026-05-25 | `verified-data` | |

---

## Chapter 2: 竞争对手分析

### 2.1 L2 竞品数据

| # | 数据点 | 报告引用 | 研究 Section | 原始数据源 | 快照时间 | 可信度 | Caveat |
|---|--------|---------|-------------|-----------|---------|--------|--------|
| 41 | Base: Azul 目标主网 2026-05-28 | final-report L127 | `competitor-base/final.md` | Base 官方 blog | 2026-05-24 | `verified-primary` | |
| 42 | Base: Flashblocks 200ms | final-report L128 / slides Slide 8 | `competitor-base/final.md` | Base 官方 blog/docs | 2026-05-24 | `verified-primary` | 增量状态更新，在 2s 块内，非硬终局 |
| 43 | Base: Coinbase 110M+ 用户 | final-report L133 / slides Slide 8 | `competitor-base/final.md` | Coinbase 官方公开数据 | 2026 | `verified-primary` | |
| 44 | Arbitrum: Nitro 256 PRs / 186 merged | final-report L142 / slides Slide 8 | `competitor-arbitrum/final.md` | GitHub `arbitrum/nitro` | 2026-05-24 | `verified-primary` | |
| 45 | Arbitrum: L2Beat Stage 1 评级 | final-report L143 | `competitor-arbitrum/final.md` | L2Beat | 2026-05-24 | `verified-data` | |
| 46 | Optimism: 1,202 PRs / 751 merged | final-report L157 / slides Slide 8 | `competitor-optimism/final.md` | GitHub `optimism` monorepo | 2026-05-24 | `verified-primary` | |
| 47 | Optimism: op-geth 支持截止 2026-05-31 | final-report L159 / slides Slide 21 | `competitor-optimism/final.md` | Optimism 官方公告 | 2026-05-24 | `verified-primary` | |
| 48 | zkSync: zksync-os-server 404 PRs / 238 merged / 34 authors | final-report L172 | `competitor-zksync/final.md` Item-1 | GitHub `matter-labs/zksync-os-server` PR search | 2026-05-23 | `verified-primary` | |
| 49 | zkSync Prividium: 35+ 银行 | final-report L178-179 / slides Slide 9, 16-17 | `competitor-zksync/final.md` + `narrative-institutional/final.md` Item-3 | ZKsync 官网/产品页: https://www.zksync.io/prividium | 2026-05-23 | **`vendor-claimed`** | **供应商声称，未独立验证。仅 local-prividium Docker Compose 环境，非生产部署证据** |
| 50 | zkSync DeFi TVL 暴跌 >96% | final-report L179 | `competitor-zksync/final.md` + `market-landscape/final.md` | DefiLlama | 2026-05-25 | `verified-data` | |
| 51 | StarkNet: sequencer 1,324 PRs / 881 merged | final-report L188 | `competitor-starknet/final.md` | GitHub `starkware-libs/sequencer` | 2026-05-24 | `verified-primary` | |
| 52 | StarkNet DeFi TVL ~$199M | final-report L194 | `competitor-starknet/final.md` | DefiLlama | 2026-05-25 | `verified-data` | |
| 53 | X Layer: OP Stack 迁移 2025-10-27 | final-report L200 | `competitor-xlayer/final.md` | L2Beat + OKX 官方 | 2025-10 | `verified-primary` | |
| 54 | X Layer: Exchange OS 白皮书 2026-05-26 | final-report L204 | `competitor-xlayer/final.md` | X Layer 官方白皮书 | 2026-05-26 | `verified-primary` | |
| 55 | OKX 120M 用户 | final-report L209 | `competitor-xlayer/final.md` | OKX 官方数据 | 2026 | `verified-primary` | |

### 2.2 L1 通用链数据

| # | 数据点 | 报告引用 | 研究 Section | 原始数据源 | 快照时间 | 可信度 | Caveat |
|---|--------|---------|-------------|-----------|---------|--------|--------|
| 56 | Solana: $10B 稳定币供给，$200B 月度转账 | final-report L223 / slides Slide 10 | `competitor-solana/final.md` | Solana 官方叙事数据 | 2026-05 | `vendor-claimed` | 官方叙事 |
| 57 | Sui: Gasless 主网 v1.72.2 (2026-05-20) | final-report L234 / slides Slide 10 | `competitor-sui/final.md` | Sui GitHub release | 2026-05-20 | `verified-primary` | gasless_max_tps = 300 |
| 58 | Sui DeFi TVL ~$565.96M | final-report L237 | `competitor-sui/final.md` | DefiLlama | 2026-05-25 | `verified-data` | |
| 59 | BNB Chain: Mendel 硬分叉主网激活 2026-04-28 | final-report L248 | `competitor-bnbchain/final.md` | BSC 官方 | 2026-04-28 | `verified-primary` | |
| 60 | BNB Chain: MCP 89% PR 关闭率 | final-report L245 | `competitor-bnbchain/final.md` | GitHub 数据 | 2026-05-24 | `verified-primary` | 代码成熟度弱信号 |

### 2.3 L1 垂直链数据

| # | 数据点 | 报告引用 | 研究 Section | 原始数据源 | 快照时间 | 可信度 | Caveat |
|---|--------|---------|-------------|-----------|---------|--------|--------|
| 61 | Tempo: ~500-600ms 终局目标 | final-report L269 / slides Slide 11 | `payment-tempo/final.md` | Tempo 营销资料 | 2026-05-22 | **`vendor-claimed`** | 营销数据，未独立验证 |
| 62 | Tempo: Mainnet/Presto 已运营，T4 激活 2026-05-18 | final-report L271 | `payment-tempo/final.md` | Tempo 状态页 + 链上数据 | 2026-05-22 | `verified-primary` | 但实际交易量/活跃商户未被独立验证 |
| 63 | Tempo: Zones proof bytes 为空 | final-report L271 / slides Slide 11 | `payment-tempo/final.md` | 链上代码检查 | 2026-05-22 | `verified-primary` | **仅有架构接口，无实际有效性证明** |
| 64 | Circle Arc: Malachite BFT ~780ms (100 验证器) | final-report L283 | `payment-ark/final.md` Item-2 | Arc blog "Arc's Deterministic Finality" | 2026-05-23 | `verified-primary` | 测试网基准 |
| 65 | Circle Arc: CCTP V2 $126B 累计, $31B Q3 2025 (+740% YoY) | final-report L285 / slides Slide 11 | `payment-ark/final.md` | Circle CCTP 文档 + Circle 财报 | 2026-05-23 | `verified-primary` | |
| 66 | Circle Arc: **Mantle 不在 CCTP 支持列表** | final-report L285, L392 | `payment-ark/final.md` + `narrative-payment/final.md` Item-4 | Circle CCTP docs: https://developers.circle.com/cctp/concepts/supported-chains-and-domains | 2026-05-26 | `verified-primary` | **结构性障碍** |
| 67 | Circle Q1 2026: 收入 $694M, USDC $77B, 链上量 $21.5T (+263%) | final-report L289 / slides Slide 4, 11 | `payment-ark/final.md` Item-1 | Circle Q1 2026 pressroom: https://www.circle.com/pressroom/circle-reports-first-quarter-2026-results | 2026-05-11 | `verified-primary` | Circle 官方财报一手数据 |
| 68 | Arc 代币预售 $222M / $3B FDV | final-report L291 / slides Slide 11 | `payment-ark/final.md` Item-1 | Bitcoin.com / CoinGecko 等二级资料 | 2026-05-11 | `secondary` | 预售条款来自二手媒体，非白皮书直接披露 |
| 69 | Arc 测试网 100+ 机构, 244.1M 交易 | final-report L290 / slides Slide 11 | `payment-ark/final.md` Item-1 | ARC 白皮书 PDF 直接解析（截至 2026-05-05）| 2026-05-05 | `verified-primary` | 白皮书一手数据 |
| 70 | Canton: Broadridge DLR $368B/日, ~$8T/月 | final-report L312 / slides Slide 11 | `enterprise-canton/final.md` Item-8 | Broadridge 2026-04 新闻稿（vendor-reported） | 2026-04 | **`vendor-claimed`** | **供应商报告的数据，非独立审计** |
| 71 | Canton: GS DAP 结算 T+5→<60s | final-report L313 | `enterprise-canton/final.md` | Goldman Sachs / Digital Asset 官方材料 | 2026 | `vendor-claimed` | |
| 72 | Canton: DTCC 目标 2026H1 可控生产 MVP | final-report L315 / slides Slide 11 | `enterprise-canton/final.md` | DTCC 2025-12-17 公告 | 2025-12-17 | `verified-primary` | 是目标声明，非已上线 |
| 73 | Canton: JPM Kinexys 2026-01-07 宣布合作意向 | final-report L316 | `enterprise-canton/final.md` | JPM 2026-01-07 公告 | 2026-01-07 | `verified-primary` | **未上线，分阶段** |
| 74 | GENIUS Act 2025-07-18 签署 | final-report L452 | `payment-ark/final.md` Item-1 | White House S.1582 signing notice | 2025-07-18 | `verified-primary` | |

---

## Chapter 3: 叙事方向技术分析

### 3.1 AgentFi 数据

| # | 数据点 | 报告引用 | 研究 Section | 原始数据源 | 快照时间 | 可信度 | Caveat |
|---|--------|---------|-------------|-----------|---------|--------|--------|
| 75 | CoinGecko AI Agents ~$3.68B 市值 | final-report L344 / slides Slide 14 | `narrative-agentfi/final.md` Item-2.1 | CoinGecko API `/api/v3/coins/categories`, category id `ai-agents` | 2026-05-26T00:27:30Z | `verified-data` | **token 资产指标，非真实 Agent 商务 TAM** |
| 76 | x402: 50,566 上架资源, 326,224 L30 调用 | final-report L347 | `narrative-agentfi/final.md` Item-2.1 | Coinbase CDP x402 discovery API: https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources | 2026-05-26T00:37:32Z | `verified-data` | unique payers 按 resource 求和，未跨资源去重；含测试流量 |
| 77 | Virtuals Protocol 30 天费用 ~$411K | final-report L347 | `narrative-agentfi/final.md` Item-2.1 | DefiLlama fees: https://api.llama.fi/summary/fees/virtuals-protocol | 2026-05-26 | `verified-data` | protocol activity proxy，非 ACP jobs |

### 3.2 Payment Chain 数据

| # | 数据点 | 报告引用 | 研究 Section | 原始数据源 | 快照时间 | 可信度 | Caveat |
|---|--------|---------|-------------|-----------|---------|--------|--------|
| 78 | 全球稳定币供给 ~$320.7B | final-report L373 / slides Slide 15 | `narrative-payment/final.md` Item-1 | DefiLlama stablecoins API: https://stablecoins.llama.fi/stablecoins?includePrices=true | 2026-05-26 | `verified-data` | |
| 79 | 真实稳定币支付渗透率 ~$390B/年，占全球支付 0.02% | final-report L375 / slides Slide 15 | `narrative-payment/final.md` Item-1 | McKinsey/Artemis: https://www.mckinsey.com/industries/financial-services/our-insights/stablecoins-in-payments-what-the-raw-transaction-numbers-miss | 2026-02-18 | `industry-report` | true-payment activity 估算，非链上总转账量 |
| 80 | 跨境支付 TAM: McKinsey ~$179T | final-report L376 | `narrative-payment/final.md` Item-1 | McKinsey: https://www.mckinsey.com/industries/financial-services/our-insights/banking-matters/how-banks-can-win-back-lower-value-cross-border-payments-business | 2025-04-25 | `industry-report` | |
| 81 | FXC Intelligence B2B 跨境 $39.3T(2023)→$56.1T(2030) | final-report L376 | `narrative-payment/final.md` Item-1 | FXC Intelligence public summary: https://news.cision.com/fxc-intelligence/... | 2023-04-27 | `industry-report` | 公开摘要数字 |
| 82 | Mantle 稳定币 ~$557.8M | final-report L397 / slides Slide 15 | `narrative-payment/final.md` Item-3 | DefiLlama chainCirculating API | 2026-05-26 | `verified-data` | USDT ~$364.5M, USDe ~$123.1M, USDC ~$35.7M |

### 3.3 机构金融数据

| # | 数据点 | 报告引用 | 研究 Section | 原始数据源 | 快照时间 | 可信度 | Caveat |
|---|--------|---------|-------------|-----------|---------|--------|--------|
| 83 | 美国国债代币化 ~$15.35B (2026-05) | final-report L429 | `narrative-institutional/final.md` Item-1 | Rekord 2026-05 引用 RWA.xyz | 2026-05 | `secondary` | 同 #27 |
| 84 | McKinsey 2030 RWA 预测 $2T | final-report L431 | `narrative-institutional/final.md` Item-1 | McKinsey report | 2025 | `industry-report` | 中等置信度 |
| 85 | BCG-Ripple 2033 预测 $18.9T | final-report L431 | `narrative-institutional/final.md` Item-1 | BCG report | 2025 | `industry-report` | **低置信度** |
| 86 | SEC 2026-01-28 代币化证券声明 | final-report L451 | `narrative-institutional/final.md` Item-2 | SEC: https://www.sec.gov/newsroom/speeches-statements/corp-fin-statement-tokenized-securities-012826-statement-tokenized-securities | 2026-01-28 | `verified-primary` | 监管一手声明 |
| 87 | Vitalik 2026-02 cypherpunk 文章 | final-report L83 | `market-landscape/final.md` Item-6.2 | Vitalik 宣言 2026-02-22 + https://coingenius.news/vitalik-buterin-advocates-cypherpunk-revival-for-2026/ | 2026-02-22 | `verified-primary` | |
| 88 | FOCIL 纳入 Hegota 硬分叉 (2026 年底) | final-report L83 | `market-landscape/final.md` Item-6.2 | Ethereum Foundation roadmap / 官方确认 | 2026 | `verified-primary` | |
| 89 | ERC-3643 demo **无公开来源确认** | final-report L466 | `narrative-institutional/final.md` Item-4 | — | — | **`unverified`** | **明确数据缺口**: 未找到公开主要来源 |

---

## 汇总: 需要特别关注的数据点

### 高风险数据（复核重点）

| # | 数据点 | 风险原因 | 建议处理 |
|---|--------|---------|---------|
| 25-27 | RWA 市场规模 $31-34B / $15.35B 国债 | 来自二手文章引用 RWA.xyz view，非 API 直接导出 | 2026-06-05 前用 RWA.xyz 登录/API 刷新 |
| 49 | Prividium 35+ 银行 | 供应商声称，无逐家机构公告 | 标注为 vendor-claimed |
| 70 | Canton Broadridge $368B/日 | 供应商新闻稿数据 | 标注为 vendor-reported |
| 61 | Tempo ~500-600ms 终局 | 营销数据 | 标注为未独立验证 |
| 85 | BCG-Ripple $18.9T 预测 | 低置信度行业预测 | 标注低置信度或考虑移除 |
| 89 | Mantle ERC-3643 demo | 无公开来源 | 不应作为事实使用 |

### 结构性数据缺口

| # | 缺口 | 影响 | 建议 |
|---|------|------|------|
| 20 | Mantle GitHub 开发者活动未量化 | 无法与竞品对比 | 补充 mantlenetworkio org PR/commit 分析 |
| 66 | Mantle 不在 CCTP 列表 | 支付和机构叙事障碍 | 评估合作可行性 |
| 10b | X Layer DAU 数据不可用 | Slide 3 DAU 饼图缺少 X Layer | Dune `evms.transactions` 不覆盖 xlayer；需寻找 OKX Explorer API 或其他来源 |

### 数据口径提醒

| 关注点 | 说明 |
|--------|------|
| TVL 口径 | Slide 3 统一使用 DefiLlama DeFi 协议锁仓口径（每日 API）；L2Beat 含桥接资产，口径不同不可混用 |
| DAU 定义 | Slide 3 统一使用 Dune `evms.transactions` + `approx_distinct("from")`，sender-based unique addresses，含 bot/spam，未过滤 |
| 费用口径 | Slide 3 使用 Dune `gas.fees` Spellbook 中位数（`approx_percentile(tx_fee_usd, 0.5)`），含 L1+L2 费用组成 |
| RWA 口径 | distributed vs represented vs 含稳定币，三种口径差异巨大 |
| USDC 链上量 | Circle Q1 $21.5T 为 onchain transaction volume，含交易所/做市/DeFi，非纯支付 |
| 采用声称 | 合作公告 ≠ 生产部署；logo 参与 ≠ 生产级集成 |
