#!/usr/bin/env sh

set -e
cd $(dirname $0)/..

# Use tox if installed.
if [ $(which tox 2>/dev/null) ]; then
    tox
    exit $?; fi

# This section is provided for convenience of minimun requirements.
# tox is the recommended way to run tests.
py.test -sv --doctest-modules --ignore=setup.py
