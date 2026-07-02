from entities.units.base_unit import BaseUnit
import assets

class Archer(BaseUnit):

    def __init__(self, x, y):
        super().__init__("assets/sprites/archerwalking.png", x, y, animated=True, sprites=8)

        self.sprite.set_curr_frame(0)
        # stats
        self.name = "Archer"
        self.damage = 15
        self.vision = 130
        self.range = 300
        self.cost = 30
        self.speed = 90
        self.baseCooldown = 60
        self.cooldown = 0

    def update(self, dt):
        try:
            super().update(dt)
        except Exception:
            pass
