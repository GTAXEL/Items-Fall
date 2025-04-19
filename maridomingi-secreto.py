# -*- coding: utf-8 -*-

import pygame
import random
import os
import sys

from Rat import Rat  # Esto importa la clase Rat del archivo Rat.py

# Función para encontrar la ruta correcta para los recursos
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Función para padear el score a 6 dígitos
def pad_score(score):
    return str(score).zfill(6)

# Función para padear el número a 2 dígitos
def pad_two_digits(count):
    return str(count).zfill(2)

# Inicializar pygame
pygame.init()
pygame.mixer.init()

# Cargar sonidos
shoot_sound = pygame.mixer.Sound(resource_path("sounds/disparo.wav"))
hit_sound = pygame.mixer.Sound(resource_path("sounds/impacto.wav"))
boss_defeat_sound = pygame.mixer.Sound(resource_path("sounds/boss_defeat.wav"))
bonus_sound = pygame.mixer.Sound(resource_path("sounds/bonus.mp3"))
castle_them = pygame.mixer.Sound(resource_path("songs/castle_them.mp3"))

# Configuración de pantalla
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drop items")

# Sprites
player_sprite_right = pygame.image.load(resource_path("sprites/maridomingi/maridomingi-right.png"))
player_sprite_right = pygame.transform.scale(player_sprite_right, (100, 100))

player_sprite_left = pygame.image.load(resource_path("sprites/maridomingi/maridomingi-left.png"))
player_sprite_left = pygame.transform.scale(player_sprite_left, (100, 100))

player_sprite = player_sprite_right  # Imagen inicial del personaje

kaki_moto_sprite = pygame.image.load(resource_path("sprites/kaki/kaki.png"))
kaki_moto_sprite = pygame.transform.scale(kaki_moto_sprite, (150, 75))

castle_sprite = pygame.image.load(resource_path("backgrounds/castle.png"))
castle_sprite = pygame.transform.scale(castle_sprite, (WIDTH, HEIGHT))

mansion_sprite = pygame.image.load(resource_path("backgrounds/mansion.png"))
mansion_sprite = pygame.transform.scale(mansion_sprite, (WIDTH, HEIGHT))

soccer_field_sprite = pygame.image.load(resource_path("backgrounds/futbol.png"))
soccer_field_sprite = pygame.transform.scale(soccer_field_sprite, (WIDTH, HEIGHT))

# Fireball
fireball_sprite = pygame.image.load(resource_path("sprites/enemies/fireball.png"))
fireball_sprite = pygame.transform.scale(fireball_sprite, (80, 80))

# Potion
potion_sprite = pygame.image.load(resource_path("sprites/powerups/potion.png"))
potion_sprite = pygame.transform.scale(potion_sprite, (60, 60))

# Star
star_sprite = pygame.image.load(resource_path("sprites/powerups/star.png"))
star_sprite = pygame.transform.scale(star_sprite, (90, 75))

# Enderpearl
enderpearl_sprite = pygame.image.load(resource_path("sprites/powerups/enderpearl.png"))
enderpearl_sprite = pygame.transform.scale(enderpearl_sprite, (60, 60))

# Bomb
bomb_sprite = pygame.image.load(resource_path("sprites/powerups/bomb.png"))
bomb_sprite = pygame.transform.scale(bomb_sprite, (60, 60))

# Rata
rat_sprite = pygame.image.load(resource_path("sprites/enemies/rat.png"))  # Asegúrate de que esta ruta es correcta
rat_sprite = pygame.transform.scale(rat_sprite, (60, 40))  # Ajusta el tamaño si es necesario

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
LIME = (92, 233, 0)

# Jugador
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT - player_size - 100
player_speed = 5
jumping = False
velocity_y = 0
gravity = 1
jump_strength = -15
ground_y = HEIGHT - player_size - 100  # El "suelo"

# Balas
bullets = []
bullet_speed = 10
max_bullets = 25
bullet_recharge_time = 1000
last_bullet_recharge = pygame.time.get_ticks()

# Enemigos
enemies = []
ENEMY_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(ENEMY_EVENT, 1000)
enemy_speed = 2

# Ratas
rats = []
RAT_EVENT = pygame.USEREVENT + 3
pygame.time.set_timer(RAT_EVENT, random.randint(3000, 5000))

# Textos flotantes
floating_texts = []

# Power-ups
powerups = []
POWERUP_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(POWERUP_EVENT, 7000)
powerup_duration = 300
powerup_type = None
powerup_timer = 0

# Score y vida
score = 0
lives = 3

# Carga la fuente de letra
font_path = resource_path("fonts/ARCADE_I.ttf") 
font = pygame.font.Font(font_path, 16)

# Jefe
boss_health = 100
boss_size = 100
boss_x = WIDTH // 2 - boss_size // 2
boss_y = 50
boss_speed = 10
boss_alive = False
boss_bullets = [99]

# Nivel
level = 1
next_boss_score = 10000

clock = pygame.time.Clock()

