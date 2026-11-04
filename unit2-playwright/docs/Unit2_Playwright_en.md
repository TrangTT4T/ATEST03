# Unit 2 – Playwright End-to-End Automation (Sauce Demo)

pytest + pytest-bdd + Playwright · Application under test: https://sauce-demo.myshopify.com · Code: this repository

Unit 2 builds on Unit 1: the same Gherkin feature files, test data, risk and requirement tags run on Playwright (Day 5), then gain tracing, network control, saved login and parallel runs (Day 6), are applied to the prioritised workflows in the lab (Day 7), and are made reliable with flaky-test control and stability checks (Day 8).

| Day | Content | LO | Delivery | Minutes | Format |
| --- | --- | --- | --- | --- | --- |
| Day 5 | Playwright architecture, browser contexts, locators, fixtures, assertions, isolation | LO3 | Concept/Lecture | 120 | Virtual |
| Day 6 | Tracing, network interception, authentication state, parallel execution, reporting patterns | LO3 | Concept/Lecture | 120 | Virtual |
| Day 7 | Playwright implementation lab: prioritised end-to-end workflows with fixtures, tracing, network control | LO3 | Assignment/Lab | 150 | Hybrid |
| Day 8 | Topic revision | LO3 | Guides/Review | 60 | Virtual |
| Day 8 | Reliability and maintainability: failure analysis, flaky-test control, tracing diagnostics, stability | LO3 | Concept/Lecture | 120 | Virtual |

Contents: Day 5 – Architecture · Day 6 – Tracing, network, auth, parallel · Day 7 – Lab · Day 8 – Revision + reliability

---

## Day 5 – Playwright Architecture: Browser Contexts, Locators, Fixtures, Assertions & Isolation

Unit 2 · LO3 · Concept/Lecture · 120 min · Virtual · Code: repo `sauce-demo-unit2-playwright` (Python, pytest-playwright, pytest-bdd)

Unit 2 keeps everything Unit 1 built and changes only the engine: the same 6 feature files, shared test data, risk and requirement tags now run on Playwright, and pytest fixtures replace behave hooks.

### 1. What is inherited from Unit 1, what is new

| Unit 1 (behave + Selenium) | Unit 2 (pytest + Playwright) | Status |
| --- | --- | --- |
| Unit 1 `features/*.feature` | Copied unchanged into `features/`, run by `tests/test_bdd_features.py` (pytest-bdd) | Inherited unchanged |
| `shared/products.json`, `requirements.json`, `risk_register.csv` | Same files | Inherited, REQ-09/REQ-10 added |
| Tags `@REQ-xx`, `@Rxx`, `@critical`, `@smoke` | Become pytest markers: `pytest -m smoke`, `-m R01` | Inherited |
| Page Objects (`pages/`) | Same class names, Playwright `Locator` instead of `WebElement` | Ported |
| Step definitions (`features/steps/`) | `tests/step_defs/shop_steps.py`, same sentences | Ported |
| `environment.py` hooks | `tests/conftest.py` fixtures | Replaced |
| `WebDriverWait` explicit waits | Auto-waiting actions + retrying `expect()` | Replaced |
| Fresh browser per scenario | Fresh **browser context** per test (much cheaper) | Improved |
| Screenshot on failure | Screenshot + video + **trace** on failure | Extended (Day 6) |
| Traceability matrix | Same idea, built inside pytest, works in parallel | Extended (Day 6) |
| — | Network interception, auth state, parallel runs, flaky detection | New (Day 6–8) |

### 2. Playwright architecture

```text
pytest session
└── playwright  (driver process, one per worker)
    └── browser  (Chromium / Firefox / WebKit, one per worker, session scope)
        └── context  (one per test: own cookies, cache, storage → isolation)
            └── page  (one tab per test)
```

A context costs milliseconds, so every test gets a clean cart without restarting the browser. In Unit 1 the same isolation needed a new Chrome per scenario.

### 3. Locators

Locator order used in `pages/`:

| Priority | Locator | Example in `pages/` |
| --- | --- | --- |
| 1 | Role + accessible name | `page.get_by_role("link", name=re.compile(r"My Cart \(\d+\)"))` |
| 2 | Role + level | `page.get_by_role("heading", level=1)` (product title) |
| 3 | Text | `page.get_by_text("£60.00")` |
| 4 | Stable attribute / form action | `form[action*='/cart/add']`, `input[name^='updates']` |
| 5 | Filtered locator | `locator("tr, li, div").filter(has=get_by_role("link", name="Striped top"))` |
| Never | Position | `:nth-child`, `xpath=(//a)[3]` (blocked by `scripts/stability_check.py`) |

