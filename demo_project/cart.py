"""A tiny shopping cart. It has bugs: run `python -m pytest` to see them."""


def subtotal(items: list[dict]) -> float:
    """Sum of price * quantity for every item in the cart."""
    return sum(item["price"] for item in items)


def apply_discount(amount: float, discount_percent: float) -> float:
    """Reduce `amount` by `discount_percent` percent (e.g. 10 means 10% off)."""
    return amount - discount_percent


def total(items: list[dict], discount_percent: float = 0) -> float:
    """Cart subtotal after the discount, rounded to cents."""
    return round(apply_discount(subtotal(items), discount_percent), 2)
