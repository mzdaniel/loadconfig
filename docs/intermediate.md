# Intermediate tutorial

---

## Yaml expansion

Yaml config sources are meant to reduce redundancy whenever possible:

    :::python
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

    :::python
    >>> conf = '''\
    ...     name: [Zeela, Kim]
    ...     team: $name
    ...     choreography: $team
    ...     '''
    >>> Config(conf)
    {name: [Zeela, Kim], team: [Zeela, Kim], choreography: [Zeela, Kim]}


## loadconfig yaml goodies


!!! note ""
    Yaml is highly sensitive of leading whitespaces. Similarly to pyyaml itself,
    loadconfig dedents its yaml_string input before anything else.


### Include

Another feature is the ability to include config files from a yaml config
source:

    :::python
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

    :::python
    >>> conf = 'colors: !include birds.yml:hummingbird:colors'
    >>> Config(conf)
    {colors: [iris, teal, coral]}


### Substitution

This feature allows to expand just a key from a previously included yaml file:

    :::python
    >>> conf = '''\
    ...     _: !include birds.yml:&
    ...     colors: !expand hummingbird:colors
    ...     '''
    >>> Config(conf)
    {colors: [iris, teal, coral]}


### Pre-processed !include

If !include needs to be pre-processed before the resulting yaml string
is parsed, insert it at the beginning of a line with a newline after the
file path. In this mode, loadconfig will literally replace the !include
line with the file content.

For the following example, loadconfig first dedents the conf string as
usual, then replaces all pre-processed !include lines, and finally passes
the resulting string to pyyaml. Note that without dedenting birds.yml, this
example would have been broken:

    :::python
    >>> from textwrap import dedent
    >>> content = dedent(open('birds.yml').read())
    >>> with open('birds.yml', 'w') as fh:
    ...     _ = fh.write(content)
    >>>
    >>> conf = '''\
    ...     goldfinch:
    ...       colors: [yellow]
    ...
    ...     !include birds.yml
    ... '''
    >>> Config(conf)
    {goldfinch: {colors: [yellow]}, hummingbird: {colors: [iris, teal, coral]}}


### Environment variables

Plenty of times it is *very* useful to access environment variables. They
provide a way to inherit configuration and even they could make our programs
more secure as envvars are runtime configuration:

    :::python
    >>> from os import environ
    >>> environ['CITY'] = 'San Francisco'
    >>> c = Config('!env city')
    >>> c.city
    'San Francisco'


### Read files

Another common use is to load a key reading a file. This is different from
include as the file content is literally loaded to the key instead of being
interpreted as yaml:

    :::python
    >>> with open('libpath.cfg', 'w') as fh:
    ...     _ = fh.write('/usr/local/lib')
    >>> Config('libpath: !read libpath.cfg')
    {libpath: /usr/local/lib}


## Introducing -E and -C cli switches

As with the inline config and include, we have the -E switch for extra yaml
config and -C for yam config files. Let's looks again at our beautiful
hummingbird:

    :::python
    >>> birds = '''\
    ...     hummingbird:
    ...       colors: [iris, teal, coral]
    ...     '''
    >>> extra_arg = '-E="{}"'.format(birds)
    >>> Config(args=[extra_arg])
    {hummingbird: {colors: [iris, teal, coral]}}


Similarly we can introduce the same data through a configuration file. In this
case, we will reuse our birds.yml file with simply:

    :::python
    >>> Config(args=['-C="{}"'.format('birds.yml')])
    {hummingbird: {colors: [iris, teal, coral]}}


These operations are in themselves pretty useful. They are even more revealing
when considering them in the shell context. loadconfig is at its core a python
library, so the issue is how do we bridge these two worlds. Shell environment
variables, and some little magic from our loadconfig script would help. Let's
reintroduce loadconfig script call here:

    :::bash
    $ BIRDS='hummingbird: [iris, teal, coral]'
    $ loadconfig -E="$BIRDS"
    export HUMMINGBIRD="iris teal coral"


If our bird decided to take a nap in a file, it would be:

    :::bash
    $ echo "$BIRDS" > birds.yml
    $ loadconfig -C="birds.yml"
    export HUMMINGBIRD="iris teal coral"


At this point, we can use both switches. loadconfig accepts them in sequence,
updating and overriding older data with new values from the sequence:

    :::bash
    $ BIRDS2="hummingbird: [ruby, myrtle]"
    $ BIRDS3="swallow: [cyan, yellow]"
    $ loadconfig -E="$BIRDS2" -C="birds.yml" -E="$BIRDS3"
    export HUMMINGBIRD="iris teal coral"
    export SWALLOW="cyan yellow"

    $ loadconfig -E="$BIRDS3" -C="birds.yml" -E="$BIRDS2"
    export SWALLOW="cyan yellow"
    export HUMMINGBIRD="ruby myrtle"


