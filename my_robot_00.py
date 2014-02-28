import random
import math
import rg

def around(l):
    return rg.locs_around(l)
    
def diag(l1, l2):
    if rg.wdist(l1, l2) == 2:
        if abs(l1[0] - l2[0]) == 1:
            return True
    return False

def long_diag(l1, l2):
    if abs(l1[0]-l2[0])==abs(l1[1]-l2[1]) :
        return True
    return False    
    
def infront(l1, l2):
    if rg.wdist(l1, l2) == 2:
        if diag(l1, l2):
            return False
        else:
            return True
    return False
    
def mid(l1, l2):
    return (int((l1[0]+l2[0]) / 2), int((l1[1]+l2[1]) / 2))

current_turn=0
all_enemies={}
all_enemies_locations=[]


class Robot:
     def act(self, game):
        global current_turn, all_enemies, all_enemies_locations 
        robots = game['robots']
        groups=[]
        flag_new_group=False
     
        def isenemy(l):
            if robots.get(l) != None:
                if robots[l]['player_id'] != self.player_id:
                    return True
            return False

        if current_turn!=game['turn'] :
            current_turn=game['turn']
            # raw_input("Press Enter to continue...")
            for loc, robot in robots.items():
                if robot.player_id != self.player_id:
                    all_enemies[loc]=robot                
                    all_enemies_locations.append(loc)
            while all_enemies_locations :
                cur_e_loc=all_enemies_locations.pop()
                for temp_loc in around(cur_e_loc) :
                    if temp_loc in all_enemies_locations :
                        flag_new_group=False
                        for cur_group in groups :
                            if all_enemies[cur_e_loc] in cur_group :
                                groups[groups.index(cur_group)].append(all_enemies[temp_loc])
                                flag_new_group=True
                                break
                        if not flag_new_group :
                            groups.append([all_enemies[cur_e_loc]])
                            groups[-1].append(all_enemies[temp_loc])
            for cur_group in groups :
                if len(cur_group)<=2 :
                    groups.remove(cur_group)
                    break
                # print(cur_group)
                print(map(lambda x : x.location[0], cur_group))

            # print(groups)
        
        def isempty(l):
            if ('normal' in rg.loc_types(l)) and not ('obstacle' in rg.loc_types(l)):
                if robots.get(l) == None:
                    return True
            return False
        
        def isspawn(l):
            if 'spawn' in rg.loc_types(l):
                return True
            return False
        
        # scan the area around
        enemies = []
        for loc in around(self.location):
            if isenemy(loc):
                enemies.append(loc)
        # print(game.robots)        
        
        moveable = []
        moveable_safe = []
        for loc in around(self.location):
            if isempty(loc):
                moveable.append(loc)
            if isempty(loc) and not isspawn(loc):
                moveable_safe.append(loc)
        
        def guard():
            return ['guard']
        
        def suicide():
            return ['suicide']
        
        def canflee():
            return len(moveable) > 0
        
        def flee():
            if len(moveable_safe) > 0:
                return ['move', random.choice(moveable_safe)]
            if len(moveable) > 0:
                return ['move', random.choice(moveable)]
            return guard()
        
        def canattack():
            return len(enemies) > 0
            
        def attack():
            r = enemies[0]
            for loc in enemies:
                if robots[loc]['hp'] > robots[r]['hp']:
                    r = loc
            return ['attack', r]
        
        def panic():
            if canflee():
                return flee()
            elif canattack():
                return attack()
            else:
                return guard()
        
        # if there are too many enemies around and we are low on health, suicide
        if (self.hp <= 19) and (self.hp <= len(enemies)*10) :
            return suicide()

        # for cur_group in groups :
        #     if len(cur_group)>2 :


        # if there are too many enemies around and we are low on health, suicide
        if self.hp <= len(enemies)*10:
            return suicide()
        
        # if there are too many enemies around and our health is not bad, get out
        # if enemy is alone, attack
        if len(enemies) > 1:
            return panic()
        elif canattack():
            return attack()
        
        # if we're at spawn, get out
        if isspawn(self.location):
            return panic()
        
        # if there are enemies in 2 squares, predict and attack
        for loc, bot in game.get('robots').items():
            if isenemy(loc):
                if rg.wdist(loc, self.location) == 2:
                    if infront(loc, self.location):
                        return ['attack', mid(loc, self.location)]
                    if rg.wdist(rg.toward(loc, rg.CENTER_POINT), self.location) == 1:
                        return ['attack', rg.toward(loc, rg.CENTER_POINT)]
                    else:
                        return ['attack', (self.location[0], loc[1])]
        
        # move randomly
        return panic()
