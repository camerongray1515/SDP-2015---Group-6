__author__ = 's1210443'

from Plan import Plan
from Polygon.cPolygon import Polygon
import math
import consol
from time import time
from Utility.CommandDict import CommandDict

#todo make invalid when ball too far away
class ShootAll(Plan):
    "Plan for the robot to take a shot at goal"


    # states: 'go1', 'go2' 'swing' 'wall', 'wallsh'

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        self.res_timer()

        self.state = 'init'
        self.nstate = 'init'
        return super(ShootAll, self).__init__(world, robot)


    def catch(self):
        self.finished = True
        self.robot.catcher = "closed"
        #self.robot.set_busy_for(1.1)
        return CommandDict.catch()


    def res_timer(self):
        self.timer = time()

    def get_time(self):
        return time() - self.timer


    def initi(self, prev_plan):
        self.res_timer()
        self.state = 'init'
        self.nstate = 'init'
        consol.log_time('ShootAll', 'initi')



    def isValid(self):
        """
        Current constraints are:
            - Robot must have the ball
            - Shot must not be blocked
        """
        #return True
        consol.log("Clear shot", self.has_clear_shot(), "ShootAll")
        ball_dist = self.robot.get_euclidean_distance_to_point(*self.get_ball_pos()) > 80 and self.world.ball.x != 0
        if ball_dist:
            self.robot.hball = False
        return self.robot.hball and not ball_dist


    def kick_new(self):

        self.robot.catcher = "open"
        #self.robot.set_busy_for(1.1)
        self.robot.hball = False
        return self.kick()

    def move_to(self,x ,y):
        return self.go_to_asym(x, y, forward=True, max_speed = 80, min_speed=50, sharp_arc=True, mid_x= True)

    def arrived(self, x, y):
        consol.log('distance to destination', self.robot.get_euclidean_distance_to_point(x, y), 'ShootAll')

        return self.robot.get_euclidean_distance_to_point(x, y) < 50

    def nextCommand(self):
        # Plan is always finished to allow switching to other plans at any point.
        self.finished = True
        rotation_error = math.pi/15
        (gx, gy) = self.goalCentre()
        consol.log("(gx, gy)", (gx,gy), "TakeShot")

        command = None


        dedge = 60
        timeout = self.get_time() > 1.5

        consol.log('state', self.state, 'ShootAll')
        if self.state == 'init':
            if timeout:
                self.nstate = 'go1'
            command = CommandDict.stop()
        elif self.state == 'go1':
            p = (self.midX, self.max_y -dedge)
            if self.arrived(*p):
                self.nstate = 'go2'
            elif self.has_clear_shot():
                self.nstate = 'swing'
                self.res_timer()
            else:
                command = self.move_to(*p)

        elif self.state == 'go2':
            p = (self.midX, dedge)
            if self.arrived(*p):
                self.nstate = 'go1'
            elif self.has_clear_shot():
                self.nstate = 'swing'
                self.res_timer()
            else:
                command = self.move_to(*p)

        elif self.state == 'swing':

            p = self.goalCentre()
            #if not self.has_clear_shot():
            #    self.nstate = 'go1'
            #else:
            if self.robot.get_dot_to_target(gx, gy) > 0.95:
                command = self.kick_new()
                self.res_timer()
                self.nstate = 'wait'
            else:
                command = self.look_at(gx, gy, max_speed=60, min_speed=40)

        elif self.state == 'wait':
            if timeout:
                self.robot.hball = False
                self.finished = True
            command = CommandDict.stop()

        '''
        elif self.state == 'swing':

            p = self.goalCentre()
            if not self.has_clear_shot():
                self.nstate = 'wall'
            elif timeout:
                command = self.kick_new()
            else:
                command = self.move_to(*p)


        elif self.state == 'testwall':
            if timeout:
                self.nstate = 'wall'
            command = self.catch()

        elif self.state == 'wall':
            p = (self.midX, self.midY)
            if self.arrived(*p):
                self.nstate = 'wallsh'
                self.res_timer()
            else:
                command = self.move_to(*p)

        elif self.state == 'wallsh':
            p = ((self.robot.x + gx) * 0.5, 0.0)
            if timeout:
                command = self.kick_new()
                self.res_timer()
            else:
                command = self.move_to(*p)
        '''


        self.state = self.nstate

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

        edge = 50

        if self.robot.y < 60 or self.robot.y > self.max_y - 60:
            return False

        obstacle_width=25

        (target_x, target_y) = self.goalCentre()
        their_defender = self.world.their_defender


        #if no defender
        if their_defender._vector.x == 0:
            consol.log("clear shoot", True, "ShootAll")
            return True

        rob_y = self.robot.y

        relo = rob_y - target_y
        reld = their_defender._vector.y - target_y
        consol.log("clear shoot", relo * reld < 0.0, "ShootAll")
        return relo * reld < 0.0




        #If their defender is not on the pitch, return True:
        consol.log("defender pos", (their_defender.x, their_defender.y), "ShootAll")
        consol.log("defender angle", their_defender.angle, "ShootAll")
        if their_defender._vector.x == their_defender._vector.y and their_defender._vector.x == 0:
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
        return "ShootAll plan"
