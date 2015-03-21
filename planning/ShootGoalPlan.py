from Plan import Plan
import math
from Utility.CommandDict import CommandDict
import pdb
import consol

class ShootGoalPlan(Plan):
    """Plan for the robot shooting the ball."""

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        return super(ShootGoalPlan, self).__init__(world, robot)


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

        isBlocked = self.blocked(gx, gy, their_defender.x, their_defender.y)

        consol.log('Blocked', isBlocked, 'Shoot Goal Plan')
        if not isBlocked:
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


        close_to_goal = False
        center = self.world.pitch.zones[self.world.their_defender.zone].center()
        if their_defender.x < 250:
            if their_defender.x < center[0]:
                close_to_goal = True
        else:
            if their_defender.x > center[0]:
                close_to_goal = True

        if close_to_goal == True:
            gy = gy - 75
            angle = self.robot.get_rotation_to_point(gx, gy)
            command = self.rotate_to(angle, fudge=0.2)
            # Check if we're done rotating
            if not command == False:
                return command
            # Otherwise kick the ball
            else:
                self.finished = True
                self.robot.catcher = "open"
                return self.kick()

        else:
            #TODO
            #if self.robot.x is out of it's zone:
            #   target_x = centre of robot's zone
            #else:
            #   target_x = robot.x
            if their_defender.y < self.robot.y and self.robot.y < 200: #TODO retrieve the actual max Y for the pitch here
                command =  self.go_to(self.robot.x, self.robot.y + 150)
            elif not self.robot.y < 20 and not self.robot.y > 200: # If robot was isn't too near the edge
                command = self.go_to(self.robot.x, self.robot.y  -150)
            else:
                command = self.go_to(self.robot.x, 100) # If can't get round opponent on the wings, move towards the centre
            if command:
                return command
            else:
                command = self.go_to(self.robot.x, 200 - self.robot.y) # If that doesn't work, better to do something than nothing.
            if command:
                return command
            else:
                pdb.set_trace()
                return CommandDict.stop()



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
