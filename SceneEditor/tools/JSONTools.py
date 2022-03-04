#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import logging

from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import NodePath

from SceneEditor.GUI.panels.ObjectPropertiesDefinition import DEFINITIONS
from SceneEditor.GUI.panels.PropertiesPanel import PropertyHelper

class JSONTools:
    def getProjectJSON(self, scene_objects, scene_root):
        self.scene_objects = scene_objects
        jsonElements = {}
        jsonElements["ProjectVersion"] = "0"
        jsonElements["Scene"] = {}

        self.writtenRoots = []

        index = 0
        for child in scene_root.get_children():
            if child in self.scene_objects:
                if not child.is_stashed():
                    index += 1
                    jsonElements["Scene"][f"{index}|{child.get_name()}"] = self.__createJSONEntry(child)

        return jsonElements

    def __createJSONEntry(self, scene_object):
        object_type = scene_object.get_tag("object_type")

        object_dict = {
            "object_type":object_type,
            "parent":scene_object.parent.get_name()
        }

        definition_object_type = object_type
        if object_type == "light":
            #
            # LIGHT
            #
            definition_object_type = scene_object.get_tag("light_type")

            # additional specific properties not given in the definition
            object_dict["light_type"] = scene_object.get_tag("light_type")

        elif object_type == "collision":
            #
            # COLLISION
            #
            definition_object_type = scene_object.get_tag("collision_solid_type")

            # additional specific properties not given in the definition
            object_dict["collision_solid_type"] = scene_object.get_tag("collision_solid_type")
            object_dict["collision_solid_info"] = scene_object.get_tag("collision_solid_info")

        elif object_type == "camera":
            #
            # CAMERA
            #
            definition_object_type = scene_object.get_tag("camera_type")

            # additional specific properties not given in the definition
            object_dict["camera_type"] = scene_object.get_tag("camera_type")

        # get edited property names
        edit_list = []
        if scene_object.has_tag("edited_properties"):
            edit_list = scene_object.get_tag("edited_properties").split(",")

        # add all edited properties
        for definition in DEFINITIONS[definition_object_type]:
            if definition.internalName in edit_list:
                object_dict[definition.internalName] = str(PropertyHelper.getValues(definition, scene_object))

        return object_dict
