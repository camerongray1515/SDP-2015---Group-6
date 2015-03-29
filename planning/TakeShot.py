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
            - Shot must not be blocked
        """
        consol.log("Clear shot", self.has_clear_shot(), "TakeShot")
        return self.robot.has_ball(self.world.ball) and self.has_clear_shot() and (not self.robot.is_busy())

    def nextCommand(self):
        # Plan is always finished to allow switching to other plans at any point.
        self.finished = True
        rotation_error = math.pi/15         
        (gx, gy) = self.goalCentre()
        consol.log("(gx, gy)", (gx,gy), "TakeShot")

        #If we are facing the goal, shoot!
        consol.log("Scalar product", self.robot.get_dot_to_target(gx, gy), "TakeShot")
        if self.robot.get_dot_to_target(gx, gy) > 0.991:
            self.finished = True
            self.robot.catcher = "open"
            self.robot.set_busy_for(1.1)
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

    def has_clear_shot(self):
        obstacle_width=25

        (target_x, target_y) = self.goalCentre()
        their_defender = self.world.their_defender

        #If their defender is not on the pitch, return True:
        if their_defender.x == their_defender.y and their_defender.x == 0:
            return True

        obstacle_x = their_defender.x
        obstacle_y = their_defender.y

        d_y = self.robot.y - target_y
        d_x = self.robot.x - target_x
        if d_x == 0:
            d_x = 0.1
        m = d_y/float(d_x)
        c = self.robot.y - m*self.robot.x
        #Compare y-coords when x is equal:
        ball_y_at_obstacle = m*obstacle_x + c
        if math.fabs(ball_y_at_obstacle - obstacle_y)<obstacle_width:
            return False
        return True

    def __str__(self):
        return "TakeShot plan"
