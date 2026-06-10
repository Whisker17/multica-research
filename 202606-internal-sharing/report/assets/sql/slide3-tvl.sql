-- ═══════════════════════════════════════════════════════════════════════
-- Slide 3 — L2 TVL (Total Value Locked) Comparison
-- ═══════════════════════════════════════════════════════════════════════
-- Chains:  Base · Arbitrum · Optimism · zkSync · Mantle · X Layer
-- Period:  Past 12 months, monthly snapshots
-- ═══════════════════════════════════════════════════════════════════════
--
-- TVL 方法论说明:
--   链上 TVL 需要追踪所有 bridge 合约余额 + 原生资产 + 协议存款，
--   从 raw tx/trace 数据计算成本极高且容易遗漏。
--   推荐方案:
--     • 主选: DefiLlama API (行业标准 TVL 数据源)
--     • 备选: Dune 社区数据集 (如有)
--
-- DefiLlama API:
--   curl -s "https://api.llama.fi/v2/historicalChainTvl/Base"
--   curl -s "https://api.llama.fi/v2/historicalChainTvl/Arbitrum"
--   curl -s "https://api.llama.fi/v2/historicalChainTvl/Optimism"
--   curl -s "https://api.llama.fi/v2/historicalChainTvl/zkSync Era"
--   curl -s "https://api.llama.fi/v2/historicalChainTvl/Mantle"
--   curl -s "https://api.llama.fi/v2/historicalChainTvl/X Layer"
--
--   返回格式: [{"date": 1234567890, "tvl": 12345678.90}, ...]
--
-- ═══════════════════════════════════════════════════════════════════════


-- ── Option 1: Dune 社区数据集 (需验证表名) ─────────────────────────
-- Dune 团队和社区维护了 L2 TVL 数据集，常见位置:
--   • dune.dune.dataset_l2_tvl
--   • dune.hildobby.dataset_l2_tvl
--   • dune.steakhouse.dataset_chain_tvl
-- 在 Dune Dataset Explorer 中搜索 "l2 tvl" 确认可用表名

/*
SELECT
    date_trunc('month', day)    AS month,
    chain                        AS blockchain,
    AVG(tvl_usd)                AS avg_tvl_usd,
    MAX_BY(tvl_usd, day)        AS eom_tvl_usd   -- end-of-month snapshot
FROM dune.dune.dataset_l2_tvl                     -- ← 需确认表名
WHERE chain IN (
        'base', 'arbitrum', 'optimism',
        'zksync', 'mantle', 'xlayer'
      )
  AND day >= date_add('year', -1, current_date)
GROUP BY 1, 2
ORDER BY blockchain, month
;
*/


-- ── Option 2: 稳定币供应量作为 TVL 分项指标 ────────────────────────
-- 稳定币 TVL 是各链流动性的核心组成 (~40-60% of DeFi TVL)
-- 使用 Dune Spellbook 的 stablecoin 或 token transfer 模型

/*
WITH stablecoin_supply AS (
    SELECT
        date_trunc('month', block_date)  AS month,
        blockchain,
        token_symbol,
        -- 净铸造量 = 从零地址转出的累计金额
        SUM(CASE
            WHEN "from" = 0x0000000000000000000000000000000000000000
            THEN amount_usd
            WHEN "to"   = 0x0000000000000000000000000000000000000000
            THEN -amount_usd
            ELSE 0
        END) AS net_minted_usd
    FROM tokens.transfers
    WHERE blockchain IN (
            'base', 'arbitrum', 'optimism',
            'zksync', 'mantle', 'xlayer'
          )
      AND token_symbol IN ('USDC', 'USDT', 'DAI', 'USDY', 'USDe', 'FDUSD')
      AND block_date >= date_add('year', -1, current_date)
      AND block_date <  current_date
    GROUP BY 1, 2, 3
)

SELECT
    month,
    blockchain,
    SUM(net_minted_usd) AS stablecoin_net_flow_usd
FROM stablecoin_supply
GROUP BY 1, 2
ORDER BY blockchain, month
;
*/
