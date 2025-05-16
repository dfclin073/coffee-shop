"""
Module for working with coffee resources.

This module provides:
- A report on available resources
- check for resources to support the ordered drink
- Deducts the resource used when making a drink
"""

from fast.coffee.menu import MenuItem


class CoffeeMaker:
    """Models the machine that makes the coffee."""

    def __init__(self) -> None:
        """Initiate the coffee maker resources."""
        self._resources = {
            "water": 300,
            "milk": 200,
            "coffee": 100,
        }

    def report(self) -> dict[str, int]:
        """Return a report of all resources."""
        return self._resources

    def is_resource_sufficient(self, drink: MenuItem) -> bool:
        """Return True when order can be made, False if ingredients are insufficient."""
        can_make = True
        for item in drink.ingredients:
            if drink.ingredients[item] > self._resources[item]:
                can_make = False
        return can_make

    def make_coffee(self, order: MenuItem) -> str:
        """Deduct the required ingredients from the resources."""
        for item in order.ingredients:
            self._resources[item] -= order.ingredients[item]
        return order.name
