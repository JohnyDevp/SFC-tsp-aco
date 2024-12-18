import gui.mainwindow as mw
from acs.aco_solver import ACOSolver
from acs.aco_world import ACOWorld
import acs.aco_settings as acos
import threading

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer, QPointF
import sys

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
        self.timer = None
        self.lock = threading.Lock()
    
    def setControllersView(self, view):
        self.view : mw.MainWindow = view
    
    def setNodeFilePath(self, path):
        print(path, file=sys.stderr)
        self.node_file_path=path
    
    def setEdgeFilePath(self, path):
        print(path, file=sys.stderr)
        self.edge_file_path=path
    
    def notify_from_aco_solver(self, type : acos.ACS2GUIMessage, **kwargs) -> None:
        match type:
            case acos.ACS2GUIMessage.GLOBAL_PHEROMONE_UPDATE_DONE:
                if acos.VERBOSE:
                    print("Global pheromone update message received", file=sys.stderr)
                # update the view with the new pheromone values
                self.view.update_edges(
                    self.world.edges,
                    kwargs["best_tour"],
                    kwargs["min_pheromone"],
                    kwargs["max_pheromone"]
                )
                QApplication.processEvents()
        
    def __handle_aco_gui(self, num_iterations : int, comp_speed : float) -> None:
        if acos.VERBOSE:
            print("ACS gui started",file=sys.stderr)
        
        # nodes and edges expected to be drawn already

        self.current_step = 0
        
        self.solver.prepare_for_one_step_solving()
        
        def one_step_handler():
            # make sure more than one thread isnt increasing the step
            with self.lock:
                self.current_step += 1
                my_step = self.current_step
            
            # check for possibilities of step that is represented by the current thread
            if my_step == num_iterations:
                self.timer.stop()
                self.ACO_STATE = ACOComputationState.ACO_DONE
                self.solver.solve_one_step()
                self.view.update_iteration_count(self.current_step, num_iterations)
                self.view.set_computation_finised_gui(self.solver.best_tour_edges, self.solver.best_tour_nodes)
                self.view.log_message("Computation finished:",bold=True)
                self.view.log_message(f"Best tour length: {self.solver.best_tour_cost}")
                for i, node in enumerate(self.solver.best_tour_nodes):
                    self.view.log_message(f"{i}. Node: {node}")
            elif my_step > num_iterations:
                return
            else:
                self.solver.solve_one_step()
                self.view.update_iteration_count(self.current_step, num_iterations)
           
        # start solving
        self.timer = QTimer(self.view)
        self.timer.timeout.connect(lambda: one_step_handler() if self.ACO_STATE == ACOComputationState.ACO_RUNNING else None)
        self.timer.start(comp_speed*1000)  # 1 second interval
    
    def pauseACO(self) -> None:
        self.ACO_STATE = ACOComputationState.ACO_PAUSED
        self.timer.stop()
    
    def continueACO(self) -> None:
        self.ACO_STATE = ACOComputationState.ACO_RUNNING
        self.timer.start()
    
    def resetACO(self) -> None:
        self.ACO_STATE = ACOComputationState.ACO_READY
        if (self.timer != None):
            self.timer.stop()
            del self.timer
            self.timer = None
        self.world = None
        self.solver = None
        self.current_step = 0
        self.edge_file_path = None
        self.node_file_path = None
        
        self.view.reset_scene_context()
        self.view.resetUI()
    
    def rebootSame(self):
        store_path=self.edge_file_path
        store_node=self.node_file_path
        store_nodes_set=self.view.nodes_set
        self.resetACO()
        
        self.setEdgeFilePath(store_path)
        self.setNodeFilePath(store_node)
        self.view.nodes_set = store_nodes_set
        self.createWorld()
        
    def createWorld(self) -> None | Exception:
        """create the world with the given node and edge files
        it expects that the node file is set, and everything on gui is clear
        """
        try:
            world = ACOWorld(self.node_file_path, self.edge_file_path)
        except Exception as e:
            self.view.log_message("Error: " + str(e), bold=True, warning=True)
            raise e
        
        if (not world.check_for_graph_completion()):
            self.view.log_message("Graph is not complete. Euclidean distance as edges between nodes can be used.", bold=True,warning=True)
            raise Exception("Graph is not complete")
        
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
        
        # set properly params
        _alpha = params["_alpha"] if params["_alpha"]!=None else 1.0
        _beta = params["_beta"] if params["_beta"]!=None else 2.0
        _rho = params["_rho"] if params["_rho"]!=None else 0.1
        _n = int(params["_n"]) if params["_n"]!=None else 10
        _tau0 = params["_tau0"] if params["_tau0"]!=None else "greedy"
        _Q = params["_Q"] if params["_Q"]!=None else 1
        _q0 = params["_q0"] if params["_q0"]!=None else 0.9
        _alpha_decay = params["_alpha_decay"] if params["_alpha_decay"]!=None else 0.1
        _start_node_id = int(params["_start_node_id"]) if params["_start_node_id"]!=None else None
        num_iterations = int(params["num_iterations"]) if params["num_iterations"]!=None else 10
        
        # logging parameters to window
        self.view.log_message("ACO Parameters:",bold=True)
        self.view.log_message(f"Alpha: {_alpha}")
        self.view.log_message(f"Beta: {_beta}")
        self.view.log_message(f"Rho: {_rho}")
        self.view.log_message(f"Tau0: {_tau0}")
        self.view.log_message(f"Q: {_Q}")
        self.view.log_message(f"q0: {_q0}")
        self.view.log_message(f"Alpha Decay: {_alpha_decay}")
        self.view.log_message(f"Start Node ID: {_start_node_id}")
        self.view.log_message(f"Number of ants (N): {_n}")
        self.view.log_message(f"Number of iterations: {num_iterations}")
        
        # set up the world
        try:
            world = ACOWorld(self.node_file_path, self.edge_file_path)
            # check for completeness
            if (not world.check_for_graph_completion()):
                self.view.log_message("Graph is not complete. Using created edges with euclidean distance.", bold=True,warning=True)
                world = ACOWorld(self.node_file_path, None)
                
            # set up the solver
            solver = ACOSolver(
            _world=world,
            _gui_controller=self,
            _alpha=_alpha,
            _beta=_beta,
            _rho=_rho,
            _n=_n,
            _tau0=_tau0,
            _Q=_Q,
            _q0=_q0,
            _alpha_decay=_alpha_decay,
            _start_node_id=_start_node_id,
        )
        
        except Exception as e:
            self.view.log_message("Error: " + str(e), bold=True, warning=True)
            raise e
            return
    
        # draw the start node
        if _start_node_id != None:
            self.view.draw_start_node(world.nodes[_start_node_id])
        
        self.solver = solver
        self.world = world
        self.current_step = 0
        self.ACO_STATE = True
        self.__handle_aco_gui(num_iterations, comp_speed)
        
    