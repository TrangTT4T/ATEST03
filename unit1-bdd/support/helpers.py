"""Helpers shared by step modules (kept outside features/steps so behave never loads them twice)."""


def product(context, name):
    """Look up test data by product name; fail loudly on an unknown name."""
    try:
        return context.products[name]
    except KeyError:
        raise AssertionError(f"Unknown product {name!r}: add it to shared/products.json")


def page(context, cls):
    """Build a Page Object bound to this scenario's browser."""
    return cls(context.driver, context.base_url, context.timeout)
