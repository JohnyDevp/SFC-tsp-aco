# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18

import sys

class Ant:
    pass

class Node:
    def __init__(self, _id : int, _x : float, _y : float, _name=None):
        self.x = _x
        self.y = _y
        self.id = _id
        self.name = _name

class Edge:
    def __init__(self, _node_start : Node, _node_end : Node, _weight : float, _pheromone : float):
        self.node_start = _node_start
        self.node_end = _node_end
        self.weight = _weight
        self.pheromone = _pheromone
        
class ACOWorld:
    """represents the world for the ACO algorithm solving TSP problem
    
    :param dict[Node] _nodes: dictionary of nodes, there are not necessary for the computation, there are just for visualization, \n
        for creating edges between nodes, if the edges are not provided
    :param list[Edge] _edges: list of edges between nodes, in case \n
    of non existing edge file, edges will be created between each node
    """
    _nodes : dict[int, Node] = {}
    _edges : list[Edge] = []
    
    def __init__(self):
        pass
    
    def load_nodes(self, path):
        # read the file line by lines, skip comments (lines starting with #)
        file = open(path, "r")
        for line in file.readlines(): 
            if (line[0] == "#"):
                continue
            node_id, node_name, node_x, node_y = line.split(";")
            self._nodes[int(node_id)] = (Node(int(node_id), float(node_x), float(node_y), node_name))
        file.close()
        
        for i in self._nodes:
            print(self._nodes[i].id, self._nodes[i].name, self._nodes[i].x, self._nodes[i].y)
    
    def load_edges(self, path):
        if (path == None):
            self.create_edges()
        else:
            try:
                file = open(path, "r")
                for line in file.readlines(): 
                    if (line[0] == "#"):
                        continue
                    try:
                        node_start_id, node_end_id, weight = line.split(";")
                        self._edges.append(Edge(self._nodes[int(node_start_id)],self._nodes[int(node_end_id)], float(weight), .0))
                    except:
                        print("Error: Bad edge file format!", file=sys.stderr)
                        exit(2)
                file.close()
            except OSError:
                print("Error: Edge file opening error!", file=sys.stderr)
                exit(1)
        
        for edge in self._edges:
            print(edge.node_start.name, "-->", edge.node_end.name, "|", edge.weight, edge.pheromone)
        
    def _create_edges(self):
        pass
