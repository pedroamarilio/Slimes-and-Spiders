import pygame
import sys
import random
import math

from entities.base_entity import BaseEntity
from entities.units.melee import Melee
from entities.units.archer import Archer
from entities.units.necromancer import Necromancer
from entities.units.dragon import Dragon
from entities.units.slime import Slime
from entities.units.healer import Healer

from entities.enemies.imp import Imp

from entities.buildings.goldmine import GoldMine
from entities.buildings.barracks import Barracks
from entities.buildings.campfire import Campfire
from entities.buildings.tower import Tower
from entities.buildings.incubator import Incubator

from game.economy import Economy
from game.economy import Change
from game.economy import ChangeManager
from game.screen import Screen
from game.controller import Controller
from game.movement import Movement
from game.utils import Utils
from ui.hud import Button

from systems.ai_controller import AI_Controller
from systems.entity_system import EntitySystem
from game.wave_manager import WaveManager
from scenes.scene_menu import SceneMenu



#from ui.hud import HUDManager
from ui.hud import MenuContext
from entities.buildings.barracks import Barracks
#from buildings.goldmine import GoldMine
#from buildings.tower import Tower
#from buildings.volcano import Volcano






from PPlay.animation import *
from PPlay.sound import *
from PPlay.window import *
from PPlay.mouse import *
from PPlay.sprite import *
from PPlay.gameimage import *

musica1 = Sound("assets/sounds/Torre-de-Gente.ogg")
janela = Window(1366,768)


pygame.mixer.pre_init(frequency=48000, size=16, channels=4, buffer=4096)


janela.set_title("Slimes & Spiders")
# show main menu before starting the game
try:
    menu_scene = SceneMenu(janela)
    musica1.play()
    action = menu_scene.run()
    if action == 'exit':
        pygame.quit()
        sys.exit()
except Exception:
    # if menu fails, continue to game
    pass

ai_controller = AI_Controller()
entity_system = EntitySystem()

menu_atual = "empty" #empty, build, barracks, goldmine, tower, volcano
# Sprites dos botões
seta = Sprite("assets/sprites/maozinha.png")
mapa = Sprite("assets/maps/mapa01.png")

hudpadrao = Sprite("assets/sprites/hud.png")
hudpadrao.set_position(0, 510)

buildbutton = Sprite("assets/sprites/buildbutton.png")
buildbutton.set_position(1100, 520)

buildbarracks = Sprite("assets/sprites/buildbarracks.png")
buildbarracks.set_position(1100, 520)

buildcampfire = Sprite("assets/sprites/buildcampfire.png")
buildcampfire.set_position(1170, 520)

buildgoldmine = Sprite("assets/sprites/buildgoldmine.png")
buildgoldmine.set_position(1240, 520)

buildtower = Sprite("assets/sprites/buildtower.png")
buildtower.set_position(1100, 600)

buildincubator = Sprite("assets/sprites/buildincubator.png")
buildincubator.set_position(1170, 600)


cursor = janela.get_mouse()
pygame.mouse.set_visible(False)

dt = 1/60 #Por algum motivo janela.delta_time() está retornando 0.0, então não tem o que fazer
screen = Screen(janela, musica1, cursor, mapa, seta, hudpadrao, buildbutton, buildbarracks, buildcampfire, buildgoldmine, buildtower, buildincubator, menu_atual, keyboard)
controller = Controller(janela)
movement = Movement()

# Economia
economy = Economy()
changes = []
changeManager = ChangeManager()
approved = {}
income_cooldown = 0

#Entities
utils = Utils()
create_cooldown = 0

units = {}
entities = {}
enemies = {}
buildings = {}
deadEntities = {}
selected_units = []
selection_area = (0, 0, 0, 0) #x1, y1, x2, y2

# don't spawn Dragon, Slime or Necromancer at game start — player will train them
goldmine = GoldMine()
entity_system.toInitialize.append(goldmine)

# spawn three starting Warriors (Melee) around the goldmine
try:
    for i in range(3):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(24, 64)
        mx = int(goldmine.x + math.cos(angle) * r)
        my = int(goldmine.y + math.sin(angle) * r)
        entity_system.toInitialize.append(Melee(mx, my))
        try:
            economy.army += controller.room.get("Warrior", 0)
        except Exception:
            pass
except Exception:
    pass

keyboard = janela.get_keyboard()

spawn_cooldown = 0

# define the same 8 spawn points used previously so waves spawn from the map edges
spawn_points = [
    (100, -100),
    (1024, -100),
    (2048 + 100, -100),
    (-100, 1024),
    (1024, 2048 + 100),
    (2048 + 100, -50),
    (1024, 2048 + 100),
    (-50, 2048 + 100),
]

wave_manager = WaveManager(entity_system, spawn_points=spawn_points, inter_wave_delay=18.0, spawn_interval=1.0, initial_wave_delay=20.0)
wave_manager.start()

