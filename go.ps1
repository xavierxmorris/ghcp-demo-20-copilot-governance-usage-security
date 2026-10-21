<#
.SYNOPSIS
    30-minute enterprise demo: GitHub Copilot Adoption, Governance & Security.

.DESCRIPTION
    Walks through the three pillars in strict order of importance:
      1. GitHub Copilot Governance & Guardrails (12 mins)
      2. Usage, Reporting & Administration      (10 mins)
      3. Security, Compliance & Auditability    (8 mins)

    Offline by default: uses Python 3.11+ standard library and opens the
    self-contained HTML console (docs\demo-console.html).

.PARAMETER Check
    Run unit tests and repository contract validation, then exit.

.PARAMETER Manual
    Advance each presenter beat with Enter instead of a timer.

.PARAMETER NoBrowser
    Run the deterministic evaluation and print presenter beats without opening a browser.

.PARAMETER Live
    Perform an optional read-only check against GitHub's enterprise 28-day usage
    metrics endpoint via 'gh api'. Requires -EnterpriseSlug. Never mutates state.

.PARAMETER EnterpriseSlug
    Enterprise slug for optional read-only -Live mode.
#>
[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$Manual,
    [switch]$NoBrowser,
    [switch]$Live,
    [string]$EnterpriseSlug
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
Push-Location $root

function Write-Rule([string]$Title = '') {
    if ($Title) {
        $pad = [Math]::Max(0, 74 - $Title.Length - 4)
        Write-Host ""
        Write-Host ("-- $Title " + ('-' * $pad)) -ForegroundColor DarkGray
    } else {
        Write-Host ('-' * 74) -ForegroundColor DarkGray
    }
}

function Write-Beat([string]$Clock, [string]$Title) {
    Write-Host ""
    Write-Host "  $Clock  " -ForegroundColor DarkGray -NoNewline
    Write-Host $Title -ForegroundColor White
}

function Write-Say([string]$Text) {
    Write-Host '        " ' -ForegroundColor DarkGray -NoNewline
    Write-Host $Text -ForegroundColor Cyan
}

function Write-Note([string]$Text) {
    Write-Host "        $Text" -ForegroundColor DarkGray
}

function Wait-Beat([int]$Seconds) {
    if ($Manual) {
        Write-Host ""
        Write-Host "        [Enter] to advance to next beat " -ForegroundColor DarkGray -NoNewline
        try {
            [void](Read-Host)
            return
        } catch {
            Write-Host ""
        }
    }
    for ($i = $Seconds; $i -gt 0; $i--) {
        Write-Host ("`r        next beat in {0,2}s " -f $i) -ForegroundColor DarkGray -NoNewline
        Start-Sleep -Seconds 1
    }
    Write-Host "`r                             `r" -NoNewline
}

try {
    & python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 2)"
    if ($LASTEXITCODE -ne 0) { throw "Python 3.11+ is required." }

    if ($Check) {
        Write-Rule "Preflight & Unit Tests"
        & python -m unittest discover -s tests -v
        if ($LASTEXITCODE -ne 0) { throw "Unit tests failed." }
        & python (Join-Path $root 'scripts' 'check_repo.py')
        if ($LASTEXITCODE -ne 0) { throw "Repository contract check failed." }
        Write-Host ""
        Write-Host "  READY - All tests and 3-pillar priority contracts verified." -ForegroundColor Green
        exit 0
    }

    if ($Live) {
        if (-not $EnterpriseSlug) {
            throw "Pass -EnterpriseSlug <slug> when using -Live read-only inspection."
        }
        Write-Rule "Read-Only Live Enterprise Metrics Check"
        & python -m copilot_governance --live-enterprise $EnterpriseSlug
        exit $LASTEXITCODE
    }

    Write-Rule "Generating Deterministic Evaluation Bundle"
    $outLatest = Join-Path (Join-Path $root 'out') 'latest'
    & python -m copilot_governance --out $outLatest | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Evaluation run failed." }

    $consolePath = Join-Path (Join-Path $root 'docs') 'demo-console.html'
    if (-not $NoBrowser) {
        Start-Process $consolePath | Out-Null
        Write-Note "Opened interactive console: docs\demo-console.html"
    } else {
        Write-Note "NoBrowser set: skipping browser launch (console at docs\demo-console.html)"
    }

    Write-Rule "30-Minute Demo Beats (Priority Order 1 -> 2 -> 3)"

    Write-Beat "00:00 - 12:00" "PRIORITY 1: GITHUB COPILOT GOVERNANCE & GUARDRAILS"
    Write-Say "In an enterprise, 'Let organizations decide' uses LEAST RESTRICTIVE for standard surfaces (CLI, Cloud Agent, App, MCP), and MOST RESTRICTIVE only for 4 sensitive policies."
    Write-Say "Starting 22 October 2026, 'Default policy for new features' auto-enables Unconfigured GA features, while preview, open-weight (DeepSeek/Kimi K3), and non-retention models (Claude Fable 5) stay disabled by default."
    Write-Note "Console Tab 1: Click through maya_dual_org, chloe_enterprise_direct, and noah_contractor_multi_ent."
    Wait-Beat 5

    Write-Beat "12:00 - 22:00" "PRIORITY 2: USAGE, REPORTING & ADMINISTRATION"
    Write-Say "Flat DAU hides adoption depth. The Impact Dashboard tracks 28-day cohorts (Passive/No Cohort, Phase 1 Code-first, Phase 2 Agent-first, Phase 3 Multi-agent) and connects them to PR velocity via repos-1-day (CCA & CCR)."
    Write-Say "Remember the two reconciliation & budget rules: Org metrics attribute by org membership (not billing shell), and AI Credit budgets pick ONE non-additive user tier before checking lowest hard-stop headroom."
    Write-Note "Console Tab 2: Inspect the 3 vs 5 DAU reconciliation, CLI skill/plugin overlap, and Two-Rule budget table."
    Wait-Beat 5

    Write-Beat "22:00 - 30:00" "PRIORITY 3: SECURITY, COMPLIANCE & AUDITABILITY"
    Write-Say "Content exclusion blocks inline completions and Cloud Agent on /src/hsm/**, but GitHub Docs explicitly warns that Copilot CLI and IDE Agent Mode do not support content exclusion."
    Write-Say "Pair repo RBAC, Rulesets, Secret Scanning Push Protection, and CodeQL Autofix with 180-day actor:Copilot (agent_session_id) audit logs and EMU /copilot/usage-records session observability."
    Write-Note "Console Tab 3 & Tab 4: Review content-exclusion probes, PR #108 vs #109 gates, and the 30 discovery questions."
    Wait-Beat 3

    Write-Rule "Completed"
    Write-Host "  Reports written to: out\latest\evaluation-report.json and out\latest\evaluation-report.md" -ForegroundColor Green
} finally {
    Pop-Location
}
