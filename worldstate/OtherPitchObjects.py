from Polygon.cPolygon import Polygon

from worldstate.PitchObject import PitchObject
from planning.utilities import get_croppings
from math import cos, sin, pi
import consol

BALL_WIDTH = 5
BALL_LENGTH = 5
BALL_HEIGHT = 5

GOAL_WIDTH = 140
GOAL_LENGTH = 1
GOAL_HEIGHT = 10


class Ball(PitchObject):

    def __init__(self, x, y, angle, velocity):
        super(Ball, self).__init__(x, y, angle, velocity, BALL_WIDTH, BALL_LENGTH, BALL_HEIGHT)

    '''
    @property
    def x(self):
        nx = self._vector.x + cos(self.angle) * self.velocity * 1.0
        consol.log_pos_angle([nx, self.y], self.angle, self, self.velocity * 1.0)
        return nx

    @property
    def y(self):
        return self._vector.y + sin(self.angle) * self.velocity * 1.0
    '''

class Goal(PitchObject):

    def __init__(self, zone, x, y, angle):
        super(Goal, self).__init__(x, y, angle, 0, GOAL_WIDTH, GOAL_LENGTH, GOAL_HEIGHT)
        self._zone = zone

    @property
    def zone(self):
        return self._zone

    def __repr__(self):
        return ('zone: %s\nx: %s\ny: %s\nangle: %s\nvelocity: %s\ndimensions: %s\n' %
                (self._zone, self.x, self.y, self.angle, self.velocity, (self.width, self.length, self.height)))


class Pitch(object):
    '''
    Class that describes the pitch
    '''

    def __init__(self, pitch_num):
        config_json = get_croppings(pitch=pitch_num)

        self._width = max([point[0] for point in config_json['outline']]) - min([point[0] for point in config_json['outline']])
        self._height = max([point[1] for point in config_json['outline']]) - min([point[1] for point in config_json['outline']])
        # Getting the zones:
        self._zones = []
        self._zones.append(Polygon([(x, self._height - y) for (x, y) in config_json['Zone_0']]))
        self._zones.append(Polygon([(x, self._height - y) for (x, y) in config_json['Zone_1']]))
        self._zones.append(Polygon([(x, self._height - y) for (x, y) in config_json['Zone_2']]))
        self._zones.append(Polygon([(x, self._height - y) for (x, y) in config_json['Zone_3']]))

    def is_within_bounds(self, robot, x, y):
        '''
        Checks whether the position/point planned for the robot is reachable
        '''
        zone = self._zones[robot.zone]
        return zone.isInside(x, y)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def zones(self):
        return self._zones

    def __repr__(self):
        return str(self._zones)