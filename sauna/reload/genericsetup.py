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

from Zope2.App.startup import app

from zope.site.hooks import setSite
from zope.interface import Interface, implements
from zope.component import getUtilitiesFor


class IProfileAutoImport(Interface):
    """ """
    def autoimport(sitename, profilename):
        pass


class ProfileAutoImport(object):
    """ """
    implements(IProfileAutoImport)

    def autoimport(self, sitename, profilename):
       site = getattr(app(), sitename, None)
       portal_setup = getattr(site, "portal_setup", None)
       if site and portal_setup:
           setSite(site)
           portal_setup.runAllImportStepsFromProfile(profilename)


def importGSProfiles(event):
    registrations = getUtilitiesFor(IProfileAutoImport)
    for registration in registrations:
        sitename, profilename = registration[0].split(";")
        utility = registration[1]
        utility.autoimport(sitename, profilename)
