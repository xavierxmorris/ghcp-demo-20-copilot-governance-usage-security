"""Unit tests for the 30-minute GitHub Copilot Governance, Usage, and Security evaluator."""

from __future__ import annotations

import unittest

from copilot_governance.evaluator import (
    classify_adoption_cohort,
    evaluate_all,
    evaluate_budgets,
    evaluate_governance,
    evaluate_security,
    evaluate_usage_and_reporting,
    load_scenario,
)


class GovernanceUsageSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = load_scenario()
        cls.full = evaluate_all(cls.scenario)

    def test_strict_priority_ordering_across_pillars(self) -> None:
        pillars = self.full["pillars_in_priority_order"]
        self.assertEqual(
            [p["priority_order"] for p in pillars],
            [1, 2, 3],
        )
        self.assertEqual(
            [p["pillar"] for p in pillars],
            [
                "GitHub Copilot Governance & Guardrails",
                "Usage, Reporting & Administration",
                "Security, Compliance & Auditability",
            ],
        )

    def test_multi_org_policy_conflict_least_vs_most_restrictive(self) -> None:
        gov = evaluate_governance(self.scenario)
        personas = {p["login"]: p["effective_policies"] for p in gov["persona_effective_policies"]}

        maya = personas["maya_dual_org"]
        # Sensitive policies use Most Restrictive across retail-digital and regulated-payments
        self.assertEqual(maya["Copilot Metrics API"]["effective"], "Disabled")
        self.assertEqual(maya["Suggestions matching public code"]["effective"], "Blocked")
        self.assertEqual(
            maya["Semantic indexing for non-GitHub repositories"]["effective"],
            "Disabled",
        )
        self.assertEqual(
            maya["Allow members without a Copilot license to use Copilot code review in GitHub.com"]["effective"],
            "Disabled",
        )
        # Productivity/surface policies use Least Restrictive across organizations
        self.assertEqual(maya["Copilot CLI"]["effective"], "Enabled")
        self.assertEqual(maya["The GitHub Copilot app"]["effective"], "Enabled")
        self.assertEqual(maya["Copilot cloud agent"]["effective"], "Enabled")

    def test_direct_enterprise_seat_and_multi_enterprise_locks(self) -> None:
        gov = evaluate_governance(self.scenario)
        personas = {p["login"]: p["effective_policies"] for p in gov["persona_effective_policies"]}

        # Direct enterprise seat is not covered by 'Let organizations decide'; uses enterprise fallback
        chloe = personas["chloe_enterprise_direct"]
        self.assertEqual(chloe["Copilot CLI"]["effective"], "Disabled")
        self.assertIn("enterprise-assigned", chloe["Copilot CLI"]["resolution_rule"])

        # Multi-enterprise seat applies Most Restrictive across enterprises
        noah = personas["noah_contractor_multi_ent"]
        self.assertEqual(noah["Copilot CLI"]["effective"], "Disabled")
        self.assertEqual(noah["Copilot cloud agent"]["effective"], "Disabled")
        self.assertEqual(noah["The GitHub Copilot app"]["effective"], "Enabled")

    def test_october_22_2026_default_feature_and_model_exclusions(self) -> None:
        gov = evaluate_governance(self.scenario)
        ent_pols = gov["resolved_enterprise_policies"]
        self.assertIn("Enabled everywhere", ent_pols["Copilot code review"])
        self.assertIn("Enabled everywhere", ent_pols["MCP servers in Copilot"])
        self.assertIn("Exempt", ent_pols["Store local sessions in the Cloud"])
        self.assertIn("Exempt", ent_pols["Restrict Copilot to data residency models"])

        models = {m["id"]: m["effective_outcome"] for m in gov["model_governance"]}
        self.assertIn("open-weight", models["deepseek-r1"])
        self.assertIn("data retention", models["claude-fable-5.1"])
        self.assertIn("pre-GA preview", models["gemini-next-preview"])

    def test_adoption_cohorts_and_reconciliation_metrics(self) -> None:
        usage = evaluate_usage_and_reporting(self.scenario)
        cohorts = {u["user_login"]: u["ai_adoption_phase"] for u in usage["user_cohort_summaries"]}
        self.assertEqual(cohorts["maya_dual_org"], "Phase 3: Multi-agent")
        self.assertEqual(cohorts["priya_cli_specialist"], "Phase 3: Multi-agent")
        self.assertEqual(cohorts["liam_payments_only"], "Phase 2: Agent first")
        self.assertEqual(cohorts["chloe_enterprise_direct"], "Phase 1: Code first")
        # Chat-only days without code completion or agent edits stay in No Cohort (Passive)
        self.assertEqual(cohorts["noah_contractor_multi_ent"], "No Cohort")
        self.assertEqual(cohorts["ethan_idle_seat"], "No Cohort")

        rec = usage["reconciliation"]
        self.assertEqual(rec["enterprise_daily_active_users"], 3)
        self.assertEqual(rec["ide_feature_breakdown_users"], 2)
        self.assertEqual(rec["server_side_only_active_users"], 1)
        self.assertEqual(rec["daily_active_cli_users_separate"], 2)
        self.assertEqual(rec["sum_of_org_daus"], 5)
        self.assertEqual(rec["multi_org_double_count_delta"], 2)
        self.assertIn("ent:small-tiger-team", rec["user_teams_report_excluded_under_5_seats"])

    def test_two_rule_ai_credit_budget_precedence(self) -> None:
        decisions = {b["login"]: b for b in evaluate_budgets(self.scenario)}
        # maya has explicit $80 user budget ($34 left), alert-only cost center ($15 left), and hard enterprise ($40 left)
        self.assertEqual(decisions["maya_dual_org"]["selected_user_budget_tier"], "explicit_user")
        self.assertEqual(decisions["maya_dual_org"]["effective_remaining_headroom_usd"], 34.0)
        self.assertFalse(decisions["maya_dual_org"]["blocked"])

        # liam has $15 per-user cost-center budget ($1 left), hard shared cost-center budget ($2 left)
        self.assertEqual(decisions["liam_payments_only"]["effective_remaining_headroom_usd"], 1.0)
        self.assertFalse(decisions["liam_payments_only"]["blocked"])

        # chloe hits the $10 multi_user_customer enterprise default
        self.assertTrue(decisions["chloe_enterprise_direct"]["blocked"])
        self.assertEqual(decisions["chloe_enterprise_direct"]["effective_remaining_headroom_usd"], 0.0)

    def test_content_exclusion_surface_boundaries_and_security_gates(self) -> None:
        sec = evaluate_security(self.scenario)
        probes = sec["content_exclusion_probes"]
        # HSM file blocked in IDE Completions and Cloud Agent, but NOT supported in Copilot CLI local shell
        self.assertTrue(probes[0]["blocked_by_exclusion"])
        self.assertTrue(probes[1]["blocked_by_exclusion"])
        self.assertFalse(probes[2]["surface_supports_content_exclusion"])
        self.assertFalse(probes[2]["blocked_by_exclusion"])
        self.assertIsNotNone(probes[2]["compensating_control"])

        # Audit log & EMU usage records pairing
        summary = sec["auditability_summary"]
        self.assertEqual(len(summary["agentic_events_with_session_id"]), 1)
        self.assertEqual(
            summary["agentic_events_with_session_id"][0]["agent_session_id"],
            "012345a6-b7c8-9012-de3f-45gh678i9012",
        )
        self.assertEqual(
            summary["emu_paired_usage_record_request_ids"],
            ["ABCD:1234:567890:FEDCBA:67150001"],
        )

        # PR security gates: PR 108 passes with human approval; PR 109 blocked by CodeQL & missing human review
        prs = {p["pr_number"]: p for p in sec["pr_security_gate_decisions"]}
        self.assertTrue(prs[108]["merge_eligible"])
        self.assertFalse(prs[109]["merge_eligible"])

    def test_classify_adoption_cohort_direct_cases(self) -> None:
        self.assertEqual(
            classify_adoption_cohort({"completions_or_ide_agent_edits": 1}),
            "No Cohort",
        )
        self.assertEqual(
            classify_adoption_cohort({"completions_or_ide_agent_edits": 2}),
            "Phase 1: Code first",
        )
        self.assertEqual(
            classify_adoption_cohort({"cloud_agent": 2}),
            "Phase 2: Agent first",
        )
        self.assertEqual(
            classify_adoption_cohort({"copilot_app": 2}),
            "Phase 3: Multi-agent",
        )


if __name__ == "__main__":
    unittest.main()
