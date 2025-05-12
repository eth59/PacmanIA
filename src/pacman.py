import pygame
from pygame.locals import *
from alphabeta import AlphaBeta
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from sound import DummySound

class Pacman(Entity):
    def __init__(self, node, no_sound=False):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.pipe_sound = pygame.mixer.Sound("resources/sounds/pipe.mp3") if not no_sound else DummySound()

    def copy(self):
        """Create a copy of the Pacman object.

        Returns:
            Pacman: A new Pacman object with the same attributes as the original.
        """
        new_pacman = Pacman(self.node, no_sound=True)
        new_pacman.position = self.position.copy()
        new_pacman.direction = self.direction
        new_pacman.target = self.target
        new_pacman.speed = self.speed
        new_pacman.alive = self.alive
        return new_pacman

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def update(self, dt, ia, state=None, dir=None):
        """Update the pacman position and check for collisions with pellets or ghosts.

        Args:
            dt (?): ? ct de base quoi
            ia (int): pour savoir quel ia utiliser
            state (State, optional): C'est l'état de la partie, utile pour alpha beta. Defaults to None.

        Raises:
            NotImplementedError: si ia est un nombre qui correspond pas à une IA implémentée.
        """
        self.sprites.update(dt)
        if ia == 1:
            # dt fixe pour le alpha beta sinon il traverse tout les pellets et fantômes
            self.position += self.directions[self.direction]*self.speed*0.05
        else:
            self.position += self.directions[self.direction]*self.speed*dt
        if ia == 0:
            direction = self.getValidKey()
        elif ia == 1:
            ab = AlphaBeta(state)
            direction = ab.getBestMove()
        elif ia == 2 or ia == 3:
            direction=dir

        else:
            raise NotImplementedError("Other AI not implemented yet")
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.pipe_sound.play()
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else: 
            if self.oppositeDirection(direction):
                self.reverseDirection()

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP  

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None    
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False
