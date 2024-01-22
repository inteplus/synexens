/*************************************************
文件描述：各对外信息通知接口类
创建者：王尉
创建版本：v1.0
**************************************************/
#ifndef SYObserverInterface_h
#define SYObserverInterface_h

#include "SYDataDefine.h"

namespace Synexens
{
    //错误信息通知接口类
    class SYSDK_DLL ISYErrorObserver
    {
    public:
        //错误信息通知
        //@ param [in] nErrorCode 错误码
        //@ param [in] pParam 额外错误信息，默认为空，可参照错误码表转换成相应数据类型指针以获取对应信息
        //@ return true-成功 false-失败
        virtual void OnErrorNotify(SYErrorCode nErrorCode, void* pParam = nullptr) = 0;
    };

    //事件通知接口类
    class SYSDK_DLL ISYEventObserver
    {
    public:
        //事件通知
        //@ param [in] nEventType 事件类型
        //@ param [in] pParam 事件信息，默认为空，可参照事件类型表转换成相应数据类型指针以获取对应信息
        //@ return true-成功 false-失败
        virtual void OnEventNotify(int nEventType, void* pParam = nullptr) = 0;
    };

    //帧数据通知接口类
    class SYSDK_DLL ISYFrameObserver
    {
    public:
        //帧数据通知
        //@ param [in] nDeviceID 设备ID
        //@ param [in] pFrameData 帧数据
        //@ return true-成功 false-失败
        virtual void OnFrameNotify(unsigned int nDeviceID, SYFrameData* pFrameData = nullptr) = 0;
    };

}

#endif //SYObserverInterface_h