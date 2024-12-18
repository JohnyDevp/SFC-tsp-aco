# author: Jan Holan
# mail: xholan11@stud.fit.vutbr.cz
# date: 2024-11-18
# file: main.py

from gui.mainwindow import MainWindow
from gui.controller import AntGuiController

from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # init app controller
    controller = AntGuiController()
    # init main window
    window = MainWindow(controller)
    # tell controller about window
    controller.setControllersView(window)
    window.show()

    app.exec()
    
    
    
    