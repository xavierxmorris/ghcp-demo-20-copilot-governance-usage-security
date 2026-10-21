# High-Signal Discovery & Architecture Questions: GitHub Copilot Adoption, Governance & Security

Organized in strict priority order (**1. Governance & Guardrails → 2. Usage, Reporting & Administration → 3. Security, Compliance & Auditability**). Every question includes:
- **Why ask** (the architectural or operational risk it uncovers)
- **Red-flag customer answer** (what signals a hidden misconfiguration or misconception)
- **Target architecture / remediation** (grounded in GitHub Enterprise Cloud docs, retrieved 21 October 2026)

---

## Priority 1 — GitHub Copilot Governance & Guardrails (Questions 1–10)

### Q1. Multi-Organization Policy Bleed vs. Sensitive Policy Locks
> *"Do any of your developers belong to more than one GitHub organization in your enterprise (for example, a restricted regulated org and an innovation/sandbox org), and have you delegated Copilot policies using 'Let organizations decide'?"*
- **Why ask:** In GHEC, when a user holds seats or access across multiple organizations in the same enterprise, **Least restrictive** wins for almost all features (`Copilot CLI`, `The GitHub Copilot app`, `Copilot cloud agent`, `Copilot code review`, `Copilot Agent Mode in IDE Chat`, `MCP servers in Copilot`, `Copilot can search the web`). Only **four** policies enforce **Most restrictive** (`Copilot Metrics API`, `Semantic indexing for non-GitHub repositories`, `Suggestions matching public code`, and `Allow members without a Copilot license to use Copilot code review in GitHub.com`).
- **Red-flag answer:** *"We disabled Copilot CLI and Agent Mode in our PCI payments org, so developers in that org can't use them—even though they're also members of our shared digital org."*
- **Target architecture:** Scope strict compliance isolation at the enterprise level, remove dual-org licensing for restricted personas, or explicitly disable non-negotiable surfaces enterprise-wide while using repository-level controls for Copilot cloud agent.

### Q2. The 22 October 2026 `Default policy for new features` Cutover
> *"What is your enterprise setting for `Default policy for new features` and `Default availability for released models`, and have you audited which policies are currently sitting in `Unconfigured` state?"*
- **Why ask:** Starting **22 October 2026**, `Default policy for new features` (which defaults to **Enabled**) governs every new GA feature and every existing GA feature left as `Unconfigured` on `Features & clients`, plus `Copilot code review` and `MCP servers in Copilot`.
- **Red-flag answer:** *"We leave new features `Unconfigured` until our security board reviews them."*
- **Target architecture:** Audit the enterprise banner showing eligible `Unconfigured` policies. Either explicitly set restricted policies to `Disabled everywhere` / `Let organizations decide` (with org defaults set appropriately) or set `Default policy for new features` to `Disabled everywhere` in regulated tenants. Note that preview features, `Store local sessions in the Cloud`, and GHE.com data-residency/FedRAMP model locks are exempt.

### Q3. Model Governance & Automatic Enablement Exclusions
> *"How do you onboard new frontier models vs. open-weight or non-standard data-retention models, and do you use pre-vetted BYOK custom model endpoints?"*
- **Why ask:** `Default availability for released models` automatically enables GA models labeled `Delegate to Default Policy`, **excluding** pre-GA preview models, open-weight models (`DeepSeek`, `Kimi K3`), and models outside GitHub's data-retention agreement (`Claude Fable 5`, `Claude Fable 5.1`), which stay disabled unless explicitly turned on.
- **Red-flag answer:** *"We turned off auto-model availability because we were afraid preview or open-weight models would turn on automatically—now our developers are stuck on year-old models."*
- **Target architecture:** Keep `Default availability for released models` enabled for vetted GA models (since preview, open-weight, and non-retention models are excluded by design), or attach pre-vetted provider keys via `Configure custom models`.

