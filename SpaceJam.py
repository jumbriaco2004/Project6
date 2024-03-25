from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from CollideObjectBase import PlacedObject
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import Vec3
from panda3d.core import TransparencyAttrib
import DefensePaths as defensePaths
import SpaceJamClasses as spaceJamClasses
import math, random

class SpaceJam(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.SetupScene()
        self.SetCamera()
        self.EnableHud()

    def SetupScene(self):
        self.cTrav = CollisionTraverser()
        
        self.Universe = spaceJamClasses.Universe(self.loader, "./Assets/Universe/Universe.obj", self.render, "Universe", "./Assets/Universe/starfield-in-blue.jpg", (0, 0, 0), 10000)
        self.Planet1 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet1", "Assets/Planets/planet1.jpg", (150, 5000, 67), 350)
        self.Planet2 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet2", "Assets/Planets/planet2.jpg", (5000, 5000, 100), 350)
        self.Planet3 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet3", "Assets/Planets/planet3.jpg", (5000, 100, -500), 350)
        self.Planet4 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet4", "Assets/Planets/planet4.jpg", (3000, 1000, 1000), 350)
        self.Planet5 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet5", "Assets/Planets/planet5.jpg", (-1000, 2000, 200), 350)
        self.Planet6 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet6", "Assets/Planets/planet6.jpg", (1000, 3000, -300), 350)
        self.SpaceStation1 = spaceJamClasses.SpaceStation(self.loader, "./Assets/Space Station/spaceStation.x", self.render, "Space Station", (1000, 500, 0), (0, 90, 0), 10)
        self.Player = spaceJamClasses.Player(self.loader, "./Assets/Spaceships/theBorg2.x", self.render, "Player", "./Assets/Spaceships/theBorg.jpg", (100, 100, 0), 2, self.taskMgr, self.render, self.accept, self.cTrav)
 
        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.Player.collisionNode, self.Player.modelNode)
        self.cTrav.traverse(self.render)
        self.cTrav.addCollider(self.Player.collisionNode, self.pusher)
        self.cTrav.showCollisions(self.render)

        #Setting Drones
        spaceJamClasses.Drone.droneCount += 1
        droneName = "Drone" + str(spaceJamClasses.Drone.droneCount)
        centralObject = self.SpaceStation1.modelNode.getPos()

        self.DrawCloudDefense(centralObject, droneName)
        self.DrawBaseballSeams(centralObject, droneName, 2, 60)
        self.DrawCircleXYDefense(centralObject, droneName, radius = 300, numDrones = 30)
        self.DrawCircleXZDefense(centralObject, droneName, radius = 300, numDrones = 30)
        self.DrawCircleYZDefense(centralObject, droneName, radius = 300, numDrones = 30)



    def DrawCloudDefense(self, centralObject, droneName):
        fullCycle = 60
        for j in range(fullCycle):
            unitVec = defensePaths.Cloud()
            unitVec.normalize()
            position = unitVec * 500 + centralObject
            spaceJamClasses.Drone(self.loader, "./Assets/Drone Defender/DroneDefender.obj", self.render, droneName, "./Assets/Drone Defender/octotoad1_auv.png", position, 10)

    def DrawBaseballSeams(self, centralObject, droneName, step, numSeams, radius = 1):
        for i in range(numSeams):
            unitVec = defensePaths.BaseballSeams(step * i, numSeams, B = 0.4)
            unitVec.normalize()
            position = unitVec * radius * 250 + centralObject
            spaceJamClasses.Drone(self.loader, "./Assets/Drone Defender/DroneDefender.obj", self.render, droneName, "./Assets/Drone Defender/octotoad1_auv.png", position, 10)

    def DrawCircleXYDefense(self, centralObject, droneName, radius=50.0, numDrones=30):
        points = defensePaths.CircleXY(radius, numDrones)
        for i, point in enumerate(points):
            posVec = point + centralObject
            spaceJamClasses.Drone(self.loader, "./Assets/Drone Defender/DroneDefender.obj", self.render, droneName, "./Assets/Drone Defender/octotoad1_auv.png", posVec, 10)

    def DrawCircleXZDefense(self, centralObject, droneName, radius = 50.0, numDrones = 30):
        points = defensePaths.CircleXZ(radius, numDrones)
        for i, point in enumerate(points):
            posVec = point + centralObject
            spaceJamClasses.Drone(self.loader, "./Assets/Drone Defender/DroneDefender.obj", self.render, droneName, "./Assets/Drone Defender/octotoad1_auv.png", posVec, 10)

    def DrawCircleYZDefense(self, centralObject, droneName, radius = 50.0, numDrones = 30):
        points = defensePaths.CircleYZ(radius, numDrones)
        for i, point in enumerate(points):
            posVec = point + centralObject
            spaceJamClasses.Drone(self.loader, "./Assets/Drone Defender/DroneDefender.obj", self.render, droneName, "./Assets/Drone Defender/octotoad1_auv.png", posVec, 10)
    
    def SetCamera(self):
        self.disableMouse()
        self.camera.setPos(0, -100, 0)
        self.camera.reparentTo(self.Player.modelNode)

    def EnableHud(self):
        self.Hud = OnscreenImage(image = "./Assets/Hud/Reticle3b.png", pos = Vec3(0, 0, 0), scale = 0.1)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)

play = SpaceJam()
play.run()