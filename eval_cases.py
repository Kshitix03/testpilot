# Each case is an English instruction the agent must turn into a passing test.
# Deliberately varied in difficulty so the scoreboard shows something interesting.

CASES = [
    {
        "id": 1,
        "instruction": "Log in to saucedemo.com and verify the inventory page loads",
    },
    {
        "id": 2,
        "instruction": "Log in to saucedemo.com and verify the page title says 'Swag Labs'",
    },
    {
        "id": 3,
        "instruction": "Log in to saucedemo.com and verify there are 6 products on the inventory page",
    },
    {
        "id": 4,
        "instruction": "Log in to saucedemo.com and add the first product to the cart",
    },
    {
        "id": 5,
        "instruction": "Log in to saucedemo.com, add one product to the cart, and verify the cart badge shows the number 1",
    },
    {
        "id": 6,
        "instruction": "Log in to saucedemo.com and sort the products by price low to high",
    },
    {
        "id": 7,
        "instruction": "Log in to saucedemo.com and click on the first product to open its detail page",
    },
    {
        "id": 8,
        "instruction": "Log in to saucedemo.com, navigate to the cart, and verify the cart is empty",
    },
    {
        "id": 9,
        "instruction": "Go to saucedemo.com, enter the wrong password, and verify an error message appears",
    },
    {
        "id": 10,
        "instruction": "Log in to saucedemo.com and open the side navigation menu",
    },
    {
        "id": 11,
        "instruction": "Log in to saucedemo.com, add an item to the cart, click checkout, and verify the checkout form appears",
    },
    {
        "id": 12,
        "instruction": "Log in to saucedemo.com and verify the footer contains a link to Twitter",
    },
]
