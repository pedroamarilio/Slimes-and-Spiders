from entities.units.base_unit import BaseUnit
import assets

class Dragon(BaseUnit):

    def __init__(self, x, y):
        super().__init__("assets/sprites/dragonflying.png", x, y, animated=True, sprites=10)

        self.vision = 150
        self.damage = 50
        self.cost = 100
        self.range = 200
        self.baseCooldown = 60
        self.cooldown = 0
        self.speed = 40
        # flying unit
        self.flying = True

