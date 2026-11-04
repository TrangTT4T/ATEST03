# Sauce Demo – Unit 1: BDD Automation Design and Framework Practices

behave (Cucumber for Python) + Selenium WebDriver · Application under test: https://sauce-demo.myshopify.com

Covers Day 1–4. The whole unit is documented in one file, with a section per day: `docs/Unit1_BDD_vi.md` (Tiếng Việt) and `docs/Unit1_BDD_en.md` (English). Unit 2 (Playwright) lives in `../unit2-playwright/`; it reuses these feature files and keeps its own copy of `dataset/`.

| Day | Topic | Section in the unit document | Code used |
| --- | --- | --- | --- |
| 1 | Risk-based strategy, testability, BDD principles | Day 1 section | `scripts/risk_score.py`, `dataset/risk_register.csv`, `tests/features/` |
| 2 | Cucumber architecture: features, steps, hooks, tags, reporting | Day 2 section | `tests/features/cart.feature`, `login.feature`, `tests/environment.py`, `behave.ini`, `tests/steps/`, `pages/` |
| 3 | Lab: executable specs, reusable steps, traceable reports | Day 3 section | all features, `run.py`, `scripts/traceability.py` |
| 4 | Framework review | Day 4 section | `scripts/bdd_review.py` |

```text
sauce-demo-unit1-bdd/
├── behave.ini                  # default tags, userdata (base_url, browser), formatters
├── requirements.txt
├── run.py                      # tests + reports + traceability in one command
├── pages/                      # Selenium Page Objects (only place with locators)
├── tests/                      # everything behave runs (behave.ini: paths = tests)
│   ├── features/               # Gherkin specs (also copied into Unit 2)
│   │   ├── cart.feature  checkout.feature  product.feature
│   │   └── login.feature register.feature  search.feature
│   ├── steps/                  # common, cart, product, account, search
│   └── environment.py          # hooks
├── dataset/                    # test data (Unit 2 keeps its own copy)
│   ├── products.json
│   ├── requirements.json
│   └── risk_register.csv
├── helper_utility/helpers.py   # page(), product(): helpers shared by steps
├── scripts/
│   ├── risk_score.py           # Day 1
│   ├── traceability.py         # Day 3
│   └── bdd_review.py           # Day 4
├── reports/                    # generated
└── docs/Unit1_BDD_vi.md, Unit1_BDD_en.md (+ images/)
```

## Run

```bash
pip install -r requirements.txt
behave --dry-run                    # every step implemented?
python run.py                       # default suite (not @manual / @wip / @data-creating)
python run.py --tags=@smoke
python run.py --allure
python scripts/risk_score.py        # → reports/risk_strategy.md
python scripts/bdd_review.py .      # automated review rubric
```

Options: `BASE_URL`, `BROWSER=firefox`, `HEADLESS=false` (or `behave -D headless=false`). Chrome must be installed; Selenium Manager downloads chromedriver. Expected: 21 scenarios passed, 1 skipped (`@data-creating`), traceability 8/8.

Verified against a local mock with the standard Shopify page structure. If a locator differs on the live theme, fix it in `pages/` only.

## Create the repository

```bash
cd sauce-demo-unit1-bdd
git init && git add . && git commit -m "Unit 1: BDD framework for Sauce Demo"
git remote add origin <your-repo-url> && git push -u origin main
```
