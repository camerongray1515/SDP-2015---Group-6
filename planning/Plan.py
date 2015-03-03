
from abc import ABCMeta, abstractmethod
from World import World
from Utility.CommandDict import CommandDict
from math import pi

# Constants for the rotation/distance movement fudge factors
ROTATION_ERROR = pi/8
DISTANCE_ERROR = 43

class Plan(object):
    """
    Base class for all plans. Contains virtual method stubs that child classes must implement and concrete implementations of general functions.
    Notes:
        - The isValid and isFinished functions define if the plan can still be executed and if the plan has finished executing, respectively
        - These are utilized somewhat differently by the Idle plan, in which both are always true
            - Upshot-> We can always execute the Idle plan but we have to exit it at every update
    """

    # Register this class as an abstract class
    __metaclass__ = ABCMeta

    def __init__(self, world, robot):
        """
        Constructor.
        :param world: A World object that contains the world state. Note: the given World should be updated externally, it should not happen in this class.
        :param robot: A Robot object that defines the robot this plan is attached to.
        """
        self.world = world
        self.robot = robot
        self.finished = False

    #virtual functions
    @abstractmethod
    def nextCommand(self):
        """Plan update function. Must be overridden by child classes. Should be called once per frame for an active plan.
        :return: A CommandDict containing the next command for this plan.
        """
        return NotImplemented

    @abstractmethod
    def isValid(self):
        """Plan validity function. Must be overridden by child classes. 
           :return: True if the plan can still be executed or False if it cannot"""
        return NotImplemented

    #concrete functions
    def isFinished(self):
        return self.finished
    
    def go_to(self, x, y, speed=100, distance_fudge=1):
        """
        Generates commands for the robot to navigate to a point
        :param x: x coordinate to navigate to
        :param y: y coordinate to navigate to
        :return: Returns a CommandDict with the next command if we need to move to the given point or False if there is nothing to be done
        """
        # Calculate the distance and the angle from the robot to the ball
        distance = self.robot.get_euclidean_distance_to_point(x, y)
        angle = self.robot.get_rotation_to_point(x, y)

        # DEBUG
        #print(angle)

        # If we are done rotating then go forward
        command = self.rotate_to(angle)
        if command:
            return command
        else:
            return self.go_forward(distance, speed, fudge=distance_fudge)

    def rotate_to(self, angle, fudge=1 ):
        """
        Generates commands for the robot to rotate by a specific angle
        :param angle: Radians to turn
        :param fudge: optional multiplier of the rotation error - e.g use 0.5 for double precision
        :return: False if :angle: is within ROTATION_ERROR otherwise returns a CommandDict with the next command
        """
        if abs(angle) < fudge * ROTATION_ERROR:
            return False
        speed = 70 if angle > 3 * ROTATION_ERROR else 50
        direction = "Right" if angle < 0 else "Left"
        kick = "None"
        return CommandDict(speed, direction, kick)

    def go_backward(self, distance, speed=100):
        """
        Generates commands for the robot to move backward
        :param distance: unit??? distance to target position
        :return: False if :distance: is within DISTANCE_ERROR, otherwise a CommandDict containing the next command
        """
        if distance < DISTANCE_ERROR:
            return False
        else:
            direction = "Backward"
            kick = "None"
            return CommandDict(speed, direction, kick)

    def go_forward(self, distance, speed=100, fudge=1):
        """
        Generates commands for the robot to move forward
        :param distance: unit??? distance to target position
        :return: False if :distance: is within DISTANCE_ERROR, otherwise a CommandDict containing the next command
        """
        if distance < DISTANCE_ERROR * fudge:
            return False
        else:
            speed = speed if distance > 2 * DISTANCE_ERROR else 40
            direction = "Forward"
            kick = "None"
            return CommandDict(speed, direction, kick)

    def kick(self, speed=100):
        """
        Generates a kick command with optional speed.
        """
        return CommandDict(speed, "None", "Kick")

    # def __str__(self):
    #     return self.__name__
   

    