### Q4. Direct Enterprise-Assigned Seats vs. `"Let organizations decide"`
> *"Do you assign any Copilot seats directly at the enterprise level (or via Enterprise Teams) rather than through organizations?"*
- **Why ask:** Users who receive Copilot directly from the enterprise are **not covered** by `"Let organizations decide"`. Their access is controlled by a separate **`Policies for enterprise-assigned users`** toggle (`Enabled` or `Disabled`). Similarly, enabling Enterprise Teams mode removes `"Let organizations decide"` from model availability in favor of `"Delegate to Enterprise Teams/Apps"`.
- **Red-flag answer:** *"We assigned seats at the enterprise root to simplify billing, and set policies to 'Let organizations decide' so each org owner can manage their people."*
- **Target architecture:** Explicitly configure `Policies for enterprise-assigned users` or assign seats via organization/enterprise teams with matching delegation mode.

### Q5. Contractors Licensed Across Multiple Enterprises
> *"Do external contractors or partner consultants bring their own GitHub identity that also holds a Copilot license in their employer's enterprise?"*
- **Why ask:** When a user is licensed across **multiple enterprises** (non-EMU), the **most restrictive** policy across all enterprises applies to that user for almost every feature (except `AI credit paid usage` and `GitHub Spark`).
- **Red-flag answer:** *"Our systems-integrator contractors say Copilot CLI and Cloud Agent are greyed out for them even though we enabled both in our org."*
- **Target architecture:** Provision contractors with dedicated **Enterprise Managed User (EMU)** identities in your enterprise so external enterprise policies cannot bleed into your environment (and vice versa).

### Q6. Surface-Specific Policy Enforcement Gaps (`Copilot can search the web`)
> *"When you disable `Copilot can search the web`, which Copilot surfaces do you believe are blocked from reaching the internet?"*
- **Why ask:** Per GitHub's *Supported surfaces for GitHub Copilot policies* matrix, `Copilot can search the web` applies **only** to **IDEs** and **Copilot Chat in GitHub.com**. It does **not** control internet access for **Copilot cloud agent**, **Copilot CLI**, or **The GitHub Copilot app**.
- **Red-flag answer:** *"We disabled web search in Copilot settings, so Copilot cloud agent and Copilot CLI cannot make outbound internet requests."*
- **Target architecture:** Configure the dedicated **Copilot cloud agent firewall / allowlist** for cloud-agent egress, and use Copilot CLI sandbox/network settings and corporate proxy controls for local terminal agents.

### Q7. MCP Server Governance: Registry Lock vs. Third-Party Hosts
> *"How are you governing Model Context Protocol (MCP) servers in IDEs and CLI versus third-party AI clients connecting to your GitHub repositories?"*
- **Why ask:** Enabling `MCP servers in Copilot` + `Restrict MCP access to registry servers` governs IDEs, Copilot CLI, and the GitHub Copilot app—but **does not** block third-party hosts (Cursor, Windsurf, Claude) from calling the GitHub MCP Server using a user's OAuth token or PAT.
- **Red-flag answer:** *"We turned off 'MCP servers in Copilot' so nobody can connect external AI clients to our GitHub org via MCP."*
- **Target architecture:** Pair `MCP servers in Copilot` + `Restrict MCP access to registry servers` with GitHub App approval policies, fine-grained PAT lifetimes/policies, and Conditional Access / IP allowlists.

### Q8. Copilot CLI vs. GitHub Copilot Desktop App Separation
> *"Do your security policies treat Copilot CLI and the GitHub Copilot desktop app as a single client or separate policies?"*
- **Why ask:** They are governed by **two independent client policies** (`Copilot CLI` and `The GitHub Copilot app`), even though the desktop app is built on the Copilot CLI runtime. Furthermore, `Copilot Memory` is supported on Cloud Agent, 3rd-party agents, Copilot CLI, and Code Review, but not IDEs or the Copilot app.
- **Red-flag answer:** *"We only enabled the Copilot CLI policy and don't know why the Copilot app is blocked (or vice versa)."*
- **Target architecture:** Explicitly align both client policies (`Copilot CLI` and `The GitHub Copilot app`) per persona cohort.

