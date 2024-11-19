import aco_world as aco_world
import aco_settings as acos    

if __name__ == "__main__":
    # set verbose for all modules - debug mode
    acos.VERBOSE = True
    
    # init the world
    world = aco_world.ACOWorld(path_nodes="data/input1_nodes.in", path_edges="data/input1_edges.in")
    
    
    