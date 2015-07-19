#!/usr/bin/env python
# Create wheel with:  python setup.py bdist_wheel
# Install with:       pip install -U dist/loadconfig-*.whl

from os import environ
from setuptools import setup
import sys

sys.path.append('.')
from loadconfig import __version__
environ["PBR_VERSION"] = __version__

setup(setup_requires=['pbr'], pbr=True)
