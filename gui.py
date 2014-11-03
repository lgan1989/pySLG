# -*- coding: utf-8 -*-

import pygame
import battle_map
import skill
import config
import logic
from resource import face_image_cache , skill_image
from renderer import render_queue

ATTRIBUTE_HEALTH = 0
ATTRIBUTE_ATTACK = 1
ATTRIBUTE_DEFENCE = 2
ATTRIBUTE_SPEED = 3
ATTRIBUTE_STRATEGY = 4
ATTRIBUTE_SKILL = 5

logic_controller = None

class Menu:

    MENU_BACKGROUND_COLOC = (44, 62, 80)

    class MenuItem:


        def __init__(self , gui , position , size  , text , order):
            self.size = size
            self.position = position
            self.text = text
            self.order = order
            self.gui = gui
        def display(self):
            rect = pygame.Surface(self.size)
            rect.set_alpha(255)
            rect.fill(Menu.MENU_BACKGROUND_COLOC)
            render_queue.append( (-11 , rect , self.position) )
            text = self.gui.in_game_menu_font.render(self.text , 1 , (240,240,240))
            render_queue.append((-13,text , (self.position[0] + self.size[0]/2 - text.get_width()/2 , self.position[1] +10) ))
        def selected(self, selecting = False):
            rect = pygame.Surface(self.size)
            rect.set_alpha(255)
            if selecting:
                rect.fill((255, 57, 43))
            else:
                rect.fill((162, 57, 43))
            render_queue.append( (-12 , rect , self.position) )
            text = self.gui.in_game_menu_font.render(self.text , 1 , (240,240,240))
            render_queue.append((-13,text , (self.position[0] + self.size[0]/2 - text.get_width()/2 , self.position[1] +10) ))

    def __init__(self , gui, position , size, menu_items):
        self.gui = gui
        self.size = size
        x = position[0]
        y = position[1]
        if x + size[0] > logic_controller.current_map.map_width:
            x = logic_controller.current_map.map_width - size[0]
        if y + size[1] > logic_controller.current_map.map_height:
            y = logic_controller.current_map.map_height - size[1]

        self.position = (x,y)
        self.menu_items = []
        for idx , item in enumerate( menu_items ):
            item_position = (x  , y + idx * 30)

            self.menu_items.append( Menu.MenuItem(gui , item_position  ,(150 , 30)  , item[0] , item[1] ) )

    def inside_rect(self, point , rect):

        if rect[0] < point[0] < rect[0] + rect[2] and rect[1] < point[1] < rect[1] + rect[3]:
            return True
        return False

    def get_selected_item(self, selecting = False):
        mouse_position = pygame.mouse.get_pos()
        for item in self.menu_items:

            if self.inside_rect( mouse_position , item.position + item.size ):
                item.selected(selecting)
                return item
        return None


    def display(self , selecting = False):

        height = 30 * len(self.menu_items)
        rect = pygame.Surface((150 , height))
        rect.set_alpha(255)
        rect.fill((127, 140, 141))
        render_queue.append( (-10,rect,self.position) )
        for item in self.menu_items:
            item.display()
        self.gui.selected_menu_item = self.get_selected_item(selecting)




