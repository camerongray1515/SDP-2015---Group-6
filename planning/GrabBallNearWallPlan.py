from Plan import Plan
from Utility.CommandDict import CommandDict
from Control import robot_api
import consol

DISTANCE_ERROR = 42
class GrabBallNearWallPlan(Plan):
    """
    Plan for the robot navigating to and grabbing the ball when it is near the wall
    by closing the grabber and driving into the wall.
    """

    def initi(self, prevPlan):
        # Need to record has_ball here as the check for having the ball is closed grabber - which we will need
        self.has_ball = False 
        robot_api.robot_api.catch()
        self.robot.catcher = "closed"



    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        super(GrabBallNearWallPlan, self).__init__(world, robot)

    def isValid(self):
        """
        Current constraints are:
            - Ball must be within the robot's zone
            - Robot must not have the ball
            - Ball must be near a wall
        """        
        # See if self.has_ball exists:
        if not hasattr(self, 'has_ball'):
            self.has_ball = True
            
        consol.log("Ball dist from wall", self.ball_distance_from_wall(), "GrabNearWall")
        near_dist = 40 # Note DO NOT CHANGE WITHOUT ALSO CHANGING IN GRABBALLPLAN
        if self.world.ball is not None and self.world.ball.velocity <= 3:
            isValid = self.world.pitch.is_within_bounds(self.robot, self.world.ball.x, self.world.ball.y) and \
                   ((not self.robot.has_ball(self.world.ball)) or (not self.has_ball)) and \
                   self.ball_distance_from_wall <= near_dist and (not self.robot.is_busy())
        else:
            isValid = False
        consol.log("isValid", isValid, "GrabNearWall")
        return isValid

    def nextCommand(self):

        '''
        if self.robot.catcher != "prepared":
            self.robot.catcher = "prepared"
            return CommandDict.prepare()
        '''

        # If we need to move to the ball, then get the command and return it
        # command = self.go_to(self.world.ball.x, self.world.ball.y, speed=75)

        command = self.go_to_asym(self.world.ball.x, self.world.ball.y, forward=True, max_speed = 70, min_speed=50)

        distance = self.robot.get_euclidean_distance_to_point(self.world.ball.x, self.world.ball.y)


        # this is a useful function that tells you how rotation aligns with wanted rotation
        dot = self.robot.get_dot_to_target(self.world.ball.x, self.world.ball.y)


        # if very close to ball
        if distance < DISTANCE_ERROR and dot > 0.96:
            self.finished = True
        return command

    def ball_distance_from_wall(self):

        "Returns the distance of the ball from the wall nearest to it."
        cur_y = self.world.ball.y
        bottom_dist = self.robot.y
        top_dist = self.max_y - self.robot.y


        if top_dist < bottom_dist:
            return top_dist
        else:
            return bottom_dist

    def __str__(self):
        return "GrabBallNearWallPlan"
