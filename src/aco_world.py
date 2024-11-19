# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18

import sys
import aco_settings as acos

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
    
    def __init__(self, path_nodes, path_edges=None):
        """initialize the world with nodes and edges
        
        :param str path_nodes: path to the file with nodes
        :param str path_edges: path to the file with edges, if None, the edges will be created
        """
        self.__load_nodes(path_nodes)
        if (path_edges == None):
            self.__create_edges()
        else: 
            self.__load_edges(path_edges)
    
    def __load_nodes(self, path):
        # read the file line by lines, skip comments (lines starting with #)
        try:
            file = open(path, "r")
            for line in file.readlines(): 
                try:
                    if (line[0] == "#"):
                        continue
                    # parse the node info from the line (there have to be four values separated by semicolon)
                    node_id, node_name, node_x, node_y = line.split(";")
                    # create the node and add it to the dictionary
                    self._nodes[int(node_id)] = (Node(int(node_id), float(node_x), float(node_y), node_name))
                except:
                    print("Error: Bad edge file format!", file=sys.stderr)
                    exit(2)
                    file.close()
            file.close()
        except OSError:
            print("Error: Edge file opening error!", file=sys.stderr)
            exit(1)
            
        if (acos.VERBOSE):
            for i in self._nodes:
                print(self._nodes[i].id, self._nodes[i].name, self._nodes[i].x, self._nodes[i].y)
    
    def __load_edges(self, path):
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
        
        # print the edges, if verbose
        if (acos.VERBOSE):
            for edge in self._edges:
                print(edge.node_start.name, "-->", edge.node_end.name, "|", edge.weight, edge.pheromone)
        
    def __create_edges(self):
        pass