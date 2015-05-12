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
import mission
import sys
import copy


def main():
    #Initialize Everything
    sound_controler = Sound()

    db = database.Database('localhost', 27017)

    pygame.init()
    pygame.display.set_caption((u'武将大乱斗').encode('utf-8'))

    hero.initiate_hero_pool(db)

    current_map = Map(name='map-1',team_count=3)
    sprite.Sprite.current_map = current_map
    screen = pygame.display.set_mode((current_map.map_width + 256, current_map.map_height))
    current_map.init_terrain_mask()
    skill.load_skill_images()

    gui_controller = gui.Gui(current_map, screen)

    current_mission = mission.test_mission

    #yun = pawn.Pawn((9,6) ,pawn.DIRECTION_RIGHT , pawn.ARM_MELEE , pawn.MOBILE_MOUNT, hero.hero_pool[0] , 0 , True , False)
    #lvbu = pawn.Pawn((6,5) , pawn.DIRECTION_LEFT ,  pawn.ARM_MELEE , pawn.MOBILE_MOUNT, hero.hero_pool[1] , 1 , False , True)
    #zhouyu = pawn.Pawn((6,6) , pawn.DIRECTION_LEFT ,  pawn.ARM_MELEE , pawn.MOBILE_WALK, hero.hero_pool[2] , 1 , False , True)
    #guanyu = pawn.Pawn((8,9) , pawn.DIRECTION_LEFT ,  pawn.ARM_MELEE , pawn.MOBILE_MOUNT, hero.hero_pool[3] , 0 , True , False)
    #weiwen = pawn.Pawn((10,9) , pawn.DIRECTION_LEFT ,  pawn.ARM_MELEE , pawn.MOBILE_WALK, hero.hero_pool[4] , 0 , True , False)

    #yun.action_turn = 0
    #lvbu.action_turn = 1
    #zhouyu.action_turn = 1
    #guanyu.action_turn = 0
    #
    #pawn_list = [yun , lvbu , zhouyu  , guanyu , weiwen]
    pawn_list = []
    for roster in current_mission.player_roster:
        p = pawn.Pawn(roster[1], roster[2], roster[3], roster[4], hero.hero_pool[roster[0]], roster[5], 0, roster[6],
                      roster[7])
        pawn_list.append(p)
    for roster in current_mission.friend_roster:
        h = copy.copy(hero.hero_pool[roster[0]])
        p = pawn.Pawn(roster[1], roster[2], roster[3], roster[4], h, roster[5], 1, roster[6], roster[7])
        p.ai_group = roster[9][0]
        p.is_leader = roster[9][1]
        p.ai_strategy = roster[10]
        pawn_list.append(p)
    for roster in current_mission.enemy_roster:
        h = copy.copy(hero.hero_pool[roster[0]])
        p = pawn.Pawn(roster[1], roster[2], roster[3], roster[4], h, roster[5], 2, roster[6], roster[7])
        p.persuade = roster[8]
        p.ai_group = roster[9][0]
        p.is_leader = roster[9][1]
        p.ai_strategy = roster[10]
        pawn_list.append(p)

    selected_pawn = None
    control = Control(current_map)
    gui_controller.side_menu(selected_pawn)
    logic_controller = logic.Logic(current_map, pawn_list)
    fight_logic_controller = fight_logic.FightLogic(current_map, pawn_list)
    skill.fight_logic_controller = fight_logic_controller

    logic_controller.process_action_queue()
    logic_controller.turn_team = 0
    logic.control = control
    logic.fight_logic_controller = fight_logic_controller

    ai.logic_controller = logic_controller
    gui.logic_controller = logic_controller
    info_before_move = (None, None, None)

    ai_controller = ai.AI(pawn_list)

    logic_controller.new_turn()

    current_round = 1
    last_turn_team = 0

    while True:

        config.clock = pygame.time.Clock().tick(config.FPS)

        current_map.render()

        logic_controller.update_terrain_mask()
        skill.fight_logic_controller.trigger_passive_skills_realtime()
        logic_controller.update_pawn_status()

        for p in logic_controller.pawn_list:
            if p.hero.alive:
                p.render()
            else:
                pawn_list.remove(p)


        #AI Processing
        if logic_controller.turn_team != 0:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return

            flag = False

            if control.status == control.CONTROL_STATUS_IDlE:
                ai_action = ai_controller.get_next_ai() 
                if ai_action != None:
                    flag = True
                    ai_controller.take_action( ai_action )
                    control.status = control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION
            elif control.status != control.CONTROL_STATUS_TURN_FINISHING:
                control.status = control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION 
                flag = True
            
            if not flag:
                control.status = control.CONTROL_STATUS_TURN_FINISHING
                
            if control.status == control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION:
                if not logic_controller.process_action_queue():
                    control.status = control.CONTROL_STATUS_IDlE
        else:

            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        if debug and selected_pawn:
                            logger(  selected_pawn.status_info() )
                            logger( logic_controller.target_info(selected_pawn) )

                if control.status == control.CONTROL_STATUS_MENU_ATTACK_CHOOSE:
                    target = gui_controller.get_grid_on_mouse()
                    target_type = logic_controller.is_valid_target(selected_pawn, target, pawn.ACTION_ATTACK, )
                elif control.status == control.CONTROL_STATUS_MENU_OPENED:
                    target_type = gui_controller.is_mouse_on_menu()
                else:
                    target = gui_controller.get_grid_on_mouse()
                    target_type = logic_controller.get_target_type(0, target)
                if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
                    control.event_queue.append((event, target_type))

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
                    logic_controller.current_map.map_collision_info[selected_pawn.position[0]][
                        selected_pawn.position[1]] = battle_map.COLLISION_INFO_EMPTY

                    selected_pawn.position = info_before_move[0]
                    selected_pawn.direction = info_before_move[1]
                    selected_pawn.move_count = info_before_move[2]
                    selected_pawn.render_position = selected_pawn.get_render_position(selected_pawn.position)
                    logic_controller.current_map.map_collision_info[selected_pawn.position[0]][
                        selected_pawn.position[1]] = battle_map.COLLISION_INFO_OCCUPIED

                control.status = control.CONTROL_STATUS_IDlE


            elif control.status == control.CONTROL_STATUS_MENU_ITEM_SELECTED:
                control.status = control.get_control_status_by_menu_order(gui_controller.selected_menu_item)
                logic_controller.process_menu_order(selected_pawn, gui_controller.selected_menu_item)

            elif control.status == Control.CONTROL_STATUS_PROCESS_PLAYER_ACTION:

                if target and selected_pawn:
                    order = None
                    if gui_controller.selected_menu_item:
                        order = gui_controller.selected_menu_item.order
                    logic_controller.process_player_action(selected_pawn, target , order)
                    control.status = Control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION

            elif control.status == control.CONTROL_STATUS_PAWN_SELECTED:

                if selected_pawn:
                    info_before_move = (selected_pawn.position, selected_pawn.direction , selected_pawn.move_count)
                    valid_move = logic_controller.get_valid_move(selected_pawn)

                    gui_controller.highlight_valid_move(valid_move, selected_pawn.controllable)
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
            elif control.status == control.CONTROL_STATUS_MENU_PERSUADE_CHOOSE:
                valid_target = logic_controller.get_persuade_target(selected_pawn)
                gui_controller.highlight_valid_target(valid_target)
            else:
                selected_pawn = gui_controller.get_selected_pawn(pawn_list)

        if control.status == control.CONTROL_STATUS_TURN_FINISHING:
            if (gui_controller.switch_turn(logic_controller.turn_team)):
                logic_controller.end_turn()
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
                screen.blit(top[1], top[2])

        gui_controller.draw_border()

        pygame.display.update()


if __name__ == '__main__': main()
