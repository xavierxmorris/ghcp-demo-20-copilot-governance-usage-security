# Deep Research Brief: GitHub Copilot Adoption, Governance & Security

**Retrieval Date:** 21 October 2026 | **GitHub REST API Version:** `2026-03-10` | **Target Plan:** GitHub Enterprise Cloud (Copilot Business & Copilot Enterprise, Standard & EMU / Data Residency)

This brief synthesizes first-party GitHub Enterprise Cloud documentation in strict priority order:
1. **GitHub Copilot Governance & Guardrails** (Priority 1)
2. **Usage, Reporting & Administration** (Priority 2)
3. **Security, Compliance & Auditability** (Priority 3)

---

## 1. Priority 1 — GitHub Copilot Governance & Guardrails

### 1.1 Enterprise AI Controls Architecture & Delegated Administration
- **Control Plane Navigation:** Enterprise owners configure policies under **Enterprise → AI controls**, split into three dedicated control surfaces:
  1. **Agents** (`github.com/enterprises/ENTERPRISE/ai-controls/agents`) — governs Copilot cloud agent (formerly Copilot coding agent), Copilot code review, and third-party agents.
  2. **Copilot** (`github.com/enterprises/ENTERPRISE/ai-controls/copilot`) — governs administration, privacy (`Suggestions matching public code`), model availability, billing/AI credit policies, and **Features & clients** (`Copilot CLI`, `The GitHub Copilot app`, `Copilot in GitHub.com`, `Copilot in GitHub Desktop`, `Copilot Chat in the IDE`, `Copilot Agent Mode in IDE Chat`, `Editor preview features`, `Spark`).
  3. **MCP** (`github.com/enterprises/ENTERPRISE/ai-controls/mcp`) — governs `MCP servers in Copilot` and `Restrict MCP access to registry servers`.
- **Delegated AI Managers:** Enterprises should avoid making every AI policy change require a full Enterprise Owner. Custom enterprise roles support the **`Manage enterprise AI controls`** and **`View Enterprise Copilot Metrics`** permissions, and custom organization roles support **`View organization Copilot metrics`**.

### 1.2 Policy Inheritance & Multi-Organization / Multi-Enterprise Conflict Resolution
When an enterprise policy is set to **Enabled everywhere** or **Disabled everywhere**, organizations cannot override it. When set to **Let organizations decide** (`No policy`), three distinct rules determine effective access:

| Assignment / Conflict Scenario | Resolution Rule | Critical Exceptions & Traps |
| --- | --- | --- |
| **User licensed in multiple organizations within the same enterprise** | **Least restrictive** wins for standard productivity features (`Copilot CLI`, `The GitHub Copilot app`, `Copilot cloud agent`, `Copilot code review`, `Copilot Agent Mode in IDE Chat`, `MCP servers in Copilot`, `Copilot can search the web`, `Spark`). | **Most restrictive** wins for **four compliance-sensitive policies**:<br>1. `Copilot Metrics API`<br>2. `Semantic indexing for non-GitHub repositories` (only available when **all** seat orgs explicitly set `Enabled`; `Unconfigured` behaves as `Disabled`)<br>3. `Suggestions matching public code` (privacy policy)<br>4. `Allow members without a Copilot license to use Copilot code review in GitHub.com` |
| **User assigned a Copilot seat directly at the enterprise level** | **Not covered** by `"Let organizations decide"`. | Governed by the separate **`Policies for enterprise-assigned users`** setting (`Enabled` or `Disabled`). Even if the user belongs to an organization that enabled a feature, a direct enterprise seat follows `Policies for enterprise-assigned users`. |
| **User licensed across multiple different enterprises** | **Most restrictive** across enterprises almost always wins (if *any* enterprise disables a feature, it is disabled everywhere for that user). | Two exceptions:<br>• `AI credit paid usage` (applies to each enterprise independently, not the user)<br>• `GitHub Spark` |

### 1.3 Default Availability Policies (Including the 22 October 2026 Cutover)
Two separate policies govern whether unconfigured GA features and models automatically turn on:

