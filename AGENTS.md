# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

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

**Structural variants:** Not every section has a `drafts/` folder (some go straight to `final.md`), and some sections carry their own evidence subdirs such as `datasets/` or `source-data/` (e.g. `202606-internal-sharing/research-sections/competitor-solana/datasets/`). A few directories are scaffolding stubs with only an empty `research-sections/` (e.g. `compliant-token-standards/`) — treat these as not-yet-started.

### Key file types

- **`_index.md`** — Markdown table tracking section order, dependencies, multica issue IDs, and completion status. This is the project's source of truth for what sections exist and their state.
- **Outlines** (`outlines/<topic-slug>.md`) — YAML frontmatter defining `topic`, `project_slug`, `topic_slug`, `scope`, `audience`, `expected_output`, `artifact_paths`, and `dependencies`. The body contains prioritized research items.
- **Drafts** (`research-sections/<topic>/drafts/round-{n}.md`) — Iterative drafts that go through adversarial review cycles.
- **Finals** (`research-sections/<topic>/final.md`) — Promoted from the last accepted draft.
- **Final reports** (`report/final-report.md`) — Technical writer synthesis of all sections into a single themed document with traceability matrix.

### Presentation/deck projects

Some projects (notably `202606-internal-sharing/`) extend the report stage into a full presentation deliverable under `report/assets/`:

- `slides-outline.md` — slide-by-slide deck outline; `speech-zh.md` / `speech-en.md` — bilingual speaker scripts.
- `charts/` — **Python (matplotlib/pandas) chart generators** (`generate_slideN_charts.py`) that read CSVs from `data/` and emit `.png`/`.svg` into `charts/`. Per-chain brand colors are hardcoded in each script.
- `data/` — source CSVs; `sql/` — the Dune/SQL queries that produced them; `data-source-annotations.md` — provenance for every figure.
- `supplementary/` — long-form supporting research that backs specific slides.

## Commit Message Conventions

Two patterns are used:

1. **Research section integration**: `research(<topic-slug>): integrate accepted research package (<multica-issue-uuid>)`
2. **Final report integration**: `Integrate TW final report: <project-slug>`

Earlier commits during the draft lifecycle use prefixes like `outline(...)`, `draft(...)`, `final(...)`, `index(...)`, `integrate(...)`, `promote(...)`. Deck projects additionally use `slides(...)`, `tw(...)`.

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
| `compliance-token-standards` | Compliance/RWA token standards comparison (ERC-3643/T-REX, ERC-1400, Base B20, Tempo TIP-20) + Mantle strategy |
| `repo-github-actions` | Cross-chain CI/CD (GitHub Actions) comparison across reth/geth/Base/OP/Solana/Tempo + Mantle gap analysis |
| `hoodi-launch-notice` | Hoodi testnet launch notice and reth adoption trends |
| `202606-internal-sharing` | Internal-sharing presentation: competitor/narrative/payment/enterprise landscape → slide deck, charts, bilingual speech |
| `compliant-token-standards` | Empty scaffolding stub (superseded by `compliance-token-standards`) |

## Creating Issues (multica CLI)

Issues are managed through the local `multica` CLI (`multica issue …`; `multica issue create --help` for flags).

**When creating any issue, you MUST follow the canonical template at [`.multica/issue-template.md`](.multica/issue-template.md).** Do not free-form an issue body. Specifically:

- **Title**: `[类别] 简短动宾式标题` — reuse an existing category prefix (`[Research]`, `[Analysis]`, `[M2-对比]`, `[Config]`, `[Infra]`, `[Reporter]`, `[Daily]`, …); invent a new one only when none fits, then update the template and this section together.
- **Body** (Chinese, Markdown, in this order): `## 目标` (required), then as needed `## 背景` / `## 范围 / 输入` / `## 执行步骤`, then the required closers `## 交付物`, `## 验收标准` (checkbox list), `## Review 要求`, `## 依赖`. Research/analysis issues must include `## 执行步骤`; engineering/ops issues may omit it when the task is already atomic. Engineering issues may prepend `## Parent` / `## Spec` / `## Blocked By` / `## Blocks`.
- **交付物** must list exact output paths and end with "完成后在本 issue 评论中贴交付物链接"; **验收标准** for research must require each conclusion to cite a file path/URL + commit SHA, and external web/doc conclusions must include access date or version.
- **Create** with the body in a file to preserve multi-line Chinese content:
  ```bash
  multica issue create --title "[Research] <标题>" --priority low --description-file /tmp/issue-body.md
  ```

See the template file for the full section-by-section spec and a copy-paste skeleton. If you change the conventions, update `.multica/issue-template.md` and this section together.

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
- **Mostly no build system**: Research content is pure Markdown — no package manager, tests, or build steps. The lone exception is the deck chart pipeline (`report/assets/charts/*.py`), which needs Python with `pandas`/`matplotlib`/`numpy`; run a generator from its `charts/` dir to regenerate the `.png`/`.svg` for that slide.
- **Adding a new section**: Create an outline in `outlines/`, then add a row to `research-sections/_index.md`, then create `research-sections/<topic>/drafts/round-1.md`.
- **Promoting a draft**: Copy the accepted draft to `research-sections/<topic>/final.md` and update the status in `_index.md` to `done`.
- **Diagrams**: The `fireworks-tech-graph` skill (vendored under `.agents/skills/`, pinned in `skills-lock.json`) generates technical architecture diagrams as SVG+PNG — use it for new slide/report diagrams rather than hand-authoring SVG.
