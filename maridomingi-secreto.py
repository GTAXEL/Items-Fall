# -*- coding: utf-8 -*-

import pygame
import random
import os
import sys

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
game_over_sound = pygame.mixer.Sound(resource_path("sounds/game_over.wav"))
boss_defeat_sound = pygame.mixer.Sound(resource_path("sounds/boss_defeat.wav"))
bonus_sound = pygame.mixer.Sound(resource_path("sounds/bonus.mp3"))


# Configuración de pantalla
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("El Maridomingi Secreto")

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


# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)

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
font_path = resource_path("fonts/ARCADE_I.ttf")  # Asegurate que el nombre sea correcto
font = pygame.font.Font(font_path, 16)  # Ajustá el tamaño si es muy grande

# Jefe
boss_health = 1000
boss_size = 100
boss_x = WIDTH // 2 - boss_size // 2
boss_y = 50
boss_speed = 10
boss_alive = False
boss_bullets = [99]

# Nivel
level = 1
next_boss_score = 100

clock = pygame.time.Clock()

def show_start_screen():
    win.fill(BLACK)
    title = font.render("EL MARIDOMINGI SECRETO", True, WHITE)
    instructions = font.render("Presiona ENTER para comenzar", True, WHITE)
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

show_start_screen()

running = True
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
                    score += 1
                    hit_sound.play()
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
                lives += 1
            elif kind == "bomb":
                enemies.clear()
                score += 20
            elif kind == "life":
                lives += 2
                score += 10
            bonus_sound.play()
    if score >= next_boss_score and not boss_alive:
        boss_alive = True
        boss_y = 50
        boss_health = 100 + (level * 20)
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
                boss_health -= 10
                if boss_health <= 0:
                    boss_alive = False
                    score += 50
                    level += 1
                    next_boss_score += 100
                    boss_defeat_sound.play()

        draw_boss_health_bar()

    hud_text = f"Puntos: {pad_score(score)}   Vidas: {pad_two_digits(lives)}   Nivel: {pad_two_digits(level)}"
    hud_render = font.render(hud_text, True, YELLOW)

    # Justificación a la derecha
    text_width = hud_render.get_width()
    win.blit(hud_render, (WIDTH - text_width - 10, 10)) 

    if lives <= 0:
        win.blit(font.render("GAME OVER - Presiona ESC para salir", True, RED), (WIDTH//2 - 200, HEIGHT//2))
        pygame.display.update()
        game_over_sound.play()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        continue

    pygame.display.update()

pygame.quit()


