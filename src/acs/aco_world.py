# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: aco_world.py
import sys
import numpy as np
import acs.aco_settings as acos
import acs.aco_helper as acoh

class Node:
    def __init__(self, _id : int, _x : float, _y : float, _name=None):
        self.x = _x
        self.y = _y
        self.id = _id
        self.name = _name

    def __eq__(self, value):
        """function for checking equality of nodes"""
        return self.id == value.id
    
    def __str__(self):
        """function for printing out the node"""
        return f"{self.id} {self.name} {self.x} {self.y}"
    
class Edge:
    def __init__(self, _node_first : Node, _node_second : Node, _weight : float, _pheromone : float):
        self.node_first = _node_first
        self.node_second = _node_second
        self.weight = _weight
        self.pheromone = _pheromone
    
    def __str__(self):
        """function for printing out the edge"""
        return f"{self.node_first.id} --> {self.node_second.id} | {self.weight} {self.pheromone}"
    
    def __eq__(self, value):
        """function for checking equality of edges"""
        return self.node_first == value.node_first and self.node_second == value.node_second and self.weight == value.weight
         
class ACOWorld:
    """represents the world for the ACO algorithm
    """
    # dictionary of nodes, there are not necessary for the computation, there are just for visualization,
    # for creating edges between nodes, if the edges are not provided
    nodes : dict[int, Node] = {}
    # list of edges between nodes, in case 
    # of non existing edge file, edges will be created between each node
    edges : list[Edge] = []
    
    def __init__(self, path_nodes, path_edges=None, distance_function=acoh.euclidean_distance) -> None | Exception:
        """initialize the world with nodes and edges
        
        :param `str` path_nodes: path to the file with nodes
        :param `str` path_edges: path to the file with edges, if None, the edges will be created
        :param `function` distance_function: function for computing the distance between two nodes,
            used only if the edges are not provided
            
        :raises Exception: if the nodes or edges are not loaded correctly or the files have bad format
        """
        # setup distance function (even if none)
        self._distance_function = distance_function
        
        # load the nodes from file
        try:
            self.__load_nodes(path_nodes)
        
            # load edges (or create them)
            if (path_edges == None):
                self.__create_edges()
            else: 
                self.__load_edges(path_edges)
            
        except Exception as e:
            raise e
        
    def get_random_node(self) -> Node:
        return np.random.choice(list(self.nodes.values()))
    
    def get_adjacent_edges(self, node) -> list[Edge]:
        """get the edges adjacent to the given node
        
        :return: list of edges adjacent to the given node
        :rtype: list[Edge]
        """
        adjacent_edges = []
        for edge in self.edges:
            if (edge.node_first == node or edge.node_second == node):
                adjacent_edges.append(edge)
        return adjacent_edges
    
    def check_for_graph_completion(self) -> bool:
        """check whether the graph is complete
        
        :rtype: bool
        :return: True if the graph is complete, False otherwise
        """
        node_count = len(self.nodes)
        all_nodes = list(self.nodes.values())
        path_matrix = np.zeros((node_count, node_count))
        for edge in self.edges:
            path_matrix[all_nodes.index(edge.node_first)][all_nodes.index(edge.node_second)] = 1
            path_matrix[all_nodes.index(edge.node_second)][all_nodes.index(edge.node_first)] = 1
    
        # condition for graph completeness - nodes connected to each other, that results from matrix
        # adding node_count to the sum is because of the diagonal of the matrix (node connected to itself)
        complete = (np.sum(path_matrix,axis=(0,1)) + node_count) == node_count ** 2
        
        if (acos.VERBOSE and not complete):
            print("Warning: The graph is not complete!", file=sys.stderr)
        elif (acos.VERBOSE and complete):
            print("The graph is complete.", file=sys.stderr)
        
        return complete
                
    def __load_nodes(self, path) -> None | Exception:
        # read the file line by lines, skip comments (lines starting with #)
        nodes_loaded = {}
        try:
            file = open(path, "r")
        except OSError:
            raise Exception("Node file opening error!")
        
        for line in file.readlines(): 
            try:
                if (line[0] == "#"):
                    continue
                # parse the node info from the line (there have to be four values separated by semicolon)
                node_id, node_name, node_x, node_y = line.split(";")
                # create the node and add it to the dictionary
                nodes_loaded[int(node_id)] = (Node(int(node_id), float(node_x), float(node_y), node_name))
            except:
                file.close()
                raise Exception("Error: Bad node file format!")
        
        file.close()
        
        # check for empty file
        if (nodes_loaded.__len__() == 0):
            raise Exception("No nodes loaded, empty file!")
        
        self.nodes = nodes_loaded
        
        if (acos.VERBOSE):
            self.print_nodes()
    
    def __load_edges(self, path, check_complete_graph=True) -> Exception | None:
        """load the edges from the file
        
        :param str path: path to the file with edges
        :param bool check_complete_graph: default True, if True, the function will check whether the graph is complete \
            and print warning if not
        
        :rtype: bool
        :return: True if the graph is created successfully, false otherwise
        """
        
        edges_loaded = []
        try:
            file = open(path, "r")
        except OSError:
            raise Exception("Error: Edge file opening error!")
        
        for line in file.readlines(): 
            try:
                if (line[0] == "#"):
                    continue
                node_first_id, node_second_id, weight = line.split(";")
                edges_loaded.append(Edge(self.nodes[int(node_first_id)],self.nodes[int(node_second_id)], float(weight), .0))
            except:
                file.close()
                raise Exception("Error: Bad edge file format!")
                    
        file.close()
        
        self.edges = edges_loaded
        
        # check for empty file
        if (edges_loaded.__len__() == 0):
            raise Exception("No edges loaded, empty file!")
        
        # print the edges, if verbose
        if (acos.VERBOSE):
            self.print_edges()
        
    def __create_edges(self) -> None:
        # create list of nodes, to be able to iterate normally over them (dict is not good for this...)
        all_nodes = list(self.nodes.values())
        # calculate the number of nodes
        node_count = all_nodes.__len__()
        
        # iterate over all nodes and create edge between each pair of nodes
        for node_first_idx in range(0, node_count - 1):
            for node_second_idx in range(node_first_idx + 1, node_count):
                self.edges.append(Edge(
                    all_nodes[node_first_idx], 
                    all_nodes[node_second_idx], 
                    self._distance_function(all_nodes[node_first_idx], all_nodes[node_second_idx]),
                    .0
                ))    
            
        # control printout of the edges
        if (acos.VERBOSE):
            self.print_edges()
      
    def init_pheromone(self, tau0) -> float:
        """initialize the pheromone on the edges
        
        :return: the initial pheromone value, usefull in case that the greedy solution is computed, \
            otherwise the same value as the input tau0 is returned
        :rtype: float
        """
        float_tau0 = .0 
        if (isinstance(tau0,str) and tau0 == "greedy"):
            # compute the greedy solution
            greedy_solution_cost, _, _ = acoh.greedy_solution(self)
            # set the pheromone on the edges to 1/(greedy solution cost)
            for edge in self.edges:
                edge.pheromone = 1 / (len(self.nodes)*greedy_solution_cost)
            float_tau0 = 1 / greedy_solution_cost    
        elif (isinstance(tau0,float) or isinstance(tau0,int)):
            for edge in self.edges:
                edge.pheromone = float(tau0)
            float_tau0 = float(tau0)
        else:
            print("Error: Bad initial phereomone value (tau0 parameter)!", file=sys.stderr)
            exit(3)

        return float_tau0
    
    def print_edges(self) -> None:
        """print the edges in the world"""
        for edge in self.edges:
            print(edge)
            
    def print_nodes(self) -> None:
        """print the nodes in the world"""
        for node in self.nodes.values():
            print(node)
      