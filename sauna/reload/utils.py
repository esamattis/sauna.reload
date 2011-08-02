

class ReloadPaths(object):

    def __init__(self, paths):
        self.paths = paths

    def isActive(self):
        return len(self.paths) > 0

    def has(self, test_path):
        for path in self.paths:
            if path == "":
                continue

            if test_path.startswith(path):
                return True
        return False


    def getParentPaths(self):
        parents = []

        parent = None

        for path in sorted(self.paths):

            if parent is None:
                parent = path
                continue

            if path.startswith(parent):
                continue
            else:
                parents.append(parent)
                parent = path

        if parent not in parents:
            parents.append(parent)

        return parents



if __name__ == '__main__':
    paths = [
        "/foo/bar",
        "/newparent",
        "/foo",
        "/foo/child",
        "/another/one",
    ]
    rp = ReloadPaths(paths)
    print list(rp.getParentPaths())
