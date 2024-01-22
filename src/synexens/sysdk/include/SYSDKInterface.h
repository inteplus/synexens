/*************************************************
文件描述：SDK接口
创建者：王尉
创建版本：v1.0
**************************************************/
#ifndef SYSDKInterface_h
#define SYSDKInterface_h

#include "SYDataDefine.h"
#include "SYObserverInterface.h"

namespace Synexens
{
    //获取SDK版本号
    //@ param [in/out] nLength 字符长度
    //@ param [in/out] pstrSDKVersion SDK版本号字符串指针
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetSDKVersion(int& nLength, char* pstrSDKVersion = nullptr);

    //初始化SDK
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode InitSDK();

    //反初始化SDK，释放资源
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode UnInitSDK();

    //注册错误消息通知对象指针
    //@ param [in] pObserver 错误消息通知对象指针
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode RegisterErrorObserver(ISYErrorObserver* pObserver);

    //注册事件通知对象指针
    //@ param [in] pObserver 事件通知对象指针
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode RegisterEventObserver(ISYEventObserver* pObserver);

    //注册数据帧通知对象指针
    //@ param [in] pObserver 数据帧通知对象指针
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode RegisterFrameObserver(ISYFrameObserver* pObserver);

    //注销错误消息通知对象指针
    //@ param [in] pObserver 错误消息通知对象指针
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode UnRegisterErrorObserver(ISYErrorObserver* pObserver);

    //注销事件通知对象指针
    //@ param [in] pObserver 事件通知对象指针
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode UnRegisterEventObserver(ISYEventObserver* pObserver);

    //注销数据帧通知对象指针
    //@ param [in] pObserver 数据帧通知对象指针
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode UnRegisterFrameObserver(ISYFrameObserver* pObserver);

    //查找设备
    //@ param [in/out] nCount 设备数量
    //@ param [in/out] pDevice 设备信息，由外部分配内存，pDevice传入nullptr时仅获取nCount
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode FindDevice(int& nCount, SYDeviceInfo* pDevice = nullptr);

    //打开设备
    //@ param [in] deviceInfo 设备信息
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode OpenDevice(const SYDeviceInfo& deviceInfo);

    //关闭设备
    //@ param [in] nDeviceID 设备ID
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode CloseDevice(unsigned int nDeviceID);

    //查询设备支持类型
    //@ param [in] nDeviceID 设备ID
    //@ param [in/out] nCount 支持的数据帧类型数量,pSupportType为空时仅用作返回数量，否则用来校验pSupportType内存分配数量是否匹配
    //@ param [in/out] pSupportType 支持的类型，由外部分配内存，pSupportType传入nullptr时仅获取nCount
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode QueryDeviceSupportFrameType(unsigned int nDeviceID, int& nCount, SYSupportType * pSupportType = nullptr);

    //查询设备支持的帧分辨率
    //@ param [in] nDeviceID 设备ID
    //@ param [in] supportType 帧类型
    //@ param [in/out] nCount 支持的分辨率数量,pResolution为空时仅用作返回数量，否则用来校验pResolution内存分配数量是否匹配
    //@ param [in/out] pResolution 支持的分辨率类型，由外部分配内存，pResolution传入nullptr时仅获取nCount
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode QueryDeviceSupportResolution(unsigned int nDeviceID, SYSupportType supportType, int& nCount, SYResolution* pResolution = nullptr);

    //获取当前流类型
    //@ param [in] nDeviceID 设备ID
    //@ return 当前流类型
    extern "C" SYSDK_DLL SYStreamType GetCurrentStreamType(unsigned int nDeviceID);

    //启动数据流
    //@ param [in] nDeviceID 设备ID
    //@ param [in] streamType 数据流类型
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode StartStreaming(unsigned int nDeviceID, SYStreamType streamType);

    //停止数据流
    //@ param [in] nDeviceID 设备ID
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode StopStreaming(unsigned int nDeviceID);

    //切换数据流
    //@ param [in] nDeviceID 设备ID
    //@ param [in] streamType 数据流类型
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode ChangeStreaming(unsigned int nDeviceID, SYStreamType streamType);

    //设置分辨率（如果已启动数据流，内部会执行关流->设置分辨率->重新开流的操作流程）
    //@ param [in] nDeviceID 设备ID
    //@ param [in] frameType 帧类型
    //@ param [in] resolution 帧分辨率
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode SetFrameResolution(unsigned int nDeviceID, SYFrameType frameType, SYResolution resolution);

    //获取设备帧分辨率
    //@ param [in] nDeviceID 设备ID
    //@ param [in] frameType 帧类型
    //@ param [out] resolution 帧分辨率
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetFrameResolution(unsigned int nDeviceID, SYFrameType frameType, SYResolution& resolution);

