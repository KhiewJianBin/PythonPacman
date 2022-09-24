import sys
import direct.directbase.DirectStart

from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState

from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode

from direct.stdpy.file import *

from random import randint

class LabTask(DirectObject):

  def __init__(self):
    #setup environment
    self.init()

    # Task
    taskMgr.add(self.update, 'updateWorld')

    # Physics
    self.setup()

  # _____INIT_____
  def init(self):
    base.setBackgroundColor(0.1, 0.1, 0.8, 1)
    base.setFrameRateMeter(True)

    base.cam.setPos(0, -1, 50)
    base.cam.lookAt(0, 0, 0)

    # Input
    self.accept('escape', self.doExit)
    self.accept('r', self.doReset)
    self.accept('f1', self.toggleWireframe)
    self.accept('f2', self.toggleTexture)
    self.accept('f3', self.toggleDebug)
    self.accept('f5', self.doScreenshot)

    inputState.watchWithModifiers('forward', 'w')
    inputState.watchWithModifiers('left', 'a')
    inputState.watchWithModifiers('reverse', 's')
    inputState.watchWithModifiers('right', 'd')

    # Light
    alight = AmbientLight('ambientLight')
    alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
    alightNP = render.attachNewNode(alight)

    dlight = DirectionalLight('directionalLight')
    dlight.setDirection(Vec3(1, 1, -1))
    dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
    dlightNP = render.attachNewNode(dlight)

    render.clearLight()
    render.setLight(alightNP)
    render.setLight(dlightNP)

  #____HANDLER______
  def doExit(self):
      self.cleanup()
      sys.exit(1)

  def doReset(self):
      self.cleanup()
      self.setup()
  
  def toggleWireframe(self):
      base.toggleWireframe()

  def toggleTexture(self):
      base.toggleTexture()
   
  def toggleDebug(self):
      if self.debugNP.isHidden():
          self.debugNP.show()
      else:
          self.debugNP.hide()
  def doScreenshot(self):
      base.screenshot('Bullet')

  # ____TASK___
  def update(self, task):
    dt = globalClock.getDt()
    self.world.doPhysics(dt)
    return task.cont
    
  def cleanup(self):
      self.world.removeRigidBody(self.ground)
      self.world = None

      self.worldNP.removeNode()

  # ____SETUP___
  def setup(self):
    self.worldNP = render.attachNewNode('World')
    self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
    self.debugNP.show()

    # World
    self.world = BulletWorld()
    self.world.setGravity(Vec3(0, 0, -9.81))
    self.world.setDebugNode(self.debugNP.node())

    # Plane
    shape = BulletPlaneShape(Vec3(0, 0, 1), 0.15)

    self.ground = BulletRigidBodyNode('Ground')
    self.ground.addShape(shape)
    np = render.attachNewNode(self.ground)
    np.setPos(0,0,-0.5)
    
    self.world.attachRigidBody(self.ground)
    model = loader.loadModel('Models/floor.egg')
    model.reparentTo(np)

    self.setupMaze()

  def setupMaze(self):    
      Pos = Vec3(-9,-9.5,0.25)
      self.mazeinfo = []
      Mazefile = open("Maze.txt")
      Rowcount = -1;
      for rows in Mazefile.readlines():
        self.mazeinfo.append([])
        Rowcount += 1
        for i in rows:
            if i != '\n':
                if i == '0':
                    self.mazeinfo[Rowcount].append(0)
                else:
                    self.mazeinfo[Rowcount].append(1)

      self.BoxScale = Vec3(0,1,1)
      self.first = False
      self.mazeinfo.reverse() #reverse the list of rows
      for i in range(len(self.mazeinfo)):
        for j in range(len(self.mazeinfo[i])):
            if self.mazeinfo[i][j] == 1:
                self.BoxScale.setX(self.BoxScale.getX()+1)
                if(self.first == False):
                    self.first = True
                    x = j + Pos.getX()
                    y = i + Pos.getY()
                    z = Pos.getZ()
            else:
                CreateBox(Vec3( 0.5*self.BoxScale.getX(), 0.5*self.BoxScale.getY(), 0.5*self.BoxScale.getZ()),Vec3(x,y,z))

  def CreateBox(self,Scale,Pos):
        shape = BulletBoxShape(Scale)
        body = BulletRigidBodyNode()
        bodyNP = self.worldNP.attachNewNode(body)
        bodyNP.node().addShape(shape)
        bodyNP.node().setMass(10000000.0)
        bodyNP.setPos(Pos)
        bodyNP.setCollideMask(BitMask32.allOn())

        self.world.attachRigidBody(bodyNP.node())

        visNP = loader.loadModel('Models/box.egg')
        visNP.clearModelNodes()
        visNP.reparentTo(bodyNP)
        visNP.setScale(Scale)