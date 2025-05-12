import pygame
import numpy as np
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause
from state import State
from text import TextGroup
from sprites import LifeSprites
from sprites import MazeSprites
from mazedata import MazeData
from sound import DummySound
import argparse
from A_star import A_star
#from MonteCarlo import MonteCarloSearch
from test import MonteCarloSearch
import numpy as np
from vector import Vector2
from jeveuxmourir import DijkstraAI

class GameController(object):
    def __init__(self, no_sound=False, ia=0):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.fruitCaptured = []
        self.fruitNode = None
        self.mazedata = MazeData()
        if no_sound:
            self.powerup_sound = self.death_sound = self.eatfruit_sound = self.eatghost_sound = DummySound()
        else:
            pygame.mixer.music.load("resources/sounds/music.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.2)
            self.powerup_sound = pygame.mixer.Sound("resources/sounds/powerup.mp3")
            self.death_sound = pygame.mixer.Sound("resources/sounds/death.wav")
            self.eatfruit_sound = pygame.mixer.Sound("resources/sounds/eatfruit.wav")
            self.eatghost_sound = pygame.mixer.Sound("resources/sounds/eatghost.wav")
        self.current_state = None # État actuel de la partie pour alpha-beta
        self.direction = None # direction à prendre si on utilise A*
        self.ia = ia # 0 = no AI, 1 = alpha_beta, 2 = A*, 3=MonteCarlo 4=Djikstra et le reste démerdez vous     
        self.mcts_simulations = 500   

    def setBackground(self):
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.constructBackground(self.background_norm, self.level%5)
        self.background_flash = self.mazesprites.constructBackground(self.background_flash, 5)
        self.flashBG = False
        self.background = self.background_norm

    def startGame(self, no_sound=False):      
        self.mazedata.loadMaze(self.level)
        self.mazesprites = MazeSprites("resources/"+self.mazedata.obj.name+".txt", "resources/"+self.mazedata.obj.name+"_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup("resources/"+self.mazedata.obj.name+".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart), no_sound=no_sound)
        self.pellets = PelletGroup("resources/"+self.mazedata.obj.name+".txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)
        self.dijkstra_ai=DijkstraAI(self.nodes, self.pacman, self.pellets, self.ghosts)

        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3)))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3)))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0)))

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)
        self.mcts_ai = MonteCarloSearch(
            pacman=self.pacman,
            ghosts=self.ghosts.ghosts, 
            pellets=self.pellets,
            level_data="resources/"+self.mazedata.obj.name+".txt",
            maze_nodes=self.nodes.nodesLUT,
            N=self.mcts_simulations,
            current_score=self.score,
            last_actual_move=self.pacman.direction 
        )
        

    def startGame_old(self):      
        self.mazedata.loadMaze(self.level)#######
        self.mazesprites = MazeSprites("maze1.txt", "maze1_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.setPortalPair((0,17), (27,17))
        homekey = self.nodes.createHomeNodes(11.5, 14)
        self.nodes.connectHomeNodes(homekey, (12,14), LEFT)
        self.nodes.connectHomeNodes(homekey, (15,14), RIGHT)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(15, 26))
        self.pellets = PelletGroup("maze1.txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 0+14))
        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 3+14))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(0+11.5, 3+14))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(4+11.5, 3+14))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(2+11.5, 3+14))

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, LEFT, self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, RIGHT, self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.nodes.denyAccessList(12, 14, UP, self.ghosts)
        self.nodes.denyAccessList(15, 14, UP, self.ghosts)
        self.nodes.denyAccessList(12, 26, UP, self.ghosts)
        self.nodes.denyAccessList(15, 26, UP, self.ghosts)

    def getValidKey_Astar(self):
        astar=A_star(self.ghosts,self.pellets.pelletList,self.pacman,"resources/"+self.mazedata.obj.name+".txt")
        self.mazedata.obj.setPortalPairsAstar(astar)
        return astar.next_move()

    def getValidKey_Dijkstra(self):
        """Gets Pacman's next move using the Dijkstra AI."""
        if not self.pacman or not self.pacman.alive or self.pause.paused:
            return STOP 
        if self.dijkstra_ai:
            try:
                self.dijkstra_ai.update_ghosts(self.ghosts)
                next_dir = self.dijkstra_ai.nextDir()
                return next_dir if next_dir is not None else STOP 
            except Exception as e:
                print(e)
                import traceback
                traceback.print_exc()
        else:
            print("Warning: Dijkstra not initialized in getValidKey_Dijkstra.")
            return STOP 
    def update(self,i):
    
    def getValidKey_MonteCarlo(self):
        if not self.pacman or not self.pacman.alive or self.pause.paused:
            return STOP

        if self.mcts_ai:
            try:
                self.mcts_ai.pacman_start = self.pacman 
                self.mcts_ai.ghosts_start = self.ghosts.ghosts
                self.mcts_ai.pellets_start = self.pellets 
                self.mcts_ai.current_score = self.score
                self.mcts_ai.last_actual_move = self.pacman.direction 
                next_dir = self.mcts_ai.search()
                return next_dir if next_dir is not None else STOP
            except Exception as e:
                print(f"Error in MonteCarloSearch (V2) AI: {e}")
                import traceback
                traceback.print_exc()
                return STOP
        else:
            try:
                maze_name = self.mazedata.obj.name
                maze_filepath = f"resources/{maze_name}.txt"
                level_data_for_mcts = np.loadtxt(maze_filepath, dtype='<U1')

                temp_mcts = MonteCarloSearch(
                    pacman=self.pacman,
                    ghosts=self.ghosts.ghosts,
                    pellets=self.pellets,
                    level_data=level_data_for_mcts,
                    maze_nodes=self.nodes.nodesLUT,
                    N=self.mcts_simulations,
                    current_score=self.score,
                    last_actual_move=self.pacman.direction
                )
                next_dir = temp_mcts.search()
                return next_dir if next_dir is not None else STOP
            except Exception as e_fallback:
                traceback.print_exc()
                return STOP


    def update(self, ia):
        dt = self.clock.tick(30) / 1000.0
        if ia==3:
            dt=0.033
        self.textgroup.update(dt)
        self.pellets.update(dt)
        if not self.pause.paused:
            self.ghosts.update(dt, ia)      
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()
            
        # Préparation de l'état pour alpha-beta
        if self.ia == 1:
            if self.current_state:
                self.current_state = State(self.pacman, self.ghosts, self.pellets.pelletList)
            else:
                self.current_state = State(self.pacman, self.ghosts, self.pellets.pelletList)

        if self.ia == 2:
            self.direction = self.getValidKey_Astar()
        
        if self.ia == 3:
            self.direction = self.getValidKey_MonteCarlo()

        if self.pacman.alive:
            if not self.pause.paused:
                self.pacman.update(dt, self.ia, state=self.current_state, dir=self.direction)
        else:
            self.pacman.update(dt, self.ia, state=self.current_state, dir=self.direction)

        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.checkEvents()
        self.render()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.pacman.alive:
                        self.pause.setPause(playerPaused=True)
                        if not self.pause.paused:
                            self.textgroup.hideText()
                            self.showEntities()
                        else:
                            self.textgroup.showText(PAUSETXT)
                            #self.hideEntities()

    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.updateScore(pellet.points)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == POWERPELLET:
                self.powerup_sound.play()
                self.ghosts.startFreight()
            if self.pellets.isEmpty():
                self.flashBG = True
                self.hideEntities()
                self.pause.setPause(pauseTime=3, func=self.nextLevel)

    def checkGhostEvents(self):
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.eatghost_sound.play()
                    self.updateScore(ghost.points)                  
                    self.textgroup.addText(str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1)
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime=1, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -=  1
                        self.lifesprites.removeImage()
                        self.pacman.die()   
                        self.death_sound.play()            
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(pauseTime=3, func=self.restartGame)
                        else:
                            self.pause.setPause(pauseTime=3, func=self.resetLevel)
    
    def checkFruitEvents(self):
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.getNodeFromTiles(9, 20), self.level)
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)
                self.eatfruit_sound.play()
                self.textgroup.addText(str(self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8, time=1)
                fruitCaptured = False
                for fruit in self.fruitCaptured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruitCaptured = True
                        break
                if not fruitCaptured:
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def showEntities(self):
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self):
        self.pacman.visible = False
        self.ghosts.hide()

    def nextLevel(self):
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()
        self.textgroup.updateLevel(self.level)

    def restartGame(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def resetLevel(self):
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.showText(READYTXT)

    def updateScore(self, points):
        self.score += points
        self.textgroup.updateScore(self.score)

    def render(self):
        self.screen.blit(self.background, (0, 0))
        #self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textgroup.render(self.screen)

        for i in range(len(self.lifesprites.images)):
            x = self.lifesprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
            self.screen.blit(self.lifesprites.images[i], (x, y))

        for i in range(len(self.fruitCaptured)):
            x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i+1)
            y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
            self.screen.blit(self.fruitCaptured[i], (x, y))

        pygame.display.update()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-sound', '-ns', action='store_true', help='Désactive les sons')
    parser.add_argument('--ia', '-ia', type=int, default=0, help='Choix de l\'IA (0 = aucune IA, 1 = alpha-beta, 2 = A*, 3 = Monte Carlo,4= Djikstra)')
    args = parser.parse_args()
    game = GameController(no_sound=args.no_sound, ia=args.ia)
    game.startGame(no_sound=args.no_sound)
    while True:
        game.update(args.ia)


