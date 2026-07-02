from entities.units.healer import Healer
from entities.enemies.base_enemy import BaseEnemy
from entities.units.base_unit import BaseUnit
from entities.buildings.base_building import BaseBuilding

class CombatSystem:
    def __init__(self):
        pass

    def dealDamage(self, attacker, receiver):
        attacker.resetCooldown()
        # prefer using receiver.take_damage if available (buildings)
        try:
            if hasattr(receiver, 'take_damage'):
                receiver.take_damage(attacker.damage)
            else:
                receiver.hp -= attacker.damage
        except Exception:
            try:
                receiver.hp -= attacker.damage
            except Exception:
                pass

    def dealHeal(self, healer, unit):
        # single-target heal (keeps existing behavior)
        unit.hp += healer.healing


    def verifyCombat(self, unit1, unit2):
        # allow enemy vs unit and enemy vs building combat
        pos1 = isinstance(unit1, BaseEnemy) and (isinstance(unit2, BaseUnit) or isinstance(unit2, BaseBuilding))
        pos2 = isinstance(unit2, BaseEnemy) and (isinstance(unit1, BaseUnit) or isinstance(unit1, BaseBuilding))
        return pos1 or pos2
    
    def inRange(self, unit1, unit2):
        # centro de unit1
        c1x = unit1.x + unit1.sprite.width / 2
        c1y = unit1.y + unit1.sprite.height / 2

        # borda mais próxima da hitbox de unit2 ao centro de unit1
        closest_x = max(unit2.x, min(c1x, unit2.x + unit2.sprite.width))
        closest_y = max(unit2.y, min(c1y, unit2.y + unit2.sprite.height))

        distance = ((c1x - closest_x)**2 + (c1y - closest_y)**2)**0.5

        if distance <= unit1.range:
            if not isinstance(unit1, Healer):
                # marque a unidade como em ataque e não force movimento em direção ao inimigo
                unit1.inAttack = True
                return True
            else:
                unit1.inAttack = False
                return False
        else:
            # quando fora de alcance, garantir que não esteja em ataque
            unit1.inAttack = False
            if isinstance(unit1, BaseEnemy):
                unit1.destiny = (1024, 1024)
            return False
    
    def combatSequence(self, unit1, unit2):
        if(self.verifyCombat(unit1, unit2)):
            if getattr(unit1, 'cooldown', 1) <= 0 and self.inRange(unit1, unit2):
                try:
                    print(f"HP1: {unit2.hp}")
                except Exception:
                    pass
                self.dealDamage(unit1, unit2)
                try:
                    print(f"HP2: {unit2.hp}")
                    print(f"{unit1.id} deu {unit1.damage} de dano em {unit2.id})")
                except Exception:
                    pass

            # only attempt counter-attack if the target has a cooldown (i.e., can attack)
            if hasattr(unit2, 'cooldown') and getattr(unit2, 'cooldown', 1) <= 0 and self.inRange(unit2, unit1):
                try:
                    print(f"HP1: {unit1.hp}")
                except Exception:
                    pass
                self.dealDamage(unit2, unit1)
                try:
                    print(f"HP2: {unit1.hp}")
                    print(f"{unit2.id} deu {unit2.damage} de dano em {unit1.id})")
                except Exception:
                    pass
    
    def healingSequence(self, healer, unit):
        if(healer.cooldown <= 0 and self.inRange(healer, unit)):
                # keep single-target fallback if used elsewhere
                self.dealHeal(healer, unit)

    def areaHeal(self, healer, units_list):
        """Heal all friendly units within healer.range once, then apply cooldown."""
        if healer.cooldown > 0:
            return

        healed_any = False
        for unit in units_list:
            try:
                if unit is healer:
                    continue
                # compute distance from healer center to closest point on unit hitbox
                c1x = healer.x + healer.sprite.width / 2
                c1y = healer.y + healer.sprite.height / 2
                closest_x = max(unit.x, min(c1x, unit.x + unit.sprite.width))
                closest_y = max(unit.y, min(c1y, unit.y + unit.sprite.height))
                distance = ((c1x - closest_x)**2 + (c1y - closest_y)**2)**0.5
                if distance <= healer.range:
                    unit.hp = min(getattr(unit, 'max_hp', unit.hp), unit.hp + healer.healing)
                    healed_any = True
            except Exception:
                continue

        if healed_any:
            healer.resetCooldown()