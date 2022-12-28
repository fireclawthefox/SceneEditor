#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import json
import logging
import tempfile

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectDialog import YesNoDialog

from SceneEditor.tools.JSONTools import JSONTools

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser

class ExporterProject:
    def __init__(self, save_path, save_file, scene_root, scene_objects, exceptionSave=False, autosave=False, tooltip=None):
        self.objects = scene_objects
        self.scene_root = scene_root
        self.isAutosave = False

        if exceptionSave:
            self.excSave()
            return

        if autosave:
            self.isAutosave = True
            self.autoSave(os.path.join(save_path, save_file))
            return


        self.browser = DirectFolderBrowser(
            self.save,
            True,
            save_path,
            save_file,
            tooltip=tooltip,
            askForOverwrite=True,
            title="Save Scene")
        self.browser.show()

    def excSave(self):
        tmpPath = os.path.join(tempfile.gettempdir(), "SEExceptionSave.scene")
        self.__executeSave(tmpPath)
        logging.info("Wrote crash session file to {}".format(tmpPath))

    def autoSave(self, fileName=""):
        if fileName == "":
            fileName = os.path.join(tempfile.gettempdir(), "SEAutosave.scene")
        self.__executeSave(fileName)
        logging.info("Wrote autosave file to {}".format(fileName))

    def save(self, doSave):
        if doSave:
            path = self.browser.get()
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)
            self.__executeSave(path)
            base.messenger.send("setLastPath", [path])
        self.browser.destroy()
        del self.browser

    def __executeSave(self, path):
        jsonTools = JSONTools()
        jsonElements = jsonTools.getProjectJSON(self.objects, self.scene_root)
        with open(path, 'w') as outfile:
            json.dump(jsonElements, outfile, indent=2)

        if not self.isAutosave:
            base.messenger.send("clearDirtyFlag")

