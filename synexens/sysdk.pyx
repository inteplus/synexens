# distutils: language = c++
# distutils: language_level = 3

from libcpp.vector cimport vector
from libcpp cimport bool

import numpy as np

cdef extern from "SYSDKInterface.h" namespace "Synexens" nogil:

    # ----- constants -----

    # ----- enums -----

    cpdef enum SYErrorCode:  # 错误码
        # 成功
        SYERRORCODE_SUCCESS = 0,
        # 失败
        SYERRORCODE_FAILED = 1,
        # 设备不存在
        SYERRORCODE_DEVICENOTEXIST = 2,
        # 设备未打开
        SYERRORCODE_DEVICENOTOPENED = 3,
        # 不支持的分辨率
        SYERRORCODE_UNKOWNRESOLUTION = 4,
        # 设备指针句柄为空
        SYERRORCODE_DEVICEHANDLEEMPTY = 5,
        # 设备输出数据格式设置失败
        SYERRORCODE_SETOUTPUTFORMATFAILED = 6,
        # 获取视频流控制指针失败
        SYERRORCODE_GETSTREAMCTRLFAILED = 7,
        # 启动视频流失败
        SYERRORCODE_STARTSTREAMINGFAILED = 8,
        # 通讯指针为空
        SYERRORCODE_COMMUNICATEOBJECTEMPTY = 9,
        # 无效的SN号
        SYERRORCODE_UNKOWNSN = 10,
        # 字符串长度溢出
        SYERRORCODE_STRINGLENGTHOUTRANGE = 11,
        # 无效帧类型
        SYERRORCODE_UNKOWNFRAMETYPE = 12,
        # 无效设备类型
        SYERRORCODE_UNKOWNDEVICETYPE = 13,
        # 设备对象指针为空
        SYERRORCODE_DEVICEOBJECTEMPTY = 14,
        # 通知对象指针为空
        SYERRORCODE_OBSERVEREMPTY = 15,
        # 通知对象未找到
        SYERRORCODE_OBSERVERNOTFOUND = 16,
        # 数量溢出
        SYERRORCODE_COUNTOUTRANGE = 17,
        # UVC初始化失败
        SYERRORCODE_UVCINITFAILED = 18,
        # UVC查找设备失败
        SYERRORCODE_UVCFINDDEVICEFAILED = 19,
        # 无数据帧
        SYERRORCODE_NOFRAME = 20,
        # 程序路径获取失败
        SYERRORCODE_GETAPPFOLDERPATHFAILED = 21,
        # 视频流未启动
        SYERRORCODE_NOSTREAMING = 22,
        # 算法指针为空
        SYERRORCODE_RECONSTRUCTIONEMPTY = 23,
        # 视频流已开启
        SYERRORCODE_STREAMINGEXIST = 24,
        # 未知的流类型
        SYERRORCODE_UNKOWNSTREAMTYPE = 25,
        # 数据指针为空
        SYERRORCODE_DATABUFFEREMPTY = 26,

    cpdef enum SYDeviceType:  # 设备类型
        # 无效
        SYDEVICETYPE_NULL = 0,
        # CS30双频
        SYDEVICETYPE_CS30_DUAL,
        # CS30单频
        SYDEVICETYPE_CS30_SINGLE,
        # CS20双频
        SYDEVICETYPE_CS20_DUAL,
        # CS20单频
        SYDEVICETYPE_CS20_SINGLE,
        # CS20_P
        SYDEVICETYPE_CS20_P,
        # CS40
        SYDEVICETYPE_CS40,

    cpdef enum SYStreamType:  # 数据流类型
        # 无效
        SYSTREAMTYPE_NULL = 0,
        # RAW
        SYSTREAMTYPE_RAW,
        # 深度
        SYSTREAMTYPE_DEPTH,
        # RGB
        SYSTREAMTYPE_RGB,
        # 深度+IR
        SYSTREAMTYPE_DEPTHIR,
        # 深度+RGB
        SYSTREAMTYPE_DEPTHRGB,
        # 深度+IR+RGB
        SYSTREAMTYPE_DEPTHIRRGB,
        # RGBD(mapping后的深度+RGB)
        SYSTREAMTYPE_RGBD,
        # RAW_RGB
        SYSTREAMTYPE_RAWRGB,

    cpdef enum SYResolution:  # 分辨率枚举
        # 无效
        SYRESOLUTION_NULL = 0,
        # 320*240
        SYRESOLUTION_320_240,
        # 640*480
        SYRESOLUTION_640_480,
        # 960*540
        SYRESOLUTION_960_540,
        # 1920*1080
        SYRESOLUTION_1920_1080,

    cpdef enum SYFrameType:  # 数据帧类型
        # 无效
        SYFRAMETYPE_NULL = 0,
        # RAW
        SYFRAMETYPE_RAW,
        # 深度
        SYFRAMETYPE_DEPTH,
        # IR
        SYFRAMETYPE_IR,
        # RGB
        SYFRAMETYPE_RGB,

    cpdef enum SYSupportType:  # 支持的类型
        # 无效
        SYSUPPORTTYPE_NULL = 0,
        # 深度
        SYSUPPORTTYPE_DEPTH,
        # RGB
        SYSUPPORTTYPE_RGB,
        # RGBD
        SYSUPPORTTYPE_RGBD,

    cpdef enum SYEventType:  # 事件类型
        # 无效
        SYEVENTTYPE_NULL = 0,
        # 设备连接
        SYEVENTTYPE_DEVICECONNECT,
        # 设备断开
        SYEVENTTYPE_DEVICEDISCONNECT,

    cpdef enum SYFilterType:  # 滤波类型
        # 无效
        SYFILTERTYPE_NULL = 0,
        # 中值
        SYFILTERTYPE_MEDIAN,
        # 幅值
        SYFILTERTYPE_AMPLITUDE,
        # 边界
        SYFILTERTYPE_EDGE,
        # 斑点
        SYFILTERTYPE_SPECKLE,
        # 大金阈值
        SYFILTERTYPE_OKADA,
        # 边界2
        SYFILTERTYPE_EDGE_MAD,
        # 高斯
        SYFILTERTYPE_GAUSS,
        # 备用
        SYFILTERTYPE_EXTRA,
        # 备用2
        SYFILTERTYPE_EXTRA2,

    # ----- structs -----

    cdef cppclass SYDeviceInfo:  # 设备信息
        # 设备唯一ID
        unsigned int m_nDeviceID
        # 设备类型
        SYDeviceType m_deviceType


    cdef cppclass SYEventInfo:  # 事件信息
        # 事件类型
        SYEventType m_eventType
        # 事件信息数据
        void* m_pEventInfo
        # 数据长度
        int m_nLength

    cdef cppclass SYFrameInfo: # 数据帧信息
        # 帧类型
        SYFrameType m_frameType
        # 高度（像素）
        int m_nFrameHeight
        # 宽度（像素）
        int m_nFrameWidth

    cdef cppclass SYFrameData:  # 数据帧
        # 帧数量
        int m_nFrameCount
        # 帧信息
        SYFrameInfo* m_pFrameInfo
        # 帧数据
        void* m_pData
        # 数据长度
        int m_nBuffferLength

    cdef cppclass SYPointCloudData:  # 点云数据结构
        # X
        float m_fltX
        # Y
        float m_fltY
        # Z
        float m_fltZ

    cdef cppclass SYIntrinsics:  # 相机参数结构体
        #  镜头视角
        float m_fltFOV[2]
        #  畸变系数
        float m_fltCoeffs[5]
        #  x 方向的焦距
        float m_fltFocalDistanceX
        #  y 方向的焦距
        float m_fltFocalDistanceY
        #  x 方向的成像中心点 即cx
        float m_fltCenterPointX
        #  y 方向的成像中心点 即cy
        float m_fltCenterPointY
        #  宽度
        int m_nWidth
        #  高度
        int m_nHeight

    # ----- functions -----

    # 获取SDK版本号
    # @ param [in/out] nLength 字符长度
    # @ param [in/out] pstrSDKVersion SDK版本号字符串指针
    # @ return 错误码
    SYErrorCode GetSDKVersion(int& nLength, char* pstrSDKVersion)

    # 初始化SDK
    # @ return 错误码
    SYErrorCode InitSDK()

    # 反初始化SDK，释放资源
    # @ return 错误码
    SYErrorCode UnInitSDK()

    # 查找设备
    # @ param [in/out] nCount 设备数量
    # @ param [in/out] pDevice 设备信息，由外部分配内存，pDevice传入nullptr时仅获取nCount
    # @ return 错误码
    SYErrorCode FindDevice(int& nCount, SYDeviceInfo* pDevice)

    # 打开设备
    # @ param [in] deviceInfo 设备信息
    # @ return 错误码
    SYErrorCode OpenDevice(const SYDeviceInfo& deviceInfo)

    # 关闭设备
    # @ param [in] nDeviceID 设备ID
    # @ return 错误码
    SYErrorCode CloseDevice(unsigned int nDeviceID)

    # 查询设备支持类型
    # @ param [in] nDeviceID 设备ID
    # @ param [in/out] nCount 支持的数据帧类型数量,pSupportType为空时仅用作返回数量，否则用来校验pSupportType内存分配数量是否匹配
    # @ param [in/out] pSupportType 支持的类型，由外部分配内存，pSupportType传入nullptr时仅获取nCount
    # @ return 错误码
    SYErrorCode QueryDeviceSupportFrameType(unsigned int nDeviceID, int& nCount, SYSupportType * pSupportType)

    # 查询设备支持的帧分辨率
    # @ param [in] nDeviceID 设备ID
    # @ param [in] supportType 帧类型
    # @ param [in/out] nCount 支持的分辨率数量,pResolution为空时仅用作返回数量，否则用来校验pResolution内存分配数量是否匹配
    # @ param [in/out] pResolution 支持的分辨率类型，由外部分配内存，pResolution传入nullptr时仅获取nCount
    # @ return 错误码
    SYErrorCode QueryDeviceSupportResolution(unsigned int nDeviceID, SYSupportType supportType, int& nCount, SYResolution* pResolution)

    # 获取当前流类型
    # @ param [in] nDeviceID 设备ID
    # @ return 当前流类型
    SYStreamType GetCurrentStreamType(unsigned int nDeviceID)

    # 启动数据流
    # @ param [in] nDeviceID 设备ID
    # @ param [in] streamType 数据流类型
    # @ return 错误码
    SYErrorCode StartStreaming(unsigned int nDeviceID, SYStreamType streamType)

    # 停止数据流
    # @ param [in] nDeviceID 设备ID
    # @ return 错误码
    SYErrorCode StopStreaming(unsigned int nDeviceID)

    # 切换数据流
    # @ param [in] nDeviceID 设备ID
    # @ param [in] streamType 数据流类型
    # @ return 错误码
    SYErrorCode ChangeStreaming(unsigned int nDeviceID, SYStreamType streamType)

    # 设置分辨率（如果已启动数据流，内部会执行关流->设置分辨率->重新开流的操作流程）
    # @ param [in] nDeviceID 设备ID
    # @ param [in] frameType 帧类型
    # @ param [in] resolution 帧分辨率
    # @ return 错误码
    SYErrorCode SetFrameResolution(unsigned int nDeviceID, SYFrameType frameType, SYResolution resolution)

    # 获取设备帧分辨率
    # @ param [in] nDeviceID 设备ID
    # @ param [in] frameType 帧类型
    # @ param [out] resolution 帧分辨率
    # @ return 错误码
    SYErrorCode GetFrameResolution(unsigned int nDeviceID, SYFrameType frameType, SYResolution& resolution)

    # 获取滤波开启状态
    # @ param [in] nDeviceID 设备ID
    # @ param [out] bFilter 滤波开启状态，true-已开启滤波，false-未开启滤波
    # @ return 错误码
    SYErrorCode GetFilter(unsigned int nDeviceID, bool& bFilter)

    # 开启/关闭滤波
    # @ param [in] nDeviceID 设备ID
    # @ param [in] bFilter 滤波开关，true-开启滤波，false-关闭滤波
    # @ return 错误码
    SYErrorCode SetFilter(unsigned int nDeviceID, bool bFilter)

    # 获取滤波列表
    # @ param [in] nDeviceID 设备ID
    # @ param [in/out] nCount 滤波列表长度
    # @ param [in/out] pFilterType 滤波列表
    # @ return 错误码
    SYErrorCode GetFilterList(unsigned int nDeviceID, int& nCount, SYFilterType* pFilterType)

    # 设置默认滤波
    # @ param [in] nDeviceID 设备ID
    # @ return 错误码
    SYErrorCode SetDefaultFilter(unsigned int nDeviceID)

    # 增加滤波
    # @ param [in] nDeviceID 设备ID
    # @ param [in] filterType 滤波类型
    # @ return 错误码
    SYErrorCode AddFilter(unsigned int nDeviceID, SYFilterType filterType)

    # 移除滤波
    # @ param [in] nDeviceID 设备ID
    # @ param [in] nIndex 滤波列表中的索引
    # @ return 错误码
    SYErrorCode DeleteFilter(unsigned int nDeviceID, int nIndex)

    # 清除滤波
    # @ param [in] nDeviceID 设备ID
    # @ return 错误码
    SYErrorCode ClearFilter(unsigned int nDeviceID)

    # 设置滤波参数
    # @ param [in] nDeviceID 设备ID
    # @ param [in] filterType 滤波类型
    # @ param [in] nParamCount 滤波参数个数
    # @ param [in] pFilterParam 滤波参数
    # @ return 错误码
    SYErrorCode SetFilterParam(unsigned int nDeviceID, SYFilterType filterType, int nParamCount, float* pFilterParam)

    # 获取滤波参数
    # @ param [in] nDeviceID 设备ID
    # @ param [in] filterType 滤波类型
    # @ param [in/out] nParamCount 滤波参数个数
    # @ param [in/out] pFilterParam 滤波参数
    # @ return 错误码
    SYErrorCode GetFilterParam(unsigned int nDeviceID, SYFilterType filterType, int& nParamCount, float* pFilterParam)

