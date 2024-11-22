from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent, QPainterPath, QPen, QImage, QPainter

class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        # setting title
        # self.setWindowTitle("Paint with PyQt5")

        # setting geometry to main window
        # self.setGeometry(100, 100, 800, 600)

        # creating image object
        self.image = QImage(self.size(), QImage.Format_RGB32)
        # self.setAutoFillBackground(True)
        # making image color to white
        # self.image.fill(Qt.white)
        
        # variables
        # drawing flag
        self.drawing = False
        # default brush size
        self.brushSize = 2
        # default color
        self.brushColor = Qt.black
        # QPoint object to tract the point
        self.lastPoint = QPoint()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
        # super().mousePressEvent(event)

    # method for tracking mouse activity
    def mouseMoveEvent(self, event):
        
        # checking if left button is pressed and drawing flag is true
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            # creating painter object
            painter = QPainter(self.image)
            
            # set the pen of the painter
            painter.setPen(QPen(self.brushColor, self.brushSize, 
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
            # draw line from the last point of cursor to the current point
            # this will draw only one step
            painter.drawLine(self.lastPoint, event.pos())
            
            # change the last point
            self.lastPoint = event.pos()
            # update
            self.update()

    # method for mouse left button release
    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            # make drawing flag false
            self.drawing = False