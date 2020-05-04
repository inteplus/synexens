'''Useful modules for accessing MySQL'''

from mt.base import logger
logger.warn_module_move('sqlmt.mysql', 'mt.sql.mysql')

from mt.sql.mysql import *
