from launch import  Main
import cProfile
import re
import pstats


#To profile, run "python profiler.py". Once the program terminates (press esc), the results will print to terminal.

cProfile.run("c = Main(pitch=1, color='yellow', our_side='left', comm_port='/dev/ttyS0').control_loop()", 'restats')

p = pstats.Stats('restats')
p.strip_dirs().sort_stats('time').print_stats() # Also of interest - "cumulative" which includes time in sub calls.