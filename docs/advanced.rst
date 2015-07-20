.. include:: /defs.irst

.. _advanced tutorial:

=================
Advanced Tutorial
=================

There are plenty of advanced topics available to us. Here, we will try to look
at them with an enphasis on simplicity.


Multiple commands and execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once we start adding more capabilities to our program, we might find having
multiple commands with their own arguments and options does make the interface
cleaner. To keep it simple, let's look at a small program that can install,
run and uninstall itself:

.. code-block:: bash

    $ ls -l netinstall.py
    -rwxr-xr-x 1 admin admin 745 Jul  2 21:00 netapplet.py

    $ cat netinstall.py

.. code-block:: python

    #!/usr/bin/env python

    from loadconfig import Config
    import sys

    conf = """\
        clg:
            subparsers:
                run:
                    help: 'run as:  $prog run'
                install:
                    help: 'run as:  $prog install | sudo bash'
                uninstall:
                    help: 'run as:  $prog uninstall | sudo bash'
        """

    def install(c):
        print('cp {} /usr/bin'.format(c.prog))

    def uninstall(c):
        print('rm -f /usr/bin/{}'.format(c.prog))

    def run(c):
        print('Running {}'.format(c.prog))

    def main(args):
        c = Config(conf, args=args)
        c.run()

    if __name__ == '__main__':
        main(sys.argv)


A couple of runs will show:

.. code-block:: bash

    # Our program is not installed in the system /usr/bin directory
    netapplet.py
    bash: netapplet.py: command not found


    # Running netapplet.py from the current directory.
    # ( ./ needs to be prepended to the command as . is not usually on $PATH )
    $ ./netapplet.py
    usage: netapplet.py [-h] {run,install,uninstall} ...


    # Retrieving help
    $ ./netapplet.py --help
    usage: netapplet.py [-h] {run,install,uninstall} ...

    positional arguments:
      {run,install,uninstall}
        run                 run as:  ./netapplet.py run
        install             run as:  ./netapplet.py install | sudo bash
        uninstall           run as:  ./netapplet.py uninstall | sudo bash

    optional arguments:
      -h, --help            show this help message and exit


    # Looking the output of install
    ./netapplet.py install
    cp ./netapplet.py /usr/bin


    # Sounds good. Lets install it according to the help.
    $ ./netapplet.py install | sudo bash


    # Checking our program is working on the system. Yeey!
    $ netapplet.py run
    Running /usr/bin/netapplet.py


    # Time to uninstall it
    $ ./netapplet.py uninstall | sudo bash

    # And... it's gone
    $ netapplet.py run
    bash: /usr/bin/netapplet.py: No such file or directory


The program is clean, self-installable and self-documented.

The first line is a typical unix shebang to look for the system or virtualenv
python shell. (Note: $VIRTUAL_ENV could had been used to optionally autoinstall
within the virtualenv). It follows a few import lines and the conf global
variable. The install, uninstall and run functions are simple print statements
that will be leveraged by a sudo shell in our program, though these functions
can be as complex as wanted, being part of other modules, etc. They receive
the configuration as the first argument. The main function is called if our
program is executed directly. This is a good programming and testing practice.
Having main as a function with parameters allows to test it with handcrafted
arguments. Lets now focus on the conf and the main functions.

conf is a clg key with subparsers. This is an argparse concept which basically
means a subcommand. In our case we have three of them with their documentation.
If you are wondering why the quotes in the help of the subparsers keys, this is
to escape the usual yaml meaning of the colon (:) char on these help strings.
As we are using a clg key, loadconfig assigns args[0] to the $prog attribute,
decoupling the program name from sys.argv[0]. Next, it loads the configuration
in the c variable, and finally c.run() executes the function invoked by the cli
arguments. c.run() only makes sense if the config holds a clg key with
subparsers.

This simple program succinctly highlights very common needs in a program
lifecycle (configuration, interface, documentation, deployment) and it can
easily be used as a base for more complex ones.
