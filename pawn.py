import pygame
from resource import sprite_image_cache , face_image_cache , sound_cache
import sprite
from battle_map import *
import font
import sound
import uuid


#pawn classes
ARM_MELEE = 1
ARM_RANGE = 2
ARM_SUPPORT = 3

ATTACK_RANGE = {}
ATTACK_RANGE[ARM_MELEE] = ((0,1),(0,-1),(-1,0),(1,0),(1,1) ,(1,-1),(-1,1),(-1,-1))
ATTACK_RANGE[ARM_RANGE] = ((1,1),(-1,-1),(1,-1),(-1,1),(2,0),(0,2),(-2,0),(0,-2))

MOBILE_WALK = 0
MOBILE_MOUNT = 1

DIRECTION_DOWN = 0
DIRECTION_LEFT = 1
DIRECTION_RIGHT = 2
DIRECTION_UP = 3

ACTION_STAND = 0
ACTION_MOVE = 1
ACTION_ATTACK = 2
ACTION_PARRY = 3
ACTION_ATTACKED = 4
ACTION_DYING = 5
ACTION_PROCESSING = 6



D = ((1, 0), (0, -1), (0, 1), (-1, 0))
GET_D = {D[0]: DIRECTION_DOWN, D[1]: DIRECTION_LEFT, D[2]: DIRECTION_RIGHT, D[3]: DIRECTION_UP}

