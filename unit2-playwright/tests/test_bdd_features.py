"""Run every Unit 1 feature file on Playwright through pytest-bdd.

Nothing in the .feature files changes between units: same scenarios, same tags (@Rxx,
@critical, @smoke), same Examples. Only the step implementation moves from Selenium to Playwright.
Step definitions live in tests/steps/shop_steps.py (loaded by conftest.py).
"""
from pytest_bdd import scenarios

scenarios(".")  # "." = bdd_features_base_dir = tests/features/ (the Unit 1 feature files)
