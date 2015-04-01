from Plan import Plan
from Utility.CommandDict import CommandDict
from Control import robot_api
import consol
from time import time

DISTANCE_ERROR = 40
class GrabBallEverywhere(Plan):
    """Plan for the robot navigating to and grabbing the ball."""


    # states 'pick' 'pick wall' 'goto center'
    def initi(self, prevPlan):
        consol.log_time('GrabAll', 'initi')

        robot_api.robot_api.prepare_catch()
        self.robot.catcher = "prepared"
        self.state = 'pick'
        self.nstate = 'pick'
        self.robot.hball = False





    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        self.state = 'pick'
        self.nstate = 'pick'


        super(GrabBallEverywhere, self).__init__(world, robot)

    def isValid(self):
        """
        Current constraints are:
            - Ball must be within the robot's zone
            - Robot must not have the ball
            - Ball must not be near the walls
            - NOT IMPLEMENTED : Robot must be within its zone - though this -should- be handled by the go_to function. This may be useful for some kind of state-reset if we get out of the zone somehow
        """
        near_dist = 40 # Note DO NOT CHANGE WITHOUT ALSO CHANGING IN GrabBallNearWallPlan
        #if self.world.ball is not None and self.world.ball.velocity <= 3:
        if self.world.ball is not None:
            return self.world.pitch.is_within_bounds(self.robot, self.world.ball.x, self.world.ball.y) and \
            (not self.robot.hball)
        return False


    def catch(self):
        self.finished = True
        self.robot.catcher = "closed"
        self.robot.hball = True
        #self.robot.set_busy_for(1.1)
        return CommandDict.catch()

    def close(self):
        self.robot.catcher = "closed"

    def res_timer(self):
        self.timer = time()

    def get_time(self):
        return time() - self.timer


    def nextCommand(self):
        maxs =70
        mins = 50

        #compute inputs

        distance = self.robot.get_euclidean_distance_to_point(self.world.ball.x, self.world.ball.y)
        dot = self.robot.get_dot_to_target(self.world.ball.x, self.world.ball.y)

        ball_catchable = distance < DISTANCE_ERROR and dot > 0.96 #input

        wall_ball = self.ball_distance_from_wall() < 50 #input

        near_center = self.robot.get_euclidean_distance_to_point(self.world.ball.x, self.midY) < 80 #input


        consol.log('state', self.state, 'GrabAll')
        #FSM body

        command = None



        if self.state == 'pick':
            '''
            if wall_ball:

                self.robot.catcher = "closed"

                self.nstate = 'goto center'
            '''
            if ball_catchable:
                command = self.catch()
            else:
                command = self.go_to_asym(self.world.ball.x, self.world.ball.y, forward=True, max_speed = maxs, min_speed=mins, mid_x=True)




        elif self.state == 'goto center':
            if near_center:
                self.nstate = 'pick wall'
                #command = CommandDict.catch()


            elif ball_catchable:
                command = self.catch()

            elif not wall_ball:
                self.nstate = 'pick'
            else:
                command = self.go_to_asym(self.world.ball.x, self.midY, forward=True, max_speed = 90, min_speed=mins)



        elif self.state == 'pick wall':
            consol.log_time('GrabAll', 'wall move')
            if not wall_ball:
                self.nstate = 'pick'
            elif ball_catchable:
                command = self.catch()

            else:
                command = self.go_to_asym(self.world.ball.x, self.world.ball.y, forward=True, max_speed = maxs, min_speed=mins, mid_y= True)



        '''
        if self.robot.catcher != "prepared":
            self.robot.catcher = "prepared"
            return CommandDict.prepare()
        '''

        # If we need to move to the ball, then get the command and return it
        # command = self.go_to(self.world.ball.x, self.world.ball.y, speed=75)




        self.state = self.nstate

        return command

    def ball_distance_from_wall(self):

        "Returns the distance of the ball from the wall nearest to it."
        cur_y = self.world.ball.y
        bottom_dist = cur_y
        top_dist = self.max_y - cur_y
        consol.log("top_dist", top_dist, "GrabAll")
        consol.log("bottom_dist", bottom_dist, "GrabAll")
        if top_dist < bottom_dist:
            return top_dist
        else:
            return bottom_dist

    def __str__(self):
        return "grab ball plan"
