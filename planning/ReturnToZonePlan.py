from Plan import Plan
from Utility.CommandDict import CommandDict

class ReturnToZonePlan(Plan):
    """Plan for the robot shooting the ball."""

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        return super(ReturnToZonePlan, self).__init__(world, robot)


    def isValid(self):
        """
        Current constraints are:
            - Robot must be outside the zone
        """
        return not self.world.pitch.is_within_bounds(self.robot, self.robot.x, self.robot.y)

    def nextCommand(self):
        # Center of the robot's zone
        (x, y) = self.world.pitch.zones[self.robot.zone].center()

        command = self.go_to(x, y)
        if command is not False:
            return command
        else:
            self.finished = True
            return CommandDict.stop()





