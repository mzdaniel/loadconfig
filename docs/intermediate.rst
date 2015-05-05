.. include:: /defs.irst

.. _intermediate tutorial:

=====================
Intermediate tutorial
=====================

.. _expansion:

Expansion
=========

Yaml config sources are meant to reduce redundancy whenever possible:

    >>> from loadconfig import Config
    >>> conf = '''\
    ...     name: &dancer
    ...       - Zeela
    ...       - Kim
    ...     team:
    ...       *dancer
    ...     '''
    >>> Config(conf)
    {name: [Zeela, Kim], team: [Zeela, Kim]}


To make the syntax more DRY and intuitive, loadconfig introduces an alternative
form of expansion:

    >>> conf = '''\
    ...     name: [Zeela, Kim]
    ...     team: $name
    ...     choreography: $team
    ...     '''
    >>> Config(conf)
    {name: [Zeela, Kim], team: [Zeela, Kim], choreography: [Zeela, Kim]}


Include
=======

Another feature is the ability to include config files from a yaml config
source:

    >>> birds = '''\
    ...     hummingbird:
    ...       colors:
    ...         - iris
    ...         - teal
    ...         - coral
    ...     '''
    >>> with open('birds.yml', 'w') as fh:
    ...     _ = fh.write(birds)
    >>> conf = '!include birds.yml'
    >>> Config(conf)
    {hummingbird: {colors: [iris, teal, coral]}}


!include can also take a key (or multiple colon separated keys) to get more
specific config data:

    >>> conf = 'colors: !include birds.yml:hummingbird:colors'
    >>> Config(conf)
    {colors: [iris, teal, coral]}


Substitution
============

This feature allows to expand just a key from a previously included yaml file

    >>> conf = '''\
    ...     _: !include birds.yml:&
    ...     colors: !expand hummingbird:colors
    ...     '''
    >>> Config(conf)
    {colors: [iris, teal, coral]}


Introducing -E and -C cli switches
==================================

As with the inline config and include, we have the -E switch for extra yaml
config and -C for yam config files. Let's looks again at our beautiful
hummingbird:

    >>> birds = '''\
    ...     hummingbird:
    ...       colors:
    ...         - iris
    ...         - teal
    ...         - coral
    ...     '''
    >>> extra_arg = '-E="{}"'.format(birds)
    >>> Config(args=[extra_arg])
    {hummingbird: {colors: [iris, teal, coral]}}


Similarly we can introduce the same data through a configuration file. In this
case, we will reuse our birds.yml file with simply:

    >>> Config(args=['-C="{}"'.format('birds.yml')])
    {hummingbird: {colors: [iris, teal, coral]}}

.. highlight:: bash

These operations are in themselves pretty useful. They are even more revealing
when considering them in the shell context. loadconfig is at its core a python
library, so the issue is how do we bridge these two worlds. Shell environment
variables, and some little magic from our loadconfig script would help. Let's
reintroduce loadconfig script call here::

    $ BIRDS=$(cat << 'EOF'
    >   hummingbird:
    >     - iris
    >     - teal
    >     - coral
    > EOF
    > )
    $ loadconfig -E="$BIRDS"
    export HUMMINGBIRD="iris teal coral"


If our bird decided to take a nap in a file, it would be::

    $ echo "$BIRDS" > birds.yml
    $ loadconfig -C="birds.yml"
    export HUMMINGBIRD="iris teal coral"


At this point, we can use both switches. loadconfig accepts them in sequence,
updating and overriding older data with new values from the sequence::

    $ BIRDS2="hummingbird: [ruby, myrtle]"
    $ BIRDS3="swallow: [cyan, yellow]"
    $ loadconfig -E="$BIRDS2" -C="birds.yml" -E="$BIRDS3"
    export HUMMINGBIRD="iris teal coral"
    export SWALLOW="cyan yellow"

    $ loadconfig -E="$BIRDS3" -C="birds.yml" -E="$BIRDS2"
    export SWALLOW="cyan yellow"
    export HUMMINGBIRD="ruby myrtle"


.. testcleanup::

    import os
    os.remove('birds.yml')

.. _cli interface:

CLI interface
=============

One key feature of loadconfig is its CLG integration. `CLG`_ is a wonderful
yaml based command line generator that wraps the standard argparse module.
Loadconfig uses a special clg keyword to unleash its power.

.. _CLG: https://clg.readthedocs.org/en/latest/

First steps
~~~~~~~~~~~

Lets start with a more concise shell example to get the concepts first::

    $ CONF=$(cat << 'EOF'
    >   clg:
    >     description: Build a full system
    >     args:
    >       host:
    >         help: Host to build
    > EOF
    > )
    $ loadconfig -E="$CONF" --help
    usage: loadconfig [-h] host

    Build a full system

    positional arguments:
      host        Host to build

    optional arguments:
      -h, --help  show this help message and exit

Neat! A handful lines got us a wonderful command line interface with full
usage documentation!

* clg is a special loadconfig keyword declaring what is going to be interpreted
  by CLG.
