"""
Module for working with drinks and ingredients.

This module provides:
- a list of menu items
- a data class of ingredients and their types
- looks up the users requested order and check if its on the menu
"""


class MenuItem:
    """Models each Menu Item."""

    def __init__(
        self, name: str, water: int, milk: int, coffee: int, cost: float
    ) -> None:
        """Initialize the menu items and their ingredient types."""
        self.name = name
        self.cost = cost
        self.ingredients = {"water": water, "milk": milk, "coffee": coffee}


class Menu:
    """Models the Menu with drinks."""

    def __init__(self) -> None:
        """Initialize the drinks and their ingredients with the amount need."""
        self.menu = [
            MenuItem(name="Latte", water=200, milk=150, coffee=24, cost=2.50),
            MenuItem(name="Espresso", water=50, milk=0, coffee=18, cost=1.50),
            MenuItem(name="Cappuccino", water=250, milk=50, coffee=24, cost=3.00),
        ]

    def get_items(self) -> list[str]:
        """Return all the names of the available menu items."""
        return [item.name for item in self.menu]

    def find_drink(self, order_name: str) -> MenuItem:
        """Search the menu for a drink. Returns item if it exists, else returns None."""
        for item in self.menu:
            if item.name == order_name:
                return item
        raise DrinkNotFoundError


class DrinkNotFoundError(Exception):
    """Error handling for when user requests a drink not found in the menu."""
