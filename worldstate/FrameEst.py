__author__ = 's1210443'
import numpy as np
import consol
from Control import robot_api
from time import time
from math import sin, cos,pi



#fest needs to be type of FrameEst
#add new est and deletes too old ones
# output format ([dx, dy], a)
def update():
    ra = robot_api.robot_api

    dt = time() - FrameEst.last_time
    fest = FrameEst(dt, ra.current_motor_speeds['right'], ra.current_motor_speeds['left'], time())

    consol.log('time', time(), 'Future')

    FrameEst.est = [x for x in FrameEst.est if x.time > time()-FrameEst.vision_late] + [fest]

    FrameEst.last_time = time()

def get_future():
    d = [0,0]
    a = 0

    consol.log('frames', [(int(x.len *1000), int(x.sl), int(x.sr)) for x in FrameEst.est], 'Future')

    for i in FrameEst.est:
        das = np.interp((i.sr -i.sl) * 0.5, [-100, -10, 10, 100], [-FrameEst.rot_speed, 0, 0, FrameEst.rot_speed]) * i.len
        a+= das

        dds = np.interp((i.sl + i.sr) * 0.5, [-100, -40, 40, 100], [-FrameEst.speed, 0, 0, FrameEst.speed]) * i.len

        # assuming average angle
        d += rot_vec([dds, 0], a * 0.5)

    #consol.log('future rel', (d,a), 'Future')


    return (d,a)


def rot_vec(vec, theta):
    rotMatrix = np.array([[np.cos(theta), -np.sin(theta)],
                [np.sin(theta),  np.cos(theta)]])

    return np.dot(rotMatrix, vec)


def get_rot_future(cd, ca):

    d, a = get_future()

    rel_d = rot_vec(d, ca)

    nd = np.array(cd + rel_d)

    na = (a + ca)%(2.0*pi)

    #consol.log('future abs', (nd, na), 'Future')
    consol.log_pos_angle(nd, na, 'Future')


    return (nd, na)


class FrameEst:

    vision_late = 0.3 # secs
    est = []
    last_time = time()

    speed = 200.0
    rot_speed = 4






    def __init__(self, len, sr, sl, time):
        self.len = len
        self.sr = sr
        self.sl = sl
        self.time = time
