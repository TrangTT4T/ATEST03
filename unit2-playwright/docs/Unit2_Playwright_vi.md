# Unit 2 – Playwright End-to-End Automation (Sauce Demo)

pytest + pytest-bdd + Playwright · Website kiểm thử: https://sauce-demo.myshopify.com · Code: chính repo này

Unit 2 kế thừa Unit 1: cùng các feature Gherkin, dữ liệu test, tag rủi ro và requirement, chạy trên Playwright (Day 5); thêm tracing, kiểm soát network, lưu phiên đăng nhập, chạy song song (Day 6); áp dụng cho các luồng ưu tiên trong bài lab (Day 7); và làm cho ổn định bằng kiểm soát flaky và kiểm tra độ ổn định (Day 8).

| Day | Nội dung | LO | Hình thức | Phút | Format |
| --- | --- | --- | --- | --- | --- |
| Day 5 | Kiến trúc Playwright, browser context, locator, fixture, assertion, cô lập | LO3 | Concept/Lecture | 120 | Virtual |
| Day 6 | Tracing, chặn/giả lập network, trạng thái đăng nhập, chạy song song, mẫu báo cáo | LO3 | Concept/Lecture | 120 | Virtual |
| Day 7 | Lab Playwright: tự động hóa luồng E2E ưu tiên với fixture, tracing, kiểm soát network | LO3 | Assignment/Lab | 150 | Hybrid |
| Day 8 | Ôn tập chủ đề | LO3 | Guides/Review | 60 | Virtual |
| Day 8 | Độ tin cậy và bảo trì: phân tích lỗi, kiểm soát flaky, chẩn đoán bằng trace, ổn định | LO3 | Concept/Lecture | 120 | Virtual |

Nội dung: Day 5 – Kiến trúc · Day 6 – Tracing, network, đăng nhập, song song · Day 7 – Lab · Day 8 – Ôn tập + độ tin cậy

---

## Day 5 – Playwright Architecture: Browser Contexts, Locators, Fixtures, Assertions & Isolation

Unit 2 · LO3 · Concept/Lecture · 120 phút · Virtual · Code: repo `sauce-demo-unit2-playwright` (Python, pytest-playwright, pytest-bdd)

Unit 2 giữ nguyên mọi thứ Unit 1 đã xây và chỉ đổi "động cơ": cùng 6 feature file, cùng dữ liệu dùng chung, cùng tag rủi ro và requirement, giờ chạy trên Playwright; fixture của pytest thay cho hook của behave.

### 1. Kế thừa từ Unit 1 và phần mới

| Unit 1 (behave + Selenium) | Unit 2 (pytest + Playwright) | Trạng thái |
| --- | --- | --- |
| `tests/features/*.feature` của Unit 1 | Chép nguyên vẹn vào `tests/features/`, chạy qua `tests/test_bdd_features.py` (pytest-bdd) | Kế thừa nguyên vẹn |
| `dataset/products.json`, `requirements.json`, `risk_register.csv` | Cùng file | Kế thừa, thêm REQ-09/REQ-10 |
| Tag `@REQ-xx`, `@Rxx`, `@critical`, `@smoke` | Thành marker pytest: `pytest -m smoke`, `-m R01` | Kế thừa |
| Page Object (`pages/`) | Cùng tên class, dùng `Locator` của Playwright thay `WebElement` | Chuyển đổi |
| Step definitions (`tests/steps/`) | `tests/steps/shop_steps.py`, cùng câu chữ | Chuyển đổi |
| Hook trong `environment.py` | Fixture trong `tests/conftest.py` | Thay thế |
| Explicit wait `WebDriverWait` | Action tự chờ + `expect()` tự thử lại | Thay thế |
| Trình duyệt mới mỗi scenario | **Browser context** mới mỗi test (rẻ hơn nhiều) | Cải tiến |
| Ảnh khi fail | Ảnh + video + **trace** khi fail | Mở rộng (Day 6) |
| Ma trận truy vết | Cùng ý tưởng, chạy trong pytest, đúng cả khi chạy song song | Mở rộng (Day 6) |
| — | Chặn/giả lập network, lưu trạng thái đăng nhập, chạy song song, phát hiện flaky | Mới (Day 6–8) |

### 2. Kiến trúc Playwright

