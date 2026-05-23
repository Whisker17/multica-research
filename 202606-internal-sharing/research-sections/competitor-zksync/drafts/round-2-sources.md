---
topic: "zkSync 近期开发与叙事分析"
project_slug: "202606-internal-sharing"
topic_slug: "competitor-zksync"
github_repo: "Whisker17/multica-research"
round: 2
status: source-appendix
parent_draft: "202606-internal-sharing/research-sections/competitor-zksync/drafts/round-2.md"
generated_at_utc: "2026-05-23T21:54:05Z"
source_query_timestamp_utc: "2026-05-23T21:29:17Z"
query_window_utc: "2026-02-23T00:00:00Z..2026-05-23T23:59:59Z"
---

# Source and Evidence Appendix - zkSync 近期开发与叙事分析

This appendix is the durable evidence trail for `round-2.md`. It preserves the round-1 analysis and commits the data needed to audit the org scan, query shape, ranking inputs, and representative source links without relying on ephemeral session exports.

## 1. Query Manifest

### 1.1 Repo Universe Scan

Scanned orgs:

- `matter-labs`
- `zkSync-Community-Hub`
- `zksync-sdk`
- `zksync-association`
- `zksync`

Command template:

```shell
gh repo list {org} --limit 1000 \
  --json name,nameWithOwner,url,description,isArchived,isFork,isPrivate,primaryLanguage,stargazerCount,forkCount,createdAt,updatedAt,pushedAt,defaultBranchRef,latestRelease
```

Field names captured:

- `name`
- `nameWithOwner`
- `url`
- `description`
- `isArchived`
- `isFork`
- `isPrivate`
- `primaryLanguage.name`
- `stargazerCount`
- `forkCount`
- `createdAt`
- `updatedAt`
- `pushedAt`
- `defaultBranchRef.name`
- `latestRelease.name`
- `latestRelease.tagName`
- `latestRelease.url`
- `latestRelease.publishedAt`

Pagination parameters:

- `--limit 1000` per org.
- All five orgs were below that limit; no repo-list continuation was needed.

### 1.2 PR-Created Queries

Purpose: count all PRs created inside the UTC window and capture PR-level metadata.

Command template:

```shell
gh search prs --owner {org} \
  --created {chunk_start}..{chunk_end} \
  --limit 1000 \
  --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url
```

Date chunks:

- `2026-02-23..2026-03-31`
- `2026-04-01..2026-04-30`
- `2026-05-01..2026-05-23`

Expanded GitHub Search query matrix:

