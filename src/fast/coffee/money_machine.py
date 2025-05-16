"""
Module for working with money.

This module provides:
- coin values
- calculates generates a profits reports
- provides change to the customer
"""

from typing import ClassVar


class MoneyMachine:
    """Tracks money value, receives payments and calculates profits."""

    CURRENCY = "$"

    COIN_VALUES: ClassVar[dict[str, float]] = {
        "quarters": 0.25,
        "dimes": 0.10,
        "nickles": 0.05,
        "pennies": 0.01,
    }

    def __init__(self) -> None:
        """Initialize the money machine with no profit and no money from customers."""
        self.profit = float(0)
        self.money_received = float(0)

    def report(self) -> float:
        """Return the current profit."""
        return self.profit

    def process_coins(self, coin_amount: dict[str, int]) -> float:
        """Return the sum of coins inserted."""
        for coin in self.COIN_VALUES:
            count = coin_amount.get(coin, 0)
            self.money_received += count * self.COIN_VALUES[coin]
        return self.money_received

    def make_payment(self, cost: float, coin_amount: dict[str, int]) -> bool | float:
        """Return True when payment is accepted, or False if insufficient."""
        self.process_coins(coin_amount)
        if self.money_received >= cost:
            change: float = round(self.money_received - cost, 2)
            self.profit += cost
            self.money_received = 0
            return change
        self.money_received = 0
        return False
