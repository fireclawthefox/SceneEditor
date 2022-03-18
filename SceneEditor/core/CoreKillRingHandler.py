import logging
from SceneEditor.core.KillRing import KillRing

class CoreKillRingHandler:
    def __init__(self):
        self.killRing = KillRing()

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

        if workOn is None:
            return

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
        elif workOn.action == "add":
            logging.debug(f"undo remove added element {workOn.editObject}")
            self.remove([workOn.editObject], False)

        elif workOn.action == "kill" and workOn.objectType == "element":
            logging.debug(f"undo last kill {workOn.editObject}")
            workOn.editObject.unstash()
            if workOn.editObject.get_tag("object_type") == "light":
                self.scene_model_parent.set_light(workOn.editObject.find("+Light"))
            base.messenger.send("update_structure")

        elif workOn.action == "copy":
            logging.debug(f"undo last copy {workOn.objectType}")
            if workOn.objectType == "element":
                self.remove([workOn.editObject], False)

        elif workOn.action == "cut":
            logging.debug(f"undo last cut {workOn.objectType}")
            if workOn.objectType == "element":
                workOn.editObject.reparent_to(workOn.oldValue)

        if len(self.selected_objects):
            base.messenger.send("update_selection_highlight_marker")

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

        elif workOn.action == "add":
            workOn.editObject.unstash()
            base.messenger.send("update_structure")
            if workOn.editObject.get_tag("object_type") == "light":
                self.scene_model_parent.set_light(workOn.editObject.find("+Light"))

        elif workOn.action == "kill" and workOn.objectType == "element":
            self.remove([workOn.editObject], False)
            base.messenger.send("update_structure")

        elif workOn.action == "copy":
            if workOn.objectType == "element":
                workOn.editObject.unstash()
                base.messenger.send("update_structure")
                if workOn.editObject.get_tag("object_type") == "light":
                    self.scene_model_parent.set_light(workOn.editObject.find("+Light"))

        elif workOn.action == "cut":
            logging.debug(f"undo last cut {workOn.objectType}")
            if workOn.objectType == "element":
                workOn.editObject.reparent_to(workOn.newValue)

        if len(self.selected_objects):
            base.messenger.send("update_selection_highlight_marker")

        base.messenger.send("setDirtyFlag")

    def cycleKillRing(self):
        """Cycles through the redo branches at the current depth of the kill ring"""
        self.undo()
        self.killRing.cycleChildren()
        self.redo()
