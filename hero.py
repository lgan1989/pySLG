# -*- coding: utf-8 -*-

import skill
import database

HERO_TYPE_STRENGTH = 0
HERO_TYPE_AGILITY = 1
HERO_TYPE_INTELLIGENCE = 2

hero_pool = {}

class Hero:
    cid = None
    name = None
    type = None
    health = None
    power = None
    skills = None
    face_id = None
    action_frame_id = None
    level = None
    quote = None

    def __init__(self, cid, rid, fid,name, type, health, strength, agility, intelligence, level , quote ):
        self.cid = cid
        self.name = name
        self.type = type
        self.health = health
        self.power = [0 for _ in range(3)]
        self.power[HERO_TYPE_AGILITY] = agility
        self.power[HERO_TYPE_STRENGTH] = strength
        self.power[HERO_TYPE_INTELLIGENCE] = intelligence
        self.skills = []
        self.face_id = fid
        self.action_frame_id = rid
        self.level = level
        self.parent_pawn = None
        self.quote = quote
        self.strength = self.power[HERO_TYPE_STRENGTH]
        self.agility = self.power[HERO_TYPE_AGILITY]
        self.intelligence = self.power[HERO_TYPE_INTELLIGENCE]
        self.init_attributes()


    def init_attributes(self):


        self.weak = 0
        self.alive = 1
        self.max_health = self.health + int(self.strength * 1.5)
        self.current_health = self.max_health
        self.health_decrease = 0
        self.attack = self.power[self.type]
        self.defence = int ( (self.strength) * 0.7 + (self.agility) * 0.3 )
        self.speed = int(self.agility * 15 / 100)
        self.strategy = int(self.intelligence * self.speed/15)

        self.strength_buff = 0
        self.agiligy_buff = 0
        self.intelligence_buff = 0

        self.attack_buff = 0
        self.defence_buff = 0
        self.speed_buff = 0
        self.strategy_buff = 0


    def use_skill(self , s):
        getattr(skill , s.trigger_function)(self.parent_pawn , s)


def initiate_hero_pool(db):
    hero_list = db.list_heros()
    for h in hero_list:

        new_hero = Hero( h['_id'] , h['render_id'] , h['face_id'], h['name'] , h['type'] , h['health'] , h['strength'] , h['agility'] , h['intelligence'] , h['level'] , h['quote'] )
        hero_skill_list = db.get_hero_skill_list( h['_id'] )
        for s in hero_skill_list:
            hero_skill = skill.Skill( s['_id'] , s['name'] ,  s['type'] , s['is_active'] ,s['passive_type'] ,s['effect_range'] , s['trigger_function'])
            new_hero.skills.append( hero_skill )
        hero_pool[ new_hero.cid ] = new_hero


