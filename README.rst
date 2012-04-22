.. figure:: https://github.com/collective/sauna.reload/raw/gh-pages/saunasprint_logo.jpg

*sauna.reload: so that you can finish your Plone development today and relax in
sauna after calling it a day*

.. contents:: :local:


Introduction
============

``sauna.reload`` partially restarts Plone and reloads your changed source
code every time you save a file.

* Edit your code
* Save
* Go to a browser and hit *Refresh* |->| your latest changes are active

It greatly simplifies your Plone development workflow and gives back the
agility of Python.

It works with any code.

``sauna.reload`` works on OSX and Linux with Plone 4.0 and 4.1. In theory
works on Windows, but no one has looked into that yet.

.. |->| unicode:: U+02794 .. thick rightwards arrow


User comments
-------------

"I don't want to use sauna.reload as I can knit a row while I restart ..."

"no more do I start a 5 minute cigarette every time Plone restarts for 30
seconds... ok wait, this kind of joy leads to poetry, I'm gonna stop here."


Installation
============

Here are brief installation instructions.


Prerequisitements
-----------------

In order to take the advantage of ``sauna.reload``

* You know how to develop your own Plone add-ons and basics of buildout folder
  structure

* You know UNIX command line basics

* You know how to run buildout

No knowledge for warming up sauna is needed in order to use this product.


Using new buildout file for the development
-------------------------------------------

This is the recommended approach how to enable ``sauna.reload`` for your
development environment.

Use git to fetch  ``sauna.reload`` source code to your buildout environment::

  cd src
  git clone git://github.com/collective/sauna.reload.git

Create a new buildout file ``development.cfg`` which extends your existing
``buildout.cfg`` – this way you can easily keep development stuff separate
from your main buildout.cfg which you can also use on the production server.

``development.cfg``::

  [buildout]

  extends = buildout.cfg

  develop +=
      src/sauna.reload

  [instance]

  # XXX: May conflict with existing zope-conf-additional directives
  zope-conf-additional = %import sauna.reload

  eggs +=
      sauna.reload

.. note:: With this approach you do not need to modify the existing
   buildout.cfg.

Then build it out with this special config file::

  bin/buildout -c development.cfg

*I like to buildout buildout. I like to buildout buildout...*


OSX special notes
+++++++++++++++++

