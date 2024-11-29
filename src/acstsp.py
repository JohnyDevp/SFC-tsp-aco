# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: main.py

import acs.aco_world as acow
import acs.aco_solver as aco_solver
import acs.aco_settings as acos
import sys
import argparse

def main():
    # argument parser setup
    parser = argparse.ArgumentParser(
        description="Run Ant Colony Optimization Solver on a given graph."
    )
    parser.add_argument(
        "node_file", 
        type=str, 
        help="Path to the nodes input file (required)."
    )
    parser.add_argument(
        "--edge_file", 
        type=str, 
        default=None, 
        help="Path to the edges input file (optional)."
    )
    parser.add_argument("--alpha", type=float, default=1.0, help="Alpha parameter (default: 1.0).")
    parser.add_argument("--beta", type=float, default=2.0, help="Beta parameter (default: 2.0).")
    parser.add_argument("--rho", type=float, default=0.1, help="Rho parameter (default: 0.1).")
    parser.add_argument("--n", type=int, default=10, help="Number of ants (default: 10).")
    parser.add_argument("--tau0", type=str, default="greedy", help="Initial pheromone value (default: 'greedy').")
    parser.add_argument("--Q", type=float, default=1, help="Pheromone intensity (default: 1).")
    parser.add_argument("--q0", type=float, default=0.9, help="Probability threshold for exploitation (default: 0.9).")
    parser.add_argument("--alpha_decay", type=float, default=0.1, help="Alpha decay rate (default: 0.1).")
    parser.add_argument("--start_node", type=int, default=1, help="Start node ID (default: 1).")
    parser.add_argument("--iterations", type=int, default=10, help="Number of iterations for solving (default: 10).")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output for debugging.")
    
    args = parser.parse_args()
    
    # set verbose mode globally
    acos.VERBOSE = args.verbose

    # print parameters
    print("\n--- Algorithm Parameters ---")
    for arg, value in vars(args).items():
        print(f"{arg}: {value}")
    print("----------------------------\n")

    # initialize the world
    try:
        world = acow.ACOWorld(
            path_nodes=args.node_file, 
            path_edges=args.edge_file
        )
    except Exception as e:
        print("Error: " + str(e), file=sys.stderr)
        exit(1)

    # initialize the solver
    solver = aco_solver.ACOSolver(
        _world=world, 
        _alpha=args.alpha, 
        _beta=args.beta, 
        _rho=args.rho, 
        _n=args.n, 
        _tau0=args.tau0, 
        _Q=args.Q, 
        _q0=args.q0, 
        _alpha_decay=args.alpha_decay, 
        _start_node_id=args.start_node
    )

    # start solving acs
    solver.solve(args.iterations)

    # print results
    nodes, bt, cost = solver.get_best_tour()
    print("Best tour cost: ", cost)
    print("****** Best tour edges ******")
    for edge in bt:
        print(edge)
    print("****** Best tour nodes ******")
    for node in nodes:
        print(node)

if __name__ == "__main__":
    main()
