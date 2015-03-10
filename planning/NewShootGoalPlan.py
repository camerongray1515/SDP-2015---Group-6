from Plan import Plan
import math
from Utility.CommandDict import CommandDict
import pdb

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

        # Returns list of points in order: xmin, xmax, ymin, ymax
        goal_points = self.world.their_goal.get_polygon().boundingBox()
        x_min = goal_points[0]
        x_max = goal_points[1]
        y_min = goal_points[2]
        y_max = goal_points[3]

        # Center of the goal
        (gx, gy) = ((x_max + x_min)/2, (y_min + y_max)/2)

        # for each 5 pixels between start of goal to end of goal 
        # check if isBLocked
        # if false, rotate towards the unblocked point and shoot

        # store position we are aiming at, if it becomes blocked pick a new one

        # if we go through the whole loop without finding a spot
        # move to a different positon and try agian

        #find their robot position pick top or bottom, move in that direction (make sure not to go into the wall)


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