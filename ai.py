# -*- coding: utf-8 -*-

from config import debug, logger

logic_controller = None

AI_LEVEL_STUPID = 0
AI_LEVEL_NORMAL = 1
AI_LEVEL_SMART = 2

AI_ACTION_MOVE = 0
AI_ACTION_ATTACK = 1
AI_ACTION_STAND_BY = 2

AI_STATUS_IDLE = 0
AI_STATUS_MOVED = 1
AI_STATUS_ATTACKED = 2


class AI:
    level = None
    pawn_list = None

    def __init__(self, pawn_list):
        self.level = 0
        self.pawn_list = pawn_list

    def distance(self, p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def find_attack_candidates(self, pawn_info):
        """
        To find available targets to attack
        Return a list of pawn
        """
        return logic_controller.get_valid_target(pawn_info)

    def take_action(self, pawn_info=None):

        if debug:
            logger(u'{0}{1} is taking action, is_leader = {2}'.format(pawn_info.position, pawn_info.hero.name , pawn_info.is_leader))

        if pawn_info.is_leader:
            attack_target = self.find_attack_candidates(pawn_info)

            if attack_target:
                pawn_info.next_move = [(AI_ACTION_ATTACK, attack_target[0])]
                logger(u'{0} decide to attack the target at {1}'.format(pawn_info.hero.name , attack_target[0]))
            else:
                if pawn_info.ai_status == AI_STATUS_IDLE:
                    closest_enermy = self.find_closest_enermy(pawn_info)
                    if closest_enermy:
                        destination = self.move_forawrd_to(pawn_info, closest_enermy.position)
                        pawn_info.next_move = [(AI_ACTION_MOVE, destination)]
                        pawn_info.ai_status = AI_STATUS_MOVED
                        logger(u'{0} decide to move to {1}'.format(pawn_info.hero.name , destination))
                    else:            
                        logger(u'{0} decide to stand by'.format(pawn_info.hero.name))
                        pawn_info.turn_finished = True
                else:
                    logger(u'{0} decide to stand by'.format(pawn_info.hero.name))
                    pawn_info.turn_finished = True
        else:
            attack_target = self.find_attack_candidates(pawn_info)
            if attack_target:
                pawn_info.next_move = [(AI_ACTION_ATTACK, attack_target[0])]
                logger(u'{0} decide to attack the target at {1}'.format(pawn_info.hero.name , attack_target[0]))
            else:
                if pawn_info.ai_status == AI_STATUS_IDLE:
                    for ld in self.pawn_list:

                        if ld.ai_group == pawn_info.ai_group and ld.is_leader:
                            leader_move = ld.next_move

                            if leader_move:
                                if leader_move[0][0] == AI_ACTION_MOVE:
                                    destination = self.move_forawrd_to(pawn_info, leader_move[0][1])
                                    pawn_info.next_move = [(AI_ACTION_MOVE, destination)]
                                    pawn_info.ai_status = AI_STATUS_MOVED
                                else:
                                    destination = self.move_forawrd_to(pawn_info, ld.position)
                                    pawn_info.next_move = [(AI_ACTION_MOVE, destination)]
                                    pawn_info.ai_status = AI_STATUS_MOVED
                                logger(u'{0} followed leader {1} to move to {2}'.format(pawn_info.hero.name , ld.hero.name, destination))
                            else:
                                pawn_info.turn_finished = True
                                logger(u'{0} decide to stand by'.format(pawn_info.hero.name))
                            break
                else:
                    pawn_info.turn_finished = True
                    logger(u'{0} decide to stand by'.format(pawn_info.hero.name))




    def find_closest_enermy(self, pawn_info):
        closest_pawn = None
        d = -1
        for p in logic_controller.pawn_list:
            if p.team != pawn_info.team:
                mobility_requied = logic_controller.calculate_mobile_reduce(pawn_info.team)
                mobility_requied[pawn_info.position[0]][pawn_info.position[1]] = 1
                tmp = logic_controller.real_distance(pawn_info.position, p.position, mobility_requied)
                if tmp < d or d < 0:
                    d = tmp
                    closest_pawn = p
        return closest_pawn


    def move_forawrd_to(self, pawn_info, grid):
        valid_move = logic_controller.get_valid_move(pawn_info)

        d = -1
        destination = None

        for pos in valid_move:
            mobility_requied = logic_controller.calculate_mobile_reduce(pawn_info.team)
            mobility_requied[pos[0]][pos[1]] = 1
            tmp = logic_controller.real_distance(pos, grid, mobility_requied)
            logger(u'Real distance from {0} to {1} is {2}'.format(pos , grid , tmp ))

            if tmp < d or d < 0:
                d = tmp
                destination = pos

        return destination
