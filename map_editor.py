# -*- coding: utf-8 -*-

#Import Modules
import os, pygame
from pygame.locals import *
from battle_map import *
from gui import *
from control import *
from sound import *
from logic import  *
import config
import sprite
import sys

sys.stdout = open("map-editor-log.txt" , "w")

def main():

#Initialize Everything

    pygame.init()
    pygame.display.set_caption((u'地图编辑器').encode('utf-8'))


    current_map = Map(name='map-1')
    sprite.Sprite.current_map = current_map
    screen = pygame.display.set_mode((current_map.map_width + 256, current_map.map_height))
    current_map.init_terrain_mask()


    yun = pawn.Pawn((0,0) ,pawn.DIRECTION_RIGHT , pawn.ARM_MELEE , pawn.MOBILE_MOUNT, hero_pool[0] , 1 , True)
    lvbu = pawn.Pawn((4,5) , pawn.DIRECTION_LEFT ,  pawn.ARM_MELEE , pawn.MOBILE_MOUNT, hero_pool[1] , 0 , True)
    zhouyu = pawn.Pawn((3,4) , pawn.DIRECTION_LEFT ,  pawn.ARM_MELEE , pawn.MOBILE_WALK, hero_pool[2] , 0 , True)
    pawn.action_turn = 1
    lvbu.action_turn = 0

    pawn_list = [yun , lvbu , zhouyu]

    selected_pawn = None
    control = Control(current_map)
    gui_controller.side_menu(selected_pawn)
    logic_controller = Logic(current_map , pawn_list)

    logic_controller.process_action_queue()

    while 1:

        config.clock = pygame.time.Clock().tick(config.FPS)

        current_map.render()
        logic_controller.update_terrain_mask()
        logic_controller.update_pawn_status()
        for p in pawn_list:
            if p.hero.alive:
                p.render()
            else:
                pawn_list.remove(p)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            target = gui_controller.get_grid_on_mouse()
            target_type = logic_controller.get_target_type(0 , target)
            control.process_event(event , target_type)

        if control.status == Control.CONTROL_STATUS_PROCESS_PLAYER_ACTION:
            if target:
                logic_controller.process_player_action(selected_pawn,target)
                control.status = Control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION

        elif control.status == control.CONTROL_STATUS_PAWN_SELECTED:
            if selected_pawn:
                gui_controller.side_menu(selected_pawn)
                valid_move = logic_controller.get_valid_move(selected_pawn)
                gui_controller.highlight_valid_move(valid_move)
                valid_target = logic_controller.get_valid_target(selected_pawn)
                gui_controller.highlight_valid_target(valid_target)
                attack_range = logic_controller.get_attack_range_grids(selected_pawn)
                gui_controller.draw_attack_frame_on_target(attack_range)
        elif control.status == control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION:
            if not logic_controller.process_action_queue():
                control.status = control.CONTROL_STATUS_IDlE
        else:
            selected_pawn = gui_controller.get_selected_pawn(pawn_list)

        gui_controller.draw_selection_frame()
        gui_controller.draw_border()

        render_queue.sort()

        while render_queue:
            top = render_queue.pop()
            if top[1] and top[2]:
                screen.blit(top[1] , top[2])

        pygame.display.update()

if __name__ == '__main__': main()
