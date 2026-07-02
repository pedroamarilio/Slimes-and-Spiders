from entities.buildings.base_building import BaseBuilding


class Movement:
    def __init__(self):
        pass

    def update(self, entities, dt):
        # filtra entidades que não são construções antes de iterar
        filtered_entities = [e for e in entities.values() if not isinstance(e, BaseBuilding)]

        for entity in filtered_entities:
            if not hasattr(entity, 'destiny') or entity.destiny == (0, 0):
                entity.isWalking = False
                # clear forced move when there's no destiny
                if hasattr(entity, 'forced_move'):
                    entity.forced_move = False
                continue

            # se a entidade estiver em ataque, só permita movimento se foi forçada (ex: ordenada ou empurrada)
            if entity.inAttack and not getattr(entity, 'forced_move', False):
                continue

            entity.isWalking = True
            direction_x = entity.destiny[0] - (entity.x + entity.sprite.width / 2)
            direction_y = entity.destiny[1] - (entity.y + entity.sprite.height / 2)
            distance = (direction_x ** 2 + direction_y ** 2) ** 0.5
            speed = entity.speed
            step = speed * dt

            # update facing based on movement direction
            try:
                if direction_x < 0:
                    entity.facing = -1
                else:
                    entity.facing = 1
                try:
                    # inform sprite about flip state if supported
                    entity.sprite.flip_x = (entity.facing == -1)
                except Exception:
                    pass
            except Exception:
                pass

            if distance <= step + 20:
                entity.x = entity.destiny[0] - entity.sprite.width / 2
                entity.y = entity.destiny[1] - entity.sprite.height / 2
                entity.destiny = (0, 0)
                # ao alcançar o destino, limpa o forced_move
                if hasattr(entity, 'forced_move'):
                    entity.forced_move = False
            else:
                print(f"Unit {entity.id} moving to {entity.destiny}, current position: ({entity.x}, {entity.y}), delta: ({direction_x}, {direction_y}), distance: {distance}, step: {step}, dt: {dt}")
                entity.x += (direction_x / distance) * step
                entity.y += (direction_y / distance) * step
                print(f"Unit {entity.id} moving to {entity.destiny}, current position: ({entity.x}, {entity.y})")