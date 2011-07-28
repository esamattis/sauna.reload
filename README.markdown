# sauna.reload

sauna.reload is an attempt to recreate [plone.reload][] without the issues it
has. Like being unable to reload new views or portlet code.


sauna.reload does reloading by using a fork loop. So actually it does not
reload the code, but restarts small part of Zope2.


It does following on Zope2 startup:

1. Defers loading of your development packages by hooking into PEP 302 loader
2. Starts a watcher thread which monitors changes in your development py-files
3. Stops loading of Zope2 in zope.processlifetime.IProcessStarting event by
   stepping into a infinite loop
4. It forks a new child and lets it pass the loop
5. Installs all your development packages. This is fast!

And now every time when the watcher thread detects a change in development
files it will signal the child to shutdown and the child will signal the parent
to fork new a child when it is just about to close itself.

## Installing

Add this package to your buildout eggs and add following zope-conf-additional
line and reload_watch_dir environment var to you instance part of buildout.cfg:

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zope-conf-additional = %import sauna.reload
    environment-vars =
        reload_watch_dir ${buildout:directory}/src


## Known issues

  * Caching issues with ZODB(?)
  * The watcher (watchdog) does not compile on OS X


## Authors

  * Esa-Matti Suuronen (esa-matti aet suuronen.org)
  * Asko Soukka (asko.soukka aet iki.fi)


Idea: Mikko Ohtamaa


