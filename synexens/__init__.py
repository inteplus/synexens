from .version import version as __version__
from .base import get_sdk_version, find_devices, Device

__api__ = [
    "get_sdk_version",
    "find_devices",
    "Device",
]

import synexens_sdk as _sdk

for key in _sdk.__dict__:
    if key.startswith("SY"):
        globals()[key] = getattr(_sdk, key)
