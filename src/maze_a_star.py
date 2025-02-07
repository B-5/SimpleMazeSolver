# -*- coding: utf-8 -*-
"""
Carrega um mapa à partir de um arquivo e exibe na tela

@author: Prof. Daniel Cavalcanti Jeronymo
"""

import pygame
    
import sys
import os
import traceback
import random
import math
import time
import numpy as np
from enum import IntEnum
import itertools


class GameConstants:
    #                  R    G    B
    ColorWhite     = (255, 255, 255)
    ColorBlack     = (  0,   0,   0)
    ColorRed       = (255,   0,   0)
    ColorGreen     = (  0, 255,   0)
    ColorBlue     = (  0, 0,   255)
    ColorDarkGreen = (  0, 155,   0)
    ColorDarkGray  = ( 40,  40,  40)
    BackgroundColor = ColorBlack
    
    screenScale = 1
    screenWidth = screenScale*800
    screenHeight = screenScale*800
    
    # grid size in units
    gridWidth = 20
    gridHeight = 20
    
    # grid size in pixels
    gridMarginSize = 0.5
    gridCellWidth = screenWidth//gridWidth - 2*gridMarginSize
    gridCellHeight = screenHeight//gridHeight - 2*gridMarginSize
    
    randomSeed = 0
    
    FPS = 5
    
    fontSize = 20


class Game:
    class CellType(IntEnum):
        Full = 0
        Empty = 1
        Start = 2
        End = 3
        Visited = 4
    

def printText(screen, text, x, y, size = 50, color = (200, 000, 000), fontType = None):
    try:
        if fontType == None:
            fontType = pygame.font.get_default_font()

        text = str(text)
        font = pygame.font.Font(fontType, size)
        text = font.render(text, True, color)
        screen.blit(text, (x, y))

    except Exception as e:
        print('ERROR: Font Error')
        raise e

def drawGrid(screen, grid):
    rects = []

    rects = [screen.fill(GameConstants.BackgroundColor)]
 
    # Draw the grid
    for row in range(GameConstants.gridHeight):
        for column in range(GameConstants.gridWidth):
            color = GameConstants.ColorWhite
            
            if grid[row, column] == Game.CellType.Empty:
                color = (255, 255, 255)
            elif grid[row, column] == Game.CellType.Full:
                color = (102, 102, 102)
            elif grid[row, column] == Game.CellType.Visited:
                color = (0, 0, 255) 
            elif grid[row, column] == Game.CellType.Start:
                color = (0, 255, 0)
            elif grid[row, column] == Game.CellType.End:
                color = (255, 0, 0)
       
            
            m = GameConstants.gridMarginSize
            w = GameConstants.gridCellWidth
            h = GameConstants.gridCellHeight
            rects += [pygame.draw.rect(screen, color, [(2*m+w) * column + m, (2*m+h) * row + m, w, h])]    
    
    return rects


def initialize():
    random.seed(GameConstants.randomSeed)
    pygame.init()
    font = pygame.font.SysFont('Courier', GameConstants.fontSize)
    fpsClock = pygame.time.Clock()

    # Create display surface
    screen = pygame.display.set_mode((GameConstants.screenWidth, GameConstants.screenHeight), pygame.DOUBLEBUF)
    screen.fill(GameConstants.BackgroundColor)
        
    return screen, font, fpsClock


def handleEvents():
   
    for event in pygame.event.get():
        '''
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            
            col = pos[0] // (GameConstants.screenWidth // GameConstants.gridWidth)
            row = pos[1] // (GameConstants.screenHeight // GameConstants.gridHeight)
            #print('clicked cell: {}, {}'.format(cellX, cellY))
        '''
                        
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()


def readGridFile(fileName):
    # Determine map size
    maxLineSize = 0
    lineCount = 0
    with open(fileName, 'r', encoding='utf8') as f:
        for line in f:
            if len(line) > maxLineSize:
                maxLineSize = len(line)
                
            lineCount += 1
    
    grid = np.ones((lineCount, maxLineSize - 1))*Game.CellType.Empty
    
    # Read map
    row = 0
    col = 0
    posStart = (-1, -1)
    posEnd = (-1, -1)
    with open(fileName, 'r', encoding='utf8') as f:
        while True:
            c = f.read(1)
            if len(c) == 0:
                break
            
            if c == '*':
                grid[row][col] = Game.CellType.Full
            
            if c == 'S':
                grid[row][col] = Game.CellType.Start
                posStart = (row, col)
            
            if c == 'E':
                grid[row][col] = Game.CellType.End
                posEnd = (row, col)
            
            if c == '\n':
                row += 1
                col = 0
            else:
                col += 1
    
    return grid, posStart, posEnd

def funcHeuristica2(celula1, celula2):
    X1, Y1 = celula1
    X2, Y2 = celula2
    
    cateto1 = abs(X1-X2)
    cateto2 = abs(Y1-Y2)

    return math.sqrt((cateto1*cateto1)+(cateto2*cateto2))

