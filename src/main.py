# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: main.py

import aco_world 
import aco_solver
import aco_settings as acos    

if __name__ == "__main__":
    # set verbose for all modules - debug mode
    acos.VERBOSE = True
    
    # init the world
    world = aco_world.ACOWorld(path_nodes="data/input1_nodes.in", path_edges=None) # "data/input1_edges.in"
    # world.print_edges()
    world.check_for_graph_completion()
    # init the solver (100 ants)
    solver = aco_solver.ACOSolver(_world=world, _alpha=1.0, _beta=1.0, _rho=0.5, _n=5, _tau0="greedy", start_node_id=1)
    # world.print_edges()
    # start the solver with 100 iterations
    acos.VERBOSE = True
    solver.solve(10)
    
    
    