#!/usr/bin/env python
'''Test loadconfig script

tox is recommented for running this test file.
For manual run:
    python -m unittest test_loadconfig
'''

from loadconfig.lib import addpath
addpath(__file__)
addpath(__file__, parent=True)

from loadconfig.lib import (assertequal, capture_stream, ppath, run,
    import_file, set_verprog, tempdir, tempfile)
from os.path import dirname
from six import assertRegex
from textwrap import dedent as d
import unittest

# Import main function from loadconfig script.
# These extra steps are needed as loadconfig script doesn't end in .py
loadconfig_path = '{}/../scripts/loadconfig'.format(ppath(__file__))
module = import_file(loadconfig_path)
main = module.main

prog = 'test_loadconfig.py'
test_version = '0.1.7'
project_path = dirname(ppath(__file__))


class ConfigLoadTest(unittest.TestCase):
    '''Test load_config.py class'''

    conf = '''\
        clg:
            prog: $prog
            description: Build a full system
            options:
                version:
                    short: v
                    action: version
                    version: $prog $version
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
        docker__image:     reg.gdl/debian'''

    # load program and version from this test module (string substitution)
    # prog argument is hardcoded as this test may be running under testsuite
    conf = set_verprog(conf, test_version, prog)

    # Declare PYTHONPATH to use loadconfig package from this project
    loadconfig_cmd = 'PYTHONPATH={0} {0}/scripts/loadconfig'.format(
        project_path)

    def test_main(self):
        pass
        '''loadconfig main unittest'''
        host = 'leon'
        conf_option = '-E="{}"'.format(self.conf)
        with capture_stream() as stdout:
            main([prog, conf_option, host])
        exp = d('''\
            export ARGS=""
            export DOCKER__IMAGE="reg.gdl/debian"
            export HOST="leon"
            export SYSTEM_PATH="/data/salt/system"''')
        ret = '\n'.join(sorted(stdout.getvalue()[:-1].split('\n')))
        assertequal(exp, ret)

    def test_main_usage(self):
        pass
        '''loadconfig main usage unittest'''
        conf_option = '-E="{}"'.format(self.conf)
        exp = '{} {}'.format(prog, test_version)
        with capture_stream('stderr') as stderr:
            try:
                main([prog, conf_option, '-v'])
            except SystemExit:
                pass
        assertequal(exp, stderr.getvalue()[:-1])

    def test_from_string(self):
        pass
        '''Functional test Config from string'''
        host = 'leon'
        cmd = '{} -E="{}" {}'.format(self.loadconfig_cmd, self.conf, host)
        ret = run(cmd)
        self.assertIn('export SYSTEM_PATH="/data/salt/system"', ret.stdout)
        self.assertIn('export HOST="{}"'.format(host), ret.stdout)

    def test_from_directory(self):
        pass
        '''Functional test Config from directory (default on config.conf)'''
        host = 'leon'
        # Place conf in a temporary directory and run test
        with tempfile() as fh:
            fh.write(self.conf)
            fh.flush()
            cmd = '{} -C="{}" {}'.format(self.loadconfig_cmd, fh.name, host)
            ret = run(cmd)
        self.assertIn('export SYSTEM_PATH="/data/salt/system"', ret.stdout)
        self.assertIn('export HOST="{}"'.format(host), ret.stdout)

    def test_options_are_cleaned(self):
        cmd = '{} -E="greet: hi"'.format(self.loadconfig_cmd)
        ret = run(cmd)
        self.assertIn('export GREET="hi"', ret.stdout)
        self.assertNotIn('export CONF=""', ret.stdout)

    def test_multiple_options_are_cleaned(self):
        pass
        '''test_multiple_options_are_cleaned.

        shell equivalent:
        $ load_config.py -E="greet: hi" -E="name: Jenny"
        export GREET=hi
        export NAME=Jenny
        '''
        cmd = '{} -E="greet: hi" -E="name: Jenny"'.format(self.loadconfig_cmd)
        ret = run(cmd)
        self.assertIn('export GREET="hi"', ret.stdout)
        self.assertIn('export NAME="Jenny"', ret.stdout)
        self.assertNotIn('export STR="name: Jenny"', ret.stdout)
        self.assertNotIn('export ARGS=""', ret.stdout)

    def test_extra_config_have_precedenced(self):
        host = 'leon'
        with tempdir() as tmpdir:
            with open('{}/config.conf'.format(tmpdir), 'w') as fh:
                fh.write(self.conf)
            cmd = '{} -C="{}" -E="system_path: /tmp/systest" {}'.format(
                self.loadconfig_cmd, tmpdir, host)
            ret = run(cmd)
        self.assertIn('export SYSTEM_PATH="/tmp/systest"', ret.stdout)

    def test_extra_positional_arguments(self):
        pass
        '''Test extra positional arguments are properly handled.'''
        host = 'leon'
        cmd = '{} -E="{}" {} test'.format(self.loadconfig_cmd, self.conf, host)
        ret = run(cmd)
        self.assertIn('export ARGS="test"', ret.stdout)

    def test_verprog(self):
        pass
        '''Test version and program show properly.'''
        # argparse python 2.7 still send version option to stderr
        cmd = '{} -E="{}" -v'.format(self.loadconfig_cmd, self.conf)
        ret = run(cmd)
        assertRegex(self, ret.stderr, '^{} {}$'.format(prog, test_version))

    def test_empty_extra_argument(self):
        pass
        cmd = '{} -E=""'.format(self.loadconfig_cmd)
        ret = run(cmd)
        assertequal(ret.code, 0)
        assertequal(ret.stderr, '')
