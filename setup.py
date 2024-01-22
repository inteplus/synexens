#!/usr/bin/env python3

import platform

from setuptools import setup, find_packages
from synexens.version import version

if platform.machine() == "x86_64":
    plat = "amd64"
elif platform.machine() == "aarch64":
    plat = "arm64"
else:
    raise NotImplementedError

setup(
    name="synexens",
    version=version,
    description="Wrapper for Synexens SDK to access their LiDAR devices",
    author=["Minh-Tri Pham"],
    packages=find_packages(),
    package_data={"synexens.sysdk.lib.amd64": ["*.so"], "": ["*.so"]},
    include_package_data=True,
    install_requires=[
        "mtbase",  # for numpy access
        "cython",  # for wrapping purposes
    ],
)
