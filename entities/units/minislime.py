from entities.units.base_unit import BaseUnit
import assets

class MiniSlime(BaseUnit):

    def __init__(self, x, y):
        super().__init__("assets/sprites/lilslimewalking.png", x, y, animated=True, sprites=5)

        self.vision = 60
        self.damage = 10
        self.cost = 0
        self.range = 80
        self.baseCooldown = 60
        self.cooldown = 0
        self.speed = 25
