"""Repository contract checker for ghcp-demo-20-copilot-governance-usage-security."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from copilot_governance.evaluator import evaluate_all

REQUIRED_FILES = (
    "README.md",
    "RUN-SHEET.md",
    "PROMPTS.md",
    "WORKSHOP.md",
    "go.ps1",
    ".github/copilot-instructions.md",
    "AGENTS.md",
    "fixtures/enterprise-scenario.json",
    "docs/DEEP-RESEARCH-BRIEF.md",
    "docs/DISCOVERY-QUESTIONS.md",
    "docs/demo-console.html",
    "iteration/2026-10-21-verification-log.md",
    ".github/workflows/ci.yml",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    missing = [rel for rel in REQUIRED_FILES if not (root / rel).is_file()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")

    readme = (root / "README.md").read_text(encoding="utf-8")
    if "## Honesty notes" not in readme:
        raise SystemExit("README.md must include an '## Honesty notes' section.")

    result = evaluate_all()
    pillars = [p["pillar"] for p in result["pillars_in_priority_order"]]
    expected = [
        "GitHub Copilot Governance & Guardrails",
        "Usage, Reporting & Administration",
        "Security, Compliance & Auditability",
    ]
    if pillars != expected:
        raise SystemExit(f"Pillar order mismatch: {pillars} != {expected}")

    print(f"Verified {len(REQUIRED_FILES)} repository artifacts and 3-pillar priority contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
