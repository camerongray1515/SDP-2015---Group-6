from serial import Serial, SerialException
import time
import random

speed = 19.5 # speed in cm/s, this is a constant we should calibrate when we get the motors working

class RobotAPI():
    motorPins = {
        "left": 0,
        "right": 1,
        "kicker": 2
    }

    # The speed of each motor will be set to the specified speed multiplied by the *_scale speed in the
    # dictionary below.  If it falls between two of these points, the speed will be linearly interpolated
    scaling_data_points = {
        100: {
            "left_scale": 1,
            "right_scale": 0.85
        },
        90: {
            "left_scale": 1,
            "right_scale": 0.6667
        },
        80: {
            "left_scale": 1,
            "right_scale": 0.5875
        },
        70: {
            "left_scale": 1,
            "right_scale": 0.6
        },
        60: {
            "left_scale": 1,
            "right_scale": 0.63
        },
        50: {
            "left_scale": 1,
            "right_scale": 0.56
        },
        -100: {
            "left_scale": 1,
            "right_scale": 0.85
        },
        -90: {
            "left_scale": 1,
            "right_scale": 0.6667
        },
        -80: {
            "left_scale": 1,
            "right_scale": 0.5875
        },
        -70: {
            "left_scale": 1,
            "right_scale": 0.6
        },
        -60: {
            "left_scale": 1,
            "right_scale": 0.63
        },
        -50: {
            "left_scale": 1,
            "right_scale": 0.56
        }
    }

    current_motor_speeds = {
        "left": 0,
        "right": 0,
        "kicker": 0
    }

    def __init__(self, device_path=None, baud_rate=None):
        # check if there are valid parameters
        if (device_path is not None and baud_rate is not None):
            try:
                self.serial = Serial(device_path, baud_rate, timeout=0.1)
            except SerialException:
                print "Error in initalizing serial connection. Is the path correct?"
                #alias the _write_serial function so we don't throw errors
                self._write_serial = self._write_serial_debug

    #debug/error function if we're not using serial
    def _write_serial_debug(self, data):
        print data

    def _write_serial(self, data):
        ack = False

        # Test code that will drop the majority of commands to test fault tollerance
        while not ack:
            data_bytes = str.encode(data)
            data_bytes += '\r'
            self.serial.write(data_bytes)
            print("Sent command: {0}".format(data))

            try:
                ack = self.serial.read()
            except SerialException as ex:
                ack = False

    def blink_led(self, delay=500):
        command = "blink {0}".format(delay)
        self._write_serial(command)

    def stop_blinking(self):
        self._write_serial("stop_blinking")

    def led_on(self):
        self._write_serial("led_on")

    def led_off(self):
        self._write_serial("led_off")

    def go_forward(self, speed=100):
        self.set_motor("left", speed)
        self.set_motor("right", speed)

    def go_backward(self, speed=100):
        self.set_motor("left", -1 * speed)
        self.set_motor("right", -1 * speed)

    def turn_left(self, speed=100):
        self.set_motor("left", -1 * speed)
        self.set_motor("right", speed)

    def turn_right(self, speed=100):
        self.set_motor("right", -1 * speed)
        self.set_motor("left", speed)

    def kick(self, speed=100):
        self._write_serial("kick {0}".format(speed))


    def prepare_catch(self):  # This may be needed if we remove side bars from the robot
        # It closes grabber just a bit so we can collect the ball without kicker in the way
        self._write_serial("prepare_catch")

    def catch(self, speed=100):
        self._write_serial("catch {0}".format(speed))


    def stop(self):
        self.set_motor("left", 0)
        self.set_motor("right", 0)

    def go_forward_for(self, distance):  # distance is in centimeters
        move_time = distance / speed
        self.go_forward()
        time.sleep(move_time)
        self.stop()

    def go_backward_for(self, distance):  # distance is in centimeters
        move_time = distance / speed
        self.go_backward()
        time.sleep(move_time)
        self.stop()

    def forward_n_seconds(self, num_seconds):
        self.go_forward()
        time.sleep(num_seconds)
        self.stop()

    def set_both_wheels(self, left, right):
        self.set_motor("left", left, False)
        self.set_motor("right", right, False)

    def set_motor(self, motor, speed, scale=True, delay=0):
        # If the motor is already running at this speed, do not send the command
        if speed == self.current_motor_speeds[motor]:
            return
        
        if scale:
            scaled_speed = self.get_scaled_speed(motor, speed)
        else:
            scaled_speed = speed

        self._write_serial("set {0} {1} {2}".format(self.motorPins[motor], scaled_speed, delay))
        self.current_motor_speeds[motor] = speed

    def get_scaled_speed(self, motor, speed):
        return speed
        # Find the two speeds that the specified speed lies between, or if the speed has
        # an exact match in the data points, simply return that

        # We don't scale the kicker
        if motor == "kicker":
            return speed

        # We don't scale if the speed is 0 (stop)
        if speed == 0:
            return 0

        if speed in self.scaling_data_points:
            if motor == "left":
                return int(round(speed * self.scaling_data_points[speed]["left_scale"]))
            elif motor == "right":
                return int(round(speed * self.scaling_data_points[speed]["right_scale"]))
            else:
                raise Exception("Invalid motor {0}".format(motor))

        # Find the two data points that the given speed lies between
        data_points = sorted(self.scaling_data_points.keys())

        lower = -1
        upper = -1
        for point_speed in data_points:
            if point_speed < speed:
                lower = point_speed
            else:
                upper = point_speed
                break

        # The speed given is out of the range of the points that we have, therefore do not scale
        if lower == -1:
            return speed

        # Here we attempt to remember high school maths to work out the equation of the line between the
        # two scaling values at the lower and upper speeds
        m = (self.scaling_data_points[upper]["{0}_scale".format(motor)] - self.scaling_data_points[lower]["{0}_scale".format(motor)]) / (upper - lower)
        c = self.scaling_data_points[upper]["{0}_scale".format(motor)] - (m * upper)

        # We can now estimate the scaling value for the given speed
        scaling_value = m * speed + c

        return int(round(speed * scaling_value))
