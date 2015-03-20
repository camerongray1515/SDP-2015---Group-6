from math import pi

from worldstate.Robot import Robot
from worldstate.OtherPitchObjects import Pitch, Goal, Ball


class World(object):
    '''
    This class describes the environment
    '''

    def __init__(self, our_side, pitch_num):
        assert our_side in ['left', 'right']
        self._pitch = Pitch(pitch_num)
        self._our_side = our_side
        self._their_side = 'left' if our_side == 'right' else 'right'
        self._ball = Ball(0, 0, 0, 0)
        self._robots = []
        self._robots.append(Robot(0, 0, 0, 0, 0))
        self._robots.append(Robot(1, 0, 0, 0, 0))
        self._robots.append(Robot(2, 0, 0, 0, 0))
        self._robots.append(Robot(3, 0, 0, 0, 0))
        self._goals = []
        self._goals.append(Goal(0, 0, self._pitch.height/2.0, 0))
        self._goals.append(Goal(3, self._pitch.width, self._pitch.height/2.0, pi))


    @property
    def our_attacker(self):
        return self._robots[2] if self._our_side == 'left' else self._robots[1]

    @property
    def their_attacker(self):
        return self._robots[1] if self._our_side == 'left' else self._robots[2]

    @property
    def our_defender(self):
        return self._robots[0] if self._our_side == 'left' else self._robots[3]

    @property
    def their_defender(self):
        return self._robots[3] if self._our_side == 'left' else self._robots[0]

    @property
    def ball(self):
        return self._ball

    @property
    def our_goal(self):
        return self._goals[0] if self._our_side == 'left' else self._goals[1]

    @property
    def their_goal(self):
        return self._goals[1] if self._our_side == 'left' else self._goals[0]

    @property
    def pitch(self):
        return self._pitch

    def update_positions(self, pos_dict):
        ''' This method will update the positions of the pitch objects
            that it gets passed by the vision system '''
        robots = {'our_attacker':self.our_attacker,'their_attacker':self.their_attacker , 'our_defender':self.our_defender ,'their_defender':self.their_defender}
        for key in robots.keys():

            if robots[key].vector.angle == pos_dict[key].angle:
                robots[key].out_of_bounds_counter -= 1
            else:
                robots[key].out_of_bounds_counter = 5
            robots[key].vector = pos_dict[key]

        self.ball.vector = pos_dict['ball']
        # Checking if the robot locations make sense:
        # Is the side correct:
        if (self._our_side == 'left' and not(self.our_defender.x < self.their_attacker.x
            < self.our_attacker.x < self.their_defender.x)):
            #print "WARNING: The sides are probably wrong!"
	    pass
        if (self._our_side == 'right' and not(self.our_defender.x > self.their_attacker.x
            > self.our_attacker.x > self.their_defender.x)):
            #print "WARNING: The sides are probably wrong!"
            pass
