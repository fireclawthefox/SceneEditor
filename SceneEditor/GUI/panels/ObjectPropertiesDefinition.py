import types

from panda3d.core import PGFrameStyle, TransparencyAttrib
from direct.gui import DirectGuiGlobals as DGG

class PropertyEditTypes:
    integer = "integer"
    float = "float"
    bool = "bool"
    text = "text"
    base2 = "base2"
    base3 = "base3"
    base4 = "base4"
    command = "command"
    path = "path"
    optionMenu = "optionmenu"
    list = "list"
    tuple = "tuple"

t = PropertyEditTypes

class Definition:
    def __init__(self,
            internalName,
            visiblename,
            internalType,
            editType=None,
            nullable=False,
            valueOptions=None,
            getFunctionName=None,
            setFunctionName=None,
            addToExtraOptions=False,
            loaderFunc=None,
            postProcessFunctionName=None,
            setAsTag=False,
            lookupAttrs=None):
        # Name to be shown in the editor
        self.visiblename = visiblename

        # Internal name of this property
        self.internalName = internalName

        # Type of this property
        self.type = internalType

        # defines if the value of this property may be None
        self.nullable = nullable

        # The value or values stored in here will be used dependent on the type
        # of property.
        # In case it's a selectable option, the value must be a dictionary
        # consisting of user visible key and code value
        # If it is a runnable command, it should be the name of the function
        # to be called from the element itself
        self.valueOptions = valueOptions


        # Function pointers or names to get and set the desired property
        self.getFunctionName = getFunctionName
        self.setFunctionName = setFunctionName

        # If enabled, the option will be set on the element itself as well as in
        # the elementInfos extraOptions dictionary
        self.addToExtraOptions = addToExtraOptions

        # a function which is passed the value entered in the editor to process
        # it prior to setting it in the property (e.g. loadFont or loadModel)
        self.loaderFunc = loaderFunc

        # a function name which will be called on the element after setting the
        # new value on it
        self.postProcessFunctionName = postProcessFunctionName

        # This can be set to the group of a widget, e.G. the "text" group of a
        # DirectButton to know we're interested in the text_* sub element
        # properties rather than the ones directly available on the root element
        self.elementGroup = ""

        # The edit type defines how the property can be edited in the designer
        if editType is None:
            # if the edit type is not given, try to predict it from values
            # that can definitely be determined
            if self.type == int:
                self.editType = t.integer
            elif self.type == float:
                self.editType = t.float
            elif self.type == bool:
                self.editType = t.bool
            elif self.type == str:
                self.editType = t.text
            elif self.type == list:
                self.editType = t.list
            elif self.type == tuple:
                self.editType = t.tuple
            elif self.type == object:
                self.editType = t.text
            else:
                raise Exception(f"Edit type can not be predicted for type: {self.type}")
        else:
            self.editType = editType

        self.setAsTag = setAsTag
        self.lookupAttrs = lookupAttrs

# definitions for DirectGuiWidget
DEFAULT_DEFINITIONS = [
    Definition('name', 'Name', str, setFunctionName="setName"),
    Definition('pos', 'Position (X/Y/Z)', object, editType=t.base3, nullable=True, getFunctionName="getPos", setFunctionName="setPos"),
    Definition('hpr', 'Rotation (H/P/R)', object, editType=t.base3, nullable=True, getFunctionName="getHpr", setFunctionName="setHpr"),
    Definition('scale', 'Scale (W/H/D)', object, editType=t.base3, nullable=True, getFunctionName="getScale", setFunctionName="setScale"),
    Definition('color', 'Color (R/G/B/A)', object, editType=t.base4, nullable=True, getFunctionName="getColor", setFunctionName="setColor"),
    Definition('transparency', 'Transparency', str, editType=t.optionMenu, valueOptions={"None":TransparencyAttrib.M_none,"Alpha":TransparencyAttrib.M_alpha,"Premultiplied Alpha":TransparencyAttrib.M_premultiplied_alpha,"Multisample":TransparencyAttrib.M_multisample,"Multisample Mask":TransparencyAttrib.M_multisample_mask,"Binary":TransparencyAttrib.M_binary,"Dual":TransparencyAttrib.M_dual}, getFunctionName="getTransparency", setFunctionName="setTransparency")
]

COLLISION_LOOKUP_ATTRS={"node":[], "get_solid":[0]}

DEFINITIONS = {
    #
    # Model
    #
    "model":DEFAULT_DEFINITIONS + [
        Definition('filepath', 'Filepath', str, setAsTag=True),
    ],

    #
    # Empty
    #
    "empty":DEFAULT_DEFINITIONS,

    #
    # Collision definitions
    #
    "CollisionSphere":DEFAULT_DEFINITIONS + [
        Definition('center', 'Center', object, editType=t.base3, setFunctionName="set_center", lookupAttrs=COLLISION_LOOKUP_ATTRS),
        Definition('radius', 'Radius', float, setFunctionName="set_radius", lookupAttrs=COLLISION_LOOKUP_ATTRS),
    ],
    "CollisionBox":DEFAULT_DEFINITIONS + [
        Definition('center', 'Center', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
        Definition('dimension', 'Dimension', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
    ],
    "CollisionPlane":DEFAULT_DEFINITIONS + [
        #Definition('center', 'Center', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
        #Definition('dimension', 'Dimension', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
    ],
    "CollisionCapsule":DEFAULT_DEFINITIONS + [
        Definition('point_a', 'Point A', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
        Definition('point_b', 'Point B', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
        Definition('radius', 'Radius', float, lookupAttrs=COLLISION_LOOKUP_ATTRS),
    ],
    "CollisionLine":DEFAULT_DEFINITIONS + [
        Definition('origin', 'Origin', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
        Definition('direction', 'Direction', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
    ],
    "CollisionSegment":DEFAULT_DEFINITIONS + [
        Definition('point_a', 'Point A', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
        Definition('point_b', 'Point B', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
    ],
    "CollisionRay":DEFAULT_DEFINITIONS + [
        Definition('origin', 'Origin', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
        Definition('direction', 'Direction', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
    ],
    "CollisionInvSphere":DEFAULT_DEFINITIONS + [
        Definition('center', 'Center', object, editType=t.base3, lookupAttrs=COLLISION_LOOKUP_ATTRS),
        Definition('radius', 'Radius', float, lookupAttrs=COLLISION_LOOKUP_ATTRS),
    ],

    #
    # Light
    #
    "light_PointLight":DEFAULT_DEFINITIONS + [
    ]

    #
    # Camera
    #
}
