from entities.enemies.base_enemy import BaseEnemy
import assets

class Spider(BaseEnemy):

    def __init__(self, x, y):
        super().__init__("assets/sprites/spider.png", x, y, animated=True, sprites=6)

        # Parameters updated per user request
        self.damage = 20
        self.vision = 90
        # baseCooldown measured in frame-ticks (~60 ticks = 1s)
        self.baseCooldown = 50
        self.range = 110
        self.speed = 60

    def update(self, dt):
        try:
            super().update(dt)
        except Exception:
            pass