def load_high_score():
    try:
        with open("high-score.txt", "r") as file:
            high_score = int(file.read())  # Leer el puntaje desde el archivo
    except FileNotFoundError:
        high_score = 0  # Si el archivo no existe, iniciamos con 0
    print(high_score)
    return high_score

def save_high_score(score):
    with open("high-score.txt", "w") as file:
        file.write(str(score))  # Guardar el puntaje en el archivo

def show_start_screen():
    win.fill(LIME)
    title = font.render("Drop Items", True, BLUE)
    instructions = font.render("Presiona ENTER para comenzar", True, BLACK)
    win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 50))
    win.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT // 2))

    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False

def draw_boss_health_bar():
    if boss_alive:
        health_bar_width = 200
        health_bar_height = 20
        pygame.draw.rect(win, RED, (boss_x - 10, boss_y - 30, health_bar_width, health_bar_height))
        pygame.draw.rect(win, GREEN, (boss_x - 10, boss_y - 30, health_bar_width * (boss_health / (100 + (level * 20))), health_bar_height))
        pygame.draw.rect(win, WHITE, (boss_x - 10, boss_y - 30, health_bar_width, health_bar_height), 2)

# Carga la puntuación máxima
high_score = load_high_score()

show_start_screen()

running = True
castle_them.play()
while running:
    clock.tick(60)
    
    # Fondo según el nivel
    if level == 4:
        win.blit(soccer_field_sprite, (0, 0))
    elif level == 3:
        win.blit(mansion_sprite, (0, 0))
    else:
        win.blit(castle_sprite, (0, 0))

    current_time = pygame.time.get_ticks()
    if current_time - last_bullet_recharge >= bullet_recharge_time and len([b for b in bullets if b is not None]) < max_bullets:
        bullets.append(None)
        last_bullet_recharge = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == ENEMY_EVENT:
            enemy_x = random.randint(0, WIDTH - player_size)
            enemies.append(pygame.Rect(enemy_x, 0, player_size, player_size))
        if event.type == POWERUP_EVENT:
            powerup_x = random.randint(0, WIDTH - 30)
            kind = random.choice(["speed", "shield", "bomb", "life"])
            powerups.append((pygame.Rect(powerup_x, 0, 30, 30), kind))
        if event.type == RAT_EVENT:
            rat_x = -100
            rat_width = rat_sprite.get_width()
            rat_height = rat_sprite.get_height()
            rats.append(Rat(rat_x, ground_y, rat_sprite))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > - 25:
        player_x -= player_speed
        player_sprite = player_sprite_left
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size - 20:
        player_x += player_speed
        player_sprite = player_sprite_right

    if not jumping and keys[pygame.K_UP] and player_y >= ground_y:
        jumping = True
        velocity_y = jump_strength

    if jumping:
        player_y += velocity_y
        velocity_y += gravity
        if player_y >= ground_y:
            player_y = ground_y
            jumping = False
            velocity_y = 0

    if keys[pygame.K_DOWN] and player_y < HEIGHT - player_size - 100:
        player_y += player_speed
    if (keys[pygame.K_LCTRL] or keys[pygame.K_SPACE])  and len([b for b in bullets if b is not None]) < max_bullets and bullets.count(None) == 0:
        new_bullet = pygame.Rect(player_x + player_size // 2 - 2, player_y, 4, 10)
        bullets.append(new_bullet)
        shoot_sound.play()

    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    win.blit(player_sprite, (player_x, player_y))

    for bullet in bullets[:]:
        if bullet is None:
            bullets.remove(bullet)
            continue
        bullet.y -= bullet_speed
        if bullet.y < 0:
            bullets.remove(bullet)
        else:
            pygame.draw.rect(win, RED, bullet)

    for enemy in enemies[:]:
        enemy.y += enemy_speed
        win.blit(fireball_sprite, (enemy.x, enemy.y))
        if enemy.y > HEIGHT:
            enemies.remove(enemy)
        elif player_rect.colliderect(enemy):
            lives -= 1
            enemies.remove(enemy)
            hit_sound.play()
        else:
            for bullet in bullets:
                if bullet and bullet.colliderect(enemy):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 150
                    hit_sound.play()
                    floating_texts.append({
                        "x": bullet.x + 60,
                        "y": bullet.y + 60,
                        "text": "150",
                        "alpha": 255
                    })
                    break

    for powerup in powerups[:]:
        rect, kind = powerup
        rect.y += 3
        color = BLUE if kind == "speed" else CYAN if kind == "shield" else YELLOW if kind == "bomb" else RED
        # potion_sprite
        if BLUE == color:
            win.blit(potion_sprite, (rect.x, rect.y))
        elif RED == color:
            win.blit(star_sprite, (rect.x, rect.y))
        elif CYAN == color:
            win.blit(enderpearl_sprite, (rect.x, rect.y))
        elif YELLOW == color:
            win.blit(bomb_sprite, (rect.x, rect.y))
        else:
            pygame.draw.rect(win, color, rect)
        
        if rect.y > HEIGHT:
            powerups.remove(powerup)
        elif player_rect.colliderect(rect):
            powerups.remove(powerup)
            powerup_type = kind
            powerup_timer = powerup_duration
            if kind == "speed":
                bullet_speed = 20
            elif kind == "shield":
                score += 250
                floating_texts.append({
                    "x": rect.x + 60,
                    "y": rect.y + 60,
                    "text": "250",
                    "alpha": 255
                })
            elif kind == "bomb":
                enemies.clear()
                score += 200
                floating_texts.append({
                    "x": rect.x + 60,
                    "y": rect.y + 60,
                    "text": "200",
                    "alpha": 255
                })
            elif kind == "life":
                lives += 1
                score += 100
                floating_texts.append({
                    "x": rect.x + 60,
                    "y": rect.y + 60,
                    "text": "100",
                    "alpha": 255
                })
            bonus_sound.play()

    # Movimiento de las ratas
    for rat in rats[:]:
        rat.update()  # Actualizar la posición de la rata
        
        if rat.rect.x > WIDTH:
            rats.remove(rat)
            continue  # Saltarse lo demás si ya se eliminó

        win.blit(rat_sprite, (rat.rect.x + 60, rat.rect.y + 60))

        # Verificar si el jugador pasa por encima de la rata (saltó sobre ella)
        if velocity_y > 0 and player_rect.x < rat.rect.x and not rat.jumped and player_rect.top < rat.rect.bottom and player_rect.bottom > rat.rect.top:
            rat.jumped = True
            # El jugador está saltando y su parte superior pasa por encima de la rata
            score += 1000
            bonus_sound.play()
            floating_texts.append({
                "x": rat.rect.x + 60,
                "y": rat.rect.y + 60,
                "text": "1000",
                "alpha": 255
            })
        else:
            # Detectar la colisión normal (cuando el jugador cae y toca la rata)
            if player_rect.colliderect(rat):
                hit_sound.play()  # Sonido del impacto
                lives -= 1        # El jugador pierde una vida
                rats.remove(rat)  # Eliminar la rata

    if score >= next_boss_score and not boss_alive:
        boss_alive = True
        boss_y = 50
        boss_health = 100 * level
        boss_x = WIDTH // 2 - boss_size // 2
        boss_bullets.clear()

    if boss_alive:
        boss_y += boss_speed
        if boss_y > HEIGHT // 4:
            boss_y = HEIGHT // 4

        win.blit(kaki_moto_sprite, (boss_x - 25, boss_y + 30))

        for bullet in bullets[:]:
            if bullet and pygame.Rect(boss_x, boss_y, boss_size, boss_size).colliderect(bullet):
                bullets.remove(bullet)
                boss_health -= 1
                if boss_health <= 0:
                    boss_alive = False
                    score += 500
                    level += 1
                    next_boss_score *= 2
                    boss_defeat_sound.play()

        draw_boss_health_bar()

    hud_text = f" Hi: {pad_score(high_score)}  Score: {pad_score(score)}  Lives: {pad_two_digits(lives)}   Level: {pad_two_digits(level)}"
    hud_render = font.render(hud_text, True, YELLOW)

    # Justificación a la derecha
    text_width = hud_render.get_width()
    win.blit(hud_render, (WIDTH - text_width - 10, 10)) 

    if lives <= 0:
        font_game_over = pygame.font.Font(font_path, 36)

        win.blit(font_game_over.render("GAME OVER", True, YELLOW), (WIDTH//2 - 120, HEIGHT//2))
        pygame.display.update()
        castle_them.stop()
        keys = pygame.key.get_pressed()
        
        # Verificar si el puntaje es más alto que el High Score
        if score > high_score:
            high_score = score
            save_high_score(high_score)  # Guardar el nuevo High Score

        # Espera 5 segundos antes de seguir
        pygame.time.delay(5000)
        sys.exit()

    # Mostrar textos flotantes
    for ft in floating_texts[:]:
        ft["y"] -= 1  # Sube
        ft["alpha"] -= 3  # Se desvanece

        if ft["alpha"] <= 0:
            floating_texts.remove(ft)
            continue

        floating_font = pygame.font.Font(font_path, 24)
        floating_surface = floating_font.render(ft["text"], True, (255, 255, 0))
        floating_surface.set_alpha(ft["alpha"])
        win.blit(floating_surface, (ft["x"], ft["y"]))

    pygame.display.update()

pygame.quit()
flag_background = pygame.image.load("resource_path/backgrounds/bandera.png")  # Cambia 'bandera.png' por el nombre correcto
flag_background = pygame.transform.scale(flag_background, (800, 600))  # Ajusta al tamaño de tu pantalla
if level == 5:
    win.blit(flag_background, (0, 0))  # Mostrar la bandera como fondo
else:
    win.fill((0, 0, 0))  # Fondo normal (negro) o usa tu fondo por defecto