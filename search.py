class PriorityQueue:
    def __init__(self, queue=None):
        if queue is None:
            queue = []
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

    def enqueueGBFS(self , newNode):
        idx = 0
        for node in self.queue:
            if newNode[1] >= node[1]:
                idx += 1
            else:
                break
        self.queue.insert(idx, newNode)

    def enqueueAStar(self, newNode):
        idx = 0
        for node in self.queue:
            fn1 = newNode[1] + newNode[2]
            fn2 = node[1] + node[2]
            hn1 = newNode[2]
            hn2 = node[2]
            if (fn1 > fn2) or (fn1 == fn2 and hn1 > hn2):
                idx += 1
            else:
                break
        self.queue.insert(idx, newNode)

    def dequeue(self):
        result = self.queue[0]
        del self.queue[0]
        return result


def getSolutionUCS(listNodes):
    solution = [listNodes[0][0]]
    idx = 0
    while True:
        nextNode = listNodes[idx][1][1]
        idx = next((i for i, value in enumerate(listNodes) if value[0] == nextNode), None)
        if idx is None:
            break
        else:
            solution.append(listNodes[idx][0])

    return solution[::-1]  # reverse


def checkDiagonal(point1, point2):
    if abs(point1[0] - point2[0]) == 1 and abs(point1[1] - point2[1]) == 1:
        return True
    return False


def uninformedCostSearch(graph, root, goal):
    node = (root, (0, None))  # root(0;null)
    frontier = PriorityQueue([node])
    explored = []
    listNodes = []
    while True:
        if frontier.isEmpty():
            return None
        node = frontier.dequeue()
        listNodes.insert(0, node)
        if node[0] == goal:
            return getSolutionUCS(listNodes)
        explored.append(node)

        cost = node[1][0] + 1
        # check neighbors
        for neightbor in graph[node[0]]:
            if checkDiagonal(node[0], neightbor) == True:
                neightbor = (neightbor, (cost + 1, node[0]))
            else:
                neightbor = (neightbor, (cost, node[0]))
            neightborIndex = next((idx for idx, value in enumerate(explored)
                                   if value[0] == neightbor[0]), None)
            if neightborIndex == None:  # If neightbor not in explored
                neightborIndex = next((idx for idx, value in enumerate(frontier.queue)
                                       if value[0] == neightbor[0]), None)
                if neightborIndex == None:  # If neightbor not in frontier
                    frontier.enqueue(neightbor)
                else:
                    # search already nodes in frontier and update them.
                    if neightbor[1][0] < frontier.queue[neightborIndex][1][0]:
                        frontier.queue[neightborIndex] = neightbor

def getSolution(parentMap, goal):
    curr = goal
    solution = []
    while (curr != None):
        solution.insert(0, curr)
        try:
            curr = parentMap[curr]
        except KeyError:
            curr = None
    return solution

def depthFirstSearch(graph, root, goal):
    stack = [root]
    visited = []
    parentMap = {}
    while len(stack) != 0:
        node = stack[-1]
        del stack[-1]  # stack.pop()
        if node not in visited:
            visited.append(node)
            if node == goal:
                return getSolution(parentMap, goal)
            for neightbor in graph[node]:
                if neightbor in visited:
                    continue
                stack.append(neightbor)  # stack.push()
                parentMap[neightbor] = node
    return None

def heuristic(node, goal):
    D = 1
    D2 = 1.5
    dx1 = abs(node[0] - goal[0])
    dy1 = abs(node[1] - goal[1])
    result = D*(dx1+dy1) + (D2 - 2*D)*min(dx1, dy1)
    # dx2 = root[0] - goal[0]
    # dy2 = root[1] - goal[1]
    # cross = abs(dx1*dy2 - dx2*dy1)
    # result += cross*0.001
    return result

def greedyBestFirstSearch(graph, root, goal):
    visited = []
    parentMap = {}
    queue = PriorityQueue()
    node = (root, heuristic(root, goal))
    queue.enqueueGBFS(node)
    while not queue.isEmpty():
        node = queue.dequeue()
        visited.append(node[0])
        if node[0] == goal:
            return getSolution(parentMap, goal)
        for neightbor in graph[node[0]]:
            if neightbor in visited:
                continue
            neightbor = (neightbor, heuristic(neightbor, goal))
            queue.enqueueGBFS(neightbor)
            parentMap[neightbor[0]] = node[0]
    return None

def astarSearch(graph, root, goal):
    visited = []
    parentMap = {}
    cost = 1
    queue = PriorityQueue()
    node = (root, 0, heuristic(root, goal))
    queue.enqueueAStar(node)
    while not queue.isEmpty():
        node = queue.dequeue()
        visited.append(node[0])
        if node[0] == goal:
            return getSolution(parentMap, goal)
        for neightbor in graph[node[0]]:
            if neightbor in visited:
                continue
            if checkDiagonal(node[0], neightbor) == True:
                cost = 1.5
            else:
                cost = 1
            neightbor = (neightbor, node[1]+cost, heuristic(neightbor, goal))
            queue.enqueueAStar(neightbor)
            parentMap[neightbor[0]] = node[0]
    return None


def calculateCost(path):
    cost = 0
    for i in range(1, len(path)):
        cost += 1
        if checkDiagonal(path[i], path[i-1]) == True:
            cost += 0.5
    return cost 

def pickUpPoints(graph, listPoints):
    noVisited = listPoints[1:-1]
    root = listPoints[0]
    goal = listPoints[-1]
    visited = [root]
    allPaths = []
    while len(noVisited) > 0:
        costList = []
        paths = []
        for node in noVisited:
            path = uninformedCostSearch(graph, visited[-1], node)
            paths.append(path)
            costList.append(calculateCost(path))
        idx = costList.index(min(costList))
        visited.append(noVisited[idx])
        allPaths.append(paths[idx])
        del noVisited[idx]
    
    allPaths.append(uninformedCostSearch(graph, visited[-1], goal))
    return allPaths

def pickUpPointsWithoutObstacle(graph, listPoints):
    unvisited = listPoints[1:-1]
    root = listPoints[0]
    goal = listPoints[-1]
    visited = [root]
    allPaths = []
    while len(unvisited) > 0:
        heuristicList = []
        paths = []
        for node in unvisited:
            hn =  heuristic(visited[-1], node)
            heuristicList.append(hn)
        idx = heuristicList.index(min(heuristicList))
        visited.append(unvisited[idx])
        del unvisited[idx]
    visited.append(goal)
    return visited


    