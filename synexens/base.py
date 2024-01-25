"""The interface."""


import errno
import functools
import atexit
import v4l2py as v4l2

import synexens_sdk as sdk

from mt import tp

_ret = sdk.init_sdk()
if _ret != 0:
    raise RuntimeError("Unable to initialise the Synexens SDK.")
atexit.register(sdk.uninit_sdk)


@functools.cache
def get_sdk_version():
    """Retrieves the SDK version being used.

    Returns
    -------
    str
        the sdk version
    """
    return sdk.get_sdk_version()


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
    def __init__(self, device_id: tp.Optional[int] = None):
        super().__init__()

        if device_id is None:
            device_id = list(find_devices().keys())[0]
        elif device_id not in find_devices():
            raise OSError(
                errno.ENXIO, f"Synexens device with id {device_id} not found."
            )
        self.index = device_id
        self.info = None
        self.closed = True
        self.streaming = False

    def __del__(self):
        self.close()

    def open(self):
        if self.closed:
            device_type = find_devices()[self.index]
            sdk.open_device(self.index, device_type)
            self.info = {
                "device_type": sdk.SYDeviceType(device_type),
                "hw_version": sdk.get_device_hw_version(self.index),
                "serial_number": sdk.get_device_sn(self.index),
            }
            l_supportTypes = sdk.query_device_support_frame_type(self.index)
            d_supportTypes = {}
            for supportType in l_supportTypes:
                l_resolutions = sdk.query_device_support_resolution(
                    self.index, supportType
                )
                d_supportTypes[supportType] = l_resolutions
            self.info["support_frame_types"] = d_supportTypes
            self.closed = False
            self.streaming = False

    def close(self):
        if not self.closed:
            if self.streaming:
                self.stream_off()
            sdk.close_device(self.index)
            self.closed = True

    def __repr__(self):
        return f"<{type(self).__name__} index={self.index}, closed={self.closed}>"

    @property
    def stream_type(self):
        return sdk.get_current_stream_type(self.index)

    @stream_type.setter
    def stream_type(self, stream_type: sdk.SYStreamType):
        if self.streaming:
            return sdk.change_streaming(self.index, stream_type)
        ret = sdk.start_streaming(self.index, stream_type)
        if ret != 0:
            raise RuntimeError(
                f"synexens_sdk.start_streaming() returns {str(sdk.SYErrorCode(ret))}."
            )
        self.streaming = True

    def stream_on(self, stream_type: tp.Optional[sdk.SYStreamType] = None):
        self.stream_type = stream_type

    def stream_off(self):
        ret = sdk.stop_streaming(self.index)
        if ret != 0:
            raise RuntimeError(
                f"synexens_sdk.stop_streaming() returns {str(sdk.SYErrorCode(ret))}."
            )
        self.streaming = False
        return ret

    @property
    def resolution(self):
        return sdk.get_frame_resolution(self.index, sdk.SYFRAMETYPE_IR)

    @resolution.setter
    def resolution(self, resolution: sdk.SYResolution):
        l_frameTypes = [sdk.SYFRAMETYPE_IR]
        for support_frame_type in self.info["support_frame_types"]:
            if support_frame_type == sdk.SYSUPPORTTYPE_DEPTH:
                l_frameTypes.append(sdk.SYFRAMETYPE_DEPTH)
            elif support_frame_type == sdk.SYSUPPORTTYPE_RGB:
                l_frameTypes.append(sdk.SYFRAMETYPE_RGB)

        for frame_type in l_frameTypes:
            ret = sdk.set_frame_resolution(self.index, frame_type, resolution)
            if ret != 0:
                raise RuntimeError(
                    f"Unable to set the resolution {str(sdk.SYResolution(resolution))} to frame type {str(sdk.SYFrameType(frame_type))}."
                )
