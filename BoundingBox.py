"""
Image Annotator

by Amir Kardoost and Beatriz Fernandes
"""

from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor

class BoundingBox(QGraphicsRectItem):
    def __init__(self, x, y, width, height, show_bb_flag, type=None):
        super().__init__(x, y, width, height)

        if show_bb_flag:
            self.setPen(QPen(Qt.green, 3))
        else:
            if type == 'center':
                self.setPen(QPen(Qt.red, 2))
            else:
                self.setPen(QPen(QColor(0, 255, 255), 2))
        self.setBrush(Qt.transparent)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.pen().color() == Qt.red:
            self.setPen(QPen(Qt.green, 3))

        else:
            self.setPen(QPen(Qt.red, 3))
            
        