| owner | created window | command shape |
|---|---|---|
| `matter-labs` | `2026-02-23..2026-03-31` | `gh search prs --owner matter-labs --created 2026-02-23..2026-03-31 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `matter-labs` | `2026-04-01..2026-04-30` | `gh search prs --owner matter-labs --created 2026-04-01..2026-04-30 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `matter-labs` | `2026-05-01..2026-05-23` | `gh search prs --owner matter-labs --created 2026-05-01..2026-05-23 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zkSync-Community-Hub` | `2026-02-23..2026-03-31` | `gh search prs --owner zkSync-Community-Hub --created 2026-02-23..2026-03-31 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zkSync-Community-Hub` | `2026-04-01..2026-04-30` | `gh search prs --owner zkSync-Community-Hub --created 2026-04-01..2026-04-30 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zkSync-Community-Hub` | `2026-05-01..2026-05-23` | `gh search prs --owner zkSync-Community-Hub --created 2026-05-01..2026-05-23 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-sdk` | `2026-02-23..2026-03-31` | `gh search prs --owner zksync-sdk --created 2026-02-23..2026-03-31 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-sdk` | `2026-04-01..2026-04-30` | `gh search prs --owner zksync-sdk --created 2026-04-01..2026-04-30 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-sdk` | `2026-05-01..2026-05-23` | `gh search prs --owner zksync-sdk --created 2026-05-01..2026-05-23 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-association` | `2026-02-23..2026-03-31` | `gh search prs --owner zksync-association --created 2026-02-23..2026-03-31 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-association` | `2026-04-01..2026-04-30` | `gh search prs --owner zksync-association --created 2026-04-01..2026-04-30 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-association` | `2026-05-01..2026-05-23` | `gh search prs --owner zksync-association --created 2026-05-01..2026-05-23 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync` | `2026-02-23..2026-03-31` | `gh search prs --owner zksync --created 2026-02-23..2026-03-31 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync` | `2026-04-01..2026-04-30` | `gh search prs --owner zksync --created 2026-04-01..2026-04-30 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync` | `2026-05-01..2026-05-23` | `gh search prs --owner zksync --created 2026-05-01..2026-05-23 --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |

Pagination / cap handling:

- Each `{org,chunk}` query used `--limit 1000`.
- The single full-window `matter-labs` query hit GitHub Search's 1000-result cap, so the final count uses segmented queries.
- Raw segment outputs were de-duplicated by `url`.
- `collection_log.json` recorded `created_total_raw=1427`, `created_total_dedup=1427`, and `search_errors=[]`.

Field names captured:

- `author.id`
- `author.is_bot`
- `author.login`
- `author.type`
- `author.url`
- `closedAt`
- `createdAt`
- `isDraft`
- `labels`
- `number`
- `repository.name`
- `repository.nameWithOwner`
- `state`
- `title`
- `updatedAt`
- `url`

### 1.3 PR-Merged Queries

Two merged views were captured:

1. Ranking merged count: PRs created in the window and merged by collection time.
2. Supporting merged-at count: PRs merged during the window for Top 25 repos.

Ranking command template:

```shell
gh search prs --owner {org} \
  --created {chunk_start}..{chunk_end} \
  --merged \
  --limit 1000 \
  --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url
```

Supporting merged-at command template:

```shell
gh search prs --repo {owner}/{repo} \
  --merged-at 2026-02-23..2026-05-23 \
  --limit 1000 \
  --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url
```

Date chunks for created-window merged queries:

- `2026-02-23..2026-03-31`
- `2026-04-01..2026-04-30`
- `2026-05-01..2026-05-23`

Expanded GitHub Search query matrix:

| owner | created window | command shape |
|---|---|---|
| `matter-labs` | `2026-02-23..2026-03-31` | `gh search prs --owner matter-labs --created 2026-02-23..2026-03-31 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `matter-labs` | `2026-04-01..2026-04-30` | `gh search prs --owner matter-labs --created 2026-04-01..2026-04-30 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `matter-labs` | `2026-05-01..2026-05-23` | `gh search prs --owner matter-labs --created 2026-05-01..2026-05-23 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zkSync-Community-Hub` | `2026-02-23..2026-03-31` | `gh search prs --owner zkSync-Community-Hub --created 2026-02-23..2026-03-31 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zkSync-Community-Hub` | `2026-04-01..2026-04-30` | `gh search prs --owner zkSync-Community-Hub --created 2026-04-01..2026-04-30 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zkSync-Community-Hub` | `2026-05-01..2026-05-23` | `gh search prs --owner zkSync-Community-Hub --created 2026-05-01..2026-05-23 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-sdk` | `2026-02-23..2026-03-31` | `gh search prs --owner zksync-sdk --created 2026-02-23..2026-03-31 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-sdk` | `2026-04-01..2026-04-30` | `gh search prs --owner zksync-sdk --created 2026-04-01..2026-04-30 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-sdk` | `2026-05-01..2026-05-23` | `gh search prs --owner zksync-sdk --created 2026-05-01..2026-05-23 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-association` | `2026-02-23..2026-03-31` | `gh search prs --owner zksync-association --created 2026-02-23..2026-03-31 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-association` | `2026-04-01..2026-04-30` | `gh search prs --owner zksync-association --created 2026-04-01..2026-04-30 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync-association` | `2026-05-01..2026-05-23` | `gh search prs --owner zksync-association --created 2026-05-01..2026-05-23 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync` | `2026-02-23..2026-03-31` | `gh search prs --owner zksync --created 2026-02-23..2026-03-31 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync` | `2026-04-01..2026-04-30` | `gh search prs --owner zksync --created 2026-04-01..2026-04-30 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |
| `zksync` | `2026-05-01..2026-05-23` | `gh search prs --owner zksync --created 2026-05-01..2026-05-23 --merged --limit 1000 --json author,closedAt,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url` |

