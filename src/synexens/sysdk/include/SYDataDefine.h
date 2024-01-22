/*************************************************
文件描述：数据结构定义
创建者：王尉
创建版本：v1.0
**************************************************/
#ifndef SYDataDefine_h
#define SYDataDefine_h

#ifdef WIN32
#ifdef SYSDK_EXPORT
#define SYSDK_DLL __declspec(dllexport)
#else
#define SYSDK_DLL __declspec(dllimport)
#endif
#else
#define SYSDK_DLL
#endif

#pragma pack(1)

namespace Synexens
{
    //无效设备ID
    const unsigned int UNKOWN_DEVICE_ID = 0;
    //通讯类型
    //UVC
    const unsigned char SYCOMMUNICATETYPE_UVC = 0x01;
    //TCP
    const unsigned char SYCOMMUNICATETYPE_TCP = 0x02;

    //错误码
    enum SYErrorCode
    {
        //成功
        SYERRORCODE_SUCCESS = 0,
        //失败
        SYERRORCODE_FAILED = 1,
        //设备不存在
        SYERRORCODE_DEVICENOTEXIST = 2,
        //设备未打开
        SYERRORCODE_DEVICENOTOPENED = 3,
        //不支持的分辨率
        SYERRORCODE_UNKOWNRESOLUTION = 4,
        //设备指针句柄为空
        SYERRORCODE_DEVICEHANDLEEMPTY = 5,
        //设备输出数据格式设置失败
        SYERRORCODE_SETOUTPUTFORMATFAILED = 6,
        //获取视频流控制指针失败
        SYERRORCODE_GETSTREAMCTRLFAILED = 7,
        //启动视频流失败
        SYERRORCODE_STARTSTREAMINGFAILED = 8,
        //通讯指针为空
        SYERRORCODE_COMMUNICATEOBJECTEMPTY = 9,
        //无效的SN号
        SYERRORCODE_UNKOWNSN = 10,
        //字符串长度溢出
        SYERRORCODE_STRINGLENGTHOUTRANGE = 11,
        //无效帧类型
        SYERRORCODE_UNKOWNFRAMETYPE = 12,
        //无效设备类型
        SYERRORCODE_UNKOWNDEVICETYPE = 13,
        //设备对象指针为空
        SYERRORCODE_DEVICEOBJECTEMPTY = 14,
        //通知对象指针为空
        SYERRORCODE_OBSERVEREMPTY = 15,
        //通知对象未找到
        SYERRORCODE_OBSERVERNOTFOUND = 16,
        //数量溢出
        SYERRORCODE_COUNTOUTRANGE = 17,
        //UVC初始化失败
        SYERRORCODE_UVCINITFAILED = 18,
        //UVC查找设备失败
        SYERRORCODE_UVCFINDDEVICEFAILED = 19,
        //无数据帧
        SYERRORCODE_NOFRAME = 20,
        //程序路径获取失败
        SYERRORCODE_GETAPPFOLDERPATHFAILED = 21,
        //视频流未启动
        SYERRORCODE_NOSTREAMING = 22,
        //算法指针为空
        SYERRORCODE_RECONSTRUCTIONEMPTY = 23,
        //视频流已开启
        SYERRORCODE_STREAMINGEXIST = 24,
        //未知的流类型
        SYERRORCODE_UNKOWNSTREAMTYPE = 25,
        //数据指针为空
        SYERRORCODE_DATABUFFEREMPTY = 26,

    };

    //设备类型
    enum SYDeviceType
    {
        //无效
        SYDEVICETYPE_NULL = 0,
        //CS30双频
        SYDEVICETYPE_CS30_DUAL,
        //CS30单频
        SYDEVICETYPE_CS30_SINGLE,
        //CS20双频
        SYDEVICETYPE_CS20_DUAL,
        //CS20单频
        SYDEVICETYPE_CS20_SINGLE,
        //CS20_P
        SYDEVICETYPE_CS20_P,
        //CS40
        SYDEVICETYPE_CS40,
    };

