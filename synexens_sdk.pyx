# distutils: language = c++
# distutils: language_level = 3

from libc.string cimport memcpy
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

    # 获取水平镜像状态
    # @ param [in] nDeviceID 设备ID
    # @ param [out] bMirror 水平镜像状态，true-已开启水平镜像，false-未开启水平镜像
    # @ return 错误码
    SYErrorCode GetMirror(unsigned int nDeviceID, bool& bMirror)

    # 开启/关闭水平镜像
    # @ param [in] nDeviceID 设备ID
    # @ param [in] bMirror 水平镜像开关，true-开启水平镜像，false-关闭水平镜像
    # @ return 错误码
    SYErrorCode SetMirror(unsigned int nDeviceID, bool bMirror)

    # 获取垂直翻转状态
    # @ param [in] nDeviceID 设备ID
    # @ param [out] bFlip 垂直翻转状态，true-已开启垂直翻转，false-未开启垂直翻转
    # @ return 错误码
    SYErrorCode GetFlip(unsigned int nDeviceID, bool& bFlip)

    # 开启/关闭垂直翻转
    # @ param [in] nDeviceID 设备ID
    # @ param [in] bFlip 垂直翻转开关，true-开启垂直翻转，false-关闭垂直翻转
    # @ return 错误码
    SYErrorCode SetFlip(unsigned int nDeviceID, bool bFlip)

    # 获取积分时间
    # @ param [in] nDeviceID 设备ID
    # @ param [out] nIntegralTime 积分时间
    # @ return 错误码
    SYErrorCode GetIntegralTime(unsigned int nDeviceID, int& nIntegralTime)

    # 设置积分时间
    # @ param [in] nDeviceID 设备ID
    # @ param [in] nIntegralTime 积分时间
    # @ return 错误码
    SYErrorCode SetIntegralTime(unsigned int nDeviceID, int nIntegralTime)

    # 获取积分时间调节范围
    # @ param [in] nDeviceID 设备ID
    # @ param [in] depthResolution depth分辨率
    # @ param [out] nMin 积分时间最小值
    # @ param [out] nMax 积分时间最大值
    # @ return 错误码
    SYErrorCode GetIntegralTimeRange(unsigned int nDeviceID, SYResolution depthResolution, int& nMin, int& nMax)

    # 获取测距量程
    # @ param [in] nDeviceID 设备ID
    # @ param [out] nMin 量程最小值
    # @ param [out] nMax 量程最大值
    # @ return 错误码
    SYErrorCode GetDistanceMeasureRange(unsigned int nDeviceID, int& nMin, int& nMax)

    # 获取用户测距范围
    # @ param [in] nDeviceID 设备ID
    # @ param [out] nMin 测距范围最小值
    # @ param [out] nMax 测距范围最大值
    # @ return 错误码
    SYErrorCode GetDistanceUserRange(unsigned int nDeviceID, int& nMin, int& nMax)

    # 设置用户测距范围
    # @ param [in] nDeviceID 设备ID
    # @ param [in] nMin 测距范围最小值
    # @ param [in] nMax 测距范围最大值
    # @ return 错误码
    SYErrorCode SetDistanceUserRange(unsigned int nDeviceID, int nMin, int nMax)

    # 读取设备sn号
    # @ param [in] nDeviceID 设备ID
    # @ param [in/out] nLength 字符长度
    # @ param [in/out] pstrSN 设备sn号字符串指针,由外部分配内存，pstrSN传入nullptr时仅获取nLength
    # @ return 错误码
    SYErrorCode GetDeviceSN(unsigned int nDeviceID, int& nLength, char* pstrSN)

    # 写入设备sn号
    # @ param [in] nDeviceID 设备ID
    # @ param [in] nLength 字符长度
    # @ param [in] pstrSN 设备sn号字符串指针
    # @ return 错误码
    SYErrorCode SetDeviceSN(unsigned int nDeviceID, int nLength, const char* pstrSN)

    # 读取设备固件版本号
    # @ param [in] nDeviceID 设备ID
    # @ param [in/out] nLength 字符长度
    # @ param [in/out] pstrHWVersion 固件版本号字符串指针,由外部分配内存，pstrHWVersion传入nullptr时仅获取nLength
    # @ return 错误码
    SYErrorCode GetDeviceHWVersion(unsigned int nDeviceID, int& nLength, char* pstrHWVersion)

    # 获取深度对应伪彩色
    # @ param [in] nDeviceID 设备ID
    # @ param [in] nCount 数据量(内存空间pDepth需要nCount*2字节，pColor需要nCount*3字节)
    # @ param [in] pDepth 深度数据
    # @ param [in/out] pColor 深度对应伪彩色(24位RGB格式)
    # @ return 错误码
    SYErrorCode GetDepthColor(unsigned int nDeviceID, int nCount, const unsigned short* pDepth, unsigned char* pColor)

    # 获取深度对应点云数据
    # @ param [in] nDeviceID 设备ID
    # @ param [in] nWidth 宽度
    # @ param [in] nHeight 高度
    # @ param [in] pDepth 深度数据
    # @ param [in/out] pPointCloud 深度对应点云数据,由外部分配内存
    # @ param [in] bUndistort 裁剪标志，true-裁剪 false-不裁剪
    # @ return 错误码
    SYErrorCode GetDepthPointCloud(unsigned int nDeviceID, int nWidth, int nHeight, const unsigned short* pDepth, SYPointCloudData* pPointCloud, bool bUndistort)

    # 获取RGBD
    # @ param [in] nDeviceID 设备ID
    # @ param [in] nSourceDepthWidth 源深度数据宽度
    # @ param [in] nSourceDepthHeight 源深度数据高度
    # @ param [in] pSourceDepth 源深度数据
    # @ param [in] nSourceRGBWidth 源RGB数据宽度
    # @ param [in] nSourceRGBHeight 源RGB数据高度
    # @ param [in] pSourceRGB 源RGB数据
    # @ param [in] nTargetWidth RGBD数据宽度
    # @ param [in] nTargetHeight RGBD数据高度
    # @ param [in/out] pTargetDepth RGBD中的深度数据,由外部分配内存,数据长度与源RGB长度一致
    # @ param [in/out] pTargetRGB RGBD中的RGB数据,由外部分配内存,数据长度与源RGB长度一致
    # @ return 错误码
    SYErrorCode GetRGBD(unsigned int nDeviceID, int nSourceDepthWidth, int nSourceDepthHeight, unsigned short* pSourceDepth, int nSourceRGBWidth, int nSourceRGBHeight, unsigned char* pSourceRGB, int nTargetWidth, int nTargetHeight, unsigned short* pTargetDepth, unsigned char* pTargetRGB)

    # 获取最新一帧数据
    # @ param [in] nDeviceID 设备ID
    # @ param [in/out] pFrameData 最后一帧数据
    # @ return 错误码
    SYErrorCode GetLastFrameData(unsigned int nDeviceID, SYFrameData*& pFrameData)

    # 去畸变
    # @ param [in] nDeviceID 设备ID
    # @ param [in] pSource  待去畸变数据指针
    # @ param [in] nWidth 图像宽度
    # @ param [in] nHeight 图像高度
    # @ param [in] bDepth 是否是深度数据/RGB数据
    # @ param [out] pTarget  去畸变结果数据指针，由外部分配内存,数据长度与待去畸变数据指针长度一致
    SYErrorCode Undistort(unsigned int nDeviceID, const unsigned short* pSource, int nWidth, int nHeight, bool bDepth, unsigned short* pTarget)

    # 获取相机参数
    # @ param [in] nDeviceID 设备ID
    # @ param [in] resolution  分辨率
    # @ param [in/out] intrinsics 相机参数
    SYErrorCode GetIntric(unsigned int nDeviceID, SYResolution resolution, SYIntrinsics& intrinsics)

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
    cdef SYErrorCode ret
    ret = SYErrorCode(InitSDK())
    if ret != 0:
        raise RuntimeError(f"InitSDK() returns {ret}.")

