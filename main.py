from direct.showbase.ShowBase import ShowBase
from SceneEditor.SceneEditor import SceneEditor

base = ShowBase()

SceneEditor(base.pixel2d)

base.run()
