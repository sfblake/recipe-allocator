"""
Functions for generating test data.
"""

from .utils import *
import numpy as np


def generate_data(customer_lims=(10, 100), num_veg=8, num_gourmet=22, extra_stock=0):
    """
    Generate order and stock data.

    Parameters
    ----------
    customer_lims : tuple (min, max+1)
        Allowed range of customer numbers, per subcategory.
    num_veg : int
        Number of vegetarian recipes.
    num_gourmet : int
        Number of gourmet recipes
    extra_stock : int
        Amount of extra stock to add or remove (if negative).
    Returns
    ----------
    orders : dict
        Order dictionary
    stock : dict
        Stock dictionary
    possible : bool
        True if orders can be met, False if they cannot
    """
    box_type = ["vegetarian", "gourmet"]
    recipe_count = ["two_recipes", "three_recipes", "four_recipes"]
    portion_count = ["two_portions", "four_portions"]

    assert num_veg >= 4, "Not enough vegetarian recipes"

    # Generate random orders
    orders = {}
    for b in box_type:
        orders[b] = {}
        for r in recipe_count:
            orders[b][r] = {}
            for p in portion_count:
                orders[b][r][p] = np.random.randint(*customer_lims)

    # Generate stock dictionary
    stock = {}
    for i in range(1, num_veg + 1):
        stock["recipe_{}".format(i)] = {'stock_count': 0, 'box_type': 'vegetarian'}
    for i in range(num_veg + 1, num_gourmet + num_veg + 1):
        stock["recipe_{}".format(i)] = {'stock_count': 0, 'box_type': 'gourmet'}

    # Fill in stock dictionary to match orders
    veg_recipes = [k for k, v in stock.items() if v["box_type"] == "vegetarian"]
    all_recipes = [k for k, v in stock.items()]  # Non-veg customers can have both veg and non-veg boxes
    for order in flatten_orders(orders):
        for i in range(order["customers"]):
            # Select random, non-repeating recipes
            if order["box_type"] == "vegetarian":
                recipes = np.random.choice(veg_recipes, order["recipe_count"], replace=False)
            else:
                recipes = np.random.choice(all_recipes, order["recipe_count"], replace=False)
            for r in recipes:
                stock[r]["stock_count"] += order["portion_count"]

    # Add extra stock
    if extra_stock >= 0:
        possible = True
        for i in range(1, extra_stock + 1):
            r = np.random.choice(all_recipes)
            stock[r]["stock_count"] += 1
    else:
        possible = False
        for i in range(extra_stock, 0):
            r = np.random.choice(all_recipes)
            stock[r]["stock_count"] -= 1

    return orders, stock, possible
