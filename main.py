# -*- coding: utf-8 -*-

#Import Modules
import os, pygame
from pygame.locals import *
from battle_map import *
import skill
import pawn
import database
import fight_logic
import hero
import gui
from control import *
from sound import *
import logic
import config
import sprite
import ai
import sys

sys.stdout = open("log.txt" , "w")

def main():

    #Initialize Everything
    sound_controler = Sound()

    db = database.Database('localhost' , 27017)

    pygame.init()
    pygame.display.set_caption((u'武将大乱斗').encode('utf-8'))

    hero.initiate_hero_pool(db)

    current_map = Map(name='map-1')
    sprite.Sprite.current_map = current_map
    screen = pygame.display.set_mode((current_map.map_width + 256, current_map.map_height))
    current_map.init_terrain_mask()
    skill.load_skill_images()


    gui_controller = gui.Gui(current_map , screen)


    yun = pawn.Pawn((9,6) ,pawn.DIRECTION_RIGHT , pawn.ARM_MELEE , pawn.MOBILE_MOUNT, hero.hero_pool[0] , 0 , True , False)
    lvbu = pawn.Pawn((6,5) , pawn.DIRECTION_LEFT ,  pawn.ARM_MELEE , pawn.MOBILE_MOUNT, hero.hero_pool[1] , 1 , False , True)
    zhouyu = pawn.Pawn((6,6) , pawn.DIRECTION_LEFT ,  pawn.ARM_MELEE , pawn.MOBILE_WALK, hero.hero_pool[2] , 1 , False , True)
    guanyu = pawn.Pawn((8,9) , pawn.DIRECTION_LEFT ,  pawn.ARM_MELEE , pawn.MOBILE_MOUNT, hero.hero_pool[3] , 0 , True , False)

    yun.action_turn = 0
    lvbu.action_turn = 1
    zhouyu.action_turn = 1
    guanyu.action_turn = 0

    pawn_list = [yun , lvbu , zhouyu  , guanyu]

    selected_pawn = None
    control = Control(current_map)
    gui_controller.side_menu(selected_pawn)
    logic_controller = logic.Logic(current_map , pawn_list)
    fight_logic_controller = fight_logic.FightLogic(current_map , pawn_list)
    skill.fight_logic_controller = fight_logic_controller

    logic_controller.process_action_queue()
    logic_controller.turn_team = 0
    logic.control = control
    logic.fight_logic_controller = fight_logic_controller


    ai.logic_controller = logic_controller
    gui.logic_controller = logic_controller
    info_before_move = (None,None)

    ai_controller = ai.AI(pawn_list)

    logic_controller.new_turn()
    while 1:

        config.clock = pygame.time.Clock().tick(config.FPS)

        current_map.render()

        logic_controller.update_terrain_mask()
        logic_controller.update_pawn_status()
        skill.fight_logic_controller.trigger_passive_skills_realtime()



        for p in logic_controller.pawn_list:
            if p.hero.alive:
                p.render()
            else:
                pawn_list.remove(p)


        #FOR AI

        if logic_controller.turn_team == 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return



            flag = False
            for p in ai_controller.pawn_list:
                if not p.turn_finished and p.has_ai:
                    if control.status == control.CONTROL_STATUS_IDlE:
                        ai_controller.take_action(p)
                        if p and  p.next_move:
                            top = p.next_move[0]
                            p.next_move.pop(0)
                            action_type = top[0]
                            action_target = top[1]
                            if action_type == ai.AI_ACTION_MOVE:
                                logic_controller.process_player_action( p, action_target )
                                control.status = control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION
                            elif action_type == ai.AI_ACTION_ATTACK:
                                logic_controller.process_player_action( p, action_target )
                                control.status = control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION
                        print p.hero.name.encode('utf-8') , ' not finished' , p.next_move , 'control status: ' , control.status
                        flag = True
                        break
                    elif control.status == control.CONTROL_STATUS_PAWN_MOVED:
                        control.status = control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION
                    flag = True

            if not flag:
                control.status = control.CONTROL_STATUS_TURN_FINISHING

            if control.status == control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION:
                if not logic_controller.process_action_queue():

                    control.status = control.CONTROL_STATUS_IDlE

        #FOR AI

        else:

            for event in pygame.event.get():
                if event.type == QUIT:
                    return

                if control.status == control.CONTROL_STATUS_MENU_ATTACK_CHOOSE:
                    target = gui_controller.get_grid_on_mouse()
                    target_type = logic_controller.is_valid_target( selected_pawn , target , pawn.ACTION_ATTACK , )
                elif control.status == control.CONTROL_STATUS_MENU_OPENED:
                    target_type = gui_controller.is_mouse_on_menu()
                else:
                    target = gui_controller.get_grid_on_mouse()
                    target_type = logic_controller.get_target_type(0 , target)
                if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
                    control.event_queue.append( (event , target_type) )


            if control.status == control.CONTROL_STATUS_MENU_OPENED:

                #当鼠标在地图上右键, 打开菜单

                if gui_controller.menu is None:
                    gui_controller.build_menu(None)
                gui_controller.menu.display()
            elif control.status == control.CONTROL_STATUS_MENU_ITEM_SELECTING:
                gui_controller.menu.display(1)

            elif control.status == control.CONTROL_STATUS_PAWN_MOVED or control.status == control.CONTROL_STATUS_MENU_ATTACK_CHOOSE_CANCELED:
                gui_controller.build_menu(selected_pawn)
                control.status = control.CONTROL_STATUS_MENU_OPENED

            elif control.status == control.CONTROL_STATUS_MENU_CANCEL:

                #战斗菜单被取消后, 单位回到操作前的状态(包括位置,方向)

                gui_controller.menu = None
                if selected_pawn:
                    logic_controller.current_map.map_collision_info[selected_pawn.position[0]][selected_pawn.position[1]] = battle_map.COLLISION_INFO_EMPTY

                    selected_pawn.position = info_before_move[0]
                    selected_pawn.direction = info_before_move[1]
                    selected_pawn.render_position = selected_pawn.get_render_position(selected_pawn.position)
                    logic_controller.current_map.map_collision_info[selected_pawn.position[0]][selected_pawn.position[1]] = battle_map.COLLISION_INFO_OCCUPIED

                control.status = control.CONTROL_STATUS_IDlE


            elif control.status == control.CONTROL_STATUS_MENU_ITEM_SELECTED:
                control.status = control.get_control_status_by_menu_order(gui_controller.selected_menu_item)
                logic_controller.process_menu_order( selected_pawn ,  gui_controller.selected_menu_item )

            elif control.status == Control.CONTROL_STATUS_PROCESS_PLAYER_ACTION:
                if target and selected_pawn:
                    logic_controller.process_player_action(selected_pawn,target)
                    control.status = Control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION

            elif control.status == control.CONTROL_STATUS_PAWN_SELECTED:

                if selected_pawn:
                    info_before_move = (selected_pawn.position , selected_pawn.direction)
                    valid_move = logic_controller.get_valid_move(selected_pawn)
                    gui_controller.highlight_valid_move(valid_move , selected_pawn.team == logic_controller.turn_team )
                    attack_range = logic_controller.get_attack_range_grids(selected_pawn)
                    gui_controller.draw_attack_frame_on_target(attack_range)


            elif control.status == control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION:
                if not logic_controller.process_action_queue():
                    control.status = control.CONTROL_STATUS_IDlE
            elif control.status == control.CONTROL_STATUS_MENU_ATTACK_CHOOSE:
                valid_target = logic_controller.get_valid_target(selected_pawn)
                gui_controller.highlight_valid_target(valid_target)
                attack_range = logic_controller.get_attack_range_grids(selected_pawn)
                gui_controller.draw_attack_frame_on_target(attack_range)
                if selected_pawn.taunted_to:
                    gui_controller.highlight_taunting_target(valid_target)
            else:
                selected_pawn = gui_controller.get_selected_pawn(pawn_list)

        if control.status == control.CONTROL_STATUS_TURN_FINISHING:
            if (gui_controller.switch_turn(logic_controller.turn_team)):
                logic_controller.end_trun()
                control.status = control.CONTROL_STATUS_IDlE
        else:

            control.process_event()

        if control.status not in (
            control.CONTROL_STATUS_MENU_OPENED,
            control.CONTROL_STATUS_MENU_BUILD,
            control.CONTROL_STATUS_MENU_ITEM_SELECTING
        ):
            gui_controller.menu = None
            gui_controller.draw_selection_frame()
            gui_controller.side_menu(selected_pawn)

        render_queue.sort()

        while render_queue:
            top = render_queue.pop()
            if top[1] and top[2]:
                screen.blit(top[1] , top[2])

        gui_controller.draw_border()

        pygame.display.update()

if __name__ == '__main__': main()
