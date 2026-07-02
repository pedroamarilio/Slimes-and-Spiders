from entities.units.base_unit import BaseUnit
import assets

class Melee(BaseUnit):

    def __init__(self, x, y):
        super().__init__("assets/sprites/warriorwalking.png", x, y, animated=True, sprites=3)

        self.sprite.set_curr_frame(0)

        # stats
        self.name = "Warrior"
        self.damage = 30
        self.vision = 70
        self.range = 110
        self.cost = 30
        # increase warrior speed: previous + extra small buff (≈45% total)
        self.speed = int(round(40 * 1.45))
        self.baseCooldown = 60
        self.cooldown = 0

    def update(self, dt):
        try:
            super().update(dt)
        except Exception:
            pass

