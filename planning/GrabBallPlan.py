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
            - NOT IMPLEMENTED : Robot must be within its zone - though this -should- be handled by the go_to function. This may be useful for some kind of state-reset if we get out of the zone somehow
        """
        return self.world.pitch.is_within_bounds(self.robot,self.world.ball.x,self.world.ball.y)

    def nextCommand(self):
        command = self.go_to(self.world.ball.x,self.world.ball.y)
        # If we need to move to the ball, then get the command and return it
        if not command == False:
            # Merge this command with the prepare kicker command
            return CommandDict.mergeCommands(command, CommandDict.prepare())

        # Otherwise we are finished with this plan
        else:
            self.finished = True
            return CommandDict.catch()