from Plan import Plan
from Utility.CommandDict import CommandDict

class IdlePlan(Plan):
    """Defines the idle plan. This is the fallback plan the robot will end up in if the planner cannot find a suitable plan."""

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        super(IdlePlan, self).__init__(world, robot)

    def isValid(self):
        """
        Returns true because we can always execute the Idle plan regardless of world state.
        """
        return True

    def isFinished(self):
        """
        This method is overridden here because we always want to transition out of the Idle plan if we can.
        """
        return True

    def nextCommand(self):
        return CommandDict.stop()

    def __str__(self):
        return "idle plan"


