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
from ZODB.POSException import ConflictError

from zope.site.hooks import setSite
from zope.interface import Interface, implements
from zope.component import getUtilitiesFor

from Products.CMFCore.interfaces import ISiteRoot


class IProfileAutoImport(Interface):
    """``sauna.reload`` GenericSetup profile auto import utility"""

    def autoImport(profile):
        """Look up for Plone sites from Zope root and import all steps from
        "profile" GenericSetups profile"""
        pass


class ProfileAutoImport(object):
    """``sauna.reload`` GenericSetup profile auto import utility"""

    implements(IProfileAutoImport)

    def autoImport(self, profile):
        from Zope2.App.startup import app
        for site in (o for o in app().values() if ISiteRoot.providedBy(o)):
            portal_setup = getattr(site, "portal_setup", None)
            if site and portal_setup:
                setSite(site)
                portal_setup.runAllImportStepsFromProfile(profile)


def autoImportProfiles(event=None):
    registrations = getUtilitiesFor(IProfileAutoImport)
    for registration in registrations:
        utility = registration[1]
        profile = registration[0]
        try:
            utility.autoImport(profile)
        except ConflictError:
            raise
        finally:
            commit()
