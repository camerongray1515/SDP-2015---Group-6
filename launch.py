from vision.vision import Vision, Camera
from planning.Planner_new import Planner_new
from postprocessing.postprocessing import Postprocessing
from preprocessing.preprocessing import Preprocessing
import vision.tools as tools
from cv2 import waitKey
import cv2
import serial
import warnings
import time
from controller import Robot_Controller, Attacker_Controller, Defender_Controller
from gui import GUI
import pdb
from visionwrapper import VisionWrapper
from Control.dict_control import Controller
warnings.filterwarnings("ignore", category=DeprecationWarning)


class Main:
    """
    Primary source of robot control. Ties vision and planning together.
    """

    def __init__(self, pitch, color, our_side, video_port=0, comm_port='/dev/ttyACM0', comms=1, test_mode=False):
        """
        Entry point for the SDP system.

        Params:
            [int] video_port                port number for the camera
            [string] comm_port              port number for the arduino
            [int] pitch                     0 - main pitch, 1 - secondary pitch
            [string] our_side               the side we're on - 'left' or 'right'
            *[int] port                     The camera port to take the feed from
            *[Robot_Controller] attacker    Robot controller object - Attacker Robot has a RED
                                            power wire
            *[Robot_Controller] defender    Robot controller object - Defender Robot has a YELLOW
                                            power wire
        """

        self.vision = VisionWrapper(pitch, color, our_side, video_port)
        # Set up main planner
        self.planner = Planner_new(our_side, pitch)

        # Set up GUI
        self.GUI = GUI(calibration=self.vision.calibration, pitch=pitch)

        self.controller = Controller(comm_port)
        print("Waiting 10 seconds for serial to initialise")
        time.sleep(10)

        self.control_loop()


    def control_loop(self, verbose=False):
        """
        The main loop for the control system. Runs until ESC is pressed.

        Takes a frame from the camera; processes it, gets the world state;
        gets the actions for the robots to perform;  passes it to the robot
        controllers before finally updating the GUI.
        """
        counter = 1L
        timer = time.clock()
        try:

            key = -1
            while key != 27:  # the ESC key

                #update the vision system with the next frame
                self.vision.update()

                # Find appropriate action
                command = self.planner.update(self.vision.model_positions)
                self.controller.update(command)

                # Information about the grabbers from the world
                grabbers = {
                    'our_defender': self.planner.world.our_defender.catcher_area,
                    'our_attacker': self.planner.world.our_attacker.catcher_area
                }
                # Information about states
                attackerState = ""
                defenderState = ""

                # Use 'y', 'b', 'r' to change color.
                key = waitKey(delay=2)  # Returns -1 if no keypress detected
                gui_actions = []
                fps = float(counter) / (time.clock() - timer)

                # Draw vision content and actions
                self.GUI.draw(self.vision,
                     gui_actions, fps, attackerState,
                    defenderState, "", "", grabbers, key=key)
                counter += 1

        except Exception as e:
            print(e.message)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Main pitch, [1] Secondary pitch")
    parser.add_argument("side", help="The side of our defender ['left', 'right'] allowed.")
    parser.add_argument("color", help="The color of our team - ['yellow', 'blue'] allowed.")
    parser.add_argument("comms", help="The serial port that the RF stick is using (Usually /dev/ttyACMx)")
    parser.add_argument(
        "-n", "--test", help="Disables sending commands to the robot.", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose mode - print more stuff", action="store_true")
    args = parser.parse_args()
    c = Main(pitch=int(args.pitch), color=args.color, our_side=args.side, comm_port=args.comms, test_mode=args.test).control_loop(verbose=args.verbose)
