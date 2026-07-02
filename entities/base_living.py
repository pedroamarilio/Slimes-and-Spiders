from entities.base_entity import BaseEntity

class BaseLiving(BaseEntity):
    def __init__(self, imagem, x, y, animated=False, sprites=1):
        super().__init__(imagem, x, y, animated, sprites)
        self.alive = True
        self.isWalking = False

        self.vision = 70
        self.damage = 20
        self.cost = 70
        self.destiny = (0, 0)
        self.range = 100
        # baseCooldown measured in frame-ticks (~60 ticks = 1s)
        self.baseCooldown = 60
        self.cooldown = 0
        self.inAttack = False

    def update(self, dt):
        # decrement attack/heal cooldown measured in frames (approx using dt)
        try:
            if getattr(self, 'cooldown', 0) > 0:
                # convert dt (seconds) to approximate frame ticks (assuming 60 FPS baseline)
                ticks = max(1, int(round(dt * 60)))
                self.cooldown -= ticks
                if self.cooldown < 0:
                    self.cooldown = 0
        except Exception:
            pass

    def resetCooldown(self):
        self.cooldown = self.baseCooldown
