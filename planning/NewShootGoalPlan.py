from Plan import Plan
import math
from Utility.CommandDict import CommandDict
from Polygon.cPolygon import Polygon
import consol
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
        goal_points = Polygon(self.world.their_goal.get_polygon()).boundingBox()
        x_min = goal_points[0]
        x_max = goal_points[1]
        y_min = goal_points[2]
        y_max = goal_points[3]

        # Center of the goal
        (gx, gy) = ((x_max + x_min)/2, (y_min + y_max)/2)
        angle1 = self.robot.get_rotation_to_point(gx, gy)
        angle = (self.robot.angle + angle1) % 2 * math.pi
        command = self.rotate_fade(angle, min_speed = 50, max_speed = 70)
        consol.log("Goal angle",angle,"Attacking")
        # Shoot for the centre of the goal if possible
        a = abs(angle-self.robot.angle)
        consol.log("Angle", a, "Attacking")
    	if abs(angle-self.robot.angle) > (math.pi / 12):
            return command
        # Otherwise kick the ball
        else:
            self.finished = True
            self.robot.catcher = "open"
            return self.kick()
        if not self.blocked(gx, gy, their_defender.x, their_defender.y):
            return self.shoot(gx, gy)
        
        # If that isn't possble check if
        # a target has been set, try that first
        if self.robot.target_y is not None:
            if not self.blocked(gx, self.robot.target_y, their_defender.x, their_defender.y):
                return self.shoot(gx, self.robot.target_y)

        # If the previous target is no longer clear, try again
        # Searches the goal in 5 pixel intervals for a clear spot
        current_y = y_min + 5
        while current_y < y_max:
            if not self.blocked(gx, current_y, their_defender.x, their_defender.y):
                self.robot.target_y = current_y
                return self.shoot(gx, current_y)
            current_y += 5

        # If there is no clear shot then pick a side (top/bottom) and move there
        if self.robot.y < their_defender.y:
            move_to_y = self.world.pitch.zones[self.robot.zone].boundingBox()[3] - 60
        else:
            move_to_y = 60

        command = self.go_to(self.world.pitch.zones[self.robot.zone].center()[0], move_to_y, speed=80)
        if not command == False:
            return command
        else:
            # If we're already there and still blocked, swap sides:
            if move_to_y == 60:
                move_to_y = self.world.pitch.zones[self.robot.zone].boundingBox()[3] - 60
            else:
                move_to_y = 60
            command = self.go_to(self.world.pitch.zones[self.robot.zone].center()[0], move_to_y, speed=80)
            if not command == False:
                return command
            else:
                print "NewShootGoalPlan failed!"



        
    def blocked(self, target_x, target_y, obstacle_x, obstacle_y, obstacle_width=25):
        d_y = self.robot.y - target_y
        d_x = self.robot.x - target_x
        m = d_y/d_x
        c = self.robot.y - m*self.robot.x
        #Compare y-coords when x is equal:
        ball_y_at_obstacle = m*obstacle_x + c
        if math.fabs(ball_y_at_obstacle - obstacle_y)<obstacle_width:
            return True
        return False

    def shoot(self, gx, gy):
        angle = self.robot.get_rotation_to_point(gx, gy)
        command = self.rotate_to(angle, fudge=0.2)
        # Check if we're done rotating
        if command is not False:
            return command
        # Otherwise kick the ball
        else:
            self.finished = True
            self.robot.catcher = "open"
            self.robot.target_y = None
            return self.kick()

    def __str__(self):
        return "shoot goal plan"