def uninit_sdk():
    cdef SYErrorCode ret
    ret = SYErrorCode(UnInitSDK())
    if ret != 0:
        raise RuntimeError(f"UnInitSDK() returns {ret}.")

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
    cdef SYErrorCode ret
    cdef SYDeviceInfo di

    di.m_nDeviceID = nDeviceID
    di.m_deviceType = deviceType

    ret = SYErrorCode(OpenDevice(di))
    if ret != 0:
        raise RuntimeError(f"OpenDevice() returns {ret}.")

def close_device(unsigned int nDeviceID):
    cdef SYErrorCode ret
    ret = SYErrorCode(CloseDevice(nDeviceID))
    if ret != 0:
        raise RuntimeError(f"CloseDevice() returns {ret}.")

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
    cdef SYErrorCode ret
    ret = SYErrorCode(StartStreaming(nDeviceID, streamType))
    if ret != 0:
        raise RuntimeError(f"StartStreaming() returns {ret}.")

def stop_streaming(unsigned int nDeviceID):
    cdef SYErrorCode ret
    ret = SYErrorCode(StopStreaming(nDeviceID))
    if ret != 0:
        raise RuntimeError(f"StopStreaming() returns {ret}.")

def change_streaming(unsigned int nDeviceID, SYStreamType streamType):
    cdef SYErrorCode ret
    ret = SYErrorCode(ChangeStreaming(nDeviceID, streamType))
    if ret != 0:
        raise RuntimeError(f"ChangeStreaming() returns {ret}.")

