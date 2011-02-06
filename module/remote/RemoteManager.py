# -*- coding: utf-8 -*-
"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.

    @author: mkaay
"""

from threading import Thread
from traceback import print_exc

class BackendBase(Thread):
    def __init__(self, manager):
        Thread.__init__(self)
        self.manager = manager
        self.core = manager.core
    
    def run(self):
        self.core.log.info(_("Starting %s") % self.__class__.__name__)
        try:
            self.serve()
        except:
            self.core.log.error(_("%s: Remote backend error") % self.__class__.__name__)
            if self.core.debug:
                print_exc()
    
    def setup(self):
        pass
    
    def checkDeps(self):
        return True
    
    def serve(self):
        pass
    
    def checkAuth(self, user, password, remoteip=None):
        return self.manager.checkAuth(user, password, remoteip)

class RemoteManager():
    available = ("XMLRPCBackend", "ThriftBackend")
    
    def __init__(self, core):
        self.core = core
        self.backends = []
    
    def startBackends(self):
        for b in self.available:
            klass = getattr(__import__("module.remote.%s" % b, globals(), locals(), [b] , -1), b)
            backend = klass(self)
            if not backend.checkDeps():
                continue
            try:
                backend.setup()
            except:
                self.core.log.error(_("Failed loading backend %s") % b)
                if self.core.debug:
                    print_exc()
            else:
                backend.start()
                self.backends.append(backend)
    def checkAuth(self, user, password, remoteip=None):
        if self.core.config["remote"]["nolocalauth"] and remoteip == "127.0.0.1":
            return True
        return self.core.db.checkAuth(user, password)
