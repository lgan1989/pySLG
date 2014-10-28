
logic_controller = None


AI_LEVEL_STUPID = 0
AI_LEVEL_NORMAL = 1
AI_LEVEL_SMART = 2


AI_ACTION_MOVE = 0
AI_ACTION_ATTACK = 1
AI_ACTION_STAND_BY = 2

class AI:
    def __init__(self , pawn_list ):
        self.level = 0
        self.pawn_list = pawn_list

    def distance(self , p1 , p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def find_attack_candidates(self , pawn_info):

        return logic_controller.get_valid_target(pawn_info)



    def take_action(self):

        for p in self.pawn_list:
            if not p.has_ai:
                continue
            if p.turn_finished:
                continue
            attack_target = self.find_attack_candidates( p )
            if attack_target:
                p.next_move = [ (AI_ACTION_ATTACK , attack_target[0]) ]
            else:
                closest_enermy = self.find_closest_enermy(p)
                if closest_enermy:

                    destination = self.move_forawrd_to( p , closest_enermy.position )
                    p.next_move = [ (AI_ACTION_MOVE , destination) ]
                    #print 'next move :' , p.next_move


    def find_closest_enermy(self , pawn_info):
        closest_pawn = None
        d = -1
        for p in logic_controller.pawn_list:
            if p.team != pawn_info.team:
                tmp = self.distance( pawn_info.position , p.position )
                if  tmp < d or d < 0:
                    d = tmp
                    closest_pawn = p
        return closest_pawn


    def move_forawrd_to(self, pawn_info , grid):
        valid_move = logic_controller.get_valid_move( pawn_info )
        d = -1
        destination = None

        for pos in valid_move:
            tmp = self.distance( pos , grid )
            if tmp < d or d < 0:
                d = tmp
                destination = pos

        return destination
