from constants import*
import math
import random
from vector import Vector2
import numpy as np
from nodes import Node

c= math.sqrt(2)

class MonteCarlo():
    def __init__(self, pacman, ghosts, pellets,level, N):
        self.pacman = pacman
        self.ghosts = ghosts
        self.pellets = pellets
        self.N = N
        self.node_mc = noeud_MonteCarlo(self.pacman.position)

        self.level=level
        self.nodes={}
        self.pathSymbols = ['.', '-', '|', 'p','+', 'P', 'n']
        self.data = self.readMazeFile(level)
        self.createNodeTable(self.data)
        self.connectHorizontally(self.data)
        self.connectVertically(self.data)

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
    

    def selection(self, mc_node):
        mc_node.children = mc_node.findNeighbors(self.nodes,self.ghosts,self.pacman)[0]
        while mc_node.children!=[]:  # Traverse until a leaf mc_node
            mc_node = max(mc_node.children,
                        key=lambda child: ((child.value / (child.nbvisits + 1e-6)) + c * math.sqrt(max(0,math.log(mc_node.nbvisits + 1e-6) / (child.nbvisits + 1e-6)))))
        mc_node.moves= mc_node.findNeighbors(self.nodes,self.ghosts,self.pacman)[1]
        return mc_node

    def expansion(self, mc_node):
        mc_node.children = mc_node.findNeighbors(self.nodes,self.ghosts,self.pacman)[0]
        return mc_node
    
    def simulation(self, mc_node):
        current_simulation_state = mc_node
        pacman = self.pacman
        pellets = self.pellets
        current_simulation_state.moves= current_simulation_state.findNeighbors(self.nodes,self.ghosts,self.pacman)[1]
        i=0
        while i<20:
            possible_moves= current_simulation_state.moves
            if not possible_moves:
                break
            move = random.choice(possible_moves)
            current_simulation_state = current_simulation_state.childrenandMoves.get(move)
            i+=1 
            if current_simulation_state is None:
                print("aaaaaaaaaa")
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
        start_16=Vector2((self.pacman.position.x//16)*16,(self.pacman.position.y//16)*16)
        root = noeud_MonteCarlo(start_16)
        root.moves= root.findNeighbors(self.nodes,self.ghosts,self.pacman)[1]
        root.children = root.findNeighbors(self.nodes,self.ghosts,self.pacman)[0]
        #print(root.moves, root.children)
        i=0
        while i<self.N:
            node= self.selection(root)
            #print(node.nbvisits)
            if node.moves:
                node= self.expansion(node)
                #print(node.children)
            resultat = self.simulation(node)
            self.backpropagation(node,resultat)
            i+=1
        #print(root.children)
        best_child = max (root.children, key=lambda child: child.nbvisits)
        key = next((k for k, v in root.childrenandMoves.items() if v == best_child), None)
        if key is not None:
            print("key: ", key)
            return key
        return STOP 
        



class noeud_MonteCarlo:
    def __init__(self, position,parent=None):
        self.position = position
        self.parent = parent
        self.childrenandMoves={}
        self.children=[]
        self.moves=[]
        self.score = 0
        self.nbvisits = 0
        self.value = 0
    
    def findNeighbors(self,nodes,ghosts,pacman): #TODO : gérer les fantômes
        neighbors=[]
        possible_direction =[]
        x,y=(self.position.x,self.position.y)
        pos=(x,y)
        for neighbor in nodes[pos].neighbors:
            if nodes[pos].neighbors[neighbor]!=None:
                if not collideGhosts(nodes[pos].neighbors[neighbor].position,ghosts,pacman): #considère les fantômes comme des murs mouvants
                    if not nextToGhosts(nodes[pos].neighbors[neighbor].position,ghosts):
                        neighbors.append(noeud_MonteCarlo(nodes[pos].neighbors[neighbor].position,parent=self))
                        possible_direction.append(neighbor)
                # neighbors.append(Noeud(nodes[pos].neighbors[neighbor].position,dir=neighbor))
        neib = neighbors.copy()
        direct= possible_direction.copy()
        while neib!=[]:
            nb= neib.pop()
            dir  =direct.pop()
            self.childrenandMoves[dir]=nb
        return [neighbors, possible_direction]
    

    

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

def manhattan_distance(a, b):
        return abs(a.x - b.x) + abs(a.y - b.y)