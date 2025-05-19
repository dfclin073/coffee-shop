from decimal import Decimal, getcontext
from typing import Annotated

from fastapi import Depends, FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from fast.coffee.coffee_maker import CoffeeMaker
from fast.coffee.menu import Menu
from fast.coffee.money_machine import MoneyMachine

money_machine = MoneyMachine()
coffee_maker = CoffeeMaker()
menu = Menu()
app = FastAPI()
getcontext().prec = 28


class Coins(BaseModel):
    Quarters: Annotated[Decimal, Form()]
    Dimes: Annotated[Decimal, Form()]
    Nickles: Annotated[Decimal, Form()]
    Pennies: Annotated[Decimal, Form()]


def get_coins(
    Quarters: Annotated[Decimal, Form()],
    Dimes: Annotated[Decimal, Form()],
    Nickles: Annotated[Decimal, Form()],
    Pennies: Annotated[Decimal, Form()],
) -> Coins:
    return Coins(Quarters=Quarters, Dimes=Dimes, Nickles=Nickles, Pennies=Pennies)


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


def coin_input(num_field: str) -> str:
    """Display payment field submits payment to money_machine."""
    return f"""
    <div style="display: flex; justify-content: space-between; width: 200px;">
    <label for="{num_field}" >{num_field}:</label>
    <input style="font-size: 1.2rem; width: 100px;" type="number" value="0" id="{num_field}" name="{num_field}" min="0" max="300">
    </div>
    """


def payment_form(drink: str, cost: Decimal) -> str:
    """Submit money back to website."""
    num_field = "\n".join(coin_input(coin) for coin in money_machine.COIN_VALUES)
    return f"""<form method="post" action="/payment">
    {num_field}
    <input type="hidden" id="cost" name="cost" value="{cost}">
    <input type="hidden" id="drink" name="drink" value="{drink}">
    <button style="font-size: 1.2rem; width: 25%;" type="submit" > Submit</button>
    </form>
    """


def index() -> str:
    """Coffee order page."""
    return f"""
<!DOCTYPE html>
<html data-theme="auto">
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


def drink_ready(moneyback: Decimal, drink: str) -> str:
    """Receipt page."""
    return f"""
<!DOCTYPE html>
<html data-theme="auto">
<head>
<title>Dan's Coffee Shop</title>
</head>
<body>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@latest/css/pico.min.css">
<h1>Your change is ${moneyback}<h1>
<h1>Here's Your {drink}</h1>
<img src="https://images.immediate.co.uk/production/volatile/sites/30/2020/08/flat-white-3402c4f.jpg?quality=90&webp=true&resize=300,272" alt="Your Drink">
</body>
</html>
"""


def nofunds(cost: Decimal, drink: str, paid: Decimal) -> str:
    """Receipt page."""
    return f"""
<!DOCTYPE html>
<html data-theme="auto">
<head>
<title>Dan's Coffee Shop</title>
</head>
<body>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@latest/css/pico.min.css">
<h1>You selected {drink} which costs ${cost}<h1>
<h1>You only paid ${paid}</h1>
<img src="https://m.media-amazon.com/images/I/71ABlL4AwKL.jpg" alt="No Drink">
</body>
</html>
"""


def payment(drink_name: str, cost: Decimal) -> str:
    """Coffee payment page."""
    return f"""
<!DOCTYPE html>
<html data-theme="auto">
<head>
<title>Dan's Coffee Shop</title>
</head>
<body>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@latest/css/pico.min.css">
<h1> You Selected {drink_name}</h1>
<br>
<h1>Please Insert ${cost}</h1>
{payment_form(drink_name, cost)}
</body>
</html>
"""


def report_format() -> str:
    """Format the report for user readability."""
    report = coffee_maker.report()
    coffee_line = "<br>".join(f"{k}: {v}" for k, v in report.items())
    money_line = f"Profit: ${money_machine.report()}"
    return f"{coffee_line}<br>{money_line}"


def report() -> str:
    """Render the report on the webpage."""
    return f"""<!DOCTYPE html>
<html data-theme="auto">
<head>
<title>Dan's Coffee Shop Inventory</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@latest/css/pico.min.css">
</head>
<body>
<h1>Inventory & Profit Report</h1>
<div>{report_format()}</div>
</body>
</html>"""


@app.get("/report")
def get_report() -> HTMLResponse:
    """Display an inventory report."""
    return HTMLResponse(report())


@app.get("/")
def get_index() -> HTMLResponse:
    """Display the main page to the customer."""
    return HTMLResponse(index())


@app.post("/")
async def submit_drink(menu_item: Annotated[str, Form()]) -> HTMLResponse:
    """Return the drink choice to the machine."""
    drink_ordered = menu.find_drink(menu_item)
    coffee_maker.make_coffee(drink_ordered)
    return HTMLResponse(payment(drink_ordered.name, drink_ordered.cost))


@app.get("/payment")
def get_payment() -> HTMLResponse:
    """Display the payment page to the customer."""
    return HTMLResponse(payment)


@app.post("/payment")
async def submit_payment(
    coins: Annotated[Coins, Depends(get_coins)], cost: Annotated[Decimal, Form()], drink: Annotated[str, Form()]
) -> HTMLResponse:
    """Check payment amount complete add payment to profits."""
    coin_dict = coins.model_dump()
    change = money_machine.make_payment(cost, coin_dict)
    if change is False:
        return HTMLResponse(nofunds(cost, drink, money_machine.process_coins(coin_dict)))
    return HTMLResponse(drink_ready(change, drink))
