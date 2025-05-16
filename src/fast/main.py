from typing import Annotated

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from fast.coffee.coffee_maker import CoffeeMaker
from fast.coffee.menu import Menu
from fast.coffee.money_machine import MoneyMachine

money_machine = MoneyMachine()
coffee_maker = CoffeeMaker()
menu = Menu()
app = FastAPI()


def order_button(item_name: str) -> str:
    """Check for enough resources for each of the drink types, labels each button with drink type and cost."""
    enabled = coffee_maker.is_resource_sufficient(menu.find_drink(item_name))
    drink_ordered = menu.find_drink(item_name)

    return f"""
    <button style="font-size: 1.2rem; width: 25%;" {"" if enabled else "disabled"}
        name="menu_item" value="{item_name}" type="submit">{drink_ordered.name} - ${drink_ordered.cost}
    </button>
    """


def order_form() -> str:
    """Submit order back to website."""
    buttons = "\n".join([order_button(item) for item in menu.get_items()])
    return f"""<form method="post">
    {buttons}
    </form>
"""


# #def coin_input(?):
#     ""

# def payment_form():
#     money = coin_input(coin) for coin in money_machine.COIN_VALUES[coins??]
#     return f"""<form method="post">
#     {money}
#     </form>"""


def index() -> str:
    """Website outline."""
    return f"""
<!DOCTYPE html>
<html data-theme="dark">
<head>
<title>Dan's Coffee Shop</title>
</head>
<body>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@latest/css/pico.min.css">

<h1>Please Pick Your Drink</h1>
{order_form()}
</body>
</html>
"""


def report_format() -> str:
    """Format the report for user readability."""
    report = coffee_maker.report()
    return "<br>".join(f"{k}: {v}" for k, v in report.items())


def report() -> str:
    """Render the report on the webpage."""
    return f"""
<!DOCTYPE html>
<html data-theme="dark">
<head>
<title>Dan's Coffee Shop Inventory</title>
</head>
<body>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@latest/css/pico.min.css">
<h1>{report_format()}</h1>
</body>
</html>
"""


@app.get("/")
def get_index() -> HTMLResponse:
    """Display the main page to the customer."""
    return HTMLResponse(index())


@app.get("/report")
def get_report() -> HTMLResponse:
    """Display an inventory report."""
    return HTMLResponse(report())


@app.post("/")
async def submit_drink(menu_item: Annotated[str, Form()]) -> HTMLResponse:
    """Return the drink choice to the machine."""
    drink_ordered = menu.find_drink(menu_item)
    coffee_maker.make_coffee(drink_ordered)
    return HTMLResponse(index())
