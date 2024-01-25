"""The interface."""


import errno
import functools
import atexit
import v4l2py as v4l2

import synexens_sdk as sdk

from mt import tp, np

sdk.init_sdk()
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


def check_depth_image(depth_image: np.ndarray, is_ir: bool = False):
    depth = "IR" if is_ir else "depth"
    if not depth_image.flags["C_CONTIGUOUS"]:
        raise ValueError(f"The {depth} image is not C_CONTIGUOUS.")
    if len(depth_image.shape) != 3:
        raise ValueError(
            f"The {depth} image must have rank 3. Shape: {depth_image.shape}."
        )
    if depth_image.shape[2] != 1:
        raise ValueError(
            f"The {depth} image must have dim 1 for the last rank. Shape: {depth_image.shape}."
        )
    if depth_image.dtype != np.uint16:
        raise ValueError(
            f"The {depth} image must have dtype uint16. Dtype: {depth_image.dtype}."
        )


class Device(v4l2.device.ReentrantContextManager):
    """A Synexens device."""

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
        """Opens the device and gets the device information."""
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
            s_resolutions = set()
            for supportType in l_supportTypes:
                l_resolutions = sdk.query_device_support_resolution(
                    self.index, supportType
                )
                d_supportTypes[supportType] = l_resolutions
                s_resolutions.update(l_resolutions)
            self.info["support_frame_types"] = d_supportTypes
            d_resolutions = {}
            for resolution in sorted(s_resolutions):
                res = {}
                res["intrinsics"] = sdk.get_intrinsics(self.index, resolution)
                nMin, nMax = sdk.get_integral_time_range(self.index, resolution)
                res["integral_time_min"] = nMin
                res["integral_time_max"] = nMax
                d_resolutions[resolution] = res
            self.info["resolutions"] = d_resolutions
            nMin, nMax = sdk.get_distance_measure_range(self.index)
            res["distance_measure_min"] = nMin
            res["distance_measure_max"] = nMax
            self.closed = False
            self.streaming = False

    def close(self):
        """Closes the device."""

        if not self.closed:
            if self.streaming:
                self.stream_off()
            sdk.close_device(self.index)
            self.closed = True

    def __repr__(self):
        return f"<{type(self).__name__} index={self.index}, closed={self.closed}>"

    @property
    def stream_type(self):
        """The current stream type."""
        return sdk.get_current_stream_type(self.index)

    @stream_type.setter
    def stream_type(self, stream_type: sdk.SYStreamType):
        if self.streaming:
            return sdk.change_streaming(self.index, stream_type)
        sdk.start_streaming(self.index, stream_type)
        self.streaming = True

    def stream_on(self, stream_type: tp.Optional[sdk.SYStreamType] = None):
        """Starts streaming."""
        self.stream_type = stream_type

    def stream_off(self):
        """Stops streaming."""
        sdk.stop_streaming(self.index)
        self.streaming = False

    @property
    def resolution(self):
        """The current resolution."""
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
            sdk.set_frame_resolution(self.index, frame_type, resolution)

    @property
    def filter(self):
        """Whether the filter is on or off."""
        return sdk.get_filter(self.index)

    @filter.setter
    def filter(self, bFilter: bool):
        sdk.set_filter(self.index, bFilter)

    def get_filter_list(self):
        """Gets the list of filters currently being used."""
        return sdk.get_filter_list(self.index)

    def set_default_filter(self):
        """Sets the default filter."""
        sdk.set_default_filter(self.index)

    def add_filter(self, filter_type: sdk.SYFilterType):
        """Adds a filter of a given type to the filter list."""
        sdk.add_filter(self.index, filter_type)

    def delete_filter(self, index: int):
        """Deletes a filter at a given position on the filter list."""
        sdk.delete_filter(self.index, index)

    def clear_filter(self):
        """Clears all filters on the filter list."""
        sdk.clear_filter(self.index)

    def get_filter_params(self, filter_type: sdk.SYFilterType):
        """Gets the parameters for a given filter type."""
        return sdk.get_filter_params(self.index, filter_type)

    def set_filter_params(self, filter_type: sdk.SYFilterType, params: np.ndarray):
        """Sets the parameters for a given filter type."""
        return sdk.set_filter_params(self.index, filter_type, params)

    @property
    def mirror(self):
        """Whether the mirror is on or off."""
        return sdk.get_mirror(self.index)

    @mirror.setter
    def mirror(self, bMirror: bool):
        sdk.set_mirror(self.index, bMirror)

    @property
    def flip(self):
        """Whether the flip is on or off."""
        return sdk.get_flip(self.index)

    @flip.setter
    def flip(self, bFlip: bool):
        sdk.set_flip(self.index, bFlip)

    @property
    def integral_time(self):
        """The integral time."""
        return sdk.get_integral_time(self.index)

    @integral_time.setter
    def integral_time(self, itime: int):
        sdk.set_integral_time(self.index, itime)

    def get_depth_color(self, depth_image: np.ndarray):
        """Gets the depth color for a given depth image."""
        check_depth_image(depth_image)
        return sdk.get_depth_color(self.index, depth_image)

    def get_depth_point_cloud(self, depth_image: np.ndarray, undistort: bool):
        """Gets the depth point cloud for a given depth image."""
        check_depth_image(depth_image)
        return sdk.get_depth_point_cloud(self.index, depth_image, undistort)

    def get_last_frame_data(self):
        """Gets the latest frame(s) of data."""
        return sdk.get_last_frame_data(self.index)

    def undistort_depth(self, depth_image: np.ndarray):
        """Undistorts the depth image."""
        check_depth_image(depth_image)
        return sdk.undistort_depth(depth_image)

    def undistort_ir(self, ir_image: np.ndarray):
        """Undistorts the IR image."""
        check_depth_image(ir_image, is_ir=True)
        return sdk.undistort_depth(ir_image)
