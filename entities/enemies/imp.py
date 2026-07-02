from entities.enemies.base_enemy import BaseEnemy
import assets

class Imp(BaseEnemy):

    def __init__(self, x, y):
        super().__init__("assets/sprites/imp.png", x, y, animated=True, sprites=4)

        self.damage = 20
        self.vision = 100
        # increase damage cooldown slightly so Imps hit less frequently
        self.baseCooldown = 40
        self.range = 100
        self.speed = 30

    def update(self, dt):
        try:
            super().update(dt)
        except Exception:
            pass