# ----- functions -----

def get_sdk_version():
    cdef char arr[256]
    cdef int nLength = 256
    cdef SYErrorCode ret

    ret = SYErrorCode(GetSDKVersion(nLength, &arr[0]))
    if ret != 0:
        raise RuntimeError(f"GetSDKVersion() returns {ret}.")

    return arr[:nLength].decode()

def init_sdk():
    return SYErrorCode(InitSDK())

def uninit_sdk():
    return SYErrorCode(UnInitSDK())

def find_device():
    cdef int nCount = 0
    cdef vector[SYDeviceInfo] devices
    cdef SYErrorCode ret

    if True:
        ret = SYErrorCode(FindDevice(nCount, NULL))
        if ret != 0:
            raise RuntimeError(f"First FindDevice() returns {ret}.")
        devices.resize(nCount)
    else:
        devices.resize(1)

    ret = SYErrorCode(FindDevice(nCount, &devices[0]))
    if ret != 0:
        raise RuntimeError(f"Second FindDevice() returns {ret}.")
    res = {}
    for i in range(nCount):
        device = devices[i]
        res[device.m_nDeviceID] = SYDeviceType(device.m_deviceType)

    return res

def open_device(unsigned int nDeviceID, SYDeviceType deviceType):
    cdef SYDeviceInfo di

    di.m_nDeviceID = nDeviceID
    di.m_deviceType = deviceType

    return SYErrorCode(OpenDevice(di))

