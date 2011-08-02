.. figure:: http://www.coactivate.org/projects/sauna-sprint-2010/project-home/image.jpeg

*sauna.reload: so that you can finish your Plone development today and relax in
sauna after calling it a day*


Introduction
------------

``sauna.reload`` is an attempt to recreate ``plone.reload`` without the issues
it has. Like being unable to reload new grokked views or portlet code.

``sauna.reload`` does reloading by using a fork loop. So actually it does not
reload the code, but restarts small part of Zope2.

It does following on Zope2 startup:

* Defers loading of your development packages by hooking into PEP 302 loader
  and changing their ``z3c.autoinclude`` target module

* Starts a watcher thread which monitors changes in your development py-files

* Stops loading of Zope2 in ``zope.processlifetime.IProcessStarting`` event by
  stepping into a infinite loop; Just before this, tries to load all
  non-developed dependencies of your development packages (resolved by
  ``z3c.autoinclude``)

* It forks a new child and lets it pass the loop

* Loads all your development packages invoking ``z3c.autoinclude``. This is
  fast!

* And now every time when the watcher thread detects a change in development
  files it will signal the child to shutdown and the child will signal
  the parent to fork new a child when it is just about to close itself

* Just before dying, the child saves ``Data.fs.index`` to help the new child to
  see the changes in ZODB (by loading the saved index)

* GOTO 4


Installing
----------

Add this package to your buildout eggs and add following
``zope-conf-additional`` line  to you instance part of buildout.cfg::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zope-conf-additional = %import sauna.reload


Using
-----

Fork loop is not active by default. You can activate it by setting
``RELOAD_PATH`` environment variable to your development egg path(s)::


    RELOAD_PATH=src bin/instance fg

    Or if you want to optimize load speed you can specify your eggs one by one:

    RELOAD_PATH=src/my.egg:src/my.another.egg bin/instance fg

Known issues
------------

* If there is an start up error you'll get a loop of forever

* Currently reloading is limited to new style z3c.autoincluded Python packages
  and does not cover old-style Products.XXX namespaced packages or
  Five-packages (== does not reload Archetypes yet)

* Currently only FileStorage (ZODB) is supported

* The watcher (watchdog) does not compile on OS X Lion 10.7. Snowleopard is
  fine


TODOs
-----

* Figure out how to detect failed installation of packages in atexit of Zope2
  to prevent infinitely spawning fork loop

* Be able to reload oldschool (Products.XXX and Five) packages too

* Update ``autoincludetools.py`` to use ``reload_watch_dir`` env

* Test it!

* Find out the limitations

* Disable fork loop if debug mode is not on

* Disable fork loop when running tests


Authors
-------

* Esa-Matti Suuronen (esa-matti aet suuronen.org)

* Asko Soukka (asko.soukka aet iki.fi)

* Mikko Ohtamaa (idea)

* Andreas Jung (approved in IRC)

300 kg of beer was consumed to create this package (at least). Also several
kilos of firewood, one axe, one chainsaw and one boat.
