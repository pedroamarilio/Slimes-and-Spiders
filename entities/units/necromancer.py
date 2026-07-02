from entities.units.base_unit import BaseUnit
from game.economy import Economy
import assets

class Necromancer(BaseUnit):

    def __init__(self, x, y):
        super().__init__("assets/sprites/necromancerwalking.png", x, y, animated=True, sprites=9)

        self.vision = 80
        self.damage = 0
        self.cost = 50
        self.range = 150
        self.baseCooldown = 120
        self.cooldown = 0
        self.speed = 60

