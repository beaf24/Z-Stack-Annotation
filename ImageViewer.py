from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen

from BoundingBox import BoundingBox


class ImageViewer(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.drawing = False
        self.currentRect = None
        self.startPoint = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.scene().\
                itemsBoundingRect().contains(self.mapToScene(event.pos())):
            self.startPoint = self.mapToScene(event.pos())
            self.drawing = True
            self.currentRect = BoundingBox(0, 0, 0, 0, 'Macrophage', False)
            self.currentRect.setPen(QPen(Qt.red, 3))
            self.scene().addItem(self.currentRect)
            self.updateRectangle(event.pos())

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing and self.currentRect:
            self.updateRectangle(event.pos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.updateRectangle(event.pos())
            self.drawing = False
            if self.currentRect.rect().width() < 5 or \
               self.currentRect.rect().height() < 5:
                # Remove zero-sized rectangle
                self.scene().removeItem(self.currentRect)
            self.currentRect = None
        super().mouseReleaseEvent(event)

    def updateRectangle(self, currentPos):
        """
        Update the rectangle's dimensions based on the current
        mouse position.
        """
        if self.currentRect:
            endPoint = self.mapToScene(currentPos)
            x1, x2 = sorted([self.startPoint.x(), endPoint.x()])
            y1, y2 = sorted([self.startPoint.y(), endPoint.y()])
            self.currentRect.setRect(QRectF(x1, y1, x2 - x1, y2 - y1))
