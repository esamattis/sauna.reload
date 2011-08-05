.. figure:: https://github.com/epeli/sauna.reload/raw/gh-pages/saunasprint_logo.jpg

*sauna.reload: so that you can finish your Plone development today and relax in
sauna after calling it a day*


Introduction
============

``sauna.reload`` is an attempt to recreate ``plone.reload`` without the issues
it has. Like being unable to reload new grokked views or portlet code. This
project was on Plone Sauna Sprint 2011. There for the name, ``sauna.reload``.

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
   the parent to fork new a child when it is just about to close itself

7. Just before dying, the child saves ``Data.fs.index`` to help the new child
   to see the changes in ZODB (by loading the saved index)

8. GOTO 4




Installing
==========

Add this package to your buildout eggs and add following
``zope-conf-additional`` line  to you instance part of buildout.cfg::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zope-conf-additional = %import sauna.reload


Using
=====

Fork loop is not active by default. You can activate it by setting
``RELOAD_PATH`` environment variable to your development product path(s). In
most setups ``src`` is what you want::

    $ RELOAD_PATH=src bin/instance fg

Or if you want to optimize load speed you can directly specify only some of
your development products::

    $ RELOAD_PATH=src/my.product:src/my.another.product bin/instance fg

There is also a view on Zope2 root from which it is possible to
manually reload code

   http://127.0.0.1:8080/@@saunareload


Events
------

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
-----------

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

Please, report issues at:
https://github.com/epeli/sauna.reload/issues.



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

Troubleshooting
==================

Too many files open on OSX
-----------------------------

Watchdog, the Python library used by sauna.reload internally,  
must be compiled with fsevent support to allow file-system monitoring without
need to open each individual file. In OSX Snow Leopard the default limit of open file handles
is 256 and on OSX raising this limit is made unnecessary difficult.

More info

* https://github.com/epeli/sauna.reload/issues/4

Authors
=======

* Esa-Matti Suuronen (esa-matti aet suuronen.org)

* Asko Soukka (asko.soukka aet iki.fi)

* Mikko Ohtamaa (idea)

Thanks to all happy hackers on Sauna Sprint 2011!

The logo was originally the logo of Sauna Sprint 2011 and it was created by
Vilmos Somogyi.

300 kg of beer was consumed to create this package (at least). Also several
kilos of firewood, one axe, one chainsaw and one boat.


We still need testers and contributors. You are very welcome!
