"""The interface."""


import errno
import functools
import atexit
import v4l2py as v

from .sysdk import *

_ret = init_sdk()
if _ret != 0:
    raise RuntimeError("Unable to initialise the Synexens SDK.")
atexit.register(uninit_sdk)


@functools.cache
def find_devices():
    """Finds all Synexens devices attached to the machine.

    Returns
    -------
    dict
        a dictionary mapping each found device id to device type
    """
    return find_device()


class Device(v.device.ReentrantContextManager):
    def __init__(self, device_id: int):
        super().__init__()
        if device_id not in find_devices():
            raise OSError(
                errno.ENXIO, f"Synexens device with id {device_id} not found."
            )
        self.device_id = device_id

    def open(self):
        pass

    def close(self):
        pass
