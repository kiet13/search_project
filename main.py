import pygame
from pygame.locals import *
from sys import exit
from enum import Enum
import argparse
from drawing import *
from search import *
import tkinter as tk
from tkinter import messagebox

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', metavar='', type=str, help="Input txt file")
parser.add_argument('-a', '--algorithm', nargs='?', metavar='', type=str, help="Algorithm for searching")
parser.add_argument('-m', '--move', nargs='?', default=False, metavar='', type=bool, help="Input txt file")
args = parser.parse_args()


class State(Enum):
    OBSTACLE = 0
    CAN_MOVE = 1
    START = 2
    END = 3
    PICKUP_POINT = 4


array2DGrid = [[]]


class Polygon:
    def __init__(self, peakPoints, color):
        self.peakPoints = peakPoints
        self.color = color
        self.edges = [] 
        for i in range(len(self.peakPoints)):
            j = i + 1
            if j == len(self.peakPoints):
                j = 0
            di = plotLine(self.peakPoints[i][0], self.peakPoints[i][1],
                          self.peakPoints[j][0], self.peakPoints[j][1])
            self.edges.append(di[1:-1])
            
    def draw(self, surface, grid):
        for edge in self.edges:
            for point in edge:
                drawCube(surface, grid, self.color, point[0], point[1])
                array2DGrid[point[0]][point[1]] = State.OBSTACLE

        for point in self.peakPoints:
            drawCube(surface, grid, self.color, point[0], point[1])
            array2DGrid[point[0]][point[1]] = State.OBSTACLE

    def remove(self, surface, grid, color):
        for edge in self.edges:
            for point in edge:
                drawCube(surface, grid, color, point[0], point[1])
                array2DGrid[point[0]][point[1]] = State.CAN_MOVE

        for point in self.peakPoints:
            drawCube(surface, grid, color, point[0], point[1])
            array2DGrid[point[0]][point[1]] = State.CAN_MOVE

    def move(self, surface, grid):
        import random
        self.remove(surface, grid, self.color)

        newPeakPoints = self.peakPoints[:]
        randomTimes = 0
        i = 0
        gridX = gridY = 0
        while i < len(newPeakPoints):
            while abs(gridX) == abs(gridY):
                gridX = random.randint(-1, 1)
                gridY = random.randint(-1, 1)
            newX = newPeakPoints[i][0] + gridX
            newY = newPeakPoints[i][1] + gridY
            if newX <= 0 or newY <= 0 or newX >= columns or newY >= rows:
                if randomTimes == 3:
                    self.draw(surface, grid)
                    randomTimes = 0
                    return False
                else:
                    randomTimes += 1
                    continue
            if (array2DGrid[newX][newY] == State.OBSTACLE or
                array2DGrid[newX][newY] == State.END or
                array2DGrid[newX][newY] == State.START):
                if randomTimes == 3:
                    self.draw(surface, grid)
                    randomTimes = 0
                    return False
                else:
                    randomTimes += 1
                    continue
            newPeakPoints[i] = (newX, newY)
            i += 1
        
        newPolygon = Polygon(newPeakPoints, self.color)
        for edge in newPolygon.edges:
            for point in edge:
                if newX <= 0 or newY <= 0 or newX >= columns or newY >= rows:
                        self.draw(surface, grid)
                        return False
                if (array2DGrid[point[0]][point[1]] == State.OBSTACLE or
                    array2DGrid[point[0]][point[1]] == State.END or
                    array2DGrid[point[0]][point[1]] == State.START):   
                        self.draw(surface, grid)
                        return False
        self.remove(surface, grid, (0, 0, 0))
        newPolygon.draw(surface, grid)
        
        self.__init__(newPeakPoints, newPolygon.color)
        return True

                
def getNeightbors(gridX, gridY):
    listNeightbors = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            nearX, nearY = gridX + i, gridY + j
            if (((nearX < columns) and (nearY < rows)) and
                ((nearX >= 0) and (nearY >= 0))) and (i != 0 or j != 0):
                if array2DGrid[nearX][nearY] != State.OBSTACLE:
                    if abs(i) == 1 and abs(j) == 1:
                        if (array2DGrid[nearX - i][nearY] == State.OBSTACLE
                                and array2DGrid[nearX][nearY - j] == State.OBSTACLE):
                            continue
                    listNeightbors.append((nearX, nearY))
    return listNeightbors

def drawPath(path):
    r, g = 204, 204
    screen.lock()
    for idx, point in enumerate(path):
        pygame.event.get()
        if idx == len(path)-1:
            drawCircle(screen, grid, (255, 0, 255), point[0], point[1])
            if idx != 1:
                drawCircle(screen, grid, (128, 128, 128), path[idx-1][0], path[idx-1][1])
            else:
                drawCircle(screen, grid, (0, 0, 255), path[idx-1][0], path[idx-1][1])
        elif idx > 0 and idx != 1:
            drawCircle(screen, grid, (0, 0, 255), point[0], point[1])
            drawCircle(screen, grid, (128, 128, 128), path[idx-1][0], path[idx-1][1])
        elif idx == 1:
            drawCircle(screen, grid, (0, 0, 255), point[0], point[1])
            if (array2DGrid[path[idx-1][0]][path[idx-1][1]] == State.PICKUP_POINT):
                drawCircle(screen, grid, (0, 255, 255), path[idx-1][0], path[idx-1][1])
            elif (array2DGrid[path[idx-1][0]][path[idx-1][1]] == State.START):
                drawCircle(screen, grid, (0, 0, 255), path[idx-1][0], path[idx-1][1])
        
        pygame.display.update()
        pygame.time.wait(300)
        # if r > 0 and g > 0:
        #     r -= 1
        #     g -= 1
    screen.unlock()

