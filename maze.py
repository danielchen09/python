import pygame
import random
import time

from pygame.locals import *

def randint(a, b):
    if b == 0:
        return 0
    return random.randint(a, b-1)

class Game():
    def __init__(self, w, h):
        self.clock = pygame.time.Clock()
        self.counter = 0
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w, h))
        self.sprites = []
        self.running = True
        self.gridSize = int(w/15)
        self.fps = 30
        self.player = None
        self.exit = None
        self.canUpdate = True
        self.maze = Maze(int(w/15), int(h/15), self.gridSize, self)
        while self.maze.grid[-1][-1]:
            self.maze = Maze(int(w/15), int(h/15), self.gridSize, self)
        for sprite in self.sprites:
            sprite.y += self.gridSize
            sprite.x += self.gridSize
    def mainloop(self):

        while self.running:

            if self.counter == self.fps:
                self.counter = 0
                self.canUpdate = True

            self.screen.fill(0)

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                elif event.type == QUIT:
                    self.running = False

            self.render()

    def render(self):
        for sprite in self.sprites:
            sprite.update()
            self.screen.blit(sprite.surf, (sprite.x, sprite.y))

        self.player.update()
        self.screen.blit(self.player.surf, (self.player.x, self.player.y))

        pygame.display.flip()


    def setPlayer(self, p):
        self.player = p

    def setExit(self, e):
        self.sprites.append(e)
        self.exit = e

    def win(self):
        winTextFont = pygame.font.SysFont('Comic Sans MS', 30)
        winText = winTextFont.render('You win! press R to start a new game', False, (255, 255, 255))
        self.screen.fill(0)
        self.screen.blit(winText,(self.width/5, self.height/2))

class Maze():
    def __init__(self, width, height, size, game):
        self.game = game
        self.size = size
        self.width = width
        self.height = height
        self.grid = []
        self.passage = []
        for i in range(0, height):
            temp = []
            for j in range(0, width):
                temp.append(False)
            self.grid.append(temp)

        self.divide(0, 0, self.width, self.height, self.orientation(self.width, self.height))
        self.draw()

    def orientation(self, w, h):
        if w < h:
            return "h"
        elif h < w:
            return "v"
        else:
            return "h" if randint(0, 1)==0 else "v"

    def divide(self, x, y, w, h, orientation):
        minsize = 5

        if w < minsize or h < minsize:
            return

        horizontal = orientation == "h"
        length = w if horizontal else h

        a = 1
        b = 1

        xi = x + (0 if horizontal else randint(a, w-b))
        yi = y + (randint(a, h-b) if horizontal else 0)

        for p in self.passage:
            px = p[0]
            py = p[1]
            if horizontal:
                while [xi-1, yi] == p or [xi+length, yi] == p:
                    yi = y + (randint(a, h-b) if horizontal else 0)
            else:
                while [xi, yi-1] == p or [xi, yi+length] == p:
                    xi = x + (0 if horizontal else randint(a, w-b))

        px = xi + (randint(0, w) if horizontal else 0)
        py = yi + (0 if horizontal else randint(0, h))

        self.passage.append([px, py])


        dx = 1 if horizontal else 0
        dy = 0 if horizontal else 1

        xr = xi
        yr = yi
        for i in range(0, length):
            if xr != px or yr != py:
                self.grid[xr][yr] = True
            xr += dx
            yr += dy

        #left or top
        nx, ny = [x, y]
        nw, nh = [w, yi-y] if horizontal else [xi-x, h]
        self.divide(nx, ny, nw, nh, self.orientation(nw, nh))

        #right or bottom
        nx, ny = [xi, yi+1] if horizontal else [xi+1, yi] 
        nw, nh = [w, h-nh-1] if horizontal else [w-nw-1, h]
        self.divide(nx, ny, nw, nh, self.orientation(nw, nh))

    def draw(self):
        for i in range(0, self.height):
            for j in range(0, self.width):
                if self.grid[i][j]:
                    self.game.sprites.append(Wall(j*self.size, i*self.size, self.size))

        for i in range(-1, self.height+1):
            self.game.sprites.append(Wall(-self.size, i*self.size, self.size))
            self.game.sprites.append(Wall(self.width*self.size, i*self.size, self.size))

        for i in range(-1, self.width+1):
            self.game.sprites.append(Wall(i*self.size, -self.size,  self.size))
            self.game.sprites.append(Wall(i*self.size, self.width*self.size,  self.size))