If you are using vim (or macvim) on OSX, you must disable vim's writebackups
to allow WatchDog to see your modifications
(otherwise vim will technicallyj create a new file on each save and WatchDog
doesn't report the modification back to ``sauna.reload``).

So, Add the following to the end of your ``.vimrc``::

  set noswapfile
  set nobackup
  set nowritebackup

Similar issues have been reported with some other OSX-editors.
Tips and fixes for these are welcome.


Ubuntu/Debian/Linux special notes
+++++++++++++++++++++++++++++++++++

You might need to raise your open files *ulimit* if you are operating on the
large set of files, both hard and soft limit.

* http://posidev.com/blog/2009/06/04/set-ulimit-parameters-on-ubuntu/

104000 is a known good value.

If your *ulimit* is too low you'll get very misleading *OSError: No space left
on device*.


Updating the existing buildout.cfg
----------------------------------

Alternatively you can just hack your existing buildout.cfg to have
``sauna.reload``.

Add this package to your buildout eggs and add following
``zope-conf-additional`` line  to you instance part of buildout.cfg::

  [instance]
  recipe = plone.recipe.zope2instance
  ...
  zope-conf-additional = %import sauna.reload


Usage: start Plone in reload enabled manner
===========================================

To start Plone with reload functionality you need
to give special environment variable ``RELOAD_PATH``
for your instance command::

  RELOAD_PATH=src bin/instance fg

Or if you want to optimize load speed you can directly specify only some of
your development products::

  RELOAD_PATH=src/my.product:src/my.another.product bin/instance fg

.. warning:: If other products depend on your product, e.g CMFPlone
   dependencies, sauna.reload does not kick in early enough and the reload does
   not work.

When reload is active you should see something like this in your console
when Zope starts up::

  2011-08-10 13:28:59 INFO sauna.reload Starting file monitor on /Users/moo/code/x/plone4/src
  2011-08-10 13:29:02 INFO sauna.reload We saved at least 29.8229699135 seconds from boot up time
  2011-08-10 13:29:02 INFO sauna.reload Overview available at: http://127.0.0.1:8080/@@saunareload
  2011-08-10 13:29:02 INFO sauna.reload Fork loop starting on process 14607
  2011-08-10 13:29:02 INFO sauna.reload Booted up new new child in 0.104816913605 seconds. Pid 14608

... and when you save some file in ``src`` folder::

  2011-08-10 13:29:41 INFO SignalHandler Caught signal SIGINT
  2011-08-10 13:29:41 INFO Z2 Shutting down
  2011-08-10 13:29:42 INFO SignalHandler Caught signal SIGCHLD
  2011-08-10 13:29:42 INFO sauna.reload Booted up new new child in 0.123936891556 seconds. Pid 14609

CTRL+C should terminate Zope normally. There might be stil some kinks and error
messages with shutdown.

.. note:: Your reloadable eggs must be included using z3c.autoinclude
   mechanism.

Only eggs loaded through `z3c.autoinclude
<http://plone.org/products/plone/roadmap/247>`_ can be reloaded.
Make sure you don't use buildout.cfg ``zcml =`` directive for your eggs or
``sauna.reload`` silently ignores changes.


Manual reload
-------------

There is also a view on Zope2 root from which it is possible to manually reload
code::

  http://127.0.0.1:8080/@@saunareload


Debugging with ``sauna.reload``
===============================

Regular ``import pdb; pdb.set_trace()`` will work just fine with
``sauna.reload``
and using ``ipdb`` as a drop-in for ``pdb`` will work fine as well.
When reloads happen while in either pdb or ipdb, the debugger will get
killed.
To avoid losing your terminal echo, because of reload unexpectedly
killing your debugger, you may add the following to your ``~/.pdbrc``::

  import termios, sys
  term_fd = sys.stdin.fileno()
  term_echo = termios.tcgetattr(term_fd)
  term_echo[3] = term_echo[3] | termios.ECHO
  term_result = termios.tcsetattr(term_fd, termios.TCSADRAIN, term_echo)

As ipdb extends pdb, this configuration file will also work to restore the
terminal echo.

``sauna.reload`` also should work nicely with `PdbTextMateSupport
<http://pypi.python.org/pypi/PdbTextMateSupport>`_ and `PdbSublimeTextSupport
<http://pypi.python.org/pypi/PdbSublimeTextSupport>`_. Unfortunately, we
haven't seen it working with ``vimpdb`` yet.


Background
==========

``sauna.reload`` is an attempt to recreate ``plone.reload`` without the issues
it has. Like being unable to reload new grokked views or portlet code. This
project was started on Plone Sauna Sprint 2011. There for the name,
``sauna.reload``.

``sauna.reload`` does reloading by using a fork loop. So actually it does not
reload the code, but restarts small part of Zope2. That's why it can it reload
stuff ``plone.reload`` cannot.

It does following on Zope2 startup:

1. Defers loading of your development packages by hooking into PEP 302 loader
   and changing their ``z3c.autoinclude`` target module (and monkeypatching
   fiveconfigure/metaconfigure for legacy packages).

2. Starts a watcher thread which monitors changes in your development py-files

3. Stops loading of Zope2 in ``zope.processlifetime.IProcessStarting`` event by
   stepping into a infinite loop; Just before this, tries to load all
   non-developed dependencies of your development packages (resolved by
   ``z3c.autoinclude``)

4. It forks a new child and lets it pass the loop

5. Loads all your development packages invoking ``z3c.autoinclude`` (and
   fiveconfigure/metaconfigure for legacy packages). This is fast!

6. And now every time when the watcher thread detects a change in development
   files it will signal the child to shutdown and the child will signal
   the parent to fork a new child when it is just about to close itself

7. Just before dying, the child saves ``Data.fs.index`` to help the new child
   to see the changes in ZODB (by loading the saved index)

8. GOTO 4

Internally ``sauna.reload`` uses
`WatchDog <http://pypi.python.org/pypi/watchdog>`_
Python component for monitoring file-system change events.

See also `Ruby guys on fork trick <http://www.youtube.com/watch?feature=player_detailpage&v=ghLCtCwAKqQ#t=286s>`_.


Events
======

.. note:: The following concerns you only if your code needs to react specially
   to reloads (clear caches, etc.)

``sauna.reload`` emits couple of events during reloading.

**sauna.reload.events.INewChildForked**
  Emited immediately after new process is forked. No development packages have
  been yet installed.  Useful if you want to do something before your code gets
  loaded.  Note that you cannot listen this event on a package that is marked
  for reloading as it is not yet installed when this is fired.

**sauna.reload.events.INewChildIsReady**
  Emitted when all the development packages has been installed to the new
  forked child.  Useful for notifications etc.


Limitations
===========

``sauna.reload`` has a major pitfall. Because it depends on deferring loading
of packages to be watched and reloaded, also every package depending on those
packages should be defined to be reloaded (in ``RELOAD_PATH``). And
``sauna.reload`` doesn't resolve those dependencies automatically!

An another potential troublemaker is that ``sauna.reload`` performs implicit
``<includeDependencies package="." />`` for every package in ``RELOAD_PATH``
(to preload dependencies for those packages to speed up the reload).

We are sorry that ``sauna.reload`` may not work for everyone. For example,
reloading of core Plone packages could be tricky, if not impossible, because
many of them are explicitly included by ``configure.zcml`` of CMFPlone and are
not using ``z3c.autoinclude`` at all. You would have to remove the dependency
from CMFPlone for development to make it work...

Also because the product installation order is altered (by all the above) you
may find some issue if your product does something funky on installation or at
import time.

Please report any other issues at:
https://github.com/collective/sauna.reload/issues.


Troubleshooting
===============

Report all issues on `GitHub <https://github.com/collective/sauna.reload>`_.


My code does not reload properly
--------------------------------

You'll see reload process going on in the terminal, but your code is still not
loaded.

You should see following warnings with zcml-paths from your products::

  2011-08-13 09:38:12 ERROR sauna.reload.child Cannot reload
  src/sauna.reload/sauna/reload/configure.zcml.

Make sure your code is hooked into Plone through
`z3c.autoinclude <http://plone.org/products/plone/roadmap/247>`_ and NOT
using explicit ``zcml = directive`` in buildout.cfg.

* Retrofit your eggs with autoinclude support if needed
* Remove zcml = lines for your eggs in buildout.cfg
* Rerun buildout (remember bin/buildout -c development.cfg)
* Restart Plone with sauna.reload enabled


I want to exclude my ``meta.zcml`` from reload
----------------------------------------------

It's possible to manually exclude configuration files from reloading by forcing
them to be loaded before forkloop in a custom ``site.zcml``. Be aware, that
when ``site-zcml`` option is used, ``zope2instance`` ignores ``zcml`` and
``zcml-additional`` options.

Define a custom ``site.zcml`` in your ``buildout.cfg`` with::

  [instance]
  recipe = plone.recipe.zope2instance
  ...
  site-zcml =
    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:meta="http://namespaces.zope.org/meta"
               xmlns:five="http://namespaces.zope.org/five">
      <include package="Products.Five" />
      <meta:redefinePermission from="zope2.Public" to="zope.Public" />
      <five:loadProducts file="meta.zcml"/>

      <!-- Add include for your package's meta.zcml here: -->
      <include package="my.product" file="meta.zcml" />

      <five:loadProducts />
      <five:loadProductsOverrides />
      <securityPolicy component="Products.Five.security.FiveSecurityPolicy" />
    </configure>


I want to exclude ALL ``meta.zcml`` from reload
-----------------------------------------------

Sure. See the tip above and use the snippet below instead::

  [instance]
  recipe = plone.recipe.zope2instance
  ...
  site-zcml =
    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:meta="http://namespaces.zope.org/meta"
               xmlns:five="http://namespaces.zope.org/five">
      <include package="Products.Five" />
      <meta:redefinePermission from="zope2.Public" to="zope.Public" />
      <five:loadProducts file="meta.zcml"/>

      <!-- Add autoinclude-directive for deferred meta.zcml here: -->
      <includePlugins package="sauna.reload" file="meta.zcml" />

      <five:loadProducts />
      <five:loadProductsOverrides />
      <securityPolicy component="Products.Five.security.FiveSecurityPolicy" />
    </configure>


sauna.reload is not active - nothing printed on console
-------------------------------------------------------

Check that your buildout.cfg includes
``zope-conf-additionalzope-conf-additional`` line.

If using separate ``development.cfg`` make sure you run your buildout using
it::

  bin/buildout -c development.cfg


Source
======

On `GitHub <https://github.com/collective/sauna.reload>`_.


Credits
=======

* Esa-Matti Suuronen [esa-matti aet suuronen.org]
* Asko Soukka [asko.soukka aet iki.fi]
* Mikko Ohtamaa (idea, doccing)
* Vilmos Somogyi (logo). The logo was originally the logo of Sauna Sprint 2011
  and it was created by Vilmos Somogyi.
* Martijn Pieters for teaching us PEP 302 -loader trick at Sauna Sprint 2011.
* `Yesudeep Mangalapilly <https://github.com/gorakhargosh>`_ for creating
  ``WatchDog`` component and providing support for Sauna Sprint team using it

Thanks to all happy hackers on Sauna Sprint 2011!

300 kg of beer was consumed to create this package (at least). Also several
kilos of firewood, one axe, one chainsaw and one boat.

We still need testers and contributors. You are very welcome!