### Q9. Delegating AI Administration Without Over-Privileging
> *"Who currently holds permission to change Copilot policies or pull usage metrics—only Enterprise Owners, or a dedicated AI Governance / Platform Engineering team?"*
- **Why ask:** Relying on full Enterprise Owners creates bottlenecks or leads to over-granting Enterprise Owner to platform leads, increasing policy-drift risk.
- **Red-flag answer:** *"We made five engineering managers Enterprise Owners so they could check Copilot metrics and toggle models."*
- **Target architecture:** Create custom roles with least-privilege permissions: **`Manage enterprise AI controls`**, **`View Enterprise Copilot Metrics`**, and **`View organization Copilot metrics`**.

### Q10. Repository Instructions (`AGENTS.md`) vs. Hard Platform Controls
> *"Where do you draw the line between repository instruction files (`AGENTS.md`, `.github/copilot-instructions.md`) and platform enforcement?"*
- **Why ask:** Instruction files combine across scopes (`~/.copilot`, `.github/copilot-instructions.md`, `AGENTS.md`, `.github/instructions/*.instructions.md`) to steer code quality and architecture, but they are **not an authorization boundary** (and VS Code inline completions do not read custom instruction files).
- **Red-flag answer:** *"We put 'Never touch production workflows or secrets' in `AGENTS.md` as our primary security control."*
- **Target architecture:** Use `AGENTS.md` and path-scoped `.instructions.md` for coding standards, test gates, and architecture conventions; enforce security boundaries with repository rulesets, CODEOWNERS, and GitHub Actions environment protection rules.

---

## Priority 2 — Usage, Reporting & Administration (Questions 11–20)

### Q11. Usage Metrics API (`2026-03-10`) vs. User Management API
> *"Are your BI dashboards pulling from the current Copilot Usage Metrics NDJSON report endpoints (`/copilot/metrics/reports/...`) and joining with the User Management API for seat state?"*
- **Why ask:** The Usage Metrics API provides 1-day and 28-day signed NDJSON reports (`enterprise`, `organization`, `users`, `repos`, `user-teams`), while license/seat assignment and `last_activity_at` live in the **Copilot User Management API**. Neither replaces the other.
- **Red-flag answer:** *"We only query `/copilot/metrics` and wonder why completely idle licensed seats aren't listed with seat assignment dates."*
- **Target architecture:** Ingest daily NDJSON exports (`users-1-day`, `repos-1-day`, `user-teams-1-day`) after the 2–3 UTC day finalization window, and join with the Copilot User Management seat inventory.

### Q12. Moving Beyond Flat DAU to AI Adoption Cohorts (Phases 1–3)
> *"What percentage of your licensed developers are in **Phase 2 (Agent first)** and **Phase 3 (Multi-agent)** versus plateauing in **Phase 1 (Code first)** or **Passive (`No Cohort`)**?"*
- **Why ask:** Flat DAU treats a developer who accepts one autocomplete line the same as one orchestrating Cloud Agent + Code Review + CLI. GitHub's Impact Dashboard groups users over a trailing 28-day window (2+ active days required) into `Passive (No Cohort)`, `Phase 1 (Code first)`, `Phase 2 (Agent first)`, and `Phase 3 (Multi-agent)`, and links cohorts to PR throughput via the **Adoption Multiplier**.
- **Red-flag answer:** *"We have 75% monthly active users, so our Copilot rollout is complete."*
- **Target architecture:** Track cohort progression from Phase 1 → Phase 2 (enable 1 agent surface: Cloud Agent, Code Review, or CLI) → Phase 3 (2+ agent surfaces or Copilot App) alongside PR merge velocity (`repos-1-day`).

