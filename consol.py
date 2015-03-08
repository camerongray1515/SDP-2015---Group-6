__author__ = 's1210443'

import os
import time

# use log function to print something that changes often


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

groups = {}


def special_str(s, type):
    return type + str(s) + bcolors.ENDC


def log(name, value, group = "general"):
    if group not in groups:
        groups[group] = {}
    groups[group][name] = value

def log_time(group, name = 'time'):
    if group not in groups:
        groups[group] = {}
    localtime = time.asctime( time.localtime(time.time()) )
    groups[group][name] = localtime


def draw():
    clear = "\n" * 100
    print clear
    print(special_str('NOTE: ', bcolors.BOLD) + 'vision window has to be active window in order for key input to work')

    # won't work on windows
    # os.system('clear')
    for k,v in groups.iteritems():
        print(special_str(k + "-----------", bcolors.BOLD))
        for k,v in v.iteritems():
            line = str(k) + ": "
            if isinstance(v, bool):
                line += special_str(v, bcolors.OKGREEN if v else bcolors.FAIL)
            else:
                line += str(v)
            print(line)
        print(special_str("----------------", bcolors.BOLD))
