from pygame import transform,PixelArray,Color, image,BLEND_RGBA_MULT
import pawn
import config
from renderer import render_queue
from resource import  *
import array

KEY_COLOR = (247,0,255)

ANIMATION_TYPE_STAND = 0
ANIMATION_TYPE_MOVE = 1
ANIMATION_TYPE_ATTACK = 2
ANIMATION_TYPE_PARRY = 3
ANIMATION_TYPE_ATTACKED = 4
ANIMATION_TYPE_CHEER = 5
ANIMATION_TYPE_WEAK = 6
ANIMATION_TYPE_DYING = 7


INTERVAL_DEFAULT = (250,)
INTERVAL_STAND = (250,250)
INTERVAL_WEAK = (250,250)
INTERVAL_ATTACK = (300,50,50,150)
INTERVAL_PARRY = (250,250)
INTERVAL_MOVE = (40,40,40,40)
INTERVAL_ATTACKED = (150,150,300)
INTERVAL_DYING = (100,100,100,100)


class Sprite:

    current_map = None

    def __init__(self, cid = 0, sheet=None, row_num=4, col_num=1, color_key=(0, 0, 0), type=None , interval=INTERVAL_DEFAULT , sound=None , sound_play_time_offset=0 , sound_repeat=0):

        self.cid = cid
        self.sprite_sheet = sheet
        self.row_num = row_num
        self.col_num = col_num
        self.color_key = color_key
        self.render_idx = 0
        self.image_list = [[] for i in range(4)]
        self.sheet_width = sheet.get_width()
        self.sheet_height = sheet.get_height()
        self.single_width = self.sheet_width / col_num
        self.single_height = self.sheet_height / row_num
        self.interval = interval
        self.cycletime = 0
        self.repeat = 0
        self.finished = False
        self.clock = 0
        self.animation_type = type
        self.sound = sound
        self.sound_playing = self.sound
        self.sound_time_stamp = 0
        self.sound_play_time_offset = sound_play_time_offset
        self.sound_repeat = sound_repeat
        self.sound_played_counter = 0
        if sound:
            self.sound_length = int(sound.get_length() * 1000)
        else:
            self.sound_length = 0
        self.sound_play_start = 999999999

        raw_image_list = []
        for i in range(row_num):
            for j in range(col_num):
                raw_image_list.append(
                    self.sprite_sheet.subsurface(j * self.single_width, i * self.single_height, self.single_width,
                                                 self.single_height))
                raw_image_list[-1].set_colorkey(self.color_key)
                raw_image_list[-1] = raw_image_list[-1].convert_alpha()
                sprite_image_cache[str(self.cid) + '_ANIMATION_' + str(type)  + '_' + str(i * col_num + j) ] = raw_image_list[-1]

        self.arrange_image_list(raw_image_list, type)

    def get_image_cache_id(self, cid , type, frame):
        return str(cid) + '_ANIMATION_' + str(type) + '_' + str(frame)

    def arrange_image_list(self, raw_image_list, type=None):

        if type == ANIMATION_TYPE_STAND:
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[0])
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[1])

            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[2])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[3])

            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[4])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[5])

            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[4], True, False))
            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[5], True, False))

        elif type == ANIMATION_TYPE_MOVE:
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[0])
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[6])
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[1])
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[6])

            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[2])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[7])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[3])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[7])


            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[4])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[8])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[5])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[8])

            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[4], True, False))
            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[8], True, False))
            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[5], True, False))
            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[8], True, False))

        elif type == ANIMATION_TYPE_ATTACK:
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[0])
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[1])
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[2])
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[3])

            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[4])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[5])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[6])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[7])

            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[8])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[9])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[10])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[11])

            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[8], True, False))
            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[9], True, False))
            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[10], True, False))
            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[11], True, False))
        elif type == ANIMATION_TYPE_PARRY:
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[0])
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[0])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[1])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[1])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[2])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[2])
            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[2], True, False))
            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(raw_image_list[2], True, False))

        elif type == ANIMATION_TYPE_ATTACKED:
            self.image_list[pawn.DIRECTION_DOWN].append(sprite_image_cache[ self.get_image_cache_id(self.cid , ANIMATION_TYPE_STAND, 0) ])
            self.image_list[pawn.DIRECTION_DOWN].append(sprite_image_cache[ self.get_image_cache_id(self.cid , ANIMATION_TYPE_STAND, 1) ])
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[3])

            self.image_list[pawn.DIRECTION_UP].append(sprite_image_cache[ self.get_image_cache_id(self.cid , ANIMATION_TYPE_STAND, 2) ])
            self.image_list[pawn.DIRECTION_UP].append(sprite_image_cache[ self.get_image_cache_id(self.cid , ANIMATION_TYPE_STAND, 3) ])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[3])

            self.image_list[pawn.DIRECTION_LEFT].append(sprite_image_cache[ self.get_image_cache_id(self.cid , ANIMATION_TYPE_STAND, 4) ])
            self.image_list[pawn.DIRECTION_LEFT].append(sprite_image_cache[ self.get_image_cache_id(self.cid , ANIMATION_TYPE_STAND, 5) ])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[3])

            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip( sprite_image_cache[self.get_image_cache_id(self.cid , ANIMATION_TYPE_STAND, 4) ], True, False))
            self.image_list[pawn.DIRECTION_RIGHT].append(transform.flip(sprite_image_cache[ self.get_image_cache_id(self.cid , ANIMATION_TYPE_STAND, 5) ], True, False))
            self.image_list[pawn.DIRECTION_RIGHT].append(raw_image_list[3])

        elif type == ANIMATION_TYPE_CHEER:
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[0])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[0])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[0])
            self.image_list[pawn.DIRECTION_RIGHT].append(raw_image_list[0])
        elif type == ANIMATION_TYPE_WEAK:
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[9])
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[10])

            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[9])
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[10])

            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[9])
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[10])

            self.image_list[pawn.DIRECTION_RIGHT].append(raw_image_list[9])
            self.image_list[pawn.DIRECTION_RIGHT].append(raw_image_list[10])
        elif type == ANIMATION_TYPE_DYING:
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[9])
            self.image_list[pawn.DIRECTION_DOWN].append(None)
            self.image_list[pawn.DIRECTION_DOWN].append(raw_image_list[10])
            self.image_list[pawn.DIRECTION_DOWN].append(None)

            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[9])
            self.image_list[pawn.DIRECTION_UP].append(None)
            self.image_list[pawn.DIRECTION_UP].append(raw_image_list[10])
            self.image_list[pawn.DIRECTION_UP].append(None)

            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[9])
            self.image_list[pawn.DIRECTION_LEFT].append(None)
            self.image_list[pawn.DIRECTION_LEFT].append(raw_image_list[10])
            self.image_list[pawn.DIRECTION_LEFT].append(None)

            self.image_list[pawn.DIRECTION_RIGHT].append(raw_image_list[9])
            self.image_list[pawn.DIRECTION_RIGHT].append(None)
            self.image_list[pawn.DIRECTION_RIGHT].append(raw_image_list[10])
            self.image_list[pawn.DIRECTION_RIGHT].append(None)

    def play_animation_sound(self , sound):


        self.sound_time_stamp += config.clock
        if sound:
            sound_length = int( sound.get_length() * 1000 )

            sound_played_time = self.sound_time_stamp - self.sound_play_start

            if self.sound_repeat == -1:

                if (sound_played_time < 0 or sound_played_time > sound_length - 100) and self.sound_time_stamp > self.sound_play_time_offset:
                    sound.play()
                    self.sound_play_start = self.sound_time_stamp
            else:
                if (sound_played_time < 0 or sound_played_time > sound_length) and self.sound_time_stamp > self.sound_play_time_offset and self.sound_played_counter < self.sound_repeat:
                    sound.play()
                    self.sound_played_counter += 1
                    self.sound_play_start = self.sound_time_stamp


    def finish(self):

        self.sound_time_stamp = 0
        self.sound_played_counter = 0
        self.sound_play_start = 9999999999
        self.finished = True

    def animate(self, direction, position , repeat , special_render_item , render_single_frame = None , finished = False):



        if not self.finished and not finished :
            if special_render_item and 'sound' in special_render_item:
                if self.sound_playing != sound_cache[special_render_item['sound']]:
                    self.sound_play_start = 9999999999
                self.sound_playing = sound_cache[special_render_item['sound']]
                self.play_animation_sound(sound_cache[special_render_item['sound']])
            else:
                if self.sound_playing != self.sound:
                    self.sound_play_start = 9999999999
                self.sound_playing = self.sound
                self.play_animation_sound(self.sound)

        self.cycletime += config.clock

        animation_size = len(self.image_list[direction])
        if animation_size > 0:
            if self.cycletime > self.interval[self.render_idx]:
                self.cycletime = 0

                if self.render_idx + 1  == animation_size:
                    if repeat == -1:
                        self.render_idx = (self.render_idx + 1) % animation_size
                    elif self.repeat + 1 < repeat:
                        self.render_idx = (self.render_idx + 1) % animation_size
                        self.repeat += 1
                    elif self.repeat + 1 == repeat:
                        self.repeat = 0
                        self.finish()
                else:
                    self.render_idx = (self.render_idx + 1) % animation_size
            render_image = None
            if render_single_frame is not None:
                self.render_idx = render_single_frame
            if self.image_list[direction][self.render_idx] is not None:
                render_image = self.image_list[direction][self.render_idx].copy()
                if  finished:
                    tmp = image.load("image/mask/finished.bmp").convert()
                    render_image.blit(tmp , (0,0) , None , BLEND_RGBA_MULT)
                if special_render_item and 'mask' in special_render_item:
                    pixel_array = PixelArray(  map_image_cache[ special_render_item['mask'] ] )
                    render_image_pixel_array = PixelArray(render_image )

                    for i in range(len(render_image_pixel_array)):
                        for j in range(len(render_image_pixel_array[0])):
                            if pixel_array[i][j] != map_image_cache[ special_render_item['mask'] ].map_rgb(247,0,255):
                                render_image_pixel_array[i][j] = Color(247,0,255,0)
                    render_image = render_image.convert_alpha()
                    render_image.set_colorkey(self.color_key)
            render_queue.append( (0 , render_image , position) )





