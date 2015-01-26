from serial import Serial
from threading import Timer
import time

class RobotAPI():
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

    def go_forward(self):
        self._write_serial("forward")

    def go_backward(self):
        self._write_serial("reverse")

    def turn_left(self):
        self._write_serial("turn_left")

    def turn_right(self):
        self._write_serial("turn_right")

    def kick(self):
        print "Kicking"

    def stop(self):
        self._write_serial("stop")