```text
pytest session
└── playwright  (tiến trình driver, mỗi worker một cái)
    └── browser  (Chromium / Firefox / WebKit, mỗi worker một cái, scope session)
        └── context  (mỗi test một cái: cookie, cache, storage riêng → cô lập)
            └── page  (mỗi test một tab)
```

Tạo context chỉ mất vài mili giây, nên mỗi test có giỏ hàng sạch mà không cần khởi động lại trình duyệt. Ở Unit 1, muốn cô lập như vậy phải mở Chrome mới cho mỗi scenario.

### 3. Locator

Thứ tự ưu tiên trong `pages/`:

| Ưu tiên | Locator | Ví dụ trong `pages/` |
| --- | --- | --- |
| 1 | Role + tên hiển thị | `page.get_by_role("link", name=re.compile(r"My Cart \(\d+\)"))` |
| 2 | Role + level | `page.get_by_role("heading", level=1)` (tên sản phẩm) |
| 3 | Text | `page.get_by_text("£60.00")` |
| 4 | Thuộc tính ổn định / action của form | `form[action*='/cart/add']`, `input[name^='updates']` |
| 5 | Locator có filter | `locator("tr, li, div").filter(has=get_by_role("link", name="Striped top"))` |
| Không dùng | Theo vị trí | `:nth-child`, `xpath=(//a)[3]` (bị `scripts/stability_check.py` chặn) |

### 4. Fixture (`tests/conftest.py`)

| Fixture | Scope | Thay cho phần nào ở Unit 1 | Làm gì |
| --- | --- | --- | --- |
| `browser`, `context`, `page` | session / test / test | `before_scenario` + `after_scenario` | pytest-playwright cung cấp |
| `browser_context_args` | session | option trong `_make_driver()` | Viewport 1366×900, locale en-GB |
| `products` | session | `before_all` đọc JSON | Đọc `dataset/products.json` |
| `shop` | test | `helper_utility/helpers.page()` | Mọi Page Object gắn với page của test |
| `cart_with` | test | code của step Given | Factory: `cart_with("Noir jacket", 2)` |
| `block_third_party` | test, autouse | — | Kiểm soát network (Day 6) |
| `customer_state` | session | — | Lưu trạng thái đăng nhập (Day 6) |

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

### 5. Assertion

`expect()` tự thử lại tới khi đúng hoặc hết timeout (5 giây), nên không phải viết wait:

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
| `assert cart.is_empty()` sau khi wait | `expect(cart.quantity_inputs).to_have_count(0)` |
| `assert error_text().strip()` | `expect(shop.login.error).to_be_visible()` |

### 6. Kiểm tra tính cô lập

`tests/test_auth_state.py::test_auth_state_does_not_leak_into_other_tests` chứng minh test dùng `page` mặc định không bị đăng nhập, dù test khác trong cùng session dùng trạng thái đăng nhập đã lưu.

### 7. Chạy

```bash
cd sauce-demo-unit2-playwright
pip install -r requirements.txt
playwright install chromium
pytest --collect-only -q          # 25 test: 21 từ feature của Unit 1 + 4 test riêng của Playwright
pytest -m smoke                   # cùng tag smoke như Unit 1
pytest --headed --slowmo 300      # xem trình duyệt chạy
```

### 8. Câu hỏi ôn tập

1. Vì sao browser context mới cô lập giống trình duyệt mới, và vì sao rẻ hơn?
2. `browser_context_args` thay cho file nào ở Unit 1?
3. Viết lại `self.wait.until(lambda d: name in body_text())` bằng assertion của Playwright.
4. Vì sao `get_by_role("link", name=...)` tốt hơn `a[href*='/cart']`?

---

## Day 6 – Tracing, Network Interception, Authentication State, Parallel Execution & Reporting

Unit 2 · LO3 · Concept/Lecture · 120 phút · Virtual · Code: repo `sauce-demo-unit2-playwright`

Day 6 thêm năm khả năng mà Unit 1 chưa có: trace đầy đủ cho mỗi test fail, kiểm soát lưu lượng network, dùng lại phiên đăng nhập, chạy song song, và báo cáo vẫn đúng khi chạy song song.

### 1. Tracing (mở rộng ảnh chụp khi fail của Unit 1)