### Q13. Why Chat-Only Users Appear as `Passive (No Cohort)`
> *"Why do some developers who use Copilot Chat every day show up as `Passive users` (`No Cohort` in the API) on the Impact Dashboard?"*
- **Why ask:** Per GitHub Docs, asking questions in IDE Chat or Agent mode **without** producing code completion or agent file-edit activity (or using only Copilot Chat on GitHub.com) does **not** qualify a user for Phase 1.
- **Red-flag answer:** *"Our architects use Chat all day for design reviews, so the dashboard must be broken because it marks them Passive."*
- **Target architecture:** Cross-check `user_initiated_interaction_count` and `used_chat` in `users-28-day/latest` alongside `ai_adoption_phase` when evaluating non-coding roles (architects, BAs, security reviewers).

### Q14. The "Shell Billing Organization" Attribution Trap
> *"Do you assign Copilot licenses in a central 'billing shell' organization while developers work in separate product organizations?"*
- **Why ask:** Organization-level Copilot metrics attribute a licensed user's entire activity to **every organization in the enterprise they belong to**, regardless of which organization provides the seat or where the code was written.
- **Red-flag answer:** *"We summed the DAU across our 12 GitHub organizations and got 1,800 active users—even though we only bought 900 seats!"*
- **Target architecture:** Use `enterprise-28-day/latest` or `users-1-day` for deduplicated enterprise totals; use organization reports only for intra-org trend analysis, never for cross-org summation.

### Q15. IDE Telemetry Blockers vs. Server-Side Active Users
> *"Have your workstation GPO/MDM profiles or corporate proxies disabled IDE telemetry in VS Code, Visual Studio, or JetBrains?"*
- **Why ask:** When IDE client telemetry is disabled or blocked, GitHub's **server-side telemetry** still counts those developers in `daily_active_users` (and `totals_by_ide`), but `totals_by_feature`, `totals_by_language_*`, and Lines-of-Code metrics are empty!
- **Red-flag answer:** *"Our dashboard shows 400 Daily Active Users, but the feature and language charts only add up to 120 users."*
- **Target architecture:** Verify IDE telemetry settings and proxy allowlists (`*.github.com`, `*.githubusercontent.com`, Copilot telemetry endpoints) and ensure IDEs meet minimum versions (VS Code `1.107.1+` / Chat `0.35.3+`, Visual Studio `17.14.13+`, JetBrains `2024.2.6+`, Eclipse `4.31+`, Xcode `13.2.1+`).

### Q16. Separate Copilot CLI Telemetry & Customization Analytics
> *"How are you tracking Copilot CLI adoption, and how do you discover which internal skills, custom agents, plugins, and MCP servers developers actually use?"*
- **Why ask:** `daily_active_cli_users` is tracked **separately** from IDE `daily_active_users` and is omitted from main IDE dashboard charts. Moreover, CLI customization telemetry (`totals_by_skill`, `totals_by_custom_agent`, `totals_by_mcp`, `totals_by_slash_cmd`, `totals_by_plugin`) is **API-only** (`users-1-day`, `enterprise-1-day`, `users-28-day`).
- **Red-flag answer:** *"We look at the main Copilot Usage Dashboard to see CLI and MCP adoption."*
- **Target architecture:** Query `daily_active_cli_users`, `totals_by_cli`, and `totals_by_skill` / `totals_by_mcp` from the Usage Metrics API. Remember: **do not add `plugin` and `skill` interaction counts together** (plugin skill runs are already included in `totals_by_skill`), and each array only returns the **top 5** items per record.

### Q17. Team-Level Reporting & The `<5` Seated Users Privacy Floor
> *"How are you building team-level Copilot adoption reports, and why do small squads disappear from team exports?"*
- **Why ask:** Team metrics are not pre-aggregated; you must join `user-teams-1-day` with `users-1-day`. Teams with **fewer than 5 seated Copilot users** on a given day are excluded from `user-teams-1-day`.
- **Red-flag answer:** *"Our 3-person security architecture team is missing from `user-teams-1-day`, so we think their seats are broken."*
- **Target architecture:** Join `user-teams-1-day` + `users-1-day` for teams with `>=5` seated users, and fall back to an internal HR/Entra group mapping for small (<5 seat) specialist squads.

