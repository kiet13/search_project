import pygame
from pygame.locals import *
from sys import exit
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', metavar='', type=str, help="Input txt file")
args = parser.parse_args()

sizeCube = 35
array2DGrid = [[]]
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

if __name__ == '__main__':
    
    listPoints = []
    listPolygons = []
    
    fileInput = open(args.input, 'r')
    # read rows and columns
    columns, rows = fileInput.readline().rstrip('\n').split(',')
    rows  = int(rows) + 1
    columns = int(columns) + 1
    # read points position
    points = list(map(int, fileInput.readline().rstrip('\n').split(',')))
    for i in range(1, len(points), 2):
        listPoints.append((points[i-1], points[i]))
    numPolygons = int(fileInput.readline().rstrip('\n'))
    # read peak points of the polygons
    
    for i in range(numPolygons):
        listPeakPolygons = []
        points = list(map(int, fileInput.readline().rstrip('\n').split(',')))
        for i in range(1, len(points), 2):
            listPeakPolygons.append((points[i-1], points[i]))
        polygon = Polygon(listPeakPolygons)
        listPolygons.append(polygon)
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), 0 , 32)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()



        screen.lock()
        # draw boundary
        boundary = Polygon([(0,0), (0, rows-1), (columns-1,rows-1), (columns-1,0)])
        boundary.draw(screen, (96, 96, 96))
        for polygon in listPolygons:
            polygon.draw(screen, (255, 255, 0))

        for point in listPoints:
            drawCircle(screen, (0, 0, 255), point[0], point[1])
        drawGrid(screen, (255, 255, 255), rows, columns)
        screen.unlock()

        pygame.display.update()
