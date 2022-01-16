from panda3d.core import (
    CollisionTraverser,
    CollisionHandlerQueue,
    CollisionRay,
    CollisionNode,
    GeomNode,
    Point3)

class SelectionHandler:
    def __init__(self):
        self.pick_traverser = CollisionTraverser()

        self.picker_ray = CollisionRay()
        self.pick_handler = CollisionHandlerQueue()

        self.picker_node = CollisionNode("mouseRay")
        self.picker_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.picker_node.addSolid(self.picker_ray)

        self.picker_np = base.cam.attachNewNode(self.picker_node)

        self.pick_traverser.addCollider(self.picker_np, self.pick_handler)

        self.selection_highlight_marker = loader.loadModel('models/misc/sphere')
        self.selection_highlight_marker.node().setName('selection_highlight_marker')
        self.selection_highlight_marker.reparentTo(self.scene_root)
        self.selection_highlight_marker.setColor(1, 0.6, 0.2, 1)
        self.selection_highlight_marker.set_depth_test(False)
        self.selection_highlight_marker.set_depth_write(False)
        self.selection_highlight_marker.set_bin("fixed",0)
        self.selection_highlight_marker.setScale(0.3)
        self.selection_highlight_marker.hide()


    def handle_pick(self, multiselect):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.picker_ray.setFromLens(base.camNode, mpos.x, mpos.y)
            self.pick_traverser.traverse(self.scene_model_parent)

            if self.pick_handler.getNumEntries() > 0:
                self.pick_handler.sortEntries()
                picked_obj = self.pick_handler.getEntry(0).getIntoNodePath()
                picked_obj = picked_obj.findNetTag("model_id")
                if not picked_obj.isEmpty():
                    base.messenger.send("pickObject", [picked_obj, multiselect])

    def select(self, obj, multiselect=False):
        if obj in self.selected_objects and multiselect:
            # deselect an already selected model
            self.deselect(obj)

            self.selection_highlight_marker.setPos(self.get_selection_middle_point())
            return
        if not multiselect:
            self.deselect_all()

        self.selected_objects += [obj]

        self.selected_objects[-1].setColorScale(1, 0.8, 0.3, 1)
        for obj in self.selected_objects[:-1]:
            # lighter color for all except the last selected
            obj.setColorScale(1, 1, 0.4, 1)


        self.selection_highlight_marker.setPos(self.get_selection_middle_point())
        self.selection_highlight_marker.show()

        base.messenger.send("update_structure")

    def deselect(self, obj):
        if obj not in self.selected_objects: return
        obj.clearColorScale()
        self.selected_objects.remove(obj)
        if len(self.selected_objects) == 0:
            self.selection_highlight_marker.hide()

        base.messenger.send("update_structure")

    def deselect_all(self):
        for obj in self.selected_objects:
            obj.clearColorScale()
        self.selection_highlight_marker.hide()

        self.selected_objects = []

        base.messenger.send("update_structure")

    def remove(self, objs=None, includeWithKillCycle=True):
        if objs is None:
            objs = self.selected_objects[:]

        for obj in objs:
            self.deselect(obj)
            obj.stash()
            if includeWithKillCycle:
                base.messenger.send("addToKillRing",
                    [obj, "kill", "element", None, None])

        base.messenger.send("setDirtyFlag")
        base.messenger.send("update_structure")

    def remove_all(self):
        for obj in self.models[:]:
            self.deselect(obj)
            obj.stash()

        base.messenger.send("setDirtyFlag")
        base.messenger.send("update_structure")

    def toggle_visibility(self, objs=None):
        if objs is None:
            objs = self.selected_objects

        for obj in objs:
            if obj.is_stashed():
                obj.unstash()
            else:
                obj.stash()
                #self.deselect(obj)

        base.messenger.send("update_structure")

    def get_selection_middle_point(self):
        max_x = None
        max_y = None
        max_z = None
        min_x = None
        min_y = None
        min_z = None
        for obj in self.selected_objects:
            if max_x is None:
                max_x = obj.get_x()
                max_y = obj.get_y()
                max_z = obj.get_z()
                min_x = obj.get_x()
                min_y = obj.get_y()
                min_z = obj.get_z()
            else:
                max_x = max(max_x, obj.get_x())
                max_y = max(max_y, obj.get_y())
                max_z = max(max_z, obj.get_z())
                min_x = min(min_x, obj.get_x())
                min_y = min(min_y, obj.get_y())
                min_z = min(min_z, obj.get_z())

        return Point3((min_x + max_x)/2, (min_y + max_y)/2, (min_z + max_z)/2)

