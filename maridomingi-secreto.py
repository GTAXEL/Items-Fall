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

# Inicializar pygame
pygame.init()
pygame.mixer.init()

# Cargar sonidos
shoot_sound = pygame.mixer.Sound(resource_path("disparo.wav"))
hit_sound = pygame.mixer.Sound(resource_path("impacto.wav"))
game_over_sound = pygame.mixer.Sound(resource_path("game_over.wav"))
boss_defeat_sound = pygame.mixer.Sound(resource_path("boss_defeat.wav"))

# Configuración de pantalla
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("El Maridomingi Secreto")

# Sprites
player_sprite = pygame.image.load(resource_path("maridomingi.png"))
player_sprite = pygame.transform.scale(player_sprite, (50, 50))

kaki_moto_sprite = pygame.image.load(resource_path("kaki.png"))
kaki_moto_sprite = pygame.transform.scale(kaki_moto_sprite, (150, 75))

castle_sprite = pygame.image.load(resource_path("castle.png"))
castle_sprite = pygame.transform.scale(castle_sprite, (WIDTH, HEIGHT))

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
player_y = HEIGHT - player_size - 10
player_speed = 5

# Balas
bullets = []
bullet_speed = 10

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
font = pygame.font.SysFont("Arial", 24)

# Jefe
boss_health = 100
boss_size = 100
boss_x = WIDTH // 2 - boss_size // 2
boss_y = 50
boss_speed = 1
boss_alive = False
boss_bullets = []

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
    win.blit(castle_sprite, (0, 0))

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
    if keys[pygame.K_a] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_d] and player_x < WIDTH - player_size:
        player_x += player_speed
    if keys[pygame.K_w] and player_y > 0:
        player_y -= player_speed
    if keys[pygame.K_s] and player_y < HEIGHT - player_size:
        player_y += player_speed
    if keys[pygame.K_SPACE]:
        bullets.append(pygame.Rect(player_x + player_size // 2 - 2, player_y, 4, 10))
        shoot_sound.play()

    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    win.blit(player_sprite, (player_x, player_y))

    for bullet in bullets[:]:
        bullet.y -= bullet_speed
        if bullet.y < 0:
            bullets.remove(bullet)
        pygame.draw.rect(win, RED, bullet)

    for enemy in enemies[:]:
        enemy.y += enemy_speed
        pygame.draw.rect(win, GREEN, enemy)
        if enemy.y > HEIGHT:
            enemies.remove(enemy)
        elif player_rect.colliderect(enemy):
            lives -= 1
            enemies.remove(enemy)
            hit_sound.play()
        else:
            for bullet in bullets:
                if bullet.colliderect(enemy):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 1
                    hit_sound.play()
                    break

    for powerup in powerups[:]:
        rect, kind = powerup
        rect.y += 3
        color = BLUE if kind == "speed" else CYAN if kind == "shield" else YELLOW if kind == "bomb" else RED
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
            if pygame.Rect(boss_x, boss_y, boss_size, boss_size).colliderect(bullet):
                bullets.remove(bullet)
                boss_health -= 10
                if boss_health <= 0:
                    boss_alive = False
                    score += 50
                    level += 1
                    next_boss_score += 100
                    boss_defeat_sound.play()

        draw_boss_health_bar()

    win.blit(font.render(f"Puntos: {score}", True, WHITE), (10, 10))
    win.blit(font.render(f"Vidas: {lives}", True, WHITE), (10, 40))
    win.blit(font.render(f"Nivel: {level}", True, WHITE), (10, 70))

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
