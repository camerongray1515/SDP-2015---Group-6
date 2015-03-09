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

        if self.world.ball is not None and (not self.world.pitch.is_within_bounds(self.robot, self.world.ball.x, self.world.ball.y)\
                or self.world.ball.velocity > 3):
            return not self.isMatched(self.robot, self.world.ball)
        return False

    def nextCommand(self):
        ball_y = self.world.ball.y
        robot_y = self.robot.y
        robot_angle = self.robot.angle
        predicted_x = (ball_y-robot_y) * math.atan(robot_angle)
        print predicted_x
        goto_x = self.robot.x + predicted_x
        distance = self.robot.get_euclidean_distance_to_point(goto_x, robot_y)
        # check if the x,y coordinate we would end up in if we matched y is within bounds
        # if it's outside use go_to to match the y position and a central x position
        if (not self.world.pitch.is_within_bounds(self.robot,goto_x, ball_y)):
            zone = self.world.pitch.zones[self.robot.zone]
            command = self.go_to(zone.center()[0], ball_y)
            if command:
                return command
            else:
                return CommandDict.stop()
        if robot_angle <= math.pi:
            if ball_y > robot_y:
                command = self.go_forward(distance)
                # Pass the distance to go forward and backward so it slows down closer to the target
            else:
                command = self.go_backward(distance)
        else:
            if ball_y < robot_y:
                command = self.go_forward(distance)
            else:
                command = self.go_backward(distance)
        if command:
            return command
        else:
            return CommandDict.stop()

    def isMatched(self, robot, ball):
        return math.fabs(robot.y - ball.y) < ERROR 


    def __str__(self):
        return "match y"