#!/usr/bin/env python
'''usage: demoscript.py [-h] [-v]

demoscript.py 0.1.5 shows usage of loadconfig package

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit

Extra demoscript.py documentation.
'''

version = '0.1.5'

from loadconfig import Config, set_verprog
import sys

conf = """\
    clg:
        description: $prog $version shows usage of loadconfig package
        epilog: |
            Extra ${prog} documentation.
        options:
            version:
                short: v
                action: version
                version: $prog $version"""


def main(args):
    config = set_verprog(conf, version)
    c = Config(config, args)
    assert c.version == '0.1.5'

if __name__ == '__main__':
    main(sys.argv)
