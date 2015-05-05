.. include:: /defs.irst

==========
loadconfig
==========

loadconfig is a tool to simplify configuration management.

We live in an incredible moment in software history. As never before, the
quality and quantity of excellent open source software have unleashed massive
advances in pretty much all fields of human knowledge. It is overwhelming to
have such vast posibilities, and often having a hard time trying to understand
how the pieces fit together. More importantly, we are concern on how can we use
the software for things that matter to us.

Plenty of times we find what is really needed is a small custom configuration
we can easily understand and a handful ways to call the software. And although
we barely think about it as we are too busy trying to understand all the bells
and whistles, the interface and documentation is in the center of any software.

loadconfig syntax is designed to be clean and DRY, to foster descriptive
programming, and to leverage version control systems. loadconfig can be used
as a light wrapper around programs to make them behave and to document them
the way we design.

    >>> from loadconfig import Config
    >>> c = Config('greeter: Hi there')
    >>> c
    {greeter: Hi there}

    >>> c.greeter
    'Hi there'

.. highlight:: bash

::

    $ loadconfig -E="greeter: Welcome to the loadconfig documentation"
    export GREETER="Welcome to the loadconfig documentation"


Contents
========

.. toctree::
    :maxdepth: 2

    basic
    intermediate
    examples


Technical description
=====================

loadconfig dynamically creates a python configuration order dictionary from
sources like the command line, configuration files and yaml strings that can
be used in python code and shell scripts. Dependencies are pyyaml, clg and six.


Installation
============

Installation is straightforward using a wheel from pypi::

    pip install loadconfig

Alternatively, install from github::

    pip install git+https://github.com/mzdaniel/loadconfig


Local test/build
================

Assumptions for this section: A unix system, python2.7 or 3.4, and pip >= 6.1.
Although git is recommended, it is not required.

loadconfig is hosted on github::

    # Download the project using git
    git clone https://github.com/mzdaniel/loadconfig
    cd loadconfig

    # or from a tarball
    wget -O- https://github.com/mzdaniel/loadconfig/archive/0.1.tar.gz | tar xz
    cd loadconfig

For a simple way to run the tests with minimum dependencies, tests/runtests.sh
is provided.
Note: python programs and libraries depend on the environment where it is run.
At a minimun, it is adviced to run the tests and build process in a virtualenv.
tox is the recommended way to run loadconfig tests and build its package::

    # Install loadconfig dependencies.
    pip install -r requirements.txt

    # Run the tests
    ./tests/runtests.sh

For building a pip installable wheel, pbr is used::

    # Install setup.py dependencies if needed.
    pip install pbr wheel six

    # Build loadconfig package
    python setup.py bdist_wheel

We use tox to test loadconfig in virtualenvs for both python2.7 and python3.4.
`Tox`_ is a generic virtualenv management and test command line tool. It
handles the creation of virtualenvs with proper python dependencies for
testing, pep8 checking, coverage and building::

    # Install the only tox dependency if needed (tox takes care of any other
    # needed dependency using pip)
    pip install tox

    # Run tests, create coverage report and build universal loadconfig package
    # loadconfig package is left in dist/
    tox

If you are curious, `loadconfig buildbot`_ continuos integration server shows
the tox test and build run for each commit done in the loadconfig repo.

.. _tox: http://tox.readthedocs.org
.. _loadconfig buildbot: http://buildbot.gdl/waterfall


Security
========

Disclosure: loadconfig is meant for both flexibility and productivity.
It does not attempt to be safe with untrusted input. There are ways (linux
containers, PyPy’s sandboxing) that can be implemented for such environments
and left for the user to consider.


Thanks!
=======

* `Guido van Rossum`_ and `Linus Torvalds`_
* Clark Evans and Kirill Simonov for `YAML`_ and `PyYAML`_ implementation
* Steven Bethard and François Ménabé for `argparse`_ and `CLG`_ implementations
* David Goodger & Georg Brandl for `reStructuredText`_ and `Sphinx`_
* Solomon Hykes, Jerome Petazzoni and Sam Alba for `Docker`_
* The awesome Python, Linux and Git communities


.. _Guido van Rossum: http://en.wikipedia.org/wiki/Guido_van_Rossum
.. _Linus Torvalds: http://en.wikipedia.org/wiki/Linus_Torvalds
.. _yaml: http://yaml.org/spec/1.2/spec.html
.. _pyyaml: http://pyyaml.org/wiki/PyYAMLDocumentation
.. _argparse: https://docs.python.org/3/library/argparse.html
.. _CLG: https://clg.readthedocs.org
.. _docker: https://www.docker.com/
.. _reStructuredText: http://sphinx-doc.org/rest.html
.. _Sphinx: http://sphinx-doc.org/tutorial.html
