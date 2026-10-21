# Workshop: Governing, Measuring & Securing GitHub Copilot at Enterprise Scale (60 Minutes)

## Learning Objectives

By the end of this 60-minute hands-on lab, participants will be able to:
1. **Priority 1 — Governance & Guardrails (20 min):** Predict and verify effective Copilot policies across multi-organization users, direct enterprise seats, multi-enterprise contractors, the 22 October 2026 `Default policy for new features` cutover, and model delegation rules.
2. **Priority 2 — Usage, Reporting & Administration (20 min):** Classify users into trailing 28-day AI Adoption Cohorts (`No Cohort`, `Phase 1–3`), reconcile Enterprise vs. Organization DAU and server-side vs. IDE telemetry, and evaluate Two-Rule AI Credit budgets.
3. **Priority 3 — Security, Compliance & Auditability (20 min):** Prove where Content Exclusion applies (and why Copilot CLI and IDE Agent Mode require repository RBAC and Push Protection), correlate `actor:Copilot` `agent_session_id` audit events with EMU `usage-records`, and enforce PR ruleset gates.

---

## Lab Setup (2 Minutes)

```powershell
.\go.ps1 -Check
python -m copilot_governance --out out\baseline
```

Open `docs\demo-console.html` in your browser and `out\baseline\evaluation-report.md` in your editor.

---

## Exercise 1 (20 Min) — Fix a Multi-Org Governance Leak & Direct-Seat Misconfiguration

1. **Predict:** Look at `maya_dual_org` in `fixtures/enterprise-scenario.json`. She is a member of both `retail-digital` and `regulated-payments`. Because `Copilot cloud agent` is set to `Let organizations decide` at the enterprise level, `retail-digital` (`Enabled`) overrides `regulated-payments` (`Disabled`) under the **Least restrictive** rule.
2. **Challenge:** What happens if the enterprise administrator changes `Policies for enterprise-assigned users` from `Disabled` to `Enabled` for `chloe_enterprise_direct`, while locking `Copilot cloud agent` to `Disabled everywhere` at the enterprise root?
3. **Verify:** Run `python -m unittest discover -s tests -v` to confirm all 7 governance and security invariants pass.

---

## Exercise 2 (20 Min) — Reconcile Telemetry Discrepancies & Unblock a Standard User Budget

1. **Observe:** Inspect `out\baseline\evaluation-report.md`:
   - Enterprise DAU is `3`, IDE feature breakdown count is `2`, CLI DAU is `2`, and the sum of organization DAUs is `5`.
   - `noah_contractor_multi_ent` has `11` chat-only days and `1` completion day, placing him in `No Cohort` (Passive).
2. **Challenge:** How many additional days of `Copilot cloud agent` or `Copilot CLI` activity does `noah_contractor_multi_ent` need in the 28-day window to move directly from `No Cohort` to `Phase 2: Agent first`? *(Answer: 2 qualifying days on a single GitHub-based agent surface—even without additional IDE completion days!)*
3. **Budget Precedence Check:** Inspect `chloe_enterprise_direct` (`blocked: true` at `$10.00` `multi_user_customer` limit while the shared enterprise budget still has `$40.00` headroom). Explain using the Two-Rule model why raising the shared enterprise budget from `$500` to `$1,000` will **not** unblock Chloe.

---

## Exercise 3 (20 Min) — Content Exclusion Boundaries & Agentic Audit Trail

1. **Observe:** In `evaluate_security`, `/src/hsm/pin_block.c` matches the organization exclusion pattern `/src/hsm/**`.
   - On `IDE Inline Completions` and `Copilot cloud agent`, `blocked_by_exclusion` is `True`.
   - On `Copilot CLI local shell`, `surface_supports_content_exclusion` is `False` and `blocked_by_exclusion` is `False`.
2. **Design Remediation:** Write a 3-bullet architecture recommendation for the CISO combining:
   - Repository separation / RBAC for HSM modules
   - Enterprise Rulesets + Secret Scanning Push Protection + CodeQL / Copilot Autofix (compare PR `#108` vs. PR `#109`)
   - Audit log streaming (`actor:Copilot`, `agent_session_id`) + EMU `GET /enterprises/{enterprise}/copilot/usage-records` for session payload compliance.
