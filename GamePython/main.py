import pgzrun
import random
import math
import time
from pygame import Rect

from settings import *
from characters import *

sounds.totality.play(-1)  # Toca a música em loop
sounds.totality.set_volume(0.2)


def draw_menu():
    global game_started
    screen.clear()
    bg_menu.draw()
    button_mute.draw()
    button_start.draw()
    button_quit.draw()

def on_mouse_down(pos):
    global game_started, toggle_sound

    if button_start.collidepoint(pos):
        game_started = True  # Inicia o jogo

    elif button_quit.collidepoint(pos):
        quit()  # Fecha o jogo

    elif button_mute.collidepoint(pos):
        if toggle_sound:
            sounds.totality.stop()
            button_mute.image = 'ui/mute_checked'
            toggle_sound = False
        else:
            sounds.totality.play(-1)
            button_mute.image = 'ui/mute_gray'
            toggle_sound = True

def draw_game_over():
    global game_over, game_started
    screen.clear()
    game_started = False
    game_over = True
    restart_game()

def restart_game():
    global current_level, game_started, game_over
    current_level = -1
    game_started = True
    game_over = False
    next_level()

def draw_game_won():
    global game_won, game_started
    screen.clear()
    bg_won.draw()

    game_started = False
    game_won = True

def draw_game():
    screen.clear()
    bg_sky.draw()
    for platform, _ in platforms:
        screen.draw.filled_rect(platform, 'darkgreen')
    for key in keys:
        if key not in collected_keys:
            key.draw()
    for door in doors:
        door.draw()
    for enemy_spike in enemies_spike:
        enemy_spike.draw()
    for enemy_fly in enemies_fly:
        enemy_fly.draw()
    for spike in spikes:
        spike.draw()
    player.draw()

def idle_animation():
    global frame_index, animation_speed, float_speed, float_amplitude, origin, smoothing
    time_elapsed = time.time()

    if not keyboard.left and not keyboard.right:
        frame_index['player_idle'] += animation_speed
        if frame_index['player_idle'] >= len(player_idle):
            frame_index['player_idle'] = 0
        player.image = player_idle[int(frame_index['player_idle'])]

    elif keyboard.left or keyboard.right:
        frame_index['player_run'] += animation_speed
        if frame_index['player_run'] >= len(player_run):
            frame_index['player_run'] = 0
        player.image = player_run[int(frame_index['player_run'])]
        
    for key in keys:
        if key not in collected_keys:
            index = keys.index(key)
            origin_y = origin['key'][index][1]
            key.y = origin_y + math.sin(time_elapsed * float_speed * (1 - smoothing)) * float_amplitude

    for door in doors:
        index = doors.index(door)
        origin_y = origin['door'][index][1]
        door.y = origin_y + math.sin(time_elapsed * float_speed * (1 - smoothing)) * float_amplitude

    for enemy_spike in enemies_spike:
        frame_index['enemy_spike_run'] += animation_speed
        if frame_index['enemy_spike_run'] >= len(enemy_spike_run):
            frame_index['enemy_spike_run'] = 0
        enemy_spike.image = enemy_spike_run[int(frame_index['enemy_spike_run'])]

    for enemy_fly in enemies_fly:
        frame_index['fly_idle'] += animation_speed
        if frame_index['fly_idle'] >= len(fly_idle):
            frame_index['fly_idle'] = 0
        enemy_fly.image = fly_idle[int(frame_index['fly_idle'])]
    
def handle_input():
    if keyboard.left and player.midleft[0] > 0:
        player.x -= MOVE_SPEED
    if keyboard.right and player.midright[0] < WIDTH:
        player.x += MOVE_SPEED
    if keyboard.space and player.on_ground:
        player.vy = JUMP_STRENGTH
        player.on_ground = False
        if toggle_sound:
            sounds.jump.play()

def apply_gravity():
    player.vy += GRAVITY
    player.y += player.vy

    player.on_ground = False

    for platform, _ in platforms:
        if player.colliderect(platform) and player.vy > 0:  # Colisão com a plataforma
            if player.bottom >= platform.top:
                player.y = platform.top - player.height // 2
                player.vy = 0
                player.on_ground = True
        if player.colliderect(platform) and player.vy < 0: #se tiver pulando
                player.y = platform.bottom + player.height // 2 # Para de subir ao bater no teto
                player.vy = 0 

def check_collision():
    global sounds_off
    for platform, _ in platforms:
        if player.colliderect(platform):
            # Movendo para a direita
            if keyboard.right and player.right > platform.left and player.x < platform.x:
                player.right = platform.left
            # Movendo para a esquerda
            if keyboard.left and player.left < platform.right and player.x > platform.x:
                player.left = platform.right 

    for obj in enemies_spike + enemies_fly + spikes:
        if player.colliderect(obj):
            draw_game_over()
            if toggle_sound:
                sounds.ouch.play()

def enemy_spike_walking ():
    global enemy_spike_offset, enemy_spike_direction
    for i, enemy_spike in enumerate(enemies_spike):
        enemy_spike_offset[i] += 2 * enemy_spike_direction[i]
        
        if enemy_spike_offset[i] >= 100:
            enemy_spike_offset[i] = 100  
            enemy_spike_direction[i] = -1
        elif enemy_spike_offset[i] <= -100:
            enemy_spike_offset[i] = -100
            enemy_spike_direction[i] = 1

