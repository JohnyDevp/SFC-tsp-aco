from aco_world import Node, Edge, ACOWorld
import aco_settings as acoh
import numpy as np
import bisect

class Ant:
    current_node : Node = None
    visited_nodes : list[Node] = []
    current_path : list[Edge] = []
    __world : ACOWorld = None
    
    def __init__(self, world : ACOWorld):
        self.__world = world
        
    def do_next_move(self, alpha, beta) -> None:
        """move the ant to the next node
        
        :param ACOWorld world: world with nodes and edges
        :param float tau: initial pheromone value
        :param float eta: heuristic value
        :param float alpha: alpha parameter
        :param float beta: beta parameter
        """
        # get possible next edges
        possible_edges = self.__world.get_adjacent_edges(self.current_node)
        
        # get the probabilities for the next node (for all neighbors of the current node)
        probabilities = self.__get_probabilities(possible_edges, alpha, beta)
        edge_probabilities_intervals = np.cumsum(probabilities)
        # randomly choose interval from the probabilities
        random_number = np.random.uniform(0, 1)
        selected_edge_idx = bisect.bisect_left(edge_probabilities_intervals, random_number)
        
        # select the next node according to the probabilities
        chosen_edge = possible_edges[selected_edge_idx]
        # update the ant's position
        self.__update_position(chosen_edge)

    def __get_probabilities(self, possible_edges, alpha, beta) -> list[float]:
        """compute the probabilities for choosing the next edge (... next node)
        
        :return: list of probabilities for adjacent edges in order as the edges are sorted in the list possible_edges
        :rtype: list[float]
        """
        
        # probability going from node [x] to [y] in step [k]: 
        # prob_(x->y) = [(tau_(x->y))^alpha * (eta_(x->y))^beta] / [sum(tau_(x->z)^alpha * eta_(x->z)^beta)]
        # go through all possible edges for the current node and compute the numerator for the formula for probability
        probabilities = []
        for edge in possible_edges:
            tau = edge.pheromone
            eta = 1 / edge.weight
            # compute just the numerator
            numerator = ((tau**alpha)*(eta**beta))
            probabilities.append(numerator)

        # normalize the probabilities by denominator (from formula)
        denominator = sum(probabilities)
        probabilities = [numerator/denominator for numerator in probabilities]
        return probabilities
    
    def __update_position(self, chosen_edge : Edge) -> None:
        self.visited_nodes.append(self.current_node)
        self.current_path.append(chosen_edge)
        self.current_node = chosen_edge.node_second if chosen_edge.node_first == self.current_node else chosen_edge.node_first
   