#!/usr/bin/env python
# Create wheel with:  python setup.py bdist_wheel
# Install with:       pip install -U dist/loadconfig-*.whl

from os import environ
from re import sub
from setuptools import setup

for line in open('loadconfig/__init__.py'):
    if line.startswith('__version__'):
        version = sub(".+'(.+?)'", r'\1', line)

environ["PBR_VERSION"] = version

setup(setup_requires=['pbr'], pbr=True)
