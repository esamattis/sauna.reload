.. figure:: https://github.com/epeli/sauna.reload/raw/gh-pages/saunasprint_logo.jpg

*sauna.reload: so that you can finish your Plone development today and relax in
sauna after calling it a day*

.. contents:: :local:

Introduction
=============

``sauna.reload`` partially restarts Plone and reloads your changed source
code every time you save a file.

* Edit your code

* Save 

* Go to a browser and hit *Refresh* -> your latest changes are active

It greatly simplifies your Plone development workflow and gives back the agility of Python.

It works with any code.

``sauna.reload`` works on OSX and Linux. In theory works on Windows, but no one has looked into that yet.

Installation
==============

Here are brief installation instructions.

Prerequisitements
-------------------

In order to take the advantage of ``sauna.reload``

* You know how to develop your own Plone add-ons and basics of buildout folder structure

* You know UNIX command line basics

* You know how to run buildout

No knowledge for warming up sauna is needed in order to use this product.

.. note ::

        Currently it is recommended to install sauna.reload directly from
        GitHub as it is under heavy development.

Using new buildout file for the development
---------------------------------------------------

This is the recommended approach how to enable ``sauna.reload`` for your development
environment.

Use git to feacth  ``sauna.reload`` source code to your buildout environment::

        cd src
        git clone git://github.com/epeli/sauna.reload.git
        
Create a new buildout file ``development.cfg`` which extends
your existing ``buildout.cfg`` - this way you can easily
keep development stuff separate from your main buildout.cfg
which you can also use on the production server.

``development.cfg``::

        [buildout]
        
        extends = buildout.cfg
        
        develop +=
                src/sauna.relaod
        
        [instance]
        
        # XXX: May conflict with existing xope-conf-additional directives
        zope-conf-additional = 
                %import sauna.reload
                
        eggs +=
                sauna.reload

.. note ::

        With this approach you do not need to modify the existing
        buildout.cfg.
                
Then build it out with this special config file::

        bin/buildout -c development.cfg

*I like to buildout buildout. I like to buildout buildout...*
               
OSX special notes
++++++++++++++++++

.. note :: 

        The following applies to OSX only until
        Watchog 0.5.4+ is released.
               
For OSX you need to install trunk version of WatchDog
providing `FSEvents <http://en.wikipedia.org/wiki/FSEvents>`_ based file-system monitoring support.
                                
**Do this before running buildout. Otherwise delete existing downloaded
WatchDog eggs**.                                
                                
::

        cd src
        # Activate your virtualenv or whatever
        # Python you are using for the buildout
        source ~/code/collective.buildout.python/python-2.6/bin/activate
        git clone git://github.com/gorakhargosh/watchdog.git
        cd watchdog
        python setup.py install
        
It will complain::

        error: yaml.h: No such file or directory
        
... but just ignore it.                
        
Updating the existing buildout.cfg
-------------------------------------

Alternatively you can just hack your existing buildout.cfg to have sauna.reload.

Add this package to your buildout eggs and add following
``zope-conf-additional`` line  to you instance part of buildout.cfg::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zope-conf-additional = %import sauna.reload


Usage: start Plone in reload enabled manner
=============================================

To start Plone with reload functionality you need
to give special environment variable ``RELOAD_PATH``
for your instance command::

    RELOAD_PATH=src bin/instance fg

Or if you want to optimize load speed you can directly specify only some of
your development products::

    RELOAD_PATH=src/my.product:src/my.another.product bin/instance fg

.. warning ::

        If other products depend on your product, e.g CMFPlone dependencies, 
        sauna.reload does not kick in early enough and the reload does not work.
        
        
When reload is active you should see something like this in your console
when Zope starts up::

        2011-08-10 13:28:59 INFO sauna.reload Starting file monitor on /Users/moo/code/x/plone4/src
        2011-08-10 13:29:02 INFO sauna.reload We saved at least 29.8229699135 seconds from boot up time
        2011-08-10 13:29:02 INFO sauna.reload Packages marked for reload are listed in here: http://127.0.0.1:8080/@@saunareload
        2011-08-10 13:29:02 INFO sauna.reload Fork loop starting on process 14607
        2011-08-10 13:29:02 INFO sauna.reload Booted up new new child in 0.104816913605 seconds. Pid 14608
        
... and when you save some file in ``src`` folder::

        2011-08-10 13:29:41 INFO SignalHandler Caught signal SIGINT
        2011-08-10 13:29:41 INFO Z2 Shutting down
        2011-08-10 13:29:42 INFO SignalHandler Caught signal SIGCHLD
        2011-08-10 13:29:42 INFO sauna.reload Booted up new new child in 0.123936891556 seconds. Pid 14609

CTRL+C should terminate Zope normally. There might be stil some kinks and error messages with shutdown.


Manual reload
---------------

