#!/usr/bin/env sh

set -e
cd $(dirname $0)/..

# Use rust-just if installed.
if which just >/dev/null 2>&1 && which uv >/dev/null 2>&1; then
    just test
    exit $?; fi

# Ensure loadconfig dependencies are in place
if ! pip show -q clg || ! pip show -q pyyaml; then
    echo "Error: loadconfig clg and/or pyyaml dependencies are missing"; exit 1; fi

# Ensure pytest test dependency is in place
if ! pip show -q pytest || ! pip show -q pytest-cov; then
    echo "Error: pytest and/or pytest-cov are missing"; exit 1; fi

# This section is provided for convenience of minimun requirements.
# rust-just is the recommended way to run tests as it does linting,
# and test documentation is consistent with the code.
pytest
