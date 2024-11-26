from acs.aco_world import Node, Edge, ACOWorld
import acs.aco_settings as acoh
import numpy as np
import bisect

class Ant:
    """class representing the ant in the ACO algorithm
    
    :info:
        - !!! if you use this Ant class in AS algorithm, for moving USE `do_next_move_AS()` method !!! \n 
        - !!! if you use this Ant class in ACS algorithm, for moving USE `do_next_move_ACS()` method !!!
    """
    
    # public
    id : int = None
    current_node : Node = None
    visited_nodes : list[Node] = []
    tour : list[Edge] = []
    tour_cost : float = 0
    # private
    __world : ACOWorld = None
    
    def __init__(self, world : ACOWorld, id : int, start_node : Node):
        self.__world = world
        self.id = id
        self.current_node = start_node
        self.visited_nodes = []
        self.tour = []
        self.tour_cost = 0
    
    def reset(self, start_node : Node) -> None:
        """reset the ant to the starting position
        
        :param Node start_node: starting node for the ant
        """
        self.current_node = start_node
        self.visited_nodes = []
        self.tour = []
        self.tour_cost = 0
        
    def can_move(self) -> bool:
        """check if the ant can move to the next node
        
        :return: True if the ant can move, False otherwise
        :rtype: bool
        """
        possible_edges = self.__get_possible_edges()
        return possible_edges != []
    
    def ant_has_returned_to_start(self) -> bool:
        """check if the ant has returned to the starting position
        
        :return: True if the ant has returned to the starting position, False otherwise
        :rtype: bool
        """
        return self.current_node == self.visited_nodes[0] if len(self.visited_nodes) > 0 else False
    
    def do_final_move_to_start(self) -> None:
        # get possible next edges
        possible_edges = self.__world.get_adjacent_edges(self.current_node)
        # get the edge that leads to the starting node
        for edge in possible_edges:
            if edge.node_first == self.current_node and edge.node_second == self.visited_nodes[0] or edge.node_first == self.visited_nodes[0] and edge.node_second == self.current_node :
                self.tour.append(edge)
                self.tour_cost += edge.weight
                self.current_node = self.visited_nodes[0]
                return
    
    def do_next_move_ACS(self, q0 : float, alpha : float, beta : float) -> None:
        """move the ant to the next node according to the ACS (ant colony system) algorithm
        
        :param: float q0: exploitation probability, 0<=q0<=1
        :param: float alpha: alpha parameter, influence of pheromone on the edge
        :param: float beta: beta parameter, influence of the weight of the edge
        """
        # check if the ant can move
        if (not self.can_move()):
            return
        
        # choose whether to exploit or explore
        if (np.random.uniform(0, 1) < q0):
            self.__do_next_move_exploit(alpha, beta)
        else:
            # exploration is done by the AS algorithm
            self.do_next_move_AS(alpha, beta)
    
    def __do_next_move_exploit(self,alpha,beta) -> None:
        """go for the edge with highest probability (no random choosing), it is equivalent to the to the first \
            part of the AS edge-choosing algorithm
        """
        possible_edges = self.__get_possible_edges()
        # if no edge to move to, return
        if (possible_edges == []):
            return
        
        # get the probabilities for the next node (for all neighbors of the current node)
        chosen_edge_list_idx = np.argmax(self.__get_prob_dist_for_edges(possible_edges, alpha, beta))
        
        # update the ant's position
        self.__update_position(possible_edges[chosen_edge_list_idx])
        
    def do_next_move_AS(self, alpha, beta) -> None:
        """move the ant to the next node according to the AS (ant system) algorithm
    
        :param float alpha: alpha parameter
        :param float beta: beta parameter
        """
        possible_edges = self.__get_possible_edges()
        # if no edge to move to, return
        if (possible_edges == []):
            return
        
        # get the probabilities for the next node (for all neighbors of the current node)
        probabilities = self.__get_prob_dist_for_edges(possible_edges, alpha, beta)
        edge_probabilities = np.cumsum(probabilities)
        
        # choose the next edge according to the probabilities
        random_number = np.random.uniform(0, 1)
        selected_edge_idx = bisect.bisect_left(edge_probabilities, random_number)
        
        # select the next node according to the probabilities
        chosen_edge = possible_edges[selected_edge_idx]
        # update the ant's position
        self.__update_position(chosen_edge)

    def __get_possible_edges(self) -> list[Edge]:
        """get the possible edges for the current node, meaning all the edges, leading 
        to the nodes that have not been visited yet from the current node
        
        :return: list of possible edges
        :rtype: list[Edge]
        """
        # get possible next edges
        possible_edges = self.__world.get_adjacent_edges(self.current_node)
        # remove the edges that leads to nodes already visited
        possible_edges = [edge for edge in possible_edges if (edge.node_first not in self.visited_nodes) and (edge.node_second not in self.visited_nodes)]
        return possible_edges
    
    def __get_prob_dist_for_edges(self, possible_edges, alpha, beta) -> list[float]:
        """compute the probability distribution for all possible edges
        
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
        """update the ant's position to the next node, add the edge and node to the visited nodes and path 
        
        :param Edge chosen_edge: edge that the ant has chosen to move to the next node
        """
        # store the processed things
        self.visited_nodes.append(self.current_node)
        self.tour.append(chosen_edge)
        self.tour_cost += chosen_edge.weight
        # update the current node
        self.current_node = chosen_edge.node_second if chosen_edge.node_first == self.current_node else chosen_edge.node_first
