
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen

class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_pos = None
        self.rect_item = None
        self.normalized_coords = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = self.mapToScene(event.pos())
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.start_pos and event.buttons() & Qt.LeftButton:
            end_pos = self.mapToScene(event.pos())
            rect = QRectF(self.start_pos, end_pos).normalized()

            if self.rect_item:
                self.scene().removeItem(self.rect_item)

            pen = QPen(Qt.red, 2)
            self.rect_item = self.scene().addRect(rect, pen)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_pos:
            end_pos = self.mapToScene(event.pos())
            rect = QRectF(self.start_pos, end_pos).normalized()

            if self.rect_item:
                self.scene().removeItem(self.rect_item)

            pen = QPen(Qt.red, 2)
            self.rect_item = self.scene().addRect(rect, pen)
            
            # Normalize coordinates
            scene_width = self.scene().width()
            scene_height = self.scene().height()
            
            # Calculate center point
            center_x = (rect.x() + rect.width()/2) / scene_width
            center_y = (rect.y() + rect.height()/2) / scene_height
            
            # Calculate normalized width and height
            norm_width = rect.width() / scene_width
            norm_height = rect.height() / scene_height
            
            # Store normalized coordinates
            self.normalized_coords = (round(center_x, 6), round(center_y, 6), round(norm_width, 6), round(norm_height, 6))
            print(self.normalized_coords)
            
            self.start_pos = None
        super().mouseReleaseEvent(event)