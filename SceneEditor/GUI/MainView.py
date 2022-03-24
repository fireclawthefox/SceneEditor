import logging

from panda3d.core import NodePath

from direct.showbase.DirectObject import DirectObject

from direct.gui import DirectGuiGlobals as DGG

from DirectGuiExtension import DirectGuiHelper as DGH

from DirectGuiExtension.DirectTooltip import DirectTooltip

from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer
from DirectGuiExtension.DirectSplitFrame import DirectSplitFrame

from SceneEditor.GUI.MenuBar import MenuBar
from SceneEditor.GUI.ToolBar import ToolBar
from SceneEditor.GUI.panels.PropertiesPanel import PropertiesPanel
from SceneEditor.GUI.panels.StructurePanel import StructurePanel
from SceneEditor.GUI.dialogs.ShaderLoaderDialogManager import ShaderLoaderDialogManager


class MainView(DirectObject):
    def __init__(self, tooltip, grid, core, parent):
        logging.debug("Setup GUI")

        self.parent = parent
        self.core = core

        splitterWidth = 8
        self.menuBarHeight = 24
        self.toolBarHeight = 48

        #
        # LAYOUT SETUP
        #

        # the box everything get's added to
        self.mainBox = DirectBoxSizer(
            frameColor=(0,0,0,0),
            state=DGG.DISABLED,
            orientation=DGG.VERTICAL,
            autoUpdateFrameSize=False)

        # our root element for the main box
        self.mainSizer = DirectAutoSizer(
            frameColor=(0,0,0,0),
            parent=parent,
            child=self.mainBox,
            childUpdateSizeFunc=self.mainBox.refresh
            )

        # our menu bar
        self.menuBarSizer = DirectAutoSizer(
            updateOnWindowResize=False,
            frameColor=(0,0,0,0),
            parent=self.mainBox,
            extendVertical=False)

        # our tool bar
        self.toolBarSizer = DirectAutoSizer(
            updateOnWindowResize=False,
            frameColor=(0,0,0,0),
            parent=self.mainBox,
            extendVertical=False)

        # the splitter separating the the panels from the main content area
        splitterPos = 0
        if type(self.parent) is NodePath:
            splitterPos = -base.get_size()[0] / 4
        else:
            splitterPos = -parent["frameSize"][1] / 4

        self.mainSplitter = DirectSplitFrame(
            frameSize=self.get_main_splitter_size(),
            splitterWidth=splitterWidth,
            splitterPos=splitterPos)
        self.mainSplitter["frameColor"] = (0,0,0,0)
        self.mainSplitter.firstFrame["frameColor"] = (0,0,0,0)
        self.mainSplitter.secondFrame["frameColor"] = (0,0,0,0)

        # The sizer which makes sure our splitter is filling up
        self.mainSplitSizer = DirectAutoSizer(
            updateOnWindowResize=False,
            frameColor=(0,0,0,0),
            parent=self.mainBox,
            child=self.mainSplitter,
            parentGetSizeFunction=self.get_main_splitter_size,
            childUpdateSizeFunc=self.mainSplitter.refresh,
            )

        # The splitter dividing the sidebar on the left
        self.sidebarSplitter = DirectSplitFrame(
            orientation=DGG.VERTICAL,
            frameSize=self.mainSplitter.firstFrame["frameSize"],
            splitterWidth=splitterWidth,
            splitterPos=DGH.getRealHeight(self.mainSplitter.firstFrame) / 2,
            pixel2d=True)

        # The sizer which makes sure our sidebar is filling up
        self.sidebarSplitSizer = DirectAutoSizer(
            updateOnWindowResize=False,
            frameColor=(0,0,0,0),
            parent=self.mainSplitter.firstFrame,
            child=self.sidebarSplitter,
            childUpdateSizeFunc=self.sidebarSplitter.refresh,
            )

        # CONNECT THE UI ELEMENTS
        self.mainBox.addItem(
            self.menuBarSizer,
            updateFunc=self.menuBarSizer.refresh,
            skipRefresh=True)
        self.mainBox.addItem(
            self.toolBarSizer,
            updateFunc=self.toolBarSizer.refresh,
            skipRefresh=True)
        self.mainBox.addItem(
            self.mainSplitSizer,
            updateFunc=self.mainSplitSizer.refresh,
            skipRefresh=True)

        #
        # CONTENT SETUP
        #
        self.menuBar = MenuBar()
        self.menuBarSizer.setChild(self.menuBar.menuBar)
        self.menuBarSizer["childUpdateSizeFunc"] = self.menuBar.menuBar.refresh

        self.tool_bar = ToolBar(tooltip, grid)
        self.toolBarSizer.setChild(self.tool_bar.toolBar)
        self.toolBarSizer["childUpdateSizeFunc"] = self.tool_bar.toolBar.refresh

        self.propertiesPanel = PropertiesPanel(self.sidebarSplitter.firstFrame, tooltip)
        self.sidebarSplitter["firstFrameUpdateSizeFunc"] = self.propertiesPanel.resizeFrame

        self.structurePanel = StructurePanel(self.sidebarSplitter.secondFrame)
        self.sidebarSplitter["secondFrameUpdateSizeFunc"] = self.structurePanel.resizeFrame

        self.mainSplitter["firstFrameUpdateSizeFunc"] = self.sidebarSplitSizer.refresh
        self.mainSplitter["secondFrameUpdateSizeFunc"] = self.update_3d_display_region

        self.accept("show_load_shader_dialog", self.show_load_shader_dialog)

        self.mainBox.refresh()

    def update_3d_display_region(self):
        dr = base.cam.node().get_display_region(0)

        # get the size of the frame the display region should be fit into
        size = [0,1,-1,0]
        if type(self.parent) is NodePath:
            #TODO: Get the size of the actual nodepath
            # currently we expect the nodepath to be pixel2d
            size = [0, base.get_size()[0], -base.get_size()[1], 0]
        else:
            size = self.parent["frameSize"]

        # store the display resolution
        dw = base.get_size()[0]
        dh = base.get_size()[1]

        # store the frame size
        fw = size[1]
        fh = -size[2]

        # calculate the shift from top and left
        top_height = (self.menuBarHeight + self.toolBarHeight) / dh
        left_frame_width = DGH.getRealWidth(self.mainSplitter.firstFrame) / dw

        # get the frames position according to pixel2d
        pos = self.parent.getPos(base.pixel2d)

        # calculate the left and right values for the display region
        left_x = (pos.x / dw) + left_frame_width
        right_x = (pos.x / dw) + (fw / dw)

        # calculate the bottom and top values for the display region
        bottom_y = -(pos.z / dh)
        top_y = -(pos.z / dh) + (fh / dh) - top_height

        # update the display region with the new values
        dr.dimensions = (
            left_x, right_x,
            bottom_y, top_y)

        # calculate width and height for the aspect ratio calculation
        w = 1
        h = 1
        if type(self.parent) is NodePath:
            w = (1-left_frame_width) * dw
            h = (1-top_height) * dh
        else:
            w = (right_x - left_x) * dw
            h = (top_y - bottom_y) * dh

        # update the aspect ratio
        base.camLens.setAspectRatio(w/h)

        base.messenger.send("3d_display_region_changed")

    def get_main_splitter_size(self):
        size = [0,1,1,0]
        if type(self.parent) is NodePath:
            width = base.get_size()[0]
            height = base.get_size()[1]
        else:
            width = DGH.getRealWidth(self.parent)
            height = DGH.getRealHeight(self.parent)
        return (
            -width/2,
            width/2,
            0,
            height - self.menuBarHeight - self.toolBarHeight)

    def show_load_shader_dialog(self):
        base.messenger.send("unregisterKeyboardAndMouseEvents")
        ShaderLoaderDialogManager(self.close_load_shader_dialog, self.core.scene_objects)

    def close_load_shader_dialog(self, accept, shader_details):
        base.messenger.send("reregisterKeyboardAndMouseEvents")
        if accept:
            base.messenger.send("addShader", [shader_details])
