#!/usr/bin/env python
'''Test loadconfig script

tox is recommented for running this test file.
For manual run:
    pip install -rtests/test_requirements.txt
    python -m pytest tests/test_loadconfig.py
'''

from loadconfig.lib import addpath
addpath(__file__)
addpath(__file__, parent=True)

from loadconfig import Config
from loadconfig.lib import (exc, capture_stream, ppath, run, import_file,
    tempdir, tempfile)
from os.path import dirname
from pytest import fixture
from textwrap import dedent as d

# Import main function from loadconfig script.
# These extra steps are needed as loadconfig script doesn't end in .py
loadconfig_path = '{}/../scripts/loadconfig'.format(ppath(__file__))
loadconfig_module = import_file(loadconfig_path)
main = loadconfig_module.main


@fixture(scope='module')
def c(request):
    '''Config fixture. Return a config object for easy attribute access'''

    c = Config('''\
        prog: test_loadconfig.py
        test_version: 0.1.7

        conf: |
            version: $test_version
            clg:
                description: Build a full system
                options:
                    version:
                        short: v
                        action: version
                        version: $prog $test_version
                args:
                    host:
                        help: Host to build
                    args:
                        nargs: '*'
                        help: extra arguments
            checkconfig: |
                import re
                if re.search('[^\d\w]', '$host'):
                    raise Exception()

            system_path:       /data/salt/system
            docker__image:     reg.gdl/debian
        ''')

    # prog and version configs are hardcoded as this test runs in testsuite
    # Declare PYTHONPATH to use loadconfig package from this project
    c.project_path = dirname(ppath(__file__))
    c.loadconfig_cmd = 'PYTHONPATH={0} {0}/scripts/loadconfig'.format(
        c.project_path)
    return c


def test_main(c):
    '''loadconfig main unittest'''
    host = 'leon'
    conf_option = '-E="{}"'.format(c.conf)
    with capture_stream() as stdout:
        main([c.prog, conf_option, host])
    exp = d('''\
        export ARGS=""
        export DOCKER__IMAGE="reg.gdl/debian"
        export HOST="leon"
        export PROG="test_loadconfig.py"
        export SYSTEM_PATH="/data/salt/system"
        export VERSION="0.1.7"''')
    ret = '\n'.join(sorted(stdout.getvalue()[:-1].split('\n')))
    assert exp == ret


def test_main_usage(c):
    '''loadconfig main usage unittest'''
    conf_option = '-E="{}"'.format(c.conf)
    exp = '{} {}'.format(c.prog, c.test_version)
    with exc(SystemExit) as e:
        main([c.prog, conf_option, '-v'])
    assert exp == e().args[0]


def test_from_string(c):
    '''Functional test Config from string'''
    host = 'leon'
    cmd = '{} -E="{}" {}'.format(c.loadconfig_cmd, c.conf, host)
    ret = run(cmd)
    assert 'export SYSTEM_PATH="/data/salt/system"' in ret.stdout
    assert 'export HOST="{}"'.format(host) in ret.stdout


def test_from_directory(c):
    '''Functional test Config from directory (default on config.conf)'''
    host = 'leon'
    # Place conf in a temporary directory and run test
    with tempfile() as fh:
        fh.write(c.conf)
        fh.flush()
        cmd = '{} -C="{}" {}'.format(c.loadconfig_cmd, fh.name, host)
        ret = run(cmd)
    assert 'export SYSTEM_PATH="/data/salt/system"' in ret.stdout
    assert 'export HOST="{}"'.format(host) in ret.stdout


def test_options_are_cleaned(c):
    cmd = '{} -E="greet: hi"'.format(c.loadconfig_cmd)
    ret = run(cmd)
    assert 'export GREET="hi"' in ret.stdout
    assert 'export CONF=""' not in ret.stdout


def test_multiple_options_are_cleaned(c):
    '''test_multiple_options_are_cleaned.

    shell equivalent:
    $ load_config.py -E="greet: hi" -E="name: Jenny"
    export GREET=hi
    export NAME=cmd
    '''
    cmd = '{} -E="greet: hi" -E="name: Jenny"'.format(c.loadconfig_cmd)
    ret = run(cmd)
    assert 'export GREET="hi"' in ret.stdout
    assert 'export NAME="Jenny"' in ret.stdout
    assert 'export STR="name: Jenny"' not in ret.stdout
    assert 'export ARGS=""' not in ret.stdout


def test_extra_config_have_precedenced(c):
    host = 'leon'
    with tempdir() as tmpdir:
        with open('{}/config.conf'.format(tmpdir), 'w') as fh:
            fh.write(c.conf)
        cmd = '{} -C="{}" -E="system_path: /tmp/systest" {}'.format(
            c.loadconfig_cmd, tmpdir, host)
        ret = run(cmd)
    assert'export SYSTEM_PATH="/tmp/systest"' in ret.stdout


def test_extra_positional_arguments(c):
    '''Test extra positional arguments are properly handled.'''
    host = 'leon'
    cmd = '{} -E="{}" {} test'.format(c.loadconfig_cmd, c.conf, host)
    ret = run(cmd)
    assert 'export ARGS="test"' in ret.stdout


def test_verprog(c):
    '''Test version and program show properly.'''
    # argparse python 2.7 still send version option to stderr
    cmd = '{} -E="{}" -v'.format(c.loadconfig_cmd, c.conf)
    ret = run(cmd)
    assert '{} {}\n'.format(c.prog, c.test_version) == ret.stderr


def test_empty_extra_argument(c):
    cmd = '{} -E=""'.format(c.loadconfig_cmd)
    ret = run(cmd)
    assert 0 == ret.code
    assert '' == ret.stderr