def set_frame_resolution(unsigned int nDeviceID, SYFrameType frameType, SYResolution resolution):
    cdef SYErrorCode ret
    ret = SYErrorCode(SetFrameResolution(nDeviceID, frameType, resolution))
    if ret != 0:
        raise RuntimeError(f"SetFrameResolution() returns {ret}.")

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
    cdef SYErrorCode ret
    ret = SYErrorCode(SetFilter(nDeviceID, bFilter))
    if ret != 0:
        raise RuntimeError(f"SetFilter() returns {ret}.")

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
    cdef SYErrorCode ret
    ret = SYErrorCode(SetDefaultFilter(nDeviceID))
    if ret != 0:
        raise RuntimeError(f"SetDefaultFilter() returns {ret}.")

def add_filter(unsigned int nDeviceID, SYFilterType filterType):
    cdef SYErrorCode ret
    ret = SYErrorCode(AddFilter(nDeviceID, filterType))
    if ret != 0:
        raise RuntimeError(f"AddFilter() returns {ret}.")

def delete_filter(unsigned int nDeviceID, int nIndex):
    cdef SYErrorCode ret
    ret = SYErrorCode(DeleteFilter(nDeviceID, nIndex))
    if ret != 0:
        raise RuntimeError(f"DeleteFilter() returns {ret}.")

def clear_filter(unsigned int nDeviceID):
    cdef SYErrorCode ret
    ret = SYErrorCode(ClearFilter(nDeviceID))
    if ret != 0:
        raise RuntimeError(f"ClearFilter() returns {ret}.")

def set_filter_params(unsigned int nDeviceID, SYFilterType filterType, float[:] filterParams):
    cdef SYErrorCode ret
    if filterParams.strides[0] != 4:
        raise ValueError("Argument 'filterParams' is not contiguous.")
    ret = SYErrorCode(SetFilterParam(nDeviceID, filterType, filterParams.shape[0], &filterParams[0]))
    if ret != 0:
        raise RuntimeError(f"SetFitlerParam() returns {ret}.")

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

def get_mirror(unsigned int nDeviceID):
    cdef bool bMirror
    cdef SYErrorCode ret

    ret = SYErrorCode(GetMirror(nDeviceID, bMirror))
    if ret != 0:
        raise RuntimeError(f"GetMirror() returns {ret}.")

    return bMirror

def set_mirror(unsigned int nDeviceID, bool bMirror):
    cdef SYErrorCode ret
    ret = SYErrorCode(SetMirror(nDeviceID, bMirror))
    if ret != 0:
        raise RuntimeError(f"SetMirror() returns {ret}.")

def get_flip(unsigned int nDeviceID):
    cdef bool bFlip
    cdef SYErrorCode ret

    ret = SYErrorCode(GetFlip(nDeviceID, bFlip))
    if ret != 0:
        raise RuntimeError(f"GetFlip() returns {ret}.")

    return bFlip

def set_flip(unsigned int nDeviceID, bool bFlip):
    cdef SYErrorCode ret
    ret = SYErrorCode(SetFlip(nDeviceID, bFlip))
    if ret != 0:
        raise RuntimeError(f"SetFlip() returns {ret}.")

def get_integral_time(unsigned int nDeviceID):
    cdef int nIntegralTime
    cdef SYErrorCode ret

    ret = SYErrorCode(GetIntegralTime(nDeviceID, nIntegralTime))
    if ret != 0:
        raise RuntimeError(f"GetIntegralTime() returns {ret}.")

    return nIntegralTime

