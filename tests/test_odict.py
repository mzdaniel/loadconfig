#!/usr/bin/env python
'''Test Config class

pytest is recommented for running this test file.
For manual run:
    pip install pytest pytest-cov pyyaml clg
    pytest tests/test_odict.py
'''
from os import environ
from loadconfig import Config, Odict
from loadconfig.lib import tempfile
from yaml import safe_load


def test_list_substitution():
    d = Odict('''\
            name:  &dancer
              - Zeela
              - Kim
            team:
              *dancer
            ''')
    assert '{name: [Zeela, Kim], team: [Zeela, Kim]}' == repr(d)


def test_set():
    '''Verify Odict builds sets'''
    d = Odict("dancers: !!set {'Zeela', 'Kim'}")
    assert isinstance(d.dancers, set)
    assert ['Kim', 'Zeela'] == sorted(d.dancers)


def test_load_set():
    '''Verify Odict builds equivalent objects to YAML safe_load !!set'''
    yaml_string = '''
        app:
            option:
                default: !!set {}
        '''
    expected_object = {'app': {'option': {'default': set()}}}
    safe_loaded = safe_load(yaml_string)
    assert safe_loaded == expected_object, "ordinary safe_load loads !!set"
    assert Odict(yaml_string) == expected_object, "ODict loads !!set"


def test_include_odict_file_quoting():
    '''Test pre-processing !include '''
    with tempfile() as fh:
        fh.write('y: [3, 4]\n')
        fh.flush()
        d = Odict(f'''\
            !include '{fh.name}'

            x:
              a : 1
              b : 2
            ''')
    assert '{y: [3, 4], x: {a: 1, b: 2}}' == repr(d)


def test_unexistent_include_config():
    '''Test yaml !include tag ignore unxexistent file'''
    with tempfile() as fh:
        tmpfile = fh.name
    c = Config('''\
            _: !include {}
            test: hi
            '''.format(tmpfile))
    assert '{test: hi}' == repr(c)


def test_empty_include_config():
    '''Test yaml !include tag ignore empty file'''
    with tempfile() as fh:
        c = Config('_: !include {}'.format(fh.name))
    assert '{}' == repr(c)


def test_unexistent_include__config_wont_empty_subkey_lists():
    '''Ensure including a nonexistent file will parse lists properly'''
    with tempfile() as fh:  # Create a non-existent reference filename
        pass
    c = Config('''\
            _: !include {}
            test:
                list: [1, 2]
            '''.format(fh.name))
    assert '{test: {list: [1, 2]}}' == repr(c)


def test_include_config_wont_empty_subkey_lists():
    '''Ensure including a file, even an empty one, will parse lists properly'''
    with tempfile() as fh:  # Create an empty file
        c = Config('''\
                _: !include {}
                test:
                    list: [1, 2]
                '''.format(fh.name))
    assert '{test: {list: [1, 2]}}' == repr(c)


def test_env():
    '''Test yaml !env tag'''
    environ['CITY'] = 'San Francisco'
    c = Config('!env city')
    assert 'San Francisco' == c.city
    del environ['CITY']


def test_read():
    '''Test yaml !read tag'''
    with tempfile() as fh:
        fh.write('/usr/local/lib')
        fh.flush()
        assert {'libpath': '/usr/local/lib'} == Config('libpath: !read {}'.
            format(fh.name))


def test_env_unexistent():
    c = Config('!env city')
    assert '' == c.city