    //数据流类型
    enum SYStreamType
    {
        //无效
        SYSTREAMTYPE_NULL = 0,
        //RAW
        SYSTREAMTYPE_RAW,
        //深度
        SYSTREAMTYPE_DEPTH,
        //RGB
        SYSTREAMTYPE_RGB,
        //深度+IR
        SYSTREAMTYPE_DEPTHIR,
        //深度+RGB
        SYSTREAMTYPE_DEPTHRGB,
        //深度+IR+RGB
        SYSTREAMTYPE_DEPTHIRRGB,
        //RGBD(mapping后的深度+RGB)
        SYSTREAMTYPE_RGBD,
        //RAW_RGB
        SYSTREAMTYPE_RAWRGB,
    };

    //分辨率枚举
    enum SYResolution
    {
        //无效
        SYRESOLUTION_NULL = 0,
        //320*240
        SYRESOLUTION_320_240,
        //640*480
        SYRESOLUTION_640_480,
        //960*540
        SYRESOLUTION_960_540,
        //1920*1080
        SYRESOLUTION_1920_1080,
    };

    //数据帧类型
    enum SYFrameType
    {
        //无效
        SYFRAMETYPE_NULL = 0,
        //RAW
        SYFRAMETYPE_RAW,
        //深度
        SYFRAMETYPE_DEPTH,
        //IR
        SYFRAMETYPE_IR,
        //RGB
        SYFRAMETYPE_RGB,
    };

    //支持的类型
    enum SYSupportType
    {
        //无效
        SYSUPPORTTYPE_NULL = 0,
        //深度
        SYSUPPORTTYPE_DEPTH,
        //RGB
        SYSUPPORTTYPE_RGB,
        //RGBD
        SYSUPPORTTYPE_RGBD,
    };

    //事件类型
    enum SYEventType
    {
        //无效
        SYEVENTTYPE_NULL = 0,
        //设备连接
        SYEVENTTYPE_DEVICECONNECT,
        //设备断开
        SYEVENTTYPE_DEVICEDISCONNECT,
    };

    //滤波类型
    enum SYFilterType
    {
        //无效
        SYFILTERTYPE_NULL = 0,
        //中值
        SYFILTERTYPE_MEDIAN,
        //幅值
        SYFILTERTYPE_AMPLITUDE,
        //边界
        SYFILTERTYPE_EDGE,
        //斑点
        SYFILTERTYPE_SPECKLE,
        //大金阈值
        SYFILTERTYPE_OKADA,
        //边界2
        SYFILTERTYPE_EDGE_MAD,
        //高斯
        SYFILTERTYPE_GAUSS,
        //备用
        SYFILTERTYPE_EXTRA,
        //备用2
        SYFILTERTYPE_EXTRA2,
    };

    //设备信息
    struct SYDeviceInfo
    {
        //设备唯一ID
        unsigned int m_nDeviceID = 0;
        //设备类型
        SYDeviceType m_deviceType = SYDEVICETYPE_NULL;
    };

    //事件信息
    struct SYEventInfo
    {
        //事件类型
        SYEventType m_eventType = SYEVENTTYPE_NULL;
        //事件信息数据
        void* m_pEventInfo = nullptr;
        //数据长度
        int m_nLength = 0;
    };

    //数据帧信息
    struct SYFrameInfo
    {
        //帧类型
        SYFrameType m_frameType = SYFRAMETYPE_NULL;
        //高度（像素）
        int m_nFrameHeight = 0;
        //宽度（像素）
        int m_nFrameWidth = 0;
    };

    //数据帧
    struct SYFrameData
    {
        //帧数量
        int m_nFrameCount = 0;
        //帧信息
        SYFrameInfo* m_pFrameInfo = nullptr;
        //帧数据
        void* m_pData = nullptr;
        //数据长度
        int m_nBuffferLength = 0;
    };

    //点云数据结构
    struct SYPointCloudData
    {
        //X
        float m_fltX = 0.f;
        //Y
        float m_fltY = 0.f;
        //Z
        float m_fltZ = 0.f;
    };

	//相机参数结构体
	struct SYIntrinsics
	{
		// 镜头视角
		float m_fltFOV[2];
		// 畸变系数
		float m_fltCoeffs[5];
		// x 方向的焦距
		float m_fltFocalDistanceX;
		// y 方向的焦距
		float m_fltFocalDistanceY;
		// x 方向的成像中心点 即cx
		float m_fltCenterPointX;
		// y 方向的成像中心点 即cy
		float m_fltCenterPointY;
		// 宽度
		int m_nWidth;
		// 高度
		int m_nHeight;
	};


}

#pragma pack()

#endif //SYDataDefine_h