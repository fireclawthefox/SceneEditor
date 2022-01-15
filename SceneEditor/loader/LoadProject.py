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

from direct.showbase.DirectObject import DirectObject
from direct.gui import DirectGuiGlobals as DGG

from panda3d.core import TextNode
from panda3d.core import LVecBase2f, LVecBase3f, LVecBase4f, LPoint2f, LPoint3f, LPoint4f
from panda3d.core import LVecBase2, LVecBase3, LVecBase4, LPoint2, LPoint3, LPoint4

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser


class ProjectLoader(DirectObject):
    def __init__(self, load_path, load_file, core, exceptionLoading=False, tooltip=None, newProjectCall=None):
        self.newProjectCall = newProjectCall
        self.hasErrors = False
        self.core = core
        self.objects = []
        if exceptionLoading:
            self.excLoad()
        else:
            self.browser = DirectFolderBrowser(
                self.load,
                True,
                load_path,
                load_file,
                tooltip=tooltip)
            self.browser.show()

    def excLoad(self):
        tmpPath = os.path.join(tempfile.gettempdir(), "SEExceptionSave.json")
        self.__executeLoad(tmpPath)

    def get(self):
        return self.objects

    def load(self, doLoad):
        if doLoad:
            path = self.browser.get()
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)

            if not os.path.exists(path):
                base.messenger.send("showWarning", ["File \"{}\" does not exist.".format(path)])
                return

            if self.newProjectCall():
                self.__executeLoad(path)
            else:
                self.accept("clearDirtyFlag", self.__executeLoad, [path])

        self.browser.destroy()
        del self.browser

    def __executeLoad(self, path):
        fileContent = None
        with open(path, 'r') as infile:
            try:
                fileContent = json.load(infile)
            except Exception as e:
                logging.error("Couldn't load project file {}".format(infile))
                logging.exception(e)
                base.messenger.send("showWarning", ["Error while loading Project!\nPlease check output logs for more information."])
                return
        if fileContent is None:
            logging.error("Problems reading Project file: {}".format(infile))
            return

        if fileContent["ProjectVersion"] != "0":
            logging.warning("Unsupported Project Version")
            base.messenger.send("showWarning", ["Unsupported Project Version"])
            return

        for name, info in fileContent["Scene"].items():
            self.__createElement(name.split("|")[1], info)

        if self.hasErrors:
            base.messenger.send("showWarning", ["Errors occured while loading the project!\nProject may not be fully loaded\nSee output log for more information."])
            return

        base.messenger.send("setLastPath", [path])
        base.messenger.send("update_structure")

    def __createElement(self, name, info):
        # create the element
        model = self.core.load_model(info["filepath"])
        model.set_name(name)
        #TODO: We probably shouldn't use eval here
        model.set_pos(eval(info["pos"]))
        model.set_hpr(eval(info["hpr"]))
        model.set_scale(eval(info["scale"]))
        parent_name = info["parent"]
        if parent_name != "scene_model_parent":
            parents = self.core.models[:]
            for obj in parents.reverse():
                if obj.get_name() == parent_name:
                    model.reparent_to(obj)
                    break
