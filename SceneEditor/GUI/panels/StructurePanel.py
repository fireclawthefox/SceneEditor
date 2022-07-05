#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

from panda3d.core import VBase4, TextNode, Point3, TransparencyAttrib

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectCheckBox import DirectCheckBox

from DirectGuiExtension import DirectGuiHelper as DGH
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer

class StructurePanel():
    def __init__(self, parent):
        height = DGH.getRealHeight(parent)
        self.collapsedElements = []

        self.parent = parent

        self.object_list = []

        self.box = DirectBoxSizer(
            frameColor=(0.25, 0.25, 0.25, 1),
            autoUpdateFrameSize=False,
            orientation=DGG.VERTICAL)
        self.sizer = DirectAutoSizer(
            updateOnWindowResize=False,
            parent=parent,
            child=self.box,
            childUpdateSizeFunc=self.box.refresh)

        self.lblHeader = DirectLabel(
            text="Structure",
            text_scale=16,
            text_align=TextNode.ALeft,
            text_fg=(1,1,1,1),
            frameColor=VBase4(0, 0, 0, 0),
            )
        self.box.addItem(self.lblHeader)

        color = (
            (0.8, 0.8, 0.8, 1), # Normal
            (0.9, 0.9, 1, 1), # Click
            (0.8, 0.8, 1, 1), # Hover
            (0.5, 0.5, 0.5, 1)) # Disabled
        self.structureFrame = DirectScrolledFrame(
            # make the frame fit into our background frame
            frameSize=VBase4(
                self.parent["frameSize"][0], self.parent["frameSize"][1],
                self.parent["frameSize"][2]+DGH.getRealHeight(self.lblHeader), self.parent["frameSize"][3]),
            #canvasSize=VBase4(parent["frameSize"][0], parent["frameSize"][1]-20, height+30, 0),
            # set the frames color to transparent
            frameColor=VBase4(1, 1, 1, 1),
            scrollBarWidth=20,
            verticalScroll_scrollSize=20,
            verticalScroll_thumb_relief=DGG.FLAT,
            verticalScroll_incButton_relief=DGG.FLAT,
            verticalScroll_decButton_relief=DGG.FLAT,
            verticalScroll_thumb_frameColor=color,
            verticalScroll_incButton_frameColor=color,
            verticalScroll_decButton_frameColor=color,
            horizontalScroll_thumb_relief=DGG.FLAT,
            horizontalScroll_incButton_relief=DGG.FLAT,
            horizontalScroll_decButton_relief=DGG.FLAT,
            horizontalScroll_thumb_frameColor=color,
            horizontalScroll_incButton_frameColor=color,
            horizontalScroll_decButton_frameColor=color,
            state=DGG.NORMAL)
        self.box.addItem(self.structureFrame)
        self.structureFrame.bind(DGG.MWDOWN, self.scroll, [0.01])
        self.structureFrame.bind(DGG.MWUP, self.scroll, [-0.01])
        self.maxWidth = parent["frameSize"][1]-20

        self.skipped_nodes = ["DirectGrid", "selection_highlight_marker", "show_collisions", "Pivot Point"]

    def scroll(self, scrollStep, event):
        self.structureFrame.verticalScroll.scrollStep(scrollStep)

    def recalcScrollSize(self):
        a = self.structureFrame["canvasSize"][2]
        b = abs(self.structureFrame["frameSize"][2]) + self.structureFrame["frameSize"][3]
        scrollDefault = 200
        s = -(scrollDefault / (a / b))

        self.structureFrame["verticalScroll_scrollSize"] = s
        self.structureFrame["verticalScroll_pageSize"] = s


    def resizeFrame(self):
        preSize = self.sizer["frameSize"]
        self.sizer.refresh()
        postSize = self.sizer["frameSize"]

        if preSize != postSize:
            self.structureFrame["frameSize"] = (
                    self.parent["frameSize"][0], self.parent["frameSize"][1],
                    self.parent["frameSize"][2]+DGH.getRealHeight(self.lblHeader), self.parent["frameSize"][3])

            self.recalcScrollSize()

    def refreshStructureTree(self, objects, selected_objects):
        self.objects = objects
        self.selected_objects = selected_objects

        # cleanup the structure tree
        for element in self.structureFrame.getCanvas().getChildren():
            element.removeNode()

        self.maxWidth = self.parent["frameSize"][1]-20
        self.itemCounter = 1

        # create the tree
        self.__fill_structure_tree(render, 0, -16)

        self.structureFrame["canvasSize"] = (
            self.structureFrame["frameSize"][0], self.maxWidth,
            self.itemCounter*-16, 0)
        self.structureFrame.setCanvasSize()
        self.recalcScrollSize()

    def __fill_structure_tree(self, root, level, z):
        if root.getName() in self.skipped_nodes: return

        #if level > 0:
        scene_roots = ["scene_root", "scene_model_parent"]
        if root.get_name() not in scene_roots and root.get_name() != "":
            self.itemCounter += 1
            self.__make_structure_frame_tree_item(root, level, z)
        if hasattr(root, "getChildren") \
        and root not in self.collapsedElements:
            for child in root.getChildren():
                if not child.is_stashed():
                    z=-16*self.itemCounter
                    self.__fill_structure_tree(child, level+1, z)

    def __make_structure_frame_tree_item(self, obj, parents_level, z):
        parent_shift = 10
        margin = 5
        shift = 6
        self.object_list.append(obj)
        if not obj.has_tag("scene_object_id"):
            if hasattr(obj, "getChildren") and obj.getNumChildren() > 0:
                is_good = False
                for child in obj.getChildren():
                    if child.get_name() != "":
                        is_good = True
                        break
                if is_good:
                    # Collapse Button
                    btnC = DirectCheckBox(
                        relief=DGG.FLAT,
                        pos=(self.structureFrame["frameSize"][0] + parent_shift*parents_level - 16 + margin, 0, z+shift),
                        frameSize=(-8, 8, -8, 8),
                        frameColor=(0,0,0,0),
                        command=self.__collapse_element,
                        extraArgs=[obj],
                        image="icons/Collapsed.png" if obj in self.collapsedElements else "icons/Collapse.png",
                        uncheckedImage="icons/Collapse.png",
                        checkedImage="icons/Collapsed.png",
                        image_scale=8,
                        isChecked=obj in self.collapsedElements,
                        parent=self.structureFrame.getCanvas())
                    btnC.setTransparency(TransparencyAttrib.M_alpha)
                    btnC.bind(DGG.MWDOWN, self.scroll, [0.01])
                    btnC.bind(DGG.MWUP, self.scroll, [-0.01])

            lbl = DirectLabel(
                text=obj.getName(),
                text_align=TextNode.ALeft,
                frameColor=(0,0,0,0),
                relief=DGG.FLAT,
                pos=(self.structureFrame["frameSize"][0] + parent_shift*parents_level, 0, z),
                scale=16,
                parent=self.structureFrame.getCanvas())
            self.maxWidth = max(self.maxWidth, lbl.getX() + lbl.getWidth()*lbl.getScale()[0])
        else:

            if hasattr(obj, "getChildren") and obj.getNumChildren() > 0:
                # Collapse Button
                btnC = DirectCheckBox(
                    relief=DGG.FLAT,
                    pos=(self.structureFrame["frameSize"][0] + parent_shift*parents_level - 16 + margin, 0, z+shift),
                    frameSize=(-8, 8, -8, 8),
                    frameColor=(0,0,0,0),
                    command=self.__collapse_element,
                    extraArgs=[obj],
                    image="icons/Collapsed.png" if obj in self.collapsedElements else "icons/Collapse.png",
                    uncheckedImage="icons/Collapse.png",
                    checkedImage="icons/Collapsed.png",
                    image_scale=8,
                    isChecked=obj in self.collapsedElements,
                    parent=self.structureFrame.getCanvas())
                btnC.setTransparency(TransparencyAttrib.M_alpha)
                btnC.bind(DGG.MWDOWN, self.scroll, [0.01])
                btnC.bind(DGG.MWUP, self.scroll, [-0.01])

            # Element Name
            btn = DirectButton(
                frameColor=(VBase4(1,1,1,1), #normal
                    VBase4(0.9,0.9,0.9,1), #click
                    VBase4(0.8,0.8,0.8,1), #hover
                    VBase4(0.5,0.5,0.5,1)), #disabled
                text=f"{obj.name} | sort: {obj.get_sort()}",
                text_align=TextNode.ALeft,
                relief=DGG.FLAT,
                pos=(self.structureFrame["frameSize"][0] + parent_shift*parents_level, 0, z),
                scale=16,
                command=self.__select_element,
                extraArgs=[obj],
                parent=self.structureFrame.getCanvas())
            btn.bind(DGG.MWDOWN, self.scroll, [0.01])
            btn.bind(DGG.MWUP, self.scroll, [-0.01])

            if obj in self.selected_objects:
                btn.setColorScale(1,1,0,1)

            x = self.structureFrame["frameSize"][0] + 8 + margin + parent_shift*parents_level + btn.getWidth()*btn.getScale()[0]
            # Delete Button
            btnX = DirectButton(
                relief=DGG.FLAT,
                pos=(x, 0, z+shift),
                frameSize=(-8, 8, -8, 8),
                frameColor=(0,0,0,0),
                command=self.__remove_element,
                extraArgs=[obj],
                image="icons/DeleteSmall.png",
                image_scale=8,
                parent=self.structureFrame.getCanvas())
            btnX.setTransparency(TransparencyAttrib.M_multisample)
            btnX.bind(DGG.MWDOWN, self.scroll, [0.01])
            btnX.bind(DGG.MWUP, self.scroll, [-0.01])

            x += margin + btnX.getWidth()
            # Visibility Button
            btnV = DirectCheckBox(
                relief=DGG.FLAT,
                pos=(x, 0, z+shift),
                frameSize=(-8, 8, -8, 8),
                frameColor=(0,0,0,0),
                command=self.__toggle_element_visibility,
                extraArgs=[obj],
                image="icons/VisibilityOffSmall.png" if obj.isHidden() else "icons/VisibilityOnSmall.png",
                uncheckedImage="icons/VisibilityOffSmall.png",
                checkedImage="icons/VisibilityOnSmall.png",
                image_scale=8,
                isChecked=not obj.isHidden(),
                parent=self.structureFrame.getCanvas())
            btnV.setTransparency(TransparencyAttrib.M_multisample)
            btnV.bind(DGG.MWDOWN, self.scroll, [0.01])
            btnV.bind(DGG.MWUP, self.scroll, [-0.01])
            self.maxWidth = max(self.maxWidth, btnV.getX() + 8)

            x += margin + btnV.getWidth()
            # Move Up Button
            btnUp = DirectButton(
                relief=DGG.FLAT,
                pos=(x, 0, z+shift),
                frameSize=(-8, 8, -8, 8),
                frameColor=(0,0,0,0),
                command=self.__move_element_in_structure,
                extraArgs=[-1, obj],
                image="icons/ArrowUpSmall.png",
                image_scale=8,
                parent=self.structureFrame.getCanvas())
            btnUp.setTransparency(TransparencyAttrib.M_multisample)
            btnUp.bind(DGG.MWDOWN, self.scroll, [0.01])
            btnUp.bind(DGG.MWUP, self.scroll, [-0.01])

            x += margin + btnUp.getWidth()
            # Move Down Button
            btnDown = DirectButton(
                relief=DGG.FLAT,
                pos=(x, 0, z+shift),
                frameSize=(-8, 8, -8, 8),
                frameColor=(0,0,0,0),
                command=self.__move_element_in_structure,
                extraArgs=[1, obj],
                image="icons/ArrowDownSmall.png",
                image_scale=8,
                parent=self.structureFrame.getCanvas())
            btnDown.setTransparency(TransparencyAttrib.M_multisample)
            btnDown.bind(DGG.MWDOWN, self.scroll, [0.01])
            btnDown.bind(DGG.MWUP, self.scroll, [-0.01])

    def __select_element(self, obj, args=None):
        if obj is not None:
            base.messenger.send("selectElement", [obj, base.mouseWatcherNode.isButtonDown("shift")])

    def __remove_element(self, obj):
        if obj is not None:
            base.messenger.send("removeElement", [[obj]])

    def __toggle_element_visibility(self, toggle, obj):
        if obj is not None:
            base.messenger.send("toggleElementVisibility", [[obj]])

    def __move_element_in_structure(self, direction, obj):
        if obj is not None:
            base.messenger.send("moveElementInStructure", [direction, [obj]])

    def __collapse_element(self, collapse, obj, update_tree=True):
        if obj is not None:
            if collapse:
                if obj not in self.collapsedElements:
                    self.collapsedElements.append(obj)
            else:
                if obj in self.collapsedElements:
                    self.collapsedElements.remove(obj)
            if update_tree:
                base.messenger.send("update_structure")

    def collapse_all(self):
        self.collapsedElements = []
        scene_roots = ["scene_root", "scene_model_parent", "render"]
        for obj in self.object_list:
            if obj.get_name() in scene_roots or obj.get_name() == "":
                continue
            self.__collapse_element(True, obj, False)
        base.messenger.send("update_structure")
