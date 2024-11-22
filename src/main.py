# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: main.py

import acs.aco_world as acow
import acs.aco_solver as aco_solver
import acs.aco_settings as acos

if __name__ == "__main__":
    # set verbose for all modules - debug mode
    acos.VERBOSE = True
    
    # init the world
    world = acow.ACOWorld(path_nodes="data/input2_nodes.in", path_edges=None) # "data/input1_edges.in"
    # world.print_edges()
    # world.check_for_graph_completion()
    # init the solver (100 ants)
    solver = aco_solver.ACOSolver(_world=world, _alpha=1.0, _beta=2.0, _rho=0.1, _n=10, _tau0="greedy", _Q=1, _q0=0.9, _alpha_decay=0.1, _start_node_id=None)
    world.print_edges()
    # start the solver 
    acos.VERBOSE = False
    solver.solve(1000)
    print()
    world.print_edges()
    
    
    
    