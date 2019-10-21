# recipe-allocator
An algorithm for determining whether a set of orders can be fulfilled 
by a set of stock levels.

## Installation
Install via pip:
```
pip install git+https://github.com/sfblake/recipe-allocator
```

## Usage
The algorithm takes stock and orders data, and returns `True` if the
stock can fulfill the orders and `False` if it cannot.

It can be called on stock and order json files directly:
```
>>> from recipeallocator import satisfy_order_json
>>> satisfy_order_json("path/to/stock.json", "path/to/orders.json")
False
```
Or can be passed the data in dictionary format:
```
>>> # Generate some fulfillable stock and orders data
>>> from recipeallocator.data import generate_data
>>> orders, stock, _ = generate_data(num_veg=4, num_gourmet=2)
>>> print(orders)
{
'vegetarian': {
'two_recipes': {'two_portions': 83, 'four_portions': 69}, 
'three_recipes': {'two_portions': 51, 'four_portions': 68}, 
'four_recipes': {'two_portions': 31, 'four_portions': 50}
}, 
'gourmet': {
'two_recipes': {'two_portions': 94, 'four_portions': 37}, 
'three_recipes': {'two_portions': 87, 'four_portions': 10}, 
'four_recipes': {'two_portions': 78, 'four_portions': 79}
}
}
>>> print(stock)
{
'recipe_1': {'stock_count': 1062, 'box_type': 'vegetarian'}, 
'recipe_2': {'stock_count': 1086, 'box_type': 'vegetarian'}, 
'recipe_3': {'stock_count': 1140, 'box_type': 'vegetarian'}, 
'recipe_4': {'stock_count': 1122, 'box_type': 'vegetarian'}, 
'recipe_5': {'stock_count': 386, 'box_type': 'gourmet'}, 
'recipe_6': {'stock_count': 390, 'box_type': 'gourmet'}
}
>>> # Call the algorithm
>>> from recipeallocator import satisfy_order
>>> satisfy_order(stock, orders)
True
```

## Overview

### Operation
**recipe-allocator** is an algorithm for determining whether a set of
orders can be fulfilled by a set of stock levels. 

The stock is the number of unique recipes, each of which
have a certain number of units in stock and can be
either vegetarian or gourmet.

The orders are the total number of customer orders, for every
customer category. These categories split the customer base by number
of portions, number of recipes, and whether these recipes must be
vegetarian.

Examples of both the stock and orders data are given in the usage
example above.

When allocating stock to customers, there are three rules which must
be adhered to:
1. Each customer must receive the correct amount of units - both the 
number of recipes and the number of portions per recipe.
2. The recipes sent to each customer must all be different.
3. Vegetarian customers may not receive non-vegetarian (gourmet)
recipes. (Gourmet customers may receive vegetarian recipes.)

If all the orders can be fulfilled by the stock levels (while
adhering to the above rules) the algorithm returns `True`, otherwise
it returns `False`.

### Approach
The algorithm's approach is simple: it assigns recipes to customers
until either it runs out of stock (and so returns `False`) or it runs
out of customers (and so returns `True`).

However for this approach to work, the algorithm must assign stock
to customers in the optimal way, so it can fulfill as many orders as
possible. In determining the optimal way to assign stock, there are
two things which the algorithm must consider:
1. For a given customer, which recipes should be chosen to maximise
the options for the remaining customers?
2. In what order should the customers be processed?

#### 1. Recipe choice
As a measure of the number of options remaining, we can quantify the 
diversity of the stock levels using the Shannon entropy:  

![equation](https://latex.codecogs.com/gif.latex?%24%24H%20%3D%20-%20%5Csum_%7Bi%7DP_%7Bi%7D%20%5C%2C%20%5Ctextup%7Blog%7D%28P_%7Bi%7D%29%24%24)  

where ![equation](https://latex.codecogs.com/gif.latex?%24%24P_%7Bi%7D%24%24)
is the proportion of stock levels belonging to  recipe _i_. (This is 
only an approximate measure of the number of options as it  does not 
take into account the portion counts of the remaining  orders).

To give an example:  
Let's say we have 10 recipes and 100 units of stock. The diversity
will be lowest when all 100 units are of the same recipe:

![equation](https://latex.codecogs.com/gif.latex?%24%24H%20%3D%20-%20%5Csum_%7Bi%7DP_%7Bi%7D%20%5C%2C%20%5Ctextup%7Blog%7D%28P_%7Bi%7D%29%20%3D%20-%201%20%5C%2C%20%5Ctextup%7Blog%7D%281%29%20%3D%200%24%24)

And highest when each recipe has the same number of units (10):

![equation](https://latex.codecogs.com/gif.latex?%24%24H%20%3D%20-%20%5Csum_%7Bi%7DP_%7Bi%7D%20%5C%2C%20%5Ctextup%7Blog%7D%28P_%7Bi%7D%29%20%3D%20-%20%5Csum_%7Bi%3D1%7D%5E%7B10%7D0.1%20%5C%2C%20%5Ctextup%7Blog%7D%280.1%29%20%3D%201%24%24)

In order to maximise the diversity of the stock levels, the algorithm 
must choose the recipes for each customer that balance the remaining 
stock levels as evenly as possible across the recipes. In other 
words, the algorithm must choose the recipes (of those allowed) with 
the highest current stock levels.

#### 2. Customer order
Because the above procedure aims to maximise the diversity of the
remaining stock levels, the algorithm must always process the
customers with the largest portions first. Otherwise situations may
arise where the stock levels are diverse but too small to be used
(`stock_count<num_portions`).

As vegetarian customers are limited to vegetarian recipes (while
gourmet customers can receive any), they are processed before gourmet
customers (with the same portion size). Furthermore, to leave as many
recipes as possible available for the remaining vegetarian customers,
the algorithm tries first to fulfill gourmet orders with only gourmet 
recipes. Only when this is not possible does it include vegetarian
recipes.

Finally, the algorithm prioritises the customers with the largest 
number of recipes, as these need the widest range of recipes to
choose from.

Putting the above together, the first five customer categories
processed would be:  
_vegetarian_, _four_recipes_, _four_portions_  
_vegetarian_, _three_recipes_, _four_portions_  
_vegetarian_, _two_recipes_, _four_portions_  
_gourmet_, _four_recipes_, _four_portions_  
_gourmet_, _three_recipes_, _four_portions_  

### Potential risks
The algorithm is designed to handle any numbers of recipes in stock,
and anywhere between 1 and 5 recipes and portions for a customer 
(this requires a string to int conversion for the specified data
format, hence the fixed range). Only the default options of {2,4}
portions and {2,3,4} recipes are covered by the test cases however.

Running locally, computation time for complete allocation scales
linearly with the number of recipe units, taking approximately 1s per
million units with the default number of recipes. Assuming an upper 
limit of 450 million units (7 meals a week x 66 million UK 
population) gives an upper run time of 7.5 minutes for the current 
implementation.

Although the algorithm is designed to return only `True` or `False`
when the orders can and cannot be met, it could also be used to
determine which recipes customers should be given - this is already
calculated as part of the algorithm's operation. However I would
advise against this. Because of the order in which the different
customer categories are processed, they will receive, on average,
different kinds of recipes: two portion gourmet customers would
receive a higher proportion of vegetarian recipes than four portion 
gourmet customers, for example. Some shuffling of recipes between
customers would be necessary to make the distribution of recipes more
random before the algorithm's recommendations could be used.