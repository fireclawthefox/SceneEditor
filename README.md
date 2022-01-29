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

Basics
Ctrl-Q - Quit the editor
Ctrl-N - New Scene
Ctrl-O - Open Scene from JSON format
Ctrl-S - Save Scene to JSON format
Ctrl-E - Export Scene to Python format

Navigation in the scene is similar to Blender in that you can move around with the mouse.
Rotate around pivot - Middle mouse button
Pan - Shift + Middle mouse button
Zoom - mouse wheel
Select - Left mouse button
Multiselect - Shift + Left mouse button
Ctrl-G - Toggle grid
5 - Toggle Perspective/Orthographic lense
7 - Show top
Ctrl-7 - Show bottom
1 - Show front
Ctrl-1 - Show back
3 - Show right
Ctrl-3 - Show left

Editing shortcuts:
G - Move selected objects
R - Rotate selected objects around objects center
S - Scale selected objects
X, Y and Z - During moving and rotating clips to the respective axis
Del - Remove objects
Ctrl-Z - Undo
Ctrl-Y - Redo
Ctrl-Shift-Y - Switch between redo branches
C - Show collision solids
H - Toggle model hidden status
Ctrl-C - Copy
Ctrl-X - Cut
Ctrl-V - Paste (makes last selected object parent or render if none is selected)
Page Up - Increase objects sort value
Page Down - Decrease objects sort value

## WIP
Not all values will be saved and loaded yet
Property editor is heavily work in progress
