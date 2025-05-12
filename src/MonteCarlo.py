from constants import *
import math
import random
from vector import Vector2
import time
c = math.sqrt(2)

DIRECTIONS = {
    UP:    Vector2(0, -1),
    DOWN:  Vector2(0, 1),
    LEFT:  Vector2(-1, 0),
    RIGHT: Vector2(1, 0),
    STOP:  Vector2(0, 0)
}

def collideGhosts(pacman_pos, ghost_positions, pacman_radius, ghost_radius):
    for ghost_pos in ghost_positions:
        d = pacman_pos - ghost_pos
        dSquared = d.magnitudeSquared()
        rSquared = (pacman_radius + ghost_radius)**2
        if dSquared <= rSquared:
            return True
    return False

def nextToGhosts(pos, ghost_positions, threshold_dist=2*TILEWIDTH):
    for ghost_pos in ghost_positions:
        if manhattan_distance(pos, ghost_pos) < threshold_dist:
            return True
    return False

def nextToGhostsSQ(pos, ghost_positions, threshold_dist_sq): 
    for ghost_pos in ghost_positions:
        dist_sq = (pos - ghost_pos).magnitudeSquared()
        if dist_sq < threshold_dist_sq:
            return True
    return False

def manhattan_distance(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)

class MonteCarloNode:
    def __init__(self, position, parent=None, move_leading_here=None, possible_moves=None):
        self.position = position
        self.parent = parent
        self.move_leading_here = move_leading_here 
        self.children = {}
        self.possible_moves = list(possible_moves) if possible_moves else []
        self.untried_moves = list(self.possible_moves)
        self.value = 0.0
        self.visits = 0

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def get_ucb1(self, exploration_constant=c):
        visits_plus_epsilon = self.visits + 1e-6
        if visits_plus_epsilon == 1e-6: 
             return float('inf') 

        exploitation_term = self.value / visits_plus_epsilon
        if self.parent is None or self.parent.visits == 0:
             return exploitation_term

        exploration_term = exploration_constant * math.sqrt(math.log(self.parent.visits) / visits_plus_epsilon)
        return exploitation_term + exploration_term


    def select_best_child(self, exploration_constant=c):
        best_score = -float('inf')
        best_child = None
        shuffled_children = list(self.children.values())
        random.shuffle(shuffled_children)
        for child in shuffled_children:
            score = child.get_ucb1(exploration_constant)
            if score > best_score:
                best_score = score
                best_child = child
        return best_child
    
