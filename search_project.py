import pygame
from pygame.locals import *
from sys import exit
from enum import Enum
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', metavar='', type=str, help="Input txt file")
args = parser.parse_args()


class State(Enum):
    OBSTACLE = 0
    CAN_MOVE = 1
    START = 2
    END = 3
    PICKUP_POINT = 4

array2DGrid = [[]]
sizeCube = 25

rows, columns = 0, 0


def parseCoordinate(gridX, gridY):
    map_width = sizeCube * columns
    map_height = sizeCube * rows
    x = gridX * sizeCube
    y = map_height - (gridY + 1)*sizeCube
    return x, y

def drawGrid(surface, color, rows, columns):
    x, y = 0, 0
    map_width = sizeCube * columns
    map_height = sizeCube * rows
    for _ in range(columns):
        x += sizeCube
        pygame.draw.line(surface, color, (x, 0), (x, map_height))

    for _ in range(rows):
        y += sizeCube
        pygame.draw.line(surface, color, (0, y), (map_width, y))


def plotLineLow(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    yi = 1
    peakPoints = [(x0, y0)]
    if dy < 0:
        yi = -1
        dy = -dy
    P = 2*dy - dx
    y = y0
    for x in range(x0 + 1, x1):
        if P >= 0:
            P -= 2*dx
            y += yi
        P += 2*dy
        peakPoints.append((x, y))
    peakPoints.append((x1, y1))

    return peakPoints


def plotLineHigh(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    xi = 1
    peakPoints = [(x0, y0)]
    if dx < 0:
        xi = -1
        dx = -dx
    P = 2*dx - dy
    x = x0
    for y in range(y0 + 1, y1):
        if P >= 0:
            P -= 2*dy
            x += xi
        P += 2*dx
        peakPoints.append((x, y))
    peakPoints.append((x1, y1))

    return peakPoints


def plotLine(x0, y0, x1, y1):
    if abs(y1-y0) < abs(x1 - x0):
        if x0 < x1:
            return plotLineLow(x0, y0, x1, y1)
        else:
            return plotLineLow(x1, y1, x0, y0)
    else:
        if y0 < y1:
            return plotLineHigh(x0, y0, x1, y1)
        else:
            return plotLineHigh(x1, y1, x0, y0)


def drawCube(surface, color, gridX, gridY):
    x, y = parseCoordinate(gridX, gridY)
    pygame.draw.rect(surface, color, Rect(x, y, sizeCube, sizeCube))


def drawCircle(surface, color, gridX, gridY):
    x, y = parseCoordinate(gridX, gridY)
    radius = sizeCube // 2
    x += radius
    y += radius
    pygame.draw.circle(surface, color, (x, y), radius)


class Polygon:
    def __init__(self, peakPoints):
        self.peakPoints = peakPoints

    def draw(self, surface, color):
        for i in range(len(self.peakPoints)):
            j = i + 1
            if j == len(self.peakPoints):
                j = 0
            di = plotLine(self.peakPoints[i][0], self.peakPoints[i][1],
                          self.peakPoints[j][0], self.peakPoints[j][1])
            for point in di:
               drawCube(surface, color, point[0], point[1])
               array2DGrid[point[0]][point[1]] = State.OBSTACLE

def getNeightbors(gridX, gridY):
    listNeightbors = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            nearX, nearY = gridX+i, gridY+j
            if (((nearX < columns) and (nearY < rows)) and
               ((nearX >= 0) and (nearY >=0))) and (i != 0 or j != 0):
               if array2DGrid[nearX][nearY] != State.OBSTACLE:
                    if abs(i) == 1 and abs(j) == 1:
                        if (array2DGrid[nearX-i][nearY] == State.OBSTACLE
                        and array2DGrid[nearX][nearY-j] == State.OBSTACLE):
                            continue
                    listNeightbors.append((nearX, nearY))
    return listNeightbors      

class PriorityQueue:
    def __init__(self, queue = []):
        self.queue = queue

    def isEmpty(self):
        return len(self.queue) == 0

    def enqueue(self, newNode):
        idx = 0
        for node in self.queue:
            if newNode[1][0] >= node[1][0]:
                idx += 1
            else:
                break
        self.queue.insert(idx, newNode)
    
    def dequeue(self):
        result = self.queue[0]
        del self.queue[0]
        return result

        

def getSolution(listNodes):
    solution = [listNodes[0][0]]
    idx = 0
    while True:
        nextNode = listNodes[idx][1][1]
        idx = next((i for i, value in enumerate(listNodes) if value[0] == nextNode), None)
        if idx == None:
            break
        else:
            solution.append(listNodes[idx][0])
    
    return solution[::-1] # reverse



def uninformedCostSearch(graph, root, goal):
    node = (root, (0, None))  #  root(0;null)
    frontier = PriorityQueue([node])
    explored = []
    listNodes = []
    while True:
        if frontier.isEmpty():
            return False           
        node = frontier.dequeue()
        listNodes.insert(0, node)
        if node[0] == goal:
            return getSolution(listNodes)
        explored.append(node)
        
        cost = node[1][0] + 1 
        # check neightbor
        for neightbor in graph[node[0]]:
            neightbor = (neightbor, (cost, node[0]))
            neightborIndex = next((idx for idx, value in enumerate(explored)
                                            if value[0] == neightbor[0]), None)
            if neightborIndex == None: # If neightbor not in explored
                neightborIndex = next((idx for idx, value in enumerate(frontier.queue)
                                            if value[0] == neightbor[0]), None)
                if neightborIndex == None: # If neightbor not in frontier
                    frontier.enqueue(neightbor)
                else:
                    # search already nodes in frontier and update them.
                    if neightbor[1][0] < frontier.queue[neightborIndex][1][0]:
                        frontier.queue[neightborIndex] = neightbor


    

if __name__ == '__main__':
    
    listPoints = []
    listPolygons = []
   
    
    fileInput = open(args.input, 'r')
    # read rows and columns
    columns, rows = fileInput.readline().rstrip('\n').split(',')
    rows  = int(rows) + 1
    columns = int(columns) + 1
    array2DGrid = [[State.CAN_MOVE for _ in range(rows)] for _ in range(columns)]
    # read points position
    points = list(map(int, fileInput.readline().rstrip('\n').split(',')))
    for i in range(1, len(points), 2):
        listPoints.append((points[i-1], points[i]))
    numPolygons = int(fileInput.readline().rstrip('\n'))
    # read peak points of the polygons
    if (numPolygons != 0):
        for i in range(numPolygons):
            listPeakPolygons = []
            points = list(map(int, fileInput.readline().rstrip('\n').split(',')))
            for i in range(1, len(points), 2):
                listPeakPolygons.append((points[i-1], points[i]))
            polygon = Polygon(listPeakPolygons)
            listPolygons.append(polygon)
    fileInput.close()

    pygame.init()
    screen = pygame.display.set_mode((1280, 720), 0 , 32)

    



    screen.lock()
    # draw boundary
    boundary = Polygon([(0,0), (0, rows-1), (columns-1,rows-1), (columns-1,0)])
    boundary.draw(screen, (96, 96, 96))
    # draw polygons
    for polygon in listPolygons:
        polygon.draw(screen, (255, 255, 0))
    # draw start, end and pickup points
    for idx, point in enumerate(listPoints):
        drawCircle(screen, (0, 0, 255), point[0], point[1])
        if idx == 0:
            array2DGrid[point[0]][point[1]] = State.START
        elif idx == len(listPoints)-1:
            array2DGrid[point[0]][point[1]] = State.END
        else:
            array2DGrid[point[0]][point[1]] = State.PICKUP_POINT
    drawGrid(screen, (255, 255, 255), rows, columns)
    screen.unlock()
    pygame.display.update()

    graph = {}
    getNeightbors(2, 5)
    for i in range(columns):
        for j in range(rows):
            if array2DGrid[i][j] != State.OBSTACLE:
                graph[(i, j)] = getNeightbors(i, j)

    path = uninformedCostSearch(graph, listPoints[0], listPoints[-1])
    
    #screen.lock()
    for point in path[1:-1]:
        drawCircle(screen, (0, 128, 255), point[0], point[1])
        pygame.display.update()
        pygame.time.wait(100)
    #screen.unlock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
        




