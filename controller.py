from Control.robot_api import  RobotAPI

class Robot_Controller(object):
    """
    Robot_Controller superclass for robot control.
    """

    def __init__(self):
        """
        Connect to Brick and setup Motors/Sensors.
        """
        self.api = RobotAPI()
        self.current_speed = 0

    def shutdown(self, comm):
        # TO DO
            pass


class Defender_Controller(Robot_Controller):
    """
    Defender implementation.
    """

    def __init__(self):
        """
        Do the same setup as the Robot class, as well as anything specific to the Defender.
        """
        super(Defender_Controller, self).__init__()

    def execute(self, action):
        """
        Execute robot action.
        Actions come in form {}
        """
        print "Actions = ", action


    def shutdown(self):
        print "shutdown"


class Attacker_Controller(Robot_Controller):
    """
    Attacker implementation.
    """

    def __init__(self):
        """
        Do the same setup as the Robot class, as well as anything specific to the Attacker.
        """
        super(Attacker_Controller, self).__init__()

    def execute(self, action):
        """
        Execute robot action.
        """
        print "Actions = ", action

        #if 'turn_90' in action:


    def shutdown(self,):
        print "shutdown"