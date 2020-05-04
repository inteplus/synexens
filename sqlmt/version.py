from mt.base import logger
logger.warn_module_move('sqlmt.version', 'mt.sql.version')

from mt.sql.version import *
