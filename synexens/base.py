"""The interface."""


import errno
import functools
import atexit
import v4l2py as v4l2

import synexens_sdk as sdk

_ret = sdk.init_sdk()
if _ret != 0:
    raise RuntimeError("Unable to initialise the Synexens SDK.")
atexit.register(sdk.uninit_sdk)


@functools.cache
def find_devices():
    """Finds all Synexens devices attached to the machine.

    Returns
    -------
    dict
        a dictionary mapping each found device id to device type
    """
    return sdk.find_device()


class Device(v4l2.device.ReentrantContextManager):
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
