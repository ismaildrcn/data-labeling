import os
from typing import overload

from PyQt5.QtWidgets import QGraphicsRectItem, QListWidgetItem, QFileDialog
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen

from label.widget import LabelWidget

from mains.source import Source


class Annotations(object):
    def __init__(self, connector=None):
        self._connector = connector
        self.label_widget = LabelWidget()

        self.annotation_dict = {}

    @overload
    def add(annotation) -> None: ...
    @overload
    def add(self, source: Source, coords: QRectF, rect_obj: QGraphicsRectItem, label: str = None, without: bool = False) -> None: ...
    def add(self, *args):
        widget = LabelWidget().setup(self._connector)
        widget.label_list.addItems(self._connector.configurator.labels)
        widget.label_list.setCurrentIndex(-1)
        item = QListWidgetItem(self._connector.current_label_list)
        item.setSizeHint(widget.main.sizeHint())
        self._connector.current_label_list.setItemWidget(item, widget.main)

        if len(args) != 1:    
            annotation = Annotation(args[0], args[1], args[2])
            if args[0] in self.annotation_dict:
                self.annotation_dict[args[0]].append(annotation)
            else:
                self.annotation_dict[args[0]] = [annotation]
        else:
            annotation = args[0]
            widget.label_list.setCurrentText(annotation.label)

        widget.delete_label.clicked.connect(lambda: self.delete(annotation))
        widget.view_label.clicked.connect(lambda: self.hide(annotation))
        widget.label_list.currentTextChanged.connect(lambda: self.type_changed(widget.label_list.currentText(), annotation))
        print(self.annotation_dict)

    def hide(self, annotation):
        if annotation.rect_obj:
            annotation.rect_obj.setVisible(not annotation.rect_obj.isVisible())

    def delete(self, annotation, only_front=False):
        self.delete_annotation_from_list()
        if annotation.rect_obj and not only_front:
            # Sahneyi al
            scene = self._connector.scene
            
            # Rect'i sahneden sil
            if annotation.rect_obj in scene.items():
                scene.removeItem(annotation.rect_obj)
                # Rect'i memory'den temizle
                annotation.rect_obj = None
            
            self.annotation_dict[annotation.source].remove(annotation)
            if len(self.annotation_dict[annotation.source]) == 0:
                del self.annotation_dict[annotation.source]
    
    def delete_annotation_from_list(self):
        # Widget'ı listeden bul ve sil
        list_widget = self._connector.current_label_list
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            widget = list_widget.itemWidget(item)
            if widget:
                widget.deleteLater()  # QWidget nesnesini temizle
                widget = None

        # Sonra tüm item'leri temizle
        list_widget.clear()
    
    def type_changed(self, l_type, annotation):
        for key, value in self._connector.configurator.label_type.items():
            if key == l_type:
                annotation.label = key
                break
        print(f"{annotation.source} - {annotation.label} - {annotation.coords}")

    def export_annotations(self):
        # Replace the existing line with:
        save_dir = QFileDialog.getExistingDirectory(self._connector, 'Select Directory to Save Annotations')
        if save_dir:
            for image in self.annotation_dict:
                path = os.path.join(save_dir, image.split(os.path.sep)[-1].split('.')[0]) + '.txt'
                with open(path, 'w') as f:
                    for annotation in self.annotation_dict[image]:
                        f.write(f"{annotation.label} {annotation.coords[0]} {annotation.coords[1]} {annotation.coords[2]} {annotation.coords[3]}\n")
    
    def multi_annotations(self, source: Source):
        if source.previous in self.annotation_dict:
            annotations_clear = self.annotation_dict[source.previous].copy()
            for annotation in annotations_clear:
                self.delete(annotation, only_front=True)
        if source.current in self.annotation_dict:
            # Görsel boyutlarını al
            pixmap = self._connector.image_pixmap
            img_width = pixmap.width()
            img_height = pixmap.height()
            annotations = self.annotation_dict[source.current].copy()
            for annotation in annotations:
                # Normalize edilmiş koordinatları al
                center_x, center_y, width, height = annotation.coords
                
                # Gerçek koordinatlara çevir
                real_width = width * img_width
                real_height = height * img_height
                
                # Merkez koordinatlarını sol üst köşe koordinatlarına çevir
                real_x = (center_x * img_width) - (real_width / 2)
                real_y = (center_y * img_height) - (real_height / 2)

                # QRectF ile dikdörtgen oluştur
                rect = QRectF(real_x, real_y, real_width, real_height)
            
                # Scene üzerinde rect oluştur
                pen = QPen(Qt.red, 2)
                self._connector.scene.addRect(rect, pen)
            
                # Yeni annotation'ı ekle
                self.add(annotation)

class Annotation(object):
    def __init__(self, source, coords, rect_obj):
        self.source: str = source
        self.coords: tuple = coords
        self.rect_obj: QGraphicsRectItem = rect_obj
        self.label: str = ""