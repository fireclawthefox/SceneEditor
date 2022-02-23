#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectOptionMenu import DirectOptionMenu
from panda3d.core import (
    LPoint3f,
    LVecBase3f,
    LVecBase4f,
    TextNode
)

class GUI:
    def __init__(self, rootParent=None):

        self.frm_main = DirectFrame(
            borderWidth = (2, 2),
            frameSize = (-250.0, 250.0, -250.0, 250.0),
            frameColor = (1, 1, 1, 1),
            pos = LPoint3f(337.5, 0, -331.5),
            parent=rootParent,
        )
        self.frm_main.setTransparency(0)

        self.lbl_header = DirectLabel(
            borderWidth = (2.0, 2.0),
            frameColor = (0.0, 0.0, 0.0, 1.0),
            pad = (5.0, 5.0),
            pos = LPoint3f(-246, 0, 235),
            text = ['Shader loader'],
            text0_scale = (14.0, 14.0),
            text0_fg = LVecBase4f(1, 1, 1, 1),
            text0_align = 0,
            parent=self.frm_main,
        )
        self.lbl_header.setTransparency(0)

        self.btn_ok = DirectButton(
            relief = 1,
            borderWidth = (2, 2),
            frameSize = (-40.0, 40.0, -6.0, 22.0),
            pos = LPoint3f(112.5, 0, -235),
            text = ['Ok'],
            text0_scale = (24, 24),
            text1_scale = (24, 24),
            text2_scale = (24, 24),
            text3_scale = (24, 24),
            parent=self.frm_main,
            pressEffect=1,
        )
        self.btn_ok.setTransparency(0)

        self.frm_shader_input = DirectScrolledFrame(
            state = 'normal',
            relief = 3,
            frameSize = (-225.0, 225.0, -75.0, 75.0),
            frameColor = (1, 1, 1, 1),
            pos = LPoint3f(0, 0, -120),
            canvasSize = (-213.0, 213.0, -300.0, 300.0),
            scrollBarWidth = 20,
            parent=self.frm_main,
        )
        self.frm_shader_input.setTransparency(0)

        self.btn_add_shader_input = DirectButton(
            relief = 1,
            borderWidth = (2, 2),
            pad = (4.0, 4.0),
            pos = LPoint3f(-216, 0, -213),
            text = ['+'],
            text0_scale = (24, 24),
            text1_scale = (24, 24),
            text2_scale = (24, 24),
            text3_scale = (24, 24),
            parent=self.frm_main,
            pressEffect=1,
        )
        self.btn_add_shader_input.setTransparency(0)

        self.lbl_shader_input = DirectLabel(
            borderWidth = (2, 2),
            frameColor = (0.8, 0.8, 0.8, 0.0),
            pos = LPoint3f(-222.5, 0, -36.5),
            text = ['Shader input'],
            text0_scale = (12.0, 12.0),
            text0_align = 0,
            parent=self.frm_main,
        )
        self.lbl_shader_input.setTransparency(0)

        self.txt_fragment_path = DirectEntry(
            relief = 3,
            borderWidth = (0.08333333333333333, 0.08333333333333333),
            frameColor = (1.0, 1.0, 1.0, 1.0),
            pad = (0.5, 0.5),
            pos = LPoint3f(-154, 0, 4.5),
            scale = LVecBase3f(12, 12, 12),
            width = 25.0,
            overflow = 1,
            parent=self.frm_main,
        )
        self.txt_fragment_path.setTransparency(0)

        self.lbl_frag = DirectLabel(
            borderWidth = (2, 2),
            frameColor = (0.8, 0.8, 0.8, 0.0),
            pos = LPoint3f(-194, 0, 4.5),
            text = ['Fragment'],
            text0_scale = (12.0, 12.0),
            parent=self.frm_main,
        )
        self.lbl_frag.setTransparency(0)

        self.lbl_vertex = DirectLabel(
            borderWidth = (2, 2),
            frameColor = (0.8, 0.8, 0.8, 0.0),
            pos = LPoint3f(-194, 0, 184.5),
            text = ['Vertex'],
            text0_scale = (12.0, 12.0),
            parent=self.frm_main,
        )
        self.lbl_vertex.setTransparency(0)

        self.txt_tessellation_ev_path = DirectEntry(
            relief = 3,
            borderWidth = (0.08333333333333333, 0.08333333333333333),
            frameColor = (1.0, 1.0, 1.0, 1.0),
            pad = (0.5, 0.5),
            pos = LPoint3f(-154, 0, 94.5),
            scale = LVecBase3f(12, 12, 12),
            width = 25.0,
            overflow = 1,
            parent=self.frm_main,
        )
        self.txt_tessellation_ev_path.setTransparency(0)

        self.txt_tessellation_ctrl_path = DirectEntry(
            relief = 3,
            borderWidth = (0.08333333333333333, 0.08333333333333333),
            frameColor = (1.0, 1.0, 1.0, 1.0),
            pad = (0.5, 0.5),
            pos = LPoint3f(-154, 0, 139.5),
            scale = LVecBase3f(12, 12, 12),
            width = 25.0,
            overflow = 1,
            parent=self.frm_main,
        )
        self.txt_tessellation_ctrl_path.setTransparency(0)

        self.txt_vertex_path = DirectEntry(
            relief = 3,
            borderWidth = (0.08333333333333333, 0.08333333333333333),
            frameColor = (1.0, 1.0, 1.0, 1.0),
            pad = (0.5, 0.5),
            pos = LPoint3f(-154, 0, 184.5),
            scale = LVecBase3f(12, 12, 12),
            width = 25.0,
            overflow = 1,
            parent=self.frm_main,
        )
        self.txt_vertex_path.setTransparency(0)

        self.lbl_tessellation_ctrl = DirectLabel(
            borderWidth = (2, 2),
            frameColor = (0.8, 0.8, 0.8, 0.0),
            pos = LPoint3f(-194, 0, 139.5),
            text = ['Tessellation ctrl'],
            text0_scale = (12.0, 12.0),
            parent=self.frm_main,
        )
        self.lbl_tessellation_ctrl.setTransparency(0)

        self.lbl_tessellation_ev = DirectLabel(
            borderWidth = (2, 2),
            frameColor = (0.8, 0.8, 0.8, 0.0),
            pos = LPoint3f(-194, 0, 94.5),
            text = ['Tesselation ev'],
            text0_scale = (12.0, 12.0),
            parent=self.frm_main,
        )
        self.lbl_tessellation_ev.setTransparency(0)

        self.txt_geometry_path = DirectEntry(
            relief = 3,
            borderWidth = (0.08333333333333333, 0.08333333333333333),
            frameColor = (1.0, 1.0, 1.0, 1.0),
            pad = (0.5, 0.5),
            pos = LPoint3f(-154, 0, 49.5),
            scale = LVecBase3f(12, 12, 12),
            width = 25.0,
            overflow = 1,
            parent=self.frm_main,
        )
        self.txt_geometry_path.setTransparency(0)

        self.lbl_geometry = DirectLabel(
            borderWidth = (2, 2),
            frameColor = (0.8, 0.8, 0.8, 0.0),
            pos = LPoint3f(-194, 0, 49.5),
            text = ['Geometry'],
            text0_scale = (12.0, 12.0),
            parent=self.frm_main,
        )
        self.lbl_geometry.setTransparency(0)

        self.btn_browse_vertex = DirectButton(
            relief = 1,
            borderWidth = (2, 2),
            pad = (2.0, 2.0),
            pos = LPoint3f(197.5, 0, 180.5),
            text = ['browse'],
            text0_scale = (24, 24),
            text1_scale = (24, 24),
            text2_scale = (24, 24),
            text3_scale = (24, 24),
            parent=self.frm_main,
            pressEffect=1,
            command='base.messenger.send',
            extraArgs=[],
        )
        self.btn_browse_vertex.setTransparency(0)

        self.btn_browse_tessellation_ctrl = DirectButton(
            relief = 1,
            borderWidth = (2, 2),
            pad = (2.0, 2.0),
            pos = LPoint3f(197.5, 0, 135.5),
            text = ['browse'],
            text0_scale = (24, 24),
            text1_scale = (24, 24),
            text2_scale = (24, 24),
            text3_scale = (24, 24),
            parent=self.frm_main,
            pressEffect=1,
            command='',
            extraArgs=[],
        )
        self.btn_browse_tessellation_ctrl.setTransparency(0)

        self.btn_browse_tessellation_eval = DirectButton(
            relief = 1,
            borderWidth = (2, 2),
            pad = (2.0, 2.0),
            pos = LPoint3f(197.5, 0, 90.5),
            text = ['browse'],
            text0_scale = (24, 24),
            text1_scale = (24, 24),
            text2_scale = (24, 24),
            text3_scale = (24, 24),
            parent=self.frm_main,
            pressEffect=1,
            extraArgs=[],
            command='',
        )
        self.btn_browse_tessellation_eval.setTransparency(0)

        self.btn_browse_geometry = DirectButton(
            relief = 1,
            borderWidth = (2, 2),
            pad = (2.0, 2.0),
            pos = LPoint3f(197.5, 0, 45.5),
            text = ['browse'],
            text0_scale = (24, 24),
            text1_scale = (24, 24),
            text2_scale = (24, 24),
            text3_scale = (24, 24),
            parent=self.frm_main,
            pressEffect=1,
            command='',
            extraArgs=[],
        )
        self.btn_browse_geometry.setTransparency(0)

        self.btn_browse_fragment = DirectButton(
            relief = 1,
            borderWidth = (2, 2),
            pad = (2.0, 2.0),
            pos = LPoint3f(197.5, 0, 0.5),
            text = ['browse'],
            text0_scale = (24, 24),
            text1_scale = (24, 24),
            text2_scale = (24, 24),
            text3_scale = (24, 24),
            parent=self.frm_main,
            pressEffect=1,
            command='',
            extraArgs=[],
        )
        self.btn_browse_fragment.setTransparency(0)

        self.cmb_shader_input_type = DirectOptionMenu(
            relief = 1,
            borderWidth = (2, 2),
            borderUvWidth = (0.0, 0.1),
            pos = LPoint3f(-202.5, 0, -211),
            scale = LVecBase3f(12, 12, 12),
            text = 'Texture',
            items = ['Texture', 'Nodepath', 'Vector'],
            popupMarker_pos = None,
            text_align = 0,
            parent=self.frm_main,
        )
        self.cmb_shader_input_type.setTransparency(0)

        self.btn_cancel = DirectButton(
            relief = 1,
            borderWidth = (2, 2),
            frameSize = (-40.0, 40.0, -6.0, 22.0),
            pos = LPoint3f(202.5, 0, -234.5),
            text = ['Cancel'],
            text0_scale = (24, 24),
            text1_scale = (24, 24),
            text2_scale = (24, 24),
            text3_scale = (24, 24),
            parent=self.frm_main,
            pressEffect=1,
        )
        self.btn_cancel.setTransparency(0)


    def show(self):
        self.frm_main.show()

    def hide(self):
        self.frm_main.hide()

    def destroy(self):
        self.frm_main.destroy()
