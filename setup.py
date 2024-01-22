#!/usr/bin/env python3

from setuptools import setup, find_packages
from synexens.version import version

setup(
    name="synexens",
    version=version,
    description="Wrapper for Synexens SDK to access their LiDAR devices",
    author=["Minh-Tri Pham"],
    packages=find_packages(),
    install_requires=[
        "mtbase",  # for numpy access
        "cython",  # for wrapping purposes
    ],
)
