from math import pi

class Coordinate(object):

    def __init__(self, x, y):
        if x == None or y == None:
            raise ValueError('Can not initialize to attributes to None')
        else:
            self._x = x
            self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, new_x):
        if new_x == None:
            raise ValueError('Can not set attributes of Coordinate to None')
        else:
            self._x = new_x

    @y.setter
    def y(self, new_y):
        if new_y == None:
            raise ValueError('Can not set attributes of Coordinate to None')
        else:
            self._y = new_y

    def __repr__(self):
        return 'x: %s, y: %s\n' % (self._x, self._y)


class Vector(Coordinate):

    def __init__(self, x, y, angle, velocity):
        super(Vector, self).__init__(x, y)
        if angle == None or velocity == None:
            raise ValueError('Can not initialise attributes of Vector to None')
        else:
            self._angle = angle
            self._velocity = velocity

    @property
    def angle(self):
        return self._angle

    @property
    def velocity(self):
        return self._velocity



    @angle.setter
    def angle(self, new_angle):
        if new_angle == None:
            raise ValueError('Angle can not be None')
        self._angle = new_angle

    @velocity.setter
    def velocity(self, new_velocity):
        if new_velocity == None:
            raise ValueError('Velocity can not be None')
        self._velocity = new_velocity

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and (self.__dict__ == other.__dict__))

    def __repr__(self):
        return ('x: %s, y: %s, angle: %s, velocity: %s\n' %
                (self.x, self.y,
                 self._angle, self._velocity))