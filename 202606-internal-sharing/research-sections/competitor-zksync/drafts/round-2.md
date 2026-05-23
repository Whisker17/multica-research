---
topic: "zkSync 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-zksync"
github_repo: "Whisker17/multica-research"
round: 2
status: draft

artifact_paths:
  outline: "202606-internal-sharing/outlines/competitor-zksync.md"
  draft: "202606-internal-sharing/research-sections/competitor-zksync/drafts/round-2.md"
  final: "202606-internal-sharing/research-sections/competitor-zksync/final.md"
  index: "202606-internal-sharing/research-sections/_index.md"

draft_metadata:
  created_by: "agent:research-agent (Deep Research Agent, id=13a888db-49bb-4a19-9906-827729e156d9)"
  created_at: "2026-05-24T05:54:05+08:00"
  mode: revision_deep_draft
  revision_from_round: 1
  revision_reason: "Round-1 draft review requested durable source/evidence appendix because raw data exports were only referenced as session-local files."
  outline_path: "202606-internal-sharing/outlines/competitor-zksync.md"
  outline_commit: "90069f3b0553bf596fe7d4dbb3814ae08eb27bc7"
  outline_approval_source: "Review Verdict outline-approved comment 2e11cb90-ceae-466a-aa52-69cc4e9d04de; Orchestrator deep-draft dispatch b679deab-d1f3-4d6d-98be-cd7522c71beb"
  outline_file_status_note: "Persisted outline frontmatter remains status:candidate; Orchestrator consensus and deep-draft dispatch are treated as the Phase B approval gate. This draft does not edit the outline."
  branch: "research/202606-internal-sharing/competitor-zksync"
  language: "zh-CN"
  research_depth: standard
  verification_date: "2026-05-23"
  github_query_window: "2026-02-23T00:00:00Z..2026-05-23T23:59:59Z"
  github_query_timestamp_utc: "2026-05-23T21:29:17Z"
  methodology_gate_result: "completed before PR/narrative analysis"
  source_appendix: "202606-internal-sharing/research-sections/competitor-zksync/drafts/round-2-sources.md"
  source_appendix_generated_at_utc: "2026-05-23T21:54:05Z"
  phase_b_guardrail_applied:
    - "Reran segmented GitHub PR search for the exact 2026-02-23..2026-05-23 UTC window instead of reusing outline pre-scan counts."
    - "Recomputed branch-aware default-branch commit counts via GitHub REST/GraphQL per active repo; raw and normalized values are recorded in the ranking table."
    - "Explained Top 8 changes versus outline pre-scan: zksync-era moves to composite rank 2; era-contracts and zksync-os remain high on PR metrics but lower on commit metric."
    - "Preserved caveat that GitHub Search commit counts and default-branch commit counts can undercount non-default branch, sync/generated, squash-merge, private/internal, or workflow-generated work."
  source_caveats:
    - "GitHub data covers public repositories only; private Matter Labs work and internal planning are invisible."
    - "PR created counts use GitHub issue search segmented into 2026-02-23..03-31, 04-01..04-30, 05-01..05-23 to avoid the 1000-result cap; single-window matter-labs search hits the cap."
    - "Merged counts in the main ranking are PRs created in the window and merged by collection time; a supporting merged-at query was also run for Top 25 repos."
    - "Commit counts are default-branch, branch-aware public commits in the UTC window; they can undercount feature branches, generated sync flows, squash-merge internals, and non-default release branches."
    - "Representative PR classification is a research taxonomy based on title/path/body sampling, not an official Matter Labs label set."
    - "External docs/blog sources are used for public narrative and maturity labels; code evidence remains primary for engineering-activity conclusions."
  items_covered: [item-1, item-2, item-3, item-4, item-5, item-6, item-7, item-8, item-9, item-10, item-11, item-12]
  diagrams_produced: [diag-1, diag-2, diag-3, diag-4, diag-5]
---

# zkSync 近期开发与叙事分析 - Round 2 Draft

## 1. Executive Summary

本轮研究先做全 org repo discovery/ranking，再进入 PR 分类和叙事分析。2026-02-23 至 2026-05-23 UTC 窗口内，扫描 `matter-labs`、`zkSync-Community-Hub`、`zksync-sdk`、`zksync-association`、`zksync` 五个可见 GitHub org，共 **274 个 public repo**；非 archived 且非 fork repo 为 **185 个**。通过三段 GitHub PR search 去重后得到 **1,427 个 created PR**、**911 个 created-in-window 且已 merged PR**。`matter-labs` 贡献了绝大多数工程活动，其他 org 主要提供治理、社区和 legacy SDK supporting signals。

最核心的数据结论是：**近期 ZKsync 工程重心不是单一 `zksync-era`，而是 `zksync-os-server` 绝对领先，`zksync-era`、`era-contracts`、`zksync-os`、`zksync-airbender`、compiler/tooling 和 Airbender platform 组成第二梯队。** Composite score Top 8 为：

1. `matter-labs/zksync-os-server` - 404 PR、238 merged、227 default-branch commits、34 human PR authors，score 100；
2. `matter-labs/zksync-era` - 130 PR、88 merged、60 commits、27 authors，score 42.70；
3. `matter-labs/era-contracts` - 154 PR、95 merged、4 commits、23 authors，score 36.32；
4. `matter-labs/zksync-os` - 146 PR、72 merged、2 commits、12 authors，score 30.68；
5. `matter-labs/zksync-airbender` - 94 PR、73 merged、2 commits、17 authors，score 25.99；
6. `matter-labs/solx-llvm` - 56 PR、52 merged、92 commits，score 22.68；
7. `matter-labs/airbender-platform` - 49 PR、38 merged、42 commits，score 17.97；
8. `matter-labs/zksync-js` - 39 PR、30 merged、30 commits，score 16.07。

相对 outline pre-scan，Top 8 集合不变，但顺序有关键修正：**`zksync-era` 从预扫描 rank 4 升到 composite rank 2**，原因是 branch-aware commit count 和 contributor count 明显高于 `era-contracts`/`zksync-os`。这不推翻 "Era 不是唯一主仓" 的方法论，反而说明 ZKsync 近期是 **Era release/API/compatibility + OS/server/prover/contracts 多仓并行**，不能用单仓叙事解释。

PR 级事实显示五条工程主线最强：

