
from game.economy import Change
from entities.base_entity import BaseEntity
from PPlay.sprite import Sprite
class BaseBuilding(BaseEntity):
    def __init__(self, x, y, hp, imagem, animated=False, sprites=1):
        # allow buildings to specify whether they're animated and how many frames
        super().__init__(imagem, x, y, animated=animated, sprites=sprites)
        self.hp = hp
        self.max_hp = hp
        self.is_alive = True

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.is_alive = False
            self.on_destroyed()



    
class ProductionBuilding(BaseBuilding):
    def __init__(self, name, hp, position, production_cost, economy, id, image=None, animated=False, sprites=1):
        # choose a sensible default image based on the building name
        if image is None:
            default_images = {
                "Barracks": "assets/sprites/barracks.png",
            }
            image = default_images.get(name, "assets/sprites/buildbarracks.png")

        super().__init__(position[0], position[1], hp, image, animated=animated, sprites=sprites)
        self.position = position
        self.name = name
        self.production_cost = production_cost  # custo em recursos por tropa
        self.economy = economy                  # referência à Economy
        # fila de treino: [(unit_type, time_left, total_time), ...]
        self.queue = []
        self.max_queue = 5
        self.is_producing = False
        self.id = id
        self.spawn_blocked = False
        # upgrade system
        self.level = 1
        self.upgrade_in_progress = False
        self.upgrade_time_remaining = 0.0
        self.upgrade_target_level = None
        # last training error code for UI feedback
        self.last_train_error = None
        # last required cost recorded when a spend was denied
        self.last_required_cost = None


    # ── Fila de produção ──────────────────────────────────────────────

    def train(self, unit_type, build_time, unit_cost=None):
        """Tenta enfileirar uma tropa. Retorna True se aprovado.

        `unit_cost` if provided overrides the building's `production_cost`.
        """
        # reset last error
        self.last_train_error = None

        if len(self.queue) >= self.max_queue:
            print("Fila cheia!")
            return False

        # check unit-level requirements (e.g., Archer requires Barracks level 2)
        min_levels = getattr(self, 'MIN_LEVEL', {})
        required_level = min_levels.get(unit_type, 1)
        if self.level < required_level:
            self.last_train_error = 'needs_upgrade'
            print(f"Cannot train {unit_type}: building level {self.level} < required {required_level}")
            return False

        cost = unit_cost if unit_cost is not None else self.production_cost

        approved = {}
        # Create Change using the correct constructor signature: (amount, entity_string, position)
        change = Change(-cost, unit_type, self.position)
        # attempt to spend resources immediately
        self.economy.update([change], approved)
        if approved.get(change.id):
            # store total time as well so HUD can show remaining vs total
            self.queue.append([unit_type, build_time, build_time])
            self.is_producing = True
            print(f"{unit_type} enfileirado em {self.name}")
            return True

        # Insufficient resources
        self.last_train_error = 'insufficient_resources'
        # record required cost for UI
        try:
            self.last_required_cost = int(cost)
        except Exception:
            self.last_required_cost = cost
        print("Recursos insuficientes!")
        return False

    def cancel_last(self):
        """Cancela o último item da fila e devolve metade do custo."""
        if self.queue:
            self.queue.pop()
            refund = self.production_cost // 2
            self.economy.add_resources(refund)
            self.is_producing = bool(self.queue)

    def update(self, dt):
        """Avança o timer da tropa em treinamento.

        Nota: não remove automaticamente a tropa quando pronta; ela ficará
        com tempo restante = 0 até que o sistema principal consiga spawná-la
        (verificação de espaço)."""
        # handle building upgrade timer first so upgrades progress even when queue is empty
        if self.upgrade_in_progress:
            self.upgrade_time_remaining -= dt
            if self.upgrade_time_remaining <= 0:
                # complete upgrade
                try:
                    self.level = self.upgrade_target_level or (self.level + 1)
                except Exception:
                    self.level += 1
                self.upgrade_in_progress = False
                self.upgrade_time_remaining = 0.0
                self.upgrade_target_level = None

        if not self.queue:
            self.is_producing = False
            self.spawn_blocked = False
            return

        # decrementa apenas o tempo da tropa atual (se ainda > 0)
        if self.queue[0][1] > 0:
            self.queue[0][1] -= dt
            if self.queue[0][1] < 0:
                self.queue[0][1] = 0

        self.is_producing = bool(self.queue)

    def on_unit_ready(self, unit_type):
        """Hook chamado quando uma tropa termina de treinar.

        Hoje não é usado diretamente — o sistema principal consulta `queue`
        e chama `pop_ready()` quando for hora de spawnar a tropa.
        """
        print(f"{unit_type} pronto! (building {self.name})")

    # ── HUD ──────────────────────────────────────────────────────────

    def get_menu_buttons(self):
        """Sobrescreve BaseBuilding — retorna botões específicos de produção."""
        return [
            {"label": "Cancelar último", "action": self.cancel_last},
        ]

    def get_queue_progress(self):
        """Retorna (unit_type, time_left, total_time) da tropa atual, ou None."""
        if not self.queue:
            return None
        unit_type, time_left, total_time = self.queue[0]
        return unit_type, time_left, total_time

    def pop_ready(self):
        """Remove e retorna a tropa pronta do início da fila (se houver)."""
        if not self.queue:
            return None
        unit_type, time_left, total_time = self.queue[0]
        if time_left <= 0:
            self.queue.pop(0)
            self.is_producing = bool(self.queue)
            self.spawn_blocked = False
            return unit_type
        return None

    # Upgrade support
    def start_upgrade(self, cost, time_seconds):
        """Begin an upgrade if possible. Returns True if started."""
        # reset last error
        self.last_train_error = None

        if self.upgrade_in_progress:
            self.last_train_error = 'upgrade_in_progress'
            return False

        # simple max level guard (default 2)
        max_level = getattr(self, 'max_level', 2)
        if self.level >= max_level:
            self.last_train_error = 'max_level'
            return False

        approved = {}
        change = Change(-cost, None, self.position)
        # attempt to spend resources immediately
        self.economy.update([change], approved)

        if approved.get(change.id):
            self.upgrade_in_progress = True
            self.upgrade_time_remaining = time_seconds
            self.upgrade_target_level = self.level + 1
            return True

        self.last_train_error = 'insufficient_resources'
        try:
            self.last_required_cost = int(cost)
        except Exception:
            self.last_required_cost = cost
        return False
