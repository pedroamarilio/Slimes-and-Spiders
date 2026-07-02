from entities.enemies.base_enemy import BaseEnemy
import assets

class Giant(BaseEnemy):

    def __init__(self, x, y):
        super().__init__("assets/sprites/giant.png", x, y, animated=True, sprites=5)

        # Parameters updated per user request
        self.damage = 50
        self.vision = 130
        # baseCooldown measured in frame-ticks (~60 ticks = 1s)
        # reduced per user request to make Giant attack more often
        self.baseCooldown = 50
        # increase attack range so Giant can hit from further away
        self.range = 200
        self.speed = 10

    def update(self, dt):
        try:
            super().update(dt)
        except Exception:
            pass