def enemy_fly_height():
    global enemy_fly_offset, enemy_fly_direction
    for i, enemy_fly in enumerate(enemies_fly):
        enemy_fly_offset[i] += 2 * enemy_fly_direction[i]
        
        if enemy_fly_offset[i] >= 100:
            enemy_fly_offset[i] = 100  
            enemy_fly_direction[i] = -1  
        elif enemy_fly_offset[i] <= -100:
            enemy_fly_offset[i] = -100
            enemy_fly_direction[i] = 1 
        
        enemy_fly.y = origin['enemy_fly'][i][1] + enemy_fly_offset[i]  

def camera_moving():
    global x_movement, origin, right_platform, left_platform, smoothing

    new_x_movement = min(max(WIDTH // 2 - player.x, WIDTH - right_platform), - left_platform)
    x_movement = x_movement * (1 - smoothing) + new_x_movement * smoothing

    for i, (platform, _) in enumerate(platforms):
        platform.x = origin['platform'][i][0] + x_movement
    for i, key in enumerate(keys):
        key.x = origin['key'][i][0] + x_movement
    for i, door in enumerate(doors):
        door.x = origin['door'][i][0] + x_movement 
    for i, enemy_spike in enumerate(enemies_spike):
        enemy_spike.x = origin['enemy_spike'][i][0] + x_movement + enemy_spike_offset[i]
    for i, enemy_fly in enumerate(enemies_fly):
        enemy_fly.x = origin['enemy_fly'][i][0] + x_movement
    for i, spike in enumerate(spikes):
        spike.x = origin['spike'][i][0] + x_movement

    bg_sky.x = WIDTH // 2 + x_movement

def collect_key():
    global collected_keys
    for key in keys:
        if player.colliderect(key) and key not in collected_keys: 
            collected_keys.append(key)  # Adiciona a chave ao conjunto de coletadas
            if toggle_sound:
                sounds.collect.play()

def unlock_door():
    global door_unlocked
    if total_keys == len(collected_keys):  # Verifica se todas as chaves foram coletadas
        for door in doors:
            door.image = 'sunflower'
            door_unlocked = True

    for door in doors:
        if player.colliderect(door) and door_unlocked:
            next_level()
            if toggle_sound:
                sounds.teleport.play()

def next_level():
    global current_level, layout, platforms, keys, doors, origin, door_unlocked, enemies_spike, enemies_fly, spikes, enemy_spike_run, fly_idle, enemy_spike 

    if current_level == len(LEVELS) - 1:
        draw_game_won()
        return

    current_level = (current_level + 1) % len(LEVELS) 
    layout = LEVELS[current_level]

    platforms.clear()
    keys.clear()
    doors.clear()
    enemies_spike.clear()
    enemies_fly.clear()
    spikes.clear()
    door_unlocked = False  # Reseta o estado da porta

    platforms = [
        (Rect((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)), 'dark green')
        for y in range(len(layout)) for x in range(len(layout[y])) if layout[y][x] == 1
    ]

    keys = [
        Actor('key', (x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2))
        for y in range(len(layout)) for x in range(len(layout[y])) if layout[y][x] == 2
    ]

    doors = [
        Actor('locked', (x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2))
        for y in range(len(layout)) for x in range(len(layout[y])) if layout[y][x] == 3
    ]

    enemies_spike = [
        Actor(enemy_spike_run[int(frame_index['enemy_spike_run'])], (x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2))
        for y in range(len(layout)) for x in range(len(layout[y])) if layout[y][x] == 4
    ] if enemy_spike_run else []
    for i, enemy_spike in enumerate(enemies_spike):
        enemy_spike_offset[i] = 0  # Começa parado
        enemy_spike_direction[i] = 1

    enemies_fly = [
        Actor(fly_idle[int(frame_index['fly_idle'])], (x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2))
        for y in range(len(layout)) for x in range(len(layout[y])) if layout[y][x] == 5
    ] if fly_idle else [] 
    for i, enemy_fly in enumerate(enemies_fly):
        enemy_fly_offset[i] = 0
        enemy_fly_direction[i] = 1

    spikes = [
        Actor('spike', (x * TILE_SIZE + TILE_SIZE / 2, (y + 1) * TILE_SIZE - 25 / 2))
        for y in range(len(layout)) for x in range(len(layout[y])) if layout[y][x] == 6
    ] 

    origin = {
    'platform': [(platform.x, platform.y) for platform, _ in platforms],
    'key': [(key.x, key.y) for key in keys],
    'door': [(door.x, door.y) for door in doors],
    'enemy_spike': [(enemy_spike.x, enemy_spike.y) for enemy_spike in enemies_spike] if enemies_spike else [],
    'enemy_fly': [(enemy_fly.x, enemy_fly.y) for enemy_fly in enemies_fly] if enemies_fly else [],
    'spike': [(spike.x, spike.y) for spike in spikes] if spikes else []
    }
    # Reinicializa as chaves coletadas
    collected_keys.clear()

    player.x, player.y = INITIAL_POSITION  # Reinicia a posição do personagem

def update():
    if game_started:
        handle_input()
        check_collision()
        apply_gravity()
        idle_animation()
        camera_moving()
        collect_key()
        unlock_door()
        enemy_spike_walking ()
        enemy_fly_height()


def draw():
    if game_started:
        draw_game()
    elif game_over:
        draw_game_over()
    elif game_won:
        draw_game_won()
    else:
        draw_menu()
    

pgzrun.go()