### Q18. Repository-Level PR Lifecycle Metrics (`repos-1-day` CCA & CCR)
> *"How do you measure whether Copilot Cloud Agent (`CCA`) and Copilot Code Review (`CCR`) are actually reducing PR cycle time per repository?"*
- **Why ask:** `GET /enterprises/{enterprise}/copilot/metrics/reports/repos-1-day?day=YYYY-MM-DD` provides per-repository PR creation, merge, suggestion acceptance, and review-stage duration breakdowns specifically separating human PRs, **CCA (Copilot Coding/Cloud Agent)** PRs, and **CCR (Copilot Code Review)** reviews.
- **Red-flag answer:** *"We only measure Lines of Code accepted in the IDE to prove ROI to leadership."*
- **Target architecture:** Combine `repos-1-day` (CCA PR merge rate + CCR review coverage + PR stage duration) with Impact Dashboard cohort metrics to report end-to-end delivery impact.

### Q19. Two-Rule AI Credit Budget Precedence (User-Level vs. Shared Cost Centre)
> *"When you configure a shared Cost Centre budget alongside an enterprise default per-user budget (`multi_user_customer`) and a cost-centre per-user budget (`multi_user_cost_center`), which limit actually stops a developer?"*
- **Why ask:** AI Credit budgets follow **two rules, not one**:
  1. Select **one** applicable user-level budget (`explicit user` > `multi_user_cost_center` > `multi_user_customer`); they **never add together**.
  2. Evaluate all independent hard-stop controls (the selected user-level budget + shared `cost_center` budget + org/enterprise spending budgets + `AI credit paid usage` policy); **whichever hard-stop control has the lowest remaining headroom blocks first**.
- **Red-flag answer:** *"We raised the shared cost-centre budget from $100 to $500, so our power users won't get blocked—even though the enterprise per-user default is still a hard $10 cap."*
- **Target architecture:** Give power-user cohorts an explicit `multi_user_cost_center` per-user limit (or explicit `user` override) in addition to an alert-only (`hard_stop = false`) or appropriately sized shared cost-centre budget.

### Q20. Reconciling 28-Day Dashboard Cohorts vs. Daily API Exports
> *"Why do your BI team's daily API cohort percentages (`totals_by_ai_adoption_phase`) never match the Impact Dashboard's cohort chart?"*
- **Why ask:** Both use the same trailing 28-day phase definition, but **different populations**: the Impact Dashboard includes every user active during the 28-day window, while `totals_by_ai_adoption_phase` in a daily API record only counts users active **on that single day**.
- **Red-flag answer:** *"Our BI pipeline sums `totals_by_ai_adoption_phase` from `enterprise-1-day` and gets different cohort percentages than the GitHub UI."*
- **Target architecture:** Use `users-28-day/latest` (or `copilot_feature_engagement.active_user_count` on `report_end_day` of `enterprise-28-day/latest`) when reconciling against the 28-day Impact Dashboard.

---

## Priority 3 — Security, Compliance & Auditability (Questions 21–30)

### Q21. The Content Exclusion Surface Boundary (Copilot CLI & IDE Agent Mode)
> *"Which sensitive files do you protect with Copilot Content Exclusion, and are developers using **Copilot CLI** or **IDE Agent Mode** in repositories containing those files?"*
- **Why ask:** GitHub's official Content Exclusion documentation states explicitly:
  > *"GitHub Copilot CLI and Agent mode in Copilot Chat in IDEs do not support content exclusion."*
