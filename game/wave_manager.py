import random
from entities.enemies.imp import Imp
from entities.enemies.giant import Giant
from entities.enemies.spider import Spider
from entities.enemies.ranged import Ranged

class WaveManager:
    """Manage waves (hordes) of enemies.

    Responsibilities:
    - generate wave compositions (presets + procedural)
    - schedule spawns (spawn_queue with timing)
    - detect wave completion and countdown to next wave
    - append spawned enemies into the provided EntitySystem via its `toInitialize` list
    """
    SIDES = ["top", "right", "bottom", "left"]

    def __init__(self, entity_system, spawn_points=None, inter_wave_delay=10.0, spawn_interval=0.6, presets=None, initial_wave_delay=0.0):
        self.entity_system = entity_system
        # spawn_points: list of (x,y) positions around the map (use main.py's points)
        self.spawn_points = spawn_points or [
            (100, -100),
            (1024, -100),
            (2048 + 100, -100),
            (-100, 1024),
            (1024, 2048 + 100),
            (2048 + 100, -50),
            (1024, 2048 + 100),
            (-50, 2048 + 100),
        ]

        # simple mapping from side -> indices in spawn_points
        self.side_to_indices = {
            "top": [0, 1, 2],
            "right": [2, 5],
            "bottom": [4, 6, 7],
            "left": [3, 7],
        }

        self.inter_wave_delay = inter_wave_delay
        self.spawn_interval = spawn_interval
        # extra delay before the very first wave begins (seconds)
        self.initial_wave_delay = initial_wave_delay

        self.presets = presets or {
            1: [("Imp", 3)],
            2: [("Imp", 3), ("Giant", 1)],
            3: [("Imp", 5)],
            4: [("Spider", 4), ("Imp", 4)],
            5: [("Imp", 8), ("Giant", 1)],
        }

        self.wave_index = 0
        self.state = "idle"  # idle, spawning, waiting, countdown
        self.spawn_queue = []  # list of dicts: {'time': offset, 'cls': cls, 'pos': (x,y)}
        self.spawn_timer = 0.0
        self.countdown = 0.0
        self.enemies_remaining = 0

    def start(self):
        if self.state == "idle":
            # If an initial delay is configured, start with a countdown
            if getattr(self, 'initial_wave_delay', 0) and self.initial_wave_delay > 0:
                self.countdown = self.initial_wave_delay
                self.state = 'countdown'
                # clear initial delay so subsequent waves use inter_wave_delay
                self.initial_wave_delay = 0.0
            else:
                self.start_next_wave()

    def start_next_wave(self):
        self.wave_index += 1
        entries = self.generate_wave(self.wave_index)

        # build spawn_queue with cumulative times
        t = 0.0
        queue = []
        for ent in entries:
            cls = ent.get("cls")
            count = ent.get("count", 1)
            side = ent.get("side")
            for _ in range(count):
                pos = self.pick_spawn_point(side)
                # jitter a bit so units don't stack exactly
                spawn_pos = (pos[0] + random.randint(-32, 32), pos[1] + random.randint(-32, 32))
                queue.append({"time": t, "cls": cls, "pos": spawn_pos})
                t += self.spawn_interval

        self.spawn_queue = queue
        self.spawn_timer = 0.0
        self.state = "spawning"
        self.countdown = 0.0

    def generate_wave(self, wave_index):
        """Return a list of entries {'cls':Class,'count':N,'side':side or None} in spawn order."""
        # use preset if available
        if wave_index in self.presets:
            preset = self.presets[wave_index]
            entries = []
            # preserve order in preset: weaker first, boss last
            for name, count in preset:
                entries.append({"cls": self._cls_from_name(name), "count": count, "side": None})
            return entries

        # procedural generation
        base_count = 3 + int(wave_index * 0.6)
        total_units = base_count + (wave_index // 2)
        sides_count = min(4, 1 + (wave_index - 1) // 5)
        sides = random.sample(self.SIDES, sides_count)

        per_side = total_units // sides_count
        extras = total_units % sides_count

        entries = []
        for i, side in enumerate(sides):
            cnt = per_side + (1 if i < extras else 0)
            for _ in range(cnt):
                r = random.random()
                if wave_index >= 12 and r > 0.92:
                    cls = Giant
                elif r > 0.78:
                    cls = Spider
                else:
                    cls = Imp
                entries.append({"cls": cls, "count": 1, "side": side})

        return entries

    def _cls_from_name(self, name):
        name = name.lower()
        if name == "imp":
            return Imp
        if name == "giant":
            return Giant
        if name == "spider":
            return Spider
        if name == "ranged":
            return Ranged
        # fallback
        return Imp

    def pick_spawn_point(self, side=None):
        if side is None:
            return random.choice(self.spawn_points)
        indices = self.side_to_indices.get(side, None)
        if not indices:
            return random.choice(self.spawn_points)
        idx = random.choice(indices)
        return self.spawn_points[idx]

    def update(self, dt, entities, enemies):
        # update count of known enemies (the main loop should pass the enemies dict)
        try:
            self.enemies_remaining = len(enemies)
        except Exception:
            self.enemies_remaining = 0

        if self.state == "idle":
            return

        if self.state == "spawning":
            # advance timer and spawn entries whose time <= spawn_timer
            self.spawn_timer += dt
            to_spawn = []
            while self.spawn_queue and self.spawn_queue[0]["time"] <= self.spawn_timer + 1e-6:
                to_spawn.append(self.spawn_queue.pop(0))

            for s in to_spawn:
                try:
                    obj = s["cls"](s["pos"][0], s["pos"][1])
                    self.entity_system.toInitialize.append(obj)
                except Exception:
                    pass

            # if nothing left to spawn, wait until enemies are cleared
            if not self.spawn_queue:
                self.state = "waiting"
                return

        if self.state == "waiting":
            # wait until no enemies remain
            if self.enemies_remaining == 0:
                self.countdown = self.inter_wave_delay
                self.state = "countdown"
            return

        if self.state == "countdown":
            self.countdown -= dt
            if self.countdown <= 0:
                self.start_next_wave()
