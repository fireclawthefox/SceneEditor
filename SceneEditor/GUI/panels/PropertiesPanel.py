#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Fireclaw the Fox"
__license__ = """
Simplified BSD (BSD 2-Clause) License.
See License.txt or http://opensource.org/licenses/BSD-2-Clause for more info
"""

import logging
import sys
import copy

from panda3d.core import (
    VBase4,
    LVecBase4f,
    TextNode,
    Point3,
    TextProperties,
    TransparencyAttrib,
    PGButton,
    PGFrameStyle,
    MouseButton,
    NodePath,
    ConfigVariableString)
from direct.showbase.DirectObject import DirectObject

from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectButton import DirectButton
from directGuiOverrides.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectCheckButton import DirectCheckButton

from DirectFolderBrowser.DirectFolderBrowser import DirectFolderBrowser

from DirectGuiExtension import DirectGuiHelper as DGH
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from DirectGuiExtension.DirectAutoSizer import DirectAutoSizer
from DirectGuiExtension.DirectCollapsibleFrame import DirectCollapsibleFrame

from SceneEditor.GUI.panels import ObjectPropertiesDefinition

DGG.BELOW = "below"
MWUP = PGButton.getPressPrefix() + MouseButton.wheel_up().getName() + '-'
MWDOWN = PGButton.getPressPrefix() + MouseButton.wheel_down().getName() + '-'

SCROLLBARWIDTH = 20


class PropertyHelper:
    def getFormated(value, isInt=False):
        if type(value) is int or isInt:
            return "{}".format(int(value))
        elif type(value) is not str:
            try:
                return "{:0.3f}".format(value)
            except:
                logging.error(f"couldn't convert value of type {type(value)} to float")
                return None
        else:
            return value

    def getValues(definition, obj):
        editObj = obj
        if definition.lookupAttrs is not None:
            for lookupAttr, lookupAttrArgs in definition.lookupAttrs.items():
                editObj = getattr(editObj, lookupAttr)(*lookupAttrArgs)
        if definition.setAsTag:
            return editObj.get_tag(definition.internalName)
        if definition.getFunctionName:
            return getattr(editObj, definition.getFunctionName)()
        return getattr(editObj, definition.internalName)

    def setValue(definition, obj, value, valueAsString=""):
        editObj = obj
        if definition.lookupAttrs is not None:
            for lookupAttr, lookupAttrArgs in definition.lookupAttrs.items():
                editObj = getattr(editObj, lookupAttr)(*lookupAttrArgs)
        if definition.setFunctionName:
            print(editObj)
            getattr(editObj, definition.setFunctionName)(value)
        elif definition.setAsTag:
            editObj.set_tag(definition.internalName, value)
        else:
            setattr(editObj, definition.internalName, value)


