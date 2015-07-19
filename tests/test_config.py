#!/usr/bin/env python
'''Test Config class

tox is recommented for running this test file.
For manual run:
    pip install -rtests/test_requirements.txt
    python -m pytest tests/test_config.py
'''

from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(abspath(__file__)))
from loadconfig.lib import addpath
addpath(__file__, parent=True)

from loadconfig import Config, Odict
from loadconfig.lib import (exc, run, tempdir, tempfile)
from os.path import basename
from pytest import fixture
import re
from textwrap import dedent


@fixture(scope='module')
def f(request):
    '''Config fixture. Return a generic object for easy attribute access'''
    class F(object):
        '''Generic config class for proper Config class testing'''
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
        project_path = dirname(dirname(abspath(__file__)))
    return F()


def test_empty_args(f):
    c = Config()
    assert [] == list(c)  # get c keys in a py2/3 compatible way


def test_arguments(f):
    c = Config('data_path: /data', types=[basename],
            args=[f.prog, '-e', '/data/conf/sasha.conf', f.host,
            '-E="{}"'.format(f.conf)])
    assert f.host == c.host
    assert '/data/data.txt' == c.data_file
    assert '/data/salt/system' == c.system_path
    assert 'sasha.conf' == c.extra_config


def test_string_argument(f):
    c = Config('hi: there')
    assert 'there' == c.hi


def test_update_with_string_argument(f):
    c = Config('hi: there')
    c.update('hi: Liss')
    assert 'Liss' == c.hi


def test_string_argument_value_integer_is_preserved(f):
    c = Config('year: 2015')
    assert 2015 == c.year


def test_clg_key_not_present(f):
    '''Config stores all args including program name'''
    c = Config(args=[f.prog, f.host, '-E="{}"'.format(f.conf)])
    assert 'clg' not in c


def test_extra_config_and_config_file(f):
    with tempfile() as fh:
        fh.write(f.conf)
        fh.flush()
        c = Config(args=[f.prog, f.host, '-C="{}"'.format(fh.name),
            '-E="system_path: /tmp/systest"'])
    assert '/tmp/systest' == c.system_path


def test_include_config(f):
    '''Test yaml !include tag loads config'''
    conf = 'field: magnetic'
    with tempfile() as fh:
        fh.write(conf)
        fh.flush()
        c = Config('photon: !include {}'.format(fh.name))
    assert Odict('field: magnetic') == c.photon


def test_include_tag(f):
    '''Test include with a key'''
    conf = 'field: [magnetic, electric]'
    with tempfile() as fh:
        fh.write(conf)
        fh.flush()
        c = Config('photon: !include {}:field'.format(fh.name))
        assert Odict('photon: [magnetic, electric]') == c


def test_include_unknown_key(f):
    '''Test include with a key'''
    conf = 'field: [magnetic, electric]'
    with tempfile() as fh:
        fh.write(conf)
        fh.flush()
        c = Config('photon: !include {}:properties'.format(fh.name))
        assert Odict("photon: ''") == c


def test_expand_tag(f):
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
        assert Odict('photon: [magnetic, electric]') == c


def test_expand_unknown_key(f):
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
        assert Odict("photon: ''") == c


def test_extra_config_expansion(f):
    c = Config(args=['-E="name: Jessica, greet: \'Hi ${name}\'"'])
    assert 'Hi Jessica' == c.greet


def test_extra_config_single_line_properly_handled(f):
    '''Config adds extra {} on single-line strings as yaml require'''
    c = Config(args=['-E="hobbie: dancer"'])
    assert 'dancer' == c.hobbie
    # As usual, multiline dictionaries are indented on the next line
    c = Config(args=['-E="hobbie:\n  dancer"'])
    assert 'dancer' == c.hobbie


def test_attribute_auto_expansion(f):
    c = Config(args=[f.prog, f.host, '-E="{}"'.format(f.conf),
        '-E="backup_path: /backup/$host.img"'])
    assert '/backup/leon.img' == c.backup_path