class Gui:

    def __init__(self, current_map, screen):

        self.main_window_row_number = current_map.tile_row_number
        self.main_window_col_number = current_map.tile_col_number

        self.face_frame = self.get_image_source("image/gui/face_frame.bmp", (51, 51, 51))
        self.face_border_position = (current_map.map_width, 0)
        self.face_position = (current_map.map_width + 8, 8)
        self.lvl_icon_position = (current_map.map_width + 20, 315)
        self.lvl_font = pygame.font.Font('font/bell.ttf', 27)
        self.quote_font = pygame.font.Font('font/simkai.ttf', 16)
        self.quote_position = (current_map.map_width + 50, 280)
        self.side_menu_height = current_map.map_height
        self.side_menu_background = pygame.image.load("image/gui/menu_bg.bmp").convert()
        self.side_menu_font = pygame.font.Font('font/shuti.ttf', 18)
        self.switch_turn_font = pygame.font.Font('font/simkai.ttf', 50)
        self.in_game_menu_font = pygame.font.Font('font/simkai.ttf', 15)

        self.side_menu_attribute_health_postion = (current_map.map_width + 30, 400)


        self.attribute_health_icon = self.get_image_source("image/gui/health.bmp" , (247,0,255))
        self.attribute_attack_icon = self.get_image_source("image/gui/attack.bmp", (247, 0, 255))
        self.attribute_defence_icon = self.get_image_source("image/gui/defence.bmp", (247, 0, 255))
        self.attribute_speed_icon = self.get_image_source("image/gui/speed.bmp", (247, 0, 255))
        self.attribute_strategy_icon = self.get_image_source("image/gui/strategy.bmp", (247, 0, 255))
        self.attribute_skill_icon = self.get_image_source("image/gui/skill.bmp", (247, 0, 255))

        self.attributes_icon_set = {ATTRIBUTE_HEALTH: self.attribute_health_icon,
                                    ATTRIBUTE_ATTACK: self.attribute_attack_icon,
                                    ATTRIBUTE_DEFENCE: self.attribute_defence_icon,
                                    ATTRIBUTE_SPEED: self.attribute_speed_icon,
                                    ATTRIBUTE_STRATEGY: self.attribute_strategy_icon,
                                    ATTRIBUTE_SKILL:self.attribute_skill_icon}
        self.attributes_icon_pos = {ATTRIBUTE_HEALTH: (current_map.map_width + 50 ,390),
                                    ATTRIBUTE_ATTACK: (current_map.map_width + 50, 450),
                                    ATTRIBUTE_DEFENCE: (current_map.map_width + 170, 450),
                                    ATTRIBUTE_SPEED: (current_map.map_width + 50, 510),
                                    ATTRIBUTE_STRATEGY: (current_map.map_width + 170, 510),
                                    ATTRIBUTE_SKILL: (current_map.map_width + 50, 570)
        }

        self.selection_frame = self.get_image_source("image/gui/selection.bmp", (247, 0, 255))
        self.attack_frame = self.get_image_source("image/gui/attack_frame.bmp", (247, 0, 255))

        self.current_map = current_map
        self.menu_items = []
        self.menu = None
        self.selected_menu_item = None
        self.cycletime = 0
        self.screen = screen
        self.turn_switch_wait = 0

    def get_image_source(self, resource, colorkey):
        ret = pygame.image.load(resource).convert()
        ret.set_colorkey(colorkey)
        return ret

    def draw_quote(self, quote):
        text = self.quote_font.render(quote, 1, (10, 10, 10))
        render_queue.append((0, text, self.quote_position))



    def draw_health_bar(self, current_health, max_health):
        if current_health * 2 >= max_health:
            G = 255
            R = (255 * (max_health - current_health) * 2) / max_health
        else:
            R = 255
            G = (255 * (current_health) * 2 / max_health)

        R = max(0 , R)
        G = max(0 , G)
        B = 0

        rect = pygame.Surface((max(1,100 * current_health / max_health), 20))
        rect.fill((R, G, B))

        if current_health > 0:
            render_queue.append((
            0, rect, (self.side_menu_attribute_health_postion[0] + 40, self.side_menu_attribute_health_postion[1] + 3)))
        text = self.side_menu_font.render(str(current_health) + '/' + str(max_health), 1, (10, 10, 10))

        render_queue.append((0, text, (self.side_menu_attribute_health_postion[0] + 45 + rect.get_width(),
                                       self.side_menu_attribute_health_postion[1] + 5)))

    def draw_attribute_bar(self, type, value , buff_value):

        text = self.side_menu_font.render( str(value) , 1 , (10,10,10) )
        pos = self.attributes_icon_pos[type]
        buff_text = None
        if buff_value > 0:
            buff_text = self.side_menu_font.render( '(+' + str(buff_value) + ')' , 1 , (1,100,1))
        elif buff_value < 0:
            buff_text = self.side_menu_font.render( ' ( - ' + str(buff_value) + ')', 1 , (255,10,10))
        render_queue.append((0, text, (pos[0] + 14, pos[1] + 10)))
        if buff_text:
            render_queue.append((0, buff_text, (pos[0] + 14  , pos[1] + 10 + text.get_height() + 3)))


    def draw_level(self, lvl):
        text = self.lvl_font.render(str(lvl), 1, (200, 230, 190))
        render_queue.append((0, text, self.lvl_icon_position))

    def get_selected_pawn(self, pawn_list):
        pos = self.get_grid_on_mouse()
        for pawn in pawn_list:
            if pawn.position == pos:
                return pawn
        return None

    def draw_selection_frame(self):
        grid = self.get_grid_on_mouse()
        if 0 <= grid[0] < self.main_window_row_number and 0 <= grid[1] < self.main_window_col_number:
            render_queue.append((-1, self.selection_frame, self.get_grid_render_position(grid)))


    def get_grid_on_mouse(self):
        mouse_position = pygame.mouse.get_pos()
        return mouse_position[1] / battle_map.DEFAULT_MAP_TILE_HEIGHT, mouse_position[0] / battle_map.DEFAULT_MAP_TILE_WIDTH

    def get_grid_render_position(self, grid):
        return grid[1] * battle_map.DEFAULT_MAP_TILE_WIDTH, grid[0] * battle_map.DEFAULT_MAP_TILE_HEIGHT


    def draw_attack_frame_on_target(self, grids):
        if not grids:
            return
        for grid in grids:
            render_queue.append((0, self.attack_frame, self.get_grid_render_position(grid)))

    def highlight_taunting_target(self , grids):
        if not grids:
            return

        taunt_image = skill_image[skill.SKILL_IMAGE_TAUNT]
        self.cycletime += config.clock
        if self.cycletime < 350:
            for grid in grids:
                render_queue.append((-1, taunt_image , self.get_grid_render_position(grid)))
        elif self.cycletime > 700:
            self.cycletime = 0

    def highlight_valid_target(self, grids):
        if not grids:
            return
        for grid in grids:
            self.highlight_grid(grid, (255, 50, 50), 240)

    def highlight_valid_move(self, grids , controllable):
        if not grids:
            return
        for grid in grids:
            if controllable:
                self.highlight_grid(grid, (50, 50, 255), 200)
            else:
                self.highlight_grid(grid, (50, 255, 50), 200)

    def highlight_grid(self, grid, color, alpha):
        rect = pygame.Surface((48, 48))
        rect.set_alpha(alpha)
        rect.fill(color)
        render_queue.append((1, rect, self.get_grid_render_position(grid)))


    def side_menu_attributes(self, pawn_info):

        hero = pawn_info.hero
        render_queue.append((0, self.attribute_health_icon, (
            self.attributes_icon_pos[ATTRIBUTE_HEALTH][0] - 40,
            self.attributes_icon_pos[ATTRIBUTE_HEALTH][1])))

        self.draw_health_bar(hero.current_health, hero.max_health)

        render_queue.append((0, self.attribute_attack_icon, (
            self.attributes_icon_pos[ATTRIBUTE_ATTACK][0] - 40,
            self.attributes_icon_pos[ATTRIBUTE_ATTACK][1])))

        self.draw_attribute_bar(ATTRIBUTE_ATTACK, hero.attack , hero.attack_buff)


        render_queue.append((0, self.attribute_defence_icon, (
            self.attributes_icon_pos[ATTRIBUTE_DEFENCE][0] - 40,
            self.attributes_icon_pos[ATTRIBUTE_DEFENCE][1])))

        self.draw_attribute_bar(ATTRIBUTE_DEFENCE, hero.defence , hero.defence_buff)


        render_queue.append((0, self.attribute_speed_icon, (
            self.attributes_icon_pos[ATTRIBUTE_SPEED][0] - 40,
            self.attributes_icon_pos[ATTRIBUTE_SPEED][1])))
        self.draw_attribute_bar(ATTRIBUTE_SPEED, hero.speed , hero.speed_buff)


        render_queue.append((0, self.attribute_strategy_icon, (
            self.attributes_icon_pos[ATTRIBUTE_STRATEGY][0] - 40,
            self.attributes_icon_pos[ATTRIBUTE_STRATEGY][1])))

        self.draw_attribute_bar(ATTRIBUTE_STRATEGY, hero.strategy , hero.strategy_buff)


        render_queue.append((0, self.attribute_skill_icon, (
            self.attributes_icon_pos[ATTRIBUTE_SKILL][0] - 40,
            self.attributes_icon_pos[ATTRIBUTE_SKILL][1])))

        margin = 0
        for skill in pawn_info.hero.skills:
            text = self.side_menu_font.render(skill.name , 1 , (10,10,10))
            render_queue.append((0 , text , (
                self.attributes_icon_pos[ATTRIBUTE_SKILL][0] ,
                self.attributes_icon_pos[ATTRIBUTE_SKILL][1] + margin)))
            margin = self.side_menu_font.get_height()

    def draw_border(self):
        pygame.draw.rect(self.screen, ((149, 165, 166)),
                         pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height()), 2)
        pygame.draw.rect(self.screen, ((149, 165, 166)),
                         pygame.Rect(self.face_border_position[0], self.face_border_position[1], 256, 720), 2)

    def side_menu(self, pawn_info):
        render_queue.append(
            (3, self.side_menu_background, (self.face_border_position[0], self.face_border_position[1])))
        if pawn_info:

            if pawn_info.hero.health_decrease and pawn_info.hero.current_health > 0:
                pawn_info.hero.current_health -= 1
                pawn_info.hero.health_decrease -= 1
            render_queue.append((2, face_image_cache[pawn_info.face_resource_id], self.face_position))
            render_queue.append((1, self.face_frame, self.face_border_position))
            self.draw_level(pawn_info.hero.level)
            self.side_menu_attributes(pawn_info)
            self.draw_quote(pawn_info.hero.quote)

    def switch_turn(self, turn_team):
        rect = pygame.Surface((self.current_map.map_width, self.current_map.map_height))
        rect.set_alpha(150)
        if turn_team == 2:
            rect.fill((255,0,0))
        elif turn_team == 0:
            rect.fill((255,100,0))
        elif turn_team == 1:
            rect.fill((0,0,255))
        self.turn_switch_wait += config.clock
        if self.turn_switch_wait > 1000:
            self.turn_switch_wait = 0
            return True
        render_queue.append((-2 , rect , (0,0)))

        if turn_team == 2:
            text = self.switch_turn_font.render(u'我军回合', 1, (250, 250, 250))
        elif turn_team == 0:
            text = self.switch_turn_font.render(u'友军回合', 1, (250, 250, 250))
        elif turn_team == 1:
            text = self.switch_turn_font.render(u'敌军回合', 1, (250, 250, 250))
        render_queue.append((-3 , text , (self.current_map.map_width/2 - text.get_width()/2 , self.current_map.map_height/2 - text.get_height())))
        return False

    def build_menu(self, pawn_info):
        if not pawn_info:
            #build default menu
            menu_items = [(u'回合结束' , logic.MENU_ORDER_END_TURN) , (u'取消' , logic.MENU_ORDER_CANCEL)]
            size = (150 , len(menu_items) * 30)
            self.menu = Menu(self , pygame.mouse.get_pos() ,  size , menu_items)
        else:
            menu_items = []
            valid_target = logic_controller.get_valid_target(pawn_info)

            persuade_target = logic_controller.get_persuade_target(pawn_info)

            if persuade_target and pawn_info.can_attack:
                menu_items.append((u'劝降', logic.MENU_ORDER_PERSUADE) )
            if valid_target and pawn_info.can_attack:
                menu_items.append( (u'攻击' , logic.MENU_ORDER_ATTACK) )

            menu_items.append((u'待命' , logic.MENU_ORDER_STAND_BY))
            size = (150 , len(menu_items) * 30)
            self.menu = Menu(self, pawn_info.render_position , size , menu_items)

    def is_mouse_on_menu(self):
        if self.selected_menu_item:
            return logic.TARGET_TYPE_MENU_ITEM
        return logic.TARGET_TYPE_TILE



