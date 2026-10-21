"""Core evaluation engine for the 30-minute GitHub Copilot Governance, Usage, and Security demo."""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Any

MOST_RESTRICTIVE_ORG_POLICIES = frozenset(
    {
        "Copilot Metrics API",
        "Semantic indexing for non-GitHub repositories",
        "Suggestions matching public code",
        "Allow members without a Copilot license to use Copilot code review in GitHub.com",
    }
)

DEFAULT_FEATURE_POLICY_EXEMPTIONS = frozenset(
    {
        "Store local sessions in the Cloud",
        "Restrict Copilot to data residency models",
        "Restrict Copilot to FedRAMP models",
    }
)

CONTENT_EXCLUSION_UNSUPPORTED_SURFACES = frozenset(
    {
        "Copilot CLI",
        "Copilot CLI local shell",
        "IDE Agent Mode",
        "IDE Agent Mode & Copilot CLI",
    }
)


def load_scenario(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        path = Path(__file__).resolve().parents[1] / "fixtures" / "enterprise-scenario.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_enterprise_feature_default(
    policy_name: str, raw_state: str, default_new_features: str
) -> str:
    if raw_state != "Unconfigured":
        return raw_state
    if policy_name in DEFAULT_FEATURE_POLICY_EXEMPTIONS:
        return "Unconfigured (Exempt from Default policy for new features)"
    return f"{default_new_features} (via Default policy for new features, active 2026-10-22)"


def _resolve_multi_org_policy(policy_name: str, org_states: list[str]) -> str:
    if policy_name == "Suggestions matching public code":
        return "Blocked" if "Blocked" in org_states else "Allowed"
    if policy_name == "Semantic indexing for non-GitHub repositories":
        return "Enabled" if org_states and all(state == "Enabled" for state in org_states) else "Disabled"
    if policy_name in MOST_RESTRICTIVE_ORG_POLICIES:
        return "Disabled" if any(state in ("Disabled", "Unconfigured") for state in org_states) else "Enabled"
    return "Enabled" if "Enabled" in org_states else "Disabled"


def evaluate_governance(scenario: dict[str, Any]) -> dict[str, Any]:
    ent = scenario["enterprise"]
    orgs = scenario["organizations"]
    default_feat = ent["default_policy_for_new_features"]

    resolved_enterprise_policies: dict[str, str] = {}
    for policy_name, raw_state in ent["enterprise_policies"].items():
        resolved_enterprise_policies[policy_name] = _resolve_enterprise_feature_default(
            policy_name, raw_state, default_feat
        )

    persona_results: list[dict[str, Any]] = []
    tracked_policies = [
        "Copilot Metrics API",
        "Suggestions matching public code",
        "Semantic indexing for non-GitHub repositories",
        "Allow members without a Copilot license to use Copilot code review in GitHub.com",
        "Copilot CLI",
        "The GitHub Copilot app",
        "Copilot cloud agent",
    ]
    for persona in scenario["Personas"]:
        effective: dict[str, dict[str, str]] = {}
        for policy_name in tracked_policies:
            ent_state = ent["enterprise_policies"][policy_name]
            if ent_state in ("Enabled everywhere", "Disabled everywhere"):
                val = "Enabled" if ent_state == "Enabled everywhere" else "Disabled"
                rule = "Enterprise lock"
            elif persona["seat_source"] == "enterprise_direct":
                val = ent["policies_for_enterprise_assigned_users"]
                rule = "Policies for enterprise-assigned users (not covered by 'Let organizations decide')"
            else:
                seat_org_states = [
                    orgs[org_name]["policies"].get(policy_name, "Unconfigured")
                    for org_name in persona["seat_orgs"]
                ]
                val = _resolve_multi_org_policy(policy_name, seat_org_states)
                rule = (
                    "Most restrictive organization"
                    if policy_name in MOST_RESTRICTIVE_ORG_POLICIES
                    else "Least restrictive organization"
                )
            if policy_name in persona.get("external_enterprise_restrictive_locks", []):
                val = "Disabled"
                rule = "Most restrictive across multiple enterprises"
            effective[policy_name] = {"effective": val, "resolution_rule": rule}

        persona_results.append(
            {
                "login": persona["login"],
                "role": persona["role"],
                "seat_source": persona["seat_source"],
                "seat_orgs": persona["seat_orgs"],
                "effective_policies": effective,
            }
        )

    model_results: list[dict[str, Any]] = []
    for model in ent["models"]:
        status = model["enterprise_status"]
        if status == "Enabled":
            effective_status = "Enabled everywhere"
        elif status == "Disabled":
            effective_status = "Disabled everywhere"
        elif model["open_weight"]:
            effective_status = "Disabled by default (open-weight model excluded from Default availability policy)"
        elif not model["data_retention_covered"]:
            effective_status = "Disabled by default (not covered by GitHub data retention agreement)"
        elif model["category"] == "preview":
            effective_status = "Disabled by default (pre-GA preview model ignores Default availability policy)"
        elif status == "Delegate to organizations":
            org_outcomes = {
                org_name: (
                    org_data["default_availability_for_released_models"]
                    if org_data["models"].get(model["id"]) == "Delegate to default policy"
                    else org_data["models"].get(model["id"], "Disabled")
                )
                for org_name, org_data in orgs.items()
            }
            effective_status = f"Delegated to organizations: {org_outcomes}"
        else:
            effective_status = status
        model_results.append(
            {
                "id": model["id"],
                "category": model["category"],
                "enterprise_status": status,
                "effective_outcome": effective_status,
            }
        )

    return {
        "priority_order": 1,
        "pillar": "GitHub Copilot Governance & Guardrails",
        "enterprise_slug": ent["slug"],
        "resolved_enterprise_policies": resolved_enterprise_policies,
        "persona_effective_policies": persona_results,
        "model_governance": model_results,
        "surface_policy_checks": scenario["surface_policy_checks"],
    }