def close_device(unsigned int nDeviceID):
    return SYErrorCode(CloseDevice(nDeviceID))

def query_device_support_frame_type(unsigned int nDeviceID):
    cdef int nCount = 0
    cdef vector[SYSupportType] supportTypes
    cdef SYErrorCode ret

    ret = SYErrorCode(QueryDeviceSupportFrameType(nDeviceID, nCount, NULL))
    if ret != 0:
        raise RuntimeError(f"First QueryDeviceSupportFrameType() returns {ret}.")
    supportTypes.resize(nCount)

    ret = SYErrorCode(QueryDeviceSupportFrameType(nDeviceID, nCount, &supportTypes[0]))
    if ret != 0:
        raise RuntimeError(f"Second QueryDeviceSupportFrameType() returns {ret}.")
    res = []
    for i in range(nCount):
        res.append(SYSupportType(supportTypes[i]))

    return res

def query_device_support_resolution(unsigned int nDeviceID, SYSupportType supportType):
    cdef int nCount = 0
    cdef vector[SYResolution] resolutions
    cdef SYErrorCode ret

    ret = SYErrorCode(QueryDeviceSupportResolution(nDeviceID, supportType, nCount, NULL))
    if ret != 0:
        raise RuntimeError(f"First QueryDeviceSupportResolution() returns {ret}.")
    resolutions.resize(nCount)

    ret = SYErrorCode(QueryDeviceSupportResolution(nDeviceID, supportType, nCount, &resolutions[0]))
    if ret != 0:
        raise RuntimeError(f"Second QueryDeviceSupportFrameType() returns {ret}.")
    res = []
    for i in range(nCount):
        res.append(SYResolution(resolutions[i]))

    return res