* description declares the description content we see at the top of the output.
* args declares positional arguments for our command line. In this case we are
  saying there is one positional argument we call host.
* help declares a succinct description of the argument host in this case.

Our little program does something more than just throwing back a few text
lines::

    $ loadconfig -E="$CONF" antares
    export HOST="antares"

.. highlight:: python

Think about it for a second. We fed yaml 'data' lines that actually
controlled the 'behavior' of our program. It created a meaningful  interface,
processed the arguments and output a shell environment variable for further
processing. The core of the whole activity was the data and its organization
that matters for the programmer instead of the individual lines of code
normally required by programming languages. This is what this author calls
descriptive programming.

The following lines shows the same snippet for python. As usually all the setup
involved to validate the doctest is just too distracting, we will use a handy
advanced technique here. From all these lines, the only two that matters are
the definition of conf, and the Config assignment. Lets play with clg:

    >>> from loadconfig import Config
    >>> from mock import patch
    >>> from six.moves import cStringIO
    >>> conf = '''
    ...     clg:
    ...         description: Build a full system
    ...         args:
    ...             host:
    ...                 help: Host to build
    ...     '''
    >>> with patch('sys.stderr', new_callable=cStringIO) as stderr:
    ...     try:
    ...         c = Config(conf, args=['', '--help'])
    ...     except SystemExit:
    ...         pass

    >>> print(stderr.getvalue())
    usage: sphinx-build [-h] host
    <BLANKLINE>
    Build a full system
    <BLANKLINE>
    positional arguments:
      host        Host to build
    <BLANKLINE>
    optional arguments:
      -h, --help  show this help message and exit
    <BLANKLINE>

And putting the 'conf' in action:

    >>> Config(conf, args=['', 'antares'])
    {host: antares}

.. highlight:: bash

Multiple arguments and options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Lets take a closer look at CLG. Here is the clg key of the sphinx program
used to render and browse this very documentation in real time::

    $ CONF=$(cat << 'EOF'
    >     clg:
    >         prog: $prog
    >         description: $prog $version is a documentation server.
    >         epilog: |
    >             Build sphinx docs, launch a browser for easy reading,
    >             detect and render doc changes with inotify.
    >         options:
    >             version:
    >                 short: v
    >                 action: version
    >                 version: $prog $version
    >             debug:
    >                 short: d
    >                 action: store_true
    >                 default: __SUPPRESS__
    >                 help: show docker call
    >         args:
    >             sphinx_dir:
    >                 nargs: '?'
    >                 default: /data/rst
    >                 help: |
    >                     directory holding sphinx conf.py and doc sources
    >                     (default: %(default)s)
    > EOF
    > )

::

    $ loadconfig -E="$CONF" --help
    usage: $prog [-h] [-v] [-d] [sphinx_dir]

    $prog $version is a documentation server.

    positional arguments:
      sphinx_dir     directory holding sphinx conf.py and doc sources
                     (default: /data/rst)

    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit
      -d, --debug    show docker call

    Build sphinx docs, launch a browser for easy reading,
    detect and render doc changes with inotify.

* prog declares the program name for the usage line. Its content, $prog, will
  be expanded from the prog loadconfig key (not shown here) later on.
* epilog declares the footer of our command. Notice | that is used for
  multiline text.
* options declares optional letters or arguments preceded by -
* short declares a single letter (lower or upper case) for the option.
* default declares a default string literal in case none is provided in the
  command line. __SUPPRESS__ is used to indicate that its argument or option
  should not be included on the processed result.
* `nargs`_ declares how many arguments or options are needed. Common used
  nargs are '?' for 0 or 1, or '*' for 0 or as many as needed. If nargs is
  omitted 1 is assumed.
* `action`_ declares what will be done with the argument or option. version
  indicates the version output. store_true indicates a boolean type.
* version, debug and sphinx_dir are user defined variables that will hold
  input string literals after processed.

.. _nargs: https://docs.python.org/dev/library/argparse.html#nargs
.. _action: https://docs.python.org/dev/library/argparse.html#action

After defining our CONF, we can now put it on action::

    $ loadconfig -E="$CONF"
    export SPHINX_DIR="/data/rst"

Passing no cli arguments return the sphinx_dir variable with its default.
debug variable was suppressed as indicated, and version is only used with its
own call.

If we use the version option with no extra config we get::

    $ loadconfig -E="$CONF" -v
    $prog $version

Adding an extra -E should make a more pleasant result::

    $ loadconfig -E="$CONF" -E="prog: sphinx, version: 0.1" -v
    sphinx 0.1

If we request debugging and define another path::

    $ loadconfig -E="$CONF" -d /data/salt/prog/loadconfig/docs
    export SPHINX_DIR="/data/salt/prog/loadconfig/docs"
    export DEBUG="True"


Now that we have a good overview of the different pieces, lets put them
together. We have built enough knowledge to fully understand our magical
loadconfig program on the :ref:`examples <examples>` chapter.
