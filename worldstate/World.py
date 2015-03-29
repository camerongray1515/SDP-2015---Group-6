from math import pi

from worldstate.Coordinate import Vector
from worldstate.Robot import Robot
from worldstate.OtherPitchObjects import Pitch, Goal, Ball
from vision.Kalman import Kalman
import FrameEst
import consol


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
        self.Kp = Kalman()
        self.Ka = Kalman() #not entirely sure that separate kalmans are required but if
                           #different values are required for internal variables
                           #it could be useful to be able to change them here easily

        self.x = 0.0
        self.y = 0.0
        self.a = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self.dangle = 0.0
        global world
        world = self






    def get_future(self):
        oa = self.our_attacker
        cd, ca = ([oa._vector.x, oa._vector.y], oa._vector.angle)

        return FrameEst.get_rot_future(cd, ca)

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



    @staticmethod
    def low_pass(new_val, old_val, coef = 0.6):
        return coef * new_val + (1.0 - coef) * old_val




    def update_positions(self, pos_dict):
        ''' This method will update the positions of the pitch objects
            that it gets passed by the vision system '''
        robots = {'our_attacker':self.our_attacker,'their_attacker':self.their_attacker , 'our_defender':self.our_defender ,'their_defender':self.their_defender}

        # Using these it should be possible to predict the position and angle of our robot
        # Currently is set to predict 20 frames ahead
        last_x = self.our_attacker.vector.x
        last_y = self.our_attacker.vector.y
        last_angle = self.our_attacker.vector.angle

        x = pos_dict['our_attacker'].x
        y = pos_dict['our_attacker'].y
        a = pos_dict['our_attacker'].angle
        dx = x - last_x
        dy = y - last_y
        dangle = a - last_angle



        x = World.low_pass(x, self.x)
        y = World.low_pass(y, self.x)
        a = World.low_pass(a, self.x)
        dx = World.low_pass(dx, self.x)
        dy = World.low_pass(dy, self.x)
        dangle = World.low_pass(dangle, self.x)


        predicted_pos = self.Kp.n_frames(20, [x,y,dx,dy])
        predicted_angle = self.Ka.n_frames(20, [a,0,dangle,0])
        self.our_attacker.predicted_vector = Vector(predicted_pos[0],predicted_pos[1],predicted_angle[0],0)
        # Currently doesnt use any predicted velocity. If any reason to use this were to be found feel free to add

        # Update robot positions
        for key in robots.keys():
            robots[key].vector = pos_dict[key]

        # Update ball
        self.ball.vector = pos_dict['ball']


        FrameEst.update()

        self.get_future()
