# Starknet GitHub Activity Source Data

This directory preserves the raw source artifacts behind the 117-repo activity ranking used in `../../final.md`.

- `graphql-metrics.json`: per-repo metric objects from the completed GitHub GraphQL / `gh` candidate pass.
- `graphql-leaderboard.tsv`: sorted leaderboard derived from the same metrics.

Window: `2026-02-23..2026-05-23` UTC.

The candidate set covers active seed-org repos plus discovered related Starknet ecosystem repos. It is not a complete 235-repo long-tail dump; that full REST crawl was interrupted by network resets, as recorded in the final section gap analysis.
