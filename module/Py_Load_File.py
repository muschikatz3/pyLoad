#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from download_thread import Status

class PyLoadFile:
    """ represents the url or file
    """
    def __init__(self, parent, url):
        self.parent = parent
        self.id = None
        self.url = url
        self.filename = "filename"
        self.download_folder = ""
        self.modul = __import__(self._get_my_plugin())
        pluginClass = getattr(self.modul, self.modul.__name__)
        self.plugin = pluginClass(self)
        self.status = Status(self)

    def _get_my_plugin(self):
        """ searches the right plugin for an url
        """
        for plugin, plugin_pattern in self.parent.plugins_avaible.items():
            if re.match(plugin_pattern, self.url) != None:
                return plugin

        return "Plugin"

    def init_download(self):

        if self.parent.config['proxy']['activated']:
            self.plugin.req.add_proxy(self.parent.config['proxy']['protocol'], self.parent.config['proxy']['adress'])

        #@todo: check dependicies, ocr etc

