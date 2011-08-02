# -*- coding: utf-8 -*-
# Copyright (c) 2011 University of Jyväskylä
#
# Authors:
#     Esa-Matti Suuronen <esa-matti@suuronen.org>
#     Asko Soukka <asko.soukka@iki.fi>
#
# This file is part of sauna.reload.
#
# sauna.reload is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# sauna.reload is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with sauna.reload.  If not, see <http://www.gnu.org/licenses/>.

import time

from sauna.reload import forkloop
from sauna.reload.autoincludetools import get_deferred_deps
from sauna.reload.watcher import Watcher
from sauna.reload import reload_paths


def startForkLoop(event):

    if not reload_paths.isActive():
        print
        print "No paths in RELOAD_PATH environment variable. Not starting fork loop."
        print "Set it to your development egg paths to activete reloading"
        print
        print "Example: RELOAD_PATH=src bin/instance fg"
        print
        return


    # Start fs monitor before the forkloop
    Watcher(reload_paths.getParentPaths(), forkloop).start()

    # Build and execute a configuration file to include meta, configuration and
    # overrides for dependencies of the deferred development packages.
    deps = get_deferred_deps()
    config = u"""\
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:zcml="http://namespaces.zope.org/zcml">

    """ + u"".join([u"""<include
        zcml:condition="not-have disable-autoinclude"
        package="%s"
        file="meta.zcml"
        />""" % name for name in deps.get("meta.zcml", ())]) + """

    """ + u"".join([u"""<include
        zcml:condition="not-have disable-autoinclude"
        package="%s"
        file="configure.zcml"
        />""" % name for name in deps.get("configure.zcml", ())]) + """

    """ + u"".join([u"""<includeOverrides
        zcml:condition="not-have disable-autoinclude"
        package="%s"
        file="overrides.zcml"
        />""" % name for name in deps.get("overrides.zcml", ())]) + """

</configure>"""
    from Products.Five.zcml import load_string
    load_string(config)

    print "We saved at least %s seconds from boot up time" % (time.time() - forkloop.boot_started)
    forkloop.start()

