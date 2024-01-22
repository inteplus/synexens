from libcpp cimport bool
from libcpp.string cimport string

from .sysdk cimport InitSDK, UnInitSDK

def init_sdk():
    return InitSDK()

def uninit_sdk():
    return UnInitSDK()
