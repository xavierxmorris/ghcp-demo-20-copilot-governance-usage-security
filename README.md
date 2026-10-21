# Demo 20 — GitHub Copilot Adoption, Governance & Security (30-Minute Enterprise Demo)

**Priority Order: 1. Governance & Guardrails → 2. Usage, Reporting & Administration → 3. Security, Compliance & Auditability**

A runnable **30-minute enterprise briefing, interactive HTML console, and deterministic Python evaluator** for GitHub Enterprise Cloud (`2026-03-10` REST API), grounded in first-party GitHub Docs retrieved **21 October 2026**.

```text
Priority 1 (00:00–12:00)  GitHub Copilot Governance & Guardrails
  ├─ Enterprise AI Controls (Agents, Copilot, MCP) & delegated AI Manager custom roles
  ├─ Multi-org conflict resolution: Least Restrictive vs. 4 Most Restrictive sensitive policies
  ├─ Direct enterprise-assigned seats ("Policies for enterprise-assigned users") & multi-enterprise locks
  ├─ 22 October 2026 "Default policy for new features" cutover + model delegation exclusions
  └─ Surface policy enforcement matrix (where web search, public code filter & MCP registry locks apply)

Priority 2 (12:00–22:00)  Usage, Reporting & Administration
  ├─ Copilot Usage Metrics API (2026-03-10 signed NDJSON reports: enterprise, users, repos CCA/CCR, user-teams)
  ├─ Impact Dashboard AI Adoption Cohorts (Passive / No Cohort, Phase 1 Code-first, Phase 2 Agent-first, Phase 3 Multi-agent)
  ├─ Six telemetry reconciliation rules (org membership attribution, server-side vs. IDE telemetry, separate CLI DAU, <5 team floor)
  └─ Two-rule AI Credit budget precedence (non-additive user-level selection + lowest hard-stop headroom)

Priority 3 (22:00–30:00)  Security, Compliance & Auditability
  ├─ Content exclusion YAML rules & the critical CLI / IDE Agent Mode non-support boundary
  ├─ 180-day Audit Log (action:copilot, actor:Copilot, agent_session_id) + SIEM streaming
  ├─ EMU Session Observability (GET /enterprises/{enterprise}/copilot/usage-records request/response pairing)
  └─ Agent PR security gates (Rulesets, Secret Scanning Push Protection, CodeQL + Copilot Autofix, human sign-off)
```

## Quick Start (100% Offline by Default)

Requires **Python 3.11+** (standard library only) and **PowerShell 7+** for `go.ps1`. Zero packages, credentials, or network access required.

```powershell
# 1. Validate all unit tests and repository contracts
.\go.ps1 -Check

# 2. Run the 30-minute timed or presenter-paced demo (opens docs\demo-console.html)
.\go.ps1 -Manual

# 3. Run headless in terminal and emit JSON + Markdown evaluation reports
.\go.ps1 -NoBrowser
python -m copilot_governance --out out\latest
```

## Key Artifacts in This Repository

| Artifact | Purpose |
| --- | --- |
| [`RUN-SHEET.md`](RUN-SHEET.md) | Minute-by-minute **30-minute presenter script** (`00:00–12:00` Governance, `12:00–22:00` Usage/Admin, `22:00–30:00` Security/Audit) |
| [`docs/demo-console.html`](docs/demo-console.html) | Self-contained **interactive HTML demo console** with persona simulator, cohort/reconciliation tables, content-exclusion tester, and question bank |
| [`docs/DEEP-RESEARCH-BRIEF.md`](docs/DEEP-RESEARCH-BRIEF.md) | Sourced **deep-research reference** with exact API endpoints, policy matrices, and dated GitHub Docs citations |
| [`docs/DISCOVERY-QUESTIONS.md`](docs/DISCOVERY-QUESTIONS.md) | **30 high-signal discovery & architecture questions** (with *Why ask*, *Red-flag answer*, and *Target architecture*) in 1 → 2 → 3 priority order |
| [`WORKSHOP.md`](WORKSHOP.md) | **60-minute hands-on architect/operator lab** with predict-observe-explain exercises and negative boundary tests |
| [`PROMPTS.md`](PROMPTS.md) | Ready-to-paste Copilot CLI and Chat prompts for live customer sessions |
| [`fixtures/enterprise-scenario.json`](fixtures/enterprise-scenario.json) | Synthetic enterprise (`aurorabank-ghec`) modeling 3 organizations, 6 personas, 28-day telemetry, AI Credit budgets, content exclusions, and audit logs |

