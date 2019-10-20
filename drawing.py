import pygame
from pygame.locals import *


class Grid:
    def __init__(self, sizeCube, rows, columns):
        self.sizeCube = sizeCube
        self.rows = rows
        self.columns = columns

    def draw(self, surface, color):
        x, y = 0, 0
        map_width = self.sizeCube * self.columns
        map_height = self.sizeCube * self.rows
        for _ in range(self.columns):
            x += self.sizeCube
            pygame.draw.line(surface, color, (x, 0), (x, map_height))

        for _ in range(self.rows):
            y += self.sizeCube
            pygame.draw.line(surface, color, (0, y), (map_width, y))
    
    def parseCoordinate(self, gridX, gridY):
        map_width = self.sizeCube * self.columns
        map_height = self.sizeCube * self.rows
        x = gridX * self.sizeCube
        y = map_height - (gridY + 1) * self.sizeCube
        return x, y


def plotLineLow(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    yi = 1
    peakPoints = [(x0, y0)]
    if dy < 0:
        yi = -1
        dy = -dy
    P = 2 * dy - dx
    y = y0
    for x in range(x0 + 1, x1):
        if P >= 0:
            P -= 2 * dx
            y += yi
        P += 2 * dy
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
    P = 2 * dx - dy
    x = x0
    for y in range(y0 + 1, y1):
        if P >= 0:
            P -= 2 * dy
            x += xi
        P += 2 * dx
        peakPoints.append((x, y))
    peakPoints.append((x1, y1))

    return peakPoints


def plotLine(x0, y0, x1, y1):
    if abs(y1 - y0) < abs(x1 - x0):
        if x0 < x1:
            return plotLineLow(x0, y0, x1, y1)
        else:
            return plotLineLow(x1, y1, x0, y0)
    else:
        if y0 < y1:
            return plotLineHigh(x0, y0, x1, y1)
        else:
            return plotLineHigh(x1, y1, x0, y0)


def drawCube(surface, grid, color, gridX, gridY):
    x, y = grid.parseCoordinate(gridX, gridY)
    pygame.draw.rect(surface, color, Rect(x, y, grid.sizeCube, grid.sizeCube))


def drawCircle(surface, grid, color, gridX, gridY):
    x, y = grid.parseCoordinate(gridX, gridY)
    radius = grid.sizeCube // 2
    x += radius
    y += radius
    pygame.draw.circle(surface, color, (x, y), radius)
