from serial import Serial, SerialException
from threading import Timer
import time

speed = 19.5 # speed in cm/s, this is a constant we should calibrate when we get the motors working

class RobotAPI():
    def __init__(self, device_path=None, baud_rate=None):
        #check if there are valid parameters
        if (device_path is not None and baud_rate is not None):
            try:
                self.serial = Serial(device_path, baud_rate)
            except SerialException:
                print "Error in initalizing serial connection. Is the path correct?"
                #alias the _write_serial function so we don't throw errors
                self._write_serial = self._write_serial_debug
    
    #debug/error function if we're not using serial
    def _write_serial_debug(self, data):
        print data

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
        self._write_serial("forward {0}".format(speed))

    def go_backward(self, speed=100):
        self._write_serial("reverse {0}".format(speed))

    def turn_left(self, speed=100):
        self._write_serial("turn_left {0}".format(speed))

    def turn_right(self, speed=100):
        self._write_serial("turn_right {0}".format(speed))

    def kick(self, speed=100):
        self._write_serial("kicker_kick {0}".format(speed))
        time.sleep(1)
        self._write_serial("kicker_stop")

    def prepare_catch(self):  # This may be needed if we remove side bars from the robot
                            # It closes grabber just a bit so we can collect the ball without kicker in the way
        self._write_serial("kicker_catch 50")
        time.sleep(0.2)
        self._write_serial("kicker_stop")

    def catch(self, speed=100):
        self._write_serial("kicker_catch {0}".format(speed))
        time.sleep(1)
        self._write_serial("kicker_stop")

    def stop(self):
        self._write_serial("stop")

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
