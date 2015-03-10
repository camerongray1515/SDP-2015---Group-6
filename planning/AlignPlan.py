from Plan import Plan
from Utility.CommandDict import CommandDict
import math
import pdb

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
            return not self.world.pitch.is_within_bounds(self.robot, self.world.ball.x, self.world.ball.y) and \
                   (not self.isAligned(self.robot))
        return False

    def nextCommand(self):
        return_threshold = 40 # return to centre if this close to edge
        current_angle = self.robot.angle
        current_x = self.robot.x
        # If close to the edge of zone, return to the centre
        zone = self.world.pitch.zones[self.robot.zone][0] 
        #zone is of form [(115.0, 290.0), (255.0, 290.0), (255.0, 0.0), (115.0, 0.0)]
        min_x = 10000
        max_x = 0
        for point in zone:
            x_coord = point[0]
            if min_x > x_coord:
                min_x = x_coord
            if max_x < x_coord:
                max_x = x_coord
        if math.fabs(current_x - max_x) < return_threshold or math.fabs(current_x - min_x) < return_threshold:
            print "ALIGN - Return to centre"
            mid_x = (min_x + max_x)/2
            command = self.go_to(mid_x, self.robot.y, speed=75)
            if command:
                return command


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

    def __str__(self):
        return "align plan"