## Top 10 High-Signal Takeaways Across the 3 Pillars

1. **Multi-Org Conflict Surprise (Pillar 1):** When an enterprise delegates policies (`Let organizations decide`), a developer in multiple organizations gets the **Least restrictive** setting for `Copilot CLI`, `The GitHub Copilot app`, `Copilot cloud agent`, `Copilot code review`, and `MCP servers in Copilot`—and the **Most restrictive** setting only for `Copilot Metrics API`, `Semantic indexing for non-GitHub repositories` (where `Unconfigured` = `Disabled`), `Suggestions matching public code`, and unlicensed Code Review.
2. **22 October 2026 Default Feature Cutover (Pillar 1):** `Default policy for new features` is enabled by default and auto-enables any `Unconfigured` GA feature on *Features & clients* plus `Copilot code review` and `MCP servers in Copilot` (exempting preview features, `Store local sessions in the Cloud`, and GHE.com data-residency/FedRAMP model locks).
3. **Model Auto-Enablement Safety (Pillar 1):** `Default availability for released models` never auto-enables preview models, open-weight models (`DeepSeek`, `Kimi K3`), or models outside GitHub's data-retention agreement (`Claude Fable 5`, `Claude Fable 5.1`).
4. **Direct Enterprise Seats Ignore Org Delegation (Pillar 1):** Users granted seats directly at the enterprise root are not covered by `Let organizations decide`; they follow `Policies for enterprise-assigned users`.
5. **Surface Enforcement Gaps (Pillar 1):** `Copilot can search the web` governs IDEs and GitHub.com Chat only—not Copilot cloud agent (which uses its own network firewall/allowlist) or Copilot CLI.
6. **AI Adoption Cohorts vs. Chat-Only Usage (Pillar 2):** Cohorts require `>=2` qualifying days in a trailing 28-day window (`Phase 1: Code first`, `Phase 2: Agent first`, `Phase 3: Multi-agent`). Asking questions in IDE Chat without applying code edits—or using GitHub.com Chat—leaves a user in `No Cohort` (`Passive users`).
7. **Why Org DAUs Never Sum to Enterprise DAU (Pillar 2):** Organization usage metrics attribute all activity of a licensed user to **every organization in the enterprise they belong to**, regardless of which organization pays for the seat (`billing-shell` pattern) or where code was written.
8. **Server-Side DAU & Separate CLI DAU (Pillar 2):** Users who disable IDE telemetry are still counted in `daily_active_users` via server-side telemetry (with empty feature/LoC breakdowns), while `daily_active_cli_users` is reported separately from IDE DAU. In CLI customization arrays, `plugin` interactions are already included in `skill` counts and must never be summed.
9. **Two-Rule AI Credit Budget Precedence (Pillar 2):** First select one non-additive user-level budget (`user` > `multi_user_cost_center` > `multi_user_customer`); then compare remaining headroom across independent hard-stop controls (`cost_center`, org, enterprise). Lowest remaining headroom blocks first.
10. **Content Exclusion Boundary & EMU Session Observability (Pillar 3):** Official GitHub Docs states that **Copilot CLI and Agent mode in IDE Chat do not support content exclusion**—requiring repo RBAC, OS permissions, CLI sandboxing, and Secret Scanning Push Protection. For auditability, `actor:Copilot` tracks agent actions (`agent_session_id`), while EMU enterprises can query/stream full prompt/response bodies via `GET /enterprises/{enterprise}/copilot/usage-records` (public preview).

## Honesty notes

- This repository is a **deterministic local simulator and enablement kit** using synthetic enterprise data (`aurorabank-ghec`). Running `.\go.ps1` or `python -m copilot_governance` does not modify or inspect any live GitHub enterprise unless `-Live -EnterpriseSlug <slug>` is explicitly passed.
- The optional `-Live` mode performs a single **read-only** `GET /enterprises/{enterprise}/copilot/metrics/reports/enterprise-28-day/latest` check and redacts signed URLs; it never mutates policies, seats, or budgets.
- Product behavior, policy names, and preview endpoints (`GET /enterprises/{enterprise}/copilot/usage-records`) were verified against official GitHub Enterprise Cloud documentation on **21 October 2026** (`2026-03-10` REST API) and can change over time.
