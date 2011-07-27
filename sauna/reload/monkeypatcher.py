import imp
import os
from pkgutil import ImpLoader

class PatchLoader(ImpLoader):
    """Lucky for us ZConfig will use PEP 302 module hooks to load this file,
    and this class implements a get_data hook to intercept the component.xml
    loading and give us a point to generate it."""

    def __init__(self, module):
        name = module.__name__
        path = os.path.dirname(module.__file__)
        description = ("", "", imp.PKG_DIRECTORY)
        ImpLoader.__init__(self, name, None, path, description)

    def get_data(self, pathname):
        if os.path.split(pathname) == (self.filename, "component.xml"):
            # apply our patch and return dummy config to keep zope happy
            # TODO: insert monkeypatch here
            return u"<component></component>"
        return ImpLoader.get_data(self, pathname)