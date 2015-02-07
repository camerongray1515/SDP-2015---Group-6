from serial import Serial
from threading import Timer
import time

speed = 18.0 # speed in cm/s, this is a constant we should calibrate when we get the motors working

class RobotAPI():
    motorPins = {
        "left": 0,
        "right": 1,
        "kicker": 2
    }

    def __init__(self, device_path=None, baud_rate=None):
        #check if there are valid parameters
        if (device_path is not None and baud_rate is not None):
            self.serial = Serial(device_path, baud_rate)

    def _write_serial(self, data):
        data_bytes = str.encode(data)
        data_bytes += '\r'
        self.serial.write(data_bytes)

    def blink_led(self, delay=500):
        command = "blink {0}".format(delay)
        self._write_serial(command)

    def stop_blinking(self):
        self._write_serial("stop_blinking")

    def led_on(self):
        self._write_serial("led_on")

    def led_off(self):
        self._write_serial("led_off")

    def on_for_n_seconds(self, on_time):
        self.led_on()
        timer = Timer(on_time, self.led_off)
        timer.start()

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
        self.set_motor("kicker", speed)
        time.sleep(1)
        self.set_motor("kicker", 0)

    def prepare_catch(self):  # This may be needed if we remove side bars from the robot
                            # It closes grabber just a bit so we can collect the ball without kicker in the way
        self.set_motor("kicker", -1 * 50)
        time.sleep(0.2)
        self.set_motor("kicker", 0)

    def catch(self, speed=100):
        self.set_motor("kicker", -1 * speed)
        time.sleep(1)
        self.set_motor("kicker", 0)

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
        self.set_motor(self, "left", left)
        self.set_motor(self, "right", right)

    def set_motor(self, motor, speed):
        self._write_serial("set_motor {0} {1}".format(self.motorPins[motor], speed))
