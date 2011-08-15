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

from persistent.TimeStamp import TimeStamp

from ZODB.FileStorage.FileStorage import read_index


# TODO: register to ZCA so that ``sauna.reload`` can support also other
# storages than ZODB.
class FileStorageIndex(object):

    def __init__(self, storage):
        # Try to get the *real* FileStorage, because `storage` may be just
        # a BlobStorage-wrapper and it wraps FileStorage differently between
        # ZODB3-3.9.5 and 3.10.x-series (eg. between Plone 4.0 and 4.1).
        self.storage = getattr(storage, "_BlobStorage__storage", storage)

    def save(self):
        # Save ``Data.fs.index`` before dying to notify the next child of the
        # persistent changes.
        self.storage._lock_acquire()
        try:
            self.storage._save_index()
        finally:
            self.storage._lock_release()

    def restore(self):
        self.storage._lock_acquire()
        try:
            # Get indexes in their pre-fork state
            index, tindex = (self.storage._index, self.storage._tindex)
            # Load saved ``Data.fs.index`` to see the persistent changes
            # created by the previous child.
            index, start, ltid =\
                self.storage._restore_index() or (None, None, None)
            # Sanity check. Last transaction in restored index must match
            # the last transaction given by FileStorage transaction iterator.
            if ltid and ltid == tuple(self.storage.iterator())[-1].tid:
                self.storage._initIndex(index, tindex)
                self.storage._pos, self.storage._oid, tid = read_index(
                    self.storage._file, self.storage._file_name, index, tindex,
                    stop="\377" * 8, ltid=ltid, start=start, read_only=False)
                self.storage._ltid = tid
                self.storage._ts = TimeStamp(tid)
        finally:
            self.storage._lock_release()