Cấu hình một lần trong `pytest.ini`:

```ini
addopts =
    --tracing retain-on-failure
    --screenshot only-on-failure
    --video retain-on-failure
    --output test-results
```

| Unit 1 | Unit 2 |
| --- | --- |
| `after_step` lưu một ảnh PNG | `test-results/<test>/trace.zip`, `test-failed-1.png`, `video.webm` |
| Chỉ thấy màn hình cuối | Mọi action, DOM trước/sau, console, network, dòng code |

Mở trace:

```bash
playwright show-trace test-results/<thư-mục-test>/trace.zip
```

Khi debug muốn có trace cho mọi test: `pytest --tracing on`.

### 2. Chặn và giả lập network

#### 2.1 Chặn request bên thứ ba (fixture autouse)

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

Cho phép: host của store và `*.shopify.com`, `*.myshopify.com`, `*.shopifycdn.com`. Mọi host khác (Facebook, Twitter, Pinterest, ứng dụng Sauce) bị hủy. Nhờ vậy rủi ro R09 (kiểm thủ công ở Unit 1) trở thành REQ-09, được test tự động.

#### 2.2 Bốn test network (`tests/test_network.py`)

| Test | Kỹ thuật | REQ / Risk |
| --- | --- | --- |
| `test_third_party_calls_are_blocked_and_shop_still_works` | `context.route` + abort, rồi chạy luồng giỏ hàng | REQ-09 / R09 |
| `test_add_to_cart_posts_the_product_form` | `page.expect_request(...)`: kiểm tra method và body | REQ-01 / R01 |
| `test_failed_add_to_cart_request_does_not_add_the_product` | `page.route(...).fulfill(status=500)`: giả lập lỗi server | REQ-01 / R01 |
| `test_catalog_loads_on_a_slow_network` | CDP của Chromium `Network.emulateNetworkConditions` (trễ 400 ms) | REQ-06 / R05 |

Ví dụ giả lập lỗi:

```python
page.route("**/cart/add*", lambda route: route.fulfill(status=500, body="Internal Server Error"))
shop.product.open_product(products["Noir jacket"]["handle"])
shop.product.add_button.click()
page.unroute("**/cart/add*")
expect(shop.cart.open().quantity_inputs).to_have_count(0)
```

### 3. Lưu trạng thái đăng nhập

Unit 1 gõ thông tin đăng nhập ở mọi scenario cần đăng nhập. Unit 2 đăng nhập một lần mỗi session và lưu cookie, localStorage:

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

Được dùng trong `tests/test_auth_state.py` (REQ-10). File `.auth/customer.json` chứa phiên đăng nhập: không được đưa lên git.

```bash
# Linux/macOS
SAUCE_EMAIL=you@example.com SAUCE_PASSWORD='...' python run.py auth
# Windows PowerShell
$env:SAUCE_EMAIL="you@example.com"; $env:SAUCE_PASSWORD="..."; python run.py auth
```

### 4. Chạy song song

```bash
python run.py parallel        # = pytest -n auto (pytest-xdist)
pytest -n 4
```

Chạy song song an toàn vì mỗi test có context riêng (Day 5) và không test nào phụ thuộc test khác. Store demo dùng chung nên trên site thật để `-n` nhỏ.

### 5. Mẫu báo cáo

| Báo cáo | Tạo bởi | Đường dẫn |
| --- | --- | --- |
| HTML | pytest-html (`--html` trong `pytest.ini`) | `reports/report.html` |
| JUnit XML | `--junitxml` | `reports/junit.xml` |
| Trace, ảnh, video | pytest-playwright | `test-results/` |
| Ma trận truy vết | hook trong `conftest.py` | `reports/traceability.md` |

Hook truy vết đọc tag Gherkin (`@REQ-01`, `@R01`) và marker `req()` / `risk()` của test thường. Khi chạy xdist, bước collect diễn ra ở worker, nên mã REQ/Risk được gửi kèm qua `item.user_properties` để tiến trình điều phối ghi ma trận:

```python
def pytest_collection_modifyitems(items):
    for item in items:
        names = [m.name for m in item.iter_markers()]
        reqs = sorted({n for n in names if re.fullmatch(r"REQ-\d+", n)} | {m.args[0] for m in item.iter_markers("req")})
        risks = sorted({n for n in names if re.fullmatch(r"R\d+", n)} | {m.args[0] for m in item.iter_markers("risk")})
        item.user_properties.append(("reqs", reqs or ["(none)"]))
        item.user_properties.append(("risks", risks))
```

