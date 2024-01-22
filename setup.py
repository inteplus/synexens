#!/usr/bin/env python3

import platform

from mt import path, shutil

from setuptools import setup, find_packages
from synexens.version import version

if platform.machine() == "x86_64":
    plat = "amd64"
elif platform.machine() == "aarch64":
    plat = "arm64"
else:
    raise NotImplementedError
setup_dirpath = path.dirname(__file__)
src_dirpath = path.join(setup_dirpath, "sysdk", "lib", plat)
dst_dirpath = path.join(setup_dirpath, "synexens")
for filepath in path.glob(src_dirpath + "/*.so"):
    dst_filepath = path.join(dst_dirpath, path.basename(filepath))
    shutil.copyfile(filepath, dst_filepath)

setup(
    name="synexens",
    version=version,
    description="Wrapper for Synexens SDK to access their LiDAR devices",
    author=["Minh-Tri Pham"],
    packages=find_packages(),
    include_package_data=True,
    package_data={"": ["*.so"]},
    install_requires=[
        "mtbase",  # for numpy access
        "cython",  # for wrapping purposes
    ],
)
