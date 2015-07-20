.. include:: /defs.irst

.. _features:

========
Features
========

loadconfig CLG features
=======================

One key feature of loadconfig is its CLG integration. We saw in
:ref:`cli interface` some of its features. Here, we mention extra features
that loadconfig adds to `CLG`_


default_cmd
~~~~~~~~~~~

This feature is used to add a default command to loadconfig cli. In
:ref:`advanced tutorial`, an example of clg subparsers was presented. Lets
show again how it runs::

    # Using the conf variable as in the original example
    $ netapplet.py run
    Running /usr/bin/netapplet.py

    $ ./netapplet.py
    usage: netapplet.py [-h] {run,install,uninstall} ...

If instead we introduce default_cmd to conf, it now renders::

    conf = """\
        clg:
            default_cmd: run
            subparsers:
                run:
                    help: 'run as:  $prog run'

    $ ./netapplet.py
    Running ./netapplet.py


.. _CLG: https://clg.readthedocs.org/en/latest
