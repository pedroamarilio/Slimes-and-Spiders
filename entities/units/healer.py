from entities.units.base_unit import BaseUnit
import assets

class Healer(BaseUnit):

    def __init__(self, x, y):
        super().__init__("assets/sprites/healerfloating.png", x, y, animated=True, sprites=2)

        self.healing = 5
        self.vision = 80
        self.damage = 0
        self.cost = 70
        self.range = 100
        self.baseCooldown = 60
        self.cooldown = 0
        self.speed = 80
        # mark as flying so it can pass over buildings/units
        self.flying = True
