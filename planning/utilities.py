from math import tan, pi, hypot
import json
import os
import consol

from worldstate import Robot


DISTANCE_MATCH_THRESHOLD = 15
ANGLE_MATCH_THRESHOLD = pi/10
BALL_ANGLE_THRESHOLD = pi/20
MAX_DISPLACEMENT_SPEED = 690
MAX_ANGLE_SPEED = 50
BALL_VELOCITY = 3

PATH = os.getcwd()
PITCHES = ['Pitch_0', 'Pitch_1', 'Pitch_2']

def is_shot_blocked(world, our_robot, their_robot):
    '''
    Checks if our robot could shoot past their robot
    '''
    predicted_y = predict_y_intersection(
        world, their_robot.x, our_robot, full_width=True, bounce=True)
    if predicted_y is None:
        return True
    consol.log('##########', (predicted_y, their_robot.y, their_robot.length), 'Utils')
    b = abs(predicted_y - their_robot.y) < their_robot.length
    consol.log('is blocked', b, 'Utils')
    return b


def is_attacker_shot_blocked(world, our_attacker, their_defender):
    '''
    Checks if our attacker would score if it would immediately turn and shoot.
    '''

    # Acceptable distance that the opponent defender can be relative to our
    # shooting position in order for us to have a clear shot.
    distance_threshold = 40

    # Return True if attacker and defender ar close to each other on
    # the y dimension
    return abs(our_attacker.y - their_defender.y) < distance_threshold


def can_score(world, our_robot, their_goal, turn=0):
    # Offset the robot angle if need be
    robot_angle = our_robot.angle + turn
    goal_zone_poly = world.pitch.zones[their_goal.zone][0]

    reverse = True if their_goal.zone == 3 else False
    goal_posts = sorted(goal_zone_poly, key=lambda x: x[0], reverse=reverse)[:2]
    # Makes goal be sorted from smaller to bigger
    goal_posts = sorted(goal_posts, key=lambda x: x[1])

    goal_x = goal_posts[0][0]

    robot = Robot(
        our_robot.zone, our_robot.x, our_robot.y, robot_angle % (pi * 2), our_robot.velocity)

    predicted_y = predict_y_intersection(world, goal_x, robot, full_width=True)

    return goal_posts[0][1] < predicted_y < goal_posts[1][1]

def predict_y_intersection(world, predict_for_x, robot, full_width=False, bounce=False):
        '''
        Predicts the (x, y) coordinates of the ball shot by the robot
        Corrects them if it's out of the bottom_y - top_y range.
        If bounce is set to True, predicts for a bounced shot
        Returns None if the robot is facing the wrong direction.
        '''
        x = robot.x
        y = robot.y
        top_y = world._pitch.height - 60 if full_width else world.our_goal.y + (world.our_goal.width/2) - 30
        bottom_y = 60 if full_width else world.our_goal.y - (world.our_goal.width/2) + 30
        angle = robot.angle
        if (robot.x < predict_for_x and not (pi/2 < angle < 3*pi/2)) or (robot.x > predict_for_x and (3*pi/2 > angle > pi/2)):
            if bounce:
                if not (0 <= (y + tan(angle) * (predict_for_x - x)) <= world._pitch.height):
                    bounce_pos = 'top' if (y + tan(angle) * (predict_for_x - x)) > world._pitch.height else 'bottom'
                    x += (world._pitch.height - y) / tan(angle) if bounce_pos == 'top' else (0 - y) / tan(angle)
                    y = world._pitch.height if bounce_pos == 'top' else 0
                    angle = (-angle) % (2*pi)
            predicted_y = (y + tan(angle) * (predict_for_x - x))
            # Correcting the y coordinate to the closest y coordinate on the goal line:
            if predicted_y > top_y:
                return top_y
            elif predicted_y < bottom_y:
                return bottom_y
            return predicted_y
        else:
            return None

def has_matched(robot, x=None, y=None, angle=None, angle_threshold=ANGLE_MATCH_THRESHOLD, distance_threshold=DISTANCE_MATCH_THRESHOLD):
    dist_matched = True
    angle_matched = True
    if not(x is None and y is None):
        dist_matched = hypot(robot.x - x, robot.y - y) < distance_threshold
    if not(angle is None):
        angle_matched = abs(angle) < angle_threshold
    return dist_matched and angle_matched


# Code duplicated from vision.tools to avoid the dependency on OpenCV
# TODO - consolidate into single location
def get_croppings(filename=PATH+'/vision/calibrations/croppings.json', pitch=0):
    croppings = get_json(filename)
    return croppings[PITCHES[pitch]]


def get_json(filename=PATH+'/vision/calibrations/calibrations.json'):
    _file = open(filename, 'r')
    content = json.loads(_file.read())
    _file.close()
    return content
