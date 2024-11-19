# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18

from aco_world import ACOWorld

class ACOSolver:
    def __init__(self, world, tau, eta, alpha, beta, rho, n):
        """initialize the solver with parameters for the ACO algorithm
        
        :param ACOWorld world: initialized world with nodes and edges
        :param float tau: initial pheromone value
        :param float eta: heuristic value
        :param float alpha: alpha parameter
        :param float beta: beta parameter
        :param float rho: evaporation rate
        :param int n: number of ants
        """
        
    
    def __prepare(self):
        pass
    
    def __one_step(self):
        pass
    
    def solve(self, num_of_iterations=10):
        # prepare the world - create the ants, initialize pheromones, etc.
        self.__prepare()
        
        for _ in range(num_of_iterations):
            self.__one_step()
        pass

