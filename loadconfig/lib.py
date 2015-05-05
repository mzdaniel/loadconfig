'''loadconfig library helpers

tox is recommented for testing this file.
For partial manual run:
    python -m doctest lib.py -v
'''
__all__ = ['addpath', 'assertequal', 'capture_stream', 'delregex', 'dfl',
    'exc', 'findregex', 'import_file', 'read_config_file', 'ppath', 'run',
    'set_verprog', 'tempdir', 'tempfile']
__author__ = 'Daniel Mizyrycki'

import argparse
import clg
from contextlib import contextmanager
from pip import get_installed_distributions
from os.path import basename, dirname, abspath, exists, isdir, isfile
import os
import re
from shutil import rmtree
from six.moves import cStringIO
from subprocess import Popen, PIPE
from string import Template
import sys
from tempfile import mkdtemp, mkstemp
from types import ModuleType


def addpath(path, parent=False):
    '''Add path to syspath (or path dirname if it is a file)

    >>> addpath('/var')
    >>> '/var' == sys.path[0]
    True
    >>> addpath(__file__)
    >>> abspath(dirname(__file__)) == sys.path[0]
    True
    >>> addpath('/tmp', parent=True)
    >>> '/tmp' == sys.path[0]
    False
    >>> '/' == sys.path[0]
    True
    '''
    def _addpath(path):
        if isdir(path):
            sys.path.insert(0, path)
        else:
            sys.path.insert(0, dirname(path))

    path = abspath(path)
    assert exists(path), 'path {} does not exist.'.format(path)
    if parent:
        if isfile(path):
            path = dirname(path)
        _addpath(dirname(path))
    else:
        _addpath(path)


def assertequal(a, b, msg=''):
    '''Assert 2 values are equal

    >>> assertequal('seagull', 'dolphin', 'Different animals')
    Traceback (most recent call last):
        ...
    AssertionError: Different animals 'seagull' != 'dolphin'
    '''
    if a != b:
        raise AssertionError("{} '{}' != '{}'".format(msg, a, b))


@contextmanager
def capture_stream(stream_name='stdout'):
    r'''Capture stream (stdout/stderr) in a string

    >>> with capture_stream() as stdout:
    ...     print('Hi there')
    >>> stdout.getvalue()
    'Hi there\n'
    '''
    stream = getattr(sys, stream_name)
    data = cStringIO()
    setattr(sys, stream_name, data)
    yield data
    setattr(sys, stream_name, stream)
    data.flush()


def delregex(regex, args):
    '''Delete all elements with regex from a list of strings

    >>> args = ['test', '-E="plant: carrot"', '-E="color: orange"']
    >>> delregex('^-E', args)
    ['test']
    '''
    match = list(filter(lambda x: not re.search(regex, str(x)), args))
    return match


def dfl(value, dfl=''):
    '''Return default value if argument is None or empty string

    >>> dfl('big', 'small')
    'big'
    >>> dfl(None, 'Hi')
    'Hi'
    '''
    return value if value not in [None, ''] else dfl


@contextmanager
def exc(exception):
    '''Swallow exceptions

    >>> with exc(ZeroDivisionError):
    ...     0/0
    '''
    try:
        yield
    except exception:
        pass


def findregex(regex, args):
    '''Find all elements matching regex

    >>> args = ['test', '-E="plant: carrot"', '-E="color: orange"']
    >>> findregex('^-E', args)
    ['-E="plant: carrot"', '-E="color: orange"']
    '''
    return list(filter(lambda x: re.search(regex, str(x)), args))


def import_file(filepath):
    '''Return filepath as a module

    >>> libpy = import_file('{}/lib.py'.format(ppath(__file__)))
    >>> 'import_file' in libpy.__dict__
    True
    '''
    module_name = basename(filepath).partition('.')[0]
    module = ModuleType(module_name)
    with open(filepath) as fh:
        data = fh.read()
    exec(data, module.__dict__)
    return module


