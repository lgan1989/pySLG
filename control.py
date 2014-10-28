import pawn
from logic import *
from pygame.constants import *
import pygame

class Control:

    CONTROL_STATUS_IDlE = 0
    CONTROL_STATUS_PAWN_SELECTED = 1
    CONTROL_STATUS_MAP_TILE_SELECTED = 2
    CONTROL_STATUS_MENU_BUILD = 3
    CONTROL_STATUS_MENU_OPENED = 4
    CONTROL_STATUS_PROCESS_PLAYER_ACTION = 5
    CONTROL_STATUS_PROCESSING_PLAYER_ACTION = 6
    CONTROL_STATUS_TURN_FINISHING = 7
    CONTROL_STATUS_TURN_FINISHED = 8


    CONTROL_STATUS_MENU_ITEM_SELECTING = 9
    CONTROL_STATUS_MENU_ITEM_SELECTED = 10

    CONTROL_STATUS_PAWN_MOVING = 11
    CONTROL_STATUS_PAWN_MOVED = 12

    CONTROL_STATUS_MENU_CANCEL = 13

    CONTROL_STATUS_MENU_ATTACK_CHOOSE = 14

    CONTROL_STATUS_MENU_ATTACK_CHOOSE_CANCELED = 15

    CONTROL_STATUS_MAX_SIZE = 32


    def __init__(self , current_map):
        self.status = self.CONTROL_STATUS_IDlE
        self.current_map = current_map
        self.status_automata =  [{} for _ in range(Control.CONTROL_STATUS_MAX_SIZE)]
        self.status_automata[Control.CONTROL_STATUS_PAWN_SELECTED][MOUSEBUTTONDOWN,1,TARGET_TYPE_TILE] = Control.CONTROL_STATUS_PROCESS_PLAYER_ACTION
        self.status_automata[Control.CONTROL_STATUS_PAWN_SELECTED][MOUSEBUTTONDOWN,1,TARGET_TYPE_FRIEND_PAWN] = Control.CONTROL_STATUS_PROCESS_PLAYER_ACTION

        self.status_automata[Control.CONTROL_STATUS_PAWN_SELECTED][MOUSEBUTTONDOWN,3,TARGET_TYPE_TILE] = Control.CONTROL_STATUS_IDlE
        self.status_automata[Control.CONTROL_STATUS_PAWN_SELECTED][MOUSEBUTTONDOWN,3,TARGET_TYPE_FRIEND_PAWN] = Control.CONTROL_STATUS_IDlE
        self.status_automata[Control.CONTROL_STATUS_PAWN_SELECTED][MOUSEBUTTONDOWN,3,TARGET_TYPE_ENEMY_PAWN] = Control.CONTROL_STATUS_IDlE

        self.status_automata[Control.CONTROL_STATUS_IDlE][MOUSEBUTTONDOWN,3,TARGET_TYPE_TILE] = Control.CONTROL_STATUS_MENU_OPENED

        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 1 , TARGET_TYPE_MENU_ITEM] = Control.CONTROL_STATUS_MENU_ITEM_SELECTING
        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 1 , TARGET_TYPE_MENU_ITEM] = Control.CONTROL_STATUS_MENU_ITEM_SELECTING
        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 1 , TARGET_TYPE_MENU_ITEM] = Control.CONTROL_STATUS_MENU_ITEM_SELECTING

        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 3 , TARGET_TYPE_MENU_ITEM] = Control.CONTROL_STATUS_MENU_ITEM_SELECTING
        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 3 , TARGET_TYPE_MENU_ITEM] = Control.CONTROL_STATUS_MENU_ITEM_SELECTING
        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 3 , TARGET_TYPE_MENU_ITEM] = Control.CONTROL_STATUS_MENU_ITEM_SELECTING

        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 1 , TARGET_TYPE_TILE] = Control.CONTROL_STATUS_MENU_CANCEL
        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 1 , TARGET_TYPE_ENEMY_PAWN] = Control.CONTROL_STATUS_MENU_CANCEL
        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 1 , TARGET_TYPE_FRIEND_PAWN] = Control.CONTROL_STATUS_MENU_CANCEL

        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 3 , TARGET_TYPE_TILE] = Control.CONTROL_STATUS_MENU_CANCEL
        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 3 , TARGET_TYPE_ENEMY_PAWN] = Control.CONTROL_STATUS_MENU_CANCEL
        self.status_automata[Control.CONTROL_STATUS_MENU_OPENED][MOUSEBUTTONDOWN , 3 , TARGET_TYPE_FRIEND_PAWN] = Control.CONTROL_STATUS_MENU_CANCEL

        self.status_automata[Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE][MOUSEBUTTONDOWN , 3 , TARGET_TYPE_TILE] = Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE_CANCELED
        self.status_automata[Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE][MOUSEBUTTONDOWN , 3 , TARGET_TYPE_ENEMY_PAWN] = Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE_CANCELED
        self.status_automata[Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE][MOUSEBUTTONDOWN , 3 , TARGET_TYPE_FRIEND_PAWN] = Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE_CANCELED
        self.status_automata[Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE][MOUSEBUTTONDOWN , 3 , TARGET_TYPE_INVALID] = Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE_CANCELED

        self.status_automata[Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE][MOUSEBUTTONDOWN , 1 , TARGET_TYPE_TILE] = Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE
        self.status_automata[Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE][MOUSEBUTTONDOWN , 1 , TARGET_TYPE_ENEMY_PAWN] = Control.CONTROL_STATUS_PROCESS_PLAYER_ACTION
        self.status_automata[Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE][MOUSEBUTTONDOWN , 1 , TARGET_TYPE_FRIEND_PAWN] = Control.CONTROL_STATUS_PROCESS_PLAYER_ACTION
        self.status_automata[Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE][MOUSEBUTTONDOWN , 1 , TARGET_TYPE_INVALID] = Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE

        self.status_automata[Control.CONTROL_STATUS_MENU_ITEM_SELECTING][MOUSEBUTTONUP , 0 , TARGET_TYPE_TILE] = Control.CONTROL_STATUS_MENU_ITEM_SELECTED
        self.status_automata[Control.CONTROL_STATUS_MENU_ITEM_SELECTING][MOUSEBUTTONUP , 0 , TARGET_TYPE_ENEMY_PAWN] = Control.CONTROL_STATUS_MENU_ITEM_SELECTED
        self.status_automata[Control.CONTROL_STATUS_MENU_ITEM_SELECTING][MOUSEBUTTONUP , 0 , TARGET_TYPE_FRIEND_PAWN] = Control.CONTROL_STATUS_MENU_ITEM_SELECTED


        self.status_automata[Control.CONTROL_STATUS_MAP_TILE_SELECTED][MOUSEBUTTONDOWN,1,TARGET_TYPE_FRIEND_PAWN] = Control.CONTROL_STATUS_PAWN_SELECTED
        self.status_automata[Control.CONTROL_STATUS_MAP_TILE_SELECTED][MOUSEBUTTONDOWN,1,TARGET_TYPE_ENEMY_PAWN] = Control.CONTROL_STATUS_PAWN_SELECTED
        self.status_automata[Control.CONTROL_STATUS_MAP_TILE_SELECTED][MOUSEBUTTONDOWN,1,TARGET_TYPE_TILE] = Control.CONTROL_STATUS_MAP_TILE_SELECTED

        self.status_automata[Control.CONTROL_STATUS_MAP_TILE_SELECTED][MOUSEBUTTONDOWN,3,TARGET_TYPE_FRIEND_PAWN] = Control.CONTROL_STATUS_IDlE
        self.status_automata[Control.CONTROL_STATUS_MAP_TILE_SELECTED][MOUSEBUTTONDOWN,3,TARGET_TYPE_ENEMY_PAWN] = Control.CONTROL_STATUS_IDlE
        self.status_automata[Control.CONTROL_STATUS_MAP_TILE_SELECTED][MOUSEBUTTONDOWN,3,TARGET_TYPE_TILE] = Control.CONTROL_STATUS_IDlE

        self.status_automata[Control.CONTROL_STATUS_IDlE][MOUSEBUTTONDOWN,1,TARGET_TYPE_FRIEND_PAWN] = Control.CONTROL_STATUS_PAWN_SELECTED
        self.status_automata[Control.CONTROL_STATUS_IDlE][MOUSEBUTTONDOWN,1,TARGET_TYPE_ENEMY_PAWN] = Control.CONTROL_STATUS_PAWN_SELECTED
        self.status_automata[Control.CONTROL_STATUS_IDlE][MOUSEBUTTONDOWN,1,TARGET_TYPE_TILE] = Control.CONTROL_STATUS_MAP_TILE_SELECTED


        self.status_automata[Control.CONTROL_STATUS_PROCESS_PLAYER_ACTION][MOUSEBUTTONUP,0,TARGET_TYPE_FRIEND_PAWN] = Control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION
        self.status_automata[Control.CONTROL_STATUS_PROCESS_PLAYER_ACTION][MOUSEBUTTONUP,0,TARGET_TYPE_ENEMY_PAWN] = Control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION
        self.status_automata[Control.CONTROL_STATUS_PROCESS_PLAYER_ACTION][MOUSEBUTTONUP,0,TARGET_TYPE_TILE] = Control.CONTROL_STATUS_PROCESSING_PLAYER_ACTION

        self.menu_open_position = None
        self.event_queue = []

    def process_event(self):

        if self.event_queue:
            event = self.event_queue[0][0]
            target_type = self.event_queue[0][1]
            type = event.type

            value = 0
            if type == MOUSEBUTTONDOWN:
                value = event.button
            elif type == KEYDOWN:
                value = event.key

            #if type == MOUSEBUTTONUP or type == MOUSEBUTTONDOWN:
             #   print  (type,value,target_type) , self.status_automata[self.status]
            if (type,value,target_type) in self.status_automata[self.status]:
                #print self.status , ' -> ' ,
                self.status = self.status_automata[self.status][type,value,target_type]

                if self.status == self.CONTROL_STATUS_MENU_OPENED:
                    self.menu_open_position = pygame.mouse.get_pos()

                #print self.status
            self.event_queue.pop(0)

        return
    def get_control_status_by_menu_order(self , menu_item):
        if menu_item:
            if menu_item.order == MENU_ORDER_END_TURN:
                return Control.CONTROL_STATUS_TURN_FINISHING
            elif menu_item.order == MENU_ORDER_ATTACK:
                return Control.CONTROL_STATUS_MENU_ATTACK_CHOOSE
            elif menu_item == MENU_ORDER_CANCEL:
                return Control.CONTROL_STATUS_MENU_CANCEL
            elif menu_item.order == MENU_ORDER_STAND_BY:
                return Control.CONTROL_STATUS_IDlE
        return Control.CONTROL_STATUS_IDlE
