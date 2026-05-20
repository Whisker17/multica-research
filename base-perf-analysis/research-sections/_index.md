---
project: "解析 Base 的性能提升方式"
project_slug: base-perf-analysis
updated_at: "2026-05-20T05:52:00Z"
updated_by: "agent:orchestrator (Orchestrator, id=273629f0-3fe7-47c4-aae7-846a11dbbe13)"
---

# Research Sections Index

| order | topic_slug | multica_issue_id | final_path | dependencies | status | caveats |
|-------|-----------|------------------|------------|--------------|--------|---------|
| 1 | execution-layer-reth-fork-comparison | 747cb2ba-6502-41a3-9b08-35b743402f09 | base-perf-analysis/research-sections/execution-layer-reth-fork-comparison/final.md | - | done | - |
| 2 | block-builder-flashblocks-throughput | 49cd3543-e373-48d9-918b-55a167873968 | base-perf-analysis/research-sections/block-builder-flashblocks-throughput/final.md | - | done | - |
| 3 | gas-protocol-perf-config | b5b2870f-fe64-42e5-a232-9acce565c195 | base-perf-analysis/research-sections/gas-protocol-perf-config/final.md | - | done | C1: process-deviation (outline revision cycle skipped; adversarial feedback substantively addressed in content) |

## Caveats Registry

| ID | Section | Description | Re-verification target | Downstream issues |
|----|---------|-------------|----------------------|-------------------|
| C1 | gas-protocol-perf-config | Research agent skipped the outline revision round 2 (adversarial review returned revise on round 1). Orchestrator accept-risk: the adversarial feedback on Flashblocks TPS framing, activation-status gating, and scope boundaries was substantively addressed in the final content. The outline itself was not re-reviewed before drafting. | Downstream consumers (TW, perf-gap-analysis) should treat Flashblocks TPS framing, EIP-7825 activation status, and batcher/DA scope boundaries as validated in the final section text, not the outline. | WHI-57, WHI-63 |