def get_current_stream_type(unsigned int nDeviceID):
    return SYStreamType(GetCurrentStreamType(nDeviceID))

def start_streaming(unsigned int nDeviceID, SYStreamType streamType):
    return SYErrorCode(StartStreaming(nDeviceID, streamType))

def stop_streaming(unsigned int nDeviceID):
    return SYErrorCode(StopStreaming(nDeviceID))

def change_streaming(unsigned int nDeviceID, SYStreamType streamType):
    return SYErrorCode(ChangeStreaming(nDeviceID, streamType))

def set_frame_resolution(unsigned int nDeviceID, SYFrameType frameType, SYResolution resolution):
    return SYErrorCode(SetFrameResolution(nDeviceID, frameType, resolution))

def get_frame_resolution(unsigned int nDeviceID, SYFrameType frameType):
    cdef SYResolution resolution
    cdef SYErrorCode ret

    ret = SYErrorCode(GetFrameResolution(nDeviceID, frameType, resolution))
    if ret != 0:
        raise RuntimeError(f"GetFrameResolution() returns {ret}.")

    return SYResolution(resolution)

def get_filter(unsigned int nDeviceID):
    cdef bool bFilter
    cdef SYErrorCode ret

    ret = SYErrorCode(GetFilter(nDeviceID, bFilter))
    if ret != 0:
        raise RuntimeError(f"GetFilter() returns {ret}.")

    return bFilter

