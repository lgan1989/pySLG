import pawn
import battle_map
from ai import *


INT_MAX = 99999999999

TARGET_TYPE_PLAYER_PAWN = 0
TARGET_TYPE_FRIEND_PAWN = 1
TARGET_TYPE_ENEMY_PAWN = 2
TARGET_TYPE_TILE = 3
TARGET_TYPE_MENU_ITEM = 4
TARGET_TYPE_INVALID = 5

MENU_ORDER_END_TURN = 0
MENU_ORDER_ATTACK = 1
MENU_ORDER_STAND_BY = 2
MENU_ORDER_PERSUADE = 3
MENU_ORDER_CANCEL = 4

DIRECTION_DOWN = 0
DIRECTION_LEFT = 1
DIRECTION_RIGHT = 2
DIRECTION_UP = 3
D = ((-1, 0), (1, 0), (0, -1), (0, 1))
DIRECTION_DIFF = ((1, 0), (0, -1), (0, 1), (-1, 0),(1,1),(-1,1) , (1,-1) , (-1,-1) )
GET_D = {DIRECTION_DIFF[0]: DIRECTION_DOWN, DIRECTION_DIFF[1]: DIRECTION_LEFT, DIRECTION_DIFF[2]: DIRECTION_RIGHT, DIRECTION_DIFF[3]: DIRECTION_UP,
         DIRECTION_DIFF[4] : DIRECTION_RIGHT , DIRECTION_DIFF[5] : DIRECTION_RIGHT , DIRECTION_DIFF[6]: DIRECTION_LEFT,DIRECTION_DIFF[7]:DIRECTION_LEFT
         }

control = None
fight_logic_controller = None

