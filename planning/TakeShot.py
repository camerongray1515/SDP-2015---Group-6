from Plan import Plan
import math
import consol

class TakeShot(Plan):
    "Plan for the robot to take a shot at goal"

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        return super(NewShootGoalPlan, self).__init__(world, robot)

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

        #If we are facing the goal, shoot!
        if self.robot.get_dot_to_target(gx, gy) > 0.9:
            self.finished = True
            self.robot.catcher = "open"
            return self.kick()
        else:
            command = self.look_at(gx, gy, max_speed=65)
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


    








    # def blocked(self, target_x, target_y, obstacle_x, obstacle_y, obstacle_width=25):
        # "Tests if the obstacle is in the way of a shot to the target point"
        # d_y = self.robot.y - target_y
        # d_x = self.robot.x - target_x
        # m = d_y/d_x
        # c = self.robot.y - m*self.robot.x
        # #Compare y-coords when x is equal:
        # ball_y_at_obstacle = m*obstacle_x + c
        # if math.fabs(ball_y_at_obstacle - obstacle_y)<obstacle_width:
        #     return True
        # return False