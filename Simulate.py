from planning.Planner import Planner
import warnings
import time
from Control.dict_control import Controller
import traceback
import sys
from Simulator.Simulator import Simulator
from Simulator.Visualise import Visualise
import time
import pygame
warnings.filterwarnings("ignore", category=DeprecationWarning)

FPS = 40

class Main:

    def __init__(self):
        # Initialise world
        left_def = {'x' : 20, 'y' : 160, 'angle':1.1, 'velocity': 0}
        left_atk = {'x' : 300, 'y' : 100, 'angle':.04, 'velocity': 50}
        right_def = {'x' : 450, 'y' : 110, 'angle':4, 'velocity': 0}
        right_atk = {'x' : 180, 'y' : 85, 'angle':3.14, 'velocity': 0}
        ball = {'x' : 330, 'y' : 150, 'angle':1.5, 'velocity': 4}
        initial_state = {'our_defender':left_def, 'our_attacker':left_atk, 'their_attacker':right_atk, 'their_defender':right_def, 'ball':ball}

        # Set up planner(s)
        left_def_planner = Planner_new('left', 2, attacker=False)
        left_atk_planner = Planner_new('left', 2, attacker=True)
        right_def_planner = Planner_new('right', 2, attacker=False)
        right_atk_planner =Planner_new('right', 2, attacker=True)

        # Create simulator
        self.sim = Simulator(left_def=left_def_planner,left_atk=left_atk_planner, right_def=right_def_planner,
                             right_atk=right_atk_planner, world=initial_state, fps=FPS)

        # Create visualisor
        self.disp = Visualise()
        self.disp.set_world(self.sim.get_world_new())
        self.disp.show()

        self.control_loop()

    def control_loop(self):
        """
        The main loop for the control system. Runs until ESC is pressed.

        Takes a frame from the camera; processes it, gets the world state;
        gets the actions for the robots to perform;  passes it to the robot
        controllers before finally updating the GUI.
        """
        clock = pygame.time.Clock()
        counter = 0
        sim = self.sim
        while True:
            if counter % 4  == 0: # Not allowed to read a command every frame
                self.sim.read_commands()
            sim.step()
            self.disp.set_world(sim.get_world_new())
            if counter % 4 == 0:
                self.disp.read_messages()
            self.disp.show()
            counter = counter + 1
            clock.tick(FPS)



if __name__ == '__main__':
    Main()
