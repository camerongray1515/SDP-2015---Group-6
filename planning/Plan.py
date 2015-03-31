from abc import ABCMeta, abstractmethod
import math
from math import pi, fabs
import consol
import numpy as np
from random import random

from Utility.CommandDict import CommandDict


# Constants for the rotation/distance movement fudge factors
ROTATION_ERROR = pi/12
DISTANCE_ERROR = 43

class Plan(object):
    def initi(self, prevPlan):
        pass

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
        zone = self.world.pitch.zones[self.robot.zone][0] 
        self.min_x = 10000
        self.max_x = 0
        for point in zone:
            x_coord = point[0]
            if self.min_x > x_coord:
                self.min_x = x_coord
            if self.max_x < x_coord:
                self.max_x = x_coord
        self.min_y = 10000
        self.max_y = 0
        for point in zone:
            y_coord = point[1]
            if self.min_y > y_coord:
                self.min_y = y_coord
            if self.max_y < y_coord:
                self.max_y = y_coord


    @property
    def midX(self):
        return self.world.pitch.zones[self.robot.zone].center()[0]

    @property
    def midY(self):
        return self.world.pitch.zones[self.robot.zone].center()[1]


    def get_ball_pos(self):
        return (self.world.ball.x, self.world.ball.y)


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
    def reset(self):
        self.finished = False

    def isFinished(self):
        return self.finished

    def isAligned(self, robot):
        return math.fabs(robot.angle - math.pi/2) < ROTATION_ERROR or math.fabs(robot.angle - 3 * math.pi/2) < ROTATION_ERROR

     # rotate to a specific angle with angle dependent speed (auto calibrating)
    # angle input is absolute angle not relative like in rotate_to



    def rotate_fade(self, angle, min_speed = 50, max_speed = 80):
        """
        Generates commands for the robot to rotate to a specific angle
        :param angle: Radians to turn to
        :return: a CommandDict with the next command
        """

        min_rot_speed = min_speed
        max_rot_speed = max_speed

        av = Plan.angle_to_vector(angle)
        rv = Plan.angle_to_vector(self.robot.angle)


        dot = np.dot(av, rv)
        cross = np.cross(rv, av)

        consol.log('dot', dot, 'Plan')
        consol.log('cross', cross, 'Plan')

        speed = np.interp(dot, [0.0, 1.0], [max_rot_speed, min_rot_speed])

        direction = "Right" if cross < 0 else "Left"
        kick = "None"
        return CommandDict(speed, direction, kick)


    def look_at(self, x, y, min_speed = 50, max_speed = 80):
        """
        Generates commands for the robot to rotate to a specific angle
        :param x: X coordinate of the point to turn to
        :param y: Y coordinate of the point to turn to
        :return:  returns a CommandDict with the next command
        """

        min_rot_speed = min_speed
        max_rot_speed = max_speed


        rob_pos = np.array([self.robot.x, self.robot.y])
        target_pos = np.array([x, y])
        vec = target_pos - rob_pos
        av = vec / np.linalg.norm(vec)

        rv = Plan.angle_to_vector(self.robot.angle)


        dot = np.dot(av, rv)
        cross = np.cross(rv, av)

        consol.log('dot', dot, 'Plan')
        consol.log('cross', cross, 'Plan')

        speed = np.interp(dot, [0.0, 1.0], [max_rot_speed, min_rot_speed])

        direction = "Right" if cross < 0 else "Left"
        kick = "None"
        return CommandDict(speed, direction, kick)


    # When forward is true the robot will not consider going backwards to reach its target. 
    # Useful for when
    #mid_x approach white lines orthogonally
    #mid_y approach white walls orthogonally
    def go_to_asym(self, x, y, forward = False, max_speed = 100, min_speed = 70, mid_x = False, mid_y = False, sharp_arc = False):
        """
    if forward is set to true the robot will only attempt to reach its goal going forward
    useful for picking up the ball and shooting etc
    :param: x
    :param: y
    :param: forward
    :param: max_speed
    :param: min_speed
        """

        # slow down at pi rotation
        #slow_down = 50

        fade_distance = 100
        fade_distance_min = 20




        distance = self.robot.get_euclidean_distance_to_point(x, y)
        #if(distance):
        #    distance = 0.1

        max_e_dist = 30
        y = np.clip(y, max_e_dist, self.max_y - max_e_dist)

        if(mid_x):
            dy = fabs(self.robot.y - y)

            x = np.interp(dy, [50, 100], [x, self.midX])

        if(mid_y):
            dx = fabs(self.robot.x - x)

            y = np.interp(dx, [30, 100], [y, self.midY])

        dist_edge = self.get_distance_from_edges()

        consol.log('edge distance', dist_edge, 'Plan')
        #if dist_edge < 20:
        #    distance = min(distance,dist_edge)


        angle = self.robot.get_rotation_to_point(x, y)


        consol.log('distance', distance, 'Plan')

        rob_pos = np.array([self.robot.x, self.robot.y])
        target_pos = np.array([x, y])
        vec = target_pos - rob_pos
        av = vec / np.linalg.norm(vec)

        rv = Plan.angle_to_vector(self.robot.angle)

        consol.log('rotating to(vec)', av, 'Plan')
        consol.log('robot rotation(vec)', rv, 'Plan')


        dot = self.robot.get_dot_to_target(x, y)

        # if forward is not enforced and it is closer to go backwards


        dir = 1.0

        if not forward and dot < 0:
            rv *= -1.0
            dot = np.dot(av, rv)
            dir = -1.0



        cross = np.cross(rv, av)


        avr_speed = np.interp(distance, [fade_distance_min, fade_distance], [min_speed, max_speed]) * dir

        consol.log('avr speed', avr_speed, 'Plan')



        scale_speed_far = np.interp(dot, [0.0, 1.0], [-1.0, 0.9])

        scale_speed_near = np.interp(dot, [0.0, 0.9, 1.0], [-1.0, -0.8, 0.9])



        scale_speed = np.interp(distance, [fade_distance_min, fade_distance], [ scale_speed_near, scale_speed_far])

        if sharp_arc:
            scale_speed = scale_speed_far

        consol.log('scale speed', scale_speed, 'Plan')

        delta_angle = self.robot.get_rotation_to_point(x, y)
        consol.log('delta angle', delta_angle, 'Plan')


        consol.log('dot', dot, 'Plan')
        consol.log('cross', cross, 'Plan')



        sl = avr_speed
        sr = avr_speed

        if cross * dir > 0:
            sl *= scale_speed
        else:
            sr *= scale_speed



        direction = "Forward"
        kick = "None"
        cd = {}

        cd["speed"] = sl
        cd["direction"] = direction
        cd["kick"] = kick
        cd["speedr"] = sr

        return cd

    @staticmethod
    def angle_to_vector(angle):
        x = math.cos(angle)
        y = math.sin(angle)
        return np.array([x,y])


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
        speed = 50 if angle > 3 * ROTATION_ERROR else 45
        direction = "Right" if angle < 0 else "Left"
        kick = "None"
        return CommandDict(91, direction, kick)

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

    def stop(self):
        """
        Generates a stop command
        """
        return CommandDict.stop()

    
    def get_distance_from_edges(self):
        close_max_x = self.max_x - self.robot.x
        close_min_x = self.robot.x - self.min_x
        close_max_y = self.max_y - self.robot.y
        close_min_y = self.robot.y - self.min_y
        return min(min(close_max_x,close_min_x), min(close_max_y, close_min_y))

    

    # def __str__(self):
    #     return self.__name__
   

    


