# Agent contract

This repository is a runnable 30-minute enterprise demo, deterministic policy/metrics/security evaluator, and technical discovery toolkit for **GitHub Copilot Adoption, Governance, and Security**.

- Maintain strict priority ordering in every artifact:
  1. **Governance & Guardrails** (Enterprise AI controls, multi-org/multi-enterprise policy resolution, Oct 22 2026 default feature availability, model delegation exclusions, surface gaps, and instruction/agent guardrails)
  2. **Usage, Reporting & Administration** (Usage Metrics API `2026-03-10` NDJSON reports, CLI customization telemetry, Impact Dashboard AI adoption cohorts Phase 1–3, reconciliation traps, and two-rule AI Credit budget precedence)
  3. **Security, Compliance & Auditability** (Content exclusion & CLI/IDE Agent mode boundaries, 180-day audit log `action:copilot` & `actor:Copilot` with `agent_session_id`, EMU `usage-records` session observability, IP indemnity/public-code filter, and CodeQL/Autofix/Push Protection PR gates)
- Keep examples synthetic (`aurorabank-ghec`). Never commit customer data, tokens, or real user mappings.
- Run both validation gates before completing any change:
  - `python -m unittest discover -s tests -v`
  - `python scripts/check_repo.py`
- Never add mutating API calls (`POST`, `PUT`, `PATCH`, `DELETE`) to the optional `-Live` mode.
