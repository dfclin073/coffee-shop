from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Annotated, Any

from beanie import Document, init_beanie
from fastapi import Depends, FastAPI, Form
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from fast.coffee.coffee_maker import CoffeeMaker
from fast.coffee.menu import Menu
from fast.coffee.money_machine import MoneyMachine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(database=client.CoffeeShop, document_models=[Drinks, Ingredients])
    yield


app = FastAPI(lifespan=lifespan)
mongoip = "mongodb://localhost:27017"
client = AsyncIOMotorClient[Any](mongoip)


class Drinks(Document):
    name: str
    water: int
    milk: int
    coffee: int
    cost: float

    class Settings:
        name = "menu"


class Ingredients(Document):
    water: int
    milk: int
    coffee: int

    class Settings:
        name = "resources"


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


def order_button(item_name: str, coffee_maker: CoffeeMaker, menu: Menu) -> str:
    """Check for enough resources for each of the drink types, labels each button with drink type and cost."""
    enabled = coffee_maker.is_resource_sufficient(menu.find_drink(item_name))
    drink_ordered = menu.find_drink(item_name)
    return f"""
    <button style="font-size: 1.2rem; width: 25%;" {"" if enabled else "disabled"}
        name="menu_item" value="{item_name}" type="submit">{drink_ordered.name} - ${drink_ordered.cost}
    </button>
    """


def order_form(menu: Menu, coffee_maker: CoffeeMaker) -> str:
    """Submit order back to website."""
    buttons = "\n".join([order_button(item, coffee_maker, menu) for item in menu.get_items()])
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


def payment_form(drink: str, cost: Decimal, money_machine: MoneyMachine) -> str:
    """Submit money back to website."""
    num_field = "\n".join(coin_input(coin) for coin in money_machine.COIN_VALUES)
    return f"""<form method="post" action="/payment">
    {num_field}
    <input type="hidden" id="cost" name="cost" value="{cost}">
    <input type="hidden" id="drink" name="drink" value="{drink}">
    <button style="font-size: 1.2rem; width: 25%;" type="submit" > Submit</button>
    </form>
    """


def index(menu: Menu, coffee_maker: CoffeeMaker) -> str:
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
{order_form(menu, coffee_maker)}
</body>
</html>
"""


def drink_ready(money_back: Decimal, drink: str) -> str:
    """Receipt page."""
    return f"""
<!DOCTYPE html>
<html data-theme="auto">
<head>
<title>Dan's Coffee Shop</title>
</head>
<body>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@latest/css/pico.min.css">
<h1>Your change is ${money_back}<h1>
<h1>Here's Your {drink}</h1>
<img src="https://images.immediate.co.uk/production/volatile/sites/30/2020/08/flat-white-3402c4f.jpg?quality=90&webp=true&resize=300,272" alt="Your Drink">
</body>
</html>
"""


def no_funds(cost: Decimal, drink: str, paid: Decimal) -> str:
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


def payment(drink_name: str, cost: Decimal, money_machine: MoneyMachine) -> str:
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
{payment_form(drink_name, cost, money_machine)}
</body>
</html>
"""


async def get_coffee_maker() -> AsyncGenerator[CoffeeMaker, Any]:
    coffee_maker_id = "682e2e3ae2942466ade0077b"
    ingredients = await Ingredients.get(coffee_maker_id)
    if not ingredients:
        raise ValueError(f"Could not find ingredients for this coffee maker {coffee_maker_id}")
    ingredients_dict = ingredients.model_dump(exclude={"id"})
    coffee_maker = CoffeeMaker(ingredients_dict)
    yield coffee_maker
    updated_values = coffee_maker.report()
    for key, val in updated_values.items():
        setattr(ingredients, key, val)
        # update ingredients here. for loop to take items form .report and add them back to ingredients.
    await ingredients.save()


async def get_money_machine() -> MoneyMachine:
    return MoneyMachine()


async def get_menu() -> Menu:
    return Menu()


@app.get("/")
def get_index(
    menu: Annotated[Menu, Depends(get_menu)],
    coffee_machine: Annotated[CoffeeMaker, Depends(get_coffee_maker)],
) -> HTMLResponse:
    """Display the main page to the customer."""
    return HTMLResponse(index(menu, coffee_machine))


@app.post("/")
async def submit_drink(
    menu_item: Annotated[str, Form()],
    menu: Annotated[Menu, Depends(get_menu)],
    coffee_machine: Annotated[CoffeeMaker, Depends(get_coffee_maker)],
    money_machine: Annotated[MoneyMachine, Depends(get_money_machine)],
) -> HTMLResponse:
    """Return the drink choice to the machine."""
    drink_ordered = menu.find_drink(menu_item)
    coffee_machine.make_coffee(drink_ordered)
    return HTMLResponse(payment(drink_ordered.name, drink_ordered.cost, money_machine))


# @app.get("/payment")
# def get_payment() -> HTMLResponse:
#     """Display the payment page to the customer."""
#     return HTMLResponse(payment)


@app.post("/payment")
async def submit_payment(
    coins: Annotated[Coins, Depends(get_coins)],
    cost: Annotated[Decimal, Form()],
    drink: Annotated[str, Form()],
    money_machine: Annotated[MoneyMachine, Depends(get_money_machine)],
) -> HTMLResponse:
    """Check payment amount complete add payment to profits."""
    coin_dict = coins.model_dump()
    change = money_machine.make_payment(cost, coin_dict)
    if change is False:
        return HTMLResponse(no_funds(cost, drink, money_machine.process_coins(coin_dict)))
    if change is True:
        raise ValueError
    return HTMLResponse(drink_ready(change, drink))


@app.get("/healthz")
async def healthz() -> dict[str, bool]:
    try:
        mongo_info = await client.server_info()
    except:
        return {"mongodb": False}
    return {"mongodb": mongo_info["ok"] == 1}


@app.get("/resources")
async def get_ingredients(coffee_machine: Annotated[CoffeeMaker, Depends(get_coffee_maker)]) -> dict[str, int]:
    return coffee_machine.report()
