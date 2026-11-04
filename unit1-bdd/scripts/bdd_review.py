"""Day 4 – automated BDD framework review (works for behave and pytest-bdd step definitions).

Checks a behave project against the review rubric and prints findings:
  1. Gherkin is declarative (no URLs, CSS/XPath, clicks or waits in feature files)
  2. Scenario size (> 7 steps is flagged)
  3. Traceability tags (@REQ-xx and @Rxx on every scenario)
  4. Step reuse: unused step definitions and near-duplicate step texts
  5. Stability: time.sleep in steps/pages
  6. Hard-coded test data (prices) inside step code

Usage (from the repository root):  python scripts/bdd_review.py .
"""
import difflib
import re
import sys
from pathlib import Path

from behave.parser import parse_file
from parse import compile as parse_compile

IMPERATIVE = re.compile(r"https?://|#[\w-]+|\.[\w-]+\s*>|//\w+\[|\bclick\b|\bwait\b|\bseconds?\b|\bxpath\b|\bcss\b", re.I)
# behave: @given("...")   pytest-bdd: @given("..."), @given(parsers.parse("...")), @then(parsers.re(r"..."))
STEP_DEF = re.compile(r"""@(given|when|then|step)\(\s*(?:parsers\.(parse|re)\(\s*)?[ur]?(['"])(.+?)\3""")
MATCHER = re.compile(r"""use_step_matcher\(\s*['"](\w+)['"]""")


class RegexMatcher:
    """Same interface as parse's compiled pattern: .parse(text) -> match or None."""

    def __init__(self, pattern):
        self.rx = re.compile(pattern)

    def parse(self, text):
        return self.rx.fullmatch(text)


def features_dir(root: Path) -> Path:
    """Unit 1 keeps feature files in tests/features; Unit 2 in features/."""
    for candidate in (root / "tests" / "features", root / "features"):
        if candidate.is_dir():
            return candidate
    raise SystemExit(f"No feature files found under {root}")


def load_features(root: Path):
    return [parse_file(str(p)) for p in sorted(features_dir(root).glob("*.feature"))]


def steps_dir(root: Path) -> Path:
    """Unit 1 (behave) keeps steps in tests/steps; Unit 2 (pytest-bdd) in tests/step_defs."""
    for candidate in (root / "tests" / "steps", root / "features" / "steps", root / "tests" / "step_defs"):
        if candidate.is_dir():
            return candidate
    raise SystemExit(f"No step definitions found under {root}")


def load_step_patterns(root: Path):
    patterns = []
    for path in sorted(steps_dir(root).glob("*.py")):
        matcher = "parse"
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            switch = MATCHER.search(line)
            if switch:
                matcher = switch.group(1)
                continue
            m = STEP_DEF.search(line)
            if m:
                text = m.group(4)
                is_regex = m.group(2) == "re" or (m.group(2) is None and matcher == "re")
                compiled = RegexMatcher(text) if is_regex else parse_compile(text)
                patterns.append({"kind": m.group(1), "text": text, "file": path.name, "line": lineno,
                                 "matcher": compiled, "used": 0})
    return patterns


def review(root: Path):
    findings = []
    features = load_features(root)
    patterns = load_step_patterns(root)

    for feature in features:
        for scenario in feature.scenarios:
            where = f"{Path(feature.filename).name}:{scenario.line} '{scenario.name}'"
            tags = set(feature.tags) | set(scenario.tags)
            if not any(t.startswith("REQ-") for t in tags):
                findings.append(("Traceability", where, "missing @REQ-xx tag"))
            if not any(re.fullmatch(r"R\d+", t) for t in tags):
                findings.append(("Traceability", where, "missing @Rxx risk tag"))
            steps = list(feature.background.steps if feature.background else []) + list(scenario.steps)
            if len(scenario.steps) > 7:
                findings.append(("Scenario size", where, f"{len(scenario.steps)} steps (> 7)"))
            for step in steps:
                if IMPERATIVE.search(step.name):
                    findings.append(("Declarative Gherkin", where, f"imperative/UI detail: '{step.name}'"))
                hits = [p for p in patterns if p["matcher"].parse(step.name) is not None]
                for p in hits:
                    p["used"] += 1
                if len(hits) > 1:
                    findings.append(("Step reuse", where, f"ambiguous step '{step.name}'"))

    for p in patterns:
        if p["used"] == 0:
            findings.append(("Step reuse", f"{p['file']}:{p['line']}", f"unused step '{p['text']}'"))
    texts = [p["text"] for p in patterns]
    for i, a in enumerate(texts):
        for b in texts[i + 1:]:
            ops = difflib.SequenceMatcher(None, a, b).get_opcodes()
            changed = sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in ops if tag != "equal")
            if 0 < changed <= 2:  # e.g. 'item' vs 'items': one step with an optional suffix would do
                findings.append(("Duplication", "step definitions", f"near-duplicate: '{a}' ~ '{b}'"))

    for path in list(steps_dir(root).glob("*.py")) + list((root / "pages").glob("*.py")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("#")[0]
            if "time.sleep" in code or re.search(r"\bsleep\(", code):
                findings.append(("Stability", f"{path.name}:{lineno}", "uses sleep(); use an explicit wait"))
            if path.parent.name in ("steps", "step_defs") and re.search(r"£\s?\d", code):
                findings.append(("Data separation", f"{path.name}:{lineno}", "price hard-coded in step code"))

    scenario_count = sum(len(f.scenarios) for f in features)
    return findings, scenario_count, len(patterns)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    findings, n_scen, n_steps = review(root)
    print(f"Reviewed {root.name}: {n_scen} scenarios, {n_steps} step definitions\n")
    if not findings:
        print("No findings: every rubric check passed.")
    for category in sorted({f[0] for f in findings}):
        print(f"## {category}")
        for _, where, msg in [f for f in findings if f[0] == category]:
            print(f"- {where}: {msg}")
        print()
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
