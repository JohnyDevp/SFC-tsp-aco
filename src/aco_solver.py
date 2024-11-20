# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: aco_solver.py

from aco_world import Node, Edge, ACOWorld
from aco_ant import Ant

class ACOSolver:
    ants : list[Ant] = []
    
    def __init__(self, _world, _alpha, _beta, _rho, _n):
        """initialize the solver with parameters for the ACO algorithm
        
        :param ACOWorld world: initialized world with nodes and edges
        :param float alpha: alpha parameter
        :param float beta: beta parameter
        :param float rho: evaporation rate
        :param int n: number of ants
        """
        self.world = _world
        self.n = _n
        self.alpha = _alpha
        self.beta = _beta
        self.rho = _rho
        
    def __prepare(self):
        for _ in range(self.n):
            self.ants.append(Ant())

        for ant in self.ants:
            # set the starting node for each ant
            ant.current_node = self.world.get_random_node()
            
    def __one_step(self):
        for ant in self.ants:
            # move the ant to the next node
            ant.do_next_move(self.world, self.tau, self.eta, self.alpha, self.beta)
    
    def solve(self, num_of_iterations=10):
        # prepare the world - create the ants, initialize pheromones, etc.
        self.__prepare()
        
        # for _ in range(num_of_iterations):
        #     self.__one_step()
        

