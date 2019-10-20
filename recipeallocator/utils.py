"""
Utility functions.
"""

import numpy as np


def flatten_dict(d, level=0):
    """
    Flatten a nested dictionary into a list of {level: key/value} dictionaries.

    Parameters
    ----------
    d : dict
        Nested dictionary.
    level : int
        Level to start from. Should always be 0 unless called recursively.
    Returns
    ----------
    docs : list
        List of {level: key/value} dictionaries.
    """

    docs = []
    for k, v in d.items():
        if isinstance(v, dict):
            sub_docs = flatten_dict(v, level=level + 1)
            for doc in sub_docs:
                doc[level] = k
            docs += sub_docs
        else:
            docs.append({level + 1: v, level: k})

    return docs


def string_to_number(obj):
    """
    If obj is a string of the form "num_.*", converts num to an int
    for num in {"one", "two", "three", "four", "five"}.
    Otherwise returns obj.

    Parameters
    ----------
    obj : any
        Object to convert.
    Returns
    ----------
    any
        Integer if obj takes the necessary form, otherwise obj.
    """

    numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    if isinstance(obj, str):
        num = obj.split("_")[0]
        if num in numbers.keys():
            return numbers[num]
        else:
            return obj
    else:
        return obj


def flatten_orders(orders):
    """
    Flatten orders dictionary into list of customer subsets

    Parameters
    ----------
    orders : dict
        orders dict, loaded from json.
    Returns
    ----------
    orders : list
        List of customer subsets.
    """

    orders = flatten_dict(orders)

    # Clean up keys and values
    fields = {0: "box_type", 1: "recipe_count", 2: "portion_count", 3: "customers"}
    orders = [{fields[k]: string_to_number(v) for k, v in o.items()} for o in orders]

    return orders


def flatten_stock(stock):
    """
    Flatten stock dictionary into list of recipes

    Parameters
    ----------
    stock : dict
        stock dict, loaded from json.
    Returns
    ----------
    stock : list
        List of recipes in stock.
    """

    stock = [{"recipe_name": k, **v} for k, v in stock.items()]

    return stock


def shannon_entropy(counts):
    """
    Calculates the Shannon entropy of a set of items.

    Parameters
    ----------
    counts : numpy.array
        Stock counts of each item.
    Returns
    ----------
    float
        Shannon entropy of the items.
    """

    counts = counts[counts>0]
    probs = counts/counts.sum()

    return (-counts * probs * np.log(probs)).sum()
