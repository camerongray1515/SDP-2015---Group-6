from planning.Planner import Planner
import vision.tools as tools
from cv2 import waitKey
import warnings
import time
from gui import GUI
from visionwrapper import VisionWrapper
from Control.dict_control import Controller
from Utility.CommandDict import CommandDict
import traceback
import sys

warnings.filterwarnings("ignore", category=DeprecationWarning)

class Main:


    """
    Primary source of robot control. Ties vision and planning together.
    """
    def __init__(self, pitch, color, our_side, video_port=0, comm_port='/dev/ttyACM0', quick=False, is_attacker=False):
        """
        Entry point for the SDP system.

        Params:
            [int] video_port                port number for the camera
            [string] comm_port              port number for the arduino
            [int] pitch                     0 - main pitch, 1 - secondary pitch
            [string] our_side               the side we're on - 'left' or 'right'
        # """
        self.controller = Controller(comm_port)
        if not quick:
            print("Waiting 10 seconds for serial to initialise")
            time.sleep(10)

        # Kick once to ensure we are in the correct position
        self.controller.update(CommandDict.kick())
        self.pitch = pitch

        # Set up the vision system
        self.vision = VisionWrapper(pitch, color, our_side, video_port)

        # Set up the planner
        self.planner = Planner(our_side, pitch, attacker=is_attacker)

        # Set up GUI
        self.GUI = GUI(calibration=self.vision.calibration, pitch=pitch, launch=self)

        self.color = color
        self.side = our_side

        self.control_loop()

     
    def control_loop(self):
        #TODO change this description ESC doesn't work
        """
        The main loop for the control system. Runs until ESC is pressed.

        Takes a frame from the camera; processes it, gets the world state;
        gets the actions for the robots to perform;  passes it to the robot
        controllers before finally updating the GUI.
        """
        counter = 1L
        timer = time.clock()
        try:
            key = 255
            while key != 27:  # the ESC key
            
                # update the vision system with the next frame
                self.vision.update()
                pre_options = self.vision.preprocessing.options

                # Find appropriate action
                command = self.planner.update(self.vision.model_positions)
                self.controller.update(command)

                # Information about states
                regular_positions = self.vision.regular_positions
                model_positions = self.vision.model_positions

                defenderState = (str(self.planner.current_plan), "0")

                # Use 'y', 'b', 'r' to change color.
                key = waitKey(delay=2) & 0xFF  # Returns 255 if no keypress detected
                gui_actions = []
                fps = float(counter) / (time.clock() - timer)

                # Draw vision content and actions
                self.GUI.draw(
                    self.vision.frame, model_positions, gui_actions, regular_positions, fps, None,
                    defenderState, None, None, False,
                    our_color=self.color, our_side=self.side, key=key, preprocess=pre_options)
                counter += 1

        except Exception as e:
            print(e.message)
            traceback.print_exc(file=sys.stdout)
        finally:
            tools.save_colors(self.pitch, self.vision.calibration)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Main pitch, [1] Secondary pitch")
    parser.add_argument("side", help="The side of our defender ['left', 'right'] allowed.")
    parser.add_argument("color", help="The color of our team - ['yellow', 'blue'] allowed.")
    parser.add_argument("comms", help="""The serial port that the RF stick
                        is using (Usually /dev/ttyACMx)""")
    parser.add_argument("role", help="Role of robot - 'attack' or 'defend'")
    parser.add_argument("-q", "--quick", help="Quick mode - skips wait for serial",
                        action="store_true")
    args = parser.parse_args()
    if args.role == "attack" or args.role == "attacker":
        is_attacker = True
    elif args.role == "defend" or args.role == "defender":
        is_attacker = False
    else:
        print "Role must be 'attack' or 'defend'"
        sys.exit()
    c = Main(pitch=int(args.pitch), color=args.color, our_side=args.side, comm_port=args.comms,
             quick=args.quick, is_attacker=is_attacker)
