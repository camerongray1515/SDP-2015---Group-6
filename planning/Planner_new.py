
from World import  World
from IdlePlan import IdlePlan
from GrabBallPlan import GrabBallPlan
from ShootGoalPlan import ShootGoalPlan
from InterceptPlan import InterceptPlan
from Utility.CommandDict import CommandDict
from EasyInterceptPlan import EasyInterceptPlan

#TODO Rename!!!
class Planner_new(object):
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
        self.robot = self.world.our_attacker if attacker else self.world.our_defender

        # List of available plans. These should be instantiated in -descending- order of desirability. All plans -must- inherit from Plan!
        if (attacker):
            self.plans = [ShootGoalPlan(self.world, self.robot), GrabBallPlan(self.world, self.robot), IdlePlan(self.world, self.robot)]
        else:
            self.plans = [InterceptPlan(self.world, self.robot),GrabBallPlan(self.world, self.robot), IdlePlan(self.world,self.robot)]
        self.current_plan = self.plans[0]


    #TODO Currently each indivdual plan does not have any internal state governing transitions, we may need to modify the system to support this in future
    # Upshot-> Each plan can currently transition to any other plan, this may not be desirable
    def update(self, model_positions):
        """
        Main planner update function. Should be called once per frame.
        :param model_positions: A dictionary containing the positions of the objects on the pitch. (See VisionWrapper.model_positions)
        :return: The next command to issue to the robot.
        """
        # Update the world state with the given positions
        self.world.update_positions(model_positions)
        #print self.current_plan
        if self.world.ball != None:
            if(self.current_plan.isValid() and not self.current_plan.isFinished()):
                return self.current_plan.nextCommand()
            else:
            # If self.current_plan is invalid, then choose a new plan and return a command from it

            #TODO - is this legal? It seems ok, need to check for sure
            # Reset the old plan
            #self.plans[self.current_plan] = self.plans[self.current_plan_index].__init__(self.world, self.robot)

                for plan in self.plans:
                    if(plan.isValid()):
                        self.current_plan = plan
                        return self.current_plan.nextCommand()

        return CommandDict.stop()



