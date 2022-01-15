import os

from direct.showbase.ShowBase import ShowBase

from panda3d.core import TextNode, CollisionTraverser, loadPrcFileData, WindowProperties, ConfigVariableBool, ConfigVariableString

from SceneEditor.core.CameraController import CameraController
from SceneEditor.core.Core import Core
from SceneEditor.export.ExportPy import ExporterPy
from SceneEditor.export.ExportProject import ExporterProject
from SceneEditor.loader.LoadProject import ProjectLoader
from SceneEditor.GUI.MainView import MainView

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectDialog import OkCancelDialog

from DirectGuiExtension.DirectTooltip import DirectTooltip
from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser

loadPrcFileData(
    "",
    """
    sync-video #t
    textures-power-2 none
    window-title Scene Editor
    #show-frame-rate-meter #t
    #want-pstats #t
    maximized #t
    model-path $MAIN_DIR/models/
    win-size 1280 720
    """)


class SceneEditor(ShowBase):
    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)

        self.tt = DirectTooltip(
            text = "Tooltip",
            #text_fg = (1,1,1,1),
            pad=(0.2, 0.2),
            scale = 16,
            text_align = TextNode.ALeft,
            frameColor = (1, 1, 0.7, 1),
            parent=base.pixel2d,
            sortOrder=1000)

        self.opened_dialog_close_functions = []

        self.core = Core()
        self.camcontroller = CameraController()
        self.mainView = MainView(self.tt, self.core.grid)

        base.cTrav = CollisionTraverser("base traverser")

        panda = self.core.load_model("models/panda")

        panda = self.core.load_model("models/panda")
        panda.setY(30)
        panda.setZ(-5)

        panda = self.core.load_model("models/panda")
        panda.setX(30)
        panda.setY(15)
        panda.setZ(5)

        self.mainView.structurePanel.refreshStructureTree(self.core.models, self.core.selected_objects)

        self.dlg_quit = None
        self.dlg_new_project = None

        self.enable_events()

    def enable_events(self):
        self.accept("escape", self.inteligentEscape)

        # SAVING/LOADING
        self.accept("setLastPath", self.setLastPath)

        self.lastDirPath = ConfigVariableString("work-dir-path", "~").getValue()
        self.lastFileNameWOExtension = "scene"

        # PICKING
        self.accept("mouse1", self.core.handle_pick, [False])
        self.accept("shift-mouse1", self.core.handle_pick, [True])
        self.accept("mouse3", self.core.deselect_all)
        self.accept("pickObject", self.core.select)

        # OBJECT EDITING
        self.accept("start_moving", self.start_moving)

        # CAM HANDLING
        self.accept("mouse2", self.camcontroller.setMoveCamera, [True])
        self.accept("mouse2-up", self.camcontroller.setMoveCamera, [False])
        self.accept("shift", self.camcontroller.setMovePivot, [True])
        self.accept("shift-up", self.camcontroller.setMovePivot, [False])
        self.accept("shift-mouse2", self.camcontroller.setMoveCamera, [True])
        self.accept("shift-mouse2-up", self.camcontroller.setMoveCamera, [False])
        self.accept("wheel_up", self.camcontroller.zoom, [True])
        self.accept("wheel_down", self.camcontroller.zoom, [False])

        # CORE EVENTS
        self.accept("setDirtyFlag", self.set_dirty)
        self.accept("clearDirtyFlag", self.set_clean)

        # UI EVENTS

        # MENU- AND TOOLBAR
        self.accept("newProject", self.core.new_project)
        self.accept("loadProject", self.load)
        self.accept("saveProject", self.save)
        self.accept("exportProject", self.export)
        self.accept("loadModel", self.load_model_browser)
        self.accept("quit_app", self.quit_app)
        self.accept("toggleGrid", self.core.toggle_grid)
        self.accept("zoom-in", self.camcontroller.zoom, [True])
        self.accept("zoom-out", self.camcontroller.zoom, [False])
        self.accept("zoom-reset", self.camcontroller.reset_zoom)
        self.accept("undo", self.core.undo)
        self.accept("redo", self.core.redo)
        self.accept("cycleRedo", self.core.cycleKillRing)
        self.accept("addToKillRing", self.core.addToKillRing)
        self.accept("removeObject", self.core.remove)
        self.accept("copyElement", self.core.copy_elements)
        self.accept("cutElement", self.core.cut_elements)
        self.accept("pasteElement", self.core.paste_elements)
        #self.accept("showSettings"
        #self.accept("showHelp"

        self.accept("update_structure", self.update_structure_panel)

        # UI ELEMENT EDITING
        self.accept("toggleElementVisibility", self.core.toggle_visibility)
        self.accept("removeElement", self.core.remove)
        self.accept("selectElement", self.core.select)
        self.accept("moveElementInStructure", self.core.move_element_in_structure)

        self.register_keyboard_events()

    def register_keyboard_events(self):
        self.keyEvents = {
            "control-n": [self.new],
            "control-s": [self.save],
            "control-e": [self.export],
            "control-o": [self.load],
            "control-q": [self.quit_app],

            "+": [self.camcontroller.zoom, [True]],
            "-": [self.camcontroller.zoom, [False]],
            "control-0": [self.camcontroller.resetPivotDefault],
            "3": [self.camcontroller.setPivotRight],
            "control-3": [self.camcontroller.setPivotLeft],
            "1": [self.camcontroller.setPivotFront],
            "control-1": [self.camcontroller.setPivotBack],
            "7": [self.camcontroller.setPivotTop],
            "control-7": [self.camcontroller.setPivotBottom],
            "5": [self.camcontroller.toggle_lense],

            "c": [self.core.toggle_collision_visualization],
            "g": [self.start_moving],
            "r": [self.start_rotating],
            "delete": [self.core.remove],
            "h": [self.core.toggle_visibility],

            "control-c": [self.core.copy_elements],
            "control-x": [self.core.cut_elements],
            "control-v": [self.core.paste_elements],

            #"control-g": [self.toolBar.cb_grid.commandFunc, [None]],
            #"f1": [self.showHelp],
            "control-z": [self.core.undo],
            "control-y": [self.core.redo],
            "shift-control-y": [self.core.cycleKillRing],

            "page_up": [self.core.move_element_in_structure, [1]],
            "page_down": [self.core.move_element_in_structure, [-1]],
        }

        for event, actionSet in self.keyEvents.items():
            if len(actionSet) == 2:
                self.accept(event, actionSet[0], extraArgs=actionSet[1])
            else:
                self.accept(event, actionSet[0])

    def ignore_keyboard_events(self):
        for event, actionSet in self.keyEvents.items():
            self.ignore(event)


    def inteligentEscape(self):
        dlg_list = [self.dlg_quit]
        if not all(dlg is None for dlg in dlg_list):
            self.opened_dialog_close_functions[-1](None)

    def set_dirty(self):
        wp = WindowProperties()
        wp.setTitle("*Scene Editor")
        base.win.requestProperties(wp)

        self.core.dirty = True

    def set_clean(self):
        wp = WindowProperties()
        wp.setTitle("Scene Editor")
        base.win.requestProperties(wp)

        self.core.dirty = False
        self.hasSaved = True


    def start_moving(self):
        self.ignore("mouse1")
        self.ignore("shift-mouse1")
        self.ignore("mouse3")

        self.ignore_keyboard_events()

        self.accept("mouse1", self.stop_moving)
        self.accept("mouse3", self.stop_moving, [True])
        self.accept("g", self.stop_moving)
        self.accept("x", self.core.limit_x)
        self.accept("y", self.core.limit_y)
        self.accept("z", self.core.limit_z)

        self.core.start_move_objects(self.core.selected_objects)

    def stop_moving(self, cancel=False):
        self.ignore("mouse1")
        self.ignore("mouse3")
        self.ignore("g")
        self.ignore("x")
        self.ignore("y")
        self.ignore("z")

        self.accept("mouse1", self.core.handle_pick, [False])
        self.accept("shift-mouse1", self.core.handle_pick, [True])
        self.accept("mouse3", self.core.deselect_all)

        self.register_keyboard_events()

        if not cancel:
            self.core.stop_move_objects()
        else:
            self.core.cancel_move_objects()

    def start_rotating(self):
        self.ignore("mouse1")
        self.ignore("shift-mouse1")
        self.ignore("mouse3")

        self.ignore_keyboard_events()

        self.accept("mouse1", self.stop_rotating)
        self.accept("mouse3", self.stop_rotating, [True])
        self.accept("r", self.stop_rotating)
        self.accept("x", self.core.limit_x)
        self.accept("y", self.core.limit_y)
        self.accept("z", self.core.limit_z)

        self.core.start_rotate_objects(self.core.selected_objects)

    def stop_rotating(self, cancel=False):
        self.ignore("mouse1")
        self.ignore("mouse3")
        self.ignore("r")
        self.ignore("x")
        self.ignore("y")
        self.ignore("z")

        self.accept("mouse1", self.core.handle_pick, [False])
        self.accept("shift-mouse1", self.core.handle_pick, [True])
        self.accept("mouse3", self.core.deselect_all)

        self.register_keyboard_events()

        if not cancel:
            self.core.stop_rotate_objects()
        else:
            self.core.cancel_rotate_objects()

    def load_model_browser(self):
        self.browser = DirectFolderBrowser(
            self.load_model_browser_action,
            True,
            tooltip=self.tt)
        self.browser.show()

    def load_model_browser_action(self, confirm):
        if confirm:
            self.core.load_model(self.browser.get())
            base.messenger.send("update_structure")
        self.browser.hide()
        self.browser = None

    def update_structure_panel(self):
        self.mainView.structurePanel.refreshStructureTree(self.core.models, self.core.selected_objects)

    def disableEvents(self):
        self.ignoreAll()

    def new(self):
        if self.core.dirty:
            self.dlg_new_project = OkCancelDialog(
                text="You have unsaved changes!\nReally create new project?",
                relief=DGG.RIDGE,
                frameColor=(1,1,1,1),
                frameSize=(-0.5,0.5,-0.3,0.2),
                sortOrder=1,
                button_relief=DGG.FLAT,
                button_frameColor=(0.8, 0.8, 0.8, 1),
                command=self.__newProject,
                scale=300,
                pos=(base.getSize()[0]/2, 0, -base.getSize()[1]/2),
                parent=base.pixel2d)
            self.dlg_new_project_shadow = DirectFrame(
                pos=(base.getSize()[0]/2 + 10, 0, -base.getSize()[1]/2 - 10),
                sortOrder=0,
                frameColor=(0,0,0,0.5),
                frameSize=self.dlg_new_project.bounds,
                scale=300,
                parent=base.pixel2d)
            return False
        else:
            self.__newProject(1)
            return True

    def __newProject(self, selection):
        if selection == 1:
            self.core.new_project()
            base.messenger.send("clearDirtyFlag")
        if self.dlg_new_project is not None:
            self.dlg_new_project.destroy()
            self.dlg_new_project_shadow.destroy()
            self.dlg_new_project = None
            self.dlg_new_project_shadow = None

    def setLastPath(self, path):
        self.lastDirPath = os.path.dirname(path)
        fn = os.path.splitext(os.path.basename(path))[0]
        if fn != "":
            self.lastFileNameWOExtension = os.path.splitext(os.path.basename(path))[0]

    def save(self):
        ExporterProject(
            self.lastDirPath,
            self.lastFileNameWOExtension + ".json",
            self.core.scene_model_parent,
            self.core.models,
            tooltip=self.tt)

    def export(self):
        ExporterPy(
            self.lastDirPath,
            self.lastFileNameWOExtension + ".py",
            self.core.scene_model_parent,
            self.core.models,
            self.tt)

    def load(self):
        ProjectLoader(
            self.lastDirPath,
            self.lastFileNameWOExtension + ".json",
            self.core,
            False,
            self.tt,
            self.new)

    def __quit(self, selection):
        if selection == 1:
            self.userExit()
        else:
            self.dlg_quit.destroy()
            self.dlg_quit_shadow.destroy()
            self.dlg_quit = None
            self.dlg_quit_shadow = None
            del self.opened_dialog_close_functions[-1]

    def quit_app(self):
        if self.dlg_quit is not None: return
        if ConfigVariableBool("skip-ask-for-quit", False).getValue() or self.core.dirty == False:
            self.__quit(1)
            return

        self.dlg_quit = OkCancelDialog(
            text="You have unsaved changes!\nReally Quit?",
            state=DGG.NORMAL,
            relief=DGG.RIDGE,
            frameColor=(1,1,1,1),
            scale=300,
            pos=(base.getSize()[0]/2, 0, -base.getSize()[1]/2),
            sortOrder=1,
            button_relief=DGG.FLAT,
            button_frameColor=(0.8, 0.8, 0.8, 1),
            command=self.__quit,
            parent=base.pixel2d)
        self.dlg_quit_shadow = DirectFrame(
            state=DGG.NORMAL,
            sortOrder=0,
            frameColor=(0,0,0,0.5),
            frameSize=(0, base.getSize()[0], -base.getSize()[1], 0),
            parent=base.pixel2d)
        self.opened_dialog_close_functions.append(self.__quit)


app = SceneEditor()
app.run()