## CLI interface

One key feature of loadconfig is its CLG integration. [CLG][] is a wonderful
yaml based command line generator that wraps the standard argparse module.
Loadconfig uses a special clg keyword to unleash its power.

[CLG]: https://clg.readthedocs.org


### First steps

Lets start with a more concise shell example to get the concepts first:

    :::bash
    $ CONF=$(cat << 'EOF'
    >   clg:
    >     description: Build a full system
    >     args: {host: {help: Host to build}}
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
lines:

    :::bash
    $ loadconfig -E="$CONF" antares
    export HOST="antares"


Think about it for a second. We fed yaml 'data' lines that actually
controlled the 'behavior' of our program. It created a meaningful  interface,
processed the arguments and output a shell environment variable for further
processing. The core of the whole activity was the data and its organization
that matters for the programmer instead of the individual lines of code
normally required by programming languages. This is what this author calls
descriptive programming.

The following lines shows the same snippet for python. Lets play with clg:

    :::python
    >>> from loadconfig import Config
    >>> conf = '''
    ...     clg:
    ...         description: Build a full system
    ...         args: {host: {help: Host to build}}
    ...     '''
    >>> try:
    ...     c = Config(conf, args=['sysbuild', '--help'])
    ... except SystemExit as e:
    ...     exc = e
    >>> print(exc.code)
    usage: sysbuild [-h] host
    <BLANKLINE>
    Build a full system
    <BLANKLINE>
    positional arguments:
      host        Host to build
    <BLANKLINE>
    options:
      -h, --help  show this help message and exit


And putting the 'conf' in action:

    :::python
    >>> Config(conf, args=['', 'antares'])
    {prog: '', host: antares}


### Multiple arguments and options

Lets take a closer look at CLG. Here is the clg key of the sphinx program
used to render and browse this very documentation in real time:

    :::bash
    $ CONF=$(cat << 'EOF'
    >     clg:
    >         prog: $prog
    >         description: $prog $version is a documentation server.
    >         epilog: |
    >             Build sphinx docs, launch a browser for easy reading,
    >             detect and render doc changes with inotify.
    >         options:
    >             version: {short: v, action: version, version: $prog $version}
    >             debug:   {short: d, action: store_true, default: __SUPPRESS__,
    >                       help: show docker call}
    >         args:
    >             sphinx_dir: {nargs: '?', default: /data/rst,
    >                help: |
    >                       directory holding sphinx conf.py and doc sources
    >                       (default: %(default)s)}
    > EOF
    > )


    $ loadconfig -E="$CONF" --help
    usage: $prog [-h] [-v] [-d] [sphinx_dir]

    $prog $version is a documentation server.

    positional arguments:
      sphinx_dir     directory holding sphinx conf.py and doc sources
                     (default: /data/rst)

    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program\'s version number and exit
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
  command line. \__SUPPRESS__ is used to indicate that its argument or option
  should not be included on the processed result.
* [nargs][] declares how many arguments or options are needed. Common used
  nargs are '?' for 0 or 1, or '*' for 0 or as many as needed. If nargs is
  omitted 1 is assumed.
* [action][] declares what will be done with the argument or option. version
  indicates the version output. store_true indicates a boolean type.
* version, debug and sphinx_dir are user defined variables that will hold
  input string literals after processed.

[nargs]: https://docs.python.org/dev/library/argparse.html#nargs
[action]: https://docs.python.org/dev/library/argparse.html#action


After defining our CONF, we can now put it on action:

    :::bash
    $ loadconfig -E="$CONF"
    export SPHINX_DIR="/data/rst"


Passing no cli arguments return the sphinx_dir variable with its default.
debug variable was suppressed as indicated, and version is only used with its
own call.

If we use the version option with no extra config we get:

    :::bash
    $ loadconfig -E="$CONF" -v
    $prog $version


Adding an extra -E should make a more pleasant result:

    :::bash
    $ loadconfig -E="$CONF" -E="prog: sphinx, version: 0.1" -v
    sphinx 0.1


If we request debugging and define another path:

    :::bash
    $ loadconfig -E="$CONF" -d /data/salt/prog/loadconfig/docs
    export SPHINX_DIR="/data/salt/prog/loadconfig/docs"
    export DEBUG="True"


Now that we have a good overview of the different pieces, lets put them
together. We have built enough knowledge to fully understand our magical
loadconfig program on the [examples][] chapter.
More advanced material can also be found in [advanced tutorial][].

[examples]: examples.md
[advanced tutorial]: advanced.md
