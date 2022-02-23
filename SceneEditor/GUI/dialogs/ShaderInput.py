#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectOptionMenu import DirectOptionMenu
from panda3d.core import (
    LPoint3f,
    LVecBase3f,
    LVecBase4f,
    TextNode
)

class GUI:
    def __init__(self, rootParent=None):

        self.frm_content = DirectFrame(
            borderWidth = (2, 2),
            frameSize = (0.0, 426.0, -24.0, 0.0),
            frameColor = (1, 1, 1, 1),
            pos = LPoint3f(0, 0, 0),
            parent=rootParent,
        )
        self.frm_content.setTransparency(0)

        self.txt_input_name = DirectEntry(
            borderWidth = (0.08333333333333333, 0.08333333333333333),
            pos = LPoint3f(7.5, 0, -16.5),
            scale = LVecBase3f(12, 12, 12),
            text = [''],
            width = 7.0,
            overflow = 1,
            text0_scale = (1, 1),
            parent=self.frm_content,
            initialText='Input name',
        )
        self.txt_input_name.setTransparency(0)

        self.frm_texture = DirectFrame(
            relief = 3,
            borderWidth = (1.0, 1.0),
            frameSize = (0.0, 300.0, -24.0, 0.0),
            frameColor = (1.0, 1.0, 1.0, 1.0),
            pos = LPoint3f(99.5, 0, 0),
            parent=self.frm_content,
        )
        self.frm_texture.setTransparency(0)

        self.txt_texture_path = DirectEntry(
            borderWidth = (0.08333333333333333, 0.08333333333333333),
            pos = LPoint3f(5.5, 0, -16.5),
            scale = LVecBase3f(12, 12, 12),
            width = 19.5,
            overflow = 1,
            parent=self.frm_texture,
        )
        self.txt_texture_path.setTransparency(0)

        self.btn_browse = DirectButton(
            relief = 1,
            borderWidth = (2, 2),
            pad = (5.0, 5.0),
            pos = LPoint3f(268.5, 0, -16),
            text = ['browse'],
            text0_scale = (12.0, 12.0),
            text1_scale = (12.0, 12.0),
            text2_scale = (12.0, 12.0),
            text3_scale = (12.0, 12.0),
            parent=self.frm_texture,
            pressEffect=1,
        )
        self.btn_browse.setTransparency(0)

        self.btn_remove = DirectButton(
            relief = 1,
            borderWidth = (2, 2),
            pad = (3.0, 1.0),
            pos = LPoint3f(411, 0, -19.5),
            text = ['X'],
            text0_scale = (24, 24),
            text1_scale = (24, 24),
            text2_scale = (24, 24),
            text3_scale = (24, 24),
            parent=self.frm_content,
            pressEffect=1,
        )
        self.btn_remove.setTransparency(0)

        self.frm_nodepath = DirectFrame(
            relief = 3,
            borderWidth = (1.0, 1.0),
            frameSize = (0.0, 300.0, -24.0, 0.0),
            frameColor = (1.0, 1.0, 1.0, 1.0),
            pos = LPoint3f(99.5, 0, 0),
            parent=self.frm_content,
        )
        self.frm_nodepath.setTransparency(0)

        self.cmb_nodepaths = DirectOptionMenu(
            #relief = 1,
            borderWidth = (0.2, 0.2),
            pad = (0.2, 0.2),
            pos = LPoint3f(5, 0, -15.5),
            hpr = LVecBase3f(0, 0, 0),
            scale = LVecBase3f(12, 12, 12),
            #popupMarker_pos = None,
            #text_align = 0,
            parent=self.frm_nodepath,
        )
        self.cmb_nodepaths.setTransparency(0)

        self.frm_vector = DirectFrame(
            relief = 3,
            borderWidth = (1.0, 1.0),
            frameSize = (0.0, 300.0, -24.0, 0.0),
            frameColor = (1.0, 1.0, 1.0, 1.0),
            pos = LPoint3f(99.5, 0, 0),
            parent=self.frm_content,
        )
        self.frm_vector.setTransparency(0)

        self.txt_vec_1 = DirectEntry(
            borderWidth = (0.08333333333333333, 0.08333333333333333),
            pos = LPoint3f(12.5, 0, -16.5),
            scale = LVecBase3f(12, 12, 12),
            width = 5.0,
            overflow = 1,
            parent=self.frm_vector,
        )
        self.txt_vec_1.setTransparency(0)

        self.txt_vec_2 = DirectEntry(
            borderWidth = (0.08333333333333333, 0.08333333333333333),
            pos = LPoint3f(82.5, 0, -16.5),
            scale = LVecBase3f(12, 12, 12),
            width = 5.0,
            overflow = 1,
            parent=self.frm_vector,
        )
        self.txt_vec_2.setTransparency(0)

        self.txt_vec_3 = DirectEntry(
            borderWidth = (0.08333333333333333, 0.08333333333333333),
            pos = LPoint3f(152.5, 0, -16.5),
            scale = LVecBase3f(12, 12, 12),
            width = 5.0,
            overflow = 1,
            parent=self.frm_vector,
        )
        self.txt_vec_3.setTransparency(0)

        self.txt_vec_4 = DirectEntry(
            borderWidth = (0.08333333333333333, 0.08333333333333333),
            pos = LPoint3f(222.5, 0, -16.5),
            scale = LVecBase3f(12, 12, 12),
            width = 5.0,
            overflow = 1,
            parent=self.frm_vector,
        )
        self.txt_vec_4.setTransparency(0)


    def show(self):
        self.frm_content.show()

    def hide(self):
        self.frm_content.hide()

    def destroy(self):
        self.frm_content.destroy()
