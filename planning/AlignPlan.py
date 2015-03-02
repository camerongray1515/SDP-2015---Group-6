from Plan import Plan
from Utility.CommandDict import CommandDict
import math

ERROR = math.pi/15

class AlignPlan(Plan):
    """Plan for aligning the robot sideways on the pitch to allow for easier interception"""

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        super(AlignPlan, self).__init__(world, robot)

    def isValid(self):
        """
        Current constraints are:
            - Ball not be within the robot's zone
            - Robot must not be already aligned
        """

        if self.world.ball is not None:
            return not self.world.pitch.is_within_bounds(self.robot, self.world.ball.x, self.world.ball.y) and (not self.isAligned(self.robot))
        return False

    def nextCommand(self):
        current_angle = self.robot.angle
        # Turn either left or right, depending on which requires the least turning
        if current_angle < math.pi:
            if current_angle < math.pi/2:
                return CommandDict(57, "Left", "None")
            else:
                return CommandDict(57, "Right", "None")
        else: 
            if current_angle < 3 * math.pi /2:
                return CommandDict(57, "Left", "None")
            else: 
                return CommandDict(57, "Right", "None")

    def isAligned(self, robot):
        return math.fabs(robot.angle - math.pi/2) < ERROR or math.fabs(robot.angle - 3 * math.pi/2) < ERROR



    def __str__(self):
        return "align plan"