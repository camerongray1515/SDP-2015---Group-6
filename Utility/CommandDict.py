class CommandDict(dict):
    """
    A dictionary to be sent between the planner and the robot api
    """
    def __init__(self, speed, direction, kick):
        """
        :param speed: 0-100 motor speed in percent
        :param direction: "Forward", "Backward", "Left", "Right","None"
        :param kick: "Kick","Prepare","Catch","None"
        """
        assert(speed <= 100 and speed >= 0)
        assert(direction in ["Forward", "Backward", "Left", "Right","None"])
        assert(kick in ["Kick","Prepare","Catch","None"])
        self["speed"] = speed
        self["direction"] = direction
        self["kick"] = kick


    @staticmethod
    def stop():
        """
        :return: The command to stop everything
        """
        return CommandDict(0,"None","None")
    @staticmethod
    def prepare():
        return CommandDict(100,"None","Prepare")

    @staticmethod
    def catch():
        return CommandDict(100,"None","Catch")

