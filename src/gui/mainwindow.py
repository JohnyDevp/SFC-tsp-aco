import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QSplitter, QLineEdit, QPushButton, QHBoxLayout, 
    QFileDialog, QScrollArea,QLabel
)
from PyQt5.QtCore import Qt,QDir
from PyQt5.QtGui import QPixmap

import gui.controller as ac
import gui.drawingcanvas as gs

class MainWindow(QMainWindow):
    controller : ac.AntGuiController = None
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.setWindowTitle("PyQt Layout Example")
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
            ("Exploitation Probability (q0)", "Enter q0 (e.g., 0.5)","q0"),
            ("Alpha Decay", "Enter alpha decay (e.g., 0.1)","_alpha_decay"),
            ("Start Node ID", "Enter start node ID (optional)","start_node_id")
        ]
        self.inputs = []
        for i in range(9):  # add 8 textboxes for 8 params for ACO
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
        
        # add left widget to the layout
        mylayout.addWidget(left_widget)
       
        # right side layout (canvas area)
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)

        # create a QLabel to serve as the canvas
        self.canvas = QLabel(self)
        self.canvas_width, self.canvas_height = 2000, 2000  # Large virtual canvas size
        self.canvas.setFixedSize(self.canvas_width, self.canvas_height)
        self.canvas.setStyleSheet("background-color: white; border: 1px solid black;")

        # create a QPixmap for drawing
        self.canvas_pixmap = QPixmap(self.canvas_width, self.canvas_height)
        self.canvas_pixmap.fill(Qt.white)  # Fill the pixmap with white color
        self.canvas.setPixmap(self.canvas_pixmap)

        # wrap the QLabel in a QScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(False)  # Keep the canvas size fixed
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        
        # add the scroll area to the right layout
        right_layout.addWidget(self.scroll_area)

        # add right widget to the layout
        mylayout.addWidget(right_widget)
        
        # add layout to the main widget
        main_widget.setLayout(mylayout)
    
    def __load_node_file(self):
        print("Load node file")
        file=QFileDialog.getOpenFileName(self, 'Open file', QDir.homePath(), "Input nodes file (*.in)")
        self.controller.setNodeFilePath(file[0])
        
    def __load_edge_file(self):
        print("Load edge file")
        file=QFileDialog.getOpenFileName(self, 'Open file', QDir.homePath(), "Input edges file (*.in)")
        self.controller.setEdgeFilePath(file[0])
    
    def __obtain_params(self):
        print("Obtain params")
        # obtain the parameters from the textboxes
        try:
            params = []
            for i in range(9):
                ti = self.inputs[i][1].text().strip()
                if ti == "":
                    ti = None
                elif self.inputs[i][0] == "_tau0":
                    if ti != "greedy": float(ti)
                elif self.inputs[i][0] == "q0":
                    if float(ti) > 1.0 or float(ti) < 0.0: raise ValueError
                else:
                    float(ti)
                    
                params.append((self.inputs[i][0],ti))          
        except ValueError:
            print("Error: Invalid parameter values", file=sys.stderr)
            return None
        
        return params
    
    def __start_acs(self):
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
        
        self.controller.startACS()