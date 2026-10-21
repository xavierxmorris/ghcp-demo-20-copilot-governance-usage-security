# 30-Minute Live Demo Run-Sheet: GitHub Copilot Adoption, Governance & Security

**Total Duration:** 30:00 | **Order of Importance:**
1. **00:00–12:00 (12 min) — Priority 1: GitHub Copilot Governance & Guardrails**
2. **12:00–22:00 (10 min) — Priority 2: Usage, Reporting & Administration**
3. **22:00–30:00 (8 min)  — Priority 3: Security, Compliance & Auditability**

**Launch Command:**
```powershell
.\go.ps1 -Manual
```
*(Opens `docs\demo-console.html` and steps through each timed beat in the terminal while you drive the interactive tabs.)*

---

## Beat 1 (00:00–12:00) — Priority 1: GitHub Copilot Governance & Guardrails

### 00:00–03:00 | Enterprise AI Controls & Delegated AI Managers
- **Show in Console:** Tab **1. Governance & Guardrails** → *Enterprise AI Controls & Role Delegation*.
- **Presenter Track:**
  - Point out how GitHub Enterprise Cloud separates **AI controls** into three control planes: **Agents**, **Copilot** (Administration, Privacy, Models, Billing, Features & Clients), and **MCP**.
  - Highlight why Enterprise Owners should delegate day-to-day governance using custom roles (`Manage enterprise AI controls` and `View Enterprise Copilot Metrics`) rather than handing out full Enterprise Owner rights.
- **Ask the Room (Discovery Q9):** *"Who has permission to toggle Copilot policies today—only Enterprise Owners, or delegated AI Managers with practical AI context?"*

### 03:00–07:00 | Multi-Organization Policy Conflict Simulator (Least vs. Most Restrictive)
- **Show in Console:** Tab **1. Governance & Guardrails** → *Interactive Multi-Org & Persona Policy Simulator*.
- **Presenter Action:** Click through the 4 personas (`maya_dual_org`, `liam_payments_only`, `chloe_enterprise_direct`, `noah_contractor_multi_ent`):
  1. **`maya_dual_org` (Dual-Org: `retail-digital` + `regulated-payments`):**
     - Ask the room to **Predict**: *"If `regulated-payments` disables `Copilot CLI`, `Copilot cloud agent`, `Suggestions matching public code`, and `Copilot Metrics API`, while `retail-digital` enables all four, what does Maya actually get?"*
     - **Observe & Explain:** Maya **gets `Copilot CLI` and `Copilot cloud agent` (`Enabled`)** because productivity surfaces follow the **Least restrictive** organization! Meanwhile, **`Suggestions matching public code` (`Blocked`)** and **`Copilot Metrics API` (`Disabled`)** follow the **Most restrictive** organization (along with `Semantic indexing for non-GitHub repositories` and `Allow members without a Copilot license to use Copilot code review in GitHub.com`).
  2. **`chloe_enterprise_direct` (Direct Enterprise Seat):**
     - **Observe & Explain:** Even though Chloe is a member of `retail-digital`, her seat is assigned directly at the enterprise root. `"Let organizations decide"` **does not cover direct enterprise seats**—she falls back to **`Policies for enterprise-assigned users` (`Disabled`)**!
  3. **`noah_contractor_multi_ent` (Multi-Enterprise Seat):**
     - **Observe & Explain:** Licensed in two enterprises; **Most restrictive across enterprises** disables his CLI and Cloud Agent access until he is moved to an isolated EMU account.

### 07:00–12:00 | The 22 October 2026 Default Feature Cutover, Model Governance & Surface Gaps
- **Show in Console:** Tab **1. Governance & Guardrails** → *Default Availability & Surface Enforcement Matrix*.
- **Presenter Track:**
  - **22 October 2026 Cutover:** Show how `Default policy for new features` automatically enables `Unconfigured` GA features (`Copilot code review`, `MCP servers in Copilot`, and `Features & clients`), while explicitly exempting preview features, `Store local sessions in the Cloud`, and GHE.com data-residency/FedRAMP model locks.
  - **Model Governance:** Show why `Default availability for released models` safely enables vetted GA models (`Delegate to Default Policy`) while keeping preview models (`gemini-next-preview`), open-weight models (`DeepSeek`, `Kimi K3`), and non-retention-covered models (`Claude Fable 5`, `Claude Fable 5.1`) **disabled by default**.
  - **Surface Matrix Challenge:** Point out that `Copilot can search the web = Disabled everywhere` blocks web search in IDEs and GitHub.com Chat, **not** in Copilot cloud agent (which requires its own network/firewall allowlist) or Copilot CLI!

---

## Beat 2 (12:00–22:00) — Priority 2: Usage, Reporting & Administration

### 12:00–15:30 | Usage Metrics API (`2026-03-10`) & AI Adoption Cohorts (Phases 1–3)
- **Show in Console:** Tab **2. Usage, Reporting & Admin** → *AI Adoption Cohorts & Impact Multiplier*.
- **Presenter Track:**
  - Contrast flat DAU with the trailing 28-day **AI Adoption Cohorts** (requiring `>=2` active qualifying days):
    - **`No Cohort` (Passive):** Includes `noah_contractor_multi_ent` who had **11 chat-only days** (`chat_only_days_28d: 11`) but only 1 day of code completions/edits! Asking questions in Chat without applying edits does not qualify for Phase 1.
    - **`Phase 1: Code first`:** `chloe_enterprise_direct` (12 days of completions/IDE edits).
    - **`Phase 2: Agent first`:** `liam_payments_only` (engaged with 1 GitHub agent surface: `Copilot code review` on 4 days).
    - **`Phase 3: Multi-agent`:** `maya_dual_org` (Cloud Agent + Code Review + CLI + Copilot App) and `priya_cli_specialist` (Cloud Agent + Code Review + CLI, with **0 days of IDE completions**—proving agent usage alone qualifies a user for Phase 3!).
  - Show the **Adoption Multiplier (`4.0x` PRs merged)** and `repos-1-day` **CCA (Copilot Cloud Agent)** + **CCR (Copilot Code Review)** repository PR telemetry.

