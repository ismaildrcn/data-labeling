from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPointF
from PyQt5.QtGui import QPen, QWheelEvent, QPainter, QColor


class CustomGraphicsView(QGraphicsView):
    rect_created_signal = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_pos = None
        self.rect_item = None
        self.normalized_coords = None
        self.setMouseTracking(True)
        self.setStyleSheet("border:none;")
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            # Tıklanan noktanın scene içinde olup olmadığını kontrol et
            if self.scene().sceneRect().contains(scene_pos):
                self.start_pos = scene_pos
            else:
                self.start_pos = None
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.viewport().update()  # Her mouse hareketi için yeniden çizim
        self.rectangle_event(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_pos:
            end_pos = self.clamp_position(self.mapToScene(event.pos()))
            if self.start_pos != end_pos:
                rect = QRectF(self.start_pos, end_pos).normalized()

                # Geçici rect'i temizle
                if self.rect_item:
                    self.scene().removeItem(self.rect_item)

                # Yeni kalıcı rect'i oluştur
                pen = QPen(Qt.red, 2)
                self.rect_item = self.scene().addRect(rect, pen)
                
                # Normalize coordinates...
                scene_width = self.scene().width()
                scene_height = self.scene().height()
                
                # Calculate center point...
                center_x = (rect.x() + rect.width()/2) / scene_width
                center_y = (rect.y() + rect.height()/2) / scene_height
                
                # Calculate normalized width and height...
                norm_width = rect.width() / scene_width
                norm_height = rect.height() / scene_height
                
                self.normalized_coords = (round(center_x, 6), round(center_y, 6), 
                                        round(norm_width, 6), round(norm_height, 6))
                self.rect_created_signal.emit((self.normalized_coords, self.rect_item))
                
                self.start_pos = None
                self.rect_item = None  # Referansı temizle
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event: QWheelEvent):
        """Mouse wheel zoom with Ctrl key at cursor position."""
        if event.modifiers() == Qt.ControlModifier:
            old_pos = self.mapToScene(event.pos())  # Zoom öncesi mouse sahnedeki pozisyonu
            
            # Zoom faktörünü belirle
            zoom_factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
            self.scale(zoom_factor, zoom_factor)

            # Yeni sahne konumunu hesapla
            new_pos = self.mapToScene(event.pos())  
            delta = new_pos - old_pos  # Farkı hesapla
            
            # Viewport'u kaydırarak mouse'un sabit kalmasını sağla
            self.translate(delta.x(), delta.y())
        else:
            super().wheelEvent(event)

    def rectangle_event(self, event):
        if self.start_pos and event.buttons() & Qt.LeftButton:
            end_pos = self.clamp_position(self.mapToScene(event.pos()))
            rect = QRectF(self.start_pos, end_pos).normalized()

            # Geçici rect'i sil ve yenisini ekle
            if self.rect_item:
                self.scene().removeItem(self.rect_item)

            pen = QPen(Qt.red, 2)
            self.rect_item = self.scene().addRect(rect, pen)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        pen = QPen(QColor(57, 62, 70), 1, Qt.SolidLine)
        painter.setPen(pen)
        
        # Mouse pozisyonunu al
        mouse_pos = self.mapFromGlobal(self.cursor().pos())
        
        # Yatay çizgi
        painter.drawLine(0, mouse_pos.y(), self.width(), mouse_pos.y())
        
        # Dikey çizgi
        painter.drawLine(mouse_pos.x(), 0, mouse_pos.x(), self.height())

    def clamp_position(self, pos):
        """Pozisyonu sahne sınırları içinde tutar"""
        scene_rect = self.scene().sceneRect()
        x = max(scene_rect.left(), min(pos.x(), scene_rect.right()))
        y = max(scene_rect.top(), min(pos.y(), scene_rect.bottom()))
        return QPointF(x, y)