### 6. Câu hỏi ôn tập

1. Trace cho thấy những gì mà ảnh chụp không cho thấy?
2. Vì sao `block_third_party` là autouse, và test muốn bỏ qua thì làm thế nào?
3. Vì sao `customer_state` phải có scope session, và vì sao `.auth/` không được đưa lên git?
4. Vì sao khi dùng `-n` thì ma trận truy vết phải chuyển sang `user_properties`?

---

## Day 7 – Playwright Implementation Lab: Prioritised End-to-End Workflows with Fixtures, Tracing & Network Control

Unit 2 · LO3 · Assignment/Lab · 150 phút · Hybrid · Code: repo `sauce-demo-unit2-playwright`

Bài lab tự động hóa các ưu tiên rủi ro của Unit 1 trên Playwright: 25 test trong lần chạy mặc định (21 scenario của Unit 1 + 4 test network), thêm 2 test đăng nhập khi có tài khoản, truy vết đủ 10/10 requirement.

### 1. Luồng nghiệp vụ theo ưu tiên (từ risk register của Unit 1)

| Ưu tiên | Luồng | Risk | Test | Kỹ thuật Unit 2 |
| --- | --- | --- | --- | --- |
| P1 | Thêm vào giỏ, tổng tiền, đổi, xóa | R01 Critical (20) | 5 scenario từ `cart.feature` + 2 test network | fixture `cart_with`, `expect_request`, giả lập lỗi 500 |
| P1 | Giỏ hàng → checkout | R02 Critical (15) | 1 scenario từ `checkout.feature` | `expect(page).to_have_url` |
| P1 | Trang chi tiết, hàng hết | R03 High (12) | 2 scenario từ `product.feature` | locator theo role |
| P1 | Đăng nhập, reset mật khẩu, phiên đã lưu | R04 High (12) | 3 scenario + 2 test auth | storage state `customer_state` |
| P1 | Giá và tình trạng trên catalog | R05 High (12) | 7 dòng Examples + test mạng chậm | giới hạn băng thông qua CDP |
| P2 | Kiểm tra lỗi đăng ký | R06 Medium (9) | 1 scenario (+1 `@data-creating`) | — |
| P2 | Tìm kiếm | R07 Medium (9) | 2 scenario | — |
| P2 | Dịch vụ bên thứ ba lỗi không làm hỏng việc mua hàng | R09 Medium (6) | 1 test network | route của `block_third_party` |

R09 ở Unit 1 kiểm thủ công vì widget hay flaky; chặn chúng ở tầng network giúp rủi ro này test được.

### 2. File

| File | Vai trò |
| --- | --- |
| `tests/test_bdd_features.py` | `scenarios(".")` chạy mọi file trong `tests/features/` (Unit 1 feature files) |
| `tests/steps/shop_steps.py` | Cài đặt bằng Playwright cho mọi step của Unit 1 |
| `tests/conftest.py` | Fixture, kiểm soát network, trạng thái đăng nhập, hook truy vết |
| `tests/test_network.py` | Chặn request, kiểm tra request, giả lập lỗi, mạng chậm |
| `tests/test_auth_state.py` | Phiên đăng nhập đã lưu (REQ-10) và kiểm tra cô lập |
| `pages/` | Page Object chuyển từ Unit 1 |
| `pytest.ini` | base URL, tracing, báo cáo, bộ lọc marker mặc định, thư mục feature |
| `run.py` | Các chế độ `smoke`, `parallel`, `auth`, `stability`, `review` |

### 3. Chạy bài lab

```bash
cd sauce-demo-unit2-playwright
pip install -r requirements.txt
playwright install chromium
python run.py                  # bộ mặc định
python run.py smoke            # @smoke: thêm vào giỏ + checkout
python run.py parallel         # pytest -n auto
python run.py auth             # cần SAUCE_EMAIL / SAUCE_PASSWORD
pytest -m R01                  # mọi test của rủi ro R01 (tag Gherkin hoặc marker)
pytest -m "critical and not negative"
```

### 4. Kết quả mong đợi

