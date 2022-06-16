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
from panda3d.core import LVecBase2f, LVecBase3f, LVecBase4f, LPoint2f, LPoint3f, LPoint4f, LVector3f
from panda3d.core import LVecBase2i
from panda3d.core import LVecBase2, LVecBase3, LVecBase4, LPoint2, LPoint3, LPoint4
from panda3d.core import LVector2f
from panda3d.core import LPlane

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser

from SceneEditor.GUI.panels.ObjectPropertiesDefinition import DEFINITIONS, PropertyEditTypes
from SceneEditor.GUI.panels.PropertiesPanel import PropertyHelper


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
        object_type = info["object_type"]

        definitions = {}

        if object_type == "model":
            # create the element
            model = self.core.load_model(info["filepath"])
            if "transparency" in info:
                model.set_transparency(eval(info["transparency"]))
            definitions = DEFINITIONS[object_type]
        elif object_type == "empty":
            # create the element
            model = self.core.add_empty()
            definitions = DEFINITIONS[object_type]
        elif object_type == "collision":
            # create the element
            model = self.core.add_collision_solid(
                info["collision_solid_type"],
                eval(info["collision_solid_info"]))
            definitions = DEFINITIONS[info["collision_solid_type"]]
        elif object_type == "physics":
            model = self.core.add_physics_node()
            definitions = DEFINITIONS[object_type]
        elif object_type == "light":
            # create the element
            model = self.core.add_light(
                info["light_type"],
                {})
            definitions = DEFINITIONS[info["light_type"]]
        elif object_type == "camera":
            # create the element
            model = self.core.add_camera(
                info["camera_type"],
                {})
            definitions = DEFINITIONS[info["camera_type"]]
        self.set_nodepath_values(model, name, info, definitions)

    def set_nodepath_values(self, model, name, info, definitions):
        model.set_name(name)

        edit_list = []
        for definition in definitions:
            if definition.internalName not in info:
                continue

            edit_list.append(definition.internalName)

            if definition.editType != PropertyEditTypes.text:
                #TODO: We probably shouldn't use eval here
                value = eval(info[definition.internalName])
                PropertyHelper.setValue(definition, model, value)
            else:
                value = info[definition.internalName]
                PropertyHelper.setValue(definition, model, value)

        model.set_tag("edited_properties", ",".join(edit_list))

        parent_name = info["parent"]
        if parent_name != "scene_model_parent":
            parents = self.core.scene_objects[:]
            for obj in parents.reverse():
                if obj.get_name() == parent_name:
                    model.reparent_to(obj)
                    break

