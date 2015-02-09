import time
from Control.robot_api import  RobotAPI

class Robot_Controller(object):
    """
    Robot_Controller superclass for robot control.
    """

    def __init__(self, test_mode=False):
        """
        Connect to Brick and setup Motors/Sensors.
        """
        
        self.api = RobotAPI("/dev/ttyACM0",115200)
        self.current_speed = 0

    def execute(self, action):
        """
        Execute robot action.
        """
        print "Attacker actions = ", action

        if action['left_motor'] < action['right_motor']:
            self.api.turn_left(100)
            print("left")
        elif action['right_motor'] < action['left_motor']:
            self.api.turn_right(100)
            print("right")
        elif action['left_motor'] == action['right_motor'] and action['left_motor'] > 0:
            self.api.go_forward()
            print("forward")
        elif action['left_motor'] == action['right_motor'] and action['left_motor'] < 0:
            self.api.go_backward()
            print("forward?")
        elif action['left_motor'] == action['right_motor'] and action['left_motor'] ==  0:
            self.api.stop()
            print("stop")

        if action['catcher'] > 0:
            self.api.catch()
        if action['kicker'] > 0:
            self.api.kick()
	
    def shutdown(self, comm):
        # TO DO
        pass


class Defender_Controller(Robot_Controller):
    """
    Defender implementation.
    """

    def __init__(self, test_mode=False):
        """
        Do the same setup as the Robot class, as well as anything specific to the Defender.
        """
        super(Defender_Controller, self).__init__(test_mode)

    def shutdown(self):
        print "shutdown"


class Attacker_Controller(Robot_Controller):
    """
    Attacker implementation.
    """

    def __init__(self, test_mode=False):
        """
        Do the same setup as the Robot class, as well as anything specific to the Attacker.
        """
        super(Attacker_Controller, self).__init__(test_mode)

    def shutdown(self,):
        print "shutdown"
