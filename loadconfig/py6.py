'''Python six compatibility'''
__all__ = ['PY3', 'cStringIO', 'shlex_quote']

import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY3:  # pragma: no cover
    from io import StringIO as cStringIO
    from pipes import quote as shlex_quote
    text_type = str
else:  # pragma: no cover
    from cStringIO import StringIO as cStringIO
    from pipes import quote as shlex_quote
    text_type = unicode  # noqa