### 4. Fixtures (`tests/conftest.py`)

| Fixture | Scope | Replaces in Unit 1 | Does |
| --- | --- | --- | --- |
| `browser`, `context`, `page` | session / test / test | `before_scenario` + `after_scenario` | Provided by pytest-playwright |
| `browser_context_args` | session | `_make_driver()` options | Viewport 1366×900, locale en-GB |
| `products` | session | `before_all` loading JSON | Reads `shared/products.json` |
| `shop` | test | `support/helpers.page()` | All Page Objects bound to this test's page |
| `cart_with` | test | Given step code | Factory: `cart_with("Noir jacket", 2)` |
| `block_third_party` | test, autouse | — | Network control (Day 6) |
| `customer_state` | session | — | Saved login (Day 6) |

```python
@pytest.fixture
def cart_with(shop, products):
    """Factory fixture: cart_with("Noir jacket", 2) puts 2 Noir jackets in this test's cart."""
    def _add(name: str, quantity: int = 1):
        shop.product.open_product(products[name]["handle"])
        shop.product.add_to_cart(quantity)
        return shop.cart.open()
    return _add
```

### 5. Assertions

`expect()` retries until the condition holds or the timeout (5 s) ends, so no explicit waits are written:

```python
@then(parsers.re(r"the cart should contain (?P<count>\d+) items?"), converters={"count": int})
def cart_count(shop, count):
    cart = shop.cart.open()
    expect(cart.mini_cart).to_have_text(re.compile(rf"My Cart \({count}\)"))
    assert cart.total_quantity() == count
```

| Unit 1 | Unit 2 |
| --- | --- |
| `self.wait.until(EC.url_contains("checkout"))` | `expect(page).to_have_url(re.compile("checkout"))` |
| `assert cart.is_empty()` after a wait | `expect(cart.quantity_inputs).to_have_count(0)` |
| `assert error_text().strip()` | `expect(shop.login.error).to_be_visible()` |

### 6. Isolation check

`tests/test_auth_state.py::test_auth_state_does_not_leak_into_other_tests` proves that a test using the default `page` is not logged in even when another test in the same session uses a saved login.

### 7. Run

```bash
cd sauce-demo-unit2-playwright
pip install -r requirements.txt
playwright install chromium
pytest --collect-only -q          # 25 tests: 21 from Unit 1 features + 4 Playwright-only
pytest -m smoke                   # same smoke tags as Unit 1
pytest --headed --slowmo 300      # watch it run
```

### 8. Review questions

1. Why does a new browser context give the same isolation as a new browser, and why is it cheaper?
2. Which Unit 1 file did `browser_context_args` replace?
3. Rewrite `self.wait.until(lambda d: name in body_text())` as a Playwright assertion.
4. Why is `get_by_role("link", name=...)` preferred over `a[href*='/cart']`?

---

## Day 6 – Tracing, Network Interception, Authentication State, Parallel Execution & Reporting

Unit 2 · LO3 · Concept/Lecture · 120 min · Virtual · Code: repo `sauce-demo-unit2-playwright`

Day 6 adds the five capabilities Unit 1 did not have: a full trace of every failed test, control over network traffic, login reuse, parallel runs, and reports that stay correct in parallel.

### 1. Tracing (extends Unit 1's screenshot on failure)

Configured once in `pytest.ini`:

```ini
addopts =
    --tracing retain-on-failure
    --screenshot only-on-failure
    --video retain-on-failure
    --output test-results
```

| Unit 1 | Unit 2 |
| --- | --- |
| `after_step` saves one PNG | `test-results/<test>/trace.zip`, `test-failed-1.png`, `video.webm` |
| Shows the last screen only | Every action, DOM snapshot before/after, console, network, source line |

Open a trace:

```bash
playwright show-trace test-results/<test-folder>/trace.zip
```

Force traces for every test while debugging: `pytest --tracing on`.

### 2. Network interception

#### 2.1 Block third-party traffic (autouse fixture)

```python
@pytest.fixture(autouse=True)
def block_third_party(request, context: BrowserContext, base_url: str):
    blocked: list[str] = []
    if request.node.get_closest_marker("allow_third_party"):
        yield blocked
        return
    store_host = urlparse(base_url).hostname

    def handle(route):
        if _is_allowed(route.request.url, store_host):
            route.continue_()
        else:
            blocked.append(route.request.url)
            route.abort()

    context.route("**/*", handle)
    yield blocked
```