    //获取滤波开启状态
    //@ param [in] nDeviceID 设备ID
    //@ param [out] bFilter 滤波开启状态，true-已开启滤波，false-未开启滤波
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetFilter(unsigned int nDeviceID, bool& bFilter);

    //开启/关闭滤波
    //@ param [in] nDeviceID 设备ID
    //@ param [in] bFilter 滤波开关，true-开启滤波，false-关闭滤波
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode SetFilter(unsigned int nDeviceID, bool bFilter);

    //获取滤波列表
    //@ param [in] nDeviceID 设备ID
    //@ param [in/out] nCount 滤波列表长度
    //@ param [in/out] pFilterType 滤波列表
    //@ return 错误码
    extern "C" SYSDK_DLL  SYErrorCode GetFilterList(unsigned int nDeviceID, int& nCount, SYFilterType* pFilterType = nullptr);

    //设置默认滤波
    //@ param [in] nDeviceID 设备ID
    //@ return 错误码
    extern "C" SYSDK_DLL  SYErrorCode SetDefaultFilter(unsigned int nDeviceID);

    //增加滤波
    //@ param [in] nDeviceID 设备ID
    //@ param [in] filterType 滤波类型
    //@ return 错误码
    extern "C" SYSDK_DLL  SYErrorCode AddFilter(unsigned int nDeviceID, SYFilterType filterType);

    //移除滤波
    //@ param [in] nDeviceID 设备ID
    //@ param [in] nIndex 滤波列表中的索引
    //@ return 错误码
    extern "C" SYSDK_DLL  SYErrorCode DeleteFilter(unsigned int nDeviceID, int nIndex);

    //清除滤波
    //@ param [in] nDeviceID 设备ID
    //@ return 错误码
    extern "C" SYSDK_DLL  SYErrorCode ClearFilter(unsigned int nDeviceID);

    //设置滤波参数
    //@ param [in] nDeviceID 设备ID
    //@ param [in] filterType 滤波类型
    //@ param [in] nParamCount 滤波参数个数
    //@ param [in] pFilterParam 滤波参数
    //@ return 错误码
    extern "C" SYSDK_DLL  SYErrorCode SetFilterParam(unsigned int nDeviceID, SYFilterType filterType, int nParamCount, float* pFilterParam);

    //获取滤波参数
    //@ param [in] nDeviceID 设备ID
    //@ param [in] filterType 滤波类型
    //@ param [in/out] nParamCount 滤波参数个数
    //@ param [in/out] pFilterParam 滤波参数
    //@ return 错误码
    extern "C" SYSDK_DLL  SYErrorCode GetFilterParam(unsigned int nDeviceID, SYFilterType filterType, int& nParamCount, float* pFilterParam = nullptr);

    //获取水平镜像状态
    //@ param [in] nDeviceID 设备ID
    //@ param [out] bMirror 水平镜像状态，true-已开启水平镜像，false-未开启水平镜像
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetMirror(unsigned int nDeviceID, bool& bMirror);

    //开启/关闭水平镜像
    //@ param [in] nDeviceID 设备ID
    //@ param [in] bMirror 水平镜像开关，true-开启水平镜像，false-关闭水平镜像
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode SetMirror(unsigned int nDeviceID, bool bMirror);

    //获取垂直翻转状态
    //@ param [in] nDeviceID 设备ID
    //@ param [out] bFlip 垂直翻转状态，true-已开启垂直翻转，false-未开启垂直翻转
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetFlip(unsigned int nDeviceID, bool& bFlip);

    //开启/关闭垂直翻转
    //@ param [in] nDeviceID 设备ID
    //@ param [in] bFlip 垂直翻转开关，true-开启垂直翻转，false-关闭垂直翻转
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode SetFlip(unsigned int nDeviceID, bool bFlip);

    //获取积分时间
    //@ param [in] nDeviceID 设备ID
    //@ param [out] nIntegralTime 积分时间
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetIntegralTime(unsigned int nDeviceID, int& nIntegralTime);

    //设置积分时间
    //@ param [in] nDeviceID 设备ID
    //@ param [in] nIntegralTime 积分时间
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode SetIntegralTime(unsigned int nDeviceID, int nIntegralTime);

    //获取积分时间调节范围
    //@ param [in] nDeviceID 设备ID
    //@ param [in] depthResolution depth分辨率
    //@ param [out] nMin 积分时间最小值
    //@ param [out] nMax 积分时间最大值
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetIntegralTimeRange(unsigned int nDeviceID, SYResolution depthResolution, int& nMin, int& nMax);

    //获取测距量程
    //@ param [in] nDeviceID 设备ID
    //@ param [out] nMin 量程最小值
    //@ param [out] nMax 量程最大值
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetDistanceMeasureRange(unsigned int nDeviceID, int& nMin, int& nMax);

    //获取用户测距范围
    //@ param [in] nDeviceID 设备ID
    //@ param [out] nMin 测距范围最小值
    //@ param [out] nMax 测距范围最大值
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetDistanceUserRange(unsigned int nDeviceID, int& nMin, int& nMax);

