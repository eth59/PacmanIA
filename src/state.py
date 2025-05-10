from mazedata import MazeData
from nodes import NodeGroup
from constants import UP, DOWN, LEFT, RIGHT

class State:
    def __init__(self, pacman, ghosts, pellets):
        self.pacman = pacman
        self.ghosts = ghosts
        self.pellets = pellets
    
    def getLegalActions(self, agentIndex):
        """Get the legal actions for the given agent index.

        Args:
            agentIndex (int): 0 for Pacman, 1/2/3/4 for Ghosts.

        Returns:
            list: List of legal actions.
        """
        res = []
        for action in [UP, DOWN, LEFT, RIGHT]:
            if agentIndex == 0 and self.pacman.validDirection(action):
                res.append(action)
            elif agentIndex > 0 and self.ghosts.ghosts[agentIndex - 1].validDirection(action):
                res.append(action)
        return res
    
    def generateNextState(self, agentIndex, action):
        """Generate the next state based on the current state and the action taken.

        Args:
            agentIndex (int): 0 for Pacman, 1/2/3/4 for Ghosts.
            action (int): UP, DOWN, LEFT, RIGHT constants.
        """
        
        # Pacman's movement
        if agentIndex == 0:        
            # copy pacman
            new_pacman = self.pacman.copy()
            # Update pacman's position directly
            new_pacman.position += new_pacman.directions[action]*new_pacman.speed*0.1
            return State(new_pacman, self.ghosts, self.pellets)
            
        # Ghost's movement
        else:
            # copy ghost
            new_ghosts = self.ghosts.copy()
            # update ghost's position directly
            new_ghosts.ghosts[agentIndex - 1].position += new_ghosts.ghosts[agentIndex - 1].directions[action]*new_ghosts.ghosts[agentIndex - 1].speed*0.1
            return State(self.pacman, new_ghosts, self.pellets)