1. **`Default policy for new features` (Activates 22 October 2026):**
   - Enabled by default. Any newly released GA feature—or any existing GA feature left as **`Unconfigured`** on the enterprise `Features & clients` page, plus **`Copilot code review`** (on the `Agents` page) and **`MCP servers in Copilot`** (on the `MCP` page)—inherits this policy (`Enabled everywhere`, `Disabled everywhere`, or `Let organizations decide`).
   - **Explicit Exemptions (Never Auto-Enabled by Default Feature Policy):**
     - Preview features
     - Restrictive model policies on `ghe.com`: **`Restrict Copilot to data residency models`** and **`Restrict Copilot to FedRAMP models`**
     - **`Store local sessions in the Cloud`** for Copilot CLI and VS Code
2. **`Default availability for released models` (Active):**
   - Applies to models marked **`Delegate to Default Policy`**.
   - **Note:** When Enterprise Teams mode is enabled, the `Let organizations decide` state is unavailable at the enterprise level (replaced by `Delegate to Enterprise Teams/Apps`).
   - **Explicit Model Exclusions (Disabled by Default Regardless of Policy):**
     - Pre-GA / preview models (status: `Unconfigured`)
     - Open-weight models (**`DeepSeek`**, **`Kimi K3`**)
     - Models not covered by GitHub's data-retention agreement (**`Claude Fable 5`**, **`Claude Fable 5.1`**)
     - Any model violating active data-residency or FedRAMP model restrictions
3. **Pre-Vetted Custom LLM Models (BYOK):**
   - Enterprises with existing cloud/LLM agreements can attach their own pre-vetted LLM provider API keys (`Configure custom models`) for compliance, negotiated rates, and provider-side telemetry.

### 1.4 Supported Surfaces Policy Matrix (Where Policies Do *Not* Apply)
A policy toggle does **not** mean the capability is governed on every surface:

| Policy Name | IDEs | Copilot Cloud Agent | 3rd-Party Agents | Copilot CLI | GitHub Copilot App | Copilot Chat in GitHub | Copilot Code Review | Spark |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `Editor preview features` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `Copilot can search the web` | ✅ | ❌ *(uses agent firewall)* | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| `Configure custom models` | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `Suggestions matching public code` | ✅ | ✅ *(annotate mode only)* | ✅ *(annotate mode only)* | ❌ | ❌ | ❌ | ❌ | ❌ |
| `MCP servers in Copilot` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| `Restrict MCP access to registry servers` | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `Content exclusion` *(surface table vs local agent note)* | ✅ *(except IDE Agent mode)* | ✅ | ❌ | ❌ *(not supported in CLI)* | ✅ | ✅ | ✅ | ❌ |
| `Configure models` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `Copilot Memory` | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |

> **Critical MCP Governance Boundary:** The `MCP servers in Copilot` policy governs Copilot surfaces where MCP is GA. It does **not** control access to the GitHub MCP Server from third-party host apps (such as Cursor, Windsurf, or Claude Desktop); those must be governed via GitHub OAuth/GitHub App installation policies and Personal Access Token policies.

### 1.5 Repository & Agent Instruction Guardrails
- **Instruction Layering:**
  - `~/.copilot/copilot-instructions.md` — personal CLI defaults
  - `.github/copilot-instructions.md` — repository-wide conventions
  - `AGENTS.md` (and nested `AGENTS.md`) — agent contract
  - `.github/instructions/*.instructions.md` — path/glob-scoped rules
- Applicable instructions combine; they are developer/quality guardrails, **not** a security sandbox. Hard boundaries require repository rulesets, environment approvals, and network allowlists.

---

## 2. Priority 2 — Usage, Reporting & Administration

### 2.1 Choosing the Right API: Usage Metrics API vs. User Management API
GitHub provides two non-interchangeable REST API families (`X-GitHub-Api-Version: 2026-03-10`):

