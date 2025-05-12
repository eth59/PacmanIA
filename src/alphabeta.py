from utils import manhattanDistance
from constants import PELLET, POWERPELLET
import random

class AlphaBeta:
    
    def __init__(self, gameState):
        self.gameState = gameState
        
    def evaluate(self, curent_action):
        pacman_pos = self.gameState.pacman.position
        pellets = self.gameState.pellets
        score = 0
        
        # On influence le score en fonction de la distance aux 5 pellets les plus proches
        distances = sorted([manhattanDistance(pacman_pos, pellet.position) for pellet in pellets])
        score -= 0.5 * sum(distances[:5])
        
        # On influence le score en fonction de la distance aux fantômes
        for ghost in self.gameState.ghosts.ghosts:
            ghost_pos = ghost.position
            distance = manhattanDistance(pacman_pos, ghost_pos)
            if ghost.mode.current == 2 and distance < 150: # Ghost is frightened
                # TODO : fonctionne pas parce que ghost.mode.current vaut toujours 0, c'est bizarre
                score += 1000000/(distance+1)
            elif ghost.mode.current != 2 and distance < 150: # Ghost is not frightened
                score -= 1000000/(distance+1)
            
        return score
        
    def alphabeta(self, alpha, beta, depth, limit, agentIndex, curent_action):
        if depth == limit:
            return self.evaluate(curent_action)
        
        legal_actions = self.gameState.getLegalActions(agentIndex)
        
        if agentIndex == 0: # maj alpha, pacman turn
            if not legal_actions:
                raise ValueError("No legal actions available for pacman!")
            value = float('-inf')
            for action in legal_actions:
                next_state = self.gameState.generateNextState(agentIndex, action)
                if next_state is not None:
                    ab = AlphaBeta(next_state)
                    value = max(value, ab.alphabeta(alpha, beta, depth + 1, limit, 1, action))
                    alpha = max(alpha, value)
                    if beta <= alpha:
                        break
            return value
            
        else: # maj beta, ghost turn
            if not legal_actions:
                # Ghost can't move, go for the next agent
                next_depth = depth + 1 if agentIndex == 4 else depth
                return self.alphabeta(alpha, beta, next_depth, limit, (agentIndex + 1) % 5, curent_action)
            value = float('inf')
            for action in legal_actions:
                next_state = self.gameState.generateNextState(agentIndex, action)
                if next_state is not None:
                    ab = AlphaBeta(next_state)
                    next_depth = depth + 1 if agentIndex == 4 else depth
                    value = min(value, ab.alphabeta(alpha, beta, next_depth, limit, (agentIndex + 1) % 5, action))
                    beta = min(beta, value)
                    if beta <= alpha:
                        break
            return value
        
        
    def getBestMove(self, depth_limit=4): # utiliser un nombre pair
        best_score = float('-inf')
        best_action = None

        actions = self.gameState.getLegalActions(0)
        if not actions:
            raise ValueError("No legal actions available for pacman!")

        res_dict = {}
        for action in actions:
            next_state = self.gameState.generateNextState(0, action)
            next_state.previous_state = self.gameState
            ab = AlphaBeta(next_state)
            score = ab.alphabeta(float('-inf'), float('inf'), 1, depth_limit, 1, action)
            res_dict[action] = score
            if score > best_score:
                best_score = score
                best_action = action
        
        # Si plusieurs actions ont le même score, choisir aléatoirement parmi elles
        actions_with_best_score = [action for action, score in res_dict.items() if score == best_score]
        if len(actions_with_best_score) > 1:
            best_action = random.choice(actions_with_best_score)
        
        if best_action is None:
            raise ValueError("No valid action found!")
        return best_action
