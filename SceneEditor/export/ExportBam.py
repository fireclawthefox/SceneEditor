#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import os
import logging
from panda3d.core import ConfigVariableBool
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectDialog import YesNoDialog
from panda3d.core import LVecBase2f, LVecBase3f, LVecBase4f, LPoint2f, LPoint3f, LPoint4f, LVector3f
from panda3d.core import LVecBase2, LVecBase3, LVecBase4, LPoint2, LPoint3, LPoint4
from panda3d.core import LPlane
from panda3d.core import NodePath
from panda3d.core import Camera, OrthographicLens, PerspectiveLens

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser

class ExporterBam:
    def __init__(self, save_path, save_file, scene_root, scene_objects, tooltip):
        # create a new NP which will be written out to the bam file
        self.export_scene_np = NodePath("export_root")

        # copy the existing scene to our new NP
        scene_root.copy_to(self.export_scene_np)

        # clean up the copied scene from parts it shouldn't export
        self.cleanup_np(self.export_scene_np)

        self.browser = DirectFolderBrowser(
            self.save,
            True,
            save_path,
            save_file,
            [".bam"],
            tooltip,
            askForOverwrite=True,
            title="Export Scene as BAM")
        self.browser.show()

    def cleanup_np(self, root_np):
        if root_np.get_tag("object_type") == "empty":
            # replace the visible axis with an empty NodePath
            name = root_np.get_name()
            pos = root_np.get_pos()
            hpr = root_np.get_hpr()
            parent = root_np.get_parent()

            empty = NodePath(name)
            empty.set_pos(pos)
            empty.set_hpr(hpr)
            empty.reparent_to(parent)

            for child in list(root_np.get_children())[1:]:
                child.reparent_to(empty)

            root_np.remove_node()
            root_np = empty

        elif root_np.get_tag("object_type") == "collision":
            root_np.hide()

        elif root_np.get_tag("object_type") == "light":
            # remove the light representation model
            root_np.get_children()[0].remove_node()

        elif root_np.get_tag("object_type") == "camera":
            # create a camera and remove the dummy camera in the scene
            lens = None
            if root_np.get_tag("camera_type") == "PerspectiveLens":
                lens = PerspectiveLens()
            else:
                lens = OrthographicLens()
            cam = Camera(root_np.get_name(), lens)
            cam_np = root_np.get_parent().attach_new_node(cam)
            root_np.remove_node()
            root_np = cam_np

        for child in root_np.get_children():
            self.cleanup_np(child)

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
        self.export_scene_np.writeBamFile(path)
