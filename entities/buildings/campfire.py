from entities.buildings.base_building import BaseBuilding


class Campfire(BaseBuilding):
    def __init__(self, x=1024, y=1024, economy=None):
        super().__init__(x, y, 200, "assets/sprites/campfire.png", animated=True, sprites=3)
        self.exists = True
        # mark campfire as passable so it doesn't block placement or push units
        self.passable = True
        self.economy = economy
        if self.economy is not None:
            try:
                self.economy.campfires += 1
            except Exception:
                pass

    def on_destroyed(self):
        if getattr(self, 'economy', None) is not None:
            try:
                self.economy.campfires = max(0, self.economy.campfires - 1)
            except Exception:
                pass

    # placeholder effect (e.g., healing aura)
    def emit_aura(self):
        pass
