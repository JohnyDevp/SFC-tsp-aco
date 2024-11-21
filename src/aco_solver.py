# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: aco_solver.py

from aco_world import Node, Edge, ACOWorld
from aco_ant import Ant
import aco_settings as acos
import sys

class ACOSolver:
    ant_colony : list[Ant] = []
    
    def __init__(self, _world : ACOWorld, _alpha : float, _beta : float, _rho : float, _n : int, _tau0 : str | float = 0.01, _Q : float = 1, q0 : float = 0.5, _alpha_decay : float = 0.1, start_node_id : int =None):
        """initialize the solver with parameters for the ACO algorithm - ACS
        
        :param `ACOWorld` world: initialized world with nodes and edges
        :param `float` alpha: alpha parameter, influence of pheromone on the edge
        :param `float` beta: beta parameter, influence of the weight of the edge
        :param `float` rho: evaporation rate
        :param `int` n: number of ants
        :param `float` Q: coefficient used in global pheromone update
        :param `float` q0: exploitation probability, 0<=q0<=1
        :param `float` alpha_decay: pheromone decay for the global update pheromone (done only for the best ant), 0<alpha_decay<1 
        :param `str`|`float` tau0: initial pheromone value, if :type:`str`, then it can be only "greedy", according to which \
            the pheromone will be set to 1/(greedy solution); \n
            if :type:`float`, then the pheromone will be set to this value
        :param `int` start_node_id: id of the node where the ants will start, if None, no node will be set explicitly
        """
        self.world = _world
        self.n = _n
        self.alpha = _alpha
        self.beta = _beta
        self.rho = _rho
        self.Q = _Q
        self.q0 = q0
        self.alpha_decay = _alpha_decay
        self.start_node_id = start_node_id
        
        self.tau0 = self.world.init_pheromone(_tau0)
        
    def __create_ants(self) -> None:
        # create the ants with world object instance and id
        # and set the starting node for each ant
        for ant_id in range(self.n):
            # choose the start node according to the preferences
            if self.start_node_id is not None:
                ant_start_node = self.world.nodes[self.start_node_id]
            else:
                ant_start_node = self.world.get_random_node()
            # create the ant
            self.ant_colony.append(Ant(self.world,ant_id,ant_start_node))
    
    def __reset_ants(self) -> None:
        # reset the ants - set the starting node for each ant
        for ant in self.ant_colony:
            # choose the start node according to the preferences
            if self.start_node_id is not None:
                ant_start_node = self.world.nodes[self.start_node_id]
            else:
                ant_start_node = self.world.get_random_node()
            # reset the ant
            ant.reset(ant_start_node)
       
    def __do_ants_solutions(self) -> list[Ant]:
        # create the solution for each ant
        finished_ants = 0 # the number of ants that have finished their path-finding
        while finished_ants < len(self.ant_colony):
            for ant in self.ant_colony:
                if not ant.can_move(): continue
                
                # move the ant to the next node
                ant.do_next_move_ACS(self.q0, self.alpha, self.beta)
                # update pheromone locally
                self.__local_update_pheromones(ant)
                # if the ant cannot move anymore after the current move, increment the finished_ants
                if not ant.can_move():
                    finished_ants += 1
            
        # return the list of ants according to the total tour length
        return sorted(self.ant_colony, key=lambda ant: ant.tour_cost)
        
    def __global_update_pheromones(self, ant : Ant) -> None:
        """update the pheromone on trails
        
        :param `Ant` ant: the best ant that found the shortest path
        """
        for edge in self.world.edges:
            ant_contribution = 0
            if edge in ant.tour:
                ant_contribution = self.Q / ant.tour_cost
            # update the pheromone on the edge
            edge.pheromone = (1 - self.alpha_decay) * edge.pheromone + ant_contribution
    
    def __local_update_pheromones(self, ant : Ant) -> None:
        """update the pheromone on trails
        
        :param `Ant` ant: the best ant that found the shortest path
        """
        # diff tau is set to t0 (initial pheromone value)
        # it can also be the max of pheromones of adjacent edges to the last node
        # or it can be just 0
        ant.tour[-1].pheromone = (1 - self.rho) * ant.tour[-1].pheromone + self.rho * self.tau0    
    
    def solve(self, num_of_iterations : int = 0) -> None:
        # prepare the world - create the ants, initialize pheromones, etc.
        self.__create_ants()
            
        for _ in range(num_of_iterations):
            self.__reset_ants()
            sorted_ants = self.__do_ants_solutions()
            if acos.VERBOSE:
                print('Best ant:', sorted_ants[0].tour_cost, file=sys.stderr)
                
            self.__global_update_pheromones(sorted_ants[0])
        
