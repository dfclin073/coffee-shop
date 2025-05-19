"""
Module for working with money.

This module provides:
- coin values
- calculates generates a profits reports
- provides change to the customer
"""

from decimal import Decimal
from typing import ClassVar


class MoneyMachine:
    """Tracks money value, receives payments and calculates profits."""

    CURRENCY = "$"

    COIN_VALUES: ClassVar[dict[str, Decimal]] = {
        "Quarters": Decimal("0.25"),
        "Dimes": Decimal("0.10"),
        "Nickles": Decimal("0.05"),
        "Pennies": Decimal("0.01"),
    }

    def __init__(self) -> None:
        """Initialize the money machine with no profit and no money from customers."""
        self.profit: Decimal = Decimal("0.0")
        self.money_received: Decimal = Decimal("0.0")

    def report(self) -> Decimal:
        """Return the current profit."""
        return self.profit

    def process_coins(self, coin_amount: dict[str, int]) -> Decimal:
        """Return the sum of coins inserted."""
        for coin in self.COIN_VALUES:
            count = coin_amount.get(coin, 0)
            self.money_received += count * self.COIN_VALUES[coin]
            print(self.money_received)
        return self.money_received

    def make_payment(self, cost: Decimal, coin_amount: dict[str, int]) -> bool | Decimal:
        """Return change when payment is accepted, or False if insufficient."""
        self.process_coins(coin_amount)
        if self.money_received >= cost:
            change: Decimal = (self.money_received - cost).quantize(Decimal("0.01"))
            self.profit += cost
            self.money_received = Decimal("0.0")
            return change
        self.money_received = Decimal("0.0")
        return False
