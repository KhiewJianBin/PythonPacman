from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode

import random

def randomReal(max):
    return max * random.uniform(0,10000) / 10000.0

def randomBinomial(max):
    return randomReal(max)-randomReal(max)

class SteeringOutput(object):
    def __init__(self):
        #linear force in 3 space.
        self.linear = Vec3(0,0,0)

        #angular acceleration
        self.angular = 0.0

class Kinematic(object):
    """The base class for all kinematic movement behaviours."""
    def __init__(self,np):
        #The character who is moving.
        self.np = np
    
    def position(self):
        return self.np.getPos()

    def velocity(self):
        return self.np.node().getLinearVelocity()

    #def move(self,linear):
    #    f = Vec3(linear.getX(),linear.getY(),linear.getZ())    
    #    self.np.node().setActive(True,True)
    #    orientation = Point3(0,0.5,0)
    #    q = self.np.getQuat()
    #    orientation = q.xform(orientation)
    #    orientation = Point3(orientation.getX(),orientation.getY(),orientation.getZ())
    #    self.np.node().applyForce(f,orientation) 
    def move(self,linear):
        Velocity = Vec3(linear.getX(),linear.getY(),linear.getZ())    
        self.np.node().setActive(True,True)
        self.np.node().setLinearVelocity(Velocity) 

    def getOrientationAsVector(self):
        return self.np.getQuat().getForward()    

class TargetedKinematicMovement(Kinematic):
    '''The target may be any vector (i.e. it might be something
       that has no orientation, such as a point in space).
    '''
    def __init__(self,np,position= Vec3(10,0,1)):
        #The character who is moving.
        self.np = np

        #The target
        self.target= position

class KinematicSeek(TargetedKinematicMovement):
    '''Kinematic seek moves at full speed towards its target at each
     * frame.
    '''
    def getSteering(self):
        # First work out the direction
        output = SteeringOutput()
        output.linear = self.target-self.np.getPos();

        if (output.linear.getX()*output.linear.getX() > output.linear.getY()*output.linear.getY()):
            output.linear.setY(0)
            output.linear.setZ(0)
            output.linear.normalize()
            output.linear *= 10
        elif (output.linear.getX()*output.linear.getX() < output.linear.getY()*output.linear.getY()):
            output.linear.setX(0)
            output.linear.setZ(0)
            output.linear.normalize()
            output.linear *= 10
        # If there is no direction, do nothing
        #if (output.linear.lengthSquared() > 0):
        #    if output.linear.getX()
        #    
        #    
        return output

    def update(self):
        self.move(self.getSteering().linear)

class KinematicFlee(TargetedKinematicMovement):
    '''Kinematic seek moves at full speed towards its target at each
     * frame.
    '''
    def getSteering(self):
        # First work out the direction
        output = SteeringOutput()
        output.linear = self.position()-self.target;

        # If there is no direction, do nothing
        if (output.linear.lengthSquared() > 0 and output.linear.lengthSquared() < 100):
            output.linear.normalize()
            output.linear *= 5
        return output

    def update(self):
        self.move(self.getSteering().linear)

class KinematicArrive(TargetedKinematicMovement):
    '''Kinematic seek moves at full speed towards its target at each
     * frame.
    '''
    timeToTarget = 3.0
    radius=2.0
    def getSteering(self):
        # First work out the direction
        output = SteeringOutput()
        output.linear = self.target-self.np.getPos();

        # If there is no direction, do nothing
        if (output.linear.lengthSquared() < self.radius*self.radius):
            #output.linear=-self.np.node().getLinearVelocity()*5
            self.np.node().setLinearVelocity(Vec3(0,0,0))
        else:
            output.linear*= (10.0 / self.timeToTarget)
            if (output.linear.lengthSquared() > 900):
                output.linear.normalize()
                output.linear *= 20
        return output

    def update(self):
        self.move(self.getSteering().linear)

class KinematicWander(TargetedKinematicMovement):
    '''Kinematic seek moves at full speed towards its target at each
     * frame.
    '''
    def getSteering(self):
        # First work out the direction
        output = SteeringOutput()
        output.linear = self.np.getQuat().getForward();
        output.linear *= 3
        #Using random Binomial distribution
        change = randomBinomial(50.0);
        self.move(output.linear)
        self.np.node().applyTorque(Vec3(0,0,change))
        #Update position of target
        self.model.setPos(self.target)
        return output

    def update(self):
        self.move(self.getSteering().linear)