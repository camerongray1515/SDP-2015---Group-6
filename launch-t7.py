from vision.vision import Vision, Camera
from planning.planner import Planner
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


warnings.filterwarnings("ignore", category=DeprecationWarning)


class Main:
    """
    Primary source of robot control. Ties vision and planning together.
    """

    def __init__(self, pitch, color, our_side, video_port=0, comm_port='/dev/ttyUSB0', comms=1, test_mode=False):
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
        assert pitch in [0, 1]
        assert color in ['yellow', 'blue']
        assert our_side in ['left', 'right']

        self.pitch = pitch

        # Set up camera for frames
        self.camera = Camera(port=video_port, pitch=self.pitch)
        frame = self.camera.get_frame()
        center_point = self.camera.get_adjusted_center(frame)

        # Set up vision
        self.calibration = tools.get_colors(pitch)
        self.vision = Vision(
            pitch=pitch, color=color, our_side=our_side,
            frame_shape=frame.shape, frame_center=center_point,
            calibration=self.calibration)

        # Set up postprocessing for vision
        self.postprocessing = Postprocessing()

        # Set up main planner
        self.planner = Planner(our_side=our_side, pitch_num=self.pitch)

        # Set up GUI
        self.GUI = GUI(calibration=self.calibration, arduino=None, pitch=self.pitch)

        self.color = color
        self.side = our_side

        self.preprocessing = Preprocessing()

        self.attacker = Attacker_Controller(test_mode=test_mode)
        self.defender = Defender_Controller(test_mode=test_mode)

    def control_loop(self, verbose=False):
        """
        The main loop for the control system. Runs until ESC is pressed.

        Takes a frame from the camera; processes it, gets the world state;
        gets the actions for the robots to perform;  passes it to the robot
        controlers before finally updating the GUI.
        """
        counter = 1L
        timer = time.clock()
        try:
            key = -1
            while key != 27:  # the ESC key

                frame = self.camera.get_frame()
                pre_options = self.preprocessing.options
                # Apply preprocessing methods toggled in the UI
                preprocessed = self.preprocessing.run(frame, pre_options)
                frame = preprocessed['frame']
                if 'background_sub' in preprocessed:
                    cv2.imshow('bg sub', preprocessed['background_sub'])
                # Find object positions
                # model_positions have their y coordinate inverted

                model_positions, regular_positions = self.vision.locate(frame)
                model_positions = self.postprocessing.analyze(model_positions)
                if verbose:
                	print model_positions

                # Find appropriate action
                self.planner.update_world(model_positions)
                attacker_actions = self.planner.plan('attacker')
                defender_actions = self.planner.plan('defender')
                print(attacker_actions)
                print(defender_actions)
                if self.attacker is not None:
                    print("hello")
                    self.attacker.execute(attacker_actions)
                if self.defender is not None:
                    self.defender.execute(defender_actions)

                # Information about the grabbers from the world
                grabbers = {
                    'our_defender': self.planner._world.our_defender.catcher_area,
                    'our_attacker': self.planner._world.our_attacker.catcher_area
                }

                # Information about states
                attackerState = (self.planner.attacker_state, self.planner.attacker_strat_state)
                defenderState = (self.planner.defender_state, self.planner.defender_strat_state)

                # Use 'y', 'b', 'r' to change color.
                key = waitKey(delay=2)  # Returns -1 if no keypress detected
                gui_actions = []
                fps = float(counter) / (time.clock() - timer)

                # Draw vision content and actions
                self.GUI.draw(
                    frame, model_positions, gui_actions, regular_positions, fps, attackerState,
                    defenderState, attacker_actions, defender_actions, grabbers,
                    our_color=self.color, our_side=self.side, key=key, preprocess=pre_options)
                counter += 1

        except:
            if self.defender is not None:
                self.defender.shutdown()
            if self.attacker is not None:
                self.attacker.shutdown()
            raise

        finally:
            # Write the new calibrations to a file.
            tools.save_colors(self.pitch, self.calibration)
            if self.attacker is not None:
                self.attacker.shutdown()
            if self.defender is not None:
                self.defender.shutdown()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Main pitch, [1] Secondary pitch")
    parser.add_argument("side", help="The side of our defender ['left', 'right'] allowed.")
    parser.add_argument("color", help="The color of our team - ['yellow', 'blue'] allowed.")
    parser.add_argument(
        "-n", "--test", help="Disables sending commands to the robot.", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose mode - print more stuff", action="store_true")
    args = parser.parse_args()
    c = Main(pitch=int(args.pitch), color=args.color, our_side=args.side, comms="/dev/ttyACM0", test_mode=args.test).control_loop(verbose=args.verbose)