- **ZKsync OS server / sequencer / RPC / Gateway launch hardening**：`zksync-os-server` 是全窗口最活跃仓库，PR 热区包括 consensus/RPC forwarding、L1 watcher consistency、JSON-RPC rate limiting、`eth_simulateV1` gas estimation、S3 replay archive、Merkle tree proof I/O 优化、Gateway launch configs。
- **v31 / Gateway / contracts / governance**：`era-contracts`、`zksync-era`、`zk-governance` 同期出现 v31 fixes、FRI verifier、L1 interop contracts、verification keys、ProtocolUpgradeHandler、SecurityCouncil 8 members / 6-of-8 threshold、freezability/audit fixes。
- **ZKsync OS / RISC-V STF / MultiVM**：`zksync-os` README 明确它是 Rust/RISC-V state transition function，支持 EVM、EraVM、Wasm 等多 execution environments；近期 PR 集中在 EVM interpreter optimization、oracle transport migration、Airbender crypto/platform migration、bootloader tx flow、native prover interface。
- **Airbender proving stack**：`zksync-airbender`、`airbender-platform`、`eravm-airbender-verifier` 同时活跃，覆盖 GPU prover、WHIR/GKR/verifier、FRI/SNARK pipeline、VK handling、v31 wire format compatibility、RISC-V provable program toolchain。
- **Tooling / SDK / enterprise packaging**：`solx-llvm` 是 compiler 活跃中心；`zksync-js` 重点是 interop/Gateway docs/tests/functions；`foundry-zksync` 主要是 upstream merge、zksolc pin、cast gas-per-pubdata fixes；`local-prividium` 和 `zksync-sso` 显示 enterprise sandbox、Keycloak/Prividium API、SSO/ERC-4337/zksync-os local stack 正在迭代。

叙事上，ZKsync 的公开定位正在从 "Era ZK Rollup / ZK Stack" 扩展为 **ZKsync OS + Airbender + Elastic Chain/Gateway + Prividium/enterprise + native AA/SSO + developer tooling**。代码证据最强的是 OS server、OS/STF、Airbender、contracts/v31/Gateway 和 JS/SDK/tooling；企业/Prividium/SSO 有可见代码和 local environment，但生产 customer evidence 仍需官方客户/部署资料验证，不能把 local sandbox 当成主网采用。

对 Mantle 的竞争启示：短期应把 ZKsync OS server、v31/Gateway contracts、Airbender verifier/prover、SSO/Prividium 设为 watchlist；中期应评估 zkVM/RISC-V prover stack、multi-chain settlement/Gateway、native AA/SSO、enterprise local stack 的取舍；叙事上不能只用 "OP Stack compatible + DA cheaper" 对抗，应更明确 Mantle 在 settlement/security/governance、EigenDA economics、developer migration、enterprise privacy/permissioning 上的组合优势。

## 2. Item Findings

### item-1: Org 与 repo universe 全量发现

**执行顺序确认**：本 draft 先扫描 repo universe，再排序，再进入 PR 深挖。查询窗口固定为 `2026-02-23T00:00:00Z..2026-05-23T23:59:59Z`。抓取时间为 2026-05-23T21:29Z 左右。

**查询方式**

```shell
gh repo list matter-labs --limit 1000 \
  --json name,nameWithOwner,url,description,isArchived,isFork,isPrivate,primaryLanguage,stargazerCount,forkCount,createdAt,updatedAt,pushedAt,defaultBranchRef

gh search prs --owner {org} --created 2026-02-23..2026-03-31 --limit 1000
gh search prs --owner {org} --created 2026-04-01..2026-04-30 --limit 1000
gh search prs --owner {org} --created 2026-05-01..2026-05-23 --limit 1000

gh api repos/{owner}/{repo}/commits?sha={default_branch}&since=2026-02-23T00:00:00Z&until=2026-05-23T23:59:59Z&per_page=1 --include
gh api --paginate repos/{owner}/{repo}/commits?sha={default_branch}&since=2026-02-23T00:00:00Z&until=2026-05-23T23:59:59Z&per_page=100
```

**Repo universe 摘要**

| org | total public repos | 非 archived/fork | archived | fork | created PR | merged PR(created-window) | 处理 |
|---|---:|---:|---:|---:|---:|---:|---|
| `matter-labs` | 230 | 151 | 48 | 44 | 1408 | 900 | 核心工程 universe |
| `zkSync-Community-Hub` | 8 | 7 | 1 | 0 | 2 | 0 | 社区/docs 背景，不进入主排名 |
| `zksync-sdk` | 24 | 15 | 5 | 4 | 6 | 5 | legacy SDK background；`zksync-ethers` supporting |
| `zksync-association` | 11 | 11 | 0 | 0 | 11 | 6 | governance/security supporting |
| `zksync` | 1 | 1 | 0 | 0 | 0 | 0 | official/credo background |
| **Total** | **274** | **185** | **54** | **48** | **1427** | **911** | full scan complete |

**Universe classification**

| repo type | examples | ranking treatment |
|---|---|---|
| OS server / node runtime | `zksync-os-server`, `watchdog`, `zksync-server-action` | primary if active |
| OS STF / MultiVM | `zksync-os`, `zksync-os-interface`, `zksync-os-revm` | primary/supporting |
| Prover / Airbender | `zksync-airbender`, `airbender-platform`, `eravm-airbender-verifier`, `zksync-airbender-prover` | primary/supporting |
| Era core | `zksync-era` | primary |
| Contracts / Gateway / governance | `era-contracts`, `zksync-protocol`, `zk-governance`, `zkminters` | primary/supporting |
| Compiler / tooling / SDK | `solx-llvm`, `foundry-zksync`, `zksync-js`, `zksync-ethers`, `hardhat-zksync` | primary/supporting |
| Enterprise / Prividium / SSO | `local-prividium`, `zksync-sso`, `zksync-sso-contracts` | supporting, with maturity caveat |
| Docs/community/legacy | `zksync-docs`, `community-code`, archived SDK repos | supporting, not engineering-primary |
| Fork/mirror/dependency | `grafana`, `reth`, assorted forks | excluded from ranking even when commit-heavy |

Notable exclusion: `matter-labs/grafana` and `matter-labs/reth` show high branch commit counts, but both are forks (`grafana` fork of Grafana; `reth` archived fork of Paradigm reth). They are excluded from non-fork ranking to avoid reading upstream/mirror churn as ZKsync roadmap signal.

### item-2: 活跃度排名与 Top repo 选择

**Ranking formula**

```
score = 100 * (
  0.35 * norm(PR created)
  + 0.25 * norm(PR merged among created-window PRs)
  + 0.20 * norm(default-branch commits)
  + 0.15 * norm(active human PR authors)
  + 0.05 * release/push recency
)
```

Normalization uses max value among non-archived, non-fork repos. Recency = release-in-window and/or recent default-branch push, capped at 1.0. Bots are excluded from `active human PR authors`; bot PR count is retained as a caveat field.

**Top 18 ranking with raw and normalized values** (full Top 20 raw ranking data is committed in `round-2-sources.md`)

