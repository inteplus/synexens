#!/usr/bin/env python3

import os
import platform
from setuptools import Extension, setup, find_packages
from Cython.Build import cythonize

from mt import path, shutil


VERSION_FILE = os.path.join(os.path.dirname(__file__), "VERSION.txt")
version_from_file = open(VERSION_FILE).read()

if platform.machine() == "x86_64":
    plat = "amd64"
elif platform.machine() == "aarch64":
    plat = "arm64"
else:
    raise NotImplementedError

if False:
    setup_dirpath = path.dirname(__file__)
    src_dirpath = path.join(setup_dirpath, "sysdk", "lib", plat)
    dst_dirpath = path.join(setup_dirpath, "synexens")
    filenames = [
        "libSynexensSDK.so.4.1",
        "libcsreconstruction2.0.so.2.3",
        "libSonixCamera.so",
    ]
    for filename in filenames:
        src_filepath = path.join(src_dirpath, filename)
        dst_filepath = path.join(dst_dirpath, filename)
        path.remove(dst_filepath)
        shutil.copyfile(src_filepath, dst_filepath)

extensions = [
    Extension(
        "synexens_sdk",
        ["synexens_sdk.pyx"],
        include_dirs=["sysdk/include"],
        libraries=["SynexensSDK", "csreconstruction2.0", "SonixCamera"],
        library_dirs=[path.join("sysdk", "lib", plat)],
    )
]

setup(
    name="synexens",
    description="Wrapper for Synexens SDK to access their LiDAR devices",
    author=["Minh-Tri Pham"],
    packages=find_packages(),
    include_package_data=True,
    package_data={"": ["*.so*"]},
    install_requires=[
        "mtbase",  # for numpy access
        "cython",  # for wrapping purposes
        "v4l2py",  # for the interface
    ],
    ext_modules=cythonize(extensions),
    setup_requires=["setuptools-git-versioning<2"],
    python_requires=">=3.8",  # for asyncio to work properly
    setuptools_git_versioning={
        "enabled": True,
        "version_file": VERSION_FILE,
        "count_commits_from_version_file": True,
        "template": "{tag}",
        "dev_template": "{tag}.dev{ccount}+{branch}",
        "dirty_template": "{tag}.post{ccount}",
    },
)
