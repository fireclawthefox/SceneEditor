import logging

from direct.showbase.DirectObject import DirectObject

from direct.gui import DirectGuiGlobals as DGG

from DirectGuiExtension import DirectGuiHelper as DGH

from DirectGuiExtension.DirectTooltip import DirectTooltip

from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer
from DirectGuiExtension.DirectSplitFrame import DirectSplitFrame

from SceneEditor.GUI.MenuBar import MenuBar
from SceneEditor.GUI.ToolBar import ToolBar
from SceneEditor.GUI.panels.StructurePanel import StructurePanel


class MainView(DirectObject):
    def __init__(self, tooltip, grid):
        logging.debug("Setup GUI")

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
            parent=base.pixel2d,
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
        self.mainSplitter = DirectSplitFrame(
            frameSize=self.get_main_splitter_size(),
            #firstFrameMinSize=0,
            #secondFrameMinSize=100,
            splitterWidth=splitterWidth,
            splitterPos=-base.getSize()[0]/4,
            pixel2d=False)
        self.mainSplitter["frameColor"] = (0,0,0,0)
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

        self.structurePanel = StructurePanel(self.mainSplitter.firstFrame)
        self.mainSplitter["firstFrameUpdateSizeFunc"] = self.structurePanel.resizeFrame
        self.mainSplitter["secondFrameUpdateSizeFunc"] = self.update_3d_display_region


        self.mainBox.refresh()

    def update_3d_display_region(self):
        dr = base.cam.node().get_display_region(0)

        dw = base.win.get_size()[0]
        dh = base.win.get_size()[1]

        top_height = (self.menuBarHeight + self.toolBarHeight) / dh
        left_frame_width = DGH.getRealWidth(self.mainSplitter.firstFrame) / dw
        dr.dimensions = (
            left_frame_width,1, #L, R
            0,1 - top_height) #B, T

        w = (1-left_frame_width) * dw
        h = (1-top_height) * dh

        base.camLens.setAspectRatio(w/h)

        base.messenger.send("3d_display_region_changed")

    def get_main_splitter_size(self):
        return (
            -base.getSize()[0]/2,
            base.getSize()[0]/2,
            0,
            base.getSize()[1] - self.menuBarHeight - self.toolBarHeight)
