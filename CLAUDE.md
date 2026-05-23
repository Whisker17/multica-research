# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is the **Multica Research Squad** repository — a structured knowledge base of blockchain/L2 technical research. It contains deep-dive research projects covering Mantle, Base, Sui, and other chains. Research is produced by an agent-driven pipeline (research agents, adversarial reviewers, technical writers) and organized into self-contained project directories.

## Repository Structure

Each research project is a top-level directory (e.g., `base-azul-upgrade/`, `mantle-l2beat-risk-deficiency/`) containing three subdirectories:

```
<project-slug>/
  outlines/          # Research outlines with YAML frontmatter (scope, audience, dependencies)
  research-sections/ # The research artifacts
    _index.md        # Section registry: order, topic_slug, multica_issue_id, status
    <topic-slug>/
      drafts/        # Iterative drafts (round-1.md, round-2.md, ...)
      final.md       # Accepted final section
  report/
    final-report.md  # Synthesized report aggregating all sections
```

### Key file types

- **`_index.md`** — Markdown table tracking section order, dependencies, multica issue IDs, and completion status. This is the project's source of truth for what sections exist and their state.
- **Outlines** (`outlines/<topic-slug>.md`) — YAML frontmatter defining `topic`, `project_slug`, `topic_slug`, `scope`, `audience`, `expected_output`, `artifact_paths`, and `dependencies`. The body contains prioritized research items.
- **Drafts** (`research-sections/<topic>/drafts/round-{n}.md`) — Iterative drafts that go through adversarial review cycles.
- **Finals** (`research-sections/<topic>/final.md`) — Promoted from the last accepted draft.
- **Final reports** (`report/final-report.md`) — Technical writer synthesis of all sections into a single themed document with traceability matrix.

## Commit Message Conventions

Two patterns are used:

1. **Research section integration**: `research(<topic-slug>): integrate accepted research package (<multica-issue-uuid>)`
2. **Final report integration**: `Integrate TW final report: <project-slug>`

Earlier commits during the draft lifecycle use prefixes like `outline(...)`, `draft(...)`, `final(...)`, `index(...)`, `integrate(...)`.

## Current Research Projects

| Directory | Topic |
|-----------|-------|
| `base-vs-mantle-reth-analysis` | Base vs Mantle reth-based architecture comparison — execution client, batcher, derivation, proof system |
| `base-azul-upgrade` | Base's Azul hardfork — detachment from OP Stack, Multiproof, Flashblocks |
| `base-perf-analysis` | Base performance pipeline — sequencer, batcher, DA, gas config |
| `mantle-base-codebase-evaluation` | Mantle vs Base codebase comparison for enterprise adaptability |
| `mantle-enterprise-blockchain` | Mantle enterprise blockchain feasibility study |
| `mantle-l2beat-risk-deficiency` | Mantle L2Beat risk chart deficiencies (Proposer Failure, Exit Window) |
| `mantle-stage1-rollup` | Mantle Stage 1 rollup roadmap and compliance analysis |
| `sui-gasless-stablecoin-payments` | Sui gasless mechanism and stablecoin payment code analysis |

## Local Chain Codebases

When researching chain implementations or verifying source code, **prefer reading from local codebases** instead of fetching from GitHub. The local path is:

```
/Users/whisker/Work/src/networks/
```

Available chains:

| Directory | Chain |
|-----------|-------|
| `arbitrum` | Arbitrum |
| `base` | Base |
| `bnb` | BNB Chain |
| `canton` | Canton |
| `ethereum` | Ethereum |
| `lighter` | Lighter |
| `mantle` | Mantle |
| `optimism` | Optimism |
| `paladin` | Paladin |
| `starknet` | Starknet |
| `tempo` | Tempo |

Use these local sources for code analysis, cross-chain comparisons, and verifying implementation details referenced in research.

## Working with This Repo

- **Language**: Research content is primarily in Chinese (Mandarin). Outlines, reports, and analysis are written in Chinese unless the project scope specifies otherwise.
- **No build system**: This is a pure Markdown research repository. There are no dependencies, package managers, tests, or build steps.
- **Adding a new section**: Create an outline in `outlines/`, then add a row to `research-sections/_index.md`, then create `research-sections/<topic>/drafts/round-1.md`.
- **Promoting a draft**: Copy the accepted draft to `research-sections/<topic>/final.md` and update the status in `_index.md` to `done`.
