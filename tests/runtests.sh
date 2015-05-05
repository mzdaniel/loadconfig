#!/usr/bin/env sh
set -e
cd $(dirname $0)/..

# Use tox if installed.
if [ $(which tox 2>/dev/null) ]; then
    tox
    exit $?; fi

# This section is provided for convenience of minimun requirements.
# tox is the recommended way to run tests.
for test in loadconfig/*py tests/*py docs/*rst ; do
    python -m doctest $test -v; done
python -m unittest discover -v
