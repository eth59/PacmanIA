from constants import*
from noeud_MC import *
import math
import random

c= math.sqrt(2)

class MonteCarlo():
    def __init__(self, pacman, ghosts, pellets,level, N):
        self.pacman = pacman
        self.ghosts = ghosts
        self.pellets = pellets
        self.level=level
        self.N = N
        self.mc_node = noeud_MonteCarlo(Node(self.pacman.position.x, self.pacman.position.y),self.pacman, self.ghosts, self.pellets, parent=None)

    def selection(self, mc_node):
        while mc_node.children:  # Traverse until a leaf mc_node
            mc_node = max(mc_node.children,
                        key=lambda child: ((child.value / (child.nbvisits + 1e-6)) + c * math.sqrt(math.log(mc_node.visits + 1e-6) / (child.visits + 1e-6))))
        return mc_node

    def expansion(self, mc_node):
        mc_node.add_children()
        
    def simulation(self, mc_node):
        current_simulation_state = mc_node.node
        pacman = self.pacman
        pellets = self.pellets
        i=0
        while i<20:
            possible_moves= mc_node.moves
            move = random.choice(possible_moves)
            current_simulation_state= current_simulation_state.neighbors[move]
            i+=1 
            if current_simulation_state is None:
                break
            if pellets.isEmpty():
                return 1
        return 0

    def backpropagation(self, mc_node, resultat):
        while mc_node is not None:
            mc_node.nbvisits+=1
            mc_node.value += resultat
            mc_node = mc_node.parent

        
    
    def next_move(self):
        root = noeud_MonteCarlo(self.pacman.node, self.pacman,self.ghosts, self.pellets, parent=None)
        i=0
        while i<self.N:
            node= self.selection(root)
            if node.moves:
                node= self.expansion(node)
            resultat = self.simulation(node)
            self.backpropagation(node,resultat)
            i+=1
        best_child = max (root.children, key=lambda child: child.visits)
        for direction, neighbor in self.pacman.node.neighbors.items():
            if neighbor == best_child.node:
                return direction
        return STOP
        

