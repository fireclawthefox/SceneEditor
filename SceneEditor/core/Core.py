from uuid import uuid4
import math, logging

from direct.directtools.DirectGrid import DirectGrid

from direct.directtools.DirectGeometry import LineNodePath
from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, Point3, LVector2f, Point2, LRotation, VBase4

from SceneEditor.core.KillRing import KillRing

class Core:
    def __init__(self):
        self.killRing = KillRing()

        self.models = []

        self.selected_objects = []

        self.copied_objects = []
        self.cut_objects = []

        self.dirty = False

        self.grid = DirectGrid(gridSize=1000.0, gridSpacing=1, parent=render)

        self.pick_traverser = CollisionTraverser()

        self.picker_ray = CollisionRay()
        self.pick_handler = CollisionHandlerQueue()

        self.picker_node = CollisionNode("mouseRay")
        self.picker_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.picker_node.addSolid(self.picker_ray)

        self.scene_root = render.attach_new_node("scene_root")
        self.scene_model_parent = self.scene_root.attach_new_node("scene_model_parent")

        self.picker_np = base.cam.attachNewNode(self.picker_node)

        self.pick_traverser.addCollider(self.picker_np, self.pick_handler)

        self.load_corner_axis_display()

        self.selection_highlight_marker = loader.loadModel('models/misc/sphere')
        self.selection_highlight_marker.node().setName('selection_highlight_marker')
        self.selection_highlight_marker.reparentTo(self.scene_root)
        self.selection_highlight_marker.setColor(1, 0.6, 0.2, 1)
        self.selection_highlight_marker.set_depth_test(False)
        self.selection_highlight_marker.set_depth_write(False)
        self.selection_highlight_marker.set_bin("fixed",0)
        self.selection_highlight_marker.setScale(0.3)

        self.limiting_x = False
        self.limiting_y = False
        self.limiting_z = False


        self.limit_line_np = self.scene_root.attachNewNode('limit_line_np')
        self.limit_line = LineNodePath(self.limit_line_np)
        self.limit_line.lineNode.setName('limit_line')
        self.limit_line.setThickness(3)
        self.limit_line_np.stash()

        self.show_collisions = False

    def toggle_grid(self):
        if self.grid.is_hidden():
            self.grid.show()
        else:
            self.grid.hide()

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

    def load_model(self, path):
        model = loader.loadModel(path)
        model.set_tag("filepath", path)
        model.set_tag("object_type", "model")
        model.set_tag("model_id", str(uuid4()))
        model.reparent_to(self.scene_model_parent)
        self.models.append(model)
        return model

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

    def limit_x(self):
        self.limiting_x = not self.limiting_x
        self.limiting_y = False
        self.limiting_z = False

        self.limit_line.setColor(VBase4(1, 0, 0, 0))
        from_pos = self.get_selection_middle_point()
        extend_a = self.get_selection_middle_point()
        extend_a.set_x(extend_a.get_x() + 1000)
        extend_b = self.get_selection_middle_point()
        extend_b.set_x(extend_b.get_x() - 1000)
        self.draw_limit_line(from_pos, extend_a, extend_b)

    def limit_y(self):
        self.limiting_y = not self.limiting_y
        self.limiting_x = False
        self.limiting_z = False

        self.limit_line.setColor(VBase4(0, 1, 0, 0))
        from_pos = self.get_selection_middle_point()
        extend_a = self.get_selection_middle_point()
        extend_a.set_y(extend_a.get_y() + 1000)
        extend_b = self.get_selection_middle_point()
        extend_b.set_y(extend_b.get_y() - 1000)
        self.draw_limit_line(from_pos, extend_a, extend_b)

    def limit_z(self):
        self.limiting_z = not self.limiting_z
        self.limiting_x = False
        self.limiting_y = False

        self.limit_line.setColor(VBase4(0, 0, 1, 0))
        from_pos = self.get_selection_middle_point()
        extend_a = self.get_selection_middle_point()
        extend_a.set_z(extend_a.get_z() + 1000)
        extend_b = self.get_selection_middle_point()
        extend_b.set_z(extend_b.get_z() - 1000)
        self.draw_limit_line(from_pos, extend_a, extend_b)

    def draw_limit_line(self, start_pos, extend_a, extend_b):
        self.limit_line_np.unstash()
        self.limit_line_np.set_hpr(0,0,0)
        self.limit_line.reset()
        self.limit_line.moveTo(start_pos)
        self.limit_line.drawTo(extend_a)
        self.limit_line.moveTo(start_pos)
        self.limit_line.drawTo(extend_b)
        self.limit_line.create()

    def clear_limit(self):
        self.limit_line.reset()
        self.limit_line_np.stash()

        self.limiting_x = False
        self.limiting_y = False
        self.limiting_z = False

    def start_move_objects(self, objects):
        taskMgr.remove("move_objects_task")
        mpos = base.mouseWatcherNode.getMouse()
        object_infos = {}
        for obj in objects:
            object_infos[obj] = obj.get_pos()
        t = taskMgr.add(self.move_objects_task, "move_objects_task")
        t.object_infos = object_infos
        t.start_mouse_pos = Point2(mpos)
        t.has_moved = False
        t.last_mouse_pos = mpos

    def move_objects_task(self, t):
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():

            mpos = base.mouseWatcherNode.getMouse()

            for obj in t.object_infos.keys():

                # check if the mouse has moved far enough from it's initial position
                mouseMove = (t.start_mouse_pos - mpos)
                if mouseMove.length() < 0.001:
                    # we don't want the model to move yet
                    return t.cont

                # store the old position
                oldPos = obj.get_pos()

                # get the mouse movement for this frame
                mouse_delta = t.last_mouse_pos - mpos
                # get the model position in camera space
                camspace_point = obj.get_pos(base.cam)
                screenspace_point = Point3()
                # get the position as it is seen on screen
                base.cam.node().get_lens().project(camspace_point, screenspace_point)
                # update the position according to the mouse movement
                screenspace_point.xy -= mouse_delta
                camspace_point = Point3()
                # convert the screen position back to the 3D scene coordinates as seen by the camera
                base.cam.node().get_lens().extrude_depth(screenspace_point, camspace_point)
                # update the models position relative to the camera
                pre_pos = obj.get_pos()
                obj.set_pos(base.cam, camspace_point)
                if self.limiting_x:
                    obj.set_y(pre_pos.y)
                    obj.set_z(pre_pos.z)
                if self.limiting_y:
                    obj.set_x(pre_pos.x)
                    obj.set_z(pre_pos.z)
                if self.limiting_z:
                    obj.set_x(pre_pos.x)
                    obj.set_y(pre_pos.y)

                self.selection_highlight_marker.setPos(self.get_selection_middle_point())

                # check if the item has actually moved
                if oldPos != obj.get_pos():
                    # model has moved, notice everyone interested about it
                    t.has_moved = True

            # store the mouse position for the next frame
            t.last_mouse_pos = Point2(mpos)
        return t.cont

    def stop_move_objects(self):
        t = taskMgr.getTasksNamed("move_objects_task")[0]

        if t.has_moved:
            if not self.dirty:
                self.dirty = True
                base.messenger.send("setDirtyFlag")
            for obj in t.object_infos.keys():
                base.messenger.send("addToKillRing",
                    [obj, "set", "pos", t.object_infos[obj], obj.get_pos()])

        self.clear_limit()

        taskMgr.remove("move_objects_task")

    def cancel_move_objects(self):
        t = taskMgr.getTasksNamed("move_objects_task")[0]

        for obj in t.object_infos.keys():
            obj.set_pos(t.object_infos[obj])

        self.selection_highlight_marker.setPos(self.get_selection_middle_point())

        self.clear_limit()

        taskMgr.remove("move_objects_task")



    def start_rotate_objects(self, objects):
        taskMgr.remove("rotate_objects_task")
        mpos = base.mouseWatcherNode.getMouse()
        object_infos = {}

        max_x = None
        max_y = None
        min_x = None
        min_y = None

        for obj in objects:

            # get the model position in camera space
            camspace_point = obj.get_pos(base.cam)
            screenspace_point = Point3()
            # get the position as it is seen on screen
            base.cam.node().get_lens().project(camspace_point, screenspace_point)

            x = screenspace_point.x - mpos.x
            y = screenspace_point.y - mpos.y
            rad = -math.atan2(y, x)
            deg = rad * (180 / math.pi)

            if max_x is None:
                max_x = screenspace_point.x
                max_y = screenspace_point.y
                min_x = screenspace_point.x
                min_y = screenspace_point.y
            else:
                max_x = max(max_x, screenspace_point.x)
                max_y = max(max_y, screenspace_point.y)
                min_x = min(min_x, screenspace_point.x)
                min_y = min(min_y, screenspace_point.y)

            object_infos[obj] = [
                deg,
                obj.get_quat().getAngle(),
                obj.get_hpr()
                ]
        t = taskMgr.add(self.rotate_objects_task, "rotate_objects_task")
        t.object_infos = object_infos
        t.has_rotated = False
        t.start_mouse_pos = Point2(mpos)
        t.last_mouse_pos = mpos
        t.middle = Point2((min_x + max_x)/2, (min_y + max_y)/2)

    def rotate_objects_task(self, t):
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():

            mpos = base.mouseWatcherNode.getMouse()

            for obj in t.object_infos.keys():

                # check if the mouse has moved far enough from it's initial position
                mouseMove = (t.start_mouse_pos - mpos)
                if mouseMove.length() < 0.001:
                    # we don't want the model to move yet
                    return t.cont

                # store the old position
                old_hpr = obj.get_hpr()

                # rotate mouse around the middle point of all models
                x = t.middle.x - mpos.x
                y = t.middle.y - mpos.y
                rad = -math.atan2(y, x)
                deg = rad * (180 / math.pi)

                # subtract the start hpr so we always start at 0 where the mouse is at first
                deg -= t.object_infos[obj][0]
                # get the models start hpr so it won't be reset to a hpr of 0
                hpr = t.object_infos[obj][1]

                if not (self.limiting_x or self.limiting_y or self.limiting_z):
                    obj.set_quat(LRotation(obj.parent.get_relative_vector(base.cam, (0,1,0)), deg-hpr))
                elif self.limiting_x:
                    obj.set_p(deg-hpr)
                elif self.limiting_y:
                    obj.set_r(deg-hpr)
                elif self.limiting_z:
                    obj.set_h(deg+hpr)


                # check if the item has actually moved
                if old_hpr != obj.get_hpr():
                    # model has moved, notice everyone interested about it
                    t.has_rotated = True

            # store the mouse position for the next frame
            t.last_mouse_pos = Point2(mpos)
        return t.cont

    def stop_rotate_objects(self):
        t = taskMgr.getTasksNamed("rotate_objects_task")[0]

        if t.has_rotated:
            if not self.dirty:
                self.dirty = True
                base.messenger.send("setDirtyFlag")
            for obj in t.object_infos.keys():
                base.messenger.send("addToKillRing",
                    [obj, "set", "hpr", t.object_infos[obj][2], obj.get_hpr()])

        self.clear_limit()

        taskMgr.remove("rotate_objects_task")

    def cancel_rotate_objects(self):
        t = taskMgr.getTasksNamed("rotate_objects_task")[0]

        for obj in t.object_infos.keys():
            obj.set_hpr(t.object_infos[obj][2])

        self.clear_limit()

        taskMgr.remove("rotate_objects_task")



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


    def move_element_in_structure(self, direction=1, objects=None):
        print(direction)
        if objects is None:
            objects = self.selected_objects

        for obj in objects:
            parent = obj.getParent()
            newSort = max(0, obj.getSort()+direction)

            obj.reparentTo(parent, newSort)

        base.messenger.send("update_structure")

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
            self.remove(workOn.editObject, False)

        elif workOn.action == "kill" and workOn.objectType == "element":
            logging.debug(f"undo last kill {workOn.editObject}")
            workOn.editObject.unstash()
            base.messenger.send("update_structure")

        elif workOn.action == "copy":
            logging.debug(f"undo last copy {workOn.objectType}")
            if workOn.objectType == "element":
                self.remove(workOn.editObject.element, False)

        base.messenger.send("setDirtyFlag")


    def redo(self):
        ...
        '''
        # redo this
        workOn = self.killRing.pull()

        if workOn is None:
            logging.debug("nothing to redo")
            return

        if workOn.action == "set":
            if workOn.objectType == "pos":
                if type(workOn.newValue) is list:
                    workOn.editObject.element.setPos(*workOn.newValue)
                else:
                    workOn.editObject.element.setPos(workOn.newValue)
            elif workOn.objectType == "pressEffect":
                workOn.editObject.extraOptions["pressEffect"] = workOn.newValue
            else:
                try:
                    workOn.editObject.element[workOn.objectType] = workOn.newValue
                except:
                    logging.exception(f"property {workOn.objectType} currently not supported by undo/redo")

        elif workOn.action == "add" and workOn.objectType == "element":
            workOn.editObject.unstash()
            self.elementDict[workOn.oldValue[0]] = workOn.oldValue[1]
            base.messenger.send("update_structure")

        elif workOn.action == "kill" and workOn.objectType == "element":
            self.removeElement(workOn.editObject, False)

        elif workOn.action == "copy":
            if workOn.objectType == "element":
                workOn.editObject.unstash()
                self.elementDict[workOn.oldValue[0]] = workOn.oldValue[1]
                base.messenger.send("update_structure")
            elif workOn.objectType == "properties":
                for key, value in workOn.newValue.items():
                    if key == "pos":
                        workOn.editObject.element.setPos(value)
                    elif key == "hpr":
                        workOn.editObject.element.setHpr(value)
                    elif key == "scale":
                        workOn.editObject.element.setScale(value)
                    elif key == "text_fg":
                        workOn.editObject.element["text_fg"] = value
                    else:
                        workOn.editObject.element[key] = value[1]

        if self.selectedElement is not None:
            self.refreshProperties(self.selectedElement)
        base.messenger.send("setDirtyFlag")
        '''

    def cycleKillRing(self):
        """Cycles through the redo branches at the current depth of the kill ring"""
        self.undo()
        self.killRing.cycleChildren()
        self.redo()