def set_integral_time(unsigned int nDeviceID, int nIntegralTime):
    cdef SYErrorCode ret
    ret = SYErrorCode(SetIntegralTime(nDeviceID, nIntegralTime))
    if ret != 0:
        raise RuntimeError(f"SetIntegralTime() returns {ret}.")

def get_integral_time_range(unsigned int nDeviceID, SYResolution depthResolution):
    cdef int nMin
    cdef int nMax
    cdef SYErrorCode ret

    ret = SYErrorCode(GetIntegralTimeRange(nDeviceID, depthResolution, nMin, nMax))
    if ret != 0:
        raise RuntimeError(f"GetIntegralTime() returns {ret}.")

    return nMin, nMax

def get_distance_measure_range(unsigned int nDeviceID):
    cdef int nMin
    cdef int nMax
    cdef SYErrorCode ret

    ret = SYErrorCode(GetDistanceMeasureRange(nDeviceID, nMin, nMax))
    if ret != 0:
        raise RuntimeError(f"GetDistanceMeasureRange() returns {ret}.")

    return nMin, nMax

def get_distance_user_range(unsigned int nDeviceID):
    cdef int nMin
    cdef int nMax
    cdef SYErrorCode ret

    ret = SYErrorCode(GetDistanceUserRange(nDeviceID, nMin, nMax))
    if ret != 0:
        raise RuntimeError(f"GetDistanceUserRange() returns {ret}.")

    return nMin, nMax

def set_distance_user_range(unsigned int nDeviceID, int nMin, int nMax):
    cdef SYErrorCode ret
    ret = SYErrorCode(SetDistanceUserRange(nDeviceID, nMin, nMax))
    if ret != 0:
        raise RuntimeError(f"SetDistanceUserRange() returns {ret}.")

def get_device_sn(unsigned int nDeviceID):
    cdef char arr[256]
    cdef int nLength = 256
    cdef SYErrorCode ret

    ret = SYErrorCode(GetDeviceSN(nDeviceID, nLength, &arr[0]))
    if ret != 0:
        raise RuntimeError(f"GetDeviceSN() returns {ret}.")

    return arr[:nLength]

def get_device_hw_version(unsigned int nDeviceID):
    cdef char arr[256]
    cdef int nLength = 256
    cdef SYErrorCode ret

    ret = SYErrorCode(GetDeviceHWVersion(nDeviceID, nLength, &arr[0]))
    if ret != 0:
        raise RuntimeError(f"GetDeviceHWVersion() returns {ret}.")

    return arr[:nLength].decode()

def get_depth_color(unsigned int nDeviceID, unsigned short[:,:,:] pDepth):
    cdef SYErrorCode ret

    pColor = np.empty((pDepth.shape[0], pDepth.shape[1], 3), dtype=np.uint8)

    cdef unsigned char [:,:,:] pColor_view = pColor

    ret = SYErrorCode(GetDepthColor(nDeviceID, pDepth.size, <const unsigned short *>&pDepth[0,0,0], <unsigned char *>&pColor_view[0,0,0]))
    if ret != 0:
        raise RuntimeError(f"GetDepthColor() returns {ret}.")

    return pColor

def get_depth_point_cloud(unsigned int nDeviceID, unsigned short[:,:,:] pDepth, bool bUndistort):
    cdef SYErrorCode ret

    nHeight = pDepth.shape[0]
    nWidth = pDepth.shape[1]
    pPos = np.empty((nHeight, nWidth, 3), dtype=np.float32)

    cdef float [:,:,:] pPos_view = pPos

    ret = SYErrorCode(GetDepthPointCloud(nDeviceID, nWidth, nHeight, <const unsigned short *>&pDepth[0,0,0], <SYPointCloudData *>&pPos_view[0,0,0], bUndistort))
    if ret != 0:
        raise RuntimeError(f"GetDepthPointCloud() returns {ret}.")

    return pPos

def extract_resolution(SYResolution resolution):
    if resolution == SYRESOLUTION_NULL:
        return 0, 0
    if resolution == SYRESOLUTION_320_240:
        return 320, 240
    if resolution == SYRESOLUTION_640_480:
        return 640, 480
    if resolution == SYRESOLUTION_960_540:
        return 960, 540
    if resolution == SYRESOLUTION_1920_1080:
        return 1920, 1080

