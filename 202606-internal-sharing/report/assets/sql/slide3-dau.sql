-- ═══════════════════════════════════════════════════════════════════════
-- Slide 3 — L2 Daily Active Users (DAU) Comparison
-- ═══════════════════════════════════════════════════════════════════════
-- Chains:  Base · Arbitrum · Optimism · zkSync · Mantle · X Layer
-- Period:  Past 12 months, monthly granularity
-- Method:  Count distinct tx senders per day → monthly average
-- Source:  evms.transactions (Dune cross-chain unified view)
-- ═══════════════════════════════════════════════════════════════════════
--
-- Notes:
--   1. Uses approx_distinct() (HyperLogLog, ~2% error) for query
--      performance — acceptable for presentation-level accuracy
--   2. X Layer chain name in Dune may be 'xlayer' or 'x_layer' —
--      adjust if no results returned
--   3. Includes all transaction senders (EOA + smart contract calls)
--   4. Current incomplete month is excluded to avoid misleading averages
--   5. Expected output: ~72 rows (6 chains × 12 months)
-- ═══════════════════════════════════════════════════════════════════════

WITH daily_counts AS (
    SELECT
        date_trunc('day', block_time)  AS day,
        blockchain,
        approx_distinct("from")        AS dau
    FROM evms.transactions
    WHERE blockchain IN (
            'base', 'arbitrum', 'optimism',
            'zksync', 'mantle', 'xlayer'
          )
      AND block_time >= date_trunc('month', date_add('year', -1, current_date))
      AND block_time <  date_trunc('month', current_date)
    GROUP BY 1, 2
)

SELECT
    date_trunc('month', day)   AS month,
    blockchain,
    CAST(AVG(dau)  AS BIGINT)  AS avg_dau,
    CAST(MAX(dau)  AS BIGINT)  AS peak_dau,
    CAST(MIN(dau)  AS BIGINT)  AS min_dau,
    COUNT(*)                    AS days_in_sample
FROM daily_counts
GROUP BY 1, 2
ORDER BY blockchain, month
