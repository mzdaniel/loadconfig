#!/usr/bin/env python
'''Test loadconfig library

tox is recommented for running this test file.
For manual run:
    pip install -rtests/test_requirements.txt
    python -m pytest tests/test_lib.py
'''
from loadconfig.lib import exc, last, Run, run, tempdir
from loadconfig.py6 import text_type
from os.path import isfile
from time import sleep


def test_Run():
    ret = Run('echo -e "Test Run class\nwith multiline args"', shell=False)
    assert "Test Run class\nwith multiline args\n" == ret.stdout
    assert 0 == ret.code


def test_Run_context():
    with tempdir() as tmp, Run('echo hi > ' + tmp + '/test.txt'):
        with open(tmp + '/test.txt') as fh:
            assert 'hi\n' == fh.read()
    assert not isfile(tmp + '/test.txt')


def test_Run_context_async():
    with Run('echo hi', async=True) as proc:
        assert 'hi\n' == proc.get_output()


def test_Run_stop():
    ret = Run('echo hi; sleep 1000000', async=True)
    sleep(0.2)
    ret.stop()
    assert 'hi\n' == ret.stdout


def test_run_inexistent_cmd():
    ret = run('not_script.sh')
    assert isinstance(ret, text_type)
    assert '' == ret
    assert ret.stderr.startswith('/bin/sh: not_script.sh:')
    assert 127 == ret.code
    assert 127 == ret._r['code']


def test_Run_unicode():
    '''Test unicode is handled properly'''
    with exc(UnicodeDecodeError) as e:
        Run("echo -e '\xe2'")
    assert not e()


def test_exc():
    with exc() as e:
        0 / 0
    assert isinstance(e(), ZeroDivisionError)


def test_last():
    assert None is last([])
