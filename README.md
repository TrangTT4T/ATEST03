# ATEST03 – Sauce Demo Test Automation (Unit 1 BDD + Unit 2 Playwright)

Application under test: https://sauce-demo.myshopify.com · Python 3.11+

| Folder | Unit | Stack | Days | Document (VI / EN) |
| --- | --- | --- | --- | --- |
| [`unit1-bdd/`](unit1-bdd/) | Unit 1 – BDD Automation Design and Framework Practices | behave (Cucumber) + Selenium | Day 1–4 | [`Unit1_BDD_vi.md`](unit1-bdd/docs/Unit1_BDD_vi.md) · [`Unit1_BDD_en.md`](unit1-bdd/docs/Unit1_BDD_en.md) |
| [`unit2-playwright/`](unit2-playwright/) | Unit 2 – Playwright End-to-End Automation | pytest + pytest-bdd + Playwright | Day 5–8 | [`Unit2_Playwright_vi.md`](unit2-playwright/docs/Unit2_Playwright_vi.md) · [`Unit2_Playwright_en.md`](unit2-playwright/docs/Unit2_Playwright_en.md) |

Each folder is self-contained (its own `requirements.txt`, `dataset/` test data and README). Unit 1 is a plain BDD Cucumber project run with `behave`. Unit 2 builds on Unit 1: it runs the same Gherkin feature files (copied into `unit2-playwright/tests/features/`) on Playwright and adds tracing, network control, saved login, parallel runs and flaky-test control.

## Quick start

```bash
# Unit 1
cd unit1-bdd
pip install -r requirements.txt
behave                        # 21 scenarios (plain behave / Cucumber)

# Unit 2
cd ../unit2-playwright
pip install -r requirements.txt
playwright install chromium
pytest                        # 25 tests (21 Unit 1 scenarios + 4 network tests)
```
