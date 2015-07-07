#!/usr/bin/env python
'''Test Config library

tox is recommented for running this test file.
For manual run:
    pip install -rtests/test_requirements.txt
    python -m pytest tests/test_lib.py
'''
from loadconfig.lib import run


def test_run():
    ret = run('not_script.sh')
    assert '' == ret.stdout
    assert '/bin/sh: not_script.sh: command not found\n' == ret.stderr
    assert 127 == ret.code
    assert 65536 > ret.pid
    assert 127 == ret._r['code']
