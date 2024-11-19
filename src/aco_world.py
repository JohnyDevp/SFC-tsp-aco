# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: aco_world.py
import sys
import numpy as np
import aco_settings as acos
import aco_helper as acoh


class Node:
    def __init__(self, _id : int, _x : float, _y : float, _name=None):
        self.x = _x
        self.y = _y
        self.id = _id
        self.name = _name

class Edge:
    def __init__(self, _node_first : Node, _node_second : Node, _weight : float, _pheromone : float):
        self.node_first = _node_first
        self.node_second = _node_second
        self.weight = _weight
        self.pheromone = _pheromone
    
    def __str__(self):
        return f"{self.node_first.id} --> {self.node_second.id} |  {self.weight} {self.pheromone}"
        
class Ant:
    current_node : Node = None
    visited_nodes : list[Node] = []
    current_path : list[Edge] = []

class ACOWorld:
    """represents the world for the ACO algorithm solving TSP problem
    
    :param dict[Node] _nodes: dictionary of nodes, there are not necessary for the computation, there are just for visualization, \n
        for creating edges between nodes, if the edges are not provided
    :param list[Edge] _edges: list of edges between nodes, in case \n
    of non existing edge file, edges will be created between each node
    """
    __nodes : dict[int, Node] = {}
    __edges : list[Edge] = []
    
    def __init__(self, path_nodes, path_edges=None, distance_function=acoh.euclidean_distance):
        """initialize the world with nodes and edges
        
        :param str path_nodes: path to the file with nodes
        :param str path_edges: path to the file with edges, if None, the edges will be created
        :param function distance_function: function for computing the distance between two nodes,
            used only if the edges are not provided
        """
        # setup distance function (even if none)
        self._distance_function = distance_function
        
        # load the nodes from file
        self.__load_nodes(path_nodes)
        
        # load edges (or create them)
        if (path_edges == None):
            self.__create_edges()
        else: 
            self.__load_edges(path_edges)
    
    def get_random_node(self):
        return np.random.choice(list(self.__nodes.values()))
    
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
                    self.__nodes[int(node_id)] = (Node(int(node_id), float(node_x), float(node_y), node_name))
                except:
                    print("Error: Bad edge file format!", file=sys.stderr)
                    exit(2)
                    file.close()
            file.close()
        except OSError:
            print("Error: Edge file opening error!", file=sys.stderr)
            exit(1)
            
        if (acos.VERBOSE):
            for i in self.__nodes:
                print(self.__nodes[i].id, self.__nodes[i].name, self.__nodes[i].x, self.__nodes[i].y)
    
    def __load_edges(self, path):
        try:
            file = open(path, "r")
            for line in file.readlines(): 
                if (line[0] == "#"):
                    continue
                try:
                    node_first_id, node_second_id, weight = line.split(";")
                    self.__edges.append(Edge(self.__nodes[int(node_first_id)],self.__nodes[int(node_second_id)], float(weight), .0))
                except:
                    print("Error: Bad edge file format!", file=sys.stderr)
                    exit(2)
            file.close()
        except OSError:
            print("Error: Edge file opening error!", file=sys.stderr)
            exit(1)
        
        # print the edges, if verbose
        if (acos.VERBOSE):
            for edge in self.__edges:
                print(edge)
        
    def __create_edges(self):
        # create list of nodes, to be able to iterate normally over them (dict is not good for this...)
        all_nodes = list(self.__nodes.values())
        # calculate the number of nodes
        node_count = all_nodes.__len__()
        
        # iterate over all nodes and create edge between each pair of nodes
        for node_first_idx in range(0, node_count - 1):
            for node_second_idx in range(node_first_idx + 1, node_count):
                self.__edges.append(Edge(
                    all_nodes[node_first_idx], 
                    all_nodes[node_second_idx], 
                    self._distance_function(all_nodes[node_first_idx], all_nodes[node_second_idx]),
                    .0
                ))    
        
        # control printout of the edges
        if (acos.VERBOSE):
            for edge in self.__edges:
                print(edge)