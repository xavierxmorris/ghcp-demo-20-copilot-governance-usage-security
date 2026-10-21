# Prompts for Live Demo & Customer Discovery (`ghcp-demo-20`)

Use these prompts in **GitHub Copilot CLI** or **Copilot Chat** during a live workshop to inspect, challenge, and adapt the three governance pillars.

## 1. Priority 1 — GitHub Copilot Governance & Guardrails

```text
Read fixtures/enterprise-scenario.json and copilot_governance/evaluator.py.
Explain why maya_dual_org receives Copilot CLI and Copilot cloud agent access even though regulated-payments disabled both, while her Suggestions matching public code and Copilot Metrics API settings remain locked down.
```

```text
Audit fixtures/enterprise-scenario.json for any enterprise policy currently set to "Unconfigured".
Which of those policies will automatically turn on under "Default policy for new features" on 22 October 2026, and which policies are explicitly exempt?
```

## 2. Priority 2 — Usage, Reporting & Administration

```text
Using the 28-day telemetry in fixtures/enterprise-scenario.json, explain:
1. Why summing organization DAUs produces 5 when enterprise DAU is 3.
2. Why noah_contractor_multi_ent is classified as "No Cohort" (Passive) despite 11 active chat days.
3. Why priya_cli_specialist reaches "Phase 3: Multi-agent" with zero IDE completion days.
```

```text
Walk through the two-rule AI Credit budget calculation for maya_dual_org, priya_cli_specialist, liam_payments_only, and chloe_enterprise_direct. Show which user-level tier wins in Rule 1 and which hard-stop control is binding in Rule 2.
```

## 3. Priority 3 — Security, Compliance & Auditability

```text
Inspect the content_exclusion rules and access_probes in fixtures/enterprise-scenario.json.
Why is /src/hsm/pin_block.c blocked in IDE Inline Completions and Copilot cloud agent, but NOT blocked by content exclusion in Copilot CLI or IDE Agent Mode? What compensating controls should we recommend to a CISO?
```
