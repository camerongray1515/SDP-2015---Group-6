import pygame
from pygame.locals import *
import math
import pdb
import random
import time

COORDSCALE = 1
MESSAGEFRAMES = 40
WIDTH = 540
HEIGHT = 290
DIVIDERWIDTH = 6
DIV1X = 115 # These should match the clipping settings used for the planner
DIV2X = 255
DIV3X = 395
GOALWIDTH = 200
INSETWIDTH = 37
PLATEWIDTH = 40
BALL_RAD = 8
COLOURS = {"PITCH": (0, 120, 0), 'DIVIDER': (255,255,255), 'CORNER': (32,32,32), 'PLATE':(51, 255, 55),
            "ARROW": (255,0,0), "LABEL":(255,255,255), "BALL": (255,40,40), "BLOCKED":(200,0,0,150), "CLEAR":(0,0,200, 150)}
STATE_LABEL_X = {'LDEF':60, 'RATK':170, 'LATK':320, 'RDEF':470}
STATE_LABEL_Y = 250
TARG_X = 200
TARG_Y = 150
OBST_X = 350
OBST_Y = 150

class blocktest(object):
    world = None
    canvas = None
    messages = []

    @staticmethod
    def blocked(target_x, target_y, obstacle_x, obstacle_y, robot_x, robot_y, obstacle_width=50):
        d_y = robot_y - target_y
        d_x = robot_x - target_x
        
        # Catch div by zero
        if d_x == 0:
        	d_x = 0.0001 

        m = d_y/d_x
        c = robot_y - m*robot_x
        #Compare y-coords when x is equal:
        ball_y_at_obstacle = m*obstacle_x + c
        if math.fabs(ball_y_at_obstacle - obstacle_y)<obstacle_width:
            return True
        return False



    def set_world(self, world):
        self.world = world

    def show(self):
        world = self.world
        self.draw_background()
        #Draw Target
        pygame.draw.circle(self.windowSurface, COLOURS['PLATE'], (TARG_X, TARG_Y), 10)
        #Draw Obstacle
        pygame.draw.circle(self.windowSurface, COLOURS['PLATE'], (OBST_X, OBST_Y), 10)
        s = pygame.Surface((WIDTH,HEIGHT))
        s.set_alpha(150)
        for x in range(WIDTH):
        	for y in range(HEIGHT):
        		is_blocked = blocktest.blocked(TARG_X, TARG_Y, OBST_X, OBST_Y, x, y)
        		if is_blocked:
        			pygame.draw.line(s, COLOURS['BLOCKED'], (x, y), (x,y))
        		#else:
        			#pygame.draw.line(s, COLOURS['CLEAR'], (x, y), (x,y))
        self.windowSurface.blit(s, (0,0))

        pygame.display.flip()

    def read_messages(self):
        "Should be called only when the simulator provides new commands. Stores messages such as kicker actions"
        for entity in [self.world['LEFTDEF'],self.world['RIGHTATK'], self.world['LEFTATK'],self.world['RIGHTDEF']]:
            if entity['message'] is not None:
                # Add a random ofset - crude way of making it more likley that multiple messages will be visible.
                message_coords = (entity['x'] + 40 * random.random(), entity['y'] + 40 * random.random())
                message = (entity['message'], message_coords, MESSAGEFRAMES)
                self.messages.append(message)

    def draw_messages(self):
        new_messages = []
        for (message, coords, frames) in self.messages:
            font = pygame.font.Font(None, 26)
            text = font.render(message, 1, COLOURS['LABEL'])
            textpos = text.get_rect()
            textpos.centerx = COORDSCALE*coords[0] + 20
            textpos.centery = COORDSCALE*coords[1] + 20
            self.windowSurface.blit(text, textpos)
            frames = frames - 1
            if frames > 0:
                new_messages.append((message, coords, frames))
        self.messages = new_messages



    def __init__(self, labels=False):
        pygame.init()
        self.labels = labels
        self.windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE)
        self.windowSurface.fill(COLOURS['PITCH'])
        self.draw_background()


    def draw_background(self):
        # Clear Screen
        self.windowSurface.fill(COLOURS['PITCH'])
        # pygame.draw.polygon(self.windowSurface, COLOURS['PITCH'], ((0,0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)))

        # Draw zone dividers
        pygame.draw.polygon(self.windowSurface, COLOURS['DIVIDER'], ((DIVIDERWIDTH/2 + DIV1X, 0), (DIVIDERWIDTH/2 + DIV1X, HEIGHT), (-DIVIDERWIDTH/2 + DIV1X, HEIGHT), (-DIVIDERWIDTH/2 + DIV1X, 0)))
        pygame.draw.polygon(self.windowSurface, COLOURS['DIVIDER'], ((DIVIDERWIDTH/2 + DIV2X, 0), (DIVIDERWIDTH/2 + DIV2X, HEIGHT), (-DIVIDERWIDTH/2 + DIV2X, HEIGHT), (-DIVIDERWIDTH/2 + DIV2X, 0)))
        pygame.draw.polygon(self.windowSurface, COLOURS['DIVIDER'], ((DIVIDERWIDTH/2 + DIV3X, 0), (DIVIDERWIDTH/2 + DIV3X, HEIGHT), (-DIVIDERWIDTH/2 + DIV3X, HEIGHT), (-DIVIDERWIDTH/2 + DIV3X, 0)))

        # Draw Defender Zone Indents
        pygame.draw.polygon(self.windowSurface, COLOURS['CORNER'], ((0, HEIGHT/2 + GOALWIDTH/2), (INSETWIDTH, HEIGHT), (0, HEIGHT)))
        pygame.draw.polygon(self.windowSurface, COLOURS['CORNER'], ((0, HEIGHT/2 - GOALWIDTH/2), (INSETWIDTH, 0), (0, 0)))
        pygame.draw.polygon(self.windowSurface, COLOURS['CORNER'], ((WIDTH, HEIGHT/2 + GOALWIDTH/2), (WIDTH - INSETWIDTH, HEIGHT), (WIDTH, HEIGHT)))
        pygame.draw.polygon(self.windowSurface, COLOURS['CORNER'], ((WIDTH, HEIGHT/2 - GOALWIDTH/2), (WIDTH - INSETWIDTH, 0), (WIDTH, 0)))


if __name__ == '__main__':
    disp = blocktest()
    disp.show()
    time.sleep(200)
