# SceneEditor
A simple Scene editor for the Panda3D game engine

## Requirements
- Python 3.x
- Panda3D 1.10.4.1+
- DirectFolderBrowser
- DirectGuiExtension

To install them, using pip:
<code>pip install -r requirements.txt</code>

## How to use
NOTE: Currently the editor is heavily work in progress so things may change later

Navigation in the scene is similar to Blender in that you can move around with the mouse.
Rotate around pivot - Middle mouse button
Pan - Shift + Middle mouse button
Zoom - mouse wheel
Select - Left mouse button
Multiselect - Shift + Left mouse button

Editing shortcuts:
G - Move selected objects
R - Rotate selected objects around objects center
X, Y and Z - During moving and rotating clips to the respective axis
Del - Remove objects
Ctrl-U - Undo
C - Show collision solids
H - Toggle model hidden status

## WIP
Kill cycle
currently undo works but redo does not yet. Hence also the switching between redo and undo branches won't work

## Planed Features
- Scaling objects
- Adding other objects like lights, cameras, empty nodes, etc.
- Property editing of objects in the scene
