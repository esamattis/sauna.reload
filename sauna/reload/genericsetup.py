# -*- coding: utf-8 -*-
# Copyright (c) 2011 University of Jyväskylä and Contributors.
#
# All Rights Reserved.
#
# Authors:
#     Esa-Matti Suuronen <esa-matti@suuronen.org>
#     Asko Soukka <asko.soukka@iki.fi>
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS

from transaction import commit
from Zope2.App.startup import app
from ZODB.POSException import ConflictError

from zope.site.hooks import setSite
from zope.interface import Interface, implements
from zope.component import getUtilitiesFor


class IProfileAutoImport(Interface):
    """``sauna.reload`` GenericSetup profile auto import utility"""

    def autoimport(sitename, profilename):
        """Look up for "sitename" Plone site from
        Zope root and import all steps "profilename"
        GenericSetups profile"""
        pass


class ProfileAutoImport(object):
    """``sauna.reload`` GenericSetup profile auto import utility"""

    implements(IProfileAutoImport)

    def autoimport(self, sitename, profilename):
        site = getattr(app(), sitename, None)
        portal_setup = getattr(site, "portal_setup", None)
        if site and portal_setup:
            setSite(site)
            import pdb; pdb.set_trace()
            portal_setup.runAllImportStepsFromProfile(profilename)


def autoImportProfiles(event=None):
    registrations = getUtilitiesFor(IProfileAutoImport)
    try:
        for registration in registrations:
            utility = registration[1]
            try:
                sitename, profilename = registration[0].split(";")
            except ValueError:
                sitename = u"plone"
                profilename = registration[0]
            utility.autoimport(sitename, profilename)
    except ConflictError:
        raise
    finally:
        commit()
