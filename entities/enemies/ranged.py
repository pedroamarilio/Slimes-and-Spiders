from entities.enemies.base_enemy import BaseEnemy
import assets

class Ranged(BaseEnemy):

    def __init__(self, x, y):
        super().__init__("assets/sprites/rangedwalking.png", x, y, animated=True, sprites=1)

        self.damage = 15

    def update(self, dt):
        try:
            super().update(dt)
        except Exception:
            pass
