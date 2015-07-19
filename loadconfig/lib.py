'''loadconfig library helpers

tox is recommented for testing this file.
For partial manual run:
    python -m doctest lib.py -v
'''
__all__ = ['addpath', 'capture_stream', 'delregex', 'dfl', 'exc', 'findregex',
    'import_file', 'read_config_file', 'ppath', 'run', 'tempdir', 'tempfile']
__author__ = 'Daniel Mizyrycki'

import argparse
import clg
from contextlib import contextmanager
import os
from os import remove
from os.path import basename, dirname, abspath, exists, isdir, isfile
from pip import get_installed_distributions
from py6 import cStringIO
import re
from shutil import rmtree
from subprocess import Popen, PIPE
import sys
from tempfile import mkdtemp, mkstemp
from types import ModuleType


def addpath(path, parent=False):
    '''Add path to syspath (or path dirname if it is a file)

    >>> addpath('/var')
    '/var'
    >>> '/var' == sys.path[0]
    True
    >>> ret = addpath(__file__)
    >>> ret == abspath(dirname(__file__)) == sys.path[0]
    True
    >>> addpath('/tmp', parent=True)
    '/'
    >>> '/tmp' == sys.path[0]
    False
    >>> '/' == sys.path[0]
    True
    '''
    def _addpath(path):
        if isdir(path):
            sys.path.insert(0, path)
            return path
        else:
            sys.path.insert(0, dirname(path))
            return dirname(path)

    path = abspath(path)
    assert exists(path), 'path {} does not exist.'.format(path)
    if parent:
        if isfile(path):
            path = dirname(path)
        path = _addpath(dirname(path))
    else:
        path = _addpath(path)
    return path


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


def first(l):
    '''Get first element of a list or generator. Return None if empty.

    >>> first([1,2,3])
    1
    '''
    return next(iter(l), None)


@contextmanager
def exc(exception=BaseException):
    '''Swallow exceptions

    >>> with exc(ZeroDivisionError) as e:
    ...     0/0
    >>> isinstance(e(), ZeroDivisionError)
    True
    '''
    try:
        e = None
        yield lambda: e
    except BaseException as ex:
        e = ex


def flatten(l):
    '''Flatten a list

    >>> flatten([[1, 2], 3, 4])
    [1, 2, 3, 4]
    '''
    ret = []
    for e in l:
        if isinstance(e, (list, tuple)):
            ret += flatten(e)
        else:
            ret.append(e)
    return ret


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


def ppath(path):
    '''Get absolute parent path.
    >>> os.chdir('/var/tmp')
    >>> ppath('test_file')
    '/var/tmp'
    '''
    return dirname(abspath(path))


def read_file(file_path):
    with exc(IOError), open(file_path) as fh:
        return str(fh.read())
    return ''


def read_config_file(config_path):
    if isdir(config_path):
        config_path = '{}/config.conf'.format(config_path)
    return(read_file(config_path))


def run(cmd, **kwargs):
    r'''Execute command cmd. Return stdout, stderr, (ret)code and pid
    >>> ret = run('echo $((1+1))')
    >>> ret
    '2\n'
    >>> ret.code
    0
    >>> ret = run('not_script.sh')
    >>> ret.stdout, ret.stderr, ret.code, ret.pid
    ('', '/bin/sh: not_script.sh:...not found\n', 127, ...)
    '''
    class Ret(str):
        _r = property(lambda self: self.__dict__)
    kwargs['universal_newlines'] = kwargs.get('universal_newlines', True)
    kwargs['stdout'] = kwargs.get('stdout', PIPE)
    kwargs['stderr'] = kwargs.get('stderr', PIPE)
    kwargs['shell'] = kwargs.get('shell', True)
    proc = Popen(cmd, **kwargs)
    stdout, stderr = proc.communicate()
    ret = Ret(stdout)
    ret.stdout = stdout
    ret.stderr = stderr
    ret.code = proc.returncode
    ret.pid = proc.pid
    return ret


def tempdir(ctx=True):
    '''Create temporary directory and remove it when used as contextmanager.

    >>> with tempdir() as tmpdir:
    ...     isdir(tmpdir)
    True
    >>> with tempdir() as tmpdir:
    ...     pass
    >>> isdir(tmpdir)
    False
    >>> isinstance(tempdir(ctx=False), str)
    True
    '''
    @contextmanager
    def _tempdir():
        tmpdir = mkdtemp()
        yield tmpdir
        rmtree(tmpdir)

    if ctx:
        return _tempdir()
    return mkdtemp()


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
    tmpfile_fd, tmpfile = mkstemp()
    os.close(tmpfile_fd)
    filehandle = open(tmpfile, 'w+')
    yield filehandle
    filehandle.close()
    remove(tmpfile)


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


def _get_version(package):
    '''Get version from package installer

    >>> from pip import __version__
    >>> __version__ == _get_version('pip')
    True
    '''
    pkgs = get_installed_distributions()
    return {e.key: e.version for e in pkgs}.get(package, '')


@contextmanager
def _patch_argparse_clg(args, types):
    '''Temporarely patch argparse and clg

    Use stderr to print help and version. Allow line breaks on clg.
    Add custom types to clg. stdout is best used for shell export envvars.
    Replace help and version exit status by 1 instead of 0.
    '''
    def ap_print_message(self, message, file=None):
        if message and message[-1] == '\n':
            message = message[:-1]
        raise SystemExit(message)
    # argparse_HelpFormatter = argparse.HelpFormatter
    # # Monkeypatch argparse and clg
    sys_argv = sys.argv
    sys.argv[0] = args[0]
    argparse_HelpFormatter = argparse.HelpFormatter
    argparse.HelpFormatter = argparse.RawTextHelpFormatter
    argparse_print_message = argparse.ArgumentParser._print_message
    argparse.ArgumentParser._print_message = ap_print_message
    TYPES = clg.TYPES
    # clg expects a dictionary with function names as keys
    types = {e.__name__: e for e in types}
    clg.TYPES.update(types)
    try:
        yield
    finally:
        # Un-monkeypatch argparse and clg
        clg.TYPES = TYPES
        argparse.HelpFormatter = argparse_HelpFormatter
        argparse.ArgumentParser._print_message = argparse_print_message
        sys.argv = sys_argv
