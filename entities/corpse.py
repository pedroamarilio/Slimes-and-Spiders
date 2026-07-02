from entities.base_entity import BaseEntity

class Corpse(BaseEntity):
    def __init__(self, original_class, x, y, original_entity=None, lifetime=30):
        # bones.png is a static sprite (no animation frames)
        super().__init__("assets/sprites/bones.png", x, y, animated=False, sprites=1)

        # mark as corpse so systems can detect it
        self.is_corpse = True
        # default attributes to avoid attribute errors when iterating entities
        self.vision = 0
        # default combat/movement flags
        self.inAttack = False
        self.forced_move = False
        # reference to the class to re-instantiate when resurrected (e.g., Archer, Melee)
        self.original_class = original_class
        # optionally keep some info about the original entity
        self.original_entity = original_entity
        # seconds remaining before the corpse despawns
        self.lifetime = lifetime
        # has been marked to resurrect by a necromancer
        self.resurrected = False
        # prevent collision by marking as 'flying' (utils checks this)
        self.flying = True
        # flag to avoid multiple respawns
        self._res_spawned = False

    def update(self, dt):
        try:
            # decrement lifetime
            self.lifetime -= dt
            if self.lifetime <= 0:
                # signal removal by setting hp to 0
                self.hp = 0
            # if already been flagged to resurrect, we'll let EntitySystem handle actual spawning
        except Exception:
            pass
