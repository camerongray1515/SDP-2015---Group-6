import pygame
from pygame.locals import *
import math
import pdb
import random

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
            "ARROW": (255,0,0), "LABEL":(255,255,255), "BALL": (255,40,40)}
STATE_LABEL_X = {'LDEF':60, 'RATK':170, 'LATK':320, 'RDEF':470}
STATE_LABEL_Y = 250

class Visualise(object):
    world = None
    canvas = None
    messages = []


    def set_world(self, world):
        self.world = world

    def show(self):
        world = self.world
        self.draw_background()
        #Draw Robots
        for (robot, name) in [(world['LEFTDEF'], 'LDEF'), (world['RIGHTATK'], 'RATK'), (world['LEFTATK'], 'LATK'), (world['RIGHTDEF'], 'RDEF')]:
            points = ()
            hypotenuse = PLATEWIDTH/(2.0 * math.sqrt(2))
            for point in [0, 1, 2, 3]:
                angle = robot['angle'] + math.pi/4.0 + (point*math.pi/2.0)
                x_point = COORDSCALE * robot['x'] + (hypotenuse * math.cos(angle)) # Set X co-ordinate
                y_point = COORDSCALE * robot['y'] + (hypotenuse * math.sin(angle)) # Set Y co-ordinate
                points = points + ((x_point, y_point),)
            #Draw Plate
            pygame.draw.polygon(self.windowSurface, COLOURS['PLATE'], points)
            #Draw Arrow
            arrow_points = ((COORDSCALE * robot['x'], COORDSCALE * robot['y']),) + points[1:3]
            pygame.draw.polygon(self.windowSurface, COLOURS['ARROW'], arrow_points)
            #Draw Labels
            if self.labels:
                font = pygame.font.Font(None, 26)
                text = font.render(name, 0, COLOURS['LABEL'])
                textpos = text.get_rect()
                textpos.centerx = COORDSCALE*robot['x']
                textpos.centery = COORDSCALE*robot['y']
                self.windowSurface.blit(text, textpos)

                #Draw Planner state:
                if robot['planner'] is not None:
                	plan = robot['planner'].current_plan
                else:
                	plan = None
                if plan is None:
                    text = font.render("None", 0, COLOURS['LABEL'])
                else:
                    text = font.render(str(plan), 0, COLOURS['LABEL'])
                textpos = text.get_rect()
                textpos.centerx = STATE_LABEL_X[name]
                textpos.centery = STATE_LABEL_Y
                self.windowSurface.blit(text, textpos)
        #Draw Ball
        ball_pos = (int(world['BALL']['x']), int(world['BALL']['y']))
        pygame.draw.circle(self.windowSurface, COLOURS["BALL"], ball_pos, BALL_RAD)

        #Draw messages
        if self.labels:
            self.draw_messages()

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

def main():
    root = Tk()
    app = Visualise(master=root)
    app.mainloop()
    root.destroy()

if __name__ == '__main__':
    main()
