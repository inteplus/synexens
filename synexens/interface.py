"""The interface."""


import atexit
import v4l2py as v

from .sysdk import *

_ret = init_sdk()
if _ret != 0:
    raise RuntimeError("Unable to initialise the Synexens SDK.")
atexist.register(uninit_sdk)
_devices_found = False

_find_devices_func = find_devices


def find_devices():
    if not _devices_found:
        find_devices()
        _devices_found = True


class Device(v.device.ReentrantContextManager):
    def __init__(self, device_id: int):
        super().__init__()
        self.device_id = device_id

    def open(self):
        pass

    def close(self):
        pass