Pagination / cap handling:

- Each query used `--limit 1000`.
- Outputs were de-duplicated by `url`.
- `collection_log.json` recorded `merged_created_total_raw=911`, `merged_created_total_dedup=911`, and `search_errors=[]`.

Field names captured: same as PR-created queries.

### 1.4 Commit Queries

Purpose: branch-aware default-branch public commit count for active/recent repos.

Command templates:

```shell
gh api repos/{owner}/{repo}/commits \
  -f sha={default_branch} \
  -f since=2026-02-23T00:00:00Z \
  -f until=2026-05-23T23:59:59Z \
  -f per_page=1 \
  --include

gh api --paginate repos/{owner}/{repo}/commits \
  -f sha={default_branch} \
  -f since=2026-02-23T00:00:00Z \
  -f until=2026-05-23T23:59:59Z \
  -f per_page=100
```

Field names captured:

- `repo`
- `default_branch`
- `commit_count`
- `active_commit_authors`
- `commit_authors_sample`
- `active_commit_weeks`
- `commit_weeks`

Pagination parameters:

- `per_page=100` with `gh api --paginate`.
- The `per_page=1 --include` query was used to read response headers for total-page estimation where useful.

Known limitation:

- Counts are default-branch public commits only and can undercount feature-branch, non-default release branch, squash-merge, generated-sync, private, or workflow-generated work.

### 1.5 Contributor Queries

Contributor activity is derived from the captured PR and commit records rather than a separate GitHub Search endpoint.

PR contributor derivation:

- Input: de-duplicated PR-created data.
- Field: `author.login`, with `author.is_bot` retained.
- Metric used in ranking: `active_human_pr_authors`.
- Bot/noise handling: `author.is_bot=true` excluded from the human-author count; bot PR count retained separately as `bot_prs`.

Commit contributor derivation:

- Input: paginated default-branch commit API results.
- Fields: commit author identity/login where available.
- Metrics captured: `active_commit_authors`, `commit_authors_sample`, `active_commit_weeks`.

## 2. Generated Timestamp

- Org/repo scan and query execution timestamp used in the draft: `2026-05-23T21:29:17Z`.
- This committed source appendix was generated from the captured exports at: `2026-05-23T21:54:05Z`.

## 3. Org/Repo Universe Totals

| org | total public repos | non-archived non-fork repos | archived | fork | created PR | merged PR created-window |
|---|---:|---:|---:|---:|---:|---:|
| `matter-labs` | 230 | 151 | 48 | 44 | 1408 | 900 |
| `zkSync-Community-Hub` | 8 | 7 | 1 | 0 | 2 | 0 |
| `zksync-sdk` | 24 | 15 | 5 | 4 | 6 | 5 |
| `zksync-association` | 11 | 11 | 0 | 0 | 11 | 6 |
| `zksync` | 1 | 1 | 0 | 0 | 0 | 0 |
| **Total** | **274** | **185** | **54** | **48** | **1427** | **911** |

## 4. Top 20 Raw Ranking Data

Raw fields below are pre-normalization ranking inputs from `repo_metrics_ranked.json`.

