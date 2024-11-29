# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: main.py

import acs.aco_world as acow
import acs.aco_solver as aco_solver
import acs.aco_settings as acos
import sys

if __name__ == "__main__":
    # set verbose for all modules - debug mode
    acos.VERBOSE = False
    
    # init the world
    try:
        world = acow.ACOWorld(path_nodes="data/input1_nodes.in", path_edges="data/input1_edges.in") # "data/input1_edges.in"
    except Exception as e:
        print("Error: " + str(e), file=sys.stderr)
        exit(1)
    
    # init the solver
    solver = aco_solver.ACOSolver(_world=world, _alpha=1.0, _beta=2.0, _rho=0.1, _n=10, _tau0="greedy", _Q=1, _q0=0.9, _alpha_decay=0.1, _start_node_id=1)
    
    # start the solver 
    acos.VERBOSE = False
    solver.solve(10)
    
    # obtain and print result
    nodes,bt,cost=solver.get_best_tour()
    print("Best tour cost: ",cost)
    print("******Best tour edges******")
    for edge in bt :
        print(edge)
    print("******Best tour nodes******")
    for node in nodes:
        print(node)
    
    
    
    