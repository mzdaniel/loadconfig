'''loadconfig library helpers

tox is recommented for testing this file.
For partial manual run:
    python -m doctest lib.py -v
'''
__all__ = ['addpath', 'capture_stream', 'delregex', 'dfl', 'exc', 'findregex',
    'import_file', 'read_config_file', 'ppath', 'Run', 'run', 'tempdir',
    'tempfile']
__author__ = 'Daniel Mizyrycki'

import argparse
import clg
from collections import deque
from contextlib import contextmanager
from copy import deepcopy
import os
from os import remove
from os.path import basename, dirname, abspath, exists, isdir, isfile
from py6 import cStringIO, text_type
import re
import shlex
from shutil import rmtree
from signal import SIGTERM
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


def first(it):
    '''Get first element of an iterator. Return None if empty.

    >>> first([1,2,3])
    1
    '''
    return next(iter(it), None)


@contextmanager
def exc(*exceptions):
    '''Swallow exceptions

    >>> with exc(ZeroDivisionError) as e:
    ...     0 / 0
    >>> isinstance(e(), ZeroDivisionError)
    True
    '''
    if not exceptions:
        exceptions = BaseException
    try:
        e = None
        yield lambda: e
    except exceptions as ex:
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


def last(it):
    '''Get last element of an iterator. Return None if empty.

    >>> last([1,3,7])
    7
    '''
    try:
        return deque(it, maxlen=1).pop()
    except IndexError:
        return None


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


class Ret(text_type):
    r'''Return class.
    arg[0] is the string value for the Ret object.
    kwargs are feed as attributes.

    >>> ret = Ret('OK', code=0)
    >>> ret == 'OK'
    True
    >>> ret.code
    0
    '''
    def __new__(cls, string, **kwargs):
        ret = super(Ret, cls).__new__(cls, text_type(string))
        for k in kwargs:
            setattr(ret, k, kwargs[k])
        return ret

    _r = property(lambda self: self.__dict__)


class Run(Popen):
    r'''Simplify Popen API. Add stop method, async parameter and code attrib.
    stop method and blocking mode (async=False) call communicate.
    After communicate, stdout and stderr are mutated to strings

    >>> from time import sleep
    >>> with Run('echo hi; sleep 1000000', async=True) as proc:
    ...     sleep(0.2)
    >>> 'hi\n' == proc.stdout
    True
    '''
    def __init__(self, cmd, async=False, **kwargs):
        kw = dict(kwargs)
        kw.setdefault('universal_newlines', True)
        kw.setdefault('stdout', PIPE)
        kw.setdefault('stderr', PIPE)
        kw.setdefault('shell', True)
        kw['preexec_fn'] = os.setsid
        if not kw['shell'] and isinstance(cmd, (text_type, str)):
            cmd = shlex.split(cmd)
        super(Run, self).__init__(cmd, **kw)
        if async is False:
            self.get_output()

    def get_output(self):
        if not isinstance(self.stdout, (text_type, str)):
            self.stdout, self.stderr = self.communicate()
            self.code = self.wait()
        return self.stdout

    def stop(self):
        if not self.poll():
            with exc(OSError):
                self.send_signal(SIGTERM)
        self.get_output()

    def send_signal(self, sig):
        os.killpg(self.pid, sig)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.stop()


class run(text_type):
    r'''Execute command cmd. kwargs are the same as Popen.
    Return object is a string object with extra attributes: stdout, stderr and
    code (Popen.returncode). Note: run subclasses str for convenience and works
    well in most cases. In a few corner cases, wrapping run with str, like
    str(run()), might be needed.

    >>> ret = run('echo $((1+1))')
    >>> '2\n' == ret
    True
    >>> ret.code
    0
    '''
    def __new__(cls, cmd, **kwargs):
        proc = Run(cmd, async=False, **kwargs)
        ret = super(run, cls).__new__(cls, proc.stdout)
        ret.stdout = proc.stdout
        ret.stderr = proc.stderr
        ret.code = proc.returncode
        return ret

    _r = property(lambda self: self.__dict__)


class tempdir(str):
    '''Create temporary directory. Autoremove it if used as context manager.
    Tempdir uses same keyword arguments as tempfile.mkdtemp.

    >>> with tempdir() as tmpdir:
    ...     isdir(tmpdir)
    True
    >>> with tempdir() as tmpdir:
    ...     pass
    >>> isdir(tmpdir)
    False
    >>> isinstance(tempdir(), str)
    True
    '''
    def __new__(cls, *args, **kwargs):
        tmpdir = mkdtemp(**kwargs)
        return super(tempdir, cls).__new__(cls, tmpdir)

    def remove(self):
        rmtree(self)

    def __enter__(self):
        return str(self)

    def __exit__(self, type, value, traceback):
        self.remove()


@contextmanager
def tempfile(*args, **kwargs):
    '''Create a temporary file, returning its file handle. Remove it on exit.
    Tempdir uses same keyword arguments as tempfile.mkstemp using text mode by
    default.

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
    tmpfile_fd, tmpfile = mkstemp(**kwargs)
    os.close(tmpfile_fd)
    mode = 'wt+' if kwargs.get('text', True) else 'w+'
    filehandle = open(tmpfile, mode)
    yield filehandle
    filehandle.close()
    remove(tmpfile)


def write_file(file_path, data):
    '''Write data to file. Return True on success

    >>> with tempfile() as fh:
    ...     fh.close()
    ...     assert write_file(fh.name, 'Hi there')
    ...     assert 'Hi there' == read_file(fh.name)
    '''
    with exc(IOError) as e, open(file_path, 'w') as fh:
        fh.write(data)
    return not bool(e())


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


def _clg_parse(clg_key, args, types):
    '''Parse cli arguments using clg key.
    types: optional list of custom functions for argument checking.
    clg_key.default_cmd: optional command if none is passed on the cli args.
    '''
    if 'default_cmd' in clg_key:
        default_cmd = clg_key['default_cmd']
        del clg_key['default_cmd']
    with _patch_argparse_clg(args, types), exc(SystemExit) as e:
        clg_args = clg.CommandLine(deepcopy(clg_key)).parse(args[1:])
    if e() and hasattr(e(), 'code') and e().code.startswith('usage:') and \
     'default_cmd' in locals() and '-h' not in args and '--help' not in args:
        # Try clg parsing once more with default_cmd
        new_args = [default_cmd] + args[1:]
        with _patch_argparse_clg(args, types), exc(SystemExit) as e:
            clg_args = clg.CommandLine(deepcopy(clg_key)).parse(new_args)
        if e():
            raise e()
    elif e():
        raise e()
    return clg_args
