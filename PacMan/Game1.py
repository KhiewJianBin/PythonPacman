import sys
import direct.directbase.DirectStart
import math

from direct.showbase.DirectObject import DirectObject
#To use inputs
from direct.showbase.InputStateGlobal import inputState
#To use UI
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
#Lights
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
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode

from direct.stdpy.file import *

from random import randint


class Game1(DirectObject):

    #extras
    WhiteColor = (1,1,1,1)

    #Game Settings
    Level = 0
    havesound = True
    havemusic = True

    #Lights
    #ALightList = []
    #DLightList = []
    #SLightList = []
    #LightsList = [ALightList,DLightList,SLightList]
  
    def __init__(self):
        self.init()

        taskMgr.add(self.update, 'updateWorld')

    def init(self):
        base.setBackgroundColor(0.1,0.1,0.8,1)
        base.setFrameRateMeter(True)

        #Base Windows Input Detect
        self.accept('escape', self.doExit)
        self.accept('f1', self.toggleWireframe)
        self.accept('f2', self.toggleTexture)
        self.accept('f3', self.toggleDebug)

        self.accept('f12',self.Screenshot)
        
        #Game Stuff
        self.bg = base.loader.loadSfx("Sounds/menubg.wav")
        self.click = base.loader.loadSfx("Sounds/buttonclick.wav")
        self.bg.play()
        #GameStats Screen
        self.Gamestates=["MainMenu","Options","Instructions","Credits","Playing"]
        self.Gamestate = self.Gamestates[0]
        self.DisplayMainMenuScreen()        
    def update(self, task):
        dt = globalClock.getDt()
        if(self.Gamestate == "MainMenu"):
            print ("GameState = MainMenu")
        elif(self.Gamestate == "Options"):
            print ("GameState = Options")
        elif(self.Gamestate == "Instructions"):
            print ("GameState = Instructions")
        elif(self.Gamestate == "Credits"):
            print ("GameState = Credits")
        elif(self.Gamestate == "Playing"):
            #Listen for Game Input
            self.GameProcessInput(dt)

            self.world.doPhysics(dt)                             
        else:
            print ("Game State = Undefined")

        #Repeat
        return task.cont

    def cleanup(self):
        #clean Pointers

        self.world.removeRigidBody(self.ground)
        self.world = None

        self.worldNP.removeNode()  

    def DisplayMainMenuScreen(self):
        self.MenuImage = OnscreenImage(image = 'Textures/Menu.jpg',pos = (0 ,0 ,0), scale=(1.4,1,1))

        self.startButton = DirectButton(text = ('Start Game','GoodLuck!','Ready?','Error'), scale = 0.1, pos = (0, 0, 0.25),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.DisplayGameScreen,clickSound = self.click)
        self.optionsButton = DirectButton(text = ('Options'), scale = 0.1, pos = (0, 0, 0.1),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.DisplayOptionsScreen,clickSound = self.click)
        self.instructionsButton = DirectButton(text = ('Instructions','How to Play'), scale= 0.1, pos = (0, 0, -0.05),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.DisplayInstructionScreen,clickSound = self.click)       
        self.creditButton = DirectButton(text = 'Credits', scale= 0.1, pos = (0, 0, -0.20),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.DisplayCreditsScreen,clickSound = self.click)       

        self.Gamestate = 'MainMenu'
    def DestroyMainMenuScreen(self):
        self.MenuImage.destroy()
        self.startButton.destroy()
        self.optionsButton.destroy()
        self.creditButton.destroy()
        self.instructionsButton.destroy()
    def DisplayGameScreen(self):
        self.bg.stop()
        self.DestroyMainMenuScreen()
        self.Gamestate = 'Playing'
        self.SetupGame()
    def DisplayOptionsScreen(self):
        self.DestroyMainMenuScreen()
        if self.havesound:
            a = 'On'
        else:
            a = 'Off'
        if self.havemusic:
            b = 'On'
        else:
            b = 'Off'
        self.OptionImage = OnscreenImage(image = 'Textures/Menu.jpg',pos = (0 ,0 ,0), scale=(1.4,1,1))

        self.soundButton = DirectButton(text = ('Sound - ' + a), scale = 0.1, pos = (0, 0, 0.25),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.ToggleSound,clickSound = self.click)
        self.musicButton = DirectButton(text = ('Music - ' + b), scale = 0.1, pos = (0, 0, 0.5),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.ToggleMusic,clickSound = self.click)

        self.backButton = DirectButton(text = ('BACK'), scale = 0.1, pos = (0, 0, -0.9),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.DestoryOptionScreen,clickSound = self.click)

        self.Gamestate = 'Options'
    def DestoryOptionScreen(self):
        self.OptionImage.destroy()
        self.soundButton.destroy()
        self.musicButton.destroy()
        self.backButton.destroy()
        self.DisplayMainMenuScreen()
        self.Gamestate = "MainMenu"
    def ToggleSound(self):
        self.soundButton.destroy()
        if self.havesound:
            self.havesound = False
            self.soundButton = DirectButton(text = ('Sound - Off'), scale = 0.1, pos = (0, 0, 0.25),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.ToggleSound,clickSound = self.click)
        else:
            self.havesound = True
            self.soundButton = DirectButton(text = ('Sound - On'), scale = 0.1, pos = (0, 0, 0.25),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.ToggleSound,clickSound = self.click)
    def ToggleMusic(self):
        self.musicButton.destroy()
        if self.havemusic:
            self.havemusic = False
            self.musicButton = DirectButton(text = ('Music - Off'), scale = 0.1, pos = (0, 0, 0.5),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.ToggleMusic,clickSound = self.click)
        else:
            self.havemusic = True
            self.musicButton = DirectButton(text = ('Music - On'), scale = 0.1, pos = (0, 0, 0.5),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.ToggleMusic,clickSound = self.click)           
    def DisplayInstructionScreen(self):
        self.DestroyMainMenuScreen()
        self.InstructionImage = OnscreenImage(image = 'Textures/Instruction.jpg',pos = (0 ,0 ,0), scale=(1.4,1,1))

        self.backButton = DirectButton(text = ('BACK'), scale = 0.1, pos = (0, 0, -0.9),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.DestroyInstructionScreen,clickSound = self.click)
        
        self.Gamestate = 'Instructions'
    def DestroyInstructionScreen(self):
        self.InstructionImage.destroy()
        self.backButton.destroy()
        self.DisplayMainMenuScreen()
    def DisplayCreditsScreen(self):
        self.DestroyMainMenuScreen()
        self.CreditImage = OnscreenImage(image = 'Textures/Menu.jpg',pos = (0 ,0 ,0), scale=(1.4,1,1))
        self.CreditText = OnscreenText(text = 'Credits', pos = (0, 0.5), scale = 0.2)
        self.CreditText2 = OnscreenText(text = 'Programmer:Khiew Jian Bin\nArt:Khiew Jian Bin\nSounds And Music: sweetsoundeffects.com \nSFX_Pacman.zip - 1/24/2013', pos = (-0.1, 0.02), scale = 0.1)
        self.backButton = DirectButton(text = ('BACK'), scale = 0.1, pos = (0, 0, -0.9),frameColor = ((0.5,0.4,0.5,1),(0.5,0.8,0.5,1),(0.8,0.4,0.5,1),(0.5,0.5,0.5,1)),command=self.DestroyCreditsScreen,clickSound = self.click)
        self.Gamestate = "Credits"
    def DestroyCreditsScreen(self): 
        self.CreditImage.destroy()
        self.CreditText.destroy()
        self.CreditText2.destroy()
        self.backButton.destroy()
        self.DisplayMainMenuScreen()

    #Game Setups
    def SetupGameControls(self):
        inputState.watchWithModifiers('forward','w')
        inputState.watchWithModifiers('reverse','s')
        inputState.watchWithModifiers('turnleft','q')
        inputState.watchWithModifiers('turnright','e')

        inputState.watchWithModifiers('debugkey1','9')
        inputState.watchWithModifiers('debugkey2','0')
    def SetupGame(self):

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

        #Game Vars
        self.gamePaused = False
     
        base.cam.setPos(11, 9.5, 40)
        base.cam.lookAt(11, 10.5, 0)
        #base.disableMouse()

        self.worldNP = render.attachNewNode('World')
        self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
        #self.debugNP.show()

        # World
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())

        # Plane
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0.25)

        self.ground = BulletRigidBodyNode('Ground')
        self.ground.addShape(shape)
        np = render.attachNewNode(self.ground)
        np.setPos(0,0,-0.5)
    
        self.world.attachRigidBody(self.ground)
        model = loader.loadModel('Models/floor.egg')
        model.reparentTo(np)

        self.setupMaze()

    def setupMaze(self):   
      self.MazePos = Vec3(0,0,0.25)
      self.mazeinfo = []
      self.mazeinfo2 = []
      Mazefile = open("Maze.txt")
      Rowcount = -1; 
      for rows in Mazefile.readlines():
        self.mazeinfo.append([])
        self.mazeinfo2.append([])
        Rowcount += 1
        for i in rows:
            if i != '\n':
                self.mazeinfo2[Rowcount].append(0)
                if i == '0':
                    self.mazeinfo[Rowcount].append(0)
                else:
                    self.mazeinfo[Rowcount].append(1)
      self.mazeinfo.reverse() #reverse the list of rows

      self.BoxScale = Vec3(0,1,1)
      self.first = False
      self.boxspawn = True
      for i in range(len(self.mazeinfo)):
        if self.boxspawn == False:
            if self.BoxScale.getX() == 1:
                self.boxspawn = True
                self.first = False
                self.BoxScale.setX(0)
            else:
                for b in range(int(self.BoxScale.getX())):
                    self.mazeinfo2[i-1][(int(x - self.MazePos.getX())) + b] = 1
                self.CreateBox(self.BoxScale,Vec3(x,y,z))
                self.boxspawn = True
                self.first = False
                self.BoxScale.setX(0)
        for j in range(len(self.mazeinfo[i])):
            if self.mazeinfo[i][j] == 1:
                self.BoxScale.setX(self.BoxScale.getX()+1)
                if self.first == False:
                    self.first = True
                    self.boxspawn = False
                    x = j + self.MazePos.getX()
                    y = i + self.MazePos.getY()
                    z = self.MazePos.getZ()
            else:
                if self.boxspawn == False:
                    if self.BoxScale.getX() == 1:
                        self.boxspawn = True
                        self.first = False
                        self.BoxScale.setX(0)
                    else:
                        for b in range(int(self.BoxScale.getX())):
                            self.mazeinfo2[i][(int(x - self.MazePos.getX())) + b] = 1
                        self.CreateBox(self.BoxScale,Vec3(x,y,z))
                        self.boxspawn = True
                        self.first = False
                        self.BoxScale.setX(0)
      if self.boxspawn == False:
        if self.BoxScale.getX() == 1:
            self.boxspawn = True
            self.first = False
            self.BoxScale.setX(0)
        else:
            for c in range(len(self.mazeinfo[len(self.mazeinfo)-1])):
                self.mazeinfo2[len(self.mazeinfo)-1][c] = 1
            self.CreateBox(self.BoxScale,Vec3(x,y,z))
            self.boxspawn = True
            self.first = False
            self.BoxScale.setX(0)

      self.BoxScale = Vec3(1,0,1)
      self.first = False
      self.boxspawn = True
      for i in range(len(self.mazeinfo)):
          for j in range(len(self.mazeinfo[i])):
              a = i
              while(self.mazeinfo[a][j] == 1 and self.mazeinfo2[a][j]!=1):
                 self.BoxScale.setY(self.BoxScale.getY()+1)
                 self.mazeinfo2[a][j] = 1
                 a += 1
                 if self.first == False:
                    self.first = True
                    self.boxspawn = False
                    x = j + self.MazePos.getX()
                    y = i + self.MazePos.getY()
                    z = self.MazePos.getZ()
              if self.boxspawn == False:
                    self.CreateBox(self.BoxScale,Vec3(x,y,z))
                    self.boxspawn = True
                    self.first = False
                    self.BoxScale.setY(0)                        
    def CreateBox(self,Scale,Pos):
        shape = BulletBoxShape(Scale * 0.5)
        body = BulletRigidBodyNode()
        bodyNP = self.worldNP.attachNewNode(body)
        bodyNP.node().addShape(shape)
        bodyNP.node().setMass(10000000.0)
        Pos.setX(Pos.getX() + Scale.getX()* 0.5)
        Pos.setY(Pos.getY() + Scale.getY()* 0.5)
        bodyNP.setPos(Pos)
        bodyNP.setCollideMask(BitMask32.allOn())

        self.world.attachRigidBody(bodyNP.node())

        visNP = loader.loadModel('Models/box.egg')
        visNP.clearModelNodes()
        visNP.reparentTo(bodyNP)
        
        visNP.setScale(Scale)

    def GetCell(self,Pos):
        x = int(Pos.getY()+0.5);
        y = int(Pos.getX()+0.5);
        if( x<0 or y<0 or x>=len(self.mazeinfo) or y>=len(self.mazeinfo[x])):
            return ' '
        else:
            return self.mazeinfo[x][y]
    def IsChar(self,Pos,Letter):
        Pos -= self.MazePos
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
        #return self.IsChar(Pos,Letter) and self.IsChar(Pos + Vec3(-radius,-radius,0),Letter) and self.IsChar(Pos + Vec3(-radius,+radius,0),Letter) and self.IsChar(Pos + Vec3(+radius,-radius,0),Letter) and self.IsChar(Pos + Vec3(+radius,+radius,0),Letter)

    def GameProcessInput(self,dt):
        if inputState.isSet('debugkey1'): print ("Debug Key1 Press")
        if inputState.isSet('debugkey2'): print ("Debug Key2 Press")
    def GameUpdate(self,dt):  
        print ("GameUpdate")

    #Window Base Input Functions
    def doExit(self):
        if self.Gamestate == "Playing":
            self.cleanup()
            print("GameObjects Cleaned")
        sys.exit(1)
    def toggleWireframe(self):
        base.toggleWireframe()
        print ('WireFrame')
    def toggleTexture(self):
        base.toggleTexture()
        print ('Texture')
    def ResetEntireGame(self):
        self.cleanup()
        self.SetupGame()
        print ('ResetGame')
    def toggleDebug(self):
        if self.debugNP.isHidden():
            self.debugNP.show()
            print('DebugOn')
        else:
            self.debugNP.hide()
            print('DebugOff') 
    def Screenshot(self):
        base.screenshot('Bullet')
        print ('ScreenShot')
      
    #Additional helper Functions
    def InitALight(self,Color,Name):#Ambient Light
        alight = AmbientLight(Name)
        alight.setColor(Color)

        self.ALightList.append(alight)

        render.setLight(render.attachNewNode(alight))
    def InitSpotLight(self,Pos,Color,Name):#Spot Light
        slight = Spotlight(Name)
        slight.setColor(Color)
        lens = PerspectiveLens()
        slight.setLens(lens)
        slightNP.setPos(Pos)

        self.SLightList.append(slight)

        render.setLight(render.attachNewNode(slight))
    def InitDLight(self,Color,Dir,Name):#Directional Light
        dlight = DirectionalLight(Name)
        dlight.setDirection(Dir)
        dlight.setColor(Color)

        self.DLightList.append(dlight)
        
        render.setLight(render.attachNewNode(dlight))
    def CalculateDirVec(self,Rotation):
        lookTheta = math.radians(Rotation.getX())
        lookTheta2 = math.radians(Rotation.getY())

        #REMEBER REMEBER REMEBER x3 rotation.xyz = hpr IMPORTANT
        x = -math.sin(lookTheta)
        y = math.cos(lookTheta)
        z = math.sin(lookTheta2)

        lookatvector = Vec3(x,y,z)

        return lookatvector

        # REMEBER REMEBER REMEBER x3 rotation.xyz = hpr
        #x = -math.sin(math.radians(Rotation.getX()));
        #y =  math.cos(math.radians(Rotation.getX()));
        #z =  math.sin(math.radians(Rotation.getY()));
   

        #x = -math.sin(math.radians(Rotation.getX()));
        #y =  math.cos(math.radians(Rotation.getY()))*math.cos(math.radians(Rotation.getX()));
        #z =  math.sin(math.radians(Rotation.getY()))*math.cos(math.radians(Rotation.getX()));

        return Vec3(x,y,z)
    def drawLines(self):  
        # Draws lines for the 
        self.lines.reset()  
        self.lines.drawLines([(self.linefrom,self.lineto)])  
        self.lines.create()

        #myNodePath.setTransparency(TransparencyAttrib.MAlpha)
        #myNodePath.setColorScale(R, G, B, A)

        #camera1.node().setCameraMask(BitMask32.bit(0))
        #camera2.node().setCameraMask(BitMask32.bit(1))
        #myNodePath.hide(BitMask32.bit(0))
        #myNodePath.show(BitMask32.bit(1))
        ## Now myNodePath will only be shown on camera2...