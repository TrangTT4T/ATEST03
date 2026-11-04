"""Build the requirement -> risk -> scenario -> result traceability matrix from tags.

Usage (from the project root):
    behave -f json.pretty -o reports/results.json      # optional: adds the Result column
    python scripts/traceability.py                       # writes reports/traceability.md and .csv
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

from behave.parser import parse_file

ROOT = Path(__file__).resolve().parent.parent
FEATURES = ROOT / "features"
RESULTS = ROOT / "reports" / "results.json"
OUT_MD = ROOT / "reports" / "traceability.md"
OUT_CSV = ROOT / "reports" / "traceability.csv"

# Requirement catalogue (same file in the Unit 2 repo) (Day 4 finding F5: one source, no drift).
_CATALOGUE = json.loads((ROOT / "shared" / "requirements.json").read_text(encoding="utf-8"))["requirements"]
REQUIREMENTS = {k: (v["title"], v["risk"], v["level"]) for k, v in _CATALOGUE.items() if v["unit"] == 1}


def load_results():
    """Map 'feature file:scenario name' -> status, from behave's JSON formatter."""
    if not RESULTS.exists():
        return {}
    statuses = defaultdict(list)
    for feature in json.loads(RESULTS.read_text(encoding="utf-8")):
        for element in feature.get("elements", []):
            if element.get("type") != "scenario":
                continue
            name = re.sub(r" -- @.*$", "", element["name"])  # merge outline rows
            statuses[(Path(feature["location"].split(":")[0]).name, name)].append(element.get("status", "untested"))
    merged = {}
    for key, values in statuses.items():
        if "failed" in values or "error" in values:
            merged[key] = "failed"
        elif all(v == "passed" for v in values):
            merged[key] = "passed"
        else:
            merged[key] = values[0]
    return merged


def collect():
    rows = []
    results = load_results()
    for path in sorted(FEATURES.glob("*.feature")):
        feature = parse_file(str(path))
        for scenario in feature.scenarios:
            tags = set(feature.tags) | set(scenario.tags)
            reqs = sorted(t for t in tags if t.startswith("REQ-")) or ["(none)"]
            risks = sorted(t for t in tags if re.fullmatch(r"R\d+", t))
            status = results.get((path.name, scenario.name), "not run")
            if "data-creating" in tags or "manual" in tags:
                status = f"{status} (excluded by default)"
            for req in reqs:
                rows.append({"req": req, "risk": ",".join(risks), "feature": path.name,
                             "scenario": scenario.name, "tags": " ".join(f"@{t}" for t in sorted(tags)),
                             "result": status})
    return rows


def main():
    rows = collect()
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    covered = {r["req"] for r in rows}
    lines = ["# Traceability matrix", "",
             "| REQ | Requirement | Risk | Level | Feature | Scenario | Result |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for req, (title, risk, level) in REQUIREMENTS.items():
        mine = [r for r in rows if r["req"] == req]
        if not mine:
            lines.append(f"| {req} | {title} | {risk} | {level} | - | **NOT COVERED** | - |")
        for r in mine:
            lines.append(f"| {req} | {title} | {risk} | {level} | {r['feature']} | {r['scenario']} | {r['result']} |")
    orphans = [r for r in rows if r["req"] not in REQUIREMENTS]
    for r in orphans:
        lines.append(f"| {r['req']} | (unknown requirement) | {r['risk']} | - | {r['feature']} | {r['scenario']} | {r['result']} |")
    coverage = len(covered & REQUIREMENTS.keys())
    lines += ["", f"Requirement coverage: {coverage}/{len(REQUIREMENTS)} "
                  f"({coverage / len(REQUIREMENTS):.0%}); scenarios without @REQ tag: {len(orphans)}."]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nWritten: {OUT_MD.relative_to(ROOT)}, {OUT_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
