"""CLI entrypoint for running the 30-minute GitHub Copilot Governance, Usage, and Security evaluator."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .evaluator import evaluate_all, load_scenario


def format_markdown_report(result: dict) -> str:
    gov, usage, sec = result["pillars_in_priority_order"]
    rec = usage["reconciliation"]
    lines = [
        f"# GitHub Copilot Enterprise Evaluation Report ({result['scenario_id']})",
        "",
        f"- **REST API Version:** `{result['api_version']}`",
        f"- **Evaluation Date:** `{result['evaluation_date']}`",
        "",
        "## 1. GitHub Copilot Governance & Guardrails (Priority 1)",
        "",
        "| Persona | Seat Source | Metrics API | Public Code | Non-GH Indexing | CLI | Cloud Agent |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for p in gov["persona_effective_policies"]:
        ep = p["effective_policies"]
        lines.append(
            f"| `{p['login']}` | `{p['seat_source']}` | "
            f"{ep['Copilot Metrics API']['effective']} | "
            f"{ep['Suggestions matching public code']['effective']} | "
            f"{ep['Semantic indexing for non-GitHub repositories']['effective']} | "
            f"{ep['Copilot CLI']['effective']} | "
            f"{ep['Copilot cloud agent']['effective']} |"
        )
    lines.extend(
        [
            "",
            "## 2. Usage, Reporting & Administration (Priority 2)",
            "",
            f"- **Enterprise DAU:** `{rec['enterprise_daily_active_users']}` "
            f"(IDE client telemetry DAU: `{rec['ide_feature_breakdown_users']}`, "
            f"server-side-only active users: `{rec['server_side_only_active_users']}`)",
            f"- **Separate Copilot CLI DAU:** `{rec['daily_active_cli_users_separate']}`",
            f"- **Sum of Organization DAUs:** `{rec['sum_of_org_daus']}` "
            f"(multi-org membership delta: `+{rec['multi_org_double_count_delta']}`)",
            f"- **Adoption Multiplier (Engaged Phase 1-3 vs Passive PRs merged):** `{usage['adoption_multiplier_prs_merged']}x`",
            "",
            "| User | Adoption Cohort (28d) | Selected Budget Tier | Binding Control | Remaining Headroom | Blocked |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    cohorts_by_user = {u["user_login"]: u["ai_adoption_phase"] for u in usage["user_cohort_summaries"]}
    for b in usage["ai_credit_budget_decisions"]:
        lines.append(
            f"| `{b['login']}` | {cohorts_by_user.get(b['login'], 'N/A')} | "
            f"`{b['selected_user_budget_tier']}` | `{b['binding_control']}` | "
            f"${b['effective_remaining_headroom_usd']:.2f} | `{b['blocked']}` |"
        )
    lines.extend(
        [
            "",
            "## 3. Security, Compliance & Auditability (Priority 3)",
            "",
            "| Repo | Path | Surface | Supports Exclusion | Blocked by Exclusion |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for probe in sec["content_exclusion_probes"]:
        lines.append(
            f"| `{probe['repo']}` | `{probe['path']}` | {probe['surface']} | "
            f"`{probe['surface_supports_content_exclusion']}` | `{probe['blocked_by_exclusion']}` |"
        )
    return "\n".join(lines) + "\n"


def run_live_readonly(enterprise: str) -> int:
    """Read-only inspection of live GitHub enterprise Copilot billing/metrics metadata via gh api."""
    cmd = [
        "gh",
        "api",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        "X-GitHub-Api-Version: 2026-03-10",
        f"/enterprises/{enterprise}/copilot/metrics/reports/enterprise-28-day/latest",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print(
            json.dumps(
                {
                    "mode": "live_readonly",
                    "enterprise": enterprise,
                    "status": "unavailable_or_forbidden",
                    "detail": proc.stderr.strip(),
                },
                indent=2,
            )
        )
        return 1
    payload = json.loads(proc.stdout)
    redacted = {
        "mode": "live_readonly",
        "enterprise": enterprise,
        "report_start_day": payload.get("report_start_day"),
        "report_end_day": payload.get("report_end_day"),
        "signed_download_links_count": len(payload.get("download_links", [])),
    }
    print(json.dumps(redacted, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate GitHub Copilot Governance, Usage Reporting, and Security in priority order."
    )
    parser.add_argument("--scenario", type=Path, help="Path to scenario JSON fixture")
    parser.add_argument("--out", type=Path, help="Optional output directory for JSON and Markdown reports")
    parser.add_argument(
        "--live-enterprise",
        help="Optional read-only check against /enterprises/{enterprise}/copilot/metrics/reports/enterprise-28-day/latest",
    )
    args = parser.parse_args(argv)

    if args.live_enterprise:
        return run_live_readonly(args.live_enterprise)

    scenario = load_scenario(args.scenario)
    result = evaluate_all(scenario)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "evaluation-report.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        (args.out / "evaluation-report.md").write_text(
            format_markdown_report(result), encoding="utf-8"
        )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
