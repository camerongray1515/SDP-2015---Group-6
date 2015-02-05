from robot_api import RobotAPI

class Controller():
    def __init__(self, port="/dev/ttyACM0"):
        self.robot_api = RobotAPI(port,115200)

    def update(self,command):
        speed = command["speed"]
        direction=command["direction"]
        kick=command["kick"]

        if (direction == "Forward"):
            self.robot_api.go_forward(speed)
        elif (direction == "Backward"):
            self.robot_api.go_backward(speed)
        elif (direction == "Right"):
            self.robot_api.turn_right(speed)
        elif (direction == "Left"):
            self.robot_api.turn_left(speed)
        elif (direction == "None"):
            self.robot_api.stop()