# -*- coding: utf-8 -*-
import pawn
import logic
import skill
from config import debug,logger

class FightLogic:


    def __init__(self, current_map, pawn_list):
        self.current_map = current_map
        self.class_mobility = {pawn.MOBILE_WALK: 3, pawn.MOBILE_MOUNT: 6}
        self.pawn_list = pawn_list

    def trigger_passive_skills_realtime(self):
        """
        触发部分需要实时更新的被动技能
        1). 嘲讽
        2). 战意

        """
#        if debug:
#            logger(u'Triggering passive_skills_realtime')

        for p in self.pawn_list:
            for s in p.hero.skills:
                if s.sid in(
                    skill.SKILL_ID_WARPATH,
                    skill.SKILL_ID_TAUNT):
                    p.hero.use_skill(s)
#                    if debug:
#                        logger(u"{0} 触发了实时被动技能 {1}".format(p.hero.name , s.name))

#        if debug:
#            logger(u'Finished triggering passive_skills_realtime')



    def trigger_passive_skills_at_turn_start(self):
        """
        触发部分在回合开始前触发的被动技能
        1). 迅捷
        """

        if debug:
            logger(u'Triggering passive_skills_at_turn_start')
        for p in self.pawn_list:
            for s in p.hero.skills:                         
                if s.sid == skill.SKILL_ID_MOVE_AFTER_FIGHT:
                    if debug:
                        logger(u"{0} 触发了回合开始前的被动技能 {1}".format(p.hero.name , s.name))
                    p.hero.use_skill(s)
        if debug:
            logger(u'Finished triggering passive_skills_at_turn_start')

    def get_target_pawn(self, target):
        for p in self.pawn_list:
            if p.position == target:
                return p
        return None
