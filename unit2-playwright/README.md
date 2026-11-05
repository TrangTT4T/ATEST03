# Sauce Demo – Unit 2: Playwright End-to-End Automation (builds on Unit 1 BDD)

pytest + pytest-bdd + Playwright · Application under test: https://sauce-demo.myshopify.com

Covers Day 5–8. Everything runs with the `pytest` command. The whole unit is documented in one file, with a section per day: `docs/Unit2_Playwright_vi.md` (Tiếng Việt) and `docs/Unit2_Playwright_en.md` (English).

Unit 2 carries the BDD part of Unit 1 (the Gherkin feature files and `dataset/products.json`), runs it on Playwright, then adds Playwright-only capabilities.

| From Unit 1 (copied unchanged) | Added in Unit 2 |
| --- | --- |
| `tests/features/*.feature`: 6 features, 14 scenarios, tags `@Rxx` `@critical` `@smoke` | Run on Playwright by `tests/test_bdd_features.py` (pytest-bdd); tags become pytest markers |
| `dataset/products.json` | Same file |
| Page Object pattern | `pages/` with Playwright locators (role/text first), auto-waiting |
| Step sentences | `tests/steps/shop_steps.py` on Playwright |
| Hooks in `environment.py` | Fixtures in `tests/conftest.py` |
| Screenshot on failure | Trace + screenshot + video on failure |
| — | Network interception, fault injection, throttling, saved auth state, parallel runs, flaky reruns |

| Day | Topic | Section in the unit document | Code used |
| --- | --- | --- | --- |
| 5 | Architecture, contexts, locators, fixtures, assertions, isolation | Day 5 section | `pages/`, `tests/conftest.py`, `tests/test_bdd_features.py`, `tests/steps/` |
| 6 | Tracing, network interception, auth state, parallel, reporting | Day 6 section | `pytest.ini`, `tests/test_network.py`, `tests/test_auth_state.py` |
| 7 | Lab: prioritised end-to-end workflows | Day 7 section | full suite |
| 8 | Revision + reliability, flaky control, stability | Day 8 section | repeated runs, `pytest-rerunfailures`, trace viewer |

```text
unit2-playwright/
├── pytest.ini                   # base_url, features folder, tracing, reports, markers
├── requirements.txt
├── dataset/products.json        # Unit 1 test data
├── pages/                       # Playwright Page Objects
├── tests/
│   ├── features/                # Unit 1 Gherkin files (unchanged)
│   ├── steps/shop_steps.py      # Unit 1 steps on Playwright
│   ├── conftest.py              # fixtures, network control, auth state
│   ├── test_bdd_features.py     # runs every feature file
│   ├── test_network.py
│   └── test_auth_state.py
└── docs/Unit2_Playwright_vi.md, Unit2_Playwright_en.md
```

## Run

```bash
pip install -r requirements.txt
playwright install chromium
pytest                               # 25 tests: 21 Unit 1 scenarios + 4 network tests
pytest -m smoke
pytest -m R01                        # every test for one risk (Gherkin + plain tests)
pytest -n auto                       # parallel
pytest -m auth                       # needs SAUCE_EMAIL / SAUCE_PASSWORD
pytest -m R01 --headed --slowmo 300
playwright show-trace test-results/<test>/trace.zip
```

Outputs: `reports/report.html`, `reports/junit.xml`, `test-results/` (trace, screenshot, video of failed tests). Never commit `.auth/`.

Verified against a local mock with the standard Shopify page structure. If a locator differs on the live theme, fix it in `pages/` only.

## Keeping the features in sync with Unit 1

`tests/features/` and `dataset/products.json` are copies of `../unit1-bdd/`. When a scenario changes there, copy the file here.