def test_verprog(f):
    '''Test version and program show properly.'''
    with exc(SystemExit) as e:
        Config({'version': f.version, 'prog': f.prog},
            args=[f.prog, '-v', '-E="{}"'.format(f.conf)], types={basename})
    assert '{} {}'.format(f.prog, f.version) == e().args[0]


def test_verprog_from_options(f):
    with tempfile() as fh, exc(SystemExit) as e:
        fh.write(f.conf)
        fh.flush()
        Config({'version': f.version, 'prog': f.prog}, types={basename}, args=[
            f.prog, '-v',
            '-E="prog: {}"'.format(f.prog),
            '-C="{}"'.format(fh.name),
            '-E="version: {}"'.format(f.version)])
    assert '{} {}'.format(f.prog, f.version) == e().args[0]


def test_convenient_config_file_from_directory(f):
    conf = '{color: [red, green, blue]}'
    with tempdir() as tmpdir:
        conf_file = '{}/config.conf'.format(tmpdir)
        with open(conf_file, 'w') as fh:
            fh.write(conf)
        c = Config(args=['-C={}'.format(tmpdir)])
    assert conf == repr(c)


def test_help(f):
    '''Test version and program show properly.'''
    with exc(SystemExit) as e:
        Config({'version': f.version, 'prog': f.prog},
        args=[f.prog, '-h', '-E="{}"'.format(f.conf)], types={basename})
    exp = dedent('''\
        usage: dbuild [-h] [-v] [-e EXTRA_CONFIG] host [args [args ...]]

        Build a full system

        positional arguments:
          host                  Host to build
          args                  extra arguments

        optional arguments:
          -h, --help            show this help message and exit
          -v, --version         show program's version number and exit
          -e EXTRA_CONFIG, --extra-config EXTRA_CONFIG''')
    assert exp == e().args[0]


def test_config(f):
    '''Test config process validate args, and generate envvars'''
    c = Config({'version': f.version, 'prog': f.prog},
               args=[f.prog, 'leon', '-E="{}"'.format(f.conf)])
    # Apparently clg return data out of order. Sort its output here.
    ret = '\n'.join(sorted(c.export().split('\n')))
    exp = dedent('''\
        export ARGS=""
        export DATA_FILE="$data_path/data.txt"
        export DOCKER__IMAGE="reg.gdl/debian"
        export EXTRA_CONFIG=""
        export HOST="leon"
        export PROG="dbuild"
        export SYSTEM_PATH="/data/salt/system"
        export VERSION="0.4.3"''')
    assert exp == ret


def test_export_list(f):
    c = Config('Outdoor activity: [hike, bike, scuba dive, run]')
    exp = '{Outdoor activity: [hike, bike, scuba dive, run]}'
    assert exp == repr(c)
    exp = 'export OUTDOOR_ACTIVITY="hike bike \'scuba dive\' run"'
    assert exp == c.export()


def test_export_dict(f):
    c = Config('Outdoor activity: {mountain: bike, ocean: scuba dive}')
    exp = '{Outdoor activity: {mountain: bike, ocean: scuba dive}}'
    assert exp == repr(c)
    exp = 'export OUTDOOR_ACTIVITY="{mountain: bike, ocean: scuba dive}"'
    assert exp == c.export()


def test_functional_verprog(f):
    '''Test version and program show properly.'''
    # argparse python 2.7 still send version option to stderr
    prog = 'demoscript.py'
    version = '0.1.5'
    cmd = 'PYTHONPATH={0} {0}/tests/fixtures/{1} -v'.format(
        f.project_path, prog)
    ret = run(cmd)
    regex = '^{} {}+[ \n]*$'.format(prog, version)
    assert re.search(regex, ret.stderr)


def test_fail_to_find_config(f):
    c = Config(args=['-C="not_config_e76a41.conf"'])
    assert '{}' == repr(c)
