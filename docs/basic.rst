.. include:: /defs.irst

=====================
Basic Config Tutorial
=====================

This chapter ilustrates the usage of loadconfig with basic and practical, step
by step examples. Each one of them is in itself a doctest that was run to build
the pypi release package for proper documentation and software validation.


Inline config
=============

Lets start with the most simple and practical example:

    >>> from loadconfig import Config
    >>> Config('greeter: Hi there')
    {greeter: Hi there}

    >>> Config('{greeter: Hi there}')
    {greeter: Hi there}


As we can see, loadconfig uses yaml strings as its way to input data and
represent its state.

Our config object is in itself a yaml flavored OrderedDict:

    >>> c = Config('''
    ...         greeter:
    ...           message: Hi
    ...           group:
    ...             - Jill
    ...             - Ted
    ...             - Nancy
    ...     ''')
    >>> c
    {greeter: {message: Hi, group: [Jill, Ted, Nancy]}}


Notice our greeter was defined with a message, and a group of people to greet,
in that order. We see that both, the message and the group are kept in exactly
that order in the config representation. It might sound the most natural thing
in the world, but remember that 'normal' dictionaries do not keep key order.
There are multiple practical examples where key order is crucial, and in
fact loadconfig itself needs it for processing its clg special keyword.

Lets now see how our config prints:

    >>> print(c)
    greeter:
      message: Hi
      group:
        - Jill
        - Ted
        - Nancy


Not bad. The parsed yaml string and later rendered output generated exactly
the same input. Let's try now feeding back that pretty Config representation

    >>> Config('{greeter: {message: Hi, group: [Jill, Ted, Nancy]}}')
    {greeter: {message: Hi, group: [Jill, Ted, Nancy]}}


Not bad at all! Yaml allowed us to skip all those quotes in literal strings,
making the code much more cleaner. Just for a second lets consider how we
would write a similar expression in python:

    >>> c = {'greeter':
    ...         {'message': 'Hi',
    ...          'group':   ['Jill', 'Ted', 'Nancy']}}


In more complex cases and especially when dealing with the shell, quotes
are a real source of very subtle bugs. So we are gaining in readability and
correctness.


Idempotence
===========

To summarize, let's highlight another desirable property of Config:

    >>> c = Config('greeter: {message: Hi, group: [Jill, Ted, Nancy]}')
    >>> c
    {greeter: {message: Hi, group: [Jill, Ted, Nancy]}}
    >>> c == Config(c)
    True

In other words our config representation is idempotent. Very useful for having
a common unique representation of data regardless of what was done to make it.


Access interface
================

Now, let's check our config access interface:

    >>> c['greeter']
    {message: Hi, group: [Jill, Ted, Nancy]}

    >>> c['greeter']['group']
    ['Jill', 'Ted', 'Nancy']

    >>> c.greeter.group
    ['Jill', 'Ted', 'Nancy']


Right there, we avoided two pairs of quotes and two pairs of square brakets!
We can even intermix the dictionary and the attribute access::

    >>> c['greeter'].group
    ['Jill', 'Ted', 'Nancy']


Overriding keys
===============

Overriding keys is a fundamental feature of loadconfig that gives the ability
to quickly adapt configuration content to the program needs.


    >>> c.update('place: Yosemite')
    >>> c
    {greeter: {message: Hi, group: [Jill, Ted, Nancy]}, place: Yosemite}

    >>> c.greeter.group.append('Steve')
    >>> c
    {greeter: {message: Hi, group: [Jill, Ted, Nancy, Steve]}, place: Yosemite}

As with regular code, the latest key defined wins:

    >>> conf = '''\
    ...     greeter: {message: Hi, group: [Jill, Ted, Nancy]}
    ...     greeter: {message: Hi, group: [Jill, Ted, Nancy, Steve]}'''
    >>> Config(conf)
    {greeter: {message: Hi, group: [Jill, Ted, Nancy, Steve]}}


But what about the DRY (Don't Repeat Yourself) principle? And what about
descriptive programming? Lets explore some of the best features like include
and CLG (Command Line Generator) in the :ref:`intermediate tutorial`
