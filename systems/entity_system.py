from PPlay.animation import Animation

from game.economy import Economy
from game.controller import Controller

from entities.base_entity import BaseEntity
from entities.enemies.base_enemy import BaseEnemy
from entities.units.slime import Slime
from entities.units.minislime import MiniSlime
from entities.buildings.base_building import BaseBuilding
from entities.corpse import Corpse
from entities.units.necromancer import Necromancer

class EntitySystem:
    def __init__(self):
        self.toInitialize = []
        self.entity_id = 0
        self._dt = 1/60

    def initialize(self, entities, units, enemies, buildings):
        if self.toInitialize != []:
            for curr_ent in self.toInitialize:
                curr_ent.id = self.entity_id
                self.entity_id += 1

                entities[curr_ent.id] = curr_ent

                # Corpses are stored only in the global entities dict (no collision, no AI targeting)
                if isinstance(curr_ent, Corpse):
                    pass
                elif isinstance(curr_ent, BaseBuilding):
                    buildings[curr_ent.id] = curr_ent
                elif not isinstance(curr_ent, BaseEnemy) and isinstance(curr_ent, BaseEntity):
                    units[curr_ent.id] = curr_ent
                else:
                    enemies[curr_ent.id] = curr_ent

                if isinstance(curr_ent.sprite, Animation):
                  curr_ent.sprite.play()  

            self.toInitialize.clear()
        

    def update(self, entities, units, enemies, buildings, controller=None, economy=None):
        toRemove = []

        for entity in list(entities.values()):
            # HP check
            try:
                hp_val = getattr(entity, 'hp', None)
                if hp_val is not None and hp_val <= 0:
                    # create a corpse for allied units (non-buildings, non-enemies, non-corpse)
                    try:
                        # create corpse for allied units except for the parent Slime
                        if not isinstance(entity, BaseBuilding) and not isinstance(entity, BaseEnemy) and not isinstance(entity, Corpse) and not isinstance(entity, Slime):
                            corpse = Corpse(entity.__class__, entity.x, entity.y, original_entity=entity)
                            self.toInitialize.append(corpse)
                    except Exception:
                        pass

                    # decrement army usage if economy and controller were provided
                    try:
                        if economy is not None and controller is not None:
                            # only adjust for friendly units (not buildings, not enemies, not corpses)
                            if not isinstance(entity, BaseBuilding) and not isinstance(entity, BaseEnemy) and not isinstance(entity, Corpse):
                                unit_name = getattr(entity, 'name', entity.__class__.__name__)
                                try:
                                    dec = controller.room.get(unit_name, 0)
                                    if isinstance(dec, int) and dec > 0:
                                        economy.army = max(0, economy.army - dec)
                                except Exception:
                                    pass
                    except Exception:
                        pass

                    toRemove.append(entity.id)
                    continue
            except Exception:
                pass

            # call entity-specific update if present
            if hasattr(entity, 'update'):
                try:
                    entity.update(self._dt)
                except TypeError:
                    try:
                        entity.update()
                    except Exception:
                        pass

        for id in toRemove:
            if isinstance(entities[id], Slime):
                ms1 = MiniSlime(entities[id].x, entities[id].y)
                ms2 = MiniSlime(entities[id].x, entities[id].y)
                ms3 = MiniSlime(entities[id].x, entities[id].y)
                ms4 = MiniSlime(entities[id].x, entities[id].y)
                self.toInitialize.append(ms1)
                self.toInitialize.append(ms2)
                self.toInitialize.append(ms3)
                self.toInitialize.append(ms4)

            entities.pop(id)
            units.pop(id, None)
            enemies.pop(id, None)
            try:
                buildings.pop(id, None)
            except Exception:
                pass

        # Necromancer resurrection pass: necromancers can resurrect nearby corpses if their cooldown is 0
        try:
            necromancers = [e for e in list(entities.values()) if isinstance(e, Necromancer)]
            corpses = [e for e in list(entities.values()) if getattr(e, 'is_corpse', False)]

            for nec in necromancers:
                try:
                    if getattr(nec, 'cooldown', 0) <= 0:
                        for corpse in corpses:
                            if corpse.resurrected:
                                continue
                            # simple distance check (center to center)
                            dx = (nec.x + nec.sprite.width/2) - (corpse.x + corpse.sprite.width/2)
                            dy = (nec.y + nec.sprite.height/2) - (corpse.y + corpse.sprite.height/2)
                            dist2 = dx*dx + dy*dy
                            if dist2 <= (nec.range * nec.range):
                                # mark to resurrect and reset necromancer cooldown
                                corpse.resurrected = True
                                try:
                                    nec.resetCooldown()
                                except Exception:
                                    nec.cooldown = nec.baseCooldown
                                break
                except Exception:
                    pass
        except Exception:
            pass

        # Process corpses that have been marked for resurrection: spawn unit and remove corpse
        try:
            for entity in list(entities.values()):
                if getattr(entity, 'is_corpse', False) and getattr(entity, 'resurrected', False) and not getattr(entity, '_res_spawned', False):
                    try:
                        # instantiate the original unit class at corpse position
                        new_unit = entity.original_class(entity.x, entity.y)
                        self.toInitialize.append(new_unit)
                    except Exception:
                        pass
                    # mark spawned and schedule corpse removal
                    entity._res_spawned = True
                    entity.hp = 0
        except Exception:
            pass