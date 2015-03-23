from math import pi, hypot, atan2

from Polygon.cPolygon import Polygon

from worldstate.PitchObject import PitchObject
import numpy as np
import math
# Width measures the front and back of an object
# Length measures along the sides of an object
ROBOT_WIDTH = 30
ROBOT_LENGTH = 45
ROBOT_HEIGHT = 10

class Robot(PitchObject):

    def __init__(self, zone, x, y, angle, velocity, width=ROBOT_WIDTH, length=ROBOT_LENGTH, height=ROBOT_HEIGHT, angle_offset=0):
        super(Robot, self).__init__(x, y, angle, velocity, width, length, height, angle_offset)
        self._zone = zone
        self._catcher = 'open'
        self.target_y = None
        self.predicted_vector = self.vector

    @property
    def zone(self):
        return self._zone

    @property
    def catcher_area(self):
        front_left = (self.x + self._catcher_area['front_offset'] + self._catcher_area['height'], self.y + self._catcher_area['width']/2.0)
        front_right = (self.x + self._catcher_area['front_offset'] + self._catcher_area['height'], self.y - self._catcher_area['width']/2.0)
        back_left = (self.x + self._catcher_area['front_offset'], self.y + self._catcher_area['width']/2.0)
        back_right = (self.x + self._catcher_area['front_offset'], self.y - self._catcher_area['width']/2.0)
        area = Polygon((front_left, front_right, back_left, back_right))
        area.rotate(self.angle, self.x, self.y)
        return area

    @property
    def ball_area(self):
        front_left = (self.x + self._catcher_area['front_offset'] + self._catcher_area['height']*1.5, self.y + self._catcher_area['width']/2.0)
        front_right = (self.x + self._catcher_area['front_offset'] + self._catcher_area['height']*1.5, self.y - self._catcher_area['width']/2.0)
        back_left = (self.x - self._catcher_area['front_offset'], self.y + self._catcher_area['width'])
        back_right = (self.x - self._catcher_area['front_offset'], self.y - self._catcher_area['width'])
        area = Polygon((front_left, front_right, back_left, back_right))
        area.rotate(self.angle, self.x, self.y)
        return area


    @catcher_area.setter
    def catcher_area(self, area_dict):
        self._catcher_area = area_dict

    @property
    def catcher(self):
        return self._catcher

    @catcher.setter
    def catcher(self, new_position):
        assert new_position in ['open', 'closed', 'prepared']
        self._catcher = new_position

    def can_catch_ball(self, ball):
        '''
        Get if the ball is in the catcher zone but may not have possession
        '''
        return self.catcher_area.isInside(ball.x, ball.y)

    def has_ball(self, ball):
        '''
        Gets if the robot has possession of the ball
        '''
        return (self._catcher == 'closed') #and self.ball_area.isInside(ball.x, ball.y)

    def get_rotation_to_point(self, x, y):
        '''
        This method returns an angle by which the robot needs to rotate to achieve alignment.
        It takes either an x, y coordinate of the object that we want to rotate to
        '''
        delta_x = x - self.x
        delta_y = y - self.y
        displacement = hypot(delta_x, delta_y)
        if displacement == 0:
            theta = 0
        else:
            theta = atan2(delta_y, delta_x) - self.angle 
            if theta > pi:
                theta -= 2*pi
            elif theta < -pi:
                theta += 2*pi
        assert -pi <= theta <= pi
        return theta

    def get_euclidean_distance_to_point(self, x, y):
        '''
        This method returns the displacement between the robot and the (x, y) coordinate.
        '''
        delta_x = x - self.x
        delta_y = y - self.y
        displacement = hypot(delta_x, delta_y)
        return displacement

    @staticmethod
    def angle_to_vector(angle):
        x = math.cos(angle)
        y = math.sin(angle)
        return np.array([x,y])


    def get_dot_to_target(self, x, y):
        rob_pos = np.array([self.x, self.y])
        target_pos = np.array([x, y])
        vec = target_pos - rob_pos
        av = vec / np.linalg.norm(vec)

        rv = Robot.angle_to_vector(self.angle)
        return np.dot(av, rv)



    def get_direction_to_point(self, x, y):
        '''
        This method returns the displacement and angle to coordinate x, y.
        '''
        return self.get_euclidean_distance_to_point(x, y), self.get_rotation_to_point(x, y)

    def get_pass_path(self, target):
        '''
        Gets a path represented by a Polygon for the area for passing ball between two robots
        '''
        robot_poly = self.get_polygon()
        target_poly = target.get_polygon()
        return Polygon(robot_poly[0], robot_poly[1], target_poly[0], target_poly[1])

    


    def __repr__(self):
        return ('zone: %s\nx: %s\ny: %s\nangle: %s\nvelocity: %s\ndimensions: %s\n' %
                (self._zone, self.x, self.y,
                 self.angle, self.velocity, (self.width, self.length, self.height)))