class MonteCarloSearch:
    def __init__(self, pacman, ghosts, pellets, level_data, maze_nodes, N, current_score, last_actual_move):
        self.pacman_start = pacman          
        self.ghosts_start =ghosts           
        self.pellets_start = pellets         
        self.maze_nodes = maze_nodes         
        self.level_data = level_data         
        self.N = N                           
        self.current_score = current_score  
        self.last_actual_move = last_actual_move 
        self.current_pellet_tuples = set()
        self.current_power_pellet_tuples = set()
        self.blinky_sim_id = None
        self.simulation_depth =   100     
        self.SIM_GHOST_TARGET_PACMAN=True
        self.ghost_move_heuristic = "random"
        self.SIM_FREIGHT_DURATION = 7 
        self.SIM_GHOST_SPEED_NORMAL = 100
        self.SIM_GHOST_SPEED_FREIGHT = 50
        self.SIM_GHOST_SPEED_SPAWN = 150
        self.EMPTY_TILE_PENALTY = -100
        self.REWARD_PELLET = 500
        self.REWARD_POWER_PELLET = 600   
        self.PENALTY_DEATH = -250000
        self.PENALTY_GHOST_NEAR = -4000  
        self.GHOST_NEAR_THRESHOLD = (7 * TILEWIDTH )**2
        self.PENALTY_REVISIT = -50         
        self.PENALTY_REVERSE_MOVE = -70   
        self.REWARD_PROGRESS = 0.1        
        self.REWARD_CLEAR_LEVEL = 20000
        self.pacman_radius = TILEWIDTH / 2.5 
        if hasattr(pacman, 'collideRadius'):
             self.pacman_radius = pacman.collideRadius

        self.ghost_radius = TILEWIDTH / 2.5 
        if ghosts and hasattr(self.ghosts_start[0], 'collideRadius'):
            self.ghost_radius = self.ghosts_start[0].collideRadius
    def search(self):
        start_time = time.time()
        self.current_pellet_tuples.clear()
        self.current_power_pellet_tuples.clear()
        if self.pellets_start and hasattr(self.pellets_start, 'pelletList'):
            for p in self.pellets_start.pelletList:
                if hasattr(p, 'position'):
                    self.current_pellet_tuples.add(p.position.asTuple())
                elif p.name == POWERPELLET: 
                    self.current_power_pellet_tuples.add(p.position.asTuple())
        self.any_pellet_tuples = self.current_pellet_tuples.union(self.current_power_pellet_tuples)

        initial_ghost_states = []
        self.blinky_sim_id = None
        for g in self.ghosts_start:
             if hasattr(g, 'position') and hasattr(g, 'mode') and hasattr(g.mode, 'current'):
                   gid = getattr(g, 'id', id(g))
                   if g.name == BLINKY and self.blinky_sim_id is None:
                      self.blinky_sim_id = gid
                   initial_ghost_states.append({
                      'id': gid,
                      'position': g.position.copy(),
                      'mode': g.mode.current,
                  })
        if self.blinky_sim_id is None and any(g['name'] == INKY for g in initial_ghost_states):
             print("MCTS Warning: Blinky's ID not found, Inky simulation might be inaccurate.")
        root_pos = self._get_aligned_pacman_pos()
        if root_pos is None:
            print("MCTS FATAL ERROR: Cannot determine root node position!")
            return STOP
        initial_valid_moves = self._get_valid_moves(root_pos)
        if len(initial_valid_moves) > 1 and self.last_actual_move != STOP:
             reverse_last_actual = -self.last_actual_move
             if reverse_last_actual in initial_valid_moves:
                  initial_valid_moves.remove(reverse_last_actual)

        if not initial_valid_moves:
            return self.last_actual_move if self.last_actual_move != STOP else STOP


        root_node = MonteCarloNode(position=root_pos, possible_moves=initial_valid_moves)
        for i in range(self.N):
            selected_node = self._selection(root_node)
            node_is_terminal_by_walls = not self._get_valid_moves(selected_node.position)

            simulation_start_node = selected_node

            if not node_is_terminal_by_walls and not selected_node.is_fully_expanded():
                newly_expanded_node = self._expansion(selected_node) 
                if newly_expanded_node:
                     simulation_start_node = newly_expanded_node


            if simulation_start_node:
                reward = self._simulation(simulation_start_node, initial_ghost_states) 
                self._backpropagation(simulation_start_node, reward)

        self.current_dangerous_ghost_positions = []
        for g in self.ghosts_start:
             if hasattr(g, 'mode') and hasattr(g.mode, 'current') and g.mode.current != SPAWN:
                  if hasattr(g, 'position'):
                       self.current_dangerous_ghost_positions.append(g.position)
        best_move = self._get_best_move_from_root(root_node)
        return best_move if best_move is not None else STOP

    def _get_aligned_pacman_pos(self):
        if hasattr(self.pacman_start, 'node') and self.pacman_start.node and \
           hasattr(self.pacman_start.node, 'position') and \
           self.pacman_start.node.position.asTuple() in self.maze_nodes:
             return self.pacman_start.node.position
        pac_pos = self.pacman_start.position
        aligned_x = int(round(pac_pos.x / TILEWIDTH) * TILEWIDTH)
        aligned_y = int(round(pac_pos.y / TILEHEIGHT) * TILEHEIGHT)
        closest_node_pos = None
        min_dist_sq = float('inf')

        for node_pos_tuple, node in self.maze_nodes.items():
            dist_sq = (Vector2(aligned_x, aligned_y) - node.position).magnitudeSquared()

            if dist_sq < min_dist_sq and dist_sq < (TILEWIDTH / 2)**2 :
                min_dist_sq = dist_sq
                closest_node_pos = node.position

        if closest_node_pos:
            return closest_node_pos
        min_dist_sq = float('inf')
        absolute_closest_node_pos = None
        for node_pos_tuple, node in self.maze_nodes.items():
            dist_sq = (pac_pos - node.position).magnitudeSquared()
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                absolute_closest_node_pos = node.position
        
        return absolute_closest_node_pos

    def _get_valid_moves(self, position):
        moves = []
        pos_tuple = position.asTuple()
        node = self.maze_nodes.get(pos_tuple)

        if not node: return []
        if not hasattr(node, 'neighbors') or not isinstance(node.neighbors, dict):
             return []

        for move_dir, neighbor_node in node.neighbors.items():
            if move_dir == PORTAL:
                continue
            if neighbor_node and hasattr(neighbor_node, 'position'):
                moves.append(move_dir)
        return moves

    def _selection(self, node):
        current_node = node
        while True:
            node_valid_moves = self._get_valid_moves(current_node.position)

            if not node_valid_moves:
                 return current_node 

            if not current_node.is_fully_expanded():
                return current_node
            else:
                best_child = current_node.select_best_child()
                if best_child is None:
                    return current_node 
                current_node = best_child

    def _expansion(self, node):
        if not node.untried_moves:
            return None

        move = random.choice(node.untried_moves)
        node.untried_moves.remove(move)
        current_pos_tuple = node.position.asTuple()
        current_maze_node = self.maze_nodes.get(current_pos_tuple)
        if not current_maze_node or \
           not hasattr(current_maze_node, 'neighbors') or \
           move not in current_maze_node.neighbors or \
           current_maze_node.neighbors[move] is None or \
           not hasattr(current_maze_node.neighbors[move], 'position'):
            return None

        next_pos = current_maze_node.neighbors[move].position
        valid_moves_from_new_pos = self._get_valid_moves(next_pos)
        new_node = MonteCarloNode(position=next_pos, parent=node, move_leading_here=move, possible_moves=valid_moves_from_new_pos)
        node.children[move] = new_node
        return new_node

    def _simulation(self, start_node, initial_ghost_states):
        sim_pacman_pos = start_node.position.copy()
        sim_pacman_dir = start_node.move_leading_here if start_node.parent else self.last_actual_move 

        sim_pellets = self.current_pellet_tuples.copy()
        sim_power_pellets = self.current_power_pellet_tuples.copy()
        sim_ghosts = []
        sim_blinky_pos = None
        for gs_init in initial_ghost_states:
            g_state={
                'id': gs_init.get('id'),
                'position': gs_init.get('position',Vector2()).copy(),
                'mode': gs_init.get('mode'),
                'direction': gs_init.get('direction', STOP), 
                'goal': Vector2()
            }
            sim_ghosts.append(g_state)
            if gs_init.get('id') == self.blinky_sim_id:
                sim_blinky_pos = g_state['position']


        total_reward = 0.0
        visited_in_sim = {start_node.position.asTuple()}
        last_sim_move = start_node.move_leading_here
        for depth in range(self.simulation_depth):
            dangerous_ghost_positions = [] 
            next_blinky_pos = None 

            for g_sim in sim_ghosts:
                g_pos = g_sim.get('position')
                g_mode = g_sim.get('mode')
                g_name = g_sim.get('name')
                g_dir = g_sim.get('direction',STOP)
                g_id = g_sim.get('id')

                current_goal = Vector2() 
                if g_mode == SCATTER:
                    if g_name == BLINKY: current_goal = Vector2(SCREENWIDTH, 0) 
                    elif g_name == PINKY: current_goal = Vector2(0, 0) 
                    elif g_name == INKY: current_goal = Vector2(SCREENWIDTH, SCREENHEIGHT) 
                    elif g_name == CLYDE: current_goal = Vector2(0, SCREENHEIGHT) 
                elif g_mode == CHASE:
                    pac_pos = sim_pacman_pos
                    pac_dir_vec = DIRECTIONS.get(sim_pacman_dir, Vector2(0,0)) 

                    if g_name == BLINKY:
                        current_goal = pac_pos
                    elif g_name == PINKY:
                        current_goal = pac_pos + pac_dir_vec * TILEWIDTH * 4
                    elif g_name == INKY:
                        if sim_blinky_pos is not None: 
                            vec1 = pac_pos + pac_dir_vec * TILEWIDTH * 2
                            vec2 = (vec1 - sim_blinky_pos) * 2
                            current_goal = sim_blinky_pos + vec2
                        else:
                            current_goal = pac_pos 
                    elif g_name == CLYDE:
                        d_sq = (pac_pos - g_pos).magnitudeSquared()
                        if d_sq <= (TILEWIDTH * 8)**2:
                            current_goal = Vector2(0, SCREENHEIGHT)
                            current_goal = pac_pos + pac_dir_vec * TILEWIDTH * 4
                    else: 
                         current_goal = pac_pos
                elif g_mode == SPAWN:
                     current_goal = g_pos 

                g_sim['goal'] = current_goal 
                ghost_node = self.maze_nodes.get(g_pos.asTuple())
                valid_neighbor_moves = {}

                if ghost_node and hasattr(ghost_node, 'neighbors'):
                    for move_dir, neighbor_node_or_const in ghost_node.neighbors.items():
                        if neighbor_node_or_const and neighbor_node_or_const != PORTAL and hasattr(neighbor_node_or_const, 'position'):

                             if move_dir != -g_dir:
                                valid_neighbor_moves[move_dir] = neighbor_node_or_const.position
                    if not valid_neighbor_moves and g_dir != STOP:
                         reverse_dir = -g_dir
                         if reverse_dir in ghost_node.neighbors:
                              neighbor_node_or_const = ghost_node.neighbors[reverse_dir]
                              if neighbor_node_or_const and neighbor_node_or_const != PORTAL and hasattr(neighbor_node_or_const, 'position'):
                                   valid_neighbor_moves[reverse_dir] = neighbor_node_or_const.position


                next_g_pos = g_pos
                chosen_move_dir = STOP

                if valid_neighbor_moves:
                    best_move_dir = STOP
                    min_dist_sq = float('inf')
                    shuffled_dirs = list(valid_neighbor_moves.keys())
                    random.shuffle(shuffled_dirs)

                    for move_dir in shuffled_dirs:
                        neighbor_pos = valid_neighbor_moves[move_dir]
                        dist_sq = (neighbor_pos - current_goal).magnitudeSquared()
                        if dist_sq < min_dist_sq:
                            min_dist_sq = dist_sq
                            best_move_dir = move_dir

                    chosen_move_dir = best_move_dir
                    if chosen_move_dir != STOP:
                        next_g_pos = valid_neighbor_moves[chosen_move_dir]
                g_sim['position'] = next_g_pos
                g_sim['direction'] = chosen_move_dir 
                if g_sim['id'] == self.blinky_sim_id:
                    next_blinky_pos = next_g_pos.copy() 
                if g_mode != SPAWN: 
                    dangerous_ghost_positions.append(g_sim['position']) 
            if next_blinky_pos is not None:
                sim_blinky_pos = next_blinky_pos
            pos_tuple = sim_pacman_pos.asTuple()
            if collideGhosts(sim_pacman_pos, dangerous_ghost_positions, self.pacman_radius, self.ghost_radius):
                 total_reward += self.PENALTY_DEATH
                 break 
            if nextToGhostsSQ(sim_pacman_pos, dangerous_ghost_positions, self.GHOST_NEAR_THRESHOLD):
                 total_reward += self.PENALTY_GHOST_NEAR
                

           
            pos_tuple = sim_pacman_pos.asTuple()
            ate_pellet_this_step = False
            if pos_tuple in sim_pellets:
                total_reward += self.REWARD_PELLET
                sim_pellets.remove(pos_tuple)
                ate_pellet_this_step
            elif pos_tuple in sim_power_pellets:
                total_reward += self.REWARD_POWER_PELLET
                sim_power_pellets.remove(pos_tuple)
                ate_pellet_this_step = True
            elif not ate_pellet_this_step:
                total_reward += self.EMPTY_TILE_PENALTY

            if not sim_pellets and not sim_power_pellets:
                total_reward += self.REWARD_CLEAR_LEVEL
                break

            
            active_threat_positions = []
            possible_moves_now = self._get_valid_moves(sim_pacman_pos)
            move_to_avoid = -last_sim_move if last_sim_move != STOP and last_sim_move is not None else None
            filtered_moves = possible_moves_now
            if len(possible_moves_now) > 1 and move_to_avoid is not None and move_to_avoid in possible_moves_now:
                filtered_moves = [m for m in possible_moves_now if m != move_to_avoid]
                if not filtered_moves: 
                    filtered_moves = possible_moves_now

            if not filtered_moves:
                break 
            chosen_move = random.choice(filtered_moves)
            current_node_maze = self.maze_nodes.get(sim_pacman_pos.asTuple())
            if not current_node_maze or chosen_move not in current_node_maze.neighbors or current_node_maze.neighbors[chosen_move] is None:
                break 

            next_pacman_pos = current_node_maze.neighbors[chosen_move].position
            sim_pacman_pos = next_pacman_pos
            sim_pacman_dir = chosen_move 
            pos_tuple = sim_pacman_pos.asTuple()
            if pos_tuple in visited_in_sim:
                total_reward += self.PENALTY_REVISIT
            visited_in_sim.add(pos_tuple)
            total_reward += self.REWARD_PROGRESS
            if last_sim_move != STOP and last_sim_move is not None and chosen_move == -last_sim_move:
                 total_reward += self.PENALTY_REVERSE_MOVE

            last_sim_move = chosen_move
            if not sim_pellets and not sim_power_pellets:
                total_reward += self.REWARD_CLEAR_LEVEL
                break #
        return total_reward


    def _backpropagation(self, node, reward):
        current_node = node
        while current_node is not None:
            current_node.visits += 1
            current_node.value += reward
            current_node = current_node.parent

    def _get_best_move_from_root(self, root_node):
        if not root_node:
            
            return self.last_actual_move if self.last_actual_move != STOP else STOP
        safe_pellet_moves = []
        safe_nonpellet_moves = []
        unsafe_pellet_moves = []
        unsafe_nonpellet_moves = []
        if not root_node.children:
             safe_initial_moves = []
             unsafe_initial_moves = []
             current_dangerous_pos = self.current_dangerous_ghost_positions 
             root_maze_node_fallback = self.maze_nodes.get(root_node.position.asTuple())
             if not root_maze_node_fallback:
                 return self.last_actual_move if self.last_actual_move != STOP else STOP

             for move in root_node.possible_moves:
                 neighbor = root_maze_node_fallback.neighbors.get(move)
                 if neighbor is None or neighbor == PORTAL or not hasattr(neighbor, 'position'):
                      continue 

                 next_pos = neighbor.position
                 is_safe = True
                 if collideGhosts(next_pos, current_dangerous_pos, self.pacman_radius, self.ghost_radius): is_safe = False
                 elif nextToGhostsSQ(next_pos, current_dangerous_pos, self.GHOST_NEAR_THRESHOLD): is_safe = False

                 if is_safe: safe_initial_moves.append(move)
                 else: unsafe_initial_moves.append(move)

             if safe_initial_moves: return random.choice(safe_initial_moves)
             if unsafe_initial_moves: return random.choice(unsafe_initial_moves)
             return self.last_actual_move if self.last_actual_move != STOP else STOP 
        
        for move,child in root_node.children.items():
            child_pos = child.position
            is_pellet_move = child_pos.asTuple() in self.any_pellet_tuples
            is_safe_move = True
            if collideGhosts(child_pos, self.current_dangerous_ghost_positions, self.pacman_radius, self.ghost_radius):
                is_safe_move = False
            elif nextToGhostsSQ(child_pos, self.current_dangerous_ghost_positions, self.GHOST_NEAR_THRESHOLD):
                is_safe_move = False
            move_tuple = (move, child)
            if is_safe_move:
                if is_pellet_move: safe_pellet_moves.append(move_tuple)
                else: safe_nonpellet_moves.append(move_tuple)
            else:
                 if is_pellet_move: unsafe_pellet_moves.append(move_tuple)
                 else: unsafe_nonpellet_moves.append(move_tuple)
        
        best_move = None
        def select_best_from_list(move_list):
            best_move_in_list = None; max_avg_value = -float('inf')
            visited = False 
            random.shuffle(move_list)
            for move, child in move_list:
                if child.visits > 0:
                    visited = True; avg_value = child.value / child.visits
                    if avg_value > max_avg_value: max_avg_value = avg_value; best_move_in_list = move
            if not visited and move_list: return random.choice(move_list)[0]
            return best_move_in_list
        if not best_move and safe_pellet_moves: best_move = select_best_from_list(safe_pellet_moves)
        if not best_move and safe_nonpellet_moves: best_move = select_best_from_list(safe_nonpellet_moves)
        if best_move is None:
             if not best_move and unsafe_pellet_moves: best_move = select_best_from_list(unsafe_pellet_moves)
             if not best_move and unsafe_nonpellet_moves: best_move = select_best_from_list(unsafe_nonpellet_moves)

        if best_move is None:
            if root_node.possible_moves:
                 best_move = random.choice(root_node.possible_moves)
            else: 
                 best_move = STOP
        return best_move if best_move is not None else STOP