class Player(pygame.sprite.Sprite):
    def __init__(self, game, size):
        super(Player, self).__init__()
        self.size = size/2
        self.game = game
        self.x = size
        self.y = size
        self.gridx = 0
        self.gridy = 0
        self.v = 0.4
        self.notPressed = True
        self.surf = pygame.Surface((self.size, self.size))
        self.surf.fill((255, 0, 0))

    def update(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_UP]:
            self.moveUp()
        if pressed_keys[K_DOWN]:
            self.moveDown()
        if pressed_keys[K_LEFT]:
            self.moveLeft()
        if pressed_keys[K_RIGHT]:
            self.moveRight()
        if pressed_keys[K_RSHIFT] or pressed_keys[K_LSHIFT]:
            self.v = 1
        else:
            self.v = 0.4
        if pressed_keys[K_r]:
            self.game.running = False
            start()


        if self.game.exit.x <= self.size + 5 and self.game.exit.y <= self.size + 5:
            self.v = 0
            self.game.win()

    def moveDown(self):
        canMove = True
        distance = 0
        for sprite in self.game.sprites:
            if sprite != self and sprite != self.game.exit:
                if not self.canMoveTo(self, Coords(sprite.x, sprite.y-self.v, sprite.size)):
                    
                    distance = sprite.y - (self.x + self.size) - 0.1
                    canMove = False
                    break

        for sprite in self.game.sprites:
            if sprite != self:
                if canMove:
                    sprite.y -= self.v
                else:
                    sprite.y -= distance


    def moveUp(self):
        canMove = True
        distance = 0
        for sprite in self.game.sprites:
            if sprite != self and sprite != self.game.exit:
                if not self.canMoveTo(self, Coords(sprite.x, sprite.y+self.v, sprite.size)):
                    
                    distance = self.y - (sprite.y + sprite.size) - 0.1
                    canMove = False
                    break

        for sprite in self.game.sprites:
            if sprite != self:
                if canMove:
                    sprite.y += self.v
                else:
                    sprite.y += distance

    def moveLeft(self):
        canMove = True
        distance = 0
        for sprite in self.game.sprites:
            if sprite != self and sprite != self.game.exit:
                if not self.canMoveTo(self, Coords(sprite.x+self.v, sprite.y, sprite.size)):
                    
                    distance = self.x - (sprite.x + sprite.size) - 0.1
                    canMove = False
                    break

        for sprite in self.game.sprites:
            if sprite != self:
                if canMove:
                    sprite.x += self.v
                else:
                    sprite.x += distance

    def moveRight(self):
        canMove = True
        distance = 0
        for sprite in self.game.sprites:
            if sprite != self and sprite != self.game.exit:
                if not self.canMoveTo(self, Coords(sprite.x-self.v, sprite.y, sprite.size)):
                    
                    distance = sprite.x - (self.x + self.size) - 0.1
                    canMove = False
                    break

        for sprite in self.game.sprites:
            if sprite != self:
                if canMove:
                    sprite.x -= self.v
                else:
                    sprite.x -= distance

    def canMoveTo(self, p, w):
        return not (withinx(p, w) and withiny(p, w))


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super(Wall, self).__init__()
        self.x = x
        self.y = y
        self.v = 0.1
        self.size = size
        self.surf = pygame.Surface((self.size, self.size))
        self.surf.fill((255, 255, 255))
    def update(self):
        pass

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super(Exit, self).__init__()
        self.x = x
        self.y = y
        self.v = 0.1
        self.size = size
        self.surf = pygame.Surface((self.size, self.size))
        self.surf.fill((0, 255, 0))
    def update(self):
        pass


class Coords:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

def withinx(p, e):
  return (p.x >= e.x and p.x < e.x+e.size) or (p.x + p.size >= e.x and p.x + p.size <= e.x + e.size);

def withiny(p, e):
  return (p.y >= e.y and p.y < e.y+e.size) or (p.y + p.size >= e.y and p.y + p.size <= e.y + e.size);

def start():
    pygame.init()
    pygame.font.init()
    game = Game(600, 600)
    player = Player(game, game.gridSize)
    game.setPlayer(player)
    game.setExit(Exit((game.maze.width)*game.gridSize, (game.maze.height)*game.gridSize, game.gridSize))
    game.mainloop()

if __name__ == "__main__":
    start()