def message_box(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    messagebox.showinfo(subject, content)
    try:
        root.destroy()
    except:
        pass

if __name__ == '__main__':

    # Get data from file input

    listPoints = []
    listPolygons = []
    fileInput = open(args.input, 'r')
    # read rows and columns
    columns, rows = fileInput.readline().rstrip('\n').split(',')
    rows = int(rows)
    columns = int(columns)
    array2DGrid = [[State.CAN_MOVE for _ in range(rows)] for _ in range(columns)]
    # read points position
    points = list(map(int, fileInput.readline().rstrip('\n').split(',')))
    for i in range(1, len(points), 2):
        listPoints.append((points[i - 1], points[i]))
    # swap goal point and last point
    listPoints[1], listPoints[-1] = listPoints[-1], listPoints[1]
    numPolygons = int(fileInput.readline().rstrip('\n'))
    # read peak points of the polygons
    if numPolygons != 0:
        for i in range(numPolygons):
            listPeakPolygons = []
            points = list(map(int, fileInput.readline().rstrip('\n').split(',')))
            for i in range(1, len(points), 2):
                listPeakPolygons.append((points[i - 1], points[i]))
            polygon = Polygon(listPeakPolygons, (255, 255, 0))
            listPolygons.append(polygon)
    fileInput.close()

    # display screen and draw object
    grid = Grid(25, rows, columns)
    pygame.init()
    SCREEN_SIZE = (800, 600)
    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 0)

    screen.lock()
    # draw boundary
    boundary = Polygon([(0, 0), (0, rows-1), (columns-1, rows-1), (columns-1, 0)], (96, 96, 96))
    boundary.draw(screen, grid)
    # draw polygons
    for polygon in listPolygons:
        polygon.draw(screen, grid)
    # draw start, end and pickup points
    for idx, point in enumerate(listPoints):
        if idx == 0:
            array2DGrid[point[0]][point[1]] = State.START
            drawCircle(screen, grid, (0, 0, 255), point[0], point[1])
        elif idx == len(listPoints) - 1:
            array2DGrid[point[0]][point[1]] = State.END
            drawCircle(screen, grid, (255, 0, 0), point[0], point[1])
        else:
            array2DGrid[point[0]][point[1]] = State.PICKUP_POINT
            drawCircle(screen, grid, (0, 255, 0), point[0], point[1])
    grid.draw(screen, (255, 255, 255))
    screen.unlock()
    pygame.display.update()

    # search
    graph = {}
    getNeightbors(2, 5)
    for i in range(columns):
        for j in range(rows):
            if array2DGrid[i][j] != State.OBSTACLE:
                graph[(i, j)] = getNeightbors(i, j)
    if args.move == False:
        path = None
        if len(listPoints) == 2:
            if args.algorithm == 'dfs':
                path = depthFirstSearch(graph, listPoints[0], listPoints[-1])
            elif args.algorithm == 'ucs':
                path = uninformedCostSearch(graph, listPoints[0], listPoints[-1])     
            elif args.algorithm == 'gbfs':
                path = greedyBestFirstSearch(graph, listPoints[0], listPoints[-1])
            elif args.algorithm == 'astar':
                path = astarSearch(graph, listPoints[0], listPoints[-1])
            
            if path is None:
                message_box("Warning", "Path not found")
                exit()
            drawPath(path)
        else:
            if numPolygons != 0:
                allPaths = pickUpPoints(graph, listPoints)
                for path in allPaths:
                    if path is None:
                        message_box("Warning", "Path not found")
                        exit()
                    drawPath(path)
            else:
                orderPoints = pickUpPointsWithoutObstacle(graph, listPoints)
                for i in range(len(orderPoints)-1):
                    path = greedyBestFirstSearch(graph, orderPoints[i], orderPoints[i+1])
                    drawPath(path)
    else:
       
        path = None
        head = listPoints[0]
        tail = listPoints[-1]
        count = 0
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
            if count == 10:
                message_box("Warning", "I can't wait anymore! Please try again!")
                exit()
            screen.lock()
            for i in range(len(listPolygons)):
                listPolygons[i].move(screen, grid)

            if path != []:
                
                for i in range(columns):
                    for j in range(rows):
                        if array2DGrid[i][j] != State.OBSTACLE:
                            graph[(i, j)] = getNeightbors(i, j)
                
                path = uninformedCostSearch(graph, head, tail)
                if path is None:
                    count += 1
                if path is not None:
                    count = 0
                    array2DGrid[head[0]][head[1]] = State.CAN_MOVE
                    drawCube(screen, grid, (0, 0, 0), head[0], head[1])
                    del path[0]
                    head = path[0]
                    array2DGrid[path[0][0]][path[0][1]] = State.START
                    if (len(path) > 1):
                        drawCircle(screen, grid, (0, 0, 255), head[0], head[1])
                    else:
                        drawCircle(screen, grid, (255, 0, 255), head[0], head[1])
                        path = []
            grid.draw(screen, (255, 255, 255))
            pygame.display.update()
            screen.unlock()
            pygame.time.wait(500)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

    
