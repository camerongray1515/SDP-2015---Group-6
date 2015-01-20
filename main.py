#from multiprocessing import Process, Queue
#from msvcrt import getch

from Control.robot_api import RobotAPI
from Utility.Getch import _Getch

def getInput(q):
     while True:
        q.put(ord(getch()))




getch = _Getch()

if __name__ == "__main__":
    robot = RobotAPI()
    #queue = Queue()
    #process = Process(target = getInput, args = (queue,))
    #process.start()

    #main loop
    run = True
    while run:
        input = ord(getch())
        print input #uncomment this to print keycodes for debugging
            
        if(input == 97): # A
            robot.turn_left()
        elif(input == 115): # S
            robot.go_backward()
        elif(input == 100): # D
            robot.turn_right()
        elif(input == 119): # W
            robot.go_forward()
        elif(input == 32): # Spacebar
            robot.kick()
        elif(input == 27): # Esc
            robot.stop()
        elif(input == 113): # Q
            run = False



        