1. **Copilot Usage Metrics API (`/enterprises/{enterprise}/copilot/metrics/reports/...` and `/orgs/{org}/copilot/metrics/reports/...`):**
   - Requires the **`Copilot usage metrics`** policy set to **Enabled everywhere** (or enabled in the org) and Enterprise Owner, Billing Manager, or custom role permission **`View Enterprise Copilot Metrics`** / **`View Organization Copilot Metrics`** (or `manage_billing:copilot` / `read:enterprise` / `read:org` token scopes).
   - Returns **signed download URLs** (`download_links`) to daily or 28-day **NDJSON** report files (available from **10 October 2025** at enterprise scope and **12 December 2025** at organization scope, with up to 1 year of history):
     - `enterprise-1-day` / `organization-1-day` (`?day=YYYY-MM-DD`) — aggregated daily DAU/WAU/MAU, LoC, language/model/feature breakdowns, and `pull_requests`.
     - `enterprise-28-day/latest` / `organization-28-day/latest` — rolling 28-day `day_totals` plus top-level `copilot_feature_engagement` across 7 features (`code_completion`, `agent_edit`, `code_review_passive`, `code_review_active`, `cloud_agent`, `copilot_cli`, `github_app`).
     - `users-1-day` / `users-28-day/latest` — per-user records containing `user_id`, `user_login`, **`ai_credits_used`**, `user_initiated_interaction_count`, `code_generation_activity_count`, `code_acceptance_activity_count`, LoC sums, `used_*` booleans, **`ai_adoption_phase`**, and **Copilot CLI customization telemetry** (`distinct_*_use_count` and top-5 arrays `totals_by_skill`, `totals_by_custom_agent`, `totals_by_mcp`, `totals_by_slash_cmd`, `totals_by_plugin`).
     - `repos-1-day` (`?day=YYYY-MM-DD`) — per-repository pull request lifecycle metrics, including **Copilot Cloud Agent (`CCA`)** PR creation/merge counts and **Copilot Code Review (`CCR`)** review/suggestion counts and stage durations. Returns `204 No Content` if no repos had PR activity that day.
     - `user-teams-1-day` (`?day=YYYY-MM-DD`) — maps `user_id` / `user_login` to `team_id` / `slug` so BI pipelines can join with `users-1-day` to build team-level metrics. **Privacy floor:** teams with **fewer than 5 seated Copilot users** on that day are omitted.
2. **Copilot User Management API (`/orgs/{org}/copilot/billing/seats`, etc.):**
   - Source of truth for **license and seat state** and `last_activity_at`. Usage metrics reports do not include unlicensed/idle seat inventories unless joined with User Management data.

### 2.2 AI Adoption Cohorts & Impact Dashboard
Instead of treating a one-time autocomplete user the same as an agent orchestrator, GitHub classifies licensed users over a **trailing 28-day window** (requiring **at least 2 active qualifying days** in the 28-day window):

| Cohort Phase | Qualifying Criteria (>= 2 active days in trailing 28 days) | Key Interpretation |
| --- | --- | --- |
| **Passive users (`No Cohort` in API)** | Has not met the 2-day threshold for Phases 1–3. | Includes users who only ask questions in IDE Chat or Agent mode **without** applying code edits, or who only use Copilot Chat on GitHub.com. |
| **Phase 1: Code first** | Engaged with **code completions** and/or **IDE agent edits** (where Copilot writes changes directly into files). | Baseline IDE productivity; target with Cloud Agent or CLI enablement to advance to Phase 2. |
| **Phase 2: Agent first** | Engaged with **one** GitHub-based agent surface: **Copilot cloud agent**, **Copilot code review** (active *or* passive auto-assigned review count as the same surface), or **Copilot CLI**. | Users have crossed into asynchronous/terminal agent workflows. |
| **Phase 3: Multi-agent** | Engaged with **two or more** GitHub-based agent surfaces, **or** engaged with **The GitHub Copilot app**. | Highest-leverage cohort; compared against Passive users via the **Adoption Multiplier** (PRs merged per user per month and median time to merge). |

