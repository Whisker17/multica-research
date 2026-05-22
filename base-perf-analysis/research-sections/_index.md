---
project: "解析 Base 的性能提升方式"
project_slug: base-perf-analysis
updated_at: "2026-05-22T12:45:00Z"
updated_by: "agent:orchestrator (Orchestrator, id=273629f0-3fe7-47c4-aae7-846a11dbbe13)"
---

# Research Sections Index

| order | topic_slug | multica_issue_id | final_path | dependencies | status | caveats |
|-------|-----------|------------------|------------|--------------|--------|---------|
| 1 | execution-layer-reth-fork-comparison | 747cb2ba-6502-41a3-9b08-35b743402f09 | base-perf-analysis/research-sections/execution-layer-reth-fork-comparison/final.md | - | done | - |
| 2 | block-builder-flashblocks-throughput | 49cd3543-e373-48d9-918b-55a167873968 | base-perf-analysis/research-sections/block-builder-flashblocks-throughput/final.md | - | done | C2, C3 (rerun-round-1, supersedes previous round-3 integration) |
| 3 | gas-protocol-perf-config | b5b2870f-fe64-42e5-a232-9acce565c195 | base-perf-analysis/research-sections/gas-protocol-perf-config/final.md | - | done | C1: process-deviation (outline revision cycle skipped; adversarial feedback substantively addressed in content) |
| 4 | sequencer-consensus-pipeline-perf | c0a26a72-9c25-42ca-9b0d-2563078d82c5 | base-perf-analysis/research-sections/sequencer-consensus-pipeline-perf/final.md | order-1,order-2 | done | - |
| 5 | batcher-pipeline-architecture | c75656d7-c1ae-45bc-a83b-c9b57be14299 | base-perf-analysis/research-sections/batcher-pipeline-architecture/final.md | order-3 | done | - |
| 6 | da-bandwidth-throughput-ceiling | 3c67e028-8610-4d45-8b30-06d84bf745f3 | base-perf-analysis/research-sections/da-bandwidth-throughput-ceiling/final.md | order-3 | done | - |
| 7 | batcher-sequencer-backpressure | 612c9aac-31ea-43f8-bac4-33eff4fe4e33 | base-perf-analysis/research-sections/batcher-sequencer-backpressure/final.md | batcher-pipeline-architecture, da-bandwidth-throughput-ceiling | done | - |
| 8 | perf-gap-analysis-recommendations | 8c2eae06-c797-4831-b7e0-b98d88739311 | base-perf-analysis/research-sections/perf-gap-analysis-recommendations/final.md | execution-layer-reth-fork-comparison, block-builder-flashblocks-throughput, gas-protocol-perf-config, sequencer-consensus-pipeline-perf, batcher-pipeline-architecture, da-bandwidth-throughput-ceiling, batcher-sequencer-backpressure | done | - |

## Caveats Registry

| ID | Section | Description | Re-verification target | Downstream issues |
|----|---------|-------------|----------------------|-------------------|
| C1 | gas-protocol-perf-config | Research agent skipped the outline revision round 2 (adversarial review returned revise on round 1). Orchestrator accept-risk: the adversarial feedback on Flashblocks TPS framing, activation-status gating, and scope boundaries was substantively addressed in the final content. The outline itself was not re-reviewed before drafting. | Downstream consumers (TW, perf-gap-analysis) should treat Flashblocks TPS framing, EIP-7825 activation status, and batcher/DA scope boundaries as validated in the final section text, not the outline. | WHI-57, WHI-63 |
| C2 | block-builder-flashblocks-throughput | Mantle-aware assessment (`feat/flashblocks-mantle-aware@58741b2`) is branch-range/tree-state evidence at the `58741b2` tip — preserve this nuance when summarizing; do not treat the assessment as a single-commit analysis. | TW and downstream consumers should note branch-range scope when citing Mantle compatibility conclusions. | WHI-56, WHI-63 |
| C3 | block-builder-flashblocks-throughput | diag-2 compresses the rollup-boost proxy path in the Flashblocks lifecycle diagram. Keep diag-1 as the authoritative Engine API routing diagram; do not imply a direct Seq → Builder FCU path in report prose. | TW report: use diag-1 for Engine API routing references; diag-2 is lifecycle overview only. | WHI-56, WHI-63 |
