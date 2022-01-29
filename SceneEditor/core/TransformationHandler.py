import math

from direct.directtools.DirectGeometry import LineNodePath

from panda3d.core import (
    Point3,
    Point2,
    LRotation,
    VBase4)

class TransformationHandler:
    def __init__(self):
        self.limiting_x = False
        self.limiting_y = False
        self.limiting_z = False

        self.limit_line_np = self.scene_root.attachNewNode('limit_line_np')
        self.limit_line = LineNodePath(self.limit_line_np)
        self.limit_line.lineNode.setName('limit_line')
        self.limit_line.setThickness(3)
        self.limit_line_np.stash()


    #
    # LIMITING LINES
    #
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


    #
    # MOVING
    #
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
            base.messenger.send("update_properties")

        self.clear_limit()

        taskMgr.remove("move_objects_task")

    def cancel_move_objects(self):
        t = taskMgr.getTasksNamed("move_objects_task")[0]

        for obj in t.object_infos.keys():
            obj.set_pos(t.object_infos[obj])

        self.selection_highlight_marker.setPos(self.get_selection_middle_point())

        self.clear_limit()

        taskMgr.remove("move_objects_task")


    #
    # ROTATION
    #
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
            base.messenger.send("update_properties")

        self.clear_limit()

        taskMgr.remove("rotate_objects_task")

    def cancel_rotate_objects(self):
        t = taskMgr.getTasksNamed("rotate_objects_task")[0]

        for obj in t.object_infos.keys():
            obj.set_hpr(t.object_infos[obj][2])

        self.clear_limit()

        taskMgr.remove("rotate_objects_task")


    #
    # SCALING
    #
    def start_scale_objects(self, objects):
        taskMgr.remove("scale_objects_task")
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
                obj.get_scale()
                ]
        t = taskMgr.add(self.scale_objects_task, "scale_objects_task")
        t.object_infos = object_infos
        t.has_scaled = False
        t.start_mouse_pos = Point2(mpos)
        t.middle = Point2((min_x + max_x)/2, (min_y + max_y)/2)
        t.start_distance = (t.middle - mpos).length()

    def scale_objects_task(self, t):
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():

            mpos = base.mouseWatcherNode.getMouse()

            scale_diff = (t.middle - mpos).length() - t.start_distance
            scale_diff *= 1.2

            for obj in t.object_infos.keys():

                # check if the mouse has moved far enough from it's initial position
                mouseMove = (t.start_mouse_pos - mpos)
                if mouseMove.length() < 0.001:
                    # we don't want the model to move yet
                    return t.cont

                # store the old position
                old_scale = obj.get_scale()

                # get the models start scale
                scale = t.object_infos[obj][0]

                new_x_scale = scale.x + scale_diff
                new_y_scale = scale.y + scale_diff
                new_z_scale = scale.z + scale_diff

                if not (self.limiting_x or self.limiting_y or self.limiting_z):
                    obj.set_scale(new_x_scale,new_y_scale,new_z_scale)
                elif self.limiting_x:
                    obj.set_sx(new_x_scale)
                elif self.limiting_y:
                    obj.set_sy(new_y_scale)
                elif self.limiting_z:
                    obj.set_sz(new_z_scale)


                # check if the item has actually moved
                if old_scale != obj.get_scale():
                    # model has moved, notice everyone interested about it
                    t.has_scaled = True

        return t.cont

    def stop_scale_objects(self):
        t = taskMgr.getTasksNamed("scale_objects_task")[0]

        if t.has_scaled:
            if not self.dirty:
                self.dirty = True
                base.messenger.send("setDirtyFlag")
            for obj in t.object_infos.keys():
                base.messenger.send("addToKillRing",
                    [obj, "set", "scale", t.object_infos[obj][0], obj.get_scale()])
            base.messenger.send("update_properties")

        self.clear_limit()

        taskMgr.remove("scale_objects_task")

    def cancel_scale_objects(self):
        t = taskMgr.getTasksNamed("scale_objects_task")[0]

        for obj in t.object_infos.keys():
            obj.set_scale(t.object_infos[obj][0])

        self.clear_limit()

        taskMgr.remove("scale_objects_task")