### 2.3 Six Reconciliation Traps Every Admin & Architect Must Know
1. **Organization Membership Attribution ("Shell Billing Org" Trap):** Organization-level metrics attribute a user's activity to **every organization in the enterprise where the user is a member**, *not* the organization that pays for their seat or where the code was written. Summing organization DAUs double-counts multi-org members compared to Enterprise DAU.
2. **Server-Side vs. Client-Side IDE Telemetry:** When a developer disables IDE telemetry (or a corporate proxy blocks it), server-side telemetry still counts them in `daily_active_users` (and `totals_by_ide`), but `totals_by_feature`, `totals_by_language_*`, and LoC fields remain empty. Top-level DAU can legitimately exceed the sum of feature breakdowns.
3. **Copilot CLI DAU is Separate:** `daily_active_cli_users` and `totals_by_cli` are tracked independently and are **not** included in IDE `daily_active_users` or dashboard charts.
4. **CLI Customization Double-Counting Trap:** In `totals_by_skill` and `totals_by_plugin`, **every plugin interaction is already included in skill interaction counts**. Never add `plugin` and `skill` interaction counts together. Also, per-record arrays only list the **top 5** items; an absent item is not zero usage.
5. **28-Day Dashboard Cohort vs. 1-Day API Cohort:** The Impact Dashboard `Adoption cohort distribution` includes all users active across the 28-day window, whereas the daily report's `totals_by_ai_adoption_phase` only counts users active **on that specific day**.
6. **Data Finalization Window:** Telemetry finalizes within **2 to 3 full UTC days**. Re-export NDJSON files after 3 UTC days for immutable BI reporting.

### 2.4 Cost Centres & AI Credit Budgets (Post–June 1, 2026 Model)
- Legacy premium-request billing applies only to grandfathered annual Pro/Pro+ plans remaining after June 1, 2026. Enterprise governance uses **Cost Centres** and **AI Credit budgets** (`ai_credits_used` in per-user reports).
- **Two-Rule Precedence Evaluation:**
  1. **Rule 1 — Select ONE User-Level Budget (Non-Additive):** Explicit individual `user` budget overrides `multi_user_cost_center` (per-user cost-centre budget), which overrides `multi_user_customer` (enterprise universal per-user default). They **never add together**.
  2. **Rule 2 — Evaluate Independent Overlapping Controls:** Compare remaining headroom across the selected user-level budget and any active hard-stop shared spending budgets (`cost_center`, organization, enterprise), plus the **AI credit paid usage** policy. The control with the **lowest remaining headroom blocks first**. An alert-only shared cost-centre budget (`hard_stop = false`) sends alerts at 75%, 90%, and 100% but never overrides a hard user limit.

---

## 3. Priority 3 — Security, Compliance & Auditability

### 3.1 Content Exclusion & Its Surface Boundary
- **Configuration:** Configured at Repository settings (`Settings → Copilot → Content exclusion`) and Organization settings (`Settings → Copilot → Content exclusion`) using case-insensitive `fnmatch` YAML patterns (`"*":` for all filesystem/repo roots, or `http[s]://`, `git://`, `ssh://` repository references, including GitHub and Azure DevOps `dev.azure.com` / `visualstudio.com` remotes). Repository settings display inherited organization/enterprise exclusions in **read-only gray boxes**. Changes propagate to IDEs within ~30 minutes.
- **Critical Surface Limitation (First-Party Documented):**
  > *"GitHub Copilot CLI and Agent mode in Copilot Chat in IDEs do not support content exclusion."*
  - **What this means for Security Architects:** While inline completions, IDE Chat (Ask/Edit), GitHub.com Chat, Copilot cloud agent, and Copilot code review enforce content exclusion, a developer running **Copilot CLI** or **IDE Agent Mode** has local tool/shell access to files on disk.
  - **Required Compensating Controls:** Do not use Content Exclusion as a substitute for **repository RBAC** (separate repositories for crown-jewel HSM/crypto secrets), **local OS file permissions**, **Copilot CLI sandbox/permission policies**, and **Secret Scanning Push Protection**.

### 3.2 Audit Logs (`action:copilot` & `actor:Copilot`) vs. EMU Session Observability (`usage-records`)
GitHub separates **control-plane/agent action auditing** from **prompt/response payload observability**:

