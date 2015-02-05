from World import World

class Planning():

    def __init__(self, side,pitch,attacker=True):
        self.world = World(side, pitch)
        self.robot = self.world.our_attacker if attacker else self.world.our_defender



    def update(self, model_positions):
        self._world.update_positions(model_positions)

    def go_to(self,x,y):
        pass

    def rotate_to(self,angle):
        pass
