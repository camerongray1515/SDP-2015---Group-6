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
        return self.robot.has_ball(self.world.ball) and (not self.robot.is_busy())

    def initi(self, prev_plan):
        self.frames_before_shot = 4 #Frames to wait before shooting, to stop overshooting
        if str(prev_plan) == str(self):
            self.mx = prev_plan.mx
            self.my = prev_plan.my
            self.has_moved = prev_plan.has_moved     # Flags when the robot has moved to the correct position
            self.frames_passed = prev_plan.frames_passed
        else:
            (self.mx, self.my) = self.get_move_point()
            self.in_position = False
            self.has_moved = False
            self.frames_passed = 0

    def nextCommand(self):
        # Plan is always finished to allow switching to other plans at any point
        # E.g. making a shot if an opening is available.
        self.finished = True

        consol.log("(mx, my)", (self.mx,self.my), "WallShotPlan")

        #If we are not at the move target, move there:
        distance = self.robot.get_euclidean_distance_to_point(self.mx, self.my)
        consol.log("Distance to move target", distance, "WallShotPlan")
        if distance > 18 and not self.has_moved:
            command = self.go_to_asym(self.mx, self.my, forward=False, max_speed = 85, min_speed=50)
            return command
        #Otherwise, make a wall shot:
        else:    
            #Flag that move is complete:
            self.has_moved = True
            #Aim at x= slightly in fron of centre of opponents zone, y=nearer edge of pitch
            centre_x = self.world.pitch.zones[self.world.their_defender.zone].center()[0]
            if self.world.their_defender.zone == 0:
                target_x = centre_x 
            elif self.world.their_defender.zone == 3:
                target_x = centre_x 
            if self.robot.y > self.world.pitch.zones[self.robot.zone].center()[1]:
                target_y = self.max_y + 10
            else:
                target_y = -10

            consol.log("Shoot_target", (target_x, target_y), "WallShotPlan")
            consol.log("Dot to target", self.robot.get_dot_to_target(target_x, target_y), "WallShotPlan")
            if self.robot.get_dot_to_target(target_x, target_y) > 0.991:
                if self.frames_passed >= self.frames_before_shot:
                    self.finished = True
                    self.robot.catcher = "open"
                    self.robot.set_busy_for(1.1)
                    return self.kick()
                else:                    
                    self.frames_passed += 1
                    return self.stop()
            else:
                self.frames_passed = 0                
                command = self.look_at(target_x, target_y, max_speed=55, min_speed=40)
                return command

    def get_move_point(self):
        """
        Returns (mx, my), the closer point of (centre(ish), 1/4 height) and (centre(ish), 3/4 height)
        """
        centre_x = self.world.pitch.zones[self.robot.zone].center()[0]
        if self.world.our_attacker.zone == 1:
            mx = centre_x - 10
        elif self.world.our_attacker.zone == 2:
            mx = centre_x + 10
        centre_y = self.world.pitch.zones[self.robot.zone].center()[1]
        robot_y = self.robot.y

        if robot_y < centre_y:
            my = 0.25 * self.max_y
        else:
            my = 0.75 * self.max_y

        return (mx, my)

    def __str__(self):
        return "WallShot plan"