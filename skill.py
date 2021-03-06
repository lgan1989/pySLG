from resource import skill_image
import pygame

SKILL_TYPE_DAMAGE = 0
SKILL_TYPE_NON_DAMAGE = 1

PASSIVE_TYPE_REALTIME = 0
PASSIVE_TYPE_TURN_START = 1

SKILL_IMAGE_TAUNT = 0

fight_logic_controller = None

SKILL_ID_TAUNT = 1
SKILL_ID_MOVE_AFTER_FIGHT = 2
SKILL_ID_WARPATH = 3



def load_skill_images():
    skill_image[SKILL_IMAGE_TAUNT] = pygame.image.load("image/skill/" + str(SKILL_ID_TAUNT) + ".bmp").convert()
    skill_image[SKILL_IMAGE_TAUNT].set_alpha(200)
    return

class Skill:
    sid = None
    name = None
    type = None
    is_active = None
    passive_type = None
    trigger_function = None
    effect_range = None

    def __init__(self , sid, name , type , is_active , passive_type, effect_range, trigger_function ):
        self.sid = sid
        self.name = name
        self.type = type
        self.is_active = is_active
        self.passive_type = passive_type
        self.trigger_function = trigger_function
        self.effect_range = effect_range

#p for pawn, s for skill

def taunt(p, s):
    p.taunt = True
    pos = p.position
    for d in s.effect_range:
        nx = pos[0] + d[0]
        ny = pos[1] + d[1]
        target_pawn = fight_logic_controller.get_target_pawn((nx,ny))
        if target_pawn is not None and target_pawn.team != p.team:
            if p not in target_pawn.taunted_to:
                target_pawn.taunted_to.append(p)


def move_after_fight(p , s):
    p.move_chance = 2

def warpath(p, s):
    pos = p.position
    c = 0
    for d in s.effect_range:
        nx = pos[0] + d[0]
        ny = pos[1] + d[1]
        target_pawn = fight_logic_controller.get_target_pawn((nx,ny))
        if target_pawn is not None and target_pawn.team != p.team:
            c += 1

    p.hero.attack_buff = int( p.hero.attack * 0.1 * c )
    p.hero.defence_buff = int( p.hero.attack * 0.2 * c )


