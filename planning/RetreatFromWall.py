from Plan import Plan
from Polygon.cPolygon import Polygon
import math
import consol

class RetreatFromWall(Plan):
    """Plan for the robot to move back from the wall. Intended for use after the robot
    has grabbed the ball, to stop it getting stuck when rotating to shoot"""

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        return super(RetreatFromWall, self).__init__(world, robot)

    def isValid(self):
        """
        Current constraints are:
            - Robot must have the ball
            - Robot must be within 50px of the wall
        """
        consol.log("distance_from_wall", self.distance_from_wall(), "RetreatFromWall")
        is_valid = self.robot.has_ball(self.world.ball) and self.distance_from_wall() <= 50 and (not self.robot.is_busy())
        consol.log("is_valid", is_valid, "RetreatFromWall")
        return is_valid

    def nextCommand(self):
        centre_x = self.world.pitch.zones[self.robot.zone].center()[0]
        centre_y = self.world.pitch.zones[self.robot.zone].center()[1]
        command = self.go_to_asym(centre_x, centre_y, forward=False, max_speed = 85, min_speed=50)
        if self.distance_from_wall() > 50:
            self.finished = True
        return command


    def distance_from_wall(self):
        cur_y = self.robot.y
        bottom_dist = self.robot.y
        top_dist = self.max_y - self.robot.y
        if top_dist < bottom_dist:
            return top_dist
        else:
            return bottom_dist

    def __str__(self):
        return "RetreatFromWall"
