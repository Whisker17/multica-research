-- ═══════════════════════════════════════════════════════════════════════
-- Slide 3 — L2 Median Transaction Fee (USD)
-- ═══════════════════════════════════════════════════════════════════════
-- Chains:  Base · Arbitrum · Optimism · zkSync · Mantle · X Layer
-- Period:  Past 12 months, monthly granularity
-- Method:  approx_percentile(0.5) on per-tx USD total fee
-- Source:  gas.fees (Dune Spellbook — includes L1 + L2 fee components)
-- ═══════════════════════════════════════════════════════════════════════
--
-- Notes:
--   1. gas.fees includes both L2 execution fee and L1 data posting fee,
--      giving the true total cost to users
--   2. Post-EIP-4844 (March 2024), L1 data costs dropped ~100×; all
--      data in this window is post-Dencun
--   3. p25/p75 included for spread analysis — fee distribution is
--      long-tailed, so median >> mean for typical user experience
--   4. If gas.fees does not cover Mantle or X Layer, use the fallback
--      query at the bottom of this file
-- ═══════════════════════════════════════════════════════════════════════


-- ── Primary Query (gas.fees Spellbook) ──────────────────────────────

SELECT
    date_trunc('month', block_time)          AS month,
    blockchain,
    approx_percentile(tx_fee_usd, 0.5)      AS median_fee_usd,
    approx_percentile(tx_fee_usd, 0.25)     AS p25_fee_usd,
    approx_percentile(tx_fee_usd, 0.75)     AS p75_fee_usd,
    AVG(tx_fee_usd)                          AS avg_fee_usd,
    COUNT(*)                                  AS tx_count
FROM gas.fees
WHERE blockchain IN (
        'base', 'arbitrum', 'optimism',
        'zksync', 'mantle', 'xlayer'
      )
  AND block_time >= date_trunc('month', date_add('year', -1, current_date))
  AND block_time <  date_trunc('month', current_date)
GROUP BY 1, 2
ORDER BY blockchain, month
;


-- ═══════════════════════════════════════════════════════════════════════
-- Fallback: manual fee calculation from evms.transactions + prices.usd
-- ═══════════════════════════════════════════════════════════════════════
-- Use this if gas.fees doesn't cover a chain (e.g. Mantle, X Layer).
--
-- Caveats:
--   • Captures L2 execution fee only (no L1 data cost component)
--   • Uses monthly avg native token price for USD conversion
--   • Gas token: ETH (Base/Arb/OP/zkSync), MNT (Mantle), OKB (X Layer)
-- ═══════════════════════════════════════════════════════════════════════

/*
WITH monthly_median_native AS (
    SELECT
        date_trunc('month', block_time) AS month,
        blockchain,
        approx_percentile(
            CAST(gas_used AS DOUBLE) * CAST(gas_price AS DOUBLE) / 1e18,
            0.5
        ) AS median_fee_native,
        approx_percentile(
            CAST(gas_used AS DOUBLE) * CAST(gas_price AS DOUBLE) / 1e18,
            0.25
        ) AS p25_fee_native,
        approx_percentile(
            CAST(gas_used AS DOUBLE) * CAST(gas_price AS DOUBLE) / 1e18,
            0.75
        ) AS p75_fee_native,
        COUNT(*) AS tx_count
    FROM evms.transactions
    WHERE blockchain IN (
            'base', 'arbitrum', 'optimism',
            'zksync', 'mantle', 'xlayer'
          )
      AND block_time >= date_trunc('month', date_add('year', -1, current_date))
      AND block_time <  date_trunc('month', current_date)
    GROUP BY 1, 2
),

native_prices AS (
    SELECT
        date_trunc('month', minute) AS month,
        symbol,
        AVG(price)                  AS avg_price_usd
    FROM prices.usd
    WHERE blockchain = 'ethereum'
      AND symbol IN ('WETH', 'MNT', 'OKB')
      AND minute >= date_trunc('month', date_add('year', -1, current_date))
      AND minute <  date_trunc('month', current_date)
    GROUP BY 1, 2
)

SELECT
    m.month,
    m.blockchain,
    m.median_fee_native * p.avg_price_usd  AS median_fee_usd,
    m.p25_fee_native    * p.avg_price_usd  AS p25_fee_usd,
    m.p75_fee_native    * p.avg_price_usd  AS p75_fee_usd,
    p.avg_price_usd                         AS native_token_price,
    m.tx_count
FROM monthly_median_native m
LEFT JOIN native_prices p
    ON  m.month = p.month
    AND p.symbol = CASE
        WHEN m.blockchain = 'mantle' THEN 'MNT'
        WHEN m.blockchain = 'xlayer' THEN 'OKB'
        ELSE 'WETH'
    END
ORDER BY m.blockchain, m.month
;
*/
