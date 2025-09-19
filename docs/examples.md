# Full, real application examples

---


## loadconfig as a generic program wrapper

In modern unix systems, the sheer amount of options in most of the cli tools is
plain staggering. Often we have use cases that matter to us, but in order to
use them effectively we find ourselves writing a wrapper around them. The real
goal is to create a new 'interface' with sensible defaults. Now, instead of
thinking in solving our original problem, we are thinking how to solve
implementation details of an imperative language.(do we need to escape that
space?, enclose that string in double quotes?)

Regardless of the language, our tool have a set of common interfaces: argument
processing, documentation, configuration files, and variables. loadconfig is
meant to unify the management of these interfaces with simple, descriptive yaml
strings.

<!--codeinclude-->
[loadconfig](../scripts/loadconfig)
<!--/codeinclude-->

Following loadconfig's philosophy, its script implementation is in itself
straightforward. All imperative programming aspects are kept to minimum. As
we can see, all keywords and concepts of our conf python variable were already
introduced in [cli interface][]. When using a clg key, loadconfig defines the
$prog attribute using args[0]. This allows to decouple the program name from
sys.argv[0]. Sometimes, it is nice to get the program version from an external
source (eg: another module) and feed it into Config. The convenient Config
version parameter is used in this case. At this point, we are familiar with
the Config class. c.export is just a Config method that iterates over all
keywords defined, making them uppercase, replacing space by underline and
prepending the word export. Want to take a guess? We will see shortly why.
Finally, all the actual commands are enclosed in the main function as good
organizational practice and as it allows for easy testing.

Ok Daniel, all of this looks fine. Did I miss something?

This seamlessly simple script hides really well its true expressiveness power
when combined with some shell scripting. Here we go.


## Sphinx renderer

Lets assume we have an application that renders sphinx html documentation,
detects changes in the documentation sources in real time and controls a
browser. There is a wonderful project called [docker][] that encapsulates
incredibly well all the application pieces (libraries, fonts, programs) in a
single unit called image and offers a neat cli to interact with the
operating system. Now, there are lots of possibilities to precisely control how
docker will communicate with the filesystem, with the video and audio
subsystems, with the network ...  Wait! we just want to run our application,
remember?   Sure!  Docker makes the task trivially simple in just one line...
one looong line::

    docker run -d -u admin -v /data/rst:/data/sphinx -e DISPLAY=:0.0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix reg.csl/sphinx

The point is that although it is an incredible simple interface to interact
with the operating system, typing those 'lines' are not exactly fun. loadconfig
allow us to take back the command line interface, defining the defaults we want
in configuration files or within a wrapper and to leave the command line for
the variable arguments we care the most. In this case, most of the docker run
command is setup. The only 'interesting' variable part, is the path of our
sphinx source documents, in this case /data/rst.

<!--codeinclude-->
[sphinx](examples/sphinx)
<!--/codeinclude-->

As this is a full application, there are plenty of details to see. Still,
with a simple glance, we can see 2 distinctive sections. A config section with
just one shell variable, CONF, and an executable section. Most of the 'code'
happens on the CONF variable. The executable section is driven by loadconfig
script, docker and the shell interpreter.


### CONF variable

* version is a literal string, just as the ones on [basic tutorial][].
* desktop_args is another literal string with a twist. It contains the shell
  environment variable DISPLAY. The shell will expand it later.
* docker_args is also a multiline literal string (separated by \\) with a big
  twist

    ```
    docker_args: -d -u admin -v $(realpath $sphinx_dir):/data/sphinx \
        $DESKTOP_ARGS reg.csl/sphinx
    ```

* sphinx_dir is the path we want loadconfig to load as a cli argument. As
  such, it is declared within clg. loadconfig will expand sphinx_dir after it
  runs. We saw loadconfig expansion on the [intermediate tutorial][]

* $(realpath ... ):/data/sphinx is a literal for loadconfig. After loadconfig
  runs the shell will see $(realpath /data/rst):/data/sphinx assuming the
  default defined in clg and will expand $()

* DESKTOP_ARGS is a literal for loadconfig. It will be expanded by the shell

* clg was covered on [cli interface][] except for %(default)s with is
  expanded by clg with /data/rst.

* check_config is a special loadconfig keyword. It makes loadconfig exec the
  declared python string with the primary purpose of validating the
  configuration. In this case, it checks that a conf.py file exist within the
  sphinx_dir path


### Executable section

This is where the 'action' happens.

* set -e makes the shell to stop when a command does not succeed. This is
  good shell programming practice and loadconfig takes advantage of it.
* ENV=$(loadconfig -E="prog: $(basename $0)" -E="$CONF" "$@") executes
  loadconfig which will interpret our CONF variable and the command line
  arguments. Remember that loadconfig printed export lines with the each key
  of config?  This output is assigned to the ENV shell variable. There are
  two cases where loadconfig will not print envars: when passing the options
  -h or -v. -h is controlled by clg and -v by the version action on the CONF
  variable. In these cases loadconfig script exits with 1 which signals the
  shell to stop as we just saw. The version and the help are printed to the
  standard error so they can be seen instead of being taken as ENV content.
* eval "$ENV" is what makes those text exported strings become shell
  environment variables and as such leverage shell commands like docker in this
  case.

The rest of the lines are simple shell commands:

* [ $DEBUG ] && echo "docker run $DOCKER_ARGS" ouputs the docker call in case
  we pass the -d option for debugging purpose
* cid=$(docker run $DOCKER_ARGS) launches the docker image reg.csl/sphinx and
  assigns the container id (sort of a process in normal shell) to the cid
  shell variable.
* docker wait $cid will wait for the container to stop before returning control
  to the shell
* And finally docker rm $cid >/dev/null does the cleanup removing the container


Docker is just one (very good) use case example. François Ménabé, the author of
CLG, shows us how to leverage KVM virtual machines on his [CLG examples][].
Pretty much all functionality and examples from CLG work unmodified in
loadconfig, including CLG execute keyword. There is plenty of [CLG][] and
[argparse][] documentation to make the most of the cli.


[argparse]: https://docs.python.org/3/library/argparse.html
[bash hackers]: http://wiki.bash-hackers.org
[basic tutorial]: basic.md
[CLG examples]: https://clg.readthedocs.org/en/latest/examples.html
[CLG]: https://clg.readthedocs.org
[cli interface]: intermediate.md#cli-interface
[docker]: https://www.docker.com
[intermediate tutorial]: intermediate.md
