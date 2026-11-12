from cart import apply_discount, subtotal, total

BASKET = [
    {"name": "coffee", "price": 4.50, "quantity": 2},
    {"name": "bagel", "price": 3.00, "quantity": 1},
]


def test_empty_cart_costs_nothing():
    assert total([]) == 0


def test_subtotal_counts_quantity():
    assert subtotal(BASKET) == 12.00


def test_discount_is_a_percentage():
    assert apply_discount(200, 10) == 180


def test_total_with_discount():
    assert total(BASKET, discount_percent=25) == 9.00
