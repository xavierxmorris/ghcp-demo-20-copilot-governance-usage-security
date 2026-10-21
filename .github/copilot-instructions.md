# Repository guidance

Follow `AGENTS.md`. This repository is a public, synthetic 30-minute enterprise demo and deterministic evaluator for **GitHub Copilot Adoption, Governance, and Security**, ordered strictly by priority:

1. **GitHub Copilot Governance & Guardrails** (Priority 1 — 12 minutes)
2. **Usage, Reporting & Administration** (Priority 2 — 10 minutes)
3. **Security, Compliance & Auditability** (Priority 3 — 8 minutes)

## Rules for changes

- Keep all three pillars in strict 1 → 2 → 3 priority order across code, CLI output, HTML demo console, run-sheet, and discovery questions.
- Ground every product, API, policy, and billing claim in first-party GitHub Enterprise Cloud documentation (`2026-03-10` REST API). Cite exact URLs and retrieval dates in `docs/DEEP-RESEARCH-BRIEF.md`.
- Preserve critical architectural truths verified in official docs:
  - Multi-organization conflict resolution is **Least restrictive** for standard features (`Copilot CLI`, `The GitHub Copilot app`, `Copilot cloud agent`, `Copilot code review`, `MCP servers in Copilot`, `Copilot can search the web`) and **Most restrictive** for the four sensitive policies (`Copilot Metrics API`, `Semantic indexing for non-GitHub repositories` where `Unconfigured` behaves as `Disabled`, `Suggestions matching public code`, and `Allow members without a Copilot license to use Copilot code review in GitHub.com`).
  - `Default policy for new features` activates on **22 October 2026** (enabled by default for unconfigured GA features on `Features & clients` + `Copilot code review` + `MCP servers in Copilot`, excluding GHE.com data-residency/FedRAMP model restrictions and `Store local sessions in the Cloud`).
  - `Default availability for released models` applies only to models set to `Delegate to Default Policy` and never auto-enables pre-GA models, open-weight models (`DeepSeek`, `Kimi K3`), or models outside GitHub's data-retention agreement (`Claude Fable 5`, `Claude Fable 5.1`).
  - Surface enforcement boundaries: `Copilot can search the web` applies to IDEs and Copilot Chat in GitHub, not to Copilot cloud agent, Copilot CLI, or the Copilot app; `Suggestions matching public code` applies to IDEs and annotate-mode cloud/third-party agents, not Copilot CLI, the Copilot app, or Copilot code review; and **Copilot CLI and Agent mode in IDE Chat do not support repository/organization content exclusion**.
  - Usage metrics reconciliation: organization-level reports attribute activity by **organization membership** (not seat-billing org), `daily_active_cli_users` is separate from IDE `daily_active_users`, server-side telemetry users appear in DAU even when IDE client telemetry is disabled, `user-teams-1-day` omits teams with `<5` seated users, and AI Credit budgets follow the two-rule evaluation (single non-additive user-level budget `user` > `multi_user_cost_center` > `multi_user_customer`, then lowest remaining headroom across independent spending controls).
- Offline mode (`.\go.ps1`, `.\go.ps1 -Check`, `python -m copilot_governance`) must use Python 3.11+ standard library only, with zero network calls or credentials.
- Live inspection mode (`.\go.ps1 -Live`) is strictly **read-only** (`GET` only) and must never mutate enterprise/organization policies, seat assignments, or budgets.