Allowed: the store host and `*.shopify.com`, `*.myshopify.com`, `*.shopifycdn.com`. Everything else (Facebook, Twitter, Pinterest, the Sauce app) is aborted. This turns risk R09 (manual in Unit 1) into REQ-09, tested automatically.

#### 2.2 The four network tests (`tests/test_network.py`)

| Test | Technique | REQ / Risk |
| --- | --- | --- |
| `test_third_party_calls_are_blocked_and_shop_still_works` | `context.route` + abort, then the cart flow | REQ-09 / R09 |
| `test_add_to_cart_posts_the_product_form` | `page.expect_request(...)`: assert method and body | REQ-01 / R01 |
| `test_failed_add_to_cart_request_does_not_add_the_product` | `page.route(...).fulfill(status=500)`: fault injection | REQ-01 / R01 |
| `test_catalog_loads_on_a_slow_network` | Chromium CDP `Network.emulateNetworkConditions` (400 ms latency) | REQ-06 / R05 |

Fault injection example:

```python
page.route("**/cart/add*", lambda route: route.fulfill(status=500, body="Internal Server Error"))
shop.product.open_product(products["Noir jacket"]["handle"])
shop.product.add_button.click()
page.unroute("**/cart/add*")
expect(shop.cart.open().quantity_inputs).to_have_count(0)
```

### 3. Authentication state

Unit 1 typed credentials in every scenario that needed a login. Unit 2 logs in once per session and saves cookies and localStorage:

```python
@pytest.fixture(scope="session")
def customer_state(browser: Browser, base_url: str) -> Path:
    email, password = os.getenv("SAUCE_EMAIL"), os.getenv("SAUCE_PASSWORD")
    if not (email and password):
        pytest.skip("Set SAUCE_EMAIL and SAUCE_PASSWORD to run @auth tests")
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    login = LoginPage(page).open()
    login.login(email, password)
    page.wait_for_url("**/account**")
    AUTH_FILE.parent.mkdir(exist_ok=True)
    context.storage_state(path=str(AUTH_FILE))
    context.close()
    return AUTH_FILE
```

Used by `tests/test_auth_state.py` (REQ-10). `.auth/customer.json` holds a session: never commit it.

```bash
# Linux/macOS
SAUCE_EMAIL=you@example.com SAUCE_PASSWORD='...' python run.py auth
# Windows PowerShell
$env:SAUCE_EMAIL="you@example.com"; $env:SAUCE_PASSWORD="..."; python run.py auth
```

### 4. Parallel execution

```bash
python run.py parallel        # = pytest -n auto (pytest-xdist)
pytest -n 4
```

Parallel runs are safe because every test has its own context (Day 5) and no test depends on another. The shared demo store limits how far to push it: keep `-n` small on the live site.

### 5. Reporting patterns

| Report | Produced by | Path |
| --- | --- | --- |
| HTML | pytest-html (`--html` in `pytest.ini`) | `reports/report.html` |
| JUnit XML | `--junitxml` | `reports/junit.xml` |
| Trace, screenshot, video | pytest-playwright | `test-results/` |
| Traceability matrix | hooks in `conftest.py` | `reports/traceability.md` |

The traceability hooks read the Gherkin tags (`@REQ-01`, `@R01`) and the `req()` / `risk()` markers of plain tests. Under xdist the collection runs on the workers, so the ids travel in `item.user_properties` and the controller writes the matrix:

```python
def pytest_collection_modifyitems(items):
    for item in items:
        names = [m.name for m in item.iter_markers()]
        reqs = sorted({n for n in names if re.fullmatch(r"REQ-\d+", n)} | {m.args[0] for m in item.iter_markers("req")})
        risks = sorted({n for n in names if re.fullmatch(r"R\d+", n)} | {m.args[0] for m in item.iter_markers("risk")})
        item.user_properties.append(("reqs", reqs or ["(none)"]))
        item.user_properties.append(("risks", risks))
```

### 6. Review questions

1. What does a trace show that a screenshot cannot?
2. Why is `block_third_party` autouse, and how does a test opt out?
3. Why must `customer_state` be session-scoped, and why must `.auth/` stay out of git?
4. Why did the traceability matrix need `user_properties` once `-n` was used?

---

## Day 7 – Playwright Implementation Lab: Prioritised End-to-End Workflows with Fixtures, Tracing & Network Control

Unit 2 · LO3 · Assignment/Lab · 150 min · Hybrid · Code: repo `sauce-demo-unit2-playwright`

The lab automates the Unit 1 risk priorities on Playwright: 25 tests in the default run (21 Unit 1 scenarios + 4 network tests), 2 auth tests with credentials, 10/10 requirements traceable.

