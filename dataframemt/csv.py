from basemt import logger
logger.debug_call_stack()
logger.warning("Module dataframemt.csv is deprecated. Please use module pandasmt.csv instead.")
from pandasmt.csv import *
