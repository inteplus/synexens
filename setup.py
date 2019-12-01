#!/usr/bin/env python3

from setuptools import setup, find_packages
from sqlmt.version import VERSION as version

setup(
    name='sqlmt',
    version=version,
    description="Extra Python modules to deal with the interaction between pandas dataframes and remote SQL servers, for Minh-Tri Pham",
    author=["Minh-Tri Pham"],
    packages=find_packages(),
    install_requires=[
        'sqlalchemy',  # for psql access
        'tzlocal',  # for getting the local timezone
        'psycopg2-binary',  # for psql access
        # 'mysql', # for mysql access
        'basemt',  # Minh-Tri's base modules for logging and multi-threading
        'pandasmt',
    ],
)
