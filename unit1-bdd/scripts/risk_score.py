"""Day 1 – risk-based automation strategy calculator.

Reads risk_register.csv, scores each risk (Likelihood x Impact), assigns a level,
an automation priority and the behave tags to use, then prints the strategy
sorted by score and writes risk_strategy.md.

Usage (from the repository root):   python scripts/risk_score.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "dataset" / "risk_register.csv"
OUTPUT = ROOT / "reports" / "risk_strategy.md"

LEVELS = [(15, "Critical"), (10, "High"), (6, "Medium"), (0, "Low")]


def level_for(score: int) -> str:
    return next(name for threshold, name in LEVELS if score >= threshold)


def decide(level: str, automatable: str) -> tuple[str, str]:
    """Return (decision, priority) from the risk level and whether it can be automated."""
    if automatable == "no" or level == "Low":
        return "Manual / exploratory", "-"
    priority = {"Critical": "P1", "High": "P1", "Medium": "P2"}[level]
    decision = "Automate" if automatable == "yes" else "Automate partially"
    return decision, priority


def tags_for(risk_id: str, level: str, decision: str) -> str:
    if decision.startswith("Manual"):
        return "@manual"
    tags = [f"@{risk_id}", f"@{level.lower()}", "@regression"]
    if level == "Critical":
        tags.append("@smoke")
    return " ".join(tags)


def load():
    with REGISTER.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        likelihood, impact = int(row["likelihood"]), int(row["impact"])
        if not (1 <= likelihood <= 5 and 1 <= impact <= 5):
            raise ValueError(f"{row['risk_id']}: likelihood and impact must be 1-5")
        row["score"] = likelihood * impact
        row["level"] = level_for(row["score"])
        row["decision"], row["priority"] = decide(row["level"], row["automatable"])
        row["tags"] = tags_for(row["risk_id"], row["level"], row["decision"])
    return sorted(rows, key=lambda r: (-r["score"], r["risk_id"]))


def main():
    rows = load()
    header = "| Risk | Feature | L | I | Score | Level | Decision | Priority | Tags |"
    lines = ["# Risk-based automation strategy (generated)", "", header,
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['risk_id']} | {r['feature']} | {r['likelihood']} | {r['impact']} | {r['score']} | "
                     f"{r['level']} | {r['decision']} | {r['priority']} | {r['tags']} |")
    automated = [r for r in rows if not r["decision"].startswith("Manual")]
    lines += ["", f"Automated: {len(automated)}/{len(rows)} risks; "
                  f"smoke suite covers {', '.join(r['risk_id'] for r in rows if '@smoke' in r['tags'])}."]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nWritten: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
