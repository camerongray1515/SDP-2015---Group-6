from Control.robot_api import RobotAPI
from Utility.Getch import _Getch

getch = _Getch()

has_ball = False

if __name__ == "__main__":

    robot = RobotAPI('/dev/ttyACM0', 115200)
    robot.go_forward_for(5)

    #main loop
    while input != 27:
        input = ord(getch())
        #print input #uncomment this to print keycodes for debugging
            
        if(input == 97): # A
            robot.turn_left()
        elif(input == 115): # S
            robot.go_backward()
        elif(input == 100): # D
            robot.turn_right()
        elif(input == 119): # W
            robot.go_forward()
        elif(input == 32): # Spacebar
            if has_ball: 
                robot.kick()
                has_ball = False
            else:
                robot.catch()
                has_ball = True
        elif(input == 27): # Esc
            robot.stop()
        elif(input == 113): # Q
            run = False




        


