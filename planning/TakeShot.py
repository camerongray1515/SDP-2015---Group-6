from Plan import Plan
from Polygon.cPolygon import Polygon
import math
import consol

class TakeShot(Plan):
    "Plan for the robot to take a shot at goal"

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        return super(TakeShot, self).__init__(world, robot)

    def isValid(self):
        """
        Current constraints are:
            - Robot must have the ball
            (- Shot must not be blocked) - not implemented now for simplicity
        """
        return self.robot.has_ball(self.world.ball) #and self.has_clear_shot()

    def nextCommand(self):
        rotation_error = math.pi/15         
        their_defender = self.world.their_defender
        (gx, gy) = self.goalCentre()
        consol.log("(gx, gy)", (gx,gy), "TakeShot")

        #If we are facing the goal, shoot!
        consol.log("Scalar product", self.robot.get_dot_to_target(gx, gy), "TakeShot")
        if self.robot.get_dot_to_target(gx, gy) > 0.95:
            self.finished = True
            self.robot.catcher = "open"
            return self.kick()
        else:
            command = self.look_at(gx, gy, max_speed=55, min_speed=40)
            return command

    def goalCentre(self):
        """
        Returns (gx, gy), the coordinates of the centre of the other team's goal.
        """
        # boundingBox returns list of points in order: xmin, xmax, ymin, ymax
        goal_points = Polygon(self.world.their_goal.get_polygon()).boundingBox()
        x_min = goal_points[0]
        x_max = goal_points[1]
        y_min = goal_points[2]
        y_max = goal_points[3]

        # Centre of the goal
        (gx, gy) = ((x_max + x_min)/2, (y_min + y_max)/2)
        return (gx, gy)

    def __str__(self):
        return "TakeShot plan"