| Rank | repo | PR | PRn | merged | Mn | commits | Cn | authors | An | rec | score | sensitivity P/M/C/A |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `matter-labs/zksync-os-server` | 404 | 1.000 | 238 | 1.000 | 227 | 1.000 | 34 | 1.000 | 1.00 | 100.00 | 1/1/1/1 |
| 2 | `matter-labs/zksync-era` | 130 | 0.322 | 88 | 0.370 | 60 | 0.264 | 27 | 0.794 | 1.00 | 42.70 | 4/3/4/2 |
| 3 | `matter-labs/era-contracts` | 154 | 0.381 | 95 | 0.399 | 4 | 0.018 | 23 | 0.676 | 0.50 | 36.32 | 2/2/28/3 |
| 4 | `matter-labs/zksync-os` | 146 | 0.361 | 72 | 0.303 | 2 | 0.009 | 12 | 0.353 | 1.00 | 30.68 | 3/5/34/5 |
| 5 | `matter-labs/zksync-airbender` | 94 | 0.233 | 73 | 0.307 | 2 | 0.009 | 17 | 0.500 | 0.50 | 25.99 | 5/4/33/4 |
| 6 | `matter-labs/solx-llvm` | 56 | 0.139 | 52 | 0.218 | 92 | 0.405 | 4 | 0.118 | 0.50 | 22.68 | 6/6/2/20 |
| 7 | `matter-labs/airbender-platform` | 49 | 0.121 | 38 | 0.160 | 42 | 0.185 | 8 | 0.235 | 0.50 | 17.97 | 7/7/5/6 |
| 8 | `matter-labs/zksync-js` | 39 | 0.097 | 30 | 0.126 | 30 | 0.132 | 6 | 0.176 | 0.85 | 16.07 | 8/8/6/13 |
| 9 | `matter-labs/zksync-os-interface` | 21 | 0.052 | 20 | 0.084 | 22 | 0.097 | 7 | 0.206 | 1.00 | 13.95 | 12/11/7/9 |
| 10 | `matter-labs/foundry-zksync` | 25 | 0.062 | 12 | 0.050 | 61 | 0.269 | 3 | 0.088 | 0.65 | 13.37 | 10/14/3/26 |
| 11 | `matter-labs/block-explorer` | 22 | 0.054 | 21 | 0.088 | 20 | 0.088 | 5 | 0.147 | 1.00 | 13.08 | 11/10/8/15 |
| 12 | `matter-labs/eravm-airbender-verifier` | 32 | 0.079 | 21 | 0.088 | 19 | 0.084 | 7 | 0.206 | 0.50 | 12.24 | 9/9/9/8 |
| 13 | `matter-labs/watchdog` | 19 | 0.047 | 14 | 0.059 | 15 | 0.066 | 6 | 0.176 | 1.00 | 12.09 | 14/13/12/10 |
| 14 | `matter-labs/zksync-airbender-prover` | 17 | 0.042 | 10 | 0.042 | 10 | 0.044 | 8 | 0.235 | 1.00 | 11.93 | 15/17/17/7 |
| 15 | `matter-labs/zksync-docs` | 16 | 0.040 | 10 | 0.042 | 10 | 0.044 | 6 | 0.176 | 1.00 | 10.96 | 16/16/16/11 |
| 16 | `matter-labs/zkos-wrapper` | 12 | 0.030 | 10 | 0.042 | 7 | 0.031 | 5 | 0.147 | 1.00 | 9.91 | 19/18/22/17 |
| 17 | `matter-labs/local-prividium` | 20 | 0.050 | 15 | 0.063 | 16 | 0.070 | 5 | 0.147 | 0.50 | 9.42 | 13/12/10/14 |
| 18 | `matter-labs/zksync-protocol` | 11 | 0.027 | 4 | 0.017 | 4 | 0.018 | 6 | 0.176 | 1.00 | 9.37 | 20/26/29/12 |

**Sensitivity check**

| single metric | Top 10 |
|---|---|
| PR-only | `zksync-os-server`, `era-contracts`, `zksync-os`, `zksync-era`, `zksync-airbender`, `solx-llvm`, `airbender-platform`, `zksync-js`, `eravm-airbender-verifier`, `foundry-zksync` |
| merged-only | `zksync-os-server`, `era-contracts`, `zksync-era`, `zksync-airbender`, `zksync-os`, `solx-llvm`, `airbender-platform`, `zksync-js`, `block-explorer`, `eravm-airbender-verifier` |
| commit-only | `zksync-os-server`, `solx-llvm`, `foundry-zksync`, `zksync-era`, `airbender-platform`, `zksync-js`, `zksync-os-interface`, `block-explorer`, `eravm-airbender-verifier`, `local-prividium` |
| contributors-only | `zksync-os-server`, `zksync-era`, `era-contracts`, `zksync-airbender`, `zksync-os`, `airbender-platform`, `zksync-airbender-prover`, `zksync-os-interface`, `eravm-airbender-verifier`, `zksync-js` |

**Top repo selection and changes from outline**

Top 8 remains: `zksync-os-server`, `zksync-era`, `era-contracts`, `zksync-os`, `zksync-airbender`, `solx-llvm`, `airbender-platform`, `zksync-js`.

Changes versus outline pre-scan:

- `zksync-era` rises from outline rank 4 to composite rank 2 because branch-aware commit count (60) and human PR authors (27) are strong.
- `era-contracts` remains PR-heavy but drops behind `zksync-era` in composite rank because default-branch commits are only 4. This may reflect branch/squash/sync workflows, so the draft still treats contracts/v31/Gateway as high strategic signal.
- `zksync-os` remains PR-heavy but commit-light on default branch; PR bodies and release activity still justify primary analysis.
- `foundry-zksync` is commit-only rank 3 but composite rank 10; it is supporting tooling rather than primary Top 8 because PR volume and human PR authors are much lower.
- `zksync-os-interface`, `eravm-airbender-verifier`, `zksync-airbender-prover`, `local-prividium`, `zksync-sso`, `zk-governance` are supporting repos because they carry important subsystem evidence despite lower composite score.

### item-3: Top repo PR 活动基线与趋势

| repo | created PR | merged(created-window) | merged-at window | open | closed-unmerged | top weeks | top authors |
|---|---:|---:|---:|---:|---:|---|---|
| `zksync-os-server` | 404 | 238 | 243 | 39 | 127 | W13 61, W11 61, W12 39 | `perekopskiy`, `romanbrodetski-ai`, `LogvinovLeon`, `zksync-era-bot`, `Artemka374` |
| `zksync-era` | 130 | 88 | 97 | 21 | 21 | W11 17, W13 16, W17 16 | `zkzoomer`, `zksync-era-bot`, `Deniallugo`, `hatemosphere` |
| `era-contracts` | 154 | 95 | 109 | 25 | 34 | W16 29, W15 20, W12 18 | `kelemeno`, `valera-grinenko-ai`, `StanislavBreadfulAI`, `zkzoomer` |
| `zksync-os` | 146 | 72 | 77 | 32 | 42 | W20 20, W12 19, W13 16 | `0xVolosnikov`, `antoniolocascio`, `vv-dev-ai`, `vibelyova` |
| `zksync-airbender` | 94 | 73 | 74 | 9 | 12 | W12 13, W11 12, W09 12 | `popzxc`, `shamatar`, `robik75`, `yoaveshel` |
| `solx-llvm` | 56 | 52 | 53 | 3 | 1 | W11 9, W17 7, W16 7 | `vladimirradosavljevic`, `PavelKopyl`, `abinavpp` |
| `airbender-platform` | 49 | 38 | 38 | 3 | 8 | W13 10, W14 8, W19 7 | `ia-agentic`, `vibelyova`, `Jrigada`, `nbaztec` |
| `zksync-js` | 39 | 30 | 30 | 4 | 5 | W13 7, W14 6, W12 5 | `vasyl-ivanchuk`, `dutterbutter`, `zksync-era-bot` |

**Representative PR evidence**

