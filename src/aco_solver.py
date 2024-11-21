# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: aco_solver.py

from aco_world import Node, Edge, ACOWorld
from aco_ant import Ant

class ACOSolver:
    ant_colony : list[Ant] = []
    
    def __init__(self, _world : ACOWorld, _alpha : float, _beta : float, _rho : float, _n : int, _tau0 : str | float = 0.01, start_node_id : int =None):
        """initialize the solver with parameters for the ACO algorithm
        
        :param `ACOWorld` world: initialized world with nodes and edges
        :param `float` alpha: alpha parameter
        :param `float` beta: beta parameter
        :param `float` rho: evaporation rate
        :param `int` n: number of ants
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
        self.start_node_id = start_node_id
        
        self.tau0 = _tau0
        self.world.init_pheromone(self.tau0)
        
    def __prepare(self) -> None:
        # create the ants with world object instance and id
        # and set the starting node for each ant
        for ant_id in range(self.n):
            if self.start_node_id is not None:
                ant_start_node = self.world.get_nodes()[self.start_node_id]
            else:
                ant_start_node = self.world.get_random_node()
            self.ant_colony.append(Ant(self.world,ant_id,ant_start_node))
            
    def __do_ants_solutions(self) -> None:
        # create the solution for each ant
        finished_ants = 0 # the number of ants that have finished their path-finding
        # while finished_ants < len(self.ant_colony):
        for ant in self.ant_colony:
            # move the ant to the next node
            ant.do_next_move(self.alpha, self.beta)
            # self.__update_pheromones()
    
    def solve(self, num_of_iterations : int = 0) -> None:
        # prepare the world - create the ants, initialize pheromones, etc.
        self.__prepare()
        
        for _ in range(num_of_iterations):
            self.__do_ants_solutions()
        

