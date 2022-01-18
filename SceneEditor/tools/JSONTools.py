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
        if object_type == "model":
            return {
                "object_type":object_type,
                "filepath":scene_object.get_tag("filepath"),
                "pos":str(scene_object.get_pos()),
                "hpr":str(scene_object.get_hpr()),
                "scale":str(scene_object.get_scale()),
                "parent":scene_object.parent.get_name(),
            }
        elif object_type == "collision":
            return {
                "object_type":object_type,
                "collision_solid_type":scene_object.get_tag("collision_solid_type"),
                "pos":str(scene_object.get_pos()),
                "hpr":str(scene_object.get_hpr()),
                "scale":str(scene_object.get_scale()),
                "parent":scene_object.parent.get_name(),
            }
