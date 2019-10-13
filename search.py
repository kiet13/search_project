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

    def enqueueHeuristic(self , newNode):
        idx = 0
        for node in self.queue:
            if newNode[1] >= node[1]:
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
            return getSolution(listNodes)
        explored.append(node)

        cost = node[1][0] + 1
        # check neighbors
        for neightbor in graph[node[0]]:
            if checkDiagonal(node[0], neightbor) == True:
                neightbor = (neightbor, (cost + 0.5, node[0]))
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


def depthFirstSearch(graph, root, goal):
    stack = [root]
    visited = []
    while len(stack) != 0:
        node = stack[-1]
        del stack[-1]  # stack.pop()
        if node not in visited:
            visited.append(node)
            if node == goal:
                return visited
            for neightbor in graph[node]:
                if neightbor in visited:
                    continue
                stack.append(neightbor)  # stack.push()
    return None

def heuristic(node, goal):
    D = 1
    D2 = 1.5
    dx = abs(node[0] - goal[0])
    dy = abs(node[1] - goal[1])
    return D*(dx+dy) + (D2 - 2*D)*min(dx, dy)

def greedyBestFirstSearch(graph, root, goal):
    visited = []
    queue = PriorityQueue()
    node = (root, heuristic(root, goal))
    queue.enqueueHeuristic(node)
    while not queue.isEmpty():
        node = queue.dequeue()
        visited.append(node[0])
        if node[0] == goal:
            return visited
        for neightbor in graph[node[0]]:
            if neightbor in visited:
                continue
            neightbor = (neightbor, heuristic(neightbor, goal))
            queue.enqueueHeuristic(neightbor)
    return None