class Logic:


    def __init__(self, current_map, pawn_list):
        self.current_map = current_map
        self.class_mobility = {pawn.MOBILE_WALK: 5, pawn.MOBILE_MOUNT: 8}
        self.pawn_list = pawn_list
        self.turn_team = 0

    def get_face_direction(self, diff):

        d1 = -1 if diff[0] < 0 else diff[0] > 0
        d2 = -1 if diff[1] < 0 else diff[1] > 0
        d = (int(d1) , int(d2))

        return GET_D[d]

    def get_attack_range_grids(self, pawn_info):
        pos = pawn_info.position
        range = pawn_info.range
        ret = []
        for dis in range:
            tx = pos[0] + dis[0]
            ty = pos[1] + dis[1]
            if 0 <= tx < self.current_map.tile_row_number and 0 <= ty < self.current_map.tile_col_number:
                ret.append((tx,ty))
        return ret

    def new_turn(self):
        for p in self.pawn_list:
            p.action_started = False
            p.turn_finished = False
            p.hero.skill_triggered = False
            p.ai_status = AI_STATUS_IDLE
            p.can_attack = True
            p.reset_render_index()
            if p.turn_team != self.turn_team:
                p.action_turn = False
            else:
                p.action_turn = True
        fight_logic_controller.trigger_passive_skills_at_turn_start()

    def end_trun(self):

        self.turn_team = (self.turn_team + 1)
        self.turn_team %= 3

        self.new_turn()

    def get_target_pawn(self, target):
        for p in self.pawn_list:
            if p.position == target:
                return p
        return None

    def is_valid_target(self, pawn_info , target , action):
        if action == pawn.ACTION_ATTACK:
            valid_target = self.get_valid_target(pawn_info)
            if target in valid_target:
                return TARGET_TYPE_ENEMY_PAWN
            return TARGET_TYPE_INVALID
        return self.get_target_type(pawn_info.team , target)


    def get_target_team(self, target):
        for p in self.pawn_list:
            if p.position == target:
                return p.team
        return -1

    def get_target_type(self, team, target):
        for p in self.pawn_list:
            if p.position == target:

                if p.controllable:
                    return TARGET_TYPE_PLAYER_PAWN
                elif p.team == team:
                    return TARGET_TYPE_FRIEND_PAWN
                else:
                    return TARGET_TYPE_ENEMY_PAWN
        return TARGET_TYPE_TILE

    def fight(self, attacker , defender):

        if self.diff_position(attacker.position , defender.position) in attacker.range:
            if attacker.turn_team == self.turn_team:
                attacker.action_started = True
            diff = self.diff_position(attacker.position , defender.position)
            attacker.direction = self.get_face_direction(diff)
            attacker.action_queue.insert(0 , (pawn.ACTION_ATTACK , defender.position))
            defender.direction = self.get_face_direction((-diff[0] , -diff[1]))
            defender.action_queue.insert(0, (pawn.ACTION_ATTACKED , attacker.position))


    def update_terrain_mask(self):
        for p in self.pawn_list:
            position = p.position
            terrain = self.current_map.map_terrain_info[position[0]][position[1]]
            p.special_render_item = {}
            terrain_mask = battle_map.get_mask( terrain,p.action )
            if terrain_mask != None:
                p.special_render_item['mask'] = terrain_mask
            terrain_sound = battle_map.get_sound(terrain,p.action)
            if terrain_sound != None:
                p.special_render_item['sound'] = terrain_sound



    def update_pawn_status(self):
        for p in self.pawn_list:
            if p.action == pawn.ACTION_PROCESSING or p.action_queue:
                return
        for p in self.pawn_list:
            if p.hero.alive:
                if p.move_after_fight == -1:
                    p.can_attack = False
                if p.hero.current_health <= 0:
                    p.hero.alive = 0
                else:
                    if p.hero.current_health * 5 < p.hero.max_health:
                        p.hero.weak = 1
                    else:
                        p.hero.weak = 0
                p.taunted_to = []
                if p.action_started:
                    if p.move_after_fight == 1:
                        p.move_after_fight = -1
                    if p.move_after_fight == 0:
                        p.turn_finished = True
            else:
                self.current_map.map_collision_info[p.position[0]][p.position[1]] = battle_map.COLLISION_INFO_EMPTY
                self.pawn_list.remove(p)


    def process_player_action(self , pawn_info, target , order=None):
        if pawn_info.turn_finished:
            return
        if self.turn_team != pawn_info.turn_team:
            return

        type = self.get_target_type(pawn_info.team , target)
        team = self.get_target_team(target)
        if type == TARGET_TYPE_TILE or target == pawn_info.position:
            start = pawn_info.position
            if pawn_info.action_queue:
                pawn_info.action_queue = [pawn_info.action_queue[0]]
                start = pawn_info.action_queue[0][1]
            mobility_requied = self.calculate_mobile_reduce(pawn_info.team)
            mobility_requied[start[0]][start[1]] = 1
            step_limit = (pawn_info.hero.speed * 10 + 100 ) * self.class_mobility[pawn_info.mobility] / 100

            valid_move = self.get_valid_move(pawn_info)
            if target in valid_move:
                path = self.find_path(start , target  , pawn_info.position , mobility_requied ,step_limit)
                pawn_info.action_queue += [ (pawn.ACTION_MOVE, movement) for movement in path ]
        elif team != -1 and team !=  pawn_info.team:

            if order == MENU_ORDER_ATTACK:

                attacker = pawn_info
                defender = self.get_target_pawn(target)

                if attacker.taunted_to and defender in attacker.taunted_to:
                    self.fight(attacker , defender)
                elif not attacker.taunted_to:
                    if defender.can_be_attacked:
                        self.fight(attacker , defender)
            elif order == MENU_ORDER_PERSUADE:
                self.persuade_target(pawn_info , self.get_target_pawn(target))


    def process_attack_result(self , attacker , defender):

        attack_value = attacker.hero.attack + attacker.hero.attack_buff
        defence_value = defender.hero.defence + defender.hero.defence_buff
        reduce_percent = (defender.hero.strategy + defender.hero.strength_buff) * 1.0 / 100

        damage = attack_value
        damage_reduce = int(defence_value * reduce_percent)

        damage -= damage_reduce

        #print 'damage:' , damage

        defender.hero.health_decrease = min(damage , defender.hero.current_health)

        defender.action = pawn.ACTION_PROCESSING



    def process_action_queue(self):
        for p in self.pawn_list:
            if p.action == pawn.ACTION_PROCESSING:
                return True

        flag = False
        for p in self.pawn_list:
            last_pos = None
            if p.action_queue:
                flag = True
                current_action = p.action_queue[0]
                action_type = current_action[0]
                action_grid = current_action[1]
                p.action = action_type

                if action_type == pawn.ACTION_MOVE:
                    last_pos = p.position
                    p.move_to_grid(action_grid)
                    if p.position == action_grid:
                        p.action_queue.pop(0)
                        if not p.action_queue or p.action_queue[0][0] != pawn.ACTION_MOVE:
                            p.sprite_move.finish()
                            p.action = pawn.ACTION_STAND
                            control.status = control.CONTROL_STATUS_PAWN_MOVED

                elif action_type == pawn.ACTION_ATTACK:
                    if not p.attack():
                        p.action_queue.pop(0)
                elif action_type == pawn.ACTION_PARRY:
                    if not p.parry():
                        p.action_queue.pop(0)
                elif action_type == pawn.ACTION_ATTACKED:
                    if not p.attacked():
                        p.action_queue.pop(0)
                        defender = self.get_target_pawn(action_grid)
                        self.process_attack_result( defender , p)

                        if not p.action_turn and p.hero.current_health - p.hero.health_decrease > 0:
                            self.fight(p , defender)

                        if p.hero.current_health - p.hero.health_decrease <= 0:
                            self.die(p)

                        return True
                elif action_type == pawn.ACTION_DYING:
                    if p.died():
                        p.action_queue.pop(0)
            else:
                p.action = pawn.ACTION_STAND
            if last_pos:
                self.current_map.map_collision_info[last_pos[0]][last_pos[1]] = battle_map.COLLISION_INFO_EMPTY
            self.current_map.map_collision_info[p.position[0]][p.position[1]] = battle_map.COLLISION_INFO_OCCUPIED

        return flag

    def die(self, p):
        p.action_queue.append( (pawn.ACTION_DYING , p.position) )

    def real_distance(self, start , destination , mobility_requied):

        if start == destination:
            return 0
        que = []

        visited = [[False for i in range(self.current_map.tile_col_number)] for j in
                   range(self.current_map.tile_row_number)]

        visited[start[0]][start[1]] = True
        que.append((0,start))

        while que:
            top = que.pop(0)
            step = top[0]
            pos = top[1]
            if pos == destination:
                return step
            for idx , d in enumerate(D):
                nx = pos[0] + d[0]
                ny = pos[1] + d[1]
                if (nx , ny) == destination:
                    return step + 1
                if  0 <= nx < self.current_map.tile_row_number and 0 <= ny < self.current_map.tile_col_number and \
                                visited[nx][ny] == False and  (
                        ( (self.current_map.map_collision_info[nx][ny] == battle_map.COLLISION_INFO_EMPTY ) and (self.current_map.map_block_info[pos[0]][pos[1]] & (1<<idx) == 0) )):

                    if mobility_requied[pos[0]][pos[1]] != INT_MAX:
                        visited[nx][ny] = True
                        que.append((step + 1 , (nx, ny)))

        return INT_MAX

    def find_path(self, start, destination, self_position , mobility_requied , step_limit):

        if start == destination:
            return [start]

        que = []

        visited = [[False for i in range(self.current_map.tile_col_number)] for j in
                   range(self.current_map.tile_row_number)]
        prev = [[None for i in range(self.current_map.tile_col_number)] for j in
                range(self.current_map.tile_row_number)]
        path = []
        visited[start[0]][start[1]] = True
        que.append((0,start))
        find = False
        while que:
            top = que.pop(0)
            step = top[0]
            pos = top[1]
            if step > step_limit:
                break
            if pos == destination:
                find = True
                break
            for idx , d in enumerate(D):
                nx = pos[0] + d[0]
                ny = pos[1] + d[1]
                if  0 <= nx < self.current_map.tile_row_number and 0 <= ny < self.current_map.tile_col_number and \
                                visited[nx][ny] == False and  (
                            self_position == (nx, ny) or
                        ( (self.current_map.map_collision_info[nx][ny] == battle_map.COLLISION_INFO_EMPTY ) and (self.current_map.map_block_info[pos[0]][pos[1]] & (1<<idx) == 0) )):

                    if mobility_requied[pos[0]][pos[1]] != INT_MAX:
                        visited[nx][ny] = True
                        prev[nx][ny] = ((pos[0], pos[1]))
                        que.append((step + 1 , (nx, ny)))


        if find:
            cur = destination
            while prev[cur[0]][cur[1]] != None:
                path.append(cur)
                cur = prev[cur[0]][cur[1]]
        return path[::-1]

    def calculate_mobile_reduce(self, team):

        row = self.current_map.tile_row_number
        col = self.current_map.tile_col_number

        ret = [[1 for _ in range(col)] for _ in range(row)]

        for p in self.pawn_list:
            if p.team != team:
                pos = p.position
                for i in range(4):
                    nx = pos[0] + D[i][0]
                    ny = pos[1] + D[i][1]
                    if 0 <= nx < self.current_map.tile_row_number and 0 <= ny < self.current_map.tile_col_number:
                        if self.current_map.map_collision_info[nx][ny] == battle_map.COLLISION_INFO_EMPTY :
                            ret[nx][ny] = INT_MAX
        return ret

    def get_valid_move(self, pawn_info):
        mobility = (pawn_info.hero.speed  * 10 ) * self.class_mobility[pawn_info.mobility] / 100

        current_position = pawn_info.position
        visited = {}
        visited[current_position] = 1

        ret = []
        q = [(0, current_position)]

        mobility_requied = self.calculate_mobile_reduce(pawn_info.team)
        mobility_requied[current_position[0]][current_position[1]] = 1

        while q:
            top = q[0]
            q.pop(0)
            step = top[0]
            if step > mobility:
                continue
            pos = top[1]
            ret.append(pos)
            for i in range(4):
                nx = pos[0] + D[i][0]
                ny = pos[1] + D[i][1]
                if 0 <= nx < self.current_map.tile_row_number and 0 <= ny < self.current_map.tile_col_number and (
                nx, ny) not in visited:
                    if self.current_map.map_collision_info[nx][ny] == battle_map.COLLISION_INFO_EMPTY and  ((self.current_map.map_block_info[pos[0]][pos[1]] & (1<<i)) == 0):
                        if step + mobility_requied[pos[0]][pos[1]] <= mobility:
                            visited[(nx, ny)] = 1
                            q.append((step + mobility_requied[pos[0]][pos[1]], (nx, ny)))

        return ret

    def diff_position(self , source_position , target_positin):
        return (target_positin[0] - source_position[0] , target_positin[1]  - source_position[1])

    def distance(self, pos1 , pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_persuade_target(self , pawn_info):

        ret = []

        cid_list = []
        for p in self.pawn_list:
            cid_list.append(p.hero.cid)

        for p in self.pawn_list:
            if p.team != pawn_info.team and self.diff_position(pawn_info.position , p.position) in pawn.PERSUADE_RANGE:
                if p.persuade and pawn_info.hero.cid in p.persuade['by']:
                    ret.append( p.position )
        return ret

    def persuade_target(self , pawn_info , target_pawn):
        succ = True

        dead_required = target_pawn.persuade['dead_required']
        alive_required = target_pawn.persuade['alive_required']

        cid_list = []
        for p in self.pawn_list:
            cid_list.append(p.hero.cid)
        for d in dead_required:
            if d in cid_list:
                succ = False
                break
        for d in alive_required:
            if d not in cid_list:
                succ = False
                break

        pawn_info.action_started = True
        diff = self.diff_position(target_pawn.position , pawn_info.position)
        pawn_info.direction = self.get_face_direction((-diff[0] , -diff[1]))
        target_pawn.direction = self.get_face_direction(diff)
        if succ:
            target_pawn.turn_team = pawn_info.turn_team
            target_pawn.team = pawn_info.team
            target_pawn.has_ai = pawn_info.has_ai
            target_pawn.controllable = pawn_info.controllable
            target_pawn.turn_finished = True
            target_pawn.load(True)
        return succ


    def get_valid_target(self, pawn_info):

        ret = []
        if pawn_info.taunted_to:
            for p in pawn_info.taunted_to:
                ret.append(p.position)
            return ret
        for p in self.pawn_list:
            if p.can_be_attacked and p.team != pawn_info.team and self.diff_position(pawn_info.position , p.position) in pawn_info.range:
                ret.append(p.position)
        return ret

    def process_menu_order(self , pawn_info, item):
        if not item:
            return
        if item.order == MENU_ORDER_STAND_BY:
            if pawn_info:
                pawn_info.turn_finished = True

        return


