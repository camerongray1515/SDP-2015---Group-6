from robot_api import RobotAPI
from flask import Flask, request

app = Flask(__name__)
app.debug = True

robot = RobotAPI('/dev/ttyACM0', 115200)

@app.route('/')
def yo_received():
    method = request.args.get('method')
    print("Yo received! Method: {0}".format(method))
    
    if method == 'forward':
        robot.go_forward()
    elif method == 'reverse':
        robot.go_backward()
    elif method == 'right':
        robot.turn_right()
    elif method == 'left':
        robot.turn_left()
    elif method == "kick":
        robot.kick()
    elif method == 'stop':
        robot.stop()

    return ''

if __name__ == '__main__':
    app.run()