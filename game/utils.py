from entities.buildings.base_building import BaseBuilding

class Utils:
    #r1 é o sprite e r2 a seleção, ambos no formato (x1, y1, x2, y2)
    def intersecta(self, r1, r2):
        ax1, ay1, ax2, ay2 = r1

        bx1, by1, bx2, by2 = r2

        return not (
            ax2 < bx1 or
            bx2 < ax1 or
            ay2 < by1 or
            by2 < ay1
        )
    
    def separate_troups(self, a, b):
            # flying units don't collide with ground troops
            if getattr(a, 'flying', False) or getattr(b, 'flying', False):
                return

            r1 = (a.x, a.y, a.x + a.sprite.width, a.y + a.sprite.height)
            r2 = (b.x, b.y, b.x + b.sprite.width, b.y + b.sprite.height)

            if self.intersecta(r1, r2):
                overlap_x = min(a.x + a.sprite.width, b.x + b.sprite.width) - max(a.x, b.x)
                overlap_y = min(a.y + a.sprite.height, b.y + b.sprite.height) - max(a.y, b.y)

                if overlap_x < overlap_y:
                    push = overlap_x / 2
                    if a.x < b.x:
                        a.x -= push
                        b.x += push
                    else:
                        a.x += push
                        b.x -= push
                else:
                    push = overlap_y / 2
                    if a.y < b.y:
                        a.y -= push
                        b.y += push
                    else:
                        a.y += push
                        b.y -= push

    def separate_building(self, building, troup):
            # flying troops should pass over buildings
            if getattr(troup, 'flying', False):
                return

            r1 = (building.x, building.y, building.x + building.sprite.width, building.y + building.sprite.height)
            r2 = (troup.x, troup.y, troup.x + troup.sprite.width, troup.y + troup.sprite.height)

            if self.intersecta(r1, r2):
                overlap_x = min(building.x + building.sprite.width, troup.x + troup.sprite.width) - max(building.x, troup.x)
                overlap_y = min(building.y + building.sprite.height, troup.y + troup.sprite.height) - max(building.y, troup.y)

                if overlap_x < overlap_y:
                    push = overlap_x / 2
                    if building.x < troup.x:
                        troup.x += push
                    else:
                        troup.x -= push
                else:
                    push = overlap_y / 2
                    if building.y < troup.y:
                        troup.y += push
                    else:
                        troup.y -= push


    
    def updateCollision(self,entities):
        entity_list = list(entities.values())

        for i in range(len(entity_list)):
            for j in range(i + 1, len(entity_list)):
                a = entity_list[i]
                b = entity_list[j]

                a_is_building = isinstance(a, BaseBuilding)
                b_is_building = isinstance(b, BaseBuilding)

                # both are non-buildings: separate troups normally
                if not a_is_building and not b_is_building:
                    self.separate_troups(a, b)
                # exactly one is a building: push only the troup away
                elif a_is_building and not b_is_building:
                    # ignore passable buildings (campfires)
                    if getattr(a, 'passable', False):
                        continue
                    self.separate_building(a, b)
                elif b_is_building and not a_is_building:
                    if getattr(b, 'passable', False):
                        continue
                    self.separate_building(b, a)
                # both are buildings: do nothing (don't move existing buildings)
                else:
                    continue

    #def collide_with(self, entity, world_x, world_y):
    #    return entity.x <= world_x <= entity.x + entity.sprite.width and \
    #        entity.y <= world_y <= entity.y + entity.sprite.height