- **Red-flag answer:** *"We added `/secrets/**` and `*.pem` to Content Exclusion, so developers using IDE Agent Mode or Copilot CLI can't read or leak those files."*
- **Target architecture:** Treat Content Exclusion as a preventive control for supported surfaces (inline completions, IDE Ask/Edit chat, GitHub.com Chat, Cloud Agent, Code Review), and isolate crown-jewel secrets/HSM code using **repository RBAC**, **OS file permissions**, **Copilot CLI sandboxing/hooks**, and **Secret Scanning Push Protection**.

### Q22. Organization-Wide Wildcard (`"*":`) vs. Multi-Protocol Repository Exclusion
> *"Do your organization content-exclusion rules protect sensitive files outside Git repositories or in repositories cloned via SSH vs. HTTPS?"*
- **Why ask:** Organization content exclusion supports `"*":` to match files **anywhere on the filesystem** (even outside Git control) and normalizes `http[s]://`, `git://`, `ssh://`, and `[user@]host.xz:path/to/repo.git` (including Azure DevOps `dev.azure.com` and `visualstudio.com` remotes).
- **Red-flag answer:** *"We only configured content exclusion inside a few individual repository settings pages."*
- **Target architecture:** Configure baseline wildcard exclusions (`"*": ["**/*.pem", "**/*.key", ".env*"]`) at the **organization** level so they apply across all repos and non-Git local directories, and verify inherited read-only gray boxes in repository settings.

### Q23. Auditing Agentic Actions (`actor:Copilot` & `agent_session_id`)
> *"If Copilot cloud agent opens a pull request or modifies a branch, how does your SOC trace that action back to the exact human who initiated it and the specific agent session?"*
- **Why ask:** Enterprise audit logs support the `actor:Copilot` filter. Every agentic event includes `actor_is_agent: true`, `agent_session_id` (UUID linking all actions in that session), and `user` (the human who initiated the agent task).
- **Red-flag answer:** *"All bot actions look the same in our SIEM; we can't tell which developer triggered a Copilot agent PR."*
- **Target architecture:** Stream the GitHub Enterprise audit log to your SIEM (e.g., Microsoft Sentinel) and build correlation rules on `actor_is_agent == true`, `agent_session_id`, and `user`.

### Q24. Prompt & Response Payload Observability (`GET /enterprises/{enterprise}/copilot/usage-records`)
> *"Does your compliance regulator require inspecting or archiving actual prompt and response payloads sent across IDEs, Copilot CLI, and Cloud Agents?"*
- **Why ask:** The standard GitHub audit log **never** contains local client prompts or responses. However, for **EMU enterprises (GHEC and GHEC with Data Residency on `ghe.com`)**, the public-preview endpoint `GET /enterprises/{enterprise}/copilot/usage-records` streams/returns `request` and `response` JSON bodies (`github_request_id`, `event_id`, `endpoint`, `user_id`, `@timestamp`, `truncated` at 1 MB) across Cloud Agents, Copilot CLI, VS Code, Visual Studio, JetBrains, and Eclipse.
- **Red-flag answer:** *"We assumed the standard enterprise audit log records every prompt a developer types into VS Code."*
- **Target architecture:** For regulated EMU / Data Residency tenants requiring payload archiving, integrate `GET /enterprises/{enterprise}/copilot/usage-records` (or audit-log streaming of Copilot usage records) into immutable compliance storage, or use Copilot CLI hooks for non-EMU tenants.

### Q25. Public Code Matching Filter & Surface Coverage
> *"Where is your `Suggestions matching public code` policy set (`Blocked` vs. `Allowed`), and do your legal/compliance teams know which surfaces enforce it?"*
- **Why ask:** Public code matching (`Blocked` / `Allowed`) is a **Most restrictive** multi-org policy and is required (`Blocked`) for standard IP indemnity conditions, but per the *Supported surfaces* matrix it applies to **IDEs** and **annotate mode** in Cloud Agent / 3rd-party agents—not Copilot CLI, the Copilot app, or Copilot code review.
- **Red-flag answer:** *"We left one sandbox org set to `Allowed` without realizing our regulated developers aren't in it, or assumed `Suggestions matching public code` filters CLI shell outputs."*
- **Target architecture:** Enforce `Blocked` across regulated organizations (or enterprise-wide) and pair with dependency/license scanning on all PRs.

