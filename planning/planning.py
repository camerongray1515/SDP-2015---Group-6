from World import World
from math import pi
from Utility.CommandDict import CommandDict

ROTATION_ERROR = pi/17
DISTANCE_ERROR = 8*pi

class Planning():

    def __init__(self, side,pitch,attacker=True):
        self.world = World(side, pitch)
        self.world.our_defender.catcher_area = {'width' : 30, 'height' : 30, 'front_offset' : 12}
        self.world.our_attacker.catcher_area = {'width' : 30, 'height' : 30, 'front_offset' : 14}
        self.robot = self.world.our_attacker if attacker else self.world.our_defender
        self.catched = False

    def update(self, model_positions):
        self.world.update_positions(model_positions)
        command = self.go_to(self.world.ball.x,self.world.ball.y)
        if command:
            return command
        else:
            if not self.catched:
                self.catched = True
                return self.catch()

            else:
                return self.shoot_at_goal()
            return CommandDict.stop()

    def go_to(self,x,y):
        distance = self.robot.get_euclidean_distance_to_point(x,y)
        if not self.world.pitch.is_within_bounds(self.robot,x,y): #if the point is outside of the current zone dont do the thing
            return False

        angle = self.robot.get_rotation_to_point(x,y)
        print(angle)
        # If we are done rotating go forward
        command = self.rotate_to(angle)
        if command:
            return command
        else:
            return self.go_forward(distance)

        return CommandDict.stop()

    def rotate_to(self,angle):
        """
        :param angle: Radians to turn
        :return: False if angle within rotation error otherwise returns a command dictionary
        """
        if abs(angle) < ROTATION_ERROR:
            return False
        speed = 80
        direction = "Right" if angle < 0 else "Left"
        kick = "None"
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
            kick = "None"
            return CommandDict(speed,direction,kick)


    def prepare_kicker(self):
        return CommandDict.prepare()

    def catch(self):
        return CommandDict.catch()

    def kick(self,speed=100):
        return CommandDict(speed, "None","Kick")


    def shoot_at_goal(self):
        (x,y) = self.world.pitch.zones[self.robot._zone].center()
        (gx,gy) = (500,self.world.pitch._height/2) # centre point of goal

        command = self.go_to(x,y)
        if command:
            return command
        else:
            angle = self.robot.get_rotation_to_point(gx,gy)
            command = self.rotate_to(angle)
            if command:
                return command
            else: # if its gone as far as it should
                return self.kick()



