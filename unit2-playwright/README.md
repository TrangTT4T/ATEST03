# Sauce Demo – Unit 2: Playwright End-to-End Automation (builds on Unit 1 BDD)

pytest + pytest-bdd + Playwright · Application under test: https://sauce-demo.myshopify.com

Covers Day 5–8. The whole unit is documented in one file, with a section per day: `docs/Unit2_Playwright_vi.md` (Tiếng Việt) and `docs/Unit2_Playwright_en.md` (English).

This repository is self-contained: it carries the BDD part of Unit 1 (the Gherkin feature files, `dataset/` data and the BDD review script) and runs it on Playwright, then adds Playwright-only capabilities.

| From Unit 1 (copied unchanged) | Added in Unit 2 |
| --- | --- |
| `tests/features/*.feature`: 6 features, 14 scenarios, tags `@REQ-xx` `@Rxx` `@critical` `@smoke` | Run on Playwright by `tests/test_bdd_features.py` (pytest-bdd); tags become pytest markers |
| `dataset/products.json`, `requirements.json`, `risk_register.csv` | REQ-09 (third-party failure), REQ-10 (saved login) |
| Page Object pattern | `pages/` with Playwright locators (role/text first), auto-waiting |
| Step sentences | `tests/steps/shop_steps.py` on Playwright |
| Day 4 review checklist (done by hand in Unit 1) | Automated: `scripts/bdd_review.py`, `scripts/stability_check.py`, `scripts/flaky_report.py` |
| Screenshot on failure, traceability matrix | Trace + video on failure; traceability inside pytest, parallel-safe |
| — | Network interception, fault injection, throttling, saved auth state, parallel runs |

| Day | Topic | Section in the unit document | Code used |
| --- | --- | --- | --- |
| 5 | Architecture, contexts, locators, fixtures, assertions, isolation | Day 5 section | `pages/`, `tests/conftest.py`, `tests/test_bdd_features.py`, `tests/steps/` |
| 6 | Tracing, network interception, auth state, parallel, reporting | Day 6 section | `pytest.ini`, `tests/test_network.py`, `tests/test_auth_state.py` |
| 7 | Lab: prioritised end-to-end workflows | Day 7 section | full suite, `run.py` |
| 8 | Revision + reliability, flaky control, stability | Day 8 section | `scripts/flaky_report.py`, `scripts/stability_check.py`, `scripts/bdd_review.py` |

```text
sauce-demo-unit2-playwright/
├── pytest.ini                   # base_url, features folder, tracing, reports, markers
├── requirements.txt
├── run.py                       # all | smoke | parallel | auth | stability | review
├── pages/                       # Playwright Page Objects
├── tests/
│   ├── features/                # Unit 1 Gherkin files (unchanged)
│   ├── steps/shop_steps.py      # Unit 1 steps on Playwright
│   ├── conftest.py              # fixtures, network control, auth state, traceability
│   ├── test_bdd_features.py     # runs every feature file
│   ├── test_network.py
│   └── test_auth_state.py
├── dataset/                     # Unit 1 test data + REQ-09/REQ-10
├── scripts/
│   ├── bdd_review.py            # Unit 1's Day 4 checklist, automated
│   ├── stability_check.py
│   └── flaky_report.py
└── docs/Unit2_Playwright_vi.md, Unit2_Playwright_en.md
```

## Run

```bash
pip install -r requirements.txt
playwright install chromium
python run.py                        # 25 tests: 21 Unit 1 scenarios + 4 network tests
python run.py smoke
python run.py parallel               # pytest -n auto
python run.py auth                   # needs SAUCE_EMAIL / SAUCE_PASSWORD
python run.py stability --runs 3     # flaky report
python run.py review                 # Gherkin review + Playwright stability check
pytest -m R01 --headed --slowmo 300
playwright show-trace test-results/<test>/trace.zip
```

Outputs: `reports/report.html`, `reports/junit.xml`, `reports/traceability.md`, `reports/flaky_report.md`, `test-results/` (trace, screenshot, video of failed tests). Never commit `.auth/`.

Verified against a local mock with the standard Shopify page structure. If a locator differs on the live theme, fix it in `pages/` only.

## Keeping the features in sync with Unit 1

`tests/features/` and `dataset/` are copies of the Unit 1 repo. When a scenario changes there, copy the file here (or add the Unit 1 repo as a git submodule and point `bdd_features_base_dir` in `pytest.ini` to it).

## Create the repository

```bash
cd sauce-demo-unit2-playwright
git init && git add . && git commit -m "Unit 2: Playwright framework for Sauce Demo (builds on Unit 1 BDD)"
git remote add origin <your-repo-url> && git push -u origin main
```
