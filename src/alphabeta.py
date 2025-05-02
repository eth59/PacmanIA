from constants import UP, DOWN, LEFT, RIGHT
from utils import manhattanDistance

class AlphaBeta:
    
    def __init__(self, gameState):
        self.gameState = gameState
        
    def evaluate(self):
        state = self.gameState
        score = 0
        
        if state.previous_state:
            prev_gommes = set((x, y, t) for (x, y, t) in state.previous_state.getGommesPos())
            curr_gommes = set((x, y, t) for (x, y, t) in state.getGommesPos())
            eaten = prev_gommes - curr_gommes
            
            for (_, _, t) in eaten:
                if t == 'small':
                    score += 10
                elif t == 'big':
                    score += 100
        
        for ghost_pos in state.getGhostsPos():
            dist = manhattanDistance(state.getPacmanPos(), ghost_pos)
            if state.getIsFrite():
                score += 250
            elif dist == 0:
                score -= 10000
            elif dist <= 2:
                score -= 50
                
        return score    
        
        
    def alphabeta(self, alpha, beta, depth, limit, agentIndex):
        if depth == limit:
            return self.evaluate()
        
        legal_actions = [UP, DOWN, LEFT, RIGHT]
        if not legal_actions:
            return self.evaluate()
        
        isPacMan = agentIndex == 0
        
        if isPacMan: # maj alpha
            value = float('-inf')
            for action in legal_actions:
                next_state = self.gameState.generateNextState(agentIndex, action)
                if next_state is not None:
                    ab = AlphaBeta(next_state)
                    value = max(value, ab.alphabeta(alpha, beta, depth + 1, limit, 1))
                    alpha = max(alpha, value)
                    if beta <= alpha:
                        break
            return value
            
        else: # maj beta
            value = float('inf')
            for action in legal_actions:
                next_state = self.gameState.generateNextState(agentIndex, action)
                if next_state is not None:
                    ab = AlphaBeta(next_state)
                    value = min(value, ab.alphabeta(alpha, beta, depth + 1, limit, agentIndex + 1 % 5))
                    beta = min(beta, value)
                    if beta <= alpha:
                        break
            return value
        
        
    def getBestMove(self, depth_limit=10):
        best_score = float('-inf')
        best_action = None

        actions = [UP, DOWN, LEFT, RIGHT]

        for action in actions:
            next_state = self.gameState.generateNextState(0, action)
            if next_state is not None:
                ab = AlphaBeta(next_state)
                score = ab.alphabeta(alpha=float('-inf'), beta=float('inf'), depth=1, limit=depth_limit, agentIndex=1)

                if score > best_score:
                    best_score = score
                    best_action = action

        if best_action is None:
            raise ValueError("No valid action found!")
        return best_action