| rank | repo | PR count | merged PR count | default-branch commit count | active human PR authors | recency signal | score |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `matter-labs/zksync-os-server` | 404 | 238 | 227 | 34 | 1.0 | 100.0 |
| 2 | `matter-labs/zksync-era` | 130 | 88 | 60 | 27 | 1.0 | 42.7 |
| 3 | `matter-labs/era-contracts` | 154 | 95 | 4 | 23 | 0.5 | 36.32 |
| 4 | `matter-labs/zksync-os` | 146 | 72 | 2 | 12 | 1.0 | 30.68 |
| 5 | `matter-labs/zksync-airbender` | 94 | 73 | 2 | 17 | 0.5 | 25.99 |
| 6 | `matter-labs/solx-llvm` | 56 | 52 | 92 | 4 | 0.5 | 22.68 |
| 7 | `matter-labs/airbender-platform` | 49 | 38 | 42 | 8 | 0.5 | 17.97 |
| 8 | `matter-labs/zksync-js` | 39 | 30 | 30 | 6 | 0.85 | 16.07 |
| 9 | `matter-labs/zksync-os-interface` | 21 | 20 | 22 | 7 | 1.0 | 13.95 |
| 10 | `matter-labs/foundry-zksync` | 25 | 12 | 61 | 3 | 0.65 | 13.37 |
| 11 | `matter-labs/block-explorer` | 22 | 21 | 20 | 5 | 1.0 | 13.08 |
| 12 | `matter-labs/eravm-airbender-verifier` | 32 | 21 | 19 | 7 | 0.5 | 12.24 |
| 13 | `matter-labs/watchdog` | 19 | 14 | 15 | 6 | 1.0 | 12.09 |
| 14 | `matter-labs/zksync-airbender-prover` | 17 | 10 | 10 | 8 | 1.0 | 11.93 |
| 15 | `matter-labs/zksync-docs` | 16 | 10 | 10 | 6 | 1.0 | 10.96 |
| 16 | `matter-labs/zkos-wrapper` | 12 | 10 | 7 | 5 | 1.0 | 9.91 |
| 17 | `matter-labs/local-prividium` | 20 | 15 | 16 | 5 | 0.5 | 9.42 |
| 18 | `matter-labs/zksync-protocol` | 11 | 4 | 4 | 6 | 1.0 | 9.37 |
| 19 | `matter-labs/ethereum-prover` | 15 | 11 | 11 | 3 | 0.85 | 9.0 |
| 20 | `matter-labs/era-watchdog` | 8 | 6 | 6 | 4 | 1.0 | 8.62 |

## 5. Normalized-Score Inputs

### 5.1 Weight Parameters

Composite score formula:

```text
score = 100 * (
  0.35 * norm(PR created)
  + 0.25 * norm(PR merged among created-window PRs)
  + 0.20 * norm(default-branch commits)
  + 0.15 * norm(active human PR authors)
  + 0.05 * release/push recency
)
```

Normalization:

- `norm(PR created)`: raw `pr_created` divided by max among non-archived non-fork repos.
- `norm(PR merged)`: raw `pr_merged_created` divided by max among non-archived non-fork repos.
- `norm(default-branch commits)`: raw `commit_count` divided by max among non-archived non-fork repos.
- `norm(active human PR authors)`: raw `active_human_pr_authors` divided by max among non-archived non-fork repos.
- `release/push recency`: captured recency signal, capped at `1.0`.

### 5.2 Top 8 and Rank-Change/Sensitivity Repos

This table includes the Top 8 plus supporting repos whose treatment changed or needed sensitivity explanation relative to the outline pre-scan.

