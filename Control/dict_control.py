from robot_api import RobotAPI
from consol import log,log_time
import time

class Controller():
    def __init__(self, port="/dev/ttyACM1"):
        self.robot_api = RobotAPI(port, 115200)

    def update(self, command):
        speed = command["speed"]
        direction=command["direction"]
        kick=command["kick"]

        log_time('dict_control')
        log('speed', speed, 'dict_control')
        log('direction', direction, 'dict_control')
        log('kick', kick, 'dict_control')


        if (direction == "Forward"):
            log_time('dict_control', 'time go forward called')
            if 'speedr' in command:
                speed_right = command["speedr"]
                self.robot_api.go_forward_asym(speed, speed_right)
            else:
                self.robot_api.go_forward(speed)

        elif (direction == "Backward"):
            self.robot_api.go_backward(speed)
        elif (direction == "Right"):
            self.robot_api.turn_right(speed)
        elif (direction == "Left"):
            self.robot_api.turn_left(speed)
        elif (direction == "None"):
            self.robot_api.stop()

        if (kick == "Kick"):
            for i in range(0, 10):
                self.robot_api.kick(100)
                time.sleep(.001)
        elif (kick == "Prepare"):
            log_time("dict_control", "prepare")
            for i in range(0, 10):
                self.robot_api.prepare_catch()
                time.sleep(.001)
        elif (kick == "Catch"):
            for i in range (0, 10):
                self.robot_api.catch(100)
                time.sleep(.001)
