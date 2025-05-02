from mazedata import MazeData
from nodes import NodeGroup, Node
from constants import UP, DOWN, LEFT, RIGHT, PACMAN, GHOST

class State:
    def __init__(self, pacman, ghosts, is_frite, gommes_pos, level, previous_state=None):
        self.pacman = pacman
        self.ghosts = ghosts
        self.pacman_node = pacman.node
        self.ghosts_nodes = ghosts.getGhostsNodes()
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
    
    def generateNextState(self, agentIndex, action):
        """Generate the next state based on the current state and the action taken.

        Args:
            agentIndex (int): 0 for Pacman, 1/2/3/4 for Ghosts.
            action (int): UP, DOWN, LEFT, RIGHT constants.
        """
        isPacMan = agentIndex == 0
        
        # Get the current position (either pacman or ghost)
        node = self.pacman_node if isPacMan else self.ghosts_nodes[agentIndex - 1]
        
        if node is None:
            print("Invalid node!")
            return None
            
        # Check if movement in that direction is possible
        if isPacMan:
            is_valid_move = self.pacman.validDirection(action)
        else:
            is_valid_move = self.ghosts.ghosts[agentIndex - 1].validDirection(action)
        
        if not is_valid_move:
            print("Invalid move!")
            return None
        
        # Pacman's movement
        if isPacMan:
            # Move pacman to the new node
            new_node = node.neighbors[action]
            if new_node is not None:
                new_pacman = self.pacman.copy()
                new_pacman.node = new_node
                new_pacman.setBetweenNodes(action)
                return State(new_pacman, self.ghosts, self.is_frite, self.gommes_pos, self.level, self)
            else:
                raise ValueError("Pacman cannot move in that direction!")
            
            
        # Ghost's movement
        else:
            # Move ghost to the new node
            new_node = node.neighbors[action]
            if new_node is not None:
                new_ghosts = self.ghosts.copy()
                new_ghost = new_ghosts.ghosts[agentIndex - 1].copy()
                new_ghost.node = new_node
                new_ghost.setBetweenNodes(action)
                new_ghosts.ghosts[agentIndex - 1] = new_ghost
                return State(self.pacman, new_ghosts, self.is_frite, self.gommes_pos, self.level, self)
            else:
                raise ValueError("Ghost cannot move in that direction!")
