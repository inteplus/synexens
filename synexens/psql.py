'''Useful modules for accessing PostgreSQL'''

from mt.base import logger
logger.warn_module_move('sqlmt.psql', 'mt.sql.psql')

from mt.sql.psql import *
