from direct.showbase.InputStateGlobal import inputState

from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import BitMask32

from panda3d.bullet import BulletCylinderShape
from panda3d.bullet import BulletRigidBodyNode

from panda3d.core import TransparencyAttrib

from AStar import node
from Game1 import *
from KinematicSteering import *

from heapq import heappush, heappop # for priority queue
import random
import copy

pacmove = base.loader.loadSfx("Sounds/pacmove.wav")
pacmove.setLoop(True)

class PacGame(Game1):
  def __init__(self):

    self.isinMenu = True
    self.IsGamePaused = True
    self.IsGameEnd = False

    self.IsStartMusic = False

    self.GameScore = 0
    self.GameTimer = 0
    self.GameTimerLimit = 300

    self.PlayerLives = 3
    self.canRespawn = False

    self.IsPlayerPowerUp = False

    self.PowerUpTimer = 0
    self.PowerUpLimit = 5

    self.ScoreText = OnscreenText(text ='Score:'+str(self.GameScore), pos = (1.0, 0.8), scale = 0.1, frame = Vec4(1,1,1,1) , fg = Vec4(1,1,1,1) ,bg = Vec4(0.396,0.611,0.937,0.4))
    self.TimerText = OnscreenText(text ='Timer:'+str(self.GameTimer), pos = (-1.1, 0.8), scale = 0.1, frame = Vec4(1,1,1,1), fg = Vec4(1,1,1,1) ,bg = Vec4(0.396,0.611,0.937,0.4))
    self.LivesText = OnscreenText(text ='Lifes:'+str(self.PlayerLives), pos = (-0.1, 0.8), scale = 0.1, frame = Vec4(1,1,1,1), fg = Vec4(1,1,1,1) ,bg = Vec4(0.396,0.611,0.937,0.4))
    self.PauseText = OnscreenText(text ='[Game [P]ause]', pos = (-0.1, 0.0), scale = 0.1, frame = Vec4(1,1,1,1), fg = Vec4(1,1,1,1) ,bg = Vec4(0.396,0.611,0.937,0.4))
    self.PauseText.hide()
    self.PlayerSpawnText = OnscreenText(text ='Press [Space] To Spawn', pos = (0.0, 0.6), scale = 0.1, frame = Vec4(1,1,1,1), fg = Vec4(1,1,1,1) ,bg = Vec4(0.396,0.611,0.937,0.4))
    self.PlayerSpawnText.hide()
    self.GameOverText = OnscreenText(text ='GameOver\nScore:'+str(self.GameScore), pos = (-0.1, 0.4), scale = 0.1, frame = Vec4(1,1,1,1), fg = Vec4(1,1,1,1) ,bg = Vec4(0.396,0.611,0.937,0.4))
    self.GameOverText.hide()
    Game1.__init__(self)
  def setupPlayer(self):
        self.PlayerStates = ["Up","Down","Left","Right","None"]
        self.Playerstate = self.PlayerStates[4]
        self.PrevPlayerstate = self.PlayerStates[4]
        self.IsPlayerAlive = True
        self.IsPlayerCollided = False
        self.IsPlayerPowerUp = False
        shape = BulletSphereShape(0.499)
        #shape = BulletBoxShape(Vec3( 0.5, 0.5, 0.5))
        body = BulletRigidBodyNode()
        bodyNP = self.worldNP.attachNewNode(body)
        bodyNP.node().addShape(shape)
        bodyNP.node().setMass(1.0)
        bodyNP.setPos(Vec3(10.5,1.5,0.25))
        bodyNP.setHpr(Vec3(180,0,0))
        bodyNP.setCollideMask(BitMask32(0x10))

        self.world.attachRigidBody(bodyNP.node())

        visNP = loader.loadModel('smiley')
        visNP.clearModelNodes()
        visNP.reparentTo(bodyNP)
        visNP.setScale(0.5, 0.5, 0.5)

        self.pacman = bodyNP

        self.pacman.node().setActive(False)
  def SpawnPlayer(self,pos= Vec3(10.5,1.5,0.25)):
       self.pacman.setPos(pos)
       self.pacman.setHpr(Vec3(180,0,0))
       self.PlayerSpawnText.hide()
       self.IsPlayerAlive = True
       self.IsPlayerCollided = False
       self.IsPlayerPowerUp = False
       self.canRespawn = False
       self.PlayerLives -= 1
  def KillPlayer(self):
       self.pacman.setPos(Vec3(10000,10000,0.25))
       self.IsPlayerAlive = False
       pacmove.stop()
       if(self.PlayerLives == 0):
           self.ENDGAME()
       else:
           self.canRespawn = True
           self.PlayerSpawnText.show()  
  def ENDGAME(self):
       pacmove.stop()
       self.IsGamePaused = True
       self.IsGameEnd = True
       self.GameOverText.setText('GameOver\nScore:'+str(self.GameScore))
       self.GameOverText.show()     
  def UpdatePacman(self):
        if(self.IsPlayerAlive):
            #UpdatePlayer
            Velocity = Vec3(0,0,0)
            self.pacman.node().setActive(True)
            if self.Playerstate == "Up":
                self.PrevPlayerstate = self.Playerstate
                if pacmove.status() == pacmove.READY:
                    pacmove.play()
                Velocity = Vec3(0,5.5,0)
                self.pacman.setX(self.roundHint(self.pacman.getX()))      
                if(Game1.IsCharUp(self,self.pacman.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                   Velocity = Vec3(0,0,0)
                   self.pacman.setX(self.roundHint(self.pacman.getX()))
                   self.pacman.setY(self.roundHint(self.pacman.getY()))
                   self.Playerstate = "None"

            elif self.Playerstate == "Down":
                self.PrevPlayerstate = self.Playerstate
                if pacmove.status() == pacmove.READY:
                    pacmove.play()
                Velocity = Vec3(0,-5.5,0)
                self.pacman.setX(self.roundHint(self.pacman.getX())) 
                if(Game1.IsCharDown(self,self.pacman.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                   Velocity = Vec3(0,0,0)
                   self.pacman.setX(self.roundHint(self.pacman.getX()))
                   self.pacman.setY(self.roundHint(self.pacman.getY()))
                   self.Playerstate = "None"
                                           
            elif self.Playerstate == "Left":
                self.PrevPlayerstate = self.Playerstate
                if pacmove.status() == pacmove.READY:
                    pacmove.play()
                Velocity = Vec3(-5.5,0,0)
                self.pacman.setY(self.roundHint(self.pacman.getY()))
                if(Game1.IsCharLeft(self,self.pacman.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                    Velocity = Vec3(0,0,0)
                    self.pacman.setX(self.roundHint(self.pacman.getX()))
                    self.pacman.setY(self.roundHint(self.pacman.getY()))
                    self.Playerstate = "None"
            elif self.Playerstate == "Right":
                self.PrevPlayerstate = self.Playerstate
                if pacmove.status() == pacmove.READY:
                    pacmove.play()                     
                Velocity = Vec3(5.5,0,0)
                self.pacman.setY(self.roundHint(self.pacman.getY())) 
                if(Game1.IsCharRight(self,self.pacman.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                   Velocity = Vec3(0,0,0)
                   self.pacman.setX(self.roundHint(self.pacman.getX()))
                   self.pacman.setY(self.roundHint(self.pacman.getY()))
                   self.Playerstate = "None"
            
            elif self.Playerstate == "None":  
                #print "Press WASD"  
                if pacmove.status() == pacmove.PLAYING:
                   pacmove.stop()
                            
            if(self.lastkeypress == 'W'):
                if(self.PrevPlayerstate == "Down"):
                    Velocity = Vec3(0,0,0)                  
                    self.Playerstate = "Up"
                elif(self.PrevPlayerstate != "Up"):
                    if(self.roundHint(self.pacman.getX()) != int(self.roundHint(self.pacman.getX()))):
                        if(Game1.IsCharUp(self,self.pacman.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                            Velocity = Vec3(0,0,0)                  
                            self.Playerstate = "Up"
                self.lastkeypress = 'None'

            elif(self.lastkeypress == 'S'):
                if(self.PrevPlayerstate == "Up"):
                    Velocity = Vec3(0,0,0)                  
                    self.Playerstate = "Down"
                elif(self.PrevPlayerstate != "Down"):
                    if(self.roundHint(self.pacman.getX()) != int(self.roundHint(self.pacman.getX()))):
                        if(Game1.IsCharDown(self,self.pacman.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                            Velocity = Vec3(0,0,0)                 
                            self.Playerstate = "Down"
                self.lastkeypress = 'None'

            elif(self.lastkeypress == 'A'):
                if(self.PrevPlayerstate == "Right"):
                    Velocity = Vec3(0,0,0)
                    self.Playerstate = "Left"
                elif(self.PrevPlayerstate != "Left"):
                    if(self.roundHint(self.pacman.getY()) != int(self.roundHint(self.pacman.getY()))):
                        if(Game1.IsCharLeft(self,self.pacman.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                            Velocity = Vec3(0,0,0)
                            self.Playerstate = "Left"
                self.lastkeypress == 'None'

            elif(self.lastkeypress == 'D'):
                if(self.PrevPlayerstate == "Left"):
                    Velocity = Vec3(0,0,0)                
                    self.Playerstate = "Right"
                elif(self.PrevPlayerstate != "Right"):
                    if(self.roundHint(self.pacman.getY()) != int(self.roundHint(self.pacman.getY()))):
                        if(Game1.IsCharRight(self,self.pacman.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                            Velocity = Vec3(0,0,0)                
                            self.Playerstate = "Right"
                self.lastkeypress = 'None'

            self.pacman.node().setLinearVelocity(Velocity)   
  def SetupGameControls(self):
        inputState.watchWithModifiers('forward','w')
        inputState.watchWithModifiers('reverse','s')
        inputState.watchWithModifiers('left','a')
        inputState.watchWithModifiers('right','d')

        inputState.watchWithModifiers('spawn','space')
        inputState.watchWithModifiers('pause','p')
        
        inputState.watchWithModifiers('debugkey1','9')
        inputState.watchWithModifiers('debugkey2','0')
  def roundHint(self,val):
      return round(2*val)/2.0
  def cleanup(self):
    Game1.cleanup(self)
  def processInput(self, dt):
    self.lastkeypress = 'None'
    if inputState.isSet('forward'): self.lastkeypress = 'W'
    if inputState.isSet('reverse'): self.lastkeypress = 'S'
    if inputState.isSet('right'):   self.lastkeypress = 'D'
    if inputState.isSet('left'):    self.lastkeypress = 'A'
  def togglepausegame(self):
      if self.IsGamePaused:
          self.IsGamePaused = False
          self.PauseText.hide()
          pacmove.play()
      else:
          self.IsGamePaused = True
          self.PauseText.show()
          if pacmove.status() == pacmove.PLAYING:
              pacmove.stop()
  def nothing(self):
      a=1
  def update(self, task):
    if self.isinMenu:
        if(self.Gamestate == "Playing"):
            self.SetupGameControls()

            self.map = Map(self.world,self.mazeinfo)

            self.setupPlayer()

            self.gamebg = base.loader.loadSfx("Sounds/gamestart.wav")
            self.gamebg.play()
            self.IsStartMusic = True

            self.Ghosts = GhostGroup(self.world,self.map,self.mazeinfo,3)

            self.Pacdots = PacDotsGroup(self.world)

            self.PowerUps = PowerUpGroup(self.world)

            self.isinMenu = False
    else:
        if(self.IsGameEnd == False):
            if (self.IsStartMusic):
                if (self.gamebg.status() != self.gamebg.PLAYING):
                    self.IsGamePaused = False
                    self.IsStartMusic = False
            elif (self.IsGamePaused == False):
                dt = globalClock.getDt()
                self.processInput(dt)

                #Update Text
                self.ScoreText.setText('Score:'+str(self.GameScore))
                self.TimerText.setText('Timer:'+str(int(self.GameTimer)))                
                self.LivesText.setText('Lifes:'+str(self.PlayerLives))

                self.GameTimer += dt
                if(self.GameTimer>= self.GameTimerLimit):
                    self.ENDGAME()
                
                #updatePlayer
                self.UpdatePacman()

                #UpdateGhosts
                self.Ghosts.updateall(dt,self.pacman.getPos(),self.IsPlayerAlive,self.IsPlayerPowerUp,self.pacman)
                if (self.Ghosts.PlayerCollision and self.IsPlayerPowerUp == False):
                    self.KillPlayer()

                #UpdatePacdots
                self.GameScore = self.Pacdots.Update(self.pacman,self.GameScore)
                if (self.Pacdots.havepacdot == False):
                    self.ENDGAME()

                #Update PowerUps
                if (self.PowerUps.Update(self.pacman)):
                    self.IsPlayerPowerUp = True
                    self.PowerUpTimer = 0

                if (self.IsPlayerPowerUp):
                    self.PowerUpTimer += dt
                    if(self.PowerUpTimer >= self.PowerUpLimit):
                        self.IsPlayerPowerUp = False
                        self.PowerUpTimer = 0

                Game1.update(self,task)

                if(self.IsPlayerAlive == False):
                    if(self.canRespawn):
                        self.acceptOnce('space',self.SpawnPlayer)

                #Pause Press
                self.accept('p',self.togglepausegame)
            else:
                #Pause Press
                self.acceptOnce('space',self.nothing)
                if(self.IsPlayerAlive):
                    self.acceptOnce('p',self.togglepausegame)              
        else:
            print ("Game Ended")
            self.acceptOnce('space',self.nothing)
            self.acceptOnce('p',self.nothing)

    return task.cont

class PacDotsGroup:
    def __init__(self,world):
        self.world = world
        self.pacdots = []
        self.havepacdot = True
        for i in range(10):
            self.pacdots.append(PacDots())
        self.pacdots[0].SetupPacDot(world,Vec3(1.5,10.5,0.25),Vec3(0.2,0.2,0.2))
        self.pacdots[1].SetupPacDot(world,Vec3(19.5,10.5,0.25),Vec3(0.2,0.2,0.2))
        self.pacdots[2].SetupPacDot(world,Vec3(10.5,4.5,0.25),Vec3(0.2,0.2,0.2))
        self.pacdots[3].SetupPacDot(world,Vec3(10.5,16.5,0.25),Vec3(0.2,0.2,0.2))
        self.pacdots[4].SetupPacDot(world,Vec3(6.5,10.5,0.25),Vec3(0.2,0.2,0.2))
        self.pacdots[5].SetupPacDot(world,Vec3(13.5,10.5,0.25),Vec3(0.2,0.2,0.2))

        self.pacdots[6].SetupPacDot(world,Vec3(6.5,6.5,0.25),Vec3(0.2,0.2,0.2))
        self.pacdots[7].SetupPacDot(world,Vec3(14.5,6.5,0.25),Vec3(0.2,0.2,0.2))
        self.pacdots[8].SetupPacDot(world,Vec3(6.5,14.5,0.25),Vec3(0.2,0.2,0.2))
        self.pacdots[9].SetupPacDot(world,Vec3(14.5,14.5,0.25),Vec3(0.2,0.2,0.2))
    def Update(self,pacman,gamescore):
        if(len(self.pacdots) == 0):
            self.havepacdot = False
        for i in xrange(len(self.pacdots)-1, -1, -1):
            self.pacdots[i].Update(self.world,pacman)
            if (self.pacdots[i].isAlive == False):
                self.pacdots.pop(i)
                gamescore += 10
        return gamescore
class PacDots:
    def __init__(self):
        self.isEaten = False
        self.isAlive = False
    def SetupPacDot(self,world,pos,scale):
        shape = BulletSphereShape(scale.getX())
        node = BulletRigidBodyNode()

        self.pacdot = render.attachNewNode(node)
        self.pacdot.setPos(pos)
        self.pacdot.setCollideMask(BitMask32.allOff()) 
        self.pacdot.node().setMass(0.0)
        self.pacdot.node().addShape(shape)

        world.attachRigidBody(node)

        visnp = loader.loadModel('frowney')
        visnp.setScale(scale)
        visnp.reparentTo(self.pacdot)

        self.isAlive = True
    def Update(self,world,pacman):
        if (self.isAlive):
            result = world.contactTestPair(self.pacdot.node(), pacman.node())
            if result.getNumContacts() > 0:
                self.isEaten = True
                world.removeRigidBody(self.pacdot.node())   
                self.pacdot.removeNode()   
                self.isAlive = False  
class PowerUpGroup:
    def __init__(self,world):
        self.world = world
        self.powerups = []
        for i in range(4):
            self.powerups.append(PowerUp())
        self.powerups[0].SetupPowerUp(world,Vec3(1.5,1.5,0.25),Vec3(0.5,0.5,0.5))
        self.powerups[1].SetupPowerUp(world,Vec3(19.5,1.5,0.25),Vec3(0.5,0.5,0.5))
        self.powerups[2].SetupPowerUp(world,Vec3(1.5,19.5,0.25),Vec3(0.5,0.5,0.5))
        self.powerups[3].SetupPowerUp(world,Vec3(19.5,19.5,0.25),Vec3(0.5,0.5,0.5))
    def Update(self,pacman):
        for i in xrange(len(self.powerups)-1, -1, -1):
            self.powerups[i].Update(self.world,pacman)
            if (self.powerups[i].isAlive == False):
                self.powerups.pop(i)
                return True
        return False
class PowerUp:
    def __init__(self):
        self.isEaten = False
        self.isAlive = False
    def SetupPowerUp(self,world,pos,scale):
        shape = BulletSphereShape(scale.getX())
        node = BulletRigidBodyNode()

        self.PowerUp = render.attachNewNode(node)
        self.PowerUp.setPos(pos)
        self.PowerUp.setCollideMask(BitMask32.allOff()) 
        self.PowerUp.node().setMass(0.0)
        self.PowerUp.node().addShape(shape)

        world.attachRigidBody(node)

        visnp = loader.loadModel('frowney')
        visnp.setScale(scale)
        visnp.reparentTo(self.PowerUp)

        self.isAlive = True
    def Update(self,world,pacman):
        if (self.isAlive):
            result = world.contactTestPair(self.PowerUp.node(), pacman.node())
            if result.getNumContacts() > 0:
                self.isEaten = True
                world.removeRigidBody(self.PowerUp.node())   
                self.PowerUp.removeNode()   
                self.isAlive = False  

class GhostGroup:
    def __init__(self,world,themap,inmazeinfo,numofghost):
        self.Ghostgrp = []
        for i in range(numofghost):
            self.Ghostgrp.append(GhostStateMachine(themap,inmazeinfo))
        self.Ghostgrp[0].initGhost(world,Vec3(9.5,10.5,0.25),Vec3(0.7,0.7,0.7),BitMask32(0x01))
        self.Ghostgrp[1].initGhost(world,Vec3(10.5,10.5,0.25),Vec3(0.7,0.7,0.7),BitMask32(0x02))
        self.Ghostgrp[2].initGhost(world,Vec3(11.5,10.5,0.25),Vec3(0.7,0.7,0.7),BitMask32(0x04))
        self.numofGhostAlive = 0
        self.maxGhost = numofghost
        self.spawnDelay = 10.0
        self.spawnTimer = 0.0
        
        self.world = world

        self.PlayerCollision = False
    def updateall(self,dt,targetPos,IsPlayerAlive,IsPlayerPowerUp,pacman):
        self.PlayerCollision = False
        for i in range(len(self.Ghostgrp)):
            #Spawn Dead Ghosts
            if self.numofGhostAlive != self.maxGhost:
                if self.Ghostgrp[i].canSpawn == False:
                    self.spawnTimer += dt
                    if self.spawnTimer >= self.spawnDelay:
                        if (self.Ghostgrp[i].hasReachHome):
                            self.Ghostgrp[i].Spawn()
                            self.Ghostgrp[i].hasReachHome = False
                            self.spawnTimer = 0.0
                            self.numofGhostAlive += 1
            self.numofGhostAlive = self.Ghostgrp[i].updateGhost(dt,self.numofGhostAlive,targetPos,IsPlayerAlive,IsPlayerPowerUp,pacman,self.world)
            if (self.Ghostgrp[i].PlayerCollision):
                self.PlayerCollision = True 
class GhostStateMachine:
  def GetCell(self,Pos):
        x = int(Pos.getY()+0.5);
        y = int(Pos.getX()+0.5);
        if( x<0 or y<0 or x>=len(self.mazeinfo) or y>=len(self.mazeinfo[x])):
            return ' '
        else:
            return self.mazeinfo[x][y]
  def IsChar(self,Pos,Letter):
        char = self.GetCell(Pos)
        if char == Letter:
            return True
        return False
  def IsCharUp(self,Pos,Radius,Letter):
        return  self.IsChar(Pos + Vec3(0,+Radius,0),Letter)
  def IsCharDown(self,Pos,Radius,Letter):
        return  self.IsChar(Pos + Vec3(0,-Radius,0),Letter)
  def IsCharLeft(self,Pos,Radius,Letter):
        return  self.IsChar(Pos + Vec3(-Radius,0,0),Letter)
  def IsCharRight(self,Pos,Radius,Letter):
        return  self.IsChar(Pos + Vec3(+Radius,0,0),Letter)
  def __init__(self,themap,inMazeinfo):
    self.states=["Home","Wander","Wander2","Chase","Evade","Death"]
    self.state = self.states[0]
    
    self.wayboid = BoidWayPoints()
    
    self.mazemap = themap

    self.canSpawn = False
    self.IsAlive = False
    #For Home
    self.HomeDir = 'None'
    #For Wandering
    self.WanderCount = 0
    self.WanderLimit = 7
    self.WanderTargets = []
    self.WanderTargets.append((1,1))
    self.WanderTargets.append((3,3))
    self.WanderTargets.append((6,6))
    self.WanderTargets.append((20,1))
    self.WanderTargets.append((17,3))
    self.WanderTargets.append((14,6))
    self.WanderTargets.append((1,19))
    self.WanderTargets.append((3,16))
    self.WanderTargets.append((6,13))
    self.WanderTargets.append((20,19))
    self.WanderTargets.append((17,16))
    self.WanderTargets.append((14,13))
    self.WanderTargets.append((7,8))
    self.WanderTargets.append((13,8))
    self.WanderTargets.append((13,12))
    self.WanderTargets.append((7,12))
    #For Chasing
    self.waypointcount = 0
    self.waypointLimit = 4
    self.updatewayTimer = 8.0
    self.Timer = 0.0
    self.isTimerHit = False
    #For Evade
    self.lastevadeDir = "None"
    #For Death and Home
    self.hasReachHome = True
    #For Collision
    self.PlayerCollision = False

    self.mazeinfo = inMazeinfo
  def initGhost(self,world,pos= Vec3(1, 1, 0.25),size= Vec3(1, 1, 1),mask = BitMask32.allOn()):
    shape = BulletSphereShape(0.499)
    node = BulletRigidBodyNode()

    self.ghost = render.attachNewNode(node)
    self.ghost.setPos(pos)
    self.ghost.setCollideMask(mask)

    node.setFriction(0.1)
    node.setAngularDamping(0.9)
    node.setMass(1.0)
    node.addShape(shape)
    world.attachRigidBody(node)

    visnp = loader.loadModel('Models/ghost')
    visnp.reparentTo(self.ghost)
    visnp.setScale(size)

    self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(1,1,0))
    self.aiKS = KinematicSeek(self.ghost,self.wayboid.waypoints[0])
    self.aiKS.np.setTransparency(TransparencyAttrib.MAlpha)
  def Spawn(self):
        self.wayboid.clearwaypoints()
        self.canSpawn = True
        self.HomeDir = 'None'
  def KillGhost(self):
      self.wayboid.clearwaypoints()
      self.canSpawn = False
      self.hasReachHome = False
      self.IsAlive = False
  def roundHint(self,val):
      return round(2*val)/2.0
  def CheckDirection(self,PosVec):
      direction = "None"
      PosVec.setX(self.roundHint(PosVec.getX()))
      PosVec.setY(self.roundHint(PosVec.getY()))
      if PosVec.getX() != 0:
          if PosVec.getX()>0:
              direction = "Left"
          else:
              direction = "Right"
      elif PosVec.getY() != 0:
          if PosVec.getY()>0:
              direction = "Down"
          else:
              direction = "Up"
      else:
          direction = "None"
      return direction
  #HOME IS DONE
  def HomeLogic(self):
      if (self.HomeDir != 'Left' and self.HomeDir !='Right'):
            self.HomeDir = 'Left'
            self.ghost.setY(self.roundHint(self.ghost.getY()))
            self.ghost.setX(self.roundHint(self.ghost.getX()))
            self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(9,10,0))
            self.waypointcount = 0

      Velocity = Vec3(0,0,0)
      if len(self.wayboid.waypoints)>self.waypointcount:
            self.moveDir = self.CheckDirection(self.aiKS.np.getPos() - self.wayboid.waypoints[1])
            if(self.moveDir == "Right"):
                self.HomeDir = "Right"
                Velocity =  Vec3(5,0,0)
                self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                if(self.IsCharRight(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                    Velocity = Vec3(0,0,0)
                        
            elif(self.moveDir == "Left"):
                self.HomeDir = "Left"
                Velocity =  Vec3(-5,0,0)
                self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                if(self.IsCharLeft(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                    Velocity = Vec3(0,0,0)
                       
            elif(self.moveDir == "None"):
                if (self.HomeDir == "Left"):
                    self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                    self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(11,10,0))
                else:
                    self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                    self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(9,10,0))
      else:
          self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
          self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(11,10,0))
      self.aiKS.np.node().setLinearVelocity(Velocity)
      print (self.aiKS.np.getPos())
  #WANDER IS DONE
  def WanderLogic(self,dt,wanderlimit=100):
      if len(self.wayboid.waypoints)>0:
          if (self.WanderCount < wanderlimit):
              self.moveDir = self.CheckDirection(self.aiKS.np.getPos() - self.wayboid.waypoints[1])
              Velocity =  Vec3(0,0,0)
              if(self.moveDir == "Up"):
                    Velocity =  Vec3(0,5,0)
                    self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
                    if(self.IsCharUp(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                        Velocity = Vec3(0,0,0)                  
                        self.WanderCount += 1
                        (posx,posy) = random.choice(self.WanderTargets)
                        self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(posx,posy,0))   
              elif(self.moveDir == "Down"):
                    Velocity =  Vec3(0,-5,0)
                    self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
                    if(self.IsCharDown(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                        Velocity = Vec3(0,0,0)
                        self.WanderCount += 1
                        (posx,posy) = random.choice(self.WanderTargets)
                        self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(posx,posy,0))
              elif(self.moveDir == "Right"):
                    Velocity =  Vec3(5,0,0)
                    self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                    if(self.IsCharRight(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                        Velocity = Vec3(0,0,0)
                        self.WanderCount += 1
                        (posx,posy) = random.choice(self.WanderTargets)
                        self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(posx,posy,0))
              elif(self.moveDir == "Left"):
                    Velocity =  Vec3(-5,0,0)
                    self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                    if(self.IsCharLeft(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                        Velocity = Vec3(0,0,0)
                        self.WanderCount += 1
                        (posx,posy) = random.choice(self.WanderTargets)
                        self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(posx,posy,0))
              elif(self.moveDir == "None"):
                    self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                    self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
                    self.WanderCount += 1
                    (posx,posy) = random.choice(self.WanderTargets)
                    self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(posx,posy,0))

              self.aiKS.np.node().setLinearVelocity(Velocity)
          else:
              self.WanderCount = 0
      else:
          self.WanderCount += 1
          (posx,posy) = random.choice(self.WanderTargets)
          self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(posx,posy,0))                        
  #CHASE IS DONE
  def ChaseLogic(self,dt,targetPos):    
         if len(self.wayboid.waypoints)>self.waypointcount: #If Waypoint is not out of index
            self.Timer += dt
            if self.waypointcount <= self.waypointLimit:
                self.moveDir = self.CheckDirection(self.aiKS.np.getPos() - self.wayboid.waypoints[self.waypointcount])

                Velocity =  Vec3(0,0,0)
                if(self.moveDir == "Up"):
                    Velocity =  Vec3(0,5,0)
                    self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
                    if(self.IsCharUp(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                        Velocity = Vec3(0,0,0)                     
                        self.waypointcount+=1
                elif(self.moveDir == "Down"):
                    Velocity =  Vec3(0,-5,0)
                    self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
                    if(self.IsCharDown(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                       Velocity = Vec3(0,0,0)
                       self.waypointcount+=1
                elif(self.moveDir == "Right"):
                    Velocity =  Vec3(5,0,0)
                    self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                    if(self.IsCharRight(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                       Velocity = Vec3(0,0,0)
                       self.waypointcount+=1
                elif(self.moveDir == "Left"):
                    Velocity =  Vec3(-5,0,0)
                    self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                    if(self.IsCharLeft(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                       Velocity = Vec3(0,0,0)
                       self.waypointcount+=1
                elif(self.moveDir == "None"):
                    if self.isTimerHit:
                        #print "Recalculate path: Timer End"
                        self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                        self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
                        self.waypointcount = 0
                        self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(int(self.roundHint(targetPos.getX())-0.5),int(self.roundHint(targetPos.getY())-0.5),0))
                        self.isTimerHit = False
                    else:        
                        self.waypointcount+=1  
                        if len(self.wayboid.waypoints)<=self.waypointcount:
                            #print "Recalculate path: End of Way Points"
                            self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                            self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
                            self.waypointcount = 0
                            self.Timer = 0.0
                            self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(int(self.roundHint(targetPos.getX())-0.5),int(self.roundHint(targetPos.getY())-0.5),0))
                                                  
                self.aiKS.np.node().setLinearVelocity(Velocity)   
                         
            else:
                #print "Recalculate path: WayPoint Limit Reach"
                self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
                self.waypointcount = 0
                self.Timer = 0.0
                self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(int(self.roundHint(targetPos.getX())-0.5),int(self.roundHint(targetPos.getY())-0.5),0))
            if (self.Timer > self.updatewayTimer):
                self.isTimerHit = True 
                self.Timer = 0
         else:
            #print "Uncomment this line for Eenmy to Chase Player no Matter What"
            #print "Recalculate path: No Way Points Found"
            self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
            self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
            self.waypointcount = 0
            self.Timer = 0.0
            self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(int(self.roundHint(targetPos.getX())-0.5),int(self.roundHint(targetPos.getY())-0.5),0))
            self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(self.roundHint(targetPos.getX())-0.5,self.roundHint(targetPos.getY())-0.5,0))
  #EVADE IS DONE
  def EvadeLogic(self,dt,targetPos):
      Dir = self.aiKS.np.getPos()-targetPos;
      MoveDir = []
      if (abs(Dir.getX())>=abs(Dir.getY())):
          if(Dir.getX()>0):
             MoveDir.append("Right")
          else:
             MoveDir.append("Left")
          if(Dir.getY()>0):
             MoveDir.append("Up")
             MoveDir.append("Down")
             if(Dir.getX()>0):
                 MoveDir.append("Left")
             else:
                 MoveDir.append("Right")
          else:
             MoveDir.append("Down")
             MoveDir.append("Up")
             if(Dir.getX()>0):
                 MoveDir.append("Left")
             else:
                 MoveDir.append("Right")
      else:
          if(Dir.getY()>0):
             MoveDir.append("Up")
          else:
             MoveDir.append("Down")
          if(Dir.getX()>0):
             MoveDir.append("Right")
             MoveDir.append("Left")
             if(Dir.getY()>0):
                 MoveDir.append("Down")       
             else:
                 MoveDir.append("Up")
          else:
             MoveDir.append("Left")
             MoveDir.append("Right")
             if(Dir.getY()>0):
                 MoveDir.append("Down")       
             else:
                 MoveDir.append("Up")
    
      for i in range(len(MoveDir)):
          if (MoveDir[i] == "Up"):
                    Velocity = Vec3(0,0,0) 
                    if(self.lastevadeDir != "Down"):
                        if(self.roundHint(self.ghost.getX()) != int(self.roundHint(self.ghost.getX()))):
                            if(self.IsCharUp(self.ghost.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                                Velocity = Vec3(0,3.0,0)
                                self.ghost.setX(self.roundHint(self.ghost.getX()))
                                self.lastevadeDir = MoveDir[i]
                                break                           
          elif (MoveDir[i] == "Down"):   
                    Velocity = Vec3(0,0,0)       
                    if(self.lastevadeDir != "Up"):
                        if(self.roundHint(self.ghost.getX()) != int(self.roundHint(self.ghost.getX()))):
                            if(self.IsCharDown(self.ghost.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                                Velocity = Vec3(0,-3.0,0)
                                self.ghost.setX(self.roundHint(self.ghost.getX()))
                                self.lastevadeDir = MoveDir[i]
                                break                        
          elif (MoveDir[i] == "Left"):
                    Velocity = Vec3(0,0,0) 
                    if(self.lastevadeDir != "Right"):
                        if(self.roundHint(self.ghost.getY()) != int(self.roundHint(self.ghost.getY()))):
                            if(self.IsCharLeft(self.ghost.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                                Velocity = Vec3(-3.0,0,0)
                                self.ghost.setY(self.roundHint(self.ghost.getY()))
                                self.lastevadeDir = MoveDir[i]
                                break
          elif (MoveDir[i] == "Right"):                 
                    Velocity = Vec3(0,0,0) 
                    if(self.lastevadeDir != "Left"):
                        if(self.roundHint(self.ghost.getY()) != int(self.roundHint(self.ghost.getY()))):   
                            if(self.IsCharRight(self.ghost.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                                Velocity = Vec3(3.0,0,0)
                                self.ghost.setY(self.roundHint(self.ghost.getY()))
                                self.lastevadeDir = MoveDir[i]
                                break      
      self.ghost.node().setLinearVelocity(Velocity)   
  def EvadeLogic2(self,dt,targetPos):
      Dir = self.aiKS.np.getPos()-targetPos;
      MoveDir = []
      if (abs(Dir.getX())>=abs(Dir.getY())):
          if(Dir.getX()>0):
             MoveDir.append("Right")
          else:
             MoveDir.append("Left")
          if(Dir.getY()>0):
             MoveDir.append("Up")
             MoveDir.append("Down")
             if(Dir.getX()>0):
                 MoveDir.append("Left")
             else:
                 MoveDir.append("Right")
          else:
             MoveDir.append("Down")
             MoveDir.append("Up")
             if(Dir.getX()>0):
                 MoveDir.append("Left")
             else:
                 MoveDir.append("Right")
      else:
          if(Dir.getY()>0):
             MoveDir.append("Up")
          else:
             MoveDir.append("Down")
          if(Dir.getX()>0):
             MoveDir.append("Right")
             MoveDir.append("Left")
             if(Dir.getY()>0):
                 MoveDir.append("Down")       
             else:
                 MoveDir.append("Up")
          else:
             MoveDir.append("Left")
             MoveDir.append("Right")
             if(Dir.getY()>0):
                 MoveDir.append("Down")       
             else:
                 MoveDir.append("Up")

      for i in range(len(MoveDir)):
          if (MoveDir[i] == "Up"):
                    Velocity = Vec3(0,0,0) 
                    if(self.roundHint(self.ghost.getX()) != int(self.roundHint(self.ghost.getX()))):
                        if(self.IsCharUp(self.ghost.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                            Velocity = Vec3(0,3.0,0)
                            self.ghost.setX(self.roundHint(self.ghost.getX()))
                            break                           
          elif (MoveDir[i] == "Down"):   
                    Velocity = Vec3(0,0,0)       
                    if(self.roundHint(self.ghost.getX()) != int(self.roundHint(self.ghost.getX()))):
                        if(self.IsCharDown(self.ghost.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                            Velocity = Vec3(0,-3.0,0)
                            self.ghost.setX(self.roundHint(self.ghost.getX()))
                            break                        
          elif (MoveDir[i] == "Left"):
                    Velocity = Vec3(0,0,0) 
                    if(self.roundHint(self.ghost.getY()) != int(self.roundHint(self.ghost.getY()))):
                        if(self.IsCharLeft(self.ghost.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                            Velocity = Vec3(-3.0,0,0)
                            self.ghost.setY(self.roundHint(self.ghost.getY()))
                            break
          elif (MoveDir[i] == "Right"): 
                    Velocity = Vec3(0,0,0) 
                    if(self.roundHint(self.ghost.getY()) != int(self.roundHint(self.ghost.getY()))):   
                        if(self.IsCharRight(self.ghost.getPos()-Vec3(0.5,0.5,0),0.51,0)):
                            Velocity = Vec3(3.0,0,0)
                            self.ghost.setY(self.roundHint(self.ghost.getY()))
                            break      
      self.ghost.node().setLinearVelocity(Velocity)
  #Death IS DONE
  def DeathLogic(self,dt):        
      if len(self.wayboid.waypoints)>self.waypointcount:
            self.moveDir = self.CheckDirection(self.aiKS.np.getPos() - self.wayboid.waypoints[self.waypointcount])
            Velocity =  Vec3(0,0,0)
            if(self.moveDir == "Up"):
                Velocity =  Vec3(0,5,0)
                self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
                if(self.IsCharUp(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                    Velocity = Vec3(0,0,0)                     
                    self.waypointcount+=1
            elif(self.moveDir == "Down"):
                Velocity =  Vec3(0,-5,0)
                self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
                if(self.IsCharDown(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                    Velocity = Vec3(0,0,0)
                    self.waypointcount+=1
            elif(self.moveDir == "Right"):
                Velocity =  Vec3(5,0,0)
                self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                if(self.IsCharRight(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                    Velocity = Vec3(0,0,0)
                    self.waypointcount+=1
            elif(self.moveDir == "Left"):
                Velocity =  Vec3(-5,0,0)
                self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
                if(self.IsCharLeft(self.aiKS.np.getPos()-Vec3(0.5,0.5,0),0.51,1)):
                    Velocity = Vec3(0,0,0)
                    self.waypointcount+=1
            elif(self.moveDir == "None"):        
                    self.waypointcount+=1                                                  
            self.aiKS.np.node().setLinearVelocity(Velocity)
      else:
          self.aiKS.np.setX(self.roundHint(self.aiKS.np.getX()))
          self.aiKS.np.setY(self.roundHint(self.aiKS.np.getY()))
          self.hasReachHome = True

  def updateGhost(self,dt,numofGhostAlive,targetPos,IsPlayerAlive,IsPlayerPowerUp,pacman,world):
    self.ghost.node().setActive(True)
    #Collision
    result = world.contactTestPair(self.ghost.node(), pacman.node())
    if self.IsAlive:
        if result.getNumContacts() > 0:
            self.PlayerCollision = True
        else:
            self.PlayerCollision = False
    else:
        self.PlayerCollision = False
    if self.state == 'Home':       
        if (self.canSpawn):
            self.IsAlive = True
            self.canSpawn = False
            self.hasReachHome = False
            DistVec = self.aiKS.np.getPos()-targetPos
            Distance = DistVec.length()
            if (Distance <= 3.0):
                self.state = 'Chase'
            else:
                self.state = 'Wander'
                self.WanderCount = 0           
        else:
            self.HomeLogic()
    elif self.state == 'Wander':
        if(IsPlayerPowerUp):
            self.wayboid.clearwaypoints()
            self.state = 'Evade'
        elif(self.WanderCount<self.WanderLimit):
            self.WanderLogic(dt)
        else:
            self.state = 'Wander2'
    elif self.state == 'Wander2':
        if(IsPlayerPowerUp):
            self.wayboid.clearwaypoints()
            self.state = 'Evade'
        elif (IsPlayerAlive):
            self.wayboid.clearwaypoints()
            self.state = 'Chase'
        else:
            self.WanderLogic(dt)
    elif self.state == 'Chase':
        if(IsPlayerPowerUp):
            self.wayboid.clearwaypoints()
            self.state = 'Evade'
        elif (IsPlayerAlive):
            self.ChaseLogic(dt,targetPos)
        else:
            self.state = 'Wander2'
    elif self.state == 'Evade':
        if (IsPlayerPowerUp):
            self.EvadeLogic(dt,targetPos)
            if(self.PlayerCollision):
                self.KillGhost()
                numofGhostAlive -= 1
                self.aiKS.np.setAlphaScale(0.5)
                self.mazemap.UpdateWayPoints(self.wayboid,Vec3(self.ghost.getX()-0.5,self.ghost.getY()-0.5,self.ghost.getZ()),Vec3(10,10,0))
                self.state = 'Death'
        else:
            self.state = 'Chase'
    elif self.state == 'Death':
        self.DeathLogic(dt)
        if (self.hasReachHome):
            self.wayboid.clearwaypoints()
            self.state = "Home"
            self.IsAlive = True
            self.aiKS.np.setAlphaScale(1.0) 
    return numofGhostAlive
class BoidWayPoints:
  def __init__(self):
    self.waypoints=[]
    self.count = 0

  def setupBoid(self,world,pos= Vec3(0, 0, 2),size= Vec3(1, 0.5, 0.8)):
    # Boid
    shape = BulletCylinderShape(size)
    node = BulletRigidBodyNode('Teapot')
    node.setFriction(0.1)
    node.setAngularDamping(0.9)
    node.setMass(1.0)
    node.addShape(shape)
    np = render.attachNewNode(node)
    pos=self.waypoints[0]
    np.setPos(pos)
    world.attachRigidBody(node)
    model = loader.loadModel('teapot')
    model.setH(90)
    model.setZ(-0.75)
    model.setScale(0.5)
    model.reparentTo(np)
    self.aiKE = KinematicArrive(np,self.waypoints[0])

  def update(self):
    if len(self.waypoints)>self.count:
        self.aiKE.update()
        if (self.aiKE.np.getPos() - self.waypoints[self.count]).lengthSquared() < 4:
            self.count+=1
            if self.count<len(self.waypoints):
                self.aiKE.target = self.waypoints[self.count]
        self.aiKE.model.setPos(self.waypoints[self.count])

  def clearwaypoints(self):
      self.waypoints=[]
      self.count = 0
class Map(object):
  def __init__(self,world,mazeinfo,dirs=4):
    self.world = world
    self.dirs = dirs # number of possible directions to move on the map
    if self.dirs == 4:
        self.dx = [1, 0, -1, 0]
        self.dy = [0, 1, 0, -1]

    self.m = 21 # vertical size rows
    self.n = 21 # horizontal size column    
    self.the_map = copy.deepcopy(mazeinfo)
  def UpdateWayPoints(self,wayboid,StartPos,EndPos):
      wayboid.clearwaypoints()
      self.xA = int(StartPos.getX())
      self.yA = int(StartPos.getY())
      self.xB = int(EndPos.getX())
      self.yB = int(EndPos.getY())
      route = self.pathFind(self.the_map, self.n, self.m, self.dirs, self.dx, self.dy, self.xA, self.yA, self.xB, self.yB)

      if len(route) > 0:
        x = self.xA
        y = self.yA
        oldx = copy.deepcopy(x)
        oldy = copy.deepcopy(y)
        isfirst = False;
        hasspawn = True
        checkupdown = False
        checkleftright = False
        self.addWayPoint(wayboid,x,y)
        for i in range(len(route)):
            j = int(route[i])
            x += self.dx[j]
            y += self.dy[j]

            if checkupdown:
                if (oldx != x):
                    self.addWayPoint(wayboid,oldx,y)
                    checkupdown = False
            elif checkleftright:
                if (oldy != y):
                    self.addWayPoint(wayboid,x,oldy)
                    checkleftright = False
            if checkupdown == False and checkleftright == False:
                if (oldx == x):
                    checkupdown=True
                    checkleftright=False
                elif (oldy == y):
                    checkupdown=False
                    checkleftright=True
            oldx = copy.deepcopy(x)
            oldy = copy.deepcopy(y)
        self.addWayPoint(wayboid,x,y)
      #print 'WayPointUpdated'
  def pathFind(self,the_map, n, m, dirs, dx, dy, xA, yA, xB, yB):
    closed_nodes_map = [] # map of closed (tried-out) nodes
    open_nodes_map = [] # map of open (not-yet-tried) nodes
    dir_map = [] # map of dirs
    row = [0] * n
    for i in range(m): # create 2d arrays
        closed_nodes_map.append(list(row))
        open_nodes_map.append(list(row))
        dir_map.append(list(row))

    pq = [[], []] # priority queues of open (not-yet-tried) nodes
    pqi = 0 # priority queue index
    # create the start node and push into list of open nodes
    n0 = node(xA, yA, 0, 0)
    n0.updatePriority(xB, yB)
    heappush(pq[pqi], n0)
    open_nodes_map[yA][xA] = n0.priority # mark it on the open nodes map

    # A* search
    while len(pq[pqi]) > 0:
        # get the current node w/ the highest priority
        # from the list of open nodes
        n1 = pq[pqi][0] # top node
        n0 = node(n1.xPos, n1.yPos, n1.distance, n1.priority)
        x = n0.xPos
        y = n0.yPos
        heappop(pq[pqi]) # remove the node from the open list
        open_nodes_map[y][x] = 0
        closed_nodes_map[y][x] = 1 # mark it on the closed nodes map

        # quit searching when the goal is reached
        # if n0.estimate(xB, yB) == 0:
        if x == xB and y == yB:
            # generate the path from finish to start
            # by following the dirs
            path = ''
            while not (x == xA and y == yA):
                j = dir_map[y][x]
                c = str((j + dirs / 2) % dirs)
                path = c + path
                x += dx[j]
                y += dy[j]
            return path

        # generate moves (child nodes) in all possible dirs
        for i in range(dirs):
            xdx = x + dx[i]
            ydy = y + dy[i]
            if not (xdx < 0 or xdx > n-1 or ydy < 0 or ydy > m - 1
                    or the_map[ydy][xdx] == 1 or closed_nodes_map[ydy][xdx] == 1):
                # generate a child node
                m0 = node(xdx, ydy, n0.distance, n0.priority)
                m0.nextMove(dirs, i)
                m0.updatePriority(xB, yB)
                # if it is not in the open list then add into that
                if open_nodes_map[ydy][xdx] == 0:
                    open_nodes_map[ydy][xdx] = m0.priority
                    heappush(pq[pqi], m0)
                    # mark its parent node direction
                    dir_map[ydy][xdx] = (i + dirs / 2) % dirs
                elif open_nodes_map[ydy][xdx] > m0.priority:
                    # update the priority
                    open_nodes_map[ydy][xdx] = m0.priority
                    # update the parent direction
                    dir_map[ydy][xdx] = (i + dirs / 2) % dirs
                    # replace the node
                    # by emptying one pq to the other one
                    # except the node to be replaced will be ignored
                    # and the new node will be pushed in instead
                    while not (pq[pqi][0].xPos == xdx and pq[pqi][0].yPos == ydy):
                        heappush(pq[1 - pqi], pq[pqi][0])
                        heappop(pq[pqi])
                    heappop(pq[pqi]) # remove the target node
                    # empty the larger size priority queue to the smaller one
                    if len(pq[pqi]) > len(pq[1 - pqi]):
                        pqi = 1 - pqi
                    while len(pq[pqi]) > 0:
                        heappush(pq[1-pqi], pq[pqi][0])
                        heappop(pq[pqi])       
                    pqi = 1 - pqi
                    heappush(pq[pqi], m0) # add the better node instead
    return '' # if no route found
  def drawObstacle(self):
    # display the map with the route added
    drawmap = []
    drawmap = self.the_map
    #drawmap.reverse()
    for x in range(self.m):
        for y in range(self.n):
            xy = drawmap[x][y]
            if xy == 0:
                print ('.'), # space
            elif xy == 1:
                print ('O'), # obstacle
            elif xy == 2:
                print ('S'), # start
            elif xy == 3:
                print ('R'), # route
            elif xy == 4:
                print ('F'), # finish
        print
  def addWayPoint(self,boid,x,y,size= Vec3(0.25,0.25,0.25)):
    # Translating Map Grid to actual coordinate
    pos = Vec3(x+0.5,y+0.5,0.25)
    boid.waypoints.append(pos)

    #shape = BulletBoxShape(size)
    #self.np = render.attachNewNode("WayPoint")
    #self.np.setPos(pos)
   
    #model = loader.loadModel('frowney')
    #model.setScale(size)
    #model.reparentTo(self.np)
   
game = PacGame()
base.run()