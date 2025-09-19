# loadconfig

[![Docs](https://readthedocs.org/projects/loadconfig/badge)](https://loadconfig.readthedocs.org)
[![Tests](https://github.com/mzdaniel/loadconfig/actions/workflows/test.yml/badge.svg)](https://github.com/mzdaniel/loadconfig/actions/workflows/test.yml)

---


## A tool to simplify configuration management

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

    >>> from loadconfig import Config
    >>> c = Config('greeter: Hi there')
    >>> c
    {greeter: Hi there}

    >>> c.greeter
    'Hi there'

    $ loadconfig -E="greeter: Welcome to the loadconfig documentation"
    export GREETER="Welcome to the loadconfig documentation"


## Technical description

loadconfig dynamically creates a python configuration ordered dictionary from
sources like the command line, configuration files and yaml strings that can
be used in python code and shell scripts. Dependencies are pyyaml and clg.


## Installation

Installation is straightforward using a wheel from pypi:

    pip install loadconfig

Alternatively, install from github:

    pip install git+https://github.com/mzdaniel/loadconfig


## Local test and build

Assumptions for this section: A unix system, python >= 3.11, and pip >= 24.3

loadconfig is hosted on github:

    # Download the project using git
    git clone https://github.com/mzdaniel/loadconfig
    cd loadconfig

    # or from the source tarball from github, first finding the latest tag
    # released on https://github.com/mzdaniel/loadconfig/releases/latest
    wget -O- https://github.com/mzdaniel/loadconfig/archive/0.2.0.tar.gz | tar xz
    cd loadconfig

!!! note ""
	loadconfig tests are exhaustive and also tests described in the documentation
	are exercised to have confidence loadconfig code is as reliable as posible.

	python programs and libraries depend on the environment where it is run.
	At a minimun, it is adviced to run the tests and build process in a
	venv (python virtual environment)

<!-- -->

    # Create and activate venv (python virtual environment)
    python -m venv build/venv
    source build/venv/bin/activate

    # Install loadconfig dependencies and pytest with coverage and linting
    pip install 'clg>=3.3' 'PyYAML>=6.0.2' 'pytest-cov>=6.2.1' 'pytest-ruff>=0.5'

    # Run the tests
    pytest


Building loadconfig pip installable wheel (on build/wheel) is as easy as:

    pip wheel -w build/wheel .


To test and build (on build/site) loadconfig documentation:

    pip install 'mkdocs>=1.6.1' 'mkdocs-codeinclude-plugin>=0.2.1'
    mkdocs build

If you are curious, since loadconfig 0.1.2, [github actions CI][] continuos integration
server shows the test runs for each commit and pull requests done in the loadconfig repo.

[github actions CI]: https://github.com/mzdaniel/loadconfig/actions/workflows/test.yml


## Security

Disclosure: loadconfig is meant for both flexibility and productivity.
It does not attempt to be safe with untrusted input. There are ways (linux
containers, PyPy’s sandboxing) that can be implemented for such environments
and left for the user to consider.


## Thanks!

* [Guido van Rossum][] and [Linus Torvalds][]
* [Raymond Hettinger][] and Armin Ronacher for [OrderedDict][]
* Clark Evans and Kirill Simonov for [YAML][] and [PyYAML][] implementation
* Steven Bethard and François Ménabé for [argparse][] and [CLG][] implementations
* Holger Krekel for [pytest][]
* David Goodger and Georg Brandl for [reStructuredText][] and [Sphinx][]
* John Gruber and Tom Christie for [markdown][] and [Mkdocs][]
* Solomon Hykes, Jerome Petazzoni and Sam Alba for [Docker][]
* The awesome Python, Linux and Git communities


[Guido van Rossum]: http://en.wikipedia.org/wiki/Guido_van_Rossum
[Linus Torvalds]: http://en.wikipedia.org/wiki/Linus_Torvalds
[Raymond Hettinger]: https://www.youtube.com/watch?v=p33CVV29OG8
[yaml]: https://yaml.org/spec/1.1
[pyyaml]: http://pyyaml.org/wiki/PyYAMLDocumentation
[OrderedDict]: https://www.python.org/dev/peps/pep-0372
[argparse]: https://docs.python.org/3/library/argparse.html
[CLG]: https://clg.readthedocs.org
[docker]: https://www.docker.com
[pytest]: https://docs.pytest.org
[reStructuredText]: http://sphinx-doc.org/rest.html
[Sphinx]: http://sphinx-doc.org/tutorial.html
[markdown]: https://daringfireball.net/projects/markdown
[Mkdocs]: https://www.mkdocs.org
