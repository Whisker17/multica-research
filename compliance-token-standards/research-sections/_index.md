# Research Sections Index

| order | topic_slug | multica_issue_id | final_path | dependencies | status |
|-------|-----------|-----------------|------------|--------------|--------|
| 1 | compliance-token-landscape | f6a0c156-96f4-49df-b7c3-70109c308c5f | compliance-token-standards/research-sections/compliance-token-landscape/final.md | - | done |
| 2 | erc1400-series-analysis | cf57ea5d-c512-47fc-8c8d-99b1f15a86e5 | compliance-token-standards/research-sections/erc1400-series-analysis/final.md | compliance-token-landscape | done |
| 3 | erc3643-trex-analysis | 4036a12f-42fd-4ec1-a113-18df6c26c9a1 | compliance-token-standards/research-sections/erc3643-trex-analysis/final.md | compliance-token-landscape | done |

## Section Descriptions

### 1. compliance-token-landscape
合规 Token 标准的监管驱动力（EU/US/APAC）、RWA 市场数据、ERC-3643/ERC-1400/B20/TIP-20/Circle Arc 五大标准横向对比（8 类合规能力 Taxonomy + 7 维度评估矩阵），以及应用层合规 vs 协议层合规的设计范式分析。

### 2. erc1400-series-analysis
ERC-1400 系列标准（ERC-1410/1594/1643/1644）的模块化架构分析，含 `_data` 参数三种合规实现模式、ERC-20 fallback 安全风险审计证据（ConsenSys Diligence 2020 Codefi 审计）、基于 WHI-177 taxonomy 的 8 类合规能力 × 7 维度与 ERC-3643 深度对比，以及历史地位与演化路径（partition 机制 → ERC-7518、controller → Agent role 演化）。

### 3. erc3643-trex-analysis
ERC-3643（T-REX）标准深度分析：6 组件架构（Token Contract / Identity Registry / Compliance Module / Trusted Issuers Registry / Claim Topics Registry / ONCHAINID）、receiver-only 合规检查 transfer flow、发行方控制体系（Agent role / 双层 freeze / forcedTransfer / Recovery）、ERC-20 兼容与 UUPS 代理升级、$32B+ 生态采用（Association 自报数据）、Gas 开销与局限性（DeFi 可组合性 / 中心化依赖 / 跨链挑战）、8 类合规能力 taxonomy 评估、7 维度框架评分。
