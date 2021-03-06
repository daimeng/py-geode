#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='geode',
    version='0.3.20',
    description='Geode',
    author='Test',
    author_email='daimengchen@gmail.com',
    url='',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'pandas',
        'numpy',
        'scipy',
        'ujson',
        'asyncpg',
        'pyyaml',
        'tenacity'
    ])
