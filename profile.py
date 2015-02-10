from launch import  Main
import cProfile
import re

#To profile, run "python profiler.py". Once the program terminates (press esc), the results will print to terminal.

cProfile.run("c = Main(pitch=1, color='yellow', our_side='left', comm_port='/dev/ttyS0').control_loop()")