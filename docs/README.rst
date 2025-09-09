==========
loadconfig
==========

.. image:: https://readthedocs.org/projects/loadconfig/badge/?version=master
    :target: http://loadconfig.readthedocs.org/en/master
    :alt: [Docs]
.. image:: https://github.com/mzdaniel/loadconfig/actions/workflows/runtests.yml/badge.svg
    :target: https://github.com/mzdaniel/loadconfig/actions/workflows/runtests.yml
    :alt: [Tests]


loadconfig is a tool to simplify configuration management
=========================================================

We live in an incredible moment in software history. As never before, the
quality and quantity of excellent open source software have unleashed massive
advances in pretty much all fields of human knowledge. It is overwhelming to
have such vast posibilities, and often having a hard time trying to understand
how the pieces fit together. More importantly, we are concern on how can we use
the software for things that matter to us.

Plenty of times we find what is really needed is a small custom configuration
we can easily understand and a handful ways to run the software. And although
we barely think about it as we are too busy trying to understand all the bells
and whistles, the interface and documentation is at the center of any software.

loadconfig syntax is designed to be clean and DRY, to foster descriptive
programming, and to leverage version control systems. loadconfig can be used
as a light wrapper around programs to make them behave and to document them
the way we designed.

.. code-block:: python

    >>> from loadconfig import Config
    >>> c = Config('greeter: Hi there')
    >>> c
    {greeter: Hi there}

    >>> c.greeter
    'Hi there'

.. code-block:: bash

    $ loadconfig -E="greeter: Welcome to the loadconfig documentation"
    export GREETER="Welcome to the loadconfig documentation"


Technical description
=====================

loadconfig dynamically creates a python configuration ordered dictionary from
sources like the command line, configuration files and yaml strings that can
be used in python code and shell scripts. Dependencies are pyyaml and clg.


Installation
============

Installation is straightforward using a wheel from pypi::

    pip install loadconfig

Alternatively, install from github::

    pip install git+https://github.com/mzdaniel/loadconfig


Local test/build
================

Assumptions for this section: A unix system, python >= 3.11, and pip >= 24.3

loadconfig is hosted on github:

.. code-block:: bash

    # Download the project using git
    git clone https://github.com/mzdaniel/loadconfig
    cd loadconfig

    # or from a tarball
    wget -O- https://github.com/mzdaniel/loadconfig/archive/0.1.tar.gz | tar xz
    cd loadconfig

For a simple way to run the tests with minimum dependencies, tests/runtests.sh
is provided.
Note: python programs and libraries depend on the environment where it is run.
At a minimun, it is adviced to run the tests and build process in a venv.
loadconfig tests are exhaustive and also tests described in the documentation
are exercised to have confidence loadconfig code is as reliable as posible.

.. code-block:: bash

    # Install loadconfig dependencies plus ruff and pytest with coverage
    python -m venv build/venv
    source build/venv/bin/activate
    pip install clg pyyaml ruff pytest-cov

    # Run the tests
    ruff check
    pytest

Building loadconfig pip installable wheel is as easy as:

.. code-block:: bash

    pip wheel -w build/wheel .

Although rust-just, uv and git are used in this project for performance
and organizational tasks, at this point it's most effective to stick
with our familiar pip and venv.

To test and build loadconfig documentation, the following can be added
to the venv:

.. code-block:: bash

    pip install sphinx sphinx_bootstrap_theme
    sphinx-build -E -d build/.doctrees -b doctest docs build/html
    sphinx-build -E -d build/.doctrees docs build/html


If you are curious, since loadconfig 0.1.2, `github actions CI`_ continuos integration
server shows the test runs for each commit and pull requests done in the loadconfig repo.

.. _github actions CI: https://github.com/mzdaniel/loadconfig/actions/workflows/runtests.yml


Security
========

Disclosure: loadconfig is meant for both flexibility and productivity.
It does not attempt to be safe with untrusted input. There are ways (linux
containers, PyPy’s sandboxing) that can be implemented for such environments
and left for the user to consider.


Thanks!
=======

* `Guido van Rossum`_ and `Linus Torvalds`_
* Raymond Hettinger and Armin Ronacher for `OrderedDict`_
* Clark Evans and Kirill Simonov for `YAML`_ and `PyYAML`_ implementation
* Steven Bethard and François Ménabé for `argparse`_ and `CLG`_ implementations
* David Goodger & Georg Brandl for `reStructuredText`_ and `Sphinx`_
* Solomon Hykes, Jerome Petazzoni and Sam Alba for `Docker`_
* The awesome Python, Linux and Git communities


.. _Guido van Rossum: http://en.wikipedia.org/wiki/Guido_van_Rossum
.. _Linus Torvalds: http://en.wikipedia.org/wiki/Linus_Torvalds
.. _yaml: http://yaml.org/spec/1.2/spec.html
.. _pyyaml: http://pyyaml.org/wiki/PyYAMLDocumentation
.. _OrderedDict: https://www.python.org/dev/peps/pep-0372
.. _argparse: https://docs.python.org/3/library/argparse.html
.. _CLG: https://clg.readthedocs.org
.. _docker: https://www.docker.com/
.. _reStructuredText: http://sphinx-doc.org/rest.html
.. _Sphinx: http://sphinx-doc.org/tutorial.html
