"""One-command runner: tests + HTML/JSON/JUnit reports + traceability matrix.

    python run.py                     # default suite (behave.ini tags: no @manual/@wip/@data-creating)
    python run.py --tags=@smoke       # any extra behave arguments are passed through
    python run.py --allure            # also write Allure results to reports/allure-results
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"


def main():
    args = sys.argv[1:]
    REPORTS.mkdir(exist_ok=True)
    # behave pairs each -o with the -f before it; the last formatter (progress) prints to the console.
    cmd = [sys.executable, "-m", "behave",
           "-f", "json.pretty", "-o", str(REPORTS / "results.json"),
           "-f", "html", "-o", str(REPORTS / "report.html")]
    if "--allure" in args:
        args.remove("--allure")
        cmd += ["-f", "allure_behave.formatter:AllureFormatter", "-o", str(REPORTS / "allure-results")]
    cmd += ["-f", "progress", *args]
    code = subprocess.call(cmd, cwd=ROOT)
    subprocess.call([sys.executable, str(ROOT / "scripts" / "traceability.py")], cwd=ROOT)
    print(f"\nReports: {REPORTS / 'report.html'} | traceability: {REPORTS / 'traceability.md'}")
    sys.exit(code)


if __name__ == "__main__":
    main()
