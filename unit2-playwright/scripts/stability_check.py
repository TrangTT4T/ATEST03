"""Day 8 – static stability and maintainability check for the Playwright suite.

Extends the Unit 1 review (scripts/bdd_review.py checks the feature files and step definitions) with
Playwright-specific rules:
  1. no fixed waits: page.wait_for_timeout(), time.sleep()
  2. no force=True clicks (they hide real actionability problems)
  3. no positional selectors in tests/steps: :nth-child, nth=, .nth(), xpath [index]
  4. no raw CSS/XPath in tests or step definitions: locators belong in pages/
  5. every plain test (not Gherkin) carries req(...) and risk(...) markers for traceability

Usage (from the repository root):  python scripts/stability_check.py
Exit code 1 when anything is found, so it can gate CI.
"""
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = [
    (re.compile(r"wait_for_timeout\("), "fixed wait: use expect() or wait_for_url/response instead"),
    (re.compile(r"\btime\.sleep\("), "time.sleep in test code"),
    (re.compile(r"force\s*=\s*True"), "force=True hides actionability problems"),
]
TEST_ONLY_RULES = [
    (re.compile(r":nth-child|nth=|\.nth\(|\)\[\d+\]"), "positional selector: brittle when the layout changes"),
    (re.compile(r"""\.locator\(\s*['"](?:css=|xpath=|//|\.|#)"""), "raw CSS/XPath in a test: move it to pages/"),
]


def code_lines(path: Path):
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        code = line.split("#", 1)[0]
        if code.strip():
            yield lineno, code


def missing_trace_markers(path: Path):
    """Plain test functions must have req() and risk() via pytestmark or decorators."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    module_marks = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "pytestmark" for t in node.targets):
            module_marks |= {m for m in ("req", "risk") if f"mark.{m}(" in ast.unparse(node.value)}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            marks = set(module_marks)
            for dec in node.decorator_list:
                marks |= {m for m in ("req", "risk") if f"mark.{m}(" in ast.unparse(dec)}
            for m in sorted({"req", "risk"} - marks):
                yield node.lineno, f"{node.name}: missing pytest.mark.{m}(...)"


def main():
    findings = []
    for folder in ("tests", "pages"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            rel = path.relative_to(ROOT)
            rules = RULES + (TEST_ONLY_RULES if folder == "tests" else [])
            for lineno, code in code_lines(path):
                for rx, msg in rules:
                    if rx.search(code):
                        findings.append(f"{rel}:{lineno}: {msg}")
            if folder == "tests" and path.name.startswith("test_") and path.name != "test_bdd_features.py":
                findings += [f"{rel}:{ln}: {msg}" for ln, msg in missing_trace_markers(path)]
    if findings:
        print("Stability check findings:")
        print("\n".join(f"- {f}" for f in findings))
        sys.exit(1)
    print("Stability check: no findings (no fixed waits, no force clicks, no positional or raw selectors in tests).")


if __name__ == "__main__":
    main()
