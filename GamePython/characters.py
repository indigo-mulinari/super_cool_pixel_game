from pgzero.actor import Actor
from settings import *

INITIAL_POSITION = (100, 300)

# Lista de imagens da animação
player_idle = ['player/player_001', 'player/player_002', 'player/player_003']
player_run = ['player/player_001','player/player_004']

fly_idle = ['enemy_fly/enemy_fly_001', 'enemy_fly/enemy_fly_002', 'enemy_fly/enemy_fly_003']
enemy_spike_run = ['enemy_spike/enemy_spike_001', 'enemy_spike/enemy_spike_002']

frame_index = {
    'player_idle': 0,
    'player_run': 0,
    'fly_idle': 0,
    'enemy_spike_run': 0
}

animation_speed = 0.07
float_speed = 5  # Velocidade da animação
float_amplitude = 4 # Intensidade do movimento
smoothing = 0.1  

# Personagem principal
player = Actor(player_idle[int(frame_index['player_idle'])], INITIAL_POSITION)
player.vy = 0

# Fundo
bg_sky = Actor('bg/sky', (0, 275))
bg_menu = Actor('bg/menu', (400, 275))
bg_won = Actor('bg/won', (400, 275))


button_mute = Actor('ui/mute_gray', (400, 250))
button_start = Actor('ui/button_start', (400, 350))
button_quit = Actor('ui/button_quit', (400, 470))
