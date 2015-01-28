from os import system
from robot_api import RobotAPI
import curses

screen = curses.initscr()


def main():
     motor_speed = 100
     
     # Prompt for the path to the RF dongle
     serial_port = get_param("Enter path to serial port")

     robot = RobotAPI(serial_port, 115200)
     x = 0

     while x != ord('q'):
          screen.clear()
          screen.border(0)
          screen.addstr(1, 2, "SDP Group 6 - Robot Control System")
          screen.addstr(2, 2, "----------------------------------")
          screen.addstr(4, 4, "1 - Go Forward")
          screen.addstr(5, 4, "2 - Go Backward")
          screen.addstr(6, 4, "3 - Turn Right")
          screen.addstr(7, 4, "4 - Turn Left")
          screen.addstr(8, 4, "5 - Stop")
          screen.addstr(9, 4, "6 - Prepare for Catch")
          screen.addstr(10, 4, "7 - Catch")
          screen.addstr(11, 4, "8 - Kick")
          screen.addstr(12, 4, "9 - Go forward n centimeters")
          screen.addstr(13, 4, "0 - Go forward for n seconds")
          screen.addstr(14, 4, "a - Go backward n centimeters")

          screen.addstr(16, 4, "s - Set motor speed")
          screen.addstr(18, 4, "q - Quit")

          screen.addstr(20, 2, "Please pick an option...")
          screen.addstr(21, 2, "System Information")
          screen.addstr(22, 2, "------------------")
          screen.addstr(23, 2, "Serial Port: {0}".format(serial_port))
          screen.addstr(24, 2, "Motor Speed: {0}".format(motor_speed))
          screen.refresh()

          x = screen.getch()

          if x == ord('1'):
               robot.go_forward(speed=motor_speed)
          if x == ord('2'):
               robot.go_backward(speed=motor_speed)
          if x == ord('3'):
               robot.turn_right(speed=motor_speed)
          if x == ord('4'):
               robot.turn_left(speed=motor_speed)
          if x == ord('5'):
               robot.stop()
          if x == ord('6'):
               robot.prepare_catch()
          if x == ord('7'):
               robot.catch(speed=motor_speed)
          if x == ord('8'):
               robot.kick(speed=motor_speed)
          if x == ord('9'):
               num_cm = get_param("Enter distance in centimeters")
               robot.go_forward_for(int(num_cm))
          if x == ord('a'):
               num_cm = get_param("Enter distance in centimeters")
               robot.go_backward_for(int(num_cm))

          if x == ord('0'):
               num_seconds = get_param("Enter number of seconds to drive for")
               robot.forward_n_seconds(int(num_seconds))
          if x == ord('s'):
               motor_speed = int(get_param("Enter speed for motor from 1 to 100"))

     curses.endwin()

def get_param(prompt_string):
     screen.clear()
     screen.border(0)
     screen.addstr(2, 2, prompt_string)
     screen.addstr(3, 2, '>')
     screen.refresh()
     input = screen.getstr(3, 4, 60)
     return input

if __name__ == "__main__":
     main()
