import os
import logging
from importlib.machinery import SourceFileLoader

from direct.showbase.ShowBase import ShowBase

from panda3d.core import (
    TextNode,
    CollisionTraverser,
    loadPrcFileData,
    WindowProperties,
    ConfigVariableBool,
    ConfigVariableString,
    AntialiasAttrib,
    Filename
    )

from SceneEditor.core.CameraController import CameraController
from SceneEditor.core.Core import Core
from SceneEditor.export.ExportPy import ExporterPy
from SceneEditor.export.ExportProject import ExporterProject
from SceneEditor.export.ExportBam import ExporterBam
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

SIMPLE_PBR_SUPPORT = True
try:
    import simplepbr
except:
    SIMPLE_PBR_SUPPORT = False

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
        self.mainView = MainView(self.tt, self.core.grid, self.core)

        base.cTrav = CollisionTraverser("base traverser")

        self.mainView.structurePanel.refreshStructureTree(self.core.scene_objects, self.core.selected_objects)

        self.dlg_quit = None
        self.dlg_new_project = None

        self.move_object = False
        self.rotate_object = False
        self.scale_object = False
        self.mouse_events_disabled = True
        self.keyboard_events_disabled = True

        self.custom_exporters = {}

        if ConfigVariableBool("scene-editor-want-simplepbr", False).getValue() \
        and SIMPLE_PBR_SUPPORT:
            simplepbr.init(
                render_node=self.core.scene_model_parent,
                enable_shadows=True)
            pixel2d.set_shader_auto()
            aspect2d.set_shader_auto()
        else:
            self.core.scene_root.set_shader_auto()
            #self.core.scene_root.setAntialias(AntialiasAttrib.MAuto)

        self.enableParticles()


        # Event actions
        self.mouseEvents = {
            # CAM MOUSE HANDLING
            "mouse2": [self.camcontroller.setMoveCamera, [True]],
            "mouse2-up": [self.camcontroller.setMoveCamera, [False]],
            "shift": [self.camcontroller.setMovePivot, [True]],
            "shift-up": [self.camcontroller.setMovePivot, [False]],
            "shift-mouse2": [self.camcontroller.setMoveCamera, [True]],
            "shift-mouse2-up": [self.camcontroller.setMoveCamera, [False]],
            "wheel_up": [self.camcontroller.zoom, [True]],
            "wheel_down": [self.camcontroller.zoom, [False]],

            # MOUSE PICKING
            "mouse1": [self.core.handle_pick, [False]],
            "shift-mouse1": [self.core.handle_pick, [True]],
            "mouse3": [self.core.deselect_all],
        }

        self.keyboard_events = {
            # PROJECT HANDLING
            "control-n": [self.new],
            "control-s": [self.save],
            "control-e": [self.export_python],
            "control-o": [self.load],
            "control-g": [self.mainView.tool_bar.cb_grid.commandFunc, [None]],
            "control-q": [self.quit_app],

            # LOAD HANDLING
            "shift-control-s": [self.mainView.show_load_shader_dialog],
            #"shift-control-s": [self.mainView.show_load_shader_dialog],

            # CAM KEYBOARD
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

            # EDITING
            "c": [self.core.toggle_collision_visualization],
            "g": [self.start_moving],
            "r": [self.start_rotating],
            "s": [self.start_scaling],
            "delete": [self.core.remove],
            "h": [self.core.toggle_visibility],

            # KILL RING
            "control-c": [self.core.copy_elements],
            "control-x": [self.core.cut_elements],
            "control-v": [self.core.paste_elements],
            "control-z": [self.core.undo],
            "control-y": [self.core.redo],
            "shift-control-y": [self.core.cycleKillRing],

            # HELP
            #"f1": [self.showHelp],

            # SCENE GRAPH STRUCTURE
            "page_up": [self.core.move_element_in_structure, [1]],
            "page_down": [self.core.move_element_in_structure, [-1]],
        }

        self.enable_events()

        self.add_custom_exporters()

        base.taskMgr.step()
        base.taskMgr.do_method_later(0, self.mainView.update_3d_display_region, "delayed_display_region_update", extraArgs=[])

    def enable_events(self):
        self.accept("escape", self.inteligentEscape)

        # SAVING/LOADING
        self.accept("setLastPath", self.setLastPath)

        self.lastDirPath = ConfigVariableString("work-dir-path", "~").getValue()
        self.lastFileNameWOExtension = "scene"

        # PICKING
        self.accept("pickObject", self.core.select)

        # OBJECT EDITING
        self.accept("start_moving", self.start_moving)

        # CORE EVENTS
        self.accept("setDirtyFlag", self.set_dirty)
        self.accept("clearDirtyFlag", self.set_clean)

        #
        # UI EVENTS
        #

        # MENU- AND TOOLBAR
        self.accept("newProject", self.new)
        self.accept("loadProject", self.load)
        self.accept("saveProject", self.save)
        self.accept("exportProject_python", self.export_python)
        self.accept("exportProject_bam", self.export_bam)
        self.accept("custom_export", self.custom_export)
        self.accept("loadModel", self.load_model_browser)
        self.accept("loadPanda", self.core.load_model, ["models/panda"])
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
        self.accept("addEmpty", self.core.add_empty)
        self.accept("addCollision", self.core.add_collision_solid)
        self.accept("addLight", self.core.add_light)
        self.accept("addCamera", self.core.add_camera)
        self.accept("addPhysicsNode", self.core.add_physics_node)
        self.accept("addShader", self.core.add_shader)

        self.accept("update_structure", self.update_structure_panel)
        base.accept("update_properties", self.update_properties_panel)

        # UI ELEMENT EDITING
        self.accept("toggleElementVisibility", self.core.toggle_visibility)
        self.accept("removeElement", self.core.remove)
        self.accept("selectElement", self.core.select)
        self.accept("moveElementInStructure", self.core.move_element_in_structure)

        self.accept("3d_display_region_changed", self.core.update_selection_mouse_watcher)

        self.accept("unregisterKeyboardEvents", self.ignore_keyboard_events)
        self.accept("reregisterKeyboardEvents", self.register_keyboard_events)

        self.accept("unregisterMouseEvents", self.ignore_mouse_events)
        self.accept("reregisterMouseEvents", self.register_mouse_events)

        self.accept("unregisterKeyboardAndMouseEvents", self.ignore_keyboard_and_mouse_events)
        self.accept("reregisterKeyboardAndMouseEvents", self.register_keyboard_and_mouse_events)
        self.register_keyboard_and_mouse_events()

    def register_keyboard_and_mouse_events(self):
        self.register_mouse_events()
        self.register_keyboard_events()

    def register_mouse_events(self):
        if self.mouse_events_disabled:
            for event, action_set in self.mouseEvents.items():
                self.__register_events(event, action_set)
            self.mouse_events_disabled = False

    def register_keyboard_events(self):
        if self.keyboard_events_disabled:
            for event, action_set in self.keyboard_events.items():
                self.__register_events(event, action_set)
            self.keyboard_events_disabled = False

    def __register_events(self, event, action_set):
        if len(action_set) == 2:
            self.accept(event, action_set[0], extraArgs=action_set[1])
        else:
            self.accept(event, action_set[0])

    def ignore_keyboard_and_mouse_events(self):
        self.ignore_mouse_events()
        self.ignore_keyboard_events()

    def ignore_mouse_events(self):
        if not self.mouse_events_disabled:
            for event, action_set in self.mouseEvents.items():
                self.ignore(event)
            self.mouse_events_disabled = True

    def ignore_keyboard_events(self):
        if not self.keyboard_events_disabled:
            for event, actionSet in self.keyboard_events.items():
                self.ignore(event)
            self.keyboard_events_disabled = True

    def inteligentEscape(self):
        dlg_list = [self.dlg_quit, self.dlg_new_project]
        if not all(dlg is None for dlg in dlg_list):
            self.opened_dialog_close_functions[-1](None)

        if self.camcontroller.startCameraMovement:
            self.camcontroller.setMoveCamera(False)

        if self.keyboard_events_disabled:
            self.register_keyboard_and_mouse_events()

        if self.move_object:
            self.stop_move_objects()
        if self.rotate_object:
            self.stop_rotate_objects()
        if self.scale_object:
            self.stop_scale_objects()


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
        if not self.core.has_objects_selected(): return
        self.ignore_keyboard_and_mouse_events()

        self.accept("mouse1", self.stop_moving)
        self.accept("mouse3", self.stop_moving, [True])
        self.accept("g", self.stop_moving)
        self.accept("x", self.core.limit_x)
        self.accept("y", self.core.limit_y)
        self.accept("z", self.core.limit_z)

        self.core.start_move_objects(self.core.selected_objects)
        self.move_object = True

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

        self.register_keyboard_and_mouse_events()

        if not cancel:
            self.core.stop_move_objects()
        else:
            self.core.cancel_move_objects()
        self.move_object = False

    def start_rotating(self):
        if not self.core.has_objects_selected(): return
        self.ignore_keyboard_and_mouse_events()

        self.accept("mouse1", self.stop_rotating)
        self.accept("mouse3", self.stop_rotating, [True])
        self.accept("r", self.stop_rotating)
        self.accept("x", self.core.limit_x)
        self.accept("y", self.core.limit_y)
        self.accept("z", self.core.limit_z)

        self.core.start_rotate_objects(self.core.selected_objects)
        self.rotate_object = True

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

        self.register_keyboard_and_mouse_events()

        if not cancel:
            self.core.stop_rotate_objects()
        else:
            self.core.cancel_rotate_objects()
        self.rotate_object = False

    def start_scaling(self):
        if not self.core.has_objects_selected(): return
        self.ignore_keyboard_and_mouse_events()

        self.accept("mouse1", self.stop_scaling)
        self.accept("mouse3", self.stop_scaling, [True])
        self.accept("s", self.stop_scaling)
        self.accept("x", self.core.limit_x)
        self.accept("y", self.core.limit_y)
        self.accept("z", self.core.limit_z)

        self.core.start_scale_objects(self.core.selected_objects)
        self.scale_object = True

    def stop_scaling(self, cancel=False):
        self.ignore("mouse1")
        self.ignore("mouse3")
        self.ignore("s")
        self.ignore("x")
        self.ignore("y")
        self.ignore("z")

        self.accept("mouse1", self.core.handle_pick, [False])
        self.accept("shift-mouse1", self.core.handle_pick, [True])
        self.accept("mouse3", self.core.deselect_all)

        self.register_keyboard_and_mouse_events()

        if not cancel:
            self.core.stop_scale_objects()
        else:
            self.core.cancel_scale_objects()
        self.scale_object = False

    def load_model_browser(self):
        self.browser = DirectFolderBrowser(
            self.load_model_browser_action,
            True,
            tooltip=self.tt)
        self.browser.show()

    def load_model_browser_action(self, confirm):
        if confirm:
            model_path = Filename.from_os_specific(self.browser.get())
            self.core.load_model(model_path)
        self.browser.hide()
        self.browser = None

    def update_structure_panel(self):
        self.mainView.structurePanel.refreshStructureTree(self.core.scene_objects, self.core.selected_objects)

    def update_properties_panel(self):
        self.mainView.propertiesPanel.clear()
        self.mainView.propertiesPanel.setupProperties(self.core.selected_objects)

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
            self.opened_dialog_close_functions.append(self.__newProject)
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
            self.core.scene_objects,
            tooltip=self.tt)

    def export_python(self):
        ExporterPy(
            self.lastDirPath,
            self.lastFileNameWOExtension + ".py",
            self.core.scene_model_parent,
            self.core.scene_objects,
            self.tt)

    def export_bam(self):
        ExporterBam(
            self.lastDirPath,
            self.lastFileNameWOExtension + ".bam",
            self.core.scene_model_parent,
            self.core.scene_objects,
            self.tt)

    def add_custom_exporters(self):
        # get the custom exporter modules path
        custom_export_path = ConfigVariableString(
            "scene-editor-custom-export-path",
            os.path.join(".","SceneEditor", "custom_export")).getValue()

        # check if the path is good
        if not os.path.exists(custom_export_path):
            return

        # walk through the folders
        for root, dirs, files in os.walk(custom_export_path):
            for mod_dir in dirs:
                # ignore these
                if mod_dir in ["__pycache__"]:
                    continue

                filepath = os.path.join(root, mod_dir, 'exporter.py')

                # check if the required python file exists
                if not os.path.exists(filepath):
                    continue

                # imports the module from the given path
                logging.debug(f"importing custom exporter {filepath}")
                exporter = SourceFileLoader("exporter", filepath).load_module()

                # get exporter meta
                exporter_name = exporter.get_name()
                exporter_id = exporter.get_name()

                # add the exporter
                self.custom_exporters[exporter_id] = exporter
                self.mainView.menuBar.add_export_entry(exporter_name, exporter_id)

    def custom_export(self, exporter):
        logging.debug(f"Export with {exporter}")
        self.custom_exporters[exporter].Exporter(
            self.lastDirPath,
            self.lastFileNameWOExtension + ".bam",
            self.core.scene_model_parent,
            self.core.scene_objects,
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
