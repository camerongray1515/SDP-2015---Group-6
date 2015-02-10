from robot_api import RobotAPI

class Controller():
    def __init__(self, port="/dev/ttyACM1"):
        self.kick_wait = 0
        self.prepare_wait = 0
        self.catch_wait = 0
        self.robot_api = RobotAPI(port,115200)

    def update(self, command):
        if self.kick_wait > 0:
            self.kick_wait -= 1
            return
        if self.prepare_wait > 0:
            self.prepare_wait -= 1
            return
        if self.catch_wait > 0:
            self.catch_wait -= 1
            return

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

        if (kick == "Kick"):
            self.kick_wait = 20
            self.robot_api.kick(speed)
        elif (kick == "Prepare"):
            self.prepare_wait = 5
            self.robot_api.prepare_catch()
        elif (kick == "Catch"):
            self.catch_wait = 5
            self.robot_api.catch(speed)
