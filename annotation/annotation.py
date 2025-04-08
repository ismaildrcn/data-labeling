import os
import uuid
from zipfile import ZipFile
from typing import Union, overload

from PyQt5.QtWidgets import QGraphicsRectItem, QListWidgetItem, QFileDialog
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QPixmap

from label.widget import LabelWidget

from mains.source import Source
from modals.popup.messages import PopupMessages
from modals.popup.utils import Answers
from images.utils import ImageStatus


class Annotations(object):
    def __init__(self, connector=None):
        self._connector = connector
        self.label_widget = LabelWidget()

        self.annotation_count = 0
        self.annotation_dict = {}

    @overload
    def add(self, annotation) -> None: ...
    @overload
    def add(self, source: Source, coords: QRectF, rect_obj: QGraphicsRectItem) -> None: ...
    @overload
    def add(self, source: Source, coords: QRectF, rect_obj: QGraphicsRectItem, label: str = None) -> None: ...
    def add(self, *args):
        widget = LabelWidget().setup(self._connector)
        widget.label_list.addItems(self._connector.configurator.labels)
        widget.label_list.setCurrentIndex(-1)
        item = QListWidgetItem(self._connector.current_label_list)
        item.setSizeHint(widget.main.sizeHint())
        self._connector.current_label_list.setItemWidget(item, widget.main)

        if len(args) != 1:
            if len(args) == 3:
                annotation = Annotation(args[0], args[1], args[2], item)
            elif len(args) == 4:
                annotation = Annotation(args[0], args[1], args[2], item, args[3])

            self.annotation_count += 1
            if args[0] in self.annotation_dict:
                self.annotation_dict[args[0]].append(annotation)
            else:
                self.annotation_dict[args[0]] = [annotation]
        else:
            annotation = args[0]
            if annotation.label is not None:
                widget.label_list.setCurrentIndex(int(annotation.label))

        widget.delete_label.clicked.connect(lambda: self.delete(annotation))
        widget.view_label.clicked.connect(lambda: self.hide(annotation))
        widget.label_list.currentTextChanged.connect(lambda: self.type_changed(widget.label_list.currentText(), annotation))

    def hide(self, annotation):
        if annotation.rect_obj:
            annotation.rect_obj.setVisible(not annotation.rect_obj.isVisible())

    def delete(self, annotation, only_front=False):
        if only_front:
            self.delete_all_annotation_from_list()
        else:
            self.delete_one_annotation_from_list(annotation)
            if annotation.rect_obj:
                # Sahneyi al
                scene = self._connector.scene
                
                # Rect'i sahneden sil
                if annotation.rect_obj in scene.items():
                    scene.removeItem(annotation.rect_obj)
                    # Rect'i memory'den temizle
                    annotation.rect_obj = None
                
                self.annotation_dict[annotation.source].remove(annotation)
                self.annotation_count -= 1
                if len(self.annotation_dict[annotation.source]) == 0:
                    del self.annotation_dict[annotation.source]
                    self._connector.image_handler.images[annotation.source].set_status(ImageStatus.UNANNOTATED)
                    
    
    def delete_all_annotation_from_list(self):
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
    
    def delete_one_annotation_from_list(self, annotation):
        # Widget'ı listeden bul ve sil
        list_widget = self._connector.current_label_list
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item == annotation.item:
                widget = list_widget.itemWidget(item)
                if widget:
                    widget.deleteLater()  # QWidget nesnesini temizle
                    widget = None
                list_widget.takeItem(list_widget.row(item))
    
    def type_changed(self, l_type, annotation):
        for key, value in self._connector.configurator.label_type.items():
            if key == l_type:
                annotation.label = value
                break
        _, _, defined_label_count = self.check_annotation
        self._connector.label_defined_annotation_value.setText(str(defined_label_count))

    def export_annotations(self):
        try:
            has_unwrite, available_annotation, _ = self.check_annotation
            if available_annotation is False:
                self._connector.show_message(PopupMessages.Warning.M200)
            else:
                if has_unwrite:
                    answer = self._connector.show_message(PopupMessages.Action.M400)
                if has_unwrite is False or answer == Answers.OK:
                    save_dir = QFileDialog.getExistingDirectory(self._connector, 'Çalışmaların Kaydedileceği Klasörü Seçin')
                    if save_dir:
                        self.zipper(save_dir)
                        self._connector.show_message(PopupMessages.Info.M101)
        except Exception as _:
            self._connector.show_message(PopupMessages.Error.M301)
    
    def zipper(self, save_dir):
        with ZipFile(os.path.join(save_dir, str(uuid.uuid4()) + '.zip'), 'w') as archive:
            for image in self.annotation_dict:
                content = ""
                for annotation in self.annotation_dict[image]:
                    if isinstance(annotation.label, int):
                        content += f"{annotation.label} {annotation.coords[0]} {annotation.coords[1]} {annotation.coords[2]} {annotation.coords[3]}\n"
                if content:
                    archive.writestr(image.toLocalFile().split('/')[-1].split('.')[0] + '.txt', content)
            archive.writestr(str(uuid.uuid4()) + '.lbl', str(self._connector.configurator.label_type))
            archive.comment = b"Created by Desird for FAD."
        archive.close()

    def multi_annotations(self, source: Source):
        self.multi_delete(source)
        if source.current in self.annotation_dict:
            # Görsel boyutlarını al
            pixmap = self._connector.image_pixmap
            annotations = self.annotation_dict[source.current].copy()
            for annotation in annotations:
                rect = self.rect_creater_with_coordinate(annotation.coords, pixmap)

                # Scene üzerinde rect oluştur
                pen = QPen(Qt.red, 2)
                self._connector.scene.addRect(rect, pen)
            
                # Yeni annotation'ı ekle
                self.add(annotation)
    
    def multi_delete(self, source: Source):
        path = False
        if source.previous in self.annotation_dict:
            path = source.previous
        elif len(self.annotation_dict) > 0 and source.previous is None:
            path = source.current
        if path:
            annotations_clear = self.annotation_dict[path].copy()
            for annotation in annotations_clear:
                self.delete(annotation, only_front=True)
    def rect_creater_with_coordinate(self, coordinate: tuple, pixmap: QPixmap) -> QRectF:
        img_width = pixmap.width()
        img_height = pixmap.height()

        # Normalize edilmiş koordinatları al
        center_x, center_y, width, height = coordinate
                
        # Gerçek koordinatlara çevir
        real_width = width * img_width
        real_height = height * img_height
        
        # Merkez koordinatlarını sol üst köşe koordinatlarına çevir
        real_x = (center_x * img_width) - (real_width / 2)
        real_y = (center_y * img_height) - (real_height / 2)

        # QRectF ile dikdörtgen oluştur
        return QRectF(real_x, real_y, real_width, real_height)

    
    @property
    def check_annotation(self):
        defined_label_count = 0
        available_annotation = False
        has_unwrite = False
        for image in self.annotation_dict:
            for annotation in self.annotation_dict[image]:
                if annotation.label is None:
                    has_unwrite = True
                else:
                    defined_label_count += 1
                available_annotation = True
        return has_unwrite, available_annotation, defined_label_count
    
    @property
    def annotation_count(self):
        return self._annotation_count
    
    @annotation_count.setter
    def annotation_count(self, value):
        self._annotation_count = value
        self._connector.label_total_annotation_value.setText(str(value))


class Annotation(object):
    def __init__(self, source, coords, rect_obj, item, label = None):
        self.source: str = source
        self.coords: tuple = coords
        self.rect_obj: QGraphicsRectItem = rect_obj
        self.label: Union[int, None] = label
        self.item: QListWidgetItem = item