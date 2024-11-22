from time import sleep
import gui.mainwindow as mw
from acs.aco_solver import ACOSolver
from acs.aco_world import ACOWorld
import acs.aco_settings as acos

class AntGuiController:
    ACO_RUNNING = False
    
    def __init__(self):
        self.node_file_path=None
        self.edge_file_path=None
    
    def setView(self, view):
        self.view : mw.MainWindow = view
    
    def setNodeFilePath(self, path):
        print(path)
        self.node_file_path=path
    
    def setEdgeFilePath(self, path):
        print(path)
        self.edge_file_path=path
    
    def __handle_aco_gui(self, world : ACOWorld, solver : ACOSolver, num_iterations : int) -> None:
        print("ACS gui started")
        
        # draw nodes
        self.view.draw_nodes(world.nodes)
        # draw edges
        self.view.draw_edges(world.edges)
        
    def startACS(self, params : list[str,float|str]) -> None:
        """start the ACS algorithm with the given parameters
        
        :param list[str,float|str] params: list of tuples [param name,paramvalue] for the ACS algorithm
        """
        
        # create world
        acos.VERBOSE=True
        world = ACOWorld(self.node_file_path, self.edge_file_path)
        solver = ACOSolver(
            _world=world,
            _alpha=params["_alpha"] if params["_alpha"]!=None else 0.5,
            _beta=params["_beta"] if params["_beta"]!=None else 0.5,
            _rho=params["_rho"] if params["_rho"]!=None else 0.5,
            _n=params["_n"] if params["_n"]!=None else 10,
            _tau0=params["_tau0"] if params["_tau0"]!=None else 0.01,
            _Q=params["_Q"] if params["_Q"]!=None else 1,
            q0=params["q0"] if params["q0"]!=None else 0.5,
            _alpha_decay=params["_alpha_decay"] if params["_alpha_decay"]!=None else 0.1,
            start_node_id=params["start_node_id"] if params["start_node_id"]!=None else None
        )
        
        self.ACO_RUNNING = True
        num_iterations = params["num_iterations"] if params["num_iterations"]!=None else 100
        self.__handle_aco_gui(world,solver,num_iterations)
        
    