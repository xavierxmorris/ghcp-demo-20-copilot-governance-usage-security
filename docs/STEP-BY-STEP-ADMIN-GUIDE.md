# Step-by-Step Operational Guide: All GitHub Copilot Enterprise Features

**Order of Importance: 1. Governance & Guardrails → 2. Usage, Reporting & Administration → 3. Security, Compliance & Auditability**  
**Verified Against:** GitHub Enterprise Cloud Documentation (`X-GitHub-Api-Version: 2026-03-10`, retrieved 21 October 2026)

This guide provides **click-by-click UI navigation paths** and **copy-paste `gh api` / CLI commands** for every GitHub Copilot feature covered in the 30-minute enterprise briefing.

---

## Priority 1 — GitHub Copilot Governance & Guardrails

### 1.1 Establish Delegated AI Managers (Custom Enterprise Role + Enterprise Team)
Delegate day-to-day AI governance to platform/AI SMEs without granting full Enterprise Owner access.

#### Step A: Create the Custom Role (`AI Manager`)
1. Open [https://github.com/settings/enterprises](https://github.com/settings/enterprises) and select your enterprise.
2. In the top navigation bar, click **People**.
3. In the left sidebar, click **Enterprise roles** → **Role management**.
4. Click **Create custom role**.
5. Enter a role name (e.g., `Enterprise AI Manager`) and description.
6. Under **Add permissions**, search for and select:
   - **`Manage enterprise AI controls`** *(view and manage settings in the `AI controls` tab across Agents, Copilot, and MCP)*
   - **`Read enterprise audit logs`** *(inspect `action:copilot` and `actor:Copilot` events)*
   - **`View Enterprise Copilot Metrics`** *(view Copilot Usage, Impact, and Code Generation dashboards under `Insights` and call the Usage Metrics API)*
7. Click **Create role**.
   > **Note:** By design, this custom role cannot change Copilot seat licensing or billing budgets unless granted separate billing permissions.

#### Step B: Create the Enterprise Team & Assign the Role
1. Under the **People** tab sidebar, click **Enterprise teams** → **Create Enterprise team**.
2. Name the team (e.g., `ent:ai-governance-managers`), click **Create Enterprise team**, and use **Add members** to add your AI SMEs.
3. In the **People** sidebar, click **Enterprise roles** → **Role assignments** → **Assign role**.
4. Select your `ent:ai-governance-managers` team, select `Enterprise AI Manager`, and click **Assign role**.

#### Step C: Grant Agent-Profile Ruleset Bypass to AI Managers
1. At the top of your enterprise page, click **AI controls** (`https://github.com/enterprises/ENTERPRISE/ai-controls`).
2. In the **Only enterprise admins can edit agent files** field, click **Edit ruleset**.
3. Under **Bypass list**, click **+ Add bypass** and select `ent:ai-governance-managers`.
4. Click **Save changes**.

---

### 1.2 Configure Enterprise AI Controls (Agents, Copilot, and MCP Policies)

#### Step A: Configure Agent Policies (`Copilot cloud agent`, `Copilot code review`, `Third-party agents`)
1. Navigate to your enterprise → click **AI controls** in the top bar.
2. In the left sidebar, click **Agents**.
3. Configure each policy:
   - **Copilot cloud agent** (formerly coding agent): Select **Enabled** (and choose whether to enable for **All organizations** or **Selected organizations**), **Disabled**, or **Let organizations decide**.
   - **Copilot code review**: Select **Enabled everywhere**, **Disabled everywhere**, or **Let organizations decide**.
   - **Allow members without a Copilot license to use Copilot code review in GitHub.com**: Remember this is one of the **4 Most Restrictive** multi-org policies—if delegated, any member org setting it to `Disabled` blocks it for that user across all orgs.

#### Step B: Configure Copilot Administration, Privacy & Default Availability Policies
1. In the **AI controls** left sidebar, click **Copilot**.
2. Review and set the baseline policies:
   - **`Default policy for new features` (Effective 22 October 2026):**
     - Inspect the banner at the top of the page showing how many eligible policies are currently **`Unconfigured`**.
     - Choose **Enabled everywhere**, **Disabled everywhere**, or **Let organizations decide**.
     - *Scope:* Governs all `Unconfigured` GA policies on **Features & clients**, plus **`Copilot code review`** and **`MCP servers in Copilot`**. Does **not** affect preview features, **`Store local sessions in the Cloud`**, **`Restrict Copilot to data residency models`**, or **`Restrict Copilot to FedRAMP models`**.
   - **`Policies for enterprise-assigned users`:**
     - Set to **Enabled** or **Disabled**.
     - *Critical Rule:* Users granted a Copilot seat directly at the enterprise level (not through an organization) are **not covered** by `"Let organizations decide"` and always fall back to this setting.
   - **Privacy — `Suggestions matching public code`:**
     - Set to **Blocked** (recommended for IP indemnity compliance) or **Allowed**, or **Let organizations decide** (resolved via **Most restrictive** organization).
   - **Usage — `Copilot usage metrics`:**
     - Set to **Enabled everywhere** (required to unlock the Usage Metrics REST API and Insights dashboards).

#### Step C: Configure Client & Surface Policies (`Features & clients`)
1. Under **AI controls** → **Copilot**, locate **Features & clients** and click **Configure features & clients** (`https://github.com/enterprises/ENTERPRISE/ai-controls/copilot/features`).
2. Configure each surface independently:
   - **`Copilot CLI`** *(independent from the desktop app)*
   - **`The GitHub Copilot app`** *(independent from Copilot CLI)*
   - **`Copilot in GitHub.com`** *(and optional user feedback collection toggle)*
   - **`Copilot Chat in the IDE`** and **`Copilot Agent Mode in IDE Chat`**
   - **`Copilot in GitHub Desktop`** and **`Copilot Chat in GitHub Mobile`**
   - **`Copilot can search the web`** *(applies to IDEs and Copilot Chat in GitHub.com only—does **not** control internet access for Copilot cloud agent or Copilot CLI)*
   - **`Editor preview features`** and **`Spark`**
   - **`Store local sessions in the Cloud`** *(for Copilot CLI and VS Code; exempt from `Default policy for new features`)*

#### Step D: Configure Model Context Protocol (MCP) Policies
1. Under **AI controls**, click **MCP** in the left sidebar.
2. Set **`MCP servers in Copilot`** to **Enabled everywhere**, **Disabled everywhere**, or **Let organizations decide** *(applies to IDEs, Copilot cloud agent, 3rd-party agents, Copilot CLI, the Copilot app, and Copilot code review)*.
3. Set **`Restrict MCP access to registry servers`** to **Enabled everywhere** to restrict IDEs, Copilot CLI, and the Copilot app to vetted MCP registry servers.
   > **Important:** To govern third-party hosts (Cursor, Windsurf, Claude) calling the GitHub MCP Server, configure **Organization Settings → Third-party Access → GitHub Apps / OAuth App access restrictions** and **Personal access tokens** policies.

#### Step E: Configure Repository-Level MCP Servers & `copilot-setup-steps.yml` (For Cloud Agent & Code Review)
1. On GitHub.com, open your target repository → click **Settings**.
2. In the left sidebar under **Code, planning, and automation**, click **Copilot** → **MCP servers** *(shared by both **Copilot cloud agent** and **Copilot code review**; `GitHub` and `Playwright` MCP servers are enabled by default)*.
3. Enter your `mcpServers` JSON configuration and click **Save MCP configuration**:
   ```json
   {
     "mcpServers": {
       "sentry": {
         "type": "local",
         "command": "npx",
         "args": ["@sentry/mcp-server@latest", "--host=$SENTRY_HOST"],
         "env": {
           "SENTRY_HOST": "https://contoso.sentry.io",
           "SENTRY_ACCESS_TOKEN": "$COPILOT_MCP_SENTRY_ACCESS_TOKEN"
         },
         "tools": ["get_issue", "list_events"]
       }
     }
   }
   ```
   - **Critical Rules:**
     - Allowlist specific read-only tools in `"tools"` rather than `"*"` where possible, because Copilot cloud agent invokes configured MCP tools autonomously without interactive prompts.
     - For **Copilot code review**, an MCP tool is only usable if its `tools/list` schema sets `annotations.readOnlyHint: true` (tools without `readOnlyHint: true` are automatically excluded from Code Review).
     - Any secret or variable referenced by the MCP configuration must be stored as an Agents secret/variable prefixed with **`COPILOT_MCP_`** (`Settings → Environments → copilot` or Copilot Agent settings).
4. To pre-install dependencies or authenticate (for example via Azure OIDC) before Copilot cloud agent starts, commit `.github/workflows/copilot-setup-steps.yml` bound to `environment: copilot`:
   ```yaml
   name: Copilot Setup Steps
   on: workflow_dispatch
   permissions:
     id-token: write
     contents: read
   jobs:
     copilot-setup-steps:
       runs-on: ubuntu-latest
       environment: copilot
       steps:
         - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
   ```

---

### 1.3 Configure Model Availability, Targeted Model Rules & Custom BYOK Models

#### Step A: Set Enterprise Model Baseline & Default Model Policy
1. Navigate to **Enterprise → AI controls → Copilot** → click **Configure models**.
2. Set **`Default availability for released models`** to **Enabled**, **Disabled**, or **Let organizations decide** *(unavailable if Enterprise Teams mode is active)*.
   - Models marked **`Delegate to Default Policy`** inherit this setting.
   - Pre-GA preview models (`Unconfigured`), open-weight models (**`DeepSeek`**, **`Kimi K3`**), and models outside GitHub's data-retention agreement (**`Claude Fable 5`**, **`Claude Fable 5.1`**) remain **disabled by default** unless explicitly enabled.
3. For each model in the list, set:
   - **Enabled** (enabled for all users and agent apps),
   - **Disabled** (blocked everywhere), or
   - **Delegate to Organizations** (or **Delegate to Enterprise Teams/Apps** if Enterprise Teams mode is enabled).

#### Step B: Create Targeted Organization Model Rules (Without Switching to Enterprise Teams Mode)
1. On the **Configure models** page, scroll to **Targeted model rules** and click **Create access rule**.
2. Next to **Target organizations**, click **Add organizations** and select the target orgs (e.g., `retail-digital`).
3. Under **Allowed models**, click **Add models**, select the approved models, click **Save**, then click **Create rule**.

#### Step C: Enable Enterprise Teams Mode for Model Access (Opt-In Preview)
1. First, pre-stage your teams: go to **People → Enterprise teams → `<team>` → Default models** tab, and set each delegated model from `Optional` to **Enabled**.
2. Go to **AI controls → Copilot** and toggle **Enterprise teams mode** on.
3. Remember that team model access is **additive**: if a user belongs to multiple enterprise teams, they receive every model enabled on **any** of their teams (unless disabled enterprise-wide).

#### Step D: Add Pre-Vetted Custom LLM API Keys (BYOK — Microsoft Foundry, Anthropic, AWS Bedrock, OpenAI, Google AI Studio, xAI)
1. Go to **Enterprise → AI controls → Copilot** → click **Configure custom models**.
2. Click **Add API key**.
3. Select the **Provider** (e.g., `Microsoft Foundry`, `Anthropic`, `AWS Bedrock`, `OpenAI`, `Google AI Studio`, `xAI`, or `OpenAI-compatible`).
4. Enter a display **Name** and paste the least-privilege **API key**:
   - For **OpenAI, Anthropic, or xAI**: click the **Fetch new models** sync icon inside the API key field, then check the models under **Available models**.
   - For **Microsoft Foundry**: enter the **Deployment URL**, type the **Model ID** under **Available models**, and click the checkmark (`✓`) to add it *(use one API key entry per unique Deployment URL)*.
5. Click **Save**.
6. Click the **Added models** tab → click **Configure** (or **All/X organizations**) next to the model → ensure the model is **Enabled** → open the **Access** tab → choose **Allow for all organizations** or **Choose per organization** → click **Save**.

---

### 1.4 Layer Repository Instructions & Guardrails (`AGENTS.md`, `.github/copilot-instructions.md`, Rulesets)

1. **Personal CLI Defaults:** Create `~/.copilot/copilot-instructions.md` for personal terminal preferences.
2. **Repository-Wide Instructions:** Create `.github/copilot-instructions.md` at the repository root for build, test, and coding conventions.
3. **Agent Contract:** Create `AGENTS.md` at the repository root (and optional nested `AGENTS.md` files in subprojects) defining allowed paths, required verification commands, and non-goals.
4. **Path-Scoped Instructions:** Create `.github/instructions/<topic>.instructions.md` with YAML frontmatter:
   ```markdown
   ---
   applyTo: "src/payments/**"
   ---
   Require Decimal arithmetic, strict idempotency keys, and zero raw PAN logging.
   ```
5. **Verify Loaded Instructions in Copilot CLI:** Run `/instructions` or `/env` inside an interactive Copilot CLI session.

---

## Priority 2 — Usage, Reporting & Administration

### 2.1 View the Three Enterprise Dashboards (Usage, Impact, and Code Generation)
**Prerequisite:** `Copilot usage metrics` policy must be **Enabled**; caller must be Enterprise Owner, Billing Manager, or hold `View Enterprise Copilot Metrics`.

1. **Copilot Usage Dashboard (28-Day Adoption, Languages, Models & Chat Modes):**
   - Navigate to **Enterprise → Insights → Copilot usage** (`https://github.com/enterprises/ENTERPRISE/insights/copilot-usage`).
   - Review Daily/Weekly/Total Active Users, Code completion acceptance rate, Requests per chat mode (`Ask`, `Edit`, `Plan`, `Agent`), and Model usage per chat mode. *(Note: Excludes Copilot CLI usage.)*
2. **Copilot Impact Dashboard (28-Day AI Adoption Cohorts & PR Throughput):**
   - Navigate to **Enterprise → Insights → Copilot impact**.
   - Inspect **Adoption cohort distribution** (`Passive users`, `Phase 1: Code first`, `Phase 2: Agent first`, `Phase 3: Multi-agent`), **Feature engagement** (`>=2` active days in 28d), **Adoption multiplier** (PRs merged/month & time to merge vs. Passive users), **Recommendations** cards, and the directional **Potential return on investment** estimator.
3. **Code Generation Dashboard (User-Initiated vs. Agent-Initiated LoC):**
   - Navigate to **Enterprise → Insights → Code generation**.
   - Compare **Lines of code changed with AI**, **Agent contribution %**, **User-initiated code changes**, and **Agent-initiated code changes** by model and language.

---

### 2.2 Download & Automate NDJSON Reports via the Copilot Usage Metrics REST API (`2026-03-10`)
**Required Token Scopes / Permissions:** Fine-grained `"View Enterprise Copilot Metrics"` / `"View Organization Copilot Metrics"`, or classic PAT / OAuth token with `manage_billing:copilot` or `read:enterprise` (or `read:org` for org endpoints).

#### Step A: Enterprise 1-Day & 28-Day Aggregated Reports
```powershell
# 1. Get signed download URLs for the latest 28-day enterprise report
gh api `
  -H "Accept: application/vnd.github+json" `
  -H "X-GitHub-Api-Version: 2026-03-10" `
  "/enterprises/ENTERPRISE/copilot/metrics/reports/enterprise-28-day/latest"

# 2. Get signed download URLs for a finalized 1-day enterprise report (wait 2-3 UTC days for finalization)
gh api `
  -H "Accept: application/vnd.github+json" `
  -H "X-GitHub-Api-Version: 2026-03-10" `
  "/enterprises/ENTERPRISE/copilot/metrics/reports/enterprise-1-day?day=2026-10-18"
```

#### Step B: Per-User 1-Day & 28-Day Reports (Includes `ai_credits_used`, `ai_adoption_phase`, and CLI Customizations)
```powershell
# Download the latest 28-day per-user NDJSON report
$resp = gh api `
  -H "Accept: application/vnd.github+json" `
  -H "X-GitHub-Api-Version: 2026-03-10" `
  "/enterprises/ENTERPRISE/copilot/metrics/reports/users-28-day/latest" | ConvertFrom-Json

Invoke-WebRequest -Uri $resp.download_links[0] -OutFile "users-28-day.ndjson"
```
Each NDJSON line contains:
- `user_id`, `user_login`, **`ai_credits_used`**
- `user_initiated_interaction_count`, `code_generation_activity_count`, `code_acceptance_activity_count`
- `loc_suggested_to_add_sum`, `loc_added_sum`, `loc_deleted_sum`
- `used_agent`, `used_chat`, `used_cli`, `used_copilot_app`, `used_copilot_cloud_agent`, `used_copilot_code_review_active`, `used_copilot_code_review_passive`, `used_vscode_agent`
- **`ai_adoption_phase`** (`No Cohort`, `Phase 1`, `Phase 2`, `Phase 3`)
- **CLI customization telemetry (API-only):** `distinct_skill_use_count`, `distinct_custom_agent_use_count`, `distinct_mcp_use_count`, `distinct_slash_cmd_use_count`, `distinct_plugin_use_count`, and top-5 arrays `totals_by_skill`, `totals_by_custom_agent`, `totals_by_mcp`, `totals_by_slash_cmd`, `totals_by_plugin`.
  > **Rule:** Never add `plugin` and `skill` interaction counts together—every plugin interaction is already counted in `totals_by_skill`.

#### Step C: Repository-Level PR Lifecycle Report (`repos-1-day` — CCA & CCR Breakdowns)
```powershell
# Per-repository PR creation, merge, and stage duration for Copilot Cloud Agent (CCA) and Code Review (CCR)
gh api `
  -H "Accept: application/vnd.github+json" `
  -H "X-GitHub-Api-Version: 2026-03-10" `
  "/enterprises/ENTERPRISE/copilot/metrics/reports/repos-1-day?day=2026-10-18"
```
*(Returns HTTP `200` with `download_links` or HTTP `204 No Content` if no repositories had PR activity on that day.)*

#### Step D: Construct Team-Level Metrics (`user-teams-1-day` Joined with `users-1-day`)
```powershell
# Retrieve user-to-team mappings (teams with <5 seated Copilot users on that day are excluded)
gh api `
  -H "Accept: application/vnd.github+json" `
  -H "X-GitHub-Api-Version: 2026-03-10" `
  "/enterprises/ENTERPRISE/copilot/metrics/reports/user-teams-1-day?day=2026-10-18"
```
Join `user-teams-1-day` with `users-1-day` on `user_id` + `day` in your BI pipeline (or run `python -m copilot_governance` in this repo to see the reconciliation logic).

---

### 2.3 Administer Copilot Seats via the User Management REST API (`2026-03-10`)
The Usage Metrics API only reports telemetry; the **Copilot User Management API** is the source of truth for assigned seats and `last_activity_at`.

```powershell
# 1. List all billed Copilot seats across the enterprise (deduplicated total_seats + per-org/team seat array)
gh api `
  -H "Accept: application/vnd.github+json" `
  -H "X-GitHub-Api-Version: 2026-03-10" `
  "/enterprises/ENTERPRISE/copilot/billing/seats?per_page=100"

# 2. Assign Copilot seats to enterprise teams (requires manage_billing:copilot or admin:enterprise)
gh api --method POST `
  -H "Accept: application/vnd.github+json" `
  -H "X-GitHub-Api-Version: 2026-03-10" `
  "/enterprises/ENTERPRISE/copilot/billing/selected_enterprise_teams" `
  -f "selected_enterprise_teams[]=ent:platform-architecture"

# 3. Remove enterprise teams from Copilot subscription (sets seats to pending cancellation at cycle end)
gh api --method DELETE `
  -H "Accept: application/vnd.github+json" `
  -H "X-GitHub-Api-Version: 2026-03-10" `
  "/enterprises/ENTERPRISE/copilot/billing/selected_enterprise_teams" `
  -f "selected_enterprise_teams[]=ent:legacy-pilot"
```

---

### 2.4 Configure Cost Centres & Two-Rule AI Credit Budgets

1. **Create Cost Centres & Map Cohorts:**
   - Navigate to **Enterprise → Billing and licensing → Cost centers**.
   - Create distinct cost centres for each persona tier (e.g., `AI-POWER-USERS` and `AI-STANDARD-USERS`) and assign the corresponding Enterprise Teams or Organizations (never put the same user in two competing user-budget cohorts).
2. **Configure User-Level Budgets (Rule 1 — Non-Additive Selection):**
   - Navigate to **Enterprise → Billing and licensing → Budgets and alerts**.
   - Configure:
     - **Enterprise universal per-user default (`multi_user_customer`):** Baseline hard cap for standard users.
     - **Cost-centre per-user budget (`multi_user_cost_center`):** Higher per-user cap for `AI-POWER-USERS` (overrides `multi_user_customer`; never adds to it).
     - **Explicit user override (`user`):** Optional exception cap for specific principal engineers (overrides both `multi_user_cost_center` and `multi_user_customer`).
3. **Configure Independent Shared Spending Budgets (Rule 2 — Lowest Hard-Stop Headroom Wins):**
   - Create a **shared cost-centre budget (`cost_center`)** for `AI-POWER-USERS` with **alerts at 75%, 90%, and 100%** and `Stop usage when budget limit is reached` **unchecked** (`hard_stop = false`) for visibility, or **checked** (`hard_stop = true`) for a hard shared ceiling.
   - Verify **AI credit paid usage** policy under **AI controls → Copilot** aligns with whether overages beyond the included enterprise pool are permitted.

---

## Priority 3 — Security, Compliance & Auditability

### 3.1 Configure Content Exclusion (Repository & Organization Scopes)

#### Step A: Configure Repository-Level Content Exclusion
1. Navigate to the repository on GitHub.com → click **Settings**.
2. In the left sidebar, under **Code, planning, and automation**, click **Copilot** → **Content exclusion**.
3. Inspect any **read-only gray boxes** at the top showing exclusions inherited from the parent organization or enterprise.
4. In **Paths to exclude in this repository**, enter case-insensitive `fnmatch` patterns (one per line, prefixed with `- `):
   ```yaml
   # Exclude specific sensitive file
   - "/src/hsm/pin_block.c"

   # Exclude all files named secrets.json anywhere in the repo
   - "secrets.json"

   # Exclude an entire directory tree
   - "/config/swift-routing/**"
   ```
5. Click **Save changes** *(propagates to IDEs within ~30 minutes)*.

#### Step B: Configure Organization-Wide & Wildcard (`"*":`) Content Exclusion
1. Navigate to your Organization → click **Settings** → in the left sidebar, click **Copilot** → **Content exclusion**.
2. In **Repositories and paths to exclude**, define global filesystem rules (`"*":`) and protocol-independent repository rules:
   ```yaml
   # Exclude .env and private key files across ALL repos and non-Git local folders
   "*":
     - "**/*.pem"
     - "**/*.key"
     - ".env*"

   # Exclude HSM and routing configs in a specific repository (matches HTTPS, SSH, or git:// clones)
   https://github.com/aurorabank-ghec/payments-settlement-engine.git:
     - "/src/hsm/**"
     - "/config/swift-routing/*.cfg"
   ```
3. Click **Save changes**.

#### Step C: Enforce Compensating Controls for Copilot CLI & IDE Agent Mode
> **Official GitHub Docs Limitation:** *"GitHub Copilot CLI and Agent mode in Copilot Chat in IDEs do not support content exclusion."*
- **Action 1:** Move crown-jewel secrets, HSM modules, and production key material into dedicated repositories with strict **Repository RBAC** so unauthorized developers cannot clone them locally.
- **Action 2:** Enable **Secret Scanning Push Protection** across all repositories (`Enterprise → Settings → Code security → Secret scanning`).
- **Action 3:** Use Copilot CLI `/sandbox` and `/permissions` controls to restrict file-path and network access during local terminal sessions.

---

### 3.2 Review Audit Logs (`action:copilot` & `actor:Copilot`) & Stream to SIEM

#### Step A: Search Control-Plane & Agentic Events in the Audit Log UI
1. Navigate to **Enterprise → Settings → Audit log**.
2. Run targeted queries:
   - **All Copilot admin, policy, content-exclusion & seat events:**
     ```text
     action:copilot
     ```
   - **Specific seat assignment events:**
     ```text
     action:copilot.cfb_seat_assignment_created
     ```
   - **All autonomous agent actions on GitHub.com (PR creation, commits, comments):**
     ```text
     actor:Copilot
     ```
3. Inspect agentic event fields in the JSON payload:
   - `actor_is_agent`: `true`
   - `agent_session_id`: UUID linking all events from that specific agent run (e.g., `012345a6-b7c8-9012-de3f-45gh678i9012`)
   - `user`: login of the human who initiated the agent task

#### Step B: Stream Audit Logs Beyond the 180-Day Native Retention Cliff
1. Navigate to **Enterprise → Settings → Audit log → Log streaming**.
2. Click **Configure stream** and select one or more destinations *(multiple simultaneous streams are supported in public preview)*:
   - **Azure Event Hubs** *(for Microsoft Sentinel SIEM correlation)* or **Azure Blob Storage**
   - **Microsoft Purview** *(specifically for streaming Copilot agent session events into Purview compliance archives)*
   - **Amazon S3** *(supports keyless OpenID Connect via provider URL `https://oidc-configuration.audit-log.githubusercontent.com`, audience `sts.amazonaws.com`, and subject `https://github.com/ENTERPRISE`)*
   - **Splunk**, **Datadog**, or **Google Cloud Storage**
3. Click **Check endpoint** to verify write connectivity, then click **Save**.
   > **Operational Note:** Streamed logs arrive as `YYYY/MM/DD/HH/MM/<uuid>.json.log.gz` with at-least-once delivery. Paused streams buffer events for up to **7 days**, and automated health checks run every **24 hours** (misconfigured streams must be repaired within 6 days to prevent dropped events).

---

### 3.3 Query EMU Session Payload Observability (`GET /enterprises/{enterprise}/copilot/usage-records`)
**Scope:** Public preview for **Enterprise Managed Users (EMU)** on GHEC and GHEC with Data Residency (`ghe.com`). Requires an **Enterprise Owner** using an OAuth token or classic PAT with `read:enterprise` scope.

```powershell
# Retrieve recent Copilot session request/response payloads across Cloud Agents, CLI, VS Code, Visual Studio, JetBrains & Eclipse
gh api `
  -H "Accept: application/vnd.github+json" `
  -H "X-GitHub-Api-Version: 2026-03-10" `
  "/enterprises/ENTERPRISE/copilot/usage-records?per_page=25&order=desc"

# Filter by request/response type, user_id, or created timestamp
gh api `
  -H "Accept: application/vnd.github+json" `
  -H "X-GitHub-Api-Version: 2026-03-10" `
  "/enterprises/ENTERPRISE/copilot/usage-records?phrase=type:request+user_id:1001&per_page=25"
```
Each returned object includes `type` (`request` or `response`), `user_id`, `enterprise_id`, `github_request_id`, `endpoint`, `body` (JSON-encoded payload up to 1 MB), `truncated` (boolean), `@timestamp`, and `event_id`.

---

### 3.4 Enforce Repository Rulesets, CodeQL Autofix & Human Review on Agent PRs

1. **Create an Enterprise or Organization Repository Ruleset:**
   - Navigate to **Organization (or Enterprise) → Settings → Repository → Rulesets → New ruleset → New branch ruleset**.
   - Target the **Default branch** across all repositories (or filter by repository custom properties such as `system_criticality: high`).
2. **Enable Required Guardrails:**
   - Check **Require a pull request before merging**:
     - Set **Required approvals** to `>= 1`.
     - Check **Dismiss stale pull request approvals when new commits are pushed**.
     - Check **Require review from Code Owners**.
     - Optionally enable automatic **Copilot code review** on new pull requests *(note: Copilot code review provides diagnostic comments, never an approving review that satisfies required human approvals)*.
   - Check **Require status checks to pass before merging** and add:
     - `CodeQL` (with **Copilot Autofix** enabled under **Settings → Code security → Code scanning**)
     - `Dependency Review`
   - Ensure **Secret scanning push protection** is enabled under **Settings → Code security**.
