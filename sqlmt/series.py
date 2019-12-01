'''Only for backward compatibility. You should import pandasmt.series instead.'''

from pandasmt.series import *
from basemt import logger
logger.debug_call_stack()
logger.warn("Module sqlmt.series is deprecated. Its existence is only for backward compatibility. Please use module pandasmt.series instead.")
