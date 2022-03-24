#!/usr/bin/env python
# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, WindowProperties
from editorLogHandler import setupLog
from SceneEditor.SceneEditor import SceneEditor

loadPrcFileData(
    "",
    """
    sync-video #t
    textures-power-2 none
    window-title Scene Editor
    maximized #t
    win-size 1280 720
    """)

setupLog("SceneEditor")

base = ShowBase()

def set_dirty_name():
    wp = WindowProperties()
    wp.setTitle("*Scene Editor")
    base.win.requestProperties(wp)

def set_clean_name():
    wp = WindowProperties()
    wp.setTitle("Scene Editor")
    base.win.requestProperties(wp)

base.accept("request_dirty_name", set_dirty_name)
base.accept("request_clean_name", set_clean_name)

SceneEditor(base.pixel2d)

base.run()
