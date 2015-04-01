from Plan import Plan
from Utility.CommandDict import CommandDict
import math
from Polygon.cPolygon import Polygon
import MyMath
from numpy import *
from consol import log_dot, log

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

        their_defender = self.world.their_defender
        (target_x, target_y) = self.goalCentre()



        ball_y = self.world.ball.y
        ball_x = self.world.ball.x
        zone = self.world.pitch.zones[self.robot.zone]


        zone = self.world.pitch.zones[self.robot.zone]


        between = (ball_x - target_x) * (ball_x - self.midX) < 0.0


        return ball and not within_bounds and not is_matched and (not self.robot.is_busy()) or ball_x < 1.0


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



    def nextCommand(self):

        their_defender = self.world.their_defender
        (target_x, target_y) = self.goalCentre()



        ball_y = self.world.ball.y
        ball_x = self.world.ball.x
        zone = self.world.pitch.zones[self.robot.zone]


        zone = self.world.pitch.zones[self.robot.zone]


        between = (ball_x - target_x) * (ball_x - self.midX) < 0.0
        if between or ball_x < 1.0:
            def_ang = their_defender._vector.angle
            def_pos = their_defender._vector

            p1 = array( [self.midX, 0.0] )
            p2 = array( [self.midX, self.max_y] )

            ad = array([math.cos(def_ang), math.sin(def_ang)])

            p3 = array( [def_pos.x, def_pos.y] )
            p4 = array( p3 + ad)

            si = MyMath.seg_intersect( p1,p2, p3,p4)
            #log_dot(si, 'yellow', 'haha')
            #log('inter', si, 'MatchY')
            command = self.go_to_asym(zone.center()[0], si[1], max_speed=100, min_speed=50)
        else:
            command = self.go_to_asym(zone.center()[0], ball_y, max_speed=100, min_speed=50)
        return command


    def isMatched(self, robot, ball):
        return math.fabs(robot.y - ball.y) < ERROR 


    def __str__(self):
        return "match y"