### 15:30–18:30 | Live Reconciliation Walkthrough (Why Dashboard ≠ API ≠ Org Sums)
- **Show in Console:** Tab **2. Usage, Reporting & Admin** → *Telemetry Reconciliation Inspector*.
- **Presenter Track:** Walk through four numbers that look contradictory until you know the rules:
  1. **Sum of Org DAUs (`5`) vs. Enterprise DAU (`3`):** `maya_dual_org` and `liam_payments_only` belong to two orgs each. Org metrics attribute activity by **organization membership**, not where the seat is billed (`billing-shell`).
  2. **Enterprise DAU (`3`) vs. IDE Feature Breakdown Users (`2`):** `chloe_enterprise_direct` has IDE client telemetry disabled (`ide_client_telemetry_enabled: false`). Server-side telemetry counts her in DAU, while her feature/LoC breakdowns are empty.
  3. **Copilot CLI DAU (`2`) is Separate:** `priya_cli_specialist` used only Copilot CLI today; she appears in `daily_active_cli_users`, not IDE `daily_active_users`.
  4. **CLI Customizations & `<5` Team Privacy Floor:** Show why `plugin_interactions` (`15`) is already inside `skill_interactions` (`41`) and must not be added (`41` total, `26` non-plugin skills), and why `ent:small-tiger-team` (`3` seats) is omitted from `user-teams-1-day`.

### 18:30–22:00 | Two-Rule AI Credit Budget Precedence Simulator
- **Show in Console:** Tab **2. Usage, Reporting & Admin** → *Two-Rule AI Credit Budget Simulator*.
- **Presenter Track:**
  - Explain the **Two Rules**:
    - **Rule 1 (Single Non-Additive User Budget):** `explicit_user` (`$80` for Maya) > `multi_user_cost_center` (`$50` for Power Users, `$15` for Standard Users) > `multi_user_customer` (`$10` enterprise default).
    - **Rule 2 (Independent Overlapping Controls):** Compare remaining headroom across the selected user budget and hard-stop shared budgets (`cost_center`, `enterprise`). Lowest remaining headroom blocks first; alert-only shared budgets (`AI-POWER-USERS` has `hard_stop: false`) alert at 75%/90%/100% without blocking.

---

## Beat 3 (22:00–30:00) — Priority 3: Security, Compliance & Auditability

### 22:00–25:00 | Content Exclusion & The Critical CLI / IDE Agent Mode Boundary
- **Show in Console:** Tab **3. Security, Compliance & Audit** → *Content Exclusion Surface Tester*.
- **Presenter Track:**
  - Test `/src/hsm/pin_block.c` in `aurorabank-ghec/payments-settlement-engine`:
    - **IDE Inline Completions:** `BLOCKED` by org rule `/src/hsm/**`.
    - **Copilot cloud agent:** `BLOCKED` by org rule `/src/hsm/**`.
    - **Copilot CLI local shell / IDE Agent Mode:** **`NOT SUPPORTED BY CONTENT EXCLUSION`!** Point directly to the official GitHub Docs warning: *"GitHub Copilot CLI and Agent mode in Copilot Chat in IDEs do not support content exclusion."*
  - Explain the defense-in-depth architecture: repository RBAC (split HSM code into a restricted repo), OS permissions, CLI sandbox/hooks, and Secret Scanning Push Protection.

### 25:00–27:30 | Audit Log (`action:copilot` & `actor:Copilot`) vs. EMU `usage-records`
- **Show in Console:** Tab **3. Security, Compliance & Audit** → *Audit Trail & EMU Session Observability*.
- **Presenter Track:**
  - Show standard 180-day audit log events: admin changes (`copilot.cfb_seat_assignment_created`, `copilot.content_exclusion_changed`) and agentic events (`actor:Copilot`, `actor_is_agent: true`, `agent_session_id: 012345a6-b7c8-9012-de3f-45gh678i9012`, `user: maya_dual_org`).
  - Show the public-preview EMU / GHEC Data Residency endpoint `GET /enterprises/{enterprise}/copilot/usage-records`, pairing `request` (`urec_9001`) and `response` (`urec_9002`) by `github_request_id` (`ABCD:1234:567890:FEDCBA:67150001`).

### 27:30–30:00 | Securing Agent-Authored PRs & Discovery Wrap-Up
- **Show in Console:** Tab **3. Security, Compliance & Audit** → *Agent PR Security Gates* & Tab **4. Discovery Question Bank**.
- **Presenter Track:**
  - Contrast **PR #108** (`copilot-swe-agent[bot]` delegated by `maya_dual_org`: Push Protection passed, CodeQL passed after Copilot Autofix, CCR completed, 1 independent human approval → **Merge Eligible**) with **PR #109** (CodeQL High SQLi failure + 0 human approvals → **Blocked by Ruleset**).
  - Switch to Tab **4. Discovery Question Bank** to leave the audience with the top 30 architecture questions across Governance, Usage/Reporting, and Security.
