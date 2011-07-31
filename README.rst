
.. figure :: http://www.coactivate.org/projects/sauna-sprint-2010/project-home/image.jpeg

*sauna.reload: so that you can finish your Plone development today and relax in sauna after calling it a day*

Introduction
---------------

``sauna.reload`` is an attempt to recreate ``plone.reload`` without the issues it
has. Like being unable to reload new views or portlet code.

``sauna.reload`` does reloading by using a fork loop. So actually it does not
reload the code, but restarts small part of Zope2.

It does following on Zope2 startup:

*  Defers loading of your development packages by hooking into PEP 302 loader
   and changing their z3c.autoinclude target module

*  Starts a watcher thread which monitors changes in your development py-files

*  Stops loading of Zope2 in zope.processlifetime.IProcessStarting event by
   stepping into a infinite loop

*  It forks a new child and lets it pass the loop

*  Installs all your development packages invoking z3c.autoinclude. This is
   fast!

*  And now every time when the watcher thread detects a change in development
   files it will signal the child to shutdown and the child will signal
   the parent to fork new a child when it is just about to close itself.

* GOTO 4

Installing
------------

Add this package to your buildout eggs and add following zope-conf-additional
line and reload_watch_dir environment var to you instance part of buildout.cfg:


::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zope-conf-additional = %import sauna.reload
    environment-vars =
        reload_watch_dir ${buildout:directory}/src



Known issues
----------------

* Currently reloading is limited to z3c.autoincluded Python packages
  and does not cover old style Products.XXX namespaced packages

* The watcher (watchdog) does not compile on OS X Lion 10.7. Snowleopard is fine.

* If there is an start up error you'll get a loop of forever 


TODOs
-----

* Make new instance script that starts plone with the fork loop. Normal fg should not start the fork loop.

* Install dependencies of the development packages before the fork loop. Currently you can do this  manually by listing  them in your buildout.  There is some issues if you don't do it. Under investigation.

* Update *autoincludetools* and *fiveconfiguretools* to use *reload_watch_dir* env 

* Figure out how to detect failed installation of packages in atexit of Zope2 to prevent infinitely spawning fork loop.

* Test it!

* Find out the limitations

* Be able to reload oldschool packages too

* Disable fork loop if debug mode is not on

Authors
---------

* Esa-Matti Suuronen (esa-matti aet suuronen.org)
 
* Asko Soukka (asko.soukka aet iki.fi)

* Mikko Ohtamaa (idea)

* Andreas Jung (approved in IRC)

300 kg of beer was consumed to create this package (at least).
Also several kilos of firewood, one axe, one chainsaw and one boat.