class PropertiesPanel(DirectObject):
    scrollSpeedUp = -0.001
    scrollSpeedDown = 0.001

    def __init__(self, parent, tooltip):
        height = DGH.getRealHeight(parent)
        self.tooltip = tooltip
        self.parent = parent

        self.box = DirectBoxSizer(
            frameColor=(0.25, 0.25, 0.25, 1),
            autoUpdateFrameSize=False,
            orientation=DGG.VERTICAL)

        self.sizer = DirectAutoSizer(
            updateOnWindowResize=False,
            parent=parent,
            child=self.box,
            childUpdateSizeFunc=self.box.refresh)

        self.lblHeader = DirectLabel(
            text="Properties",
            text_scale=16,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=VBase4(0, 0, 0, 0),
            )
        self.box.addItem(self.lblHeader, skipRefresh=True)

        color = (
            (0.8, 0.8, 0.8, 1),  # Normal
            (0.9, 0.9, 1, 1),  # Click
            (0.8, 0.8, 1, 1),  # Hover
            (0.5, 0.5, 0.5, 1))  # Disabled
        self.propertiesFrame = DirectScrolledFrame(
            # make the frame fit into our background frame
            frameSize=VBase4(
                self.parent["frameSize"][0], self.parent["frameSize"][1],
                self.parent["frameSize"][2]+DGH.getRealHeight(self.lblHeader), self.parent["frameSize"][3]),
            # set the frames color to transparent
            frameColor=VBase4(1, 1, 1, 1),
            scrollBarWidth=SCROLLBARWIDTH,
            verticalScroll_scrollSize=20,
            verticalScroll_thumb_relief=DGG.FLAT,
            verticalScroll_incButton_relief=DGG.FLAT,
            verticalScroll_decButton_relief=DGG.FLAT,
            verticalScroll_thumb_frameColor=color,
            verticalScroll_incButton_frameColor=color,
            verticalScroll_decButton_frameColor=color,
            horizontalScroll_thumb_relief=DGG.FLAT,
            horizontalScroll_incButton_relief=DGG.FLAT,
            horizontalScroll_decButton_relief=DGG.FLAT,
            horizontalScroll_thumb_frameColor=color,
            horizontalScroll_incButton_frameColor=color,
            horizontalScroll_decButton_frameColor=color,
            state=DGG.NORMAL)
        self.box.addItem(self.propertiesFrame)
        self.propertiesFrame.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        self.propertiesFrame.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

    def scroll(self, scrollStep, event):
        """Scrolls the properties frame vertically with the given step.
        A negative step will scroll down while a positive step value will scroll
        the frame upwards"""
        self.propertiesFrame.verticalScroll.scrollStep(scrollStep)

    def resizeFrame(self):
        """Refreshes the sizer and recalculates the framesize to fit the parents
        frame size"""
        self.sizer.refresh()
        self.propertiesFrame["frameSize"] = (
                self.sizer["frameSize"][0], self.sizer["frameSize"][1],
                self.sizer["frameSize"][2]+DGH.getRealHeight(self.lblHeader), self.sizer["frameSize"][3])
        self.propertiesFrame

    def setupProperties(self, objs):
        """Creates the set of editable properties for the given element"""

        if objs == []: return

        self.ignoreAll()
        # create the frame that will hold all our properties
        self.mainBoxFrame = DirectBoxSizer(
            orientation=DGG.VERTICAL,
            itemAlign=DirectBoxSizer.A_Left,
            frameColor=VBase4(0, 0, 0, 0),
            parent=self.propertiesFrame.getCanvas(),
            suppressMouse=True,
            state=DGG.NORMAL)
        self.mainBoxFrame.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        self.mainBoxFrame.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        for obj in objs:
            headerText = obj.get_name()
            # Create the header for the properties
            lbl = DirectLabel(
                text=headerText,
                text_scale=18,
                text_pos=(-10, 0),
                text_align=TextNode.ACenter,
                frameSize=VBase4(
                    -self.propertiesFrame["frameSize"][1],
                    self.propertiesFrame["frameSize"][1]-SCROLLBARWIDTH,
                    -10,
                    20),
                frameColor=VBase4(0.7, 0.7, 0.7, 1),
                state=DGG.NORMAL)
            lbl.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
            lbl.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
            self.mainBoxFrame.addItem(lbl)

            # Set up all the properties
            try:

                allDefinitions = {**ObjectPropertiesDefinition.DEFINITIONS}

                object_type = obj.get_tag("object_type")

                if object_type == "light":
                    object_type = obj.get_tag("light_type")
                elif object_type == "collision":
                    object_type = obj.get_tag("collision_solid_type")
                elif object_type == "camera":
                    object_type = obj.get_tag("camera_type")

                # check if we have a definition for this specific GUI element
                if object_type in allDefinitions:
                    # create the main set of properties to edit
                    wd = allDefinitions[object_type]
                    # create a header for this type of element
                    self.__createInbetweenHeader(object_type)

                    section = self.createSection()

                    # create the set of properties to edit on the main component
                    for definition in wd:
                        self.createProperty(definition, obj)

                    self.updateSection(section)

            except Exception:
                e = sys.exc_info()[1]
                base.messenger.send("showWarning", [str(e)])
                logging.exception("Error while loading properties panel")

        #
        # Reset property Frame framesize
        #
        self.updateCanvasSize()

    def updateCanvasSize(self):
        self.mainBoxFrame.refresh()

        self.propertiesFrame["canvasSize"] = (
            0,
            self.propertiesFrame["frameSize"][1]-SCROLLBARWIDTH,
            self.mainBoxFrame.bounds[2],
            0)
        self.propertiesFrame.setCanvasSize()

        a = self.propertiesFrame["canvasSize"][2]
        b = abs(self.propertiesFrame["frameSize"][2]) + self.propertiesFrame["frameSize"][3]
        scrollDefault = 200
        s = -(scrollDefault / (a / b))

        self.propertiesFrame["verticalScroll_scrollSize"] = s
        self.propertiesFrame["verticalScroll_pageSize"] = s

    def createSection(self):
        section = DirectCollapsibleFrame(
            collapsed=True,
            frameColor=(1, 1, 1, 1),
            headerheight=24,
            frameSize=(
                -self.propertiesFrame["frameSize"][1],
                self.propertiesFrame["frameSize"][1]-SCROLLBARWIDTH,
                0, 20))

        self.accept(section.getCollapsedEvent(), self.sectionCollapsed, extraArgs=[section])
        self.accept(section.getExtendedEvent(), self.updateCanvasSize)

        section.toggleCollapseButton["text_scale"] = 12
        section.toggleCollapseButton["text_pos"] = (0, -12)

        section.toggleCollapseButton.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        section.toggleCollapseButton.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        section.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        section.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])

        self.mainBoxFrame.addItem(section)
        self.boxFrame = DirectBoxSizer(
            pos=(0, 0, -section["headerheight"]),
            frameSize=(
                -self.propertiesFrame["frameSize"][1],
                self.propertiesFrame["frameSize"][1]-SCROLLBARWIDTH,
                0, 0),
            orientation=DGG.VERTICAL,
            itemAlign=DirectBoxSizer.A_Left,
            frameColor=VBase4(0, 0, 0, 0),
            parent=section,
            suppressMouse=True,
            state=DGG.NORMAL)
        self.boxFrame.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        self.boxFrame.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        return section

    def sectionCollapsed(self, section):
        self.updateCanvasSize()

    def updateSection(self, section):
        self.boxFrame.refresh()
        fs = self.boxFrame["frameSize"]
        section["frameSize"] = (fs[0], fs[1], fs[2]-section["headerheight"], fs[3])
        section.updateFrameSize()

    def createProperty(self, definition, obj):
        if definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.integer:
            self.__createNumberInput(definition, obj, int)
        elif definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.float:
            self.__createNumberInput(definition, obj, float)
        elif definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.bool:
            self.__createBoolProperty(definition, obj)
        elif definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.text:
            self.__createTextProperty(definition, obj)
        elif definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.base2:
            self.__createBaseNInput(definition, obj, 2)
        elif definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.base3:
            self.__createBaseNInput(definition, obj, 3)
        elif definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.base4:
            self.__createBaseNInput(definition, obj, 4)
        elif definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.command:
            self.__createCustomCommand(definition, obj)
        elif definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.path:
            self.__createPathProperty(definition, obj)
        elif definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.optionMenu:
            self.__createOptionMenuProperty(definition, obj)
        elif definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.list:
            self.__createListProperty(definition, obj)
        elif definition.editType == ObjectPropertiesDefinition.PropertyEditTypes.tuple:
            self.__createTupleProperty(definition, obj)
        else:
            logging.error(f"Edit type {definition.editType} not in Edit type definitions")

    def clear(self):
        if not hasattr(self, "mainBoxFrame"): return
        if self.mainBoxFrame is not None:
            self.mainBoxFrame.destroy()

    def __createInbetweenHeader(self, description):
        l = DirectLabel(
            text=description,
            text_scale=16,
            text_pos=(-10, 0),
            text_align=TextNode.ACenter,
            frameSize=VBase4(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1], -10, 20),
            frameColor=VBase4(0.85, 0.85, 0.85, 1),
            state=DGG.NORMAL)
        l.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        l.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.mainBoxFrame.addItem(l, skipRefresh=True)

    def __createPropertyHeader(self, description):
        l = DirectLabel(
            text=description,
            text_scale=12,
            text_pos=(self.propertiesFrame["frameSize"][0], 0),
            text_align=TextNode.ALeft,
            frameSize=VBase4(self.propertiesFrame["frameSize"][0], self.propertiesFrame["frameSize"][1], -10, 20),
            frameColor=VBase4(0.85, 0.85, 0.85, 1),
            state=DGG.NORMAL)
        l.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        l.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(l, skipRefresh=True)

    def __addToKillRing(self, obj, definition, oldValue, newValue):
        base.messenger.send("addToKillRing",
            [obj, "set", definition.internalName, oldValue, newValue])

    def __createTextEntry(self, text, width, command, commandArgs=[]):
        def focusOut():
            base.messenger.send("reregisterKeyboardEvents")
            command(*[entry.get()] + entry["extraArgs"])
        entry = DirectEntry(
            initialText=text,
            relief=DGG.SUNKEN,
            frameColor=(1,1,1,1),
            scale=12,
            width=width/12,
            overflow=True,
            command=command,
            extraArgs=commandArgs,
            focusInCommand=base.messenger.send,
            focusInExtraArgs=["unregisterKeyboardEvents"],
            focusOutCommand=focusOut)
        entry.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        entry.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        return entry

    #
    # General input elements
    #
    def __createBaseNInput(self, definition, obj, n, numberType=float):
        entryList = []

        def update(text, obj):
            base.messenger.send("setDirtyFlag")
            values = []
            for value in entryList:
                try:
                    values.append(numberType(value.get(True)))
                except Exception:
                    if value.get(True) == "":
                        values.append(None)
                    else:
                        logging.exception("ERROR: NAN", value.get(True))
                        values.append(numberType(0))
            try:
                oldValue = PropertyHelper.getValues(definition, obj)
                differ = False
                if oldValue is not None:
                    for i in range(n):
                        if oldValue[i] != values[i]:
                            differ = True
                            break
                elif values is not None and values != []:
                    differ = True
                if differ:
                    self.__addToKillRing(obj, definition, oldValue, values)
            except Exception as e:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")
            allValuesSet = True
            allValuesNone = True
            for value in values:
                if value is None:
                    allValuesSet = False
                if value is not None:
                    allValuesNone = False
            if allValuesNone:
                values = None
            elif allValuesSet:
                values = tuple(values)
            if allValuesNone or allValuesSet:
                PropertyHelper.setValue(definition, obj, values)
        self.__createPropertyHeader(definition.visiblename)
        values = PropertyHelper.getValues(definition, obj)
        if type(values) is int or type(values) is float:
            values = [values] * n
        if definition.nullable:
            if values is None:
                values = [""] * n
        width = (DGH.getRealWidth(self.boxFrame) - 2*SCROLLBARWIDTH) / n
        entryBox = DirectBoxSizer()
        for i in range(n):
            value = PropertyHelper.getFormated(values[i])
            entry = self.__createTextEntry(str(value), width, update, [obj])
            entryList.append(entry)
            entryBox.addItem(entry)
        self.boxFrame.addItem(entryBox, skipRefresh=True)

    def __createNumberInput(self, definition, obj, numberType):
        def update(text, obj):
            base.messenger.send("setDirtyFlag")
            value = numberType(0)
            try:
                value = numberType(text)
            except Exception:
                if text == "" and definition.nullable:
                    value = None
                else:
                    logging.exception("ERROR: NAN", value)
                    value = numberType(0)
            try:
                oldValue = PropertyHelper.getValues(definition, obj)
                self.__addToKillRing(obj, definition, oldValue, value)
            except Exception:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")
            PropertyHelper.setValue(definition, obj, value)
        self.__createPropertyHeader(definition.visiblename)
        valueA = PropertyHelper.getValues(definition, obj)
        if valueA is None and not definition.nullable:
            logging.error(f"Got None value for not nullable element {definition.internalName}")
        if valueA is not None:
            valueA = PropertyHelper.getFormated(valueA, numberType is int)
        width = DGH.getRealWidth(self.boxFrame)
        entry = self.__createTextEntry(str(valueA), width, update, [obj])
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createTextProperty(self, definition, obj):
        def update(text, obj):
            base.messenger.send("setDirtyFlag")
            try:
                oldValue = PropertyHelper.getValues(definition, obj)
                self.__addToKillRing(obj, definition, oldValue, text)
            except:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            PropertyHelper.setValue(definition, obj, text)
        self.__createPropertyHeader(definition.visiblename)
        text = PropertyHelper.getValues(definition, obj)
        width = DGH.getRealWidth(self.boxFrame)
        entry = self.__createTextEntry(text, width, update, [obj])
        self.boxFrame.addItem(entry, skipRefresh=True)

    def __createBoolProperty(self, definition, obj):
        def update(value):
            base.messenger.send("setDirtyFlag")
            try:
                oldValue = PropertyHelper.getValues(definition, obj)
                self.__addToKillRing(obj, definition, oldValue, value)
            except:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")
            PropertyHelper.setValue(definition, obj, value)
        self.__createPropertyHeader(definition.visiblename)
        valueA = PropertyHelper.getValues(definition, obj)
        btn = DirectCheckButton(
            indicatorValue=valueA,
            scale=24,
            frameSize=(-.5,.5,-.5,.5),
            text_align=TextNode.ALeft,
            command=update)
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(btn, skipRefresh=True)

    def __createListProperty(self, definition, obj):
        def update(text, obj, entries):
            base.messenger.send("setDirtyFlag")
            value = []

            for entry in entries:
                #if entry.get() != "":
                value.append(entry.get())

            try:
                oldValue = PropertyHelper.getValues(definition, obj)
                self.__addToKillRing(obj, definition, oldValue, value)
            except Exception:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            PropertyHelper.setValue(definition, obj, value)

        def addEntry(text="", updateEntries=True, updateMainBox=True):
            entry = self.__createTextEntry(text, width, update, [obj])
            entriesBox.addItem(entry, skipRefresh=True)
            entries.append(entry)

            if updateEntries:
                for entry in entries:
                    oldArgs = entry["extraArgs"]
                    if len(oldArgs) > 1:
                        oldArgs = oldArgs[:-1]
                    entry["extraArgs"] = oldArgs + [entries]

            if updateMainBox:
                entriesBox.refresh()
                self.boxFrame.refresh(id(entriesBox))
                self.resizeFrame()

        self.__createPropertyHeader(definition.visiblename)
        listItems = PropertyHelper.getValues(definition, obj)

        # make sure we have a list
        if listItems is None or isinstance(listItems, str):
            listItems = [listItems]

        width = DGH.getRealWidth(self.boxFrame)
        entriesBox = DirectBoxSizer(
            orientation=DGG.VERTICAL,
            itemAlign=DirectBoxSizer.A_Left,
            frameColor=VBase4(0,0,0,0),
            suppressMouse=True,
            state=DGG.NORMAL)
        entriesBox.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        entriesBox.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(entriesBox, skipRefresh=True)
        entries = []
        for i in range(len(listItems)):
            text = listItems[i]
            addEntry(text, i == len(listItems)-1, i == len(listItems)-1)
        btn = DirectButton(
            text="Add entry",
            pad=(0.25,0.25),
            scale=12,
            command=addEntry
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(btn, skipRefresh=True)

    def __createTupleProperty(self, definition, obj):
        def update(text, obj, entries):
            base.messenger.send("setDirtyFlag")
            value = []

            for entry in entries:
                if entry.get() != "":
                    value.append(entry.get())

            value = tuple(value)

            try:
                oldValue = PropertyHelper.getValues(definition, obj)
                self.__addToKillRing(obj, definition, oldValue, value)
            except Exception:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            PropertyHelper.setValue(definition, obj, value)

        def addEntry(text="", updateEntries=True, updateMainBox=True):
            entry = self.__createTextEntry(text, width, update, [obj])
            entriesBox.addItem(entry, skipRefresh=True)
            entries.append(entry)

            if updateEntries:
                for entry in entries:
                    oldArgs = entry["extraArgs"]
                    if len(oldArgs) > 1:
                        oldArgs = oldArgs[:-1]
                    entry["extraArgs"] = oldArgs + [entries]

            if updateMainBox:
                entriesBox.refresh()
                self.boxFrame.refresh()
                self.resizeFrame()

        self.__createPropertyHeader(definition.visiblename)
        listItems = PropertyHelper.getValues(definition, obj)
        width = DGH.getRealWidth(self.boxFrame)
        entriesBox = DirectBoxSizer(
            orientation=DGG.VERTICAL,
            itemAlign=DirectBoxSizer.A_Left,
            frameColor=VBase4(0,0,0,0),
            suppressMouse=True,
            state=DGG.NORMAL)
        entriesBox.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        entriesBox.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(entriesBox, skipRefresh=True)
        entries = []
        for i in range(len(listItems)):
            text = listItems[i]
            addEntry(text, i==len(listItems)-1, i==len(listItems)-1)
        btn = DirectButton(
            text="Add entry",
            pad=(0.25,0.25),
            scale=12,
            command=addEntry
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(btn, skipRefresh=True)

    def __createPathProperty(self, definition, obj):

        def update(text):
            value = text
            if text == "" and definition.nullable:
                value = None
            elif definition.loaderFunc is not None:
                try:
                    if type(definition.loaderFunc) is str:
                        value = eval(definition.loaderFunc)
                    else:
                        value = definition.loaderFunc(value)
                except Exception:
                    logging.exception("Couldn't load path with loader function")
                    value = text
            base.messenger.send("setDirtyFlag")
            try:
                PropertyHelper.setValue(definition, obj, value, text)
            except Exception:
                logging.exception("Couldn't load font: {}".format(text))
                updateElement[updateAttribute] = None

        def setPath(path):
            update(path)

            # make sure to take the actual value to write it to the textbox in
            # case something hapened while updating the value
            v = PropertyHelper.getValues(definition, obj)
            if v is None:
                v = ""
            entry.set(v)

        def selectPath(confirm):
            if confirm:
                setPath(self.browser.get())
            self.browser.hide()

        def showBrowser():
            self.browser = DirectFolderBrowser(
                selectPath,
                True,
                ConfigVariableString("work-dir-path", "~").getValue(),
                "",
                tooltip=self.tooltip)
            self.browser.show()
        self.__createPropertyHeader(definition.visiblename)
        path = PropertyHelper.getValues(definition, obj)
        if type(path) is not str:
            path = ""
        width = DGH.getRealWidth(self.boxFrame)
        entry = self.__createTextEntry(path, width, update)
        self.boxFrame.addItem(entry, skipRefresh=True)

        btn = DirectButton(
            text="Browse",
            text_align=TextNode.ALeft,
            command=showBrowser,
            pad=(0.25,0.25),
            scale=12
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(btn, skipRefresh=True)

    def __createOptionMenuProperty(self, definition, obj):
        def update(selection):
            oldValue = PropertyHelper.getValues(definition, obj)
            value = definition.valueOptions[selection]
            # Undo/Redo setup
            try:
                if oldValue != value:
                    self.__addToKillRing(obj, definition, oldValue, value)
            except Exception as e:
                logging.exception(f"{definition.internalName} not supported by undo/redo yet")

            # actually set the value on the element
            PropertyHelper.setValue(definition, obj, value)

        self.__createPropertyHeader(definition.visiblename)
        if definition.valueOptions is None:
            return
        value = PropertyHelper.getValues(definition, obj)
        selectedElement = list(definition.valueOptions.keys())[0]
        for k, v in definition.valueOptions.items():
            if v == value:
                selectedElement = k
                break
        menu = DirectOptionMenu(
            items=list(definition.valueOptions.keys()),
            scale=12,
            popupMenuLocation=DGG.BELOW,
            initialitem=selectedElement,
            command=update)
        menu.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        menu.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(menu, skipRefresh=True)

    def __createCustomCommand(self, definition, obj):
        self.__createPropertyHeader(definition.visiblename)
        btn = DirectButton(
            text="Run Command",
            pad=(0.25,0.25),
            scale=12,
            command=getattr(obj.element, definition.valueOptions)
            )
        btn.bind(DGG.MWDOWN, self.scroll, [self.scrollSpeedDown])
        btn.bind(DGG.MWUP, self.scroll, [self.scrollSpeedUp])
        self.boxFrame.addItem(btn, skipRefresh=True)