### 1. Prioritised workflows (from the Unit 1 risk register)

| Priority | Workflow | Risk | Tests | Unit 2 technique |
| --- | --- | --- | --- | --- |
| P1 | Add to cart, totals, change, remove | R01 Critical (20) | 5 scenarios from `cart.feature` + 2 network tests | `cart_with` fixture, `expect_request`, 500 fault injection |
| P1 | Cart → checkout | R02 Critical (15) | 1 scenario from `checkout.feature` | `expect(page).to_have_url` |
| P1 | Product detail, sold-out | R03 High (12) | 2 scenarios from `product.feature` | role locators |
| P1 | Login, password reset, saved session | R04 High (12) | 3 scenarios + 2 auth tests | `customer_state` storage state |
| P1 | Catalog prices and stock | R05 High (12) | 7 Examples rows + slow-network test | CDP throttling |
| P2 | Registration validation | R06 Medium (9) | 1 scenario (+1 `@data-creating`) | — |
| P2 | Search | R07 Medium (9) | 2 scenarios | — |
| P2 | Third-party failure does not break shopping | R09 Medium (6) | 1 network test | `block_third_party` route |

R09 was manual in Unit 1 because the widgets are flaky; blocking them at the network layer makes the risk testable.

### 2. Files

| File | Role |
| --- | --- |
| `tests/test_bdd_features.py` | `scenarios(".")` runs every file in `features/` (Unit 1 feature files) |
| `tests/step_defs/shop_steps.py` | Playwright implementation of every Unit 1 step |
| `tests/conftest.py` | Fixtures, network control, auth state, traceability hooks |
| `tests/test_network.py` | Interception, request assertion, fault injection, throttling |
| `tests/test_auth_state.py` | Saved login (REQ-10) and isolation check |
| `pages/` | Page Objects ported from Unit 1 |
| `pytest.ini` | base URL, tracing, reports, default marker filter, features folder |
| `run.py` | `smoke`, `parallel`, `auth`, `stability`, `review` modes |

### 3. Run the lab

```bash
cd sauce-demo-unit2-playwright
pip install -r requirements.txt
playwright install chromium
python run.py                  # default suite
python run.py smoke            # @smoke: add to cart + checkout
python run.py parallel         # pytest -n auto
python run.py auth             # needs SAUCE_EMAIL / SAUCE_PASSWORD
pytest -m R01                  # every test for risk R01 (Gherkin tag or marker)
pytest -m "critical and not negative"
```

### 4. Expected results

| Check | Result |
| --- | --- |
| `python run.py` | 25 passed, 3 deselected (`@auth` ×2, `@data-creating` ×1) |
| `python run.py parallel` | 25 passed, same traceability matrix |
| `python run.py auth` (with an account) | 2 passed |
| `reports/traceability.md` | REQ-01…REQ-09 covered in the default run; REQ-10 shown as "no test ran in this session" until `auth` runs |
| Failed test | `test-results/<test>/trace.zip`, screenshot, video |

Verified against a local Shopify-structured mock store. Against the live store, check locators first (Unit 1 finding F2).

### 5. Lab tasks

1. Add a fault-injection test: the cart page answers 503. What should the customer see? Write the assertion.
2. Make `test_catalog_loads_on_a_slow_network` fail by lowering the timeout to 1 s, then open its trace and find the slow request.
3. Add a scenario to `features/search.feature`. Run it here and in the Unit 1 repo: which code had to change? (Answer: none, unless the step sentence is new.)
4. Run `python run.py parallel` three times and compare durations with the serial run.

---

## Day 8 – Topic Revision + Playwright Reliability & Maintainability: Failure Analysis, Flaky-Test Control, Tracing Diagnostics

Unit 2 · LO3 · Guides/Review (60 min) + Concept/Lecture (120 min) · Virtual · Code: repo `sauce-demo-unit2-playwright`

Day 8 closes both units: part A revises Unit 2 against Unit 1, part B turns stability from a manual check (Unit 1 finding F3) into automated tools: repeated runs with flaky classification, a static stability check, and a trace-driven failure analysis routine.

### Part A – Topic revision (60 min)

| Topic | Unit 1 (Day 1–4) | Unit 2 (Day 5–7) |
| --- | --- | --- |
| Specification | Gherkin features, risk + REQ tags | Same files, run by pytest-bdd |
| Engine | Selenium WebDriver | Playwright (auto-wait, contexts) |
| Setup / teardown | behave hooks | pytest fixtures (`conftest.py`) |
| Isolation | New browser per scenario | New context per test |
| Waiting | `WebDriverWait` | Actions auto-wait, `expect()` retries |
| Failure evidence | Screenshot | Trace + screenshot + video |
| Network | Not controlled | Block, assert, fault-inject, throttle |
| Login | UI login each time | Saved storage state |
| Speed | Serial | `-n auto` parallel |
| Traceability | `scripts/traceability.py` after the run | Built into pytest hooks, parallel-safe |
| Review | `bdd_review.py` | Same script + `stability_check.py` + flaky report |

