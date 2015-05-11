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

AI_STRATEGY_OFFENCE = 0
AI_STRATEGY_DEFENCE = 1


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
        
        if pawn_info.ai_status == AI_STATUS_IDLE:
            value, action = self.evaluated_movement(pawn_info , False)
            if action[0] == AI_ACTION_MOVE:
                logger(u' {0} at {1} decide to move to {2}.'.format(pawn_info.hero.name , pawn_info.position , action[1]))
                pawn_info.next_move = [(AI_ACTION_MOVE , action[1])]
                pawn_info.ai_status = AI_STATUS_MOVED
            else:
                logger(u'{0} at {1} decide to attack {2} at {3}'.format( pawn_info.hero.name , pawn_info.position , logic_controller.get_target_pawn(action[1]).hero.name , action[1] ))
                pawn_info.next_move = [(AI_ACTION_ATTACK , action[1])]
        else:
            value, action = self.evaluated_movement(pawn_info , True)
            if action[0] == AI_ACTION_MOVE:
                logger(u'{0} at {1} decide to move to {2}.'.format(pawn_info.hero.name , pawn_info.position , action[1]))
                pawn_info.next_move = [(AI_ACTION_MOVE , action[1])]
                pawn_info.turn_finished = True
            else:
                logger(u'{0} at {1} decide to attack {2} at {3}'.format( pawn_info.hero.name , pawn_info.position , logic_controller.get_target_pawn(action[1]).hero.name , action[1] ))
                pawn_info.next_move = [(AI_ACTION_ATTACK , action[1])]
            

                             

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

    def evaluate_enermy(self, pawn_info):
        enermy_list = []

        d0 = 2
        d1 = 60
        d2 = 40
        d3 = 20

        for p in self.pawn_list:
            if not p.hero.alive:
                continue
            if p.team != pawn_info.team:

                v1 = p.hero.attack - p.hero.defence
                v2 = 1 - 1.0 * p.hero.current_health / p.hero.max_health
                v3,ratio = logic_controller.calculate_damage(pawn_info , p)
                v3 = v3 * ratio

                v = v1 * d1 + v2 * d2 + v3 * d3

                enermy_list.append(  (v , p)  )

        return sorted(enermy_list)



    def evaluated_movement(self, pawn_info , moved):
        pawn_value = 100

        if moved:
            valid_move = [pawn_info.position]
        else:
            valid_move = logic_controller.get_valid_move(pawn_info)
        
        action_list = []
        for pos in valid_move:
            action_list.append( (AI_ACTION_MOVE , pos) )
        attack_target = self.find_attack_candidates(pawn_info)
        for target in attack_target:
            action_list.append( (AI_ACTION_ATTACK , target) )

        enermy_list = self.evaluate_enermy(pawn_info)
        enermy_value = {}
        for e in enermy_list:
            enermy_value[ e[1].index ] = e[0]
#            logger(u'Enermy {0} : {1}'.format(e[1].hero.name , e[0]))
        valued_action_list = []
        for action in action_list:
            offence = 0
            danger = 0
            if action[0] == AI_ACTION_MOVE:
                offence , danger = self.evaluate_position(pawn_info , action[1] , enermy_value)
            else:
                target_pawn =  logic_controller.get_target_pawn(action[1])
                damage , ratio = logic_controller.calculate_damage(pawn_info ,  target_pawn)
                damage = damage * ratio
                rest = target_pawn.hero.current_health - damage
                rest = max(0, rest)
                if rest == 0:
                    offence += enermy_value[ target_pawn.index ]
                else:
                    offence += enermy_value[target_pawn.index] * damage * 1.0 /target_pawn.hero.current_health 
                position_evl = self.evaluate_position( pawn_info, pawn_info.position ,enermy_value )

                offence += position_evl[0]
                danger += position_evl[1]

            valued_action_list.append(( (offence , danger) , action  ))

        if valued_action_list:
            if pawn_info.ai_strategy == AI_STRATEGY_OFFENCE:
                valued_action_list.sort(reverse=True)
            elif pawn_info.ai_strategy == AI_STRATEGY_DEFENCE:
                valued_action_list.sort(key=lambda x:x[1])

            ret = valued_action_list[0]
            if debug:
                for tmp in valued_action_list:
                    if tmp[1][0] == AI_ACTION_MOVE:
                        logger( u'[Move to {0}] [ offence : {1} , danger : {2}  ]'.format(tmp[1][1] ,tmp[0][0] , tmp[0][1]) )
                    else:
                        logger(u'[Attack {0}] [ offence : {1} , danger : {2}  ]'.format( logic_controller.get_target_pawn(tmp[1][1]).hero.name , tmp[0][0] , tmp[0][1]))
            return ret
        return None
                    
    def evaluate_position(self, pawn_info, position , enermy_value):
        pawn_value = 100
        damage_take = 0
        best_enermy = 0
        offence = 0
        danger = 0
        d_dist = 100
        for p in self.pawn_list:
            if not p.hero.alive:
                continue
            if p.team != pawn_info.team:
                dist = logic_controller.distance(p.position , position)
                offence += d_dist * 1.0/dist
                if logic_controller.targfet_can_be_attacked_by_pawn_from(position , p , p.position):  #damage take
                    d , r = logic_controller.calculate_damage(p , pawn_info)
                    damage_take += d * r
                if logic_controller.targfet_can_be_attacked_by_pawn_from( p.position , pawn_info, position ): #damage make
                    best_enermy = max(best_enermy, enermy_value[ p.index ] )
        offence += best_enermy
        # Damage will kill me
        if damage_take > pawn_info.hero.current_health:
            danger += pawn_value
        else: #not going to kill me
            delta = pawn_info.hero.current_health - damage_take
            perc = 1 - delta * 1.0 / pawn_info.hero.current_health
            danger += pawn_value * perc

        return offence , danger
