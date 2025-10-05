'''loadconfig python library'''
from __future__ import print_function
__all__ = ['Config', 'Odict', '__version__']

__author__ = 'Daniel Mizyrycki'
__version__ = '0.2.1rc1'

from itertools import count
from .lib import (Odict, delregex, dfl, findregex, flatten,
    read_config_file, _clg_parse, _get_option)
from shlex import quote as shlex_quote
from string import Template


class Config(Odict):
    '''Config class for programs.

    The Config class is designed to be a versatile interface to load a config
    object for use in python and shell programs.
    Source data comes from config_data object and from interpreting the args
    parameter (usually sys.args) from command line.
    config_data object can be a yaml string or a dictionary (eg: 1 doctest).
    args list take any number of arguments. Optionally some arguments can be
    in the form of -C (for config file) and -E (for extra) options (2).
    The python clg package is used to parse normal cli arguments using the
    special clg key (3).

    >>> c = Config('hi: there')
    >>> c.hi
    'there'

    >>> import os
    >>> tmpfile = '/tmp/test_tempfile.conf'
    >>> with open(tmpfile, 'w') as fh:
    ...     ret = fh.write('a: 1, b: 2')
    >>> c = Config(args=['', '-C={}'.format(tmpfile)])
    >>> c.b
    2
    >>> os.remove(tmpfile)

    >>> conf = """
    ...    clg:
    ...        description: Build a full system
    ...        args:
    ...            host:
    ...                help: Host to build"""
    >>> c = Config(args=['', '-E={}'.format(conf), 'leon'])
    >>> c.host
    'leon'
    '''
    # Try up to max times to expand $ keys
    expand_max = 5

    def __init__(self, config_data='', args=None, version=None, types=set()):
        '''Initialize config object. Keep its __dict__ clean for easy access'''
        super().__init__()
        if config_data == '' and args is None:
            return
        if version:
            self.version = version
        if args and 'clg' in config_data:
            self.prog = args[0]
        self._expand_keys(config_data)
        args = self._load_options(args)
        self._load_config_cli(args, types)
        self._checkconfig()

    def _expand_keys(self, config_data=''):
        '''Add config_data into config and interpolate $keys.

        >>> config_data = 'data_path: /data, data_file: $data_path/data.txt'
        >>> c = Config()
        >>> c._expand_keys(config_data)
        >>> c.data_file
        '/data/data.txt'
        '''
        self.update(config_data)
        # Convert self to text for full key interpolation
        config_string = str(self)
        n = count()
        while '$' in config_string and next(n) < self.expand_max:
            config_string = self.render(config_string)
            self.update(config_string)

    def _load_config_file(self, filepath):
        '''Return config file adding data from loadconfig.template keyword'''
        datafile = read_config_file(filepath)
        self._expand_keys(datafile)
        return datafile

    def _load_options(self, args):
        '''Load config from options -E and -C from cli arguments.

        >>> c = Config()
        >>> c._load_options(['-E="data_file: data.txt"'])
        []
        >>> c.data_file
        'data.txt'
        '''
        if args is None:
            return
        for arg in findregex('^(-E|-C)=', args):
            config_string, option = _get_option(arg)
            if option == 'C':
                # Expand $ keys in file name
                config_string = self.render(config_string)
                config_string = self._load_config_file(config_string)
            if 'prog' not in self and 'clg' in config_string:
                self.prog = args[0]
            self._expand_keys(config_string)
        # Prevent clg seeing -E or -C options
        return delregex('^(-E|-C)=', args)

    def _load_config_cli(self, args, types=set()):
        '''Load config parsing cli arguments with clg.
        clg key config may come from config file, cli arg, or python config.

        >>> from os.path import basename
        >>> c = Config()
        >>> c.update("""
        ...     clg:
        ...         args:
        ...             filename:
        ...                 type: basename
        ...     """)
        >>> c._load_config_cli(args=['', '/data/data.txt'], types={basename})
        >>> c.filename
        'data.txt'
        '''
        if not args or 'clg' not in self:
            return
        clg_args = _clg_parse(self.clg, args, types)
        self._expand_keys(clg_args)  # Add config from cli args
        del self['clg']  # Remove clg key from Config

    def _checkconfig(self):
        '''Check configuration using keyword checkconfig

        >>> c = Config("""
        ...         action: stop
        ...         checkconfig: |
        ...             if  '$action' == 'stop':
        ...                 raise Exception('Stopping now.')
        ...         """)
        Traceback (most recent call last):
            ...
        Exception: Stopping now.
        '''
        if 'checkconfig' in self:
            exec(self.checkconfig)
            self._expand_keys('')
            del self['checkconfig']

    def export(self):
        '''Export the config for shell usage.
        Keys are uppercased. List-like keys are flattened.

        >>> c = Config('activity: hanggliding')
        >>> c.export()
        'export ACTIVITY="hanggliding"'
        '''
        retval = ''
        for key in self:
            val = dfl(self[key])
            # Make list-like keys shell friendly
            if isinstance(val, (list, tuple)):
                val = flatten(val)
                val = ' '.join([shlex_quote(e) for e in val])
            elif isinstance(val, dict):
                val = repr(val)
            retval += 'export {}="{}"\n'.format(
                key.upper().replace(' ', '_'), val)
        return retval[:-1]

    def render(self, template):
        '''Render a string template

        >>> c = Config('name: Jay')
        >>> c.render('Good morning $name.')
        'Good morning Jay.'
        '''
        return Template(template).safe_substitute(self)

    def run(self, namespace='__main__'):
        r'''Run selected subparser command from namespace.
        Namespace can be full qualified string (eg: package.module.class), a
        module or a class. Subparser command correspond with either a function
        or a method from the namespace.

        >>> conf = Config("""
        ...            prog: netapplet
        ...            clg:
        ...                subparsers:
        ...                    install:
        ...                        help: 'run as $prog install | bash'""")
        >>> def install(c):
        ...     print(f'echo "Commands for {c.prog} installation"')
        >>> # Ensure install function is reachable
        >>> __import__(__name__).install = install
        >>> c = Config(conf, args=['', 'install'])
        >>> c.run(__name__)
        echo "Commands for netapplet installation"
        '''
        if isinstance(namespace, str):  # rename namespace with its last name
            lname = __import__(namespace.partition('.')[0])
            for name in namespace.split('.')[1:]:
                lname = getattr(lname, name)
            namespace = lname
        if isinstance(namespace, type):  # namespace is a class
            return getattr(namespace(self), str(self.command0))()
        return getattr(namespace, str(self.command0))(self)

    def __repr__(self):
        return repr(Odict(self))

    def __str__(self):
        return str(Odict(self))
