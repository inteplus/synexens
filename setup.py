#!/usr/bin/env python3

from setuptools import setup, find_packages
from mt.sql.version import VERSION

setup(
    name='sqlmt',
    version=VERSION,
    description="Extra Python modules to deal with the interaction between pandas dataframes and remote SQL servers, for Minh-Tri Pham. This package is now deprecated. Use package 'mtsql' instead.",
    author=["Minh-Tri Pham"],
    packages=find_packages(),
    install_requires=[
        'sqlalchemy',  # for psql access
        'tzlocal',  # for getting the local timezone
        'psycopg2-binary',  # for psql access
        # 'mysql', # for mysql access
        'pandasmt>=0.1.0',
        'mtsql',
    ],
)
