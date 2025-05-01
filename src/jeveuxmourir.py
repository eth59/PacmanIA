import heapq
from vector import Vector2
from constants import *

PERIMETREdeDANGER=(TILEWIDTH*4)**2
FANTOMEpenalite= 500
PERIMETREdeFUITE =(TILEWIDTH *6)**2
PERIMETREdeFUITE_URGENTE =(TILEWIDTH *2)**2
SCOREfuiteversSECURITE=1.0
PENALITEfuite=0.0
diametre_mange_PELLET =(TILEWIDTH*0.3)**2


class DijkstraAI:
    def __init__(self, nodes, pacman, pellets, ghosts):
        self.nodes_group =nodes
        self.pacman =pacman
        self.pellets =pellets
        self.ghosts =ghosts if ghosts is not None else []
        self.nodes_lut=nodes.nodesLUT
        self.last_target_pos=None
        self.power_pellet_nodes= self.getPowerPelletNodes()
        self.last_flee_target_node=None 
    def update_ghosts(self, ghosts):
        self.ghosts =ghosts if ghosts is not None else []

    def getPowerPelletNodes(self):
        pp_nodes =set()
        if not self.pellets or not hasattr(self.pellets, 'pelletList'): 
            return pp_nodes
        try: pellet_iter =iter(self.pellets.pelletList)
        except TypeError: 
            return pp_nodes
        for pellet in pellet_iter:
            if pellet and pellet.name ==POWERPELLET and pellet.visible:
                node =self.findNodePlusProche(pellet.position)
                if node: 
                    pp_nodes.add(node)
        return pp_nodes

    def updatePowerPelletNodes(self):
        new_pp_nodes =self.getPowerPelletNodes()
        if new_pp_nodes !=self.power_pellet_nodes:
            self.power_pellet_nodes =new_pp_nodes
            self.last_target_pos =None
            self.last_flee_target_node=None

    def findNodePlusProche(self, position, nodes_to_search=None):
        min_dist_sq=float('inf')
        closest_node=None
        search_space=nodes_to_search if nodes_to_search else self.nodes_lut.values()
        if not search_space or position is None:
            return None
        vec_pos=position if isinstance(position, Vector2) else Vector2(position[0], position[1])
        for node in search_space:
            if node and node.position:
                try:
                    dist_sq = (vec_pos - node.position).magnitudeSquared()
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        closest_node = node
                except Exception: continue
        return closest_node

    def getThreatGhosts(self, radius_sq):
        threatening =[]
        pac_pos =self.pacman.position
        if not self.ghosts or pac_pos is None: 
            return threatening
        for ghost in self.ghosts:
            if not (ghost and ghost.visible and hasattr(ghost, 'position') and ghost.position):
                continue
            current_mode = getattr(getattr(ghost, 'mode', None), 'current', None)
            if current_mode not in [FREIGHT, SPAWN]:
                try:
                    if (pac_pos-ghost.position).magnitudeSquared()<radius_sq:
                        threatening.append(ghost)
                except Exception: 
                    continue
        return threatening

    def nodeDangerous(self, node, dangerous_ghosts):
        if not dangerous_ghosts or node is None or node.position is None: return False
        node_pos=node.position
        for ghost in dangerous_ghosts:
            if ghost and ghost.position:
                try:
                    if (node_pos-ghost.position).magnitudeSquared()<PERIMETREdeDANGER: 
                        return True
                except Exception: continue
        return False

    def nodeNeighbors(self, node, dangerous_ghosts):
        neighbors=[]
        if node is None or node.neighbors is None: return neighbors
        apply_penalty =bool(dangerous_ghosts)
        for direction, neighbor_node in node.neighbors.items():
            if neighbor_node and neighbor_node.position:
                cost =max(1.0, (neighbor_node.position-node.position).magnitude())
                if apply_penalty and self.nodeDangerous(neighbor_node, dangerous_ghosts):
                    cost +=FANTOMEpenalite
                if self.pacman.name in node.access.get(direction, []):
                    neighbors.append((neighbor_node, cost))
        return neighbors

    def dijkstra(self, start_node, threatening_ghosts):
        if start_node is None: 
            return {}, {}
        if start_node not in self.nodes_lut.values():
             actual_start_node = self.findNodePlusProche(start_node.position, self.nodes_lut.values())
             if actual_start_node is None:
                 return {}, {}
             start_node = actual_start_node

        distances = {node: float('inf') for node in self.nodes_lut.values()}
        previous_nodes = {node: None for node in self.nodes_lut.values()}
        distances[start_node] = 0
        pq = [(0, id(start_node), start_node)]

        while pq:
            current_distance, _, current_node=heapq.heappop(pq)
            if current_node is None or distances.get(current_node, float('inf'))<current_distance: 
                continue
            neighbors_with_costs=self.nodeNeighbors(current_node,threatening_ghosts)
            for neighbor_node, cost in neighbors_with_costs:
                if neighbor_node is None: 
                    continue
                distance = current_distance + cost
                if distance < distances.get(neighbor_node, float('inf')):
                    distances[neighbor_node]=distance
                    previous_nodes[neighbor_node] =current_node
                    heapq.heappush(pq, (distance, id(neighbor_node),neighbor_node))
        return distances, previous_nodes

    def pathReconstruction(self, previous_nodes, start_node, target_node):
        path =[]
        if start_node is None or target_node is None or not previous_nodes:
            return None
        if start_node==target_node:
            return [start_node]
        current_start_node = None; current_target_node = None
        target_pos = target_node.position.asTuple()
        start_pos = start_node.position.asTuple()
        for node_obj in previous_nodes.keys():
            if node_obj.position.asTuple() == start_pos:
                current_start_node = node_obj
            if node_obj.position.asTuple() == target_pos: 
                current_target_node = node_obj
            if current_start_node and current_target_node: 
                break
        if current_target_node is None:
             for node_obj in previous_nodes.values():
                 if node_obj and node_obj.position.asTuple() == target_pos:
                     current_target_node = node_obj
                     break
        if current_start_node is None or current_target_node is None: 
            return None
        start_node_lut= current_start_node; target_node_lut = current_target_node
        current =target_node_lut
        if target_node_lut != start_node_lut and previous_nodes.get(target_node_lut) is None: 
            return None
        count=0
        max_count=len(self.nodes_lut)+15
        while current is not None and current!=start_node_lut:
            path.append(current)
            count += 1
            if count > max_count:
                return None
            prev = previous_nodes.get(current)
            if prev == current:
                return None
            current= prev
        if current ==start_node_lut:
            path.append(start_node_lut)
            path.reverse()
            return path
        else: 
            return None

    def dirNextNode(self, current_node, next_node):
        if current_node is None or next_node is None or current_node.neighbors is None: 
            return STOP
        for direction, neighbor in current_node.neighbors.items():
            if neighbor == next_node:
                return direction if self.pacman.name in current_node.access.get(direction, []) else STOP
        return STOP

    def emergencyflee(self, start_node, emergency_ghosts):
        if start_node is None or not emergency_ghosts or start_node.neighbors is None:
            return STOP
        valid_options= []
        last_actual_move =self.pacman.direction
        opposite_last_move =(last_actual_move * -1) if last_actual_move !=STOP else None

        for direction, neighbor_node in start_node.neighbors.items():
            if neighbor_node is not None and neighbor_node.position and self.pacman.name in start_node.access.get(direction, []):
                neighbor_pos = neighbor_node.position
                min_dist_sq_to_any_ghost = float('inf')
                for ghost in emergency_ghosts:
                    try:
                        dist_sq = (neighbor_pos - ghost.position).magnitudeSquared()
                        min_dist_sq_to_any_ghost = min(min_dist_sq_to_any_ghost,dist_sq)
                    except Exception:
                        continue
                safety_score = min_dist_sq_to_any_ghost
                if direction==opposite_last_move:
                    safety_score-=FANTOMEpenalite
                valid_options.append((safety_score,direction))

        if not valid_options:
            return STOP
        valid_options.sort(key=lambda x: x[0], reverse=True)
        best_score, best_direction= valid_options[0]
        return best_direction
    
   
    def bestPtTarget(self, distances, previous_nodes, start_node):
            target_node =None 
            target_pellet_obj = None
            final_path = None
            if not self.pellets or not hasattr(self.pellets, 'pelletList') or not self.pellets.pelletList: 
                return None, None, None
            pellet_options = []
            for pellet in self.pellets.pelletList:
                if not pellet or not pellet.visible or pellet.position is None: 
                    continue
                p_node =self.findNodePlusProche(pellet.position, distances.keys())
                if p_node and distances.get(p_node, float('inf')) < float('inf'):
                    pellet_options.append((distances[p_node], p_node, pellet))
            if not pellet_options:
                return None, None, None
            pellet_options.sort(key=lambda x: x[0])
            for cost, p_node, p_obj in pellet_options:
                path= self.pathReconstruction(previous_nodes, start_node, p_node)
                if path and len(path) > 0:
                    target_node, target_pellet_obj, final_path = p_node, p_obj, path
                    break
            return target_node, target_pellet_obj, final_path

    def safestNode(self, distances, threatening_ghosts):
        max_safety_score =float('-inf')
        safest_node=None
        for node, cost in distances.items():
            if cost == float('inf') or node.position is None:
                continue
            min_dist_sq_to_ghost =float('inf')
            for ghost in threatening_ghosts:
                try:
                    dist_sq = (node.position-ghost.position).magnitudeSquared()
                    min_dist_sq_to_ghost=min(min_dist_sq_to_ghost, dist_sq)
                except Exception:
                    continue
            safety_score = (min_dist_sq_to_ghost * SCOREfuiteversSECURITE) - (cost * PENALITEfuite)
            if safety_score > max_safety_score:
                max_safety_score = safety_score
                safest_node = node

        return safest_node

    def nextDir(self):
        if not self.pacman or not self.pacman.alive or self.pacman.position is None:
            return STOP
        if not self.nodes_lut:
            return STOP

        self.updatePowerPelletNodes()
        start_node = self.findNodePlusProche(self.pacman.position, self.nodes_lut.values())
        if not start_node:
            return STOP
        last_actual_move=self.pacman.direction
        emergency_ghosts=self.getThreatGhosts(PERIMETREdeFUITE_URGENTE)
        threatening_ghosts= self.getThreatGhosts(PERIMETREdeFUITE)
        is_fleeing=bool(threatening_ghosts)

        if emergency_ghosts:
            emergency_direction=self.emergencyflee(start_node, emergency_ghosts)
            if emergency_direction not in [None, STOP]:
                self.last_flee_target_node = None
                self.last_target_pos = None
                #print("emergency direction test:", emergency_direction)
                return emergency_direction
            else:
                is_fleeing = True
                if not threatening_ghosts:
                    threatening_ghosts = emergency_ghosts
        distances, previous_nodes =self.dijkstra(start_node, threatening_ghosts if is_fleeing else [])
        #print("distance:", distances)
        #print("previous:", previous_nodes)
        if not distances or not previous_nodes:
            return STOP
        target_node =None
        target_pellet_obj=None
        final_path=None

        if is_fleeing:
            self.last_target_pos=None
            target_node =self.safestNode(distances, threatening_ghosts)
            if target_node:
                final_path =self.pathReconstruction(previous_nodes, start_node, target_node)
                if final_path:
                    self.last_flee_target_node =target_node
                else:
                    target_node = None
        else: 
            self.last_flee_target_node = None
            target_node, target_pellet_obj, final_path =self.bestPtTarget(distances, previous_nodes, start_node)
        if target_node is None or final_path is None or not final_path:
            if last_actual_move != STOP and start_node.neighbors.get(last_actual_move):
                return last_actual_move
            valid_directions=[]
            for direction, neighbor_node in start_node.neighbors.items():
                if neighbor_node and self.pacman.name in start_node.access.get(direction, []):
                    valid_directions.append(direction)
            if valid_directions:
                safe_directions =[]
                for direction in valid_directions:
                    neighbor_node =start_node.neighbors[direction]
                    min_dist_sq_to_any_ghost =float('inf')
                    for ghost in self.ghosts:
                        try:
                            dist_sq =(neighbor_node.position-ghost.position).magnitudeSquared()
                            min_dist_sq_to_any_ghost =min(min_dist_sq_to_any_ghost, dist_sq)
                        except Exception:
                            continue
                    safe_directions.append((min_dist_sq_to_any_ghost, direction))
                safe_directions.sort(reverse=True, key=lambda x: x[0])
                return safe_directions[0][1] 

            return STOP
        if final_path[0] !=start_node:
            return STOP
        next_direction = STOP
        if len(final_path)>1:
            next_node_on_path =final_path[1]
            next_direction = self.dirNextNode(start_node, next_node_on_path)

        elif len(final_path) ==1:
            if is_fleeing:
                next_direction =STOP
                self.last_flee_target_node =None
            elif target_pellet_obj and target_pellet_obj.position: 
                dist_sq_pacman_pos =(self.pacman.position-target_pellet_obj.position).magnitudeSquared()
                if dist_sq_pacman_pos<diametre_mange_PELLET:
                    next_direction = STOP
                    self.last_target_pos=None
                else:
                    delta =target_pellet_obj.position - start_node.position
                    preferred_direction =STOP
                    if abs(delta.x) > abs(delta.y):
                        preferred_direction =RIGHT if delta.x >0 else LEFT
                    elif abs(delta.y) > 0:
                        preferred_direction =DOWN if delta.y>0 else UP

                    preferred_neighbor=start_node.neighbors.get(preferred_direction) if start_node.neighbors else None
                    can_move_preferred= False
                    if preferred_neighbor and self.pacman.name in start_node.access.get(preferred_direction, []):
                        can_move_preferred =True

                    if can_move_preferred:
                        next_direction =preferred_direction
                    else:  # Fallback logic
                        best_fallback_dir =STOP
                        valid_fallback_options =[]
                        neighbor_items =list(start_node.neighbors.items()) if start_node.neighbors else []
                        for d, neighbor_node in neighbor_items:
                            if neighbor_node and self.pacman.name in start_node.access.get(d, []) and neighbor_node.position:
                                try:
                                    valid_fallback_options.append(((neighbor_node.position - target_pellet_obj.position).magnitudeSquared(), d))
                                except:
                                    continue
                        if valid_fallback_options:
                            valid_fallback_options.sort()
                            best_dist_sq, best_dir =valid_fallback_options[0]
                            opposite_last_move_fallback= (last_actual_move*-1) if last_actual_move !=STOP else None
                            if best_dir ==opposite_last_move_fallback and len(valid_fallback_options) > 1:
                                best_fallback_dir = valid_fallback_options[1][1]
                            else:
                                best_fallback_dir =best_dir
                            next_direction =best_fallback_dir

        if next_direction is None:
            next_direction=STOP
        return next_direction