    //设置用户测距范围
    //@ param [in] nDeviceID 设备ID
    //@ param [in] nMin 测距范围最小值
    //@ param [in] nMax 测距范围最大值
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode SetDistanceUserRange(unsigned int nDeviceID, int nMin, int nMax);

    //读取设备sn号
    //@ param [in] nDeviceID 设备ID
    //@ param [in/out] nLength 字符长度
    //@ param [in/out] pstrSN 设备sn号字符串指针,由外部分配内存，pstrSN传入nullptr时仅获取nLength
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetDeviceSN(unsigned int nDeviceID, int& nLength, char* pstrSN = nullptr);

    //写入设备sn号
    //@ param [in] nDeviceID 设备ID
    //@ param [in] nLength 字符长度
    //@ param [in] pstrSN 设备sn号字符串指针
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode SetDeviceSN(unsigned int nDeviceID, int nLength, const char* pstrSN);

    //读取设备固件版本号
    //@ param [in] nDeviceID 设备ID
    //@ param [in/out] nLength 字符长度
    //@ param [in/out] pstrHWVersion 固件版本号字符串指针,由外部分配内存，pstrHWVersion传入nullptr时仅获取nLength
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetDeviceHWVersion(unsigned int nDeviceID, int& nLength, char* pstrHWVersion = nullptr);

    //获取深度对应伪彩色
    //@ param [in] nDeviceID 设备ID
    //@ param [in] nCount 数据量(内存空间pDepth需要nCount*2字节，pColor需要nCount*3字节)
    //@ param [in] pDepth 深度数据
    //@ param [in/out] pColor 深度对应伪彩色(24位RGB格式)
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetDepthColor(unsigned int nDeviceID, int nCount, const unsigned short* pDepth, unsigned char* pColor);

    //获取深度对应点云数据
    //@ param [in] nDeviceID 设备ID
    //@ param [in] nWidth 宽度
    //@ param [in] nHeight 高度
    //@ param [in] pDepth 深度数据
    //@ param [in/out] pPointCloud 深度对应点云数据,由外部分配内存
    //@ param [in] bUndistort 裁剪标志，true-裁剪 false-不裁剪
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetDepthPointCloud(unsigned int nDeviceID, int nWidth, int nHeight, const unsigned short* pDepth, SYPointCloudData* pPointCloud, bool bUndistort = false);

    //获取RGBD
    //@ param [in] nDeviceID 设备ID
    //@ param [in] nSourceDepthWidth 源深度数据宽度
    //@ param [in] nSourceDepthHeight 源深度数据高度
    //@ param [in] pSourceDepth 源深度数据
    //@ param [in] nSourceRGBWidth 源RGB数据宽度
    //@ param [in] nSourceRGBHeight 源RGB数据高度
    //@ param [in] pSourceRGB 源RGB数据
    //@ param [in] nTargetWidth RGBD数据宽度
    //@ param [in] nTargetHeight RGBD数据高度
    //@ param [in/out] pTargetDepth RGBD中的深度数据,由外部分配内存,数据长度与源RGB长度一致
    //@ param [in/out] pTargetRGB RGBD中的RGB数据,由外部分配内存,数据长度与源RGB长度一致
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetRGBD(unsigned int nDeviceID, int nSourceDepthWidth, int nSourceDepthHeight, unsigned short* pSourceDepth, int nSourceRGBWidth, int nSourceRGBHeight, unsigned char* pSourceRGB, int nTargetWidth, int nTargetHeight, unsigned short* pTargetDepth, unsigned char* pTargetRGB);

    //获取最新一帧数据
    //@ param [in] nDeviceID 设备ID
    //@ param [in/out] pFrameData 最后一帧数据
    //@ return 错误码
    extern "C" SYSDK_DLL SYErrorCode GetLastFrameData(unsigned int nDeviceID, SYFrameData*& pFrameData);

    //去畸变
    //@ param [in] nDeviceID 设备ID
    //@ param [in] pSource  待去畸变数据指针
    //@ param [in] nWidth 图像宽度
    //@ param [in] nHeight 图像高度
    //@ param [in] bDepth 是否是深度数据/RGB数据
    //@ param [out] pTarget  去畸变结果数据指针，由外部分配内存,数据长度与待去畸变数据指针长度一致
    extern "C" SYSDK_DLL SYErrorCode Undistort(unsigned int nDeviceID, const unsigned short* pSource, int nWidth, int nHeight, bool bDepth, unsigned short* pTarget);

    //获取相机参数
    //@ param [in] nDeviceID 设备ID
    //@ param [in] resolution  分辨率
    //@ param [in/out] intrinsics 相机参数
    extern "C" SYSDK_DLL SYErrorCode GetIntric(unsigned int nDeviceID, SYResolution resolution, SYIntrinsics& intrinsics);

}

#endif //SYSDKInterface_h