from recipeallocator.algorithm import satisfy_order
from recipeallocator.data import generate_data


def test_algorithm():

    # Test case 1: check prioritisation of larger portions
    stock = {'recipe_1': {'stock_count': 2, 'box_type': 'vegetarian'},
             'recipe_2': {'stock_count': 2, 'box_type': 'vegetarian'},
             'recipe_3': {'stock_count': 4, 'box_type': 'vegetarian'},
             'recipe_4': {'stock_count': 4, 'box_type': 'vegetarian'},
             'recipe_5': {'stock_count': 0, 'box_type': 'gourmet'}}
    orders = {'vegetarian': {'two_recipes': {'two_portions': 0, 'four_portions': 1},
                             'three_recipes': {'two_portions': 0, 'four_portions': 0},
                             'four_recipes': {'two_portions': 0, 'four_portions': 0}},
              'gourmet': {'two_recipes': {'two_portions': 1, 'four_portions': 0},
                          'three_recipes': {'two_portions': 0, 'four_portions': 0},
                          'four_recipes': {'two_portions': 0, 'four_portions': 0}}}
    assert satisfy_order(stock, orders) is True

    # Test case 2: check diversity of recipes, check vegetarian orders are all vegetarian
    stock = {'recipe_1': {'stock_count': 10000, 'box_type': 'vegetarian'},
             'recipe_2': {'stock_count': 10000, 'box_type': 'vegetarian'},
             'recipe_3': {'stock_count': 0, 'box_type': 'vegetarian'},
             'recipe_4': {'stock_count': 10000, 'box_type': 'vegetarian'},
             'recipe_5': {'stock_count': 10000, 'box_type': 'gourmet'}}
    orders = {'vegetarian': {'two_recipes': {'two_portions': 0, 'four_portions': 0},
                             'three_recipes': {'two_portions': 0, 'four_portions': 0},
                             'four_recipes': {'two_portions': 0, 'four_portions': 1}},
              'gourmet': {'two_recipes': {'two_portions': 0, 'four_portions': 0},
                          'three_recipes': {'two_portions': 0, 'four_portions': 0},
                          'four_recipes': {'two_portions': 0, 'four_portions': 1}}}
    assert satisfy_order(stock, orders) is False

    # Random test cases: generate random stock and orders, see if the algorithm gets them right
    for extra_stock in [-10,-1,0,1,10]:
        orders, stock, possible = generate_data(customer_lims=(100, 200), extra_stock=extra_stock)
        assert satisfy_order(stock, orders) is possible
