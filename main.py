from multiprocessing import Process, Queue
from msvcrt import getch

from robot_api import RobotAPI

def getInput(q):
     while True:
        q.put(ord(getch()))

if __name__ == "__main__":
    robot = RobotAPI()
    queue = Queue()
    process = Process(target = getInput, args = (queue,))
    process.start()

    #main loop
    while True:
        if not queue.empty():
            input = queue.get()
            #print input #uncomment this to print keycodes for debugging
            
            if(input == 97):
                robot.turn_left()
            if(input == 115):
                robot.go_backward()
            if(input == 100):
                robot.turn_right()
            if(input == 119):
                robot.go_forward()
            if(input == 32):
                robot.kick()
            if(input == 27):
                robot.stop()

    process.join()



        


