from Plan import Plan
import math
from Utility.CommandDict import CommandDict
import planning.utilities

class PassPlan(Plan):
    """Plan for the robot passing to the its teammate
       Meant to be used only by the defender"""

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        return super(PassPlan, self).__init__(world, robot)


    def isValid(self):
        """
        Current constraints are:
            - Robot must have the ball
        """
        # TODO/DISCUSS how are we going to do this? Options currently are either a set state or read directly from the vision system
        # Either way the grabber state is not currently updated, need to look through the team 7 code and fix this
        return self.robot.has_ball(self.world.ball)

    def nextCommand(self):
        their_atk = self.world.their_attacker

        # Center of the robot's zone
        (x,y) = self.world.pitch.zones[self.robot._zone].center()

        # Aim at friendly attacker position
        (gx,gy) = (self.world.our_attacker.x, self.world.our_attacker.y)

        #isBlocked = self.blocked(gx, gy, their_atk.x, their_atk.y, self.robot.x, self.robot.y)
        isBlocked = planning.utilities.is_shot_blocked(self.world, self.robot, self.world.their_attacker)
        if not isBlocked: # if our pass path is not blocked
            angle = self.robot.get_rotation_to_point(gx, gy)
            command = self.rotate_to(angle, fudge=0.1)
            # Check if we're done rotating
            if not command == False:
                return command
            # Otherwise kick the ball
            else:
                self.finished = True
                self.robot.catcher = "open"
                return self.kick(80)
        print "BLOCKED!"

        (cent_x, cent_y) = self.world.pitch.zones[self.robot.zone].center() # find the middle y position of the zone

        if their_atk.y >= cent_y:
            # if their attacker is on the top half we want to go toward the bottom half of the pitch
            goto_y = cent_y - cent_y/2
        else:
            goto_y = cent_y + cent_y/2

        command = self.go_to(cent_x, goto_y)
        if command:
            return command
        else:
            return CommandDict.stop()



        # closely_marked = False # Closely marked = their attacker is close to our robot
        # #If closely marked, try and shoot around the opponent
        # #If not, move until a clear shot is possible
        #
        # if math.fabs(their_atk.x - self.robot.x) < 150:
        #         closely_marked = True
        #
        # if closely_marked == True:
       	#     gx = their_atk.x
        #     gy = 0
        #     angle = self.robot.get_rotation_to_point(gx, gy)
        #     command = self.rotate_to(angle, fudge=0.3)
        #     # Check if we're done rotating
        #     if not command == False:
        #         return command
        #     # Otherwise kick the ball
        #     else:
        #         self.finished = True
        #         self.robot.catcher = "open"
        #         return self.kick(70)
        #
        # else:
        #     command =  self.go_to(self.robot.x, self.robot.y + 150)
        #     if command:
        #         return command
        #     return CommandDict.Stop()



    @staticmethod
    def blocked(target_x, target_y, obstacle_x, obstacle_y, robot_x, robot_y, obstacle_width=40):
        d_y = robot_y - target_y
        d_x = robot_x - target_x
        
        # Catch div by zero
        if d_x == 0:
            d_x = 0.0001 

        m = d_y/float(d_x)
        c = robot_y - m*robot_x
        #Compare y-coords when x is equal:
        ball_y_at_obstacle = m*obstacle_x + c
        if math.fabs(ball_y_at_obstacle - obstacle_y)<obstacle_width:
            return True
        return False

    def __str__(self):
        return "pass plan"