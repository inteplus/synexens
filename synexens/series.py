'''Only for backward compatibility. You should import pandasmt.series instead.'''

from mt.base import logger
logger.warn_module_move('sqlmt.series', 'mt.pandas.series')

from mt.pandas.series import *
