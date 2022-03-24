import logging

from SceneEditor.GUI.dialogs.ShaderLoaderDialog import GUI
from SceneEditor.GUI.dialogs.ShaderInput import GUI as ShaderInput
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from SceneEditor.directGuiOverrides.DirectOptionMenu import DirectOptionMenu
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer
from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer

from panda3d.core import Shader, Vec2, Vec3, Vec4

DGG.BELOW = "below"

class ShaderDetails:
    shader_language = Shader.SL_GLSL

    vertex_path = ""
    tessellation_ctrl_path = ""
    tessellation_eval_path = ""
    geometry_path = ""
    fragment_path = ""

    input_dict = {}

class ShaderLoaderDialogManager(GUI):
    def __init__(self, accept_func, scene_objects):
        self.bg_frame = DirectFrame(frameColor=(0,0,0,0.5))
        self.autoSizer = DirectAutoSizer(
            frameColor=(0,0,0,0),
            parent=base.pixel2d,
            child=self.bg_frame
            )
        GUI.__init__(self, base.pixel2d)
        self.frm_main.set_pos((base.win.get_size().x/2, 0, -base.win.get_size().y/2))

        self.accept_func = accept_func
        self.scene_objects = scene_objects

        self.btn_ok["command"] = self.close_dialog
        self.btn_ok["extraArgs"] = [True]

        self.btn_cancel["command"] = self.close_dialog
        self.btn_cancel["extraArgs"] = [False]

        self.lbl_tessellation_ctrl["text"] = "Tessellation\nControll"
        self.lbl_tessellation_ev["text"] = "Tessellation\nEvaluation"

        self.btn_browse_vertex["command"] = self.browse_vertex
        self.btn_browse_fragment["command"] = self.browse_fragment
        self.btn_browse_tessellation_ctrl["command"] = self.browse_tessellation_ctrl
        self.btn_browse_tessellation_eval["command"] = self.browse_tessellation_eval
        self.btn_browse_geometry["command"] = self.browse_geometry

        self.shader_input_list = []
        self.btn_add_shader_input["command"] = self.add_input
        self.input_box = DirectBoxSizer(
            parent=self.frm_shader_input.canvas,
            orientation=DGG.VERTICAL)

        # prepare the item list for the nodepath selection
        self.item_dict = {}
        max_length = 40
        for obj in self.scene_objects:
            entry = str(obj)
            if len(entry) > max_length:
                entry = f"...{entry[-max_length:]}"
            if entry in self.item_dict:
                index = 1
                new_entry = ""
                while True:
                    new_entry = f"{index}-...{entry[-max_length:]}"
                    if new_entry not in self.item_dict:
                        entry = new_entry
                        break
                    index += 1
            self.item_dict[entry] = obj

    def add_input(self):
        input_type = self.cmb_shader_input_type.get().lower()
        shader_input = ShaderInput()
        shader_input.input_type = input_type
        if input_type == "texture":
            shader_input.frm_nodepath.hide()
            shader_input.frm_vector.hide()
        elif input_type == "nodepath":
            shader_input.frm_texture.hide()
            shader_input.frm_vector.hide()

            shader_input.cmb_nodepaths.destroy()
            shader_input.cmb_nodepaths = DirectOptionMenu(
                borderWidth = (0.2, 0.2),
                pad = (0.2, 0.2),
                pos = (5, 0, -15.5),
                hpr = (0, 0, 0),
                scale = (12, 12, 12),
                parent=shader_input.frm_nodepath,
                items=list(self.item_dict.keys()),
                popupMenuLocation=DGG.BELOW
            )

            #shader_input.cmb_nodepaths["items"] = list(self.item_dict.keys())
            #shader_input.cmb_nodepaths.setItems()
            #shader_input.cmb_nodepaths["item_text_align"] = 0
            #shader_input.cmb_nodepaths.resetFrameSize()
        elif input_type == "vector":
            shader_input.frm_texture.hide()
            shader_input.frm_nodepath.hide()
        self.input_box.addItem(shader_input.frm_content)
        shader_input.txt_input_name["focusInCommand"] = self.clearText
        shader_input.txt_input_name["focusInExtraArgs"] = [shader_input.txt_input_name]

        shader_input.btn_remove["command"] = self.remove_input
        shader_input.btn_remove["extraArgs"] = [shader_input]

        self.frm_shader_input["canvasSize"] = self.input_box["frameSize"]

        self.shader_input_list.append(shader_input)

    def remove_input(self, shader_input):
        self.shader_input_list.remove(shader_input)
        shader_input.destroy()

    def clearText(self, entry):
        entry.enterText('')

    def browse_vertex(self):
        self.show_browser(self.set_vertex_path, "vertex.glsl")

    def set_vertex_path(self, accept):
        if accept:
            self.txt_vertex_path.set(self.browser.get())
        self.browser.destroy()

    def browse_fragment(self):
        self.show_browser(self.set_fragment_path, "fragment.glsl")

    def set_fragment_path(self, accept):
        if accept:
            self.txt_fragment_path.set(self.browser.get())
        self.browser.destroy()

    def browse_tessellation_eval(self):
        self.show_browser(self.set_tessellation_eval_path, "tessellation_evaluation.glsl")

    def set_tessellation_eval_path(self, accept):
        if accept:
            self.txt_tessellation_ev_path.set(self.browser.get())
        self.browser.destroy()

    def browse_tessellation_ctrl(self):
        self.show_browser(self.set_tessellation_ctrl_path, "tessellation_control.glsl")

    def set_tessellation_ctrl_path(self, accept):
        if accept:
            self.txt_tessellation_ctrl_path.set(self.browser.get())
        self.browser.destroy()

    def browse_geometry(self):
        self.show_browser(self.set_geometry_path, "geometry.glsl")

    def set_geometry_path(self, accept):
        if accept:
            self.txt_geometry_path.set(self.browser.get())
        self.browser.destroy()

    def show_browser(self, cmd, filename):
        self.browser = DirectFolderBrowser(
            cmd,
            True,
            defaultFilename=filename)

    def close_dialog(self, accept):
        details = ShaderDetails()
        details.vertex_path = self.txt_vertex_path.get()
        details.tessellation_ctrl_path = self.txt_tessellation_ctrl_path.get()
        details.tessellation_eval_path = self.txt_tessellation_ev_path.get()
        details.geometry_path = self.txt_geometry_path.get()
        details.fragment_path = self.txt_fragment_path.get()
        for entry in self.shader_input_list:
            input_name = entry.txt_input_name.get()
            value = None
            print("CHECK INPUT VALUE")
            print(entry.input_type)
            if entry.input_type == "texture":
                value = entry.txt_texture_path.get()
            elif entry.input_type == "nodepath":
                value = self.item_dict[entry.cmb_nodepaths.get()]
            elif entry.input_type == "vector":
                print("VECTOR VALUE")
                val_1 = entry.txt_vec_1.get()
                val_2 = entry.txt_vec_2.get()
                val_3 = entry.txt_vec_3.get()
                val_4 = entry.txt_vec_4.get()
                if val_4:
                    print("VEC 4")
                    val_1 = float(val_1 if val_1 != "" else 0.0)
                    val_2 = float(val_2 if val_2 != "" else 0.0)
                    val_3 = float(val_3 if val_3 != "" else 0.0)
                    val_4 = float(val_4 if val_4 != "" else 0.0)
                    value = Vec4(val_1, val_2, val_3, val_4)
                elif val_3:
                    print("VEC 3")
                    val_1 = float(val_1 if val_1 != "" else 0.0)
                    val_2 = float(val_2 if val_2 != "" else 0.0)
                    val_3 = float(val_3 if val_3 != "" else 0.0)
                    value = Vec3(val_1, val_2, val_3)
                elif val_2:
                    print("VEC 2")
                    val_1 = float(val_1 if val_1 != "" else 0.0)
                    val_2 = float(val_2 if val_2 != "" else 0.0)
                    value = Vec2(val_1, val_2)
                else:
                    print("VEC Failed")
                    logging.error(f"Can't create a 1 dimensional vector for {input_name}")

                print(value)

            if value != None:
                details.input_dict[input_name] = value

        self.accept_func(accept, details)
        self.destroy()

        self.autoSizer["updateOnWindowResize"] = False
        self.autoSizer.removeChild()
        self.autoSizer.destroy()
        self.bg_frame.destroy()
