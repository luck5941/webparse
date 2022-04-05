#!/usr/bin/env python
import sys
import os

class UserDirs:
    def __init__(self, appname, version):
        self.system = sys.platform
        self.appname = appname
        self.version = version

    def join(func): # pylint: disable=no-self-argument
        def wrapper(self, *args, **kargs):
            path = func(self, *args, **kargs) # pylint: disable=not-callable
            return os.path.join(path, self.appname, self.version)
        return wrapper


    @property
    @join
    def userdatadir(self):
        if self.system == "win32":
            path = os.path.normalpath(os.environ("CSIDL_LOCAL_APPDATA"))
        elif self.system == "darwin":
            path = os.path.expanduser("~/Library/Application Support/")
        else:
            path = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        return path

    @property
    @join
    def userconfigdir(self):
        if self.system == "win32":
            path = self.userdatadir
        elif self.system == "darwin":
            path = os.path.expanduser("/Library/Preferences")
        else:
            path = os.path.expanduser("~/.config")
        return path

    @property
    def usercachedir(self):
        if self.system == "wind32":
            path = os.path.join(self.userdatadir, "Cache")
            return path
        return self.usercachedirnix()

    @join
    def usercachedirnix(self):
        if self.system == "darwin":
            path = os.path.expanduser("~/Library/Caches")
        else:
            path = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
        return path
