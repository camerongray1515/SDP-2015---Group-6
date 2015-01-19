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
        robot.led_on()
    elif method == 'stop':
        robot.led_off()

    return ''

if __name__ == '__main__':
    app.run()