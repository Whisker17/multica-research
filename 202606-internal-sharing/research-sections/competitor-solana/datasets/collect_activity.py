#!/usr/bin/env python3
"""Collect reproducible Solana-related GitHub activity datasets.

This collector is deliberately conservative:
- REST is used for full org repo listings because the Phase B gate requires
  archived/fork/template flags for every visible public repo.
- GraphQL is used for per-repo metrics to keep the full-universe scan
  recomputable within GitHub API limits.
- Heavier PR row collection is limited to the selected Top repos after ranking.
"""

from __future__ import annotations

import csv
import json
import math
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WINDOW_START = "2026-02-23T00:00:00Z"
WINDOW_END = "2026-05-23T23:59:59Z"
WINDOW_START_DT = datetime.fromisoformat(WINDOW_START.replace("Z", "+00:00"))
WINDOW_END_DT = datetime.fromisoformat(WINDOW_END.replace("Z", "+00:00"))
TIMEZONE = "UTC"
DATASET_VERSION = "2026-05-23.solana-activity.v2"

MANDATORY_ORGS = ["solana-labs", "anza-xyz", "jito-foundation"]
EXTENDED_ORGS = ["solana-foundation", "firedancer-io", "jito-labs"]
TOP_REPO_LIMIT = 12
TOP_PR_LIMIT_PER_REPO = 120
REPRESENTATIVE_FILES_PER_REPO = 8
DATASET_DIR = Path(__file__).resolve().parent

WEIGHTS = {
    "pr_created": 0.20,
    "pr_merged": 0.18,
    "commit_count": 0.16,
    "unique_contributors": 0.12,
    "active_days": 0.08,
    "release_count": 0.08,
    "issue_activity": 0.08,
    "issue_comment_count": 0.04,
    "recent_acceleration": 0.06,
}

NOISE_TITLE_RE = re.compile(
    r"\b(bump|deps?|dependabot|renovate|release|changelog|version|snapshot|"
    r"format|fmt|lint|clippy|typo|readme|doc(?:s|umentation)?|ci|workflow|"
    r"flake|cargo\s+update|lockfile|generated|bindings?)\b",
    re.IGNORECASE,
)
DOCS_TITLE_RE = re.compile(r"\b(readme|docs?|documentation|typo|website|book)\b", re.IGNORECASE)
CI_TITLE_RE = re.compile(r"\b(ci|workflow|action|build|clippy|lint|flake)\b", re.IGNORECASE)
RELEASE_TITLE_RE = re.compile(r"\b(release|changelog|version|tag|publish|v\d+\.\d+)\b", re.IGNORECASE)

REPO_METRICS_QUERY = """
query($owner:String!, $name:String!, $sinceGit:GitTimestamp!, $untilGit:GitTimestamp!, $sinceDate:DateTime!) {
  repository(owner:$owner, name:$name) {
    id
    nameWithOwner
    isArchived
    isFork
    isTemplate
    primaryLanguage { name }
    defaultBranchRef {
      name
      target {
        ... on Commit {
          history(since:$sinceGit, until:$untilGit) { totalCount }
        }
      }
    }
    pullRequests(first:100, orderBy:{field:UPDATED_AT, direction:DESC}) {
      totalCount
      nodes {
        number
        title
        state
        isDraft
        createdAt
        updatedAt
        mergedAt
        closedAt
        changedFiles
        comments { totalCount }
        commits { totalCount }
        author { login __typename }
      }
    }
    issues(first:100, filterBy:{since:$sinceDate}, orderBy:{field:UPDATED_AT, direction:DESC}) {
      totalCount
      nodes {
        createdAt
        updatedAt
        comments { totalCount }
      }
    }
    releases(first:50, orderBy:{field:CREATED_AT, direction:DESC}) {
      totalCount
      nodes {
        tagName
        publishedAt
        createdAt
      }
    }
  }
  rateLimit { cost remaining }
}
"""


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def in_window(value: str | None) -> bool:
    dt = parse_dt(value)
    return bool(dt and WINDOW_START_DT <= dt <= WINDOW_END_DT)


