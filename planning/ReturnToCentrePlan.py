from Plan import Plan
from Utility.CommandDict import CommandDict
import math

return_threshold = 45

class ReturnToCentrePlan(Plan):
    """Plan for aligning the robot sideways on the pitch to allow for easier interception"""

    def __init__(self, world, robot):
        """
        Constructor. Calls superclass constructor.
        """
        super(ReturnToCentrePlan, self).__init__(world, robot)
        zone = self.world.pitch.zones[self.robot.zone][0] 
        self.min_x = 10000
        self.max_x = 0
        for point in zone:
            x_coord = point[0]
            if self.min_x > x_coord:
                self.min_x = x_coord
            if self.max_x < x_coord:
                self.max_x = x_coord

    def isValid(self):
        """
        Current constraints are:
            - Ball not be within the robot's zone
            - Robot must be within 'return_threshold' of the edge of the zone'
        """

        if self.world.ball is not None:
            return math.fabs(self.robot.x - self.max_x) < return_threshold or math.fabs(self.robot.x - self.min_x) < return_threshold
        return False

    def nextCommand(self):
        
        current_angle = self.robot.angle
        current_x = self.robot.x
        
        mid_x = (self.min_x + self.max_x) / 2

        return self.go_to_asym(mid_x,self.robot.y)

        # If the robot is pointing left
        if current_angle > math.pi / 2 and current_angle < 3*math.pi / 2:
            # If the robot is on the right side of the zone
            if math.fabs(self.robot.x - self.max_x) < return_threshold:
                return self.go_forward(50)
            # If the robot is on the left side of the zone
            elif math.fabs(self.robot.x - self.min_x) < return_threshold:
                return self.go_backward(50)
        # If the robot is pointing right
        elif (current_angle > 0 and current_angle < math.pi / 2) or current_angle > 3*math.pi / 2:
            # If the robot is on the right side of the zone
            if math.fabs(self.robot.x - self.max_x) < return_threshold:
                return self.go_backward(50)
            # If the robot is on the left side of the zone
            elif math.fabs(self.robot.x - self.min_x) < return_threshold:
                return self.go_forward(50)
        else:
            print "Massive fucking error!"
            return CommandDict.stop()

        command = self.go_to(mid_x, self.robot.y, speed=75)
        if command:
            return command
        return CommandDict.stop()

    def __str__(self):
        return "Return to centre"