def funcHeuristica(celula1, celula2):
    return np.linalg.norm(np.array(celula1)-np.array(celula2))

def main():
    grid, posStart, posEnd = readGridFile('maze-8.txt')
    
    # grid size in units
    GameConstants.gridHeight = grid.shape[0]
    GameConstants.gridWidth = grid.shape[1]
    ratio = grid.shape[1]/grid.shape[0]

    print('Start pos: {}'.format(posStart))
    print('End pos: {}'.format(posEnd))
    
    print(funcHeuristica(posStart, posEnd))
    ############### MAIN DIJKSTRA ALGORITHM ###############
    # Create a paired list of all possible cells
    Q = list(itertools.product(range(GameConstants.gridHeight),range(GameConstants.gridWidth)))

    # Remove walls from Q
    for row in range(GameConstants.gridHeight):
        for col in range(GameConstants.gridWidth):
            if grid[row][col] == Game.CellType.Full:
                Q.remove((row,col))

    # Stores cell->distance to startPos (distances)
    dist = dict(zip(Q, [10000 for i in range(GameConstants.gridHeight*GameConstants.gridWidth)]))
    # Stores cell->nearest cell with smallest distance to startPos (previous best)
    prev = dict(zip(Q, [None for i in range(GameConstants.gridHeight*GameConstants.gridWidth)]))
    dist[posStart] = 0

    visited = []

    while Q:
        # consider only items in Q
        distQ = {k:v for (k,v) in dist.items() if k in Q}
        u = min(distQ, key=distQ.get)

        # remove u from Q
        Q.remove(u)
        
        visited.append(u)
        if u == posEnd:
            break

        # check neighbours
        neighbours = u + np.array(list(itertools.product((0,-1,+1), (0,-1,+1))),dtype=int)
        neighbours = [tuple(v) for v in neighbours]
        neighbours.pop(0) # the first element (u) is not a neighbour
    
        # update distances
        for v in neighbours:
            if v in Q:
                alt = dist[u] + funcHeuristica(v, posEnd) - funcHeuristica(u, posEnd)
                if alt < dist[v]:               
                    dist[v] = alt 
                    prev[v] = u 
                

    ############### MAIN DIJKSTRA ALGORITHM ###############
    # From this point on, all nodes have been visited, distances from posStart calculated and stored in "dist"
    
    Game.visited = visited

    ratioW = 1
    ratioH = 1
    
    if ratio > 1:
        ratioH = ratio
    elif ratio < 1:
        ratioW = 1/ratio
    
    # grid size in pixels
    GameConstants.gridCellWidth = math.floor((GameConstants.screenWidth//GameConstants.gridWidth - 2*GameConstants.gridMarginSize)/ratioW)
    GameConstants.gridCellHeight = math.floor((GameConstants.screenHeight//GameConstants.gridHeight - 2*GameConstants.gridMarginSize)/ratioH)

    #grid = np.ones((GameConstants.gridHeight, GameConstants.gridWidth))
    #grid = np.random.rand(GameConstants.gridHeight, GameConstants.gridWidth)
    
    try:
        # Initialize pygame and etc.
        screen, font, fpsClock = initialize()
              
        # Main game loop
        while True:
            # Handle events
            handleEvents()
                    
            # Update world
            #game.update()
            # Print visited nodes one by one
            if Game.visited:
                u = Game.visited.pop(0)
                grid[u[0]][u[1]] = Game.CellType.Visited
            
            # Draw this world frame
            rects = drawGrid(screen, grid)

            # If there are no more visited nodes, print position, distance to startPos and previous best of each cell
            if not Game.visited:
                m = GameConstants.gridMarginSize
                w = GameConstants.gridCellWidth
                h = GameConstants.gridCellHeight
                for (k,v) in dist.items():
                    row, column = k[0], k[1]
                    printText(screen, '({0},{1})'.format(row, column), (2*m+w) * column + m, (2*m+h) * row + m, 10, (0,0,0))
                    printText(screen, '{0:.2f}'.format(v), (2*m+w) * column + m, (2*m+h) * row + m + 10, 10, (30, 30, 30))
                    if prev[k]:
                        r, c = prev[k]
                        printText(screen, '({0},{1})'.format(r, c), (2*m+w) * column + m, (2*m+h) * row + m + 20, 10, (30,30,30))
            
            pygame.display.update(rects)
            
            # Delay for required FPS
            fpsClock.tick(GameConstants.FPS)
            
        # close up shop
        pygame.quit()
    except SystemExit:
        pass
    except Exception as e:
        #print("Unexpected error:", sys.exc_info()[0])
        traceback.print_exc(file=sys.stdout)
        pygame.quit()
        #raise Exception from e
    
    
if __name__ == "__main__":
    # Set the working directory (where we expect to find files) to the same
    # directory this .py file is in. You can leave this out of your own
    # code, but it is needed to easily run the examples using "python -m"
    file_path = os.path.dirname(os.path.abspath(__file__))
    print(file_path)
    os.chdir(file_path)

    main()