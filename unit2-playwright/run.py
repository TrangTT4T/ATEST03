"""One-command runner for Unit 2.

    python run.py                       # default suite: all Unit 1 features + Playwright tests
    python run.py smoke                 # @smoke only
    python run.py parallel              # pytest-xdist, one worker per CPU
    python run.py auth                  # @auth tests (needs SAUCE_EMAIL / SAUCE_PASSWORD)
    python run.py stability --runs 3    # repeat the suite, then classify flaky tests (Day 8)
    python run.py review                # Unit 1 Gherkin review + Unit 2 stability check (Day 8)
Any other arguments are passed to pytest, e.g.  python run.py --headed --slowmo 300
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTEST = [sys.executable, "-m", "pytest"]


def call(cmd):
    print("$", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


def main(argv):
    mode = argv[0] if argv and not argv[0].startswith("-") else "all"
    rest = argv[1:] if mode != "all" else argv
    if mode == "smoke":
        return call(PYTEST + ["-m", "smoke", *rest])
    if mode == "parallel":
        return call(PYTEST + ["-n", "auto", *rest])
    if mode == "auth":
        return call(PYTEST + ["-m", "auth", *rest])
    if mode == "stability":
        runs = 3
        if "--runs" in rest:
            i = rest.index("--runs")
            runs = int(rest[i + 1])
            rest = rest[:i] + rest[i + 2:]
        out = ROOT / "reports" / "runs"
        out.mkdir(parents=True, exist_ok=True)
        for old in out.glob("*.xml"):
            old.unlink()
        for n in range(1, runs + 1):
            call(PYTEST + [f"--junitxml=reports/runs/run_{n}.xml", *rest])
        return call([sys.executable, "scripts/flaky_report.py"])
    if mode == "review":
        # Unit 1 Gherkin review on the inherited features + the pytest-bdd step definitions
        code = call([sys.executable, "scripts/bdd_review.py", "."])
        return call([sys.executable, "scripts/stability_check.py"]) or code
    return call(PYTEST + rest)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
