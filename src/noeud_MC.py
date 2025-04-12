from nodes import Node

class noeud_MonteCarlo:
    def __init__(self, node, pacman, ghosts,pellets, parent=None):
        self.node = node
        self.parent = parent
        self.children=[]
        self.moves = self.valid_moves()
        self.pellets = pellets
        self.pacman=pacman
        self.ghosts = ghosts
        self.score = 0
        self.nbvisits = 0
        self.value = 0


    def valid_moves(self):
        return list(self.node.neighbors.keys())
    
    def children(self):
        while self.moves is not None:
            move= self.moves.pop()
            if move is not None:
                new_node_pour_MC = self.node.neighbors[move]
                child_noeud_MC = noeud_MonteCarlo(new_node_pour_MC,self.pacman,self.ghosts,self.pellets, parent=self)
                self.children.append(child_noeud_MC)
                return child_noeud_MC
        return None