def extract_dtype(SYFrameType frameType):
    if frameType in (SYFRAMETYPE_DEPTH, SYFRAMETYPE_IR):
        return np.uint16
    return np.uint8

def extract_channel_count(SYFrameType frameType):
    if frameType in (SYFRAMETYPE_DEPTH, SYFRAMETYPE_IR):
        return 1
    return 3

def get_last_frame_data(unsigned int nDeviceID):
    cdef SYErrorCode ret
    cdef SYFrameData* pFrameData
    cdef SYFrameInfo* pFrameInfo
    cdef unsigned short [:,:,:] uint16Data
    cdef unsigned char [:,:,:] uint8Data

    ret = GetLastFrameData(nDeviceID, pFrameData)
    if ret == SYERRORCODE_NOFRAME:
        return None

    if ret != 0:
        raise RuntimeError(f"GetLastFrameData() returns {str(SYErrorCode(ret))}.")

    d_frames = {}
    ofs = 0
    for i in range(pFrameData[0].m_nFrameCount):
        pFrameInfo = &pFrameData[0].m_pFrameInfo[i]
        frameType = pFrameInfo[0].m_frameType
        dtype = extract_dtype(frameType)
        nChannels = extract_channel_count(frameType)
        width = pFrameInfo[0].m_nFrameWidth
        height = pFrameInfo[0].m_nFrameHeight
        size = np.nbytes[dtype]*width*height*nChannels
        img = np.empty((height, width, nChannels), dtype=dtype)
        if dtype == np.uint8:
            uint8Data = img
            memcpy(<void *>&uint8Data[0,0,0], &(<char*>pFrameData[0].m_pData)[ofs], size)
        else:
            uint16Data = img
            memcpy(<void *>&uint16Data[0,0,0], &(<char*>pFrameData[0].m_pData)[ofs], size)
        ofs += size
        d_frames[SYFrameType(frameType)] = img

    return d_frames

def undistort_depth(unsigned int nDeviceID, unsigned short[:,:,:] pDepth):
    cdef SYErrorCode ret

    nHeight = pDepth.shape[0]
    nWidth = pDepth.shape[1]
    pDepth2 = np.empty((nHeight, nWidth, 1), dtype=np.uint16)

    cdef unsigned short [:,:,:] pDepth2_view = pDepth2

    ret = SYErrorCode(Undistort(nDeviceID, <const unsigned short *>&pDepth[0,0,0], nWidth, nHeight, True, &pDepth2_view[0,0,0]))
    if ret != 0:
        raise RuntimeError(f"Undistort() returns {ret}.")

    return pDepth2

def undistort_ir(unsigned int nDeviceID, unsigned short[:,:,:] pIr):
    cdef SYErrorCode ret

    nHeight = pIr.shape[0]
    nWidth = pIr.shape[1]
    pIr2 = np.empty((nHeight, nWidth, 1), dtype=np.uint16)

    cdef unsigned short [:,:,:] pIr2_view = pIr2

    ret = SYErrorCode(Undistort(nDeviceID, <const unsigned short *>&pIr[0,0,0], nWidth, nHeight, False, &pIr2_view[0,0,0]))
    if ret != 0:
        raise RuntimeError(f"Undistort() returns {ret}.")

    return pIr2

def get_intrinsics(unsigned int nDeviceID, SYResolution resolution):
    cdef SYErrorCode ret
    cdef SYIntrinsics intrinsics

    ret = SYErrorCode(GetIntric(nDeviceID, resolution, intrinsics))
    if ret != 0:
        raise RuntimeError(f"GetIntric() returns {ret}.")

    return {
        "fov_x": intrinsics.m_fltFOV[0],
        "fov_y": intrinsics.m_fltFOV[1],
        "distortion_coeff_x": intrinsics.m_fltCoeffs[0],
        "distortion_coeff_y": intrinsics.m_fltCoeffs[1],
        "focal_length_x": intrinsics.m_fltFocalDistanceX,
        "focal_length_y": intrinsics.m_fltFocalDistanceY,
        "center_point_x": intrinsics.m_fltCenterPointX,
        "center_point_y": intrinsics.m_fltCenterPointY,
        "width": intrinsics.m_nWidth,
        "height": intrinsics.m_nHeight,
    }
