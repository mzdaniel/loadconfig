#!/usr/bin/env python
# Create wheel with:  python setup.py bdist_wheel
# Install with:       pip install dist/loadconfig-*-none-any.whl

from os import environ
from os.path import dirname, abspath
from setuptools import setup
import sys
if sys.version_info[0] == 3:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser

c = ConfigParser()
c.read('{}/setup.cfg'.format(dirname(abspath(__file__))))
environ["PBR_VERSION"] = c.get('metadata', 'version')
setup(setup_requires=['pbr'], pbr=True)
