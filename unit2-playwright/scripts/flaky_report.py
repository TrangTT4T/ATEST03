"""Day 8 – flaky-test detection from repeated runs.

Reads every JUnit XML in reports/runs/ (one file per run, written by `python run.py stability`),
counts pass/fail per test and classifies it:
  stable-pass  passed in every run
  stable-fail  failed in every run   -> real defect or broken test: analyse the trace
  flaky        passed in some runs and failed in others -> quarantine + root-cause
Writes reports/flaky_report.md.
"""
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "reports" / "runs"
OUT = ROOT / "reports" / "flaky_report.md"


def outcomes():
    results = defaultdict(list)
    files = sorted(RUNS.glob("*.xml"))
    for xml in files:
        for case in ET.parse(xml).iter("testcase"):
            name = f"{case.get('classname')}::{case.get('name')}"
            if case.find("skipped") is not None:
                continue
            failed = case.find("failure") is not None or case.find("error") is not None
            results[name].append("failed" if failed else "passed")
    return files, results


def main():
    files, results = outcomes()
    if not files:
        sys.exit("No runs found in reports/runs/ - run: python run.py stability --runs 3")
    rows, flaky, broken = [], 0, 0
    for name, runs in sorted(results.items()):
        passes = runs.count("passed")
        if passes == len(runs):
            status = "stable-pass"
        elif passes == 0:
            status, broken = "stable-fail", broken + 1
        else:
            status, flaky = "flaky", flaky + 1
        rows.append(f"| `{name}` | {passes}/{len(runs)} | {status} |")
    total = len(results)
    lines = ["# Flaky-test report", "",
             f"Runs analysed: {len(files)} · tests: {total} · flaky: {flaky} ({flaky / total:.0%}) · "
             f"always failing: {broken}", "", "| Test | Passed | Status |", "| --- | --- | --- |", *rows]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:3]))
    print(f"Written: {OUT.relative_to(ROOT)}")
    sys.exit(1 if flaky or broken else 0)


if __name__ == "__main__":
    main()
