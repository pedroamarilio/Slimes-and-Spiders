from entities.buildings.base_building import BaseBuilding

from game.economy import Change

class GoldMine(BaseBuilding):
    def __init__(self, x=1024, y=1024):
        # Increase GoldMine HP to 5000
        super().__init__(x, y, 5000, "assets/sprites/goldmine.png")

        self.exists = True

    def provide(self):
        Change(amount=100, entity_string=None, position=None)