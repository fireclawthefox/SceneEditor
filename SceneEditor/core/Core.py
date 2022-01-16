import logging
from uuid import uuid4

from direct.directtools.DirectGrid import DirectGrid

from SceneEditor.core.KillRing import KillRing
from SceneEditor.core.TransformationHandler import TransformationHandler
from SceneEditor.core.SelectionHandler import SelectionHandler

class Core(TransformationHandler, SelectionHandler):
    def __init__(self):
        self.killRing = KillRing()

        self.models = []

        self.selected_objects = []

        self.copied_objects = []
        self.cut_objects = []

        self.dirty = False

        self.grid = DirectGrid(gridSize=1000.0, gridSpacing=1, parent=render)

        self.scene_root = render.attach_new_node("scene_root")
        self.scene_model_parent = self.scene_root.attach_new_node("scene_model_parent")

        self.load_corner_axis_display()

        self.show_collisions = False

        TransformationHandler.__init__(self)
        SelectionHandler.__init__(self)

    #
    # PROJECT HANDLING
    #
    def new_project(self):
        self.limiting_x = False
        self.limiting_y = False
        self.limiting_z = False

        for obj in self.models[:]:
            self.deselect(obj)
            obj.remove_node()

        self.models = []
        self.limit_line.reset()
        self.limit_line_np.stash()
        base.messenger.send("update_structure")

    #
    # SCENE INFORMATION DISPLAY
    #
    def load_corner_axis_display(self):
        # a node that is placed at the bottom left corner of the screen
        self.compas_node = base.cam.attach_new_node("compas_node")
        self.compas_node.setCompass()

        # load the axis that should be displayed
        self.axis = loader.loadModel("zup-axis")
        # make sure it will be drawn above all other elements
        self.axis.set_scale(0.02)
        self.axis.reparentTo(aspect2d)

        ws = base.win.get_size()

        self.axis_z = 0.55

        base.task_mgr.add(self.axis_updater_task, "axis_updater_task")

    def axis_updater_task(self, task):
        self.axis.set_hpr(self.compas_node.get_hpr(base.cam))

        ws = base.win.get_size()
        self.axis.set_pos((ws.x / ws.y) - 0.3, 0, self.axis_z)
        return task.cont

    def toggle_grid(self):
        if self.grid.is_hidden():
            self.grid.show()
        else:
            self.grid.hide()

    #
    # SCENE GRAPH HANDLING
    #
    def load_model(self, path):
        model = loader.loadModel(path)
        model.set_tag("filepath", path)
        model.set_tag("object_type", "model")
        model.set_tag("model_id", str(uuid4()))
        model.reparent_to(self.scene_model_parent)
        self.models.append(model)
        return model

    def move_element_in_structure(self, direction=1, objects=None):
        print(direction)
        if objects is None:
            objects = self.selected_objects

        for obj in objects:
            parent = obj.getParent()
            newSort = max(0, obj.getSort()+direction)

            obj.reparentTo(parent, newSort)

        base.messenger.send("update_structure")

    #
    # COLLISION HANDLING
    #
    def toggle_collision_visualization(self):
        if self.show_collisions:
            print("HIDE COLLISIONS")
            base.cTrav.hide_collisions()
            for obj in self.models:
                collisionNodes = obj.find_all_matches("**/+CollisionNode")
                for collisionNode in collisionNodes:
                    collisionNode.hide()
        else:
            print("SHOW COLLISIONS")
            base.cTrav.show_collisions(render)
            for obj in self.models:
                collisionNodes = obj.find_all_matches("**/+CollisionNode")
                for collisionNode in collisionNodes:
                    collisionNode.show()

        self.show_collisions = not self.show_collisions
        base.messenger.send("update_structure")

    #
    # CLIPBOARD HANDLING
    #
    def copy_elements(self):
        if len(self.selected_objects) == 0: return
        self.copied_objects = self.selected_objects[:]

    def cut_elements(self):
        if len(self.selected_objects) == 0: return
        self.cut_objects = self.selected_objects[:]

    def paste_elements(self):
        if len(self.cut_objects) > 0:
            parent = self.scene_model_parent
            if len(self.selected_objects) > 0:
                parent = self.selected_objects[-1]
            self.deselect_all()
            for obj in self.cut_objects:
                if obj == parent: continue
                obj.reparent_to(parent)
                self.select(obj, True)
            self.cut_objects = []
        elif len(self.copied_objects) > 0:
            parent = self.scene_model_parent
            if len(self.selected_objects) > 0:
                parent = self.selected_objects[-1]

            self.deselect_all()

            for obj in self.copied_objects:
                new_obj = obj.copy_to(parent)
                new_obj.set_tag("model_id", str(uuid4()))
                self.models.append(new_obj)
                self.select(new_obj, True)

        base.messenger.send("update_structure")
        base.messenger.send("start_moving")

    #
    # KILL RING HANDLING
    #
    def addToKillRing(self, obj, action, objectType, oldValue, newValue):
        if action == "set" and oldValue == newValue:
            logging.debug(f"action={action}, type={objectType} was not added to killring, reason: old={oldValue} equals new={newValue}")
            return
        logging.debug(f"Add to killring action={action}, type={objectType}, old={oldValue}, new={newValue}")
        self.killRing.push(obj, action, objectType, oldValue, newValue)

    def undo(self):
        # undo this action
        workOn = self.killRing.pop()

        if workOn is None: return

        if workOn.action == "set":
            if workOn.objectType == "pos":
                logging.debug(f"undo Position to {workOn.oldValue}")
                workOn.editObject.set_pos(workOn.oldValue)
            elif workOn.objectType == "hpr":
                logging.debug(f"undo Rotation to {workOn.oldValue}")
                workOn.editObject.set_hpr(workOn.oldValue)
            elif workOn.objectType == "scale":
                logging.debug(f"undo Scale to {workOn.oldValue}")
                workOn.editObject.set_scale(workOn.oldValue)
        elif workOn.action == "add" and workOn.objectType == "element":
            logging.debug(f"undo remove added element {workOn.editObject}")
            self.remove([workOn.editObject], False)

        elif workOn.action == "kill" and workOn.objectType == "element":
            logging.debug(f"undo last kill {workOn.editObject}")
            workOn.editObject.unstash()
            base.messenger.send("update_structure")

        elif workOn.action == "copy":
            logging.debug(f"undo last copy {workOn.objectType}")
            if workOn.objectType == "element":
                self.remove([workOn.editObject], False)

        if len(self.selected_objects):
            self.selection_highlight_marker.setPos(self.get_selection_middle_point())

        base.messenger.send("setDirtyFlag")

    def redo(self):
        # redo this
        workOn = self.killRing.pull()

        if workOn is None:
            logging.debug("nothing to redo")
            return

        if workOn.action == "set":
            if workOn.objectType == "pos":
                if type(workOn.newValue) is list:
                    workOn.editObject.set_pos(*workOn.newValue)
                else:
                    workOn.editObject.set_pos(workOn.newValue)
            elif workOn.objectType == "hpr":
                if type(workOn.newValue) is list:
                    workOn.editObject.set_hpr(*workOn.newValue)
                else:
                    workOn.editObject.set_hpr(workOn.newValue)
            elif workOn.objectType == "scale":
                if type(workOn.newValue) is list:
                    workOn.editObject.set_scale(*workOn.newValue)
                else:
                    workOn.editObject.set_scale(workOn.newValue)

        elif workOn.action == "add" and workOn.objectType == "element":
            workOn.editObject.unstash()
            base.messenger.send("update_structure")

        elif workOn.action == "kill" and workOn.objectType == "element":
            self.remove([workOn.editObject], False)
            base.messenger.send("update_structure")

        elif workOn.action == "copy":
            if workOn.objectType == "element":
                workOn.editObject.unstash()
                base.messenger.send("update_structure")

        if len(self.selected_objects):
            self.selection_highlight_marker.setPos(self.get_selection_middle_point())

        base.messenger.send("setDirtyFlag")

    def cycleKillRing(self):
        """Cycles through the redo branches at the current depth of the kill ring"""
        self.undo()
        self.killRing.cycleChildren()
        self.redo()
