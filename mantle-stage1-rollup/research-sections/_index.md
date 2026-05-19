---
project: "Mantle 如何进入 Stage 1 Rollups"
project_slug: mantle-stage1-rollup
updated_at: "2026-05-19T08:55:00Z"
updated_by: "agent:orchestrator (Orchestrator, id=273629f0-3fe7-47c4-aae7-846a11dbbe13)"
---

# Research Sections Index

| order | topic_slug | multica_issue_id | final_path | dependencies | status | caveats |
|-------|-----------|------------------|------------|--------------|--------|---------|
| 1 | l2beat-stage-framework-2026 | 4a3e2e68-83df-44d9-a856-63efb733084e | mantle-stage1-rollup/research-sections/l2beat-stage-framework-2026/final.md | - | done | - |
| 2 | mantle-architecture-2026 | e7988e5f-a834-4ce6-99a8-9a53f52348a6 | mantle-stage1-rollup/research-sections/mantle-architecture-2026/final.md | - | done | - |
| 3 | stage1-case-studies | 856af005-11a9-4812-be51-f76a1bd7ff95 | mantle-stage1-rollup/research-sections/stage1-case-studies/final.md | - | done | C1: exit-window cell re-verification; C2: Starknet gate-4 sourcing re-verification |
| 4 | upgrade-exitwindow-securitycouncil | 6cc99efe-e183-4588-a6d7-c2f61efb19ae | mantle-stage1-rollup/research-sections/upgrade-exitwindow-securitycouncil/final.md | l2beat-stage-framework-2026, mantle-architecture-2026, stage1-case-studies | done | - |
| 5 | proposer-decentralization-zk-compliance | cc2b0693-6554-4866-83b9-401cfd232570 | mantle-stage1-rollup/research-sections/proposer-decentralization-zk-compliance/final.md | l2beat-stage-framework-2026, mantle-architecture-2026, stage1-case-studies | done | - |

## Caveats Registry

| ID | Section | Description | Re-verification target | Downstream issues |
|----|---------|-------------|----------------------|-------------------|
| C1 | stage1-case-studies | OP Mainnet and Scroll Item-7(C) exit-window matrix cells require re-verification against current L2Beat live data | L2Beat project pages: Stages section + permissions section for OP Mainnet, Scroll | WHI-42, WHI-43, WHI-44 |
| C2 | stage1-case-studies | Starknet gate (4) program-commitment risk sourcing should be re-verified against current L2Beat + ZK Catalog data | l2beat.com/scaling/projects/starknet proof system section; zk-catalog.dev Starknet entry | WHI-42, WHI-43, WHI-44 |
