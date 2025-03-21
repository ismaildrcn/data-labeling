import os

from PyQt5.QtWidgets import QGraphicsRectItem, QListWidgetItem, QFileDialog
from PyQt5.QtCore import Qt

from label.widget import LabelWidget



class Annotations(object):
    def __init__(self, connector=None):
        self._connector = connector
        self.label_widget = LabelWidget()

        self.annotation_dict = {}
        

    def add(self, source, coords, rect_obj):
        widget = LabelWidget().setup(self._connector)
        widget.label_list.addItems(self._connector.configurator.labels)
        widget.label_list.setCurrentIndex(-1)

        item = QListWidgetItem(self._connector.current_label_list)
        item.setSizeHint(widget.main.sizeHint())
        self._connector.current_label_list.setItemWidget(item, widget.main)
        annotation = Annotation(source, coords, rect_obj, widget)
        if source in self.annotation_dict:
            self.annotation_dict[source].append(annotation)
        else:
            self.annotation_dict[source] = [annotation]
        widget.delete_label.clicked.connect(lambda: self.delete(annotation))
        widget.view_label.clicked.connect(lambda: self.hide(annotation))
        widget.label_list.currentTextChanged.connect(lambda: self.type_changed(widget.label_list.currentText(), annotation))

        print(self.annotation_dict)

    def hide(self, annotation):
        if annotation.rect_obj:
            annotation.rect_obj.setVisible(not annotation.rect_obj.isVisible())

    def delete(self, annotation):
        if annotation.rect_obj:
            # Sahneyi al
            scene = self._connector.scene
            
            # Rect'i sahneden sil
            if annotation.rect_obj in scene.items():
                scene.removeItem(annotation.rect_obj)
                # Rect'i memory'den temizle
                annotation.rect_obj = None
            
            # Widget'ı listeden bul ve sil
            list_widget = self._connector.current_label_list
            for index in range(list_widget.count()):
                item = list_widget.item(index)
                if list_widget.itemWidget(item) == annotation.widget.main:
                    # Widget'ı item'dan ayır
                    list_widget.setItemWidget(item, None)
                    # Item'ı listeden sil
                    list_widget.takeItem(index)
                    # Widget'ı daha sonra sil
                    annotation.widget.main.deleteLater()
                    break
    
    def type_changed(self, l_type, annotation):
        for key, value in self._connector.configurator.label_type.items():
            if value == l_type:
                annotation.type = key
                break

    def export_annotations(self):
        # Replace the existing line with:
        save_dir = QFileDialog.getExistingDirectory(self._connector, 'Select Directory to Save Annotations')
        if save_dir:
            for image in self.annotation_dict:
                path = os.path.join(save_dir, image.split(os.path.sep)[-1].split('.')[0]) + '.txt'
                with open(path, 'w') as f:
                    for annotation in self.annotation_dict[image]:
                        f.write(f"{annotation.type} {annotation.coords[0]} {annotation.coords[1]} {annotation.coords[2]} {annotation.coords[3]}\n")

class Annotation(object):
    def __init__(self, source, coords, rect_obj, widget: LabelWidget):
        self.source: str = source
        self.coords: tuple = coords
        self.rect_obj: QGraphicsRectItem = rect_obj
        self.widget: LabelWidget = widget
        self.type: str = ""