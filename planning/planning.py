from World import World
from math import pi
from Utility.CommandDict import CommandDict

ROTATION_ERROR = pi/17
DISTANCE_ERROR = 5*pi

class Planning():


    def __init__(self, side,pitch,attacker=True):
        self.world = World(side, pitch)
        self.robot = self.world.our_attacker if attacker else self.world.our_defender



    def update(self, model_positions):
        self._world.update_positions(model_positions)
        self.go_to(self.world.ball.x,self.world.ball.y)

    def go_to(self,x,y):
        distance = self.robot.get_euclidean_distance_to_point(x,y)
        if not self.world.pitch.is_within_bounds(self.robot,x,y):
            return False

        angle = self.robot.get_rotation_to_point(x,y)
        # If we are done rotating go forward
        command = self.rotate_to(angle)
        if command:
            return command
        else:
            return self.go_forward()
        return CommandDict.stop()




    def rotate_to(self,angle):
        """
        :param angle: Radians to turn
        :return: False if angle within rotation error otherwise returns a command dictionary
        """
        if abs(angle) < ROTATION_ERROR:
            return False
        speed = 100
        direction = "Right" if angle > 0 else "Left"
        kick = False
        return CommandDict(speed,direction,kick)


    def go_forward(self, distance):
        """
        :param distance: unit??? distance to target position
        :return: False if within distance error otherwise a CommandDict
        """
        if distance < DISTANCE_ERROR:
            return False
        else:
            speed = 100
            direction = "Forward"
            kick = False
            return CommandDict(speed,direction,kick)