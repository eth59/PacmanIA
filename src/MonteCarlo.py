from constants import*
import math
import random
from vector import Vector2
import numpy as np
from nodes import Node

c= 2#math.sqrt(2)

class MonteCarlo():
    def __init__(self, pacman, ghosts, pellets,level, N, score):
        self.pacman = pacman
        self.ghosts = ghosts
        self.pellets = pellets
        self.N = N
        self.node_mc = noeud_MonteCarlo(self.pacman.position)
        self.score = score
        self.last_move=0

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
                        #key=lambda child: child.value/(child.nbvisits +1e-9))
            #print(mc_node)
        mc_node.moves= mc_node.findNeighbors(self.nodes,self.ghosts,self.pacman)[1]
        return mc_node

    def expansion(self, mc_node):
        mc_node.children = mc_node.findNeighbors(self.nodes,self.ghosts,self.pacman)[0]
        return mc_node
    
    def simulation(self, mc_node):
        current_simulation_state = mc_node
        pacman = self.pacman
        pellets = self.pellets
        rewards = 0
        visited_positions=[]
        current_simulation_state.moves= current_simulation_state.findNeighbors(self.nodes,self.ghosts,self.pacman)[1]
        visited_positions.append(current_simulation_state.position)
        sim_pellet_positions = [pellet.position for pellet in self.pellets.pelletList]
        last_sim_move = self.last_move
        start_pos = mc_node.position
        i=0
        while i<200:
            possible_moves= current_simulation_state.moves
            if not possible_moves:
                break
            #print(possible_moves)
            move = random.choice(possible_moves)
            #print("move",move)
            #print(move)
            if current_simulation_state.childrenandMoves.get(move) is None:
                #print('aaaaaaaaaaa')
                break
            current_simulation_state = current_simulation_state.childrenandMoves.get(move)
            if current_simulation_state.position in visited_positions:
                rewards -=300
                #print("hallo")
            else:
                visited_positions.append(current_simulation_state.position)
            if move == -(self.last_move):
                if len(possible_moves) > 1:
                    rewards -= 1000
                else:
                    rewards -=100
                #print('test')
            if current_simulation_state is None:
                break
            i+=1 
            if sim_pellet_positions == []:
                return 10000000
            if len(visited_positions) > 2 and current_simulation_state.position == visited_positions[-3]:
                rewards -= 2000
            pos = Vector2((current_simulation_state.position.x // 16) * 16,
              (current_simulation_state.position.y // 16) * 16)

            if pos in sim_pellet_positions:
                rewards += 10000
                sim_pellet_positions.remove(pos)

            if i > 0 and move == last_sim_move:
                rewards += 200
                last_sim_move = move
        #distance = (current_simulation_state.position - start_pos).magnitude()
        #rewards += distance * 0.35  
        return self.score + rewards

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
        #self.last_move=root.position
        while i<self.N:
            node= self.selection(root)
            #print(node.nbvisits)
            if node.moves:
                node= self.expansion(node)
                #node.moves = node.findNeighbors(self.nodes, self.ghosts, self.pacman)[1]
                #print(node.children)
            #self.last_move=node.position
            resultat = self.simulation(node)
            #print("resultat:", resultat)
            self.backpropagation(node,resultat)
            i+=1
        #print(root.children)
        if root.children!=[]:
            best_child = max(root.children, key=lambda child: (child.value / (child.nbvisits + 1e-7)) +random.uniform(0, 0.1))

            key = next((k for k, v in root.childrenandMoves.items() if v == best_child), None)
            if key is not None:
                #print("key: ", key)
                self.last_move= key
                return key
        #list = [LEFT,RIGHT,UP,DOWN]
        #return random.choice(list)
        self.last_move= STOP
        return STOP
        

    def pelletPresent(self,x,y):
        current_position = pos=Vector2(x//16*16,y//16*16)
        for pellet in self.pellets.pelletList:
            if pellet.position == current_position:
                return True
        return False



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