def classify_adoption_cohort(qualifying_days: dict[str, int]) -> str:
    agent_surfaces = sum(
        1
        for surface in ("cloud_agent", "code_review", "copilot_cli")
        if qualifying_days.get(surface, 0) >= 2
    )
    if qualifying_days.get("copilot_app", 0) >= 2 or agent_surfaces >= 2:
        return "Phase 3: Multi-agent"
    if agent_surfaces == 1:
        return "Phase 2: Agent first"
    if qualifying_days.get("completions_or_ide_agent_edits", 0) >= 2:
        return "Phase 1: Code first"
    return "No Cohort"


def evaluate_budgets(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    cfg = scenario["usage_and_reporting"]["ai_credit_budgets"]
    defaults = cfg["user_level_defaults"]
    shared = cfg["shared_spending_budgets"]
    results: list[dict[str, Any]] = []

    for case in cfg["budget_test_cases"]:
        login = case["login"]
        cc = case["cost_center"]
        consumed = float(case["user_consumed_usd"])

        if login in defaults["explicit_user_overrides"]:
            user_budget = defaults["explicit_user_overrides"][login]
            selected_tier = "explicit_user"
        elif cc and cc in defaults["multi_user_cost_center"]:
            user_budget = defaults["multi_user_cost_center"][cc]
            selected_tier = f"multi_user_cost_center ({cc})"
        else:
            user_budget = defaults["multi_user_customer"]
            selected_tier = "multi_user_customer (enterprise default)"

        user_headroom = round(float(user_budget["limit_usd"]) - consumed, 2)
        active_hard_controls: list[tuple[str, float]] = [
            (f"user_level:{selected_tier}", user_headroom)
        ]
        alert_only_notes: list[str] = []

        if cc and cc in shared:
            cc_budget = shared[cc]
            cc_headroom = round(float(cc_budget["limit_usd"]) - float(cc_budget["consumed_usd"]), 2)
            if cc_budget["hard_stop"]:
                active_hard_controls.append((f"shared:{cc}", cc_headroom))
            else:
                alert_only_notes.append(
                    f"{cc} is alert-only (${cc_headroom:.2f} remaining of ${cc_budget['limit_usd']:.2f}); does not block."
                )

        ent_budget = shared["enterprise"]
        ent_headroom = round(float(ent_budget["limit_usd"]) - float(ent_budget["consumed_usd"]), 2)
        if ent_budget["hard_stop"]:
            active_hard_controls.append(("shared:enterprise", ent_headroom))

        binding_control, min_headroom = min(active_hard_controls, key=lambda item: item[1])
        results.append(
            {
                "login": login,
                "selected_user_budget_tier": selected_tier,
                "selected_user_limit_usd": float(user_budget["limit_usd"]),
                "user_consumed_usd": consumed,
                "user_remaining_headroom_usd": user_headroom,
                "binding_control": binding_control,
                "effective_remaining_headroom_usd": min_headroom,
                "blocked": min_headroom <= 0,
                "alert_only_notes": alert_only_notes,
            }
        )
    return results


def evaluate_usage_and_reporting(scenario: dict[str, Any]) -> dict[str, Any]:
    usage = scenario["usage_and_reporting"]
    users = usage["users_28d_activity"]

    cohort_counts = {
        "Phase 3: Multi-agent": 0,
        "Phase 2: Agent first": 0,
        "Phase 1: Code first": 0,
        "No Cohort": 0,
    }
    user_cohorts: list[dict[str, Any]] = []
    engaged_prs: list[int] = []
    passive_prs: list[int] = []

    for u in users:
        phase = classify_adoption_cohort(u["qualifying_days_28d"])
        cohort_counts[phase] += 1
        if phase == "No Cohort":
            passive_prs.append(u["prs_merged_28d"])
        else:
            engaged_prs.append(u["prs_merged_28d"])

        cli_c = u["cli_customizations"]
        user_cohorts.append(
            {
                "user_login": u["user_login"],
                "ai_adoption_phase": phase,
                "ai_credits_used": u["ai_credits_used"],
                "prs_merged_28d": u["prs_merged_28d"],
                "cli_skill_interactions_inclusive_of_plugins": cli_c["skill_interactions"],
                "cli_plugin_interactions_subset": cli_c["plugin_interactions"],
                "cli_non_plugin_skill_interactions": (
                    cli_c["skill_interactions"] - cli_c["plugin_interactions"]
                ),
            }
        )

    avg_engaged = sum(engaged_prs) / len(engaged_prs) if engaged_prs else 0.0
    avg_passive = sum(passive_prs) / len(passive_prs) if passive_prs else 1.0
    adoption_multiplier = round(avg_engaged / avg_passive, 2)

    enterprise_dau = sum(1 for u in users if u["server_side_active_today"])
    ide_client_telemetry_dau = sum(
        1 for u in users if u["server_side_active_today"] and u["ide_client_telemetry_enabled"]
    )
    cli_dau = sum(1 for u in users if u["used_cli_today"])

    org_dau_by_membership: dict[str, int] = {}
    for org_name in scenario["organizations"]:
        org_dau_by_membership[org_name] = sum(
            1
            for u in users
            if u["server_side_active_today"] and org_name in u["member_orgs"]
        )

    eligible_teams = {
        slug: count
        for slug, count in usage["teams_seated_counts"].items()
        if count >= 5
    }
    excluded_small_teams = {
        slug: count
        for slug, count in usage["teams_seated_counts"].items()
        if count < 5
    }

    return {
        "priority_order": 2,
        "pillar": "Usage, Reporting & Administration",
        "window_28d": usage["window_28d"],
        "cohort_distribution_28d": cohort_counts,
        "adoption_multiplier_prs_merged": adoption_multiplier,
        "user_cohort_summaries": user_cohorts,
        "reconciliation": {
            "enterprise_daily_active_users": enterprise_dau,
            "ide_feature_breakdown_users": ide_client_telemetry_dau,
            "server_side_only_active_users": enterprise_dau - ide_client_telemetry_dau,
            "daily_active_cli_users_separate": cli_dau,
            "org_dau_by_membership": org_dau_by_membership,
            "sum_of_org_daus": sum(org_dau_by_membership.values()),
            "multi_org_double_count_delta": sum(org_dau_by_membership.values()) - enterprise_dau,
            "user_teams_report_included": eligible_teams,
            "user_teams_report_excluded_under_5_seats": excluded_small_teams,
        },
        "repos_1_day_cca_ccr": usage["repos_1_day"],
        "ai_credit_budget_decisions": evaluate_budgets(scenario),
    }


def _matches_exclusion_pattern(path: str, pattern: str) -> bool:
    norm_path = path.lower().lstrip("/")
    norm_pat = pattern.lower().lstrip("/")
    if norm_pat.endswith("/**"):
        prefix = norm_pat[:-3].rstrip("/")
        if norm_path == prefix or norm_path.startswith(prefix + "/"):
            return True
    return fnmatch.fnmatch(norm_path, norm_pat) or fnmatch.fnmatch(Path(norm_path).name, norm_pat)


def evaluate_security(scenario: dict[str, Any]) -> dict[str, Any]:
    sec = scenario["security_and_compliance"]
    exclusions = sec["content_exclusion"]
    org_rules = exclusions["organization_rules"]
    repo_rules = exclusions["repository_rules"]

    probe_results: list[dict[str, Any]] = []
    for probe in exclusions["access_probes"]:
        repo = probe["repo"]
        path = probe["path"]
        surface = probe["surface"]

        applicable_patterns: list[str] = list(org_rules.get("*", []))
        repo_git_url = f"https://github.com/{repo}.git"
        applicable_patterns.extend(org_rules.get(repo_git_url, []))
        applicable_patterns.extend(repo_rules.get(repo, []))

        matched_pattern = next(
            (pat for pat in applicable_patterns if _matches_exclusion_pattern(path, pat)),
            None,
        )
        surface_supports_exclusion = surface not in CONTENT_EXCLUSION_UNSUPPORTED_SURFACES
        blocked_by_exclusion = bool(matched_pattern) and surface_supports_exclusion

        probe_results.append(
            {
                "repo": repo,
                "path": path,
                "surface": surface,
                "matched_pattern": matched_pattern,
                "surface_supports_content_exclusion": surface_supports_exclusion,
                "blocked_by_exclusion": blocked_by_exclusion,
                "compensating_control": probe.get("compensating_control"),
            }
        )

    agent_audit_events = [
        evt for evt in sec["audit_log_events"] if evt.get("actor_is_agent") is True
    ]
    admin_audit_events = [
        evt for evt in sec["audit_log_events"] if not evt.get("actor_is_agent")
    ]

    request_ids = {
        r["github_request_id"]
        for r in sec["emu_usage_records"]
        if r["type"] == "request"
    }
    response_ids = {
        r["github_request_id"]
        for r in sec["emu_usage_records"]
        if r["type"] == "response"
    }
    paired_session_requests = sorted(request_ids & response_ids)

    pr_decisions: list[dict[str, Any]] = []
    for pr in sec["pr_security_gates"]:
        checks_ok = (
            pr["secret_scanning_push_protection"] == "passed"
            and pr["codeql_analysis"].startswith("passed")
            and pr["dependency_review"] == "passed"
            and pr["copilot_code_review"] == "completed"
            and pr["human_approvals"] >= 1
            and not pr["author_attempted_self_approval"]
        )
        pr_decisions.append(
            {
                "pr_number": pr["pr_number"],
                "author": pr["author"],
                "delegated_by": pr["delegated_by"],
                "merge_eligible": checks_ok,
                "blocking_reason": (
                    None
                    if checks_ok
                    else "Requires passing CodeQL/Secret Scanning and >=1 independent human approval"
                ),
            }
        )

    return {
        "priority_order": 3,
        "pillar": "Security, Compliance & Auditability",
        "content_exclusion_probes": probe_results,
        "auditability_summary": {
            "admin_policy_and_seat_events": len(admin_audit_events),
            "agentic_events_with_session_id": [
                {
                    "action": e["action"],
                    "actor": e["actor"],
                    "user": e["user"],
                    "agent_session_id": e["agent_session_id"],
                }
                for e in agent_audit_events
            ],
            "emu_paired_usage_record_request_ids": paired_session_requests,
        },
        "pr_security_gate_decisions": pr_decisions,
    }


def evaluate_all(scenario: dict[str, Any] | None = None) -> dict[str, Any]:
    data = load_scenario() if scenario is None else scenario
    pillars = [
        evaluate_governance(data),
        evaluate_usage_and_reporting(data),
        evaluate_security(data),
    ]
    return {
        "scenario_id": data["scenario_id"],
        "api_version": data["enterprise"]["api_version"],
        "evaluation_date": data["enterprise"]["evaluation_date"],
        "pillars_in_priority_order": pillars,
    }