class Pawn:



    def __init__(self, spawn_position=(0, 0), direction=0 , arm_type=ARM_MELEE , mobile_type=MOBILE_WALK, hero=None , team = 0 , turn_team=0, controllable=True, has_ai = False):
        self.pawn_class = arm_type
        self.mobility = mobile_type
        self.direction = direction
        self.action = ACTION_STAND
        self.position = spawn_position
        self.render_position = None
        self.attacking = 0
        self.parrying = 0
        self.attackeding = 0
        self.action_queue = []
        self.sprite_stand = None
        self.sprite_move = None
        self.sprite_attack = None
        self.sprite_parry = None
        self.sprite_attacked = None
        self.sprite_weak = None
        self.sprite_dying = None
        self.sprite_finished = None
        self.special_render_item = None
        self.move_resource_id = uuid.uuid1()
        self.attack_resource_id = uuid.uuid1()
        self.spec_resource_id = uuid.uuid1()
        self.face_resource_id = uuid.uuid1()
        self.map_tile = None
        self.in_grid = True
        self.hero = hero
        self.hero.parent_pawn = self
        self.turn_finished = False
        self.action_started = False
        self.has_ai = has_ai


        #fight logic
        self.team = team
        self.turn_team = turn_team
        self.controllable = controllable
        self.range = ATTACK_RANGE[self.pawn_class]
        self.action_turn = True

        #for skill taunt
        self.taunted_to = []

        #for skill move_after_fight
        self.move_after_fight = 0
        self.can_attack = True

        self.can_be_attacked = True
        self.can_be_targeted = True


        #for ai
        self.next_move = None
        self.ai_status = 0

        self.load()

    def load(self):
        #assign resource id
        if self.face_resource_id not in face_image_cache:
            face_image_cache[self.face_resource_id] = pygame.image.load("image/face/" + str(self.hero.face_id) + ".jpg")

        if self.move_resource_id not in sprite_image_cache:
            sprite_image_cache[self.move_resource_id] = pygame.image.load("image/move/Unit_mov_" + str(self.hero.action_frame_id) + "-1.bmp")
        if self.attack_resource_id not in sprite_image_cache:
            sprite_image_cache[self.attack_resource_id] = pygame.image.load("image/attack/Unit_atk_" + str(self.hero.action_frame_id) + "-1.bmp")
        if self.spec_resource_id not in sprite_image_cache:
            sprite_image_cache[self.spec_resource_id] = pygame.image.load("image/spec/Unit_spc_" + str(self.hero.action_frame_id) + "-1.bmp")


        self.sprite_stand = sprite.Sprite( self.hero.cid , sprite_image_cache[self.move_resource_id].convert(), 11, 1, (247, 0, 255),
                                         sprite.ANIMATION_TYPE_STAND , sprite.INTERVAL_STAND , None , 0)

        move_sound = sound_cache[sound.SOUND_TYPE_WALK] if self.mobility == MOBILE_WALK else sound_cache[sound.SOUND_TYPE_WALK_MOUNT]
        self.sprite_move = sprite.Sprite(self.hero.cid ,sprite_image_cache[self.move_resource_id].convert(), 11, 1, (247, 0, 255),
                                         sprite.ANIMATION_TYPE_MOVE , sprite.INTERVAL_MOVE, move_sound , 0 , -1)
        self.sprite_attack = sprite.Sprite(self.hero.cid ,sprite_image_cache[self.attack_resource_id].convert(), 12, 1, (247, 0, 255),
                                           sprite.ANIMATION_TYPE_ATTACK , sprite.INTERVAL_ATTACK, sound_cache[sound.SOUND_TYPE_ATTACK] , 0 , 1)
        self.sprite_parry = sprite.Sprite(self.hero.cid ,sprite_image_cache[self.spec_resource_id].convert(), 5, 1, (247, 0, 255),
                                          sprite.ANIMATION_TYPE_PARRY , sprite.INTERVAL_PARRY, sound_cache[sound.SOUND_TYPE_ATTACK])
        self.sprite_attacked = sprite.Sprite(self.hero.cid ,sprite_image_cache[self.spec_resource_id].convert(), 5, 1, (247, 0, 255),
                                          sprite.ANIMATION_TYPE_ATTACKED , sprite.INTERVAL_ATTACKED, sound_cache[sound.SOUND_TYPE_HIT] ,350 , 1)
        self.sprite_weak = sprite.Sprite(self.hero.cid , sprite_image_cache[self.move_resource_id].convert(), 11 , 1 , (247,0,255),
                                         sprite.ANIMATION_TYPE_WEAK , sprite.INTERVAL_WEAK, None, 0)
        self.sprite_dying = sprite.Sprite(self.hero.cid , sprite_image_cache[self.move_resource_id].convert(), 11 , 1 , (247,0,255),
                                         sprite.ANIMATION_TYPE_DYING , sprite.INTERVAL_DYING, sound_cache[sound.SOUND_TYPE_RETREAT], 0 , 1)

        self.render_position = (
            self.position[1] * self.sprite_move.single_width, self.position[0] * self.sprite_move.single_height)

    def move_to_grid(self, grid):

        self.action = ACTION_MOVE
        diff = (grid[0] - self.position[0], grid[1] - self.position[1])
        if diff in GET_D:
            d = GET_D[diff]
            if d != self.direction:
                self.sprite_move.render_idx = 0
            self.move(d)
        grid_render_position = (
            grid[1] * self.sprite_move.single_width, grid[0] * self.sprite_move.single_height)
        if grid_render_position[0]  == self.render_position[0] and grid_render_position[1] == self.render_position[1]:
            self.position = grid
            self.in_grid = True

    def move(self, direction):
        self.direction = direction
        self.render_position = (
            self.render_position[0] + D[direction][1] * 12, self.render_position[1] + D[direction][0] * 12)
        self.in_grid = False
        if self.sprite_move.finished:
            self.sprite_move.finished = False

    def reset_position(self):
        self.action = ACTION_STAND
        self.render_position = (
            self.position[1] * self.sprite_move.single_width, self.position[0] * self.sprite_move.single_height)


    def died(self):
        if self.sprite_dying.finished:
            self.hero.alive = False
            return True
        return False

    def attack(self):

        if self.attacking == 1 and self.sprite_attack.finished:
            self.sprite_attack.finished = False
            self.reset_position()
            self.attacking = 0
            self.sprite_attack.cycletime = 0
            return False

        if self.attacking == 0:
            self.render_position = (
            self.position[1] * self.sprite_move.single_width - 8, self.position[0] * self.sprite_move.single_height - 8)
            self.attacking = 1
            self.sprite_attack.render_idx = 0
        return True

    def attacked(self):

        if self.attackeding == 1 and self.sprite_attacked.finished:
            self.attackeding = 0
            self.sprite_attacked.finished = False
            self.sprite_attacked.cycletime = 0
            return False
        if self.attackeding == 0:
            self.render_position = (
            self.position[1] * self.sprite_move.single_width , self.position[0] * self.sprite_move.single_height)
            self.attackeding = 1
            self.sprite_attacked.render_idx = 0

        return True

    def parry(self):

        if self.parrying == 1 and self.sprite_parry.finished:
            self.parrying = 0
            self.sprite_parry.finished = False
            return False
        if self.parrying == 0:
            self.render_position = (
            self.position[1] * self.sprite_move.single_width , self.position[0] * self.sprite_move.single_height)
            self.parrying = 1
            self.sprite_parry.render_idx = 0
        return True

    def draw_pawn_health_bar(self):

        current_health = self.hero.current_health
        max_health = self.hero.max_health
        decrease = self.hero.health_decrease

        delta = 5 if decrease > 5 else 1
        if decrease and self.hero.current_health > 0:
            self.hero.health_decrease -= delta
            self.hero.current_health -= delta

        if decrease:
            self.action = ACTION_PROCESSING
        elif self.action == ACTION_PROCESSING:
            self.action = ACTION_STAND

        if current_health * 2 >= max_health:
            G = 255
            R = (255 * (max_health - current_health) * 2) / max_health
        else:
            R = 255
            G = (255 * (current_health) * 2 / max_health)

        R = max(0 , R)
        G = max(0 , G)
        B = 0
        rect = pygame.Surface((max(1,42 * current_health / max_health), 5))
        rect.set_alpha(200)
        rect.fill((R, G, B))

        health_bar_position = self.render_position

        if self.action == ACTION_ATTACK:
            health_bar_position = (self.render_position[0] + 8 , self.render_position[1] + 8)

        text = font.font_cache[font.FONT_PAWN_HEALTH_BAR].render(str(current_health) + '/' + str(max_health), 1, (255, 255, 255))
        #render_queue.append((-1, text, (self.render_position[0] + 3, self.render_position[1]-20)))
        if current_health > 0:
            render_queue.append((-1 , rect ,(health_bar_position[0] + 3, health_bar_position[1]-5)) )

    def get_render_position(self, position):

        if self.action == ACTION_ATTACK:
            return (position[1] * self.sprite_move.single_width - 8, position[0] * self.sprite_move.single_height - 8)
        else:
            return (position[1] * self.sprite_move.single_width , position[0] * self.sprite_move.single_height)

    def render(self):


        if not self.turn_finished:
            if self.action == ACTION_STAND or self.action == ACTION_PROCESSING:
                if self.hero.weak:
                    self.sprite_weak.animate(self.direction , self.render_position , -1 , self.special_render_item)
                else:
                    self.sprite_stand.animate( self.direction, self.render_position , -1, self.special_render_item)
            elif self.action == ACTION_MOVE:
                self.sprite_move.animate(self.direction , self.render_position , -1, self.special_render_item)
            elif self.action == ACTION_ATTACK:
                self.sprite_attack.animate(self.direction, self.render_position , 1, self.special_render_item)
            elif self.action == ACTION_PARRY:
                self.sprite_parry.animate(self.direction, self.render_position , 1, self.special_render_item)
            elif self.action == ACTION_ATTACKED:
                self.sprite_attacked.animate(self.direction, self.render_position , 1, self.special_render_item)
            elif self.action == ACTION_DYING:
                self.sprite_dying.animate(self.direction , self.render_position , 1, self.special_render_item)
        else:

            if self.hero.weak:
                self.sprite_weak.animate(self.direction , self.render_position , -1 , self.special_render_item , 0 , True)
            else:
                self.sprite_move.animate(self.direction , self.render_position , -1 , self.special_render_item , 1 , True)

        self.draw_pawn_health_bar()