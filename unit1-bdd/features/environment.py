"""behave hooks: browser lifecycle, tag handling, screenshots on failure.

Hook order per run:
  before_all -> (before_feature -> (before_tag -> before_scenario -> before_step/after_step ... -> after_scenario) ...) -> after_all
"""
import json
import os
import re
from pathlib import Path
import sys

from selenium import webdriver

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # makes pages/ and support/ importable from steps
REPORTS = ROOT / "reports"
SCREENSHOTS = REPORTS / "screenshots"


def _make_driver(browser: str, headless: bool):
    if browser == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        return webdriver.Firefox(options=options)
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    options.add_argument("--disable-dev-shm-usage")
    if os.getenv("CI") or (hasattr(os, "geteuid") and os.geteuid() == 0):
        options.add_argument("--no-sandbox")  # needed in Docker/CI containers running as root
    driver_path = os.getenv("CHROMEDRIVER_PATH")
    if driver_path:  # optional: use a local chromedriver instead of Selenium Manager
        from selenium.webdriver.chrome.service import Service
        service = Service(driver_path, service_args=os.getenv("CHROMEDRIVER_ARGS", "").split())
        return webdriver.Chrome(options=options, service=service)
    return webdriver.Chrome(options=options)  # Selenium Manager downloads the matching driver


def before_all(context):
    userdata = context.config.userdata
    context.base_url = os.getenv("BASE_URL", userdata.get("base_url", "https://sauce-demo.myshopify.com"))
    context.browser_name = os.getenv("BROWSER", userdata.get("browser", "chrome"))
    context.headless = os.getenv("HEADLESS", userdata.get("headless", "true")).lower() == "true"
    context.timeout = int(userdata.get("timeout", "10"))
    with open(ROOT / "shared" / "products.json", encoding="utf-8") as fh:  # same file in the Unit 2 repo
        context.products = json.load(fh)["products"]
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)


def before_scenario(context, scenario):
    # Tags that must never hit the pipeline are skipped here, before a browser opens.
    if {"manual", "wip"} & set(scenario.effective_tags):
        scenario.skip("Tagged @manual / @wip")
        return
    # One fresh browser per scenario = clean cookies = an empty cart (independence).
    context.driver = _make_driver(context.browser_name, context.headless)
    context.driver.implicitly_wait(0)  # explicit waits only


def after_step(context, step):
    if step.status == "failed" and getattr(context, "driver", None):
        name = re.sub(r"[^\w-]+", "_", f"{context.scenario.name}_{step.name}")[:120]
        path = SCREENSHOTS / f"{name}.png"
        context.driver.save_screenshot(str(path))
        try:  # attach to the Allure report when allure-behave is the formatter
            import allure
            allure.attach.file(str(path), name="failure", attachment_type=allure.attachment_type.PNG)
        except Exception:
            pass


def after_scenario(context, scenario):
    driver = getattr(context, "driver", None)
    if driver:
        driver.quit()
        context.driver = None
