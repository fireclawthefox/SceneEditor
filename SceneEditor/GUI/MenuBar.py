from direct.showbase.DirectObject import DirectObject
from direct.gui import DirectGuiGlobals as DGG
from DirectGuiExtension.DirectMenuItem import (
    DirectMenuItem,
    DirectMenuItemEntry,
    DirectMenuItemSubMenu,
    DirectMenuSeparator)
from DirectGuiExtension.DirectMenuBar import DirectMenuBar

class MenuBar(DirectObject):
    def __init__(self):
        screenWidthPx = base.getSize()[0]

        #
        # Menubar
        #
        self.menuBar = DirectMenuBar(
            frameColor=(0.25, 0.25, 0.25, 1),
            frameSize=(0,screenWidthPx,-12, 12),
            autoUpdateFrameSize=False,
            pos=(0, 0, 0),
            itemMargin=(2,2,2,2),
            parent=base.pixel2d)

        self.export_entry = DirectMenuItemSubMenu("Export >", [
            DirectMenuItemEntry("Python", base.messenger.send, ["exportProject_python"]),
            DirectMenuItemEntry("Bam", base.messenger.send, ["exportProject_bam"]),
        ])
        self.fileEntries = [
            DirectMenuItemEntry("New", base.messenger.send, ["newProject"]),
            DirectMenuSeparator(),
            DirectMenuItemEntry("Open", base.messenger.send, ["loadProject"]),
            DirectMenuItemEntry("Save", base.messenger.send, ["saveProject"]),
            self.export_entry,
            DirectMenuSeparator(),
            DirectMenuItemEntry("Quit", base.messenger.send, ["quit_app"]),
            ]
        self.file = self.__create_menu_item("File", self.fileEntries)

        viewEntries = [
            DirectMenuItemEntry("Toggle Grid", base.messenger.send, ["toggleGrid"]),
            DirectMenuSeparator(),
            DirectMenuItemEntry("Zoom-in", base.messenger.send, ["zoom-in"]),
            DirectMenuItemEntry("Zoom-out", base.messenger.send, ["zoom-out"]),
            DirectMenuItemEntry("reset Zoom", base.messenger.send, ["zoom-reset"]),

        ]
        self.view = self.__create_menu_item("View", viewEntries)

        toolsEntries = [
            DirectMenuItemEntry("Undo", base.messenger.send, ["undo"]),
            DirectMenuItemEntry("Redo", base.messenger.send, ["redo"]),
            DirectMenuItemEntry("Cycle redos", base.messenger.send, ["cycleRedo"]),
            DirectMenuSeparator(),
            DirectMenuItemEntry("Delete Object", base.messenger.send, ["removeObject"]),
            DirectMenuItemEntry("Copy", base.messenger.send, ["copyElement"]),
            DirectMenuItemEntry("Cut", base.messenger.send, ["cutElement"]),
            DirectMenuItemEntry("Paste", base.messenger.send, ["pasteElement"]),
            #DirectMenuSeparator(),
            #DirectMenuItemEntry("Options", base.messenger.send, ["showSettings"]),
            #DirectMenuItemEntry("Help", base.messenger.send, ["showHelp"]),
        ]
        self.tools = self.__create_menu_item("Tools", toolsEntries)

        addEntries = [
            DirectMenuItemEntry("Model", base.messenger.send, ["loadModel"]),
            DirectMenuItemEntry("Panda", base.messenger.send, ["loadPanda"]),
            DirectMenuItemEntry("Empty", base.messenger.send, ["addEmpty"]),
            DirectMenuItemSubMenu("Collision >", [
                DirectMenuItemEntry("Sphere", base.messenger.send, ["addCollision", ["CollisionSphere", {}]]),
                DirectMenuItemEntry("Box", base.messenger.send, ["addCollision", ["CollisionBox", {}]]),
                DirectMenuItemEntry("Plane", base.messenger.send, ["addCollision", ["CollisionPlane", {}]]),
                DirectMenuItemEntry("Capsule", base.messenger.send, ["addCollision", ["CollisionCapsule", {}]]),
                DirectMenuItemEntry("Line", base.messenger.send, ["addCollision", ["CollisionLine", {}]]),
                DirectMenuItemEntry("Segment", base.messenger.send, ["addCollision", ["CollisionSegment", {}]]),
                DirectMenuItemEntry("Ray", base.messenger.send, ["addCollision", ["CollisionRay", {}]]),
                #DirectMenuItemEntry("Parabola", base.messenger.send, ["addCollision", ["CollisionParabola", {}]]),
                DirectMenuItemEntry("Inverse Sphere", base.messenger.send, ["addCollision", ["CollisionInvSphere", {}]]),
                #Polygon    # Do we want to support this
                ]),
            DirectMenuItemEntry("Physics Node", base.messenger.send, ["addPhysicsNode"]),
            DirectMenuItemSubMenu("Light >", [
                DirectMenuItemEntry("Point Light", base.messenger.send, ["addLight", ["PointLight", {}]]),
                DirectMenuItemEntry("Spotlight", base.messenger.send, ["addLight", ["Spotlight", {}]]),
                DirectMenuItemEntry("Directional Light", base.messenger.send, ["addLight", ["DirectionalLight", {}]]),
                DirectMenuItemEntry("Ambient Light", base.messenger.send, ["addLight", ["AmbientLight", {}]]),
                ]),
            DirectMenuItemSubMenu("Camera >", [
                DirectMenuItemEntry("Perspective", base.messenger.send, ["addCamera", ["PerspectiveLens", {}]]),
                DirectMenuItemEntry("Orthographic", base.messenger.send, ["addCamera", ["OrthographicLens", {}]]),
                ]),
            DirectMenuItemEntry("Shader", base.messenger.send, ["show_load_shader_dialog"]),
        ]
        #TODO: THE COLORS DON'T WORK CORRECT YET
        self.add = self.__create_menu_item("Add", addEntries)

        self.menuBar["menuItems"] = [self.file, self.view, self.tools, self.add]

    def add_export_entry(self, text, tag):
        self.export_entry.items.append(
            DirectMenuItemEntry(text, base.messenger.send, ["custom_export", [tag]]))
        self.fileEntries[4] = self.export_entry
        self.file["items"] = self.fileEntries

        color = (
            (0.25, 0.25, 0.25, 1), # Normal
            (0.35, 0.35, 1, 1), # Click
            (0.25, 0.25, 1, 1), # Hover
            (0.1, 0.1, 0.1, 1)) # Disabled

        self.file["item_text_fg"]=(1,1,1,1)
        self.file["item_text_scale"]=0.8
        self.file["item_relief"]=DGG.FLAT
        self.file["item_pad"]=(0.2, 0.2)
        self.file["itemFrameColor"]=color
        self.file["popupMenu_itemMargin"]=(0,0,-.1,-.1)
        self.file["popupMenu_frameColor"]=color

    def __create_menu_item(self, text, entries):
        color = (
            (0.25, 0.25, 0.25, 1), # Normal
            (0.35, 0.35, 1, 1), # Click
            (0.25, 0.25, 1, 1), # Hover
            (0.1, 0.1, 0.1, 1)) # Disabled

        sepColor = (0.7, 0.7, 0.7, 1)

        return DirectMenuItem(
            text=text,
            text_fg=(1,1,1,1),
            text_scale=0.8,
            items=entries,
            frameSize=(0,65/21,-7/21,17/21),
            frameColor=color,
            scale=21,
            relief=DGG.FLAT,
            item_text_fg=(1,1,1,1),
            item_text_scale=0.8,
            item_relief=DGG.FLAT,
            item_pad=(0.2, 0.2),
            itemFrameColor=color,
            separatorFrameColor=sepColor,
            popupMenu_itemMargin=(0,0,-.1,-.1),
            popupMenu_frameColor=color,
            highlightColor=color[2])
