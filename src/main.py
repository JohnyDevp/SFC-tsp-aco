import aco_world 
import aco_solver
import aco_settings as acos    

if __name__ == "__main__":
    # set verbose for all modules - debug mode
    acos.VERBOSE = True
    
    # init the world
    world = aco_world.ACOWorld(path_nodes="data/input1_nodes.in", path_edges=None) # "data/input1_edges.in"
    
    # init the solver (100 ants)
    solver = aco_solver.ACOSolver(world=world, tau=1.0, eta=1.0, alpha=1.0, beta=1.0, rho=0.5, n=100)
    
    # start the solver with 100 iterations
    solver.solve(100)
    