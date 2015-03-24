from worldstate.World import World
from IdlePlan import IdlePlan
from GrabBallPlan import GrabBallPlan
from NewShootGoalPlan import NewShootGoalPlan
from Utility.CommandDict import CommandDict
from MatchY import MatchY
from PassPlan import PassPlan
from TakeShot import TakeShot
from ReturnToCentrePlan import ReturnToCentrePlan
import consol

class Planner(object):
    """Finite State Machine-Based planner. Generates commands for the robot based on plan classes derived from Plan"""

    def __init__(self, side, pitch, attacker=True):
        """
        Constructor.
        :param side: "left" or "right"; The side of the pitch we are on
        :param pitch: 0 or 1; The main pitch (0) or the side pitch (1)
        :param attacker: True (or not given) if we are the attacker robot, otherwise False if we are the defender
        """
        self.world = World(side, pitch)
        #TODO catcher_areas need tweaking for our robot, they are currently set to team 7's
        self.world.our_defender.catcher_area = {'width' : 30, 'height' : 30, 'front_offset' : 12}
        self.world.our_attacker.catcher_area = {'width' : 30, 'height' : 30, 'front_offset' : 14}
        self.robot = self.world.our_attacker 

        # List of available plans. These should be instantiated in -descending- order of desirability. All plans -must- inherit from Plan!
        p = (lambda plan: plan(self.world, self.robot))
        
        self.plans = [p(TakeShot), p(GrabBallPlan), p(MatchY), p(IdlePlan)]

        self.current_plan = self.plans[0]

    def update(self, model_positions):
        """
        Main planner update function. Should be called once per frame.
        :param model_positions: A dictionary containing the positions of the objects on the pitch. (See VisionWrapper.model_positions)
        :return: The next command to issue to the robot.
        """
        # Update the world state with the given positions
        self.world.update_positions(model_positions)

        if self.world.ball != None:
            consol.log("Catcher",self.robot.catcher,"Robot")
            if(self.current_plan.isValid() and not self.current_plan.isFinished()):
                return self.current_plan.nextCommand()
            else:
            # If self.current_plan is invalid, then choose a new plan and return a command from it
                for plan in self.plans:
                    if(plan.isValid()):
                        self.current_plan = plan
                        #self.current_plan.reset()
                        return self.current_plan.nextCommand()
        else:
            return CommandDict.stop()



