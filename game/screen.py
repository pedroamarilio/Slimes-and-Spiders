from PPlay.window import Window
import pygame
from PPlay.animation import Animation
from PPlay.sprite import Sprite
from game import economy
from ui import hud
from entities.buildings.base_building import BaseBuilding
from entities.units.necromancer import Necromancer


class Screen:
    def __init__(self, janela, musica, cursor, mapa, seta, hud, buildbutton, buildbarracks, buildcampfire, buildgoldmine, buildtower, buildincubator, menu_atual, keyboard):
        self.janela = janela
        self.musica = musica
        self.cursor = cursor
        self.mapa = mapa
        self.seta = seta
        self.hud = hud
        self.buildbutton = buildbutton
        self.buildbarracks = buildbarracks
        self.buildcampfire = buildcampfire
        self.buildgoldmine = buildgoldmine
        self.buildtower = buildtower
        self.buildincubator = buildincubator
        self.menu_atual = menu_atual
        self.keyboard = janela.get_keyboard()
        # pre-create tower train button sprites so controller can detect clicks
        try:
            self.train_necro = Sprite('assets/sprites/trainnecromancer.png', 1)
            self.train_necro.set_position(1100, 520)
        except Exception:
            self.train_necro = None
        try:
            self.train_healer = Sprite('assets/sprites/trainhealer.png', 1)
            self.train_healer.set_position(1170, 520)
        except Exception:
            self.train_healer = None
        # incubator training buttons (use unit sprites as icons)
        try:
            self.train_slime = Sprite('assets/sprites/trainslime.png', 1)
            self.train_slime.set_position(1100, 520)
        except Exception:
            self.train_slime = None
        try:
            self.train_dragon = Sprite('assets/sprites/traindragon.png', 1)
            self.train_dragon.set_position(1170, 520)
        except Exception:
            self.train_dragon = None
        # upgrade button sprite (shared across building menus)
        try:
            self.upgrade = Sprite('assets/sprites/upgrade.png', 1)
            self.upgrade.set_position(1240, 520)
        except Exception:
            self.upgrade = None
        # HUD message state
        self.hud_message = None
        self.hud_message_time = 0.0
        # destination markers for right-click move (list of dicts {'x','y','time'})
        self.destination_markers = []
        # barracks training buttons
        try:
            self.trainwarrior = Sprite('assets/sprites/trainwarrior.png', 1)
            self.trainwarrior.set_position(1100, 520)
        except Exception:
            self.trainwarrior = None
        try:
            self.trainarcher = Sprite('assets/sprites/trainarcher.png', 1)
            self.trainarcher.set_position(1170, 520)
        except Exception:
            self.trainarcher = None

    def inScreen(self, mx1, my1, mx2, my2, x, y):
        if x > mx1 and x < mx2 and y > my1 and y < my2:
            return True
        return False

    def update(self, economy, entities, selection_area, dt, menu_atual, toPlace=None, wave_manager=None, present=True):
        #self.musica.play()
        self.janela.set_background_color((0,0,0))
        self.seta.x, self.seta.y = self.cursor.get_position()

        toDraw = []

        for entity in entities.values():
            screen_x = entity.x + self.mapa.x
            screen_y = entity.y + self.mapa.y
            margem = 200
            if self.inScreen(0 - margem, 0 - margem, 1366 + margem, 768 + margem, screen_x, screen_y): #Adicionei uma margem de 50 pixels para evitar que as unidades desapareçam quando estão na borda da tela
                toDraw.append(entity)

        if self.seta.x > 1316 and self.mapa.x > -650:
            self.mapa.set_position(self.mapa.x - 4, self.mapa.y)
        if self.seta.x < 50 and self.mapa.x < 0:
            self.mapa.set_position(self.mapa.x + 4, self.mapa.y)
        if self.seta.y < 50  and self.mapa.y < 0:
            self.mapa.set_position(self.mapa.x, self.mapa.y + 4)
        if self.seta.y > 718  and self.mapa.y > -1280:
            self.mapa.set_position(self.mapa.x, self.mapa.y - 4)

        self.mapa.draw()

        # Draw in explicit layers so flying units render above buildings/ground.
        buildings = []
        corpses = []
        ground_units = []
        flying_units = []
        for entity in toDraw:
            if getattr(entity, 'flying', False):
                flying_units.append(entity)
            elif isinstance(entity, BaseBuilding):
                buildings.append(entity)
            elif getattr(entity, 'is_corpse', False):
                corpses.append(entity)
            else:
                ground_units.append(entity)

        # draw helper
        def _draw_entities(list_entities):
            for entity in list_entities:
                screen_x = entity.x + self.mapa.x
                screen_y = entity.y + self.mapa.y
                entity.sprite.set_position(screen_x, screen_y)
                if(not isinstance(entity.sprite, Sprite)):
                    # update animation if unit is walking or it's a building (buildings animate constantly)
                    if getattr(entity, 'isWalking', False) or isinstance(entity, BaseBuilding):
                        try:
                            # ensure animation is playing before updating (fixes paused animations)
                            try:
                                entity.sprite.play()
                            except Exception:
                                pass
                            entity.sprite.update()
                        except Exception:
                            pass
                    else:
                        entity.sprite.set_curr_frame(0)
                        try:
                            entity.sprite.pause()
                        except Exception:
                            pass
                entity.sprite.draw()

        # buildings, corpses, ground units, then flying on top
        _draw_entities(buildings)
        _draw_entities(corpses)
        _draw_entities(ground_units)
        _draw_entities(flying_units)

        # placement preview: draw before HUD so HUD stays visually on top
        self.draw_placement_preview(toPlace, (self.seta.x, self.seta.y), self.mapa)

        # draw selection rectangle (screen coords in selection_area)
        try:
            # draw only while left mouse button is held to avoid persistent rectangle
            if selection_area and selection_area != (0, 0, 0, 0) and self.cursor.is_button_pressed(1):
                sx1, sy1, sx2, sy2 = selection_area
                left = int(min(sx1, sx2))
                top = int(min(sy1, sy2))
                width = int(abs(sx2 - sx1))
                height = int(abs(sy2 - sy1))
                # outline
                try:
                    pygame.draw.rect(Window.get_screen(), (0, 200, 200), (left, top, width, height), 1)
                except Exception:
                    pass
        except Exception:
            pass

        # draw destination markers (world coords stored) — small red squares
        try:
            for m in list(self.destination_markers):
                try:
                    m['time'] -= dt
                    sx = int(m['x'] + self.mapa.x)
                    sy = int(m['y'] + self.mapa.y)
                    size = 6
                    rect = (sx - size//2, sy - size//2, size, size)
                    try:
                        pygame.draw.rect(Window.get_screen(), (220, 40, 40), rect)
                    except Exception:
                        pass
                    if m['time'] <= 0:
                        self.destination_markers.remove(m)
                except Exception:
                    try:
                        self.destination_markers.remove(m)
                    except Exception:
                        pass
        except Exception:
            pass

        # draw HUD and buttons according to current menu state
        self.drawHUD(menu_atual)

        if menu_atual == "barracks":
            self.trainwarrior.draw()
            self.trainarcher.draw()
            if getattr(self, 'upgrade', None) is not None:
                try:
                    self.upgrade.draw()
                except Exception:
                    pass
        if menu_atual == "tower":
            if getattr(self, 'train_necro', None) is not None:
                try:
                    self.train_necro.draw()
                except Exception:
                    pass
            if getattr(self, 'train_healer', None) is not None:
                try:
                    self.train_healer.draw()
                except Exception:
                    pass
            if getattr(self, 'upgrade', None) is not None:
                try:
                    self.upgrade.draw()
                except Exception:
                    pass
        if menu_atual == "incubator":
            if getattr(self, 'train_slime', None) is not None:
                try:
                    self.train_slime.draw()
                except Exception:
                    pass
            if getattr(self, 'train_dragon', None) is not None:
                try:
                    self.train_dragon.draw()
                except Exception:
                    pass
            if getattr(self, 'upgrade', None) is not None:
                try:
                    self.upgrade.draw()
                except Exception:
                    pass

        


        self.seta.draw()

        # central HUD: show selected building or unit HP and production queue
        hud_center_x = 600
        hud_text_y = 530

        # prefer building selection if present
        selected_building = None
        selected_unit = None
        for ent in entities.values():
            if getattr(ent, 'selected', False):
                if isinstance(ent, BaseBuilding):
                    selected_building = ent
                    break
                else:
                    selected_unit = ent
                    # don't break here so buildings take precedence if also selected

        if selected_building is not None:
            try:
                hp_text = f"HP: {int(selected_building.hp)}/{int(getattr(selected_building, 'max_hp', selected_building.hp))}"
                self.janela.draw_text(hp_text, hud_center_x, hud_text_y, size=18, color=(255,255,255), font_name="Arial", bold=True, italic=False)
                hud_text_y += 22
                # show building level
                try:
                    level = getattr(selected_building, 'level', None)
                    if level is not None:
                        self.janela.draw_text(f"Nível: {int(level)}", hud_center_x, hud_text_y, size=16, color=(200,200,255), font_name="Arial")
                        hud_text_y += 18
                except Exception:
                    pass
                # if upgrade in progress show remaining time
                try:
                    if getattr(selected_building, 'upgrade_in_progress', False):
                        remaining = max(0, int(getattr(selected_building, 'upgrade_time_remaining', 0)))
                        self.janela.draw_text(f"Upgrade: {remaining}s", hud_center_x, hud_text_y, size=14, color=(200,255,200), font_name="Arial")
                        hud_text_y += 18
                except Exception:
                    pass
                # show production progress if building supports queues
                if hasattr(selected_building, 'get_queue_progress'):
                    qp = selected_building.get_queue_progress()
                    if qp is None:
                        self.janela.draw_text("Em produção: nenhum", hud_center_x, hud_text_y, size=16, color=(255,255,255), font_name="Arial")
                        hud_text_y += 18
                    else:
                        unit_type, time_left, total_time = qp
                        self.janela.draw_text(f"Em produção: {unit_type}: {int(time_left)}s / {int(total_time)}s", hud_center_x, hud_text_y, size=16, color=(255,255,255), font_name="Arial")
                        hud_text_y += 18
                        # list queued units
                        q = getattr(selected_building, 'queue', [])
                        for queued in q[1:4]:
                            if len(queued) >= 1:
                                self.janela.draw_text(f"{queued[0]}: Na fila", hud_center_x, hud_text_y, size=14, color=(200,200,200), font_name="Arial")
                                hud_text_y += 16
                # show blocked spawn message
                if getattr(selected_building, 'spawn_blocked', False):
                    self.janela.draw_text("Sem espaço", hud_center_x, hud_text_y, size=16, color=(255,100,100), font_name="Arial", bold=True)
                    hud_text_y += 18
            except Exception:
                pass
        elif selected_unit is not None:
            try:
                # show unit name then HP
                unit_name = getattr(selected_unit, 'name', selected_unit.__class__.__name__)
                self.janela.draw_text(f"{unit_name}", hud_center_x, hud_text_y, size=18, color=(255,255,255), font_name="Arial", bold=True, italic=False)
                hud_text_y += 20
                hp_text = f"HP: {int(selected_unit.hp)}/{int(getattr(selected_unit, 'max_hp', selected_unit.hp))}%"
                self.janela.draw_text(hp_text, hud_center_x, hud_text_y, size=16, color=(255,255,255), font_name="Arial")
                hud_text_y += 22
                # show necromancer resurrection cooldown next to HP
                try:
                    if isinstance(selected_unit, Necromancer):
                        cd_ticks = getattr(selected_unit, 'cooldown', 0)
                        # convert ticks (~60 ticks = 1s) to seconds
                        cd_seconds = max(0, int(round(cd_ticks / 60)))
                        self.janela.draw_text(f"Ressureição CD: {cd_seconds}s", hud_center_x, hud_text_y, size=14, color=(200,200,255), font_name="Arial")
                        hud_text_y += 18
                except Exception:
                    pass
            except Exception:
                pass

        # Left HUD area: show wave and resources (move from top to left HUD)
        try:
            left_x = 50
            left_y = 525
            line_h = 18
            y = left_y
            if wave_manager is not None:
                wave = getattr(wave_manager, 'wave_index', 0)
                state = getattr(wave_manager, 'state', 'idle')
                enemies_left = getattr(wave_manager, 'enemies_remaining', 0)
                countdown = int(getattr(wave_manager, 'countdown', 0)) if state == 'countdown' else 0
                self.janela.draw_text(f"Onda: {wave}  Estado: {state}", left_x, y, size=16, color=(255,255,255), font_name="Arial", bold=True)
                y += line_h
                self.janela.draw_text(f"Inimigos: {enemies_left}  Próxima: {countdown}s", left_x, y, size=14, color=(200,200,255), font_name="Arial")
                y += line_h
            # resources and army below wave info
            self.janela.draw_text(f"Recursos: {economy.resources}", left_x, y, size=16, color=(255,255,255), font_name="Arial", bold=True)
            y += line_h
            self.janela.draw_text(f"Alojamento: {int(economy.army)}/{int(economy.army_max)}", left_x, y, size=14, color=(200,200,200), font_name="Arial")
        except Exception:
            pass

        # HUD message (if any) — supports multi-line messages separated by '\n'
        try:
            if getattr(self, 'hud_message', None) and getattr(self, 'hud_message_time', 0) > 0:
                base_x = 600
                base_y = 600
                line_h = 20
                lines = str(self.hud_message).split('\n')
                for i, line in enumerate(lines):
                    try:
                        self.janela.draw_text(line, base_x, base_y + i * line_h, size=16, color=(255,200,50), font_name="Arial", bold=True)
                    except Exception:
                        pass
                # decrement timer
                self.hud_message_time -= dt
                if self.hud_message_time <= 0:
                    self.hud_message = None
                    self.hud_message_time = 0
        except Exception:
            pass

        if present:
            self.janela.update()

    def set_hud_message(self, message, duration=3.0):
        try:
            self.hud_message = message
            self.hud_message_time = duration
        except Exception:
            pass

    def add_destination_marker(self, world_x, world_y, duration=1.0):
        try:
            self.destination_markers.append({'x': world_x, 'y': world_y, 'time': duration})
        except Exception:
            pass

    def drawHUD(self, menu_atual):
        # hud background
        if isinstance(self.hud, Sprite):
            self.hud.draw()

        if menu_atual == "empty":
            self.buildbutton.draw()

        if menu_atual == "build":
            self.buildbarracks.draw()
            self.buildcampfire.draw()
            self.buildgoldmine.draw()
            self.buildtower.draw()
            self.buildincubator.draw()

    def get_menu_buttons(self, menu_atual):
        """Return a list of tuples (label, rect, sprite) for the simple static HUD buttons.
        Used by controller and for hover/click checks.
        """
        buttons = []
        if menu_atual == "empty":
            buttons.append(("build", self.buildbutton))
        if menu_atual == "build":
            for b in (self.buildbarracks, self.buildcampfire, self.buildgoldmine, self.buildtower, self.buildincubator):
                buttons.append(("build_option", b))
        return buttons

    def draw_placement_preview(self, toPlace, screen_pos, mapa):
        """Draw translucent preview of building under cursor if toPlace is set and cursor is outside HUD."""
        if toPlace is None:
            return
        mx, my = screen_pos
        hud_y = getattr(self.hud, 'y', None)

        preview = None
        if toPlace == "GoldMine":
            if not hasattr(self, '_preview_goldmine'):
                self._preview_goldmine = Sprite('assets/sprites/goldmine.png', 1)
                try:
                    self._preview_goldmine.image.set_alpha(128)
                except Exception:
                    pass
            preview = self._preview_goldmine

        elif toPlace == "Barracks":
            if not hasattr(self, '_preview_barracks'):
                self._preview_barracks = Sprite('assets/sprites/barracks.png', 1)
                try:
                    self._preview_barracks.image.set_alpha(128)
                except Exception:
                    pass
            preview = self._preview_barracks

        elif toPlace == "Campfire":
            # campfire uses 3-frame animation
            if not hasattr(self, '_preview_campfire'):
                self._preview_campfire = Animation('assets/sprites/campfire.png', 3, loop=True)
                try:
                    self._preview_campfire.image.set_alpha(128)
                except Exception:
                    pass
                self._preview_campfire.play()
            preview = self._preview_campfire

        elif toPlace == "Tower":
            if not hasattr(self, '_preview_tower'):
                self._preview_tower = Sprite('assets/sprites/tower.png', 1)
                try:
                    self._preview_tower.image.set_alpha(128)
                except Exception:
                    pass
            preview = self._preview_tower

        elif toPlace == "Incubator":
            if not hasattr(self, '_preview_incubator'):
                self._preview_incubator = Sprite('assets/sprites/incubator.png', 1)
                try:
                    self._preview_incubator.image.set_alpha(128)
                except Exception:
                    pass
            preview = self._preview_incubator

        if preview is None:
            return

        w, h = preview.width, preview.height
        draw_x = mx - w // 2
        draw_y = my - h // 2

        # if preview would overlap HUD area, don't draw it (so HUD stays visually on top)
        if hud_y is not None and (draw_y + h) >= hud_y:
            return

        # animate preview if it's an Animation
        if not isinstance(preview, Sprite):
            try:
                preview.update()
            except Exception:
                pass

        preview.set_position(draw_x, draw_y)
        preview.draw()

        

    