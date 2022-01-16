from panda3d.core import Point2, Vec3, PerspectiveLens, OrthographicLens

class CameraController:
    def __init__(self):
        #
        # Camera
        #
        # set ortographic lens
        #lens = OrthographicLens()
        #lens.setFilmSize(80, 60)  # Or whatever is appropriate for your scene
        #base.cam.node().setLens(lens)
        self.fov = 90
        base.camLens.setFov(self.fov)

        self.is_orthographic = False

        self.ortho_zoom_size = 90
        self.min_ortho_zoom_size = 10
        self.max_ortho_zoom_size = 180

        self.pivotDefaultH = 30
        self.pivotDefaultP = 30

        # camera movement
        self.mousePos = None
        self.startCameraMovement = False
        self.movePivot = False

        # disable pandas default mouse-camera controls so we can handle the cam
        # movements by ourself
        base.disableMouse()
        # this variable will be used to determine the distance from the player to
        # the camera
        self.camDistance = 75.0
        # min and maximal distance between player and camera
        self.maxCamDistance = 1000.0
        self.minCamDistance = 5.0
        # the speed at which the mousewheel and +/- will zoom the camera in/out
        self.zoomSpeed = 5.0
        # the speed at which the mouse moves the camera
        self.mouseSpeed = 50

        self.pivot = render.attachNewNode("Pivot Point")
        self.pivot.setPos(0, 0, 0)
        self.pivot.setHpr(self.pivotDefaultH, self.pivotDefaultP, 0)
        camera.reparentTo(self.pivot)

        # add the cameras update task so it will be updated every frame
        base.taskMgr.add(self.updateCam, "task_camActualisation", priority=-4)

    def toggle_lense(self):
        if self.is_orthographic:
            lens = PerspectiveLens()
            lens.set_film_size(*base.win.get_size())
            lens.set_fov(self.fov)
            lens.set_near_far(0.1, 1000)
        else:
            lens = OrthographicLens()
            aspect = base.win.get_size()[0] / base.win.get_size()[1]
            lens.setFilmSize(self.ortho_zoom_size*aspect, self.ortho_zoom_size)
            lens.set_near_far(0.001, 1000)
        base.cam.node().set_lens(lens)
        self.is_orthographic = not self.is_orthographic

    def setPivot(self, h, p):
        interval = self.pivot.hprInterval(0.5, Vec3(h, p, 0))
        interval.start()

    def resetPivotDefault(self):
        self.setPivot(self.pivotDefaultH, self.pivotDefaultP)

    def setPivotLeft(self):
        self.setPivot(270, 0)

    def setPivotRight(self):
        self.setPivot(90, 0)

    def setPivotFront(self):
        self.setPivot(0, 0)

    def setPivotBack(self):
        self.setPivot(180, 0)

    def setPivotTop(self):
        self.setPivot(0, 90)

    def setPivotBottom(self):
        self.setPivot(0, -90)

    def setMoveCamera(self, moveCamera):
        # store the mouse position if weh have a mouse
        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
            self.mousePos = Point2(x, y)
        # set the variable according to if we want to move the camera or not
        self.startCameraMovement = moveCamera

    def setMovePivot(self, movePivot):
        self.movePivot = movePivot

    def setAndMovePivot(self, move):
        self.setMovePivot(move)
        self.setMoveCamera(move)

    #
    # CAMERA SPECIFIC FUNCTIONS
    #
    def zoom(self, zoomIn):
        if not self.is_orthographic:
            if zoomIn:
                # check if we are far enough away to further zoom in
                if self.camDistance > self.minCamDistance:
                    # zoom in by a given speed
                    self.camDistance -= self.zoomSpeed
            else:
                # check if we are close enough to further zoom out
                if self.camDistance < self.maxCamDistance:
                    # zoom out by a given speed
                    self.camDistance += self.zoomSpeed
        else:
            aspect = base.win.get_size()[0] / base.win.get_size()[1]

            if zoomIn:
                self.ortho_zoom_size -= 1
                if self.ortho_zoom_size < self.min_ortho_zoom_size:
                    self.ortho_zoom_size = self.min_ortho_zoom_size
            else:
                self.ortho_zoom_size += 1
                if self.ortho_zoom_size > self.max_ortho_zoom_size:
                    self.ortho_zoom_size = self.max_ortho_zoom_size

            lens = base.cam.node().get_lens()
            lens.setFilmSize(self.ortho_zoom_size*aspect, self.ortho_zoom_size)

    def reset_zoom(self):
        self.camDistance = 75.0

    def updateCam(self, task):
        # variables to store the mouses current x and y position
        x = 0.0
        y = 0.0
        if base.mouseWatcherNode.hasMouse():
            # get the mouse position
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
        if base.mouseWatcherNode.hasMouse() \
        and self.mousePos is not None \
        and self.startCameraMovement:
            # Move the camera if the left mouse key is pressed and the mouse moved
            mouseMoveX = (self.mousePos.getX() - x) * (self.mouseSpeed + globalClock.getDt())
            mouseMoveY = (self.mousePos.getY() - y) * (self.mouseSpeed + globalClock.getDt())
            self.mousePos = Point2(x, y)

            if not self.movePivot:
                # Rotate the pivot point
                preP = self.pivot.getP()
                self.pivot.setP(0)
                self.pivot.setH(self.pivot, mouseMoveX)
                self.pivot.setP(preP)
                self.pivot.setP(self.pivot, mouseMoveY)
            else:
                # Move the pivot point
                self.pivot.setX(self.pivot, -mouseMoveX)
                self.pivot.setZ(self.pivot, mouseMoveY)

        # set the cameras zoom
        camera.setY(self.camDistance)

        # always look at the pivot point
        camera.lookAt(self.pivot)

        # continue the task until it got manually stopped
        return task.cont
