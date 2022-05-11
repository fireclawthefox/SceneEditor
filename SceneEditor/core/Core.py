import logging
from uuid import uuid4

#from direct.directtools.DirectGrid import DirectGrid
from SceneEditor.directtoolsOverrides.DirectGrid import DirectGrid

from SceneEditor.core.TransformationHandler import TransformationHandler
from SceneEditor.core.SelectionHandler import SelectionHandler
from SceneEditor.core.CoreKillRingHandler import CoreKillRingHandler

from panda3d.physics import ActorNode

from panda3d.core import (
    Plane,
    Vec3,
    Vec4,
    Point3,
    NodePath,
    DrawMask,

    # Shaders
    Shader,

    # Collision solids
    CollisionNode,
    CollisionSphere,
    CollisionCapsule,
    CollisionInvSphere,
    CollisionPlane,
    CollisionRay,
    CollisionLine,
    CollisionSegment,
    CollisionParabola,
    CollisionBox,

    # Lights
    PointLight,
    DirectionalLight,
    AmbientLight,
    Spotlight,

    # Camera
    Camera,
    # Lens
    PerspectiveLens,
    OrthographicLens,
    GeomNode,
    )

class Core(TransformationHandler, SelectionHandler, CoreKillRingHandler):
    def __init__(self):
        self.shading_mask = DrawMask(0x0000ffff)

        CoreKillRingHandler.__init__(self)

        self.scene_objects = []

        self.selected_objects = []

        self.copied_objects = []
        self.cut_objects = []

        self.dirty = False

        self.grid = DirectGrid(gridSize=1000.0, gridSpacing=1, parent=render)
        # usual scene editor setup
        self.prepare_for_editor(self.grid)
        self.grid.flatten_strong()
        self.grid.set_shader_off(1)

        self.scene_root = render.attach_new_node("scene_root")
        self.scene_model_parent = self.scene_root.attach_new_node("scene_model_parent")

        self.load_corner_axis_display()

        self.show_collisions = False

        TransformationHandler.__init__(self)
        SelectionHandler.__init__(self)

    def disable(self):
        self.scene_root.hide()
        self.grid.hide()
        self.axis.hide()

    def enable(self):
        self.scene_root.show()
        self.grid.show()
        self.axis.show()

    #
    # PROJECT HANDLING
    #
    def new_project(self):
        self.limiting_x = False
        self.limiting_y = False
        self.limiting_z = False

        for obj in self.scene_objects[:]:
            self.deselect(obj)
            obj.remove_node()

        self.scene_model_parent.clearLight()

        self.scene_objects = []
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
        self.axis2 = loader.loadModel("misc/xyzAxis")
        self.axis2.set_h(180)
        self.axis2.set_sz(-1)
        self.axis2.reparent_to(self.axis)
        # make sure it will be drawn above all other elements
        self.axis.set_scale(0.02)
        self.axis.reparent_to(aspect2d)

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
        model.set_tag("filepath", str(path))
        model.set_tag("object_type", "model")
        model.set_tag("scene_object_id", str(uuid4()))
        model.reparent_to(self.scene_model_parent)
        self.scene_objects.append(model)

        base.messenger.send("addToKillRing",
            [model, "add", "model", None, None])

        base.messenger.send("update_structure")
        return model

    def add_empty(self):
        model = loader.loadModel("models/misc/xyzAxis")
        model.set_tag("object_type", "empty")
        model.set_tag("scene_object_id", str(uuid4()))
        model.reparent_to(self.scene_model_parent)
        self.scene_objects.append(model)

        # usual scene editor setup
        self.prepare_for_editor(model)

        base.messenger.send("addToKillRing",
            [model, "add", "empty", None, None])

        base.messenger.send("update_structure")
        return model

    def add_physics_node(self):
        actor_node = ActorNode("ActorNode")
        base.physicsMgr.attach_physical_node(actor_node)

        i = 1
        physics_node_name = f"PhysicsNode_{i}"
        while self.scene_model_parent.find(f"**/{physics_node_name}"):
            i += 1
            physics_node_name = f"PhysicsNode_{i}"

        physics_np = NodePath(physics_node_name)
        physics_np.set_tag("object_type", "physics")
        physics_np.set_tag("scene_object_id", str(uuid4()))
        physics_np.reparentTo(self.scene_model_parent)
        physics_np.attachNewNode(actor_node)
        self.scene_objects.append(physics_np)

        base.messenger.send("addToKillRing",
            [physics_np, "add", "physics_node", None, None])

        base.messenger.send("update_structure")
        return physics_np

    def add_collision_solid(self, solid_type, solid_info):
        i = 1
        solid_name = f"{solid_type}_{i}"
        while self.scene_model_parent.find(f"**/{solid_name}"):
            i += 1
            solid_name = f"{solid_type}_{i}"

        cn = CollisionNode(solid_name)
        col_np = self.scene_model_parent.attachNewNode(cn)
        col_np.show()
        col_np.set_tag("object_type", "collision")
        col_np.set_tag("collision_solid_type", solid_type)
        col_np.set_tag("scene_object_id", str(uuid4()))

        if solid_type == "CollisionSphere":
            if solid_info == {}:
                solid_info["center"] = Point3(0, 0, 0)
                solid_info["radius"] = 1
            center = solid_info["center"]
            radius = solid_info["radius"]
            col = CollisionSphere(center,radius)
        elif solid_type == "CollisionBox":
            if solid_info == {}:
                solid_info["center"] = Point3(0, 0, 0)
                solid_info["x"] = 1
                solid_info["y"] = 1
                solid_info["z"] = 1
            center = solid_info["center"]
            x = solid_info["x"]
            y = solid_info["y"]
            z = solid_info["z"]
            col = CollisionBox(center, x, y, z)
        elif solid_type == "CollisionPlane":
            if solid_info == {}:
                solid_info["plane"] = Plane(Vec3(0,0,1), Point3(0,0,0))
            plane = solid_info["plane"]
            col = CollisionPlane(plane)
        elif solid_type == "CollisionCapsule":
            if solid_info == {}:
                solid_info["point_a"] = Vec3(0, 0, 0)
                solid_info["point_b"] = Point3(0, 0, 1)
                solid_info["radius"] = 0.3
            point_a = solid_info["point_a"]
            point_b = solid_info["point_b"]
            radius = solid_info["radius"]
            col = CollisionCapsule(point_a, point_b, radius)
        elif solid_type == "CollisionLine":
            if solid_info == {}:
                solid_info["origin"] = Point3(0, 0, 0)
                solid_info["direction"] = Vec3(0, 0, 1)
            origin = solid_info["origin"]
            direction = solid_info["direction"]
            col = CollisionLine(origin, direction)
        elif solid_type == "CollisionSegment":
            if solid_info == {}:
                solid_info["point_a"] = Vec3(0, 0, 0)
                solid_info["point_b"] = Point3(0, 0, 1)
            point_a = solid_info["point_a"]
            point_b = solid_info["point_b"]
            col = CollisionSegment(point_a, point_b)
        elif solid_type == "CollisionRay":
            if solid_info == {}:
                solid_info["origin"] = Point3(0, 0, 0)
                solid_info["direction"] = Vec3(0, 0, 1)
            origin = solid_info["origin"]
            direction = solid_info["direction"]
            col = CollisionRay(origin, direction)
        #elif solid_type == "Parabola":
        elif solid_type == "CollisionInvSphere":
            if solid_info == {}:
                solid_info["center"] = Point3(0, 0, 0)
                solid_info["radius"] = 1
            center = solid_info["center"]
            radius = solid_info["radius"]
            col = CollisionInvSphere(center,radius)
        else:
            logging.warning(f"Unsupported collision solid type {solid_type}.")
            return

        if solid_type == "CollisionPlane":
            # BUG https://github.com/panda3d/panda3d/issues/1248
            col_np.set_tag("collision_solid_info", str(solid_info).replace(" ", ", ").replace(":,", ":"))
        else:
            col_np.set_tag("collision_solid_info", str(solid_info))
        cn.addSolid(col)

        # usual scene editor setup
        self.prepare_for_editor(col_np)

        self.scene_objects.append(col_np)

        base.messenger.send("addToKillRing",
            [col_np, "add", "collision", None, None])

        base.messenger.send("update_structure")
        return col_np

    def update_collision_info_tag(self, obj):
        solid_type = obj.get_tag("collision_solid_type")
        solid_info == {}
        solid = obj.find("*/+CollisionNode")
        if solid_type == "CollisionSphere":
            solid_info["center"] = solid.center
            solid_info["radius"] = solid.radius
        elif solid_type == "CollisionBox":
            solid_info["center"] = solid.center
            solid_info["x"] = solid.dimensions.x
            solid_info["y"] = solid.dimensions.y
            solid_info["z"] = solid.dimensions.z
        elif solid_type == "CollisionPlane":
            solid_info["plane"] = solid.plane
        elif solid_type == "CollisionCapsule":
            solid_info["point_a"] = solid.point_a
            solid_info["point_b"] = solid.point_b
            solid_info["radius"] = solid.radius
        elif solid_type == "CollisionLine":
            solid_info["origin"] = solid.origin
            solid_info["direction"] = solid.direction
        elif solid_type == "CollisionSegment":
            solid_info["point_a"] = solid.point_a
            solid_info["point_b"] = solid.point_b
        elif solid_type == "CollisionRay":
            solid_info["origin"] = solid.origin
            solid_info["direction"] = solid.direction
        #elif solid_type == "Parabola":
        elif solid_type == "CollisionInvSphere":
            solid_info["center"] = solid.center
            solid_info["radius"] = solid.radius
        else:
            logging.warning(f"Unsupported collision solid type {solid_type}.")
            return
        if solid_type == "CollisionPlane":
            # BUG https://github.com/panda3d/panda3d/issues/1248
            obj.set_tag("collision_solid_info", str(solid_info).replace(" ", ", ").replace(":,", ":"))
        else:
            obj.set_tag("collision_solid_info", str(solid_info))

    def add_light(self, light_type, light_info):
        light_model_np = None
        light_np = None
        light = None
        lens_node = None

        i = 1
        light_name = f"{light_type}_{i}"
        while self.scene_model_parent.find(f"**/{light_name}"):
            i += 1
            light_name = f"{light_type}_{i}"

        if light_type == "PointLight":
            light_model_np = loader.loadModel("models/misc/Pointlight")
            light = PointLight('Point Light')

        elif light_type == "DirectionalLight":
            light_model_np = loader.loadModel("models/misc/Dirlight")
            light = DirectionalLight('Directional Light')

            light.camera_mask = self.shading_mask

            # create the lens visualization
            lens_node = self.create_lens_geom(light.get_lens())

        elif light_type == "AmbientLight":
            light_model_np = NodePath(light_name)
            light = AmbientLight('Ambient Light')

        elif light_type == "Spotlight":
            light_model_np = loader.loadModel("models/misc/Spotlight")
            light = Spotlight('Spotlight')

            lens = PerspectiveLens()
            light.setLens(lens)
            light.camera_mask = self.shading_mask

            # create the lens visualization
            lens_node = self.create_lens_geom(lens)

        light_model_np.set_name(light_name)
        light_model_np.set_light_off()
        light_np = light_model_np.attachNewNode(light)
        if lens_node is not None:
            lens_np = light_np.attach_new_node(lens_node)
            lens_np.hide(self.shading_mask)
        light_model_np.set_tag("object_type", "light")
        light_model_np.set_tag("light_type", light_type)
        light_model_np.set_tag("scene_object_id", str(uuid4()))
        light_model_np.reparent_to(self.scene_model_parent)
        self.scene_model_parent.setLight(light_np)

        # usual scene editor setup
        self.prepare_for_editor(light_model_np)

        self.scene_objects.append(light_model_np)

        base.messenger.send("addToKillRing",
            [light_model_np, "add", "light", None, None])

        base.messenger.send("update_structure")
        return light_model_np

    def add_camera(self, cam_type, cam_info):
        model = loader.loadModel("models/misc/camera")
        model.set_tag("object_type", "camera")
        model.set_tag("scene_object_id", str(uuid4()))
        model.set_tag("camera_type", cam_type)

        lens = None
        if cam_type == "OrthographicLens":
            lens = OrthographicLens()
        else:
            lens = PerspectiveLens()

        i = 1
        cam_name = f"{cam_type}_camera_{i}"
        while self.scene_model_parent.find(f"**/{cam_name}"):
            i += 1
            cam_name = f"{cam_type}_camera_{i}"
        model.set_name(cam_name)

        cam = Camera("Camera", lens)
        model.attach_new_node(cam)

        # create the lens visualization
        node = self.create_lens_geom(lens)
        model.attach_new_node(node)

        model.reparent_to(self.scene_model_parent)
        self.scene_objects.append(model)

        # usual scene editor setup
        self.prepare_for_editor(model)

        base.messenger.send("addToKillRing",
            [model, "add", "camera", None, None])

        base.messenger.send("update_structure")
        return model

    def create_lens_geom(self, cam_lens):
        node = GeomNode("cam_lense_display_node")
        node.addGeom(cam_lens.makeGeometry())
        return node

    def move_element_in_structure(self, direction=1, objects=None):
        if objects is None:
            objects = self.selected_objects

        for obj in objects:
            parent = obj.getParent()
            newSort = max(0, obj.getSort()+direction)

            obj.reparentTo(parent, newSort)

        base.messenger.send("update_structure")

    def add_shader(self, shader_details):
        for obj in self.selected_objects:
            shader = Shader.load(
                shader_details.shader_language,
                vertex=shader_details.vertex_path,
                fragment=shader_details.fragment_path,
                geometry=shader_details.geometry_path,
                tess_control=shader_details.tessellation_ctrl_path,
                tess_evaluation=shader_details.tessellation_eval_path)

            for name, value in shader_details.input_dict.items():
                obj.set_shader_input(name, value)
            obj.setShader(shader)

    def prepare_for_editor(self, nodepath, cast_shadow=False, disable_lighting=True):
        if not cast_shadow:
            # don't cast shadows
            nodepath.hide(self.shading_mask)

        # disable lighing of this object
        if disable_lighting:
            nodepath.set_light_off()

    #
    # OBJECT TAG HANDLING
    #
    def set_edited_tag(self, obj, tag):
        tag_string = ""
        if obj.has_tag("edited_properties"):
            tag_string = obj.get_tag("edited_properties")

        tag_values = tag_string.split(",")
        if tag not in tag_values:
            tag_values.append(tag)
            obj.set_tag("edited_properties", ",".join(tag_values))

    def remove_edited_tag(self, obj, tag):
        tag_string = ""
        if obj.has_tag("edited_properties"):
            tag_string = obj.get_tag("edited_properties")

        tag_values = tag_string.split(",")
        if tag not in tag_values:
            tag_values.remove(tag)
            obj.set_tag("edited_properties", tag_values)

    def is_edited_property(self, obj, tag):
        tag_string = ""
        if obj.has_tag("edited_properties"):
            tag_string = obj.get_tag("edited_properties")

        tag_values = tag_string.split(",")
        return tag in tag_values

    #
    # COLLISION HANDLING
    #
    def toggle_collision_visualization(self):
        if self.show_collisions:
            base.cTrav.hide_collisions()
            for obj in self.scene_objects:
                if obj.get_tag("object_type") == "collision":
                    obj.hide()
                else:
                    collisionNodes = obj.find_all_matches("**/+CollisionNode")
                    for collisionNode in collisionNodes:
                        collisionNode.hide()
        else:
            base.cTrav.show_collisions(render)
            for obj in self.scene_objects:
                if obj.get_tag("object_type") == "collision":
                    obj.show()
                else:
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
                base.messenger.send("addToKillRing",
                    [obj, "cut", "element", obj.get_parent(), parent])
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
                new_obj.set_tag("scene_object_id", str(uuid4()))
                if obj.get_tag("object_type") == "collision":
                    todo
                elif obj.get_tag("object_type") == "light":
                    light_np = light_model_np.attachNewNode(light)
                    new_obj.set_tag("object_type", "light")
                    new_obj.set_tag("light_type", light_type)
                    self.scene_model_parent.setLight(new_obj.children[0])
                self.scene_objects.append(new_obj)
                self.select(new_obj, True)

                base.messenger.send("addToKillRing",
                    [new_obj, "copy", "element", None, None])

        base.messenger.send("update_structure")
        base.messenger.send("start_moving")

