from Plan import Plan
from Utility.CommandDict import CommandDict

class GrabBallPlan(Plan):
    """Plan for the robot navigating to and grabbing the ball."""

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        super(GrabBallPlan, self).__init__(world, robot)

    def isValid(self):
        """
        Current constraints are:
            - Ball must be within the robot's zone
            - Robot must not have the ball
            - NOT IMPLEMENTED : Robot must be within its zone - though this -should- be handled by the go_to function. This may be useful for some kind of state-reset if we get out of the zone somehow
        """

        if self.world.ball is not None:
            return self.world.pitch.is_within_bounds(self.robot,self.world.ball.x,self.world.ball.y) and (not self.robot.has_ball())
        return False

    def nextCommand(self):
        if self.robot.catcher != "prepared":
            self.robot.catcher = "prepared"
            return CommandDict.prepare()

        command = self.go_to(self.world.ball.x,self.world.ball.y)
        # If we need to move to the ball, then get the command and return it
        if not command == False:
            return command

        # Otherwise we are finished with this plan
        else:
            self.finished = True
            self.robot.catcher = "closed"
            return CommandDict.catch()