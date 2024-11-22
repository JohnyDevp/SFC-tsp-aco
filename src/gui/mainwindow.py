import sys
import time
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QHBoxLayout, 
    QFileDialog, QScrollArea,QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsLineItem
)
from PyQt5.QtCore import Qt,QDir,QPointF, QLineF
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QLinearGradient

import gui.controller as ac

from acs.aco_world import Node, Edge

class MainWindow(QMainWindow):
    controller : ac.AntGuiController = None
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.nodes_set = False
        
        self.setWindowTitle("ACS GUI")
        self.setGeometry(100, 100, 800, 600)  # Window size

        # Create main layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # create layout of the main widget
        mylayout = QHBoxLayout()
        
        # left side layout (textboxes + buttons)
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)

        # add textboxes to the left layout
        # these tuples define the label, placeholder, and the name of the parameter, according
        # to which the parameter will be !!! passed to the ACO !!!
        self.textboxes_params = [
            ("Alpha", "Enter alpha (e.g., 1.0)","_alpha"),
            ("Beta", "Enter beta (e.g., 2.0)","_beta"),
            ("Rho", "Enter rho (e.g., 0.5)","_rho"),
            ("Number of Ants", "Enter number of ants (e.g., 50)","_n"),
            ("Initial Pheromone (tau0)", "Enter initial pheromone (e.g., 0.01)","_tau0"),
            ("Q Value", "Enter Q value (e.g., 1.0)","_Q"),
            ("Exploitation Probability (q0)", "Enter q0 (e.g., 0.5)","_q0"),
            ("Alpha Decay", "Enter alpha decay (e.g., 0.1)","_alpha_decay"),
            ("Start Node ID", "Enter start node ID (optional)","_start_node_id"),
            ("Number of Iterations", "Enter number of iterations (e.g., 100)","num_iterations")
        ]
        self.inputs = []
        for i in range(10):  # add 8 textboxes for 8 params for ACO
            textbox = QLineEdit(self)
            textbox.setFixedSize(200, 30)
            textbox.setPlaceholderText(f"{self.textboxes_params[i][0]}")
            self.inputs.append((self.textboxes_params[i][2],textbox))
            left_layout.addWidget(textbox)
            
        # add buttons to the left layout
        button1 = QPushButton("Load node file", self)
        button1.clicked.connect(self.__load_node_file)
        button2 = QPushButton("Load edge file", self)
        button2.clicked.connect(self.__load_edge_file)
        button3 = QPushButton("START ACS", self)
        button3.clicked.connect(self.__start_acs)
        self.button1 = button1
        self.button2 = button2
        self.button3 = button3
        for b in [button1, button2, button3]:
            left_layout.addWidget(b)
            b.setFixedSize(200, 30)
        
        # add left widget to the layout
        mylayout.addWidget(left_widget)
       
        # right side layout (canvas area)
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)

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

        # add the scroll area to the right layout
        right_layout.addWidget(self.scroll_area)
        
        # add buttons for zooming
        btn_zoom_in = QPushButton("Zoom In", self)
        btn_zoom_in.clicked.connect(self.__zoom_in)
        btn_zoom_out = QPushButton("Zoom Out", self)
        btn_zoom_out.clicked.connect(self.__zoom_out)
        right_layout.addWidget(btn_zoom_in)
        right_layout.addWidget(btn_zoom_out)
        
        # initialize the zoom factor
        self.zoom_factor = 1.0
        
        # add right widget to the layout
        mylayout.addWidget(right_widget)
        
        mylayout.setStretch(0, 0)  # left side (textboxes and buttons)
        mylayout.setStretch(1, 3)  # right side (canvas)
        
        # add layout to the main widget
        main_widget.setLayout(mylayout)
    
    def draw_nodes(self, nodes : dict[int, Node]) -> None:
        print("Draw nodes")
        
        # define a pen to draw the nodes with
        pen = QPen(QColor(0, 0, 0))  # black color
        pen.setWidth(2)  # Set line width
        pen.setStyle(Qt.SolidLine) 
        
        # draw the nodes
        for node in nodes.values():
            print(node)
            item=self.scene.addEllipse(node.x - 5, node.y - 5, 10, 10, pen, pen.color())
            item.setZValue(10)
        
        self.scene.update()
    
    def draw_edges(self, edges : list[Edge]):
        print("Draw edges")
        
        # define a pen to draw the nodes with
        pen = QPen(Qt.black)  # Blue color
        pen.setWidth(1)  # Set line width
        pen.setStyle(Qt.SolidLine) 
        
        self.edge_ui = []
        # draw the edges
        for edge in edges:
            print(edge)
            
            lineitem = self.scene.addLine(
                QLineF(
                    QPointF(edge.node_first.x,edge.node_first.y), 
                    QPointF(edge.node_second.x,edge.node_second.y)
                ),
                pen
            )
            self.edge_ui.append( lineitem)
        self.scene.update()
    
    def update_edges(self, edges : list[Edge], best_tour : list[Edge], min_pheromone, max_pheromone) -> None:
        print("Update edges")
        
        # define a pen to draw the nodes with
        pen = QPen(Qt.black)  # Blue color
        pen.setWidth(2)  # Set line width
        pen.setStyle(Qt.SolidLine) 
        
        # remove the old edges
        for edge in self.edge_ui:
            self.scene.removeItem(edge)
            
        # draw the new edges
        for edge in edges:
            print(edge)
            pen.setColor(self.__get_color_from_value(edge.pheromone, min_pheromone, max_pheromone))
            lineitem = self.scene.addLine(
                QLineF(
                    QPointF(edge.node_first.x,edge.node_first.y), 
                    QPointF(edge.node_second.x,edge.node_second.y)
                ),
                pen
            )
            self.edge_ui.append(lineitem)
            
        self.scene.update()
        time.sleep(0.5)
    
    def __get_color_from_value(self, value, min_val, max_val):
        """Map a value from min to max range to a color."""
        # Normalize value between 0 and 1
        normalized_value = (value - min_val) / (max_val - min_val)

        # Define start and end colors (blue to red)
        start_color = QColor(0, 0, 100)   # Blue
        end_color = QColor(255, 0, 255)    # Red

        # Interpolate each color channel
        r = start_color.red() + (end_color.red() - start_color.red()) * normalized_value
        g = start_color.green() + (end_color.green() - start_color.green()) * normalized_value
        b = start_color.blue() + (end_color.blue() - start_color.blue()) * normalized_value
    
        # Return the interpolated color
        return QColor(int(r), int(g), int(b))
    
    def __zoom_in(self):
        """Zoom in by increasing the zoom factor."""
        self.zoom_factor *= 1.2  # Increase zoom factor by 20%
        self.view.resetTransform()
        self.view.scale(self.zoom_factor, self.zoom_factor)
        
    def __zoom_out(self):
        """Zoom out by decreasing the zoom factor."""
        self.zoom_factor /= 1.2  # Decrease zoom factor by ~16.7%
        self.view.resetTransform()
        self.view.scale(self.zoom_factor, self.zoom_factor)
       
    def __load_node_file(self):
        print("Load node file")
        file=QFileDialog.getOpenFileName(self, 'Open file', QDir.homePath(), "Input nodes file (*.in)")
        self.nodes_set = True
        self.controller.setNodeFilePath(file[0])
        
    def __load_edge_file(self):
        print("Load edge file")
        file=QFileDialog.getOpenFileName(self, 'Open file', QDir.homePath(), "Input edges file (*.in)")
        self.controller.setEdgeFilePath(file[0])
    
    def __obtain_params(self) -> dict:
        print("Obtain params")
        # obtain the parameters from the textboxes
        current_item = 0
        try:
            params = {}
            for i in range(10):
                current_item = i
                ti = self.inputs[i][1].text().strip()
                if ti == "":
                    ti = None
                elif self.inputs[i][0] == "_tau0":
                    if ti != "greedy": float(ti)
                elif self.inputs[i][0] == "q0":
                    if float(ti) > 1.0 or float(ti) < 0.0: raise ValueError
                else:
                    float(ti)
                
                self.inputs[current_item][1].setStyleSheet("")    
                params[self.inputs[i][0]] = ti
        except ValueError:
            print(f"Error: Invalid parameter values - param {self.inputs[current_item][0]}", file=sys.stderr)
            self.inputs[current_item][1].setStyleSheet("border: 2px solid red;")    
            return None
        
        return params
    
    def __start_acs(self):
        if (self.controller.ACO_RUNNING):
            print("Stop ACS")
            self.controller.ACO_RUNNING = False
            self.button1.setEnabled(True)
            self.button2.setEnabled(True)
            self.button3.setText("START ACS")
        else:
            # TODO: uncomment this 
            # check whether node file is already set
            # if (not self.nodes_set):
            #     print("Error: Node file not set!", file=sys.stderr)
            #     self.button1.setStyleSheet("border: 2px solid red;")
            #     return
            # else :
            #     self.button1.setStyleSheet("")
            self.controller.setNodeFilePath("/home/johnny/Code/MIT/SFC/data/input2_nodes.in")
            
            # obtain the parameters from the textboxes
            params = self.__obtain_params()
            if (params is None):
                return
            
            print("Start ACS")
            # disable buttons for loading files
            self.button1.setEnabled(False)
            self.button2.setEnabled(False)
            # change button text
            self.button3.setText("STOP ACS")
            
            self.controller.startACS(params)