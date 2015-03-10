from Plan import Plan
import math
from Utility.CommandDict import CommandDict

class NewShootGoalPlan(Plan):
    """Plan for the robot shooting the ball."""

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        return super(NewShootGoalPlan, self).__init__(world, robot)


    def isValid(self):
        """
        Current constraints are:
            - Robot must have the ball
        """
        # TODO/DISCUSS how are we going to do this? Options currently are either a set state or read directly from the vision system
        # Either way the grabber state is not currently updated, need to look through the team 7 code and fix this
        return self.robot.has_ball(self.world.ball)

    def nextCommand(self):
        their_defender = self.world.their_defender

        # Center of the robot's zone
        (x, y) = self.world.pitch.zones[self.robot.zone].center()

        # Center of the goal
        (gx, gy) = (self.world.their_goal.get_polygon()[0][0], self.world.pitch.height / 2)


        angle = self.robot.get_rotation_to_point(gx, gy)
        command = self.rotate_to(angle, fudge=0.2)
        # Check if we're done rotating
        if command is not False:
            return command
        # Otherwise kick the ball
        else:
            self.finished = True
            self.robot.catcher = "open"
            return self.kick()




    def blocked(self, target_x, target_y, obstacle_x, obstacle_y, obstacle_width=30):
        d_y = self.robot.y - target_y
        d_x = self.robot.x - target_x
        m = d_y/d_x
        c = self.robot.y - m*self.robot.x
        #Compare y-coords when x is equal:
        ball_y_at_obstacle = m*obstacle_x + c
        if math.fabs(ball_y_at_obstacle - obstacle_y)<obstacle_width:
            return True
        return False

    def __str__(self):
        return "shoot goal plan"