| rank | repo | PRn | Mn | Cn | An | recency | score | reason included |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `matter-labs/zksync-os-server` | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 100.0 | Top 8 |
| 2 | `matter-labs/zksync-era` | 0.3217821782178218 | 0.3697478991596639 | 0.2643171806167401 | 0.7941176470588235 | 1.0 | 42.7 | Top 8; moved from outline pre-scan rank 4 to composite rank 2 |
| 3 | `matter-labs/era-contracts` | 0.3811881188118812 | 0.39915966386554624 | 0.01762114537444934 | 0.6764705882352942 | 0.5 | 36.32 | Top 8; moved from outline pre-scan rank 2 to composite rank 3 |
| 4 | `matter-labs/zksync-os` | 0.3613861386138614 | 0.3025210084033613 | 0.00881057268722467 | 0.35294117647058826 | 1.0 | 30.68 | Top 8; moved from outline pre-scan rank 3 to composite rank 4 |
| 5 | `matter-labs/zksync-airbender` | 0.23267326732673269 | 0.3067226890756303 | 0.00881057268722467 | 0.5 | 0.5 | 25.99 | Top 8 |
| 6 | `matter-labs/solx-llvm` | 0.13861386138613863 | 0.2184873949579832 | 0.4052863436123348 | 0.11764705882352941 | 0.5 | 22.68 | Top 8 |
| 7 | `matter-labs/airbender-platform` | 0.12128712871287128 | 0.15966386554621848 | 0.18502202643171806 | 0.23529411764705882 | 0.5 | 17.97 | Top 8 |
| 8 | `matter-labs/zksync-js` | 0.09653465346534654 | 0.12605042016806722 | 0.13215859030837004 | 0.17647058823529413 | 0.85 | 16.07 | Top 8 |
| 9 | `matter-labs/zksync-os-interface` | 0.05198019801980198 | 0.08403361344537816 | 0.09691629955947137 | 0.20588235294117646 | 1.0 | 13.95 | outline supporting; Top 12 / OS-interface sensitivity |
| 10 | `matter-labs/foundry-zksync` | 0.06188118811881188 | 0.05042016806722689 | 0.2687224669603524 | 0.08823529411764706 | 0.65 | 13.37 | outline supporting; commit-only rank 3 but composite rank 10 |
| 17 | `matter-labs/local-prividium` | 0.04950495049504951 | 0.06302521008403361 | 0.07048458149779736 | 0.14705882352941177 | 0.5 | 9.42 | outline supporting; enterprise evidence kept despite lower composite rank |

## 6. Durable Primary-Source Links

### 6.1 Representative PR Links

