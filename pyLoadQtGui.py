#!/usr/bin/env python
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
    @version: v0.3
"""

SERVER_VERSION = "0.3"

import sys

from time import sleep, time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from xmlrpclib import ServerProxy

class main(QObject):
    def __init__(self):
        """
            main setup
        """
        QObject.__init__(self)
        self.app = QApplication(sys.argv)
        self.mainWindow = mainWindow()
        self.connector = connector()
        
        self.connector.start()
        sleep(1)
        self.mainWindow.show()
        self.testStuff()
    
    def connectSignals(self):
        """
            signal and slot stuff, yay!
        """
        self.connect(self.connector, SIGNAL("error_box"), self.slotErrorBox)
    
    def loop(self):
        """
            start exec loop
        """
        sys.exit(self.app.exec_())
    
    def slotErrorBox(self, msg):
        """
            display a nice error box
        """
        QMessageBox(QMessageBox.Warning, "Error", msg)
    
    def testStuff(self):
        """
            only for testing ;)
        """
        #test for link collector
        ids = self.connector.getLinkCollector()
        for id in ids:
            data = self.connector.getLinkInfo(id)
            item = QListWidgetItem()
            item.setData(Qt.UserRole, QVariant(data))
            item.setData(Qt.DisplayRole, QVariant(data["url"]))
            self.mainWindow.tabs["collector_links"]["listwidget"].addItem(item)
        
        #test for package collector
        packs = self.connector.getPackageCollector()
        for data in packs:
            item = QTreeWidgetItem()
            item.setData(0, Qt.UserRole, QVariant(data))
            item.setData(0, Qt.DisplayRole, QVariant(data["package_name"]))
            files = self.connector.getPackageFiles(data["id"])
            for id in files:
                info = self.connector.getLinkInfo(id)
                sub = QTreeWidgetItem(item)
                sub.setData(0, Qt.DisplayRole, QVariant(info["filename"]))
            self.mainWindow.tabs["collector_packages"]["treewidget"].addTopLevelItem(item)
        
        #test for queue
        """
        packs = self.connector.getPackageQueue()
        for data in packs:
            item = QTreeWidgetItem()
            item.setData(0, Qt.UserRole, QVariant(data))
            item.setData(0, Qt.DisplayRole, QVariant(data["package_name"]))
            files = self.connector.getPackageFiles(data["id"])
            for id in files:
                info = self.connector.getLinkInfo(id)
                sub = QTreeWidgetItem(item)
                sub.setData(0, Qt.DisplayRole, QVariant(info["filename"]))
                sub.setData(1, Qt.DisplayRole, QVariant(info["status_type"]))
            self.mainWindow.tabs["queue"]["treewidget"].addTopLevelItem(item)
        """
        model = QueueModel(self.connector)
        model.setView(self.mainWindow.tabs["queue"]["view"])
        self.mainWindow.tabs["queue"]["view"].setModel(model)
        self.mainWindow.tabs["queue"]["view"].setup()
        model.startLoop()

class connector(QThread):
    def __init__(self):
        """
            init thread
        """
        QThread.__init__(self)
        self.lock = QMutex()
        self.running = True
        self.proxy = None
    
    def run(self):
        """
            start thread
            (called from thread.start())
        """
        self.connectProxy("http://admin:pwhere@localhost:7227/")    #@TODO: change me!
        while self.running:
            sleep(1)
    
    def stop(self):
        """
            stop thread
        """
        self.running = False
    
    def connectProxy(self, addr):
        """
            connect to remote server
        """
        self.proxy = ServerProxy(addr, allow_none=True)
        server_version = self.proxy.get_server_version()
        if not server_version == SERVER_VERSION:
            self.emit(SIGNAL("error_box"), "server is version %s client accepts version %s" % (server_version, SERVER_VERSION))
    
    def getLinkCollector(self):
        """
            grab links from collector and return the ids
        """
        return self.proxy.get_collector_files()
    
    def getPackageCollector(self):
        """
            grab packages from collector and return the data
        """
        return self.proxy.get_collector_packages()
    
    def getLinkInfo(self, id):
        """
            grab file info for the given id and return it
        """
        return self.proxy.get_file_info(id)
    
    def getPackageInfo(self, id):
        """
            grab package info for the given id and return it
        """
        return self.proxy.get_package_data(id)
    
    def getPackageQueue(self):
        """
            grab queue return the data
        """
        return self.proxy.get_queue()
    
    def getPackageFiles(self, id):
        """
            grab package files and return ids
        """
        return self.proxy.get_package_files(id)
    
    def getDownloadQueue(self):
        """
            grab files that are currently downloading and return info
        """
        return self.proxy.status_downloads()

class mainWindow(QMainWindow):
    def __init__(self):
        """
            set up main window
        """
        QMainWindow.__init__(self)
        #window stuff
        self.setWindowTitle("pyLoad Client")
        self.setWindowIcon(QIcon("icons/logo.png"))
        self.resize(600,500)
        
        #central widget, layout
        self.masterlayout = QVBoxLayout()
        lw = QWidget()
        lw.setLayout(self.masterlayout)
        self.setCentralWidget(lw)
        
        #set menubar and statusbar
        self.menubar = self.menuBar()
        self.statusbar = self.statusBar()
        
        #menu
        self.menus = {}
        self.menus["file"] = self.menubar.addMenu("&File")
        self.menus["connections"] = self.menubar.addMenu("&Connections")
        
        #menu actions
        self.mactions = {}
        self.mactions["exit"] = QAction("Exit", self.menus["file"])
        self.mactions["manager"] = QAction("Connection manager", self.menus["connections"])
        
        #add menu actions
        self.menus["file"].addAction(self.mactions["exit"])
        self.menus["connections"].addAction(self.mactions["manager"])
        
        #tabs
        self.tabw = QTabWidget()
        self.tabs = {}
        self.tabs["queue"] = {"w":QWidget()}
        self.tabs["collector_packages"] = {"w":QWidget()}
        self.tabs["collector_links"] = {"w":QWidget()}
        self.tabw.addTab(self.tabs["queue"]["w"], "Queue")
        self.tabw.addTab(self.tabs["collector_packages"]["w"], "Package collector")
        self.tabw.addTab(self.tabs["collector_links"]["w"], "Link collector")
        
        #init tabs
        self.init_tabs()
        
        #layout
        self.masterlayout.addWidget(self.tabw)
    
    def init_tabs(self):
        """
            create tabs
        """
        #queue
        self.tabs["queue"]["l"] = QGridLayout()
        self.tabs["queue"]["w"].setLayout(self.tabs["queue"]["l"])
        self.tabs["queue"]["view"] = QueueView()
        self.tabs["queue"]["l"].addWidget(self.tabs["queue"]["view"])
        
        #collector_packages
        self.tabs["collector_packages"]["l"] = QGridLayout()
        self.tabs["collector_packages"]["w"].setLayout(self.tabs["collector_packages"]["l"])
        self.tabs["collector_packages"]["treewidget"] = QTreeWidget()
        self.tabs["collector_packages"]["l"].addWidget(self.tabs["collector_packages"]["treewidget"])
        
        #collector_links
        self.tabs["collector_links"]["l"] = QGridLayout()
        self.tabs["collector_links"]["w"].setLayout(self.tabs["collector_links"]["l"])
        self.tabs["collector_links"]["listwidget"] = QListWidget()
        self.tabs["collector_links"]["l"].addWidget(self.tabs["collector_links"]["listwidget"])

class QueueFile():
    def __init__(self, data, pack):
        self.pack = pack
        self.update(data)
    
    def update(self, data):
        self.data = data
    
    def getID(self):
        return self.data["id"]

class QueuePack():
    def __init__(self, data):
        self.data = data
        self.children = []
    
    def update(self, data):
        self.data = data
    
    def addChild(self, NewQFile, model, index):
        for k, QFile in enumerate(self.children):
            if QFile.getID() == NewQFile.getID():
                QFile.update(NewQFile.data)
                #model.emit(SIGNAL("dataChanged(const QModelIndex topLeft, const QModelIndex bottomRight)"), model.index(k, 0, index), model.index(k, 2, index))
                return
        model.beginInsertRows(index, len(self.children), len(self.children)+1)
        self.children.append(NewQFile)
        model.endInsertRows()
    
    def getChildren(self):
        return self.children
    
    def getID(self):
        return self.data["id"]

class QueueModel(QAbstractItemModel):
    def __init__(self, connector):
        QAbstractItemModel.__init__(self)
        self.mutex = QMutex()
        self.mutex.lock()
        self.connector = connector
        self.queue = []
        self.downloading = []
        self.statusMap = {
            "finished":    0,
            "checking":    1,
            "waiting":     2,
            "reconnected": 3,
            "downloading": 4,
            "failed":      5,
            "aborted":     6,
        }
        self.statusMapReverse = dict((v,k) for k, v in self.statusMap.iteritems())
        self.cols = 3
        self.interval = 1
        self.view = None
        self.mutex.unlock()
        self.update()
        self.loop = self.Loop(self)
    
    def setView(self, view):
        self.view = view
    
    def _update(self):
        packs = self.connector.getPackageQueue()
        previous = None
        for data in packs:
            pos = self._inQueue(data["id"])
            if not type(pos) == int:
                pack = QueuePack(data)
            else:
                pack = QueuePack(data)
                self.queue[pos] = pack
            if not type(pos) == int:
                self._insertPack(pack, previous)
            files = self.connector.getPackageFiles(data["id"])
            pos = self._inQueue(data["id"])
            for fid in files:
                info = self.connector.getLinkInfo(fid)
                qFile = QueueFile(info, pack)
                if type(pos) == int:
                    pack.addChild(qFile, self, self.index(pos, 0))
            previous = pack.getID()
    
    def update(self):
        locker = QMutexLocker(self.mutex)
        self._update()
        self.downloading = self.connector.getDownloadQueue()
        #if self.view:
        #    self.view.emit(SIGNAL("update()"))
    
    def startLoop(self):
        self.loop.start()
    
    def _inQueue(self, pid):
        for k, pack in enumerate(self.queue):
            if pack.getID() == pid:
                return k
        return False
    
    def _insertPack(self, newpack, prevID):
        ck = 0
        for k, pack in enumerate(self.queue):
            ck = k
            if pack.getID() == prevID:
                break
        self.beginInsertRows(QModelIndex(),ck+1, ck+2)
        self.queue.insert(ck+1, newpack)
        self.endInsertRows()
    
    def index(self, row, column, parent=QModelIndex()):
        if parent == QModelIndex():
            pointer = self.queue[row]
            index = self.createIndex(row, column, pointer)
        elif parent.isValid():
            q = self.nodeFromIndex(parent)
            pointer = q.getChildren()[row]
            index = self.createIndex(row, column, pointer)
        else:
            index = QModelIndex()
        return index
    
    def nodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return None
    
    def parent(self, index):
        if index == QModelIndex():
            return QModelIndex()
        if index.isValid():
            q = self.nodeFromIndex(index)
            if isinstance(q, QueueFile):
                row = None
                for k, pack in enumerate(self.queue):
                    if pack.getID() == q.pack.getID():
                        row = k
                if row != None:
                    return self.createIndex(row, 0, q.pack)
        return QModelIndex()
    
    def rowCount(self, parent=QModelIndex()):
        if parent == QModelIndex():
            #return package count
            return len(self.queue)
        else:
            if parent.isValid():
                #index is valid
                q = self.nodeFromIndex(parent)
                if isinstance(q, QueuePack):
                    #index points to a package
                    #return len of children
                    return len(q.getChildren())
            else:
                #index is invalid
                return False
        #files have no children
        return 0
    
    def columnCount(self, parent=QModelIndex()):
        return self.cols
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole:
            q = self.nodeFromIndex(index)
            if index.column() == 0:
                if isinstance(q, QueuePack):
                    return QVariant(q.data["package_name"])
                else:
                    return QVariant(q.data["filename"])
            elif index.column() == 1:
                if isinstance(q, QueueFile):
                    return QVariant(q.data["status_type"])
                else:
                    status = 0
                    for child in q.getChildren():
                        if self.statusMap.has_key(child.data["status_type"]) and self.statusMap[child.data["status_type"]] > status:
                            status = self.statusMap[child.data["status_type"]]
                    return QVariant(self.statusMapReverse[status])
        return QVariant()
    
    def hasChildren(self, parent=QModelIndex()):
        if not parent.isValid():
            return True
        return (self.rowCount(parent) > 0)
    
    def canFetchMore(self, parent):
        return False
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return QVariant("Name")
            elif section == 1:
                return QVariant("Status")
            elif section == 2:
                return QVariant("Fortschritt")
        return QVariant()
    
    def getProgress(self, index):
        q = self.nodeFromIndex(index)
        if isinstance(q, QueueFile):
            for d in self.downloading:
                if d["id"] == q.getID():
                    return int(d["percent"])
            if q.data["status_type"] == "finished" or \
                  q.data["status_type"] == "failed" or \
                  q.data["status_type"] == "aborted":
                return 100
        elif isinstance(q, QueuePack):
            children = q.getChildren()
            count = len(children)
            perc_sum = 0
            for child in children:
                val = 0
                for d in self.downloading:
                    if d["id"] == child.getID():
                        val = int(d["percent"])
                        break
                if child.data["status_type"] == "finished" or \
                        child.data["status_type"] == "failed" or \
                        child.data["status_type"] == "aborted":
                    val = 100
                perc_sum += val
            if count == 0:
                return None
            return perc_sum/count
        return None
    
    class Loop(QThread):
        def __init__(self, module):
            QThread.__init__(self)
            self.module = module
            self.running = True
        
        def run(self):
            while self.running:
                sleep(self.module.interval)
                self.module.update()

class QueueView(QTreeView):
    def __init__(self):
        QTreeView.__init__(self)
    
    def setup(self):
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 100)
        delegate = QueueProgressBarDelegate(self)
        self.setItemDelegateForColumn(2, delegate)

class QueueProgressBarDelegate(QItemDelegate):
    def __init__(self, parent):
        QItemDelegate.__init__(self, parent)
    
    def paint(self, painter, option, index):
        if index.column() == 2:
            model = index.model()
            progress = model.getProgress(index)
            if progress == None:
                QItemDelegate.paint(self, painter, option, index)
                return
            opts = QStyleOptionProgressBarV2()
            opts.maximum = 100
            opts.minimum = 0
            opts.progress = progress
            opts.rect = option.rect
            opts.rect.setRight(option.rect.right()-1)
            opts.rect.setHeight(option.rect.height()-1)
            opts.textVisible = True
            opts.textAlignment = Qt.AlignCenter
            opts.text = QString.number(opts.progress) + "%"
            QApplication.style().drawControl(QStyle.CE_ProgressBar, opts, painter)
            return
        QItemDelegate.paint(painter, option, index)

if __name__ == "__main__":
    app = main()
    app.loop()