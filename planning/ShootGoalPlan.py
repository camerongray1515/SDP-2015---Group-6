from Plan import Plan

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
        # Center of the robot's zone
        (x,y) = self.world.pitch.zones[self.robot._zone].center()
  
        # Center of the goal
        #TODO test if this works
        (gx,gy) = (self.world.their_goal.get_polygon()[0][0], self.world.pitch._height / 2)

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
   


