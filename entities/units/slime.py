from entities.units.base_unit import BaseUnit
import assets

class Slime(BaseUnit):

    def __init__(self, x, y):
        super().__init__("assets/sprites/bigslimewalking.png", x, y, animated=True, sprites=10)

        self.vision = 70
        self.damage = 20
        self.cost = 70
        self.range = 100
        self.baseCooldown = 60
        self.cooldown = 0
        self.speed = 50

