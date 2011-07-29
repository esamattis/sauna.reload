
import time

from sauna.reload import forkloop
from sauna.reload.autoincludetools import get_deferred_deps

def startForkLoop(event):
    # Build and execute a configuration file to include meta,
    # configuration and overrides for dependencies of the deferred
    # development packages.
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

