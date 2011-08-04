.. figure:: http://www.coactivate.org/projects/sauna-sprint-2010/project-home/image.jpeg

*sauna.reload: so that you can finish your Plone development today and relax in
sauna after calling it a day*

Please, see `Known Issues`_ and `TODOs`_. Report new issues at:
https://github.com/epeli/sauna.reload/issues.

Introduction
============

``sauna.reload`` is an attempt to recreate ``plone.reload`` without the issues
it has. Like being unable to reload new grokked views or portlet code.

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


Known issues
============

* Currently only FileStorage (ZODB) is supported

* The watcher (watchdog) does not compile on OS X Lion 10.7. Snowleopard is
  fine

* Reloading of Plone core packages is very tricky

TODOs
=====

* Test it!

* Find out the limitations


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


Authors
=======

* Esa-Matti Suuronen (esa-matti aet suuronen.org)

* Asko Soukka (asko.soukka aet iki.fi)

* Mikko Ohtamaa (idea)

* Andreas Jung (approved in IRC)

300 kg of beer was consumed to create this package (at least). Also several
kilos of firewood, one axe, one chainsaw and one boat.