def set_filter(unsigned int nDeviceID, bool bFilter):
    return SYErrorCode(SetFilter(nDeviceID, bFilter))

def get_filter_list(unsigned int nDeviceID):
    cdef int nCount = 0
    cdef vector[SYFilterType] filterTypes
    cdef SYErrorCode ret

    ret = SYErrorCode(GetFilterList(nDeviceID, nCount, NULL))
    if ret != 0:
        raise RuntimeError(f"First GetFilterList() returns {ret}.")
    filterTypes.resize(nCount)

    ret = SYErrorCode(GetFilterList(nDeviceID, nCount, &filterTypes[0]))
    if ret != 0:
        raise RuntimeError(f"Second GetFilterList() returns {ret}.")
    res = []
    for i in range(nCount):
        res.append(SYFilterType(filterTypes[i]))

    return res

def set_default_filter(unsigned int nDeviceID):
    return SYErrorCode(SetDefaultFilter(nDeviceID))

def add_filter(unsigned int nDeviceID, SYFilterType filterType):
    return SYErrorCode(AddFilter(nDeviceID, filterType))

def delete_filter(unsigned int nDeviceID, int nIndex):
    return SYErrorCode(DeleteFilter(nDeviceID, nIndex))

def clear_filter(unsigned int nDeviceID):
    return SYErrorCode(ClearFilter(nDeviceID))

def set_filter_params(unsigned int nDeviceID, SYFilterType filterType, float[:] filterParams):
    if filterParams.strides[0] != 4:
        raise ValueError("Argument 'filterParams' is not contiguous.")
    return SYErrorCode(SetFilterParam(nDeviceID, filterType, filterParams.shape[0], &filterParams[0]))

def get_filter_params(unsigned int nDeviceID, SYFilterType filterType):
    cdef int nCount = 0
    cdef vector[float] filterParams
    cdef SYErrorCode ret

    ret = SYErrorCode(GetFilterParam(nDeviceID, filterType, nCount, NULL))
    if ret != 0:
        raise RuntimeError(f"First GetFilterParam() returns {ret}.")
    filterParams.resize(nCount)

    ret = SYErrorCode(GetFilterParam(nDeviceID, filterType, nCount, &filterParams[0]))
    if ret != 0:
        raise RuntimeError(f"Second GetFilterParam() returns {ret}.")
    res = np.empty(nCount, dtype=np.float32)
    res[:] = filterParams

    return res
