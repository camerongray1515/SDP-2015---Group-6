class Robot_Controller(object):
    """
    Robot_Controller superclass for robot control.
    """

    def __init__(self):
        """
        Connect to Brick and setup Motors/Sensors.
        """
        self.current_speed = 0

    def shutdown(self, comm):
        # TO DO
            pass


class Defender_Controller(Robot_Controller):
    """
    Defender implementation.
    """

    def __init__(self):
        """
        Do the same setup as the Robot class, as well as anything specific to the Defender.
        """
        super(Defender_Controller, self).__init__()

    def execute(self, comm, action):
        """
        Execute robot action.
        """

        if 'turn_90' in action:
            comm.write('D_RUN_ENGINE %d %d\n' % (0, 0))
            time.sleep(0.2)
            comm.write('D_RUN_SHOOT %d\n' % int(action['turn_90']))
            time.sleep(2.2)

        #print action
        left_motor = int(action['left_motor'])
        right_motor = int(action['right_motor'])
        speed = action['speed']

        comm.write('D_SET_ENGINE %d %d\n' % (speed, speed))
        comm.write('D_RUN_ENGINE %d %d\n' % (left_motor, right_motor))
        if action['kicker'] != 0:
            try:
                comm.write('D_RUN_KICK\n')
                time.sleep(0.5)
            except StandardError:
                pass
        elif action['catcher'] != 0:
            try:
                comm.write('D_RUN_CATCH\n')
            except StandardError:
                pass

    def shutdown(self, comm):
        comm.write('D_RUN_KICK\n')
        comm.write('D_RUN_ENGINE %d %d\n' % (0, 0))


class Attacker_Controller(Robot_Controller):
    """
    Attacker implementation.
    """

    def __init__(self):
        """
        Do the same setup as the Robot class, as well as anything specific to the Attacker.
        """
        super(Attacker_Controller, self).__init__()

    def execute(self, comm, action):
        """
        Execute robot action.
        """
        if 'turn_90' in action:
            comm.write('A_RUN_ENGINE %d %d\n' % (0, 0))
            time.sleep(0.2)
            comm.write('A_RUN_SHOOT %d\n' % int(action['turn_90']))
            # time.sleep(1.2)
        else:
            left_motor = int(action['left_motor'])
            right_motor = int(action['right_motor'])
            speed = int(action['speed'])
            comm.write('A_SET_ENGINE %d %d\n' % (speed, speed))
            comm.write('A_RUN_ENGINE %d %d\n' % (left_motor, right_motor))
            if action['kicker'] != 0:
                try:
                    comm.write('A_RUN_KICK\n')
                except StandardError:
                    pass
            elif action['catcher'] != 0:
                try:
                    comm.write('A_RUN_CATCH\n')
                except StandardError:
                    pass

    def shutdown(self, comm):
        comm.write('A_RUN_KICK\n')
        comm.write('A_RUN_ENGINE %d %d\n' % (0, 0))