from Plan import Plan, DISTANCE_ERROR
from Utility.CommandDict import CommandDict
import utilities
from math import tan, pi

BALL_VELOCITY = 3


class InterceptPlan(Plan):
    """Defines the idle plan. This is the fallback plan the robot will end up in if the planner cannot find a suitable plan."""

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        super(InterceptPlan, self).__init__(world, robot)

    def isValid(self):
        """
        Returns true if the ball is moving fast and we are not holding the ball.

        """
        if self.world.ball != None and self.world.ball.velocity != None:
            return self.world.ball.velocity > BALL_VELOCITY #TODO add a check for if we are holding the ball or not.
        else:
            return False

    def isFinished(self):
        """
        This method is overridden here because we always want to transition out of the Idle plan if we can.
        """
        if self.world.ball != None:
            y = utilities.predict_y_intersection(self.world,self.robot.x,self.world.ball,bounce = True)
            if y != None:
                return abs(y-self.robot.y) < DISTANCE_ERROR

        return False

    def nextCommand(self):
        y = utilities.predict_y_intersection(self.world,self.robot.x,self.world.ball,bounce = True)
        if y != None:
            x = find_x(self.robot,y)
            if self.world.pitch.is_within_bounds(self.robot,x,y):
                return self.go_to_intercept(x,y)
            else:
                command = self.rotate_to(self.robot.angle+pi/2)
                if command:
                    return command
                return CommandDict.stop()
        print "y is none"
        return CommandDict.stop()


    def go_to_intercept(self,x,y):
        # Forward direction is < pi/2 on a circle.
        distance = self.robot.get_euclidean_distance_to_point(x,y)
        command = self.go_forward(distance) if (abs(self.robot.get_rotation_to_point(x,y)) < pi/2) else self.go_backward(distance)
        if command:
            return command
        return CommandDict.stop()



def find_x(robot,y):
    dy = y - robot.y
    x = dy * tan(robot.angle)
    return x
