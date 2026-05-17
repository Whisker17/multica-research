# Diagram Assets

All diagrams in `../final-report.md` are rendered as **Mermaid** inline.

## Why no `.png` / `.svg` files here?

Per `.claude/skills/technical-writer-reporting/references/diagram-upgrade-guide.md`, architecture and topology diagrams would normally be upgraded with `/fireworks-tech-graph` and emitted to this directory as paired `.svg` + `.png` files. That skill was **not accessible at runtime** in this Technical Writer Agent's environment. The guide's fallback rule applies:

> If `/fireworks-tech-graph` is not accessible at runtime:
> 1. Render ALL diagrams as Mermaid (including those that would normally be upgraded)
> 2. Add a note in the report appendix under "Methodology Notes"
> 3. Include this gap in the completion comment under "Unresolved Risks / Integration Gaps"
> 4. Do NOT block the report — it still ships with Mermaid-only diagrams

The gap is recorded in `../final-report.md` §10.1 (Methodology Notes) and §10.3 (Integration Gaps), and is propagated to the Final Report Ready completion comment.

## Future Maintainers

If `/fireworks-tech-graph` becomes available, the two diagrams most suited to upgrading are:

1. **§4.1 Aggregate verifier topology** — multi-layer with on-chain contracts, off-chain provers, and registry binding.
2. **§5.1 Off-chain service map** — five Rust services with L1/L2 RPC edges.

The remaining diagrams (state machine, sequence, fork-pair flow) are well-served by Mermaid and need not be upgraded.