def gh(args: list[str]) -> str:
    proc = subprocess.run(
        ["gh", *args],
        cwd=DATASET_DIR,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed:\nSTDOUT={proc.stdout}\nSTDERR={proc.stderr}")
    return proc.stdout


def gh_json(path: str, params: dict[str, Any] | None = None, paginate: bool = False) -> Any:
    args = ["api", "--method", "GET", path]
    if paginate:
        args.extend(["--paginate", "--slurp"])
    if params:
        for key, value in params.items():
            args.extend(["-f", f"{key}={value}"])
    out = gh(args)
    if not out.strip():
        return []
    data = json.loads(out)
    if paginate and data and all(isinstance(page, list) for page in data):
        rows: list[Any] = []
        for page in data:
            rows.extend(page)
        return rows
    return data


def gh_graphql(query: str, variables: dict[str, str]) -> dict[str, Any]:
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        args.extend(["-f", f"{key}={value}"])
    return json.loads(gh(args))


def rate_limit() -> dict[str, Any]:
    return gh_json("rate_limit")


def is_bot_author(author: dict[str, Any] | None) -> bool:
    if not author:
        return False
    login = (author.get("login") or "").lower()
    typename = (author.get("__typename") or author.get("type") or "").lower()
    return "bot" in typename or "bot" in login or "dependabot" in login or "renovate" in login


def classify_pr(pr: dict[str, Any], files: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    title = pr.get("title") or ""
    body = pr.get("body") or ""
    text = f"{title}\n{body}"
    author = pr.get("author") or pr.get("user")
    file_names = [f.get("filename", "") for f in (files or [])]
    lower_files = [name.lower() for name in file_names]

    docs_only = bool(DOCS_TITLE_RE.search(text))
    ci_only = bool(CI_TITLE_RE.search(text))
    release_automation = bool(RELEASE_TITLE_RE.search(text))
    generated = bool(re.search(r"\b(generated|bindings?|snapshot|lockfile)\b", text, re.IGNORECASE))
    if files:
        docs_only = all(
            name.endswith((".md", ".mdx", ".rst", ".txt"))
            or name.startswith(("docs/", "book/", "website/"))
            for name in lower_files
        )
        ci_only = all(
            name.startswith((".github/", "ci/", ".buildkite/"))
            or "workflow" in name
            or name.endswith((".yml", ".yaml"))
            for name in lower_files
        )
        generated = generated or any(
            "generated" in name or name.endswith((".snap", ".lock")) or "fixtures/" in name
            for name in lower_files
        )

    is_bot = is_bot_author(author)
    title_noise = bool(NOISE_TITLE_RE.search(text))
    noise = is_bot or docs_only or ci_only or release_automation or generated or title_noise

    category = "other"
    rules = [
        ("consensus_alpenglow", r"\b(alpenglow|votor|rotor|vote|consensus|finality|bls)\b"),
        ("client_runtime_svm", r"\b(svm|runtime|bank|replay|accounts?|loader|program|sbpf|vm)\b"),
        ("performance_scheduling", r"\b(perf|performance|scheduler|scheduling|priority fee|compute|latency|throughput|quic|tpu|packet)\b"),
        ("validator_ops_rpc", r"\b(validator|rpc|geyser|snapshot|ledger|cluster|devops|monitor|cli)\b"),
        ("mev_jito", r"\b(jito|mev|bundle|tip|block engine|shred|relayer|restaking|ncn|bam)\b"),
        ("program_token_tooling", r"\b(token|spl|program|anchor|sdk|kit|pinocchio|mollusk|web3|client)\b"),
        ("payments_depin_mobile", r"\b(pay|payment|mobile|depin|rwa|stablecoin|kora|wallet)\b"),
        ("docs_ci_release", r"\b(docs?|ci|release|changelog|workflow|bump|dependabot|renovate)\b"),
    ]
    for candidate, pattern in rules:
        if re.search(pattern, text, re.IGNORECASE):
            category = candidate
            break
    if category == "other" and lower_files:
        joined = "\n".join(lower_files)
        for candidate, pattern in rules:
            if re.search(pattern, joined, re.IGNORECASE):
                category = candidate
                break

    state = (pr.get("state") or "").lower()
    evidence_grade = "open-pr" if state in {"open", "OPEN".lower()} else "closed-unmerged"
    if pr.get("mergedAt") or pr.get("merged_at"):
        evidence_grade = "merged-code"
    if pr.get("isDraft") or pr.get("draft"):
        evidence_grade = "draft-pr"
    if docs_only:
        evidence_grade = "docs-only"
    elif ci_only:
        evidence_grade = "test-only"

    return {
        "is_bot": is_bot,
        "docs_only": docs_only,
        "ci_only": ci_only,
        "release_automation": release_automation,
        "generated_or_snapshot": generated,
        "noise_flag": noise,
        "human_code_activity": not noise,
        "pr_category": category,
        "evidence_grade": evidence_grade,
        "file_sample_count": len(file_names),
        "file_sample": file_names[:12],
    }


def strategic_relevance(repo: dict[str, Any]) -> tuple[int, list[str]]:
    full_name = (repo.get("full_name") or repo.get("nameWithOwner") or "").lower()
    text = f"{repo.get('name','')} {repo.get('description') or ''} {full_name}".lower()
    signals: list[str] = []
    patterns = [
        ("consensus/alpenglow", r"alpenglow|votalizer|consensus|simd"),
        ("core-client/runtime", r"\bagave\b|\bsolana\b|\bsvm\b|runtime|sbpf|sdk"),
        ("firedancer-client", r"firedancer"),
        ("mev/jito", r"jito|mev|bundle|restaking|ncn|tip-router|bam"),
        ("payments/token", r"pay|payment|token|spl|kora|attestation"),
        ("validator/rpc", r"validator|geyser|rpc|tpu|packets"),
    ]
    for label, pattern in patterns:
        if re.search(pattern, text):
            signals.append(label)
    return len(signals), signals


def normalize(rows: list[dict[str, Any]], key: str) -> dict[str, float]:
    values = [max(0.0, float(row.get(key, 0) or 0)) for row in rows]
    max_value = max([math.log1p(v) for v in values] or [0.0])
    if max_value == 0:
        return {row["full_name"]: 0.0 for row in rows}
    return {row["full_name"]: math.log1p(max(0.0, float(row.get(key, 0) or 0))) / max_value for row in rows}


def score_rows(rows: list[dict[str, Any]]) -> None:
    raw_mapping = {
        "pr_created": "pr_created_count",
        "pr_merged": "pr_merged_count",
        "commit_count": "commit_count",
        "unique_contributors": "unique_contributors",
        "active_days": "active_days",
        "release_count": "release_count",
        "issue_activity": "issue_activity_count",
        "issue_comment_count": "issue_comment_count",
        "recent_acceleration": "recent_acceleration",
    }
    human_mapping = {
        "pr_created": "human_code_pr_created_count",
        "pr_merged": "human_code_pr_merged_count",
        "commit_count": "commit_count",
        "unique_contributors": "unique_contributors",
        "active_days": "active_days",
        "release_count": "release_count",
        "issue_activity": "human_issue_activity_count",
        "issue_comment_count": "issue_comment_count",
        "recent_acceleration": "recent_acceleration",
    }
    raw_norm = {label: normalize(rows, key) for label, key in raw_mapping.items()}
    human_norm = {label: normalize(rows, key) for label, key in human_mapping.items()}
    for row in rows:
        full = row["full_name"]
        raw_score = sum(WEIGHTS[label] * raw_norm[label][full] for label in WEIGHTS)
        human_score = sum(WEIGHTS[label] * human_norm[label][full] for label in WEIGHTS)
        if row["is_archived"] or row["is_template"]:
            human_score *= 0.35
        if row["is_fork"]:
            human_score *= 0.65
        row["raw_activity_score"] = round(raw_score, 6)
        row["human_code_activity_score"] = round(human_score, 6)
        strategic_score, signals = strategic_relevance(row)
        row["strategic_relevance_score"] = strategic_score
        row["strategic_signals"] = ";".join(signals)
        row["strategic_low_activity_watchlist"] = bool(human_score < 0.25 and strategic_score >= 1)

    for idx, row in enumerate(sorted(rows, key=lambda r: r["raw_activity_score"], reverse=True), 1):
        row["raw_activity_rank"] = idx
    for idx, row in enumerate(sorted(rows, key=lambda r: r["human_code_activity_score"], reverse=True), 1):
        row["human_code_activity_rank"] = idx
    watch_rank = 0
    for row in sorted(rows, key=lambda r: (r["strategic_low_activity_watchlist"], r["strategic_relevance_score"], r["human_code_activity_score"]), reverse=True):
        if row["strategic_low_activity_watchlist"]:
            watch_rank += 1
            row["strategic_low_activity_rank"] = watch_rank
        else:
            row["strategic_low_activity_rank"] = ""


def safe_repo_call(label: str, path: str, params: dict[str, Any], paginate: bool = True) -> tuple[list[dict[str, Any]], str]:
    try:
        data = gh_json(path, params, paginate=paginate)
        return data if isinstance(data, list) else [], ""
    except Exception as exc:  # noqa: BLE001
        return [], f"{label}: {exc}"


def collect_org_repos(orgs: list[str], scope: str) -> tuple[list[dict[str, Any]], list[str]]:
    repos: list[dict[str, Any]] = []
    failures: list[str] = []
    for org in orgs:
        data, failure = safe_repo_call(
            f"repo list {org}",
            f"/orgs/{org}/repos",
            {"type": "public", "per_page": 100},
            paginate=True,
        )
        if failure:
            failures.append(failure)
            continue
        for repo in data:
            repo["scan_org"] = org
            repo["scan_scope"] = scope
        repos.extend(data)
        print(f"repo universe: {org} -> {len(data)} repos", flush=True)
    return repos, failures


def collect_extended_discovery() -> tuple[list[dict[str, Any]], list[str]]:
    repos, failures = collect_org_repos(EXTENDED_ORGS, "extended-discovery")
    rows: list[dict[str, Any]] = []
    for repo in sorted(repos, key=lambda r: r["full_name"]):
        strategic_score, signals = strategic_relevance(repo)
        rows.append(
            {
                "dataset_version": DATASET_VERSION,
                "fetch_timestamp": FETCH_TIMESTAMP,
                "timezone": TIMEZONE,
                "org": repo.get("scan_org"),
                "full_name": repo.get("full_name"),
                "repo_id": repo.get("id"),
                "html_url": repo.get("html_url"),
                "description": repo.get("description") or "",
                "primary_language": repo.get("language") or "",
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "pushed_at": repo.get("pushed_at"),
                "is_archived": bool(repo.get("archived")),
                "is_fork": bool(repo.get("fork")),
                "is_template": bool(repo.get("is_template")),
                "strategic_relevance_score": strategic_score,
                "strategic_signals": ";".join(signals),
                "inclusion_decision": "context/watchlist only; not included in approved-gate Top repo score",
            }
        )
    return rows, failures


def repo_universe_rows(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for repo in sorted(repos, key=lambda r: r["full_name"]):
        rows.append(
            {
                "dataset_version": DATASET_VERSION,
                "fetch_timestamp": FETCH_TIMESTAMP,
                "timezone": TIMEZONE,
                "scan_org": repo.get("scan_org"),
                "scan_scope": repo.get("scan_scope"),
                "repo_id": repo.get("id"),
                "node_id": repo.get("node_id"),
                "full_name": repo.get("full_name"),
                "html_url": repo.get("html_url"),
                "description": repo.get("description") or "",
                "primary_language": repo.get("language") or "",
                "default_branch": repo.get("default_branch") or "",
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "open_issues": repo.get("open_issues_count", 0),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
                "is_archived": bool(repo.get("archived")),
                "is_fork": bool(repo.get("fork")),
                "is_template": bool(repo.get("is_template")),
                "visibility": repo.get("visibility", "public"),
                "zero_low_activity_note": "computed in repo_activity_metrics and repo_ranking",
            }
        )
    return rows


def collect_metrics(repos: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]], list[str]]:
    rows: list[dict[str, Any]] = []
    pr_samples_by_repo: dict[str, list[dict[str, Any]]] = {}
    failures: list[str] = []
    for idx, repo in enumerate(sorted(repos, key=lambda r: r["full_name"]), 1):
        full_name = repo["full_name"]
        owner, name = full_name.split("/", 1)
        print(f"[{idx}/{len(repos)}] graphql metrics: {full_name}", flush=True)
        try:
            payload = gh_graphql(
                REPO_METRICS_QUERY,
                {
                    "owner": owner,
                    "name": name,
                    "sinceGit": WINDOW_START,
                    "untilGit": WINDOW_END,
                    "sinceDate": WINDOW_START,
                },
            )
            repository = payload.get("data", {}).get("repository") or {}
        except Exception as exc:  # noqa: BLE001
            failures.append(f"graphql metrics {full_name}: {exc}")
            repository = {}

        pr_nodes = (repository.get("pullRequests") or {}).get("nodes") or []
        pr_in_window = [
            pr for pr in pr_nodes if in_window(pr.get("createdAt")) or in_window(pr.get("mergedAt")) or in_window(pr.get("updatedAt"))
        ]
        pr_samples_by_repo[full_name] = pr_in_window
        pr_created = [pr for pr in pr_in_window if in_window(pr.get("createdAt"))]
        pr_merged = [pr for pr in pr_in_window if in_window(pr.get("mergedAt"))]
        classifications = [classify_pr(pr) for pr in pr_created]
        human_created = [pr for pr in pr_created if classify_pr(pr)["human_code_activity"]]
        human_merged = [pr for pr in pr_merged if classify_pr(pr)["human_code_activity"]]

        issues = (repository.get("issues") or {}).get("nodes") or []
        issues_in_window = [issue for issue in issues if in_window(issue.get("createdAt")) or in_window(issue.get("updatedAt"))]
        issue_comment_count = sum((issue.get("comments") or {}).get("totalCount", 0) for issue in issues_in_window)
        releases = (repository.get("releases") or {}).get("nodes") or []
        releases_in_window = [rel for rel in releases if in_window(rel.get("publishedAt") or rel.get("createdAt"))]
        commit_count = (
            (((repository.get("defaultBranchRef") or {}).get("target") or {}).get("history") or {}).get("totalCount", 0)
        )
        contributors = {
            ((pr.get("author") or {}).get("login") or "")
            for pr in pr_in_window
            if (pr.get("author") or {}).get("login")
        }
        active_days = {
            (parse_dt(pr.get("createdAt")) or WINDOW_START_DT).date().isoformat()
            for pr in pr_created
        }
        active_days |= {
            (parse_dt(pr.get("mergedAt")) or WINDOW_START_DT).date().isoformat()
            for pr in pr_merged
        }
        first_half = [
            pr for pr in pr_created if parse_dt(pr.get("createdAt")) and parse_dt(pr.get("createdAt")) < datetime(2026, 4, 9, tzinfo=timezone.utc)
        ]
        second_half = [
            pr for pr in pr_created if parse_dt(pr.get("createdAt")) and parse_dt(pr.get("createdAt")) >= datetime(2026, 4, 9, tzinfo=timezone.utc)
        ]
        strategic_score, strategic_signals = strategic_relevance(repo)
        is_archived = bool(repo.get("archived") or repository.get("isArchived"))
        is_fork = bool(repo.get("fork") or repository.get("isFork"))
        is_template = bool(repo.get("is_template") or repository.get("isTemplate"))
        row = {
            "dataset_version": DATASET_VERSION,
            "fetch_timestamp": FETCH_TIMESTAMP,
            "timezone": TIMEZONE,
            "window_start": WINDOW_START,
            "window_end": WINDOW_END,
            "scan_org": repo.get("scan_org"),
            "scan_scope": repo.get("scan_scope"),
            "repo_id": repo.get("id"),
            "node_id": repo.get("node_id"),
            "full_name": full_name,
            "html_url": repo.get("html_url"),
            "description": repo.get("description") or "",
            "primary_language": repo.get("language") or "",
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "default_branch": repo.get("default_branch") or "",
            "created_at": repo.get("created_at"),
            "updated_at": repo.get("updated_at"),
            "pushed_at": repo.get("pushed_at"),
            "is_archived": is_archived,
            "is_fork": is_fork,
            "is_template": is_template,
            "visibility": repo.get("visibility", "public"),
            "pr_total_count_graphql": (repository.get("pullRequests") or {}).get("totalCount", 0),
            "pr_sample_count": len(pr_nodes),
            "pr_created_count": len(pr_created),
            "pr_merged_count": len(pr_merged),
            "pr_open_count": sum(1 for pr in pr_in_window if pr.get("state") == "OPEN"),
            "pr_closed_unmerged_count": sum(1 for pr in pr_in_window if pr.get("state") == "CLOSED" and not pr.get("mergedAt")),
            "draft_pr_count": sum(1 for pr in pr_in_window if pr.get("isDraft")),
            "human_code_pr_created_count": len(human_created),
            "human_code_pr_merged_count": len(human_merged),
            "bot_pr_count": sum(1 for c in classifications if c["is_bot"]),
            "noisy_pr_count": sum(1 for c in classifications if c["noise_flag"]),
            "commit_count": commit_count,
            "unique_contributors": len(contributors),
            "active_days": len(active_days),
            "release_count": len(releases_in_window),
            "issue_activity_count": len(issues_in_window),
            "human_issue_activity_count": len(issues_in_window),
            "issue_comment_count": issue_comment_count,
            "recent_acceleration": len(second_half) - len(first_half),
            "zero_activity_flag": not (pr_created or pr_merged or commit_count or releases_in_window or issues_in_window),
            "low_activity_flag": (len(pr_created) + commit_count + len(issues_in_window)) <= 3,
            "strategic_relevance_score": strategic_score,
            "strategic_signals": ";".join(strategic_signals),
            "exclusion_reason": "",
            "ranking_stage_noise_treatment": "bots/docs/CI/release/changelog/generated PRs flagged; human-code score uses human_code_pr_* counts and archived/fork/template penalties",
            "metric_collection_note": "GraphQL pullRequests first 100 by UPDATED_AT desc; commit_count is default-branch history totalCount for fixed window.",
        }
        if is_archived:
            row["exclusion_reason"] = "archived; kept in universe and raw ranking, penalized in human-code ranking"
        elif is_template:
            row["exclusion_reason"] = "template; kept in universe and raw ranking, penalized in human-code ranking"
        elif is_fork:
            row["exclusion_reason"] = "fork; kept in universe and raw ranking, penalized unless current activity is material"
        rows.append(row)

    score_rows(rows)
    for row in rows:
        selected = row["human_code_activity_rank"] <= TOP_REPO_LIMIT
        row["selected_for_top_pr_analysis"] = selected
        if selected:
            row["selection_rationale"] = f"Top {TOP_REPO_LIMIT} by human-code activity score after noise/fork/archive penalties"
        elif row["strategic_low_activity_watchlist"]:
            row["selection_rationale"] = "Not in Top activity set, but retained as strategic-low-activity watchlist"
        else:
            row["selection_rationale"] = "Not selected; lower human-code activity score in evidence window"
    return rows, pr_samples_by_repo, failures


def collect_recent_pulls(owner: str, repo: str, limit: int) -> tuple[list[dict[str, Any]], str]:
    rows: list[dict[str, Any]] = []
    page = 1
    try:
        while len(rows) < limit:
            data = gh_json(
                f"/repos/{owner}/{repo}/pulls",
                {"state": "all", "sort": "updated", "direction": "desc", "per_page": 100, "page": page},
                paginate=False,
            )
            if not data:
                break
            for pr in data:
                if in_window(pr.get("created_at")) or in_window(pr.get("merged_at")) or in_window(pr.get("updated_at")):
                    rows.append(pr)
                if len(rows) >= limit:
                    break
            min_updated = min([parse_dt(pr.get("updated_at")) for pr in data if pr.get("updated_at")] or [None])
            if min_updated and min_updated < WINDOW_START_DT:
                break
            page += 1
    except Exception as exc:  # noqa: BLE001
        return rows, f"pull list {owner}/{repo}: {exc}"
    return rows, ""


def collect_top_pr_rows(metrics_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    result: list[dict[str, Any]] = []
    top_rows = sorted([row for row in metrics_rows if row["selected_for_top_pr_analysis"]], key=lambda r: r["human_code_activity_rank"])
    for metric in top_rows:
        full_name = metric["full_name"]
        owner, repo = full_name.split("/", 1)
        print(f"top PR dataset: {full_name}", flush=True)
        pulls, failure = collect_recent_pulls(owner, repo, TOP_PR_LIMIT_PER_REPO)
        if failure:
            failures.append(failure)
        ranked = sorted(
            pulls,
            key=lambda pr: (
                classify_pr(pr)["human_code_activity"],
                bool(pr.get("merged_at")),
                pr.get("comments", 0) + pr.get("review_comments", 0) + pr.get("commits", 0),
                pr.get("updated_at") or "",
            ),
            reverse=True,
        )
        file_cache: dict[int, list[dict[str, Any]]] = {}
        for pr in ranked[:REPRESENTATIVE_FILES_PER_REPO]:
            try:
                file_cache[pr["number"]] = gh_json(
                    f"/repos/{owner}/{repo}/pulls/{pr['number']}/files",
                    {"per_page": 100},
                    paginate=True,
                )
            except Exception as exc:  # noqa: BLE001
                failures.append(f"pull files {full_name}#{pr['number']}: {exc}")
                file_cache[pr["number"]] = []
        classed = [(pr, classify_pr(pr, file_cache.get(pr["number"]))) for pr in pulls]
        category_seen: Counter[str] = Counter()
        for pr, cls in ranked_classed(classed):
            representative = cls["human_code_activity"] and category_seen[cls["pr_category"]] < 6
            if representative:
                category_seen[cls["pr_category"]] += 1
            result.append(
                {
                    "dataset_version": DATASET_VERSION,
                    "fetch_timestamp": FETCH_TIMESTAMP,
                    "timezone": TIMEZONE,
                    "window_start": WINDOW_START,
                    "window_end": WINDOW_END,
                    "repo_full_name": full_name,
                    "repo_id": metric["repo_id"],
                    "repo_human_code_activity_rank": metric["human_code_activity_rank"],
                    "repo_human_code_activity_score": metric["human_code_activity_score"],
                    "pr_number": pr.get("number"),
                    "pr_url": pr.get("html_url"),
                    "api_url": pr.get("url"),
                    "title": pr.get("title") or "",
                    "state": pr.get("state"),
                    "draft": bool(pr.get("draft")),
                    "created_at": pr.get("created_at"),
                    "updated_at": pr.get("updated_at"),
                    "closed_at": pr.get("closed_at"),
                    "merged_at": pr.get("merged_at"),
                    "author_login": (pr.get("user") or {}).get("login") or "",
                    "author_type": (pr.get("user") or {}).get("type") or "",
                    "comments": pr.get("comments", 0),
                    "review_comments": pr.get("review_comments", 0),
                    "commits": pr.get("commits", 0),
                    "additions": pr.get("additions", ""),
                    "deletions": pr.get("deletions", ""),
                    "changed_files": pr.get("changed_files", ""),
                    "is_bot": cls["is_bot"],
                    "docs_only": cls["docs_only"],
                    "ci_only": cls["ci_only"],
                    "release_automation": cls["release_automation"],
                    "generated_or_snapshot": cls["generated_or_snapshot"],
                    "noise_flag": cls["noise_flag"],
                    "human_code_activity": cls["human_code_activity"],
                    "pr_category": cls["pr_category"],
                    "evidence_grade": cls["evidence_grade"],
                    "representative_pr": representative,
                    "file_sample_count": cls["file_sample_count"],
                    "file_sample": ";".join(cls["file_sample"]),
                    "classification_basis": "title/body/user for all rows; changed-files sample for top representative candidates",
                }
            )
    return result, failures


def ranked_classed(classed: list[tuple[dict[str, Any], dict[str, Any]]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return sorted(
        classed,
        key=lambda pair: (
            pair[1]["human_code_activity"],
            bool(pair[0].get("merged_at")),
            pair[0].get("comments", 0) + pair[0].get("review_comments", 0) + pair[0].get("commits", 0),
            pair[0].get("updated_at") or "",
        ),
        reverse=True,
    )


def query_metadata() -> list[dict[str, Any]]:
    return [
        {
            "query_id": "repo-universe",
            "method": "GET",
            "endpoint": "/orgs/{org}/repos",
            "params": {"type": "public", "per_page": 100},
            "gh_cli_equivalent": "gh api --method GET /orgs/{org}/repos -f type=public -f per_page=100 --paginate",
            "pagination": "gh --paginate until Link rel=last exhausted",
            "notes": "Collects all visible public repos for each mandatory org, including archived/fork/template flags.",
        },
        {
            "query_id": "repo-metrics-graphql",
            "method": "POST",
            "endpoint": "GraphQL repository(owner,name)",
            "params": {"sinceGit": WINDOW_START, "untilGit": WINDOW_END, "sinceDate": WINDOW_START},
            "gh_cli_equivalent": "gh api graphql -f query=<REPO_METRICS_QUERY> -f owner=<owner> -f name=<repo> -f sinceGit=... -f untilGit=... -f sinceDate=...",
            "pagination": "One GraphQL call per repo; PR/issue/release nodes capped but totalCount/default-branch commit history persisted.",
            "notes": "Used for full-universe metrics. pullRequests first 100 by UPDATED_AT desc are used for created/merged/noise/contributor sample; default-branch commit history totalCount covers the full evidence window.",
        },
        {
            "query_id": "top-repo-prs",
            "method": "GET",
            "endpoint": "/repos/{owner}/{repo}/pulls",
            "params": {"state": "all", "sort": "updated", "direction": "desc", "per_page": 100},
            "gh_cli_equivalent": "gh api --method GET /repos/{owner}/{repo}/pulls -f state=all -f sort=updated -f direction=desc -f per_page=100 -f page=N",
            "pagination": f"Manual page=N until {TOP_PR_LIMIT_PER_REPO} in-window rows or updated_at < window_start.",
            "notes": "Creates row-level PR dataset for Top repos only.",
        },
        {
            "query_id": "top-pr-files-sampled",
            "method": "GET",
            "endpoint": "/repos/{owner}/{repo}/pulls/{number}/files",
            "params": {"per_page": 100},
            "gh_cli_equivalent": "gh api --method GET /repos/{owner}/{repo}/pulls/{number}/files -f per_page=100 --paginate",
            "pagination": f"Sampled for top {REPRESENTATIVE_FILES_PER_REPO} representative candidates per selected repo.",
            "notes": "Changed files improve PR categorization; ranking does not depend on this auxiliary sample.",
        },
    ]


def metadata(dataset_name: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    base = {
        "dataset_name": dataset_name,
        "dataset_version": DATASET_VERSION,
        "fetch_timestamp": FETCH_TIMESTAMP,
        "timezone": TIMEZONE,
        "window_start": WINDOW_START,
        "window_end": WINDOW_END,
        "mandatory_orgs": MANDATORY_ORGS,
        "extended_orgs": EXTENDED_ORGS,
        "queries": query_metadata(),
        "rate_limit_before": RATE_LIMIT_BEFORE,
        "rate_limit_after": RATE_LIMIT_AFTER,
        "pagination_notes": "Repo universe uses REST pagination. Full-universe metrics use one GraphQL call per repo. Top PR rows use REST page=N until row cap or window boundary.",
        "rate_limit_notes": "GitHub REST and GraphQL rate-limit snapshots are persisted.",
        "archived_fork_template_flags": "Every repo row persists archived/fork/template flags. Archived/templates/forks remain in universe and raw ranking; human-code score applies penalties.",
        "exclusions_applied": "No visible public repo from the mandatory orgs was removed from repo_universe. Top PR analysis selects Top 12 by human-code score; non-selected repos remain in ranking/watchlist datasets.",
        "zero_low_activity_handling": "zero_activity_flag and low_activity_flag are persisted for every repo; low-activity strategic repos are surfaced in the watchlist view.",
        "duplicate_fork_rename_handling": "Repository identity uses GitHub repo id plus full_name. Fork/template/archive status is explicit. Renames are not merged unless GitHub preserves the same repo id; active forks are not combined with upstream counts.",
        "scoring": {
            "weights": WEIGHTS,
            "normalization": "log1p(metric) divided by max log1p(metric) across the mandatory universe for each metric; raw and human-code views are separate.",
            "de_noising": "PRs from bot users and PRs classified as docs-only, CI-only, release/changelog automation, generated/snapshot, dependency bumps, formatting, or lockfile-only noise are flagged. Human-code view uses human_code_pr_* counts and penalties for archived/template/fork repos.",
            "sensitivity_views": [
                "raw_activity_rank/raw_activity_score",
                "human_code_activity_rank/human_code_activity_score",
                "strategic_low_activity_watchlist/strategic_low_activity_rank",
            ],
        },
    }
    if extra:
        base.update(extra)
    return base


def write_json(path: Path, rows: list[dict[str, Any]], meta: dict[str, Any]) -> None:
    path.write_text(json.dumps({"metadata": meta, "rows": rows}, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], meta: dict[str, Any]) -> None:
    keys = sorted({key for row in rows for key in row.keys()})
    for key in ["dataset_version", "fetch_timestamp", "timezone", "window_start", "window_end"]:
        if key not in keys:
            keys.insert(0, key)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    global FETCH_TIMESTAMP, RATE_LIMIT_BEFORE, RATE_LIMIT_AFTER
    FETCH_TIMESTAMP = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    RATE_LIMIT_BEFORE = rate_limit()
    repos, universe_failures = collect_org_repos(MANDATORY_ORGS, "mandatory")
    extended_rows, extended_failures = collect_extended_discovery()
    universe = repo_universe_rows(repos)
    metrics_rows, _pr_samples, metric_failures = collect_metrics(repos)
    top_pr_rows, top_pr_failures = collect_top_pr_rows(metrics_rows)
    RATE_LIMIT_AFTER = rate_limit()

    all_failures = universe_failures + extended_failures + metric_failures + top_pr_failures
    selected = [
        row["full_name"]
        for row in sorted(metrics_rows, key=lambda r: r["human_code_activity_rank"])
        if row["selected_for_top_pr_analysis"]
    ]

    universe_meta = metadata(
        "repo_universe",
        {
            "scan_failures": universe_failures,
            "scope_note": "Full ranking universe is limited to approved-gate mandatory orgs: solana-labs, anza-xyz, jito-foundation.",
            "extended_discovery_path": "202606-internal-sharing/research-sections/competitor-solana/datasets/extended_org_discovery.{csv,json}",
        },
    )
    metrics_meta = metadata("repo_activity_metrics", {"scan_failures": universe_failures + metric_failures})
    ranking_meta = metadata(
        "repo_ranking",
        {
            "scan_failures": all_failures,
            "top_repo_limit": TOP_REPO_LIMIT,
            "selected_top_repos": selected,
        },
    )
    pr_meta = metadata(
        "top_repo_prs",
        {
            "scan_failures": top_pr_failures,
            "top_repo_limit": TOP_REPO_LIMIT,
            "top_pr_limit_per_repo": TOP_PR_LIMIT_PER_REPO,
        },
    )
    extended_meta = metadata(
        "extended_org_discovery",
        {
            "scan_failures": extended_failures,
            "scope_note": "Related-org discovery only; these repos are not included in the mandatory Top-repo score unless a future revision expands the gate.",
        },
    )

    write_json(DATASET_DIR / "repo_universe.json", universe, universe_meta)
    write_csv(DATASET_DIR / "repo_universe.csv", universe, universe_meta)
    write_json(DATASET_DIR / "extended_org_discovery.json", extended_rows, extended_meta)
    write_csv(DATASET_DIR / "extended_org_discovery.csv", extended_rows, extended_meta)
    write_json(DATASET_DIR / "repo_activity_metrics.json", metrics_rows, metrics_meta)
    write_csv(DATASET_DIR / "repo_activity_metrics.csv", metrics_rows, metrics_meta)
    ranked = sorted(metrics_rows, key=lambda r: r["human_code_activity_rank"])
    write_json(DATASET_DIR / "repo_ranking.json", ranked, ranking_meta)
    write_csv(DATASET_DIR / "repo_ranking.csv", ranked, ranking_meta)
    write_json(DATASET_DIR / "top_repo_prs.json", top_pr_rows, pr_meta)
    write_csv(DATASET_DIR / "top_repo_prs.csv", top_pr_rows, pr_meta)

    print(
        json.dumps(
            {
                "fetch_timestamp": FETCH_TIMESTAMP,
                "repo_count": len(universe),
                "extended_discovery_count": len(extended_rows),
                "metrics_rows": len(metrics_rows),
                "top_pr_rows": len(top_pr_rows),
                "selected_top_repos": selected,
                "failure_count": len(all_failures),
                "failures": all_failures[:20],
                "dataset_dir": str(DATASET_DIR),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