| repo | representative PR URLs |
|---|---|
| `matter-labs/zksync-os-server` | [#1322](https://github.com/matter-labs/zksync-os-server/pull/1322), [#1317](https://github.com/matter-labs/zksync-os-server/pull/1317), [#1315](https://github.com/matter-labs/zksync-os-server/pull/1315), [#1310](https://github.com/matter-labs/zksync-os-server/pull/1310), [#1297](https://github.com/matter-labs/zksync-os-server/pull/1297), [#1241](https://github.com/matter-labs/zksync-os-server/pull/1241), [#1319](https://github.com/matter-labs/zksync-os-server/pull/1319), [#1308](https://github.com/matter-labs/zksync-os-server/pull/1308) |
| `matter-labs/zksync-era` | [#4817](https://github.com/matter-labs/zksync-era/pull/4817), [#4816](https://github.com/matter-labs/zksync-era/pull/4816), [#4813](https://github.com/matter-labs/zksync-era/pull/4813), [#4811](https://github.com/matter-labs/zksync-era/pull/4811), [#4809](https://github.com/matter-labs/zksync-era/pull/4809), [#4807](https://github.com/matter-labs/zksync-era/pull/4807), [#4801](https://github.com/matter-labs/zksync-era/pull/4801), [#4796](https://github.com/matter-labs/zksync-era/pull/4796) |
| `matter-labs/era-contracts` | [#2202](https://github.com/matter-labs/era-contracts/pull/2202), [#2200](https://github.com/matter-labs/era-contracts/pull/2200), [#2198](https://github.com/matter-labs/era-contracts/pull/2198), [#2188](https://github.com/matter-labs/era-contracts/pull/2188), [#2186](https://github.com/matter-labs/era-contracts/pull/2186), [#2192](https://github.com/matter-labs/era-contracts/pull/2192), [#2181](https://github.com/matter-labs/era-contracts/pull/2181), [#2195](https://github.com/matter-labs/era-contracts/pull/2195) |
| `matter-labs/zksync-os` | [#663](https://github.com/matter-labs/zksync-os/pull/663), [#660](https://github.com/matter-labs/zksync-os/pull/660), [#655](https://github.com/matter-labs/zksync-os/pull/655), [#652](https://github.com/matter-labs/zksync-os/pull/652), [#646](https://github.com/matter-labs/zksync-os/pull/646), [#641](https://github.com/matter-labs/zksync-os/pull/641), [#634](https://github.com/matter-labs/zksync-os/pull/634), [#673](https://github.com/matter-labs/zksync-os/pull/673) |
| `matter-labs/zksync-airbender` | [#305](https://github.com/matter-labs/zksync-airbender/pull/305), [#302](https://github.com/matter-labs/zksync-airbender/pull/302), [#300](https://github.com/matter-labs/zksync-airbender/pull/300), [#291](https://github.com/matter-labs/zksync-airbender/pull/291), [#290](https://github.com/matter-labs/zksync-airbender/pull/290), [#288](https://github.com/matter-labs/zksync-airbender/pull/288), [#280](https://github.com/matter-labs/zksync-airbender/pull/280), [#277](https://github.com/matter-labs/zksync-airbender/pull/277) |
| `matter-labs/solx-llvm` | [#77](https://github.com/matter-labs/solx-llvm/pull/77), [#76](https://github.com/matter-labs/solx-llvm/pull/76), [#75](https://github.com/matter-labs/solx-llvm/pull/75), [#73](https://github.com/matter-labs/solx-llvm/pull/73), [#70](https://github.com/matter-labs/solx-llvm/pull/70), [#35](https://github.com/matter-labs/solx-llvm/pull/35), [#30](https://github.com/matter-labs/solx-llvm/pull/30), [#20](https://github.com/matter-labs/solx-llvm/pull/20) |
| `matter-labs/airbender-platform` | [#66](https://github.com/matter-labs/airbender-platform/pull/66), [#64](https://github.com/matter-labs/airbender-platform/pull/64), [#60](https://github.com/matter-labs/airbender-platform/pull/60), [#58](https://github.com/matter-labs/airbender-platform/pull/58), [#52](https://github.com/matter-labs/airbender-platform/pull/52), [#47](https://github.com/matter-labs/airbender-platform/pull/47), [#34](https://github.com/matter-labs/airbender-platform/pull/34), [#32](https://github.com/matter-labs/airbender-platform/pull/32) |
| `matter-labs/zksync-js` | [#106](https://github.com/matter-labs/zksync-js/pull/106), [#95](https://github.com/matter-labs/zksync-js/pull/95), [#92](https://github.com/matter-labs/zksync-js/pull/92), [#85](https://github.com/matter-labs/zksync-js/pull/85), [#82](https://github.com/matter-labs/zksync-js/pull/82), [#77](https://github.com/matter-labs/zksync-js/pull/77), [#80](https://github.com/matter-labs/zksync-js/pull/80), [#94](https://github.com/matter-labs/zksync-js/pull/94) |
| `matter-labs/zksync-os-interface` | [#73](https://github.com/matter-labs/zksync-os-interface/pull/73), [#72](https://github.com/matter-labs/zksync-os-interface/pull/72), [#71](https://github.com/matter-labs/zksync-os-interface/pull/71), [#70](https://github.com/matter-labs/zksync-os-interface/pull/70), [#68](https://github.com/matter-labs/zksync-os-interface/pull/68), [#66](https://github.com/matter-labs/zksync-os-interface/pull/66), [#56](https://github.com/matter-labs/zksync-os-interface/pull/56) |
| `matter-labs/foundry-zksync` | [#1283](https://github.com/matter-labs/foundry-zksync/pull/1283), [#1282](https://github.com/matter-labs/foundry-zksync/pull/1282), [#1276](https://github.com/matter-labs/foundry-zksync/pull/1276), [#1264](https://github.com/matter-labs/foundry-zksync/pull/1264), [#1259](https://github.com/matter-labs/foundry-zksync/pull/1259) |
| `matter-labs/local-prividium` | [#38](https://github.com/matter-labs/local-prividium/pull/38), [#36](https://github.com/matter-labs/local-prividium/pull/36), [#34](https://github.com/matter-labs/local-prividium/pull/34), [#32](https://github.com/matter-labs/local-prividium/pull/32), [#30](https://github.com/matter-labs/local-prividium/pull/30), [#26](https://github.com/matter-labs/local-prividium/pull/26) |
| `matter-labs/zksync-sso` | [#275](https://github.com/matter-labs/zksync-sso/pull/275), [#274](https://github.com/matter-labs/zksync-sso/pull/274), [#273](https://github.com/matter-labs/zksync-sso/pull/273), [#270](https://github.com/matter-labs/zksync-sso/pull/270), [#265](https://github.com/matter-labs/zksync-sso/pull/265), [#267](https://github.com/matter-labs/zksync-sso/pull/267) |
| `zksync-association/zk-governance` | [#43](https://github.com/zksync-association/zk-governance/pull/43), [#42](https://github.com/zksync-association/zk-governance/pull/42), [#41](https://github.com/zksync-association/zk-governance/pull/41), [#37](https://github.com/zksync-association/zk-governance/pull/37), [#36](https://github.com/zksync-association/zk-governance/pull/36) |

### 6.2 Release Links

| repo | release / tag link | use in draft |
|---|---|---|
| `matter-labs/zksync-os-server` | [v0.20.3](https://github.com/matter-labs/zksync-os-server/releases/tag/v0.20.3), [v0.20.2](https://github.com/matter-labs/zksync-os-server/releases/tag/v0.20.2), [v0.20.1](https://github.com/matter-labs/zksync-os-server/releases/tag/v0.20.1), [v0.20.0](https://github.com/matter-labs/zksync-os-server/releases/tag/v0.20.0), [v0.19.3](https://github.com/matter-labs/zksync-os-server/releases/tag/v0.19.3), [v0.19.2](https://github.com/matter-labs/zksync-os-server/releases/tag/v0.19.2), [v0.19.1](https://github.com/matter-labs/zksync-os-server/releases/tag/v0.19.1), [v0.19.0](https://github.com/matter-labs/zksync-os-server/releases/tag/v0.19.0) | release-train / OS server maturity signal |
| `matter-labs/zksync-era` | [core-v29.17.0](https://github.com/matter-labs/zksync-era/releases/tag/core-v29.17.0) | Era release / compatibility signal |
| `matter-labs/zksync-js` | [v0.0.18](https://github.com/matter-labs/zksync-js/releases/tag/v0.0.18) | JS SDK release / tooling signal |
| `matter-labs/foundry-zksync` | [foundry-zksync-v0.1.9](https://github.com/matter-labs/foundry-zksync/releases/tag/foundry-zksync-v0.1.9) | Foundry tooling release signal |
| `matter-labs/zksync-os` | [dev-20260224-base-token-holder](https://github.com/matter-labs/zksync-os/releases/tag/dev-20260224-base-token-holder) | OS dev release signal |

### 6.3 Docs and README Links

| claim / source surface | durable URL |
|---|---|
| ZKsync OS official docs / Developer Preview source | https://docs.zksync.io/zksync-network/zksync-os |
| Airbender official component docs | https://docs.zksync.io/zk-stack/components/zksync-airbender |
| Prividium commercial licensing / module context | https://docs.zksync.io/zk-stack/license |
| `zksync-os-server` repository / README source | https://github.com/matter-labs/zksync-os-server |
| `zksync-os` repository / README source | https://github.com/matter-labs/zksync-os |
| `zksync-airbender` repository / README source | https://github.com/matter-labs/zksync-airbender |
| `airbender-platform` repository / README source | https://github.com/matter-labs/airbender-platform |
| `zksync-js` repository / README source | https://github.com/matter-labs/zksync-js |
| `local-prividium` repository / local enterprise stack README source | https://github.com/matter-labs/local-prividium |
| `zksync-sso` repository / README source | https://github.com/matter-labs/zksync-sso |
| `era-contracts` repository / contracts source | https://github.com/matter-labs/era-contracts |
| `zk-governance` repository / governance source | https://github.com/zksync-association/zk-governance |

## 7. Raw Export Lineage

The following local export names were used to construct this appendix and the round-2 draft. They are listed for lineage only; the audit-critical values and links above are committed in this file.

- `repos.json`
- `prs_created_20260223_20260523.json`
- `prs_merged_created_20260223_20260523.json`
- `prs_merged_at_top25_20260223_20260523.json`
- `commit_metrics.json`
- `repo_metrics_ranked.json`
- `repo_pr_classification.json`
- `representative_prs.json`
- `collection_log.json`
