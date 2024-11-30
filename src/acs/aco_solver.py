# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: aco_solver.py

from acs.aco_world import Node, Edge, ACOWorld
from acs.aco_ant import Ant
import acs.aco_settings as acos
import sys

class ACOSolver:
    ant_colony : list[Ant] = []
    GUIACTIVE : bool = False
    
    def __init__(self, _world : ACOWorld, _alpha : float, _beta : float, _rho : float, _n : int, _tau0 : str | float = 0.01, _Q : float = 1, _q0 : float = 0.5, _alpha_decay : float = 0.1, _start_node_id : int =None,_gui_controller = None):
        """initialize the solver with parameters for the ACO algorithm - ACS
        
        :param `ACOWorld` world: initialized world with nodes and edges
        :param `float` alpha: alpha parameter, influence of pheromone on the edge
        :param `float` beta: beta parameter, influence of the weight of the edge
        :param `float` rho: evaporation rate 0<=rho<=1
        :param `int` n: number of ants
        :param `float` Q: coefficient used in global pheromone update
        :param `float` q0: exploitation probability, 0<=q0<=1
        :param `float` alpha_decay: pheromone decay for the global update pheromone (done only for the best ant), 0<alpha_decay<1 
        :param `str`|`float` tau0: initial pheromone value, if :type:`str`, then it can be only "greedy", according to which \
            the pheromone will be set to 1/[n*(greedy solution)]; \n
            if :type:`float`, then the pheromone will be set to this value
        :param `int` start_node_id: id of the node where the ants will start, if None, no node will be set explicitly
        """
        self.world = _world
        
        if (_n < 1):
            raise ValueError("Number of ants must be greater than 0.")
        self.n = _n
        
        self.alpha = _alpha
        self.beta = _beta
        
        if (_rho > 1 or _rho < 0):
            raise ValueError("rho must be in range [0,1].")
        self.rho = _rho
        
        self.Q = _Q
        
        if (_q0 > 1 or _q0 < 0):
            raise ValueError("q0 must be in range [0,1].")
        self.q0 = _q0
        
        if (_alpha_decay > 1 or _alpha_decay < 0):
            raise ValueError("alpha_decay must be in range [0,1].")
        self.alpha_decay = _alpha_decay
        
        # check whether start node exists
        if _start_node_id is not None and _start_node_id not in self.world.nodes:
            raise ValueError(f"Node with id {_start_node_id} does not exist in the world.")
        self.start_node_id = _start_node_id
        
        self.gui_controller = _gui_controller
        self.GUIACTIVE = False if self.gui_controller is None else True
        
        self.best_tour_nodes = None
        self.best_tour_edges = None
        self.best_tour_cost = float('inf')
        
        self.tau0 = self.world.init_pheromone(_tau0)
        
    def __create_ants(self) -> None:
        # create the ants with world object instance and id
        # and set the starting node for each ant
        self.ant_colony = []
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
                # if the ant has finished its path-finding, return him to its starting position
                if not ant.can_move():
                    # if the ant cannot move anymore, check if it has returned to the starting position
                    if ant.ant_has_returned_to_start():
                        continue
                    else:
                        # if the ant has not returned to the starting position, move it to the starting position
                        ant.do_final_move_to_start()
                        # update pheromone locally
                        self.__local_update_pheromones(ant)
                        finished_ants += 1
                        continue
                else:
                    # move the ant to the next node
                    ant.do_next_move_ACS(self.q0, self.alpha, self.beta)
                    # update pheromone locally
                    self.__local_update_pheromones(ant)
                    # if the ant cannot move anymore after the current move, increment the finished_ants
                    if not ant.can_move() and ant.ant_has_returned_to_start():
                        finished_ants += 1
            
        # return the list of ants according to the total tour length
        return sorted(self.ant_colony, key=lambda ant: ant.tour_cost)
        
    def __global_update_pheromones(self, ant : Ant) -> tuple[float,float]:
        """update the pheromone on trails
        
        :param `Ant` ant: the best ant that found the shortest path
        """
        current_min_pheromone = float('inf')
        current_max_pheromone = float('-inf')
        for edge in self.world.edges:
            ant_contribution = 0
            if edge in ant.tour:
                ant_contribution = self.Q / ant.tour_cost
            # update the pheromone on the edge
            edge.pheromone = (1 - self.alpha_decay) * edge.pheromone + ant_contribution
            current_max_pheromone = max(current_max_pheromone, edge.pheromone)
            current_min_pheromone = min(current_min_pheromone, edge.pheromone)
        
        return (current_min_pheromone, current_max_pheromone)
            
    def __local_update_pheromones(self, ant : Ant) -> None:
        """update the pheromone on last added edge in the tour of ant
        
        :param `Ant` ant: ant
        """
        # delta tau is set to t0 (initial pheromone value)
        # or it can be just 0
        ant.tour[-1].pheromone = max(
            (1 - self.rho) * ant.tour[-1].pheromone + self.rho * self.tau0,
            self.tau0
        )
    
    def get_best_tour(self) -> tuple[list[Node], list[Edge], float]:
        """get the best tour found by the ACO algorithm
        
        :return: tuple of nodes, edges and cost of the best tour
        :rtype: tuple[list[Node], list[Edge], float]
        """
        return (self.best_tour_nodes, self.best_tour_edges, self.best_tour_cost)
    
    def solve(self, num_of_iterations : int = 0) -> None:
        """solve the problem with the ACO algorithm - ACS and defined number of steps
            this methods handles whole process
        :param `int` num_of_iterations: number of iterations
        """
        self.__create_ants()
            
        for _ in range(num_of_iterations):
            self.__reset_ants()
            sorted_ants = self.__do_ants_solutions()
            if acos.VERBOSE:
                print('Best ant:', sorted_ants[0].tour_cost, file=sys.stderr)
            
            # update pheromones for each path, but add pheromone only to those walked by the best ant
            self.__global_update_pheromones(sorted_ants[0])
            
            # save the best tour so far
            if sorted_ants[0].tour_cost < self.best_tour_cost:
                self.best_tour_nodes = sorted_ants[0].visited_nodes
                self.best_tour_edges = sorted_ants[0].tour
                self.best_tour_cost = sorted_ants[0].tour_cost
    
    def prepare_for_one_step_solving(self) -> None:
        """prepare the solver for solving ACS by externally calling solve_one_step method
            in this case it just creates ants
        """
        self.__create_ants()
        
    def solve_one_step(self) -> None:
        """do one step in solving the problem with the ACO algorithm - ACS 
        this method is meant to be called externally in a loop
        necessary to call `prepare_for_one_step_solving()` method before calling this method
        
        especialy for GUI purposes
        """
        self.__reset_ants()
        sorted_ants = self.__do_ants_solutions()
        if acos.VERBOSE:
            print('Best ant:', sorted_ants[0].tour_cost, file=sys.stderr)
                        
        min_pheromone, max_pheromone = self.__global_update_pheromones(sorted_ants[0])
            
        # save the best tour so far
        if sorted_ants[0].tour_cost < self.best_tour_cost:
            self.best_tour_nodes = sorted_ants[0].visited_nodes
            self.best_tour_edges = sorted_ants[0].tour
            self.best_tour_cost = sorted_ants[0].tour_cost
            
        # if gui active, notify about current progress
        if (self.GUIACTIVE):
            self.gui_controller.notify_from_aco_solver(
                type=acos.ACS2GUIMessage.GLOBAL_PHEROMONE_UPDATE_DONE,
                best_tour=sorted_ants[0].tour,
                min_pheromone=min_pheromone,
                max_pheromone=max_pheromone
            )
            