Revision questions:

1. Which Unit 1 files does Unit 2 run without changes, and why is that useful?
2. Name two risks whose test technique changed in Unit 2 and explain how.
3. Which Unit 1 review findings are closed by Unit 2 tools? (F3 stability; F5 shared requirements; F7 and F8 found by the re-check.)

### Part B – Reliability and maintainability (120 min)

#### B1. Failure analysis routine

```text
test fails
 ├─ 1. read the assertion message in reports/report.html
 ├─ 2. open test-results/<test>/trace.zip   (playwright show-trace)
 │     ├─ Actions tab: which step, which locator, how long it waited
 │     ├─ Snapshots: DOM before/after the action
 │     └─ Network tab: status codes, slow or failed requests
 ├─ 3. classify
 │     ├─ product defect   → wrong price, wrong total, error page → raise a bug with the trace
 │     ├─ test defect      → locator changed, wrong assumption → fix in pages/ or step_defs/
 │     └─ environment      → store down, captcha, network → retry later, mark @manual if persistent
 └─ 4. if it passes on rerun without a change → flaky: see B2
```

#### B2. Flaky-test control

```bash
python run.py stability --runs 3      # runs the suite 3 times, writes reports/runs/run_N.xml
                                      # then scripts/flaky_report.py → reports/flaky_report.md
```

`scripts/flaky_report.py` classifies every test:

| Status | Meaning | Action |
| --- | --- | --- |
| stable-pass | passed in every run | — |
| stable-fail | failed in every run | real defect or broken test: analyse the trace |
| flaky | passed in some runs, failed in others | quarantine, find the root cause |

Quarantine while the root cause is found (pytest-rerunfailures is installed):

```python
@pytest.mark.flaky(reruns=2, reruns_delay=1)   # temporary, with a ticket number in the commit
def test_something_flaky(...):
    ...
```

Reruns hide problems, so they are a temporary label, never a default `--reruns` for the whole suite.

Typical root causes and the fix used in this code:

| Root cause | Fix in this repository |
| --- | --- |
| Fixed waits | None used; `expect()` and `wait_for_url` only |
| Next action before the previous request ends | `BasePage.submit()` waits for the navigation after every form button; add-to-cart also waits for the `/cart/add` response (Unit 1 findings F7, F8: the failure screenshot showed the old cart) |
| Third-party scripts | `block_third_party` autouse fixture |
| Shared state between tests | One context per test; `test_auth_state_does_not_leak_into_other_tests` |
| Positional selectors | Blocked by `stability_check.py` |

#### B3. Static stability check

```bash
python run.py review     # 1. scripts/bdd_review.py (from Unit 1) on features/ and tests/step_defs/
                         # 2. scripts/stability_check.py on Unit 2 tests and pages
```

`scripts/stability_check.py` fails (exit 1) on:

| Rule | Why |
| --- | --- |
| `wait_for_timeout(` / `time.sleep(` | Fixed waits are slow and still flaky |
| `force=True` | Hides elements that a user could not click |
| `:nth-child`, `nth=`, `.nth(`, `)[n]` in tests | Breaks when the layout changes |
| Raw CSS/XPath in tests | Locators belong in `pages/` |
| Plain test without `req()` / `risk()` | Breaks traceability |

#### B4. Maintainability criteria (checklist)

- [ ] Every requirement in `shared/requirements.json` has at least one test (`reports/traceability.md`)
- [ ] Gherkin stays declarative (`bdd_review.py` passes)
- [ ] No locator outside `pages/`
- [ ] No fixed waits, no `force=True` (`stability_check.py` passes)
- [ ] 0 flaky tests in 3 consecutive runs (`flaky_report.md`)
- [ ] Every failure leaves a trace, screenshot and video
- [ ] Suite passes with `-n auto`
- [ ] Secrets (`SAUCE_PASSWORD`, `.auth/`) are never committed

### Expected results

| Check | Result on the mock store |
| --- | --- |
| `python run.py review` | 0 findings in both checks |
| `python run.py stability --runs 2` | 25 tests, 0 flaky, 0 always failing |
| Forced failure | `trace.zip`, `test-failed-1.png`, `video.webm` in `test-results/` |
