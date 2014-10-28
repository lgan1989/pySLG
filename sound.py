import pygame
from resource import sound_cache

SOUND_TYPE_BGM = 0
SOUND_TYPE_ATTACK = 1
SOUND_TYPE_WALK = 2
SOUND_TYPE_WALK_MOUNT = 3
SOUND_TYPE_WALK_JUNGLE = 4
SOUND_TYPE_HIT = 5
SOUND_TYPE_RETREAT = 6



class Sound:



    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=128)
        self.sound_set = {}
        sound_cache[SOUND_TYPE_ATTACK] = pygame.mixer.Sound('sound/Se32.wav')
        sound_cache[SOUND_TYPE_WALK] = pygame.mixer.Sound('sound/Se23.wav')
        sound_cache[SOUND_TYPE_WALK_MOUNT] = pygame.mixer.Sound('sound/Se24.wav')
        sound_cache[SOUND_TYPE_WALK_JUNGLE] = pygame.mixer.Sound('sound/Se27.wav')
        sound_cache[SOUND_TYPE_HIT] = pygame.mixer.Sound('sound/Se35.wav')
        sound_cache[SOUND_TYPE_RETREAT] = pygame.mixer.Sound('sound/Se16.wav')


