# Research Sections Index

| order | topic_slug | multica_issue_id | final_path | dependencies | status |
|-------|-----------|-----------------|------------|--------------|--------|
| 1 | compliance-token-landscape | f6a0c156-96f4-49df-b7c3-70109c308c5f | compliance-token-standards/research-sections/compliance-token-landscape/final.md | - | done |
| 2 | erc1400-series-analysis | cf57ea5d-c512-47fc-8c8d-99b1f15a86e5 | compliance-token-standards/research-sections/erc1400-series-analysis/final.md | compliance-token-landscape | done |
| 3 | erc3643-trex-analysis | 4036a12f-42fd-4ec1-a113-18df6c26c9a1 | compliance-token-standards/research-sections/erc3643-trex-analysis/final.md | compliance-token-landscape | done |
| 4 | tempo-tip20-analysis | 586341f0-3ee8-4a89-8aa1-3535dd847d90 | compliance-token-standards/research-sections/tempo-tip20-analysis/final.md | compliance-token-landscape | done |
| 5 | compliance-token-comparison | c62bd179-f560-4ab7-b23e-9ffb153b88dd | compliance-token-standards/research-sections/compliance-token-comparison/final.md | compliance-token-landscape, erc3643-trex-analysis, erc1400-series-analysis, tempo-tip20-analysis | done |

## Section Descriptions

### 1. compliance-token-landscape
合规 Token 标准的监管驱动力（EU/US/APAC）、RWA 市场数据、ERC-3643/ERC-1400/B20/TIP-20/Circle Arc 五大标准横向对比（8 类合规能力 Taxonomy + 7 维度评估矩阵），以及应用层合规 vs 协议层合规的设计范式分析。

### 2. erc1400-series-analysis
ERC-1400 系列标准（ERC-1410/1594/1643/1644）的模块化架构分析，含 `_data` 参数三种合规实现模式、ERC-20 fallback 安全风险审计证据（ConsenSys Diligence 2020 Codefi 审计）、基于 WHI-177 taxonomy 的 8 类合规能力 × 7 维度与 ERC-3643 深度对比，以及历史地位与演化路径（partition 机制 → ERC-7518、controller → Agent role 演化）。

### 3. erc3643-trex-analysis
ERC-3643（T-REX）标准深度分析：6 组件架构（Token Contract / Identity Registry / Compliance Module / Trusted Issuers Registry / Claim Topics Registry / ONCHAINID）、receiver-only 合规检查 transfer flow、发行方控制体系（Agent role / 双层 freeze / forcedTransfer / Recovery）、ERC-20 兼容与 UUPS 代理升级、$32B+ 生态采用（Association 自报数据）、Gas 开销与局限性（DeFi 可组合性 / 中心化依赖 / 跨链挑战）、8 类合规能力 taxonomy 评估、7 维度框架评分。

### 4. tempo-tip20-analysis
Tempo TIP-20 precompile token 标准深度分析：TIP-20 核心架构（precompile suite、Factory createToken、ERC-20 向后兼容、ERC-7572 contract URI），TIP-403 Policy Registry 合规机制（Whitelist/Blacklist/Compound Policy、跨 token 共享、Chainalysis 覆盖），三层支付基础设施（Payment Lanes 独立 blockspace、per-transaction Fee AMM lifecycle、StablecoinDEX batch matching），RBAC 五角色模型，Opt-in 奖励分发，7 个扩展 TIP 分析，生态集成（Chainalysis、Zones、KlarnaUSD/LayerZero），8 类合规能力 taxonomy 映射（与 B20/ERC-3643 对比）。注：所有 TIP-20 协议层声明为 docs-stated；8 个 C1 待验证 gap 见正文 Gap Analysis 节。

### 5. compliance-token-comparison
四大合规 Token 标准横向对比分析（ERC-3643、ERC-1400、TIP-20、B20）：9 维技术对比矩阵（架构层级 / 合规机制类型 / 身份模型 / Gas 效率 / DeFi 可组合性 / 发行方控制力 / 跨链能力 / 支付优化 / 升级与治理）、6 维规范成熟度评估表、基于 WHI-177 taxonomy 的 8 类合规能力覆盖矩阵、EVM 执行栈分层架构对比图、关键 insight（合规在哪一层实现是最根本设计分歧；Precompile 路线已形成趋势但公开 spec 成熟度仍存差距；ERC-3643 与 B20/TIP-20 存在互补而非纯竞争关系）、Trade-off 分析、B20 证据边界说明（pinned commit `base/base@8e87672`，B20Security 本地分支约束，Beryl spec 待发布）。依赖 WHI-177/178/179/180/181 五个 M1 分析节。
