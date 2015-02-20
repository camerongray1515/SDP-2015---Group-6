import math
import pdb
from planning.Coordinate import Vector

class Simulator(object):
    FPS = 120 # Simulator frames per second to aim for
    LEFTDEF = {}
    LEFTATK = {}
    RIGHTDEF = {}
    RIGHTATK = {}
    WIDTH = 540
    HEIGHT = 290
    BALL = {}
    HAS_BALL = None
    ROBOT_RADIUS = 20
    BALL_FRICTION = 0.1
    MAX_SPEED = 20
    MAX_ROTATION = 3
    CATCH_DISTANCE = 35
    KICK_SPEED = 30
    VELOCITY_SCALE = 3.0 # Adjust if the velocity does not match the coordinate system.

    def __init__(self, left_def=None, left_atk=None, right_def=None, right_atk = None, fps=FPS, world=None):
        self.LEFTDEF['planner'] = left_def
        self.LEFTATK['planner'] = left_atk
        self.RIGHTDEF['planner'] = right_def
        self.RIGHTATK['planner'] = right_atk
        self.FPS = fps
        self.world = world
        self.setup_world()

    def setup_world(self):
        # Should really be speed rather than velocity, blame inherited code
        keys = ['x', 'y', 'angle', 'velocity']
        for key in keys:
            self.LEFTDEF[key] = self.world['our_defender'][key]
            self.LEFTATK[key] = self.world['our_attacker'][key]
            self.RIGHTDEF[key] = self.world['their_defender'][key]
            self.RIGHTATK[key] = self.world['their_attacker'][key]
            self.BALL[key] = self.world['ball'][key]
        #Create additional variables
        for entity in [self.LEFTDEF, self.LEFTATK, self.RIGHTDEF, self.RIGHTATK, self.BALL]:
            entity['angular_velocity'] = 0.0
            entity['angular_acceleration'] = 0.0
            entity['acceleration'] = 0.0
            entity['message'] = None

    def step(self):
        # stop robots on collision
        timestep = 1.0/self.FPS
        for entity in [self.LEFTDEF, self.LEFTATK, self.RIGHTDEF, self.RIGHTATK, self.BALL]:
            distance_x = timestep * self.VELOCITY_SCALE * entity['velocity'] * math.cos(entity['angle'])
            distance_y = timestep * self.VELOCITY_SCALE * entity['velocity'] * math.sin(entity['angle'])
            entity['x'] = entity['x'] + distance_x
            entity['y'] = entity['y'] + distance_y
            entity['angle'] = entity['angle'] + (timestep * entity['angular_velocity'])
            entity['velocity'] = entity['velocity'] + (timestep * entity['acceleration'])
            entity['angular_velocity'] = entity['angular_velocity'] + (timestep * entity['angular_acceleration'])
            # Constrain angle to be 0 <= angle < 2pi
            while entity['angle'] >= 2 * math.pi:
                entity['angle'] = entity['angle'] - (2 * math.pi)
            while entity['angle'] < 0:
                entity['angle'] = entity['angle'] + (2 * math.pi)
            #Enforce speed limit & keep robots on pitch
            if entity != self.BALL:
                if entity['velocity'] > self.MAX_SPEED:
                    entity['velocity'] = self.MAX_SPEED
                if entity['angular_velocity'] > self.MAX_ROTATION:
                    entity['angular_velocity'] = self.MAX_ROTATION
                if entity['angular_velocity'] < - self.MAX_ROTATION:
                    entity['angular_velocity'] = -self.MAX_ROTATION
                if entity['x'] < 0:
                    entity['x'] = 0
                if entity['x'] > self.WIDTH:
                    entity['x'] = self.WIDTH
                if entity['y'] < 0:
                    entity['y'] = 0
                if entity['y'] > self.HEIGHT:
                    entity['y'] = self.HEIGHT

            # Apply friction
            if entity == self.BALL:
                entity['velocity'] = entity['velocity'] - self.BALL_FRICTION*entity['velocity']*timestep

        self.bounce_ball()
        if self.HAS_BALL is not None:
            self.move_ball()

    def bounce_ball(self):
        "(very) Crude bounce method to stop the ball leaving the screen"
        if self.BALL['y'] > self.HEIGHT:
            self.BALL['angle'] += self.BALL['angle'] * 2
            self.BALL['y'] = 0
        if self.BALL['y'] < 0:
            self.BALL['angle'] += (self.BALL['angle'] - 3*math.pi/2) * 2
            self.BALL['y'] = self.HEIGHT
        if self.BALL['x'] < 0:
            self.BALL['angle'] += -self.BALL['angle']
            self.BALL['x'] = 0
        if self. BALL['x'] > self.WIDTH:
            self.BALL['angle'] = math.pi - self.BALL['angle']
            self.BALL['x'] = self.WIDTH
        while self. BALL['angle'] >= 2 * math.pi:
            self. BALL['angle'] = self. BALL['angle'] - (2 * math.pi)
        while self. BALL['angle'] < 0:
            self. BALL['angle'] = self. BALL['angle'] + (2 * math.pi)

    def move_ball(self):
        "Move the ball if it is attached to some robot"
        if self.HAS_BALL is None:
            return
        robot = self.HAS_BALL
        self.BALL['x'] = robot['x'] + self.ROBOT_RADIUS*math.cos(robot['angle'])
        self.BALL['y'] = robot['y'] + self.ROBOT_RADIUS*math.sin(robot['angle'])
        self.BALL['velocity'] = robot['velocity']
        self.BALL['angle'] = robot['angle']


    def read_commands(self):
        for robot in [self.LEFTDEF, self.LEFTATK, self.RIGHTDEF, self.RIGHTATK]:
            if robot['planner'] is not None:
                command = robot['planner'].update(self.get_world_old())
                self._read_command(robot, command)

    def _read_command(self, robot, command):
        """Applies a command to a robot, changing its velocity, acceleration, etc."""
        if command['kick'] != 'None':
            print command
        if command["direction"] == 'None':
            robot['acceleration'] = 0
            robot['velocity'] = 0
            robot['angular_velocity'] = 0
            robot['angular_acceleration'] = 0
        elif command["direction"] == 'Forward':
            if command['speed'] > robot['acceleration']:
                robot['acceleration'] = command['speed']
            else:
                robot['acceleration'] = (command['speed'] + robot['acceleration'])/2
            robot['angular_velocity'] = 0
        elif command['direction'] == 'Left':
            if command['speed'] > robot['angular_acceleration']:
                robot['angular_acceleration'] = command['speed'] * 0.05
            else:
                robot['angular_acceleration'] = (command['speed'] * 0.05 +robot['angular_acceleration'])/2
        elif command['direction'] == 'Right':
            if command['speed'] < robot['angular_acceleration']:
                robot['angular_acceleration'] = command['speed'] * 0.05
            else:
                robot['angular_acceleration'] = (command['speed'] * 0.05 +robot['angular_acceleration'])/2
        elif command["direction"] == 'Backward':
            print "BACKWARD DETECTED - need to test this"
            if command['speed'] < robot['acceleration']:
                robot['acceleration'] = command['speed']
            else:
                robot['acceleration'] = (command['speed'] + robot['acceleration'])/2
            robot['angular_velocity'] = 0
        else:
            print command

        if command['kick'] == 'Catch':
            robot['message'] = 'Catch'
            if self.in_range(robot):
                self.HAS_BALL = robot
        elif command['kick'] == 'Kick':
            robot['message'] = 'Kick'
            self.HAS_BALL = None
            self.BALL['velocity'] = self.KICK_SPEED
        elif command['kick'] == 'Prepare':
            robot['message'] = 'Prepare'
        else:
            robot['message'] = 0

    def in_range(self, robot):
        """Returns true if the robot is within catching range of the ball"""
        delta_x = robot['x'] - self.BALL['x']
        delta_y =  robot['y'] - self.BALL['y']
        distance = math.sqrt(delta_x*delta_x + delta_y*delta_y)
        return distance <= self.CATCH_DISTANCE


    def get_world_new(self):
        return {'LEFTDEF':self.LEFTDEF, 'LEFTATK':self.LEFTATK, 'RIGHTDEF':self.RIGHTDEF, 'RIGHTATK':self.RIGHTATK, 'BALL':self.BALL}

    def get_world_old(self):
        """Returns the older representation format of world state used by the planner"""
        #TODO convert angle to be be 0<=angle<2pi
        old_world = {}
        vectorify = (lambda x: Vector(x['x'], x['y'], x['angle'], x['velocity']))
        old_world['our_defender'] = vectorify(self.LEFTDEF)
        old_world['our_attacker'] = vectorify(self.LEFTATK)
        old_world['their_attacker'] = vectorify(self.RIGHTATK)
        old_world['their_defender'] = vectorify(self.RIGHTDEF)
        old_world['ball'] = vectorify(self.BALL)
        return old_world