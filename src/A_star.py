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
        data = self.readMazeFile(level)
        self.createNodeTable(data)
        self.connectHorizontally(data)
        self.connectVertically(data)

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




    def next_move (self):   # doit renvoyer UP, LEFT, DOWN, RIGHT ou STOP

        # lance a_star sur la grille de jeu avec le bon objectif
        #trouver l'objectif : choisir la bille la plus proche
        #il faut aussi considérer la place des fantômes
        #considérer les fruits et manger les fantômes ?
        #commencer par les powerpellets ?

        #lancer a_star
        goal=self.get_closest_pellet()
        path=self.a_star(goal)
        
        if path is None or len(path)==0:
            return STOP
        else:
            return path[0].dir


    def get_closest_pellet(self): # TODO : à corriger
        # trouver la node sur laquelle on est
        # partir de cette node puis de voisins en voisins (parcours en largeur)
        # dès qu'il y a un pellet on le choisi comme goal
        pos=(self.pacman.position.x//16*16,self.pacman.position.y//16*16)
        n=self.nodes[pos]
        pos=Vector2(self.pacman.position.x//16*16,self.pacman.position.y//16*16)
        open=[n]
        for pellet in self.pellets :
            if pellet.position == pos:
                return pellet
        while(len(open)!=0):
            current=open.pop(0)
            for neighbor in current.neighbors:
                neighbor = current.neighbors[neighbor]
                if neighbor is not None and neighbor not in open:
                    open.append(neighbor)
                    for pellet in self.pellets :
                        if pellet.position == neighbor.position:
                            return pellet
                        
        return None
        

    def a_star(self,goal):
        start_16=Vector2((self.pacman.position.x//16)*16,(self.pacman.position.y//16)*16)
        start_noeud = Noeud(start_16,0,0)
        # start_noeud.position.x=int(start_noeud.position.x)
        # start_noeud.position.y=int(start_noeud.position.y)
        open = []
        heapq.heappush(open, start_noeud)
        closed = []
        current=start_noeud
        goal_find = open[0].isGoal(goal,self.pacman)
        while len(open)!=0 and not goal_find:
            open=supp_noeud(open,current.position)
            closed.append(current)
            neighbors = current.findNeighbors(self.nodes,self.ghosts,self.pacman) #les voisins initialisés avec g=0 et h=0
            for neighbor in neighbors:
                if (not appartenir(closed,neighbor.position) and not appartenir(open,neighbor.position)) or (appartenir(open,neighbor.position) and getGNoeud(open,neighbor.position)>current.g+1): # TODO: cout(s,s')=1 : à modifier
                    if appartenir(open,neighbor.position):
                        open=supp_noeud(open,neighbor.position)
                    neighbor.g=current.g+1
                    neighbor.h= heuristic(neighbor,goal.position)
                    neighbor.f=neighbor.g+neighbor.h
                    neighbor.parent=current
                    heapq.heappush(open,neighbor)
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
                neighbors.append(Noeud(nodes[pos].neighbors[neighbor].position,dir=neighbor))
        return neighbors

    def isGoal(self,goal,pacman):
        d=self.position-goal.position
        dSquared = d.magnitudeSquared()
        rSquared = (pacman.collideRadius + goal.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

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
    l=[n.g for n in liste if n.position == position]
    if l==[]:
        return None
    else:
        return l[0]

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