| Kiểm tra | Kết quả |
| --- | --- |
| `python run.py` | 25 pass, 3 bị lọc (`@auth` ×2, `@data-creating` ×1) |
| `python run.py parallel` | 25 pass, cùng ma trận truy vết |
| `python run.py auth` (có tài khoản) | 2 pass |
| `reports/traceability.md` | REQ-01…REQ-09 có test trong lần chạy mặc định; REQ-10 hiện "no test ran in this session" tới khi chạy `auth` |
| Test fail | `test-results/<test>/trace.zip`, ảnh, video |

Đã chạy trên site giả lập cấu trúc Shopify. Khi chạy trên store thật, kiểm tra locator trước (phát hiện F2 của Unit 1).

### 5. Nhiệm vụ lab

1. Thêm test giả lập lỗi: trang giỏ hàng trả 503. Khách hàng phải thấy gì? Viết assertion.
2. Làm `test_catalog_loads_on_a_slow_network` fail bằng cách giảm timeout xuống 1 giây, mở trace và tìm request chậm.
3. Thêm một scenario vào `tests/features/search.feature`. Chạy ở repo này và repo Unit 1: phải sửa code nào? (Đáp án: không phải sửa, trừ khi câu step là câu mới.)
4. Chạy `python run.py parallel` ba lần, so thời gian với chạy tuần tự.

---

## Day 8 – Topic Revision + Playwright Reliability & Maintainability: Failure Analysis, Flaky-Test Control, Tracing Diagnostics

Unit 2 · LO3 · Guides/Review (60 phút) + Concept/Lecture (120 phút) · Virtual · Code: repo `sauce-demo-unit2-playwright`

Day 8 khép lại cả hai Unit: phần A ôn tập Unit 2 so với Unit 1; phần B biến việc kiểm tra độ ổn định (phát hiện F3 của Unit 1) từ thủ công thành công cụ tự động: chạy lặp và phân loại flaky, kiểm tra tĩnh độ ổn định, và quy trình phân tích lỗi bằng trace.

### Phần A – Ôn tập (60 phút)

| Chủ đề | Unit 1 (Day 1–4) | Unit 2 (Day 5–7) |
| --- | --- | --- |
| Đặc tả | Feature Gherkin, tag rủi ro + REQ | Cùng file, chạy bằng pytest-bdd |
| Động cơ | Selenium WebDriver | Playwright (tự chờ, context) |
| Setup / teardown | Hook của behave | Fixture của pytest (`conftest.py`) |
| Cô lập | Trình duyệt mới mỗi scenario | Context mới mỗi test |
| Chờ | `WebDriverWait` | Action tự chờ, `expect()` tự thử lại |
| Bằng chứng lỗi | Ảnh chụp | Trace + ảnh + video |
| Network | Không kiểm soát | Chặn, kiểm tra, giả lập lỗi, giả lập chậm |
| Đăng nhập | Đăng nhập qua UI mỗi lần | Dùng lại storage state đã lưu |
| Tốc độ | Tuần tự | Song song `-n auto` |
| Truy vết | `scripts/traceability.py` sau khi chạy | Nằm trong hook pytest, đúng cả khi song song |
| Review | `bdd_review.py` | Cùng script + `stability_check.py` + báo cáo flaky |

Câu hỏi ôn tập:

1. Unit 2 chạy nguyên vẹn những file nào của Unit 1, và vì sao điều đó có ích?
2. Kể hai rủi ro có kỹ thuật test thay đổi ở Unit 2 và giải thích.
3. Phát hiện review nào của Unit 1 được công cụ Unit 2 xử lý? (F3 độ ổn định; F5 requirement dùng chung; F7 và F8 phát hiện khi kiểm tra lại.)

### Phần B – Độ tin cậy và khả năng bảo trì (120 phút)

#### B1. Quy trình phân tích lỗi

