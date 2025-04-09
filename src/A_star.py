import heapq
from vector import Vector2
from constants import *
import numpy as np
from constants import *
from nodes import Node


class A_star():
    def __init__(self,ghosts,pellets,pacman,dt,level): #pb: le dt est fixe pour toute la partie
        self.ghosts = ghosts
        self.pellets = pellets
        self.pacman = pacman
        # self.pelletfile="resources/maze1.txt"
        self.dpl=round(pacman.speed*dt,2)
        # print("dpl",self.dpl,dt)

        #création de la map
        self.level=level
        self.nodes={}
        self.pathSymbols = ['.', '-', '|', 'p','+', 'P', 'n']
        data = self.readMazeFile(level)
        self.createNodeTable(data)
        self.connectHorizontally(data)
        self.connectVertically(data)
        self.homekey = None
        # for n in self.nodes:
        #     neig=[]
        #     for neighbor in self.nodes[n].neighbors:
        #         if self.nodes[n].neighbors[neighbor]!=None :
        #             neig.append((self.nodes[n].neighbors[neighbor].position.x,self.nodes[n].neighbors[neighbor].position.y))
        #         else:
        #             neig.append(None)
        #     print(f"node : {n} : {neig}")
    
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

        #TODO : piste pour reprendre : pour tester si goal atteint tester l'intersection des zones de collision (eatpellet) et du coup utiliser les vrais déplacements de pacman


        #lancer a_star
        # start=self.pacman.position
        # start=Vector2(32,64)
        goal=self.get_closest_pellet()
        path=self.a_star(goal)
        # print(f"start : {start}")
        
        if path is None or len(path)==0:
            # print("test")
            return STOP
        else:
            print(f"path : {[((n.position.x,n.position.y),n.dir) for n in path]}")
            print(f"dir voulue voulue : {path[0].dir}")
            return path[0].dir


    def get_closest_pellet(self): # TODO : à définir
        return self.pellets[0]
        

    def a_star(self,goal):
        start_16=Vector2((self.pacman.position.x//16)*16,(self.pacman.position.y//16)*16)
        print(f"start_16 : {start_16}")
        start_noeud = Noeud(start_16,0,0) #voir quoi mettre pour h
        start_noeud.position.x=int(start_noeud.position.x)
        start_noeud.position.y=int(start_noeud.position.y)
        open = []
        heapq.heappush(open, start_noeud)
        closed = []
        current=start_noeud
        # goal_find = (open[0].position == goal)
        goal_find = open[0].isGoal(goal,self.pacman)
        while len(open)!=0 and not goal_find:
            open=supp_noeud(open,current.position)
            closed.append(current)
            neighbors = current.findNeighbors(self.nodes,self.ghosts) #les voisins initialisés avec g=0 et h=0
            # print(f"neighbors : {[(n.position.x,n.position.y) for n in neighbors]}")
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
            # print(f"ope : {[(n.position.x,n.position.y) for n in open]}")
        if len(open)==0:
            return None
        else:
            path=[]
            while current.parent != None:
                path.append(current)
                current=current.parent
            return path[::-1]

    # def a_star_correct(self,goal):
    #     #TODO : rajouter un nb d'itérations au bout duquel on abandonne la recherche ?
    #     start = self.pacman.position
    #     print(f"start : {start}")
    #     # start=goal.position.copy()
    #     start_noeud = Noeud(start,0,0)
    #     print(f"heuristique goal-start : {heuristic(start_noeud,goal.position)}")
    #     open = []
    #     heapq.heappush(open, start_noeud)
    #     closed = []
    #     current=start_noeud
    #     goal_find = open[0].isGoal(goal,self.pacman) #test si la position du noeud permet de manger le pellet goal
    #     while len(open)!=0 and not goal_find:
    #         # print(f"current : {open[0].position}, f = {current.f}, g= {current.g}, h = {current.h}")
    #         # print(f"longueur de open : {len(open)}")
    #         open=supp_noeud(open,current.position)
    #         # print(f"longueur de open après : {len(open)}")
    #         closed.append(current)
    #         # print(f"longueur de close : {len(closed)}\n")
    #         neighbors = current.findNeighbors(self.pacman,self.ghosts,self.dpl) #les voisins initialisés avec g=0 et h=0
    #         # print(f"neighbors : {[(n.position.x,n.position.y) for n in neighbors]}")
    #         for neighbor in neighbors:
    #             if (not appartenir(closed,neighbor.position) and not appartenir(open,neighbor.position)) or (appartenir(open,neighbor.position) and getGNoeud(open,neighbor.position)>current.g+self.dpl): # TODO: cout(s,s')=1 : à modifier
    #                 if appartenir(open,neighbor.position):
    #                     open=supp_noeud(open,neighbor.position)
    #                 neighbor.g=current.g+self.dpl
    #                 neighbor.h= heuristic(neighbor,goal.position)
    #                 neighbor.f=neighbor.g+neighbor.h
    #                 neighbor.parent=current
    #                 heapq.heappush(open,neighbor)
    #                 if appartenir(closed,neighbor.position):
    #                     closed=supp_noeud(closed,neighbor.position)
                    
    #         if len(open)!=0:
    #             current=open[0]
    #             goal_find = open[0].isGoal(goal,self.pacman) #test si la position du noeud permet de manger le pellet goal
            
    #         # print(f"dt*speed = {self.dpl}")
    #         # b=a
    #     # print(len(closed))
    #     if len(open)==0:
    #         return None
    #     else:
    #         path=[]
    #         while current.parent != None:
    #             path.append(current)
    #             current=current.parent
    #         return path[::-1]

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
    
    def findNeighbors(self,nodes,ghosts): #TODO : gérer les fantômes
        # directions={STOP:Vector2(), UP:Vector2(0, -1),DOWN:Vector2(0, 1), 
        #                   LEFT:Vector2(-1, 0), RIGHT:Vector2(1, 0)}
        # neighbors=[]
        # for dir in [UP,DOWN,LEFT,RIGHT]:
        #     # print(f"dir : {dir}")
        #     if self.validDirection(dir):
        #         # print(f"valid direction : {dir,directions[dir].x,directions[dir].y}")
        #         pos=self.position+directions[dir]*dpl
        #         if pos.x<=416 and pos.x>=16 and pos.y>=64 and pos.y<=512:
        #             neighbors.append(Noeud(pos))
        
        neighbors=[]
        x,y=(self.position.x,self.position.y)
        pos=(x,y)
        for neighbor in nodes[pos].neighbors:
            if nodes[pos].neighbors[neighbor]!=None :
                neighbors.append(Noeud(nodes[pos].neighbors[neighbor].position,dir=neighbor))
        # print(f"node : {pos} : {neighbors}")
        return neighbors

    # def findNeighbors_correct(self,pacman,ghosts,dpl):
    #     directions={STOP:Vector2(), UP:Vector2(0, -1),DOWN:Vector2(0, 1), 
    #                       LEFT:Vector2(-1, 0), RIGHT:Vector2(1, 0)}
    #     neighbors=[]
    #     for dir in [UP,DOWN,LEFT,RIGHT]:
    #         # print(f"dir : {dir}")
    #         if self.validDirection(dir):
    #             # print(f"valid direction : {dir,directions[dir].x,directions[dir].y}")
    #             pos=self.position+directions[dir]*dpl
    #             if pos.x<=416 and pos.x>=16 and pos.y>=64 and pos.y<=512:
    #                 neighbors.append(Noeud(pos))
    

        # print(pacman.validDirections())
        # for dir in pacman.validDirections():
        #     print(directions[dir])
        #     neighbors.append(Noeud(self.position+directions[dir]*dpl))
        # for dir in [UP,DOWN,LEFT,RIGHT]:
        #     pos=self.position+directions[dir]*dpl
            # print(f"pos : {pos}")
            # if pos.x>=0 and pos.y>=0 and pos.x<=448 and pos.y<=576 and validDirection(pos) and not collideGhosts(pos,ghosts,pacman):
            # pos_save=pacman.position.copy()
            # pacman.position=pos
            # print(f"position test pour voisin : {pacman.position}")
            # if pacman.overshotTarget():
            #     print("overshotTarget voisin true")
            #     save_target=pacman.target
            #     pacman.target = pacman.getNewTarget(dir)
            #     if pacman.target is not pacman.node:
            #         print("deuxième test voisin ok")
            #         neighbors.append(Noeud(pos,0,0,dir)) #TODO : rajouter la prise en comte des fantômes
            #     pacman.target=save_target
            # pacman.position=pos_save
            # if pacman.validDirection(dir) and not collideGhosts(pos,ghosts,pacman): #TODO : remplacer validDirection
            #     neighbors.append(Noeud(pos,0,0,dir))
        # return neighbors
    
    def isValidDirection(self,dir):
        #tester si il n'y a pas de mur, si c'est dans le labyrinthe et si il n'y a pas de fantôme
        #récupérer la case sur laquelle est pacman d'après sa position
        
        return 
    
    def validDirection(self, direction):
        # print(f"direction : {direction}")
        if direction is not STOP:
            if self.name in self.node.access[direction]:
                if self.node.neighbors[direction] is not None:
                    return True
        return False

    def isGoal(self,goal,pacman):
        d=self.position-goal.position
        dSquared = d.magnitudeSquared()
        rSquared = (pacman.collideRadius + goal.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False
    
# def validDirection(pos):
#     data = readPelletfile("resources/maze1.txt")
#     if data[int(pos.y/16)][int(pos.x/16)].isdigit():
#         return False
#     return True

# def readPelletfile(textfile):
#     return np.loadtxt(textfile, dtype='<U1')

# def collide_goal(pacman,goal): # renvoie true si pacman mange le goal
#     d = pacman.position - goal.position
#     dSquared = d.magnitudeSquared()
#     rSquared = (pacman.collideRadius + goal.collideRadius)**2
#     if dSquared <= rSquared:
#         return True
#     return False

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