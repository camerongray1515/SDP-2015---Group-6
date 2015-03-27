from Plan import Plan
from Utility.CommandDict import CommandDict
import math

ERROR = 15

class MatchY(Plan):
    """Plan for aligning the robot sideways on the pitch to allow for easier interception"""

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        super(MatchY, self).__init__(world, robot)

    def isValid(self):
        """
        Current constraints are:
            - Ball must not be in the robot's zone OR the ball is in the robot's zone and has a velocity > 3
            - Robot is not already matching the ball's position
        """

        ball = self.world.ball is not None
        within_bounds = self.world.pitch.is_within_bounds(self.robot, self.world.ball.x, self.world.ball.y)

        is_matched = self.isMatched(self.robot, self.world.ball)

        return ball and not within_bounds and not is_matched and (not self.robot.is_busy())


    def nextCommand(self):
        ball_y = self.world.ball.y
        zone = self.world.pitch.zones[self.robot.zone]


        zone = self.world.pitch.zones[self.robot.zone]
        command = self.go_to_asym(zone.center()[0], ball_y, max_speed=100, min_speed=50)
        return command


    def isMatched(self, robot, ball):
        return math.fabs(robot.y - ball.y) < ERROR 


    def __str__(self):
        return "match y"
