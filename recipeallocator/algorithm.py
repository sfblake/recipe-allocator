"""
The recipe allocation algorithm.
"""

from .utils import *
import numpy as np
import pandas as pd
import json


def assign_recipes(stock_count, customers, portion_count, recipe_count):
    """
    Assign recipes to customers.

    Parameters
    ----------
    stock_count : numpy.array, shape (num_recipes,)
        Stock levels for each recipe.
    customers : int
        Number of customers.
    portion_count : int
        Number of portions for these customers.
    recipe_count : int
        Number of recipes for these customers.
    Returns
    ----------
    leftover : int
        The number of customers who could not have recipes assigned.
    stock_count : numpy.array, shape (num_recipes,)
        Remaining stock levels.
    """

    # Not enough unique recipes to assign any
    if len(stock_count) < recipe_count:
        return customers, stock_count

    # Iterate through customers
    for leftover in range(customers, 0, -1):
        # Get the recipes with the most stock remaining
        most_stock = np.argpartition(stock_count, -recipe_count)[-recipe_count:]
        stock_count[most_stock] = stock_count[most_stock] - portion_count

        # If negative stock, then the demand cannot be satisfied
        if stock_count.min() < 0:
            # Add the subtracted stock back on
            stock_count[most_stock] = stock_count[most_stock] + portion_count
            return leftover, stock_count

    return 0, stock_count


def satisfy_order(stock, orders):
    """
    Determine whether stocked recipes can satisfy orders.

    Parameters
    ----------
    stock : dict
        stock dict, loaded from json.
    orders : dict
        orders dict, loaded from json.
    Returns
    ----------
    bool
        True if stock can satisfy the orders, False if not.
    """

    # Convert data to dataframes
    stockDF = pd.DataFrame(flatten_stock(stock))
    orderDF = pd.DataFrame(flatten_orders(orders))

    # Check whether there is enough stock of any kind
    total_stock = stockDF["stock_count"].sum()
    total_demand = (orderDF["customers"] * orderDF["portion_count"] * orderDF["recipe_count"]).sum()

    # If demand is greater than stock, then demand cannot be satisfied
    if total_demand > total_stock:
        return False

    stock_count = stockDF["stock_count"].values.copy()
    veg_mask = (stockDF["box_type"] == "vegetarian").values  # Mask for vegetarian recipes

    # Iterate through subsets by most portions, then vegetarian, then most recipes
    orderDF.sort_values(["portion_count", "box_type", "recipe_count"], ascending=False, inplace=True)

    # Assign orders for each customer subset
    for _, order in orderDF.sort_values(["portion_count", "recipe_count"], ascending=False).iterrows():

        if order["box_type"] == "vegetarian":
            # Vegetarian orders only
            stock_count_veg = stock_count[veg_mask].copy()
            leftover, stock_count_veg = assign_recipes(stock_count_veg, order["customers"],
                                                       order["portion_count"], order["recipe_count"])
            if leftover > 0:
                # Orders cannot be satisfied
                return False
            # Update stock
            stock_count[veg_mask] = stock_count_veg

        else:
            # Try gourmet recipes only
            stock_count_nonveg = stock_count[~veg_mask].copy()
            leftover, stock_count_nonveg = assign_recipes(stock_count_nonveg, order["customers"],
                                                          order["portion_count"], order["recipe_count"])
            # Update stock
            stock_count[~veg_mask] = stock_count_nonveg

            if leftover > 0:
                # Try gourmet and non-veg recipes for remaining customers
                stock_count_all = stock_count.copy()
                leftover, stock_count_all = assign_recipes(stock_count_all, leftover,
                                                           order["portion_count"], order["recipe_count"])
                if leftover > 0:
                    # Orders cannot be satisfied
                    return False
                # Update stock
                stock_count = stock_count_all

    return True


def satisfy_order_json(stock_file, orders_file):
    """
    Determine whether stocked recipes can satisfy orders, from json data.

    Parameters
    ----------
    stock_file : str
        Path to json stock file.
    orders_file : str
        Path to json orders file.
    Returns
    ----------
    bool
        True if stock can satisfy the orders, False if not.
    """

    stock = json.load(open(stock_file, "rb"))
    orders = json.load(open(orders_file, "rb"))

    return satisfy_order(stock, orders)
