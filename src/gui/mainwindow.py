import sys
import time
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QHBoxLayout, 
    QFileDialog, QScrollArea,QGraphicsView, QGraphicsScene,
    QTextEdit, QLabel, QSlider, QGraphicsTextItem, QGraphicsRectItem
)
from PyQt5.QtCore import Qt,QDir,QPointF, QLineF,QCoreApplication
from PyQt5.QtGui import QPen, QColor,QFont

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
            textbox.setFixedSize(100, 30)
            textbox.setPlaceholderText(f"{self.textboxes_params[i][0]}")
            self.inputs.append((self.textboxes_params[i][2],textbox))
            left_layout.addWidget(textbox)
            
        # add buttons to the left layout
        button1 = QPushButton("Load node file", self)
        button1.clicked.connect(self.__load_node_file_btn_handler)
        button2 = QPushButton("Load edge file", self)
        button2.clicked.connect(self.__load_edge_file_btn_handler)
        self.load_node_file_btn = button1
        self.load_edge_file_btn = button2
        for b in [button1, button2]:
            left_layout.addWidget(b)
            b.setFixedSize(100, 30)
        # Slider setup
        self.comp_speed_label = QLabel("Computation delay: 0s", self)
        left_layout.addWidget(self.comp_speed_label)
        self.comp_speed_slider = QSlider(Qt.Horizontal, self)
        self.comp_speed_slider.setMinimum(0)
        self.comp_speed_slider.setMaximum(6)
        self.comp_speed_slider.setValue(0)
        self.comp_speed_slider.setTickPosition(QSlider.TicksBelow)
        # Connect slider value change to the method
        self.comp_speed_slider.valueChanged.connect(lambda value: self.comp_speed_label.setText(f"Computation delay: {(value/2.0):.1f}s"))
        self.comp_speed_slider.setTickInterval(1)
        left_layout.addWidget(self.comp_speed_slider)
        
        left_layout.addStretch()
        
        # add left widget to the layout
        mylayout.addWidget(left_widget)
       
        # right side layout (canvas area)
        center_widget = QWidget(self)
        center_layout = QVBoxLayout(center_widget)

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
        center_layout.addWidget(self.scroll_area)
        
        # add right widget to the layout
        mylayout.addWidget(center_widget)
        
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)
        self.message_box = QTextEdit(self)
        self.message_box.setReadOnly(True)
        self.message_box.setFixedSize(200, 300)
        right_layout.addWidget(self.message_box)
        # label to display slider value
        self.iteration_count_label = QLabel("Iteration: 0/0", self)
        self.iteration_count_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.iteration_count_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.iteration_count_label)
        
        create_world_btn = QPushButton("CREATE WORLD", self)
        create_world_btn.clicked.connect(self.__create_world_btn_handler)
        self.create_world_btn = create_world_btn
        right_layout.addWidget(create_world_btn)
        
        run_acs_btn = QPushButton("START ACS", self)
        run_acs_btn.clicked.connect(self.__start_acs_btn_handler)
        run_acs_btn.setEnabled(False)
        self.run_acs_btn = run_acs_btn
        right_layout.addWidget(run_acs_btn)
        
        reset_acs_btn = QPushButton("RESET", self)
        reset_acs_btn.clicked.connect(self.__reset_acs_btn_handler)
        reset_acs_btn.setEnabled(True)
        self.reset_acs_btn = reset_acs_btn
        right_layout.addWidget(reset_acs_btn)
        
        right_layout.addStretch()
        
        # add buttons for zooming
        btn_zoom_in = QPushButton("Zoom In", self)
        btn_zoom_in.clicked.connect(self.__zoom_in)
        btn_zoom_out = QPushButton("Zoom Out", self)
        btn_zoom_out.clicked.connect(self.__zoom_out)
        right_layout.addWidget(btn_zoom_in)
        right_layout.addWidget(btn_zoom_out)
        # zoom factor
        self.zoom_factor = 1.0
        
        mylayout.addWidget(right_widget)
        
        # ensure behavior when resizing the window (stretch only the canvas)
        mylayout.setStretch(0, 0)  # left side (textboxes and buttons)
        mylayout.setStretch(1, 3)  # center (canvas) and right side
        
        # add layout to the main widget
        main_widget.setLayout(mylayout)
    
    def draw_nodes(self, nodes : dict[int, Node], start_node=None) -> None:
        print("Draw nodes")
        
        # define a pen to draw the nodes with
        pen = QPen(QColor(0, 0, 0))  # black color
        pen.setWidth(2)  # Set line width
        pen.setStyle(Qt.SolidLine) 
        
        # draw the nodes
        for node in nodes.values():
            print(node)
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
    
    def draw_start_node(self, node : Node) -> None:
        # define a pen to draw the nodes with
        pen = QPen(QColor(255, 0, 0))  # red color
        pen.setWidth(2)  # Set line width
        pen.setStyle(Qt.SolidLine) 
        item=self.scene.addEllipse(node.x - 5, node.y - 5, 10, 10, pen, pen.color())
        item.setZValue(20)
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
    
    def update_iteration_count(self, current_iteration, max_iterations):
        """update the iteration count label
        
        :param int current_iteration: current iteration
        :param int max_iterations: maximum number of iterations
        """
        self.iteration_count_label.setText(f"Iterace: {current_iteration}/{max_iterations}")
        
    def update_edges(self, edges : list[Edge], best_tour : list[Edge], min_pheromone, max_pheromone) -> None:
        print("Update edges")
        
        # define a pen to draw the nodes with
        pen = QPen(Qt.black)  # Blue color
        pen.setWidth(2)  # Set line width
        pen.setStyle(Qt.SolidLine) 
        
        # remove the old edges
        for edge in self.edge_ui:
            self.scene.removeItem(edge)
            self.edge_ui.remove(edge)
            
        # draw the new edges
        for edge in edges:
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
    
    def log_message(self, message : str, bold=False, warning=False) -> None:
        """log the message to the message box
        
        :param str message: message to log
        """
        prefix = ""
        suffix = ""
        if warning:
            prefix += "<font color='red'>"
            suffix += "</font>"
        if bold:
            prefix += "<b>"
            suffix += "</b>"
        
        self.message_box.append(prefix + message + suffix)
        
    def __get_color_from_value(self, value, min_val, max_val):
        """Map a value from min to max range to a color."""
        # Normalize value between 0 and 1
        normalized_value = (value - min_val) / (max_val - min_val)

        # Define start and end colors (blue to red)
        start_color = QColor(23, 230, 212)   # Blue
        end_color = QColor(28, 21, 230)    # Red

        # Interpolate each color channel
        r = start_color.red() + (end_color.red() - start_color.red()) * normalized_value
        g = start_color.green() + (end_color.green() - start_color.green()) * normalized_value
        b = start_color.blue() + (end_color.blue() - start_color.blue()) * normalized_value
    
        # Return the interpolated color
        return QColor(int(r), int(g), int(b))
    
    def __zoom_in(self):
        """zoom in by increasing the zoom factor."""
        self.zoom_factor *= 1.2  # increase zoom factor by 20%
        self.view.resetTransform()
        self.view.scale(self.zoom_factor, self.zoom_factor)
        # resize the view, to be able to still see whole scene
        self.view.setMinimumSize(int(self.canvas_width * self.zoom_factor), int(self.canvas_height*self.zoom_factor))
    
    def __zoom_out(self):
        """Zoom out by decreasing the zoom factor."""
        self.zoom_factor /= 1.2  # decrease zoom factor by ~16.7%
        self.view.resetTransform()
        self.view.scale(self.zoom_factor, self.zoom_factor)
        # resize the view back
        self.view.setMinimumSize(int(self.canvas_width * self.zoom_factor), int(self.canvas_height*self.zoom_factor))
       
    def scroll_to_area(self, top_left_x, top_left_y):
        """move the scrollbar, so in top left corner will be visible point with coordinates top_left_x, top_left_y
        
        :param int top_left_x: x coordinate of the top left corner
        :param int top_left_y: y coordinate of the top left corner
        """
        self.scroll_area.horizontalScrollBar().setValue(int(1000 + top_left_x))
        self.scroll_area.verticalScrollBar().setValue(int(1000 - top_left_y))
        
        print(self.scroll_area.horizontalScrollBar().value(), self.scroll_area.verticalScrollBar().value())
          
    def __load_node_file_btn_handler(self):
        print("Load node file")
        file=QFileDialog.getOpenFileName(self, 'Open file', QDir.homePath(), "Input nodes file (*.in)")
        self.nodes_set = True
        self.controller.setNodeFilePath(file[0])
        
    def __load_edge_file_btn_handler(self):
        print("Load edge file")
        file=QFileDialog.getOpenFileName(self, 'Open file', QDir.homePath(), "Input edges file (*.in)")
        self.controller.setEdgeFilePath(file[0])
    
    def __create_world_btn_handler(self):
        print("Create world")
        # reset the scene, because we are creating a new world
        self.reset_scene_context()
        
        # TODO remove this hardcoded path
        self.controller.setNodeFilePath("/home/johnny/Code/MIT/SFC/data/input2_nodes.in")
        self.nodes_set = True
        
        # chceck whether the node file is set
        if not self.nodes_set:
            print("Error: Node file not set!", file=sys.stderr)
            self.load_node_file_btn.setStyleSheet("border: 2px solid red;")
            return
        else:
            self.run_acs_btn.setEnabled(True)
            self.load_node_file_btn.setStyleSheet("")
            self.controller.createWorld()
            # disable this button, because the world is already created
            self.create_world_btn.setEnabled(False)
    
    def __reset_acs_btn_handler(self):
        self.controller.resetACO()
        self.iteration_count_label.setText("Iterace: 0/0")
        self.run_acs_btn.setText("START ACS")
        self.run_acs_btn.setEnabled(False)
        self.load_node_file_btn.setEnabled(True)
        self.load_edge_file_btn.setEnabled(True)
        self.create_world_btn.setEnabled(True)
    
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
                    params[self.inputs[i][0]] = None
                elif self.inputs[i][0] == "_tau0":
                    if ti != "greedy":
                        params[self.inputs[i][0]] = float(ti)
                elif self.inputs[i][0] == "q0":
                    if float(ti) > 1.0 or float(ti) < 0.0: raise ValueError
                    else: params[self.inputs[i][0]] = float(ti)
                else:
                    params[self.inputs[i][0]] = float(ti)
                
                self.inputs[current_item][1].setStyleSheet("")    
        except ValueError:
            print(f"Error: Invalid parameter values - param {self.inputs[current_item][0]}", file=sys.stderr)
            self.inputs[current_item][1].setStyleSheet("border: 2px solid red;")    
            return None
        
        return params
    
    def reset_scene_context(self):
        """resets scene, array with edges and zoom factor"""
        print("Clear the scene")
        self.scene.clear()
        self.scene.update()
        self.edge_ui = []
        self.zoom_factor = 1
    
    def set_computation_finised_gui(self, best_tour_edges : list[Edge], best_tour_nodes : list[Node]):
        self.run_acs_btn.setEnabled(False)  
        
        self.best_nodes_edges_gui = []
        # draw edges
        # define a pen to draw the nodes with
        pen = QPen(QColor(237, 188, 52))  # Blue color
        pen.setWidth(2)  # Set line width
        pen.setStyle(Qt.SolidLine) 
        for edge in best_tour_edges:
            item = self.scene.addLine(
                QLineF(
                    QPointF(edge.node_first.x,edge.node_first.y), 
                    QPointF(edge.node_second.x,edge.node_second.y)
                ),
                pen
            )
            self.best_nodes_edges_gui.append(item)
            
        # draw nodes
        pen.setColor(QColor(40, 201, 54))
        for node in best_tour_nodes:
            item=self.scene.addEllipse(node.x - 5, node.y - 5, 10, 10, pen, pen.color())
            item.setZValue(10)
            self.best_nodes_edges_gui.append(item)
            
        # update the scene
        self.scene.update()
           
    def __start_acs_btn_handler(self):
        if (self.controller.ACO_STATE == ac.ACOComputationState.ACO_RUNNING):
            print("Pause ACS")
            self.controller.pauseACO()
            self.run_acs_btn.setText("CONTINUE ACS")
        elif (self.controller.ACO_STATE == ac.ACOComputationState.ACO_PAUSED):
            print("Continue ACS")
            self.controller.continueACO()
            self.run_acs_btn.setText("PAUSE ACS")
        elif (self.controller.ACO_STATE == ac.ACOComputationState.ACO_READY):
            # check whether node file is already set
            if (not self.nodes_set):
                print("Error: Node file not set!", file=sys.stderr)
                self.load_node_file_btn.setStyleSheet("border: 2px solid red;")
                return
            else :
                self.load_node_file_btn.setStyleSheet("")
            
            # obtain the parameters from the textboxes
            params = self.__obtain_params()
            if (params is None):
                return
            
            print("Start ACS")
            # disable buttons for loading files
            self.load_node_file_btn.setEnabled(False)
            self.load_edge_file_btn.setEnabled(False)
            self.create_world_btn.setEnabled(False)
            
            # change button text
            self.run_acs_btn.setText("PAUSE ACS")
            
            self.controller.startACO(params, self.comp_speed_slider.value())