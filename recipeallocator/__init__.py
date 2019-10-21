from .algorithm import satisfy_order, satisfy_order_json
from .settings import log_level
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=log_level)

__version__ = '0.1'
