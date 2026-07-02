from entities.enemies.base_enemy import BaseEnemy
from entities.units.healer import Healer

from systems.combat_system import CombatSystem

class AI_Controller:
    def __init__(self):
        pass

    def inVision(self, unit1, unit2):
        # if unit has been ordered (forced_move), don't override its destiny
        if getattr(unit1, 'forced_move', False):
            return

        # center of unit1
        c1x = unit1.x + unit1.sprite.width / 2
        c1y = unit1.y + unit1.sprite.height / 2

        # center of unit2
        c2x = unit2.x + unit2.sprite.width / 2
        c2y = unit2.y + unit2.sprite.height / 2

        dx = c1x - c2x
        dy = c1y - c2y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance <= unit1.vision:
            # special handling for healers: approach to a safe distance and stop when in range
            if isinstance(unit1, Healer):
                # desired minimum gap to avoid overlapping (half widths + margin)
                margin = (unit1.sprite.width + unit2.sprite.width) / 2 + 4
                desired_distance = min(unit1.range, max(margin, 16))
                if distance <= unit1.range:
                    # already in healing range; stop moving
                    unit1.destiny = (0, 0)
                else:
                    # move to a point on the line from target to healer at desired_distance
                    if distance == 0:
                        dest_cx = c2x + desired_distance
                        dest_cy = c2y
                    else:
                        ux = dx / distance
                        uy = dy / distance
                        dest_cx = c2x + ux * desired_distance
                        dest_cy = c2y + uy * desired_distance
                    unit1.destiny = (dest_cx, dest_cy)
            else:
                unit1.destiny = (c2x, c2y)
        elif isinstance(unit1, BaseEnemy):
            unit1.destiny = (1024, 1024)

    def updateDestiny(self, units, enemies, buildings):
        units_list = list(units.values())
        healer_list = [item for item in units_list if isinstance(item, Healer)]
        enemies_list = list(enemies.values())
        buildings_list = list(buildings.values())
        combat_system = CombatSystem()

        # reset per-frame state so units don't remain 'inAttack' after targets die
        for u in units_list:
            try:
                if not getattr(u, 'forced_move', False):
                    u.destiny = (0, 0)
                u.inAttack = False
            except Exception:
                pass
        for e in enemies_list:
            try:
                e.inAttack = False
            except Exception:
                pass

        for i in range(len(units_list)):
            for j in range(len(enemies_list)):
                if not isinstance(units_list[i], Healer):
                    self.inVision(units_list[i], enemies_list[j])
                self.inVision(enemies_list[j], units_list[i])

                combat_system.combatSequence(units_list[i], enemies_list[j])

        # Enemies should also seek and attack buildings
        for e in enemies_list:
            for b in buildings_list:
                try:
                    # enemy sees building and will move toward it
                    self.inVision(e, b)
                    # resolve combat enemy vs building
                    combat_system.combatSequence(e, b)
                except Exception:
                    continue

        # Healers: update vision toward friendly units then perform area heal
        for healer in healer_list:
            for unit in units_list:
                if healer != unit:
                    self.inVision(healer, unit)
            # after updating movement/intents, heal all allies in range once per cooldown
            combat_system.areaHeal(healer, units_list)
