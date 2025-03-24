import heapq
from vector import Vector2
from constants import *

class A_star():
    def __init__(self,ghosts,pellets,pacman,dt):
        self.ghosts = ghosts
        self.pellets = pellets
        self.pacman = pacman
        self.dt=dt
        # print([(p.position.x,p.position.y) for p in self.pellets])
        # print(pacman.position.x,pacman.position.y)

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
        start=self.pacman.position
        # start=Vector2(32,64)
        goal=self.get_closest_pellet()
        path=self.a_star(start,goal)
        if path is None:
            # print(f"direction_next_move_none : STOP")
            return STOP
        else:
            # print(path)
            # print(f"direction_next_move : {path[0].dir}")
            return path[0].dir


    def get_closest_pellet(self): # TODO : à définir
        return self.pellets[0].position
        

    def a_star(self,start,goal):
        print(f"goal : {goal}")
        # la position de pacman prend les multiples de 16 les plus proches
        start_16=Vector2(int(start.x/16)*16,int(start.y/16)*16)
        print(f"départ : {start_16.x},{start_16.y}")
        start_noeud = Noeud(start_16,0,0) #voir quoi mettre pour h
        start_noeud.position.x=int(start_noeud.position.x)
        start_noeud.position.y=int(start_noeud.position.y)
        open = []
        heapq.heappush(open, start_noeud)
        closed = []
        current=start_noeud
        while len(open)!=0 and open[0].position != goal:
            # print(len(open))
            open=supp_noeud(open,current.position)
            closed.append(current)
            neighbors = current.findNeighbors(self.pacman,self.ghosts,self.dt) #les voisins initialisés avec g=0 et h=0
            # print(f"current : {current.position}")
            # print(f"neighbors : {[(n.position.x,n.position.y) for n in neighbors]}")
            for neighbor in neighbors:
                # print(not appartenir(closed,neighbor.position) and not appartenir(open,neighbor.position)) or (appartenir(open,neighbor.position) and getGNoeud(open,neighbor.position)>current.g+1)
                if (not appartenir(closed,neighbor.position) and not appartenir(open,neighbor.position)) or (appartenir(open,neighbor.position) and getGNoeud(open,neighbor.position)>current.g+1): # TODO: cout(s,s')=1 : à modifier
                    if appartenir(open,neighbor.position):
                        open=supp_noeud(open,neighbor.position)
                    neighbor.g=current.g+1
                    neighbor.h= heuristic(neighbor,goal)
                    neighbor.f=neighbor.g+neighbor.h
                    neighbor.parent=current
                    heapq.heappush(open,neighbor)
                    # print(f"open : {[(n.position.x,n.position.y) for n in open]}")
                    if appartenir(closed,neighbor.position):
                        closed=supp_noeud(closed,neighbor.position)
                    
            if len(open)!=0:
                current=open[0]
            print(f"open : {[(n.position.x,n.position.y) for n in open]}")
            # print(f"closed : {[(n.position.x,n.position.y) for n in closed]}")
            # b=a
            # print(goal in [n.position for n in open])
        if len(open)==0:
            return None
        else:
            path=[]
            while current.parent != None:
                path.append(current)
                current=current.parent
            # print(f"path : {[(n.x,n.y) for n in path]}")
            # print(path)
            return path[::-1]

    

class Noeud():
    def __init__(self, position, g=0, h=0,dir=STOP):
        self.position = position
        self.g = g
        self.h = h
        self.f = g+h
        self.parent = None
        self.dir=dir

    def __lt__(self, other):
        """Permet de comparer deux objets Noeud par la valeur de f."""
        return self.f < other.f
    
    def findNeighbors(self,pacman,ghosts,dt):
        directions={UP:Vector2(0, -16),DOWN:Vector2(0, 16), 
                          LEFT:Vector2(-16, 0), RIGHT:Vector2(16, 0), STOP:Vector2()}
        neighbors=[]
        for dir in [UP,DOWN,LEFT,RIGHT]:
            pos=self.position+directions[dir]
            if pacman.validDirection(dir) and not collideGhosts(pos,ghosts,pacman):
                neighbors.append(Noeud(pos,0,0,dir))
        return neighbors
    
def collideGhosts(pos,ghosts,pacman):
    for ghost in ghosts:
        d = pos - ghost.position
        dSquared = d.magnitudeSquared()
        rSquared = (pacman.collideRadius + ghost.collideRadius)**2
        if dSquared <= rSquared:
            return True
    return False

def supp_noeud(liste, position):
        l=[n for n in liste if n.position != position]
        heapq.heapify(l)
        if l==None:
            return []
        else:
            return l

def appartenir(liste, position):
    return position in [n.position for n in liste]

def getGNoeud(liste,position):
    return [n.g for n in liste if n.position == position][0]

def heuristic(noeud, goal):
    return abs(noeud.position.x-goal.x)+abs(noeud.position.y-goal.y)

if __name__ == "__main__":
    n1=Noeud((1,1))
    n2=Noeud((2,2))
    n3=Noeud((3,3))
    l=[]
    heapq.heappush(l,n1)
    heapq.heappush(l,n2)
    heapq.heappush(l,n3)
    print(l)
    l=supp_noeud(l,(1,1))
    print(l)