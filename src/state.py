from mazedata import MazeData
from nodes import NodeGroup
from constants import UP, DOWN, LEFT, RIGHT, PACMAN, GHOST

class State:
    def __init__(self, pacman_node, ghosts_nodes, is_frite, gommes_pos, level, previous_state=None):
        self.pacman_node = pacman_node
        self.ghosts_nodes = ghosts_nodes
        self.is_frite = is_frite
        # Convert gommes to (x, y, type) tuples if they're not already
        self.gommes_pos = []
        for gomme in gommes_pos:
            if isinstance(gomme, tuple):
                self.gommes_pos.append(gomme)
            else:  # It's a Vector2
                t = 'big' if hasattr(gomme, 'points') and gomme.points == 50 else 'small'
                self.gommes_pos.append((gomme.x, gomme.y, t))
        self.previous_state = previous_state
        self.level = level
        self.mazedata = MazeData()
        self.mazedata.loadMaze(level)
        self.nodes = NodeGroup("resources/"+self.mazedata.obj.name+".txt")
        
    def getPacmanPos(self):
        return self.pacman_node
    
    def getGhostsPos(self):
        return self.ghosts_nodes
    
    def getIsFrite(self):
        return self.is_frite
    
    def getGommesPos(self):
        return self.gommes_pos
    
    def getPreviousState(self):
        return self.previous_state
    
    def getNodeFromPos(self, pos):
        return self.nodes.getNodeFromPixels(pos.x, pos.y)
        
    def getLegalActions(self, isPacMan):        
        # Check if a direction is valid for an entity at a given node
        def is_valid_direction(node, direction, entity_type):
            # Check if there's a neighbor in that direction and the entity has access
            if node.neighbors[direction] is not None and entity_type in node.access[direction]:
                return True
            return False

        if isPacMan:
            legal_actions = []
            current_node = self.pacman_node
            if current_node:
                for direction in [UP, DOWN, LEFT, RIGHT]:
                    if is_valid_direction(current_node, direction, PACMAN):
                        legal_actions.append(direction)
            return legal_actions
        
        # Handle all ghosts
        all_ghost_actions = []
        for ghost_index, ghost_pos in enumerate(self.ghosts_nodes):
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
                                for other_index, other_ghost_pos in enumerate(self.ghosts_nodes):
                                    if other_index != ghost_index:
                                        other_node = self.getNodeFromPos(other_ghost_pos)
                                        if other_node and other_node == next_node:
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
            current_node = self.pacman_node
            
            if current_node and current_node.neighbors[action]:
                # Get the next node's position
                next_node = current_node.neighbors[action]
                next_pos = next_node.position.asTuple()
                
                # Check if the new position has a pellet
                remaining_gommes = []
                for gomme in self.gommes_pos:
                    if (gomme[0], gomme[1]) != next_pos:  # Compare positions without type
                        remaining_gommes.append(gomme)  # Keep the complete tuple with type
                
                # Create new state with updated positions and pellets
                return State(
                    pacman_node=next_node,
                    ghosts_nodes=self.ghosts_nodes[:],  # Copy ghost nodes
                    is_frite=self.is_frite,
                    gommes_pos=remaining_gommes,
                    previous_state=self,
                    level=self.level
                )
            
            # If move not possible, return copy of current state
            return State(
                pacman_node=self.pacman_node,
                ghosts_nodes=self.ghosts_nodes[:],
                is_frite=self.is_frite,
                gommes_pos=self.gommes_pos[:],
                previous_state=self,
                level=self.level
            )
        else:
            # For ghosts, action is a list of moves for each ghost
            new_ghost_nodes = []
            for ghost_index, (ghost_pos, ghost_action) in enumerate(zip(self.ghosts_nodes, action)):
                current_node = self.getNodeFromPos(ghost_pos)
                if current_node and ghost_action and current_node.neighbors[ghost_action]:
                    # Get the next node's position
                    next_node = current_node.neighbors[ghost_action]
                    new_ghost_nodes.append(next_node.position)
                else:
                    # If move not possible, keep current position
                    new_ghost_nodes.append(ghost_pos)
            
            # Create new state with updated ghost positions
            return State(
                pacman_node=self.pacman_node,
                ghosts_nodes=new_ghost_nodes,
                is_frite=self.is_frite,
                gommes_pos=self.gommes_pos[:],
                previous_state=self,
                level=self.level
            )
