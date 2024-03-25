from direct.task import Task
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from CollideObjectBase import *
from panda3d.core import CollisionHandlerEvent
from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect
from panda3d.core import Filename
#Regex module import for string editing
import re

class Universe(InverseSphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Universe, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), .9)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

class Planet(SphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Planet, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 1.1)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.collisionNode.show()

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

class SpaceStation(CapsuleCollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, Hpr: Vec3 , scaleVec: float):
        super(SpaceStation, self).__init__(loader, modelPath, parentNode, nodeName, 2, -1, 5, 1, -1, -5, 20)
        self.modelNode.setPos(posVec)
        self.modelNode.setHpr(Hpr)
        self.modelNode.setScale(scaleVec)
        self.collisionNode.show()
        
class Player(SphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float, taskMgr, render, accept, traverser):
        super(Player, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 10) #Changes radius value of drone
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

        self.collisionNode.show()

        self.taskMgr = taskMgr
        self.render = render
        self.accept = accept

        self.reloadTime = .25
        self.missileDistance = 1000
        self.missileBay = 1

        self.SetParticles()

        self.SetKeyBindings()

        #Checks Intervals Dictionary
        self.taskMgr.add(self.CheckIntervals, "checkMissiles", 34)

        self.cntExplode = 0
        self.explodeIntervals = {}

        self.traverser = traverser
        self.handler = CollisionHandlerEvent()

        self.handler.addInPattern('into')
        self.accept('into', self.HandleInto)

    def HandleInto(self, entry):
        fromNode = entry.getFromNodePath().getName()
        print("fromNode: " + fromNode)
        intoNode = entry.getIntoNodePath().getName()
        print("intoNode: " + intoNode)
        intoPosition = Vec3(entry.getSurfacePoint(self.render))

        tempVar = fromNode.split('_')
        shooter = tempVar[0]
        tempVar = intoNode.split('-')
        tempVar = intoNode.split('_')
        victim = tempVar[0]
        
        pattern = r'[0-9]'
        strippedString = re.sub(pattern, '', victim)

        if (strippedString == "Drone"):
            print(shooter + ' is DONE.')
            Missile.Intervals[shooter].finish()
            print(victim, ' hit at ', intoPosition)
            self.DroneDestroy(victim, intoPosition)
        else:
            Missile.Intervals[shooter].finish()

    def DroneDestroy(self, hitID, hitPosition):
        nodeID = self.render.find(hitID)
        nodeID.detachNode()

        self.explodeNode.setPos(hitPosition)
        self.Explode(hitPosition)

    def Explode(self, impactPoint):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, fromData = 0, toData = 1, duration = 4.0, extraArgs = [impactPoint])
        self.explodeIntervals[tag].start()

    def ExplodeLight(self, t, explosionPosition):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()
        elif t == 0:
            self.explodeEffect.start(self.explodeNode)

    def SetParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        #self.explodeEffect.loadConfig("./Assets/ParticleEffects/Explosions/basic_xpld_efx.ptf")

        self.explodeEffect.setScale(20)
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')
    
    def Fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward()) #The direction the ship is facing
            aim.normalize()

            fireSolution = aim * travRate
            inFront = aim * 150
            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = "Missle" + str(Missile.missileCount)
            posVec = self.modelNode.getPos() + inFront #Spawns missile in front of the nose of the ship
            currentMissile = Missile(loader, "./Assets/Phaser/phaser.egg", self.render, tag, posVec, 4.0) #Create our missile
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            Missile.Intervals[tag].start()
            self.traverser.addCollider(currentMissile.collisionNode, self.handler)
        else:
            #When we're not reloading, start reloading
            if not self.taskMgr.hasTaskNamed("reload"):
                print("Initializing reload...")
                self.taskMgr.doMethodLater(0, self.Reload, "reload")
                return Task.cont
            
    def Reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 1
            print ("Reload Complete.")
            return Task.done
        if self.missileBay > 1:
            self.missileBay = 1
        elif task.time <= self.reloadTime:
            print("Reload proceeding...")
            return Task.cont
    
    def CheckIntervals(self, task):
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying():
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()
                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]
                print(i + " has reached the end of its fire solution") #Debugging
                break
        return Task.cont
        
    def SetKeyBindings(self):
        self.accept("space", self.Thrust, [1])
        self.accept("space-up", self.Thrust, [0])
        self.accept("a", self.LeftTurn, [1])
        self.accept("a-up", self.LeftTurn, [0])
        self.accept("d", self.RightTurn, [1])
        self.accept("d-up", self.RightTurn, [0])
        self.accept("w", self.UpTurn, [1])
        self.accept("w-up", self.UpTurn, [0])
        self.accept("s", self.DownTurn, [1])
        self.accept("s-up", self.DownTurn, [0])
        self.accept("e", self.RightRoll, [1])
        self.accept("e-up", self.RightRoll, [0])
        self.accept("q", self.LeftRoll, [1])
        self.accept("q-up", self.LeftRoll, [0])
        self.accept('f', self.Fire)

    def Thrust(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyThrust, "forward-thrust")
        else:
            self.taskMgr.remove("forward-thrust")

    def ApplyThrust(self, task):
        rate = 5
        trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()
        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)
        return Task.cont
    
    def LeftTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyLeftTurn, "left-turn")
        else:
            self.taskMgr.remove("left-turn")

    def ApplyLeftTurn(self, task):
        rate = .5
        self.modelNode.setH(self.modelNode.getH() + rate)
        return Task.cont
    
    def RightTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRightTurn, "right-turn")
        else:
            self.taskMgr.remove("right-turn")

    def ApplyRightTurn(self, task):
        rate = .5
        self.modelNode.setH(self.modelNode.getH() - rate)
        return Task.cont
    
    def UpTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyUpTurn, "up-turn")
        else:
            self.taskMgr.remove("up-turn")

    def ApplyUpTurn(self, task):
        rate = .5
        self.modelNode.setP(self.modelNode.getP() + rate)
        return Task.cont
    
    def DownTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyDownTurn, "down-turn")
        else:
            self.taskMgr.remove("down-turn")

    def ApplyDownTurn(self, task):
        rate = .5
        self.modelNode.setP(self.modelNode.getP() - rate)
        return Task.cont
    
    def RightRoll(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRightRoll, "right-roll")
        else:
            self.taskMgr.remove("right-roll")

    def ApplyRightRoll(self, task):
        rate = .5
        self.modelNode.setR(self.modelNode.getR() + rate)
        return Task.cont
    
    def LeftRoll(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyLeftRoll, "left-roll")
        else:
            self.taskMgr.remove("left-roll")

    def ApplyLeftRoll(self, task):
        rate = .5
        self.modelNode.setR(self.modelNode.getR() - rate)
        return Task.cont

class Drone(SphereCollideObject):
    droneCount = 0
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Drone, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

class Missile(SphereCollideObject):
    fireModels = {}
    cNodes = {}
    collisionSolids = {}
    Intervals = {}
    missileCount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float = 1.0):
        super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3.0)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setPos(posVec)

        Missile.missileCount += 1
        Missile.fireModels[nodeName] = self.modelNode
        Missile.cNodes[nodeName] = self.collisionNode

        #Debugging
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        Missile.cNodes[nodeName].show()
        print("Fire missile #" + str(Missile.missileCount))