| Capability | Enterprise / Org Audit Log | EMU Session Usage Records API (Public Preview) |
| --- | --- | --- |
| **Scope & Access** | All GHEC / Copilot Business & Enterprise plans (`Settings → Audit log`, REST/GraphQL API, SIEM streaming). Retained **180 days**. | **EMU (GHEC & GHEC with Data Residency on `ghe.com`) Enterprise Owners only** (`GET /enterprises/{enterprise}/copilot/usage-records`, `read:enterprise` scope). |
| **What It Captures** | • Admin/policy/seat events (`action:copilot`, e.g., `copilot.cfb_seat_assignment_created`, content exclusion edits)<br>• GitHub-hosted agent actions (`actor:Copilot`, `actor_is_agent: true`, `agent_session_id`, initiating `user`) | Streamed or queried **`request`** and **`response`** payloads (`body` JSON string up to 1 MB with `truncated` flag, `github_request_id`, `event_id`, `endpoint`, `user_id`, `@timestamp`) across **Cloud Agents, Copilot CLI, VS Code, Visual Studio, JetBrains, and Eclipse**. |
| **What It Excludes** | Does **not** log local IDE or CLI prompt/response text. | Requires EMU / Data Residency; non-EMU enterprises must use client hooks or SIEM forwarders for local CLI prompt logging. |

### 3.3 IP Indemnity, Public Code Filter & Securing AI-Generated Code
- **Public Code Filter (`Suggestions matching public code`):** Set to `Blocked` (or `Allowed` with code-referencing logs). Remember it is a **Most restrictive** policy across organizations in an enterprise, and applies to IDEs and annotate-mode cloud/3rd-party agents (not CLI/App/Code Review).
- **Mandatory PR Guardrails for Agent-Authored Code:**
  - **Repository Rulesets:** Require pull requests, required status checks, and **at least 1 independent human approval** (`copilot-swe-agent[bot]` cannot approve or merge its own pull request, and the user who delegated the task should be backed by branch/ruleset review requirements).
  - **Secret Scanning Push Protection:** Blocks commits containing credentials whether pushed by a human or by Copilot cloud agent.
  - **CodeQL + Copilot Autofix & Dependency Review:** Automatically scans every agent-created PR for vulnerabilities (SQLi, XSS, SSRF, vulnerable dependencies) and proposes deterministic remediation before human sign-off.

---

## 4. Authoritative References (Retrieved 21 October 2026)

1. [Managing policies and features for GitHub Copilot in your enterprise](https://docs.github.com/en/enterprise-cloud@latest/copilot/managing-copilot/managing-copilot-for-your-enterprise/managing-policies-and-features-for-copilot-in-your-enterprise)
2. [GitHub Copilot policies for enterprises and organizations](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/enterprise/policies)
3. [Feature availability when GitHub Copilot policies conflict in organizations](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/enterprise-administrators/policy-conflicts)
4. [About default availability of Copilot features and models](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/enterprise/default-availability)
5. [Supported surfaces for GitHub Copilot policies](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/supported-surfaces-for-policies)
6. [Governing Copilot to support developer productivity](https://docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/roll-out-at-scale/govern-at-scale/govern-for-adoption)
7. [REST API endpoints for Copilot usage metrics (`2026-03-10`)](https://docs.github.com/en/enterprise-cloud@latest/rest/copilot/copilot-usage-metrics)
8. [Data available in Copilot usage metrics](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/copilot-usage-metrics/copilot-usage-metrics)
9. [Interpreting usage and adoption metrics for GitHub Copilot](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/copilot-usage-metrics/interpret-copilot-metrics)
10. [Reconciling Copilot usage metrics across dashboards, APIs, and reports](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/copilot-usage-metrics/reconciling-usage-metrics)
11. [GitHub Copilot usage metrics & adoption cohorts](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/billing-and-usage/copilot-usage-metrics/copilot-metrics)
12. [Excluding content from GitHub Copilot](https://docs.github.com/en/enterprise-cloud@latest/copilot/managing-copilot/configuring-and-auditing-content-exclusion/excluding-content-from-github-copilot)
13. [Reviewing audit logs for GitHub Copilot](https://docs.github.com/en/enterprise-cloud@latest/copilot/managing-copilot/managing-github-copilot-in-your-organization/reviewing-activity-related-to-github-copilot-in-your-organization/reviewing-audit-logs-for-copilot-business)
14. [Audit log events for agents (`actor:Copilot`, `agent_session_id`, EMU `usage-records`)](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/enterprise-administrators/agentic-audit-log-events)