def read_config_file(config_path):
    if isdir(config_path):
        config_path = '{}/config.conf'.format(config_path)
    if not(isfile(config_path)):
        raise Exception("Config file '{}' not found".format(config_path))
    with open(config_path) as fh:
        return str(fh.read())


def ppath(path):
    '''Get absolute parent path.
    >>> os.chdir('/var/tmp')
    >>> ppath('test_file')
    '/var/tmp'
    '''
    return dirname(abspath(path))


def run(cmd, **kwargs):
    r'''Execute command cmd. Return stdout, stderr, (ret)code

    >>> run('echo $((1+1))').stdout
    '2\n'
    >>> ret = run('not_script.sh')
    >>> ret.stdout, ret.stderr, ret.code
    ('', '/bin/bash: not_script.sh: command not found\n', 127)
    '''
    class ret(object):  # define a return object
        pass
    kwargs['universal_newlines'] = kwargs.get('universal_newlines', True)
    p = Popen(['/bin/bash', '-c', cmd], stdout=PIPE, stderr=PIPE, **kwargs)
    ret.stdout, ret.stderr = p.communicate()
    ret.code = p.returncode
    return ret


def set_verprog(template, version=None, prog=None):
    '''Add program name and version to a config template string.

    Shell programs need to define prog. prog is optional for python programs

    >>> conf = 'version: $prog $version'
    >>> set_verprog(conf, '0.1.2')  # doctest: +ELLIPSIS
    'version: ... 0.1.2'
    '''
    data = {'prog': dfl(prog, basename(sys.argv[0]))}
    if version:
        data['version'] = version
    return Template(template).safe_substitute(**data)


@contextmanager
def tempdir():
    '''Create and remove temporary directory

    >>> with tempdir() as tmpdir:
    ...     isdir(tmpdir)
    True
    >>> with tempdir() as tmpdir:
    ...     pass
    >>> isdir(tmpdir)
    False
    '''
    tmpdir = mkdtemp()
    yield tmpdir
    rmtree(tmpdir)


@contextmanager
def tempfile():
    '''Create a temporary file, returning its file handle. Remove it on exit.

    >>> with tempfile() as fh:
    ...    _ = fh.write('Hi there')
    ...    _ = fh.seek(0)
    ...    fh.read()
    'Hi there'
    >>> with tempfile() as fh:
    ...     isfile(fh.name)
    True
    >>> isfile(fh.name)
    False
    '''
    tmpfile = mkstemp()
    os.close(tmpfile[0])
    filehandle = open(tmpfile[1], 'w+')
    yield filehandle
    filehandle.close()
    os.remove(tmpfile[1])


def _get_option(option_string):
    '''Get the value and option letter of an argument

    >>> _get_option("-C='/data/conf/build.conf'")
    ('/data/conf/build.conf', 'C')
    '''
    assert re.search('^-\w', option_string)
    option = option_string[1]
    value = (option_string[3:] if option_string[3:4] not in ['"', "'"]
        else option_string[4:-1])
    return value, option


def _get_version():
    '''Get version from package installer using this module name'''
    pkgs = get_installed_distributions()
    return {e.key: e.version for e in pkgs}.get(
        basename(dirname(abspath(__file__))))


@contextmanager
def _patch_argparse_clg(types):
    '''Temporarely patch argparse and clg

    Use stderr to print help and version. Allow line breaks on clg.
    Add custom types to clg. stdout is best used for shell export envvars.
    '''
    # argparse_HelpFormatter = argparse.HelpFormatter
    # # Monkeypatch argparse and clg
    stdout = sys.stdout
    sys.stdout = sys.stderr
    argparse_HelpFormatter = argparse.HelpFormatter
    argparse.HelpFormatter = argparse.RawTextHelpFormatter
    TYPES = clg.TYPES
    # clg expects a dictionary with function name as keys
    types = {e.__name__: e for e in types}
    clg.TYPES.update(types)
    try:
        yield
    finally:
        # Un-monkeypatch argparse and clg
        clg.TYPES = TYPES
        argparse.HelpFormatter = argparse_HelpFormatter
        sys.stdout = stdout