```text
test fail
 ├─ 1. đọc thông điệp assertion trong reports/report.html
 ├─ 2. mở test-results/<test>/trace.zip   (playwright show-trace)
 │     ├─ tab Actions: step nào, locator nào, chờ bao lâu
 │     ├─ Snapshots: DOM trước/sau action
 │     └─ tab Network: mã trạng thái, request chậm hoặc lỗi
 ├─ 3. phân loại
 │     ├─ lỗi sản phẩm   → sai giá, sai tổng, trang lỗi → báo bug kèm trace
 │     ├─ lỗi test       → locator đổi, giả định sai → sửa trong pages/ hoặc tests/steps/
 │     └─ môi trường     → store sập, captcha, mạng → chạy lại sau, gắn @manual nếu kéo dài
 └─ 4. chạy lại pass mà không sửa gì → flaky: xem B2
```

#### B2. Kiểm soát test flaky

```bash
python run.py stability --runs 3      # chạy cả bộ 3 lần, ghi reports/runs/run_N.xml
                                      # rồi scripts/flaky_report.py → reports/flaky_report.md
```

`scripts/flaky_report.py` phân loại từng test:

| Trạng thái | Ý nghĩa | Hành động |
| --- | --- | --- |
| stable-pass | pass mọi lần | — |
| stable-fail | fail mọi lần | lỗi thật hoặc test hỏng: phân tích trace |
| flaky | lúc pass lúc fail | cách ly, tìm nguyên nhân gốc |

Cách ly trong lúc tìm nguyên nhân (đã cài pytest-rerunfailures):

```python
@pytest.mark.flaky(reruns=2, reruns_delay=1)   # tạm thời, ghi số ticket trong commit
def test_something_flaky(...):
    ...
```

Chạy lại sẽ che giấu vấn đề, nên đây chỉ là nhãn tạm, không bao giờ đặt `--reruns` mặc định cho cả bộ.

Nguyên nhân hay gặp và cách code này xử lý:

| Nguyên nhân | Cách xử lý trong repo |
| --- | --- |
| Chờ cố định | Không dùng; chỉ `expect()` và `wait_for_url` |
| Action sau chạy trước khi request trước xong | `BasePage.submit()` chờ chuyển trang sau mỗi nút submit form; thêm vào giỏ còn chờ response `/cart/add` (phát hiện F7, F8 của Unit 1: ảnh lỗi cho thấy giỏ hàng cũ) |
| Script bên thứ ba | Fixture autouse `block_third_party` |
| Trạng thái dùng chung giữa các test | Mỗi test một context; `test_auth_state_does_not_leak_into_other_tests` |
| Selector theo vị trí | Bị `stability_check.py` chặn |

#### B3. Kiểm tra tĩnh độ ổn định

```bash
python run.py review     # 1. scripts/bdd_review.py (từ Unit 1) trên tests/features/ và tests/steps/
                         # 2. scripts/stability_check.py trên test và pages của Unit 2
```

`scripts/stability_check.py` báo lỗi (mã thoát 1) khi gặp:

| Quy tắc | Lý do |
| --- | --- |
| `wait_for_timeout(` / `time.sleep(` | Chờ cố định vừa chậm vừa vẫn flaky |
| `force=True` | Che đi phần tử mà người dùng không bấm được |
| `:nth-child`, `nth=`, `.nth(`, `)[n]` trong test | Hỏng khi bố cục thay đổi |
| CSS/XPath thô trong test | Locator phải nằm trong `pages/` |
| Test thường thiếu `req()` / `risk()` | Làm mất truy vết |

#### B4. Tiêu chí bảo trì (checklist)

- [ ] Mọi requirement trong `dataset/requirements.json` có ít nhất một test (`reports/traceability.md`)
- [ ] Gherkin vẫn declarative (`bdd_review.py` pass)
- [ ] Không có locator ngoài `pages/`
- [ ] Không chờ cố định, không `force=True` (`stability_check.py` pass)
- [ ] 0 test flaky trong 3 lần chạy liên tiếp (`flaky_report.md`)
- [ ] Mỗi lần fail đều có trace, ảnh và video
- [ ] Bộ test pass với `-n auto`
- [ ] Thông tin bí mật (`SAUCE_PASSWORD`, `.auth/`) không bao giờ đưa lên git

### Kết quả mong đợi

| Kiểm tra | Kết quả trên site giả lập |
| --- | --- |
| `python run.py review` | 0 phát hiện ở cả hai bước |
| `python run.py stability --runs 2` | 25 test, 0 flaky, 0 luôn fail |
| Cố ý làm fail | `trace.zip`, `test-failed-1.png`, `video.webm` trong `test-results/` |
