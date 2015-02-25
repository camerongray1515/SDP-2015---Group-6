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
            - Robot is not already matching the ball's position
        """

        if self.world.ball is not None:
            return  not self.isMatched(self.robot, self.world.ball)
        return False

    def nextCommand(self):
        ball_y = self.world.ball.y
        robot_y = self.robot.y
        robot_angle = self.robot.angle
        if robot_angle <= math.pi:
            if ball_y > robot_y:
                command =  self.go_to(self.robot.x, ball_y, distance_fudge=0.2)
            else:
                return self.go_backward(70)
        else:
            if ball_y < robot_y:
                command =  self.go_to(self.robot.x, ball_y, distance_fudge=0.2)
            else:
                return self.go_backward(70)
        if not command:
            return CommandDict.stop()
        else:
            return command

    def isMatched(self, robot, ball):
        return math.fabs(robot.y - ball.y) < ERROR  