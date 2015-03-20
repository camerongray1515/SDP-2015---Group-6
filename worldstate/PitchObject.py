from Polygon.cPolygon import Polygon

from worldstate.Coordinate import Vector


class PitchObject(object):
    '''
    A class that describes an abstract pitch object
    Width measures the front and back of an object
    Length measures along the sides of an object
    '''

    def __init__(self, x, y, angle, velocity, width, length, height, angle_offset=0):
        if width < 0 or length < 0 or height < 0:
            raise ValueError('Object dimensions must be positive')
        else:
            self._width = width
            self._length = length
            self._height = height
            self._angle_offset = angle_offset
            self._vector = Vector(x, y, angle, velocity)

    @property
    def width(self):
        return self._width

    @property
    def length(self):
        return self._length

    @property
    def height(self):
        return self._height

    @property
    def angle_offset(self):
        return self._angle_offset

    @property
    def angle(self):
        return self._vector.angle

    @property
    def velocity(self):
        return self._vector.velocity

    @property
    def x(self):
        return self._vector.x

    @property
    def y(self):
        return self._vector.y

    @property
    def vector(self):
        return self._vector

    @vector.setter
    def vector(self, new_vector):
        if new_vector == None or not isinstance(new_vector, Vector):
            raise ValueError('The new vector can not be None and must be an instance of a Vector')
        else:
            self._vector = Vector(new_vector.x, new_vector.y, new_vector.angle - self._angle_offset, new_vector.velocity)

    def get_generic_polygon(self, width, length):
        '''
        Get polygon drawn around the current object, but with some
        custom width and length:
        '''
        front_left = (self.x + length/2, self.y + width/2)
        front_right = (self.x + length/2, self.y - width/2)
        back_left = (self.x - length/2, self.y + width/2)
        back_right = (self.x - length/2, self.y - width/2)
        poly = Polygon((front_left, front_right, back_left, back_right))
        poly.rotate(self.angle, self.x, self.y)
        return poly[0]

    def get_polygon(self):
        '''
        Returns 4 edges of a rectangle bounding the current object in the
        following order: front left, front right, bottom left and bottom right.
        '''
        return self.get_generic_polygon(self.width, self.length)

    def __repr__(self):
        return ('x: %s\ny: %s\nangle: %s\nvelocity: %s\ndimensions: %s\n' %
                (self.x, self.y,
                 self.angle, self.velocity, (self.width, self.length, self.height)))