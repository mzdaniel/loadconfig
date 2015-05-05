#!/usr/bin/env python
'''Test Config class

tox is recommented for running this test file.
For manual run:
    python -m unittest test_config
'''
from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(abspath(__file__)))
from loadconfig.lib import addpath
addpath(__file__, parent=True)

from loadconfig import Config, Odict
from loadconfig.lib import (assertequal, capture_stream, exc, tempdir,
    tempfile, run)
from mock import patch
import os
from os.path import basename
from six import assertRegex
from six.moves import cStringIO
from tempfile import mkstemp
from textwrap import dedent as d
import unittest

project_path = dirname(dirname(abspath(__file__)))


class ConfigTest(unittest.TestCase):
    '''Test Config class'''
    conf = '''\
        clg:
            prog: $prog
            description: Build a full system
            options:
                version:
                    short: v
                    action: version
                    version: $prog $version
                extra_config:
                    short: e
                    type: basename
            args:
                host:
                    help: Host to build
                args:
                    nargs: '*'
                    help: extra arguments
        checkconfig: |
            import re
            if re.search('[^\d\w]', '$host'):
                raise Exception('Valid chars are [\d\w]. hostname: $host')

        system_path:        /data/salt/system
        data_file:          $data_path/data.txt
        docker__image:      reg.gdl/debian'''
    prog = 'dbuild'
    version = '0.4.3'
    host = 'leon'

    def test_empty_args(self):
        c = Config()
        assertequal([], list(c))  # get c keys in a py2/3 compatible way

    def test_arguments(self):
        c = Config('data_path: /data', types=[basename],
                args=[self.prog, '-e', '/data/conf/sasha.conf', self.host,
                '-E="{}"'.format(self.conf)])
        assertequal(self.host, c.host)
        assertequal('/data/data.txt', c.data_file)
        assertequal('/data/salt/system', c.system_path)
        assertequal('sasha.conf', c.extra_config)

    def test_string_argument(self):
        c = Config('hi: there')
        assertequal(c.hi, 'there')

    def test_update_with_string_argument(self):
        c = Config('hi: there')
        c.update('hi: Liss')
        assertequal(c.hi, 'Liss')

    def test_string_argument_value_integer_is_preserved(self):
        c = Config('year: 2015')
        assertequal(c.year, 2015)

    def test_clg_key_not_present(self):
        pass
        '''Config stores all args including program name'''
        c = Config(args=[self.prog, self.host, '-E="{}"'.format(self.conf)])
        assertequal(True, 'clg' not in c)

    def test_extra_config_and_config_file(self):
        with tempfile() as fh:
            fh.write(self.conf)
            fh.flush()
            c = Config(args=[self.prog, self.host, '-C="{}"'.format(fh.name),
                '-E="system_path: /tmp/systest"'])
        assertequal('/tmp/systest', c.system_path)

    def test_include_config(self):
        pass
        '''Test yaml !include tag loads config'''
        conf = 'field: magnetic'
        with tempfile() as fh:
            fh.write(conf)
            fh.flush()
            c = Config('photon: !include {}'.format(fh.name))
        assertequal(Odict('field: magnetic'), c.photon)

    def test_include_tag(self):
        pass
        '''Test include with a key'''
        conf = 'field: [magnetic, electric]'
        with tempfile() as fh:
            fh.write(conf)
            fh.flush()
            c = Config('photon: !include {}:field'.format(fh.name))
            assertequal(Odict('photon: [magnetic, electric]'), c)

    def test_include_unknown_key(self):
        pass
        '''Test include with a key'''
        conf = 'field: [magnetic, electric]'
        with tempfile() as fh:
            fh.write(conf)
            fh.flush()
            c = Config('photon: !include {}:properties'.format(fh.name))
            assertequal(Odict('photon: null'), c)

    def test_expand_tag(self):
        conf = '''\
            properties:
              field:
                - magnetic
                - electric'''
        with tempfile() as fh:
            fh.write(conf)
            fh.flush()
            c = Config('''\
                _: !include {}:&
                photon: !expand properties:field'''.format(fh.name))
            assertequal(c, Odict('photon: [magnetic, electric]'))

    def test_expand_unknown_key(self):
        conf = '''\
            properties:
              field:
                - magnetic
                - electric'''
        with tempfile() as fh:
            fh.write(conf)
            fh.flush()
            c = Config('''\
                _: !include {}:&
                photon: !expand properties:viscosity'''.format(fh.name))
            assertequal(c, Odict('photon: null'))

    def test_extra_config_expansion(self):
        c = Config(args=['-E="name: Jessica, greet: \'Hi ${name}\'"'])
        assertequal('Hi Jessica', c.greet)

    def test_extra_config_single_line_properly_handled(self):
        pass
        '''Config adds extra {} on single-line strings as yaml require'''
        c = Config(args=['-E="hobbie: dancer"'])
        assertequal('dancer', c.hobbie)
        # As usual, multiline dictionaries are indented on the next line
        c = Config(args=['-E="hobbie:\n  dancer"'])
        assertequal('dancer', c.hobbie)

    def test_attribute_auto_expansion(self):
        c = Config(args=[self.prog, self.host, '-E="{}"'.format(self.conf),
            '-E="backup_path:\n  /backup/${host}.img"'])
        assertequal('/backup/leon.img', c.backup_path)

    def test_verprog(self):
        pass
        '''Test version and program show properly.'''
        with capture_stream('stderr') as stderr:
            try:
                Config({'version': self.version, 'prog': self.prog},
                       args=[self.prog, '-v', '-E="{}"'.format(self.conf)])
            except SystemExit:
                pass
        assertequal('{} {}\n'.format(self.prog, self.version),
            stderr.getvalue())

    def test_verprog_from_options(self):
        with tempfile() as fh, capture_stream('stderr') as stderr:
            fh.write(self.conf)
            fh.flush()
            try:
                Config(args=[self.prog, '-v',
                    '-E="prog: {}"'.format(self.prog),
                    '-C="{}"'.format(fh.name),
                    '-E="version: {}"'.format(self.version)])
            except SystemExit:
                pass
        assertequal('{} {}\n'.format(self.prog, self.version),
            stderr.getvalue())

    def test_convenient_config_file_from_directory(self):
        conf = '{color: [red, green, blue]}'
        with tempdir() as tmpdir:
            conf_file = '{}/config.conf'.format(tmpdir)
            with open(conf_file, 'w') as fh:
                fh.write(conf)
            c = Config(args=['-C={}'.format(tmpdir)])
        assertequal(conf, repr(c))

    def test_verprog_with_no_version(self):
        pass
        '''Cover patch_argparse'''
        conf = self.conf.replace('version: $prog $version', '')
        with exc((SystemExit, AttributeError)), capture_stream(
         'stderr') as stderr:
            Config(conf, args=['', '-v'])
        assertequal('', stderr.getvalue())

    def test_help(self):
        pass
        '''Test version and program show properly.'''
        with exc(SystemExit), patch('sys.stderr', new_callable=cStringIO) as \
         stderr:
            Config({'version': self.version, 'prog': self.prog},
                args=[self.prog, '-h', '-E="{}"'.format(self.conf)])
        exp = d('''\
            usage: dbuild [-h] [-v] [-e EXTRA_CONFIG] host [args [args ...]]

            Build a full system

            positional arguments:
              host                  Host to build
              args                  extra arguments

            optional arguments:
              -h, --help            show this help message and exit
              -v, --version         show program's version number and exit
              -e EXTRA_CONFIG, --extra-config EXTRA_CONFIG
            ''')
        assertequal(exp, stderr.getvalue())

    def test_config(self):
        pass
        '''Test config process validate args, and generate envvars'''
        c = Config({'version': self.version, 'prog': self.prog},
                   args=[self.prog, 'leon', '-E="{}"'.format(self.conf)])
        # Apparently clg return data out of order. Sort its output here.
        ret = '\n'.join(sorted(c.export().split('\n')))
        exp = d('''\
            export ARGS=""
            export DATA_FILE="$data_path/data.txt"
            export DOCKER__IMAGE="reg.gdl/debian"
            export EXTRA_CONFIG=""
            export HOST="leon"
            export PROG="dbuild"
            export SYSTEM_PATH="/data/salt/system"
            export VERSION="0.4.3"''')
        assertequal(exp, ret)

    def test_export(self):
        c = Config('Outdoor activity: [hike, bike, scuba dive, run]')
        exp = '{Outdoor activity: [hike, bike, scuba dive, run]}'
        assertequal(exp, repr(c))
        exp = 'export OUTDOOR_ACTIVITY="hike bike \'scuba dive\' run"'
        assertequal(exp, c.export())

    def test_functional_verprog(self):
        pass
        '''Test version and program show properly.'''
        # argparse python 2.7 still send version option to stderr
        prog = 'demoscript.py'
        version = '0.1.5'
        cmd = 'PYTHONPATH={0} {0}/tests/fixtures/{1} -v'.format(
            project_path, prog)
        ret = run(cmd)
        assertRegex(self, ret.stderr, '^{} {}+[ \n]*$'.format(prog, version))

    def test_fail_to_find_config(self):
        with self.assertRaises(Exception) as e:
            Config(args=['-C="not_config_e76a41.conf"'])
        assertequal("Config file 'not_config_e76a41.conf' not found",
            e.exception.args[0])


class OdictTest(unittest.TestCase):
    '''Test Odict class'''

    def test_list_substitution(self):
        d = Odict('''\
                name:  &dancer
                  - Zeela
                  - Kim
                team:
                  *dancer
        ''')
        assertequal('{name: [Zeela, Kim], team: [Zeela, Kim]}', repr(d))

    def test_unexistent_include_config(self):
        pass
        '''Test yaml !include tag ignore unxexistent file'''
        tmpfile_fd, tmpfile = mkstemp()
        os.close(tmpfile_fd)
        os.remove(tmpfile)
        c = Config('_: !include {}'.format(tmpfile))
        assertequal('{}', repr(c))

    def test_empty_include_config(self):
        pass
        '''Test yaml !include tag ignore empty file'''
        with tempfile() as fh:
            c = Config('_: !include {}'.format(fh.name))
        assertequal('{}', repr(c))
