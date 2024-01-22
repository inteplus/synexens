# distutils: language = c++
# distutils: language_level = 3

from libcpp cimport bool
from libcpp.string cimport string

cdef extern from "SYSDKInterface.h" namespace "Synexens" nogil:
    # ----- constants -----

    # ----- enums -----

    enum SYErrorCode:  # 错误码
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

def init_sdk():
    return InitSDK()

def uninit_sdk():
    return UnInitSDK()
