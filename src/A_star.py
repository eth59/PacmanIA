import heapq
from vector import Vector2
from constants import *

class A_star():
    def __init__(self,ghosts,pellets,pacman,grid):
        self.ghosts = ghosts
        self.pellets = pellets
        self.pacman = pacman
        self.grid = grid
    def next_move (self):   # doit renvoyer UP, LEFT, DOWN, RIGHT ou STOP
        # lance a_star sur la grille de jeu avec le bon objectif
        #trouver l'objectif : choisir la bille la plus proche
        #il faut aussi considérer la place des fantômes
        # récupérer la position des fantômes :
        #self.ghosts = self.get_ghosts()
        #self.pacman = self.get_pacman()
        #self.food = self.get_food()
        #self.grid = self.get_grid()
        #commencer par les powerpellets ?
        #considérer les fruits et manger les fantômes ?

        # self.ghosts.pinky.position
        # inky
        # clyde
        # blinky
        # self.pellets.pelletList
        # if pellet.name == POWERPELLET:
            #qd un pellet est mangé il est enlevé de pelletList, pellet est un power pellet si pellet.name == POWERPELLET

        # récupère la liste des pellets et des fantômes
        


        #lancer a_star
        # goal = # position à definir
        start=self.pacman.position
        goal=self.get_closest_pellet()
        path=self.a_star(start,goal)
        if path is None:
            return STOP
        else:
            return self.get_direction(path[0],path[1])

    def a_star(self,start,goal):
        start_noeud = Noeud(start,0,0) #voir quoi mettre pour h
        open = []
        heapq.heappush(open, start_noeud)
        closed = []
        current=start_noeud
        while not open.isEmpty() and open[0].position != goal:
            open=self.supp_noeud(open,current.position)
            closed.append(current)
            neighbors = current.findNeighbors(pacman) #les voisins initialisés avec g=0 (et h=0 ?)
            for neighbor in neighbors:
                if (not self.appartenir(closed,neighbor.position) and not appartenir(open,neighbor.position)) or (self.appartenir(open,neighbor.position) and self.getGNoeud(open,neighbor.position)>current.g+1): #cout(s,s')=1
                    if self.appartenir(open,neighbor.position):
                        neighbor=self.supp_noeud(open,neighbor.position)
                    neighbor.g=current.g+1
                    neighbor.h= self.heuristic(neighbor,goal)
                    neighbor.f=neighbor.g+neighbor.h
                    neighbor.parent=current
                    heapq.heappush(open,neighbor)
                    if self.appartenir(closed,neighbor.position):
                        closed=self.supp_noeud(closed,neighbor.position)
            if not open.isEmpty():
                current=heapq.heappop(open)
        if open.isEmpty():
            return None
        else:
            path=[]
            while current.parent != None:
                path.append(current.position)
                current=current.parent
            return path[::-1]



    def supp_noeud(self,liste, position):
        l=[n for n in liste if n.position != position]
        return heapq.heapify(l)

    def appartenir(self,liste, position):
        return position in [n.position for n in liste]
    
    def getGNoeud(self,liste,position):
        return [n.g for n in liste if n.position == position][0]
    
    def heuristic(self, noeud, goal):
        return abs(noeud.position[0]-goal[0])+abs(noeud.position[1]-goal[1])


class Noeud():
    def __init__(self, position, g=0, h=0):
        self.position = position
        self.g = g
        self.h = h
        self.f = g+h
        self.parent = None

    def __lt__(self, other):
        """Permet de comparer deux objets Noeud par la valeur de f."""
        return self.f < other.f
    
    def findNeighbors(self,pacman):
        directions={UP:Vector2(0, -1),DOWN:Vector2(0, 1), 
                          LEFT:Vector2(-1, 0), RIGHT:Vector2(1, 0), STOP:Vector2()}

        neighbors=[]
        for dir in [UP,DOWN,LEFT,RIGHT]:
            pos=self.position+directions[dir]*speed*dt
            if pacman.validDirection(dir) and not self.collideGhosts(pos):
                neighbors.append(Noeud(pos))
        return neighbors
    
    def collideGhosts(self,pos):
        for ghost in ghosts:
            d = pos - ghost.position
            dSquared = d.magnitudeSquared()
            rSquared = (pacman.collideRadius + ghost.collideRadius)**2
            if dSquared <= rSquared:
                return True
        return False

if __name__ == "__main__":
    n=Noeud((1,1))
    n.findNeighbors()