class State:
    def __init__(self, pacman_pos, ghosts_pos, is_frite, gommes_pos, previous_state=None, level=0):
        from nodes import NodeGroup
        self.pacman_pos = pacman_pos
        self.ghosts_pos = ghosts_pos
        self.is_frite = is_frite
        self.gommes_pos = gommes_pos
        self.previous_state = previous_state
        self.level = level
        self.nodes = NodeGroup(level)
        
    def getPacmanPos(self):
        return self.pacman_pos
    
    def getGhostsPos(self):
        return self.ghosts_pos
    
    def getIsFrite(self):
        return self.is_frite
    
    def getGommesPos(self):
        return self.gommes_pos
    
    def getPreviousState(self):
        return self.previous_state
    
    def getNodeFromPos(self, pos):
        return self.nodes.getNodeFromPixels(pos[0], pos[1])
        
    def getLegalActions(self, isPacMan):
        from constants import UP, DOWN, LEFT, RIGHT, PACMAN, GHOST
        from nodes import NodeGroup
        
        # Check if a direction is valid for an entity at a given node
        def is_valid_direction(node, direction, entity_type):
            # Check if there's a neighbor in that direction and the entity has access
            if node.neighbors[direction] is not None and entity_type in node.access[direction]:
                return True
            return False

        if isPacMan:
            legal_actions = []
            current_node = self.getNodeFromPos(self.pacman_pos)
            if current_node:
                for direction in [UP, DOWN, LEFT, RIGHT]:
                    if is_valid_direction(current_node, direction, PACMAN):
                        legal_actions.append(direction)
            return legal_actions
        
        # Handle all ghosts
        all_ghost_actions = []
        for ghost_index, ghost_pos in enumerate(self.ghosts_pos):
            legal_actions = []
            current_node = self.getNodeFromPos(ghost_pos)
            
            if current_node:
                for direction in [UP, DOWN, LEFT, RIGHT]:
                    if is_valid_direction(current_node, direction, GHOST):
                        # Only check ghost collisions if not in fright mode
                        if not self.is_frite:
                            next_node = current_node.neighbors[direction]
                            if next_node:
                                ghost_collision = False
                                for other_index, other_ghost_pos in enumerate(self.ghosts_pos):
                                    if other_index != ghost_index:
                                        other_node = self.getNodeFromPos(other_ghost_pos)
                                        if other_node == next_node:
                                            ghost_collision = True
                                            break
                                if not ghost_collision:
                                    legal_actions.append(direction)
                        else:
                            legal_actions.append(direction)
            
            all_ghost_actions.append(legal_actions)
        
        return all_ghost_actions
    
    def generateNextState(self, isPacMan, action):
        from constants import UP, DOWN, LEFT, RIGHT
        
        # Get current position and node
        if isPacMan:
            current_pos = self.pacman_pos
            current_node = self.getNodeFromPos(current_pos)
            
            if current_node and current_node.neighbors[action]:
                # Get the next node's position
                next_node = current_node.neighbors[action]
                next_pos = next_node.position.asTuple()
                
                # Check if the new position has a pellet
                remaining_gommes = []
                for gomme in self.gommes_pos:
                    if gomme[:2] != next_pos:  # Only compare x,y coordinates
                        remaining_gommes.append(gomme)
                
                # Create new state with updated positions and pellets
                return State(
                    pacman_pos=next_pos,
                    ghosts_pos=self.ghosts_pos[:],  # Copy ghost positions
                    is_frite=self.is_frite,
                    gommes_pos=remaining_gommes,
                    previous_state=self,
                    level=self.level
                )
            
            # If move not possible, return copy of current state
            return State(
                pacman_pos=self.pacman_pos,
                ghosts_pos=self.ghosts_pos[:],
                is_frite=self.is_frite,
                gommes_pos=self.gommes_pos[:],
                previous_state=self,
                level=self.level
            )
        else:
            # For ghosts, action is a list of moves for each ghost
            new_ghost_positions = []
            for ghost_index, (ghost_pos, ghost_action) in enumerate(zip(self.ghosts_pos, action)):
                current_node = self.getNodeFromPos(ghost_pos)
                
                if current_node and ghost_action and current_node.neighbors[ghost_action]:
                    # Get the next node's position
                    next_node = current_node.neighbors[ghost_action]
                    new_ghost_positions.append(next_node.position.asTuple())
                else:
                    # If move not possible, keep current position
                    new_ghost_positions.append(ghost_pos)
            
            # Create new state with updated ghost positions
            return State(
                pacman_pos=self.pacman_pos,
                ghosts_pos=new_ghost_positions,
                is_frite=self.is_frite,
                gommes_pos=self.gommes_pos[:],
                previous_state=self,
                level=self.level
            )
