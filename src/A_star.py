import heapq
from vector import Vector2
from constants import *
import numpy as np
from constants import *
from nodes import Node


class A_star():
    def __init__(self,ghosts,pellets,pacman,level):
        self.ghosts = ghosts
        self.pellets = pellets
        self.pacman = pacman

        #création de la map
        #TODO : ajout du tunnel
        self.level=level
        self.nodes={}
        self.pathSymbols = ['.', '-', '|', 'p','+', 'P', 'n']
        self.data = self.readMazeFile(level)
        self.createNodeTable(self.data)
        self.connectHorizontally(self.data)
        self.connectVertically(self.data)
        # for n in self.nodes:
        #     neigbhbors=[]
        #     for neig in self.nodes[n].neighbors:
        #         if self.nodes[n].neighbors[neig] is not None:
        #             neigbhbors.append((self.nodes[n].neighbors[neig].position.x,self.nodes[n].neighbors[neig].position.y))
        #     print(f"Node {self.nodes[n].position} has neighbors {neigbhbors}")
        self.tunnels = []

    def createNodeTable(self, data):
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.pathSymbols:
                    x, y = col*TILEWIDTH, row*TILEHEIGHT
                    self.nodes[(x, y)] = Node(x, y)

    def readMazeFile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')
    
    def connectHorizontally(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            key = None
            for col in list(range(data.shape[1])):
                if data[row][col] in self.pathSymbols:
                    if key is None:
                        key = (col*TILEWIDTH,row*TILEHEIGHT)
                    else:
                        otherkey = (col*TILEWIDTH,row*TILEHEIGHT)
                        self.nodes[key].neighbors[RIGHT] = self.nodes[otherkey]
                        self.nodes[otherkey].neighbors[LEFT] = self.nodes[key]
                        key = otherkey
                else:
                    key = None
    
    def connectVertically(self, data):
        dataT = data.transpose()
        for col in list(range(dataT.shape[0])):
            key = None
            for row in list(range(dataT.shape[1])):
                if dataT[col][row] in self.pathSymbols:
                    if key is None:
                        key = (col*TILEWIDTH,row*TILEHEIGHT)
                    else:
                        otherkey = (col*TILEWIDTH,row*TILEHEIGHT)
                        self.nodes[key].neighbors[DOWN] = self.nodes[otherkey]
                        self.nodes[otherkey].neighbors[UP] = self.nodes[key]
                        key = otherkey
                else:
                    key = None
    
    def setPortalPair(self,pair1,pair2):
        #trouver si c'est un tunnel vers le bas, vers le haut, vers la droite ou vers la gauche
        # regarder quels sont les voisins : peut venir que d'une direction donc continuera dans cette direction
        x1,y1=pair1
        x2,y2=pair2
        x1=x1*16
        y1=y1*16
        x2=x2*16
        y2=y2*16
        pair1=(x1,y1)
        pair2=(x2,y2)
        self.tunnels.append((pair1,pair2))
        for neighbor in self.nodes[pair1].neighbors:
            if self.nodes[pair1].neighbors[neighbor] is not None:
                dir1=-neighbor
        for neighbor in self.nodes[pair2].neighbors:
            if self.nodes[pair2].neighbors[neighbor] is not None:
                dir2=-neighbor
        self.nodes[pair1].neighbors[dir1]=self.nodes[pair2]
        self.nodes[pair2].neighbors[dir2]=self.nodes[pair1]
        
        # for n in self.nodes:
        #     neigbhbors=[]
        #     for neig in self.nodes[n].neighbors:
        #         if self.nodes[n].neighbors[neig] is not None:
        #             neigbhbors.append((self.nodes[n].neighbors[neig].position.x,self.nodes[n].neighbors[neig].position.y))
        #     print(f"Node {self.nodes[n].position} has neighbors {neigbhbors}")

        return







    def next_move (self):   # doit renvoyer UP, LEFT, DOWN, RIGHT ou STOP

        # lance a_star sur la grille de jeu avec le bon objectif
        #trouver l'objectif : choisir la bille la plus proche
        #il faut aussi considérer la place des fantômes
        #considérer les fruits et manger les fantômes ?
        #commencer par les powerpellets ?
        #considérer le fait qu'un fantôme peut pas revenir en arrière

        #lancer a_star
        goal=self.get_closest_pellet()
        path=None
        if goal is not None:
            path=self.a_star(goal)
        
        if path is None or len(path)==0:
            return STOP
        else:
            #on affiche les positions dans le path
            # print([(p.position.x,p.position.y) for p in path])  
            return path[0].dir


    def get_closest_pellet(self): # TODO : à corriger ? (pb du il change d'avis)
        # trouver la node sur laquelle on est
        # partir de cette node puis de voisins en voisins (parcours en largeur)
        # dès qu'il y a un pellet on le choisi comme goal
        pos=(self.pacman.position.x//16*16,self.pacman.position.y//16*16)
        n=self.nodes[pos]
        pos=Vector2(self.pacman.position.x//16*16,self.pacman.position.y//16*16)
        open=[n]
        closed=[]
        for pellet in self.pellets :
            if pellet.position == pos:
                return pellet
        while(len(open)!=0):
            current=open.pop(0)
            closed.append(current)
            for neighbor in current.neighbors:
                neighbor = current.neighbors[neighbor]
                if neighbor is not None and neighbor not in open and neighbor not in closed and not collideGhosts(neighbor.position,self.ghosts,self.pacman) and not nextToGhosts(neighbor.position,self.ghosts):
                    #il faut trouver un objectif pour qu'il fuit les fantômes quand il y a un blocage à cause des fantômes
                    open.append(neighbor)
                    for pellet in self.pellets :
                        if pellet.position == neighbor.position:
                            return pellet
                        
        return None
        

    def a_star(self,goal):
        start_16=Vector2((self.pacman.position.x//16)*16,(self.pacman.position.y//16)*16)
        start_noeud = Noeud(start_16,0,0)
        open = []
        heapq.heappush(open, start_noeud)
        closed = []
        current=start_noeud
        goal_find = open[0].isGoal(goal,self.pacman)
        while len(open)!=0 and not goal_find:
            # print(f"open : {[(p.position.x,p.position.y,p.f) for p in open]}")
            open=supp_noeud(open,current.position)
            closed.append(current)
            neighbors = current.findNeighbors(self.nodes,self.ghosts,self.pacman) #les voisins initialisés avec g=0 et h=0
            # print(f"neighbors of {current.position.x,current.position.y}: {[(n.position.x,n.position.y) for n in neighbors]}")
            for neighbor in neighbors:
                if (not appartenir(closed,neighbor.position) and not appartenir(open,neighbor.position)) or (appartenir(open,neighbor.position) and getGNoeud(open,neighbor.position)>current.g+1): # TODO: cout(s,s')=1 : à modifier
                    if appartenir(open,neighbor.position):
                        open=supp_noeud(open,neighbor.position)
                    neighbor.g=current.g+1
                    neighbor.h= self.heuristic(neighbor,goal.position)
                    neighbor.f=neighbor.g+neighbor.h
                    neighbor.parent=current
                    heapq.heappush(open,neighbor)
                    # print(f"open : {[(p.position.x,p.position.y) for p in open]}")
                    if appartenir(closed,neighbor.position):
                        closed=supp_noeud(closed,neighbor.position)
                    
            if len(open)!=0:
                current=open[0]
                goal_find = open[0].isGoal(goal,self.pacman) #test si la position du noeud permet de manger le pellet goal
        if len(open)==0:
            return None
        else:
            path=[]
            while current.parent != None:
                path.append(current)
                current=current.parent
            return path[::-1]
    
    def heuristic(self, noeud, goal):
        dist = abs(noeud.position.x-goal.x)+abs(noeud.position.y-goal.y)
        #comparer aux distances en passant par chaque tunnel
        if self.tunnels != []:
            for t in self.tunnels:
                #dist aux deux entrées :
                dist_1= abs(noeud.position.x-t[0][0])+abs(noeud.position.y-t[0][1])
                dist_2= abs(noeud.position.x-t[1][0])+abs(noeud.position.y-t[1][1])
                if dist_1<dist_2:
                    dist_tunnel=dist_1+abs(t[1][0]-goal.x)+abs(t[1][1]-goal.y)
                else:
                    dist_tunnel=dist_2+abs(t[0][0]-goal.x)+abs(t[0][1]-goal.y)
                if dist_tunnel<dist:
                    dist=dist_tunnel
        dist,nb_pen=self.ghost_penality(noeud,dist) #le risque de croiser un fantôme doit être pénalisé
        return dist

    def ghost_penality(self,noeud,dist): #TODO : mettre une variable frightened
        nb_pen=0
        if collideGhosts(noeud.position,self.ghosts,self.pacman): # normalement n'arrive pas (fantômes considérés comme des murs mouvants)
            dist+=1000000
            nb_pen
        n = 5 # n est le nombre de tiles entre un fantôme et pacman nécessaire pour qu'il n'y ait pas de pénalité
        for ghost in self.ghosts:
            if not ghost.mode.current == FREIGHT:
                if manhattan_distance(noeud.position,ghost.position) < n*TILEWIDTH:
                    nb_pen+=1
                    dist+=1000000*(n-(manhattan_distance(noeud.position,ghost.position)//(TILEWIDTH)))
        return dist,nb_pen
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
    
    def findNeighbors(self,nodes,ghosts,pacman): #TODO : gérer les fantômes
        neighbors=[]
        x,y=(self.position.x,self.position.y)
        pos=(x,y)
        for neighbor in nodes[pos].neighbors:
            if nodes[pos].neighbors[neighbor]!=None:
                if not collideGhosts(nodes[pos].neighbors[neighbor].position,ghosts,pacman): #considère les fantômes comme des murs mouvants
                    if not nextToGhosts(nodes[pos].neighbors[neighbor].position,ghosts):
                        neighbors.append(Noeud(nodes[pos].neighbors[neighbor].position,dir=neighbor))
                # neighbors.append(Noeud(nodes[pos].neighbors[neighbor].position,dir=neighbor))
        return neighbors

    def isGoal(self,goal,pacman):
        d=self.position-goal.position
        dSquared = d.magnitudeSquared()
        rSquared = (pacman.collideRadius + goal.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

def collideGhosts(pos,ghosts,pacman): #TODO : mettre une variable frightened
    for ghost in ghosts:
        if not ghost.mode.current == FREIGHT:
            d = pos - ghost.position
            dSquared = d.magnitudeSquared()
            rSquared = (pacman.collideRadius + ghost.collideRadius)**2
            if dSquared <= rSquared:
                return True
    return False

def nextToGhosts(pos,ghosts):
    n = 2 # n est le nombre de tiles entre un fantôme et la position nécessaire pour qu'il ne soit pas considéré comme un mur
    for ghost in ghosts:
        if not ghost.mode.current ==FREIGHT:
            if manhattan_distance(pos,ghost.position) < n*TILEWIDTH:
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
    l=[n.g for n in liste if n.position == position]
    if l==[]:
        return None
    else:
        return l[0]

def manhattan_distance(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)

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