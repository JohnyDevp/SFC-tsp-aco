import gui.mainwindow as mw
from acs.aco_solver import ACOSolver
from acs.aco_world import ACOWorld
import acs.aco_settings as acos

from time import sleep
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
    
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
    
    def notify_from_aco_solver(self, type : acos.ACS2GUIMessage, **kwargs) -> None:
        match type:
            case acos.ACS2GUIMessage.GLOBAL_PHEROMONE_UPDATE_DONE:
                print("Global pheromone update message received")
                # update the view with the new pheromone values
                self.view.update_edges(
                    self.world.edges,
                    kwargs["best_tour"],
                    kwargs["min_pheromone"],
                    kwargs["max_pheromone"]
                    )
                QApplication.processEvents()
        
    def __handle_aco_gui(self, world : ACOWorld, solver : ACOSolver, num_iterations : int) -> None:
        print("ACS gui started")
        
        # draw nodes
        self.view.draw_nodes(world.nodes)
        # draw edges
        self.view.draw_edges(world.edges)
        
        self.world = world
        
        self.current_step = 0
        
        solver.prepare_for_one_step_solving()
        
        def one_step_handler():
            print("one step")
            self.current_step += 1
            solver.solve_one_step()
            if not self.ACO_RUNNING or self.current_step >= num_iterations:
                self.timer.stop()
            
        # start solving
        self.timer = QTimer(self.view)
        self.timer.timeout.connect(one_step_handler)
        self.timer.start(3000)  # 1 second interval
        
    def startACS(self, params : list[str,float|str]) -> None:
        """start the ACS algorithm with the given parameters
        
        :param list[str,float|str] params: list of tuples [param name,paramvalue] for the ACS algorithm
        """
        
        # create world
        acos.VERBOSE=False
        world = ACOWorld(self.node_file_path, self.edge_file_path)
        solver = ACOSolver(
            _world=world,
            _gui_controller=self,
            _alpha=params["_alpha"] if params["_alpha"]!=None else 0.5,
            _beta=params["_beta"] if params["_beta"]!=None else 0.5,
            _rho=params["_rho"] if params["_rho"]!=None else 0.5,
            _n=params["_n"] if params["_n"]!=None else 10,
            _tau0=params["_tau0"] if params["_tau0"]!=None else 0.01,
            _Q=params["_Q"] if params["_Q"]!=None else 1,
            _q0=params["_q0"] if params["_q0"]!=None else 0.5,
            _alpha_decay=params["_alpha_decay"] if params["_alpha_decay"]!=None else 0.1,
            _start_node_id=params["_start_node_id"] if params["_start_node_id"]!=None else None
        )
        
        self.ACO_RUNNING = True
        num_iterations = params["num_iterations"] if params["num_iterations"]!=None else 10
        self.__handle_aco_gui(world,solver,num_iterations)
        
    