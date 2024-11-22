import gui.mainwindow as mw
from acs.aco_solver import ACOSolver
from acs.aco_world import ACOWorld
import acs.aco_settings as acos

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer, QPointF

class ACOComputationState:
    ACO_READY = 0
    ACO_RUNNING = 1
    ACO_PAUSED = 2
    ACO_STOPPED = 3
    ACO_DONE = 3
    
class AntGuiController:
    ACO_STATE : ACOComputationState = False
    
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
        
    def __handle_aco_gui(self, world : ACOWorld, solver : ACOSolver, num_iterations : int, comp_speed : float) -> None:
        print("ACS gui started")
        
        # nodes and edges expected to be drawn already

        self.current_step = 0
        
        solver.prepare_for_one_step_solving()
        
        def one_step_handler():
            print("one step")
            self.current_step += 1
            solver.solve_one_step()
            self.view.update_iteration_count(self.current_step, num_iterations)
            if self.current_step >= num_iterations:
                self.ACO_STATE = ACOComputationState.ACO_DONE
                self.timer.stop()
            
        # start solving
        self.timer = QTimer(self.view)
        self.timer.timeout.connect(one_step_handler)
        self.timer.start(comp_speed*1000)  # 1 second interval
    
    def pauseACO(self) -> None:
        self.ACO_STATE = ACOComputationState.ACO_PAUSED
        self.timer.stop()
    
    def continueACO(self) -> None:
        self.ACO_STATE = ACOComputationState.ACO_RUNNING
        self.timer.start()
    
    def resetACO(self) -> None:
        self.ACO_STATE = ACOComputationState.ACO_READY
        self.world = None
        self.current_step = 0
        self.edge_file_path = None
        self.node_file_path = None
        self.view.reset_scene_context()
    
    def createWorld(self) -> None:
        """create the world with the given node and edge files
        it expects that the node file is set, and everything on gui is clear
        """
        world = ACOWorld(self.node_file_path, self.edge_file_path)
        self.world = world
        self.view.draw_nodes(world.nodes)
        self.view.draw_edges(world.edges)
        
        # center the view
        top_left_x = float("inf")
        top_left_y = float("-inf")
        for node in world.nodes.values():
            top_left_x = min(top_left_x, node.x)
            top_left_y = max(top_left_y, node.y)
            
        self.view.scroll_to_area(int(top_left_x), int(top_left_y))
        
    def startACO(self, params : list[str,float|str], comp_speed : float = 0) -> None:
        """start the ACO algorithm with the given parameters
        
        :param list[str,float|str] params: list of tuples [param name,paramvalue] for the ACO algorithm
        """
        
        # create world
        acos.VERBOSE=False
        world = ACOWorld(self.node_file_path, self.edge_file_path)
        solver = ACOSolver(
            _world=world,
            _gui_controller=self,
            _alpha=params["_alpha"]                 if params["_alpha"]!=None           else 1.0,
            _beta=params["_beta"]                   if params["_beta"]!=None            else 2.0,
            _rho=params["_rho"]                     if params["_rho"]!=None             else 0.1,
            _n=params["_n"]                         if params["_n"]!=None               else 10,
            _tau0=params["_tau0"]                   if params["_tau0"]!=None            else "greedy",
            _Q=params["_Q"]                         if params["_Q"]!=None               else 1,
            _q0=params["_q0"]                       if params["_q0"]!=None              else 0.9,
            _alpha_decay=params["_alpha_decay"]     if params["_alpha_decay"]!=None     else 0.1,
            _start_node_id=params["_start_node_id"] if params["_start_node_id"]!=None   else None
        )
        
        self.world = world
        self.current_step = 0
        self.ACO_STATE = True
        num_iterations = params["num_iterations"] if params["num_iterations"]!=None else 10
        self.__handle_aco_gui(world,solver,num_iterations, comp_speed)
        
    