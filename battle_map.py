from pygame import image
from resource import map_image_cache
from renderer import render_queue
import pawn
import sound

DEFAULT_MAP_WIDTH = 480
DEFAULT_MAP_HEIGHT = 720
DEFAULT_MAP_TILE_WIDTH = 48
DEFAULT_MAP_TILE_HEIGHT = 48
DEFAULT_MAP_NAME = "map-1"

COLLISION_INFO_EMPTY = 0
COLLISION_INFO_OCCUPIED = 1
BLOCK_INFO_UP_BLOCKED = 1
BLOCK_INFO_DOWN_BLOCKED = 2
BLOCK_INFO_LEFT_BLOCKED = 4
BLOCK_INFO_RIGHT_BLOCKED = 8

TERRAIN_INFO_GROUND = 0
TERRAIN_INFO_JUNGLE_LOW = 1
TERRAIN_INFO_JUNGLE_HIGH = 2
TERRAIN_INFO_WATER = 3

TERRAIN_MASK_JUNGLE_HIGH_48 = 0
TERRAIN_MASK_JUNGLE_HIGH_64 = 1

TERRAIN_MASK_JUNGLE_LOW_48 = 2
TERRAIN_MASK_JUNGLE_LOW_64 = 3

TERRAIN_MASK = {}
TERRAIN_MASK[TERRAIN_INFO_JUNGLE_LOW,0] = TERRAIN_MASK_JUNGLE_LOW_48
TERRAIN_MASK[TERRAIN_INFO_JUNGLE_LOW,1] = TERRAIN_MASK_JUNGLE_LOW_64
TERRAIN_MASK[TERRAIN_INFO_JUNGLE_HIGH,0] = TERRAIN_MASK_JUNGLE_HIGH_48
TERRAIN_MASK[TERRAIN_INFO_JUNGLE_HIGH,1] = TERRAIN_MASK_JUNGLE_HIGH_64


TERRAIN_SOUND = {}
TERRAIN_SOUND[ TERRAIN_INFO_JUNGLE_HIGH ] = sound.SOUND_TYPE_WALK_JUNGLE
TERRAIN_SOUND[ TERRAIN_INFO_JUNGLE_LOW ] = sound.SOUND_TYPE_WALK_JUNGLE

def get_sound(terrain , action ):

    if action == pawn.ACTION_MOVE:
        if terrain in TERRAIN_SOUND:
            return TERRAIN_SOUND[terrain]
    return None

def get_mask(terrain , action):
    if (terrain , 0) in TERRAIN_MASK:
        use_64 = 1 if action == pawn.ACTION_ATTACK else 0

        return TERRAIN_MASK[ (terrain , use_64) ]
    return None

class Map:


    def __init__(self, width=DEFAULT_MAP_WIDTH, height=DEFAULT_MAP_HEIGHT, name=DEFAULT_MAP_NAME):
        self.map_width = width
        self.map_height = height
        self.map_name = name
        self.map_terrain_info = []
        self.map_collision_info = []
        self.tile_row_number = self.map_height / DEFAULT_MAP_TILE_HEIGHT
        self.tile_col_number = self.map_width / DEFAULT_MAP_TILE_WIDTH
        self.map_image_file = image.load(name + ".bmp")
        self.load()

    def load(self):

        self.map_terrain_info = [[-1 for i in range(self.tile_col_number)] for j in range(self.tile_row_number)]
        self.map_collision_info = [[0 for i in range(self.tile_col_number)] for j in range(self.tile_row_number)]
        self.map_block_info = [[0 for i in range(self.tile_col_number)] for j in range(self.tile_row_number)]
        file = open(self.map_name + '.map', 'r')


        for r, row in enumerate(file):
            row = row.strip()
            for c in range(0, len(row), 2):
                try:
                    idx = int(row[c:c + 2])
                    if r < 15:
                        self.map_collision_info[r][c/2] = COLLISION_INFO_EMPTY
                        self.map_terrain_info[r][c/2] = idx
                    else:

                        self.map_block_info[r-15][c/2] = idx

                except:
                    continue


    def init_terrain_mask(self):
        map_image_cache[TERRAIN_MASK_JUNGLE_HIGH_48] = image.load("jungle_high_48.bmp").convert_alpha()
        map_image_cache[TERRAIN_MASK_JUNGLE_HIGH_48].set_colorkey((247,0,255))
        map_image_cache[TERRAIN_MASK_JUNGLE_HIGH_64] = image.load("jungle_high_64.bmp").convert_alpha()
        map_image_cache[TERRAIN_MASK_JUNGLE_HIGH_64].set_colorkey((247,0,255))

        map_image_cache[TERRAIN_MASK_JUNGLE_LOW_48] = image.load("jungle_low_48.bmp").convert_alpha()
        map_image_cache[TERRAIN_MASK_JUNGLE_LOW_48].set_colorkey((247,0,255))
        map_image_cache[TERRAIN_MASK_JUNGLE_LOW_64] = image.load("jungle_low_64.bmp").convert_alpha()
        map_image_cache[TERRAIN_MASK_JUNGLE_LOW_64].set_colorkey((247,0,255))

    def render(self):
        render_queue.append((2, self.map_image_file, (0,0)))