### Q26. Mandatory Human Review & Segregation of Duties on Agent PRs
> *"Can a pull request created by Copilot cloud agent (`copilot-swe-agent[bot]`) ever be merged without an independent human reviewer and passing AppSec checks?"*
- **Why ask:** Autonomous agents speed up PR creation, which increases review pressure if branch/ruleset protections are weak.
- **Red-flag answer:** *"Repo admins can bypass branch protection and merge bot PRs directly when builds are slow."*
- **Target architecture:** Enforce **Enterprise Repository Rulesets** requiring:
  1. At least 1 independent human approval (with bypasses restricted and audited in SIEM)
  2. Passing **CodeQL** (with **Copilot Autofix** suggestions reviewed before merge)
  3. **Secret Scanning Push Protection** active on all repositories
  4. **Dependency Review** blocking known vulnerable packages

### Q27. Copilot Cloud Agent Network Egress & Environment Isolation
> *"What network endpoints and secrets can the Copilot cloud agent runtime access when executing tasks on a repository?"*
- **Why ask:** Copilot cloud agent runs in an ephemeral GitHub Actions-backed environment with configurable internet firewall/allowlist rules and dedicated `copilot` environment variables/secrets.
- **Red-flag answer:** *"We gave the repository's default environment production cloud credentials without scoping them away from agent branches."*
- **Target architecture:** Keep production deployment credentials inside protected environments with required human reviewers and branch restrictions (`main` only), and keep the Copilot cloud agent firewall allowlist restricted to approved package registries and documentation hosts.

### Q28. Audit Log Retention & SIEM Streaming (180-Day Cliff)
> *"Where are your `action:copilot` and `actor:Copilot` audit events stored after 180 days?"*
- **Why ask:** GitHub's native audit log UI and API retain events for **180 days**. Regulated financial and government audits typically require 1 to 7 years of retention.
- **Red-flag answer:** *"We just query the GitHub Audit Log UI whenever internal audit asks for last year's seat and policy changes."*
- **Target architecture:** Configure **Audit Log Streaming** (to Azure Event Hubs / Microsoft Sentinel, Amazon S3, Splunk, or Datadog) before scaling seats.

### Q29. Data Residency (`ghe.com`) & Model Residency Locks
> *"Do your regulatory obligations require GitHub Enterprise Cloud with Data Residency (`ghe.com`) or FedRAMP-restricted model routing?"*
- **Why ask:** GHEC with Data Residency provides dedicated regional data storage on `ghe.com` and unlocks policies like `Restrict Copilot to data residency models` and `Restrict Copilot to FedRAMP models`—which are explicitly **exempt** from automatic override by `Default policy for new features`.
- **Red-flag answer:** *"We enabled `Default policy for new features` and worried it would overwrite our data-residency model lock."*
- **Target architecture:** Use `Restrict Copilot to data residency models` on `ghe.com` and verify model eligibility under `AI controls → Copilot`.

### Q30. Measuring Security Quality of AI-Assisted Code Over Time
> *"How do you prove to your CISO that deeper Copilot adoption (Phase 2 and Phase 3 cohorts) is decreasing—not increasing—vulnerability escape rates?"*
- **Why ask:** Security teams worry that higher PR velocity from Phase 2/3 agent cohorts will introduce more vulnerabilities or secrets.
- **Red-flag answer:** *"We track PR velocity in the Copilot dashboard, but our AppSec team tracks CodeQL alerts in a completely separate spreadsheet."*
- **Target architecture:** Join `repos-1-day` (`CCA` and `CCR` PR metrics) with GitHub Advanced Security metrics (CodeQL alert MTTR, Copilot Autofix acceptance rate, Secret Scanning Push Protection blocks) to prove governed velocity.
