'''loadconfig python library'''
from __future__ import print_function
__all__ = ['Config', 'Odict', '__version__']

__author__ = 'Daniel Mizyrycki'
__version__ = '0.1.1'

from os.path import dirname, abspath
import sys
sys.path.insert(0, dirname(abspath(__file__)))

from collections import OrderedDict
from copy import deepcopy
from itertools import count
from lib import (delregex, dfl, findregex, flatten, read_config_file,
    read_file, _clg_parse, _get_option)
from os import environ
from py6 import cStringIO, shlex_quote
from string import Template
import yaml
from yaml.scanner import ScannerError


class Odict(OrderedDict):
    r'''Add more readable representation to OrderedDict using yaml.

    >>> d = Odict('{a: 1, b: {c: 3}}')
    >>> repr(d)
    '{a: 1, b: {c: 3}}'
    >>> str(d)
    'a: 1\nb:\n  c: 3'
    >>> d == Odict(d)
    True
    >>> d.b.c
    3
    >>> d._p
    a: 1
    b:
      c: 3
    '''
    def __init__(self, *args, **kwargs):
        '''Process first argument as yaml if it is a string'''
        args = self._process_args(*args, **kwargs)
        super(Odict, self).__init__(*args, **kwargs)

    def _process_args(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], str):
            try:
                pair_list = self.load(args[0])
            except ScannerError:
                # Yaml needs {} on multi-key single-line strings
                pair_list = self.load('{{{}}}'.format(args[0]))
            args = [pair_list] if pair_list else []
        return args

    def update(self, *args, **kwargs):
        '''Add yaml string as posible argument

        >>> d = Odict('hi: there')
        >>> d.hi
        'there'
        >>> d.update({'hi': 'Liss'})
        >>> d.hi
        'Liss'
        '''
        args = self._process_args(*args, **kwargs)
        super(Odict, self).update(*args, **kwargs)
        # Remove '_' key possible used by include
        if '_' in self:
            del self['_']

    def __getattr__(self, name):
        '''Access Odict key as attribute

        >>> c = Config('activity: [hike, bike, scuba dive, run]')
        >>> c.activity
        ['hike', 'bike', 'scuba dive', 'run']
        '''
        if name in self:
            return self[name]
        if name in ['_OrderedDict__root', '__deepcopy__']:
            return super(Odict, self).__getattr__(name)

    def __delattr__(self, name):
        '''Delete Odict key from attribute
        >>> c = Config('activity: [hike, bike, scuba dive, run]')
        >>> del c.activity
        >>> c
        {}
        '''
        del self[name]

    def __setattr__(self, name, value):
        '''Set Odict key from attribute

        >>> c = Config('activity: [hike, scuba dive]')
        >>> c.place = 'Hawaii'
        >>> c
        {activity: [hike, scuba dive], place: Hawaii}
        '''
        if name in ['_OrderedDict__root', '_OrderedDict__hardroot',
         '_OrderedDict__map']:
            return super(Odict, self).__setattr__(name, value)
        self[name] = value

    def __str__(self):
        return Odict.dump(self, False)

    def __repr__(self):
        return Odict.dump(self)

    # Convenient shortcuts
    _r = property(__repr__)
    _s = property(__str__)
    _p = property(lambda x: print(str(x)))

    @staticmethod
    def load(yaml_string):
        '''Return pair list from a yaml string'''
        class Loader(yaml.SafeLoader):
            yaml_mapping = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
            _data = ''

            def __init__(self, *args, **kwargs):
                super(Loader, self).__init__(*args, **kwargs)
                self.add_constructor(self.yaml_mapping, self.construct_mapping)
                self.add_constructor('!env', self.env)
                self.add_constructor('!read', self.read)
                self.add_constructor('!include', self.include)
                self.add_constructor('!expand', self.expand)

            def env(self, safeloader, node):
                node = self.construct_scalar(node)
                if node.upper() in environ:
                    return {node: environ[node.upper()]}
                return {node: ''}

            def read(self, safeloader, node):
                node = self.construct_scalar(node)
                return read_file(node)

            def include(self, safeloader, node):
                node = self.construct_scalar(node)
                filepath, sep, key = node.partition(':')
                self._data = yaml.load(read_file(filepath), Loader)
                return self.subkey(key)

            def expand(self, safeloader, node):
                key = self.construct_scalar(node)
                self._data = safeloader._data
                return self.subkey(key)

            def subkey(self, key):
                if not self._data:
                    return ''
                data = deepcopy(self._data)
                if key == '&':
                    return ''
                for k in key.split(':'):
                    if not k:
                        return data
                    data = data.get(k)
                    if data is None:
                        return ''
                return data

            def construct_mapping(self, safeloader, node):
                safeloader.flatten_mapping(node)
                return Odict(safeloader.construct_pairs(node))

        return yaml.load(yaml_string, Loader)

    @staticmethod
    def dump(self, default_flow_style=True):
        '''Serialize odict into yaml string'''
        class Dumper(yaml.SafeDumper):
            def __init__(self, *args, **kwargs):
                super(Dumper, self).__init__(*args, **kwargs)
                self.ignore_aliases = lambda self: True
                self.add_representer(Odict, lambda self, data:
                    self.represent_dict(data.items()))

            def increase_indent(self, flow=False, indentless=False):
                return super(Dumper, self).increase_indent(flow, False)

        stream = cStringIO()
        yaml.dump(self, stream, Dumper, default_flow_style=default_flow_style)
        return stream.getvalue()[:-1]


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
        super(Config, self).__init__()
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
        ...            prog: netapplet.py
        ...            clg:
        ...                subparsers:
        ...                    install:
        ...                        help: 'run as $prog install | bash'""")
        >>> def install(c):
        ...     print('echo "Installation shell script lines for {}."'.format(
        ...         c.prog))
        >>> # Ensure install function is reachable
        >>> __import__(__name__).install = install
        >>> c = Config(conf, args=['', 'install'])
        >>> c.run(__name__)
        echo "Installation shell script lines for netapplet.py."
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
