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

"""Database Adapters"""

from persistent.TimeStamp import TimeStamp

from zope.interface import implements
from zope.component import adapts

from ZODB.interfaces import IDatabase
from ZODB.blob import BlobStorage
from ZODB.FileStorage.FileStorage import FileStorage, read_index
from ZEO.ClientStorage import ClientStorage

from sauna.reload.interfaces import IDatabaseHooks


class ZODBDatabaseHooksAdapter(object):
    """
    Selective ZODB-adapter (e.g. supporting both FileStorage and ZEO)
    """
    implements(IDatabaseHooks)
    adapts(IDatabase)

    def __init__(self, context):
        self.context = context
        self.adapter = IDatabaseHooks(context.storage)

    def prepareForReload(self):
        return self.adapter.prepareForReload()

    def resumeFromReload(self):
        return self.adapter.resumeFromReload()


class ZODBFileStorageDatabaseHooksAdapter(object):
    """
    FileStorage-adapter
    """
    implements(IDatabaseHooks)
    adapts(FileStorage)

    def __init__(self, context):
        self.context = context

    def prepareForReload(self):
        # Save ``Data.fs.index`` before dying
        # to notify the next child
        # about all the presistent changes
        self.context._lock_acquire()
        try:
            self.context._save_index()
        finally:
            self.context._lock_release()

    def resumeFromReload(self):
        # Reload ``Data.fs.index``
        # to get up to date
        # about all the persistent changes
        self.context._lock_acquire()
        try:
            # Get indexes in their pre-fork state
            index, tindex = (self.context._index, self.context._tindex)
            # Load saved ``Data.fs.index`` to see the persistent changes
            # created by the previous child.
            index, start, ltid =\
                self.context._restore_index() or (None, None, None)
            # Sanity check. Last transaction in restored index must match
            # the last transaction given by FileStorage transaction iterator.
            if ltid and ltid == tuple(self.context.iterator())[-1].tid:
                self.context._initIndex(index, tindex)
                self.context._pos, self.context._oid, tid = read_index(
                    self.context._file, self.context._file_name, index, tindex,
                    stop='\377' * 8, ltid=ltid, start=start, read_only=False)
                self.context._ltid = tid
                self.context._ts = TimeStamp(tid)
        finally:
            self.context._lock_release()


class ZODBBlobStorageDatabaseHooksAdapter(ZODBFileStorageDatabaseHooksAdapter):
    """
    BlogStorage-proxied FileStorage-adapter
    """
    implements(IDatabaseHooks)
    adapts(BlobStorage)

    def __init__(self, context):
        # Try to get the *real* FileStorage,
        # because `context` may be just a BlobStorage-wrapper
        # and it wraps FileStorage differently between
        # ZODB3-3.9.5 and 3.10.x-series (eg. between Plone 4.0 and 4.1).
        self.context = getattr(context, '_BlobStorage__storage', context)


class ZEOClientStorageDatabaseHooksAdapter(object):
    """
    ZEO-client adapter
    """
    implements(IDatabaseHooks)
    adapts(ClientStorage)

    def __init__(self, context):
        self.context = context

        # Store cache settings
        self._cache_path = self.context._cache.path
        self._cache_size = self.context._cache.maxsize

        # Close the main process' connection (before forkloop)
        _rpc_mgr = self.context._rpc_mgr
        _rpc_mgr.close()

        # Close the main process' cache (before forkloop)
        self.context._cache.close()

    def prepareForReload(self):
        # Close the connection (before the child is killed)
        _rpc_mgr = self.context._rpc_mgr
        _rpc_mgr.close()
        # Close the cache (before the child is killed)
        self.context._cache.close()

    def resumeFromReload(self):
        # Open a new cache for the new child
        self.context._cache = self.context.ClientCacheClass(
            self._cache_path, size=self._cache_size)

        # Prepare a new connection for the new child
        self.context._rpc_mgr = self.context.ConnectionManagerClass(
            self.context._addr, self.context, tmin=1, tmax=30)

        # Connect the new child to ZEO
        self.context._rpc_mgr.attempt_connect()
        if not self.context._rpc_mgr.attempt_connect():
            self.context._rpc_mgr.connect()
