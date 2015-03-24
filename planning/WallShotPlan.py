from Plan import Plan
from Polygon.cPolygon import Polygon
import math
import consol

class WallShotPlan(Plan):
    "Plan for the robot to take a shot at goal"

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        return super(WallShotPlan, self).__init__(world, robot)

    def isValid(self):
        """
        Current constraints are:
            - Robot must have the ball
        """
        return self.robot.has_ball(self.world.ball) 

    def nextCommand(self):
        (move_x, move_y) = self.get_move_point()
        consol.log("(mx, my)", (gx,gy), "WallShotPlan")

        #If we are not at the move target, move there:
        distance = self.robot.get_euclidean_distance_to_point(move_x, move_y)
        consol.log("Distance to move target", distance, "WallShotPlan")
        if distance < 25:
            command = self.go_to_asym(move_x, move_y, forward=False, max_speed = 85, min_speed=50)
            return command
        #Otherwise, make a wall shot:
        else:
            rotation_error = math.pi/15         
            #Aim at x=centre of opponents zone, y=nearer edge of pitch
            target_x = self.world.pitch.zones[self.world.their_defender.zone].center()[0]
            if self.robot.y > self.world.pitch.zones[self.robot.zone].center()[1]:
                target_y = self.max_y
            else:
                target_y = 0
            if self.robot.get_dot_to_target(target_x, target_y) > 0.95:
                self.finished = True
                self.robot.catcher = "open"
                return self.kick()
            else:
                command = self.look_at(target_x, target_y, max_speed=55, min_speed=40)
                return command

    def get_move_point(self):
        """
        Returns (mx, my), the closer point of (centre, 1/4 height) and (centre, 3/4 height)
        """
        mx = self.world.pitch.zones[self.robot.zone].center()[0]
        centre_y = self.world.pitch.zones[self.robot.zone].center()[1]
        robot_y = self.robot.y

        if robot_y < robot_y:
            my = 0.25 * self.max_y
        else:
            my = 0.75 * self.max_y

        return (mx, my)

    def __str__(self):
        return "WallShot plan"