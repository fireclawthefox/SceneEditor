from direct.showbase.DirectObject import DirectObject
from direct.gui import DirectGuiGlobals as DGG
from DirectGuiExtension.DirectMenuItem import (
    DirectMenuItem,
    DirectMenuItemEntry,
    DirectMenuItemSubMenu,
    DirectMenuSeparator)
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from panda3d_frame_editor_base.ui.FrameMenuBar import FrameMenuBar, MenuItem

class SEMenuBar(FrameMenuBar):
    def __init__(self):

        self.fileEntries = {
            "New": "newProject",
            "sep1": "---",
            "Open": "loadProject",
            "Save": "saveProject",
            "Export >": {
                "Python": "exportProject_python",
                "Bam": "exportProject_bam"
            },
            "sep2": "---",
            "Quit": "quit_app"
        }

        entries = [
            MenuItem("File", self.fileEntries),
            MenuItem("View", {
                "Toggle Grid": "toggleGrid",
                "sep1": "---",
                "Zoom In": [base.messenger.send, ["zoom-in", [True]]],
                "Zoom Out": [base.messenger.send, ["zoom-out", [False]]],
                "Reset Zoom": "zoom-reset"
            }),
            MenuItem("Tools", {
                "Undo": "undo",
                "Redo": "redo",
                "Cycle redos": "cycleRedo",
                "sep1": "---",
                "Delete Object": "removeObject",
                "Copy": "copyElement",
                "Cut": "cutElement",
                "Paste": "pasteElement",
            }),
            MenuItem("Add", {
                "Model": "loadModel",
                "Panda": "loadPanda",
                "Empty": "addEmpty",
                "Collision >": {
                    "Sphere": [base.messenger.send, ["addCollision", ["CollisionSphere", {}]]],
                    "Box": [base.messenger.send, ["addCollision", ["CollisionBox", {}]]],
                    "Plane": [base.messenger.send, ["addCollision", ["CollisionPlane", {}]]],
                    "Capsule": [base.messenger.send, ["addCollision", ["CollisionCapsule", {}]]],
                    "Line": [base.messenger.send, ["addCollision", ["CollisionLine", {}]]],
                    "Segment": [base.messenger.send, ["addCollision", ["CollisionSegment", {}]]],
                    "Ray": [base.messenger.send, ["addCollision", ["CollisionRay", {}]]],
                    #"Parabola": [base.messenger.send, ["addCollision", ["CollisionParabola", {}]]],
                    "Inverse Sphere": [base.messenger.send, ["addCollision", ["CollisionInvSphere", {}]]],
                    #Polygon    # Do we want to support this
                },
                "Physics Node": "addPhysicsNode",
                "Light >": {
                    "Point Light": [base.messenger.send, ["addLight", ["PointLight", {}]]],
                    "Spotlight": [base.messenger.send, ["addLight", ["Spotlight", {}]]],
                    "Directional Light": [base.messenger.send, ["addLight", ["DirectionalLight", {}]]],
                    "Ambient Light": [base.messenger.send, ["addLight", ["AmbientLight", {}]]],
                },
                "Camera >": {
                    "Perspective": [base.messenger.send, ["addCamera", ["PerspectiveLens", {}]]],
                    "Orthographic": [base.messenger.send, ["addCamera", ["OrthographicLens", {}]]],
                },
                "Shader": "show_load_shader_dialog",
            })
        ]

        FrameMenuBar.__init__(self, entries)

    def add_export_entry(self, text, tag):
        self.fileEntries["Export >"].update({
            text: [base.messenger.send, ["custom_export", [tag]]]
        })

        self.entries[0].entry_dict = self.fileEntries
        self.set_entries(self.entries)
        #self.update_entry([MenuItem("File", self.fileEntries)])