There is also a view on Zope2 root from which it is possible to
manually reload code

   http://127.0.0.1:8080/@@saunareload

Debugging with ``sauna.reload``
===============================

Regular ``import pdb; pdb.set_trace()`` will work just fine with
``sauna.reload``. When reload happens while in pdb, though, pdb will get
killed. To avoid losing your terminal echo, because of reload unexpectedly killing
your pdb, you may add the following to your ``~/.pdbrc``::

   import termios, sys
   term_fd = sys.stdin.fileno()
   term_echo = termios.tcgetattr(term_fd)
   term_echo[3] = term_echo[3] | termios.ECHO
   term_result = termios.tcsetattr(term_fd, termios.TCSADRAIN, term_echo)

Background
============

``sauna.reload`` is an attempt to recreate ``plone.reload`` without the issues
it has. Like being unable to reload new grokked views or portlet code. This
project was started on Plone Sauna Sprint 2011. There for the name,
``sauna.reload``.

It can currently reload following:

*  Portlets

*  Schema Interface changes

*  Adapters

*  Meta programming magic

*  ZCML

* Translations (changes in PO files)

* etc.


``sauna.reload`` does reloading by using a fork loop. So actually it does not
reload the code, but restarts small part of Zope2.

It does following on Zope2 startup:

1. Defers loading of your development packages by hooking into PEP 302 loader
   and changing their ``z3c.autoinclude`` target module

2. Starts a watcher thread which monitors changes in your development py-files

3. Stops loading of Zope2 in ``zope.processlifetime.IProcessStarting`` event by
   stepping into a infinite loop; Just before this, tries to load all
   non-developed dependencies of your development packages (resolved by
   ``z3c.autoinclude``)

4. It forks a new child and lets it pass the loop

5. Loads all your development packages invoking ``z3c.autoinclude``. This is
   fast!

6. And now every time when the watcher thread detects a change in development
   files it will signal the child to shutdown and the child will signal
   the parent to fork a new child when it is just about to close itself

7. Just before dying, the child saves ``Data.fs.index`` to help the new child
   to see the changes in ZODB (by loading the saved index)

8. GOTO 4

Internally ``sauna.reload`` uses 
`WatchDog <http://pypi.python.org/pypi/watchdog>`_
Python component for monitoring file-system change events.


Events
=========

.. note::

        The following concerns you only if your code
        needs to react specially to reloads (clear caches,
        etc.)

``sauna.reload`` emits couple of events during reloading.

   sauna.reload.events.INewChildForked

Emited immediately after new process is forked. No development packages have
been yet installed.  Useful if you want to do something before your code gets
loaded.  Note that you cannot listen this event on a package that is marked for
reloading as it is not yet installed when this is fired.

   sauna.reload.events.INewChildIsReady

Emitted when all the development packages has been installed to the new forked
child.  Useful for notifications etc.

Limitations
===============

Defering installation of development packages to the end of Plone boot up
process means that reloading of Core Plone packages is tricky (or impossible?).
For example plone.app.form is depended by CMFPlone and CMFPlone really must be
installed before the fork loop or there would be no speed difference between
``sauna.reload`` and normal Plone restart. So we cannot defer the installation
of plone.app.form to the end of boot up process. You would have to remove the
dependency from CMFPlone for development to make it work...

Also because the product installation order is altered you may find some issues
if your product does something funky on installation or at import time.

Currently only FileStorage (ZODB) is supported.

Please report any other issues at:
https://github.com/epeli/sauna.reload/issues.

Troubleshooting
==================

Report all issues on `GitHub <https://github.com/epeli/sauna.reload>`_.

Too many files open on OSX
-----------------------------

This happens when starting Plone in relaod mode.

Probably FSEvents support is not active in Watchdog. Follow
the instructions above.

OSX has limitation of 256 file handles. If not using 
FSEvents (using kqueue) each monitored file needs an open handle.
Raising the ulimit of open file handles is not exactly trivial on OSX.

More info

* https://github.com/epeli/sauna.reload/issues/4

Source
=======

On `GitHub <https://github.com/epeli/sauna.reload>`_.

Credits
=======

* Esa-Matti Suuronen [esa-matti aet suuronen.org]

* Asko Soukka [asko.soukka aet iki.fi]

* Mikko Ohtamaa (idea, doccing)

* Vilmos Somogyi (logo). The logo was originally the logo of 
  Sauna Sprint 2011 and it was created by
  Vilmos Somogyi.

* `Yesudeep Mangalapilly <https://github.com/gorakhargosh>`_
  for creating ``WatchDog`` component and providing support
  for Sauna Sprint team using it

Thanks to all happy hackers on Sauna Sprint 2011!

300 kg of beer was consumed to create this package (at least). Also several
kilos of firewood, one axe, one chainsaw and one boat.

We still need testers and contributors. You are very welcome!
