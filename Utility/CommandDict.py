class CommandDict(dict):
    """
    A dictionary to be sent between the planner and RobotAPI
    """
    def __init__(self, speed, direction, kick):
        """
        :param speed: 0-100 motor speed in percent
        :param direction: "Forward", "Backward", "Left", "Right", "None"
        :param kick: "Kick", "Prepare", "Catch", "None"
        """
        assert(speed <= 100 and speed >= 0)
        assert(direction in ["Forward", "Backward", "Left", "Right", "None"])
        assert(kick in ["Kick", "Prepare", "Catch", "None"])
        self["speed"] = speed
        self["direction"] = direction
        self["kick"] = kick

    @staticmethod
    # TODO This could probably be done generically (without hardcoding specific commands). -Very- low down on the todo list though...
    def mergeCommands(command1, command2):
        """
        Helper function to merge two commands as our system is limited to sending one command per frame. Any "None" entries are overridden by the entries of the other command.
        :param command1: The first command. The speed is always taken from this command and any other variables in case of a conflict.
        :param command2: The second command.
        """
        direction = "None"
        if(command1["direction"] == None\ and not command2["direction"] == None):
            direction = command2["direction"]
        else:
            direction = command1["direction"]

        kick = "None"
        if(command1["kick"] == None and not command2["kick"] == None):
            kick = command2["kick"]
        else:
            kick = command1["kick"]

        return CommandDict(command1["speed"], direction, kick)

    @staticmethod
    def stop():
        """
        :return: The command to stop everything
        """
        return CommandDict(0, "None", "None")

    @staticmethod
    def prepare():
        """
        :return: The command to prepare the grabber
        """
        return CommandDict(100, "None", "Prepare")

    @staticmethod
    def catch():
        """
        :return: The command to catch the ball
        """
        return CommandDict(100, "None", "Catch")