while True:
    change, selection_area, menu_atual = controller.update(mapa, entities, units, selected_units, screen, menu_atual)

    if change != None:
        changeManager.toInitialize.append(change)

    for goldmine in [b for b in buildings.values() if isinstance(b, GoldMine)]:
        if income_cooldown == 0 and goldmine.exists:
            change = Change(amount=100, entity_string=None, position=None)
            changeManager.toInitialize.append(change)
            # reduce cooldown from 360 -> 36 to make gold production 10x faster
            income_cooldown = 360
        else:
            income_cooldown -= 1

    # Update wave manager (spawns enemies into entity_system.toInitialize)
    wave_manager.update(dt, entities, enemies)



    changes, approved = changeManager.initialize()
    economy.update(changes, approved)

    # If any spend change was denied due to insufficient funds, show central HUD message
    try:
        for change in changes:
            if not approved.get(change.id, False) and change.amount < 0:
                try:
                    req = -int(change.amount)
                except Exception:
                    req = -change.amount
                try:
                    screen.set_hud_message(f"Sem dinheiro para ação!\nDinheiro necessário: {req}", 3.0)
                except Exception:
                    pass
                break
    except Exception:
        pass

    procesed_changes = []
    for change in changes:
        if approved[change.id]:
            if change.amount < 0:
                if change.entity_string == "Slime":
                    # spawn Slime around incubator position if provided
                    if isinstance(change.position, (list, tuple)) and len(change.position) >= 4:
                        cx, cy, bw, bh = change.position[0], change.position[1], change.position[2], change.position[3]
                        base_r = max(bw, bh) / 2 + 8
                        angle = random.uniform(0, 2 * math.pi)
                        r = random.uniform(base_r, base_r + 48)
                        rx = int(cx + math.cos(angle) * r)
                        ry = int(cy + math.sin(angle) * r)
                    else:
                        rx = change.position[0] + random.randint(-32, 32)
                        ry = change.position[1] + random.randint(-32, 32)
                    new_entity = Slime(rx, ry)
                    entity_system.toInitialize.append(new_entity)
                    economy.army += controller.room[change.entity_string]
                elif change.entity_string == "Necromancer":
                    # spawn Necromancer around the provided position (tower center)
                    if isinstance(change.position, (list, tuple)) and len(change.position) >= 4:
                        cx, cy, bw, bh = change.position[0], change.position[1], change.position[2], change.position[3]
                        base_r = max(bw, bh) / 2 + 8
                        angle = random.uniform(0, 2 * math.pi)
                        r = random.uniform(base_r, base_r + 48)
                        rx = int(cx + math.cos(angle) * r)
                        ry = int(cy + math.sin(angle) * r)
                    else:
                        rx = change.position[0] + random.randint(-32, 32)
                        ry = change.position[1] + random.randint(-32, 32)
                    new_entity = Necromancer(rx, ry)
                    entity_system.toInitialize.append(new_entity)
                    economy.army += controller.room[change.entity_string]
                elif change.entity_string == "Dragon":
                    # spawn Dragon around incubator position if provided
                    if isinstance(change.position, (list, tuple)) and len(change.position) >= 4:
                        cx, cy, bw, bh = change.position[0], change.position[1], change.position[2], change.position[3]
                        base_r = max(bw, bh) / 2 + 8
                        angle = random.uniform(0, 2 * math.pi)
                        r = random.uniform(base_r, base_r + 48)
                        rx = int(cx + math.cos(angle) * r)
                        ry = int(cy + math.sin(angle) * r)
                    else:
                        rx = change.position[0] + random.randint(-32, 32)
                        ry = change.position[1] + random.randint(-32, 32)
                    new_entity = Dragon(rx, ry)
                    entity_system.toInitialize.append(new_entity)
                    economy.army += controller.room[change.entity_string]
                elif change.entity_string == "Healer":
                    # spawn Healer around the provided position (tower center)
                    if isinstance(change.position, (list, tuple)) and len(change.position) >= 4:
                        cx, cy, bw, bh = change.position[0], change.position[1], change.position[2], change.position[3]
                        base_r = max(bw, bh) / 2 + 8
                        angle = random.uniform(0, 2 * math.pi)
                        r = random.uniform(base_r, base_r + 48)
                        rx = int(cx + math.cos(angle) * r)
                        ry = int(cy + math.sin(angle) * r)
                    else:
                        rx = change.position[0] + random.randint(-32, 32)
                        ry = change.position[1] + random.randint(-32, 32)
                    new_entity = Healer(rx, ry)
                    entity_system.toInitialize.append(new_entity)
                    economy.army += controller.room[change.entity_string]
                elif change.entity_string == "GoldMine":
                    # spawn goldmine at approved position
                    gx, gy = change.position
                    new_building = GoldMine(gx, gy)
                    entity_system.toInitialize.append(new_building)
                    # clear placement state
                    controller.toPlace = None
                elif change.entity_string == "Barracks":
                    gx, gy = change.position
                    new_building = Barracks((gx, gy), economy, None)
                    entity_system.toInitialize.append(new_building)
                    controller.toPlace = None
                elif change.entity_string == "Campfire":
                    gx, gy = change.position
                    new_building = Campfire(gx, gy, economy)
                    entity_system.toInitialize.append(new_building)
                    controller.toPlace = None
                elif change.entity_string == "Tower":
                    gx, gy = change.position
                    # Tower expects a position tuple and economy reference
                    new_building = Tower((gx, gy), economy, None)
                    entity_system.toInitialize.append(new_building)
                    controller.toPlace = None
                elif change.entity_string == "Incubator":
                    gx, gy = change.position
                    new_building = Incubator((gx, gy), economy, None)
                    entity_system.toInitialize.append(new_building)
                    controller.toPlace = None

                procesed_changes.append(change)
        else:
            procesed_changes.append(change)

    for change in procesed_changes:
        changes.remove(change)   

    changes.clear()
    approved.clear()    


    entity_system.initialize(entities, units, enemies, buildings)
    # update buildings' production timers by passing dt
    # EntitySystem stores dt internally; set it here
    entity_system._dt = dt
    entity_system.update(entities, units, enemies, buildings, controller, economy)
    # After building timers advanced, attempt to spawn ready units from building queues
    for b in list(buildings.values()):
        # peek at head of production queue and spawn only when there's space
        if hasattr(b, 'queue') and b.queue:
            unit_type, time_left, total_time = b.queue[0]
            if time_left <= 0:
                # check army capacity
                if economy.army + controller.room.get(unit_type, 0) > economy.army_max:
                    b.spawn_blocked = True
                    print("sem espaço")
                else:
                    # consume from queue and spawn the unit around building
                    b.queue.pop(0)
                    b.spawn_blocked = False
                    cx = b.x + b.sprite.width // 2
                    cy = b.y + b.sprite.height // 2
                    base_r = max(b.sprite.width, b.sprite.height) / 2 + 8
                    angle = random.uniform(0, 2 * math.pi)
                    r = random.uniform(base_r, base_r + 48)
                    rx = int(cx + math.cos(angle) * r)
                    ry = int(cy + math.sin(angle) * r)
                    if unit_type == "Slime":
                        entity_system.toInitialize.append(Slime(rx, ry))
                    elif unit_type == "Dragon":
                        entity_system.toInitialize.append(Dragon(rx, ry))
                    elif unit_type == "Necromancer":
                        entity_system.toInitialize.append(Necromancer(rx, ry))
                    elif unit_type == "Healer":
                        entity_system.toInitialize.append(Healer(rx, ry))
                    elif unit_type == "Warrior":
                        entity_system.toInitialize.append(Melee(rx, ry))
                    elif unit_type == "Archer":
                        entity_system.toInitialize.append(Archer(rx, ry))
                    economy.army += controller.room.get(unit_type, 0)
    movement.update(entities, dt)
    utils.updateCollision(entities)
    ai_controller.updateDestiny(units, enemies, buildings)
    screen.update(economy, entities, selection_area, dt, menu_atual, controller.toPlace, wave_manager)

    # GAME OVER: no units, no goldmines and not enough resources to build one
    try:
        if len(units) == 0 or len(buildings) == 0: 
            has_goldmine = any(isinstance(b, GoldMine) for b in buildings.values())
            can_build_goldmine = economy.resources >= 1000
            if (not has_goldmine) and (not can_build_goldmine):
                # try to show a full-screen game over image
                try:
                    gameover = Sprite('assets/sprites/gameover.png', 1)
                    gw = getattr(janela, 'width', 1366)
                    gh = getattr(janela, 'height', 768)
                    gx = int((gw - gameover.width) / 2)
                    gy = int((gh - gameover.height) / 2)
                    gameover.set_position(gx, gy)

                    # wait for user input while drawing the current scene behind the image
                    waiting = True
                    while waiting:
                        try:
                            screen.update(economy, entities, selection_area, dt, menu_atual, controller.toPlace, wave_manager)
                        except Exception:
                            pass
                        try:
                            gameover.draw()
                        except Exception:
                            pass
                        janela.update()
                        try:
                            # accept Enter, Space, Esc or mouse click to continue/exit
                            if keyboard.key_pressed('ENTER') or keyboard.key_pressed('SPACE') or keyboard.key_pressed('ESC'):
                                waiting = False
                            if janela.get_mouse().is_button_pressed(1):
                                waiting = False
                        except Exception:
                            pass
                        pygame.time.delay(100)
                except Exception:
                    # fallback to text message
                    screen.set_hud_message("GAME OVER", 9999)
                    screen.update(economy, entities, selection_area, dt, menu_atual, controller.toPlace, wave_manager)
                break
    except Exception:
        pass

#A FAZER:
#Deixar a unidade parada para atacar
#Deixar as construções paradas