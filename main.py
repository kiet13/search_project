import pygame
from pygame.locals import *
from sys import exit
from enum import Enum
import argparse
from drawing import *
from search import *

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', metavar='', type=str, help="Input txt file")
parser.add_argument('-a', '--algorithm', metavar='', type=str, help="Algorithm for searching")
args = parser.parse_args()


class State(Enum):
    OBSTACLE = 0
    CAN_MOVE = 1
    START = 2
    END = 3
    PICKUP_POINT = 4


array2DGrid = [[]]


class Polygon:
    def __init__(self, peakPoints):
        self.peakPoints = peakPoints

    def draw(self, surface, grid, color):
        for i in range(len(self.peakPoints)):
            j = i + 1
            if j == len(self.peakPoints):
                j = 0
            di = plotLine(self.peakPoints[i][0], self.peakPoints[i][1],
                          self.peakPoints[j][0], self.peakPoints[j][1])
            for point in di:
                drawCube(surface, grid, color, point[0], point[1])
                array2DGrid[point[0]][point[1]] = State.OBSTACLE


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


if __name__ == '__main__':

    # Get data from file input

    listPoints = []
    listPolygons = []
    fileInput = open(args.input, 'r')
    # read rows and columns
    columns, rows = fileInput.readline().rstrip('\n').split(',')
    rows = int(rows) + 1
    columns = int(columns) + 1
    array2DGrid = [[State.CAN_MOVE for _ in range(rows)] for _ in range(columns)]
    # read points position
    points = list(map(int, fileInput.readline().rstrip('\n').split(',')))
    for i in range(1, len(points), 2):
        listPoints.append((points[i - 1], points[i]))
    numPolygons = int(fileInput.readline().rstrip('\n'))
    # read peak points of the polygons
    if numPolygons != 0:
        for i in range(numPolygons):
            listPeakPolygons = []
            points = list(map(int, fileInput.readline().rstrip('\n').split(',')))
            for i in range(1, len(points), 2):
                listPeakPolygons.append((points[i - 1], points[i]))
            polygon = Polygon(listPeakPolygons)
            listPolygons.append(polygon)
    fileInput.close()

    # display screen and draw object
    grid = Grid(25, rows, columns)
    pygame.init()
    SCREEN_SIZE = (800, 600)
    screen = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE, 32)

    screen.lock()
    # draw boundary
    boundary = Polygon([(0, 0), (0, rows - 1), (columns - 1, rows - 1), (columns - 1, 0)])
    boundary.draw(screen, grid, (96, 96, 96))
    # draw polygons
    for polygon in listPolygons:
        polygon.draw(screen, grid, (255, 255, 0))
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

    path = None
    if args.algorithm == 'dfs':
        path = depthFirstSearch(graph, listPoints[0], listPoints[-1])
    elif args.algorithm == 'ucs':
        path = uninformedCostSearch(graph, listPoints[0], listPoints[-1])     
    elif args.algorithm == 'gbfs':
        path = greedyBestFirstSearch(graph, listPoints[0], listPoints[-1])     

    if path is None:
        print('Path not found')

    r, g = 204, 204
    screen.lock()
    for idx, point in enumerate(path):
        pygame.event.get()
        if idx == len(path)-1:
            drawCircle(screen, grid, (255, 0, 255), point[0], point[1])
        elif idx > 0:
            drawCircle(screen, grid, (r, g, 255), point[0], point[1])
        pygame.display.update()
        pygame.time.wait(500)
        if r > 51 and g > 51:
            r -= 5
            g -= 5
    screen.unlock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
