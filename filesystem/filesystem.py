"""A simple filesystem implemetation.

Focus on path parsing, error handling, good design.
"""
import collection
import enum

class Node:

    def __init__(self, name, parent, is_directory=False):
        self.name = name
        self.parent = parent
        self.is_directory = is_directory

    def isDirectory(self):
        return self.is_directory


class File(Node):

    def __init__(self, name, parent, data):
        super().__init__(name, parent)
        self.data = data
        self.size = len(data)

    def read(self):
        return self.data

    def seek(self, offset):
        if offset > self.size:
            raise ValueError(f'file {self.name} is smaller than {offset}')
        return self.data[offset:]


class Directory(Node):

    def __init__(self, name, parent=None):
        super().__init__(name, parent, True)

        if parent is None:
            # this is the root, set the parent to itself.
            parent = self

        self.entries = {
            ".": self,
            "..": parent,
        }

    def getChild(self, name):
        if name not in self.entries:
            raise ValueError(f"Path {name} doesn't exist.")
        return self.entries[name]

    def addFile(self, name, data):
        if name in self.entries:
            raise ValueError(f"Path {name} already exists.")
        self.entries[name] = File(name, self, data)

    def addSubdirectory(self, name):
        if name in self.entries:
            raise ValueError(f"Path {name} already exists.")
        self.entries[name] = Directory(name, self)

    def ls(self):
        return self.entries.keys()


class FileSystem:

    def __init__(self):
        self.root = Directory('/')
        self.cwd = self.root

    DIVISOR = '/'

    @staticmethod
    def _splitPath(path):
        p = path.removesuffix(FileSystem.DIVISOR)
        res = p.split(FileSystem.DIVISOR)
        return res

    def _walkPath(self, path):
        if not path:
            raise ValueError(f"Empty path {path}")
        components = FileSystem._splitPath(path)

        base = self.cwd
        if components and len(components[0]) == 0:
            base = self.root
            components.pop(0)

        for c in components:
            if not c: continue
            base = base.getChild(c)

        if not base.isDirectory():
            return ValueError(f"{path} is not directory.")

        return base

    def _dirname(self, path):
        components = self._splitPath(path)
        if not components:
            return self.cwd, ""

        new = components[-1]
        if new in ('.', '..'):
            raise ValueError(f"Cannot create a directory with name {new}")

        base = None
        if len(components) == 1 and not path.startswith(FileSystem.DIVISOR):
            base = self.cwd
        else:
            prefix = FileSystem.DIVISOR.join(components[:-1])
            if path.startswith(FileSystem.DIVISOR) and not prefix.startswith(FileSystem.DIVISOR):
                prefix = FileSystem.DIVISOR + prefix
            base = self._walkPath(prefix)

        if not base.isDirectory():
            raise ValueError(f"Path {base} is not a directory.")
        return base, new
    
    def cd(self, path):
        self.cwd = self._walkPath(path)

    def makePath(self, directory):
        base, new = self._dirname(directory)
        base.addSubdirectory(new)
        
    def ls(self, path = '.'):
        d = self._walkPath(path)
        if not d.isDirectory():
            return [d.name]
        return d.ls()

    def createFile(self, path, content):
        base, new = self._dirname(path)
        base.addFile(new, content)

    def readFromFile(self, path):
        base, new = self._dirname(path)
        f = base.getChild(new)
        if f.isDirectory():
            raise ValueError(f'{path} is a directory not a file.')
        return f.data

    def seek(self, path, offset):
        base, new = self._dirname(path)
        f = base.getChild(new)
        if f.isDirectory():
            raise ValueError(f'{path} is a directory not a file.')
        return f.seek(offset)
    
