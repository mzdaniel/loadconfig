# Advanced Tutorial

There are plenty of advanced topics available to us. Here, we will try to look
at them with an emphasis on simplicity.

---


## Multiple commands and execution

Once we start adding more capabilities to our program, we might find having
multiple commands with their own arguments and options does make the interface
cleaner. To make it simple, let's look at a small program that can install,
run and uninstall itself:

    :::python
    $ ls -l netapplet
    -rwxr-xr-x 1 admin admin 784 2025-09-17 16:32:58 netapplet

    $ cat netapplet
    #!/usr/bin/env python
    from loadconfig import Config
    from sys import argv

    conf = """\
        clg:
            subparsers:
                run:       {help: 'run as:  $prog run',
                            execute: {module: __main__, function: run}}
                install:   {help: 'run as:  $prog install | bash',
                            execute: {module: __main__, function: install}}
                uninstall: {help: 'run as:  $prog uninstall | bash',
                            execute: {module: __main__, function: uninstall}}
        """

    def install(clg_ns):
        print(f'mkdir -p ~/bin; cp {argv[0]} ~/bin')

    def uninstall(clg_ns):
        print(f'rm -f {argv[0]}')

    def run(clg_ns):
        print(f'Running {argv[0]}')

    def main(args):
        c = Config(conf, args=args)

    if __name__ == '__main__':
        main(argv)


A couple of runs will show:

    :::bash
    # Our program is not installed in $PATH
    netapplet
    bash: netapplet: command not found

    # To keep things simple, let's temporarely add ~/bin to the shell session
    export PATH=~/bin:"$PATH"

    # Running netapplet from the current directory
    # ( ./ needs to be prepended to the command as . is not usually on $PATH )
    $ ./netapplet
    usage: netapplet [-h] {run,install,uninstall} ...


    # Retrieving help
    $ ./netapplet --help
    usage: netapplet [-h] {run,install,uninstall} ...

    positional arguments:
      {run,install,uninstall}
        run                 run as:  ./netapplet run
        install             run as:  ./netapplet install | bash
        uninstall           run as:  ./netapplet uninstall | bash

    options:
      -h, --help            show this help message and exit

    # Looking the output of install
    ./netapplet install
    mkdir -p ~/bin; cp ./netapplet ~/bin

    # Sounds good. Lets install it according to the help.
    $ ./netapplet install | bash

    # Checking our program is now available
    $ ls -la ~/bin/netapplet
    -rwxr-xr-x 1 admin admin 784 2025-09-17 16:38:58 /data/admin/bin/netapplet

    # and working... (notice no ./)  Yeey!
    $ netapplet run
    Running /data/admin/bin/netapplet

    # Time to uninstall it
    $ ./netapplet uninstall
    rm -f ./netapplet
    $ netapplet uninstall | bash

    # And... it's gone
    $ netapplet run
    /bin/ash: netapplet: not found


The program is clean, self-installable and self-documented.

The first line is a typical unix shebang to look for the system or virtualenv
python shell. (Note: $VIRTUAL_ENV could had been used to optionally autoinstall
within the virtualenv). It follows a couple import lines and the conf global
variable. The install, uninstall and run functions are simple print statements
that will be leveraged by a shell in our program, though these functions
can be as complex as wanted, being part of other modules, etc. They receive
clg namespace configuration as the first argument. The main function is called
if our program is executed directly. This is a good programming and testing
practice. Having main as a function with parameters allows to test it with
handcrafted arguments. Lets now focus on the conf and the functions.

conf is a clg key with subparsers. This is an argparse concept which basically
means a subcommand. In our case we have three of them with their documentation.
If you are wondering why the quotes in the help of the subparsers keys, this is
to escape the usual yaml meaning of the colon (:) char on these help strings.
As we are using a clg key, loadconfig (through clg) assigns args[0] to the
$prog attribute, decoupling the program name from sys.argv[0].
Once Config(conf, args=args) is called, clg creates a configuration based on
the command line arguments and passes it to the function requested. After
the function finishes, loadconfig return a Config object like
{prog: ./netapplet, command0: run}.


## loadconfig CLG features

One key feature of loadconfig is its CLG integration. We saw in
[cli interface][] some of its features. Here, we mention extra features
that loadconfig adds to [CLG][]


### default command

This feature is used to add a default command to loadconfig cli. In
[Multiple commands and execution][], a clg subparsers example was presented.
Lets show again how it runs:

    :::bash
    # Using the conf variable as in the original example
    $ ./netapplet run
    Running ./netapplet

    $ ./netapplet
    usage: netapplet [-h] {run,install,uninstall} ...

If instead we introduce default_cmd to conf, it now renders:

    conf = """\
        clg:
            default_cmd:   run
            subparsers:
                run:       {help: 'run as:  $prog run',
        ...

    $ ./netapplet
    Running ./netapplet


## Closing

The netapplet program succinctly highlights very important needs in a
program lifecycle (configuration, interface, documentation, deployment)
and it can easily be used as a base for more complex ones.


[advanced tutorial]: advanced.md
[CLG]: https://clg.readthedocs.org
[cli interface]: intermediate.md#cli-interface