| repo | representative PRs | signal |
|---|---|---|
| `zksync-os-server` | [#1322](https://github.com/matter-labs/zksync-os-server/pull/1322), [#1317](https://github.com/matter-labs/zksync-os-server/pull/1317), [#1315](https://github.com/matter-labs/zksync-os-server/pull/1315), [#1310](https://github.com/matter-labs/zksync-os-server/pull/1310), [#1297](https://github.com/matter-labs/zksync-os-server/pull/1297), [#1241](https://github.com/matter-labs/zksync-os-server/pull/1241), [#1319](https://github.com/matter-labs/zksync-os-server/pull/1319), [#1308](https://github.com/matter-labs/zksync-os-server/pull/1308) | consensus/RPC forwarding, EN L1 consistency, Gateway-launch artifacts, JSON-RPC errors/rate limits, Merkle tree proof I/O, replay archive, gas simulation |
| `zksync-era` | [#4817](https://github.com/matter-labs/zksync-era/pull/4817), [#4816](https://github.com/matter-labs/zksync-era/pull/4816), [#4813](https://github.com/matter-labs/zksync-era/pull/4813), [#4811](https://github.com/matter-labs/zksync-era/pull/4811), [#4809](https://github.com/matter-labs/zksync-era/pull/4809), [#4807](https://github.com/matter-labs/zksync-era/pull/4807), [#4801](https://github.com/matter-labs/zksync-era/pull/4801), [#4796](https://github.com/matter-labs/zksync-era/pull/4796) | proving networks, debug/API compatibility, protocol upgrade automation, Airbender SNARK/FRI data handling, v31 DA gating, interop bootloader |
| `era-contracts` | [#2202](https://github.com/matter-labs/era-contracts/pull/2202), [#2200](https://github.com/matter-labs/era-contracts/pull/2200), [#2198](https://github.com/matter-labs/era-contracts/pull/2198), [#2188](https://github.com/matter-labs/era-contracts/pull/2188), [#2186](https://github.com/matter-labs/era-contracts/pull/2186), [#2192](https://github.com/matter-labs/era-contracts/pull/2192), [#2181](https://github.com/matter-labs/era-contracts/pull/2181), [#2195](https://github.com/matter-labs/era-contracts/pull/2195) | FRI verifier, L1 interop contracts, v31 fixes, OZ audit fixes, v31 verification keys, AssetRouter/Gateway fixes, Sepolia v31 ecosystem registration |
| `zksync-os` | [#663](https://github.com/matter-labs/zksync-os/pull/663), [#660](https://github.com/matter-labs/zksync-os/pull/660), [#655](https://github.com/matter-labs/zksync-os/pull/655), [#652](https://github.com/matter-labs/zksync-os/pull/652), [#646](https://github.com/matter-labs/zksync-os/pull/646), [#641](https://github.com/matter-labs/zksync-os/pull/641), [#634](https://github.com/matter-labs/zksync-os/pull/634), [#673](https://github.com/matter-labs/zksync-os/pull/673) | oracle transport, KZG verifier, host verification, RISC-V EVM interpreter specialization, Airbender crypto migration, bootloader zk tx flow |
| `zksync-airbender` | [#305](https://github.com/matter-labs/zksync-airbender/pull/305), [#302](https://github.com/matter-labs/zksync-airbender/pull/302), [#300](https://github.com/matter-labs/zksync-airbender/pull/300), [#291](https://github.com/matter-labs/zksync-airbender/pull/291), [#290](https://github.com/matter-labs/zksync-airbender/pull/290), [#288](https://github.com/matter-labs/zksync-airbender/pull/288), [#280](https://github.com/matter-labs/zksync-airbender/pull/280), [#277](https://github.com/matter-labs/zksync-airbender/pull/277) | GKR circuit, V2 tests, RISC-V verifier perf, structured prover config, GPU prover optimization, public verifier interfaces, benchmarking |
| `airbender-platform` | [#66](https://github.com/matter-labs/airbender-platform/pull/66), [#64](https://github.com/matter-labs/airbender-platform/pull/64), [#60](https://github.com/matter-labs/airbender-platform/pull/60), [#58](https://github.com/matter-labs/airbender-platform/pull/58), [#52](https://github.com/matter-labs/airbender-platform/pull/52), [#47](https://github.com/matter-labs/airbender-platform/pull/47), [#34](https://github.com/matter-labs/airbender-platform/pull/34), [#32](https://github.com/matter-labs/airbender-platform/pull/32) | release pipeline, GPU setup cache, Secp256k1 hooks, CPU prover RAM checks, cargo-airbender templating, raw proof access, cycle marker API |
| `zksync-js` | [#106](https://github.com/matter-labs/zksync-js/pull/106), [#95](https://github.com/matter-labs/zksync-js/pull/95), [#92](https://github.com/matter-labs/zksync-js/pull/92), [#85](https://github.com/matter-labs/zksync-js/pull/85), [#82](https://github.com/matter-labs/zksync-js/pull/82), [#77](https://github.com/matter-labs/zksync-js/pull/77), [#80](https://github.com/matter-labs/zksync-js/pull/80), [#94](https://github.com/matter-labs/zksync-js/pull/94) | interop tests/docs, tx overrides, verifyBundle/getInteropRoot, viem interop resource, v31/Gateway support, zks_getProof, priority gas estimation |

### item-4: PR 分类体系与开发方向归因

Classification method: PR title/path/body sampling, with representative PR body/files reviewed for high-signal claims. Counts are directional, not official labels.

| repo | category distribution | interpretation |
|---|---|---|
| `zksync-os-server` | OS server/RPC 117; Gateway/contracts 105; product code 87; maintenance/CI 46; tooling 19; enterprise/ops 14; Airbender 10 | The server is not a side project: it is where sequencing, RPC, Gateway launch hardening, replay/archive, L1 watcher, and proof-adjacent paths converge. |
| `zksync-era` | Gateway/contracts 37; Airbender/prover 30; product code 23; maintenance 19; tooling/API 12; server/RPC 9 | Era remains active but recent work often bridges old Era surfaces to Airbender/v31/API compatibility rather than standalone new narrative. |
| `era-contracts` | Gateway/contracts 68; product code 60; maintenance 16; OS/Airbender small tails | Contracts are the strongest v31/Gateway/security/audit evidence despite low default-branch commit count. |
| `zksync-os` | product code 58; RISC-V/EVM interpreter 29; maintenance 29; Airbender 15; Gateway 8; tooling 6 | Core STF/RISC-V work is real and performance-oriented; many PRs are low-level execution semantics and integration. |
| `zksync-airbender` | Airbender/prover 40; maintenance 22; product code 19; RISC-V 6; Gateway 5 | Proof-system development is active; maturity is developer/prover-stack rather than product adoption by itself. |
| `solx-llvm` | compiler/tooling 48; Gateway/contracts 3; product code 3 | Compiler effort is concentrated and high-commit; one small team is pushing Solidity/Yul/MLIR/EVM semantics. |
| `airbender-platform` | product code 16; Airbender 11; tooling 9; maintenance 8; RISC-V 4 | Platform is turning Airbender from internal prover code into a developer/runtime toolkit. |
| `zksync-js` | Gateway/interop 17; tooling 12; maintenance 4; product code 3 | JS SDK is aligning with v31/Gateway/interop and release cadence. |
| `local-prividium` | maintenance/sync 15; enterprise/SSO 3; product/tooling 2 | Enterprise sandbox exists but many PRs are automated sync/version churn. |
| `zksync-sso` | enterprise/SSO 6; tooling 3; contracts/server 2 | SSO is active around Prividium SDK, ERC-4337, auth server, session/account deployment flows. |

### item-5: 重大功能变更与架构调整

| change | evidence | maturity | impact |
|---|---|---|---|
| ZKsync OS Server as new sequencer/server surface | repo README says it is sequencer implementation for ZKsync OS; PRs [#1322](https://github.com/matter-labs/zksync-os-server/pull/1322), [#1317](https://github.com/matter-labs/zksync-os-server/pull/1317), [#1297](https://github.com/matter-labs/zksync-os-server/pull/1297), [#1308](https://github.com/matter-labs/zksync-os-server/pull/1308), releases v0.19/v0.20 in window | active dev / release train / gateway-launch hardening | Direct engineering watch; this is the top public activity center. |
| ZKsync OS / RISC-V generalized STF | repo README says OS is Rust/RISC-V STF supporting multiple execution environments; PRs [#646](https://github.com/matter-labs/zksync-os/pull/646), [#652](https://github.com/matter-labs/zksync-os/pull/652), [#641](https://github.com/matter-labs/zksync-os/pull/641), [#655](https://github.com/matter-labs/zksync-os/pull/655) | active development / pre-production maturity for some flows | Shows zkVM/STF route beyond EraVM-only; migration risk remains. |
| Airbender prover/verifier pipeline | `zksync-airbender` README says RISC-V proving tools; PRs [#290](https://github.com/matter-labs/zksync-airbender/pull/290), [#288](https://github.com/matter-labs/zksync-airbender/pull/288), [#302](https://github.com/matter-labs/zksync-airbender/pull/302); verifier PRs [#17](https://github.com/matter-labs/eravm-airbender-verifier/pull/17), [#19](https://github.com/matter-labs/eravm-airbender-verifier/pull/19), [#22](https://github.com/matter-labs/eravm-airbender-verifier/pull/22) | active prover stack; some PRs open; not enough to claim full production adoption | ZK/RISC-V prover investment is a meaningful differentiator vs optimistic stacks. |
| v31 / Gateway / contracts security hardening | `era-contracts` PRs [#2200](https://github.com/matter-labs/era-contracts/pull/2200), [#2198](https://github.com/matter-labs/era-contracts/pull/2198), [#2186](https://github.com/matter-labs/era-contracts/pull/2186), [#2192](https://github.com/matter-labs/era-contracts/pull/2192); `zksync-era` [#4807](https://github.com/matter-labs/zksync-era/pull/4807), [#4796](https://github.com/matter-labs/zksync-era/pull/4796) | merged/open mix; audit fixes and protocol ops active | Gateway is code-supported, not only marketing. |
| Governance/security boundary changes | `zk-governance` [#42](https://github.com/zksync-association/zk-governance/pull/42), [#41](https://github.com/zksync-association/zk-governance/pull/41), [#37](https://github.com/zksync-association/zk-governance/pull/37) | governance/supporting repo; PR-level evidence | SecurityCouncil threshold and freezability matter for Stage/security comparison. |
| Compiler/tooling compatibility | `solx-llvm` PRs [#77](https://github.com/matter-labs/solx-llvm/pull/77), [#76](https://github.com/matter-labs/solx-llvm/pull/76), [#73](https://github.com/matter-labs/solx-llvm/pull/73), [#70](https://github.com/matter-labs/solx-llvm/pull/70); `foundry-zksync` [#1282](https://github.com/matter-labs/foundry-zksync/pull/1282), [#1276](https://github.com/matter-labs/foundry-zksync/pull/1276) | active maintenance / compatibility | Necessary to lower migration cost into nonstandard VM/proving stack. |
| Enterprise/Prividium/SSO package | `local-prividium` README and PRs [#26](https://github.com/matter-labs/local-prividium/pull/26), [#30](https://github.com/matter-labs/local-prividium/pull/30), [#36](https://github.com/matter-labs/local-prividium/pull/36); `zksync-sso` README and PRs [#270](https://github.com/matter-labs/zksync-sso/pull/270), [#273](https://github.com/matter-labs/zksync-sso/pull/273), [#274](https://github.com/matter-labs/zksync-sso/pull/274) | local development / enterprise module; not mainnet adoption evidence | Strong commercial packaging signal but production evidence is incomplete. |

### item-6: 开发重点变化与资源配置判断

**What changed versus the old Era-first view**

The old framing "analyze `zksync-era` as the main repo" is now too narrow:

- `zksync-os-server` alone has more PRs than `zksync-era`, `era-contracts`, and `zksync-os` individually, and it ranks first on PR, merged PR, commits, and human PR authors.
- `zksync-era` is still highly active and rises to composite rank 2, but much of its high-signal work is compatibility, API, protocol-upgrade automation, and Airbender/v31 integration.
- `era-contracts` and `zk-governance` show protocol/governance/security work that cannot be inferred from `zksync-era` alone.
- OS/Airbender/tooling repos form a product chain: OS server runs the new stack, OS is the RISC-V STF, Airbender proves it, interfaces/verifiers translate it, JS/Foundry/compiler maintain developer access, and contracts/Gateway settle or interoperate.

**Evidence-grade conclusions**

| conclusion | evidence grade | confidence |
|---|---|---|
| Public engineering center has shifted to OS/server/prover/contracts multi-repo work, with `zksync-os-server` the most active repo. | GitHub ranking + PR body reviewed | high |
| `zksync-era` is not dead; it is still rank 2 by composite score and remains an Era compatibility/API/release/prover integration surface. | branch-aware commits + PR samples | high |
| Gateway/v31 is strongly code-supported in contracts, SDK, OS server, Era, and governance repos. | PR body/files reviewed | high |
| Airbender/RISC-V is a serious technical route, not a docs-only claim. | multiple repos + README + PRs | high |
| Prividium/SSO has real local/dev code, but production customer deployment evidence is not established by these repos alone. | repo README + PRs, source caveat | medium |
| External contributor expansion is limited; most high-signal PRs are Matter Labs/core/automation. | author counts | medium-high |

### item-7: 公开叙事时间线与 GitHub 活动映射

This section uses official docs/blog/repo README where available. If a narrative source is not available in the repository or official docs observed in this pass, it is marked as inferred from code activity.

| narrative tag | public source / official surface | GitHub mapping | maturity label | evidence grade |
|---|---|---|---|---|
| ZKsync OS | `zksync-os` README: new state transition function, multiple execution environments, Rust compiled to RISC-V; `zksync-os-server` README links user docs and describes sequencer implementation | `zksync-os-server` rank 1; `zksync-os` rank 4; `zksync-os-interface` rank 9 | active development / release train | repo primary |
| Airbender | `zksync-airbender` README: RISC-V compilation/proving tools; `airbender-platform` README: Rust toolkit and `cargo airbender` lifecycle | `zksync-airbender`, `airbender-platform`, `eravm-airbender-verifier`, `zksync-airbender-prover` | active proving stack; not treated as full production fact | repo primary |
| Elastic Chain / Gateway / v31 | code evidence in `era-contracts`, `zksync-era`, `zksync-js`, `zk-governance`; official docs search did not expose a single stable current source in this pass | v31, Gateway launch hardening, L1 interop contracts, verification keys, interop SDK functions | merged/open mix; code-supported | PR primary; docs partial |
| Native AA / SSO | `zksync-sso` README: modular smart accounts, passkeys, sessions, paymaster, recovery, auth server; docs link in README | `zksync-sso` PRs around Prividium SDK, ERC-4337, auth server; `local-prividium` includes Keycloak and user/admin panels | active development, not yet feature complete per README | repo primary |
| Prividium / enterprise | `local-prividium` README: local development only, Docker Compose Prividium cluster with Keycloak, protected RPC, block explorer, institutional demo | `local-prividium`, `zksync-sso`, `block-explorer` | local dev / enterprise module | repo primary; adoption caveat |
| Developer tooling | repo READMEs/releases for `zksync-js`, `foundry-zksync`, `solx-llvm` and PRs | interop docs/tests, compiler MLIR/Yul/EVM ops, Foundry upstream merge | active tooling | PR primary |

**Narrative mapping**

The code activity and public repo docs broadly align around a "new stack" story:

```text
ZKsync OS Server
  -> ZKsync OS / RISC-V STF / MultiVM interface
  -> Airbender prover/verifier/platform
  -> era-contracts / Gateway / v31 / governance
  -> JS/Foundry/compiler/tooling
  -> Prividium/SSO enterprise packaging
```

The caveat is maturity: OS/Airbender/Gateway are code-heavy but still mixed active development/open PR/release train; Prividium and SSO are visible but not proven by public code alone as deployed customer production. Therefore the draft distinguishes **engineering direction** from **market adoption**.

### item-8: ZKsync OS + Airbender 技术路线专项分析

**Component boundaries**

| component | repo | role |
|---|---|---|
| Sequencer/server runtime | `zksync-os-server` | Runs local/testnet/mainnet-child/gateway presets, JSON-RPC, L1 watcher, batcher, consensus, replay archive, proof API artifacts |
| State transition function | `zksync-os` | Rust/RISC-V OS that can handle multiple execution environments; includes bootloader, EVM interpreter, runner, basic system |
| Interface layer | `zksync-os-interface` | MultiVM interface, native prover input, FRI precompile errors/types |
| Proving system | `zksync-airbender` | RISC-V circuits, simulator, witness/proof/verification tooling |
| Developer/prover platform | `airbender-platform` | `cargo airbender`, guest/host SDK, proof generation/verification CLI and profiling |
| EraVM Airbender verifier | `eravm-airbender-verifier` | Verifier/prover server, v31 wire-format compatibility, FRI/SNARK VK handling |

**Technical interpretation**

ZKsync is building a vertical zkVM-style stack: execution becomes RISC-V provable (`zksync-os`), server/runtime is separated into `zksync-os-server`, proving is handled by Airbender, and compatibility layers connect to Era/V31/contracts. This is materially different from OP Stack/Arbitrum, where the public engineering narrative is still optimistic/fraud-proof/client stack rather than production ZK proof generation for every transition.

**Mantle impact**

- Direct watch: Airbender verifier memory/proof performance, FRI/SNARK pipeline, OS server RPC/consensus reliability, v31/Gateway settlement changes.
- Optional inspiration: modular prover interfaces, RISC-V guest/host SDK, proof-as-server pattern, native prover input generation.
- Hard-to-copy boundary: migrating an EVM-compatible L2 to a new STF/prover stack is not a feature toggle; it requires compiler, SDK, tooling, contracts, explorer, governance, and ops coordination.

### item-9: Gateway / Elastic Chain / contracts / governance 专项分析

The most concrete Gateway/v31 evidence is in PR files and titles rather than one single repo:

- `era-contracts` [#2200](https://github.com/matter-labs/era-contracts/pull/2200) adds L1 interop contracts including `BridgeRegistry`, `L1InteropHandler`, `L1ShadowAccount`, `L2InteropCenter`, and private interop handlers.
- `era-contracts` [#2198](https://github.com/matter-labs/era-contracts/pull/2198), [#2192](https://github.com/matter-labs/era-contracts/pull/2192), [#2195](https://github.com/matter-labs/era-contracts/pull/2195) change governance/server notifier/admin/AssetRouter/Gateway upgrade paths.
- `era-contracts` [#2186](https://github.com/matter-labs/era-contracts/pull/2186) updates verification keys for protocol v31.0; [#2202](https://github.com/matter-labs/era-contracts/pull/2202) adds a FRI verifier expected by Gateway.
- `zksync-era` [#4807](https://github.com/matter-labs/zksync-era/pull/4807) gates DA commitment decode before v31; [#4796](https://github.com/matter-labs/zksync-era/pull/4796) adds medium interop bootloader.
- `zksync-js` [#77](https://github.com/matter-labs/zksync-js/pull/77), [#85](https://github.com/matter-labs/zksync-js/pull/85), [#92](https://github.com/matter-labs/zksync-js/pull/92), [#95](https://github.com/matter-labs/zksync-js/pull/95) put v31/Gateway/interop into developer APIs and docs/tests.
- `zk-governance` [#42](https://github.com/zksync-association/zk-governance/pull/42), [#41](https://github.com/zksync-association/zk-governance/pull/41), [#37](https://github.com/zksync-association/zk-governance/pull/37) show ProtocolUpgradeHandler, ZKsync OS CTM, SecurityCouncil redeployment, and freezability work.

**Comparison**

| dimension | ZKsync | Optimism/Base | Arbitrum | Mantle implication |
|---|---|---|---|---|
| Multi-chain narrative | Elastic Chain / Gateway / interop contracts | Superchain interop / registry / op-supervisor | Orbit appchains, AnyTrust, BoLD/Timeboost optionality | Mantle needs a clearer appchain/interoperability stance if it wants to compete beyond single L2. |
| Proof/security route | ZK/RISC-V/Airbender + Gateway settlement | optimistic proof, op-reth/kona transition | BoLD/fraud proof + Stylus | ZKsync has stronger ZK narrative; Mantle can counter with pragmatic EVM/DA/governance maturity. |
| Governance/security | ZKsync Association, SecurityCouncil/ProtocolUpgradeHandler/freezability PRs | OP governance/standard config/registry | Arbitrum DAO/security council | Mantle should benchmark freeze/unfreeze, upgrade delay, and exit-window story explicitly. |

### item-10: Developer tooling / SDK / compiler / explorer 专项分析

**Compiler**

`solx-llvm` ranks 6 composite and 2 commit-only. PRs include Solidity/Yul MLIR ops, EVM control-flow fixes, `gasleft`, `blockhash`, `blobhash`, `selfdestruct`, calldata struct lowering, modifier expansion. The small author set means high focus but also key-person concentration risk.

**SDK / JS**

`zksync-js` is explicitly described as "ZKsync OS JavaScript SDK". Recent PRs are heavily interop/Gateway/v31 oriented: `verifyBundle`, `getInteropRoot`, viem interop resource, tx overrides, ERC7786 destination validation, `zks_getProof`, priority transaction gas estimation, interop docs snippets and e2e tests.

**Foundry**

`foundry-zksync` is no longer a high-PR repo but still commit-significant. PR [#1282](https://github.com/matter-labs/foundry-zksync/pull/1282) is an upstream Foundry merge; [#1283](https://github.com/matter-labs/foundry-zksync/pull/1283) pins upstream merge commit and zksolc version; [#1276](https://github.com/matter-labs/foundry-zksync/pull/1276) fixes `--zk-gas-per-pubdata` behavior.

**Explorer / docs**

`block-explorer` and `zksync-docs` are supporting rather than primary, but they matter for migration and ecosystem maturity. `block-explorer` has 22 PR and 20 commits; `zksync-docs` has 16 PR and 10 commits.

**Mantle implications**

- If ZKsync's new stack succeeds, developer migration will depend less on proof system superiority and more on SDK/RPC/Foundry/compiler/explorer parity.
- Mantle should track RPC parity gaps, Foundry fork maintenance cost, and whether ZKsync JS interop APIs start shaping developer expectations for multi-chain UX.

### item-11: Enterprise / Prividium / SSO / private-chain 专项分析

**Local Prividium evidence**

`local-prividium` README is explicit: it is a Docker Compose setup for a complete local Prividium cluster, for local development only. It includes Admin Panel, User Panel, Prividium API with control/permissions/protected RPC, PostgreSQL, Keycloak, zkSync OS, L1 Anvil, Block Explorer, Prometheus, Grafana, and an optional "institutional repo lending demo". This is a strong packaging signal, not production deployment proof.

Recent PRs mostly synchronize versions and harden local setup:

- [#26](https://github.com/matter-labs/local-prividium/pull/26): SSO and example apps framework;
- [#30](https://github.com/matter-labs/local-prividium/pull/30): SSO setup script fix;
- [#32](https://github.com/matter-labs/local-prividium/pull/32): source local SSO env at runtime;
- [#34](https://github.com/matter-labs/local-prividium/pull/34), [#36](https://github.com/matter-labs/local-prividium/pull/36), [#38](https://github.com/matter-labs/local-prividium/pull/38): automated version sync.

**ZKsync SSO evidence**

`zksync-sso` README describes a modular smart account implementation on ZKsync, with ERC-7579 modules, passkeys, sessions, integrated paymaster support, account recovery, JavaScript SDK for smart accounts on zksync-os, auth server, and demo app. It also warns the project is under active development and not feature complete.

Recent PRs tie SSO to Prividium and zksync-os:

- [#265](https://github.com/matter-labs/zksync-sso/pull/265): new Prividium version / auth server API;
- [#270](https://github.com/matter-labs/zksync-sso/pull/270): switch active ERC-4337 path to zksync-os;
- [#273](https://github.com/matter-labs/zksync-sso/pull/273): repair Prividium account deployment registration;
- [#274](https://github.com/matter-labs/zksync-sso/pull/274): bump Prividium SDK;
- [#275](https://github.com/matter-labs/zksync-sso/pull/275): auth API hardening.

**Interpretation**

ZKsync is packaging an enterprise/private deployment story around permissioned access, identity, protected RPC, Keycloak, SSO, admin/user panels, and local demos. The code evidence is enough to say "enterprise module development is real"; it is not enough to say "large regulated customers are in production" without separate official deployment evidence.

### item-12: 横向竞争定位与 Mantle 行动建议

**Competitor positioning**

| dimension | ZKsync | Optimism/Base | Arbitrum | Sui / enterprise stacks | Mantle read |
|---|---|---|---|---|---|
| Core technical narrative | ZKsync OS + Airbender + Gateway | Superchain interop, op-reth/kona, standardization | Nitro/BoLD, Stylus, Timeboost, Orbit | Sui payments/data/app stack; Canton need-to-know privacy | ZKsync has the sharpest ZK/RISC-V proof narrative among L2 competitors. |
| Developer compatibility | EVM/EraVM compatibility plus new compiler/JS/Foundry work | OP Stack compatibility and large ecosystem | EVM + Stylus/WASM | Move/Canton different app model | Mantle should defend with EVM/tooling reliability and lower migration friction. |
| Multi-chain strategy | Elastic Chain/Gateway/Prividium | Superchain/interop/registry/Base | Orbit/custom chains | app stacks/private domains | Mantle needs a more explicit L2/L3/appchain answer. |
| Enterprise | Prividium + SSO + protected RPC/local stack | Base enterprise/payment distribution and OP ecosystem | Orbit/custom deployment | Canton/Tempo stronger enterprise-native privacy | ZKsync is closer to enterprise packaging than pure public L2 peers; Canton/Tempo still more enterprise-native. |
| Security/proof | ZK/RISC-V prover route | optimistic fault proofs/client migration | BoLD fraud proofs | varies | Mantle should articulate DA/security/governance tradeoffs rather than ignore proof narrative. |

**Mantle action matrix**

| horizon | action | rationale |
|---|---|---|
| 1-2 months | Track `zksync-os-server`, `era-contracts`, `zksync-era`, `zksync-airbender`, `eravm-airbender-verifier` weekly PR/release deltas | These are the public early indicators of OS/Gateway/Airbender maturity. |
| 1-2 months | Build a ZKsync v31/Gateway watch note: contract upgrade flow, verifier keys, FRI verifier, governance/security council, SDK APIs | Gateway is the area most likely to affect multi-chain settlement narrative. |
| 1-2 months | Benchmark Mantle's current RPC/SDK/Foundry/explorer parity story against ZKsync JS/Foundry/compiler changes | Developer migration is won or lost in tooling details. |
| 1 quarter | Prototype or at least design-review a zkVM/RISC-V prover strategy memo: partner, buy, or ignore | ZKsync is spending engineering capital here; Mantle should choose deliberately. |
| 1 quarter | Define Mantle's enterprise/private-chain packaging story: protected RPC, permissioning, identity, private DA, admin portal, SSO/paymaster | Prividium/SSO local stack shows how competitors package enterprise demos. |
| 1-2 quarters | Decide whether Mantle wants a multi-chain/interoperability narrative beyond single L2 + EigenDA economics | ZKsync Gateway and OP Superchain will keep pressuring single-chain positioning. |

**What not to copy blindly**

- Do not copy ZKsync OS/Airbender without accepting a multi-year compiler/prover/tooling migration burden.
- Do not copy Gateway/multi-chain settlement unless Mantle has a concrete appchain demand and governance/security model.
- Do not over-index on local Prividium demos as proof of enterprise adoption; evaluate actual customer workflows, compliance needs, and private DA/security assumptions.
- Do not assume ZK proof narrative alone beats OP/EVM compatibility; ZKsync is spending heavily on SDK/Foundry/compiler because compatibility remains a constraint.

## 3. Diagrams

### diag-1: Repo universe and selection funnel

```text
5 orgs scanned
  matter-labs (230 repos, 1408 PR)
  zkSync-Community-Hub (8 repos, 2 PR)
  zksync-sdk (24 repos, 6 PR)
  zksync-association (11 repos, 11 PR)
  zksync (1 repo, 0 PR)
        |
        v
274 public repos
        |
        +-- exclude archived/forks from ranking
        v
185 non-archived, non-fork repos
        |
        +-- score by PR / merged / commits / authors / recency
        v
Top 8 primary: os-server, era, era-contracts, os, airbender, solx-llvm, airbender-platform, zksync-js
Supporting: os-interface, foundry, verifier, prover, local-prividium, sso, governance, docs/explorer
```

### diag-2: ZKsync technical route map

```text
Developer / SDK / compiler
  zksync-js, foundry-zksync, solx-llvm
        |
        v
ZKsync OS Server
  RPC, consensus, L1 watcher, batcher, replay archive, Gateway configs
        |
        v
ZKsync OS / MultiVM STF
  EVM/EraVM/Wasm-ready execution environment, Rust -> RISC-V
        |
        v
Airbender stack
  zksync-airbender -> airbender-platform -> eravm-airbender-verifier/prover
        |
        v
Contracts / Gateway / governance
  era-contracts, v31 keys, FRI verifier, L1 interop, ProtocolUpgradeHandler, SecurityCouncil
```

### diag-3: PR category heat map

| repo | OS server/RPC | Gateway/contracts | OS/STF/RISC-V | Airbender/prover | compiler/tooling | enterprise/SSO | maintenance |
|---|---:|---:|---:|---:|---:|---:|---:|
| `zksync-os-server` | 117 | 105 | 6 | 10 | 19 | 14 | 46 |
| `zksync-era` | 9 | 37 | 0 | 30 | 12 | 0 | 19 |
| `era-contracts` | 2 | 68 | 3 | 3 | 2 | 0 | 16 |
| `zksync-os` | 1 | 8 | 29 | 15 | 6 | 0 | 29 |
| `zksync-airbender` | 0 | 5 | 6 | 40 | 2 | 0 | 22 |
| `solx-llvm` | 0 | 3 | 0 | 0 | 48 | 0 | 2 |
| `airbender-platform` | 1 | 0 | 4 | 11 | 9 | 0 | 8 |
| `zksync-js` | 2 | 17 | 0 | 1 | 12 | 0 | 4 |

### diag-4: Development and narrative timeline

```text
2026-W09..W13
  os-server PR peaks begin; zksync-os / Airbender / solx-llvm active
  zksync-sso new Prividium version and local stack work

2026-W14..W17
  era-contracts v31/Gateway/audit fixes peak
  zksync-js interop/Gateway SDK work
  zksync-os EVM interpreter and Airbender migration work

2026-W18..W21
  os-server v0.20 releases, RPC/rate limiting/L1 watcher/Gateway launch hardening
  era Airbender SNARK/FRI and v31 compatibility
  governance ZKsync OS CTM / SecurityCouncil / freezability work
```

### diag-5: Mantle threat/opportunity matrix

| ZKsync move | Threat to Mantle | Opportunity for Mantle | Caveat |
|---|---|---|---|
| ZKsync OS + Airbender | Strong ZK/RISC-V technical narrative; possible proof-performance moat | Learn modular prover interfaces; sharpen Mantle proof/security roadmap | Migration cost and maturity risk high |
| Gateway / Elastic Chain | Multi-chain settlement/interoperability story pressures single-L2 narrative | Define Mantle L2/L3/appchain and settlement story | Requires real appchain demand |
| Prividium / SSO | Enterprise demos may look more packaged than generic L2 infra | Package Mantle enterprise stack: identity, protected RPC, private DA, admin tools | Public evidence is local/dev heavy |
| JS/Foundry/compiler tooling | Better migration rails reduce ZKsync adoption friction | Mantle can win on EVM compatibility and mature tooling if executed | Need measurable DX, not slogans |
| Governance/security PRs | ZKsync can argue mature upgrade/freezability controls | Mantle can compare Stage/security/exit-window clearly | Must avoid overclaiming either side |

## 4. Source Coverage

| requirement | coverage |
|---|---|
| Org-wide repo scan | full: 5 orgs, 274 repos, raw export saved |
| Exact UTC window PR queries | full: segmented `gh search prs` for 2026-02-23..03-31, 04-01..04-30, 05-01..05-23 |
| GitHub 1000 cap handling | full: single `matter-labs` full-window query returns 1000; segmented queries avoid cap and dedupe URLs |
| Branch-aware commit metrics | partial-to-full: default branch counts via GitHub commit API for active/recent repos; raw values recorded |
| Contributor metrics | full for PR authors, partial for commit authors due default-branch visibility |
| Representative PR bodies/files | full for Top 8 + supporting repos: 101 representative PRs captured |
| Official docs/blog | partial: repo READMEs and linked docs used; some external official blog/docs search results were sparse in this runtime |
| Existing internal competitor sections | partial: Optimism, Arbitrum, enterprise privacy/Canton sections used for comparison framing, with time-sensitive claims not reasserted as fresh facts |
| Durable evidence appendix | full: query manifest, generated timestamp, org/repo totals, Top 20 raw data, normalized score inputs, and durable PR/release/docs links are committed in `round-2-sources.md` |

## 5. Gap Analysis

- **Private/internal work invisibility**: Matter Labs may have private repos or internal roadmap work not visible in GitHub public data.
- **Commit-count caveat**: default-branch commit counts can undercount feature branches, non-default release branches, squash-merge internals, generated sync commits, and workflow-generated changes. `era-contracts` / `zksync-os` PR activity is high despite low default-branch commit count, so PR evidence remains important.
- **Merged metric caveat**: ranking uses PRs created in the window and merged by collection time; merged-at query was run for Top 25, but not every repo in the universe.
- **Classification caveat**: PR category counts are research-derived and directional; Matter Labs labels may differ.
- **Narrative-source caveat**: Some ZKsync official blog/docs pages did not surface cleanly through search in this environment. Repo READMEs, release lists, and PRs are therefore primary for engineering claims; public narrative claims are kept maturity-qualified.
- **Enterprise adoption gap**: Prividium/SSO/local enterprise stack has code evidence, but public production customer evidence was not fully verified in this standard-depth pass.
- **On-chain adoption gap**: No on-chain metrics for Gateway, Prividium, SSO, or Airbender proof usage were collected; this draft is GitHub/public-doc centered.

## 6. Revision Log

- Round 1 initial deep draft created from approved outline commit `90069f3b0553bf596fe7d4dbb3814ae08eb27bc7`.
- Applied outline-review Phase B guardrail: reran exact-window paginated/segmented GitHub PR queries, recomputed branch-aware commit/contributor metrics, recorded raw/normalized scores, explained Top 8 ordering changes, and preserved GitHub Search/default-branch commit caveats.
- Round 2 revision preserves the round-1 analysis and adds committed source appendix `202606-internal-sharing/research-sections/competitor-zksync/drafts/round-2-sources.md`, replacing the previous session-local evidence trail with durable query, ranking, normalization, and source-link records.
