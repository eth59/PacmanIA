from constants import*


class MonteCarlo():
    def __init__(self, pacman, ghosts, pellets,level, N):
        self.pacman = pacman
        self.ghosts = ghosts
        self.pellets = pellets
        self.level=level
        self.N = N

    def selection(self):
        pass
    def expansion(self):
        pass
    def simulation(self):
        pass
    def backpropagation(self):
        pass
    
    def next_move(self): #renvoie 
        start = self.pacman.position
        

