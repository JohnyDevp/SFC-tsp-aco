# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-20
# file: aco_helper.py

import numpy as np

def euclidean_distance(node_first, node_second):
    return np.round(np.sqrt((node_first.x - node_second.x)**2 + (node_first.y - node_second.y)**2), 3)

def greedy_solution(world):
    """compute the greedy solution for the TSP problem
    
    :param ACOWorld world: initialized world with nodes and edges
    :return: tuple of the path cost, list of edges and list of nodes
    :rtype: `tuple[float, list[Edge], list[Node]]`
    """
    # create the solution
    all_nodes = list(world.nodes.values())
    solution_nodes = [all_nodes[0]]
    solution_edges = []
    path_cost = 0
    # start from the first node
    current_node = all_nodes[0]
    # go through all nodes
    while len(solution_nodes) < len(all_nodes):
        next_node = None
        next_edge = None
        min_distance = np.inf
        
        # find the closest node to the current node
        for edge in world.get_adjacent_edges(current_node):
            neighbor = edge.node_second if edge.node_first == current_node else edge.node_first
            if neighbor not in solution_nodes:
                if edge.weight < min_distance:
                    min_distance = edge.weight
                    next_edge = edge
                    next_node = neighbor
        
        # add the node to the solution
        solution_nodes.append(next_node)
        solution_edges.append(next_edge)
        # update the all path cost
        path_cost += min_distance
        # move to the next node
        current_node = next_node
        
    return path_cost,solution_edges,solution_nodes