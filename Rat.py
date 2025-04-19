# -*- coding: utf-8 -*-

import pygame

class Rat:
    """
        Define una rata
    """
    def __init__(self, x, y, sprite):
        self.rect = pygame.Rect(x, y, 60, 40)  # Rectángulo para la rata
        self.sprite = sprite  # Imagen de la rata
        self.jumped = False  # Atributo personalizado 'jumped'

    def update(self):
        # Mover la rata (por ejemplo, moverla de izquierda a derecha)
        self.rect.x += 2

    def draw(self, surface):
        # Dibujar la rata en la pantalla
        surface.blit(self.sprite, (self.rect.x, self.rect.y))
