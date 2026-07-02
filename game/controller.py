import time

from game import economy
from game.economy import Change
from game.economy import Economy
from game.utils import Utils
from entities.buildings.base_building import BaseBuilding
from entities.enemies.base_enemy import BaseEnemy

economy = Economy()


class Controller:
    def __init__(self, janela):
        self.janela = janela
        self.cursor = janela.get_mouse()
        self.keyboard = janela.get_keyboard()
        self.chosen_unit = "Slime"
        self.create_cooldown = 0
        self.prices = {"Slime": 50, "Necromancer": 100, "Dragon": 200, "Healer": 70, "Warrior": 30, "Archer": 30}
        self.room = {"Slime": 10, "Necromancer": 25, "Dragon": 50, "Healer": 15, "Warrior": 20, "Archer": 20}
        self.timeA = 0
        self.timeB = 0
        self.posA = (0, 0)
        self.posB = (0, 0)
        # right-click tracking for move markers
        self.rTimeA = 0
        self.rTimeB = 0
        self.rPosA = (0, 0)
        self.rPosB = (0, 0)
        self.selection_area = (0, 0, 0, 0)  # x1, y1, x2, y2
        self.utils = Utils()
        self.toPlace = None
        self.selected_building = None

    def _icon_clicked(self, mx, my, buttons):
        """Check a list of buttons for a click at (mx,my).
        `buttons` is an iterable of (name, sprite) tuples or Sprite objects.
        Returns the `name` of the clicked button (or the sprite) when clicked, else None.
        """
        for b in buttons:
            if isinstance(b, tuple) and len(b) >= 2:
                name, sprite = b[0], b[1]
            else:
                sprite = b
                name = getattr(sprite, 'name', None)

            if sprite is None:
                continue

            bx, by = sprite.x, sprite.y
            bw, bh = getattr(sprite, 'width', 0), getattr(sprite, 'height', 0)
            if bx <= mx <= bx + bw and by <= my <= by + bh and self.cursor.is_button_pressed(1):
                return name if name is not None else sprite
        return None

    def _building_menu(self, screen, screen_pos, mapa, entities):
        """Handle building menu input. Returns a Change when user places a building."""
        mx, my = screen_pos
        # hotkeys for buildings (can be used even without opening the build menu)
        if self.keyboard.key_pressed("G"):
            self.toPlace = "GoldMine"
        if self.keyboard.key_pressed("B"):
            self.toPlace = "Barracks"
        if self.keyboard.key_pressed("C"):
            self.toPlace = "Campfire"
        if self.keyboard.key_pressed("T"):
            self.toPlace = "Tower"
        if self.keyboard.key_pressed("I"):
            self.toPlace = "Incubator"

        # click on build icons (use helper to reduce duplication)
        building_buttons = []
        if hasattr(screen, 'buildgoldmine'):
            building_buttons.append(("GoldMine", screen.buildgoldmine))
        if hasattr(screen, 'buildbarracks'):
            building_buttons.append(("Barracks", screen.buildbarracks))
        if hasattr(screen, 'buildcampfire'):
            building_buttons.append(("Campfire", screen.buildcampfire))
        if hasattr(screen, 'buildtower'):
            building_buttons.append(("Tower", screen.buildtower))
        if hasattr(screen, 'buildincubator'):
            building_buttons.append(("Incubator", screen.buildincubator))

        clicked = self._icon_clicked(mx, my, building_buttons)
        if clicked:
            self.toPlace = clicked

        # attempt placement with left click when a building is selected
        if self.toPlace is not None and self.cursor.is_button_pressed(1):
            world_x = mx - mapa.x
            world_y = my - mapa.y

            # determine preview/building size based on selection
            if self.toPlace == "GoldMine" and hasattr(screen, 'buildgoldmine'):
                w = screen.buildgoldmine.width
                h = screen.buildgoldmine.height
            elif self.toPlace == "Barracks" and hasattr(screen, 'buildbarracks'):
                w = screen.buildbarracks.width
                h = screen.buildbarracks.height
            elif self.toPlace == "Campfire" and hasattr(screen, 'buildcampfire'):
                w = screen.buildcampfire.width
                h = screen.buildcampfire.height
            elif self.toPlace == "Tower" and hasattr(screen, 'buildtower'):
                w = screen.buildtower.width
                h = screen.buildtower.height
            elif self.toPlace == "Incubator" and hasattr(screen, 'buildincubator'):
                w = screen.buildincubator.width
                h = screen.buildincubator.height
            else:
                w, h = 64, 64

            pos_x = world_x - w // 2
            pos_y = world_y - h // 2

            # check no existing building overlaps the new building rect
            new_rect = (pos_x, pos_y, pos_x + w, pos_y + h)
            allowed = True
            for ent in entities.values():
                if isinstance(ent, BaseBuilding):
                    # ignore buildings marked as passable (e.g., campfire)
                    if getattr(ent, 'passable', False):
                        continue
                    ent_rect = (ent.x, ent.y, ent.x + ent.sprite.width, ent.y + ent.sprite.height)
                    if self.utils.intersecta(new_rect, ent_rect):
                        allowed = False
                        break

            if not allowed:
                # placement blocked: overlapping another building
                print("Colocação bloqueada: sobrepõe outra construção")
                return None

            # costs (building placement costs)
            costs = {
                "GoldMine": 1000,
                "Barracks": 200,
                "Campfire": 300,
                "Tower": 400,
                "Incubator": 700,
            }

            cost = costs.get(self.toPlace, 1000)
            return Change(amount=-cost, entity_string=self.toPlace, position=(pos_x, pos_y))

        return None

    def update(self, mapa, entities, units, selected_units, screen, menu_atual):
        selected_cost = self.prices[self.chosen_unit]

        change = Change(0, entity_string=None, position=None)

        screen_pos = self.cursor.get_position()
        world_x = screen_pos[0] - mapa.x  # mapa.x é negativo, então subtrai negativo = soma
        world_y = screen_pos[1] - mapa.y
        # figure out HUD top Y so clicks on HUD don't interact with world
        hud_y = None
        try:
            hud_y = getattr(screen.hud, 'y', None)
        except Exception:
            hud_y = None

        if self.keyboard.key_pressed("A"):
            self.chosen_unit = "Necromancer"
            selected_cost = self.prices[self.chosen_unit]
        elif self.keyboard.key_pressed("S"):
            self.chosen_unit = "Slime"
            selected_cost = self.prices[self.chosen_unit]
        elif self.keyboard.key_pressed("D"):
            self.chosen_unit = "Dragon"
            selected_cost = self.prices[self.chosen_unit]
        elif self.keyboard.key_pressed("F"):
            self.chosen_unit = "Healer"
            selected_cost = self.prices[self.chosen_unit]
        # SPACE creates the currently chosen unit except when it's a building-only unit
        elif self.keyboard.key_pressed("SPACE") and self.create_cooldown == 0:
            # prevent creating units that must be trained at specific buildings
            if self.chosen_unit in ("Necromancer", "Healer", "Slime", "Dragon"):
                # ignore SPACE for these units
                pass
            else:
                change = Change(amount=-selected_cost, entity_string=self.chosen_unit, position=(1024, 1024))
                self.create_cooldown = 60
        elif self.keyboard.key_pressed("B") and menu_atual == "empty":
            menu_atual = "build"


        if (self.cursor.is_button_pressed(1) and self.timeA == 0):
            # ignore clicks that start inside the HUD area
            if hud_y is None or screen_pos[1] < hud_y:
                self.timeA = time.time()
                self.posA = self.cursor.get_position()

        if (self.cursor.is_button_pressed(1) and self.timeA != 0):
            # ignore drag that happens inside HUD area
            if hud_y is None or screen_pos[1] < hud_y:
                self.timeB = time.time()
                self.posB = self.cursor.get_position()
                self.selection_area = (min(self.posA[0], self.posB[0]), min(self.posA[1], self.posB[1]), max(self.posA[0], self.posB[0]), max(self.posA[1], self.posB[1]))
                selected_units.clear()

        if (not self.cursor.is_button_pressed(1) and self.timeA != 0 and self.timeB != 0):
            # build list of entities that intersect the selection rectangle (supports enemies and units)
            selected_entities = []
            for ent in entities.values():
                try:
                    screen_x = ent.x + mapa.x
                    screen_y = ent.y + mapa.y
                    if self.utils.intersecta((screen_x, screen_y, screen_x + ent.sprite.width, screen_y + ent.sprite.height), self.selection_area):
                        selected_entities.append(ent)
                except Exception:
                    continue

            # populate selected_units with only friendly units (used for move orders)
            selected_units.clear()
            for ent in selected_entities:
                if not isinstance(ent, BaseEnemy):
                    selected_units.append(ent)

            # set `selected` flag on all entities so HUD can show the selection (includes enemies)
            for e in entities.values():
                try:
                    e.selected = (e in selected_entities)
                except Exception:
                    pass

            # clear any building selection when units are selected
            if selected_units:
                self.selected_building = None

            # reset drag timers
            self.timeA = 0
            self.timeB = 0
            self.posA = (0, 0)
            self.posB = (0, 0)
            # clear selection rectangle after applying selection
            self.selection_area = (0, 0, 0, 0)

        # Building menu handling (only when menu open)
        if menu_atual == "build":
            bchange = self._building_menu(screen, screen_pos, mapa, entities)
            if bchange is not None:
                change = bchange

        # Tower training hotkeys when tower menu is open
        if menu_atual == "tower":
            # prefer the building the player clicked (stored in self.selected_building)
            tower_entity = self.selected_building
            # fallback: find any tower in entities
            if tower_entity is None:
                for ent in entities.values():
                    if getattr(ent, 'name', None) == 'Tower':
                        tower_entity = ent
                        break

            if tower_entity is not None:
                # handle clicks on the HUD train buttons if present
                if hasattr(screen, 'train_necro') and hasattr(screen, 'train_healer'):
                    clicked = self._icon_clicked(screen_pos[0], screen_pos[1], [("Necromancer", screen.train_necro), ("Healer", screen.train_healer)])
                    if clicked == "Necromancer" and self.create_cooldown == 0:
                        # enqueue in tower's production queue (cost deducted inside train)
                        if hasattr(tower_entity, 'train'):
                            success = tower_entity.train("Necromancer", tower_entity.UNITS["Necromancer"], unit_cost=self.prices["Necromancer"])
                            if success:
                                self.create_cooldown = 30
                            else:
                                err = getattr(tower_entity, 'last_train_error', None)
                                if err == 'needs_upgrade':
                                    screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                                elif err == 'insufficient_resources':
                                    req = getattr(tower_entity, 'last_required_cost', None) or self.prices.get("Necromancer", 0)
                                    screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)
                    elif clicked == "Healer" and self.create_cooldown == 0:
                        if hasattr(tower_entity, 'train'):
                            success = tower_entity.train("Healer", tower_entity.UNITS["Healer"], unit_cost=self.prices["Healer"])
                            if success:
                                self.create_cooldown = 30
                            else:
                                err = getattr(tower_entity, 'last_train_error', None)
                                if err == 'needs_upgrade':
                                    screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                                elif err == 'insufficient_resources':
                                    req = getattr(tower_entity, 'last_required_cost', None) or self.prices.get("Healer", 0)
                                    screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)

                # upgrade button for tower
                if getattr(screen, 'upgrade', None) is not None:
                    upclicked = self._icon_clicked(screen_pos[0], screen_pos[1], [("Upgrade", screen.upgrade)])
                    if upclicked and getattr(tower_entity, 'start_upgrade', None) is not None:
                        ok = tower_entity.start_upgrade(tower_entity.upgrade_cost, tower_entity.upgrade_time)
                        if not ok:
                            if getattr(tower_entity, 'last_train_error', None) == 'insufficient_resources':
                                req = getattr(tower_entity, 'last_required_cost', tower_entity.upgrade_cost)
                                screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)

                # hotkey: U starts upgrade when in tower menu
                if self.keyboard.key_pressed("U") and getattr(tower_entity, 'start_upgrade', None) is not None:
                    ok = tower_entity.start_upgrade(tower_entity.upgrade_cost, tower_entity.upgrade_time)
                    if not ok:
                        if getattr(tower_entity, 'last_train_error', None) == 'insufficient_resources':
                            req = getattr(tower_entity, 'last_required_cost', tower_entity.upgrade_cost)
                            screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)
                    elif ok:
                        screen.set_hud_message("Upgrade iniciado", 2.0)

                # hotkeys: N -> Necromancer, H -> Healer
                if self.keyboard.key_pressed("N") and self.create_cooldown == 0:
                    if hasattr(tower_entity, 'train'):
                        success = tower_entity.train("Necromancer", tower_entity.UNITS["Necromancer"], unit_cost=self.prices["Necromancer"])
                        if success:
                            self.create_cooldown = 30
                        else:
                            err = getattr(tower_entity, 'last_train_error', None)
                            if err == 'needs_upgrade':
                                screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                            elif err == 'insufficient_resources':
                                req = getattr(tower_entity, 'last_required_cost', None) or self.prices.get("Necromancer", 0)
                                screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)
                if self.keyboard.key_pressed("H") and self.create_cooldown == 0:
                    if hasattr(tower_entity, 'train'):
                        success = tower_entity.train("Healer", tower_entity.UNITS["Healer"], unit_cost=self.prices["Healer"])
                        if success:
                            self.create_cooldown = 30
                        else:
                            err = getattr(tower_entity, 'last_train_error', None)
                            if err == 'needs_upgrade':
                                screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                            elif err == 'insufficient_resources':
                                req = getattr(tower_entity, 'last_required_cost', None) or self.prices.get("Healer", 0)
                                screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)

        # Barracks menu: train Warrior (W) and Archer (A)
        if menu_atual == "barracks":
            barracks_entity = self.selected_building
            if barracks_entity is None:
                for ent in entities.values():
                    if getattr(ent, 'name', None) == 'Barracks':
                        barracks_entity = ent
                        break

            if barracks_entity is not None:
                # handle clicks on the HUD train buttons if present
                if hasattr(screen, 'trainwarrior') and hasattr(screen, 'trainarcher'):
                    clicked = self._icon_clicked(screen_pos[0], screen_pos[1], [("Warrior", screen.trainwarrior), ("Archer", screen.trainarcher)])
                    if clicked == "Warrior" and self.create_cooldown == 0:
                        if hasattr(barracks_entity, 'train'):
                            success = barracks_entity.train("Warrior", barracks_entity.UNITS["Warrior"], unit_cost=self.prices["Warrior"])
                            if success:
                                self.create_cooldown = 30
                            else:
                                err = getattr(barracks_entity, 'last_train_error', None)
                                if err == 'needs_upgrade':
                                    screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                                elif err == 'insufficient_resources':
                                    req = getattr(barracks_entity, 'last_required_cost', None) or self.prices.get("Warrior", 0)
                                    screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)
                    elif clicked == "Archer" and self.create_cooldown == 0:
                        if hasattr(barracks_entity, 'train'):
                            success = barracks_entity.train("Archer", barracks_entity.UNITS["Archer"], unit_cost=self.prices["Archer"])
                            if success:
                                self.create_cooldown = 30
                            else:
                                err = getattr(barracks_entity, 'last_train_error', None)
                                if err == 'needs_upgrade':
                                    screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                                elif err == 'insufficient_resources':
                                    req = getattr(barracks_entity, 'last_required_cost', None) or self.prices.get("Archer", 0)
                                    screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)

                    # upgrade button for barracks
                    if getattr(screen, 'upgrade', None) is not None:
                        upclicked = self._icon_clicked(screen_pos[0], screen_pos[1], [("Upgrade", screen.upgrade)])
                        if upclicked and getattr(barracks_entity, 'start_upgrade', None) is not None:
                            ok = barracks_entity.start_upgrade(barracks_entity.upgrade_cost, barracks_entity.upgrade_time)
                            if not ok:
                                if getattr(barracks_entity, 'last_train_error', None) == 'insufficient_resources':
                                    req = getattr(barracks_entity, 'last_required_cost', barracks_entity.upgrade_cost)
                                    screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)

                    # hotkey: U starts upgrade when in barracks menu
                    if self.keyboard.key_pressed("U") and getattr(barracks_entity, 'start_upgrade', None) is not None:
                        ok = barracks_entity.start_upgrade(barracks_entity.upgrade_cost, barracks_entity.upgrade_time)
                        if not ok:
                            if getattr(barracks_entity, 'last_train_error', None) == 'insufficient_resources':
                                req = getattr(barracks_entity, 'last_required_cost', barracks_entity.upgrade_cost)
                                screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)
                        elif ok:
                            screen.set_hud_message("Upgrade iniciado", 2.0)

                # hotkeys: W -> Warrior, A -> Archer (when in barracks menu)
                if self.keyboard.key_pressed("W") and self.create_cooldown == 0:
                    if hasattr(barracks_entity, 'train'):
                        success = barracks_entity.train("Warrior", barracks_entity.UNITS["Warrior"], unit_cost=self.prices["Warrior"])
                        if success:
                            self.create_cooldown = 30
                        else:
                            err = getattr(barracks_entity, 'last_train_error', None)
                            if err == 'needs_upgrade':
                                screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                            elif err == 'insufficient_resources':
                                req = getattr(barracks_entity, 'last_required_cost', None) or self.prices.get("Warrior", 0)
                                screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)
                if self.keyboard.key_pressed("A") and self.create_cooldown == 0:
                    if hasattr(barracks_entity, 'train'):
                        success = barracks_entity.train("Archer", barracks_entity.UNITS["Archer"], unit_cost=self.prices["Archer"])
                        if success:
                            self.create_cooldown = 30
                        else:
                            err = getattr(barracks_entity, 'last_train_error', None)
                            if err == 'needs_upgrade':
                                screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                            elif err == 'insufficient_resources':
                                req = getattr(barracks_entity, 'last_required_cost', None) or self.prices.get("Archer", 0)
                                screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)

        # Incubator menu: allow training Slime (S) and Dragon (D)
        if menu_atual == "incubator":
            incubator_entity = self.selected_building
            if incubator_entity is None:
                for ent in entities.values():
                    if getattr(ent, 'name', None) == 'Incubator':
                        incubator_entity = ent
                        break

            if incubator_entity is not None:
                if hasattr(screen, 'train_slime') and hasattr(screen, 'train_dragon'):
                    clicked = self._icon_clicked(screen_pos[0], screen_pos[1], [("Slime", screen.train_slime), ("Dragon", screen.train_dragon)])
                    if clicked == "Slime" and self.create_cooldown == 0:
                        if hasattr(incubator_entity, 'train'):
                            success = incubator_entity.train("Slime", incubator_entity.UNITS["Slime"], unit_cost=self.prices["Slime"])
                            if success:
                                self.create_cooldown = 30
                            else:
                                err = getattr(incubator_entity, 'last_train_error', None)
                                if err == 'needs_upgrade':
                                    screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                                elif err == 'insufficient_resources':
                                    req = getattr(incubator_entity, 'last_required_cost', None) or self.prices.get("Slime", 0)
                                    screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)
                    elif clicked == "Dragon" and self.create_cooldown == 0:
                        if hasattr(incubator_entity, 'train'):
                            success = incubator_entity.train("Dragon", incubator_entity.UNITS["Dragon"], unit_cost=self.prices["Dragon"])
                            if success:
                                self.create_cooldown = 30
                            else:
                                err = getattr(incubator_entity, 'last_train_error', None)
                                if err == 'needs_upgrade':
                                    screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                                elif err == 'insufficient_resources':
                                    req = getattr(incubator_entity, 'last_required_cost', None) or self.prices.get("Dragon", 0)
                                    screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)

                    # upgrade button for incubator
                    if getattr(screen, 'upgrade', None) is not None:
                        upclicked = self._icon_clicked(screen_pos[0], screen_pos[1], [("Upgrade", screen.upgrade)])
                        if upclicked and getattr(incubator_entity, 'start_upgrade', None) is not None:
                            ok = incubator_entity.start_upgrade(incubator_entity.upgrade_cost, incubator_entity.upgrade_time)
                            if not ok:
                                if getattr(incubator_entity, 'last_train_error', None) == 'insufficient_resources':
                                    req = getattr(incubator_entity, 'last_required_cost', incubator_entity.upgrade_cost)
                                    screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)

                    # hotkey: U starts upgrade when in incubator menu
                    if self.keyboard.key_pressed("U") and getattr(incubator_entity, 'start_upgrade', None) is not None:
                        ok = incubator_entity.start_upgrade(incubator_entity.upgrade_cost, incubator_entity.upgrade_time)
                        if not ok:
                            if getattr(incubator_entity, 'last_train_error', None) == 'insufficient_resources':
                                req = getattr(incubator_entity, 'last_required_cost', incubator_entity.upgrade_cost)
                                screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)
                        elif ok:
                            screen.set_hud_message("Upgrade iniciado", 2.0)

                if self.keyboard.key_pressed("S") and self.create_cooldown == 0:
                    if hasattr(incubator_entity, 'train'):
                        success = incubator_entity.train("Slime", incubator_entity.UNITS["Slime"], unit_cost=self.prices["Slime"])
                        if success:
                            self.create_cooldown = 30
                        else:
                            err = getattr(incubator_entity, 'last_train_error', None)
                            if err == 'needs_upgrade':
                                screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                            elif err == 'insufficient_resources':
                                req = getattr(incubator_entity, 'last_required_cost', None) or self.prices.get("Slime", 0)
                                screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)
                if self.keyboard.key_pressed("D") and self.create_cooldown == 0:
                    if hasattr(incubator_entity, 'train'):
                        success = incubator_entity.train("Dragon", incubator_entity.UNITS["Dragon"], unit_cost=self.prices["Dragon"])
                        if success:
                            self.create_cooldown = 30
                        else:
                            err = getattr(incubator_entity, 'last_train_error', None)
                            if err == 'needs_upgrade':
                                screen.set_hud_message("Evolua a construção para invocar a criatura", 3.0)
                            elif err == 'insufficient_resources':
                                req = getattr(incubator_entity, 'last_required_cost', None) or self.prices.get("Dragon", 0)
                                screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)

        # Right-click behavior: placement has priority over unit move
        # We treat right-click press/release and only add the red marker on a click (no drag)
        try:
            # just-pressed
            if self.cursor.is_button_pressed(3) and self.rTimeA == 0:
                self.rTimeA = time.time()
                self.rPosA = self.cursor.get_position()
                # immediate unit order for responsiveness
                if self.toPlace is not None and change and change.amount < 0 and change.entity_string == "GoldMine":
                    # placement takes precedence
                    pass
                elif selected_units != []:
                    for unit in selected_units:
                        unit.destiny = (world_x, world_y)
                        unit.forced_move = True
            # held
            elif self.cursor.is_button_pressed(3) and self.rTimeA != 0:
                # update current drag pos
                self.rPosB = self.cursor.get_position()
                if selected_units != []:
                    for unit in selected_units:
                        unit.destiny = (world_x, world_y)
                        unit.forced_move = True
            # released
            elif (not self.cursor.is_button_pressed(3)) and self.rTimeA != 0:
                self.rTimeB = time.time()
                self.rPosB = self.cursor.get_position()
                # if not dragged (small movement), register a visible marker
                try:
                    dx = self.rPosB[0] - self.rPosA[0]
                    dy = self.rPosB[1] - self.rPosA[1]
                    if dx*dx + dy*dy <= 25:  # within ~5px
                        if selected_units != []:
                            try:
                                screen.add_destination_marker(world_x, world_y, duration=1.0)
                            except Exception:
                                pass
                except Exception:
                    pass
                # reset right-click trackers
                self.rTimeA = 0
                self.rTimeB = 0
                self.rPosA = (0, 0)
                self.rPosB = (0, 0)
        except Exception:
            pass

        # toggle hud menu when clicking the build button (use helper)
        if hasattr(screen, 'buildbutton'):
            clicked_build = self._icon_clicked(screen_pos[0], screen_pos[1], [("build", screen.buildbutton)])
            if clicked_build:
                menu_atual = "build"
                # clear any selected building when opening build menu
                self.selected_building = None

        # click on existing buildings to open their specific menu (e.g., Tower)
        if self.cursor.is_button_pressed(1):
            # do not interpret clicks on the HUD area as world clicks
            if hud_y is None or screen_pos[1] < hud_y:
                # translate screen pos to world coords
                wx, wy = world_x, world_y
                for ent in entities.values():
                    # building sprites have width/height
                    try:
                        bw, bh = ent.sprite.width, ent.sprite.height
                    except Exception:
                        continue
                    if ent.x <= wx <= ent.x + bw and ent.y <= wy <= ent.y + bh:
                        ent_name = getattr(ent, 'name', None)
                        # building-specific menus
                        if ent_name == 'Tower':
                            menu_atual = 'tower'
                            # mark this building as selected so training anchors to it
                            self.selected_building = ent
                            # mark selection flag on entities (clear others)
                            for e in entities.values():
                                try:
                                    e.selected = (e is ent)
                                except Exception:
                                    pass
                            # clear unit selection list
                            selected_units.clear()
                            break
                        elif ent_name == 'Incubator':
                            menu_atual = 'incubator'
                            self.selected_building = ent
                            for e in entities.values():
                                try:
                                    e.selected = (e is ent)
                                except Exception:
                                    pass
                            selected_units.clear()
                            break
                        elif ent_name == 'Barracks':
                            menu_atual = 'barracks'
                            self.selected_building = ent
                            for e in entities.values():
                                try:
                                    e.selected = (e is ent)
                                except Exception:
                                    pass
                            selected_units.clear()
                            break
                        else:
                            # clicked on a non-building entity (unit) -> select it
                            selected_units.clear()
                            selected_units.append(ent)
                            self.selected_building = None
                            for e in entities.values():
                                try:
                                    e.selected = (e is ent)
                                except Exception:
                                    pass
                            break
            else:
                # click was on HUD area — ignore world selection
                pass

        if self.keyboard.key_pressed("ESCAPE"):
            menu_atual = "empty"
            self.toPlace = None

        elif self.create_cooldown > 0:
            self.create_cooldown -= 1

        return change, self.selection_area, menu_atual

        