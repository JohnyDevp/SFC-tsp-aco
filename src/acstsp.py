# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: main.py

import acs.aco_world as acow
import acs.aco_solver as aco_solver
import acs.aco_settings as acos
import sys
import argparse

from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import Qt, QLineF, QPointF
from PyQt5.QtGui import QPen, QColor, QFont

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
    parser.add_argument("--display", action="store_true", help="Show solved graph.")
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

    if (args.display):
        app = QApplication(sys.argv)
        window = MainWindow(solver, world)
        sys.exit(app.exec_())

class MainWindow(QMainWindow):
    def __init__(self, solver : aco_solver.ACOSolver, world : acow.ACOWorld):
        super().__init__()
        self.initUI()
        self.drawNodes(world.nodes)
        self.drawEdges(world.edges)
        self.set_computation_finised_gui(solver.best_tour_edges, solver.best_tour_nodes)
        
    def drawNodes(self,nodes):
        # define a pen to draw the nodes with
        pen = QPen(QColor(0, 0, 0))  # black color
        pen.setWidth(2)  # Set line width
        pen.setStyle(Qt.SolidLine) 
        
        # draw the nodes
        for node in nodes.values():
            item=self.scene.addEllipse(node.x - 5, node.y - 5, 10, 10, pen, pen.color())
            txt =self.scene.addText(str(node.id), QFont("Arial", 12, weight=1000))
            txt.setPos(node.x, node.y)
            txt.setZValue(12)
            # constatns here are just guessed ... to make the background not so large 
            backg = QGraphicsRectItem(txt.x(),txt.y()+5,txt.boundingRect().width()-2,txt.boundingRect().height()-8)
            backg.setBrush(QColor(158, 134, 28))
            backg.setZValue(11)
            self.scene.addItem(backg)
            item.setZValue(10)
        
        self.scene.update()
    
    def drawEdges(self,edges):
        # define a pen to draw the nodes with
        pen = QPen(Qt.black)  # Blue color
        pen.setWidth(1)  # Set line width
        pen.setStyle(Qt.SolidLine) 
        
        # draw the edges
        for edge in edges:            
            self.scene.addLine(
                QLineF(
                    QPointF(edge.node_first.x,edge.node_first.y), 
                    QPointF(edge.node_second.x,edge.node_second.y)
                ),
                pen
            )
        self.scene.update()
    
    def set_computation_finised_gui(self, best_tour_edges : list[acow.Edge], best_tour_nodes : list[acow.Node]):
        # draw edges
        # define a pen to draw the nodes with
        pen = QPen(QColor(237, 188, 52))  # Blue color
        pen.setWidth(2)  # Set line width
        pen.setStyle(Qt.SolidLine) 
        for edge in best_tour_edges:
            self.scene.addLine(
                QLineF(
                    QPointF(edge.node_first.x,edge.node_first.y), 
                    QPointF(edge.node_second.x,edge.node_second.y)
                ),
                pen
            )
            
        # draw nodes
        pen.setColor(QColor(40, 201, 54))
        for node in best_tour_nodes:
            item=self.scene.addEllipse(node.x - 5, node.y - 5, 10, 10, pen, pen.color())
            item.setZValue(10)
            
        # update the scene
        self.scene.update()
    
    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Solution Visualization")
    
        # create GraphicsView and Scene
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.canvas_width, self.canvas_height = 2000, 2000  # Large virtual canvas size
        self.view.setMinimumSize(self.canvas_width, self.canvas_height)
        self.view.setStyleSheet("background-color: white; border: 1px solid black;")
        
        # wrap the QLabel in a QScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.view)
        self.scroll_area.setWidgetResizable(True)  # Keep the canvas size fixed
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        self.setCentralWidget(self.scroll_area)
        self.show()
    
if __name__ == "__main__":
    main()
