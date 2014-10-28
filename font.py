import pygame
from resource import font_cache

pygame.font.init()

FONT_PAWN_HEALTH_BAR = 0

font_cache[FONT_PAWN_HEALTH_BAR] = pygame.font.Font('font/simkai.ttf', 12)