# -*- coding: utf-8 -*-

import pymongo
import hero
import config
import skill
import ast

class Database:

    def __init__(self , host , port):
        self.client = pymongo.MongoClient(host , port)
        self.db = self.client.slg_database
        if not config.db_initiated:
            self.initiate_database()

        self.collection_hero = self.db.collection_hero
        self.collection_skill = self.db.collection_skill
        self.collection_hero_skill = self.db.collection_hero_skill

        if not config.db_initiated:
            self.populate_database()


    def populate_database(self):

        self.add_hero(128, u'赵云', hero.HERO_TYPE_AGILITY, 100, 75, 80, 60 , 25 , u'“新鲜龙胆，五金一副。”')
        self.add_hero(135, u'吕布', hero.HERO_TYPE_STRENGTH, 120, 90, 70, 50 , 25 , u'“一起上，我赶时间。”')
        self.add_hero(134, u'周瑜', hero.HERO_TYPE_INTELLIGENCE, 100, 70, 80, 90 , 25 , u'“喂，你先把音调一调！”')
        self.add_hero(146, u'关羽', hero.HERO_TYPE_STRENGTH, 110, 88, 65, 70 , 25 , u'“某略忙，只在夜里读书。”')

        self.add_skill(1, u'嘲讽' , skill.SKILL_TYPE_NON_DAMAGE , False , ((0,1),(0,-1),(-1,0),(1,0)), 'taunt')
        self.add_skill(2 , u'迅捷' , skill.SKILL_TYPE_NON_DAMAGE , False , () , 'move_after_fight')
        self.add_skill(3, u'战意' , skill.SKILL_TYPE_NON_DAMAGE , False , ((0,1),(0,-1),(-1,0),(1,0)) , 'warpath')

        self.add_hero_skill(135 , 1)
        self.add_hero_skill(128 , 2)
        self.add_hero_skill(135 , 3)

    def initiate_database(self):

        self.client.drop_database('slg_database')
        self.db = self.client.slg_database
        self.db.create_collection('collection_hero')
        self.db.create_collection('collection_skill')
        self.db.create_collection('collection_hero_skill')
        self.db.collection_hero_skill.ensure_index([("hid" , pymongo.ASCENDING) , ("sid" , pymongo.ASCENDING)])


    def add_hero(self , hid = 0, name = '' , type = 0 , health = 0 , strength = 0 , agility = 0 , intelligence = 0 , level = 1 , quite = ''):
        hero = {
                "_id" : hid,
                "name" : name,
                "type" : type,
                "health" : health,
                "strength" : strength,
                "agility" : agility,
                "intelligence" : intelligence,
                "level":level,
                "quote" : quite
                }
        self.collection_hero.insert(hero)

    def add_skill(self, sid = 0 , name = '' , type = 0 , is_active = False , effect_range = () , trigger_function = ''):

        skill = {
            "_id" : sid,
            "name" : name,
            "type" : type,
            "is_active" : is_active,
            "effect_range" : effect_range,
            "trigger_function" : trigger_function
        }
        self.collection_skill.insert(skill)

    def add_hero_skill(self, hid , sid):

        hero_skill = {
            "hid" : hid,
            "sid" : sid
        }
        self.collection_hero_skill.insert(hero_skill)

    def get_hero_skill_list(self, hid):
        ret = []
        relation_list = self.collection_hero_skill.find({'hid' : hid})
        for relation in relation_list:
            ret.append( self.collection_skill.find_one(relation['sid']))
        return ret

    def list_heros(self):
        return self.collection_hero.find()


